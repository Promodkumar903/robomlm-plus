# ============================================================
# ROBOMLM SUBSCRIPTION
# subscriber_service.py — PART 1
# SUBSCRIBER FOUNDATION / CONTRACTS
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Optional, Tuple


SUBSCRIBER_SERVICE_ENGINE = "ROBOMLM_SUBSCRIBER_SERVICE"
SUBSCRIBER_SERVICE_VERSION = "1.0"


# ============================================================
# ENUMS
# ============================================================

class SubscriberStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    BLOCKED = "BLOCKED"


class SubscriberDecision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    RESTRICTED = "RESTRICTED"


class SubscriberMode(str, Enum):
    PAPER = "PAPER"
    DEMO = "DEMO"
    LIVE = "LIVE"
    UNKNOWN = "UNKNOWN"


class SubscriberPriority(str, Enum):
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SubscriberContractStatus(str, Enum):
    CREATED = "CREATED"
    VALID = "VALID"
    INVALID = "INVALID"
    ASSESSED = "ASSESSED"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    BLOCKED = "BLOCKED"


class SubscriberAction(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    ACTIVATE = "ACTIVATE"
    SUSPEND = "SUSPEND"
    CANCEL = "CANCEL"
    EXPIRE = "EXPIRE"
    BLOCK = "BLOCK"
    UNBLOCK = "UNBLOCK"


class SubscriberSource(str, Enum):
    SYSTEM = "SYSTEM"
    SELF_SERVICE = "SELF_SERVICE"
    ADMIN = "ADMIN"
    PAYMENT = "PAYMENT"
    MIGRATION = "MIGRATION"
    UNKNOWN = "UNKNOWN"


# ============================================================
# HELPERS
# ============================================================

def _subscriber_text(
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


def _subscriber_enum(
    enum_type: type[Enum],
    value: Any,
    default: Enum,
) -> Enum:
    if isinstance(value, enum_type):
        return value

    if value is None:
        return default

    raw = getattr(value, "value", value)

    try:
        return enum_type(str(raw).strip().upper())
    except (ValueError, TypeError):
        return default


def _subscriber_bool(
    value: Any,
    default: bool = False,
) -> bool:
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        normalized = value.strip().lower()

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


def _subscriber_timestamp(
    value: Any = None,
) -> datetime:
    if isinstance(value, datetime):
        return value

    return datetime.now(timezone.utc)


# ============================================================
# PRIMARY REQUEST CONTRACT
# ============================================================

@dataclass(frozen=True)
class SubscriberRequest:
    user_id: Optional[str] = None
    subscriber_id: Optional[str] = None
    account_id: Optional[str] = None

    plan_id: Optional[str] = None
    subscription_id: Optional[str] = None

    status: SubscriberStatus = SubscriberStatus.ACTIVE
    mode: SubscriberMode = SubscriberMode.UNKNOWN
    priority: SubscriberPriority = SubscriberPriority.NORMAL
    source: SubscriberSource = SubscriberSource.SYSTEM

    email: Optional[str] = None
    display_name: str = ""

    active: bool = True
    verified: bool = False

    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    request_id: Optional[str] = None
    timestamp: datetime = field(
        default_factory=_subscriber_timestamp
    )


# ============================================================
# REFERENCE CONTRACT
# ============================================================

@dataclass(frozen=True)
class SubscriberReference:
    subscriber_id: str
    user_id: str

    account_id: Optional[str] = None
    plan_id: Optional[str] = None
    subscription_id: Optional[str] = None

    status: SubscriberStatus = SubscriberStatus.UNKNOWN

    version: str = SUBSCRIBER_SERVICE_VERSION

    created_at: datetime = field(
        default_factory=_subscriber_timestamp
    )


# ============================================================
# VALIDATION CONTRACT
# ============================================================

@dataclass(frozen=True)
class SubscriberContractValidation:
    valid: bool
    errors: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()

    checked_at: datetime = field(
        default_factory=_subscriber_timestamp
    )


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_subscriber_status(
    value: Any,
) -> SubscriberStatus:
    return _subscriber_enum(
        SubscriberStatus,
        value,
        SubscriberStatus.UNKNOWN,
    )


def normalize_subscriber_source(
    value: Any,
) -> SubscriberSource:
    return _subscriber_enum(
        SubscriberSource,
        value,
        SubscriberSource.UNKNOWN,
    )


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_subscriber_request(
    request: SubscriberRequest,
) -> SubscriberContractValidation:

    errors = []
    warnings = []

    if not isinstance(request, SubscriberRequest):
        return SubscriberContractValidation(
            valid=False,
            errors=(
                "request must be SubscriberRequest.",
            ),
        )

    if not _subscriber_text(request.user_id):
        errors.append(
            "user_id is required."
        )

    if request.valid_from is not None:
        if not isinstance(
            request.valid_from,
            datetime,
        ):
            errors.append(
                "valid_from must be datetime."
            )

    if request.valid_until is not None:
        if not isinstance(
            request.valid_until,
            datetime,
        ):
            errors.append(
                "valid_until must be datetime."
            )

    if (
        request.valid_from is not None
        and request.valid_until is not None
        and request.valid_until < request.valid_from
    ):
        errors.append(
            "valid_until cannot be earlier than valid_from."
        )

    if (
        request.status == SubscriberStatus.ACTIVE
        and not request.active
    ):
        warnings.append(
            "Subscriber status is ACTIVE but active flag is False."
        )

    if (
        request.status
        in {
            SubscriberStatus.CANCELLED,
            SubscriberStatus.EXPIRED,
            SubscriberStatus.BLOCKED,
        }
        and request.active
    ):
        warnings.append(
            "Terminal/restricted subscriber status "
            "has active flag set to True."
        )

    if request.plan_id is None:
        warnings.append(
            "No plan_id supplied."
        )

    if request.subscription_id is None:
        warnings.append(
            "No subscription_id supplied."
        )

    return SubscriberContractValidation(
        valid=not errors,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


# ============================================================
# REFERENCE VALIDATION
# ============================================================

def validate_subscriber_reference(
    reference: SubscriberReference,
) -> bool:

    if not isinstance(
        reference,
        SubscriberReference,
    ):
        return False

    if not _subscriber_text(
        reference.subscriber_id
    ):
        return False

    if not _subscriber_text(
        reference.user_id
    ):
        return False

    if not _subscriber_text(
        reference.version
    ):
        return False

    return True


# ============================================================
# REQUEST BUILDER
# ============================================================

def build_subscriber_request(
    *,
    user_id: Optional[str] = None,
    subscriber_id: Optional[str] = None,
    account_id: Optional[str] = None,
    plan_id: Optional[str] = None,
    subscription_id: Optional[str] = None,
    status: Any = SubscriberStatus.ACTIVE,
    mode: Any = SubscriberMode.UNKNOWN,
    priority: Any = SubscriberPriority.NORMAL,
    source: Any = SubscriberSource.SYSTEM,
    email: Optional[str] = None,
    display_name: Any = "",
    active: Any = True,
    verified: Any = False,
    valid_from: Optional[datetime] = None,
    valid_until: Optional[datetime] = None,
    metadata: Optional[Mapping[str, Any]] = None,
    request_id: Optional[str] = None,
    timestamp: Optional[datetime] = None,
) -> SubscriberRequest:

    normalized_metadata = dict(
        metadata or {}
    )

    return SubscriberRequest(
        user_id=_subscriber_text(user_id) or None,
        subscriber_id=(
            _subscriber_text(subscriber_id) or None
        ),
        account_id=(
            _subscriber_text(account_id) or None
        ),
        plan_id=(
            _subscriber_text(plan_id) or None
        ),
        subscription_id=(
            _subscriber_text(subscription_id) or None
        ),
        status=normalize_subscriber_status(status),
        mode=_subscriber_enum(
            SubscriberMode,
            mode,
            SubscriberMode.UNKNOWN,
        ),
        priority=_subscriber_enum(
            SubscriberPriority,
            priority,
            SubscriberPriority.NORMAL,
        ),
        source=normalize_subscriber_source(source),
        email=_subscriber_text(email) or None,
        display_name=_subscriber_text(
            display_name
        ),
        active=_subscriber_bool(
            active,
            True,
        ),
        verified=_subscriber_bool(
            verified,
            False,
        ),
        valid_from=valid_from,
        valid_until=valid_until,
        metadata=normalized_metadata,
        request_id=(
            _subscriber_text(request_id) or None
        ),
        timestamp=_subscriber_timestamp(
            timestamp
        ),
    )


# ============================================================
# REFERENCE BUILDER
# ============================================================

def build_subscriber_reference(
    *,
    subscriber_id: Any,
    user_id: Any,
    account_id: Any = None,
    plan_id: Any = None,
    subscription_id: Any = None,
    status: Any = SubscriberStatus.ACTIVE,
    version: str = SUBSCRIBER_SERVICE_VERSION,
    created_at: Optional[datetime] = None,
) -> SubscriberReference:

    return SubscriberReference(
        subscriber_id=_subscriber_text(
            subscriber_id
        ),
        user_id=_subscriber_text(
            user_id
        ),
        account_id=(
            _subscriber_text(account_id)
            or None
        ),
        plan_id=(
            _subscriber_text(plan_id)
            or None
        ),
        subscription_id=(
            _subscriber_text(subscription_id)
            or None
        ),
        status=normalize_subscriber_status(
            status
        ),
        version=_subscriber_text(
            version,
            SUBSCRIBER_SERVICE_VERSION,
        ),
        created_at=_subscriber_timestamp(
            created_at
        ),
    )


# ============================================================
# AUTHORITY BOUNDARY
# ============================================================

def subscriber_authority_boundary() -> Mapping[str, bool]:
    return {
        "subscriber_identity_authority": True,
        "subscriber_lifecycle_authority": True,

        "plan_definition_authority": False,
        "entitlement_authority": False,

        "market_decision_authority": False,
        "d13_decision_override": False,
        "risk_override": False,
        "cas_override": False,

        "execution_authority": False,
        "order_authority": False,
        "position_authority": False,
    }


def validate_subscriber_authority_boundary() -> bool:
    boundary = subscriber_authority_boundary()

    forbidden = (
        "plan_definition_authority",
        "entitlement_authority",
        "market_decision_authority",
        "d13_decision_override",
        "risk_override",
        "cas_override",
        "execution_authority",
        "order_authority",
        "position_authority",
    )

    return all(
        boundary.get(key) is False
        for key in forbidden
    )
# ============================================================
# ROBOMLM SUBSCRIPTION
# subscriber_service.py — PART 2
# SUBSCRIBER ASSESSMENT / ELIGIBILITY ENGINE
# ============================================================


# ============================================================
# ASSESSMENT ENUMS
# ============================================================

class SubscriberDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    INVALID = "INVALID"


class SubscriberConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONDITIONAL = "CONDITIONAL"
    INCONSISTENT = "INCONSISTENT"
    UNKNOWN = "UNKNOWN"


class SubscriberReadiness(str, Enum):
    READY = "READY"
    CONDITIONALLY_READY = "CONDITIONALLY_READY"
    NOT_READY = "NOT_READY"
    BLOCKED = "BLOCKED"


# ============================================================
# REQUIREMENTS CONTRACT
# ============================================================

@dataclass(frozen=True)
class SubscriberRequirements:
    require_user_id: bool = True
    require_subscriber_id: bool = False
    require_account_id: bool = False

    require_plan_id: bool = False
    require_subscription_id: bool = False

    require_active_status: bool = True
    require_verified: bool = False

    require_validity_window: bool = False

    allow_inactive: bool = False
    allow_suspended: bool = False
    allow_cancelled: bool = False
    allow_expired: bool = False
    allow_blocked: bool = False


# ============================================================
# ASSESSMENT CONTRACT
# ============================================================

@dataclass(frozen=True)
class SubscriberAssessment:
    data_state: SubscriberDataState
    consistency: SubscriberConsistency
    readiness: SubscriberReadiness

    completeness: float = 0.0
    subscriber_quality: float = 0.0
    confidence: float = 0.0

    flags: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    unmet_requirements: Tuple[str, ...] = ()

    eligible: bool = False
    active: bool = False
    verified: bool = False

    currently_valid: bool = False
    expired: bool = False

    user_id: Optional[str] = None
    subscriber_id: Optional[str] = None
    account_id: Optional[str] = None
    plan_id: Optional[str] = None
    subscription_id: Optional[str] = None

    status: SubscriberStatus = SubscriberStatus.UNKNOWN
    source: SubscriberSource = SubscriberSource.UNKNOWN

    notes: Tuple[str, ...] = ()


# ============================================================
# VALIDITY
# ============================================================

def evaluate_subscriber_validity(
    request: SubscriberRequest,
    *,
    now: Optional[datetime] = None,
) -> Tuple[bool, bool]:

    current_time = (
        now
        if isinstance(now, datetime)
        else datetime.now(timezone.utc)
    )

    if request.valid_from is not None:
        if current_time < request.valid_from:
            return False, False

    if request.valid_until is not None:
        if current_time > request.valid_until:
            return False, True

    return True, False


# ============================================================
# DATA STATE
# ============================================================

def evaluate_subscriber_data_state(
    request: SubscriberRequest,
) -> SubscriberDataState:

    validation = validate_subscriber_request(request)

    if validation.errors:
        return SubscriberDataState.INVALID

    present = 0
    total = 0

    fields = (
        request.user_id,
        request.subscriber_id,
        request.account_id,
        request.plan_id,
        request.subscription_id,
        request.display_name,
        request.email,
    )

    for value in fields:
        total += 1

        if _subscriber_text(value):
            present += 1

    if present == 0:
        return SubscriberDataState.MISSING

    if present < total:
        return SubscriberDataState.PARTIAL

    return SubscriberDataState.COMPLETE


# ============================================================
# CONSISTENCY
# ============================================================

def evaluate_subscriber_consistency(
    request: SubscriberRequest,
) -> SubscriberConsistency:

    validation = validate_subscriber_request(request)

    if validation.errors:
        return SubscriberConsistency.INCONSISTENT

    if (
        request.status == SubscriberStatus.ACTIVE
        and not request.active
    ):
        return SubscriberConsistency.CONDITIONAL

    if (
        request.status
        in {
            SubscriberStatus.CANCELLED,
            SubscriberStatus.EXPIRED,
            SubscriberStatus.BLOCKED,
        }
        and request.active
    ):
        return SubscriberConsistency.CONDITIONAL

    if (
        request.valid_from is not None
        and request.valid_until is not None
        and request.valid_until < request.valid_from
    ):
        return SubscriberConsistency.INCONSISTENT

    return SubscriberConsistency.CONSISTENT


# ============================================================
# REQUIREMENT EVALUATION
# ============================================================

def evaluate_subscriber_requirements(
    request: SubscriberRequest,
    requirements: Optional[
        SubscriberRequirements
    ] = None,
) -> Tuple[str, ...]:

    requirements = (
        requirements
        if requirements is not None
        else SubscriberRequirements()
    )

    unmet = []

    if (
        requirements.require_user_id
        and not _subscriber_text(request.user_id)
    ):
        unmet.append("user_id")

    if (
        requirements.require_subscriber_id
        and not _subscriber_text(request.subscriber_id)
    ):
        unmet.append("subscriber_id")

    if (
        requirements.require_account_id
        and not _subscriber_text(request.account_id)
    ):
        unmet.append("account_id")

    if (
        requirements.require_plan_id
        and not _subscriber_text(request.plan_id)
    ):
        unmet.append("plan_id")

    if (
        requirements.require_subscription_id
        and not _subscriber_text(request.subscription_id)
    ):
        unmet.append("subscription_id")

    if (
        requirements.require_active_status
        and request.status != SubscriberStatus.ACTIVE
    ):
        unmet.append("active_status")

    if (
        requirements.require_verified
        and not request.verified
    ):
        unmet.append("verified")

    if (
        requirements.require_validity_window
        and (
            request.valid_from is None
            or request.valid_until is None
        )
    ):
        unmet.append("validity_window")

    if (
        request.status == SubscriberStatus.INACTIVE
        and not requirements.allow_inactive
    ):
        unmet.append("inactive_not_allowed")

    if (
        request.status == SubscriberStatus.SUSPENDED
        and not requirements.allow_suspended
    ):
        unmet.append("suspended_not_allowed")

    if (
        request.status == SubscriberStatus.CANCELLED
        and not requirements.allow_cancelled
    ):
        unmet.append("cancelled_not_allowed")

    if (
        request.status == SubscriberStatus.EXPIRED
        and not requirements.allow_expired
    ):
        unmet.append("expired_not_allowed")

    if (
        request.status == SubscriberStatus.BLOCKED
        and not requirements.allow_blocked
    ):
        unmet.append("blocked_not_allowed")

    return tuple(unmet)


# ============================================================
# FLAGS
# ============================================================

def evaluate_subscriber_flags(
    request: SubscriberRequest,
    *,
    currently_valid: bool = True,
    expired: bool = False,
) -> Tuple[str, ...]:

    flags = []

    if not _subscriber_text(request.user_id):
        flags.append("MISSING_USER_ID")

    if not _subscriber_text(request.subscriber_id):
        flags.append("MISSING_SUBSCRIBER_ID")

    if not _subscriber_text(request.plan_id):
        flags.append("MISSING_PLAN_ID")

    if not _subscriber_text(request.subscription_id):
        flags.append("MISSING_SUBSCRIPTION_ID")

    if request.status == SubscriberStatus.SUSPENDED:
        flags.append("SUBSCRIBER_SUSPENDED")

    if request.status == SubscriberStatus.CANCELLED:
        flags.append("SUBSCRIBER_CANCELLED")

    if request.status == SubscriberStatus.BLOCKED:
        flags.append("SUBSCRIBER_BLOCKED")

    if request.status == SubscriberStatus.EXPIRED:
        flags.append("SUBSCRIBER_EXPIRED")

    if expired:
        flags.append("VALIDITY_EXPIRED")

    if not currently_valid:
        flags.append("NOT_CURRENTLY_VALID")

    if not request.verified:
        flags.append("NOT_VERIFIED")

    if (
        request.status == SubscriberStatus.ACTIVE
        and not request.active
    ):
        flags.append("ACTIVE_STATUS_INACTIVE_FLAG")

    return tuple(dict.fromkeys(flags))


# ============================================================
# COMPLETENESS
# ============================================================

def evaluate_subscriber_completeness(
    request: SubscriberRequest,
) -> float:

    required_fields = (
        request.user_id,
        request.subscriber_id,
        request.account_id,
        request.plan_id,
        request.subscription_id,
        request.display_name,
        request.email,
    )

    if not required_fields:
        return 0.0

    present = sum(
        1
        for value in required_fields
        if _subscriber_text(value)
    )

    return round(
        (present / len(required_fields)) * 100.0,
        2,
    )


# ============================================================
# QUALITY
# ============================================================

def evaluate_subscriber_quality(
    request: SubscriberRequest,
    *,
    currently_valid: bool = True,
    expired: bool = False,
    unmet_requirements: Tuple[str, ...] = (),
) -> float:

    score = 100.0

    if expired:
        score -= 50.0

    if not currently_valid:
        score -= 25.0

    if request.status == SubscriberStatus.BLOCKED:
        score -= 100.0

    elif request.status == SubscriberStatus.CANCELLED:
        score -= 70.0

    elif request.status == SubscriberStatus.SUSPENDED:
        score -= 50.0

    elif request.status == SubscriberStatus.EXPIRED:
        score -= 70.0

    elif request.status == SubscriberStatus.INACTIVE:
        score -= 35.0

    if not request.verified:
        score -= 10.0

    if not _subscriber_text(request.plan_id):
        score -= 5.0

    if not _subscriber_text(request.subscription_id):
        score -= 5.0

    score -= min(
        40.0,
        float(len(unmet_requirements) * 10),
    )

    return round(
        max(0.0, min(100.0, score)),
        2,
    )


# ============================================================
# CONFIDENCE
# ============================================================

def evaluate_subscriber_confidence(
    request: SubscriberRequest,
    *,
    data_state: SubscriberDataState,
    consistency: SubscriberConsistency,
    completeness: float,
    quality: float,
) -> float:

    score = (
        completeness * 0.35
        + quality * 0.35
    )

    if data_state == SubscriberDataState.COMPLETE:
        score += 15.0
    elif data_state == SubscriberDataState.PARTIAL:
        score += 7.0
    elif data_state == SubscriberDataState.MISSING:
        score -= 20.0
    elif data_state == SubscriberDataState.INVALID:
        score -= 40.0

    if consistency == SubscriberConsistency.CONSISTENT:
        score += 15.0
    elif consistency == SubscriberConsistency.CONDITIONAL:
        score += 5.0
    elif consistency == SubscriberConsistency.INCONSISTENT:
        score -= 25.0

    return round(
        max(0.0, min(100.0, score)),
        2,
    )


# ============================================================
# READINESS
# ============================================================

def evaluate_subscriber_readiness(
    request: SubscriberRequest,
    *,
    data_state: SubscriberDataState,
    consistency: SubscriberConsistency,
    unmet_requirements: Tuple[str, ...],
    currently_valid: bool,
    expired: bool,
    quality: float,
    requirements: Optional[
        SubscriberRequirements
    ] = None,
) -> SubscriberReadiness:

    requirements = (
        requirements
        if requirements is not None
        else SubscriberRequirements()
    )

    if data_state == SubscriberDataState.INVALID:
        return SubscriberReadiness.BLOCKED

    if request.status == SubscriberStatus.BLOCKED:
        return SubscriberReadiness.BLOCKED

    if (
        request.status == SubscriberStatus.CANCELLED
        and not requirements.allow_cancelled
    ):
        return SubscriberReadiness.BLOCKED

    if (
        expired
        and not requirements.allow_expired
    ):
        return SubscriberReadiness.BLOCKED

    if consistency == SubscriberConsistency.INCONSISTENT:
        return SubscriberReadiness.BLOCKED

    if unmet_requirements:
        return SubscriberReadiness.NOT_READY

    if not currently_valid:
        return SubscriberReadiness.NOT_READY

    if quality < 50.0:
        return SubscriberReadiness.NOT_READY

    if (
        consistency == SubscriberConsistency.CONDITIONAL
        or quality < 80.0
    ):
        return SubscriberReadiness.CONDITIONALLY_READY

    return SubscriberReadiness.READY


# ============================================================
# ELIGIBILITY
# ============================================================

def evaluate_subscriber_eligibility(
    request: SubscriberRequest,
    *,
    readiness: SubscriberReadiness,
    requirements: Optional[
        SubscriberRequirements
    ] = None,
) -> bool:

    requirements = (
        requirements
        if requirements is not None
        else SubscriberRequirements()
    )

    if readiness == SubscriberReadiness.BLOCKED:
        return False

    if readiness == SubscriberReadiness.NOT_READY:
        return False

    if request.status == SubscriberStatus.BLOCKED:
        return False

    if (
        request.status == SubscriberStatus.INACTIVE
        and not requirements.allow_inactive
    ):
        return False

    if (
        request.status == SubscriberStatus.SUSPENDED
        and not requirements.allow_suspended
    ):
        return False

    if (
        request.status == SubscriberStatus.CANCELLED
        and not requirements.allow_cancelled
    ):
        return False

    if (
        request.status == SubscriberStatus.EXPIRED
        and not requirements.allow_expired
    ):
        return False

    return True


# ============================================================
# ASSESSMENT BUILDER
# ============================================================

def build_subscriber_assessment(
    request: SubscriberRequest,
    *,
    requirements: Optional[
        SubscriberRequirements
    ] = None,
    now: Optional[datetime] = None,
) -> SubscriberAssessment:

    requirements = (
        requirements
        if requirements is not None
        else SubscriberRequirements()
    )

    validation = validate_subscriber_request(
        request
    )

    data_state = evaluate_subscriber_data_state(
        request
    )

    consistency = evaluate_subscriber_consistency(
        request
    )

    currently_valid, expired = (
        evaluate_subscriber_validity(
            request,
            now=now,
        )
    )

    unmet = evaluate_subscriber_requirements(
        request,
        requirements,
    )

    flags = evaluate_subscriber_flags(
        request,
        currently_valid=currently_valid,
        expired=expired,
    )

    completeness = evaluate_subscriber_completeness(
        request
    )

    quality = evaluate_subscriber_quality(
        request,
        currently_valid=currently_valid,
        expired=expired,
        unmet_requirements=unmet,
    )

    readiness = evaluate_subscriber_readiness(
        request,
        data_state=data_state,
        consistency=consistency,
        unmet_requirements=unmet,
        currently_valid=currently_valid,
        expired=expired,
        quality=quality,
        requirements=requirements,
    )

    eligible = evaluate_subscriber_eligibility(
        request,
        readiness=readiness,
        requirements=requirements,
    )

    confidence = evaluate_subscriber_confidence(
        request,
        data_state=data_state,
        consistency=consistency,
        completeness=completeness,
        quality=quality,
    )

    warnings = tuple(
        validation.warnings
    )

    notes = []

    if eligible:
        notes.append(
            "Subscriber satisfies current access eligibility checks."
        )

    if not eligible:
        notes.append(
            "Subscriber is not currently eligible under supplied requirements."
        )

    return SubscriberAssessment(
        data_state=data_state,
        consistency=consistency,
        readiness=readiness,

        completeness=completeness,
        subscriber_quality=quality,
        confidence=confidence,

        flags=flags,
        warnings=warnings,
        unmet_requirements=unmet,

        eligible=eligible,
        active=request.active,
        verified=request.verified,

        currently_valid=currently_valid,
        expired=expired,

        user_id=request.user_id,
        subscriber_id=request.subscriber_id,
        account_id=request.account_id,
        plan_id=request.plan_id,
        subscription_id=request.subscription_id,

        status=request.status,
        source=request.source,

        notes=tuple(notes),
    )
# ============================================================
# ROBOMLM SUBSCRIPTION
# subscriber_service.py — PART 3
# SUBSCRIBER RESOLUTION / LIFECYCLE ENGINE
# ============================================================


# ============================================================
# RESOLUTION RULES
# ============================================================

@dataclass(frozen=True)
class SubscriberResolutionRules:
    require_active_status: bool = True
    require_validity: bool = True
    require_verified: bool = False

    allow_inactive: bool = False
    allow_suspended: bool = False
    allow_cancelled: bool = False
    allow_expired: bool = False
    allow_blocked: bool = False

    require_plan: bool = False
    require_subscription: bool = False


def build_subscriber_resolution_rules(
    *,
    require_active_status: bool = True,
    require_validity: bool = True,
    require_verified: bool = False,
    allow_inactive: bool = False,
    allow_suspended: bool = False,
    allow_cancelled: bool = False,
    allow_expired: bool = False,
    allow_blocked: bool = False,
    require_plan: bool = False,
    require_subscription: bool = False,
) -> SubscriberResolutionRules:

    return SubscriberResolutionRules(
        require_active_status=_subscriber_bool(
            require_active_status,
            True,
        ),
        require_validity=_subscriber_bool(
            require_validity,
            True,
        ),
        require_verified=_subscriber_bool(
            require_verified,
            False,
        ),
        allow_inactive=_subscriber_bool(
            allow_inactive,
            False,
        ),
        allow_suspended=_subscriber_bool(
            allow_suspended,
            False,
        ),
        allow_cancelled=_subscriber_bool(
            allow_cancelled,
            False,
        ),
        allow_expired=_subscriber_bool(
            allow_expired,
            False,
        ),
        allow_blocked=_subscriber_bool(
            allow_blocked,
            False,
        ),
        require_plan=_subscriber_bool(
            require_plan,
            False,
        ),
        require_subscription=_subscriber_bool(
            require_subscription,
            False,
        ),
    )


# ============================================================
# RESOLUTION RESULT
# ============================================================

@dataclass(frozen=True)
class SubscriberResult:
    decision: SubscriberDecision
    status: SubscriberStatus

    allowed: bool
    restricted: bool
    review_required: bool
    blocked: bool

    user_id: Optional[str] = None
    subscriber_id: Optional[str] = None
    account_id: Optional[str] = None
    plan_id: Optional[str] = None
    subscription_id: Optional[str] = None

    assessment: Optional[SubscriberAssessment] = None

    flags: Tuple[str, ...] = ()
    restrictions: Tuple[str, ...] = ()
    errors: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()

    reason: str = ""

    timestamp: datetime = field(
        default_factory=_subscriber_timestamp
    )


# ============================================================
# RESOLUTION FLAGS
# ============================================================

def collect_subscriber_resolution_flags(
    request: SubscriberRequest,
    assessment: SubscriberAssessment,
) -> Tuple[str, ...]:

    flags = list(assessment.flags)

    if assessment.data_state == SubscriberDataState.INVALID:
        flags.append("INVALID_SUBSCRIBER_DATA")

    if (
        assessment.consistency
        == SubscriberConsistency.INCONSISTENT
    ):
        flags.append("INCONSISTENT_SUBSCRIBER_STATE")

    if (
        assessment.readiness
        == SubscriberReadiness.BLOCKED
    ):
        flags.append("SUBSCRIBER_READINESS_BLOCKED")

    if not assessment.eligible:
        flags.append("SUBSCRIBER_NOT_ELIGIBLE")

    return tuple(dict.fromkeys(flags))


# ============================================================
# RESTRICTIONS
# ============================================================

def collect_subscriber_restrictions(
    request: SubscriberRequest,
    assessment: SubscriberAssessment,
    rules: SubscriberResolutionRules,
) -> Tuple[str, ...]:

    restrictions = []

    if not request.verified:
        if not rules.require_verified:
            restrictions.append(
                "VERIFICATION_RESTRICTED"
            )

    if request.status == SubscriberStatus.SUSPENDED:
        restrictions.append(
            "SUSPENDED_RESTRICTION"
        )

    if request.status == SubscriberStatus.INACTIVE:
        restrictions.append(
            "INACTIVE_RESTRICTION"
        )

    if not request.plan_id:
        restrictions.append(
            "PLAN_UNSPECIFIED"
        )

    if not request.subscription_id:
        restrictions.append(
            "SUBSCRIPTION_UNSPECIFIED"
        )

    if assessment.consistency == SubscriberConsistency.CONDITIONAL:
        restrictions.append(
            "CONDITIONAL_SUBSCRIBER_STATE"
        )

    return tuple(dict.fromkeys(restrictions))


# ============================================================
# SUBSCRIBER RESOLUTION
# ============================================================

def resolve_subscriber(
    request: SubscriberRequest,
    *,
    requirements: Optional[
        SubscriberRequirements
    ] = None,
    rules: Optional[
        SubscriberResolutionRules
    ] = None,
    now: Optional[datetime] = None,
) -> SubscriberResult:

    requirements = (
        requirements
        if requirements is not None
        else SubscriberRequirements()
    )

    rules = (
        rules
        if rules is not None
        else SubscriberResolutionRules()
    )

    validation = validate_subscriber_request(
        request
    )

    if validation.errors:
        return SubscriberResult(
            decision=SubscriberDecision.DENY,
            status=SubscriberStatus.BLOCKED,
            allowed=False,
            restricted=False,
            review_required=False,
            blocked=True,
            user_id=request.user_id,
            subscriber_id=request.subscriber_id,
            account_id=request.account_id,
            plan_id=request.plan_id,
            subscription_id=request.subscription_id,
            errors=validation.errors,
            warnings=validation.warnings,
            reason="Invalid subscriber request.",
        )

    assessment = build_subscriber_assessment(
        request,
        requirements=requirements,
        now=now,
    )

    flags = collect_subscriber_resolution_flags(
        request,
        assessment,
    )

    restrictions = collect_subscriber_restrictions(
        request,
        assessment,
        rules,
    )

    # --------------------------------------------------------
    # HARD BLOCKS
    # --------------------------------------------------------

    if (
        assessment.data_state
        == SubscriberDataState.INVALID
    ):
        return SubscriberResult(
            decision=SubscriberDecision.DENY,
            status=SubscriberStatus.BLOCKED,
            allowed=False,
            restricted=False,
            review_required=False,
            blocked=True,
            user_id=request.user_id,
            subscriber_id=request.subscriber_id,
            account_id=request.account_id,
            plan_id=request.plan_id,
            subscription_id=request.subscription_id,
            assessment=assessment,
            flags=flags,
            restrictions=restrictions,
            errors=assessment.unmet_requirements,
            warnings=assessment.warnings,
            reason="Subscriber data is invalid.",
        )

    if request.status == SubscriberStatus.BLOCKED:
        return SubscriberResult(
            decision=SubscriberDecision.DENY,
            status=SubscriberStatus.BLOCKED,
            allowed=False,
            restricted=False,
            review_required=False,
            blocked=True,
            user_id=request.user_id,
            subscriber_id=request.subscriber_id,
            account_id=request.account_id,
            plan_id=request.plan_id,
            subscription_id=request.subscription_id,
            assessment=assessment,
            flags=flags,
            restrictions=restrictions,
            reason="Subscriber is blocked.",
        )

    if (
        request.status == SubscriberStatus.CANCELLED
        and not rules.allow_cancelled
    ):
        return SubscriberResult(
            decision=SubscriberDecision.DENY,
            status=SubscriberStatus.CANCELLED,
            allowed=False,
            restricted=False,
            review_required=False,
            blocked=True,
            user_id=request.user_id,
            subscriber_id=request.subscriber_id,
            account_id=request.account_id,
            plan_id=request.plan_id,
            subscription_id=request.subscription_id,
            assessment=assessment,
            flags=flags,
            restrictions=restrictions,
            reason="Subscriber is cancelled.",
        )

    if (
        request.status == SubscriberStatus.EXPIRED
        and not rules.allow_expired
    ):
        return SubscriberResult(
            decision=SubscriberDecision.DENY,
            status=SubscriberStatus.EXPIRED,
            allowed=False,
            restricted=False,
            review_required=False,
            blocked=True,
            user_id=request.user_id,
            subscriber_id=request.subscriber_id,
            account_id=request.account_id,
            plan_id=request.plan_id,
            subscription_id=request.subscription_id,
            assessment=assessment,
            flags=flags,
            restrictions=restrictions,
            reason="Subscriber is expired.",
        )

    # --------------------------------------------------------
    # VALIDITY
    # --------------------------------------------------------

    if (
        rules.require_validity
        and not assessment.currently_valid
    ):
        return SubscriberResult(
            decision=SubscriberDecision.DENY,
            status=(
                SubscriberStatus.EXPIRED
                if assessment.expired
                else request.status
            ),
            allowed=False,
            restricted=False,
            review_required=False,
            blocked=True,
            user_id=request.user_id,
            subscriber_id=request.subscriber_id,
            account_id=request.account_id,
            plan_id=request.plan_id,
            subscription_id=request.subscription_id,
            assessment=assessment,
            flags=flags,
            restrictions=restrictions,
            reason="Subscriber validity requirements are not satisfied.",
        )

    # --------------------------------------------------------
    # REQUIRED PLAN / SUBSCRIPTION
    # --------------------------------------------------------

    if (
        rules.require_plan
        and not _subscriber_text(request.plan_id)
    ):
        return SubscriberResult(
            decision=SubscriberDecision.REVIEW_REQUIRED,
            status=request.status,
            allowed=False,
            restricted=False,
            review_required=True,
            blocked=False,
            user_id=request.user_id,
            subscriber_id=request.subscriber_id,
            account_id=request.account_id,
            plan_id=request.plan_id,
            subscription_id=request.subscription_id,
            assessment=assessment,
            flags=flags,
            restrictions=restrictions,
            reason="Plan reference is required.",
        )

    if (
        rules.require_subscription
        and not _subscriber_text(request.subscription_id)
    ):
        return SubscriberResult(
            decision=SubscriberDecision.REVIEW_REQUIRED,
            status=request.status,
            allowed=False,
            restricted=False,
            review_required=True,
            blocked=False,
            user_id=request.user_id,
            subscriber_id=request.subscriber_id,
            account_id=request.account_id,
            plan_id=request.plan_id,
            subscription_id=request.subscription_id,
            assessment=assessment,
            flags=flags,
            restrictions=restrictions,
            reason="Subscription reference is required.",
        )

    # --------------------------------------------------------
    # VERIFICATION
    # --------------------------------------------------------

    if (
        rules.require_verified
        and not request.verified
    ):
        return SubscriberResult(
            decision=SubscriberDecision.REVIEW_REQUIRED,
            status=request.status,
            allowed=False,
            restricted=False,
            review_required=True,
            blocked=False,
            user_id=request.user_id,
            subscriber_id=request.subscriber_id,
            account_id=request.account_id,
            plan_id=request.plan_id,
            subscription_id=request.subscription_id,
            assessment=assessment,
            flags=flags,
            restrictions=restrictions,
            reason="Subscriber verification is required.",
        )

    # --------------------------------------------------------
    # SUSPENDED / INACTIVE
    # --------------------------------------------------------

    if (
        request.status == SubscriberStatus.SUSPENDED
        and not rules.allow_suspended
    ):
        return SubscriberResult(
            decision=SubscriberDecision.RESTRICTED,
            status=SubscriberStatus.SUSPENDED,
            allowed=False,
            restricted=True,
            review_required=True,
            blocked=False,
            user_id=request.user_id,
            subscriber_id=request.subscriber_id,
            account_id=request.account_id,
            plan_id=request.plan_id,
            subscription_id=request.subscription_id,
            assessment=assessment,
            flags=flags,
            restrictions=restrictions,
            reason="Subscriber is suspended.",
        )

    if (
        request.status == SubscriberStatus.INACTIVE
        and not rules.allow_inactive
    ):
        return SubscriberResult(
            decision=SubscriberDecision.RESTRICTED,
            status=SubscriberStatus.INACTIVE,
            allowed=False,
            restricted=True,
            review_required=True,
            blocked=False,
            user_id=request.user_id,
            subscriber_id=request.subscriber_id,
            account_id=request.account_id,
            plan_id=request.plan_id,
            subscription_id=request.subscription_id,
            assessment=assessment,
            flags=flags,
            restrictions=restrictions,
            reason="Subscriber is inactive.",
        )

    # --------------------------------------------------------
    # CONDITIONAL ACCESS
    # --------------------------------------------------------

    if (
        assessment.readiness
        == SubscriberReadiness.CONDITIONALLY_READY
    ):
        return SubscriberResult(
            decision=SubscriberDecision.RESTRICTED,
            status=request.status,
            allowed=True,
            restricted=True,
            review_required=False,
            blocked=False,
            user_id=request.user_id,
            subscriber_id=request.subscriber_id,
            account_id=request.account_id,
            plan_id=request.plan_id,
            subscription_id=request.subscription_id,
            assessment=assessment,
            flags=flags,
            restrictions=restrictions,
            reason="Subscriber is eligible with restrictions.",
        )

    # --------------------------------------------------------
    # FINAL ALLOW
    # --------------------------------------------------------

    if assessment.eligible:
        return SubscriberResult(
            decision=SubscriberDecision.ALLOW,
            status=SubscriberStatus.ACTIVE,
            allowed=True,
            restricted=False,
            review_required=False,
            blocked=False,
            user_id=request.user_id,
            subscriber_id=request.subscriber_id,
            account_id=request.account_id,
            plan_id=request.plan_id,
            subscription_id=request.subscription_id,
            assessment=assessment,
            flags=flags,
            restrictions=restrictions,
            reason="Subscriber is eligible.",
        )

    # --------------------------------------------------------
    # FALLBACK REVIEW
    # --------------------------------------------------------

    return SubscriberResult(
        decision=SubscriberDecision.REVIEW_REQUIRED,
        status=request.status,
        allowed=False,
        restricted=False,
        review_required=True,
        blocked=False,
        user_id=request.user_id,
        subscriber_id=request.subscriber_id,
        account_id=request.account_id,
        plan_id=request.plan_id,
        subscription_id=request.subscription_id,
        assessment=assessment,
        flags=flags,
        restrictions=restrictions,
        reason="Subscriber requires review.",
    )


# ============================================================
# ADMIN LIFECYCLE VALIDATION
# ============================================================

def validate_subscriber_action(
    action: Any,
) -> Tuple[bool, str]:

    normalized = _subscriber_text(
        action
    ).upper()

    if normalized not in {
        item.value
        for item in SubscriberAction
    }:
        return (
            False,
            f"Unsupported subscriber action: {normalized}.",
        )

    return True, ""


@dataclass(frozen=True)
class SubscriberAdminRequest:
    action: SubscriberAction

    subscriber_id: Optional[str] = None
    user_id: Optional[str] = None
    account_id: Optional[str] = None

    plan_id: Optional[str] = None
    subscription_id: Optional[str] = None

    status: SubscriberStatus = SubscriberStatus.ACTIVE

    email: Optional[str] = None
    display_name: str = ""

    verified: bool = False

    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None

    admin_id: Optional[str] = None
    reason: str = ""

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    request_id: Optional[str] = None
    timestamp: datetime = field(
        default_factory=_subscriber_timestamp
    )


@dataclass(frozen=True)
class SubscriberAdminResult:
    success: bool
    changed: bool

    action: SubscriberAction

    subscriber_id: Optional[str] = None

    previous: Optional[SubscriberReference] = None
    current: Optional[SubscriberReference] = None

    errors: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()

    reason: str = ""

    timestamp: datetime = field(
        default_factory=_subscriber_timestamp
    )


def validate_subscriber_admin_request(
    request: SubscriberAdminRequest,
) -> Tuple[str, ...]:

    errors = []

    if not isinstance(
        request,
        SubscriberAdminRequest,
    ):
        return (
            "request must be SubscriberAdminRequest.",
        )

    valid_action, action_error = (
        validate_subscriber_action(
            request.action
        )
    )

    if not valid_action:
        errors.append(action_error)

    if not _subscriber_text(
        request.admin_id
    ):
        errors.append(
            "admin_id is required."
        )

    if not _subscriber_text(
        request.reason
    ):
        errors.append(
            "Administrative reason is required."
        )

    if request.action == SubscriberAction.CREATE:
        if not _subscriber_text(
            request.user_id
        ):
            errors.append(
                "user_id is required for CREATE."
            )

    else:
        if not _subscriber_text(
            request.subscriber_id
        ):
            errors.append(
                "subscriber_id is required."
            )

    if (
        request.valid_from is not None
        and request.valid_until is not None
        and request.valid_until < request.valid_from
    ):
        errors.append(
            "valid_until cannot be earlier than valid_from."
        )

    return tuple(errors)
# ============================================================
# ROBOMLM SUBSCRIPTION
# subscriber_service.py — PART 4
# SUBSCRIBER REGISTRY / ADMIN LIFECYCLE
# ============================================================


# ============================================================
# REGISTRY CONTRACTS
# ============================================================

@dataclass(frozen=True)
class SubscriberRegistryEntry:
    subscriber: SubscriberReference
    revision: int = 1
    updated_by: Optional[str] = None
    updated_at: datetime = field(
        default_factory=_subscriber_timestamp
    )


@dataclass(frozen=True)
class SubscriberRegistrySnapshot:
    total: int
    active: int
    inactive: int
    suspended: int
    cancelled: int
    expired: int
    blocked: int

    subscribers: Tuple[
        SubscriberReference,
        ...
    ] = ()

    timestamp: datetime = field(
        default_factory=_subscriber_timestamp
    )


# ============================================================
# REGISTRY
# ============================================================

class SubscriberRegistry:
    """
    Authoritative in-process subscriber state registry.

    Owns subscriber identity/lifecycle state only.

    It does NOT own:
      - plan definitions
      - entitlements
      - market decisions
      - D13
      - risk
      - CAS
      - execution
      - orders
      - positions
    """

    def __init__(self) -> None:
        self._entries: dict[
            str,
            SubscriberRegistryEntry,
        ] = {}

    def exists(
        self,
        subscriber_id: str,
    ) -> bool:
        return (
            _subscriber_text(subscriber_id)
            in self._entries
        )

    def get(
        self,
        subscriber_id: str,
    ) -> Optional[SubscriberReference]:
        entry = self._entries.get(
            _subscriber_text(subscriber_id)
        )

        return (
            entry.subscriber
            if entry is not None
            else None
        )

    def get_entry(
        self,
        subscriber_id: str,
    ) -> Optional[SubscriberRegistryEntry]:
        return self._entries.get(
            _subscriber_text(subscriber_id)
        )

    def add(
        self,
        subscriber: SubscriberReference,
        *,
        updated_by: Optional[str] = None,
    ) -> SubscriberRegistryEntry:

        if not validate_subscriber_reference(
            subscriber
        ):
            raise ValueError(
                "Invalid subscriber reference."
            )

        if self.exists(
            subscriber.subscriber_id
        ):
            raise ValueError(
                f"Subscriber already exists: "
                f"{subscriber.subscriber_id}"
            )

        entry = SubscriberRegistryEntry(
            subscriber=subscriber,
            revision=1,
            updated_by=updated_by,
        )

        self._entries[
            subscriber.subscriber_id
        ] = entry

        return entry

    def replace(
        self,
        subscriber: SubscriberReference,
        *,
        updated_by: Optional[str] = None,
    ) -> SubscriberRegistryEntry:

        if not validate_subscriber_reference(
            subscriber
        ):
            raise ValueError(
                "Invalid subscriber reference."
            )

        previous = self._entries.get(
            subscriber.subscriber_id
        )

        revision = (
            previous.revision + 1
            if previous is not None
            else 1
        )

        entry = SubscriberRegistryEntry(
            subscriber=subscriber,
            revision=revision,
            updated_by=updated_by,
        )

        self._entries[
            subscriber.subscriber_id
        ] = entry

        return entry

    def remove(
        self,
        subscriber_id: str,
    ) -> bool:

        return (
            self._entries.pop(
                _subscriber_text(subscriber_id),
                None,
            )
            is not None
        )

    def list_subscribers(
        self,
        *,
        user_id: Optional[str] = None,
        plan_id: Optional[str] = None,
        subscription_id: Optional[str] = None,
        status: Optional[SubscriberStatus] = None,
    ) -> Tuple[SubscriberReference, ...]:

        normalized_user = (
            _subscriber_text(user_id)
        )

        normalized_plan = (
            _subscriber_text(plan_id)
        )

        normalized_subscription = (
            _subscriber_text(subscription_id)
        )

        result = []

        for entry in self._entries.values():

            subscriber = entry.subscriber

            if (
                normalized_user
                and subscriber.user_id
                != normalized_user
            ):
                continue

            if (
                normalized_plan
                and subscriber.plan_id
                != normalized_plan
            ):
                continue

            if (
                normalized_subscription
                and subscriber.subscription_id
                != normalized_subscription
            ):
                continue

            if (
                status is not None
                and subscriber.status != status
            ):
                continue

            result.append(subscriber)

        result.sort(
            key=lambda item: item.subscriber_id
        )

        return tuple(result)

    def snapshot(
        self,
    ) -> SubscriberRegistrySnapshot:

        subscribers = tuple(
            entry.subscriber
            for entry in self._entries.values()
        )

        counts = {
            SubscriberStatus.ACTIVE: 0,
            SubscriberStatus.INACTIVE: 0,
            SubscriberStatus.SUSPENDED: 0,
            SubscriberStatus.CANCELLED: 0,
            SubscriberStatus.EXPIRED: 0,
            SubscriberStatus.BLOCKED: 0,
        }

        for subscriber in subscribers:
            if subscriber.status in counts:
                counts[subscriber.status] += 1

        return SubscriberRegistrySnapshot(
            total=len(subscribers),
            active=counts[
                SubscriberStatus.ACTIVE
            ],
            inactive=counts[
                SubscriberStatus.INACTIVE
            ],
            suspended=counts[
                SubscriberStatus.SUSPENDED
            ],
            cancelled=counts[
                SubscriberStatus.CANCELLED
            ],
            expired=counts[
                SubscriberStatus.EXPIRED
            ],
            blocked=counts[
                SubscriberStatus.BLOCKED
            ],
            subscribers=tuple(
                sorted(
                    subscribers,
                    key=lambda item:
                    item.subscriber_id,
                )
            ),
        )

    def count(self) -> int:
        return len(self._entries)


# ============================================================
# REFERENCE STATUS TRANSITION
# ============================================================

def _subscriber_reference_with_status(
    reference: SubscriberReference,
    status: SubscriberStatus,
) -> SubscriberReference:

    return SubscriberReference(
        subscriber_id=reference.subscriber_id,
        user_id=reference.user_id,
        account_id=reference.account_id,
        plan_id=reference.plan_id,
        subscription_id=reference.subscription_id,
        status=status,
        version=reference.version,
        created_at=reference.created_at,
    )


# ============================================================
# ADMIN MUTATION RESULT HELPER
# ============================================================

def _subscriber_admin_result(
    *,
    success: bool,
    changed: bool,
    action: SubscriberAction,
    subscriber_id: Optional[str],
    previous: Optional[SubscriberReference],
    current: Optional[SubscriberReference],
    errors: Tuple[str, ...] = (),
    warnings: Tuple[str, ...] = (),
    reason: str = "",
) -> SubscriberAdminResult:

    return SubscriberAdminResult(
        success=success,
        changed=changed,
        action=action,
        subscriber_id=subscriber_id,
        previous=previous,
        current=current,
        errors=errors,
        warnings=warnings,
        reason=reason,
    )


# ============================================================
# CREATE
# ============================================================

def create_subscriber(
    registry: SubscriberRegistry,
    request: SubscriberAdminRequest,
) -> SubscriberAdminResult:

    errors = validate_subscriber_admin_request(
        request
    )

    if errors:
        return _subscriber_admin_result(
            success=False,
            changed=False,
            action=SubscriberAction.CREATE,
            subscriber_id=request.subscriber_id,
            previous=None,
            current=None,
            errors=errors,
        )

    subscriber_id = _subscriber_text(
        request.subscriber_id
    )

    if not subscriber_id:
        return _subscriber_admin_result(
            success=False,
            changed=False,
            action=SubscriberAction.CREATE,
            subscriber_id=None,
            previous=None,
            current=None,
            errors=(
                "subscriber_id is required for "
                "registry creation.",
            ),
        )

    if registry.exists(subscriber_id):
        return _subscriber_admin_result(
            success=False,
            changed=False,
            action=SubscriberAction.CREATE,
            subscriber_id=subscriber_id,
            previous=registry.get(subscriber_id),
            current=None,
            errors=(
                "Subscriber already exists.",
            ),
        )

    reference = build_subscriber_reference(
        subscriber_id=subscriber_id,
        user_id=request.user_id,
        account_id=request.account_id,
        plan_id=request.plan_id,
        subscription_id=request.subscription_id,
        status=request.status,
    )

    registry.add(
        reference,
        updated_by=request.admin_id,
    )

    return _subscriber_admin_result(
        success=True,
        changed=True,
        action=SubscriberAction.CREATE,
        subscriber_id=subscriber_id,
        previous=None,
        current=reference,
        reason=request.reason,
    )


# ============================================================
# STATUS UPDATE
# ============================================================

def update_subscriber_status(
    registry: SubscriberRegistry,
    request: SubscriberAdminRequest,
    status: SubscriberStatus,
) -> SubscriberAdminResult:

    errors = validate_subscriber_admin_request(
        request
    )

    if errors:
        return _subscriber_admin_result(
            success=False,
            changed=False,
            action=request.action,
            subscriber_id=request.subscriber_id,
            previous=None,
            current=None,
            errors=errors,
        )

    subscriber_id = _subscriber_text(
        request.subscriber_id
    )

    previous = registry.get(
        subscriber_id
    )

    if previous is None:
        return _subscriber_admin_result(
            success=False,
            changed=False,
            action=request.action,
            subscriber_id=subscriber_id,
            previous=None,
            current=None,
            errors=(
                "Subscriber not found.",
            ),
        )

    current = _subscriber_reference_with_status(
        previous,
        status,
    )

    changed = (
        current.status
        != previous.status
    )

    if changed:
        registry.replace(
            current,
            updated_by=request.admin_id,
        )

    return _subscriber_admin_result(
        success=True,
        changed=changed,
        action=request.action,
        subscriber_id=subscriber_id,
        previous=previous,
        current=current,
        reason=request.reason,
    )


# ============================================================
# LIFECYCLE OPERATIONS
# ============================================================

def activate_subscriber(
    registry: SubscriberRegistry,
    request: SubscriberAdminRequest,
) -> SubscriberAdminResult:

    return update_subscriber_status(
        registry,
        request,
        SubscriberStatus.ACTIVE,
    )


def suspend_subscriber(
    registry: SubscriberRegistry,
    request: SubscriberAdminRequest,
) -> SubscriberAdminResult:

    return update_subscriber_status(
        registry,
        request,
        SubscriberStatus.SUSPENDED,
    )


def cancel_subscriber(
    registry: SubscriberRegistry,
    request: SubscriberAdminRequest,
) -> SubscriberAdminResult:

    return update_subscriber_status(
        registry,
        request,
        SubscriberStatus.CANCELLED,
    )


def expire_subscriber(
    registry: SubscriberRegistry,
    request: SubscriberAdminRequest,
) -> SubscriberAdminResult:

    return update_subscriber_status(
        registry,
        request,
        SubscriberStatus.EXPIRED,
    )


def block_subscriber(
    registry: SubscriberRegistry,
    request: SubscriberAdminRequest,
) -> SubscriberAdminResult:

    return update_subscriber_status(
        registry,
        request,
        SubscriberStatus.BLOCKED,
    )


def unblock_subscriber(
    registry: SubscriberRegistry,
    request: SubscriberAdminRequest,
) -> SubscriberAdminResult:

    return update_subscriber_status(
        registry,
        request,
        SubscriberStatus.ACTIVE,
    )


# ============================================================
# UPDATE REFERENCE
# ============================================================

def update_subscriber_reference(
    registry: SubscriberRegistry,
    request: SubscriberAdminRequest,
) -> SubscriberAdminResult:

    errors = validate_subscriber_admin_request(
        request
    )

    if errors:
        return _subscriber_admin_result(
            success=False,
            changed=False,
            action=SubscriberAction.UPDATE,
            subscriber_id=request.subscriber_id,
            previous=None,
            current=None,
            errors=errors,
        )

    subscriber_id = _subscriber_text(
        request.subscriber_id
    )

    previous = registry.get(
        subscriber_id
    )

    if previous is None:
        return _subscriber_admin_result(
            success=False,
            changed=False,
            action=SubscriberAction.UPDATE,
            subscriber_id=subscriber_id,
            previous=None,
            current=None,
            errors=(
                "Subscriber not found.",
            ),
        )

    current = SubscriberReference(
        subscriber_id=previous.subscriber_id,
        user_id=(
            _subscriber_text(
                request.user_id
            )
            or previous.user_id
        ),
        account_id=(
            _subscriber_text(
                request.account_id
            )
            or previous.account_id
        ),
        plan_id=(
            _subscriber_text(
                request.plan_id
            )
            or previous.plan_id
        ),
        subscription_id=(
            _subscriber_text(
                request.subscription_id
            )
            or previous.subscription_id
        ),
        status=request.status,
        version=previous.version,
        created_at=previous.created_at,
    )

    changed = current != previous

    if changed:
        registry.replace(
            current,
            updated_by=request.admin_id,
        )

    return _subscriber_admin_result(
        success=True,
        changed=changed,
        action=SubscriberAction.UPDATE,
        subscriber_id=subscriber_id,
        previous=previous,
        current=current,
        reason=request.reason,
    )


# ============================================================
# REGISTRY INTEGRITY
# ============================================================

def validate_subscriber_registry(
    registry: SubscriberRegistry,
) -> Tuple[str, ...]:

    if not isinstance(
        registry,
        SubscriberRegistry,
    ):
        return (
            "registry must be SubscriberRegistry.",
        )

    errors = []
    seen = set()

    for subscriber in registry.list_subscribers():

        subscriber_id = subscriber.subscriber_id

        if subscriber_id in seen:
            errors.append(
                f"Duplicate subscriber_id: "
                f"{subscriber_id}"
            )

        seen.add(subscriber_id)

        if not validate_subscriber_reference(
            subscriber
        ):
            errors.append(
                f"Invalid subscriber reference: "
                f"{subscriber_id}"
            )

    return tuple(errors)


# ============================================================
# REGISTRY HEALTH
# ============================================================

def subscriber_registry_health(
    registry: SubscriberRegistry,
) -> Mapping[str, Any]:

    errors = validate_subscriber_registry(
        registry
    )

    snapshot = registry.snapshot()

    return {
        "engine": SUBSCRIBER_SERVICE_ENGINE,
        "version": SUBSCRIBER_SERVICE_VERSION,
        "healthy": not errors,

        "registry_count": snapshot.total,

        "active": snapshot.active,
        "inactive": snapshot.inactive,
        "suspended": snapshot.suspended,
        "cancelled": snapshot.cancelled,
        "expired": snapshot.expired,
        "blocked": snapshot.blocked,

        "errors": errors,

        "timestamp": _subscriber_timestamp(),
    }
# ============================================================
# ROBOMLM SUBSCRIPTION
# subscriber_service.py — PART 5
# SERIALIZATION / INTEGRITY / SERVICE FACADE / PUBLIC API
# ============================================================

def _subscriber_iso(value: Any) -> Optional[str]:
    if isinstance(value, datetime):
        return value.isoformat()
    return None


def serialize_subscriber_reference(
    reference: SubscriberReference,
) -> Mapping[str, Any]:
    return {
        "subscriber_id": reference.subscriber_id,
        "user_id": reference.user_id,
        "account_id": reference.account_id,
        "plan_id": reference.plan_id,
        "subscription_id": reference.subscription_id,
        "status": reference.status.value,
        "version": reference.version,
        "created_at": _subscriber_iso(reference.created_at),
    }


def serialize_subscriber_assessment(
    assessment: SubscriberAssessment,
) -> Mapping[str, Any]:
    return {
        "data_state": assessment.data_state.value,
        "consistency": assessment.consistency.value,
        "readiness": assessment.readiness.value,
        "completeness": assessment.completeness,
        "subscriber_quality": assessment.subscriber_quality,
        "confidence": assessment.confidence,
        "flags": tuple(assessment.flags),
        "warnings": tuple(assessment.warnings),
        "unmet_requirements": tuple(assessment.unmet_requirements),
        "eligible": assessment.eligible,
        "active": assessment.active,
        "verified": assessment.verified,
        "currently_valid": assessment.currently_valid,
        "expired": assessment.expired,
        "user_id": assessment.user_id,
        "subscriber_id": assessment.subscriber_id,
        "account_id": assessment.account_id,
        "plan_id": assessment.plan_id,
        "subscription_id": assessment.subscription_id,
        "status": assessment.status.value,
        "source": assessment.source.value,
        "notes": tuple(assessment.notes),
    }


def serialize_subscriber_result(
    result: SubscriberResult,
) -> Mapping[str, Any]:
    return {
        "decision": result.decision.value,
        "status": result.status.value,
        "allowed": result.allowed,
        "restricted": result.restricted,
        "review_required": result.review_required,
        "blocked": result.blocked,
        "user_id": result.user_id,
        "subscriber_id": result.subscriber_id,
        "account_id": result.account_id,
        "plan_id": result.plan_id,
        "subscription_id": result.subscription_id,
        "assessment": serialize_subscriber_assessment(result.assessment),
        "flags": tuple(result.flags),
        "restrictions": tuple(result.restrictions),
        "errors": tuple(result.errors),
        "warnings": tuple(result.warnings),
        "reason": result.reason,
        "timestamp": _subscriber_iso(result.timestamp),
    }


def serialize_subscriber_admin_result(
    result: SubscriberAdminResult,
) -> Mapping[str, Any]:
    return {
        "success": result.success,
        "changed": result.changed,
        "action": result.action.value,
        "subscriber_id": result.subscriber_id,
        "previous": (
            serialize_subscriber_reference(result.previous)
            if result.previous is not None
            else None
        ),
        "current": (
            serialize_subscriber_reference(result.current)
            if result.current is not None
            else None
        ),
        "errors": tuple(result.errors),
        "warnings": tuple(result.warnings),
        "reason": result.reason,
        "timestamp": _subscriber_iso(result.timestamp),
    }


def serialize_subscriber_snapshot(
    snapshot: SubscriberRegistrySnapshot,
) -> Mapping[str, Any]:
    return {
        "total": snapshot.total,
        "active": snapshot.active,
        "inactive": snapshot.inactive,
        "suspended": snapshot.suspended,
        "cancelled": snapshot.cancelled,
        "expired": snapshot.expired,
        "blocked": snapshot.blocked,
        "subscribers": tuple(
            serialize_subscriber_reference(item)
            for item in snapshot.subscribers
        ),
        "timestamp": _subscriber_iso(snapshot.timestamp),
    }


# ============================================================
# INTEGRITY
# ============================================================

def validate_subscriber_integrity(
    subscriber: SubscriberReference,
) -> bool:
    if not validate_subscriber_reference(subscriber):
        return False

    if not isinstance(subscriber.status, SubscriberStatus):
        return False

    if not _subscriber_text(subscriber.subscriber_id):
        return False

    if not _subscriber_text(subscriber.user_id):
        return False

    if not _subscriber_text(subscriber.version):
        return False

    return True


def validate_subscriber_snapshot_integrity(
    snapshot: SubscriberRegistrySnapshot,
) -> bool:
    if not isinstance(snapshot, SubscriberRegistrySnapshot):
        return False

    if snapshot.total < 0:
        return False

    if any(
        value < 0
        for value in (
            snapshot.active,
            snapshot.inactive,
            snapshot.suspended,
            snapshot.cancelled,
            snapshot.expired,
            snapshot.blocked,
        )
    ):
        return False

    if sum(
        (
            snapshot.active,
            snapshot.inactive,
            snapshot.suspended,
            snapshot.cancelled,
            snapshot.expired,
            snapshot.blocked,
        )
    ) != snapshot.total:
        return False

    if len(snapshot.subscribers) != snapshot.total:
        return False

    return all(
        validate_subscriber_integrity(item)
        for item in snapshot.subscribers
    )


def build_subscriber_summary(
    subscriber: SubscriberReference,
) -> Mapping[str, Any]:
    if not validate_subscriber_integrity(subscriber):
        return {
            "valid": False,
            "subscriber_id": None,
            "status": SubscriberStatus.UNKNOWN.value,
        }

    return {
        "valid": True,
        "subscriber_id": subscriber.subscriber_id,
        "user_id": subscriber.user_id,
        "account_id": subscriber.account_id,
        "plan_id": subscriber.plan_id,
        "subscription_id": subscriber.subscription_id,
        "status": subscriber.status.value,
        "active": subscriber.status == SubscriberStatus.ACTIVE,
    }


# ============================================================
# SERVICE FACADE
# ============================================================

class SubscriberService:
    """
    Subscriber Service is the authoritative subscriber identity
    and lifecycle layer.

    It does NOT own:
      - plan definitions
      - pricing
      - entitlements
      - market intelligence
      - D13 decisions
      - risk
      - CAS
      - execution
      - orders
      - positions
    """

    def __init__(self) -> None:
        self.registry = SubscriberRegistry()

    def resolve(
        self,
        request: SubscriberRequest,
        *,
        rules: Optional[SubscriberResolutionRules] = None,
        now: Optional[datetime] = None,
    ) -> SubscriberResult:
        return resolve_subscriber(
            request,
            rules=rules,
            now=now,
        )

    def create(
        self,
        request: SubscriberAdminRequest,
        *,
        registry: Optional[SubscriberRegistry] = None,
    ) -> SubscriberAdminResult:
        return create_subscriber(
            request,
            registry=registry or self.registry,
        )

    def update_status(
        self,
        subscriber_id: str,
        status: SubscriberStatus,
        *,
        admin_id: str,
        reason: str,
    ) -> SubscriberAdminResult:
        return update_subscriber_status(
            self.registry,
            subscriber_id,
            status,
            admin_id=admin_id,
            reason=reason,
        )

    def activate(
        self,
        subscriber_id: str,
        *,
        admin_id: str,
        reason: str = "Subscriber activated.",
    ) -> SubscriberAdminResult:
        return activate_subscriber(
            self.registry,
            subscriber_id,
            admin_id=admin_id,
            reason=reason,
        )

    def suspend(
        self,
        subscriber_id: str,
        *,
        admin_id: str,
        reason: str = "Subscriber suspended.",
    ) -> SubscriberAdminResult:
        return suspend_subscriber(
            self.registry,
            subscriber_id,
            admin_id=admin_id,
            reason=reason,
        )

    def cancel(
        self,
        subscriber_id: str,
        *,
        admin_id: str,
        reason: str = "Subscriber cancelled.",
    ) -> SubscriberAdminResult:
        return cancel_subscriber(
            self.registry,
            subscriber_id,
            admin_id=admin_id,
            reason=reason,
        )

    def expire(
        self,
        subscriber_id: str,
        *,
        admin_id: str,
        reason: str = "Subscriber expired.",
    ) -> SubscriberAdminResult:
        return expire_subscriber(
            self.registry,
            subscriber_id,
            admin_id=admin_id,
            reason=reason,
        )

    def block(
        self,
        subscriber_id: str,
        *,
        admin_id: str,
        reason: str = "Subscriber blocked.",
    ) -> SubscriberAdminResult:
        return block_subscriber(
            self.registry,
            subscriber_id,
            admin_id=admin_id,
            reason=reason,
        )

    def unblock(
        self,
        subscriber_id: str,
        *,
        admin_id: str,
        reason: str = "Subscriber unblocked.",
    ) -> SubscriberAdminResult:
        return unblock_subscriber(
            self.registry,
            subscriber_id,
            admin_id=admin_id,
            reason=reason,
        )

    def update(
        self,
        request: SubscriberAdminRequest,
    ) -> SubscriberAdminResult:
        return update_subscriber_reference(
            self.registry,
            request,
        )

    def get(
        self,
        subscriber_id: str,
    ) -> Optional[SubscriberReference]:
        return self.registry.get(subscriber_id)

    def list_subscribers(
        self,
        *,
        user_id: Optional[str] = None,
        plan_id: Optional[str] = None,
        subscription_id: Optional[str] = None,
        status: Optional[SubscriberStatus] = None,
    ) -> Tuple[SubscriberReference, ...]:
        return self.registry.list_subscribers(
            user_id=user_id,
            plan_id=plan_id,
            subscription_id=subscription_id,
            status=status,
        )

    def snapshot(self) -> SubscriberRegistrySnapshot:
        return self.registry.snapshot()

    def health(self) -> Mapping[str, Any]:
        return subscriber_registry_health(self.registry)

    def integrity(self) -> bool:
        return validate_subscriber_registry(self.registry)

    def info(self) -> Mapping[str, Any]:
        return {
            "engine": SUBSCRIBER_SERVICE_ENGINE,
            "version": SUBSCRIBER_SERVICE_VERSION,
            "authority": subscriber_authority_boundary(),
            "registry_count": self.registry.count(),
            "healthy": self.integrity(),
        }


# ============================================================
# SINGLETON
# ============================================================

_SUBSCRIBER_SERVICE = SubscriberService()


def get_subscriber_service() -> SubscriberService:
    return _SUBSCRIBER_SERVICE


# ============================================================
# CONVENIENCE API
# ============================================================

def resolve_subscriber_access(
    request: SubscriberRequest,
    *,
    rules: Optional[SubscriberResolutionRules] = None,
    now: Optional[datetime] = None,
) -> SubscriberResult:
    return _SUBSCRIBER_SERVICE.resolve(
        request,
        rules=rules,
        now=now,
    )


def create_subscriber_record(
    request: SubscriberAdminRequest,
) -> SubscriberAdminResult:
    return _SUBSCRIBER_SERVICE.create(request)


def get_subscriber(
    subscriber_id: str,
) -> Optional[SubscriberReference]:
    return _SUBSCRIBER_SERVICE.get(subscriber_id)


def list_subscribers(
    *,
    user_id: Optional[str] = None,
    plan_id: Optional[str] = None,
    subscription_id: Optional[str] = None,
    status: Optional[SubscriberStatus] = None,
) -> Tuple[SubscriberReference, ...]:
    return _SUBSCRIBER_SERVICE.list_subscribers(
        user_id=user_id,
        plan_id=plan_id,
        subscription_id=subscription_id,
        status=status,
    )


def subscriber_snapshot() -> SubscriberRegistrySnapshot:
    return _SUBSCRIBER_SERVICE.snapshot()


def subscriber_count() -> int:
    return _SUBSCRIBER_SERVICE.registry.count()


def subscriber_health() -> Mapping[str, Any]:
    return _SUBSCRIBER_SERVICE.health()


def subscriber_integrity() -> bool:
    return _SUBSCRIBER_SERVICE.integrity()


def subscriber_operational_check() -> bool:
    if not validate_subscriber_authority_boundary():
        return False

    if not _SUBSCRIBER_SERVICE.integrity():
        return False

    return True


def subscriber_service_authority() -> Mapping[str, bool]:
    return subscriber_authority_boundary()


def subscriber_service_info() -> Mapping[str, Any]:
    return _SUBSCRIBER_SERVICE.info()


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [
    # Constants
    "SUBSCRIBER_SERVICE_ENGINE",
    "SUBSCRIBER_SERVICE_VERSION",

    # Enums
    "SubscriberStatus",
    "SubscriberDecision",
    "SubscriberMode",
    "SubscriberPriority",
    "SubscriberContractStatus",
    "SubscriberAction",
    "SubscriberSource",
    "SubscriberDataState",
    "SubscriberConsistency",
    "SubscriberReadiness",

    # Contracts
    "SubscriberRequest",
    "SubscriberReference",
    "SubscriberContractValidation",
    "SubscriberRequirements",
    "SubscriberAssessment",
    "SubscriberResolutionRules",
    "SubscriberResult",
    "SubscriberAdminRequest",
    "SubscriberAdminResult",

    # Normalization / validation
    "normalize_subscriber_status",
    "normalize_subscriber_source",
    "validate_subscriber_request",
    "validate_subscriber_reference",
    "validate_subscriber_authority_boundary",

    # Assessment
    "evaluate_subscriber_validity",
    "evaluate_subscriber_data_state",
    "evaluate_subscriber_consistency",
    "evaluate_subscriber_requirements",
    "evaluate_subscriber_flags",
    "evaluate_subscriber_completeness",
    "evaluate_subscriber_quality",
    "evaluate_subscriber_confidence",
    "evaluate_subscriber_readiness",
    "evaluate_subscriber_eligibility",
    "build_subscriber_assessment",

    # Resolution
    "build_subscriber_resolution_rules",
    "collect_subscriber_resolution_flags",
    "collect_subscriber_restrictions",
    "resolve_subscriber",
    "resolve_subscriber_access",
    "validate_subscriber_action",
    "validate_subscriber_admin_request",

    # Registry / lifecycle
    "SubscriberRegistryEntry",
    "SubscriberRegistrySnapshot",
    "SubscriberRegistry",
    "create_subscriber",
    "create_subscriber_record",
    "update_subscriber_status",
    "activate_subscriber",
    "suspend_subscriber",
    "cancel_subscriber",
    "expire_subscriber",
    "block_subscriber",
    "unblock_subscriber",
    "update_subscriber_reference",
    "validate_subscriber_registry",
    "subscriber_registry_health",

    # Serialization / integrity
    "serialize_subscriber_reference",
    "serialize_subscriber_assessment",
    "serialize_subscriber_result",
    "serialize_subscriber_admin_result",
    "serialize_subscriber_snapshot",
    "validate_subscriber_integrity",
    "validate_subscriber_snapshot_integrity",
    "build_subscriber_summary",

    # Service
    "SubscriberService",
    "get_subscriber_service",
    "get_subscriber",
    "list_subscribers",
    "subscriber_snapshot",
    "subscriber_count",
    "subscriber_health",
    "subscriber_integrity",
    "subscriber_operational_check",
    "subscriber_service_authority",
    "subscriber_service_info",
]