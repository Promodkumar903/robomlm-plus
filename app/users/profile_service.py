# ============================================================
# ROBOMLM_PLUS
# app/users/profile_service.py
# PROFILE SERVICE — PART 1
# Foundation • Enums • Authority • Core Contracts
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


# ============================================================
# ENGINE IDENTITY
# ============================================================

PROFILE_SERVICE_ENGINE = "ROBOMLM_PROFILE_SERVICE"
PROFILE_SERVICE_VERSION = "1.0"


# ============================================================
# ENUMS
# ============================================================

class ProfileStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    INCOMPLETE = "INCOMPLETE"
    RESTRICTED = "RESTRICTED"
    SUSPENDED = "SUSPENDED"
    DISABLED = "DISABLED"
    DELETED = "DELETED"
    INVALID = "INVALID"


class ProfileMode(str, Enum):
    PAPER = "PAPER"
    DEMO = "DEMO"
    LIVE = "LIVE"
    UNKNOWN = "UNKNOWN"


class ProfilePriority(str, Enum):
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ProfileSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ProfileContractStatus(str, Enum):
    CREATED = "CREATED"
    VALID = "VALID"
    INVALID = "INVALID"
    READY = "READY"


class ProfileUpdateEvent(str, Enum):
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    ACTIVATED = "ACTIVATED"
    RESTRICTED = "RESTRICTED"
    UNRESTRICTED = "UNRESTRICTED"
    SUSPENDED = "SUSPENDED"
    REACTIVATED = "REACTIVATED"
    DISABLED = "DISABLED"
    DELETED = "DELETED"


class ProfileField(str, Enum):
    DISPLAY_NAME = "DISPLAY_NAME"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    LOCALE = "LOCALE"
    TIMEZONE = "TIMEZONE"
    COUNTRY = "COUNTRY"
    AVATAR = "AVATAR"
    BIO = "BIO"
    PREFERENCES = "PREFERENCES"
    NOTIFICATIONS = "NOTIFICATIONS"
    METADATA = "METADATA"


# ============================================================
# HELPERS
# ============================================================

def _profile_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _profile_enum(value: Any, enum_cls: Any, default: Any) -> Any:
    if isinstance(value, enum_cls):
        return value

    text = _profile_text(value).upper()
    if not text:
        return default

    try:
        return enum_cls(text)
    except (ValueError, TypeError):
        return default


def _profile_timestamp(value: Any) -> Optional[datetime]:
    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    try:
        return datetime.fromisoformat(str(value))
    except (ValueError, TypeError):
        return None


def _profile_now() -> datetime:
    return datetime.now(timezone.utc)


# ============================================================
# AUTHORITY
# ============================================================

PROFILE_SERVICE_AUTHORITY: Dict[str, bool] = {
    # Own domain authority
    "profile_domain_authority": True,
    "profile_contract_authority": True,
    "profile_metadata_authority": True,
    "profile_update_authority": True,

    # User identity remains User Service authority
    "user_identity_authority": False,
    "user_lifecycle_authority": False,

    # Authentication / credentials
    "authentication_authority": False,
    "credential_authority": False,
    "security_override_authority": False,

    # Subscription / billing
    "billing_authority": False,
    "subscription_authority": False,
    "entitlement_authority": False,

    # Market intelligence
    "market_data_authority": False,
    "evidence_generation_authority": False,
    "intelligence_generation_authority": False,
    "market_context_generation_authority": False,
    "decision_generation_authority": False,
    "d13_authority": False,
    "d13_mutation": False,

    # Risk / CAS
    "risk_generation_authority": False,
    "risk_override": False,
    "cas_generation_authority": False,
    "cas_override": False,

    # Execution
    "execution_authority": False,
    "order_authority": False,
    "position_authority": False,

    # Upstream mutation
    "upstream_mutation_authority": False,
}


# ============================================================
# CORE REQUEST CONTRACT
# ============================================================

@dataclass
class ProfileRequest:
    request_id: str = ""
    user_id: str = ""

    display_name: str = ""
    email: str = ""
    phone: str = ""

    locale: str = ""
    timezone: str = ""
    country: str = ""

    avatar: str = ""
    bio: str = ""

    preferences: Dict[str, Any] = field(default_factory=dict)
    notifications: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    status: ProfileStatus = ProfileStatus.CREATED
    mode: ProfileMode = ProfileMode.UNKNOWN
    priority: ProfilePriority = ProfilePriority.NORMAL
    update_event: ProfileUpdateEvent = ProfileUpdateEvent.UPDATED

    created_at: Optional[datetime] = None


# ============================================================
# PROFILE REFERENCE
# ============================================================

@dataclass
class ProfileReference:
    user_id: str
    profile_source: str = "app.users.profile_service"

    display_name: str = ""
    email: str = ""

    status: ProfileStatus = ProfileStatus.UNKNOWN
    mode: ProfileMode = ProfileMode.UNKNOWN

    locale: str = ""
    timezone: str = ""
    country: str = ""

    created_at: Optional[datetime] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# PROFILE CONTRACT VALIDATION
# ============================================================

@dataclass
class ProfileContractValidation:
    status: ProfileContractStatus = ProfileContractStatus.CREATED
    valid: bool = False

    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    checked_at: datetime = field(default_factory=_profile_now)

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# PROFILE RECORD
# ============================================================

@dataclass
class ProfileRecord:
    user_id: str

    display_name: str = ""
    email: str = ""
    phone: str = ""

    locale: str = ""
    timezone: str = ""
    country: str = ""

    avatar: str = ""
    bio: str = ""

    preferences: Dict[str, Any] = field(default_factory=dict)
    notifications: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    status: ProfileStatus = ProfileStatus.CREATED
    mode: ProfileMode = ProfileMode.UNKNOWN

    created_at: datetime = field(default_factory=_profile_now)
    updated_at: datetime = field(default_factory=_profile_now)
    last_seen_at: Optional[datetime] = None

    last_update_event: ProfileUpdateEvent = ProfileUpdateEvent.CREATED


# ============================================================
# SERVICE RESULT CONTRACT
# ============================================================

@dataclass
class ProfileServiceResult:
    request_id: str = ""

    reference: Optional[ProfileReference] = None
    profile: Optional[ProfileRecord] = None
    validation: Optional[ProfileContractValidation] = None

    success: bool = False

    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    event: Optional[ProfileUpdateEvent] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# REQUEST NORMALIZATION
# ============================================================

def normalize_profile_request(
    request: ProfileRequest,
) -> ProfileRequest:
    request.request_id = _profile_text(request.request_id)
    request.user_id = _profile_text(request.user_id)

    request.display_name = _profile_text(request.display_name)
    request.email = _profile_text(request.email).lower()
    request.phone = _profile_text(request.phone)

    request.locale = _profile_text(request.locale)
    request.timezone = _profile_text(request.timezone)
    request.country = _profile_text(request.country)

    request.avatar = _profile_text(request.avatar)
    request.bio = _profile_text(request.bio)

    if not isinstance(request.preferences, dict):
        request.preferences = {}

    if not isinstance(request.notifications, dict):
        request.notifications = {}

    if not isinstance(request.metadata, dict):
        request.metadata = {}

    request.status = _profile_enum(
        request.status,
        ProfileStatus,
        ProfileStatus.CREATED,
    )

    request.mode = _profile_enum(
        request.mode,
        ProfileMode,
        ProfileMode.UNKNOWN,
    )

    request.priority = _profile_enum(
        request.priority,
        ProfilePriority,
        ProfilePriority.NORMAL,
    )

    request.update_event = _profile_enum(
        request.update_event,
        ProfileUpdateEvent,
        ProfileUpdateEvent.UPDATED,
    )

    request.created_at = _profile_timestamp(request.created_at)

    return request


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_profile_request(
    request: ProfileRequest,
) -> ProfileContractValidation:

    errors: List[str] = []
    warnings: List[str] = []

    request = normalize_profile_request(request)

    if not request.request_id:
        warnings.append("request_id is empty")

    if not request.user_id:
        errors.append("user_id is required")

    if request.email and "@" not in request.email:
        errors.append("email format is invalid")

    if not isinstance(request.status, ProfileStatus):
        errors.append("status is invalid")

    if not isinstance(request.mode, ProfileMode):
        errors.append("mode is invalid")

    if not isinstance(request.priority, ProfilePriority):
        errors.append("priority is invalid")

    if not isinstance(request.update_event, ProfileUpdateEvent):
        errors.append("update_event is invalid")

    if not isinstance(request.preferences, dict):
        errors.append("preferences must be a dictionary")

    if not isinstance(request.notifications, dict):
        errors.append("notifications must be a dictionary")

    if not isinstance(request.metadata, dict):
        errors.append("metadata must be a dictionary")

    valid = not errors

    return ProfileContractValidation(
        status=(
            ProfileContractStatus.VALID
            if valid
            else ProfileContractStatus.INVALID
        ),
        valid=valid,
        errors=errors,
        warnings=warnings,
        checked_at=_profile_now(),
        metadata={
            "engine": PROFILE_SERVICE_ENGINE,
            "version": PROFILE_SERVICE_VERSION,
        },
    )


# ============================================================
# REQUEST BUILDER
# ============================================================

