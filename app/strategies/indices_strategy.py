"""Indices market strategy.

V1 deliberately does not invent option-chain formulas.
It consumes existing derivative/context/regime intelligence.
"""

from __future__ import annotations

from app.strategies.base import (
    BaseStrategy,
    StrategyInput,
    StrategyOutput,
)


class IndicesStrategy(BaseStrategy):
    ID = "INDICES"
    VERSION = "1.0"

    MIN_SCORE = 30.0

    def decide(self, data: StrategyInput) -> StrategyOutput:
        direction = str(data.direction).upper()
        action = str(data.action).upper()

        if direction not in {"BULLISH", "BEARISH"}:
            return self._reject(
                "INDICES_NEUTRAL_DIRECTION",
                data,
            )

        if action not in {"BUY", "SELL"}:
            return self._reject(
                "INDICES_INVALID_ACTION",
                data,
            )

        score = self._score(data)

        if score < self.MIN_SCORE:
            return self._reject(
                "INDICES_SCORE_BELOW_B",
                data,
                score,
            )

        return StrategyOutput(
            strategy_id=self.ID,
            direction="BUY" if direction == "BULLISH" else "SELL",
            entry_permission=True,
            strategy_score=score,
            confidence=float(data.confidence),
            timing_quality=self._component(data, "derivative"),
            risk_quality=self._component(data, "context"),
            reason_codes=("INDICES_STRATEGY_PASS",),
            notes=(
                "V1 indices strategy interpreted existing "
                "backend intelligence."
            ),
        )

    def _score(self, data: StrategyInput) -> float:
        values = [
            float(data.strength),
            float(data.confidence),
            self._component(data, "derivative"),
            self._component(data, "flow"),
            self._component(data, "context"),
            self._component(data, "regime"),
        ]

        return max(
            0.0,
            min(100.0, sum(values) / len(values)),
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
            notes="V1 indices strategy rejected entry.",
        )