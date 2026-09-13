# ============================================================
# ROBOMLM_PLUS
# app/intelligence/research/research_service.py
# RESEARCH SERVICE
# PART 1/5
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Optional
from uuid import uuid4


RESEARCH_SERVICE_ENGINE = "ROBOMLM_RESEARCH_SERVICE"
RESEARCH_SERVICE_VERSION = "1.0"


# ============================================================
# ENUMS
# ============================================================

class ResearchServiceStatus(str, Enum):
    NEW = "NEW"
    INITIALIZED = "INITIALIZED"
    PROCESSING = "PROCESSING"
    READY = "READY"
    REVIEW = "REVIEW"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"
    UNKNOWN = "UNKNOWN"


class ResearchServiceOperation(str, Enum):
    REGISTER = "REGISTER"
    ANALYZE = "ANALYZE"
    EVALUATE = "EVALUATE"
    VALIDATE = "VALIDATE"
    STRESS_TEST = "STRESS_TEST"
    VERSION = "VERSION"
    DEPLOYMENT_REVIEW = "DEPLOYMENT_REVIEW"
    STATUS = "STATUS"
    UNKNOWN = "UNKNOWN"


class ResearchServicePriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class ResearchServiceDecision(str, Enum):
    PROCEED = "PROCEED"
    REVIEW = "REVIEW"
    HOLD = "HOLD"
    BLOCK = "BLOCK"
    REJECT = "REJECT"
    UNKNOWN = "UNKNOWN"


class ResearchServiceContractStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


# ============================================================
# REQUEST CONTRACT
# ============================================================

@dataclass(frozen=True)
class ResearchServiceRequest:
    research: Any
    operation: ResearchServiceOperation = (
        ResearchServiceOperation.UNKNOWN
    )
    priority: ResearchServicePriority = (
        ResearchServicePriority.UNKNOWN
    )

    candidate: Any = None
    dataset: Any = None
    hypothesis: Any = None
    experiment: Any = None
    validation: Any = None
    deployment: Any = None
    version: Any = None
    stress_test: Any = None

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    request_id: str = field(
        default_factory=lambda: (
            f"RSQ-{uuid4().hex[:12].upper()}"
        )
    )

    timestamp: str = field(
        default_factory=lambda: (
            datetime.now(timezone.utc).isoformat()
        )
    )

    def validate(self) -> bool:
        if self.research is None:
            return False

        if not self.request_id:
            return False

        if not isinstance(self.metadata, Mapping):
            return False

        return True


# ============================================================
# RESEARCH REFERENCE
# ============================================================

@dataclass(frozen=True)
class ResearchReference:
    research_id: str
    name: str
    research_type: str
    status: ResearchServiceStatus
    priority: ResearchServicePriority

    candidate_id: Optional[str] = None
    dataset_id: Optional[str] = None
    hypothesis_id: Optional[str] = None
    experiment_id: Optional[str] = None
    validation_id: Optional[str] = None
    deployment_id: Optional[str] = None
    version_id: Optional[str] = None

    raw_research: Any = None


@dataclass(frozen=True)
class ResearchServiceContractValidation:
    valid: bool
    status: ResearchServiceContractStatus
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    request_id: str = ""


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _rs_read(
    source: Any,
    *keys: str,
    default: Any = None,
) -> Any:

    if source is None:
        return default

    if isinstance(source, Mapping):
        for key in keys:
            if key in source:
                return source[key]

    for key in keys:
        try:
            value = getattr(source, key)
        except Exception:
            continue

        if value is not None:
            return value

    return default


def _rs_text(
    value: Any,
    default: str = "",
) -> str:

    if value is None:
        return default

    text = str(value).strip()

    return text if text else default


def _rs_enum(
    value: Any,
    enum_cls: type[Enum],
    default: Enum,
) -> Enum:

    if isinstance(value, enum_cls):
        return value

    if value is None:
        return default

    text = str(value).strip().upper()

    for item in enum_cls:
        if item.value == text:
            return item

    return default


# ============================================================
# REFERENCE BUILDER
# ============================================================

