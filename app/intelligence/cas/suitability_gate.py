# ============================================================
# ROBOMLM CAS — SUITABILITY GATE
# Part 1/5
#
# Role:
#   Validate whether a proposed decision/action is suitable
#   for the supplied user/account/plan/permission context.
#
# Authority:
#   CAS internal gate only.
#
# MUST NOT:
#   - generate a trading decision
#   - modify D13
#   - override Risk
#   - override CAS
#   - execute an order
#   - change a position
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Optional
from uuid import uuid4


SUITABILITY_GATE_ENGINE = "ROBOMLM_CAS_SUITABILITY_GATE"
SUITABILITY_GATE_VERSION = "1.0"


# ============================================================
# ENUMS
# ============================================================

class SuitabilityStatus(str, Enum):
    NEW = "NEW"
    VALIDATING = "VALIDATING"
    SUITABLE = "SUITABLE"
    CONDITIONAL = "CONDITIONAL"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    UNSUITABLE = "UNSUITABLE"
    INVALID = "INVALID"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"


class SuitabilityDecision(str, Enum):
    ALLOW = "ALLOW"
    ALLOW_WITH_RESTRICTION = "ALLOW_WITH_RESTRICTION"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


class SuitabilityMode(str, Enum):
    ANALYSIS = "ANALYSIS"
    SIMULATION = "SIMULATION"
    AUTHORIZED_EXECUTION = "AUTHORIZED_EXECUTION"
    UNKNOWN = "UNKNOWN"


class SuitabilityPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class SuitabilityContractStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


# ============================================================
# REQUEST CONTRACT
# ============================================================

@dataclass(frozen=True)
class SuitabilityRequest:
    """
    Input contract for suitability evaluation.

    This is a validation request, not an execution request.
    """

    market: str
    instrument: str
    contract: Optional[str] = None

    user_id: Optional[str] = None
    account_id: Optional[str] = None
    plan_id: Optional[str] = None

    permission: Optional[str] = None
    role: Optional[str] = None

    action: Optional[str] = None
    direction: Optional[str] = None
    mode: SuitabilityMode = SuitabilityMode.UNKNOWN

    strategy: Optional[str] = None
    timeframe: Optional[str] = None

    priority: SuitabilityPriority = SuitabilityPriority.MEDIUM

    metadata: Mapping[str, Any] = field(default_factory=dict)

    request_id: str = field(
        default_factory=lambda: str(uuid4())
    )


# ============================================================
# RESULT REFERENCE
# ============================================================

@dataclass(frozen=True)
class SuitabilityReference:
    request_id: str
    user_id: Optional[str]
    account_id: Optional[str]
    plan_id: Optional[str]

    market: str
    instrument: str
    contract: Optional[str]

    permission: Optional[str]
    role: Optional[str]

    action: Optional[str]
    direction: Optional[str]

    mode: SuitabilityMode
    strategy: Optional[str]
    timeframe: Optional[str]

    timestamp: datetime

    status: SuitabilityStatus
    decision: SuitabilityDecision

    suitability_score: float
    restrictions: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()


# ============================================================
# CONTRACT VALIDATION
# ============================================================

@dataclass(frozen=True)
class SuitabilityContractValidation:
    valid: bool

    market_available: bool
    instrument_available: bool
    user_available: bool
    account_available: bool
    plan_available: bool
    permission_available: bool

    mode_valid: bool
    metadata_valid: bool

    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:
        return self.valid


# ============================================================
# HELPERS
# ============================================================

def _sg_read_value(
    source: Any,
    key: str,
    default: Any = None,
) -> Any:
    if source is None:
        return default

    if isinstance(source, Mapping):
        return source.get(key, default)

    return getattr(source, key, default)


def _sg_text(value: Any) -> Optional[str]:
    if value is None:
        return None

    text = str(value).strip()

    return text if text else None


def _sg_enum(
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
        if member.value == text:
            return member

    return default


def _sg_bool(value: Any) -> bool:
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
            "allowed",
        }

    return bool(value)


def _sg_timestamp(value: Any) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)

    return datetime.now(timezone.utc)


# ============================================================
# REQUEST BUILDER
# ============================================================

def build_suitability_request(
    source: Any = None,
    **kwargs: Any,
) -> SuitabilityRequest:

    market = _sg_text(
        kwargs.get(
            "market",
            _sg_read_value(source, "market"),
        )
    ) or ""

    instrument = _sg_text(
        kwargs.get(
            "instrument",
            _sg_read_value(source, "instrument"),
        )
    ) or ""

    mode = _sg_enum(
        kwargs.get(
            "mode",
            _sg_read_value(source, "mode"),
        ),
        SuitabilityMode,
        SuitabilityMode.UNKNOWN,
    )

    priority = _sg_enum(
        kwargs.get(
            "priority",
            _sg_read_value(source, "priority"),
        ),
        SuitabilityPriority,
        SuitabilityPriority.MEDIUM,
    )

    metadata = kwargs.get(
        "metadata",
        _sg_read_value(source, "metadata", {}),
    )

    if not isinstance(metadata, Mapping):
        metadata = {}

    return SuitabilityRequest(
        market=market,
        instrument=instrument,

        contract=(
            _sg_text(
                kwargs.get(
                    "contract",
                    _sg_read_value(source, "contract"),
                )
            )
        ),

        user_id=(
            _sg_text(
                kwargs.get(
                    "user_id",
                    _sg_read_value(source, "user_id"),
                )
            )
        ),

        account_id=(
            _sg_text(
                kwargs.get(
                    "account_id",
                    _sg_read_value(source, "account_id"),
                )
            )
        ),

        plan_id=(
            _sg_text(
                kwargs.get(
                    "plan_id",
                    _sg_read_value(source, "plan_id"),
                )
            )
        ),

        permission=(
            _sg_text(
                kwargs.get(
                    "permission",
                    _sg_read_value(source, "permission"),
                )
            )
        ),

        role=(
            _sg_text(
                kwargs.get(
                    "role",
                    _sg_read_value(source, "role"),
                )
            )
        ),

        action=(
            _sg_text(
                kwargs.get(
                    "action",
                    _sg_read_value(source, "action"),
                )
            )
        ),

        direction=(
            _sg_text(
                kwargs.get(
                    "direction",
                    _sg_read_value(source, "direction"),
                )
            )
        ),

        mode=mode,

        strategy=(
            _sg_text(
                kwargs.get(
                    "strategy",
                    _sg_read_value(source, "strategy"),
                )
            )
        ),

        timeframe=(
            _sg_text(
                kwargs.get(
                    "timeframe",
                    _sg_read_value(source, "timeframe"),
                )
            )
        ),

        priority=priority,

        metadata=dict(metadata),

        request_id=(
            _sg_text(
                kwargs.get(
                    "request_id",
                    _sg_read_value(source, "request_id"),
                )
            )
            or str(uuid4())
        ),
    )


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_suitability_request(
    request: Optional[SuitabilityRequest],
) -> SuitabilityContractValidation:

    if not isinstance(request, SuitabilityRequest):
        return SuitabilityContractValidation(
            valid=False,
            market_available=False,
            instrument_available=False,
            user_available=False,
            account_available=False,
            plan_available=False,
            permission_available=False,
            mode_valid=False,
            metadata_valid=False,
            errors=("Invalid SuitabilityRequest",),
        )

    errors: list[str] = []
    warnings: list[str] = []

    market_available = bool(_sg_text(request.market))
    instrument_available = bool(_sg_text(request.instrument))

    user_available = bool(_sg_text(request.user_id))
    account_available = bool(_sg_text(request.account_id))
    plan_available = bool(_sg_text(request.plan_id))
    permission_available = bool(_sg_text(request.permission))

    mode_valid = (
        request.mode != SuitabilityMode.UNKNOWN
    )

    metadata_valid = isinstance(
        request.metadata,
        Mapping,
    )

    if not market_available:
        errors.append("Market is required")

    if not instrument_available:
        errors.append("Instrument is required")

    if not user_available:
        errors.append("User identity is required")

    if not account_available:
        errors.append("Account identity is required")

    if not plan_available:
        warnings.append("Plan identity is missing")

    if not permission_available:
        warnings.append("Permission is missing")

    if not mode_valid:
        errors.append("Valid suitability mode is required")

    if not metadata_valid:
        errors.append("Metadata must be a mapping")

    valid = len(errors) == 0

    return SuitabilityContractValidation(
        valid=valid,
        market_available=market_available,
        instrument_available=instrument_available,
        user_available=user_available,
        account_available=account_available,
        plan_available=plan_available,
        permission_available=permission_available,
        mode_valid=mode_valid,
        metadata_valid=metadata_valid,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )
