# app/ui/account/account_page.py
"""
ROBOMLM_PLUS — Account Page

Part 1: Account Presentation Foundation

Purpose
-------
Defines the presentation-layer contracts for the Account workspace.

The Account Page is responsible for:
    - account overview presentation
    - profile presentation
    - account status presentation
    - workspace-level navigation metadata
    - safe account UI state
    - display-ready account summaries

The Account Page is NOT responsible for:
    - authentication
    - password verification
    - credential storage
    - security enforcement
    - billing mutation
    - subscription authority
    - entitlement authority
    - market intelligence
    - evidence generation
    - decision generation
    - D13 modification
    - risk generation or override
    - CAS generation or bypass
    - order execution
    - position mutation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# PAGE IDENTITY
# ---------------------------------------------------------------------------

ACCOUNT_PAGE_ENGINE = "ROBOMLM_PLUS_UI_ACCOUNT"
ACCOUNT_PAGE_VERSION = "1.0"

ACCOUNT_PAGE_NAME = "Account"
ACCOUNT_PAGE_TITLE = "Account & Settings"
ACCOUNT_PAGE_DESCRIPTION = (
    "ROBOMLM account, profile and application management workspace."
)

ACCOUNT_ROUTE = "/account"


# ---------------------------------------------------------------------------
# ACCOUNT UI AUTHORITY
# ---------------------------------------------------------------------------

ACCOUNT_UI_AUTHORITY: Dict[str, bool] = {
    "account_presentation": True,
    "profile_presentation": True,
    "account_status_presentation": True,
    "account_navigation": True,
    "account_summary": True,
    "display_configuration": True,

    "authentication_authority": False,
    "credential_authority": False,
    "security_authority": False,

    "billing_authority": False,
    "subscription_authority": False,
    "entitlement_authority": False,

    "market_data_authority": False,
    "evidence_authority": False,
    "market_context_authority": False,
    "intelligence_authority": False,

    "decision_authority": False,
    "d13_authority": False,

    "risk_authority": False,
    "cas_authority": False,

    "execution_authority": False,
    "order_authority": False,
    "position_authority": False,

    "upstream_mutation": False,
}


# ---------------------------------------------------------------------------
# ENUMS
# ---------------------------------------------------------------------------

class AccountPageStatus(str, Enum):
    LOADING = "LOADING"
    READY = "READY"
    DEGRADED = "DEGRADED"
    LOCKED = "LOCKED"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class AccountPresentationMode(str, Enum):
    OVERVIEW = "OVERVIEW"
    PROFILE = "PROFILE"
    SECURITY = "SECURITY"
    BILLING = "BILLING"
    NOTIFICATIONS = "NOTIFICATIONS"
    SETTINGS = "SETTINGS"
    UNKNOWN = "UNKNOWN"


class AccountState(str, Enum):
    UNKNOWN = "UNKNOWN"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    DISABLED = "DISABLED"
    DELETED = "DELETED"


class AccountPriority(str, Enum):
    NORMAL = "NORMAL"
    IMPORTANT = "IMPORTANT"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AccountBadgeType(str, Enum):
    STATUS = "STATUS"
    PLAN = "PLAN"
    SECURITY = "SECURITY"
    PROFILE = "PROFILE"
    SYSTEM = "SYSTEM"


# ---------------------------------------------------------------------------
# NORMALIZATION HELPERS
# ---------------------------------------------------------------------------

def _account_text(
    value: Any,
    default: str = "",
) -> str:
    if value is None:
        return default

    try:
        text = str(value).strip()
    except Exception:
        return default

    return text or default


def _account_bool(
    value: Any,
    default: bool = False,
) -> bool:
    if isinstance(value, bool):
        return value

    if value is None:
        return default

    if isinstance(value, str):
        normalized = value.strip().lower()

        if normalized in {
            "true",
            "1",
            "yes",
            "on",
            "enabled",
        }:
            return True

        if normalized in {
            "false",
            "0",
            "no",
            "off",
            "disabled",
        }:
            return False

    return bool(value)


def _account_enum(
    enum_type: type[Enum],
    value: Any,
    default: Enum,
) -> Enum:
    if isinstance(value, enum_type):
        return value

    if value is None:
        return default

    try:
        return enum_type(
            str(value).strip().upper()
        )
    except (ValueError, TypeError):
        return default


def _account_now() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# ACCOUNT CONTRACTS
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AccountIdentityView:
    """
    Display-safe identity information.

    This contract intentionally contains no credentials or secrets.
    """

    user_id: str = ""
    display_name: str = ""
    email: str = ""
    avatar_url: Optional[str] = None

    verified: bool = False
    profile_complete: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class AccountStatusView:
    """
    Presentation representation of account state.

    Actual lifecycle authority remains in the user/domain service.
    """

    state: AccountState = AccountState.UNKNOWN
    label: str = "Unknown"
    description: str = ""

    active: bool = False
    restricted: bool = False

    priority: AccountPriority = AccountPriority.NORMAL

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class AccountPlanView:
    """
    Display-only subscription/plan information.

    Actual subscription and entitlement authority remains external.
    """

    plan_name: str = "Unknown"
    plan_label: str = "Plan unavailable"

    plus_visible: bool = False
    entitlement_known: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class AccountBadge:
    """
    Small presentation badge used by the Account workspace.
    """

    badge_type: AccountBadgeType
    label: str
    value: str

    priority: AccountPriority = AccountPriority.NORMAL
    visible: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class AccountAction:
    """
    Presentation navigation/action descriptor.

    Actions do not directly mutate domain state.
    """

    action_id: str
    label: str
    route: Optional[str] = None

    enabled: bool = True
    visible: bool = True

    requires_authentication: bool = False
    requires_plus: bool = False

    priority: AccountPriority = AccountPriority.NORMAL

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class AccountPageRequest:
    """
    Request used to construct an Account page presentation.
    """

    user_id: str = ""

    mode: AccountPresentationMode = (
        AccountPresentationMode.OVERVIEW
    )

    authenticated: bool = False
    plus_enabled: bool = False

    page_status: AccountPageStatus = (
        AccountPageStatus.LOADING
    )

    source: str = "ui"

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class AccountPageView:
    """
    Complete display-ready Account page contract.
    """

    page_name: str
    page_title: str
    route: str

    status: AccountPageStatus
    mode: AccountPresentationMode

    identity: AccountIdentityView
    account_status: AccountStatusView
    plan: AccountPlanView

    badges: Tuple[AccountBadge, ...] = ()
    actions: Tuple[AccountAction, ...] = ()

    authenticated: bool = False
    plus_enabled: bool = False

    generated_at: datetime = field(
        default_factory=_account_now
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ---------------------------------------------------------------------------
# DEFAULT ACCOUNT ACTIONS
# ---------------------------------------------------------------------------

DEFAULT_ACCOUNT_ACTIONS: Tuple[AccountAction, ...] = (
    AccountAction(
        action_id="account_overview",
        label="Account Overview",
        route=ACCOUNT_ROUTE,
        priority=AccountPriority.NORMAL,
    ),

    AccountAction(
        action_id="profile",
        label="Profile",
        route="/account/profile",
        priority=AccountPriority.NORMAL,
    ),

    AccountAction(
        action_id="security",
        label="Security",
        route="/account/security",
        requires_authentication=True,
        priority=AccountPriority.IMPORTANT,
    ),

    AccountAction(
        action_id="billing",
        label="Billing",
        route="/account/billing",
        requires_authentication=True,
        priority=AccountPriority.NORMAL,
    ),

    AccountAction(
        action_id="notifications",
        label="Notifications",
        route="/account/notifications",
        requires_authentication=True,
        priority=AccountPriority.NORMAL,
    ),

    AccountAction(
        action_id="settings",
        label="Settings",
        route="/account/settings",
        requires_authentication=True,
        priority=AccountPriority.NORMAL,
    ),
)


# ---------------------------------------------------------------------------
# NORMALIZATION
# ---------------------------------------------------------------------------

def normalize_account_identity(
    identity: Optional[AccountIdentityView],
) -> AccountIdentityView:
    if identity is None:
        return AccountIdentityView()

    return AccountIdentityView(
        user_id=_account_text(identity.user_id),
        display_name=_account_text(
            identity.display_name
        ),
        email=_account_text(identity.email),
        avatar_url=(
            _account_text(identity.avatar_url)
            if identity.avatar_url
            else None
        ),
        verified=_account_bool(identity.verified),
        profile_complete=_account_bool(
            identity.profile_complete
        ),
        metadata=dict(identity.metadata or {}),
    )


def normalize_account_status(
    status: Optional[AccountStatusView],
) -> AccountStatusView:
    if status is None:
        return AccountStatusView()

    state = _account_enum(
        AccountState,
        status.state,
        AccountState.UNKNOWN,
    )

    return AccountStatusView(
        state=state,
        label=_account_text(
            status.label,
            state.value.title(),
        ),
        description=_account_text(
            status.description
        ),
        active=_account_bool(status.active),
        restricted=_account_bool(
            status.restricted
        ),
        priority=_account_enum(
            AccountPriority,
            status.priority,
            AccountPriority.NORMAL,
        ),
        metadata=dict(status.metadata or {}),
    )


def normalize_account_plan(
    plan: Optional[AccountPlanView],
) -> AccountPlanView:
    if plan is None:
        return AccountPlanView()

    return AccountPlanView(
        plan_name=_account_text(
            plan.plan_name,
            "Unknown",
        ),
        plan_label=_account_text(
            plan.plan_label,
            "Plan unavailable",
        ),
        plus_visible=_account_bool(
            plan.plus_visible
        ),
        entitlement_known=_account_bool(
            plan.entitlement_known
        ),
        metadata=dict(plan.metadata or {}),
    )


# ---------------------------------------------------------------------------
# BADGE BUILDERS
# ---------------------------------------------------------------------------

def build_account_status_badge(
    status: AccountStatusView,
) -> AccountBadge:
    return AccountBadge(
        badge_type=AccountBadgeType.STATUS,
        label="Account",
        value=status.label,
        priority=status.priority,
        metadata={
            "state": status.state.value,
            "restricted": status.restricted,
        },
    )


def build_account_plan_badge(
    plan: AccountPlanView,
) -> AccountBadge:
    return AccountBadge(
        badge_type=AccountBadgeType.PLAN,
        label="Plan",
        value=plan.plan_label,
        priority=AccountPriority.NORMAL,
        metadata={
            "entitlement_known": (
                plan.entitlement_known
            ),
            "plus_visible": (
                plan.plus_visible
            ),
        },
    )


def build_profile_badge(
    identity: AccountIdentityView,
) -> AccountBadge:
    if identity.profile_complete:
        value = "Complete"
        priority = AccountPriority.NORMAL
    else:
        value = "Incomplete"
        priority = AccountPriority.IMPORTANT

    return AccountBadge(
        badge_type=AccountBadgeType.PROFILE,
        label="Profile",
        value=value,
        priority=priority,
        metadata={
            "verified": identity.verified,
        },
    )


def build_account_badges(
    identity: AccountIdentityView,
    status: AccountStatusView,
    plan: AccountPlanView,
) -> Tuple[AccountBadge, ...]:
    return (
        build_account_status_badge(status),
        build_account_plan_badge(plan),
        build_profile_badge(identity),
    )


# ---------------------------------------------------------------------------
# ACTION FILTERING
# ---------------------------------------------------------------------------

def get_account_actions(
    *,
    authenticated: bool = False,
    plus_enabled: bool = False,
    actions: Tuple[
        AccountAction, ...
    ] = DEFAULT_ACCOUNT_ACTIONS,
) -> Tuple[AccountAction, ...]:
    result: List[AccountAction] = []

    for action in actions:
        if not action.visible:
            continue

        if (
            action.requires_authentication
            and not authenticated
        ):
            continue

        if (
            action.requires_plus
            and not plus_enabled
        ):
            continue

        result.append(action)

    return tuple(result)


# ---------------------------------------------------------------------------
# ACCOUNT PAGE BUILDER
# ---------------------------------------------------------------------------

def build_account_page_view(
    request: AccountPageRequest,
    *,
    identity: Optional[AccountIdentityView] = None,
    account_status: Optional[AccountStatusView] = None,
    plan: Optional[AccountPlanView] = None,
) -> AccountPageView:
    normalized_identity = normalize_account_identity(
        identity
    )

    normalized_status = normalize_account_status(
        account_status
    )

    normalized_plan = normalize_account_plan(
        plan
    )

    authenticated = _account_bool(
        request.authenticated
    )

    plus_enabled = (
        _account_bool(request.plus_enabled)
        if authenticated
        else False
    )

    badges = build_account_badges(
        normalized_identity,
        normalized_status,
        normalized_plan,
    )

    actions = get_account_actions(
        authenticated=authenticated,
        plus_enabled=plus_enabled,
    )

    return AccountPageView(
        page_name=ACCOUNT_PAGE_NAME,
        page_title=ACCOUNT_PAGE_TITLE,
        route=ACCOUNT_ROUTE,

        status=_account_enum(
            AccountPageStatus,
            request.page_status,
            AccountPageStatus.LOADING,
        ),

        mode=_account_enum(
            AccountPresentationMode,
            request.mode,
            AccountPresentationMode.OVERVIEW,
        ),

        identity=normalized_identity,
        account_status=normalized_status,
        plan=normalized_plan,

        badges=badges,
        actions=actions,

        authenticated=authenticated,
        plus_enabled=plus_enabled,

        metadata={
            **dict(request.metadata or {}),
            "engine": ACCOUNT_PAGE_ENGINE,
            "version": ACCOUNT_PAGE_VERSION,
            "source": _account_text(
                request.source,
                "ui",
            ),
            "ui_only": True,
            "intelligence_generation": False,
            "decision_generation": False,
            "d13_modification": False,
            "risk_generation": False,
            "cas_generation": False,
            "execution": False,
        },
    )
# ---------------------------------------------------------------------------
# ACCOUNT DATA ADAPTER CONTRACTS
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AccountSourceState:
    """
    Presentation-safe container for upstream account information.

    This object does not become an authority over the source services.
    It only carries their already-authoritative outputs into the UI layer.
    """

    identity: AccountIdentityView = field(
        default_factory=AccountIdentityView
    )

    account_status: AccountStatusView = field(
        default_factory=AccountStatusView
    )

    plan: AccountPlanView = field(
        default_factory=AccountPlanView
    )

    authenticated: bool = False
    plus_enabled: bool = False

    source_available: bool = True
    source_errors: Tuple[str, ...] = ()

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class AccountSectionState:
    """
    Presentation state for one Account workspace section.
    """

    section_id: str
    title: str
    description: str

    route: Optional[str] = None

    visible: bool = True
    enabled: bool = True

    status: AccountPageStatus = (
        AccountPageStatus.READY
    )

    priority: AccountPriority = (
        AccountPriority.NORMAL
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


DEFAULT_ACCOUNT_SECTIONS: Tuple[
    AccountSectionState, ...
] = (
    AccountSectionState(
        section_id="profile",
        title="Profile",
        description=(
            "Manage display identity and profile information."
        ),
        route="/account/profile",
    ),

    AccountSectionState(
        section_id="security",
        title="Security",
        description=(
            "Review account security and access controls."
        ),
        route="/account/security",
        priority=AccountPriority.IMPORTANT,
    ),

    AccountSectionState(
        section_id="billing",
        title="Billing",
        description=(
            "Review subscription and billing information."
        ),
        route="/account/billing",
    ),

    AccountSectionState(
        section_id="notifications",
        title="Notifications",
        description=(
            "Manage application notification preferences."
        ),
        route="/account/notifications",
    ),

    AccountSectionState(
        section_id="settings",
        title="Settings",
        description=(
            "Configure application-level preferences."
        ),
        route="/account/settings",
    ),
)


# ---------------------------------------------------------------------------
# SOURCE NORMALIZATION
# ---------------------------------------------------------------------------

def normalize_account_source_state(
    source: Optional[AccountSourceState],
) -> AccountSourceState:
    """
    Normalize upstream account information before presentation.

    Important:
        No new business truth is calculated here.
        Existing source truth is normalized only.
    """

    if source is None:
        return AccountSourceState(
            source_available=False,
            source_errors=(
                "Account source unavailable",
            ),
        )

    authenticated = _account_bool(
        source.authenticated
    )

    plus_enabled = (
        _account_bool(source.plus_enabled)
        if authenticated
        else False
    )

    errors = tuple(
        _account_text(error)
        for error in source.source_errors
        if _account_text(error)
    )

    return AccountSourceState(
        identity=normalize_account_identity(
            source.identity
        ),

        account_status=normalize_account_status(
            source.account_status
        ),

        plan=normalize_account_plan(
            source.plan
        ),

        authenticated=authenticated,
        plus_enabled=plus_enabled,

        source_available=_account_bool(
            source.source_available,
            True,
        ),

        source_errors=errors,

        metadata=dict(
            source.metadata or {}
        ),
    )


# ---------------------------------------------------------------------------
# PRESENTATION READINESS
# ---------------------------------------------------------------------------

def evaluate_account_presentation_status(
    source: AccountSourceState,
) -> AccountPageStatus:
    """
    Determine UI presentation state from source availability.

    This is NOT account lifecycle authority.
    """

    if not source.authenticated:
        return AccountPageStatus.LOCKED

    if not source.source_available:
        return AccountPageStatus.DEGRADED

    if source.source_errors:
        return AccountPageStatus.DEGRADED

    if (
        source.account_status.state
        in {
            AccountState.SUSPENDED,
            AccountState.DISABLED,
        }
    ):
        return AccountPageStatus.LOCKED

    if (
        source.account_status.state
        == AccountState.UNKNOWN
    ):
        return AccountPageStatus.DEGRADED

    return AccountPageStatus.READY


# ---------------------------------------------------------------------------
# SECTION AVAILABILITY
# ---------------------------------------------------------------------------

def build_account_sections(
    source: AccountSourceState,
    *,
    sections: Tuple[
        AccountSectionState, ...
    ] = DEFAULT_ACCOUNT_SECTIONS,
) -> Tuple[AccountSectionState, ...]:
    """
    Build section visibility/enabled state.

    The UI may hide or disable a section, but it never grants
    authority that the underlying domain service does not provide.
    """

    result: List[AccountSectionState] = []

    authenticated = source.authenticated
    account_locked = (
        source.account_status.state
        in {
            AccountState.SUSPENDED,
            AccountState.DISABLED,
        }
    )

    for section in sections:
        visible = section.visible
        enabled = section.enabled

        if section.section_id != "profile":
            enabled = (
                enabled
                and authenticated
                and not account_locked
            )

        if section.section_id == "billing":
            # Billing page owns billing semantics.
            # Account page only controls presentation access.
            enabled = (
                enabled
                and authenticated
            )

        if section.section_id == "security":
            enabled = (
                enabled
                and authenticated
            )

        result.append(
            AccountSectionState(
                section_id=section.section_id,
                title=section.title,
                description=section.description,
                route=section.route,
                visible=visible,
                enabled=enabled,
                status=(
                    AccountPageStatus.READY
                    if enabled
                    else AccountPageStatus.LOCKED
                ),
                priority=section.priority,
                metadata={
                    **dict(section.metadata or {}),
                    "presentation_only": True,
                    "authority_owner_external": True,
                },
            )
        )

    return tuple(result)


# ---------------------------------------------------------------------------
# ACCOUNT DISPLAY NAME
# ---------------------------------------------------------------------------

def resolve_account_display_name(
    identity: AccountIdentityView,
) -> str:
    """
    Resolve the safest display label.

    Priority:
        display_name → email → generic Account

    This does not modify the source identity.
    """

    display_name = _account_text(
        identity.display_name
    )

    if display_name:
        return display_name

    email = _account_text(
        identity.email
    )

    if email:
        return email

    return "Account"


# ---------------------------------------------------------------------------
# ACCOUNT STATUS MESSAGE
# ---------------------------------------------------------------------------

def build_account_status_message(
    source: AccountSourceState,
) -> str:
    """
    Produce presentation text from existing source state.
    """

    if not source.authenticated:
        return (
            "Sign in to access your account workspace."
        )

    if not source.source_available:
        return (
            "Account information is temporarily unavailable."
        )

    if source.account_status.state == AccountState.ACTIVE:
        return (
            "Your ROBOMLM account is active."
        )

    if source.account_status.state == AccountState.SUSPENDED:
        return (
            "Account access is currently restricted."
        )

    if source.account_status.state == AccountState.DISABLED:
        return (
            "Account access is currently disabled."
        )

    if source.account_status.state == AccountState.INACTIVE:
        return (
            "Your account is currently inactive."
        )

    return (
        "Account status is currently unavailable."
    )


# ---------------------------------------------------------------------------
# ACCOUNT SUMMARY
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AccountSummaryView:
    """
    High-level presentation summary.

    No financial balance, trading performance, risk score,
    intelligence score or decision score is calculated here.
    """

    display_name: str
    email: str

    status_label: str
    status_message: str

    plan_label: str

    profile_complete: bool
    verified: bool

    authenticated: bool
    plus_enabled: bool

    priority: AccountPriority = (
        AccountPriority.NORMAL
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def build_account_summary(
    source: AccountSourceState,
) -> AccountSummaryView:
    """
    Build display-only Account summary from upstream truth.
    """

    status = source.account_status

    if status.restricted:
        priority = AccountPriority.HIGH
    elif status.state == AccountState.UNKNOWN:
        priority = AccountPriority.IMPORTANT
    else:
        priority = AccountPriority.NORMAL

    return AccountSummaryView(
        display_name=resolve_account_display_name(
            source.identity
        ),

        email=_account_text(
            source.identity.email
        ),

        status_label=_account_text(
            status.label,
            "Unknown",
        ),

        status_message=build_account_status_message(
            source
        ),

        plan_label=_account_text(
            source.plan.plan_label,
            "Plan unavailable",
        ),

        profile_complete=(
            source.identity.profile_complete
        ),

        verified=source.identity.verified,

        authenticated=source.authenticated,
        plus_enabled=source.plus_enabled,

        priority=priority,

        metadata={
            "ui_only": True,
            "source_available": (
                source.source_available
            ),
        },
    )


# ---------------------------------------------------------------------------
# ACCOUNT PAGE COMPOSITION
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AccountPageComposition:
    """
    Complete presentation composition for Account workspace.
    """

    page: AccountPageView
    summary: AccountSummaryView

    sections: Tuple[
        AccountSectionState, ...
    ] = ()

    status_message: str = ""

    errors: Tuple[str, ...] = ()

    generated_at: datetime = field(
        default_factory=_account_now
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def compose_account_page(
    request: AccountPageRequest,
    *,
    source: Optional[AccountSourceState] = None,
) -> AccountPageComposition:
    """
    Compose the Account workspace from upstream account truth.

    Flow:
        Upstream Account Data
            ↓
        Normalize
            ↓
        Presentation Readiness
            ↓
        Summary
            ↓
        Sections
            ↓
        Account Page View
            ↓
        Final UI Composition
    """

    normalized = normalize_account_source_state(
        source
    )

    presentation_status = (
        evaluate_account_presentation_status(
            normalized
        )
    )

    effective_request = AccountPageRequest(
        user_id=_account_text(
            request.user_id,
            normalized.identity.user_id,
        ),

        mode=_account_enum(
            AccountPresentationMode,
            request.mode,
            AccountPresentationMode.OVERVIEW,
        ),

        authenticated=normalized.authenticated,
        plus_enabled=normalized.plus_enabled,

        page_status=presentation_status,

        source=_account_text(
            request.source,
            "account_service",
        ),

        metadata={
            **dict(request.metadata or {}),
            "composition": "account_page",
            "presentation_only": True,
        },
    )

    page = build_account_page_view(
        effective_request,
        identity=normalized.identity,
        account_status=normalized.account_status,
        plan=normalized.plan,
    )

    summary = build_account_summary(
        normalized
    )

    sections = build_account_sections(
        normalized
    )

    status_message = build_account_status_message(
        normalized
    )

    errors = tuple(
        normalized.source_errors
    )

    return AccountPageComposition(
        page=page,
        summary=summary,
        sections=sections,
        status_message=status_message,
        errors=errors,
        metadata={
            "engine": ACCOUNT_PAGE_ENGINE,
            "version": ACCOUNT_PAGE_VERSION,
            "ui_only": True,
            "upstream_truth_preserved": True,
            "decision_authority": False,
            "d13_authority": False,
            "risk_authority": False,
            "cas_authority": False,
            "execution_authority": False,
        },
    )
# ---------------------------------------------------------------------------
# ACCOUNT INTERACTION
# ---------------------------------------------------------------------------

class AccountInteraction(str, Enum):
    OPEN_OVERVIEW = "OPEN_OVERVIEW"
    OPEN_PROFILE = "OPEN_PROFILE"
    OPEN_SECURITY = "OPEN_SECURITY"
    OPEN_BILLING = "OPEN_BILLING"
    OPEN_NOTIFICATIONS = "OPEN_NOTIFICATIONS"
    OPEN_SETTINGS = "OPEN_SETTINGS"
    REFRESH = "REFRESH"
    LOCK = "LOCK"
    NONE = "NONE"


ACCOUNT_INTERACTION_ROUTES: Dict[
    AccountInteraction, str
] = {
    AccountInteraction.OPEN_OVERVIEW: ACCOUNT_ROUTE,
    AccountInteraction.OPEN_PROFILE: "/account/profile",
    AccountInteraction.OPEN_SECURITY: "/account/security",
    AccountInteraction.OPEN_BILLING: "/account/billing",
    AccountInteraction.OPEN_NOTIFICATIONS: (
        "/account/notifications"
    ),
    AccountInteraction.OPEN_SETTINGS: "/account/settings",
}


def normalize_account_interaction(
    value: Any,
) -> AccountInteraction:
    return _account_enum(
        AccountInteraction,
        value,
        AccountInteraction.NONE,
    )


# ---------------------------------------------------------------------------
# ACCOUNT SESSION STATE
# ---------------------------------------------------------------------------

@dataclass
class AccountPageState:
    """
    Mutable UI-local state.

    This state is intentionally separate from domain/account authority.
    """

    user_id: str = ""

    authenticated: bool = False
    plus_enabled: bool = False

    mode: AccountPresentationMode = (
        AccountPresentationMode.OVERVIEW
    )

    status: AccountPageStatus = (
        AccountPageStatus.LOADING
    )

    current_route: str = ACCOUNT_ROUTE

    initialized: bool = False
    ready: bool = False
    locked: bool = False

    interaction_count: int = 0
    refresh_count: int = 0

    last_interaction: AccountInteraction = (
        AccountInteraction.NONE
    )

    last_error: Optional[str] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def create_account_page_state(
    *,
    user_id: str = "",
    authenticated: bool = False,
    plus_enabled: bool = False,
) -> AccountPageState:
    authenticated = _account_bool(
        authenticated
    )

    return AccountPageState(
        user_id=_account_text(user_id),
        authenticated=authenticated,
        plus_enabled=(
            _account_bool(plus_enabled)
            if authenticated
            else False
        ),
        mode=AccountPresentationMode.OVERVIEW,
        status=(
            AccountPageStatus.LOADING
            if authenticated
            else AccountPageStatus.LOCKED
        ),
        current_route=ACCOUNT_ROUTE,
        initialized=False,
        ready=False,
        locked=not authenticated,
        metadata={
            "engine": ACCOUNT_PAGE_ENGINE,
            "version": ACCOUNT_PAGE_VERSION,
            "ui_only": True,
        },
    )


def normalize_account_page_state(
    state: Optional[AccountPageState],
) -> AccountPageState:
    if state is None:
        return create_account_page_state()

    authenticated = _account_bool(
        state.authenticated
    )

    plus_enabled = (
        _account_bool(state.plus_enabled)
        if authenticated
        else False
    )

    mode = _account_enum(
        AccountPresentationMode,
        state.mode,
        AccountPresentationMode.OVERVIEW,
    )

    status = _account_enum(
        AccountPageStatus,
        state.status,
        AccountPageStatus.UNKNOWN,
    )

    route = _account_text(
        state.current_route,
        ACCOUNT_ROUTE,
    )

    if not route.startswith("/"):
        route = ACCOUNT_ROUTE

    return AccountPageState(
        user_id=_account_text(state.user_id),
        authenticated=authenticated,
        plus_enabled=plus_enabled,
        mode=mode,
        status=status,
        current_route=route,
        initialized=_account_bool(
            state.initialized
        ),
        ready=_account_bool(state.ready),
        locked=_account_bool(
            state.locked
        ) or not authenticated,
        interaction_count=max(
            0,
            int(state.interaction_count or 0),
        ),
        refresh_count=max(
            0,
            int(state.refresh_count or 0),
        ),
        last_interaction=normalize_account_interaction(
            state.last_interaction
        ),
        last_error=(
            _account_text(state.last_error)
            if state.last_error
            else None
        ),
        metadata=dict(state.metadata or {}),
    )


# ---------------------------------------------------------------------------
# ROUTE → PRESENTATION MODE
# ---------------------------------------------------------------------------

def route_to_account_mode(
    route: str,
) -> AccountPresentationMode:
    normalized = _account_text(
        route,
        ACCOUNT_ROUTE,
    )

    mapping = {
        ACCOUNT_ROUTE: AccountPresentationMode.OVERVIEW,
        "/account/profile": AccountPresentationMode.PROFILE,
        "/account/security": AccountPresentationMode.SECURITY,
        "/account/billing": AccountPresentationMode.BILLING,
        "/account/notifications": (
            AccountPresentationMode.NOTIFICATIONS
        ),
        "/account/settings": AccountPresentationMode.SETTINGS,
    }

    return mapping.get(
        normalized,
        AccountPresentationMode.UNKNOWN,
    )


# ---------------------------------------------------------------------------
# PRESENTATION ACCESS
# ---------------------------------------------------------------------------

def evaluate_account_route_access(
    route: str,
    *,
    authenticated: bool,
    plus_enabled: bool = False,
) -> Tuple[bool, str]:
    """
    Presentation-only access evaluation.

    Actual authentication, subscription and entitlement authority
    remains outside this page.
    """

    normalized = _account_text(
        route,
        ACCOUNT_ROUTE,
    )

    known_routes = {
        ACCOUNT_ROUTE,
        "/account/profile",
        "/account/security",
        "/account/billing",
        "/account/notifications",
        "/account/settings",
    }

    if normalized not in known_routes:
        return False, "ACCOUNT_ROUTE_NOT_FOUND"

    if not authenticated:
        return False, "AUTHENTICATION_REQUIRED"

    # Account pages currently do not claim PLUS authority.
    # plus_enabled is therefore intentionally not used to grant access.

    return True, "ALLOWED"


# ---------------------------------------------------------------------------
# INTERACTION RESOLUTION
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AccountInteractionResult:
    interaction: AccountInteraction

    requested_route: Optional[str]
    resolved_route: str

    allowed: bool
    reason: str

    mode: AccountPresentationMode

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def resolve_account_interaction(
    interaction: Any,
    *,
    authenticated: bool,
    plus_enabled: bool = False,
) -> AccountInteractionResult:
    normalized_interaction = (
        normalize_account_interaction(
            interaction
        )
    )

    if normalized_interaction == AccountInteraction.NONE:
        return AccountInteractionResult(
            interaction=normalized_interaction,
            requested_route=None,
            resolved_route=ACCOUNT_ROUTE,
            allowed=False,
            reason="NO_INTERACTION",
            mode=AccountPresentationMode.OVERVIEW,
            metadata={
                "ui_only": True,
            },
        )

    if normalized_interaction == AccountInteraction.REFRESH:
        return AccountInteractionResult(
            interaction=normalized_interaction,
            requested_route=ACCOUNT_ROUTE,
            resolved_route=ACCOUNT_ROUTE,
            allowed=authenticated,
            reason=(
                "ALLOWED"
                if authenticated
                else "AUTHENTICATION_REQUIRED"
            ),
            mode=AccountPresentationMode.OVERVIEW,
            metadata={
                "refresh": True,
                "ui_only": True,
            },
        )

    if normalized_interaction == AccountInteraction.LOCK:
        return AccountInteractionResult(
            interaction=normalized_interaction,
            requested_route=ACCOUNT_ROUTE,
            resolved_route=ACCOUNT_ROUTE,
            allowed=True,
            reason="UI_LOCK_REQUESTED",
            mode=AccountPresentationMode.OVERVIEW,
            metadata={
                "ui_lock_only": True,
                "domain_security_unchanged": True,
            },
        )

    route = ACCOUNT_INTERACTION_ROUTES.get(
        normalized_interaction
    )

    if route is None:
        return AccountInteractionResult(
            interaction=normalized_interaction,
            requested_route=None,
            resolved_route=ACCOUNT_ROUTE,
            allowed=False,
            reason="UNSUPPORTED_INTERACTION",
            mode=AccountPresentationMode.OVERVIEW,
        )

    allowed, reason = evaluate_account_route_access(
        route,
        authenticated=authenticated,
        plus_enabled=plus_enabled,
    )

    resolved_route = (
        route
        if allowed
        else ACCOUNT_ROUTE
    )

    return AccountInteractionResult(
        interaction=normalized_interaction,
        requested_route=route,
        resolved_route=resolved_route,
        allowed=allowed,
        reason=reason,
        mode=route_to_account_mode(
            resolved_route
        ),
        metadata={
            "ui_only": True,
            "fallback_route": ACCOUNT_ROUTE,
        },
    )


# ---------------------------------------------------------------------------
# ACCOUNT PAGE CONTROLLER
# ---------------------------------------------------------------------------

class AccountPageController:
    """
    Presentation controller for Account workspace.

    The controller may change UI state and navigation state only.
    It cannot change account-domain truth.
    """

    def __init__(
        self,
        state: Optional[AccountPageState] = None,
    ) -> None:
        self._state = normalize_account_page_state(
            state
        )

        self._interaction_history: List[
            AccountInteractionResult
        ] = []

    @property
    def state(self) -> AccountPageState:
        return normalize_account_page_state(
            self._state
        )

    @property
    def current_route(self) -> str:
        return self._state.current_route

    @property
    def current_mode(
        self,
    ) -> AccountPresentationMode:
        return self._state.mode

    @property
    def status(self) -> AccountPageStatus:
        return self._state.status

    def initialize(
        self,
        *,
        source: Optional[
            AccountSourceState
        ] = None,
    ) -> AccountPageComposition:
        normalized_source = (
            normalize_account_source_state(
                source
            )
        )

        self._state.user_id = (
            normalized_source.identity.user_id
        )

        self._state.authenticated = (
            normalized_source.authenticated
        )

        self._state.plus_enabled = (
            normalized_source.plus_enabled
        )

        self._state.status = (
            evaluate_account_presentation_status(
                normalized_source
            )
        )

        self._state.locked = (
            self._state.status
            == AccountPageStatus.LOCKED
        )

        self._state.initialized = True
        self._state.ready = (
            self._state.status
            == AccountPageStatus.READY
        )

        return compose_account_page(
            AccountPageRequest(
                user_id=self._state.user_id,
                mode=self._state.mode,
                authenticated=(
                    self._state.authenticated
                ),
                plus_enabled=(
                    self._state.plus_enabled
                ),
                page_status=self._state.status,
                source="account_controller",
            ),
            source=normalized_source,
        )

    def interact(
        self,
        interaction: Any,
    ) -> AccountInteractionResult:
        result = resolve_account_interaction(
            interaction,
            authenticated=self._state.authenticated,
            plus_enabled=self._state.plus_enabled,
        )

        self._state.interaction_count += 1
        self._state.last_interaction = (
            result.interaction
        )

        if result.interaction == (
            AccountInteraction.REFRESH
        ):
            self._state.refresh_count += 1

        if result.interaction == (
            AccountInteraction.LOCK
        ):
            self._state.locked = True
            self._state.status = (
                AccountPageStatus.LOCKED
            )
            self._state.ready = False

        elif result.allowed:
            self._state.current_route = (
                result.resolved_route
            )

            self._state.mode = result.mode

            self._state.last_error = None

        else:
            self._state.last_error = (
                result.reason
            )

        self._interaction_history.append(
            result
        )

        # Keep history bounded for UI memory safety.
        if len(self._interaction_history) > 200:
            self._interaction_history = (
                self._interaction_history[-200:]
            )

        return result

    def navigate(
        self,
        route: str,
    ) -> AccountInteractionResult:
        route = _account_text(
            route,
            ACCOUNT_ROUTE,
        )

        mapping = {
            ACCOUNT_ROUTE:
                AccountInteraction.OPEN_OVERVIEW,
            "/account/profile":
                AccountInteraction.OPEN_PROFILE,
            "/account/security":
                AccountInteraction.OPEN_SECURITY,
            "/account/billing":
                AccountInteraction.OPEN_BILLING,
            "/account/notifications":
                AccountInteraction.OPEN_NOTIFICATIONS,
            "/account/settings":
                AccountInteraction.OPEN_SETTINGS,
        }

        interaction = mapping.get(
            route,
            AccountInteraction.NONE,
        )

        return self.interact(
            interaction
        )

    def unlock(
        self,
    ) -> None:
        """
        UI unlock only.

        Does not authenticate the user and does not alter
        domain security state.
        """

        if not self._state.authenticated:
            self._state.status = (
                AccountPageStatus.LOCKED
            )
            self._state.locked = True
            self._state.ready = False
            return

        self._state.locked = False
        self._state.status = (
            AccountPageStatus.READY
        )
        self._state.ready = True

    def set_authenticated(
        self,
        authenticated: bool,
    ) -> None:
        """
        Presentation authentication state only.

        Actual authentication remains external.
        """

        authenticated = _account_bool(
            authenticated
        )

        self._state.authenticated = authenticated

        if not authenticated:
            self._state.plus_enabled = False
            self._state.locked = True
            self._state.ready = False
            self._state.status = (
                AccountPageStatus.LOCKED
            )
            self._state.current_route = ACCOUNT_ROUTE
            self._state.mode = (
                AccountPresentationMode.OVERVIEW
            )
        elif not self._state.locked:
            self._state.status = (
                AccountPageStatus.READY
            )
            self._state.ready = True

    def set_plus_visibility(
        self,
        enabled: bool,
    ) -> None:
        """
        Presentation visibility only.

        Does not grant entitlement.
        """

        self._state.plus_enabled = (
            _account_bool(enabled)
            if self._state.authenticated
            else False
        )

    def interaction_history(
        self,
    ) -> Tuple[
        AccountInteractionResult, ...
    ]:
        return tuple(
            self._interaction_history
        )

    def clear_interaction_history(
        self,
    ) -> None:
        self._interaction_history.clear()


# ---------------------------------------------------------------------------
# ACCOUNT SNAPSHOT
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AccountPageSnapshot:
    """
    Read-only presentation snapshot.
    """

    state: AccountPageState
    composition: Optional[
        AccountPageComposition
    ] = None

    captured_at: datetime = field(
        default_factory=_account_now
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def build_account_page_snapshot(
    controller: AccountPageController,
    *,
    composition: Optional[
        AccountPageComposition
    ] = None,
) -> AccountPageSnapshot:
    return AccountPageSnapshot(
        state=controller.state,
        composition=composition,
        captured_at=_account_now(),
        metadata={
            "engine": ACCOUNT_PAGE_ENGINE,
            "version": ACCOUNT_PAGE_VERSION,
            "ui_only": True,
            "read_only": True,
            "d13_mutation": False,
            "risk_override": False,
            "cas_bypass": False,
            "execution": False,
        },
    )
# ---------------------------------------------------------------------------
# SERIALIZATION HELPERS
# ---------------------------------------------------------------------------

def _serialize_account_value(
    value: Any,
) -> Any:
    """
    Convert Account UI contracts into safe primitive structures.
    """

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, tuple):
        return [
            _serialize_account_value(item)
            for item in value
        ]

    if isinstance(value, list):
        return [
            _serialize_account_value(item)
            for item in value
        ]

    if isinstance(value, dict):
        return {
            str(key): _serialize_account_value(item)
            for key, item in value.items()
        }

    if hasattr(value, "__dataclass_fields__"):
        return {
            name: _serialize_account_value(
                getattr(value, name)
            )
            for name in value.__dataclass_fields__
        }

    return value


def serialize_account_identity(
    identity: AccountIdentityView,
) -> Dict[str, Any]:
    return _serialize_account_value(identity)


def serialize_account_status(
    status: AccountStatusView,
) -> Dict[str, Any]:
    return _serialize_account_value(status)


def serialize_account_plan(
    plan: AccountPlanView,
) -> Dict[str, Any]:
    return _serialize_account_value(plan)


def serialize_account_badge(
    badge: AccountBadge,
) -> Dict[str, Any]:
    return _serialize_account_value(badge)


def serialize_account_action(
    action: AccountAction,
) -> Dict[str, Any]:
    return _serialize_account_value(action)


def serialize_account_section(
    section: AccountSectionState,
) -> Dict[str, Any]:
    return _serialize_account_value(section)


def serialize_account_summary(
    summary: AccountSummaryView,
) -> Dict[str, Any]:
    return _serialize_account_value(summary)


def serialize_account_page_view(
    page: AccountPageView,
) -> Dict[str, Any]:
    return _serialize_account_value(page)


def serialize_account_composition(
    composition: AccountPageComposition,
) -> Dict[str, Any]:
    return _serialize_account_value(composition)


def serialize_account_state(
    state: AccountPageState,
) -> Dict[str, Any]:
    return _serialize_account_value(state)


def serialize_account_snapshot(
    snapshot: AccountPageSnapshot,
) -> Dict[str, Any]:
    return _serialize_account_value(snapshot)


def serialize_account_interaction_result(
    result: AccountInteractionResult,
) -> Dict[str, Any]:
    return _serialize_account_value(result)


# ---------------------------------------------------------------------------
# CONTRACT VALIDATION
# ---------------------------------------------------------------------------

def validate_account_identity(
    identity: AccountIdentityView,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(
        identity,
        AccountIdentityView,
    ):
        return ["INVALID_ACCOUNT_IDENTITY"]

    if identity.user_id and not isinstance(
        identity.user_id,
        str,
    ):
        errors.append(
            "INVALID_USER_ID_TYPE"
        )

    if identity.email and not isinstance(
        identity.email,
        str,
    ):
        errors.append(
            "INVALID_EMAIL_TYPE"
        )

    if identity.avatar_url is not None:
        if not isinstance(
            identity.avatar_url,
            str,
        ):
            errors.append(
                "INVALID_AVATAR_URL_TYPE"
            )

    return errors


def validate_account_status(
    status: AccountStatusView,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(
        status,
        AccountStatusView,
    ):
        return ["INVALID_ACCOUNT_STATUS"]

    if not isinstance(
        status.state,
        AccountState,
    ):
        errors.append(
            "INVALID_ACCOUNT_STATE"
        )

    if status.active and status.restricted:
        errors.append(
            "ACTIVE_AND_RESTRICTED_CONFLICT"
        )

    return errors


def validate_account_plan(
    plan: AccountPlanView,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(
        plan,
        AccountPlanView,
    ):
        return ["INVALID_ACCOUNT_PLAN"]

    if (
        plan.plus_visible
        and not plan.entitlement_known
    ):
        errors.append(
            "PLUS_VISIBLE_WITH_UNKNOWN_ENTITLEMENT"
        )

    return errors


# ---------------------------------------------------------------------------
# PAGE VIEW VALIDATION
# ---------------------------------------------------------------------------

def validate_account_page_view(
    page: AccountPageView,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(
        page,
        AccountPageView,
    ):
        return ["INVALID_ACCOUNT_PAGE_VIEW"]

    if page.page_name != ACCOUNT_PAGE_NAME:
        errors.append(
            "INVALID_PAGE_NAME"
        )

    if page.route != ACCOUNT_ROUTE:
        errors.append(
            "INVALID_ACCOUNT_ROUTE"
        )

    if not isinstance(
        page.status,
        AccountPageStatus,
    ):
        errors.append(
            "INVALID_PAGE_STATUS"
        )

    if not isinstance(
        page.mode,
        AccountPresentationMode,
    ):
        errors.append(
            "INVALID_PRESENTATION_MODE"
        )

    errors.extend(
        validate_account_identity(
            page.identity
        )
    )

    errors.extend(
        validate_account_status(
            page.account_status
        )
    )

    errors.extend(
        validate_account_plan(
            page.plan
        )
    )

    if page.plus_enabled and not page.authenticated:
        errors.append(
            "PLUS_ENABLED_WITHOUT_AUTHENTICATION"
        )

    # Account UI must remain presentation-only.
    forbidden_authority_fields = {
        "intelligence_authority": False,
        "decision_authority": False,
        "d13_modification": False,
        "risk_authority": False,
        "cas_authority": False,
        "execution": False,
    }

    for key, expected in (
        forbidden_authority_fields.items()
    ):
        if page.metadata.get(key) != expected:
            errors.append(
                f"AUTHORITY_VIOLATION:{key}"
            )

    return errors


# ---------------------------------------------------------------------------
# COMPOSITION VALIDATION
# ---------------------------------------------------------------------------

def validate_account_composition(
    composition: AccountPageComposition,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(
        composition,
        AccountPageComposition,
    ):
        return [
            "INVALID_ACCOUNT_COMPOSITION"
        ]

    errors.extend(
        validate_account_page_view(
            composition.page
        )
    )

    if not isinstance(
        composition.summary,
        AccountSummaryView,
    ):
        errors.append(
            "INVALID_ACCOUNT_SUMMARY"
        )

    seen_sections = set()

    for section in composition.sections:
        if not section.section_id:
            errors.append(
                "SECTION_ID_MISSING"
            )

        if section.section_id in seen_sections:
            errors.append(
                f"DUPLICATE_SECTION:{section.section_id}"
            )

        seen_sections.add(
            section.section_id
        )

    if composition.metadata.get(
        "ui_only"
    ) is not True:
        errors.append(
            "COMPOSITION_NOT_UI_ONLY"
        )

    if composition.metadata.get(
        "decision_authority"
    ) is not False:
        errors.append(
            "DECISION_AUTHORITY_VIOLATION"
        )

    if composition.metadata.get(
        "d13_authority"
    ) is not False:
        errors.append(
            "D13_AUTHORITY_VIOLATION"
        )

    if composition.metadata.get(
        "risk_authority"
    ) is not False:
        errors.append(
            "RISK_AUTHORITY_VIOLATION"
        )

    if composition.metadata.get(
        "cas_authority"
    ) is not False:
        errors.append(
            "CAS_AUTHORITY_VIOLATION"
        )

    if composition.metadata.get(
        "execution_authority"
    ) is not False:
        errors.append(
            "EXECUTION_AUTHORITY_VIOLATION"
        )

    return errors


# ---------------------------------------------------------------------------
# STATE VALIDATION
# ---------------------------------------------------------------------------

def validate_account_page_state(
    state: AccountPageState,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(
        state,
        AccountPageState,
    ):
        return [
            "INVALID_ACCOUNT_PAGE_STATE"
        ]

    if (
        state.plus_enabled
        and not state.authenticated
    ):
        errors.append(
            "PLUS_WITHOUT_AUTHENTICATION"
        )

    if (
        state.locked
        and state.ready
    ):
        errors.append(
            "LOCKED_AND_READY_CONFLICT"
        )

    if (
        not state.authenticated
        and not state.locked
    ):
        errors.append(
            "UNAUTHENTICATED_STATE_NOT_LOCKED"
        )

    if state.interaction_count < 0:
        errors.append(
            "NEGATIVE_INTERACTION_COUNT"
        )

    if state.refresh_count < 0:
        errors.append(
            "NEGATIVE_REFRESH_COUNT"
        )

    if not state.current_route.startswith("/"):
        errors.append(
            "INVALID_CURRENT_ROUTE"
        )

    return errors


# ---------------------------------------------------------------------------
# AUTHORITY VALIDATION
# ---------------------------------------------------------------------------

def validate_account_authority() -> List[str]:
    """
    Hard architectural boundary check.

    The Account Page must never become a domain authority.
    """

    errors: List[str] = []

    required_true = {
        "account_presentation",
        "profile_presentation",
        "account_status_presentation",
        "account_navigation",
        "account_summary",
        "display_configuration",
    }

    required_false = {
        "authentication_authority",
        "credential_authority",
        "security_authority",
        "billing_authority",
        "subscription_authority",
        "entitlement_authority",
        "market_data_authority",
        "evidence_authority",
        "market_context_authority",
        "intelligence_authority",
        "decision_authority",
        "d13_authority",
        "risk_authority",
        "cas_authority",
        "execution_authority",
        "order_authority",
        "position_authority",
        "upstream_mutation",
    }

    for key in required_true:
        if ACCOUNT_UI_AUTHORITY.get(key) is not True:
            errors.append(
                f"REQUIRED_UI_AUTHORITY_MISSING:{key}"
            )

    for key in required_false:
        if ACCOUNT_UI_AUTHORITY.get(key) is not False:
            errors.append(
                f"FORBIDDEN_AUTHORITY_ENABLED:{key}"
            )

    return errors


# ---------------------------------------------------------------------------
# INTERACTION VALIDATION
# ---------------------------------------------------------------------------

def validate_account_interaction_result(
    result: AccountInteractionResult,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(
        result,
        AccountInteractionResult,
    ):
        return [
            "INVALID_INTERACTION_RESULT"
        ]

    if not isinstance(
        result.interaction,
        AccountInteraction,
    ):
        errors.append(
            "INVALID_INTERACTION"
        )

    if not result.resolved_route.startswith("/"):
        errors.append(
            "INVALID_RESOLVED_ROUTE"
        )

    if (
        result.allowed
        and result.reason
        not in {
            "ALLOWED",
            "UI_LOCK_REQUESTED",
        }
    ):
        errors.append(
            "ALLOWED_RESULT_HAS_INVALID_REASON"
        )

    if (
        result.interaction
        == AccountInteraction.LOCK
        and not result.metadata.get(
            "ui_lock_only"
        )
    ):
        errors.append(
            "LOCK_INTERACTION_MUST_BE_UI_ONLY"
        )

    return errors


# ---------------------------------------------------------------------------
# SNAPSHOT VALIDATION
# ---------------------------------------------------------------------------

def validate_account_snapshot(
    snapshot: AccountPageSnapshot,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(
        snapshot,
        AccountPageSnapshot,
    ):
        return [
            "INVALID_ACCOUNT_SNAPSHOT"
        ]

    errors.extend(
        validate_account_page_state(
            snapshot.state
        )
    )

    if snapshot.composition is not None:
        errors.extend(
            validate_account_composition(
                snapshot.composition
            )
        )

    if snapshot.metadata.get(
        "ui_only"
    ) is not True:
        errors.append(
            "SNAPSHOT_NOT_UI_ONLY"
        )

    if snapshot.metadata.get(
        "read_only"
    ) is not True:
        errors.append(
            "SNAPSHOT_NOT_READ_ONLY"
        )

    if snapshot.metadata.get(
        "d13_mutation"
    ) is not False:
        errors.append(
            "D13_MUTATION_ENABLED"
        )

    if snapshot.metadata.get(
        "risk_override"
    ) is not False:
        errors.append(
            "RISK_OVERRIDE_ENABLED"
        )

    if snapshot.metadata.get(
        "cas_bypass"
    ) is not False:
        errors.append(
            "CAS_BYPASS_ENABLED"
        )

    if snapshot.metadata.get(
        "execution"
    ) is not False:
        errors.append(
            "EXECUTION_ENABLED"
        )

    return errors


# ---------------------------------------------------------------------------
# ACCOUNT OPERATIONAL HEALTH
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AccountPageHealth:
    """
    Presentation-layer health report.

    Operational health here means the Account UI module is internally
    coherent and respecting its architecture. It does NOT mean that
    authentication, billing, security or account services are healthy.
    """

    engine: str
    version: str

    operational: bool
    initialized: bool
    ready: bool

    status: AccountPageStatus

    validation_errors: Tuple[str, ...] = ()

    authority_valid: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def build_account_page_health(
    controller: AccountPageController,
    *,
    composition: Optional[
        AccountPageComposition
    ] = None,
) -> AccountPageHealth:
    state = controller.state

    errors = validate_account_page_state(
        state
    )

    authority_errors = (
        validate_account_authority()
    )

    errors.extend(authority_errors)

    if composition is not None:
        errors.extend(
            validate_account_composition(
                composition
            )
        )

    errors = list(
        dict.fromkeys(errors)
    )

    authority_valid = not bool(
        authority_errors
    )

    operational = (
        state.initialized
        and bool(errors) is False
        and authority_valid
    )

    return AccountPageHealth(
        engine=ACCOUNT_PAGE_ENGINE,
        version=ACCOUNT_PAGE_VERSION,
        operational=operational,
        initialized=state.initialized,
        ready=state.ready,
        status=state.status,
        validation_errors=tuple(errors),
        authority_valid=authority_valid,
        metadata={
            "ui_only": True,
            "domain_authority_external": True,
            "intelligence_authority": False,
            "decision_authority": False,
            "d13_authority": False,
            "risk_authority": False,
            "cas_authority": False,
            "execution_authority": False,
        },
    )


def serialize_account_page_health(
    health: AccountPageHealth,
) -> Dict[str, Any]:
    return _serialize_account_value(
        health
    )


# ---------------------------------------------------------------------------
# MODULE OPERATIONAL CHECK
# ---------------------------------------------------------------------------

def account_page_operational_check(
    *,
    controller: Optional[
        AccountPageController
    ] = None,
    composition: Optional[
        AccountPageComposition
    ] = None,
) -> Dict[str, Any]:
    if controller is None:
        controller = AccountPageController(
            create_account_page_state()
        )

    health = build_account_page_health(
        controller,
        composition=composition,
    )

    return {
        "engine": ACCOUNT_PAGE_ENGINE,
        "version": ACCOUNT_PAGE_VERSION,
        "operational": health.operational,
        "initialized": health.initialized,
        "ready": health.ready,
        "status": health.status.value,
        "validation_errors": list(
            health.validation_errors
        ),
        "authority_valid": health.authority_valid,
        "authority": dict(
            ACCOUNT_UI_AUTHORITY
        ),
        "ui_only": True,
    }


# ---------------------------------------------------------------------------
# ACCOUNT PAGE SUMMARY
# ---------------------------------------------------------------------------

def account_page_summary() -> Dict[str, Any]:
    return {
        "engine": ACCOUNT_PAGE_ENGINE,
        "version": ACCOUNT_PAGE_VERSION,
        "name": ACCOUNT_PAGE_NAME,
        "route": ACCOUNT_ROUTE,

        "responsibilities": [
            "account presentation",
            "profile presentation",
            "account status presentation",
            "account summary",
            "account workspace navigation",
            "presentation state management",
        ],

        "not_responsible_for": [
            "authentication",
            "credentials",
            "security enforcement",
            "billing authority",
            "subscription authority",
            "entitlement authority",
            "market intelligence",
            "evidence",
            "decision authority",
            "D13",
            "risk",
            "CAS",
            "execution",
            "orders",
            "positions",
        ],

        "architecture": (
            "UPSTREAM ACCOUNT TRUTH → "
            "NORMALIZE → "
            "PRESENTATION READINESS → "
            "SUMMARY/SECTIONS → "
            "ACCOUNT PAGE VIEW"
        ),

        "ui_only": True,
    }


# ---------------------------------------------------------------------------
# DEFAULT ACCOUNT PAGE FACTORY
# ---------------------------------------------------------------------------

def create_default_account_page(
    *,
    user_id: str = "",
    authenticated: bool = False,
    plus_enabled: bool = False,
) -> AccountPageController:
    state = create_account_page_state(
        user_id=user_id,
        authenticated=authenticated,
        plus_enabled=plus_enabled,
    )

    return AccountPageController(
        state
    )


# ---------------------------------------------------------------------------
# MODULE CONTRACT CHECK
# ---------------------------------------------------------------------------

def account_page_module_check() -> Dict[str, Any]:
    authority_errors = (
        validate_account_authority()
    )

    sample_identity = AccountIdentityView()

    sample_status = AccountStatusView()

    sample_plan = AccountPlanView()

    sample_source = AccountSourceState(
        identity=sample_identity,
        account_status=sample_status,
        plan=sample_plan,
        authenticated=False,
        plus_enabled=False,
        source_available=True,
    )

    sample_request = AccountPageRequest(
        authenticated=False,
        plus_enabled=False,
        page_status=AccountPageStatus.LOCKED,
    )

    sample_page = build_account_page_view(
        sample_request,
        identity=sample_identity,
        account_status=sample_status,
        plan=sample_plan,
    )

    page_errors = validate_account_page_view(
        sample_page
    )

    return {
        "engine": ACCOUNT_PAGE_ENGINE,
        "version": ACCOUNT_PAGE_VERSION,
        "module": ACCOUNT_PAGE_NAME,

        "authority_valid": not bool(
            authority_errors
        ),

        "contract_valid": not bool(
            page_errors
        ),

        "authority_errors": authority_errors,
        "contract_errors": page_errors,

        "ui_only": True,

        "forbidden_authority": {
            key: value
            for key, value in ACCOUNT_UI_AUTHORITY.items()
            if not value
        },
    }


# ---------------------------------------------------------------------------
# PUBLIC EXPORTS
# ---------------------------------------------------------------------------

__all__ = [
    # Identity
    "ACCOUNT_PAGE_ENGINE",
    "ACCOUNT_PAGE_VERSION",
    "ACCOUNT_PAGE_NAME",
    "ACCOUNT_PAGE_TITLE",
    "ACCOUNT_PAGE_DESCRIPTION",
    "ACCOUNT_ROUTE",
    "ACCOUNT_UI_AUTHORITY",

    # Enums
    "AccountPageStatus",
    "AccountPresentationMode",
    "AccountState",
    "AccountPriority",
    "AccountBadgeType",
    "AccountInteraction",

    # Contracts
    "AccountIdentityView",
    "AccountStatusView",
    "AccountPlanView",
    "AccountBadge",
    "AccountAction",
    "AccountPageRequest",
    "AccountPageView",
    "AccountSourceState",
    "AccountSectionState",
    "AccountSummaryView",
    "AccountPageComposition",
    "AccountInteractionResult",
    "AccountPageState",
    "AccountPageSnapshot",
    "AccountPageHealth",

    # Registries
    "DEFAULT_ACCOUNT_ACTIONS",
    "DEFAULT_ACCOUNT_SECTIONS",
    "ACCOUNT_INTERACTION_ROUTES",

    # Normalization
    "normalize_account_identity",
    "normalize_account_status",
    "normalize_account_plan",
    "normalize_account_source_state",
    "normalize_account_page_state",
    "normalize_account_interaction",

    # Builders
    "build_account_status_badge",
    "build_account_plan_badge",
    "build_profile_badge",
    "build_account_badges",
    "get_account_actions",
    "build_account_page_view",
    "build_account_sections",
    "resolve_account_display_name",
    "build_account_status_message",
    "build_account_summary",
    "compose_account_page",

    # Routing / interaction
    "route_to_account_mode",
    "evaluate_account_route_access",
    "resolve_account_interaction",

    # Controller
    "create_account_page_state",
    "AccountPageController",

    # Snapshot
    "build_account_page_snapshot",

    # Serialization
    "_serialize_account_value",
    "serialize_account_identity",
    "serialize_account_status",
    "serialize_account_plan",
    "serialize_account_badge",
    "serialize_account_action",
    "serialize_account_section",
    "serialize_account_summary",
    "serialize_account_page_view",
    "serialize_account_composition",
    "serialize_account_state",
    "serialize_account_snapshot",
    "serialize_account_interaction_result",

    # Validation
    "validate_account_identity",
    "validate_account_status",
    "validate_account_plan",
    "validate_account_page_view",
    "validate_account_composition",
    "validate_account_page_state",
    "validate_account_authority",
    "validate_account_interaction_result",
    "validate_account_snapshot",

    # Health / diagnostics
    "build_account_page_health",
    "serialize_account_page_health",
    "account_page_operational_check",
    "account_page_summary",
    "create_default_account_page",
    "account_page_module_check",
]
# ---------------------------------------------------------------------------
# SAFE PRESENTATION REFRESH
# ---------------------------------------------------------------------------

def refresh_account_page(
    controller: AccountPageController,
    *,
    source: Optional[AccountSourceState] = None,
) -> AccountPageComposition:
    """
    Refresh Account presentation from current upstream source truth.

    This function does NOT refresh the domain itself.
    It only rebuilds the UI composition from supplied source data.
    """

    if not isinstance(
        controller,
        AccountPageController,
    ):
        raise TypeError(
            "controller must be AccountPageController"
        )

    normalized_source = (
        normalize_account_source_state(
            source
        )
    )

    controller._state.user_id = (
        normalized_source.identity.user_id
    )

    controller._state.authenticated = (
        normalized_source.authenticated
    )

    controller._state.plus_enabled = (
        normalized_source.plus_enabled
    )

    controller._state.status = (
        evaluate_account_presentation_status(
            normalized_source
        )
    )

    controller._state.locked = (
        controller._state.status
        == AccountPageStatus.LOCKED
    )

    controller._state.ready = (
        controller._state.status
        == AccountPageStatus.READY
    )

    controller._state.refresh_count += 1
    controller._state.last_interaction = (
        AccountInteraction.REFRESH
    )
    controller._state.last_error = None

    return compose_account_page(
        AccountPageRequest(
            user_id=controller._state.user_id,
            mode=controller._state.mode,
            authenticated=(
                controller._state.authenticated
            ),
            plus_enabled=(
                controller._state.plus_enabled
            ),
            page_status=controller._state.status,
            source="account_refresh",
        ),
        source=normalized_source,
    )


# ---------------------------------------------------------------------------
# SAFE PAGE ACCESSOR
# ---------------------------------------------------------------------------

def get_account_page(
    controller: AccountPageController,
    *,
    source: Optional[AccountSourceState] = None,
) -> AccountPageComposition:
    """
    Return current display composition.

    If a source is supplied, the composition is rebuilt from that source.
    Otherwise a safe presentation snapshot is generated from controller state.
    """

    if not isinstance(
        controller,
        AccountPageController,
    ):
        raise TypeError(
            "controller must be AccountPageController"
        )

    if source is not None:
        return compose_account_page(
            AccountPageRequest(
                user_id=controller.state.user_id,
                mode=controller.state.mode,
                authenticated=(
                    controller.state.authenticated
                ),
                plus_enabled=(
                    controller.state.plus_enabled
                ),
                page_status=controller.state.status,
                source="account_accessor",
            ),
            source=source,
        )

    empty_source = AccountSourceState(
        identity=AccountIdentityView(
            user_id=controller.state.user_id
        ),
        authenticated=(
            controller.state.authenticated
        ),
        plus_enabled=(
            controller.state.plus_enabled
        ),
        source_available=False,
        source_errors=(
            "No upstream account source supplied",
        ),
    )

    return compose_account_page(
        AccountPageRequest(
            user_id=controller.state.user_id,
            mode=controller.state.mode,
            authenticated=(
                controller.state.authenticated
            ),
            plus_enabled=(
                controller.state.plus_enabled
            ),
            page_status=controller.state.status,
            source="account_accessor",
        ),
        source=empty_source,
    )


# ---------------------------------------------------------------------------
# PRESENTATION SAFE NAVIGATION
# ---------------------------------------------------------------------------

def can_navigate_account_page(
    controller: AccountPageController,
    route: str,
) -> bool:
    if not isinstance(
        controller,
        AccountPageController,
    ):
        return False

    allowed, _ = evaluate_account_route_access(
        route,
        authenticated=(
            controller.state.authenticated
        ),
        plus_enabled=(
            controller.state.plus_enabled
        ),
    )

    return allowed


def select_account_route(
    controller: AccountPageController,
    route: str,
) -> AccountInteractionResult:
    """
    Presentation-only route selection.
    """

    if not isinstance(
        controller,
        AccountPageController,
    ):
        raise TypeError(
            "controller must be AccountPageController"
        )

    return controller.navigate(route)


# ---------------------------------------------------------------------------
# SAFE UI LOCK
# ---------------------------------------------------------------------------

def lock_account_page(
    controller: AccountPageController,
) -> AccountPageSnapshot:
    """
    Locks only the Account UI presentation.

    It does NOT:
        - revoke authentication
        - change credentials
        - alter security policy
        - alter subscription
        - alter billing
        - alter trading state
        - alter D13
        - alter Risk
        - alter CAS
        - execute anything
    """

    if not isinstance(
        controller,
        AccountPageController,
    ):
        raise TypeError(
            "controller must be AccountPageController"
        )

    controller.interact(
        AccountInteraction.LOCK
    )

    return build_account_page_snapshot(
        controller
    )


# ---------------------------------------------------------------------------
# PRESENTATION DIAGNOSTICS
# ---------------------------------------------------------------------------

def diagnose_account_page(
    controller: AccountPageController,
    *,
    composition: Optional[
        AccountPageComposition
    ] = None,
) -> Dict[str, Any]:
    """
    Produce a complete diagnostic report for the Account UI module.
    """

    if not isinstance(
        controller,
        AccountPageController,
    ):
        return {
            "operational": False,
            "errors": [
                "INVALID_ACCOUNT_CONTROLLER"
            ],
        }

    state = controller.state

    state_errors = (
        validate_account_page_state(
            state
        )
    )

    authority_errors = (
        validate_account_authority()
    )

    composition_errors: List[str] = []

    if composition is not None:
        composition_errors = (
            validate_account_composition(
                composition
            )
        )

    interaction_errors: List[str] = []

    for result in controller.interaction_history():
        interaction_errors.extend(
            validate_account_interaction_result(
                result
            )
        )

    all_errors = list(
        dict.fromkeys(
            state_errors
            + authority_errors
            + composition_errors
            + interaction_errors
        )
    )

    return {
        "engine": ACCOUNT_PAGE_ENGINE,
        "version": ACCOUNT_PAGE_VERSION,

        "operational": not bool(
            all_errors
        ),

        "initialized": state.initialized,
        "ready": state.ready,
        "locked": state.locked,

        "status": state.status.value,
        "mode": state.mode.value,
        "current_route": state.current_route,

        "authenticated": state.authenticated,
        "plus_enabled": state.plus_enabled,

        "interaction_count": (
            state.interaction_count
        ),
        "refresh_count": (
            state.refresh_count
        ),

        "errors": all_errors,

        "authority_valid": not bool(
            authority_errors
        ),

        "ui_only": True,

        "domain_authority_external": True,

        "forbidden_authorities": {
            key: value
            for key, value
            in ACCOUNT_UI_AUTHORITY.items()
            if value is False
        },
    }


# ---------------------------------------------------------------------------
# CONTRACT MANIFEST
# ---------------------------------------------------------------------------

def account_page_contract_manifest() -> Dict[str, Any]:
    """
    Machine-readable architectural contract.

    This manifest documents what Account Page may and may not do.
    """

    return {
        "module": ACCOUNT_PAGE_NAME,
        "engine": ACCOUNT_PAGE_ENGINE,
        "version": ACCOUNT_PAGE_VERSION,
        "route": ACCOUNT_ROUTE,

        "layer": "UI_PRESENTATION",

        "input_flow": [
            "USER_SERVICE_OUTPUT",
            "PROFILE_SERVICE_OUTPUT",
            "SUBSCRIPTION_PRESENTATION_OUTPUT",
            "APPLICATION_SESSION_STATE",
        ],

        "processing_flow": [
            "NORMALIZATION",
            "PRESENTATION_READINESS",
            "SUMMARY_COMPOSITION",
            "SECTION_COMPOSITION",
            "VIEW_COMPOSITION",
            "SNAPSHOT",
            "VALIDATION",
        ],

        "output_flow": [
            "ACCOUNT_PAGE_VIEW",
            "ACCOUNT_PAGE_COMPOSITION",
            "ACCOUNT_PAGE_SNAPSHOT",
        ],

        "authority_owner": {
            "authentication": "EXTERNAL_AUTH_SERVICE",
            "profile": "USER_PROFILE_SERVICE",
            "billing": "BILLING_SERVICE",
            "subscription": "SUBSCRIPTION_SERVICE",
            "entitlement": "ENTITLEMENT_SERVICE",
            "security": "SECURITY_SERVICE",
            "intelligence": "INTELLIGENCE_LAYER",
            "decision": "D13_DECISION_AUTHORITY",
            "risk": "RISK_LAYER",
            "cas": "CAS_LAYER",
            "execution": "EXECUTION_LAYER",
        },

        "ui_authority": dict(
            ACCOUNT_UI_AUTHORITY
        ),

        "principles": [
            "PRESENTATION_ONLY",
            "UPSTREAM_TRUTH_PRESERVED",
            "NO_FAKE_INTELLIGENCE",
            "NO_DECISION_GENERATION",
            "NO_D13_MUTATION",
            "NO_RISK_OVERRIDE",
            "NO_CAS_BYPASS",
            "NO_EXECUTION",
            "NO_DOMAIN_STATE_MUTATION",
        ],
    }


# ---------------------------------------------------------------------------
# FINAL INTEGRITY CHECK
# ---------------------------------------------------------------------------

def validate_account_page_module() -> Dict[str, Any]:
    """
    Final module-level structural integrity check.

    This validates contracts without requiring live services.
    """

    module_check = (
        account_page_module_check()
    )

    default_controller = (
        create_default_account_page()
    )

    default_snapshot = (
        build_account_page_snapshot(
            default_controller
        )
    )

    snapshot_errors = (
        validate_account_snapshot(
            default_snapshot
        )
    )

    contract = (
        account_page_contract_manifest()
    )

    errors = list(
        dict.fromkeys(
            module_check.get(
                "authority_errors",
                [],
            )
            + module_check.get(
                "contract_errors",
                [],
            )
            + snapshot_errors
        )
    )

    return {
        "engine": ACCOUNT_PAGE_ENGINE,
        "version": ACCOUNT_PAGE_VERSION,
        "module": ACCOUNT_PAGE_NAME,

        "valid": not bool(errors),
        "errors": errors,

        "authority_valid": (
            not bool(
                module_check.get(
                    "authority_errors",
                    [],
                )
            )
        ),

        "contract_valid": (
            not bool(
                module_check.get(
                    "contract_errors",
                    [],
                )
            )
        ),

        "snapshot_valid": not bool(
            snapshot_errors
        ),

        "ui_only": True,

        "contract_manifest": contract,
    }


# ---------------------------------------------------------------------------
# DEFAULT PRESENTATION SNAPSHOT
# ---------------------------------------------------------------------------

def default_account_page_snapshot() -> AccountPageSnapshot:
    """
    Return a safe unauthenticated default snapshot.

    This represents UI state only and does not imply any account truth.
    """

    controller = create_default_account_page()

    return build_account_page_snapshot(
        controller
    )


# ---------------------------------------------------------------------------
# FINAL PUBLIC EXPORT EXTENSION
# ---------------------------------------------------------------------------

__all__.extend(
    [
        # Refresh / access
        "refresh_account_page",
        "get_account_page",

        # Navigation
        "can_navigate_account_page",
        "select_account_route",

        # UI lock
        "lock_account_page",

        # Diagnostics
        "diagnose_account_page",

        # Architecture
        "account_page_contract_manifest",
        "validate_account_page_module",

        # Default snapshot
        "default_account_page_snapshot",
    ]
)