def build_research_reference(
    request: ResearchServiceRequest,
) -> ResearchReference:

    raw = request.research

    research_id = _rs_text(
        _rs_read(
            raw,
            "research_id",
            "id",
            "identifier",
            default="",
        )
    )

    if not research_id:
        research_id = (
            f"RES-{uuid4().hex[:12].upper()}"
        )

    name = _rs_text(
        _rs_read(
            raw,
            "name",
            "title",
            "research_name",
            default="Research",
        ),
        default="Research",
    )

    research_type = _rs_text(
        _rs_read(
            raw,
            "research_type",
            "type",
            "category",
            default="UNKNOWN",
        ),
        default="UNKNOWN",
    )

    status = _rs_enum(
        _rs_read(
            raw,
            "status",
            default=ResearchServiceStatus.NEW,
        ),
        ResearchServiceStatus,
        ResearchServiceStatus.NEW,
    )

    priority = _rs_enum(
        _rs_read(
            raw,
            "priority",
            default=request.priority,
        ),
        ResearchServicePriority,
        request.priority,
    )

    def _component_id(
        request_value: Any,
        raw_keys: tuple[str, ...],
    ) -> Optional[str]:

        value = request_value

        if value is None:
            value = _rs_read(
                raw,
                *raw_keys,
                default=None,
            )

        if value is None:
            return None

        if isinstance(value, Mapping):
            value = _rs_read(
                value,
                "id",
                "identifier",
                "candidate_id",
                "dataset_id",
                "hypothesis_id",
                "experiment_id",
                "validation_id",
                "deployment_id",
                "version_id",
                default=None,
            )

        if value is None:
            return None

        return _rs_text(value) or None

    return ResearchReference(
        research_id=research_id,
        name=name,
        research_type=research_type,
        status=status,
        priority=priority,

        candidate_id=_component_id(
            request.candidate,
            ("candidate_id", "candidate"),
        ),

        dataset_id=_component_id(
            request.dataset,
            ("dataset_id", "dataset"),
        ),

        hypothesis_id=_component_id(
            request.hypothesis,
            ("hypothesis_id", "hypothesis"),
        ),

        experiment_id=_component_id(
            request.experiment,
            ("experiment_id", "experiment"),
        ),

        validation_id=_component_id(
            request.validation,
            ("validation_id", "validation"),
        ),

        deployment_id=_component_id(
            request.deployment,
            ("deployment_id", "deployment"),
        ),

        version_id=_component_id(
            request.version,
            ("version_id", "version"),
        ),

        raw_research=raw,
    )


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_research_service_request(
    request: ResearchServiceRequest,
) -> ResearchServiceContractValidation:

    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(
        request,
        ResearchServiceRequest,
    ):
        return ResearchServiceContractValidation(
            valid=False,
            status=ResearchServiceContractStatus.INVALID,
            errors=("invalid_request_type",),
        )

    if request.research is None:
        errors.append("research_missing")

    if not request.request_id:
        errors.append("request_id_missing")

    if not isinstance(request.metadata, Mapping):
        errors.append("metadata_not_mapping")

    if (
        request.operation
        == ResearchServiceOperation.UNKNOWN
    ):
        warnings.append("operation_unspecified")

    if (
        request.priority
        == ResearchServicePriority.UNKNOWN
    ):
        warnings.append("priority_unspecified")

    valid = not errors

    return ResearchServiceContractValidation(
        valid=valid,
        status=(
            ResearchServiceContractStatus.VALID
            if valid
            else ResearchServiceContractStatus.INVALID
        ),
        errors=tuple(errors),
        warnings=tuple(warnings),
        request_id=request.request_id,
    )
# ============================================================
# ROBOMLM_PLUS
# app/intelligence/research/research_service.py
# RESEARCH SERVICE
# PART 2/5
# ============================================================

class ResearchDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    UNKNOWN = "UNKNOWN"


class ResearchConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONFLICTING = "CONFLICTING"
    INSUFFICIENT = "INSUFFICIENT"
    UNKNOWN = "UNKNOWN"


class ResearchReadiness(str, Enum):
    READY = "READY"
    CONDITIONAL = "CONDITIONAL"
    NOT_READY = "NOT_READY"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ResearchRequirements:
    research_available: bool
    candidate_available: bool
    dataset_available: bool
    hypothesis_available: bool
    experiment_available: bool
    validation_available: bool
    deployment_available: bool
    version_available: bool
    operation_defined: bool
    data_state: ResearchDataState
    consistency: ResearchConsistency
    readiness: ResearchReadiness
    completeness_score: float
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class ResearchAssessment:
    decision: ResearchServiceDecision
    readiness: ResearchReadiness
    data_state: ResearchDataState
    consistency: ResearchConsistency
    confidence_score: float
    completeness_score: float
    strengths: tuple[str, ...] = ()
    weaknesses: tuple[str, ...] = ()
    rationale: str = ""


# ============================================================
# COMPONENT AVAILABILITY
# ============================================================

def _rs_component_available(
    value: Any,
) -> bool:

    if value is None:
        return False

    if isinstance(value, Mapping):
        return bool(
            value.get("id")
            or value.get("identifier")
            or value.get("name")
            or value.get("title")
        )

    return bool(value)


# ============================================================
# REQUIREMENTS EVALUATION
# ============================================================