# ============================================================
# ROBOMLM CAS — SUITABILITY GATE
# Part 2/5
#
# Requirements • Readiness • Assessment • Core Evaluation
# ============================================================


# ============================================================
# ENUMS — EVALUATION STATE
# ============================================================

class SuitabilityDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    UNKNOWN = "UNKNOWN"


class SuitabilityConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONFLICTING = "CONFLICTING"
    INSUFFICIENT = "INSUFFICIENT"
    UNKNOWN = "UNKNOWN"


class SuitabilityReadiness(str, Enum):
    READY = "READY"
    CONDITIONAL = "CONDITIONAL"
    NOT_READY = "NOT_READY"
    UNKNOWN = "UNKNOWN"


# ============================================================
# REQUIREMENTS CONTRACT
# ============================================================

@dataclass(frozen=True)
class SuitabilityRequirements:
    request_valid: bool

    market_available: bool
    instrument_available: bool

    user_available: bool
    account_available: bool
    plan_available: bool
    permission_available: bool

    role_available: bool
    action_available: bool
    direction_available: bool

    mode_defined: bool
    strategy_available: bool
    timeframe_available: bool

    data_state: SuitabilityDataState
    consistency: SuitabilityConsistency
    readiness: SuitabilityReadiness

    completeness_score: float

    warnings: tuple[str, ...] = ()


# ============================================================
# ASSESSMENT CONTRACT
# ============================================================

@dataclass(frozen=True)
class SuitabilityAssessment:
    readiness: SuitabilityReadiness
    data_state: SuitabilityDataState
    consistency: SuitabilityConsistency

    suitability_score: float
    confidence_score: float
    completeness_score: float

    strengths: tuple[str, ...] = ()
    weaknesses: tuple[str, ...] = ()
    restrictions: tuple[str, ...] = ()

    rationale: str = ""


# ============================================================
# DATA STATE
# ============================================================

def evaluate_suitability_data_state(
    request: Optional[SuitabilityRequest],
) -> SuitabilityDataState:

    if not isinstance(request, SuitabilityRequest):
        return SuitabilityDataState.MISSING

    components = (
        bool(_sg_text(request.market)),
        bool(_sg_text(request.instrument)),
        bool(_sg_text(request.user_id)),
        bool(_sg_text(request.account_id)),
        bool(_sg_text(request.plan_id)),
        bool(_sg_text(request.permission)),
        bool(_sg_text(request.action)),
        request.mode != SuitabilityMode.UNKNOWN,
    )

    available = sum(1 for value in components if value)

    if available == len(components):
        return SuitabilityDataState.COMPLETE

    if available == 0:
        return SuitabilityDataState.MISSING

    if available >= len(components) // 2:
        return SuitabilityDataState.PARTIAL

    return SuitabilityDataState.UNKNOWN


# ============================================================
# CONSISTENCY
# ============================================================

def evaluate_suitability_consistency(
    request: Optional[SuitabilityRequest],
) -> SuitabilityConsistency:

    if not isinstance(request, SuitabilityRequest):
        return SuitabilityConsistency.INSUFFICIENT

    if request.mode == SuitabilityMode.UNKNOWN:
        return SuitabilityConsistency.INSUFFICIENT

    metadata = request.metadata

    if not isinstance(metadata, Mapping):
        return SuitabilityConsistency.CONFLICTING

    # Explicit conflict signals supplied by upstream systems.
    conflict_keys = (
        "conflict",
        "conflicting",
        "suitability_conflict",
        "account_conflict",
        "permission_conflict",
    )

    for key in conflict_keys:
        if _sg_bool(metadata.get(key)):
            return SuitabilityConsistency.CONFLICTING

    # Explicit unsuitable restriction signals are not automatically
    # treated as structural conflict. They are evaluated later.
    return SuitabilityConsistency.CONSISTENT


# ============================================================
# COMPLETENESS
# ============================================================

def calculate_suitability_completeness(
    request: Optional[SuitabilityRequest],
) -> float:

    if not isinstance(request, SuitabilityRequest):
        return 0.0

    checks = (
        bool(_sg_text(request.market)),
        bool(_sg_text(request.instrument)),
        bool(_sg_text(request.user_id)),
        bool(_sg_text(request.account_id)),
        bool(_sg_text(request.plan_id)),
        bool(_sg_text(request.permission)),
        bool(_sg_text(request.role)),
        bool(_sg_text(request.action)),
        bool(_sg_text(request.direction)),
        request.mode != SuitabilityMode.UNKNOWN,
        bool(_sg_text(request.strategy)),
        bool(_sg_text(request.timeframe)),
    )

    return round(
        (sum(1 for value in checks if value) / len(checks)) * 100.0,
        2,
    )


# ============================================================
# READINESS
# ============================================================

def evaluate_suitability_readiness(
    request: Optional[SuitabilityRequest],
    consistency: Optional[SuitabilityConsistency] = None,
) -> SuitabilityReadiness:

    if not isinstance(request, SuitabilityRequest):
        return SuitabilityReadiness.NOT_READY

    validation = validate_suitability_request(request)

    if not validation.valid:
        return SuitabilityReadiness.NOT_READY

    if consistency is None:
        consistency = evaluate_suitability_consistency(request)

    if consistency == SuitabilityConsistency.CONFLICTING:
        return SuitabilityReadiness.NOT_READY

    if consistency == SuitabilityConsistency.INSUFFICIENT:
        return SuitabilityReadiness.CONDITIONAL

    completeness = calculate_suitability_completeness(request)

    if completeness >= 85.0:
        return SuitabilityReadiness.READY

    if completeness >= 50.0:
        return SuitabilityReadiness.CONDITIONAL

    return SuitabilityReadiness.NOT_READY


# ============================================================
# REQUIREMENTS EVALUATION
# ============================================================

