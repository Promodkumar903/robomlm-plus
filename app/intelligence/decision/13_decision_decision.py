# ============================================================
# D13 - DECISION AUTHORITY
# PART 1 / 4
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


# ============================================================
# ENGINE METADATA
# ============================================================

D13_ENGINE_NAME = "D13_DecisionAuthority"
D13_ENGINE_VERSION = "V6-CAS-1.0"


# ============================================================
# STATUS
# ============================================================

class D13Status(str, Enum):
    READY = "READY"
    LIMITED = "LIMITED"
    BLOCKED = "BLOCKED"
    UNDETERMINED = "UNDETERMINED"


# ============================================================
# DECISION STATE
# ============================================================

class DecisionState(str, Enum):
    ACTIONABLE = "ACTIONABLE"
    WAIT = "WAIT"
    NO_DECISION = "NO_DECISION"
    BLOCKED = "BLOCKED"
    UNDETERMINED = "UNDETERMINED"


# ============================================================
# DECISION TYPE
# ============================================================

class DecisionType(str, Enum):
    CONTINUE = "CONTINUE"
    REVERSE = "REVERSE"
    BREAKOUT = "BREAKOUT"
    BREAKDOWN = "BREAKDOWN"
    RANGE = "RANGE"
    WAIT = "WAIT"
    NO_DECISION = "NO_DECISION"
    BLOCKED = "BLOCKED"
    UNDETERMINED = "UNDETERMINED"


# ============================================================
# EVIDENCE QUALITY
# ============================================================

class D13EvidenceQuality(str, Enum):
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    WEAK = "WEAK"
    INSUFFICIENT = "INSUFFICIENT"


# ============================================================
# AUTHORITY SOURCES
# ============================================================

D13_UPSTREAM_AUTHORITIES = (
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
)

D13_DOWNSTREAM_VALIDATOR = "D14"
D13_LEARNING_AUTHORITY = "D15"
D13_INTELLIGENCE_SYNTHESIS = "D16"


# ============================================================
# FORBIDDEN OUTPUTS
# ============================================================

D13_FORBIDDEN_OUTPUTS = {
    "EXECUTE",
    "ORDER",
    "PLACE_ORDER",
    "POSITION_SIZE",
    "LEVERAGE",
    "PROFIT_TARGET",
    "PNL_TARGET",
    "GUARANTEED_PROFIT",
    "UNIVERSAL_PROBABILITY",
    "FABRICATED_CONFIDENCE",
}


# ============================================================
# INPUT CONTRACT
# ============================================================

@dataclass
class D13DecisionInput:
    """
    Validated information arriving at D13.

    D13 does not manufacture upstream evidence.
    """

    market_id: str

    as_of: Any

    market_state: Optional[str] = None
    transition_type: Optional[str] = None

    scenarios: List[Any] = field(default_factory=list)

    evidence: List[Any] = field(default_factory=list)

    context: Dict[str, Any] = field(
        default_factory=dict
    )

    risk_context: Dict[str, Any] = field(
        default_factory=dict
    )

    validation_context: Dict[str, Any] = field(
        default_factory=dict
    )

    provenance: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# DECISION RESULT
# ============================================================

@dataclass
class D13DecisionResult:
    """
    D13 authoritative decision result.

    Decision authority belongs to D13.
    Execution authority does not.
    """

    status: D13Status

    market_id: str
    as_of: Any

    decision_state: DecisionState
    decision_type: DecisionType

    rationale: List[str] = field(
        default_factory=list
    )

    supporting_evidence: List[str] = field(
        default_factory=list
    )

    conflicting_evidence: List[str] = field(
        default_factory=list
    )

    scenario_ids: List[str] = field(
        default_factory=list
    )

    market_state: Optional[str] = None
    transition_type: Optional[str] = None

    evidence_quality: D13EvidenceQuality = (
        D13EvidenceQuality.INSUFFICIENT
    )

    decision_performed: bool = True

    execution_authority: bool = False

    d13_authority: str = "D13"
    d14_validation_authority: str = "D14"

    provenance: Dict[str, Any] = field(
        default_factory=dict
    )

    warnings: List[str] = field(
        default_factory=list
    )


# ============================================================
# D13 ENGINE
# ============================================================

class D13DecisionAuthorityEngine:
    """
    D13 Decision Authority.

    Responsibilities:
        1. Consume validated D1-D12 information.
        2. Reconcile state, transition and scenario context.
        3. Determine whether a decision is sufficiently supported.
        4. Produce an explicit decision state.
        5. Preserve provenance and contradiction information.

    D13 does NOT:
        - execute trades
        - calculate position size
        - fabricate probability
        - fabricate confidence
        - replace D14 validation
        - replace D15 learning
        - replace D16 intelligence synthesis
    """

    def __init__(self) -> None:
        self._history: List[D13DecisionResult] = []
        self._latest: Optional[D13DecisionResult] = None

    # --------------------------------------------------------
    # INPUT VALIDATION
    # --------------------------------------------------------

    @staticmethod
    def validate_input(
        data: D13DecisionInput,
    ) -> List[str]:

        errors: List[str] = []

        if not isinstance(data, D13DecisionInput):
            return ["INVALID_INPUT_OBJECT"]

        if not str(data.market_id).strip():
            errors.append("MISSING_MARKET_ID")

        if data.as_of is None:
            errors.append("MISSING_AS_OF")

        if not data.market_state:
            errors.append("MISSING_MARKET_STATE")

        if not data.transition_type:
            errors.append("MISSING_TRANSITION_TYPE")

        return errors

    # --------------------------------------------------------
    # SCENARIO EXTRACTION
    # --------------------------------------------------------

    @staticmethod
    def _scenario_id(
        scenario: Any,
    ) -> Optional[str]:

        if isinstance(scenario, dict):
            value = scenario.get("scenario_id")
            return (
                str(value)
                if value is not None
                else None
            )

        value = getattr(
            scenario,
            "scenario_id",
            None,
        )

        return (
            str(value)
            if value is not None
            else None
        )

    @staticmethod
    def _scenario_role(
        scenario: Any,
    ) -> Optional[str]:

        if isinstance(scenario, dict):
            value = scenario.get("role")
        else:
            value = getattr(
                scenario,
                "role",
                None,
            )

        if value is None:
            return None

        if hasattr(value, "value"):
            return str(value.value).upper()

        return str(value).upper()

    @staticmethod
    def _scenario_direction(
        scenario: Any,
    ) -> str:

        if isinstance(scenario, dict):
            value = scenario.get(
                "direction",
                "NEUTRAL",
            )
        else:
            value = getattr(
                scenario,
                "direction",
                "NEUTRAL",
            )

        if value is None:
            return "NEUTRAL"

        return str(value).upper()

    # --------------------------------------------------------
    # EVIDENCE QUALITY
    # --------------------------------------------------------

    @staticmethod
    def assess_evidence_quality(
        data: D13DecisionInput,
    ) -> D13EvidenceQuality:

        evidence_count = len(data.evidence)

        if evidence_count == 0:
            return D13EvidenceQuality.INSUFFICIENT

        if evidence_count >= 5:
            return D13EvidenceQuality.STRONG

        if evidence_count >= 3:
            return D13EvidenceQuality.MODERATE

        if evidence_count >= 1:
            return D13EvidenceQuality.WEAK

        return D13EvidenceQuality.INSUFFICIENT

    # --------------------------------------------------------
    # SCENARIO RECONCILIATION
    # --------------------------------------------------------

    def reconcile_scenarios(
        self,
        scenarios: Sequence[Any],
    ) -> Dict[str, Any]:

        primary: List[Any] = []
        alternatives: List[Any] = []
        invalidations: List[Any] = []

        for scenario in scenarios:

            role = self._scenario_role(
                scenario
            )

            if role == "PRIMARY":
                primary.append(scenario)

            elif role == "ALTERNATIVE":
                alternatives.append(scenario)

            elif role == "INVALIDATION":
                invalidations.append(scenario)

        return {
            "primary": primary,
            "alternatives": alternatives,
            "invalidations": invalidations,
            "primary_count": len(primary),
            "alternative_count": len(alternatives),
            "invalidation_count": len(
                invalidations
            ),
        }

    # --------------------------------------------------------
    # DIRECTION RECONCILIATION
    # --------------------------------------------------------

    def reconcile_direction(
        self,
        market_state: str,
        transition_type: str,
        scenarios: Sequence[Any],
    ) -> Dict[str, Any]:

        state = str(
            market_state
        ).upper()

        transition = str(
            transition_type
        ).upper()

        directions = []

        for scenario in scenarios:
            direction = self._scenario_direction(
                scenario
            )

            if direction in {
                "UP",
                "DOWN",
                "NEUTRAL",
            }:
                directions.append(direction)

        unique_directions = sorted(
            set(directions)
        )

        conflict = (
            "UP" in unique_directions
            and
            "DOWN" in unique_directions
        )

        return {
            "state": state,
            "transition": transition,
            "directions": unique_directions,
            "direction_conflict": conflict,
        }

    # --------------------------------------------------------
    # DECISION DETERMINATION
    # --------------------------------------------------------

    def determine_decision(
        self,
        data: D13DecisionInput,
        scenario_info: Dict[str, Any],
        direction_info: Dict[str, Any],
    ) -> Tuple[
        DecisionState,
        DecisionType,
        List[str],
    ]:

        rationale: List[str] = []

        primary = scenario_info["primary"]

        if direction_info["direction_conflict"]:
            rationale.append(
                "UPWARD_AND_DOWNWARD_SCENARIO_BRANCHES_CONFLICT"
            )

            return (
                DecisionState.WAIT,
                DecisionType.WAIT,
                rationale,
            )

        if not primary:
            rationale.append(
                "NO_PRIMARY_SCENARIO_AVAILABLE"
            )

            return (
                DecisionState.NO_DECISION,
                DecisionType.NO_DECISION,
                rationale,
            )

        state = str(
            data.market_state
        ).upper()

        transition = str(
            data.transition_type
        ).upper()

        direction = (
            direction_info["directions"][0]
            if len(direction_info["directions"]) == 1
            else "NEUTRAL"
        )

        if state in {
            "CHAOS",
            "UNKNOWN",
            "UNDETERMINED",
        }:
            rationale.append(
                "MARKET_STATE_DOES_NOT_SUPPORT_DIRECT_DECISION"
            )

            return (
                DecisionState.WAIT,
                DecisionType.WAIT,
                rationale,
            )

        if transition in {
            "UNKNOWN",
            "UNDETERMINED",
        }:
            rationale.append(
                "TRANSITION_INFORMATION_IS_INSUFFICIENT"
            )

            return (
                DecisionState.WAIT,
                DecisionType.WAIT,
                rationale,
            )

        if direction == "UP":
            if "BREAKOUT" in transition:
                rationale.append(
                    "VALIDATED_UPWARD_SCENARIO_BRANCH_PRESENT"
                )

                return (
                    DecisionState.ACTIONABLE,
                    DecisionType.BREAKOUT,
                    rationale,
                )

            rationale.append(
                "UPWARD_PRIMARY_SCENARIO_SUPPORTED"
            )

            return (
                DecisionState.ACTIONABLE,
                DecisionType.CONTINUE,
                rationale,
            )

        if direction == "DOWN":
            if "BREAKDOWN" in transition:
                rationale.append(
                    "VALIDATED_DOWNWARD_SCENARIO_BRANCH_PRESENT"
                )

                return (
                    DecisionState.ACTIONABLE,
                    DecisionType.BREAKDOWN,
                    rationale,
                )

            rationale.append(
                "DOWNWARD_PRIMARY_SCENARIO_SUPPORTED"
            )

            return (
                DecisionState.ACTIONABLE,
                DecisionType.CONTINUE,
                rationale,
            )

        rationale.append(
            "DIRECTIONAL_RESOLUTION_IS_NOT_ESTABLISHED"
        )

        return (
            DecisionState.WAIT,
            DecisionType.WAIT,
            rationale,
        )

    # --------------------------------------------------------
    # EVALUATE
    # --------------------------------------------------------

    def evaluate(
        self,
        data: D13DecisionInput,
    ) -> D13DecisionResult:

        errors = self.validate_input(data)

        if errors:
            result = D13DecisionResult(
                status=D13Status.BLOCKED,
                market_id=(
                    data.market_id
                    if isinstance(
                        data,
                        D13DecisionInput,
                    )
                    else ""
                ),
                as_of=(
                    data.as_of
                    if isinstance(
                        data,
                        D13DecisionInput,
                    )
                    else None
                ),
                decision_state=DecisionState.BLOCKED,
                decision_type=DecisionType.BLOCKED,
                rationale=[],
                evidence_quality=(
                    D13EvidenceQuality.INSUFFICIENT
                ),
                decision_performed=False,
                execution_authority=False,
                provenance={
                    "engine": D13_ENGINE_NAME,
                    "version": D13_ENGINE_VERSION,
                    "validation_errors": errors,
                    "d13_authority": "D13",
                    "d14_validation_authority": "D14",
                },
                warnings=errors,
            )

            self._record(result)
            return result

        scenario_info = self.reconcile_scenarios(
            data.scenarios
        )

        direction_info = self.reconcile_direction(
            data.market_state,
            data.transition_type,
            data.scenarios,
        )

        quality = self.assess_evidence_quality(
            data
        )

        decision_state, decision_type, rationale = (
            self.determine_decision(
                data,
                scenario_info,
                direction_info,
            )
        )

        scenario_ids = []

        for scenario in data.scenarios:
            scenario_id = self._scenario_id(
                scenario
            )

            if scenario_id is not None:
                scenario_ids.append(
                    scenario_id
                )

        warnings: List[str] = []

        if quality == D13EvidenceQuality.INSUFFICIENT:
            warnings.append(
                "INSUFFICIENT_EVIDENCE"
            )

            decision_state = DecisionState.WAIT
            decision_type = DecisionType.WAIT

        if quality == D13EvidenceQuality.WEAK:
            warnings.append(
                "EVIDENCE_QUALITY_WEAK"
            )

        if direction_info[
            "direction_conflict"
        ]:
            warnings.append(
                "DIRECTIONAL_SCENARIO_CONFLICT"
            )

        status = D13Status.READY

        if decision_state in {
            DecisionState.WAIT,
            DecisionState.NO_DECISION,
        }:
            status = D13Status.LIMITED

        result = D13DecisionResult(
            status=status,
            market_id=data.market_id,
            as_of=data.as_of,
            decision_state=decision_state,
            decision_type=decision_type,
            rationale=rationale,
            supporting_evidence=[],
            conflicting_evidence=(
                [
                    "UP_DOWN_SCENARIO_CONFLICT"
                ]
                if direction_info[
                    "direction_conflict"
                ]
                else []
            ),
            scenario_ids=scenario_ids,
            market_state=data.market_state,
            transition_type=data.transition_type,
            evidence_quality=quality,
            decision_performed=True,
            execution_authority=False,
            d13_authority="D13",
            d14_validation_authority="D14",
            provenance={
                "engine": D13_ENGINE_NAME,
                "version": D13_ENGINE_VERSION,
                "d10_state_consumed": True,
                "d11_transition_consumed": True,
                "d12_scenarios_consumed": True,
                "d14_validation_authority": "D14",
                "d15_learning_authority": "D15",
                "d16_intelligence_synthesis": "D16",
                "future_outcome_validated": False,
                "execution_authority": False,
            },
            warnings=warnings,
        )

        self._record(result)
        return result

    # --------------------------------------------------------
    # HISTORY
    # --------------------------------------------------------

    def _record(
        self,
        result: D13DecisionResult,
    ) -> None:
        self._history.append(result)
        self._latest = result

    @property
    def history(
        self,
    ) -> List[D13DecisionResult]:
        return list(self._history)

    @property
    def latest(
        self,
    ) -> Optional[D13DecisionResult]:
        return self._latest

    # --------------------------------------------------------
    # CONTRACT
    # --------------------------------------------------------

    @staticmethod
    def result_contract(
        result: D13DecisionResult,
    ) -> Dict[str, Any]:

        return {
            "engine": D13_ENGINE_NAME,
            "version": D13_ENGINE_VERSION,
            "status": result.status.value,
            "market_id": result.market_id,
            "as_of": result.as_of,
            "decision_state": (
                result.decision_state.value
            ),
            "decision_type": (
                result.decision_type.value
            ),
            "market_state": result.market_state,
            "transition_type": result.transition_type,
            "scenario_count": len(
                result.scenario_ids
            ),
            "evidence_quality": (
                result.evidence_quality.value
            ),
            "decision_performed": (
                result.decision_performed
            ),
            "execution_authority": (
                result.execution_authority
            ),
            "d13_authority": result.d13_authority,
            "d14_validation_authority": (
                result.d14_validation_authority
            ),
        }

    # --------------------------------------------------------
    # SELF TEST
    # --------------------------------------------------------

    def self_test(self) -> Dict[str, bool]:

        class TestScenario:
            scenario_id = "D13-S01"
            role = "PRIMARY"
            direction = "UP"

        data = D13DecisionInput(
            market_id="D13_SELF_TEST",
            as_of="2026-01-01T10:00:00",
            market_state="BULLISH_EXPANSION",
            transition_type="BULLISH_DEVELOPMENT",
            scenarios=[
                TestScenario()
            ],
            evidence=[
                {
                    "evidence_id": "E1",
                    "value": "validated",
                },
                {
                    "evidence_id": "E2",
                    "value": "supporting",
                },
                {
                    "evidence_id": "E3",
                    "value": "structure",
                },
            ],
        )

        result = self.evaluate(data)

        return {
            "engine_ready": (
                result.status
                in {
                    D13Status.READY,
                    D13Status.LIMITED,
                }
            ),
            "decision_created": (
                result.decision_performed is True
            ),
            "d13_authority": (
                result.d13_authority == "D13"
            ),
            "d14_authority": (
                result.d14_validation_authority
                == "D14"
            ),
            "execution_false": (
                result.execution_authority is False
            ),
            "no_position_size": (
                not hasattr(
                    result,
                    "position_size",
                )
            ),
            "no_probability_field": (
                not hasattr(
                    result,
                    "probability",
                )
            ),
        }


