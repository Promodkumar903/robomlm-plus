# ============================================================
# ROBOMLM SUBSCRIPTION
# entitlement_service.py — PART 1
# ENTITLEMENT FOUNDATION / CONTRACTS
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Optional, Tuple


# ============================================================
# ENGINE IDENTITY
# ============================================================

ENTITLEMENT_SERVICE_ENGINE = "ROBOMLM_ENTITLEMENT_SERVICE"
ENTITLEMENT_SERVICE_VERSION = "1.0"


# ============================================================
# ENTITLEMENT STATUS
# ============================================================

class EntitlementStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    BLOCKED = "BLOCKED"
    PENDING = "PENDING"


# ============================================================
# ENTITLEMENT DECISION
# ============================================================

class EntitlementDecision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    RESTRICTED = "RESTRICTED"


# ============================================================
# ENTITLEMENT MODE
# ============================================================

class EntitlementMode(str, Enum):
    PAPER = "PAPER"
    DEMO = "DEMO"
    LIVE = "LIVE"
    UNKNOWN = "UNKNOWN"


# ============================================================
# ENTITLEMENT PRIORITY
# ============================================================

class EntitlementPriority(str, Enum):
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ============================================================
# ENTITLEMENT CONTRACT STATUS
# ============================================================

class EntitlementContractStatus(str, Enum):
    CREATED = "CREATED"
    VALID = "VALID"
    INVALID = "INVALID"
    ASSESSED = "ASSESSED"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    BLOCKED = "BLOCKED"


# ============================================================
# ENTITLEMENT SOURCE
# ============================================================

class EntitlementSource(str, Enum):
    PLAN = "PLAN"
    ADMIN_OVERRIDE = "ADMIN_OVERRIDE"
    SYSTEM = "SYSTEM"
    SUBSCRIPTION = "SUBSCRIPTION"
    UNKNOWN = "UNKNOWN"


# ============================================================
# CAPABILITY
# ============================================================

class EntitlementCapability(str, Enum):
    TERMINAL = "TERMINAL"
    DISCOVERY = "DISCOVERY"
    MEMORY = "MEMORY"
    RESEARCH = "RESEARCH"
    AUTOMATION = "AUTOMATION"
    CHAT = "CHAT"
    QUICK_ANALYSIS = "QUICK_ANALYSIS"
    DEEP_ANALYSIS = "DEEP_ANALYSIS"

    # Future/extensible capability namespace.
    CUSTOM = "CUSTOM"


# ============================================================
# NORMALIZATION HELPERS
# ============================================================

def _entitlement_text(
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


def _entitlement_enum(
    enum_type: type[Enum],
    value: Any,
    default: Enum,
) -> Enum:

    if isinstance(value, enum_type):
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


def _entitlement_bool(
    value: Any,
    default: bool = False,
) -> bool:

    if value is None:
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, str):

        normalized = (
            value.strip().lower()
        )

        if normalized in {
            "true",
            "1",
            "yes",
            "y",
            "on",
        }:
            return True

        if normalized in {
            "false",
            "0",
            "no",
            "n",
            "off",
        }:
            return False

    return bool(value)


def _entitlement_timestamp(
    value: Any = None,
) -> datetime:

    if isinstance(value, datetime):
        return value

    return datetime.now(
        timezone.utc
    )


# ============================================================
# ENTITLEMENT REQUEST
# ============================================================

@dataclass(frozen=True)
class EntitlementRequest:
    """
    Request to resolve access to a ROBOMLM capability.

    Entitlement Service determines ACCESS entitlement only.
    It does not create market decisions and does not override
    D13, Risk, CAS, or execution authority.
    """

    user_id: Optional[str] = None
    account_id: Optional[str] = None

    plan_id: Optional[str] = None
    subscription_id: Optional[str] = None

    capability: str = ""

    mode: EntitlementMode = (
        EntitlementMode.UNKNOWN
    )

    priority: EntitlementPriority = (
        EntitlementPriority.NORMAL
    )

    requested: bool = True

    subscription_active: bool = False

    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None

    source: EntitlementSource = (
        EntitlementSource.PLAN
    )

    admin_override: bool = False
    system_grant: bool = False

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    request_id: Optional[str] = None

    timestamp: datetime = field(
        default_factory=_entitlement_timestamp
    )


# ============================================================
# ENTITLEMENT REFERENCE
# ============================================================

@dataclass(frozen=True)
class EntitlementReference:
    entitlement_id: str

    user_id: str
    capability: str

    plan_id: Optional[str] = None
    subscription_id: Optional[str] = None

    status: EntitlementStatus = (
        EntitlementStatus.UNKNOWN
    )

    source: EntitlementSource = (
        EntitlementSource.UNKNOWN
    )

    version: str = (
        ENTITLEMENT_SERVICE_VERSION
    )

    created_at: datetime = field(
        default_factory=_entitlement_timestamp
    )


# ============================================================
# ENTITLEMENT CONTRACT VALIDATION
# ============================================================

@dataclass(frozen=True)
class EntitlementContractValidation:
    valid: bool

    errors: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()

    checked_at: datetime = field(
        default_factory=_entitlement_timestamp
    )


# ============================================================
# CAPABILITY NORMALIZATION
# ============================================================

def normalize_entitlement_capability(
    capability: Any,
) -> str:

    value = _entitlement_text(
        capability
    ).upper()

    if not value:
        return ""

    try:
        return EntitlementCapability(
            value
        ).value
    except ValueError:
        # Preserve future/custom capabilities.
        return value


