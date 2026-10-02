"""Install unified_signal.py — final D13-ready signal from all engines"""
from pathlib import Path

ROOT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\intelligence\real")

FILE = '''"""
ROBOMLM_PLUS - Unified Signal Engine

FINAL intelligence output for D13 consumption.

Combines:
    1. Order Flow      (tape + book + absorption)
    2. Derivatives     (basis, OI, funding, L/S)
    3. Volume          (delta, whales, ROC, divergence)
    4. Obstacles       (SMC, VWAP, Pivots)
    5. Levels          (institutional levels)
    6. Context         (session, vol regime, correlations)
    7. Advanced Stats  (Hurst, entropy, regime)

Produces ONE authoritative signal per symbol with:
    - Direction (BUY/SELL/HOLD)
    - Confidence (0-100)
    - Expected move (%)
    - Entry/SL/TP guidance
    - Full audit trail

Candle direction is NEVER used as primary.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from app.intelligence.real.real_market_data import get_real_market_data
from app.intelligence.real.order_flow_engine import get_order_flow_engine
from app.intelligence.real.obstacle_mapper import get_obstacle_mapper
from app.intelligence.real.derivatives_engine import get_derivatives_engine
from app.intelligence.real.levels_engine import get_levels_engine
from app.intelligence.real.volume_engine import get_volume_engine
from app.intelligence.real.market_context_engine import get_market_context_engine
from app.intelligence.real.advanced_stats_engine import get_advanced_stats_engine


# ============================================================
# RESULT
# ============================================================

@dataclass(frozen=True)
class UnifiedSignal:
    symbol: str
    timestamp: str

    # FINAL VERDICT
    direction: str                 # BULLISH | BEARISH | NEUTRAL
    action: str                    # BUY | SELL | HOLD
    confidence: float              # 0-100
    strength: float                # 0-100

    # Component scores (0-100 each)
    flow_score: float
    derivative_score: float
    volume_score: float
    obstacle_score: float
    context_score: float
    regime_score: float

    # Trade guidance
    entry_price: float
    stop_loss: Optional[float]
    take_profit: Optional[float]
    risk_reward: Optional[float]
    expected_move_pct: float
    suggested_size_pct: float      # % of capital

    # Quality filter
    trade_quality: str             # A+ | A | B+ | B | HOLD
    trade_grade_reason: str

    # Risk
    risk_level: str                # LOW | MEDIUM | HIGH | EXTREME
    warnings: tuple

    # Audit — every component's own verdict
    audit: dict = field(default_factory=dict)

    def to_dict(self):
        def r(v):
            return round(v, 6) if v is not None else None
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp,
            "verdict": {
                "direction": self.direction,
                "action": self.action,
                "confidence": self.confidence,
                "strength": self.strength,
            },
            "components": {
                "flow": self.flow_score,
                "derivative": self.derivative_score,
                "volume": self.volume_score,
                "obstacle": self.obstacle_score,
                "context": self.context_score,
                "regime": self.regime_score,
            },
            "trade": {
                "entry": self.entry_price,
                "stop_loss": self.stop_loss,
                "take_profit": self.take_profit,
                "risk_reward": self.risk_reward,
                "expected_move_pct": self.expected_move_pct,
                "suggested_size_pct": self.suggested_size_pct,
            },
            "quality": {
                "grade": self.trade_quality,
                "reason": self.trade_grade_reason,
            },
            "risk": {
                "level": self.risk_level,
                "warnings": list(self.warnings),
            },
            "audit": dict(self.audit),
        }


def _clamp(v, lo=0.0, hi=100.0):
    return max(lo, min(hi, v))


# ============================================================
# ENGINE
# ============================================================

class UnifiedSignalEngine:

    # Weights — flow first, per user priority
    WEIGHTS = {
        "flow": 0.30,
        "volume": 0.15,
        "derivative": 0.15,
        "obstacle": 0.10,
        "context": 0.05,
        "regime": 0.10,
        "levels": 0.15,   # levels work through obstacles actually, but weight it here
    }

    def compute(self, symbol: str) -> UnifiedSignal:

        now = datetime.now(timezone.utc)
        md = get_real_market_data()

        current_price = md.get_last_price(symbol) or 0.0

        # ----------------------------------------------------
        # RUN ALL ENGINES
        # ----------------------------------------------------
        candles_1m, _ = md.get_candles(symbol, "1", 100)

        try:
            flow = get_order_flow_engine().analyze(symbol, candles_1m)
        except Exception as e:
            flow = None

        try:
            candles_15m, _ = md.get_candles(symbol, "15", 200)
            om = get_obstacle_mapper().build(symbol, candles_15m) if candles_15m else None
        except Exception:
            om = None

        try:
            deriv = get_derivatives_engine().analyze(symbol, current_price)
        except Exception:
            deriv = None

        try:
            levels = get_levels_engine().compute(symbol)
        except Exception:
            levels = None

        try:
            vol = get_volume_engine().compute(symbol)
        except Exception:
            vol = None

        try:
            ctx = get_market_context_engine().compute(symbol)
        except Exception:
            ctx = None

        try:
            stats = get_advanced_stats_engine().compute(symbol)
        except Exception:
            stats = None

        # ----------------------------------------------------
        # COMPONENT SCORING
        # ----------------------------------------------------
        warnings = []
        reasons = []

        # FLOW (30%)
        flow_bull = flow_bear = 0.0
        if flow:
            if flow.flow_direction == "BULLISH":
                flow_bull = flow.flow_strength
            elif flow.flow_direction == "BEARISH":
                flow_bear = flow.flow_strength
            reasons.extend(flow.reasons)

        # VOLUME (15%)
        vol_bull = vol_bear = 0.0
        if vol:
            if vol.volume_direction == "BULLISH":
                vol_bull = vol.volume_strength
            elif vol.volume_direction == "BEARISH":
                vol_bear = vol.volume_strength
            reasons.extend(vol.reasons)

        # DERIVATIVES (15%)
        deriv_bull = deriv_bear = 0.0
        if deriv:
            if deriv.derivative_direction == "BULLISH":
                deriv_bull = deriv.derivative_strength
            elif deriv.derivative_direction == "BEARISH":
                deriv_bear = deriv.derivative_strength
            reasons.extend(deriv.reasons)

        # OBSTACLE (10%)
        obstacle_bull = obstacle_bear = 0.0
        if om and current_price > 0:
            # If nearest support is strong and close → bullish bounce
            if om.nearest_support and om.nearest_support.distance_pct < 0.3 and om.nearest_support.strength >= 75:
                obstacle_bull = min(100.0, om.nearest_support.strength + (0.3 - om.nearest_support.distance_pct) * 50)
            # If nearest resistance is strong and close → bearish rejection
            if om.nearest_resistance and om.nearest_resistance.distance_pct < 0.3 and om.nearest_resistance.strength >= 75:
                obstacle_bear = min(100.0, om.nearest_resistance.strength + (0.3 - om.nearest_resistance.distance_pct) * 50)
            if om.bos_detected:
                reasons.append("BOS active")

        # CONTEXT (5%) — modifier, not directional
        context_score = 0.0
        context_modifier = 1.0
        if ctx:
            context_score = ctx.activity_score
            if ctx.vol_regime == "EXTREME":
                context_modifier = 0.6
                warnings.append("Extreme volatility — reduced size")
            elif ctx.vol_regime == "HIGH":
                context_modifier = 0.85
            if ctx.session == "QUIET":
                context_modifier *= 0.9
                warnings.append("Quiet session — wide spreads")

        # REGIME (10%) — modifier for signal quality
        regime_score = 0.0
        regime_modifier = 1.0
        if stats:
            regime_score = stats.regime_strength
            if stats.market_regime == "TRENDING":
                regime_modifier = 1.2   # trending regime amplifies directional signals
            elif stats.market_regime == "RANGING":
                regime_modifier = 0.85  # ranging kills trend follow
            elif stats.market_regime == "CHAOTIC":
                regime_modifier = 0.5
                warnings.append("Chaotic regime — avoid")

        # LEVELS (15%) — pivot / vwap direction
        levels_bull = levels_bear = 0.0
        if levels and current_price > 0:
            if levels.vwap_daily:
                if current_price > levels.vwap_daily:
                    levels_bull = 40.0
                elif current_price < levels.vwap_daily:
                    levels_bear = 40.0
            if levels.pivot_pp:
                if current_price > levels.pivot_pp:
                    levels_bull += 20
                else:
                    levels_bear += 20
            # If near upper band → mean reversion down
            if levels.vwap_upper_2 and current_price >= levels.vwap_upper_2:
                levels_bear += 20
                warnings.append("Price at 2σ upper VWAP band")
            elif levels.vwap_lower_2 and current_price <= levels.vwap_lower_2:
                levels_bull += 20
                warnings.append("Price at 2σ lower VWAP band")

        # ----------------------------------------------------
        # WEIGHTED COMBINATION
        # ----------------------------------------------------
        w = self.WEIGHTS

        final_bull = (
            flow_bull * w["flow"] +
            vol_bull * w["volume"] +
            deriv_bull * w["derivative"] +
            obstacle_bull * w["obstacle"] +
            levels_bull * w["levels"]
        )

        final_bear = (
            flow_bear * w["flow"] +
            vol_bear * w["volume"] +
            deriv_bear * w["derivative"] +
            obstacle_bear * w["obstacle"] +
            levels_bear * w["levels"]
        )

        # Apply context + regime modifiers
        total_modifier = context_modifier * regime_modifier
        final_bull *= total_modifier
        final_bear *= total_modifier

        total = final_bull + final_bear

        if total < 15:
            direction = "NEUTRAL"
            strength = 0.0
            confidence = 0.0
        elif final_bull > final_bear * 1.15:
            direction = "BULLISH"
            strength = round(_clamp(final_bull), 2)
            confidence = round(final_bull / total * 100, 2)
        elif final_bear > final_bull * 1.15:
            direction = "BEARISH"
            strength = round(_clamp(final_bear), 2)
            confidence = round(final_bear / total * 100, 2)
        else:
            direction = "NEUTRAL"
            strength = round(_clamp(max(final_bull, final_bear)), 2)
            confidence = 50.0

        # ----------------------------------------------------
        # ACTION
        # ----------------------------------------------------
        if direction == "BULLISH" and confidence >= 60:
            action = "BUY"
        elif direction == "BEARISH" and confidence >= 60:
            action = "SELL"
        else:
            action = "HOLD"

        # ----------------------------------------------------
        # TRADE GUIDANCE
        # ----------------------------------------------------
        entry = current_price
        sl = tp = None
        rr = None

        if action in {"BUY", "SELL"} and om:
            if action == "BUY":
                # SL below nearest support
                if om.nearest_support and om.nearest_support.price:
                    sl = om.nearest_support.price * 0.999
                elif levels and levels.vwap_daily:
                    sl = levels.vwap_daily * 0.998
                # TP at nearest strong resistance
                if om.nearest_resistance and om.nearest_resistance.price:
                    tp = om.nearest_resistance.price * 0.999
            elif action == "SELL":
                if om.nearest_resistance and om.nearest_resistance.price:
                    sl = om.nearest_resistance.price * 1.001
                elif levels and levels.vwap_daily:
                    sl = levels.vwap_daily * 1.002
                if om.nearest_support and om.nearest_support.price:
                    tp = om.nearest_support.price * 1.001

            if sl and tp and entry > 0:
                risk = abs(entry - sl)
                reward = abs(tp - entry)
                rr = (reward / risk) if risk > 0 else None

        # ----------------------------------------------------
        # EXPECTED MOVE
        # ----------------------------------------------------
        expected_move = 0.0
        if candles_1m and len(candles_1m) >= 15:
            # ATR from 1m
            trs = []
            for i in range(1, 15):
                c = candles_1m[-i]
                prev = candles_1m[-i - 1]
                tr = max(c.high - c.low, abs(c.high - prev.close), abs(c.low - prev.close))
                trs.append(tr)
            atr = sum(trs) / len(trs)
            expected_move = (atr / current_price * 100) if current_price > 0 else 0.0
            expected_move = round(expected_move * (1.0 + confidence / 100.0), 4)

        # ----------------------------------------------------
        # TRADE QUALITY GRADE
        # ----------------------------------------------------
        # Score = combined confidence + regime + RR
        quality_score = confidence
        if rr and rr >= 2.0:
            quality_score += 10
        elif rr and rr < 1.0:
            quality_score -= 15

        if stats and stats.market_regime == "TRENDING":
            quality_score += 10
        if stats and stats.market_regime == "CHAOTIC":
            quality_score -= 20

        if ctx and ctx.vol_regime == "EXTREME":
            quality_score -= 15

        # Grade
        if quality_score >= 75 and action in {"BUY", "SELL"}:
            grade = "A+"
            grade_reason = "High confidence + trend regime + good RR"
        elif quality_score >= 55 and action in {"BUY", "SELL"}:
            grade = "A"
            grade_reason = "Good confidence + acceptable RR"
        elif quality_score >= 45 and action in {"BUY", "SELL"}:
            grade = "B+"
            grade_reason = "Moderate confidence"
        elif quality_score >= 30 and action in {"BUY", "SELL"}:
            grade = "B"
            grade_reason = "Low confidence — small position only"
        else:
            grade = "HOLD"
            grade_reason = "Insufficient quality — no trade"

        # ----------------------------------------------------
        # SUGGESTED SIZE
        # ----------------------------------------------------
        # Base 1%, scaled by grade
        size_map = {"A+": 2.0, "A": 1.5, "B+": 1.0, "B": 0.5, "HOLD": 0.0}
        size_pct = size_map.get(grade, 0.0)

        # Risk level
        risk_level = "LOW"
        if ctx and ctx.vol_regime == "EXTREME":
            risk_level = "EXTREME"
        elif ctx and ctx.vol_regime == "HIGH":
            risk_level = "HIGH"
        elif stats and stats.market_regime == "CHAOTIC":
            risk_level = "HIGH"
        elif grade in {"B+", "B"}:
            risk_level = "MEDIUM"

        # ----------------------------------------------------
        # AUDIT
        # ----------------------------------------------------
        audit = {
            "engine": "UnifiedSignalEngine",
            "version": "1.0",
            "primary_input": "ORDER_FLOW",
            "candle_direction_used": False,
            "flow": {
                "direction": flow.flow_direction if flow else None,
                "strength": flow.flow_strength if flow else None,
                "tape_pressure": flow.tape_pressure if flow else None,
                "book_imbalance": flow.bid_ask_imbalance if flow else None,
                "absorption": flow.absorption_side if flow else None,
            },
            "derivatives": {
                "direction": deriv.derivative_direction if deriv else None,
                "basis": deriv.basis_pct if deriv else None,
                "funding_state": deriv.funding_state if deriv else None,
                "oi_interp": deriv.oi_interpretation if deriv else None,
            },
            "volume": {
                "direction": vol.volume_direction if vol else None,
                "delta_trend": vol.delta_trend if vol else None,
                "whale_signal": vol.smart_money_signal if vol else None,
                "roc_signal": vol.roc_signal if vol else None,
                "divergence": vol.divergence_type if vol else None,
            },
            "regime": {
                "type": stats.market_regime if stats else None,
                "hurst": stats.hurst_exponent if stats else None,
                "entropy": stats.shannon_entropy if stats else None,
                "autocorr": stats.autocorr_lag1 if stats else None,
            },
            "context": {
                "session": ctx.session if ctx else None,
                "vol_regime": ctx.vol_regime if ctx else None,
                "activity": ctx.activity_score if ctx else None,
            },
            "modifiers": {
                "context_modifier": round(context_modifier, 4),
                "regime_modifier": round(regime_modifier, 4),
                "total_modifier": round(total_modifier, 4),
            },
            "reasons": reasons[:20],  # top 20
        }

        return UnifiedSignal(
            symbol=symbol,
            timestamp=now.isoformat(),
            direction=direction,
            action=action,
            confidence=confidence,
            strength=strength,
            flow_score=round(flow_bull if direction == "BULLISH" else flow_bear, 2),
            derivative_score=round(deriv_bull if direction == "BULLISH" else deriv_bear, 2),
            volume_score=round(vol_bull if direction == "BULLISH" else vol_bear, 2),
            obstacle_score=round(obstacle_bull if direction == "BULLISH" else obstacle_bear, 2),
            context_score=round(context_score, 2),
            regime_score=round(regime_score, 2),
            entry_price=round(entry, 6),
            stop_loss=round(sl, 6) if sl is not None else None,
            take_profit=round(tp, 6) if tp is not None else None,
            risk_reward=round(rr, 4) if rr is not None else None,
            expected_move_pct=expected_move,
            suggested_size_pct=size_pct,
            trade_quality=grade,
            trade_grade_reason=grade_reason,
            risk_level=risk_level,
            warnings=tuple(warnings),
            audit=audit,
        )


_engine: Optional[UnifiedSignalEngine] = None
_lock = None


def get_unified_signal_engine() -> UnifiedSignalEngine:
    global _engine, _lock
    if _lock is None:
        from threading import RLock
        _lock = RLock()
    with _lock:
        if _engine is None:
            _engine = UnifiedSignalEngine()
        return _engine


__all__ = [
    "UnifiedSignal",
    "UnifiedSignalEngine",
    "get_unified_signal_engine",
]
'''

(ROOT / "unified_signal.py").write_text(FILE, encoding="utf-8")
print(f"WROTE: {ROOT / 'unified_signal.py'}")
print()
print("Test:")
print('  python -c "from app.intelligence.real.unified_signal import get_unified_signal_engine; import json; s = get_unified_signal_engine().compute(\\"BTC/USDT\\"); print(json.dumps(s.to_dict(), indent=2, default=str))"')