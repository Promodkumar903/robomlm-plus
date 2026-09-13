# ============================================================
# ROBOMLM_PLUS
# app/intelligence/research/validation.py
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

VALIDATION_ENGINE = "ROBOMLM_RESEARCH_VALIDATION_ENGINE"
VALIDATION_VERSION = "1.0"


# ============================================================
# ENUMS
# ============================================================

class ValidationStatus(str, Enum):
    NEW = "NEW"
    PROPOSED = "PROPOSED"
    PREPARING = "PREPARING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    PASSED = "PASSED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    ARCHIVED = "ARCHIVED"
    UNKNOWN = "UNKNOWN"


class ValidationType(str, Enum):
    DATA = "DATA"
    EVIDENCE = "EVIDENCE"
    HYPOTHESIS = "HYPOTHESIS"
    FORMULA = "FORMULA"
    ALGORITHM = "ALGORITHM"
    SIGNAL = "SIGNAL"
    STRATEGY = "STRATEGY"
    MODEL = "MODEL"
    ENGINE = "ENGINE"
    SYSTEM = "SYSTEM"
    OUTCOME = "OUTCOME"
    UNKNOWN = "UNKNOWN"


class ValidationPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class ValidationDecision(str, Enum):
    PASS = "PASS"
    CONDITIONAL = "CONDITIONAL"
    FAIL = "FAIL"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"
    RETEST = "RETEST"
    UNKNOWN = "UNKNOWN"


class ValidationContractStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


# ============================================================
# REQUEST CONTRACT
# ============================================================

@dataclass(frozen=True)
class ValidationRequest:
    """
    Immutable validation request.

    This layer evaluates research artifacts and their validation
    evidence. It does not create trading authorization and does
    not override D13, Risk, or CAS.
    """

    target: Any

    validation_type: ValidationType = ValidationType.UNKNOWN
    evidence: Any = None
    dataset: Any = None
    hypothesis: Any = None
    experiment: Any = None
    candidate: Any = None
    stress_test: Any = None

    priority: ValidationPriority = ValidationPriority.MEDIUM

    metadata: Mapping[str, Any] = field(default_factory=dict)

    request_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def validate(self) -> bool:
        if self.target is None:
            return False

        if not isinstance(self.request_id, str):
            return False

        if not self.request_id.strip():
            return False

        if not isinstance(self.metadata, Mapping):
            return False

        return True


# ============================================================
# TARGET REFERENCE
# ============================================================

@dataclass(frozen=True)
class ValidationReference:
    """Normalized reference to the object being validated."""

    target_id: str
    name: str

    validation_type: ValidationType
    status: ValidationStatus
    priority: ValidationPriority

    evidence_id: Optional[str] = None
    dataset_id: Optional[str] = None
    hypothesis_id: Optional[str] = None
    experiment_id: Optional[str] = None
    candidate_id: Optional[str] = None
    stress_test_id: Optional[str] = None

    raw_target: Any = None


# ============================================================
# EVIDENCE REFERENCE
# ============================================================

@dataclass(frozen=True)
class ValidationEvidenceReference:
    """Normalized reference to validation evidence."""

    evidence_id: str
    name: str

    evidence_type: str = "UNKNOWN"
    source: Optional[str] = None
    strength: Optional[str] = None
    description: str = ""

    raw_evidence: Any = None


# ============================================================
# CONTRACT VALIDATION
# ============================================================

@dataclass(frozen=True)
class ValidationContractValidation:
    """Validation state of an incoming ValidationRequest."""

    valid: bool

    target_available: bool
    evidence_available: bool
    dataset_available: bool

    validation_type_defined: bool
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

def _val_read_value(
    obj: Any,
    *names: str,
    default: Any = None,
) -> Any:
    """Safely read a value from mapping or object input."""

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


def _val_text(
    value: Any,
    default: str = "",
) -> str:
    """Normalize a value into safe text."""

    if value is None:
        return default

    try:
        text = str(value).strip()
    except Exception:
        return default

    return text if text else default


