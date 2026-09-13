from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


# ============================================================
# ROBOMLM_PLUS — DISCOVERY PAGE
# Opportunity Discovery / Scanner Presentation Surface
# ============================================================

DISCOVERY_PAGE_ENGINE = "ROBOMLM_PLUS_UI_DISCOVERY"
DISCOVERY_PAGE_VERSION = "1.0"

DISCOVERY_PAGE_NAME = "Discovery"
DISCOVERY_PAGE_TITLE = "Opportunity Discovery"

DISCOVERY_PAGE_DESCRIPTION = (
    "ROBOMLM opportunity discovery workspace for presenting "
    "upstream market opportunities, scanner results, "
    "watchlists and discovery intelligence."
)

DISCOVERY_ROUTE = "/discovery"


# ============================================================
# AUTHORITY BOUNDARY
# ============================================================

DISCOVERY_UI_AUTHORITY: Dict[str, bool] = {

    # --------------------------------------------------------
    # Allowed presentation responsibilities
    # --------------------------------------------------------

    "discovery_presentation": True,
    "opportunity_presentation": True,
    "scanner_presentation": True,
    "market_selection": True,
    "instrument_selection": True,
    "contract_selection": True,
    "watchlist_presentation": True,
    "favorites_presentation": True,
    "discovery_navigation": True,
    "filter_presentation": True,
    "sorting_presentation": True,
    "display_configuration": True,

    # --------------------------------------------------------
    # Forbidden authority
    # --------------------------------------------------------

    "market_data_generation": False,
    "evidence_generation": False,
    "intelligence_generation": False,
    "decision_generation": False,

    "d13_modification": False,

    "risk_generation": False,
    "risk_override": False,

    "cas_generation": False,
    "cas_bypass": False,

    "execution": False,
    "order_authority": False,
    "order_mutation": False,

    "position_authority": False,
    "position_mutation": False,

    "portfolio_mutation": False,

    "scanner_intelligence_generation": False,
    "opportunity_generation": False,

    "upstream_mutation": False,
}


# ============================================================
# ENUMS
# ============================================================

class DiscoveryPageStatus(str, Enum):
    LOADING = "LOADING"
    READY = "READY"
    DEGRADED = "DEGRADED"
    LOCKED = "LOCKED"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class DiscoveryMode(str, Enum):
    OVERVIEW = "OVERVIEW"
    UNIVERSAL = "UNIVERSAL"
    STOCKS = "STOCKS"
    INDICES = "INDICES"
    COMMODITIES = "COMMODITIES"
    CRYPTO = "CRYPTO"
    FX = "FX"
    FAVORITES = "FAVORITES"
    UNKNOWN = "UNKNOWN"


class DiscoveryAssetClass(str, Enum):
    STOCK = "STOCK"
    INDEX = "INDEX"
    COMMODITY = "COMMODITY"
    CRYPTO = "CRYPTO"
    FX = "FX"
    UNKNOWN = "UNKNOWN"


class OpportunityState(str, Enum):
    UNKNOWN = "UNKNOWN"
    WATCH = "WATCH"
    DEVELOPING = "DEVELOPING"
    QUALIFIED = "QUALIFIED"
    INVALIDATED = "INVALIDATED"
    EXPIRED = "EXPIRED"