# ============================================================
# FACTORY
# ============================================================

def create_d13_decision_authority_engine(
) -> D13DecisionAuthorityEngine:

    return D13DecisionAuthorityEngine()


# ============================================================
# PART 1 EXPORTS
# ============================================================

D13_PART1_EXPORTS = [
    "D13Status",
    "DecisionState",
    "DecisionType",
    "D13EvidenceQuality",
    "D13DecisionInput",
    "D13DecisionResult",
    "D13DecisionAuthorityEngine",
    "create_d13_decision_authority_engine",
]
# ============================================================
# D13 DECISION AUTHORITY
# PART 2 / 4
# Evidence Reconciliation + Upstream Authority Validation
# ============================================================

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple
from datetime import datetime


# ============================================================
# PART-2 CONSTANTS
# ============================================================

D13_PART2_NAME = "D13_EvidenceAuthorityReconciliation"
D13_PART2_VERSION = "V6-CAS-1.0"

D13_UPSTREAM_ENGINES = (
    "D10_MarketState",
    "D11_DecisionTransition",
    "D12_FutureScenario",
)

D13_DOWNSTREAM_ENGINES = (
    "D14_Validation",
    "D15_Learning",
    "D16_IntelligenceSynthesis",
)


# ============================================================
# ENUMS
# ============================================================

class D13ReconciliationStatus(str, Enum):
    READY = "READY"
    LIMITED = "LIMITED"
    BLOCKED = "BLOCKED"
    UNDETERMINED = "UNDETERMINED"


class D13EvidenceDisposition(str, Enum):
    SUPPORTING = "SUPPORTING"
    CONFLICTING = "CONFLICTING"
    NEUTRAL = "NEUTRAL"
    INVALID = "INVALID"
    UNAVAILABLE = "UNAVAILABLE"


class D13ConflictType(str, Enum):
    NONE = "NONE"
    STATE_CONFLICT = "STATE_CONFLICT"
    TRANSITION_CONFLICT = "TRANSITION_CONFLICT"
    SCENARIO_CONFLICT = "SCENARIO_CONFLICT"
    DIRECTION_CONFLICT = "DIRECTION_CONFLICT"
    TIMESTAMP_CONFLICT = "TIMESTAMP_CONFLICT"
    PROVENANCE_CONFLICT = "PROVENANCE_CONFLICT"
    AUTHORITY_CONFLICT = "AUTHORITY_CONFLICT"
    DATA_CONTRACT_CONFLICT = "DATA_CONTRACT_CONFLICT"
    UNKNOWN_CONFLICT = "UNKNOWN_CONFLICT"


# ============================================================
# EVIDENCE RECORD
# ============================================================

@dataclass
class D13EvidenceRecord:
    evidence_id: str
    source: str
    dimension: str
    value: Any = None

    observed_at: Optional[Any] = None
    as_of: Optional[Any] = None

    provenance: Dict[str, Any] = field(default_factory=dict)

    disposition: D13EvidenceDisposition = (
        D13EvidenceDisposition.NEUTRAL
    )

    validity: bool = True
    reason: str = ""

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# UPSTREAM AUTHORITY RECORD
# ============================================================

@dataclass
class D13UpstreamAuthorityRecord:
    engine: str
    status: str

    authority: bool = True
    decision_performed: bool = False
    execution_authority: bool = False

    market_id: Optional[str] = None
    as_of: Optional[Any] = None

    result: Any = None
    provenance: Dict[str, Any] = field(default_factory=dict)

    warnings: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)


# ============================================================
# RECONCILIATION RESULT
# ============================================================

@dataclass
class D13EvidenceReconciliation:
    status: D13ReconciliationStatus

    market_id: Optional[str]
    as_of: Optional[Any]

    evidence: List[D13EvidenceRecord] = field(default_factory=list)

    supporting_evidence: List[str] = field(default_factory=list)
    conflicting_evidence: List[str] = field(default_factory=list)

    conflicts: List[Dict[str, Any]] = field(default_factory=list)

    upstream_statuses: Dict[str, str] = field(default_factory=dict)

    provenance_valid: bool = True
    temporal_valid: bool = True
    authority_valid: bool = True

    warnings: List[str] = field(default_factory=list)

    ready_for_d13: bool = False


# ============================================================
# GENERIC HELPERS
# ============================================================

def _d13_p2_clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _d13_p2_upper(value: Any) -> str:
    return _d13_p2_clean(value).upper()


def _d13_p2_get(obj: Any, name: str, default: Any = None) -> Any:
    if obj is None:
        return default

    if isinstance(obj, dict):
        return obj.get(name, default)

    return getattr(obj, name, default)


def _d13_p2_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    if value is None:
        return False

    return _d13_p2_upper(value) in {
        "TRUE",
        "1",
        "YES",
        "VALID",
        "READY",
    }


def _d13_p2_timestamp(value: Any) -> Optional[datetime]:
    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(value)
        except Exception:
            return None

    if isinstance(value, str):
        text = value.strip()

        if not text:
            return None

        try:
            return datetime.fromisoformat(
                text.replace("Z", "+00:00")
            )
        except Exception:
            return None

    return None


# ============================================================
# PROVENANCE VALIDATION
# ============================================================

def validate_d13_provenance(
    provenance: Any,
) -> Tuple[bool, List[str]]:
    """
    D13 requires traceable provenance.

    No provenance means evidence cannot be treated as fully
    authoritative evidence.

    This function does not fabricate missing provenance.
    """

    warnings: List[str] = []

    if not isinstance(provenance, dict):
        return False, ["PROVENANCE_NOT_MAPPING"]

    source = provenance.get("source")
    engine = provenance.get("engine")
    version = provenance.get("version")

    if not source and not engine:
        warnings.append("PROVENANCE_SOURCE_MISSING")

    if engine and not version:
        warnings.append("PROVENANCE_VERSION_MISSING")

    required_trace_fields = (
        "source",
        "engine",
        "version",
        "generated_at",
    )

    present = sum(
        1
        for field_name in required_trace_fields
        if provenance.get(field_name) not in (None, "")
    )

    # IMPORTANT:
    # This is not an evidence-quality score.
    # It only checks whether a provenance contract is structurally
    # traceable enough for audit purposes.
    valid = present > 0 and not (
        engine and not version
    )

    return valid, warnings


# ============================================================
# TEMPORAL VALIDATION
# ============================================================

def validate_d13_temporal_alignment(
    target_as_of: Any,
    evidence_as_of: Any,
) -> Tuple[bool, str]:
    """
    Evidence must be temporally compatible with the D13
    evaluation point.

    Future evidence is never accepted.
    """

    target = _d13_p2_timestamp(target_as_of)
    evidence = _d13_p2_timestamp(evidence_as_of)

    if target is None or evidence is None:
        return False, "TIMESTAMP_UNRESOLVED"

    if evidence > target:
        return False, "FUTURE_EVIDENCE_BLOCKED"

    return True, ""


# ============================================================
# UPSTREAM STATUS EXTRACTION
# ============================================================

def extract_d13_upstream_status(
    result: Any,
    engine_name: str,
) -> D13UpstreamAuthorityRecord:

    status = _d13_p2_upper(
        _d13_p2_get(result, "status", "UNDETERMINED")
    )

    authority = _d13_p2_bool(
        _d13_p2_get(result, "authority", True)
    )

    decision_performed = _d13_p2_bool(
        _d13_p2_get(result, "decision_performed", False)
    )

    execution_authority = _d13_p2_bool(
        _d13_p2_get(result, "execution_authority", False)
    )

    market_id = _d13_p2_get(result, "market_id")
    as_of = _d13_p2_get(result, "as_of")

    provenance = _d13_p2_get(
        result,
        "provenance",
        {},
    )

    warnings = list(
        _d13_p2_get(
            result,
            "warnings",
            [],
        ) or []
    )

    conflicts = list(
        _d13_p2_get(
            result,
            "conflicts",
            [],
        ) or []
    )

    return D13UpstreamAuthorityRecord(
        engine=engine_name,
        status=status,
        authority=authority,
        decision_performed=decision_performed,
        execution_authority=execution_authority,
        market_id=market_id,
        as_of=as_of,
        result=result,
        provenance=provenance,
        warnings=warnings,
        conflicts=conflicts,
    )


# ============================================================
# AUTHORITY BOUNDARY VALIDATION
# ============================================================

def validate_d13_upstream_authority(
    record: D13UpstreamAuthorityRecord,
) -> Tuple[bool, List[str]]:

    problems: List[str] = []

    if not record.authority:
        problems.append(
            f"{record.engine}:AUTHORITY_FALSE"
        )

    if record.execution_authority:
        problems.append(
            f"{record.engine}:EXECUTION_AUTHORITY_FORBIDDEN"
        )

    if record.decision_performed:
        problems.append(
            f"{record.engine}:UNEXPECTED_DECISION_AUTHORITY"
        )

    return len(problems) == 0, problems


# ============================================================
# EVIDENCE RECONCILER
# ============================================================

