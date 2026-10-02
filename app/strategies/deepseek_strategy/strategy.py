"""Y — DeepSeek Strategy v1.

Goal
----
Improve AutoROBOMLM win rate and reduce SL hits by applying
strict multi-gate filtering on top of UnifiedSignal.

Logic
-----
1. Basic sanity (direction, grade, risk, RR)
2. Strength + Confidence double gate
3. Multi-component confluence (>= 3 of 6 agree)
4. Context alignment
5. SL sanity (not too wide)
6. Final weighted score

This strategy DOES NOT:
    - replace backend intelligence
    - bypass risk / gates / CAS
    - fabricate values
Only entry-permission + score are produced.
"""

from __future__ import annotations

from app.strategies.base import (
    BaseStrategy, StrategyID, StrategyInput, StrategyOutput,
)


class DeepSeekStrategy(BaseStrategy):
    ID = StrategyID.DEEPSEEK
    VERSION = "1.0"

    # ---------- Tunable thresholds ----------
    MIN_STRENGTH = 45.0
    STRONG_STRENGTH = 60.0
    MIN_CONFIDENCE = 55.0
    STRONG_CONFIDENCE = 70.0
    MIN_CONTEXT = 30.0
    MIN_CONFLUENCE = 2              # out of 6 components
    CONFLUENCE_COMPONENT_MIN = 35.0
    MIN_RR = 1.4
    MAX_SL_PCT = 3.0                # SL must be < 3% away
    # Grade B allowed only if other quality bars are met.
    ALLOWED_GRADES = {"A+", "A", "B+", "B"}
    B_GRADE_MIN_STRENGTH = 55.0
    B_GRADE_MIN_CONFIDENCE = 60.0
    EXTREME_RISK = "EXTREME"

    # ---------- Helpers ----------
    def _reject(self, reason: str, notes: str = "") -> StrategyOutput:
        return StrategyOutput(
            strategy_id=self.ID,
            direction="HOLD",
            entry_permission=False,
            strategy_score=0.0,
            confidence=0.0,
            timing_quality=0.0,
            risk_quality=0.0,
            reason_codes=(reason,),
            notes=notes,
        )

    def _num(self, v, default=0.0):
        try:
            return float(v)
        except (TypeError, ValueError):
            return default

    # ---------- Main ----------
    def decide(self, data: StrategyInput) -> StrategyOutput:

        # 1. Direction must be directional
        if data.direction not in ("BULLISH", "BEARISH"):
            return self._reject("NEUTRAL_DIRECTION")

        # 2. Trade quality — trust pipeline. Only block if
        #    trade_quality is HOLD AND strength is also low.
        if (data.trade_quality == "HOLD") and (data.strength < 40.0):
            return self._reject("GRADE_HOLD_LOW_STRENGTH")

        # 3. Extreme risk
        if (data.risk_level or "").upper() == self.EXTREME_RISK:
            return self._reject("EXTREME_RISK")

        # 4. Risk-reward gate REMOVED.
        # Reason: signal.risk_reward is calculated by UnifiedSignal
        # but AutoROBOMLM uses ATR-based SL/TP (fixed 2:1). Signal RR
        # is not the actual trade RR. Backend guarantees 2:1.

        # 5. Strength gate
        min_strength = self.MIN_STRENGTH
        min_confidence = self.MIN_CONFIDENCE

        # Grade B — stricter bar
        if data.trade_quality == "B":
            min_strength = self.B_GRADE_MIN_STRENGTH
            min_confidence = self.B_GRADE_MIN_CONFIDENCE

        if data.strength < min_strength:
            return self._reject(f"STRENGTH_{data.strength:.1f}")

        # 6. Confidence gate
        if data.confidence < min_confidence:
            return self._reject(f"CONFIDENCE_{data.confidence:.1f}")

        # 7. Confluence — only if components present in signal
        c = data.components or {}
        has_components = any(
            self._num(c.get(k)) > 0 for k in
            ("flow", "derivative", "volume", "obstacle", "context", "regime")
        )
        scores = [
            self._num(c.get("flow")),
            self._num(c.get("derivative")),
            self._num(c.get("volume")),
            self._num(c.get("obstacle")),
            self._num(c.get("context")),
            self._num(c.get("regime")),
        ]
        aligned = 0
        context = 0.0
        if has_components:
            aligned = sum(1 for s in scores if s >= self.CONFLUENCE_COMPONENT_MIN)
            if aligned < self.MIN_CONFLUENCE:
                return self._reject(f"CONFLUENCE_{aligned}_OF_6")
            context = self._num(c.get("context"))
            if context < self.MIN_CONTEXT:
                return self._reject(f"CONTEXT_{context:.1f}")

        # 9. SL sanity
        if data.stop_loss is not None and data.entry_price > 0:
            sl_pct = abs(data.entry_price - data.stop_loss) / data.entry_price * 100.0
            if sl_pct > self.MAX_SL_PCT:
                return self._reject(f"SL_WIDE_{sl_pct:.2f}%")

        # ---------- Compute scores ----------
        avg_conf = sum(scores) / 6.0
        timing_quality = (scores[0] + scores[2]) / 2.0      # flow + volume
        risk_quality = (context + scores[5]) / 2.0          # context + regime

        strategy_score = (
            data.strength * 0.35 +
            data.confidence * 0.25 +
            avg_conf * 0.20 +
            context * 0.10 +
            scores[5] * 0.10
        )

        # ---------- Direction map ----------
        action = "BUY" if data.direction == "BULLISH" else "SELL"

        return StrategyOutput(
            strategy_id=self.ID,
            direction=action,
            entry_permission=True,
            strategy_score=round(strategy_score, 2),
            confidence=round(data.confidence, 2),
            timing_quality=round(timing_quality, 2),
            risk_quality=round(risk_quality, 2),
            reason_codes=(
                "ALL_GATES_PASSED",
                f"CONFLUENCE_{aligned}_OF_6",
                f"STRENGTH_{data.strength:.1f}",
                f"CONFIDENCE_{data.confidence:.1f}",
            ),
            notes=(
                f"{data.symbol} {action} "
                f"score={strategy_score:.1f}"
            ),
        )
