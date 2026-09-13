# app/ui/ui/router.py
"""
ROBOMLM_PLUS — UI Router

Part 1: Routing Foundation & Contracts

Purpose
-------
Defines the presentation-layer routing contracts used by ROBOMLM_PLUS.

The router is responsible for:
    - route identity
    - route metadata
    - navigation state
    - authentication/PLUS visibility requirements
    - route normalization
    - safe route resolution

The router is NOT responsible for:
    - market intelligence generation
    - evidence calculation
    - decision generation
    - D13 modification
    - risk generation or override
    - CAS generation or bypass
    - order execution
    - position mutation
    - authentication authority
    - entitlement authority
    - billing authority

Actual authentication, entitlement, intelligence, risk, CAS and execution
decisions remain owned by their respective upstream/domain services.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# ROUTER IDENTITY
# ---------------------------------------------------------------------------

ROUTER_ENGINE = "ROBOMLM_PLUS_UI_ROUTER"
ROUTER_VERSION = "1.0"

ROUTER_NAME = "ROBOMLM Router"
ROUTER_DESCRIPTION = (
    "Presentation-layer route orchestration for the ROBOMLM "
    "Market Intelligence OS."
)


# ---------------------------------------------------------------------------
# ROUTE CONSTANTS
# ---------------------------------------------------------------------------

ROUTE_TERMINAL = "/terminal"
ROUTE_DISCOVERY = "/discovery"
ROUTE_MEMORY = "/memory"
ROUTE_RESEARCH = "/research"
ROUTE_AUTOMATION = "/automation"
ROUTE_ACCOUNT = "/account"

ROUTE_LOGIN = "/login"
ROUTE_CONSTITUTION = "/constitution"
ROUTE_RISK_DISCLOSURE = "/risk-disclosure"
ROUTE_WORKSPACE = "/workspace"


PUBLIC_ROUTES = (
    ROUTE_LOGIN,
    ROUTE_CONSTITUTION,
    ROUTE_RISK_DISCLOSURE,
)

AUTHENTICATED_ROUTES = (
    ROUTE_TERMINAL,
    ROUTE_DISCOVERY,
    ROUTE_MEMORY,
    ROUTE_RESEARCH,
    ROUTE_AUTOMATION,
    ROUTE_ACCOUNT,
)

PLUS_ROUTES = (
    ROUTE_AUTOMATION,
)


# ---------------------------------------------------------------------------
# ENUMS
# ---------------------------------------------------------------------------

class RouteType(str, Enum):
    PUBLIC = "PUBLIC"
    AUTHENTICATED = "AUTHENTICATED"
    PLUS = "PLUS"
    SYSTEM = "SYSTEM"
    UNKNOWN = "UNKNOWN"


class RouteStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    HIDDEN = "HIDDEN"
    LOCKED = "LOCKED"
    UNKNOWN = "UNKNOWN"


class RouteAccess(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRES_LOGIN = "REQUIRES_LOGIN"
    REQUIRES_PLUS = "REQUIRES_PLUS"
    NOT_FOUND = "NOT_FOUND"
    LOCKED = "LOCKED"
    UNKNOWN = "UNKNOWN"


class RouterMode(str, Enum):
    NORMAL = "NORMAL"
    READ_ONLY = "READ_ONLY"
    LOCKED = "LOCKED"
    MAINTENANCE = "MAINTENANCE"
    UNKNOWN = "UNKNOWN"


class NavigationDirection(str, Enum):
    PUSH = "PUSH"
    REPLACE = "REPLACE"
    BACK = "BACK"
    FORWARD = "FORWARD"
    NONE = "NONE"


# ---------------------------------------------------------------------------
# AUTHORITY BOUNDARY
# ---------------------------------------------------------------------------

ROUTER_UI_AUTHORITY: Dict[str, bool] = {
    "route_resolution": True,
    "navigation": True,
    "workspace_navigation": True,
    "route_visibility": True,
    "presentation_access_state": True,
    "route_metadata": True,

    "authentication_authority": False,
    "credential_authority": False,
    "security_authority": False,

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

    "billing_authority": False,
    "subscription_authority": False,
    "entitlement_authority": False,

    "upstream_mutation": False,
}


# ---------------------------------------------------------------------------
# NORMALIZATION HELPERS
# ---------------------------------------------------------------------------

def _route_text(value: Any, default: str = "") -> str:
    if value is None:
        return default

    try:
        text = str(value).strip()
    except Exception:
        return default

    return text or default


def _route_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value

    if value is None:
        return default

    if isinstance(value, str):
        normalized = value.strip().lower()

        if normalized in {"true", "1", "yes", "on", "enabled"}:
            return True

        if normalized in {"false", "0", "no", "off", "disabled"}:
            return False

    return bool(value)


def _route_enum(
    enum_type: type[Enum],
    value: Any,
    default: Enum,
) -> Enum:
    if isinstance(value, enum_type):
        return value

    if value is None:
        return default

    try:
        return enum_type(str(value).strip().upper())
    except (ValueError, TypeError):
        return default


def normalize_route_path(path: Any) -> str:
    """
    Normalize a route without changing its semantic destination.
    """
    value = _route_text(path, ROUTE_TERMINAL)

    if not value.startswith("/"):
        value = f"/{value}"

    while "//" in value:
        value = value.replace("//", "/")

    if len(value) > 1 and value.endswith("/"):
        value = value[:-1]

    return value.lower()


# ---------------------------------------------------------------------------
# ROUTE CONTRACTS
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RouteDefinition:
    """
    Immutable presentation contract describing one UI route.
    """

    route: str
    name: str
    title: str
    description: str = ""

    route_type: RouteType = RouteType.AUTHENTICATED
    status: RouteStatus = RouteStatus.ACTIVE

    requires_login: bool = True
    requires_plus: bool = False

    icon: str = ""
    workspace: str = ""

    order: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RouteAccessContext:
    """
    Presentation-layer access state.

    These flags represent already-known application state.
    They do not perform authentication or entitlement verification.
    """

    authenticated: bool = False
    plus_enabled: bool = False
    router_mode: RouterMode = RouterMode.NORMAL

    session_active: bool = True
    ui_locked: bool = False

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RouteResolution:
    """
    Result of resolving a requested route.
    """

    requested_route: str
    resolved_route: str

    access: RouteAccess
    route_type: RouteType
    status: RouteStatus

    allowed: bool = False
    redirected: bool = False

    redirect_route: Optional[str] = None
    reason: str = ""

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class NavigationRequest:
    """
    Presentation navigation request.

    This request never carries execution/order authority.
    """

    route: str
    direction: NavigationDirection = NavigationDirection.PUSH

    authenticated: bool = False
    plus_enabled: bool = False

    source: str = "ui"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class NavigationResult:
    """
    Safe navigation outcome.
    """

    request: NavigationRequest

    route: str
    previous_route: Optional[str]

    allowed: bool
    access: RouteAccess

    redirected: bool = False
    redirect_route: Optional[str] = None

    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# DEFAULT ROUTE REGISTRY
# ---------------------------------------------------------------------------

DEFAULT_ROUTES: Tuple[RouteDefinition, ...] = (
    RouteDefinition(
        route=ROUTE_LOGIN,
        name="Login",
        title="Sign in to ROBOMLM",
        description="Secure application entry point.",
        route_type=RouteType.PUBLIC,
        requires_login=False,
        order=0,
    ),

    RouteDefinition(
        route=ROUTE_CONSTITUTION,
        name="Constitution",
        title="ROBOMLM Constitution",
        description="Core product principles and operating boundaries.",
        route_type=RouteType.PUBLIC,
        requires_login=False,
        order=1,
    ),

    RouteDefinition(
        route=ROUTE_RISK_DISCLOSURE,
        name="Risk Disclosure",
        title="Risk Disclosure",
        description="Risk and responsible-use information.",
        route_type=RouteType.PUBLIC,
        requires_login=False,
        order=2,
    ),

    RouteDefinition(
        route=ROUTE_TERMINAL,
        name="Terminal",
        title="ROBOMLM Terminal",
        description="Primary market intelligence workspace.",
        route_type=RouteType.AUTHENTICATED,
        requires_login=True,
        icon="terminal",
        workspace="TERMINAL",
        order=10,
    ),

    RouteDefinition(
        route=ROUTE_DISCOVERY,
        name="Discovery",
        title="Opportunity Discovery",
        description="Market opportunity discovery and scanner workspace.",
        route_type=RouteType.AUTHENTICATED,
        requires_login=True,
        icon="search",
        workspace="DISCOVERY",
        order=20,
    ),

    RouteDefinition(
        route=ROUTE_MEMORY,
        name="Memory",
        title="Market Memory",
        description="Historical market, evidence and decision memory.",
        route_type=RouteType.AUTHENTICATED,
        requires_login=True,
        icon="database",
        workspace="MEMORY",
        order=30,
    ),

    RouteDefinition(
        route=ROUTE_RESEARCH,
        name="Research",
        title="Research Lab",
        description="Research, analysis and learning workspace.",
        route_type=RouteType.AUTHENTICATED,
        requires_login=True,
        icon="flask",
        workspace="RESEARCH",
        order=40,
    ),

    RouteDefinition(
        route=ROUTE_AUTOMATION,
        name="Automation",
        title="AUTOROBOMLM",
        description="Automation workspace with PLUS access gating.",
        route_type=RouteType.PLUS,
        requires_login=True,
        requires_plus=True,
        icon="bolt",
        workspace="AUTOMATION",
        order=50,
    ),

    RouteDefinition(
        route=ROUTE_ACCOUNT,
        name="Account",
        title="Account & Settings",
        description="Profile, security, billing and application settings.",
        route_type=RouteType.AUTHENTICATED,
        requires_login=True,
        icon="user",
        workspace="ACCOUNT",
        order=60,
    ),
)


# ---------------------------------------------------------------------------
# ROUTE REGISTRY HELPERS
# ---------------------------------------------------------------------------

def get_default_routes() -> Tuple[RouteDefinition, ...]:
    return DEFAULT_ROUTES


def get_route_definition(
    route: Any,
    routes: Optional[Tuple[RouteDefinition, ...]] = None,
) -> Optional[RouteDefinition]:
    normalized = normalize_route_path(route)
    registry = routes or DEFAULT_ROUTES

    for item in registry:
        if normalize_route_path(item.route) == normalized:
            return item

    return None


def route_exists(
    route: Any,
    routes: Optional[Tuple[RouteDefinition, ...]] = None,
) -> bool:
    return get_route_definition(route, routes) is not None


def get_route_type(
    route: Any,
    routes: Optional[Tuple[RouteDefinition, ...]] = None,
) -> RouteType:
    definition = get_route_definition(route, routes)

    if definition is None:
        return RouteType.UNKNOWN

    return definition.route_type


def get_route_status(
    route: Any,
    routes: Optional[Tuple[RouteDefinition, ...]] = None,
) -> RouteStatus:
    definition = get_route_definition(route, routes)

    if definition is None:
        return RouteStatus.UNKNOWN

    return definition.status


def list_routes(
    authenticated: bool = False,
    plus_enabled: bool = False,
    include_hidden: bool = False,
    routes: Optional[Tuple[RouteDefinition, ...]] = None,
) -> List[RouteDefinition]:
    registry = routes or DEFAULT_ROUTES
    result: List[RouteDefinition] = []

    for definition in sorted(registry, key=lambda item: item.order):
        if definition.status == RouteStatus.HIDDEN and not include_hidden:
            continue

        if definition.requires_login and not authenticated:
            continue

        if definition.requires_plus and not plus_enabled:
            continue

        result.append(definition)

    return result
# ---------------------------------------------------------------------------
# ACCESS POLICY
# ---------------------------------------------------------------------------

def evaluate_route_access(
    route: Any,
    context: Optional[RouteAccessContext] = None,
    routes: Optional[Tuple[RouteDefinition, ...]] = None,
) -> RouteAccess:
    """
    Evaluate presentation-layer access for a route.

    This evaluates already-known UI/session state only.
    It does not authenticate users or verify subscription entitlement.
    """
    context = context or RouteAccessContext()
    normalized = normalize_route_path(route)

    definition = get_route_definition(normalized, routes)

    if definition is None:
        return RouteAccess.NOT_FOUND

    if definition.status == RouteStatus.HIDDEN:
        return RouteAccess.DENY

    if definition.status == RouteStatus.INACTIVE:
        return RouteAccess.DENY

    if definition.status == RouteStatus.LOCKED:
        return RouteAccess.LOCKED

    if context.router_mode in {
        RouterMode.LOCKED,
        RouterMode.MAINTENANCE,
    }:
        if definition.route not in PUBLIC_ROUTES:
            return RouteAccess.LOCKED

    if context.ui_locked and definition.route not in PUBLIC_ROUTES:
        return RouteAccess.LOCKED

    if not context.session_active and definition.requires_login:
        return RouteAccess.REQUIRES_LOGIN

    if definition.requires_login and not context.authenticated:
        return RouteAccess.REQUIRES_LOGIN

    if definition.requires_plus and not context.plus_enabled:
        return RouteAccess.REQUIRES_PLUS

    return RouteAccess.ALLOW


def is_route_allowed(
    route: Any,
    context: Optional[RouteAccessContext] = None,
    routes: Optional[Tuple[RouteDefinition, ...]] = None,
) -> bool:
    return (
        evaluate_route_access(route, context, routes)
        == RouteAccess.ALLOW
    )


# ---------------------------------------------------------------------------
# REDIRECT POLICY
# ---------------------------------------------------------------------------

def get_redirect_route(
    access: RouteAccess,
    requested_route: Any,
    context: Optional[RouteAccessContext] = None,
) -> Optional[str]:
    """
    Determine a safe presentation redirect.

    Redirects never grant authority. They only select another UI route.
    """
    context = context or RouteAccessContext()
    requested = normalize_route_path(requested_route)

    if access == RouteAccess.REQUIRES_LOGIN:
        return ROUTE_LOGIN

    if access == RouteAccess.REQUIRES_PLUS:
        # PLUS-gated automation must not become accessible by redirect.
        # Return Terminal as the safe authenticated fallback.
        if context.authenticated:
            return ROUTE_TERMINAL
        return ROUTE_LOGIN

    if access in {
        RouteAccess.NOT_FOUND,
        RouteAccess.DENY,
        RouteAccess.LOCKED,
    }:
        if context.authenticated:
            return ROUTE_TERMINAL
        return ROUTE_LOGIN

    if access == RouteAccess.ALLOW:
        return requested

    return None


# ---------------------------------------------------------------------------
# ROUTE RESOLUTION
# ---------------------------------------------------------------------------

def resolve_route(
    requested_route: Any,
    context: Optional[RouteAccessContext] = None,
    routes: Optional[Tuple[RouteDefinition, ...]] = None,
) -> RouteResolution:
    """
    Resolve a requested route into an allowed or safely redirected route.
    """
    context = context or RouteAccessContext()

    requested = normalize_route_path(requested_route)
    definition = get_route_definition(requested, routes)

    if definition is None:
        access = RouteAccess.NOT_FOUND

        redirect = get_redirect_route(
            access,
            requested,
            context,
        )

        return RouteResolution(
            requested_route=requested,
            resolved_route=redirect or ROUTE_LOGIN,
            access=access,
            route_type=RouteType.UNKNOWN,
            status=RouteStatus.UNKNOWN,
            allowed=False,
            redirected=redirect is not None,
            redirect_route=redirect,
            reason="Requested route does not exist.",
        )

    access = evaluate_route_access(
        requested,
        context,
        routes,
    )

    if access == RouteAccess.ALLOW:
        return RouteResolution(
            requested_route=requested,
            resolved_route=requested,
            access=access,
            route_type=definition.route_type,
            status=definition.status,
            allowed=True,
            redirected=False,
            redirect_route=None,
            reason="Route access allowed.",
            metadata=dict(definition.metadata),
        )

    redirect = get_redirect_route(
        access,
        requested,
        context,
    )

    return RouteResolution(
        requested_route=requested,
        resolved_route=redirect or ROUTE_LOGIN,
        access=access,
        route_type=definition.route_type,
        status=definition.status,
        allowed=False,
        redirected=redirect is not None,
        redirect_route=redirect,
        reason=_route_access_reason(access),
        metadata=dict(definition.metadata),
    )


def _route_access_reason(access: RouteAccess) -> str:
    reasons = {
        RouteAccess.ALLOW: "Route access allowed.",
        RouteAccess.DENY: "Route access denied.",
        RouteAccess.REQUIRES_LOGIN: "Authentication is required.",
        RouteAccess.REQUIRES_PLUS: "ROBOMLM PLUS access is required.",
        RouteAccess.NOT_FOUND: "Route was not found.",
        RouteAccess.LOCKED: "Route is currently locked.",
        RouteAccess.UNKNOWN: "Route access state is unknown.",
    }

    return reasons.get(
        access,
        "Route access state is unknown.",
    )


# ---------------------------------------------------------------------------
# NAVIGATION POLICY
# ---------------------------------------------------------------------------

def build_navigation_request(
    route: Any,
    authenticated: bool = False,
    plus_enabled: bool = False,
    direction: NavigationDirection = NavigationDirection.PUSH,
    source: str = "ui",
    metadata: Optional[Dict[str, Any]] = None,
) -> NavigationRequest:
    return NavigationRequest(
        route=normalize_route_path(route),
        direction=(
            direction
            if isinstance(direction, NavigationDirection)
            else _route_enum(
                NavigationDirection,
                direction,
                NavigationDirection.PUSH,
            )
        ),
        authenticated=_route_bool(authenticated),
        plus_enabled=_route_bool(plus_enabled),
        source=_route_text(source, "ui"),
        metadata=dict(metadata or {}),
    )


def process_navigation(
    request: NavigationRequest,
    previous_route: Optional[str] = None,
    router_mode: RouterMode = RouterMode.NORMAL,
    session_active: bool = True,
    ui_locked: bool = False,
    routes: Optional[Tuple[RouteDefinition, ...]] = None,
) -> NavigationResult:
    """
    Process a presentation navigation request.

    The router may deny or redirect navigation but can never grant
    market, decision, risk, CAS, or execution authority.
    """
    context = RouteAccessContext(
        authenticated=request.authenticated,
        plus_enabled=request.plus_enabled,
        router_mode=(
            router_mode
            if isinstance(router_mode, RouterMode)
            else _route_enum(
                RouterMode,
                router_mode,
                RouterMode.NORMAL,
            )
        ),
        session_active=_route_bool(session_active, True),
        ui_locked=_route_bool(ui_locked),
    )

    resolution = resolve_route(
        request.route,
        context,
        routes,
    )

    final_route = resolution.resolved_route

    return NavigationResult(
        request=request,
        route=final_route,
        previous_route=(
            normalize_route_path(previous_route)
            if previous_route
            else None
        ),
        allowed=resolution.allowed,
        access=resolution.access,
        redirected=resolution.redirected,
        redirect_route=resolution.redirect_route,
        reason=resolution.reason,
        metadata={
            "router_engine": ROUTER_ENGINE,
            "router_version": ROUTER_VERSION,
            "requested_route": resolution.requested_route,
            "resolved_route": resolution.resolved_route,
            "ui_only": True,
        },
    )


# ---------------------------------------------------------------------------
# WORKSPACE ROUTING
# ---------------------------------------------------------------------------

ROUTE_TO_WORKSPACE: Dict[str, str] = {
    ROUTE_TERMINAL: "TERMINAL",
    ROUTE_DISCOVERY: "DISCOVERY",
    ROUTE_MEMORY: "MEMORY",
    ROUTE_RESEARCH: "RESEARCH",
    ROUTE_AUTOMATION: "AUTOMATION",
    ROUTE_ACCOUNT: "ACCOUNT",
}


WORKSPACE_TO_ROUTE: Dict[str, str] = {
    workspace: route
    for route, workspace in ROUTE_TO_WORKSPACE.items()
}


def route_to_workspace(route: Any) -> Optional[str]:
    normalized = normalize_route_path(route)
    return ROUTE_TO_WORKSPACE.get(normalized)


def workspace_to_route(workspace: Any) -> Optional[str]:
    value = _route_text(workspace).upper()

    return WORKSPACE_TO_ROUTE.get(value)


def resolve_workspace_route(
    workspace: Any,
    context: Optional[RouteAccessContext] = None,
) -> RouteResolution:
    route = workspace_to_route(workspace)

    if route is None:
        requested = _route_text(workspace, "UNKNOWN")

        return RouteResolution(
            requested_route=requested,
            resolved_route=ROUTE_TERMINAL,
            access=RouteAccess.NOT_FOUND,
            route_type=RouteType.UNKNOWN,
            status=RouteStatus.UNKNOWN,
            allowed=False,
            redirected=True,
            redirect_route=ROUTE_TERMINAL,
            reason="Workspace route was not found.",
        )

    return resolve_route(
        route,
        context,
    )


# ---------------------------------------------------------------------------
# NAVIGATION HISTORY
# ---------------------------------------------------------------------------

@dataclass
class NavigationHistory:
    """
    Presentation-only browser-style navigation history.
    """

    current_route: str = ROUTE_TERMINAL
    back_stack: List[str] = field(default_factory=list)
    forward_stack: List[str] = field(default_factory=list)
    max_entries: int = 50

    def push(self, route: Any) -> None:
        normalized = normalize_route_path(route)

        if normalized == self.current_route:
            return

        self.back_stack.append(self.current_route)

        if len(self.back_stack) > self.max_entries:
            self.back_stack = self.back_stack[-self.max_entries:]

        self.current_route = normalized
        self.forward_stack.clear()

    def back(self) -> Optional[str]:
        if not self.back_stack:
            return None

        previous = self.back_stack.pop()

        self.forward_stack.append(self.current_route)
        self.current_route = previous

        return previous

    def forward(self) -> Optional[str]:
        if not self.forward_stack:
            return None

        next_route = self.forward_stack.pop()

        self.back_stack.append(self.current_route)
        self.current_route = next_route

        return next_route

    def clear(self) -> None:
        self.back_stack.clear()
        self.forward_stack.clear()

    def snapshot(self) -> Dict[str, Any]:
        return {
            "current_route": self.current_route,
            "back_stack": list(self.back_stack),
            "forward_stack": list(self.forward_stack),
            "max_entries": self.max_entries,
        }
# ---------------------------------------------------------------------------
# ROUTER EVENTS
# ---------------------------------------------------------------------------

from datetime import datetime, timezone


def _router_now() -> datetime:
    return datetime.now(timezone.utc)


class RouterEvent(str, Enum):
    ROUTE_REQUESTED = "ROUTE_REQUESTED"
    ROUTE_RESOLVED = "ROUTE_RESOLVED"
    NAVIGATION_ALLOWED = "NAVIGATION_ALLOWED"
    NAVIGATION_DENIED = "NAVIGATION_DENIED"
    REDIRECTED = "REDIRECTED"
    ROUTE_CHANGED = "ROUTE_CHANGED"
    BACK = "BACK"
    FORWARD = "FORWARD"
    HISTORY_CLEARED = "HISTORY_CLEARED"
    ROUTER_LOCKED = "ROUTER_LOCKED"
    ROUTER_UNLOCKED = "ROUTER_UNLOCKED"


@dataclass(frozen=True)
class RouterEventRecord:
    event: RouterEvent
    route: str
    previous_route: Optional[str] = None
    timestamp: datetime = field(default_factory=_router_now)
    source: str = "router"
    metadata: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# ROUTER STATE
# ---------------------------------------------------------------------------

@dataclass
class RouterState:
    current_route: str = ROUTE_TERMINAL
    previous_route: Optional[str] = None

    authenticated: bool = False
    plus_enabled: bool = False

    router_mode: RouterMode = RouterMode.NORMAL
    session_active: bool = True
    ui_locked: bool = False

    initialized: bool = False
    ready: bool = False

    navigation_count: int = 0
    denied_count: int = 0
    redirect_count: int = 0

    metadata: Dict[str, Any] = field(default_factory=dict)


def create_router_state(
    *,
    current_route: str = ROUTE_TERMINAL,
    authenticated: bool = False,
    plus_enabled: bool = False,
) -> RouterState:
    return RouterState(
        current_route=normalize_route_path(current_route),
        authenticated=_route_bool(authenticated),
        plus_enabled=_route_bool(plus_enabled),
    )


def normalize_router_state(state: RouterState) -> RouterState:
    state.current_route = normalize_route_path(
        state.current_route
    )

    if state.previous_route:
        state.previous_route = normalize_route_path(
            state.previous_route
        )

    state.authenticated = _route_bool(
        state.authenticated
    )

    state.plus_enabled = _route_bool(
        state.plus_enabled
    )

    state.session_active = _route_bool(
        state.session_active,
        True,
    )

    state.ui_locked = _route_bool(
        state.ui_locked
    )

    state.navigation_count = max(
        0,
        int(state.navigation_count),
    )

    state.denied_count = max(
        0,
        int(state.denied_count),
    )

    state.redirect_count = max(
        0,
        int(state.redirect_count),
    )

    return state


# ---------------------------------------------------------------------------
# ROUTER SNAPSHOT
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RouterSnapshot:
    engine: str
    version: str

    current_route: str
    previous_route: Optional[str]

    authenticated: bool
    plus_enabled: bool

    router_mode: RouterMode
    session_active: bool
    ui_locked: bool

    initialized: bool
    ready: bool

    navigation_count: int
    denied_count: int
    redirect_count: int

    history: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


def build_router_snapshot(
    state: RouterState,
    history: NavigationHistory,
) -> RouterSnapshot:
    normalize_router_state(state)

    return RouterSnapshot(
        engine=ROUTER_ENGINE,
        version=ROUTER_VERSION,
        current_route=state.current_route,
        previous_route=state.previous_route,
        authenticated=state.authenticated,
        plus_enabled=state.plus_enabled,
        router_mode=state.router_mode,
        session_active=state.session_active,
        ui_locked=state.ui_locked,
        initialized=state.initialized,
        ready=state.ready,
        navigation_count=state.navigation_count,
        denied_count=state.denied_count,
        redirect_count=state.redirect_count,
        history=history.snapshot(),
        metadata={
            **state.metadata,
            "ui_only": True,
            "d13_authority": False,
            "risk_authority": False,
            "cas_authority": False,
            "execution_authority": False,
        },
    )


# ---------------------------------------------------------------------------
# ROUTER CONTROLLER
# ---------------------------------------------------------------------------

class UIRouter:
    """
    Central presentation-layer router.

    The router controls where the UI goes, not what the intelligence says.
    """

    def __init__(
        self,
        state: Optional[RouterState] = None,
        routes: Optional[Tuple[RouteDefinition, ...]] = None,
    ) -> None:
        self.state = state or create_router_state()
        self.routes = routes or DEFAULT_ROUTES
        self.history = NavigationHistory(
            current_route=self.state.current_route
        )
        self.events: List[RouterEventRecord] = []

    # ------------------------------------------------------------------
    # INTERNAL EVENT RECORDING
    # ------------------------------------------------------------------

    def _record(
        self,
        event: RouterEvent,
        route: Optional[str] = None,
        previous_route: Optional[str] = None,
        source: str = "router",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RouterEventRecord:
        record = RouterEventRecord(
            event=event,
            route=normalize_route_path(
                route or self.state.current_route
            ),
            previous_route=(
                normalize_route_path(previous_route)
                if previous_route
                else None
            ),
            source=source,
            metadata=dict(metadata or {}),
        )

        self.events.append(record)

        # Prevent uncontrolled in-memory event growth.
        if len(self.events) > 500:
            self.events = self.events[-500:]

        return record

    # ------------------------------------------------------------------
    # LIFECYCLE
    # ------------------------------------------------------------------

    def initialize(self) -> RouterSnapshot:
        self.state.initialized = True
        self.state.ready = True

        self._record(
            RouterEvent.ROUTE_RESOLVED,
            metadata={
                "initialization": True,
                "ui_only": True,
            },
        )

        return self.snapshot()

    def lock(self) -> RouterSnapshot:
        self.state.router_mode = RouterMode.LOCKED
        self.state.ui_locked = True

        self._record(
            RouterEvent.ROUTER_LOCKED,
            metadata={"ui_only": True},
        )

        return self.snapshot()

    def unlock(self) -> RouterSnapshot:
        self.state.router_mode = RouterMode.NORMAL
        self.state.ui_locked = False

        self._record(
            RouterEvent.ROUTER_UNLOCKED,
            metadata={"ui_only": True},
        )

        return self.snapshot()

    # ------------------------------------------------------------------
    # PRESENTATION ACCESS STATE
    # ------------------------------------------------------------------

    def set_authenticated(
        self,
        authenticated: bool,
    ) -> RouterSnapshot:
        """
        Set already-established presentation authentication state.

        This does NOT authenticate the user.
        """
        self.state.authenticated = _route_bool(
            authenticated
        )

        if not self.state.authenticated:
            self.state.plus_enabled = False

            if (
                self.state.current_route
                not in PUBLIC_ROUTES
            ):
                previous = self.state.current_route
                self.state.previous_route = previous
                self.state.current_route = ROUTE_LOGIN
                self.history.push(ROUTE_LOGIN)

        return self.snapshot()

    def set_plus_enabled(
        self,
        enabled: bool,
    ) -> RouterSnapshot:
        """
        Set already-established presentation PLUS visibility.

        This does NOT verify subscription entitlement.
        """
        self.state.plus_enabled = (
            _route_bool(enabled)
            if self.state.authenticated
            else False
        )

        if (
            not self.state.plus_enabled
            and self.state.current_route
            in PLUS_ROUTES
        ):
            previous = self.state.current_route

            self.state.previous_route = previous
            self.state.current_route = ROUTE_TERMINAL

            self.history.push(ROUTE_TERMINAL)

        return self.snapshot()

    # ------------------------------------------------------------------
    # NAVIGATION
    # ------------------------------------------------------------------

    def navigate(
        self,
        route: Any,
        *,
        direction: NavigationDirection = NavigationDirection.PUSH,
        source: str = "ui",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> NavigationResult:
        requested = normalize_route_path(route)

        self._record(
            RouterEvent.ROUTE_REQUESTED,
            route=requested,
            source=source,
            metadata=dict(metadata or {}),
        )

        request = build_navigation_request(
            requested,
            authenticated=self.state.authenticated,
            plus_enabled=self.state.plus_enabled,
            direction=direction,
            source=source,
            metadata=metadata,
        )

        result = process_navigation(
            request=request,
            previous_route=self.state.current_route,
            router_mode=self.state.router_mode,
            session_active=self.state.session_active,
            ui_locked=self.state.ui_locked,
            routes=self.routes,
        )

        if result.allowed:
            old_route = self.state.current_route

            self.state.previous_route = old_route
            self.state.current_route = result.route

            if result.route != old_route:
                self.history.push(result.route)

            self.state.navigation_count += 1

            self._record(
                RouterEvent.NAVIGATION_ALLOWED,
                route=result.route,
                previous_route=old_route,
                source=source,
            )

            if result.route != old_route:
                self._record(
                    RouterEvent.ROUTE_CHANGED,
                    route=result.route,
                    previous_route=old_route,
                    source=source,
                )

        else:
            self.state.denied_count += 1

            self._record(
                RouterEvent.NAVIGATION_DENIED,
                route=requested,
                previous_route=self.state.current_route,
                source=source,
                metadata={
                    "access": result.access.value,
                    "reason": result.reason,
                },
            )

            if result.redirected:
                old_route = self.state.current_route

                self.state.previous_route = old_route
                self.state.current_route = result.route
                self.state.redirect_count += 1

                self.history.push(result.route)

                self._record(
                    RouterEvent.REDIRECTED,
                    route=result.route,
                    previous_route=old_route,
                    source=source,
                    metadata={
                        "requested_route": requested,
                        "reason": result.reason,
                    },
                )

        return result

    # ------------------------------------------------------------------
    # BACK / FORWARD
    # ------------------------------------------------------------------

    def back(self) -> Optional[NavigationResult]:
        target = self.history.back()

        if target is None:
            return None

        previous = self.state.current_route

        request = build_navigation_request(
            target,
            authenticated=self.state.authenticated,
            plus_enabled=self.state.plus_enabled,
            direction=NavigationDirection.BACK,
            source="router",
        )

        result = process_navigation(
            request=request,
            previous_route=previous,
            router_mode=self.state.router_mode,
            session_active=self.state.session_active,
            ui_locked=self.state.ui_locked,
            routes=self.routes,
        )

        if result.allowed:
            self.state.previous_route = previous
            self.state.current_route = target

            self._record(
                RouterEvent.BACK,
                route=target,
                previous_route=previous,
            )

        return result

    def forward(self) -> Optional[NavigationResult]:
        target = self.history.forward()

        if target is None:
            return None

        previous = self.state.current_route

        request = build_navigation_request(
            target,
            authenticated=self.state.authenticated,
            plus_enabled=self.state.plus_enabled,
            direction=NavigationDirection.FORWARD,
            source="router",
        )

        result = process_navigation(
            request=request,
            previous_route=previous,
            router_mode=self.state.router_mode,
            session_active=self.state.session_active,
            ui_locked=self.state.ui_locked,
            routes=self.routes,
        )

        if result.allowed:
            self.state.previous_route = previous
            self.state.current_route = target

            self._record(
                RouterEvent.FORWARD,
                route=target,
                previous_route=previous,
            )

        return result

    # ------------------------------------------------------------------
    # HISTORY
    # ------------------------------------------------------------------

    def clear_history(self) -> None:
        self.history.clear()

        self._record(
            RouterEvent.HISTORY_CLEARED,
            route=self.state.current_route,
        )

    # ------------------------------------------------------------------
    # QUERY
    # ------------------------------------------------------------------

    def current_definition(self) -> Optional[RouteDefinition]:
        return get_route_definition(
            self.state.current_route,
            self.routes,
        )

    def current_workspace(self) -> Optional[str]:
        return route_to_workspace(
            self.state.current_route
        )

    def available_routes(self) -> List[RouteDefinition]:
        return list_routes(
            authenticated=self.state.authenticated,
            plus_enabled=self.state.plus_enabled,
            routes=self.routes,
        )

    # ------------------------------------------------------------------
    # SNAPSHOT
    # ------------------------------------------------------------------

    def snapshot(self) -> RouterSnapshot:
        return build_router_snapshot(
            self.state,
            self.history,
        )

    def event_history(self) -> List[RouterEventRecord]:
        return list(self.events)


# ---------------------------------------------------------------------------
# DEFAULT ROUTER
# ---------------------------------------------------------------------------

_DEFAULT_ROUTER: Optional[UIRouter] = None


def get_ui_router() -> UIRouter:
    global _DEFAULT_ROUTER

    if _DEFAULT_ROUTER is None:
        _DEFAULT_ROUTER = UIRouter()

    return _DEFAULT_ROUTER


def create_ui_router(
    *,
    authenticated: bool = False,
    plus_enabled: bool = False,
    current_route: str = ROUTE_TERMINAL,
) -> UIRouter:
    state = create_router_state(
        current_route=current_route,
        authenticated=authenticated,
        plus_enabled=plus_enabled,
    )

    return UIRouter(state=state)


# ---------------------------------------------------------------------------
# ROUTER PUBLIC HELPERS
# ---------------------------------------------------------------------------

def navigate_route(
    route: Any,
    *,
    authenticated: bool = False,
    plus_enabled: bool = False,
    current_route: str = ROUTE_TERMINAL,
) -> NavigationResult:
    router = create_ui_router(
        authenticated=authenticated,
        plus_enabled=plus_enabled,
        current_route=current_route,
    )

    return router.navigate(route)


def resolve_ui_route(
    route: Any,
    *,
    authenticated: bool = False,
    plus_enabled: bool = False,
) -> RouteResolution:
    context = RouteAccessContext(
        authenticated=authenticated,
        plus_enabled=plus_enabled,
    )

    return resolve_route(
        route,
        context,
    )
# ---------------------------------------------------------------------------
# SERIALIZATION
# ---------------------------------------------------------------------------

def _serialize_router_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            str(key): _serialize_router_value(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            _serialize_router_value(item)
            for item in value
        ]

    if hasattr(value, "__dataclass_fields__"):
        return {
            key: _serialize_router_value(
                getattr(value, key)
            )
            for key in value.__dataclass_fields__
        }

    return value


def serialize_route_definition(
    definition: RouteDefinition,
) -> Dict[str, Any]:
    return _serialize_router_value(definition)


def serialize_route_access_context(
    context: RouteAccessContext,
) -> Dict[str, Any]:
    return _serialize_router_value(context)


def serialize_route_resolution(
    resolution: RouteResolution,
) -> Dict[str, Any]:
    return _serialize_router_value(resolution)


def serialize_navigation_request(
    request: NavigationRequest,
) -> Dict[str, Any]:
    return _serialize_router_value(request)


def serialize_navigation_result(
    result: NavigationResult,
) -> Dict[str, Any]:
    return _serialize_router_value(result)


def serialize_router_state(
    state: RouterState,
) -> Dict[str, Any]:
    return _serialize_router_value(state)


def serialize_router_snapshot(
    snapshot: RouterSnapshot,
) -> Dict[str, Any]:
    return _serialize_router_value(snapshot)


def serialize_router_event(
    event: RouterEventRecord,
) -> Dict[str, Any]:
    return _serialize_router_value(event)


# ---------------------------------------------------------------------------
# ROUTE INTEGRITY
# ---------------------------------------------------------------------------

def validate_route_definition(
    definition: RouteDefinition,
) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    if not normalize_route_path(definition.route):
        errors.append("Route path is empty.")

    if not _route_text(definition.name):
        errors.append("Route name is empty.")

    if not _route_text(definition.title):
        errors.append("Route title is empty.")

    if (
        definition.requires_plus
        and not definition.requires_login
    ):
        errors.append(
            "PLUS route cannot bypass login requirement."
        )

    if (
        definition.requires_plus
        and definition.route_type != RouteType.PLUS
    ):
        errors.append(
            "PLUS-gated route must use RouteType.PLUS."
        )

    if (
        definition.route_type == RouteType.PUBLIC
        and definition.requires_login
    ):
        errors.append(
            "Public route cannot require login."
        )

    return len(errors) == 0, errors


def validate_route_registry(
    routes: Optional[Tuple[RouteDefinition, ...]] = None,
) -> Dict[str, Any]:
    registry = routes or DEFAULT_ROUTES

    errors: List[str] = []
    warnings: List[str] = []
    seen: set[str] = set()

    for definition in registry:
        normalized = normalize_route_path(
            definition.route
        )

        if normalized in seen:
            errors.append(
                f"Duplicate route: {normalized}"
            )

        seen.add(normalized)

        valid, definition_errors = (
            validate_route_definition(definition)
        )

        if not valid:
            errors.extend(
                f"{normalized}: {error}"
                for error in definition_errors
            )

    required_routes = {
        ROUTE_TERMINAL,
        ROUTE_DISCOVERY,
        ROUTE_MEMORY,
        ROUTE_RESEARCH,
        ROUTE_AUTOMATION,
        ROUTE_ACCOUNT,
    }

    registered_routes = {
        normalize_route_path(item.route)
        for item in registry
    }

    missing = required_routes - registered_routes

    if missing:
        errors.extend(
            f"Missing required route: {route}"
            for route in sorted(missing)
        )

    automation = get_route_definition(
        ROUTE_AUTOMATION,
        registry,
    )

    if automation is not None:
        if not automation.requires_plus:
            errors.append(
                "Automation route must require PLUS."
            )

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "route_count": len(registry),
        "registered_routes": sorted(registered_routes),
    }


# ---------------------------------------------------------------------------
# ROUTER STATE INTEGRITY
# ---------------------------------------------------------------------------

def validate_router_state_integrity(
    state: RouterState,
    routes: Optional[Tuple[RouteDefinition, ...]] = None,
) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []

    normalize_router_state(state)

    if not route_exists(state.current_route, routes):
        errors.append(
            f"Current route does not exist: "
            f"{state.current_route}"
        )

    if state.previous_route:
        if not route_exists(
            state.previous_route,
            routes,
        ):
            warnings.append(
                f"Previous route is not registered: "
                f"{state.previous_route}"
            )

    if state.plus_enabled and not state.authenticated:
        errors.append(
            "PLUS visibility cannot be enabled "
            "without authenticated presentation state."
        )

    if (
        state.current_route in PLUS_ROUTES
        and not state.plus_enabled
    ):
        errors.append(
            "PLUS route cannot remain active "
            "when PLUS visibility is disabled."
        )

    if (
        state.current_route in AUTHENTICATED_ROUTES
        and not state.authenticated
    ):
        errors.append(
            "Authenticated route cannot be active "
            "without authenticated presentation state."
        )

    if state.navigation_count < 0:
        errors.append(
            "Navigation count cannot be negative."
        )

    if state.denied_count < 0:
        errors.append(
            "Denied count cannot be negative."
        )

    if state.redirect_count < 0:
        errors.append(
            "Redirect count cannot be negative."
        )

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
    }


# ---------------------------------------------------------------------------
# RESOLUTION INTEGRITY
# ---------------------------------------------------------------------------

def validate_route_resolution(
    resolution: RouteResolution,
) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []

    requested = normalize_route_path(
        resolution.requested_route
    )

    resolved = normalize_route_path(
        resolution.resolved_route
    )

    if not requested:
        errors.append(
            "Requested route is empty."
        )

    if not resolved:
        errors.append(
            "Resolved route is empty."
        )

    if resolution.allowed:
        if resolution.access != RouteAccess.ALLOW:
            errors.append(
                "Allowed resolution must have "
                "RouteAccess.ALLOW."
            )

        if resolution.redirected:
            warnings.append(
                "Resolution is marked allowed and redirected."
            )

        if requested != resolved:
            errors.append(
                "Allowed route resolution must preserve "
                "the requested route."
            )

    if resolution.redirected:
        if not resolution.redirect_route:
            errors.append(
                "Redirected resolution requires "
                "redirect_route."
            )

        if (
            resolution.redirect_route
            and normalize_route_path(
                resolution.redirect_route
            ) != resolved
        ):
            errors.append(
                "Redirect route must match resolved route."
            )

    if (
        resolution.access == RouteAccess.REQUIRES_PLUS
        and resolved == ROUTE_AUTOMATION
    ):
        errors.append(
            "PLUS-denied automation cannot resolve "
            "to automation itself."
        )

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
    }


# ---------------------------------------------------------------------------
# AUTHORITY INTEGRITY
# ---------------------------------------------------------------------------

def validate_router_authority() -> Dict[str, Any]:
    required_false = {
        "authentication_authority",
        "credential_authority",
        "security_authority",
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
        "billing_authority",
        "subscription_authority",
        "entitlement_authority",
        "upstream_mutation",
    }

    errors: List[str] = []

    for key in required_false:
        if ROUTER_UI_AUTHORITY.get(key) is not False:
            errors.append(
                f"Router authority violation: {key}"
            )

    if not ROUTER_UI_AUTHORITY.get(
        "route_resolution",
        False,
    ):
        errors.append(
            "Route resolution authority must remain enabled."
        )

    if not ROUTER_UI_AUTHORITY.get(
        "navigation",
        False,
    ):
        errors.append(
            "Navigation authority must remain enabled."
        )

    return {
        "valid": not errors,
        "errors": errors,
        "authority": dict(ROUTER_UI_AUTHORITY),
    }


# ---------------------------------------------------------------------------
# ROUTER HEALTH
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RouterHealth:
    engine: str
    version: str

    operational: bool
    initialized: bool
    ready: bool

    route_registry_valid: bool
    state_valid: bool
    authority_valid: bool

    current_route: str
    current_access: RouteAccess

    error_count: int = 0
    warning_count: int = 0

    details: Dict[str, Any] = field(
        default_factory=dict
    )


def build_router_health(
    router: UIRouter,
) -> RouterHealth:
    registry_check = validate_route_registry(
        router.routes
    )

    state_check = validate_router_state_integrity(
        router.state,
        router.routes,
    )

    authority_check = validate_router_authority()

    current_access = evaluate_route_access(
        router.state.current_route,
        RouteAccessContext(
            authenticated=router.state.authenticated,
            plus_enabled=router.state.plus_enabled,
            router_mode=router.state.router_mode,
            session_active=router.state.session_active,
            ui_locked=router.state.ui_locked,
        ),
        router.routes,
    )

    errors = (
        len(registry_check["errors"])
        + len(state_check["errors"])
        + len(authority_check["errors"])
    )

    warnings = (
        len(registry_check["warnings"])
        + len(state_check["warnings"])
    )

    operational = (
        errors == 0
        and router.state.initialized
        and router.state.ready
        and current_access
        in {
            RouteAccess.ALLOW,
            RouteAccess.REQUIRES_LOGIN,
            RouteAccess.REQUIRES_PLUS,
        }
    )

    return RouterHealth(
        engine=ROUTER_ENGINE,
        version=ROUTER_VERSION,
        operational=operational,
        initialized=router.state.initialized,
        ready=router.state.ready,
        route_registry_valid=registry_check["valid"],
        state_valid=state_check["valid"],
        authority_valid=authority_check["valid"],
        current_route=router.state.current_route,
        current_access=current_access,
        error_count=errors,
        warning_count=warnings,
        details={
            "ui_only": True,
            "route_count": len(router.routes),
            "navigation_count": router.state.navigation_count,
            "denied_count": router.state.denied_count,
            "redirect_count": router.state.redirect_count,
        },
    )


def serialize_router_health(
    health: RouterHealth,
) -> Dict[str, Any]:
    return _serialize_router_value(health)


# ---------------------------------------------------------------------------
# OPERATIONAL CHECK
# ---------------------------------------------------------------------------

def router_operational_check(
    router: Optional[UIRouter] = None,
) -> Dict[str, Any]:
    active_router = router or get_ui_router()

    health = build_router_health(
        active_router
    )

    return {
        "engine": ROUTER_ENGINE,
        "version": ROUTER_VERSION,
        "operational": health.operational,
        "initialized": health.initialized,
        "ready": health.ready,
        "route_registry_valid": health.route_registry_valid,
        "state_valid": health.state_valid,
        "authority_valid": health.authority_valid,
        "current_route": health.current_route,
        "current_access": health.current_access.value,
        "errors": health.error_count,
        "warnings": health.warning_count,

        "ui_only": True,
        "intelligence_generation": False,
        "decision_generation": False,
        "d13_modification": False,
        "risk_generation": False,
        "risk_override": False,
        "cas_generation": False,
        "cas_bypass": False,
        "execution": False,
        "order_mutation": False,
        "position_mutation": False,
    }


# ---------------------------------------------------------------------------
# ROUTER SUMMARY
# ---------------------------------------------------------------------------

def router_summary(
    router: Optional[UIRouter] = None,
) -> Dict[str, Any]:
    active_router = router or get_ui_router()

    health = build_router_health(
        active_router
    )

    return {
        "engine": ROUTER_ENGINE,
        "version": ROUTER_VERSION,
        "name": ROUTER_NAME,
        "description": ROUTER_DESCRIPTION,

        "current_route": active_router.state.current_route,
        "current_workspace": (
            active_router.current_workspace()
        ),

        "authenticated": (
            active_router.state.authenticated
        ),
        "plus_enabled": (
            active_router.state.plus_enabled
        ),

        "router_mode": (
            active_router.state.router_mode.value
        ),

        "initialized": (
            active_router.state.initialized
        ),
        "ready": active_router.state.ready,
        "operational": health.operational,

        "route_count": len(active_router.routes),
        "available_route_count": len(
            active_router.available_routes()
        ),

        "navigation_count": (
            active_router.state.navigation_count
        ),
        "denied_count": (
            active_router.state.denied_count
        ),
        "redirect_count": (
            active_router.state.redirect_count
        ),

        "ui_only": True,
        "d13_authority": False,
        "risk_authority": False,
        "cas_authority": False,
        "execution_authority": False,
    }


# ---------------------------------------------------------------------------
# PUBLIC EXPORTS
# ---------------------------------------------------------------------------

__all__ = [
    # Identity
    "ROUTER_ENGINE",
    "ROUTER_VERSION",
    "ROUTER_NAME",
    "ROUTER_DESCRIPTION",

    # Route constants
    "ROUTE_TERMINAL",
    "ROUTE_DISCOVERY",
    "ROUTE_MEMORY",
    "ROUTE_RESEARCH",
    "ROUTE_AUTOMATION",
    "ROUTE_ACCOUNT",
    "ROUTE_LOGIN",
    "ROUTE_CONSTITUTION",
    "ROUTE_RISK_DISCLOSURE",
    "ROUTE_WORKSPACE",

    "PUBLIC_ROUTES",
    "AUTHENTICATED_ROUTES",
    "PLUS_ROUTES",

    # Enums
    "RouteType",
    "RouteStatus",
    "RouteAccess",
    "RouterMode",
    "NavigationDirection",
    "RouterEvent",

    # Authority
    "ROUTER_UI_AUTHORITY",

    # Contracts
    "RouteDefinition",
    "RouteAccessContext",
    "RouteResolution",
    "NavigationRequest",
    "NavigationResult",
    "NavigationHistory",
    "RouterEventRecord",
    "RouterState",
    "RouterSnapshot",
    "RouterHealth",

    # Registry
    "DEFAULT_ROUTES",
    "ROUTE_TO_WORKSPACE",
    "WORKSPACE_TO_ROUTE",

    # Normalization
    "normalize_route_path",

    # Route helpers
    "get_default_routes",
    "get_route_definition",
    "route_exists",
    "get_route_type",
    "get_route_status",
    "list_routes",

    # Access
    "evaluate_route_access",
    "is_route_allowed",
    "get_redirect_route",
    "resolve_route",

    # Navigation
    "build_navigation_request",
    "process_navigation",

    # Workspace
    "route_to_workspace",
    "workspace_to_route",
    "resolve_workspace_route",

    # Controller
    "UIRouter",
    "get_ui_router",
    "create_ui_router",

    # Public navigation
    "navigate_route",
    "resolve_ui_route",

    # Serialization
    "serialize_route_definition",
    "serialize_route_access_context",
    "serialize_route_resolution",
    "serialize_navigation_request",
    "serialize_navigation_result",
    "serialize_router_state",
    "serialize_router_snapshot",
    "serialize_router_event",
    "serialize_router_health",

    # Validation
    "validate_route_definition",
    "validate_route_registry",
    "validate_router_state_integrity",
    "validate_route_resolution",
    "validate_router_authority",

    # Health
    "build_router_health",
    "router_operational_check",
    "router_summary",
]
# ---------------------------------------------------------------------------
# ROUTER EVENT / HISTORY SERIALIZATION
# ---------------------------------------------------------------------------

def serialize_navigation_history(
    history: NavigationHistory,
) -> Dict[str, Any]:
    return {
        "current_route": normalize_route_path(
            history.current_route
        ),
        "back_stack": [
            normalize_route_path(route)
            for route in history.back_stack
        ],
        "forward_stack": [
            normalize_route_path(route)
            for route in history.forward_stack
        ],
        "max_entries": int(history.max_entries),
    }


def serialize_router_events(
    events: List[RouterEventRecord],
) -> List[Dict[str, Any]]:
    return [
        serialize_router_event(event)
        for event in events
    ]


# ---------------------------------------------------------------------------
# NAVIGATION HISTORY INTEGRITY
# ---------------------------------------------------------------------------

def validate_navigation_history(
    history: NavigationHistory,
    routes: Optional[Tuple[RouteDefinition, ...]] = None,
) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []

    if history.max_entries <= 0:
        errors.append(
            "Navigation history max_entries must be greater than zero."
        )

    if not route_exists(
        history.current_route,
        routes,
    ):
        errors.append(
            "Navigation history current route is not registered."
        )

    for route in history.back_stack:
        if not route_exists(route, routes):
            warnings.append(
                f"Back-stack route is not registered: {route}"
            )

    for route in history.forward_stack:
        if not route_exists(route, routes):
            warnings.append(
                f"Forward-stack route is not registered: {route}"
            )

    if len(history.back_stack) > history.max_entries:
        errors.append(
            "Back-stack exceeds configured history limit."
        )

    if len(history.forward_stack) > history.max_entries:
        errors.append(
            "Forward-stack exceeds configured history limit."
        )

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
    }


# ---------------------------------------------------------------------------
# ROUTER EVENT INTEGRITY
# ---------------------------------------------------------------------------

def validate_router_events(
    events: List[RouterEventRecord],
) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []

    if len(events) > 500:
        errors.append(
            "Router event buffer exceeds safety limit."
        )

    for index, event in enumerate(events):
        if not isinstance(event.event, RouterEvent):
            errors.append(
                f"Invalid router event at index {index}."
            )

        if not _route_text(event.route):
            errors.append(
                f"Empty route in router event at index {index}."
            )

        if event.previous_route:
            if not _route_text(event.previous_route):
                warnings.append(
                    f"Invalid previous route at index {index}."
                )

        if event.timestamp.tzinfo is None:
            warnings.append(
                f"Naive timestamp at event index {index}."
            )

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "event_count": len(events),
    }


# ---------------------------------------------------------------------------
# ROUTER COMPLETE INTEGRITY
# ---------------------------------------------------------------------------

def validate_router_integrity(
    router: UIRouter,
) -> Dict[str, Any]:
    registry = validate_route_registry(
        router.routes
    )

    state = validate_router_state_integrity(
        router.state,
        router.routes,
    )

    history = validate_navigation_history(
        router.history,
        router.routes,
    )

    events = validate_router_events(
        router.events
    )

    authority = validate_router_authority()

    errors = (
        registry["errors"]
        + state["errors"]
        + history["errors"]
        + events["errors"]
        + authority["errors"]
    )

    warnings = (
        registry["warnings"]
        + state["warnings"]
        + history["warnings"]
        + events["warnings"]
    )

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,

        "registry": registry,
        "state": state,
        "history": history,
        "events": events,
        "authority": authority,

        "ui_only": True,
    }


# ---------------------------------------------------------------------------
# ROUTE DIAGNOSTICS
# ---------------------------------------------------------------------------

def diagnose_route(
    route: Any,
    *,
    authenticated: bool = False,
    plus_enabled: bool = False,
    router_mode: RouterMode = RouterMode.NORMAL,
    session_active: bool = True,
    ui_locked: bool = False,
    routes: Optional[Tuple[RouteDefinition, ...]] = None,
) -> Dict[str, Any]:
    normalized = normalize_route_path(route)

    context = RouteAccessContext(
        authenticated=_route_bool(authenticated),
        plus_enabled=_route_bool(plus_enabled),
        router_mode=(
            router_mode
            if isinstance(router_mode, RouterMode)
            else _route_enum(
                RouterMode,
                router_mode,
                RouterMode.NORMAL,
            )
        ),
        session_active=_route_bool(
            session_active,
            True,
        ),
        ui_locked=_route_bool(ui_locked),
    )

    definition = get_route_definition(
        normalized,
        routes,
    )

    access = evaluate_route_access(
        normalized,
        context,
        routes,
    )

    resolution = resolve_route(
        normalized,
        context,
        routes,
    )

    return {
        "requested_route": normalized,

        "exists": definition is not None,

        "route_type": (
            definition.route_type.value
            if definition
            else RouteType.UNKNOWN.value
        ),

        "route_status": (
            definition.status.value
            if definition
            else RouteStatus.UNKNOWN.value
        ),

        "requires_login": (
            definition.requires_login
            if definition
            else None
        ),

        "requires_plus": (
            definition.requires_plus
            if definition
            else None
        ),

        "access": access.value,

        "allowed": resolution.allowed,

        "resolved_route": resolution.resolved_route,

        "redirected": resolution.redirected,

        "redirect_route": resolution.redirect_route,

        "reason": resolution.reason,

        "workspace": route_to_workspace(
            normalized
        ),

        "ui_only": True,
    }


# ---------------------------------------------------------------------------
# SAFE ROUTE SELECTION
# ---------------------------------------------------------------------------

def select_safe_route(
    requested_route: Any,
    *,
    authenticated: bool = False,
    plus_enabled: bool = False,
) -> str:
    """
    Return the route the presentation layer should display.

    This helper never grants authority.
    """
    resolution = resolve_ui_route(
        requested_route,
        authenticated=authenticated,
        plus_enabled=plus_enabled,
    )

    return resolution.resolved_route


# ---------------------------------------------------------------------------
# ROUTER STATE UPDATE HELPERS
# ---------------------------------------------------------------------------

def set_router_session_state(
    router: UIRouter,
    *,
    authenticated: Optional[bool] = None,
    plus_enabled: Optional[bool] = None,
    session_active: Optional[bool] = None,
) -> RouterSnapshot:
    """
    Update already-established presentation session state.
    """
    if authenticated is not None:
        router.set_authenticated(
            _route_bool(authenticated)
        )

    if plus_enabled is not None:
        router.set_plus_enabled(
            _route_bool(plus_enabled)
        )

    if session_active is not None:
        router.state.session_active = _route_bool(
            session_active,
            True,
        )

    return router.snapshot()


def set_router_mode(
    router: UIRouter,
    mode: RouterMode,
) -> RouterSnapshot:
    normalized = (
        mode
        if isinstance(mode, RouterMode)
        else _route_enum(
            RouterMode,
            mode,
            RouterMode.NORMAL,
        )
    )

    router.state.router_mode = normalized

    if normalized == RouterMode.LOCKED:
        router.state.ui_locked = True
        router._record(
            RouterEvent.ROUTER_LOCKED,
            metadata={"source": "set_router_mode"},
        )

    elif normalized == RouterMode.NORMAL:
        router.state.ui_locked = False
        router._record(
            RouterEvent.ROUTER_UNLOCKED,
            metadata={"source": "set_router_mode"},
        )

    return router.snapshot()


# ---------------------------------------------------------------------------
# DEFAULT ROUTER DIAGNOSTICS
# ---------------------------------------------------------------------------

def default_router_health() -> RouterHealth:
    return build_router_health(
        get_ui_router()
    )


def validate_default_router() -> Dict[str, Any]:
    router = get_ui_router()

    integrity = validate_router_integrity(
        router
    )

    health = build_router_health(
        router
    )

    return {
        "valid": integrity["valid"],
        "operational": health.operational,

        "engine": ROUTER_ENGINE,
        "version": ROUTER_VERSION,

        "integrity": integrity,
        "health": serialize_router_health(
            health
        ),

        "ui_only": True,
        "d13_authority": False,
        "risk_authority": False,
        "cas_authority": False,
        "execution_authority": False,
    }


# ---------------------------------------------------------------------------
# ROUTER RESET
# ---------------------------------------------------------------------------

def reset_ui_router() -> UIRouter:
    """
    Recreate the default presentation router.

    This only resets UI routing state.
    It does not reset market, intelligence, decision,
    risk, CAS, execution, account or financial state.
    """
    global _DEFAULT_ROUTER

    _DEFAULT_ROUTER = UIRouter()

    return _DEFAULT_ROUTER


# ---------------------------------------------------------------------------
# ROUTER CONTRACT MANIFEST
# ---------------------------------------------------------------------------

def router_contract_manifest() -> Dict[str, Any]:
    return {
        "engine": ROUTER_ENGINE,
        "version": ROUTER_VERSION,
        "name": ROUTER_NAME,

        "responsibilities": [
            "route_identity",
            "route_registry",
            "route_resolution",
            "access_state",
            "navigation",
            "redirects",
            "workspace_mapping",
            "navigation_history",
            "route_events",
            "ui_route_diagnostics",
        ],

        "forbidden_authority": [
            "authentication",
            "credentials",
            "security",
            "market_data",
            "evidence",
            "market_context",
            "intelligence",
            "decision",
            "d13",
            "risk",
            "cas",
            "execution",
            "orders",
            "positions",
            "billing",
            "subscription",
            "entitlement",
            "upstream_mutation",
        ],

        "route_count": len(
            DEFAULT_ROUTES
        ),

        "public_routes": list(
            PUBLIC_ROUTES
        ),

        "authenticated_routes": list(
            AUTHENTICATED_ROUTES
        ),

        "plus_routes": list(
            PLUS_ROUTES
        ),

        "ui_only": True,
    }


# ---------------------------------------------------------------------------
# FINAL MODULE CHECK
# ---------------------------------------------------------------------------

def router_module_check() -> Dict[str, Any]:
    """
    Static/module-level health check.

    This checks router architecture and contracts only.
    It does not claim market or trading readiness.
    """
    registry = validate_route_registry()
    authority = validate_router_authority()

    required_exports = {
        "UIRouter",
        "RouteDefinition",
        "RouteResolution",
        "NavigationRequest",
        "NavigationResult",
        "resolve_route",
        "process_navigation",
        "router_operational_check",
        "validate_router_integrity",
    }

    missing_exports = sorted(
        name
        for name in required_exports
        if name not in __all__
    )

    errors = (
        registry["errors"]
        + authority["errors"]
    )

    if missing_exports:
        errors.extend(
            f"Missing public export: {name}"
            for name in missing_exports
        )

    return {
        "engine": ROUTER_ENGINE,
        "version": ROUTER_VERSION,

        "module_valid": not errors,

        "route_registry_valid": registry["valid"],
        "authority_valid": authority["valid"],

        "missing_exports": missing_exports,

        "errors": errors,
        "warnings": (
            registry["warnings"]
        ),

        "ui_only": True,

        "intelligence_generation": False,
        "decision_generation": False,
        "d13_modification": False,
        "risk_generation": False,
        "risk_override": False,
        "cas_generation": False,
        "cas_bypass": False,
        "execution": False,
        "order_mutation": False,
        "position_mutation": False,
    }