# ============================================================
# ROBOMLM_PLUS — STOCK DISCOVERY SCANNER
# PART 1 — CORE CONTRACT / AUTHORITY / SCHEMAS
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


STOCK_SCANNER_ENGINE = "ROBOMLM_PLUS_STOCK_SCANNER"
STOCK_SCANNER_VERSION = "1.0"
STOCK_SCANNER_NAME = "Stock Opportunity Scanner"
STOCK_SCANNER_TITLE = "Stock Market Opportunity Scanner"
STOCK_SCANNER_DESCRIPTION = (
    "Stock discovery scanner for presenting and routing "
    "upstream stock opportunity intelligence."
)


STOCK_SCANNER_AUTHORITY = {
    "scanner_orchestration": True,
    "stock_opportunity_presentation": True,
    "market_filtering": True,
    "instrument_filtering": True,
    "sector_filtering": True,
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
    "upstream_mutation": False,
}


class StockScannerStatus(str, Enum):
    IDLE = "IDLE"
    LOADING = "LOADING"
    READY = "READY"
    DEGRADED = "DEGRADED"
    BLOCKED = "BLOCKED"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class StockScannerMode(str, Enum):
    UNIVERSAL_STOCKS = "UNIVERSAL_STOCKS"
    MARKET = "MARKET"
    SECTOR = "SECTOR"
    INSTRUMENT = "INSTRUMENT"
    FAVORITES = "FAVORITES"
    WATCHLIST = "WATCHLIST"
    UNKNOWN = "UNKNOWN"


class StockOpportunityState(str, Enum):
    UNKNOWN = "UNKNOWN"
    WATCH = "WATCH"
    DEVELOPING = "DEVELOPING"
    QUALIFIED = "QUALIFIED"
    INVALIDATED = "INVALIDATED"
    EXPIRED = "EXPIRED"