def evaluate_research_requirements(
    request: ResearchServiceRequest,
    reference: ResearchReference,
) -> ResearchRequirements:

    research_available = bool(
        request.research is not None
        and reference.research_id
    )

    candidate_available = (
        request.candidate is not None
        or bool(reference.candidate_id)
    )

    dataset_available = (
        request.dataset is not None
        or bool(reference.dataset_id)
    )

    hypothesis_available = (
        request.hypothesis is not None
        or bool(reference.hypothesis_id)
    )

    experiment_available = (
        request.experiment is not None
        or bool(reference.experiment_id)
    )

    validation_available = (
        request.validation is not None
        or bool(reference.validation_id)
    )

    deployment_available = (
        request.deployment is not None
        or bool(reference.deployment_id)
    )

    version_available = (
        request.version is not None
        or bool(reference.version_id)
    )

    operation_defined = (
        request.operation
        != ResearchServiceOperation.UNKNOWN
    )

    components = (
        research_available,
        candidate_available,
        dataset_available,
        hypothesis_available,
        experiment_available,
        validation_available,
        deployment_available,
        version_available,
        operation_defined,
    )

    completeness_score = round(
        sum(
            1
            for value in components
            if value
        )
        / len(components)
        * 100.0,
        2,
    )

    available_count = sum(
        1 for value in components if value
    )

    if available_count == len(components):
        data_state = ResearchDataState.COMPLETE
    elif available_count > 0:
        data_state = ResearchDataState.PARTIAL
    else:
        data_state = ResearchDataState.MISSING

    warnings: list[str] = []

    if not candidate_available:
        warnings.append("candidate_missing")

    if not dataset_available:
        warnings.append("dataset_missing")

    if not hypothesis_available:
        warnings.append("hypothesis_missing")

    if not experiment_available:
        warnings.append("experiment_missing")

    if not validation_available:
        warnings.append("validation_missing")

    if not version_available:
        warnings.append("version_missing")

    if not operation_defined:
        warnings.append("operation_unspecified")

    # Service-level consistency is evaluated from explicit
    # conflict information only. No research conclusion is
    # invented here.
    raw = request.research
    conflict_value = _rs_read(
        raw,
        "conflict",
        "conflicts",
        "inconsistent",
        "consistency",
        default=None,
    )

    if isinstance(conflict_value, bool):
        consistency = (
            ResearchConsistency.CONFLICTING
            if conflict_value
            else ResearchConsistency.CONSISTENT
        )
    elif isinstance(conflict_value, str):
        normalized = conflict_value.strip().upper()

        if normalized in {
            "CONFLICTING",
            "CONFLICT",
            "INCONSISTENT",
        }:
            consistency = ResearchConsistency.CONFLICTING
        elif normalized in {
            "CONSISTENT",
            "ALIGNED",
            "OK",
        }:
            consistency = ResearchConsistency.CONSISTENT
        else:
            consistency = ResearchConsistency.INSUFFICIENT
    else:
        consistency = ResearchConsistency.INSUFFICIENT

    if consistency == ResearchConsistency.CONFLICTING:
        readiness = ResearchReadiness.NOT_READY
    elif completeness_score >= 80.0:
        readiness = ResearchReadiness.READY
    elif completeness_score >= 40.0:
        readiness = ResearchReadiness.CONDITIONAL
    else:
        readiness = ResearchReadiness.NOT_READY

    return ResearchRequirements(
        research_available=research_available,
        candidate_available=candidate_available,
        dataset_available=dataset_available,
        hypothesis_available=hypothesis_available,
        experiment_available=experiment_available,
        validation_available=validation_available,
        deployment_available=deployment_available,
        version_available=version_available,
        operation_defined=operation_defined,
        data_state=data_state,
        consistency=consistency,
        readiness=readiness,
        completeness_score=completeness_score,
        warnings=tuple(warnings),
    )


# ============================================================
# READINESS EVALUATION
# ============================================================

def evaluate_research_readiness(
    requirements: ResearchRequirements,
) -> ResearchReadiness:

    if not requirements.research_available:
        return ResearchReadiness.NOT_READY

    if (
        requirements.consistency
        == ResearchConsistency.CONFLICTING
    ):
        return ResearchReadiness.NOT_READY

    if requirements.data_state == ResearchDataState.MISSING:
        return ResearchReadiness.NOT_READY

    if (
        requirements.completeness_score >= 80.0
        and requirements.operation_defined
    ):
        return ResearchReadiness.READY

    if requirements.completeness_score >= 40.0:
        return ResearchReadiness.CONDITIONAL

    return ResearchReadiness.NOT_READY


# ============================================================
# CONFIDENCE EVALUATION
# ============================================================

def calculate_research_confidence(
    requirements: ResearchRequirements,
) -> float:

    score = 0.0

    if requirements.research_available:
        score += 20.0

    if requirements.candidate_available:
        score += 10.0

    if requirements.dataset_available:
        score += 15.0

    if requirements.hypothesis_available:
        score += 15.0

    if requirements.experiment_available:
        score += 10.0

    if requirements.validation_available:
        score += 15.0

    if requirements.version_available:
        score += 5.0

    if requirements.operation_defined:
        score += 10.0

    if (
        requirements.consistency
        == ResearchConsistency.CONFLICTING
    ):
        score -= 30.0

    return round(
        min(max(score, 0.0), 100.0),
        2,
    )


# ============================================================
# SERVICE DECISION
# ============================================================

def determine_research_service_decision(
    requirements: ResearchRequirements,
    confidence_score: float,
) -> ResearchServiceDecision:

    if (
        requirements.consistency
        == ResearchConsistency.CONFLICTING
    ):
        return ResearchServiceDecision.BLOCK

    if requirements.data_state == ResearchDataState.MISSING:
        return ResearchServiceDecision.HOLD

    if not requirements.research_available:
        return ResearchServiceDecision.BLOCK

    if not requirements.operation_defined:
        return ResearchServiceDecision.REVIEW

    if confidence_score >= 80.0:
        return ResearchServiceDecision.PROCEED

    if confidence_score >= 50.0:
        return ResearchServiceDecision.REVIEW

    return ResearchServiceDecision.HOLD


# ============================================================
# ASSESSMENT BUILDER
# ============================================================

