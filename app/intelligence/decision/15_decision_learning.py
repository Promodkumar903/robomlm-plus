"""
ROBOMLM_PLUS
D15 — DECISION LEARNING ENGINE

Decision Layer:
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
D15 LEARNING
D16 Intelligence

D15 converts validated historical decision outcomes into
auditable learning observations.

D15 MUST:
- consume D14 validation records
- preserve original D13 decision history
- preserve D14 validation history
- reject blocked/unvalidated records
- isolate market/instrument identity
- reject future leakage
- maintain learning provenance
- version learning updates
- separate observation from learned update
- avoid contaminating historical T0 decisions
- produce auditable learning records

D15 MUST NOT:
- create a new trading decision
- rewrite historical decisions
- modify D14 validation records
- use information unavailable at the original decision time
- directly become D16
- silently change production parameters
- invent universal learning weights
- invent arbitrary 0-100 proprietary scores

IMPORTANT:
Learning parameters/policies are externally supplied and versioned.
No universal V6 numerical learning formula is invented here.
"""


from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# =====================================================================
# ENUMS
# =====================================================================

class LearningStatus(str, Enum):
    LEARNED = "LEARNED"
    PARTIAL = "PARTIAL"
    REJECTED = "REJECTED"
    UNDETERMINED = "UNDETERMINED"
    BLOCKED = "BLOCKED"


class LearningResult(str, Enum):
    SUPPORTED = "SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    MIXED = "MIXED"
    INSUFFICIENT = "INSUFFICIENT"


class ValidationStatus(str, Enum):
    VALIDATED = "VALIDATED"
    PARTIAL = "PARTIAL"
    INVALIDATED = "INVALIDATED"
    UNDETERMINED = "UNDETERMINED"
    BLOCKED = "BLOCKED"


class ValidationResult(str, Enum):
    CORRECT = "CORRECT"
    INCORRECT = "INCORRECT"
    PARTIAL = "PARTIAL"
    UNDETERMINED = "UNDETERMINED"


class LearningReason(str, Enum):
    VALIDATED_INPUT = "VALIDATED_INPUT"
    PARTIAL_INPUT = "PARTIAL_INPUT"
    INVALIDATED_INPUT = "INVALIDATED_INPUT"
    BLOCKED_INPUT = "BLOCKED_INPUT"
    UNDETERMINED_INPUT = "UNDETERMINED_INPUT"

    FUTURE_LEAKAGE = "FUTURE_LEAKAGE"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    TIMESTAMP_ERROR = "TIMESTAMP_ERROR"

    NO_LEARNABLE_EVIDENCE = "NO_LEARNABLE_EVIDENCE"
    LEARNING_OBSERVATION_CREATED = "LEARNING_OBSERVATION_CREATED"

    PARAMETER_PROPOSAL_CREATED = "PARAMETER_PROPOSAL_CREATED"
    PARAMETER_UPDATE_NOT_APPLIED = "PARAMETER_UPDATE_NOT_APPLIED"


# =====================================================================
# HELPERS
# =====================================================================

def parse_dt(value: Any) -> Optional[datetime]:
    """
    Normalize timestamp into timezone-aware UTC datetime.
    """

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
        return dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


# =====================================================================
# D14 VALIDATION SNAPSHOT
# =====================================================================

@dataclass
class ValidationSnapshot:
    """
    Read-only representation of the D14 validation result consumed
    by D15.

    D15 does not mutate this object.
    """

    validation_id: str

    decision_id: str
    market_id: str

    decision_timestamp: datetime
    validation_timestamp: datetime

    status: ValidationStatus
    overall_result: ValidationResult

    direction_result: ValidationResult = ValidationResult.UNDETERMINED
    scenario_result: ValidationResult = ValidationResult.UNDETERMINED
    horizon_result: ValidationResult = ValidationResult.UNDETERMINED
    invalidation_result: ValidationResult = ValidationResult.UNDETERMINED
    pnl_result: ValidationResult = ValidationResult.UNDETERMINED

    leakage_detected: bool = False
    identity_mismatch: bool = False

    provenance: Dict[str, Any] = field(default_factory=dict)


