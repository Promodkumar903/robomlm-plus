# ============================================================
# ROBOMLM PLUS
# app/intelligence/research/version_manager.py
# PART 1 / 5
# Version Manager Foundation + Contracts
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

VERSION_MANAGER_ENGINE = "ROBOMLM_RESEARCH_VERSION_MANAGER"
VERSION_MANAGER_VERSION = "1.0"


# ============================================================
# CORE ENUMS
# ============================================================

class VersionStatus(str, Enum):
    NEW = "NEW"
    DRAFT = "DRAFT"
    PROPOSED = "PROPOSED"
    VALIDATING = "VALIDATING"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    DEPRECATED = "DEPRECATED"
    ROLLED_BACK = "ROLLED_BACK"
    ARCHIVED = "ARCHIVED"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"
    UNKNOWN = "UNKNOWN"


class VersionType(str, Enum):
    RESEARCH = "RESEARCH"
    DATASET = "DATASET"
    HYPOTHESIS = "HYPOTHESIS"
    EXPERIMENT = "EXPERIMENT"
    VALIDATION = "VALIDATION"
    STRESS_TEST = "STRESS_TEST"
    MODEL = "MODEL"
    STRATEGY = "STRATEGY"
    SIGNAL = "SIGNAL"
    FORMULA = "FORMULA"
    ALGORITHM = "ALGORITHM"
    ENGINE = "ENGINE"
    SYSTEM = "SYSTEM"
    UNKNOWN = "UNKNOWN"


class VersionPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class VersionDecision(str, Enum):
    CREATE = "CREATE"
    ACCEPT = "ACCEPT"
    ACTIVATE = "ACTIVATE"
    HOLD = "HOLD"
    REVIEW = "REVIEW"
    REJECT = "REJECT"
    SUPERSEDE = "SUPERSEDE"
    DEPRECATE = "DEPRECATE"
    ROLLBACK = "ROLLBACK"
    ARCHIVE = "ARCHIVE"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


class VersionContractStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


# ============================================================
# REQUEST CONTRACT
# ============================================================

@dataclass(frozen=True)
class VersionRequest:
    version: Any

    version_type: VersionType = VersionType.UNKNOWN
    parent_version: Any = None
    source: Any = None
    artifact: Any = None
    validation: Any = None
    experiment: Any = None
    candidate: Any = None

    priority: VersionPriority = VersionPriority.UNKNOWN

    metadata: Mapping[str, Any] = field(default_factory=dict)

    request_id: str = field(
        default_factory=lambda: f"VERREQ-{uuid4().hex[:12].upper()}"
    )

    timestamp: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )

    def validate(self) -> tuple[str, ...]:
        errors = []

        if self.version is None:
            errors.append("Version is required.")

        if not self.request_id:
            errors.append("Request ID is required.")

        if not isinstance(self.metadata, Mapping):
            errors.append("Metadata must be a Mapping.")

        if not isinstance(self.version_type, VersionType):
            errors.append("Invalid version_type.")

        if not isinstance(self.priority, VersionPriority):
            errors.append("Invalid priority.")

        return tuple(errors)


# ============================================================
# VERSION REFERENCE
# ============================================================

@dataclass(frozen=True)
class VersionReference:
    version_id: str
    version_name: str

    version_type: VersionType
    status: VersionStatus
    priority: VersionPriority

    version_number: str = ""
    parent_version_id: Optional[str] = None

    source_id: Optional[str] = None
    artifact_id: Optional[str] = None
    validation_id: Optional[str] = None
    experiment_id: Optional[str] = None
    candidate_id: Optional[str] = None

    raw_version: Any = None


# ============================================================
# VERSION ARTIFACT REFERENCE
# ============================================================

@dataclass(frozen=True)
class VersionArtifactReference:
    artifact_id: str
    name: str = ""
    artifact_type: str = ""
    source: str = ""
    checksum: str = ""
    description: str = ""
    raw_artifact: Any = None


# ============================================================
# VERSION CONTRACT VALIDATION
# ============================================================

@dataclass(frozen=True)
class VersionContractValidation:
    valid: bool

    version_available: bool
    version_type_defined: bool
    priority_defined: bool
    parent_valid: bool
    source_available: bool
    artifact_available: bool
    metadata_valid: bool

    errors: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_valid(self) -> bool:
        return bool(
            self.valid
            and self.version_available
            and self.version_type_defined
            and self.priority_defined
            and self.metadata_valid
            and not self.errors
        )


# ============================================================
# SAFE VALUE HELPERS
# ============================================================

