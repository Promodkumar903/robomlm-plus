# ============================================================
# ROBOMLM_PLUS — INDEX DISCOVERY SCANNER
# PART 1 — CORE CONTRACT / AUTHORITY / SCHEMAS
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


# ============================================================
# ENGINE IDENTITY
# ============================================================

INDEX_SCANNER_ENGINE = "ROBOMLM_PLUS_INDEX_SCANNER"
INDEX_SCANNER_VERSION = "1.0"
INDEX_SCANNER_NAME = "Index Opportunity Scanner"
INDEX_SCANNER_TITLE = "Index Market Opportunity Scanner"

INDEX_SCANNER_DESCRIPTION = (
    "Dedicated index discovery scanner for presenting and routing "
    "upstream index opportunity intelligence across supported "
    "markets, regions and index instruments."
)


# ============================================================
# AUTHORITY BOUNDARY
# ============================================================

# IMPORTANT:
# Index Scanner is an independent discovery surface.
#
# It does NOT become a dependency for Equity Scanner.
# Individual equities must remain independently scannable even
# in markets where a broad index is absent or not meaningful.
#
# Index-specific intelligence algorithms will be researched and
# plugged in upstream after the coding architecture is complete.

INDEX_SCANNER_AUTHORITY = {

    # --------------------------------------------------------
    # ALLOWED — PRESENTATION / ROUTING / FILTERING
    # --------------------------------------------------------

    "scanner_orchestration": True,
    "index_opportunity_presentation": True,
    "market_filtering": True,
    "region_filtering": True,
    "exchange_filtering": True,
    "index_filtering": True,
    "instrument_filtering": True,
    "category_filtering": True,
    "upstream_opportunity_consumption": True,

    # --------------------------------------------------------
    # INDEX INTELLIGENCE BOUNDARY
    # --------------------------------------------------------

    "index_specific_intelligence_consumption": True,
    "index_specific_algorithm_generation": False,
    "index_signal_generation": False,
    "index_score_generation": False,

    # --------------------------------------------------------
    # EQUITY INDEPENDENCE
    # --------------------------------------------------------

    "equity_scanner_dependency": False,
    "equity_scanner_authority": False,
    "individual_equity_requirement": False,

    # --------------------------------------------------------
    # FORBIDDEN AUTHORITY
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

    "opportunity_generation": False,
    "scanner_intelligence_generation": False,
    "upstream_mutation": False,
}


# ============================================================
# ENUMS
# ============================================================

class IndexScannerStatus(str, Enum):
    IDLE = "IDLE"
    LOADING = "LOADING"
    READY = "READY"
    DEGRADED = "DEGRADED"
    BLOCKED = "BLOCKED"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class IndexScannerMode(str, Enum):
    UNIVERSAL_INDICES = "UNIVERSAL_INDICES"
    MARKET = "MARKET"
    REGION = "REGION"
    EXCHANGE = "EXCHANGE"
    INDEX = "INDEX"
    CATEGORY = "CATEGORY"
    FAVORITES = "FAVORITES"
    WATCHLIST = "WATCHLIST"
    UNKNOWN = "UNKNOWN"


class IndexType(str, Enum):
    BROAD_MARKET = "BROAD_MARKET"
    SECTOR = "SECTOR"
    INDUSTRY = "INDUSTRY"
    THEMATIC = "THEMATIC"
    VOLATILITY = "VOLATILITY"
    STRATEGY = "STRATEGY"
    OTHER_INDEX = "OTHER_INDEX"
    UNKNOWN = "UNKNOWN"


class IndexOpportunityState(str, Enum):
    UNKNOWN = "UNKNOWN"
    WATCH = "WATCH"
    DEVELOPING = "DEVELOPING"
    QUALIFIED = "QUALIFIED"
    INVALIDATED = "INVALIDATED"
    EXPIRED = "EXPIRED"


