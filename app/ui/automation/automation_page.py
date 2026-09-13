from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


# ============================================================
# ROBOMLM_PLUS — AUTOMATION PAGE
# Presentation / orchestration surface for AUTOROBOMLM.
# ============================================================

AUTOMATION_PAGE_ENGINE = "ROBOMLM_PLUS_UI_AUTOMATION"
AUTOMATION_PAGE_VERSION = "1.0"
AUTOMATION_PAGE_NAME = "Automation"
AUTOMATION_PAGE_TITLE = "AUTOROBOMLM"
AUTOMATION_PAGE_DESCRIPTION = (
    "ROBOMLM automation workspace for presenting automation state, "
    "readiness, controls and execution-system status."
)
AUTOMATION_ROUTE = "/automation"


# ------------------------------------------------------------
# UI AUTHORITY
# ------------------------------------------------------------

AUTOMATION_UI_AUTHORITY: Dict[str, bool] = {
    # Presentation authority
    "automation_presentation": True,
    "automation_status_presentation": True,
    "automation_summary_presentation": True,
    "automation_navigation": True,
    "automation_control_presentation": True,
    "automation_readiness_presentation": True,
    "automation_event_presentation": True,
    "display_configuration": True,

    # Forbidden authority
    "automation_mutation_authority": False,
    "execution_authority": False,
    "order_authority": False,
    "position_authority": False,
    "broker_authority": False,
    "market_data_authority": False,
    "evidence_authority": False,
    "market_context_authority": False,
    "intelligence_authority": False,
    "decision_authority": False,
    "d13_authority": False,
    "risk_authority": False,
    "cas_authority": False,
    "d13_modification": False,
    "risk_override": False,
    "cas_bypass": False,
    "order_mutation": False,
    "position_mutation": False,
    "upstream_mutation": False,
}


# ------------------------------------------------------------
# ENUMS
# ------------------------------------------------------------

class AutomationPageStatus(str, Enum):
    LOADING = "LOADING"
    READY = "READY"
    DEGRADED = "DEGRADED"
    LOCKED = "LOCKED"
    DISABLED = "DISABLED"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class AutomationPresentationMode(str, Enum):
    OVERVIEW = "OVERVIEW"
    STATUS = "STATUS"
    READINESS = "READINESS"
    CONTROLS = "CONTROLS"
    EVENTS = "EVENTS"
    HISTORY = "HISTORY"
    UNKNOWN = "UNKNOWN"


class AutomationState(str, Enum):
    UNKNOWN = "UNKNOWN"
    DISABLED = "DISABLED"
    ARMED = "ARMED"
    READY = "READY"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"
    BLOCKED = "BLOCKED"
    ERROR = "ERROR"


class AutomationReadiness(str, Enum):
    UNKNOWN = "UNKNOWN"
    NOT_READY = "NOT_READY"
    READY = "READY"
    BLOCKED = "BLOCKED"
    DEGRADED = "DEGRADED"


class AutomationControlState(str, Enum):
    UNKNOWN = "UNKNOWN"
    AVAILABLE = "AVAILABLE"
    DISABLED = "DISABLED"
    LOCKED = "LOCKED"
    RESTRICTED = "RESTRICTED"


class AutomationPriority(str, Enum):
    NORMAL = "NORMAL"
    IMPORTANT = "IMPORTANT"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AutomationBadgeType(str, Enum):
    STATUS = "STATUS"
    READINESS = "READINESS"
    MODE = "MODE"
    SAFETY = "SAFETY"
    CUSTOM = "CUSTOM"


class AutomationControlType(str, Enum):
    UNKNOWN = "UNKNOWN"
    VIEW = "VIEW"
    ENABLE = "ENABLE"
    DISABLE = "DISABLE"
    PAUSE = "PAUSE"
    RESUME = "RESUME"
    ARM = "ARM"
    DISARM = "DISARM"
    STOP = "STOP"


# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------

def _automation_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _automation_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, str):
        value = value.strip().lower()
        if value in {"true", "1", "yes", "on", "enabled"}:
            return True
        if value in {"false", "0", "no", "off", "disabled"}:
            return False
    return bool(value)


def _automation_enum(enum_cls: Any, value: Any, default: Any) -> Any:
    if isinstance(value, enum_cls):
        return value
    try:
        return enum_cls(value)
    except (TypeError, ValueError):
        return default


def _automation_now() -> datetime:
    return datetime.now(timezone.utc)


# ------------------------------------------------------------
# VIEW CONTRACTS
# ------------------------------------------------------------