def normalize_entitlement_capabilities(
    capabilities: Any,
) -> Tuple[str, ...]:

    if capabilities is None:
        return ()

    if isinstance(
        capabilities,
        str,
    ):
        capabilities = (
            capabilities,
        )

    try:
        values = tuple(
            capabilities
        )
    except TypeError:
        return ()

    normalized = []

    for capability in values:

        value = (
            normalize_entitlement_capability(
                capability
            )
        )

        if value and value not in normalized:
            normalized.append(value)

    return tuple(normalized)


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_entitlement_request(
    request: EntitlementRequest,
) -> EntitlementContractValidation:

    errors = []
    warnings = []

    if not isinstance(
        request,
        EntitlementRequest,
    ):
        return EntitlementContractValidation(
            valid=False,
            errors=(
                "request must be EntitlementRequest.",
            ),
        )

    if not _entitlement_text(
        request.user_id
    ):
        errors.append(
            "user_id is required."
        )

    if not _entitlement_text(
        request.capability
    ):
        errors.append(
            "capability is required."
        )

    if (
        request.valid_from is not None
        and request.valid_until is not None
        and request.valid_until
        < request.valid_from
    ):
        errors.append(
            "valid_until cannot be earlier than valid_from."
        )

    if (
        request.admin_override
        and request.source
        != EntitlementSource.ADMIN_OVERRIDE
    ):
        warnings.append(
            "admin_override is enabled but source "
            "is not ADMIN_OVERRIDE."
        )

    if (
        request.system_grant
        and request.source
        != EntitlementSource.SYSTEM
    ):
        warnings.append(
            "system_grant is enabled but source "
            "is not SYSTEM."
        )

    if (
        not request.plan_id
        and not request.subscription_id
        and not request.admin_override
        and not request.system_grant
    ):
        warnings.append(
            "No plan_id or subscription_id supplied."
        )

    return EntitlementContractValidation(
        valid=not errors,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


# ============================================================
# REFERENCE VALIDATION
# ============================================================

def validate_entitlement_reference(
    reference: EntitlementReference,
) -> bool:

    if not isinstance(
        reference,
        EntitlementReference,
    ):
        return False

    if not _entitlement_text(
        reference.entitlement_id
    ):
        return False

    if not _entitlement_text(
        reference.user_id
    ):
        return False

    if not _entitlement_text(
        reference.capability
    ):
        return False

    if not _entitlement_text(
        reference.version
    ):
        return False

    return True


# ============================================================
# REQUEST BUILDER
# ============================================================

def build_entitlement_request(
    *,
    user_id: Optional[str] = None,
    account_id: Optional[str] = None,
    plan_id: Optional[str] = None,
    subscription_id: Optional[str] = None,
    capability: Any = "",
    mode: Any = EntitlementMode.UNKNOWN,
    priority: Any = EntitlementPriority.NORMAL,
    requested: Any = True,
    subscription_active: Any = False,
    valid_from: Optional[datetime] = None,
    valid_until: Optional[datetime] = None,
    source: Any = EntitlementSource.PLAN,
    admin_override: Any = False,
    system_grant: Any = False,
    metadata: Optional[
        Mapping[str, Any]
    ] = None,
    request_id: Optional[str] = None,
) -> EntitlementRequest:

    return EntitlementRequest(
        user_id=_entitlement_text(
            user_id,
            None,
        ),
        account_id=_entitlement_text(
            account_id,
            None,
        ),
        plan_id=_entitlement_text(
            plan_id,
            None,
        ),
        subscription_id=_entitlement_text(
            subscription_id,
            None,
        ),
        capability=(
            normalize_entitlement_capability(
                capability
            )
        ),
        mode=_entitlement_enum(
            EntitlementMode,
            mode,
            EntitlementMode.UNKNOWN,
        ),
        priority=_entitlement_enum(
            EntitlementPriority,
            priority,
            EntitlementPriority.NORMAL,
        ),
        requested=_entitlement_bool(
            requested,
            True,
        ),
        subscription_active=_entitlement_bool(
            subscription_active,
            False,
        ),
        valid_from=valid_from,
        valid_until=valid_until,
        source=_entitlement_enum(
            EntitlementSource,
            source,
            EntitlementSource.PLAN,
        ),
        admin_override=_entitlement_bool(
            admin_override,
            False,
        ),
        system_grant=_entitlement_bool(
            system_grant,
            False,
        ),
        metadata=dict(
            metadata or {}
        ),
        request_id=_entitlement_text(
            request_id,
            None,
        ),
    )


# ============================================================
# REFERENCE BUILDER
# ============================================================

def build_entitlement_reference(
    *,
    entitlement_id: str,
    user_id: str,
    capability: Any,
    plan_id: Optional[str] = None,
    subscription_id: Optional[str] = None,
    status: Any = EntitlementStatus.UNKNOWN,
    source: Any = EntitlementSource.UNKNOWN,
) -> EntitlementReference:

    return EntitlementReference(
        entitlement_id=_entitlement_text(
            entitlement_id
        ),
        user_id=_entitlement_text(
            user_id
        ),
        capability=(
            normalize_entitlement_capability(
                capability
            )
        ),
        plan_id=_entitlement_text(
            plan_id,
            None,
        ),
        subscription_id=_entitlement_text(
            subscription_id,
            None,
        ),
        status=_entitlement_enum(
            EntitlementStatus,
            status,
            EntitlementStatus.UNKNOWN,
        ),
        source=_entitlement_enum(
            EntitlementSource,
            source,
            EntitlementSource.UNKNOWN,
        ),
    )
# ============================================================
# ROBOMLM SUBSCRIPTION
# entitlement_service.py — PART 2
# ENTITLEMENT EVALUATION / READINESS / VALIDITY
# ============================================================


# ============================================================
# ENTITLEMENT DATA STATE
# ============================================================

class EntitlementDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    INVALID = "INVALID"


# ============================================================
# ENTITLEMENT CONSISTENCY
# ============================================================

class EntitlementConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONDITIONAL = "CONDITIONAL"
    INCONSISTENT = "INCONSISTENT"
    UNKNOWN = "UNKNOWN"


# ============================================================
# ENTITLEMENT READINESS
# ============================================================

class EntitlementReadiness(str, Enum):
    READY = "READY"
    CONDITIONALLY_READY = "CONDITIONALLY_READY"
    NOT_READY = "NOT_READY"
    BLOCKED = "BLOCKED"


# ============================================================
# ENTITLEMENT REQUIREMENTS
# ============================================================

@dataclass(frozen=True)
class EntitlementRequirements:
    require_user_id: bool = True
    require_capability: bool = True

    require_plan_or_subscription: bool = True

    require_active_subscription: bool = True

    require_validity_window: bool = False

    allow_admin_override: bool = True
    allow_system_grant: bool = True

    allow_expired: bool = False
    allow_revoked: bool = False


def build_entitlement_requirements(
    *,
    require_user_id: bool = True,
    require_capability: bool = True,
    require_plan_or_subscription: bool = True,
    require_active_subscription: bool = True,
    require_validity_window: bool = False,
    allow_admin_override: bool = True,
    allow_system_grant: bool = True,
    allow_expired: bool = False,
    allow_revoked: bool = False,
) -> EntitlementRequirements:

    return EntitlementRequirements(
        require_user_id=require_user_id,
        require_capability=require_capability,
        require_plan_or_subscription=(
            require_plan_or_subscription
        ),
        require_active_subscription=(
            require_active_subscription
        ),
        require_validity_window=(
            require_validity_window
        ),
        allow_admin_override=(
            allow_admin_override
        ),
        allow_system_grant=(
            allow_system_grant
        ),
        allow_expired=allow_expired,
        allow_revoked=allow_revoked,
    )


# ============================================================
# ENTITLEMENT ASSESSMENT
# ============================================================

@dataclass(frozen=True)
class EntitlementAssessment:
    data_state: EntitlementDataState
    consistency: EntitlementConsistency
    readiness: EntitlementReadiness

    completeness: float
    entitlement_quality: float
    confidence: float

    flags: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    unmet_requirements: Tuple[str, ...] = ()

    requested: bool = False
    subscription_active: bool = False

    currently_valid: bool = False
    expired: bool = False

    capability: str = ""

    source: EntitlementSource = (
        EntitlementSource.UNKNOWN
    )

    plan_id: Optional[str] = None
    subscription_id: Optional[str] = None

    notes: Tuple[str, ...] = ()


# ============================================================
# VALIDITY WINDOW
# ============================================================

def evaluate_entitlement_validity(
    request: EntitlementRequest,
    *,
    now: Optional[datetime] = None,
) -> Tuple[bool, bool]:

    current = (
        now
        if isinstance(now, datetime)
        else datetime.now(timezone.utc)
    )

    if (
        request.valid_from is not None
        and current < request.valid_from
    ):
        return False, False

    if (
        request.valid_until is not None
        and current > request.valid_until
    ):
        return False, True

    return True, False


# ============================================================
# DATA STATE
# ============================================================

def evaluate_entitlement_data_state(
    request: EntitlementRequest,
    requirements: EntitlementRequirements,
) -> EntitlementDataState:

    if not isinstance(
        request,
        EntitlementRequest,
    ):
        return EntitlementDataState.INVALID

    validation = validate_entitlement_request(
        request
    )

    if not validation.valid:
        return EntitlementDataState.INVALID

    missing = []

    if (
        requirements.require_user_id
        and not _entitlement_text(
            request.user_id
        )
    ):
        missing.append("user_id")

    if (
        requirements.require_capability
        and not _entitlement_text(
            request.capability
        )
    ):
        missing.append("capability")

    if (
        requirements.require_plan_or_subscription
        and not request.plan_id
        and not request.subscription_id
        and not request.admin_override
        and not request.system_grant
    ):
        missing.append(
            "plan_id_or_subscription_id"
        )

    if missing:
        return EntitlementDataState.PARTIAL

    return EntitlementDataState.COMPLETE


# ============================================================
# CONSISTENCY
# ============================================================

def evaluate_entitlement_consistency(
    request: EntitlementRequest,
    requirements: EntitlementRequirements,
) -> EntitlementConsistency:

    if not isinstance(
        request,
        EntitlementRequest,
    ):
        return EntitlementConsistency.INCONSISTENT

    validation = validate_entitlement_request(
        request
    )

    if not validation.valid:
        return EntitlementConsistency.INCONSISTENT

    if (
        request.admin_override
        and not requirements.allow_admin_override
    ):
        return EntitlementConsistency.INCONSISTENT

    if (
        request.system_grant
        and not requirements.allow_system_grant
    ):
        return EntitlementConsistency.INCONSISTENT

    if (
        request.admin_override
        and request.system_grant
    ):
        return EntitlementConsistency.CONDITIONAL

    if (
        request.source == EntitlementSource.ADMIN_OVERRIDE
        and not request.admin_override
    ):
        return EntitlementConsistency.CONDITIONAL

    if (
        request.source == EntitlementSource.SYSTEM
        and not request.system_grant
    ):
        return EntitlementConsistency.CONDITIONAL

    if (
        requirements.require_active_subscription
        and not request.subscription_active
        and not request.admin_override
        and not request.system_grant
    ):
        return EntitlementConsistency.CONDITIONAL

    return EntitlementConsistency.CONSISTENT


# ============================================================
# REQUIREMENT EVALUATION
# ============================================================

def evaluate_entitlement_requirements(
    request: EntitlementRequest,
    requirements: EntitlementRequirements,
) -> Tuple[str, ...]:

    unmet = []

    if (
        requirements.require_user_id
        and not _entitlement_text(
            request.user_id
        )
    ):
        unmet.append(
            "USER_ID_REQUIRED"
        )

    if (
        requirements.require_capability
        and not _entitlement_text(
            request.capability
        )
    ):
        unmet.append(
            "CAPABILITY_REQUIRED"
        )

    if (
        requirements.require_plan_or_subscription
        and not request.plan_id
        and not request.subscription_id
        and not request.admin_override
        and not request.system_grant
    ):
        unmet.append(
            "PLAN_OR_SUBSCRIPTION_REQUIRED"
        )

    if (
        requirements.require_active_subscription
        and not request.subscription_active
        and not request.admin_override
        and not request.system_grant
    ):
        unmet.append(
            "ACTIVE_SUBSCRIPTION_REQUIRED"
        )

    return tuple(unmet)


# ============================================================
# FLAGS
# ============================================================

def extract_entitlement_flags(
    request: EntitlementRequest,
    requirements: EntitlementRequirements,
    *,
    currently_valid: bool = True,
    expired: bool = False,
) -> Tuple[str, ...]:

    flags = []

    if not request.requested:
        flags.append(
            "ENTITLEMENT_NOT_REQUESTED"
        )

    if not request.subscription_active:
        flags.append(
            "SUBSCRIPTION_INACTIVE"
        )

    if not request.plan_id:
        if not request.admin_override:
            flags.append(
                "PLAN_ID_MISSING"
            )

    if not request.subscription_id:
        if not request.admin_override:
            flags.append(
                "SUBSCRIPTION_ID_MISSING"
            )

    if expired:
        flags.append(
            "ENTITLEMENT_EXPIRED"
        )

    elif not currently_valid:
        flags.append(
            "ENTITLEMENT_NOT_YET_VALID"
        )

    if request.admin_override:
        flags.append(
            "ADMIN_OVERRIDE_ACTIVE"
        )

    if request.system_grant:
        flags.append(
            "SYSTEM_GRANT_ACTIVE"
        )

    if (
        request.admin_override
        and request.system_grant
    ):
        flags.append(
            "MULTIPLE_GRANT_SOURCES"
        )

    return tuple(flags)


# ============================================================
# COMPLETENESS
# ============================================================

def calculate_entitlement_completeness(
    request: EntitlementRequest,
    requirements: EntitlementRequirements,
) -> float:

    checks = []

    if requirements.require_user_id:
        checks.append(
            bool(
                _entitlement_text(
                    request.user_id
                )
            )
        )

    if requirements.require_capability:
        checks.append(
            bool(
                _entitlement_text(
                    request.capability
                )
            )
        )

    if requirements.require_plan_or_subscription:
        checks.append(
            bool(
                request.plan_id
                or request.subscription_id
                or request.admin_override
                or request.system_grant
            )
        )

    if requirements.require_active_subscription:
        checks.append(
            bool(
                request.subscription_active
                or request.admin_override
                or request.system_grant
            )
        )

    if requirements.require_validity_window:
        checks.append(
            bool(
                request.valid_from
                or request.valid_until
            )
        )

    if not checks:
        return 100.0

    return round(
        100.0
        * sum(
            1
            for value in checks
            if value
        )
        / len(checks),
        2,
    )


# ============================================================
# READINESS
# ============================================================

def evaluate_entitlement_readiness(
    request: EntitlementRequest,
    requirements: EntitlementRequirements,
    data_state: EntitlementDataState,
    consistency: EntitlementConsistency,
    unmet: Tuple[str, ...],
    currently_valid: bool,
    expired: bool,
) -> EntitlementReadiness:

    if data_state == EntitlementDataState.INVALID:
        return EntitlementReadiness.BLOCKED

    if consistency == EntitlementConsistency.INCONSISTENT:
        return EntitlementReadiness.BLOCKED

    if not request.requested:
        return EntitlementReadiness.NOT_READY

    if expired and not requirements.allow_expired:
        return EntitlementReadiness.BLOCKED

    if unmet:
        return EntitlementReadiness.NOT_READY

    if (
        requirements.require_active_subscription
        and not request.subscription_active
        and not request.admin_override
        and not request.system_grant
    ):
        return EntitlementReadiness.NOT_READY

    if not currently_valid:
        return EntitlementReadiness.NOT_READY

    if consistency == EntitlementConsistency.CONDITIONAL:
        return EntitlementReadiness.CONDITIONALLY_READY

    if data_state == EntitlementDataState.PARTIAL:
        return EntitlementReadiness.CONDITIONALLY_READY

    return EntitlementReadiness.READY


# ============================================================
# ENTITLEMENT QUALITY
# ============================================================

def calculate_entitlement_quality(
    completeness: float,
    consistency: EntitlementConsistency,
    readiness: EntitlementReadiness,
) -> float:

    score = completeness

    if consistency == EntitlementConsistency.CONSISTENT:
        score += 10.0

    elif consistency == EntitlementConsistency.CONDITIONAL:
        score += 5.0

    if readiness == EntitlementReadiness.READY:
        score += 10.0

    elif readiness == EntitlementReadiness.CONDITIONALLY_READY:
        score += 5.0

    elif readiness == EntitlementReadiness.NOT_READY:
        score -= 15.0

    elif readiness == EntitlementReadiness.BLOCKED:
        score -= 35.0

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
# ENTITLEMENT CONFIDENCE
# ============================================================

def calculate_entitlement_confidence(
    completeness: float,
    consistency: EntitlementConsistency,
    readiness: EntitlementReadiness,
) -> float:

    confidence = completeness

    if consistency == EntitlementConsistency.INCONSISTENT:
        confidence -= 40.0

    elif consistency == EntitlementConsistency.CONDITIONAL:
        confidence -= 15.0

    if readiness == EntitlementReadiness.BLOCKED:
        confidence -= 30.0

    elif readiness == EntitlementReadiness.NOT_READY:
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
# ASSESSMENT BUILDER
# ============================================================

def build_entitlement_assessment(
    request: EntitlementRequest,
    requirements: Optional[
        EntitlementRequirements
    ] = None,
    *,
    now: Optional[datetime] = None,
) -> EntitlementAssessment:

    requirements = (
        requirements
        or build_entitlement_requirements()
    )

    data_state = (
        evaluate_entitlement_data_state(
            request,
            requirements,
        )
    )

    consistency = (
        evaluate_entitlement_consistency(
            request,
            requirements,
        )
    )

    currently_valid, expired = (
        evaluate_entitlement_validity(
            request,
            now=now,
        )
    )

    unmet = (
        evaluate_entitlement_requirements(
            request,
            requirements,
        )
    )

    readiness = (
        evaluate_entitlement_readiness(
            request,
            requirements,
            data_state,
            consistency,
            unmet,
            currently_valid,
            expired,
        )
    )

    completeness = (
        calculate_entitlement_completeness(
            request,
            requirements,
        )
    )

    flags = (
        extract_entitlement_flags(
            request,
            requirements,
            currently_valid=currently_valid,
            expired=expired,
        )
    )

    quality = (
        calculate_entitlement_quality(
            completeness,
            consistency,
            readiness,
        )
    )

    confidence = (
        calculate_entitlement_confidence(
            completeness,
            consistency,
            readiness,
        )
    )

    warnings = []

    if (
        request.admin_override
        and request.source
        != EntitlementSource.ADMIN_OVERRIDE
    ):
        warnings.append(
            "Admin override source mismatch."
        )

    if (
        request.system_grant
        and request.source
        != EntitlementSource.SYSTEM
    ):
        warnings.append(
            "System grant source mismatch."
        )

    if not request.subscription_active:
        if not request.admin_override:
            warnings.append(
                "Subscription is not active."
            )

    notes = [
        "Entitlement quality measures access-context "
        "quality, not market intelligence quality."
    ]

    notes.append(
        "Final feature entitlement resolution is "
        "performed by Entitlement Service."
    )

    notes.append(
        "Entitlement does not override D13, Risk, CAS, "
        "or execution authority."
    )

    return EntitlementAssessment(
        data_state=data_state,
        consistency=consistency,
        readiness=readiness,

        completeness=completeness,
        entitlement_quality=quality,
        confidence=confidence,

        flags=flags,
        warnings=tuple(warnings),
        unmet_requirements=unmet,

        requested=request.requested,
        subscription_active=(
            request.subscription_active
        ),

        currently_valid=currently_valid,
        expired=expired,

        capability=request.capability,

        source=request.source,

        plan_id=request.plan_id,
        subscription_id=request.subscription_id,

        notes=tuple(notes),
    )
# ============================================================
# ROBOMLM SUBSCRIPTION
# entitlement_service.py — PART 3
# ENTITLEMENT RESOLUTION ENGINE
# ============================================================


# ============================================================
# ENTITLEMENT RESULT
# ============================================================

@dataclass(frozen=True)
class EntitlementResult:
    decision: EntitlementDecision
    status: EntitlementStatus

    allowed: bool
    restricted: bool
    review_required: bool
    blocked: bool

    capability: str

    user_id: Optional[str] = None
    plan_id: Optional[str] = None
    subscription_id: Optional[str] = None

    source: EntitlementSource = (
        EntitlementSource.UNKNOWN
    )

    assessment: Optional[
        EntitlementAssessment
    ] = None

    flags: Tuple[str, ...] = ()
    restrictions: Tuple[str, ...] = ()
    errors: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()

    reason: str = ""

    timestamp: datetime = field(
        default_factory=_entitlement_timestamp
    )


# ============================================================
# ENTITLEMENT RESOLUTION RULES
# ============================================================

@dataclass(frozen=True)
class EntitlementResolutionRules:
    deny_without_active_subscription: bool = True

    allow_admin_override: bool = True
    allow_system_grant: bool = True

    require_plan_capability: bool = True

    expired_is_denied: bool = True
    revoked_is_denied: bool = True

    inactive_plan_is_denied: bool = True

    unknown_capability_is_denied: bool = True


def build_entitlement_resolution_rules(
    *,
    deny_without_active_subscription: bool = True,
    allow_admin_override: bool = True,
    allow_system_grant: bool = True,
    require_plan_capability: bool = True,
    expired_is_denied: bool = True,
    revoked_is_denied: bool = True,
    inactive_plan_is_denied: bool = True,
    unknown_capability_is_denied: bool = True,
) -> EntitlementResolutionRules:

    return EntitlementResolutionRules(
        deny_without_active_subscription=(
            deny_without_active_subscription
        ),
        allow_admin_override=(
            allow_admin_override
        ),
        allow_system_grant=(
            allow_system_grant
        ),
        require_plan_capability=(
            require_plan_capability
        ),
        expired_is_denied=expired_is_denied,
        revoked_is_denied=revoked_is_denied,
        inactive_plan_is_denied=(
            inactive_plan_is_denied
        ),
        unknown_capability_is_denied=(
            unknown_capability_is_denied
        ),
    )


# ============================================================
# PLAN CAPABILITY CHECK
# ============================================================

def plan_has_capability(
    plan: Any,
    capability: str,
) -> bool:

    if plan is None:
        return False

    normalized = (
        normalize_entitlement_capability(
            capability
        )
    )

    if not normalized:
        return False

    capabilities = getattr(
        plan,
        "capabilities",
        (),
    )

    normalized_capabilities = (
        normalize_entitlement_capabilities(
            capabilities
        )
    )

    return normalized in normalized_capabilities


# ============================================================
# PLAN STATUS CHECK
# ============================================================

def plan_is_entitlement_eligible(
    plan: Any,
) -> bool:

    if plan is None:
        return False

    status = getattr(
        plan,
        "status",
        None,
    )

    return status == EntitlementStatus.ACTIVE or (
        getattr(
            status,
            "value",
            status,
        ) == "ACTIVE"
    )


# ============================================================
# SUBSCRIPTION CONTEXT
# ============================================================

@dataclass(frozen=True)
class EntitlementSubscriptionContext:
    """
    Normalized subscription context supplied by
    Subscriber Service.

    Entitlement Service consumes this context.
    It does not own subscription lifecycle authority.
    """

    subscriber_id: Optional[str] = None
    subscription_id: Optional[str] = None
    user_id: Optional[str] = None
    plan_id: Optional[str] = None

    active: bool = False
    cancelled: bool = False
    expired: bool = False
    suspended: bool = False

    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )


