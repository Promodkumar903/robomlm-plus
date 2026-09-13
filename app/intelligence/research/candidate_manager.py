# ============================================================
# ROBOMLM_PLUS
# app/intelligence/research/candidate_manager.py
# RESEARCH CANDIDATE MANAGEMENT — PART 1
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Optional
from uuid import uuid4


# ============================================================
# ENGINE IDENTITY
# ============================================================

CANDIDATE_MANAGER_ENGINE = "ROBOMLM_RESEARCH_CANDIDATE_MANAGER"
CANDIDATE_MANAGER_VERSION = "1.0"


# ============================================================
# ENUMS
# ============================================================

class CandidateStatus(str, Enum):
    NEW = "NEW"
    PROPOSED = "PROPOSED"
    SCREENING = "SCREENING"
    QUALIFIED = "QUALIFIED"
    REJECTED = "REJECTED"
    ARCHIVED = "ARCHIVED"
    INVALID = "INVALID"


class CandidateType(str, Enum):
    HYPOTHESIS = "HYPOTHESIS"
    STRATEGY = "STRATEGY"
    MODEL = "MODEL"
    SIGNAL = "SIGNAL"
    FORMULA = "FORMULA"
    ALGORITHM = "ALGORITHM"
    FEATURE = "FEATURE"
    ENGINE = "ENGINE"
    UNKNOWN = "UNKNOWN"


class CandidatePriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class CandidateDecision(str, Enum):
    ACCEPT = "ACCEPT"
    HOLD = "HOLD"
    REJECT = "REJECT"
    REVIEW = "REVIEW"
    UNKNOWN = "UNKNOWN"


class CandidateContractStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


# ============================================================
# REQUEST CONTRACT
# ============================================================

@dataclass(frozen=True)
class CandidateRequest:
    """
    Controlled input contract for research-candidate management.

    This layer manages research candidates only.

    It MUST NOT:
        - create trading decisions
        - override D13
        - recalculate Risk
        - create CAS authorization
        - execute orders
        - modify live positions
        - invent research evidence
    """

    candidate: Any
    candidate_type: CandidateType = CandidateType.UNKNOWN

    source: Optional[Any] = None
    hypothesis: Optional[Any] = None
    dataset: Optional[Any] = None
    experiment: Optional[Any] = None

    priority: CandidatePriority = CandidatePriority.UNKNOWN

    metadata: Mapping[str, Any] = field(default_factory=dict)

    request_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []

        if self.candidate is None:
            errors.append("candidate is required")

        if not self.request_id.strip():
            errors.append("request_id is required")

        if not isinstance(self.metadata, Mapping):
            errors.append("metadata must be a Mapping")

        return tuple(errors)


# ============================================================
# CANDIDATE REFERENCE
# ============================================================

@dataclass(frozen=True)
class CandidateReference:
    candidate_id: str
    name: str
    candidate_type: CandidateType

    status: CandidateStatus
    priority: CandidatePriority

    source: Optional[str] = None
    hypothesis_id: Optional[str] = None
    dataset_id: Optional[str] = None
    experiment_id: Optional[str] = None

    raw_candidate: Any = None


# ============================================================
# SOURCE REFERENCE
# ============================================================

@dataclass(frozen=True)
class CandidateSourceReference:
    source_id: Optional[str]
    source_type: Optional[str]
    source_name: Optional[str]

    source_version: Optional[str] = None
    source_location: Optional[str] = None

    raw_source: Any = None


# ============================================================
# CONTRACT VALIDATION
# ============================================================

@dataclass(frozen=True)
class CandidateContractValidation:
    status: CandidateContractStatus
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:
        return self.status == CandidateContractStatus.VALID


# ============================================================
# SAFE READ HELPERS
# ============================================================

def _cm_read_value(
    obj: Any,
    *names: str,
    default: Any = None,
) -> Any:
    if obj is None:
        return default

    if isinstance(obj, Mapping):
        for name in names:
            if name in obj:
                return obj[name]

    for name in names:
        try:
            value = getattr(obj, name)
        except Exception:
            continue

        if value is not None:
            return value

    return default


def _cm_text(
    value: Any,
    default: Optional[str] = None,
) -> Optional[str]:
    if value is None:
        return default

    text = str(value).strip()

    return text if text else default


def _cm_enum(
    value: Any,
    enum_type: type[Enum],
    default: Enum,
) -> Enum:
    if isinstance(value, enum_type):
        return value

    if value is None:
        return default

    text = str(value).strip().upper()

    for member in enum_type:
        if text in {member.name, str(member.value).upper()}:
            return member

    return default


# ============================================================
# CANDIDATE ADAPTER
# ============================================================

