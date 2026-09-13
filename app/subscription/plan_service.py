# ============================================================
# ROBOMLM SUBSCRIPTION
# plan_service.py — PART 1
# Plan Domain Foundation / Contracts / Validation
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Optional, Tuple


# ============================================================
# ENGINE / SERVICE IDENTITY
# ============================================================

PLAN_SERVICE_ENGINE = "ROBOMLM_PLAN_SERVICE"
PLAN_SERVICE_VERSION = "1.0"


# ============================================================
# PLAN STATES
# ============================================================

class PlanStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    RETIRED = "RETIRED"


class PlanType(str, Enum):
    FREE = "FREE"
    PRO = "PRO"
    ELITE = "ELITE"
    AUTO = "AUTO"
    CUSTOM = "CUSTOM"


class PlanPriority(str, Enum):
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class PlanMode(str, Enum):
    PAPER = "PAPER"
    DEMO = "DEMO"
    LIVE = "LIVE"
    UNKNOWN = "UNKNOWN"


class PlanContractStatus(str, Enum):
    CREATED = "CREATED"
    VALID = "VALID"
    INVALID = "INVALID"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    RETIRED = "RETIRED"


# ============================================================
# PATH / CAPABILITY CATEGORIES
# ============================================================

class PlanCapability(str, Enum):
    TERMINAL = "TERMINAL"
    DISCOVERY = "DISCOVERY"
    MEMORY = "MEMORY"
    RESEARCH = "RESEARCH"
    AUTOMATION = "AUTOMATION"
    CHAT = "CHAT"
    QUICK_ANALYSIS = "QUICK_ANALYSIS"
    DEEP_ANALYSIS = "DEEP_ANALYSIS"


# ============================================================
# HELPERS
# ============================================================

def _plan_text(
    value: Any,
    default: str = "",
) -> str:

    if value is None:
        return default

    try:
        text = str(value).strip()
    except Exception:
        return default

    return text if text else default


def _plan_enum(
    enum_type: type[Enum],
    value: Any,
    default: Enum,
) -> Enum:

    if isinstance(
        value,
        enum_type,
    ):
        return value

    if value is None:
        return default

    raw = getattr(
        value,
        "value",
        value,
    )

    try:
        return enum_type(
            str(raw).strip().upper()
        )
    except (ValueError, TypeError):
        return default


def _plan_bool(
    value: Any,
    default: bool = False,
) -> bool:

    if value is None:
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, str):

        value = value.strip().lower()

        if value in {
            "true",
            "1",
            "yes",
            "y",
            "on",
        }:
            return True

        if value in {
            "false",
            "0",
            "no",
            "n",
            "off",
        }:
            return False

    return bool(value)


def _plan_number(
    value: Any,
    default: Optional[float] = None,
) -> Optional[float]:

    if value is None:
        return default

    try:
        return float(value)
    except (
        TypeError,
        ValueError,
    ):
        return default


def _plan_timestamp(
    value: Any = None,
) -> datetime:

    if isinstance(
        value,
        datetime,
    ):
        return value

    return datetime.now(
        timezone.utc
    )


# ============================================================
# PLAN REQUEST
# ============================================================