class OpportunityBias(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"


class OpportunityStrength(str, Enum):
    VERY_WEAK = "VERY_WEAK"
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    VERY_STRONG = "VERY_STRONG"
    UNKNOWN = "UNKNOWN"


class DiscoveryPriority(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DiscoveryBadgeType(str, Enum):
    STATUS = "STATUS"
    ASSET_CLASS = "ASSET_CLASS"
    BIAS = "BIAS"
    STRENGTH = "STRENGTH"
    FAVORITE = "FAVORITE"
    CUSTOM = "CUSTOM"


# ============================================================
# HELPERS
# ============================================================

def _discovery_text(
    value: Any,
    default: str = "",
) -> str:

    if value is None:
        return default

    text = str(value).strip()

    return text if text else default


def _discovery_bool(
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


def _discovery_enum(
    enum_cls: Any,
    value: Any,
    default: Any,
) -> Any:

    if isinstance(value, enum_cls):
        return value

    try:
        return enum_cls(value)

    except (TypeError, ValueError):
        return default


def _discovery_float(
    value: Any,
    default: float = 0.0,
) -> float:

    try:
        return float(value)

    except (TypeError, ValueError):
        return default


def _discovery_now() -> datetime:
    return datetime.now(
        timezone.utc
    )


# ============================================================
# IDENTITY VIEW
# ============================================================

@dataclass
class DiscoveryIdentityView:

    user_id: str = ""

    display_name: str = ""

    email: str = ""

    authenticated: bool = False

    plus_enabled: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# MARKET SELECTION VIEW
# ============================================================

@dataclass
class DiscoveryMarketView:

    market_id: str = ""

    market_name: str = ""

    asset_class: DiscoveryAssetClass = (
        DiscoveryAssetClass.UNKNOWN
    )

    region: str = ""

    timezone: str = ""

    market_state: str = ""

    selected: bool = False

    visible: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# INSTRUMENT VIEW
# ============================================================

@dataclass
class DiscoveryInstrumentView:

    instrument_id: str = ""

    symbol: str = ""

    display_name: str = ""

    asset_class: DiscoveryAssetClass = (
        DiscoveryAssetClass.UNKNOWN
    )

    exchange: str = ""

    currency: str = ""

    selected: bool = False

    visible: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# OPPORTUNITY VIEW
# ============================================================

@dataclass
class OpportunityView:

    opportunity_id: str = ""

    symbol: str = ""

    instrument_name: str = ""

    asset_class: DiscoveryAssetClass = (
        DiscoveryAssetClass.UNKNOWN
    )

    state: OpportunityState = (
        OpportunityState.UNKNOWN
    )

    bias: OpportunityBias = (
        OpportunityBias.UNKNOWN
    )

    strength: OpportunityStrength = (
        OpportunityStrength.UNKNOWN
    )

    summary: str = ""

    confidence: float = 0.0

    timestamp: Optional[
        datetime
    ] = None

    favorite: bool = False

    visible: bool = True

    priority: DiscoveryPriority = (
        DiscoveryPriority.NORMAL
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# WATCHLIST VIEW
# ============================================================

@dataclass
class DiscoveryWatchlistView:

    watchlist_id: str = ""

    name: str = ""

    instrument_ids: List[str] = field(
        default_factory=list
    )

    opportunity_ids: List[str] = field(
        default_factory=list
    )

    selected: bool = False

    visible: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# FAVORITE VIEW
# ============================================================

@dataclass
class DiscoveryFavoriteView:

    favorite_id: str = ""

    symbol: str = ""

    instrument_id: str = ""

    asset_class: DiscoveryAssetClass = (
        DiscoveryAssetClass.UNKNOWN
    )

    note: str = ""

    visible: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# BADGE
# ============================================================

@dataclass
class DiscoveryBadge:

    badge_type: DiscoveryBadgeType = (
        DiscoveryBadgeType.STATUS
    )

    label: str = ""

    value: str = ""

    priority: DiscoveryPriority = (
        DiscoveryPriority.NORMAL
    )

    visible: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# SUMMARY
# ============================================================

@dataclass
class DiscoverySummaryView:

    total_opportunities: int = 0

    visible_opportunities: int = 0

    qualified_opportunities: int = 0

    developing_opportunities: int = 0

    watch_opportunities: int = 0

    invalidated_opportunities: int = 0

    favorite_count: int = 0

    selected_market_count: int = 0

    selected_instrument_count: int = 0

    authenticated: bool = False

    plus_enabled: bool = False

    priority: DiscoveryPriority = (
        DiscoveryPriority.NORMAL
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )
# ============================================================
# ROBOMLM_PLUS — DISCOVERY PAGE
# PART 2 — SOURCE STATE / NORMALIZATION / FILTERING / SUMMARY
# ============================================================

@dataclass
class DiscoverySourceState:
    identity: DiscoveryIdentityView
    markets: List[DiscoveryMarketView] = field(default_factory=list)
    instruments: List[DiscoveryInstrumentView] = field(default_factory=list)
    opportunities: List[OpportunityView] = field(default_factory=list)
    watchlists: List[DiscoveryWatchlistView] = field(default_factory=list)
    favorites: List[DiscoveryFavoriteView] = field(default_factory=list)
    source_available: bool = True
    source_errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


DEFAULT_DISCOVERY_MODES = {
    DiscoveryMode.OVERVIEW: "All Opportunities",
    DiscoveryMode.UNIVERSAL: "Universal",
    DiscoveryMode.STOCKS: "Stocks",
    DiscoveryMode.INDICES: "Indices",
    DiscoveryMode.COMMODITIES: "Commodities",
    DiscoveryMode.CRYPTO: "Crypto",
    DiscoveryMode.FX: "Forex",
    DiscoveryMode.FAVORITES: "Favorites",
}


DISCOVERY_MODE_ASSET_CLASS = {
    DiscoveryMode.STOCKS: DiscoveryAssetClass.STOCK,
    DiscoveryMode.INDICES: DiscoveryAssetClass.INDEX,
    DiscoveryMode.COMMODITIES: DiscoveryAssetClass.COMMODITY,
    DiscoveryMode.CRYPTO: DiscoveryAssetClass.CRYPTO,
    DiscoveryMode.FX: DiscoveryAssetClass.FX,
}


def normalize_discovery_identity(
    value: Optional[DiscoveryIdentityView] = None,
) -> DiscoveryIdentityView:
    if value is None:
        return DiscoveryIdentityView(
            user_id="",
            display_name="Guest",
            email="",
            authenticated=False,
            plus_enabled=False,
            metadata={},
        )

    return DiscoveryIdentityView(
        user_id=_discovery_text(value.user_id),
        display_name=_discovery_text(value.display_name, "Guest"),
        email=_discovery_text(value.email),
        authenticated=_discovery_bool(value.authenticated),
        plus_enabled=_discovery_bool(value.plus_enabled),
        metadata=dict(value.metadata or {}),
    )


def normalize_discovery_market(
    value: DiscoveryMarketView,
) -> DiscoveryMarketView:
    return DiscoveryMarketView(
        market_id=_discovery_text(value.market_id),
        market_name=_discovery_text(value.market_name),
        asset_class=_discovery_enum(
            value.asset_class,
            DiscoveryAssetClass,
            DiscoveryAssetClass.UNKNOWN,
        ),
        region=_discovery_text(value.region),
        timezone=_discovery_text(value.timezone),
        market_state=_discovery_text(value.market_state, "UNKNOWN"),
        selected=_discovery_bool(value.selected),
        visible=_discovery_bool(value.visible, True),
        metadata=dict(value.metadata or {}),
    )


def normalize_discovery_instrument(
    value: DiscoveryInstrumentView,
) -> DiscoveryInstrumentView:
    return DiscoveryInstrumentView(
        instrument_id=_discovery_text(value.instrument_id),
        symbol=_discovery_text(value.symbol),
        display_name=_discovery_text(value.display_name),
        asset_class=_discovery_enum(
            value.asset_class,
            DiscoveryAssetClass,
            DiscoveryAssetClass.UNKNOWN,
        ),
        exchange=_discovery_text(value.exchange),
        currency=_discovery_text(value.currency),
        selected=_discovery_bool(value.selected),
        visible=_discovery_bool(value.visible, True),
        metadata=dict(value.metadata or {}),
    )


def normalize_opportunity(
    value: OpportunityView,
) -> OpportunityView:
    return OpportunityView(
        opportunity_id=_discovery_text(value.opportunity_id),
        symbol=_discovery_text(value.symbol),
        instrument_name=_discovery_text(value.instrument_name),
        asset_class=_discovery_enum(
            value.asset_class,
            DiscoveryAssetClass,
            DiscoveryAssetClass.UNKNOWN,
        ),
        state=_discovery_enum(
            value.state,
            OpportunityState,
            OpportunityState.UNKNOWN,
        ),
        bias=_discovery_enum(
            value.bias,
            OpportunityBias,
            OpportunityBias.UNKNOWN,
        ),
        strength=_discovery_enum(
            value.strength,
            OpportunityStrength,
            OpportunityStrength.UNKNOWN,
        ),
        summary=_discovery_text(value.summary),
        confidence=_discovery_float(value.confidence),
        timestamp=_discovery_text(value.timestamp),
        favorite=_discovery_bool(value.favorite),
        visible=_discovery_bool(value.visible, True),
        priority=_discovery_enum(
            value.priority,
            DiscoveryPriority,
            DiscoveryPriority.NORMAL,
        ),
        metadata=dict(value.metadata or {}),
    )


def normalize_discovery_watchlist(
    value: DiscoveryWatchlistView,
) -> DiscoveryWatchlistView:
    return DiscoveryWatchlistView(
        watchlist_id=_discovery_text(value.watchlist_id),
        name=_discovery_text(value.name),
        instrument_ids=list(value.instrument_ids or []),
        opportunity_ids=list(value.opportunity_ids or []),
        selected=_discovery_bool(value.selected),
        visible=_discovery_bool(value.visible, True),
        metadata=dict(value.metadata or {}),
    )


def normalize_discovery_favorite(
    value: DiscoveryFavoriteView,
) -> DiscoveryFavoriteView:
    return DiscoveryFavoriteView(
        favorite_id=_discovery_text(value.favorite_id),
        symbol=_discovery_text(value.symbol),
        instrument_id=_discovery_text(value.instrument_id),
        asset_class=_discovery_enum(
            value.asset_class,
            DiscoveryAssetClass,
            DiscoveryAssetClass.UNKNOWN,
        ),
        note=_discovery_text(value.note),
        visible=_discovery_bool(value.visible, True),
        metadata=dict(value.metadata or {}),
    )


def normalize_discovery_source_state(
    source: Optional[DiscoverySourceState] = None,
) -> DiscoverySourceState:
    if source is None:
        return DiscoverySourceState(
            identity=normalize_discovery_identity(),
            markets=[],
            instruments=[],
            opportunities=[],
            watchlists=[],
            favorites=[],
            source_available=False,
            source_errors=["Discovery source is not connected."],
            metadata={
                "source_state": "DISCONNECTED",
                "presentation_only": True,
            },
        )

    return DiscoverySourceState(
        identity=normalize_discovery_identity(source.identity),
        markets=[
            normalize_discovery_market(item)
            for item in (source.markets or [])
        ],
        instruments=[
            normalize_discovery_instrument(item)
            for item in (source.instruments or [])
        ],
        opportunities=[
            normalize_opportunity(item)
            for item in (source.opportunities or [])
        ],
        watchlists=[
            normalize_discovery_watchlist(item)
            for item in (source.watchlists or [])
        ],
        favorites=[
            normalize_discovery_favorite(item)
            for item in (source.favorites or [])
        ],
        source_available=_discovery_bool(source.source_available),
        source_errors=[
            _discovery_text(error)
            for error in (source.source_errors or [])
            if _discovery_text(error)
        ],
        metadata=dict(source.metadata or {}),
    )


def evaluate_discovery_status(
    source: DiscoverySourceState,
) -> DiscoveryPageStatus:
    if not source.identity.authenticated:
        return DiscoveryPageStatus.LOCKED

    if not source.source_available:
        return DiscoveryPageStatus.DEGRADED

    if source.source_errors:
        return DiscoveryPageStatus.DEGRADED

    return DiscoveryPageStatus.READY


def filter_discovery_markets(
    markets: List[DiscoveryMarketView],
    mode: DiscoveryMode,
) -> List[DiscoveryMarketView]:
    markets = [
        item for item in markets
        if item.visible
    ]

    asset_class = DISCOVERY_MODE_ASSET_CLASS.get(mode)

    if asset_class is None:
        return markets

    return [
        item for item in markets
        if item.asset_class == asset_class
    ]


def filter_discovery_instruments(
    instruments: List[DiscoveryInstrumentView],
    mode: DiscoveryMode,
) -> List[DiscoveryInstrumentView]:
    instruments = [
        item for item in instruments
        if item.visible
    ]

    asset_class = DISCOVERY_MODE_ASSET_CLASS.get(mode)

    if asset_class is None:
        return instruments

    return [
        item for item in instruments
        if item.asset_class == asset_class
    ]


def filter_discovery_opportunities(
    opportunities: List[OpportunityView],
    mode: DiscoveryMode,
    include_invalidated: bool = False,
) -> List[OpportunityView]:
    result = [
        item for item in opportunities
        if item.visible
    ]

    if not include_invalidated:
        result = [
            item for item in result
            if item.state not in {
                OpportunityState.INVALIDATED,
                OpportunityState.EXPIRED,
            }
        ]

    if mode == DiscoveryMode.FAVORITES:
        return [
            item for item in result
            if item.favorite
        ]

    asset_class = DISCOVERY_MODE_ASSET_CLASS.get(mode)

    if asset_class is None:
        return result

    return [
        item for item in result
        if item.asset_class == asset_class
    ]


def filter_discovery_favorites(
    favorites: List[DiscoveryFavoriteView],
    mode: DiscoveryMode,
) -> List[DiscoveryFavoriteView]:
    result = [
        item for item in favorites
        if item.visible
    ]

    if mode != DiscoveryMode.FAVORITES:
        return result

    return result


def build_discovery_summary(
    source: DiscoverySourceState,
    opportunities: List[OpportunityView],
    markets: List[DiscoveryMarketView],
    instruments: List[DiscoveryInstrumentView],
) -> DiscoverySummaryView:
    qualified = sum(
        1 for item in opportunities
        if item.state == OpportunityState.QUALIFIED
    )

    developing = sum(
        1 for item in opportunities
        if item.state == OpportunityState.DEVELOPING
    )

    watch = sum(
        1 for item in opportunities
        if item.state == OpportunityState.WATCH
    )

    invalidated = sum(
        1 for item in opportunities
        if item.state == OpportunityState.INVALIDATED
    )

    favorites = sum(
        1 for item in opportunities
        if item.favorite
    )

    selected_markets = sum(
        1 for item in markets
        if item.selected
    )

    selected_instruments = sum(
        1 for item in instruments
        if item.selected
    )

    priority = DiscoveryPriority.NORMAL

    if qualified > 0:
        priority = DiscoveryPriority.HIGH

    if any(
        item.priority == DiscoveryPriority.CRITICAL
        for item in opportunities
    ):
        priority = DiscoveryPriority.CRITICAL

    return DiscoverySummaryView(
        total_opportunities=len(source.opportunities),
        visible_opportunities=len(opportunities),
        qualified_opportunities=qualified,
        developing_opportunities=developing,
        watch_opportunities=watch,
        invalidated_opportunities=invalidated,
        favorite_count=favorites,
        selected_market_count=selected_markets,
        selected_instrument_count=selected_instruments,
        authenticated=source.identity.authenticated,
        plus_enabled=source.identity.plus_enabled,
        priority=priority,
        metadata={
            "summary_source": "UPSTREAM_DISCOVERY_OUTPUT",
            "opportunity_scoring": False,
            "opportunity_generation": False,
            "intelligence_generation": False,
            "presentation_only": True,
        },
    )


def resolve_discovery_display_name(
    identity: DiscoveryIdentityView,
) -> str:
    if identity.display_name:
        return identity.display_name

    if identity.user_id:
        return identity.user_id

    return "Guest"


def build_discovery_status_message(
    status: DiscoveryPageStatus,
) -> str:
    messages = {
        DiscoveryPageStatus.LOADING:
            "Loading discovery intelligence.",
        DiscoveryPageStatus.READY:
            "Discovery intelligence is available.",
        DiscoveryPageStatus.DEGRADED:
            "Discovery data is partially unavailable.",
        DiscoveryPageStatus.LOCKED:
            "Authentication is required to access Discovery.",
        DiscoveryPageStatus.ERROR:
            "Discovery presentation encountered an error.",
        DiscoveryPageStatus.UNKNOWN:
            "Discovery status is unavailable.",
    }

    return messages.get(
        status,
        "Discovery status is unavailable.",
    )


def build_discovery_mode_message(
    mode: DiscoveryMode,
) -> str:
    return DEFAULT_DISCOVERY_MODES.get(
        mode,
        "Discovery",
    )
# ============================================================
# ROBOMLM_PLUS — DISCOVERY PAGE
# PART 3 — VIEW / COMPOSITION / INTERACTION / STATE / CONTROLLER
# ============================================================

@dataclass
class DiscoveryAction:
    action_id: str
    label: str
    route: str
    enabled: bool = True
    visible: bool = True
    requires_authentication: bool = True
    priority: DiscoveryPriority = DiscoveryPriority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)


DEFAULT_DISCOVERY_ACTIONS = [
    DiscoveryAction("overview", "Overview", "/discovery"),
    DiscoveryAction("universal", "Universal", "/discovery/universal"),
    DiscoveryAction("stocks", "Stocks", "/discovery/stocks"),
    DiscoveryAction("indices", "Indices", "/discovery/indices"),
    DiscoveryAction("commodities", "Commodities", "/discovery/commodities"),
    DiscoveryAction("crypto", "Crypto", "/discovery/crypto"),
    DiscoveryAction("fx", "Forex", "/discovery/fx"),
    DiscoveryAction("favorites", "Favorites", "/discovery/favorites"),
]


def build_discovery_actions(
    authenticated: bool = False,
) -> List[DiscoveryAction]:
    result = []

    for action in DEFAULT_DISCOVERY_ACTIONS:
        item = DiscoveryAction(
            action_id=action.action_id,
            label=action.label,
            route=action.route,
            enabled=authenticated,
            visible=True,
            requires_authentication=True,
            priority=action.priority,
            metadata=dict(action.metadata or {}),
        )
        result.append(item)

    return result


@dataclass
class DiscoveryPageView:
    page_name: str
    page_title: str
    route: str
    status: DiscoveryPageStatus
    mode: DiscoveryMode
    identity: DiscoveryIdentityView
    markets: List[DiscoveryMarketView]
    instruments: List[DiscoveryInstrumentView]
    opportunities: List[OpportunityView]
    watchlists: List[DiscoveryWatchlistView]
    favorites: List[DiscoveryFavoriteView]
    badges: List[DiscoveryBadge]
    actions: List[DiscoveryAction]
    summary: DiscoverySummaryView
    authenticated: bool
    plus_enabled: bool
    generated_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DiscoveryPageComposition:
    page: DiscoveryPageView
    summary: DiscoverySummaryView
    markets: List[DiscoveryMarketView]
    instruments: List[DiscoveryInstrumentView]
    opportunities: List[OpportunityView]
    watchlists: List[DiscoveryWatchlistView]
    favorites: List[DiscoveryFavoriteView]
    warnings: List[str]
    errors: List[str]
    generated_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)


def build_discovery_badges(
    status: DiscoveryPageStatus,
    mode: DiscoveryMode,
    summary: DiscoverySummaryView,
) -> List[DiscoveryBadge]:
    badges = [
        DiscoveryBadge(
            badge_type=DiscoveryBadgeType.STATUS,
            label="Status",
            value=status.value,
            priority=DiscoveryPriority.NORMAL,
            visible=True,
            metadata={"presentation_only": True},
        ),
        DiscoveryBadge(
            badge_type=DiscoveryBadgeType.CUSTOM,
            label="Mode",
            value=DEFAULT_DISCOVERY_MODES.get(mode, "Discovery"),
            priority=DiscoveryPriority.NORMAL,
            visible=True,
            metadata={"presentation_only": True},
        ),
    ]

    if summary.qualified_opportunities > 0:
        badges.append(
            DiscoveryBadge(
                badge_type=DiscoveryBadgeType.STRENGTH,
                label="Qualified",
                value=str(summary.qualified_opportunities),
                priority=DiscoveryPriority.HIGH,
                visible=True,
                metadata={"source": "UPSTREAM_OPPORTUNITY_STATE"},
            )
        )

    if summary.favorite_count > 0:
        badges.append(
            DiscoveryBadge(
                badge_type=DiscoveryBadgeType.FAVORITE,
                label="Favorites",
                value=str(summary.favorite_count),
                priority=DiscoveryPriority.NORMAL,
                visible=True,
                metadata={"presentation_only": True},
            )
        )

    return badges


def compose_discovery_page(
    source: Optional[DiscoverySourceState] = None,
    mode: DiscoveryMode = DiscoveryMode.OVERVIEW,
) -> DiscoveryPageComposition:
    source = normalize_discovery_source_state(source)

    mode = _discovery_enum(
        mode,
        DiscoveryMode,
        DiscoveryMode.OVERVIEW,
    )

    status = evaluate_discovery_status(source)

    markets = filter_discovery_markets(
        source.markets,
        mode,
    )

    instruments = filter_discovery_instruments(
        source.instruments,
        mode,
    )

    opportunities = filter_discovery_opportunities(
        source.opportunities,
        mode,
    )

    favorites = filter_discovery_favorites(
        source.favorites,
        mode,
    )

    watchlists = [
        item for item in source.watchlists
        if item.visible
    ]

    summary = build_discovery_summary(
        source=source,
        opportunities=opportunities,
        markets=markets,
        instruments=instruments,
    )

    badges = build_discovery_badges(
        status=status,
        mode=mode,
        summary=summary,
    )

    actions = build_discovery_actions(
        authenticated=source.identity.authenticated,
    )

    warnings = list(source.source_errors)

    page = DiscoveryPageView(
        page_name=DISCOVERY_PAGE_NAME,
        page_title=DISCOVERY_PAGE_TITLE,
        route=DISCOVERY_ROUTE,
        status=status,
        mode=mode,
        identity=source.identity,
        markets=markets,
        instruments=instruments,
        opportunities=opportunities,
        watchlists=watchlists,
        favorites=favorites,
        badges=badges,
        actions=actions,
        summary=summary,
        authenticated=source.identity.authenticated,
        plus_enabled=source.identity.plus_enabled,
        generated_at=_discovery_now(),
        metadata={
            "ui_only": True,
            "presentation_only": True,
            "upstream_opportunity_truth": True,
            "scanner_generation": False,
            "opportunity_generation": False,
            "opportunity_scoring": False,
            "market_data_generation": False,
            "evidence_generation": False,
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
            "upstream_mutation": False,
        },
    )

    return DiscoveryPageComposition(
        page=page,
        summary=summary,
        markets=markets,
        instruments=instruments,
        opportunities=opportunities,
        watchlists=watchlists,
        favorites=favorites,
        warnings=warnings,
        errors=[],
        generated_at=_discovery_now(),
        metadata={
            "presentation_only": True,
            "opportunity_generation": False,
            "scanner_generation": False,
            "intelligence_generation": False,
            "decision_generation": False,
            "d13_modification": False,
            "risk_override": False,
            "cas_bypass": False,
            "execution": False,
            "upstream_mutation": False,
        },
    )


class DiscoveryInteraction(str, Enum):
    OPEN_OVERVIEW = "OPEN_OVERVIEW"
    OPEN_UNIVERSAL = "OPEN_UNIVERSAL"
    OPEN_STOCKS = "OPEN_STOCKS"
    OPEN_INDICES = "OPEN_INDICES"
    OPEN_COMMODITIES = "OPEN_COMMODITIES"
    OPEN_CRYPTO = "OPEN_CRYPTO"
    OPEN_FX = "OPEN_FX"
    OPEN_FAVORITES = "OPEN_FAVORITES"
    REFRESH = "REFRESH"
    NONE = "NONE"


DISCOVERY_INTERACTION_ROUTES = {
    DiscoveryInteraction.OPEN_OVERVIEW: "/discovery",
    DiscoveryInteraction.OPEN_UNIVERSAL: "/discovery/universal",
    DiscoveryInteraction.OPEN_STOCKS: "/discovery/stocks",
    DiscoveryInteraction.OPEN_INDICES: "/discovery/indices",
    DiscoveryInteraction.OPEN_COMMODITIES: "/discovery/commodities",
    DiscoveryInteraction.OPEN_CRYPTO: "/discovery/crypto",
    DiscoveryInteraction.OPEN_FX: "/discovery/fx",
    DiscoveryInteraction.OPEN_FAVORITES: "/discovery/favorites",
}


def normalize_discovery_interaction(
    value: Any,
) -> DiscoveryInteraction:
    return _discovery_enum(
        value,
        DiscoveryInteraction,
        DiscoveryInteraction.NONE,
    )


@dataclass
class DiscoveryPageState:
    user_id: str = ""
    authenticated: bool = False
    plus_enabled: bool = False
    mode: DiscoveryMode = DiscoveryMode.OVERVIEW
    status: DiscoveryPageStatus = DiscoveryPageStatus.LOCKED
    current_route: str = DISCOVERY_ROUTE
    initialized: bool = False
    ready: bool = False
    locked: bool = True
    interaction_count: int = 0
    refresh_count: int = 0
    last_interaction: DiscoveryInteraction = DiscoveryInteraction.NONE
    last_error: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


def create_discovery_page_state(
    authenticated: bool = False,
    plus_enabled: bool = False,
) -> DiscoveryPageState:
    return DiscoveryPageState(
        authenticated=authenticated,
        plus_enabled=plus_enabled,
        status=(
            DiscoveryPageStatus.LOADING
            if authenticated
            else DiscoveryPageStatus.LOCKED
        ),
        initialized=False,
        ready=False,
        locked=not authenticated,
    )


DISCOVERY_ROUTE_MODES = {
    "/discovery": DiscoveryMode.OVERVIEW,
    "/discovery/universal": DiscoveryMode.UNIVERSAL,
    "/discovery/stocks": DiscoveryMode.STOCKS,
    "/discovery/indices": DiscoveryMode.INDICES,
    "/discovery/commodities": DiscoveryMode.COMMODITIES,
    "/discovery/crypto": DiscoveryMode.CRYPTO,
    "/discovery/fx": DiscoveryMode.FX,
    "/discovery/favorites": DiscoveryMode.FAVORITES,
}


def route_to_discovery_mode(
    route: str,
) -> DiscoveryMode:
    return DISCOVERY_ROUTE_MODES.get(
        _discovery_text(route),
        DiscoveryMode.UNKNOWN,
    )


def evaluate_discovery_route_access(
    route: str,
    authenticated: bool,
    locked: bool = False,
) -> bool:
    route = _discovery_text(route)

    if route not in DISCOVERY_ROUTE_MODES:
        return False

    if not authenticated:
        return False

    if locked:
        return False

    return True


@dataclass
class DiscoveryInteractionResult:
    interaction: DiscoveryInteraction
    requested_route: str
    resolved_route: str
    allowed: bool
    reason: str
    mode: DiscoveryMode
    metadata: Dict[str, Any] = field(default_factory=dict)


def resolve_discovery_interaction(
    interaction: DiscoveryInteraction,
    state: DiscoveryPageState,
) -> DiscoveryInteractionResult:
    interaction = normalize_discovery_interaction(interaction)

    if interaction == DiscoveryInteraction.NONE:
        return DiscoveryInteractionResult(
            interaction=interaction,
            requested_route="",
            resolved_route=state.current_route,
            allowed=False,
            reason="NO_INTERACTION",
            mode=state.mode,
        )

    if interaction == DiscoveryInteraction.REFRESH:
        allowed = state.authenticated and not state.locked

        return DiscoveryInteractionResult(
            interaction=interaction,
            requested_route=state.current_route,
            resolved_route=state.current_route,
            allowed=allowed,
            reason="ALLOWED" if allowed else "ACCESS_DENIED",
            mode=state.mode,
        )

    route = DISCOVERY_INTERACTION_ROUTES.get(
        interaction,
        "",
    )

    allowed = evaluate_discovery_route_access(
        route,
        state.authenticated,
        state.locked,
    )

    mode = route_to_discovery_mode(route)

    return DiscoveryInteractionResult(
        interaction=interaction,
        requested_route=route,
        resolved_route=route if allowed else state.current_route,
        allowed=allowed,
        reason="ALLOWED" if allowed else "ACCESS_DENIED",
        mode=mode if allowed else state.mode,
        metadata={
            "presentation_only": True,
            "authority_change": False,
        },
    )


class DiscoveryPageController:
    def __init__(
        self,
        state: Optional[DiscoveryPageState] = None,
    ):
        self._state = state or create_discovery_page_state()
        self._interaction_history: List[DiscoveryInteractionResult] = []
        self._last_composition: Optional[
            DiscoveryPageComposition
        ] = None

    @property
    def state(self) -> DiscoveryPageState:
        return self._state

    @property
    def current_route(self) -> str:
        return self._state.current_route

    @property
    def current_mode(self) -> DiscoveryMode:
        return self._state.mode

    @property
    def status(self) -> DiscoveryPageStatus:
        return self._state.status

    @property
    def last_composition(self) -> Optional[DiscoveryPageComposition]:
        return self._last_composition

    def initialize(
        self,
        source: Optional[DiscoverySourceState] = None,
    ) -> DiscoveryPageComposition:
        normalized = normalize_discovery_source_state(source)

        self._state.user_id = normalized.identity.user_id
        self._state.authenticated = normalized.identity.authenticated
        self._state.plus_enabled = normalized.identity.plus_enabled
        self._state.initialized = True
        self._state.locked = not self._state.authenticated

        composition = self.compose(normalized)

        return composition

    def compose(
        self,
        source: Optional[DiscoverySourceState] = None,
    ) -> DiscoveryPageComposition:
        composition = compose_discovery_page(
            source=source,
            mode=self._state.mode,
        )

        self._last_composition = composition
        self._state.status = composition.page.status
        self._state.ready = (
            composition.page.status == DiscoveryPageStatus.READY
            and not self._state.locked
        )

        self._state.last_error = (
            composition.errors[0]
            if composition.errors
            else ""
        )

        return composition

    def interact(
        self,
        interaction: DiscoveryInteraction,
    ) -> DiscoveryInteractionResult:
        result = resolve_discovery_interaction(
            interaction,
            self._state,
        )

        self._state.interaction_count += 1
        self._state.last_interaction = result.interaction

        if result.allowed:
            if result.interaction == DiscoveryInteraction.REFRESH:
                self._state.refresh_count += 1
            else:
                self._state.current_route = result.resolved_route
                self._state.mode = result.mode

        self._interaction_history.append(result)

        if len(self._interaction_history) > 500:
            self._interaction_history = self._interaction_history[-500:]

        return result

    def navigate(
        self,
        route: str,
    ) -> DiscoveryInteractionResult:
        mode = route_to_discovery_mode(route)

        interaction_by_mode = {
            DiscoveryMode.OVERVIEW:
                DiscoveryInteraction.OPEN_OVERVIEW,
            DiscoveryMode.UNIVERSAL:
                DiscoveryInteraction.OPEN_UNIVERSAL,
            DiscoveryMode.STOCKS:
                DiscoveryInteraction.OPEN_STOCKS,
            DiscoveryMode.INDICES:
                DiscoveryInteraction.OPEN_INDICES,
            DiscoveryMode.COMMODITIES:
                DiscoveryInteraction.OPEN_COMMODITIES,
            DiscoveryMode.CRYPTO:
                DiscoveryInteraction.OPEN_CRYPTO,
            DiscoveryMode.FX:
                DiscoveryInteraction.OPEN_FX,
            DiscoveryMode.FAVORITES:
                DiscoveryInteraction.OPEN_FAVORITES,
        }

        interaction = interaction_by_mode.get(
            mode,
            DiscoveryInteraction.NONE,
        )

        return self.interact(interaction)

    def refresh(
        self,
        source: Optional[DiscoverySourceState] = None,
    ) -> DiscoveryPageComposition:
        self._state.refresh_count += 1
        self._state.interaction_count += 1
        self._state.last_interaction = DiscoveryInteraction.REFRESH

        return self.compose(source)

    def lock(self) -> None:
        self._state.locked = True
        self._state.ready = False
        self._state.status = DiscoveryPageStatus.LOCKED

    def unlock(self) -> bool:
        if not self._state.authenticated:
            return False

        self._state.locked = False

        if self._state.status == DiscoveryPageStatus.LOCKED:
            self._state.status = DiscoveryPageStatus.LOADING

        return True

    def set_authenticated(
        self,
        authenticated: bool,
    ) -> None:
        self._state.authenticated = bool(authenticated)

        if not authenticated:
            self._state.locked = True
            self._state.ready = False
            self._state.status = DiscoveryPageStatus.LOCKED
            self._state.current_route = DISCOVERY_ROUTE
            self._state.mode = DiscoveryMode.OVERVIEW
        else:
            self._state.locked = False
            self._state.status = DiscoveryPageStatus.LOADING

    @property
    def interaction_history(
        self,
    ) -> List[DiscoveryInteractionResult]:
        return list(self._interaction_history)

    def clear_interaction_history(self) -> None:
        self._interaction_history.clear()


@dataclass(frozen=True)
class DiscoveryPageSnapshot:
    state: DiscoveryPageState
    composition: DiscoveryPageComposition
    captured_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)


def build_discovery_page_snapshot(
    controller: DiscoveryPageController,
    source: Optional[DiscoverySourceState] = None,
) -> DiscoveryPageSnapshot:
    composition = controller.compose(source)

    return DiscoveryPageSnapshot(
        state=controller.state,
        composition=composition,
        captured_at=_discovery_now(),
        metadata={
            "snapshot_type": "DISCOVERY_PRESENTATION",
            "presentation_only": True,
            "opportunity_generation": False,
            "scanner_generation": False,
            "intelligence_generation": False,
            "decision_generation": False,
            "d13_modification": False,
            "risk_override": False,
            "cas_bypass": False,
            "execution": False,
            "upstream_mutation": False,
        },
    )
# ============================================================
# ROBOMLM_PLUS — DISCOVERY PAGE
# PART 4 — SERIALIZATION / VALIDATION / HEALTH
# ============================================================


def _serialize_discovery_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, list):
        return [
            _serialize_discovery_value(item)
            for item in value
        ]

    if isinstance(value, tuple):
        return [
            _serialize_discovery_value(item)
            for item in value
        ]

    if isinstance(value, dict):
        return {
            str(key): _serialize_discovery_value(item)
            for key, item in value.items()
        }

    if hasattr(value, "__dataclass_fields__"):
        return {
            key: _serialize_discovery_value(
                getattr(value, key)
            )
            for key in value.__dataclass_fields__
        }

    return value


