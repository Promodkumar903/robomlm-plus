# ============================================================
# ROBOMLM_PLUS
# app/intelligence/research/deployment_manager.py
# RESEARCH DEPLOYMENT MANAGEMENT — PART 1
# FOUNDATION + CONTRACTS
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Optional
from uuid import uuid4


# ============================================================
# CONSTANTS
# ============================================================

DEPLOYMENT_MANAGER_ENGINE = "ROBOMLM_RESEARCH_DEPLOYMENT_MANAGER"
DEPLOYMENT_MANAGER_VERSION = "1.0"


# ============================================================
# ENUMS
# ============================================================

class DeploymentStatus(str, Enum):
    NEW = "NEW"
    PROPOSED = "PROPOSED"
    VALIDATING = "VALIDATING"
    APPROVED = "APPROVED"
    STAGED = "STAGED"
    DEPLOYED = "DEPLOYED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"
    ARCHIVED = "ARCHIVED"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


class DeploymentType(str, Enum):
    RESEARCH = "RESEARCH"
    EXPERIMENT = "EXPERIMENT"
    MODEL = "MODEL"
    STRATEGY = "STRATEGY"
    SIGNAL = "SIGNAL"
    FORMULA = "FORMULA"
    ENGINE = "ENGINE"
    FEATURE = "FEATURE"
    UNKNOWN = "UNKNOWN"


class DeploymentEnvironment(str, Enum):
    RESEARCH = "RESEARCH"
    SANDBOX = "SANDBOX"
    PAPER = "PAPER"
    DEMO = "DEMO"
    LIVE = "LIVE"
    UNKNOWN = "UNKNOWN"


class DeploymentPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class DeploymentDecision(str, Enum):
    DEPLOY = "DEPLOY"
    STAGE = "STAGE"
    HOLD = "HOLD"
    REJECT = "REJECT"
    ROLLBACK = "ROLLBACK"
    REVIEW = "REVIEW"
    UNKNOWN = "UNKNOWN"


class DeploymentContractStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


# ============================================================
# REQUEST CONTRACT
# ============================================================

@dataclass(frozen=True)
class DeploymentRequest:
    """
    Entry contract for the Research Deployment Manager.

    The manager evaluates deployment state and readiness.

    It does NOT:
        - execute broker orders
        - activate trading automatically
        - create CAS authorization
        - bypass validation
        - invent deployment approval
        - override D13 or Risk
    """

    deployment: Any

    deployment_type: DeploymentType = DeploymentType.UNKNOWN
    environment: DeploymentEnvironment = (
        DeploymentEnvironment.UNKNOWN
    )

    candidate: Optional[Any] = None
    experiment: Optional[Any] = None
    validation: Optional[Any] = None
    version: Optional[Any] = None
    approval: Optional[Any] = None

    priority: DeploymentPriority = DeploymentPriority.UNKNOWN

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    request_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []

        if self.deployment is None:
            errors.append(
                "Deployment is required."
            )

        if not self.request_id:
            errors.append(
                "request_id is required."
            )

        if not isinstance(self.metadata, Mapping):
            errors.append(
                "metadata must be a Mapping."
            )

        return tuple(errors)


# ============================================================
# DEPLOYMENT REFERENCE
# ============================================================

@dataclass(frozen=True)
class DeploymentReference:
    """
    Normalized deployment identity.

    Only explicitly supplied deployment information
    is consumed.
    """

    deployment_id: str
    name: str

    deployment_type: DeploymentType
    status: DeploymentStatus
    environment: DeploymentEnvironment
    priority: DeploymentPriority

    candidate_id: str = ""
    experiment_id: str = ""
    validation_id: str = ""
    version_id: str = ""
    approval_id: str = ""

    raw_deployment: Any = None


# ============================================================
# DEPLOYMENT SOURCE / ARTIFACT REFERENCE
# ============================================================

@dataclass(frozen=True)
class DeploymentArtifactReference:
    """
    Reference to the artifact being considered for deployment.

    This layer identifies the artifact only.
    It does not modify or activate it.
    """

    artifact_id: str
    artifact_type: str = ""
    artifact_name: str = ""
    artifact_version: str = ""
    source_location: str = ""

    raw_artifact: Any = None