def build_research_assessment(
    request: ResearchServiceRequest,
    reference: ResearchReference,
    requirements: ResearchRequirements,
) -> ResearchAssessment:

    readiness = evaluate_research_readiness(
        requirements
    )

    confidence_score = calculate_research_confidence(
        requirements
    )

    decision = determine_research_service_decision(
        requirements,
        confidence_score,
    )

    strengths: list[str] = []
    weaknesses: list[str] = []

    if requirements.research_available:
        strengths.append("research_available")

    if requirements.dataset_available:
        strengths.append("dataset_available")

    if requirements.hypothesis_available:
        strengths.append("hypothesis_available")

    if requirements.experiment_available:
        strengths.append("experiment_available")

    if requirements.validation_available:
        strengths.append("validation_available")

    if requirements.version_available:
        strengths.append("version_available")

    for warning in requirements.warnings:
        weaknesses.append(warning)

    if (
        requirements.consistency
        == ResearchConsistency.CONFLICTING
    ):
        weaknesses.append("research_conflict")

    rationale = (
        f"readiness={readiness.value}; "
        f"confidence={confidence_score:.2f}; "
        f"completeness="
        f"{requirements.completeness_score:.2f}; "
        f"decision={decision.value}"
    )

    return ResearchAssessment(
        decision=decision,
        readiness=readiness,
        data_state=requirements.data_state,
        consistency=requirements.consistency,
        confidence_score=confidence_score,
        completeness_score=requirements.completeness_score,
        strengths=tuple(strengths),
        weaknesses=tuple(weaknesses),
        rationale=rationale,
    )
# ============================================================
# ROBOMLM_PLUS
# app/intelligence/research/research_service.py
# RESEARCH SERVICE
# PART 3/5
# ============================================================


class ResearchServiceResultStatus(str, Enum):
    PROCEED = "PROCEED"
    REVIEW = "REVIEW"
    HOLD = "HOLD"
    BLOCKED = "BLOCKED"
    REJECTED = "REJECTED"
    INVALID = "INVALID"