class D13EvidenceReconciler:
    """
    D13 Evidence Reconciliation Layer.

    Responsibilities:
        - preserve provenance
        - validate temporal ordering
        - detect conflicts
        - validate upstream authority boundaries
        - classify evidence disposition

    It does NOT:
        - create BUY/SELL
        - create execution instructions
        - invent confidence
        - create probability
        - replace D10/D11/D12 authority
    """

    def __init__(self) -> None:
        self._history: List[D13EvidenceReconciliation] = []

    # --------------------------------------------------------
    # NORMALIZE EVIDENCE
    # --------------------------------------------------------

    def normalize_evidence(
        self,
        evidence: Sequence[Any],
        target_as_of: Any = None,
    ) -> List[D13EvidenceRecord]:

        normalized: List[D13EvidenceRecord] = []

        for index, item in enumerate(evidence or []):

            if isinstance(item, D13EvidenceRecord):
                record = item
            else:
                evidence_id = _d13_p2_clean(
                    _d13_p2_get(
                        item,
                        "evidence_id",
                        f"D13-EVID-{index + 1}",
                    )
                )

                source = _d13_p2_clean(
                    _d13_p2_get(
                        item,
                        "source",
                        _d13_p2_get(
                            item,
                            "engine",
                            "UNKNOWN",
                        ),
                    )
                )

                dimension = _d13_p2_clean(
                    _d13_p2_get(
                        item,
                        "dimension",
                        "UNKNOWN",
                    )
                )

                record = D13EvidenceRecord(
                    evidence_id=evidence_id,
                    source=source,
                    dimension=dimension,
                    value=_d13_p2_get(item, "value"),
                    observed_at=_d13_p2_get(
                        item,
                        "observed_at",
                    ),
                    as_of=_d13_p2_get(
                        item,
                        "as_of",
                        target_as_of,
                    ),
                    provenance=_d13_p2_get(
                        item,
                        "provenance",
                        {},
                    ) or {},
                    metadata=_d13_p2_get(
                        item,
                        "metadata",
                        {},
                    ) or {},
                )

            provenance_ok, provenance_warnings = (
                validate_d13_provenance(
                    record.provenance
                )
            )

            if not provenance_ok:
                record.validity = False
                record.disposition = (
                    D13EvidenceDisposition.INVALID
                )
                record.reason = ";".join(
                    provenance_warnings
                )

            if target_as_of is not None and record.as_of is not None:
                temporal_ok, temporal_reason = (
                    validate_d13_temporal_alignment(
                        target_as_of,
                        record.as_of,
                    )
                )

                if not temporal_ok:
                    record.validity = False
                    record.disposition = (
                        D13EvidenceDisposition.INVALID
                    )
                    record.reason = temporal_reason

            normalized.append(record)

        return normalized

    # --------------------------------------------------------
    # CONFLICT DETECTION
    # --------------------------------------------------------

    def detect_conflicts(
        self,
        evidence: Sequence[D13EvidenceRecord],
    ) -> List[Dict[str, Any]]:

        conflicts: List[Dict[str, Any]] = []

        valid = [
            item
            for item in evidence
            if item.validity
        ]

        # Same dimension + incompatible explicit values.
        by_dimension: Dict[str, List[D13EvidenceRecord]] = {}

        for item in valid:
            key = _d13_p2_upper(item.dimension)

            by_dimension.setdefault(
                key,
                [],
            ).append(item)

        for dimension, items in by_dimension.items():

            values = [
                _d13_p2_upper(item.value)
                for item in items
                if item.value not in (None, "")
            ]

            unique_values = set(values)

            if len(unique_values) <= 1:
                continue

            direction_values = {
                "BULLISH",
                "BEARISH",
            }

            if unique_values.issubset(direction_values):
                conflicts.append(
                    {
                        "type": D13ConflictType.DIRECTION_CONFLICT.value,
                        "dimension": dimension,
                        "values": sorted(unique_values),
                        "evidence_ids": [
                            item.evidence_id
                            for item in items
                        ],
                    }
                )
            else:
                conflicts.append(
                    {
                        "type": D13ConflictType.UNKNOWN_CONFLICT.value,
                        "dimension": dimension,
                        "values": sorted(unique_values),
                        "evidence_ids": [
                            item.evidence_id
                            for item in items
                        ],
                    }
                )

        return conflicts

    # --------------------------------------------------------
    # CLASSIFY SUPPORT / CONFLICT
    # --------------------------------------------------------

    def classify_evidence(
        self,
        evidence: Sequence[D13EvidenceRecord],
        expected_direction: Optional[str] = None,
    ) -> None:

        expected = _d13_p2_upper(
            expected_direction
        )

        for item in evidence:

            if not item.validity:
                item.disposition = (
                    D13EvidenceDisposition.INVALID
                )
                continue

            value = _d13_p2_upper(item.value)

            if not expected:
                item.disposition = (
                    D13EvidenceDisposition.NEUTRAL
                )
                continue

            if value == expected:
                item.disposition = (
                    D13EvidenceDisposition.SUPPORTING
                )

            elif value in {
                "BULLISH",
                "BEARISH",
            }:
                item.disposition = (
                    D13EvidenceDisposition.CONFLICTING
                )

            else:
                item.disposition = (
                    D13EvidenceDisposition.NEUTRAL
                )

    # --------------------------------------------------------
    # MAIN RECONCILIATION
    # --------------------------------------------------------

    def reconcile(
        self,
        market_id: Optional[str],
        as_of: Any,
        evidence: Sequence[Any],
        upstream_results: Optional[
            Dict[str, Any]
        ] = None,
        expected_direction: Optional[str] = None,
    ) -> D13EvidenceReconciliation:

        normalized = self.normalize_evidence(
            evidence,
            target_as_of=as_of,
        )

        self.classify_evidence(
            normalized,
            expected_direction=expected_direction,
        )

        conflicts = self.detect_conflicts(
            normalized
        )

        upstream_results = upstream_results or {}

        upstream_records: Dict[
            str,
            D13UpstreamAuthorityRecord,
        ] = {}

        upstream_statuses: Dict[str, str] = {}

        warnings: List[str] = []

        provenance_valid = True
        temporal_valid = True
        authority_valid = True

        for engine_name, result in upstream_results.items():

            record = extract_d13_upstream_status(
                result,
                engine_name,
            )

            upstream_records[
                engine_name
            ] = record

            upstream_statuses[
                engine_name
            ] = record.status

            authority_ok, authority_problems = (
                validate_d13_upstream_authority(
                    record
                )
            )

            if not authority_ok:
                authority_valid = False
                warnings.extend(
                    authority_problems
                )

            provenance_ok, provenance_warnings = (
                validate_d13_provenance(
                    record.provenance
                )
            )

            if not provenance_ok:
                provenance_valid = False

            warnings.extend(
                provenance_warnings
            )

            for upstream_warning in record.warnings:
                warnings.append(
                    f"{engine_name}:{upstream_warning}"
                )

            for upstream_conflict in record.conflicts:
                warnings.append(
                    f"{engine_name}:{upstream_conflict}"
                )

        for item in normalized:

            if not item.validity:
                if "FUTURE_EVIDENCE_BLOCKED" in item.reason:
                    temporal_valid = False

                if "PROVENANCE" in item.reason:
                    provenance_valid = False

        supporting = [
            item.evidence_id
            for item in normalized
            if item.disposition
            == D13EvidenceDisposition.SUPPORTING
        ]

        conflicting = [
            item.evidence_id
            for item in normalized
            if item.disposition
            == D13EvidenceDisposition.CONFLICTING
        ]

        blocking_upstream = any(
            status == "BLOCKED"
            for status in upstream_statuses.values()
        )

        limited_upstream = any(
            status == "LIMITED"
            for status in upstream_statuses.values()
        )

        if not authority_valid:
            status = D13ReconciliationStatus.BLOCKED

        elif not temporal_valid:
            status = D13ReconciliationStatus.BLOCKED

        elif blocking_upstream:
            status = D13ReconciliationStatus.BLOCKED

        elif conflicts:
            status = D13ReconciliationStatus.LIMITED

        elif limited_upstream:
            status = D13ReconciliationStatus.LIMITED

        elif not normalized:
            status = D13ReconciliationStatus.UNDETERMINED

        elif not provenance_valid:
            status = D13ReconciliationStatus.LIMITED

        else:
            status = D13ReconciliationStatus.READY

        ready_for_d13 = (
            status
            == D13ReconciliationStatus.READY
            and authority_valid
            and temporal_valid
            and provenance_valid
        )

        result = D13EvidenceReconciliation(
            status=status,
            market_id=market_id,
            as_of=as_of,
            evidence=normalized,
            supporting_evidence=supporting,
            conflicting_evidence=conflicting,
            conflicts=conflicts,
            upstream_statuses=upstream_statuses,
            provenance_valid=provenance_valid,
            temporal_valid=temporal_valid,
            authority_valid=authority_valid,
            warnings=warnings,
            ready_for_d13=ready_for_d13,
        )

        self._history.append(result)

        return result

    # --------------------------------------------------------
    # HISTORY
    # --------------------------------------------------------

    def history(self) -> List[D13EvidenceReconciliation]:
        return list(self._history)

    def latest(self) -> Optional[D13EvidenceReconciliation]:
        if not self._history:
            return None

        return self._history[-1]


# ============================================================
# D10 / D11 / D12 RECONCILIATION BRIDGE
# ============================================================

def d13_reconcile_upstream(
    market_id: Optional[str],
    as_of: Any,
    evidence: Sequence[Any],
    d10_result: Any = None,
    d11_result: Any = None,
    d12_result: Any = None,
    expected_direction: Optional[str] = None,
) -> D13EvidenceReconciliation:

    upstream: Dict[str, Any] = {}

    if d10_result is not None:
        upstream[
            "D10_MarketState"
        ] = d10_result

    if d11_result is not None:
        upstream[
            "D11_DecisionTransition"
        ] = d11_result

    if d12_result is not None:
        upstream[
            "D12_FutureScenario"
        ] = d12_result

    reconciler = D13EvidenceReconciler()

    return reconciler.reconcile(
        market_id=market_id,
        as_of=as_of,
        evidence=evidence,
        upstream_results=upstream,
        expected_direction=expected_direction,
    )


# ============================================================
# D13 EVIDENCE GATE
# ============================================================

def d13_evidence_gate(
    reconciliation: Optional[D13EvidenceReconciliation],
) -> Tuple[bool, List[str]]:

    if reconciliation is None:
        return False, [
            "D13_RECONCILIATION_MISSING"
        ]

    reasons: List[str] = []

    if reconciliation.status == (
        D13ReconciliationStatus.BLOCKED
    ):
        reasons.append(
            "D13_RECONCILIATION_BLOCKED"
        )

    if not reconciliation.provenance_valid:
        reasons.append(
            "D13_PROVENANCE_INVALID"
        )

    if not reconciliation.temporal_valid:
        reasons.append(
            "D13_TEMPORAL_INVALID"
        )

    if not reconciliation.authority_valid:
        reasons.append(
            "D13_UPSTREAM_AUTHORITY_INVALID"
        )

    if reconciliation.conflicts:
        reasons.append(
            "D13_EVIDENCE_CONFLICT_PRESENT"
        )

    return (
        reconciliation.ready_for_d13,
        reasons,
    )


# ============================================================
# ATTACH RECONCILIATION TO D13 INPUT
# ============================================================

def attach_d13_reconciliation(
    d13_input: Any,
    reconciliation: D13EvidenceReconciliation,
) -> Any:

    if d13_input is None:
        return d13_input

    if hasattr(d13_input, "reconciliation"):
        try:
            setattr(
                d13_input,
                "reconciliation",
                reconciliation,
            )
        except Exception:
            pass

    if hasattr(d13_input, "warnings"):
        try:
            existing = list(
                getattr(
                    d13_input,
                    "warnings",
                    [],
                ) or []
            )

            existing.extend(
                reconciliation.warnings
            )

            setattr(
                d13_input,
                "warnings",
                existing,
            )
        except Exception:
            pass

    return d13_input


# ============================================================
# PART-2 CONTRACT
# ============================================================

def d13_reconciliation_contract(
    reconciliation: D13EvidenceReconciliation,
) -> Dict[str, Any]:

    return {
        "engine": D13_PART2_NAME,
        "version": D13_PART2_VERSION,
        "status": reconciliation.status.value,
        "market_id": reconciliation.market_id,
        "as_of": reconciliation.as_of,

        "supporting_evidence": list(
            reconciliation.supporting_evidence
        ),

        "conflicting_evidence": list(
            reconciliation.conflicting_evidence
        ),

        "conflicts": list(
            reconciliation.conflicts
        ),

        "upstream_statuses": dict(
            reconciliation.upstream_statuses
        ),

        "provenance_valid": (
            reconciliation.provenance_valid
        ),

        "temporal_valid": (
            reconciliation.temporal_valid
        ),

        "authority_valid": (
            reconciliation.authority_valid
        ),

        "ready_for_d13": (
            reconciliation.ready_for_d13
        ),

        "warnings": list(
            reconciliation.warnings
        ),

        "decision_authority": False,
        "execution_authority": False,
    }


# ============================================================
# PART-2 SELF TEST
# ============================================================

def d13_part2_self_check() -> Dict[str, bool]:

    test_as_of = datetime(
        2026,
        1,
        1,
        10,
        0,
        0,
    )

    evidence = [
        D13EvidenceRecord(
            evidence_id="E1",
            source="D10",
            dimension="STATE",
            value="BULLISH",
            as_of=test_as_of,
            provenance={
                "source": "D10",
                "engine": "D10_MarketState",
                "version": "V6-CAS-1.0",
                "generated_at": test_as_of.isoformat(),
            },
        )
    ]

    d10_result = {
        "status": "READY",
        "market_id": "TEST",
        "as_of": test_as_of,
        "authority": True,
        "decision_performed": False,
        "execution_authority": False,
        "provenance": {
            "source": "D10",
            "engine": "D10_MarketState",
            "version": "V6-CAS-1.0",
            "generated_at": test_as_of.isoformat(),
        },
    }

    reconciler = D13EvidenceReconciler()

    result = reconciler.reconcile(
        market_id="TEST",
        as_of=test_as_of,
        evidence=evidence,
        upstream_results={
            "D10_MarketState": d10_result,
        },
        expected_direction="BULLISH",
    )

    gate, gate_reasons = d13_evidence_gate(
        result
    )

    future_ok, future_reason = (
        validate_d13_temporal_alignment(
            test_as_of,
            datetime(
                2026,
                1,
                1,
                11,
                0,
                0,
            ),
        )
    )

    authority_record = extract_d13_upstream_status(
        d10_result,
        "D10_MarketState",
    )

    authority_ok, authority_problems = (
        validate_d13_upstream_authority(
            authority_record
        )
    )

    contract = d13_reconciliation_contract(
        result
    )

    return {
        "reconciliation_created": (
            result is not None
        ),

        "ready_status": (
            result.status
            == D13ReconciliationStatus.READY
        ),

        "supporting_evidence_detected": (
            "E1"
            in result.supporting_evidence
        ),

        "authority_valid": (
            authority_ok
            and not authority_problems
        ),

        "gate_open": (
            gate
            and not gate_reasons
        ),

        "future_evidence_blocked": (
            not future_ok
            and future_reason
            == "FUTURE_EVIDENCE_BLOCKED"
        ),

        "contract_no_decision": (
            contract["decision_authority"]
            is False
        ),

        "contract_no_execution": (
            contract["execution_authority"]
            is False
        ),
    }