def build_profile_request(
    user_id: str,
    display_name: str = "",
    email: str = "",
    phone: str = "",
    locale: str = "",
    timezone: str = "",
    country: str = "",
    avatar: str = "",
    bio: str = "",
    preferences: Optional[Dict[str, Any]] = None,
    notifications: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    status: ProfileStatus = ProfileStatus.CREATED,
    mode: ProfileMode = ProfileMode.UNKNOWN,
    priority: ProfilePriority = ProfilePriority.NORMAL,
    update_event: ProfileUpdateEvent = ProfileUpdateEvent.UPDATED,
    request_id: str = "",
) -> ProfileRequest:

    request = ProfileRequest(
        request_id=request_id,
        user_id=user_id,
        display_name=display_name,
        email=email,
        phone=phone,
        locale=locale,
        timezone=timezone,
        country=country,
        avatar=avatar,
        bio=bio,
        preferences=dict(preferences or {}),
        notifications=dict(notifications or {}),
        metadata=dict(metadata or {}),
        status=status,
        mode=mode,
        priority=priority,
        update_event=update_event,
        created_at=_profile_now(),
    )

    return normalize_profile_request(request)


# ============================================================
# REFERENCE BUILDER
# ============================================================

def build_profile_reference(
    profile: ProfileRecord,
) -> ProfileReference:

    return ProfileReference(
        user_id=profile.user_id,
        profile_source="app.users.profile_service",
        display_name=profile.display_name,
        email=profile.email,
        status=profile.status,
        mode=profile.mode,
        locale=profile.locale,
        timezone=profile.timezone,
        country=profile.country,
        created_at=profile.created_at,
        metadata=dict(profile.metadata),
    )


# ============================================================
# AUTHORITY VALIDATION
# ============================================================

def validate_profile_service_authority() -> Dict[str, Any]:
    violations = [
        key
        for key, value in PROFILE_SERVICE_AUTHORITY.items()
        if key.endswith("_authority")
        and key not in {
            "profile_domain_authority",
            "profile_contract_authority",
            "profile_metadata_authority",
            "profile_update_authority",
        }
        and value is True
    ]

    return {
        "engine": PROFILE_SERVICE_ENGINE,
        "version": PROFILE_SERVICE_VERSION,
        "valid": not violations,
        "violations": violations,
        "authority": dict(PROFILE_SERVICE_AUTHORITY),
        "checked_at": _profile_now().isoformat(),
    }
# ============================================================
# PROFILE SERVICE — PART 2
# Account Security • Financial Action Controls • Requirements
# ============================================================

# ============================================================
# SECURITY / ACCOUNT ENUMS
# ============================================================

class ProfileCredentialType(str, Enum):
    ACCOUNT_PASSWORD = "ACCOUNT_PASSWORD"
    BALANCE_PASSWORD = "BALANCE_PASSWORD"
    WITHDRAWAL_PASSWORD = "WITHDRAWAL_PASSWORD"
    RECEIVE_PASSWORD = "RECEIVE_PASSWORD"


class ProfileCredentialStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    NOT_SET = "NOT_SET"
    ACTIVE = "ACTIVE"
    LOCKED = "LOCKED"
    EXPIRED = "EXPIRED"
    DISABLED = "DISABLED"
    INVALID = "INVALID"


class ProfileFinancialAction(str, Enum):
    VIEW_BALANCE = "VIEW_BALANCE"
    WITHDRAW = "WITHDRAW"
    RECEIVE = "RECEIVE"
    TRANSFER = "TRANSFER"


class ProfileFinancialActionStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    ALLOWED = "ALLOWED"
    RESTRICTED = "RESTRICTED"
    BLOCKED = "BLOCKED"
    REQUIRES_AUTHENTICATION = "REQUIRES_AUTHENTICATION"


# ============================================================
# SECURE CREDENTIAL REFERENCE
# ============================================================

@dataclass
class ProfileCredentialReference:
    user_id: str
    credential_type: ProfileCredentialType

    status: ProfileCredentialStatus = (
        ProfileCredentialStatus.NOT_SET
    )

    credential_source: str = "security_service"

    # Reference / identifier only.
    # NEVER store plaintext passwords here.
    credential_id: str = ""

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_verified_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    failed_attempts: int = 0
    lockout_until: Optional[datetime] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# FINANCIAL ACTION CONTROL
# ============================================================

@dataclass
class ProfileFinancialActionControl:
    user_id: str
    action: ProfileFinancialAction

    status: ProfileFinancialActionStatus = (
        ProfileFinancialActionStatus.UNKNOWN
    )

    required_credential: Optional[ProfileCredentialType] = None

    authentication_required: bool = True
    additional_verification_required: bool = False

    daily_limit: Optional[float] = None
    transaction_limit: Optional[float] = None

    currency: str = ""

    reason: str = ""

    updated_at: Optional[datetime] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# ACCOUNT SECURITY STATE
# ============================================================

@dataclass
class ProfileSecurityState:
    user_id: str

    account_password: ProfileCredentialReference = field(
        default_factory=lambda: ProfileCredentialReference(
            user_id="",
            credential_type=ProfileCredentialType.ACCOUNT_PASSWORD,
        )
    )

    balance_password: ProfileCredentialReference = field(
        default_factory=lambda: ProfileCredentialReference(
            user_id="",
            credential_type=ProfileCredentialType.BALANCE_PASSWORD,
        )
    )

    withdrawal_password: ProfileCredentialReference = field(
        default_factory=lambda: ProfileCredentialReference(
            user_id="",
            credential_type=ProfileCredentialType.WITHDRAWAL_PASSWORD,
        )
    )

    receive_password: ProfileCredentialReference = field(
        default_factory=lambda: ProfileCredentialReference(
            user_id="",
            credential_type=ProfileCredentialType.RECEIVE_PASSWORD,
        )
    )

    account_locked: bool = False
    financial_actions_locked: bool = False

    security_level: str = "STANDARD"

    last_security_review_at: Optional[datetime] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# PROFILE REQUIREMENTS
# ============================================================

@dataclass
class ProfileRequirements:
    require_user_id: bool = True

    require_display_name: bool = False
    require_email: bool = False
    require_locale: bool = False
    require_timezone: bool = False
    require_country: bool = False

    require_account_password: bool = False
    require_balance_password: bool = False
    require_withdrawal_password: bool = False
    require_receive_password: bool = False

    require_security_state: bool = False

    minimum_completeness: float = 0.70
    minimum_confidence: float = 0.70
    minimum_quality: float = 0.70

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# PROFILE ASSESSMENT
# ============================================================

@dataclass
class ProfileAssessment:
    status: ProfileStatus = ProfileStatus.UNKNOWN

    completeness_score: float = 0.0
    confidence_score: float = 0.0
    quality_score: float = 0.0

    requirements_met: bool = False

    data_state: str = "MISSING"
    readiness: str = "NOT_READY"

    flags: List[str] = field(default_factory=list)

    credential_states: Dict[str, str] = field(
        default_factory=dict
    )

    financial_action_states: Dict[str, str] = field(
        default_factory=dict
    )

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# REQUIREMENT BUILDER
# ============================================================

def build_profile_requirements(
    require_email: bool = False,
    require_account_password: bool = False,
    require_balance_password: bool = False,
    require_withdrawal_password: bool = False,
    require_receive_password: bool = False,
    require_security_state: bool = False,
) -> ProfileRequirements:

    return ProfileRequirements(
        require_email=require_email,
        require_account_password=require_account_password,
        require_balance_password=require_balance_password,
        require_withdrawal_password=require_withdrawal_password,
        require_receive_password=require_receive_password,
        require_security_state=require_security_state,
    )


# ============================================================
# CREDENTIAL STATE EXTRACTION
# ============================================================

def _profile_credential_state(
    credential: Optional[ProfileCredentialReference],
) -> str:

    if credential is None:
        return ProfileCredentialStatus.NOT_SET.value

    if not isinstance(
        credential,
        ProfileCredentialReference,
    ):
        return ProfileCredentialStatus.INVALID.value

    return credential.status.value


# ============================================================
# SECURITY STATE ASSESSMENT
# ============================================================

def assess_profile_security_state(
    security: Optional[ProfileSecurityState],
) -> Dict[str, Any]:

    if security is None:
        return {
            "available": False,
            "account_locked": False,
            "financial_actions_locked": False,
            "credential_states": {},
        }

    credentials = {
        ProfileCredentialType.ACCOUNT_PASSWORD.value:
            _profile_credential_state(
                security.account_password
            ),

        ProfileCredentialType.BALANCE_PASSWORD.value:
            _profile_credential_state(
                security.balance_password
            ),

        ProfileCredentialType.WITHDRAWAL_PASSWORD.value:
            _profile_credential_state(
                security.withdrawal_password
            ),

        ProfileCredentialType.RECEIVE_PASSWORD.value:
            _profile_credential_state(
                security.receive_password
            ),
    }

    return {
        "available": True,
        "account_locked": security.account_locked,
        "financial_actions_locked": (
            security.financial_actions_locked
        ),
        "credential_states": credentials,
        "security_level": security.security_level,
    }


# ============================================================
# FINANCIAL ACTION REQUIREMENTS
# ============================================================

