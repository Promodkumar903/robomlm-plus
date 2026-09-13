# ============================================================
# ROBOMLM_PLUS
# app/intelligence/research/hypothesis.py
# RESEARCH HYPOTHESIS ENGINE
# PART 1/5
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

HYPOTHESIS_ENGINE = (
    "ROBOMLM_RESEARCH_HYPOTHESIS_ENGINE"
)

HYPOTHESIS_VERSION = "1.0"


# ============================================================
# ENUMS
# ============================================================

class HypothesisStatus(str, Enum):

    DRAFT = "DRAFT"
    PROPOSED = "PROPOSED"
    TESTING = "TESTING"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    RETEST_REQUIRED = "RETEST_REQUIRED"
    ARCHIVED = "ARCHIVED"
    UNKNOWN = "UNKNOWN"


class HypothesisType(str, Enum):

    MARKET = "MARKET"
    STRATEGY = "STRATEGY"
    FORMULA = "FORMULA"
    SIGNAL = "SIGNAL"
    EXECUTION = "EXECUTION"
    RISK = "RISK"
    BEHAVIORAL = "BEHAVIORAL"
    UNKNOWN = "UNKNOWN"


class HypothesisPriority(str, Enum):

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class HypothesisDecision(str, Enum):

    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    REVIEW = "REVIEW"
    HOLD = "HOLD"
    RETEST = "RETEST"
    UNKNOWN = "UNKNOWN"


class HypothesisConfidence(str, Enum):

    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class HypothesisContractStatus(str, Enum):

    VALID = "VALID"
    INVALID = "INVALID"


# ============================================================
# REQUEST CONTRACT
# ============================================================