# ============================================================
# FACTORY
# ============================================================

def create_d13_evidence_reconciler() -> (
    D13EvidenceReconciler
):
    return D13EvidenceReconciler()


# ============================================================
# EXPORTS
# ============================================================

D13_PART2_EXPORTS = (
    "D13ReconciliationStatus",
    "D13EvidenceDisposition",
    "D13ConflictType",
    "D13EvidenceRecord",
    "D13UpstreamAuthorityRecord",
    "D13EvidenceReconciliation",
    "D13EvidenceReconciler",
    "validate_d13_provenance",
    "validate_d13_temporal_alignment",
    "extract_d13_upstream_status",
    "validate_d13_upstream_authority",
    "d13_reconcile_upstream",
    "d13_evidence_gate",
    "attach_d13_reconciliation",
    "d13_reconciliation_contract",
    "d13_part2_self_check",
    "create_d13_evidence_reconciler",
)


# ============================================================
# DIRECT PART-2 TEST
# ============================================================

if __name__ == "__main__":
    try:
        result = d13_part2_self_check()

        print(
            "D13 PART-2 SELF-TEST:",
            "PASS"
            if all(result.values())
            else "FAIL",
        )

        for key, value in result.items():
            print(
                f"  {key}: {value}"
            )

    except Exception as exc:
        print(
            "D13 PART-2 SELF-TEST: ERROR"
        )
        print(
            f"{type(exc).__name__}: {exc}"
        )
# ============================================================
# D13 DECISION AUTHORITY
# PART 3 / 4
# MTF + SCENARIO + TEMPORAL + RISK/VALIDATION READINESS
# ============================================================

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple
from datetime import datetime


# ============================================================
# PART-3 CONSTANTS
# ============================================================

D13_PART3_NAME = "D13_ContextAndReadiness"
D13_PART3_VERSION = "V6-CAS-1.0"

D13_TIMEFRAME_RANK = {
    "TICK": 1,
    "1M": 2,
    "3M": 3,
    "5M": 4,
    "10M": 5,
    "15M": 6,
    "30M": 7,
    "1H": 8,
    "2H": 9,
    "4H": 10,
    "6H": 11,
    "12H": 12,
    "1D": 13,
    "1W": 14,
    "1MO": 15,
}


# ============================================================
# ENUMS
# ============================================================

class D13MTFStatus(str, Enum):
    ALIGNED = "ALIGNED"
    PARTIAL = "PARTIAL"
    CONFLICT = "CONFLICT"
    UNDETERMINED = "UNDETERMINED"


class D13ScenarioStatus(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONFLICT = "CONFLICT"
    INCOMPLETE = "INCOMPLETE"
    UNDETERMINED = "UNDETERMINED"


class D13TemporalStatus(str, Enum):
    VALID = "VALID"
    STALE = "STALE"
    FUTURE_DATA = "FUTURE_DATA"
    INVALID = "INVALID"
    UNDETERMINED = "UNDETERMINED"


class D13ReadinessStatus(str, Enum):
    READY = "READY"
    LIMITED = "LIMITED"
    BLOCKED = "BLOCKED"
    UNDETERMINED = "UNDETERMINED"


# ============================================================
# MTF RECORD
# ============================================================

@dataclass
class D13MTFRecord:
    timeframe: str
    state: Optional[str] = None
    transition: Optional[str] = None
    direction: Optional[str] = None

    as_of: Optional[Any] = None
    provenance: Dict[str, Any] = field(default_factory=dict)

    valid: bool = True
    warnings: List[str] = field(default_factory=list)


# ============================================================
# MTF RECONCILIATION
# ============================================================

@dataclass
class D13MTFReconciliation:
    status: D13MTFStatus

    records: List[D13MTFRecord] = field(default_factory=list)

    higher_timeframe_direction: Optional[str] = None
    lower_timeframe_direction: Optional[str] = None

    aligned_timeframes: List[str] = field(
        default_factory=list
    )

    conflicting_timeframes: List[str] = field(
        default_factory=list
    )

    conflicts: List[Dict[str, Any]] = field(
        default_factory=list
    )

    temporal_valid: bool = True

    warnings: List[str] = field(
        default_factory=list
    )


# ============================================================
# SCENARIO RECORD
# ============================================================

@dataclass
class D13ScenarioRecord:
    scenario_id: str
    scenario_type: Optional[str] = None
    horizon: Optional[str] = None
    role: Optional[str] = None

    direction: Optional[str] = None

    trigger: Any = None
    invalidation: Any = None

    evidence_ids: List[str] = field(
        default_factory=list
    )

    probability: Any = None

    as_of: Optional[Any] = None

    provenance: Dict[str, Any] = field(
        default_factory=dict
    )

    valid: bool = True
    warnings: List[str] = field(
        default_factory=list
    )


# ============================================================
# SCENARIO RECONCILIATION
# ============================================================

@dataclass
class D13ScenarioReconciliation:
    status: D13ScenarioStatus

    scenarios: List[D13ScenarioRecord] = field(
        default_factory=list
    )

    primary_scenario_id: Optional[str] = None

    compatible_scenarios: List[str] = field(
        default_factory=list
    )

    conflicting_scenarios: List[str] = field(
        default_factory=list
    )

    conflicts: List[Dict[str, Any]] = field(
        default_factory=list
    )

    future_data_blocked: bool = False

    warnings: List[str] = field(
        default_factory=list
    )


# ============================================================
# TEMPORAL VALIDATION RESULT
# ============================================================

@dataclass
class D13TemporalValidation:
    status: D13TemporalStatus

    target_as_of: Optional[Any]

    latest_valid_timestamp: Optional[Any] = None

    invalid_items: List[str] = field(
        default_factory=list
    )

    future_items: List[str] = field(
        default_factory=list
    )

    stale_items: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )


# ============================================================
# RISK READINESS
# ============================================================

@dataclass
class D13RiskReadiness:
    status: D13ReadinessStatus

    risk_available: bool = False
    risk_valid: bool = False

    risk_dimensions: Dict[str, Any] = field(
        default_factory=dict
    )

    blockers: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )


# ============================================================
# VALIDATION READINESS
# ============================================================

@dataclass
class D13ValidationReadiness:
    status: D13ReadinessStatus

    validation_available: bool = False
    validation_valid: bool = False

    validation_dimensions: Dict[str, Any] = field(
        default_factory=dict
    )

    blockers: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )


# ============================================================
# CONTEXT READINESS
# ============================================================

@dataclass
class D13ContextReadiness:
    status: D13ReadinessStatus

    mtf: Optional[D13MTFReconciliation] = None
    scenarios: Optional[D13ScenarioReconciliation] = None
    temporal: Optional[D13TemporalValidation] = None
    risk: Optional[D13RiskReadiness] = None
    validation: Optional[D13ValidationReadiness] = None

    blockers: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    ready_for_authority: bool = False


# ============================================================
# GENERIC HELPERS
# ============================================================

def _d13_p3_clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _d13_p3_upper(value: Any) -> str:
    return _d13_p3_clean(value).upper()


def _d13_p3_get(
    obj: Any,
    name: str,
    default: Any = None,
) -> Any:

    if obj is None:
        return default

    if isinstance(obj, dict):
        return obj.get(name, default)

    return getattr(obj, name, default)


def _d13_p3_timestamp(
    value: Any,
) -> Optional[datetime]:

    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(value)
        except Exception:
            return None

    if isinstance(value, str):
        text = value.strip()

        if not text:
            return None

        try:
            return datetime.fromisoformat(
                text.replace("Z", "+00:00")
            )
        except Exception:
            return None

    return None


def _d13_p3_bool(value: Any) -> bool:

    if isinstance(value, bool):
        return value

    if value is None:
        return False

    return _d13_p3_upper(value) in {
        "TRUE",
        "1",
        "YES",
        "VALID",
        "READY",
    }


# ============================================================
# TIMEFRAME NORMALIZATION
# ============================================================

def normalize_d13_timeframe(
    timeframe: Any,
) -> str:

    value = _d13_p3_upper(timeframe)

    aliases = {
        "MIN": "1M",
        "1MIN": "1M",
        "3MIN": "3M",
        "5MIN": "5M",
        "10MIN": "10M",
        "15MIN": "15M",
        "30MIN": "30M",
        "60M": "1H",
        "60MIN": "1H",
        "1HR": "1H",
        "H1": "1H",
        "H4": "4H",
        "D1": "1D",
        "W1": "1W",
        "MONTHLY": "1MO",
    }

    return aliases.get(
        value,
        value,
    )


# ============================================================
# MTF RECONCILER
# ============================================================

class D13MTFReconciler:

    def reconcile(
        self,
        records: Sequence[Any],
        target_as_of: Any = None,
    ) -> D13MTFReconciliation:

        normalized: List[D13MTFRecord] = []
        warnings: List[str] = []

        for index, item in enumerate(
            records or []
        ):

            timeframe = normalize_d13_timeframe(
                _d13_p3_get(
                    item,
                    "timeframe",
                    "",
                )
            )

            record = D13MTFRecord(
                timeframe=timeframe,
                state=_d13_p3_get(
                    item,
                    "state",
                ),
                transition=_d13_p3_get(
                    item,
                    "transition",
                ),
                direction=_d13_p3_get(
                    item,
                    "direction",
                ),
                as_of=_d13_p3_get(
                    item,
                    "as_of",
                ),
                provenance=_d13_p3_get(
                    item,
                    "provenance",
                    {},
                ) or {},
            )

            if timeframe not in D13_TIMEFRAME_RANK:
                record.valid = False
                record.warnings.append(
                    "UNKNOWN_TIMEFRAME"
                )

            if target_as_of is not None:
                target = _d13_p3_timestamp(
                    target_as_of
                )
                timestamp = _d13_p3_timestamp(
                    record.as_of
                )

                if target and timestamp:
                    if timestamp > target:
                        record.valid = False
                        record.warnings.append(
                            "FUTURE_DATA_BLOCKED"
                        )

            normalized.append(record)

        valid_records = [
            item
            for item in normalized
            if item.valid
        ]

        valid_records.sort(
            key=lambda item: D13_TIMEFRAME_RANK.get(
                item.timeframe,
                999,
            )
        )

        conflicts: List[Dict[str, Any]] = []

        aligned: List[str] = []
        conflicting: List[str] = []

        directions = [
            _d13_p3_upper(
                item.direction
            )
            for item in valid_records
            if item.direction
        ]

        unique_directions = {
            value
            for value in directions
            if value
        }

        if len(unique_directions) > 1:

            for item in valid_records:
                direction = _d13_p3_upper(
                    item.direction
                )

                if direction:
                    conflicting.append(
                        item.timeframe
                    )

            conflicts.append(
                {
                    "type": "MTF_DIRECTION_CONFLICT",
                    "directions": sorted(
                        unique_directions
                    ),
                    "timeframes": conflicting,
                }
            )

        elif len(unique_directions) == 1:

            direction = next(
                iter(unique_directions)
            )

            for item in valid_records:
                if _d13_p3_upper(
                    item.direction
                ) == direction:
                    aligned.append(
                        item.timeframe
                    )

        higher_direction = None
        lower_direction = None

        if valid_records:

            higher_candidates = [
                item
                for item in valid_records
                if D13_TIMEFRAME_RANK.get(
                    item.timeframe,
                    0,
                ) >= 8
            ]

            lower_candidates = [
                item
                for item in valid_records
                if D13_TIMEFRAME_RANK.get(
                    item.timeframe,
                    0,
                ) < 8
            ]

            if higher_candidates:
                higher_direction = _d13_p3_upper(
                    higher_candidates[-1].direction
                ) or None

            if lower_candidates:
                lower_direction = _d13_p3_upper(
                    lower_candidates[-1].direction
                ) or None

        temporal_valid = not any(
            "FUTURE_DATA_BLOCKED"
            in item.warnings
            for item in normalized
        )

        if not valid_records:
            status = D13MTFStatus.UNDETERMINED

        elif not temporal_valid:
            status = D13MTFStatus.CONFLICT

        elif conflicts:
            status = D13MTFStatus.CONFLICT

        elif len(aligned) == len(valid_records):
            status = D13MTFStatus.ALIGNED

        else:
            status = D13MTFStatus.PARTIAL

        for item in normalized:
            warnings.extend(
                item.warnings
            )

        return D13MTFReconciliation(
            status=status,
            records=normalized,
            higher_timeframe_direction=higher_direction,
            lower_timeframe_direction=lower_direction,
            aligned_timeframes=aligned,
            conflicting_timeframes=conflicting,
            conflicts=conflicts,
            temporal_valid=temporal_valid,
            warnings=warnings,
        )


# ============================================================
# SCENARIO RECONCILER
# ============================================================