def get_profile_financial_action_control(
    user_id: str,
    action: ProfileFinancialAction,
) -> ProfileFinancialActionControl:

    credential_map = {
        ProfileFinancialAction.VIEW_BALANCE:
            ProfileCredentialType.BALANCE_PASSWORD,

        ProfileFinancialAction.WITHDRAW:
            ProfileCredentialType.WITHDRAWAL_PASSWORD,

        ProfileFinancialAction.RECEIVE:
            ProfileCredentialType.RECEIVE_PASSWORD,

        ProfileFinancialAction.TRANSFER:
            ProfileCredentialType.WITHDRAWAL_PASSWORD,
    }

    required_credential = credential_map.get(action)

    return ProfileFinancialActionControl(
        user_id=_profile_text(user_id),
        action=action,
        status=(
            ProfileFinancialActionStatus.REQUIRES_AUTHENTICATION
            if required_credential is not None
            else ProfileFinancialActionStatus.UNKNOWN
        ),
        required_credential=required_credential,
        authentication_required=True,
        updated_at=_profile_now(),
    )


# ============================================================
# PROFILE COMPLETENESS
# ============================================================

def calculate_profile_completeness(
    profile: ProfileRecord,
    security: Optional[ProfileSecurityState] = None,
    requirements: Optional[ProfileRequirements] = None,
) -> float:

    requirements = requirements or ProfileRequirements()

    checks: List[bool] = []

    checks.append(bool(profile.user_id))

    if requirements.require_display_name:
        checks.append(bool(profile.display_name))

    if requirements.require_email:
        checks.append(bool(profile.email))

    if requirements.require_locale:
        checks.append(bool(profile.locale))

    if requirements.require_timezone:
        checks.append(bool(profile.timezone))

    if requirements.require_country:
        checks.append(bool(profile.country))

    if requirements.require_account_password:
        checks.append(
            security is not None
            and security.account_password.status
            == ProfileCredentialStatus.ACTIVE
        )

    if requirements.require_balance_password:
        checks.append(
            security is not None
            and security.balance_password.status
            == ProfileCredentialStatus.ACTIVE
        )

    if requirements.require_withdrawal_password:
        checks.append(
            security is not None
            and security.withdrawal_password.status
            == ProfileCredentialStatus.ACTIVE
        )

    if requirements.require_receive_password:
        checks.append(
            security is not None
            and security.receive_password.status
            == ProfileCredentialStatus.ACTIVE
        )

    if requirements.require_security_state:
        checks.append(security is not None)

    if not checks:
        return 0.0

    return sum(1.0 for value in checks if value) / len(checks)


# ============================================================
# PROFILE CONFIDENCE
# ============================================================

def calculate_profile_confidence(
    profile: ProfileRecord,
    security: Optional[ProfileSecurityState] = None,
) -> float:

    score = 1.0

    if not profile.user_id:
        score -= 0.35

    if not profile.email:
        score -= 0.10

    if profile.status == ProfileStatus.UNKNOWN:
        score -= 0.15

    if profile.mode == ProfileMode.UNKNOWN:
        score -= 0.05

    if profile.created_at is None:
        score -= 0.05

    if not isinstance(profile.metadata, dict):
        score -= 0.10

    if security is not None:
        credential_list = [
            security.account_password,
            security.balance_password,
            security.withdrawal_password,
            security.receive_password,
        ]

        invalid_credentials = sum(
            1
            for credential in credential_list
            if credential.status
            == ProfileCredentialStatus.INVALID
        )

        score -= min(0.20, invalid_credentials * 0.05)

    return max(0.0, min(1.0, score))


# ============================================================
# PROFILE QUALITY
# ============================================================

def calculate_profile_quality(
    completeness_score: float,
    confidence_score: float,
) -> float:

    completeness = max(
        0.0,
        min(1.0, float(completeness_score)),
    )

    confidence = max(
        0.0,
        min(1.0, float(confidence_score)),
    )

    # Profile quality only.
    # This is NOT trading intelligence,
    # alpha probability, risk score, or decision score.
    return (
        completeness * 0.60
        + confidence * 0.40
    )


# ============================================================
# PROFILE DATA STATE
# ============================================================

def determine_profile_data_state(
    profile: Optional[ProfileRecord],
) -> str:

    if profile is None:
        return "MISSING"

    if profile.status == ProfileStatus.INVALID:
        return "INVALID"

    populated = sum(
        bool(value)
        for value in (
            profile.user_id,
            profile.display_name,
            profile.email,
            profile.locale,
            profile.timezone,
            profile.country,
        )
    )

    if populated >= 4:
        return "COMPLETE"

    if populated >= 1:
        return "PARTIAL"

    return "MISSING"


# ============================================================
# PROFILE READINESS
# ============================================================

def determine_profile_readiness(
    profile: Optional[ProfileRecord],
    assessment: ProfileAssessment,
) -> str:

    if profile is None:
        return "BLOCKED"

    if profile.status in {
        ProfileStatus.INVALID,
        ProfileStatus.DELETED,
        ProfileStatus.DISABLED,
        ProfileStatus.SUSPENDED,
    }:
        return "BLOCKED"

    if assessment.quality_score < 0.50:
        return "NOT_READY"

    if not assessment.requirements_met:
        return "CONDITIONALLY_READY"

    if (
        assessment.completeness_score < 0.70
        or assessment.confidence_score < 0.70
        or assessment.quality_score < 0.70
    ):
        return "CONDITIONALLY_READY"

    return "READY"


# ============================================================
# PROFILE ASSESSMENT BUILDER
# ============================================================

def assess_profile(
    profile: Optional[ProfileRecord],
    security: Optional[ProfileSecurityState] = None,
    requirements: Optional[ProfileRequirements] = None,
) -> ProfileAssessment:

    requirements = requirements or ProfileRequirements()

    if profile is None:
        return ProfileAssessment(
            status=ProfileStatus.UNKNOWN,
            completeness_score=0.0,
            confidence_score=0.0,
            quality_score=0.0,
            requirements_met=False,
            data_state="MISSING",
            readiness="BLOCKED",
            flags=["PROFILE_MISSING"],
        )

    completeness = calculate_profile_completeness(
        profile,
        security,
        requirements,
    )

    confidence = calculate_profile_confidence(
        profile,
        security,
    )

    quality = calculate_profile_quality(
        completeness,
        confidence,
    )

    requirement_checks = [
        (
            requirements.require_user_id,
            bool(profile.user_id),
        ),
        (
            requirements.require_display_name,
            bool(profile.display_name),
        ),
        (
            requirements.require_email,
            bool(profile.email),
        ),
        (
            requirements.require_locale,
            bool(profile.locale),
        ),
        (
            requirements.require_timezone,
            bool(profile.timezone),
        ),
        (
            requirements.require_country,
            bool(profile.country),
        ),
        (
            requirements.require_account_password,
            security is not None
            and security.account_password.status
            == ProfileCredentialStatus.ACTIVE,
        ),
        (
            requirements.require_balance_password,
            security is not None
            and security.balance_password.status
            == ProfileCredentialStatus.ACTIVE,
        ),
        (
            requirements.require_withdrawal_password,
            security is not None
            and security.withdrawal_password.status
            == ProfileCredentialStatus.ACTIVE,
        ),
        (
            requirements.require_receive_password,
            security is not None
            and security.receive_password.status
            == ProfileCredentialStatus.ACTIVE,
        ),
        (
            requirements.require_security_state,
            security is not None,
        ),
    ]

    active_requirements = [
        result
        for required, result in requirement_checks
        if required
    ]

    requirements_met = all(active_requirements)

    security_info = assess_profile_security_state(security)

    flags: List[str] = []

    if security_info.get("account_locked"):
        flags.append("ACCOUNT_LOCKED")

    if security_info.get("financial_actions_locked"):
        flags.append("FINANCIAL_ACTIONS_LOCKED")

    for credential, state in security_info.get(
        "credential_states",
        {},
    ).items():
        if state in {
            ProfileCredentialStatus.NOT_SET.value,
            ProfileCredentialStatus.LOCKED.value,
            ProfileCredentialStatus.EXPIRED.value,
            ProfileCredentialStatus.DISABLED.value,
            ProfileCredentialStatus.INVALID.value,
        }:
            flags.append(f"CREDENTIAL_{credential}_{state}")

    assessment = ProfileAssessment(
        status=profile.status,
        completeness_score=completeness,
        confidence_score=confidence,
        quality_score=quality,
        requirements_met=requirements_met,
        data_state=determine_profile_data_state(profile),
        readiness="NOT_READY",
        flags=flags,
        credential_states=security_info.get(
            "credential_states",
            {},
        ),
        metadata={
            "engine": PROFILE_SERVICE_ENGINE,
            "version": PROFILE_SERVICE_VERSION,
            "assessment_only": True,
            "password_plaintext_stored": False,
            "financial_balance_generation": False,
            "withdrawal_authority": False,
            "receive_funds_authority": False,
        },
    )

    assessment.readiness = determine_profile_readiness(
        profile,
        assessment,
    )

    return assessment
# ============================================================
# PROFILE SERVICE — PART 3
# Resolution • Security Restrictions • Financial Actions
# ============================================================

# ============================================================
# RESOLUTION ENUMS
# ============================================================

class ProfileResolutionStatus(str, Enum):
    RESOLVED = "RESOLVED"
    CONDITIONAL = "CONDITIONAL"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"


class ProfileDecision(str, Enum):
    ALLOW = "ALLOW"
    ALLOW_WITH_RESTRICTION = "ALLOW_WITH_RESTRICTION"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


# ============================================================
# RESOLUTION RULES
# ============================================================

