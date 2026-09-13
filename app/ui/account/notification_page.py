# app/ui/account/notification_page.py

"""
ROBOMLM_PLUS — Notification Page
================================

Presentation-only notification workspace.

Responsibilities
----------------
- Notification presentation
- Notification grouping/filtering metadata
- Notification status display
- Notification navigation
- Notification summary
- Safe UI state normalization

Authority Boundary
------------------
This module MUST NOT:
- send notifications
- deliver notifications
- persist notification state as domain truth
- mutate notification records
- generate market intelligence
- calculate evidence
- generate decisions
- modify D13
- generate or override risk
- generate or bypass CAS
- execute orders
- mutate positions
- modify upstream domain state

Actual notification authority belongs to the external
notification/application service layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


# ============================================================================
# MODULE IDENTITY
# ============================================================================

NOTIFICATION_PAGE_ENGINE = "ROBOMLM_PLUS_UI_NOTIFICATION"
NOTIFICATION_PAGE_VERSION = "1.0"
NOTIFICATION_PAGE_NAME = "Notifications"
NOTIFICATION_PAGE_TITLE = "Notifications"
NOTIFICATION_PAGE_DESCRIPTION = (
    "ROBOMLM notification center and notification presentation workspace."
)
NOTIFICATION_ROUTE = "/account/notifications"


# ============================================================================
# UI AUTHORITY CONTRACT
# ============================================================================

NOTIFICATION_UI_AUTHORITY: Dict[str, bool] = {
    # Presentation authority
    "notification_presentation": True,
    "notification_summary_presentation": True,
    "notification_status_presentation": True,
    "notification_navigation": True,
    "notification_filter_presentation": True,
    "notification_grouping_presentation": True,
    "display_configuration": True,

    # Domain authority — external
    "notification_delivery_authority": False,
    "notification_send_authority": False,
    "notification_persistence_authority": False,
    "notification_mutation_authority": False,
    "notification_read_state_authority": False,
    "notification_preference_authority": False,

    # Security / account authority — external
    "authentication_authority": False,
    "credential_authority": False,
    "security_authority": False,

    # Billing authority — external
    "billing_authority": False,
    "subscription_authority": False,
    "entitlement_authority": False,

    # Market authority — external
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

    # Upstream mutation
    "upstream_mutation": False,
}


# ============================================================================
# ENUMS
# ============================================================================

class NotificationPageStatus(str, Enum):
    """Presentation readiness state."""

    LOADING = "LOADING"
    READY = "READY"
    DEGRADED = "DEGRADED"
    LOCKED = "LOCKED"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class NotificationPresentationMode(str, Enum):
    """Notification center presentation modes."""

    ALL = "ALL"
    UNREAD = "UNREAD"
    IMPORTANT = "IMPORTANT"
    SYSTEM = "SYSTEM"
    MARKET = "MARKET"
    ACCOUNT = "ACCOUNT"
    AUTOMATION = "AUTOMATION"
    SECURITY = "SECURITY"
    UNKNOWN = "UNKNOWN"


class NotificationState(str, Enum):
    """Upstream notification state represented by the UI."""

    UNKNOWN = "UNKNOWN"
    UNREAD = "UNREAD"
    READ = "READ"
    ARCHIVED = "ARCHIVED"
    EXPIRED = "EXPIRED"


class NotificationCategory(str, Enum):
    """Presentation category supplied by upstream notification data."""

    UNKNOWN = "UNKNOWN"
    SYSTEM = "SYSTEM"
    MARKET = "MARKET"
    ACCOUNT = "ACCOUNT"
    SECURITY = "SECURITY"
    AUTOMATION = "AUTOMATION"
    BILLING = "BILLING"
    RESEARCH = "RESEARCH"
    GENERAL = "GENERAL"


class NotificationPriority(str, Enum):
    """Display priority only; not execution authority."""

    NORMAL = "NORMAL"
    IMPORTANT = "IMPORTANT"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class NotificationBadgeType(str, Enum):
    """Notification summary badge types."""

    STATUS = "STATUS"
    UNREAD = "UNREAD"
    IMPORTANT = "IMPORTANT"
    CATEGORY = "CATEGORY"
    SYSTEM = "SYSTEM"


# ============================================================================
# SAFE HELPERS
# ============================================================================

def _notification_text(value: Any, default: str = "") -> str:
    """Safely normalize presentation text."""

    if value is None:
        return default

    text = str(value).strip()
    return text if text else default


def _notification_bool(value: Any, default: bool = False) -> bool:
    """Safely normalize a boolean presentation value."""

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        value_lower = value.strip().lower()

        if value_lower in {"true", "1", "yes", "on"}:
            return True

        if value_lower in {"false", "0", "no", "off"}:
            return False

    if isinstance(value, (int, float)):
        return bool(value)

    return default


def _notification_enum(
    enum_type: type[Enum],
    value: Any,
    default: Enum,
) -> Enum:
    """Safely normalize an enum value."""

    if isinstance(value, enum_type):
        return value

    try:
        return enum_type(str(value).strip().upper())
    except (ValueError, TypeError):
        return default


def _notification_now() -> datetime:
    """Return timezone-aware UTC timestamp."""

    return datetime.now(timezone.utc)


# ============================================================================
# PRESENTATION CONTRACTS
# ============================================================================

@dataclass(frozen=True)
class NotificationIdentityView:
    """Presentation identity for the notification center."""

    user_id: str = ""
    display_name: str = ""
    email: str = ""
    authenticated: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class NotificationItemView:
    """
    Single notification presentation record.

    This object represents upstream notification truth.
    It does not own notification persistence or delivery.
    """

    notification_id: str = ""
    title: str = ""
    message: str = ""

    category: NotificationCategory = NotificationCategory.UNKNOWN
    state: NotificationState = NotificationState.UNKNOWN
    priority: NotificationPriority = NotificationPriority.NORMAL

    created_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    action_label: str = ""
    action_route: str = ""

    visible: bool = True
    actionable: bool = False

    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class NotificationSummaryView:
    """High-level notification summary for the page."""

    total_count: int = 0
    unread_count: int = 0
    important_count: int = 0
    critical_count: int = 0

    system_count: int = 0
    market_count: int = 0
    account_count: int = 0
    security_count: int = 0
    automation_count: int = 0

    has_unread: bool = False
    has_important: bool = False

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class NotificationBadge:
    """Display-only notification badge."""

    badge_type: NotificationBadgeType = NotificationBadgeType.STATUS
    label: str = ""
    value: str = ""
    priority: NotificationPriority = NotificationPriority.NORMAL
    visible: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class NotificationAction:
    """Presentation/navigation action."""

    action_id: str = ""
    label: str = ""
    route: str = ""

    enabled: bool = True
    visible: bool = True

    requires_authentication: bool = True
    priority: NotificationPriority = NotificationPriority.NORMAL

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class NotificationPageRequest:
    """Request contract for building the notification page."""

    user_id: str = ""

    mode: NotificationPresentationMode = (
        NotificationPresentationMode.ALL
    )

    authenticated: bool = False

    page_status: NotificationPageStatus = (
        NotificationPageStatus.UNKNOWN
    )

    source: str = ""

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class NotificationPageView:
    """Complete presentation view consumed by the UI."""

    page_name: str = NOTIFICATION_PAGE_NAME
    page_title: str = NOTIFICATION_PAGE_TITLE
    route: str = NOTIFICATION_ROUTE

    status: NotificationPageStatus = NotificationPageStatus.UNKNOWN
    mode: NotificationPresentationMode = (
        NotificationPresentationMode.ALL
    )

    identity: NotificationIdentityView = field(
        default_factory=NotificationIdentityView
    )

    notifications: Sequence[NotificationItemView] = field(
        default_factory=tuple
    )

    summary: NotificationSummaryView = field(
        default_factory=NotificationSummaryView
    )

    badges: Sequence[NotificationBadge] = field(
        default_factory=tuple
    )

    actions: Sequence[NotificationAction] = field(
        default_factory=tuple
    )

    authenticated: bool = False

    generated_at: datetime = field(default_factory=_notification_now)

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# DEFAULT ACTIONS
# ============================================================================

DEFAULT_NOTIFICATION_ACTIONS: tuple[NotificationAction, ...] = (
    NotificationAction(
        action_id="notification_all",
        label="All Notifications",
        route=NOTIFICATION_ROUTE,
        enabled=True,
        visible=True,
        requires_authentication=True,
        priority=NotificationPriority.NORMAL,
    ),
    NotificationAction(
        action_id="notification_unread",
        label="Unread",
        route=f"{NOTIFICATION_ROUTE}/unread",
        enabled=True,
        visible=True,
        requires_authentication=True,
        priority=NotificationPriority.IMPORTANT,
    ),
    NotificationAction(
        action_id="notification_important",
        label="Important",
        route=f"{NOTIFICATION_ROUTE}/important",
        enabled=True,
        visible=True,
        requires_authentication=True,
        priority=NotificationPriority.IMPORTANT,
    ),
    NotificationAction(
        action_id="notification_system",
        label="System",
        route=f"{NOTIFICATION_ROUTE}/system",
        enabled=True,
        visible=True,
        requires_authentication=True,
        priority=NotificationPriority.NORMAL,
    ),
    NotificationAction(
        action_id="notification_security",
        label="Security",
        route=f"{NOTIFICATION_ROUTE}/security",
        enabled=True,
        visible=True,
        requires_authentication=True,
        priority=NotificationPriority.HIGH,
    ),
)


# ============================================================================
# NORMALIZATION
# ============================================================================

def normalize_notification_identity(
    identity: Optional[NotificationIdentityView] = None,
    *,
    user_id: str = "",
    display_name: str = "",
    email: str = "",
    authenticated: bool = False,
) -> NotificationIdentityView:
    """Normalize upstream identity without creating account truth."""

    if identity is not None:
        return NotificationIdentityView(
            user_id=_notification_text(identity.user_id),
            display_name=_notification_text(identity.display_name),
            email=_notification_text(identity.email),
            authenticated=_notification_bool(identity.authenticated),
            metadata=dict(identity.metadata or {}),
        )

    return NotificationIdentityView(
        user_id=_notification_text(user_id),
        display_name=_notification_text(display_name),
        email=_notification_text(email),
        authenticated=_notification_bool(authenticated),
    )


def normalize_notification_item(
    item: NotificationItemView,
) -> NotificationItemView:
    """Normalize one upstream notification record."""

    return NotificationItemView(
        notification_id=_notification_text(item.notification_id),
        title=_notification_text(item.title),
        message=_notification_text(item.message),
        category=_notification_enum(
            NotificationCategory,
            item.category,
            NotificationCategory.UNKNOWN,
        ),
        state=_notification_enum(
            NotificationState,
            item.state,
            NotificationState.UNKNOWN,
        ),
        priority=_notification_enum(
            NotificationPriority,
            item.priority,
            NotificationPriority.NORMAL,
        ),
        created_at=item.created_at,
        read_at=item.read_at,
        expires_at=item.expires_at,
        action_label=_notification_text(item.action_label),
        action_route=_notification_text(item.action_route),
        visible=_notification_bool(item.visible, True),
        actionable=_notification_bool(item.actionable),
        source=_notification_text(item.source),
        metadata=dict(item.metadata or {}),
    )


def normalize_notification_items(
    items: Optional[Sequence[NotificationItemView]],
) -> tuple[NotificationItemView, ...]:
    """Normalize a notification collection."""

    if not items:
        return tuple()

    return tuple(
        normalize_notification_item(item)
        for item in items
        if isinstance(item, NotificationItemView)
    )


# ============================================================================
# BADGE BUILDERS
# ============================================================================

def build_notification_status_badge(
    status: NotificationPageStatus,
) -> NotificationBadge:
    """Build presentation status badge."""

    return NotificationBadge(
        badge_type=NotificationBadgeType.STATUS,
        label="Status",
        value=status.value,
        priority=(
            NotificationPriority.HIGH
            if status in {
                NotificationPageStatus.ERROR,
                NotificationPageStatus.LOCKED,
            }
            else NotificationPriority.NORMAL
        ),
        visible=True,
    )


def build_notification_unread_badge(
    unread_count: int,
) -> NotificationBadge:
    """Build unread count badge."""

    count = max(0, int(unread_count))

    return NotificationBadge(
        badge_type=NotificationBadgeType.UNREAD,
        label="Unread",
        value=str(count),
        priority=(
            NotificationPriority.IMPORTANT
            if count > 0
            else NotificationPriority.NORMAL
        ),
        visible=True,
    )


def build_notification_important_badge(
    important_count: int,
) -> NotificationBadge:
    """Build important notification badge."""

    count = max(0, int(important_count))

    return NotificationBadge(
        badge_type=NotificationBadgeType.IMPORTANT,
        label="Important",
        value=str(count),
        priority=(
            NotificationPriority.HIGH
            if count > 0
            else NotificationPriority.NORMAL
        ),
        visible=True,
    )


# ============================================================================
# ACTION / BADGE REGISTRY HELPERS
# ============================================================================

def get_notification_actions(
    authenticated: bool = False,
) -> tuple[NotificationAction, ...]:
    """Return presentation actions according to session state."""

    if not authenticated:
        return tuple(
            NotificationAction(
                action_id=action.action_id,
                label=action.label,
                route=action.route,
                enabled=False,
                visible=action.visible,
                requires_authentication=True,
                priority=action.priority,
                metadata=dict(action.metadata),
            )
            for action in DEFAULT_NOTIFICATION_ACTIONS
        )

    return tuple(DEFAULT_NOTIFICATION_ACTIONS)


def build_notification_badges(
    status: NotificationPageStatus,
    summary: NotificationSummaryView,
) -> tuple[NotificationBadge, ...]:
    """Build display-only notification badges."""

    return (
        build_notification_status_badge(status),
        build_notification_unread_badge(summary.unread_count),
        build_notification_important_badge(summary.important_count),
    )


# ============================================================================
# PAGE VIEW BUILDER
# ============================================================================

def build_notification_page_view(
    *,
    identity: Optional[NotificationIdentityView] = None,
    notifications: Optional[Sequence[NotificationItemView]] = None,
    summary: Optional[NotificationSummaryView] = None,
    status: NotificationPageStatus = NotificationPageStatus.UNKNOWN,
    mode: NotificationPresentationMode = NotificationPresentationMode.ALL,
    authenticated: bool = False,
    source: str = "",
    metadata: Optional[Dict[str, Any]] = None,
) -> NotificationPageView:
    """
    Build the notification presentation view.

    IMPORTANT:
    This function only assembles upstream notification information.
    It does not create, send, persist, mark-read, archive, or mutate
    notifications.
    """

    normalized_identity = normalize_notification_identity(
        identity,
        authenticated=authenticated,
    )

    normalized_items = normalize_notification_items(notifications)

    normalized_summary = (
        summary
        if summary is not None
        else NotificationSummaryView()
    )

    normalized_status = _notification_enum(
        NotificationPageStatus,
        status,
        NotificationPageStatus.UNKNOWN,
    )

    normalized_mode = _notification_enum(
        NotificationPresentationMode,
        mode,
        NotificationPresentationMode.ALL,
    )

    badges = build_notification_badges(
        normalized_status,
        normalized_summary,
    )

    actions = get_notification_actions(authenticated)

    view_metadata: Dict[str, Any] = {
        "ui_only": True,
        "presentation_only": True,
        "source": _notification_text(source),
        "notification_generation": False,
        "notification_delivery": False,
        "notification_mutation": False,
        "notification_persistence": False,
        "notification_read_state_mutation": False,
        "intelligence_generation": False,
        "decision_generation": False,
        "d13_modification": False,
        "risk_generation": False,
        "cas_generation": False,
        "execution": False,
    }

    if metadata:
        view_metadata.update(dict(metadata))

    return NotificationPageView(
        page_name=NOTIFICATION_PAGE_NAME,
        page_title=NOTIFICATION_PAGE_TITLE,
        route=NOTIFICATION_ROUTE,
        status=normalized_status,
        mode=normalized_mode,
        identity=normalized_identity,
        notifications=normalized_items,
        summary=normalized_summary,
        badges=badges,
        actions=actions,
        authenticated=_notification_bool(authenticated),
        generated_at=_notification_now(),
        metadata=view_metadata,
    )


# ============================================================================
# PART 1 EXPORTS
# ============================================================================

__all__ = [
    # Identity
    "NOTIFICATION_PAGE_ENGINE",
    "NOTIFICATION_PAGE_VERSION",
    "NOTIFICATION_PAGE_NAME",
    "NOTIFICATION_PAGE_TITLE",
    "NOTIFICATION_PAGE_DESCRIPTION",
    "NOTIFICATION_ROUTE",

    # Authority
    "NOTIFICATION_UI_AUTHORITY",

    # Enums
    "NotificationPageStatus",
    "NotificationPresentationMode",
    "NotificationState",
    "NotificationCategory",
    "NotificationPriority",
    "NotificationBadgeType",

    # Contracts
    "NotificationIdentityView",
    "NotificationItemView",
    "NotificationSummaryView",
    "NotificationBadge",
    "NotificationAction",
    "NotificationPageRequest",
    "NotificationPageView",

    # Defaults
    "DEFAULT_NOTIFICATION_ACTIONS",

    # Helpers
    "normalize_notification_identity",
    "normalize_notification_item",
    "normalize_notification_items",

    # Badges / actions
    "build_notification_status_badge",
    "build_notification_unread_badge",
    "build_notification_important_badge",
    "get_notification_actions",
    "build_notification_badges",

    # Page
    "build_notification_page_view",
]
# ============================================================================
# PART 2 — SOURCE STATE, SECTIONS & COMPOSITION
# ============================================================================


@dataclass(frozen=True)
class NotificationSourceState:
    """
    Upstream notification presentation source.

    The notification service owns the actual notification records.
    This object only carries already-available information into the UI.
    """

    identity: NotificationIdentityView = field(
        default_factory=NotificationIdentityView
    )

    notifications: Sequence[NotificationItemView] = field(
        default_factory=tuple
    )

    source_available: bool = False
    source_errors: Sequence[str] = field(default_factory=tuple)

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class NotificationSectionState:
    """Presentation state for one notification section/filter."""

    section_id: str = ""
    title: str = ""
    description: str = ""
    route: str = ""

    visible: bool = True
    enabled: bool = True

    status: NotificationPageStatus = NotificationPageStatus.UNKNOWN

    priority: NotificationPriority = NotificationPriority.NORMAL

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# DEFAULT SECTIONS
# ============================================================================

DEFAULT_NOTIFICATION_SECTIONS: tuple[
    NotificationSectionState, ...
] = (
    NotificationSectionState(
        section_id="all",
        title="All Notifications",
        description="View all available notifications.",
        route=NOTIFICATION_ROUTE,
        priority=NotificationPriority.NORMAL,
    ),
    NotificationSectionState(
        section_id="unread",
        title="Unread",
        description="View notifications that are currently unread.",
        route=f"{NOTIFICATION_ROUTE}/unread",
        priority=NotificationPriority.IMPORTANT,
    ),
    NotificationSectionState(
        section_id="important",
        title="Important",
        description="View important notification items.",
        route=f"{NOTIFICATION_ROUTE}/important",
        priority=NotificationPriority.IMPORTANT,
    ),
    NotificationSectionState(
        section_id="system",
        title="System",
        description="View system-level notifications.",
        route=f"{NOTIFICATION_ROUTE}/system",
        priority=NotificationPriority.NORMAL,
    ),
    NotificationSectionState(
        section_id="security",
        title="Security",
        description="View security-related notifications.",
        route=f"{NOTIFICATION_ROUTE}/security",
        priority=NotificationPriority.HIGH,
    ),
)


# ============================================================================
# SOURCE NORMALIZATION
# ============================================================================

def normalize_notification_source_state(
    source: Optional[NotificationSourceState] = None,
) -> NotificationSourceState:
    """
    Normalize upstream notification source state.

    No notification truth is created here.
    """

    if source is None:
        return NotificationSourceState(
            identity=NotificationIdentityView(),
            notifications=tuple(),
            source_available=False,
            source_errors=("NOTIFICATION_SOURCE_NOT_PROVIDED",),
            metadata={
                "normalized": True,
                "source_present": False,
            },
        )

    identity = normalize_notification_identity(source.identity)
    notifications = normalize_notification_items(source.notifications)

    errors = tuple(
        _notification_text(error)
        for error in (source.source_errors or tuple())
        if _notification_text(error)
    )

    return NotificationSourceState(
        identity=identity,
        notifications=notifications,
        source_available=_notification_bool(source.source_available),
        source_errors=errors,
        metadata=dict(source.metadata or {}),
    )


# ============================================================================
# PRESENTATION READINESS
# ============================================================================

def evaluate_notification_presentation_status(
    source: NotificationSourceState,
) -> NotificationPageStatus:
    """
    Determine notification page presentation readiness.

    This is NOT notification-service health authority.
    It only determines whether the UI can safely present the supplied source.
    """

    if not source.identity.authenticated:
        return NotificationPageStatus.LOCKED

    if not source.source_available:
        return NotificationPageStatus.DEGRADED

    if source.source_errors:
        return NotificationPageStatus.DEGRADED

    return NotificationPageStatus.READY


# ============================================================================
# SECTION COMPOSITION
# ============================================================================

def build_notification_sections(
    *,
    authenticated: bool,
    page_status: NotificationPageStatus,
) -> tuple[NotificationSectionState, ...]:
    """
    Build notification navigation/filter sections.

    Sections only control presentation availability.
    """

    if not authenticated:
        return tuple(
            NotificationSectionState(
                section_id=section.section_id,
                title=section.title,
                description=section.description,
                route=section.route,
                visible=section.section_id == "all",
                enabled=False,
                status=NotificationPageStatus.LOCKED,
                priority=section.priority,
                metadata={
                    **section.metadata,
                    "presentation_locked": True,
                },
            )
            for section in DEFAULT_NOTIFICATION_SECTIONS
        )

    if page_status == NotificationPageStatus.LOCKED:
        return tuple(
            NotificationSectionState(
                section_id=section.section_id,
                title=section.title,
                description=section.description,
                route=section.route,
                visible=section.section_id == "all",
                enabled=False,
                status=NotificationPageStatus.LOCKED,
                priority=section.priority,
                metadata={
                    **section.metadata,
                    "presentation_locked": True,
                },
            )
            for section in DEFAULT_NOTIFICATION_SECTIONS
        )

    return tuple(
        NotificationSectionState(
            section_id=section.section_id,
            title=section.title,
            description=section.description,
            route=section.route,
            visible=True,
            enabled=page_status != NotificationPageStatus.ERROR,
            status=page_status,
            priority=section.priority,
            metadata=dict(section.metadata),
        )
        for section in DEFAULT_NOTIFICATION_SECTIONS
    )


# ============================================================================
# SUMMARY ENGINE — PRESENTATION ONLY
# ============================================================================

def build_notification_summary(
    notifications: Sequence[NotificationItemView],
) -> NotificationSummaryView:
    """
    Build display summary from upstream notification records.

    This function does not modify notification state.
    """

    items = tuple(
        item
        for item in notifications
        if isinstance(item, NotificationItemView)
        and item.visible
    )

    total_count = len(items)

    unread_count = sum(
        1
        for item in items
        if item.state == NotificationState.UNREAD
    )

    important_count = sum(
        1
        for item in items
        if item.priority
        in {
            NotificationPriority.IMPORTANT,
            NotificationPriority.HIGH,
            NotificationPriority.CRITICAL,
        }
    )

    critical_count = sum(
        1
        for item in items
        if item.priority == NotificationPriority.CRITICAL
    )

    system_count = sum(
        1
        for item in items
        if item.category == NotificationCategory.SYSTEM
    )

    market_count = sum(
        1
        for item in items
        if item.category == NotificationCategory.MARKET
    )

    account_count = sum(
        1
        for item in items
        if item.category == NotificationCategory.ACCOUNT
    )

    security_count = sum(
        1
        for item in items
        if item.category == NotificationCategory.SECURITY
    )

    automation_count = sum(
        1
        for item in items
        if item.category == NotificationCategory.AUTOMATION
    )

    return NotificationSummaryView(
        total_count=total_count,
        unread_count=unread_count,
        important_count=important_count,
        critical_count=critical_count,
        system_count=system_count,
        market_count=market_count,
        account_count=account_count,
        security_count=security_count,
        automation_count=automation_count,
        has_unread=unread_count > 0,
        has_important=important_count > 0,
        metadata={
            "summary_source": "UPSTREAM_NOTIFICATION_ITEMS",
            "calculation_scope": "PRESENTATION_ONLY",
        },
    )


# ============================================================================
# DISPLAY HELPERS
# ============================================================================

def resolve_notification_display_name(
    identity: NotificationIdentityView,
) -> str:
    """Resolve safe display name without creating identity truth."""

    if identity.display_name:
        return identity.display_name

    if identity.email:
        return identity.email

    return "Notifications"


def build_notification_status_message(
    status: NotificationPageStatus,
    summary: NotificationSummaryView,
    errors: Sequence[str] = tuple(),
) -> str:
    """Build human-readable notification page status."""

    if status == NotificationPageStatus.LOCKED:
        return "Sign in to view your notifications."

    if status == NotificationPageStatus.LOADING:
        return "Loading notification center..."

    if status == NotificationPageStatus.ERROR:
        return "Notification center is currently unavailable."

    if status == NotificationPageStatus.DEGRADED:
        if errors:
            return "Notification data is partially unavailable."
        return "Notification data is currently unavailable."

    if status == NotificationPageStatus.READY:
        if summary.unread_count > 0:
            return (
                f"You have {summary.unread_count} unread "
                "notification(s)."
            )
        return "You are up to date."

    return "Notification status is unavailable."


def build_notification_mode_message(
    mode: NotificationPresentationMode,
    summary: NotificationSummaryView,
) -> str:
    """Build presentation message for the active notification filter."""

    if mode == NotificationPresentationMode.UNREAD:
        return f"{summary.unread_count} unread notification(s)."

    if mode == NotificationPresentationMode.IMPORTANT:
        return (
            f"{summary.important_count} important "
            "notification(s)."
        )

    if mode == NotificationPresentationMode.SYSTEM:
        return f"{summary.system_count} system notification(s)."

    if mode == NotificationPresentationMode.MARKET:
        return f"{summary.market_count} market notification(s)."

    if mode == NotificationPresentationMode.ACCOUNT:
        return f"{summary.account_count} account notification(s)."

    if mode == NotificationPresentationMode.SECURITY:
        return (
            f"{summary.security_count} security "
            "notification(s)."
        )

    if mode == NotificationPresentationMode.AUTOMATION:
        return (
            f"{summary.automation_count} automation "
            "notification(s)."
        )

    return f"{summary.total_count} notification(s)."


# ============================================================================
# COMPOSITION SUMMARY
# ============================================================================

@dataclass(frozen=True)
class NotificationPageSummary:
    """Compact summary for the notification workspace."""

    display_name: str = ""
    email: str = ""

    status_label: str = ""
    status_message: str = ""

    total_count: int = 0
    unread_count: int = 0
    important_count: int = 0
    critical_count: int = 0

    active_mode: NotificationPresentationMode = (
        NotificationPresentationMode.ALL
    )

    has_unread: bool = False
    has_important: bool = False

    authenticated: bool = False

    priority: NotificationPriority = NotificationPriority.NORMAL

    metadata: Dict[str, Any] = field(default_factory=dict)


def build_notification_page_summary(
    *,
    identity: NotificationIdentityView,
    summary: NotificationSummaryView,
    status: NotificationPageStatus,
    mode: NotificationPresentationMode,
) -> NotificationPageSummary:
    """Build compact notification page summary."""

    priority = NotificationPriority.NORMAL

    if summary.critical_count > 0:
        priority = NotificationPriority.CRITICAL
    elif summary.important_count > 0:
        priority = NotificationPriority.HIGH
    elif summary.unread_count > 0:
        priority = NotificationPriority.IMPORTANT

    return NotificationPageSummary(
        display_name=resolve_notification_display_name(identity),
        email=identity.email,
        status_label=status.value,
        status_message=build_notification_status_message(
            status,
            summary,
        ),
        total_count=summary.total_count,
        unread_count=summary.unread_count,
        important_count=summary.important_count,
        critical_count=summary.critical_count,
        active_mode=mode,
        has_unread=summary.has_unread,
        has_important=summary.has_important,
        authenticated=identity.authenticated,
        priority=priority,
        metadata={
            "presentation_only": True,
        },
    )


# ============================================================================
# PAGE COMPOSITION
# ============================================================================

@dataclass(frozen=True)
class NotificationPageComposition:
    """
    Complete notification workspace composition.

    Contains presentation objects only.
    """

    page: NotificationPageView = field(
        default_factory=NotificationPageView
    )

    summary: NotificationPageSummary = field(
        default_factory=NotificationPageSummary
    )

    sections: Sequence[NotificationSectionState] = field(
        default_factory=tuple
    )

    status_message: str = ""

    mode_message: str = ""

    errors: Sequence[str] = field(default_factory=tuple)

    generated_at: datetime = field(default_factory=_notification_now)

    metadata: Dict[str, Any] = field(default_factory=dict)


def compose_notification_page(
    source: Optional[NotificationSourceState] = None,
    *,
    mode: NotificationPresentationMode = (
        NotificationPresentationMode.ALL
    ),
) -> NotificationPageComposition:
    """
    Compose the complete notification page.

    Flow
    ----
    Upstream Notification Source
        ↓
    Source Normalization
        ↓
    Presentation Readiness
        ↓
    Notification Summary
        ↓
    Section Composition
        ↓
    Page View
        ↓
    Page Composition

    No notification mutation occurs.
    """

    normalized_source = normalize_notification_source_state(source)

    status = evaluate_notification_presentation_status(
        normalized_source
    )

    normalized_mode = _notification_enum(
        NotificationPresentationMode,
        mode,
        NotificationPresentationMode.ALL,
    )

    summary = build_notification_summary(
        normalized_source.notifications
    )

    page_summary = build_notification_page_summary(
        identity=normalized_source.identity,
        summary=summary,
        status=status,
        mode=normalized_mode,
    )

    sections = build_notification_sections(
        authenticated=normalized_source.identity.authenticated,
        page_status=status,
    )

    page = build_notification_page_view(
        identity=normalized_source.identity,
        notifications=normalized_source.notifications,
        summary=summary,
        status=status,
        mode=normalized_mode,
        authenticated=normalized_source.identity.authenticated,
        source="NOTIFICATION_SOURCE",
        metadata={
            "source_available": normalized_source.source_available,
            "source_errors": list(
                normalized_source.source_errors
            ),
        },
    )

    status_message = build_notification_status_message(
        status,
        summary,
        normalized_source.source_errors,
    )

    mode_message = build_notification_mode_message(
        normalized_mode,
        summary,
    )

    return NotificationPageComposition(
        page=page,
        summary=page_summary,
        sections=sections,
        status_message=status_message,
        mode_message=mode_message,
        errors=tuple(normalized_source.source_errors),
        generated_at=_notification_now(),
        metadata={
            "ui_only": True,
            "presentation_only": True,
            "source_normalized": True,
            "notification_generation": False,
            "notification_delivery": False,
            "notification_persistence": False,
            "notification_mutation": False,
            "notification_read_state_mutation": False,
            "intelligence_generation": False,
            "decision_generation": False,
            "d13_modification": False,
            "risk_generation": False,
            "cas_generation": False,
            "execution": False,
        },
    )


# ============================================================================
# PART 2 EXPORTS
# ============================================================================

__all__.extend(
    [
        # Source
        "NotificationSourceState",
        "normalize_notification_source_state",

        # Sections
        "NotificationSectionState",
        "DEFAULT_NOTIFICATION_SECTIONS",
        "build_notification_sections",

        # Readiness
        "evaluate_notification_presentation_status",

        # Summary
        "build_notification_summary",
        "NotificationPageSummary",
        "build_notification_page_summary",

        # Display
        "resolve_notification_display_name",
        "build_notification_status_message",
        "build_notification_mode_message",

        # Composition
        "NotificationPageComposition",
        "compose_notification_page",
    ]
)
# ============================================================================
# PART 3 — STATE, INTERACTION, CONTROLLER & SNAPSHOT
# ============================================================================


class NotificationInteraction(str, Enum):
    """Presentation/navigation interactions."""

    OPEN_ALL = "OPEN_ALL"
    OPEN_UNREAD = "OPEN_UNREAD"
    OPEN_IMPORTANT = "OPEN_IMPORTANT"
    OPEN_SYSTEM = "OPEN_SYSTEM"
    OPEN_MARKET = "OPEN_MARKET"
    OPEN_ACCOUNT = "OPEN_ACCOUNT"
    OPEN_AUTOMATION = "OPEN_AUTOMATION"
    OPEN_SECURITY = "OPEN_SECURITY"
    REFRESH = "REFRESH"
    LOCK = "LOCK"
    NONE = "NONE"


NOTIFICATION_INTERACTION_ROUTES: Dict[
    NotificationInteraction, str
] = {
    NotificationInteraction.OPEN_ALL: NOTIFICATION_ROUTE,
    NotificationInteraction.OPEN_UNREAD: (
        f"{NOTIFICATION_ROUTE}/unread"
    ),
    NotificationInteraction.OPEN_IMPORTANT: (
        f"{NOTIFICATION_ROUTE}/important"
    ),
    NotificationInteraction.OPEN_SYSTEM: (
        f"{NOTIFICATION_ROUTE}/system"
    ),
    NotificationInteraction.OPEN_MARKET: (
        f"{NOTIFICATION_ROUTE}/market"
    ),
    NotificationInteraction.OPEN_ACCOUNT: (
        f"{NOTIFICATION_ROUTE}/account"
    ),
    NotificationInteraction.OPEN_AUTOMATION: (
        f"{NOTIFICATION_ROUTE}/automation"
    ),
    NotificationInteraction.OPEN_SECURITY: (
        f"{NOTIFICATION_ROUTE}/security"
    ),
}


def normalize_notification_interaction(
    value: Any,
) -> NotificationInteraction:
    """Safely normalize an interaction."""

    return _notification_enum(
        NotificationInteraction,
        value,
        NotificationInteraction.NONE,
    )


# ============================================================================
# PAGE STATE
# ============================================================================

@dataclass
class NotificationPageState:
    """
    Mutable presentation state for the notification workspace.

    This state does not represent notification-service persistence.
    """

    user_id: str = ""

    authenticated: bool = False

    mode: NotificationPresentationMode = (
        NotificationPresentationMode.ALL
    )

    status: NotificationPageStatus = (
        NotificationPageStatus.UNKNOWN
    )

    current_route: str = NOTIFICATION_ROUTE

    initialized: bool = False
    ready: bool = False
    locked: bool = True

    interaction_count: int = 0
    refresh_count: int = 0

    last_interaction: NotificationInteraction = (
        NotificationInteraction.NONE
    )

    last_error: str = ""

    metadata: Dict[str, Any] = field(default_factory=dict)


def create_notification_page_state(
    *,
    user_id: str = "",
    authenticated: bool = False,
) -> NotificationPageState:
    """Create safe default notification page state."""

    return NotificationPageState(
        user_id=_notification_text(user_id),
        authenticated=_notification_bool(authenticated),
        status=(
            NotificationPageStatus.UNKNOWN
            if authenticated
            else NotificationPageStatus.LOCKED
        ),
        current_route=NOTIFICATION_ROUTE,
        initialized=False,
        ready=False,
        locked=not authenticated,
    )


def normalize_notification_page_state(
    state: NotificationPageState,
) -> NotificationPageState:
    """Normalize mutable presentation state."""

    authenticated = _notification_bool(state.authenticated)
    locked = _notification_bool(
        state.locked,
        not authenticated,
    )

    if not authenticated:
        locked = True

    if state.current_route not in {
        NOTIFICATION_ROUTE,
        f"{NOTIFICATION_ROUTE}/unread",
        f"{NOTIFICATION_ROUTE}/important",
        f"{NOTIFICATION_ROUTE}/system",
        f"{NOTIFICATION_ROUTE}/market",
        f"{NOTIFICATION_ROUTE}/account",
        f"{NOTIFICATION_ROUTE}/automation",
        f"{NOTIFICATION_ROUTE}/security",
    }:
        current_route = NOTIFICATION_ROUTE
    else:
        current_route = state.current_route

    return NotificationPageState(
        user_id=_notification_text(state.user_id),
        authenticated=authenticated,
        mode=_notification_enum(
            NotificationPresentationMode,
            state.mode,
            NotificationPresentationMode.ALL,
        ),
        status=_notification_enum(
            NotificationPageStatus,
            state.status,
            NotificationPageStatus.UNKNOWN,
        ),
        current_route=current_route,
        initialized=_notification_bool(state.initialized),
        ready=_notification_bool(state.ready),
        locked=locked,
        interaction_count=max(
            0,
            int(state.interaction_count),
        ),
        refresh_count=max(
            0,
            int(state.refresh_count),
        ),
        last_interaction=normalize_notification_interaction(
            state.last_interaction
        ),
        last_error=_notification_text(state.last_error),
        metadata=dict(state.metadata or {}),
    )


# ============================================================================
# ROUTE / MODE
# ============================================================================

def route_to_notification_mode(
    route: str,
) -> NotificationPresentationMode:
    """Map notification route to presentation mode."""

    mapping = {
        NOTIFICATION_ROUTE: NotificationPresentationMode.ALL,
        f"{NOTIFICATION_ROUTE}/unread": (
            NotificationPresentationMode.UNREAD
        ),
        f"{NOTIFICATION_ROUTE}/important": (
            NotificationPresentationMode.IMPORTANT
        ),
        f"{NOTIFICATION_ROUTE}/system": (
            NotificationPresentationMode.SYSTEM
        ),
        f"{NOTIFICATION_ROUTE}/market": (
            NotificationPresentationMode.MARKET
        ),
        f"{NOTIFICATION_ROUTE}/account": (
            NotificationPresentationMode.ACCOUNT
        ),
        f"{NOTIFICATION_ROUTE}/automation": (
            NotificationPresentationMode.AUTOMATION
        ),
        f"{NOTIFICATION_ROUTE}/security": (
            NotificationPresentationMode.SECURITY
        ),
    }

    return mapping.get(
        route,
        NotificationPresentationMode.ALL,
    )


# ============================================================================
# INTERACTION RESULT
# ============================================================================

@dataclass(frozen=True)
class NotificationInteractionResult:
    """Result of a presentation interaction."""

    interaction: NotificationInteraction = (
        NotificationInteraction.NONE
    )

    requested_route: str = ""

    resolved_route: str = NOTIFICATION_ROUTE

    allowed: bool = False

    reason: str = ""

    mode: NotificationPresentationMode = (
        NotificationPresentationMode.ALL
    )

    metadata: Dict[str, Any] = field(default_factory=dict)


def evaluate_notification_route_access(
    *,
    route: str,
    authenticated: bool,
    locked: bool,
) -> tuple[bool, str]:
    """
    Evaluate notification-page route access.

    Presentation access only. No authentication or security authority.
    """

    known_routes = {
        NOTIFICATION_ROUTE,
        f"{NOTIFICATION_ROUTE}/unread",
        f"{NOTIFICATION_ROUTE}/important",
        f"{NOTIFICATION_ROUTE}/system",
        f"{NOTIFICATION_ROUTE}/market",
        f"{NOTIFICATION_ROUTE}/account",
        f"{NOTIFICATION_ROUTE}/automation",
        f"{NOTIFICATION_ROUTE}/security",
    }

    if route not in known_routes:
        return False, "NOTIFICATION_ROUTE_NOT_FOUND"

    if not authenticated:
        return False, "AUTHENTICATION_REQUIRED"

    if locked:
        return False, "NOTIFICATION_PAGE_LOCKED"

    return True, "ALLOWED"


def resolve_notification_interaction(
    interaction: NotificationInteraction,
    *,
    authenticated: bool,
    locked: bool,
) -> NotificationInteractionResult:
    """Resolve a notification presentation interaction."""

    interaction = normalize_notification_interaction(interaction)

    if interaction == NotificationInteraction.NONE:
        return NotificationInteractionResult(
            interaction=interaction,
            requested_route=NOTIFICATION_ROUTE,
            resolved_route=NOTIFICATION_ROUTE,
            allowed=False,
            reason="NO_INTERACTION",
            mode=NotificationPresentationMode.ALL,
        )

    if interaction == NotificationInteraction.REFRESH:
        return NotificationInteractionResult(
            interaction=interaction,
            requested_route=NOTIFICATION_ROUTE,
            resolved_route=NOTIFICATION_ROUTE,
            allowed=authenticated and not locked,
            reason=(
                "ALLOWED"
                if authenticated and not locked
                else "AUTHENTICATION_OR_LOCK_REQUIRED"
            ),
            mode=NotificationPresentationMode.ALL,
        )

    if interaction == NotificationInteraction.LOCK:
        return NotificationInteractionResult(
            interaction=interaction,
            requested_route=NOTIFICATION_ROUTE,
            resolved_route=NOTIFICATION_ROUTE,
            allowed=True,
            reason="UI_LOCK_ALLOWED",
            mode=NotificationPresentationMode.ALL,
        )

    requested_route = NOTIFICATION_INTERACTION_ROUTES.get(
        interaction,
        NOTIFICATION_ROUTE,
    )

    allowed, reason = evaluate_notification_route_access(
        route=requested_route,
        authenticated=authenticated,
        locked=locked,
    )

    return NotificationInteractionResult(
        interaction=interaction,
        requested_route=requested_route,
        resolved_route=(
            requested_route
            if allowed
            else NOTIFICATION_ROUTE
        ),
        allowed=allowed,
        reason=reason,
        mode=route_to_notification_mode(
            requested_route
        ),
        metadata={
            "presentation_only": True,
        },
    )


# ============================================================================
# CONTROLLER
# ============================================================================

class NotificationPageController:
    """
    Controller for notification-page presentation state.

    The controller does NOT:
    - send notifications
    - mark notifications read
    - archive notifications
    - persist notification state
    - modify notification records
    """

    def __init__(
        self,
        state: Optional[NotificationPageState] = None,
    ) -> None:
        self._state = normalize_notification_page_state(
            state
            if state is not None
            else create_notification_page_state()
        )

        self._interaction_history: List[
            NotificationInteractionResult
        ] = []

        self._last_composition: Optional[
            NotificationPageComposition
        ] = None

    @property
    def state(self) -> NotificationPageState:
        return normalize_notification_page_state(
            self._state
        )

    @property
    def current_route(self) -> str:
        return self._state.current_route

    @property
    def current_mode(self) -> NotificationPresentationMode:
        return self._state.mode

    @property
    def status(self) -> NotificationPageStatus:
        return self._state.status

    @property
    def last_composition(
        self,
    ) -> Optional[NotificationPageComposition]:
        return self._last_composition

    def initialize(
        self,
        source: Optional[NotificationSourceState] = None,
    ) -> NotificationPageComposition:
        """Initialize the presentation controller."""

        normalized_source = (
            normalize_notification_source_state(source)
        )

        self._state.user_id = (
            normalized_source.identity.user_id
        )

        self._state.authenticated = (
            normalized_source.identity.authenticated
        )

        self._state.locked = (
            not self._state.authenticated
        )

        self._state.initialized = True

        composition = self.compose(
            normalized_source
        )

        self._state.ready = (
            composition.page.status
            == NotificationPageStatus.READY
            and not self._state.locked
        )

        return composition

    def interact(
        self,
        interaction: NotificationInteraction,
    ) -> NotificationInteractionResult:
        """Process a presentation interaction."""

        interaction = normalize_notification_interaction(
            interaction
        )

        result = resolve_notification_interaction(
            interaction,
            authenticated=self._state.authenticated,
            locked=self._state.locked,
        )

        self._state.interaction_count += 1
        self._state.last_interaction = interaction

        if result.allowed:
            if interaction == NotificationInteraction.LOCK:
                self.lock()
            elif interaction == NotificationInteraction.REFRESH:
                self._state.refresh_count += 1
            else:
                self._state.current_route = (
                    result.resolved_route
                )
                self._state.mode = result.mode

        self._interaction_history.append(result)

        return result

    def navigate(
        self,
        route: str,
    ) -> NotificationInteractionResult:
        """Navigate within the notification presentation workspace."""

        route = _notification_text(
            route,
            NOTIFICATION_ROUTE,
        )

        mode = route_to_notification_mode(route)

        interaction_map = {
            NotificationPresentationMode.ALL:
                NotificationInteraction.OPEN_ALL,
            NotificationPresentationMode.UNREAD:
                NotificationInteraction.OPEN_UNREAD,
            NotificationPresentationMode.IMPORTANT:
                NotificationInteraction.OPEN_IMPORTANT,
            NotificationPresentationMode.SYSTEM:
                NotificationInteraction.OPEN_SYSTEM,
            NotificationPresentationMode.MARKET:
                NotificationInteraction.OPEN_MARKET,
            NotificationPresentationMode.ACCOUNT:
                NotificationInteraction.OPEN_ACCOUNT,
            NotificationPresentationMode.AUTOMATION:
                NotificationInteraction.OPEN_AUTOMATION,
            NotificationPresentationMode.SECURITY:
                NotificationInteraction.OPEN_SECURITY,
        }

        interaction = interaction_map.get(
            mode,
            NotificationInteraction.NONE,
        )

        return self.interact(interaction)

    def lock(self) -> None:
        """Lock the notification UI only."""

        self._state.locked = True
        self._state.ready = False
        self._state.status = NotificationPageStatus.LOCKED

    def unlock(self) -> bool:
        """
        Presentation unlock.

        Actual authentication remains external.
        """

        if not self._state.authenticated:
            return False

        self._state.locked = False

        if self._state.status == NotificationPageStatus.LOCKED:
            self._state.status = NotificationPageStatus.UNKNOWN

        return True

    def set_authenticated(
        self,
        authenticated: bool,
    ) -> None:
        """
        Update presentation authentication state.

        This does not authenticate the user.
        """

        authenticated = _notification_bool(authenticated)

        self._state.authenticated = authenticated

        if not authenticated:
            self._state.locked = True
            self._state.ready = False
            self._state.status = NotificationPageStatus.LOCKED

    def compose(
        self,
        source: Optional[NotificationSourceState] = None,
    ) -> NotificationPageComposition:
        """Compose and retain the latest presentation."""

        composition = compose_notification_page(
            source,
            mode=self._state.mode,
        )

        self._last_composition = composition

        self._state.status = composition.page.status

        if composition.page.status == NotificationPageStatus.LOCKED:
            self._state.locked = True
            self._state.ready = False
        elif not self._state.locked:
            self._state.ready = (
                composition.page.status
                == NotificationPageStatus.READY
            )

        self._state.last_error = (
            composition.errors[0]
            if composition.errors
            else ""
        )

        return composition

    @property
    def interaction_history(
        self,
    ) -> tuple[NotificationInteractionResult, ...]:
        """Return presentation interaction history."""

        return tuple(self._interaction_history)

    def clear_interaction_history(self) -> None:
        """Clear local UI interaction history."""

        self._interaction_history.clear()


# ============================================================================
# SNAPSHOT
# ============================================================================

@dataclass(frozen=True)
class NotificationPageSnapshot:
    """Immutable presentation snapshot."""

    state: NotificationPageState = field(
        default_factory=NotificationPageState
    )

    composition: NotificationPageComposition = field(
        default_factory=NotificationPageComposition
    )

    captured_at: datetime = field(
        default_factory=_notification_now
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def build_notification_page_snapshot(
    controller: NotificationPageController,
    source: Optional[NotificationSourceState] = None,
) -> NotificationPageSnapshot:
    """Build a presentation snapshot from the controller."""

    composition = controller.compose(source)

    state = normalize_notification_page_state(
        controller.state
    )

    return NotificationPageSnapshot(
        state=state,
        composition=composition,
        captured_at=_notification_now(),
        metadata={
            "ui_only": True,
            "presentation_only": True,
            "notification_mutation": False,
            "notification_delivery": False,
            "notification_persistence": False,
            "d13_modification": False,
            "risk_override": False,
            "cas_bypass": False,
            "execution": False,
        },
    )


# ============================================================================
# PART 3 EXPORTS
# ============================================================================

__all__.extend(
    [
        # Interactions
        "NotificationInteraction",
        "NOTIFICATION_INTERACTION_ROUTES",
        "normalize_notification_interaction",

        # State
        "NotificationPageState",
        "create_notification_page_state",
        "normalize_notification_page_state",

        # Routing
        "route_to_notification_mode",
        "evaluate_notification_route_access",

        # Interaction result
        "NotificationInteractionResult",
        "resolve_notification_interaction",

        # Controller
        "NotificationPageController",

        # Snapshot
        "NotificationPageSnapshot",
        "build_notification_page_snapshot",
    ]
)
# ============================================================================
# PART 4 — SERIALIZATION, VALIDATION & HEALTH
# ============================================================================


def _serialize_notification_value(value: Any) -> Any:
    """Recursively serialize notification presentation values."""

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            str(key): _serialize_notification_value(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            _serialize_notification_value(item)
            for item in value
        ]

    if hasattr(value, "__dataclass_fields__"):
        return {
            name: _serialize_notification_value(
                getattr(value, name)
            )
            for name in value.__dataclass_fields__
        }

    return value


# ============================================================================
# SERIALIZERS
# ============================================================================

def serialize_notification_identity(
    value: NotificationIdentityView,
) -> Dict[str, Any]:
    return _serialize_notification_value(value)


def serialize_notification_item(
    value: NotificationItemView,
) -> Dict[str, Any]:
    return _serialize_notification_value(value)


def serialize_notification_summary(
    value: NotificationSummaryView,
) -> Dict[str, Any]:
    return _serialize_notification_value(value)


def serialize_notification_badge(
    value: NotificationBadge,
) -> Dict[str, Any]:
    return _serialize_notification_value(value)


def serialize_notification_action(
    value: NotificationAction,
) -> Dict[str, Any]:
    return _serialize_notification_value(value)


def serialize_notification_page_request(
    value: NotificationPageRequest,
) -> Dict[str, Any]:
    return _serialize_notification_value(value)


def serialize_notification_page_view(
    value: NotificationPageView,
) -> Dict[str, Any]:
    return _serialize_notification_value(value)


def serialize_notification_source(
    value: NotificationSourceState,
) -> Dict[str, Any]:
    return _serialize_notification_value(value)


def serialize_notification_section(
    value: NotificationSectionState,
) -> Dict[str, Any]:
    return _serialize_notification_value(value)


def serialize_notification_page_summary(
    value: NotificationPageSummary,
) -> Dict[str, Any]:
    return _serialize_notification_value(value)


def serialize_notification_composition(
    value: NotificationPageComposition,
) -> Dict[str, Any]:
    return _serialize_notification_value(value)


def serialize_notification_state(
    value: NotificationPageState,
) -> Dict[str, Any]:
    return _serialize_notification_value(value)


def serialize_notification_interaction_result(
    value: NotificationInteractionResult,
) -> Dict[str, Any]:
    return _serialize_notification_value(value)


def serialize_notification_snapshot(
    value: NotificationPageSnapshot,
) -> Dict[str, Any]:
    return _serialize_notification_value(value)


# ============================================================================
# VALIDATION HELPERS
# ============================================================================

def validate_notification_identity(
    value: NotificationIdentityView,
) -> List[str]:
    """Validate identity presentation invariants."""

    errors: List[str] = []

    if not isinstance(value, NotificationIdentityView):
        return ["INVALID_NOTIFICATION_IDENTITY_TYPE"]

    if value.authenticated and not value.user_id:
        errors.append(
            "AUTHENTICATED_IDENTITY_REQUIRES_USER_ID"
        )

    if value.email and "@" not in value.email:
        errors.append(
            "IDENTITY_EMAIL_FORMAT_WARNING"
        )

    return errors


def validate_notification_item(
    value: NotificationItemView,
) -> List[str]:
    """Validate one notification presentation record."""

    errors: List[str] = []

    if not isinstance(value, NotificationItemView):
        return ["INVALID_NOTIFICATION_ITEM_TYPE"]

    if not value.notification_id:
        errors.append(
            "NOTIFICATION_ID_MISSING"
        )

    if not value.title and not value.message:
        errors.append(
            "NOTIFICATION_CONTENT_MISSING"
        )

    if (
        value.state == NotificationState.READ
        and value.read_at is None
    ):
        errors.append(
            "READ_NOTIFICATION_MISSING_READ_TIMESTAMP"
        )

    if (
        value.state == NotificationState.UNREAD
        and value.read_at is not None
    ):
        errors.append(
            "UNREAD_NOTIFICATION_HAS_READ_TIMESTAMP"
        )

    if (
        value.actionable
        and not value.action_route
    ):
        errors.append(
            "ACTIONABLE_NOTIFICATION_MISSING_ROUTE"
        )

    if (
        value.expires_at is not None
        and value.created_at is not None
        and value.expires_at < value.created_at
    ):
        errors.append(
            "NOTIFICATION_EXPIRY_BEFORE_CREATION"
        )

    return errors


def validate_notification_summary(
    value: NotificationSummaryView,
) -> List[str]:
    """Validate summary counters."""

    errors: List[str] = []

    if not isinstance(value, NotificationSummaryView):
        return ["INVALID_NOTIFICATION_SUMMARY_TYPE"]

    counters = {
        "total_count": value.total_count,
        "unread_count": value.unread_count,
        "important_count": value.important_count,
        "critical_count": value.critical_count,
        "system_count": value.system_count,
        "market_count": value.market_count,
        "account_count": value.account_count,
        "security_count": value.security_count,
        "automation_count": value.automation_count,
    }

    for name, count in counters.items():
        if count < 0:
            errors.append(
                f"NEGATIVE_NOTIFICATION_COUNTER:{name}"
            )

    if value.unread_count > value.total_count:
        errors.append(
            "UNREAD_COUNT_EXCEEDS_TOTAL_COUNT"
        )

    if value.critical_count > value.important_count:
        errors.append(
            "CRITICAL_COUNT_EXCEEDS_IMPORTANT_COUNT"
        )

    if value.has_unread != (value.unread_count > 0):
        errors.append(
            "HAS_UNREAD_FLAG_MISMATCH"
        )

    if value.has_important != (
        value.important_count > 0
    ):
        errors.append(
            "HAS_IMPORTANT_FLAG_MISMATCH"
        )

    return errors


def validate_notification_badge(
    value: NotificationBadge,
) -> List[str]:
    """Validate notification badge."""

    errors: List[str] = []

    if not isinstance(value, NotificationBadge):
        return ["INVALID_NOTIFICATION_BADGE_TYPE"]

    if value.visible and not value.label:
        errors.append(
            "VISIBLE_BADGE_MISSING_LABEL"
        )

    return errors


def validate_notification_action(
    value: NotificationAction,
) -> List[str]:
    """Validate navigation action."""

    errors: List[str] = []

    if not isinstance(value, NotificationAction):
        return ["INVALID_NOTIFICATION_ACTION_TYPE"]

    if value.visible and not value.label:
        errors.append(
            "VISIBLE_ACTION_MISSING_LABEL"
        )

    if value.enabled and not value.route:
        errors.append(
            "ENABLED_ACTION_MISSING_ROUTE"
        )

    if (
        value.requires_authentication
        and not value.route.startswith(
            NOTIFICATION_ROUTE
        )
    ):
        errors.append(
            "AUTHENTICATED_ACTION_OUTSIDE_NOTIFICATION_ROUTE"
        )

    return errors


# ============================================================================
# SOURCE / PAGE VALIDATION
# ============================================================================

def validate_notification_source(
    value: NotificationSourceState,
) -> List[str]:
    """Validate upstream source presentation contract."""

    errors: List[str] = []

    if not isinstance(value, NotificationSourceState):
        return ["INVALID_NOTIFICATION_SOURCE_TYPE"]

    errors.extend(
        validate_notification_identity(
            value.identity
        )
    )

    seen_ids = set()

    for item in value.notifications:
        errors.extend(
            validate_notification_item(item)
        )

        if item.notification_id:
            if item.notification_id in seen_ids:
                errors.append(
                    "DUPLICATE_NOTIFICATION_ID:"
                    f"{item.notification_id}"
                )
            seen_ids.add(item.notification_id)

    if not value.source_available and not value.source_errors:
        errors.append(
            "SOURCE_UNAVAILABLE_WITHOUT_SOURCE_ERROR"
        )

    return errors


def validate_notification_page_view(
    value: NotificationPageView,
) -> List[str]:
    """Validate complete notification page view."""

    errors: List[str] = []

    if not isinstance(value, NotificationPageView):
        return ["INVALID_NOTIFICATION_PAGE_VIEW_TYPE"]

    if value.page_name != NOTIFICATION_PAGE_NAME:
        errors.append(
            "NOTIFICATION_PAGE_NAME_MISMATCH"
        )

    if value.route != NOTIFICATION_ROUTE:
        errors.append(
            "NOTIFICATION_PAGE_ROUTE_MISMATCH"
        )

    errors.extend(
        validate_notification_identity(
            value.identity
        )
    )

    errors.extend(
        validate_notification_summary(
            value.summary
        )
    )

    for item in value.notifications:
        errors.extend(
            validate_notification_item(item)
        )

    for badge in value.badges:
        errors.extend(
            validate_notification_badge(badge)
        )

    for action in value.actions:
        errors.extend(
            validate_notification_action(action)
        )

    if not value.authenticated and (
        value.status != NotificationPageStatus.LOCKED
    ):
        errors.append(
            "UNAUTHENTICATED_PAGE_MUST_BE_LOCKED"
        )

    authority_errors = validate_notification_authority(
        value.metadata
    )

    errors.extend(authority_errors)

    return errors


def validate_notification_section(
    value: NotificationSectionState,
) -> List[str]:
    """Validate notification navigation section."""

    errors: List[str] = []

    if not isinstance(value, NotificationSectionState):
        return ["INVALID_NOTIFICATION_SECTION_TYPE"]

    if value.visible and not value.title:
        errors.append(
            "VISIBLE_NOTIFICATION_SECTION_MISSING_TITLE"
        )

    if value.visible and not value.route:
        errors.append(
            "VISIBLE_NOTIFICATION_SECTION_MISSING_ROUTE"
        )

    return errors


def validate_notification_page_summary(
    value: NotificationPageSummary,
) -> List[str]:
    """Validate compact page summary."""

    errors: List[str] = []

    if not isinstance(value, NotificationPageSummary):
        return ["INVALID_NOTIFICATION_PAGE_SUMMARY_TYPE"]

    counters = {
        "total_count": value.total_count,
        "unread_count": value.unread_count,
        "important_count": value.important_count,
        "critical_count": value.critical_count,
    }

    for name, count in counters.items():
        if count < 0:
            errors.append(
                f"NEGATIVE_PAGE_SUMMARY_COUNTER:{name}"
            )

    if value.unread_count > value.total_count:
        errors.append(
            "PAGE_SUMMARY_UNREAD_EXCEEDS_TOTAL"
        )

    if value.critical_count > value.important_count:
        errors.append(
            "PAGE_SUMMARY_CRITICAL_EXCEEDS_IMPORTANT"
        )

    return errors


def validate_notification_composition(
    value: NotificationPageComposition,
) -> List[str]:
    """Validate complete notification composition."""

    errors: List[str] = []

    if not isinstance(
        value,
        NotificationPageComposition,
    ):
        return [
            "INVALID_NOTIFICATION_COMPOSITION_TYPE"
        ]

    errors.extend(
        validate_notification_page_view(value.page)
    )

    errors.extend(
        validate_notification_page_summary(
            value.summary
        )
    )

    for section in value.sections:
        errors.extend(
            validate_notification_section(section)
        )

    return errors


# ============================================================================
# STATE / INTERACTION VALIDATION
# ============================================================================

def validate_notification_page_state(
    value: NotificationPageState,
) -> List[str]:
    """Validate mutable notification presentation state."""

    errors: List[str] = []

    if not isinstance(value, NotificationPageState):
        return ["INVALID_NOTIFICATION_PAGE_STATE_TYPE"]

    if value.interaction_count < 0:
        errors.append(
            "NEGATIVE_INTERACTION_COUNT"
        )

    if value.refresh_count < 0:
        errors.append(
            "NEGATIVE_REFRESH_COUNT"
        )

    if not value.authenticated and not value.locked:
        errors.append(
            "UNAUTHENTICATED_STATE_MUST_BE_LOCKED"
        )

    if value.ready and value.locked:
        errors.append(
            "READY_STATE_CANNOT_BE_LOCKED"
        )

    known_routes = {
        NOTIFICATION_ROUTE,
        f"{NOTIFICATION_ROUTE}/unread",
        f"{NOTIFICATION_ROUTE}/important",
        f"{NOTIFICATION_ROUTE}/system",
        f"{NOTIFICATION_ROUTE}/market",
        f"{NOTIFICATION_ROUTE}/account",
        f"{NOTIFICATION_ROUTE}/automation",
        f"{NOTIFICATION_ROUTE}/security",
    }

    if value.current_route not in known_routes:
        errors.append(
            "CURRENT_NOTIFICATION_ROUTE_UNKNOWN"
        )

    return errors


def validate_notification_interaction_result(
    value: NotificationInteractionResult,
) -> List[str]:
    """Validate interaction resolution."""

    errors: List[str] = []

    if not isinstance(
        value,
        NotificationInteractionResult,
    ):
        return [
            "INVALID_NOTIFICATION_INTERACTION_RESULT_TYPE"
        ]

    if value.allowed and not value.resolved_route:
        errors.append(
            "ALLOWED_INTERACTION_MISSING_RESOLVED_ROUTE"
        )

    if (
        value.allowed
        and value.reason
        not in {
            "ALLOWED",
            "UI_LOCK_ALLOWED",
        }
    ):
        errors.append(
            "ALLOWED_INTERACTION_REASON_MISMATCH"
        )

    if (
        value.interaction == NotificationInteraction.NONE
        and value.allowed
    ):
        errors.append(
            "NONE_INTERACTION_CANNOT_BE_ALLOWED"
        )

    return errors


def validate_notification_snapshot(
    value: NotificationPageSnapshot,
) -> List[str]:
    """Validate notification presentation snapshot."""

    errors: List[str] = []

    if not isinstance(
        value,
        NotificationPageSnapshot,
    ):
        return [
            "INVALID_NOTIFICATION_SNAPSHOT_TYPE"
        ]

    errors.extend(
        validate_notification_page_state(
            value.state
        )
    )

    errors.extend(
        validate_notification_composition(
            value.composition
        )
    )

    errors.extend(
        validate_notification_authority(
            value.metadata
        )
    )

    return errors


# ============================================================================
# AUTHORITY VALIDATION
# ============================================================================

def validate_notification_authority(
    metadata: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """
    Ensure forbidden notification/domain authorities remain disabled.

    This is an architecture guard, not a security mechanism.
    """

    errors: List[str] = []

    for authority, allowed in NOTIFICATION_UI_AUTHORITY.items():
        expected = bool(allowed)

        if not expected:
            if authority in (metadata or {}):
                actual = _notification_bool(
                    metadata.get(authority)
                )

                if actual:
                    errors.append(
                        f"FORBIDDEN_AUTHORITY_ENABLED:{authority}"
                    )

    protected_false_flags = {
        "notification_generation": False,
        "notification_delivery": False,
        "notification_mutation": False,
        "notification_persistence": False,
        "notification_read_state_mutation": False,
        "intelligence_generation": False,
        "decision_generation": False,
        "d13_modification": False,
        "risk_generation": False,
        "cas_generation": False,
        "execution": False,
        "upstream_mutation": False,
    }

    for key, expected in protected_false_flags.items():
        if key in (metadata or {}):
            if _notification_bool(
                metadata.get(key)
            ) != expected:
                errors.append(
                    f"PROTECTED_FLAG_VIOLATION:{key}"
                )

    return errors


# ============================================================================
# HEALTH CONTRACT
# ============================================================================

@dataclass(frozen=True)
class NotificationPageHealth:
    """Presentation-layer health report."""

    engine: str = NOTIFICATION_PAGE_ENGINE
    version: str = NOTIFICATION_PAGE_VERSION

    initialized: bool = False
    ready: bool = False

    status: NotificationPageStatus = (
        NotificationPageStatus.UNKNOWN
    )

    notification_count: int = 0
    unread_count: int = 0
    important_count: int = 0

    validation_errors: Sequence[str] = field(
        default_factory=tuple
    )

    authority_valid: bool = True

    operational: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def build_notification_page_health(
    controller: NotificationPageController,
    composition: Optional[
        NotificationPageComposition
    ] = None,
) -> NotificationPageHealth:
    """Build notification UI health report."""

    state = controller.state

    if composition is None:
        composition = controller.last_composition

    if composition is None:
        validation_errors = tuple(
            validate_notification_page_state(state)
        )

        return NotificationPageHealth(
            initialized=state.initialized,
            ready=False,
            status=state.status,
            notification_count=0,
            unread_count=0,
            important_count=0,
            validation_errors=validation_errors,
            authority_valid=True,
            operational=False,
            metadata={
                "ui_only": True,
                "composition_present": False,
            },
        )

    validation_errors = tuple(
        validate_notification_page_state(state)
        + validate_notification_composition(
            composition
        )
    )

    authority_errors = validate_notification_authority(
        {
            **composition.metadata,
            **composition.page.metadata,
        }
    )

    all_errors = tuple(
        list(validation_errors)
        + list(authority_errors)
    )

    authority_valid = not authority_errors

    operational = (
        state.initialized
        and state.ready
        and not state.locked
        and composition.page.status
        == NotificationPageStatus.READY
        and not all_errors
        and authority_valid
    )

    return NotificationPageHealth(
        initialized=state.initialized,
        ready=state.ready,
        status=composition.page.status,
        notification_count=(
            composition.summary.total_count
        ),
        unread_count=(
            composition.summary.unread_count
        ),
        important_count=(
            composition.summary.important_count
        ),
        validation_errors=all_errors,
        authority_valid=authority_valid,
        operational=operational,
        metadata={
            "ui_only": True,
            "presentation_only": True,
            "notification_authority_external": True,
        },
    )


def serialize_notification_page_health(
    value: NotificationPageHealth,
) -> Dict[str, Any]:
    return _serialize_notification_value(value)


# ============================================================================
# OPERATIONAL CHECK
# ============================================================================

def notification_page_operational_check(
    controller: Optional[
        NotificationPageController
    ] = None,
) -> Dict[str, Any]:
    """Return machine-readable notification page health."""

    if controller is None:
        controller = NotificationPageController()

    health = build_notification_page_health(
        controller
    )

    return {
        "engine": NOTIFICATION_PAGE_ENGINE,
        "version": NOTIFICATION_PAGE_VERSION,
        "operational": health.operational,
        "initialized": health.initialized,
        "ready": health.ready,
        "status": health.status.value,
        "notification_count": health.notification_count,
        "unread_count": health.unread_count,
        "important_count": health.important_count,
        "validation_errors": list(
            health.validation_errors
        ),
        "authority_valid": health.authority_valid,
        "ui_only": True,
        "notification_delivery": False,
        "notification_mutation": False,
        "notification_persistence": False,
        "notification_read_state_mutation": False,
        "intelligence_generation": False,
        "decision_generation": False,
        "d13_modification": False,
        "risk_generation": False,
        "cas_generation": False,
        "execution": False,
    }


# ============================================================================
# SUMMARY / DEFAULT OBJECTS
# ============================================================================

def notification_page_summary() -> Dict[str, Any]:
    """Return static module summary."""

    return {
        "engine": NOTIFICATION_PAGE_ENGINE,
        "version": NOTIFICATION_PAGE_VERSION,
        "name": NOTIFICATION_PAGE_NAME,
        "title": NOTIFICATION_PAGE_TITLE,
        "route": NOTIFICATION_ROUTE,
        "layer": "UI_PRESENTATION",
        "responsibility": [
            "NOTIFICATION_PRESENTATION",
            "NOTIFICATION_SUMMARY",
            "NOTIFICATION_STATUS",
            "NOTIFICATION_NAVIGATION",
            "NOTIFICATION_FILTER_PRESENTATION",
        ],
        "authority": {
            key: value
            for key, value
            in NOTIFICATION_UI_AUTHORITY.items()
        },
        "forbidden": [
            "NOTIFICATION_DELIVERY",
            "NOTIFICATION_SEND",
            "NOTIFICATION_MUTATION",
            "NOTIFICATION_PERSISTENCE",
            "NOTIFICATION_READ_STATE_MUTATION",
            "INTELLIGENCE_GENERATION",
            "DECISION_GENERATION",
            "D13_MODIFICATION",
            "RISK_OVERRIDE",
            "CAS_BYPASS",
            "EXECUTION",
        ],
    }


def create_default_notification_page() -> (
    NotificationPageController
):
    """Create a safe default notification controller."""

    return NotificationPageController(
        create_notification_page_state()
    )


def notification_page_module_check() -> Dict[str, Any]:
    """Static module integrity check."""

    controller = create_default_notification_page()

    source = NotificationSourceState(
        identity=NotificationIdentityView(
            authenticated=False,
        ),
        notifications=tuple(),
        source_available=False,
        source_errors=(
            "DEFAULT_NOTIFICATION_SOURCE_NOT_CONNECTED",
        ),
    )

    composition = compose_notification_page(
        source
    )

    errors = (
        validate_notification_page_state(
            controller.state
        )
        + validate_notification_composition(
            composition
        )
        + validate_notification_authority(
            composition.page.metadata
        )
    )

    return {
        "engine": NOTIFICATION_PAGE_ENGINE,
        "version": NOTIFICATION_PAGE_VERSION,
        "module": NOTIFICATION_PAGE_NAME,
        "valid": not errors,
        "errors": errors,
        "ui_only": True,
        "notification_mutation": False,
        "notification_delivery": False,
        "notification_persistence": False,
        "d13_modification": False,
        "risk_override": False,
        "cas_bypass": False,
        "execution": False,
    }


# ============================================================================
# PART 4 EXPORTS
# ============================================================================

__all__.extend(
    [
        # Serialization
        "_serialize_notification_value",
        "serialize_notification_identity",
        "serialize_notification_item",
        "serialize_notification_summary",
        "serialize_notification_badge",
        "serialize_notification_action",
        "serialize_notification_page_request",
        "serialize_notification_page_view",
        "serialize_notification_source",
        "serialize_notification_section",
        "serialize_notification_page_summary",
        "serialize_notification_composition",
        "serialize_notification_state",
        "serialize_notification_interaction_result",
        "serialize_notification_snapshot",

        # Validation
        "validate_notification_identity",
        "validate_notification_item",
        "validate_notification_summary",
        "validate_notification_badge",
        "validate_notification_action",
        "validate_notification_source",
        "validate_notification_page_view",
        "validate_notification_section",
        "validate_notification_page_summary",
        "validate_notification_composition",
        "validate_notification_page_state",
        "validate_notification_interaction_result",
        "validate_notification_snapshot",
        "validate_notification_authority",

        # Health
        "NotificationPageHealth",
        "build_notification_page_health",
        "serialize_notification_page_health",

        # Operational
        "notification_page_operational_check",
        "notification_page_summary",
        "create_default_notification_page",
        "notification_page_module_check",
    ]
)
# ============================================================================
# PART 5 — PAGE OPERATIONS, DIAGNOSTICS, CONTRACT & FINAL VALIDATION
# ============================================================================


def refresh_notification_page(
    controller: NotificationPageController,
    source: Optional[NotificationSourceState] = None,
) -> NotificationPageComposition:
    """
    Refresh notification presentation from upstream source.

    IMPORTANT:
    This does NOT fetch, send, mark-read, archive, persist, or mutate
    notification-domain data. The source must already be supplied by
    the upstream notification service/application layer.
    """

    if not isinstance(
        controller,
        NotificationPageController,
    ):
        raise TypeError(
            "controller must be NotificationPageController"
        )

    controller._state.refresh_count += 1
    controller._state.last_interaction = (
        NotificationInteraction.REFRESH
    )

    return controller.compose(source)


def get_notification_page(
    controller: NotificationPageController,
    source: Optional[NotificationSourceState] = None,
) -> NotificationPageComposition:
    """
    Return the current notification presentation.

    When no source is supplied, a safe degraded presentation is built.
    """

    if not isinstance(
        controller,
        NotificationPageController,
    ):
        raise TypeError(
            "controller must be NotificationPageController"
        )

    if source is not None:
        return controller.compose(source)

    if controller.last_composition is not None:
        return controller.last_composition

    return controller.compose(
        NotificationSourceState(
            identity=NotificationIdentityView(
                user_id=controller.state.user_id,
                authenticated=controller.state.authenticated,
            ),
            notifications=tuple(),
            source_available=False,
            source_errors=(
                "NOTIFICATION_SOURCE_NOT_CONNECTED",
            ),
        )
    )


# ============================================================================
# ROUTE ACCESS / SELECTION
# ============================================================================

def can_navigate_notification_page(
    controller: NotificationPageController,
    route: str,
) -> bool:
    """Check whether a notification route is presentation-accessible."""

    if not isinstance(
        controller,
        NotificationPageController,
    ):
        return False

    route = _notification_text(
        route,
        NOTIFICATION_ROUTE,
    )

    allowed, _ = evaluate_notification_route_access(
        route=route,
        authenticated=controller.state.authenticated,
        locked=controller.state.locked,
    )

    return allowed


def select_notification_route(
    controller: NotificationPageController,
    route: str,
) -> NotificationInteractionResult:
    """Select a notification presentation route."""

    if not isinstance(
        controller,
        NotificationPageController,
    ):
        raise TypeError(
            "controller must be NotificationPageController"
        )

    return controller.navigate(route)


# ============================================================================
# UI LOCK
# ============================================================================

def lock_notification_page(
    controller: NotificationPageController,
) -> None:
    """
    Lock notification presentation.

    This does NOT change authentication, security,
    notification persistence, or account state.
    """

    if not isinstance(
        controller,
        NotificationPageController,
    ):
        raise TypeError(
            "controller must be NotificationPageController"
        )

    controller.lock()


# ============================================================================
# DIAGNOSTICS
# ============================================================================

def diagnose_notification_page(
    controller: NotificationPageController,
    composition: Optional[
        NotificationPageComposition
    ] = None,
) -> Dict[str, Any]:
    """
    Produce a complete presentation-layer diagnostic report.
    """

    if not isinstance(
        controller,
        NotificationPageController,
    ):
        raise TypeError(
            "controller must be NotificationPageController"
        )

    state = controller.state

    if composition is None:
        composition = controller.last_composition

    state_errors = validate_notification_page_state(
        state
    )

    composition_errors: List[str] = []

    if composition is not None:
        composition_errors = (
            validate_notification_composition(
                composition
            )
        )

    authority_errors = validate_notification_authority(
        {
            **(
                composition.metadata
                if composition is not None
                else {}
            ),
            **(
                composition.page.metadata
                if composition is not None
                else {}
            ),
        }
    )

    health = build_notification_page_health(
        controller,
        composition,
    )

    return {
        "engine": NOTIFICATION_PAGE_ENGINE,
        "version": NOTIFICATION_PAGE_VERSION,
        "page": NOTIFICATION_PAGE_NAME,
        "route": NOTIFICATION_ROUTE,

        "state": serialize_notification_state(
            state
        ),

        "composition": (
            serialize_notification_composition(
                composition
            )
            if composition is not None
            else None
        ),

        "health": serialize_notification_page_health(
            health
        ),

        "state_errors": state_errors,
        "composition_errors": composition_errors,
        "authority_errors": authority_errors,

        "valid": not (
            state_errors
            or composition_errors
            or authority_errors
        ),

        "ui_only": True,

        "authority": {
            "notification_delivery": False,
            "notification_send": False,
            "notification_persistence": False,
            "notification_mutation": False,
            "notification_read_state_mutation": False,
            "intelligence_generation": False,
            "decision_generation": False,
            "d13_modification": False,
            "risk_generation": False,
            "cas_generation": False,
            "execution": False,
        },
    }


# ============================================================================
# ARCHITECTURE CONTRACT MANIFEST
# ============================================================================

def notification_page_contract_manifest() -> Dict[str, Any]:
    """
    Return the machine-readable architecture contract.

    This manifest defines the boundary of the notification UI.
    """

    return {
        "module": NOTIFICATION_PAGE_NAME,
        "engine": NOTIFICATION_PAGE_ENGINE,
        "version": NOTIFICATION_PAGE_VERSION,

        "layer": "UI_PRESENTATION",

        "responsibility": [
            "NOTIFICATION_PRESENTATION",
            "NOTIFICATION_STATUS_PRESENTATION",
            "NOTIFICATION_SUMMARY_PRESENTATION",
            "NOTIFICATION_NAVIGATION",
            "NOTIFICATION_FILTER_PRESENTATION",
            "NOTIFICATION_GROUPING_PRESENTATION",
        ],

        "input_flow": [
            "USER_SERVICE_OUTPUT",
            "NOTIFICATION_SERVICE_OUTPUT",
            "APPLICATION_SESSION_STATE",
        ],

        "processing": [
            "SOURCE_NORMALIZATION",
            "PRESENTATION_READINESS",
            "NOTIFICATION_SUMMARY",
            "SECTION_COMPOSITION",
            "VIEW_COMPOSITION",
            "SNAPSHOT",
            "VALIDATION",
            "DIAGNOSTICS",
        ],

        "outputs": [
            "NOTIFICATION_PAGE_VIEW",
            "NOTIFICATION_PAGE_COMPOSITION",
            "NOTIFICATION_PAGE_SNAPSHOT",
            "NOTIFICATION_PAGE_HEALTH",
            "NOTIFICATION_PAGE_DIAGNOSTICS",
        ],

        "authority_owners": {
            "authentication": "AUTHENTICATION_LAYER",
            "notification_delivery": (
                "NOTIFICATION_SERVICE"
            ),
            "notification_send": (
                "NOTIFICATION_SERVICE"
            ),
            "notification_persistence": (
                "NOTIFICATION_SERVICE"
            ),
            "notification_mutation": (
                "NOTIFICATION_SERVICE"
            ),
            "notification_read_state": (
                "NOTIFICATION_SERVICE"
            ),
            "notification_preferences": (
                "SETTINGS_PREFERENCE_SERVICE"
            ),
            "security": "SECURITY_LAYER",
            "billing": "BILLING_SERVICE",
            "subscription": "SUBSCRIBER_SERVICE",
            "entitlement": "ENTITLEMENT_SERVICE",
            "intelligence": "INTELLIGENCE_LAYER",
            "decision": "DECISION_CORTEX",
            "d13": "D13_DECISION_AUTHORITY",
            "risk": "RISK_LAYER",
            "cas": "CAS",
            "execution": "EXECUTION_LAYER",
        },

        "principles": [
            "PRESENTATION_ONLY",
            "UPSTREAM_TRUTH_PRESERVED",
            "NO_FAKE_NOTIFICATION_TRUTH",
            "NO_NOTIFICATION_DELIVERY",
            "NO_NOTIFICATION_SEND",
            "NO_NOTIFICATION_MUTATION",
            "NO_NOTIFICATION_PERSISTENCE",
            "NO_READ_STATE_MUTATION",
            "NO_NOTIFICATION_PREFERENCE_MUTATION",
            "NO_INTELLIGENCE_GENERATION",
            "NO_DECISION_GENERATION",
            "NO_D13_MUTATION",
            "NO_RISK_OVERRIDE",
            "NO_CAS_BYPASS",
            "NO_EXECUTION",
        ],

        "forbidden_authority": {
            key: value
            for key, value
            in NOTIFICATION_UI_AUTHORITY.items()
            if not value
        },
    }


# ============================================================================
# FINAL MODULE VALIDATION
# ============================================================================

def validate_notification_page_module() -> Dict[str, Any]:
    """
    Run complete static notification-page module validation.
    """

    module_check = notification_page_module_check()

    contract = notification_page_contract_manifest()

    authority_errors = validate_notification_authority(
        {
            "notification_delivery": False,
            "notification_send": False,
            "notification_persistence": False,
            "notification_mutation": False,
            "notification_read_state_mutation": False,
            "intelligence_generation": False,
            "decision_generation": False,
            "d13_modification": False,
            "risk_generation": False,
            "cas_generation": False,
            "execution": False,
            "upstream_mutation": False,
        }
    )

    errors = list(
        module_check.get("errors", [])
    )

    errors.extend(authority_errors)

    return {
        "engine": NOTIFICATION_PAGE_ENGINE,
        "version": NOTIFICATION_PAGE_VERSION,
        "module": NOTIFICATION_PAGE_NAME,

        "valid": not errors,

        "errors": errors,

        "module_check": module_check,

        "contract_valid": bool(
            contract.get("layer")
            == "UI_PRESENTATION"
        ),

        "authority_valid": not authority_errors,

        "ui_only": True,

        "notification_delivery": False,
        "notification_send": False,
        "notification_persistence": False,
        "notification_mutation": False,
        "notification_read_state_mutation": False,

        "intelligence_generation": False,
        "decision_generation": False,
        "d13_modification": False,
        "risk_generation": False,
        "cas_generation": False,
        "execution": False,
    }


# ============================================================================
# DEFAULT SNAPSHOT
# ============================================================================

def default_notification_page_snapshot() -> (
    NotificationPageSnapshot
):
    """
    Build the safe default notification snapshot.

    Default state is unauthenticated and source-disconnected.
    """

    controller = create_default_notification_page()

    source = NotificationSourceState(
        identity=NotificationIdentityView(
            user_id="",
            display_name="",
            email="",
            authenticated=False,
        ),
        notifications=tuple(),
        source_available=False,
        source_errors=(
            "DEFAULT_NOTIFICATION_SOURCE_NOT_CONNECTED",
        ),
        metadata={
            "default_snapshot": True,
        },
    )

    return build_notification_page_snapshot(
        controller,
        source,
    )


# ============================================================================
# EXTENDED EXPORTS
# ============================================================================

__all__.extend(
    [
        # Page operations
        "refresh_notification_page",
        "get_notification_page",

        # Navigation
        "can_navigate_notification_page",
        "select_notification_route",

        # UI state
        "lock_notification_page",

        # Diagnostics
        "diagnose_notification_page",

        # Architecture
        "notification_page_contract_manifest",
        "validate_notification_page_module",

        # Defaults
        "default_notification_page_snapshot",
    ]
)