def build_subscription_context(
    *,
    subscriber_id: Optional[str] = None,
    subscription_id: Optional[str] = None,
    user_id: Optional[str] = None,
    plan_id: Optional[str] = None,
    active: Any = False,
    cancelled: Any = False,
    expired: Any = False,
    suspended: Any = False,
    valid_from: Optional[datetime] = None,
    valid_until: Optional[datetime] = None,
    metadata: Optional[
        Mapping[str, Any]
    ] = None,
) -> EntitlementSubscriptionContext:

    return EntitlementSubscriptionContext(
        subscriber_id=_entitlement_text(
            subscriber_id,
            None,
        ),
        subscription_id=_entitlement_text(
            subscription_id,
            None,
        ),
        user_id=_entitlement_text(
            user_id,
            None,
        ),
        plan_id=_entitlement_text(
            plan_id,
            None,
        ),
        active=_entitlement_bool(
            active,
            False,
        ),
        cancelled=_entitlement_bool(
            cancelled,
            False,
        ),
        expired=_entitlement_bool(
            expired,
            False,
        ),
        suspended=_entitlement_bool(
            suspended,
            False,
        ),
        valid_from=valid_from,
        valid_until=valid_until,
        metadata=dict(
            metadata or {}
        ),
    )


# ============================================================
# SUBSCRIPTION CONTEXT VALIDATION
# ============================================================

