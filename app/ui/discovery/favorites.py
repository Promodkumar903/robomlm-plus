# ============================================================
# ROBOMLM_PLUS — DISCOVERY FAVORITES
# PART 1 — CORE CONTRACT / AUTHORITY / SCHEMAS
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


FAVORITES_ENGINE = "ROBOMLM_PLUS_DISCOVERY_FAVORITES"
FAVORITES_VERSION = "1.0"
FAVORITES_NAME = "Discovery Favorites"
FAVORITES_TITLE = "ROBOMLM Opportunity Favorites"
FAVORITES_DESCRIPTION = (
    "Presentation and management surface for user-selected "
    "market instruments and upstream opportunities."
)


# ============================================================
# AUTHORITY BOUNDARY
# ============================================================

FAVORITES_AUTHORITY = {
    "favorite_presentation": True,
    "favorite_selection": True,
    "favorite_filtering": True,
    "favorite_grouping": True,
    "watchlist_linking": True,
    "opportunity_presentation": True,
    "upstream_opportunity_consumption": True,

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

    "opportunity_generation": False,
    "scanner_intelligence_generation": False,
    "upstream_mutation": False,
}


# ============================================================
# ENUMS
# ============================================================

class FavoritesStatus(str, Enum):
    IDLE = "IDLE"
    LOADING = "LOADING"
    READY = "READY"
    DEGRADED = "DEGRADED"
    BLOCKED = "BLOCKED"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class FavoriteAssetClass(str, Enum):
    STOCK = "STOCK"
    INDEX = "INDEX"
    COMMODITY = "COMMODITY"
    CRYPTO = "CRYPTO"
    FX = "FX"
    EQUITY = "EQUITY"
    UNKNOWN = "UNKNOWN"


class FavoriteItemType(str, Enum):
    INSTRUMENT = "INSTRUMENT"
    OPPORTUNITY = "OPPORTUNITY"
    MARKET = "MARKET"
    WATCHLIST = "WATCHLIST"
    UNKNOWN = "UNKNOWN"