@dataclass(frozen=True)
class PlanRequest:
    """
    Request for retrieving or evaluating a subscription plan.

    This contract describes plan identity and requested
    commercial capability context.

    It does not grant entitlement by itself.
    """

    plan_id: Optional[str] = None
    plan_type: PlanType = PlanType.CUSTOM
    name: str = ""

    status: PlanStatus = PlanStatus.ACTIVE

    description: str = ""

    mode: PlanMode = PlanMode.UNKNOWN
    priority: PlanPriority = PlanPriority.NORMAL

    currency: str = "USD"

    monthly_price: Optional[float] = None
    yearly_price: Optional[float] = None

    capabilities: Tuple[
        str,
        ...
    ] = ()

    metadata: Mapping[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    request_id: Optional[str] = None

    timestamp: datetime = field(
        default_factory=_plan_timestamp
    )


# ============================================================
# PLAN REFERENCE
# ============================================================

@dataclass(frozen=True)
class PlanReference:
    """
    Stable reference to a subscription plan.

    Reference identity does not itself authorize access.
    """

    plan_id: str
    plan_type: PlanType

    name: str = ""

    version: str = PLAN_SERVICE_VERSION

    status: PlanStatus = PlanStatus.ACTIVE

    created_at: datetime = field(
        default_factory=_plan_timestamp
    )


# ============================================================
# PLAN CONTRACT VALIDATION
# ============================================================

@dataclass(frozen=True)
class PlanContractValidation:
    """
    Result of structural plan-contract validation.
    """

    valid: bool

    errors: Tuple[
        str,
        ...
    ] = ()

    warnings: Tuple[
        str,
        ...
    ] = ()

    checked_at: datetime = field(
        default_factory=_plan_timestamp
    )


# ============================================================
# PLAN NUMERIC VALIDATION
# ============================================================

def validate_plan_numeric_inputs(
    request: PlanRequest,
) -> Tuple[
    str,
    ...
]:

    errors = []

    if (
        request.monthly_price is not None
        and request.monthly_price < 0
    ):
        errors.append(
            "monthly_price cannot be negative."
        )

    if (
        request.yearly_price is not None
        and request.yearly_price < 0
    ):
        errors.append(
            "yearly_price cannot be negative."
        )

    return tuple(errors)


# ============================================================
# PLAN REQUEST VALIDATION
# ============================================================

def validate_plan_request(
    request: PlanRequest,
) -> PlanContractValidation:

    errors = []
    warnings = []

    if not isinstance(
        request,
        PlanRequest,
    ):
        return PlanContractValidation(
            valid=False,
            errors=(
                "request must be PlanRequest.",
            ),
        )

    if not _plan_text(
        request.name
    ):
        errors.append(
            "Plan name is required."
        )

    if (
        request.plan_type
        == PlanType.CUSTOM
        and not _plan_text(
            request.plan_id
        )
    ):
        warnings.append(
            "Custom plan has no plan_id."
        )

    errors.extend(
        validate_plan_numeric_inputs(
            request
        )
    )

    if not _plan_text(
        request.currency
    ):
        errors.append(
            "Currency is required."
        )

    for capability in request.capabilities:

        if not _plan_text(
            capability
        ):
            errors.append(
                "Plan capability cannot be empty."
            )

    if (
        request.status
        == PlanStatus.ACTIVE
        and not request.capabilities
    ):
        warnings.append(
            "Active plan has no declared capabilities."
        )

    return PlanContractValidation(
        valid=not errors,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


# ============================================================
# PLAN REQUEST BUILDER
# ============================================================

def build_plan_request(
    *,
    plan_id: Optional[str] = None,
    plan_type: Any = PlanType.CUSTOM,
    name: str = "",
    status: Any = PlanStatus.ACTIVE,
    description: str = "",
    mode: Any = PlanMode.UNKNOWN,
    priority: Any = PlanPriority.NORMAL,
    currency: str = "USD",
    monthly_price: Optional[float] = None,
    yearly_price: Optional[float] = None,
    capabilities: Optional[
        Tuple[str, ...]
    ] = None,
    metadata: Optional[
        Mapping[str, Any]
    ] = None,
    request_id: Optional[str] = None,
    timestamp: Any = None,
) -> PlanRequest:

    return PlanRequest(
        plan_id=_plan_text(
            plan_id,
            default="",
        ) or None,

        plan_type=_plan_enum(
            PlanType,
            plan_type,
            PlanType.CUSTOM,
        ),

        name=_plan_text(name),

        status=_plan_enum(
            PlanStatus,
            status,
            PlanStatus.ACTIVE,
        ),

        description=_plan_text(
            description
        ),

        mode=_plan_enum(
            PlanMode,
            mode,
            PlanMode.UNKNOWN,
        ),

        priority=_plan_enum(
            PlanPriority,
            priority,
            PlanPriority.NORMAL,
        ),

        currency=_plan_text(
            currency,
            default="USD",
        ).upper(),

        monthly_price=_plan_number(
            monthly_price
        ),

        yearly_price=_plan_number(
            yearly_price
        ),

        capabilities=tuple(
            _plan_text(x)
            for x in (
                capabilities
                or ()
            )
            if _plan_text(x)
        ),

        metadata=dict(
            metadata or {}
        ),

        request_id=_plan_text(
            request_id,
            default="",
        ) or None,

        timestamp=_plan_timestamp(
            timestamp
        ),
    )


# ============================================================
# PLAN REFERENCE BUILDER
# ============================================================

def build_plan_reference(
    *,
    plan_id: str,
    plan_type: Any,
    name: str = "",
    version: str = PLAN_SERVICE_VERSION,
    status: Any = PlanStatus.ACTIVE,
) -> PlanReference:

    return PlanReference(
        plan_id=_plan_text(
            plan_id
        ),

        plan_type=_plan_enum(
            PlanType,
            plan_type,
            PlanType.CUSTOM,
        ),

        name=_plan_text(
            name
        ),

        version=_plan_text(
            version,
            default=PLAN_SERVICE_VERSION,
        ),

        status=_plan_enum(
            PlanStatus,
            status,
            PlanStatus.ACTIVE,
        ),
    )


# ============================================================
# PLAN REFERENCE VALIDATION
# ============================================================

def validate_plan_reference(
    reference: PlanReference,
) -> bool:

    if not isinstance(
        reference,
        PlanReference,
    ):
        return False

    if not _plan_text(
        reference.plan_id
    ):
        return False

    if not _plan_text(
        reference.name
    ):
        return False

    if not _plan_text(
        reference.version
    ):
        return False

    return True
# ============================================================
# ROBOMLM SUBSCRIPTION
# plan_service.py — PART 2
# Plan Evaluation / Pricing / Capability / Lifecycle
# ============================================================


# ============================================================
# PLAN DATA STATE
# ============================================================

class PlanDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    INVALID = "INVALID"


class PlanConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONDITIONAL = "CONDITIONAL"
    INCONSISTENT = "INCONSISTENT"
    UNKNOWN = "UNKNOWN"


class PlanReadiness(str, Enum):
    READY = "READY"
    CONDITIONALLY_READY = "CONDITIONALLY_READY"
    NOT_READY = "NOT_READY"
    BLOCKED = "BLOCKED"


# ============================================================
# PLAN REQUIREMENTS
# ============================================================

@dataclass(frozen=True)
class PlanRequirements:
    require_name: bool = True
    require_plan_type: bool = True
    require_status: bool = True
    require_currency: bool = True

    require_plan_id: bool = False

    require_price: bool = False
    require_capabilities: bool = False

    allow_free_without_price: bool = True
    allow_custom_without_id: bool = False
    allow_inactive_plan: bool = False
    allow_retired_plan: bool = False


def build_plan_requirements(
    *,
    require_name: bool = True,
    require_plan_type: bool = True,
    require_status: bool = True,
    require_currency: bool = True,
    require_plan_id: bool = False,
    require_price: bool = False,
    require_capabilities: bool = False,
    allow_free_without_price: bool = True,
    allow_custom_without_id: bool = False,
    allow_inactive_plan: bool = False,
    allow_retired_plan: bool = False,
) -> PlanRequirements:

    return PlanRequirements(
        require_name=require_name,
        require_plan_type=require_plan_type,
        require_status=require_status,
        require_currency=require_currency,
        require_plan_id=require_plan_id,
        require_price=require_price,
        require_capabilities=require_capabilities,
        allow_free_without_price=
            allow_free_without_price,
        allow_custom_without_id=
            allow_custom_without_id,
        allow_inactive_plan=
            allow_inactive_plan,
        allow_retired_plan=
            allow_retired_plan,
    )


# ============================================================
# PLAN ASSESSMENT
# ============================================================

@dataclass(frozen=True)
class PlanAssessment:
    data_state: PlanDataState
    consistency: PlanConsistency
    readiness: PlanReadiness

    completeness: float
    plan_quality: float
    confidence: float

    flags: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    unmet_requirements: Tuple[str, ...] = ()

    active: bool = False
    purchasable: bool = False

    capabilities: Tuple[str, ...] = ()

    monthly_price: Optional[float] = None
    yearly_price: Optional[float] = None

    notes: Tuple[str, ...] = ()


# ============================================================
# PLAN DATA STATE
# ============================================================

def evaluate_plan_data_state(
    request: PlanRequest,
    requirements: PlanRequirements,
) -> PlanDataState:

    if not isinstance(
        request,
        PlanRequest,
    ):
        return PlanDataState.INVALID

    if (
        requirements.require_name
        and not _plan_text(
            request.name
        )
    ):
        return PlanDataState.MISSING

    if (
        requirements.require_currency
        and not _plan_text(
            request.currency
        )
    ):
        return PlanDataState.MISSING

    numeric_errors = (
        validate_plan_numeric_inputs(
            request
        )
    )

    if numeric_errors:
        return PlanDataState.INVALID

    missing = []

    if (
        requirements.require_plan_id
        and not _plan_text(
            request.plan_id
        )
    ):
        missing.append(
            "plan_id"
        )

    if (
        requirements.require_price
        and request.plan_type != PlanType.FREE
        and request.monthly_price is None
        and request.yearly_price is None
    ):
        missing.append(
            "price"
        )

    if (
        requirements.require_capabilities
        and not request.capabilities
    ):
        missing.append(
            "capabilities"
        )

    if missing:
        return PlanDataState.PARTIAL

    return PlanDataState.COMPLETE


# ============================================================
# PLAN CONSISTENCY
# ============================================================

def evaluate_plan_consistency(
    request: PlanRequest,
    requirements: PlanRequirements,
) -> PlanConsistency:

    if not isinstance(
        request,
        PlanRequest,
    ):
        return PlanConsistency.INCONSISTENT

    numeric_errors = (
        validate_plan_numeric_inputs(
            request
        )
    )

    if numeric_errors:
        return PlanConsistency.INCONSISTENT

    if (
        request.plan_type
        == PlanType.CUSTOM
        and not request.plan_id
        and not requirements.allow_custom_without_id
    ):
        return PlanConsistency.CONDITIONAL

    if (
        request.plan_type
        == PlanType.FREE
        and request.monthly_price is not None
        and request.monthly_price > 0
    ):
        return PlanConsistency.INCONSISTENT

    if (
        request.plan_type
        == PlanType.FREE
        and request.yearly_price is not None
        and request.yearly_price > 0
    ):
        return PlanConsistency.INCONSISTENT

    if (
        request.status
        == PlanStatus.RETIRED
        and not requirements.allow_retired_plan
    ):
        return PlanConsistency.CONDITIONAL

    return PlanConsistency.CONSISTENT


# ============================================================
# PLAN COMPLETENESS
# ============================================================

def calculate_plan_completeness(
    request: PlanRequest,
    requirements: PlanRequirements,
) -> float:

    checks = []

    if requirements.require_name:
        checks.append(
            bool(
                _plan_text(
                    request.name
                )
            )
        )

    if requirements.require_plan_type:
        checks.append(
            isinstance(
                request.plan_type,
                PlanType,
            )
        )

    if requirements.require_status:
        checks.append(
            isinstance(
                request.status,
                PlanStatus,
            )
        )

    if requirements.require_currency:
        checks.append(
            bool(
                _plan_text(
                    request.currency
                )
            )
        )

    if requirements.require_plan_id:
        checks.append(
            bool(
                _plan_text(
                    request.plan_id
                )
            )
        )

    if requirements.require_price:
        checks.append(
            request.plan_type == PlanType.FREE
            or request.monthly_price is not None
            or request.yearly_price is not None
        )

    if requirements.require_capabilities:
        checks.append(
            bool(
                request.capabilities
            )
        )

    if not checks:
        return 100.0

    return round(
        100.0
        * sum(
            1 for value in checks
            if value
        )
        / len(checks),
        2,
    )


# ============================================================
# PLAN REQUIREMENT EVALUATION
# ============================================================

def evaluate_plan_requirements(
    request: PlanRequest,
    requirements: PlanRequirements,
) -> Tuple[str, ...]:

    unmet = []

    if (
        requirements.require_name
        and not _plan_text(
            request.name
        )
    ):
        unmet.append(
            "NAME_REQUIRED"
        )

    if (
        requirements.require_plan_id
        and not _plan_text(
            request.plan_id
        )
    ):
        unmet.append(
            "PLAN_ID_REQUIRED"
        )

    if (
        requirements.require_currency
        and not _plan_text(
            request.currency
        )
    ):
        unmet.append(
            "CURRENCY_REQUIRED"
        )

    if (
        requirements.require_price
        and request.plan_type != PlanType.FREE
        and request.monthly_price is None
        and request.yearly_price is None
    ):
        unmet.append(
            "PRICE_REQUIRED"
        )

    if (
        requirements.require_capabilities
        and not request.capabilities
    ):
        unmet.append(
            "CAPABILITIES_REQUIRED"
        )

    return tuple(unmet)


# ============================================================
# PLAN FLAGS
# ============================================================

def extract_plan_flags(
    request: PlanRequest,
    requirements: PlanRequirements,
) -> Tuple[str, ...]:

    flags = []

    if request.status == PlanStatus.INACTIVE:
        flags.append(
            "PLAN_INACTIVE"
        )

    if request.status == PlanStatus.RETIRED:
        flags.append(
            "PLAN_RETIRED"
        )

    if (
        request.plan_type == PlanType.CUSTOM
        and not request.plan_id
    ):
        flags.append(
            "CUSTOM_PLAN_ID_MISSING"
        )

    if (
        request.plan_type == PlanType.FREE
        and (
            (
                request.monthly_price
                is not None
                and request.monthly_price > 0
            )
            or
            (
                request.yearly_price
                is not None
                and request.yearly_price > 0
            )
        )
    ):
        flags.append(
            "FREE_PLAN_PRICE_CONFLICT"
        )

    return tuple(flags)


# ============================================================
# PLAN READINESS
# ============================================================

def evaluate_plan_readiness(
    request: PlanRequest,
    requirements: PlanRequirements,
    data_state: PlanDataState,
    consistency: PlanConsistency,
    unmet: Tuple[str, ...],
) -> PlanReadiness:

    if data_state == PlanDataState.INVALID:
        return PlanReadiness.BLOCKED

    if consistency == PlanConsistency.INCONSISTENT:
        return PlanReadiness.BLOCKED

    if request.status == PlanStatus.RETIRED:
        if not requirements.allow_retired_plan:
            return PlanReadiness.BLOCKED

    if request.status == PlanStatus.INACTIVE:
        if not requirements.allow_inactive_plan:
            return PlanReadiness.NOT_READY

    if unmet:
        return PlanReadiness.NOT_READY

    if consistency == PlanConsistency.CONDITIONAL:
        return PlanReadiness.CONDITIONALLY_READY

    if data_state == PlanDataState.PARTIAL:
        return PlanReadiness.CONDITIONALLY_READY

    return PlanReadiness.READY


# ============================================================
# PLAN QUALITY
# ============================================================

def calculate_plan_quality(
    completeness: float,
    consistency: PlanConsistency,
    readiness: PlanReadiness,
) -> float:

    score = completeness

    if consistency == PlanConsistency.CONSISTENT:
        score += 10.0

    elif consistency == PlanConsistency.CONDITIONAL:
        score += 5.0

    if readiness == PlanReadiness.READY:
        score += 10.0

    elif readiness == PlanReadiness.CONDITIONALLY_READY:
        score += 5.0

    elif readiness == PlanReadiness.NOT_READY:
        score -= 10.0

    elif readiness == PlanReadiness.BLOCKED:
        score -= 30.0

    return round(
        max(
            0.0,
            min(
                100.0,
                score,
            ),
        ),
        2,
    )


# ============================================================
# PLAN CONFIDENCE
# ============================================================

def calculate_plan_confidence(
    completeness: float,
    consistency: PlanConsistency,
    readiness: PlanReadiness,
) -> float:

    confidence = completeness

    if consistency == PlanConsistency.INCONSISTENT:
        confidence -= 35.0

    elif consistency == PlanConsistency.CONDITIONAL:
        confidence -= 15.0

    if readiness == PlanReadiness.BLOCKED:
        confidence -= 30.0

    elif readiness == PlanReadiness.NOT_READY:
        confidence -= 15.0

    return round(
        max(
            0.0,
            min(
                100.0,
                confidence,
            ),
        ),
        2,
    )


# ============================================================
# PURCHASABILITY
# ============================================================

def plan_is_purchasable(
    request: PlanRequest,
    requirements: PlanRequirements,
    readiness: PlanReadiness,
) -> bool:

    if readiness != PlanReadiness.READY:
        return False

    if request.status != PlanStatus.ACTIVE:
        return False

    if (
        request.plan_type != PlanType.FREE
        and request.monthly_price is None
        and request.yearly_price is None
        and requirements.require_price
    ):
        return False

    return True


# ============================================================
# ASSESSMENT BUILDER
# ============================================================

def build_plan_assessment(
    request: PlanRequest,
    requirements: Optional[
        PlanRequirements
    ] = None,
) -> PlanAssessment:

    requirements = (
        requirements
        or build_plan_requirements()
    )

    data_state = (
        evaluate_plan_data_state(
            request,
            requirements,
        )
    )

    consistency = (
        evaluate_plan_consistency(
            request,
            requirements,
        )
    )

    completeness = (
        calculate_plan_completeness(
            request,
            requirements,
        )
    )

    unmet = (
        evaluate_plan_requirements(
            request,
            requirements,
        )
    )

    readiness = (
        evaluate_plan_readiness(
            request,
            requirements,
            data_state,
            consistency,
            unmet,
        )
    )

    flags = (
        extract_plan_flags(
            request,
            requirements,
        )
    )

    quality = (
        calculate_plan_quality(
            completeness,
            consistency,
            readiness,
        )
    )

    confidence = (
        calculate_plan_confidence(
            completeness,
            consistency,
            readiness,
        )
    )

    warnings = []

    if (
        request.plan_type
        == PlanType.CUSTOM
        and not request.plan_id
    ):
        warnings.append(
            "Custom plan has no stable plan_id."
        )

    if not request.capabilities:
        warnings.append(
            "Plan has no declared capabilities."
        )

    notes = [
        "Plan quality is commercial/domain "
        "configuration quality, not market confidence."
    ]

    if request.status == PlanStatus.INACTIVE:
        notes.append(
            "Inactive plan cannot be treated as "
            "normally purchasable."
        )

    if request.status == PlanStatus.RETIRED:
        notes.append(
            "Retired plan is preserved for historical "
            "reference but is not normally purchasable."
        )

    return PlanAssessment(
        data_state=data_state,
        consistency=consistency,
        readiness=readiness,

        completeness=completeness,
        plan_quality=quality,
        confidence=confidence,

        flags=flags,
        warnings=tuple(warnings),
        unmet_requirements=unmet,

        active=(
            request.status
            == PlanStatus.ACTIVE
        ),

        purchasable=plan_is_purchasable(
            request,
            requirements,
            readiness,
        ),

        capabilities=tuple(
            request.capabilities
        ),

        monthly_price=
            request.monthly_price,

        yearly_price=
            request.yearly_price,

        notes=tuple(notes),
    )
# ============================================================
# ROBOMLM SUBSCRIPTION
# plan_service.py — PART 3
# ADMIN MANUAL PLAN MANAGEMENT
# ============================================================

from dataclasses import replace


# ============================================================
# ADMIN ACTIONS
# ============================================================

class PlanAdminAction(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    ACTIVATE = "ACTIVATE"
    DEACTIVATE = "DEACTIVATE"
    RETIRE = "RETIRE"


class PlanAdminDecision(str, Enum):
    ALLOW = "ALLOW"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCK = "BLOCK"


class PlanAdminRole(str, Enum):
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"


# ============================================================
# ADMIN REQUEST
# ============================================================

@dataclass(frozen=True)
class PlanAdminRequest:
    action: PlanAdminAction
    admin_id: str

    plan_id: Optional[str] = None
    plan_type: Optional[PlanType] = None
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[PlanStatus] = None

    currency: Optional[str] = None
    monthly_price: Optional[float] = None
    yearly_price: Optional[float] = None

    capabilities: Optional[Tuple[str, ...]] = None

    admin_role: PlanAdminRole = PlanAdminRole.ADMIN
    reason: str = ""

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    request_id: Optional[str] = None
    timestamp: datetime = field(
        default_factory=_plan_timestamp
    )


# ============================================================
# ADMIN RESULT
# ============================================================

@dataclass(frozen=True)
class PlanAdminResult:
    decision: PlanAdminDecision

    success: bool
    changed: bool

    action: PlanAdminAction
    plan_id: Optional[str]

    errors: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()

    previous_plan: Optional[PlanRequest] = None
    updated_plan: Optional[PlanRequest] = None

    changed_fields: Tuple[str, ...] = ()

    reason: str = ""

    timestamp: datetime = field(
        default_factory=_plan_timestamp
    )


# ============================================================
# ADMIN AUTHORIZATION
# ============================================================

def validate_plan_admin_request(
    request: PlanAdminRequest,
) -> Tuple[str, ...]:

    errors = []

    if not isinstance(
        request,
        PlanAdminRequest,
    ):
        return (
            "request must be PlanAdminRequest.",
        )

    if not _plan_text(
        request.admin_id
    ):
        errors.append(
            "admin_id is required."
        )

    if request.admin_role not in {
        PlanAdminRole.ADMIN,
        PlanAdminRole.SUPER_ADMIN,
    }:
        errors.append(
            "Unauthorized admin role."
        )

    if not _plan_text(
        request.reason
    ):
        errors.append(
            "Admin reason is required."
        )

    if (
        request.action
        != PlanAdminAction.CREATE
        and not _plan_text(
            request.plan_id
        )
    ):
        errors.append(
            "plan_id is required for this action."
        )

    return tuple(errors)


# ============================================================
# NORMALIZE ADMIN PATCH
# ============================================================

def normalize_plan_admin_patch(
    request: PlanAdminRequest,
) -> Mapping[str, Any]:

    patch = {}

    if request.plan_type is not None:
        patch["plan_type"] = _plan_enum(
            PlanType,
            request.plan_type,
            PlanType.CUSTOM,
        )

    if request.name is not None:
        patch["name"] = _plan_text(
            request.name
        )

    if request.description is not None:
        patch["description"] = _plan_text(
            request.description
        )

    if request.status is not None:
        patch["status"] = _plan_enum(
            PlanStatus,
            request.status,
            PlanStatus.ACTIVE,
        )

    if request.currency is not None:
        patch["currency"] = _plan_text(
            request.currency
        ).upper()

    if request.monthly_price is not None:
        patch["monthly_price"] = (
            _plan_number(
                request.monthly_price
            )
        )

    if request.yearly_price is not None:
        patch["yearly_price"] = (
            _plan_number(
                request.yearly_price
            )
        )

    if request.capabilities is not None:
        patch["capabilities"] = tuple(
            _plan_text(value)
            for value in request.capabilities
            if _plan_text(value)
        )

    return patch


# ============================================================
# PLAN PATCH VALIDATION
# ============================================================

def validate_plan_admin_patch(
    previous: PlanRequest,
    patch: Mapping[str, Any],
) -> Tuple[str, ...]:

    errors = []

    if not isinstance(
        previous,
        PlanRequest,
    ):
        return (
            "previous plan must be PlanRequest.",
        )

    if (
        "monthly_price" in patch
        and patch["monthly_price"] is not None
        and patch["monthly_price"] < 0
    ):
        errors.append(
            "monthly_price cannot be negative."
        )

    if (
        "yearly_price" in patch
        and patch["yearly_price"] is not None
        and patch["yearly_price"] < 0
    ):
        errors.append(
            "yearly_price cannot be negative."
        )

    effective_type = patch.get(
        "plan_type",
        previous.plan_type,
    )

    monthly = patch.get(
        "monthly_price",
        previous.monthly_price,
    )

    yearly = patch.get(
        "yearly_price",
        previous.yearly_price,
    )

    if effective_type == PlanType.FREE:
        if monthly is not None and monthly > 0:
            errors.append(
                "FREE plan cannot have positive monthly price."
            )

        if yearly is not None and yearly > 0:
            errors.append(
                "FREE plan cannot have positive yearly price."
            )

    if (
        "currency" in patch
        and not _plan_text(
            patch["currency"]
        )
    ):
        errors.append(
            "Currency cannot be empty."
        )

    if (
        "name" in patch
        and not _plan_text(
            patch["name"]
        )
    ):
        errors.append(
            "Plan name cannot be empty."
        )

    return tuple(errors)


# ============================================================
# APPLY ADMIN PATCH
# ============================================================

def apply_plan_admin_patch(
    previous: PlanRequest,
    request: PlanAdminRequest,
) -> PlanRequest:

    patch = normalize_plan_admin_patch(
        request
    )

    return replace(
        previous,
        **patch,
        timestamp=datetime.now(
            timezone.utc
        ),
    )


# ============================================================
# CHANGED FIELDS
# ============================================================

def detect_plan_changes(
    previous: PlanRequest,
    updated: PlanRequest,
) -> Tuple[str, ...]:

    fields = (
        "plan_id",
        "plan_type",
        "name",
        "status",
        "description",
        "currency",
        "monthly_price",
        "yearly_price",
        "capabilities",
    )

    changed = []

    for field_name in fields:
        if getattr(
            previous,
            field_name,
        ) != getattr(
            updated,
            field_name,
        ):
            changed.append(
                field_name
            )

    return tuple(changed)


# ============================================================
# ADMIN ACTION SAFETY
# ============================================================

def validate_plan_admin_action(
    request: PlanAdminRequest,
    previous: Optional[PlanRequest] = None,
) -> Tuple[str, ...]:

    errors = list(
        validate_plan_admin_request(
            request
        )
    )

    if request.action == PlanAdminAction.CREATE:

        if previous is not None:
            errors.append(
                "CREATE cannot use an existing plan."
            )

        if not _plan_text(
            request.plan_id
        ):
            errors.append(
                "CREATE requires plan_id."
            )

    else:

        if previous is None:
            errors.append(
                "Existing plan is required."
            )

    if request.action == PlanAdminAction.ACTIVATE:
        if previous is not None:
            if previous.status == PlanStatus.RETIRED:
                errors.append(
                    "Retired plan cannot be activated."
                )

    if request.action == PlanAdminAction.RETIRE:
        if previous is not None:
            if previous.status == PlanStatus.RETIRED:
                errors.append(
                    "Plan is already retired."
                )

    return tuple(errors)


# ============================================================
# CREATE PLAN
# ============================================================

def admin_create_plan(
    request: PlanAdminRequest,
) -> PlanAdminResult:

    errors = validate_plan_admin_action(
        request
    )

    if errors:
        return PlanAdminResult(
            decision=PlanAdminDecision.BLOCK,
            success=False,
            changed=False,
            action=request.action,
            plan_id=request.plan_id,
            errors=errors,
            reason="Admin plan creation validation failed.",
        )

    plan = build_plan_request(
        plan_id=request.plan_id,
        plan_type=(
            request.plan_type
            or PlanType.CUSTOM
        ),
        name=request.name or "",
        status=(
            request.status
            or PlanStatus.ACTIVE
        ),
        description=request.description or "",
        currency=request.currency or "USD",
        monthly_price=request.monthly_price,
        yearly_price=request.yearly_price,
        capabilities=request.capabilities or (),
        metadata=request.metadata,
    )

    validation = validate_plan_request(
        plan
    )

    if not validation.valid:
        return PlanAdminResult(
            decision=PlanAdminDecision.BLOCK,
            success=False,
            changed=False,
            action=request.action,
            plan_id=plan.plan_id,
            errors=validation.errors,
            warnings=validation.warnings,
            reason="Created plan failed contract validation.",
        )

    return PlanAdminResult(
        decision=PlanAdminDecision.ALLOW,
        success=True,
        changed=True,
        action=request.action,
        plan_id=plan.plan_id,
        warnings=validation.warnings,
        updated_plan=plan,
        changed_fields=(
            "plan_id",
            "plan_type",
            "name",
            "status",
            "description",
            "currency",
            "monthly_price",
            "yearly_price",
            "capabilities",
        ),
        reason="Plan created by authorized admin.",
    )


# ============================================================
# UPDATE EXISTING PLAN
# ============================================================

def admin_update_plan(
    previous: PlanRequest,
    request: PlanAdminRequest,
) -> PlanAdminResult:

    errors = validate_plan_admin_action(
        request,
        previous,
    )

    if errors:
        return PlanAdminResult(
            decision=PlanAdminDecision.BLOCK,
            success=False,
            changed=False,
            action=request.action,
            plan_id=request.plan_id,
            errors=errors,
            previous_plan=previous,
            reason="Admin plan update validation failed.",
        )

    updated = apply_plan_admin_patch(
        previous,
        request,
    )

    errors = validate_plan_admin_patch(
        previous,
        normalize_plan_admin_patch(
            request
        ),
    )

    if errors:
        return PlanAdminResult(
            decision=PlanAdminDecision.BLOCK,
            success=False,
            changed=False,
            action=request.action,
            plan_id=previous.plan_id,
            errors=errors,
            previous_plan=previous,
            reason="Plan patch violates plan contract.",
        )

    validation = validate_plan_request(
        updated
    )

    if not validation.valid:
        return PlanAdminResult(
            decision=PlanAdminDecision.BLOCK,
            success=False,
            changed=False,
            action=request.action,
            plan_id=previous.plan_id,
            errors=validation.errors,
            warnings=validation.warnings,
            previous_plan=previous,
            reason="Updated plan failed validation.",
        )

    changed_fields = detect_plan_changes(
        previous,
        updated,
    )

    return PlanAdminResult(
        decision=PlanAdminDecision.ALLOW,
        success=True,
        changed=bool(
            changed_fields
        ),
        action=request.action,
        plan_id=updated.plan_id,
        warnings=validation.warnings,
        previous_plan=previous,
        updated_plan=updated,
        changed_fields=changed_fields,
        reason="Plan updated by authorized admin.",
    )


# ============================================================
# LIFECYCLE ACTIONS
# ============================================================

def admin_activate_plan(
    previous: PlanRequest,
    request: PlanAdminRequest,
) -> PlanAdminResult:

    action_request = replace(
        request,
        action=PlanAdminAction.UPDATE,
        status=PlanStatus.ACTIVE,
    )

    return admin_update_plan(
        previous,
        action_request,
    )


def admin_deactivate_plan(
    previous: PlanRequest,
    request: PlanAdminRequest,
) -> PlanAdminResult:

    action_request = replace(
        request,
        action=PlanAdminAction.UPDATE,
        status=PlanStatus.INACTIVE,
    )

    return admin_update_plan(
        previous,
        action_request,
    )


def admin_retire_plan(
    previous: PlanRequest,
    request: PlanAdminRequest,
) -> PlanAdminResult:

    action_request = replace(
        request,
        action=PlanAdminAction.UPDATE,
        status=PlanStatus.RETIRED,
    )

    return admin_update_plan(
        previous,
        action_request,
    )


# ============================================================
# ADMIN DISPATCHER
# ============================================================

def execute_plan_admin_action(
    request: PlanAdminRequest,
    previous: Optional[PlanRequest] = None,
) -> PlanAdminResult:

    if request.action == PlanAdminAction.CREATE:
        return admin_create_plan(
            request
        )

    if previous is None:
        return PlanAdminResult(
            decision=PlanAdminDecision.BLOCK,
            success=False,
            changed=False,
            action=request.action,
            plan_id=request.plan_id,
            errors=(
                "Existing plan is required.",
            ),
            reason="Cannot execute admin action without plan.",
        )

    if request.action == PlanAdminAction.UPDATE:
        return admin_update_plan(
            previous,
            request,
        )

    if request.action == PlanAdminAction.ACTIVATE:
        return admin_activate_plan(
            previous,
            request,
        )

    if request.action == PlanAdminAction.DEACTIVATE:
        return admin_deactivate_plan(
            previous,
            request,
        )

    if request.action == PlanAdminAction.RETIRE:
        return admin_retire_plan(
            previous,
            request,
        )

    return PlanAdminResult(
        decision=PlanAdminDecision.BLOCK,
        success=False,
        changed=False,
        action=request.action,
        plan_id=request.plan_id,
        errors=(
            "Unsupported admin action.",
        ),
        reason="Unknown plan administration action.",
    )


# ============================================================
# ADMIN AUTHORITY BOUNDARY
# ============================================================

def plan_admin_authority_check() -> Mapping[str, bool]:

    return {
        "can_manage_plan_definition": True,
        "can_change_plan_price": True,
        "can_change_plan_capabilities": True,
        "can_change_plan_status": True,

        # Explicitly outside Plan Service authority.
        "can_grant_user_entitlement": False,
        "can_override_cas": False,
        "can_override_risk": False,
        "can_override_d13": False,
        "can_execute_trade": False,
        "can_change_market_decision": False,
    }
# ============================================================
# ROBOMLM SUBSCRIPTION
# plan_service.py — PART 4
# PLAN CATALOG / REGISTRY / VERSION CONTROL
# ============================================================


# ============================================================
# PLAN CATALOG
# ============================================================

@dataclass(frozen=True)
class PlanCatalogEntry:
    plan: PlanRequest
    version: str = PLAN_SERVICE_VERSION
    revision: int = 1
    updated_by: Optional[str] = None
    updated_at: datetime = field(
        default_factory=_plan_timestamp
    )


@dataclass(frozen=True)
class PlanCatalogSnapshot:
    total: int
    active: int
    inactive: int
    retired: int
    plans: Tuple[PlanCatalogEntry, ...] = ()
    timestamp: datetime = field(
        default_factory=_plan_timestamp
    )


# ============================================================
# PLAN CATALOG ENGINE
# ============================================================

class PlanCatalog:

    def __init__(self) -> None:
        self._plans: dict[str, PlanCatalogEntry] = {}

    # --------------------------------------------------------
    # INTERNAL KEY
    # --------------------------------------------------------

    @staticmethod
    def _key(plan_id: Any) -> str:
        return _plan_text(plan_id)

    # --------------------------------------------------------
    # EXISTS
    # --------------------------------------------------------

    def exists(
        self,
        plan_id: str,
    ) -> bool:

        return self._key(plan_id) in self._plans

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    def get(
        self,
        plan_id: str,
    ) -> Optional[PlanRequest]:

        entry = self._plans.get(
            self._key(plan_id)
        )

        if entry is None:
            return None

        return entry.plan

    # --------------------------------------------------------
    # GET ENTRY
    # --------------------------------------------------------

    def get_entry(
        self,
        plan_id: str,
    ) -> Optional[PlanCatalogEntry]:

        return self._plans.get(
            self._key(plan_id)
        )

    # --------------------------------------------------------
    # ADD
    # --------------------------------------------------------

    def add(
        self,
        plan: PlanRequest,
        *,
        updated_by: Optional[str] = None,
    ) -> bool:

        plan_id = self._key(
            plan.plan_id
        )

        if not plan_id:
            return False

        if plan_id in self._plans:
            return False

        self._plans[plan_id] = (
            PlanCatalogEntry(
                plan=plan,
                revision=1,
                updated_by=updated_by,
            )
        )

        return True

    # --------------------------------------------------------
    # REPLACE
    # --------------------------------------------------------

    def replace(
        self,
        plan: PlanRequest,
        *,
        updated_by: Optional[str] = None,
    ) -> bool:

        plan_id = self._key(
            plan.plan_id
        )

        if not plan_id:
            return False

        previous = self._plans.get(
            plan_id
        )

        if previous is None:
            return False

        self._plans[plan_id] = (
            PlanCatalogEntry(
                plan=plan,
                version=previous.version,
                revision=previous.revision + 1,
                updated_by=updated_by,
                updated_at=datetime.now(
                    timezone.utc
                ),
            )
        )

        return True

    # --------------------------------------------------------
    # REMOVE
    # --------------------------------------------------------

    def remove(
        self,
        plan_id: str,
    ) -> bool:

        key = self._key(plan_id)

        if key not in self._plans:
            return False

        del self._plans[key]
        return True

    # --------------------------------------------------------
    # LIST
    # --------------------------------------------------------

    def list_plans(
        self,
        *,
        status: Optional[PlanStatus] = None,
        plan_type: Optional[PlanType] = None,
    ) -> Tuple[PlanRequest, ...]:

        plans = []

        for entry in self._plans.values():

            plan = entry.plan

            if (
                status is not None
                and plan.status != status
            ):
                continue

            if (
                plan_type is not None
                and plan.plan_type != plan_type
            ):
                continue

            plans.append(plan)

        return tuple(plans)

    # --------------------------------------------------------
    # SNAPSHOT
    # --------------------------------------------------------

    def snapshot(self) -> PlanCatalogSnapshot:

        entries = tuple(
            self._plans.values()
        )

        return PlanCatalogSnapshot(
            total=len(entries),
            active=sum(
                1
                for item in entries
                if item.plan.status
                == PlanStatus.ACTIVE
            ),
            inactive=sum(
                1
                for item in entries
                if item.plan.status
                == PlanStatus.INACTIVE
            ),
            retired=sum(
                1
                for item in entries
                if item.plan.status
                == PlanStatus.RETIRED
            ),
            plans=entries,
        )

    # --------------------------------------------------------
    # COUNT
    # --------------------------------------------------------

    def count(self) -> int:
        return len(self._plans)


# ============================================================
# PLAN SERVICE RESULT
# ============================================================

@dataclass(frozen=True)
class PlanServiceResult:
    success: bool
    decision: PlanAdminDecision

    action: Optional[PlanAdminAction] = None
    plan_id: Optional[str] = None

    plan: Optional[PlanRequest] = None
    assessment: Optional[PlanAssessment] = None

    errors: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()

    reason: str = ""

    timestamp: datetime = field(
        default_factory=_plan_timestamp
    )


# ============================================================
# PLAN SERVICE
# ============================================================

class PlanService:

    def __init__(
        self,
        catalog: Optional[PlanCatalog] = None,
    ) -> None:

        self.catalog = (
            catalog
            or PlanCatalog()
        )

    # --------------------------------------------------------
    # CREATE
    # --------------------------------------------------------

    def create_plan(
        self,
        request: PlanAdminRequest,
    ) -> PlanServiceResult:

        if self.catalog.exists(
            request.plan_id
        ):
            return PlanServiceResult(
                success=False,
                decision=PlanAdminDecision.BLOCK,
                action=request.action,
                plan_id=request.plan_id,
                errors=(
                    "Plan already exists.",
                ),
                reason="Duplicate plan_id.",
            )

        result = admin_create_plan(
            request
        )

        if not result.success:
            return PlanServiceResult(
                success=False,
                decision=result.decision,
                action=result.action,
                plan_id=result.plan_id,
                errors=result.errors,
                warnings=result.warnings,
                reason=result.reason,
            )

        added = self.catalog.add(
            result.updated_plan,
            updated_by=request.admin_id,
        )

        if not added:
            return PlanServiceResult(
                success=False,
                decision=PlanAdminDecision.BLOCK,
                action=request.action,
                plan_id=request.plan_id,
                errors=(
                    "Plan could not be added to catalog.",
                ),
                reason="Catalog insertion failed.",
            )

        assessment = build_plan_assessment(
            result.updated_plan
        )

        return PlanServiceResult(
            success=True,
            decision=PlanAdminDecision.ALLOW,
            action=request.action,
            plan_id=result.updated_plan.plan_id,
            plan=result.updated_plan,
            assessment=assessment,
            warnings=result.warnings,
            reason="Plan created and registered.",
        )

    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------

    def update_plan(
        self,
        request: PlanAdminRequest,
    ) -> PlanServiceResult:

        previous = self.catalog.get(
            request.plan_id
        )

        if previous is None:
            return PlanServiceResult(
                success=False,
                decision=PlanAdminDecision.BLOCK,
                action=request.action,
                plan_id=request.plan_id,
                errors=(
                    "Plan not found.",
                ),
                reason="Cannot update unknown plan.",
            )

        result = admin_update_plan(
            previous,
            request,
        )

        if not result.success:
            return PlanServiceResult(
                success=False,
                decision=result.decision,
                action=result.action,
                plan_id=result.plan_id,
                errors=result.errors,
                warnings=result.warnings,
                reason=result.reason,
            )

        if result.updated_plan is None:
            return PlanServiceResult(
                success=False,
                decision=PlanAdminDecision.BLOCK,
                action=request.action,
                plan_id=request.plan_id,
                errors=(
                    "Updated plan missing.",
                ),
                reason="Invalid update result.",
            )

        replaced = self.catalog.replace(
            result.updated_plan,
            updated_by=request.admin_id,
        )

        if not replaced:
            return PlanServiceResult(
                success=False,
                decision=PlanAdminDecision.BLOCK,
                action=request.action,
                plan_id=request.plan_id,
                errors=(
                    "Catalog replacement failed.",
                ),
                reason="Plan update was not committed.",
            )

        assessment = build_plan_assessment(
            result.updated_plan
        )

        return PlanServiceResult(
            success=True,
            decision=PlanAdminDecision.ALLOW,
            action=request.action,
            plan_id=result.updated_plan.plan_id,
            plan=result.updated_plan,
            assessment=assessment,
            warnings=result.warnings,
            reason="Plan updated and registered.",
        )

    # --------------------------------------------------------
    # LIFECYCLE
    # --------------------------------------------------------

    def activate(
        self,
        request: PlanAdminRequest,
    ) -> PlanServiceResult:

        request = replace(
            request,
            action=PlanAdminAction.ACTIVATE,
            status=PlanStatus.ACTIVE,
        )

        return self.update_plan(
            request
        )

    def deactivate(
        self,
        request: PlanAdminRequest,
    ) -> PlanServiceResult:

        request = replace(
            request,
            action=PlanAdminAction.DEACTIVATE,
            status=PlanStatus.INACTIVE,
        )

        return self.update_plan(
            request
        )

    def retire(
        self,
        request: PlanAdminRequest,
    ) -> PlanServiceResult:

        request = replace(
            request,
            action=PlanAdminAction.RETIRE,
            status=PlanStatus.RETIRED,
        )

        return self.update_plan(
            request
        )

    # --------------------------------------------------------
    # READ
    # --------------------------------------------------------

    def get_plan(
        self,
        plan_id: str,
    ) -> Optional[PlanRequest]:

        return self.catalog.get(
            plan_id
        )

    def get_plan_assessment(
        self,
        plan_id: str,
    ) -> Optional[PlanAssessment]:

        plan = self.get_plan(
            plan_id
        )

        if plan is None:
            return None

        return build_plan_assessment(
            plan
        )

    def list_plans(
        self,
        *,
        status: Optional[PlanStatus] = None,
        plan_type: Optional[PlanType] = None,
    ) -> Tuple[PlanRequest, ...]:

        return self.catalog.list_plans(
            status=status,
            plan_type=plan_type,
        )

    # --------------------------------------------------------
    # SNAPSHOT
    # --------------------------------------------------------

    def snapshot(self) -> PlanCatalogSnapshot:
        return self.catalog.snapshot()

    # --------------------------------------------------------
    # HEALTH
    # --------------------------------------------------------

    def health(self) -> Mapping[str, Any]:

        snapshot = self.snapshot()

        return {
            "engine": PLAN_SERVICE_ENGINE,
            "version": PLAN_SERVICE_VERSION,
            "healthy": True,
            "plan_count": snapshot.total,
            "active_count": snapshot.active,
            "inactive_count": snapshot.inactive,
            "retired_count": snapshot.retired,
        }


# ============================================================
# SINGLETON SERVICE
# ============================================================

_PLAN_SERVICE = PlanService()


def get_plan_service() -> PlanService:
    return _PLAN_SERVICE


# ============================================================
# CONVENIENCE API
# ============================================================

def create_plan(
    request: PlanAdminRequest,
) -> PlanServiceResult:

    return _PLAN_SERVICE.create_plan(
        request
    )


def update_plan(
    request: PlanAdminRequest,
) -> PlanServiceResult:

    return _PLAN_SERVICE.update_plan(
        request
    )


def get_plan(
    plan_id: str,
) -> Optional[PlanRequest]:

    return _PLAN_SERVICE.get_plan(
        plan_id
    )


def get_plan_assessment(
    plan_id: str,
) -> Optional[PlanAssessment]:

    return _PLAN_SERVICE.get_plan_assessment(
        plan_id
    )


def list_plans(
    *,
    status: Optional[PlanStatus] = None,
    plan_type: Optional[PlanType] = None,
) -> Tuple[PlanRequest, ...]:

    return _PLAN_SERVICE.list_plans(
        status=status,
        plan_type=plan_type,
    )
# ============================================================
# ROBOMLM SUBSCRIPTION
# plan_service.py — PART 5
# SERIALIZATION / INTEGRITY / BOOTSTRAP / PUBLIC API
# ============================================================


# ============================================================
# SERIALIZATION
# ============================================================

def serialize_plan(
    plan: Optional[PlanRequest],
) -> Mapping[str, Any]:

    if plan is None:
        return {}

    return {
        "plan_id": plan.plan_id,
        "plan_type": plan.plan_type.value,
        "name": plan.name,
        "status": plan.status.value,
        "description": plan.description,
        "mode": plan.mode.value,
        "priority": plan.priority.value,
        "currency": plan.currency,
        "monthly_price": plan.monthly_price,
        "yearly_price": plan.yearly_price,
        "capabilities": tuple(
            plan.capabilities
        ),
        "metadata": dict(
            plan.metadata
        ),
        "request_id": plan.request_id,
        "timestamp": plan.timestamp.isoformat(),
    }


def serialize_plan_assessment(
    assessment: Optional[PlanAssessment],
) -> Mapping[str, Any]:

    if assessment is None:
        return {}

    return {
        "data_state": assessment.data_state.value,
        "consistency": assessment.consistency.value,
        "readiness": assessment.readiness.value,
        "completeness": assessment.completeness,
        "plan_quality": assessment.plan_quality,
        "confidence": assessment.confidence,
        "flags": tuple(assessment.flags),
        "warnings": tuple(assessment.warnings),
        "unmet_requirements": tuple(
            assessment.unmet_requirements
        ),
        "active": assessment.active,
        "purchasable": assessment.purchasable,
        "capabilities": tuple(
            assessment.capabilities
        ),
        "monthly_price": assessment.monthly_price,
        "yearly_price": assessment.yearly_price,
        "notes": tuple(assessment.notes),
    }


def serialize_plan_result(
    result: PlanServiceResult,
) -> Mapping[str, Any]:

    return {
        "success": result.success,
        "decision": result.decision.value,
        "action": (
            result.action.value
            if result.action
            else None
        ),
        "plan_id": result.plan_id,
        "plan": serialize_plan(
            result.plan
        ),
        "assessment": serialize_plan_assessment(
            result.assessment
        ),
        "errors": tuple(result.errors),
        "warnings": tuple(result.warnings),
        "reason": result.reason,
        "timestamp": result.timestamp.isoformat(),
    }


def serialize_catalog_snapshot(
    snapshot: PlanCatalogSnapshot,
) -> Mapping[str, Any]:

    return {
        "total": snapshot.total,
        "active": snapshot.active,
        "inactive": snapshot.inactive,
        "retired": snapshot.retired,
        "plans": tuple(
            serialize_plan(
                entry.plan
            )
            for entry in snapshot.plans
        ),
        "timestamp": snapshot.timestamp.isoformat(),
    }


# ============================================================
# INTEGRITY VALIDATION
# ============================================================

def validate_plan_integrity(
    plan: Optional[PlanRequest],
) -> Tuple[str, ...]:

    if plan is None:
        return (
            "plan is required.",
        )

    errors = list(
        validate_plan_numeric_inputs(
            plan
        )
    )

    if not _plan_text(
        plan.plan_id
    ):
        errors.append(
            "plan_id is required for registered plans."
        )

    if not _plan_text(
        plan.name
    ):
        errors.append(
            "plan name is required."
        )

    if not _plan_text(
        plan.currency
    ):
        errors.append(
            "currency is required."
        )

    if (
        plan.plan_type == PlanType.FREE
        and plan.monthly_price is not None
        and plan.monthly_price > 0
    ):
        errors.append(
            "FREE plan cannot have positive monthly price."
        )

    if (
        plan.plan_type == PlanType.FREE
        and plan.yearly_price is not None
        and plan.yearly_price > 0
    ):
        errors.append(
            "FREE plan cannot have positive yearly price."
        )

    return tuple(errors)


def validate_catalog_integrity(
    catalog: PlanCatalog,
) -> Tuple[str, ...]:

    errors = []

    snapshot = catalog.snapshot()

    seen = set()

    for entry in snapshot.plans:

        plan_id = _plan_text(
            entry.plan.plan_id
        )

        if not plan_id:
            errors.append(
                "Catalog contains plan without plan_id."
            )
            continue

        if plan_id in seen:
            errors.append(
                f"Duplicate plan_id: {plan_id}"
            )

        seen.add(plan_id)

        errors.extend(
            validate_plan_integrity(
                entry.plan
            )
        )

        if entry.revision < 1:
            errors.append(
                f"Invalid revision for plan: {plan_id}"
            )

    return tuple(errors)


# ============================================================
# PLAN SUMMARY
# ============================================================

def build_plan_summary(
    plan: PlanRequest,
) -> Mapping[str, Any]:

    assessment = build_plan_assessment(
        plan
    )

    return {
        "plan_id": plan.plan_id,
        "name": plan.name,
        "type": plan.plan_type.value,
        "status": plan.status.value,
        "currency": plan.currency,
        "monthly_price": plan.monthly_price,
        "yearly_price": plan.yearly_price,
        "capabilities": tuple(
            plan.capabilities
        ),
        "active": assessment.active,
        "purchasable": assessment.purchasable,
        "quality": assessment.plan_quality,
        "readiness": assessment.readiness.value,
    }


# ============================================================
# DEFAULT PLAN DEFINITIONS
# ============================================================

def build_default_plan_requests() -> Tuple[PlanRequest, ...]:

    return (
        build_plan_request(
            plan_id="FREE",
            plan_type=PlanType.FREE,
            name="ROBOMLM Free",
            status=PlanStatus.ACTIVE,
            description=(
                "Core ROBOMLM market intelligence access."
            ),
            currency="USD",
            monthly_price=0.0,
            yearly_price=0.0,
            capabilities=(
                PlanCapability.TERMINAL.value,
                PlanCapability.DISCOVERY.value,
                PlanCapability.CHAT.value,
            ),
        ),

        build_plan_request(
            plan_id="PRO",
            plan_type=PlanType.PRO,
            name="ROBOMLM Pro",
            status=PlanStatus.ACTIVE,
            description=(
                "Advanced market intelligence workspace."
            ),
            currency="USD",
            capabilities=(
                PlanCapability.TERMINAL.value,
                PlanCapability.DISCOVERY.value,
                PlanCapability.MEMORY.value,
                PlanCapability.RESEARCH.value,
                PlanCapability.CHAT.value,
                PlanCapability.QUICK_ANALYSIS.value,
            ),
        ),

        build_plan_request(
            plan_id="ELITE",
            plan_type=PlanType.ELITE,
            name="ROBOMLM Elite",
            status=PlanStatus.ACTIVE,
            description=(
                "High-level advanced intelligence access."
            ),
            currency="USD",
            capabilities=(
                PlanCapability.TERMINAL.value,
                PlanCapability.DISCOVERY.value,
                PlanCapability.MEMORY.value,
                PlanCapability.RESEARCH.value,
                PlanCapability.CHAT.value,
                PlanCapability.QUICK_ANALYSIS.value,
                PlanCapability.DEEP_ANALYSIS.value,
            ),
        ),

        build_plan_request(
            plan_id="AUTO",
            plan_type=PlanType.AUTO,
            name="ROBOMLM Auto",
            status=PlanStatus.ACTIVE,
            description=(
                "Advanced intelligence with "
                "AUTOROBOMLM capability."
            ),
            currency="USD",
            capabilities=(
                PlanCapability.TERMINAL.value,
                PlanCapability.DISCOVERY.value,
                PlanCapability.MEMORY.value,
                PlanCapability.RESEARCH.value,
                PlanCapability.AUTOMATION.value,
                PlanCapability.CHAT.value,
                PlanCapability.QUICK_ANALYSIS.value,
                PlanCapability.DEEP_ANALYSIS.value,
            ),
        ),
    )


# ============================================================
# BOOTSTRAP DEFAULT PLANS
# ============================================================

def bootstrap_default_plans(
    service: Optional[PlanService] = None,
) -> Mapping[str, Any]:

    service = (
        service
        or get_plan_service()
    )

    created = []
    skipped = []
    errors = []

    for plan in build_default_plan_requests():

        if service.catalog.exists(
            plan.plan_id
        ):
            skipped.append(
                plan.plan_id
            )
            continue

        admin_request = PlanAdminRequest(
            action=PlanAdminAction.CREATE,
            admin_id="SYSTEM",
            plan_id=plan.plan_id,
            plan_type=plan.plan_type,
            name=plan.name,
            description=plan.description,
            status=plan.status,
            currency=plan.currency,
            monthly_price=plan.monthly_price,
            yearly_price=plan.yearly_price,
            capabilities=plan.capabilities,
            admin_role=PlanAdminRole.SUPER_ADMIN,
            reason="System plan bootstrap.",
        )

        result = service.create_plan(
            admin_request
        )

        if result.success:
            created.append(
                plan.plan_id
            )
        else:
            errors.append(
                {
                    "plan_id": plan.plan_id,
                    "errors": result.errors,
                }
            )

    return {
        "created": tuple(created),
        "skipped": tuple(skipped),
        "errors": tuple(errors),
        "total": service.catalog.count(),
    }


# ============================================================
# OPERATIONAL CHECK
# ============================================================

def plan_service_operational_check(
    service: Optional[PlanService] = None,
) -> Mapping[str, Any]:

    service = (
        service
        or get_plan_service()
    )

    integrity_errors = (
        validate_catalog_integrity(
            service.catalog
        )
    )

    health = service.health()

    return {
        "engine": PLAN_SERVICE_ENGINE,
        "version": PLAN_SERVICE_VERSION,
        "operational": (
            health["healthy"]
            and not integrity_errors
        ),
        "health": health,
        "integrity_errors": integrity_errors,
    }


# ============================================================
# AUTHORITY BOUNDARY
# ============================================================

def plan_service_authority() -> Mapping[str, bool]:

    return {
        "define_plan": True,
        "validate_plan": True,
        "manage_plan_catalog": True,
        "admin_price_change": True,
        "admin_capability_change": True,
        "admin_status_change": True,

        # Separate domain authorities.
        "create_subscription": False,
        "grant_entitlement": False,
        "revoke_entitlement": False,
        "override_cas": False,
        "override_risk": False,
        "override_d13": False,
        "execute_trade": False,
    }


# ============================================================
# ENGINE INFO
# ============================================================

def plan_service_info() -> Mapping[str, Any]:

    service = get_plan_service()

    return {
        "engine": PLAN_SERVICE_ENGINE,
        "version": PLAN_SERVICE_VERSION,
        "service": "Plan Service",
        "role": (
            "Plan definition, validation, "
            "catalog and admin lifecycle management."
        ),
        "plan_count": service.catalog.count(),
        "authority": plan_service_authority(),
    }


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [
    # Constants
    "PLAN_SERVICE_ENGINE",
    "PLAN_SERVICE_VERSION",

    # Enums
    "PlanStatus",
    "PlanType",
    "PlanPriority",
    "PlanMode",
    "PlanContractStatus",
    "PlanCapability",
    "PlanDataState",
    "PlanConsistency",
    "PlanReadiness",
    "PlanAdminAction",
    "PlanAdminDecision",
    "PlanAdminRole",

    # Contracts
    "PlanRequest",
    "PlanReference",
    "PlanContractValidation",
    "PlanRequirements",
    "PlanAssessment",
    "PlanAdminRequest",
    "PlanAdminResult",
    "PlanCatalogEntry",
    "PlanCatalogSnapshot",
    "PlanServiceResult",

    # Validation
    "validate_plan_numeric_inputs",
    "validate_plan_request",
    "validate_plan_reference",
    "validate_plan_admin_request",
    "validate_plan_admin_patch",
    "validate_plan_admin_action",
    "validate_plan_integrity",
    "validate_catalog_integrity",

    # Assessment
    "evaluate_plan_data_state",
    "evaluate_plan_consistency",
    "calculate_plan_completeness",
    "evaluate_plan_requirements",
    "extract_plan_flags",
    "evaluate_plan_readiness",
    "calculate_plan_quality",
    "calculate_plan_confidence",
    "plan_is_purchasable",
    "build_plan_assessment",

    # Admin
    "normalize_plan_admin_patch",
    "apply_plan_admin_patch",
    "detect_plan_changes",
    "admin_create_plan",
    "admin_update_plan",
    "admin_activate_plan",
    "admin_deactivate_plan",
    "admin_retire_plan",
    "execute_plan_admin_action",

    # Catalog / Service
    "PlanCatalog",
    "PlanService",
    "get_plan_service",
    "create_plan",
    "update_plan",
    "get_plan",
    "get_plan_assessment",
    "list_plans",

    # Serialization / Summary
    "serialize_plan",
    "serialize_plan_assessment",
    "serialize_plan_result",
    "serialize_catalog_snapshot",
    "build_plan_summary",

    # Bootstrap / Operations
    "build_default_plan_requests",
    "bootstrap_default_plans",
    "plan_service_operational_check",
    "plan_service_authority",
    "plan_service_info",
]