@dataclass
class ProfileResolutionRules:
    allow_when_ready: bool = True
    allow_when_conditionally_ready: bool = True
    review_when_not_ready: bool = True

    block_when_invalid: bool = True
    block_when_disabled: bool = True
    block_when_deleted: bool = True
    block_when_suspended: bool = True
    block_when_account_locked: bool = True
    block_when_financial_actions_locked: bool = True
    block_when_authority_violation: bool = True

    minimum_quality: float = 0.70

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# PRESENTATION CONTRACT
# ============================================================

@dataclass
class ProfilePresentation:
    user_id: str = ""
    display_name: str = ""
    email: str = ""

    status: ProfileStatus = ProfileStatus.UNKNOWN
    mode: ProfileMode = ProfileMode.UNKNOWN

    readiness: str = "NOT_READY"
    decision: ProfileDecision = ProfileDecision.UNKNOWN

    quality_score: float = 0.0

    credential_states: Dict[str, str] = field(
        default_factory=dict
    )

    financial_action_states: Dict[str, str] = field(
        default_factory=dict
    )

    flags: List[str] = field(default_factory=list)
    restrictions: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# PROFILE RESULT
# ============================================================

@dataclass
class ProfileResult:
    request: Optional[ProfileRequest] = None
    reference: Optional[ProfileReference] = None
    profile: Optional[ProfileRecord] = None

    security: Optional[ProfileSecurityState] = None
    assessment: Optional[ProfileAssessment] = None
    presentation: Optional[ProfilePresentation] = None

    decision: ProfileDecision = ProfileDecision.UNKNOWN
    resolution: ProfileResolutionStatus = (
        ProfileResolutionStatus.REVIEW_REQUIRED
    )

    flags: List[str] = field(default_factory=list)
    restrictions: List[str] = field(default_factory=list)

    authority_valid: bool = False

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# SECURITY RESTRICTIONS
# ============================================================

def collect_profile_restrictions(
    profile: Optional[ProfileRecord],
    security: Optional[ProfileSecurityState],
    assessment: Optional[ProfileAssessment],
) -> List[str]:

    restrictions: List[str] = []

    if profile is None:
        restrictions.append("PROFILE_UNAVAILABLE")
        return restrictions

    if profile.status == ProfileStatus.INCOMPLETE:
        restrictions.append("PROFILE_INCOMPLETE")

    if profile.status == ProfileStatus.RESTRICTED:
        restrictions.append("PROFILE_RESTRICTED")

    if security is None:
        restrictions.append("SECURITY_STATE_UNAVAILABLE")
        restrictions.append("AUTHENTICATION_REQUIRED")

    else:
        if security.account_locked:
            restrictions.append("ACCOUNT_LOCKED")

        if security.financial_actions_locked:
            restrictions.append("FINANCIAL_ACTIONS_LOCKED")

        credential_map = {
            "ACCOUNT_PASSWORD": security.account_password,
            "BALANCE_PASSWORD": security.balance_password,
            "WITHDRAWAL_PASSWORD": security.withdrawal_password,
            "RECEIVE_PASSWORD": security.receive_password,
        }

        for name, credential in credential_map.items():
            if credential.status == ProfileCredentialStatus.NOT_SET:
                restrictions.append(f"{name}_NOT_CONFIGURED")

            elif credential.status == ProfileCredentialStatus.LOCKED:
                restrictions.append(f"{name}_LOCKED")

            elif credential.status == ProfileCredentialStatus.EXPIRED:
                restrictions.append(f"{name}_EXPIRED")

            elif credential.status == ProfileCredentialStatus.DISABLED:
                restrictions.append(f"{name}_DISABLED")

            elif credential.status == ProfileCredentialStatus.INVALID:
                restrictions.append(f"{name}_INVALID")

    if assessment is not None:
        if assessment.quality_score < 0.70:
            restrictions.append("PROFILE_QUALITY_BELOW_THRESHOLD")

        if not assessment.requirements_met:
            restrictions.append("PROFILE_REQUIREMENTS_INCOMPLETE")

    return sorted(set(restrictions))


# ============================================================
# PROFILE FLAGS
# ============================================================

def collect_profile_flags(
    profile: Optional[ProfileRecord],
    security: Optional[ProfileSecurityState],
    assessment: Optional[ProfileAssessment],
) -> List[str]:

    flags: List[str] = []

    if profile is None:
        return ["PROFILE_MISSING"]

    if profile.status == ProfileStatus.INVALID:
        flags.append("PROFILE_INVALID")

    if profile.status == ProfileStatus.INCOMPLETE:
        flags.append("PROFILE_INCOMPLETE")

    if profile.status == ProfileStatus.RESTRICTED:
        flags.append("PROFILE_RESTRICTED")

    if profile.status == ProfileStatus.SUSPENDED:
        flags.append("PROFILE_SUSPENDED")

    if profile.status == ProfileStatus.DISABLED:
        flags.append("PROFILE_DISABLED")

    if profile.status == ProfileStatus.DELETED:
        flags.append("PROFILE_DELETED")

    if security is not None:
        if security.account_locked:
            flags.append("ACCOUNT_LOCKED")

        if security.financial_actions_locked:
            flags.append("FINANCIAL_ACTIONS_LOCKED")

    if assessment is not None:
        flags.extend(assessment.flags)

    return sorted(set(flags))


# ============================================================
# FINANCIAL ACTION RESOLUTION
# ============================================================

def resolve_profile_financial_action(
    user_id: str,
    action: ProfileFinancialAction,
    security: Optional[ProfileSecurityState],
) -> ProfileFinancialActionControl:

    control = get_profile_financial_action_control(
        user_id,
        action,
    )

    if security is None:
        control.status = (
            ProfileFinancialActionStatus.REQUIRES_AUTHENTICATION
        )
        control.reason = "SECURITY_STATE_UNAVAILABLE"
        return control

    if security.account_locked:
        control.status = ProfileFinancialActionStatus.BLOCKED
        control.reason = "ACCOUNT_LOCKED"
        return control

    if security.financial_actions_locked:
        control.status = ProfileFinancialActionStatus.BLOCKED
        control.reason = "FINANCIAL_ACTIONS_LOCKED"
        return control

    credential = None

    if control.required_credential == (
        ProfileCredentialType.ACCOUNT_PASSWORD
    ):
        credential = security.account_password

    elif control.required_credential == (
        ProfileCredentialType.BALANCE_PASSWORD
    ):
        credential = security.balance_password

    elif control.required_credential == (
        ProfileCredentialType.WITHDRAWAL_PASSWORD
    ):
        credential = security.withdrawal_password

    elif control.required_credential == (
        ProfileCredentialType.RECEIVE_PASSWORD
    ):
        credential = security.receive_password

    if credential is None:
        control.status = (
            ProfileFinancialActionStatus.REQUIRES_AUTHENTICATION
        )
        control.reason = "CREDENTIAL_REQUIRED"
        return control

    if credential.status != ProfileCredentialStatus.ACTIVE:
        control.status = ProfileFinancialActionStatus.BLOCKED
        control.reason = (
            f"CREDENTIAL_{credential.status.value}"
        )
        return control

    # This service establishes the requirement/state only.
    # Actual password verification belongs to security/auth service.
    control.status = (
        ProfileFinancialActionStatus.REQUIRES_AUTHENTICATION
    )
    control.reason = "CREDENTIAL_VERIFICATION_REQUIRED"

    return control


# ============================================================
# PRESENTATION BUILDER
# ============================================================

def build_profile_presentation(
    profile: Optional[ProfileRecord],
    assessment: Optional[ProfileAssessment],
    security: Optional[ProfileSecurityState],
    decision: ProfileDecision = ProfileDecision.UNKNOWN,
) -> ProfilePresentation:

    if profile is None:
        return ProfilePresentation(
            decision=decision,
            readiness="BLOCKED",
            flags=["PROFILE_MISSING"],
            restrictions=["PROFILE_UNAVAILABLE"],
        )

    restrictions = collect_profile_restrictions(
        profile,
        security,
        assessment,
    )

    flags = collect_profile_flags(
        profile,
        security,
        assessment,
    )

    financial_states: Dict[str, str] = {}

    if security is not None:
        for action in ProfileFinancialAction:
            control = resolve_profile_financial_action(
                profile.user_id,
                action,
                security,
            )
            financial_states[action.value] = control.status.value

    return ProfilePresentation(
        user_id=profile.user_id,
        display_name=profile.display_name,
        email=profile.email,
        status=profile.status,
        mode=profile.mode,
        readiness=(
            assessment.readiness
            if assessment is not None
            else "NOT_READY"
        ),
        decision=decision,
        quality_score=(
            assessment.quality_score
            if assessment is not None
            else 0.0
        ),
        credential_states=(
            assessment.credential_states
            if assessment is not None
            else {}
        ),
        financial_action_states=financial_states,
        flags=flags,
        restrictions=restrictions,
        metadata={
            "engine": PROFILE_SERVICE_ENGINE,
            "version": PROFILE_SERVICE_VERSION,
            "password_verification": False,
            "balance_mutation": False,
            "withdrawal_execution": False,
            "receive_execution": False,
        },
    )


# ============================================================
# PROFILE RESOLVER
# ============================================================