class ResearchServiceContractState(str, Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


@dataclass(frozen=True)
class ResearchServiceResult:
    request_id: str
    result_id: str
    status: ResearchServiceResultStatus

    research: ResearchReference
    requirements: ResearchRequirements
    assessment: ResearchAssessment

    rationale: str = ""
    warnings: tuple[str, ...] = ()

    created_at: str = field(
        default_factory=lambda: (
            datetime.now(timezone.utc).isoformat()
        )
    )

    @property
    def is_valid(self) -> bool:
        return (
            bool(self.request_id)
            and bool(self.result_id)
            and bool(self.research.research_id)
            and self.status
            != ResearchServiceResultStatus.INVALID
        )

    @property
    def can_proceed(self) -> bool:
        return (
            self.is_valid
            and self.status
            == ResearchServiceResultStatus.PROCEED
        )

    @property
    def requires_review(self) -> bool:
        return (
            self.status
            == ResearchServiceResultStatus.REVIEW
        )

    @property
    def requires_hold(self) -> bool:
        return (
            self.status
            == ResearchServiceResultStatus.HOLD
        )

    @property
    def is_blocked(self) -> bool:
        return (
            self.status
            == ResearchServiceResultStatus.BLOCKED
        )

    @property
    def is_action_request(self) -> bool:
        return False


@dataclass(frozen=True)
class ResearchServiceContract:
    request_id: str
    contract_id: str
    state: ResearchServiceContractState

    result: ResearchServiceResult

    rationale: str = ""
    warnings: tuple[str, ...] = ()

    created_at: str = field(
        default_factory=lambda: (
            datetime.now(timezone.utc).isoformat()
        )
    )

    @property
    def is_valid(self) -> bool:
        return (
            bool(self.request_id)
            and bool(self.contract_id)
            and self.state
            != ResearchServiceContractState.INVALID
            and self.result.is_valid
        )

    @property
    def can_proceed(self) -> bool:
        return (
            self.is_valid
            and self.state
            == ResearchServiceContractState.COMPLETE
            and self.result.can_proceed
        )

    @property
    def is_action_request(self) -> bool:
        return False


# ============================================================
# RESULT STATUS
# ============================================================

def determine_research_result_status(
    assessment: ResearchAssessment,
) -> ResearchServiceResultStatus:

    decision = assessment.decision

    if decision == ResearchServiceDecision.PROCEED:
        return ResearchServiceResultStatus.PROCEED

    if decision == ResearchServiceDecision.REVIEW:
        return ResearchServiceResultStatus.REVIEW

    if decision == ResearchServiceDecision.HOLD:
        return ResearchServiceResultStatus.HOLD

    if decision == ResearchServiceDecision.BLOCK:
        return ResearchServiceResultStatus.BLOCKED

    if decision == ResearchServiceDecision.REJECT:
        return ResearchServiceResultStatus.REJECTED

    return ResearchServiceResultStatus.INVALID


# ============================================================
# RESULT BUILDER
# ============================================================

def build_research_service_result(
    request: ResearchServiceRequest,
    reference: ResearchReference,
    requirements: ResearchRequirements,
    assessment: ResearchAssessment,
) -> ResearchServiceResult:

    status = determine_research_result_status(
        assessment
    )

    warnings = list(requirements.warnings)

    warnings.extend(
        assessment.weaknesses
    )

    rationale = (
        f"research_result={status.value}; "
        f"operation="
        f"{request.operation.value}; "
        f"readiness="
        f"{assessment.readiness.value}; "
        f"confidence="
        f"{assessment.confidence_score:.2f}; "
        f"decision="
        f"{assessment.decision.value}"
    )

    return ResearchServiceResult(
        request_id=request.request_id,
        result_id=(
            f"RS-RES-{uuid4().hex[:12].upper()}"
        ),
        status=status,
        research=reference,
        requirements=requirements,
        assessment=assessment,
        rationale=rationale,
        warnings=tuple(
            dict.fromkeys(warnings)
        ),
    )


# ============================================================
# CONTRACT STATE
# ============================================================

def determine_research_contract_state(
    result: ResearchServiceResult,
) -> ResearchServiceContractState:

    if not result.is_valid:
        return ResearchServiceContractState.INVALID

    if result.status == ResearchServiceResultStatus.INVALID:
        return ResearchServiceContractState.INVALID

    if result.status in {
        ResearchServiceResultStatus.HOLD,
        ResearchServiceResultStatus.BLOCKED,
        ResearchServiceResultStatus.REJECTED,
    }:
        return ResearchServiceContractState.BLOCKED

    if not result.research.research_id:
        return ResearchServiceContractState.INCOMPLETE

    return ResearchServiceContractState.COMPLETE


# ============================================================
# CONTRACT BUILDER
# ============================================================

def build_research_service_contract(
    request: ResearchServiceRequest,
    result: ResearchServiceResult,
) -> ResearchServiceContract:

    state = determine_research_contract_state(
        result
    )

    return ResearchServiceContract(
        request_id=request.request_id,
        contract_id=(
            f"RS-CON-{uuid4().hex[:12].upper()}"
        ),
        state=state,
        result=result,
        rationale=result.rationale,
        warnings=result.warnings,
    )


# ============================================================
# CENTRAL RESEARCH SERVICE ENGINE
# ============================================================

class ResearchServiceEngine:

    engine_name = RESEARCH_SERVICE_ENGINE
    version = RESEARCH_SERVICE_VERSION

    def validate_request(
        self,
        request: ResearchServiceRequest,
    ) -> ResearchServiceContractValidation:

        return validate_research_service_request(
            request
        )

    def evaluate(
        self,
        request: ResearchServiceRequest,
    ) -> ResearchServiceContract:

        validation = self.validate_request(
            request
        )

        reference = build_research_reference(
            request
        )

        requirements = evaluate_research_requirements(
            request,
            reference,
        )

        if not validation.valid:

            assessment = ResearchAssessment(
                decision=ResearchServiceDecision.BLOCK,
                readiness=ResearchReadiness.NOT_READY,
                data_state=requirements.data_state,
                consistency=requirements.consistency,
                confidence_score=0.0,
                completeness_score=(
                    requirements.completeness_score
                ),
                strengths=(),
                weaknesses=(
                    "request_contract_invalid",
                ),
                rationale=(
                    "Research service request "
                    "contract is invalid."
                ),
            )

            result = ResearchServiceResult(
                request_id=request.request_id,
                result_id=(
                    f"RS-RES-{uuid4().hex[:12].upper()}"
                ),
                status=(
                    ResearchServiceResultStatus.INVALID
                ),
                research=reference,
                requirements=requirements,
                assessment=assessment,
                rationale=(
                    "Invalid research service request."
                ),
                warnings=(
                    "request_contract_invalid",
                ),
            )

            return ResearchServiceContract(
                request_id=request.request_id,
                contract_id=(
                    f"RS-CON-{uuid4().hex[:12].upper()}"
                ),
                state=(
                    ResearchServiceContractState.INVALID
                ),
                result=result,
                rationale=(
                    "Research request rejected "
                    "by contract validation."
                ),
                warnings=(
                    "request_contract_invalid",
                ),
            )

        assessment = build_research_assessment(
            request,
            reference,
            requirements,
        )

        result = build_research_service_result(
            request,
            reference,
            requirements,
            assessment,
        )

        return build_research_service_contract(
            request,
            result,
        )


# ============================================================
# PUBLIC ENGINE INSTANCE
# ============================================================

research_service_engine = ResearchServiceEngine()


# ============================================================
# PUBLIC SERVICE FUNCTIONS
# ============================================================

def evaluate_research(
    request: ResearchServiceRequest,
) -> ResearchServiceContract:

    return research_service_engine.evaluate(
        request
    )


def analyze_research(
    request: ResearchServiceRequest,
) -> ResearchServiceContract:

    return research_service_engine.evaluate(
        request
    )


def process_research(
    request: ResearchServiceRequest,
) -> ResearchServiceContract:

    return research_service_engine.evaluate(
        request
    )


def review_research(
    request: ResearchServiceRequest,
) -> ResearchServiceContract:

    return research_service_engine.evaluate(
        request
    )
# ============================================================
# ROBOMLM_PLUS
# app/intelligence/research/research_service.py
# RESEARCH SERVICE
# PART 4/5
# ============================================================


def validate_research_service_result(
    result: ResearchServiceResult,
) -> bool:

    if not isinstance(result, ResearchServiceResult):
        return False

    if not result.is_valid:
        return False

    if not result.research.research_id:
        return False

    if not 0.0 <= result.assessment.confidence_score <= 100.0:
        return False

    if not 0.0 <= result.assessment.completeness_score <= 100.0:
        return False

    return True


def validate_research_service_contract(
    contract: ResearchServiceContract,
) -> bool:

    if not isinstance(contract, ResearchServiceContract):
        return False

    if not contract.is_valid:
        return False

    return validate_research_service_result(
        contract.result
    )


# ============================================================
# READINESS / ADVANCE GATES
# ============================================================

def research_ready(
    contract: ResearchServiceContract,
) -> bool:

    if not validate_research_service_contract(contract):
        return False

    result = contract.result
    assessment = result.assessment
    requirements = result.requirements

    return (
        contract.state
        == ResearchServiceContractState.COMPLETE
        and result.status
        == ResearchServiceResultStatus.PROCEED
        and assessment.decision
        == ResearchServiceDecision.PROCEED
        and assessment.readiness
        == ResearchReadiness.READY
        and assessment.confidence_score >= 80.0
        and requirements.research_available
        and requirements.operation_defined
        and requirements.consistency
        == ResearchConsistency.CONSISTENT
    )


def research_can_advance(
    contract: ResearchServiceContract,
) -> bool:

    if not validate_research_service_contract(contract):
        return False

    if (
        contract.state
        != ResearchServiceContractState.COMPLETE
    ):
        return False

    return research_ready(contract)


# ============================================================
# STATE ACCESSORS
# ============================================================

def research_status(
    contract: ResearchServiceContract,
) -> ResearchServiceStatus:

    if not validate_research_service_contract(contract):
        return ResearchServiceStatus.FAILED

    return contract.result.research.status


def research_decision(
    contract: ResearchServiceContract,
) -> ResearchServiceDecision:

    if not validate_research_service_contract(contract):
        return ResearchServiceDecision.UNKNOWN

    return contract.result.assessment.decision


def research_readiness(
    contract: ResearchServiceContract,
) -> ResearchReadiness:

    if not validate_research_service_contract(contract):
        return ResearchReadiness.UNKNOWN

    return contract.result.assessment.readiness


def research_confidence(
    contract: ResearchServiceContract,
) -> float:

    if not validate_research_service_contract(contract):
        return 0.0

    return contract.result.assessment.confidence_score


def research_completeness(
    contract: ResearchServiceContract,
) -> float:

    if not validate_research_service_contract(contract):
        return 0.0

    return contract.result.assessment.completeness_score


# ============================================================
# AUDIT
# ============================================================

def research_audit(
    contract: ResearchServiceContract,
) -> dict[str, Any]:

    if not validate_research_service_contract(contract):
        return {
            "valid": False,
            "engine": RESEARCH_SERVICE_ENGINE,
            "version": RESEARCH_SERVICE_VERSION,
            "status": ResearchServiceStatus.FAILED.value,
            "decision": ResearchServiceDecision.UNKNOWN.value,
            "readiness": ResearchReadiness.UNKNOWN.value,
            "confidence": 0.0,
            "completeness": 0.0,
            "can_advance": False,
        }

    result = contract.result
    requirements = result.requirements
    assessment = result.assessment

    return {
        "valid": True,
        "engine": RESEARCH_SERVICE_ENGINE,
        "version": RESEARCH_SERVICE_VERSION,
        "request_id": contract.request_id,
        "contract_id": contract.contract_id,
        "research_id": result.research.research_id,
        "research_name": result.research.name,
        "research_type": result.research.research_type,
        "operation": None,
        "status": result.status.value,
        "decision": assessment.decision.value,
        "readiness": assessment.readiness.value,
        "data_state": assessment.data_state.value,
        "consistency": assessment.consistency.value,
        "confidence": assessment.confidence_score,
        "completeness": assessment.completeness_score,
        "candidate_available": requirements.candidate_available,
        "dataset_available": requirements.dataset_available,
        "hypothesis_available": requirements.hypothesis_available,
        "experiment_available": requirements.experiment_available,
        "validation_available": requirements.validation_available,
        "deployment_available": requirements.deployment_available,
        "version_available": requirements.version_available,
        "operation_defined": requirements.operation_defined,
        "can_proceed": result.can_proceed,
        "can_advance": research_can_advance(contract),
        "warnings": list(result.warnings),
    }


# ============================================================
# SAFETY BOUNDARY
# ============================================================

def research_is_safe(
    contract: ResearchServiceContract,
) -> bool:

    return (
        validate_research_service_contract(contract)
        and not contract.is_action_request
    )


def research_allows_execution(
    contract: Optional[ResearchServiceContract],
) -> bool:
    return False


def research_allows_trade(
    contract: Optional[ResearchServiceContract],
) -> bool:
    return False


def research_allows_order(
    contract: Optional[ResearchServiceContract],
) -> bool:
    return False


def research_allows_position_change(
    contract: Optional[ResearchServiceContract],
) -> bool:
    return False


def research_allows_authorization(
    contract: Optional[ResearchServiceContract],
) -> bool:
    return False


def research_overrides_decision(
    contract: Optional[ResearchServiceContract],
) -> bool:
    return False


def research_overrides_risk(
    contract: Optional[ResearchServiceContract],
) -> bool:
    return False


def research_overrides_cas(
    contract: Optional[ResearchServiceContract],
) -> bool:
    return False


# ============================================================
# ENGINE INFORMATION
# ============================================================

def get_research_service_engine_info() -> dict[str, Any]:

    return {
        "engine": RESEARCH_SERVICE_ENGINE,
        "version": RESEARCH_SERVICE_VERSION,
        "domain": "research",
        "role": "research_service_orchestration",
        "produces_execution": False,
        "produces_orders": False,
        "produces_authorization": False,
        "overrides_d13": False,
        "overrides_risk": False,
        "overrides_cas": False,
    }


# ============================================================
# HEALTH CHECK
# ============================================================

def research_service_health_check() -> dict[str, Any]:

    checks = {
        "engine_name": bool(
            RESEARCH_SERVICE_ENGINE
        ),
        "version": bool(
            RESEARCH_SERVICE_VERSION
        ),
        "engine_instance": isinstance(
            research_service_engine,
            ResearchServiceEngine,
        ),
        "request_validation": callable(
            validate_research_service_request
        ),
        "reference_builder": callable(
            build_research_reference
        ),
        "requirements_evaluator": callable(
            evaluate_research_requirements
        ),
        "readiness_evaluator": callable(
            evaluate_research_readiness
        ),
        "assessment_builder": callable(
            build_research_assessment
        ),
        "result_builder": callable(
            build_research_service_result
        ),
        "contract_builder": callable(
            build_research_service_contract
        ),
        "result_validation": callable(
            validate_research_service_result
        ),
        "contract_validation": callable(
            validate_research_service_contract
        ),
        "audit_available": callable(
            research_audit
        ),
        "execution_disabled": (
            research_allows_execution(None) is False
        ),
        "trade_disabled": (
            research_allows_trade(None) is False
        ),
        "order_disabled": (
            research_allows_order(None) is False
        ),
        "position_change_disabled": (
            research_allows_position_change(None) is False
        ),
        "authorization_disabled": (
            research_allows_authorization(None) is False
        ),
        "d13_override_disabled": (
            research_overrides_decision(None) is False
        ),
        "risk_override_disabled": (
            research_overrides_risk(None) is False
        ),
        "cas_override_disabled": (
            research_overrides_cas(None) is False
        ),
    }

    return {
        "engine": RESEARCH_SERVICE_ENGINE,
        "version": RESEARCH_SERVICE_VERSION,
        "healthy": all(checks.values()),
        "checks": checks,
    }


def run_research_service_health_check() -> dict[str, Any]:
    return research_service_health_check()
# ============================================================
# PART 5 â€” SERIALIZATION / INTEGRITY / EXPORTS
# ============================================================

def _rs_enum_value(value: Any) -> Any:
    """Return enum value when applicable, otherwise preserve value."""
    if isinstance(value, Enum):
        return value.value
    return value


def _rs_safe_dict(value: Any) -> dict[str, Any]:
    """Safely convert mapping/dataclass-like objects to a dictionary."""
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


def _rs_reference_to_dict(reference: Optional[ResearchReference]) -> dict[str, Any]:
    """Serialize ResearchReference without exposing unsafe object internals."""
    if reference is None:
        return {}

    return {
        "research_id": reference.research_id,
        "name": reference.name,
        "research_type": _rs_enum_value(reference.research_type),
        "status": _rs_enum_value(reference.status),
        "priority": _rs_enum_value(reference.priority),
        "candidate_id": reference.candidate_id,
        "dataset_id": reference.dataset_id,
        "hypothesis_id": reference.hypothesis_id,
        "experiment_id": reference.experiment_id,
        "validation_id": reference.validation_id,
        "deployment_id": reference.deployment_id,
        "version_id": reference.version_id,
    }


def _rs_requirements_to_dict(
    requirements: Optional[ResearchRequirements],
) -> dict[str, Any]:
    """Serialize research requirements."""
    if requirements is None:
        return {}

    return {
        "research_available": requirements.research_available,
        "candidate_available": requirements.candidate_available,
        "dataset_available": requirements.dataset_available,
        "hypothesis_available": requirements.hypothesis_available,
        "experiment_available": requirements.experiment_available,
        "validation_available": requirements.validation_available,
        "deployment_available": requirements.deployment_available,
        "version_available": requirements.version_available,
        "operation_defined": requirements.operation_defined,
        "data_state": _rs_enum_value(requirements.data_state),
        "consistency": _rs_enum_value(requirements.consistency),
        "readiness": _rs_enum_value(requirements.readiness),
        "completeness_score": requirements.completeness_score,
        "warnings": list(requirements.warnings),
    }


def _rs_assessment_to_dict(
    assessment: Optional[ResearchAssessment],
) -> dict[str, Any]:
    """Serialize research assessment."""
    if assessment is None:
        return {}

    return {
        "decision": _rs_enum_value(assessment.decision),
        "readiness": _rs_enum_value(assessment.readiness),
        "data_state": _rs_enum_value(assessment.data_state),
        "consistency": _rs_enum_value(assessment.consistency),
        "confidence_score": assessment.confidence_score,
        "completeness_score": assessment.completeness_score,
        "strengths": list(assessment.strengths),
        "weaknesses": list(assessment.weaknesses),
        "rationale": assessment.rationale,
    }


def research_service_result_to_dict(
    result: Optional[ResearchServiceResult],
) -> dict[str, Any]:
    """Convert ResearchServiceResult into a stable dictionary contract."""
    if result is None:
        return {}

    return {
        "request_id": result.request_id,
        "result_id": result.result_id,
        "status": _rs_enum_value(result.status),
        "research": _rs_reference_to_dict(result.research),
        "requirements": _rs_requirements_to_dict(result.requirements),
        "assessment": _rs_assessment_to_dict(result.assessment),
        "rationale": result.rationale,
        "warnings": list(result.warnings),
        "created_at": result.created_at.isoformat()
        if result.created_at is not None
        else None,
        "is_valid": result.is_valid,
        "can_proceed": result.can_proceed,
        "requires_review": result.requires_review,
        "requires_hold": result.requires_hold,
        "is_blocked": result.is_blocked,
        "is_action_request": result.is_action_request,
    }


def research_service_contract_to_dict(
    contract: Optional[ResearchServiceContract],
) -> dict[str, Any]:
    """Convert ResearchServiceContract into a stable dictionary contract."""
    if contract is None:
        return {}

    return {
        "request_id": contract.request_id,
        "contract_id": contract.contract_id,
        "state": _rs_enum_value(contract.state),
        "result": research_service_result_to_dict(contract.result),
        "rationale": contract.rationale,
        "warnings": list(contract.warnings),
        "created_at": contract.created_at.isoformat()
        if contract.created_at is not None
        else None,
        "is_valid": contract.is_valid,
        "can_proceed": contract.can_proceed,
        "is_action_request": contract.is_action_request,
    }


# ============================================================
# INTEGRITY CHECK
# ============================================================

def research_service_integrity_check() -> dict[str, Any]:
    """
    Structural integrity check.

    This verifies the research-service contract surface only.
    It does not execute research, deploy anything, place orders,
    mutate market data, or override D13/Risk/CAS.
    """
    checks = {
        "engine_constant": bool(RESEARCH_SERVICE_ENGINE),
        "version_constant": bool(RESEARCH_SERVICE_VERSION),
        "request_model": ResearchServiceRequest is not None,
        "reference_model": ResearchReference is not None,
        "requirements_model": ResearchRequirements is not None,
        "assessment_model": ResearchAssessment is not None,
        "result_model": ResearchServiceResult is not None,
        "contract_model": ResearchServiceContract is not None,
        "request_validator": callable(validate_research_service_request),
        "result_validator": callable(validate_research_service_result),
        "contract_validator": callable(validate_research_service_contract),
        "result_serializer": callable(research_service_result_to_dict),
        "contract_serializer": callable(research_service_contract_to_dict),
        "audit_function": callable(research_audit),
        "health_function": callable(research_service_health_check),
        "safety_function": callable(research_is_safe),
        "execution_disabled": (
            research_allows_execution(None) is False
        ),
        "trade_disabled": (
            research_allows_trade(None) is False
        ),
        "order_disabled": (
            research_allows_order(None) is False
        ),
        "position_disabled": (
            research_allows_position_change(None) is False
        ),
        "authorization_disabled": (
            research_allows_authorization(None) is False
        ),
    }

    passed = all(checks.values())

    return {
        "engine": RESEARCH_SERVICE_ENGINE,
        "version": RESEARCH_SERVICE_VERSION,
        "integrity": "PASS" if passed else "FAIL",
        "passed": passed,
        "checks": checks,
        "action_authority": False,
        "execution_authority": False,
        "order_authority": False,
        "position_authority": False,
        "authorization_authority": False,
        "d13_override": False,
        "risk_override": False,
        "cas_override": False,
    }


def verify_research_service_integrity() -> bool:
    """Return True only when all structural integrity checks pass."""
    return bool(research_service_integrity_check().get("passed", False))


def run_research_service_integrity_check() -> dict[str, Any]:
    """Public integrity-check entry point."""
    return research_service_integrity_check()


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [
    # Constants
    "RESEARCH_SERVICE_ENGINE",
    "RESEARCH_SERVICE_VERSION",

    # Enums
    "ResearchServiceStatus",
    "ResearchServiceOperation",
    "ResearchServicePriority",
    "ResearchServiceDecision",
    "ResearchServiceContractStatus",
    "ResearchDataState",
    "ResearchConsistency",
    "ResearchReadiness",
    "ResearchServiceResultStatus",
    "ResearchServiceContractState",

    # Request / reference / validation
    "ResearchServiceRequest",
    "ResearchReference",
    "ResearchServiceContractValidation",

    # Requirements / assessment
    "ResearchRequirements",
    "ResearchAssessment",

    # Result / contract
    "ResearchServiceResult",
    "ResearchServiceContract",

    # Builders / evaluators
    "build_research_reference",
    "validate_research_service_request",
    "evaluate_research_requirements",
    "evaluate_research_readiness",
    "calculate_research_confidence",
    "determine_research_service_decision",
    "build_research_assessment",

    # Engine
    "ResearchServiceEngine",
    "research_service_engine",

    # Public service APIs
    "evaluate_research",
    "analyze_research",
    "process_research",
    "review_research",

    # Validation
    "validate_research_service_result",
    "validate_research_service_contract",

    # Readiness / lifecycle
    "research_ready",
    "research_can_advance",
    "research_status",
    "research_decision",
    "research_readiness",
    "research_confidence",
    "research_completeness",

    # Audit / safety
    "research_audit",
    "research_is_safe",
    "research_execution_allowed",
    "research_trade_allowed",
    "research_order_allowed",
    "research_position_allowed",
    "research_authorization_allowed",

    # Information / health
    "get_research_service_engine_info",
    "research_service_health_check",
    "run_research_service_health_check",

    # Serialization
    "research_service_result_to_dict",
    "research_service_contract_to_dict",

    # Integrity
    "research_service_integrity_check",
    "verify_research_service_integrity",
    "run_research_service_integrity_check",
]