def serialize_discovery_identity(
    value: DiscoveryIdentityView,
) -> Dict[str, Any]:
    return _serialize_discovery_value(value)


def serialize_discovery_market(
    value: DiscoveryMarketView,
) -> Dict[str, Any]:
    return _serialize_discovery_value(value)


def serialize_discovery_instrument(
    value: DiscoveryInstrumentView,
) -> Dict[str, Any]:
    return _serialize_discovery_value(value)


def serialize_opportunity(
    value: OpportunityView,
) -> Dict[str, Any]:
    return _serialize_discovery_value(value)


def serialize_discovery_watchlist(
    value: DiscoveryWatchlistView,
) -> Dict[str, Any]:
    return _serialize_discovery_value(value)


def serialize_discovery_favorite(
    value: DiscoveryFavoriteView,
) -> Dict[str, Any]:
    return _serialize_discovery_value(value)


def serialize_discovery_badge(
    value: DiscoveryBadge,
) -> Dict[str, Any]:
    return _serialize_discovery_value(value)


def serialize_discovery_action(
    value: DiscoveryAction,
) -> Dict[str, Any]:
    return _serialize_discovery_value(value)


def serialize_discovery_summary(
    value: DiscoverySummaryView,
) -> Dict[str, Any]:
    return _serialize_discovery_value(value)