class D13ScenarioReconciler:

    def normalize(
        self,
        scenarios: Sequence[Any],
    ) -> List[D13ScenarioRecord]:

        result: List[D13ScenarioRecord] = []

        for index, item in enumerate(
            scenarios or []
        ):

            scenario_id = _d13_p3_clean(
                _d13_p3_get(
                    item,
                    "scenario_id",
                    f"D12-SCENARIO-{index + 1}",
                )
            )

            record = D13ScenarioRecord(
                scenario_id=scenario_id,
                scenario_type=_d13_p3_get(
                    item,
                    "scenario_type",
                ),
                horizon=_d13_p3_get(
                    item,
                    "horizon",
                ),
                role=_d13_p3_get(
                    item,
                    "role",
                ),
                direction=_d13_p3_get(
                    item,
                    "direction",
                ),
                trigger=_d13_p3_get(
                    item,
                    "trigger",
                ),
                invalidation=_d13_p3_get(
                    item,
                    "invalidation",
                ),
                evidence_ids=list(
                    _d13_p3_get(
                        item,
                        "evidence_ids",
                        [],
                    ) or []
                ),
                probability=_d13_p3_get(
                    item,
                    "probability",
                ),
                as_of=_d13_p3_get(
                    item,
                    "as_of",
                ),
                provenance=_d13_p3_get(
                    item,
                    "provenance",
                    {},
                ) or {},
            )

            result.append(record)

        return result

    def reconcile(
        self,
        scenarios: Sequence[Any],
        target_as_of: Any = None,
    ) -> D13ScenarioReconciliation:

        normalized = self.normalize(
            scenarios
        )

        conflicts: List[Dict[str, Any]] = []
        warnings: List[str] = []

        future_blocked = False

        valid = []

        for scenario in normalized:

            if target_as_of is not None:
                target = _d13_p3_timestamp(
                    target_as_of
                )
                timestamp = _d13_p3_timestamp(
                    scenario.as_of
                )

                if target and timestamp:
                    if timestamp > target:
                        scenario.valid = False
                        future_blocked = True
                        scenario.warnings.append(
                            "FUTURE_SCENARIO_BLOCKED"
                        )

            if scenario.valid:
                valid.append(scenario)

            warnings.extend(
                scenario.warnings
            )

        directions = {
            _d13_p3_upper(
                scenario.direction
            )
            for scenario in valid
            if scenario.direction
        }

        directions.discard("")

        if len(directions) > 1:

            conflicts.append(
                {
                    "type": "SCENARIO_DIRECTION_CONFLICT",
                    "directions": sorted(
                        directions
                    ),
                    "scenario_ids": [
                        scenario.scenario_id
                        for scenario in valid
                    ],
                }
            )

        primary_candidates = [
            scenario
            for scenario in valid
            if _d13_p3_upper(
                scenario.role
            ) == "PRIMARY"
        ]

        primary_id = (
            primary_candidates[0].scenario_id
            if primary_candidates
            else None
        )

        compatible = []
        conflicting = []

        primary_direction = None

        if primary_candidates:
            primary_direction = _d13_p3_upper(
                primary_candidates[0].direction
            )

        for scenario in valid:

            direction = _d13_p3_upper(
                scenario.direction
            )

            if (
                primary_direction
                and direction
                and direction != primary_direction
            ):
                conflicting.append(
                    scenario.scenario_id
                )
            else:
                compatible.append(
                    scenario.scenario_id
                )

        # External probability is preserved as upstream data.
        # D13 does not calculate or fabricate probability.
        for scenario in normalized:

            if scenario.probability is not None:
                warnings.append(
                    f"{scenario.scenario_id}:"
                    "EXTERNAL_PROBABILITY_PRESERVED"
                )

        if not normalized:
            status = D13ScenarioStatus.UNDETERMINED

        elif future_blocked:
            status = D13ScenarioStatus.CONFLICT

        elif conflicts:
            status = D13ScenarioStatus.CONFLICT

        elif not primary_candidates:
            status = D13ScenarioStatus.INCOMPLETE

        else:
            status = D13ScenarioStatus.CONSISTENT

        return D13ScenarioReconciliation(
            status=status,
            scenarios=normalized,
            primary_scenario_id=primary_id,
            compatible_scenarios=compatible,
            conflicting_scenarios=conflicting,
            conflicts=conflicts,
            future_data_blocked=future_blocked,
            warnings=warnings,
        )


# ============================================================
# TEMPORAL VALIDATOR
# ============================================================

class D13TemporalValidator:

    def validate(
        self,
        target_as_of: Any,
        items: Sequence[Any],
    ) -> D13TemporalValidation:

        target = _d13_p3_timestamp(
            target_as_of
        )

        if target is None:
            return D13TemporalValidation(
                status=D13TemporalStatus.UNDETERMINED,
                target_as_of=target_as_of,
                warnings=[
                    "TARGET_TIMESTAMP_UNRESOLVED"
                ],
            )

        invalid_items: List[str] = []
        future_items: List[str] = []
        stale_items: List[str] = []

        latest_valid = None

        for index, item in enumerate(
            items or []
        ):

            item_id = _d13_p3_clean(
                _d13_p3_get(
                    item,
                    "evidence_id",
                    _d13_p3_get(
                        item,
                        "scenario_id",
                        _d13_p3_get(
                            item,
                            "timeframe",
                            f"ITEM-{index + 1}",
                        ),
                    ),
                )
            )

            timestamp = _d13_p3_timestamp(
                _d13_p3_get(
                    item,
                    "as_of",
                )
            )

            if timestamp is None:
                invalid_items.append(
                    item_id
                )
                continue

            if timestamp > target:
                future_items.append(
                    item_id
                )
                continue

            if (
                latest_valid is None
                or timestamp > latest_valid
            ):
                latest_valid = timestamp

        if future_items:
            status = D13TemporalStatus.FUTURE_DATA

        elif invalid_items and latest_valid is None:
            status = D13TemporalStatus.INVALID

        elif invalid_items:
            status = D13TemporalStatus.STALE

        else:
            status = D13TemporalStatus.VALID

        return D13TemporalValidation(
            status=status,
            target_as_of=target_as_of,
            latest_valid_timestamp=latest_valid,
            invalid_items=invalid_items,
            future_items=future_items,
            stale_items=stale_items,
        )


# ============================================================
# RISK READINESS
# ============================================================

def evaluate_d13_risk_readiness(
    risk_context: Any,
) -> D13RiskReadiness:

    if risk_context is None:
        return D13RiskReadiness(
            status=D13ReadinessStatus.UNDETERMINED,
            risk_available=False,
            risk_valid=False,
            blockers=[
                "RISK_CONTEXT_MISSING"
            ],
        )

    if isinstance(risk_context, dict):
        dimensions = dict(
            risk_context
        )
    else:
        dimensions = {
            key: getattr(
                risk_context,
                key,
            )
            for key in (
                "risk_state",
                "risk_level",
                "risk_density",
                "liquidity_risk",
                "volatility_risk",
                "drawdown_state",
            )
            if hasattr(
                risk_context,
                key,
            )
        }

    if not dimensions:
        return D13RiskReadiness(
            status=D13ReadinessStatus.LIMITED,
            risk_available=True,
            risk_valid=False,
            risk_dimensions={},
            blockers=[
                "RISK_DIMENSIONS_UNRESOLVED"
            ],
        )

    invalid = []

    for key, value in dimensions.items():

        if value is None:
            invalid.append(
                f"RISK_VALUE_MISSING:{key}"
            )

    if invalid:
        return D13RiskReadiness(
            status=D13ReadinessStatus.LIMITED,
            risk_available=True,
            risk_valid=False,
            risk_dimensions=dimensions,
            blockers=invalid,
        )

    return D13RiskReadiness(
        status=D13ReadinessStatus.READY,
        risk_available=True,
        risk_valid=True,
        risk_dimensions=dimensions,
    )


# ============================================================
# VALIDATION READINESS
# ============================================================

def evaluate_d13_validation_readiness(
    validation_context: Any,
) -> D13ValidationReadiness:

    if validation_context is None:
        return D13ValidationReadiness(
            status=D13ReadinessStatus.UNDETERMINED,
            validation_available=False,
            validation_valid=False,
            blockers=[
                "VALIDATION_CONTEXT_MISSING"
            ],
        )

    if isinstance(validation_context, dict):
        dimensions = dict(
            validation_context
        )
    else:
        dimensions = {
            key: getattr(
                validation_context,
                key,
            )
            for key in (
                "validation_state",
                "validated",
                "quality",
                "status",
                "gate",
            )
            if hasattr(
                validation_context,
                key,
            )
        }

    if not dimensions:
        return D13ValidationReadiness(
            status=D13ReadinessStatus.LIMITED,
            validation_available=True,
            validation_valid=False,
            blockers=[
                "VALIDATION_DIMENSIONS_UNRESOLVED"
            ],
        )

    # Explicit invalid/blocking states are respected.
    status_value = _d13_p3_upper(
        dimensions.get("status")
    )

    if status_value in {
        "BLOCKED",
        "INVALID",
        "FAILED",
    }:
        return D13ValidationReadiness(
            status=D13ReadinessStatus.BLOCKED,
            validation_available=True,
            validation_valid=False,
            validation_dimensions=dimensions,
            blockers=[
                "UPSTREAM_VALIDATION_BLOCKED"
            ],
        )

    explicit_valid = dimensions.get(
        "validated"
    )

    if explicit_valid is False:
        return D13ValidationReadiness(
            status=D13ReadinessStatus.LIMITED,
            validation_available=True,
            validation_valid=False,
            validation_dimensions=dimensions,
            blockers=[
                "VALIDATION_NOT_PASSED"
            ],
        )

    return D13ValidationReadiness(
        status=D13ReadinessStatus.READY,
        validation_available=True,
        validation_valid=True,
        validation_dimensions=dimensions,
    )


# ============================================================
# CONTEXT READINESS ENGINE
# ============================================================

class D13ContextReadinessEngine:

    def evaluate(
        self,
        mtf: Optional[D13MTFReconciliation],
        scenarios: Optional[
            D13ScenarioReconciliation
        ],
        temporal: Optional[
            D13TemporalValidation
        ],
        risk: Optional[D13RiskReadiness],
        validation: Optional[
            D13ValidationReadiness
        ],
    ) -> D13ContextReadiness:

        blockers: List[str] = []
        warnings: List[str] = []

        # ----------------------------------------------------
        # MTF
        # ----------------------------------------------------

        if mtf is None:
            blockers.append(
                "MTF_RECONCILIATION_MISSING"
            )

        elif mtf.status == D13MTFStatus.CONFLICT:
            warnings.append(
                "MTF_CONFLICT"
            )

        elif mtf.status == D13MTFStatus.UNDETERMINED:
            warnings.append(
                "MTF_UNDETERMINED"
            )

        # ----------------------------------------------------
        # SCENARIO
        # ----------------------------------------------------

        if scenarios is None:
            blockers.append(
                "SCENARIO_RECONCILIATION_MISSING"
            )

        elif scenarios.future_data_blocked:
            blockers.append(
                "FUTURE_SCENARIO_BLOCKED"
            )

        elif scenarios.status == (
            D13ScenarioStatus.CONFLICT
        ):
            warnings.append(
                "SCENARIO_CONFLICT"
            )

        # ----------------------------------------------------
        # TEMPORAL
        # ----------------------------------------------------

        if temporal is None:
            blockers.append(
                "TEMPORAL_VALIDATION_MISSING"
            )

        elif temporal.status == (
            D13TemporalStatus.FUTURE_DATA
        ):
            blockers.append(
                "FUTURE_DATA_BLOCKED"
            )

        elif temporal.status in {
            D13TemporalStatus.INVALID,
            D13TemporalStatus.UNDETERMINED,
        }:
            warnings.append(
                "TEMPORAL_VALIDITY_LIMITED"
            )

        # ----------------------------------------------------
        # RISK
        # ----------------------------------------------------

        if risk is None:
            blockers.append(
                "RISK_READINESS_MISSING"
            )

        elif risk.status == (
            D13ReadinessStatus.BLOCKED
        ):
            blockers.extend(
                risk.blockers
            )

        elif risk.status in {
            D13ReadinessStatus.LIMITED,
            D13ReadinessStatus.UNDETERMINED,
        }:
            warnings.extend(
                risk.blockers
            )

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if validation is None:
            blockers.append(
                "VALIDATION_READINESS_MISSING"
            )

        elif validation.status == (
            D13ReadinessStatus.BLOCKED
        ):
            blockers.extend(
                validation.blockers
            )

        elif validation.status in {
            D13ReadinessStatus.LIMITED,
            D13ReadinessStatus.UNDETERMINED,
        }:
            warnings.extend(
                validation.blockers
            )

        # ----------------------------------------------------
        # FINAL READINESS
        # ----------------------------------------------------

        if blockers:
            status = D13ReadinessStatus.BLOCKED
            ready = False

        elif warnings:
            status = D13ReadinessStatus.LIMITED
            ready = False

        else:
            status = D13ReadinessStatus.READY
            ready = True

        return D13ContextReadiness(
            status=status,
            mtf=mtf,
            scenarios=scenarios,
            temporal=temporal,
            risk=risk,
            validation=validation,
            blockers=blockers,
            warnings=warnings,
            ready_for_authority=ready,
        )


# ============================================================
# D13 DIRECTION RECONCILIATION
# ============================================================

