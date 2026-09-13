# ============================================================
# ROBOMLM_PLUS
# app/intelligence/research/stress_testing.py
# PART 1 / 5 — FOUNDATION + CONTRACTS
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

STRESS_TESTING_ENGINE = "ROBOMLM_RESEARCH_STRESS_TESTING_ENGINE"
STRESS_TESTING_VERSION = "1.0"


# ============================================================
# ENUMS
# ============================================================

class StressTestStatus(str, Enum):
    NEW = "NEW"
    PROPOSED = "PROPOSED"
    PREPARING = "PREPARING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    ARCHIVED = "ARCHIVED"
    UNKNOWN = "UNKNOWN"


class StressTestType(str, Enum):
    DATA = "DATA"
    MARKET = "MARKET"
    REGIME = "REGIME"
    SIGNAL = "SIGNAL"
    STRATEGY = "STRATEGY"
    MODEL = "MODEL"
    FORMULA = "FORMULA"
    ENGINE = "ENGINE"
    SYSTEM = "SYSTEM"
    UNKNOWN = "UNKNOWN"


class StressTestPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class StressTestDecision(str, Enum):
    PASS = "PASS"
    CONDITIONAL = "CONDITIONAL"
    FAIL = "FAIL"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


class StressTestContractStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


# ============================================================
# REQUEST CONTRACT
# ============================================================