def serialize_discovery_page(
    value: DiscoveryPageView,
) -> Dict[str, Any]:
    return _serialize_discovery_value(value)


def serialize_discovery_source(
    value: DiscoverySourceState,
) -> Dict[str, Any]:
    return _serialize_discovery_value(value)


def serialize_discovery_composition(
    value: DiscoveryPageComposition,
) -> Dict[str, Any]:
    return _serialize_discovery_value(value)


def serialize_discovery_state(
    value: DiscoveryPageState,
) -> Dict[str, Any]:
    return _serialize_discovery_value(value)


def serialize_discovery_interaction_result(
    value: DiscoveryInteractionResult,
) -> Dict[str, Any]:
    return _serialize_discovery_value(value)


def serialize_discovery_snapshot(
    value: DiscoveryPageSnapshot,
) -> Dict[str, Any]:
    return _serialize_discovery_value(value)


def validate_discovery_identity(
    identity: DiscoveryIdentityView,
) -> List[str]:
    errors = []

    if identity.authenticated and not identity.user_id:
        errors.append(
            "Authenticated Discovery identity requires user_id."
        )

    if identity.email and "@" not in identity.email:
        errors.append(
            "Discovery identity email format is invalid."
        )

    return errors


def validate_discovery_market(
    market: DiscoveryMarketView,
) -> List[str]:
    errors = []

    if not market.market_id:
        errors.append("Market requires market_id.")

    if not market.market_name:
        errors.append("Market requires market_name.")

    return errors