def resolve_profile(
    profile: Optional[ProfileRecord],
    security: Optional[ProfileSecurityState] = None,
    assessment: Optional[ProfileAssessment] = None,
    rules: Optional[ProfileResolutionRules] = None,
) -> ProfileResult:

    rules = rules or ProfileResolutionRules()

    authority_check = validate_profile_service_authority()
    authority_valid = bool(authority_check["valid"])

    if not authority_valid and rules.block_when_authority_violation:
        decision = ProfileDecision.BLOCK
        resolution = ProfileResolutionStatus.BLOCKED

    elif profile is None:
        decision = ProfileDecision.BLOCK
        resolution = ProfileResolutionStatus.BLOCKED

    elif profile.status == ProfileStatus.INVALID:
        decision = ProfileDecision.BLOCK
        resolution = ProfileResolutionStatus.BLOCKED

    elif (
        profile.status == ProfileStatus.DELETED
        and rules.block_when_deleted
    ):
        decision = ProfileDecision.BLOCK
        resolution = ProfileResolutionStatus.BLOCKED

    elif (
        profile.status == ProfileStatus.DISABLED
        and rules.block_when_disabled
    ):
        decision = ProfileDecision.BLOCK
        resolution = ProfileResolutionStatus.BLOCKED

    elif (
        profile.status == ProfileStatus.SUSPENDED
        and rules.block_when_suspended
    ):
        decision = ProfileDecision.BLOCK
        resolution = ProfileResolutionStatus.BLOCKED

    elif (
        security is not None
        and security.account_locked
        and rules.block_when_account_locked
    ):
        decision = ProfileDecision.BLOCK
        resolution = ProfileResolutionStatus.BLOCKED

    elif (
        security is not None
        and security.financial_actions_locked
        and rules.block_when_financial_actions_locked
    ):
        decision = ProfileDecision.ALLOW_WITH_RESTRICTION
        resolution = ProfileResolutionStatus.CONDITIONAL

    elif assessment is None:
        decision = ProfileDecision.REVIEW_REQUIRED
        resolution = ProfileResolutionStatus.REVIEW_REQUIRED

    elif assessment.readiness == "BLOCKED":
        decision = ProfileDecision.BLOCK
        resolution = ProfileResolutionStatus.BLOCKED

    elif assessment.readiness == "NOT_READY":
        decision = ProfileDecision.REVIEW_REQUIRED
        resolution = ProfileResolutionStatus.REVIEW_REQUIRED

    elif assessment.readiness == "CONDITIONALLY_READY":
        decision = ProfileDecision.ALLOW_WITH_RESTRICTION
        resolution = ProfileResolutionStatus.CONDITIONAL

    else:
        decision = ProfileDecision.ALLOW
        resolution = ProfileResolutionStatus.RESOLVED

    presentation = build_profile_presentation(
        profile,
        assessment,
        security,
        decision,
    )

    flags = collect_profile_flags(
        profile,
        security,
        assessment,
    )

    restrictions = collect_profile_restrictions(
        profile,
        security,
        assessment,
    )

    return ProfileResult(
        request=None,
        reference=(
            build_profile_reference(profile)
            if profile is not None
            else None
        ),
        profile=profile,
        security=security,
        assessment=assessment,
        presentation=presentation,
        decision=decision,
        resolution=resolution,
        flags=flags,
        restrictions=restrictions,
        authority_valid=authority_valid,
        metadata={
            "engine": PROFILE_SERVICE_ENGINE,
            "version": PROFILE_SERVICE_VERSION,
            "profile_authority_preserved": True,
            "user_identity_mutation": False,
            "authentication_authority": False,
            "credential_verification": False,
            "billing_authority": False,
            "balance_mutation": False,
            "withdrawal_authority": False,
            "receive_authority": False,
            "transfer_authority": False,
        },
    )


# ============================================================
# RESULT VALIDATION
# ============================================================

def validate_profile_result(
    result: ProfileResult,
) -> Dict[str, Any]:

    errors: List[str] = []

    if not isinstance(result, ProfileResult):
        return {
            "valid": False,
            "errors": ["result must be a ProfileResult"],
        }

    if result.profile is not None:
        if not result.profile.user_id:
            errors.append("profile user_id is required")

    if result.assessment is not None:
        if not 0.0 <= result.assessment.quality_score <= 1.0:
            errors.append("assessment quality_score is invalid")

    if result.presentation is not None:
        if not 0.0 <= result.presentation.quality_score <= 1.0:
            errors.append(
                "presentation quality_score is invalid"
            )

    if not isinstance(result.authority_valid, bool):
        errors.append("authority_valid must be boolean")

    # Security invariant:
    # plaintext credentials must never enter ProfileResult.
    if result.metadata.get("password_plaintext") is not None:
        errors.append("plaintext password detected")

    return {
        "valid": not errors,
        "errors": errors,
        "checked_at": _profile_now().isoformat(),
    }
# ============================================================
# PROFILE SERVICE — PART 4
# Registry • Service • Security State Management
# ============================================================

# ============================================================
# REGISTRY CONTRACTS
# ============================================================

@dataclass
class ProfileRegistryEntry:
    user_id: str
    reference: ProfileReference

    created_at: datetime = field(default_factory=_profile_now)
    updated_at: datetime = field(default_factory=_profile_now)

    active: bool = True

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProfileRegistrySnapshot:
    engine: str = PROFILE_SERVICE_ENGINE
    version: str = PROFILE_SERVICE_VERSION

    entries: List[ProfileRegistryEntry] = field(
        default_factory=list
    )

    count: int = 0
    captured_at: datetime = field(default_factory=_profile_now)

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# PROFILE REGISTRY
# ============================================================

class ProfileRegistry:

    def __init__(self) -> None:
        self._entries: Dict[str, ProfileRegistryEntry] = {}

    def exists(self, user_id: str) -> bool:
        return _profile_text(user_id) in self._entries

    def get(
        self,
        user_id: str,
    ) -> Optional[ProfileReference]:

        entry = self._entries.get(
            _profile_text(user_id)
        )

        if entry is None or not entry.active:
            return None

        return entry.reference

    def get_entry(
        self,
        user_id: str,
    ) -> Optional[ProfileRegistryEntry]:

        return self._entries.get(
            _profile_text(user_id)
        )

    def add(
        self,
        profile: ProfileRecord,
    ) -> ProfileRegistryEntry:

        user_id = _profile_text(profile.user_id)

        if not user_id:
            raise ValueError("user_id is required")

        if user_id in self._entries:
            raise ValueError(
                f"profile already registered: {user_id}"
            )

        reference = build_profile_reference(profile)

        entry = ProfileRegistryEntry(
            user_id=user_id,
            reference=reference,
            created_at=_profile_now(),
            updated_at=_profile_now(),
            active=True,
            metadata=dict(profile.metadata),
        )

        self._entries[user_id] = entry

        return entry

    def replace(
        self,
        profile: ProfileRecord,
    ) -> ProfileRegistryEntry:

        user_id = _profile_text(profile.user_id)

        if not user_id:
            raise ValueError("user_id is required")

        reference = build_profile_reference(profile)

        existing = self._entries.get(user_id)

        created_at = (
            existing.created_at
            if existing is not None
            else _profile_now()
        )

        entry = ProfileRegistryEntry(
            user_id=user_id,
            reference=reference,
            created_at=created_at,
            updated_at=_profile_now(),
            active=True,
            metadata=dict(profile.metadata),
        )

        self._entries[user_id] = entry

        return entry

    def remove(
        self,
        user_id: str,
    ) -> bool:

        user_id = _profile_text(user_id)

        entry = self._entries.get(user_id)

        if entry is None:
            return False

        entry.active = False
        entry.updated_at = _profile_now()

        return True

    def list_references(
        self,
        active_only: bool = True,
    ) -> List[ProfileReference]:

        references: List[ProfileReference] = []

        for entry in self._entries.values():

            if active_only and not entry.active:
                continue

            references.append(entry.reference)

        return references

    def snapshot(self) -> ProfileRegistrySnapshot:

        entries = list(self._entries.values())

        return ProfileRegistrySnapshot(
            engine=PROFILE_SERVICE_ENGINE,
            version=PROFILE_SERVICE_VERSION,
            entries=entries,
            count=len(entries),
            captured_at=_profile_now(),
            metadata={
                "active_count": sum(
                    1
                    for entry in entries
                    if entry.active
                ),
                "total_count": len(entries),
            },
        )

    def count(
        self,
        active_only: bool = True,
    ) -> int:

        if not active_only:
            return len(self._entries)

        return sum(
            1
            for entry in self._entries.values()
            if entry.active
        )


# ============================================================
# REGISTRY VALIDATION
# ============================================================

def validate_profile_registry(
    registry: ProfileRegistry,
) -> Dict[str, Any]:

    errors: List[str] = []

    if not isinstance(registry, ProfileRegistry):
        return {
            "valid": False,
            "errors": ["registry must be ProfileRegistry"],
        }

    for user_id, entry in registry._entries.items():

        if not user_id:
            errors.append("empty registry user_id")

        if not isinstance(
            entry,
            ProfileRegistryEntry,
        ):
            errors.append(
                f"invalid registry entry: {user_id}"
            )
            continue

        if entry.user_id != user_id:
            errors.append(
                f"user_id key mismatch: {user_id}"
            )

        if not isinstance(
            entry.reference,
            ProfileReference,
        ):
            errors.append(
                f"invalid profile reference: {user_id}"
            )

        if not isinstance(entry.active, bool):
            errors.append(
                f"invalid active state: {user_id}"
            )

    return {
        "valid": not errors,
        "errors": errors,
        "count": len(registry._entries),
        "checked_at": _profile_now().isoformat(),
    }