# =====================================================================
# LEARNING OBSERVATION
# =====================================================================

@dataclass
class LearningObservation:
    """
    Immutable-style historical learning observation.

    This records what D14 taught the learning layer.

    It is NOT a trading decision.
    """

    observation_id: str

    decision_id: str
    validation_id: str

    market_id: str

    decision_timestamp: datetime
    validation_timestamp: datetime

    result: LearningResult

    source_validation_status: ValidationStatus
    source_validation_result: ValidationResult

    features: Dict[str, Any] = field(default_factory=dict)

    evidence: Dict[str, Any] = field(default_factory=dict)

    provenance: Dict[str, Any] = field(default_factory=dict)


# =====================================================================
# LEARNING UPDATE PROPOSAL
# =====================================================================

@dataclass
class LearningUpdateProposal:
    """
    Versioned proposal for a possible model/parameter update.

    D15 may propose an update.

    D15 does NOT silently apply it to production.
    """

    proposal_id: str

    market_id: str

    learning_observation_ids: List[str]

    parameter_family: str

    current_version: str

    proposed_version: str

    changes: Dict[str, Any] = field(default_factory=dict)

    rationale: List[str] = field(default_factory=list)

    approved: bool = False
    applied: bool = False

    provenance: Dict[str, Any] = field(default_factory=dict)


# =====================================================================
# D15 RESULT
# =====================================================================

@dataclass
class LearningRecord:
    """
    Auditable D15 output.
    """

    learning_id: str

    decision_id: str
    validation_id: str
    market_id: str

    status: LearningStatus
    result: LearningResult

    observation: Optional[LearningObservation] = None

    update_proposal: Optional[LearningUpdateProposal] = None

    notes: List[str] = field(default_factory=list)

    provenance: Dict[str, Any] = field(default_factory=dict)


# =====================================================================
# D15 ENGINE
# =====================================================================

