# ============================================================
# ROBOMLM_PLUS
# app/intelligence/research/experiment.py
# RESEARCH EXPERIMENT MANAGEMENT — PART 1
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

EXPERIMENT_ENGINE = (
    "ROBOMLM_RESEARCH_EXPERIMENT_ENGINE"
)

EXPERIMENT_VERSION = "1.0"


# ============================================================
# ENUMS
# ============================================================

class ExperimentStatus(str, Enum):
    NEW = "NEW"
    PROPOSED = "PROPOSED"
    ACTIVE = "ACTIVE"
    TESTING = "TESTING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"
    ARCHIVED = "ARCHIVED"
    UNKNOWN = "UNKNOWN"


class ExperimentType(str, Enum):
    HYPOTHESIS = "HYPOTHESIS"
    DATASET = "DATASET"
    MODEL = "MODEL"
    STRATEGY = "STRATEGY"
    FORMULA = "FORMULA"
    SIGNAL = "SIGNAL"
    ENGINE = "ENGINE"
    UNKNOWN = "UNKNOWN"


class ExperimentPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class ExperimentOutcome(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILURE = "FAILURE"
    INCONCLUSIVE = "INCONCLUSIVE"
    UNKNOWN = "UNKNOWN"


class ExperimentDecision(str, Enum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    REVIEW = "REVIEW"
    HOLD = "HOLD"
    RETEST = "RETEST"
    UNKNOWN = "UNKNOWN"


class ExperimentContractStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


# ============================================================
# REQUEST CONTRACT
# ============================================================

@dataclass(frozen=True)
class ExperimentRequest:
    """
    Research Experiment Request.

    Purpose:
        Evaluate experiment quality,
        completeness and outcome.

    Never:
        - place trades
        - create orders
        - authorize execution
        - override D13
        - override CAS
        - override Risk
    """

    experiment: Any

    experiment_type: ExperimentType = (
        ExperimentType.UNKNOWN
    )

    candidate: Optional[Any] = None
    dataset: Optional[Any] = None
    hypothesis: Optional[Any] = None
    validation: Optional[Any] = None

    priority: ExperimentPriority = (
        ExperimentPriority.UNKNOWN
    )

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    request_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )

    def validate(self) -> tuple[str, ...]:

        errors: list[str] = []

        if self.experiment is None:
            errors.append(
                "Experiment is required."
            )

        if not self.request_id:
            errors.append(
                "request_id is required."
            )

        if not isinstance(
            self.metadata,
            Mapping,
        ):
            errors.append(
                "metadata must be a Mapping."
            )

        return tuple(errors)


# ============================================================
# EXPERIMENT REFERENCE
# ============================================================

@dataclass(frozen=True)
class ExperimentReference:

    experiment_id: str
    name: str

    experiment_type: ExperimentType
    status: ExperimentStatus
    priority: ExperimentPriority

    candidate_id: str = ""
    dataset_id: str = ""
    hypothesis_id: str = ""
    validation_id: str = ""

    raw_experiment: Any = None


# ============================================================
# SOURCE REFERENCE
# ============================================================

@dataclass(frozen=True)
class ExperimentArtifactReference:

    artifact_id: str

    artifact_type: str = ""
    artifact_name: str = ""
    artifact_version: str = ""

    raw_artifact: Any = None


# ============================================================
# VALIDATION CONTRACT
# ============================================================

@dataclass(frozen=True)
class ExperimentContractValidation:

    status: ExperimentContractStatus

    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:

        return (
            self.status
            == ExperimentContractStatus.VALID
            and not self.errors
        )


# ============================================================
# SAFE HELPERS
# ============================================================

def _exp_read(
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

        return default

    for name in names:

        if hasattr(obj, name):
            try:
                return getattr(obj, name)
            except Exception:
                continue

    return default


def _exp_text(
    value: Any,
    default: str = "",
) -> str:

    if value is None:
        return default

    value = str(value).strip()

    return value if value else default


def _exp_enum(
    value: Any,
    enum_type: type[Enum],
    default: Enum,
) -> Enum:

    if isinstance(
        value,
        enum_type,
    ):
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
# REFERENCE BUILDER
# ============================================================

def build_experiment_reference(
    experiment: Any,
    experiment_type: ExperimentType = (
        ExperimentType.UNKNOWN
    ),
    priority: ExperimentPriority = (
        ExperimentPriority.UNKNOWN
    ),
) -> ExperimentReference:

    experiment_id = _exp_text(
        _exp_read(
            experiment,
            "experiment_id",
            "id",
            "uuid",
        )
    )

    name = _exp_text(
        _exp_read(
            experiment,
            "name",
            "title",
            "experiment_name",
        )
    )

    status = _exp_enum(
        _exp_read(
            experiment,
            "status",
            "state",
        ),
        ExperimentStatus,
        ExperimentStatus.NEW,
    )

    resolved_type = _exp_enum(
        _exp_read(
            experiment,
            "experiment_type",
            "type",
        ),
        ExperimentType,
        experiment_type,
    )

    resolved_priority = _exp_enum(
        _exp_read(
            experiment,
            "priority",
        ),
        ExperimentPriority,
        priority,
    )

    return ExperimentReference(
        experiment_id=experiment_id,
        name=name,

        experiment_type=resolved_type,
        status=status,
        priority=resolved_priority,

        candidate_id=_exp_text(
            _exp_read(
                experiment,
                "candidate_id",
            )
        ),

        dataset_id=_exp_text(
            _exp_read(
                experiment,
                "dataset_id",
            )
        ),

        hypothesis_id=_exp_text(
            _exp_read(
                experiment,
                "hypothesis_id",
            )
        ),

        validation_id=_exp_text(
            _exp_read(
                experiment,
                "validation_id",
            )
        ),

        raw_experiment=experiment,
    )


# ============================================================
# ARTIFACT BUILDER
# ============================================================

def build_experiment_artifact_reference(
    artifact: Any,
) -> Optional[
    ExperimentArtifactReference
]:

    if artifact is None:
        return None

    return ExperimentArtifactReference(
        artifact_id=_exp_text(
            _exp_read(
                artifact,
                "artifact_id",
                "id",
                "uuid",
            )
        ),
        artifact_type=_exp_text(
            _exp_read(
                artifact,
                "artifact_type",
                "type",
            )
        ),
        artifact_name=_exp_text(
            _exp_read(
                artifact,
                "artifact_name",
                "name",
            )
        ),
        artifact_version=_exp_text(
            _exp_read(
                artifact,
                "version",
                "artifact_version",
            )
        ),
        raw_artifact=artifact,
    )


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_experiment_request(
    request: ExperimentRequest,
) -> ExperimentContractValidation:

    errors = list(
        request.validate()
    )

    warnings: list[str] = []

    if not errors:

        ref = build_experiment_reference(
            request.experiment,
            request.experiment_type,
            request.priority,
        )

        if not ref.experiment_id:
            warnings.append(
                "Experiment identity unavailable."
            )

        if not ref.name:
            warnings.append(
                "Experiment name unavailable."
            )

        if (
            ref.experiment_type
            == ExperimentType.UNKNOWN
        ):
            warnings.append(
                "Experiment type UNKNOWN."
            )

    return ExperimentContractValidation(
        status=(
            ExperimentContractStatus.VALID
            if not errors
            else ExperimentContractStatus.INVALID
        ),
        errors=tuple(errors),
        warnings=tuple(warnings),
    )
# ============================================================
# EXPERIMENT REQUIREMENTS
# ============================================================

@dataclass(frozen=True)
class ExperimentRequirements:

    dataset_available: bool = False
    candidate_available: bool = False
    hypothesis_available: bool = False
    validation_available: bool = False

    minimum_sample_size_met: bool = False
    reproducible: bool = False
    measurable: bool = False

    readiness_score: float = 0.0


# ============================================================
# EXPERIMENT ASSESSMENT
# ============================================================

@dataclass(frozen=True)
class ExperimentAssessment:

    outcome: ExperimentOutcome

    confidence_score: float
    readiness_score: float

    decision: ExperimentDecision

    strengths: tuple[str, ...] = ()
    weaknesses: tuple[str, ...] = ()
    rationale: tuple[str, ...] = ()


# ============================================================
# RESULT CONTRACT
# ============================================================

@dataclass(frozen=True)
class ExperimentResult:

    request_id: str
    result_id: str

    experiment: ExperimentReference

    requirements: ExperimentRequirements
    assessment: ExperimentAssessment

    created_at: datetime

    warnings: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:

        return bool(
            self.result_id
            and self.request_id
        )

    @property
    def accepted(self) -> bool:

        return (
            self.assessment.decision
            == ExperimentDecision.ACCEPT
        )


# ============================================================
# REQUIREMENT ANALYSIS
# ============================================================

def build_experiment_requirements(
    request: ExperimentRequest,
) -> ExperimentRequirements:

    dataset_available = (
        request.dataset is not None
    )

    candidate_available = (
        request.candidate is not None
    )

    hypothesis_available = (
        request.hypothesis is not None
    )

    validation_available = (
        request.validation is not None
    )

    measurable = any(
        [
            dataset_available,
            validation_available,
        ]
    )

    reproducible = all(
        [
            dataset_available,
            hypothesis_available,
        ]
    )

    minimum_sample_size_met = bool(
        _exp_read(
            request.dataset,
            "minimum_sample_size_met",
            "sample_size_valid",
            default=False,
        )
    )

    readiness_components = [
        dataset_available,
        candidate_available,
        hypothesis_available,
        validation_available,
        measurable,
        reproducible,
        minimum_sample_size_met,
    ]

    readiness_score = (
        sum(
            1.0
            for item in readiness_components
            if item
        )
        / len(readiness_components)
    ) * 100.0

    return ExperimentRequirements(
        dataset_available=dataset_available,
        candidate_available=candidate_available,
        hypothesis_available=hypothesis_available,
        validation_available=validation_available,
        minimum_sample_size_met=(
            minimum_sample_size_met
        ),
        reproducible=reproducible,
        measurable=measurable,
        readiness_score=round(
            readiness_score,
            2,
        ),
    )


# ============================================================
# OUTCOME ANALYSIS
# ============================================================

def determine_experiment_outcome(
    request: ExperimentRequest,
    requirements: ExperimentRequirements,
) -> ExperimentOutcome:

    status = _exp_enum(
        _exp_read(
            request.experiment,
            "status",
            "state",
        ),
        ExperimentStatus,
        ExperimentStatus.UNKNOWN,
    )

    if status == ExperimentStatus.COMPLETED:

        success = bool(
            _exp_read(
                request.experiment,
                "success",
                "passed",
                default=False,
            )
        )

        return (
            ExperimentOutcome.SUCCESS
            if success
            else ExperimentOutcome.FAILURE
        )

    if status in {
        ExperimentStatus.TESTING,
        ExperimentStatus.ACTIVE,
    }:
        return (
            ExperimentOutcome.INCONCLUSIVE
        )

    if (
        requirements.readiness_score
        < 40.0
    ):
        return ExperimentOutcome.FAILURE

    return ExperimentOutcome.PARTIAL


# ============================================================
# CONFIDENCE SCORING
# ============================================================

def calculate_experiment_confidence(
    requirements: ExperimentRequirements,
) -> float:

    score = 0.0

    if requirements.dataset_available:
        score += 20.0

    if requirements.candidate_available:
        score += 15.0

    if requirements.hypothesis_available:
        score += 20.0

    if requirements.validation_available:
        score += 20.0

    if requirements.reproducible:
        score += 15.0

    if requirements.minimum_sample_size_met:
        score += 10.0

    return round(
        min(score, 100.0),
        2,
    )


# ============================================================
# DECISION ENGINE
# ============================================================

def determine_experiment_decision(
    outcome: ExperimentOutcome,
    confidence_score: float,
    readiness_score: float,
) -> ExperimentDecision:

    if (
        outcome
        == ExperimentOutcome.SUCCESS
        and confidence_score >= 75.0
        and readiness_score >= 70.0
    ):
        return ExperimentDecision.ACCEPT

    if (
        outcome
        == ExperimentOutcome.FAILURE
    ):
        return ExperimentDecision.REJECT

    if confidence_score < 40.0:
        return ExperimentDecision.RETEST

    if readiness_score < 50.0:
        return ExperimentDecision.HOLD

    return ExperimentDecision.REVIEW


# ============================================================
# ASSESSMENT BUILDER
# ============================================================

def build_experiment_assessment(
    request: ExperimentRequest,
    requirements: ExperimentRequirements,
) -> ExperimentAssessment:

    outcome = determine_experiment_outcome(
        request,
        requirements,
    )

    confidence_score = (
        calculate_experiment_confidence(
            requirements
        )
    )

    decision = (
        determine_experiment_decision(
            outcome,
            confidence_score,
            requirements.readiness_score,
        )
    )

    strengths: list[str] = []
    weaknesses: list[str] = []
    rationale: list[str] = []

    if requirements.dataset_available:
        strengths.append(
            "Dataset available."
        )

    if requirements.validation_available:
        strengths.append(
            "Validation available."
        )

    if not requirements.hypothesis_available:
        weaknesses.append(
            "Hypothesis missing."
        )

    if not requirements.reproducible:
        weaknesses.append(
            "Experiment not reproducible."
        )

    rationale.append(
        f"Outcome={outcome.value}"
    )

    rationale.append(
        f"Confidence={confidence_score:.2f}"
    )

    rationale.append(
        f"Readiness={requirements.readiness_score:.2f}"
    )

    return ExperimentAssessment(
        outcome=outcome,
        confidence_score=confidence_score,
        readiness_score=(
            requirements.readiness_score
        ),
        decision=decision,
        strengths=tuple(strengths),
        weaknesses=tuple(weaknesses),
        rationale=tuple(rationale),
    )
# ============================================================
# EXPERIMENT CONTRACT
# ============================================================

@dataclass(frozen=True)
class ExperimentContract:

    request_id: str
    contract_id: str

    result: ExperimentResult

    validation: ExperimentContractValidation

    created_at: datetime

    warnings: tuple[str, ...] = ()
    rationale: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:

        return (
            self.validation.is_valid
        )

    @property
    def accepted(self) -> bool:

        return (
            self.result.accepted
        )


# ============================================================
# RESULT BUILDER
# ============================================================

def build_experiment_result(
    request: ExperimentRequest,
) -> ExperimentResult:

    experiment_ref = (
        build_experiment_reference(
            request.experiment,
            request.experiment_type,
            request.priority,
        )
    )

    requirements = (
        build_experiment_requirements(
            request
        )
    )

    assessment = (
        build_experiment_assessment(
            request,
            requirements,
        )
    )

    warnings: list[str] = []

    if (
        assessment.decision
        == ExperimentDecision.RETEST
    ):
        warnings.append(
            "Experiment requires retesting."
        )

    if (
        assessment.decision
        == ExperimentDecision.HOLD
    ):
        warnings.append(
            "Experiment placed on hold."
        )

    return ExperimentResult(
        request_id=request.request_id,

        result_id=str(
            uuid4()
        ),

        experiment=experiment_ref,

        requirements=requirements,

        assessment=assessment,

        created_at=datetime.now(
            timezone.utc
        ),

        warnings=tuple(
            warnings
        ),
    )


# ============================================================
# CONTRACT BUILDER
# ============================================================

def build_experiment_contract(
    request: ExperimentRequest,
    result: ExperimentResult,
    validation: ExperimentContractValidation,
) -> ExperimentContract:

    rationale = [
        (
            f"Decision="
            f"{result.assessment.decision.value}"
        ),
        (
            f"Outcome="
            f"{result.assessment.outcome.value}"
        ),
        (
            f"Confidence="
            f"{result.assessment.confidence_score}"
        ),
    ]

    return ExperimentContract(
        request_id=request.request_id,

        contract_id=str(
            uuid4()
        ),

        result=result,

        validation=validation,

        created_at=datetime.now(
            timezone.utc
        ),

        warnings=result.warnings,

        rationale=tuple(
            rationale
        ),
    )


# ============================================================
# ENGINE
# ============================================================

class ExperimentEngine:

    def __init__(
        self,
    ) -> None:

        self.engine_name = (
            EXPERIMENT_ENGINE
        )

        self.version = (
            EXPERIMENT_VERSION
        )

    def evaluate(
        self,
        request: ExperimentRequest,
    ) -> ExperimentContract:

        validation = (
            validate_experiment_request(
                request
            )
        )

        if not validation.is_valid:

            empty_ref = (
                build_experiment_reference(
                    request.experiment,
                    request.experiment_type,
                    request.priority,
                )
            )

            failed_result = (
                ExperimentResult(
                    request_id=(
                        request.request_id
                    ),

                    result_id=str(
                        uuid4()
                    ),

                    experiment=empty_ref,

                    requirements=(
                        ExperimentRequirements()
                    ),

                    assessment=(
                        ExperimentAssessment(
                            outcome=(
                                ExperimentOutcome.FAILURE
                            ),
                            confidence_score=0.0,
                            readiness_score=0.0,
                            decision=(
                                ExperimentDecision.REJECT
                            ),
                        )
                    ),

                    created_at=(
                        datetime.now(
                            timezone.utc
                        )
                    ),

                    warnings=(
                        validation.errors
                    ),
                )
            )

            return build_experiment_contract(
                request=request,
                result=failed_result,
                validation=validation,
            )

        result = (
            build_experiment_result(
                request
            )
        )

        return (
            build_experiment_contract(
                request=request,
                result=result,
                validation=validation,
            )
        )


# ============================================================
# SINGLETON
# ============================================================

experiment_engine = (
    ExperimentEngine()
)


# ============================================================
# PUBLIC ENTRYPOINTS
# ============================================================

def evaluate_experiment(
    request: ExperimentRequest,
) -> ExperimentContract:

    return (
        experiment_engine.evaluate(
            request
        )
    )


def analyze_experiment(
    request: ExperimentRequest,
) -> ExperimentContract:

    return (
        evaluate_experiment(
            request
        )
    )


def review_experiment(
    request: ExperimentRequest,
) -> ExperimentContract:

    return (
        evaluate_experiment(
            request
        )
    )
# ============================================================
# RESULT VALIDATION
# ============================================================

def validate_experiment_result(
    result: ExperimentResult,
) -> ExperimentContractValidation:

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
        not result.experiment.experiment_id
    ):
        warnings.append(
            "Experiment identity unavailable."
        )

    if (
        result.assessment.decision
        == ExperimentDecision.REJECT
    ):
        warnings.append(
            "Experiment rejected."
        )

    if (
        result.assessment.decision
        == ExperimentDecision.RETEST
    ):
        warnings.append(
            "Retest required."
        )

    return ExperimentContractValidation(
        status=(
            ExperimentContractStatus.VALID
            if not errors
            else ExperimentContractStatus.INVALID
        ),
        errors=tuple(
            dict.fromkeys(errors)
        ),
        warnings=tuple(
            dict.fromkeys(warnings)
        ),
    )


# ============================================================
# READINESS GATE
# ============================================================

def experiment_ready(
    contract: ExperimentContract,
) -> bool:

    if not contract.is_valid:
        return False

    result = contract.result

    if (
        result.assessment.decision
        != ExperimentDecision.ACCEPT
    ):
        return False

    if (
        result.assessment.confidence_score
        < 70.0
    ):
        return False

    if (
        result.assessment.readiness_score
        < 70.0
    ):
        return False

    return True


def experiment_can_advance(
    contract: ExperimentContract,
) -> bool:

    return experiment_ready(
        contract
    )


# ============================================================
# DECISION HELPERS
# ============================================================

def experiment_decision(
    contract: ExperimentContract,
) -> str:

    return (
        contract.result.assessment
        .decision
        .value
    )


def experiment_outcome(
    contract: ExperimentContract,
) -> str:

    return (
        contract.result.assessment
        .outcome
        .value
    )


def experiment_confidence(
    contract: ExperimentContract,
) -> float:

    return (
        contract.result.assessment
        .confidence_score
    )


def experiment_readiness(
    contract: ExperimentContract,
) -> float:

    return (
        contract.result.assessment
        .readiness_score
    )


# ============================================================
# AUDIT
# ============================================================

def experiment_audit(
    contract: ExperimentContract,
) -> dict[str, Any]:

    result = contract.result

    return {
        "engine": (
            EXPERIMENT_ENGINE
        ),

        "version": (
            EXPERIMENT_VERSION
        ),

        "request_id": (
            contract.request_id
        ),

        "contract_id": (
            contract.contract_id
        ),

        "experiment_id": (
            result.experiment
            .experiment_id
        ),

        "experiment_name": (
            result.experiment
            .name
        ),

        "experiment_type": (
            result.experiment
            .experiment_type
            .value
        ),

        "status": (
            result.experiment
            .status
            .value
        ),

        "decision": (
            result.assessment
            .decision
            .value
        ),

        "outcome": (
            result.assessment
            .outcome
            .value
        ),

        "confidence": (
            result.assessment
            .confidence_score
        ),

        "readiness": (
            result.assessment
            .readiness_score
        ),

        "accepted": (
            result.accepted
        ),

        "safe_to_advance": (
            experiment_can_advance(
                contract
            )
        ),

        "strengths": list(
            result.assessment
            .strengths
        ),

        "weaknesses": list(
            result.assessment
            .weaknesses
        ),

        "warnings": list(
            result.warnings
        ),
    }


# ============================================================
# RESEARCH SAFETY
# ============================================================

def experiment_is_safe(
    contract: ExperimentContract,
) -> bool:

    if not contract.is_valid:
        return False

    return True


def experiment_authorizes_execution(
    contract: ExperimentContract,
) -> bool:

    return False


def experiment_creates_trade(
    contract: ExperimentContract,
) -> bool:

    return False


def experiment_creates_position(
    contract: ExperimentContract,
) -> bool:

    return False


def experiment_creates_order(
    contract: ExperimentContract,
) -> bool:

    return False


# ============================================================
# ENGINE INFO
# ============================================================

def get_experiment_engine_info(
) -> dict[str, Any]:

    return {
        "engine": (
            EXPERIMENT_ENGINE
        ),

        "version": (
            EXPERIMENT_VERSION
        ),

        "research_only": True,

        "creates_orders": False,
        "creates_positions": False,
        "creates_trades": False,

        "overrides_d13": False,
        "overrides_cas": False,
        "overrides_risk": False,

        "safe_for_research": True,
    }


# ============================================================
# HEALTH CHECK
# ============================================================

def experiment_health_check(
) -> dict[str, Any]:

    return {
        "engine": (
            EXPERIMENT_ENGINE
        ),

        "version": (
            EXPERIMENT_VERSION
        ),

        "healthy": True,

        "request_validation": True,
        "assessment_engine": True,
        "audit_layer": True,
        "decision_layer": True,
        "readiness_gate": True,
    }
# ============================================================
# SERIALIZATION
# ============================================================

def experiment_result_to_dict(
    result: ExperimentResult,
) -> dict[str, Any]:

    return {
        "request_id": (
            result.request_id
        ),

        "result_id": (
            result.result_id
        ),

        "experiment": {
            "experiment_id": (
                result.experiment
                .experiment_id
            ),

            "name": (
                result.experiment
                .name
            ),

            "experiment_type": (
                result.experiment
                .experiment_type
                .value
            ),

            "status": (
                result.experiment
                .status
                .value
            ),

            "priority": (
                result.experiment
                .priority
                .value
            ),
        },

        "requirements": {
            "dataset_available":
                result.requirements
                .dataset_available,

            "candidate_available":
                result.requirements
                .candidate_available,

            "hypothesis_available":
                result.requirements
                .hypothesis_available,

            "validation_available":
                result.requirements
                .validation_available,

            "minimum_sample_size_met":
                result.requirements
                .minimum_sample_size_met,

            "reproducible":
                result.requirements
                .reproducible,

            "measurable":
                result.requirements
                .measurable,

            "readiness_score":
                result.requirements
                .readiness_score,
        },

        "assessment": {
            "outcome":
                result.assessment
                .outcome
                .value,

            "confidence_score":
                result.assessment
                .confidence_score,

            "readiness_score":
                result.assessment
                .readiness_score,

            "decision":
                result.assessment
                .decision
                .value,

            "strengths":
                list(
                    result.assessment
                    .strengths
                ),

            "weaknesses":
                list(
                    result.assessment
                    .weaknesses
                ),

            "rationale":
                list(
                    result.assessment
                    .rationale
                ),
        },

        "accepted":
            result.accepted,

        "warnings":
            list(result.warnings),

        "created_at":
            result.created_at.isoformat(),
    }


def experiment_contract_to_dict(
    contract: ExperimentContract,
) -> dict[str, Any]:

    return {
        "request_id":
            contract.request_id,

        "contract_id":
            contract.contract_id,

        "is_valid":
            contract.is_valid,

        "accepted":
            contract.accepted,

        "warnings":
            list(contract.warnings),

        "rationale":
            list(contract.rationale),

        "result":
            experiment_result_to_dict(
                contract.result
            ),
    }


# ============================================================
# CONTRACT VALIDATION
# ============================================================

def validate_experiment_contract(
    contract: ExperimentContract,
) -> ExperimentContractValidation:

    errors: list[str] = []
    warnings: list[str] = []

    if not contract.contract_id:
        errors.append(
            "Missing contract_id."
        )

    if not contract.request_id:
        errors.append(
            "Missing request_id."
        )

    result_validation = (
        validate_experiment_result(
            contract.result
        )
    )

    errors.extend(
        result_validation.errors
    )

    warnings.extend(
        result_validation.warnings
    )

    return (
        ExperimentContractValidation(
            status=(
                ExperimentContractStatus.VALID
                if not errors
                else
                ExperimentContractStatus.INVALID
            ),

            errors=tuple(
                dict.fromkeys(errors)
            ),

            warnings=tuple(
                dict.fromkeys(warnings)
            ),
        )
    )


# ============================================================
# INTEGRITY CHECK
# ============================================================

def experiment_integrity_check(
    contract: ExperimentContract,
) -> dict[str, Any]:

    validation = (
        validate_experiment_contract(
            contract
        )
    )

    return {
        "contract_valid":
            validation.is_valid,

        "accepted":
            contract.accepted,

        "safe_to_advance":
            experiment_can_advance(
                contract
            ),

        # research-only guarantees
        "creates_orders": False,
        "creates_positions": False,
        "creates_trades": False,

        "overrides_d13": False,
        "overrides_cas": False,
        "overrides_risk": False,

        "integrity_pass":
            validation.is_valid,
    }


def verify_experiment_integrity(
    contract: ExperimentContract,
) -> bool:

    report = (
        experiment_integrity_check(
            contract
        )
    )

    return bool(
        report["integrity_pass"]
    )


# ============================================================
# HEALTH WRAPPER
# ============================================================

def run_experiment_health_check(
) -> dict[str, Any]:

    report = (
        experiment_health_check()
    )

    report.update(
        {
            "serialization": True,
            "integrity": True,
            "contract_validation": True,
        }
    )

    return report


# ============================================================
# EXPORTS
# ============================================================

__all__ = [

    # constants
    "EXPERIMENT_ENGINE",
    "EXPERIMENT_VERSION",

    # enums
    "ExperimentStatus",
    "ExperimentType",
    "ExperimentPriority",
    "ExperimentOutcome",
    "ExperimentDecision",
    "ExperimentContractStatus",

    # contracts
    "ExperimentRequest",
    "ExperimentReference",
    "ExperimentArtifactReference",
    "ExperimentRequirements",
    "ExperimentAssessment",
    "ExperimentResult",
    "ExperimentContract",
    "ExperimentContractValidation",

    # builders
    "build_experiment_reference",
    "build_experiment_artifact_reference",
    "build_experiment_requirements",
    "build_experiment_assessment",
    "build_experiment_result",
    "build_experiment_contract",

    # validation
    "validate_experiment_request",
    "validate_experiment_result",
    "validate_experiment_contract",

    # engine
    "ExperimentEngine",
    "experiment_engine",

    # public api
    "evaluate_experiment",
    "analyze_experiment",
    "review_experiment",

    # readiness
    "experiment_ready",
    "experiment_can_advance",

    # audit
    "experiment_audit",

    # serialization
    "experiment_result_to_dict",
    "experiment_contract_to_dict",

    # integrity
    "experiment_integrity_check",
    "verify_experiment_integrity",

    # health
    "experiment_health_check",
    "run_experiment_health_check",
    "get_experiment_engine_info",
]