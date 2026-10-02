"""
ROBOMLM_PLUS - Multi Timeframe Analyzer

Combines 3m / 5m / 15m / 1h / 4h analysis into ONE unified intelligence.

Also integrates real microstructure:
    - Order book imbalance
    - Open Interest delta
    - Funding rate
    - Trade tape buy/sell pressure

Output feeds D13 and AutoROBOMLM.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from app.intelligence.real.real_market_data import get_real_market_data
from app.intelligence.real.structure_analyzer import (
    get_structure_analyzer,
    StructureResult,
)


# Bybit interval codes
TF_BYBIT = {
    "3m": "3",
    "5m": "5",
    "15m": "15",
    "1h": "60",
    "4h": "240",
}

DEFAULT_TIMEFRAMES = ("3m", "5m", "15m", "1h", "4h")


@dataclass(frozen=True)
class MicrostructureContext:
    spread_bps: Optional[float]
    orderbook_imbalance: Optional[float]     # -1 to +1
    tape_buy_pressure: Optional[float]       # -1 to +1
    open_interest: Optional[float]
    funding_rate: Optional[float]
    volume_24h_ratio: Optional[float]

    def to_dict(self):
        return {
            "spread_bps": self.spread_bps,
            "orderbook_imbalance": self.orderbook_imbalance,
            "tape_buy_pressure": self.tape_buy_pressure,
            "open_interest": self.open_interest,
            "funding_rate": self.funding_rate,
            "volume_24h_ratio": self.volume_24h_ratio,
        }


@dataclass(frozen=True)
class MultiTFAnalysis:
    symbol: str
    overall_direction: str            # BULLISH | BEARISH | NEUTRAL
    overall_confidence: float         # 0-100

    timeframes: dict                  # {"3m": StructureResult, ...}
    timeframe_directions: dict        # {"3m": "BULLISH", ...}

    bullish_count: int
    bearish_count: int
    neutral_count: int

    # Higher-timeframe bias (1h + 4h)
    htf_bias: str
    ltf_bias: str                     # 3m + 5m

    microstructure: MicrostructureContext

    # The "action" for downstream
    suggested_action: str             # BUY | SELL | HOLD

    reasons: tuple
    computed_at: datetime

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "overall_direction": self.overall_direction,
            "overall_confidence": self.overall_confidence,
            "timeframe_directions": self.timeframe_directions,
            "bullish_count": self.bullish_count,
            "bearish_count": self.bearish_count,
            "neutral_count": self.neutral_count,
            "htf_bias": self.htf_bias,
            "ltf_bias": self.ltf_bias,
            "microstructure": self.microstructure.to_dict(),
            "suggested_action": self.suggested_action,
            "reasons": list(self.reasons),
            "computed_at": self.computed_at.isoformat(),
            "timeframes": {
                tf: r.to_dict() if hasattr(r, "to_dict") else r
                for tf, r in self.timeframes.items()
            },
        }


class MultiTFAnalyzer:

    def analyze(
        self,
        symbol: str,
        timeframes=DEFAULT_TIMEFRAMES,
    ) -> MultiTFAnalysis:

        now = datetime.now(timezone.utc)
        md = get_real_market_data()
        sa = get_structure_analyzer()

        tf_results = {}
        tf_directions = {}

        for tf in timeframes:
            bybit_tf = TF_BYBIT.get(tf)
            if bybit_tf is None:
                continue

            candles, _ = md.get_candles(symbol, bybit_tf, limit=200)
            if not candles:
                continue

            result = sa.analyze(symbol, tf, candles)
            tf_results[tf] = result
            tf_directions[tf] = result.direction

        # ---- Counts ----
        bullish = sum(1 for d in tf_directions.values() if d == "BULLISH")
        bearish = sum(1 for d in tf_directions.values() if d == "BEARISH")
        neutral = sum(1 for d in tf_directions.values() if d == "NEUTRAL")

        # ---- HTF / LTF bias ----
        htf_dirs = [tf_directions.get(tf) for tf in ("1h", "4h") if tf in tf_directions]
        ltf_dirs = [tf_directions.get(tf) for tf in ("3m", "5m") if tf in tf_directions]

        htf_bias = self._majority(htf_dirs)
        ltf_bias = self._majority(ltf_dirs)

        # ---- Microstructure ----
        micro = self._fetch_microstructure(symbol, md)

        # ---- Overall direction with weights ----
        # HTF weight = 2, LTF weight = 1
        weighted_bull = 0.0
        weighted_bear = 0.0
        reasons = []

        for tf, result in tf_results.items():
            weight = 2.0 if tf in ("1h", "4h") else 1.0
            if result.direction == "BULLISH":
                weighted_bull += weight * (result.confidence / 100.0)
            elif result.direction == "BEARISH":
                weighted_bear += weight * (result.confidence / 100.0)

        # Microstructure bonus
        if micro.orderbook_imbalance is not None:
            if micro.orderbook_imbalance > 0.10:
                weighted_bull += 0.5
                reasons.append(f"Orderbook bid-heavy ({micro.orderbook_imbalance:+.2f})")
            elif micro.orderbook_imbalance < -0.10:
                weighted_bear += 0.5
                reasons.append(f"Orderbook ask-heavy ({micro.orderbook_imbalance:+.2f})")

        if micro.tape_buy_pressure is not None:
            if micro.tape_buy_pressure > 0.15:
                weighted_bull += 0.5
                reasons.append(f"Buy pressure ({micro.tape_buy_pressure:+.2f})")
            elif micro.tape_buy_pressure < -0.15:
                weighted_bear += 0.5
                reasons.append(f"Sell pressure ({micro.tape_buy_pressure:+.2f})")

        total_weight = weighted_bull + weighted_bear
        if total_weight == 0:
            overall = "NEUTRAL"
            confidence = 0.0
        else:
            if weighted_bull > weighted_bear * 1.2:
                overall = "BULLISH"
                confidence = round((weighted_bull / total_weight) * 100, 2)
            elif weighted_bear > weighted_bull * 1.2:
                overall = "BEARISH"
                confidence = round((weighted_bear / total_weight) * 100, 2)
            else:
                overall = "NEUTRAL"
                confidence = 50.0

        reasons.append(f"TF agreement: {bullish}B / {bearish}S / {neutral}N")
        reasons.append(f"HTF bias: {htf_bias} | LTF bias: {ltf_bias}")

        # Suggested action for D13
        if overall == "BULLISH" and confidence >= 60:
            action = "BUY"
        elif overall == "BEARISH" and confidence >= 60:
            action = "SELL"
        else:
            action = "HOLD"

        return MultiTFAnalysis(
            symbol=symbol,
            overall_direction=overall,
            overall_confidence=confidence,
            timeframes=tf_results,
            timeframe_directions=tf_directions,
            bullish_count=bullish,
            bearish_count=bearish,
            neutral_count=neutral,
            htf_bias=htf_bias,
            ltf_bias=ltf_bias,
            microstructure=micro,
            suggested_action=action,
            reasons=tuple(reasons),
            computed_at=now,
        )

    @staticmethod
    def _majority(directions):
        if not directions:
            return "NEUTRAL"
        bull = directions.count("BULLISH")
        bear = directions.count("BEARISH")
        if bull > bear:
            return "BULLISH"
        if bear > bull:
            return "BEARISH"
        return "NEUTRAL"

    @staticmethod
    def _fetch_microstructure(symbol, md):
        spread_bps = None
        imbalance = None
        buy_pressure = None
        oi = None
        funding = None
        vol_ratio = None

        # Orderbook
        try:
            ob = md.get_orderbook(symbol, depth=25)
            if ob is not None:
                spread_bps = round(ob.spread_bps, 4)
                imbalance = round(ob.imbalance, 4)
        except Exception:
            pass

        # Tape
        try:
            trades, _ = md.get_recent_trades(symbol, limit=200)
            if trades:
                buy_vol = sum(t.size for t in trades if t.side == "Buy")
                sell_vol = sum(t.size for t in trades if t.side == "Sell")
                total = buy_vol + sell_vol
                if total > 0:
                    buy_pressure = round((buy_vol - sell_vol) / total, 4)
        except Exception:
            pass

        # OI
        try:
            oi_obj, _ = md.get_open_interest(symbol)
            if oi_obj:
                oi = oi_obj.open_interest
        except Exception:
            pass

        # Funding
        try:
            f = md.get_funding_rate(symbol)
            if f:
                funding = f.funding_rate
        except Exception:
            pass

        return MicrostructureContext(
            spread_bps=spread_bps,
            orderbook_imbalance=imbalance,
            tape_buy_pressure=buy_pressure,
            open_interest=oi,
            funding_rate=funding,
            volume_24h_ratio=vol_ratio,
        )


_engine: Optional[MultiTFAnalyzer] = None


def get_multi_tf_analyzer() -> MultiTFAnalyzer:
    global _engine
    if _engine is None:
        _engine = MultiTFAnalyzer()
    return _engine


__all__ = [
    "MicrostructureContext",
    "MultiTFAnalysis",
    "MultiTFAnalyzer",
    "get_multi_tf_analyzer",
    "DEFAULT_TIMEFRAMES",
    "TF_BYBIT",
]