def profile_registry_health(
    registry: ProfileRegistry,
) -> Dict[str, Any]:

    validation = validate_profile_registry(
        registry
    )

    active_count = registry.count(
        active_only=True
    )

    total_count = registry.count(
        active_only=False
    )

    return {
        "engine": PROFILE_SERVICE_ENGINE,
        "version": PROFILE_SERVICE_VERSION,
        "healthy": bool(validation["valid"]),
        "active_count": active_count,
        "total_count": total_count,
        "errors": validation["errors"],
        "checked_at": _profile_now().isoformat(),
    }


# ============================================================
# PROFILE SERVICE
# ============================================================

class ProfileService:

    def __init__(self) -> None:
        self._registry = ProfileRegistry()
        self._security_states: Dict[
            str,
            ProfileSecurityState,
        ] = {}

    # --------------------------------------------------------
    # PROFILE CREATE
    # --------------------------------------------------------

    def create(
        self,
        request: ProfileRequest,
    ) -> ProfileServiceResult:

        request = normalize_profile_request(request)

        validation = validate_profile_request(request)

        if not validation.valid:
            return ProfileServiceResult(
                request_id=request.request_id,
                validation=validation,
                success=False,
                errors=list(validation.errors),
                warnings=list(validation.warnings),
                event=request.update_event,
            )

        profile = ProfileRecord(
            user_id=request.user_id,
            display_name=request.display_name,
            email=request.email,
            phone=request.phone,
            locale=request.locale,
            timezone=request.timezone,
            country=request.country,
            avatar=request.avatar,
            bio=request.bio,
            preferences=dict(request.preferences),
            notifications=dict(request.notifications),
            metadata=dict(request.metadata),
            status=request.status,
            mode=request.mode,
            created_at=(
                request.created_at
                or _profile_now()
            ),
            updated_at=_profile_now(),
            last_update_event=(
                ProfileUpdateEvent.CREATED
            ),
        )

        try:
            self._registry.add(profile)
        except ValueError as exc:
            return ProfileServiceResult(
                request_id=request.request_id,
                validation=validation,
                success=False,
                errors=[str(exc)],
                warnings=list(validation.warnings),
                event=request.update_event,
            )

        reference = build_profile_reference(profile)

        return ProfileServiceResult(
            request_id=request.request_id,
            reference=reference,
            profile=profile,
            validation=validation,
            success=True,
            errors=[],
            warnings=list(validation.warnings),
            event=ProfileUpdateEvent.CREATED,
            metadata={
                "engine": PROFILE_SERVICE_ENGINE,
                "version": PROFILE_SERVICE_VERSION,
            },
        )

    # --------------------------------------------------------
    # GET PROFILE
    # --------------------------------------------------------

    def get(
        self,
        user_id: str,
    ) -> Optional[ProfileReference]:

        return self._registry.get(user_id)

    def get_entry(
        self,
        user_id: str,
    ) -> Optional[ProfileRegistryEntry]:

        return self._registry.get_entry(user_id)

    # --------------------------------------------------------
    # REGISTER / REPLACE
    # --------------------------------------------------------

    def register(
        self,
        profile: ProfileRecord,
        replace: bool = False,
    ) -> ProfileRegistryEntry:

        if replace:
            return self._registry.replace(profile)

        return self._registry.add(profile)

    # --------------------------------------------------------
    # SECURITY STATE
    # --------------------------------------------------------

    def set_security_state(
        self,
        security: ProfileSecurityState,
    ) -> ProfileSecurityState:

        user_id = _profile_text(
            security.user_id
        )

        if not user_id:
            raise ValueError("user_id is required")

        security.user_id = user_id

        # Ensure credential references belong to
        # the same user.
        credentials = [
            security.account_password,
            security.balance_password,
            security.withdrawal_password,
            security.receive_password,
        ]

        for credential in credentials:
            credential.user_id = user_id

        self._security_states[user_id] = security

        return security

    def get_security_state(
        self,
        user_id: str,
    ) -> Optional[ProfileSecurityState]:

        return self._security_states.get(
            _profile_text(user_id)
        )

    # --------------------------------------------------------
    # ASSESSMENT
    # --------------------------------------------------------

    def assess(
        self,
        profile: ProfileRecord,
        requirements: Optional[
            ProfileRequirements
        ] = None,
    ) -> ProfileAssessment:

        security = self.get_security_state(
            profile.user_id
        )

        return assess_profile(
            profile,
            security,
            requirements,
        )

    # --------------------------------------------------------
    # RESOLUTION
    # --------------------------------------------------------

    def resolve(
        self,
        profile: ProfileRecord,
        requirements: Optional[
            ProfileRequirements
        ] = None,
        rules: Optional[
            ProfileResolutionRules
        ] = None,
    ) -> ProfileResult:

        security = self.get_security_state(
            profile.user_id
        )

        assessment = assess_profile(
            profile,
            security,
            requirements,
        )

        return resolve_profile(
            profile,
            security,
            assessment,
            rules,
        )

    # --------------------------------------------------------
    # SECURITY ACTION RESOLUTION
    # --------------------------------------------------------

    def resolve_financial_action(
        self,
        user_id: str,
        action: ProfileFinancialAction,
    ) -> ProfileFinancialActionControl:

        security = self.get_security_state(
            user_id
        )

        return resolve_profile_financial_action(
            user_id,
            action,
            security,
        )

    # --------------------------------------------------------
    # LIST / SNAPSHOT
    # --------------------------------------------------------

    def list_references(
        self,
        active_only: bool = True,
    ) -> List[ProfileReference]:

        return self._registry.list_references(
            active_only=active_only
        )

    def snapshot(self) -> ProfileRegistrySnapshot:

        return self._registry.snapshot()

    def count(
        self,
        active_only: bool = True,
    ) -> int:

        return self._registry.count(
            active_only=active_only
        )

    def health(self) -> Dict[str, Any]:

        return profile_registry_health(
            self._registry
        )

    def authority(self) -> Dict[str, Any]:

        return dict(PROFILE_SERVICE_AUTHORITY)


# ============================================================
# SINGLETON SERVICE
# ============================================================

_PROFILE_SERVICE = ProfileService()


def get_profile_service() -> ProfileService:
    return _PROFILE_SERVICE


# ============================================================
# PUBLIC HELPERS
# ============================================================

def create_profile(
    request: ProfileRequest,
) -> ProfileServiceResult:

    return get_profile_service().create(request)


def get_profile(
    user_id: str,
) -> Optional[ProfileReference]:

    return get_profile_service().get(user_id)


def get_profile_entry(
    user_id: str,
) -> Optional[ProfileRegistryEntry]:

    return get_profile_service().get_entry(user_id)


def register_profile(
    profile: ProfileRecord,
    replace: bool = False,
) -> ProfileRegistryEntry:

    return get_profile_service().register(
        profile,
        replace=replace,
    )


def set_profile_security_state(
    security: ProfileSecurityState,
) -> ProfileSecurityState:

    return get_profile_service().set_security_state(
        security
    )


def get_profile_security_state(
    user_id: str,
) -> Optional[ProfileSecurityState]:

    return get_profile_service().get_security_state(
        user_id
    )


def assess_profile_record(
    profile: ProfileRecord,
    requirements: Optional[
        ProfileRequirements
    ] = None,
) -> ProfileAssessment:

    return get_profile_service().assess(
        profile,
        requirements,
    )


def resolve_profile_record(
    profile: ProfileRecord,
    requirements: Optional[
        ProfileRequirements
    ] = None,
    rules: Optional[
        ProfileResolutionRules
    ] = None,
) -> ProfileResult:

    return get_profile_service().resolve(
        profile,
        requirements,
        rules,
    )


def resolve_profile_financial_action_state(
    user_id: str,
    action: ProfileFinancialAction,
) -> ProfileFinancialActionControl:

    return get_profile_service().resolve_financial_action(
        user_id,
        action,
    )


def list_profiles(
    active_only: bool = True,
) -> List[ProfileReference]:

    return get_profile_service().list_references(
        active_only=active_only
    )


def profile_registry_snapshot() -> ProfileRegistrySnapshot:

    return get_profile_service().snapshot()


def profile_count(
    active_only: bool = True,
) -> int:

    return get_profile_service().count(
        active_only=active_only
    )


def profile_registry_health_check() -> Dict[str, Any]:

    return get_profile_service().health()


def profile_service_authority_check() -> Dict[str, Any]:

    return validate_profile_service_authority()
# ============================================================
# PROFILE SERVICE — PART 5
# Serialization • Integrity • Summary • Operational Checks
# ============================================================

def _profile_serialize_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            str(key): _profile_serialize_value(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            _profile_serialize_value(item)
            for item in value
        ]

    if hasattr(value, "__dataclass_fields__"):
        return {
            name: _profile_serialize_value(
                getattr(value, name)
            )
            for name in value.__dataclass_fields__
        }

    return value


# ============================================================
# SERIALIZERS
# ============================================================

def serialize_profile_request(
    request: ProfileRequest,
) -> Dict[str, Any]:
    return _profile_serialize_value(request)


def serialize_profile_reference(
    reference: ProfileReference,
) -> Dict[str, Any]:
    return _profile_serialize_value(reference)


def serialize_profile_contract_validation(
    validation: ProfileContractValidation,
) -> Dict[str, Any]:
    return _profile_serialize_value(validation)


def serialize_profile_record(
    profile: ProfileRecord,
) -> Dict[str, Any]:
    return _profile_serialize_value(profile)


def serialize_profile_credential_reference(
    credential: ProfileCredentialReference,
) -> Dict[str, Any]:
    return _profile_serialize_value(credential)