def reconcile_d13_direction(
    market_state: Any,
    transition: Any,
    scenario_direction: Optional[str],
    mtf: Optional[D13MTFReconciliation],
) -> Tuple[
    Optional[str],
    List[Dict[str, Any]],
]:

    conflicts: List[Dict[str, Any]] = []

    state_direction = _d13_p3_upper(
        _d13_p3_get(
            market_state,
            "direction",
        )
    )

    if not state_direction:
        state_direction = _d13_p3_upper(
            _d13_p3_get(
                market_state,
                "market_direction",
            )
        )

    transition_direction = _d13_p3_upper(
        _d13_p3_get(
            transition,
            "direction",
        )
    )

    scenario_direction = _d13_p3_upper(
        scenario_direction
    )

    mtf_direction = None

    if mtf is not None:

        mtf_direction = (
            mtf.higher_timeframe_direction
            or mtf.lower_timeframe_direction
        )

        mtf_direction = _d13_p3_upper(
            mtf_direction
        )

    candidates = {
        "MARKET_STATE": state_direction,
        "TRANSITION": transition_direction,
        "SCENARIO": scenario_direction,
        "MTF": mtf_direction,
    }

    candidates = {
        key: value
        for key, value in candidates.items()
        if value
    }

    unique = set(
        candidates.values()
    )

    if len(unique) > 1:

        for source, direction in candidates.items():

            conflicts.append(
                {
                    "type": "DIRECTION_CONFLICT",
                    "source": source,
                    "direction": direction,
                }
            )

        return None, conflicts

    if len(unique) == 1:
        return next(
            iter(unique)
        ), conflicts

    return None, conflicts


# ============================================================
# PART-3 CONTRACT
# ============================================================

def d13_context_readiness_contract(
    context: D13ContextReadiness,
) -> Dict[str, Any]:

    return {
        "engine": D13_PART3_NAME,
        "version": D13_PART3_VERSION,

        "status": context.status.value,

        "mtf_status": (
            context.mtf.status.value
            if context.mtf
            else None
        ),

        "scenario_status": (
            context.scenarios.status.value
            if context.scenarios
            else None
        ),

        "temporal_status": (
            context.temporal.status.value
            if context.temporal
            else None
        ),

        "risk_status": (
            context.risk.status.value
            if context.risk
            else None
        ),

        "validation_status": (
            context.validation.status.value
            if context.validation
            else None
        ),

        "blockers": list(
            context.blockers
        ),

        "warnings": list(
            context.warnings
        ),

        "ready_for_authority": (
            context.ready_for_authority
        ),

        "decision_authority": False,
        "execution_authority": False,
    }


# ============================================================
# PART-3 HANDOFF
# ============================================================

def d13_part3_handoff(
    context: D13ContextReadiness,
) -> Dict[str, Any]:

    contract = d13_context_readiness_contract(
        context
    )

    return {
        "source": D13_PART3_NAME,
        "source_version": D13_PART3_VERSION,

        "readiness": contract,

        # Explicit authority boundary.
        "decision_authority": False,
        "execution_authority": False,

        # No decision is created here.
        "decision_created": False,

        # No probability is generated here.
        "probability_generated": False,

        # No execution instruction is generated here.
        "execution_instruction_created": False,
    }


# ============================================================
# PART-3 SELF TEST
# ============================================================

def d13_part3_self_check() -> Dict[str, bool]:

    test_as_of = datetime(
        2026,
        1,
        1,
        10,
        0,
        0,
    )

    mtf_records = [
        {
            "timeframe": "5M",
            "direction": "BULLISH",
            "as_of": test_as_of,
            "provenance": {
                "source": "TEST",
                "engine": "TEST",
                "version": "1.0",
            },
        },
        {
            "timeframe": "1H",
            "direction": "BULLISH",
            "as_of": test_as_of,
            "provenance": {
                "source": "TEST",
                "engine": "TEST",
                "version": "1.0",
            },
        },
    ]

    mtf = D13MTFReconciler().reconcile(
        mtf_records,
        target_as_of=test_as_of,
    )

    scenarios = [
        {
            "scenario_id": "SC-1",
            "role": "PRIMARY",
            "direction": "BULLISH",
            "as_of": test_as_of,
            "evidence_ids": ["E1"],
            "provenance": {
                "source": "D12",
                "engine": "D12_FutureScenario",
                "version": "V6-CAS-1.0",
            },
        }
    ]

    scenario_result = (
        D13ScenarioReconciler().reconcile(
            scenarios,
            target_as_of=test_as_of,
        )
    )

    temporal = D13TemporalValidator().validate(
        target_as_of=test_as_of,
        items=[
            {
                "evidence_id": "E1",
                "as_of": test_as_of,
            }
        ],
    )

    risk = evaluate_d13_risk_readiness(
        {
            "risk_state": "NORMAL",
            "risk_density": "AVAILABLE",
        }
    )

    validation = evaluate_d13_validation_readiness(
        {
            "status": "READY",
            "validated": True,
        }
    )

    context = D13ContextReadinessEngine().evaluate(
        mtf=mtf,
        scenarios=scenario_result,
        temporal=temporal,
        risk=risk,
        validation=validation,
    )

    direction, conflicts = (
        reconcile_d13_direction(
            {
                "direction": "BULLISH",
            },
            {
                "direction": "BULLISH",
            },
            "BULLISH",
            mtf,
        )
    )

    contract = d13_context_readiness_contract(
        context
    )

    handoff = d13_part3_handoff(
        context
    )

    return {
        "mtf_created": (
            mtf is not None
        ),

        "mtf_aligned": (
            mtf.status
            == D13MTFStatus.ALIGNED
        ),

        "scenario_created": (
            scenario_result is not None
        ),

        "scenario_consistent": (
            scenario_result.status
            == D13ScenarioStatus.CONSISTENT
        ),

        "temporal_valid": (
            temporal.status
            == D13TemporalStatus.VALID
        ),

        "risk_ready": (
            risk.status
            == D13ReadinessStatus.READY
        ),

        "validation_ready": (
            validation.status
            == D13ReadinessStatus.READY
        ),

        "context_ready": (
            context.ready_for_authority
        ),

        "direction_reconciled": (
            direction == "BULLISH"
            and not conflicts
        ),

        "contract_no_decision": (
            contract["decision_authority"]
            is False
        ),

        "contract_no_execution": (
            contract["execution_authority"]
            is False
        ),

        "handoff_no_decision": (
            handoff["decision_created"]
            is False
        ),

        "handoff_no_probability": (
            handoff["probability_generated"]
            is False
        ),

        "handoff_no_execution": (
            handoff["execution_instruction_created"]
            is False
        ),
    }


# ============================================================
# FACTORY
# ============================================================

def create_d13_context_readiness_engine() -> (
    D13ContextReadinessEngine
):
    return D13ContextReadinessEngine()


def create_d13_mtf_reconciler() -> (
    D13MTFReconciler
):
    return D13MTFReconciler()


def create_d13_scenario_reconciler() -> (
    D13ScenarioReconciler
):
    return D13ScenarioReconciler()


def create_d13_temporal_validator() -> (
    D13TemporalValidator
):
    return D13TemporalValidator()


# ============================================================
# EXPORTS
# ============================================================

D13_PART3_EXPORTS = (
    "D13MTFStatus",
    "D13ScenarioStatus",
    "D13TemporalStatus",
    "D13ReadinessStatus",

    "D13MTFRecord",
    "D13MTFReconciliation",
    "D13ScenarioRecord",
    "D13ScenarioReconciliation",
    "D13TemporalValidation",
    "D13RiskReadiness",
    "D13ValidationReadiness",
    "D13ContextReadiness",

    "normalize_d13_timeframe",
    "D13MTFReconciler",
    "D13ScenarioReconciler",
    "D13TemporalValidator",

    "evaluate_d13_risk_readiness",
    "evaluate_d13_validation_readiness",
    "D13ContextReadinessEngine",

    "reconcile_d13_direction",

    "d13_context_readiness_contract",
    "d13_part3_handoff",

    "d13_part3_self_check",

    "create_d13_context_readiness_engine",
    "create_d13_mtf_reconciler",
    "create_d13_scenario_reconciler",
    "create_d13_temporal_validator",
)


# ============================================================
# DIRECT PART-3 TEST
# ============================================================

if __name__ == "__main__":
    try:
        result = d13_part3_self_check()

        print(
            "D13 PART-3 SELF-TEST:",
            "PASS"
            if all(result.values())
            else "FAIL",
        )

        for key, value in result.items():
            print(
                f"  {key}: {value}"
            )

    except Exception as exc:
        print(
            "D13 PART-3 SELF-TEST: ERROR"
        )
        print(
            f"{type(exc).__name__}: {exc}"
        )
# ============================================================
# D13 DECISION AUTHORITY
# PART 4 / 4
# FINAL CONTRACT + AUTHORITY GATE + DOWNSTREAM HANDOFF
# ============================================================

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple


# ============================================================
# PART-4 CONSTANTS
# ============================================================

D13_PART4_NAME = "D13_FinalDecisionAuthority"
D13_PART4_VERSION = "V6-CAS-1.0"

D13_FINAL_DOWNSTREAM = (
    "D14_Validation",
    "D15_Learning",
    "D16_IntelligenceSynthesis",
)

D13_FORBIDDEN_DECISION_OUTPUTS = (
    "EXECUTE",
    "EXECUTION",
    "ORDER",
    "PLACE_ORDER",
    "POSITION_SIZE",
    "LEVERAGE",
    "MARGIN_AMOUNT",
    "PROFIT_TARGET",
    "PNL_TARGET",
    "GUARANTEED_PROFIT",
    "GUARANTEED_RETURN",
    "UNIVERSAL_PROBABILITY",
    "FABRICATED_CONFIDENCE",
)

D13_ALLOWED_DECISION_STATES = (
    "ACTIONABLE",
    "WAIT",
    "NO_DECISION",
    "BLOCKED",
    "UNDETERMINED",
)

D13_ALLOWED_DECISION_TYPES = (
    "CONTINUE",
    "REVERSE",
    "BREAKOUT",
    "BREAKDOWN",
    "RANGE",
    "WAIT",
    "NO_DECISION",
    "BLOCKED",
    "UNDETERMINED",
)


# ============================================================
# ENUMS
# ============================================================

class D13FinalStatus(str, Enum):
    READY = "READY"
    LIMITED = "LIMITED"
    BLOCKED = "BLOCKED"
    UNDETERMINED = "UNDETERMINED"


class D13AuthorityGateStatus(str, Enum):
    OPEN = "OPEN"
    LIMITED = "LIMITED"
    CLOSED = "CLOSED"


class D13HandoffType(str, Enum):
    VALIDATION = "VALIDATION"
    LEARNING = "LEARNING"
    INTELLIGENCE_SYNTHESIS = "INTELLIGENCE_SYNTHESIS"


# ============================================================
# FINAL CONTRACT
# ============================================================

@dataclass
class D13FinalContract:
    engine: str
    version: str

    status: D13FinalStatus

    market_id: Optional[str]
    as_of: Any

    decision_state: str
    decision_type: str

    direction: Optional[str] = None

    rationale: str = ""

    supporting_evidence: List[str] = field(
        default_factory=list
    )

    conflicting_evidence: List[str] = field(
        default_factory=list
    )

    scenario_ids: List[str] = field(
        default_factory=list
    )

    primary_scenario_id: Optional[str] = None

    market_state: Optional[str] = None
    transition_type: Optional[str] = None

    evidence_quality: Optional[str] = None

    reconciliation_status: Optional[str] = None
    context_status: Optional[str] = None

    blockers: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    provenance: Dict[str, Any] = field(
        default_factory=dict
    )

    decision_performed: bool = True

    decision_authority: bool = True

    execution_authority: bool = False

    probability_generated: bool = False

    fabricated_confidence: bool = False

    future_data_used: bool = False

    validation_required: bool = True

    learning_required: bool = True

    intelligence_synthesis_allowed: bool = True


# ============================================================
# AUTHORITY GATE
# ============================================================

@dataclass
class D13AuthorityGate:
    status: D13AuthorityGateStatus

    decision_authority: bool

    execution_authority: bool

    reasons: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    upstream_ready: bool = False
    context_ready: bool = False
    reconciliation_ready: bool = False

    future_data_blocked: bool = True

    forbidden_output_detected: bool = False


# ============================================================
# DOWNSTREAM HANDOFF
# ============================================================

@dataclass
class D13DownstreamHandoff:
    handoff_type: D13HandoffType

    source_engine: str
    source_version: str

    market_id: Optional[str]
    as_of: Any

    contract: Dict[str, Any]

    authority_verified: bool

    execution_authority: bool = False

    immutable_decision_snapshot: bool = True

    warnings: List[str] = field(
        default_factory=list
    )


# ============================================================
# FINAL PIPELINE RESULT
# ============================================================

@dataclass
class D13FinalResult:
    contract: D13FinalContract

    authority_gate: D13AuthorityGate

    validation_handoff: Optional[
        D13DownstreamHandoff
    ] = None

    learning_handoff: Optional[
        D13DownstreamHandoff
    ] = None

    intelligence_handoff: Optional[
        D13DownstreamHandoff
    ] = None


# ============================================================
# GENERIC HELPERS
# ============================================================

def _d13_p4_clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _d13_p4_upper(value: Any) -> str:
    return _d13_p4_clean(value).upper()


def _d13_p4_get(
    obj: Any,
    name: str,
    default: Any = None,
) -> Any:

    if obj is None:
        return default

    if isinstance(obj, dict):
        return obj.get(name, default)

    return getattr(
        obj,
        name,
        default,
    )


# ============================================================
# FORBIDDEN OUTPUT SCANNER
# ============================================================

def scan_d13_forbidden_outputs(
    value: Any,
) -> List[str]:
    """
    Detects prohibited execution/financial-authority fields.

    This is a structural safety boundary.
    It does not inspect natural-language rationale for ordinary
    market words such as BUY/SELL because D13's decision meaning
    may be represented through decision_state/type/direction.

    Explicit execution fields are always rejected.
    """

    found: List[str] = []

    if value is None:
        return found

    if isinstance(value, dict):

        for key, item in value.items():

            key_upper = _d13_p4_upper(key)

            if key_upper in D13_FORBIDDEN_DECISION_OUTPUTS:
                found.append(key_upper)

            found.extend(
                scan_d13_forbidden_outputs(item)
            )

        return sorted(
            set(found)
        )

    if isinstance(value, (list, tuple, set)):

        for item in value:
            found.extend(
                scan_d13_forbidden_outputs(item)
            )

        return sorted(
            set(found)
        )

    # Dataclass/object inspection is intentionally limited
    # to public instance attributes.
    if hasattr(value, "__dict__"):

        for key, item in vars(value).items():

            key_upper = _d13_p4_upper(key)

            if key_upper in D13_FORBIDDEN_DECISION_OUTPUTS:
                found.append(key_upper)

            found.extend(
                scan_d13_forbidden_outputs(item)
            )

    return sorted(
        set(found)
    )