@dataclass
class AutomationIdentityView:
    user_id: str = ""
    display_name: str = ""
    email: str = ""
    authenticated: bool = False
    plus_enabled: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AutomationStatusView:
    state: AutomationState = AutomationState.UNKNOWN
    readiness: AutomationReadiness = AutomationReadiness.UNKNOWN
    control_state: AutomationControlState = AutomationControlState.UNKNOWN
    status_message: str = ""
    readiness_message: str = ""
    running: bool = False
    paused: bool = False
    blocked: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AutomationEventView:
    event_id: str = ""
    event_type: str = ""
    timestamp: Optional[datetime] = None
    severity: str = "INFO"
    message: str = ""
    source: str = ""
    visible: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AutomationControlView:
    control_id: str = ""
    label: str = ""
    description: str = ""
    control_type: AutomationControlType = AutomationControlType.UNKNOWN
    state: AutomationControlState = AutomationControlState.UNKNOWN
    enabled: bool = False
    visible: bool = True
    requires_plus: bool = False
    priority: AutomationPriority = AutomationPriority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AutomationBadge:
    badge_type: AutomationBadgeType = AutomationBadgeType.STATUS
    label: str = ""
    value: str = ""
    priority: AutomationPriority = AutomationPriority.NORMAL
    visible: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AutomationAction:
    action_id: str = ""
    label: str = ""
    route: str = ""
    enabled: bool = True
    visible: bool = True
    requires_authentication: bool = True
    requires_plus: bool = False
    priority: AutomationPriority = AutomationPriority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AutomationSummaryView:
    state: AutomationState = AutomationState.UNKNOWN
    readiness: AutomationReadiness = AutomationReadiness.UNKNOWN
    event_count: int = 0
    visible_event_count: int = 0
    control_count: int = 0
    enabled_control_count: int = 0
    running: bool = False
    paused: bool = False
    blocked: bool = False
    authenticated: bool = False
    plus_enabled: bool = False
    priority: AutomationPriority = AutomationPriority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AutomationPageRequest:
    user_id: str = ""
    mode: AutomationPresentationMode = AutomationPresentationMode.OVERVIEW
    authenticated: bool = False
    plus_enabled: bool = False
    page_status: AutomationPageStatus = AutomationPageStatus.UNKNOWN
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AutomationPageView:
    page_name: str = AUTOMATION_PAGE_NAME
    page_title: str = AUTOMATION_PAGE_TITLE
    route: str = AUTOMATION_ROUTE
    status: AutomationPageStatus = AutomationPageStatus.UNKNOWN
    mode: AutomationPresentationMode = AutomationPresentationMode.OVERVIEW

    identity: AutomationIdentityView = field(
        default_factory=AutomationIdentityView
    )
    status_view: AutomationStatusView = field(
        default_factory=AutomationStatusView
    )
    events: List[AutomationEventView] = field(default_factory=list)
    controls: List[AutomationControlView] = field(default_factory=list)
    badges: List[AutomationBadge] = field(default_factory=list)
    actions: List[AutomationAction] = field(default_factory=list)
    summary: AutomationSummaryView = field(
        default_factory=AutomationSummaryView
    )

    authenticated: bool = False
    plus_enabled: bool = False
    generated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# ------------------------------------------------------------
# DEFAULT NAVIGATION ACTIONS
# ------------------------------------------------------------

DEFAULT_AUTOMATION_ACTIONS: Sequence[AutomationAction] = (
    AutomationAction(
        action_id="automation_overview",
        label="Overview",
        route="/automation",
        priority=AutomationPriority.NORMAL,
    ),
    AutomationAction(
        action_id="automation_status",
        label="Status",
        route="/automation/status",
        priority=AutomationPriority.NORMAL,
    ),
    AutomationAction(
        action_id="automation_readiness",
        label="Readiness",
        route="/automation/readiness",
        priority=AutomationPriority.IMPORTANT,
    ),
    AutomationAction(
        action_id="automation_controls",
        label="Controls",
        route="/automation/controls",
        priority=AutomationPriority.HIGH,
    ),
    AutomationAction(
        action_id="automation_events",
        label="Events",
        route="/automation/events",
        priority=AutomationPriority.NORMAL,
    ),
    AutomationAction(
        action_id="automation_history",
        label="History",
        route="/automation/history",
        priority=AutomationPriority.NORMAL,
    ),
)


# ------------------------------------------------------------
# NORMALIZATION
# ------------------------------------------------------------

def normalize_automation_identity(
    identity: Optional[AutomationIdentityView] = None,
) -> AutomationIdentityView:
    if identity is None:
        return AutomationIdentityView()

    return AutomationIdentityView(
        user_id=_automation_text(identity.user_id),
        display_name=_automation_text(identity.display_name),
        email=_automation_text(identity.email),
        authenticated=_automation_bool(identity.authenticated),
        plus_enabled=_automation_bool(identity.plus_enabled),
        metadata=dict(identity.metadata or {}),
    )


def normalize_automation_status(
    status: Optional[AutomationStatusView] = None,
) -> AutomationStatusView:
    if status is None:
        return AutomationStatusView()

    state = _automation_enum(
        AutomationState,
        status.state,
        AutomationState.UNKNOWN,
    )
    readiness = _automation_enum(
        AutomationReadiness,
        status.readiness,
        AutomationReadiness.UNKNOWN,
    )
    control_state = _automation_enum(
        AutomationControlState,
        status.control_state,
        AutomationControlState.UNKNOWN,
    )

    return AutomationStatusView(
        state=state,
        readiness=readiness,
        control_state=control_state,
        status_message=_automation_text(status.status_message),
        readiness_message=_automation_text(status.readiness_message),
        running=_automation_bool(
            status.running,
            state == AutomationState.RUNNING,
        ),
        paused=_automation_bool(
            status.paused,
            state == AutomationState.PAUSED,
        ),
        blocked=_automation_bool(
            status.blocked,
            state == AutomationState.BLOCKED,
        ),
        metadata=dict(status.metadata or {}),
    )


def normalize_automation_events(
    events: Optional[Sequence[AutomationEventView]] = None,
) -> List[AutomationEventView]:
    result: List[AutomationEventView] = []

    for event in events or []:
        if not isinstance(event, AutomationEventView):
            continue

        result.append(
            AutomationEventView(
                event_id=_automation_text(event.event_id),
                event_type=_automation_text(event.event_type),
                timestamp=event.timestamp,
                severity=_automation_text(event.severity, "INFO"),
                message=_automation_text(event.message),
                source=_automation_text(event.source),
                visible=_automation_bool(event.visible, True),
                metadata=dict(event.metadata or {}),
            )
        )

    return result


def normalize_automation_controls(
    controls: Optional[Sequence[AutomationControlView]] = None,
) -> List[AutomationControlView]:
    result: List[AutomationControlView] = []

    for control in controls or []:
        if not isinstance(control, AutomationControlView):
            continue

        result.append(
            AutomationControlView(
                control_id=_automation_text(control.control_id),
                label=_automation_text(control.label),
                description=_automation_text(control.description),
                control_type=_automation_enum(
                    AutomationControlType,
                    control.control_type,
                    AutomationControlType.UNKNOWN,
                ),
                state=_automation_enum(
                    AutomationControlState,
                    control.state,
                    AutomationControlState.UNKNOWN,
                ),
                enabled=_automation_bool(control.enabled),
                visible=_automation_bool(control.visible, True),
                requires_plus=_automation_bool(control.requires_plus),
                priority=_automation_enum(
                    AutomationPriority,
                    control.priority,
                    AutomationPriority.NORMAL,
                ),
                metadata=dict(control.metadata or {}),
            )
        )

    return result