def _val_enum(
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

def _val_component_id(
    value: Any,
    *names: str,
) -> Optional[str]:
    """Extract an optional component identifier."""

    if value is None:
        return None

    identifier = _val_read_value(
        value,
        *names,
        "id",
        "uuid",
        "key",
        default=None,
    )

    if identifier is None:
        return None

    text = _val_text(identifier)

    return text or None


# ============================================================
# REFERENCE BUILDER
# ============================================================

def build_validation_reference(
    request: ValidationRequest,
) -> ValidationReference:
    """Build normalized validation target reference."""

    target = request.target

    target_id = _val_component_id(
        target,
        "target_id",
        "validation_id",
        "id",
        "research_id",
        "candidate_id",
        "experiment_id",
        "hypothesis_id",
    )

    if not target_id:
        target_id = request.request_id

    name = _val_text(
        _val_read_value(
            target,
            "name",
            "title",
            "target_name",
            "validation_name",
            "research_name",
            default=None,
        ),
        default=target_id,
    )

    validation_type = _val_enum(
        ValidationType,
        _val_read_value(
            target,
            "validation_type",
            "target_type",
            "type",
            default=request.validation_type,
        ),
        request.validation_type,
    )

    status = _val_enum(
        ValidationStatus,
        _val_read_value(
            target,
            "status",
            "state",
            default=ValidationStatus.NEW,
        ),
        ValidationStatus.NEW,
    )

    priority = _val_enum(
        ValidationPriority,
        _val_read_value(
            target,
            "priority",
            default=request.priority,
        ),
        request.priority,
    )

    return ValidationReference(
        target_id=target_id,
        name=name,
        validation_type=validation_type,
        status=status,
        priority=priority,

        evidence_id=_val_component_id(
            request.evidence,
            "evidence_id",
            "id",
        ),

        dataset_id=_val_component_id(
            request.dataset,
            "dataset_id",
            "id",
        ),

        hypothesis_id=_val_component_id(
            request.hypothesis,
            "hypothesis_id",
            "id",
        ),

        experiment_id=_val_component_id(
            request.experiment,
            "experiment_id",
            "id",
        ),

        candidate_id=_val_component_id(
            request.candidate,
            "candidate_id",
            "id",
        ),

        stress_test_id=_val_component_id(
            request.stress_test,
            "stress_test_id",
            "id",
        ),

        raw_target=target,
    )


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_validation_request(
    request: Any,
) -> ValidationContractValidation:
    """Validate incoming ValidationRequest."""

    if not isinstance(request, ValidationRequest):
        return ValidationContractValidation(
            valid=False,
            target_available=False,
            evidence_available=False,
            dataset_available=False,
            validation_type_defined=False,
            priority_defined=False,
            metadata_valid=False,
            errors=("request must be ValidationRequest",),
        )

    target_available = request.target is not None
    evidence_available = request.evidence is not None
    dataset_available = request.dataset is not None

    validation_type_defined = (
        request.validation_type != ValidationType.UNKNOWN
    )

    priority_defined = (
        request.priority != ValidationPriority.UNKNOWN
    )

    metadata_valid = isinstance(
        request.metadata,
        Mapping,
    )

    errors: list[str] = []
    warnings: list[str] = []

    if not target_available:
        errors.append("target is required")

    if not request.request_id.strip():
        errors.append("request_id is required")

    if not metadata_valid:
        errors.append(
            "metadata must be a Mapping"
        )

    if not validation_type_defined:
        warnings.append(
            "validation_type is UNKNOWN"
        )

    if not evidence_available:
        warnings.append(
            "validation evidence is not provided"
        )

    if not dataset_available:
        warnings.append(
            "dataset is not provided"
        )

    if not priority_defined:
        warnings.append(
            "priority is UNKNOWN"
        )

    return ValidationContractValidation(
        valid=len(errors) == 0,
        target_available=target_available,
        evidence_available=evidence_available,
        dataset_available=dataset_available,
        validation_type_defined=validation_type_defined,
        priority_defined=priority_defined,
        metadata_valid=metadata_valid,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )
# ============================================================
# ROBOMLM PLUS
# app/intelligence/research/validation.py
# PART 2 / 5
# Validation Requirements + Assessment Intelligence
# ============================================================

class ValidationDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    UNKNOWN = "UNKNOWN"


class ValidationConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONFLICTING = "CONFLICTING"
    INSUFFICIENT = "INSUFFICIENT"
    UNKNOWN = "UNKNOWN"


class ValidationReadiness(str, Enum):
    READY = "READY"
    CONDITIONAL = "CONDITIONAL"
    NOT_READY = "NOT_READY"
    UNKNOWN = "UNKNOWN"


class ValidationStrength(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ValidationRequirements:
    target_available: bool
    evidence_available: bool
    dataset_available: bool
    hypothesis_available: bool
    experiment_available: bool
    candidate_available: bool
    stress_test_available: bool
    validation_type_defined: bool
    measurable: bool
    reproducible: bool

    data_state: ValidationDataState
    consistency: ValidationConsistency
    readiness: ValidationReadiness

    completeness_score: float
    warnings: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ValidationAssessment:
    decision: ValidationDecision
    readiness: ValidationReadiness
    data_state: ValidationDataState
    consistency: ValidationConsistency
    strength: ValidationStrength

    confidence_score: float
    completeness_score: float

    strengths: tuple[str, ...] = field(default_factory=tuple)
    weaknesses: tuple[str, ...] = field(default_factory=tuple)
    rationale: str = ""


def _val_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    if value is None:
        return False

    if isinstance(value, str):
        return value.strip().lower() in {
            "true",
            "1",
            "yes",
            "y",
            "valid",
            "available",
            "present",
            "complete",
            "pass",
            "passed",
            "consistent",
            "measurable",
            "reproducible",
        }

    return bool(value)


def _val_conflict_detected(target: Any) -> bool:
    explicit_conflict = _val_read_value(
        target,
        "conflict",
        "conflicts",
        "inconsistent",
        "contradiction",
        "contradictions",
    )

    if isinstance(explicit_conflict, str):
        return explicit_conflict.strip().lower() in {
            "true",
            "yes",
            "1",
            "conflict",
            "conflicting",
            "inconsistent",
            "contradiction",
        }

    return _val_bool(explicit_conflict)


def evaluate_validation_data_state(
    *,
    target_available: bool,
    evidence_available: bool,
    dataset_available: bool,
    validation_type_defined: bool,
    measurable: bool,
) -> ValidationDataState:
    required = (
        target_available,
        evidence_available,
        dataset_available,
        validation_type_defined,
        measurable,
    )

    available_count = sum(bool(x) for x in required)

    if available_count == len(required):
        return ValidationDataState.COMPLETE

    if available_count == 0:
        return ValidationDataState.MISSING

    return ValidationDataState.PARTIAL


def evaluate_validation_consistency(
    target: Any,
    *,
    evidence: Any = None,
    dataset: Any = None,
    hypothesis: Any = None,
    experiment: Any = None,
    stress_test: Any = None,
) -> ValidationConsistency:
    components = (
        target,
        evidence,
        dataset,
        hypothesis,
        experiment,
        stress_test,
    )

    for component in components:
        if component is not None and _val_conflict_detected(component):
            return ValidationConsistency.CONFLICTING

    explicit_values = []

    for component in components:
        if component is None:
            continue

        value = _val_read_value(
            component,
            "consistency",
            "validation_consistency",
            "state",
        )

        if value is not None:
            explicit_values.append(str(value).strip().upper())

    if any(
        value in {
            "CONFLICTING",
            "CONFLICT",
            "INCONSISTENT",
            "CONTRADICTORY",
        }
        for value in explicit_values
    ):
        return ValidationConsistency.CONFLICTING

    if any(
        value in {
            "CONSISTENT",
            "CONSISTENTLY_VALID",
            "ALIGNED",
            "VALID",
            "PASS",
            "PASSED",
        }
        for value in explicit_values
    ):
        return ValidationConsistency.CONSISTENT

    if any(
        value in {
            "INSUFFICIENT",
            "UNKNOWN",
            "UNAVAILABLE",
            "MISSING",
        }
        for value in explicit_values
    ):
        return ValidationConsistency.INSUFFICIENT

    return ValidationConsistency.UNKNOWN


def evaluate_validation_requirements(
    *,
    target: Any,
    validation_type: ValidationType,
    evidence: Any = None,
    dataset: Any = None,
    hypothesis: Any = None,
    experiment: Any = None,
    candidate: Any = None,
    stress_test: Any = None,
) -> ValidationRequirements:
    target_available = target is not None
    evidence_available = evidence is not None
    dataset_available = dataset is not None
    hypothesis_available = hypothesis is not None
    experiment_available = experiment is not None
    candidate_available = candidate is not None
    stress_test_available = stress_test is not None

    validation_type_defined = (
        validation_type != ValidationType.UNKNOWN
    )

    measurable_value = _val_read_value(
        target,
        "measurable",
        "measurement_available",
        "metric",
        "metric_available",
    )

    measurable = (
        _val_bool(measurable_value)
        if measurable_value is not None
        else bool(dataset_available or evidence_available)
    )

    reproducible_value = _val_read_value(
        target,
        "reproducible",
        "reproducibility",
        "reproducibility_available",
    )

    reproducible = (
        _val_bool(reproducible_value)
        if reproducible_value is not None
        else bool(dataset_available and (
            experiment_available
            or hypothesis_available
            or stress_test_available
        ))
    )

    data_state = evaluate_validation_data_state(
        target_available=target_available,
        evidence_available=evidence_available,
        dataset_available=dataset_available,
        validation_type_defined=validation_type_defined,
        measurable=measurable,
    )

    consistency = evaluate_validation_consistency(
        target,
        evidence=evidence,
        dataset=dataset,
        hypothesis=hypothesis,
        experiment=experiment,
        stress_test=stress_test,
    )

    components = (
        target_available,
        evidence_available,
        dataset_available,
        validation_type_defined,
        measurable,
        reproducible,
    )

    completeness_score = (
        sum(bool(value) for value in components)
        / len(components)
    ) * 100.0

    warnings = []

    if not target_available:
        warnings.append("Validation target is missing.")

    if not evidence_available:
        warnings.append("Validation evidence is missing.")

    if not dataset_available:
        warnings.append("Validation dataset is missing.")

    if not validation_type_defined:
        warnings.append("Validation type is undefined.")

    if not measurable:
        warnings.append("Validation target is not measurable.")

    if not reproducible:
        warnings.append("Validation reproducibility is not established.")

    if consistency == ValidationConsistency.CONFLICTING:
        warnings.append("Validation inputs contain an explicit conflict.")

    if consistency == ValidationConsistency.INSUFFICIENT:
        warnings.append("Validation consistency evidence is insufficient.")

    if consistency == ValidationConsistency.CONFLICTING:
        readiness = ValidationReadiness.NOT_READY
    elif completeness_score >= 80.0:
        readiness = ValidationReadiness.READY
    elif completeness_score >= 50.0:
        readiness = ValidationReadiness.CONDITIONAL
    else:
        readiness = ValidationReadiness.NOT_READY

    return ValidationRequirements(
        target_available=target_available,
        evidence_available=evidence_available,
        dataset_available=dataset_available,
        hypothesis_available=hypothesis_available,
        experiment_available=experiment_available,
        candidate_available=candidate_available,
        stress_test_available=stress_test_available,
        validation_type_defined=validation_type_defined,
        measurable=measurable,
        reproducible=reproducible,
        data_state=data_state,
        consistency=consistency,
        readiness=readiness,
        completeness_score=round(completeness_score, 4),
        warnings=tuple(warnings),
    )


def evaluate_validation_readiness(
    requirements: ValidationRequirements,
) -> ValidationReadiness:
    if requirements.consistency == ValidationConsistency.CONFLICTING:
        return ValidationReadiness.NOT_READY

    if requirements.data_state == ValidationDataState.MISSING:
        return ValidationReadiness.NOT_READY

    if requirements.completeness_score >= 80.0:
        return ValidationReadiness.READY

    if requirements.completeness_score >= 50.0:
        return ValidationReadiness.CONDITIONAL

    return ValidationReadiness.NOT_READY


def calculate_validation_confidence(
    requirements: ValidationRequirements,
) -> float:
    """
    Structural confidence only.

    This is NOT a source-specific research-performance formula.
    It measures the quality/completeness of the validation contract
    inputs until the authoritative research specification is wired.
    """

    score = requirements.completeness_score

    if requirements.consistency == ValidationConsistency.CONFLICTING:
        score -= 30.0
    elif requirements.consistency == ValidationConsistency.CONSISTENT:
        score += 5.0
    elif requirements.consistency == ValidationConsistency.INSUFFICIENT:
        score -= 10.0

    if requirements.data_state == ValidationDataState.MISSING:
        score -= 20.0
    elif requirements.data_state == ValidationDataState.PARTIAL:
        score -= 5.0

    return round(max(0.0, min(100.0, score)), 4)


def determine_validation_strength(
    confidence_score: float,
    requirements: ValidationRequirements,
) -> ValidationStrength:
    if requirements.consistency == ValidationConsistency.CONFLICTING:
        return ValidationStrength.LOW

    if confidence_score >= 90.0:
        return ValidationStrength.CRITICAL

    if confidence_score >= 75.0:
        return ValidationStrength.HIGH

    if confidence_score >= 50.0:
        return ValidationStrength.MODERATE

    return ValidationStrength.LOW


def determine_validation_decision(
    *,
    requirements: ValidationRequirements,
    confidence_score: float,
) -> ValidationDecision:
    if requirements.consistency == ValidationConsistency.CONFLICTING:
        return ValidationDecision.BLOCK

    if requirements.data_state == ValidationDataState.MISSING:
        return ValidationDecision.BLOCK

    if not requirements.target_available:
        return ValidationDecision.BLOCK

    if requirements.readiness == ValidationReadiness.NOT_READY:
        if confidence_score < 40.0:
            return ValidationDecision.RETEST
        return ValidationDecision.REVIEW

    if (
        requirements.readiness == ValidationReadiness.READY
        and confidence_score >= 80.0
    ):
        return ValidationDecision.PASS

    if (
        requirements.readiness == ValidationReadiness.CONDITIONAL
        and confidence_score >= 50.0
    ):
        return ValidationDecision.CONDITIONAL

    return ValidationDecision.REVIEW


def build_validation_assessment(
    requirements: ValidationRequirements,
) -> ValidationAssessment:
    readiness = evaluate_validation_readiness(requirements)
    confidence_score = calculate_validation_confidence(requirements)

    decision = determine_validation_decision(
        requirements=requirements,
        confidence_score=confidence_score,
    )

    strength = determine_validation_strength(
        confidence_score,
        requirements,
    )

    strengths = []
    weaknesses = []

    if requirements.target_available:
        strengths.append("Validation target is available.")

    if requirements.evidence_available:
        strengths.append("Validation evidence is available.")

    if requirements.dataset_available:
        strengths.append("Validation dataset is available.")

    if requirements.measurable:
        strengths.append("Validation target is measurable.")

    if requirements.reproducible:
        strengths.append("Validation reproducibility is established.")

    if requirements.consistency == ValidationConsistency.CONSISTENT:
        strengths.append("Validation inputs are explicitly consistent.")

    if not requirements.target_available:
        weaknesses.append("Validation target is missing.")

    if not requirements.evidence_available:
        weaknesses.append("Validation evidence is missing.")

    if not requirements.dataset_available:
        weaknesses.append("Validation dataset is missing.")

    if not requirements.measurable:
        weaknesses.append("Validation target is not measurable.")

    if not requirements.reproducible:
        weaknesses.append("Validation reproducibility is not established.")

    if requirements.consistency == ValidationConsistency.CONFLICTING:
        weaknesses.append("Validation inputs contain conflicting information.")

    if decision == ValidationDecision.PASS:
        rationale = (
            "Validation contract is sufficiently complete and "
            "structurally ready for a PASS assessment."
        )
    elif decision == ValidationDecision.CONDITIONAL:
        rationale = (
            "Validation contract is partially ready and requires "
            "conditional handling before final acceptance."
        )
    elif decision == ValidationDecision.BLOCK:
        rationale = (
            "Validation is blocked because required inputs are missing "
            "or explicitly conflicting."
        )
    elif decision == ValidationDecision.RETEST:
        rationale = (
            "Validation evidence is insufficient and requires another "
            "validation cycle."
        )
    else:
        rationale = (
            "Validation requires review before a final validation "
            "decision can be accepted."
        )

    return ValidationAssessment(
        decision=decision,
        readiness=readiness,
        data_state=requirements.data_state,
        consistency=requirements.consistency,
        strength=strength,
        confidence_score=confidence_score,
        completeness_score=requirements.completeness_score,
        strengths=tuple(strengths),
        weaknesses=tuple(weaknesses),
        rationale=rationale,
    )
# ============================================================
# ROBOMLM PLUS
# app/intelligence/research/validation.py
# PART 3 / 5
# Validation Result + Contract + Engine
# ============================================================


class ValidationResultStatus(str, Enum):
    PASS = "PASS"
    CONDITIONAL = "CONDITIONAL"
    REVIEW = "REVIEW"
    BLOCKED = "BLOCKED"
    RETEST = "RETEST"
    FAILED = "FAILED"
    INVALID = "INVALID"


class ValidationContractState(str, Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


@dataclass(frozen=True)
class ValidationResult:
    request_id: str
    result_id: str
    status: ValidationResultStatus

    target: ValidationReference
    requirements: ValidationRequirements
    assessment: ValidationAssessment

    rationale: str = ""
    warnings: tuple[str, ...] = field(default_factory=tuple)
    created_at: str = ""

    @property
    def is_valid(self) -> bool:
        return (
            bool(self.request_id)
            and bool(self.result_id)
            and self.status != ValidationResultStatus.INVALID
            and bool(self.target.target_id)
        )

    @property
    def passed(self) -> bool:
        return (
            self.is_valid
            and self.status == ValidationResultStatus.PASS
            and self.assessment.decision == ValidationDecision.PASS
        )

    @property
    def is_conditional(self) -> bool:
        return (
            self.status == ValidationResultStatus.CONDITIONAL
            or self.assessment.decision == ValidationDecision.CONDITIONAL
        )

    @property
    def requires_review(self) -> bool:
        return (
            self.status == ValidationResultStatus.REVIEW
            or self.assessment.decision == ValidationDecision.REVIEW
        )

    @property
    def requires_retest(self) -> bool:
        return (
            self.status == ValidationResultStatus.RETEST
            or self.assessment.decision == ValidationDecision.RETEST
        )

    @property
    def is_blocked(self) -> bool:
        return (
            self.status == ValidationResultStatus.BLOCKED
            or self.assessment.decision == ValidationDecision.BLOCK
        )

    @property
    def is_action_request(self) -> bool:
        return False


@dataclass(frozen=True)
class ValidationContract:
    request_id: str
    contract_id: str
    state: ValidationContractState

    result: ValidationResult

    rationale: str = ""
    warnings: tuple[str, ...] = field(default_factory=tuple)
    created_at: str = ""

    @property
    def is_valid(self) -> bool:
        return (
            bool(self.request_id)
            and bool(self.contract_id)
            and self.state != ValidationContractState.INVALID
            and self.result.is_valid
        )

    @property
    def passed(self) -> bool:
        return self.is_valid and self.result.passed

    @property
    def is_action_request(self) -> bool:
        return False


def _determine_validation_result_status(
    assessment: ValidationAssessment,
) -> ValidationResultStatus:
    decision = assessment.decision

    if decision == ValidationDecision.PASS:
        return ValidationResultStatus.PASS

    if decision == ValidationDecision.CONDITIONAL:
        return ValidationResultStatus.CONDITIONAL

    if decision == ValidationDecision.REVIEW:
        return ValidationResultStatus.REVIEW

    if decision == ValidationDecision.RETEST:
        return ValidationResultStatus.RETEST

    if decision == ValidationDecision.BLOCK:
        return ValidationResultStatus.BLOCKED

    if decision == ValidationDecision.FAIL:
        return ValidationResultStatus.FAILED

    return ValidationResultStatus.REVIEW


def build_validation_result(
    *,
    request: ValidationRequest,
    target: ValidationReference,
    requirements: ValidationRequirements,
    assessment: ValidationAssessment,
    warnings: tuple[str, ...] = (),
) -> ValidationResult:
    status = _determine_validation_result_status(assessment)

    return ValidationResult(
        request_id=request.request_id,
        result_id=f"VALRES-{uuid4().hex[:12].upper()}",
        status=status,
        target=target,
        requirements=requirements,
        assessment=assessment,
        rationale=assessment.rationale,
        warnings=tuple(
            list(requirements.warnings)
            + list(warnings)
        ),
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def _determine_validation_contract_state(
    result: ValidationResult,
) -> ValidationContractState:
    if not result.is_valid:
        return ValidationContractState.INVALID

    if result.is_blocked:
        return ValidationContractState.BLOCKED

    requirements = result.requirements

    if (
        requirements.data_state == ValidationDataState.COMPLETE
        and requirements.readiness == ValidationReadiness.READY
        and result.assessment.consistency
        != ValidationConsistency.CONFLICTING
    ):
        return ValidationContractState.COMPLETE

    if requirements.data_state == ValidationDataState.MISSING:
        return ValidationContractState.INCOMPLETE

    if result.requires_retest:
        return ValidationContractState.INCOMPLETE

    return ValidationContractState.INCOMPLETE


def build_validation_contract(
    *,
    request: ValidationRequest,
    result: ValidationResult,
) -> ValidationContract:
    state = _determine_validation_contract_state(result)

    return ValidationContract(
        request_id=request.request_id,
        contract_id=f"VALCON-{uuid4().hex[:12].upper()}",
        state=state,
        result=result,
        rationale=result.rationale,
        warnings=result.warnings,
        created_at=datetime.now(timezone.utc).isoformat(),
    )


class ValidationEngine:
    """
    Research validation orchestration layer.

    This engine evaluates validation readiness and produces a
    normalized ValidationResult + ValidationContract.

    It does NOT:
      - execute trades
      - create orders
      - authorize actions
      - modify D13
      - override Risk
      - override CAS
      - mutate production state
    """

    engine_name = VALIDATION_ENGINE
    version = VALIDATION_VERSION

    def validate_request(
        self,
        request: Any,
    ) -> ValidationContractValidation:
        return validate_validation_request(request)

    def _invalid_result(
        self,
        request: Any,
        reason: str,
    ) -> ValidationResult:
        reference = build_validation_reference(
            request.target if isinstance(request, ValidationRequest)
            else None,
            request if isinstance(request, ValidationRequest)
            else None,
        )

        empty_requirements = ValidationRequirements(
            target_available=False,
            evidence_available=False,
            dataset_available=False,
            hypothesis_available=False,
            experiment_available=False,
            candidate_available=False,
            stress_test_available=False,
            validation_type_defined=False,
            measurable=False,
            reproducible=False,
            data_state=ValidationDataState.MISSING,
            consistency=ValidationConsistency.UNKNOWN,
            readiness=ValidationReadiness.NOT_READY,
            completeness_score=0.0,
            warnings=(reason,),
        )

        empty_assessment = ValidationAssessment(
            decision=ValidationDecision.BLOCK,
            readiness=ValidationReadiness.NOT_READY,
            data_state=ValidationDataState.MISSING,
            consistency=ValidationConsistency.UNKNOWN,
            strength=ValidationStrength.LOW,
            confidence_score=0.0,
            completeness_score=0.0,
            strengths=(),
            weaknesses=(reason,),
            rationale=reason,
        )

        return ValidationResult(
            request_id=(
                request.request_id
                if isinstance(request, ValidationRequest)
                else ""
            ),
            result_id=f"VALRES-{uuid4().hex[:12].upper()}",
            status=ValidationResultStatus.INVALID,
            target=reference,
            requirements=empty_requirements,
            assessment=empty_assessment,
            rationale=reason,
            warnings=(reason,),
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    def evaluate(
        self,
        request: ValidationRequest,
    ) -> ValidationContract:
        validation = self.validate_request(request)

        if not validation.is_valid:
            result = self._invalid_result(
                request,
                "; ".join(validation.errors)
                or "Invalid validation request.",
            )
            return build_validation_contract(
                request=request,
                result=result,
            )

        target = build_validation_reference(
            request.target,
            request,
        )

        requirements = evaluate_validation_requirements(
            target=request.target,
            validation_type=request.validation_type,
            evidence=request.evidence,
            dataset=request.dataset,
            hypothesis=request.hypothesis,
            experiment=request.experiment,
            candidate=request.candidate,
            stress_test=request.stress_test,
        )

        assessment = build_validation_assessment(
            requirements,
        )

        result = build_validation_result(
            request=request,
            target=target,
            requirements=requirements,
            assessment=assessment,
        )

        return build_validation_contract(
            request=request,
            result=result,
        )


validation_engine = ValidationEngine()


def evaluate_validation(
    request: ValidationRequest,
) -> ValidationContract:
    return validation_engine.evaluate(request)


def analyze_validation(
    request: ValidationRequest,
) -> ValidationContract:
    return validation_engine.evaluate(request)


def review_validation(
    request: ValidationRequest,
) -> ValidationContract:
    return validation_engine.evaluate(request)
# ============================================================
# ROBOMLM PLUS
# app/intelligence/research/validation.py
# PART 4 / 5
# Validation Gates + Audit + Safety + Health
# ============================================================


def validate_validation_result(
    result: Any,
) -> bool:
    if not isinstance(result, ValidationResult):
        return False

    if not result.is_valid:
        return False

    if not result.request_id:
        return False

    if not result.result_id:
        return False

    if not result.target.target_id:
        return False

    confidence = result.assessment.confidence_score
    completeness = result.assessment.completeness_score

    if not 0.0 <= confidence <= 100.0:
        return False

    if not 0.0 <= completeness <= 100.0:
        return False

    if result.requirements.readiness == ValidationReadiness.UNKNOWN:
        return False

    return True


def validate_validation_contract(
    contract: Any,
) -> bool:
    if not isinstance(contract, ValidationContract):
        return False

    if not contract.is_valid:
        return False

    if not contract.request_id:
        return False

    if not contract.contract_id:
        return False

    if not validate_validation_result(contract.result):
        return False

    if contract.state == ValidationContractState.INVALID:
        return False

    return True


def validation_ready(
    result_or_contract: Any,
) -> bool:
    if isinstance(result_or_contract, ValidationContract):
        result = result_or_contract.result
    elif isinstance(result_or_contract, ValidationResult):
        result = result_or_contract
    else:
        return False

    if not validate_validation_result(result):
        return False

    requirements = result.requirements
    assessment = result.assessment

    return (
        result.passed
        and assessment.decision == ValidationDecision.PASS
        and assessment.readiness == ValidationReadiness.READY
        and requirements.data_state == ValidationDataState.COMPLETE
        and requirements.consistency
        != ValidationConsistency.CONFLICTING
        and requirements.target_available
        and requirements.evidence_available
        and requirements.dataset_available
        and requirements.validation_type_defined
        and requirements.measurable
        and requirements.reproducible
        and assessment.confidence_score >= 80.0
    )


def validation_can_advance(
    result_or_contract: Any,
) -> bool:
    if isinstance(result_or_contract, ValidationContract):
        result = result_or_contract.result
    elif isinstance(result_or_contract, ValidationResult):
        result = result_or_contract
    else:
        return False

    if not validate_validation_result(result):
        return False

    if validation_ready(result):
        return True

    # Conditional validation may move only to REVIEW/next
    # research lifecycle stage; it is never treated as PASS.
    return (
        result.is_conditional
        and result.assessment.readiness
        == ValidationReadiness.CONDITIONAL
        and result.assessment.confidence_score >= 50.0
        and not result.is_blocked
    )


def validation_status(
    result_or_contract: Any,
) -> ValidationResultStatus:
    if isinstance(result_or_contract, ValidationContract):
        return result_or_contract.result.status

    if isinstance(result_or_contract, ValidationResult):
        return result_or_contract.status

    return ValidationResultStatus.INVALID


def validation_decision(
    result_or_contract: Any,
) -> ValidationDecision:
    if isinstance(result_or_contract, ValidationContract):
        return result_or_contract.result.assessment.decision

    if isinstance(result_or_contract, ValidationResult):
        return result_or_contract.assessment.decision

    return ValidationDecision.UNKNOWN


def validation_readiness(
    result_or_contract: Any,
) -> ValidationReadiness:
    if isinstance(result_or_contract, ValidationContract):
        return result_or_contract.result.assessment.readiness

    if isinstance(result_or_contract, ValidationResult):
        return result_or_contract.assessment.readiness

    return ValidationReadiness.UNKNOWN


def validation_confidence(
    result_or_contract: Any,
) -> float:
    if isinstance(result_or_contract, ValidationContract):
        return result_or_contract.result.assessment.confidence_score

    if isinstance(result_or_contract, ValidationResult):
        return result_or_contract.assessment.confidence_score

    return 0.0


def validation_strength(
    result_or_contract: Any,
) -> ValidationStrength:
    if isinstance(result_or_contract, ValidationContract):
        return result_or_contract.result.assessment.strength

    if isinstance(result_or_contract, ValidationResult):
        return result_or_contract.assessment.strength

    return ValidationStrength.UNKNOWN


def validation_completeness(
    result_or_contract: Any,
) -> float:
    if isinstance(result_or_contract, ValidationContract):
        return result_or_contract.result.assessment.completeness_score

    if isinstance(result_or_contract, ValidationResult):
        return result_or_contract.assessment.completeness_score

    return 0.0


def validation_audit(
    result_or_contract: Any,
) -> dict[str, Any]:
    if isinstance(result_or_contract, ValidationContract):
        contract = result_or_contract
        result = contract.result
    elif isinstance(result_or_contract, ValidationResult):
        contract = None
        result = result_or_contract
    else:
        return {
            "engine": VALIDATION_ENGINE,
            "version": VALIDATION_VERSION,
            "valid": False,
            "status": ValidationResultStatus.INVALID.value,
        }

    return {
        "engine": VALIDATION_ENGINE,
        "version": VALIDATION_VERSION,
        "valid": validate_validation_result(result),
        "request_id": result.request_id,
        "result_id": result.result_id,
        "contract_id": (
            contract.contract_id
            if contract is not None
            else None
        ),
        "contract_state": (
            contract.state.value
            if contract is not None
            else None
        ),
        "target_id": result.target.target_id,
        "target_name": result.target.name,
        "validation_type": result.target.validation_type.value,
        "status": result.status.value,
        "decision": result.assessment.decision.value,
        "readiness": result.assessment.readiness.value,
        "data_state": result.assessment.data_state.value,
        "consistency": result.assessment.consistency.value,
        "strength": result.assessment.strength.value,
        "confidence_score": result.assessment.confidence_score,
        "completeness_score": result.assessment.completeness_score,
        "passed": result.passed,
        "conditional": result.is_conditional,
        "requires_review": result.requires_review,
        "requires_retest": result.requires_retest,
        "blocked": result.is_blocked,
        "can_advance": validation_can_advance(result),
        "warnings": list(result.warnings),
        "rationale": result.rationale,
        "created_at": result.created_at,
    }


# ------------------------------------------------------------
# HARD SAFETY BOUNDARIES
# ------------------------------------------------------------

def validation_is_safe(
    result_or_contract: Any,
) -> bool:
    """
    Validation is an analytical/research lifecycle operation only.

    It must never be interpreted as authorization for:
      - execution
      - trading
      - order creation
      - position changes
      - account actions
    """

    return (
        isinstance(result_or_contract, (
            ValidationResult,
            ValidationContract,
        ))
        and validate_validation_result(
            result_or_contract.result
            if isinstance(result_or_contract, ValidationContract)
            else result_or_contract
        )
    )


def validation_allows_execution(
    result_or_contract: Any,
) -> bool:
    return False


def validation_allows_trade(
    result_or_contract: Any,
) -> bool:
    return False


def validation_allows_order(
    result_or_contract: Any,
) -> bool:
    return False


def validation_allows_position_change(
    result_or_contract: Any,
) -> bool:
    return False


def validation_allows_authorization(
    result_or_contract: Any,
) -> bool:
    return False


# ------------------------------------------------------------
# AUTHORITY BOUNDARIES
# ------------------------------------------------------------

def validation_overrides_d13(
    result_or_contract: Any,
) -> bool:
    return False


def validation_overrides_risk(
    result_or_contract: Any,
) -> bool:
    return False


def validation_overrides_cas(
    result_or_contract: Any,
) -> bool:
    return False


# ------------------------------------------------------------
# ENGINE INFORMATION
# ------------------------------------------------------------

def get_validation_engine_info() -> dict[str, Any]:
    return {
        "engine": VALIDATION_ENGINE,
        "version": VALIDATION_VERSION,
        "module": "app.intelligence.research.validation",
        "role": "RESEARCH_VALIDATION",
        "decision_authority": False,
        "execution_authority": False,
        "order_authority": False,
        "position_authority": False,
        "authorization_authority": False,
        "d13_override": False,
        "risk_override": False,
        "cas_override": False,
    }


# ------------------------------------------------------------
# HEALTH CHECK
# ------------------------------------------------------------

def validation_health_check() -> dict[str, Any]:
    checks = {
        "engine_available": isinstance(
            validation_engine,
            ValidationEngine,
        ),
        "version_defined": bool(VALIDATION_VERSION),
        "engine_name_defined": bool(VALIDATION_ENGINE),
        "result_validator_available": callable(
            validate_validation_result
        ),
        "contract_validator_available": callable(
            validate_validation_contract
        ),
        "readiness_gate_available": callable(
            validation_ready
        ),
        "advance_gate_available": callable(
            validation_can_advance
        ),
        "audit_available": callable(
            validation_audit
        ),
        "execution_blocked": (
            validation_allows_execution(None) is False
        ),
        "trade_blocked": (
            validation_allows_trade(None) is False
        ),
        "order_blocked": (
            validation_allows_order(None) is False
        ),
        "position_blocked": (
            validation_allows_position_change(None) is False
        ),
        "authorization_blocked": (
            validation_allows_authorization(None) is False
        ),
        "d13_override_blocked": (
            validation_overrides_d13(None) is False
        ),
        "risk_override_blocked": (
            validation_overrides_risk(None) is False
        ),
        "cas_override_blocked": (
            validation_overrides_cas(None) is False
        ),
    }

    passed = all(checks.values())

    return {
        "engine": VALIDATION_ENGINE,
        "version": VALIDATION_VERSION,
        "healthy": passed,
        "checks": checks,
        "failed_checks": [
            name
            for name, value in checks.items()
            if not value
        ],
    }


def run_validation_health_check() -> bool:
    return bool(validation_health_check()["healthy"])
# ============================================================
# ROBOMLM PLUS
# app/intelligence/research/validation.py
# PART 5 / 5
# Serialization + Integrity + Public API
# ============================================================


def _val_enum_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    return value


def _val_safe_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)

    if hasattr(value, "__dict__"):
        return dict(vars(value))

    return {}


def _val_reference_to_dict(
    reference: ValidationReference,
) -> dict[str, Any]:
    return {
        "target_id": reference.target_id,
        "name": reference.name,
        "validation_type": _val_enum_value(
            reference.validation_type
        ),
        "status": _val_enum_value(reference.status),
        "priority": _val_enum_value(reference.priority),
        "evidence_id": reference.evidence_id,
        "dataset_id": reference.dataset_id,
        "hypothesis_id": reference.hypothesis_id,
        "experiment_id": reference.experiment_id,
        "candidate_id": reference.candidate_id,
        "stress_test_id": reference.stress_test_id,
        "raw_target": _val_safe_dict(reference.raw_target),
    }


def _val_evidence_to_dict(
    evidence: ValidationEvidenceReference,
) -> dict[str, Any]:
    return {
        "evidence_id": evidence.evidence_id,
        "name": evidence.name,
        "evidence_type": evidence.evidence_type,
        "source": evidence.source,
        "strength": evidence.strength,
        "description": evidence.description,
        "raw_evidence": _val_safe_dict(
            evidence.raw_evidence
        ),
    }


def _val_requirements_to_dict(
    requirements: ValidationRequirements,
) -> dict[str, Any]:
    return {
        "target_available": requirements.target_available,
        "evidence_available": requirements.evidence_available,
        "dataset_available": requirements.dataset_available,
        "hypothesis_available": requirements.hypothesis_available,
        "experiment_available": requirements.experiment_available,
        "candidate_available": requirements.candidate_available,
        "stress_test_available": requirements.stress_test_available,
        "validation_type_defined": requirements.validation_type_defined,
        "measurable": requirements.measurable,
        "reproducible": requirements.reproducible,
        "data_state": _val_enum_value(
            requirements.data_state
        ),
        "consistency": _val_enum_value(
            requirements.consistency
        ),
        "readiness": _val_enum_value(
            requirements.readiness
        ),
        "completeness_score": requirements.completeness_score,
        "warnings": list(requirements.warnings),
    }


def _val_assessment_to_dict(
    assessment: ValidationAssessment,
) -> dict[str, Any]:
    return {
        "decision": _val_enum_value(
            assessment.decision
        ),
        "readiness": _val_enum_value(
            assessment.readiness
        ),
        "data_state": _val_enum_value(
            assessment.data_state
        ),
        "consistency": _val_enum_value(
            assessment.consistency
        ),
        "strength": _val_enum_value(
            assessment.strength
        ),
        "confidence_score": assessment.confidence_score,
        "completeness_score": assessment.completeness_score,
        "strengths": list(assessment.strengths),
        "weaknesses": list(assessment.weaknesses),
        "rationale": assessment.rationale,
    }


def validation_result_to_dict(
    result: ValidationResult,
) -> dict[str, Any]:
    if not isinstance(result, ValidationResult):
        return {}

    return {
        "request_id": result.request_id,
        "result_id": result.result_id,
        "status": _val_enum_value(result.status),
        "target": _val_reference_to_dict(result.target),
        "requirements": _val_requirements_to_dict(
            result.requirements
        ),
        "assessment": _val_assessment_to_dict(
            result.assessment
        ),
        "rationale": result.rationale,
        "warnings": list(result.warnings),
        "created_at": result.created_at,
        "is_valid": result.is_valid,
        "passed": result.passed,
        "is_conditional": result.is_conditional,
        "requires_review": result.requires_review,
        "requires_retest": result.requires_retest,
        "is_blocked": result.is_blocked,
        "is_action_request": result.is_action_request,
    }


def validation_contract_to_dict(
    contract: ValidationContract,
) -> dict[str, Any]:
    if not isinstance(contract, ValidationContract):
        return {}

    return {
        "request_id": contract.request_id,
        "contract_id": contract.contract_id,
        "state": _val_enum_value(contract.state),
        "result": validation_result_to_dict(
            contract.result
        ),
        "rationale": contract.rationale,
        "warnings": list(contract.warnings),
        "created_at": contract.created_at,
        "is_valid": contract.is_valid,
        "passed": contract.passed,
        "is_action_request": contract.is_action_request,
    }


def validation_integrity_check(
    contract_or_result: Any = None,
) -> dict[str, Any]:
    """
    Structural integrity verification.

    This function validates the research-validation contract only.
    It does not validate trading profitability or market performance.
    """

    if isinstance(contract_or_result, ValidationContract):
        result_valid = validate_validation_result(
            contract_or_result.result
        )
        contract_valid = validate_validation_contract(
            contract_or_result
        )

        return {
            "engine": VALIDATION_ENGINE,
            "version": VALIDATION_VERSION,
            "valid": contract_valid,
            "result_valid": result_valid,
            "contract_valid": contract_valid,
            "passed": contract_or_result.passed,
            "ready": validation_ready(
                contract_or_result
            ),
            "can_advance": validation_can_advance(
                contract_or_result
            ),
        }

    if isinstance(contract_or_result, ValidationResult):
        result_valid = validate_validation_result(
            contract_or_result
        )

        return {
            "engine": VALIDATION_ENGINE,
            "version": VALIDATION_VERSION,
            "valid": result_valid,
            "result_valid": result_valid,
            "contract_valid": False,
            "passed": contract_or_result.passed,
            "ready": validation_ready(
                contract_or_result
            ),
            "can_advance": validation_can_advance(
                contract_or_result
            ),
        }

    health = validation_health_check()

    return {
        "engine": VALIDATION_ENGINE,
        "version": VALIDATION_VERSION,
        "valid": bool(health["healthy"]),
        "result_valid": False,
        "contract_valid": False,
        "passed": False,
        "ready": False,
        "can_advance": False,
        "health": health,
    }


def verify_validation_integrity(
    contract_or_result: Any = None,
) -> bool:
    return bool(
        validation_integrity_check(
            contract_or_result
        )["valid"]
    )


def run_validation_integrity_check() -> bool:
    return bool(
        validation_health_check()["healthy"]
    )


# ------------------------------------------------------------
# PUBLIC API
# ------------------------------------------------------------

__all__ = [
    # Constants
    "VALIDATION_ENGINE",
    "VALIDATION_VERSION",

    # Core enums
    "ValidationStatus",
    "ValidationType",
    "ValidationPriority",
    "ValidationDecision",
    "ValidationContractStatus",

    # Request/reference contracts
    "ValidationRequest",
    "ValidationReference",
    "ValidationEvidenceReference",
    "ValidationContractValidation",

    # Assessment enums
    "ValidationDataState",
    "ValidationConsistency",
    "ValidationReadiness",
    "ValidationStrength",

    # Assessment contracts
    "ValidationRequirements",
    "ValidationAssessment",

    # Result/contract
    "ValidationResultStatus",
    "ValidationContractState",
    "ValidationResult",
    "ValidationContract",

    # Builders / validators
    "build_validation_reference",
    "validate_validation_request",
    "evaluate_validation_data_state",
    "evaluate_validation_consistency",
    "evaluate_validation_requirements",
    "evaluate_validation_readiness",
    "calculate_validation_confidence",
    "determine_validation_strength",
    "determine_validation_decision",
    "build_validation_assessment",
    "build_validation_result",
    "build_validation_contract",

    # Engine
    "ValidationEngine",
    "validation_engine",
    "evaluate_validation",
    "analyze_validation",
    "review_validation",

    # Result/contract validation
    "validate_validation_result",
    "validate_validation_contract",

    # Gates/accessors
    "validation_ready",
    "validation_can_advance",
    "validation_status",
    "validation_decision",
    "validation_readiness",
    "validation_confidence",
    "validation_strength",
    "validation_completeness",

    # Audit
    "validation_audit",

    # Safety boundaries
    "validation_is_safe",
    "validation_allows_execution",
    "validation_allows_trade",
    "validation_allows_order",
    "validation_allows_position_change",
    "validation_allows_authorization",

    # Authority boundaries
    "validation_overrides_d13",
    "validation_overrides_risk",
    "validation_overrides_cas",

    # Engine information / health
    "get_validation_engine_info",
    "validation_health_check",
    "run_validation_health_check",

    # Serialization
    "validation_result_to_dict",
    "validation_contract_to_dict",

    # Integrity
    "validation_integrity_check",
    "verify_validation_integrity",
    "run_validation_integrity_check",
]