# ============================================================
# PROBABILITY PROTECTION
# ============================================================

def validate_d13_probability_boundary(
    result: Any,
) -> Tuple[bool, List[str]]:

    reasons: List[str] = []

    probability_generated = _d13_p4_get(
        result,
        "probability_generated",
        False,
    )

    fabricated_confidence = _d13_p4_get(
        result,
        "fabricated_confidence",
        False,
    )

    if probability_generated is True:
        reasons.append(
            "D13_MUST_NOT_GENERATE_PROBABILITY"
        )

    if fabricated_confidence is True:
        reasons.append(
            "D13_FABRICATED_CONFIDENCE_FORBIDDEN"
        )

    return (
        not reasons,
        reasons,
    )


# ============================================================
# UPSTREAM READINESS EXTRACTION
# ============================================================

def _d13_p4_upstream_status(
    result: Any,
) -> str:

    return _d13_p4_upper(
        _d13_p4_get(
            result,
            "status",
            "UNDETERMINED",
        )
    )


def _d13_p4_upstream_ready(
    result: Any,
) -> bool:

    if result is None:
        return False

    ready_for_d13 = _d13_p4_get(
        result,
        "ready_for_d13",
        None,
    )

    if isinstance(
        ready_for_d13,
        bool,
    ):
        return ready_for_d13

    status = _d13_p4_upstream_status(
        result
    )

    return status == "READY"


# ============================================================
# D13 FINAL AUTHORITY GATE
# ============================================================

class D13FinalAuthorityGateEngine:

    def evaluate(
        self,
        reconciliation: Any,
        context: Any,
        upstream_results: Optional[
            Dict[str, Any]
        ] = None,
        proposed_result: Any = None,
    ) -> D13AuthorityGate:

        reasons: List[str] = []
        warnings: List[str] = []

        upstream_results = (
            upstream_results or {}
        )

        # ----------------------------------------------------
        # RECONCILIATION
        # ----------------------------------------------------

        reconciliation_status = (
            _d13_p4_upper(
                _d13_p4_get(
                    reconciliation,
                    "status",
                    "UNDETERMINED",
                )
            )
        )

        reconciliation_ready = (
            _d13_p4_get(
                reconciliation,
                "ready_for_d13",
                False,
            )
            is True
        )

        if not reconciliation_ready:

            if reconciliation_status == "BLOCKED":
                reasons.append(
                    "EVIDENCE_RECONCILIATION_BLOCKED"
                )
            else:
                reasons.append(
                    "EVIDENCE_RECONCILIATION_NOT_READY"
                )

        # ----------------------------------------------------
        # CONTEXT
        # ----------------------------------------------------

        context_ready = (
            _d13_p4_get(
                context,
                "ready_for_authority",
                False,
            )
            is True
        )

        context_status = _d13_p4_upper(
            _d13_p4_get(
                context,
                "status",
                "UNDETERMINED",
            )
        )

        if not context_ready:

            if context_status == "BLOCKED":
                reasons.append(
                    "D13_CONTEXT_BLOCKED"
                )
            else:
                reasons.append(
                    "D13_CONTEXT_NOT_READY"
                )

        # ----------------------------------------------------
        # D10 / D11 / D12
        # ----------------------------------------------------

        upstream_ready = True

        for engine_name in (
            "D10_MarketState",
            "D11_DecisionTransition",
            "D12_FutureScenario",
        ):

            result = upstream_results.get(
                engine_name
            )

            if result is None:
                upstream_ready = False
                reasons.append(
                    f"{engine_name}:RESULT_MISSING"
                )
                continue

            status = _d13_p4_upstream_status(
                result
            )

            if status == "BLOCKED":
                upstream_ready = False
                reasons.append(
                    f"{engine_name}:BLOCKED"
                )

            elif status == "UNDETERMINED":
                upstream_ready = False
                reasons.append(
                    f"{engine_name}:UNDETERMINED"
                )

            elif status == "LIMITED":
                upstream_ready = False
                warnings.append(
                    f"{engine_name}:LIMITED"
                )

            if not _d13_p4_upstream_ready(
                result
            ):
                warnings.append(
                    f"{engine_name}:NOT_EXPLICITLY_READY"
                )

            execution_authority = (
                _d13_p4_get(
                    result,
                    "execution_authority",
                    False,
                )
            )

            if execution_authority is True:
                upstream_ready = False
                reasons.append(
                    f"{engine_name}:"
                    "EXECUTION_AUTHORITY_FORBIDDEN"
                )

        # ----------------------------------------------------
        # PROPOSED OUTPUT
        # ----------------------------------------------------

        forbidden = (
            scan_d13_forbidden_outputs(
                proposed_result
            )
            if proposed_result is not None
            else []
        )

        if forbidden:
            reasons.append(
                "FORBIDDEN_OUTPUT:"
                + ",".join(forbidden)
            )

        forbidden_detected = bool(
            forbidden
        )

        probability_ok, probability_reasons = (
            validate_d13_probability_boundary(
                proposed_result
            )
        )

        if not probability_ok:
            reasons.extend(
                probability_reasons
            )

        # ----------------------------------------------------
        # FINAL GATE
        # ----------------------------------------------------

        if reasons:
            gate_status = (
                D13AuthorityGateStatus.CLOSED
            )

        elif warnings:
            gate_status = (
                D13AuthorityGateStatus.LIMITED
            )

        else:
            gate_status = (
                D13AuthorityGateStatus.OPEN
            )

        decision_authority = (
            gate_status
            == D13AuthorityGateStatus.OPEN
        )

        return D13AuthorityGate(
            status=gate_status,
            decision_authority=decision_authority,
            execution_authority=False,
            reasons=reasons,
            warnings=warnings,
            upstream_ready=upstream_ready,
            context_ready=context_ready,
            reconciliation_ready=reconciliation_ready,
            future_data_blocked=True,
            forbidden_output_detected=(
                forbidden_detected
            ),
        )


# ============================================================
# DECISION TYPE NORMALIZATION
# ============================================================

def normalize_d13_decision_state(
    value: Any,
) -> str:

    state = _d13_p4_upper(
        value
    )

    if state in D13_ALLOWED_DECISION_STATES:
        return state

    return "UNDETERMINED"


def normalize_d13_decision_type(
    value: Any,
) -> str:

    decision_type = _d13_p4_upper(
        value
    )

    if decision_type in D13_ALLOWED_DECISION_TYPES:
        return decision_type

    return "UNDETERMINED"


# ============================================================
# FINAL CONTRACT BUILDER
# ============================================================

def build_d13_final_contract(
    decision_result: Any,
    reconciliation: Any,
    context: Any,
    authority_gate: D13AuthorityGate,
) -> D13FinalContract:

    market_id = _d13_p4_get(
        decision_result,
        "market_id",
    )

    as_of = _d13_p4_get(
        decision_result,
        "as_of",
    )

    decision_state = normalize_d13_decision_state(
        _d13_p4_get(
            decision_result,
            "decision_state",
            "UNDETERMINED",
        )
    )

    decision_type = normalize_d13_decision_type(
        _d13_p4_get(
            decision_result,
            "decision_type",
            "UNDETERMINED",
        )
    )

    direction = _d13_p4_get(
        decision_result,
        "direction",
    )

    rationale = _d13_p4_clean(
        _d13_p4_get(
            decision_result,
            "rationale",
            "",
        )
    )

    supporting = list(
        _d13_p4_get(
            decision_result,
            "supporting_evidence",
            [],
        )
        or []
    )

    conflicting = list(
        _d13_p4_get(
            decision_result,
            "conflicting_evidence",
            [],
        )
        or []
    )

    scenario_ids = list(
        _d13_p4_get(
            decision_result,
            "scenario_ids",
            [],
        )
        or []
    )

    primary_scenario_id = (
        _d13_p4_get(
            decision_result,
            "primary_scenario_id",
        )
        or _d13_p4_get(
            reconciliation,
            "primary_scenario_id",
        )
    )

    market_state = _d13_p4_get(
        decision_result,
        "market_state",
    )

    transition_type = _d13_p4_get(
        decision_result,
        "transition_type",
    )

    evidence_quality = _d13_p4_get(
        decision_result,
        "evidence_quality",
    )

    reconciliation_status = _d13_p4_upper(
        _d13_p4_get(
            reconciliation,
            "status",
        )
    )

    context_status = _d13_p4_upper(
        _d13_p4_get(
            context,
            "status",
        )
    )

    blockers = list(
        authority_gate.reasons
    )

    warnings = list(
        authority_gate.warnings
    )

    status = D13FinalStatus.BLOCKED

    if authority_gate.status == (
        D13AuthorityGateStatus.OPEN
    ):
        status = D13FinalStatus.READY

    elif authority_gate.status == (
        D13AuthorityGateStatus.LIMITED
    ):
        status = D13FinalStatus.LIMITED

    elif authority_gate.status == (
        D13AuthorityGateStatus.CLOSED
    ):
        status = D13FinalStatus.BLOCKED

    provenance = dict(
        _d13_p4_get(
            decision_result,
            "provenance",
            {},
        )
        or {}
    )

    provenance.update(
        {
            "d13_part4_engine": D13_PART4_NAME,
            "d13_part4_version": D13_PART4_VERSION,
        }
    )

    return D13FinalContract(
        engine=D13_PART4_NAME,
        version=D13_PART4_VERSION,
        status=status,
        market_id=market_id,
        as_of=as_of,
        decision_state=decision_state,
        decision_type=decision_type,
        direction=direction,
        rationale=rationale,
        supporting_evidence=supporting,
        conflicting_evidence=conflicting,
        scenario_ids=scenario_ids,
        primary_scenario_id=primary_scenario_id,
        market_state=market_state,
        transition_type=transition_type,
        evidence_quality=evidence_quality,
        reconciliation_status=(
            reconciliation_status
        ),
        context_status=context_status,
        blockers=blockers,
        warnings=warnings,
        provenance=provenance,
        decision_performed=True,
        decision_authority=(
            authority_gate.decision_authority
        ),
        execution_authority=False,
        probability_generated=False,
        fabricated_confidence=False,
        future_data_used=False,
        validation_required=True,
        learning_required=True,
        intelligence_synthesis_allowed=True,
    )


# ============================================================
# FINAL CONTRACT VALIDATOR
# ============================================================

def validate_d13_final_contract(
    contract: D13FinalContract,
) -> Tuple[bool, List[str]]:

    problems: List[str] = []

    if not contract.engine:
        problems.append(
            "ENGINE_MISSING"
        )

    if not contract.version:
        problems.append(
            "VERSION_MISSING"
        )

    if contract.execution_authority:
        problems.append(
            "EXECUTION_AUTHORITY_MUST_BE_FALSE"
        )

    if contract.probability_generated:
        problems.append(
            "PROBABILITY_GENERATION_FORBIDDEN"
        )

    if contract.fabricated_confidence:
        problems.append(
            "FABRICATED_CONFIDENCE_FORBIDDEN"
        )

    if contract.future_data_used:
        problems.append(
            "FUTURE_DATA_FORBIDDEN"
        )

    if contract.decision_state not in (
        D13_ALLOWED_DECISION_STATES
    ):
        problems.append(
            "INVALID_DECISION_STATE"
        )

    if contract.decision_type not in (
        D13_ALLOWED_DECISION_TYPES
    ):
        problems.append(
            "INVALID_DECISION_TYPE"
        )

    if contract.status == (
        D13FinalStatus.READY
    ):
        if not contract.decision_authority:
            problems.append(
                "READY_REQUIRES_DECISION_AUTHORITY"
            )

        if contract.blockers:
            problems.append(
                "READY_CONTRACT_HAS_BLOCKERS"
            )

    return (
        len(problems) == 0,
        problems,
    )


# ============================================================
# IMMUTABLE DOWNSTREAM HANDOFF BUILDER
# ============================================================

def build_d13_downstream_handoff(
    contract: D13FinalContract,
    handoff_type: D13HandoffType,
) -> D13DownstreamHandoff:

    contract_dict = d13_final_contract_to_dict(
        contract
    )

    warnings: List[str] = []

    if not contract.decision_authority:
        warnings.append(
            "DECISION_AUTHORITY_NOT_OPEN"
        )

    return D13DownstreamHandoff(
        handoff_type=handoff_type,
        source_engine=contract.engine,
        source_version=contract.version,
        market_id=contract.market_id,
        as_of=contract.as_of,
        contract=contract_dict,
        authority_verified=(
            contract.decision_authority
        ),
        execution_authority=False,
        immutable_decision_snapshot=True,
        warnings=warnings,
    )


# ============================================================
# FINAL CONTRACT SERIALIZATION
# ============================================================

def d13_final_contract_to_dict(
    contract: D13FinalContract,
) -> Dict[str, Any]:

    return {
        "engine": contract.engine,
        "version": contract.version,

        "status": contract.status.value,

        "market_id": contract.market_id,
        "as_of": contract.as_of,

        "decision_state": contract.decision_state,
        "decision_type": contract.decision_type,
        "direction": contract.direction,

        "rationale": contract.rationale,

        "supporting_evidence": list(
            contract.supporting_evidence
        ),

        "conflicting_evidence": list(
            contract.conflicting_evidence
        ),

        "scenario_ids": list(
            contract.scenario_ids
        ),

        "primary_scenario_id": (
            contract.primary_scenario_id
        ),

        "market_state": contract.market_state,
        "transition_type": contract.transition_type,

        "evidence_quality": (
            contract.evidence_quality
        ),

        "reconciliation_status": (
            contract.reconciliation_status
        ),

        "context_status": (
            contract.context_status
        ),

        "blockers": list(
            contract.blockers
        ),

        "warnings": list(
            contract.warnings
        ),

        "provenance": dict(
            contract.provenance
        ),

        "decision_performed": (
            contract.decision_performed
        ),

        "decision_authority": (
            contract.decision_authority
        ),

        "execution_authority": False,

        "probability_generated": False,

        "fabricated_confidence": False,

        "future_data_used": False,

        "validation_required": (
            contract.validation_required
        ),

        "learning_required": (
            contract.learning_required
        ),

        "intelligence_synthesis_allowed": (
            contract.intelligence_synthesis_allowed
        ),
    }