# ============================================================
# SOURCE CONTRACT
# ============================================================

@dataclass(frozen=True)
class AutomationSourceState:
    """
    Upstream automation truth source.

    UI consumes this state.
    UI never owns automation execution authority.
    """

    identity: AutomationIdentityView = field(
        default_factory=AutomationIdentityView
    )

    status: AutomationStatusView = field(
        default_factory=AutomationStatusView
    )

    events: List[AutomationEventView] = field(
        default_factory=list
    )

    controls: List[AutomationControlView] = field(
        default_factory=list
    )

    source_available: bool = False

    source_errors: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# SOURCE NORMALIZATION
# ============================================================

def normalize_automation_source_state(
    source: Optional[AutomationSourceState],
) -> AutomationSourceState:

    if source is None:
        return AutomationSourceState(
            identity=AutomationIdentityView(),
            status=AutomationStatusView(),
            events=[],
            controls=[],
            source_available=False,
            source_errors=[
                "AUTOMATION_SOURCE_NOT_PROVIDED"
            ],
            metadata={
                "presentation_only": True,
            },
        )

    return AutomationSourceState(
        identity=normalize_automation_identity(
            source.identity
        ),
        status=normalize_automation_status(
            source.status
        ),
        events=normalize_automation_events(
            source.events
        ),
        controls=normalize_automation_controls(
            source.controls
        ),
        source_available=_automation_bool(
            source.source_available
        ),
        source_errors=[
            _automation_text(error)
            for error in (
                source.source_errors or []
            )
            if _automation_text(error)
        ],
        metadata=dict(source.metadata or {}),
    )


# ============================================================
# PAGE STATUS EVALUATION
# ============================================================

def evaluate_automation_page_status(
    source: AutomationSourceState,
) -> AutomationPageStatus:

    identity = source.identity

    if not identity.authenticated:
        return AutomationPageStatus.LOCKED

    if not source.source_available:
        return AutomationPageStatus.DEGRADED

    if source.source_errors:
        return AutomationPageStatus.DEGRADED

    if source.status.state == AutomationState.ERROR:
        return AutomationPageStatus.ERROR

    if source.status.state == AutomationState.BLOCKED:
        return AutomationPageStatus.DEGRADED

    return AutomationPageStatus.READY


# ============================================================
# SUMMARY BUILDER
# ============================================================

def build_automation_summary(
    identity: AutomationIdentityView,
    status: AutomationStatusView,
    events: Sequence[AutomationEventView],
    controls: Sequence[AutomationControlView],
) -> AutomationSummaryView:

    visible_events = [
        event
        for event in events
        if event.visible
    ]

    enabled_controls = [
        control
        for control in controls
        if control.enabled
    ]

    priority = AutomationPriority.NORMAL

    if status.blocked:
        priority = AutomationPriority.CRITICAL

    elif status.state == AutomationState.ERROR:
        priority = AutomationPriority.CRITICAL

    elif status.state == AutomationState.RUNNING:
        priority = AutomationPriority.HIGH

    elif status.readiness == (
        AutomationReadiness.READY
    ):
        priority = AutomationPriority.IMPORTANT

    return AutomationSummaryView(
        state=status.state,
        readiness=status.readiness,

        event_count=len(events),
        visible_event_count=len(
            visible_events
        ),

        control_count=len(controls),
        enabled_control_count=len(
            enabled_controls
        ),

        running=status.running,
        paused=status.paused,
        blocked=status.blocked,

        authenticated=identity.authenticated,
        plus_enabled=identity.plus_enabled,

        priority=priority,

        metadata={
            "presentation_only": True,
        },
    )


# ============================================================
# BADGES
# ============================================================

def build_automation_badges(
    status: AutomationStatusView,
) -> List[AutomationBadge]:

    badges: List[
        AutomationBadge
    ] = []

    badges.append(
        AutomationBadge(
            badge_type=AutomationBadgeType.STATUS,
            label="State",
            value=status.state.value,
            priority=AutomationPriority.NORMAL,
        )
    )

    badges.append(
        AutomationBadge(
            badge_type=AutomationBadgeType.READINESS,
            label="Readiness",
            value=status.readiness.value,
            priority=AutomationPriority.IMPORTANT,
        )
    )

    if status.running:
        badges.append(
            AutomationBadge(
                badge_type=AutomationBadgeType.MODE,
                label="Mode",
                value="RUNNING",
                priority=AutomationPriority.HIGH,
            )
        )

    if status.paused:
        badges.append(
            AutomationBadge(
                badge_type=AutomationBadgeType.MODE,
                label="Mode",
                value="PAUSED",
                priority=AutomationPriority.IMPORTANT,
            )
        )

    if status.blocked:
        badges.append(
            AutomationBadge(
                badge_type=AutomationBadgeType.SAFETY,
                label="Safety",
                value="BLOCKED",
                priority=AutomationPriority.CRITICAL,
            )
        )

    return badges


# ============================================================
# ACTIONS
# ============================================================