class FavoritePriority(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class FavoriteState(str, Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    INVALIDATED = "INVALIDATED"
    EXPIRED = "EXPIRED"
    REMOVED = "REMOVED"
    UNKNOWN = "UNKNOWN"


class FavoriteBias(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"


# ============================================================
# HELPERS
# ============================================================

def _favorite_text(
    value: Any,
    default: str = "",
) -> str:
    if value is None:
        return default

    text = str(value).strip()

    return text if text else default


def _favorite_bool(
    value: Any,
    default: bool = False,
) -> bool:

    if value is None:
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.strip().lower() in {
            "1",
            "true",
            "yes",
            "y",
            "on",
            "enabled",
        }

    return bool(value)


def _favorite_float(
    value: Any,
    default: float = 0.0,
) -> float:

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _favorite_enum(
    value: Any,
    enum_type: Any,
    default: Any,
) -> Any:

    if isinstance(value, enum_type):
        return value

    try:
        return enum_type(value)
    except (TypeError, ValueError):
        return default


def _favorite_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ============================================================
# CORE SCHEMAS
# ============================================================

@dataclass
class FavoriteIdentity:
    user_id: str
    display_name: str = ""
    authenticated: bool = False
    plus_enabled: bool = False
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class FavoriteInstrument:
    instrument_id: str
    symbol: str
    display_name: str = ""

    asset_class: FavoriteAssetClass = (
        FavoriteAssetClass.UNKNOWN
    )

    market_id: str = ""
    market_name: str = ""
    exchange: str = ""
    country: str = ""
    currency: str = ""

    sector: str = ""
    industry: str = ""

    favorite: bool = True
    state: FavoriteState = FavoriteState.ACTIVE
    priority: FavoritePriority = (
        FavoritePriority.NORMAL
    )

    note: str = ""
    created_at: str = ""
    updated_at: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class FavoriteOpportunity:
    opportunity_id: str
    instrument_id: str
    symbol: str

    instrument_name: str = ""

    asset_class: FavoriteAssetClass = (
        FavoriteAssetClass.UNKNOWN
    )

    market_id: str = ""
    exchange: str = ""
    country: str = ""
    currency: str = ""

    state: FavoriteState = FavoriteState.UNKNOWN
    bias: FavoriteBias = FavoriteBias.UNKNOWN

    strength: str = ""
    summary: str = ""

    confidence: float = 0.0

    favorite: bool = True
    priority: FavoritePriority = (
        FavoritePriority.NORMAL
    )

    timestamp: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class FavoriteMarket:
    market_id: str
    market_name: str

    asset_class: FavoriteAssetClass = (
        FavoriteAssetClass.UNKNOWN
    )

    country: str = ""
    region: str = ""
    exchange: str = ""
    currency: str = ""
    timezone: str = ""

    favorite: bool = True
    state: FavoriteState = FavoriteState.ACTIVE

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class FavoriteRecord:
    favorite_id: str
    item_id: str
    item_type: FavoriteItemType

    symbol: str = ""
    display_name: str = ""

    asset_class: FavoriteAssetClass = (
        FavoriteAssetClass.UNKNOWN
    )

    state: FavoriteState = FavoriteState.ACTIVE
    priority: FavoritePriority = (
        FavoritePriority.NORMAL
    )

    note: str = ""

    created_at: str = ""
    updated_at: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class FavoritesFilter:
    asset_classes: List[FavoriteAssetClass] = (
        field(default_factory=list)
    )

    item_types: List[FavoriteItemType] = (
        field(default_factory=list)
    )

    states: List[FavoriteState] = (
        field(default_factory=list)
    )

    priorities: List[FavoritePriority] = (
        field(default_factory=list)
    )

    market_ids: List[str] = field(
        default_factory=list
    )

    exchanges: List[str] = field(
        default_factory=list
    )

    symbols: List[str] = field(
        default_factory=list
    )

    sectors: List[str] = field(
        default_factory=list
    )

    industries: List[str] = field(
        default_factory=list
    )

    include_invalidated: bool = False
    include_expired: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class FavoritesSourceState:
    identity: FavoriteIdentity

    instruments: List[FavoriteInstrument] = (
        field(default_factory=list)
    )

    opportunities: List[FavoriteOpportunity] = (
        field(default_factory=list)
    )

    markets: List[FavoriteMarket] = (
        field(default_factory=list)
    )

    records: List[FavoriteRecord] = (
        field(default_factory=list)
    )

    source_available: bool = False

    source_errors: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class FavoritesSummary:
    total_favorites: int = 0
    active_favorites: int = 0

    instrument_count: int = 0
    opportunity_count: int = 0
    market_count: int = 0

    bullish_count: int = 0
    bearish_count: int = 0

    high_priority_count: int = 0
    critical_priority_count: int = 0

    authenticated: bool = False
    plus_enabled: bool = False

    status: FavoritesStatus = (
        FavoritesStatus.UNKNOWN
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class FavoritesRequest:
    filter: FavoritesFilter = field(
        default_factory=FavoritesFilter
    )

    source: Optional[FavoritesSourceState] = None

    authenticated: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class FavoritesResult:
    status: FavoritesStatus

    favorites: List[FavoriteRecord] = field(
        default_factory=list
    )

    instruments: List[FavoriteInstrument] = field(
        default_factory=list
    )

    opportunities: List[FavoriteOpportunity] = field(
        default_factory=list
    )

    markets: List[FavoriteMarket] = field(
        default_factory=list
    )

    summary: Optional[FavoritesSummary] = None

    source_available: bool = False

    source_errors: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    generated_at: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class FavoritesSnapshot:
    request: FavoritesRequest
    result: FavoritesResult
    captured_at: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )
# ============================================================
# ROBOMLM_PLUS — DISCOVERY FAVORITES
# PART 2 — NORMALIZATION / FILTERING / SOURCE PROCESSING
# ============================================================


def normalize_favorite_identity(
    value: Optional[FavoriteIdentity],
) -> FavoriteIdentity:

    if value is None:
        return FavoriteIdentity(
            user_id="",
            authenticated=False,
            plus_enabled=False,
        )

    return FavoriteIdentity(
        user_id=_favorite_text(value.user_id),
        display_name=_favorite_text(value.display_name),
        authenticated=_favorite_bool(
            value.authenticated
        ),
        plus_enabled=_favorite_bool(
            value.plus_enabled
        ),
        metadata=dict(value.metadata or {}),
    )


def normalize_favorite_instrument(
    value: FavoriteInstrument,
) -> FavoriteInstrument:

    return FavoriteInstrument(
        instrument_id=_favorite_text(
            value.instrument_id
        ),
        symbol=_favorite_text(value.symbol),
        display_name=_favorite_text(
            value.display_name
        ),
        asset_class=_favorite_enum(
            value.asset_class,
            FavoriteAssetClass,
            FavoriteAssetClass.UNKNOWN,
        ),
        market_id=_favorite_text(value.market_id),
        market_name=_favorite_text(
            value.market_name
        ),
        exchange=_favorite_text(value.exchange),
        country=_favorite_text(value.country),
        currency=_favorite_text(value.currency),
        sector=_favorite_text(value.sector),
        industry=_favorite_text(value.industry),
        favorite=_favorite_bool(
            value.favorite,
            True,
        ),
        state=_favorite_enum(
            value.state,
            FavoriteState,
            FavoriteState.UNKNOWN,
        ),
        priority=_favorite_enum(
            value.priority,
            FavoritePriority,
            FavoritePriority.NORMAL,
        ),
        note=_favorite_text(value.note),
        created_at=_favorite_text(
            value.created_at
        ),
        updated_at=_favorite_text(
            value.updated_at
        ),
        metadata=dict(value.metadata or {}),
    )


def normalize_favorite_opportunity(
    value: FavoriteOpportunity,
) -> FavoriteOpportunity:

    return FavoriteOpportunity(
        opportunity_id=_favorite_text(
            value.opportunity_id
        ),
        instrument_id=_favorite_text(
            value.instrument_id
        ),
        symbol=_favorite_text(value.symbol),
        instrument_name=_favorite_text(
            value.instrument_name
        ),
        asset_class=_favorite_enum(
            value.asset_class,
            FavoriteAssetClass,
            FavoriteAssetClass.UNKNOWN,
        ),
        market_id=_favorite_text(
            value.market_id
        ),
        exchange=_favorite_text(
            value.exchange
        ),
        country=_favorite_text(
            value.country
        ),
        currency=_favorite_text(
            value.currency
        ),
        state=_favorite_enum(
            value.state,
            FavoriteState,
            FavoriteState.UNKNOWN,
        ),
        bias=_favorite_enum(
            value.bias,
            FavoriteBias,
            FavoriteBias.UNKNOWN,
        ),
        strength=_favorite_text(
            value.strength
        ),
        summary=_favorite_text(
            value.summary
        ),
        confidence=_favorite_float(
            value.confidence
        ),
        favorite=_favorite_bool(
            value.favorite,
            True,
        ),
        priority=_favorite_enum(
            value.priority,
            FavoritePriority,
            FavoritePriority.NORMAL,
        ),
        timestamp=_favorite_text(
            value.timestamp
        ),
        metadata=dict(value.metadata or {}),
    )


def normalize_favorite_market(
    value: FavoriteMarket,
) -> FavoriteMarket:

    return FavoriteMarket(
        market_id=_favorite_text(
            value.market_id
        ),
        market_name=_favorite_text(
            value.market_name
        ),
        asset_class=_favorite_enum(
            value.asset_class,
            FavoriteAssetClass,
            FavoriteAssetClass.UNKNOWN,
        ),
        country=_favorite_text(value.country),
        region=_favorite_text(value.region),
        exchange=_favorite_text(value.exchange),
        currency=_favorite_text(value.currency),
        timezone=_favorite_text(value.timezone),
        favorite=_favorite_bool(
            value.favorite,
            True,
        ),
        state=_favorite_enum(
            value.state,
            FavoriteState,
            FavoriteState.UNKNOWN,
        ),
        metadata=dict(value.metadata or {}),
    )


def normalize_favorite_record(
    value: FavoriteRecord,
) -> FavoriteRecord:

    return FavoriteRecord(
        favorite_id=_favorite_text(
            value.favorite_id
        ),
        item_id=_favorite_text(
            value.item_id
        ),
        item_type=_favorite_enum(
            value.item_type,
            FavoriteItemType,
            FavoriteItemType.UNKNOWN,
        ),
        symbol=_favorite_text(value.symbol),
        display_name=_favorite_text(
            value.display_name
        ),
        asset_class=_favorite_enum(
            value.asset_class,
            FavoriteAssetClass,
            FavoriteAssetClass.UNKNOWN,
        ),
        state=_favorite_enum(
            value.state,
            FavoriteState,
            FavoriteState.UNKNOWN,
        ),
        priority=_favorite_enum(
            value.priority,
            FavoritePriority,
            FavoritePriority.NORMAL,
        ),
        note=_favorite_text(value.note),
        created_at=_favorite_text(
            value.created_at
        ),
        updated_at=_favorite_text(
            value.updated_at
        ),
        metadata=dict(value.metadata or {}),
    )


def _normalize_favorite_string_list(
    values: Optional[List[Any]],
) -> List[str]:

    if not values:
        return []

    output: List[str] = []

    for value in values:
        text = _favorite_text(value)

        if text and text not in output:
            output.append(text)

    return output


def _normalize_favorite_enum_list(
    values: Optional[List[Any]],
    enum_type: Any,
) -> List[Any]:

    if not values:
        return []

    output: List[Any] = []

    for value in values:
        item = _favorite_enum(
            value,
            enum_type,
            enum_type.UNKNOWN,
        )

        if item != enum_type.UNKNOWN and item not in output:
            output.append(item)

    return output


def normalize_favorites_filter(
    value: Optional[FavoritesFilter],
) -> FavoritesFilter:

    if value is None:
        return FavoritesFilter()

    return FavoritesFilter(
        asset_classes=_normalize_favorite_enum_list(
            value.asset_classes,
            FavoriteAssetClass,
        ),
        item_types=_normalize_favorite_enum_list(
            value.item_types,
            FavoriteItemType,
        ),
        states=_normalize_favorite_enum_list(
            value.states,
            FavoriteState,
        ),
        priorities=_normalize_favorite_enum_list(
            value.priorities,
            FavoritePriority,
        ),
        market_ids=_normalize_favorite_string_list(
            value.market_ids
        ),
        exchanges=_normalize_favorite_string_list(
            value.exchanges
        ),
        symbols=_normalize_favorite_string_list(
            value.symbols
        ),
        sectors=_normalize_favorite_string_list(
            value.sectors
        ),
        industries=_normalize_favorite_string_list(
            value.industries
        ),
        include_invalidated=_favorite_bool(
            value.include_invalidated
        ),
        include_expired=_favorite_bool(
            value.include_expired
        ),
        metadata=dict(value.metadata or {}),
    )


def normalize_favorites_source(
    value: Optional[FavoritesSourceState],
) -> FavoritesSourceState:

    if value is None:
        return FavoritesSourceState(
            identity=FavoriteIdentity(
                user_id="",
                authenticated=False,
            ),
            source_available=False,
        )

    return FavoritesSourceState(
        identity=normalize_favorite_identity(
            value.identity
        ),
        instruments=[
            normalize_favorite_instrument(item)
            for item in value.instruments
        ],
        opportunities=[
            normalize_favorite_opportunity(item)
            for item in value.opportunities
        ],
        markets=[
            normalize_favorite_market(item)
            for item in value.markets
        ],
        records=[
            normalize_favorite_record(item)
            for item in value.records
        ],
        source_available=_favorite_bool(
            value.source_available
        ),
        source_errors=[
            _favorite_text(error)
            for error in value.source_errors
            if _favorite_text(error)
        ],
        metadata=dict(value.metadata or {}),
    )


def normalize_favorites_request(
    value: Optional[FavoritesRequest],
) -> FavoritesRequest:

    if value is None:
        return FavoritesRequest(
            authenticated=False
        )

    source = normalize_favorites_source(
        value.source
    )

    authenticated = _favorite_bool(
        value.authenticated
    )

    return FavoritesRequest(
        filter=normalize_favorites_filter(
            value.filter
        ),
        source=source,
        authenticated=authenticated,
        metadata=dict(value.metadata or {}),
    )


# ============================================================
# FILTER HELPERS
# ============================================================

def _favorite_matches_list(
    value: str,
    allowed: List[str],
) -> bool:

    if not allowed:
        return True

    normalized = value.strip().lower()

    return any(
        normalized == item.strip().lower()
        for item in allowed
    )


def _favorite_matches_enum(
    value: Any,
    allowed: List[Any],
) -> bool:

    if not allowed:
        return True

    return value in allowed


def favorite_instrument_matches_filter(
    value: FavoriteInstrument,
    filter_value: FavoritesFilter,
) -> bool:

    if not value.favorite:
        return False

    if (
        filter_value.asset_classes
        and value.asset_class
        not in filter_value.asset_classes
    ):
        return False

    if (
        filter_value.states
        and value.state
        not in filter_value.states
    ):
        return False

    if (
        filter_value.priorities
        and value.priority
        not in filter_value.priorities
    ):
        return False

    if not _favorite_matches_list(
        value.market_id,
        filter_value.market_ids,
    ):
        return False

    if not _favorite_matches_list(
        value.exchange,
        filter_value.exchanges,
    ):
        return False

    if not _favorite_matches_list(
        value.symbol,
        filter_value.symbols,
    ):
        return False

    if not _favorite_matches_list(
        value.sector,
        filter_value.sectors,
    ):
        return False

    if not _favorite_matches_list(
        value.industry,
        filter_value.industries,
    ):
        return False

    if (
        value.state == FavoriteState.INVALIDATED
        and not filter_value.include_invalidated
    ):
        return False

    if (
        value.state == FavoriteState.EXPIRED
        and not filter_value.include_expired
    ):
        return False

    return True


def favorite_opportunity_matches_filter(
    value: FavoriteOpportunity,
    filter_value: FavoritesFilter,
) -> bool:

    if not value.favorite:
        return False

    if (
        filter_value.asset_classes
        and value.asset_class
        not in filter_value.asset_classes
    ):
        return False

    if (
        filter_value.states
        and value.state
        not in filter_value.states
    ):
        return False

    if (
        filter_value.priorities
        and value.priority
        not in filter_value.priorities
    ):
        return False

    if not _favorite_matches_list(
        value.market_id,
        filter_value.market_ids,
    ):
        return False

    if not _favorite_matches_list(
        value.exchange,
        filter_value.exchanges,
    ):
        return False

    if not _favorite_matches_list(
        value.symbol,
        filter_value.symbols,
    ):
        return False

    if not _favorite_matches_list(
        value.metadata.get("sector", ""),
        filter_value.sectors,
    ):
        return False

    if not _favorite_matches_list(
        value.metadata.get("industry", ""),
        filter_value.industries,
    ):
        return False

    if (
        value.state == FavoriteState.INVALIDATED
        and not filter_value.include_invalidated
    ):
        return False

    if (
        value.state == FavoriteState.EXPIRED
        and not filter_value.include_expired
    ):
        return False

    return True


def favorite_market_matches_filter(
    value: FavoriteMarket,
    filter_value: FavoritesFilter,
) -> bool:

    if not value.favorite:
        return False

    if (
        filter_value.asset_classes
        and value.asset_class
        not in filter_value.asset_classes
    ):
        return False

    if (
        filter_value.states
        and value.state
        not in filter_value.states
    ):
        return False

    if (
        filter_value.priorities
        and filter_value.priorities
    ):
        # Market records do not carry priority.
        pass

    if not _favorite_matches_list(
        value.market_id,
        filter_value.market_ids,
    ):
        return False

    if not _favorite_matches_list(
        value.exchange,
        filter_value.exchanges,
    ):
        return False

    return True


def favorite_record_matches_filter(
    value: FavoriteRecord,
    filter_value: FavoritesFilter,
) -> bool:

    if value.state == FavoriteState.REMOVED:
        return False

    if (
        value.asset_class
        not in (
            filter_value.asset_classes
            or [value.asset_class]
        )
    ):
        return False

    if (
        filter_value.item_types
        and value.item_type
        not in filter_value.item_types
    ):
        return False

    if (
        filter_value.states
        and value.state
        not in filter_value.states
    ):
        return False

    if (
        filter_value.priorities
        and value.priority
        not in filter_value.priorities
    ):
        return False

    if not _favorite_matches_list(
        value.symbol,
        filter_value.symbols,
    ):
        return False

    if (
        value.state == FavoriteState.INVALIDATED
        and not filter_value.include_invalidated
    ):
        return False

    if (
        value.state == FavoriteState.EXPIRED
        and not filter_value.include_expired
    ):
        return False

    return True


# ============================================================
# SOURCE FILTERING
# ============================================================

def filter_favorite_instruments(
    values: List[FavoriteInstrument],
    filter_value: FavoritesFilter,
) -> List[FavoriteInstrument]:

    return [
        item
        for item in values
        if favorite_instrument_matches_filter(
            item,
            filter_value,
        )
    ]


def filter_favorite_opportunities(
    values: List[FavoriteOpportunity],
    filter_value: FavoritesFilter,
) -> List[FavoriteOpportunity]:

    return [
        item
        for item in values
        if favorite_opportunity_matches_filter(
            item,
            filter_value,
        )
    ]


def filter_favorite_markets(
    values: List[FavoriteMarket],
    filter_value: FavoritesFilter,
) -> List[FavoriteMarket]:

    return [
        item
        for item in values
        if favorite_market_matches_filter(
            item,
            filter_value,
        )
    ]


def filter_favorite_records(
    values: List[FavoriteRecord],
    filter_value: FavoritesFilter,
) -> List[FavoriteRecord]:

    return [
        item
        for item in values
        if favorite_record_matches_filter(
            item,
            filter_value,
        )
    ]


# ============================================================
# SUMMARY
# ============================================================

def build_favorites_summary(
    identity: FavoriteIdentity,
    instruments: List[FavoriteInstrument],
    opportunities: List[FavoriteOpportunity],
    markets: List[FavoriteMarket],
    records: List[FavoriteRecord],
    status: FavoritesStatus,
) -> FavoritesSummary:

    bullish_count = sum(
        1
        for item in opportunities
        if item.bias == FavoriteBias.BULLISH
    )

    bearish_count = sum(
        1
        for item in opportunities
        if item.bias == FavoriteBias.BEARISH
    )

    high_priority_count = sum(
        1
        for item in records
        if item.priority == FavoritePriority.HIGH
    )

    critical_priority_count = sum(
        1
        for item in records
        if item.priority == FavoritePriority.CRITICAL
    )

    return FavoritesSummary(
        total_favorites=len(records),
        active_favorites=sum(
            1
            for item in records
            if item.state == FavoriteState.ACTIVE
        ),
        instrument_count=len(instruments),
        opportunity_count=len(opportunities),
        market_count=len(markets),
        bullish_count=bullish_count,
        bearish_count=bearish_count,
        high_priority_count=high_priority_count,
        critical_priority_count=critical_priority_count,
        authenticated=identity.authenticated,
        plus_enabled=identity.plus_enabled,
        status=status,
        metadata={
            "presentation_only": True,
            "intelligence_generated": False,
            "decision_generated": False,
        },
    )


# ============================================================
# SOURCE STATUS / RESULT
# ============================================================

def favorites_source_status(
    source: FavoritesSourceState,
    authenticated: bool,
) -> FavoritesStatus:

    if not authenticated:
        return FavoritesStatus.BLOCKED

    if not source.source_available:
        return FavoritesStatus.DEGRADED

    if source.source_errors:
        return FavoritesStatus.DEGRADED

    return FavoritesStatus.READY


def build_favorites_result(
    request: FavoritesRequest,
) -> FavoritesResult:

    normalized = normalize_favorites_request(
        request
    )

    source = normalized.source

    if source is None:
        source = normalize_favorites_source(
            None
        )

    status = favorites_source_status(
        source,
        normalized.authenticated,
    )

    if status == FavoritesStatus.BLOCKED:
        return FavoritesResult(
            status=FavoritesStatus.BLOCKED,
            favorites=[],
            instruments=[],
            opportunities=[],
            markets=[],
            summary=build_favorites_summary(
                source.identity,
                [],
                [],
                [],
                [],
                FavoritesStatus.BLOCKED,
            ),
            source_available=False,
            source_errors=[
                "Authenticated session required."
            ],
            warnings=[],
            generated_at=_favorite_now(),
            metadata={
                "presentation_only": True,
                "intelligence_generated": False,
                "decision_generated": False,
            },
        )

    filter_value = normalized.filter

    records = filter_favorite_records(
        source.records,
        filter_value,
    )

    instruments = filter_favorite_instruments(
        source.instruments,
        filter_value,
    )

    opportunities = filter_favorite_opportunities(
        source.opportunities,
        filter_value,
    )

    markets = filter_favorite_markets(
        source.markets,
        filter_value,
    )

    warnings: List[str] = []

    if not records:
        warnings.append(
            "No matching favorites found."
        )

    if source.source_errors:
        warnings.extend(
            source.source_errors
        )

    summary = build_favorites_summary(
        source.identity,
        instruments,
        opportunities,
        markets,
        records,
        status,
    )

    return FavoritesResult(
        status=status,
        favorites=records,
        instruments=instruments,
        opportunities=opportunities,
        markets=markets,
        summary=summary,
        source_available=source.source_available,
        source_errors=list(
            source.source_errors
        ),
        warnings=warnings,
        generated_at=_favorite_now(),
        metadata={
            "presentation_only": True,
            "upstream_truth_preserved": True,
            "intelligence_generated": False,
            "decision_generated": False,
            "d13_modified": False,
            "risk_generated": False,
            "cas_bypassed": False,
            "execution_authority": False,
        },
    )


def run_favorites(
    request: FavoritesRequest,
) -> FavoritesResult:

    return build_favorites_result(
        normalize_favorites_request(request)
    )
# ============================================================
# ROBOMLM_PLUS — DISCOVERY FAVORITES
# PART 3 — STATE / CONTROLLER / INTERACTION / SNAPSHOT
# ============================================================


@dataclass
class FavoritesState:
    initialized: bool = False
    ready: bool = False
    authenticated: bool = False

    status: FavoritesStatus = FavoritesStatus.IDLE

    request_count: int = 0
    refresh_count: int = 0

    last_error: str = ""
    last_refresh_at: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def create_favorites_state(
    authenticated: bool = False,
) -> FavoritesState:

    return FavoritesState(
        initialized=False,
        ready=False,
        authenticated=authenticated,
        status=(
            FavoritesStatus.IDLE
            if authenticated
            else FavoritesStatus.BLOCKED
        ),
    )


def normalize_favorites_state(
    value: Optional[FavoritesState],
) -> FavoritesState:

    if value is None:
        return create_favorites_state()

    status = _favorite_enum(
        value.status,
        FavoritesStatus,
        FavoritesStatus.UNKNOWN,
    )

    return FavoritesState(
        initialized=_favorite_bool(
            value.initialized
        ),
        ready=_favorite_bool(
            value.ready
        ),
        authenticated=_favorite_bool(
            value.authenticated
        ),
        status=status,
        request_count=max(
            0,
            int(value.request_count),
        ),
        refresh_count=max(
            0,
            int(value.refresh_count),
        ),
        last_error=_favorite_text(
            value.last_error
        ),
        last_refresh_at=_favorite_text(
            value.last_refresh_at
        ),
        metadata=dict(value.metadata or {}),
    )


# ============================================================
# CONTROLLER
# ============================================================

class FavoritesController:

    def __init__(
        self,
        state: Optional[FavoritesState] = None,
    ) -> None:

        self._state = normalize_favorites_state(
            state
        )

        self._last_request: Optional[
            FavoritesRequest
        ] = None

        self._last_result: Optional[
            FavoritesResult
        ] = None

        self._request_history: List[
            FavoritesRequest
        ] = []

        self._result_history: List[
            FavoritesResult
        ] = []

    @property
    def state(self) -> FavoritesState:
        return self._state

    @property
    def status(self) -> FavoritesStatus:
        return self._state.status

    @property
    def authenticated(self) -> bool:
        return self._state.authenticated

    @property
    def last_request(
        self,
    ) -> Optional[FavoritesRequest]:
        return self._last_request

    @property
    def last_result(
        self,
    ) -> Optional[FavoritesResult]:
        return self._last_result

    def initialize(self) -> FavoritesState:

        self._state.initialized = True

        if self._state.authenticated:
            self._state.ready = True
            self._state.status = (
                FavoritesStatus.READY
            )
        else:
            self._state.ready = False
            self._state.status = (
                FavoritesStatus.BLOCKED
            )

        return self._state

    def set_authenticated(
        self,
        authenticated: bool,
    ) -> FavoritesState:

        self._state.authenticated = (
            bool(authenticated)
        )

        if not authenticated:
            self._state.ready = False
            self._state.status = (
                FavoritesStatus.BLOCKED
            )
            return self._state

        if self._state.initialized:
            self._state.ready = True
            self._state.status = (
                FavoritesStatus.READY
            )

        return self._state

    def load(
        self,
        request: FavoritesRequest,
    ) -> FavoritesResult:

        normalized = normalize_favorites_request(
            request
        )

        normalized.authenticated = (
            self._state.authenticated
        )

        self._state.request_count += 1

        self._last_request = normalized

        self._request_history.append(
            normalized
        )

        if len(self._request_history) > 500:
            del self._request_history[:-500]

        try:
            result = run_favorites(
                normalized
            )

            self._last_result = result

            self._result_history.append(
                result
            )

            if len(self._result_history) > 500:
                del self._result_history[:-500]

            self._state.status = result.status

            self._state.ready = (
                result.status
                == FavoritesStatus.READY
            )

            self._state.last_error = ""

            self._state.last_refresh_at = (
                result.generated_at
            )

            return result

        except Exception as exc:

            self._state.status = (
                FavoritesStatus.ERROR
            )

            self._state.ready = False

            self._state.last_error = str(
                exc
            )

            return FavoritesResult(
                status=FavoritesStatus.ERROR,
                generated_at=_favorite_now(),
                source_available=False,
                source_errors=[
                    str(exc)
                ],
                warnings=[],
                metadata={
                    "presentation_only": True,
                    "intelligence_generated": False,
                    "decision_generated": False,
                    "d13_modified": False,
                    "risk_generated": False,
                    "cas_bypassed": False,
                    "execution_authority": False,
                },
            )

    def refresh(
        self,
        request: FavoritesRequest,
    ) -> FavoritesResult:

        self._state.refresh_count += 1

        return self.load(request)

    def block(self) -> FavoritesState:

        self._state.ready = False

        self._state.status = (
            FavoritesStatus.BLOCKED
        )

        return self._state

    def reset(self) -> FavoritesState:

        self._state = create_favorites_state(
            authenticated=self._state.authenticated
        )

        self._last_request = None
        self._last_result = None

        self._request_history.clear()
        self._result_history.clear()

        return self._state

    def snapshot(
        self,
    ) -> "FavoritesSnapshot":

        request = (
            self._last_request
            or FavoritesRequest(
                authenticated=self.authenticated
            )
        )

        result = (
            self._last_result
            or FavoritesResult(
                status=self.status,
                generated_at=_favorite_now(),
            )
        )

        return FavoritesSnapshot(
            request=request,
            result=result,
            captured_at=_favorite_now(),
            metadata={
                "presentation_only": True,
                "upstream_truth_preserved": True,
                "intelligence_generated": False,
                "decision_generated": False,
                "d13_modified": False,
                "risk_generated": False,
                "cas_bypassed": False,
                "execution_authority": False,
            },
        )

    @property
    def request_history(
        self,
    ) -> List[FavoritesRequest]:

        return list(self._request_history)

    @property
    def result_history(
        self,
    ) -> List[FavoritesResult]:

        return list(self._result_history)


# ============================================================
# DEFAULT CONTROLLER
# ============================================================

_DEFAULT_FAVORITES = FavoritesController()


def get_favorites() -> FavoritesController:

    return _DEFAULT_FAVORITES


def create_favorites(
    authenticated: bool = False,
) -> FavoritesController:

    return FavoritesController(
        create_favorites_state(
            authenticated=authenticated
        )
    )


def load_favorites(
    request: FavoritesRequest,
) -> FavoritesResult:

    return get_favorites().load(request)


def refresh_favorites(
    request: FavoritesRequest,
) -> FavoritesResult:

    return get_favorites().refresh(request)


# ============================================================
# INTERACTION MODEL
# ============================================================

class FavoritesAction(str, Enum):
    VIEW_ALL = "VIEW_ALL"
    VIEW_INSTRUMENTS = "VIEW_INSTRUMENTS"
    VIEW_OPPORTUNITIES = "VIEW_OPPORTUNITIES"
    VIEW_MARKETS = "VIEW_MARKETS"
    REFRESH = "REFRESH"
    CLEAR_FILTER = "CLEAR_FILTER"
    NONE = "NONE"


@dataclass
class FavoritesInteraction:
    action: FavoritesAction = FavoritesAction.NONE
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class FavoritesInteractionResult:
    action: FavoritesAction
    accepted: bool
    message: str = ""
    route: str = ""
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def normalize_favorites_interaction(
    value: Optional[FavoritesInteraction],
) -> FavoritesInteraction:

    if value is None:
        return FavoritesInteraction()

    return FavoritesInteraction(
        action=_favorite_enum(
            value.action,
            FavoritesAction,
            FavoritesAction.NONE,
        ),
        metadata=dict(value.metadata or {}),
    )


def resolve_favorites_interaction(
    interaction: FavoritesInteraction,
) -> FavoritesInteractionResult:

    value = normalize_favorites_interaction(
        interaction
    )

    routes = {
        FavoritesAction.VIEW_ALL:
            "/discovery/favorites",

        FavoritesAction.VIEW_INSTRUMENTS:
            "/discovery/favorites/instruments",

        FavoritesAction.VIEW_OPPORTUNITIES:
            "/discovery/favorites/opportunities",

        FavoritesAction.VIEW_MARKETS:
            "/discovery/favorites/markets",

        FavoritesAction.REFRESH:
            "/discovery/favorites",

        FavoritesAction.CLEAR_FILTER:
            "/discovery/favorites",

        FavoritesAction.NONE:
            "",
    }

    if value.action == FavoritesAction.NONE:
        return FavoritesInteractionResult(
            action=value.action,
            accepted=False,
            message="No favorites action requested.",
            metadata={
                "presentation_only": True
            },
        )

    return FavoritesInteractionResult(
        action=value.action,
        accepted=True,
        message="Favorites action accepted.",
        route=routes.get(
            value.action,
            "/discovery/favorites",
        ),
        metadata={
            "presentation_only": True,
            "intelligence_generation": False,
            "decision_generation": False,
            "d13_modification": False,
            "risk_override": False,
            "cas_bypass": False,
            "execution": False,
        },
    )
# ============================================================
# ROBOMLM_PLUS — DISCOVERY FAVORITES
# PART 4 — SERIALIZATION / VALIDATION / HEALTH
# ============================================================


def _serialize_favorite_value(
    value: Any,
) -> Any:

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, list):
        return [
            _serialize_favorite_value(item)
            for item in value
        ]

    if isinstance(value, tuple):
        return [
            _serialize_favorite_value(item)
            for item in value
        ]

    if isinstance(value, dict):
        return {
            str(key): _serialize_favorite_value(item)
            for key, item in value.items()
        }

    if hasattr(value, "__dataclass_fields__"):
        return {
            key: _serialize_favorite_value(
                getattr(value, key)
            )
            for key in value.__dataclass_fields__
        }

    return value


def serialize_favorite_identity(
    value: FavoriteIdentity,
) -> Dict[str, Any]:
    return _serialize_favorite_value(value)


def serialize_favorite_instrument(
    value: FavoriteInstrument,
) -> Dict[str, Any]:
    return _serialize_favorite_value(value)


def serialize_favorite_opportunity(
    value: FavoriteOpportunity,
) -> Dict[str, Any]:
    return _serialize_favorite_value(value)


def serialize_favorite_market(
    value: FavoriteMarket,
) -> Dict[str, Any]:
    return _serialize_favorite_value(value)


def serialize_favorite_record(
    value: FavoriteRecord,
) -> Dict[str, Any]:
    return _serialize_favorite_value(value)


def serialize_favorites_filter(
    value: FavoritesFilter,
) -> Dict[str, Any]:
    return _serialize_favorite_value(value)


def serialize_favorites_source(
    value: FavoritesSourceState,
) -> Dict[str, Any]:
    return _serialize_favorite_value(value)


def serialize_favorites_summary(
    value: FavoritesSummary,
) -> Dict[str, Any]:
    return _serialize_favorite_value(value)


def serialize_favorites_request(
    value: FavoritesRequest,
) -> Dict[str, Any]:
    return _serialize_favorite_value(value)


def serialize_favorites_result(
    value: FavoritesResult,
) -> Dict[str, Any]:
    return _serialize_favorite_value(value)


def serialize_favorites_state(
    value: FavoritesState,
) -> Dict[str, Any]:
    return _serialize_favorite_value(value)


def serialize_favorites_snapshot(
    value: FavoritesSnapshot,
) -> Dict[str, Any]:
    return _serialize_favorite_value(value)


# ============================================================
# VALIDATION
# ============================================================

def validate_favorite_identity(
    value: FavoriteIdentity,
) -> bool:

    if not isinstance(value, FavoriteIdentity):
        return False

    if value.authenticated and not value.user_id:
        return False

    return True


def validate_favorite_instrument(
    value: FavoriteInstrument,
) -> bool:

    if not value.instrument_id:
        return False

    if not value.symbol:
        return False

    if value.asset_class == FavoriteAssetClass.UNKNOWN:
        return False

    if value.state == FavoriteState.UNKNOWN:
        return False

    if value.priority == FavoritePriority.CRITICAL:
        if not value.favorite:
            return False

    return True


def validate_favorite_opportunity(
    value: FavoriteOpportunity,
) -> bool:

    if not value.opportunity_id:
        return False

    if not value.instrument_id:
        return False

    if not value.symbol:
        return False

    if value.asset_class == FavoriteAssetClass.UNKNOWN:
        return False

    if value.state == FavoriteState.UNKNOWN:
        return False

    if value.bias == FavoriteBias.UNKNOWN:
        return False

    if not 0.0 <= value.confidence <= 1.0:
        return False

    if not value.favorite:
        return False

    return True


def validate_favorite_market(
    value: FavoriteMarket,
) -> bool:

    if not value.market_id:
        return False

    if not value.market_name:
        return False

    if value.asset_class == FavoriteAssetClass.UNKNOWN:
        return False

    if value.state == FavoriteState.UNKNOWN:
        return False

    return True


def validate_favorite_record(
    value: FavoriteRecord,
) -> bool:

    if not value.favorite_id:
        return False

    if not value.item_id:
        return False

    if value.item_type == FavoriteItemType.UNKNOWN:
        return False

    if value.asset_class == FavoriteAssetClass.UNKNOWN:
        return False

    if value.state == FavoriteState.UNKNOWN:
        return False

    if value.priority == FavoritePriority.CRITICAL:
        if not value.favorite_id:
            return False

    return True


def validate_favorites_filter(
    value: FavoritesFilter,
) -> bool:

    if not isinstance(value.asset_classes, list):
        return False

    if not isinstance(value.item_types, list):
        return False

    if not isinstance(value.states, list):
        return False

    if not isinstance(value.priorities, list):
        return False

    for item in value.asset_classes:
        if item == FavoriteAssetClass.UNKNOWN:
            return False

    for item in value.item_types:
        if item == FavoriteItemType.UNKNOWN:
            return False

    for item in value.states:
        if item == FavoriteState.UNKNOWN:
            return False

    for item in value.priorities:
        if item == FavoritePriority.UNKNOWN:
            return False

    return True


def validate_favorites_source(
    value: FavoritesSourceState,
) -> bool:

    if not validate_favorite_identity(
        value.identity
    ):
        return False

    for item in value.instruments:
        if not validate_favorite_instrument(item):
            return False

    for item in value.opportunities:
        if not validate_favorite_opportunity(item):
            return False

    for item in value.markets:
        if not validate_favorite_market(item):
            return False

    for item in value.records:
        if not validate_favorite_record(item):
            return False

    return True


def validate_favorites_summary(
    value: FavoritesSummary,
) -> bool:

    counters = (
        value.total_favorites,
        value.active_favorites,
        value.instrument_count,
        value.opportunity_count,
        value.market_count,
        value.bullish_count,
        value.bearish_count,
        value.high_priority_count,
        value.critical_priority_count,
    )

    if any(
        int(item) < 0
        for item in counters
    ):
        return False

    if value.status == FavoritesStatus.UNKNOWN:
        return False

    if (
        value.critical_priority_count
        > value.total_favorites
    ):
        return False

    return True


def validate_favorites_request(
    value: FavoritesRequest,
) -> bool:

    if not validate_favorites_filter(
        value.filter
    ):
        return False

    if value.source is not None:
        if not validate_favorites_source(
            value.source
        ):
            return False

    return True


def validate_favorites_result(
    value: FavoritesResult,
) -> bool:

    if value.status == FavoritesStatus.UNKNOWN:
        return False

    for item in value.favorites:
        if not validate_favorite_record(item):
            return False

    for item in value.instruments:
        if not validate_favorite_instrument(item):
            return False

    for item in value.opportunities:
        if not validate_favorite_opportunity(item):
            return False

    for item in value.markets:
        if not validate_favorite_market(item):
            return False

    if value.summary is not None:
        if not validate_favorites_summary(
            value.summary
        ):
            return False

    metadata = value.metadata

    forbidden_flags = (
        "intelligence_generated",
        "decision_generated",
        "d13_modified",
        "risk_generated",
        "cas_bypassed",
        "execution_authority",
    )

    for flag in forbidden_flags:
        if metadata.get(flag) is True:
            return False

    return True


def validate_favorites_state(
    value: FavoritesState,
) -> bool:

    if value.status == FavoritesStatus.UNKNOWN:
        return False

    if value.request_count < 0:
        return False

    if value.refresh_count < 0:
        return False

    if value.status == FavoritesStatus.READY:
        if not value.ready:
            return False

    if value.status == FavoritesStatus.BLOCKED:
        if value.ready:
            return False

    return True


def validate_favorites_snapshot(
    value: FavoritesSnapshot,
) -> bool:

    if not validate_favorites_request(
        value.request
    ):
        return False

    if not validate_favorites_result(
        value.result
    ):
        return False

    if not value.captured_at:
        return False

    metadata = value.metadata

    if metadata.get(
        "intelligence_generated"
    ) is True:
        return False

    if metadata.get(
        "decision_generated"
    ) is True:
        return False

    if metadata.get(
        "d13_modified"
    ) is True:
        return False

    return True


def validate_favorites_authority(
    authority: Dict[str, Any],
) -> bool:

    forbidden = (
        "market_data_generation",
        "evidence_generation",
        "intelligence_generation",
        "decision_generation",
        "d13_modification",
        "risk_generation",
        "risk_override",
        "cas_generation",
        "cas_bypass",
        "execution",
        "order_authority",
        "order_mutation",
        "position_authority",
        "position_mutation",
        "portfolio_mutation",
        "opportunity_generation",
        "scanner_intelligence_generation",
        "upstream_mutation",
    )

    for key in forbidden:
        if authority.get(key) is not False:
            return False

    return True


# ============================================================
# HEALTH
# ============================================================

@dataclass
class FavoritesHealth:
    engine: str
    version: str
    status: FavoritesStatus

    initialized: bool
    ready: bool
    authenticated: bool

    state_valid: bool
    authority_valid: bool
    last_result_valid: bool

    warnings: List[str] = field(
        default_factory=list
    )

    errors: List[str] = field(
        default_factory=list
    )

    presentation_only: bool = True
    upstream_truth_preserved: bool = True


def build_favorites_health(
    controller: Optional[
        FavoritesController
    ] = None,
) -> FavoritesHealth:

    current = (
        controller
        or get_favorites()
    )

    state_valid = validate_favorites_state(
        current.state
    )

    authority_valid = validate_favorites_authority(
        FAVORITES_AUTHORITY
    )

    last_result_valid = True

    if current.last_result is not None:
        last_result_valid = (
            validate_favorites_result(
                current.last_result
            )
        )

    warnings: List[str] = []
    errors: List[str] = []

    if not current.authenticated:
        warnings.append(
            "Authenticated session required."
        )

    if current.status == FavoritesStatus.DEGRADED:
        warnings.append(
            "Favorites source is degraded."
        )

    if not state_valid:
        errors.append(
            "Favorites state validation failed."
        )

    if not authority_valid:
        errors.append(
            "Favorites authority validation failed."
        )

    if not last_result_valid:
        errors.append(
            "Last favorites result validation failed."
        )

    return FavoritesHealth(
        engine=FAVORITES_ENGINE,
        version=FAVORITES_VERSION,
        status=current.status,
        initialized=current.state.initialized,
        ready=current.state.ready,
        authenticated=current.authenticated,
        state_valid=state_valid,
        authority_valid=authority_valid,
        last_result_valid=last_result_valid,
        warnings=warnings,
        errors=errors,
        presentation_only=True,
        upstream_truth_preserved=True,
    )


def serialize_favorites_health(
    value: FavoritesHealth,
) -> Dict[str, Any]:

    return _serialize_favorite_value(value)


def favorites_operational_check(
    controller: Optional[
        FavoritesController
    ] = None,
) -> Dict[str, Any]:

    health = build_favorites_health(
        controller
    )

    return {
        "engine": health.engine,
        "version": health.version,

        "operational": (
            health.state_valid
            and health.authority_valid
            and health.last_result_valid
            and not health.errors
        ),

        "status": health.status.value,
        "initialized": health.initialized,
        "ready": health.ready,
        "authenticated": health.authenticated,

        "presentation_only": True,
        "upstream_truth_preserved": True,

        "intelligence_generation": False,
        "decision_generation": False,
        "d13_modification": False,
        "risk_override": False,
        "cas_bypass": False,
        "execution": False,

        "warnings": health.warnings,
        "errors": health.errors,
    }
# ============================================================
# ROBOMLM_PLUS — DISCOVERY FAVORITES
# PART 5 — DIAGNOSTICS / CONTRACT / SELF-CHECK / EXPORTS
# ============================================================


def diagnose_favorites(
    controller: Optional[FavoritesController] = None,
) -> Dict[str, Any]:

    current = controller or get_favorites()
    health = build_favorites_health(current)

    return {
        "engine": FAVORITES_ENGINE,
        "version": FAVORITES_VERSION,
        "name": FAVORITES_NAME,
        "status": current.status.value,

        "initialized": current.state.initialized,
        "ready": current.state.ready,
        "authenticated": current.authenticated,

        "presentation_only": True,
        "upstream_truth_preserved": True,

        "intelligence_generation": False,
        "decision_generation": False,
        "d13_modification": False,
        "risk_generation": False,
        "cas_bypass": False,
        "execution": False,

        "state_valid": health.state_valid,
        "authority_valid": health.authority_valid,
        "last_result_valid": health.last_result_valid,

        "warnings": list(health.warnings),
        "errors": list(health.errors),
    }


def favorites_summary(
    controller: Optional[FavoritesController] = None,
) -> Dict[str, Any]:

    current = controller or get_favorites()

    if current.last_result is None:
        return {
            "engine": FAVORITES_ENGINE,
            "status": current.status.value,
            "total_favorites": 0,
            "active_favorites": 0,
            "instrument_count": 0,
            "opportunity_count": 0,
            "market_count": 0,
            "bullish_count": 0,
            "bearish_count": 0,
            "high_priority_count": 0,
            "critical_priority_count": 0,
            "presentation_only": True,
        }

    result = current.last_result

    summary = result.summary

    if summary is None:
        return {
            "engine": FAVORITES_ENGINE,
            "status": result.status.value,
            "total_favorites": len(
                result.favorites
            ),
            "active_favorites": 0,
            "instrument_count": len(
                result.instruments
            ),
            "opportunity_count": len(
                result.opportunities
            ),
            "market_count": len(
                result.markets
            ),
            "presentation_only": True,
        }

    return {
        "engine": FAVORITES_ENGINE,
        "version": FAVORITES_VERSION,
        "status": result.status.value,

        "total_favorites": summary.total_favorites,
        "active_favorites": summary.active_favorites,

        "instrument_count": summary.instrument_count,
        "opportunity_count": summary.opportunity_count,
        "market_count": summary.market_count,

        "bullish_count": summary.bullish_count,
        "bearish_count": summary.bearish_count,

        "high_priority_count": (
            summary.high_priority_count
        ),
        "critical_priority_count": (
            summary.critical_priority_count
        ),

        "authenticated": summary.authenticated,
        "plus_enabled": summary.plus_enabled,

        "presentation_only": True,
        "upstream_truth_preserved": True,

        "intelligence_generated": False,
        "decision_generated": False,
        "d13_modified": False,
        "risk_generated": False,
        "cas_bypassed": False,
        "execution_authority": False,
    }


def favorites_contract_manifest() -> Dict[str, Any]:

    return {
        "engine": FAVORITES_ENGINE,
        "version": FAVORITES_VERSION,
        "layer": "UI_PRESENTATION",
        "role": "DISCOVERY_FAVORITES",
        "importance": "SUPPORTING_DISCOVERY_COMPONENT",

        "objective": {
            "preserve_user_selected_opportunities": True,
            "preserve_user_selected_instruments": True,
            "fast_opportunity_retrieval": True,
            "better_opportunity_access": True,
        },

        "inputs": [
            "USER_SERVICE_OUTPUT",
            "UPSTREAM_EQUITY_OPPORTUNITY_OUTPUT",
            "UPSTREAM_OPPORTUNITY_ENGINE_OUTPUT",
            "EQUITY_SCANNER_OUTPUT",
            "STOCK_SCANNER_OUTPUT",
            "UNIVERSAL_SCANNER_OUTPUT",
            "WATCHLIST_OUTPUT",
            "FAVORITES_SOURCE",
            "APPLICATION_SESSION_STATE",
        ],

        "processing": [
            "SOURCE_NORMALIZATION",
            "FAVORITE_FILTERING",
            "ASSET_CLASS_FILTERING",
            "ITEM_TYPE_FILTERING",
            "MARKET_FILTERING",
            "EXCHANGE_FILTERING",
            "SECTOR_FILTERING",
            "INDUSTRY_FILTERING",
            "STATE_FILTERING",
            "PRIORITY_FILTERING",
            "OPPORTUNITY_PRESENTATION",
            "INSTRUMENT_PRESENTATION",
            "MARKET_PRESENTATION",
        ],

        "outputs": [
            "FAVORITES_RESULT",
            "FAVORITES_SUMMARY",
            "FAVORITES_SNAPSHOT",
            "FAVORITES_HEALTH",
            "FAVORITES_DIAGNOSTICS",
        ],

        "truth_policy": {
            "upstream_truth_preserved": True,
            "favorite_selection_is_presentation_state": True,
            "favorite_surface_generates_intelligence": False,
            "favorite_surface_generates_decision": False,
            "favorite_surface_changes_upstream_truth": False,
        },

        "intelligence_boundary": {
            "structure_intelligence_owner":
                "UPSTREAM_EQUITY_STRUCTURE_INTELLIGENCE",

            "consolidation_owner":
                "UPSTREAM_EQUITY_STRUCTURE_INTELLIGENCE",

            "accumulation_distribution_owner":
                "UPSTREAM_EQUITY_STRUCTURE_INTELLIGENCE",

            "breakout_boundary_owner":
                "UPSTREAM_EQUITY_STRUCTURE_INTELLIGENCE",

            "breakout_direction_owner":
                "UPSTREAM_EQUITY_STRUCTURE_INTELLIGENCE",

            "breakout_confirmation_owner":
                "UPSTREAM_EQUITY_STRUCTURE_INTELLIGENCE",

            "exact_levels_owner":
                "UPSTREAM_EQUITY_STRUCTURE_INTELLIGENCE",
        },

        "forbidden": [
            "MARKET_DATA_GENERATION",
            "EVIDENCE_GENERATION",
            "INTELLIGENCE_GENERATION",
            "DECISION_GENERATION",
            "D13_MODIFICATION",
            "RISK_GENERATION",
            "RISK_OVERRIDE",
            "CAS_GENERATION",
            "CAS_BYPASS",
            "EXECUTION",
            "ORDER_MUTATION",
            "POSITION_MUTATION",
            "PORTFOLIO_MUTATION",
            "OPPORTUNITY_GENERATION",
            "SCANNER_INTELLIGENCE_GENERATION",
            "UPSTREAM_MUTATION",
        ],
    }


def validate_favorites_integrity(
    controller: Optional[FavoritesController] = None,
) -> bool:

    current = controller or get_favorites()

    if not validate_favorites_authority(
        FAVORITES_AUTHORITY
    ):
        return False

    if not validate_favorites_state(
        current.state
    ):
        return False

    if current.last_request is not None:
        if not validate_favorites_request(
            current.last_request
        ):
            return False

    if current.last_result is not None:
        if not validate_favorites_result(
            current.last_result
        ):
            return False

    return True


def validate_favorites_contract() -> bool:

    manifest = favorites_contract_manifest()

    required = (
        "layer",
        "role",
        "importance",
        "inputs",
        "processing",
        "outputs",
        "truth_policy",
        "intelligence_boundary",
        "forbidden",
    )

    for key in required:
        if key not in manifest:
            return False

    truth_policy = manifest["truth_policy"]

    if truth_policy.get(
        "upstream_truth_preserved"
    ) is not True:
        return False

    if truth_policy.get(
        "favorite_surface_generates_intelligence"
    ) is not False:
        return False

    if truth_policy.get(
        "favorite_surface_generates_decision"
    ) is not False:
        return False

    if truth_policy.get(
        "favorite_surface_changes_upstream_truth"
    ) is not False:
        return False

    boundary = manifest[
        "intelligence_boundary"
    ]

    required_owners = (
        "structure_intelligence_owner",
        "consolidation_owner",
        "accumulation_distribution_owner",
        "breakout_boundary_owner",
        "breakout_direction_owner",
        "breakout_confirmation_owner",
        "exact_levels_owner",
    )

    for key in required_owners:
        if not boundary.get(key):
            return False

    return True


def favorites_module_check(
    controller: Optional[FavoritesController] = None,
) -> Dict[str, Any]:

    current = controller or get_favorites()

    integrity = validate_favorites_integrity(
        current
    )

    contract = validate_favorites_contract()

    operational = favorites_operational_check(
        current
    )

    return {
        "engine": FAVORITES_ENGINE,
        "version": FAVORITES_VERSION,

        "integrity_valid": integrity,
        "contract_valid": contract,
        "operational": operational["operational"],

        "presentation_only": True,
        "upstream_truth_preserved": True,

        "intelligence_generation": False,
        "decision_generation": False,
        "d13_modification": False,
        "risk_override": False,
        "cas_bypass": False,
        "execution": False,

        "errors": (
            []
            if integrity and contract
            else [
                "Favorites module validation failed."
            ]
        ),
    }


def favorites_self_check() -> Dict[str, Any]:

    identity = FavoriteIdentity(
        user_id="SELF_CHECK_USER",
        display_name="Self Check",
        authenticated=True,
    )

    instrument = FavoriteInstrument(
        instrument_id="SELF_CHECK_INSTRUMENT",
        symbol="TESTEQ",
        display_name="Test Equity",
        asset_class=FavoriteAssetClass.EQUITY,
        market_id="TEST_MARKET",
        market_name="Test Market",
        exchange="TEST_EXCHANGE",
        favorite=True,
        state=FavoriteState.ACTIVE,
        priority=FavoritePriority.HIGH,
    )

    opportunity = FavoriteOpportunity(
        opportunity_id="SELF_CHECK_OPPORTUNITY",
        instrument_id="SELF_CHECK_INSTRUMENT",
        symbol="TESTEQ",
        instrument_name="Test Equity",
        asset_class=FavoriteAssetClass.EQUITY,
        market_id="TEST_MARKET",
        exchange="TEST_EXCHANGE",
        state=FavoriteState.ACTIVE,
        bias=FavoriteBias.BULLISH,
        strength="STRONG",
        summary="Upstream opportunity self-check.",
        confidence=0.90,
        favorite=True,
        priority=FavoritePriority.HIGH,
        timestamp=_favorite_now(),
        metadata={
            "upstream_truth": True,
            "research_owner":
                "UPSTREAM_EQUITY_STRUCTURE_INTELLIGENCE",
            "scanner_generated_intelligence": False,
        },
    )

    record = FavoriteRecord(
        favorite_id="SELF_CHECK_FAVORITE",
        item_id="SELF_CHECK_INSTRUMENT",
        item_type=FavoriteItemType.INSTRUMENT,
        symbol="TESTEQ",
        display_name="Test Equity",
        asset_class=FavoriteAssetClass.EQUITY,
        state=FavoriteState.ACTIVE,
        priority=FavoritePriority.HIGH,
        created_at=_favorite_now(),
        updated_at=_favorite_now(),
    )

    source = FavoritesSourceState(
        identity=identity,
        instruments=[instrument],
        opportunities=[opportunity],
        records=[record],
        source_available=True,
    )

    request = FavoritesRequest(
        source=source,
        authenticated=True,
    )

    result = run_favorites(request)

    result_valid = validate_favorites_result(
        result
    )

    preserved = bool(
        result.opportunities
        and result.opportunities[0].symbol
        == opportunity.symbol
        and result.opportunities[0].bias
        == opportunity.bias
        and result.opportunities[0].metadata.get(
            "upstream_truth"
        ) is True
    )

    contract_valid = (
        validate_favorites_contract()
    )

    return {
        "engine": FAVORITES_ENGINE,
        "self_check": True,

        "request_valid":
            validate_favorites_request(request),

        "result_valid": result_valid,
        "upstream_truth_preserved": preserved,
        "contract_valid": contract_valid,

        "presentation_only": True,
        "intelligence_generation": False,
        "decision_generation": False,
        "d13_modification": False,
        "execution": False,

        "overall": (
            result_valid
            and preserved
            and contract_valid
        ),
    }


def create_default_favorites(
    authenticated: bool = False,
) -> FavoritesController:

    controller = create_favorites(
        authenticated=authenticated
    )

    controller.initialize()

    return controller


__all__ = [
    # Constants
    "FAVORITES_ENGINE",
    "FAVORITES_VERSION",
    "FAVORITES_NAME",
    "FAVORITES_TITLE",
    "FAVORITES_DESCRIPTION",
    "FAVORITES_AUTHORITY",

    # Enums
    "FavoritesStatus",
    "FavoriteAssetClass",
    "FavoriteItemType",
    "FavoritePriority",
    "FavoriteState",
    "FavoriteBias",

    # Schemas
    "FavoriteIdentity",
    "FavoriteInstrument",
    "FavoriteOpportunity",
    "FavoriteMarket",
    "FavoriteRecord",
    "FavoritesFilter",
    "FavoritesSourceState",
    "FavoritesSummary",
    "FavoritesRequest",
    "FavoritesResult",
    "FavoritesSnapshot",
    "FavoritesState",
    "FavoritesHealth",

    # Normalization
    "normalize_favorite_identity",
    "normalize_favorite_instrument",
    "normalize_favorite_opportunity",
    "normalize_favorite_market",
    "normalize_favorite_record",
    "normalize_favorites_filter",
    "normalize_favorites_source",
    "normalize_favorites_request",

    # Filtering
    "favorite_instrument_matches_filter",
    "favorite_opportunity_matches_filter",
    "favorite_market_matches_filter",
    "favorite_record_matches_filter",
    "filter_favorite_instruments",
    "filter_favorite_opportunities",
    "filter_favorite_markets",
    "filter_favorite_records",

    # Processing
    "build_favorites_summary",
    "favorites_source_status",
    "build_favorites_result",
    "run_favorites",

    # Controller
    "FavoritesController",
    "get_favorites",
    "create_favorites",
    "load_favorites",
    "refresh_favorites",

    # Interaction
    "FavoritesAction",
    "FavoritesInteraction",
    "FavoritesInteractionResult",
    "normalize_favorites_interaction",
    "resolve_favorites_interaction",

    # Serialization
    "serialize_favorite_identity",
    "serialize_favorite_instrument",
    "serialize_favorite_opportunity",
    "serialize_favorite_market",
    "serialize_favorite_record",
    "serialize_favorites_filter",
    "serialize_favorites_source",
    "serialize_favorites_summary",
    "serialize_favorites_request",
    "serialize_favorites_result",
    "serialize_favorites_state",
    "serialize_favorites_snapshot",
    "serialize_favorites_health",

    # Validation / health
    "validate_favorite_identity",
    "validate_favorite_instrument",
    "validate_favorite_opportunity",
    "validate_favorite_market",
    "validate_favorite_record",
    "validate_favorites_filter",
    "validate_favorites_source",
    "validate_favorites_summary",
    "validate_favorites_request",
    "validate_favorites_result",
    "validate_favorites_state",
    "validate_favorites_snapshot",
    "validate_favorites_authority",
    "build_favorites_health",
    "favorites_operational_check",

    # Diagnostics / contract
    "diagnose_favorites",
    "favorites_summary",
    "favorites_contract_manifest",
    "validate_favorites_integrity",
    "validate_favorites_contract",
    "favorites_module_check",
    "favorites_self_check",
    "create_default_favorites",
]