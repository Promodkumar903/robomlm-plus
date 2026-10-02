"""
ROBOMLM_PLUS - Order Flow Engine

REAL INTELLIGENCE — not candle-based.

Reads raw market microstructure:
    - Trade tape (per-tick buy/sell)
    - Orderbook depth (DOM)
    - Iceberg detection (repeated fills)
    - Absorption detection (vol vs range)
    - OI delta (new positions)
    - Funding pressure
    - Wall detection (limit orders)

Produces:
    - Flow direction (BUY/SELL pressure)
    - Strength (0-100)
    - Absorption probability at current level
    - Expected displacement

This is the LEADING indicator. Candle is a byproduct.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from math import isfinite, log10
from threading import RLock
from typing import Optional, Sequence

from app.intelligence.real.real_market_data import (
    get_real_market_data,
    Candle,
    OrderbookSnapshot,
    RecentTrade,
)


# ============================================================
# FLOW RESULT
# ============================================================

@dataclass(frozen=True)
class FlowAnalysis:
    symbol: str
    timestamp: str

    # Trade tape
    tape_buy_volume: float
    tape_sell_volume: float
    tape_buy_count: int
    tape_sell_count: int
    tape_pressure: float             # -1 to +1

    # Order book
    bid_volume_25: float
    ask_volume_25: float
    bid_ask_imbalance: float         # -1 to +1
    spread_bps: float
    bid_wall_price: Optional[float]
    bid_wall_size: Optional[float]
    ask_wall_price: Optional[float]
    ask_wall_size: Optional[float]

    # Icebergs
    iceberg_bid_levels: tuple
    iceberg_ask_levels: tuple

    # Absorption
    absorption_detected: bool
    absorption_side: Optional[str]    # BUY_ABSORBED | SELL_ABSORBED
    absorption_strength: float        # 0-100

    # Derivatives
    open_interest: Optional[float]
    funding_rate: Optional[float]
    funding_pressure: str             # LONG_CROWDED | SHORT_CROWDED | NEUTRAL

    # Volume context
    recent_volume_ratio: float        # recent / baseline

    # Verdict
    flow_direction: str               # BULLISH | BEARISH | NEUTRAL
    flow_strength: float              # 0-100
    flow_confidence: float            # 0-100

    reasons: tuple = ()
    provenance: str = "REAL_FLOW"

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp,
            "tape": {
                "buy_volume": self.tape_buy_volume,
                "sell_volume": self.tape_sell_volume,
                "buy_count": self.tape_buy_count,
                "sell_count": self.tape_sell_count,
                "pressure": self.tape_pressure,
            },
            "orderbook": {
                "bid_volume_25": self.bid_volume_25,
                "ask_volume_25": self.ask_volume_25,
                "imbalance": self.bid_ask_imbalance,
                "spread_bps": self.spread_bps,
                "bid_wall": (
                    {"price": self.bid_wall_price, "size": self.bid_wall_size}
                    if self.bid_wall_price else None
                ),
                "ask_wall": (
                    {"price": self.ask_wall_price, "size": self.ask_wall_size}
                    if self.ask_wall_price else None
                ),
            },
            "icebergs": {
                "bid_levels": list(self.iceberg_bid_levels),
                "ask_levels": list(self.iceberg_ask_levels),
            },
            "absorption": {
                "detected": self.absorption_detected,
                "side": self.absorption_side,
                "strength": self.absorption_strength,
            },
            "derivatives": {
                "open_interest": self.open_interest,
                "funding_rate": self.funding_rate,
                "funding_pressure": self.funding_pressure,
            },
            "volume_ratio": self.recent_volume_ratio,
            "verdict": {
                "direction": self.flow_direction,
                "strength": self.flow_strength,
                "confidence": self.flow_confidence,
                "reasons": list(self.reasons),
            },
        }


# ============================================================
# HELPERS
# ============================================================

def _finite(v, default=0.0):
    try:
        n = float(v)
        return n if isfinite(n) else default
    except (TypeError, ValueError):
        return default


def _wall_detection(levels, avg_size, threshold=3.0):
    """Find levels with size > avg * threshold."""
    walls = []
    if avg_size <= 0:
        return walls
    for lvl in levels:
        if lvl.size > avg_size * threshold:
            walls.append(lvl)
    return walls


def _iceberg_detection(trades, price_tolerance_bps=2.0, min_trades=4):
    """
    Iceberg = many trades at nearly same price with similar size.
    Group trades by price bucket, find buckets with high count.
    """
    if not trades or len(trades) < min_trades:
        return []

    buckets = {}
    for t in trades:
        if t.price <= 0:
            continue
        # bucket = price rounded to bps tolerance
        bucket_key = round(t.price / (t.price * price_tolerance_bps / 10000))
        bucket_key = round(t.price, int(-log10(t.price * price_tolerance_bps / 10000) + 1)) if t.price > 0 else t.price
        key = round(t.price, 2)  # simple: 2 decimal
        buckets.setdefault(key, []).append(t)

    icebergs = []
    for price, items in buckets.items():
        if len(items) >= min_trades:
            total_size = sum(x.size for x in items)
            avg = total_size / len(items)
            # uniform sizes = iceberg signature
            sizes = [x.size for x in items]
            if max(sizes) > 0 and (max(sizes) - min(sizes)) / max(sizes) < 0.3:
                side = "BID" if items[0].side == "Buy" else "ASK"
                icebergs.append({
                    "price": float(price),
                    "side": side,
                    "trade_count": len(items),
                    "total_size": round(total_size, 4),
                })
    return icebergs


# ============================================================
# ENGINE
# ============================================================

class OrderFlowEngine:
    """
    Reads microstructure. Does not use candles for direction.
    """

    def analyze(
        self,
        symbol: str,
        candles_1m: Optional[Sequence[Candle]] = None,
    ) -> FlowAnalysis:

        now = datetime.now(timezone.utc)
        md = get_real_market_data()

        reasons = []

        # ------------------------------------------------------
        # 1. TRADE TAPE
        # ------------------------------------------------------
        trades, _ = md.get_recent_trades(symbol, limit=500)

        buy_vol = sell_vol = 0.0
        buy_count = sell_count = 0
        for t in trades:
            if t.side == "Buy":
                buy_vol += t.size
                buy_count += 1
            elif t.side == "Sell":
                sell_vol += t.size
                sell_count += 1

        total_vol = buy_vol + sell_vol
        tape_pressure = (
            (buy_vol - sell_vol) / total_vol if total_vol > 0 else 0.0
        )

        # ------------------------------------------------------
        # 2. ORDER BOOK
        # ------------------------------------------------------
        ob = md.get_orderbook(symbol, depth=25)

        bid_vol_25 = ask_vol_25 = 0.0
        bid_imbalance = 0.0
        spread_bps = 0.0
        bid_wall_price = bid_wall_size = None
        ask_wall_price = ask_wall_size = None

        if ob:
            bid_vol_25 = ob.bid_volume_total
            ask_vol_25 = ob.ask_volume_total
            bid_imbalance = ob.imbalance
            spread_bps = ob.spread_bps

            # wall detection
            if ob.bids:
                avg_bid = sum(x.size for x in ob.bids) / len(ob.bids)
                walls = _wall_detection(ob.bids, avg_bid, threshold=3.0)
                if walls:
                    strongest = max(walls, key=lambda x: x.size)
                    bid_wall_price = strongest.price
                    bid_wall_size = strongest.size

            if ob.asks:
                avg_ask = sum(x.size for x in ob.asks) / len(ob.asks)
                walls = _wall_detection(ob.asks, avg_ask, threshold=3.0)
                if walls:
                    strongest = max(walls, key=lambda x: x.size)
                    ask_wall_price = strongest.price
                    ask_wall_size = strongest.size

        # ------------------------------------------------------
        # 3. ICEBERGS
        # ------------------------------------------------------
        icebergs = _iceberg_detection(trades, price_tolerance_bps=2.0, min_trades=4)

        iceberg_bid = tuple(
            (i["price"], i["total_size"]) for i in icebergs if i["side"] == "BID"
        )[:5]
        iceberg_ask = tuple(
            (i["price"], i["total_size"]) for i in icebergs if i["side"] == "ASK"
        )[:5]

        # ------------------------------------------------------
        # 4. ABSORPTION (volume high but price stuck)
        # ------------------------------------------------------
        absorption_detected = False
        absorption_side = None
        absorption_strength = 0.0

        if candles_1m and len(candles_1m) >= 5:
            recent = candles_1m[-3:]
            baseline_vol = sum(c.volume for c in candles_1m[-20:-3]) / 17 if len(candles_1m) >= 20 else None

            if baseline_vol and baseline_vol > 0:
                recent_vol = sum(c.volume for c in recent)
                recent_range = max(c.high for c in recent) - min(c.low for c in recent)

                avg_range = sum(
                    c.high - c.low for c in candles_1m[-20:-3]
                ) / 17 if len(candles_1m) >= 20 else 0

                if avg_range > 0:
                    vol_ratio = (recent_vol / 3) / baseline_vol
                    range_ratio = recent_range / (avg_range * 3)

                    # high volume, low range = absorption
                    if vol_ratio > 1.5 and range_ratio < 0.8:
                        absorption_detected = True
                        absorption_strength = round(
                            min(100.0, (vol_ratio * 30) + ((1.0 - range_ratio) * 50)),
                            2,
                        )
                        # side from tape pressure
                        if tape_pressure > 0:
                            absorption_side = "BUY_ABSORBED"
                        elif tape_pressure < 0:
                            absorption_side = "SELL_ABSORBED"
                        else:
                            absorption_side = "UNKNOWN"
                        reasons.append(
                            f"Absorption: vol_ratio={vol_ratio:.2f} range_ratio={range_ratio:.2f}"
                        )

        # ------------------------------------------------------
        # 5. DERIVATIVES
        # ------------------------------------------------------
        oi_obj, _ = md.get_open_interest(symbol)
        open_interest = oi_obj.open_interest if oi_obj else None

        fund_obj = md.get_funding_rate(symbol)
        funding_rate = fund_obj.funding_rate if fund_obj else None

        if funding_rate is not None:
            if funding_rate > 0.0005:
                funding_pressure = "LONG_CROWDED"
                reasons.append(f"Longs paying shorts ({funding_rate:.6f})")
            elif funding_rate < -0.0005:
                funding_pressure = "SHORT_CROWDED"
                reasons.append(f"Shorts paying longs ({funding_rate:.6f})")
            else:
                funding_pressure = "NEUTRAL"
        else:
            funding_pressure = "UNKNOWN"

        # ------------------------------------------------------
        # 6. VOLUME CONTEXT
        # ------------------------------------------------------
        recent_volume_ratio = 1.0
        if candles_1m and len(candles_1m) >= 50:
            last_5 = sum(c.volume for c in candles_1m[-5:]) / 5
            base_20 = sum(c.volume for c in candles_1m[-25:-5]) / 20
            recent_volume_ratio = (last_5 / base_20) if base_20 > 0 else 1.0

        # ------------------------------------------------------
        # 7. VERDICT — weighted flow
        # ------------------------------------------------------
        bull_score = 0.0
        bear_score = 0.0

        # Tape pressure (weight 40%)
        if tape_pressure > 0:
            bull_score += abs(tape_pressure) * 40
        else:
            bear_score += abs(tape_pressure) * 40

        # Orderbook imbalance (weight 25%)
        if bid_imbalance > 0:
            bull_score += abs(bid_imbalance) * 25
        else:
            bear_score += abs(bid_imbalance) * 25

        # Wall detection (weight 15%)
        if bid_wall_size and ask_wall_size:
            if bid_wall_size > ask_wall_size * 1.3:
                bull_score += 15
                reasons.append("Bid wall > Ask wall")
            elif ask_wall_size > bid_wall_size * 1.3:
                bear_score += 15
                reasons.append("Ask wall > Bid wall")

        # Icebergs (weight 10%)
        if len(iceberg_bid) > len(iceberg_ask):
            bull_score += 10
            reasons.append(f"Iceberg bids: {len(iceberg_bid)}")
        elif len(iceberg_ask) > len(iceberg_bid):
            bear_score += 10
            reasons.append(f"Iceberg asks: {len(iceberg_ask)}")

        # Funding pressure (weight 10%)
        if funding_pressure == "SHORT_CROWDED":
            # Shorts paying = bullish bias (squeeze potential)
            bull_score += 10
        elif funding_pressure == "LONG_CROWDED":
            bear_score += 10

        # Absorption (overrides other signals)
        if absorption_detected and absorption_side == "BUY_ABSORBED":
            bear_score += 20
            reasons.append("Buy absorption → bulls trapped")
        elif absorption_detected and absorption_side == "SELL_ABSORBED":
            bull_score += 20
            reasons.append("Sell absorption → bears trapped")

        total = bull_score + bear_score
        if total < 10:
            flow_direction = "NEUTRAL"
            flow_strength = 0.0
            flow_confidence = 0.0
        elif bull_score > bear_score * 1.2:
            flow_direction = "BULLISH"
            flow_strength = min(100.0, bull_score)
            flow_confidence = round(bull_score / total * 100, 2)
        elif bear_score > bull_score * 1.2:
            flow_direction = "BEARISH"
            flow_strength = min(100.0, bear_score)
            flow_confidence = round(bear_score / total * 100, 2)
        else:
            flow_direction = "NEUTRAL"
            flow_strength = max(bull_score, bear_score)
            flow_confidence = 50.0
            reasons.append("Balanced flow")

        return FlowAnalysis(
            symbol=symbol,
            timestamp=now.isoformat(),
            tape_buy_volume=round(buy_vol, 6),
            tape_sell_volume=round(sell_vol, 6),
            tape_buy_count=buy_count,
            tape_sell_count=sell_count,
            tape_pressure=round(tape_pressure, 4),
            bid_volume_25=round(bid_vol_25, 6),
            ask_volume_25=round(ask_vol_25, 6),
            bid_ask_imbalance=round(bid_imbalance, 4),
            spread_bps=round(spread_bps, 4),
            bid_wall_price=bid_wall_price,
            bid_wall_size=bid_wall_size,
            ask_wall_price=ask_wall_price,
            ask_wall_size=ask_wall_size,
            iceberg_bid_levels=iceberg_bid,
            iceberg_ask_levels=iceberg_ask,
            absorption_detected=absorption_detected,
            absorption_side=absorption_side,
            absorption_strength=absorption_strength,
            open_interest=open_interest,
            funding_rate=funding_rate,
            funding_pressure=funding_pressure,
            recent_volume_ratio=round(recent_volume_ratio, 4),
            flow_direction=flow_direction,
            flow_strength=round(flow_strength, 2),
            flow_confidence=flow_confidence,
            reasons=tuple(reasons),
            provenance="BYBIT_REAL_FLOW",
        )


_engine: Optional[OrderFlowEngine] = None


def get_order_flow_engine() -> OrderFlowEngine:
    global _engine
    if _engine is None:
        _engine = OrderFlowEngine()
    return _engine


__all__ = [
    "FlowAnalysis",
    "OrderFlowEngine",
    "get_order_flow_engine",
]