def validate_discovery_instrument(
    instrument: DiscoveryInstrumentView,
) -> List[str]:
    errors = []

    if not instrument.instrument_id:
        errors.append(
            "Instrument requires instrument_id."
        )

    if not instrument.symbol:
        errors.append(
            "Instrument requires symbol."
        )

    return errors


def validate_opportunity(
    opportunity: OpportunityView,
) -> List[str]:
    errors = []

    if not opportunity.opportunity_id:
        errors.append(
            "Opportunity requires opportunity_id."
        )

    if not opportunity.symbol:
        errors.append(
            "Opportunity requires symbol."
        )

    if opportunity.confidence < 0.0:
        errors.append(
            "Opportunity confidence cannot be below zero."
        )

    if opportunity.confidence > 1.0:
        errors.append(
            "Opportunity confidence cannot exceed one."
        )

    if opportunity.state == OpportunityState.UNKNOWN:
        errors.append(
            "Opportunity state cannot remain UNKNOWN "
            "for a valid upstream opportunity."
        )

    return errors


def validate_discovery_watchlist(
    watchlist: DiscoveryWatchlistView,
) -> List[str]:
    errors = []

    if not watchlist.watchlist_id:
        errors.append(
            "Watchlist requires watchlist_id."
        )

    if not watchlist.name:
        errors.append(
            "Watchlist requires name."
        )

    return errors


