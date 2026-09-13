# ============================================================
# ROBOMLM_PLUS — COMMODITY DISCOVERY SCANNER
# PART 1 — CORE CONTRACT / AUTHORITY / SCHEMAS
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List


COMMODITY_SCANNER_ENGINE = "ROBOMLM_PLUS_COMMODITY_SCANNER"
COMMODITY_SCANNER_VERSION = "1.0"
COMMODITY_SCANNER_NAME = "Commodity Opportunity Scanner"
COMMODITY_SCANNER_TITLE = "Commodity Market Opportunity Scanner"
COMMODITY_SCANNER_DESCRIPTION = (
    "Dedicated commodity discovery scanner for presenting and routing "
    "upstream commodity opportunity intelligence across supported "
    "markets, contracts and commodity groups."
)


# ============================================================
# AUTHORITY BOUNDARY
# ============================================================

COMMODITY_SCANNER_AUTHORITY = {
    # Allowed presentation / routing responsibilities
    "scanner_orchestration": True,
    "commodity_opportunity_presentation": True,
    "market_filtering": True,
    "region_filtering": True,
    "exchange_filtering": True,
    "commodity_filtering": True,
    "contract_filtering": True,
    "instrument_filtering": True,
    "category_filtering": True,
    "upstream_opportunity_consumption": True,
    "commodity_specific_intelligence_consumption": True,

    # Commodity intelligence belongs upstream.
    "commodity_specific_algorithm_generation": False,
    "commodity_signal_generation": False,
    "commodity_score_generation": False,

    # Cross-scanner dependency must not become intelligence authority.
    "equity_scanner_dependency": False,
    "equity_scanner_authority": False,
    "index_scanner_dependency": False,
    "index_scanner_authority": False,

    # Core intelligence / decision authority
    "market_data_generation": False,
    "evidence_generation": False,
    "intelligence_generation": False,
    "decision_generation": False,
    "d13_modification": False,

    # Risk / CAS authority
    "risk_generation": False,
    "risk_override": False,
    "cas_generation": False,
    "cas_bypass": False,

    # Execution authority
    "execution": False,
    "order_authority": False,
    "order_mutation": False,
    "position_authority": False,
    "position_mutation": False,
    "portfolio_mutation": False,

    # Opportunity / scanner intelligence generation
    "opportunity_generation": False,
    "scanner_intelligence_generation": False,

    # Upstream mutation
    "upstream_mutation": False,
}


# ============================================================
# STATUS / MODE
# ============================================================

class CommodityScannerStatus(str, Enum):
    IDLE = "IDLE"
    LOADING = "LOADING"
    READY = "READY"
    DEGRADED = "DEGRADED"
    BLOCKED = "BLOCKED"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class CommodityScannerMode(str, Enum):
    UNIVERSAL_COMMODITIES = "UNIVERSAL_COMMODITIES"
    MARKET = "MARKET"
    REGION = "REGION"
    EXCHANGE = "EXCHANGE"
    COMMODITY = "COMMODITY"
    CONTRACT = "CONTRACT"
    CATEGORY = "CATEGORY"
    FAVORITES = "FAVORITES"
    WATCHLIST = "WATCHLIST"
    UNKNOWN = "UNKNOWN"


# ============================================================
# COMMODITY DOMAIN TYPES
# ============================================================

class CommodityType(str, Enum):
    ENERGY = "ENERGY"
    METAL = "METAL"
    PRECIOUS_METAL = "PRECIOUS_METAL"
    BASE_METAL = "BASE_METAL"
    AGRICULTURE = "AGRICULTURE"
    LIVESTOCK = "LIVESTOCK"
    SOFT_COMMODITY = "SOFT_COMMODITY"
    OTHER_COMMODITY = "OTHER_COMMODITY"
    UNKNOWN = "UNKNOWN"


class CommodityContractType(str, Enum):
    SPOT = "SPOT"
    FUTURE = "FUTURE"
    FORWARD = "FORWARD"
    CFD = "CFD"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


class CommodityOpportunityState(str, Enum):
    UNKNOWN = "UNKNOWN"
    WATCH = "WATCH"
    DEVELOPING = "DEVELOPING"
    QUALIFIED = "QUALIFIED"
    INVALIDATED = "INVALIDATED"
    EXPIRED = "EXPIRED"