def validate_subscription_context(
    context: EntitlementSubscriptionContext,
) -> Tuple[str, ...]:

    errors = []

    if not isinstance(
        context,
        EntitlementSubscriptionContext,
    ):
        return (
            "context must be EntitlementSubscriptionContext.",
        )

    if (
        context.valid_from is not None
        and context.valid_until is not None
        and context.valid_until
        < context.valid_from
    ):
        errors.append(
            "Subscription valid_until cannot be "
            "earlier than valid_from."
        )

    if (
        context.cancelled
        and context.active
    ):
        errors.append(
            "Subscription cannot be simultaneously "
            "cancelled and active."
        )

    if (
        context.expired
        and context.active
    ):
        errors.append(
            "Subscription cannot be simultaneously "
            "expired and active."
        )

    if (
        context.suspended
        and context.active
    ):
        errors.append(
            "Suspended subscription cannot be active."
        )

    return tuple(errors)


# ============================================================
# RESOLUTION FLAGS
# ============================================================

def collect_entitlement_resolution_flags(
    request: EntitlementRequest,
    assessment: EntitlementAssessment,
    context: Optional[
        EntitlementSubscriptionContext
    ],
    plan: Any,
) -> Tuple[str, ...]:

    flags = list(
        assessment.flags
    )

    if context is None:
        flags.append(
            "SUBSCRIPTION_CONTEXT_MISSING"
        )

    else:

        if not context.active:
            flags.append(
                "SUBSCRIPTION_NOT_ACTIVE"
            )

        if context.cancelled:
            flags.append(
                "SUBSCRIPTION_CANCELLED"
            )

        if context.expired:
            flags.append(
                "SUBSCRIPTION_EXPIRED"
            )

        if context.suspended:
            flags.append(
                "SUBSCRIPTION_SUSPENDED"
            )

    if plan is None:
        flags.append(
            "PLAN_NOT_FOUND"
        )

    else:
        status = getattr(
            plan,
            "status",
            None,
        )

        status_value = getattr(
            status,
            "value",
            status,
        )

        if status_value != "ACTIVE":
            flags.append(
                "PLAN_NOT_ACTIVE"
            )

        if not plan_has_capability(
            plan,
            request.capability,
        ):
            flags.append(
                "CAPABILITY_NOT_IN_PLAN"
            )

    return tuple(
        dict.fromkeys(flags)
    )


# ============================================================
# RESTRICTION COLLECTION
# ============================================================

def collect_entitlement_restrictions(
    request: EntitlementRequest,
    context: Optional[
        EntitlementSubscriptionContext
    ],
    plan: Any,
) -> Tuple[str, ...]:

    restrictions = []

    if context is not None:

        if context.suspended:
            restrictions.append(
                "SUBSCRIPTION_SUSPENDED"
            )

        if context.cancelled:
            restrictions.append(
                "SUBSCRIPTION_CANCELLED"
            )

    if plan is not None:

        if not plan_has_capability(
            plan,
            request.capability,
        ):
            restrictions.append(
                "CAPABILITY_NOT_ENTITLED"
            )

    if request.admin_override:
        restrictions.append(
            "ADMIN_OVERRIDE_PATH"
        )

    if request.system_grant:
        restrictions.append(
            "SYSTEM_GRANT_PATH"
        )

    return tuple(
        dict.fromkeys(
            restrictions
        )
    )


# ============================================================
# CORE RESOLUTION
# ============================================================