def build_candidate_reference(
    candidate: Any,
    *,
    candidate_type: CandidateType = CandidateType.UNKNOWN,
    priority: CandidatePriority = CandidatePriority.UNKNOWN,
    source: Optional[Any] = None,
    hypothesis: Optional[Any] = None,
    dataset: Optional[Any] = None,
    experiment: Optional[Any] = None,
) -> CandidateReference:

    candidate_id = _cm_text(
        _cm_read_value(
            candidate,
            "candidate_id",
            "id",
            "uid",
        ),
        default=str(uuid4()),
    )

    name = _cm_text(
        _cm_read_value(
            candidate,
            "name",
            "title",
            "candidate_name",
        ),
        default=candidate_id,
    )

    raw_type = _cm_read_value(
        candidate,
        "candidate_type",
        "type",
    )

    normalized_type = _cm_enum(
        raw_type,
        CandidateType,
        candidate_type,
    )

    raw_status = _cm_read_value(
        candidate,
        "status",
        "state",
    )

    status = _cm_enum(
        raw_status,
        CandidateStatus,
        CandidateStatus.NEW,
    )

    raw_priority = _cm_read_value(
        candidate,
        "priority",
    )

    normalized_priority = _cm_enum(
        raw_priority,
        CandidatePriority,
        priority,
    )

    source_id = _cm_text(
        _cm_read_value(
            source,
            "source_id",
            "id",
        )
    )

    hypothesis_id = _cm_text(
        _cm_read_value(
            hypothesis,
            "hypothesis_id",
            "id",
        )
    )

    dataset_id = _cm_text(
        _cm_read_value(
            dataset,
            "dataset_id",
            "id",
        )
    )

    experiment_id = _cm_text(
        _cm_read_value(
            experiment,
            "experiment_id",
            "id",
        )
    )

    return CandidateReference(
        candidate_id=candidate_id,
        name=name,
        candidate_type=normalized_type,
        status=status,
        priority=normalized_priority,
        source=source_id,
        hypothesis_id=hypothesis_id,
        dataset_id=dataset_id,
        experiment_id=experiment_id,
        raw_candidate=candidate,
    )


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_candidate_request(
    request: CandidateRequest,
) -> CandidateContractValidation:

    errors = request.validate()

    if errors:
        return CandidateContractValidation(
            status=CandidateContractStatus.INVALID,
            errors=errors,
        )

    reference = build_candidate_reference(
        request.candidate,
        candidate_type=request.candidate_type,
        priority=request.priority,
        source=request.source,
        hypothesis=request.hypothesis,
        dataset=request.dataset,
        experiment=request.experiment,
    )

    warnings: list[str] = []

    if reference.candidate_type == CandidateType.UNKNOWN:
        warnings.append("candidate type is unknown")

    if reference.priority == CandidatePriority.UNKNOWN:
        warnings.append("candidate priority is unknown")

    return CandidateContractValidation(
        status=CandidateContractStatus.VALID,
        warnings=tuple(warnings),
    )


# ============================================================
# PUBLIC EXPORTS — PART 1
# ============================================================

__all__ = [
    "CANDIDATE_MANAGER_ENGINE",
    "CANDIDATE_MANAGER_VERSION",
    "CandidateStatus",
    "CandidateType",
    "CandidatePriority",
    "CandidateDecision",
    "CandidateContractStatus",
    "CandidateRequest",
    "CandidateReference",
    "CandidateSourceReference",
    "CandidateContractValidation",
    "build_candidate_reference",
    "validate_candidate_request",
]
# ============================================================
# CANDIDATE INTELLIGENCE — PART 2
# ============================================================

class CandidateConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONFLICTING = "CONFLICTING"
    INSUFFICIENT = "INSUFFICIENT"


class CandidateDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"


class CandidateDisposition(str, Enum):
    ADVANCE = "ADVANCE"
    REVIEW = "REVIEW"
    HOLD = "HOLD"
    REJECT = "REJECT"
    ARCHIVE = "ARCHIVE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class CandidateRequirements:
    candidate_available: bool
    candidate_id_available: bool
    name_available: bool
    type_available: bool
    source_available: bool
    hypothesis_available: bool
    dataset_available: bool
    experiment_available: bool
    priority_available: bool

    identity_consistent: bool = True
    source_consistent: bool = True


@dataclass(frozen=True)
class CandidateIntelligence:
    consistency: CandidateConsistency
    data_state: CandidateDataState

    status: CandidateStatus
    candidate_type: CandidateType
    priority: CandidatePriority
    disposition: CandidateDisposition

    candidate_id: Optional[str]
    name: Optional[str]

    source_id: Optional[str]
    hypothesis_id: Optional[str]
    dataset_id: Optional[str]
    experiment_id: Optional[str]

    rationale: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    source: str = CANDIDATE_MANAGER_ENGINE


@dataclass(frozen=True)
class CandidateAssessment:
    intelligence: CandidateIntelligence
    requirements: CandidateRequirements
    candidate: CandidateReference
    source: Optional[CandidateSourceReference] = None

    rationale: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


# ============================================================
# NORMALIZATION HELPERS
# ============================================================