class IndexOpportunityBias(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"


class IndexOpportunityStrength(str, Enum):
    VERY_WEAK = "VERY_WEAK"
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    VERY_STRONG = "VERY_STRONG"
    UNKNOWN = "UNKNOWN"


class IndexScannerPriority(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IndexSourceType(str, Enum):
    UPSTREAM_OPPORTUNITY_ENGINE = "UPSTREAM_OPPORTUNITY_ENGINE"
    INDEX_OPPORTUNITY_ENGINE = "INDEX_OPPORTUNITY_ENGINE"
    DISCOVERY_ENGINE = "DISCOVERY_ENGINE"
    UNKNOWN = "UNKNOWN"


# ============================================================
# NORMALIZATION HELPERS
# ============================================================

def _index_text(
    value: Any,
    default: str = "",
) -> str:

    if value is None:
        return default

    text = str(value).strip()

    return text if text else default


def _index_bool(
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


def _index_float(
    value: Any,
    default: float = 0.0,
) -> float:

    try:
        return float(value)

    except (TypeError, ValueError):
        return default


def _index_enum(
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


def _index_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ============================================================
# MARKET INPUT
# ============================================================

@dataclass
class IndexMarketInput:
    market_id: str
    market_name: str

    country: str = ""
    region: str = ""
    exchange: str = ""
    currency: str = ""
    timezone: str = ""

    enabled: bool = True
    selected: bool = False

    # Informational only.
    # This does NOT make index availability a requirement for
    # equity discovery.
    index_available: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# INDEX INSTRUMENT INPUT
# ============================================================

@dataclass
class IndexInstrumentInput:
    instrument_id: str
    symbol: str

    display_name: str = ""

    index_type: IndexType = IndexType.BROAD_MARKET

    market_id: str = ""
    country: str = ""
    region: str = ""
    exchange: str = ""
    currency: str = ""

    category: str = ""

    enabled: bool = True
    selected: bool = False
    tradable: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# UPSTREAM INDEX OPPORTUNITY
# ============================================================

@dataclass
class UpstreamIndexOpportunity:
    opportunity_id: str
    symbol: str

    instrument_id: str = ""
    instrument_name: str = ""

    index_type: IndexType = IndexType.BROAD_MARKET

    market_id: str = ""
    country: str = ""
    region: str = ""
    exchange: str = ""
    currency: str = ""

    category: str = ""

    # --------------------------------------------------------
    # UPSTREAM INTELLIGENCE OUTPUT
    # --------------------------------------------------------

    state: IndexOpportunityState = (
        IndexOpportunityState.UNKNOWN
    )

    bias: IndexOpportunityBias = (
        IndexOpportunityBias.UNKNOWN
    )

    strength: IndexOpportunityStrength = (
        IndexOpportunityStrength.UNKNOWN
    )

    summary: str = ""

    confidence: float = 0.0

    timestamp: str = ""

    favorite: bool = False
    watchlisted: bool = False

    priority: IndexScannerPriority = (
        IndexScannerPriority.NORMAL
    )

    source: IndexSourceType = (
        IndexSourceType.UPSTREAM_OPPORTUNITY_ENGINE
    )

    # --------------------------------------------------------
    # FUTURE INDEX-SPECIFIC RESEARCH OUTPUT
    # --------------------------------------------------------

    # These fields remain upstream-owned.
    #
    # No index formula is invented here.
    # Future validated research can populate these through
    # the upstream Index Intelligence / Opportunity Engine.

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# INDEX SCANNER FILTER
# ============================================================

@dataclass
class IndexScannerFilter:

    market_ids: List[str] = field(
        default_factory=list
    )

    countries: List[str] = field(
        default_factory=list
    )

    regions: List[str] = field(
        default_factory=list
    )

    exchange_names: List[str] = field(
        default_factory=list
    )

    instrument_ids: List[str] = field(
        default_factory=list
    )

    symbols: List[str] = field(
        default_factory=list
    )

    index_types: List[IndexType] = field(
        default_factory=list
    )

    categories: List[str] = field(
        default_factory=list
    )

    states: List[IndexOpportunityState] = field(
        default_factory=list
    )

    biases: List[IndexOpportunityBias] = field(
        default_factory=list
    )

    strengths: List[IndexOpportunityStrength] = field(
        default_factory=list
    )

    favorites_only: bool = False
    watchlist_only: bool = False
    tradable_only: bool = True

    include_invalidated: bool = False
    include_expired: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# SCANNER OPPORTUNITY
# ============================================================

@dataclass
class IndexScannerOpportunity:

    opportunity_id: str
    symbol: str

    instrument_id: str
    instrument_name: str

    index_type: IndexType

    market_id: str
    country: str
    region: str
    exchange: str
    currency: str

    category: str

    state: IndexOpportunityState
    bias: IndexOpportunityBias
    strength: IndexOpportunityStrength

    summary: str
    confidence: float
    timestamp: str

    favorite: bool
    watchlisted: bool

    priority: IndexScannerPriority
    source: IndexSourceType

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# SCANNER RESULT
# ============================================================

@dataclass
class IndexScannerResult:

    status: IndexScannerStatus
    mode: IndexScannerMode

    opportunities: List[IndexScannerOpportunity] = field(
        default_factory=list
    )

    total_input_opportunities: int = 0
    total_output_opportunities: int = 0

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


# ============================================================
# SCANNER REQUEST
# ============================================================

@dataclass
class IndexScannerRequest:

    mode: IndexScannerMode = (
        IndexScannerMode.UNIVERSAL_INDICES
    )

    markets: List[IndexMarketInput] = field(
        default_factory=list
    )

    instruments: List[IndexInstrumentInput] = field(
        default_factory=list
    )

    opportunities: List[UpstreamIndexOpportunity] = field(
        default_factory=list
    )

    scanner_filter: IndexScannerFilter = field(
        default_factory=IndexScannerFilter
    )

    authenticated: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# SNAPSHOT
# ============================================================

@dataclass
class IndexScannerSnapshot:

    request: IndexScannerRequest

    result: IndexScannerResult

    captured_at: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )
# ============================================================
# ROBOMLM_PLUS — INDEX DISCOVERY SCANNER
# PART 2 — NORMALIZATION / FILTERING / UPSTREAM ROUTING
# ============================================================


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_index_market(
    value: Any,
) -> IndexMarketInput:

    if isinstance(value, IndexMarketInput):
        return value

    if not isinstance(value, dict):
        return IndexMarketInput(
            market_id="",
            market_name="",
        )

    return IndexMarketInput(
        market_id=_index_text(
            value.get("market_id")
        ),
        market_name=_index_text(
            value.get("market_name")
        ),
        country=_index_text(
            value.get("country")
        ),
        region=_index_text(
            value.get("region")
        ),
        exchange=_index_text(
            value.get("exchange")
        ),
        currency=_index_text(
            value.get("currency")
        ),
        timezone=_index_text(
            value.get("timezone")
        ),
        enabled=_index_bool(
            value.get("enabled"),
            True,
        ),
        selected=_index_bool(
            value.get("selected"),
            False,
        ),
        index_available=_index_bool(
            value.get("index_available"),
            True,
        ),
        metadata=dict(
            value.get("metadata") or {}
        ),
    )


def normalize_index_instrument(
    value: Any,
) -> IndexInstrumentInput:

    if isinstance(value, IndexInstrumentInput):
        return value

    if not isinstance(value, dict):
        return IndexInstrumentInput(
            instrument_id="",
            symbol="",
        )

    return IndexInstrumentInput(
        instrument_id=_index_text(
            value.get("instrument_id")
        ),
        symbol=_index_text(
            value.get("symbol")
        ),
        display_name=_index_text(
            value.get("display_name")
        ),
        index_type=_index_enum(
            value.get("index_type"),
            IndexType,
            IndexType.UNKNOWN,
        ),
        market_id=_index_text(
            value.get("market_id")
        ),
        country=_index_text(
            value.get("country")
        ),
        region=_index_text(
            value.get("region")
        ),
        exchange=_index_text(
            value.get("exchange")
        ),
        currency=_index_text(
            value.get("currency")
        ),
        category=_index_text(
            value.get("category")
        ),
        enabled=_index_bool(
            value.get("enabled"),
            True,
        ),
        selected=_index_bool(
            value.get("selected"),
            False,
        ),
        tradable=_index_bool(
            value.get("tradable"),
            True,
        ),
        metadata=dict(
            value.get("metadata") or {}
        ),
    )


def normalize_upstream_index_opportunity(
    value: Any,
) -> UpstreamIndexOpportunity:

    if isinstance(
        value,
        UpstreamIndexOpportunity,
    ):
        return value

    if not isinstance(value, dict):
        return UpstreamIndexOpportunity(
            opportunity_id="",
            symbol="",
        )

    return UpstreamIndexOpportunity(
        opportunity_id=_index_text(
            value.get("opportunity_id")
        ),
        symbol=_index_text(
            value.get("symbol")
        ),
        instrument_id=_index_text(
            value.get("instrument_id")
        ),
        instrument_name=_index_text(
            value.get("instrument_name")
        ),
        index_type=_index_enum(
            value.get("index_type"),
            IndexType,
            IndexType.UNKNOWN,
        ),
        market_id=_index_text(
            value.get("market_id")
        ),
        country=_index_text(
            value.get("country")
        ),
        region=_index_text(
            value.get("region")
        ),
        exchange=_index_text(
            value.get("exchange")
        ),
        currency=_index_text(
            value.get("currency")
        ),
        category=_index_text(
            value.get("category")
        ),
        state=_index_enum(
            value.get("state"),
            IndexOpportunityState,
            IndexOpportunityState.UNKNOWN,
        ),
        bias=_index_enum(
            value.get("bias"),
            IndexOpportunityBias,
            IndexOpportunityBias.UNKNOWN,
        ),
        strength=_index_enum(
            value.get("strength"),
            IndexOpportunityStrength,
            IndexOpportunityStrength.UNKNOWN,
        ),
        summary=_index_text(
            value.get("summary")
        ),
        confidence=_index_float(
            value.get("confidence"),
            0.0,
        ),
        timestamp=_index_text(
            value.get("timestamp")
        ),
        favorite=_index_bool(
            value.get("favorite"),
            False,
        ),
        watchlisted=_index_bool(
            value.get("watchlisted"),
            False,
        ),
        priority=_index_enum(
            value.get("priority"),
            IndexScannerPriority,
            IndexScannerPriority.NORMAL,
        ),
        source=_index_enum(
            value.get("source"),
            IndexSourceType,
            IndexSourceType.UNKNOWN,
        ),
        metadata=dict(
            value.get("metadata") or {}
        ),
    )


# ============================================================
# FILTER NORMALIZATION
# ============================================================

def _normalize_index_string_list(
    value: Any,
) -> List[str]:

    if value is None:
        return []

    if isinstance(value, str):
        value = [value]

    if not isinstance(value, (list, tuple, set)):
        return []

    return [
        _index_text(item)
        for item in value
        if _index_text(item)
    ]


def _normalize_index_enum_list(
    value: Any,
    enum_type: Any,
) -> List[Any]:

    if value is None:
        return []

    if not isinstance(value, (list, tuple, set)):
        value = [value]

    result: List[Any] = []

    for item in value:
        normalized = _index_enum(
            item,
            enum_type,
            enum_type.UNKNOWN,
        )

        if normalized != enum_type.UNKNOWN:
            result.append(normalized)

    return result


def normalize_index_filter(
    value: Any,
) -> IndexScannerFilter:

    if isinstance(
        value,
        IndexScannerFilter,
    ):
        return value

    if not isinstance(value, dict):
        return IndexScannerFilter()

    return IndexScannerFilter(
        market_ids=_normalize_index_string_list(
            value.get("market_ids")
        ),
        countries=_normalize_index_string_list(
            value.get("countries")
        ),
        regions=_normalize_index_string_list(
            value.get("regions")
        ),
        exchange_names=_normalize_index_string_list(
            value.get("exchange_names")
        ),
        instrument_ids=_normalize_index_string_list(
            value.get("instrument_ids")
        ),
        symbols=_normalize_index_string_list(
            value.get("symbols")
        ),
        index_types=_normalize_index_enum_list(
            value.get("index_types"),
            IndexType,
        ),
        categories=_normalize_index_string_list(
            value.get("categories")
        ),
        states=_normalize_index_enum_list(
            value.get("states"),
            IndexOpportunityState,
        ),
        biases=_normalize_index_enum_list(
            value.get("biases"),
            IndexOpportunityBias,
        ),
        strengths=_normalize_index_enum_list(
            value.get("strengths"),
            IndexOpportunityStrength,
        ),
        favorites_only=_index_bool(
            value.get("favorites_only"),
            False,
        ),
        watchlist_only=_index_bool(
            value.get("watchlist_only"),
            False,
        ),
        tradable_only=_index_bool(
            value.get("tradable_only"),
            True,
        ),
        include_invalidated=_index_bool(
            value.get("include_invalidated"),
            False,
        ),
        include_expired=_index_bool(
            value.get("include_expired"),
            False,
        ),
        metadata=dict(
            value.get("metadata") or {}
        ),
    )


def normalize_index_request(
    value: Any,
) -> IndexScannerRequest:

    if isinstance(
        value,
        IndexScannerRequest,
    ):
        return value

    if not isinstance(value, dict):
        return IndexScannerRequest()

    markets = [
        normalize_index_market(item)
        for item in value.get("markets", [])
    ]

    instruments = [
        normalize_index_instrument(item)
        for item in value.get("instruments", [])
    ]

    opportunities = [
        normalize_upstream_index_opportunity(item)
        for item in value.get("opportunities", [])
    ]

    return IndexScannerRequest(
        mode=_index_enum(
            value.get("mode"),
            IndexScannerMode,
            IndexScannerMode.UNKNOWN,
        ),
        markets=markets,
        instruments=instruments,
        opportunities=opportunities,
        scanner_filter=normalize_index_filter(
            value.get("scanner_filter")
        ),
        authenticated=_index_bool(
            value.get("authenticated"),
            False,
        ),
        metadata=dict(
            value.get("metadata") or {}
        ),
    )


# ============================================================
# MATCH HELPERS
# ============================================================

def _index_matches_list(
    value: str,
    allowed: List[str],
) -> bool:

    if not allowed:
        return True

    normalized_value = value.strip().lower()

    return normalized_value in {
        item.strip().lower()
        for item in allowed
    }


def _index_matches_enum_list(
    value: Any,
    allowed: List[Any],
) -> bool:

    if not allowed:
        return True

    return value in allowed


# ============================================================
# OPPORTUNITY FILTER
# ============================================================

def index_opportunity_matches_filter(
    opportunity: UpstreamIndexOpportunity,
    scanner_filter: IndexScannerFilter,
) -> bool:

    if not _index_matches_list(
        opportunity.market_id,
        scanner_filter.market_ids,
    ):
        return False

    if not _index_matches_list(
        opportunity.country,
        scanner_filter.countries,
    ):
        return False

    if not _index_matches_list(
        opportunity.region,
        scanner_filter.regions,
    ):
        return False

    if not _index_matches_list(
        opportunity.exchange,
        scanner_filter.exchange_names,
    ):
        return False

    if not _index_matches_list(
        opportunity.instrument_id,
        scanner_filter.instrument_ids,
    ):
        return False

    if not _index_matches_list(
        opportunity.symbol,
        scanner_filter.symbols,
    ):
        return False

    if not _index_matches_enum_list(
        opportunity.index_type,
        scanner_filter.index_types,
    ):
        return False

    if not _index_matches_list(
        opportunity.category,
        scanner_filter.categories,
    ):
        return False

    if not _index_matches_enum_list(
        opportunity.state,
        scanner_filter.states,
    ):
        return False

    if not _index_matches_enum_list(
        opportunity.bias,
        scanner_filter.biases,
    ):
        return False

    if not _index_matches_enum_list(
        opportunity.strength,
        scanner_filter.strengths,
    ):
        return False

    if (
        scanner_filter.favorites_only
        and not opportunity.favorite
    ):
        return False

    if (
        scanner_filter.watchlist_only
        and not opportunity.watchlisted
    ):
        return False

    if (
        not scanner_filter.include_invalidated
        and opportunity.state
        == IndexOpportunityState.INVALIDATED
    ):
        return False

    if (
        not scanner_filter.include_expired
        and opportunity.state
        == IndexOpportunityState.EXPIRED
    ):
        return False

    return True


def filter_upstream_index_opportunities(
    opportunities: List[UpstreamIndexOpportunity],
    scanner_filter: IndexScannerFilter,
) -> List[UpstreamIndexOpportunity]:

    return [
        opportunity
        for opportunity in opportunities
        if index_opportunity_matches_filter(
            opportunity,
            scanner_filter,
        )
    ]


# ============================================================
# MARKET FILTER
# ============================================================

def filter_index_markets(
    markets: List[IndexMarketInput],
    scanner_filter: IndexScannerFilter,
) -> List[IndexMarketInput]:

    result: List[IndexMarketInput] = []

    for market in markets:

        if not market.enabled:
            continue

        if not _index_matches_list(
            market.market_id,
            scanner_filter.market_ids,
        ):
            continue

        if not _index_matches_list(
            market.country,
            scanner_filter.countries,
        ):
            continue

        if not _index_matches_list(
            market.region,
            scanner_filter.regions,
        ):
            continue

        if not _index_matches_list(
            market.exchange,
            scanner_filter.exchange_names,
        ):
            continue

        result.append(market)

    return result


# ============================================================
# INSTRUMENT FILTER
# ============================================================

def filter_index_instruments(
    instruments: List[IndexInstrumentInput],
    scanner_filter: IndexScannerFilter,
) -> List[IndexInstrumentInput]:

    result: List[IndexInstrumentInput] = []

    for instrument in instruments:

        if not instrument.enabled:
            continue

        if (
            scanner_filter.tradable_only
            and not instrument.tradable
        ):
            continue

        if not _index_matches_list(
            instrument.market_id,
            scanner_filter.market_ids,
        ):
            continue

        if not _index_matches_list(
            instrument.country,
            scanner_filter.countries,
        ):
            continue

        if not _index_matches_list(
            instrument.region,
            scanner_filter.regions,
        ):
            continue

        if not _index_matches_list(
            instrument.exchange,
            scanner_filter.exchange_names,
        ):
            continue

        if not _index_matches_list(
            instrument.instrument_id,
            scanner_filter.instrument_ids,
        ):
            continue

        if not _index_matches_list(
            instrument.symbol,
            scanner_filter.symbols,
        ):
            continue

        if not _index_matches_enum_list(
            instrument.index_type,
            scanner_filter.index_types,
        ):
            continue

        if not _index_matches_list(
            instrument.category,
            scanner_filter.categories,
        ):
            continue

        result.append(instrument)

    return result


# ============================================================
# UPSTREAM → SCANNER CONVERSION
# ============================================================

def convert_upstream_index_opportunity(
    opportunity: UpstreamIndexOpportunity,
) -> IndexScannerOpportunity:

    metadata = dict(
        opportunity.metadata
    )

    # --------------------------------------------------------
    # TRUTH-PRESERVATION FLAGS
    # --------------------------------------------------------

    metadata.update({
        "upstream_truth": True,

        "scanner_generated_intelligence": False,
        "scanner_generated_score": False,
        "scanner_generated_decision": False,

        "index_algorithm_generated": False,

        "d13_modified": False,

        "risk_generated": False,
        "risk_overridden": False,

        "cas_bypassed": False,

        "execution_authority": False,
    })

    return IndexScannerOpportunity(
        opportunity_id=opportunity.opportunity_id,
        symbol=opportunity.symbol,
        instrument_id=opportunity.instrument_id,
        instrument_name=opportunity.instrument_name,
        index_type=opportunity.index_type,
        market_id=opportunity.market_id,
        country=opportunity.country,
        region=opportunity.region,
        exchange=opportunity.exchange,
        currency=opportunity.currency,
        category=opportunity.category,
        state=opportunity.state,
        bias=opportunity.bias,
        strength=opportunity.strength,
        summary=opportunity.summary,
        confidence=opportunity.confidence,
        timestamp=opportunity.timestamp,
        favorite=opportunity.favorite,
        watchlisted=opportunity.watchlisted,
        priority=opportunity.priority,
        source=opportunity.source,
        metadata=metadata,
    )


# ============================================================
# RESULT BUILDER
# ============================================================

def build_index_scanner_result(
    mode: IndexScannerMode,
    input_opportunities: List[
        UpstreamIndexOpportunity
    ],
    filtered_opportunities: List[
        UpstreamIndexOpportunity
    ],
    status: IndexScannerStatus,
    source_available: bool,
    source_errors: Optional[List[str]] = None,
    warnings: Optional[List[str]] = None,
) -> IndexScannerResult:

    output = [
        convert_upstream_index_opportunity(
            opportunity
        )
        for opportunity in filtered_opportunities
    ]

    return IndexScannerResult(
        status=status,
        mode=mode,
        opportunities=output,
        total_input_opportunities=len(
            input_opportunities
        ),
        total_output_opportunities=len(
            output
        ),
        source_available=source_available,
        source_errors=list(
            source_errors or []
        ),
        warnings=list(
            warnings or []
        ),
        generated_at=_index_now(),
        metadata={
            "upstream_truth_preserved": True,
            "scanner_generated_intelligence": False,
            "scanner_generated_score": False,
            "scanner_generated_decision": False,
            "index_algorithm_generated": False,
            "d13_modified": False,
            "risk_generated": False,
            "risk_overridden": False,
            "cas_bypassed": False,
            "execution_authority": False,

            # Explicit architecture boundary.
            "index_scanner_independent": True,
            "equity_scanner_dependency": False,
        },
    )


# ============================================================
# SOURCE STATUS
# ============================================================

def index_scanner_source_status(
    authenticated: bool,
    opportunities: List[
        UpstreamIndexOpportunity
    ],
    source_errors: Optional[List[str]] = None,
) -> IndexScannerStatus:

    if not authenticated:
        return IndexScannerStatus.BLOCKED

    if source_errors:
        return IndexScannerStatus.DEGRADED

    if not opportunities:
        return IndexScannerStatus.DEGRADED

    return IndexScannerStatus.READY
# ============================================================
# ROBOMLM_PLUS — INDEX DISCOVERY SCANNER
# PART 3 — STATE / EXECUTION FLOW / CONTROLLER
# ============================================================


# ============================================================
# SCANNER STATE
# ============================================================

@dataclass
class IndexScannerState:
    initialized: bool = False
    ready: bool = False
    authenticated: bool = False

    status: IndexScannerStatus = (
        IndexScannerStatus.IDLE
    )

    mode: IndexScannerMode = (
        IndexScannerMode.UNIVERSAL_INDICES
    )

    request_count: int = 0
    scan_count: int = 0

    last_error: str = ""
    last_scan_at: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def create_index_scanner_state(
    authenticated: bool = False,
    mode: IndexScannerMode = (
        IndexScannerMode.UNIVERSAL_INDICES
    ),
) -> IndexScannerState:

    return IndexScannerState(
        initialized=False,
        ready=False,
        authenticated=authenticated,
        status=(
            IndexScannerStatus.IDLE
            if authenticated
            else IndexScannerStatus.BLOCKED
        ),
        mode=mode,
    )


def normalize_index_scanner_state(
    value: Any,
) -> IndexScannerState:

    if isinstance(
        value,
        IndexScannerState,
    ):
        return value

    if not isinstance(value, dict):
        return create_index_scanner_state()

    return IndexScannerState(
        initialized=_index_bool(
            value.get("initialized"),
            False,
        ),
        ready=_index_bool(
            value.get("ready"),
            False,
        ),
        authenticated=_index_bool(
            value.get("authenticated"),
            False,
        ),
        status=_index_enum(
            value.get("status"),
            IndexScannerStatus,
            IndexScannerStatus.UNKNOWN,
        ),
        mode=_index_enum(
            value.get("mode"),
            IndexScannerMode,
            IndexScannerMode.UNKNOWN,
        ),
        request_count=int(
            _index_float(
                value.get("request_count"),
                0.0,
            )
        ),
        scan_count=int(
            _index_float(
                value.get("scan_count"),
                0.0,
            )
        ),
        last_error=_index_text(
            value.get("last_error")
        ),
        last_scan_at=_index_text(
            value.get("last_scan_at")
        ),
        metadata=dict(
            value.get("metadata") or {}
        ),
    )


# ============================================================
# MAIN SCAN FLOW
# ============================================================

def run_index_scanner(
    request: IndexScannerRequest,
) -> IndexScannerResult:

    request = normalize_index_request(request)

    scanner_filter = normalize_index_filter(
        request.scanner_filter
    )

    # --------------------------------------------------------
    # AUTHENTICATION GATE
    # --------------------------------------------------------

    if not request.authenticated:

        return build_index_scanner_result(
            mode=request.mode,
            input_opportunities=request.opportunities,
            filtered_opportunities=[],
            status=IndexScannerStatus.BLOCKED,
            source_available=False,
            warnings=[
                "Authenticated session required."
            ],
        )

    # --------------------------------------------------------
    # FILTER MARKET UNIVERSE
    # --------------------------------------------------------

    filtered_markets = filter_index_markets(
        request.markets,
        scanner_filter,
    )

    # --------------------------------------------------------
    # FILTER INDEX INSTRUMENT UNIVERSE
    # --------------------------------------------------------

    filtered_instruments = filter_index_instruments(
        request.instruments,
        scanner_filter,
    )

    # --------------------------------------------------------
    # FILTER UPSTREAM OPPORTUNITIES
    # --------------------------------------------------------

    filtered_opportunities = (
        filter_upstream_index_opportunities(
            request.opportunities,
            scanner_filter,
        )
    )

    warnings: List[str] = []

    # --------------------------------------------------------
    # EXPLICIT MARKET UNIVERSE
    # --------------------------------------------------------

    if request.markets:

        enabled_market_ids = {
            market.market_id
            for market in filtered_markets
            if market.enabled
        }

        filtered_opportunities = [
            opportunity
            for opportunity in filtered_opportunities
            if (
                not opportunity.market_id
                or opportunity.market_id
                in enabled_market_ids
            )
        ]

    else:

        warnings.append(
            "No explicit index market universe supplied; "
            "scanner is using upstream opportunity universe."
        )

    # --------------------------------------------------------
    # EXPLICIT INDEX UNIVERSE
    # --------------------------------------------------------

    if request.instruments:

        enabled_instrument_ids = {
            instrument.instrument_id
            for instrument in filtered_instruments
            if instrument.enabled
        }

        filtered_opportunities = [
            opportunity
            for opportunity in filtered_opportunities
            if (
                not opportunity.instrument_id
                or opportunity.instrument_id
                in enabled_instrument_ids
            )
        ]

    else:

        warnings.append(
            "No explicit index instrument universe supplied; "
            "scanner is using upstream opportunity universe."
        )

    # --------------------------------------------------------
    # SOURCE STATUS
    # --------------------------------------------------------

    status = index_scanner_source_status(
        authenticated=request.authenticated,
        opportunities=filtered_opportunities,
    )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    return build_index_scanner_result(
        mode=request.mode,
        input_opportunities=request.opportunities,
        filtered_opportunities=filtered_opportunities,
        status=status,
        source_available=bool(
            request.opportunities
        ),
        warnings=warnings,
    )


# ============================================================
# CONTROLLER
# ============================================================

class IndexScannerController:

    def __init__(
        self,
        authenticated: bool = False,
        mode: IndexScannerMode = (
            IndexScannerMode.UNIVERSAL_INDICES
        ),
    ) -> None:

        self._state = create_index_scanner_state(
            authenticated=authenticated,
            mode=mode,
        )

        self._last_request: Optional[
            IndexScannerRequest
        ] = None

        self._last_result: Optional[
            IndexScannerResult
        ] = None

        self._request_history: List[
            IndexScannerRequest
        ] = []

        self._result_history: List[
            IndexScannerResult
        ] = []

    # --------------------------------------------------------
    # PROPERTIES
    # --------------------------------------------------------

    @property
    def state(self) -> IndexScannerState:
        return self._state

    @property
    def status(self) -> IndexScannerStatus:
        return self._state.status

    @property
    def mode(self) -> IndexScannerMode:
        return self._state.mode

    @property
    def authenticated(self) -> bool:
        return self._state.authenticated

    @property
    def last_request(
        self,
    ) -> Optional[IndexScannerRequest]:
        return self._last_request

    @property
    def last_result(
        self,
    ) -> Optional[IndexScannerResult]:
        return self._last_result

    @property
    def request_history(
        self,
    ) -> List[IndexScannerRequest]:
        return list(self._request_history)

    @property
    def result_history(
        self,
    ) -> List[IndexScannerResult]:
        return list(self._result_history)

    # --------------------------------------------------------
    # INITIALIZE
    # --------------------------------------------------------

    def initialize(self) -> IndexScannerState:

        self._state.initialized = True

        if self._state.authenticated:
            self._state.status = (
                IndexScannerStatus.READY
            )
            self._state.ready = True
        else:
            self._state.status = (
                IndexScannerStatus.BLOCKED
            )
            self._state.ready = False

        return self._state

    # --------------------------------------------------------
    # SCAN
    # --------------------------------------------------------

    def scan(
        self,
        request: IndexScannerRequest,
    ) -> IndexScannerResult:

        normalized_request = normalize_index_request(
            request
        )

        self._state.request_count += 1

        self._last_request = normalized_request

        self._request_history.append(
            normalized_request
        )

        if len(self._request_history) > 500:
            self._request_history = (
                self._request_history[-500:]
            )

        self._state.status = (
            IndexScannerStatus.LOADING
        )

        result = run_index_scanner(
            normalized_request
        )

        self._last_result = result

        self._result_history.append(result)

        if len(self._result_history) > 500:
            self._result_history = (
                self._result_history[-500:]
            )

        self._state.scan_count += 1
        self._state.status = result.status
        self._state.ready = (
            result.status
            in {
                IndexScannerStatus.READY,
                IndexScannerStatus.DEGRADED,
            }
        )
        self._state.last_scan_at = (
            result.generated_at
        )

        if result.source_errors:
            self._state.last_error = (
                result.source_errors[-1]
            )
        else:
            self._state.last_error = ""

        return result

    # --------------------------------------------------------
    # MODE
    # --------------------------------------------------------

    def set_mode(
        self,
        mode: IndexScannerMode,
    ) -> IndexScannerState:

        normalized = _index_enum(
            mode,
            IndexScannerMode,
            IndexScannerMode.UNKNOWN,
        )

        self._state.mode = normalized

        return self._state

    # --------------------------------------------------------
    # AUTHENTICATION
    # --------------------------------------------------------

    def set_authenticated(
        self,
        authenticated: bool,
    ) -> IndexScannerState:

        self._state.authenticated = bool(
            authenticated
        )

        if not self._state.authenticated:

            self._state.ready = False
            self._state.status = (
                IndexScannerStatus.BLOCKED
            )

        elif self._state.initialized:

            self._state.ready = True
            self._state.status = (
                IndexScannerStatus.READY
            )

        return self._state

    # --------------------------------------------------------
    # BLOCK
    # --------------------------------------------------------

    def block(
        self,
        reason: str = "",
    ) -> IndexScannerState:

        self._state.ready = False

        self._state.status = (
            IndexScannerStatus.BLOCKED
        )

        self._state.last_error = _index_text(
            reason,
            "Index scanner blocked.",
        )

        return self._state

    # --------------------------------------------------------
    # RESET
    # --------------------------------------------------------

    def reset(self) -> IndexScannerState:

        authenticated = (
            self._state.authenticated
        )

        mode = self._state.mode

        self._state = create_index_scanner_state(
            authenticated=authenticated,
            mode=mode,
        )

        self._last_request = None
        self._last_result = None

        self._request_history.clear()
        self._result_history.clear()

        return self._state

    # --------------------------------------------------------
    # SNAPSHOT
    # --------------------------------------------------------

    def snapshot(
        self,
    ) -> "IndexScannerSnapshot":

        request = (
            self._last_request
            or IndexScannerRequest(
                authenticated=self.authenticated,
                mode=self.mode,
            )
        )

        result = (
            self._last_result
            or build_index_scanner_result(
                mode=self.mode,
                input_opportunities=[],
                filtered_opportunities=[],
                status=self.status,
                source_available=False,
            )
        )

        return IndexScannerSnapshot(
            request=request,
            result=result,
            captured_at=_index_now(),
            metadata={
                "scanner_snapshot": True,
                "upstream_truth_preserved": True,
                "index_scanner_independent": True,
                "equity_scanner_dependency": False,
            },
        )


# ============================================================
# DEFAULT CONTROLLER
# ============================================================

_DEFAULT_INDEX_SCANNER = IndexScannerController()


def get_index_scanner() -> IndexScannerController:
    return _DEFAULT_INDEX_SCANNER


def create_index_scanner(
    authenticated: bool = False,
    mode: IndexScannerMode = (
        IndexScannerMode.UNIVERSAL_INDICES
    ),
) -> IndexScannerController:

    return IndexScannerController(
        authenticated=authenticated,
        mode=mode,
    )


# ============================================================
# PUBLIC SCAN HELPERS
# ============================================================

def scan_index_market(
    opportunities: List[
        UpstreamIndexOpportunity
    ],
    authenticated: bool = True,
    mode: IndexScannerMode = (
        IndexScannerMode.UNIVERSAL_INDICES
    ),
    markets: Optional[
        List[IndexMarketInput]
    ] = None,
    instruments: Optional[
        List[IndexInstrumentInput]
    ] = None,
    scanner_filter: Optional[
        IndexScannerFilter
    ] = None,
) -> IndexScannerResult:

    request = IndexScannerRequest(
        mode=mode,
        markets=list(markets or []),
        instruments=list(instruments or []),
        opportunities=list(opportunities),
        scanner_filter=(
            scanner_filter
            or IndexScannerFilter()
        ),
        authenticated=authenticated,
    )

    return run_index_scanner(request)


def scan_with_index_scanner(
    request: IndexScannerRequest,
    scanner: Optional[
        IndexScannerController
    ] = None,
) -> IndexScannerResult:

    controller = (
        scanner
        or get_index_scanner()
    )

    if not controller.state.initialized:
        controller.initialize()

    return controller.scan(request)
# ============================================================
# ROBOMLM_PLUS — INDEX DISCOVERY SCANNER
# PART 4 — SERIALIZATION / VALIDATION / HEALTH
# ============================================================


# ============================================================
# SERIALIZATION
# ============================================================

def _serialize_index_value(
    value: Any,
) -> Any:

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, list):
        return [
            _serialize_index_value(item)
            for item in value
        ]

    if isinstance(value, tuple):
        return [
            _serialize_index_value(item)
            for item in value
        ]

    if isinstance(value, dict):
        return {
            str(key): _serialize_index_value(item)
            for key, item in value.items()
        }

    if hasattr(
        value,
        "__dataclass_fields__",
    ):
        return {
            key: _serialize_index_value(
                getattr(value, key)
            )
            for key in value.__dataclass_fields__
        }

    return value


def serialize_index_market(
    value: IndexMarketInput,
) -> Dict[str, Any]:

    return _serialize_index_value(value)


def serialize_index_instrument(
    value: IndexInstrumentInput,
) -> Dict[str, Any]:

    return _serialize_index_value(value)


def serialize_upstream_index_opportunity(
    value: UpstreamIndexOpportunity,
) -> Dict[str, Any]:

    return _serialize_index_value(value)


def serialize_index_filter(
    value: IndexScannerFilter,
) -> Dict[str, Any]:

    return _serialize_index_value(value)


def serialize_index_scanner_opportunity(
    value: IndexScannerOpportunity,
) -> Dict[str, Any]:

    return _serialize_index_value(value)


def serialize_index_scanner_result(
    value: IndexScannerResult,
) -> Dict[str, Any]:

    return _serialize_index_value(value)


def serialize_index_scanner_request(
    value: IndexScannerRequest,
) -> Dict[str, Any]:

    return _serialize_index_value(value)


def serialize_index_scanner_state(
    value: IndexScannerState,
) -> Dict[str, Any]:

    return _serialize_index_value(value)


def serialize_index_scanner_snapshot(
    value: IndexScannerSnapshot,
) -> Dict[str, Any]:

    return _serialize_index_value(value)


# ============================================================
# MARKET VALIDATION
# ============================================================

def validate_index_market(
    value: IndexMarketInput,
) -> bool:

    if not value.market_id:
        return False

    if not value.market_name:
        return False

    return True


# ============================================================
# INDEX INSTRUMENT VALIDATION
# ============================================================

def validate_index_instrument(
    value: IndexInstrumentInput,
) -> bool:

    if not value.instrument_id:
        return False

    if not value.symbol:
        return False

    if value.index_type == IndexType.UNKNOWN:
        return False

    return True


# ============================================================
# UPSTREAM OPPORTUNITY VALIDATION
# ============================================================

def validate_upstream_index_opportunity(
    value: UpstreamIndexOpportunity,
) -> bool:

    if not value.opportunity_id:
        return False

    if not value.symbol:
        return False

    if value.index_type == IndexType.UNKNOWN:
        return False

    if value.state == IndexOpportunityState.UNKNOWN:
        return False

    if value.bias == IndexOpportunityBias.UNKNOWN:
        return False

    if value.strength == IndexOpportunityStrength.UNKNOWN:
        return False

    if not 0.0 <= value.confidence <= 1.0:
        return False

    if value.source == IndexSourceType.UNKNOWN:
        return False

    return True


# ============================================================
# FILTER VALIDATION
# ============================================================

def validate_index_filter(
    value: IndexScannerFilter,
) -> bool:

    if not isinstance(
        value.market_ids,
        list,
    ):
        return False

    if not isinstance(
        value.countries,
        list,
    ):
        return False

    if not isinstance(
        value.regions,
        list,
    ):
        return False

    if not isinstance(
        value.exchange_names,
        list,
    ):
        return False

    if not isinstance(
        value.instrument_ids,
        list,
    ):
        return False

    if not isinstance(
        value.symbols,
        list,
    ):
        return False

    if not isinstance(
        value.categories,
        list,
    ):
        return False

    for item in value.index_types:

        if item == IndexType.UNKNOWN:
            return False

    for item in value.states:

        if item == IndexOpportunityState.UNKNOWN:
            return False

    for item in value.biases:

        if item == IndexOpportunityBias.UNKNOWN:
            return False

    for item in value.strengths:

        if item == IndexOpportunityStrength.UNKNOWN:
            return False

    return True


# ============================================================
# SCANNER OPPORTUNITY VALIDATION
# ============================================================

def validate_index_scanner_opportunity(
    value: IndexScannerOpportunity,
) -> bool:

    if not value.opportunity_id:
        return False

    if not value.symbol:
        return False

    if not value.instrument_id:
        return False

    if value.index_type == IndexType.UNKNOWN:
        return False

    if value.state == IndexOpportunityState.UNKNOWN:
        return False

    if value.bias == IndexOpportunityBias.UNKNOWN:
        return False

    if value.strength == IndexOpportunityStrength.UNKNOWN:
        return False

    if not 0.0 <= value.confidence <= 1.0:
        return False

    if value.source == IndexSourceType.UNKNOWN:
        return False

    metadata = value.metadata

    # --------------------------------------------------------
    # UPSTREAM TRUTH MUST BE PRESERVED
    # --------------------------------------------------------

    if metadata.get(
        "upstream_truth"
    ) is not True:
        return False

    forbidden_flags = (
        "scanner_generated_intelligence",
        "scanner_generated_score",
        "scanner_generated_decision",
        "index_algorithm_generated",
        "d13_modified",
        "risk_generated",
        "risk_overridden",
        "cas_bypassed",
        "execution_authority",
    )

    for flag in forbidden_flags:

        if metadata.get(flag) is True:
            return False

    return True


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_index_scanner_request(
    value: IndexScannerRequest,
) -> bool:

    if value.mode == IndexScannerMode.UNKNOWN:
        return False

    if not validate_index_filter(
        value.scanner_filter
    ):
        return False

    for market in value.markets:

        if not validate_index_market(
            market
        ):
            return False

    for instrument in value.instruments:

        if not validate_index_instrument(
            instrument
        ):
            return False

    for opportunity in value.opportunities:

        if not validate_upstream_index_opportunity(
            opportunity
        ):
            return False

    return True


# ============================================================
# RESULT VALIDATION
# ============================================================

def validate_index_scanner_result(
    value: IndexScannerResult,
) -> bool:

    if value.mode == IndexScannerMode.UNKNOWN:
        return False

    if value.status == IndexScannerStatus.UNKNOWN:
        return False

    if value.total_input_opportunities < 0:
        return False

    if value.total_output_opportunities < 0:
        return False

    if (
        value.total_output_opportunities
        != len(value.opportunities)
    ):
        return False

    if (
        value.total_output_opportunities
        > value.total_input_opportunities
    ):
        return False

    for opportunity in value.opportunities:

        if not validate_index_scanner_opportunity(
            opportunity
        ):
            return False

    metadata = value.metadata

    forbidden_result_flags = (
        "scanner_generated_intelligence",
        "scanner_generated_score",
        "scanner_generated_decision",
        "index_algorithm_generated",
        "d13_modified",
        "risk_generated",
        "risk_overridden",
        "cas_bypassed",
        "execution_authority",
    )

    for flag in forbidden_result_flags:

        if metadata.get(flag) is True:
            return False

    if metadata.get(
        "upstream_truth_preserved"
    ) is not True:
        return False

    return True


# ============================================================
# STATE VALIDATION
# ============================================================

def validate_index_scanner_state(
    value: IndexScannerState,
) -> bool:

    if value.status == IndexScannerStatus.UNKNOWN:
        return False

    if value.mode == IndexScannerMode.UNKNOWN:
        return False

    if value.request_count < 0:
        return False

    if value.scan_count < 0:
        return False

    if (
        value.status
        == IndexScannerStatus.READY
        and not value.ready
    ):
        return False

    if (
        value.status
        == IndexScannerStatus.BLOCKED
        and value.ready
    ):
        return False

    return True


# ============================================================
# SNAPSHOT VALIDATION
# ============================================================

def validate_index_scanner_snapshot(
    value: IndexScannerSnapshot,
) -> bool:

    if not validate_index_scanner_request(
        value.request
    ):
        return False

    if not validate_index_scanner_result(
        value.result
    ):
        return False

    if not value.captured_at:
        return False

    metadata = value.metadata

    if metadata.get(
        "upstream_truth_preserved"
    ) is not True:
        return False

    if metadata.get(
        "index_scanner_independent"
    ) is not True:
        return False

    if metadata.get(
        "equity_scanner_dependency"
    ) is True:
        return False

    return True


# ============================================================
# AUTHORITY VALIDATION
# ============================================================

def validate_index_scanner_authority(
    authority: Dict[str, Any],
) -> bool:

    required_forbidden = (
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

    for key in required_forbidden:

        if authority.get(key) is not False:
            return False

    # Index scanner itself must not become an equity dependency.
    if authority.get(
        "equity_scanner_dependency"
    ) is not False:
        return False

    return True


# ============================================================
# HEALTH CONTRACT
# ============================================================

@dataclass
class IndexScannerHealth:

    engine: str
    version: str

    status: IndexScannerStatus

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

    critical_scanner: bool = True

    index_scanner_independent: bool = True

    equity_scanner_dependency: bool = False

    # --------------------------------------------------------
    # FUTURE INDEX RESEARCH READINESS
    # --------------------------------------------------------

    index_structure_analysis: bool = False
    index_regime_analysis: bool = False
    index_participation_analysis: bool = False
    index_breakout_analysis: bool = False
    index_confirmation_analysis: bool = False
    index_exact_levels: bool = False


# ============================================================
# HEALTH BUILDER
# ============================================================

def build_index_scanner_health(
    scanner: Optional[
        IndexScannerController
    ] = None,
) -> IndexScannerHealth:

    controller = (
        scanner
        or get_index_scanner()
    )

    state_valid = (
        validate_index_scanner_state(
            controller.state
        )
    )

    authority_valid = (
        validate_index_scanner_authority(
            INDEX_SCANNER_AUTHORITY
        )
    )

    last_result_valid = True

    if controller.last_result is not None:

        last_result_valid = (
            validate_index_scanner_result(
                controller.last_result
            )
        )

    warnings: List[str] = []
    errors: List[str] = []

    if not controller.authenticated:

        warnings.append(
            "Authenticated session required."
        )

    if (
        controller.status
        == IndexScannerStatus.DEGRADED
    ):

        warnings.append(
            "Upstream index opportunity source "
            "is degraded."
        )

    if not state_valid:

        errors.append(
            "Index scanner state validation failed."
        )

    if not authority_valid:

        errors.append(
            "Index scanner authority validation failed."
        )

    if not last_result_valid:

        errors.append(
            "Last index scanner result validation failed."
        )

    return IndexScannerHealth(

        engine=INDEX_SCANNER_ENGINE,

        version=INDEX_SCANNER_VERSION,

        status=controller.status,

        initialized=controller.state.initialized,

        ready=controller.state.ready,

        authenticated=controller.authenticated,

        state_valid=state_valid,

        authority_valid=authority_valid,

        last_result_valid=last_result_valid,

        warnings=warnings,

        errors=errors,

        critical_scanner=True,

        index_scanner_independent=True,

        equity_scanner_dependency=False,

        # Future research remains upstream-owned.
        index_structure_analysis=False,
        index_regime_analysis=False,
        index_participation_analysis=False,
        index_breakout_analysis=False,
        index_confirmation_analysis=False,
        index_exact_levels=False,
    )


# ============================================================
# HEALTH SERIALIZATION
# ============================================================

def serialize_index_scanner_health(
    value: IndexScannerHealth,
) -> Dict[str, Any]:

    return _serialize_index_value(value)


# ============================================================
# OPERATIONAL CHECK
# ============================================================

def index_scanner_operational_check(
    scanner: Optional[
        IndexScannerController
    ] = None,
) -> Dict[str, Any]:

    health = build_index_scanner_health(
        scanner
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

        "critical_scanner": True,

        "index_scanner_independent": True,
        "equity_scanner_dependency": False,

        # ----------------------------------------------------
        # FUTURE RESEARCH FLAGS
        # ----------------------------------------------------

        "index_structure_analysis": False,
        "index_regime_analysis": False,
        "index_participation_analysis": False,
        "index_breakout_analysis": False,
        "index_confirmation_analysis": False,
        "index_exact_levels": False,

        "warnings": health.warnings,
        "errors": health.errors,
    }
# ============================================================
# ROBOMLM_PLUS — INDEX DISCOVERY SCANNER
# PART 5 — DIAGNOSTICS / CONTRACT / INTEGRITY / SELF-CHECK
# ============================================================


# ============================================================
# DIAGNOSTICS
# ============================================================

def diagnose_index_scanner(
    scanner: Optional[
        IndexScannerController
    ] = None,
) -> Dict[str, Any]:

    controller = (
        scanner
        or get_index_scanner()
    )

    health = build_index_scanner_health(
        controller
    )

    result = controller.last_result

    return {
        "engine": INDEX_SCANNER_ENGINE,
        "version": INDEX_SCANNER_VERSION,

        "status": controller.status.value,
        "mode": controller.mode.value,

        "initialized": controller.state.initialized,
        "ready": controller.state.ready,
        "authenticated": controller.authenticated,

        "request_count": (
            controller.state.request_count
        ),
        "scan_count": (
            controller.state.scan_count
        ),

        "last_scan_at": (
            controller.state.last_scan_at
        ),
        "last_error": (
            controller.state.last_error
        ),

        "health": serialize_index_scanner_health(
            health
        ),

        "last_result_available": (
            result is not None
        ),

        "last_result_count": (
            len(result.opportunities)
            if result is not None
            else 0
        ),

        "authority": dict(
            INDEX_SCANNER_AUTHORITY
        ),

        "research_boundary": {
            "index_structure_analysis": False,
            "index_regime_analysis": False,
            "index_participation_analysis": False,
            "index_breakout_analysis": False,
            "index_confirmation_analysis": False,
            "index_exact_levels": False,
            "formula_generation_in_scanner": False,
            "formula_owner": (
                "UPSTREAM_INDEX_INTELLIGENCE"
            ),
        },

        "independence": {
            "index_scanner_independent": True,
            "equity_scanner_dependency": False,
        },
    }


# ============================================================
# SUMMARY
# ============================================================

def index_scanner_summary(
    scanner: Optional[
        IndexScannerController
    ] = None,
) -> Dict[str, Any]:

    controller = (
        scanner
        or get_index_scanner()
    )

    result = controller.last_result

    qualified = 0
    developing = 0
    watch = 0
    bullish = 0
    bearish = 0

    if result is not None:

        for opportunity in result.opportunities:

            if (
                opportunity.state
                == IndexOpportunityState.QUALIFIED
            ):
                qualified += 1

            elif (
                opportunity.state
                == IndexOpportunityState.DEVELOPING
            ):
                developing += 1

            elif (
                opportunity.state
                == IndexOpportunityState.WATCH
            ):
                watch += 1

            if (
                opportunity.bias
                == IndexOpportunityBias.BULLISH
            ):
                bullish += 1

            elif (
                opportunity.bias
                == IndexOpportunityBias.BEARISH
            ):
                bearish += 1

    return {
        "engine": INDEX_SCANNER_ENGINE,
        "version": INDEX_SCANNER_VERSION,

        "status": controller.status.value,
        "mode": controller.mode.value,

        "initialized": controller.state.initialized,
        "ready": controller.state.ready,
        "authenticated": controller.authenticated,

        "critical_scanner": True,

        "index_scanner_independent": True,
        "equity_scanner_dependency": False,

        "total_opportunities": (
            len(result.opportunities)
            if result is not None
            else 0
        ),

        "qualified_opportunities": qualified,
        "developing_opportunities": developing,
        "watch_opportunities": watch,

        "bullish_opportunities": bullish,
        "bearish_opportunities": bearish,

        # ----------------------------------------------------
        # INTELLIGENCE IS NOT GENERATED HERE
        # ----------------------------------------------------

        "scanner_generates_intelligence": False,
        "scanner_generates_score": False,
        "scanner_generates_decision": False,

        "upstream_truth_preserved": True,
    }


# ============================================================
# CONTRACT MANIFEST
# ============================================================

def index_scanner_contract_manifest() -> Dict[str, Any]:

    return {

        "engine": INDEX_SCANNER_ENGINE,
        "version": INDEX_SCANNER_VERSION,
        "name": INDEX_SCANNER_NAME,
        "title": INDEX_SCANNER_TITLE,

        "layer": "UI_PRESENTATION",

        "role": "INDEX_OPPORTUNITY_SCANNER",

        "importance": "CLASS_A_DISCOVERY_COMPONENT",

        "critical_scanner": True,

        # ----------------------------------------------------
        # INPUTS
        # ----------------------------------------------------

        "inputs": [
            "USER_SERVICE_OUTPUT",
            "INDEX_MARKET_INPUT",
            "INDEX_INSTRUMENT_INPUT",
            "INDEX_SCANNER_FILTER",
            "UPSTREAM_INDEX_OPPORTUNITY_OUTPUT",
            "WATCHLIST_OUTPUT",
            "FAVORITES_OUTPUT",
            "APPLICATION_SESSION_STATE",
        ],

        # ----------------------------------------------------
        # PROCESSING
        # ----------------------------------------------------

        "processing": [
            "SOURCE_NORMALIZATION",
            "INDEX_MARKET_FILTERING",
            "INDEX_REGION_FILTERING",
            "INDEX_EXCHANGE_FILTERING",
            "INDEX_INSTRUMENT_FILTERING",
            "INDEX_CATEGORY_FILTERING",
            "OPPORTUNITY_STATE_FILTERING",
            "OPPORTUNITY_BIAS_FILTERING",
            "OPPORTUNITY_STRENGTH_FILTERING",
            "FAVORITE_FILTERING",
            "WATCHLIST_FILTERING",
            "UPSTREAM_OPPORTUNITY_ROUTING",
            "RESULT_BUILDING",
            "SERIALIZATION",
            "VALIDATION",
            "HEALTH",
            "DIAGNOSTICS",
        ],

        # ----------------------------------------------------
        # OUTPUTS
        # ----------------------------------------------------

        "outputs": [
            "INDEX_SCANNER_RESULT",
            "INDEX_SCANNER_SNAPSHOT",
            "INDEX_SCANNER_STATE",
            "INDEX_SCANNER_HEALTH",
            "INDEX_SCANNER_DIAGNOSTICS",
        ],

        # ----------------------------------------------------
        # TRUTH POLICY
        # ----------------------------------------------------

        "truth_policy": {
            "upstream_truth_preserved": True,
            "scanner_generated_intelligence": False,
            "scanner_generated_score": False,
            "scanner_generated_decision": False,
            "index_algorithm_generated": False,
            "d13_modified": False,
            "risk_generated": False,
            "risk_overridden": False,
            "cas_bypassed": False,
            "execution_authority": False,
        },

        # ----------------------------------------------------
        # INTELLIGENCE OWNERSHIP
        # ----------------------------------------------------

        "intelligence_authority": {
            "owner": "UPSTREAM_INDEX_INTELLIGENCE",

            "index_structure": (
                "UPSTREAM_INDEX_INTELLIGENCE"
            ),

            "index_regime": (
                "UPSTREAM_INDEX_INTELLIGENCE"
            ),

            "index_participation": (
                "UPSTREAM_INDEX_INTELLIGENCE"
            ),

            "index_breakout": (
                "UPSTREAM_INDEX_INTELLIGENCE"
            ),

            "index_confirmation": (
                "UPSTREAM_INDEX_INTELLIGENCE"
            ),

            "index_exact_levels": (
                "UPSTREAM_INDEX_INTELLIGENCE"
            ),

            "formula_generation_in_scanner": False,
        },

        # ----------------------------------------------------
        # INDEPENDENCE
        # ----------------------------------------------------

        "independence_policy": {
            "index_scanner_independent": True,
            "equity_scanner_dependency": False,
            "equity_scanner_requires_index": False,
            "index_signal_required_for_equity": False,
        },

        # ----------------------------------------------------
        # FORBIDDEN
        # ----------------------------------------------------

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
            "ORDER_AUTHORITY",
            "ORDER_MUTATION",
            "POSITION_AUTHORITY",
            "POSITION_MUTATION",
            "PORTFOLIO_MUTATION",
            "OPPORTUNITY_GENERATION",
            "SCANNER_INTELLIGENCE_GENERATION",
            "UPSTREAM_MUTATION",
        ],
    }


# ============================================================
# INTEGRITY VALIDATION
# ============================================================

def validate_index_scanner_integrity(
    scanner: Optional[
        IndexScannerController
    ] = None,
) -> Dict[str, Any]:

    controller = (
        scanner
        or get_index_scanner()
    )

    state_valid = (
        validate_index_scanner_state(
            controller.state
        )
    )

    authority_valid = (
        validate_index_scanner_authority(
            INDEX_SCANNER_AUTHORITY
        )
    )

    result_valid = True

    if controller.last_result is not None:

        result_valid = (
            validate_index_scanner_result(
                controller.last_result
            )
        )

    contract_valid = (
        validate_index_scanner_contract()
    )

    return {

        "engine": INDEX_SCANNER_ENGINE,
        "version": INDEX_SCANNER_VERSION,

        "state_valid": state_valid,
        "authority_valid": authority_valid,
        "result_valid": result_valid,
        "contract_valid": contract_valid,

        "index_scanner_independent": True,
        "equity_scanner_dependency": False,

        "integrity_valid": (
            state_valid
            and authority_valid
            and result_valid
            and contract_valid
        ),
    }


# ============================================================
# CONTRACT VALIDATION
# ============================================================

def validate_index_scanner_contract() -> bool:

    manifest = (
        index_scanner_contract_manifest()
    )

    if manifest.get("layer") != "UI_PRESENTATION":
        return False

    if manifest.get("role") != (
        "INDEX_OPPORTUNITY_SCANNER"
    ):
        return False

    if manifest.get(
        "critical_scanner"
    ) is not True:
        return False

    truth_policy = manifest.get(
        "truth_policy",
        {},
    )

    if truth_policy.get(
        "upstream_truth_preserved"
    ) is not True:
        return False

    forbidden_truth_flags = (
        "scanner_generated_intelligence",
        "scanner_generated_score",
        "scanner_generated_decision",
        "index_algorithm_generated",
        "d13_modified",
        "risk_generated",
        "risk_overridden",
        "cas_bypassed",
        "execution_authority",
    )

    for flag in forbidden_truth_flags:

        if truth_policy.get(flag) is True:
            return False

    independence = manifest.get(
        "independence_policy",
        {},
    )

    if independence.get(
        "index_scanner_independent"
    ) is not True:
        return False

    if independence.get(
        "equity_scanner_dependency"
    ) is not False:
        return False

    if independence.get(
        "equity_scanner_requires_index"
    ) is not False:
        return False

    if independence.get(
        "index_signal_required_for_equity"
    ) is not False:
        return False

    intelligence = manifest.get(
        "intelligence_authority",
        {},
    )

    if intelligence.get(
        "formula_generation_in_scanner"
    ) is not False:
        return False

    return True


# ============================================================
# MODULE CHECK
# ============================================================

def index_scanner_module_check(
    scanner: Optional[
        IndexScannerController
    ] = None,
) -> Dict[str, Any]:

    integrity = validate_index_scanner_integrity(
        scanner
    )

    return {
        "module": INDEX_SCANNER_NAME,
        "engine": INDEX_SCANNER_ENGINE,
        "version": INDEX_SCANNER_VERSION,

        "passed": integrity[
            "integrity_valid"
        ],

        "checks": integrity,
    }


# ============================================================
# SELF CHECK
# ============================================================

def index_scanner_self_check() -> Dict[str, Any]:

    sample = UpstreamIndexOpportunity(

        opportunity_id="INDEX_SELF_CHECK_001",

        symbol="TEST_INDEX",

        instrument_id="INDEX_TEST",

        instrument_name="Test Index",

        index_type=IndexType.BROAD_MARKET,

        market_id="TEST_MARKET",

        country="TEST",

        region="TEST",

        exchange="TEST_EXCHANGE",

        currency="TEST",

        category="BROAD_MARKET",

        state=IndexOpportunityState.QUALIFIED,

        bias=IndexOpportunityBias.BULLISH,

        strength=IndexOpportunityStrength.STRONG,

        summary=(
            "Upstream index intelligence self-check."
        ),

        confidence=0.90,

        timestamp=_index_now(),

        source=(
            IndexSourceType
            .UPSTREAM_OPPORTUNITY_ENGINE
        ),

        metadata={
            "research_source":
                "UPSTREAM_INDEX_INTELLIGENCE",

            "structure_analysis": True,

            "scanner_generated_intelligence":
                False,
        },
    )

    converted = (
        convert_upstream_index_opportunity(
            sample
        )
    )

    result = build_index_scanner_result(
        mode=IndexScannerMode.INDEX,
        input_opportunities=[sample],
        filtered_opportunities=[sample],
        status=IndexScannerStatus.READY,
        source_available=True,
    )

    conversion_valid = (
        converted.symbol == sample.symbol
        and converted.bias == sample.bias
        and converted.strength == sample.strength
        and converted.state == sample.state
        and converted.confidence == sample.confidence
        and converted.metadata.get(
            "upstream_truth"
        ) is True
    )

    result_valid = (
        validate_index_scanner_result(
            result
        )
    )

    authority_valid = (
        validate_index_scanner_authority(
            INDEX_SCANNER_AUTHORITY
        )
    )

    contract_valid = (
        validate_index_scanner_contract()
    )

    return {

        "engine": INDEX_SCANNER_ENGINE,

        "passed": (
            conversion_valid
            and result_valid
            and authority_valid
            and contract_valid
        ),

        "checks": {

            "upstream_truth_preserved":
                conversion_valid,

            "result_valid":
                result_valid,

            "authority_valid":
                authority_valid,

            "contract_valid":
                contract_valid,

            "index_scanner_independent":
                True,

            "equity_scanner_dependency":
                False,

            # No invented research formula.
            "research_formula_generated":
                False,
        },
    }


# ============================================================
# DEFAULT FACTORY
# ============================================================

def create_default_index_scanner(
    authenticated: bool = False,
) -> IndexScannerController:

    scanner = create_index_scanner(
        authenticated=authenticated,
        mode=(
            IndexScannerMode
            .UNIVERSAL_INDICES
        ),
    )

    scanner.initialize()

    return scanner


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [

    # --------------------------------------------------------
    # IDENTITY
    # --------------------------------------------------------

    "INDEX_SCANNER_ENGINE",
    "INDEX_SCANNER_VERSION",
    "INDEX_SCANNER_NAME",
    "INDEX_SCANNER_TITLE",
    "INDEX_SCANNER_DESCRIPTION",

    "INDEX_SCANNER_AUTHORITY",

    # --------------------------------------------------------
    # ENUMS
    # --------------------------------------------------------

    "IndexScannerStatus",
    "IndexScannerMode",
    "IndexType",
    "IndexOpportunityState",
    "IndexOpportunityBias",
    "IndexOpportunityStrength",
    "IndexScannerPriority",
    "IndexSourceType",

    # --------------------------------------------------------
    # SCHEMAS
    # --------------------------------------------------------

    "IndexMarketInput",
    "IndexInstrumentInput",
    "UpstreamIndexOpportunity",
    "IndexScannerFilter",
    "IndexScannerOpportunity",
    "IndexScannerResult",
    "IndexScannerRequest",
    "IndexScannerSnapshot",

    "IndexScannerState",
    "IndexScannerHealth",

    # --------------------------------------------------------
    # NORMALIZATION
    # --------------------------------------------------------

    "normalize_index_market",
    "normalize_index_instrument",
    "normalize_upstream_index_opportunity",
    "normalize_index_filter",
    "normalize_index_request",

    # --------------------------------------------------------
    # FILTERING
    # --------------------------------------------------------

    "index_opportunity_matches_filter",
    "filter_upstream_index_opportunities",
    "filter_index_markets",
    "filter_index_instruments",

    # --------------------------------------------------------
    # RESULT / SOURCE
    # --------------------------------------------------------

    "convert_upstream_index_opportunity",
    "build_index_scanner_result",
    "index_scanner_source_status",

    # --------------------------------------------------------
    # STATE / CONTROLLER
    # --------------------------------------------------------

    "create_index_scanner_state",
    "normalize_index_scanner_state",
    "run_index_scanner",

    "IndexScannerController",

    "get_index_scanner",
    "create_index_scanner",

    "scan_index_market",
    "scan_with_index_scanner",

    # --------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------

    "serialize_index_market",
    "serialize_index_instrument",
    "serialize_upstream_index_opportunity",
    "serialize_index_filter",
    "serialize_index_scanner_opportunity",
    "serialize_index_scanner_result",
    "serialize_index_scanner_request",
    "serialize_index_scanner_state",
    "serialize_index_scanner_snapshot",

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    "validate_index_market",
    "validate_index_instrument",
    "validate_upstream_index_opportunity",
    "validate_index_filter",
    "validate_index_scanner_opportunity",
    "validate_index_scanner_request",
    "validate_index_scanner_result",
    "validate_index_scanner_state",
    "validate_index_scanner_snapshot",
    "validate_index_scanner_authority",

    # --------------------------------------------------------
    # HEALTH
    # --------------------------------------------------------

    "build_index_scanner_health",
    "serialize_index_scanner_health",
    "index_scanner_operational_check",

    # --------------------------------------------------------
    # DIAGNOSTICS / CONTRACT
    # --------------------------------------------------------

    "diagnose_index_scanner",
    "index_scanner_summary",
    "index_scanner_contract_manifest",
    "validate_index_scanner_integrity",
    "validate_index_scanner_contract",
    "index_scanner_module_check",

    # --------------------------------------------------------
    # SELF CHECK / FACTORY
    # --------------------------------------------------------

    "index_scanner_self_check",
    "create_default_index_scanner",
]