def validate_discovery_favorite(
    favorite: DiscoveryFavoriteView,
) -> List[str]:
    errors = []

    if not favorite.favorite_id:
        errors.append(
            "Favorite requires favorite_id."
        )

    if not favorite.symbol:
        errors.append(
            "Favorite requires symbol."
        )

    return errors


def validate_discovery_badge(
    badge: DiscoveryBadge,
) -> List[str]:
    errors = []

    if badge.visible and not badge.label:
        errors.append(
            "Visible Discovery badge requires label."
        )

    return errors


def validate_discovery_action(
    action: DiscoveryAction,
) -> List[str]:
    errors = []

    if action.visible and not action.label:
        errors.append(
            "Visible Discovery action requires label."
        )

    if action.enabled and not action.route:
        errors.append(
            "Enabled Discovery action requires route."
        )

    if action.route and not action.route.startswith(
        "/discovery"
    ):
        errors.append(
            "Discovery action route must remain in "
            "Discovery presentation scope."
        )

    return errors


def validate_discovery_summary(
    summary: DiscoverySummaryView,
) -> List[str]:
    errors = []

    counters = {
        "total_opportunities": summary.total_opportunities,
        "visible_opportunities": summary.visible_opportunities,
        "qualified_opportunities":
            summary.qualified_opportunities,
        "developing_opportunities":
            summary.developing_opportunities,
        "watch_opportunities":
            summary.watch_opportunities,
        "invalidated_opportunities":
            summary.invalidated_opportunities,
        "favorite_count": summary.favorite_count,
        "selected_market_count":
            summary.selected_market_count,
        "selected_instrument_count":
            summary.selected_instrument_count,
    }

    for name, value in counters.items():
        if value < 0:
            errors.append(
                f"{name} cannot be negative."
            )

    if (
        summary.visible_opportunities
        > summary.total_opportunities
    ):
        errors.append(
            "Visible opportunities cannot exceed total opportunities."
        )

    return errors


def validate_discovery_page(
    page: DiscoveryPageView,
) -> List[str]:
    errors = []

    if page.page_name != DISCOVERY_PAGE_NAME:
        errors.append(
            "Discovery page name mismatch."
        )

    if page.route != DISCOVERY_ROUTE:
        errors.append(
            "Discovery page route mismatch."
        )

    errors.extend(
        validate_discovery_identity(page.identity)
    )

    for item in page.markets:
        errors.extend(
            validate_discovery_market(item)
        )

    for item in page.instruments:
        errors.extend(
            validate_discovery_instrument(item)
        )

    for item in page.opportunities:
        errors.extend(
            validate_opportunity(item)
        )

    for item in page.watchlists:
        errors.extend(
            validate_discovery_watchlist(item)
        )

    for item in page.favorites:
        errors.extend(
            validate_discovery_favorite(item)
        )

    for item in page.badges:
        errors.extend(
            validate_discovery_badge(item)
        )

    for item in page.actions:
        errors.extend(
            validate_discovery_action(item)
        )

    errors.extend(
        validate_discovery_summary(page.summary)
    )

    if not page.authenticated:
        if page.status != DiscoveryPageStatus.LOCKED:
            errors.append(
                "Unauthenticated Discovery page must be LOCKED."
            )

    protected_flags = (
        "opportunity_generation",
        "scanner_generation",
        "intelligence_generation",
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
                f"Discovery UI cannot enable protected flag: {flag}."
            )

    return errors


def validate_discovery_source(
    source: DiscoverySourceState,
) -> List[str]:
    errors = []

    if not isinstance(
        source,
        DiscoverySourceState,
    ):
        return ["Invalid Discovery source state."]

    errors.extend(
        validate_discovery_identity(source.identity)
    )

    market_ids = set()

    for market in source.markets:
        errors.extend(
            validate_discovery_market(market)
        )

        if market.market_id in market_ids:
            errors.append(
                f"Duplicate market_id: {market.market_id}"
            )

        market_ids.add(market.market_id)

    instrument_ids = set()

    for instrument in source.instruments:
        errors.extend(
            validate_discovery_instrument(instrument)
        )

        if instrument.instrument_id in instrument_ids:
            errors.append(
                "Duplicate instrument_id: "
                f"{instrument.instrument_id}"
            )

        instrument_ids.add(instrument.instrument_id)

    opportunity_ids = set()

    for opportunity in source.opportunities:
        errors.extend(
            validate_opportunity(opportunity)
        )

        if opportunity.opportunity_id in opportunity_ids:
            errors.append(
                "Duplicate opportunity_id: "
                f"{opportunity.opportunity_id}"
            )

        opportunity_ids.add(opportunity.opportunity_id)

    for watchlist in source.watchlists:
        errors.extend(
            validate_discovery_watchlist(watchlist)
        )

    for favorite in source.favorites:
        errors.extend(
            validate_discovery_favorite(favorite)
        )

    if not source.source_available and not source.source_errors:
        errors.append(
            "Unavailable Discovery source requires source_errors."
        )

    return errors


def validate_discovery_composition(
    composition: DiscoveryPageComposition,
) -> List[str]:
    errors = []

    errors.extend(
        validate_discovery_page(composition.page)
    )

    errors.extend(
        validate_discovery_summary(
            composition.summary
        )
    )

    protected_flags = (
        "opportunity_generation",
        "scanner_generation",
        "intelligence_generation",
        "decision_generation",
        "d13_modification",
        "risk_override",
        "cas_bypass",
        "execution",
        "upstream_mutation",
    )

    for flag in protected_flags:
        if composition.metadata.get(flag) is True:
            errors.append(
                f"Protected Discovery composition flag enabled: {flag}"
            )

    return errors


def validate_discovery_state(
    state: DiscoveryPageState,
) -> List[str]:
    errors = []

    if state.interaction_count < 0:
        errors.append(
            "Discovery interaction_count cannot be negative."
        )

    if state.refresh_count < 0:
        errors.append(
            "Discovery refresh_count cannot be negative."
        )

    if not state.authenticated:
        if not state.locked:
            errors.append(
                "Unauthenticated Discovery state must be locked."
            )

        if state.ready:
            errors.append(
                "Unauthenticated Discovery state cannot be ready."
            )

        if state.status != DiscoveryPageStatus.LOCKED:
            errors.append(
                "Unauthenticated Discovery state must be LOCKED."
            )

    if state.ready and state.locked:
        errors.append(
            "Discovery state cannot be ready while locked."
        )

    if state.current_route not in DISCOVERY_ROUTE_MODES:
        errors.append(
            "Discovery current_route is not registered."
        )

    return errors


