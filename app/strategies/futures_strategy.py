"""Futures market strategy.

V1:
- Consumes existing backend intelligence only.
- Does not create new market-data formulas.
- Does not execute trades.
- Does not bypass downstream risk gates.
"""

from __future__ import annotations

from app.strategies.base import (
    BaseStrategy,
    StrategyInput,
    StrategyOutput,
)


class FuturesStrategy(BaseStrategy):
    ID = "FUTURES"
    VERSION = "1.0"

    MIN_SCORE = 30.0

    def decide(self, data: StrategyInput) -> StrategyOutput:
        direction = str(data.direction).upper()
        action = str(data.action).upper()

        if direction not in {"BULLISH", "BEARISH"}:
            return self._reject("FUTURES_NEUTRAL_DIRECTION", data)

        if action not in {"BUY", "SELL"}:
            return self._reject("FUTURES_INVALID_ACTION", data)

        score = self._score(data)

        if score < self.MIN_SCORE:
            return self._reject(
                "FUTURES_SCORE_BELOW_B",
                data,
                score,
            )

        return StrategyOutput(
            strategy_id=self.ID,
            direction="BUY" if direction == "BULLISH" else "SELL",
            entry_permission=True,
            strategy_score=score,
            confidence=float(data.confidence),
            timing_quality=self._timing(data),
            risk_quality=self._risk(data),
            reason_codes=("FUTURES_STRATEGY_PASS",),
            notes=(
                "V1 futures strategy interpreted existing "
                "backend intelligence."
            ),
        )

    def _score(self, data: StrategyInput) -> float:
        values = [
            float(data.strength),
            float(data.confidence),
            self._component(data, "flow"),
            self._component(data, "derivative"),
            self._component(data, "context"),
            self._component(data, "regime"),
        ]

        return max(
            0.0,
            min(100.0, sum(values) / len(values)),
        )

    def _timing(self, data: StrategyInput) -> float:
        return max(
            0.0,
            min(
                100.0,
                self._component(data, "flow") * 0.50
                + self._component(data, "volume") * 0.50,
            ),
        )

    def _risk(self, data: StrategyInput) -> float:
        return max(
            0.0,
            min(
                100.0,
                self._component(data, "context") * 0.50
                + self._component(data, "regime") * 0.50,
            ),
        )

    @staticmethod
    def _component(
        data: StrategyInput,
        name: str,
    ) -> float:
        try:
            return max(
                0.0,
                min(100.0, float(data.components.get(name, 0.0))),
            )
        except (TypeError, ValueError):
            return 0.0

    def _reject(
        self,
        reason: str,
        data: StrategyInput,
        score: float = 0.0,
    ) -> StrategyOutput:
        direction = str(data.direction).upper()

        return StrategyOutput(
            strategy_id=self.ID,
            direction=(
                "BUY"
                if direction == "BULLISH"
                else "SELL"
            ),
            entry_permission=False,
            strategy_score=score,
            confidence=float(data.confidence),
            timing_quality=0.0,
            risk_quality=0.0,
            reason_codes=(reason,),
            notes="V1 futures strategy rejected entry.",
        )