@dataclass(frozen=True)
class HypothesisRequest:

    hypothesis: Any

    hypothesis_type: HypothesisType = (
        HypothesisType.UNKNOWN
    )

    priority: HypothesisPriority = (
        HypothesisPriority.UNKNOWN
    )

    experiment: Optional[Any] = None
    dataset: Optional[Any] = None
    candidate: Optional[Any] = None

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

        if self.hypothesis is None:
            errors.append(
                "Hypothesis is required."
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
# HYPOTHESIS REFERENCE
# ============================================================

@dataclass(frozen=True)
class HypothesisReference:

    hypothesis_id: str
    title: str

    hypothesis_type: HypothesisType
    status: HypothesisStatus
    priority: HypothesisPriority

    statement: str = ""

    experiment_id: str = ""
    dataset_id: str = ""
    candidate_id: str = ""

    raw_hypothesis: Any = None


# ============================================================
# EVIDENCE REFERENCE
# ============================================================

@dataclass(frozen=True)
class HypothesisEvidenceReference:

    evidence_id: str

    evidence_type: str = ""
    evidence_name: str = ""
    source: str = ""

    raw_evidence: Any = None


# ============================================================
# VALIDATION CONTRACT
# ============================================================

@dataclass(frozen=True)
class HypothesisContractValidation:

    status: HypothesisContractStatus

    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:

        return (
            self.status
            == HypothesisContractStatus.VALID
            and not self.errors
        )


# ============================================================
# SAFE HELPERS
# ============================================================

def _hyp_read(
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
                return getattr(
                    obj,
                    name,
                )
            except Exception:
                pass

    return default


def _hyp_text(
    value: Any,
    default: str = "",
) -> str:

    if value is None:
        return default

    value = str(value).strip()

    return value if value else default


def _hyp_enum(
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

def build_hypothesis_reference(
    hypothesis: Any,
    hypothesis_type: HypothesisType = (
        HypothesisType.UNKNOWN
    ),
    priority: HypothesisPriority = (
        HypothesisPriority.UNKNOWN
    ),
) -> HypothesisReference:

    return HypothesisReference(

        hypothesis_id=_hyp_text(
            _hyp_read(
                hypothesis,
                "hypothesis_id",
                "id",
                "uuid",
            )
        ),

        title=_hyp_text(
            _hyp_read(
                hypothesis,
                "title",
                "name",
                "hypothesis_name",
            )
        ),

        hypothesis_type=_hyp_enum(
            _hyp_read(
                hypothesis,
                "hypothesis_type",
                "type",
            ),
            HypothesisType,
            hypothesis_type,
        ),

        status=_hyp_enum(
            _hyp_read(
                hypothesis,
                "status",
                "state",
            ),
            HypothesisStatus,
            HypothesisStatus.UNKNOWN,
        ),

        priority=_hyp_enum(
            _hyp_read(
                hypothesis,
                "priority",
            ),
            HypothesisPriority,
            priority,
        ),

        statement=_hyp_text(
            _hyp_read(
                hypothesis,
                "statement",
                "description",
                "hypothesis",
            )
        ),

        experiment_id=_hyp_text(
            _hyp_read(
                hypothesis,
                "experiment_id",
            )
        ),

        dataset_id=_hyp_text(
            _hyp_read(
                hypothesis,
                "dataset_id",
            )
        ),

        candidate_id=_hyp_text(
            _hyp_read(
                hypothesis,
                "candidate_id",
            )
        ),

        raw_hypothesis=hypothesis,
    )


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_hypothesis_request(
    request: HypothesisRequest,
) -> HypothesisContractValidation:

    errors = list(
        request.validate()
    )

    warnings: list[str] = []

    if not errors:

        ref = build_hypothesis_reference(
            request.hypothesis,
            request.hypothesis_type,
            request.priority,
        )

        if not ref.hypothesis_id:
            warnings.append(
                "Hypothesis identity unavailable."
            )

        if not ref.title:
            warnings.append(
                "Hypothesis title unavailable."
            )

        if not ref.statement:
            warnings.append(
                "Hypothesis statement unavailable."
            )

    return HypothesisContractValidation(
        status=(
            HypothesisContractStatus.VALID
            if not errors
            else
            HypothesisContractStatus.INVALID
        ),
        errors=tuple(errors),
        warnings=tuple(warnings),
    )
# ============================================================
# HYPOTHESIS REQUIREMENTS
# ============================================================

@dataclass(frozen=True)
class HypothesisRequirements:

    statement_available: bool = False
    experiment_available: bool = False
    dataset_available: bool = False
    candidate_available: bool = False

    evidence_available: bool = False
    measurable: bool = False
    testable: bool = False

    completeness_score: float = 0.0


# ============================================================
# HYPOTHESIS ASSESSMENT
# ============================================================

@dataclass(frozen=True)
class HypothesisAssessment:

    evidence_strength: float
    validation_score: float
    confidence_score: float

    confidence_level: HypothesisConfidence

    decision: HypothesisDecision

    strengths: tuple[str, ...] = ()
    weaknesses: tuple[str, ...] = ()
    rationale: tuple[str, ...] = ()


# ============================================================
# REQUIREMENT ANALYSIS
# ============================================================

def build_hypothesis_requirements(
    request: HypothesisRequest,
) -> HypothesisRequirements:

    reference = build_hypothesis_reference(
        request.hypothesis,
        request.hypothesis_type,
        request.priority,
    )

    statement_available = bool(
        reference.statement
    )

    experiment_available = (
        request.experiment is not None
    )

    dataset_available = (
        request.dataset is not None
    )

    candidate_available = (
        request.candidate is not None
    )

    evidence_available = bool(
        _hyp_read(
            request.hypothesis,
            "evidence",
            "evidence_available",
            "supporting_evidence",
            default=None,
        )
    ) or bool(
        _hyp_read(
            request.metadata,
            "evidence",
            "evidence_available",
            default=False,
        )
    )

    measurable = bool(
        _hyp_read(
            request.hypothesis,
            "measurable",
            "measurable_criteria",
            "metric",
            default=False,
        )
    )

    testable = bool(
        statement_available
        and (
            experiment_available
            or dataset_available
        )
    )

    components = (
        statement_available,
        experiment_available,
        dataset_available,
        candidate_available,
        evidence_available,
        measurable,
        testable,
    )

    completeness_score = (
        sum(
            1.0
            for value in components
            if value
        )
        / len(components)
    ) * 100.0

    return HypothesisRequirements(
        statement_available=statement_available,
        experiment_available=experiment_available,
        dataset_available=dataset_available,
        candidate_available=candidate_available,
        evidence_available=evidence_available,
        measurable=measurable,
        testable=testable,
        completeness_score=round(
            completeness_score,
            2,
        ),
    )


# ============================================================
# EVIDENCE STRENGTH
# ============================================================

def calculate_hypothesis_evidence_strength(
    request: HypothesisRequest,
    requirements: HypothesisRequirements,
) -> float:

    score = 0.0

    if requirements.evidence_available:
        score += 40.0

    if requirements.dataset_available:
        score += 20.0

    if requirements.experiment_available:
        score += 20.0

    if requirements.validation_available \
            if hasattr(
                requirements,
                "validation_available",
            ) else False:
        score += 10.0

    if requirements.candidate_available:
        score += 10.0

    return round(
        min(score, 100.0),
        2,
    )


# ============================================================
# VALIDATION SCORE
# ============================================================

def calculate_hypothesis_validation_score(
    request: HypothesisRequest,
    requirements: HypothesisRequirements,
) -> float:

    score = 0.0

    validation = _hyp_read(
        request.metadata,
        "validation",
        "validation_score",
        default=None,
    )

    if isinstance(
        validation,
        (int, float),
    ):
        score = float(validation)

    elif request.experiment is not None:

        experiment_status = str(
            _hyp_read(
                request.experiment,
                "status",
                "state",
                default="",
            )
        ).upper()

        if experiment_status in {
            "COMPLETED",
            "VALIDATED",
            "SUCCESS",
        }:
            score = 80.0

        elif experiment_status in {
            "TESTING",
            "ACTIVE",
        }:
            score = 50.0

    elif request.dataset is not None:
        score = 30.0

    return round(
        max(
            0.0,
            min(score, 100.0),
        ),
        2,
    )


# ============================================================
# CONFIDENCE
# ============================================================

def calculate_hypothesis_confidence(
    evidence_strength: float,
    validation_score: float,
    completeness_score: float,
) -> float:

    confidence = (
        evidence_strength * 0.40
        + validation_score * 0.35
        + completeness_score * 0.25
    )

    return round(
        max(
            0.0,
            min(confidence, 100.0),
        ),
        2,
    )


def determine_hypothesis_confidence_level(
    confidence_score: float,
) -> HypothesisConfidence:

    if confidence_score >= 85.0:
        return HypothesisConfidence.VERY_HIGH

    if confidence_score >= 70.0:
        return HypothesisConfidence.HIGH

    if confidence_score >= 50.0:
        return HypothesisConfidence.MEDIUM

    if confidence_score >= 30.0:
        return HypothesisConfidence.LOW

    return HypothesisConfidence.VERY_LOW


# ============================================================
# DECISION
# ============================================================

def determine_hypothesis_decision(
    request: HypothesisRequest,
    requirements: HypothesisRequirements,
    confidence_score: float,
) -> HypothesisDecision:

    status = _hyp_enum(
        _hyp_read(
            request.hypothesis,
            "status",
            "state",
        ),
        HypothesisStatus,
        HypothesisStatus.UNKNOWN,
    )

    if status == HypothesisStatus.REJECTED:
        return HypothesisDecision.REJECT

    if status == HypothesisStatus.RETEST_REQUIRED:
        return HypothesisDecision.RETEST

    if not requirements.testable:
        return HypothesisDecision.HOLD

    if confidence_score >= 80.0:
        return HypothesisDecision.ACCEPT

    if confidence_score >= 50.0:
        return HypothesisDecision.REVIEW

    return HypothesisDecision.RETEST


# ============================================================
# ASSESSMENT BUILDER
# ============================================================

def build_hypothesis_assessment(
    request: HypothesisRequest,
    requirements: HypothesisRequirements,
) -> HypothesisAssessment:

    evidence_strength = (
        calculate_hypothesis_evidence_strength(
            request,
            requirements,
        )
    )

    validation_score = (
        calculate_hypothesis_validation_score(
            request,
            requirements,
        )
    )

    confidence_score = (
        calculate_hypothesis_confidence(
            evidence_strength,
            validation_score,
            requirements.completeness_score,
        )
    )

    confidence_level = (
        determine_hypothesis_confidence_level(
            confidence_score
        )
    )

    decision = (
        determine_hypothesis_decision(
            request,
            requirements,
            confidence_score,
        )
    )

    strengths: list[str] = []
    weaknesses: list[str] = []
    rationale: list[str] = []

    if requirements.statement_available:
        strengths.append(
            "Hypothesis statement available."
        )

    if requirements.testable:
        strengths.append(
            "Hypothesis has a testable structure."
        )

    if requirements.evidence_available:
        strengths.append(
            "Supporting evidence is available."
        )

    if not requirements.dataset_available:
        weaknesses.append(
            "Dataset unavailable."
        )

    if not requirements.experiment_available:
        weaknesses.append(
            "Experiment unavailable."
        )

    if not requirements.measurable:
        weaknesses.append(
            "Measurement criteria unavailable."
        )

    rationale.extend(
        [
            f"EvidenceStrength={evidence_strength:.2f}",
            f"ValidationScore={validation_score:.2f}",
            f"Completeness={requirements.completeness_score:.2f}",
            f"Confidence={confidence_score:.2f}",
            f"Decision={decision.value}",
        ]
    )

    return HypothesisAssessment(
        evidence_strength=evidence_strength,
        validation_score=validation_score,
        confidence_score=confidence_score,
        confidence_level=confidence_level,
        decision=decision,
        strengths=tuple(strengths),
        weaknesses=tuple(weaknesses),
        rationale=tuple(rationale),
    )
# ============================================================
# ROBOMLM_PLUS
# app/intelligence/research/hypothesis.py
# RESEARCH HYPOTHESIS ENGINE
# PART 3/5
# ============================================================

class HypothesisResultStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    REVIEW = "REVIEW"
    HOLD = "HOLD"
    RETEST = "RETEST"
    REJECTED = "REJECTED"
    INVALID = "INVALID"


class HypothesisContractState(str, Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


@dataclass(frozen=True)
class HypothesisResult:
    request_id: str
    result_id: str
    status: HypothesisResultStatus
    hypothesis: HypothesisReference
    requirements: HypothesisRequirements
    assessment: HypothesisAssessment
    rationale: str = ""
    warnings: tuple[str, ...] = ()
    created_at: str = ""

    @property
    def is_valid(self) -> bool:
        return (
            bool(self.request_id)
            and bool(self.result_id)
            and self.status != HypothesisResultStatus.INVALID
        )

    @property
    def accepted(self) -> bool:
        return (
            self.is_valid
            and self.status == HypothesisResultStatus.ACCEPTED
        )

    @property
    def requires_review(self) -> bool:
        return self.status == HypothesisResultStatus.REVIEW

    @property
    def requires_hold(self) -> bool:
        return self.status == HypothesisResultStatus.HOLD

    @property
    def requires_retest(self) -> bool:
        return self.status == HypothesisResultStatus.RETEST

    @property
    def is_action_request(self) -> bool:
        return False


@dataclass(frozen=True)
class HypothesisContract:
    request_id: str
    contract_id: str
    state: HypothesisContractState
    result: HypothesisResult
    rationale: str = ""
    warnings: tuple[str, ...] = ()
    created_at: str = ""

    @property
    def is_valid(self) -> bool:
        return (
            bool(self.request_id)
            and bool(self.contract_id)
            and self.state == HypothesisContractState.COMPLETE
            and self.result.is_valid
        )

    @property
    def is_action_request(self) -> bool:
        return False


def determine_hypothesis_result_status(
    assessment: HypothesisAssessment,
) -> HypothesisResultStatus:

    decision = assessment.decision

    if decision == HypothesisDecision.ACCEPT:
        return HypothesisResultStatus.ACCEPTED

    if decision == HypothesisDecision.REVIEW:
        return HypothesisResultStatus.REVIEW

    if decision == HypothesisDecision.HOLD:
        return HypothesisResultStatus.HOLD

    if decision == HypothesisDecision.RETEST:
        return HypothesisResultStatus.RETEST

    if decision == HypothesisDecision.REJECT:
        return HypothesisResultStatus.REJECTED

    return HypothesisResultStatus.INVALID


def build_hypothesis_result(
    request: HypothesisRequest,
    reference: HypothesisReference,
    requirements: HypothesisRequirements,
    assessment: HypothesisAssessment,
) -> HypothesisResult:

    status = determine_hypothesis_result_status(
        assessment
    )

    warnings = list(assessment.weaknesses)

    rationale = (
        f"hypothesis_result={status.value}; "
        f"confidence={assessment.confidence_score:.2f}; "
        f"decision={assessment.decision.value}"
    )

    return HypothesisResult(
        request_id=request.request_id,
        result_id=f"HYP-RES-{uuid4().hex[:12].upper()}",
        status=status,
        hypothesis=reference,
        requirements=requirements,
        assessment=assessment,
        rationale=rationale,
        warnings=tuple(warnings),
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def determine_hypothesis_contract_state(
    result: HypothesisResult,
) -> HypothesisContractState:

    if not result.is_valid:
        return HypothesisContractState.INVALID

    if result.status == HypothesisResultStatus.INVALID:
        return HypothesisContractState.INVALID

    if result.status in {
        HypothesisResultStatus.HOLD,
        HypothesisResultStatus.RETEST,
    }:
        return HypothesisContractState.BLOCKED

    if not result.hypothesis.hypothesis_id:
        return HypothesisContractState.INCOMPLETE

    return HypothesisContractState.COMPLETE


def build_hypothesis_contract(
    request: HypothesisRequest,
    result: HypothesisResult,
) -> HypothesisContract:

    state = determine_hypothesis_contract_state(result)

    return HypothesisContract(
        request_id=request.request_id,
        contract_id=f"HYP-CON-{uuid4().hex[:12].upper()}",
        state=state,
        result=result,
        rationale=result.rationale,
        warnings=result.warnings,
        created_at=datetime.now(timezone.utc).isoformat(),
    )


class HypothesisEngine:

    engine_name = HYPOTHESIS_ENGINE
    version = HYPOTHESIS_VERSION

    def validate_request(
        self,
        request: HypothesisRequest,
    ) -> HypothesisContractValidation:
        return validate_hypothesis_request(request)

    def evaluate(
        self,
        request: HypothesisRequest,
    ) -> HypothesisContract:

        validation = self.validate_request(request)

        if not validation.valid:
            reference = build_hypothesis_reference(request)

            requirements = build_hypothesis_requirements(
                request,
                reference,
            )

            assessment = HypothesisAssessment(
                evidence_strength=0.0,
                validation_score=0.0,
                confidence_score=0.0,
                confidence_level=HypothesisConfidence.VERY_LOW,
                decision=HypothesisDecision.HOLD,
                strengths=(),
                weaknesses=("request_contract_invalid",),
                rationale="Hypothesis request contract is invalid.",
            )

            result = HypothesisResult(
                request_id=request.request_id,
                result_id=f"HYP-RES-{uuid4().hex[:12].upper()}",
                status=HypothesisResultStatus.INVALID,
                hypothesis=reference,
                requirements=requirements,
                assessment=assessment,
                rationale="Invalid hypothesis request.",
                warnings=("request_contract_invalid",),
                created_at=datetime.now(timezone.utc).isoformat(),
            )

            return HypothesisContract(
                request_id=request.request_id,
                contract_id=f"HYP-CON-{uuid4().hex[:12].upper()}",
                state=HypothesisContractState.INVALID,
                result=result,
                rationale="Hypothesis request rejected by contract validation.",
                warnings=("request_contract_invalid",),
                created_at=datetime.now(timezone.utc).isoformat(),
            )

        reference = build_hypothesis_reference(request)

        requirements = build_hypothesis_requirements(
            request,
            reference,
        )

        assessment = build_hypothesis_assessment(
            request,
            reference,
            requirements,
        )

        result = build_hypothesis_result(
            request,
            reference,
            requirements,
            assessment,
        )

        return build_hypothesis_contract(
            request,
            result,
        )


hypothesis_engine = HypothesisEngine()


def evaluate_hypothesis(
    request: HypothesisRequest,
) -> HypothesisContract:
    return hypothesis_engine.evaluate(request)


def analyze_hypothesis(
    request: HypothesisRequest,
) -> HypothesisContract:
    return hypothesis_engine.evaluate(request)


def review_hypothesis(
    request: HypothesisRequest,
) -> HypothesisContract:
    return hypothesis_engine.evaluate(request)
# ============================================================
# ROBOMLM_PLUS
# app/intelligence/research/hypothesis.py
# RESEARCH HYPOTHESIS ENGINE
# PART 4/5
# ============================================================

def validate_hypothesis_result(
    result: HypothesisResult,
) -> bool:

    if not result.is_valid:
        return False

    if not result.hypothesis.hypothesis_id:
        return False

    if result.requirements.completeness_score < 0.0:
        return False

    if result.requirements.completeness_score > 100.0:
        return False

    if not 0.0 <= result.assessment.evidence_strength <= 100.0:
        return False

    if not 0.0 <= result.assessment.validation_score <= 100.0:
        return False

    if not 0.0 <= result.assessment.confidence_score <= 100.0:
        return False

    return True


def validate_hypothesis_contract(
    contract: HypothesisContract,
) -> bool:

    if not contract.is_valid:
        return False

    if not validate_hypothesis_result(contract.result):
        return False

    return True


def hypothesis_ready(
    contract: HypothesisContract,
) -> bool:

    if not validate_hypothesis_contract(contract):
        return False

    result = contract.result
    assessment = result.assessment

    return (
        result.status == HypothesisResultStatus.ACCEPTED
        and assessment.decision == HypothesisDecision.ACCEPT
        and assessment.confidence_score >= 80.0
        and result.requirements.testable
        and result.requirements.measurable
    )


def hypothesis_can_advance(
    contract: HypothesisContract,
) -> bool:

    if not validate_hypothesis_contract(contract):
        return False

    if contract.state != HypothesisContractState.COMPLETE:
        return False

    return hypothesis_ready(contract)


def hypothesis_decision(
    contract: HypothesisContract,
) -> HypothesisDecision:

    if not validate_hypothesis_contract(contract):
        return HypothesisDecision.UNKNOWN

    return contract.result.assessment.decision


def hypothesis_status(
    contract: HypothesisContract,
) -> HypothesisResultStatus:

    if not validate_hypothesis_contract(contract):
        return HypothesisResultStatus.INVALID

    return contract.result.status


def hypothesis_confidence(
    contract: HypothesisContract,
) -> float:

    if not validate_hypothesis_contract(contract):
        return 0.0

    return contract.result.assessment.confidence_score


def hypothesis_readiness(
    contract: HypothesisContract,
) -> float:

    if not validate_hypothesis_contract(contract):
        return 0.0

    return contract.result.requirements.completeness_score


def hypothesis_audit(
    contract: HypothesisContract,
) -> dict[str, Any]:

    if not validate_hypothesis_contract(contract):
        return {
            "valid": False,
            "engine": HYPOTHESIS_ENGINE,
            "version": HYPOTHESIS_VERSION,
            "decision": HypothesisDecision.UNKNOWN.value,
            "status": HypothesisResultStatus.INVALID.value,
            "confidence": 0.0,
            "readiness": 0.0,
            "can_advance": False,
        }

    result = contract.result
    assessment = result.assessment

    return {
        "valid": True,
        "engine": HYPOTHESIS_ENGINE,
        "version": HYPOTHESIS_VERSION,
        "request_id": contract.request_id,
        "contract_id": contract.contract_id,
        "hypothesis_id": result.hypothesis.hypothesis_id,
        "status": result.status.value,
        "decision": assessment.decision.value,
        "confidence": assessment.confidence_score,
        "confidence_level": assessment.confidence_level.value,
        "evidence_strength": assessment.evidence_strength,
        "validation_score": assessment.validation_score,
        "readiness": result.requirements.completeness_score,
        "testable": result.requirements.testable,
        "measurable": result.requirements.measurable,
        "can_advance": hypothesis_can_advance(contract),
        "warnings": list(result.warnings),
    }


def hypothesis_is_safe(
    contract: HypothesisContract,
) -> bool:

    return (
        validate_hypothesis_contract(contract)
        and not contract.is_action_request
    )


def hypothesis_allows_execution(
    contract: HypothesisContract,
) -> bool:
    return False


def hypothesis_allows_trade(
    contract: HypothesisContract,
) -> bool:
    return False


def hypothesis_allows_order(
    contract: HypothesisContract,
) -> bool:
    return False


def hypothesis_allows_position_change(
    contract: HypothesisContract,
) -> bool:
    return False


def hypothesis_allows_authorization(
    contract: HypothesisContract,
) -> bool:
    return False


def hypothesis_overrides_decision(
    contract: HypothesisContract,
) -> bool:
    return False


def hypothesis_overrides_risk(
    contract: HypothesisContract,
) -> bool:
    return False


def hypothesis_overrides_cas(
    contract: HypothesisContract,
) -> bool:
    return False


def get_hypothesis_engine_info() -> dict[str, Any]:

    return {
        "engine": HYPOTHESIS_ENGINE,
        "version": HYPOTHESIS_VERSION,
        "domain": "research",
        "role": "hypothesis_evaluation",
        "produces_execution": False,
        "produces_orders": False,
        "produces_authorization": False,
        "overrides_d13": False,
        "overrides_risk": False,
        "overrides_cas": False,
    }


def hypothesis_health_check() -> dict[str, Any]:

    checks = {
        "engine_name": bool(HYPOTHESIS_ENGINE),
        "version": bool(HYPOTHESIS_VERSION),
        "request_validation": callable(
            validate_hypothesis_request
        ),
        "reference_builder": callable(
            build_hypothesis_reference
        ),
        "requirements_builder": callable(
            build_hypothesis_requirements
        ),
        "assessment_builder": callable(
            build_hypothesis_assessment
        ),
        "result_builder": callable(
            build_hypothesis_result
        ),
        "contract_builder": callable(
            build_hypothesis_contract
        ),
        "result_validation": callable(
            validate_hypothesis_result
        ),
        "contract_validation": callable(
            validate_hypothesis_contract
        ),
        "execution_disabled": (
            hypothesis_allows_execution(
                None  # type: ignore[arg-type]
            ) is False
        ),
        "trade_disabled": (
            hypothesis_allows_trade(
                None  # type: ignore[arg-type]
            ) is False
        ),
        "order_disabled": (
            hypothesis_allows_order(
                None  # type: ignore[arg-type]
            ) is False
        ),
        "authorization_disabled": (
            hypothesis_allows_authorization(
                None  # type: ignore[arg-type]
            ) is False
        ),
        "d13_override_disabled": (
            hypothesis_overrides_decision(
                None  # type: ignore[arg-type]
            ) is False
        ),
        "risk_override_disabled": (
            hypothesis_overrides_risk(
                None  # type: ignore[arg-type]
            ) is False
        ),
        "cas_override_disabled": (
            hypothesis_overrides_cas(
                None  # type: ignore[arg-type]
            ) is False
        ),
    }

    return {
        "engine": HYPOTHESIS_ENGINE,
        "version": HYPOTHESIS_VERSION,
        "healthy": all(checks.values()),
        "checks": checks,
    }


def run_hypothesis_health_check() -> dict[str, Any]:
    return hypothesis_health_check()
# ============================================================
# ROBOMLM_PLUS
# app/intelligence/research/hypothesis.py
# RESEARCH HYPOTHESIS ENGINE
# PART 5/5
# ============================================================

def _hyp_enum_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    return value


def _hyp_safe_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)

    if hasattr(value, "__dict__"):
        return dict(vars(value))

    return {}


def _hyp_requirements_to_dict(
    requirements: HypothesisRequirements,
) -> dict[str, Any]:

    return {
        "statement_available": requirements.statement_available,
        "experiment_available": requirements.experiment_available,
        "dataset_available": requirements.dataset_available,
        "candidate_available": requirements.candidate_available,
        "evidence_available": requirements.evidence_available,
        "measurable": requirements.measurable,
        "testable": requirements.testable,
        "completeness_score": requirements.completeness_score,
    }


def _hyp_assessment_to_dict(
    assessment: HypothesisAssessment,
) -> dict[str, Any]:

    return {
        "evidence_strength": assessment.evidence_strength,
        "validation_score": assessment.validation_score,
        "confidence_score": assessment.confidence_score,
        "confidence_level": _hyp_enum_value(
            assessment.confidence_level
        ),
        "decision": _hyp_enum_value(
            assessment.decision
        ),
        "strengths": list(assessment.strengths),
        "weaknesses": list(assessment.weaknesses),
        "rationale": assessment.rationale,
    }


def hypothesis_result_to_dict(
    result: HypothesisResult,
) -> dict[str, Any]:

    return {
        "request_id": result.request_id,
        "result_id": result.result_id,
        "status": _hyp_enum_value(result.status),
        "hypothesis": {
            "hypothesis_id": result.hypothesis.hypothesis_id,
            "title": result.hypothesis.title,
            "type": _hyp_enum_value(result.hypothesis.hypothesis_type),
            "status": _hyp_enum_value(result.hypothesis.status),
            "priority": _hyp_enum_value(result.hypothesis.priority),
            "statement": result.hypothesis.statement,
            "experiment_id": result.hypothesis.experiment_id,
            "dataset_id": result.hypothesis.dataset_id,
            "candidate_id": result.hypothesis.candidate_id,
        },
        "requirements": _hyp_requirements_to_dict(
            result.requirements
        ),
        "assessment": _hyp_assessment_to_dict(
            result.assessment
        ),
        "rationale": result.rationale,
        "warnings": list(result.warnings),
        "created_at": result.created_at,
        "is_valid": result.is_valid,
        "accepted": result.accepted,
        "requires_review": result.requires_review,
        "requires_hold": result.requires_hold,
        "requires_retest": result.requires_retest,
    }


def hypothesis_contract_to_dict(
    contract: HypothesisContract,
) -> dict[str, Any]:

    return {
        "request_id": contract.request_id,
        "contract_id": contract.contract_id,
        "state": _hyp_enum_value(contract.state),
        "result": hypothesis_result_to_dict(
            contract.result
        ),
        "rationale": contract.rationale,
        "warnings": list(contract.warnings),
        "created_at": contract.created_at,
        "is_valid": contract.is_valid,
        "is_action_request": contract.is_action_request,
    }


def hypothesis_integrity_check() -> dict[str, Any]:

    checks = {
        "engine_constant": HYPOTHESIS_ENGINE
        == "ROBOMLM_RESEARCH_HYPOTHESIS_ENGINE",

        "version_present": bool(
            HYPOTHESIS_VERSION
        ),

        "engine_instance": isinstance(
            hypothesis_engine,
            HypothesisEngine,
        ),

        "request_validator": callable(
            validate_hypothesis_request
        ),

        "reference_builder": callable(
            build_hypothesis_reference
        ),

        "requirements_builder": callable(
            build_hypothesis_requirements
        ),

        "assessment_builder": callable(
            build_hypothesis_assessment
        ),

        "result_builder": callable(
            build_hypothesis_result
        ),

        "contract_builder": callable(
            build_hypothesis_contract
        ),

        "result_validator": callable(
            validate_hypothesis_result
        ),

        "contract_validator": callable(
            validate_hypothesis_contract
        ),

        "audit_available": callable(
            hypothesis_audit
        ),

        "health_check_available": callable(
            hypothesis_health_check
        ),

        "execution_disabled": (
            hypothesis_allows_execution(None) is False
        ),

        "trade_disabled": (
            hypothesis_allows_trade(None) is False
        ),

        "order_disabled": (
            hypothesis_allows_order(None) is False
        ),

        "position_change_disabled": (
            hypothesis_allows_position_change(None) is False
        ),

        "authorization_disabled": (
            hypothesis_allows_authorization(None) is False
        ),

        "d13_override_disabled": (
            hypothesis_overrides_decision(None) is False
        ),

        "risk_override_disabled": (
            hypothesis_overrides_risk(None) is False
        ),

        "cas_override_disabled": (
            hypothesis_overrides_cas(None) is False
        ),
    }

    return {
        "engine": HYPOTHESIS_ENGINE,
        "version": HYPOTHESIS_VERSION,
        "healthy": all(checks.values()),
        "checks": checks,
    }


def verify_hypothesis_integrity() -> bool:
    return bool(
        hypothesis_integrity_check().get(
            "healthy",
            False,
        )
    )


def run_hypothesis_integrity_check() -> dict[str, Any]:
    return hypothesis_integrity_check()


def run_hypothesis_health_check() -> dict[str, Any]:
    return hypothesis_health_check()


__all__ = [
    # Constants
    "HYPOTHESIS_ENGINE",
    "HYPOTHESIS_VERSION",

    # Enums
    "HypothesisStatus",
    "HypothesisType",
    "HypothesisPriority",
    "HypothesisDecision",
    "HypothesisConfidence",
    "HypothesisContractStatus",
    "HypothesisResultStatus",
    "HypothesisContractState",

    # Contracts / references
    "HypothesisRequest",
    "HypothesisReference",
    "HypothesisEvidenceReference",
    "HypothesisContractValidation",
    "HypothesisRequirements",
    "HypothesisAssessment",
    "HypothesisResult",
    "HypothesisContract",

    # Builders
    "build_hypothesis_reference",
    "validate_hypothesis_request",
    "build_hypothesis_requirements",
    "calculate_hypothesis_evidence_strength",
    "calculate_hypothesis_validation_score",
    "calculate_hypothesis_confidence",
    "determine_hypothesis_confidence_level",
    "determine_hypothesis_decision",
    "build_hypothesis_assessment",
    "determine_hypothesis_result_status",
    "build_hypothesis_result",
    "determine_hypothesis_contract_state",
    "build_hypothesis_contract",

    # Engine
    "HypothesisEngine",
    "hypothesis_engine",
    "evaluate_hypothesis",
    "analyze_hypothesis",
    "review_hypothesis",

    # Validation / gates
    "validate_hypothesis_result",
    "validate_hypothesis_contract",
    "hypothesis_ready",
    "hypothesis_can_advance",
    "hypothesis_decision",
    "hypothesis_status",
    "hypothesis_confidence",
    "hypothesis_readiness",

    # Audit / safety
    "hypothesis_audit",
    "hypothesis_is_safe",
    "hypothesis_allows_execution",
    "hypothesis_allows_trade",
    "hypothesis_allows_order",
    "hypothesis_allows_position_change",
    "hypothesis_allows_authorization",
    "hypothesis_overrides_decision",
    "hypothesis_overrides_risk",
    "hypothesis_overrides_cas",

    # Diagnostics
    "get_hypothesis_engine_info",
    "hypothesis_health_check",
    "run_hypothesis_health_check",
    "hypothesis_integrity_check",
    "verify_hypothesis_integrity",
    "run_hypothesis_integrity_check",

    # Serialization
    "hypothesis_result_to_dict",
    "hypothesis_contract_to_dict",
]