def validate_discovery_authority(
    metadata: Optional[Dict[str, Any]] = None,
) -> List[str]:
    errors = []

    for authority, allowed in DISCOVERY_UI_AUTHORITY.items():
        if authority in {
            "discovery_presentation",
            "opportunity_presentation",
            "scanner_presentation",
            "market_selection",
            "instrument_selection",
            "contract_selection",
            "watchlist_presentation",
            "favorites_presentation",
            "discovery_navigation",
            "filter_presentation",
            "sorting_presentation",
            "display_configuration",
        }:
            if allowed is not True:
                errors.append(
                    f"Required Discovery UI authority disabled: {authority}"
                )
        else:
            if allowed is not False:
                errors.append(
                    f"Forbidden Discovery authority enabled: {authority}"
                )

    if metadata:
        forbidden = [
            key for key, value in metadata.items()
            if key.endswith("_generation")
            or key.endswith("_mutation")
            or key in {
                "d13_modification",
                "risk_override",
                "cas_bypass",
                "execution",
                "upstream_mutation",
            }
            if value is True
        ]

        for key in forbidden:
            errors.append(
                f"Discovery metadata violates presentation boundary: {key}"
            )

    return errors


@dataclass
class DiscoveryPageHealth:
    engine: str
    version: str
    initialized: bool
    ready: bool
    locked: bool
    status: DiscoveryPageStatus
    opportunity_count: int
    market_count: int
    instrument_count: int
    validation_errors: List[str]
    authority_valid: bool
    operational: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


def build_discovery_page_health(
    controller: DiscoveryPageController,
) -> DiscoveryPageHealth:
    state_errors = validate_discovery_state(
        controller.state
    )

    composition = controller.last_composition

    composition_errors = []

    if composition is not None:
        composition_errors = validate_discovery_composition(
            composition
        )

    authority_errors = validate_discovery_authority(
        composition.page.metadata
        if composition is not None
        else None
    )

    errors = (
        state_errors
        + composition_errors
        + authority_errors
    )

    opportunity_count = 0
    market_count = 0
    instrument_count = 0

    if composition is not None:
        opportunity_count = len(
            composition.opportunities
        )
        market_count = len(
            composition.markets
        )
        instrument_count = len(
            composition.instruments
        )

    authority_valid = not bool(
        authority_errors
    )

    operational = (
        controller.state.initialized
        and controller.state.ready
        and not controller.state.locked
        and controller.state.status
        == DiscoveryPageStatus.READY
        and not errors
        and authority_valid
    )

    return DiscoveryPageHealth(
        engine=DISCOVERY_PAGE_ENGINE,
        version=DISCOVERY_PAGE_VERSION,
        initialized=controller.state.initialized,
        ready=controller.state.ready,
        locked=controller.state.locked,
        status=controller.state.status,
        opportunity_count=opportunity_count,
        market_count=market_count,
        instrument_count=instrument_count,
        validation_errors=errors,
        authority_valid=authority_valid,
        operational=operational,
        metadata={
            "ui_only": True,
            "presentation_only": True,
            "opportunity_generation": False,
            "scanner_generation": False,
            "intelligence_generation": False,
            "decision_generation": False,
            "d13_modification": False,
            "risk_override": False,
            "cas_bypass": False,
            "execution": False,
            "upstream_mutation": False,
        },
    )


def serialize_discovery_health(
    health: DiscoveryPageHealth,
) -> Dict[str, Any]:
    return _serialize_discovery_value(health)


def discovery_page_operational_check(
    controller: Optional[DiscoveryPageController] = None,
) -> Dict[str, Any]:
    controller = controller or DiscoveryPageController()

    health = build_discovery_page_health(
        controller
    )

    return {
        "engine": DISCOVERY_PAGE_ENGINE,
        "version": DISCOVERY_PAGE_VERSION,
        "operational": health.operational,
        "initialized": health.initialized,
        "ready": health.ready,
        "locked": health.locked,
        "status": health.status.value,
        "validation_errors": list(
            health.validation_errors
        ),
        "authority_valid": health.authority_valid,
        "opportunity_generation": False,
        "scanner_generation": False,
        "intelligence_generation": False,
        "decision_generation": False,
        "d13_modification": False,
        "risk_override": False,
        "cas_bypass": False,
        "execution": False,
        "order_mutation": False,
        "position_mutation": False,
        "upstream_mutation": False,
    }
# ============================================================
# ROBOMLM_PLUS — DISCOVERY PAGE
# PART 5 — DIAGNOSTICS / CONTRACT / MODULE CHECK / FACTORY
# ============================================================


def diagnose_discovery_page(
    controller: DiscoveryPageController,
    composition: Optional[DiscoveryPageComposition] = None,
) -> Dict[str, Any]:
    if composition is None:
        composition = controller.last_composition

    state_errors = validate_discovery_state(
        controller.state
    )

    composition_errors = []

    if composition is not None:
        composition_errors = validate_discovery_composition(
            composition
        )

    authority_errors = validate_discovery_authority(
        composition.page.metadata
        if composition is not None
        else None
    )

    health = build_discovery_page_health(
        controller
    )

    return {
        "engine": DISCOVERY_PAGE_ENGINE,
        "version": DISCOVERY_PAGE_VERSION,
        "page": DISCOVERY_PAGE_NAME,
        "route": DISCOVERY_ROUTE,
        "state": serialize_discovery_state(
            controller.state
        ),
        "health": serialize_discovery_health(
            health
        ),
        "state_errors": state_errors,
        "composition_errors": composition_errors,
        "authority_errors": authority_errors,
        "authority_valid": not bool(
            authority_errors
        ),
        "presentation_only": True,
        "opportunity_generation": False,
        "scanner_generation": False,
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
        "upstream_mutation": False,
    }


def discovery_page_summary() -> Dict[str, Any]:
    return {
        "engine": DISCOVERY_PAGE_ENGINE,
        "version": DISCOVERY_PAGE_VERSION,
        "name": DISCOVERY_PAGE_NAME,
        "title": DISCOVERY_PAGE_TITLE,
        "route": DISCOVERY_ROUTE,
        "layer": "UI_PRESENTATION",
        "role": "ROBOMLM_OPPORTUNITY_DISCOVERY",
        "responsibilities": [
            "DISCOVERY_PRESENTATION",
            "OPPORTUNITY_PRESENTATION",
            "SCANNER_RESULT_PRESENTATION",
            "MARKET_SELECTION",
            "INSTRUMENT_SELECTION",
            "CONTRACT_SELECTION",
            "WATCHLIST_PRESENTATION",
            "FAVORITES_PRESENTATION",
            "DISCOVERY_NAVIGATION",
            "FILTER_PRESENTATION",
            "SORTING_PRESENTATION",
        ],
        "principles": [
            "PRESENTATION_ONLY",
            "UPSTREAM_OPPORTUNITY_TRUTH_PRESERVED",
            "NO_FAKE_OPPORTUNITY_SCORE",
            "NO_SCANNER_ALGORITHM",
            "NO_INTELLIGENCE_GENERATION",
            "NO_DECISION_GENERATION",
            "NO_D13_MUTATION",
            "NO_RISK_OVERRIDE",
            "NO_CAS_BYPASS",
            "NO_EXECUTION",
            "NO_ORDER_MUTATION",
            "NO_POSITION_MUTATION",
            "NO_UPSTREAM_MUTATION",
        ],
        "authority": dict(
            DISCOVERY_UI_AUTHORITY
        ),
    }