# ============================================================
# FINAL PIPELINE
# ============================================================

class D13FinalPipeline:

    def __init__(self) -> None:

        self._history: List[
            D13FinalResult
        ] = []

        self._gate_engine = (
            D13FinalAuthorityGateEngine()
        )

    def evaluate(
        self,
        decision_result: Any,
        reconciliation: Any,
        context: Any,
        upstream_results: Optional[
            Dict[str, Any]
        ] = None,
    ) -> D13FinalResult:

        # ----------------------------------------------------
        # SECURITY / AUTHORITY GATE
        # ----------------------------------------------------

        gate = self._gate_engine.evaluate(
            reconciliation=reconciliation,
            context=context,
            upstream_results=(
                upstream_results or {}
            ),
            proposed_result=decision_result,
        )

        # ----------------------------------------------------
        # FINAL CONTRACT
        # ----------------------------------------------------

        contract = build_d13_final_contract(
            decision_result=decision_result,
            reconciliation=reconciliation,
            context=context,
            authority_gate=gate,
        )

        contract_ok, contract_problems = (
            validate_d13_final_contract(
                contract
            )
        )

        if not contract_ok:

            contract.status = (
                D13FinalStatus.BLOCKED
            )

            contract.decision_authority = False

            contract.blockers.extend(
                contract_problems
            )

        # ----------------------------------------------------
        # DOWNSTREAM HANDOFFS
        # ----------------------------------------------------

        validation_handoff = (
            build_d13_downstream_handoff(
                contract,
                D13HandoffType.VALIDATION,
            )
        )

        learning_handoff = (
            build_d13_downstream_handoff(
                contract,
                D13HandoffType.LEARNING,
            )
        )

        intelligence_handoff = (
            build_d13_downstream_handoff(
                contract,
                D13HandoffType.INTELLIGENCE_SYNTHESIS,
            )
        )

        result = D13FinalResult(
            contract=contract,
            authority_gate=gate,
            validation_handoff=validation_handoff,
            learning_handoff=learning_handoff,
            intelligence_handoff=(
                intelligence_handoff
            ),
        )

        self._history.append(
            result
        )

        return result

    def history(self) -> List[D13FinalResult]:
        return list(
            self._history
        )

    def latest(self) -> Optional[D13FinalResult]:

        if not self._history:
            return None

        return self._history[-1]


# ============================================================
# D13 -> D14 HANDOFF
# ============================================================

def d13_to_d14_handoff(
    final_result: D13FinalResult,
) -> D13DownstreamHandoff:

    return build_d13_downstream_handoff(
        final_result.contract,
        D13HandoffType.VALIDATION,
    )


# ============================================================
# D13 -> D15 HANDOFF
# ============================================================

def d13_to_d15_handoff(
    final_result: D13FinalResult,
) -> D13DownstreamHandoff:

    return build_d13_downstream_handoff(
        final_result.contract,
        D13HandoffType.LEARNING,
    )


# ============================================================
# D13 -> D16 HANDOFF
# ============================================================

def d13_to_d16_handoff(
    final_result: D13FinalResult,
) -> D13DownstreamHandoff:

    return build_d13_downstream_handoff(
        final_result.contract,
        D13HandoffType.INTELLIGENCE_SYNTHESIS,
    )


# ============================================================
# COMPLETE D13 CONTRACT
# ============================================================

def d13_complete_contract(
    final_result: D13FinalResult,
) -> Dict[str, Any]:

    return {
        "d13": d13_final_contract_to_dict(
            final_result.contract
        ),

        "authority_gate": {
            "status": (
                final_result.authority_gate.status.value
            ),
            "decision_authority": (
                final_result.authority_gate.decision_authority
            ),
            "execution_authority": False,
            "upstream_ready": (
                final_result.authority_gate.upstream_ready
            ),
            "context_ready": (
                final_result.authority_gate.context_ready
            ),
            "reconciliation_ready": (
                final_result.authority_gate.reconciliation_ready
            ),
            "future_data_blocked": True,
            "forbidden_output_detected": (
                final_result.authority_gate
                .forbidden_output_detected
            ),
            "reasons": list(
                final_result.authority_gate.reasons
            ),
            "warnings": list(
                final_result.authority_gate.warnings
            ),
        },

        "downstream": {
            "D14": (
                d13_final_contract_to_dict(
                    final_result.contract
                )
            ),
            "D15": (
                d13_final_contract_to_dict(
                    final_result.contract
                )
            ),
            "D16": (
                d13_final_contract_to_dict(
                    final_result.contract
                )
            ),
        },

        "authority_boundary": {
            "D13_decision_authority": (
                final_result.contract
                .decision_authority
            ),
            "D13_execution_authority": False,
            "D13_probability_generation": False,
            "D13_future_data_usage": False,
        },
    }


# ============================================================
# COMPLETE SELF TEST
# ============================================================

def d13_part4_self_check() -> Dict[str, bool]:

    reconciliation = {
        "status": "READY",
        "ready_for_d13": True,
        "primary_scenario_id": "SC-1",
    }

    context = {
        "status": "READY",
        "ready_for_authority": True,
    }

    test_decision = {
        "market_id": "TEST",
        "as_of": "2026-01-01T10:00:00",
        "decision_state": "ACTIONABLE",
        "decision_type": "CONTINUE",
        "direction": "BULLISH",
        "rationale": (
            "Validated upstream market state and transition."
        ),
        "supporting_evidence": [
            "E1",
            "E2",
        ],
        "conflicting_evidence": [],
        "scenario_ids": [
            "SC-1",
        ],
        "primary_scenario_id": "SC-1",
        "market_state": "BULLISH_EXPANSION",
        "transition_type": "BULLISH_DEVELOPMENT",
        "evidence_quality": "STRONG",
        "provenance": {
            "source": "D13",
            "engine": "D13_DecisionAuthority",
            "version": "V6-CAS-1.0",
        },

        # Explicitly false.
        "execution_authority": False,
        "probability_generated": False,
        "fabricated_confidence": False,
    }

    upstream = {
        "D10_MarketState": {
            "status": "READY",
            "ready_for_d13": True,
            "authority": True,
            "decision_performed": False,
            "execution_authority": False,
        },
        "D11_DecisionTransition": {
            "status": "READY",
            "ready_for_d13": True,
            "authority": True,
            "decision_performed": False,
            "execution_authority": False,
        },
        "D12_FutureScenario": {
            "status": "READY",
            "ready_for_d13": True,
            "authority": True,
            "decision_performed": False,
            "execution_authority": False,
        },
    }

    pipeline = D13FinalPipeline()

    result = pipeline.evaluate(
        decision_result=test_decision,
        reconciliation=reconciliation,
        context=context,
        upstream_results=upstream,
    )

    contract = result.contract

    valid, problems = (
        validate_d13_final_contract(
            contract
        )
    )

    complete = d13_complete_contract(
        result
    )

    forbidden = scan_d13_forbidden_outputs(
        {
            "decision_state": "ACTIONABLE",
            "decision_type": "CONTINUE",
            "execution_authority": False,
        }
    )

    probability_ok, probability_reasons = (
        validate_d13_probability_boundary(
            test_decision
        )
    )

    d14 = d13_to_d14_handoff(
        result
    )

    d15 = d13_to_d15_handoff(
        result
    )

    d16 = d13_to_d16_handoff(
        result
    )

    return {
        "pipeline_created": (
            result is not None
        ),

        "gate_open": (
            result.authority_gate.status
            == D13AuthorityGateStatus.OPEN
        ),

        "decision_authority_true": (
            contract.decision_authority
            is True
        ),

        "execution_authority_false": (
            contract.execution_authority
            is False
        ),

        "contract_valid": (
            valid
            and not problems
        ),

        "probability_boundary_valid": (
            probability_ok
            and not probability_reasons
        ),

        "no_forbidden_output": (
            not forbidden
        ),

        "future_data_blocked": (
            contract.future_data_used
            is False
        ),

        "d14_handoff_created": (
            d14 is not None
        ),

        "d15_handoff_created": (
            d15 is not None
        ),

        "d16_handoff_created": (
            d16 is not None
        ),

        "d14_no_execution": (
            d14.execution_authority
            is False
        ),

        "d15_no_execution": (
            d15.execution_authority
            is False
        ),

        "d16_no_execution": (
            d16.execution_authority
            is False
        ),

        "immutable_snapshot": (
            d14.immutable_decision_snapshot
            and d15.immutable_decision_snapshot
            and d16.immutable_decision_snapshot
        ),

        "complete_contract_created": (
            isinstance(
                complete,
                dict,
            )
        ),

        "authority_boundary_preserved": (
            complete[
                "authority_boundary"
            ][
                "D13_execution_authority"
            ]
            is False
        ),
    }


# ============================================================
# COMPLETE D13 SELF CHECK
# ============================================================

def d13_complete_self_check() -> Dict[str, bool]:
    """
    Combined D13 Parts 1-4 audit.

    Existing Part-1 self-test is called when available.
    Part-2 and Part-3 tests are called when available.
    Part-4 final authority test is always included.

    The function intentionally does not convert missing
    upstream implementation into a fake PASS.
    """

    result: Dict[str, bool] = {}

    # --------------------------------------------------------
    # PART 1
    # --------------------------------------------------------

    part1_function = globals().get(
        "d13_part1_self_check"
    )

    if callable(part1_function):

        try:
            part1 = part1_function()

            if isinstance(part1, dict):
                result.update(
                    {
                        f"part1_{key}": bool(value)
                        for key, value in part1.items()
                    }
                )

                result["part1_all_pass"] = (
                    all(part1.values())
                    if part1
                    else False
                )

            else:
                result["part1_all_pass"] = False

        except Exception:
            result["part1_all_pass"] = False

    else:
        result["part1_all_pass"] = False

    # --------------------------------------------------------
    # PART 2
    # --------------------------------------------------------

    part2_function = globals().get(
        "d13_part2_self_check"
    )

    if callable(part2_function):

        try:
            part2 = part2_function()

            if isinstance(part2, dict):
                result.update(
                    {
                        f"part2_{key}": bool(value)
                        for key, value in part2.items()
                    }
                )

                result["part2_all_pass"] = (
                    all(part2.values())
                    if part2
                    else False
                )

            else:
                result["part2_all_pass"] = False

        except Exception:
            result["part2_all_pass"] = False

    else:
        result["part2_all_pass"] = False

    # --------------------------------------------------------
    # PART 3
    # --------------------------------------------------------

    part3_function = globals().get(
        "d13_part3_self_check"
    )

    if callable(part3_function):

        try:
            part3 = part3_function()

            if isinstance(part3, dict):
                result.update(
                    {
                        f"part3_{key}": bool(value)
                        for key, value in part3.items()
                    }
                )

                result["part3_all_pass"] = (
                    all(part3.values())
                    if part3
                    else False
                )

            else:
                result["part3_all_pass"] = False

        except Exception:
            result["part3_all_pass"] = False

    else:
        result["part3_all_pass"] = False

    # --------------------------------------------------------
    # PART 4
    # --------------------------------------------------------

    part4 = d13_part4_self_check()

    result.update(
        {
            f"part4_{key}": bool(value)
            for key, value in part4.items()
        }
    )

    result["part4_all_pass"] = (
        all(part4.values())
        if part4
        else False
    )

    # --------------------------------------------------------
    # COMPLETE
    # --------------------------------------------------------

    result["all_pass"] = (
        all(result.values())
        if result
        else False
    )

    return result


# ============================================================
# FACTORY
# ============================================================

def create_d13_final_pipeline() -> (
    D13FinalPipeline
):
    return D13FinalPipeline()


def create_d13_authority_gate() -> (
    D13FinalAuthorityGateEngine
):
    return D13FinalAuthorityGateEngine()


# ============================================================
# EXPORTS
# ============================================================

D13_PART4_EXPORTS = (
    "D13FinalStatus",
    "D13AuthorityGateStatus",
    "D13HandoffType",

    "D13FinalContract",
    "D13AuthorityGate",
    "D13DownstreamHandoff",
    "D13FinalResult",

    "scan_d13_forbidden_outputs",
    "validate_d13_probability_boundary",

    "D13FinalAuthorityGateEngine",

    "normalize_d13_decision_state",
    "normalize_d13_decision_type",

    "build_d13_final_contract",
    "validate_d13_final_contract",

    "build_d13_downstream_handoff",

    "d13_final_contract_to_dict",

    "D13FinalPipeline",

    "d13_to_d14_handoff",
    "d13_to_d15_handoff",
    "d13_to_d16_handoff",

    "d13_complete_contract",

    "d13_part4_self_check",
    "d13_complete_self_check",

    "create_d13_final_pipeline",
    "create_d13_authority_gate",
)


# ============================================================
# DIRECT PART-4 TEST
# ============================================================

if __name__ == "__main__":
    try:

        result = d13_part4_self_check()

        print(
            "D13 PART-4 SELF-TEST:",
            "PASS"
            if all(result.values())
            else "FAIL",
        )

        for key, value in result.items():
            print(
                f"  {key}: {value}"
            )

    except Exception as exc:

        print(
            "D13 PART-4 SELF-TEST: ERROR"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )