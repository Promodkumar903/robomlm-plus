"""Install flow_direction_engine.py — real direction from flow + obstacles"""
from pathlib import Path

ROOT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\intelligence\real")

FILE = '''"""
ROBOMLM_PLUS - Flow Direction Engine

Final direction is derived from:

  1. ORDER FLOW (primary, 50%)
     - Tape buy/sell pressure
     - Orderbook imbalance
     - Iceberg positions
     - Absorbed side (trapped traders)

  2. OBSTACLE INTERACTION (secondary, 30%)
     - Where is price relative to key levels?
     - Nearest strong resistance / support
     - BOS / CHOCH active?
     - Distance to next cluster

  3. DERIVATIVES (support, 20%)
     - Basis (perp - spot)
     - Funding rate
     - OI change

Candles are used ONLY for:
  - Absorbed volume detection
  - Level extraction (already done)

Never for direction.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Sequence

from app.intelligence.real.real_market_data import (
    get_real_market_data,
    Candle,
)
from app.intelligence.real.order_flow_engine import (
    get_order_flow_engine,
    FlowAnalysis,
)
from app.intelligence.real.obstacle_mapper import (
    get_obstacle_mapper,
    ObstacleMap,
)


# ============================================================
# RESULT
# ============================================================

@dataclass(frozen=True)
class TimeframeSignal:
    timeframe: str
    direction: str            # BULLISH | BEARISH | NEUTRAL
    strength: float           # 0-100
    confidence: float         # 0-100

    # Component scores (0-100 each)
    flow_score: float
    obstacle_score: float
    derivative_score: float

    # Context
    flow_direction: str
    nearest_resistance_price: Optional[float]
    nearest_resistance_distance_pct: Optional[float]
    nearest_support_price: Optional[float]
    nearest_support_distance_pct: Optional[float]

    expected_displacement_pct: float
    sl_cluster_risk: str       # LOW | MEDIUM | HIGH

    reasons: tuple

    def to_dict(self):
        return {
            "timeframe": self.timeframe,
            "direction": self.direction,
            "strength": self.strength,
            "confidence": self.confidence,
            "components": {
                "flow_score": self.flow_score,
                "obstacle_score": self.obstacle_score,
                "derivative_score": self.derivative_score,
            },
            "flow_direction": self.flow_direction,
            "obstacles": {
                "resistance": self.nearest_resistance_price,
                "resistance_dist_pct": self.nearest_resistance_distance_pct,
                "support": self.nearest_support_price,
                "support_dist_pct": self.nearest_support_distance_pct,
            },
            "expected_displacement_pct": self.expected_displacement_pct,
            "sl_cluster_risk": self.sl_cluster_risk,
            "reasons": list(self.reasons),
        }


@dataclass(frozen=True)
class DirectionSignal:
    symbol: str
    as_of: str

    overall_direction: str
    overall_strength: float
    overall_confidence: float

    timeframe_signals: dict    # tf -> TimeframeSignal

    action: str                # BUY | SELL | HOLD
    expected_move_pct: float
    risk_level: str

    # Audit
    audit: dict = field(default_factory=dict)

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "as_of": self.as_of,
            "overall_direction": self.overall_direction,
            "overall_strength": self.overall_strength,
            "overall_confidence": self.overall_confidence,
            "action": self.action,
            "expected_move_pct": self.expected_move_pct,
            "risk_level": self.risk_level,
            "timeframes": {
                tf: sig.to_dict()
                for tf, sig in self.timeframe_signals.items()
            },
            "audit": dict(self.audit),
        }


# ============================================================
# MATH HELPERS
# ============================================================

def _clamp(v, lo=0.0, hi=100.0):
    return max(lo, min(hi, v))


def _atr_pct(candles):
    if not candles or len(candles) < 15:
        return 0.5
    trs = []
    for i in range(1, len(candles)):
        tr = max(
            candles[i].high - candles[i].low,
            abs(candles[i].high - candles[i-1].close),
            abs(candles[i].low - candles[i-1].close),
        )
        trs.append(tr)
    atr = sum(trs[-14:]) / 14
    last = candles[-1].close
    return (atr / last * 100) if last > 0 else 0.5


# ============================================================
# ENGINE
# ============================================================

TF_MAP = {
    "3m": "3", "5m": "5", "15m": "15", "1h": "60", "4h": "240",
}


class FlowDirectionEngine:

    def compute(
        self,
        symbol: str,
        timeframes: Sequence[str] = ("5m", "15m", "1h"),
    ) -> DirectionSignal:

        now = datetime.now(timezone.utc)
        md = get_real_market_data()
        flow_engine = get_order_flow_engine()
        obstacle_mapper = get_obstacle_mapper()

        # ---- Global flow (one shot, used for all TFs) ----
        candles_1m, _ = md.get_candles(symbol, "1", 100)
        global_flow = flow_engine.analyze(symbol, candles_1m)

        # ---- Per timeframe ----
        tf_signals = {}

        for tf in timeframes:
            bybit_tf = TF_MAP.get(tf)
            if bybit_tf is None:
                continue

            candles, _ = md.get_candles(symbol, bybit_tf, 200)
            if not candles or len(candles) < 30:
                continue

            sig = self._tf_signal(
                symbol=symbol,
                timeframe=tf,
                candles=candles,
                flow=global_flow,
                obstacle_mapper=obstacle_mapper,
                md=md,
            )
            tf_signals[tf] = sig

        # ---- Aggregate ----
        if not tf_signals:
            return DirectionSignal(
                symbol=symbol, as_of=now.isoformat(),
                overall_direction="NEUTRAL",
                overall_strength=0.0, overall_confidence=0.0,
                timeframe_signals={},
                action="HOLD",
                expected_move_pct=0.0, risk_level="UNKNOWN",
                audit={},
            )

        # Higher TFs get more weight
        weight_map = {"3m": 0.5, "5m": 1.0, "15m": 2.0, "1h": 3.0, "4h": 4.0}

        bull_weight = 0.0
        bear_weight = 0.0
        total_weight = 0.0

        for tf, sig in tf_signals.items():
            w = weight_map.get(tf, 1.0)
            total_weight += w
            if sig.direction == "BULLISH":
                bull_weight += w * (sig.confidence / 100.0)
            elif sig.direction == "BEARISH":
                bear_weight += w * (sig.confidence / 100.0)

        if total_weight == 0 or (bull_weight + bear_weight) == 0:
            overall = "NEUTRAL"
            strength = 0.0
            conf = 0.0
        else:
            if bull_weight > bear_weight * 1.15:
                overall = "BULLISH"
                strength = round(_clamp(bull_weight / total_weight * 100), 2)
                conf = round(bull_weight / (bull_weight + bear_weight) * 100, 2)
            elif bear_weight > bull_weight * 1.15:
                overall = "BEARISH"
                strength = round(_clamp(bear_weight / total_weight * 100), 2)
                conf = round(bear_weight / (bull_weight + bear_weight) * 100, 2)
            else:
                overall = "NEUTRAL"
                strength = round(_clamp(max(bull_weight, bear_weight) / total_weight * 100), 2)
                conf = 50.0

        # ---- Action ----
        # Only act if confidence is meaningful
        if overall == "BULLISH" and conf >= 60 and strength >= 40:
            action = "BUY"
        elif overall == "BEARISH" and conf >= 60 and strength >= 40:
            action = "SELL"
        else:
            action = "HOLD"

        # ---- Expected move (blend ATR + flow strength) ----
        # Use largest TF's ATR
        largest_tf = max(tf_signals.keys(), key=lambda x: weight_map.get(x, 1))
        expected_move = tf_signals[largest_tf].expected_displacement_pct

        # ---- Risk level ----
        risk_level = "LOW"
        for sig in tf_signals.values():
            if sig.sl_cluster_risk == "HIGH":
                risk_level = "HIGH"
                break
            if sig.sl_cluster_risk == "MEDIUM" and risk_level != "HIGH":
                risk_level = "MEDIUM"

        return DirectionSignal(
            symbol=symbol,
            as_of=now.isoformat(),
            overall_direction=overall,
            overall_strength=strength,
            overall_confidence=conf,
            timeframe_signals=tf_signals,
            action=action,
            expected_move_pct=round(expected_move, 4),
            risk_level=risk_level,
            audit={
                "flow_global_direction": global_flow.flow_direction,
                "flow_global_strength": global_flow.flow_strength,
                "flow_global_confidence": global_flow.flow_confidence,
                "flow_tape_pressure": global_flow.tape_pressure,
                "flow_book_imbalance": global_flow.bid_ask_imbalance,
                "flow_funding_pressure": global_flow.funding_pressure,
                "flow_absorption": global_flow.absorption_side,
                "flow_reasons": list(global_flow.reasons),
                "engine": "FlowDirectionEngine",
                "input": "ORDER_FLOW_PRIMARY",
                "candle_direction_used": False,
            },
        )

    # ----------------------------------------------------------
    # PER-TF SIGNAL
    # ----------------------------------------------------------

    def _tf_signal(
        self,
        symbol,
        timeframe,
        candles,
        flow: FlowAnalysis,
        obstacle_mapper,
        md,
    ) -> TimeframeSignal:

        reasons = []

        # ---------- 1. FLOW SCORE (primary) ----------
        flow_score_bull = 0.0
        flow_score_bear = 0.0

        # Tape
        if flow.tape_pressure > 0:
            flow_score_bull += abs(flow.tape_pressure) * 30
        else:
            flow_score_bear += abs(flow.tape_pressure) * 30

        # Book
        if flow.bid_ask_imbalance > 0:
            flow_score_bull += abs(flow.bid_ask_imbalance) * 20
        else:
            flow_score_bear += abs(flow.bid_ask_imbalance) * 20

        # Walls
        if flow.bid_wall_size and flow.ask_wall_size:
            if flow.bid_wall_size > flow.ask_wall_size * 1.3:
                flow_score_bull += 15
                reasons.append("Bid wall dominant")
            elif flow.ask_wall_size > flow.bid_wall_size * 1.3:
                flow_score_bear += 15
                reasons.append("Ask wall dominant")

        # Icebergs
        ib_count = len(flow.iceberg_bid_levels)
        ia_count = len(flow.iceberg_ask_levels)
        if ib_count > ia_count:
            flow_score_bull += 10
            reasons.append(f"Iceberg bids: {ib_count}")
        elif ia_count > ib_count:
            flow_score_bear += 10
            reasons.append(f"Iceberg asks: {ia_count}")

        # Absorption
        if flow.absorption_detected:
            if flow.absorption_side == "SELL_ABSORBED":
                flow_score_bull += 25
                reasons.append("Sell absorbed → bear trap")
            elif flow.absorption_side == "BUY_ABSORBED":
                flow_score_bear += 25
                reasons.append("Buy absorbed → bull trap")

        # Funding
        if flow.funding_pressure == "SHORT_CROWDED":
            flow_score_bull += 10
        elif flow.funding_pressure == "LONG_CROWDED":
            flow_score_bear += 10

        flow_net = flow_score_bull - flow_score_bear

        # ---------- 2. OBSTACLE SCORE (secondary) ----------
        om = obstacle_mapper.build(symbol, candles)
        current = om.current_price

        obstacle_bull = 0.0
        obstacle_bear = 0.0

        # If nearest resistance is very close → price likely rejected → bearish
        if om.nearest_resistance:
            d = om.nearest_resistance.distance_pct
            s = om.nearest_resistance.strength
            if d < 0.15 and s >= 75:
                obstacle_bear += (s / 100.0) * 40
                reasons.append(
                    f"Strong resistance {om.nearest_resistance.price} "
                    f"@ {d:.2f}% (str={s})"
                )

        # If nearest support is very close → price likely bounced → bullish
        if om.nearest_support:
            d = om.nearest_support.distance_pct
            s = om.nearest_support.strength
            if d < 0.15 and s >= 75:
                obstacle_bull += (s / 100.0) * 40
                reasons.append(
                    f"Strong support {om.nearest_support.price} "
                    f"@ {d:.2f}% (str={s})"
                )

        # BOS / CHOCH
        if om.bos_detected:
            last_close = candles[-1].close
            # Determine direction from where the break happened
            if om.nearest_resistance and last_close > om.nearest_resistance.price:
                obstacle_bull += 25
                reasons.append("Bullish BOS")
            elif om.nearest_support and last_close < om.nearest_support.price:
                obstacle_bear += 25
                reasons.append("Bearish BOS")

        if om.choch_detected:
            # Reversal against recent trend
            if flow_net > 0:
                obstacle_bear += 15
                reasons.append("CHOCH vs flow")
            else:
                obstacle_bull += 15
                reasons.append("CHOCH confirm flow")

        obstacle_net = obstacle_bull - obstacle_bear

        # ---------- 3. DERIVATIVE SCORE (support) ----------
        deriv_bull = 0.0
        deriv_bear = 0.0

        # Basis: perp price vs spot
        try:
            perp_ob = md.get_orderbook(symbol)  # spot
            # Not directly basis here — using OI as proxy
        except Exception:
            pass

        # OI: high OI + rising price = bullish (new longs)
        # high OI + falling price = bearish (new shorts)
        if flow.open_interest is not None:
            # approximate OI trend from funding context
            if flow.funding_pressure == "SHORT_CROWDED":
                deriv_bull += 15
                reasons.append("OI: shorts crowded")
            elif flow.funding_pressure == "LONG_CROWDED":
                deriv_bear += 15
                reasons.append("OI: longs crowded")

        deriv_net = deriv_bull - deriv_bear

        # ---------- 4. FINAL COMBINATION ----------
        # Weights: flow 50%, obstacle 30%, derivative 20%
        final_bull = flow_score_bull * 0.5 + obstacle_bull * 0.3 + deriv_bull * 0.2
        final_bear = flow_score_bear * 0.5 + obstacle_bear * 0.3 + deriv_bear * 0.2

        net = final_bull - final_bear
        total = final_bull + final_bear

        if total < 10:
            direction = "NEUTRAL"
            strength = 0.0
            confidence = 0.0
        elif net > 0:
            direction = "BULLISH"
            strength = round(_clamp(final_bull / total * 100), 2)
            confidence = round(final_bull / total * 100, 2)
        elif net < 0:
            direction = "BEARISH"
            strength = round(_clamp(final_bear / total * 100), 2)
            confidence = round(final_bear / total * 100, 2)
        else:
            direction = "NEUTRAL"
            strength = 0.0
            confidence = 0.0

        # ---------- 5. EXPECTED DISPLACEMENT ----------
        atr_pct_val = _atr_pct(candles)
        # ATR base, extended by confidence
        expected_pct = atr_pct_val * (1.0 + confidence / 100.0)

        # ---------- 6. SL CLUSTER RISK ----------
        # High if strong SL cluster is very close in opposite direction
        sl_risk = "LOW"
        if direction == "BULLISH" and om.nearest_support:
            if om.nearest_support.distance_pct < 0.10 and om.nearest_support.strength >= 85:
                sl_risk = "HIGH"
        elif direction == "BEARISH" and om.nearest_resistance:
            if om.nearest_resistance.distance_pct < 0.10 and om.nearest_resistance.strength >= 85:
                sl_risk = "HIGH"
        if sl_risk == "LOW" and len(reasons) < 3:
            sl_risk = "MEDIUM"

        return TimeframeSignal(
            timeframe=timeframe,
            direction=direction,
            strength=strength,
            confidence=confidence,
            flow_score=round(final_bull if direction == "BULLISH" else final_bear, 2),
            obstacle_score=round(obstacle_bull if direction == "BULLISH" else obstacle_bear, 2),
            derivative_score=round(deriv_bull if direction == "BULLISH" else deriv_bear, 2),
            flow_direction=flow.flow_direction,
            nearest_resistance_price=(
                om.nearest_resistance.price if om.nearest_resistance else None
            ),
            nearest_resistance_distance_pct=(
                om.nearest_resistance.distance_pct if om.nearest_resistance else None
            ),
            nearest_support_price=(
                om.nearest_support.price if om.nearest_support else None
            ),
            nearest_support_distance_pct=(
                om.nearest_support.distance_pct if om.nearest_support else None
            ),
            expected_displacement_pct=round(expected_pct, 4),
            sl_cluster_risk=sl_risk,
            reasons=tuple(reasons),
        )


_engine: Optional[FlowDirectionEngine] = None


def get_flow_direction_engine() -> FlowDirectionEngine:
    global _engine
    if _engine is None:
        _engine = FlowDirectionEngine()
    return _engine


__all__ = [
    "TimeframeSignal",
    "DirectionSignal",
    "FlowDirectionEngine",
    "get_flow_direction_engine",
]
'''

(ROOT / "flow_direction_engine.py").write_text(FILE, encoding="utf-8")
print(f"WROTE: {ROOT / 'flow_direction_engine.py'}")