def evaluate_suitability_requirements(
    request: Optional[SuitabilityRequest],
) -> SuitabilityRequirements:

    validation = validate_suitability_request(request)

    if not isinstance(request, SuitabilityRequest):
        return SuitabilityRequirements(
            request_valid=False,
            market_available=False,
            instrument_available=False,
            user_available=False,
            account_available=False,
            plan_available=False,
            permission_available=False,
            role_available=False,
            action_available=False,
            direction_available=False,
            mode_defined=False,
            strategy_available=False,
            timeframe_available=False,
            data_state=SuitabilityDataState.MISSING,
            consistency=SuitabilityConsistency.INSUFFICIENT,
            readiness=SuitabilityReadiness.NOT_READY,
            completeness_score=0.0,
            warnings=("Invalid suitability request",),
        )

    data_state = evaluate_suitability_data_state(request)
    consistency = evaluate_suitability_consistency(request)
    completeness = calculate_suitability_completeness(request)

    readiness = evaluate_suitability_readiness(
        request,
        consistency,
    )

    warnings = list(validation.warnings)

    if not _sg_text(request.role):
        warnings.append("Role information is missing")

    if not _sg_text(request.action):
        warnings.append("Action information is missing")

    if not _sg_text(request.direction):
        warnings.append("Direction information is missing")

    if not _sg_text(request.strategy):
        warnings.append("Strategy information is missing")

    if not _sg_text(request.timeframe):
        warnings.append("Timeframe information is missing")

    return SuitabilityRequirements(
        request_valid=validation.valid,

        market_available=validation.market_available,
        instrument_available=validation.instrument_available,

        user_available=validation.user_available,
        account_available=validation.account_available,
        plan_available=validation.plan_available,
        permission_available=validation.permission_available,

        role_available=bool(_sg_text(request.role)),
        action_available=bool(_sg_text(request.action)),
        direction_available=bool(_sg_text(request.direction)),

        mode_defined=request.mode != SuitabilityMode.UNKNOWN,
        strategy_available=bool(_sg_text(request.strategy)),
        timeframe_available=bool(_sg_text(request.timeframe)),

        data_state=data_state,
        consistency=consistency,
        readiness=readiness,

        completeness_score=completeness,
        warnings=tuple(dict.fromkeys(warnings)),
    )


# ============================================================
# SUITABILITY SCORE
# ============================================================

def calculate_suitability_score(
    request: Optional[SuitabilityRequest],
    requirements: Optional[SuitabilityRequirements] = None,
) -> float:

    if not isinstance(request, SuitabilityRequest):
        return 0.0

    if requirements is None:
        requirements = evaluate_suitability_requirements(request)

    score = 0.0

    # Identity / account context
    if requirements.user_available:
        score += 15.0

    if requirements.account_available:
        score += 15.0

    if requirements.plan_available:
        score += 10.0

    # Market/action context
    if requirements.market_available:
        score += 10.0

    if requirements.instrument_available:
        score += 10.0

    if requirements.action_available:
        score += 10.0

    if requirements.permission_available:
        score += 15.0

    # Operational context
    if requirements.mode_defined:
        score += 5.0

    if requirements.strategy_available:
        score += 5.0

    if requirements.timeframe_available:
        score += 5.0

    if requirements.consistency == SuitabilityConsistency.CONFLICTING:
        return 0.0

    if requirements.consistency == SuitabilityConsistency.INSUFFICIENT:
        score *= 0.70

    return round(
        max(0.0, min(100.0, score)),
        2,
    )


# ============================================================
# CONFIDENCE
# ============================================================

def calculate_suitability_confidence(
    requirements: SuitabilityRequirements,
    suitability_score: float,
) -> float:

    if requirements.consistency == SuitabilityConsistency.CONFLICTING:
        return 0.0

    confidence = (
        requirements.completeness_score * 0.60
        + suitability_score * 0.40
    )

    if requirements.consistency == SuitabilityConsistency.CONSISTENT:
        confidence += 5.0

    elif requirements.consistency == SuitabilityConsistency.INSUFFICIENT:
        confidence -= 15.0

    return round(
        max(0.0, min(100.0, confidence)),
        2,
    )


# ============================================================
# RESTRICTION EXTRACTION
# ============================================================

def extract_suitability_restrictions(
    request: Optional[SuitabilityRequest],
) -> tuple[str, ...]:

    if not isinstance(request, SuitabilityRequest):
        return ("INVALID_REQUEST",)

    restrictions: list[str] = []

    metadata = request.metadata

    if _sg_bool(metadata.get("restricted_instrument")):
        restrictions.append("INSTRUMENT_RESTRICTED")

    if _sg_bool(metadata.get("restricted_market")):
        restrictions.append("MARKET_RESTRICTED")

    if _sg_bool(metadata.get("restricted_action")):
        restrictions.append("ACTION_RESTRICTED")

    if _sg_bool(metadata.get("plan_restricted")):
        restrictions.append("PLAN_RESTRICTED")

    if _sg_bool(metadata.get("permission_limited")):
        restrictions.append("PERMISSION_LIMITED")

    if _sg_bool(metadata.get("manual_only")):
        restrictions.append("MANUAL_ONLY")

    return tuple(dict.fromkeys(restrictions))


# ============================================================
# ASSESSMENT BUILDER
# ============================================================

def build_suitability_assessment(
    request: Optional[SuitabilityRequest],
    requirements: Optional[SuitabilityRequirements] = None,
) -> SuitabilityAssessment:

    if not isinstance(request, SuitabilityRequest):
        return SuitabilityAssessment(
            readiness=SuitabilityReadiness.NOT_READY,
            data_state=SuitabilityDataState.MISSING,
            consistency=SuitabilityConsistency.INSUFFICIENT,
            suitability_score=0.0,
            confidence_score=0.0,
            completeness_score=0.0,
            weaknesses=("Invalid suitability request",),
            rationale="Suitability cannot be established from an invalid request.",
        )

    if requirements is None:
        requirements = evaluate_suitability_requirements(request)

    suitability_score = calculate_suitability_score(
        request,
        requirements,
    )

    confidence_score = calculate_suitability_confidence(
        requirements,
        suitability_score,
    )

    restrictions = extract_suitability_restrictions(request)

    strengths: list[str] = []
    weaknesses: list[str] = []

    if requirements.user_available:
        strengths.append("User identity available")

    if requirements.account_available:
        strengths.append("Account identity available")

    if requirements.market_available:
        strengths.append("Market context available")

    if requirements.instrument_available:
        strengths.append("Instrument context available")

    if requirements.permission_available:
        strengths.append("Permission context available")

    if requirements.plan_available:
        strengths.append("Plan context available")

    if requirements.consistency == SuitabilityConsistency.CONFLICTING:
        weaknesses.append("Suitability context contains conflict")

    if not requirements.permission_available:
        weaknesses.append("Permission context unavailable")

    if not requirements.account_available:
        weaknesses.append("Account context unavailable")

    if restrictions:
        weaknesses.append("One or more suitability restrictions detected")

    if requirements.readiness == SuitabilityReadiness.READY:
        rationale = (
            "Suitability context is structurally complete and "
            "consistent enough for CAS suitability evaluation."
        )

    elif requirements.readiness == SuitabilityReadiness.CONDITIONAL:
        rationale = (
            "Suitability context is partially complete and requires "
            "conditional handling or additional validation."
        )

    elif requirements.consistency == SuitabilityConsistency.CONFLICTING:
        rationale = (
            "Suitability evaluation is blocked because the supplied "
            "context contains an explicit conflict."
        )

    else:
        rationale = (
            "Suitability cannot currently be established with sufficient "
            "structural confidence."
        )

    return SuitabilityAssessment(
        readiness=requirements.readiness,
        data_state=requirements.data_state,
        consistency=requirements.consistency,
        suitability_score=suitability_score,
        confidence_score=confidence_score,
        completeness_score=requirements.completeness_score,
        strengths=tuple(strengths),
        weaknesses=tuple(weaknesses),
        restrictions=restrictions,
        rationale=rationale,
    )


# ============================================================
# CORE SUITABILITY DETERMINATION
# ============================================================