def get_automation_actions(
    authenticated: bool,
    plus_enabled: bool,
) -> List[AutomationAction]:

    authenticated = _automation_bool(
        authenticated
    )

    plus_enabled = _automation_bool(
        plus_enabled
    )

    actions: List[
        AutomationAction
    ] = []

    for action in (
        DEFAULT_AUTOMATION_ACTIONS
    ):
        actions.append(
            AutomationAction(
                action_id=action.action_id,
                label=action.label,
                route=action.route,
                enabled=authenticated,
                visible=True,
                requires_authentication=True,
                requires_plus=False,
                priority=action.priority,
                metadata={
                    "presentation_only": True,
                },
            )
        )

    if plus_enabled:
        actions.append(
            AutomationAction(
                action_id="automation_plus",
                label="Automation Plus",
                route="/automation/plus",
                enabled=True,
                visible=True,
                requires_authentication=True,
                requires_plus=True,
                priority=AutomationPriority.HIGH,
                metadata={
                    "plus_feature": True,
                },
            )
        )

    return actions


# ============================================================
# DISPLAY HELPERS
# ============================================================

def resolve_automation_display_name(
    identity: AutomationIdentityView,
) -> str:

    if identity.display_name:
        return identity.display_name

    if identity.email:
        return identity.email

    return "Automation"


def build_automation_status_message(
    status: AutomationStatusView,
) -> str:

    state = status.state

    if state == AutomationState.RUNNING:
        return (
            "Automation engine currently running."
        )

    if state == AutomationState.PAUSED:
        return (
            "Automation engine currently paused."
        )

    if state == AutomationState.BLOCKED:
        return (
            "Automation blocked by safety controls."
        )

    if state == AutomationState.READY:
        return (
            "Automation ready for execution layer."
        )

    if state == AutomationState.ARMED:
        return (
            "Automation armed and waiting."
        )

    if state == AutomationState.ERROR:
        return (
            "Automation reported an error."
        )

    if state == AutomationState.DISABLED:
        return (
            "Automation disabled."
        )

    return (
        "Automation status unavailable."
    )


def build_automation_readiness_message(
    status: AutomationStatusView,
) -> str:

    readiness = status.readiness

    if readiness == (
        AutomationReadiness.READY
    ):
        return (
            "Readiness checks passed."
        )

    if readiness == (
        AutomationReadiness.BLOCKED
    ):
        return (
            "Readiness blocked."
        )

    if readiness == (
        AutomationReadiness.DEGRADED
    ):
        return (
            "Readiness partially available."
        )

    if readiness == (
        AutomationReadiness.NOT_READY
    ):
        return (
            "Readiness requirements incomplete."
        )

    return (
        "Readiness state unavailable."
    )


# ============================================================
# MODE FILTERING
# ============================================================

AUTOMATION_MODE_FILTERS: Dict[
    AutomationPresentationMode,
    str,
] = {
    AutomationPresentationMode.OVERVIEW:
        "overview",

    AutomationPresentationMode.STATUS:
        "status",

    AutomationPresentationMode.READINESS:
        "readiness",

    AutomationPresentationMode.CONTROLS:
        "controls",

    AutomationPresentationMode.EVENTS:
        "events",

    AutomationPresentationMode.HISTORY:
        "history",
}


def filter_automation_events(
    events: Sequence[
        AutomationEventView
    ],
    mode: AutomationPresentationMode,
) -> List[AutomationEventView]:

    mode = _automation_enum(
        AutomationPresentationMode,
        mode,
        AutomationPresentationMode.OVERVIEW,
    )

    if mode == (
        AutomationPresentationMode.EVENTS
    ):
        return [
            event
            for event in events
            if event.visible
        ]

    return [
        event
        for event in events
        if event.visible
    ]


def filter_automation_controls(
    controls: Sequence[
        AutomationControlView
    ],
    mode: AutomationPresentationMode,
) -> List[AutomationControlView]:

    mode = _automation_enum(
        AutomationPresentationMode,
        mode,
        AutomationPresentationMode.OVERVIEW,
    )

    if mode == (
        AutomationPresentationMode.CONTROLS
    ):
        return [
            control
            for control in controls
            if control.visible
        ]

    return [
        control
        for control in controls
        if control.visible
    ]
# ============================================================
# PAGE COMPOSITION CONTRACT
# ============================================================

@dataclass(frozen=True)
class AutomationPageComposition:
    page: AutomationPageView

    summary: AutomationSummaryView

    events: List[AutomationEventView] = field(
        default_factory=list
    )

    controls: List[AutomationControlView] = field(
        default_factory=list
    )

    badges: List[AutomationBadge] = field(
        default_factory=list
    )

    actions: List[AutomationAction] = field(
        default_factory=list
    )

    generated_at: datetime = field(
        default_factory=_automation_now
    )

    warnings: List[str] = field(
        default_factory=list
    )

    errors: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# PAGE COMPOSER
# ============================================================

def compose_automation_page(
    source: Optional[
        AutomationSourceState
    ] = None,
    mode: AutomationPresentationMode = (
        AutomationPresentationMode.OVERVIEW
    ),
) -> AutomationPageComposition:

    source = normalize_automation_source_state(
        source
    )

    mode = _automation_enum(
        AutomationPresentationMode,
        mode,
        AutomationPresentationMode.OVERVIEW,
    )

    identity = source.identity
    status = source.status

    page_status = (
        evaluate_automation_page_status(
            source
        )
    )

    status.status_message = (
        build_automation_status_message(
            status
        )
    )

    status.readiness_message = (
        build_automation_readiness_message(
            status
        )
    )

    filtered_events = (
        filter_automation_events(
            source.events,
            mode,
        )
    )

    filtered_controls = (
        filter_automation_controls(
            source.controls,
            mode,
        )
    )

    summary = build_automation_summary(
        identity=identity,
        status=status,
        events=filtered_events,
        controls=filtered_controls,
    )

    badges = build_automation_badges(
        status
    )

    actions = get_automation_actions(
        authenticated=identity.authenticated,
        plus_enabled=identity.plus_enabled,
    )

    page = AutomationPageView(
        page_name=AUTOMATION_PAGE_NAME,
        page_title=AUTOMATION_PAGE_TITLE,
        route=AUTOMATION_ROUTE,

        status=page_status,
        mode=mode,

        identity=identity,
        status_view=status,

        events=filtered_events,
        controls=filtered_controls,

        badges=badges,
        actions=actions,

        summary=summary,

        authenticated=(
            identity.authenticated
        ),
        plus_enabled=(
            identity.plus_enabled
        ),

        generated_at=_automation_now(),

        metadata={
            "presentation_only": True,
            "automation_mutation": False,
            "execution": False,
            "d13_modification": False,
            "risk_override": False,
            "cas_bypass": False,
        },
    )

    warnings: List[str] = []
    errors: List[str] = []

    if not source.source_available:
        warnings.append(
            "AUTOMATION_SOURCE_UNAVAILABLE"
        )

    errors.extend(
        source.source_errors
    )

    return AutomationPageComposition(
        page=page,
        summary=summary,
        events=filtered_events,
        controls=filtered_controls,
        badges=badges,
        actions=actions,

        warnings=warnings,
        errors=errors,

        metadata={
            "presentation_only": True,
            "automation_mutation": False,
            "execution": False,
            "upstream_mutation": False,
        },
    )