def _vm_read_value(
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
        if hasattr(obj, name):
            try:
                return getattr(obj, name)
            except Exception:
                continue

    return default


def _vm_text(
    value: Any,
    default: str = "",
) -> str:
    if value is None:
        return default

    text = str(value).strip()

    return text if text else default


def _vm_enum(
    value: Any,
    enum_type: type[Enum],
    default: Enum,
) -> Enum:
    if isinstance(value, enum_type):
        return value

    if value is None:
        return default

    try:
        return enum_type(str(value).strip().upper())
    except (ValueError, TypeError):
        return default


def _vm_component_id(
    component: Any,
    *names: str,
) -> Optional[str]:
    if component is None:
        return None

    value = _vm_read_value(
        component,
        *names,
        "id",
        "uuid",
        "identifier",
    )

    if value is None:
        return None

    text = _vm_text(value)

    return text or None


# ============================================================
# VERSION REFERENCE BUILDER
# ============================================================

def build_version_reference(
    version: Any,
    request: Optional[VersionRequest] = None,
) -> VersionReference:
    request_type = (
        request.version_type
        if isinstance(request, VersionRequest)
        else VersionType.UNKNOWN
    )

    request_priority = (
        request.priority
        if isinstance(request, VersionRequest)
        else VersionPriority.UNKNOWN
    )

    version_id = _vm_component_id(
        version,
        "version_id",
        "version_uuid",
        "identifier",
    )

    if not version_id:
        version_id = f"VER-{uuid4().hex[:12].upper()}"

    version_name = _vm_text(
        _vm_read_value(
            version,
            "version_name",
            "name",
            "title",
        ),
        default=version_id,
    )

    version_number = _vm_text(
        _vm_read_value(
            version,
            "version_number",
            "number",
            "version",
            "tag",
        )
    )

    status = _vm_enum(
        _vm_read_value(version, "status", "state"),
        VersionStatus,
        VersionStatus.NEW,
    )

    version_type = _vm_enum(
        _vm_read_value(
            version,
            "version_type",
            "type",
        ),
        VersionType,
        request_type,
    )

    priority = _vm_enum(
        _vm_read_value(
            version,
            "priority",
        ),
        VersionPriority,
        request_priority,
    )

    parent_version_id = _vm_component_id(
        _vm_read_value(
            version,
            "parent_version",
            "parent",
            "base_version",
        ),
        "version_id",
        "id",
        "identifier",
    )

    if parent_version_id is None and isinstance(
        request,
        VersionRequest,
    ):
        parent_version_id = _vm_component_id(
            request.parent_version,
            "version_id",
            "id",
            "identifier",
        )

    source = (
        request.source
        if isinstance(request, VersionRequest)
        else _vm_read_value(
            version,
            "source",
        )
    )

    artifact = (
        request.artifact
        if isinstance(request, VersionRequest)
        else _vm_read_value(
            version,
            "artifact",
        )
    )

    validation = (
        request.validation
        if isinstance(request, VersionRequest)
        else _vm_read_value(
            version,
            "validation",
        )
    )

    experiment = (
        request.experiment
        if isinstance(request, VersionRequest)
        else _vm_read_value(
            version,
            "experiment",
        )
    )

    candidate = (
        request.candidate
        if isinstance(request, VersionRequest)
        else _vm_read_value(
            version,
            "candidate",
        )
    )

    return VersionReference(
        version_id=version_id,
        version_name=version_name,
        version_type=version_type,
        status=status,
        priority=priority,
        version_number=version_number,
        parent_version_id=parent_version_id,
        source_id=_vm_component_id(
            source,
            "source_id",
            "id",
            "identifier",
        ),
        artifact_id=_vm_component_id(
            artifact,
            "artifact_id",
            "id",
            "identifier",
        ),
        validation_id=_vm_component_id(
            validation,
            "validation_id",
            "id",
            "identifier",
        ),
        experiment_id=_vm_component_id(
            experiment,
            "experiment_id",
            "id",
            "identifier",
        ),
        candidate_id=_vm_component_id(
            candidate,
            "candidate_id",
            "id",
            "identifier",
        ),
        raw_version=version,
    )


# ============================================================
# REQUEST VALIDATOR
# ============================================================

def validate_version_request(
    request: Any,
) -> VersionContractValidation:
    if not isinstance(request, VersionRequest):
        return VersionContractValidation(
            valid=False,
            version_available=False,
            version_type_defined=False,
            priority_defined=False,
            parent_valid=False,
            source_available=False,
            artifact_available=False,
            metadata_valid=False,
            errors=("Request must be a VersionRequest.",),
            warnings=(),
        )

    errors = list(request.validate())
    warnings = []

    version_available = request.version is not None

    version_type_defined = (
        request.version_type != VersionType.UNKNOWN
    )

    priority_defined = (
        request.priority != VersionPriority.UNKNOWN
    )

    parent_valid = True

    if request.parent_version is not None:
        parent_id = _vm_component_id(
            request.parent_version,
            "version_id",
            "id",
            "identifier",
        )

        if not parent_id:
            parent_valid = False
            errors.append(
                "Parent version is present but has no valid identifier."
            )

    source_available = request.source is not None
    artifact_available = request.artifact is not None

    if not source_available:
        warnings.append(
            "Version source is not provided."
        )

    if not artifact_available:
        warnings.append(
            "Version artifact is not provided."
        )

    if not request.validation:
        warnings.append(
            "Validation reference is not provided."
        )

    if not request.experiment:
        warnings.append(
            "Experiment reference is not provided."
        )

    if not version_available:
        errors.append(
            "Version definition is missing."
        )

    if not version_type_defined:
        errors.append(
            "Version type is undefined."
        )

    if not priority_defined:
        warnings.append(
            "Version priority is UNKNOWN."
        )

    metadata_valid = isinstance(
        request.metadata,
        Mapping,
    )

    valid = (
        not errors
        and version_available
        and version_type_defined
        and metadata_valid
        and parent_valid
    )

    return VersionContractValidation(
        valid=valid,
        version_available=version_available,
        version_type_defined=version_type_defined,
        priority_defined=priority_defined,
        parent_valid=parent_valid,
        source_available=source_available,
        artifact_available=artifact_available,
        metadata_valid=metadata_valid,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )
# ============================================================
# ROBOMLM PLUS
# app/intelligence/research/version_manager.py
# PART 2 / 5
# Version Requirements + Lineage + Assessment Intelligence
# ============================================================


class VersionDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    UNKNOWN = "UNKNOWN"


class VersionConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONFLICTING = "CONFLICTING"
    INSUFFICIENT = "INSUFFICIENT"
    UNKNOWN = "UNKNOWN"


class VersionReadiness(str, Enum):
    READY = "READY"
    CONDITIONAL = "CONDITIONAL"
    NOT_READY = "NOT_READY"
    UNKNOWN = "UNKNOWN"


class VersionStrength(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class VersionRequirements:
    version_available: bool
    version_type_defined: bool
    priority_defined: bool
    parent_available: bool
    source_available: bool
    artifact_available: bool
    validation_available: bool
    experiment_available: bool
    candidate_available: bool

    lineage_valid: bool
    reproducible: bool

    data_state: VersionDataState
    consistency: VersionConsistency
    readiness: VersionReadiness

    completeness_score: float
    warnings: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class VersionAssessment:
    decision: VersionDecision
    readiness: VersionReadiness
    data_state: VersionDataState
    consistency: VersionConsistency
    strength: VersionStrength

    confidence_score: float
    completeness_score: float

    strengths: tuple[str, ...] = field(default_factory=tuple)
    weaknesses: tuple[str, ...] = field(default_factory=tuple)
    rationale: str = ""


# ============================================================
# VALUE HELPERS
# ============================================================

def _vm_bool(value: Any) -> bool:
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
            "reproducible",
        }

    return bool(value)


def _vm_conflict_detected(
    component: Any,
) -> bool:
    value = _vm_read_value(
        component,
        "conflict",
        "conflicts",
        "inconsistent",
        "contradiction",
        "contradictions",
    )

    if isinstance(value, str):
        return value.strip().lower() in {
            "true",
            "yes",
            "1",
            "conflict",
            "conflicting",
            "inconsistent",
            "contradiction",
        }

    return _vm_bool(value)


# ============================================================
# DATA STATE
# ============================================================

def evaluate_version_data_state(
    *,
    version_available: bool,
    version_type_defined: bool,
    source_available: bool,
    artifact_available: bool,
    lineage_valid: bool,
) -> VersionDataState:
    required = (
        version_available,
        version_type_defined,
        source_available,
        artifact_available,
        lineage_valid,
    )

    available_count = sum(bool(value) for value in required)

    if available_count == len(required):
        return VersionDataState.COMPLETE

    if available_count == 0:
        return VersionDataState.MISSING

    return VersionDataState.PARTIAL


# ============================================================
# CONSISTENCY
# ============================================================

def evaluate_version_consistency(
    version: Any,
    *,
    parent_version: Any = None,
    source: Any = None,
    artifact: Any = None,
    validation: Any = None,
    experiment: Any = None,
    candidate: Any = None,
) -> VersionConsistency:
    components = (
        version,
        parent_version,
        source,
        artifact,
        validation,
        experiment,
        candidate,
    )

    for component in components:
        if component is not None and _vm_conflict_detected(component):
            return VersionConsistency.CONFLICTING

    explicit_values = []

    for component in components:
        if component is None:
            continue

        value = _vm_read_value(
            component,
            "consistency",
            "version_consistency",
            "state",
        )

        if value is not None:
            explicit_values.append(
                str(value).strip().upper()
            )

    if any(
        value in {
            "CONFLICTING",
            "CONFLICT",
            "INCONSISTENT",
            "CONTRADICTORY",
        }
        for value in explicit_values
    ):
        return VersionConsistency.CONFLICTING

    if any(
        value in {
            "CONSISTENT",
            "ALIGNED",
            "VALID",
            "PASS",
            "PASSED",
        }
        for value in explicit_values
    ):
        return VersionConsistency.CONSISTENT

    if any(
        value in {
            "INSUFFICIENT",
            "UNKNOWN",
            "UNAVAILABLE",
            "MISSING",
        }
        for value in explicit_values
    ):
        return VersionConsistency.INSUFFICIENT

    return VersionConsistency.UNKNOWN


# ============================================================
# REQUIREMENTS
# ============================================================

def evaluate_version_requirements(
    *,
    version: Any,
    version_type: VersionType,
    priority: VersionPriority,
    parent_version: Any = None,
    source: Any = None,
    artifact: Any = None,
    validation: Any = None,
    experiment: Any = None,
    candidate: Any = None,
) -> VersionRequirements:
    version_available = version is not None

    version_type_defined = (
        version_type != VersionType.UNKNOWN
    )

    priority_defined = (
        priority != VersionPriority.UNKNOWN
    )

    parent_available = parent_version is not None
    source_available = source is not None
    artifact_available = artifact is not None
    validation_available = validation is not None
    experiment_available = experiment is not None
    candidate_available = candidate is not None

    lineage_valid = True

    if parent_available:
        parent_id = _vm_component_id(
            parent_version,
            "version_id",
            "id",
            "identifier",
        )

        if not parent_id:
            lineage_valid = False

    reproducible_value = _vm_read_value(
        version,
        "reproducible",
        "reproducibility",
        "reproducibility_available",
    )

    if reproducible_value is not None:
        reproducible = _vm_bool(reproducible_value)
    else:
        reproducible = bool(
            source_available
            and artifact_available
        )

    data_state = evaluate_version_data_state(
        version_available=version_available,
        version_type_defined=version_type_defined,
        source_available=source_available,
        artifact_available=artifact_available,
        lineage_valid=lineage_valid,
    )

    consistency = evaluate_version_consistency(
        version,
        parent_version=parent_version,
        source=source,
        artifact=artifact,
        validation=validation,
        experiment=experiment,
        candidate=candidate,
    )

    # Structural completeness only.
    # This is not a research-specific performance formula.
    components = (
        version_available,
        version_type_defined,
        priority_defined,
        source_available,
        artifact_available,
        validation_available,
        experiment_available,
        candidate_available,
        lineage_valid,
        reproducible,
    )

    completeness_score = (
        sum(bool(value) for value in components)
        / len(components)
    ) * 100.0

    warnings = []

    if not version_available:
        warnings.append(
            "Version definition is missing."
        )

    if not version_type_defined:
        warnings.append(
            "Version type is undefined."
        )

    if not priority_defined:
        warnings.append(
            "Version priority is UNKNOWN."
        )

    if not source_available:
        warnings.append(
            "Version source is not provided."
        )

    if not artifact_available:
        warnings.append(
            "Version artifact is not provided."
        )

    if not validation_available:
        warnings.append(
            "Validation reference is not provided."
        )

    if not experiment_available:
        warnings.append(
            "Experiment reference is not provided."
        )

    if not candidate_available:
        warnings.append(
            "Candidate reference is not provided."
        )

    if not lineage_valid:
        warnings.append(
            "Version lineage is invalid."
        )

    if not reproducible:
        warnings.append(
            "Version reproducibility is not established."
        )

    if consistency == VersionConsistency.CONFLICTING:
        warnings.append(
            "Version inputs contain an explicit conflict."
        )

    if consistency == VersionConsistency.CONFLICTING:
        readiness = VersionReadiness.NOT_READY
    elif completeness_score >= 80.0:
        readiness = VersionReadiness.READY
    elif completeness_score >= 50.0:
        readiness = VersionReadiness.CONDITIONAL
    else:
        readiness = VersionReadiness.NOT_READY

    return VersionRequirements(
        version_available=version_available,
        version_type_defined=version_type_defined,
        priority_defined=priority_defined,
        parent_available=parent_available,
        source_available=source_available,
        artifact_available=artifact_available,
        validation_available=validation_available,
        experiment_available=experiment_available,
        candidate_available=candidate_available,
        lineage_valid=lineage_valid,
        reproducible=reproducible,
        data_state=data_state,
        consistency=consistency,
        readiness=readiness,
        completeness_score=round(
            completeness_score,
            4,
        ),
        warnings=tuple(warnings),
    )


# ============================================================
# READINESS
# ============================================================

def evaluate_version_readiness(
    requirements: VersionRequirements,
) -> VersionReadiness:
    if requirements.consistency == VersionConsistency.CONFLICTING:
        return VersionReadiness.NOT_READY

    if not requirements.version_available:
        return VersionReadiness.NOT_READY

    if requirements.data_state == VersionDataState.MISSING:
        return VersionReadiness.NOT_READY

    if not requirements.lineage_valid:
        return VersionReadiness.NOT_READY

    if requirements.completeness_score >= 80.0:
        return VersionReadiness.READY

    if requirements.completeness_score >= 50.0:
        return VersionReadiness.CONDITIONAL

    return VersionReadiness.NOT_READY


# ============================================================
# STRUCTURAL CONFIDENCE
# ============================================================

def calculate_version_confidence(
    requirements: VersionRequirements,
) -> float:
    """
    Structural version-contract confidence only.

    This does NOT represent market performance, trading accuracy,
    research validity, or deployment profitability.
    """

    score = requirements.completeness_score

    if requirements.consistency == VersionConsistency.CONFLICTING:
        score -= 30.0
    elif requirements.consistency == VersionConsistency.CONSISTENT:
        score += 5.0
    elif requirements.consistency == VersionConsistency.INSUFFICIENT:
        score -= 10.0

    if requirements.data_state == VersionDataState.MISSING:
        score -= 20.0
    elif requirements.data_state == VersionDataState.PARTIAL:
        score -= 5.0

    if not requirements.lineage_valid:
        score -= 20.0

    if not requirements.reproducible:
        score -= 5.0

    return round(
        max(0.0, min(100.0, score)),
        4,
    )


# ============================================================
# STRENGTH
# ============================================================

def determine_version_strength(
    confidence_score: float,
    requirements: VersionRequirements,
) -> VersionStrength:
    if requirements.consistency == VersionConsistency.CONFLICTING:
        return VersionStrength.LOW

    if not requirements.lineage_valid:
        return VersionStrength.LOW

    if confidence_score >= 90.0:
        return VersionStrength.CRITICAL

    if confidence_score >= 75.0:
        return VersionStrength.HIGH

    if confidence_score >= 50.0:
        return VersionStrength.MODERATE

    return VersionStrength.LOW


# ============================================================
# DECISION
# ============================================================

def determine_version_decision(
    *,
    requirements: VersionRequirements,
    confidence_score: float,
) -> VersionDecision:
    if requirements.consistency == VersionConsistency.CONFLICTING:
        return VersionDecision.BLOCK

    if not requirements.version_available:
        return VersionDecision.BLOCK

    if not requirements.lineage_valid:
        return VersionDecision.BLOCK

    if requirements.data_state == VersionDataState.MISSING:
        return VersionDecision.BLOCK

    if requirements.readiness == VersionReadiness.NOT_READY:
        if confidence_score < 40.0:
            return VersionDecision.HOLD
        return VersionDecision.REVIEW

    if (
        requirements.readiness == VersionReadiness.READY
        and confidence_score >= 80.0
    ):
        return VersionDecision.ACCEPT

    if (
        requirements.readiness == VersionReadiness.CONDITIONAL
        and confidence_score >= 50.0
    ):
        return VersionDecision.HOLD

    return VersionDecision.REVIEW


# ============================================================
# ASSESSMENT BUILDER
# ============================================================

def build_version_assessment(
    requirements: VersionRequirements,
) -> VersionAssessment:
    readiness = evaluate_version_readiness(
        requirements
    )

    confidence_score = calculate_version_confidence(
        requirements
    )

    decision = determine_version_decision(
        requirements=requirements,
        confidence_score=confidence_score,
    )

    strength = determine_version_strength(
        confidence_score,
        requirements,
    )

    strengths = []
    weaknesses = []

    if requirements.version_available:
        strengths.append(
            "Version definition is available."
        )

    if requirements.version_type_defined:
        strengths.append(
            "Version type is defined."
        )

    if requirements.source_available:
        strengths.append(
            "Version source is available."
        )

    if requirements.artifact_available:
        strengths.append(
            "Version artifact is available."
        )

    if requirements.lineage_valid:
        strengths.append(
            "Version lineage is structurally valid."
        )

    if requirements.reproducible:
        strengths.append(
            "Version reproducibility is established."
        )

    if requirements.consistency == VersionConsistency.CONSISTENT:
        strengths.append(
            "Version inputs are explicitly consistent."
        )

    if not requirements.version_available:
        weaknesses.append(
            "Version definition is missing."
        )

    if not requirements.version_type_defined:
        weaknesses.append(
            "Version type is undefined."
        )

    if not requirements.source_available:
        weaknesses.append(
            "Version source is missing."
        )

    if not requirements.artifact_available:
        weaknesses.append(
            "Version artifact is missing."
        )

    if not requirements.lineage_valid:
        weaknesses.append(
            "Version lineage is invalid."
        )

    if not requirements.reproducible:
        weaknesses.append(
            "Version reproducibility is not established."
        )

    if requirements.consistency == VersionConsistency.CONFLICTING:
        weaknesses.append(
            "Version inputs contain conflicting information."
        )

    if decision == VersionDecision.ACCEPT:
        rationale = (
            "Version contract is structurally complete and "
            "ready for acceptance."
        )
    elif decision == VersionDecision.HOLD:
        rationale = (
            "Version contract is conditionally ready and "
            "requires additional lifecycle review."
        )
    elif decision == VersionDecision.BLOCK:
        rationale = (
            "Version processing is blocked because required "
            "version or lineage information is missing or conflicting."
        )
    elif decision == VersionDecision.REVIEW:
        rationale = (
            "Version contract requires review before lifecycle "
            "progression."
        )
    else:
        rationale = (
            "Version assessment requires additional evaluation."
        )

    return VersionAssessment(
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
# app/intelligence/research/version_manager.py
# PART 3 / 5
# Version Result + Contract + Engine
# ============================================================


class VersionResultStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    CONDITIONAL = "CONDITIONAL"
    REVIEW = "REVIEW"
    BLOCKED = "BLOCKED"
    REJECTED = "REJECTED"
    ROLLBACK = "ROLLBACK"
    ARCHIVED = "ARCHIVED"
    INVALID = "INVALID"


class VersionContractState(str, Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


# ============================================================
# VERSION RESULT
# ============================================================

@dataclass(frozen=True)
class VersionResult:
    request_id: str
    result_id: str

    status: VersionResultStatus

    version: VersionReference
    requirements: VersionRequirements
    assessment: VersionAssessment

    rationale: str = ""
    warnings: tuple[str, ...] = field(default_factory=tuple)
    created_at: str = ""

    @property
    def is_valid(self) -> bool:
        return (
            bool(self.request_id)
            and bool(self.result_id)
            and self.status != VersionResultStatus.INVALID
            and bool(self.version.version_id)
        )

    @property
    def accepted(self) -> bool:
        return (
            self.is_valid
            and self.status == VersionResultStatus.ACCEPTED
            and self.assessment.decision
            == VersionDecision.ACCEPT
        )

    @property
    def is_conditional(self) -> bool:
        return (
            self.status == VersionResultStatus.CONDITIONAL
        )

    @property
    def requires_review(self) -> bool:
        return (
            self.status == VersionResultStatus.REVIEW
            or self.assessment.decision
            == VersionDecision.REVIEW
        )

    @property
    def is_blocked(self) -> bool:
        return (
            self.status == VersionResultStatus.BLOCKED
            or self.assessment.decision
            == VersionDecision.BLOCK
        )

    @property
    def requires_rollback(self) -> bool:
        return (
            self.status == VersionResultStatus.ROLLBACK
            or self.assessment.decision
            == VersionDecision.ROLLBACK
        )

    @property
    def is_action_request(self) -> bool:
        return False


# ============================================================
# VERSION CONTRACT
# ============================================================

@dataclass(frozen=True)
class VersionContract:
    request_id: str
    contract_id: str

    state: VersionContractState

    result: VersionResult

    rationale: str = ""
    warnings: tuple[str, ...] = field(default_factory=tuple)
    created_at: str = ""

    @property
    def is_valid(self) -> bool:
        return (
            bool(self.request_id)
            and bool(self.contract_id)
            and self.state != VersionContractState.INVALID
            and self.result.is_valid
        )

    @property
    def accepted(self) -> bool:
        return (
            self.is_valid
            and self.result.accepted
        )

    @property
    def is_action_request(self) -> bool:
        return False


# ============================================================
# RESULT STATUS
# ============================================================

def _determine_version_result_status(
    assessment: VersionAssessment,
) -> VersionResultStatus:
    decision = assessment.decision

    if decision == VersionDecision.ACCEPT:
        return VersionResultStatus.ACCEPTED

    if decision == VersionDecision.HOLD:
        return VersionResultStatus.CONDITIONAL

    if decision == VersionDecision.REVIEW:
        return VersionResultStatus.REVIEW

    if decision == VersionDecision.BLOCK:
        return VersionResultStatus.BLOCKED

    if decision == VersionDecision.REJECT:
        return VersionResultStatus.REJECTED

    if decision == VersionDecision.ROLLBACK:
        return VersionResultStatus.ROLLBACK

    if decision == VersionDecision.ARCHIVE:
        return VersionResultStatus.ARCHIVED

    return VersionResultStatus.REVIEW


# ============================================================
# RESULT BUILDER
# ============================================================

def build_version_result(
    *,
    request: VersionRequest,
    version: VersionReference,
    requirements: VersionRequirements,
    assessment: VersionAssessment,
    warnings: tuple[str, ...] = (),
) -> VersionResult:
    status = _determine_version_result_status(
        assessment
    )

    combined_warnings = tuple(
        list(requirements.warnings)
        + list(warnings)
    )

    return VersionResult(
        request_id=request.request_id,
        result_id=f"VERRES-{uuid4().hex[:12].upper()}",
        status=status,
        version=version,
        requirements=requirements,
        assessment=assessment,
        rationale=assessment.rationale,
        warnings=combined_warnings,
        created_at=datetime.now(
            timezone.utc
        ).isoformat(),
    )


# ============================================================
# CONTRACT STATE
# ============================================================

def _determine_version_contract_state(
    result: VersionResult,
) -> VersionContractState:
    if not result.is_valid:
        return VersionContractState.INVALID

    if result.is_blocked:
        return VersionContractState.BLOCKED

    requirements = result.requirements

    if (
        requirements.data_state
        == VersionDataState.COMPLETE
        and requirements.readiness
        == VersionReadiness.READY
        and requirements.lineage_valid
        and requirements.consistency
        != VersionConsistency.CONFLICTING
    ):
        return VersionContractState.COMPLETE

    if (
        requirements.data_state
        == VersionDataState.MISSING
    ):
        return VersionContractState.INCOMPLETE

    return VersionContractState.INCOMPLETE


# ============================================================
# CONTRACT BUILDER
# ============================================================

def build_version_contract(
    *,
    request: VersionRequest,
    result: VersionResult,
) -> VersionContract:
    state = _determine_version_contract_state(
        result
    )

    return VersionContract(
        request_id=request.request_id,
        contract_id=f"VERCON-{uuid4().hex[:12].upper()}",
        state=state,
        result=result,
        rationale=result.rationale,
        warnings=result.warnings,
        created_at=datetime.now(
            timezone.utc
        ).isoformat(),
    )


# ============================================================
# VERSION MANAGER ENGINE
# ============================================================

class VersionManagerEngine:
    """
    Research version lifecycle orchestration layer.

    Responsibilities:
      - validate version requests
      - resolve version references
      - evaluate version requirements
      - evaluate lineage/consistency
      - produce VersionResult
      - produce VersionContract

    It does NOT:
      - activate production systems
      - deploy trading systems
      - execute trades
      - create orders
      - modify positions
      - authorize accounts
      - override D13
      - override Risk
      - override CAS
    """

    engine_name = VERSION_MANAGER_ENGINE
    version = VERSION_MANAGER_VERSION

    def validate_request(
        self,
        request: Any,
    ) -> VersionContractValidation:
        return validate_version_request(request)

    def _invalid_result(
        self,
        request: Any,
        reason: str,
    ) -> VersionResult:
        if isinstance(request, VersionRequest):
            reference = build_version_reference(
                request.version,
                request,
            )
            request_id = request.request_id
        else:
            reference = VersionReference(
                version_id="",
                version_name="",
                version_type=VersionType.UNKNOWN,
                status=VersionStatus.INVALID,
                priority=VersionPriority.UNKNOWN,
                raw_version=None,
            )
            request_id = ""

        requirements = VersionRequirements(
            version_available=False,
            version_type_defined=False,
            priority_defined=False,
            parent_available=False,
            source_available=False,
            artifact_available=False,
            validation_available=False,
            experiment_available=False,
            candidate_available=False,
            lineage_valid=False,
            reproducible=False,
            data_state=VersionDataState.MISSING,
            consistency=VersionConsistency.UNKNOWN,
            readiness=VersionReadiness.NOT_READY,
            completeness_score=0.0,
            warnings=(reason,),
        )

        assessment = VersionAssessment(
            decision=VersionDecision.BLOCK,
            readiness=VersionReadiness.NOT_READY,
            data_state=VersionDataState.MISSING,
            consistency=VersionConsistency.UNKNOWN,
            strength=VersionStrength.LOW,
            confidence_score=0.0,
            completeness_score=0.0,
            strengths=(),
            weaknesses=(reason,),
            rationale=reason,
        )

        return VersionResult(
            request_id=request_id,
            result_id=f"VERRES-{uuid4().hex[:12].upper()}",
            status=VersionResultStatus.INVALID,
            version=reference,
            requirements=requirements,
            assessment=assessment,
            rationale=reason,
            warnings=(reason,),
            created_at=datetime.now(
                timezone.utc
            ).isoformat(),
        )

    def evaluate(
        self,
        request: VersionRequest,
    ) -> VersionContract:
        validation = self.validate_request(
            request
        )

        if not validation.is_valid:
            result = self._invalid_result(
                request,
                "; ".join(validation.errors)
                or "Invalid version request.",
            )

            return build_version_contract(
                request=request,
                result=result,
            )

        version = build_version_reference(
            request.version,
            request,
        )

        requirements = evaluate_version_requirements(
            version=request.version,
            version_type=request.version_type,
            priority=request.priority,
            parent_version=request.parent_version,
            source=request.source,
            artifact=request.artifact,
            validation=request.validation,
            experiment=request.experiment,
            candidate=request.candidate,
        )

        assessment = build_version_assessment(
            requirements
        )

        result = build_version_result(
            request=request,
            version=version,
            requirements=requirements,
            assessment=assessment,
        )

        return build_version_contract(
            request=request,
            result=result,
        )


# ============================================================
# SINGLETON ENGINE
# ============================================================

version_manager_engine = VersionManagerEngine()


# ============================================================
# PUBLIC ENGINE WRAPPERS
# ============================================================

def evaluate_version(
    request: VersionRequest,
) -> VersionContract:
    return version_manager_engine.evaluate(
        request
    )


def analyze_version(
    request: VersionRequest,
) -> VersionContract:
    return version_manager_engine.evaluate(
        request
    )


def review_version(
    request: VersionRequest,
) -> VersionContract:
    return version_manager_engine.evaluate(
        request
    )
# ============================================================
# PART 4/5 — VALIDATION, READINESS, AUDIT & HEALTH
# ============================================================

def validate_version_result(result: Any) -> bool:
    if not isinstance(result, VersionResult):
        return False

    if not result.request_id or not result.result_id:
        return False

    if result.status == VersionResultStatus.INVALID:
        return False

    if not isinstance(result.version, VersionReference):
        return False

    if not result.version.version_id:
        return False

    if not isinstance(result.requirements, VersionRequirements):
        return False

    if not isinstance(result.assessment, VersionAssessment):
        return False

    if not 0.0 <= float(result.assessment.confidence_score) <= 100.0:
        return False

    if not 0.0 <= float(result.assessment.completeness_score) <= 100.0:
        return False

    return True


def validate_version_contract(contract: Any) -> bool:
    if not isinstance(contract, VersionContract):
        return False

    if not contract.request_id or not contract.contract_id:
        return False

    if contract.state == VersionContractState.INVALID:
        return False

    return validate_version_result(contract.result)


def version_ready(value: Any) -> bool:
    """
    Strict research-version readiness gate.

    READY does not mean production activation.
    It only means the version contract is sufficiently
    complete and validated to advance in the research lifecycle.
    """
    result = value.result if isinstance(value, VersionContract) else value

    if not validate_version_result(result):
        return False

    if result.status != VersionResultStatus.ACCEPTED:
        return False

    req = result.requirements
    assessment = result.assessment

    if req.data_state != VersionDataState.COMPLETE:
        return False

    if req.readiness != VersionReadiness.READY:
        return False

    if req.consistency == VersionConsistency.CONFLICTING:
        return False

    if not req.version_available:
        return False

    if not req.version_type_defined:
        return False

    if not req.lineage_valid:
        return False

    if not req.reproducible:
        return False

    if assessment.decision != VersionDecision.ACCEPT:
        return False

    if float(assessment.confidence_score) < 80.0:
        return False

    return True


def version_can_advance(value: Any) -> bool:
    """
    Controlled lifecycle advancement gate.

    ACCEPTED versions require strict readiness.
    CONDITIONAL versions may advance only when the underlying
    contract remains structurally valid and non-conflicting.
    """
    result = value.result if isinstance(value, VersionContract) else value

    if not validate_version_result(result):
        return False

    if result.is_blocked or result.requires_rollback:
        return False

    if version_ready(result):
        return True

    req = result.requirements
    assessment = result.assessment

    if (
        result.is_conditional
        and req.data_state != VersionDataState.MISSING
        and req.consistency != VersionConsistency.CONFLICTING
        and req.lineage_valid
        and float(assessment.confidence_score) >= 50.0
    ):
        return True

    return False


def version_status(value: Any) -> VersionStatus:
    result = value.result if isinstance(value, VersionContract) else value

    if not isinstance(result, VersionResult):
        return VersionStatus.UNKNOWN

    return result.version.status


def version_decision(value: Any) -> VersionDecision:
    result = value.result if isinstance(value, VersionContract) else value

    if not isinstance(result, VersionResult):
        return VersionDecision.UNKNOWN

    return result.assessment.decision


def version_readiness(value: Any) -> VersionReadiness:
    result = value.result if isinstance(value, VersionContract) else value

    if not isinstance(result, VersionResult):
        return VersionReadiness.UNKNOWN

    return result.requirements.readiness


def version_confidence(value: Any) -> float:
    result = value.result if isinstance(value, VersionContract) else value

    if not isinstance(result, VersionResult):
        return 0.0

    return float(result.assessment.confidence_score)


def version_strength(value: Any) -> VersionStrength:
    result = value.result if isinstance(value, VersionContract) else value

    if not isinstance(result, VersionResult):
        return VersionStrength.UNKNOWN

    return result.assessment.strength


def version_completeness(value: Any) -> float:
    result = value.result if isinstance(value, VersionContract) else value

    if not isinstance(result, VersionResult):
        return 0.0

    return float(result.assessment.completeness_score)


def version_audit(value: Any) -> dict[str, Any]:
    result = value.result if isinstance(value, VersionContract) else value

    if not isinstance(result, VersionResult):
        return {
            "valid": False,
            "engine": VERSION_MANAGER_ENGINE,
            "version": VERSION_MANAGER_VERSION,
        }

    req = result.requirements
    assessment = result.assessment

    return {
        "valid": validate_version_result(result),
        "request_id": result.request_id,
        "result_id": result.result_id,
        "version_id": result.version.version_id,
        "version_name": result.version.version_name,
        "version_number": result.version.version_number,
        "version_type": _vm_enum(result.version.version_type),
        "status": _vm_enum(result.version.status),
        "priority": _vm_enum(result.version.priority),
        "decision": _vm_enum(assessment.decision),
        "readiness": _vm_enum(req.readiness),
        "data_state": _vm_enum(req.data_state),
        "consistency": _vm_enum(req.consistency),
        "strength": _vm_enum(assessment.strength),
        "confidence_score": float(assessment.confidence_score),
        "completeness_score": float(assessment.completeness_score),
        "lineage_valid": bool(req.lineage_valid),
        "reproducible": bool(req.reproducible),
        "version_ready": version_ready(result),
        "can_advance": version_can_advance(result),
        "is_blocked": result.is_blocked,
        "requires_rollback": result.requires_rollback,
        "execution_allowed": False,
        "trade_allowed": False,
        "order_allowed": False,
        "position_change_allowed": False,
        "authorization_allowed": False,
        "d13_override": False,
        "risk_override": False,
        "cas_override": False,
    }


# ============================================================
# HARD SAFETY BOUNDARIES
# ============================================================

def version_is_safe(value: Any) -> bool:
    """
    Research version-management safety state.

    Safe means lifecycle evaluation only.
    It does NOT grant execution authority.
    """
    result = value.result if isinstance(value, VersionContract) else value

    if not validate_version_result(result):
        return False

    return not (
        result.is_blocked
        or result.requires_rollback
        or result.status == VersionResultStatus.INVALID
    )


def version_allows_execution(value: Any = None) -> bool:
    return False


def version_allows_trade(value: Any = None) -> bool:
    return False


def version_allows_order(value: Any = None) -> bool:
    return False


def version_allows_position_change(value: Any = None) -> bool:
    return False


def version_allows_authorization(value: Any = None) -> bool:
    return False


# ============================================================
# AUTHORITY BOUNDARIES
# ============================================================

def version_overrides_d13(value: Any = None) -> bool:
    return False


def version_overrides_risk(value: Any = None) -> bool:
    return False


def version_overrides_cas(value: Any = None) -> bool:
    return False


# ============================================================
# ENGINE INFORMATION
# ============================================================

def get_version_manager_engine_info() -> dict[str, Any]:
    return {
        "engine": VERSION_MANAGER_ENGINE,
        "version": VERSION_MANAGER_VERSION,
        "engine_type": "RESEARCH_VERSION_LIFECYCLE_MANAGER",
        "status": "ACTIVE",
        "research_scope": True,
        "execution_scope": False,
        "trade_scope": False,
        "order_scope": False,
        "position_scope": False,
        "authorization_scope": False,
        "d13_authority": False,
        "risk_authority": False,
        "cas_authority": False,
        "production_activation": False,
        "supports_version_evaluation": True,
        "supports_version_validation": True,
        "supports_readiness_evaluation": True,
        "supports_lifecycle_advancement": True,
    }


# ============================================================
# HEALTH CHECK
# ============================================================

def version_manager_health_check() -> dict[str, Any]:
    checks = {
        "engine_present": version_manager_engine is not None,
        "engine_type_valid": isinstance(
            version_manager_engine,
            VersionManagerEngine,
        ),
        "engine_name_valid": (
            VERSION_MANAGER_ENGINE
            == "ROBOMLM_RESEARCH_VERSION_MANAGER"
        ),
        "version_defined": bool(VERSION_MANAGER_VERSION),
        "execution_blocked": not version_allows_execution(),
        "trade_blocked": not version_allows_trade(),
        "order_blocked": not version_allows_order(),
        "position_change_blocked": not version_allows_position_change(),
        "authorization_blocked": not version_allows_authorization(),
        "d13_override_blocked": not version_overrides_d13(),
        "risk_override_blocked": not version_overrides_risk(),
        "cas_override_blocked": not version_overrides_cas(),
    }

    healthy = all(checks.values())

    return {
        "healthy": healthy,
        "engine": VERSION_MANAGER_ENGINE,
        "version": VERSION_MANAGER_VERSION,
        "checks": checks,
        "execution_safe": checks["execution_blocked"],
        "authority_safe": (
            checks["d13_override_blocked"]
            and checks["risk_override_blocked"]
            and checks["cas_override_blocked"]
        ),
    }


def run_version_manager_health_check() -> bool:
    return bool(version_manager_health_check()["healthy"])
# ============================================================
# PART 5/5 — SERIALIZATION, INTEGRITY & PUBLIC API
# ============================================================


def _vm_enum_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    return value


def _vm_safe_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def _vm_reference_to_dict(reference: VersionReference) -> dict[str, Any]:
    return {
        "version_id": reference.version_id,
        "version_name": reference.version_name,
        "version_type": _vm_enum_value(reference.version_type),
        "status": _vm_enum_value(reference.status),
        "priority": _vm_enum_value(reference.priority),
        "version_number": reference.version_number,
        "parent_version_id": reference.parent_version_id,
        "source_id": reference.source_id,
        "artifact_id": reference.artifact_id,
        "validation_id": reference.validation_id,
        "experiment_id": reference.experiment_id,
        "candidate_id": reference.candidate_id,
        "raw_version": _vm_safe_dict(reference.raw_version),
    }


def _vm_artifact_to_dict(
    artifact: Optional[VersionArtifactReference],
) -> Optional[dict[str, Any]]:
    if artifact is None:
        return None

    return {
        "artifact_id": artifact.artifact_id,
        "name": artifact.name,
        "artifact_type": artifact.artifact_type,
        "source": artifact.source,
        "checksum": artifact.checksum,
        "description": artifact.description,
        "raw_artifact": _vm_safe_dict(artifact.raw_artifact),
    }


def _vm_requirements_to_dict(
    requirements: VersionRequirements,
) -> dict[str, Any]:
    return {
        "version_available": requirements.version_available,
        "version_type_defined": requirements.version_type_defined,
        "priority_defined": requirements.priority_defined,
        "parent_available": requirements.parent_available,
        "source_available": requirements.source_available,
        "artifact_available": requirements.artifact_available,
        "validation_available": requirements.validation_available,
        "experiment_available": requirements.experiment_available,
        "candidate_available": requirements.candidate_available,
        "lineage_valid": requirements.lineage_valid,
        "reproducible": requirements.reproducible,
        "data_state": _vm_enum_value(requirements.data_state),
        "consistency": _vm_enum_value(requirements.consistency),
        "readiness": _vm_enum_value(requirements.readiness),
        "completeness_score": float(requirements.completeness_score),
        "warnings": list(requirements.warnings),
    }


def _vm_assessment_to_dict(
    assessment: VersionAssessment,
) -> dict[str, Any]:
    return {
        "decision": _vm_enum_value(assessment.decision),
        "readiness": _vm_enum_value(assessment.readiness),
        "data_state": _vm_enum_value(assessment.data_state),
        "consistency": _vm_enum_value(assessment.consistency),
        "strength": _vm_enum_value(assessment.strength),
        "confidence_score": float(assessment.confidence_score),
        "completeness_score": float(assessment.completeness_score),
        "strengths": list(assessment.strengths),
        "weaknesses": list(assessment.weaknesses),
        "rationale": assessment.rationale,
    }


def version_result_to_dict(
    result: VersionResult,
) -> dict[str, Any]:
    if not isinstance(result, VersionResult):
        return {}

    return {
        "request_id": result.request_id,
        "result_id": result.result_id,
        "status": _vm_enum_value(result.status),
        "version": _vm_reference_to_dict(result.version),
        "requirements": _vm_requirements_to_dict(result.requirements),
        "assessment": _vm_assessment_to_dict(result.assessment),
        "rationale": result.rationale,
        "warnings": list(result.warnings),
        "created_at": result.created_at.isoformat(),
        "is_valid": result.is_valid,
        "accepted": result.accepted,
        "is_conditional": result.is_conditional,
        "requires_review": result.requires_review,
        "is_blocked": result.is_blocked,
        "requires_rollback": result.requires_rollback,
        "is_action_request": result.is_action_request,
    }


def version_contract_to_dict(
    contract: VersionContract,
) -> dict[str, Any]:
    if not isinstance(contract, VersionContract):
        return {}

    return {
        "request_id": contract.request_id,
        "contract_id": contract.contract_id,
        "state": _vm_enum_value(contract.state),
        "result": version_result_to_dict(contract.result),
        "rationale": contract.rationale,
        "warnings": list(contract.warnings),
        "created_at": contract.created_at.isoformat(),
        "is_valid": contract.is_valid,
        "accepted": contract.accepted,
        "is_action_request": contract.is_action_request,
    }


# ============================================================
# CONTRACT INTEGRITY
# ============================================================

def version_manager_integrity_check(
    value: Any = None,
) -> dict[str, Any]:
    """
    Structural integrity verification for the Version Manager.

    This check validates lifecycle contracts only.
    It never activates, deploys, executes, or authorizes anything.
    """

    if value is None:
        health = version_manager_health_check()

        return {
            "healthy": health["healthy"],
            "engine": VERSION_MANAGER_ENGINE,
            "version": VERSION_MANAGER_VERSION,
            "mode": "ENGINE_INTEGRITY",
            "checks": health["checks"],
        }

    if isinstance(value, VersionContract):
        result_valid = validate_version_result(value.result)
        contract_valid = validate_version_contract(value)

        return {
            "healthy": bool(contract_valid),
            "engine": VERSION_MANAGER_ENGINE,
            "version": VERSION_MANAGER_VERSION,
            "mode": "CONTRACT_INTEGRITY",
            "contract_valid": contract_valid,
            "result_valid": result_valid,
            "contract_state": _vm_enum_value(value.state),
            "version_ready": version_ready(value),
            "can_advance": version_can_advance(value),
            "execution_allowed": False,
            "trade_allowed": False,
            "order_allowed": False,
            "position_change_allowed": False,
            "authorization_allowed": False,
            "d13_override": False,
            "risk_override": False,
            "cas_override": False,
        }

    if isinstance(value, VersionResult):
        result_valid = validate_version_result(value)

        return {
            "healthy": bool(result_valid),
            "engine": VERSION_MANAGER_ENGINE,
            "version": VERSION_MANAGER_VERSION,
            "mode": "RESULT_INTEGRITY",
            "result_valid": result_valid,
            "status": _vm_enum_value(value.status),
            "decision": _vm_enum_value(
                value.assessment.decision
            ),
            "version_ready": version_ready(value),
            "can_advance": version_can_advance(value),
            "execution_allowed": False,
            "trade_allowed": False,
            "order_allowed": False,
            "position_change_allowed": False,
            "authorization_allowed": False,
            "d13_override": False,
            "risk_override": False,
            "cas_override": False,
        }

    return {
        "healthy": False,
        "engine": VERSION_MANAGER_ENGINE,
        "version": VERSION_MANAGER_VERSION,
        "mode": "INVALID_INPUT",
        "reason": "Unsupported integrity-check object",
    }


def verify_version_manager_integrity(
    value: Any = None,
) -> bool:
    return bool(
        version_manager_integrity_check(value)["healthy"]
    )


def run_version_manager_integrity_check() -> bool:
    return verify_version_manager_integrity()


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    # Constants
    "VERSION_MANAGER_ENGINE",
    "VERSION_MANAGER_VERSION",

    # Enums
    "VersionStatus",
    "VersionType",
    "VersionPriority",
    "VersionDecision",
    "VersionContractStatus",
    "VersionDataState",
    "VersionConsistency",
    "VersionReadiness",
    "VersionStrength",
    "VersionResultStatus",
    "VersionContractState",

    # Core request/reference contracts
    "VersionRequest",
    "VersionReference",
    "VersionArtifactReference",
    "VersionContractValidation",

    # Requirements / assessment
    "VersionRequirements",
    "VersionAssessment",

    # Result / contract
    "VersionResult",
    "VersionContract",

    # Builders
    "build_version_reference",
    "validate_version_request",
    "evaluate_version_data_state",
    "evaluate_version_consistency",
    "evaluate_version_requirements",
    "evaluate_version_readiness",
    "calculate_version_confidence",
    "determine_version_strength",
    "determine_version_decision",
    "build_version_assessment",
    "build_version_result",
    "build_version_contract",

    # Engine
    "VersionManagerEngine",
    "version_manager_engine",

    # Main operations
    "evaluate_version",
    "analyze_version",
    "review_version",

    # Validation
    "validate_version_result",
    "validate_version_contract",

    # Readiness / lifecycle
    "version_ready",
    "version_can_advance",

    # Accessors
    "version_status",
    "version_decision",
    "version_readiness",
    "version_confidence",
    "version_strength",
    "version_completeness",

    # Audit
    "version_audit",

    # Safety
    "version_is_safe",
    "version_allows_execution",
    "version_allows_trade",
    "version_allows_order",
    "version_allows_position_change",
    "version_allows_authorization",

    # Authority boundaries
    "version_overrides_d13",
    "version_overrides_risk",
    "version_overrides_cas",

    # Engine information
    "get_version_manager_engine_info",

    # Health
    "version_manager_health_check",
    "run_version_manager_health_check",

    # Serialization
    "version_result_to_dict",
    "version_contract_to_dict",

    # Integrity
    "version_manager_integrity_check",
    "verify_version_manager_integrity",
    "run_version_manager_integrity_check",
]