def serialize_profile_financial_action_control(
    control: ProfileFinancialActionControl,
) -> Dict[str, Any]:
    return _profile_serialize_value(control)


def serialize_profile_security_state(
    security: ProfileSecurityState,
) -> Dict[str, Any]:
    return _profile_serialize_value(security)


def serialize_profile_requirements(
    requirements: ProfileRequirements,
) -> Dict[str, Any]:
    return _profile_serialize_value(requirements)


def serialize_profile_assessment(
    assessment: ProfileAssessment,
) -> Dict[str, Any]:
    return _profile_serialize_value(assessment)


def serialize_profile_resolution_rules(
    rules: ProfileResolutionRules,
) -> Dict[str, Any]:
    return _profile_serialize_value(rules)


def serialize_profile_presentation(
    presentation: ProfilePresentation,
) -> Dict[str, Any]:
    return _profile_serialize_value(presentation)


def serialize_profile_result(
    result: ProfileResult,
) -> Dict[str, Any]:
    return _profile_serialize_value(result)


def serialize_profile_registry_entry(
    entry: ProfileRegistryEntry,
) -> Dict[str, Any]:
    return _profile_serialize_value(entry)


def serialize_profile_registry_snapshot(
    snapshot: ProfileRegistrySnapshot,
) -> Dict[str, Any]:
    return _profile_serialize_value(snapshot)


def serialize_profile_service_result(
    result: ProfileServiceResult,
) -> Dict[str, Any]:
    return _profile_serialize_value(result)


# ============================================================
# CREDENTIAL INTEGRITY
# ============================================================

def validate_profile_credential_integrity(
    credential: ProfileCredentialReference,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        credential,
        ProfileCredentialReference,
    ):
        return ["credential must be ProfileCredentialReference"]

    if not credential.user_id:
        errors.append("credential user_id is required")

    if not isinstance(
        credential.credential_type,
        ProfileCredentialType,
    ):
        errors.append("credential_type is invalid")

    if not isinstance(
        credential.status,
        ProfileCredentialStatus,
    ):
        errors.append("credential status is invalid")

    if credential.failed_attempts < 0:
        errors.append("failed_attempts cannot be negative")

    if not isinstance(credential.metadata, dict):
        errors.append("credential metadata must be a dictionary")

    # Critical security invariant:
    # No plaintext credential may be stored in this contract.
    forbidden_keys = {
        "password",
        "plain_password",
        "plaintext_password",
        "raw_password",
        "secret",
    }

    metadata_keys = {
        str(key).lower()
        for key in credential.metadata.keys()
    }

    if metadata_keys.intersection(forbidden_keys):
        errors.append(
            "plaintext credential field detected"
        )

    return errors


# ============================================================
# SECURITY STATE INTEGRITY
# ============================================================

def validate_profile_security_integrity(
    security: ProfileSecurityState,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        security,
        ProfileSecurityState,
    ):
        return ["security must be ProfileSecurityState"]

    if not security.user_id:
        errors.append("security user_id is required")

    credentials = [
        security.account_password,
        security.balance_password,
        security.withdrawal_password,
        security.receive_password,
    ]

    for credential in credentials:
        errors.extend(
            validate_profile_credential_integrity(
                credential
            )
        )

        if (
            credential.user_id
            and credential.user_id != security.user_id
        ):
            errors.append(
                "credential user_id does not match security user_id"
            )

    if not isinstance(security.account_locked, bool):
        errors.append(
            "account_locked must be boolean"
        )

    if not isinstance(
        security.financial_actions_locked,
        bool,
    ):
        errors.append(
            "financial_actions_locked must be boolean"
        )

    if not isinstance(security.metadata, dict):
        errors.append(
            "security metadata must be a dictionary"
        )

    return errors


# ============================================================
# PROFILE RECORD INTEGRITY
# ============================================================