# ============================================================
# INTERACTION MODEL
# ============================================================

class AutomationInteraction(
    str,
    Enum,
):
    OPEN_OVERVIEW = "OPEN_OVERVIEW"
    OPEN_STATUS = "OPEN_STATUS"
    OPEN_READINESS = "OPEN_READINESS"
    OPEN_CONTROLS = "OPEN_CONTROLS"
    OPEN_EVENTS = "OPEN_EVENTS"
    OPEN_HISTORY = "OPEN_HISTORY"

    REFRESH = "REFRESH"

    NONE = "NONE"


AUTOMATION_INTERACTION_ROUTES: Dict[
    AutomationInteraction,
    str,
] = {
    AutomationInteraction.OPEN_OVERVIEW:
        "/automation",

    AutomationInteraction.OPEN_STATUS:
        "/automation/status",

    AutomationInteraction.OPEN_READINESS:
        "/automation/readiness",

    AutomationInteraction.OPEN_CONTROLS:
        "/automation/controls",

    AutomationInteraction.OPEN_EVENTS:
        "/automation/events",

    AutomationInteraction.OPEN_HISTORY:
        "/automation/history",
}


def normalize_automation_interaction(
    interaction: Any,
) -> AutomationInteraction:

    return _automation_enum(
        AutomationInteraction,
        interaction,
        AutomationInteraction.NONE,
    )


# ============================================================
# PAGE STATE
# ============================================================

@dataclass
class AutomationPageState:
    user_id: str = ""

    authenticated: bool = False
    plus_enabled: bool = False

    initialized: bool = False
    ready: bool = False

    current_route: str = (
        AUTOMATION_ROUTE
    )

    mode: AutomationPresentationMode = (
        AutomationPresentationMode.OVERVIEW
    )

    status: AutomationPageStatus = (
        AutomationPageStatus.UNKNOWN
    )

    interaction_count: int = 0
    refresh_count: int = 0

    last_interaction: (
        AutomationInteraction
    ) = AutomationInteraction.NONE

    last_error: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def create_automation_page_state(
    user_id: str = "",
    authenticated: bool = False,
    plus_enabled: bool = False,
) -> AutomationPageState:

    authenticated = _automation_bool(
        authenticated
    )

    return AutomationPageState(
        user_id=_automation_text(
            user_id
        ),
        authenticated=authenticated,
        plus_enabled=_automation_bool(
            plus_enabled
        ),

        initialized=False,
        ready=False,

        current_route=AUTOMATION_ROUTE,

        mode=(
            AutomationPresentationMode.OVERVIEW
        ),

        status=(
            AutomationPageStatus.LOADING
            if authenticated
            else AutomationPageStatus.LOCKED
        ),

        metadata={
            "presentation_only": True,
        },
    )


# ============================================================
# ROUTING
# ============================================================

AUTOMATION_ROUTE_MODES: Dict[
    str,
    AutomationPresentationMode,
] = {
    "/automation":
        AutomationPresentationMode.OVERVIEW,

    "/automation/status":
        AutomationPresentationMode.STATUS,

    "/automation/readiness":
        AutomationPresentationMode.READINESS,

    "/automation/controls":
        AutomationPresentationMode.CONTROLS,

    "/automation/events":
        AutomationPresentationMode.EVENTS,

    "/automation/history":
        AutomationPresentationMode.HISTORY,
}


def route_to_automation_mode(
    route: str,
) -> AutomationPresentationMode:

    route = _automation_text(
        route,
        AUTOMATION_ROUTE,
    )

    return AUTOMATION_ROUTE_MODES.get(
        route,
        AutomationPresentationMode.OVERVIEW,
    )


def evaluate_automation_route_access(
    route: str,
    authenticated: bool,
) -> tuple[bool, str]:

    route = _automation_text(route)

    if route not in (
        AUTOMATION_ROUTE_MODES
    ):
        return (
            False,
            "ROUTE_NOT_FOUND",
        )

    if not authenticated:
        return (
            False,
            "AUTH_REQUIRED",
        )

    return (
        True,
        "ALLOWED",
    )


# ============================================================
# INTERACTION RESULT
# ============================================================