def determine_suitability_decision(
    request: Optional[SuitabilityRequest],
    assessment: Optional[SuitabilityAssessment] = None,
) -> SuitabilityDecision:

    if not isinstance(request, SuitabilityRequest):
        return SuitabilityDecision.BLOCK

    if assessment is None:
        requirements = evaluate_suitability_requirements(request)
        assessment = build_suitability_assessment(
            request,
            requirements,
        )

    if assessment.consistency == SuitabilityConsistency.CONFLICTING:
        return SuitabilityDecision.BLOCK

    if assessment.readiness == SuitabilityReadiness.NOT_READY:
        return SuitabilityDecision.REVIEW_REQUIRED

    if assessment.confidence_score < 50.0:
        return SuitabilityDecision.REVIEW_REQUIRED

    if assessment.suitability_score < 50.0:
        return SuitabilityDecision.BLOCK

    if assessment.restrictions:
        return SuitabilityDecision.ALLOW_WITH_RESTRICTION

    if assessment.readiness == SuitabilityReadiness.CONDITIONAL:
        return SuitabilityDecision.REVIEW_REQUIRED

    return SuitabilityDecision.ALLOW
# ============================================================
# ROBOMLM CAS — SUITABILITY GATE
# Part 3/5
#
# Action • Result • Contract • Engine
# ============================================================


# ============================================================
# ENUMS — ACTION / RESULT / CONTRACT
# ============================================================

class SuitabilityActionState(str, Enum):
    NONE = "NONE"
    EVALUATE = "EVALUATE"
    ALLOW = "ALLOW"
    RESTRICT = "RESTRICT"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"
    INVALIDATE = "INVALIDATE"