def resolve_entitlement(
    request: EntitlementRequest,
    *,
    plan: Any = None,
    subscription: Optional[
        EntitlementSubscriptionContext
    ] = None,
    requirements: Optional[
        EntitlementRequirements
    ] = None,
    rules: Optional[
        EntitlementResolutionRules
    ] = None,
    now: Optional[datetime] = None,
) -> EntitlementResult:

    requirements = (
        requirements
        or build_entitlement_requirements()
    )

    rules = (
        rules
        or build_entitlement_resolution_rules()
    )

    validation = validate_entitlement_request(
        request
    )

    if not validation.valid:

        return EntitlementResult(
            decision=EntitlementDecision.DENY,
            status=EntitlementStatus.BLOCKED,
            allowed=False,
            restricted=False,
            review_required=False,
            blocked=True,
            capability=request.capability,
            user_id=request.user_id,
            plan_id=request.plan_id,
            subscription_id=request.subscription_id,
            source=request.source,
            errors=validation.errors,
            warnings=validation.warnings,
            reason="Invalid entitlement request.",
        )

    assessment = build_entitlement_assessment(
        request,
        requirements,
        now=now,
    )

    flags = collect_entitlement_resolution_flags(
        request,
        assessment,
        subscription,
        plan,
    )

    restrictions = collect_entitlement_restrictions(
        request,
        subscription,
        plan,
    )

    errors = []

    if subscription is not None:
        errors.extend(
            validate_subscription_context(
                subscription
            )
        )

    # --------------------------------------------------------
    # HARD BLOCKS
    # --------------------------------------------------------

    if errors:

        return EntitlementResult(
            decision=EntitlementDecision.DENY,
            status=EntitlementStatus.BLOCKED,
            allowed=False,
            restricted=False,
            review_required=False,
            blocked=True,
            capability=request.capability,
            user_id=request.user_id,
            plan_id=request.plan_id,
            subscription_id=request.subscription_id,
            source=request.source,
            assessment=assessment,
            flags=flags,
            restrictions=restrictions,
            errors=tuple(errors),
            warnings=validation.warnings,
            reason="Invalid subscription context.",
        )

    if (
        request.admin_override
        and not rules.allow_admin_override
    ):

        return EntitlementResult(
            decision=EntitlementDecision.DENY,
            status=EntitlementStatus.BLOCKED,
            allowed=False,
            restricted=False,
            review_required=False,
            blocked=True,
            capability=request.capability,
            user_id=request.user_id,
            plan_id=request.plan_id,
            subscription_id=request.subscription_id,
            source=request.source,
            assessment=assessment,
            flags=flags,
            restrictions=restrictions,
            reason="Admin override is disabled.",
        )

    if (
        request.system_grant
        and not rules.allow_system_grant
    ):

        return EntitlementResult(
            decision=EntitlementDecision.DENY,
            status=EntitlementStatus.BLOCKED,
            allowed=False,
            restricted=False,
            review_required=False,
            blocked=True,
            capability=request.capability,
            user_id=request.user_id,
            plan_id=request.plan_id,
            subscription_id=request.subscription_id,
            source=request.source,
            assessment=assessment,
            flags=flags,
            restrictions=restrictions,
            reason="System grant is disabled.",
        )

    if not request.requested:

        return EntitlementResult(
            decision=EntitlementDecision.DENY,
            status=EntitlementStatus.INACTIVE,
            allowed=False,
            restricted=False,
            review_required=False,
            blocked=False,
            capability=request.capability,
            user_id=request.user_id,
            plan_id=request.plan_id,
            subscription_id=request.subscription_id,
            source=request.source,
            assessment=assessment,
            flags=flags,
            restrictions=restrictions,
            reason="Entitlement was not requested.",
        )

    if (
        assessment.expired
        and rules.expired_is_denied
    ):

        return EntitlementResult(
            decision=EntitlementDecision.DENY,
            status=EntitlementStatus.EXPIRED,
            allowed=False,
            restricted=False,
            review_required=False,
            blocked=True,
            capability=request.capability,
            user_id=request.user_id,
            plan_id=request.plan_id,
            subscription_id=request.subscription_id,
            source=request.source,
            assessment=assessment,
            flags=flags,
            restrictions=restrictions,
            reason="Entitlement validity period has expired.",
        )

    if (
        subscription is not None
        and (
            subscription.expired
            or subscription.cancelled
        )
        and rules.expired_is_denied
    ):

        return EntitlementResult(
            decision=EntitlementDecision.DENY,
            status=EntitlementStatus.EXPIRED,
            allowed=False,
            restricted=False,
            review_required=False,
            blocked=True,
            capability=request.capability,
            user_id=request.user_id,
            plan_id=request.plan_id,
            subscription_id=request.subscription_id,
            source=request.source,
            assessment=assessment,
            flags=flags,
            restrictions=restrictions,
            reason="Subscription is expired or cancelled.",
        )

    # --------------------------------------------------------
    # ADMIN / SYSTEM AUTHORIZED PATH
    # --------------------------------------------------------

    if request.admin_override:

        return EntitlementResult(
            decision=EntitlementDecision.ALLOW,
            status=EntitlementStatus.ACTIVE,
            allowed=True,
            restricted=False,
            review_required=False,
            blocked=False,
            capability=request.capability,
            user_id=request.user_id,
            plan_id=request.plan_id,
            subscription_id=request.subscription_id,
            source=EntitlementSource.ADMIN_OVERRIDE,
            assessment=assessment,
            flags=flags,
            restrictions=restrictions,
            reason="Entitlement allowed through authorized admin override.",
        )

    if request.system_grant:

        return EntitlementResult(
            decision=EntitlementDecision.ALLOW,
            status=EntitlementStatus.ACTIVE,
            allowed=True,
            restricted=False,
            review_required=False,
            blocked=False,
            capability=request.capability,
            user_id=request.user_id,
            plan_id=request.plan_id,
            subscription_id=request.subscription_id,
            source=EntitlementSource.SYSTEM,
            assessment=assessment,
            flags=flags,
            restrictions=restrictions,
            reason="Entitlement allowed through authorized system grant.",
        )

    # --------------------------------------------------------
    # SUBSCRIPTION REQUIRED
    # --------------------------------------------------------

    if (
        rules.deny_without_active_subscription
        and (
            subscription is None
            or not subscription.active
        )
    ):

        return EntitlementResult(
            decision=EntitlementDecision.DENY,
            status=EntitlementStatus.INACTIVE,
            allowed=False,
            restricted=False,
            review_required=False,
            blocked=True,
            capability=request.capability,
            user_id=request.user_id,
            plan_id=request.plan_id,
            subscription_id=request.subscription_id,
            source=EntitlementSource.SUBSCRIPTION,
            assessment=assessment,
            flags=flags,
            restrictions=restrictions,
            reason="Active subscription is required.",
        )

    # --------------------------------------------------------
    # PLAN REQUIRED
    # --------------------------------------------------------

    if (
        rules.require_plan_capability
        and plan is None
    ):

        return EntitlementResult(
            decision=EntitlementDecision.DENY,
            status=EntitlementStatus.BLOCKED,
            allowed=False,
            restricted=False,
            review_required=False,
            blocked=True,
            capability=request.capability,
            user_id=request.user_id,
            plan_id=request.plan_id,
            subscription_id=request.subscription_id,
            source=EntitlementSource.PLAN,
            assessment=assessment,
            flags=flags,
            restrictions=restrictions,
            reason="Entitled plan could not be resolved.",
        )

    # --------------------------------------------------------
    # PLAN STATUS
    # --------------------------------------------------------

    if (
        plan is not None
        and rules.inactive_plan_is_denied
        and not plan_is_entitlement_eligible(
            plan
        )
    ):

        return EntitlementResult(
            decision=EntitlementDecision.DENY,
            status=EntitlementStatus.INACTIVE,
            allowed=False,
            restricted=False,
            review_required=False,
            blocked=True,
            capability=request.capability,
            user_id=request.user_id,
            plan_id=request.plan_id,
            subscription_id=request.subscription_id,
            source=EntitlementSource.PLAN,
            assessment=assessment,
            flags=flags,
            restrictions=restrictions,
            reason="Plan is not active.",
        )

    # --------------------------------------------------------
    # CAPABILITY
    # --------------------------------------------------------

    if (
        plan is not None
        and rules.require_plan_capability
        and not plan_has_capability(
            plan,
            request.capability,
        )
    ):

        if rules.unknown_capability_is_denied:

            return EntitlementResult(
                decision=EntitlementDecision.DENY,
                status=EntitlementStatus.INACTIVE,
                allowed=False,
                restricted=False,
                review_required=False,
                blocked=True,
                capability=request.capability,
                user_id=request.user_id,
                plan_id=request.plan_id,
                subscription_id=request.subscription_id,
                source=EntitlementSource.PLAN,
                assessment=assessment,
                flags=flags,
                restrictions=restrictions,
                reason="Capability is not included in the plan.",
            )

    # --------------------------------------------------------
    # FINAL ALLOW
    # --------------------------------------------------------

    return EntitlementResult(
        decision=EntitlementDecision.ALLOW,
        status=EntitlementStatus.ACTIVE,
        allowed=True,
        restricted=False,
        review_required=False,
        blocked=False,
        capability=request.capability,
        user_id=request.user_id,
        plan_id=request.plan_id,
        subscription_id=request.subscription_id,
        source=EntitlementSource.SUBSCRIPTION,
        assessment=assessment,
        flags=flags,
        restrictions=restrictions,
        warnings=validation.warnings,
        reason="Entitlement validated and allowed.",
    )
# ============================================================
# ROBOMLM SUBSCRIPTION
# entitlement_service.py — PART 4
# ENTITLEMENT REGISTRY / ADMINISTRATION / LIFECYCLE
# ============================================================

@dataclass(frozen=True)
class EntitlementAdminRequest:
    action: str
    entitlement_id: Optional[str] = None
    user_id: Optional[str] = None
    account_id: Optional[str] = None
    plan_id: Optional[str] = None
    subscription_id: Optional[str] = None
    capability: str = ""
    admin_id: Optional[str] = None
    reason: str = ""
    source: EntitlementSource = EntitlementSource.ADMIN_OVERRIDE
    status: EntitlementStatus = EntitlementStatus.ACTIVE
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    request_id: Optional[str] = None
    timestamp: datetime = field(default_factory=_entitlement_timestamp)


@dataclass(frozen=True)
class EntitlementAdminResult:
    success: bool
    changed: bool
    action: str
    entitlement_id: Optional[str] = None
    previous: Optional[EntitlementReference] = None
    current: Optional[EntitlementReference] = None
    errors: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    reason: str = ""
    timestamp: datetime = field(default_factory=_entitlement_timestamp)


@dataclass(frozen=True)
class EntitlementRegistryEntry:
    entitlement: EntitlementReference
    revision: int = 1
    updated_by: Optional[str] = None
    updated_at: datetime = field(default_factory=_entitlement_timestamp)


@dataclass(frozen=True)
class EntitlementRegistrySnapshot:
    total: int
    active: int
    inactive: int
    expired: int
    revoked: int
    blocked: int
    pending: int
    entitlements: Tuple[EntitlementReference, ...] = ()
    timestamp: datetime = field(default_factory=_entitlement_timestamp)