class CommodityOpportunityBias(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"


class CommodityOpportunityStrength(str, Enum):
    VERY_WEAK = "VERY_WEAK"
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    VERY_STRONG = "VERY_STRONG"
    UNKNOWN = "UNKNOWN"


class CommodityScannerPriority(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CommoditySourceType(str, Enum):
    UPSTREAM_OPPORTUNITY_ENGINE = "UPSTREAM_OPPORTUNITY_ENGINE"
    COMMODITY_OPPORTUNITY_ENGINE = "COMMODITY_OPPORTUNITY_ENGINE"
    DISCOVERY_ENGINE = "DISCOVERY_ENGINE"
    UNKNOWN = "UNKNOWN"


# ============================================================
# NORMALIZATION HELPERS
# ============================================================

def _commodity_text(value: Any, default: str = "") -> str:
    if value is None:
        return default

    text = str(value).strip()
    return text if text else default


def _commodity_bool(value: Any, default: bool = False) -> bool:
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


def _commodity_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _commodity_enum(
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


def _commodity_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ============================================================
# MARKET INPUT
# ============================================================

@dataclass
class CommodityMarketInput:
    market_id: str
    market_name: str

    country: str = ""
    region: str = ""
    exchange: str = ""
    currency: str = ""
    timezone: str = ""

    enabled: bool = True
    selected: bool = False
    commodity_available: bool = True

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# COMMODITY / CONTRACT INPUT
# ============================================================

@dataclass
class CommodityInstrumentInput:
    instrument_id: str
    symbol: str

    display_name: str = ""

    commodity_type: CommodityType = CommodityType.UNKNOWN
    contract_type: CommodityContractType = CommodityContractType.UNKNOWN

    market_id: str = ""
    country: str = ""
    region: str = ""
    exchange: str = ""
    currency: str = ""

    commodity_group: str = ""
    category: str = ""

    expiry: str = ""
    contract_month: str = ""

    enabled: bool = True
    selected: bool = False
    tradable: bool = True

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# UPSTREAM COMMODITY OPPORTUNITY
# ============================================================

@dataclass
class UpstreamCommodityOpportunity:
    opportunity_id: str
    symbol: str

    instrument_id: str = ""
    instrument_name: str = ""

    commodity_type: CommodityType = CommodityType.UNKNOWN
    contract_type: CommodityContractType = CommodityContractType.UNKNOWN

    market_id: str = ""
    country: str = ""
    region: str = ""
    exchange: str = ""
    currency: str = ""

    commodity_group: str = ""
    category: str = ""

    expiry: str = ""
    contract_month: str = ""

    state: CommodityOpportunityState = CommodityOpportunityState.UNKNOWN
    bias: CommodityOpportunityBias = CommodityOpportunityBias.UNKNOWN
    strength: CommodityOpportunityStrength = (
        CommodityOpportunityStrength.UNKNOWN
    )

    summary: str = ""
    confidence: float = 0.0
    timestamp: str = ""

    favorite: bool = False
    watchlisted: bool = False

    priority: CommodityScannerPriority = CommodityScannerPriority.NORMAL
    source: CommoditySourceType = (
        CommoditySourceType.UPSTREAM_OPPORTUNITY_ENGINE
    )

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# SCANNER FILTER
# ============================================================

@dataclass
class CommodityScannerFilter:
    market_ids: List[str] = field(default_factory=list)

    countries: List[str] = field(default_factory=list)
    regions: List[str] = field(default_factory=list)
    exchange_names: List[str] = field(default_factory=list)

    instrument_ids: List[str] = field(default_factory=list)
    symbols: List[str] = field(default_factory=list)

    commodity_types: List[CommodityType] = field(default_factory=list)
    contract_types: List[CommodityContractType] = field(
        default_factory=list
    )

    commodity_groups: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)

    states: List[CommodityOpportunityState] = field(
        default_factory=list
    )
    biases: List[CommodityOpportunityBias] = field(
        default_factory=list
    )
    strengths: List[CommodityOpportunityStrength] = field(
        default_factory=list
    )

    favorites_only: bool = False
    watchlist_only: bool = False
    tradable_only: bool = True

    include_invalidated: bool = False
    include_expired: bool = False

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# SCANNER OUTPUT OPPORTUNITY
# ============================================================

@dataclass
class CommodityScannerOpportunity:
    opportunity_id: str
    symbol: str

    instrument_id: str
    instrument_name: str

    commodity_type: CommodityType
    contract_type: CommodityContractType

    market_id: str
    country: str
    region: str
    exchange: str
    currency: str

    commodity_group: str
    category: str

    expiry: str
    contract_month: str

    state: CommodityOpportunityState
    bias: CommodityOpportunityBias
    strength: CommodityOpportunityStrength

    summary: str
    confidence: float
    timestamp: str

    favorite: bool
    watchlisted: bool

    priority: CommodityScannerPriority
    source: CommoditySourceType

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# SCANNER RESULT
# ============================================================

@dataclass
class CommodityScannerResult:
    status: CommodityScannerStatus
    mode: CommodityScannerMode

    opportunities: List[CommodityScannerOpportunity] = field(
        default_factory=list
    )

    total_input_opportunities: int = 0
    total_output_opportunities: int = 0

    source_available: bool = False
    source_errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    generated_at: str = ""

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# SCANNER REQUEST
# ============================================================

@dataclass
class CommodityScannerRequest:
    mode: CommodityScannerMode = (
        CommodityScannerMode.UNIVERSAL_COMMODITIES
    )

    markets: List[CommodityMarketInput] = field(
        default_factory=list
    )

    instruments: List[CommodityInstrumentInput] = field(
        default_factory=list
    )

    opportunities: List[UpstreamCommodityOpportunity] = field(
        default_factory=list
    )

    scanner_filter: CommodityScannerFilter = field(
        default_factory=CommodityScannerFilter
    )

    authenticated: bool = False

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# SNAPSHOT
# ============================================================

@dataclass
class CommodityScannerSnapshot:
    request: CommodityScannerRequest
    result: CommodityScannerResult

    captured_at: str

    metadata: Dict[str, Any] = field(default_factory=dict)
# ============================================================
# ROBOMLM_PLUS — COMMODITY DISCOVERY SCANNER
# PART 2 — NORMALIZATION / FILTERING / UPSTREAM TRUTH ROUTING
# ============================================================


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_commodity_market(
    value: Any,
) -> CommodityMarketInput:
    if isinstance(value, CommodityMarketInput):
        return value

    if not isinstance(value, dict):
        value = {}

    return CommodityMarketInput(
        market_id=_commodity_text(value.get("market_id")),
        market_name=_commodity_text(value.get("market_name")),
        country=_commodity_text(value.get("country")),
        region=_commodity_text(value.get("region")),
        exchange=_commodity_text(value.get("exchange")),
        currency=_commodity_text(value.get("currency")),
        timezone=_commodity_text(value.get("timezone")),
        enabled=_commodity_bool(value.get("enabled"), True),
        selected=_commodity_bool(value.get("selected"), False),
        commodity_available=_commodity_bool(
            value.get("commodity_available"),
            True,
        ),
        metadata=dict(value.get("metadata") or {}),
    )


def normalize_commodity_instrument(
    value: Any,
) -> CommodityInstrumentInput:
    if isinstance(value, CommodityInstrumentInput):
        return value

    if not isinstance(value, dict):
        value = {}

    return CommodityInstrumentInput(
        instrument_id=_commodity_text(value.get("instrument_id")),
        symbol=_commodity_text(value.get("symbol")),
        display_name=_commodity_text(value.get("display_name")),
        commodity_type=_commodity_enum(
            value.get("commodity_type"),
            CommodityType,
            CommodityType.UNKNOWN,
        ),
        contract_type=_commodity_enum(
            value.get("contract_type"),
            CommodityContractType,
            CommodityContractType.UNKNOWN,
        ),
        market_id=_commodity_text(value.get("market_id")),
        country=_commodity_text(value.get("country")),
        region=_commodity_text(value.get("region")),
        exchange=_commodity_text(value.get("exchange")),
        currency=_commodity_text(value.get("currency")),
        commodity_group=_commodity_text(
            value.get("commodity_group")
        ),
        category=_commodity_text(value.get("category")),
        expiry=_commodity_text(value.get("expiry")),
        contract_month=_commodity_text(
            value.get("contract_month")
        ),
        enabled=_commodity_bool(value.get("enabled"), True),
        selected=_commodity_bool(value.get("selected"), False),
        tradable=_commodity_bool(value.get("tradable"), True),
        metadata=dict(value.get("metadata") or {}),
    )


def normalize_upstream_commodity_opportunity(
    value: Any,
) -> UpstreamCommodityOpportunity:
    if isinstance(value, UpstreamCommodityOpportunity):
        return value

    if not isinstance(value, dict):
        value = {}

    return UpstreamCommodityOpportunity(
        opportunity_id=_commodity_text(
            value.get("opportunity_id")
        ),
        symbol=_commodity_text(value.get("symbol")),
        instrument_id=_commodity_text(
            value.get("instrument_id")
        ),
        instrument_name=_commodity_text(
            value.get("instrument_name")
        ),
        commodity_type=_commodity_enum(
            value.get("commodity_type"),
            CommodityType,
            CommodityType.UNKNOWN,
        ),
        contract_type=_commodity_enum(
            value.get("contract_type"),
            CommodityContractType,
            CommodityContractType.UNKNOWN,
        ),
        market_id=_commodity_text(value.get("market_id")),
        country=_commodity_text(value.get("country")),
        region=_commodity_text(value.get("region")),
        exchange=_commodity_text(value.get("exchange")),
        currency=_commodity_text(value.get("currency")),
        commodity_group=_commodity_text(
            value.get("commodity_group")
        ),
        category=_commodity_text(value.get("category")),
        expiry=_commodity_text(value.get("expiry")),
        contract_month=_commodity_text(
            value.get("contract_month")
        ),
        state=_commodity_enum(
            value.get("state"),
            CommodityOpportunityState,
            CommodityOpportunityState.UNKNOWN,
        ),
        bias=_commodity_enum(
            value.get("bias"),
            CommodityOpportunityBias,
            CommodityOpportunityBias.UNKNOWN,
        ),
        strength=_commodity_enum(
            value.get("strength"),
            CommodityOpportunityStrength,
            CommodityOpportunityStrength.UNKNOWN,
        ),
        summary=_commodity_text(value.get("summary")),
        confidence=_commodity_float(
            value.get("confidence"),
            0.0,
        ),
        timestamp=_commodity_text(
            value.get("timestamp")
        ),
        favorite=_commodity_bool(
            value.get("favorite"),
            False,
        ),
        watchlisted=_commodity_bool(
            value.get("watchlisted"),
            False,
        ),
        priority=_commodity_enum(
            value.get("priority"),
            CommodityScannerPriority,
            CommodityScannerPriority.NORMAL,
        ),
        source=_commodity_enum(
            value.get("source"),
            CommoditySourceType,
            CommoditySourceType.UPSTREAM_OPPORTUNITY_ENGINE,
        ),
        metadata=dict(value.get("metadata") or {}),
    )


def _normalize_commodity_string_list(
    values: Any,
) -> List[str]:
    if values is None:
        return []

    if isinstance(values, str):
        values = [values]

    if not isinstance(values, (list, tuple, set)):
        return []

    result: List[str] = []

    for value in values:
        text = _commodity_text(value)
        if text:
            result.append(text)

    return result


def _normalize_commodity_enum_list(
    values: Any,
    enum_type: Any,
) -> List[Any]:
    if values is None:
        return []

    if not isinstance(values, (list, tuple, set)):
        values = [values]

    result: List[Any] = []

    for value in values:
        item = _commodity_enum(
            value,
            enum_type,
            None,
        )
        if item is not None:
            result.append(item)

    return result


def normalize_commodity_filter(
    value: Any,
) -> CommodityScannerFilter:
    if isinstance(value, CommodityScannerFilter):
        return value

    if not isinstance(value, dict):
        value = {}

    return CommodityScannerFilter(
        market_ids=_normalize_commodity_string_list(
            value.get("market_ids")
        ),
        countries=_normalize_commodity_string_list(
            value.get("countries")
        ),
        regions=_normalize_commodity_string_list(
            value.get("regions")
        ),
        exchange_names=_normalize_commodity_string_list(
            value.get("exchange_names")
        ),
        instrument_ids=_normalize_commodity_string_list(
            value.get("instrument_ids")
        ),
        symbols=_normalize_commodity_string_list(
            value.get("symbols")
        ),
        commodity_types=_normalize_commodity_enum_list(
            value.get("commodity_types"),
            CommodityType,
        ),
        contract_types=_normalize_commodity_enum_list(
            value.get("contract_types"),
            CommodityContractType,
        ),
        commodity_groups=_normalize_commodity_string_list(
            value.get("commodity_groups")
        ),
        categories=_normalize_commodity_string_list(
            value.get("categories")
        ),
        states=_normalize_commodity_enum_list(
            value.get("states"),
            CommodityOpportunityState,
        ),
        biases=_normalize_commodity_enum_list(
            value.get("biases"),
            CommodityOpportunityBias,
        ),
        strengths=_normalize_commodity_enum_list(
            value.get("strengths"),
            CommodityOpportunityStrength,
        ),
        favorites_only=_commodity_bool(
            value.get("favorites_only"),
            False,
        ),
        watchlist_only=_commodity_bool(
            value.get("watchlist_only"),
            False,
        ),
        tradable_only=_commodity_bool(
            value.get("tradable_only"),
            True,
        ),
        include_invalidated=_commodity_bool(
            value.get("include_invalidated"),
            False,
        ),
        include_expired=_commodity_bool(
            value.get("include_expired"),
            False,
        ),
        metadata=dict(value.get("metadata") or {}),
    )


def normalize_commodity_request(
    value: Any,
) -> CommodityScannerRequest:
    if isinstance(value, CommodityScannerRequest):
        return value

    if not isinstance(value, dict):
        value = {}

    markets = [
        normalize_commodity_market(item)
        for item in value.get("markets", [])
    ]

    instruments = [
        normalize_commodity_instrument(item)
        for item in value.get("instruments", [])
    ]

    opportunities = [
        normalize_upstream_commodity_opportunity(item)
        for item in value.get("opportunities", [])
    ]

    return CommodityScannerRequest(
        mode=_commodity_enum(
            value.get("mode"),
            CommodityScannerMode,
            CommodityScannerMode.UNIVERSAL_COMMODITIES,
        ),
        markets=markets,
        instruments=instruments,
        opportunities=opportunities,
        scanner_filter=normalize_commodity_filter(
            value.get("scanner_filter")
        ),
        authenticated=_commodity_bool(
            value.get("authenticated"),
            False,
        ),
        metadata=dict(value.get("metadata") or {}),
    )


# ============================================================
# MATCHING HELPERS
# ============================================================

def _commodity_matches_list(
    value: str,
    allowed: List[str],
) -> bool:
    if not allowed:
        return True

    normalized_value = value.strip().lower()

    return any(
        normalized_value == item.strip().lower()
        for item in allowed
    )


def _commodity_matches_enum_list(
    value: Any,
    allowed: List[Any],
) -> bool:
    if not allowed:
        return True

    return value in allowed


# ============================================================
# OPPORTUNITY FILTER
# ============================================================

def commodity_opportunity_matches_filter(
    opportunity: UpstreamCommodityOpportunity,
    scanner_filter: CommodityScannerFilter,
) -> bool:

    if scanner_filter.market_ids and not _commodity_matches_list(
        opportunity.market_id,
        scanner_filter.market_ids,
    ):
        return False

    if scanner_filter.countries and not _commodity_matches_list(
        opportunity.country,
        scanner_filter.countries,
    ):
        return False

    if scanner_filter.regions and not _commodity_matches_list(
        opportunity.region,
        scanner_filter.regions,
    ):
        return False

    if scanner_filter.exchange_names and not _commodity_matches_list(
        opportunity.exchange,
        scanner_filter.exchange_names,
    ):
        return False

    if scanner_filter.instrument_ids and not _commodity_matches_list(
        opportunity.instrument_id,
        scanner_filter.instrument_ids,
    ):
        return False

    if scanner_filter.symbols and not _commodity_matches_list(
        opportunity.symbol,
        scanner_filter.symbols,
    ):
        return False

    if not _commodity_matches_enum_list(
        opportunity.commodity_type,
        scanner_filter.commodity_types,
    ):
        return False

    if not _commodity_matches_enum_list(
        opportunity.contract_type,
        scanner_filter.contract_types,
    ):
        return False

    if scanner_filter.commodity_groups and not _commodity_matches_list(
        opportunity.commodity_group,
        scanner_filter.commodity_groups,
    ):
        return False

    if scanner_filter.categories and not _commodity_matches_list(
        opportunity.category,
        scanner_filter.categories,
    ):
        return False

    if not _commodity_matches_enum_list(
        opportunity.state,
        scanner_filter.states,
    ):
        return False

    if not _commodity_matches_enum_list(
        opportunity.bias,
        scanner_filter.biases,
    ):
        return False

    if not _commodity_matches_enum_list(
        opportunity.strength,
        scanner_filter.strengths,
    ):
        return False

    if scanner_filter.favorites_only and not opportunity.favorite:
        return False

    if scanner_filter.watchlist_only and not opportunity.watchlisted:
        return False

    if (
        not scanner_filter.include_invalidated
        and opportunity.state
        == CommodityOpportunityState.INVALIDATED
    ):
        return False

    if (
        not scanner_filter.include_expired
        and opportunity.state
        == CommodityOpportunityState.EXPIRED
    ):
        return False

    return True


def filter_upstream_commodity_opportunities(
    opportunities: List[UpstreamCommodityOpportunity],
    scanner_filter: CommodityScannerFilter,
) -> List[UpstreamCommodityOpportunity]:

    return [
        opportunity
        for opportunity in opportunities
        if commodity_opportunity_matches_filter(
            opportunity,
            scanner_filter,
        )
    ]


# ============================================================
# MARKET FILTER
# ============================================================

def filter_commodity_markets(
    markets: List[CommodityMarketInput],
    scanner_filter: CommodityScannerFilter,
) -> List[CommodityMarketInput]:

    result: List[CommodityMarketInput] = []

    for market in markets:
        if not market.enabled:
            continue

        if not market.commodity_available:
            continue

        if scanner_filter.market_ids and not _commodity_matches_list(
            market.market_id,
            scanner_filter.market_ids,
        ):
            continue

        if scanner_filter.countries and not _commodity_matches_list(
            market.country,
            scanner_filter.countries,
        ):
            continue

        if scanner_filter.regions and not _commodity_matches_list(
            market.region,
            scanner_filter.regions,
        ):
            continue

        if scanner_filter.exchange_names and not _commodity_matches_list(
            market.exchange,
            scanner_filter.exchange_names,
        ):
            continue

        result.append(market)

    return result


# ============================================================
# INSTRUMENT FILTER
# ============================================================

def filter_commodity_instruments(
    instruments: List[CommodityInstrumentInput],
    scanner_filter: CommodityScannerFilter,
) -> List[CommodityInstrumentInput]:

    result: List[CommodityInstrumentInput] = []

    for instrument in instruments:

        if not instrument.enabled:
            continue

        if scanner_filter.market_ids and not _commodity_matches_list(
            instrument.market_id,
            scanner_filter.market_ids,
        ):
            continue

        if scanner_filter.countries and not _commodity_matches_list(
            instrument.country,
            scanner_filter.countries,
        ):
            continue

        if scanner_filter.regions and not _commodity_matches_list(
            instrument.region,
            scanner_filter.regions,
        ):
            continue

        if scanner_filter.exchange_names and not _commodity_matches_list(
            instrument.exchange,
            scanner_filter.exchange_names,
        ):
            continue

        if scanner_filter.instrument_ids and not _commodity_matches_list(
            instrument.instrument_id,
            scanner_filter.instrument_ids,
        ):
            continue

        if scanner_filter.symbols and not _commodity_matches_list(
            instrument.symbol,
            scanner_filter.symbols,
        ):
            continue

        if not _commodity_matches_enum_list(
            instrument.commodity_type,
            scanner_filter.commodity_types,
        ):
            continue

        if not _commodity_matches_enum_list(
            instrument.contract_type,
            scanner_filter.contract_types,
        ):
            continue

        if scanner_filter.commodity_groups and not _commodity_matches_list(
            instrument.commodity_group,
            scanner_filter.commodity_groups,
        ):
            continue

        if scanner_filter.categories and not _commodity_matches_list(
            instrument.category,
            scanner_filter.categories,
        ):
            continue

        if (
            scanner_filter.tradable_only
            and not instrument.tradable
        ):
            continue

        result.append(instrument)

    return result


# ============================================================
# UPSTREAM TRUTH CONVERSION
# ============================================================

def convert_upstream_commodity_opportunity(
    opportunity: UpstreamCommodityOpportunity,
) -> CommodityScannerOpportunity:

    metadata = dict(opportunity.metadata or {})

    # Explicit truth / authority contract.
    metadata.update(
        {
            "upstream_truth": True,
            "scanner_generated_intelligence": False,
            "scanner_generated_score": False,
            "scanner_generated_decision": False,
            "commodity_algorithm_generated": False,
            "d13_modified": False,
            "risk_generated": False,
            "risk_overridden": False,
            "cas_bypassed": False,
            "execution_authority": False,
        }
    )

    return CommodityScannerOpportunity(
        opportunity_id=opportunity.opportunity_id,
        symbol=opportunity.symbol,
        instrument_id=opportunity.instrument_id,
        instrument_name=opportunity.instrument_name,
        commodity_type=opportunity.commodity_type,
        contract_type=opportunity.contract_type,
        market_id=opportunity.market_id,
        country=opportunity.country,
        region=opportunity.region,
        exchange=opportunity.exchange,
        currency=opportunity.currency,
        commodity_group=opportunity.commodity_group,
        category=opportunity.category,
        expiry=opportunity.expiry,
        contract_month=opportunity.contract_month,
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
# RESULT BUILDING
# ============================================================

def build_commodity_scanner_result(
    mode: CommodityScannerMode,
    opportunities: List[UpstreamCommodityOpportunity],
    source_available: bool = True,
    source_errors: List[str] | None = None,
    warnings: List[str] | None = None,
) -> CommodityScannerResult:

    source_errors = list(source_errors or [])
    warnings = list(warnings or [])

    output = [
        convert_upstream_commodity_opportunity(
            opportunity
        )
        for opportunity in opportunities
    ]

    return CommodityScannerResult(
        status=(
            CommodityScannerStatus.READY
            if source_available and opportunities
            else CommodityScannerStatus.DEGRADED
        ),
        mode=mode,
        opportunities=output,
        total_input_opportunities=len(opportunities),
        total_output_opportunities=len(output),
        source_available=source_available,
        source_errors=source_errors,
        warnings=warnings,
        generated_at=_commodity_now(),
        metadata={
            "upstream_truth_preserved": True,
            "commodity_scanner_independent": True,
            "commodity_algorithm_generated": False,
            "scanner_generated_intelligence": False,
            "scanner_generated_score": False,
            "scanner_generated_decision": False,
            "equity_scanner_dependency": False,
            "index_scanner_dependency": False,
            "d13_modified": False,
            "risk_generated": False,
            "risk_overridden": False,
            "cas_bypassed": False,
            "execution_authority": False,
        },
    )


# ============================================================
# SOURCE STATUS
# ============================================================

def commodity_scanner_source_status(
    authenticated: bool,
    opportunities: List[UpstreamCommodityOpportunity],
    source_errors: List[str] | None = None,
) -> CommodityScannerStatus:

    if not authenticated:
        return CommodityScannerStatus.BLOCKED

    if source_errors:
        return CommodityScannerStatus.DEGRADED

    if not opportunities:
        return CommodityScannerStatus.DEGRADED

    return CommodityScannerStatus.READY
# ============================================================
# ROBOMLM_PLUS — COMMODITY DISCOVERY SCANNER
# PART 3 — STATE / EXECUTION / CONTROLLER / SNAPSHOT
# ============================================================


# ============================================================
# SCANNER STATE
# ============================================================

@dataclass
class CommodityScannerState:
    initialized: bool = False
    ready: bool = False
    authenticated: bool = False

    status: CommodityScannerStatus = (
        CommodityScannerStatus.IDLE
    )

    mode: CommodityScannerMode = (
        CommodityScannerMode.UNIVERSAL_COMMODITIES
    )

    request_count: int = 0
    scan_count: int = 0

    last_error: str = ""
    last_scan_at: str = ""

    metadata: Dict[str, Any] = field(default_factory=dict)


def create_commodity_scanner_state(
    authenticated: bool = False,
) -> CommodityScannerState:

    return CommodityScannerState(
        initialized=False,
        ready=False,
        authenticated=authenticated,
        status=(
            CommodityScannerStatus.IDLE
            if authenticated
            else CommodityScannerStatus.BLOCKED
        ),
        mode=CommodityScannerMode.UNIVERSAL_COMMODITIES,
    )


def normalize_commodity_scanner_state(
    value: Any,
) -> CommodityScannerState:

    if isinstance(value, CommodityScannerState):
        return value

    if not isinstance(value, dict):
        value = {}

    return CommodityScannerState(
        initialized=_commodity_bool(
            value.get("initialized"),
            False,
        ),
        ready=_commodity_bool(
            value.get("ready"),
            False,
        ),
        authenticated=_commodity_bool(
            value.get("authenticated"),
            False,
        ),
        status=_commodity_enum(
            value.get("status"),
            CommodityScannerStatus,
            CommodityScannerStatus.UNKNOWN,
        ),
        mode=_commodity_enum(
            value.get("mode"),
            CommodityScannerMode,
            CommodityScannerMode.UNIVERSAL_COMMODITIES,
        ),
        request_count=int(
            _commodity_float(
                value.get("request_count"),
                0,
            )
        ),
        scan_count=int(
            _commodity_float(
                value.get("scan_count"),
                0,
            )
        ),
        last_error=_commodity_text(
            value.get("last_error")
        ),
        last_scan_at=_commodity_text(
            value.get("last_scan_at")
        ),
        metadata=dict(value.get("metadata") or {}),
    )


# ============================================================
# SCANNER EXECUTION
# ============================================================

def run_commodity_scanner(
    request: CommodityScannerRequest | Dict[str, Any],
) -> CommodityScannerResult:

    request = normalize_commodity_request(request)

    if not request.authenticated:
        return CommodityScannerResult(
            status=CommodityScannerStatus.BLOCKED,
            mode=request.mode,
            opportunities=[],
            total_input_opportunities=len(
                request.opportunities
            ),
            total_output_opportunities=0,
            source_available=False,
            source_errors=[
                "Commodity scanner requires authenticated session."
            ],
            warnings=[],
            generated_at=_commodity_now(),
            metadata={
                "upstream_truth_preserved": True,
                "commodity_scanner_independent": True,
                "commodity_algorithm_generated": False,
                "scanner_generated_intelligence": False,
                "scanner_generated_score": False,
                "scanner_generated_decision": False,
                "equity_scanner_dependency": False,
                "index_scanner_dependency": False,
                "d13_modified": False,
                "risk_generated": False,
                "risk_overridden": False,
                "cas_bypassed": False,
                "execution_authority": False,
            },
        )

    scanner_filter = request.scanner_filter

    markets = filter_commodity_markets(
        request.markets,
        scanner_filter,
    )

    instruments = filter_commodity_instruments(
        request.instruments,
        scanner_filter,
    )

    opportunities = filter_upstream_commodity_opportunities(
        request.opportunities,
        scanner_filter,
    )

    warnings: List[str] = []

    # Explicit market universe, when supplied,
    # restricts opportunities to enabled filtered markets.
    if request.markets:
        enabled_market_ids = {
            market.market_id
            for market in markets
            if market.market_id
        }

        if enabled_market_ids:
            opportunities = [
                opportunity
                for opportunity in opportunities
                if opportunity.market_id
                in enabled_market_ids
            ]
        else:
            warnings.append(
                "No enabled commodity markets matched "
                "the supplied market universe."
            )

    # Explicit instrument universe, when supplied,
    # restricts opportunities to enabled filtered instruments.
    if request.instruments:
        enabled_instrument_ids = {
            instrument.instrument_id
            for instrument in instruments
            if instrument.instrument_id
        }

        if enabled_instrument_ids:
            opportunities = [
                opportunity
                for opportunity in opportunities
                if opportunity.instrument_id
                in enabled_instrument_ids
            ]
        else:
            warnings.append(
                "No enabled commodity instruments matched "
                "the supplied instrument universe."
            )

    if not request.markets:
        warnings.append(
            "No explicit commodity market universe supplied; "
            "scanner is consuming the provided upstream opportunity set."
        )

    if not request.instruments:
        warnings.append(
            "No explicit commodity instrument universe supplied; "
            "scanner is consuming the provided upstream opportunity set."
        )

    source_errors: List[str] = []

    status = commodity_scanner_source_status(
        authenticated=request.authenticated,
        opportunities=opportunities,
        source_errors=source_errors,
    )

    result = build_commodity_scanner_result(
        mode=request.mode,
        opportunities=opportunities,
        source_available=bool(
            request.opportunities
        ),
        source_errors=source_errors,
        warnings=warnings,
    )

    # Preserve the actual source-status decision.
    result.status = status

    result.metadata.update(
        {
            "request_mode": request.mode.value,
            "filtered_market_count": len(markets),
            "filtered_instrument_count": len(instruments),
            "upstream_opportunity_count": len(
                request.opportunities
            ),
            "filtered_opportunity_count": len(
                opportunities
            ),
            "upstream_truth_preserved": True,
            "commodity_scanner_independent": True,
            "commodity_algorithm_generated": False,
            "scanner_generated_intelligence": False,
            "scanner_generated_score": False,
            "scanner_generated_decision": False,
            "equity_scanner_dependency": False,
            "index_scanner_dependency": False,
            "d13_modified": False,
            "risk_generated": False,
            "risk_overridden": False,
            "cas_bypassed": False,
            "execution_authority": False,
        }
    )

    return result


# ============================================================
# CONTROLLER
# ============================================================

class CommodityScannerController:
    def __init__(
        self,
        authenticated: bool = False,
    ) -> None:

        self._state = create_commodity_scanner_state(
            authenticated=authenticated
        )

        self._last_request: CommodityScannerRequest | None = None
        self._last_result: CommodityScannerResult | None = None

        self._request_history: List[
            CommodityScannerRequest
        ] = []

        self._result_history: List[
            CommodityScannerResult
        ] = []

    # --------------------------------------------------------
    # Properties
    # --------------------------------------------------------

    @property
    def state(self) -> CommodityScannerState:
        return self._state

    @property
    def status(self) -> CommodityScannerStatus:
        return self._state.status

    @property
    def mode(self) -> CommodityScannerMode:
        return self._state.mode

    @property
    def authenticated(self) -> bool:
        return self._state.authenticated

    @property
    def last_request(
        self,
    ) -> CommodityScannerRequest | None:
        return self._last_request

    @property
    def last_result(
        self,
    ) -> CommodityScannerResult | None:
        return self._last_result

    # --------------------------------------------------------
    # Lifecycle
    # --------------------------------------------------------

    def initialize(self) -> CommodityScannerState:

        self._state.initialized = True

        if self._state.authenticated:
            self._state.status = (
                CommodityScannerStatus.READY
            )
            self._state.ready = True
        else:
            self._state.status = (
                CommodityScannerStatus.BLOCKED
            )
            self._state.ready = False

        return self._state

    # --------------------------------------------------------
    # Scan
    # --------------------------------------------------------

    def scan(
        self,
        request: CommodityScannerRequest | Dict[str, Any],
    ) -> CommodityScannerResult:

        normalized_request = normalize_commodity_request(
            request
        )

        normalized_request.authenticated = (
            self._state.authenticated
            and normalized_request.authenticated
        )

        self._state.request_count += 1

        self._last_request = normalized_request

        self._request_history.append(
            normalized_request
        )

        if len(self._request_history) > 500:
            self._request_history.pop(0)

        self._state.mode = normalized_request.mode
        self._state.status = (
            CommodityScannerStatus.LOADING
        )

        try:
            result = run_commodity_scanner(
                normalized_request
            )

            self._last_result = result

            self._result_history.append(result)

            if len(self._result_history) > 500:
                self._result_history.pop(0)

            self._state.scan_count += 1
            self._state.status = result.status
            self._state.ready = (
                result.status
                == CommodityScannerStatus.READY
            )
            self._state.last_error = ""
            self._state.last_scan_at = (
                result.generated_at
            )

            return result

        except Exception as exc:

            self._state.status = (
                CommodityScannerStatus.ERROR
            )
            self._state.ready = False
            self._state.last_error = str(exc)
            self._state.last_scan_at = _commodity_now()

            error_result = CommodityScannerResult(
                status=CommodityScannerStatus.ERROR,
                mode=normalized_request.mode,
                opportunities=[],
                total_input_opportunities=len(
                    normalized_request.opportunities
                ),
                total_output_opportunities=0,
                source_available=False,
                source_errors=[str(exc)],
                warnings=[],
                generated_at=_commodity_now(),
                metadata={
                    "upstream_truth_preserved": True,
                    "commodity_scanner_independent": True,
                    "commodity_algorithm_generated": False,
                    "scanner_generated_intelligence": False,
                    "scanner_generated_score": False,
                    "scanner_generated_decision": False,
                    "equity_scanner_dependency": False,
                    "index_scanner_dependency": False,
                    "d13_modified": False,
                    "risk_generated": False,
                    "risk_overridden": False,
                    "cas_bypassed": False,
                    "execution_authority": False,
                },
            )

            self._last_result = error_result
            self._result_history.append(error_result)

            if len(self._result_history) > 500:
                self._result_history.pop(0)

            return error_result

    # --------------------------------------------------------
    # Mode
    # --------------------------------------------------------

    def set_mode(
        self,
        mode: CommodityScannerMode | str,
    ) -> CommodityScannerMode:

        self._state.mode = _commodity_enum(
            mode,
            CommodityScannerMode,
            CommodityScannerMode.UNIVERSAL_COMMODITIES,
        )

        return self._state.mode

    # --------------------------------------------------------
    # Authentication
    # --------------------------------------------------------

    def set_authenticated(
        self,
        authenticated: bool,
    ) -> CommodityScannerState:

        self._state.authenticated = bool(authenticated)

        if not self._state.authenticated:
            self._state.ready = False
            self._state.status = (
                CommodityScannerStatus.BLOCKED
            )
        elif self._state.initialized:
            self._state.ready = True
            self._state.status = (
                CommodityScannerStatus.READY
            )

        return self._state

    # --------------------------------------------------------
    # Block / Reset
    # --------------------------------------------------------

    def block(self) -> CommodityScannerState:

        self._state.ready = False
        self._state.status = (
            CommodityScannerStatus.BLOCKED
        )

        return self._state

    def reset(self) -> CommodityScannerState:

        authenticated = self._state.authenticated

        self._state = create_commodity_scanner_state(
            authenticated=authenticated
        )

        self._last_request = None
        self._last_result = None

        self._request_history.clear()
        self._result_history.clear()

        return self._state

    # --------------------------------------------------------
    # Snapshot
    # --------------------------------------------------------

    def snapshot(self) -> CommodityScannerSnapshot:

        request = (
            self._last_request
            if self._last_request is not None
            else CommodityScannerRequest(
                mode=self._state.mode,
                authenticated=self._state.authenticated,
            )
        )

        result = (
            self._last_result
            if self._last_result is not None
            else CommodityScannerResult(
                status=self._state.status,
                mode=self._state.mode,
                generated_at=_commodity_now(),
                metadata={
                    "upstream_truth_preserved": True,
                    "commodity_scanner_independent": True,
                },
            )
        )

        return CommodityScannerSnapshot(
            request=request,
            result=result,
            captured_at=_commodity_now(),
            metadata={
                "scanner_snapshot": True,
                "upstream_truth_preserved": True,
                "commodity_scanner_independent": True,
                "commodity_algorithm_generated": False,
                "scanner_generated_intelligence": False,
                "scanner_generated_score": False,
                "scanner_generated_decision": False,
                "equity_scanner_dependency": False,
                "index_scanner_dependency": False,
            },
        )

    # --------------------------------------------------------
    # History
    # --------------------------------------------------------

    def request_history(
        self,
    ) -> List[CommodityScannerRequest]:

        return list(self._request_history)

    def result_history(
        self,
    ) -> List[CommodityScannerResult]:

        return list(self._result_history)


# ============================================================
# DEFAULT CONTROLLER
# ============================================================

_DEFAULT_COMMODITY_SCANNER = CommodityScannerController()


def get_commodity_scanner() -> CommodityScannerController:
    return _DEFAULT_COMMODITY_SCANNER


def create_commodity_scanner(
    authenticated: bool = False,
) -> CommodityScannerController:

    return CommodityScannerController(
        authenticated=authenticated
    )


# ============================================================
# PUBLIC SCAN HELPERS
# ============================================================

def scan_commodity_market(
    opportunities: List[
        UpstreamCommodityOpportunity
    ],
    authenticated: bool = True,
    scanner_filter: CommodityScannerFilter | None = None,
    mode: CommodityScannerMode = (
        CommodityScannerMode.UNIVERSAL_COMMODITIES
    ),
    markets: List[CommodityMarketInput] | None = None,
    instruments: List[CommodityInstrumentInput] | None = None,
) -> CommodityScannerResult:

    request = CommodityScannerRequest(
        mode=mode,
        markets=list(markets or []),
        instruments=list(instruments or []),
        opportunities=list(opportunities or []),
        scanner_filter=(
            scanner_filter
            if scanner_filter is not None
            else CommodityScannerFilter()
        ),
        authenticated=authenticated,
    )

    return run_commodity_scanner(request)


def scan_with_commodity_scanner(
    request: CommodityScannerRequest | Dict[str, Any],
) -> CommodityScannerResult:

    return get_commodity_scanner().scan(request)
# ============================================================
# ROBOMLM_PLUS — COMMODITY DISCOVERY SCANNER
# PART 4 — SERIALIZATION / VALIDATION / HEALTH
# ============================================================


# ============================================================
# RECURSIVE SERIALIZATION
# ============================================================

def _serialize_commodity_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            str(key): _serialize_commodity_value(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [
            _serialize_commodity_value(item)
            for item in value
        ]

    if hasattr(value, "__dataclass_fields__"):
        return {
            key: _serialize_commodity_value(
                getattr(value, key)
            )
            for key in value.__dataclass_fields__
        }

    return value


# ============================================================
# SERIALIZERS
# ============================================================

def serialize_commodity_market(
    value: CommodityMarketInput,
) -> Dict[str, Any]:
    return _serialize_commodity_value(value)


def serialize_commodity_instrument(
    value: CommodityInstrumentInput,
) -> Dict[str, Any]:
    return _serialize_commodity_value(value)


def serialize_upstream_commodity_opportunity(
    value: UpstreamCommodityOpportunity,
) -> Dict[str, Any]:
    return _serialize_commodity_value(value)


def serialize_commodity_filter(
    value: CommodityScannerFilter,
) -> Dict[str, Any]:
    return _serialize_commodity_value(value)


def serialize_commodity_scanner_opportunity(
    value: CommodityScannerOpportunity,
) -> Dict[str, Any]:
    return _serialize_commodity_value(value)


def serialize_commodity_scanner_result(
    value: CommodityScannerResult,
) -> Dict[str, Any]:
    return _serialize_commodity_value(value)


def serialize_commodity_scanner_request(
    value: CommodityScannerRequest,
) -> Dict[str, Any]:
    return _serialize_commodity_value(value)


def serialize_commodity_scanner_snapshot(
    value: CommodityScannerSnapshot,
) -> Dict[str, Any]:
    return _serialize_commodity_value(value)


def serialize_commodity_scanner_state(
    value: CommodityScannerState,
) -> Dict[str, Any]:
    return _serialize_commodity_value(value)


def serialize_commodity_scanner_authority() -> Dict[str, bool]:
    return dict(COMMODITY_SCANNER_AUTHORITY)


# ============================================================
# VALIDATION HELPERS
# ============================================================

def validate_commodity_market(
    value: CommodityMarketInput,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(value, CommodityMarketInput):
        return ["Invalid CommodityMarketInput type."]

    if not value.market_id:
        errors.append("market_id is required.")

    if not value.market_name:
        errors.append("market_name is required.")

    if not value.enabled:
        return errors

    if value.commodity_available is not True:
        errors.append(
            "Enabled market must declare commodity_available=True."
        )

    return errors


def validate_commodity_instrument(
    value: CommodityInstrumentInput,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(value, CommodityInstrumentInput):
        return ["Invalid CommodityInstrumentInput type."]

    if not value.instrument_id:
        errors.append("instrument_id is required.")

    if not value.symbol:
        errors.append("symbol is required.")

    if not isinstance(
        value.commodity_type,
        CommodityType,
    ):
        errors.append("Invalid commodity_type.")

    if not isinstance(
        value.contract_type,
        CommodityContractType,
    ):
        errors.append("Invalid contract_type.")

    if value.enabled and value.tradable:
        if not value.exchange:
            errors.append(
                "Tradable commodity instrument requires exchange."
            )

    return errors


def validate_upstream_commodity_opportunity(
    value: UpstreamCommodityOpportunity,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        value,
        UpstreamCommodityOpportunity,
    ):
        return [
            "Invalid UpstreamCommodityOpportunity type."
        ]

    if not value.opportunity_id:
        errors.append("opportunity_id is required.")

    if not value.symbol:
        errors.append("symbol is required.")

    if not isinstance(
        value.commodity_type,
        CommodityType,
    ):
        errors.append("Invalid commodity_type.")

    if not isinstance(
        value.contract_type,
        CommodityContractType,
    ):
        errors.append("Invalid contract_type.")

    if not isinstance(
        value.state,
        CommodityOpportunityState,
    ):
        errors.append("Invalid opportunity state.")

    if not isinstance(
        value.bias,
        CommodityOpportunityBias,
    ):
        errors.append("Invalid opportunity bias.")

    if not isinstance(
        value.strength,
        CommodityOpportunityStrength,
    ):
        errors.append("Invalid opportunity strength.")

    if not isinstance(
        value.priority,
        CommodityScannerPriority,
    ):
        errors.append("Invalid scanner priority.")

    if not isinstance(
        value.source,
        CommoditySourceType,
    ):
        errors.append("Invalid source type.")

    if not 0.0 <= value.confidence <= 1.0:
        errors.append(
            "confidence must be between 0.0 and 1.0."
        )

    return errors


def validate_commodity_filter(
    value: CommodityScannerFilter,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        value,
        CommodityScannerFilter,
    ):
        return ["Invalid CommodityScannerFilter type."]

    for item in value.commodity_types:
        if not isinstance(item, CommodityType):
            errors.append(
                "Invalid commodity_types member."
            )

    for item in value.contract_types:
        if not isinstance(
            item,
            CommodityContractType,
        ):
            errors.append(
                "Invalid contract_types member."
            )

    for item in value.states:
        if not isinstance(
            item,
            CommodityOpportunityState,
        ):
            errors.append(
                "Invalid states member."
            )

    for item in value.biases:
        if not isinstance(
            item,
            CommodityOpportunityBias,
        ):
            errors.append(
                "Invalid biases member."
            )

    for item in value.strengths:
        if not isinstance(
            item,
            CommodityOpportunityStrength,
        ):
            errors.append(
                "Invalid strengths member."
            )

    return errors


def validate_commodity_scanner_opportunity(
    value: CommodityScannerOpportunity,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        value,
        CommodityScannerOpportunity,
    ):
        return [
            "Invalid CommodityScannerOpportunity type."
        ]

    if not value.opportunity_id:
        errors.append("opportunity_id is required.")

    if not value.symbol:
        errors.append("symbol is required.")

    if not isinstance(
        value.commodity_type,
        CommodityType,
    ):
        errors.append("Invalid commodity_type.")

    if not isinstance(
        value.contract_type,
        CommodityContractType,
    ):
        errors.append("Invalid contract_type.")

    if not isinstance(
        value.state,
        CommodityOpportunityState,
    ):
        errors.append("Invalid state.")

    if not isinstance(
        value.bias,
        CommodityOpportunityBias,
    ):
        errors.append("Invalid bias.")

    if not isinstance(
        value.strength,
        CommodityOpportunityStrength,
    ):
        errors.append("Invalid strength.")

    if not 0.0 <= value.confidence <= 1.0:
        errors.append(
            "confidence must be between 0.0 and 1.0."
        )

    metadata = value.metadata or {}

    required_truth_flags = {
        "upstream_truth": True,
        "scanner_generated_intelligence": False,
        "scanner_generated_score": False,
        "scanner_generated_decision": False,
        "commodity_algorithm_generated": False,
        "d13_modified": False,
        "risk_generated": False,
        "risk_overridden": False,
        "cas_bypassed": False,
        "execution_authority": False,
    }

    for key, expected in required_truth_flags.items():
        if metadata.get(key) is not expected:
            errors.append(
                f"metadata[{key!r}] must be {expected!r}."
            )

    return errors


def validate_commodity_scanner_request(
    value: CommodityScannerRequest,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        value,
        CommodityScannerRequest,
    ):
        return ["Invalid CommodityScannerRequest type."]

    if not isinstance(
        value.mode,
        CommodityScannerMode,
    ):
        errors.append("Invalid scanner mode.")

    errors.extend(
        error
        for market in value.markets
        for error in validate_commodity_market(market)
    )

    errors.extend(
        error
        for instrument in value.instruments
        for error in validate_commodity_instrument(
            instrument
        )
    )

    errors.extend(
        error
        for opportunity in value.opportunities
        for error in validate_upstream_commodity_opportunity(
            opportunity
        )
    )

    errors.extend(
        validate_commodity_filter(
            value.scanner_filter
        )
    )

    return errors


def validate_commodity_scanner_result(
    value: CommodityScannerResult,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        value,
        CommodityScannerResult,
    ):
        return ["Invalid CommodityScannerResult type."]

    if not isinstance(
        value.status,
        CommodityScannerStatus,
    ):
        errors.append("Invalid scanner status.")

    if not isinstance(
        value.mode,
        CommodityScannerMode,
    ):
        errors.append("Invalid scanner mode.")

    if value.total_input_opportunities < 0:
        errors.append(
            "total_input_opportunities cannot be negative."
        )

    if value.total_output_opportunities < 0:
        errors.append(
            "total_output_opportunities cannot be negative."
        )

    if (
        value.total_output_opportunities
        != len(value.opportunities)
    ):
        errors.append(
            "total_output_opportunities does not match "
            "opportunity list length."
        )

    for opportunity in value.opportunities:
        errors.extend(
            validate_commodity_scanner_opportunity(
                opportunity
            )
        )

    metadata = value.metadata or {}

    required_flags = {
        "upstream_truth_preserved": True,
        "commodity_scanner_independent": True,
        "commodity_algorithm_generated": False,
        "scanner_generated_intelligence": False,
        "scanner_generated_score": False,
        "scanner_generated_decision": False,
        "equity_scanner_dependency": False,
        "index_scanner_dependency": False,
        "d13_modified": False,
        "risk_generated": False,
        "risk_overridden": False,
        "cas_bypassed": False,
        "execution_authority": False,
    }

    for key, expected in required_flags.items():
        if metadata.get(key) is not expected:
            errors.append(
                f"result metadata[{key!r}] must be {expected!r}."
            )

    return errors


def validate_commodity_scanner_state(
    value: CommodityScannerState,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        value,
        CommodityScannerState,
    ):
        return ["Invalid CommodityScannerState type."]

    if not isinstance(
        value.status,
        CommodityScannerStatus,
    ):
        errors.append("Invalid state status.")

    if not isinstance(
        value.mode,
        CommodityScannerMode,
    ):
        errors.append("Invalid state mode.")

    if value.request_count < 0:
        errors.append(
            "request_count cannot be negative."
        )

    if value.scan_count < 0:
        errors.append(
            "scan_count cannot be negative."
        )

    if value.ready and not value.initialized:
        errors.append(
            "Scanner cannot be ready before initialization."
        )

    if value.ready and not value.authenticated:
        errors.append(
            "Scanner cannot be ready while unauthenticated."
        )

    return errors


def validate_commodity_scanner_snapshot(
    value: CommodityScannerSnapshot,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        value,
        CommodityScannerSnapshot,
    ):
        return [
            "Invalid CommodityScannerSnapshot type."
        ]

    errors.extend(
        validate_commodity_scanner_request(
            value.request
        )
    )

    errors.extend(
        validate_commodity_scanner_result(
            value.result
        )
    )

    metadata = value.metadata or {}

    if metadata.get("scanner_snapshot") is not True:
        errors.append(
            "snapshot metadata scanner_snapshot must be True."
        )

    if metadata.get("upstream_truth_preserved") is not True:
        errors.append(
            "snapshot must preserve upstream truth."
        )

    if metadata.get("commodity_scanner_independent") is not True:
        errors.append(
            "commodity_scanner_independent must be True."
        )

    if metadata.get("equity_scanner_dependency") is not False:
        errors.append(
            "equity_scanner_dependency must be False."
        )

    if metadata.get("index_scanner_dependency") is not False:
        errors.append(
            "index_scanner_dependency must be False."
        )

    return errors


# ============================================================
# AUTHORITY VALIDATION
# ============================================================

def validate_commodity_scanner_authority() -> List[str]:

    errors: List[str] = []

    forbidden_true = [
        key
        for key, value in COMMODITY_SCANNER_AUTHORITY.items()
        if key.endswith(
            (
                "_generation",
                "_authority",
                "_mutation",
            )
        )
        and value is True
    ]

    if forbidden_true:
        errors.extend(
            f"Forbidden authority enabled: {key}"
            for key in forbidden_true
        )

    explicit_forbidden = {
        "d13_modification",
        "risk_generation",
        "risk_override",
        "cas_generation",
        "cas_bypass",
        "execution",
        "opportunity_generation",
        "scanner_intelligence_generation",
        "upstream_mutation",
        "equity_scanner_dependency",
        "index_scanner_dependency",
    }

    for key in explicit_forbidden:
        if COMMODITY_SCANNER_AUTHORITY.get(key) is not False:
            errors.append(
                f"Authority flag {key!r} must be False."
            )

    return errors


# ============================================================
# HEALTH
# ============================================================

@dataclass
class CommodityScannerHealth:
    engine: str = COMMODITY_SCANNER_ENGINE
    version: str = COMMODITY_SCANNER_VERSION

    operational: bool = False
    initialized: bool = False
    ready: bool = False
    authenticated: bool = False

    status: CommodityScannerStatus = (
        CommodityScannerStatus.UNKNOWN
    )

    critical_scanner: bool = True

    commodity_scanner_independent: bool = True
    equity_scanner_dependency: bool = False
    index_scanner_dependency: bool = False

    # Future research readiness only.
    commodity_structure_analysis: bool = False
    commodity_supply_demand_analysis: bool = False
    commodity_inventory_analysis: bool = False
    commodity_event_sensitivity_analysis: bool = False
    commodity_contract_analysis: bool = False
    commodity_expiry_analysis: bool = False
    commodity_breakout_analysis: bool = False
    commodity_confirmation_analysis: bool = False
    commodity_exact_levels: bool = False

    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    checked_at: str = ""


def build_commodity_scanner_health(
    state: CommodityScannerState | None = None,
) -> CommodityScannerHealth:

    if state is None:
        state = get_commodity_scanner().state

    errors = validate_commodity_scanner_state(state)
    errors.extend(
        validate_commodity_scanner_authority()
    )

    operational = (
        len(errors) == 0
        and state.initialized
        and state.authenticated
        and state.status
        not in {
            CommodityScannerStatus.ERROR,
            CommodityScannerStatus.BLOCKED,
        }
    )

    return CommodityScannerHealth(
        operational=operational,
        initialized=state.initialized,
        ready=state.ready,
        authenticated=state.authenticated,
        status=state.status,
        critical_scanner=True,
        commodity_scanner_independent=True,
        equity_scanner_dependency=False,
        index_scanner_dependency=False,
        errors=errors,
        warnings=[],
        checked_at=_commodity_now(),
    )


def serialize_commodity_scanner_health(
    value: CommodityScannerHealth,
) -> Dict[str, Any]:
    return _serialize_commodity_value(value)


# ============================================================
# OPERATIONAL CHECK
# ============================================================

def commodity_scanner_operational_check() -> Dict[str, Any]:

    scanner = get_commodity_scanner()
    health = build_commodity_scanner_health(
        scanner.state
    )

    return {
        "engine": COMMODITY_SCANNER_ENGINE,
        "version": COMMODITY_SCANNER_VERSION,
        "name": COMMODITY_SCANNER_NAME,
        "operational": health.operational,
        "initialized": health.initialized,
        "ready": health.ready,
        "authenticated": health.authenticated,
        "status": health.status.value,
        "critical_scanner": True,
        "commodity_scanner_independent": True,
        "equity_scanner_dependency": False,
        "index_scanner_dependency": False,

        # Future intelligence research flags.
        "commodity_structure_analysis": False,
        "commodity_supply_demand_analysis": False,
        "commodity_inventory_analysis": False,
        "commodity_event_sensitivity_analysis": False,
        "commodity_contract_analysis": False,
        "commodity_expiry_analysis": False,
        "commodity_breakout_analysis": False,
        "commodity_confirmation_analysis": False,
        "commodity_exact_levels": False,

        # Authority boundary.
        "intelligence_generation": False,
        "decision_generation": False,
        "d13_modification": False,
        "risk_generation": False,
        "risk_override": False,
        "cas_generation": False,
        "cas_bypass": False,
        "execution": False,
        "upstream_mutation": False,

        "errors": list(health.errors),
        "warnings": list(health.warnings),
        "checked_at": health.checked_at,
    }
# ============================================================
# ROBOMLM_PLUS — COMMODITY DISCOVERY SCANNER
# PART 5 — DIAGNOSTICS / CONTRACT / INTEGRITY / SELF-CHECK
# ============================================================


# ============================================================
# DIAGNOSTICS
# ============================================================

def diagnose_commodity_scanner(
    scanner: CommodityScannerController | None = None,
) -> Dict[str, Any]:

    scanner = (
        scanner
        if scanner is not None
        else get_commodity_scanner()
    )

    state = scanner.state
    health = build_commodity_scanner_health(state)

    return {
        "engine": COMMODITY_SCANNER_ENGINE,
        "version": COMMODITY_SCANNER_VERSION,
        "name": COMMODITY_SCANNER_NAME,
        "status": state.status.value,
        "mode": state.mode.value,
        "initialized": state.initialized,
        "ready": state.ready,
        "authenticated": state.authenticated,
        "request_count": state.request_count,
        "scan_count": state.scan_count,
        "last_error": state.last_error,
        "last_scan_at": state.last_scan_at,
        "operational": health.operational,
        "critical_scanner": True,
        "commodity_scanner_independent": True,
        "equity_scanner_dependency": False,
        "index_scanner_dependency": False,
        "future_research_ready": {
            "commodity_structure_analysis": False,
            "commodity_supply_demand_analysis": False,
            "commodity_inventory_analysis": False,
            "commodity_event_sensitivity_analysis": False,
            "commodity_contract_analysis": False,
            "commodity_expiry_analysis": False,
            "commodity_breakout_analysis": False,
            "commodity_confirmation_analysis": False,
            "commodity_exact_levels": False,
        },
        "authority": serialize_commodity_scanner_authority(),
        "errors": list(health.errors),
        "warnings": list(health.warnings),
        "checked_at": health.checked_at,
    }


# ============================================================
# SUMMARY
# ============================================================

def commodity_scanner_summary(
    result: CommodityScannerResult | None = None,
) -> Dict[str, Any]:

    if result is None:
        scanner = get_commodity_scanner()
        result = scanner.last_result

    if result is None:
        return {
            "status": CommodityScannerStatus.IDLE.value,
            "mode": CommodityScannerMode.UNIVERSAL_COMMODITIES.value,
            "total_opportunities": 0,
            "qualified": 0,
            "developing": 0,
            "watch": 0,
            "bullish": 0,
            "bearish": 0,
            "neutral": 0,
            "upstream_truth_preserved": True,
            "commodity_scanner_independent": True,
        }

    qualified = 0
    developing = 0
    watch = 0

    bullish = 0
    bearish = 0
    neutral = 0

    for opportunity in result.opportunities:

        if (
            opportunity.state
            == CommodityOpportunityState.QUALIFIED
        ):
            qualified += 1

        elif (
            opportunity.state
            == CommodityOpportunityState.DEVELOPING
        ):
            developing += 1

        elif (
            opportunity.state
            == CommodityOpportunityState.WATCH
        ):
            watch += 1

        if (
            opportunity.bias
            == CommodityOpportunityBias.BULLISH
        ):
            bullish += 1

        elif (
            opportunity.bias
            == CommodityOpportunityBias.BEARISH
        ):
            bearish += 1

        elif (
            opportunity.bias
            == CommodityOpportunityBias.NEUTRAL
        ):
            neutral += 1

    return {
        "status": result.status.value,
        "mode": result.mode.value,
        "total_opportunities": len(
            result.opportunities
        ),
        "total_input_opportunities": (
            result.total_input_opportunities
        ),
        "qualified": qualified,
        "developing": developing,
        "watch": watch,
        "bullish": bullish,
        "bearish": bearish,
        "neutral": neutral,
        "source_available": result.source_available,
        "source_errors": list(result.source_errors),
        "warnings": list(result.warnings),
        "upstream_truth_preserved": True,
        "commodity_scanner_independent": True,
        "commodity_algorithm_generated": False,
        "scanner_generated_intelligence": False,
        "scanner_generated_score": False,
        "scanner_generated_decision": False,
        "equity_scanner_dependency": False,
        "index_scanner_dependency": False,
        "d13_modified": False,
        "risk_generated": False,
        "risk_overridden": False,
        "cas_bypassed": False,
        "execution_authority": False,
        "generated_at": result.generated_at,
    }


# ============================================================
# CONTRACT MANIFEST
# ============================================================

def commodity_scanner_contract_manifest() -> Dict[str, Any]:

    return {
        "engine": COMMODITY_SCANNER_ENGINE,
        "version": COMMODITY_SCANNER_VERSION,
        "name": COMMODITY_SCANNER_NAME,

        "layer": "UI_PRESENTATION",

        "role": "COMMODITY_OPPORTUNITY_SCANNER",

        "importance": "CLASS_A_DISCOVERY_COMPONENT",

        "critical_scanner": True,

        "description": (
            "Commodity-specific discovery routing layer that "
            "consumes upstream commodity intelligence without "
            "generating intelligence, decisions, risk, CAS or execution."
        ),

        # ----------------------------------------------------
        # INPUT CONTRACT
        # ----------------------------------------------------

        "inputs": [
            "USER_SERVICE_OUTPUT",
            "COMMODITY_MARKET_INPUT",
            "COMMODITY_INSTRUMENT_INPUT",
            "COMMODITY_SCANNER_FILTER",
            "UPSTREAM_COMMODITY_OPPORTUNITY_OUTPUT",
            "WATCHLIST_OUTPUT",
            "FAVORITES_OUTPUT",
            "APPLICATION_SESSION_STATE",
        ],

        # ----------------------------------------------------
        # PROCESSING CONTRACT
        # ----------------------------------------------------

        "processing": [
            "SOURCE_NORMALIZATION",
            "COMMODITY_MARKET_FILTERING",
            "COMMODITY_REGION_FILTERING",
            "COMMODITY_EXCHANGE_FILTERING",
            "COMMODITY_INSTRUMENT_FILTERING",
            "COMMODITY_CONTRACT_FILTERING",
            "COMMODITY_CATEGORY_FILTERING",
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
        # OUTPUT CONTRACT
        # ----------------------------------------------------

        "outputs": [
            "COMMODITY_SCANNER_RESULT",
            "COMMODITY_SCANNER_SNAPSHOT",
            "COMMODITY_SCANNER_STATE",
            "COMMODITY_SCANNER_HEALTH",
            "COMMODITY_SCANNER_DIAGNOSTICS",
        ],

        # ----------------------------------------------------
        # TRUTH POLICY
        # ----------------------------------------------------

        "truth_policy": {
            "upstream_truth_preserved": True,
            "scanner_generated_intelligence": False,
            "scanner_generated_score": False,
            "scanner_generated_decision": False,
            "commodity_algorithm_generated": False,
            "d13_modified": False,
            "risk_generated": False,
            "risk_overridden": False,
            "cas_bypassed": False,
            "execution_authority": False,
            "upstream_mutation": False,
        },

        # ----------------------------------------------------
        # COMMODITY INTELLIGENCE AUTHORITY
        # ----------------------------------------------------

        "intelligence_authority": {
            "owner": "UPSTREAM_COMMODITY_INTELLIGENCE",

            "structure": (
                "UPSTREAM_COMMODITY_INTELLIGENCE"
            ),

            "supply_demand": (
                "UPSTREAM_COMMODITY_INTELLIGENCE"
            ),

            "inventory": (
                "UPSTREAM_COMMODITY_INTELLIGENCE"
            ),

            "event_sensitivity": (
                "UPSTREAM_COMMODITY_INTELLIGENCE"
            ),

            "contract_analysis": (
                "UPSTREAM_COMMODITY_INTELLIGENCE"
            ),

            "expiry_analysis": (
                "UPSTREAM_COMMODITY_INTELLIGENCE"
            ),

            "breakout_analysis": (
                "UPSTREAM_COMMODITY_INTELLIGENCE"
            ),

            "confirmation": (
                "UPSTREAM_COMMODITY_INTELLIGENCE"
            ),

            "exact_levels": (
                "UPSTREAM_COMMODITY_INTELLIGENCE"
            ),
        },

        # ----------------------------------------------------
        # FUTURE RESEARCH PIPELINE
        # ----------------------------------------------------

        "future_research_pipeline": [
            "COMMODITY_STRUCTURE",
            "SUPPLY_DEMAND_ANALYSIS",
            "INVENTORY_ANALYSIS",
            "EVENT_SENSITIVITY_ANALYSIS",
            "CONTRACT_ANALYSIS",
            "EXPIRY_ANALYSIS",
            "BREAKOUT_ANALYSIS",
            "BREAKOUT_CONFIRMATION",
            "EXACT_LEVEL_CALCULATION",
            "UPSTREAM_COMMODITY_INTELLIGENCE",
            "COMMODITY_SCANNER",
        ],

        "formula_authority": (
            "UPSTREAM_COMMODITY_INTELLIGENCE"
        ),

        "formula_pluggable": True,

        # ----------------------------------------------------
        # INDEPENDENCE POLICY
        # ----------------------------------------------------

        "independence_policy": {
            "commodity_scanner_independent": True,
            "equity_scanner_dependency": False,
            "index_scanner_dependency": False,
            "equity_signal_required": False,
            "index_signal_required": False,
        },

        # ----------------------------------------------------
        # FORBIDDEN AUTHORITY
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
# INTEGRITY
# ============================================================

def validate_commodity_scanner_integrity(
    scanner: CommodityScannerController | None = None,
) -> List[str]:

    scanner = (
        scanner
        if scanner is not None
        else get_commodity_scanner()
    )

    errors: List[str] = []

    errors.extend(
        validate_commodity_scanner_state(
            scanner.state
        )
    )

    errors.extend(
        validate_commodity_scanner_authority()
    )

    if scanner.last_request is not None:
        errors.extend(
            validate_commodity_scanner_request(
                scanner.last_request
            )
        )

    if scanner.last_result is not None:
        errors.extend(
            validate_commodity_scanner_result(
                scanner.last_result
            )
        )

    return errors


# ============================================================
# CONTRACT VALIDATION
# ============================================================

def validate_commodity_scanner_contract() -> List[str]:

    errors: List[str] = []

    manifest = commodity_scanner_contract_manifest()

    if manifest.get("layer") != "UI_PRESENTATION":
        errors.append(
            "Commodity scanner layer must be UI_PRESENTATION."
        )

    if manifest.get("critical_scanner") is not True:
        errors.append(
            "Commodity scanner must remain Class-A critical."
        )

    if manifest.get(
        "formula_pluggable"
    ) is not True:
        errors.append(
            "Commodity intelligence must remain formula-pluggable."
        )

    truth_policy = manifest.get(
        "truth_policy",
        {},
    )

    required_false = [
        "scanner_generated_intelligence",
        "scanner_generated_score",
        "scanner_generated_decision",
        "commodity_algorithm_generated",
        "d13_modified",
        "risk_generated",
        "risk_overridden",
        "cas_bypassed",
        "execution_authority",
        "upstream_mutation",
    ]

    for key in required_false:
        if truth_policy.get(key) is not False:
            errors.append(
                f"truth_policy[{key!r}] must be False."
            )

    independence = manifest.get(
        "independence_policy",
        {},
    )

    if independence.get(
        "commodity_scanner_independent"
    ) is not True:
        errors.append(
            "commodity_scanner_independent must be True."
        )

    if independence.get(
        "equity_scanner_dependency"
    ) is not False:
        errors.append(
            "equity_scanner_dependency must be False."
        )

    if independence.get(
        "index_scanner_dependency"
    ) is not False:
        errors.append(
            "index_scanner_dependency must be False."
        )

    pipeline = manifest.get(
        "future_research_pipeline",
        [],
    )

    required_pipeline = [
        "COMMODITY_STRUCTURE",
        "SUPPLY_DEMAND_ANALYSIS",
        "INVENTORY_ANALYSIS",
        "EVENT_SENSITIVITY_ANALYSIS",
        "CONTRACT_ANALYSIS",
        "EXPIRY_ANALYSIS",
        "BREAKOUT_ANALYSIS",
        "BREAKOUT_CONFIRMATION",
        "EXACT_LEVEL_CALCULATION",
        "UPSTREAM_COMMODITY_INTELLIGENCE",
        "COMMODITY_SCANNER",
    ]

    for stage in required_pipeline:
        if stage not in pipeline:
            errors.append(
                f"Missing research pipeline stage: {stage}"
            )

    return errors


# ============================================================
# MODULE CHECK
# ============================================================

def commodity_scanner_module_check() -> Dict[str, Any]:

    scanner = create_commodity_scanner(
        authenticated=True
    )

    scanner.initialize()

    contract_errors = (
        validate_commodity_scanner_contract()
    )

    integrity_errors = (
        validate_commodity_scanner_integrity(
            scanner
        )
    )

    health = build_commodity_scanner_health(
        scanner.state
    )

    return {
        "engine": COMMODITY_SCANNER_ENGINE,
        "version": COMMODITY_SCANNER_VERSION,
        "module": "commodity_scanner",
        "contract_valid": not contract_errors,
        "integrity_valid": not integrity_errors,
        "health_operational": health.operational,
        "contract_errors": contract_errors,
        "integrity_errors": integrity_errors,
        "authority_valid": not validate_commodity_scanner_authority(),
    }


# ============================================================
# SELF CHECK
# ============================================================

def commodity_scanner_self_check() -> Dict[str, Any]:

    sample = UpstreamCommodityOpportunity(
        opportunity_id="commodity-self-check-001",
        symbol="SAMPLE-COMMODITY",
        instrument_id="commodity-instrument-001",
        instrument_name="Sample Commodity",
        commodity_type=CommodityType.ENERGY,
        contract_type=CommodityContractType.FUTURE,
        market_id="sample-market",
        country="TEST",
        region="TEST",
        exchange="TEST-EXCHANGE",
        currency="USD",
        commodity_group="ENERGY",
        category="TEST",
        expiry="",
        contract_month="TEST",
        state=CommodityOpportunityState.QUALIFIED,
        bias=CommodityOpportunityBias.BULLISH,
        strength=CommodityOpportunityStrength.STRONG,
        summary="Upstream commodity opportunity self-check.",
        confidence=0.90,
        timestamp=_commodity_now(),
        favorite=False,
        watchlisted=False,
        priority=CommodityScannerPriority.HIGH,
        source=CommoditySourceType.UPSTREAM_OPPORTUNITY_ENGINE,
        metadata={
            "research_formula_generated": False,
        },
    )

    request = CommodityScannerRequest(
        mode=CommodityScannerMode.UNIVERSAL_COMMODITIES,
        opportunities=[sample],
        authenticated=True,
    )

    result = run_commodity_scanner(request)

    errors = validate_commodity_scanner_result(
        result
    )

    converted = (
        result.opportunities[0]
        if result.opportunities
        else None
    )

    truth_preserved = bool(
        converted
        and converted.symbol == sample.symbol
        and converted.bias == sample.bias
        and converted.strength == sample.strength
        and converted.state == sample.state
        and converted.confidence == sample.confidence
        and converted.metadata.get(
            "upstream_truth"
        ) is True
        and converted.metadata.get(
            "commodity_algorithm_generated"
        ) is False
        and converted.metadata.get(
            "scanner_generated_intelligence"
        ) is False
        and converted.metadata.get(
            "scanner_generated_score"
        ) is False
        and converted.metadata.get(
            "scanner_generated_decision"
        ) is False
    )

    return {
        "passed": (
            not errors
            and truth_preserved
            and not validate_commodity_scanner_authority()
            and not validate_commodity_scanner_contract()
        ),
        "result_status": result.status.value,
        "output_count": len(
            result.opportunities
        ),
        "truth_preserved": truth_preserved,
        "validation_errors": errors,
        "authority_errors": (
            validate_commodity_scanner_authority()
        ),
        "contract_errors": (
            validate_commodity_scanner_contract()
        ),
        "research_formula_generated": False,
        "commodity_algorithm_generated": False,
    }


# ============================================================
# DEFAULT FACTORY
# ============================================================

def create_default_commodity_scanner(
    authenticated: bool = False,
) -> CommodityScannerController:

    scanner = CommodityScannerController(
        authenticated=authenticated
    )

    scanner.initialize()

    return scanner


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [
    # Constants
    "COMMODITY_SCANNER_ENGINE",
    "COMMODITY_SCANNER_VERSION",
    "COMMODITY_SCANNER_NAME",
    "COMMODITY_SCANNER_TITLE",
    "COMMODITY_SCANNER_DESCRIPTION",
    "COMMODITY_SCANNER_AUTHORITY",

    # Enums
    "CommodityScannerStatus",
    "CommodityScannerMode",
    "CommodityType",
    "CommodityContractType",
    "CommodityOpportunityState",
    "CommodityOpportunityBias",
    "CommodityOpportunityStrength",
    "CommodityScannerPriority",
    "CommoditySourceType",

    # Schemas
    "CommodityMarketInput",
    "CommodityInstrumentInput",
    "UpstreamCommodityOpportunity",
    "CommodityScannerFilter",
    "CommodityScannerOpportunity",
    "CommodityScannerResult",
    "CommodityScannerRequest",
    "CommodityScannerSnapshot",
    "CommodityScannerState",
    "CommodityScannerHealth",

    # Helpers
    "_commodity_text",
    "_commodity_bool",
    "_commodity_float",
    "_commodity_enum",
    "_commodity_now",

    # Normalization
    "normalize_commodity_market",
    "normalize_commodity_instrument",
    "normalize_upstream_commodity_opportunity",
    "normalize_commodity_filter",
    "normalize_commodity_request",
    "_normalize_commodity_string_list",
    "_normalize_commodity_enum_list",

    # Filtering
    "commodity_opportunity_matches_filter",
    "filter_upstream_commodity_opportunities",
    "filter_commodity_markets",
    "filter_commodity_instruments",
    "_commodity_matches_list",
    "_commodity_matches_enum_list",

    # Routing / result
    "convert_upstream_commodity_opportunity",
    "build_commodity_scanner_result",
    "commodity_scanner_source_status",
    "run_commodity_scanner",

    # Controller
    "CommodityScannerController",
    "get_commodity_scanner",
    "create_commodity_scanner",
    "scan_commodity_market",
    "scan_with_commodity_scanner",

    # Serialization
    "_serialize_commodity_value",
    "serialize_commodity_market",
    "serialize_commodity_instrument",
    "serialize_upstream_commodity_opportunity",
    "serialize_commodity_filter",
    "serialize_commodity_scanner_opportunity",
    "serialize_commodity_scanner_result",
    "serialize_commodity_scanner_request",
    "serialize_commodity_scanner_snapshot",
    "serialize_commodity_scanner_state",
    "serialize_commodity_scanner_health",
    "serialize_commodity_scanner_authority",

    # Validation
    "validate_commodity_market",
    "validate_commodity_instrument",
    "validate_upstream_commodity_opportunity",
    "validate_commodity_filter",
    "validate_commodity_scanner_opportunity",
    "validate_commodity_scanner_request",
    "validate_commodity_scanner_result",
    "validate_commodity_scanner_state",
    "validate_commodity_scanner_snapshot",
    "validate_commodity_scanner_authority",
    "validate_commodity_scanner_integrity",
    "validate_commodity_scanner_contract",

    # Health / diagnostics
    "build_commodity_scanner_health",
    "commodity_scanner_operational_check",
    "diagnose_commodity_scanner",
    "commodity_scanner_summary",

    # Contract / testing
    "commodity_scanner_contract_manifest",
    "commodity_scanner_module_check",
    "commodity_scanner_self_check",
    "create_default_commodity_scanner",
]