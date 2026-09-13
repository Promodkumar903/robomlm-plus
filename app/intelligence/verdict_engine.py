from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from statistics import mean
from typing import Any, Mapping


class Verdict(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    REJECT = "REJECT"
    CONFLICTED = "CONFLICTED"
    INSUFFICIENT = "INSUFFICIENT"


class VerdictState(str, Enum):
    STRONG = "STRONG"
    ACTIONABLE = "ACTIONABLE"
    DEVELOPING = "DEVELOPING"
    WEAK = "WEAK"
    REJECTED = "REJECTED"
    CONFLICTED = "CONFLICTED"
    INSUFFICIENT = "INSUFFICIENT"


@dataclass(frozen=True)
class VerdictAssessment:
    verdict: str
    state: str
    verdict_score: float
    confidence: float
    evidence_score: float
    context_score: float
    intelligence_score: float
    commitment_score: float
    timing_score: float
    magnitude_score: float
    relationship_score: float
    strategy_score: float
    risk_score: float
    directional_alignment: float
    decision_ready: bool
    contradictions: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()
    risk_flags: tuple[str, ...] = ()
    evidence: Mapping[str, Any] = field(default_factory=dict)
    timestamp: str = ""


class VerdictEngine:
    """
    ROBOMLM Final Verdict Engine.

    This is the final intelligence synthesis layer.

    It does NOT:
        - place orders
        - authorize execution
        - modify positions
        - bypass risk
        - bypass kill-switch
        - communicate directly with a broker

    The engine converts upstream intelligence into a coherent
    market verdict.

    Core weighted model:

        V =
            E  * 0.15
          + M  * 0.15
          + I  * 0.15
          + C  * 0.10
          + T  * 0.10
          + G  * 0.10
          + R  * 0.10
          + S  * 0.05
          + RK * 0.10

    Where:

        E  = Evidence
        M  = Market Context
        I  = Intelligence
        C  = Commitment
        T  = Timing
        G  = Magnitude
        R  = Relationship
        S  = Strategy
        RK = Risk Quality

    Directional alignment is independently calculated so that a high
    numerical score cannot hide a BUY/SELL contradiction.

    Hard gates:
        evidence
        context
        intelligence
        commitment
        timing
        risk
        liquidity
        contradiction state

    Final verdict is therefore a gated synthesis, not a simple average.
    """

    VERSION = "ROBOMLM-VERDICT-2.0"

    WEIGHTS = {
        "evidence": 0.15,
        "context": 0.15,
        "intelligence": 0.15,
        "commitment": 0.10,
        "timing": 0.10,
        "magnitude": 0.10,
        "relationship": 0.10,
        "strategy": 0.05,
        "risk": 0.10,
    }

    STRONG_THRESHOLD = 85.0
    ACTIONABLE_THRESHOLD = 70.0
    DEVELOPING_THRESHOLD = 50.0
    WEAK_THRESHOLD = 35.0

    MIN_EVIDENCE = 40.0
    MIN_CONTEXT = 40.0
    MIN_INTELLIGENCE = 50.0
    MIN_COMMITMENT = 50.0
    MIN_TIMING = 40.0
    MIN_RISK = 40.0
    MIN_LIQUIDITY = 30.0
    MIN_ALIGNMENT = 50.0

    def __init__(self) -> None:
        self._history: list[VerdictAssessment] = []

    # ------------------------------------------------------------------
    # Generic helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _number(value: Any, default: float = 0.0) -> float:
        try:
            number = float(value)
            return number if number == number else default
        except (TypeError, ValueError):
            return default

    @classmethod
    def _score(
        cls,
        value: Any,
        default: float = 50.0,
    ) -> float:
        number = cls._number(value, default)

        if -1.0 <= number <= 1.0:
            number = (number + 1.0) * 50.0

        return max(0.0, min(100.0, number))

    @staticmethod
    def _text(value: Any) -> str:
        if value is None:
            return ""
        return str(value).strip().upper()

    @staticmethod
    def _value(
        data: Mapping[str, Any] | None,
        *keys: str,
        default: Any = None,
    ) -> Any:
        if not data:
            return default

        for key in keys:
            if key in data and data[key] is not None:
                return data[key]

        return default

    # ------------------------------------------------------------------
    # Direction
    # ------------------------------------------------------------------

    @staticmethod
    def _direction(value: Any) -> str:
        text = "" if value is None else str(value).strip().upper()

        if text in {"BUY", "LONG", "UP", "BULLISH"}:
            return "BUY"

        if text in {"SELL", "SHORT", "DOWN", "BEARISH"}:
            return "SELL"

        if text in {"HOLD", "NEUTRAL", "FLAT", ""}:
            return "NEUTRAL"

        if text in {
            "CONFLICTED",
            "CONFLICT",
            "MIXED",
        }:
            return "CONFLICTED"

        return text

    # ------------------------------------------------------------------
    # Component extraction
    # ------------------------------------------------------------------

    def _component(
        self,
        data: Mapping[str, Any],
        *keys: str,
        default: float = 50.0,
    ) -> float:
        return self._score(
            self._value(
                data,
                *keys,
                default=default,
            ),
            default,
        )

    # ------------------------------------------------------------------
    # Directional alignment
    # ------------------------------------------------------------------

    def _directional_alignment(
        self,
        data: Mapping[str, Any],
    ) -> tuple[float, str, list[str]]:
        directional_keys = (
            "evidence_bias",
            "context_bias",
            "intelligence_bias",
            "commitment_bias",
            "timing_bias",
            "relationship_bias",
            "strategy_bias",
            "direction",
            "bias",
        )

        directions: list[str] = []

        for key in directional_keys:
            value = self._value(data, key, default=None)

            if value is None:
                continue

            direction = self._direction(value)

            if direction in {"BUY", "SELL"}:
                directions.append(direction)
            elif direction == "CONFLICTED":
                directions.append(direction)

        if not directions:
            return 50.0, "NEUTRAL", []

        explicit_conflict = any(
            direction == "CONFLICTED"
            for direction in directions
        )

        if explicit_conflict:
            return 0.0, "CONFLICTED", [
                "explicit_directional_conflict"
            ]

        buys = directions.count("BUY")
        sells = directions.count("SELL")
        total = buys + sells

        if total == 0:
            return 50.0, "NEUTRAL", []

        dominant = "BUY" if buys > sells else "SELL"

        if buys == sells:
            return 0.0, "CONFLICTED", [
                "balanced_buy_sell_evidence"
            ]

        alignment = (
            max(buys, sells) / total
        ) * 100.0

        return round(alignment, 4), dominant, []

    # ------------------------------------------------------------------
    # Contradictions
    # ------------------------------------------------------------------

    def _contradictions(
        self,
        data: Mapping[str, Any],
        components: Mapping[str, float],
        alignment: float,
        direction: str,
    ) -> list[str]:
        contradictions: list[str] = []

        if direction == "CONFLICTED":
            contradictions.append("directional_conflict")

        if alignment < self.MIN_ALIGNMENT:
            contradictions.append("directional_alignment_below_minimum")

        if components["evidence"] < self.MIN_EVIDENCE:
            contradictions.append("insufficient_evidence")

        if components["context"] < self.MIN_CONTEXT:
            contradictions.append("insufficient_market_context")

        if components["intelligence"] < self.MIN_INTELLIGENCE:
            contradictions.append("insufficient_intelligence")

        if components["commitment"] < self.MIN_COMMITMENT:
            contradictions.append("insufficient_commitment")

        if components["timing"] < self.MIN_TIMING:
            contradictions.append("timing_below_minimum")

        if components["risk"] < self.MIN_RISK:
            contradictions.append("risk_quality_below_minimum")

        liquidity = self._component(
            data,
            "liquidity_score",
            "liquidity_quality",
            "liquidity",
            default=50.0,
        )

        if liquidity < self.MIN_LIQUIDITY:
            contradictions.append("liquidity_below_minimum")

        upstream_contradictions = self._value(
            data,
            "contradictions",
            "conflicts",
            default=None,
        )

        if isinstance(
            upstream_contradictions,
            (list, tuple, set),
        ):
            for item in upstream_contradictions:
                text = str(item).strip()

                if text:
                    contradictions.append(
                        f"upstream:{text}"
                    )

        elif upstream_contradictions:
            contradictions.append(
                f"upstream:{upstream_contradictions}"
            )

        return list(dict.fromkeys(contradictions))

    # ------------------------------------------------------------------
    # Composite formula
    # ------------------------------------------------------------------

    def calculate_verdict_score(
        self,
        *,
        evidence: float,
        context: float,
        intelligence: float,
        commitment: float,
        timing: float,
        magnitude: float,
        relationship: float,
        strategy: float,
        risk: float,
    ) -> float:
        """
        Canonical verdict equation:

            V =
                E*0.15
              + M*0.15
              + I*0.15
              + C*0.10
              + T*0.10
              + G*0.10
              + R*0.10
              + S*0.05
              + RK*0.10
        """
        score = (
            evidence * self.WEIGHTS["evidence"]
            + context * self.WEIGHTS["context"]
            + intelligence * self.WEIGHTS["intelligence"]
            + commitment * self.WEIGHTS["commitment"]
            + timing * self.WEIGHTS["timing"]
            + magnitude * self.WEIGHTS["magnitude"]
            + relationship * self.WEIGHTS["relationship"]
            + strategy * self.WEIGHTS["strategy"]
            + risk * self.WEIGHTS["risk"]
        )

        return round(
            max(0.0, min(100.0, score)),
            4,
        )

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    def classify(
        self,
        score: float,
        contradictions: list[str],
    ) -> VerdictState:
        if contradictions:
            if any(
                item in {
                    "directional_conflict",
                    "insufficient_evidence",
                    "insufficient_intelligence",
                }
                for item in contradictions
            ):
                return VerdictState.CONFLICTED

        if score >= self.STRONG_THRESHOLD:
            return VerdictState.STRONG

        if score >= self.ACTIONABLE_THRESHOLD:
            return VerdictState.ACTIONABLE

        if score >= self.DEVELOPING_THRESHOLD:
            return VerdictState.DEVELOPING

        if score >= self.WEAK_THRESHOLD:
            return VerdictState.WEAK

        return VerdictState.REJECTED

    # ------------------------------------------------------------------
    # Confidence
    # ------------------------------------------------------------------

    def _confidence(
        self,
        components: Mapping[str, float],
        alignment: float,
        score: float,
        contradictions: list[str],
    ) -> float:
        values = list(components.values())

        if not values:
            return 0.0

        average = mean(values)
        minimum = min(values)
        spread = max(values) - minimum

        confidence = (
            average * 0.40
            + minimum * 0.25
            + alignment * 0.20
            + score * 0.15
        )

        if spread > 60.0:
            confidence -= 15.0
        elif spread > 40.0:
            confidence -= 8.0

        confidence -= len(contradictions) * 8.0

        return round(
            max(0.0, min(100.0, confidence)),
            4,
        )

    # ------------------------------------------------------------------
    # Main assessment
    # ------------------------------------------------------------------

    def assess(
        self,
        data: Mapping[str, Any] | None = None,
    ) -> VerdictAssessment:
        data = dict(data or {})

        components = {
            "evidence": self._component(
                data,
                "evidence_score",
                "evidence_quality",
                default=50.0,
            ),
            "context": self._component(
                data,
                "context_score",
                "market_context_score",
                "mci_score",
                default=50.0,
            ),
            "intelligence": self._component(
                data,
                "intelligence_score",
                "intelligence_quality",
                default=50.0,
            ),
            "commitment": self._component(
                data,
                "commitment_score",
                "commitment_quality",
                default=50.0,
            ),
            "timing": self._component(
                data,
                "timing_score",
                "timing_quality",
                default=50.0,
            ),
            "magnitude": self._component(
                data,
                "magnitude_score",
                "magnitude_quality",
                default=50.0,
            ),
            "relationship": self._component(
                data,
                "relationship_score",
                "relationship_quality",
                default=50.0,
            ),
            "strategy": self._component(
                data,
                "strategy_score",
                "strategy_fit",
                default=50.0,
            ),
            "risk": self._component(
                data,
                "risk_score",
                "risk_quality",
                default=50.0,
            ),
        }

        alignment, direction, alignment_conflicts = (
            self._directional_alignment(data)
        )

        contradictions = self._contradictions(
            data,
            components,
            alignment,
            direction,
        )

        contradictions.extend(alignment_conflicts)
        contradictions = list(dict.fromkeys(contradictions))

        score = self.calculate_verdict_score(
            evidence=components["evidence"],
            context=components["context"],
            intelligence=components["intelligence"],
            commitment=components["commitment"],
            timing=components["timing"],
            magnitude=components["magnitude"],
            relationship=components["relationship"],
            strategy=components["strategy"],
            risk=components["risk"],
        )

        state = self.classify(
            score,
            contradictions,
        )

        # Final verdict logic.
        if contradictions:
            verdict = Verdict.CONFLICTED.value

            if (
                "insufficient_evidence" in contradictions
                or "insufficient_intelligence" in contradictions
            ):
                verdict = Verdict.INSUFFICIENT.value

        elif direction == "BUY":
            verdict = Verdict.BUY.value

        elif direction == "SELL":
            verdict = Verdict.SELL.value

        else:
            verdict = Verdict.HOLD.value

        # A strong numerical score cannot override directional conflict.
        if alignment < self.MIN_ALIGNMENT:
            verdict = Verdict.CONFLICTED.value

        if score < self.WEAK_THRESHOLD:
            verdict = Verdict.REJECT.value

        confidence = self._confidence(
            components,
            alignment,
            score,
            contradictions,
        )

        decision_ready = (
            score >= self.ACTIONABLE_THRESHOLD
            and components["evidence"] >= self.MIN_EVIDENCE
            and components["context"] >= self.MIN_CONTEXT
            and components["intelligence"] >= self.MIN_INTELLIGENCE
            and components["commitment"] >= self.MIN_COMMITMENT
            and components["timing"] >= self.MIN_TIMING
            and components["risk"] >= self.MIN_RISK
            and alignment >= self.MIN_ALIGNMENT
            and direction in {"BUY", "SELL"}
            and not contradictions
        )

        if decision_ready:
            reasons = [
                "evidence_sufficient",
                "market_context_sufficient",
                "intelligence_sufficient",
                "commitment_confirmed",
                "timing_acceptable",
                "risk_quality_acceptable",
                "directionally_aligned",
                "verdict_score_actionable",
            ]
        else:
            reasons = []

            if components["evidence"] >= self.MIN_EVIDENCE:
                reasons.append("evidence_sufficient")

            if components["context"] >= self.MIN_CONTEXT:
                reasons.append("context_sufficient")

            if components["intelligence"] >= self.MIN_INTELLIGENCE:
                reasons.append("intelligence_sufficient")

            if components["commitment"] >= self.MIN_COMMITMENT:
                reasons.append("commitment_sufficient")

            if contradictions:
                reasons.append("verdict_blocked_by_contradiction")

            if score < self.ACTIONABLE_THRESHOLD:
                reasons.append("score_below_actionable_threshold")

        risk_flags: list[str] = []

        if components["risk"] < self.MIN_RISK:
            risk_flags.append("LOW_RISK_QUALITY")

        if components["timing"] < self.MIN_TIMING:
            risk_flags.append("WEAK_TIMING")

        if components["commitment"] < self.MIN_COMMITMENT:
            risk_flags.append("WEAK_COMMITMENT")

        if alignment < self.MIN_ALIGNMENT:
            risk_flags.append("DIRECTIONAL_MISALIGNMENT")

        if contradictions:
            risk_flags.append("VERDICT_CONTRADICTION")

        timestamp = datetime.now(timezone.utc).isoformat()

        assessment = VerdictAssessment(
            verdict=verdict,
            state=state.value,
            verdict_score=score,
            confidence=confidence,
            evidence_score=round(components["evidence"], 4),
            context_score=round(components["context"], 4),
            intelligence_score=round(components["intelligence"], 4),
            commitment_score=round(components["commitment"], 4),
            timing_score=round(components["timing"], 4),
            magnitude_score=round(components["magnitude"], 4),
            relationship_score=round(components["relationship"], 4),
            strategy_score=round(components["strategy"], 4),
            risk_score=round(components["risk"], 4),
            directional_alignment=round(alignment, 4),
            decision_ready=decision_ready,
            contradictions=tuple(contradictions),
            reasons=tuple(dict.fromkeys(reasons)),
            risk_flags=tuple(dict.fromkeys(risk_flags)),
            evidence={
                "components": dict(components),
                "weights": dict(self.WEIGHTS),
                "formula": (
                    "V = E*0.15 + M*0.15 + I*0.15 + "
                    "C*0.10 + T*0.10 + G*0.10 + "
                    "R*0.10 + S*0.05 + RK*0.10"
                ),
                "direction": direction,
                "directional_alignment": alignment,
                "gates": {
                    "evidence": self.MIN_EVIDENCE,
                    "context": self.MIN_CONTEXT,
                    "intelligence": self.MIN_INTELLIGENCE,
                    "commitment": self.MIN_COMMITMENT,
                    "timing": self.MIN_TIMING,
                    "risk": self.MIN_RISK,
                    "liquidity": self.MIN_LIQUIDITY,
                    "alignment": self.MIN_ALIGNMENT,
                },
            },
            timestamp=timestamp,
        )

        self._history.append(assessment)

        return assessment

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------

    @property
    def history(self) -> tuple[VerdictAssessment, ...]:
        return tuple(self._history)

    @property
    def latest(self) -> VerdictAssessment | None:
        return self._history[-1] if self._history else None

    def average_score(self) -> float:
        if not self._history:
            return 0.0

        return round(
            mean(
                item.verdict_score
                for item in self._history
            ),
            4,
        )

    def clear(self) -> None:
        self._history.clear()

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    def health_check(self) -> dict[str, Any]:
        weight_sum = sum(self.WEIGHTS.values())

        return {
            "engine": "VerdictEngine",
            "version": self.VERSION,
            "healthy": abs(weight_sum - 1.0) < 1e-9,
            "weight_sum": weight_sum,
            "history_size": len(self._history),
            "thresholds": {
                "strong": self.STRONG_THRESHOLD,
                "actionable": self.ACTIONABLE_THRESHOLD,
                "developing": self.DEVELOPING_THRESHOLD,
                "weak": self.WEAK_THRESHOLD,
            },
            "gates": {
                "evidence": self.MIN_EVIDENCE,
                "context": self.MIN_CONTEXT,
                "intelligence": self.MIN_INTELLIGENCE,
                "commitment": self.MIN_COMMITMENT,
                "timing": self.MIN_TIMING,
                "risk": self.MIN_RISK,
                "liquidity": self.MIN_LIQUIDITY,
                "alignment": self.MIN_ALIGNMENT,
            },
        }


# Compatibility aliases.
FinalVerdictEngine = VerdictEngine
DecisionVerdictEngine = VerdictEngine


__all__ = [
    "Verdict",
    "VerdictState",
    "VerdictAssessment",
    "VerdictEngine",
    "FinalVerdictEngine",
    "DecisionVerdictEngine",
]