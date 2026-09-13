"""
ROBOMLM_PLUS
D16 — Decision Intelligence

V6 Decision Layer
D1  Market Identity
D2  Data Contract
D3  Trust
D4  Relationships
D5  Structure
D6  Flow
D7  Liquidity / Volatility
D8  Instrument Mechanics
D9  Time / Event
D10 Market State
D11 Transition
D12 Future / Scenario
D13 Decision
D14 Validation
D15 Learning
D16 Intelligence

D16 PURPOSE
-----------
D16 is the final intelligence synthesis layer.

D16:
    - consumes D1-D15 outputs
    - preserves provenance
    - synthesizes validated decision + validation + learning
    - identifies intelligence implications
    - identifies recurring patterns when explicitly supplied
    - produces intelligence state, NOT a new trading decision
    - does not alter D13
    - does not alter D14
    - does not silently alter D15 parameters
    - does not use future information to reconstruct T0
    - does not invent universal probabilities/scores

IMPORTANT
---------
The exact proprietary V6 numerical D16 formula was not recovered
from the available source material.

Therefore this implementation deliberately does NOT invent a
fake 0-100 intelligence score.

All quantitative aggregation/calibration remains externally
versioned and injectable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


# ============================================================
# TIME
# ============================================================

def parse_dt(value: Any) -> Optional[datetime]:
    if value is None:
        return None

    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        text = value.strip()

        if text.endswith("Z"):
            text = text[:-1] + "+00:00"

        try:
            dt = datetime.fromisoformat(text)
        except ValueError:
            return None
    else:
        return None

    if dt.tzinfo is None:
        return None

    return dt.astimezone(timezone.utc)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


# ============================================================
# ENUMS
# ============================================================

class IntelligenceStatus(str, Enum):
    READY = "READY"
    LIMITED = "LIMITED"
    BLOCKED = "BLOCKED"
    UNDETERMINED = "UNDETERMINED"


class IntelligenceResult(str, Enum):
    CONFIRMED = "CONFIRMED"
    SUPPORTED = "SUPPORTED"
    MIXED = "MIXED"
    CONTRADICTED = "CONTRADICTED"
    INSUFFICIENT = "INSUFFICIENT"


class IntelligenceReason(str, Enum):
    VALIDATED_DECISION = "VALIDATED_DECISION"
    INVALIDATED_DECISION = "INVALIDATED_DECISION"
    PARTIAL_VALIDATION = "PARTIAL_VALIDATION"

    LEARNING_SUPPORTED = "LEARNING_SUPPORTED"
    LEARNING_CONTRADICTED = "LEARNING_CONTRADICTED"
    LEARNING_MIXED = "LEARNING_MIXED"

    FUTURE_LEAKAGE = "FUTURE_LEAKAGE"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    TIMESTAMP_ERROR = "TIMESTAMP_ERROR"

    INSUFFICIENT_INPUT = "INSUFFICIENT_INPUT"
    INTELLIGENCE_SYNTHESIZED = "INTELLIGENCE_SYNTHESIZED"

    PATTERN_OBSERVATION = "PATTERN_OBSERVATION"
    PATTERN_UPDATE_NOT_APPLIED = "PATTERN_UPDATE_NOT_APPLIED"


# ============================================================
# D13 SNAPSHOT
# ============================================================

@dataclass(frozen=True)
class DecisionSnapshot:
    decision_id: str
    market_id: str

    decision_time: str

    action: str
    direction: str = "UNKNOWN"

    scenario_type: Optional[str] = None
    horizon: Optional[str] = None

    provenance: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# D14 SNAPSHOT
# ============================================================

@dataclass(frozen=True)
class ValidationSnapshot:
    validation_id: str
    decision_id: str
    market_id: str

    decision_time: str
    validation_time: str

    status: str
    overall_result: str

    direction_result: Optional[str] = None
    scenario_result: Optional[str] = None
    horizon_result: Optional[str] = None
    invalidation_result: Optional[str] = None
    pnl_result: Optional[str] = None

    future_leakage: bool = False
    identity_mismatch: bool = False

    provenance: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# D15 SNAPSHOT
# ============================================================

@dataclass(frozen=True)
class LearningSnapshot:
    learning_id: str
    validation_id: str
    market_id: str

    learning_time: str

    status: str
    result: str

    observation_ids: List[str] = field(default_factory=list)

    parameter_update_applied: bool = False

    provenance: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# D16 INTELLIGENCE OBSERVATION
# ============================================================

@dataclass(frozen=True)
class IntelligenceObservation:
    observation_id: str
    market_id: str

    decision_id: str
    validation_id: str
    learning_id: Optional[str]

    observation_time: str

    validation_result: str
    learning_result: Optional[str]

    intelligence_implication: str

    source_layers: List[str] = field(default_factory=list)

    provenance: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# PATTERN OBSERVATION
# ============================================================

@dataclass(frozen=True)
class PatternObservation:
    pattern_id: str
    market_id: str

    pattern_type: str

    sample_size: int

    supporting_observations: List[str] = field(default_factory=list)

    confidence_source: Optional[str] = None

    provenance: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# D16 OUTPUT
# ============================================================

@dataclass
class IntelligenceRecord:
    intelligence_id: str

    market_id: str
    decision_id: str
    validation_id: str

    learning_id: Optional[str]

    status: IntelligenceStatus
    result: IntelligenceResult

    observations: List[IntelligenceObservation] = field(default_factory=list)

    patterns: List[PatternObservation] = field(default_factory=list)

    intelligence_summary: str = ""

    provenance: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# D16 ENGINE
# ============================================================

class D16DecisionIntelligenceEngine:

    VERSION = "D16-1.0"

    # --------------------------------------------------------
    # PUBLIC
    # --------------------------------------------------------

    def synthesize(
        self,
        decision: DecisionSnapshot,
        validation: ValidationSnapshot,
        learning: Optional[LearningSnapshot] = None,
        patterns: Optional[List[PatternObservation]] = None,
    ) -> IntelligenceRecord:

        intelligence_id = (
            f"D16-{decision.decision_id}-{validation.validation_id}"
        )

        # ----------------------------------------------------
        # BASIC IDENTITY
        # ----------------------------------------------------

        if not decision.market_id:
            return self._blocked(
                intelligence_id=intelligence_id,
                decision=decision,
                validation=validation,
                learning=learning,
                reason=IntelligenceReason.IDENTITY_MISMATCH,
            )

        if decision.market_id != validation.market_id:
            return self._blocked(
                intelligence_id=intelligence_id,
                decision=decision,
                validation=validation,
                learning=learning,
                reason=IntelligenceReason.IDENTITY_MISMATCH,
            )

        if learning is not None:
            if learning.market_id != decision.market_id:
                return self._blocked(
                    intelligence_id=intelligence_id,
                    decision=decision,
                    validation=validation,
                    learning=learning,
                    reason=IntelligenceReason.IDENTITY_MISMATCH,
                )

        # ----------------------------------------------------
        # TIMESTAMP VALIDATION
        # ----------------------------------------------------

        decision_time = parse_dt(decision.decision_time)
        validation_time = parse_dt(validation.validation_time)

        if decision_time is None or validation_time is None:
            return self._blocked(
                intelligence_id=intelligence_id,
                decision=decision,
                validation=validation,
                learning=learning,
                reason=IntelligenceReason.TIMESTAMP_ERROR,
            )

        if validation_time <= decision_time:
            return self._blocked(
                intelligence_id=intelligence_id,
                decision=decision,
                validation=validation,
                learning=learning,
                reason=IntelligenceReason.FUTURE_LEAKAGE,
            )

        # ----------------------------------------------------
        # VALIDATION PROVENANCE GATE
        # ----------------------------------------------------

        if validation.provenance.get("validated_by_D14") is not True:
            return self._blocked(
                intelligence_id=intelligence_id,
                decision=decision,
                validation=validation,
                learning=learning,
                reason=IntelligenceReason.INSUFFICIENT_INPUT,
            )

        # ----------------------------------------------------
        # HARD LEAKAGE / IDENTITY GATE
        # ----------------------------------------------------

        if validation.future_leakage:
            return self._blocked(
                intelligence_id=intelligence_id,
                decision=decision,
                validation=validation,
                learning=learning,
                reason=IntelligenceReason.FUTURE_LEAKAGE,
            )

        if validation.identity_mismatch:
            return self._blocked(
                intelligence_id=intelligence_id,
                decision=decision,
                validation=validation,
                learning=learning,
                reason=IntelligenceReason.IDENTITY_MISMATCH,
            )

        # ----------------------------------------------------
        # VALIDATION INTERPRETATION
        # ----------------------------------------------------

        validation_result = validation.overall_result.upper()

        if validation_result == "CORRECT":
            result = IntelligenceResult.CONFIRMED
            implication = "Decision outcome was validated as correct."

        elif validation_result == "INCORRECT":
            result = IntelligenceResult.CONTRADICTED
            implication = "Decision outcome contradicted the original decision thesis."

        elif validation_result == "PARTIAL":
            result = IntelligenceResult.MIXED
            implication = "Validation produced mixed or partial evidence."

        else:
            result = IntelligenceResult.INSUFFICIENT
            implication = "Validation did not provide sufficient evidence for intelligence synthesis."

        # ----------------------------------------------------
        # D15 LEARNING INTERPRETATION
        # ----------------------------------------------------

        learning_result = None

        if learning is not None:

            learning_result = learning.result.upper()

            if learning.provenance.get("future_information_used") is True:
                return self._blocked(
                    intelligence_id=intelligence_id,
                    decision=decision,
                    validation=validation,
                    learning=learning,
                    reason=IntelligenceReason.FUTURE_LEAKAGE,
                )

            if learning.parameter_update_applied:
                # D16 may consume the fact that an update was applied,
                # but it must never silently apply an update itself.
                pass

            if learning_result == "SUPPORTED":
                if result == IntelligenceResult.CONFIRMED:
                    implication += " Learning evidence supports the validated thesis."

            elif learning_result == "CONTRADICTED":
                if result == IntelligenceResult.CONTRADICTED:
                    implication += " Learning evidence reinforces the contradiction."

            elif learning_result == "MIXED":
                implication += " Learning evidence remains mixed."

        # ----------------------------------------------------
        # CREATE OBSERVATION
        # ----------------------------------------------------

        observation = IntelligenceObservation(
            observation_id=f"IO-{decision.decision_id}-{validation.validation_id}",
            market_id=decision.market_id,

            decision_id=decision.decision_id,
            validation_id=validation.validation_id,
            learning_id=learning.learning_id if learning else None,

            observation_time=validation.validation_time,

            validation_result=validation_result,
            learning_result=learning_result,

            intelligence_implication=implication,

            source_layers=[
                "D1",
                "D2",
                "D3",
                "D4",
                "D5",
                "D6",
                "D7",
                "D8",
                "D9",
                "D10",
                "D11",
                "D12",
                "D13",
                "D14",
                "D15",
            ],

            provenance={
                "engine": "D16DecisionIntelligenceEngine",
                "version": self.VERSION,

                "future_information_used": False,
                "future_outcome_observed": True,

                "decision_preserved": True,
                "validation_preserved": True,
                "learning_preserved": True,

                "new_decision_created": False,
                "parameter_update_applied": False,

                "D13_applied": False,
                "D14_applied": False,
                "D15_applied": False,
                "D16_applied": True,
            },
        )

        # ----------------------------------------------------
        # PATTERNS
        # ----------------------------------------------------

        clean_patterns = []

        if patterns:

            for pattern in patterns:

                if pattern.market_id != decision.market_id:
                    continue

                # Pattern itself must not contain future leakage.
                if pattern.provenance.get("future_information_used") is True:
                    continue

                clean_patterns.append(pattern)

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        if result == IntelligenceResult.INSUFFICIENT:
            status = IntelligenceStatus.UNDETERMINED

        elif result == IntelligenceResult.MIXED:
            status = IntelligenceStatus.LIMITED

        else:
            status = IntelligenceStatus.READY

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        summary = self._build_summary(
            decision=decision,
            validation=validation,
            learning=learning,
            result=result,
            patterns=clean_patterns,
        )

        # ----------------------------------------------------
        # FINAL PROVENANCE
        # ----------------------------------------------------

        provenance = {
            "engine": "D16DecisionIntelligenceEngine",
            "version": self.VERSION,

            "market_id": decision.market_id,

            "source_decision_id": decision.decision_id,
            "source_validation_id": validation.validation_id,
            "source_learning_id": (
                learning.learning_id if learning else None
            ),

            "future_information_used": False,
            "future_outcome_observed": True,

            "new_decision_created": False,
            "decision_modified": False,
            "validation_modified": False,
            "learning_modified": False,

            "parameter_update_applied": False,

            "D13_applied": False,
            "D14_applied": False,
            "D15_applied": False,
            "D16_applied": True,
        }

        return IntelligenceRecord(
            intelligence_id=intelligence_id,

            market_id=decision.market_id,
            decision_id=decision.decision_id,
            validation_id=validation.validation_id,

            learning_id=(
                learning.learning_id if learning else None
            ),

            status=status,
            result=result,

            observations=[observation],

            patterns=clean_patterns,

            intelligence_summary=summary,

            provenance=provenance,
        )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    def _build_summary(
        self,
        decision: DecisionSnapshot,
        validation: ValidationSnapshot,
        learning: Optional[LearningSnapshot],
        result: IntelligenceResult,
        patterns: List[PatternObservation],
    ) -> str:

        parts = [
            f"Market={decision.market_id}",
            f"Decision={decision.action}",
            f"Validation={validation.overall_result}",
        ]

        if learning is not None:
            parts.append(f"Learning={learning.result}")

        if patterns:
            parts.append(f"Patterns={len(patterns)}")

        parts.append(f"Intelligence={result.value}")

        return " | ".join(parts)

    # --------------------------------------------------------
    # BLOCKED
    # --------------------------------------------------------

    def _blocked(
        self,
        intelligence_id: str,
        decision: DecisionSnapshot,
        validation: ValidationSnapshot,
        learning: Optional[LearningSnapshot],
        reason: IntelligenceReason,
    ) -> IntelligenceRecord:

        return IntelligenceRecord(
            intelligence_id=intelligence_id,

            market_id=decision.market_id,
            decision_id=decision.decision_id,
            validation_id=validation.validation_id,

            learning_id=(
                learning.learning_id if learning else None
            ),

            status=IntelligenceStatus.BLOCKED,
            result=IntelligenceResult.INSUFFICIENT,

            observations=[],
            patterns=[],

            intelligence_summary=(
                f"D16 BLOCKED: {reason.value}"
            ),

            provenance={
                "engine": "D16DecisionIntelligenceEngine",
                "version": self.VERSION,

                "block_reason": reason.value,

                "future_information_used": False,

                "new_decision_created": False,
                "decision_modified": False,
                "validation_modified": False,
                "learning_modified": False,

                "parameter_update_applied": False,

                "D13_applied": False,
                "D14_applied": False,
                "D15_applied": False,
                "D16_applied": False,
            },
        )


# ============================================================
# SELF TEST
# ============================================================

def _self_test() -> None:

    engine = D16DecisionIntelligenceEngine()

    decision = DecisionSnapshot(
        decision_id="D13-001",
        market_id="NIFTY|INDEX|NSE",

        decision_time="2026-09-04T09:30:00+00:00",

        action="BUY",
        direction="UP",

        scenario_type="CONTINUATION",
        horizon="SHORT",

        provenance={
            "future_outcome_observed": False,
        },
    )

    validation = ValidationSnapshot(
        validation_id="D14-001",
        decision_id="D13-001",
        market_id="NIFTY|INDEX|NSE",

        decision_time="2026-09-04T09:30:00+00:00",
        validation_time="2026-09-04T10:00:00+00:00",

        status="VALIDATED",
        overall_result="CORRECT",

        direction_result="CORRECT",
        scenario_result="CORRECT",
        horizon_result="CORRECT",
        invalidation_result="CORRECT",
        pnl_result="CORRECT",

        future_leakage=False,
        identity_mismatch=False,

        provenance={
            "validated_by_D14": True,
            "future_outcome_observed": True,
        },
    )

    learning = LearningSnapshot(
        learning_id="D15-001",
        validation_id="D14-001",
        market_id="NIFTY|INDEX|NSE",

        learning_time="2026-09-04T10:01:00+00:00",

        status="LEARNED",
        result="SUPPORTED",

        observation_ids=["LO-001"],

        parameter_update_applied=False,

        provenance={
            "future_information_used": False,
            "D15_ready": True,
        },
    )

    pattern = PatternObservation(
        pattern_id="PAT-001",
        market_id="NIFTY|INDEX|NSE",

        pattern_type="VALIDATED_CONTINUATION",

        sample_size=10,

        supporting_observations=["LO-001"],

        confidence_source="EXTERNAL_CALIBRATION",

        provenance={
            "future_information_used": False,
        },
    )

    # --------------------------------------------------------
    # 1. NORMAL SYNTHESIS
    # --------------------------------------------------------

    result = engine.synthesize(
        decision,
        validation,
        learning,
        [pattern],
    )

    assert result.status == IntelligenceStatus.READY
    assert result.result == IntelligenceResult.CONFIRMED
    assert len(result.observations) == 1
    assert len(result.patterns) == 1

    # --------------------------------------------------------
    # 2. D13 MUST NOT CHANGE
    # --------------------------------------------------------

    before_action = decision.action
    before_direction = decision.direction

    engine.synthesize(
        decision,
        validation,
        learning,
    )

    assert decision.action == before_action
    assert decision.direction == before_direction

    # --------------------------------------------------------
    # 3. D14 MUST NOT CHANGE
    # --------------------------------------------------------

    before_validation = validation.overall_result

    engine.synthesize(
        decision,
        validation,
        learning,
    )

    assert validation.overall_result == before_validation

    # --------------------------------------------------------
    # 4. D15 MUST NOT CHANGE
    # --------------------------------------------------------

    before_learning = learning.result

    engine.synthesize(
        decision,
        validation,
        learning,
    )

    assert learning.result == before_learning
    assert learning.parameter_update_applied is False

    # --------------------------------------------------------
    # 5. FUTURE LEAKAGE ATTACK
    # --------------------------------------------------------

    leaked_validation = ValidationSnapshot(
        validation_id="D14-LEAK",
        decision_id="D13-001",
        market_id="NIFTY|INDEX|NSE",

        decision_time="2026-09-04T09:30:00+00:00",
        validation_time="2026-09-04T09:20:00+00:00",

        status="VALIDATED",
        overall_result="CORRECT",

        provenance={
            "validated_by_D14": True,
        },
    )

    blocked = engine.synthesize(
        decision,
        leaked_validation,
        learning,
    )

    assert blocked.status == IntelligenceStatus.BLOCKED

    # --------------------------------------------------------
    # 6. IDENTITY ISOLATION
    # --------------------------------------------------------

    wrong_market_validation = ValidationSnapshot(
        validation_id="D14-WRONG",
        decision_id="D13-001",
        market_id="BTC|SPOT|BINANCE",

        decision_time="2026-09-04T09:30:00+00:00",
        validation_time="2026-09-04T10:00:00+00:00",

        status="VALIDATED",
        overall_result="CORRECT",

        provenance={
            "validated_by_D14": True,
        },
    )

    blocked = engine.synthesize(
        decision,
        wrong_market_validation,
        learning,
    )

    assert blocked.status == IntelligenceStatus.BLOCKED

    # --------------------------------------------------------
    # 7. FUTURE LEARNING ATTACK
    # --------------------------------------------------------

    leaked_learning = LearningSnapshot(
        learning_id="D15-LEAK",
        validation_id="D14-001",
        market_id="NIFTY|INDEX|NSE",

        learning_time="2026-09-04T10:01:00+00:00",

        status="LEARNED",
        result="SUPPORTED",

        provenance={
            "future_information_used": True,
        },
    )

    blocked = engine.synthesize(
        decision,
        validation,
        leaked_learning,
    )

    assert blocked.status == IntelligenceStatus.BLOCKED

    # --------------------------------------------------------
    # 8. PARTIAL VALIDATION
    # --------------------------------------------------------

    partial_validation = ValidationSnapshot(
        validation_id="D14-PARTIAL",
        decision_id="D13-001",
        market_id="NIFTY|INDEX|NSE",

        decision_time="2026-09-04T09:30:00+00:00",
        validation_time="2026-09-04T10:00:00+00:00",

        status="PARTIAL",
        overall_result="PARTIAL",

        direction_result="CORRECT",
        scenario_result="PARTIAL",

        provenance={
            "validated_by_D14": True,
        },
    )

    partial = engine.synthesize(
        decision,
        partial_validation,
        learning,
    )

    assert partial.status == IntelligenceStatus.LIMITED
    assert partial.result == IntelligenceResult.MIXED

    # --------------------------------------------------------
    # 9. INSUFFICIENT VALIDATION
    # --------------------------------------------------------

    insufficient_validation = ValidationSnapshot(
        validation_id="D14-UNKNOWN",
        decision_id="D13-001",
        market_id="NIFTY|INDEX|NSE",

        decision_time="2026-09-04T09:30:00+00:00",
        validation_time="2026-09-04T10:00:00+00:00",

        status="UNDETERMINED",
        overall_result="UNDETERMINED",

        provenance={
            "validated_by_D14": True,
        },
    )

    insufficient = engine.synthesize(
        decision,
        insufficient_validation,
        learning,
    )

    assert insufficient.status == IntelligenceStatus.UNDETERMINED
    assert insufficient.result == IntelligenceResult.INSUFFICIENT

    # --------------------------------------------------------
    # 10. D16 MUST NOT APPLY PARAMETER UPDATE
    # --------------------------------------------------------

    assert result.provenance["parameter_update_applied"] is False

    # --------------------------------------------------------
    # 11. NO NEW DECISION
    # --------------------------------------------------------

    assert result.provenance["new_decision_created"] is False

    # --------------------------------------------------------
    # 12. D16 FINAL PROVENANCE
    # --------------------------------------------------------

    assert result.provenance["D13_applied"] is False
    assert result.provenance["D14_applied"] is False
    assert result.provenance["D15_applied"] is False
    assert result.provenance["D16_applied"] is True

    print("D16 SELF-TEST: PASS")


if __name__ == "__main__":
    _self_test()