class D15DecisionLearningEngine:

    VERSION = "D15-1.0"

    # -----------------------------------------------------------------
    # PUBLIC
    # -----------------------------------------------------------------

    def learn(
        self,
        validation: ValidationSnapshot,
        learning_id: str = "D15-LEARNING",
        observation_id: Optional[str] = None,
        create_update_proposal: bool = False,
        parameter_family: str = "UNSPECIFIED",
        current_version: str = "UNKNOWN"
    ) -> LearningRecord:

        # -------------------------------------------------------------
        # BASIC TIMESTAMP VALIDATION
        # -------------------------------------------------------------

        decision_time = parse_dt(
            validation.decision_timestamp
        )

        validation_time = parse_dt(
            validation.validation_timestamp
        )

        if decision_time is None or validation_time is None:
            return self._rejected(
                learning_id,
                validation,
                LearningReason.TIMESTAMP_ERROR.value
            )

        # -------------------------------------------------------------
        # VALIDATION TIME MUST BE AFTER DECISION TIME
        # -------------------------------------------------------------

        if validation_time <= decision_time:
            return self._rejected(
                learning_id,
                validation,
                LearningReason.FUTURE_LEAKAGE.value
            )

        # -------------------------------------------------------------
        # IDENTITY GATE
        # -------------------------------------------------------------

        if not validation.market_id:
            return self._rejected(
                learning_id,
                validation,
                LearningReason.IDENTITY_MISMATCH.value
            )

        # -------------------------------------------------------------
        # D14 PROVENANCE GATE
        # -------------------------------------------------------------

        if validation.provenance.get(
            "validated_by_D14"
        ) is not True:

            return self._rejected(
                learning_id,
                validation,
                LearningReason.BLOCKED_INPUT.value
            )

        # -------------------------------------------------------------
        # LEAKAGE GATE
        # -------------------------------------------------------------

        if validation.leakage_detected:
            return self._rejected(
                learning_id,
                validation,
                LearningReason.FUTURE_LEAKAGE.value
            )

        # -------------------------------------------------------------
        # IDENTITY MISMATCH GATE
        # -------------------------------------------------------------

        if validation.identity_mismatch:
            return self._rejected(
                learning_id,
                validation,
                LearningReason.IDENTITY_MISMATCH.value
            )

        # -------------------------------------------------------------
        # VALIDATION STATUS GATE
        # -------------------------------------------------------------

        if validation.status == ValidationStatus.BLOCKED:
            return self._rejected(
                learning_id,
                validation,
                LearningReason.BLOCKED_INPUT.value
            )

        if validation.status == ValidationStatus.UNDETERMINED:
            return self._undetermined(
                learning_id,
                validation
            )

        # -------------------------------------------------------------
        # DETERMINE LEARNING RESULT
        # -------------------------------------------------------------

        learning_result = self._classify_learning_result(
            validation
        )

        # -------------------------------------------------------------
        # BUILD LEARNING OBSERVATION
        # -------------------------------------------------------------

        observation = LearningObservation(
            observation_id=(
                observation_id
                or f"{learning_id}-OBS"
            ),

            decision_id=validation.decision_id,

            validation_id=validation.validation_id,

            market_id=validation.market_id,

            decision_timestamp=decision_time,

            validation_timestamp=validation_time,

            result=learning_result,

            source_validation_status=validation.status,

            source_validation_result=validation.overall_result,

            features={
                "direction_result":
                    validation.direction_result.value,

                "scenario_result":
                    validation.scenario_result.value,

                "horizon_result":
                    validation.horizon_result.value,

                "invalidation_result":
                    validation.invalidation_result.value,

                "pnl_result":
                    validation.pnl_result.value,
            },

            evidence={
                "validation_status":
                    validation.status.value,

                "overall_result":
                    validation.overall_result.value,
            },

            provenance={
                "engine":
                    "D15_DECISION_LEARNING",

                "engine_version":
                    self.VERSION,

                "source_engine":
                    validation.provenance.get(
                        "engine",
                        "D14_DECISION_VALIDATION"
                    ),

                "source_engine_version":
                    validation.provenance.get(
                        "engine_version",
                        "UNKNOWN"
                    ),

                "decision_id":
                    validation.decision_id,

                "validation_id":
                    validation.validation_id,

                "decision_time":
                    decision_time.isoformat(),

                "validation_time":
                    validation_time.isoformat(),

                "future_information_used_for_T0":
                    False,

                "historical_outcome_used":
                    True,

                "D13_modified":
                    False,

                "D14_modified":
                    False,

                "D16_applied":
                    False,
            }
        )

        # -------------------------------------------------------------
        # OPTIONAL UPDATE PROPOSAL
        # -------------------------------------------------------------

        proposal = None

        if create_update_proposal:

            proposal = self._create_update_proposal(
                observation=observation,
                parameter_family=parameter_family,
                current_version=current_version
            )

        # -------------------------------------------------------------
        # FINAL STATUS
        # -------------------------------------------------------------

        if learning_result == LearningResult.SUPPORTED:
            status = LearningStatus.LEARNED

        elif learning_result == LearningResult.CONTRADICTED:
            status = LearningStatus.LEARNED

        elif learning_result == LearningResult.MIXED:
            status = LearningStatus.PARTIAL

        else:
            status = LearningStatus.UNDETERMINED

        # -------------------------------------------------------------
        # FINAL PROVENANCE
        # -------------------------------------------------------------

        provenance = {
            "engine":
                "D15_DECISION_LEARNING",

            "engine_version":
                self.VERSION,

            "source_validation_id":
                validation.validation_id,

            "source_decision_id":
                validation.decision_id,

            "source_D14_validated":
                True,

            "learning_observation_created":
                True,

            "parameter_update_applied":
                False,

            "production_parameters_modified":
                False,

            "D13_modified":
                False,

            "D14_modified":
                False,

            "D16_applied":
                False,

            "future_information_used_for_T0":
                False,

            "D15_ready":
                True,
        }

        return LearningRecord(
            learning_id=learning_id,

            decision_id=validation.decision_id,

            validation_id=validation.validation_id,

            market_id=validation.market_id,

            status=status,

            result=learning_result,

            observation=observation,

            update_proposal=proposal,

            notes=[],

            provenance=provenance,
        )

    # -----------------------------------------------------------------
    # LEARNING CLASSIFICATION
    # -----------------------------------------------------------------

    def _classify_learning_result(
        self,
        validation: ValidationSnapshot
    ) -> LearningResult:

        # -------------------------------------------------------------
        # D14 CORRECT
        # -------------------------------------------------------------

        if validation.overall_result == ValidationResult.CORRECT:
            return LearningResult.SUPPORTED

        # -------------------------------------------------------------
        # D14 INCORRECT
        # -------------------------------------------------------------

        if validation.overall_result == ValidationResult.INCORRECT:
            return LearningResult.CONTRADICTED

        # -------------------------------------------------------------
        # D14 PARTIAL
        # -------------------------------------------------------------

        if validation.overall_result == ValidationResult.PARTIAL:
            return LearningResult.MIXED

        # -------------------------------------------------------------
        # UNKNOWN
        # -------------------------------------------------------------

        return LearningResult.INSUFFICIENT

    # -----------------------------------------------------------------
    # UPDATE PROPOSAL
    # -----------------------------------------------------------------

    def _create_update_proposal(
        self,
        observation: LearningObservation,
        parameter_family: str,
        current_version: str
    ) -> LearningUpdateProposal:

        proposed_version = (
            f"{current_version}->PROPOSED"
        )

        return LearningUpdateProposal(
            proposal_id=
                f"PROP-{observation.observation_id}",

            market_id=observation.market_id,

            learning_observation_ids=[
                observation.observation_id
            ],

            parameter_family=parameter_family,

            current_version=current_version,

            proposed_version=proposed_version,

            changes={},

            rationale=[
                "D15 generated a versioned learning proposal.",
                "No production parameter was modified.",
                "Parameter calibration remains an external approval step."
            ],

            approved=False,

            applied=False,

            provenance={
                "engine":
                    "D15_DECISION_LEARNING",

                "engine_version":
                    self.VERSION,

                "proposal_only":
                    True,

                "production_update_applied":
                    False,

                "requires_external_approval":
                    True,

                "D16_applied":
                    False,
            }
        )

    # -----------------------------------------------------------------
    # REJECTED
    # -----------------------------------------------------------------

    def _rejected(
        self,
        learning_id: str,
        validation: ValidationSnapshot,
        reason: str
    ) -> LearningRecord:

        return LearningRecord(
            learning_id=learning_id,

            decision_id=validation.decision_id,

            validation_id=validation.validation_id,

            market_id=validation.market_id,

            status=LearningStatus.REJECTED,

            result=LearningResult.INSUFFICIENT,

            observation=None,

            update_proposal=None,

            notes=[reason],

            provenance={
                "engine":
                    "D15_DECISION_LEARNING",

                "engine_version":
                    self.VERSION,

                "input_accepted":
                    False,

                "learning_applied":
                    False,

                "production_parameters_modified":
                    False,

                "D13_modified":
                    False,

                "D14_modified":
                    False,

                "D16_applied":
                    False,

                "D15_ready":
                    False,
            }
        )

    # -----------------------------------------------------------------
    # UNDETERMINED
    # -----------------------------------------------------------------

    def _undetermined(
        self,
        learning_id: str,
        validation: ValidationSnapshot
    ) -> LearningRecord:

        return LearningRecord(
            learning_id=learning_id,

            decision_id=validation.decision_id,

            validation_id=validation.validation_id,

            market_id=validation.market_id,

            status=LearningStatus.UNDETERMINED,

            result=LearningResult.INSUFFICIENT,

            observation=None,

            update_proposal=None,

            notes=[
                LearningReason.UNDETERMINED_INPUT.value
            ],

            provenance={
                "engine":
                    "D15_DECISION_LEARNING",

                "engine_version":
                    self.VERSION,

                "input_accepted":
                    False,

                "learning_applied":
                    False,

                "production_parameters_modified":
                    False,

                "D13_modified":
                    False,

                "D14_modified":
                    False,

                "D16_applied":
                    False,

                "D15_ready":
                    False,
            }
        )


