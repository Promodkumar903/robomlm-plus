"""
ROBOMLM V6
Decision Cortex
D3 — Decision Confidence

Purpose
-------
Estimate confidence in the currently supported decision hypothesis.

Pipeline position:
    D1 Decision Readiness
            ↓
    D2 Decision Condition
            ↓
    D3 Decision Confidence
            ↓
    D4+ Decision Logic

Important:
------------
- Confidence is NOT risk.
- Confidence is NOT probability of profit.
- Confidence is NOT an execution approval.
- Confidence must be traceable to evidence.
- Contradictory evidence reduces confidence.
- Invalid / stale evidence cannot silently become confidence.
- D3 does not place orders.
- D3 does not calculate position size.

V6 principle:
--------------
Evidence → Validation → Context → Relationship → Probability
→ Risk → Decision → Execution Approval → Learning

Calibration:
------------
The weighting parameters in this implementation are explicit and
configurable. They must be validated against V6 historical/live
datasets before being considered empirically locked.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from math import isfinite
from typing import Any, Dict, Optional


# ---------------------------------------------------------------------
# ENUMS
# ---------------------------------------------------------------------

class ConfidenceState(str, Enum):
    VERY_HIGH = "VERY_HIGH"
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"
    INSUFFICIENT = "INSUFFICIENT"
    BLOCKED = "BLOCKED"


class Direction(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    UNRESOLVED = "UNRESOLVED"


# ---------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class ConfidenceConfig:
    """
    Calibration parameters.

    These are intentionally explicit rather than hidden constants.
    They can be replaced after empirical V6 calibration.
    """

    # Evidence contribution
    evidence_weight: float = 0.35

    # Context contribution
    context_weight: float = 0.20

    # Directional agreement contribution
    agreement_weight: float = 0.15

    # Contradiction penalty
    contradiction_weight: float = 0.15

    # Decision readiness contribution
    readiness_weight: float = 0.15

    # State thresholds
    very_high_threshold: float = 0.85
    high_threshold: float = 0.75
    moderate_threshold: float = 0.60
    low_threshold: float = 0.40

    def validate(self) -> None:
        weights = (
            self.evidence_weight,
            self.context_weight,
            self.agreement_weight,
            self.contradiction_weight,
            self.readiness_weight,
        )

        if any(w < 0.0 or w > 1.0 for w in weights):
            raise ValueError("All confidence weights must be in [0, 1].")

        total = (
            self.evidence_weight
            + self.context_weight
            + self.agreement_weight
            + self.contradiction_weight
            + self.readiness_weight
        )

        if abs(total - 1.0) > 1e-9:
            raise ValueError(
                f"Confidence weights must sum to 1.0; got {total:.6f}"
            )

        thresholds = (
            self.very_high_threshold,
            self.high_threshold,
            self.moderate_threshold,
            self.low_threshold,
        )

        if any(t < 0.0 or t > 1.0 for t in thresholds):
            raise ValueError("Confidence thresholds must be in [0, 1].")

        if not (
            self.very_high_threshold
            > self.high_threshold
            > self.moderate_threshold
            > self.low_threshold
        ):
            raise ValueError(
                "Confidence thresholds must be strictly descending."
            )


DEFAULT_CONFIG = ConfidenceConfig()


# ---------------------------------------------------------------------
# INPUT
# ---------------------------------------------------------------------

@dataclass
class DecisionConfidenceInput:
    """
    Normalized D3 inputs.

    All normalized quantities are expected in [0, 1].
    """

    evidence_weight: float
    context_strength: float

    bullish_evidence: float = 0.0
    bearish_evidence: float = 0.0

    contradiction: float = 0.0

    decision_readiness: float = 0.0

    direction: str = Direction.UNRESOLVED.value

    evidence_valid: bool = True
    context_valid: bool = True
    identity_valid: bool = True
    dependency_valid: bool = True

    market: Optional[str] = None
    instrument: Optional[str] = None
    venue: Optional[str] = None
    contract: Optional[str] = None

    source_count: int = 1
    fresh: bool = True


# ---------------------------------------------------------------------
# OUTPUT
# ---------------------------------------------------------------------

@dataclass
class DecisionConfidenceResult:
    confidence: float
    confidence_pct: float

    state: str
    direction: str

    evidence_component: float
    context_component: float
    agreement_component: float
    contradiction_component: float
    readiness_component: float

    blocked: bool
    reason: str

    trace: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------
# ENGINE
# ---------------------------------------------------------------------

class DecisionConfidenceEngine:
    """
    D3 Decision Confidence Engine.

    Confidence is derived from:
        1. Evidence strength
        2. Context strength
        3. Directional agreement
        4. Contradiction penalty
        5. Decision readiness

    The engine is deliberately independent of risk and execution.
    """

    def __init__(
        self,
        config: ConfidenceConfig = DEFAULT_CONFIG,
    ) -> None:
        config.validate()
        self.config = config

    # -----------------------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------------------

    @staticmethod
    def _validate_unit_interval(
        value: float,
        name: str,
    ) -> float:

        if not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be numeric.")

        value = float(value)

        if not isfinite(value):
            raise ValueError(f"{name} must be finite.")

        if value < 0.0 or value > 1.0:
            raise ValueError(
                f"{name} must be between 0 and 1; got {value}."
            )

        return value

    def _validate_input(
        self,
        data: DecisionConfidenceInput,
    ) -> None:

        for name in (
            "evidence_weight",
            "context_strength",
            "bullish_evidence",
            "bearish_evidence",
            "contradiction",
            "decision_readiness",
        ):
            self._validate_unit_interval(
                getattr(data, name),
                name,
            )

        if data.source_count < 0:
            raise ValueError("source_count cannot be negative.")

    # -----------------------------------------------------------------
    # DIRECTIONAL AGREEMENT
    # -----------------------------------------------------------------

    @staticmethod
    def _directional_agreement(
        bullish: float,
        bearish: float,
        direction: str,
    ) -> float:
        """
        Measures how strongly the evidence supports the declared
        direction.

        For a directional decision:
            agreement = directional evidence / total directional evidence

        If no directional evidence exists:
            agreement = 0.

        For NEUTRAL:
            stronger the balance between bullish/bearish evidence,
            stronger the neutral support only when both sides are weak.

        This function does not invent a direction.
        """

        total = bullish + bearish

        if total <= 0.0:
            return 0.0

        direction = direction.upper()

        if direction == Direction.BULLISH.value:
            return bullish / total

        if direction == Direction.BEARISH.value:
            return bearish / total

        if direction == Direction.NEUTRAL.value:
            imbalance = abs(bullish - bearish) / total
            return 1.0 - imbalance

        return 0.0

    # -----------------------------------------------------------------
    # STATE
    # -----------------------------------------------------------------

    def _classify(
        self,
        confidence: float,
    ) -> ConfidenceState:

        if confidence >= self.config.very_high_threshold:
            return ConfidenceState.VERY_HIGH

        if confidence >= self.config.high_threshold:
            return ConfidenceState.HIGH

        if confidence >= self.config.moderate_threshold:
            return ConfidenceState.MODERATE

        if confidence >= self.config.low_threshold:
            return ConfidenceState.LOW

        return ConfidenceState.INSUFFICIENT

    # -----------------------------------------------------------------
    # MAIN CALCULATION
    # -----------------------------------------------------------------

    def calculate(
        self,
        data: DecisionConfidenceInput,
    ) -> DecisionConfidenceResult:

        self._validate_input(data)

        # -------------------------------------------------------------
        # HARD BLOCKERS
        # -------------------------------------------------------------

        blockers = []

        if not data.identity_valid:
            blockers.append("IDENTITY_INVALID")

        if not data.dependency_valid:
            blockers.append("DEPENDENCY_INVALID")

        if not data.evidence_valid:
            blockers.append("EVIDENCE_INVALID")

        if not data.context_valid:
            blockers.append("CONTEXT_INVALID")

        if not data.fresh:
            blockers.append("EVIDENCE_STALE")

        if blockers:
            return DecisionConfidenceResult(
                confidence=0.0,
                confidence_pct=0.0,
                state=ConfidenceState.BLOCKED.value,
                direction=data.direction,
                evidence_component=0.0,
                context_component=0.0,
                agreement_component=0.0,
                contradiction_component=0.0,
                readiness_component=0.0,
                blocked=True,
                reason="; ".join(blockers),
                trace={
                    "engine": "D3_DECISION_CONFIDENCE",
                    "blocked_by": blockers,
                },
            )

        # -------------------------------------------------------------
        # COMPONENTS
        # -------------------------------------------------------------

        evidence = self._validate_unit_interval(
            data.evidence_weight,
            "evidence_weight",
        )

        context = self._validate_unit_interval(
            data.context_strength,
            "context_strength",
        )

        contradiction = self._validate_unit_interval(
            data.contradiction,
            "contradiction",
        )

        readiness = self._validate_unit_interval(
            data.decision_readiness,
            "decision_readiness",
        )

        agreement = self._directional_agreement(
            data.bullish_evidence,
            data.bearish_evidence,
            data.direction,
        )

        # -------------------------------------------------------------
        # WEIGHTED CONFIDENCE
        # -------------------------------------------------------------

        evidence_component = (
            evidence * self.config.evidence_weight
        )

        context_component = (
            context * self.config.context_weight
        )

        agreement_component = (
            agreement * self.config.agreement_weight
        )

        contradiction_penalty = (
            contradiction * self.config.contradiction_weight
        )

        readiness_component = (
            readiness * self.config.readiness_weight
        )

        raw_confidence = (
            evidence_component
            + context_component
            + agreement_component
            + readiness_component
            - contradiction_penalty
        )

        confidence = max(
            0.0,
            min(1.0, raw_confidence),
        )

        # -------------------------------------------------------------
        # DIRECTION SAFETY
        # -------------------------------------------------------------

        direction = data.direction.upper()

        # If direction is unresolved, confidence must not be presented
        # as directional confidence.
        if direction == Direction.UNRESOLVED.value:
            confidence *= 0.75

        # -------------------------------------------------------------
        # CLASSIFICATION
        # -------------------------------------------------------------

        state = self._classify(confidence)

        # -------------------------------------------------------------
        # REASON
        # -------------------------------------------------------------

        if state == ConfidenceState.VERY_HIGH:
            reason = (
                "Strong evidence, context, directional agreement "
                "and readiness with limited contradiction."
            )

        elif state == ConfidenceState.HIGH:
            reason = (
                "Evidence and context materially support the current "
                "decision hypothesis."
            )

        elif state == ConfidenceState.MODERATE:
            reason = (
                "Decision hypothesis has meaningful support but "
                "confidence is not yet strong."
            )

        elif state == ConfidenceState.LOW:
            reason = (
                "Support exists but evidence/context/agreement is "
                "insufficient for strong confidence."
            )

        else:
            reason = (
                "Insufficient decision-grade support."
            )

        if contradiction > 0.50:
            reason += " Significant contradictory evidence detected."

        if direction == Direction.UNRESOLVED.value:
            reason += " Direction remains unresolved."

        # -------------------------------------------------------------
        # TRACE
        # -------------------------------------------------------------

        trace = {
            "engine": "D3_DECISION_CONFIDENCE",
            "version": "V6",
            "inputs": {
                "evidence_weight": evidence,
                "context_strength": context,
                "bullish_evidence": data.bullish_evidence,
                "bearish_evidence": data.bearish_evidence,
                "contradiction": contradiction,
                "decision_readiness": readiness,
                "direction": direction,
            },
            "components": {
                "evidence_component": evidence_component,
                "context_component": context_component,
                "agreement_component": agreement_component,
                "contradiction_penalty": contradiction_penalty,
                "readiness_component": readiness_component,
            },
            "weights": {
                "evidence": self.config.evidence_weight,
                "context": self.config.context_weight,
                "agreement": self.config.agreement_weight,
                "contradiction": self.config.contradiction_weight,
                "readiness": self.config.readiness_weight,
            },
            "raw_confidence": raw_confidence,
            "directional_adjustment": (
                0.75
                if direction == Direction.UNRESOLVED.value
                else 1.0
            ),
            "final_confidence": confidence,
            "calibration_status": "CALIBRATION_REQUIRED",
        }

        return DecisionConfidenceResult(
            confidence=confidence,
            confidence_pct=confidence * 100.0,
            state=state.value,
            direction=direction,
            evidence_component=evidence_component,
            context_component=context_component,
            agreement_component=agreement_component,
            contradiction_component=contradiction_penalty,
            readiness_component=readiness_component,
            blocked=False,
            reason=reason,
            trace=trace,
        )


# ---------------------------------------------------------------------
# CONVENIENCE FUNCTION
# ---------------------------------------------------------------------

def calculate_decision_confidence(
    evidence_weight: float,
    context_strength: float,
    bullish_evidence: float = 0.0,
    bearish_evidence: float = 0.0,
    contradiction: float = 0.0,
    decision_readiness: float = 0.0,
    direction: str = Direction.UNRESOLVED.value,
    evidence_valid: bool = True,
    context_valid: bool = True,
    identity_valid: bool = True,
    dependency_valid: bool = True,
    fresh: bool = True,
) -> DecisionConfidenceResult:

    engine = DecisionConfidenceEngine()

    data = DecisionConfidenceInput(
        evidence_weight=evidence_weight,
        context_strength=context_strength,
        bullish_evidence=bullish_evidence,
        bearish_evidence=bearish_evidence,
        contradiction=contradiction,
        decision_readiness=decision_readiness,
        direction=direction,
        evidence_valid=evidence_valid,
        context_valid=context_valid,
        identity_valid=identity_valid,
        dependency_valid=dependency_valid,
        fresh=fresh,
    )

    return engine.calculate(data)


# ---------------------------------------------------------------------
# SELF TESTS
# ---------------------------------------------------------------------

def _assert_close(
    actual: float,
    expected: float,
    tolerance: float = 1e-9,
) -> None:

    if abs(actual - expected) > tolerance:
        raise AssertionError(
            f"Expected {expected}, got {actual}"
        )


def run_self_tests() -> None:

    engine = DecisionConfidenceEngine()

    # -------------------------------------------------------------
    # TEST 1 — Strong bullish evidence
    # -------------------------------------------------------------

    result = engine.calculate(
        DecisionConfidenceInput(
            evidence_weight=0.95,
            context_strength=0.90,
            bullish_evidence=0.95,
            bearish_evidence=0.05,
            contradiction=0.05,
            decision_readiness=0.90,
            direction=Direction.BULLISH.value,
        )
    )

    assert result.blocked is False
    assert result.confidence > 0.75
    assert result.direction == Direction.BULLISH.value

    # -------------------------------------------------------------
    # TEST 2 — Strong contradiction
    # -------------------------------------------------------------

    result = engine.calculate(
        DecisionConfidenceInput(
            evidence_weight=0.80,
            context_strength=0.80,
            bullish_evidence=0.80,
            bearish_evidence=0.20,
            contradiction=0.90,
            decision_readiness=0.80,
            direction=Direction.BULLISH.value,
        )
    )

    assert result.confidence < 0.75
    assert result.contradiction_component > 0.0

    # -------------------------------------------------------------
    # TEST 3 — Unresolved direction
    # -------------------------------------------------------------

    result = engine.calculate(
        DecisionConfidenceInput(
            evidence_weight=0.90,
            context_strength=0.90,
            bullish_evidence=0.50,
            bearish_evidence=0.50,
            contradiction=0.0,
            decision_readiness=0.90,
            direction=Direction.UNRESOLVED.value,
        )
    )

    assert result.direction == Direction.UNRESOLVED.value
    assert result.confidence < 0.90

    # -------------------------------------------------------------
    # TEST 4 — Invalid evidence
    # -------------------------------------------------------------

    result = engine.calculate(
        DecisionConfidenceInput(
            evidence_weight=0.90,
            context_strength=0.90,
            decision_readiness=0.90,
            direction=Direction.BULLISH.value,
            evidence_valid=False,
        )
    )

    assert result.blocked is True
    assert result.confidence == 0.0
    assert result.state == ConfidenceState.BLOCKED.value

    # -------------------------------------------------------------
    # TEST 5 — Stale evidence
    # -------------------------------------------------------------

    result = engine.calculate(
        DecisionConfidenceInput(
            evidence_weight=0.90,
            context_strength=0.90,
            decision_readiness=0.90,
            direction=Direction.BULLISH.value,
            fresh=False,
        )
    )

    assert result.blocked is True
    assert "EVIDENCE_STALE" in result.reason

    print("D3 Decision Confidence self-tests: PASS")


# ---------------------------------------------------------------------
# DEMO
# ---------------------------------------------------------------------

def demo() -> None:

    engine = DecisionConfidenceEngine()

    result = engine.calculate(
        DecisionConfidenceInput(
            evidence_weight=0.88,
            context_strength=0.84,
            bullish_evidence=0.90,
            bearish_evidence=0.10,
            contradiction=0.12,
            decision_readiness=0.86,
            direction=Direction.BULLISH.value,
            market="NIFTY",
            instrument="NIFTY",
            venue="NSE",
        )
    )

    print("\nROBOMLM V6 — D3 Decision Confidence")
    print("-" * 48)
    print(f"Confidence : {result.confidence_pct:.2f}%")
    print(f"State      : {result.state}")
    print(f"Direction  : {result.direction}")
    print(f"Reason     : {result.reason}")
    print("-" * 48)

    for key, value in result.trace["components"].items():
        print(f"{key:24s}: {value:.6f}")


# ---------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------

if __name__ == "__main__":
    run_self_tests()
    demo()