def validate_profile_record_integrity(
    profile: ProfileRecord,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(profile, ProfileRecord):
        return ["profile must be ProfileRecord"]

    if not profile.user_id:
        errors.append("user_id is required")

    if profile.email and "@" not in profile.email:
        errors.append("email format is invalid")

    if not isinstance(profile.status, ProfileStatus):
        errors.append("status is invalid")

    if not isinstance(profile.mode, ProfileMode):
        errors.append("mode is invalid")

    if not isinstance(
        profile.last_update_event,
        ProfileUpdateEvent,
    ):
        errors.append(
            "last_update_event is invalid"
        )

    if profile.created_at is None:
        errors.append("created_at is required")

    if profile.updated_at is None:
        errors.append("updated_at is required")

    if not isinstance(profile.preferences, dict):
        errors.append(
            "preferences must be a dictionary"
        )

    if not isinstance(profile.notifications, dict):
        errors.append(
            "notifications must be a dictionary"
        )

    if not isinstance(profile.metadata, dict):
        errors.append(
            "metadata must be a dictionary"
        )

    return errors


# ============================================================
# PROFILE REQUEST INTEGRITY
# ============================================================

def validate_profile_request_integrity(
    request: ProfileRequest,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(request, ProfileRequest):
        return ["request must be ProfileRequest"]

    if not request.user_id:
        errors.append("user_id is required")

    if request.email and "@" not in request.email:
        errors.append("email format is invalid")

    if not isinstance(request.status, ProfileStatus):
        errors.append("status is invalid")

    if not isinstance(request.mode, ProfileMode):
        errors.append("mode is invalid")

    if not isinstance(
        request.priority,
        ProfilePriority,
    ):
        errors.append("priority is invalid")

    if not isinstance(
        request.update_event,
        ProfileUpdateEvent,
    ):
        errors.append("update_event is invalid")

    if not isinstance(request.preferences, dict):
        errors.append(
            "preferences must be a dictionary"
        )

    if not isinstance(request.notifications, dict):
        errors.append(
            "notifications must be a dictionary"
        )

    if not isinstance(request.metadata, dict):
        errors.append(
            "metadata must be a dictionary"
        )

    return errors


# ============================================================
# ASSESSMENT INTEGRITY
# ============================================================

def validate_profile_assessment_integrity(
    assessment: ProfileAssessment,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        assessment,
        ProfileAssessment,
    ):
        return ["assessment must be ProfileAssessment"]

    for field_name in (
        "completeness_score",
        "confidence_score",
        "quality_score",
    ):
        value = getattr(
            assessment,
            field_name,
        )

        if not isinstance(value, (int, float)):
            errors.append(
                f"{field_name} must be numeric"
            )
        elif not 0.0 <= float(value) <= 1.0:
            errors.append(
                f"{field_name} must be between 0 and 1"
            )

    valid_states = {
        "COMPLETE",
        "PARTIAL",
        "MISSING",
        "INVALID",
    }

    valid_readiness = {
        "READY",
        "CONDITIONALLY_READY",
        "NOT_READY",
        "BLOCKED",
    }

    if assessment.data_state not in valid_states:
        errors.append("data_state is invalid")

    if assessment.readiness not in valid_readiness:
        errors.append("readiness is invalid")

    if not isinstance(
        assessment.requirements_met,
        bool,
    ):
        errors.append(
            "requirements_met must be boolean"
        )

    if not isinstance(assessment.flags, list):
        errors.append("flags must be a list")

    if not isinstance(
        assessment.credential_states,
        dict,
    ):
        errors.append(
            "credential_states must be a dictionary"
        )

    if not isinstance(
        assessment.financial_action_states,
        dict,
    ):
        errors.append(
            "financial_action_states must be a dictionary"
        )

    return errors


# ============================================================
# RESULT INTEGRITY
# ============================================================

def validate_profile_result_integrity(
    result: ProfileResult,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(result, ProfileResult):
        return ["result must be ProfileResult"]

    if result.profile is not None:
        errors.extend(
            validate_profile_record_integrity(
                result.profile
            )
        )

    if result.security is not None:
        errors.extend(
            validate_profile_security_integrity(
                result.security
            )
        )

    if result.assessment is not None:
        errors.extend(
            validate_profile_assessment_integrity(
                result.assessment
            )
        )

    if result.reference is not None:
        if not isinstance(
            result.reference,
            ProfileReference,
        ):
            errors.append(
                "reference is invalid"
            )

    if result.presentation is not None:
        if not isinstance(
            result.presentation,
            ProfilePresentation,
        ):
            errors.append(
                "presentation is invalid"
            )

    if not isinstance(
        result.decision,
        ProfileDecision,
    ):
        errors.append(
            "decision is invalid"
        )

    if not isinstance(
        result.resolution,
        ProfileResolutionStatus,
    ):
        errors.append(
            "resolution is invalid"
        )

    if not isinstance(
        result.authority_valid,
        bool,
    ):
        errors.append(
            "authority_valid must be boolean"
        )

    if not isinstance(result.flags, list):
        errors.append("flags must be a list")

    if not isinstance(
        result.restrictions,
        list,
    ):
        errors.append(
            "restrictions must be a list"
        )

    if not isinstance(result.metadata, dict):
        errors.append(
            "metadata must be a dictionary"
        )

    return errors


# ============================================================
# SERVICE RESULT INTEGRITY
# ============================================================

def validate_profile_service_result_integrity(
    result: ProfileServiceResult,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        result,
        ProfileServiceResult,
    ):
        return [
            "result must be ProfileServiceResult"
        ]

    if result.profile is not None:
        errors.extend(
            validate_profile_record_integrity(
                result.profile
            )
        )

    if result.reference is not None:
        if not isinstance(
            result.reference,
            ProfileReference,
        ):
            errors.append(
                "reference is invalid"
            )

    if result.validation is not None:
        if not isinstance(
            result.validation,
            ProfileContractValidation,
        ):
            errors.append(
                "validation is invalid"
            )

    if not isinstance(result.success, bool):
        errors.append(
            "success must be boolean"
        )

    if not isinstance(result.errors, list):
        errors.append(
            "errors must be a list"
        )

    if not isinstance(result.warnings, list):
        errors.append(
            "warnings must be a list"
        )

    if not isinstance(result.metadata, dict):
        errors.append(
            "metadata must be a dictionary"
        )

    return errors


# ============================================================
# REGISTRY SNAPSHOT INTEGRITY
# ============================================================

def validate_profile_registry_snapshot_integrity(
    snapshot: ProfileRegistrySnapshot,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        snapshot,
        ProfileRegistrySnapshot,
    ):
        return [
            "snapshot must be ProfileRegistrySnapshot"
        ]

    if snapshot.engine != PROFILE_SERVICE_ENGINE:
        errors.append("engine mismatch")

    if snapshot.version != PROFILE_SERVICE_VERSION:
        errors.append("version mismatch")

    if not isinstance(snapshot.entries, list):
        errors.append("entries must be a list")
    else:
        for entry in snapshot.entries:

            if not isinstance(
                entry,
                ProfileRegistryEntry,
            ):
                errors.append(
                    "invalid registry entry"
                )
                continue

            if not entry.user_id:
                errors.append(
                    "registry entry user_id is required"
                )

            if not isinstance(
                entry.reference,
                ProfileReference,
            ):
                errors.append(
                    f"invalid reference: {entry.user_id}"
                )

            if not isinstance(
                entry.active,
                bool,
            ):
                errors.append(
                    f"invalid active state: {entry.user_id}"
                )

    if snapshot.count != len(snapshot.entries):
        errors.append("snapshot count mismatch")

    return errors


# ============================================================
# COMPLETE SERVICE INTEGRITY CHECK
# ============================================================

def profile_service_integrity_check(
    profile: Optional[ProfileRecord] = None,
    security: Optional[ProfileSecurityState] = None,
    assessment: Optional[ProfileAssessment] = None,
    result: Optional[ProfileResult] = None,
) -> Dict[str, Any]:

    errors: List[str] = []

    if profile is not None:
        errors.extend(
            validate_profile_record_integrity(
                profile
            )
        )

    if security is not None:
        errors.extend(
            validate_profile_security_integrity(
                security
            )
        )

    if assessment is not None:
        errors.extend(
            validate_profile_assessment_integrity(
                assessment
            )
        )

    if result is not None:
        errors.extend(
            validate_profile_result_integrity(
                result
            )
        )

    return {
        "engine": PROFILE_SERVICE_ENGINE,
        "version": PROFILE_SERVICE_VERSION,
        "valid": not errors,
        "errors": errors,
        "checked_at": _profile_now().isoformat(),
        "security_invariant": (
            "PLAINTEXT_CREDENTIALS_FORBIDDEN"
        ),
    }


# ============================================================
# PROFILE SUMMARY
# ============================================================

def profile_service_summary(
    profile: Optional[ProfileRecord] = None,
    security: Optional[ProfileSecurityState] = None,
    assessment: Optional[ProfileAssessment] = None,
    result: Optional[ProfileResult] = None,
) -> Dict[str, Any]:

    summary: Dict[str, Any] = {
        "engine": PROFILE_SERVICE_ENGINE,
        "version": PROFILE_SERVICE_VERSION,
        "user_id": None,
        "status": None,
        "mode": None,
        "readiness": None,
        "decision": None,
        "resolution": None,
        "quality_score": None,
        "credential_states": {},
        "financial_action_states": {},
        "flags": [],
        "restrictions": [],
        "authority_valid": None,
    }

    if profile is not None:
        summary["user_id"] = profile.user_id
        summary["status"] = profile.status.value
        summary["mode"] = profile.mode.value

    if assessment is not None:
        summary["readiness"] = assessment.readiness
        summary["quality_score"] = (
            assessment.quality_score
        )
        summary["credential_states"] = dict(
            assessment.credential_states
        )
        summary["financial_action_states"] = dict(
            assessment.financial_action_states
        )
        summary["flags"] = list(
            assessment.flags
        )

    if result is not None:
        summary["authority_valid"] = (
            result.authority_valid
        )
        summary["decision"] = (
            result.decision.value
        )
        summary["resolution"] = (
            result.resolution.value
        )
        summary["flags"] = list(
            result.flags
        )
        summary["restrictions"] = list(
            result.restrictions
        )

        if result.presentation is not None:
            summary["readiness"] = (
                result.presentation.readiness
            )
            summary["quality_score"] = (
                result.presentation.quality_score
            )
            summary["credential_states"] = dict(
                result.presentation.credential_states
            )
            summary["financial_action_states"] = dict(
                result.presentation.financial_action_states
            )

    if security is not None:
        summary["account_locked"] = (
            security.account_locked
        )
        summary["financial_actions_locked"] = (
            security.financial_actions_locked
        )

    return summary


# ============================================================
# OPERATIONAL CHECK
# ============================================================

def profile_service_operational_check() -> Dict[str, Any]:

    service = get_profile_service()

    authority = validate_profile_service_authority()
    registry = service.health()

    return {
        "engine": PROFILE_SERVICE_ENGINE,
        "version": PROFILE_SERVICE_VERSION,
        "operational": bool(
            authority["valid"]
            and registry["healthy"]
        ),
        "authority_valid": authority["valid"],
        "registry_healthy": registry["healthy"],
        "profile_count": service.count(),
        "security_states": len(
            service._security_states
        ),
        "plaintext_password_storage": False,
        "balance_mutation_authority": False,
        "withdrawal_authority": False,
        "receive_authority": False,
        "transfer_authority": False,
        "checked_at": _profile_now().isoformat(),
    }


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [
    # Identity
    "PROFILE_SERVICE_ENGINE",
    "PROFILE_SERVICE_VERSION",
    "PROFILE_SERVICE_AUTHORITY",

    # Profile enums
    "ProfileStatus",
    "ProfileMode",
    "ProfilePriority",
    "ProfileSeverity",
    "ProfileContractStatus",
    "ProfileUpdateEvent",
    "ProfileField",

    # Security enums
    "ProfileCredentialType",
    "ProfileCredentialStatus",
    "ProfileFinancialAction",
    "ProfileFinancialActionStatus",

    # Resolution enums
    "ProfileResolutionStatus",
    "ProfileDecision",

    # Core contracts
    "ProfileRequest",
    "ProfileReference",
    "ProfileContractValidation",
    "ProfileRecord",
    "ProfileServiceResult",

    # Security contracts
    "ProfileCredentialReference",
    "ProfileFinancialActionControl",
    "ProfileSecurityState",

    # Assessment contracts
    "ProfileRequirements",
    "ProfileAssessment",

    # Resolution contracts
    "ProfileResolutionRules",
    "ProfilePresentation",
    "ProfileResult",

    # Registry contracts
    "ProfileRegistryEntry",
    "ProfileRegistrySnapshot",

    # Request / validation
    "normalize_profile_request",
    "validate_profile_request",
    "build_profile_request",
    "build_profile_reference",
    "validate_profile_service_authority",

    # Security / assessment
    "assess_profile_security_state",
    "get_profile_financial_action_control",
    "calculate_profile_completeness",
    "calculate_profile_confidence",
    "calculate_profile_quality",
    "determine_profile_data_state",
    "determine_profile_readiness",
    "assess_profile",
    
    # Resolution
    "collect_profile_restrictions",
    "collect_profile_flags",
    "resolve_profile_financial_action",
    "build_profile_presentation",
    "resolve_profile",
    "validate_profile_result",

    # Registry
    "ProfileRegistry",
    "validate_profile_registry",
    "profile_registry_health",

    # Service
    "ProfileService",
    "get_profile_service",
    "create_profile",
    "get_profile",
    "get_profile_entry",
    "register_profile",
    "set_profile_security_state",
    "get_profile_security_state",
    "assess_profile_record",
    "resolve_profile_record",
    "resolve_profile_financial_action_state",
    "list_profiles",
    "profile_registry_snapshot",
    "profile_count",
    "profile_registry_health_check",
    "profile_service_authority_check",

    # Serialization
    "serialize_profile_request",
    "serialize_profile_reference",
    "serialize_profile_contract_validation",
    "serialize_profile_record",
    "serialize_profile_credential_reference",
    "serialize_profile_financial_action_control",
    "serialize_profile_security_state",
    "serialize_profile_requirements",
    "serialize_profile_assessment",
    "serialize_profile_resolution_rules",
    "serialize_profile_presentation",
    "serialize_profile_result",
    "serialize_profile_registry_entry",
    "serialize_profile_registry_snapshot",
    "serialize_profile_service_result",

    # Integrity
    "validate_profile_credential_integrity",
    "validate_profile_security_integrity",
    "validate_profile_record_integrity",
    "validate_profile_request_integrity",
    "validate_profile_assessment_integrity",
    "validate_profile_result_integrity",
    "validate_profile_service_result_integrity",
    "validate_profile_registry_snapshot_integrity",
    "profile_service_integrity_check",

    # Operational
    "profile_service_summary",
    "profile_service_operational_check",
]