@dataclass(frozen=True)
class AutomationInteractionResult:
    interaction: (
        AutomationInteraction
    ) = AutomationInteraction.NONE

    requested_route: str = ""
    resolved_route: str = ""

    allowed: bool = False
    reason: str = ""

    mode: AutomationPresentationMode = (
        AutomationPresentationMode.OVERVIEW
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def resolve_automation_interaction(
    interaction: AutomationInteraction,
    authenticated: bool,
) -> AutomationInteractionResult:

    interaction = (
        normalize_automation_interaction(
            interaction
        )
    )

    if (
        interaction
        == AutomationInteraction.NONE
    ):
        return AutomationInteractionResult(
            interaction=interaction,
            allowed=False,
            reason="NO_INTERACTION",
        )

    if (
        interaction
        == AutomationInteraction.REFRESH
    ):
        return AutomationInteractionResult(
            interaction=interaction,
            requested_route=
                AUTOMATION_ROUTE,
            resolved_route=
                AUTOMATION_ROUTE,
            allowed=authenticated,
            reason=(
                "ALLOWED"
                if authenticated
                else "AUTH_REQUIRED"
            ),
            mode=(
                AutomationPresentationMode.OVERVIEW
            ),
        )

    route = (
        AUTOMATION_INTERACTION_ROUTES
        .get(interaction)
    )

    if not route:
        return AutomationInteractionResult(
            interaction=interaction,
            allowed=False,
            reason="ROUTE_NOT_MAPPED",
        )

    allowed, reason = (
        evaluate_automation_route_access(
            route=route,
            authenticated=authenticated,
        )
    )

    return AutomationInteractionResult(
        interaction=interaction,
        requested_route=route,
        resolved_route=(
            route
            if allowed
            else AUTOMATION_ROUTE
        ),
        allowed=allowed,
        reason=reason,
        mode=route_to_automation_mode(
            route
        ),
        metadata={
            "presentation_only": True,
        },
    )
# ============================================================
# PAGE CONTROLLER
# ============================================================

class AutomationPageController:

    def __init__(
        self,
        state: Optional[
            AutomationPageState
        ] = None,
    ) -> None:

        self._state = (
            state
            if state is not None
            else create_automation_page_state()
        )

        self._last_composition: Optional[
            AutomationPageComposition
        ] = None

    @property
    def state(
        self,
    ) -> AutomationPageState:
        return self._state

    @property
    def last_composition(
        self,
    ) -> Optional[
        AutomationPageComposition
    ]:
        return self._last_composition

    @property
    def current_route(
        self,
    ) -> str:
        return self._state.current_route

    @property
    def current_mode(
        self,
    ) -> AutomationPresentationMode:
        return self._state.mode

    @property
    def status(
        self,
    ) -> AutomationPageStatus:
        return self._state.status

    def initialize(
        self,
        source: AutomationSourceState,
    ) -> AutomationPageComposition:

        source = (
            normalize_automation_source_state(
                source
            )
        )

        self._state.user_id = (
            source.identity.user_id
        )

        self._state.authenticated = (
            source.identity.authenticated
        )

        self._state.plus_enabled = (
            source.identity.plus_enabled
        )

        self._state.initialized = True

        composition = self.compose(
            source=source
        )

        self._state.ready = (
            composition.page.status
            == AutomationPageStatus.READY
        )

        self._state.status = (
            composition.page.status
        )

        return composition

    def compose(
        self,
        source: AutomationSourceState,
    ) -> AutomationPageComposition:

        composition = (
            compose_automation_page(
                source=source,
                mode=self._state.mode,
            )
        )

        self._last_composition = (
            composition
        )

        self._state.status = (
            composition.page.status
        )

        return composition

    def navigate(
        self,
        route: str,
    ) -> AutomationInteractionResult:

        allowed, reason = (
            evaluate_automation_route_access(
                route=route,
                authenticated=(
                    self._state.authenticated
                ),
            )
        )

        if not allowed:
            return (
                AutomationInteractionResult(
                    requested_route=route,
                    resolved_route=(
                        self._state.current_route
                    ),
                    allowed=False,
                    reason=reason,
                    mode=self._state.mode,
                )
            )

        self._state.current_route = route

        self._state.mode = (
            route_to_automation_mode(
                route
            )
        )

        self._state.interaction_count += 1

        return AutomationInteractionResult(
            requested_route=route,
            resolved_route=route,
            allowed=True,
            reason="ALLOWED",
            mode=self._state.mode,
        )

    def apply_interaction(
        self,
        interaction: (
            AutomationInteraction
        ),
    ) -> AutomationInteractionResult:

        result = (
            resolve_automation_interaction(
                interaction=interaction,
                authenticated=(
                    self._state.authenticated
                ),
            )
        )

        if result.allowed:
            self._state.interaction_count += 1
            self._state.last_interaction = (
                interaction
            )

            self._state.current_route = (
                result.resolved_route
            )

            self._state.mode = (
                result.mode
            )

        return result


# ============================================================
# SNAPSHOT CONTRACT
# ============================================================

@dataclass(frozen=True)
class AutomationPageSnapshot:

    state: AutomationPageState

    composition: (
        AutomationPageComposition
    )

    generated_at: datetime = field(
        default_factory=_automation_now
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def build_automation_page_snapshot(
    controller: AutomationPageController,
    source: AutomationSourceState,
) -> AutomationPageSnapshot:

    composition = controller.compose(
        source
    )

    return AutomationPageSnapshot(
        state=controller.state,
        composition=composition,
        metadata={
            "presentation_only": True,
            "execution": False,
            "order_mutation": False,
            "position_mutation": False,
            "d13_modification": False,
        },
    )


# ============================================================
# SERIALIZATION
# ============================================================

def _serialize_automation_value(
    value: Any,
) -> Any:

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            str(key):
            _serialize_automation_value(
                item
            )
            for key, item
            in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            _serialize_automation_value(
                item
            )
            for item in value
        ]

    if hasattr(
        value,
        "__dataclass_fields__",
    ):
        return {
            field_name:
            _serialize_automation_value(
                getattr(
                    value,
                    field_name,
                )
            )
            for field_name
            in value.__dataclass_fields__
        }

    return value


def serialize_automation_page(
    page: AutomationPageView,
) -> Dict[str, Any]:

    return (
        _serialize_automation_value(
            page
        )
    )


def serialize_automation_composition(
    composition:
    AutomationPageComposition,
) -> Dict[str, Any]:

    return (
        _serialize_automation_value(
            composition
        )
    )


def serialize_automation_state(
    state: AutomationPageState,
) -> Dict[str, Any]:

    return (
        _serialize_automation_value(
            state
        )
    )


def serialize_automation_snapshot(
    snapshot:
    AutomationPageSnapshot,
) -> Dict[str, Any]:

    return (
        _serialize_automation_value(
            snapshot
        )
    )


# ============================================================
# VALIDATION
# ============================================================

def validate_automation_page(
    page: AutomationPageView,
) -> List[str]:

    errors: List[str] = []

    if page.page_name != (
        AUTOMATION_PAGE_NAME
    ):
        errors.append(
            "INVALID_PAGE_NAME"
        )

    if page.route != (
        AUTOMATION_ROUTE
    ):
        errors.append(
            "INVALID_PAGE_ROUTE"
        )

    if (
        page.metadata.get(
            "execution"
        ) is True
    ):
        errors.append(
            "EXECUTION_AUTHORITY_FORBIDDEN"
        )

    if (
        page.metadata.get(
            "d13_modification"
        ) is True
    ):
        errors.append(
            "D13_MODIFICATION_FORBIDDEN"
        )

    if (
        page.metadata.get(
            "risk_override"
        ) is True
    ):
        errors.append(
            "RISK_OVERRIDE_FORBIDDEN"
        )

    if (
        page.metadata.get(
            "cas_bypass"
        ) is True
    ):
        errors.append(
            "CAS_BYPASS_FORBIDDEN"
        )

    return errors


def validate_automation_composition(
    composition:
    AutomationPageComposition,
) -> List[str]:

    errors: List[str] = []

    errors.extend(
        validate_automation_page(
            composition.page
        )
    )

    if (
        composition.metadata.get(
            "execution"
        ) is True
    ):
        errors.append(
            "EXECUTION_FORBIDDEN"
        )

    if (
        composition.metadata.get(
            "upstream_mutation"
        ) is True
    ):
        errors.append(
            "UPSTREAM_MUTATION_FORBIDDEN"
        )

    return errors


def validate_automation_state(
    state: AutomationPageState,
) -> List[str]:

    errors: List[str] = []

    if (
        state.interaction_count
        < 0
    ):
        errors.append(
            "NEGATIVE_INTERACTION_COUNT"
        )

    if (
        state.refresh_count
        < 0
    ):
        errors.append(
            "NEGATIVE_REFRESH_COUNT"
        )

    return errors


# ============================================================
# HEALTH CONTRACT
# ============================================================

@dataclass(frozen=True)
class AutomationPageHealth:

    engine: str = (
        AUTOMATION_PAGE_ENGINE
    )

    version: str = (
        AUTOMATION_PAGE_VERSION
    )

    initialized: bool = False
    ready: bool = False

    status: AutomationPageStatus = (
        AutomationPageStatus.UNKNOWN
    )

    validation_errors: List[
        str
    ] = field(
        default_factory=list
    )

    operational: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def build_automation_health(
    controller:
    AutomationPageController,
    composition: Optional[
        AutomationPageComposition
    ] = None,
) -> AutomationPageHealth:

    errors: List[str] = []

    errors.extend(
        validate_automation_state(
            controller.state
        )
    )

    if composition is not None:
        errors.extend(
            validate_automation_composition(
                composition
            )
        )

    operational = (
        controller.state.initialized
        and controller.state.ready
        and not errors
    )

    return AutomationPageHealth(
        initialized=(
            controller.state.initialized
        ),
        ready=(
            controller.state.ready
        ),
        status=(
            controller.state.status
        ),
        validation_errors=errors,
        operational=operational,
        metadata={
            "presentation_only": True,
        },
    )


def serialize_automation_health(
    health:
    AutomationPageHealth,
) -> Dict[str, Any]:

    return (
        _serialize_automation_value(
            health
        )
    )


# ============================================================
# OPERATIONAL CHECK
# ============================================================

def automation_page_operational_check(
    controller: Optional[
        AutomationPageController
    ] = None,
) -> Dict[str, Any]:

    if controller is None:
        controller = (
            AutomationPageController()
        )

    health = (
        build_automation_health(
            controller
        )
    )

    return {
        "engine":
            AUTOMATION_PAGE_ENGINE,

        "version":
            AUTOMATION_PAGE_VERSION,

        "initialized":
            health.initialized,

        "ready":
            health.ready,

        "status":
            health.status.value,

        "operational":
            health.operational,

        "validation_errors":
            list(
                health.validation_errors
            ),

        "execution": False,
        "order_mutation": False,
        "position_mutation": False,
        "d13_modification": False,
        "risk_override": False,
        "cas_bypass": False,
        "upstream_mutation": False,
    }
# ============================================================
# AUTHORITY VALIDATION
# ============================================================

def validate_automation_authority(
    metadata: Optional[
        Dict[str, Any]
    ] = None,
) -> List[str]:

    errors: List[str] = []

    metadata = metadata or {}

    forbidden_flags = {
        "execution": False,
        "order_mutation": False,
        "position_mutation": False,
        "broker_authority": False,
        "market_data_authority": False,
        "evidence_authority": False,
        "intelligence_authority": False,
        "decision_authority": False,
        "d13_modification": False,
        "risk_override": False,
        "cas_bypass": False,
        "upstream_mutation": False,
    }

    for key, expected in (
        forbidden_flags.items()
    ):
        if metadata.get(key) is True:
            errors.append(
                f"FORBIDDEN_AUTHORITY:{key}"
            )

    return errors


# ============================================================
# DIAGNOSTICS
# ============================================================

def diagnose_automation_page(
    controller:
    AutomationPageController,
    composition: Optional[
        AutomationPageComposition
    ] = None,
) -> Dict[str, Any]:

    if composition is None:
        composition = (
            controller.last_composition
        )

    health = (
        build_automation_health(
            controller,
            composition,
        )
    )

    authority_errors = (
        validate_automation_authority(
            composition.page.metadata
            if composition
            else {}
        )
    )

    return {
        "engine":
            AUTOMATION_PAGE_ENGINE,

        "version":
            AUTOMATION_PAGE_VERSION,

        "page":
            AUTOMATION_PAGE_NAME,

        "route":
            controller.current_route,

        "mode":
            controller.current_mode.value,

        "status":
            controller.status.value,

        "state":
            serialize_automation_state(
                controller.state
            ),

        "composition":
            (
                serialize_automation_composition(
                    composition
                )
                if composition
                else None
            ),

        "health":
            serialize_automation_health(
                health
            ),

        "authority_errors":
            authority_errors,

        "authority_valid":
            not authority_errors,

        "operational":
            health.operational,

        "presentation_only":
            True,
    }


# ============================================================
# CONTRACT MANIFEST
# ============================================================

def automation_page_contract_manifest(
) -> Dict[str, Any]:

    return {
        "engine":
            AUTOMATION_PAGE_ENGINE,

        "version":
            AUTOMATION_PAGE_VERSION,

        "name":
            AUTOMATION_PAGE_NAME,

        "layer":
            "UI_PRESENTATION",

        "responsibilities": [
            "AUTOMATION_PRESENTATION",
            "AUTOMATION_STATUS_PRESENTATION",
            "AUTOMATION_READINESS_PRESENTATION",
            "AUTOMATION_CONTROL_PRESENTATION",
            "AUTOMATION_EVENT_PRESENTATION",
            "AUTOMATION_NAVIGATION",
            "AUTOMATION_SUMMARY",
        ],

        "input_flow": [
            "AUTOROBOMLM",
            "EXECUTION_LAYER",
            "RISK_LAYER",
            "CAS",
            "SESSION_STATE",
        ],

        "outputs": [
            "AUTOMATION_PAGE_VIEW",
            "AUTOMATION_COMPOSITION",
            "AUTOMATION_SNAPSHOT",
            "AUTOMATION_DIAGNOSTICS",
        ],

        "authority_owner": {
            "execution":
                "EXECUTION_LAYER",

            "risk":
                "RISK_LAYER",

            "cas":
                "CAS",

            "decision":
                "D13",

            "automation":
                "AUTOROBOMLM",
        },

        "principles": [
            "PRESENTATION_ONLY",
            "NO_EXECUTION",
            "NO_ORDER_MUTATION",
            "NO_POSITION_MUTATION",
            "NO_BROKER_ACCESS",
            "NO_D13_MODIFICATION",
            "NO_RISK_OVERRIDE",
            "NO_CAS_BYPASS",
            "NO_UPSTREAM_MUTATION",
        ],
    }


# ============================================================
# MODULE VALIDATION
# ============================================================

def validate_automation_module(
) -> Dict[str, Any]:

    controller = (
        AutomationPageController()
    )

    source = AutomationSourceState(
        identity=
        AutomationIdentityView(
            authenticated=False
        ),
        source_available=False,
        source_errors=[
            "DEFAULT_SOURCE"
        ],
    )

    composition = (
        compose_automation_page(
            source=source
        )
    )

    errors: List[str] = []

    errors.extend(
        validate_automation_state(
            controller.state
        )
    )

    errors.extend(
        validate_automation_composition(
            composition
        )
    )

    errors.extend(
        validate_automation_authority(
            composition.page.metadata
        )
    )

    manifest = (
        automation_page_contract_manifest()
    )

    if (
        manifest.get("layer")
        != "UI_PRESENTATION"
    ):
        errors.append(
            "INVALID_CONTRACT_LAYER"
        )

    return {
        "engine":
            AUTOMATION_PAGE_ENGINE,

        "version":
            AUTOMATION_PAGE_VERSION,

        "valid":
            not errors,

        "errors":
            errors,

        "presentation_only":
            True,

        "execution":
            False,

        "order_mutation":
            False,

        "position_mutation":
            False,

        "d13_modification":
            False,

        "risk_override":
            False,

        "cas_bypass":
            False,

        "upstream_mutation":
            False,
    }


# ============================================================
# DEFAULT SNAPSHOT
# ============================================================

def default_automation_snapshot(
) -> AutomationPageSnapshot:

    controller = (
        AutomationPageController()
    )

    source = AutomationSourceState(
        identity=
        AutomationIdentityView(),
        status=
        AutomationStatusView(),
        source_available=False,
    )

    return (
        build_automation_page_snapshot(
            controller=controller,
            source=source,
        )
    )


# ============================================================
# FACTORY
# ============================================================

def create_default_automation_page(
) -> AutomationPageController:

    return AutomationPageController(
        create_automation_page_state()
    )


# ============================================================
# MODULE SELF CHECK
# ============================================================

def automation_page_self_check(
) -> Dict[str, Any]:

    validation = (
        validate_automation_module()
    )

    diagnostics = (
        diagnose_automation_page(
            create_default_automation_page()
        )
    )

    return {
        "engine":
            AUTOMATION_PAGE_ENGINE,

        "version":
            AUTOMATION_PAGE_VERSION,

        "module_valid":
            validation["valid"],

        "diagnostics":
            diagnostics,

        "presentation_only":
            True,
    }


# ============================================================
# EXPORTS
# ============================================================

__all__ = [

    # Core
    "AUTOMATION_PAGE_ENGINE",
    "AUTOMATION_PAGE_VERSION",
    "AUTOMATION_PAGE_NAME",

    # Source
    "AutomationSourceState",

    # State
    "AutomationPageState",

    # Controller
    "AutomationPageController",

    # Composition
    "AutomationPageComposition",

    # Snapshot
    "AutomationPageSnapshot",

    # Health
    "AutomationPageHealth",

    # Factory
    "create_default_automation_page",

    # Compose
    "compose_automation_page",

    # Diagnostics
    "diagnose_automation_page",

    # Validation
    "validate_automation_module",

    # Snapshot
    "default_automation_snapshot",

    # Manifest
    "automation_page_contract_manifest",

    # Self Check
    "automation_page_self_check",
]