def _entitlement_admin_action(value: Any) -> str:
    return _entitlement_text(value).upper()


ENTITLEMENT_ADMIN_ACTIONS = frozenset({
    "GRANT",
    "ACTIVATE",
    "DEACTIVATE",
    "REVOKE",
    "BLOCK",
    "UNBLOCK",
    "UPDATE",
})


def validate_entitlement_admin_request(
    request: EntitlementAdminRequest,
) -> Tuple[str, ...]:
    errors = []

    if not isinstance(request, EntitlementAdminRequest):
        return ("request must be EntitlementAdminRequest.",)

    action = _entitlement_admin_action(request.action)

    if action not in ENTITLEMENT_ADMIN_ACTIONS:
        errors.append(f"Unsupported entitlement admin action: {action}.")

    if not _entitlement_text(request.admin_id):
        errors.append("admin_id is required.")

    if action in {"GRANT", "ACTIVATE", "UPDATE"}:
        if not _entitlement_text(request.user_id):
            errors.append("user_id is required.")
        if not _entitlement_text(request.capability):
            errors.append("capability is required.")

    if action == "GRANT":
        if not _entitlement_text(request.entitlement_id):
            errors.append("entitlement_id is required for GRANT.")

    if action in {
        "ACTIVATE",
        "DEACTIVATE",
        "REVOKE",
        "BLOCK",
        "UNBLOCK",
        "UPDATE",
    }:
        if not _entitlement_text(request.entitlement_id):
            errors.append(
                f"entitlement_id is required for {action}."
            )

    if not _entitlement_text(request.reason):
        errors.append("Administrative reason is required.")

    if (
        request.valid_from is not None
        and request.valid_until is not None
        and request.valid_until < request.valid_from
    ):
        errors.append(
            "valid_until cannot be earlier than valid_from."
        )

    return tuple(errors)


def build_admin_entitlement_reference(
    request: EntitlementAdminRequest,
) -> EntitlementReference:
    return EntitlementReference(
        entitlement_id=_entitlement_text(request.entitlement_id),
        user_id=_entitlement_text(request.user_id),
        capability=normalize_entitlement_capability(
            request.capability
        ),
        plan_id=_entitlement_text(request.plan_id) or None,
        subscription_id=(
            _entitlement_text(request.subscription_id) or None
        ),
        status=_entitlement_enum(
            EntitlementStatus,
            request.status,
            EntitlementStatus.ACTIVE,
        ),
        source=_entitlement_enum(
            EntitlementSource,
            request.source,
            EntitlementSource.ADMIN_OVERRIDE,
        ),
    )


def _entitlement_reference_with_status(
    reference: EntitlementReference,
    status: EntitlementStatus,
) -> EntitlementReference:
    return EntitlementReference(
        entitlement_id=reference.entitlement_id,
        user_id=reference.user_id,
        capability=reference.capability,
        plan_id=reference.plan_id,
        subscription_id=reference.subscription_id,
        status=status,
        source=reference.source,
        version=reference.version,
        created_at=reference.created_at,
    )


class EntitlementRegistry:
    """
    Authoritative in-process registry for resolved entitlement state.

    This registry stores ACCESS STATE only.
    It does not become a market-decision, risk, CAS, or execution authority.
    """

    def __init__(self) -> None:
        self._entries: dict[str, EntitlementRegistryEntry] = {}

    def exists(self, entitlement_id: str) -> bool:
        return _entitlement_text(entitlement_id) in self._entries

    def get(
        self,
        entitlement_id: str,
    ) -> Optional[EntitlementReference]:
        entry = self._entries.get(
            _entitlement_text(entitlement_id)
        )
        return entry.entitlement if entry else None

    def get_entry(
        self,
        entitlement_id: str,
    ) -> Optional[EntitlementRegistryEntry]:
        return self._entries.get(
            _entitlement_text(entitlement_id)
        )

    def add(
        self,
        entitlement: EntitlementReference,
        updated_by: Optional[str] = None,
    ) -> EntitlementRegistryEntry:
        if not validate_entitlement_reference(entitlement):
            raise ValueError("Invalid entitlement reference.")

        if self.exists(entitlement.entitlement_id):
            raise ValueError(
                f"Entitlement already exists: "
                f"{entitlement.entitlement_id}"
            )

        entry = EntitlementRegistryEntry(
            entitlement=entitlement,
            revision=1,
            updated_by=updated_by,
        )
        self._entries[entitlement.entitlement_id] = entry
        return entry

    def replace(
        self,
        entitlement: EntitlementReference,
        updated_by: Optional[str] = None,
    ) -> EntitlementRegistryEntry:
        if not validate_entitlement_reference(entitlement):
            raise ValueError("Invalid entitlement reference.")

        previous = self._entries.get(entitlement.entitlement_id)
        revision = (
            previous.revision + 1
            if previous is not None
            else 1
        )

        entry = EntitlementRegistryEntry(
            entitlement=entitlement,
            revision=revision,
            updated_by=updated_by,
        )

        self._entries[entitlement.entitlement_id] = entry
        return entry

    def remove(
        self,
        entitlement_id: str,
    ) -> bool:
        return (
            self._entries.pop(
                _entitlement_text(entitlement_id),
                None,
            )
            is not None
        )

    def list_entitlements(
        self,
        *,
        user_id: Optional[str] = None,
        capability: Optional[str] = None,
        status: Optional[EntitlementStatus] = None,
    ) -> Tuple[EntitlementReference, ...]:
        normalized_user = _entitlement_text(user_id)
        normalized_capability = (
            normalize_entitlement_capability(capability)
            if capability
            else ""
        )

        values = []

        for entry in self._entries.values():
            item = entry.entitlement

            if normalized_user and item.user_id != normalized_user:
                continue

            if (
                normalized_capability
                and item.capability != normalized_capability
            ):
                continue

            if status is not None and item.status != status:
                continue

            values.append(item)

        values.sort(key=lambda x: x.entitlement_id)
        return tuple(values)

    def snapshot(self) -> EntitlementRegistrySnapshot:
        items = tuple(
            entry.entitlement
            for entry in self._entries.values()
        )

        counts = {
            EntitlementStatus.ACTIVE: 0,
            EntitlementStatus.INACTIVE: 0,
            EntitlementStatus.EXPIRED: 0,
            EntitlementStatus.REVOKED: 0,
            EntitlementStatus.BLOCKED: 0,
            EntitlementStatus.PENDING: 0,
        }

        for item in items:
            if item.status in counts:
                counts[item.status] += 1

        return EntitlementRegistrySnapshot(
            total=len(items),
            active=counts[EntitlementStatus.ACTIVE],
            inactive=counts[EntitlementStatus.INACTIVE],
            expired=counts[EntitlementStatus.EXPIRED],
            revoked=counts[EntitlementStatus.REVOKED],
            blocked=counts[EntitlementStatus.BLOCKED],
            pending=counts[EntitlementStatus.PENDING],
            entitlements=tuple(
                sorted(
                    items,
                    key=lambda x: x.entitlement_id,
                )
            ),
        )

    def count(self) -> int:
        return len(self._entries)


def _admin_mutation_result(
    *,
    success: bool,
    changed: bool,
    action: str,
    entitlement_id: Optional[str],
    previous: Optional[EntitlementReference],
    current: Optional[EntitlementReference],
    errors: Tuple[str, ...] = (),
    warnings: Tuple[str, ...] = (),
    reason: str = "",
) -> EntitlementAdminResult:
    return EntitlementAdminResult(
        success=success,
        changed=changed,
        action=action,
        entitlement_id=entitlement_id,
        previous=previous,
        current=current,
        errors=errors,
        warnings=warnings,
        reason=reason,
    )


def grant_entitlement(
    registry: EntitlementRegistry,
    request: EntitlementAdminRequest,
) -> EntitlementAdminResult:
    errors = validate_entitlement_admin_request(request)

    if errors:
        return _admin_mutation_result(
            success=False,
            changed=False,
            action="GRANT",
            entitlement_id=request.entitlement_id,
            previous=None,
            current=None,
            errors=errors,
        )

    entitlement = build_admin_entitlement_reference(request)

    if registry.exists(entitlement.entitlement_id):
        return _admin_mutation_result(
            success=False,
            changed=False,
            action="GRANT",
            entitlement_id=entitlement.entitlement_id,
            previous=registry.get(entitlement.entitlement_id),
            current=None,
            errors=("Entitlement already exists.",),
        )

    registry.add(
        entitlement,
        updated_by=request.admin_id,
    )

    return _admin_mutation_result(
        success=True,
        changed=True,
        action="GRANT",
        entitlement_id=entitlement.entitlement_id,
        previous=None,
        current=entitlement,
        reason=request.reason,
    )