def discovery_page_contract_manifest() -> Dict[str, Any]:
    return {
        "module": DISCOVERY_PAGE_ENGINE,
        "version": DISCOVERY_PAGE_VERSION,
        "layer": "UI_PRESENTATION",
        "role": "ROBOMLM_OPPORTUNITY_DISCOVERY",
        "input_flow": [
            "USER_SERVICE_OUTPUT",
            "MARKET_SELECTION_OUTPUT",
            "INSTRUMENT_SELECTION_OUTPUT",
            "CONTRACT_SELECTION_OUTPUT",
            "OPPORTUNITY_ENGINE_OUTPUT",
            "SCANNER_OUTPUT",
            "WATCHLIST_SERVICE_OUTPUT",
            "FAVORITES_SERVICE_OUTPUT",
            "APPLICATION_SESSION_STATE",
        ],
        "processing": [
            "SOURCE_NORMALIZATION",
            "PRESENTATION_READINESS",
            "MODE_FILTERING",
            "OPPORTUNITY_STATE_FILTERING",
            "MARKET_FILTERING",
            "INSTRUMENT_FILTERING",
            "SUMMARY_PRESENTATION",
            "BADGE_COMPOSITION",
            "ACTION_COMPOSITION",
            "VIEW_COMPOSITION",
            "SNAPSHOT",
            "VALIDATION",
            "DIAGNOSTICS",
        ],
        "outputs": [
            "DISCOVERY_PAGE_VIEW",
            "DISCOVERY_PAGE_COMPOSITION",
            "DISCOVERY_PAGE_SNAPSHOT",
            "DISCOVERY_PAGE_HEALTH",
            "DISCOVERY_PAGE_DIAGNOSTICS",
        ],
        "authority_owners": {
            "market_data": "MARKET_DATA_LAYER",
            "evidence": "EVIDENCE_CORTEX",
            "intelligence": "INTELLIGENCE_LAYER",
            "opportunity": "OPPORTUNITY_ENGINE",
            "scanner": "DISCOVERY_SCANNER_LAYER",
            "decision": "DECISION_CORTEX",
            "d13": "D13_DECISION_AUTHORITY",
            "risk": "RISK_LAYER",
            "cas": "CAS",
            "execution": "EXECUTION_LAYER",
            "orders": "ORDER_EXECUTION_LAYER",
            "positions": "POSITION_LAYER",
            "watchlists": "WATCHLIST_SERVICE",
            "favorites": "FAVORITES_SERVICE",
        },
        "forbidden_authority": [
            "MARKET_DATA_GENERATION",
            "EVIDENCE_GENERATION",
            "INTELLIGENCE_GENERATION",
            "OPPORTUNITY_GENERATION",
            "SCANNER_ALGORITHM",
            "DECISION_GENERATION",
            "D13_MODIFICATION",
            "RISK_GENERATION",
            "RISK_OVERRIDE",
            "CAS_GENERATION",
            "CAS_BYPASS",
            "EXECUTION",
            "ORDER_AUTHORITY",
            "ORDER_MUTATION",
            "POSITION_AUTHORITY",
            "POSITION_MUTATION",
            "PORTFOLIO_MUTATION",
            "UPSTREAM_MUTATION",
        ],
    }


def validate_discovery_page_module() -> Dict[str, Any]:
    controller = DiscoveryPageController()

    source = DiscoverySourceState(
        identity=normalize_discovery_identity(),
        markets=[],
        instruments=[],
        opportunities=[],
        watchlists=[],
        favorites=[],
        source_available=False,
        source_errors=[
            "Discovery source is not connected."
        ],
        metadata={
            "module_check": True,
            "presentation_only": True,
        },
    )

    composition = controller.initialize(
        source
    )

    state_errors = validate_discovery_state(
        controller.state
    )

    source_errors = validate_discovery_source(
        source
    )

    composition_errors = validate_discovery_composition(
        composition
    )

    authority_errors = validate_discovery_authority(
        composition.page.metadata
    )

    return {
        "module": DISCOVERY_PAGE_ENGINE,
        "version": DISCOVERY_PAGE_VERSION,
        "valid": not any([
            state_errors,
            source_errors,
            composition_errors,
            authority_errors,
        ]),
        "state_errors": state_errors,
        "source_errors": source_errors,
        "composition_errors": composition_errors,
        "authority_errors": authority_errors,
        "contract": discovery_page_contract_manifest(),
        "summary": discovery_page_summary(),
    }


def default_discovery_snapshot() -> DiscoveryPageSnapshot:
    controller = DiscoveryPageController()

    source = DiscoverySourceState(
        identity=normalize_discovery_identity(),
        markets=[],
        instruments=[],
        opportunities=[],
        watchlists=[],
        favorites=[],
        source_available=False,
        source_errors=[
            "Discovery source is not connected."
        ],
        metadata={
            "default_snapshot": True,
            "presentation_only": True,
        },
    )

    controller.initialize(source)

    return build_discovery_page_snapshot(
        controller,
        source,
    )


def create_default_discovery_page() -> DiscoveryPageController:
    controller = DiscoveryPageController()

    source = DiscoverySourceState(
        identity=normalize_discovery_identity(),
        markets=[],
        instruments=[],
        opportunities=[],
        watchlists=[],
        favorites=[],
        source_available=False,
        source_errors=[
            "Discovery source is not connected."
        ],
        metadata={
            "factory": "DEFAULT_DISCOVERY_PAGE",
            "presentation_only": True,
        },
    )

    controller.initialize(source)

    return controller


def discovery_page_self_check() -> Dict[str, Any]:
    module_check = validate_discovery_page_module()

    controller = create_default_discovery_page()

    operational = discovery_page_operational_check(
        controller
    )

    diagnostics = diagnose_discovery_page(
        controller
    )

    return {
        "module_valid": module_check["valid"],
        "operational": operational["operational"],
        "authority_valid": diagnostics[
            "authority_valid"
        ],
        "module_check": module_check,
        "operational_check": operational,
        "diagnostics": diagnostics,
        "passed": (
            module_check["valid"]
            and diagnostics["authority_valid"]
        ),
    }


__all__ = [
    "DISCOVERY_PAGE_ENGINE",
    "DISCOVERY_PAGE_VERSION",
    "DISCOVERY_PAGE_NAME",
    "DISCOVERY_PAGE_TITLE",
    "DISCOVERY_PAGE_DESCRIPTION",
    "DISCOVERY_ROUTE",
    "DISCOVERY_UI_AUTHORITY",

    "DiscoveryPageStatus",
    "DiscoveryMode",
    "DiscoveryAssetClass",
    "OpportunityState",
    "OpportunityBias",
    "OpportunityStrength",
    "DiscoveryPriority",
    "DiscoveryBadgeType",

    "DiscoveryIdentityView",
    "DiscoveryMarketView",
    "DiscoveryInstrumentView",
    "OpportunityView",
    "DiscoveryWatchlistView",
    "DiscoveryFavoriteView",
    "DiscoveryBadge",
    "DiscoverySummaryView",
    "DiscoverySourceState",

    "DiscoveryAction",
    "DiscoveryPageView",
    "DiscoveryPageComposition",

    "DiscoveryInteraction",
    "DiscoveryInteractionResult",
    "DiscoveryPageState",
    "DiscoveryPageSnapshot",
    "DiscoveryPageController",
    "DiscoveryPageHealth",

    "DEFAULT_DISCOVERY_MODES",
    "DEFAULT_DISCOVERY_ACTIONS",
    "DISCOVERY_MODE_ASSET_CLASS",
    "DISCOVERY_INTERACTION_ROUTES",
    "DISCOVERY_ROUTE_MODES",

    "normalize_discovery_identity",
    "normalize_discovery_market",
    "normalize_discovery_instrument",
    "normalize_opportunity",
    "normalize_discovery_watchlist",
    "normalize_discovery_favorite",
    "normalize_discovery_source_state",

    "evaluate_discovery_status",
    "filter_discovery_markets",
    "filter_discovery_instruments",
    "filter_discovery_opportunities",
    "filter_discovery_favorites",

    "build_discovery_summary",
    "build_discovery_badges",
    "build_discovery_actions",
    "build_discovery_status_message",
    "build_discovery_mode_message",
    "resolve_discovery_display_name",

    "compose_discovery_page",

    "normalize_discovery_interaction",
    "route_to_discovery_mode",
    "evaluate_discovery_route_access",
    "resolve_discovery_interaction",

    "create_discovery_page_state",
    "build_discovery_page_snapshot",

    "_serialize_discovery_value",
    "serialize_discovery_identity",
    "serialize_discovery_market",
    "serialize_discovery_instrument",
    "serialize_opportunity",
    "serialize_discovery_watchlist",
    "serialize_discovery_favorite",
    "serialize_discovery_badge",
    "serialize_discovery_action",
    "serialize_discovery_summary",
    "serialize_discovery_page",
    "serialize_discovery_source",
    "serialize_discovery_composition",
    "serialize_discovery_state",
    "serialize_discovery_interaction_result",
    "serialize_discovery_snapshot",
    "serialize_discovery_health",

    "validate_discovery_identity",
    "validate_discovery_market",
    "validate_discovery_instrument",
    "validate_opportunity",
    "validate_discovery_watchlist",
    "validate_discovery_favorite",
    "validate_discovery_badge",
    "validate_discovery_action",
    "validate_discovery_summary",
    "validate_discovery_page",
    "validate_discovery_source",
    "validate_discovery_composition",
    "validate_discovery_state",
    "validate_discovery_authority",

    "build_discovery_page_health",
    "discovery_page_operational_check",
    "diagnose_discovery_page",

    "discovery_page_summary",
    "discovery_page_contract_manifest",
    "validate_discovery_page_module",
    "default_discovery_snapshot",
    "create_default_discovery_page",
    "discovery_page_self_check",
]