# ============================================================
# CONTRACT VALIDATION
# ============================================================

@dataclass(frozen=True)
class DeploymentContractValidation:
    status: DeploymentContractStatus

    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:
        return (
            self.status == DeploymentContractStatus.VALID
            and not self.errors
        )


# ============================================================
# SAFE READ HELPERS
# ============================================================

def _dm_read_value(
    obj: Any,
    *names: str,
    default: Any = None,
) -> Any:
    """
    Read explicit values from mappings or objects.

    No inferred deployment values are generated.
    """

    if obj is None:
        return default

    if isinstance(obj, Mapping):
        for name in names:
            if name in obj:
                return obj[name]
        return default

    for name in names:
        if hasattr(obj, name):
            try:
                return getattr(obj, name)
            except Exception:
                continue

    return default


def _dm_text(
    value: Any,
    default: str = "",
) -> str:
    if value is None:
        return default

    text = str(value).strip()
    return text if text else default


def _dm_enum(
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
        if text in {
            member.name.upper(),
            str(member.value).upper(),
        }:
            return member

    return default


# ============================================================
# DEPLOYMENT REFERENCE BUILDER
# ============================================================

def build_deployment_reference(
    deployment: Any,
    deployment_type: DeploymentType = DeploymentType.UNKNOWN,
    environment: DeploymentEnvironment = (
        DeploymentEnvironment.UNKNOWN
    ),
    priority: DeploymentPriority = DeploymentPriority.UNKNOWN,
) -> DeploymentReference:
    """
    Build normalized deployment identity.

    No automatic promotion or environment inference.
    """

    deployment_id = _dm_text(
        _dm_read_value(
            deployment,
            "deployment_id",
            "id",
            "uuid",
        )
    )

    name = _dm_text(
        _dm_read_value(
            deployment,
            "name",
            "deployment_name",
            "title",
        )
    )

    status = _dm_enum(
        _dm_read_value(
            deployment,
            "status",
            "state",
        ),
        DeploymentStatus,
        DeploymentStatus.NEW,
    )

    resolved_type = _dm_enum(
        _dm_read_value(
            deployment,
            "deployment_type",
            "type",
        ),
        DeploymentType,
        deployment_type,
    )

    resolved_environment = _dm_enum(
        _dm_read_value(
            deployment,
            "environment",
            "env",
        ),
        DeploymentEnvironment,
        environment,
    )

    resolved_priority = _dm_enum(
        _dm_read_value(
            deployment,
            "priority",
        ),
        DeploymentPriority,
        priority,
    )

    candidate_id = _dm_text(
        _dm_read_value(
            deployment,
            "candidate_id",
            "candidate",
        )
    )

    experiment_id = _dm_text(
        _dm_read_value(
            deployment,
            "experiment_id",
            "experiment",
        )
    )

    validation_id = _dm_text(
        _dm_read_value(
            deployment,
            "validation_id",
            "validation",
        )
    )

    version_id = _dm_text(
        _dm_read_value(
            deployment,
            "version_id",
            "version",
        )
    )

    approval_id = _dm_text(
        _dm_read_value(
            deployment,
            "approval_id",
            "approval",
        )
    )

    return DeploymentReference(
        deployment_id=deployment_id,
        name=name,
        deployment_type=resolved_type,
        status=status,
        environment=resolved_environment,
        priority=resolved_priority,
        candidate_id=candidate_id,
        experiment_id=experiment_id,
        validation_id=validation_id,
        version_id=version_id,
        approval_id=approval_id,
        raw_deployment=deployment,
    )


# ============================================================
# ARTIFACT REFERENCE BUILDER
# ============================================================

def build_deployment_artifact_reference(
    artifact: Any,
) -> Optional[DeploymentArtifactReference]:
    if artifact is None:
        return None

    return DeploymentArtifactReference(
        artifact_id=_dm_text(
            _dm_read_value(
                artifact,
                "artifact_id",
                "id",
                "uuid",
            )
        ),
        artifact_type=_dm_text(
            _dm_read_value(
                artifact,
                "artifact_type",
                "type",
            )
        ),
        artifact_name=_dm_text(
            _dm_read_value(
                artifact,
                "artifact_name",
                "name",
                "title",
            )
        ),
        artifact_version=_dm_text(
            _dm_read_value(
                artifact,
                "artifact_version",
                "version",
            )
        ),
        source_location=_dm_text(
            _dm_read_value(
                artifact,
                "source_location",
                "location",
                "uri",
            )
        ),
        raw_artifact=artifact,
    )


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_deployment_request(
    request: DeploymentRequest,
) -> DeploymentContractValidation:
    errors = list(
        request.validate()
    )

    warnings: list[str] = []

    if not errors:
        reference = build_deployment_reference(
            request.deployment,
            request.deployment_type,
            request.environment,
            request.priority,
        )

        if not reference.deployment_id:
            warnings.append(
                "Deployment identity is not explicitly available."
            )

        if not reference.name:
            warnings.append(
                "Deployment name is not explicitly available."
            )

        if (
            reference.deployment_type
            == DeploymentType.UNKNOWN
        ):
            warnings.append(
                "Deployment type is UNKNOWN."
            )

        if (
            reference.environment
            == DeploymentEnvironment.UNKNOWN
        ):
            warnings.append(
                "Deployment environment is UNKNOWN."
            )

        if (
            reference.priority
            == DeploymentPriority.UNKNOWN
        ):
            warnings.append(
                "Deployment priority is UNKNOWN."
            )

    return DeploymentContractValidation(
        status=(
            DeploymentContractStatus.VALID
            if not errors
            else DeploymentContractStatus.INVALID
        ),
        errors=tuple(errors),
        warnings=tuple(warnings),
    )
# ============================================================
# DEPLOYMENT READINESS
# ============================================================

class DeploymentReadiness(str, Enum):
    READY = "READY"
    CONDITIONAL = "CONDITIONAL"
    NOT_READY = "NOT_READY"
    UNKNOWN = "UNKNOWN"


class DeploymentValidationState(str, Enum):
    PASSED = "PASSED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


class DeploymentRiskLevel(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


# ============================================================
# READINESS CONTRACTS
# ============================================================

@dataclass(frozen=True)
class DeploymentRequirements:
    validation_available: bool
    approval_available: bool
    version_available: bool

    candidate_available: bool
    experiment_available: bool

    readiness: DeploymentReadiness

    rationale: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class DeploymentAssessment:
    validation_state: DeploymentValidationState

    readiness: DeploymentReadiness
    risk_level: DeploymentRiskLevel

    decision: DeploymentDecision

    rationale: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


# ============================================================
# REQUIREMENT EVALUATION
# ============================================================

def evaluate_deployment_requirements(
    request: DeploymentRequest,
) -> DeploymentRequirements:

    rationale: list[str] = []
    warnings: list[str] = []

    validation_available = (
        request.validation is not None
    )

    approval_available = (
        request.approval is not None
    )

    version_available = (
        request.version is not None
    )

    candidate_available = (
        request.candidate is not None
    )

    experiment_available = (
        request.experiment is not None
    )

    readiness = DeploymentReadiness.NOT_READY

    if (
        validation_available
        and approval_available
        and version_available
    ):
        readiness = DeploymentReadiness.READY

        rationale.append(
            "Required deployment controls available."
        )

    elif (
        validation_available
        or approval_available
        or version_available
    ):
        readiness = (
            DeploymentReadiness.CONDITIONAL
        )

        warnings.append(
            "Deployment controls partially available."
        )

    else:
        warnings.append(
            "Deployment controls unavailable."
        )

    return DeploymentRequirements(
        validation_available=validation_available,
        approval_available=approval_available,
        version_available=version_available,
        candidate_available=candidate_available,
        experiment_available=experiment_available,
        readiness=readiness,
        rationale=tuple(rationale),
        warnings=tuple(warnings),
    )


# ============================================================
# VALIDATION STATE
# ============================================================

def evaluate_validation_state(
    validation: Any,
) -> DeploymentValidationState:

    if validation is None:
        return (
            DeploymentValidationState.UNKNOWN
        )

    status = str(
        _dm_read_value(
            validation,
            "status",
            "validation_status",
            default="",
        )
    ).upper()

    if status in {
        "PASSED",
        "PASS",
        "SUCCESS",
        "VALID",
    }:
        return (
            DeploymentValidationState.PASSED
        )

    if status in {
        "PARTIAL",
        "WARNING",
        "CONDITIONAL",
    }:
        return (
            DeploymentValidationState.PARTIAL
        )

    if status in {
        "FAILED",
        "FAIL",
        "INVALID",
        "REJECTED",
    }:
        return (
            DeploymentValidationState.FAILED
        )

    return (
        DeploymentValidationState.UNKNOWN
    )


# ============================================================
# RISK EVALUATION
# ============================================================

def evaluate_deployment_risk(
    request: DeploymentRequest,
) -> DeploymentRiskLevel:

    priority = request.priority

    if priority == DeploymentPriority.CRITICAL:
        return DeploymentRiskLevel.CRITICAL

    if priority == DeploymentPriority.HIGH:
        return DeploymentRiskLevel.HIGH

    if priority == DeploymentPriority.MEDIUM:
        return DeploymentRiskLevel.MODERATE

    if priority == DeploymentPriority.LOW:
        return DeploymentRiskLevel.LOW

    return DeploymentRiskLevel.UNKNOWN


# ============================================================
# DECISION LOGIC
# ============================================================

def evaluate_deployment_decision(
    requirements: DeploymentRequirements,
    validation_state: DeploymentValidationState,
) -> DeploymentDecision:

    if (
        validation_state
        == DeploymentValidationState.FAILED
    ):
        return DeploymentDecision.REJECT

    if (
        requirements.readiness
        == DeploymentReadiness.NOT_READY
    ):
        return DeploymentDecision.HOLD

    if (
        requirements.readiness
        == DeploymentReadiness.CONDITIONAL
    ):
        return DeploymentDecision.REVIEW

    if (
        validation_state
        == DeploymentValidationState.PASSED
    ):
        return DeploymentDecision.DEPLOY

    return DeploymentDecision.STAGE


# ============================================================
# DEPLOYMENT ASSESSMENT
# ============================================================

def build_deployment_assessment(
    request: DeploymentRequest,
) -> DeploymentAssessment:

    requirements = (
        evaluate_deployment_requirements(
            request
        )
    )

    validation_state = (
        evaluate_validation_state(
            request.validation
        )
    )

    risk_level = (
        evaluate_deployment_risk(
            request
        )
    )

    decision = (
        evaluate_deployment_decision(
            requirements,
            validation_state,
        )
    )

    rationale = list(
        requirements.rationale
    )

    warnings = list(
        requirements.warnings
    )

    rationale.append(
        f"Validation state: {validation_state.value}"
    )

    rationale.append(
        f"Deployment decision: {decision.value}"
    )

    return DeploymentAssessment(
        validation_state=validation_state,
        readiness=requirements.readiness,
        risk_level=risk_level,
        decision=decision,
        rationale=tuple(rationale),
        warnings=tuple(warnings),
    )
# ============================================================
# RESULT STATUS
# ============================================================

class DeploymentResultStatus(str, Enum):
    READY = "READY"
    CONDITIONAL = "CONDITIONAL"
    BLOCKED = "BLOCKED"
    REJECTED = "REJECTED"
    INVALID = "INVALID"


class DeploymentContractState(str, Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


# ============================================================
# DEPLOYMENT RESULT
# ============================================================

@dataclass(frozen=True)
class DeploymentResult:

    request_id: str
    result_id: str

    status: DeploymentResultStatus

    deployment: DeploymentReference

    artifact: Optional[
        DeploymentArtifactReference
    ]

    requirements: DeploymentRequirements
    assessment: DeploymentAssessment

    rationale: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    created_at: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )

    @property
    def is_valid(self) -> bool:
        return (
            self.status
            != DeploymentResultStatus.INVALID
        )

    @property
    def can_deploy(self) -> bool:
        return (
            self.assessment.decision
            == DeploymentDecision.DEPLOY
        )

    @property
    def requires_review(self) -> bool:
        return (
            self.assessment.decision
            in {
                DeploymentDecision.REVIEW,
                DeploymentDecision.HOLD,
            }
        )

    @property
    def is_action_request(self) -> bool:
        """
        Research deployment manager never
        authorizes execution.
        """
        return False


# ============================================================
# DEPLOYMENT CONTRACT
# ============================================================

@dataclass(frozen=True)
class DeploymentContract:

    deployment_id: str
    request_id: str

    state: DeploymentContractState

    result: DeploymentResult

    rationale: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    created_at: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )

    @property
    def is_valid(self) -> bool:
        return (
            self.state
            != DeploymentContractState.INVALID
        )

    @property
    def is_action_request(self) -> bool:
        return False


# ============================================================
# RESULT STATUS RESOLUTION
# ============================================================

def determine_deployment_result_status(
    assessment: DeploymentAssessment,
) -> DeploymentResultStatus:

    if (
        assessment.decision
        == DeploymentDecision.REJECT
    ):
        return DeploymentResultStatus.REJECTED

    if (
        assessment.readiness
        == DeploymentReadiness.NOT_READY
    ):
        return DeploymentResultStatus.BLOCKED

    if (
        assessment.readiness
        == DeploymentReadiness.CONDITIONAL
    ):
        return (
            DeploymentResultStatus.CONDITIONAL
        )

    if (
        assessment.readiness
        == DeploymentReadiness.READY
    ):
        return DeploymentResultStatus.READY

    return DeploymentResultStatus.INVALID


# ============================================================
# BUILD RESULT
# ============================================================

def build_deployment_result(
    request: DeploymentRequest,
) -> DeploymentResult:

    deployment = build_deployment_reference(
        request.deployment,
        request.deployment_type,
        request.environment,
        request.priority,
    )

    artifact = (
        build_deployment_artifact_reference(
            request.deployment
        )
    )

    requirements = (
        evaluate_deployment_requirements(
            request
        )
    )

    assessment = (
        build_deployment_assessment(
            request
        )
    )

    status = (
        determine_deployment_result_status(
            assessment
        )
    )

    rationale: list[str] = []
    warnings: list[str] = []

    rationale.extend(
        requirements.rationale
    )
    rationale.extend(
        assessment.rationale
    )

    warnings.extend(
        requirements.warnings
    )
    warnings.extend(
        assessment.warnings
    )

    return DeploymentResult(
        request_id=request.request_id,
        result_id=str(uuid4()),
        status=status,
        deployment=deployment,
        artifact=artifact,
        requirements=requirements,
        assessment=assessment,
        rationale=tuple(
            dict.fromkeys(rationale)
        ),
        warnings=tuple(
            dict.fromkeys(warnings)
        ),
    )


# ============================================================
# BUILD CONTRACT
# ============================================================

def build_deployment_contract(
    result: DeploymentResult,
) -> DeploymentContract:

    state = (
        DeploymentContractState.COMPLETE
    )

    if not result.is_valid:
        state = (
            DeploymentContractState.INVALID
        )

    elif (
        result.status
        == DeploymentResultStatus.BLOCKED
    ):
        state = (
            DeploymentContractState.BLOCKED
        )

    elif (
        result.status
        == DeploymentResultStatus.CONDITIONAL
    ):
        state = (
            DeploymentContractState.INCOMPLETE
        )

    return DeploymentContract(
        deployment_id=(
            result.deployment.deployment_id
        ),
        request_id=result.request_id,
        state=state,
        result=result,
        rationale=result.rationale,
        warnings=result.warnings,
    )


# ============================================================
# DEPLOYMENT ENGINE
# ============================================================

class DeploymentManagerEngine:

    ENGINE_NAME = (
        DEPLOYMENT_MANAGER_ENGINE
    )

    ENGINE_VERSION = (
        DEPLOYMENT_MANAGER_VERSION
    )

    def evaluate(
        self,
        request: DeploymentRequest,
    ) -> DeploymentContract:

        validation = (
            validate_deployment_request(
                request
            )
        )

        if not validation.is_valid:

            invalid_result = DeploymentResult(
                request_id=request.request_id,
                result_id=str(uuid4()),
                status=(
                    DeploymentResultStatus.INVALID
                ),
                deployment=(
                    build_deployment_reference(
                        request.deployment,
                        request.deployment_type,
                        request.environment,
                        request.priority,
                    )
                ),
                artifact=None,
                requirements=DeploymentRequirements(
                    validation_available=False,
                    approval_available=False,
                    version_available=False,
                    candidate_available=False,
                    experiment_available=False,
                    readiness=(
                        DeploymentReadiness.NOT_READY
                    ),
                ),
                assessment=DeploymentAssessment(
                    validation_state=(
                        DeploymentValidationState.UNKNOWN
                    ),
                    readiness=(
                        DeploymentReadiness.NOT_READY
                    ),
                    risk_level=(
                        DeploymentRiskLevel.UNKNOWN
                    ),
                    decision=(
                        DeploymentDecision.REJECT
                    ),
                ),
                warnings=validation.warnings,
                rationale=validation.errors,
            )

            return build_deployment_contract(
                invalid_result
            )

        result = build_deployment_result(
            request
        )

        return build_deployment_contract(
            result
        )


# ============================================================
# SINGLETON
# ============================================================

deployment_manager_engine = (
    DeploymentManagerEngine()
)
# ============================================================
# RESULT VALIDATION
# ============================================================

def validate_deployment_result(
    result: DeploymentResult,
) -> DeploymentContractValidation:

    errors: list[str] = []
    warnings: list[str] = []

    if not result.request_id:
        errors.append(
            "Missing request_id."
        )

    if not result.result_id:
        errors.append(
            "Missing result_id."
        )

    if (
        result.deployment is None
    ):
        errors.append(
            "Missing deployment reference."
        )

    if (
        result.assessment is None
    ):
        errors.append(
            "Missing deployment assessment."
        )

    if (
        result.requirements is None
    ):
        errors.append(
            "Missing deployment requirements."
        )

    if (
        result.status
        == DeploymentResultStatus.REJECTED
    ):
        warnings.append(
            "Deployment assessment rejected."
        )

    if (
        result.status
        == DeploymentResultStatus.BLOCKED
    ):
        warnings.append(
            "Deployment assessment blocked."
        )

    return DeploymentContractValidation(
        status=(
            DeploymentContractStatus.VALID
            if not errors
            else DeploymentContractStatus.INVALID
        ),
        errors=tuple(
            dict.fromkeys(errors)
        ),
        warnings=tuple(
            dict.fromkeys(warnings)
        ),
    )


# ============================================================
# SAFE DEPLOYMENT GATE
# ============================================================

def is_deployment_ready(
    contract: DeploymentContract,
) -> bool:

    if not contract.is_valid:
        return False

    result = contract.result

    if not result.is_valid:
        return False

    if (
        result.assessment.decision
        != DeploymentDecision.DEPLOY
    ):
        return False

    if (
        result.assessment.validation_state
        != DeploymentValidationState.PASSED
    ):
        return False

    if (
        result.requirements.readiness
        != DeploymentReadiness.READY
    ):
        return False

    return True


def deployment_can_advance(
    contract: DeploymentContract,
) -> bool:
    return is_deployment_ready(
        contract
    )


# ============================================================
# AUDIT
# ============================================================

def deployment_audit(
    contract: DeploymentContract,
) -> dict[str, Any]:

    result = contract.result

    return {
        "engine": (
            DEPLOYMENT_MANAGER_ENGINE
        ),
        "version": (
            DEPLOYMENT_MANAGER_VERSION
        ),

        "deployment_id": (
            contract.deployment_id
        ),
        "request_id": (
            contract.request_id
        ),

        "contract_state": (
            contract.state.value
        ),

        "deployment_status": (
            result.status.value
        ),

        "decision": (
            result.assessment.decision.value
        ),

        "validation_state": (
            result.assessment
            .validation_state
            .value
        ),

        "readiness": (
            result.assessment
            .readiness
            .value
        ),

        "risk_level": (
            result.assessment
            .risk_level
            .value
        ),

        "can_deploy": (
            result.can_deploy
        ),

        "safe_to_advance": (
            deployment_can_advance(
                contract
            )
        ),

        "warnings": list(
            result.warnings
        ),

        "rationale": list(
            result.rationale
        ),
    }


# ============================================================
# ENGINE INFO
# ============================================================

def get_deployment_manager_engine_info(
) -> dict[str, Any]:

    return {
        "engine": (
            DEPLOYMENT_MANAGER_ENGINE
        ),
        "version": (
            DEPLOYMENT_MANAGER_VERSION
        ),

        "purpose": (
            "Research Deployment Lifecycle"
        ),

        "authorizes_execution": False,
        "creates_orders": False,
        "creates_positions": False,
        "creates_trades": False,
        "overrides_cas": False,
        "overrides_d13": False,
        "overrides_risk": False,
    }


# ============================================================
# HEALTH CHECK
# ============================================================

def deployment_health_check(
) -> dict[str, Any]:

    return {
        "engine": (
            DEPLOYMENT_MANAGER_ENGINE
        ),
        "version": (
            DEPLOYMENT_MANAGER_VERSION
        ),

        "healthy": True,

        "request_validation": True,
        "deployment_identity": True,
        "artifact_identity": True,
        "assessment_engine": True,
        "contract_builder": True,
        "audit_layer": True,
    }


# ============================================================
# PUBLIC API
# ============================================================

def evaluate_deployment(
    request: DeploymentRequest,
) -> DeploymentContract:

    return (
        deployment_manager_engine
        .evaluate(request)
    )


def manage_deployment(
    request: DeploymentRequest,
) -> DeploymentContract:

    return evaluate_deployment(
        request
    )


def deployment_status(
    contract: DeploymentContract,
) -> str:

    return (
        contract.result.status.value
    )


def deployment_decision(
    contract: DeploymentContract,
) -> str:

    return (
        contract.result.assessment
        .decision
        .value
    )


def deployment_ready(
    contract: DeploymentContract,
) -> bool:

    return is_deployment_ready(
        contract
    )
# ============================================================
# SERIALIZATION HELPERS
# ============================================================

def _dm_enum_value(
    value: Any,
) -> Any:

    if isinstance(value, Enum):
        return value.value

    return value


def deployment_result_to_dict(
    result: DeploymentResult,
) -> dict[str, Any]:

    return {
        "request_id": result.request_id,
        "result_id": result.result_id,

        "status": _dm_enum_value(
            result.status
        ),

        "deployment": {
            "deployment_id": (
                result.deployment.deployment_id
            ),
            "name": (
                result.deployment.name
            ),
            "deployment_type": (
                result.deployment
                .deployment_type
                .value
            ),
            "environment": (
                result.deployment
                .environment
                .value
            ),
            "priority": (
                result.deployment
                .priority
                .value
            ),
        },

        "readiness": (
            result.assessment
            .readiness
            .value
        ),

        "validation_state": (
            result.assessment
            .validation_state
            .value
        ),

        "risk_level": (
            result.assessment
            .risk_level
            .value
        ),

        "decision": (
            result.assessment
            .decision
            .value
        ),

        "can_deploy": (
            result.can_deploy
        ),

        "requires_review": (
            result.requires_review
        ),

        "warnings": list(
            result.warnings
        ),

        "rationale": list(
            result.rationale
        ),

        "created_at": (
            result.created_at.isoformat()
        ),
    }


# ============================================================
# CONTRACT SERIALIZATION
# ============================================================

def deployment_manager_to_dict(
    contract: DeploymentContract,
) -> dict[str, Any]:

    return {
        "engine": (
            DEPLOYMENT_MANAGER_ENGINE
        ),

        "version": (
            DEPLOYMENT_MANAGER_VERSION
        ),

        "deployment_id": (
            contract.deployment_id
        ),

        "request_id": (
            contract.request_id
        ),

        "state": (
            contract.state.value
        ),

        "is_valid": (
            contract.is_valid
        ),

        "safe_to_advance": (
            deployment_can_advance(
                contract
            )
        ),

        "warnings": list(
            contract.warnings
        ),

        "rationale": list(
            contract.rationale
        ),

        "result": (
            deployment_result_to_dict(
                contract.result
            )
        ),
    }


# ============================================================
# CONTRACT VALIDATION
# ============================================================

def validate_deployment_contract(
    contract: DeploymentContract,
) -> DeploymentContractValidation:

    errors: list[str] = []
    warnings: list[str] = []

    if not contract.deployment_id:
        errors.append(
            "Missing deployment_id."
        )

    if not contract.request_id:
        errors.append(
            "Missing request_id."
        )

    result_validation = (
        validate_deployment_result(
            contract.result
        )
    )

    errors.extend(
        result_validation.errors
    )

    warnings.extend(
        result_validation.warnings
    )

    return DeploymentContractValidation(
        status=(
            DeploymentContractStatus.VALID
            if not errors
            else DeploymentContractStatus.INVALID
        ),
        errors=tuple(
            dict.fromkeys(errors)
        ),
        warnings=tuple(
            dict.fromkeys(warnings)
        ),
    )


# ============================================================
# INTEGRITY CHECK
# ============================================================

def deployment_manager_integrity_check(
    contract: DeploymentContract,
) -> dict[str, Any]:

    validation = (
        validate_deployment_contract(
            contract
        )
    )

    return {
        "engine": (
            DEPLOYMENT_MANAGER_ENGINE
        ),

        "version": (
            DEPLOYMENT_MANAGER_VERSION
        ),

        "deployment_id": (
            contract.deployment_id
        ),

        "contract_valid": (
            validation.is_valid
        ),

        "safe_to_advance": (
            deployment_can_advance(
                contract
            )
        ),

        # Research Safety
        "artifact_modified": False,
        "candidate_modified": False,
        "experiment_modified": False,
        "validation_modified": False,

        # Execution Safety
        "execution_created": False,
        "position_created": False,
        "trade_created": False,
        "order_created": False,

        # Authority Safety
        "cas_overridden": False,
        "risk_overridden": False,
        "d13_overridden": False,

        "integrity_pass": (
            validation.is_valid
            and not contract.is_action_request
        ),
    }


def verify_deployment_integrity(
    contract: DeploymentContract,
) -> bool:

    return bool(
        deployment_manager_integrity_check(
            contract
        )["integrity_pass"]
    )


# ============================================================
# HEALTH WRAPPER
# ============================================================

def run_deployment_manager_health_check(
) -> dict[str, Any]:

    health = (
        deployment_health_check()
    )

    health.update(
        {
            "serialization": True,
            "integrity": True,
            "contract_validation": True,
            "deployment_gate": True,
        }
    )

    return health


# ============================================================
# EXPORTS
# ============================================================

__all__ = [

    # Constants
    "DEPLOYMENT_MANAGER_ENGINE",
    "DEPLOYMENT_MANAGER_VERSION",

    # Enums
    "DeploymentStatus",
    "DeploymentType",
    "DeploymentEnvironment",
    "DeploymentPriority",
    "DeploymentDecision",
    "DeploymentReadiness",
    "DeploymentValidationState",
    "DeploymentRiskLevel",
    "DeploymentResultStatus",
    "DeploymentContractStatus",
    "DeploymentContractState",

    # Contracts
    "DeploymentRequest",
    "DeploymentReference",
    "DeploymentArtifactReference",
    "DeploymentRequirements",
    "DeploymentAssessment",
    "DeploymentResult",
    "DeploymentContract",
    "DeploymentContractValidation",

    # Builders
    "build_deployment_reference",
    "build_deployment_artifact_reference",
    "build_deployment_result",
    "build_deployment_contract",

    # Validation
    "validate_deployment_request",
    "validate_deployment_result",
    "validate_deployment_contract",

    # Engine
    "DeploymentManagerEngine",
    "deployment_manager_engine",

    # API
    "evaluate_deployment",
    "manage_deployment",
    "deployment_status",
    "deployment_decision",
    "deployment_ready",
    "deployment_can_advance",
    "deployment_audit",

    # Serialization
    "deployment_result_to_dict",
    "deployment_manager_to_dict",

    # Health
    "deployment_health_check",
    "run_deployment_manager_health_check",
    "get_deployment_manager_engine_info",

    # Integrity
    "deployment_manager_integrity_check",
    "verify_deployment_integrity",
]