def update_entitlement_status(
    registry: EntitlementRegistry,
    request: EntitlementAdminRequest,
    status: EntitlementStatus,
) -> EntitlementAdminResult:
    errors = validate_entitlement_admin_request(request)

    if errors:
        return _admin_mutation_result(
            success=False,
            changed=False,
            action=_entitlement_admin_action(request.action),
            entitlement_id=request.entitlement_id,
            previous=None,
            current=None,
            errors=errors,
        )

    entitlement_id = _entitlement_text(request.entitlement_id)
    previous = registry.get(entitlement_id)

    if previous is None:
        return _admin_mutation_result(
            success=False,
            changed=False,
            action=_entitlement_admin_action(request.action),
            entitlement_id=entitlement_id,
            previous=None,
            current=None,
            errors=("Entitlement not found.",),
        )

    current = _entitlement_reference_with_status(
        previous,
        status,
    )

    changed = current.status != previous.status

    if changed:
        registry.replace(
            current,
            updated_by=request.admin_id,
        )

    return _admin_mutation_result(
        success=True,
        changed=changed,
        action=_entitlement_admin_action(request.action),
        entitlement_id=entitlement_id,
        previous=previous,
        current=current,
        reason=request.reason,
    )


def activate_entitlement(
    registry: EntitlementRegistry,
    request: EntitlementAdminRequest,
) -> EntitlementAdminResult:
    return update_entitlement_status(
        registry,
        request,
        EntitlementStatus.ACTIVE,
    )


def deactivate_entitlement(
    registry: EntitlementRegistry,
    request: EntitlementAdminRequest,
) -> EntitlementAdminResult:
    return update_entitlement_status(
        registry,
        request,
        EntitlementStatus.INACTIVE,
    )


def revoke_entitlement(
    registry: EntitlementRegistry,
    request: EntitlementAdminRequest,
) -> EntitlementAdminResult:
    return update_entitlement_status(
        registry,
        request,
        EntitlementStatus.REVOKED,
    )


def block_entitlement(
    registry: EntitlementRegistry,
    request: EntitlementAdminRequest,
) -> EntitlementAdminResult:
    return update_entitlement_status(
        registry,
        request,
        EntitlementStatus.BLOCKED,
    )


def unblock_entitlement(
    registry: EntitlementRegistry,
    request: EntitlementAdminRequest,
) -> EntitlementAdminResult:
    return update_entitlement_status(
        registry,
        request,
        EntitlementStatus.ACTIVE,
    )


def validate_entitlement_registry(
    registry: EntitlementRegistry,
) -> Tuple[str, ...]:
    errors = []

    if not isinstance(registry, EntitlementRegistry):
        return ("registry must be EntitlementRegistry.",)

    seen = set()

    for entitlement in registry.list_entitlements():
        entitlement_id = entitlement.entitlement_id

        if entitlement_id in seen:
            errors.append(
                f"Duplicate entitlement_id: {entitlement_id}"
            )
        seen.add(entitlement_id)

        if not validate_entitlement_reference(entitlement):
            errors.append(
                f"Invalid entitlement reference: {entitlement_id}"
            )

    return tuple(errors)


def entitlement_registry_health(
    registry: EntitlementRegistry,
) -> Mapping[str, Any]:
    errors = validate_entitlement_registry(registry)
    snapshot = registry.snapshot()

    return {
        "engine": ENTITLEMENT_SERVICE_ENGINE,
        "version": ENTITLEMENT_SERVICE_VERSION,
        "healthy": not errors,
        "registry_count": snapshot.total,
        "active": snapshot.active,
        "inactive": snapshot.inactive,
        "expired": snapshot.expired,
        "revoked": snapshot.revoked,
        "blocked": snapshot.blocked,
        "pending": snapshot.pending,
        "errors": errors,
        "timestamp": _entitlement_timestamp(),
    }


def entitlement_authority_boundary() -> Mapping[str, bool]:
    return {
        "feature_access_authority": True,
        "market_decision_authority": False,
        "d13_decision_override": False,
        "risk_override": False,
        "cas_override": False,
        "execution_authority": False,
        "order_authority": False,
        "position_authority": False,
    }


def validate_entitlement_authority_boundary() -> bool:
    boundary = entitlement_authority_boundary()

    forbidden = (
        "market_decision_authority",
        "d13_decision_override",
        "risk_override",
        "cas_override",
        "execution_authority",
        "order_authority",
        "position_authority",
    )

    return all(boundary.get(key) is False for key in forbidden)
# ============================================================
# ROBOMLM SUBSCRIPTION
# entitlement_service.py — PART 5
# SERVICE FACADE / SERIALIZATION / INTEGRITY / PUBLIC API
# ============================================================


def serialize_entitlement_reference(
    reference: Optional[EntitlementReference],
) -> Mapping[str, Any]:
    if reference is None:
        return {}

    return {
        "entitlement_id": reference.entitlement_id,
        "user_id": reference.user_id,
        "capability": reference.capability,
        "plan_id": reference.plan_id,
        "subscription_id": reference.subscription_id,
        "status": reference.status.value,
        "source": reference.source.value,
        "version": reference.version,
        "created_at": reference.created_at.isoformat(),
    }


def serialize_entitlement_assessment(
    assessment: Optional[EntitlementAssessment],
) -> Mapping[str, Any]:
    if assessment is None:
        return {}

    return {
        "data_state": assessment.data_state.value,
        "consistency": assessment.consistency.value,
        "readiness": assessment.readiness.value,
        "completeness": assessment.completeness,
        "entitlement_quality": assessment.entitlement_quality,
        "confidence": assessment.confidence,
        "flags": list(assessment.flags),
        "warnings": list(assessment.warnings),
        "unmet_requirements": list(
            assessment.unmet_requirements
        ),
        "requested": assessment.requested,
        "subscription_active": assessment.subscription_active,
        "currently_valid": assessment.currently_valid,
        "expired": assessment.expired,
        "capability": assessment.capability,
        "source": assessment.source.value,
        "plan_id": assessment.plan_id,
        "subscription_id": assessment.subscription_id,
        "notes": list(assessment.notes),
    }


def serialize_entitlement_result(
    result: Optional[EntitlementResult],
) -> Mapping[str, Any]:
    if result is None:
        return {}

    return {
        "decision": result.decision.value,
        "status": result.status.value,
        "allowed": result.allowed,
        "restricted": result.restricted,
        "review_required": result.review_required,
        "blocked": result.blocked,
        "capability": result.capability,
        "user_id": result.user_id,
        "plan_id": result.plan_id,
        "subscription_id": result.subscription_id,
        "source": result.source.value,
        "assessment": serialize_entitlement_assessment(
            result.assessment
        ),
        "flags": list(result.flags),
        "restrictions": list(result.restrictions),
        "errors": list(result.errors),
        "warnings": list(result.warnings),
        "reason": result.reason,
        "timestamp": result.timestamp.isoformat(),
    }


def serialize_entitlement_admin_result(
    result: Optional[EntitlementAdminResult],
) -> Mapping[str, Any]:
    if result is None:
        return {}

    return {
        "success": result.success,
        "changed": result.changed,
        "action": result.action,
        "entitlement_id": result.entitlement_id,
        "previous": serialize_entitlement_reference(
            result.previous
        ),
        "current": serialize_entitlement_reference(
            result.current
        ),
        "errors": list(result.errors),
        "warnings": list(result.warnings),
        "reason": result.reason,
        "timestamp": result.timestamp.isoformat(),
    }


def serialize_entitlement_snapshot(
    snapshot: EntitlementRegistrySnapshot,
) -> Mapping[str, Any]:
    return {
        "total": snapshot.total,
        "active": snapshot.active,
        "inactive": snapshot.inactive,
        "expired": snapshot.expired,
        "revoked": snapshot.revoked,
        "blocked": snapshot.blocked,
        "pending": snapshot.pending,
        "entitlements": [
            serialize_entitlement_reference(item)
            for item in snapshot.entitlements
        ],
        "timestamp": snapshot.timestamp.isoformat(),
    }


def validate_entitlement_integrity(
    entitlement: Optional[EntitlementReference],
) -> Tuple[str, ...]:
    errors = []

    if entitlement is None:
        return ("entitlement is required.",)

    if not validate_entitlement_reference(entitlement):
        errors.append(
            "Invalid entitlement reference."
        )

    if entitlement.status == EntitlementStatus.ACTIVE:
        if not _entitlement_text(entitlement.user_id):
            errors.append(
                "Active entitlement requires user_id."
            )

        if not _entitlement_text(entitlement.capability):
            errors.append(
                "Active entitlement requires capability."
            )

    if entitlement.source == EntitlementSource.ADMIN_OVERRIDE:
        if not entitlement.plan_id and not entitlement.subscription_id:
            # Explicit admin override may legitimately exist
            # without a plan/subscription.
            pass

    return tuple(errors)


