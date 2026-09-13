# ============================================================
# ROBOMLM_PLUS — EQUITY DISCOVERY SCANNER
# PART 1 — CORE CONTRACT / AUTHORITY / SCHEMAS
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


EQUITY_SCANNER_ENGINE = "ROBOMLM_PLUS_EQUITY_SCANNER"
EQUITY_SCANNER_VERSION = "1.0"
EQUITY_SCANNER_NAME = "Equity Opportunity Scanner"
EQUITY_SCANNER_TITLE = "Equity Market Opportunity Scanner"
EQUITY_SCANNER_DESCRIPTION = (
    "First-class equity discovery scanner for presenting and routing "
    "upstream equity opportunity intelligence across markets and exchanges."
)

# Equity scanning is a CLASS-A discovery surface.
# It must work even where an index such as NIFTY/SENSEX is not the
# primary market representation. Individual equities remain first-class.
EQUITY_SCANNER_AUTHORITY = {
    "scanner_orchestration": True,
    "equity_opportunity_presentation": True,
    "market_filtering": True,
    "exchange_filtering": True,
    "instrument_filtering": True,
    "sector_filtering": True,
    "industry_filtering": True,
    "equity_universe_filtering": True,
    "upstream_opportunity_consumption": True,

    "individual_equity_first_class": True,
    "index_dependency_required": False,
    "index_signal_required": False,
    "index_replacement": False,

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
    "upstream_mutation": False,
}


class EquityScannerStatus(str, Enum):
    IDLE = "IDLE"
    LOADING = "LOADING"
    READY = "READY"
    DEGRADED = "DEGRADED"
    BLOCKED = "BLOCKED"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class EquityScannerMode(str, Enum):
    UNIVERSAL_EQUITIES = "UNIVERSAL_EQUITIES"
    MARKET = "MARKET"
    EXCHANGE = "EXCHANGE"
    SECTOR = "SECTOR"
    INDUSTRY = "INDUSTRY"
    INSTRUMENT = "INSTRUMENT"
    FAVORITES = "FAVORITES"
    WATCHLIST = "WATCHLIST"
    UNKNOWN = "UNKNOWN"


class EquityAssetType(str, Enum):
    COMMON_STOCK = "COMMON_STOCK"
    PREFERRED_STOCK = "PREFERRED_STOCK"
    ETF = "ETF"
    REIT = "REIT"
    ADR = "ADR"
    OTHER_EQUITY = "OTHER_EQUITY"
    UNKNOWN = "UNKNOWN"


class EquityOpportunityState(str, Enum):
    UNKNOWN = "UNKNOWN"
    WATCH = "WATCH"
    DEVELOPING = "DEVELOPING"
    QUALIFIED = "QUALIFIED"
    INVALIDATED = "INVALIDATED"
    EXPIRED = "EXPIRED"