def _cm_normalized_text(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip().upper()


def _cm_status_is_invalid(status: Any) -> bool:
    value = _cm_normalized_text(status)

    return value in {
        "INVALID",
        "FAILED",
        "ERROR",
        "CORRUPT",
    }


def _cm_status_is_blocking(status: Any) -> bool:
    value = _cm_normalized_text(status)

    return value in {
        "REJECTED",
        "BLOCKED",
        "INVALID",
        "FAILED",
        "UNSAFE",
        "CRITICAL",
    }


def _cm_status_is_unknown(status: Any) -> bool:
    value = _cm_normalized_text(status)

    return value in {
        "",
        "UNKNOWN",
        "UNSPECIFIED",
        "NONE",
        "NULL",
        "N/A",
        "NA",
    }


# ============================================================
# REQUIREMENT EVALUATION
# ============================================================

def evaluate_candidate_requirements(
    request: CandidateRequest,
) -> CandidateRequirements:

    candidate = request.candidate

    candidate_id = _cm_text(
        _cm_read_value(candidate, "candidate_id", "id", "uid")
    )

    name = _cm_text(
        _cm_read_value(candidate, "name", "title", "candidate_name")
    )

    raw_type = _cm_read_value(
        candidate,
        "candidate_type",
        "type",
    )

    source_available = request.source is not None
    hypothesis_available = request.hypothesis is not None
    dataset_available = request.dataset is not None
    experiment_available = request.experiment is not None

    priority_available = (
        request.priority != CandidatePriority.UNKNOWN
        or _cm_read_value(candidate, "priority") is not None
    )

    return CandidateRequirements(
        candidate_available=candidate is not None,
        candidate_id_available=bool(candidate_id),
        name_available=bool(name),
        type_available=(
            request.candidate_type != CandidateType.UNKNOWN
            or raw_type is not None
        ),
        source_available=source_available,
        hypothesis_available=hypothesis_available,
        dataset_available=dataset_available,
        experiment_available=experiment_available,
        priority_available=priority_available,
    )


# ============================================================
# DATA STATE
# ============================================================

def evaluate_candidate_data_state(
    requirements: CandidateRequirements,
) -> CandidateDataState:

    if not requirements.candidate_available:
        return CandidateDataState.MISSING

    critical = (
        requirements.candidate_id_available
        and requirements.name_available
    )

    if not critical:
        return CandidateDataState.PARTIAL

    if not requirements.type_available:
        return CandidateDataState.PARTIAL

    return CandidateDataState.COMPLETE


# ============================================================
# CONSISTENCY EVALUATION
# ============================================================

def evaluate_candidate_consistency(
    candidate: CandidateReference,
    requirements: CandidateRequirements,
) -> CandidateConsistency:

    if not requirements.candidate_available:
        return CandidateConsistency.INSUFFICIENT

    if not requirements.candidate_id_available:
        return CandidateConsistency.INSUFFICIENT

    if not requirements.identity_consistent:
        return CandidateConsistency.CONFLICTING

    if not requirements.source_consistent:
        return CandidateConsistency.CONFLICTING

    if candidate.status == CandidateStatus.INVALID:
        return CandidateConsistency.CONFLICTING

    return CandidateConsistency.CONSISTENT


# ============================================================
# DISPOSITION
# ============================================================

def evaluate_candidate_disposition(
    *,
    status: CandidateStatus,
    consistency: CandidateConsistency,
    data_state: CandidateDataState,
    priority: CandidatePriority,
) -> CandidateDisposition:

    if consistency == CandidateConsistency.CONFLICTING:
        return CandidateDisposition.REJECT

    if data_state == CandidateDataState.MISSING:
        return CandidateDisposition.HOLD

    if status == CandidateStatus.REJECTED:
        return CandidateDisposition.REJECT

    if status == CandidateStatus.ARCHIVED:
        return CandidateDisposition.ARCHIVE

    if status == CandidateStatus.INVALID:
        return CandidateDisposition.REJECT

    if data_state == CandidateDataState.PARTIAL:
        return CandidateDisposition.REVIEW

    if status in {
        CandidateStatus.NEW,
        CandidateStatus.PROPOSED,
        CandidateStatus.SCREENING,
    }:
        if priority == CandidatePriority.CRITICAL:
            return CandidateDisposition.ADVANCE

        if priority == CandidatePriority.HIGH:
            return CandidateDisposition.ADVANCE

        return CandidateDisposition.REVIEW

    if status == CandidateStatus.QUALIFIED:
        return CandidateDisposition.ADVANCE

    return CandidateDisposition.UNKNOWN


# ============================================================
# SOURCE REFERENCE
# ============================================================

def build_candidate_source_reference(
    source: Any,
) -> CandidateSourceReference:

    if source is None:
        return CandidateSourceReference(
            source_id=None,
            source_type=None,
            source_name=None,
        )

    return CandidateSourceReference(
        source_id=_cm_text(
            _cm_read_value(source, "source_id", "id")
        ),
        source_type=_cm_text(
            _cm_read_value(source, "source_type", "type")
        ),
        source_name=_cm_text(
            _cm_read_value(source, "source_name", "name", "title")
        ),
        source_version=_cm_text(
            _cm_read_value(source, "version", "source_version")
        ),
        source_location=_cm_text(
            _cm_read_value(
                source,
                "location",
                "source_location",
                "uri",
            )
        ),
        raw_source=source,
    )


# ============================================================
# INTELLIGENCE BUILDER
# ============================================================

def build_candidate_intelligence(
    candidate: CandidateReference,
    requirements: CandidateRequirements,
) -> CandidateIntelligence:

    data_state = evaluate_candidate_data_state(requirements)

    consistency = evaluate_candidate_consistency(
        candidate,
        requirements,
    )

    disposition = evaluate_candidate_disposition(
        status=candidate.status,
        consistency=consistency,
        data_state=data_state,
        priority=candidate.priority,
    )

    rationale: list[str] = []
    warnings: list[str] = []

    if consistency == CandidateConsistency.CONFLICTING:
        rationale.append("candidate consistency conflict detected")

    elif consistency == CandidateConsistency.INSUFFICIENT:
        rationale.append("candidate information is insufficient")

    else:
        rationale.append("candidate identity and state are structurally consistent")

    if data_state == CandidateDataState.PARTIAL:
        warnings.append("candidate research context is incomplete")

    if data_state == CandidateDataState.MISSING:
        warnings.append("candidate data is missing")

    if candidate.candidate_type == CandidateType.UNKNOWN:
        warnings.append("candidate type is unresolved")

    if candidate.priority == CandidatePriority.UNKNOWN:
        warnings.append("candidate priority is unresolved")

    if disposition == CandidateDisposition.REJECT:
        rationale.append("candidate must not advance")

    elif disposition == CandidateDisposition.REVIEW:
        rationale.append("candidate requires research review")

    elif disposition == CandidateDisposition.ADVANCE:
        rationale.append("candidate may advance to the next research stage")

    return CandidateIntelligence(
        consistency=consistency,
        data_state=data_state,
        status=candidate.status,
        candidate_type=candidate.candidate_type,
        priority=candidate.priority,
        disposition=disposition,
        candidate_id=candidate.candidate_id,
        name=candidate.name,
        source_id=candidate.source,
        hypothesis_id=candidate.hypothesis_id,
        dataset_id=candidate.dataset_id,
        experiment_id=candidate.experiment_id,
        rationale=tuple(rationale),
        warnings=tuple(warnings),
    )


# ============================================================
# ASSESSMENT BUILDER
# ============================================================

def build_candidate_assessment(
    request: CandidateRequest,
) -> CandidateAssessment:

    candidate = build_candidate_reference(
        request.candidate,
        candidate_type=request.candidate_type,
        priority=request.priority,
        source=request.source,
        hypothesis=request.hypothesis,
        dataset=request.dataset,
        experiment=request.experiment,
    )

    requirements = evaluate_candidate_requirements(request)

    intelligence = build_candidate_intelligence(
        candidate,
        requirements,
    )

    source = build_candidate_source_reference(
        request.source
    )

    rationale = list(intelligence.rationale)
    warnings = list(intelligence.warnings)

    return CandidateAssessment(
        intelligence=intelligence,
        requirements=requirements,
        candidate=candidate,
        source=source,
        rationale=tuple(rationale),
        warnings=tuple(warnings),
    )
# ============================================================
# CANDIDATE LIFECYCLE CONTRACT — PART 3
# ============================================================

class CandidateActionState(str, Enum):
    NONE = "NONE"
    ADVANCE = "ADVANCE"
    REVIEW = "REVIEW"
    HOLD = "HOLD"
    REJECT = "REJECT"
    ARCHIVE = "ARCHIVE"


class CandidateContractState(str, Enum):
    VALID = "VALID"
    INCOMPLETE = "INCOMPLETE"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


@dataclass(frozen=True)
class CandidateAction:
    action: CandidateActionState
    candidate_id: str
    reason: str
    source: str = CANDIDATE_MANAGER_ENGINE


@dataclass(frozen=True)
class CandidateResult:
    request_id: str
    result_id: str

    status: CandidateStatus
    candidate_state: CandidateStatus

    consistency: CandidateConsistency
    data_state: CandidateDataState
    disposition: CandidateDisposition
    action_state: CandidateActionState

    candidate: CandidateReference
    source: Optional[CandidateSourceReference]

    rationale: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def is_valid(self) -> bool:
        return bool(
            self.request_id
            and self.result_id
            and self.candidate.candidate_id
            and self.consistency
            and self.data_state
        )

    @property
    def requires_review(self) -> bool:
        return self.disposition == CandidateDisposition.REVIEW

    @property
    def requires_hold(self) -> bool:
        return self.disposition == CandidateDisposition.HOLD

    @property
    def requires_rejection(self) -> bool:
        return self.disposition == CandidateDisposition.REJECT

    @property
    def can_advance(self) -> bool:
        return (
            self.is_valid
            and self.disposition == CandidateDisposition.ADVANCE
            and self.consistency == CandidateConsistency.CONSISTENT
            and self.data_state == CandidateDataState.COMPLETE
        )

    @property
    def is_action_request(self) -> bool:
        # Research candidate action is not a trading action.
        return False


@dataclass(frozen=True)
class CandidateContract:
    candidate_id: str
    request_id: str

    state: CandidateContractState
    result: CandidateResult

    action_state: CandidateActionState

    rationale: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def is_valid(self) -> bool:
        return (
            bool(self.candidate_id)
            and bool(self.request_id)
            and self.result.is_valid
            and self.state == CandidateContractState.VALID
        )

    @property
    def is_action_request(self) -> bool:
        return False


# ============================================================
# ACTION STATE
# ============================================================

def _cm_action_state(
    disposition: CandidateDisposition,
) -> CandidateActionState:

    mapping = {
        CandidateDisposition.ADVANCE: CandidateActionState.ADVANCE,
        CandidateDisposition.REVIEW: CandidateActionState.REVIEW,
        CandidateDisposition.HOLD: CandidateActionState.HOLD,
        CandidateDisposition.REJECT: CandidateActionState.REJECT,
        CandidateDisposition.ARCHIVE: CandidateActionState.ARCHIVE,
    }

    return mapping.get(
        disposition,
        CandidateActionState.NONE,
    )


# ============================================================
# RESULT STATUS
# ============================================================

def _cm_result_status(
    intelligence: CandidateIntelligence,
) -> CandidateStatus:

    if intelligence.consistency == CandidateConsistency.CONFLICTING:
        return CandidateStatus.INVALID

    if intelligence.data_state == CandidateDataState.MISSING:
        return CandidateStatus.INVALID

    if intelligence.status == CandidateStatus.INVALID:
        return CandidateStatus.INVALID

    return intelligence.status


# ============================================================
# RESULT BUILDER
# ============================================================

def build_candidate_result(
    request: CandidateRequest,
    assessment: CandidateAssessment,
) -> CandidateResult:

    intelligence = assessment.intelligence

    action_state = _cm_action_state(
        intelligence.disposition
    )

    status = _cm_result_status(
        intelligence
    )

    rationale = list(assessment.rationale)
    warnings = list(assessment.warnings)

    if action_state == CandidateActionState.ADVANCE:
        rationale.append(
            "candidate is structurally eligible to advance"
        )

    elif action_state == CandidateActionState.REVIEW:
        rationale.append(
            "candidate remains under research review"
        )

    elif action_state == CandidateActionState.HOLD:
        rationale.append(
            "candidate is held pending sufficient research context"
        )

    elif action_state == CandidateActionState.REJECT:
        rationale.append(
            "candidate is rejected from the current research path"
        )

    return CandidateResult(
        request_id=request.request_id,
        result_id=str(uuid4()),
        status=status,
        candidate_state=intelligence.status,
        consistency=intelligence.consistency,
        data_state=intelligence.data_state,
        disposition=intelligence.disposition,
        action_state=action_state,
        candidate=assessment.candidate,
        source=assessment.source,
        rationale=tuple(rationale),
        warnings=tuple(warnings),
    )


# ============================================================
# CONTRACT STATE
# ============================================================

def _cm_contract_state(
    result: CandidateResult,
) -> CandidateContractState:

    if not result.is_valid:
        return CandidateContractState.INVALID

    if result.consistency == CandidateConsistency.CONFLICTING:
        return CandidateContractState.BLOCKED

    if result.data_state == CandidateDataState.MISSING:
        return CandidateContractState.INCOMPLETE

    if result.data_state == CandidateDataState.PARTIAL:
        return CandidateContractState.INCOMPLETE

    if result.status == CandidateStatus.INVALID:
        return CandidateContractState.INVALID

    if result.disposition == CandidateDisposition.REJECT:
        return CandidateContractState.BLOCKED

    return CandidateContractState.VALID


# ============================================================
# CONTRACT BUILDER
# ============================================================

def build_candidate_contract(
    request: CandidateRequest,
    result: CandidateResult,
) -> CandidateContract:

    state = _cm_contract_state(result)

    rationale = list(result.rationale)
    warnings = list(result.warnings)

    if state == CandidateContractState.INCOMPLETE:
        warnings.append(
            "candidate contract is incomplete"
        )

    elif state == CandidateContractState.BLOCKED:
        warnings.append(
            "candidate contract is blocked from advancement"
        )

    elif state == CandidateContractState.INVALID:
        warnings.append(
            "candidate contract failed validation"
        )

    return CandidateContract(
        candidate_id=result.candidate.candidate_id,
        request_id=request.request_id,
        state=state,
        result=result,
        action_state=result.action_state,
        rationale=tuple(rationale),
        warnings=tuple(warnings),
    )


# ============================================================
# ADVANCEMENT SAFETY
# ============================================================

def is_candidate_safe_to_advance(
    contract: CandidateContract,
) -> bool:

    if not contract.is_valid:
        return False

    if contract.is_action_request:
        return False

    result = contract.result

    if not result.is_valid:
        return False

    if result.consistency != CandidateConsistency.CONSISTENT:
        return False

    if result.data_state != CandidateDataState.COMPLETE:
        return False

    if result.disposition != CandidateDisposition.ADVANCE:
        return False

    if result.action_state != CandidateActionState.ADVANCE:
        return False

    return True


# ============================================================
# RESULT VALIDATION
# ============================================================

def validate_candidate_result(
    result: CandidateResult,
) -> CandidateContractValidation:

    errors: list[str] = []
    warnings: list[str] = []

    if not result.request_id:
        errors.append("result request_id is required")

    if not result.result_id:
        errors.append("result_id is required")

    if not result.candidate.candidate_id:
        errors.append("candidate_id is required")

    if result.consistency == CandidateConsistency.CONFLICTING:
        warnings.append(
            "candidate consistency is conflicting"
        )

    if result.data_state == CandidateDataState.MISSING:
        warnings.append(
            "candidate data is missing"
        )

    if result.data_state == CandidateDataState.PARTIAL:
        warnings.append(
            "candidate data is incomplete"
        )

    if result.disposition == CandidateDisposition.REJECT:
        warnings.append(
            "candidate is not eligible for advancement"
        )

    if errors:
        return CandidateContractValidation(
            status=CandidateContractStatus.INVALID,
            errors=tuple(errors),
            warnings=tuple(warnings),
        )

    return CandidateContractValidation(
        status=CandidateContractStatus.VALID,
        warnings=tuple(warnings),
    )
# ============================================================
# ROBOMLM_PLUS
# app/intelligence/research/candidate_manager.py
# RESEARCH CANDIDATE MANAGEMENT — PART 4
# ENGINE + LIFECYCLE
# ============================================================

class CandidateManagerEngine:
    """
    Research Candidate Management Engine.

    Role:
        Candidate Request
            ↓
        Contract Validation
            ↓
        Candidate Assessment
            ↓
        Candidate Result
            ↓
        Candidate Contract
            ↓
        Controlled Research Lifecycle State

    Boundaries:
        - does not create trading orders
        - does not execute trades
        - does not create CAS authorization
        - does not alter D13 decision authority
        - does not recalculate Risk
        - does not invent research evidence
        - does not silently promote incomplete candidates
    """

    ENGINE_NAME = CANDIDATE_MANAGER_ENGINE
    ENGINE_VERSION = CANDIDATE_MANAGER_VERSION

    def validate_request(
        self,
        request: CandidateRequest,
    ) -> CandidateContractValidation:
        return validate_candidate_request(request)

    def _invalid_contract(
        self,
        request: CandidateRequest,
        errors: tuple[str, ...],
    ) -> CandidateContract:
        now = datetime.now(timezone.utc)

        candidate_id = _cm_text(
            _cm_read_value(request.candidate, "candidate_id", "id")
        ) or "INVALID"

        intelligence = CandidateIntelligence(
            consistency=CandidateConsistency.INSUFFICIENT,
            data_state=CandidateDataState.MISSING,
            status=CandidateStatus.INVALID,
            candidate_type=request.candidate_type,
            priority=request.priority,
            disposition=CandidateDisposition.HOLD,
            candidate_id=candidate_id,
            name="",
            source_id="",
            hypothesis_id="",
            dataset_id="",
            experiment_id="",
            rationale=("Candidate request validation failed.",),
            warnings=errors,
            source=CANDIDATE_MANAGER_ENGINE,
        )

        assessment = CandidateAssessment(
            intelligence=intelligence,
            requirements=CandidateRequirements(
                candidate_available=False,
                candidate_id_available=False,
                name_available=False,
                type_available=False,
                source_available=False,
                hypothesis_available=False,
                dataset_available=False,
                experiment_available=False,
                priority_available=False,
            ),
            candidate=None,
            source=None,
            rationale=errors,
            warnings=errors,
        )

        result = build_candidate_result(request, assessment)

        return CandidateContract(
            candidate_id=candidate_id,
            request_id=request.request_id,
            state=CandidateContractState.INVALID,
            result=result,
            action_state=CandidateActionState.NONE,
            rationale=("Invalid candidate contract.",),
            warnings=errors,
            created_at=now,
        )

    def process(
        self,
        request: CandidateRequest,
    ) -> CandidateContract:
        """
        Full candidate lifecycle.

        Fail-closed:
            Invalid input never becomes an advanceable candidate.
        """
        try:
            validation = self.validate_request(request)

            if not validation.is_valid:
                return self._invalid_contract(
                    request,
                    validation.errors,
                )

            assessment = build_candidate_assessment(request)
            result = build_candidate_result(request, assessment)

            result_validation = validate_candidate_result(result)

            if not result_validation.is_valid:
                warnings = tuple(
                    dict.fromkeys(
                        result.warnings + result_validation.errors
                    )
                )
                result = CandidateResult(
                    request_id=result.request_id,
                    result_id=result.result_id,
                    status=CandidateStatus.INVALID,
                    candidate_state=CandidateStatus.INVALID,
                    consistency=result.consistency,
                    data_state=result.data_state,
                    disposition=CandidateDisposition.HOLD,
                    action_state=CandidateActionState.NONE,
                    candidate=result.candidate,
                    source=result.source,
                    rationale=result.rationale
                    + ("Candidate result validation failed.",),
                    warnings=warnings,
                    created_at=result.created_at,
                )

            return build_candidate_contract(
                request,
                result,
            )

        except Exception as exc:
            return self._invalid_contract(
                request,
                (f"Candidate processing failed: {exc}",),
            )

    def evaluate(
        self,
        request: CandidateRequest,
    ) -> CandidateAssessment:
        """
        Read-only assessment path.

        Does not mutate candidate state.
        """
        validation = self.validate_request(request)

        if not validation.is_valid:
            requirements = CandidateRequirements(
                candidate_available=False,
                candidate_id_available=False,
                name_available=False,
                type_available=False,
                source_available=False,
                hypothesis_available=False,
                dataset_available=False,
                experiment_available=False,
                priority_available=False,
            )

            return CandidateAssessment(
                intelligence=CandidateIntelligence(
                    consistency=CandidateConsistency.INSUFFICIENT,
                    data_state=CandidateDataState.MISSING,
                    status=CandidateStatus.INVALID,
                    candidate_type=request.candidate_type,
                    priority=request.priority,
                    disposition=CandidateDisposition.HOLD,
                    candidate_id="",
                    name="",
                    source_id="",
                    hypothesis_id="",
                    dataset_id="",
                    experiment_id="",
                    rationale=("Invalid candidate request.",),
                    warnings=validation.errors,
                    source=CANDIDATE_MANAGER_ENGINE,
                ),
                requirements=requirements,
                candidate=None,
                source=None,
                rationale=validation.errors,
                warnings=validation.errors,
            )

        return build_candidate_assessment(request)

    def can_advance(
        self,
        contract: CandidateContract,
    ) -> bool:
        return is_candidate_safe_to_advance(contract)

    def candidate_status(
        self,
        contract: CandidateContract,
    ) -> CandidateStatus:
        return contract.result.status

    def candidate_disposition(
        self,
        contract: CandidateContract,
    ) -> CandidateDisposition:
        return contract.result.disposition

    def audit_summary(
        self,
        contract: CandidateContract,
    ) -> dict[str, Any]:
        result = contract.result

        return {
            "engine": self.ENGINE_NAME,
            "version": self.ENGINE_VERSION,
            "candidate_id": contract.candidate_id,
            "request_id": contract.request_id,
            "contract_state": contract.state.value,
            "contract_valid": contract.is_valid,
            "result_valid": result.is_valid,
            "status": result.status.value,
            "candidate_state": result.candidate_state.value,
            "consistency": result.consistency.value,
            "data_state": result.data_state.value,
            "disposition": result.disposition.value,
            "action_state": result.action_state.value,
            "can_advance": result.can_advance,
            "requires_review": result.requires_review,
            "requires_hold": result.requires_hold,
            "requires_rejection": result.requires_rejection,

            # Hard authority boundaries
            "candidate_execution_created": False,
            "order_created": False,
            "authorization_created": False,
            "d13_overridden": False,
            "risk_overridden": False,
            "cas_overridden": False,
        }


# ============================================================
# PUBLIC ENGINE
# ============================================================

candidate_manager_engine = CandidateManagerEngine()


# ============================================================
# PUBLIC API
# ============================================================

def manage_candidate(
    request: CandidateRequest,
) -> CandidateContract:
    return candidate_manager_engine.process(request)


def evaluate_candidate(
    request: CandidateRequest,
) -> CandidateAssessment:
    return candidate_manager_engine.evaluate(request)


def candidate_ready(
    contract: CandidateContract,
) -> bool:
    return contract.is_valid


def candidate_can_advance(
    contract: CandidateContract,
) -> bool:
    return candidate_manager_engine.can_advance(contract)


def candidate_status(
    contract: CandidateContract,
) -> CandidateStatus:
    return candidate_manager_engine.candidate_status(contract)


def candidate_disposition(
    contract: CandidateContract,
) -> CandidateDisposition:
    return candidate_manager_engine.candidate_disposition(contract)


def candidate_audit(
    contract: CandidateContract,
) -> dict[str, Any]:
    return candidate_manager_engine.audit_summary(contract)


def candidate_health_check() -> dict[str, Any]:
    return {
        "engine": CANDIDATE_MANAGER_ENGINE,
        "version": CANDIDATE_MANAGER_VERSION,
        "status": "HEALTHY",
        "contract_layer": True,
        "assessment_layer": True,
        "result_layer": True,
        "advance_gate": True,
        "fail_closed": True,

        # Research engine must remain non-executing.
        "execution_created": False,
        "order_created": False,
        "authorization_created": False,
        "d13_overridden": False,
        "risk_overridden": False,
        "cas_overridden": False,
    }


def get_candidate_manager_engine_info() -> dict[str, Any]:
    return {
        "engine": CANDIDATE_MANAGER_ENGINE,
        "version": CANDIDATE_MANAGER_VERSION,
        "role": "Research Candidate Lifecycle Management",
        "authority": "Research Lifecycle",
        "supports": (
            "candidate assessment",
            "candidate qualification",
            "candidate lifecycle state",
            "controlled advancement",
        ),
        "does_not_support": (
            "trade execution",
            "order creation",
            "CAS authorization",
            "D13 override",
            "Risk override",
        ),
    }


# Compatibility alias
CandidateManager = CandidateManagerEngine
# ============================================================
# ROBOMLM_PLUS
# app/intelligence/research/candidate_manager.py
# RESEARCH CANDIDATE MANAGEMENT — PART 5
# SERIALIZATION + INTEGRITY + EXPORTS
# ============================================================


def _cm_enum_value(value: Any) -> Any:
    """Return stable enum representation."""
    return value.value if isinstance(value, Enum) else value


def _cm_safe_dict(value: Any) -> dict[str, Any]:
    """Safely convert mappings/objects into a dictionary."""
    if value is None:
        return {}

    if isinstance(value, Mapping):
        return dict(value)

    if hasattr(value, "to_dict"):
        try:
            result = value.to_dict()
            return dict(result) if isinstance(result, Mapping) else {}
        except Exception:
            return {}

    if hasattr(value, "__dict__"):
        try:
            return dict(value.__dict__)
        except Exception:
            return {}

    return {}


def _cm_reference_to_dict(
    reference: Any,
) -> dict[str, Any]:
    if reference is None:
        return {}

    if hasattr(reference, "__dataclass_fields__"):
        return {
            key: _cm_enum_value(value)
            for key, value in reference.__dict__.items()
        }

    return _cm_safe_dict(reference)


def candidate_result_to_dict(
    result: CandidateResult,
) -> dict[str, Any]:
    """
    Stable serialization of CandidateResult.
    """
    return {
        "request_id": result.request_id,
        "result_id": result.result_id,
        "status": _cm_enum_value(result.status),
        "candidate_state": _cm_enum_value(result.candidate_state),
        "consistency": _cm_enum_value(result.consistency),
        "data_state": _cm_enum_value(result.data_state),
        "disposition": _cm_enum_value(result.disposition),
        "action_state": _cm_enum_value(result.action_state),
        "candidate": _cm_reference_to_dict(result.candidate),
        "source": _cm_reference_to_dict(result.source),
        "rationale": list(result.rationale),
        "warnings": list(result.warnings),
        "created_at": result.created_at.isoformat(),
        "is_valid": result.is_valid,
        "requires_review": result.requires_review,
        "requires_hold": result.requires_hold,
        "requires_rejection": result.requires_rejection,
        "can_advance": result.can_advance,
        "is_action_request": result.is_action_request,
    }


def candidate_manager_to_dict(
    contract: CandidateContract,
) -> dict[str, Any]:
    """
    Stable external representation of CandidateContract.
    """
    result = contract.result

    return {
        "engine": CANDIDATE_MANAGER_ENGINE,
        "version": CANDIDATE_MANAGER_VERSION,
        "candidate_id": contract.candidate_id,
        "request_id": contract.request_id,
        "state": _cm_enum_value(contract.state),
        "action_state": _cm_enum_value(contract.action_state),
        "rationale": list(contract.rationale),
        "warnings": list(contract.warnings),
        "created_at": contract.created_at.isoformat(),
        "result": candidate_result_to_dict(result),
        "contract_valid": contract.is_valid,
        "safe_to_advance": is_candidate_safe_to_advance(contract),

        # Hard safety invariants
        "execution_created": False,
        "order_created": False,
        "authorization_created": False,
        "d13_overridden": False,
        "risk_overridden": False,
        "cas_overridden": False,
    }


def validate_candidate_contract(
    contract: CandidateContract,
) -> CandidateContractValidation:
    """
    Final contract-level integrity validation.
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not contract.candidate_id:
        errors.append("Missing candidate_id.")

    if not contract.request_id:
        errors.append("Missing request_id.")

    if contract.result is None:
        errors.append("Missing candidate result.")
    else:
        result_validation = validate_candidate_result(contract.result)

        errors.extend(result_validation.errors)
        warnings.extend(result_validation.warnings)

        if contract.result.request_id != contract.request_id:
            errors.append("Contract/result request_id mismatch.")

        if contract.result.candidate is not None:
            result_candidate_id = contract.result.candidate.candidate_id

            if (
                result_candidate_id
                and contract.candidate_id
                and result_candidate_id != contract.candidate_id
            ):
                errors.append("Contract/result candidate_id mismatch.")

        if contract.result.is_action_request:
            errors.append(
                "Candidate result must not be an action request."
            )

    if contract.is_action_request:
        errors.append(
            "Candidate contract must not be an action request."
        )

    if contract.state == CandidateContractState.INVALID:
        warnings.append("Candidate contract is INVALID.")

    if contract.state == CandidateContractState.BLOCKED:
        warnings.append("Candidate advancement is blocked.")

    if contract.state == CandidateContractState.INCOMPLETE:
        warnings.append("Candidate contract is incomplete.")

    status = (
        CandidateContractStatus.VALID
        if not errors
        else CandidateContractStatus.INVALID
    )

    return CandidateContractValidation(
        status=status,
        errors=tuple(dict.fromkeys(errors)),
        warnings=tuple(dict.fromkeys(warnings)),
    )


def candidate_manager_integrity_check(
    contract: CandidateContract,
) -> dict[str, Any]:
    """
    Final integrity gate.

    This function audits the candidate lifecycle without
    creating or executing any downstream action.
    """
    validation = validate_candidate_contract(contract)

    return {
        "engine": CANDIDATE_MANAGER_ENGINE,
        "version": CANDIDATE_MANAGER_VERSION,
        "candidate_id": contract.candidate_id,
        "request_id": contract.request_id,

        "contract_state": _cm_enum_value(contract.state),
        "contract_valid": contract.is_valid,
        "validation_status": _cm_enum_value(validation.status),

        "errors": list(validation.errors),
        "warnings": list(validation.warnings),

        "candidate_status": _cm_enum_value(
            contract.result.status
        ),
        "candidate_disposition": _cm_enum_value(
            contract.result.disposition
        ),
        "candidate_consistency": _cm_enum_value(
            contract.result.consistency
        ),
        "candidate_data_state": _cm_enum_value(
            contract.result.data_state
        ),

        "can_advance": contract.result.can_advance,
        "safe_to_advance": is_candidate_safe_to_advance(
            contract
        ),

        # Research lifecycle is non-executing.
        "execution_created": False,
        "order_created": False,
        "authorization_created": False,

        # Authority protection.
        "d13_overridden": False,
        "risk_overridden": False,
        "cas_overridden": False,

        "integrity_pass": (
            validation.is_valid
            and not contract.is_action_request
        ),
    }


def verify_candidate_manager_integrity(
    contract: CandidateContract,
) -> bool:
    return bool(
        candidate_manager_integrity_check(
            contract
        )["integrity_pass"]
    )


def run_candidate_manager_health_check() -> dict[str, Any]:
    """
    Final runtime-safe health check.
    """
    health = candidate_health_check()

    health.update(
        {
            "integrity_layer": True,
            "serialization_layer": True,
            "lifecycle_engine": True,
            "safe_advance_gate": True,
        }
    )

    return health


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [
    # Constants
    "CANDIDATE_MANAGER_ENGINE",
    "CANDIDATE_MANAGER_VERSION",

    # Enums
    "CandidateStatus",
    "CandidateType",
    "CandidatePriority",
    "CandidateDecision",
    "CandidateContractStatus",
    "CandidateConsistency",
    "CandidateDataState",
    "CandidateDisposition",
    "CandidateActionState",
    "CandidateContractState",

    # Contracts / References
    "CandidateRequest",
    "CandidateReference",
    "CandidateSourceReference",
    "CandidateContractValidation",
    "CandidateRequirements",
    "CandidateIntelligence",
    "CandidateAssessment",
    "CandidateAction",
    "CandidateResult",
    "CandidateContract",

    # Builders / Validators
    "build_candidate_reference",
    "build_candidate_source_reference",
    "validate_candidate_request",
    "evaluate_candidate_requirements",
    "evaluate_candidate_data_state",
    "evaluate_candidate_consistency",
    "evaluate_candidate_disposition",
    "build_candidate_intelligence",
    "build_candidate_assessment",
    "build_candidate_result",
    "build_candidate_contract",
    "is_candidate_safe_to_advance",
    "validate_candidate_result",
    "validate_candidate_contract",

    # Engine
    "CandidateManagerEngine",
    "CandidateManager",
    "candidate_manager_engine",

    # Public API
    "manage_candidate",
    "evaluate_candidate",
    "candidate_ready",
    "candidate_can_advance",
    "candidate_status",
    "candidate_disposition",
    "candidate_audit",
    "candidate_health_check",
    "run_candidate_manager_health_check",
    "get_candidate_manager_engine_info",

    # Serialization / Integrity
    "candidate_result_to_dict",
    "candidate_manager_to_dict",
    "candidate_manager_integrity_check",
    "verify_candidate_manager_integrity",
]