def validate_entitlement_snapshot_integrity(
    snapshot: Optional[EntitlementRegistrySnapshot],
) -> Tuple[str, ...]:
    errors = []

    if snapshot is None:
        return ("snapshot is required.",)

    if snapshot.total < 0:
        errors.append("snapshot.total cannot be negative.")

    calculated = (
        snapshot.active
        + snapshot.inactive
        + snapshot.expired
        + snapshot.revoked
        + snapshot.blocked
        + snapshot.pending
    )

    if calculated != snapshot.total:
        errors.append(
            "Snapshot status counts do not match total."
        )

    if len(snapshot.entitlements) != snapshot.total:
        errors.append(
            "Snapshot entitlement count does not match total."
        )

    seen = set()

    for entitlement in snapshot.entitlements:
        errors.extend(
            validate_entitlement_integrity(entitlement)
        )

        if entitlement.entitlement_id in seen:
            errors.append(
                f"Duplicate entitlement_id: "
                f"{entitlement.entitlement_id}"
            )

        seen.add(entitlement.entitlement_id)

    return tuple(errors)


def build_entitlement_summary(
    result: Optional[EntitlementResult] = None,
    *,
    registry: Optional[EntitlementRegistry] = None,
) -> Mapping[str, Any]:
    summary: dict[str, Any] = {
        "engine": ENTITLEMENT_SERVICE_ENGINE,
        "version": ENTITLEMENT_SERVICE_VERSION,
    }

    if result is not None:
        summary.update({
            "decision": result.decision.value,
            "status": result.status.value,
            "allowed": result.allowed,
            "restricted": result.restricted,
            "review_required": result.review_required,
            "blocked": result.blocked,
            "capability": result.capability,
            "user_id": result.user_id,
            "plan_id": result.plan_id,
            "subscription_id": result.subscription_id,
            "flags": list(result.flags),
            "restrictions": list(result.restrictions),
            "reason": result.reason,
        })

    if registry is not None:
        snapshot = registry.snapshot()
        summary["registry"] = serialize_entitlement_snapshot(
            snapshot
        )

    summary["timestamp"] = _entitlement_timestamp().isoformat()
    return summary


class EntitlementService:
    """
    Application-facing entitlement service.

    Responsibilities:
      1. Resolve feature access.
      2. Maintain entitlement registry state.
      3. Apply explicit administrative lifecycle changes.
      4. Expose auditable access contracts.

    Non-responsibilities:
      - market decisions
      - D13 decisions
      - risk authorization
      - CAS override
      - trade execution
      - order routing
      - position management
    """

    def __init__(
        self,
        registry: Optional[EntitlementRegistry] = None,
    ) -> None:
        self.registry = (
            registry
            if registry is not None
            else EntitlementRegistry()
        )

    def resolve(
        self,
        request: EntitlementRequest,
        *,
        plan: Any = None,
        subscription: Any = None,
        requirements: Optional[
            EntitlementRequirements
        ] = None,
        rules: Optional[
            EntitlementResolutionRules
        ] = None,
        now: Optional[datetime] = None,
    ) -> EntitlementResult:
        return resolve_entitlement(
            request,
            plan=plan,
            subscription=subscription,
            requirements=requirements,
            rules=rules,
            now=now,
        )

    def grant(
        self,
        request: EntitlementAdminRequest,
    ) -> EntitlementAdminResult:
        return grant_entitlement(
            self.registry,
            request,
        )

    def activate(
        self,
        request: EntitlementAdminRequest,
    ) -> EntitlementAdminResult:
        return activate_entitlement(
            self.registry,
            request,
        )

    def deactivate(
        self,
        request: EntitlementAdminRequest,
    ) -> EntitlementAdminResult:
        return deactivate_entitlement(
            self.registry,
            request,
        )

    def revoke(
        self,
        request: EntitlementAdminRequest,
    ) -> EntitlementAdminResult:
        return revoke_entitlement(
            self.registry,
            request,
        )

    def block(
        self,
        request: EntitlementAdminRequest,
    ) -> EntitlementAdminResult:
        return block_entitlement(
            self.registry,
            request,
        )

    def unblock(
        self,
        request: EntitlementAdminRequest,
    ) -> EntitlementAdminResult:
        return unblock_entitlement(
            self.registry,
            request,
        )

    def get(
        self,
        entitlement_id: str,
    ) -> Optional[EntitlementReference]:
        return self.registry.get(entitlement_id)

    def list(
        self,
        *,
        user_id: Optional[str] = None,
        capability: Optional[str] = None,
        status: Optional[EntitlementStatus] = None,
    ) -> Tuple[EntitlementReference, ...]:
        return self.registry.list_entitlements(
            user_id=user_id,
            capability=capability,
            status=status,
        )

    def snapshot(self) -> EntitlementRegistrySnapshot:
        return self.registry.snapshot()

    def health(self) -> Mapping[str, Any]:
        return entitlement_registry_health(
            self.registry
        )

    def integrity(self) -> Tuple[str, ...]:
        return validate_entitlement_registry(
            self.registry
        )

    def info(self) -> Mapping[str, Any]:
        return {
            "engine": ENTITLEMENT_SERVICE_ENGINE,
            "version": ENTITLEMENT_SERVICE_VERSION,
            "authority": entitlement_authority_boundary(),
            "registry_count": self.registry.count(),
            "timestamp": _entitlement_timestamp(),
        }


_ENTITLEMENT_SERVICE = EntitlementService()


def get_entitlement_service() -> EntitlementService:
    return _ENTITLEMENT_SERVICE


def resolve_feature_access(
    request: EntitlementRequest,
    *,
    plan: Any = None,
    subscription: Any = None,
    requirements: Optional[
        EntitlementRequirements
    ] = None,
    rules: Optional[
        EntitlementResolutionRules
    ] = None,
    now: Optional[datetime] = None,
) -> EntitlementResult:
    return _ENTITLEMENT_SERVICE.resolve(
        request,
        plan=plan,
        subscription=subscription,
        requirements=requirements,
        rules=rules,
        now=now,
    )


def entitlement_count() -> int:
    return _ENTITLEMENT_SERVICE.registry.count()


def entitlement_snapshot() -> EntitlementRegistrySnapshot:
    return _ENTITLEMENT_SERVICE.snapshot()


def entitlement_health() -> Mapping[str, Any]:
    return _ENTITLEMENT_SERVICE.health()


def entitlement_operational_check() -> bool:
    service = get_entitlement_service()

    if not validate_entitlement_authority_boundary():
        return False

    if service.integrity():
        return False

    return True


def entitlement_service_info() -> Mapping[str, Any]:
    return get_entitlement_service().info()


__all__ = [
    # Constants
    "ENTITLEMENT_SERVICE_ENGINE",
    "ENTITLEMENT_SERVICE_VERSION",

    # Enums
    "EntitlementStatus",
    "EntitlementDecision",
    "EntitlementMode",
    "EntitlementPriority",
    "EntitlementContractStatus",
    "EntitlementSource",
    "EntitlementCapability",

    # Foundation contracts
    "EntitlementRequest",
    "EntitlementReference",
    "EntitlementContractValidation",

    # Assessment
    "EntitlementDataState",
    "EntitlementConsistency",
    "EntitlementReadiness",
    "EntitlementRequirements",
    "EntitlementAssessment",

    # Resolution
    "EntitlementResult",
    "EntitlementResolutionRules",
    "EntitlementSubscriptionContext",

    # Administration
    "EntitlementAdminRequest",
    "EntitlementAdminResult",

    # Registry
    "EntitlementRegistryEntry",
    "EntitlementRegistrySnapshot",
    "EntitlementRegistry",

    # Normalization / validation
    "normalize_entitlement_capability",
    "normalize_entitlement_capabilities",
    "validate_entitlement_request",
    "validate_entitlement_reference",
    "validate_subscription_context",

    # Assessment / resolution
    "evaluate_entitlement_validity",
    "evaluate_entitlement_data_state",
    "evaluate_entitlement_consistency",
    "evaluate_entitlement_requirements",
    "evaluate_entitlement_flags",
    "evaluate_entitlement_completeness",
    "evaluate_entitlement_readiness",
    "evaluate_entitlement_quality",
    "evaluate_entitlement_confidence",
    "build_entitlement_assessment",
    "build_entitlement_resolution_rules",
    "plan_has_capability",
    "plan_is_entitlement_eligible",
    "build_subscription_context",
    "collect_entitlement_resolution_flags",
    "collect_entitlement_restrictions",
    "resolve_entitlement",

    # Administration
    "validate_entitlement_admin_request",
    "build_admin_entitlement_reference",
    "grant_entitlement",
    "activate_entitlement",
    "deactivate_entitlement",
    "revoke_entitlement",
    "block_entitlement",
    "unblock_entitlement",

    # Registry
    "validate_entitlement_registry",
    "entitlement_registry_health",

    # Serialization / integrity
    "serialize_entitlement_reference",
    "serialize_entitlement_assessment",
    "serialize_entitlement_result",
    "serialize_entitlement_admin_result",
    "serialize_entitlement_snapshot",
    "validate_entitlement_integrity",
    "validate_entitlement_snapshot_integrity",
    "build_entitlement_summary",

    # Service
    "EntitlementService",
    "get_entitlement_service",
    "resolve_feature_access",
    "entitlement_count",
    "entitlement_snapshot",
    "entitlement_health",
    "entitlement_operational_check",
    "entitlement_service_info",

    # Authority
    "entitlement_authority_boundary",
    "validate_entitlement_authority_boundary",
]