"""
ROBOMLM_PLUS — Application Shell
================================

Premium desktop-style application shell for ROBOMLM.

Responsibilities
----------------
- Application identity and UI configuration
- Global visual/application constants
- Workspace/session presentation state
- Theme and display configuration contracts
- Application shell metadata
- Safe UI-level state normalization

Architecture Boundary
---------------------
This module is PRESENTATION ONLY.

It MUST NOT:
- generate market intelligence
- calculate evidence
- calculate decisions
- modify D13
- generate/override risk
- generate/override CAS
- execute orders
- mutate positions
- bypass upstream authority
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


# ============================================================================
# APPLICATION IDENTITY
# ============================================================================

APP_ENGINE = "ROBOMLM_PLUS_UI"
APP_VERSION = "1.0"

APP_NAME = "ROBOMLM"
APP_PRODUCT_NAME = "ROBOMLM Market Intelligence OS"
APP_PLUS_NAME = "ROBOMLM PLUS"

APP_TAGLINE = "See the Market. Understand the Market. Act with Intelligence."
APP_DESCRIPTION = (
    "A professional Market Intelligence Operating System built around "
    "evidence, context, decision intelligence, risk and controlled action."
)

APP_VENDOR = "ROBOMLM"
APP_BRAND = "ROBOMLM"

APP_DEFAULT_TITLE = "ROBOMLM — Market Intelligence OS"

APP_MIN_WIDTH = 1200
APP_MIN_HEIGHT = 760


# ============================================================================
# APPLICATION UI MODES
# ============================================================================

class AppMode(str, Enum):
    """High-level application operating mode."""

    PAPER = "PAPER"
    DEMO = "DEMO"
    LIVE = "LIVE"
    UNKNOWN = "UNKNOWN"


class AppTheme(str, Enum):
    """Supported application visual themes."""

    DARK = "DARK"
    LIGHT = "LIGHT"
    SYSTEM = "SYSTEM"


class AppDensity(str, Enum):
    """UI information density."""

    COMPACT = "COMPACT"
    COMFORTABLE = "COMFORTABLE"
    SPACIOUS = "SPACIOUS"


class AppStatus(str, Enum):
    """Presentation-level application status."""

    STARTING = "STARTING"
    READY = "READY"
    DEGRADED = "DEGRADED"
    LOCKED = "LOCKED"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class WorkspaceType(str, Enum):
    """Primary ROBOMLM workspace surfaces."""

    TERMINAL = "TERMINAL"
    DISCOVERY = "DISCOVERY"
    MEMORY = "MEMORY"
    RESEARCH = "RESEARCH"
    AUTOMATION = "AUTOMATION"
    ACCOUNT = "ACCOUNT"


class NavigationStyle(str, Enum):
    """Application navigation presentation."""

    SIDEBAR = "SIDEBAR"
    TOPBAR = "TOPBAR"
    HYBRID = "HYBRID"


class NotificationLevel(str, Enum):
    """UI notification severity."""

    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# ============================================================================
# APPLICATION AUTHORITY
# ============================================================================

APP_UI_AUTHORITY: Dict[str, bool] = {
    "application_shell_authority": True,
    "navigation_authority": True,
    "presentation_authority": True,
    "workspace_selection_authority": True,
    "display_configuration_authority": True,
    "session_presentation_authority": True,

    # Upstream intelligence authority
    "market_data_authority": False,
    "evidence_generation_authority": False,
    "market_context_generation_authority": False,
    "intelligence_generation_authority": False,
    "decision_generation_authority": False,

    # Decision authority
    "d13_authority": False,
    "d13_mutation": False,

    # Safety authority
    "risk_generation_authority": False,
    "risk_override": False,
    "cas_generation_authority": False,
    "cas_override": False,

    # Trading authority
    "execution_authority": False,
    "order_authority": False,
    "position_authority": False,

    # Account/security authority
    "authentication_authority": False,
    "credential_authority": False,
    "billing_authority": False,
    "subscription_authority": False,
    "entitlement_authority": False,

    # Upstream mutation
    "upstream_mutation_authority": False,
}


# ============================================================================
# UI BRANDING
# ============================================================================

@dataclass(frozen=True)
class AppBranding:
    """
    Immutable visual identity contract.

    Branding belongs to the application shell only. It does not carry
    intelligence or decision authority.
    """

    name: str = APP_NAME
    product_name: str = APP_PRODUCT_NAME
    plus_name: str = APP_PLUS_NAME
    tagline: str = APP_TAGLINE
    description: str = APP_DESCRIPTION
    vendor: str = APP_VENDOR
    brand: str = APP_BRAND

    primary_label: str = "ROBOMLM"
    secondary_label: str = "MARKET INTELLIGENCE OS"

    status_label: str = "INTELLIGENCE SYSTEM"
    terminal_label: str = "MARKET TERMINAL"


# ============================================================================
# DISPLAY CONFIGURATION
# ============================================================================

@dataclass
class AppDisplayConfig:
    """
    Global UI presentation configuration.

    This controls HOW information is displayed, not WHAT the information
    means.
    """

    theme: AppTheme = AppTheme.DARK
    density: AppDensity = AppDensity.COMFORTABLE
    navigation: NavigationStyle = NavigationStyle.HYBRID

    show_branding: bool = True
    show_system_status: bool = True
    show_market_status: bool = True
    show_workspace_switcher: bool = True
    show_notifications: bool = True
    show_chat: bool = True

    enable_animations: bool = True
    enable_transitions: bool = True
    enable_compact_cards: bool = False

    sidebar_collapsed: bool = False
    fullscreen: bool = False

    min_width: int = APP_MIN_WIDTH
    min_height: int = APP_MIN_HEIGHT

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# APPLICATION SESSION
# ============================================================================

@dataclass
class AppSession:
    """
    Presentation-level application session.

    This is NOT an authentication/session-security authority.
    """

    session_id: str = ""
    user_id: str = ""

    mode: AppMode = AppMode.UNKNOWN
    workspace: WorkspaceType = WorkspaceType.TERMINAL

    status: AppStatus = AppStatus.STARTING

    started_at: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None

    authenticated: bool = False
    workspace_ready: bool = False

    notification_count: int = 0
    unread_count: int = 0

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# NAVIGATION ITEM
# ============================================================================

@dataclass(frozen=True)
class NavigationItem:
    """
    UI navigation contract.

    Navigation items point to application surfaces. They do not contain
    business/intelligence decision logic.
    """

    key: str
    label: str
    description: str
    workspace: WorkspaceType

    icon: str = ""
    route: str = ""

    enabled: bool = True
    visible: bool = True
    requires_login: bool = True
    requires_plus: bool = False

    badge: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# DEFAULT NAVIGATION
# ============================================================================

DEFAULT_NAVIGATION: List[NavigationItem] = [
    NavigationItem(
        key="terminal",
        label="Terminal",
        description="Live market intelligence workspace",
        workspace=WorkspaceType.TERMINAL,
        icon="⌂",
        route="/terminal",
    ),
    NavigationItem(
        key="discovery",
        label="Discovery",
        description="Opportunity discovery and market scanners",
        workspace=WorkspaceType.DISCOVERY,
        icon="⌕",
        route="/discovery",
    ),
    NavigationItem(
        key="memory",
        label="Memory",
        description="Market memory and historical intelligence",
        workspace=WorkspaceType.MEMORY,
        icon="◈",
        route="/memory",
    ),
    NavigationItem(
        key="research",
        label="Research",
        description="Research laboratory and learning intelligence",
        workspace=WorkspaceType.RESEARCH,
        icon="⌘",
        route="/research",
    ),
    NavigationItem(
        key="automation",
        label="Automation",
        description="Controlled AUTOROBOMLM automation workspace",
        workspace=WorkspaceType.AUTOMATION,
        icon="⚙",
        route="/automation",
        requires_plus=True,
    ),
    NavigationItem(
        key="account",
        label="Account",
        description="Profile, billing and application settings",
        workspace=WorkspaceType.ACCOUNT,
        icon="◎",
        route="/account",
    ),
]


# ============================================================================
# APPLICATION NOTIFICATION
# ============================================================================

@dataclass(frozen=True)
class AppNotification:
    """Presentation-only notification."""

    notification_id: str
    title: str
    message: str

    level: NotificationLevel = NotificationLevel.INFO

    created_at: Optional[datetime] = None
    read: bool = False

    workspace: Optional[WorkspaceType] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# APPLICATION SNAPSHOT
# ============================================================================

@dataclass(frozen=True)
class AppSnapshot:
    """
    Immutable presentation snapshot consumed by the UI renderer.

    Upstream intelligence remains external to this contract.
    """

    engine: str
    version: str

    branding: AppBranding
    display: AppDisplayConfig
    session: AppSession

    navigation: List[NavigationItem] = field(default_factory=list)
    notifications: List[AppNotification] = field(default_factory=list)

    generated_at: Optional[datetime] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# BASIC HELPERS
# ============================================================================

def _app_now() -> datetime:
    """Return timezone-aware UTC timestamp."""

    return datetime.now(timezone.utc)


def _app_text(value: Any, default: str = "") -> str:
    """Safely normalize presentation text."""

    if value is None:
        return default

    text = str(value).strip()
    return text if text else default


def _app_bool(value: Any, default: bool = False) -> bool:
    """Safely normalize boolean presentation values."""

    if value is None:
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        normalized = value.strip().lower()

        if normalized in {"true", "1", "yes", "on", "enabled"}:
            return True

        if normalized in {"false", "0", "no", "off", "disabled"}:
            return False

    return bool(value)


def _app_enum(
    value: Any,
    enum_type: type[Enum],
    default: Enum,
) -> Enum:
    """Safely normalize enum-like presentation values."""

    if isinstance(value, enum_type):
        return value

    if value is None:
        return default

    try:
        return enum_type(str(value).strip().upper())
    except (ValueError, TypeError):
        return default


# ============================================================================
# CONFIGURATION NORMALIZATION
# ============================================================================

def normalize_app_display_config(
    config: Optional[AppDisplayConfig],
) -> AppDisplayConfig:
    """
    Normalize global display configuration.

    No business logic is performed here.
    """

    if config is None:
        return AppDisplayConfig()

    config.theme = _app_enum(
        config.theme,
        AppTheme,
        AppTheme.DARK,
    )

    config.density = _app_enum(
        config.density,
        AppDensity,
        AppDensity.COMFORTABLE,
    )

    config.navigation = _app_enum(
        config.navigation,
        NavigationStyle,
        NavigationStyle.HYBRID,
    )

    config.show_branding = _app_bool(config.show_branding, True)
    config.show_system_status = _app_bool(
        config.show_system_status,
        True,
    )
    config.show_market_status = _app_bool(
        config.show_market_status,
        True,
    )
    config.show_workspace_switcher = _app_bool(
        config.show_workspace_switcher,
        True,
    )
    config.show_notifications = _app_bool(
        config.show_notifications,
        True,
    )
    config.show_chat = _app_bool(
        config.show_chat,
        True,
    )

    config.enable_animations = _app_bool(
        config.enable_animations,
        True,
    )
    config.enable_transitions = _app_bool(
        config.enable_transitions,
        True,
    )

    config.min_width = max(
        int(config.min_width or APP_MIN_WIDTH),
        APP_MIN_WIDTH,
    )

    config.min_height = max(
        int(config.min_height or APP_MIN_HEIGHT),
        APP_MIN_HEIGHT,
    )

    if not isinstance(config.metadata, dict):
        config.metadata = {}

    return config


def normalize_app_session(
    session: Optional[AppSession],
) -> AppSession:
    """Normalize presentation session state."""

    if session is None:
        session = AppSession()

    session.session_id = _app_text(session.session_id)
    session.user_id = _app_text(session.user_id)

    session.mode = _app_enum(
        session.mode,
        AppMode,
        AppMode.UNKNOWN,
    )

    session.workspace = _app_enum(
        session.workspace,
        WorkspaceType,
        WorkspaceType.TERMINAL,
    )

    session.status = _app_enum(
        session.status,
        AppStatus,
        AppStatus.UNKNOWN,
    )

    session.authenticated = _app_bool(
        session.authenticated,
        False,
    )

    session.workspace_ready = _app_bool(
        session.workspace_ready,
        False,
    )

    session.notification_count = max(
        0,
        int(session.notification_count or 0),
    )

    session.unread_count = max(
        0,
        int(session.unread_count or 0),
    )

    if session.started_at is None:
        session.started_at = _app_now()

    if session.last_activity_at is None:
        session.last_activity_at = session.started_at

    if not isinstance(session.metadata, dict):
        session.metadata = {}

    return session
# ============================================================================
# WORKSPACE REGISTRY
# ============================================================================

@dataclass(frozen=True)
class WorkspaceDefinition:
    """
    Application workspace contract.

    A workspace is a UI surface. Intelligence and decision authority remain
    with their respective upstream services.
    """

    key: str
    label: str
    description: str

    workspace: WorkspaceType
    route: str
    icon: str = ""

    enabled: bool = True
    visible: bool = True
    requires_login: bool = True
    requires_plus: bool = False

    order: int = 0

    metadata: Dict[str, Any] = field(default_factory=dict)


DEFAULT_WORKSPACES: List[WorkspaceDefinition] = [
    WorkspaceDefinition(
        key="terminal",
        label="Terminal",
        description="Live market intelligence workspace",
        workspace=WorkspaceType.TERMINAL,
        route="/terminal",
        icon="⌂",
        order=1,
    ),
    WorkspaceDefinition(
        key="discovery",
        label="Discovery",
        description="Opportunity discovery and universal market scanning",
        workspace=WorkspaceType.DISCOVERY,
        route="/discovery",
        icon="⌕",
        order=2,
    ),
    WorkspaceDefinition(
        key="memory",
        label="Memory",
        description="Market memory and historical intelligence",
        workspace=WorkspaceType.MEMORY,
        route="/memory",
        icon="◈",
        order=3,
    ),
    WorkspaceDefinition(
        key="research",
        label="Research",
        description="Research laboratory and learning center",
        workspace=WorkspaceType.RESEARCH,
        route="/research",
        icon="⌘",
        order=4,
    ),
    WorkspaceDefinition(
        key="automation",
        label="Automation",
        description="Controlled AUTOROBOMLM automation workspace",
        workspace=WorkspaceType.AUTOMATION,
        route="/automation",
        icon="⚙",
        requires_plus=True,
        order=5,
    ),
    WorkspaceDefinition(
        key="account",
        label="Account",
        description="Profile, billing, notification and settings",
        workspace=WorkspaceType.ACCOUNT,
        route="/account",
        icon="◎",
        order=6,
    ),
]


def get_default_workspaces() -> List[WorkspaceDefinition]:
    """Return a safe copy of the default workspace definitions."""

    return list(DEFAULT_WORKSPACES)


def get_workspace_definition(
    workspace: Any,
) -> Optional[WorkspaceDefinition]:
    """Resolve a workspace definition by enum or key."""

    if isinstance(workspace, WorkspaceType):
        target = workspace
    else:
        try:
            target = WorkspaceType(
                str(workspace).strip().upper()
            )
        except (ValueError, TypeError):
            return None

    for item in DEFAULT_WORKSPACES:
        if item.workspace == target:
            return item

    return None


# ============================================================================
# NAVIGATION HELPERS
# ============================================================================

def get_navigation_items(
    *,
    authenticated: bool = False,
    plus_enabled: bool = False,
) -> List[NavigationItem]:
    """
    Return navigation items appropriate for the current presentation state.

    This function only controls visibility/access presentation. It does not
    grant business, trading, intelligence or execution authority.
    """

    result: List[NavigationItem] = []

    for item in DEFAULT_NAVIGATION:
        if not item.visible:
            continue

        if item.requires_login and not authenticated:
            continue

        if item.requires_plus and not plus_enabled:
            continue

        result.append(item)

    return result


def resolve_navigation_item(
    key: Any,
    *,
    authenticated: bool = False,
    plus_enabled: bool = False,
) -> Optional[NavigationItem]:
    """Resolve one navigation item under current UI visibility rules."""

    normalized = _app_text(key).lower()

    for item in get_navigation_items(
        authenticated=authenticated,
        plus_enabled=plus_enabled,
    ):
        if item.key.lower() == normalized:
            return item

    return None


def resolve_workspace_route(
    workspace: Any,
) -> str:
    """Resolve a workspace to its UI route."""

    definition = get_workspace_definition(workspace)

    if definition is None:
        return "/terminal"

    return definition.route


# ============================================================================
# APPLICATION STATE
# ============================================================================

@dataclass
class AppState:
    """
    Mutable presentation state for the application shell.

    AppState is deliberately isolated from business-domain authority.
    """

    branding: AppBranding = field(default_factory=AppBranding)
    display: AppDisplayConfig = field(
        default_factory=AppDisplayConfig
    )
    session: AppSession = field(
        default_factory=AppSession
    )

    notifications: List[AppNotification] = field(
        default_factory=list
    )

    plus_enabled: bool = False

    current_route: str = "/terminal"

    initialized: bool = False
    ready: bool = False

    metadata: Dict[str, Any] = field(default_factory=dict)


def create_app_state(
    *,
    mode: AppMode = AppMode.PAPER,
    workspace: WorkspaceType = WorkspaceType.TERMINAL,
    authenticated: bool = False,
    plus_enabled: bool = False,
) -> AppState:
    """
    Create the initial application presentation state.
    """

    session = AppSession(
        mode=_app_enum(
            mode,
            AppMode,
            AppMode.PAPER,
        ),
        workspace=_app_enum(
            workspace,
            WorkspaceType,
            WorkspaceType.TERMINAL,
        ),
        status=AppStatus.STARTING,
        authenticated=_app_bool(
            authenticated,
            False,
        ),
        workspace_ready=False,
        started_at=_app_now(),
        last_activity_at=_app_now(),
    )

    state = AppState(
        session=session,
        plus_enabled=_app_bool(
            plus_enabled,
            False,
        ),
        current_route=resolve_workspace_route(workspace),
        initialized=False,
        ready=False,
    )

    normalize_app_state(state)

    return state


# ============================================================================
# STATE NORMALIZATION
# ============================================================================

def normalize_app_state(
    state: Optional[AppState],
) -> AppState:
    """
    Normalize complete application presentation state.
    """

    if state is None:
        state = create_app_state()

    state.display = normalize_app_display_config(
        state.display
    )

    state.session = normalize_app_session(
        state.session
    )

    state.plus_enabled = _app_bool(
        state.plus_enabled,
        False,
    )

    state.current_route = _app_text(
        state.current_route,
        "/terminal",
    )

    if not state.current_route.startswith("/"):
        state.current_route = f"/{state.current_route}"

    if not isinstance(state.notifications, list):
        state.notifications = []

    if not isinstance(state.metadata, dict):
        state.metadata = {}

    return state


# ============================================================================
# WORKSPACE SELECTION
# ============================================================================

def select_workspace(
    state: AppState,
    workspace: Any,
) -> bool:
    """
    Select a UI workspace.

    Returns False when the requested workspace is unavailable to the current
    presentation state.
    """

    normalize_app_state(state)

    definition = get_workspace_definition(workspace)

    if definition is None:
        return False

    if not definition.visible or not definition.enabled:
        return False

    if definition.requires_login and not state.session.authenticated:
        return False

    if definition.requires_plus and not state.plus_enabled:
        return False

    state.session.workspace = definition.workspace
    state.session.workspace_ready = True
    state.current_route = definition.route
    state.session.last_activity_at = _app_now()

    return True


def select_route(
    state: AppState,
    route: Any,
) -> bool:
    """
    Select a UI route.

    Route selection remains presentation-only.
    """

    normalize_app_state(state)

    normalized_route = _app_text(route)

    if not normalized_route:
        return False

    if not normalized_route.startswith("/"):
        normalized_route = f"/{normalized_route}"

    for item in get_navigation_items(
        authenticated=state.session.authenticated,
        plus_enabled=state.plus_enabled,
    ):
        if item.route == normalized_route:
            state.current_route = normalized_route
            state.session.workspace = item.workspace
            state.session.workspace_ready = True
            state.session.last_activity_at = _app_now()
            return True

    return False


# ============================================================================
# APPLICATION STATUS
# ============================================================================

def set_app_status(
    state: AppState,
    status: Any,
) -> AppStatus:
    """Set presentation-level application status."""

    normalize_app_state(state)

    state.session.status = _app_enum(
        status,
        AppStatus,
        AppStatus.UNKNOWN,
    )

    state.session.last_activity_at = _app_now()

    return state.session.status


def initialize_app_state(
    state: AppState,
) -> AppState:
    """
    Mark the application shell as initialized and ready.

    Readiness here means UI shell readiness only.
    It does NOT mean that market intelligence, trading, risk or execution
    systems are ready.
    """

    normalize_app_state(state)

    state.initialized = True
    state.ready = True

    state.session.status = AppStatus.READY
    state.session.workspace_ready = True
    state.session.last_activity_at = _app_now()

    return state


# ============================================================================
# NOTIFICATION MANAGEMENT
# ============================================================================

def add_app_notification(
    state: AppState,
    notification: AppNotification,
) -> AppNotification:
    """Add a presentation notification."""

    normalize_app_state(state)

    if not isinstance(notification, AppNotification):
        raise TypeError(
            "notification must be an AppNotification"
        )

    state.notifications.append(notification)

    state.session.notification_count = len(
        state.notifications
    )

    state.session.unread_count = sum(
        1
        for item in state.notifications
        if not item.read
    )

    state.session.last_activity_at = _app_now()

    return notification


def mark_notifications_read(
    state: AppState,
) -> None:
    """Mark all application notifications as read."""

    normalize_app_state(state)

    state.notifications = [
        AppNotification(
            notification_id=item.notification_id,
            title=item.title,
            message=item.message,
            level=item.level,
            created_at=item.created_at,
            read=True,
            workspace=item.workspace,
            metadata=dict(item.metadata),
        )
        for item in state.notifications
    ]

    state.session.unread_count = 0


# ============================================================================
# SNAPSHOT CONSTRUCTION
# ============================================================================

def build_app_snapshot(
    state: Optional[AppState] = None,
) -> AppSnapshot:
    """
    Build an immutable presentation snapshot.

    The snapshot contains only application/UI state and references to
    upstream information. It does not calculate intelligence or decisions.
    """

    state = normalize_app_state(state)

    navigation = get_navigation_items(
        authenticated=state.session.authenticated,
        plus_enabled=state.plus_enabled,
    )

    return AppSnapshot(
        engine=APP_ENGINE,
        version=APP_VERSION,
        branding=state.branding,
        display=state.display,
        session=state.session,
        navigation=navigation,
        notifications=list(state.notifications),
        generated_at=_app_now(),
        metadata={
            **state.metadata,
            "plus_enabled": state.plus_enabled,
            "current_route": state.current_route,
            "ui_only": True,
            "d13_mutation": False,
            "risk_override": False,
            "cas_override": False,
            "execution_authority": False,
        },
    )
# ============================================================================
# ROUTE CONTRACT
# ============================================================================

@dataclass(frozen=True)
class AppRoute:
    """
    Immutable application route contract.

    A route identifies a UI destination only. It carries no intelligence
    or execution authority.
    """

    key: str
    path: str
    label: str
    workspace: WorkspaceType

    icon: str = ""
    description: str = ""

    requires_login: bool = True
    requires_plus: bool = False

    enabled: bool = True
    visible: bool = True

    metadata: Dict[str, Any] = field(default_factory=dict)


DEFAULT_ROUTES: List[AppRoute] = [
    AppRoute(
        key="terminal",
        path="/terminal",
        label="Terminal",
        workspace=WorkspaceType.TERMINAL,
        icon="⌂",
        description="Market intelligence terminal",
    ),
    AppRoute(
        key="discovery",
        path="/discovery",
        label="Discovery",
        workspace=WorkspaceType.DISCOVERY,
        icon="⌕",
        description="Opportunity discovery",
    ),
    AppRoute(
        key="memory",
        path="/memory",
        label="Memory",
        workspace=WorkspaceType.MEMORY,
        icon="◈",
        description="Market memory",
    ),
    AppRoute(
        key="research",
        path="/research",
        label="Research",
        workspace=WorkspaceType.RESEARCH,
        icon="⌘",
        description="Research laboratory",
    ),
    AppRoute(
        key="automation",
        path="/automation",
        label="Automation",
        workspace=WorkspaceType.AUTOMATION,
        icon="⚙",
        description="AUTOROBOMLM automation",
        requires_plus=True,
    ),
    AppRoute(
        key="account",
        path="/account",
        label="Account",
        workspace=WorkspaceType.ACCOUNT,
        icon="◎",
        description="Account and settings",
    ),
]


def get_routes() -> List[AppRoute]:
    """Return the registered application routes."""

    return list(DEFAULT_ROUTES)


def get_route(
    route: Any,
) -> Optional[AppRoute]:
    """Resolve an application route by path or key."""

    value = _app_text(route)

    if not value:
        return None

    for item in DEFAULT_ROUTES:
        if (
            item.path.lower() == value.lower()
            or item.key.lower() == value.lower()
        ):
            return item

    return None


# ============================================================================
# ROUTE ACCESS PRESENTATION
# ============================================================================

def can_access_route(
    state: AppState,
    route: Any,
) -> bool:
    """
    Determine whether a route may be presented to the current UI session.

    This is a presentation/access check only. It does not replace security,
    authentication, subscription or entitlement services.
    """

    normalize_app_state(state)

    definition = get_route(route)

    if definition is None:
        return False

    if not definition.enabled or not definition.visible:
        return False

    if definition.requires_login and not state.session.authenticated:
        return False

    if definition.requires_plus and not state.plus_enabled:
        return False

    return True


# ============================================================================
# APPLICATION LIFECYCLE
# ============================================================================

class AppLifecycleEvent(str, Enum):
    """Application shell lifecycle events."""

    CREATED = "CREATED"
    INITIALIZED = "INITIALIZED"
    READY = "READY"
    ROUTE_CHANGED = "ROUTE_CHANGED"
    WORKSPACE_CHANGED = "WORKSPACE_CHANGED"
    SUSPENDED = "SUSPENDED"
    RESUMED = "RESUMED"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    ERROR = "ERROR"


@dataclass(frozen=True)
class AppLifecycleRecord:
    """Immutable lifecycle event record."""

    event: AppLifecycleEvent
    timestamp: datetime

    route: str = ""
    workspace: WorkspaceType = WorkspaceType.TERMINAL

    status: AppStatus = AppStatus.UNKNOWN

    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


def create_lifecycle_record(
    state: AppState,
    event: AppLifecycleEvent,
    message: str = "",
) -> AppLifecycleRecord:
    """Create a lifecycle record from current UI state."""

    normalize_app_state(state)

    return AppLifecycleRecord(
        event=_app_enum(
            event,
            AppLifecycleEvent,
            AppLifecycleEvent.ERROR,
        ),
        timestamp=_app_now(),
        route=state.current_route,
        workspace=state.session.workspace,
        status=state.session.status,
        message=_app_text(message),
        metadata={
            "ui_only": True,
            "d13_mutation": False,
            "risk_override": False,
            "cas_override": False,
            "execution_authority": False,
        },
    )


# ============================================================================
# APPLICATION SHELL CONTROLLER
# ============================================================================

class AppShell:
    """
    Professional application-shell controller.

    The shell coordinates presentation state, routing and workspace
    navigation. It does not own business-domain authority.
    """

    def __init__(
        self,
        state: Optional[AppState] = None,
    ) -> None:
        self.state = normalize_app_state(
            state or create_app_state()
        )

        self._lifecycle: List[AppLifecycleRecord] = []

        self._record(
            AppLifecycleEvent.CREATED,
            "Application shell created",
        )

    # ------------------------------------------------------------------
    # Internal lifecycle
    # ------------------------------------------------------------------

    def _record(
        self,
        event: AppLifecycleEvent,
        message: str = "",
    ) -> AppLifecycleRecord:
        record = create_lifecycle_record(
            self.state,
            event,
            message,
        )

        self._lifecycle.append(record)

        # Keep the presentation lifecycle lightweight.
        if len(self._lifecycle) > 100:
            self._lifecycle = self._lifecycle[-100:]

        return record

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def state_snapshot(self) -> AppState:
        """Return current normalized presentation state."""

        return normalize_app_state(self.state)

    @property
    def current_route(self) -> str:
        return self.state.current_route

    @property
    def current_workspace(self) -> WorkspaceType:
        return self.state.session.workspace

    @property
    def status(self) -> AppStatus:
        return self.state.session.status

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def initialize(self) -> AppSnapshot:
        """Initialize the UI shell."""

        initialize_app_state(self.state)

        self._record(
            AppLifecycleEvent.INITIALIZED,
            "Application shell initialized",
        )

        self._record(
            AppLifecycleEvent.READY,
            "Application shell ready",
        )

        return self.snapshot()

    def suspend(self) -> AppSnapshot:
        """Suspend presentation activity."""

        set_app_status(
            self.state,
            AppStatus.LOCKED,
        )

        self._record(
            AppLifecycleEvent.SUSPENDED,
            "Application shell suspended",
        )

        return self.snapshot()

    def resume(self) -> AppSnapshot:
        """Resume presentation activity."""

        set_app_status(
            self.state,
            AppStatus.READY,
        )

        self._record(
            AppLifecycleEvent.RESUMED,
            "Application shell resumed",
        )

        return self.snapshot()

    def stop(self) -> AppSnapshot:
        """Stop the application shell."""

        set_app_status(
            self.state,
            AppStatus.STOPPING,
        )

        self._record(
            AppLifecycleEvent.STOPPING,
            "Application shell stopping",
        )

        set_app_status(
            self.state,
            AppStatus.STOPPED,
        )

        self.state.ready = False

        self._record(
            AppLifecycleEvent.STOPPED,
            "Application shell stopped",
        )

        return self.snapshot()

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def navigate(
        self,
        route: Any,
    ) -> bool:
        """Navigate to an accessible application route."""

        if not can_access_route(
            self.state,
            route,
        ):
            return False

        definition = get_route(route)

        if definition is None:
            return False

        previous_route = self.state.current_route

        self.state.current_route = definition.path
        self.state.session.workspace = definition.workspace
        self.state.session.workspace_ready = True
        self.state.session.last_activity_at = _app_now()

        self._record(
            AppLifecycleEvent.ROUTE_CHANGED,
            f"Route changed: {previous_route} → {definition.path}",
        )

        self._record(
            AppLifecycleEvent.WORKSPACE_CHANGED,
            f"Workspace changed to {definition.workspace.value}",
        )

        return True

    def navigate_workspace(
        self,
        workspace: Any,
    ) -> bool:
        """Navigate directly to a workspace."""

        definition = get_workspace_definition(workspace)

        if definition is None:
            return False

        return self.navigate(definition.route)

    # ------------------------------------------------------------------
    # Session presentation
    # ------------------------------------------------------------------

    def set_authenticated(
        self,
        authenticated: bool,
    ) -> None:
        """
        Update presentation authentication state.

        Actual authentication remains external to the UI shell.
        """

        self.state.session.authenticated = _app_bool(
            authenticated,
            False,
        )

        self.state.session.last_activity_at = _app_now()

        # Prevent an inaccessible route from remaining selected.
        if not can_access_route(
            self.state,
            self.state.current_route,
        ):
            self.state.current_route = "/terminal"
            self.state.session.workspace = WorkspaceType.TERMINAL

    def set_plus_visibility(
        self,
        enabled: bool,
    ) -> None:
        """
        Update PLUS presentation visibility.

        Actual entitlement authority remains external.
        """

        self.state.plus_enabled = _app_bool(
            enabled,
            False,
        )

        self.state.session.last_activity_at = _app_now()

        if (
            not self.state.plus_enabled
            and self.state.session.workspace
            == WorkspaceType.AUTOMATION
        ):
            self.navigate("/terminal")

    # ------------------------------------------------------------------
    # Notifications
    # ------------------------------------------------------------------

    def notify(
        self,
        title: str,
        message: str,
        *,
        level: NotificationLevel = NotificationLevel.INFO,
        workspace: Optional[WorkspaceType] = None,
        notification_id: str = "",
    ) -> AppNotification:
        """Create and register a UI notification."""

        notification = AppNotification(
            notification_id=_app_text(
                notification_id,
                f"ui-{int(_app_now().timestamp() * 1000)}",
            ),
            title=_app_text(title, "ROBOMLM"),
            message=_app_text(message),
            level=_app_enum(
                level,
                NotificationLevel,
                NotificationLevel.INFO,
            ),
            created_at=_app_now(),
            read=False,
            workspace=workspace,
        )

        return add_app_notification(
            self.state,
            notification,
        )

    # ------------------------------------------------------------------
    # Snapshot
    # ------------------------------------------------------------------

    def snapshot(self) -> AppSnapshot:
        """Return the current immutable application snapshot."""

        return build_app_snapshot(self.state)

    def lifecycle(self) -> List[AppLifecycleRecord]:
        """Return a copy of recent lifecycle records."""

        return list(self._lifecycle)


# ============================================================================
# GLOBAL APPLICATION SHELL
# ============================================================================

_DEFAULT_APP_SHELL: Optional[AppShell] = None


def get_app_shell() -> AppShell:
    """
    Return the process-level application shell.

    The shell contains presentation state only.
    """

    global _DEFAULT_APP_SHELL

    if _DEFAULT_APP_SHELL is None:
        _DEFAULT_APP_SHELL = AppShell()

    return _DEFAULT_APP_SHELL


def create_application_shell(
    *,
    mode: AppMode = AppMode.PAPER,
    workspace: WorkspaceType = WorkspaceType.TERMINAL,
    authenticated: bool = False,
    plus_enabled: bool = False,
) -> AppShell:
    """Create an independent application shell."""

    state = create_app_state(
        mode=mode,
        workspace=workspace,
        authenticated=authenticated,
        plus_enabled=plus_enabled,
    )

    return AppShell(state)


# ============================================================================
# PRESENTATION VIEW MODEL
# ============================================================================

@dataclass(frozen=True)
class AppViewModel:
    """
    Renderer-facing application view model.

    This is intentionally presentation-focused.
    """

    title: str
    brand: str
    product: str

    route: str
    workspace: WorkspaceType
    mode: AppMode
    status: AppStatus

    authenticated: bool
    plus_enabled: bool

    navigation: List[NavigationItem]
    notifications: List[AppNotification]

    sidebar_collapsed: bool
    fullscreen: bool

    show_chat: bool
    show_notifications: bool
    show_system_status: bool
    show_market_status: bool

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def build_app_view_model(
    snapshot: Optional[AppSnapshot] = None,
) -> AppViewModel:
    """
    Convert an application snapshot into a renderer-facing view model.
    """

    if snapshot is None:
        snapshot = get_app_shell().snapshot()

    return AppViewModel(
        title=APP_DEFAULT_TITLE,
        brand=snapshot.branding.brand,
        product=snapshot.branding.product_name,

        route=snapshot.session.metadata.get(
            "current_route",
            "/terminal",
        ),
        workspace=snapshot.session.workspace,
        mode=snapshot.session.mode,
        status=snapshot.session.status,

        authenticated=snapshot.session.authenticated,
        plus_enabled=bool(
            snapshot.metadata.get(
                "plus_enabled",
                False,
            )
        ),

        navigation=list(snapshot.navigation),
        notifications=list(snapshot.notifications),

        sidebar_collapsed=snapshot.display.sidebar_collapsed,
        fullscreen=snapshot.display.fullscreen,

        show_chat=snapshot.display.show_chat,
        show_notifications=snapshot.display.show_notifications,
        show_system_status=snapshot.display.show_system_status,
        show_market_status=snapshot.display.show_market_status,

        metadata={
            "engine": snapshot.engine,
            "version": snapshot.version,
            "ui_only": True,
            "intelligence_authority": False,
            "d13_authority": False,
            "risk_override": False,
            "cas_override": False,
            "execution_authority": False,
        },
    )
# ============================================================================
# APPLICATION HEADER
# ============================================================================

@dataclass(frozen=True)
class AppHeader:
    """Professional application header presentation contract."""

    brand: str
    product_label: str
    workspace_label: str

    mode: AppMode
    status: AppStatus

    user_label: str = ""
    plus_label: str = ""

    show_branding: bool = True
    show_mode: bool = True
    show_status: bool = True
    show_user: bool = True
    show_plus: bool = False

    metadata: Dict[str, Any] = field(default_factory=dict)


def build_app_header(
    snapshot: AppSnapshot,
) -> AppHeader:
    """Build the application header from the current UI snapshot."""

    workspace = get_workspace_definition(
        snapshot.session.workspace
    )

    workspace_label = (
        workspace.label
        if workspace is not None
        else "Terminal"
    )

    user_label = snapshot.session.user_id

    plus_enabled = bool(
        snapshot.metadata.get(
            "plus_enabled",
            False,
        )
    )

    return AppHeader(
        brand=snapshot.branding.brand,
        product_label=snapshot.branding.secondary_label,
        workspace_label=workspace_label,
        mode=snapshot.session.mode,
        status=snapshot.session.status,
        user_label=user_label,
        plus_label=(
            "ROBOMLM PLUS"
            if plus_enabled
            else ""
        ),
        show_branding=snapshot.display.show_branding,
        show_mode=True,
        show_status=snapshot.display.show_system_status,
        show_user=True,
        show_plus=plus_enabled,
    )


# ============================================================================
# SIDEBAR PRESENTATION
# ============================================================================

@dataclass(frozen=True)
class AppSidebar:
    """Desktop-style navigation sidebar contract."""

    expanded: bool
    items: List[NavigationItem]

    active_route: str
    active_workspace: WorkspaceType

    title: str = "WORKSPACE"
    footer_label: str = "ROBOMLM"

    metadata: Dict[str, Any] = field(default_factory=dict)


def build_app_sidebar(
    snapshot: AppSnapshot,
) -> AppSidebar:
    """Build sidebar presentation state."""

    return AppSidebar(
        expanded=not snapshot.display.sidebar_collapsed,
        items=list(snapshot.navigation),
        active_route=snapshot.session.metadata.get(
            "current_route",
            "/terminal",
        ),
        active_workspace=snapshot.session.workspace,
        metadata={
            "navigation_style": snapshot.display.navigation.value,
            "ui_only": True,
        },
    )


# ============================================================================
# STATUS BAR
# ============================================================================

@dataclass(frozen=True)
class AppStatusBar:
    """Bottom status-bar presentation contract."""

    application_status: AppStatus
    mode: AppMode
    workspace: WorkspaceType

    notification_count: int
    unread_count: int

    system_label: str = "ROBOMLM SYSTEM"
    intelligence_label: str = "INTELLIGENCE ONLINE"
    authority_label: str = "UI PRESENTATION LAYER"

    show_system: bool = True
    show_market: bool = True

    metadata: Dict[str, Any] = field(default_factory=dict)


def build_app_status_bar(
    snapshot: AppSnapshot,
) -> AppStatusBar:
    """
    Build status-bar state.

    The intelligence label is a presentation label only. It does not assert
    or calculate upstream engine health.
    """

    return AppStatusBar(
        application_status=snapshot.session.status,
        mode=snapshot.session.mode,
        workspace=snapshot.session.workspace,
        notification_count=snapshot.session.notification_count,
        unread_count=snapshot.session.unread_count,
        show_system=snapshot.display.show_system_status,
        show_market=snapshot.display.show_market_status,
        metadata={
            "d13_mutation": False,
            "risk_override": False,
            "cas_override": False,
            "execution_authority": False,
        },
    )


# ============================================================================
# WORKSPACE HEADER
# ============================================================================

@dataclass(frozen=True)
class WorkspaceHeader:
    """Header displayed at the top of each workspace."""

    key: str
    title: str
    description: str

    route: str
    workspace: WorkspaceType

    icon: str = ""

    mode: AppMode = AppMode.UNKNOWN
    status: AppStatus = AppStatus.UNKNOWN

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def build_workspace_header(
    snapshot: AppSnapshot,
) -> WorkspaceHeader:
    """Build the active workspace header."""

    definition = get_workspace_definition(
        snapshot.session.workspace
    )

    if definition is None:
        return WorkspaceHeader(
            key="terminal",
            title="Terminal",
            description="Market intelligence terminal",
            route="/terminal",
            workspace=WorkspaceType.TERMINAL,
            icon="⌂",
            mode=snapshot.session.mode,
            status=snapshot.session.status,
        )

    return WorkspaceHeader(
        key=definition.key,
        title=definition.label,
        description=definition.description,
        route=definition.route,
        workspace=definition.workspace,
        icon=definition.icon,
        mode=snapshot.session.mode,
        status=snapshot.session.status,
        metadata=dict(definition.metadata),
    )


# ============================================================================
# QUICK ACTIONS
# ============================================================================

class AppAction(str, Enum):
    """Application-level presentation actions."""

    OPEN_TERMINAL = "OPEN_TERMINAL"
    OPEN_DISCOVERY = "OPEN_DISCOVERY"
    OPEN_MEMORY = "OPEN_MEMORY"
    OPEN_RESEARCH = "OPEN_RESEARCH"
    OPEN_AUTOMATION = "OPEN_AUTOMATION"
    OPEN_ACCOUNT = "OPEN_ACCOUNT"

    TOGGLE_SIDEBAR = "TOGGLE_SIDEBAR"
    TOGGLE_FULLSCREEN = "TOGGLE_FULLSCREEN"

    OPEN_NOTIFICATIONS = "OPEN_NOTIFICATIONS"
    OPEN_CHAT = "OPEN_CHAT"

    REFRESH_VIEW = "REFRESH_VIEW"
    LOCK_UI = "LOCK_UI"


@dataclass(frozen=True)
class AppActionItem:
    """Renderer-ready application action."""

    action: AppAction
    label: str
    description: str

    icon: str = ""

    enabled: bool = True
    visible: bool = True

    route: Optional[str] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


DEFAULT_ACTIONS: List[AppActionItem] = [
    AppActionItem(
        action=AppAction.OPEN_TERMINAL,
        label="Terminal",
        description="Open market intelligence terminal",
        icon="⌂",
        route="/terminal",
    ),
    AppActionItem(
        action=AppAction.OPEN_DISCOVERY,
        label="Discovery",
        description="Open opportunity discovery",
        icon="⌕",
        route="/discovery",
    ),
    AppActionItem(
        action=AppAction.OPEN_MEMORY,
        label="Memory",
        description="Open market memory",
        icon="◈",
        route="/memory",
    ),
    AppActionItem(
        action=AppAction.OPEN_RESEARCH,
        label="Research",
        description="Open research laboratory",
        icon="⌘",
        route="/research",
    ),
    AppActionItem(
        action=AppAction.OPEN_AUTOMATION,
        label="Automation",
        description="Open AUTOROBOMLM workspace",
        icon="⚙",
        route="/automation",
        metadata={
            "requires_plus": True,
        },
    ),
    AppActionItem(
        action=AppAction.OPEN_ACCOUNT,
        label="Account",
        description="Open account workspace",
        icon="◎",
        route="/account",
    ),
]


def get_app_actions(
    state: AppState,
) -> List[AppActionItem]:
    """Return actions visible to the current application state."""

    normalize_app_state(state)

    actions: List[AppActionItem] = []

    for item in DEFAULT_ACTIONS:
        requires_plus = bool(
            item.metadata.get(
                "requires_plus",
                False,
            )
        )

        if requires_plus and not state.plus_enabled:
            continue

        if item.route is not None:
            if not can_access_route(
                state,
                item.route,
            ):
                continue

        actions.append(item)

    actions.extend(
        [
            AppActionItem(
                action=AppAction.TOGGLE_SIDEBAR,
                label="Toggle Sidebar",
                description="Expand or collapse navigation",
                icon="☰",
            ),
            AppActionItem(
                action=AppAction.TOGGLE_FULLSCREEN,
                label="Fullscreen",
                description="Toggle fullscreen presentation",
                icon="□",
            ),
            AppActionItem(
                action=AppAction.OPEN_NOTIFICATIONS,
                label="Notifications",
                description="Open system notifications",
                icon="●",
            ),
            AppActionItem(
                action=AppAction.OPEN_CHAT,
                label="ROBOMLM Chat",
                description="Open the floating intelligence assistant",
                icon="◌",
            ),
            AppActionItem(
                action=AppAction.REFRESH_VIEW,
                label="Refresh",
                description="Refresh current presentation",
                icon="↻",
            ),
            AppActionItem(
                action=AppAction.LOCK_UI,
                label="Lock",
                description="Lock the application presentation",
                icon="◇",
            ),
        ]
    )

    return actions


# ============================================================================
# ACTION EXECUTION
# ============================================================================

def execute_app_action(
    state: AppState,
    action: Any,
) -> bool:
    """
    Execute a presentation-level application action.

    No market, decision, risk, CAS or execution operation is performed here.
    """

    normalize_app_state(state)

    try:
        resolved = (
            action
            if isinstance(action, AppAction)
            else AppAction(
                str(action).strip().upper()
            )
        )
    except (ValueError, TypeError):
        return False

    route_actions = {
        AppAction.OPEN_TERMINAL: "/terminal",
        AppAction.OPEN_DISCOVERY: "/discovery",
        AppAction.OPEN_MEMORY: "/memory",
        AppAction.OPEN_RESEARCH: "/research",
        AppAction.OPEN_AUTOMATION: "/automation",
        AppAction.OPEN_ACCOUNT: "/account",
    }

    if resolved in route_actions:
        return select_route(
            state,
            route_actions[resolved],
        )

    if resolved == AppAction.TOGGLE_SIDEBAR:
        state.display.sidebar_collapsed = (
            not state.display.sidebar_collapsed
        )
        state.session.last_activity_at = _app_now()
        return True

    if resolved == AppAction.TOGGLE_FULLSCREEN:
        state.display.fullscreen = (
            not state.display.fullscreen
        )
        state.session.last_activity_at = _app_now()
        return True

    if resolved == AppAction.OPEN_NOTIFICATIONS:
        state.session.last_activity_at = _app_now()
        return True

    if resolved == AppAction.OPEN_CHAT:
        state.session.last_activity_at = _app_now()
        return True

    if resolved == AppAction.REFRESH_VIEW:
        state.session.last_activity_at = _app_now()
        return True

    if resolved == AppAction.LOCK_UI:
        set_app_status(
            state,
            AppStatus.LOCKED,
        )
        return True

    return False


# ============================================================================
# APPLICATION COMPOSITION
# ============================================================================

@dataclass(frozen=True)
class AppComposition:
    """
    Complete renderer composition for the application shell.

    This is the main UI composition contract used by the future renderer.
    """

    snapshot: AppSnapshot
    view_model: AppViewModel

    header: AppHeader
    sidebar: AppSidebar
    status_bar: AppStatusBar
    workspace_header: WorkspaceHeader

    actions: List[AppActionItem]

    branding: AppBranding
    display: AppDisplayConfig

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def compose_application(
    state: Optional[AppState] = None,
) -> AppComposition:
    """
    Compose the complete application shell.

    This function creates presentation objects only. It does not invoke or
    replace intelligence, D13, risk, CAS or execution authority.
    """

    if state is None:
        state = get_app_shell().state

    normalize_app_state(state)

    snapshot = build_app_snapshot(state)

    return AppComposition(
        snapshot=snapshot,
        view_model=build_app_view_model(snapshot),
        header=build_app_header(snapshot),
        sidebar=build_app_sidebar(snapshot),
        status_bar=build_app_status_bar(snapshot),
        workspace_header=build_workspace_header(snapshot),
        actions=get_app_actions(state),
        branding=snapshot.branding,
        display=snapshot.display,
        metadata={
            "engine": APP_ENGINE,
            "version": APP_VERSION,
            "presentation_only": True,
            "market_intelligence_generation": False,
            "decision_generation": False,
            "d13_mutation": False,
            "risk_generation": False,
            "risk_override": False,
            "cas_generation": False,
            "cas_override": False,
            "execution_authority": False,
        },
    )


# ============================================================================
# UI ERROR PRESENTATION
# ============================================================================

@dataclass(frozen=True)
class AppErrorView:
    """Safe UI representation of an application error."""

    title: str
    message: str

    severity: NotificationLevel = NotificationLevel.ERROR

    retry_available: bool = False
    technical_detail: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def build_app_error_view(
    error: Exception,
    *,
    retry_available: bool = False,
) -> AppErrorView:
    """
    Convert an exception into a controlled presentation object.

    Raw exception details are kept separate from user-facing messaging.
    """

    if error is None:
        return AppErrorView(
            title="Application Error",
            message="An unknown application error occurred.",
            retry_available=retry_available,
        )

    return AppErrorView(
        title="Application Error",
        message=(
            "ROBOMLM could not complete the requested UI operation."
        ),
        severity=NotificationLevel.ERROR,
        retry_available=retry_available,
        technical_detail=f"{type(error).__name__}: {error}",
        metadata={
            "ui_only": True,
            "upstream_mutation": False,
        },
    )


# ============================================================================
# APPLICATION HEALTH PRESENTATION
# ============================================================================

@dataclass(frozen=True)
class AppHealthView:
    """
    Presentation-level application health.

    This does not replace Data Health, Evidence Health, Decision Health,
    Risk Health or CAS Health.
    """

    application_status: AppStatus

    initialized: bool
    ready: bool

    current_route: str
    workspace: WorkspaceType
    mode: AppMode

    navigation_available: int
    notification_count: int

    ui_operational: bool

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def build_app_health_view(
    state: Optional[AppState] = None,
) -> AppHealthView:
    """Build presentation-layer health state."""

    if state is None:
        state = get_app_shell().state

    normalize_app_state(state)

    navigation_count = len(
        get_navigation_items(
            authenticated=state.session.authenticated,
            plus_enabled=state.plus_enabled,
        )
    )

    return AppHealthView(
        application_status=state.session.status,
        initialized=state.initialized,
        ready=state.ready,
        current_route=state.current_route,
        workspace=state.session.workspace,
        mode=state.session.mode,
        navigation_available=navigation_count,
        notification_count=len(
            state.notifications
        ),
        ui_operational=(
            state.initialized
            and state.session.status
            not in {
                AppStatus.ERROR,
                AppStatus.STOPPED,
            }
        ),
        metadata={
            "health_scope": "UI_APPLICATION_SHELL",
            "not_market_health": True,
            "not_decision_health": True,
            "not_risk_health": True,
            "not_cas_health": True,
        },
    )
# ============================================================================
# SERIALIZATION HELPERS
# ============================================================================

def _serialize_app_value(value: Any) -> Any:
    """Convert application objects into safe serializable values."""

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            str(key): _serialize_app_value(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            _serialize_app_value(item)
            for item in value
        ]

    if hasattr(value, "__dataclass_fields__"):
        return {
            field_name: _serialize_app_value(
                getattr(value, field_name)
            )
            for field_name in value.__dataclass_fields__
        }

    return value


def serialize_app_branding(
    branding: AppBranding,
) -> Dict[str, Any]:
    return _serialize_app_value(branding)


def serialize_app_display_config(
    config: AppDisplayConfig,
) -> Dict[str, Any]:
    return _serialize_app_value(config)


def serialize_app_session(
    session: AppSession,
) -> Dict[str, Any]:
    return _serialize_app_value(session)


def serialize_navigation_item(
    item: NavigationItem,
) -> Dict[str, Any]:
    return _serialize_app_value(item)


def serialize_workspace_definition(
    item: WorkspaceDefinition,
) -> Dict[str, Any]:
    return _serialize_app_value(item)


def serialize_app_notification(
    notification: AppNotification,
) -> Dict[str, Any]:
    return _serialize_app_value(notification)


def serialize_app_snapshot(
    snapshot: AppSnapshot,
) -> Dict[str, Any]:
    return _serialize_app_value(snapshot)


def serialize_app_view_model(
    view_model: AppViewModel,
) -> Dict[str, Any]:
    return _serialize_app_value(view_model)


def serialize_app_composition(
    composition: AppComposition,
) -> Dict[str, Any]:
    return _serialize_app_value(composition)


def serialize_app_health_view(
    health: AppHealthView,
) -> Dict[str, Any]:
    return _serialize_app_value(health)


def serialize_app_error_view(
    error_view: AppErrorView,
) -> Dict[str, Any]:
    return _serialize_app_value(error_view)


# ============================================================================
# INTEGRITY VALIDATION
# ============================================================================

def validate_app_authority() -> bool:
    """
    Validate that the application shell does not claim prohibited authority.
    """

    prohibited = {
        "market_data_authority",
        "evidence_generation_authority",
        "market_context_generation_authority",
        "intelligence_generation_authority",
        "decision_generation_authority",
        "d13_authority",
        "d13_mutation",
        "risk_generation_authority",
        "risk_override",
        "cas_generation_authority",
        "cas_override",
        "execution_authority",
        "order_authority",
        "position_authority",
        "authentication_authority",
        "credential_authority",
        "billing_authority",
        "subscription_authority",
        "entitlement_authority",
        "upstream_mutation_authority",
    }

    return all(
        APP_UI_AUTHORITY.get(key) is False
        for key in prohibited
    )


def validate_app_state_integrity(
    state: Optional[AppState],
) -> bool:
    """
    Validate basic application-state integrity.

    This checks UI structure only and does not validate upstream domain
    intelligence.
    """

    if state is None:
        return False

    try:
        normalize_app_state(state)

        if not isinstance(
            state.branding,
            AppBranding,
        ):
            return False

        if not isinstance(
            state.display,
            AppDisplayConfig,
        ):
            return False

        if not isinstance(
            state.session,
            AppSession,
        ):
            return False

        if not isinstance(
            state.notifications,
            list,
        ):
            return False

        if not isinstance(
            state.metadata,
            dict,
        ):
            return False

        if not state.current_route.startswith("/"):
            return False

        if state.session.notification_count != len(
            state.notifications
        ):
            return False

        unread = sum(
            1
            for item in state.notifications
            if isinstance(item, AppNotification)
            and not item.read
        )

        if state.session.unread_count != unread:
            return False

        return True

    except (TypeError, ValueError, AttributeError):
        return False


def validate_app_snapshot_integrity(
    snapshot: Optional[AppSnapshot],
) -> bool:
    """Validate an immutable application snapshot."""

    if snapshot is None:
        return False

    try:
        if snapshot.engine != APP_ENGINE:
            return False

        if snapshot.version != APP_VERSION:
            return False

        if not isinstance(
            snapshot.branding,
            AppBranding,
        ):
            return False

        if not isinstance(
            snapshot.display,
            AppDisplayConfig,
        ):
            return False

        if not isinstance(
            snapshot.session,
            AppSession,
        ):
            return False

        if not isinstance(
            snapshot.navigation,
            list,
        ):
            return False

        if not isinstance(
            snapshot.notifications,
            list,
        ):
            return False

        return True

    except (TypeError, ValueError, AttributeError):
        return False


def validate_app_composition_integrity(
    composition: Optional[AppComposition],
) -> bool:
    """Validate the complete UI composition."""

    if composition is None:
        return False

    try:
        return (
            validate_app_snapshot_integrity(
                composition.snapshot
            )
            and isinstance(
                composition.view_model,
                AppViewModel,
            )
            and isinstance(
                composition.header,
                AppHeader,
            )
            and isinstance(
                composition.sidebar,
                AppSidebar,
            )
            and isinstance(
                composition.status_bar,
                AppStatusBar,
            )
            and isinstance(
                composition.workspace_header,
                WorkspaceHeader,
            )
            and isinstance(
                composition.actions,
                list,
            )
            and isinstance(
                composition.branding,
                AppBranding,
            )
            and isinstance(
                composition.display,
                AppDisplayConfig,
            )
        )

    except (TypeError, ValueError, AttributeError):
        return False


# ============================================================================
# ROUTING INTEGRITY
# ============================================================================

def validate_route_registry() -> bool:
    """Validate the static UI route registry."""

    seen_keys = set()
    seen_paths = set()

    for route in DEFAULT_ROUTES:
        if not route.key:
            return False

        if not route.path.startswith("/"):
            return False

        if route.key in seen_keys:
            return False

        if route.path in seen_paths:
            return False

        if not isinstance(
            route.workspace,
            WorkspaceType,
        ):
            return False

        seen_keys.add(route.key)
        seen_paths.add(route.path)

    return True


def validate_workspace_registry() -> bool:
    """Validate the static workspace registry."""

    seen_keys = set()
    seen_routes = set()

    for workspace in DEFAULT_WORKSPACES:
        if not workspace.key:
            return False

        if not workspace.route.startswith("/"):
            return False

        if workspace.key in seen_keys:
            return False

        if workspace.route in seen_routes:
            return False

        if not isinstance(
            workspace.workspace,
            WorkspaceType,
        ):
            return False

        seen_keys.add(workspace.key)
        seen_routes.add(workspace.route)

    return True


# ============================================================================
# APPLICATION OPERATIONAL CHECK
# ============================================================================

def app_operational_check() -> Dict[str, Any]:
    """
    Perform a presentation-layer operational check.

    This deliberately does not claim that market/intelligence/risk/CAS/
    execution systems are operational.
    """

    authority_valid = validate_app_authority()
    routes_valid = validate_route_registry()
    workspaces_valid = validate_workspace_registry()

    shell = get_app_shell()

    state_valid = validate_app_state_integrity(
        shell.state
    )

    snapshot = shell.snapshot()

    snapshot_valid = validate_app_snapshot_integrity(
        snapshot
    )

    composition = compose_application(
        shell.state
    )

    composition_valid = (
        validate_app_composition_integrity(
            composition
        )
    )

    operational = all(
        [
            authority_valid,
            routes_valid,
            workspaces_valid,
            state_valid,
            snapshot_valid,
            composition_valid,
        ]
    )

    return {
        "engine": APP_ENGINE,
        "version": APP_VERSION,
        "operational": operational,

        "authority_valid": authority_valid,
        "route_registry_valid": routes_valid,
        "workspace_registry_valid": workspaces_valid,
        "state_integrity_valid": state_valid,
        "snapshot_integrity_valid": snapshot_valid,
        "composition_integrity_valid": composition_valid,

        "presentation_only": True,

        "market_intelligence_generation": False,
        "decision_generation": False,
        "d13_mutation": False,

        "risk_generation": False,
        "risk_override": False,

        "cas_generation": False,
        "cas_override": False,

        "execution_authority": False,
        "order_authority": False,
        "position_authority": False,

        "authentication_authority": False,
        "credential_authority": False,

        "billing_authority": False,
        "subscription_authority": False,
        "entitlement_authority": False,
    }


# ============================================================================
# APPLICATION SUMMARY
# ============================================================================

def app_summary(
    state: Optional[AppState] = None,
) -> Dict[str, Any]:
    """Return a concise application-shell summary."""

    if state is None:
        state = get_app_shell().state

    normalize_app_state(state)

    return {
        "engine": APP_ENGINE,
        "version": APP_VERSION,
        "name": APP_NAME,
        "product": APP_PRODUCT_NAME,

        "status": state.session.status.value,
        "mode": state.session.mode.value,
        "workspace": state.session.workspace.value,

        "route": state.current_route,

        "authenticated": state.session.authenticated,
        "plus_enabled": state.plus_enabled,

        "initialized": state.initialized,
        "ready": state.ready,

        "navigation_count": len(
            get_navigation_items(
                authenticated=state.session.authenticated,
                plus_enabled=state.plus_enabled,
            )
        ),

        "notification_count": len(
            state.notifications
        ),

        "unread_count": state.session.unread_count,

        "authority": dict(
            APP_UI_AUTHORITY
        ),

        "presentation_only": True,
    }


# ============================================================================
# DEFAULT APPLICATION FACTORY
# ============================================================================

def create_default_application() -> AppShell:
    """
    Create a production-default presentation shell.

    PAPER is intentionally the safe initial UI mode.
    """

    return create_application_shell(
        mode=AppMode.PAPER,
        workspace=WorkspaceType.TERMINAL,
        authenticated=False,
        plus_enabled=False,
    )


# ============================================================================
# PUBLIC API
# ============================================================================

__all__ = [
    # Identity
    "APP_ENGINE",
    "APP_VERSION",
    "APP_NAME",
    "APP_PRODUCT_NAME",
    "APP_PLUS_NAME",
    "APP_TAGLINE",
    "APP_DESCRIPTION",
    "APP_VENDOR",
    "APP_BRAND",
    "APP_DEFAULT_TITLE",
    "APP_MIN_WIDTH",
    "APP_MIN_HEIGHT",

    # Authority
    "APP_UI_AUTHORITY",

    # Enums
    "AppMode",
    "AppTheme",
    "AppDensity",
    "AppStatus",
    "WorkspaceType",
    "NavigationStyle",
    "NotificationLevel",
    "AppLifecycleEvent",
    "AppAction",

    # Core contracts
    "AppBranding",
    "AppDisplayConfig",
    "AppSession",
    "NavigationItem",
    "WorkspaceDefinition",
    "AppNotification",
    "AppSnapshot",
    "AppRoute",
    "AppState",
    "AppLifecycleRecord",
    "AppHeader",
    "AppSidebar",
    "AppStatusBar",
    "WorkspaceHeader",
    "AppActionItem",
    "AppComposition",
    "AppErrorView",
    "AppHealthView",
    "AppViewModel",

    # Registries
    "DEFAULT_NAVIGATION",
    "DEFAULT_WORKSPACES",
    "DEFAULT_ROUTES",
    "DEFAULT_ACTIONS",

    # Normalization
    "normalize_app_display_config",
    "normalize_app_session",
    "normalize_app_state",

    # Workspace / navigation
    "get_default_workspaces",
    "get_workspace_definition",
    "get_navigation_items",
    "resolve_navigation_item",
    "resolve_workspace_route",
    "get_routes",
    "get_route",
    "can_access_route",
    "select_workspace",
    "select_route",

    # State
    "create_app_state",
    "initialize_app_state",
    "set_app_status",

    # Notifications
    "add_app_notification",
    "mark_notifications_read",

    # Snapshots / presentation
    "build_app_snapshot",
    "build_app_view_model",
    "build_app_header",
    "build_app_sidebar",
    "build_app_status_bar",
    "build_workspace_header",
    "get_app_actions",
    "execute_app_action",
    "compose_application",

    # Lifecycle
    "create_lifecycle_record",
    "AppShell",
    "get_app_shell",
    "create_application_shell",
    "create_default_application",

    # Error / health
    "build_app_error_view",
    "build_app_health_view",

    # Serialization
    "serialize_app_branding",
    "serialize_app_display_config",
    "serialize_app_session",
    "serialize_navigation_item",
    "serialize_workspace_definition",
    "serialize_app_notification",
    "serialize_app_snapshot",
    "serialize_app_view_model",
    "serialize_app_composition",
    "serialize_app_health_view",
    "serialize_app_error_view",

    # Validation
    "validate_app_authority",
    "validate_app_state_integrity",
    "validate_app_snapshot_integrity",
    "validate_app_composition_integrity",
    "validate_route_registry",
    "validate_workspace_registry",

    # Operational
    "app_operational_check",
    "app_summary",
]