class StockOpportunityBias(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"


class StockOpportunityStrength(str, Enum):
    VERY_WEAK = "VERY_WEAK"
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    VERY_STRONG = "VERY_STRONG"
    UNKNOWN = "UNKNOWN"


class StockScannerPriority(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class StockSourceType(str, Enum):
    UPSTREAM_OPPORTUNITY_ENGINE = "UPSTREAM_OPPORTUNITY_ENGINE"
    STOCK_OPPORTUNITY_ENGINE = "STOCK_OPPORTUNITY_ENGINE"
    DISCOVERY_ENGINE = "DISCOVERY_ENGINE"
    UNKNOWN = "UNKNOWN"


def _stock_text(value: Any, default: str = "") -> str:
    if value is None:
        return default

    text = str(value).strip()
    return text if text else default


def _stock_bool(value: Any, default: bool = False) -> bool:
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


def _stock_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _stock_enum(
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


def _stock_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class StockMarketInput:
    market_id: str
    market_name: str
    region: str = ""
    exchange: str = ""
    timezone: str = ""
    enabled: bool = True
    selected: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StockInstrumentInput:
    instrument_id: str
    symbol: str
    display_name: str = ""
    exchange: str = ""
    market_id: str = ""
    sector: str = ""
    industry: str = ""
    currency: str = ""
    enabled: bool = True
    selected: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UpstreamStockOpportunity:
    opportunity_id: str
    symbol: str
    instrument_id: str = ""
    instrument_name: str = ""
    market_id: str = ""
    exchange: str = ""
    sector: str = ""
    industry: str = ""

    state: StockOpportunityState = (
        StockOpportunityState.UNKNOWN
    )
    bias: StockOpportunityBias = (
        StockOpportunityBias.UNKNOWN
    )
    strength: StockOpportunityStrength = (
        StockOpportunityStrength.UNKNOWN
    )

    summary: str = ""
    confidence: float = 0.0
    timestamp: str = ""

    favorite: bool = False
    watchlisted: bool = False

    priority: StockScannerPriority = (
        StockScannerPriority.NORMAL
    )

    source: StockSourceType = (
        StockSourceType.UPSTREAM_OPPORTUNITY_ENGINE
    )

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StockScannerFilter:
    market_ids: List[str] = field(default_factory=list)
    exchange_names: List[str] = field(default_factory=list)
    instrument_ids: List[str] = field(default_factory=list)
    symbols: List[str] = field(default_factory=list)

    sectors: List[str] = field(default_factory=list)
    industries: List[str] = field(default_factory=list)

    states: List[StockOpportunityState] = field(
        default_factory=list
    )
    biases: List[StockOpportunityBias] = field(
        default_factory=list
    )
    strengths: List[StockOpportunityStrength] = field(
        default_factory=list
    )

    favorites_only: bool = False
    watchlist_only: bool = False
    include_invalidated: bool = False
    include_expired: bool = False

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StockScannerOpportunity:
    opportunity_id: str
    symbol: str
    instrument_id: str
    instrument_name: str
    market_id: str
    exchange: str
    sector: str
    industry: str

    state: StockOpportunityState
    bias: StockOpportunityBias
    strength: StockOpportunityStrength

    summary: str
    confidence: float
    timestamp: str

    favorite: bool
    watchlisted: bool
    priority: StockScannerPriority
    source: StockSourceType

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StockScannerResult:
    status: StockScannerStatus
    mode: StockScannerMode

    opportunities: List[StockScannerOpportunity] = (
        field(default_factory=list)
    )

    total_input_opportunities: int = 0
    total_output_opportunities: int = 0

    source_available: bool = False
    source_errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    generated_at: str = ""

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StockScannerRequest:
    mode: StockScannerMode = StockScannerMode.UNIVERSAL_STOCKS

    markets: List[StockMarketInput] = (
        field(default_factory=list)
    )

    instruments: List[StockInstrumentInput] = (
        field(default_factory=list)
    )

    opportunities: List[UpstreamStockOpportunity] = (
        field(default_factory=list)
    )

    scanner_filter: StockScannerFilter = (
        field(default_factory=StockScannerFilter)
    )

    authenticated: bool = False

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StockScannerSnapshot:
    request: StockScannerRequest
    result: StockScannerResult
    captured_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)
# ============================================================
# ROBOMLM_PLUS — STOCK DISCOVERY SCANNER
# PART 2 — NORMALIZATION / FILTERING / RESULT ORCHESTRATION
# ============================================================

def normalize_stock_market(value: Any) -> StockMarketInput:
    if isinstance(value, StockMarketInput):
        return value

    if not isinstance(value, dict):
        return StockMarketInput(
            market_id="",
            market_name="",
        )

    return StockMarketInput(
        market_id=_stock_text(value.get("market_id")),
        market_name=_stock_text(value.get("market_name")),
        region=_stock_text(value.get("region")),
        exchange=_stock_text(value.get("exchange")),
        timezone=_stock_text(value.get("timezone")),
        enabled=_stock_bool(value.get("enabled"), True),
        selected=_stock_bool(value.get("selected")),
        metadata=dict(value.get("metadata") or {}),
    )


def normalize_stock_instrument(
    value: Any,
) -> StockInstrumentInput:
    if isinstance(value, StockInstrumentInput):
        return value

    if not isinstance(value, dict):
        return StockInstrumentInput(
            instrument_id="",
            symbol="",
        )

    return StockInstrumentInput(
        instrument_id=_stock_text(value.get("instrument_id")),
        symbol=_stock_text(value.get("symbol")),
        display_name=_stock_text(value.get("display_name")),
        exchange=_stock_text(value.get("exchange")),
        market_id=_stock_text(value.get("market_id")),
        sector=_stock_text(value.get("sector")),
        industry=_stock_text(value.get("industry")),
        currency=_stock_text(value.get("currency")),
        enabled=_stock_bool(value.get("enabled"), True),
        selected=_stock_bool(value.get("selected")),
        metadata=dict(value.get("metadata") or {}),
    )


def normalize_upstream_stock_opportunity(
    value: Any,
) -> UpstreamStockOpportunity:
    if isinstance(value, UpstreamStockOpportunity):
        return value

    if not isinstance(value, dict):
        return UpstreamStockOpportunity(
            opportunity_id="",
            symbol="",
        )

    return UpstreamStockOpportunity(
        opportunity_id=_stock_text(
            value.get("opportunity_id")
        ),
        symbol=_stock_text(value.get("symbol")),
        instrument_id=_stock_text(
            value.get("instrument_id")
        ),
        instrument_name=_stock_text(
            value.get("instrument_name")
        ),
        market_id=_stock_text(value.get("market_id")),
        exchange=_stock_text(value.get("exchange")),
        sector=_stock_text(value.get("sector")),
        industry=_stock_text(value.get("industry")),
        state=_stock_enum(
            value.get("state"),
            StockOpportunityState,
            StockOpportunityState.UNKNOWN,
        ),
        bias=_stock_enum(
            value.get("bias"),
            StockOpportunityBias,
            StockOpportunityBias.UNKNOWN,
        ),
        strength=_stock_enum(
            value.get("strength"),
            StockOpportunityStrength,
            StockOpportunityStrength.UNKNOWN,
        ),
        summary=_stock_text(value.get("summary")),
        confidence=_stock_float(
            value.get("confidence"),
            0.0,
        ),
        timestamp=_stock_text(value.get("timestamp")),
        favorite=_stock_bool(value.get("favorite")),
        watchlisted=_stock_bool(
            value.get("watchlisted")
        ),
        priority=_stock_enum(
            value.get("priority"),
            StockScannerPriority,
            StockScannerPriority.NORMAL,
        ),
        source=_stock_enum(
            value.get("source"),
            StockSourceType,
            StockSourceType.UPSTREAM_OPPORTUNITY_ENGINE,
        ),
        metadata=dict(value.get("metadata") or {}),
    )


def _normalize_string_list(value: Any) -> List[str]:
    if value is None:
        return []

    if isinstance(value, str):
        return (
            [value.strip()]
            if value.strip()
            else []
        )

    if isinstance(value, (list, tuple, set)):
        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    return []


def _normalize_enum_list(
    value: Any,
    enum_type: Any,
) -> List[Any]:
    if value is None:
        return []

    values = (
        [value]
        if not isinstance(value, (list, tuple, set))
        else value
    )

    result = []

    for item in values:
        enum_value = _stock_enum(
            item,
            enum_type,
            enum_type.UNKNOWN,
        )

        if enum_value != enum_type.UNKNOWN:
            result.append(enum_value)

    return result


def normalize_stock_filter(
    value: Any = None,
) -> StockScannerFilter:
    if isinstance(value, StockScannerFilter):
        return value

    if not isinstance(value, dict):
        return StockScannerFilter()

    return StockScannerFilter(
        market_ids=_normalize_string_list(
            value.get("market_ids")
        ),
        exchange_names=_normalize_string_list(
            value.get("exchange_names")
        ),
        instrument_ids=_normalize_string_list(
            value.get("instrument_ids")
        ),
        symbols=_normalize_string_list(
            value.get("symbols")
        ),
        sectors=_normalize_string_list(
            value.get("sectors")
        ),
        industries=_normalize_string_list(
            value.get("industries")
        ),
        states=_normalize_enum_list(
            value.get("states"),
            StockOpportunityState,
        ),
        biases=_normalize_enum_list(
            value.get("biases"),
            StockOpportunityBias,
        ),
        strengths=_normalize_enum_list(
            value.get("strengths"),
            StockOpportunityStrength,
        ),
        favorites_only=_stock_bool(
            value.get("favorites_only")
        ),
        watchlist_only=_stock_bool(
            value.get("watchlist_only")
        ),
        include_invalidated=_stock_bool(
            value.get("include_invalidated")
        ),
        include_expired=_stock_bool(
            value.get("include_expired")
        ),
        metadata=dict(value.get("metadata") or {}),
    )


def normalize_stock_request(
    request: Any = None,
) -> StockScannerRequest:
    if isinstance(request, StockScannerRequest):
        request.scanner_filter = normalize_stock_filter(
            request.scanner_filter
        )
        return request

    if not isinstance(request, dict):
        return StockScannerRequest()

    return StockScannerRequest(
        mode=_stock_enum(
            request.get("mode"),
            StockScannerMode,
            StockScannerMode.UNIVERSAL_STOCKS,
        ),
        markets=[
            normalize_stock_market(item)
            for item in request.get("markets", [])
        ],
        instruments=[
            normalize_stock_instrument(item)
            for item in request.get("instruments", [])
        ],
        opportunities=[
            normalize_upstream_stock_opportunity(item)
            for item in request.get("opportunities", [])
        ],
        scanner_filter=normalize_stock_filter(
            request.get("scanner_filter")
        ),
        authenticated=_stock_bool(
            request.get("authenticated")
        ),
        metadata=dict(request.get("metadata") or {}),
    )


def _stock_matches_list(
    value: str,
    allowed: List[str],
) -> bool:
    if not allowed:
        return True

    normalized_value = _stock_text(value).upper()

    return any(
        normalized_value == _stock_text(item).upper()
        for item in allowed
    )


def _stock_matches_enum_list(
    value: Any,
    allowed: List[Any],
) -> bool:
    if not allowed:
        return True

    return value in allowed


def stock_opportunity_matches_filter(
    opportunity: UpstreamStockOpportunity,
    scanner_filter: StockScannerFilter,
) -> bool:

    if not _stock_matches_list(
        opportunity.market_id,
        scanner_filter.market_ids,
    ):
        return False

    if not _stock_matches_list(
        opportunity.exchange,
        scanner_filter.exchange_names,
    ):
        return False

    if not _stock_matches_list(
        opportunity.instrument_id,
        scanner_filter.instrument_ids,
    ):
        return False

    if not _stock_matches_list(
        opportunity.symbol,
        scanner_filter.symbols,
    ):
        return False

    if not _stock_matches_list(
        opportunity.sector,
        scanner_filter.sectors,
    ):
        return False

    if not _stock_matches_list(
        opportunity.industry,
        scanner_filter.industries,
    ):
        return False

    if not _stock_matches_enum_list(
        opportunity.state,
        scanner_filter.states,
    ):
        return False

    if not _stock_matches_enum_list(
        opportunity.bias,
        scanner_filter.biases,
    ):
        return False

    if not _stock_matches_enum_list(
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
        opportunity.state
        == StockOpportunityState.INVALIDATED
        and not scanner_filter.include_invalidated
    ):
        return False

    if (
        opportunity.state
        == StockOpportunityState.EXPIRED
        and not scanner_filter.include_expired
    ):
        return False

    return True


def filter_upstream_stock_opportunities(
    opportunities: List[UpstreamStockOpportunity],
    scanner_filter: StockScannerFilter,
) -> List[UpstreamStockOpportunity]:

    return [
        opportunity
        for opportunity in opportunities
        if stock_opportunity_matches_filter(
            opportunity,
            scanner_filter,
        )
    ]


def filter_stock_markets(
    markets: List[StockMarketInput],
    scanner_filter: StockScannerFilter,
) -> List[StockMarketInput]:

    result = []

    for market in markets:
        if not market.enabled:
            continue

        if scanner_filter.market_ids:
            if not _stock_matches_list(
                market.market_id,
                scanner_filter.market_ids,
            ):
                continue

        if scanner_filter.exchange_names:
            if not _stock_matches_list(
                market.exchange,
                scanner_filter.exchange_names,
            ):
                continue

        result.append(market)

    return result


def filter_stock_instruments(
    instruments: List[StockInstrumentInput],
    scanner_filter: StockScannerFilter,
) -> List[StockInstrumentInput]:

    result = []

    for instrument in instruments:
        if not instrument.enabled:
            continue

        if scanner_filter.instrument_ids:
            if not _stock_matches_list(
                instrument.instrument_id,
                scanner_filter.instrument_ids,
            ):
                continue

        if scanner_filter.symbols:
            if not _stock_matches_list(
                instrument.symbol,
                scanner_filter.symbols,
            ):
                continue

        if scanner_filter.market_ids:
            if not _stock_matches_list(
                instrument.market_id,
                scanner_filter.market_ids,
            ):
                continue

        if scanner_filter.exchange_names:
            if not _stock_matches_list(
                instrument.exchange,
                scanner_filter.exchange_names,
            ):
                continue

        if scanner_filter.sectors:
            if not _stock_matches_list(
                instrument.sector,
                scanner_filter.sectors,
            ):
                continue

        if scanner_filter.industries:
            if not _stock_matches_list(
                instrument.industry,
                scanner_filter.industries,
            ):
                continue

        result.append(instrument)

    return result


def convert_upstream_stock_opportunity(
    value: Any,
) -> StockScannerOpportunity:

    opportunity = normalize_upstream_stock_opportunity(
        value
    )

    metadata = dict(opportunity.metadata)

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

    return StockScannerOpportunity(
        opportunity_id=opportunity.opportunity_id,
        symbol=opportunity.symbol,
        instrument_id=opportunity.instrument_id,
        instrument_name=opportunity.instrument_name,
        market_id=opportunity.market_id,
        exchange=opportunity.exchange,
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


def build_stock_scanner_result(
    request: StockScannerRequest,
    filtered_opportunities: List[
        UpstreamStockOpportunity
    ],
    status: StockScannerStatus = StockScannerStatus.READY,
    source_available: bool = True,
    source_errors: Optional[List[str]] = None,
    warnings: Optional[List[str]] = None,
) -> StockScannerResult:

    opportunities = [
        convert_upstream_stock_opportunity(item)
        for item in filtered_opportunities
    ]

    return StockScannerResult(
        status=status,
        mode=request.mode,
        opportunities=opportunities,
        total_input_opportunities=len(
            request.opportunities
        ),
        total_output_opportunities=len(
            opportunities
        ),
        source_available=source_available,
        source_errors=list(source_errors or []),
        warnings=list(warnings or []),
        generated_at=_stock_now(),
        metadata={
            "upstream_truth_consumed": True,
            "scanner_generated_intelligence": False,
            "scanner_generated_score": False,
            "scanner_generated_decision": False,
            "d13_modification": False,
            "risk_generation": False,
            "risk_override": False,
            "cas_generation": False,
            "cas_bypass": False,
            "execution": False,
            "upstream_mutation": False,
        },
    )


def stock_scanner_source_status(
    request: StockScannerRequest,
) -> StockScannerStatus:

    if not request.authenticated:
        return StockScannerStatus.BLOCKED

    if not request.opportunities:
        return StockScannerStatus.DEGRADED

    return StockScannerStatus.READY
# ============================================================
# ROBOMLM_PLUS — STOCK DISCOVERY SCANNER
# PART 3 — ORCHESTRATION / CONTROLLER / STATE
# ============================================================


@dataclass
class StockScannerState:
    initialized: bool = False
    ready: bool = False
    authenticated: bool = False

    status: StockScannerStatus = StockScannerStatus.IDLE
    mode: StockScannerMode = StockScannerMode.UNIVERSAL_STOCKS

    request_count: int = 0
    scan_count: int = 0

    last_error: str = ""
    last_scan_at: str = ""

    metadata: Dict[str, Any] = field(default_factory=dict)


def create_stock_scanner_state(
    authenticated: bool = False,
    mode: StockScannerMode = (
        StockScannerMode.UNIVERSAL_STOCKS
    ),
) -> StockScannerState:

    return StockScannerState(
        initialized=False,
        ready=False,
        authenticated=_stock_bool(authenticated),
        status=StockScannerStatus.IDLE,
        mode=_stock_enum(
            mode,
            StockScannerMode,
            StockScannerMode.UNIVERSAL_STOCKS,
        ),
    )


def normalize_stock_scanner_state(
    value: Any = None,
) -> StockScannerState:

    if isinstance(value, StockScannerState):
        return value

    if not isinstance(value, dict):
        return create_stock_scanner_state()

    return StockScannerState(
        initialized=_stock_bool(
            value.get("initialized")
        ),
        ready=_stock_bool(
            value.get("ready")
        ),
        authenticated=_stock_bool(
            value.get("authenticated")
        ),
        status=_stock_enum(
            value.get("status"),
            StockScannerStatus,
            StockScannerStatus.IDLE,
        ),
        mode=_stock_enum(
            value.get("mode"),
            StockScannerMode,
            StockScannerMode.UNIVERSAL_STOCKS,
        ),
        request_count=max(
            0,
            int(
                _stock_float(
                    value.get("request_count"),
                    0,
                )
            ),
        ),
        scan_count=max(
            0,
            int(
                _stock_float(
                    value.get("scan_count"),
                    0,
                )
            ),
        ),
        last_error=_stock_text(
            value.get("last_error")
        ),
        last_scan_at=_stock_text(
            value.get("last_scan_at")
        ),
        metadata=dict(
            value.get("metadata") or {}
        ),
    )


def run_stock_scanner(
    request: Any = None,
) -> StockScannerResult:
    """
    Execute stock discovery filtering/orchestration.

    The stock scanner consumes upstream opportunity truth.
    It does not generate intelligence, scores, decisions,
    D13 output, risk, CAS or execution instructions.
    """

    normalized = normalize_stock_request(request)

    if not normalized.authenticated:
        return build_stock_scanner_result(
            normalized,
            [],
            status=StockScannerStatus.BLOCKED,
            source_available=False,
            source_errors=[
                "Stock scanner access requires authentication."
            ],
            warnings=[],
        )

    markets = filter_stock_markets(
        normalized.markets,
        normalized.scanner_filter,
    )

    instruments = filter_stock_instruments(
        normalized.instruments,
        normalized.scanner_filter,
    )

    opportunities = (
        filter_upstream_stock_opportunities(
            normalized.opportunities,
            normalized.scanner_filter,
        )
    )

    source_status = stock_scanner_source_status(
        normalized
    )

    warnings: List[str] = []

    if (
        normalized.opportunities
        and not opportunities
    ):
        warnings.append(
            "No upstream stock opportunities matched "
            "the active scanner filters."
        )

    if normalized.markets and not markets:
        warnings.append(
            "No enabled stock markets matched "
            "the active scanner filters."
        )

    if normalized.instruments and not instruments:
        warnings.append(
            "No enabled stock instruments matched "
            "the active scanner filters."
        )

    if source_status == StockScannerStatus.DEGRADED:
        return build_stock_scanner_result(
            normalized,
            opportunities,
            status=StockScannerStatus.DEGRADED,
            source_available=False,
            source_errors=[
                "Upstream stock opportunity source "
                "is unavailable."
            ],
            warnings=warnings,
        )

    return build_stock_scanner_result(
        normalized,
        opportunities,
        status=StockScannerStatus.READY,
        source_available=True,
        source_errors=[],
        warnings=warnings,
    )


class StockScannerController:
    """
    Application controller for the Stock Scanner.

    Owns:
    - scanner state
    - request lifecycle
    - scan lifecycle
    - stock discovery filtering
    - result exposure

    Does NOT own:
    - market intelligence
    - evidence generation
    - decision generation
    - D13
    - risk
    - CAS
    - execution
    - order authority
    - position authority
    """

    def __init__(
        self,
        state: Optional[StockScannerState] = None,
    ):
        self._state = normalize_stock_scanner_state(
            state
        )

        self._last_request: Optional[
            StockScannerRequest
        ] = None

        self._last_result: Optional[
            StockScannerResult
        ] = None

        self._request_history: List[
            StockScannerRequest
        ] = []

        self._result_history: List[
            StockScannerResult
        ] = []

    @property
    def state(self) -> StockScannerState:
        return self._state

    @property
    def status(self) -> StockScannerStatus:
        return self._state.status

    @property
    def mode(self) -> StockScannerMode:
        return self._state.mode

    @property
    def authenticated(self) -> bool:
        return self._state.authenticated

    @property
    def last_request(
        self,
    ) -> Optional[StockScannerRequest]:
        return self._last_request

    @property
    def last_result(
        self,
    ) -> Optional[StockScannerResult]:
        return self._last_result

    def initialize(
        self,
        request: Any = None,
    ) -> StockScannerResult:

        normalized = normalize_stock_request(
            request
        )

        self._state.initialized = True
        self._state.ready = False
        self._state.status = (
            StockScannerStatus.LOADING
        )
        self._state.authenticated = (
            normalized.authenticated
        )
        self._state.mode = normalized.mode
        self._state.request_count += 1

        self._last_request = normalized

        self._request_history.append(
            normalized
        )
        self._request_history = (
            self._request_history[-500:]
        )

        result = run_stock_scanner(
            normalized
        )

        self._last_result = result

        self._result_history.append(
            result
        )
        self._result_history = (
            self._result_history[-500:]
        )

        self._state.status = result.status

        self._state.ready = result.status in {
            StockScannerStatus.READY,
            StockScannerStatus.DEGRADED,
        }

        self._state.last_scan_at = (
            result.generated_at
        )

        self._state.last_error = (
            result.source_errors[-1]
            if result.source_errors
            else ""
        )

        self._state.scan_count += 1

        return result

    def scan(
        self,
        request: Any = None,
    ) -> StockScannerResult:

        if request is None:
            request = self._last_request

        if request is None:
            request = StockScannerRequest(
                mode=self._state.mode,
                authenticated=self._state.authenticated,
            )

        return self.initialize(request)

    def set_mode(
        self,
        mode: StockScannerMode,
    ) -> StockScannerState:

        self._state.mode = _stock_enum(
            mode,
            StockScannerMode,
            StockScannerMode.UNIVERSAL_STOCKS,
        )

        return self._state

    def set_authenticated(
        self,
        authenticated: bool,
    ) -> StockScannerState:

        self._state.authenticated = (
            _stock_bool(authenticated)
        )

        if not self._state.authenticated:
            self._state.ready = False
            self._state.status = (
                StockScannerStatus.BLOCKED
            )

        return self._state

    def block(self) -> StockScannerState:

        self._state.status = (
            StockScannerStatus.BLOCKED
        )
        self._state.ready = False

        return self._state

    def reset(self) -> StockScannerState:

        self._state = create_stock_scanner_state(
            authenticated=self._state.authenticated,
            mode=self._state.mode,
        )

        self._last_request = None
        self._last_result = None

        self._request_history.clear()
        self._result_history.clear()

        return self._state

    def snapshot(self) -> StockScannerSnapshot:

        request = (
            self._last_request
            or StockScannerRequest(
                mode=self._state.mode,
                authenticated=self._state.authenticated,
            )
        )

        result = (
            self._last_result
            or StockScannerResult(
                status=self._state.status,
                mode=self._state.mode,
                generated_at=_stock_now(),
            )
        )

        return StockScannerSnapshot(
            request=request,
            result=result,
            captured_at=_stock_now(),
            metadata={
                "ui_only": True,
                "stock_scanner": True,
                "upstream_truth_consumed": True,
                "scanner_generated_intelligence": False,
                "scanner_generated_score": False,
                "scanner_generated_decision": False,
                "d13_modified": False,
                "risk_generated": False,
                "risk_overridden": False,
                "cas_bypassed": False,
                "execution_authority": False,
                "order_mutation": False,
                "position_mutation": False,
                "upstream_mutation": False,
            },
        )

    def request_history(
        self,
    ) -> List[StockScannerRequest]:
        return list(self._request_history)

    def result_history(
        self,
    ) -> List[StockScannerResult]:
        return list(self._result_history)


_DEFAULT_STOCK_SCANNER = StockScannerController()


def get_stock_scanner() -> StockScannerController:
    return _DEFAULT_STOCK_SCANNER


def create_stock_scanner(
    authenticated: bool = False,
    mode: StockScannerMode = (
        StockScannerMode.UNIVERSAL_STOCKS
    ),
) -> StockScannerController:

    return StockScannerController(
        create_stock_scanner_state(
            authenticated=authenticated,
            mode=mode,
        )
    )


def scan_stock_market(
    request: Any = None,
) -> StockScannerResult:
    return run_stock_scanner(request)


def scan_with_stock_scanner(
    request: Any = None,
) -> StockScannerResult:
    return get_stock_scanner().scan(request)
# ============================================================
# ROBOMLM_PLUS — STOCK DISCOVERY SCANNER
# PART 4 — SERIALIZATION / VALIDATION / HEALTH
# ============================================================


def _serialize_stock_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, list):
        return [
            _serialize_stock_value(item)
            for item in value
        ]

    if isinstance(value, tuple):
        return [
            _serialize_stock_value(item)
            for item in value
        ]

    if isinstance(value, dict):
        return {
            str(key): _serialize_stock_value(item)
            for key, item in value.items()
        }

    if hasattr(value, "__dataclass_fields__"):
        return {
            key: _serialize_stock_value(
                getattr(value, key)
            )
            for key in value.__dataclass_fields__
        }

    return value


def serialize_stock_market(
    value: StockMarketInput,
) -> Dict[str, Any]:
    return _serialize_stock_value(value)


def serialize_stock_instrument(
    value: StockInstrumentInput,
) -> Dict[str, Any]:
    return _serialize_stock_value(value)


def serialize_upstream_stock_opportunity(
    value: UpstreamStockOpportunity,
) -> Dict[str, Any]:
    return _serialize_stock_value(value)


def serialize_stock_filter(
    value: StockScannerFilter,
) -> Dict[str, Any]:
    return _serialize_stock_value(value)


def serialize_stock_scanner_opportunity(
    value: StockScannerOpportunity,
) -> Dict[str, Any]:
    return _serialize_stock_value(value)


def serialize_stock_scanner_result(
    value: StockScannerResult,
) -> Dict[str, Any]:
    return _serialize_stock_value(value)


def serialize_stock_scanner_request(
    value: StockScannerRequest,
) -> Dict[str, Any]:
    return _serialize_stock_value(value)


def serialize_stock_scanner_state(
    value: StockScannerState,
) -> Dict[str, Any]:
    return _serialize_stock_value(value)


def serialize_stock_scanner_snapshot(
    value: StockScannerSnapshot,
) -> Dict[str, Any]:
    return _serialize_stock_value(value)


def validate_stock_market(
    value: StockMarketInput,
) -> List[str]:

    errors: List[str] = []

    if not _stock_text(value.market_id):
        errors.append("market_id is required.")

    if not _stock_text(value.market_name):
        errors.append("market_name is required.")

    return errors


def validate_stock_instrument(
    value: StockInstrumentInput,
) -> List[str]:

    errors: List[str] = []

    if not _stock_text(value.instrument_id):
        errors.append("instrument_id is required.")

    if not _stock_text(value.symbol):
        errors.append("symbol is required.")

    return errors


def validate_upstream_stock_opportunity(
    value: UpstreamStockOpportunity,
) -> List[str]:

    errors: List[str] = []

    if not _stock_text(value.opportunity_id):
        errors.append(
            "opportunity_id is required."
        )

    if not _stock_text(value.symbol):
        errors.append("symbol is required.")

    try:
        confidence = float(value.confidence)
    except (TypeError, ValueError):
        confidence = -1.0

    if not 0.0 <= confidence <= 1.0:
        errors.append(
            "confidence must be between 0 and 1."
        )

    if value.source == StockSourceType.UNKNOWN:
        errors.append(
            "source must identify an upstream source."
        )

    return errors


def validate_stock_filter(
    value: StockScannerFilter,
) -> List[str]:

    errors: List[str] = []

    list_fields = (
        "market_ids",
        "exchange_names",
        "instrument_ids",
        "symbols",
        "sectors",
        "industries",
        "states",
        "biases",
        "strengths",
    )

    for field_name in list_fields:
        if not isinstance(
            getattr(value, field_name),
            list,
        ):
            errors.append(
                f"{field_name} must be a list."
            )

    return errors


def validate_stock_scanner_opportunity(
    value: StockScannerOpportunity,
) -> List[str]:

    errors: List[str] = []

    if not _stock_text(value.opportunity_id):
        errors.append(
            "opportunity_id is required."
        )

    if not _stock_text(value.symbol):
        errors.append("symbol is required.")

    try:
        confidence = float(value.confidence)
    except (TypeError, ValueError):
        confidence = -1.0

    if not 0.0 <= confidence <= 1.0:
        errors.append(
            "confidence must be between 0 and 1."
        )

    if value.source == StockSourceType.UNKNOWN:
        errors.append(
            "source must identify an upstream source."
        )

    forbidden_truth_flags = {
        "scanner_generated_intelligence",
        "scanner_generated_score",
        "scanner_generated_decision",
        "d13_modified",
        "risk_generated",
        "risk_overridden",
        "cas_bypassed",
        "execution_authority",
    }

    for key in forbidden_truth_flags:
        if value.metadata.get(key, False):
            errors.append(
                f"Forbidden scanner flag is True: {key}"
            )

    if value.metadata.get("upstream_truth") is not True:
        errors.append(
            "Scanner opportunity must preserve "
            "upstream_truth=True."
        )

    return errors


def validate_stock_scanner_request(
    value: StockScannerRequest,
) -> List[str]:

    errors: List[str] = []

    errors.extend(
        validate_stock_filter(
            value.scanner_filter
        )
    )

    for market in value.markets:
        errors.extend(
            validate_stock_market(market)
        )

    for instrument in value.instruments:
        errors.extend(
            validate_stock_instrument(instrument)
        )

    for opportunity in value.opportunities:
        errors.extend(
            validate_upstream_stock_opportunity(
                opportunity
            )
        )

    return errors


def validate_stock_scanner_result(
    value: StockScannerResult,
) -> List[str]:

    errors: List[str] = []

    if value.total_input_opportunities < 0:
        errors.append(
            "total_input_opportunities "
            "cannot be negative."
        )

    if value.total_output_opportunities < 0:
        errors.append(
            "total_output_opportunities "
            "cannot be negative."
        )

    if (
        value.total_output_opportunities
        != len(value.opportunities)
    ):
        errors.append(
            "total_output_opportunities must match "
            "opportunities length."
        )

    if (
        value.total_output_opportunities
        > value.total_input_opportunities
    ):
        errors.append(
            "Output opportunities cannot exceed "
            "input opportunities."
        )

    for opportunity in value.opportunities:
        errors.extend(
            validate_stock_scanner_opportunity(
                opportunity
            )
        )

    return errors


def validate_stock_scanner_state(
    value: StockScannerState,
) -> List[str]:

    errors: List[str] = []

    if value.request_count < 0:
        errors.append(
            "request_count cannot be negative."
        )

    if value.scan_count < 0:
        errors.append(
            "scan_count cannot be negative."
        )

    if (
        value.status == StockScannerStatus.READY
        and not value.ready
    ):
        errors.append(
            "READY scanner must have ready=True."
        )

    if (
        value.status
        == StockScannerStatus.BLOCKED
        and value.ready
    ):
        errors.append(
            "BLOCKED scanner cannot have ready=True."
        )

    if (
        value.mode
        == StockScannerMode.UNKNOWN
    ):
        errors.append(
            "Scanner mode cannot be UNKNOWN."
        )

    return errors


def validate_stock_scanner_snapshot(
    value: StockScannerSnapshot,
) -> List[str]:

    errors: List[str] = []

    errors.extend(
        validate_stock_scanner_request(
            value.request
        )
    )

    errors.extend(
        validate_stock_scanner_result(
            value.result
        )
    )

    if not _stock_text(value.captured_at):
        errors.append(
            "captured_at is required."
        )

    metadata = value.metadata

    if metadata.get(
        "scanner_generated_intelligence",
        False,
    ):
        errors.append(
            "Snapshot cannot contain "
            "scanner-generated intelligence."
        )

    if metadata.get(
        "scanner_generated_score",
        False,
    ):
        errors.append(
            "Snapshot cannot contain "
            "scanner-generated score."
        )

    if metadata.get(
        "scanner_generated_decision",
        False,
    ):
        errors.append(
            "Snapshot cannot contain "
            "scanner-generated decision."
        )

    return errors


def validate_stock_scanner_authority(
    value: Optional[Dict[str, Any]] = None,
) -> List[str]:

    authority = (
        value
        or STOCK_SCANNER_AUTHORITY
    )

    errors: List[str] = []

    forbidden = {
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
    }

    for key in forbidden:
        if authority.get(key) is not False:
            errors.append(
                "Forbidden authority must remain "
                f"False: {key}"
            )

    return errors


@dataclass
class StockScannerHealth:
    status: StockScannerStatus

    initialized: bool
    ready: bool
    authenticated: bool

    request_count: int
    scan_count: int

    last_error: str = ""

    checks: Dict[str, bool] = field(
        default_factory=dict
    )

    warnings: List[str] = field(
        default_factory=list
    )

    errors: List[str] = field(
        default_factory=list
    )

    generated_at: str = ""


def build_stock_scanner_health(
    scanner: Optional[
        StockScannerController
    ] = None,
) -> StockScannerHealth:

    controller = (
        scanner
        or get_stock_scanner()
    )

    state = controller.state

    checks = {
        "state_valid": not validate_stock_scanner_state(
            state
        ),
        "authority_valid": not validate_stock_scanner_authority(),
        "status_known": (
            state.status
            != StockScannerStatus.UNKNOWN
        ),
        "mode_known": (
            state.mode
            != StockScannerMode.UNKNOWN
        ),
    }

    errors: List[str] = []

    for name, passed in checks.items():
        if not passed:
            errors.append(
                f"Health check failed: {name}"
            )

    warnings: List[str] = []

    if not state.authenticated:
        warnings.append(
            "Stock scanner is not authenticated."
        )

    if (
        state.status
        == StockScannerStatus.DEGRADED
    ):
        warnings.append(
            "Upstream stock opportunity "
            "source is degraded."
        )

    return StockScannerHealth(
        status=state.status,
        initialized=state.initialized,
        ready=state.ready,
        authenticated=state.authenticated,
        request_count=state.request_count,
        scan_count=state.scan_count,
        last_error=state.last_error,
        checks=checks,
        warnings=warnings,
        errors=errors,
        generated_at=_stock_now(),
    )


def serialize_stock_scanner_health(
    value: StockScannerHealth,
) -> Dict[str, Any]:

    return _serialize_stock_value(value)


def stock_scanner_operational_check(
    scanner: Optional[
        StockScannerController
    ] = None,
) -> Dict[str, Any]:

    health = build_stock_scanner_health(
        scanner
    )

    operational = (
        not health.errors
        and all(health.checks.values())
    )

    return {
        "engine": STOCK_SCANNER_ENGINE,
        "version": STOCK_SCANNER_VERSION,
        "name": STOCK_SCANNER_NAME,
        "operational": operational,
        "status": health.status.value,
        "initialized": health.initialized,
        "ready": health.ready,
        "authenticated": health.authenticated,
        "checks": health.checks,
        "errors": health.errors,
        "warnings": health.warnings,
        "authority": dict(
            STOCK_SCANNER_AUTHORITY
        ),
        "generated_at": health.generated_at,
    }
# ============================================================
# ROBOMLM_PLUS — STOCK DISCOVERY SCANNER
# PART 5 — DIAGNOSTICS / CONTRACT / SELF-CHECK / EXPORTS
# ============================================================

def diagnose_stock_scanner(
    scanner: Optional["StockScannerController"] = None,
) -> Dict[str, Any]:
    controller = scanner or get_stock_scanner()
    state = controller.state
    result = controller.last_result

    issues: List[str] = []
    warnings: List[str] = []

    state_valid = validate_stock_scanner_state(state)
    authority_valid = validate_stock_scanner_authority(STOCK_SCANNER_AUTHORITY)

    if not state_valid:
        issues.append("Stock scanner state validation failed.")
    if not authority_valid:
        issues.append("Stock scanner authority validation failed.")

    if not state.authenticated:
        warnings.append("Scanner session is not authenticated.")
    if state.status == StockScannerStatus.DEGRADED:
        warnings.append("Stock opportunity source is degraded.")
    if state.status == StockScannerStatus.ERROR:
        issues.append(state.last_error or "Stock scanner is in ERROR state.")

    result_valid = True
    if result is not None:
        result_valid = validate_stock_scanner_result(result)
        if not result_valid:
            issues.append("Last stock scanner result validation failed.")

    return {
        "engine": STOCK_SCANNER_ENGINE,
        "version": STOCK_SCANNER_VERSION,
        "status": state.status.value,
        "mode": state.mode.value,
        "initialized": state.initialized,
        "ready": state.ready,
        "authenticated": state.authenticated,
        "request_count": state.request_count,
        "scan_count": state.scan_count,
        "last_error": state.last_error,
        "state_valid": state_valid,
        "result_valid": result_valid,
        "authority_valid": authority_valid,
        "issues": issues,
        "warnings": warnings,
        "healthy": not issues,
        "critical_scanner": True,
        "individual_equity_first_class": True,
    }


def stock_scanner_summary(
    scanner: Optional["StockScannerController"] = None,
) -> Dict[str, Any]:
    controller = scanner or get_stock_scanner()
    state = controller.state
    result = controller.last_result

    return {
        "engine": STOCK_SCANNER_ENGINE,
        "version": STOCK_SCANNER_VERSION,
        "name": STOCK_SCANNER_NAME,
        "title": STOCK_SCANNER_TITLE,
        "status": state.status.value,
        "mode": state.mode.value,
        "authenticated": state.authenticated,
        "initialized": state.initialized,
        "ready": state.ready,
        "request_count": state.request_count,
        "scan_count": state.scan_count,
        "input_opportunities": (
            result.total_input_opportunities if result else 0
        ),
        "output_opportunities": (
            result.total_output_opportunities if result else 0
        ),
        "source_available": (
            result.source_available if result else False
        ),
        "critical_scanner": True,
        "supports_individual_equity_discovery": True,
        "supports_index_independent_markets": True,
    }


def stock_scanner_contract_manifest() -> Dict[str, Any]:
    return {
        "engine": STOCK_SCANNER_ENGINE,
        "version": STOCK_SCANNER_VERSION,
        "layer": "UI_PRESENTATION",
        "role": "STOCK_OPPORTUNITY_SCANNER",
        "importance": "CLASS_A_CRITICAL",
        "market_model": {
            "individual_equity_first_class": True,
            "index_dependency_required": False,
            "supports_index_light_markets": True,
            "supports_nepse_style_equity_discovery": True,
        },
        "inputs": [
            "UPSTREAM_STOCK_OPPORTUNITY_ENGINE_OUTPUT",
            "STOCK_MARKET_INPUT",
            "STOCK_INSTRUMENT_INPUT",
            "STOCK_SCANNER_FILTER",
            "WATCHLIST_SERVICE_OUTPUT",
            "FAVORITES_SERVICE_OUTPUT",
            "APPLICATION_SESSION_STATE",
        ],
        "processing": [
            "input_normalization",
            "market_filtering",
            "instrument_filtering",
            "exchange_filtering",
            "sector_filtering",
            "industry_filtering",
            "opportunity_state_filtering",
            "bias_filtering",
            "strength_filtering",
            "favorite_filtering",
            "watchlist_filtering",
            "upstream_opportunity_conversion",
            "result_construction",
            "validation",
            "diagnostics",
        ],
        "outputs": [
            "STOCK_SCANNER_RESULT",
            "STOCK_SCANNER_SNAPSHOT",
            "STOCK_SCANNER_STATE",
            "STOCK_SCANNER_HEALTH",
            "STOCK_SCANNER_DIAGNOSTICS",
        ],
        "authority_owners": [
            "MARKET_DATA_ENGINE",
            "EVIDENCE_CORTEX",
            "INTELLIGENCE_ENGINE",
            "OPPORTUNITY_ENGINE",
            "DECISION_CORTEX",
            "D13_DECISION_AUTHORITY",
            "RISK_ENGINE",
            "CAS",
            "EXECUTION_ENGINE",
            "ORDER_AUTHORITY",
            "POSITION_AUTHORITY",
            "PORTFOLIO_AUTHORITY",
        ],
        "scanner_forbidden": [
            "INTELLIGENCE_GENERATION",
            "SCORE_GENERATION",
            "DECISION_GENERATION",
            "D13_MODIFICATION",
            "RISK_GENERATION",
            "RISK_OVERRIDE",
            "CAS_BYPASS",
            "EXECUTION",
            "ORDER_MUTATION",
            "POSITION_MUTATION",
            "PORTFOLIO_MUTATION",
            "UPSTREAM_MUTATION",
        ],
        "truth_policy": {
            "upstream_truth_preserved": True,
            "scanner_generated_intelligence": False,
            "scanner_generated_score": False,
            "scanner_generated_decision": False,
            "d13_modified": False,
            "risk_generated": False,
            "risk_overridden": False,
            "cas_bypassed": False,
            "execution_authority": False,
        },
    }


def validate_stock_scanner_integrity(
    scanner: Optional["StockScannerController"] = None,
) -> bool:
    controller = scanner or get_stock_scanner()

    if not validate_stock_scanner_authority(STOCK_SCANNER_AUTHORITY):
        return False
    if not validate_stock_scanner_state(controller.state):
        return False

    if controller.last_request is not None:
        if not validate_stock_scanner_request(controller.last_request):
            return False

    if controller.last_result is not None:
        if not validate_stock_scanner_result(controller.last_result):
            return False

    return True


def validate_stock_scanner_contract() -> bool:
    manifest = stock_scanner_contract_manifest()

    required = {
        "layer": "UI_PRESENTATION",
        "role": "STOCK_OPPORTUNITY_SCANNER",
        "importance": "CLASS_A_CRITICAL",
    }

    for key, value in required.items():
        if manifest.get(key) != value:
            return False

    market_model = manifest.get("market_model", {})
    if not market_model.get("individual_equity_first_class"):
        return False
    if market_model.get("index_dependency_required"):
        return False

    truth = manifest.get("truth_policy", {})
    forbidden_truth_flags = (
        "scanner_generated_intelligence",
        "scanner_generated_score",
        "scanner_generated_decision",
        "d13_modified",
        "risk_generated",
        "risk_overridden",
        "cas_bypassed",
        "execution_authority",
    )

    if not truth.get("upstream_truth_preserved"):
        return False

    for flag in forbidden_truth_flags:
        if truth.get(flag):
            return False

    return True


def stock_scanner_module_check() -> Dict[str, Any]:
    contract_valid = validate_stock_scanner_contract()
    authority_valid = validate_stock_scanner_authority(
        STOCK_SCANNER_AUTHORITY
    )

    return {
        "engine": STOCK_SCANNER_ENGINE,
        "version": STOCK_SCANNER_VERSION,
        "contract_valid": contract_valid,
        "authority_valid": authority_valid,
        "critical_scanner": True,
        "individual_equity_first_class": True,
        "index_independent_market_support": True,
        "operational": contract_valid and authority_valid,
    }


def stock_scanner_self_check() -> Dict[str, Any]:
    scanner = create_stock_scanner()

    scanner.initialize()
    scanner.set_authenticated(True)

    opportunity = UpstreamStockOpportunity(
        opportunity_id="SELF_CHECK_STOCK_001",
        symbol="SELFTEST",
        instrument_id="SELFTEST_INSTRUMENT",
        instrument_name="Self Check Equity",
        market_id="SELFTEST_MARKET",
        exchange="SELFTEST_EXCHANGE",
        sector="TEST",
        industry="TEST",
        state=StockOpportunityState.QUALIFIED,
        bias=StockOpportunityBias.BULLISH,
        strength=StockOpportunityStrength.STRONG,
        summary="Stock scanner contract self-check opportunity.",
        confidence=0.90,
        timestamp=_stock_now(),
        source=StockSourceType.UPSTREAM_OPPORTUNITY_ENGINE,
    )

    request = StockScannerRequest(
        mode=StockScannerMode.UNIVERSAL_STOCKS,
        markets=[
            StockMarketInput(
                market_id="SELFTEST_MARKET",
                market_name="Self Test Equity Market",
                exchange="SELFTEST_EXCHANGE",
            )
        ],
        instruments=[
            StockInstrumentInput(
                instrument_id="SELFTEST_INSTRUMENT",
                symbol="SELFTEST",
                display_name="Self Check Equity",
                exchange="SELFTEST_EXCHANGE",
                market_id="SELFTEST_MARKET",
                sector="TEST",
                industry="TEST",
            )
        ],
        opportunities=[opportunity],
        authenticated=True,
    )

    result = scanner.scan(request)

    output_count_valid = result.total_output_opportunities == 1
    truth_preserved = False

    if result.opportunities:
        output = result.opportunities[0]
        truth_preserved = (
            output.metadata.get("upstream_truth") is True
            and output.metadata.get("scanner_generated_intelligence") is False
            and output.metadata.get("scanner_generated_score") is False
            and output.metadata.get("scanner_generated_decision") is False
            and output.metadata.get("d13_modified") is False
            and output.metadata.get("risk_generated") is False
            and output.metadata.get("risk_overridden") is False
            and output.metadata.get("cas_bypassed") is False
            and output.metadata.get("execution_authority") is False
        )

    integrity_valid = validate_stock_scanner_integrity(scanner)
    contract_valid = validate_stock_scanner_contract()

    passed = (
        result.status == StockScannerStatus.READY
        and output_count_valid
        and truth_preserved
        and integrity_valid
        and contract_valid
    )

    return {
        "engine": STOCK_SCANNER_ENGINE,
        "version": STOCK_SCANNER_VERSION,
        "passed": passed,
        "result_status": result.status.value,
        "output_count": result.total_output_opportunities,
        "output_count_valid": output_count_valid,
        "upstream_truth_preserved": truth_preserved,
        "integrity_valid": integrity_valid,
        "contract_valid": contract_valid,
        "critical_scanner": True,
        "individual_equity_first_class": True,
    }


def create_default_stock_scanner() -> "StockScannerController":
    return create_stock_scanner()


__all__ = [
    # constants
    "STOCK_SCANNER_ENGINE",
    "STOCK_SCANNER_VERSION",
    "STOCK_SCANNER_NAME",
    "STOCK_SCANNER_TITLE",
    "STOCK_SCANNER_DESCRIPTION",
    "STOCK_SCANNER_AUTHORITY",

    # enums
    "StockScannerStatus",
    "StockScannerMode",
    "StockOpportunityState",
    "StockOpportunityBias",
    "StockOpportunityStrength",
    "StockScannerPriority",
    "StockSourceType",

    # contracts
    "StockMarketInput",
    "StockInstrumentInput",
    "UpstreamStockOpportunity",
    "StockScannerFilter",
    "StockScannerOpportunity",
    "StockScannerResult",
    "StockScannerRequest",
    "StockScannerSnapshot",

    # normalization
    "normalize_stock_market",
    "normalize_stock_instrument",
    "normalize_upstream_stock_opportunity",
    "normalize_stock_filter",
    "normalize_stock_request",

    # filtering / conversion
    "stock_opportunity_matches_filter",
    "filter_upstream_stock_opportunities",
    "filter_stock_markets",
    "filter_stock_instruments",
    "convert_upstream_stock_opportunity",
    "build_stock_scanner_result",
    "stock_scanner_source_status",

    # state / controller
    "StockScannerState",
    "create_stock_scanner_state",
    "normalize_stock_scanner_state",
    "run_stock_scanner",
    "StockScannerController",
    "get_stock_scanner",
    "create_stock_scanner",
    "scan_stock_market",
    "scan_with_stock_scanner",

    # serialization
    "_serialize_stock_value",
    "serialize_stock_market",
    "serialize_stock_instrument",
    "serialize_upstream_stock_opportunity",
    "serialize_stock_filter",
    "serialize_stock_scanner_opportunity",
    "serialize_stock_scanner_result",
    "serialize_stock_scanner_request",
    "serialize_stock_scanner_state",
    "serialize_stock_scanner_snapshot",

    # validation / health
    "validate_stock_market",
    "validate_stock_instrument",
    "validate_upstream_stock_opportunity",
    "validate_stock_filter",
    "validate_stock_scanner_opportunity",
    "validate_stock_scanner_request",
    "validate_stock_scanner_result",
    "validate_stock_scanner_state",
    "validate_stock_scanner_snapshot",
    "validate_stock_scanner_authority",
    "StockScannerHealth",
    "build_stock_scanner_health",
    "serialize_stock_scanner_health",
    "stock_scanner_operational_check",

    # diagnostics / contract
    "diagnose_stock_scanner",
    "stock_scanner_summary",
    "stock_scanner_contract_manifest",
    "validate_stock_scanner_integrity",
    "validate_stock_scanner_contract",
    "stock_scanner_module_check",
    "stock_scanner_self_check",
    "create_default_stock_scanner",
]