class EquityOpportunityBias(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"


class EquityOpportunityStrength(str, Enum):
    VERY_WEAK = "VERY_WEAK"
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    VERY_STRONG = "VERY_STRONG"
    UNKNOWN = "UNKNOWN"


class EquityScannerPriority(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EquitySourceType(str, Enum):
    UPSTREAM_OPPORTUNITY_ENGINE = "UPSTREAM_OPPORTUNITY_ENGINE"
    EQUITY_OPPORTUNITY_ENGINE = "EQUITY_OPPORTUNITY_ENGINE"
    DISCOVERY_ENGINE = "DISCOVERY_ENGINE"
    UNKNOWN = "UNKNOWN"


def _equity_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _equity_bool(value: Any, default: bool = False) -> bool:
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


def _equity_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _equity_enum(value: Any, enum_type: Any, default: Any) -> Any:
    if isinstance(value, enum_type):
        return value
    try:
        return enum_type(value)
    except (TypeError, ValueError):
        return default


def _equity_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class EquityMarketInput:
    market_id: str
    market_name: str
    country: str = ""
    region: str = ""
    exchange: str = ""
    currency: str = ""
    timezone: str = ""
    enabled: bool = True
    selected: bool = False
    index_available: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EquityInstrumentInput:
    instrument_id: str
    symbol: str
    display_name: str = ""
    asset_type: EquityAssetType = EquityAssetType.COMMON_STOCK
    exchange: str = ""
    market_id: str = ""
    country: str = ""
    currency: str = ""
    sector: str = ""
    industry: str = ""
    enabled: bool = True
    selected: bool = False
    tradable: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UpstreamEquityOpportunity:
    opportunity_id: str
    symbol: str
    instrument_id: str = ""
    instrument_name: str = ""
    asset_type: EquityAssetType = EquityAssetType.COMMON_STOCK
    market_id: str = ""
    country: str = ""
    exchange: str = ""
    currency: str = ""
    sector: str = ""
    industry: str = ""

    state: EquityOpportunityState = EquityOpportunityState.UNKNOWN
    bias: EquityOpportunityBias = EquityOpportunityBias.UNKNOWN
    strength: EquityOpportunityStrength = EquityOpportunityStrength.UNKNOWN

    summary: str = ""
    confidence: float = 0.0
    timestamp: str = ""

    favorite: bool = False
    watchlisted: bool = False
    priority: EquityScannerPriority = EquityScannerPriority.NORMAL

    source: EquitySourceType = (
        EquitySourceType.UPSTREAM_OPPORTUNITY_ENGINE
    )

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EquityScannerFilter:
    market_ids: List[str] = field(default_factory=list)
    countries: List[str] = field(default_factory=list)
    exchange_names: List[str] = field(default_factory=list)
    instrument_ids: List[str] = field(default_factory=list)
    symbols: List[str] = field(default_factory=list)

    asset_types: List[EquityAssetType] = field(default_factory=list)
    sectors: List[str] = field(default_factory=list)
    industries: List[str] = field(default_factory=list)

    states: List[EquityOpportunityState] = field(default_factory=list)
    biases: List[EquityOpportunityBias] = field(default_factory=list)
    strengths: List[EquityOpportunityStrength] = field(default_factory=list)

    favorites_only: bool = False
    watchlist_only: bool = False
    tradable_only: bool = True

    include_invalidated: bool = False
    include_expired: bool = False

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EquityScannerOpportunity:
    opportunity_id: str
    symbol: str
    instrument_id: str
    instrument_name: str
    asset_type: EquityAssetType

    market_id: str
    country: str
    exchange: str
    currency: str
    sector: str
    industry: str

    state: EquityOpportunityState
    bias: EquityOpportunityBias
    strength: EquityOpportunityStrength

    summary: str
    confidence: float
    timestamp: str

    favorite: bool
    watchlisted: bool
    priority: EquityScannerPriority
    source: EquitySourceType

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EquityScannerResult:
    status: EquityScannerStatus
    mode: EquityScannerMode

    opportunities: List[EquityScannerOpportunity] = field(
        default_factory=list
    )

    total_input_opportunities: int = 0
    total_output_opportunities: int = 0

    source_available: bool = False
    source_errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    generated_at: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EquityScannerRequest:
    mode: EquityScannerMode = EquityScannerMode.UNIVERSAL_EQUITIES

    markets: List[EquityMarketInput] = field(
        default_factory=list
    )
    instruments: List[EquityInstrumentInput] = field(
        default_factory=list
    )
    opportunities: List[UpstreamEquityOpportunity] = field(
        default_factory=list
    )

    scanner_filter: EquityScannerFilter = field(
        default_factory=EquityScannerFilter
    )

    authenticated: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EquityScannerSnapshot:
    request: EquityScannerRequest
    result: EquityScannerResult
    captured_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)
# ============================================================
# ROBOMLM_PLUS — EQUITY DISCOVERY SCANNER
# PART 2 — NORMALIZATION / FILTERING / UPSTREAM ROUTING
# ============================================================


def normalize_equity_market(
    value: Any,
) -> EquityMarketInput:
    if isinstance(value, EquityMarketInput):
        return value

    data = value if isinstance(value, dict) else {}

    return EquityMarketInput(
        market_id=_equity_text(data.get("market_id")),
        market_name=_equity_text(data.get("market_name")),
        country=_equity_text(data.get("country")),
        region=_equity_text(data.get("region")),
        exchange=_equity_text(data.get("exchange")),
        currency=_equity_text(data.get("currency")),
        timezone=_equity_text(data.get("timezone")),
        enabled=_equity_bool(data.get("enabled"), True),
        selected=_equity_bool(data.get("selected")),
        index_available=_equity_bool(
            data.get("index_available"), True
        ),
        metadata=dict(data.get("metadata") or {}),
    )


def normalize_equity_instrument(
    value: Any,
) -> EquityInstrumentInput:
    if isinstance(value, EquityInstrumentInput):
        return value

    data = value if isinstance(value, dict) else {}

    return EquityInstrumentInput(
        instrument_id=_equity_text(data.get("instrument_id")),
        symbol=_equity_text(data.get("symbol")),
        display_name=_equity_text(
            data.get("display_name"),
            _equity_text(data.get("symbol")),
        ),
        asset_type=_equity_enum(
            data.get("asset_type"),
            EquityAssetType,
            EquityAssetType.COMMON_STOCK,
        ),
        exchange=_equity_text(data.get("exchange")),
        market_id=_equity_text(data.get("market_id")),
        country=_equity_text(data.get("country")),
        currency=_equity_text(data.get("currency")),
        sector=_equity_text(data.get("sector")),
        industry=_equity_text(data.get("industry")),
        enabled=_equity_bool(data.get("enabled"), True),
        selected=_equity_bool(data.get("selected")),
        tradable=_equity_bool(data.get("tradable"), True),
        metadata=dict(data.get("metadata") or {}),
    )


def normalize_upstream_equity_opportunity(
    value: Any,
) -> UpstreamEquityOpportunity:
    if isinstance(value, UpstreamEquityOpportunity):
        return value

    data = value if isinstance(value, dict) else {}

    return UpstreamEquityOpportunity(
        opportunity_id=_equity_text(data.get("opportunity_id")),
        symbol=_equity_text(data.get("symbol")),
        instrument_id=_equity_text(data.get("instrument_id")),
        instrument_name=_equity_text(data.get("instrument_name")),
        asset_type=_equity_enum(
            data.get("asset_type"),
            EquityAssetType,
            EquityAssetType.COMMON_STOCK,
        ),
        market_id=_equity_text(data.get("market_id")),
        country=_equity_text(data.get("country")),
        exchange=_equity_text(data.get("exchange")),
        currency=_equity_text(data.get("currency")),
        sector=_equity_text(data.get("sector")),
        industry=_equity_text(data.get("industry")),
        state=_equity_enum(
            data.get("state"),
            EquityOpportunityState,
            EquityOpportunityState.UNKNOWN,
        ),
        bias=_equity_enum(
            data.get("bias"),
            EquityOpportunityBias,
            EquityOpportunityBias.UNKNOWN,
        ),
        strength=_equity_enum(
            data.get("strength"),
            EquityOpportunityStrength,
            EquityOpportunityStrength.UNKNOWN,
        ),
        summary=_equity_text(data.get("summary")),
        confidence=_equity_float(data.get("confidence")),
        timestamp=_equity_text(data.get("timestamp")),
        favorite=_equity_bool(data.get("favorite")),
        watchlisted=_equity_bool(data.get("watchlisted")),
        priority=_equity_enum(
            data.get("priority"),
            EquityScannerPriority,
            EquityScannerPriority.NORMAL,
        ),
        source=_equity_enum(
            data.get("source"),
            EquitySourceType,
            EquitySourceType.UPSTREAM_OPPORTUNITY_ENGINE,
        ),
        metadata=dict(data.get("metadata") or {}),
    )


def _normalize_equity_string_list(
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
        text = _equity_text(value)
        if text:
            result.append(text)

    return result


def _normalize_equity_enum_list(
    values: Any,
    enum_type: Any,
) -> List[Any]:
    if values is None:
        return []

    if isinstance(values, (str, enum_type)):
        values = [values]

    if not isinstance(values, (list, tuple, set)):
        return []

    result: List[Any] = []

    for value in values:
        item = _equity_enum(value, enum_type, None)
        if item is not None:
            result.append(item)

    return result


def normalize_equity_filter(
    value: Any,
) -> EquityScannerFilter:
    if isinstance(value, EquityScannerFilter):
        return value

    data = value if isinstance(value, dict) else {}

    return EquityScannerFilter(
        market_ids=_normalize_equity_string_list(
            data.get("market_ids")
        ),
        countries=_normalize_equity_string_list(
            data.get("countries")
        ),
        exchange_names=_normalize_equity_string_list(
            data.get("exchange_names")
        ),
        instrument_ids=_normalize_equity_string_list(
            data.get("instrument_ids")
        ),
        symbols=_normalize_equity_string_list(
            data.get("symbols")
        ),
        asset_types=_normalize_equity_enum_list(
            data.get("asset_types"),
            EquityAssetType,
        ),
        sectors=_normalize_equity_string_list(
            data.get("sectors")
        ),
        industries=_normalize_equity_string_list(
            data.get("industries")
        ),
        states=_normalize_equity_enum_list(
            data.get("states"),
            EquityOpportunityState,
        ),
        biases=_normalize_equity_enum_list(
            data.get("biases"),
            EquityOpportunityBias,
        ),
        strengths=_normalize_equity_enum_list(
            data.get("strengths"),
            EquityOpportunityStrength,
        ),
        favorites_only=_equity_bool(
            data.get("favorites_only")
        ),
        watchlist_only=_equity_bool(
            data.get("watchlist_only")
        ),
        tradable_only=_equity_bool(
            data.get("tradable_only"), True
        ),
        include_invalidated=_equity_bool(
            data.get("include_invalidated")
        ),
        include_expired=_equity_bool(
            data.get("include_expired")
        ),
        metadata=dict(data.get("metadata") or {}),
    )


def normalize_equity_request(
    value: Any,
) -> EquityScannerRequest:
    if isinstance(value, EquityScannerRequest):
        return value

    data = value if isinstance(value, dict) else {}

    markets = [
        normalize_equity_market(item)
        for item in data.get("markets", [])
    ]

    instruments = [
        normalize_equity_instrument(item)
        for item in data.get("instruments", [])
    ]

    opportunities = [
        normalize_upstream_equity_opportunity(item)
        for item in data.get("opportunities", [])
    ]

    return EquityScannerRequest(
        mode=_equity_enum(
            data.get("mode"),
            EquityScannerMode,
            EquityScannerMode.UNIVERSAL_EQUITIES,
        ),
        markets=markets,
        instruments=instruments,
        opportunities=opportunities,
        scanner_filter=normalize_equity_filter(
            data.get("scanner_filter")
        ),
        authenticated=_equity_bool(
            data.get("authenticated")
        ),
        metadata=dict(data.get("metadata") or {}),
    )


def _equity_matches_list(
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


def _equity_matches_enum_list(
    value: Any,
    allowed: List[Any],
) -> bool:
    if not allowed:
        return True
    return value in allowed


def equity_opportunity_matches_filter(
    opportunity: UpstreamEquityOpportunity,
    scanner_filter: EquityScannerFilter,
) -> bool:

    if not scanner_filter.include_invalidated:
        if opportunity.state == EquityOpportunityState.INVALIDATED:
            return False

    if not scanner_filter.include_expired:
        if opportunity.state == EquityOpportunityState.EXPIRED:
            return False

    if scanner_filter.tradable_only:
        if opportunity.metadata.get("tradable") is False:
            return False

    if scanner_filter.favorites_only and not opportunity.favorite:
        return False

    if scanner_filter.watchlist_only and not opportunity.watchlisted:
        return False

    if not _equity_matches_list(
        opportunity.market_id,
        scanner_filter.market_ids,
    ):
        return False

    if not _equity_matches_list(
        opportunity.country,
        scanner_filter.countries,
    ):
        return False

    if not _equity_matches_list(
        opportunity.exchange,
        scanner_filter.exchange_names,
    ):
        return False

    if not _equity_matches_list(
        opportunity.instrument_id,
        scanner_filter.instrument_ids,
    ):
        return False

    if not _equity_matches_list(
        opportunity.symbol,
        scanner_filter.symbols,
    ):
        return False

    if not _equity_matches_enum_list(
        opportunity.asset_type,
        scanner_filter.asset_types,
    ):
        return False

    if not _equity_matches_list(
        opportunity.sector,
        scanner_filter.sectors,
    ):
        return False

    if not _equity_matches_list(
        opportunity.industry,
        scanner_filter.industries,
    ):
        return False

    if not _equity_matches_enum_list(
        opportunity.state,
        scanner_filter.states,
    ):
        return False

    if not _equity_matches_enum_list(
        opportunity.bias,
        scanner_filter.biases,
    ):
        return False

    if not _equity_matches_enum_list(
        opportunity.strength,
        scanner_filter.strengths,
    ):
        return False

    return True


def filter_upstream_equity_opportunities(
    opportunities: List[UpstreamEquityOpportunity],
    scanner_filter: EquityScannerFilter,
) -> List[UpstreamEquityOpportunity]:

    return [
        opportunity
        for opportunity in opportunities
        if equity_opportunity_matches_filter(
            opportunity,
            scanner_filter,
        )
    ]


def filter_equity_markets(
    markets: List[EquityMarketInput],
    scanner_filter: EquityScannerFilter,
) -> List[EquityMarketInput]:

    if not scanner_filter.market_ids:
        return list(markets)

    return [
        market
        for market in markets
        if _equity_matches_list(
            market.market_id,
            scanner_filter.market_ids,
        )
    ]


def filter_equity_instruments(
    instruments: List[EquityInstrumentInput],
    scanner_filter: EquityScannerFilter,
) -> List[EquityInstrumentInput]:

    result: List[EquityInstrumentInput] = []

    for instrument in instruments:

        if scanner_filter.tradable_only and not instrument.tradable:
            continue

        if not _equity_matches_list(
            instrument.market_id,
            scanner_filter.market_ids,
        ):
            continue

        if not _equity_matches_list(
            instrument.country,
            scanner_filter.countries,
        ):
            continue

        if not _equity_matches_list(
            instrument.exchange,
            scanner_filter.exchange_names,
        ):
            continue

        if not _equity_matches_list(
            instrument.instrument_id,
            scanner_filter.instrument_ids,
        ):
            continue

        if not _equity_matches_list(
            instrument.symbol,
            scanner_filter.symbols,
        ):
            continue

        if not _equity_matches_enum_list(
            instrument.asset_type,
            scanner_filter.asset_types,
        ):
            continue

        if not _equity_matches_list(
            instrument.sector,
            scanner_filter.sectors,
        ):
            continue

        if not _equity_matches_list(
            instrument.industry,
            scanner_filter.industries,
        ):
            continue

        result.append(instrument)

    return result


def convert_upstream_equity_opportunity(
    opportunity: UpstreamEquityOpportunity,
) -> EquityScannerOpportunity:

    metadata = dict(opportunity.metadata)

    # Scanner must preserve upstream truth.
    metadata.update({
        "upstream_truth": True,
        "scanner_generated_intelligence": False,
        "scanner_generated_score": False,
        "scanner_generated_decision": False,
        "d13_modified": False,
        "risk_generated": False,
        "risk_overridden": False,
        "cas_bypassed": False,
        "execution_authority": False,
    })

    return EquityScannerOpportunity(
        opportunity_id=opportunity.opportunity_id,
        symbol=opportunity.symbol,
        instrument_id=opportunity.instrument_id,
        instrument_name=opportunity.instrument_name,
        asset_type=opportunity.asset_type,
        market_id=opportunity.market_id,
        country=opportunity.country,
        exchange=opportunity.exchange,
        currency=opportunity.currency,
        sector=opportunity.sector,
        industry=opportunity.industry,
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


def build_equity_scanner_result(
    request: EquityScannerRequest,
    opportunities: List[UpstreamEquityOpportunity],
    status: EquityScannerStatus,
) -> EquityScannerResult:

    output = [
        convert_upstream_equity_opportunity(item)
        for item in opportunities
    ]

    return EquityScannerResult(
        status=status,
        mode=request.mode,
        opportunities=output,
        total_input_opportunities=len(request.opportunities),
        total_output_opportunities=len(output),
        source_available=bool(request.opportunities),
        source_errors=[],
        warnings=[],
        generated_at=_equity_now(),
        metadata={
            "upstream_truth_preserved": True,
            "scanner_generated_intelligence": False,
            "scanner_generated_score": False,
            "scanner_generated_decision": False,
            "d13_modified": False,
            "risk_generated": False,
            "risk_overridden": False,
            "cas_bypassed": False,
            "execution_authority": False,
            "individual_equity_first_class": True,
            "index_dependency_required": False,
        },
    )


def equity_scanner_source_status(
    request: EquityScannerRequest,
) -> EquityScannerStatus:

    if not request.authenticated:
        return EquityScannerStatus.BLOCKED

    if not request.opportunities:
        return EquityScannerStatus.DEGRADED

    return EquityScannerStatus.READY
# ============================================================
# ROBOMLM_PLUS — EQUITY DISCOVERY SCANNER
# PART 3 — STATE / SCAN ORCHESTRATION / CONTROLLER
# ============================================================


@dataclass
class EquityScannerState:
    initialized: bool = False
    ready: bool = False
    authenticated: bool = False

    status: EquityScannerStatus = EquityScannerStatus.IDLE
    mode: EquityScannerMode = EquityScannerMode.UNIVERSAL_EQUITIES

    request_count: int = 0
    scan_count: int = 0

    last_error: str = ""
    last_scan_at: str = ""

    metadata: Dict[str, Any] = field(default_factory=dict)


def create_equity_scanner_state(
    authenticated: bool = False,
    mode: EquityScannerMode = EquityScannerMode.UNIVERSAL_EQUITIES,
) -> EquityScannerState:
    return EquityScannerState(
        initialized=False,
        ready=False,
        authenticated=authenticated,
        status=(
            EquityScannerStatus.IDLE
            if authenticated
            else EquityScannerStatus.BLOCKED
        ),
        mode=mode,
        request_count=0,
        scan_count=0,
        last_error="",
        last_scan_at="",
        metadata={
            "critical_scanner": True,
            "individual_equity_first_class": True,
            "index_dependency_required": False,
        },
    )


def normalize_equity_scanner_state(
    value: Any,
) -> EquityScannerState:
    if isinstance(value, EquityScannerState):
        return value

    data = value if isinstance(value, dict) else {}

    return EquityScannerState(
        initialized=_equity_bool(data.get("initialized")),
        ready=_equity_bool(data.get("ready")),
        authenticated=_equity_bool(data.get("authenticated")),
        status=_equity_enum(
            data.get("status"),
            EquityScannerStatus,
            EquityScannerStatus.UNKNOWN,
        ),
        mode=_equity_enum(
            data.get("mode"),
            EquityScannerMode,
            EquityScannerMode.UNIVERSAL_EQUITIES,
        ),
        request_count=int(
            _equity_float(data.get("request_count"))
        ),
        scan_count=int(
            _equity_float(data.get("scan_count"))
        ),
        last_error=_equity_text(data.get("last_error")),
        last_scan_at=_equity_text(data.get("last_scan_at")),
        metadata=dict(data.get("metadata") or {}),
    )


def run_equity_scanner(
    request: EquityScannerRequest,
) -> EquityScannerResult:

    request = normalize_equity_request(request)

    if not request.authenticated:
        return EquityScannerResult(
            status=EquityScannerStatus.BLOCKED,
            mode=request.mode,
            opportunities=[],
            total_input_opportunities=len(
                request.opportunities
            ),
            total_output_opportunities=0,
            source_available=False,
            source_errors=[
                "Authenticated session required for equity scanner."
            ],
            warnings=[],
            generated_at=_equity_now(),
            metadata={
                "upstream_truth_preserved": True,
                "scanner_generated_intelligence": False,
                "scanner_generated_score": False,
                "scanner_generated_decision": False,
                "d13_modified": False,
                "risk_generated": False,
                "risk_overridden": False,
                "cas_bypassed": False,
                "execution_authority": False,
                "individual_equity_first_class": True,
                "index_dependency_required": False,
            },
        )

    scanner_filter = normalize_equity_filter(
        request.scanner_filter
    )

    markets = filter_equity_markets(
        request.markets,
        scanner_filter,
    )

    instruments = filter_equity_instruments(
        request.instruments,
        scanner_filter,
    )

    market_ids = {
        market.market_id
        for market in markets
        if market.enabled
    }

    instrument_ids = {
        instrument.instrument_id
        for instrument in instruments
        if instrument.enabled
    }

    filtered_opportunities = (
        filter_upstream_equity_opportunities(
            request.opportunities,
            scanner_filter,
        )
    )

    # If market/instrument universes are supplied, they act as
    # routing constraints. They do not create intelligence.
    if request.markets:
        filtered_opportunities = [
            opportunity
            for opportunity in filtered_opportunities
            if opportunity.market_id in market_ids
        ]

    if request.instruments:
        filtered_opportunities = [
            opportunity
            for opportunity in filtered_opportunities
            if opportunity.instrument_id in instrument_ids
        ]

    status = equity_scanner_source_status(request)

    warnings: List[str] = []

    if not request.markets:
        warnings.append(
            "No explicit equity market universe supplied; "
            "using upstream opportunity market identity."
        )

    if not request.instruments:
        warnings.append(
            "No explicit equity instrument universe supplied; "
            "using upstream opportunity instrument identity."
        )

    if not request.opportunities:
        warnings.append(
            "No upstream equity opportunities available."
        )

    result = build_equity_scanner_result(
        request,
        filtered_opportunities,
        status,
    )

    result.warnings.extend(warnings)

    result.metadata.update({
        "markets_considered": len(markets),
        "instruments_considered": len(instruments),
        "individual_equity_first_class": True,
        "index_dependency_required": False,
    })

    return result


class EquityScannerController:

    def __init__(
        self,
        state: Optional[EquityScannerState] = None,
    ) -> None:
        self._state = normalize_equity_scanner_state(
            state or create_equity_scanner_state()
        )
        self._last_request: Optional[EquityScannerRequest] = None
        self._last_result: Optional[EquityScannerResult] = None
        self._request_history: List[EquityScannerRequest] = []
        self._result_history: List[EquityScannerResult] = []

    @property
    def state(self) -> EquityScannerState:
        return self._state

    @property
    def status(self) -> EquityScannerStatus:
        return self._state.status

    @property
    def mode(self) -> EquityScannerMode:
        return self._state.mode

    @property
    def authenticated(self) -> bool:
        return self._state.authenticated

    @property
    def last_request(
        self,
    ) -> Optional[EquityScannerRequest]:
        return self._last_request

    @property
    def last_result(
        self,
    ) -> Optional[EquityScannerResult]:
        return self._last_result

    def initialize(self) -> EquityScannerState:
        self._state.initialized = True

        if self._state.authenticated:
            self._state.status = EquityScannerStatus.READY
            self._state.ready = True
        else:
            self._state.status = EquityScannerStatus.BLOCKED
            self._state.ready = False

        self._state.last_error = ""
        return self._state

    def scan(
        self,
        request: EquityScannerRequest,
    ) -> EquityScannerResult:

        request = normalize_equity_request(request)
        self._state.request_count += 1
        self._state.status = EquityScannerStatus.LOADING

        if not self._state.authenticated:
            request.authenticated = False
        else:
            request.authenticated = True

        self._last_request = request
        self._request_history.append(request)

        if len(self._request_history) > 500:
            self._request_history.pop(0)

        try:
            result = run_equity_scanner(request)

            self._last_result = result
            self._result_history.append(result)

            if len(self._result_history) > 500:
                self._result_history.pop(0)

            self._state.scan_count += 1
            self._state.status = result.status
            self._state.ready = (
                result.status == EquityScannerStatus.READY
            )
            self._state.last_error = ""
            self._state.last_scan_at = result.generated_at
            self._state.mode = request.mode

            return result

        except Exception as exc:
            self._state.status = EquityScannerStatus.ERROR
            self._state.ready = False
            self._state.last_error = str(exc)

            result = EquityScannerResult(
                status=EquityScannerStatus.ERROR,
                mode=request.mode,
                opportunities=[],
                total_input_opportunities=len(
                    request.opportunities
                ),
                total_output_opportunities=0,
                source_available=False,
                source_errors=[str(exc)],
                warnings=[],
                generated_at=_equity_now(),
                metadata={
                    "upstream_truth_preserved": True,
                    "scanner_generated_intelligence": False,
                    "scanner_generated_score": False,
                    "scanner_generated_decision": False,
                    "d13_modified": False,
                    "risk_generated": False,
                    "risk_overridden": False,
                    "cas_bypassed": False,
                    "execution_authority": False,
                    "individual_equity_first_class": True,
                    "index_dependency_required": False,
                },
            )

            self._last_result = result
            self._result_history.append(result)

            if len(self._result_history) > 500:
                self._result_history.pop(0)

            return result

    def set_mode(
        self,
        mode: EquityScannerMode,
    ) -> EquityScannerState:
        self._state.mode = _equity_enum(
            mode,
            EquityScannerMode,
            EquityScannerMode.UNIVERSAL_EQUITIES,
        )
        return self._state

    def set_authenticated(
        self,
        authenticated: bool,
    ) -> EquityScannerState:

        self._state.authenticated = bool(authenticated)

        if self._state.authenticated:
            self._state.status = (
                EquityScannerStatus.READY
                if self._state.initialized
                else EquityScannerStatus.IDLE
            )
            self._state.ready = self._state.initialized
        else:
            self._state.status = EquityScannerStatus.BLOCKED
            self._state.ready = False

        return self._state

    def block(self) -> EquityScannerState:
        self._state.status = EquityScannerStatus.BLOCKED
        self._state.ready = False
        return self._state

    def reset(self) -> EquityScannerState:
        authenticated = self._state.authenticated

        self._state = create_equity_scanner_state(
            authenticated=authenticated,
            mode=EquityScannerMode.UNIVERSAL_EQUITIES,
        )

        self._last_request = None
        self._last_result = None
        self._request_history.clear()
        self._result_history.clear()

        return self._state

    def snapshot(self) -> EquityScannerSnapshot:
        request = self._last_request or EquityScannerRequest(
            mode=self._state.mode,
            authenticated=self._state.authenticated,
        )

        result = self._last_result or EquityScannerResult(
            status=self._state.status,
            mode=self._state.mode,
            generated_at=_equity_now(),
            metadata={
                "upstream_truth_preserved": True,
                "individual_equity_first_class": True,
                "index_dependency_required": False,
            },
        )

        return EquityScannerSnapshot(
            request=request,
            result=result,
            captured_at=_equity_now(),
            metadata={
                "critical_scanner": True,
                "individual_equity_first_class": True,
                "index_dependency_required": False,
            },
        )

    def request_history(
        self,
    ) -> List[EquityScannerRequest]:
        return list(self._request_history)

    def result_history(
        self,
    ) -> List[EquityScannerResult]:
        return list(self._result_history)


_DEFAULT_EQUITY_SCANNER = EquityScannerController()


def get_equity_scanner() -> EquityScannerController:
    return _DEFAULT_EQUITY_SCANNER


def create_equity_scanner(
    authenticated: bool = False,
) -> EquityScannerController:
    scanner = EquityScannerController(
        create_equity_scanner_state(
            authenticated=authenticated
        )
    )
    return scanner


def scan_equity_market(
    request: EquityScannerRequest,
) -> EquityScannerResult:
    scanner = get_equity_scanner()

    if not scanner.state.initialized:
        scanner.initialize()

    return scanner.scan(request)


def scan_with_equity_scanner(
    opportunities: List[UpstreamEquityOpportunity],
    scanner_filter: Optional[EquityScannerFilter] = None,
    mode: EquityScannerMode = (
        EquityScannerMode.UNIVERSAL_EQUITIES
    ),
    authenticated: bool = False,
) -> EquityScannerResult:

    request = EquityScannerRequest(
        mode=mode,
        opportunities=opportunities,
        scanner_filter=(
            scanner_filter or EquityScannerFilter()
        ),
        authenticated=authenticated,
    )

    return run_equity_scanner(request)
# ============================================================
# ROBOMLM_PLUS — EQUITY DISCOVERY SCANNER
# PART 4 — SERIALIZATION / VALIDATION / HEALTH
# ============================================================


def _serialize_equity_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, list):
        return [_serialize_equity_value(item) for item in value]

    if isinstance(value, tuple):
        return [_serialize_equity_value(item) for item in value]

    if isinstance(value, dict):
        return {
            str(key): _serialize_equity_value(item)
            for key, item in value.items()
        }

    if hasattr(value, "__dataclass_fields__"):
        return {
            key: _serialize_equity_value(
                getattr(value, key)
            )
            for key in value.__dataclass_fields__
        }

    return value


def serialize_equity_market(
    value: EquityMarketInput,
) -> Dict[str, Any]:
    return _serialize_equity_value(value)


def serialize_equity_instrument(
    value: EquityInstrumentInput,
) -> Dict[str, Any]:
    return _serialize_equity_value(value)


def serialize_upstream_equity_opportunity(
    value: UpstreamEquityOpportunity,
) -> Dict[str, Any]:
    return _serialize_equity_value(value)


def serialize_equity_filter(
    value: EquityScannerFilter,
) -> Dict[str, Any]:
    return _serialize_equity_value(value)


def serialize_equity_scanner_opportunity(
    value: EquityScannerOpportunity,
) -> Dict[str, Any]:
    return _serialize_equity_value(value)


def serialize_equity_scanner_result(
    value: EquityScannerResult,
) -> Dict[str, Any]:
    return _serialize_equity_value(value)


def serialize_equity_scanner_request(
    value: EquityScannerRequest,
) -> Dict[str, Any]:
    return _serialize_equity_value(value)


def serialize_equity_scanner_state(
    value: EquityScannerState,
) -> Dict[str, Any]:
    return _serialize_equity_value(value)


def serialize_equity_scanner_snapshot(
    value: EquityScannerSnapshot,
) -> Dict[str, Any]:
    return _serialize_equity_value(value)


def validate_equity_market(
    value: EquityMarketInput,
) -> bool:
    return bool(
        value.market_id
        and value.market_name
    )


def validate_equity_instrument(
    value: EquityInstrumentInput,
) -> bool:
    if not value.instrument_id:
        return False

    if not value.symbol:
        return False

    if value.asset_type == EquityAssetType.UNKNOWN:
        return False

    return True


def validate_upstream_equity_opportunity(
    value: UpstreamEquityOpportunity,
) -> bool:

    if not value.opportunity_id:
        return False

    if not value.symbol:
        return False

    if value.asset_type == EquityAssetType.UNKNOWN:
        return False

    if value.state == EquityOpportunityState.UNKNOWN:
        return False

    if value.bias == EquityOpportunityBias.UNKNOWN:
        return False

    if value.strength == EquityOpportunityStrength.UNKNOWN:
        return False

    if not 0.0 <= value.confidence <= 1.0:
        return False

    if value.source == EquitySourceType.UNKNOWN:
        return False

    return True


def validate_equity_filter(
    value: EquityScannerFilter,
) -> bool:

    if not isinstance(value.market_ids, list):
        return False

    if not isinstance(value.countries, list):
        return False

    if not isinstance(value.exchange_names, list):
        return False

    if not isinstance(value.symbols, list):
        return False

    for item in value.asset_types:
        if item == EquityAssetType.UNKNOWN:
            return False

    for item in value.states:
        if item == EquityOpportunityState.UNKNOWN:
            return False

    for item in value.biases:
        if item == EquityOpportunityBias.UNKNOWN:
            return False

    for item in value.strengths:
        if item == EquityOpportunityStrength.UNKNOWN:
            return False

    return True


def validate_equity_scanner_opportunity(
    value: EquityScannerOpportunity,
) -> bool:

    if not value.opportunity_id:
        return False

    if not value.symbol:
        return False

    if not value.instrument_id:
        return False

    if value.asset_type == EquityAssetType.UNKNOWN:
        return False

    if value.state == EquityOpportunityState.UNKNOWN:
        return False

    if value.bias == EquityOpportunityBias.UNKNOWN:
        return False

    if value.strength == EquityOpportunityStrength.UNKNOWN:
        return False

    if not 0.0 <= value.confidence <= 1.0:
        return False

    if value.source == EquitySourceType.UNKNOWN:
        return False

    metadata = value.metadata

    if metadata.get("upstream_truth") is not True:
        return False

    forbidden_flags = (
        "scanner_generated_intelligence",
        "scanner_generated_score",
        "scanner_generated_decision",
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


def validate_equity_scanner_request(
    value: EquityScannerRequest,
) -> bool:

    if value.mode == EquityScannerMode.UNKNOWN:
        return False

    if not validate_equity_filter(
        value.scanner_filter
    ):
        return False

    for market in value.markets:
        if not validate_equity_market(market):
            return False

    for instrument in value.instruments:
        if not validate_equity_instrument(instrument):
            return False

    for opportunity in value.opportunities:
        if not validate_upstream_equity_opportunity(
            opportunity
        ):
            return False

    return True


def validate_equity_scanner_result(
    value: EquityScannerResult,
) -> bool:

    if value.mode == EquityScannerMode.UNKNOWN:
        return False

    if value.status == EquityScannerStatus.UNKNOWN:
        return False

    if value.total_input_opportunities < 0:
        return False

    if value.total_output_opportunities < 0:
        return False

    if value.total_output_opportunities != len(
        value.opportunities
    ):
        return False

    if value.total_output_opportunities > (
        value.total_input_opportunities
    ):
        return False

    for opportunity in value.opportunities:
        if not validate_equity_scanner_opportunity(
            opportunity
        ):
            return False

    metadata = value.metadata

    if metadata.get(
        "scanner_generated_intelligence"
    ) is True:
        return False

    if metadata.get(
        "scanner_generated_score"
    ) is True:
        return False

    if metadata.get(
        "scanner_generated_decision"
    ) is True:
        return False

    if metadata.get("d13_modified") is True:
        return False

    return True


def validate_equity_scanner_state(
    value: EquityScannerState,
) -> bool:

    if value.status == EquityScannerStatus.UNKNOWN:
        return False

    if value.mode == EquityScannerMode.UNKNOWN:
        return False

    if value.request_count < 0:
        return False

    if value.scan_count < 0:
        return False

    if value.status == EquityScannerStatus.READY:
        if not value.ready:
            return False

    if value.status == EquityScannerStatus.BLOCKED:
        if value.ready:
            return False

    return True


def validate_equity_scanner_snapshot(
    value: EquityScannerSnapshot,
) -> bool:

    if not validate_equity_scanner_request(
        value.request
    ):
        return False

    if not validate_equity_scanner_result(
        value.result
    ):
        return False

    if not value.captured_at:
        return False

    return True


def validate_equity_scanner_authority(
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
        "upstream_mutation",
    )

    for key in required_forbidden:
        if authority.get(key) is not False:
            return False

    if authority.get(
        "individual_equity_first_class"
    ) is not True:
        return False

    if authority.get(
        "index_dependency_required"
    ) is not False:
        return False

    return True


@dataclass
class EquityScannerHealth:
    engine: str
    version: str
    status: EquityScannerStatus
    initialized: bool
    ready: bool
    authenticated: bool
    state_valid: bool
    authority_valid: bool
    last_result_valid: bool
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    critical_scanner: bool = True
    individual_equity_first_class: bool = True
    index_dependency_required: bool = False
    structure_breakout_ready: bool = False


def build_equity_scanner_health(
    scanner: Optional[EquityScannerController] = None,
) -> EquityScannerHealth:

    controller = scanner or get_equity_scanner()

    state_valid = validate_equity_scanner_state(
        controller.state
    )

    authority_valid = validate_equity_scanner_authority(
        EQUITY_SCANNER_AUTHORITY
    )

    last_result_valid = True

    if controller.last_result is not None:
        last_result_valid = validate_equity_scanner_result(
            controller.last_result
        )

    warnings: List[str] = []
    errors: List[str] = []

    if not controller.authenticated:
        warnings.append(
            "Authenticated session required."
        )

    if controller.status == EquityScannerStatus.DEGRADED:
        warnings.append(
            "Upstream equity opportunity source is degraded."
        )

    if not state_valid:
        errors.append(
            "Equity scanner state validation failed."
        )

    if not authority_valid:
        errors.append(
            "Equity scanner authority validation failed."
        )

    if not last_result_valid:
        errors.append(
            "Last equity scanner result validation failed."
        )

    return EquityScannerHealth(
        engine=EQUITY_SCANNER_ENGINE,
        version=EQUITY_SCANNER_VERSION,
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
        individual_equity_first_class=True,
        index_dependency_required=False,
        structure_breakout_ready=False,
    )


def serialize_equity_scanner_health(
    value: EquityScannerHealth,
) -> Dict[str, Any]:
    return _serialize_equity_value(value)


def equity_scanner_operational_check(
    scanner: Optional[EquityScannerController] = None,
) -> Dict[str, Any]:

    health = build_equity_scanner_health(scanner)

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
        "individual_equity_first_class": True,
        "index_dependency_required": False,

        # Future research engine will populate these.
        "structure_analysis": False,
        "consolidation_analysis": False,
        "accumulation_analysis": False,
        "breakout_calculation": False,
        "breakout_direction_calculation": False,
        "exact_breakout_level": False,

        "warnings": health.warnings,
        "errors": health.errors,
    }
# ============================================================
# ROBOMLM_PLUS — EQUITY DISCOVERY SCANNER
# PART 5 — DIAGNOSTICS / CONTRACT / SELF-CHECK / EXPORTS
# ============================================================


def diagnose_equity_scanner(
    scanner: Optional[EquityScannerController] = None,
) -> Dict[str, Any]:

    controller = scanner or get_equity_scanner()
    health = build_equity_scanner_health(controller)

    return {
        "engine": EQUITY_SCANNER_ENGINE,
        "version": EQUITY_SCANNER_VERSION,
        "name": EQUITY_SCANNER_NAME,
        "status": controller.status.value,
        "initialized": controller.state.initialized,
        "ready": controller.state.ready,
        "authenticated": controller.authenticated,

        "critical_scanner": True,
        "individual_equity_first_class": True,
        "index_dependency_required": False,
        "index_signal_required": False,

        # Research intelligence is upstream-owned.
        "structure_analysis": False,
        "consolidation_analysis": False,
        "accumulation_distribution_analysis": False,
        "breakout_boundary_calculation": False,
        "breakout_direction_calculation": False,
        "breakout_confirmation": False,
        "exact_level_calculation": False,

        # These indicate architectural readiness, not completed formulas.
        "research_plugin_ready": True,
        "upstream_intelligence_ready": True,
        "profit_opportunity_focus": True,

        "state_valid": health.state_valid,
        "authority_valid": health.authority_valid,
        "last_result_valid": health.last_result_valid,

        "warnings": list(health.warnings),
        "errors": list(health.errors),
    }


def equity_scanner_summary(
    scanner: Optional[EquityScannerController] = None,
) -> Dict[str, Any]:

    controller = scanner or get_equity_scanner()
    result = controller.last_result

    opportunities = (
        list(result.opportunities)
        if result is not None
        else []
    )

    qualified = [
        item
        for item in opportunities
        if item.state == EquityOpportunityState.QUALIFIED
    ]

    bullish = [
        item
        for item in opportunities
        if item.bias == EquityOpportunityBias.BULLISH
    ]

    bearish = [
        item
        for item in opportunities
        if item.bias == EquityOpportunityBias.BEARISH
    ]

    return {
        "engine": EQUITY_SCANNER_ENGINE,
        "version": EQUITY_SCANNER_VERSION,

        "status": controller.status.value,
        "mode": controller.mode.value,

        "total_opportunities": len(opportunities),
        "qualified_opportunities": len(qualified),
        "bullish_opportunities": len(bullish),
        "bearish_opportunities": len(bearish),

        "critical_scanner": True,
        "individual_equity_first_class": True,
        "index_dependency_required": False,

        # Strategic purpose.
        "profit_opportunity_focus": True,
        "better_opportunity_discovery": True,

        # Research architecture.
        "structure_breakout_pipeline": (
            "STRUCTURE → CONSOLIDATION → "
            "ACCUMULATION_DISTRIBUTION → "
            "BREAKOUT_BOUNDARY → "
            "BREAKOUT_DIRECTION → "
            "BREAKOUT_CONFIRMATION → "
            "EXACT_LEVELS → "
            "UPSTREAM_INTELLIGENCE → EQUITY_SCANNER"
        ),

        # Formula ownership remains outside the scanner.
        "formula_authority": (
            "UPSTREAM_EQUITY_STRUCTURE_INTELLIGENCE"
        ),
        "scanner_generates_formula": False,
        "scanner_generates_intelligence": False,
        "scanner_generates_score": False,
        "scanner_generates_decision": False,

        "metadata": {
            "research_plugin_ready": True,
            "upstream_truth_preserved": True,
        },
    }


def equity_scanner_contract_manifest() -> Dict[str, Any]:

    return {
        "engine": EQUITY_SCANNER_ENGINE,
        "version": EQUITY_SCANNER_VERSION,
        "layer": "UI_PRESENTATION",
        "role": "EQUITY_OPPORTUNITY_SCANNER",
        "importance": "CLASS_A_CRITICAL",

        "market_model": {
            "individual_equity_first_class": True,
            "index_dependency_required": False,
            "index_signal_required": False,
            "supports_index_light_markets": True,
            "supports_market_level_scanning": True,
            "supports_exchange_level_scanning": True,
        },

        "strategic_objective": {
            "profit_opportunity_focus": True,
            "better_opportunity_discovery": True,
            "high_quality_equity_selection": True,
        },

        "inputs": [
            "USER_SERVICE_OUTPUT",
            "EQUITY_MARKET_INPUT",
            "EQUITY_INSTRUMENT_INPUT",
            "EQUITY_FILTER_INPUT",
            "WATCHLIST_OUTPUT",
            "FAVORITES_OUTPUT",
            "UPSTREAM_EQUITY_OPPORTUNITY_ENGINE_OUTPUT",

            # Future validated research outputs.
            "STRUCTURE_INTELLIGENCE_OUTPUT",
            "CONSOLIDATION_ANALYSIS_OUTPUT",
            "ACCUMULATION_DISTRIBUTION_OUTPUT",
            "BREAKOUT_BOUNDARY_OUTPUT",
            "BREAKOUT_DIRECTION_OUTPUT",
            "BREAKOUT_CONFIRMATION_OUTPUT",
            "EXACT_LEVELS_OUTPUT",
        ],

        "processing": [
            "SOURCE_NORMALIZATION",
            "EQUITY_UNIVERSE_FILTERING",
            "MARKET_FILTERING",
            "EXCHANGE_FILTERING",
            "SECTOR_FILTERING",
            "INDUSTRY_FILTERING",
            "INSTRUMENT_FILTERING",
            "OPPORTUNITY_STATE_FILTERING",
            "UPSTREAM_OPPORTUNITY_ROUTING",
            "STRUCTURE_INTELLIGENCE_PRESENTATION",
            "BREAKOUT_INTELLIGENCE_PRESENTATION",
            "EXACT_LEVEL_PRESENTATION",
            "OPPORTUNITY_PRIORITIZATION",
        ],

        # Explicit boundary:
        # formulas belong to the upstream research/intelligence layer.
        "formula_generation": False,
        "intelligence_generation": False,
        "decision_generation": False,

        "outputs": [
            "EQUITY_SCANNER_RESULT",
            "EQUITY_SCANNER_SNAPSHOT",
            "EQUITY_SCANNER_STATE",
            "EQUITY_SCANNER_HEALTH",
            "EQUITY_SCANNER_DIAGNOSTICS",
        ],

        "truth_policy": {
            "upstream_truth_preserved": True,
            "scanner_may_transform_presentation": True,
            "scanner_may_modify_upstream_intelligence": False,
            "scanner_may_invent_formula": False,
        },

        "authority_owners": {
            "market_data": "MARKET_DATA_LAYER",
            "evidence": "EVIDENCE_CORTEX",
            "structure": "UPSTREAM_EQUITY_STRUCTURE_INTELLIGENCE",
            "breakout": "UPSTREAM_EQUITY_STRUCTURE_INTELLIGENCE",
            "opportunity": "EQUITY_OPPORTUNITY_ENGINE",
            "decision": "DECISION_CORTEX",
            "d13": "D13",
            "risk": "RISK_ENGINE",
            "cas": "CAS",
            "execution": "EXECUTION_LAYER",
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
            "UPSTREAM_MUTATION",
        ],
    }


def validate_equity_scanner_integrity(
    scanner: Optional[EquityScannerController] = None,
) -> bool:

    controller = scanner or get_equity_scanner()

    if not validate_equity_scanner_authority(
        EQUITY_SCANNER_AUTHORITY
    ):
        return False

    if not validate_equity_scanner_state(
        controller.state
    ):
        return False

    if controller.last_request is not None:
        if not validate_equity_scanner_request(
            controller.last_request
        ):
            return False

    if controller.last_result is not None:
        if not validate_equity_scanner_result(
            controller.last_result
        ):
            return False

    return True


def validate_equity_scanner_contract() -> bool:

    manifest = equity_scanner_contract_manifest()

    required = (
        "layer",
        "role",
        "importance",
        "inputs",
        "processing",
        "outputs",
        "truth_policy",
        "authority_owners",
        "forbidden",
    )

    for key in required:
        if key not in manifest:
            return False

    market_model = manifest["market_model"]

    if market_model.get(
        "individual_equity_first_class"
    ) is not True:
        return False

    if market_model.get(
        "index_dependency_required"
    ) is not False:
        return False

    if manifest.get("formula_generation") is not False:
        return False

    if manifest.get("intelligence_generation") is not False:
        return False

    if manifest.get("decision_generation") is not False:
        return False

    truth_policy = manifest["truth_policy"]

    if truth_policy.get(
        "upstream_truth_preserved"
    ) is not True:
        return False

    if truth_policy.get(
        "scanner_may_invent_formula"
    ) is not False:
        return False

    return True


def equity_scanner_module_check(
    scanner: Optional[EquityScannerController] = None,
) -> Dict[str, Any]:

    controller = scanner or get_equity_scanner()

    integrity = validate_equity_scanner_integrity(
        controller
    )

    contract = validate_equity_scanner_contract()

    operational = equity_scanner_operational_check(
        controller
    )

    return {
        "engine": EQUITY_SCANNER_ENGINE,
        "version": EQUITY_SCANNER_VERSION,
        "integrity_valid": integrity,
        "contract_valid": contract,
        "operational": operational["operational"],
        "critical_scanner": True,
        "individual_equity_first_class": True,
        "index_dependency_required": False,
        "research_plugin_ready": True,
        "profit_opportunity_focus": True,
        "errors": (
            []
            if integrity and contract
            else [
                "Equity scanner module validation failed."
            ]
        ),
    }


def equity_scanner_self_check() -> Dict[str, Any]:

    sample = UpstreamEquityOpportunity(
        opportunity_id="SELF_CHECK_EQ_001",
        symbol="TESTEQ",
        instrument_id="TEST_INSTRUMENT",
        instrument_name="Test Equity",
        market_id="TEST_MARKET",
        country="TEST",
        exchange="TEST_EXCHANGE",
        currency="TEST",
        state=EquityOpportunityState.QUALIFIED,
        bias=EquityOpportunityBias.BULLISH,
        strength=EquityOpportunityStrength.STRONG,
        summary="Upstream intelligence self-check.",
        confidence=0.90,
        timestamp=_equity_now(),
        source=EquitySourceType.UPSTREAM_OPPORTUNITY_ENGINE,
        metadata={
            "research_owner": (
                "UPSTREAM_EQUITY_STRUCTURE_INTELLIGENCE"
            ),
            "scanner_formula_generation": False,
            "scanner_intelligence_generation": False,
            "upstream_truth": True,
        },
    )

    request = EquityScannerRequest(
        mode=EquityScannerMode.UNIVERSAL_EQUITIES,
        opportunities=[sample],
        authenticated=True,
    )

    result = run_equity_scanner(request)

    output_valid = validate_equity_scanner_result(
        result
    )

    preserved = False

    if result.opportunities:
        output = result.opportunities[0]

        preserved = (
            output.symbol == sample.symbol
            and output.bias == sample.bias
            and output.strength == sample.strength
            and output.state == sample.state
            and output.metadata.get(
                "upstream_truth"
            ) is True
            and output.metadata.get(
                "scanner_intelligence_generation"
            ) is False
        )

    contract_valid = validate_equity_scanner_contract()

    return {
        "engine": EQUITY_SCANNER_ENGINE,
        "self_check": True,
        "request_valid": validate_equity_scanner_request(
            request
        ),
        "result_valid": output_valid,
        "upstream_truth_preserved": preserved,
        "contract_valid": contract_valid,

        "individual_equity_first_class": True,
        "index_dependency_required": False,

        "research_plugin_ready": True,
        "formula_generation_in_scanner": False,
        "intelligence_generation_in_scanner": False,

        "overall": (
            output_valid
            and preserved
            and contract_valid
        ),
    }


def create_default_equity_scanner(
    authenticated: bool = False,
) -> EquityScannerController:

    scanner = create_equity_scanner()

    scanner.initialize()

    scanner.set_authenticated(
        authenticated
    )

    return scanner


__all__ = [
    # Constants
    "EQUITY_SCANNER_ENGINE",
    "EQUITY_SCANNER_VERSION",
    "EQUITY_SCANNER_NAME",
    "EQUITY_SCANNER_TITLE",
    "EQUITY_SCANNER_DESCRIPTION",
    "EQUITY_SCANNER_AUTHORITY",

    # Enums
    "EquityScannerStatus",
    "EquityScannerMode",
    "EquityAssetType",
    "EquityOpportunityState",
    "EquityOpportunityBias",
    "EquityOpportunityStrength",
    "EquityScannerPriority",
    "EquitySourceType",

    # Contracts
    "EquityMarketInput",
    "EquityInstrumentInput",
    "UpstreamEquityOpportunity",
    "EquityScannerFilter",
    "EquityScannerOpportunity",
    "EquityScannerResult",
    "EquityScannerRequest",
    "EquityScannerSnapshot",
    "EquityScannerState",
    "EquityScannerHealth",

    # Normalization / filtering
    "normalize_equity_market",
    "normalize_equity_instrument",
    "normalize_upstream_equity_opportunity",
    "normalize_equity_filter",
    "normalize_equity_request",
    "equity_opportunity_matches_filter",
    "filter_upstream_equity_opportunities",
    "filter_equity_markets",
    "filter_equity_instruments",

    # Scanner
    "convert_upstream_equity_opportunity",
    "build_equity_scanner_result",
    "equity_scanner_source_status",
    "run_equity_scanner",
    "EquityScannerController",
    "get_equity_scanner",
    "create_equity_scanner",
    "scan_equity_market",
    "scan_with_equity_scanner",

    # Serialization
    "serialize_equity_market",
    "serialize_equity_instrument",
    "serialize_upstream_equity_opportunity",
    "serialize_equity_filter",
    "serialize_equity_scanner_opportunity",
    "serialize_equity_scanner_result",
    "serialize_equity_scanner_request",
    "serialize_equity_scanner_state",
    "serialize_equity_scanner_snapshot",
    "serialize_equity_scanner_health",

    # Validation / health
    "validate_equity_market",
    "validate_equity_instrument",
    "validate_upstream_equity_opportunity",
    "validate_equity_filter",
    "validate_equity_scanner_opportunity",
    "validate_equity_scanner_request",
    "validate_equity_scanner_result",
    "validate_equity_scanner_state",
    "validate_equity_scanner_snapshot",
    "validate_equity_scanner_authority",
    "build_equity_scanner_health",
    "equity_scanner_operational_check",

    # Diagnostics / contract
    "diagnose_equity_scanner",
    "equity_scanner_summary",
    "equity_scanner_contract_manifest",
    "validate_equity_scanner_integrity",
    "validate_equity_scanner_contract",
    "equity_scanner_module_check",
    "equity_scanner_self_check",
    "create_default_equity_scanner",
]