# =====================================================================
# SELF TEST
# =====================================================================

def _self_test() -> None:

    engine = D15DecisionLearningEngine()

    t0 = datetime(
        2026,
        9,
        4,
        9,
        30,
        tzinfo=timezone.utc
    )

    t1 = datetime(
        2026,
        9,
        4,
        10,
        30,
        tzinfo=timezone.utc
    )

    # =================================================================
    # 1. VALIDATED D14 -> D15 LEARNING
    # =================================================================

    validation = ValidationSnapshot(
        validation_id="VAL-001",

        decision_id="DEC-001",

        market_id="NSE:NIFTY:SPOT",

        decision_timestamp=t0,

        validation_timestamp=t1,

        status=ValidationStatus.VALIDATED,

        overall_result=ValidationResult.CORRECT,

        direction_result=ValidationResult.CORRECT,

        scenario_result=ValidationResult.CORRECT,

        horizon_result=ValidationResult.CORRECT,

        invalidation_result=ValidationResult.UNDETERMINED,

        pnl_result=ValidationResult.CORRECT,

        leakage_detected=False,

        identity_mismatch=False,

        provenance={
            "engine":
                "D14_DECISION_VALIDATION",

            "engine_version":
                "D14-1.0",

            "validated_by_D14":
                True,

            "D15_ready":
                True,

            "future_outcome_observed":
                True,
        }
    )

    result = engine.learn(
        validation,
        learning_id="LEARN-001"
    )

    assert result.status == LearningStatus.LEARNED

    assert result.result == LearningResult.SUPPORTED

    assert result.observation is not None

    assert (
        result.observation.result
        == LearningResult.SUPPORTED
    )

    assert result.provenance["learning_observation_created"] is True

    assert result.provenance["parameter_update_applied"] is False

    assert result.provenance["production_parameters_modified"] is False

    # =================================================================
    # 2. INVALIDATED D14 -> CONTRADICTED LEARNING
    # =================================================================

    invalidated = ValidationSnapshot(
        validation_id="VAL-002",

        decision_id="DEC-002",

        market_id="NSE:NIFTY:SPOT",

        decision_timestamp=t0,

        validation_timestamp=t1,

        status=ValidationStatus.INVALIDATED,

        overall_result=ValidationResult.INCORRECT,

        direction_result=ValidationResult.INCORRECT,

        scenario_result=ValidationResult.INCORRECT,

        horizon_result=ValidationResult.CORRECT,

        invalidation_result=ValidationResult.INCORRECT,

        pnl_result=ValidationResult.INCORRECT,

        provenance={
            "engine":
                "D14_DECISION_VALIDATION",

            "engine_version":
                "D14-1.0",

            "validated_by_D14":
                True,

            "D15_ready":
                True,
        }
    )

    result_invalid = engine.learn(
        invalidated,
        learning_id="LEARN-002"
    )

    assert result_invalid.status == LearningStatus.LEARNED

    assert (
        result_invalid.result
        == LearningResult.CONTRADICTED
    )

    # =================================================================
    # 3. PARTIAL D14 -> MIXED LEARNING
    # =================================================================

    partial = ValidationSnapshot(
        validation_id="VAL-003",

        decision_id="DEC-003",

        market_id="NSE:NIFTY:SPOT",

        decision_timestamp=t0,

        validation_timestamp=t1,

        status=ValidationStatus.PARTIAL,

        overall_result=ValidationResult.PARTIAL,

        direction_result=ValidationResult.CORRECT,

        scenario_result=ValidationResult.PARTIAL,

        horizon_result=ValidationResult.UNDETERMINED,

        invalidation_result=ValidationResult.UNDETERMINED,

        pnl_result=ValidationResult.CORRECT,

        provenance={
            "engine":
                "D14_DECISION_VALIDATION",

            "engine_version":
                "D14-1.0",

            "validated_by_D14":
                True,

            "D15_ready":
                True,
        }
    )

    result_partial = engine.learn(
        partial,
        learning_id="LEARN-003"
    )

    assert result_partial.status == LearningStatus.PARTIAL

    assert (
        result_partial.result
        == LearningResult.MIXED
    )

    # =================================================================
    # 4. BLOCKED D14 MUST NOT ENTER LEARNING
    # =================================================================

    blocked = ValidationSnapshot(
        validation_id="VAL-004",

        decision_id="DEC-004",

        market_id="NSE:NIFTY:SPOT",

        decision_timestamp=t0,

        validation_timestamp=t1,

        status=ValidationStatus.BLOCKED,

        overall_result=ValidationResult.UNDETERMINED,

        leakage_detected=True,

        identity_mismatch=False,

        provenance={
            "engine":
                "D14_DECISION_VALIDATION",

            "engine_version":
                "D14-1.0",

            "validated_by_D14":
                False,

            "D15_ready":
                False,
        }
    )

    result_blocked = engine.learn(
        blocked,
        learning_id="LEARN-004"
    )

    assert result_blocked.status == LearningStatus.REJECTED

    assert result_blocked.observation is None

    assert result_blocked.provenance["learning_applied"] is False

    # =================================================================
    # 5. FUTURE LEAKAGE ATTACK
    # =================================================================

    leaked = ValidationSnapshot(
        validation_id="VAL-005",

        decision_id="DEC-005",

        market_id="NSE:NIFTY:SPOT",

        # Validation timestamp is BEFORE decision time.
        decision_timestamp=t1,

        validation_timestamp=t0,

        status=ValidationStatus.VALIDATED,

        overall_result=ValidationResult.CORRECT,

        provenance={
            "engine":
                "D14_DECISION_VALIDATION",

            "engine_version":
                "D14-1.0",

            "validated_by_D14":
                True,
        }
    )

    result_leak = engine.learn(
        leaked,
        learning_id="LEARN-005"
    )

    assert result_leak.status == LearningStatus.REJECTED

    assert (
        LearningReason.FUTURE_LEAKAGE.value
        in result_leak.notes
    )

    # =================================================================
    # 6. IDENTITY ISOLATION
    # =================================================================

    identity_bad = ValidationSnapshot(
        validation_id="VAL-006",

        decision_id="DEC-006",

        market_id="",

        decision_timestamp=t0,

        validation_timestamp=t1,

        status=ValidationStatus.VALIDATED,

        overall_result=ValidationResult.CORRECT,

        provenance={
            "engine":
                "D14_DECISION_VALIDATION",

            "engine_version":
                "D14-1.0",

            "validated_by_D14":
                True,
        }
    )

    result_identity = engine.learn(
        identity_bad,
        learning_id="LEARN-006"
    )

    assert result_identity.status == LearningStatus.REJECTED

    # =================================================================
    # 7. D15 MUST NOT MODIFY D13 / D14
    # =================================================================

    before_decision_id = validation.decision_id

    before_validation_id = validation.validation_id

    before_market_id = validation.market_id

    engine.learn(
        validation,
        learning_id="LEARN-007",
        create_update_proposal=True,
        parameter_family="TEST_FAMILY",
        current_version="V1"
    )

    assert validation.decision_id == before_decision_id

    assert validation.validation_id == before_validation_id

    assert validation.market_id == before_market_id

    # =================================================================
    # 8. UPDATE PROPOSAL MUST NOT APPLY AUTOMATICALLY
    # =================================================================

    proposal_result = engine.learn(
        validation,
        learning_id="LEARN-008",
        create_update_proposal=True,
        parameter_family="TEST_FAMILY",
        current_version="V1"
    )

    assert proposal_result.update_proposal is not None

    assert (
        proposal_result.update_proposal.approved
        is False
    )

    assert (
        proposal_result.update_proposal.applied
        is False
    )

    assert (
        proposal_result.provenance[
            "parameter_update_applied"
        ]
        is False
    )

    assert (
        proposal_result.provenance[
            "production_parameters_modified"
        ]
        is False
    )

    # =================================================================
    # 9. D16 MUST NOT RUN INSIDE D15
    # =================================================================

    assert (
        proposal_result.provenance["D16_applied"]
        is False
    )

    # =================================================================
    # PASS
    # =================================================================

    print("D15 SELF-TEST: PASS")


# =====================================================================
# ENTRY POINT
# =====================================================================

if __name__ == "__main__":
    _self_test()