class SuitabilityContractState(str, Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


class SuitabilityResultStatus(str, Enum):
    ALLOWED = "ALLOWED"
    RESTRICTED = "RESTRICTED"
    REVIEW = "REVIEW"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


# ============================================================
# ACTION CONTRACT
# ============================================================

@dataclass(frozen=True)
class SuitabilityAction:
    action_id: str
    request_id: str

    state: SuitabilityActionState
    decision: SuitabilityDecision

    is_action_request: bool
    is_execution_request: bool

    restrictions: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# ============================================================
# RESULT CONTRACT
# ============================================================

@dataclass(frozen=True)
class SuitabilityResult:
    result_id: str
    request_id: str

    status: SuitabilityResultStatus
    decision: SuitabilityDecision

    suitability_status: SuitabilityStatus
    readiness: SuitabilityReadiness

    suitability_score: float
    confidence_score: float
    completeness_score: float

    data_state: SuitabilityDataState
    consistency: SuitabilityConsistency

    restrictions: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()
    strengths: tuple[str, ...] = ()
    weaknesses: tuple[str, ...] = ()

    rationale: str = ""

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# ============================================================
# CONTRACT WRAPPER
# ============================================================

@dataclass(frozen=True)
class SuitabilityContract:
    contract_id: str
    request_id: str

    state: SuitabilityContractState

    request: SuitabilityRequest
    validation: SuitabilityContractValidation
    requirements: SuitabilityRequirements
    assessment: SuitabilityAssessment
    result: SuitabilityResult
    action: SuitabilityAction

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# ============================================================
# RESULT STATUS
# ============================================================

def determine_suitability_result_status(
    decision: SuitabilityDecision,
    assessment: SuitabilityAssessment,
) -> SuitabilityResultStatus:

    if decision == SuitabilityDecision.BLOCK:
        return SuitabilityResultStatus.BLOCKED

    if decision == SuitabilityDecision.REVIEW_REQUIRED:
        return SuitabilityResultStatus.REVIEW

    if decision == SuitabilityDecision.ALLOW_WITH_RESTRICTION:
        return SuitabilityResultStatus.RESTRICTED

    if decision == SuitabilityDecision.ALLOW:
        return SuitabilityResultStatus.ALLOWED

    return SuitabilityResultStatus.INVALID


# ============================================================
# SUITABILITY STATUS
# ============================================================

def determine_suitability_status(
    decision: SuitabilityDecision,
    assessment: SuitabilityAssessment,
) -> SuitabilityStatus:

    if assessment.consistency == SuitabilityConsistency.CONFLICTING:
        return SuitabilityStatus.BLOCKED

    if assessment.readiness == SuitabilityReadiness.NOT_READY:
        if decision == SuitabilityDecision.BLOCK:
            return SuitabilityStatus.UNSUITABLE
        return SuitabilityStatus.REVIEW_REQUIRED

    if decision == SuitabilityDecision.ALLOW_WITH_RESTRICTION:
        return SuitabilityStatus.CONDITIONAL

    if decision == SuitabilityDecision.REVIEW_REQUIRED:
        return SuitabilityStatus.REVIEW_REQUIRED

    if decision == SuitabilityDecision.ALLOW:
        return SuitabilityStatus.SUITABLE

    if decision == SuitabilityDecision.BLOCK:
        return SuitabilityStatus.UNSUITABLE

    return SuitabilityStatus.UNKNOWN


# ============================================================
# ACTION STATE
# ============================================================

def determine_suitability_action_state(
    decision: SuitabilityDecision,
    assessment: SuitabilityAssessment,
) -> SuitabilityActionState:

    if decision == SuitabilityDecision.ALLOW:
        return SuitabilityActionState.ALLOW

    if decision == SuitabilityDecision.ALLOW_WITH_RESTRICTION:
        return SuitabilityActionState.RESTRICT

    if decision == SuitabilityDecision.REVIEW_REQUIRED:
        return SuitabilityActionState.REVIEW

    if decision == SuitabilityDecision.BLOCK:
        return SuitabilityActionState.BLOCK

    return SuitabilityActionState.INVALIDATE


# ============================================================
# ACTION BUILDER
# ============================================================

def build_suitability_action(
    request: SuitabilityRequest,
    decision: SuitabilityDecision,
    assessment: SuitabilityAssessment,
) -> SuitabilityAction:

    state = determine_suitability_action_state(
        decision,
        assessment,
    )

    reasons = list(assessment.weaknesses)

    if assessment.rationale:
        reasons.append(assessment.rationale)

    return SuitabilityAction(
        action_id=str(uuid4()),
        request_id=request.request_id,

        state=state,
        decision=decision,

        # Suitability evaluates authorization context.
        # It does NOT represent an external action/execution request.
        is_action_request=False,
        is_execution_request=False,

        restrictions=assessment.restrictions,
        reasons=tuple(dict.fromkeys(reasons)),
    )


# ============================================================
# RESULT BUILDER
# ============================================================

def build_suitability_result(
    request: SuitabilityRequest,
    assessment: SuitabilityAssessment,
    decision: SuitabilityDecision,
) -> SuitabilityResult:

    status = determine_suitability_result_status(
        decision,
        assessment,
    )

    suitability_status = determine_suitability_status(
        decision,
        assessment,
    )

    reasons = list(assessment.weaknesses)

    if assessment.rationale:
        reasons.append(assessment.rationale)

    return SuitabilityResult(
        result_id=str(uuid4()),
        request_id=request.request_id,

        status=status,
        decision=decision,

        suitability_status=suitability_status,
        readiness=assessment.readiness,

        suitability_score=assessment.suitability_score,
        confidence_score=assessment.confidence_score,
        completeness_score=assessment.completeness_score,

        data_state=assessment.data_state,
        consistency=assessment.consistency,

        restrictions=assessment.restrictions,
        reasons=tuple(dict.fromkeys(reasons)),
        strengths=assessment.strengths,
        weaknesses=assessment.weaknesses,

        rationale=assessment.rationale,
    )


# ============================================================
# CONTRACT STATE
# ============================================================

def determine_suitability_contract_state(
    validation: SuitabilityContractValidation,
    result: SuitabilityResult,
) -> SuitabilityContractState:

    if not validation.valid:
        return SuitabilityContractState.INVALID

    if result.status == SuitabilityResultStatus.BLOCKED:
        return SuitabilityContractState.BLOCKED

    if result.status == SuitabilityResultStatus.INVALID:
        return SuitabilityContractState.INVALID

    if result.status == SuitabilityResultStatus.REVIEW:
        return SuitabilityContractState.INCOMPLETE

    return SuitabilityContractState.COMPLETE


# ============================================================
# CONTRACT BUILDER
# ============================================================

def build_suitability_contract(
    request: Optional[SuitabilityRequest],
) -> SuitabilityContract:

    validation = validate_suitability_request(request)

    if not isinstance(request, SuitabilityRequest):
        invalid_request = SuitabilityRequest(
            market="",
            instrument="",
        )

        requirements = evaluate_suitability_requirements(
            invalid_request
        )

        assessment = build_suitability_assessment(
            invalid_request,
            requirements,
        )

        decision = SuitabilityDecision.BLOCK

        result = build_suitability_result(
            invalid_request,
            assessment,
            decision,
        )

        action = build_suitability_action(
            invalid_request,
            decision,
            assessment,
        )

        return SuitabilityContract(
            contract_id=str(uuid4()),
            request_id=invalid_request.request_id,
            state=SuitabilityContractState.INVALID,

            request=invalid_request,
            validation=validation,
            requirements=requirements,
            assessment=assessment,
            result=result,
            action=action,
        )

    requirements = evaluate_suitability_requirements(
        request
    )

    assessment = build_suitability_assessment(
        request,
        requirements,
    )

    decision = determine_suitability_decision(
        request,
        assessment,
    )

    result = build_suitability_result(
        request,
        assessment,
        decision,
    )

    action = build_suitability_action(
        request,
        decision,
        assessment,
    )

    state = determine_suitability_contract_state(
        validation,
        result,
    )

    return SuitabilityContract(
        contract_id=str(uuid4()),
        request_id=request.request_id,
        state=state,

        request=request,
        validation=validation,
        requirements=requirements,
        assessment=assessment,
        result=result,
        action=action,
    )


# ============================================================
# ENGINE
# ============================================================

class SuitabilityGateEngine:
    """
    CAS internal suitability engine.

    Authority:
        Evaluate suitability context only.

    It cannot:
        - generate D13 decisions
        - modify D13
        - override Risk
        - override CAS
        - authorize execution
        - place orders
        - modify positions
    """

    _instance: Optional["SuitabilityGateEngine"] = None

    def __new__(
        cls,
        *args: Any,
        **kwargs: Any,
    ) -> "SuitabilityGateEngine":

        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def evaluate(
        self,
        request: Optional[SuitabilityRequest] = None,
        source: Any = None,
        **kwargs: Any,
    ) -> SuitabilityContract:

        if request is None:
            request = build_suitability_request(
                source,
                **kwargs,
            )

        return build_suitability_contract(request)

    def check(
        self,
        request: Optional[SuitabilityRequest] = None,
        source: Any = None,
        **kwargs: Any,
    ) -> SuitabilityResult:

        contract = self.evaluate(
            request=request,
            source=source,
            **kwargs,
        )

        return contract.result

    def review(
        self,
        request: Optional[SuitabilityRequest] = None,
        source: Any = None,
        **kwargs: Any,
    ) -> SuitabilityAssessment:

        if request is None:
            request = build_suitability_request(
                source,
                **kwargs,
            )

        requirements = evaluate_suitability_requirements(
            request
        )

        return build_suitability_assessment(
            request,
            requirements,
        )

    @property
    def engine_name(self) -> str:
        return SUITABILITY_GATE_ENGINE

    @property
    def engine_version(self) -> str:
        return SUITABILITY_GATE_VERSION


# ============================================================
# PUBLIC ENGINE ACCESS
# ============================================================

def get_suitability_gate_engine() -> SuitabilityGateEngine:
    return SuitabilityGateEngine()


# ============================================================
# PUBLIC EVALUATION API
# ============================================================

def evaluate_suitability(
    request: Optional[SuitabilityRequest] = None,
    source: Any = None,
    **kwargs: Any,
) -> SuitabilityContract:

    return get_suitability_gate_engine().evaluate(
        request=request,
        source=source,
        **kwargs,
    )


def check_suitability(
    request: Optional[SuitabilityRequest] = None,
    source: Any = None,
    **kwargs: Any,
) -> SuitabilityResult:

    return get_suitability_gate_engine().check(
        request=request,
        source=source,
        **kwargs,
    )


def review_suitability(
    request: Optional[SuitabilityRequest] = None,
    source: Any = None,
    **kwargs: Any,
) -> SuitabilityAssessment:

    return get_suitability_gate_engine().review(
        request=request,
        source=source,
        **kwargs,
    )
# ============================================================
# ROBOMLM CAS — SUITABILITY GATE
# Part 4/5
#
# Strict Validation • Safety • Audit • Authority • Health
# ============================================================


# ============================================================
# RESULT VALIDATION
# ============================================================

def validate_suitability_result(
    result: Optional[SuitabilityResult],
) -> bool:

    if not isinstance(result, SuitabilityResult):
        return False

    if not result.result_id:
        return False

    if not result.request_id:
        return False

    if result.status == SuitabilityResultStatus.INVALID:
        return False

    if not 0.0 <= result.suitability_score <= 100.0:
        return False

    if not 0.0 <= result.confidence_score <= 100.0:
        return False

    if not 0.0 <= result.completeness_score <= 100.0:
        return False

    if result.decision == SuitabilityDecision.ALLOW:
        if result.status != SuitabilityResultStatus.ALLOWED:
            return False

    if result.decision == SuitabilityDecision.ALLOW_WITH_RESTRICTION:
        if result.status != SuitabilityResultStatus.RESTRICTED:
            return False

    if result.decision == SuitabilityDecision.REVIEW_REQUIRED:
        if result.status != SuitabilityResultStatus.REVIEW:
            return False

    if result.decision == SuitabilityDecision.BLOCK:
        if result.status != SuitabilityResultStatus.BLOCKED:
            return False

    return True


# ============================================================
# CONTRACT VALIDATION
# ============================================================

def validate_suitability_contract(
    contract: Optional[SuitabilityContract],
) -> bool:

    if not isinstance(contract, SuitabilityContract):
        return False

    if not contract.contract_id:
        return False

    if not contract.request_id:
        return False

    if contract.request.request_id != contract.request_id:
        return False

    if not isinstance(
        contract.validation,
        SuitabilityContractValidation,
    ):
        return False

    if not isinstance(
        contract.requirements,
        SuitabilityRequirements,
    ):
        return False

    if not isinstance(
        contract.assessment,
        SuitabilityAssessment,
    ):
        return False

    if not validate_suitability_result(contract.result):
        return False

    if not isinstance(
        contract.action,
        SuitabilityAction,
    ):
        return False

    if contract.action.request_id != contract.request_id:
        return False

    return True


# ============================================================
# STRICT READINESS
# ============================================================

def suitability_ready(
    contract: Optional[SuitabilityContract],
) -> bool:

    if not validate_suitability_contract(contract):
        return False

    if contract.state != SuitabilityContractState.COMPLETE:
        return False

    if contract.result.status != SuitabilityResultStatus.ALLOWED:
        return False

    if contract.result.decision != SuitabilityDecision.ALLOW:
        return False

    if contract.result.readiness != SuitabilityReadiness.READY:
        return False

    if contract.result.consistency != SuitabilityConsistency.CONSISTENT:
        return False

    return True


# ============================================================
# ADVANCEMENT CHECK
# ============================================================

def suitability_can_advance(
    contract: Optional[SuitabilityContract],
) -> bool:

    if not validate_suitability_contract(contract):
        return False

    if contract.state in {
        SuitabilityContractState.INVALID,
        SuitabilityContractState.BLOCKED,
    }:
        return False

    if contract.result.status in {
        SuitabilityResultStatus.BLOCKED,
        SuitabilityResultStatus.INVALID,
    }:
        return False

    # Conditional/restricted/review outcomes may continue only
    # as restricted CAS pipeline states. They are NOT execution
    # authorization.
    return True


# ============================================================
# ACCESSORS
# ============================================================

def get_suitability_decision(
    contract: Optional[SuitabilityContract],
) -> SuitabilityDecision:

    if not validate_suitability_contract(contract):
        return SuitabilityDecision.UNKNOWN

    return contract.result.decision


def get_suitability_status(
    contract: Optional[SuitabilityContract],
) -> SuitabilityStatus:

    if not validate_suitability_contract(contract):
        return SuitabilityStatus.INVALID

    return contract.result.suitability_status


def get_suitability_score(
    contract: Optional[SuitabilityContract],
) -> float:

    if not validate_suitability_contract(contract):
        return 0.0

    return contract.result.suitability_score


def get_suitability_confidence(
    contract: Optional[SuitabilityContract],
) -> float:

    if not validate_suitability_contract(contract):
        return 0.0

    return contract.result.confidence_score


def get_suitability_restrictions(
    contract: Optional[SuitabilityContract],
) -> tuple[str, ...]:

    if not validate_suitability_contract(contract):
        return ("INVALID_CONTRACT",)

    return contract.result.restrictions


# ============================================================
# SAFETY HELPERS
# ============================================================

def suitability_requires_review(
    contract: Optional[SuitabilityContract],
) -> bool:

    if not validate_suitability_contract(contract):
        return True

    return (
        contract.result.status
        == SuitabilityResultStatus.REVIEW
    )


def suitability_is_blocked(
    contract: Optional[SuitabilityContract],
) -> bool:

    if not validate_suitability_contract(contract):
        return True

    return (
        contract.result.status
        == SuitabilityResultStatus.BLOCKED
    )


def suitability_is_restricted(
    contract: Optional[SuitabilityContract],
) -> bool:

    if not validate_suitability_contract(contract):
        return True

    return (
        contract.result.status
        == SuitabilityResultStatus.RESTRICTED
    )


def suitability_is_safe_for_next_gate(
    contract: Optional[SuitabilityContract],
) -> bool:

    if not validate_suitability_contract(contract):
        return False

    if suitability_is_blocked(contract):
        return False

    if contract.result.status == SuitabilityResultStatus.INVALID:
        return False

    return True


# ============================================================
# AUTHORITY BOUNDARIES
# ============================================================

def suitability_generates_decision() -> bool:
    return False


def suitability_modifies_d13() -> bool:
    return False


def suitability_overrides_d13() -> bool:
    return False


def suitability_overrides_risk() -> bool:
    return False


def suitability_overrides_cas() -> bool:
    return False


def suitability_authorizes_execution() -> bool:
    return False


def suitability_allows_order_placement() -> bool:
    return False


def suitability_changes_position() -> bool:
    return False


def suitability_has_execution_authority() -> bool:
    return False


def suitability_is_alpha_engine() -> bool:
    return False


# ============================================================
# ACTION SAFETY VALIDATION
# ============================================================

def validate_suitability_action(
    action: Optional[SuitabilityAction],
) -> bool:

    if not isinstance(action, SuitabilityAction):
        return False

    if not action.action_id:
        return False

    if not action.request_id:
        return False

    # Suitability action is an internal evaluation state.
    if action.is_action_request:
        return False

    if action.is_execution_request:
        return False

    if action.decision == SuitabilityDecision.ALLOW:
        if action.state != SuitabilityActionState.ALLOW:
            return False

    if action.decision == SuitabilityDecision.ALLOW_WITH_RESTRICTION:
        if action.state != SuitabilityActionState.RESTRICT:
            return False

    if action.decision == SuitabilityDecision.REVIEW_REQUIRED:
        if action.state != SuitabilityActionState.REVIEW:
            return False

    if action.decision == SuitabilityDecision.BLOCK:
        if action.state != SuitabilityActionState.BLOCK:
            return False

    return True


# ============================================================
# AUDIT RECORD
# ============================================================

@dataclass(frozen=True)
class SuitabilityAuditRecord:
    audit_id: str
    request_id: str
    contract_id: str

    decision: SuitabilityDecision
    result_status: SuitabilityResultStatus
    suitability_status: SuitabilityStatus

    suitability_score: float
    confidence_score: float

    restrictions: tuple[str, ...]
    reasons: tuple[str, ...]

    execution_authorized: bool
    decision_authority_modified: bool
    risk_authority_modified: bool

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


def build_suitability_audit(
    contract: Optional[SuitabilityContract],
) -> SuitabilityAuditRecord:

    if not validate_suitability_contract(contract):
        return SuitabilityAuditRecord(
            audit_id=str(uuid4()),
            request_id="",
            contract_id="",

            decision=SuitabilityDecision.UNKNOWN,
            result_status=SuitabilityResultStatus.INVALID,
            suitability_status=SuitabilityStatus.INVALID,

            suitability_score=0.0,
            confidence_score=0.0,

            restrictions=("INVALID_CONTRACT",),
            reasons=("Suitability contract validation failed.",),

            execution_authorized=False,
            decision_authority_modified=False,
            risk_authority_modified=False,
        )

    return SuitabilityAuditRecord(
        audit_id=str(uuid4()),
        request_id=contract.request_id,
        contract_id=contract.contract_id,

        decision=contract.result.decision,
        result_status=contract.result.status,
        suitability_status=contract.result.suitability_status,

        suitability_score=contract.result.suitability_score,
        confidence_score=contract.result.confidence_score,

        restrictions=contract.result.restrictions,
        reasons=contract.result.reasons,

        execution_authorized=False,
        decision_authority_modified=False,
        risk_authority_modified=False,
    )


# ============================================================
# ENGINE HEALTH
# ============================================================

@dataclass(frozen=True)
class SuitabilityEngineHealth:
    engine_name: str
    engine_version: str

    operational: bool
    contract_validation_available: bool
    evaluation_available: bool

    execution_authority: bool
    decision_authority: bool
    risk_authority: bool

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


def get_suitability_engine_health() -> SuitabilityEngineHealth:

    engine = get_suitability_gate_engine()

    return SuitabilityEngineHealth(
        engine_name=engine.engine_name,
        engine_version=engine.engine_version,

        operational=True,
        contract_validation_available=True,
        evaluation_available=True,

        execution_authority=False,
        decision_authority=False,
        risk_authority=False,
    )


# ============================================================
# ENGINE INFORMATION
# ============================================================

def get_suitability_engine_info() -> dict[str, Any]:

    engine = get_suitability_gate_engine()

    return {
        "engine": engine.engine_name,
        "version": engine.engine_version,
        "layer": "CAS",
        "role": "SUITABILITY_GATE",
        "authority": "CAS_INTERNAL_GATE",
        "decision_authority": False,
        "risk_authority": False,
        "execution_authority": False,
        "can_modify_d13": False,
        "can_override_d13": False,
        "can_override_risk": False,
        "can_override_cas": False,
        "can_place_order": False,
        "can_change_position": False,
        "is_alpha_engine": False,
    }


# ============================================================
# CONFLICT / INTEGRITY CHECK
# ============================================================

def suitability_has_authority_conflict(
    contract: Optional[SuitabilityContract],
) -> bool:

    if not validate_suitability_contract(contract):
        return True

    action = contract.action

    if not validate_suitability_action(action):
        return True

    if action.is_execution_request:
        return True

    if action.is_action_request:
        return True

    return False


def suitability_integrity_ok(
    contract: Optional[SuitabilityContract],
) -> bool:

    if not validate_suitability_contract(contract):
        return False

    if not validate_suitability_action(contract.action):
        return False

    if suitability_has_authority_conflict(contract):
        return False

    if contract.result.suitability_score < 0.0:
        return False

    if contract.result.suitability_score > 100.0:
        return False

    if contract.result.confidence_score < 0.0:
        return False

    if contract.result.confidence_score > 100.0:
        return False

    return True
# ============================================================
# ROBOMLM CAS — SUITABILITY GATE
# Part 5/5 — FINAL
#
# Lifecycle • Serialization • Summary • Freeze • Authority
# ============================================================


# ============================================================
# LIFECYCLE
# ============================================================

class SuitabilityLifecycleState(str, Enum):
    CREATED = "CREATED"
    VALIDATED = "VALIDATED"
    EVALUATED = "EVALUATED"
    REVIEW = "REVIEW"
    RESTRICTED = "RESTRICTED"
    ALLOWED = "ALLOWED"
    BLOCKED = "BLOCKED"
    FROZEN = "FROZEN"
    RETAINED = "RETAINED"
    REJECTED = "REJECTED"
    INVALID = "INVALID"


def determine_suitability_lifecycle(
    contract: Optional[SuitabilityContract],
) -> SuitabilityLifecycleState:

    if not validate_suitability_contract(contract):
        return SuitabilityLifecycleState.INVALID

    status = contract.result.status

    if status == SuitabilityResultStatus.BLOCKED:
        return SuitabilityLifecycleState.BLOCKED

    if status == SuitabilityResultStatus.REVIEW:
        return SuitabilityLifecycleState.REVIEW

    if status == SuitabilityResultStatus.RESTRICTED:
        return SuitabilityLifecycleState.RESTRICTED

    if status == SuitabilityResultStatus.ALLOWED:
        return SuitabilityLifecycleState.ALLOWED

    return SuitabilityLifecycleState.INVALID


# ============================================================
# FREEZE / RETAIN / REJECT
# ============================================================

def freeze_suitability(
    contract: Optional[SuitabilityContract],
) -> Optional[SuitabilityContract]:

    if not validate_suitability_contract(contract):
        return None

    return SuitabilityContract(
        contract_id=contract.contract_id,
        request_id=contract.request_id,

        state=SuitabilityContractState.COMPLETE,

        request=contract.request,
        validation=contract.validation,
        requirements=contract.requirements,
        assessment=contract.assessment,
        result=contract.result,
        action=contract.action,

        created_at=contract.created_at,
    )


def retain_suitability(
    contract: Optional[SuitabilityContract],
) -> bool:

    if not validate_suitability_contract(contract):
        return False

    if not suitability_integrity_ok(contract):
        return False

    return True


def reject_suitability(
    contract: Optional[SuitabilityContract],
) -> bool:

    if not validate_suitability_contract(contract):
        return True

    return (
        contract.result.status
        in {
            SuitabilityResultStatus.BLOCKED,
            SuitabilityResultStatus.INVALID,
        }
    )


# ============================================================
# SERIALIZATION HELPERS
# ============================================================

def suitability_result_to_dict(
    result: Optional[SuitabilityResult],
) -> dict[str, Any]:

    if not isinstance(result, SuitabilityResult):
        return {
            "valid": False,
            "status": SuitabilityResultStatus.INVALID.value,
        }

    return {
        "result_id": result.result_id,
        "request_id": result.request_id,

        "status": result.status.value,
        "decision": result.decision.value,

        "suitability_status": result.suitability_status.value,
        "readiness": result.readiness.value,

        "suitability_score": result.suitability_score,
        "confidence_score": result.confidence_score,
        "completeness_score": result.completeness_score,

        "data_state": result.data_state.value,
        "consistency": result.consistency.value,

        "restrictions": list(result.restrictions),
        "reasons": list(result.reasons),
        "strengths": list(result.strengths),
        "weaknesses": list(result.weaknesses),

        "rationale": result.rationale,
        "timestamp": result.timestamp.isoformat(),

        "valid": validate_suitability_result(result),
    }


def suitability_contract_to_dict(
    contract: Optional[SuitabilityContract],
) -> dict[str, Any]:

    if not isinstance(contract, SuitabilityContract):
        return {
            "valid": False,
            "state": SuitabilityContractState.INVALID.value,
        }

    request = contract.request

    return {
        "contract_id": contract.contract_id,
        "request_id": contract.request_id,

        "state": contract.state.value,
        "lifecycle": determine_suitability_lifecycle(
            contract
        ).value,

        "request": {
            "market": request.market,
            "instrument": request.instrument,
            "contract": request.contract,

            "user_id": request.user_id,
            "account_id": request.account_id,
            "plan_id": request.plan_id,

            "permission": request.permission,
            "role": request.role,

            "action": request.action,
            "direction": request.direction,

            "mode": request.mode.value,
            "strategy": request.strategy,
            "timeframe": request.timeframe,

            "priority": request.priority.value,
            "metadata": dict(request.metadata),
            "request_id": request.request_id,
        },

        "validation": {
            "valid": contract.validation.valid,
            "errors": list(contract.validation.errors),
            "warnings": list(contract.validation.warnings),
        },

        "requirements": {
            "request_valid": contract.requirements.request_valid,
            "data_state": contract.requirements.data_state.value,
            "consistency": contract.requirements.consistency.value,
            "readiness": contract.requirements.readiness.value,
            "completeness_score": (
                contract.requirements.completeness_score
            ),
            "warnings": list(contract.requirements.warnings),
        },

        "assessment": {
            "readiness": contract.assessment.readiness.value,
            "data_state": contract.assessment.data_state.value,
            "consistency": contract.assessment.consistency.value,
            "suitability_score": (
                contract.assessment.suitability_score
            ),
            "confidence_score": (
                contract.assessment.confidence_score
            ),
            "completeness_score": (
                contract.assessment.completeness_score
            ),
            "strengths": list(contract.assessment.strengths),
            "weaknesses": list(contract.assessment.weaknesses),
            "restrictions": list(contract.assessment.restrictions),
            "rationale": contract.assessment.rationale,
        },

        "result": suitability_result_to_dict(
            contract.result
        ),

        "action": {
            "action_id": contract.action.action_id,
            "request_id": contract.action.request_id,
            "state": contract.action.state.value,
            "decision": contract.action.decision.value,
            "is_action_request": (
                contract.action.is_action_request
            ),
            "is_execution_request": (
                contract.action.is_execution_request
            ),
            "restrictions": list(contract.action.restrictions),
            "reasons": list(contract.action.reasons),
            "timestamp": contract.action.timestamp.isoformat(),
        },

        "created_at": contract.created_at.isoformat(),

        "valid": validate_suitability_contract(contract),
        "integrity_ok": suitability_integrity_ok(contract),
    }


# ============================================================
# SUMMARY
# ============================================================

def summarize_suitability(
    contract: Optional[SuitabilityContract],
) -> dict[str, Any]:

    if not validate_suitability_contract(contract):
        return {
            "valid": False,
            "status": SuitabilityStatus.INVALID.value,
            "decision": SuitabilityDecision.BLOCK.value,
            "lifecycle": SuitabilityLifecycleState.INVALID.value,
            "execution_authorized": False,
        }

    result = contract.result

    return {
        "valid": True,

        "contract_id": contract.contract_id,
        "request_id": contract.request_id,

        "market": contract.request.market,
        "instrument": contract.request.instrument,

        "status": result.status.value,
        "decision": result.decision.value,
        "suitability_status": (
            result.suitability_status.value
        ),

        "readiness": result.readiness.value,
        "data_state": result.data_state.value,
        "consistency": result.consistency.value,

        "suitability_score": result.suitability_score,
        "confidence_score": result.confidence_score,
        "completeness_score": result.completeness_score,

        "restrictions": list(result.restrictions),

        "lifecycle": determine_suitability_lifecycle(
            contract
        ).value,

        # Suitability alone NEVER authorizes execution.
        "execution_authorized": False,

        "can_advance": suitability_can_advance(contract),
        "ready": suitability_ready(contract),
        "requires_review": suitability_requires_review(
            contract
        ),
        "blocked": suitability_is_blocked(contract),
        "integrity_ok": suitability_integrity_ok(contract),
    }


# ============================================================
# AUTHORITY STATEMENT
# ============================================================

def get_suitability_authority_statement() -> dict[str, Any]:

    return {
        "engine": SUITABILITY_GATE_ENGINE,
        "version": SUITABILITY_GATE_VERSION,

        "role": (
            "CAS suitability validation and authorization-context "
            "gate"
        ),

        "may_evaluate_suitability": True,

        "may_generate_market_decision": False,
        "may_generate_d13_decision": False,
        "may_modify_d13": False,
        "may_override_d13": False,

        "may_override_risk": False,
        "may_override_cas": False,

        "may_authorize_execution": False,
        "may_place_order": False,
        "may_modify_order": False,
        "may_change_position": False,

        "may_determine_winning_probability": False,
        "may_generate_alpha": False,

        "execution_authority": False,
        "decision_authority": False,
        "risk_authority": False,
    }


# ============================================================
# FINAL ENGINE STATUS
# ============================================================

def suitability_engine_operational() -> bool:
    health = get_suitability_engine_health()

    return (
        health.operational
        and health.contract_validation_available
        and health.evaluation_available
        and not health.execution_authority
        and not health.decision_authority
        and not health.risk_authority
    )


# ============================================================
# PUBLIC VALIDATION ENTRYPOINT
# ============================================================

def validate_suitability(
    request: Optional[SuitabilityRequest] = None,
    contract: Optional[SuitabilityContract] = None,
    source: Any = None,
    **kwargs: Any,
) -> bool:

    if contract is not None:
        return (
            validate_suitability_contract(contract)
            and suitability_integrity_ok(contract)
        )

    if request is None:
        request = build_suitability_request(
            source,
            **kwargs,
        )

    validation = validate_suitability_request(request)

    return validation.valid


# ============================================================
# FINAL EVALUATION SNAPSHOT
# ============================================================

def suitability_snapshot(
    contract: Optional[SuitabilityContract],
) -> dict[str, Any]:

    if not validate_suitability_contract(contract):
        return {
            "valid": False,
            "decision": SuitabilityDecision.BLOCK.value,
            "status": SuitabilityResultStatus.INVALID.value,
        }

    return {
        "valid": True,

        "engine": SUITABILITY_GATE_ENGINE,
        "version": SUITABILITY_GATE_VERSION,

        "contract_id": contract.contract_id,
        "request_id": contract.request_id,

        "decision": contract.result.decision.value,
        "status": contract.result.status.value,
        "suitability_status": (
            contract.result.suitability_status.value
        ),

        "score": contract.result.suitability_score,
        "confidence": contract.result.confidence_score,
        "completeness": contract.result.completeness_score,

        "readiness": contract.result.readiness.value,
        "consistency": contract.result.consistency.value,

        "restrictions": list(
            contract.result.restrictions
        ),

        "can_advance": suitability_can_advance(
            contract
        ),

        "execution_authorized": False,
        "d13_modified": False,
        "risk_overridden": False,
        "cas_overridden": False,

        "integrity_ok": suitability_integrity_ok(
            contract
        ),
    }


# ============================================================
# MODULE EXPORTS
# ============================================================

__all__ = [
    # Constants
    "SUITABILITY_GATE_ENGINE",
    "SUITABILITY_GATE_VERSION",

    # Enums
    "SuitabilityStatus",
    "SuitabilityDecision",
    "SuitabilityMode",
    "SuitabilityPriority",
    "SuitabilityContractStatus",

    "SuitabilityDataState",
    "SuitabilityConsistency",
    "SuitabilityReadiness",

    "SuitabilityActionState",
    "SuitabilityContractState",
    "SuitabilityResultStatus",
    "SuitabilityLifecycleState",

    # Contracts
    "SuitabilityRequest",
    "SuitabilityReference",
    "SuitabilityContractValidation",
    "SuitabilityRequirements",
    "SuitabilityAssessment",
    "SuitabilityAction",
    "SuitabilityResult",
    "SuitabilityContract",
    "SuitabilityAuditRecord",
    "SuitabilityEngineHealth",

    # Builders
    "build_suitability_request",
    "build_suitability_assessment",
    "build_suitability_action",
    "build_suitability_result",
    "build_suitability_contract",
    "build_suitability_audit",

    # Evaluation
    "evaluate_suitability_data_state",
    "evaluate_suitability_consistency",
    "calculate_suitability_completeness",
    "evaluate_suitability_readiness",
    "evaluate_suitability_requirements",
    "calculate_suitability_score",
    "calculate_suitability_confidence",
    "extract_suitability_restrictions",
    "determine_suitability_decision",
    "determine_suitability_result_status",
    "determine_suitability_status",
    "determine_suitability_action_state",
    "determine_suitability_contract_state",
    "determine_suitability_lifecycle",

    # Public API
    "SuitabilityGateEngine",
    "get_suitability_gate_engine",
    "evaluate_suitability",
    "check_suitability",
    "review_suitability",
    "validate_suitability",

    # Validation
    "validate_suitability_request",
    "validate_suitability_result",
    "validate_suitability_contract",
    "validate_suitability_action",

    # Readiness / safety
    "suitability_ready",
    "suitability_can_advance",
    "suitability_requires_review",
    "suitability_is_blocked",
    "suitability_is_restricted",
    "suitability_is_safe_for_next_gate",
    "suitability_integrity_ok",
    "suitability_has_authority_conflict",

    # Accessors
    "get_suitability_decision",
    "get_suitability_status",
    "get_suitability_score",
    "get_suitability_confidence",
    "get_suitability_restrictions",

    # Authority
    "suitability_generates_decision",
    "suitability_modifies_d13",
    "suitability_overrides_d13",
    "suitability_overrides_risk",
    "suitability_overrides_cas",
    "suitability_authorizes_execution",
    "suitability_allows_order_placement",
    "suitability_changes_position",
    "suitability_has_execution_authority",
    "suitability_is_alpha_engine",
    "get_suitability_authority_statement",

    # Audit / health
    "get_suitability_engine_health",
    "get_suitability_engine_info",
    "suitability_engine_operational",

    # Lifecycle
    "freeze_suitability",
    "retain_suitability",
    "reject_suitability",

    # Serialization / summary
    "suitability_result_to_dict",
    "suitability_contract_to_dict",
    "summarize_suitability",
    "suitability_snapshot",
]