@dataclass(frozen=True)
class StressTestRequest:
    """
    Immutable request entering the stress-testing lifecycle.

    The engine evaluates a research artifact under a defined
    stress-test context. It does not execute trades or alter
    production decision authority.
    """

    target: Any
    stress_test_type: StressTestType = StressTestType.UNKNOWN
    scenario: Any = None
    dataset: Any = None
    candidate: Any = None
    experiment: Any = None
    hypothesis: Any = None
    validation: Any = None
    priority: StressTestPriority = StressTestPriority.MEDIUM
    metadata: Mapping[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def validate(self) -> bool:
        if self.target is None:
            return False

        if not isinstance(self.request_id, str) or not self.request_id.strip():
            return False

        if not isinstance(self.metadata, Mapping):
            return False

        return True


# ============================================================
# TARGET REFERENCE
# ============================================================

@dataclass(frozen=True)
class StressTestReference:
    """Normalized reference to the object being stress-tested."""

    target_id: str
    name: str
    target_type: StressTestType
    status: StressTestStatus
    priority: StressTestPriority

    scenario_id: Optional[str] = None
    dataset_id: Optional[str] = None
    candidate_id: Optional[str] = None
    experiment_id: Optional[str] = None
    hypothesis_id: Optional[str] = None
    validation_id: Optional[str] = None

    raw_target: Any = None


# ============================================================
# SCENARIO REFERENCE
# ============================================================

@dataclass(frozen=True)
class StressScenarioReference:
    """Reference to the stress condition/scenario."""

    scenario_id: str
    name: str
    scenario_type: str = "UNKNOWN"
    severity: str = "UNKNOWN"
    description: str = ""
    raw_scenario: Any = None


# ============================================================
# CONTRACT VALIDATION
# ============================================================

@dataclass(frozen=True)
class StressTestContractValidation:
    """Validation result for an incoming stress-test request."""

    valid: bool
    target_available: bool
    scenario_available: bool
    type_defined: bool
    priority_defined: bool
    metadata_valid: bool

    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:
        return self.valid


# ============================================================
# SAFE READ HELPERS
# ============================================================

def _st_read_value(
    obj: Any,
    *names: str,
    default: Any = None,
) -> Any:
    """Read a field safely from mapping/object input."""

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


def _st_text(
    value: Any,
    default: str = "",
) -> str:
    """Normalize arbitrary values into safe text."""

    if value is None:
        return default

    try:
        text = str(value).strip()
    except Exception:
        return default

    return text if text else default


def _st_enum(
    enum_cls: type[Enum],
    value: Any,
    default: Enum,
) -> Enum:
    """Safely normalize an enum value."""

    if isinstance(value, enum_cls):
        return value

    if value is None:
        return default

    raw = getattr(value, "value", value)

    try:
        return enum_cls(raw)
    except (ValueError, TypeError):
        pass

    try:
        return enum_cls[str(raw).upper()]
    except (KeyError, TypeError):
        return default


# ============================================================
# ID EXTRACTION
# ============================================================

def _st_component_id(
    value: Any,
    *names: str,
) -> Optional[str]:
    """Extract an optional stable component identifier."""

    if value is None:
        return None

    identifier = _st_read_value(
        value,
        *names,
        "id",
        "uuid",
        "key",
        default=None,
    )

    if identifier is None:
        return None

    text = _st_text(identifier)

    return text or None


# ============================================================
# REFERENCE BUILDER
# ============================================================

def build_stress_test_reference(
    request: StressTestRequest,
) -> StressTestReference:
    """Build a normalized stress-test target reference."""

    target = request.target

    target_id = _st_component_id(
        target,
        "target_id",
        "stress_test_id",
        "id",
        "research_id",
        "candidate_id",
        "experiment_id",
        "hypothesis_id",
    )

    if not target_id:
        target_id = request.request_id

    name = _st_text(
        _st_read_value(
            target,
            "name",
            "title",
            "target_name",
            "research_name",
            default=None,
        ),
        default=target_id,
    )

    target_type = _st_enum(
        StressTestType,
        _st_read_value(
            target,
            "stress_test_type",
            "target_type",
            "type",
            default=request.stress_test_type,
        ),
        request.stress_test_type,
    )

    status = _st_enum(
        StressTestStatus,
        _st_read_value(
            target,
            "status",
            "state",
            default=StressTestStatus.NEW,
        ),
        StressTestStatus.NEW,
    )

    priority = _st_enum(
        StressTestPriority,
        _st_read_value(
            target,
            "priority",
            default=request.priority,
        ),
        request.priority,
    )

    return StressTestReference(
        target_id=target_id,
        name=name,
        target_type=target_type,
        status=status,
        priority=priority,
        scenario_id=_st_component_id(
            request.scenario,
            "scenario_id",
            "id",
        ),
        dataset_id=_st_component_id(
            request.dataset,
            "dataset_id",
            "id",
        ),
        candidate_id=_st_component_id(
            request.candidate,
            "candidate_id",
            "id",
        ),
        experiment_id=_st_component_id(
            request.experiment,
            "experiment_id",
            "id",
        ),
        hypothesis_id=_st_component_id(
            request.hypothesis,
            "hypothesis_id",
            "id",
        ),
        validation_id=_st_component_id(
            request.validation,
            "validation_id",
            "id",
        ),
        raw_target=target,
    )


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_stress_test_request(
    request: Any,
) -> StressTestContractValidation:
    """Validate the external stress-test request contract."""

    if not isinstance(request, StressTestRequest):
        return StressTestContractValidation(
            valid=False,
            target_available=False,
            scenario_available=False,
            type_defined=False,
            priority_defined=False,
            metadata_valid=False,
            errors=("request must be StressTestRequest",),
        )

    target_available = request.target is not None
    scenario_available = request.scenario is not None
    type_defined = (
        request.stress_test_type != StressTestType.UNKNOWN
    )
    priority_defined = (
        request.priority != StressTestPriority.UNKNOWN
    )
    metadata_valid = isinstance(request.metadata, Mapping)

    errors: list[str] = []
    warnings: list[str] = []

    if not target_available:
        errors.append("target is required")

    if not request.request_id.strip():
        errors.append("request_id is required")

    if not type_defined:
        warnings.append("stress_test_type is UNKNOWN")

    if not scenario_available:
        warnings.append("stress scenario is not provided")

    if not priority_defined:
        warnings.append("priority is UNKNOWN")

    if not metadata_valid:
        errors.append("metadata must be a Mapping")

    valid = len(errors) == 0

    return StressTestContractValidation(
        valid=valid,
        target_available=target_available,
        scenario_available=scenario_available,
        type_defined=type_defined,
        priority_defined=priority_defined,
        metadata_valid=metadata_valid,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )
# ============================================================
# PART 2 / 5 — REQUIREMENTS + ASSESSMENT INTELLIGENCE
# ============================================================


# ============================================================
# ASSESSMENT ENUMS
# ============================================================

class StressDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    UNKNOWN = "UNKNOWN"


class StressConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONFLICTING = "CONFLICTING"
    INSUFFICIENT = "INSUFFICIENT"
    UNKNOWN = "UNKNOWN"


class StressReadiness(str, Enum):
    READY = "READY"
    CONDITIONAL = "CONDITIONAL"
    NOT_READY = "NOT_READY"
    UNKNOWN = "UNKNOWN"


class StressSeverity(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


# ============================================================
# REQUIREMENTS
# ============================================================

@dataclass(frozen=True)
class StressTestRequirements:
    """Normalized requirements for a stress-test evaluation."""

    target_available: bool
    scenario_available: bool
    dataset_available: bool
    candidate_available: bool
    experiment_available: bool
    hypothesis_available: bool
    validation_available: bool

    test_type_defined: bool
    measurable: bool
    reproducible: bool

    data_state: StressDataState
    consistency: StressConsistency
    readiness: StressReadiness

    completeness_score: float
    warnings: tuple[str, ...] = ()


# ============================================================
# ASSESSMENT
# ============================================================

@dataclass(frozen=True)
class StressTestAssessment:
    """Intelligence produced by the stress-test assessment layer."""

    decision: StressTestDecision
    readiness: StressReadiness
    data_state: StressDataState
    consistency: StressConsistency
    severity: StressSeverity

    confidence_score: float
    completeness_score: float

    strengths: tuple[str, ...] = ()
    weaknesses: tuple[str, ...] = ()
    rationale: str = ""


# ============================================================
# BOOLEAN / VALUE HELPERS
# ============================================================

def _st_bool(
    value: Any,
    default: bool = False,
) -> bool:
    """Safely normalize a value into boolean semantics."""

    if value is None:
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        text = value.strip().lower()

        if text in {
            "true",
            "1",
            "yes",
            "y",
            "pass",
            "passed",
            "valid",
            "available",
            "complete",
        }:
            return True

        if text in {
            "false",
            "0",
            "no",
            "n",
            "fail",
            "failed",
            "invalid",
            "missing",
            "incomplete",
        }:
            return False

    try:
        return bool(value)
    except Exception:
        return default


def _st_conflict_detected(target: Any, metadata: Mapping[str, Any]) -> bool:
    """Detect explicitly supplied conflict information."""

    values = [
        _st_read_value(
            target,
            "conflict",
            "conflicts",
            "inconsistent",
            default=None,
        ),
        _st_read_value(
            target,
            "consistency",
            default=None,
        ),
        metadata.get("conflict"),
        metadata.get("conflicts"),
        metadata.get("inconsistent"),
        metadata.get("consistency"),
    ]

    for value in values:
        if isinstance(value, str):
            text = value.strip().upper()
            if text in {
                "CONFLICTING",
                "CONFLICT",
                "INCONSISTENT",
            }:
                return True

        if isinstance(value, bool) and value:
            return True

    return False


# ============================================================
# DATA STATE
# ============================================================

def evaluate_stress_data_state(
    requirements: StressTestRequirements,
) -> StressDataState:
    """Evaluate availability of the required stress-test inputs."""

    required = (
        requirements.target_available,
        requirements.scenario_available,
        requirements.dataset_available,
        requirements.test_type_defined,
        requirements.measurable,
    )

    available = sum(1 for item in required if item)

    if available == len(required):
        return StressDataState.COMPLETE

    if available == 0:
        return StressDataState.MISSING

    return StressDataState.PARTIAL


# ============================================================
# CONSISTENCY
# ============================================================

def evaluate_stress_consistency(
    target: Any,
    metadata: Mapping[str, Any],
) -> StressConsistency:
    """Evaluate only explicitly supplied consistency information."""

    if _st_conflict_detected(target, metadata):
        return StressConsistency.CONFLICTING

    explicit = _st_read_value(
        target,
        "consistency",
        default=metadata.get("consistency"),
    )

    if explicit is not None:
        text = _st_text(explicit).upper()

        if text in {
            "CONSISTENT",
            "PASS",
            "ALIGNED",
            "VALID",
        }:
            return StressConsistency.CONSISTENT

        if text in {
            "INSUFFICIENT",
            "UNKNOWN",
            "UNAVAILABLE",
        }:
            return StressConsistency.INSUFFICIENT

    return StressConsistency.UNKNOWN


# ============================================================
# REQUIREMENT EVALUATION
# ============================================================

def evaluate_stress_test_requirements(
    request: StressTestRequest,
    reference: Optional[StressTestReference] = None,
) -> StressTestRequirements:
    """Build normalized stress-test requirements."""

    target = request.target
    metadata = dict(request.metadata)

    target_available = target is not None
    scenario_available = request.scenario is not None
    dataset_available = request.dataset is not None
    candidate_available = request.candidate is not None
    experiment_available = request.experiment is not None
    hypothesis_available = request.hypothesis is not None
    validation_available = request.validation is not None

    test_type_defined = (
        request.stress_test_type != StressTestType.UNKNOWN
    )

    measurable = _st_bool(
        _st_read_value(
            target,
            "measurable",
            "measurement_available",
            "metric_available",
            default=metadata.get("measurable"),
        ),
        default=(
            dataset_available
            or validation_available
        ),
    )

    reproducible = _st_bool(
        _st_read_value(
            target,
            "reproducible",
            "reproducibility",
            default=metadata.get("reproducible"),
        ),
        default=(
            dataset_available
            and scenario_available
        ),
    )

    consistency = evaluate_stress_consistency(
        target,
        metadata,
    )

    components = (
        target_available,
        scenario_available,
        dataset_available,
        test_type_defined,
        measurable,
        reproducible,
    )

    completeness_score = round(
        (sum(1 for item in components if item) / len(components))
        * 100.0,
        2,
    )

    temporary = StressTestRequirements(
        target_available=target_available,
        scenario_available=scenario_available,
        dataset_available=dataset_available,
        candidate_available=candidate_available,
        experiment_available=experiment_available,
        hypothesis_available=hypothesis_available,
        validation_available=validation_available,
        test_type_defined=test_type_defined,
        measurable=measurable,
        reproducible=reproducible,
        data_state=StressDataState.UNKNOWN,
        consistency=consistency,
        readiness=StressReadiness.UNKNOWN,
        completeness_score=completeness_score,
        warnings=(),
    )

    data_state = evaluate_stress_data_state(temporary)

    warnings: list[str] = []

    if not scenario_available:
        warnings.append("stress scenario is not provided")

    if not dataset_available:
        warnings.append("dataset is not provided")

    if not measurable:
        warnings.append("measurable evaluation criteria are unavailable")

    if not reproducible:
        warnings.append("reproducibility criteria are unavailable")

    if consistency == StressConsistency.CONFLICTING:
        warnings.append("explicit stress-test conflict detected")

    if not test_type_defined:
        warnings.append("stress-test type is UNKNOWN")

    if completeness_score >= 80.0:
        readiness = StressReadiness.READY
    elif completeness_score >= 50.0:
        readiness = StressReadiness.CONDITIONAL
    else:
        readiness = StressReadiness.NOT_READY

    if consistency == StressConsistency.CONFLICTING:
        readiness = StressReadiness.NOT_READY

    return StressTestRequirements(
        target_available=target_available,
        scenario_available=scenario_available,
        dataset_available=dataset_available,
        candidate_available=candidate_available,
        experiment_available=experiment_available,
        hypothesis_available=hypothesis_available,
        validation_available=validation_available,
        test_type_defined=test_type_defined,
        measurable=measurable,
        reproducible=reproducible,
        data_state=data_state,
        consistency=consistency,
        readiness=readiness,
        completeness_score=completeness_score,
        warnings=tuple(warnings),
    )


# ============================================================
# READINESS
# ============================================================

def evaluate_stress_readiness(
    requirements: StressTestRequirements,
) -> StressReadiness:
    """Determine whether the stress-test can meaningfully proceed."""

    if requirements.consistency == StressConsistency.CONFLICTING:
        return StressReadiness.NOT_READY

    if requirements.data_state == StressDataState.MISSING:
        return StressReadiness.NOT_READY

    if not requirements.target_available:
        return StressReadiness.NOT_READY

    if not requirements.scenario_available:
        return StressReadiness.CONDITIONAL

    if not requirements.test_type_defined:
        return StressReadiness.CONDITIONAL

    if requirements.completeness_score >= 80.0:
        return StressReadiness.READY

    if requirements.completeness_score >= 50.0:
        return StressReadiness.CONDITIONAL

    return StressReadiness.NOT_READY


# ============================================================
# SEVERITY
# ============================================================

def evaluate_stress_severity(
    request: StressTestRequest,
    requirements: StressTestRequirements,
) -> StressSeverity:
    """
    Determine supplied stress severity.

    No severity formula is invented here. Explicit source values
    are preferred; otherwise UNKNOWN is retained.
    """

    target = request.target
    metadata = request.metadata

    raw = _st_read_value(
        target,
        "severity",
        "stress_severity",
        default=metadata.get("severity"),
    )

    if raw is None:
        return StressSeverity.UNKNOWN

    text = _st_text(raw).upper()

    mapping = {
        "LOW": StressSeverity.LOW,
        "MODERATE": StressSeverity.MODERATE,
        "MEDIUM": StressSeverity.MODERATE,
        "HIGH": StressSeverity.HIGH,
        "CRITICAL": StressSeverity.CRITICAL,
    }

    return mapping.get(
        text,
        StressSeverity.UNKNOWN,
    )


# ============================================================
# CONFIDENCE
# ============================================================

def calculate_stress_confidence(
    requirements: StressTestRequirements,
) -> float:
    """
    Calculate structural confidence from contract completeness.

    This is NOT a research-performance score. It only measures
    availability/quality of stress-test inputs.
    """

    score = requirements.completeness_score

    if requirements.consistency == StressConsistency.CONFLICTING:
        score -= 30.0
    elif requirements.consistency == StressConsistency.CONSISTENT:
        score += 5.0

    if requirements.data_state == StressDataState.MISSING:
        score -= 20.0

    return round(
        max(0.0, min(100.0, score)),
        2,
    )


# ============================================================
# DECISION
# ============================================================

def determine_stress_test_decision(
    requirements: StressTestRequirements,
    confidence_score: float,
) -> StressTestDecision:
    """Determine lifecycle decision from contract state."""

    if requirements.consistency == StressConsistency.CONFLICTING:
        return StressTestDecision.BLOCK

    if requirements.data_state == StressDataState.MISSING:
        return StressTestDecision.BLOCK

    if not requirements.target_available:
        return StressTestDecision.BLOCK

    if requirements.readiness == StressReadiness.NOT_READY:
        return StressTestDecision.REVIEW

    if confidence_score >= 80.0 and (
        requirements.readiness == StressReadiness.READY
    ):
        return StressTestDecision.PASS

    if confidence_score >= 50.0:
        return StressTestDecision.CONDITIONAL

    return StressTestDecision.REVIEW


# ============================================================
# ASSESSMENT BUILDER
# ============================================================

def build_stress_test_assessment(
    request: StressTestRequest,
    requirements: StressTestRequirements,
) -> StressTestAssessment:
    """Build the complete stress-test assessment."""

    readiness = evaluate_stress_readiness(requirements)

    confidence = calculate_stress_confidence(
        requirements,
    )

    decision = determine_stress_test_decision(
        requirements,
        confidence,
    )

    severity = evaluate_stress_severity(
        request,
        requirements,
    )

    strengths: list[str] = []
    weaknesses: list[str] = []

    if requirements.target_available:
        strengths.append("target available")

    if requirements.scenario_available:
        strengths.append("stress scenario available")

    if requirements.dataset_available:
        strengths.append("dataset available")

    if requirements.measurable:
        strengths.append("measurable evaluation criteria available")

    if requirements.reproducible:
        strengths.append("reproducibility criteria available")

    if not requirements.scenario_available:
        weaknesses.append("missing stress scenario")

    if not requirements.dataset_available:
        weaknesses.append("missing dataset")

    if not requirements.measurable:
        weaknesses.append("missing measurable criteria")

    if not requirements.reproducible:
        weaknesses.append("reproducibility not established")

    if requirements.consistency == StressConsistency.CONFLICTING:
        weaknesses.append("explicit consistency conflict")

    rationale = (
        f"Stress-test readiness={readiness.value}; "
        f"data_state={requirements.data_state.value}; "
        f"completeness={requirements.completeness_score:.2f}; "
        f"confidence={confidence:.2f}; "
        f"decision={decision.value}."
    )

    return StressTestAssessment(
        decision=decision,
        readiness=readiness,
        data_state=requirements.data_state,
        consistency=requirements.consistency,
        severity=severity,
        confidence_score=confidence,
        completeness_score=requirements.completeness_score,
        strengths=tuple(strengths),
        weaknesses=tuple(weaknesses),
        rationale=rationale,
    )
# ============================================================
# PART 3 / 5 — RESULT + CONTRACT + ENGINE
# ============================================================


# ============================================================
# RESULT STATUS
# ============================================================

class StressTestResultStatus(str, Enum):
    PASS = "PASS"
    CONDITIONAL = "CONDITIONAL"
    REVIEW = "REVIEW"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    INVALID = "INVALID"


class StressTestContractState(str, Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


# ============================================================
# RESULT
# ============================================================

@dataclass(frozen=True)
class StressTestResult:
    """Immutable result produced by the stress-test engine."""

    request_id: str
    result_id: str
    status: StressTestResultStatus

    target: StressTestReference
    requirements: StressTestRequirements
    assessment: StressTestAssessment

    rationale: str = ""
    warnings: tuple[str, ...] = ()
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def is_valid(self) -> bool:
        return (
            bool(self.request_id)
            and bool(self.result_id)
            and self.target is not None
            and self.requirements is not None
            and self.assessment is not None
            and self.status != StressTestResultStatus.INVALID
        )

    @property
    def passed(self) -> bool:
        return (
            self.is_valid
            and self.status == StressTestResultStatus.PASS
            and self.assessment.decision == StressTestDecision.PASS
        )

    @property
    def is_conditional(self) -> bool:
        return (
            self.status == StressTestResultStatus.CONDITIONAL
        )

    @property
    def requires_review(self) -> bool:
        return (
            self.status == StressTestResultStatus.REVIEW
            or self.assessment.decision
            == StressTestDecision.REVIEW
        )

    @property
    def is_blocked(self) -> bool:
        return (
            self.status == StressTestResultStatus.BLOCKED
            or self.assessment.decision
            == StressTestDecision.BLOCK
        )

    @property
    def is_action_request(self) -> bool:
        return False


# ============================================================
# CONTRACT
# ============================================================

@dataclass(frozen=True)
class StressTestContract:
    """Stable contract surrounding a stress-test result."""

    request_id: str
    contract_id: str

    state: StressTestContractState
    result: StressTestResult

    rationale: str = ""
    warnings: tuple[str, ...] = ()
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def is_valid(self) -> bool:
        return (
            bool(self.request_id)
            and bool(self.contract_id)
            and self.result is not None
            and self.state != StressTestContractState.INVALID
            and self.result.is_valid
        )

    @property
    def passed(self) -> bool:
        return self.is_valid and self.result.passed

    @property
    def is_action_request(self) -> bool:
        return False


# ============================================================
# RESULT STATUS DETERMINATION
# ============================================================

def determine_stress_test_result_status(
    assessment: StressTestAssessment,
) -> StressTestResultStatus:
    """Map assessment decision into the external result status."""

    if assessment.decision == StressTestDecision.PASS:
        return StressTestResultStatus.PASS

    if assessment.decision == StressTestDecision.CONDITIONAL:
        return StressTestResultStatus.CONDITIONAL

    if assessment.decision == StressTestDecision.REVIEW:
        return StressTestResultStatus.REVIEW

    if assessment.decision == StressTestDecision.BLOCK:
        return StressTestResultStatus.BLOCKED

    if assessment.decision == StressTestDecision.FAIL:
        return StressTestResultStatus.FAILED

    return StressTestResultStatus.INVALID


# ============================================================
# RESULT BUILDER
# ============================================================

def build_stress_test_result(
    request: StressTestRequest,
    reference: StressTestReference,
    requirements: StressTestRequirements,
    assessment: StressTestAssessment,
) -> StressTestResult:
    """Build immutable stress-test result."""

    status = determine_stress_test_result_status(
        assessment,
    )

    return StressTestResult(
        request_id=request.request_id,
        result_id=str(uuid4()),
        status=status,
        target=reference,
        requirements=requirements,
        assessment=assessment,
        rationale=assessment.rationale,
        warnings=requirements.warnings,
    )


# ============================================================
# CONTRACT STATE
# ============================================================

def determine_stress_test_contract_state(
    result: StressTestResult,
) -> StressTestContractState:
    """Determine contract state from the generated result."""

    if result is None:
        return StressTestContractState.INVALID

    if not result.is_valid:
        return StressTestContractState.INVALID

    if result.is_blocked:
        return StressTestContractState.BLOCKED

    if result.status in {
        StressTestResultStatus.PASS,
        StressTestResultStatus.CONDITIONAL,
        StressTestResultStatus.REVIEW,
    }:
        return StressTestContractState.COMPLETE

    if result.status == StressTestResultStatus.FAILED:
        return StressTestContractState.BLOCKED

    return StressTestContractState.INCOMPLETE


# ============================================================
# CONTRACT BUILDER
# ============================================================

def build_stress_test_contract(
    request: StressTestRequest,
    result: StressTestResult,
) -> StressTestContract:
    """Build the stable stress-test contract."""

    state = determine_stress_test_contract_state(
        result,
    )

    return StressTestContract(
        request_id=request.request_id,
        contract_id=str(uuid4()),
        state=state,
        result=result,
        rationale=result.rationale,
        warnings=result.warnings,
    )


# ============================================================
# ENGINE
# ============================================================

class StressTestingEngine:
    """
    Research stress-testing lifecycle engine.

    This engine evaluates stress-test readiness and contract state.
    It does not execute trades, orders, positions, or production
    actions.
    """

    engine_name = STRESS_TESTING_ENGINE
    version = STRESS_TESTING_VERSION

    def validate_request(
        self,
        request: Any,
    ) -> StressTestContractValidation:
        return validate_stress_test_request(request)

    def _invalid_result(
        self,
        request: StressTestRequest,
        validation: StressTestContractValidation,
    ) -> tuple[StressTestResult, StressTestContract]:

        reference = StressTestReference(
            target_id=request.request_id,
            name="INVALID",
            target_type=StressTestType.UNKNOWN,
            status=StressTestStatus.INVALID
            if hasattr(StressTestStatus, "INVALID")
            else StressTestStatus.UNKNOWN,
            priority=request.priority,
        )

        requirements = StressTestRequirements(
            target_available=validation.target_available,
            scenario_available=validation.scenario_available,
            dataset_available=False,
            candidate_available=False,
            experiment_available=False,
            hypothesis_available=False,
            validation_available=False,
            test_type_defined=validation.type_defined,
            measurable=False,
            reproducible=False,
            data_state=StressDataState.MISSING,
            consistency=StressConsistency.UNKNOWN,
            readiness=StressReadiness.NOT_READY,
            completeness_score=0.0,
            warnings=validation.warnings,
        )

        assessment = StressTestAssessment(
            decision=StressTestDecision.BLOCK,
            readiness=StressReadiness.NOT_READY,
            data_state=StressDataState.MISSING,
            consistency=StressConsistency.UNKNOWN,
            severity=StressSeverity.UNKNOWN,
            confidence_score=0.0,
            completeness_score=0.0,
            weaknesses=validation.errors,
            rationale="Invalid stress-test request contract.",
        )

        result = StressTestResult(
            request_id=request.request_id,
            result_id=str(uuid4()),
            status=StressTestResultStatus.INVALID,
            target=reference,
            requirements=requirements,
            assessment=assessment,
            rationale=assessment.rationale,
            warnings=validation.warnings,
        )

        contract = StressTestContract(
            request_id=request.request_id,
            contract_id=str(uuid4()),
            state=StressTestContractState.INVALID,
            result=result,
            rationale=assessment.rationale,
            warnings=validation.warnings,
        )

        return result, contract

    def evaluate(
        self,
        request: StressTestRequest,
    ) -> StressTestContract:

        validation = self.validate_request(request)

        if not validation.valid:
            return self._invalid_result(
                request,
                validation,
            )[1]

        reference = build_stress_test_reference(
            request,
        )

        requirements = evaluate_stress_test_requirements(
            request,
            reference,
        )

        assessment = build_stress_test_assessment(
            request,
            requirements,
        )

        result = build_stress_test_result(
            request,
            reference,
            requirements,
            assessment,
        )

        return build_stress_test_contract(
            request,
            result,
        )


# ============================================================
# ENGINE INSTANCE
# ============================================================

stress_testing_engine = StressTestingEngine()


# ============================================================
# PUBLIC APIs
# ============================================================

def evaluate_stress_test(
    request: StressTestRequest,
) -> StressTestContract:
    return stress_testing_engine.evaluate(request)


def analyze_stress_test(
    request: StressTestRequest,
) -> StressTestContract:
    return stress_testing_engine.evaluate(request)


def review_stress_test(
    request: StressTestRequest,
) -> StressTestContract:
    return stress_testing_engine.evaluate(request)
# ============================================================
# PART 4 / 5 — VALIDATION + LIFECYCLE + SAFETY + HEALTH
# ============================================================


# ============================================================
# RESULT VALIDATION
# ============================================================

def validate_stress_test_result(
    result: Any,
) -> bool:
    """Validate the generated stress-test result contract."""

    if not isinstance(result, StressTestResult):
        return False

    if not result.request_id or not result.result_id:
        return False

    if result.target is None:
        return False

    if result.requirements is None:
        return False

    if result.assessment is None:
        return False

    if not 0.0 <= result.assessment.confidence_score <= 100.0:
        return False

    if not 0.0 <= result.assessment.completeness_score <= 100.0:
        return False

    return result.is_valid


# ============================================================
# CONTRACT VALIDATION
# ============================================================

def validate_stress_test_contract(
    contract: Any,
) -> bool:
    """Validate the complete stress-test contract."""

    if not isinstance(contract, StressTestContract):
        return False

    if not contract.request_id or not contract.contract_id:
        return False

    if contract.result is None:
        return False

    if not validate_stress_test_result(contract.result):
        return False

    if contract.state == StressTestContractState.INVALID:
        return False

    return contract.is_valid


# ============================================================
# READINESS
# ============================================================

def stress_test_ready(
    contract: Any,
) -> bool:
    """
    Strict readiness gate.

    PASS means the stress-test contract is structurally complete
    and has passed the assessment gate. It does not mean that a
    production action is authorized.
    """

    if not validate_stress_test_contract(contract):
        return False

    result = contract.result
    requirements = result.requirements
    assessment = result.assessment

    return (
        result.passed
        and requirements.data_state
        == StressDataState.COMPLETE
        and requirements.readiness
        == StressReadiness.READY
        and requirements.consistency
        != StressConsistency.CONFLICTING
        and requirements.target_available
        and requirements.scenario_available
        and requirements.test_type_defined
        and requirements.measurable
        and requirements.reproducible
        and assessment.confidence_score >= 80.0
        and assessment.decision
        == StressTestDecision.PASS
    )


def stress_test_can_advance(
    contract: Any,
) -> bool:
    """Return whether the research lifecycle may advance."""

    if not validate_stress_test_contract(contract):
        return False

    result = contract.result

    return (
        stress_test_ready(contract)
        or (
            result.is_conditional
            and result.requirements.readiness
            == StressReadiness.CONDITIONAL
        )
    )


# ============================================================
# ACCESSORS
# ============================================================

def stress_test_status(
    contract: Any,
) -> StressTestStatus:
    if not validate_stress_test_contract(contract):
        return StressTestStatus.UNKNOWN

    return contract.result.target.status


def stress_test_decision(
    contract: Any,
) -> StressTestDecision:
    if not validate_stress_test_contract(contract):
        return StressTestDecision.UNKNOWN

    return contract.result.assessment.decision


def stress_test_readiness(
    contract: Any,
) -> StressReadiness:
    if not validate_stress_test_contract(contract):
        return StressReadiness.UNKNOWN

    return contract.result.assessment.readiness


def stress_test_confidence(
    contract: Any,
) -> float:
    if not validate_stress_test_contract(contract):
        return 0.0

    return contract.result.assessment.confidence_score


def stress_test_severity(
    contract: Any,
) -> StressSeverity:
    if not validate_stress_test_contract(contract):
        return StressSeverity.UNKNOWN

    return contract.result.assessment.severity


def stress_test_completeness(
    contract: Any,
) -> float:
    if not validate_stress_test_contract(contract):
        return 0.0

    return contract.result.assessment.completeness_score


# ============================================================
# AUDIT
# ============================================================

def stress_test_audit(
    contract: Any,
) -> dict[str, Any]:
    """Return a non-mutating audit snapshot."""

    if not validate_stress_test_contract(contract):
        return {
            "valid": False,
            "engine": STRESS_TESTING_ENGINE,
            "version": STRESS_TESTING_VERSION,
        }

    result = contract.result
    requirements = result.requirements
    assessment = result.assessment

    return {
        "valid": True,
        "engine": STRESS_TESTING_ENGINE,
        "version": STRESS_TESTING_VERSION,
        "request_id": result.request_id,
        "result_id": result.result_id,
        "contract_id": contract.contract_id,
        "target_id": result.target.target_id,
        "target_name": result.target.name,
        "target_type": result.target.target_type.value,
        "status": result.status.value,
        "decision": assessment.decision.value,
        "readiness": assessment.readiness.value,
        "data_state": assessment.data_state.value,
        "consistency": assessment.consistency.value,
        "severity": assessment.severity.value,
        "confidence_score": assessment.confidence_score,
        "completeness_score": assessment.completeness_score,
        "passed": result.passed,
        "can_advance": stress_test_can_advance(contract),
        "is_action_request": result.is_action_request,
        "rationale": result.rationale,
        "warnings": list(result.warnings),
    }


# ============================================================
# SAFETY BOUNDARIES
# ============================================================

def stress_test_is_safe(
    contract: Any,
) -> bool:
    """
    Structural safety check.

    Stress testing remains research intelligence only.
    """

    if not validate_stress_test_contract(contract):
        return False

    return (
        contract.result.is_action_request is False
        and contract.result.assessment.decision
        != StressTestDecision.BLOCK
    )


def stress_test_execution_allowed(
    contract: Any = None,
) -> bool:
    """Stress-testing never authorizes execution."""
    return False


def stress_test_trade_allowed(
    contract: Any = None,
) -> bool:
    """Stress-testing never authorizes a trade."""
    return False


def stress_test_order_allowed(
    contract: Any = None,
) -> bool:
    """Stress-testing never authorizes an order."""
    return False


def stress_test_position_allowed(
    contract: Any = None,
) -> bool:
    """Stress-testing never authorizes a position change."""
    return False


def stress_test_authorization_allowed(
    contract: Any = None,
) -> bool:
    """Stress-testing never grants authorization."""
    return False


# ============================================================
# AUTHORITY OVERRIDE PROTECTION
# ============================================================

def stress_test_can_override_d13(
    contract: Any = None,
) -> bool:
    return False


def stress_test_can_override_risk(
    contract: Any = None,
) -> bool:
    return False


def stress_test_can_override_cas(
    contract: Any = None,
) -> bool:
    return False


# ============================================================
# ENGINE INFORMATION
# ============================================================

def get_stress_testing_engine_info() -> dict[str, Any]:
    """Return static engine information."""

    return {
        "engine": STRESS_TESTING_ENGINE,
        "version": STRESS_TESTING_VERSION,
        "engine_class": StressTestingEngine.__name__,
        "instance_available": stress_testing_engine is not None,
        "research_scope": True,
        "execution_scope": False,
        "trade_scope": False,
        "order_scope": False,
        "position_scope": False,
        "authorization_scope": False,
        "d13_override": False,
        "risk_override": False,
        "cas_override": False,
    }


# ============================================================
# HEALTH CHECK
# ============================================================

def stress_testing_health_check() -> dict[str, Any]:
    """Run structural health checks for the stress-testing engine."""

    checks = {
        "engine_constant": bool(STRESS_TESTING_ENGINE),
        "version_constant": bool(STRESS_TESTING_VERSION),
        "engine_instance": stress_testing_engine is not None,
        "request_model": StressTestRequest is not None,
        "reference_model": StressTestReference is not None,
        "scenario_reference_model": StressScenarioReference is not None,
        "requirements_model": StressTestRequirements is not None,
        "assessment_model": StressTestAssessment is not None,
        "result_model": StressTestResult is not None,
        "contract_model": StressTestContract is not None,
        "request_validator": callable(
            validate_stress_test_request
        ),
        "result_validator": callable(
            validate_stress_test_result
        ),
        "contract_validator": callable(
            validate_stress_test_contract
        ),
        "audit_function": callable(
            stress_test_audit
        ),
        "safety_function": callable(
            stress_test_is_safe
        ),
        "execution_disabled": (
            stress_test_execution_allowed() is False
        ),
        "trade_disabled": (
            stress_test_trade_allowed() is False
        ),
        "order_disabled": (
            stress_test_order_allowed() is False
        ),
        "position_disabled": (
            stress_test_position_allowed() is False
        ),
        "authorization_disabled": (
            stress_test_authorization_allowed() is False
        ),
        "d13_override_disabled": (
            stress_test_can_override_d13() is False
        ),
        "risk_override_disabled": (
            stress_test_can_override_risk() is False
        ),
        "cas_override_disabled": (
            stress_test_can_override_cas() is False
        ),
    }

    passed = all(checks.values())

    return {
        "engine": STRESS_TESTING_ENGINE,
        "version": STRESS_TESTING_VERSION,
        "health": "PASS" if passed else "FAIL",
        "passed": passed,
        "checks": checks,
    }


def run_stress_testing_health_check() -> dict[str, Any]:
    """Public health-check entry point."""
    return stress_testing_health_check()
# ============================================================
# PART 5 / 5 — SERIALIZATION + INTEGRITY + EXPORTS
# ============================================================


# ============================================================
# SERIALIZATION HELPERS
# ============================================================

def _st_enum_value(value: Any) -> Any:
    """Return enum value while preserving non-enum values."""
    if isinstance(value, Enum):
        return value.value
    return value


def _st_safe_dict(value: Any) -> dict[str, Any]:
    """Safely convert mapping/dataclass-like values to dictionaries."""

    if value is None:
        return {}

    if isinstance(value, Mapping):
        return dict(value)

    if hasattr(value, "__dict__"):
        try:
            return dict(vars(value))
        except Exception:
            return {}

    return {}


def _st_reference_to_dict(
    reference: Optional[StressTestReference],
) -> dict[str, Any]:
    """Serialize normalized stress-test target reference."""

    if reference is None:
        return {}

    return {
        "target_id": reference.target_id,
        "name": reference.name,
        "target_type": _st_enum_value(reference.target_type),
        "status": _st_enum_value(reference.status),
        "priority": _st_enum_value(reference.priority),
        "scenario_id": reference.scenario_id,
        "dataset_id": reference.dataset_id,
        "candidate_id": reference.candidate_id,
        "experiment_id": reference.experiment_id,
        "hypothesis_id": reference.hypothesis_id,
        "validation_id": reference.validation_id,
    }


def _st_scenario_to_dict(
    scenario: Optional[StressScenarioReference],
) -> dict[str, Any]:
    """Serialize stress scenario reference."""

    if scenario is None:
        return {}

    return {
        "scenario_id": scenario.scenario_id,
        "name": scenario.name,
        "scenario_type": scenario.scenario_type,
        "severity": scenario.severity,
        "description": scenario.description,
    }


def _st_requirements_to_dict(
    requirements: Optional[StressTestRequirements],
) -> dict[str, Any]:
    """Serialize stress-test requirements."""

    if requirements is None:
        return {}

    return {
        "target_available": requirements.target_available,
        "scenario_available": requirements.scenario_available,
        "dataset_available": requirements.dataset_available,
        "candidate_available": requirements.candidate_available,
        "experiment_available": requirements.experiment_available,
        "hypothesis_available": requirements.hypothesis_available,
        "validation_available": requirements.validation_available,
        "test_type_defined": requirements.test_type_defined,
        "measurable": requirements.measurable,
        "reproducible": requirements.reproducible,
        "data_state": _st_enum_value(requirements.data_state),
        "consistency": _st_enum_value(requirements.consistency),
        "readiness": _st_enum_value(requirements.readiness),
        "completeness_score": requirements.completeness_score,
        "warnings": list(requirements.warnings),
    }


def _st_assessment_to_dict(
    assessment: Optional[StressTestAssessment],
) -> dict[str, Any]:
    """Serialize stress-test assessment."""

    if assessment is None:
        return {}

    return {
        "decision": _st_enum_value(assessment.decision),
        "readiness": _st_enum_value(assessment.readiness),
        "data_state": _st_enum_value(assessment.data_state),
        "consistency": _st_enum_value(assessment.consistency),
        "severity": _st_enum_value(assessment.severity),
        "confidence_score": assessment.confidence_score,
        "completeness_score": assessment.completeness_score,
        "strengths": list(assessment.strengths),
        "weaknesses": list(assessment.weaknesses),
        "rationale": assessment.rationale,
    }


# ============================================================
# RESULT SERIALIZATION
# ============================================================

def stress_test_result_to_dict(
    result: Optional[StressTestResult],
) -> dict[str, Any]:
    """Convert StressTestResult to stable dictionary contract."""

    if result is None:
        return {}

    return {
        "request_id": result.request_id,
        "result_id": result.result_id,
        "status": _st_enum_value(result.status),
        "target": _st_reference_to_dict(result.target),
        "requirements": _st_requirements_to_dict(
            result.requirements
        ),
        "assessment": _st_assessment_to_dict(
            result.assessment
        ),
        "rationale": result.rationale,
        "warnings": list(result.warnings),
        "created_at": (
            result.created_at.isoformat()
            if result.created_at is not None
            else None
        ),
        "is_valid": result.is_valid,
        "passed": result.passed,
        "is_conditional": result.is_conditional,
        "requires_review": result.requires_review,
        "is_blocked": result.is_blocked,
        "is_action_request": result.is_action_request,
    }


# ============================================================
# CONTRACT SERIALIZATION
# ============================================================

def stress_test_contract_to_dict(
    contract: Optional[StressTestContract],
) -> dict[str, Any]:
    """Convert StressTestContract to stable dictionary contract."""

    if contract is None:
        return {}

    return {
        "request_id": contract.request_id,
        "contract_id": contract.contract_id,
        "state": _st_enum_value(contract.state),
        "result": stress_test_result_to_dict(
            contract.result
        ),
        "rationale": contract.rationale,
        "warnings": list(contract.warnings),
        "created_at": (
            contract.created_at.isoformat()
            if contract.created_at is not None
            else None
        ),
        "is_valid": contract.is_valid,
        "passed": contract.passed,
        "is_action_request": contract.is_action_request,
    }


# ============================================================
# INTEGRITY CHECK
# ============================================================

def stress_testing_integrity_check() -> dict[str, Any]:
    """
    Structural integrity verification.

    This verifies the stress-testing contract surface only.
    It does not execute research, trading, orders, positions,
    or production deployment actions.
    """

    checks = {
        "engine_constant": bool(STRESS_TESTING_ENGINE),
        "version_constant": bool(STRESS_TESTING_VERSION),

        "engine_instance": stress_testing_engine is not None,

        "request_model": StressTestRequest is not None,
        "reference_model": StressTestReference is not None,
        "scenario_model": StressScenarioReference is not None,
        "requirements_model": StressTestRequirements is not None,
        "assessment_model": StressTestAssessment is not None,
        "result_model": StressTestResult is not None,
        "contract_model": StressTestContract is not None,

        "request_validator": callable(
            validate_stress_test_request
        ),
        "result_validator": callable(
            validate_stress_test_result
        ),
        "contract_validator": callable(
            validate_stress_test_contract
        ),

        "result_serializer": callable(
            stress_test_result_to_dict
        ),
        "contract_serializer": callable(
            stress_test_contract_to_dict
        ),

        "audit_function": callable(
            stress_test_audit
        ),
        "health_function": callable(
            stress_testing_health_check
        ),
        "safety_function": callable(
            stress_test_is_safe
        ),

        "execution_disabled": (
            stress_test_execution_allowed() is False
        ),
        "trade_disabled": (
            stress_test_trade_allowed() is False
        ),
        "order_disabled": (
            stress_test_order_allowed() is False
        ),
        "position_disabled": (
            stress_test_position_allowed() is False
        ),
        "authorization_disabled": (
            stress_test_authorization_allowed() is False
        ),

        "d13_override_disabled": (
            stress_test_can_override_d13() is False
        ),
        "risk_override_disabled": (
            stress_test_can_override_risk() is False
        ),
        "cas_override_disabled": (
            stress_test_can_override_cas() is False
        ),
    }

    passed = all(checks.values())

    return {
        "engine": STRESS_TESTING_ENGINE,
        "version": STRESS_TESTING_VERSION,
        "integrity": "PASS" if passed else "FAIL",
        "passed": passed,
        "checks": checks,

        "research_scope": True,
        "action_authority": False,
        "execution_authority": False,
        "trade_authority": False,
        "order_authority": False,
        "position_authority": False,
        "authorization_authority": False,

        "d13_override": False,
        "risk_override": False,
        "cas_override": False,
    }


def verify_stress_testing_integrity() -> bool:
    """Return True only when all integrity checks pass."""

    return bool(
        stress_testing_integrity_check().get(
            "passed",
            False,
        )
    )


def run_stress_testing_integrity_check() -> dict[str, Any]:
    """Public integrity-check entry point."""

    return stress_testing_integrity_check()


# ============================================================
# FINAL PUBLIC EXPORTS
# ============================================================

__all__ = [
    # Identity
    "STRESS_TESTING_ENGINE",
    "STRESS_TESTING_VERSION",

    # Core enums
    "StressTestStatus",
    "StressTestType",
    "StressTestPriority",
    "StressTestDecision",
    "StressTestContractStatus",

    # Assessment enums
    "StressDataState",
    "StressConsistency",
    "StressReadiness",
    "StressSeverity",

    # Result / contract enums
    "StressTestResultStatus",
    "StressTestContractState",

    # Request / references
    "StressTestRequest",
    "StressTestReference",
    "StressScenarioReference",
    "StressTestContractValidation",

    # Requirements / assessment
    "StressTestRequirements",
    "StressTestAssessment",

    # Builders / validation
    "build_stress_test_reference",
    "validate_stress_test_request",
    "evaluate_stress_data_state",
    "evaluate_stress_consistency",
    "evaluate_stress_test_requirements",
    "evaluate_stress_readiness",
    "evaluate_stress_severity",
    "calculate_stress_confidence",
    "determine_stress_test_decision",
    "build_stress_test_assessment",

    # Result / contract
    "determine_stress_test_result_status",
    "build_stress_test_result",
    "determine_stress_test_contract_state",
    "build_stress_test_contract",

    # Engine
    "StressTestingEngine",
    "stress_testing_engine",

    # Public APIs
    "evaluate_stress_test",
    "analyze_stress_test",
    "review_stress_test",

    # Validation
    "validate_stress_test_result",
    "validate_stress_test_contract",

    # Lifecycle
    "stress_test_ready",
    "stress_test_can_advance",
    "stress_test_status",
    "stress_test_decision",
    "stress_test_readiness",
    "stress_test_confidence",
    "stress_test_severity",
    "stress_test_completeness",

    # Audit
    "stress_test_audit",

    # Safety
    "stress_test_is_safe",
    "stress_test_execution_allowed",
    "stress_test_trade_allowed",
    "stress_test_order_allowed",
    "stress_test_position_allowed",
    "stress_test_authorization_allowed",

    # Authority protection
    "stress_test_can_override_d13",
    "stress_test_can_override_risk",
    "stress_test_can_override_cas",

    # Engine information / health
    "get_stress_testing_engine_info",
    "stress_testing_health_check",
    "run_stress_testing_health_check",

    # Serialization
    "stress_test_result_to_dict",
    "stress_test_contract_to_dict",

    # Integrity
    "stress_testing_integrity_check",
    "verify_stress_testing_integrity",
    "run_stress_testing_integrity_check",
]