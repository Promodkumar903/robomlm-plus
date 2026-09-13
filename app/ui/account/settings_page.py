"""
ROBOMLM_PLUS — Settings Page
============================

Presentation-only settings workspace.

This module:
- Presents application settings and preferences.
- Normalizes upstream preference truth.
- Builds settings sections, controls, badges and summaries.
- Supports presentation-level navigation and state.
- Does NOT mutate actual settings/preferences.
- Does NOT modify authentication, credentials or security state.
- Does NOT generate market intelligence.
- Does NOT calculate evidence.
- Does NOT generate decisions.
- Does NOT modify D13.
- Does NOT generate or override Risk.
- Does NOT generate or bypass CAS.
- Does NOT execute orders or mutate positions.

Authority boundary:
    Settings UI -> Presentation
    Settings/Preference Service -> Actual preference mutation
    Authentication Layer -> Authentication
    Security Layer -> Security
    Billing Service -> Billing
    Subscription Service -> Subscription
    Entitlement Service -> Entitlements
    Intelligence Layer -> Intelligence
    Decision Cortex -> Decision
    D13 -> Decision Authority
    Risk Layer -> Risk
    CAS -> Safety Authority
    Execution Layer -> Execution
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


# ============================================================================
# MODULE CONSTANTS
# ============================================================================

SETTINGS_PAGE_ENGINE = "ROBOMLM_PLUS_UI_SETTINGS"
SETTINGS_PAGE_VERSION = "1.0"

SETTINGS_PAGE_NAME = "Settings"
SETTINGS_PAGE_TITLE = "Settings"
SETTINGS_PAGE_DESCRIPTION = (
    "ROBOMLM application preferences and settings workspace."
)

SETTINGS_ROUTE = "/account/settings"


# ============================================================================
# UI AUTHORITY CONTRACT
# ============================================================================

SETTINGS_UI_AUTHORITY: Dict[str, bool] = {
    # Presentation authority
    "settings_presentation": True,
    "preference_presentation": True,
    "settings_summary_presentation": True,
    "settings_navigation": True,
    "settings_category_presentation": True,
    "settings_control_presentation": True,
    "display_configuration": True,

    # Mutation / protected authorities
    "settings_mutation_authority": False,
    "preference_mutation_authority": False,
    "notification_preference_mutation": False,
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


# ============================================================================
# ENUMS
# ============================================================================


class SettingsPageStatus(str, Enum):
    LOADING = "LOADING"
    READY = "READY"
    DEGRADED = "DEGRADED"
    LOCKED = "LOCKED"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class SettingsPresentationMode(str, Enum):
    OVERVIEW = "OVERVIEW"
    GENERAL = "GENERAL"
    APPEARANCE = "APPEARANCE"
    NOTIFICATIONS = "NOTIFICATIONS"
    TRADING = "TRADING"
    DATA = "DATA"
    PRIVACY = "PRIVACY"
    ACCESSIBILITY = "ACCESSIBILITY"
    UNKNOWN = "UNKNOWN"


class PreferenceState(str, Enum):
    UNKNOWN = "UNKNOWN"
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"
    DEFAULT = "DEFAULT"
    CUSTOM = "CUSTOM"
    RESTRICTED = "RESTRICTED"


class SettingsCategory(str, Enum):
    UNKNOWN = "UNKNOWN"
    GENERAL = "GENERAL"
    APPEARANCE = "APPEARANCE"
    NOTIFICATIONS = "NOTIFICATIONS"
    TRADING = "TRADING"
    DATA = "DATA"
    PRIVACY = "PRIVACY"
    ACCESSIBILITY = "ACCESSIBILITY"


class SettingsPriority(str, Enum):
    NORMAL = "NORMAL"
    IMPORTANT = "IMPORTANT"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SettingsControlType(str, Enum):
    UNKNOWN = "UNKNOWN"
    TOGGLE = "TOGGLE"
    SELECT = "SELECT"
    TEXT = "TEXT"
    NUMBER = "NUMBER"
    DISPLAY = "DISPLAY"
    ACTION = "ACTION"


class SettingsBadgeType(str, Enum):
    STATUS = "STATUS"
    CATEGORY = "CATEGORY"
    CUSTOM = "CUSTOM"
    SYSTEM = "SYSTEM"


# ============================================================================
# NORMALIZATION HELPERS
# ============================================================================


def _settings_text(
    value: Any,
    default: str = "",
) -> str:
    if value is None:
        return default

    text = str(value).strip()
    return text if text else default


def _settings_bool(
    value: Any,
    default: bool = False,
) -> bool:
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

    return default


def _settings_enum(
    enum_type: Any,
    value: Any,
    default: Any,
) -> Any:
    if isinstance(value, enum_type):
        return value

    try:
        return enum_type(value)
    except (ValueError, TypeError):
        return default


def _settings_now() -> datetime:
    return datetime.now(timezone.utc)


# ============================================================================
# PRESENTATION CONTRACTS
# ============================================================================


@dataclass(frozen=True)
class SettingsIdentityView:
    user_id: str = ""
    display_name: str = ""
    email: str = ""
    authenticated: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SettingsPreferenceView:
    preference_id: str = ""
    key: str = ""
    label: str = ""
    description: str = ""
    category: SettingsCategory = SettingsCategory.UNKNOWN
    control_type: SettingsControlType = SettingsControlType.UNKNOWN
    state: PreferenceState = PreferenceState.UNKNOWN
    value: Any = None
    display_value: str = ""
    editable: bool = False
    visible: bool = True
    enabled: bool = True
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SettingsSectionView:
    section_id: str = ""
    title: str = ""
    description: str = ""
    category: SettingsCategory = SettingsCategory.UNKNOWN
    route: str = SETTINGS_ROUTE
    visible: bool = True
    enabled: bool = True
    priority: SettingsPriority = SettingsPriority.NORMAL
    preference_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SettingsBadge:
    badge_type: SettingsBadgeType = SettingsBadgeType.SYSTEM
    label: str = ""
    value: str = ""
    priority: SettingsPriority = SettingsPriority.NORMAL
    visible: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SettingsAction:
    action_id: str = ""
    label: str = ""
    route: str = SETTINGS_ROUTE
    enabled: bool = True
    visible: bool = True
    requires_authentication: bool = True
    priority: SettingsPriority = SettingsPriority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SettingsPageRequest:
    user_id: str = ""
    mode: SettingsPresentationMode = SettingsPresentationMode.OVERVIEW
    authenticated: bool = False
    page_status: SettingsPageStatus = SettingsPageStatus.UNKNOWN
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SettingsSummaryView:
    display_name: str = ""
    email: str = ""
    preference_count: int = 0
    editable_count: int = 0
    enabled_count: int = 0
    disabled_count: int = 0
    custom_count: int = 0
    restricted_count: int = 0
    active_mode: SettingsPresentationMode = SettingsPresentationMode.OVERVIEW
    authenticated: bool = False
    priority: SettingsPriority = SettingsPriority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SettingsPageView:
    page_name: str = SETTINGS_PAGE_NAME
    page_title: str = SETTINGS_PAGE_TITLE
    route: str = SETTINGS_ROUTE
    status: SettingsPageStatus = SettingsPageStatus.UNKNOWN
    mode: SettingsPresentationMode = SettingsPresentationMode.OVERVIEW

    identity: SettingsIdentityView = field(
        default_factory=SettingsIdentityView
    )

    preferences: List[SettingsPreferenceView] = field(
        default_factory=list
    )

    sections: List[SettingsSectionView] = field(
        default_factory=list
    )

    badges: List[SettingsBadge] = field(
        default_factory=list
    )

    actions: List[SettingsAction] = field(
        default_factory=list
    )

    summary: SettingsSummaryView = field(
        default_factory=SettingsSummaryView
    )

    authenticated: bool = False
    generated_at: datetime = field(default_factory=_settings_now)

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# DEFAULT SETTINGS ACTIONS
# ============================================================================


DEFAULT_SETTINGS_ACTIONS: tuple[SettingsAction, ...] = (
    SettingsAction(
        action_id="settings_overview",
        label="Overview",
        route="/account/settings",
        priority=SettingsPriority.NORMAL,
    ),
    SettingsAction(
        action_id="settings_general",
        label="General",
        route="/account/settings/general",
        priority=SettingsPriority.NORMAL,
    ),
    SettingsAction(
        action_id="settings_appearance",
        label="Appearance",
        route="/account/settings/appearance",
        priority=SettingsPriority.NORMAL,
    ),
    SettingsAction(
        action_id="settings_notifications",
        label="Notifications",
        route="/account/settings/notifications",
        priority=SettingsPriority.IMPORTANT,
    ),
    SettingsAction(
        action_id="settings_trading",
        label="Trading",
        route="/account/settings/trading",
        priority=SettingsPriority.HIGH,
    ),
    SettingsAction(
        action_id="settings_data",
        label="Data",
        route="/account/settings/data",
        priority=SettingsPriority.NORMAL,
    ),
    SettingsAction(
        action_id="settings_privacy",
        label="Privacy",
        route="/account/settings/privacy",
        priority=SettingsPriority.HIGH,
    ),
    SettingsAction(
        action_id="settings_accessibility",
        label="Accessibility",
        route="/account/settings/accessibility",
        priority=SettingsPriority.NORMAL,
    ),
)


# ============================================================================
# NORMALIZERS
# ============================================================================


def normalize_settings_identity(
    identity: Optional[SettingsIdentityView],
) -> SettingsIdentityView:
    if identity is None:
        return SettingsIdentityView()

    return SettingsIdentityView(
        user_id=_settings_text(identity.user_id),
        display_name=_settings_text(identity.display_name),
        email=_settings_text(identity.email),
        authenticated=_settings_bool(identity.authenticated),
        metadata=dict(identity.metadata or {}),
    )


def normalize_settings_preference(
    preference: SettingsPreferenceView,
) -> SettingsPreferenceView:
    return SettingsPreferenceView(
        preference_id=_settings_text(preference.preference_id),
        key=_settings_text(preference.key),
        label=_settings_text(preference.label),
        description=_settings_text(preference.description),
        category=_settings_enum(
            SettingsCategory,
            preference.category,
            SettingsCategory.UNKNOWN,
        ),
        control_type=_settings_enum(
            SettingsControlType,
            preference.control_type,
            SettingsControlType.UNKNOWN,
        ),
        state=_settings_enum(
            PreferenceState,
            preference.state,
            PreferenceState.UNKNOWN,
        ),
        value=preference.value,
        display_value=_settings_text(preference.display_value),
        editable=_settings_bool(preference.editable),
        visible=_settings_bool(preference.visible, True),
        enabled=_settings_bool(preference.enabled, True),
        source=_settings_text(preference.source),
        metadata=dict(preference.metadata or {}),
    )


def normalize_settings_preferences(
    preferences: Optional[List[SettingsPreferenceView]],
) -> List[SettingsPreferenceView]:
    if not preferences:
        return []

    return [
        normalize_settings_preference(item)
        for item in preferences
        if isinstance(item, SettingsPreferenceView)
    ]


# ============================================================================
# BADGE BUILDERS
# ============================================================================


def build_settings_status_badge(
    status: SettingsPageStatus,
) -> SettingsBadge:
    status = _settings_enum(
        SettingsPageStatus,
        status,
        SettingsPageStatus.UNKNOWN,
    )

    return SettingsBadge(
        badge_type=SettingsBadgeType.STATUS,
        label="Settings",
        value=status.value,
        priority=(
            SettingsPriority.HIGH
            if status in {
                SettingsPageStatus.ERROR,
                SettingsPageStatus.LOCKED,
            }
            else SettingsPriority.NORMAL
        ),
    )


def build_settings_category_badges(
    preferences: List[SettingsPreferenceView],
) -> List[SettingsBadge]:
    counts: Dict[SettingsCategory, int] = {}

    for preference in preferences:
        if not preference.visible:
            continue

        category = preference.category
        counts[category] = counts.get(category, 0) + 1

    badges: List[SettingsBadge] = []

    for category, count in counts.items():
        if category == SettingsCategory.UNKNOWN:
            continue

        badges.append(
            SettingsBadge(
                badge_type=SettingsBadgeType.CATEGORY,
                label=category.value.title(),
                value=str(count),
                priority=SettingsPriority.NORMAL,
                visible=True,
            )
        )

    return badges


def build_settings_badges(
    status: SettingsPageStatus,
    preferences: List[SettingsPreferenceView],
) -> List[SettingsBadge]:
    badges = [
        build_settings_status_badge(status),
    ]

    badges.extend(
        build_settings_category_badges(preferences)
    )

    return badges


# ============================================================================
# ACTION / SUMMARY HELPERS
# ============================================================================


def get_settings_actions(
    authenticated: bool = False,
) -> List[SettingsAction]:
    authenticated = _settings_bool(authenticated)

    actions: List[SettingsAction] = []

    for action in DEFAULT_SETTINGS_ACTIONS:
        if action.requires_authentication and not authenticated:
            actions.append(
                SettingsAction(
                    action_id=action.action_id,
                    label=action.label,
                    route=action.route,
                    enabled=False,
                    visible=True,
                    requires_authentication=True,
                    priority=action.priority,
                    metadata=dict(action.metadata),
                )
            )
        else:
            actions.append(action)

    return actions


def build_settings_summary(
    identity: SettingsIdentityView,
    preferences: List[SettingsPreferenceView],
    mode: SettingsPresentationMode,
) -> SettingsSummaryView:
    visible_preferences = [
        item for item in preferences
        if item.visible
    ]

    editable_count = sum(
        1 for item in visible_preferences
        if item.editable
    )

    enabled_count = sum(
        1
        for item in visible_preferences
        if item.state == PreferenceState.ENABLED
    )

    disabled_count = sum(
        1
        for item in visible_preferences
        if item.state == PreferenceState.DISABLED
    )

    custom_count = sum(
        1
        for item in visible_preferences
        if item.state == PreferenceState.CUSTOM
    )

    restricted_count = sum(
        1
        for item in visible_preferences
        if item.state == PreferenceState.RESTRICTED
    )

    priority = (
        SettingsPriority.HIGH
        if restricted_count > 0
        else SettingsPriority.NORMAL
    )

    return SettingsSummaryView(
        display_name=_settings_text(identity.display_name),
        email=_settings_text(identity.email),
        preference_count=len(visible_preferences),
        editable_count=editable_count,
        enabled_count=enabled_count,
        disabled_count=disabled_count,
        custom_count=custom_count,
        restricted_count=restricted_count,
        active_mode=_settings_enum(
            SettingsPresentationMode,
            mode,
            SettingsPresentationMode.OVERVIEW,
        ),
        authenticated=identity.authenticated,
        priority=priority,
        metadata={
            "presentation_only": True,
            "preference_mutation": False,
        },
    )
# ============================================================================
# SOURCE STATE
# ============================================================================


@dataclass(frozen=True)
class SettingsSourceState:
    """
    Upstream settings/preference presentation source.

    This object carries already-known preference truth into the UI.
    It does not own or mutate the actual settings store.
    """

    identity: SettingsIdentityView = field(
        default_factory=SettingsIdentityView
    )

    preferences: List[SettingsPreferenceView] = field(
        default_factory=list
    )

    source_available: bool = False
    source_errors: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# SECTION CONTRACT
# ============================================================================


DEFAULT_SETTINGS_SECTIONS: tuple[SettingsSectionView, ...] = (
    SettingsSectionView(
        section_id="general",
        title="General",
        description="Core application preferences.",
        category=SettingsCategory.GENERAL,
        route="/account/settings/general",
        priority=SettingsPriority.NORMAL,
    ),
    SettingsSectionView(
        section_id="appearance",
        title="Appearance",
        description="Application display and visual preferences.",
        category=SettingsCategory.APPEARANCE,
        route="/account/settings/appearance",
        priority=SettingsPriority.NORMAL,
    ),
    SettingsSectionView(
        section_id="notifications",
        title="Notifications",
        description="Notification presentation preferences.",
        category=SettingsCategory.NOTIFICATIONS,
        route="/account/settings/notifications",
        priority=SettingsPriority.IMPORTANT,
    ),
    SettingsSectionView(
        section_id="trading",
        title="Trading",
        description="User trading-interface preferences.",
        category=SettingsCategory.TRADING,
        route="/account/settings/trading",
        priority=SettingsPriority.HIGH,
    ),
    SettingsSectionView(
        section_id="data",
        title="Data",
        description="Market-data display and application data preferences.",
        category=SettingsCategory.DATA,
        route="/account/settings/data",
        priority=SettingsPriority.NORMAL,
    ),
    SettingsSectionView(
        section_id="privacy",
        title="Privacy",
        description="Privacy-related presentation preferences.",
        category=SettingsCategory.PRIVACY,
        route="/account/settings/privacy",
        priority=SettingsPriority.HIGH,
    ),
    SettingsSectionView(
        section_id="accessibility",
        title="Accessibility",
        description="Accessibility and display preferences.",
        category=SettingsCategory.ACCESSIBILITY,
        route="/account/settings/accessibility",
        priority=SettingsPriority.NORMAL,
    ),
)


# ============================================================================
# SOURCE NORMALIZATION
# ============================================================================


def normalize_settings_source_state(
    source: Optional[SettingsSourceState],
) -> SettingsSourceState:
    """
    Normalize upstream settings source.

    No settings are created, inferred, or mutated here.
    """

    if source is None:
        return SettingsSourceState(
            identity=SettingsIdentityView(),
            preferences=[],
            source_available=False,
            source_errors=["SETTINGS_SOURCE_NOT_PROVIDED"],
            metadata={
                "source_normalized": True,
                "presentation_only": True,
            },
        )

    identity = normalize_settings_identity(source.identity)
    preferences = normalize_settings_preferences(source.preferences)

    errors = [
        _settings_text(error)
        for error in (source.source_errors or [])
        if _settings_text(error)
    ]

    return SettingsSourceState(
        identity=identity,
        preferences=preferences,
        source_available=_settings_bool(source.source_available),
        source_errors=errors,
        metadata=dict(source.metadata or {}),
    )


# ============================================================================
# PRESENTATION READINESS
# ============================================================================


def evaluate_settings_presentation_status(
    source: SettingsSourceState,
) -> SettingsPageStatus:
    """
    Determine UI presentation readiness from upstream state.

    This does not determine actual settings validity or account security.
    """

    if not source.identity.authenticated:
        return SettingsPageStatus.LOCKED

    if not source.source_available:
        return SettingsPageStatus.DEGRADED

    if source.source_errors:
        return SettingsPageStatus.DEGRADED

    return SettingsPageStatus.READY


# ============================================================================
# SECTION COMPOSITION
# ============================================================================


def build_settings_sections(
    authenticated: bool,
    page_status: SettingsPageStatus,
    preferences: Optional[List[SettingsPreferenceView]] = None,
) -> List[SettingsSectionView]:
    """
    Build visible settings sections for presentation.

    Section state does not grant mutation authority.
    """

    authenticated = _settings_bool(authenticated)

    status = _settings_enum(
        SettingsPageStatus,
        page_status,
        SettingsPageStatus.UNKNOWN,
    )

    preferences = preferences or []

    if not authenticated:
        return [
            SettingsSectionView(
                section_id="overview",
                title="Settings",
                description=SETTINGS_PAGE_DESCRIPTION,
                category=SettingsCategory.UNKNOWN,
                route=SETTINGS_ROUTE,
                visible=True,
                enabled=False,
                priority=SettingsPriority.NORMAL,
                preference_count=0,
                metadata={
                    "locked": True,
                    "presentation_only": True,
                },
            )
        ]

    sections: List[SettingsSectionView] = []

    for section in DEFAULT_SETTINGS_SECTIONS:
        count = sum(
            1
            for preference in preferences
            if (
                preference.visible
                and preference.category == section.category
            )
        )

        enabled = status not in {
            SettingsPageStatus.ERROR,
            SettingsPageStatus.LOCKED,
        }

        sections.append(
            SettingsSectionView(
                section_id=section.section_id,
                title=section.title,
                description=section.description,
                category=section.category,
                route=section.route,
                visible=True,
                enabled=enabled,
                priority=section.priority,
                preference_count=count,
                metadata={
                    "presentation_only": True,
                    "preference_mutation": False,
                },
            )
        )

    return sections


# ============================================================================
# DISPLAY HELPERS
# ============================================================================


def resolve_settings_display_name(
    identity: SettingsIdentityView,
) -> str:
    """
    Resolve display-only identity label.

    No identity is created or modified.
    """

    if identity.display_name:
        return identity.display_name

    if identity.email:
        return identity.email

    return "Settings"


def build_settings_status_message(
    status: SettingsPageStatus,
    authenticated: bool,
) -> str:
    status = _settings_enum(
        SettingsPageStatus,
        status,
        SettingsPageStatus.UNKNOWN,
    )

    authenticated = _settings_bool(authenticated)

    if not authenticated:
        return "Sign in to view your settings."

    if status == SettingsPageStatus.READY:
        return "Settings are available."

    if status == SettingsPageStatus.LOADING:
        return "Loading settings."

    if status == SettingsPageStatus.DEGRADED:
        return "Settings are partially available."

    if status == SettingsPageStatus.ERROR:
        return "Settings could not be fully displayed."

    if status == SettingsPageStatus.LOCKED:
        return "Settings are locked."

    return "Settings status is currently unavailable."


def build_settings_mode_message(
    mode: SettingsPresentationMode,
) -> str:
    mode = _settings_enum(
        SettingsPresentationMode,
        mode,
        SettingsPresentationMode.OVERVIEW,
    )

    messages = {
        SettingsPresentationMode.OVERVIEW:
            "Manage application preferences from one workspace.",
        SettingsPresentationMode.GENERAL:
            "Configure general application preferences.",
        SettingsPresentationMode.APPEARANCE:
            "Configure display and visual preferences.",
        SettingsPresentationMode.NOTIFICATIONS:
            "Review notification-related preferences.",
        SettingsPresentationMode.TRADING:
            "Review trading-interface preferences.",
        SettingsPresentationMode.DATA:
            "Review data presentation preferences.",
        SettingsPresentationMode.PRIVACY:
            "Review privacy presentation preferences.",
        SettingsPresentationMode.ACCESSIBILITY:
            "Configure accessibility preferences.",
    }

    return messages.get(
        mode,
        "Review application settings.",
    )


# ============================================================================
# MODE FILTERING
# ============================================================================


SETTINGS_MODE_CATEGORIES: Dict[
    SettingsPresentationMode,
    SettingsCategory,
] = {
    SettingsPresentationMode.GENERAL:
        SettingsCategory.GENERAL,
    SettingsPresentationMode.APPEARANCE:
        SettingsCategory.APPEARANCE,
    SettingsPresentationMode.NOTIFICATIONS:
        SettingsCategory.NOTIFICATIONS,
    SettingsPresentationMode.TRADING:
        SettingsCategory.TRADING,
    SettingsPresentationMode.DATA:
        SettingsCategory.DATA,
    SettingsPresentationMode.PRIVACY:
        SettingsCategory.PRIVACY,
    SettingsPresentationMode.ACCESSIBILITY:
        SettingsCategory.ACCESSIBILITY,
}


def filter_settings_preferences(
    preferences: List[SettingsPreferenceView],
    mode: SettingsPresentationMode,
) -> List[SettingsPreferenceView]:
    """
    Presentation-only preference filtering.

    This never changes the upstream preference objects.
    """

    mode = _settings_enum(
        SettingsPresentationMode,
        mode,
        SettingsPresentationMode.OVERVIEW,
    )

    category = SETTINGS_MODE_CATEGORIES.get(mode)

    if category is None:
        return list(preferences)

    return [
        preference
        for preference in preferences
        if preference.visible
        and preference.category == category
    ]


# ============================================================================
# PAGE COMPOSITION
# ============================================================================


def compose_settings_page(
    source: Optional[SettingsSourceState] = None,
    mode: SettingsPresentationMode = SettingsPresentationMode.OVERVIEW,
) -> "SettingsPageComposition":
    """
    Compose the complete Settings presentation.

    Flow:

        Upstream Settings Source
                ↓
        Source Normalization
                ↓
        Presentation Readiness
                ↓
        Mode Filtering
                ↓
        Summary
                ↓
        Sections / Badges / Actions
                ↓
        Settings Page View
                ↓
        Composition

    No domain settings mutation occurs.
    """

    normalized_source = normalize_settings_source_state(source)

    normalized_mode = _settings_enum(
        SettingsPresentationMode,
        mode,
        SettingsPresentationMode.OVERVIEW,
    )

    status = evaluate_settings_presentation_status(
        normalized_source
    )

    identity = normalized_source.identity

    preferences = filter_settings_preferences(
        normalized_source.preferences,
        normalized_mode,
    )

    summary = build_settings_summary(
        identity=identity,
        preferences=preferences,
        mode=normalized_mode,
    )

    sections = build_settings_sections(
        authenticated=identity.authenticated,
        page_status=status,
        preferences=normalized_source.preferences,
    )

    badges = build_settings_badges(
        status=status,
        preferences=preferences,
    )

    actions = get_settings_actions(
        authenticated=identity.authenticated,
    )

    page = SettingsPageView(
        page_name=SETTINGS_PAGE_NAME,
        page_title=SETTINGS_PAGE_TITLE,
        route=SETTINGS_ROUTE,
        status=status,
        mode=normalized_mode,
        identity=identity,
        preferences=preferences,
        sections=sections,
        badges=badges,
        actions=actions,
        summary=summary,
        authenticated=identity.authenticated,
        generated_at=_settings_now(),
        metadata={
            "ui_only": True,
            "presentation_only": True,
            "source_normalized": True,

            # Settings authority boundaries
            "settings_generation": False,
            "settings_mutation": False,
            "preference_generation": False,
            "preference_mutation": False,
            "notification_preference_mutation": False,

            # Protected system boundaries
            "authentication_mutation": False,
            "credential_mutation": False,
            "security_mutation": False,
            "billing_mutation": False,
            "subscription_mutation": False,
            "entitlement_mutation": False,

            # Intelligence / decision boundaries
            "market_intelligence_generation": False,
            "evidence_generation": False,
            "decision_generation": False,
            "d13_modification": False,
            "risk_generation": False,
            "risk_override": False,
            "cas_generation": False,
            "cas_bypass": False,

            # Execution boundaries
            "execution": False,
            "order_mutation": False,
            "position_mutation": False,
            "upstream_mutation": False,
        },
    )

    return SettingsPageComposition(
        page=page,
        summary=summary,
        sections=sections,
        status_message=build_settings_status_message(
            status,
            identity.authenticated,
        ),
        mode_message=build_settings_mode_message(
            normalized_mode,
        ),
        errors=list(normalized_source.source_errors),
        generated_at=_settings_now(),
        metadata={
            "ui_only": True,
            "presentation_only": True,
            "settings_mutation": False,
            "preference_mutation": False,
            "upstream_mutation": False,
            "intelligence_generation": False,
            "decision_generation": False,
            "d13_modification": False,
            "risk_generation": False,
            "cas_generation": False,
            "execution": False,
        },
    )


# ============================================================================
# COMPOSITION CONTRACT
# ============================================================================


@dataclass(frozen=True)
class SettingsPageComposition:
    page: SettingsPageView
    summary: SettingsSummaryView
    sections: List[SettingsSectionView] = field(
        default_factory=list
    )

    status_message: str = ""
    mode_message: str = ""

    errors: List[str] = field(
        default_factory=list
    )

    generated_at: datetime = field(
        default_factory=_settings_now
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================================
# PART 2 EXPORTS
# ============================================================================

__all__ = [
    # Source
    "SettingsSourceState",

    # Sections
    "SettingsSectionView",
    "DEFAULT_SETTINGS_SECTIONS",

    # Source helpers
    "normalize_settings_source_state",

    # Readiness
    "evaluate_settings_presentation_status",

    # Section helpers
    "build_settings_sections",

    # Display helpers
    "resolve_settings_display_name",
    "build_settings_status_message",
    "build_settings_mode_message",

    # Filtering
    "SETTINGS_MODE_CATEGORIES",
    "filter_settings_preferences",

    # Composition
    "SettingsPageComposition",
    "compose_settings_page",
]
# ============================================================================
# INTERACTION CONTRACT
# ============================================================================


class SettingsInteraction(str, Enum):
    OPEN_OVERVIEW = "OPEN_OVERVIEW"
    OPEN_GENERAL = "OPEN_GENERAL"
    OPEN_APPEARANCE = "OPEN_APPEARANCE"
    OPEN_NOTIFICATIONS = "OPEN_NOTIFICATIONS"
    OPEN_TRADING = "OPEN_TRADING"
    OPEN_DATA = "OPEN_DATA"
    OPEN_PRIVACY = "OPEN_PRIVACY"
    OPEN_ACCESSIBILITY = "OPEN_ACCESSIBILITY"
    REFRESH = "REFRESH"
    LOCK = "LOCK"
    NONE = "NONE"


SETTINGS_INTERACTION_ROUTES: Dict[
    SettingsInteraction,
    str,
] = {
    SettingsInteraction.OPEN_OVERVIEW:
        "/account/settings",

    SettingsInteraction.OPEN_GENERAL:
        "/account/settings/general",

    SettingsInteraction.OPEN_APPEARANCE:
        "/account/settings/appearance",

    SettingsInteraction.OPEN_NOTIFICATIONS:
        "/account/settings/notifications",

    SettingsInteraction.OPEN_TRADING:
        "/account/settings/trading",

    SettingsInteraction.OPEN_DATA:
        "/account/settings/data",

    SettingsInteraction.OPEN_PRIVACY:
        "/account/settings/privacy",

    SettingsInteraction.OPEN_ACCESSIBILITY:
        "/account/settings/accessibility",
}


def normalize_settings_interaction(
    interaction: Any,
) -> SettingsInteraction:
    return _settings_enum(
        SettingsInteraction,
        interaction,
        SettingsInteraction.NONE,
    )


# ============================================================================
# PAGE STATE
# ============================================================================


@dataclass
class SettingsPageState:
    user_id: str = ""
    authenticated: bool = False

    mode: SettingsPresentationMode = (
        SettingsPresentationMode.OVERVIEW
    )

    status: SettingsPageStatus = (
        SettingsPageStatus.UNKNOWN
    )

    current_route: str = SETTINGS_ROUTE

    initialized: bool = False
    ready: bool = False
    locked: bool = True

    interaction_count: int = 0
    refresh_count: int = 0

    last_interaction: SettingsInteraction = (
        SettingsInteraction.NONE
    )

    last_error: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def create_settings_page_state(
    user_id: str = "",
    authenticated: bool = False,
) -> SettingsPageState:
    authenticated = _settings_bool(authenticated)

    return SettingsPageState(
        user_id=_settings_text(user_id),
        authenticated=authenticated,
        mode=SettingsPresentationMode.OVERVIEW,
        status=(
            SettingsPageStatus.LOADING
            if authenticated
            else SettingsPageStatus.LOCKED
        ),
        current_route=SETTINGS_ROUTE,
        initialized=False,
        ready=False,
        locked=not authenticated,
        interaction_count=0,
        refresh_count=0,
        last_interaction=SettingsInteraction.NONE,
        last_error="",
        metadata={
            "ui_only": True,
            "presentation_only": True,
            "settings_mutation": False,
            "preference_mutation": False,
            "upstream_mutation": False,
        },
    )


def normalize_settings_page_state(
    state: Optional[SettingsPageState],
) -> SettingsPageState:
    if state is None:
        return create_settings_page_state()

    authenticated = _settings_bool(
        state.authenticated
    )

    mode = _settings_enum(
        SettingsPresentationMode,
        state.mode,
        SettingsPresentationMode.OVERVIEW,
    )

    status = _settings_enum(
        SettingsPageStatus,
        state.status,
        SettingsPageStatus.UNKNOWN,
    )

    route = _settings_text(
        state.current_route,
        SETTINGS_ROUTE,
    )

    if not route.startswith(SETTINGS_ROUTE):
        route = SETTINGS_ROUTE
        mode = SettingsPresentationMode.OVERVIEW

    locked = _settings_bool(
        state.locked,
        not authenticated,
    )

    if not authenticated:
        locked = True
        ready = False
        status = SettingsPageStatus.LOCKED
    else:
        ready = _settings_bool(state.ready)

    return SettingsPageState(
        user_id=_settings_text(state.user_id),
        authenticated=authenticated,
        mode=mode,
        status=status,
        current_route=route,
        initialized=_settings_bool(state.initialized),
        ready=ready,
        locked=locked,
        interaction_count=max(0, int(state.interaction_count)),
        refresh_count=max(0, int(state.refresh_count)),
        last_interaction=normalize_settings_interaction(
            state.last_interaction
        ),
        last_error=_settings_text(state.last_error),
        metadata=dict(state.metadata or {}),
    )


# ============================================================================
# ROUTE / MODE RESOLUTION
# ============================================================================


SETTINGS_ROUTE_MODES: Dict[
    str,
    SettingsPresentationMode,
] = {
    "/account/settings":
        SettingsPresentationMode.OVERVIEW,

    "/account/settings/general":
        SettingsPresentationMode.GENERAL,

    "/account/settings/appearance":
        SettingsPresentationMode.APPEARANCE,

    "/account/settings/notifications":
        SettingsPresentationMode.NOTIFICATIONS,

    "/account/settings/trading":
        SettingsPresentationMode.TRADING,

    "/account/settings/data":
        SettingsPresentationMode.DATA,

    "/account/settings/privacy":
        SettingsPresentationMode.PRIVACY,

    "/account/settings/accessibility":
        SettingsPresentationMode.ACCESSIBILITY,
}


def route_to_settings_mode(
    route: str,
) -> SettingsPresentationMode:
    route = _settings_text(
        route,
        SETTINGS_ROUTE,
    )

    return SETTINGS_ROUTE_MODES.get(
        route,
        SettingsPresentationMode.OVERVIEW,
    )


def evaluate_settings_route_access(
    route: str,
    authenticated: bool,
    locked: bool = False,
) -> tuple[bool, str]:
    """
    Presentation-layer route access only.

    This does not perform authentication or security authorization.
    """

    route = _settings_text(route)

    if route not in SETTINGS_ROUTE_MODES:
        return False, "ROUTE_NOT_FOUND"

    if not _settings_bool(authenticated):
        return False, "REQUIRES_AUTHENTICATION"

    if _settings_bool(locked):
        return False, "SETTINGS_UI_LOCKED"

    return True, "ALLOWED"


# ============================================================================
# INTERACTION RESULT
# ============================================================================


@dataclass(frozen=True)
class SettingsInteractionResult:
    interaction: SettingsInteraction = SettingsInteraction.NONE
    requested_route: str = ""
    resolved_route: str = ""
    allowed: bool = False
    reason: str = ""
    mode: SettingsPresentationMode = (
        SettingsPresentationMode.OVERVIEW
    )
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def resolve_settings_interaction(
    interaction: SettingsInteraction,
    authenticated: bool,
    locked: bool,
) -> SettingsInteractionResult:
    interaction = normalize_settings_interaction(
        interaction
    )

    authenticated = _settings_bool(authenticated)
    locked = _settings_bool(locked)

    if interaction == SettingsInteraction.NONE:
        return SettingsInteractionResult(
            interaction=interaction,
            allowed=False,
            reason="NO_INTERACTION",
            mode=SettingsPresentationMode.OVERVIEW,
            metadata={
                "presentation_only": True,
            },
        )

    if interaction == SettingsInteraction.REFRESH:
        return SettingsInteractionResult(
            interaction=interaction,
            requested_route=SETTINGS_ROUTE,
            resolved_route=SETTINGS_ROUTE,
            allowed=authenticated and not locked,
            reason=(
                "ALLOWED"
                if authenticated and not locked
                else "SETTINGS_UI_LOCKED"
            ),
            mode=SettingsPresentationMode.OVERVIEW,
            metadata={
                "refresh_only": True,
                "settings_mutation": False,
            },
        )

    if interaction == SettingsInteraction.LOCK:
        return SettingsInteractionResult(
            interaction=interaction,
            requested_route=SETTINGS_ROUTE,
            resolved_route=SETTINGS_ROUTE,
            allowed=True,
            reason="UI_LOCK_ALLOWED",
            mode=SettingsPresentationMode.OVERVIEW,
            metadata={
                "ui_lock_only": True,
                "security_mutation": False,
            },
        )

    route = SETTINGS_INTERACTION_ROUTES.get(
        interaction
    )

    if not route:
        return SettingsInteractionResult(
            interaction=interaction,
            allowed=False,
            reason="INTERACTION_NOT_MAPPED",
            mode=SettingsPresentationMode.OVERVIEW,
        )

    allowed, reason = evaluate_settings_route_access(
        route=route,
        authenticated=authenticated,
        locked=locked,
    )

    return SettingsInteractionResult(
        interaction=interaction,
        requested_route=route,
        resolved_route=route if allowed else SETTINGS_ROUTE,
        allowed=allowed,
        reason=reason,
        mode=route_to_settings_mode(route),
        metadata={
            "presentation_only": True,
            "settings_mutation": False,
            "preference_mutation": False,
            "upstream_mutation": False,
        },
    )


# ============================================================================
# PAGE CONTROLLER
# ============================================================================


class SettingsPageController:
    """
    Presentation controller for Settings.

    The controller may change UI state only.

    It MUST NOT:
    - save settings
    - mutate preferences
    - change security state
    - change credentials
    - change notification persistence
    - change billing/subscription state
    - modify D13
    - modify Risk
    - bypass CAS
    - execute trades
    """

    def __init__(
        self,
        state: Optional[SettingsPageState] = None,
    ) -> None:
        self._state = normalize_settings_page_state(
            state or create_settings_page_state()
        )

        self._interaction_history: List[
            SettingsInteractionResult
        ] = []

        self._last_composition: Optional[
            SettingsPageComposition
        ] = None

    @property
    def state(self) -> SettingsPageState:
        return normalize_settings_page_state(
            self._state
        )

    @property
    def current_route(self) -> str:
        return self._state.current_route

    @property
    def current_mode(self) -> SettingsPresentationMode:
        return self._state.mode

    @property
    def status(self) -> SettingsPageStatus:
        return self._state.status

    @property
    def last_composition(
        self,
    ) -> Optional[SettingsPageComposition]:
        return self._last_composition

    def initialize(
        self,
        source: Optional[SettingsSourceState] = None,
    ) -> SettingsPageComposition:
        normalized_source = normalize_settings_source_state(
            source
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
        self._state.last_error = ""

        composition = self.compose(
            source=normalized_source
        )

        return composition

    def interact(
        self,
        interaction: SettingsInteraction,
    ) -> SettingsInteractionResult:
        interaction = normalize_settings_interaction(
            interaction
        )

        result = resolve_settings_interaction(
            interaction=interaction,
            authenticated=self._state.authenticated,
            locked=self._state.locked,
        )

        self._state.interaction_count += 1
        self._state.last_interaction = interaction

        if result.allowed:
            if interaction == SettingsInteraction.LOCK:
                self.lock()

            elif interaction == SettingsInteraction.REFRESH:
                self._state.refresh_count += 1

            else:
                self._state.current_route = (
                    result.resolved_route
                )
                self._state.mode = result.mode

        self._interaction_history.append(result)

        if len(self._interaction_history) > 500:
            self._interaction_history = (
                self._interaction_history[-500:]
            )

        return result

    def navigate(
        self,
        route: str,
    ) -> SettingsInteractionResult:
        route = _settings_text(route)

        mode = route_to_settings_mode(route)

        interaction_map = {
            mode: interaction
            for interaction, mapped_route
            in SETTINGS_INTERACTION_ROUTES.items()
            for mode in [route_to_settings_mode(mapped_route)]
        }

        interaction = interaction_map.get(
            mode,
            SettingsInteraction.NONE,
        )

        return self.interact(interaction)

    def lock(self) -> None:
        """Lock the Settings UI only."""

        self._state.locked = True
        self._state.ready = False
        self._state.status = SettingsPageStatus.LOCKED

    def unlock(self) -> bool:
        """
        Unlock presentation state only.

        Authentication must already be established upstream.
        """

        if not self._state.authenticated:
            return False

        self._state.locked = False

        if self._state.status == SettingsPageStatus.LOCKED:
            self._state.status = (
                SettingsPageStatus.READY
            )

        return True

    def set_authenticated(
        self,
        authenticated: bool,
    ) -> None:
        """
        Update presentation authentication state.

        Actual authentication remains external.
        """

        authenticated = _settings_bool(
            authenticated
        )

        self._state.authenticated = authenticated

        if not authenticated:
            self._state.locked = True
            self._state.ready = False
            self._state.status = (
                SettingsPageStatus.LOCKED
            )
            self._state.current_route = SETTINGS_ROUTE
            self._state.mode = (
                SettingsPresentationMode.OVERVIEW
            )

    def compose(
        self,
        source: Optional[SettingsSourceState] = None,
    ) -> SettingsPageComposition:
        composition = compose_settings_page(
            source=source,
            mode=self._state.mode,
        )

        self._last_composition = composition

        self._state.status = (
            composition.page.status
        )

        self._state.ready = (
            composition.page.status
            == SettingsPageStatus.READY
        )

        self._state.last_error = (
            composition.errors[0]
            if composition.errors
            else ""
        )

        if not self._state.authenticated:
            self._state.locked = True
            self._state.ready = False

        return composition

    @property
    def interaction_history(
        self,
    ) -> List[SettingsInteractionResult]:
        return list(self._interaction_history)

    def clear_interaction_history(self) -> None:
        self._interaction_history.clear()


# ============================================================================
# SNAPSHOT CONTRACT
# ============================================================================


@dataclass(frozen=True)
class SettingsPageSnapshot:
    state: SettingsPageState
    composition: SettingsPageComposition

    captured_at: datetime = field(
        default_factory=_settings_now
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def build_settings_page_snapshot(
    controller: SettingsPageController,
    source: Optional[SettingsSourceState] = None,
) -> SettingsPageSnapshot:
    if not isinstance(
        controller,
        SettingsPageController,
    ):
        raise TypeError(
            "controller must be SettingsPageController"
        )

    composition = controller.compose(
        source=source
    )

    state = controller.state

    return SettingsPageSnapshot(
        state=state,
        composition=composition,
        captured_at=_settings_now(),
        metadata={
            "ui_only": True,
            "presentation_only": True,
            "settings_mutation": False,
            "preference_mutation": False,
            "security_mutation": False,
            "authentication_mutation": False,
            "intelligence_generation": False,
            "decision_generation": False,
            "d13_modification": False,
            "risk_generation": False,
            "cas_generation": False,
            "execution": False,
            "upstream_mutation": False,
        },
    )


# ============================================================================
# PART 3 EXPORTS
# ============================================================================

__all__.extend([
    # Interaction
    "SettingsInteraction",
    "SETTINGS_INTERACTION_ROUTES",
    "normalize_settings_interaction",

    # State
    "SettingsPageState",
    "create_settings_page_state",
    "normalize_settings_page_state",

    # Routing
    "SETTINGS_ROUTE_MODES",
    "route_to_settings_mode",
    "evaluate_settings_route_access",

    # Interaction resolution
    "SettingsInteractionResult",
    "resolve_settings_interaction",

    # Controller
    "SettingsPageController",

    # Snapshot
    "SettingsPageSnapshot",
    "build_settings_page_snapshot",
])
# ============================================================================
# SERIALIZATION
# ============================================================================


def _serialize_settings_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            str(key): _serialize_settings_value(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            _serialize_settings_value(item)
            for item in value
        ]

    if hasattr(value, "__dataclass_fields__"):
        return {
            key: _serialize_settings_value(
                getattr(value, key)
            )
            for key in value.__dataclass_fields__
        }

    return value


def serialize_settings_identity(
    value: SettingsIdentityView,
) -> Dict[str, Any]:
    return _serialize_settings_value(value)


def serialize_settings_preference(
    value: SettingsPreferenceView,
) -> Dict[str, Any]:
    return _serialize_settings_value(value)


def serialize_settings_section(
    value: SettingsSectionView,
) -> Dict[str, Any]:
    return _serialize_settings_value(value)


def serialize_settings_badge(
    value: SettingsBadge,
) -> Dict[str, Any]:
    return _serialize_settings_value(value)


def serialize_settings_action(
    value: SettingsAction,
) -> Dict[str, Any]:
    return _serialize_settings_value(value)


def serialize_settings_page_request(
    value: SettingsPageRequest,
) -> Dict[str, Any]:
    return _serialize_settings_value(value)


def serialize_settings_summary(
    value: SettingsSummaryView,
) -> Dict[str, Any]:
    return _serialize_settings_value(value)


def serialize_settings_page_view(
    value: SettingsPageView,
) -> Dict[str, Any]:
    return _serialize_settings_value(value)


def serialize_settings_source(
    value: SettingsSourceState,
) -> Dict[str, Any]:
    return _serialize_settings_value(value)


def serialize_settings_composition(
    value: SettingsPageComposition,
) -> Dict[str, Any]:
    return _serialize_settings_value(value)


def serialize_settings_state(
    value: SettingsPageState,
) -> Dict[str, Any]:
    return _serialize_settings_value(value)


def serialize_settings_interaction_result(
    value: SettingsInteractionResult,
) -> Dict[str, Any]:
    return _serialize_settings_value(value)


def serialize_settings_snapshot(
    value: SettingsPageSnapshot,
) -> Dict[str, Any]:
    return _serialize_settings_value(value)


# ============================================================================
# VALIDATION HELPERS
# ============================================================================


def validate_settings_identity(
    identity: SettingsIdentityView,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(identity, SettingsIdentityView):
        return ["INVALID_SETTINGS_IDENTITY_TYPE"]

    if identity.authenticated and not identity.user_id:
        errors.append(
            "AUTHENTICATED_IDENTITY_REQUIRES_USER_ID"
        )

    if identity.email and "@" not in identity.email:
        errors.append(
            "IDENTITY_EMAIL_FORMAT_WARNING"
        )

    return errors


def validate_settings_preference(
    preference: SettingsPreferenceView,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(
        preference,
        SettingsPreferenceView,
    ):
        return ["INVALID_SETTINGS_PREFERENCE_TYPE"]

    if not preference.preference_id:
        errors.append(
            "PREFERENCE_ID_REQUIRED"
        )

    if not preference.key:
        errors.append(
            "PREFERENCE_KEY_REQUIRED"
        )

    if preference.visible and not preference.label:
        errors.append(
            "VISIBLE_PREFERENCE_REQUIRES_LABEL"
        )

    if preference.editable and not preference.enabled:
        errors.append(
            "EDITABLE_DISABLED_PREFERENCE"
        )

    if (
        preference.state
        == PreferenceState.RESTRICTED
        and preference.editable
    ):
        errors.append(
            "RESTRICTED_PREFERENCE_CANNOT_BE_EDITABLE"
        )

    if (
        preference.control_type
        == SettingsControlType.UNKNOWN
        and preference.visible
    ):
        errors.append(
            "VISIBLE_PREFERENCE_CONTROL_TYPE_UNKNOWN"
        )

    return errors


def validate_settings_section(
    section: SettingsSectionView,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(
        section,
        SettingsSectionView,
    ):
        return ["INVALID_SETTINGS_SECTION_TYPE"]

    if section.visible and not section.title:
        errors.append(
            "VISIBLE_SECTION_REQUIRES_TITLE"
        )

    if section.visible and not section.route:
        errors.append(
            "VISIBLE_SECTION_REQUIRES_ROUTE"
        )

    if section.preference_count < 0:
        errors.append(
            "SECTION_PREFERENCE_COUNT_NEGATIVE"
        )

    return errors


def validate_settings_badge(
    badge: SettingsBadge,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(
        badge,
        SettingsBadge,
    ):
        return ["INVALID_SETTINGS_BADGE_TYPE"]

    if badge.visible and not badge.label:
        errors.append(
            "VISIBLE_BADGE_REQUIRES_LABEL"
        )

    return errors


def validate_settings_action(
    action: SettingsAction,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(
        action,
        SettingsAction,
    ):
        return ["INVALID_SETTINGS_ACTION_TYPE"]

    if action.visible and not action.label:
        errors.append(
            "VISIBLE_ACTION_REQUIRES_LABEL"
        )

    if action.enabled and not action.route:
        errors.append(
            "ENABLED_ACTION_REQUIRES_ROUTE"
        )

    if action.route and not action.route.startswith(
        SETTINGS_ROUTE
    ):
        errors.append(
            "SETTINGS_ACTION_ROUTE_OUTSIDE_SETTINGS_SCOPE"
        )

    return errors


def validate_settings_summary(
    summary: SettingsSummaryView,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(
        summary,
        SettingsSummaryView,
    ):
        return ["INVALID_SETTINGS_SUMMARY_TYPE"]

    counters = {
        "preference_count": summary.preference_count,
        "editable_count": summary.editable_count,
        "enabled_count": summary.enabled_count,
        "disabled_count": summary.disabled_count,
        "custom_count": summary.custom_count,
        "restricted_count": summary.restricted_count,
    }

    for name, value in counters.items():
        if value < 0:
            errors.append(
                f"{name.upper()}_NEGATIVE"
            )

    if summary.editable_count > summary.preference_count:
        errors.append(
            "EDITABLE_COUNT_EXCEEDS_TOTAL"
        )

    if summary.enabled_count > summary.preference_count:
        errors.append(
            "ENABLED_COUNT_EXCEEDS_TOTAL"
        )

    if summary.disabled_count > summary.preference_count:
        errors.append(
            "DISABLED_COUNT_EXCEEDS_TOTAL"
        )

    if summary.custom_count > summary.preference_count:
        errors.append(
            "CUSTOM_COUNT_EXCEEDS_TOTAL"
        )

    if summary.restricted_count > summary.preference_count:
        errors.append(
            "RESTRICTED_COUNT_EXCEEDS_TOTAL"
        )

    return errors


# ============================================================================
# PAGE VALIDATION
# ============================================================================


def validate_settings_page_view(
    page: SettingsPageView,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(
        page,
        SettingsPageView,
    ):
        return ["INVALID_SETTINGS_PAGE_VIEW_TYPE"]

    if page.page_name != SETTINGS_PAGE_NAME:
        errors.append(
            "INVALID_SETTINGS_PAGE_NAME"
        )

    if page.route != SETTINGS_ROUTE:
        errors.append(
            "INVALID_SETTINGS_PAGE_ROUTE"
        )

    errors.extend(
        validate_settings_identity(
            page.identity
        )
    )

    for preference in page.preferences:
        errors.extend(
            validate_settings_preference(
                preference
            )
        )

    for section in page.sections:
        errors.extend(
            validate_settings_section(
                section
            )
        )

    for badge in page.badges:
        errors.extend(
            validate_settings_badge(
                badge
            )
        )

    for action in page.actions:
        errors.extend(
            validate_settings_action(
                action
            )
        )

    errors.extend(
        validate_settings_summary(
            page.summary
        )
    )

    if not page.authenticated and (
        page.status != SettingsPageStatus.LOCKED
    ):
        errors.append(
            "UNAUTHENTICATED_SETTINGS_PAGE_MUST_BE_LOCKED"
        )

    protected_flags = (
        "settings_mutation",
        "preference_mutation",
        "notification_preference_mutation",
        "authentication_mutation",
        "credential_mutation",
        "security_mutation",
        "billing_mutation",
        "subscription_mutation",
        "entitlement_mutation",
        "market_intelligence_generation",
        "evidence_generation",
        "decision_generation",
        "d13_modification",
        "risk_generation",
        "risk_override",
        "cas_generation",
        "cas_bypass",
        "execution",
        "order_mutation",
        "position_mutation",
        "upstream_mutation",
    )

    for flag in protected_flags:
        if page.metadata.get(flag) is True:
            errors.append(
                f"FORBIDDEN_AUTHORITY_ENABLED:{flag}"
            )

    return errors


def validate_settings_source(
    source: SettingsSourceState,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(
        source,
        SettingsSourceState,
    ):
        return ["INVALID_SETTINGS_SOURCE_TYPE"]

    errors.extend(
        validate_settings_identity(
            source.identity
        )
    )

    seen_ids = set()

    for preference in source.preferences:
        errors.extend(
            validate_settings_preference(
                preference
            )
        )

        preference_id = preference.preference_id

        if preference_id:
            if preference_id in seen_ids:
                errors.append(
                    f"DUPLICATE_PREFERENCE_ID:{preference_id}"
                )

            seen_ids.add(preference_id)

    if (
        not source.source_available
        and not source.source_errors
    ):
        errors.append(
            "UNAVAILABLE_SOURCE_REQUIRES_SOURCE_ERROR"
        )

    return errors


def validate_settings_composition(
    composition: SettingsPageComposition,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(
        composition,
        SettingsPageComposition,
    ):
        return ["INVALID_SETTINGS_COMPOSITION_TYPE"]

    errors.extend(
        validate_settings_page_view(
            composition.page
        )
    )

    errors.extend(
        validate_settings_summary(
            composition.summary
        )
    )

    for section in composition.sections:
        errors.extend(
            validate_settings_section(
                section
            )
        )

    protected_flags = (
        "settings_mutation",
        "preference_mutation",
        "upstream_mutation",
        "intelligence_generation",
        "decision_generation",
        "d13_modification",
        "risk_generation",
        "cas_generation",
        "execution",
    )

    for flag in protected_flags:
        if composition.metadata.get(flag) is True:
            errors.append(
                f"COMPOSITION_FORBIDDEN_AUTHORITY:{flag}"
            )

    return errors


def validate_settings_page_state(
    state: SettingsPageState,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(
        state,
        SettingsPageState,
    ):
        return ["INVALID_SETTINGS_PAGE_STATE_TYPE"]

    if state.interaction_count < 0:
        errors.append(
            "INTERACTION_COUNT_NEGATIVE"
        )

    if state.refresh_count < 0:
        errors.append(
            "REFRESH_COUNT_NEGATIVE"
        )

    if not state.authenticated:
        if not state.locked:
            errors.append(
                "UNAUTHENTICATED_STATE_MUST_BE_LOCKED"
            )

        if state.ready:
            errors.append(
                "UNAUTHENTICATED_STATE_CANNOT_BE_READY"
            )

        if state.status != SettingsPageStatus.LOCKED:
            errors.append(
                "UNAUTHENTICATED_STATE_STATUS_INVALID"
            )

    if state.ready and state.locked:
        errors.append(
            "READY_STATE_CANNOT_BE_LOCKED"
        )

    if state.current_route not in SETTINGS_ROUTE_MODES:
        errors.append(
            "UNKNOWN_SETTINGS_CURRENT_ROUTE"
        )

    return errors


def validate_settings_interaction_result(
    result: SettingsInteractionResult,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(
        result,
        SettingsInteractionResult,
    ):
        return [
            "INVALID_SETTINGS_INTERACTION_RESULT_TYPE"
        ]

    if result.allowed and not result.resolved_route:
        errors.append(
            "ALLOWED_INTERACTION_REQUIRES_RESOLVED_ROUTE"
        )

    if (
        result.allowed
        and result.reason
        not in {"ALLOWED", "UI_LOCK_ALLOWED"}
    ):
        errors.append(
            "ALLOWED_INTERACTION_REASON_INVALID"
        )

    if (
        result.interaction
        == SettingsInteraction.NONE
        and result.allowed
    ):
        errors.append(
            "NONE_INTERACTION_CANNOT_BE_ALLOWED"
        )

    if result.resolved_route and not result.resolved_route.startswith(
        SETTINGS_ROUTE
    ):
        errors.append(
            "RESOLVED_ROUTE_OUTSIDE_SETTINGS_SCOPE"
        )

    return errors


# ============================================================================
# AUTHORITY VALIDATION
# ============================================================================


def validate_settings_authority(
    metadata: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """
    Verify that Settings UI has no protected domain authority.
    """

    errors: List[str] = []

    for authority, allowed in SETTINGS_UI_AUTHORITY.items():
        if authority == "settings_presentation":
            continue

        if authority == "preference_presentation":
            continue

        if authority == "settings_summary_presentation":
            continue

        if authority == "settings_navigation":
            continue

        if authority == "settings_category_presentation":
            continue

        if authority == "settings_control_presentation":
            continue

        if authority == "display_configuration":
            continue

        if allowed:
            errors.append(
                f"FORBIDDEN_UI_AUTHORITY_ENABLED:{authority}"
            )

    if metadata:
        protected_flags = (
            "settings_mutation",
            "preference_mutation",
            "notification_preference_mutation",
            "authentication_mutation",
            "credential_mutation",
            "security_mutation",
            "billing_mutation",
            "subscription_mutation",
            "entitlement_mutation",
            "intelligence_generation",
            "evidence_generation",
            "decision_generation",
            "d13_modification",
            "risk_generation",
            "risk_override",
            "cas_generation",
            "cas_bypass",
            "execution",
            "order_mutation",
            "position_mutation",
            "upstream_mutation",
        )

        for flag in protected_flags:
            if metadata.get(flag) is True:
                errors.append(
                    f"FORBIDDEN_METADATA_AUTHORITY:{flag}"
                )

    return errors


def validate_settings_snapshot(
    snapshot: SettingsPageSnapshot,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(
        snapshot,
        SettingsPageSnapshot,
    ):
        return ["INVALID_SETTINGS_SNAPSHOT_TYPE"]

    errors.extend(
        validate_settings_page_state(
            snapshot.state
        )
    )

    errors.extend(
        validate_settings_composition(
            snapshot.composition
        )
    )

    errors.extend(
        validate_settings_authority(
            snapshot.metadata
        )
    )

    return errors


# ============================================================================
# HEALTH CONTRACT
# ============================================================================


@dataclass(frozen=True)
class SettingsPageHealth:
    engine: str = SETTINGS_PAGE_ENGINE
    version: str = SETTINGS_PAGE_VERSION

    initialized: bool = False
    ready: bool = False

    status: SettingsPageStatus = (
        SettingsPageStatus.UNKNOWN
    )

    preference_count: int = 0
    editable_count: int = 0

    validation_errors: List[str] = field(
        default_factory=list
    )

    authority_valid: bool = False
    operational: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def build_settings_page_health(
    controller: SettingsPageController,
    composition: Optional[
        SettingsPageComposition
    ] = None,
) -> SettingsPageHealth:
    if not isinstance(
        controller,
        SettingsPageController,
    ):
        raise TypeError(
            "controller must be SettingsPageController"
        )

    if composition is None:
        composition = controller.last_composition

    errors = validate_settings_page_state(
        controller.state
    )

    if composition is not None:
        errors.extend(
            validate_settings_composition(
                composition
            )
        )

        authority_errors = (
            validate_settings_authority(
                composition.page.metadata
            )
        )
    else:
        authority_errors = [
            "SETTINGS_COMPOSITION_NOT_AVAILABLE"
        ]

    errors.extend(authority_errors)

    authority_valid = not bool(
        authority_errors
    )

    preference_count = 0
    editable_count = 0

    if composition is not None:
        preference_count = len(
            composition.page.preferences
        )

        editable_count = sum(
            1
            for item in composition.page.preferences
            if item.editable
        )

    operational = (
        controller.state.initialized
        and controller.state.ready
        and not controller.state.locked
        and controller.status
        == SettingsPageStatus.READY
        and not errors
        and authority_valid
    )

    return SettingsPageHealth(
        engine=SETTINGS_PAGE_ENGINE,
        version=SETTINGS_PAGE_VERSION,
        initialized=controller.state.initialized,
        ready=controller.state.ready,
        status=controller.status,
        preference_count=preference_count,
        editable_count=editable_count,
        validation_errors=errors,
        authority_valid=authority_valid,
        operational=operational,
        metadata={
            "ui_only": True,
            "presentation_only": True,
            "settings_mutation": False,
            "preference_mutation": False,
            "upstream_mutation": False,
            "intelligence_generation": False,
            "decision_generation": False,
            "d13_modification": False,
            "risk_generation": False,
            "cas_generation": False,
            "execution": False,
        },
    )


def serialize_settings_page_health(
    health: SettingsPageHealth,
) -> Dict[str, Any]:
    return _serialize_settings_value(
        health
    )


# ============================================================================
# OPERATIONAL CHECK
# ============================================================================


def settings_page_operational_check(
    controller: Optional[
        SettingsPageController
    ] = None,
) -> Dict[str, Any]:
    if controller is None:
        controller = SettingsPageController()

    health = build_settings_page_health(
        controller
    )

    return {
        "engine": SETTINGS_PAGE_ENGINE,
        "version": SETTINGS_PAGE_VERSION,
        "initialized": health.initialized,
        "ready": health.ready,
        "status": health.status.value,
        "operational": health.operational,
        "validation_errors": list(
            health.validation_errors
        ),
        "authority_valid": health.authority_valid,

        "settings_mutation": False,
        "preference_mutation": False,
        "notification_preference_mutation": False,
        "authentication_mutation": False,
        "credential_mutation": False,
        "security_mutation": False,
        "billing_mutation": False,
        "subscription_mutation": False,
        "entitlement_mutation": False,
        "intelligence_generation": False,
        "evidence_generation": False,
        "decision_generation": False,
        "d13_modification": False,
        "risk_generation": False,
        "risk_override": False,
        "cas_generation": False,
        "cas_bypass": False,
        "execution": False,
        "order_mutation": False,
        "position_mutation": False,
        "upstream_mutation": False,
    }


# ============================================================================
# MODULE SUMMARY
# ============================================================================


def settings_page_summary() -> Dict[str, Any]:
    return {
        "engine": SETTINGS_PAGE_ENGINE,
        "version": SETTINGS_PAGE_VERSION,
        "name": SETTINGS_PAGE_NAME,
        "title": SETTINGS_PAGE_TITLE,
        "route": SETTINGS_ROUTE,
        "layer": "UI_PRESENTATION",

        "responsibilities": [
            "SETTINGS_PRESENTATION",
            "PREFERENCE_PRESENTATION",
            "SETTINGS_SUMMARY_PRESENTATION",
            "SETTINGS_NAVIGATION",
            "SETTINGS_CATEGORY_PRESENTATION",
            "SETTINGS_CONTROL_PRESENTATION",
            "DISPLAY_CONFIGURATION",
        ],

        "authority": dict(
            SETTINGS_UI_AUTHORITY
        ),

        "forbidden": [
            "SETTINGS_MUTATION",
            "PREFERENCE_MUTATION",
            "NOTIFICATION_PREFERENCE_MUTATION",
            "AUTHENTICATION_MUTATION",
            "CREDENTIAL_MUTATION",
            "SECURITY_MUTATION",
            "BILLING_MUTATION",
            "SUBSCRIPTION_MUTATION",
            "ENTITLEMENT_MUTATION",
            "INTELLIGENCE_GENERATION",
            "EVIDENCE_GENERATION",
            "DECISION_GENERATION",
            "D13_MODIFICATION",
            "RISK_GENERATION",
            "RISK_OVERRIDE",
            "CAS_GENERATION",
            "CAS_BYPASS",
            "EXECUTION",
            "ORDER_MUTATION",
            "POSITION_MUTATION",
            "UPSTREAM_MUTATION",
        ],

        "principles": [
            "PRESENTATION_ONLY",
            "UPSTREAM_TRUTH_PRESERVED",
            "NO_FAKE_SETTINGS_TRUTH",
            "NO_PREFERENCE_MUTATION",
            "NO_SECURITY_MUTATION",
            "NO_AUTHENTICATION_MUTATION",
            "NO_INTELLIGENCE_GENERATION",
            "NO_DECISION_GENERATION",
            "NO_D13_MUTATION",
            "NO_RISK_OVERRIDE",
            "NO_CAS_BYPASS",
            "NO_EXECUTION",
        ],
    }


# ============================================================================
# DEFAULT MODULE CHECK
# ============================================================================


def create_default_settings_page(
) -> SettingsPageController:
    return SettingsPageController(
        state=create_settings_page_state(
            authenticated=False
        )
    )


def settings_page_module_check() -> Dict[str, Any]:
    controller = create_default_settings_page()

    source = SettingsSourceState(
        identity=SettingsIdentityView(
            authenticated=False
        ),
        preferences=[],
        source_available=False,
        source_errors=[
            "DEFAULT_SETTINGS_SOURCE_NOT_CONNECTED"
        ],
    )

    composition = controller.initialize(
        source
    )

    errors: List[str] = []

    errors.extend(
        validate_settings_source(
            source
        )
    )

    errors.extend(
        validate_settings_page_state(
            controller.state
        )
    )

    errors.extend(
        validate_settings_composition(
            composition
        )
    )

    errors.extend(
        validate_settings_authority(
            composition.page.metadata
        )
    )

    return {
        "engine": SETTINGS_PAGE_ENGINE,
        "version": SETTINGS_PAGE_VERSION,
        "valid": not bool(errors),
        "errors": errors,
        "authority_valid": not bool(
            validate_settings_authority(
                composition.page.metadata
            )
        ),
        "ui_only": True,
        "settings_mutation": False,
        "preference_mutation": False,
        "notification_preference_mutation": False,
        "authentication_mutation": False,
        "security_mutation": False,
        "intelligence_generation": False,
        "decision_generation": False,
        "d13_modification": False,
        "risk_generation": False,
        "cas_generation": False,
        "execution": False,
        "upstream_mutation": False,
    }


# ============================================================================
# PART 4 EXPORTS
# ============================================================================

__all__.extend([
    # Serialization
    "_serialize_settings_value",
    "serialize_settings_identity",
    "serialize_settings_preference",
    "serialize_settings_section",
    "serialize_settings_badge",
    "serialize_settings_action",
    "serialize_settings_page_request",
    "serialize_settings_summary",
    "serialize_settings_page_view",
    "serialize_settings_source",
    "serialize_settings_composition",
    "serialize_settings_state",
    "serialize_settings_interaction_result",
    "serialize_settings_snapshot",

    # Validation
    "validate_settings_identity",
    "validate_settings_preference",
    "validate_settings_section",
    "validate_settings_badge",
    "validate_settings_action",
    "validate_settings_summary",
    "validate_settings_page_view",
    "validate_settings_source",
    "validate_settings_composition",
    "validate_settings_page_state",
    "validate_settings_interaction_result",
    "validate_settings_authority",
    "validate_settings_snapshot",

    # Health
    "SettingsPageHealth",
    "build_settings_page_health",
    "serialize_settings_page_health",

    # Operational
    "settings_page_operational_check",

    # Module
    "settings_page_summary",
    "create_default_settings_page",
    "settings_page_module_check",
])
# ============================================================================
# FINAL PRESENTATION UTILITIES
# ============================================================================


def refresh_settings_page(
    controller: SettingsPageController,
    source: Optional[SettingsSourceState] = None,
) -> SettingsPageComposition:
    """
    Refresh the Settings presentation from supplied upstream truth.

    IMPORTANT:
    This does not fetch, save, mutate, reset, or persist settings.
    The caller is responsible for obtaining fresh upstream data.
    """

    if not isinstance(
        controller,
        SettingsPageController,
    ):
        raise TypeError(
            "controller must be SettingsPageController"
        )

    controller._state.refresh_count += 1
    controller._state.last_interaction = (
        SettingsInteraction.REFRESH
    )

    return controller.compose(
        source=source
    )


def get_settings_page(
    controller: SettingsPageController,
    source: Optional[SettingsSourceState] = None,
) -> SettingsPageComposition:
    """
    Return the current Settings presentation.

    If no prior composition exists and no source is supplied,
    a safe degraded presentation is created.
    """

    if not isinstance(
        controller,
        SettingsPageController,
    ):
        raise TypeError(
            "controller must be SettingsPageController"
        )

    if source is not None:
        return controller.compose(source)

    if controller.last_composition is not None:
        return controller.last_composition

    safe_source = SettingsSourceState(
        identity=SettingsIdentityView(
            user_id=controller.state.user_id,
            authenticated=controller.state.authenticated,
        ),
        preferences=[],
        source_available=False,
        source_errors=[
            "SETTINGS_SOURCE_NOT_CONNECTED"
        ],
    )

    return controller.compose(
        source=safe_source
    )


def can_navigate_settings_page(
    controller: SettingsPageController,
    route: str,
) -> bool:
    if not isinstance(
        controller,
        SettingsPageController,
    ):
        raise TypeError(
            "controller must be SettingsPageController"
        )

    allowed, _ = evaluate_settings_route_access(
        route=route,
        authenticated=controller.state.authenticated,
        locked=controller.state.locked,
    )

    return allowed


def select_settings_route(
    controller: SettingsPageController,
    route: str,
) -> SettingsInteractionResult:
    if not isinstance(
        controller,
        SettingsPageController,
    ):
        raise TypeError(
            "controller must be SettingsPageController"
        )

    return controller.navigate(route)


def lock_settings_page(
    controller: SettingsPageController,
) -> None:
    if not isinstance(
        controller,
        SettingsPageController,
    ):
        raise TypeError(
            "controller must be SettingsPageController"
        )

    # UI lock only.
    controller.lock()


# ============================================================================
# DIAGNOSTICS
# ============================================================================


def diagnose_settings_page(
    controller: SettingsPageController,
    composition: Optional[
        SettingsPageComposition
    ] = None,
) -> Dict[str, Any]:
    """
    Produce a machine-readable Settings UI diagnostic.

    Diagnostics observe the system; they do not modify settings.
    """

    if not isinstance(
        controller,
        SettingsPageController,
    ):
        raise TypeError(
            "controller must be SettingsPageController"
        )

    if composition is None:
        composition = controller.last_composition

    health = build_settings_page_health(
        controller=controller,
        composition=composition,
    )

    authority_errors = validate_settings_authority(
        composition.page.metadata
        if composition is not None
        else None
    )

    return {
        "engine": SETTINGS_PAGE_ENGINE,
        "version": SETTINGS_PAGE_VERSION,
        "page": SETTINGS_PAGE_NAME,
        "route": controller.current_route,
        "mode": controller.current_mode.value,
        "status": controller.status.value,

        "state": serialize_settings_state(
            controller.state
        ),

        "composition": (
            serialize_settings_composition(
                composition
            )
            if composition is not None
            else None
        ),

        "health": serialize_settings_page_health(
            health
        ),

        "validation_errors": list(
            health.validation_errors
        ),

        "authority_errors": authority_errors,

        "valid": (
            not health.validation_errors
            and health.authority_valid
        ),

        "authority": {
            key: value
            for key, value
            in SETTINGS_UI_AUTHORITY.items()
        },

        "protected_authority": {
            "settings_mutation": False,
            "preference_mutation": False,
            "notification_preference_mutation": False,
            "authentication_mutation": False,
            "credential_mutation": False,
            "security_mutation": False,
            "billing_mutation": False,
            "subscription_mutation": False,
            "entitlement_mutation": False,
            "intelligence_generation": False,
            "evidence_generation": False,
            "decision_generation": False,
            "d13_modification": False,
            "risk_generation": False,
            "risk_override": False,
            "cas_generation": False,
            "cas_bypass": False,
            "execution": False,
            "order_mutation": False,
            "position_mutation": False,
            "upstream_mutation": False,
        },
    }


# ============================================================================
# ARCHITECTURE CONTRACT MANIFEST
# ============================================================================


def settings_page_contract_manifest() -> Dict[str, Any]:
    """
    Machine-readable architectural contract for Settings UI.
    """

    return {
        "engine": SETTINGS_PAGE_ENGINE,
        "version": SETTINGS_PAGE_VERSION,
        "name": SETTINGS_PAGE_NAME,
        "layer": "UI_PRESENTATION",

        "responsibilities": [
            "SETTINGS_PRESENTATION",
            "PREFERENCE_PRESENTATION",
            "SETTINGS_SUMMARY_PRESENTATION",
            "SETTINGS_NAVIGATION",
            "SETTINGS_CATEGORY_PRESENTATION",
            "SETTINGS_CONTROL_PRESENTATION",
            "DISPLAY_CONFIGURATION",
        ],

        "input_flow": [
            "USER_SERVICE_OUTPUT",
            "PROFILE_SERVICE_OUTPUT",
            "SETTINGS_SERVICE_OUTPUT",
            "PREFERENCE_SERVICE_OUTPUT",
            "APPLICATION_SESSION_STATE",
        ],

        "processing": [
            "SOURCE_NORMALIZATION",
            "PRESENTATION_READINESS",
            "MODE_FILTERING",
            "SETTINGS_SUMMARY",
            "SECTION_COMPOSITION",
            "BADGE_COMPOSITION",
            "ACTION_COMPOSITION",
            "VIEW_COMPOSITION",
            "SNAPSHOT",
            "VALIDATION",
            "DIAGNOSTICS",
        ],

        "outputs": [
            "SETTINGS_PAGE_VIEW",
            "SETTINGS_PAGE_COMPOSITION",
            "SETTINGS_PAGE_SNAPSHOT",
            "SETTINGS_PAGE_HEALTH",
            "SETTINGS_PAGE_DIAGNOSTICS",
        ],

        "authority_owners": {
            "settings": "SETTINGS_SERVICE",
            "preferences": "PREFERENCE_SERVICE",
            "notification_preferences":
                "NOTIFICATION_PREFERENCE_SERVICE",
            "authentication":
                "AUTHENTICATION_LAYER",
            "credentials":
                "CREDENTIAL_SECURITY_LAYER",
            "security":
                "SECURITY_LAYER",
            "billing":
                "BILLING_SERVICE",
            "subscription":
                "SUBSCRIBER_SERVICE",
            "entitlement":
                "ENTITLEMENT_SERVICE",
            "market_data":
                "MARKET_DATA_LAYER",
            "evidence":
                "EVIDENCE_CORTEX",
            "market_context":
                "MARKET_CONTEXT_LAYER",
            "intelligence":
                "INTELLIGENCE_LAYER",
            "decision":
                "DECISION_CORTEX",
            "d13":
                "D13_DECISION_AUTHORITY",
            "risk":
                "RISK_LAYER",
            "cas":
                "CAS",
            "execution":
                "EXECUTION_LAYER",
        },

        "principles": [
            "PRESENTATION_ONLY",
            "UPSTREAM_TRUTH_PRESERVED",
            "NO_FAKE_SETTINGS_TRUTH",
            "NO_PREFERENCE_MUTATION",
            "NO_NOTIFICATION_PREFERENCE_MUTATION",
            "NO_AUTHENTICATION_MUTATION",
            "NO_CREDENTIAL_MUTATION",
            "NO_SECURITY_MUTATION",
            "NO_BILLING_MUTATION",
            "NO_SUBSCRIPTION_MUTATION",
            "NO_ENTITLEMENT_MUTATION",
            "NO_INTELLIGENCE_GENERATION",
            "NO_EVIDENCE_GENERATION",
            "NO_DECISION_GENERATION",
            "NO_D13_MUTATION",
            "NO_RISK_OVERRIDE",
            "NO_CAS_BYPASS",
            "NO_EXECUTION",
            "NO_ORDER_MUTATION",
            "NO_POSITION_MUTATION",
            "NO_UPSTREAM_MUTATION",
        ],
    }


# ============================================================================
# FINAL MODULE VALIDATION
# ============================================================================


def validate_settings_page_module() -> Dict[str, Any]:
    """
    Full module-level validation.

    This validates contracts and authority boundaries only.
    """

    module_result = settings_page_module_check()

    controller = create_default_settings_page()

    source = SettingsSourceState(
        identity=SettingsIdentityView(
            authenticated=False
        ),
        preferences=[],
        source_available=False,
        source_errors=[
            "DEFAULT_SETTINGS_SOURCE_NOT_CONNECTED"
        ],
    )

    composition = controller.initialize(
        source
    )

    errors: List[str] = []

    errors.extend(
        validate_settings_source(
            source
        )
    )

    errors.extend(
        validate_settings_page_state(
            controller.state
        )
    )

    errors.extend(
        validate_settings_composition(
            composition
        )
    )

    errors.extend(
        validate_settings_snapshot(
            build_settings_page_snapshot(
                controller,
                source,
            )
        )
    )

    errors.extend(
        validate_settings_authority(
            composition.page.metadata
        )
    )

    manifest = settings_page_contract_manifest()

    if manifest.get("layer") != "UI_PRESENTATION":
        errors.append(
            "INVALID_SETTINGS_CONTRACT_LAYER"
        )

    if "SETTINGS_PRESENTATION" not in (
        manifest.get("responsibilities") or []
    ):
        errors.append(
            "SETTINGS_PRESENTATION_RESPONSIBILITY_MISSING"
        )

    forbidden_principles = {
        "NO_PREFERENCE_MUTATION",
        "NO_D13_MUTATION",
        "NO_RISK_OVERRIDE",
        "NO_CAS_BYPASS",
        "NO_EXECUTION",
    }

    manifest_principles = set(
        manifest.get("principles") or []
    )

    missing_principles = (
        forbidden_principles - manifest_principles
    )

    for principle in sorted(
        missing_principles
    ):
        errors.append(
            f"CONTRACT_PRINCIPLE_MISSING:{principle}"
        )

    return {
        "engine": SETTINGS_PAGE_ENGINE,
        "version": SETTINGS_PAGE_VERSION,
        "valid": (
            module_result.get("valid", False)
            and not errors
        ),
        "errors": errors,
        "authority_valid": not bool(
            validate_settings_authority(
                composition.page.metadata
            )
        ),
        "contract_valid": not bool(
            missing_principles
        ),
        "ui_only": True,
        "presentation_only": True,

        "settings_mutation": False,
        "preference_mutation": False,
        "notification_preference_mutation": False,
        "authentication_mutation": False,
        "credential_mutation": False,
        "security_mutation": False,
        "billing_mutation": False,
        "subscription_mutation": False,
        "entitlement_mutation": False,

        "market_intelligence_generation": False,
        "evidence_generation": False,
        "decision_generation": False,
        "d13_modification": False,
        "risk_generation": False,
        "risk_override": False,
        "cas_generation": False,
        "cas_bypass": False,

        "execution": False,
        "order_mutation": False,
        "position_mutation": False,
        "upstream_mutation": False,
    }


# ============================================================================
# DEFAULT SNAPSHOT
# ============================================================================


def default_settings_page_snapshot(
) -> SettingsPageSnapshot:
    controller = create_default_settings_page()

    source = SettingsSourceState(
        identity=SettingsIdentityView(
            authenticated=False
        ),
        preferences=[],
        source_available=False,
        source_errors=[
            "DEFAULT_SETTINGS_SOURCE_NOT_CONNECTED"
        ],
    )

    return build_settings_page_snapshot(
        controller=controller,
        source=source,
    )


# ============================================================================
# FINAL EXPORTS
# ============================================================================

__all__.extend([
    # Final utilities
    "refresh_settings_page",
    "get_settings_page",
    "can_navigate_settings_page",
    "select_settings_route",
    "lock_settings_page",

    # Diagnostics
    "diagnose_settings_page",

    # Architecture
    "settings_page_contract_manifest",
    "validate_settings_page_module",

    # Defaults
    "default_settings_page_snapshot",
])
