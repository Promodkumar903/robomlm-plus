# app/ui/discovery/fx_scanner.py

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List


# ============================================================================
# FX SCANNER — CORE CONTRACT
# ============================================================================

FX_SCANNER_ENGINE = "ROBOMLM_PLUS_FX_SCANNER"
FX_SCANNER_VERSION = "1.0"
FX_SCANNER_NAME = "FX Opportunity Scanner"
FX_SCANNER_TITLE = "Foreign Exchange Opportunity Scanner"

FX_SCANNER_DESCRIPTION = (
    "Dedicated FX discovery scanner for presenting and routing "
    "upstream foreign-exchange opportunity intelligence across "
    "supported currency pairs, markets and trading sessions."
)


# ============================================================================
# AUTHORITY BOUNDARY
# ============================================================================

FX_SCANNER_AUTHORITY = {
    # Allowed scanner responsibilities
    "scanner_orchestration": True,
    "fx_opportunity_presentation": True,
    "market_filtering": True,
    "region_filtering": True,
    "session_filtering": True,
    "currency_filtering": True,
    "pair_filtering": True,
    "instrument_filtering": True,
    "quote_currency_filtering": True,
    "base_currency_filtering": True,
    "upstream_opportunity_consumption": True,
    "fx_specific_intelligence_consumption": True,

    # FX intelligence must remain upstream
    "fx_specific_algorithm_generation": False,
    "fx_signal_generation": False,
    "fx_score_generation": False,

    # Cross-scanner independence
    "equity_scanner_dependency": False,
    "equity_scanner_authority": False,
    "index_scanner_dependency": False,
    "index_scanner_authority": False,
    "commodity_scanner_dependency": False,
    "commodity_scanner_authority": False,
    "crypto_scanner_dependency": False,
    "crypto_scanner_authority": False,

    # Core intelligence / decision authority forbidden
    "market_data_generation": False,
    "evidence_generation": False,
    "intelligence_generation": False,
    "decision_generation": False,
    "d13_modification": False,

    # Risk / safety forbidden
    "risk_generation": False,
    "risk_override": False,
    "cas_generation": False,
    "cas_bypass": False,

    # Execution forbidden
    "execution": False,
    "order_authority": False,
    "order_mutation": False,
    "position_authority": False,
    "position_mutation": False,
    "portfolio_mutation": False,

    # Scanner itself must not fabricate opportunities
    "opportunity_generation": False,
    "scanner_intelligence_generation": False,
    "upstream_mutation": False,
}


# ============================================================================
# ENUMS
# ============================================================================


class FXScannerStatus(str, Enum):
    IDLE = "IDLE"
    LOADING = "LOADING"
    READY = "READY"
    DEGRADED = "DEGRADED"
    BLOCKED = "BLOCKED"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class FXScannerMode(str, Enum):
    UNIVERSAL_FX = "UNIVERSAL_FX"
    MARKET = "MARKET"
    REGION = "REGION"
    SESSION = "SESSION"
    CURRENCY = "CURRENCY"
    PAIR = "PAIR"
    QUOTE_CURRENCY = "QUOTE_CURRENCY"
    BASE_CURRENCY = "BASE_CURRENCY"
    FAVORITES = "FAVORITES"
    WATCHLIST = "WATCHLIST"
    UNKNOWN = "UNKNOWN"


class FXPairType(str, Enum):
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    CROSS = "CROSS"
    EXOTIC = "EXOTIC"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


class FXInstrumentType(str, Enum):
    SPOT = "SPOT"
    FORWARD = "FORWARD"
    FUTURE = "FUTURE"
    CFD = "CFD"
    OPTION = "OPTION"
    OTHER_DERIVATIVE = "OTHER_DERIVATIVE"
    UNKNOWN = "UNKNOWN"


class FXOpportunityState(str, Enum):
    UNKNOWN = "UNKNOWN"
    WATCH = "WATCH"
    DEVELOPING = "DEVELOPING"
    QUALIFIED = "QUALIFIED"
    INVALIDATED = "INVALIDATED"
    EXPIRED = "EXPIRED"


class FXOpportunityBias(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"


class FXOpportunityStrength(str, Enum):
    VERY_WEAK = "VERY_WEAK"
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    VERY_STRONG = "VERY_STRONG"
    UNKNOWN = "UNKNOWN"


class FXScannerPriority(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class FXSourceType(str, Enum):
    UPSTREAM_OPPORTUNITY_ENGINE = "UPSTREAM_OPPORTUNITY_ENGINE"
    FX_OPPORTUNITY_ENGINE = "FX_OPPORTUNITY_ENGINE"
    FX_INTELLIGENCE_ENGINE = "FX_INTELLIGENCE_ENGINE"
    DISCOVERY_ENGINE = "DISCOVERY_ENGINE"
    UNKNOWN = "UNKNOWN"


# ============================================================================
# NORMALIZATION HELPERS
# ============================================================================


def _fx_text(value: Any, default: str = "") -> str:
    if value is None:
        return default

    text = str(value).strip()

    return text if text else default


def _fx_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        normalized = value.strip().lower()

        if normalized in {"true", "1", "yes", "y", "on"}:
            return True

        if normalized in {"false", "0", "no", "n", "off"}:
            return False

    return bool(value)


def _fx_float(
    value: Any,
    default: float = 0.0,
) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _fx_enum(
    enum_type: type[Enum],
    value: Any,
    default: Enum,
) -> Enum:
    if isinstance(value, enum_type):
        return value

    text = _fx_text(value)

    if not text:
        return default

    normalized = text.upper()

    for member in enum_type:
        if member.value.upper() == normalized:
            return member

    return default


def _fx_now() -> datetime:
    return datetime.now(timezone.utc)


# ============================================================================
# MARKET INPUT
# ============================================================================


@dataclass
class FXMarketInput:
    market_id: str
    market_name: str

    country: str = ""
    region: str = ""
    timezone: str = ""

    enabled: bool = True
    selected: bool = False
    fx_available: bool = True

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# FX INSTRUMENT INPUT
# ============================================================================


@dataclass
class FXInstrumentInput:
    instrument_id: str
    symbol: str
    display_name: str = ""

    pair_type: FXPairType = FXPairType.UNKNOWN
    instrument_type: FXInstrumentType = FXInstrumentType.SPOT

    market_id: str = ""

    base_currency: str = ""
    quote_currency: str = ""

    country: str = ""
    region: str = ""
    exchange: str = ""

    session: str = ""

    enabled: bool = True
    selected: bool = False
    tradable: bool = True

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# UPSTREAM FX OPPORTUNITY
# ============================================================================


@dataclass
class UpstreamFXOpportunity:
    opportunity_id: str

    symbol: str
    instrument_id: str
    instrument_name: str = ""

    pair_type: FXPairType = FXPairType.UNKNOWN
    instrument_type: FXInstrumentType = FXInstrumentType.SPOT

    market_id: str = ""

    base_currency: str = ""
    quote_currency: str = ""

    country: str = ""
    region: str = ""
    exchange: str = ""

    session: str = ""

    state: FXOpportunityState = FXOpportunityState.UNKNOWN
    bias: FXOpportunityBias = FXOpportunityBias.UNKNOWN
    strength: FXOpportunityStrength = FXOpportunityStrength.UNKNOWN

    summary: str = ""
    confidence: float = 0.0

    timestamp: datetime = field(default_factory=_fx_now)

    favorite: bool = False
    watchlisted: bool = False

    priority: FXScannerPriority = FXScannerPriority.NORMAL

    source: FXSourceType = FXSourceType.UNKNOWN

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# FX SCANNER FILTER
# ============================================================================


@dataclass
class FXScannerFilter:
    market_ids: List[str] = field(default_factory=list)
    countries: List[str] = field(default_factory=list)
    regions: List[str] = field(default_factory=list)

    session_names: List[str] = field(default_factory=list)

    instrument_ids: List[str] = field(default_factory=list)
    symbols: List[str] = field(default_factory=list)

    pair_types: List[FXPairType] = field(default_factory=list)
    instrument_types: List[FXInstrumentType] = field(default_factory=list)

    base_currencies: List[str] = field(default_factory=list)
    quote_currencies: List[str] = field(default_factory=list)

    states: List[FXOpportunityState] = field(default_factory=list)
    biases: List[FXOpportunityBias] = field(default_factory=list)
    strengths: List[FXOpportunityStrength] = field(default_factory=list)

    favorites_only: bool = False
    watchlist_only: bool = False
    tradable_only: bool = False

    include_invalidated: bool = False
    include_expired: bool = False

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# ROUTED FX OPPORTUNITY
# ============================================================================


@dataclass
class FXScannerOpportunity:
    opportunity_id: str

    symbol: str
    instrument_id: str
    instrument_name: str = ""

    pair_type: FXPairType = FXPairType.UNKNOWN
    instrument_type: FXInstrumentType = FXInstrumentType.SPOT

    market_id: str = ""

    base_currency: str = ""
    quote_currency: str = ""

    country: str = ""
    region: str = ""
    exchange: str = ""

    session: str = ""

    state: FXOpportunityState = FXOpportunityState.UNKNOWN
    bias: FXOpportunityBias = FXOpportunityBias.UNKNOWN
    strength: FXOpportunityStrength = FXOpportunityStrength.UNKNOWN

    summary: str = ""
    confidence: float = 0.0

    timestamp: datetime = field(default_factory=_fx_now)

    favorite: bool = False
    watchlisted: bool = False

    priority: FXScannerPriority = FXScannerPriority.NORMAL

    source: FXSourceType = FXSourceType.UNKNOWN

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# FX SCANNER RESULT
# ============================================================================


@dataclass
class FXScannerResult:
    status: FXScannerStatus

    mode: FXScannerMode

    opportunities: List[FXScannerOpportunity] = field(
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

    generated_at: datetime = field(default_factory=_fx_now)

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# FX SCANNER REQUEST
# ============================================================================


@dataclass
class FXScannerRequest:
    mode: FXScannerMode = FXScannerMode.UNIVERSAL_FX

    markets: List[FXMarketInput] = field(
        default_factory=list
    )

    instruments: List[FXInstrumentInput] = field(
        default_factory=list
    )

    opportunities: List[UpstreamFXOpportunity] = field(
        default_factory=list
    )

    scanner_filter: FXScannerFilter = field(
        default_factory=FXScannerFilter
    )

    authenticated: bool = False

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# FX SCANNER SNAPSHOT
# ============================================================================


@dataclass
class FXScannerSnapshot:
    request: FXScannerRequest

    result: FXScannerResult

    captured_at: datetime = field(
        default_factory=_fx_now
    )

    metadata: Dict[str, Any] = field(default_factory=dict)
# app/ui/discovery/fx_scanner.py
# PART 2 — NORMALIZATION / FILTERING / UPSTREAM ROUTING

# ============================================================================
# NORMALIZATION
# ============================================================================


def normalize_fx_market(
    value: Any,
) -> FXMarketInput:
    if isinstance(value, FXMarketInput):
        return value

    data = value if isinstance(value, dict) else {}

    return FXMarketInput(
        market_id=_fx_text(data.get("market_id")),
        market_name=_fx_text(data.get("market_name")),
        country=_fx_text(data.get("country")),
        region=_fx_text(data.get("region")),
        timezone=_fx_text(data.get("timezone")),
        enabled=_fx_bool(data.get("enabled"), True),
        selected=_fx_bool(data.get("selected"), False),
        fx_available=_fx_bool(data.get("fx_available"), True),
        metadata=dict(data.get("metadata") or {}),
    )


def normalize_fx_instrument(
    value: Any,
) -> FXInstrumentInput:
    if isinstance(value, FXInstrumentInput):
        return value

    data = value if isinstance(value, dict) else {}

    return FXInstrumentInput(
        instrument_id=_fx_text(data.get("instrument_id")),
        symbol=_fx_text(data.get("symbol")),
        display_name=_fx_text(data.get("display_name")),

        pair_type=_fx_enum(
            FXPairType,
            data.get("pair_type"),
            FXPairType.UNKNOWN,
        ),

        instrument_type=_fx_enum(
            FXInstrumentType,
            data.get("instrument_type"),
            FXInstrumentType.SPOT,
        ),

        market_id=_fx_text(data.get("market_id")),

        base_currency=_fx_text(
            data.get("base_currency")
        ).upper(),

        quote_currency=_fx_text(
            data.get("quote_currency")
        ).upper(),

        country=_fx_text(data.get("country")),
        region=_fx_text(data.get("region")),
        exchange=_fx_text(data.get("exchange")),
        session=_fx_text(data.get("session")),

        enabled=_fx_bool(data.get("enabled"), True),
        selected=_fx_bool(data.get("selected"), False),
        tradable=_fx_bool(data.get("tradable"), True),

        metadata=dict(data.get("metadata") or {}),
    )


def normalize_upstream_fx_opportunity(
    value: Any,
) -> UpstreamFXOpportunity:
    if isinstance(value, UpstreamFXOpportunity):
        return value

    data = value if isinstance(value, dict) else {}

    timestamp = data.get("timestamp")

    if not isinstance(timestamp, datetime):
        timestamp = _fx_now()

    return UpstreamFXOpportunity(
        opportunity_id=_fx_text(
            data.get("opportunity_id")
        ),

        symbol=_fx_text(
            data.get("symbol")
        ),

        instrument_id=_fx_text(
            data.get("instrument_id")
        ),

        instrument_name=_fx_text(
            data.get("instrument_name")
        ),

        pair_type=_fx_enum(
            FXPairType,
            data.get("pair_type"),
            FXPairType.UNKNOWN,
        ),

        instrument_type=_fx_enum(
            FXInstrumentType,
            data.get("instrument_type"),
            FXInstrumentType.SPOT,
        ),

        market_id=_fx_text(
            data.get("market_id")
        ),

        base_currency=_fx_text(
            data.get("base_currency")
        ).upper(),

        quote_currency=_fx_text(
            data.get("quote_currency")
        ).upper(),

        country=_fx_text(
            data.get("country")
        ),

        region=_fx_text(
            data.get("region")
        ),

        exchange=_fx_text(
            data.get("exchange")
        ),

        session=_fx_text(
            data.get("session")
        ),

        state=_fx_enum(
            FXOpportunityState,
            data.get("state"),
            FXOpportunityState.UNKNOWN,
        ),

        bias=_fx_enum(
            FXOpportunityBias,
            data.get("bias"),
            FXOpportunityBias.UNKNOWN,
        ),

        strength=_fx_enum(
            FXOpportunityStrength,
            data.get("strength"),
            FXOpportunityStrength.UNKNOWN,
        ),

        summary=_fx_text(
            data.get("summary")
        ),

        confidence=max(
            0.0,
            min(
                1.0,
                _fx_float(
                    data.get("confidence"),
                    0.0,
                ),
            ),
        ),

        timestamp=timestamp,

        favorite=_fx_bool(
            data.get("favorite"),
            False,
        ),

        watchlisted=_fx_bool(
            data.get("watchlisted"),
            False,
        ),

        priority=_fx_enum(
            FXScannerPriority,
            data.get("priority"),
            FXScannerPriority.NORMAL,
        ),

        source=_fx_enum(
            FXSourceType,
            data.get("source"),
            FXSourceType.UNKNOWN,
        ),

        metadata=dict(
            data.get("metadata") or {}
        ),
    )


def _normalize_fx_string_list(
    values: Any,
    uppercase: bool = False,
) -> List[str]:
    if values is None:
        return []

    if isinstance(values, str):
        values = [values]

    if not isinstance(values, (list, tuple, set)):
        return []

    result: List[str] = []

    for value in values:
        text = _fx_text(value)

        if uppercase:
            text = text.upper()

        if text:
            result.append(text)

    return list(dict.fromkeys(result))


def _normalize_fx_enum_list(
    enum_type: type[Enum],
    values: Any,
) -> List[Enum]:
    if values is None:
        return []

    if isinstance(values, (str, enum_type)):
        values = [values]

    if not isinstance(values, (list, tuple, set)):
        return []

    result: List[Enum] = []

    for value in values:
        normalized = _fx_enum(
            enum_type,
            value,
            list(enum_type)[-1],
        )

        if normalized not in result:
            result.append(normalized)

    return result


def normalize_fx_filter(
    value: Any,
) -> FXScannerFilter:
    if isinstance(value, FXScannerFilter):
        return value

    data = value if isinstance(value, dict) else {}

    return FXScannerFilter(
        market_ids=_normalize_fx_string_list(
            data.get("market_ids")
        ),

        countries=_normalize_fx_string_list(
            data.get("countries")
        ),

        regions=_normalize_fx_string_list(
            data.get("regions")
        ),

        session_names=_normalize_fx_string_list(
            data.get("session_names")
        ),

        instrument_ids=_normalize_fx_string_list(
            data.get("instrument_ids")
        ),

        symbols=_normalize_fx_string_list(
            data.get("symbols")
        ),

        pair_types=_normalize_fx_enum_list(
            FXPairType,
            data.get("pair_types"),
        ),

        instrument_types=_normalize_fx_enum_list(
            FXInstrumentType,
            data.get("instrument_types"),
        ),

        base_currencies=_normalize_fx_string_list(
            data.get("base_currencies"),
            uppercase=True,
        ),

        quote_currencies=_normalize_fx_string_list(
            data.get("quote_currencies"),
            uppercase=True,
        ),

        states=_normalize_fx_enum_list(
            FXOpportunityState,
            data.get("states"),
        ),

        biases=_normalize_fx_enum_list(
            FXOpportunityBias,
            data.get("biases"),
        ),

        strengths=_normalize_fx_enum_list(
            FXOpportunityStrength,
            data.get("strengths"),
        ),

        favorites_only=_fx_bool(
            data.get("favorites_only"),
            False,
        ),

        watchlist_only=_fx_bool(
            data.get("watchlist_only"),
            False,
        ),

        tradable_only=_fx_bool(
            data.get("tradable_only"),
            False,
        ),

        include_invalidated=_fx_bool(
            data.get("include_invalidated"),
            False,
        ),

        include_expired=_fx_bool(
            data.get("include_expired"),
            False,
        ),

        metadata=dict(
            data.get("metadata") or {}
        ),
    )


def normalize_fx_request(
    value: Any,
) -> FXScannerRequest:
    if isinstance(value, FXScannerRequest):
        return value

    data = value if isinstance(value, dict) else {}

    markets = [
        normalize_fx_market(item)
        for item in data.get("markets", [])
    ]

    instruments = [
        normalize_fx_instrument(item)
        for item in data.get("instruments", [])
    ]

    opportunities = [
        normalize_upstream_fx_opportunity(item)
        for item in data.get("opportunities", [])
    ]

    return FXScannerRequest(
        mode=_fx_enum(
            FXScannerMode,
            data.get("mode"),
            FXScannerMode.UNIVERSAL_FX,
        ),

        markets=markets,

        instruments=instruments,

        opportunities=opportunities,

        scanner_filter=normalize_fx_filter(
            data.get("scanner_filter")
        ),

        authenticated=_fx_bool(
            data.get("authenticated"),
            False,
        ),

        metadata=dict(
            data.get("metadata") or {}
        ),
    )


# ============================================================================
# FILTER HELPERS
# ============================================================================


def _fx_matches_list(
    value: str,
    allowed: List[str],
    *,
    case_insensitive: bool = True,
) -> bool:
    if not allowed:
        return True

    if case_insensitive:
        target = value.upper()

        return any(
            target == item.upper()
            for item in allowed
        )

    return value in allowed


def _fx_matches_enum_list(
    value: Enum,
    allowed: List[Enum],
) -> bool:
    if not allowed:
        return True

    return value in allowed


# ============================================================================
# OPPORTUNITY FILTER
# ============================================================================


def fx_opportunity_matches_filter(
    opportunity: UpstreamFXOpportunity,
    scanner_filter: FXScannerFilter,
) -> bool:

    if (
        scanner_filter.market_ids
        and opportunity.market_id
        not in scanner_filter.market_ids
    ):
        return False

    if (
        scanner_filter.countries
        and not _fx_matches_list(
            opportunity.country,
            scanner_filter.countries,
        )
    ):
        return False

    if (
        scanner_filter.regions
        and not _fx_matches_list(
            opportunity.region,
            scanner_filter.regions,
        )
    ):
        return False

    if (
        scanner_filter.session_names
        and not _fx_matches_list(
            opportunity.session,
            scanner_filter.session_names,
        )
    ):
        return False

    if (
        scanner_filter.instrument_ids
        and opportunity.instrument_id
        not in scanner_filter.instrument_ids
    ):
        return False

    if (
        scanner_filter.symbols
        and not _fx_matches_list(
            opportunity.symbol,
            scanner_filter.symbols,
        )
    ):
        return False

    if not _fx_matches_enum_list(
        opportunity.pair_type,
        scanner_filter.pair_types,
    ):
        return False

    if not _fx_matches_enum_list(
        opportunity.instrument_type,
        scanner_filter.instrument_types,
    ):
        return False

    if (
        scanner_filter.base_currencies
        and opportunity.base_currency
        not in scanner_filter.base_currencies
    ):
        return False

    if (
        scanner_filter.quote_currencies
        and opportunity.quote_currency
        not in scanner_filter.quote_currencies
    ):
        return False

    if not _fx_matches_enum_list(
        opportunity.state,
        scanner_filter.states,
    ):
        return False

    if not _fx_matches_enum_list(
        opportunity.bias,
        scanner_filter.biases,
    ):
        return False

    if not _fx_matches_enum_list(
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
        scanner_filter.include_invalidated is False
        and opportunity.state
        == FXOpportunityState.INVALIDATED
    ):
        return False

    if (
        scanner_filter.include_expired is False
        and opportunity.state
        == FXOpportunityState.EXPIRED
    ):
        return False

    return True


# ============================================================================
# UPSTREAM OPPORTUNITY FILTER
# ============================================================================


def filter_upstream_fx_opportunities(
    opportunities: List[UpstreamFXOpportunity],
    scanner_filter: FXScannerFilter,
) -> List[UpstreamFXOpportunity]:

    normalized = [
        normalize_upstream_fx_opportunity(
            opportunity
        )
        for opportunity in opportunities
    ]

    return [
        opportunity
        for opportunity in normalized
        if fx_opportunity_matches_filter(
            opportunity,
            scanner_filter,
        )
    ]


# ============================================================================
# MARKET FILTER
# ============================================================================


def filter_fx_markets(
    markets: List[FXMarketInput],
    scanner_filter: FXScannerFilter,
) -> List[FXMarketInput]:

    normalized = [
        normalize_fx_market(market)
        for market in markets
    ]

    result: List[FXMarketInput] = []

    for market in normalized:

        if not market.enabled:
            continue

        if not market.fx_available:
            continue

        if (
            scanner_filter.market_ids
            and market.market_id
            not in scanner_filter.market_ids
        ):
            continue

        if (
            scanner_filter.countries
            and not _fx_matches_list(
                market.country,
                scanner_filter.countries,
            )
        ):
            continue

        if (
            scanner_filter.regions
            and not _fx_matches_list(
                market.region,
                scanner_filter.regions,
            )
        ):
            continue

        result.append(market)

    return result


# ============================================================================
# INSTRUMENT FILTER
# ============================================================================


def filter_fx_instruments(
    instruments: List[FXInstrumentInput],
    scanner_filter: FXScannerFilter,
) -> List[FXInstrumentInput]:

    normalized = [
        normalize_fx_instrument(instrument)
        for instrument in instruments
    ]

    result: List[FXInstrumentInput] = []

    for instrument in normalized:

        if not instrument.enabled:
            continue

        if (
            scanner_filter.tradable_only
            and not instrument.tradable
        ):
            continue

        if (
            scanner_filter.market_ids
            and instrument.market_id
            not in scanner_filter.market_ids
        ):
            continue

        if (
            scanner_filter.instrument_ids
            and instrument.instrument_id
            not in scanner_filter.instrument_ids
        ):
            continue

        if (
            scanner_filter.symbols
            and not _fx_matches_list(
                instrument.symbol,
                scanner_filter.symbols,
            )
        ):
            continue

        if not _fx_matches_enum_list(
            instrument.pair_type,
            scanner_filter.pair_types,
        ):
            continue

        if not _fx_matches_enum_list(
            instrument.instrument_type,
            scanner_filter.instrument_types,
        ):
            continue

        if (
            scanner_filter.base_currencies
            and instrument.base_currency
            not in scanner_filter.base_currencies
        ):
            continue

        if (
            scanner_filter.quote_currencies
            and instrument.quote_currency
            not in scanner_filter.quote_currencies
        ):
            continue

        if (
            scanner_filter.session_names
            and not _fx_matches_list(
                instrument.session,
                scanner_filter.session_names,
            )
        ):
            continue

        result.append(instrument)

    return result


# ============================================================================
# UPSTREAM → SCANNER CONVERSION
# ============================================================================


def convert_upstream_fx_opportunity(
    opportunity: UpstreamFXOpportunity,
) -> FXScannerOpportunity:

    source = normalize_upstream_fx_opportunity(
        opportunity
    )

    metadata = dict(source.metadata)

    # ------------------------------------------------------------------------
    # Truth boundary
    # ------------------------------------------------------------------------

    metadata.update(
        {
            "upstream_truth": True,
            "scanner_generated_intelligence": False,
            "scanner_generated_score": False,
            "scanner_generated_decision": False,
            "fx_algorithm_generated": False,

            # Decision authority remains upstream.
            "d13_modified": False,

            # Risk authority remains upstream.
            "risk_generated": False,
            "risk_overridden": False,

            # CAS authority remains upstream.
            "cas_bypassed": False,

            # Execution authority is forbidden here.
            "execution_authority": False,
        }
    )

    return FXScannerOpportunity(
        opportunity_id=source.opportunity_id,

        symbol=source.symbol,
        instrument_id=source.instrument_id,
        instrument_name=source.instrument_name,

        pair_type=source.pair_type,
        instrument_type=source.instrument_type,

        market_id=source.market_id,

        base_currency=source.base_currency,
        quote_currency=source.quote_currency,

        country=source.country,
        region=source.region,
        exchange=source.exchange,

        session=source.session,

        state=source.state,
        bias=source.bias,
        strength=source.strength,

        summary=source.summary,
        confidence=source.confidence,

        timestamp=source.timestamp,

        favorite=source.favorite,
        watchlisted=source.watchlisted,

        priority=source.priority,
        source=source.source,

        metadata=metadata,
    )


# ============================================================================
# RESULT BUILDING
# ============================================================================


def build_fx_scanner_result(
    mode: FXScannerMode,
    opportunities: List[UpstreamFXOpportunity],
    *,
    source_available: bool = True,
    source_errors: List[str] | None = None,
    warnings: List[str] | None = None,
) -> FXScannerResult:

    source_errors = list(source_errors or [])
    warnings = list(warnings or [])

    routed = [
        convert_upstream_fx_opportunity(
            opportunity
        )
        for opportunity in opportunities
    ]

    if source_errors:
        status = FXScannerStatus.DEGRADED
    elif not source_available:
        status = FXScannerStatus.DEGRADED
    else:
        status = FXScannerStatus.READY

    return FXScannerResult(
        status=status,
        mode=mode,
        opportunities=routed,
        total_input_opportunities=len(
            opportunities
        ),
        total_output_opportunities=len(
            routed
        ),
        source_available=source_available,
        source_errors=source_errors,
        warnings=warnings,
        generated_at=_fx_now(),
        metadata={
            "scanner_result": True,
            "upstream_truth_preserved": True,

            "fx_scanner_independent": True,

            "scanner_generated_intelligence": False,
            "scanner_generated_score": False,
            "scanner_generated_decision": False,

            "fx_algorithm_generated": False,

            "equity_scanner_dependency": False,
            "index_scanner_dependency": False,
            "commodity_scanner_dependency": False,
            "crypto_scanner_dependency": False,
        },
    )


# ============================================================================
# SOURCE STATUS
# ============================================================================


def fx_scanner_source_status(
    *,
    authenticated: bool,
    opportunities: List[UpstreamFXOpportunity],
    source_errors: List[str] | None = None,
) -> FXScannerStatus:

    if not authenticated:
        return FXScannerStatus.BLOCKED

    if source_errors:
        return FXScannerStatus.DEGRADED

    if not opportunities:
        return FXScannerStatus.DEGRADED

    return FXScannerStatus.READY
# app/ui/discovery/fx_scanner.py
# PART 3 — STATE / EXECUTION / CONTROLLER / SNAPSHOT


# ============================================================================
# FX SCANNER STATE
# ============================================================================


@dataclass
class FXScannerState:
    initialized: bool = False
    ready: bool = False
    authenticated: bool = False

    status: FXScannerStatus = FXScannerStatus.IDLE
    mode: FXScannerMode = FXScannerMode.UNIVERSAL_FX

    request_count: int = 0
    scan_count: int = 0

    last_error: str = ""
    last_scan_at: datetime | None = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def create_fx_scanner_state(
    *,
    authenticated: bool = False,
    mode: FXScannerMode = FXScannerMode.UNIVERSAL_FX,
) -> FXScannerState:

    return FXScannerState(
        initialized=False,
        ready=False,
        authenticated=authenticated,
        status=(
            FXScannerStatus.IDLE
            if authenticated
            else FXScannerStatus.BLOCKED
        ),
        mode=mode,
        request_count=0,
        scan_count=0,
        last_error="",
        last_scan_at=None,
        metadata={
            "fx_scanner_independent": True,
            "equity_scanner_dependency": False,
            "index_scanner_dependency": False,
            "commodity_scanner_dependency": False,
            "crypto_scanner_dependency": False,
        },
    )


def normalize_fx_scanner_state(
    value: Any,
) -> FXScannerState:

    if isinstance(value, FXScannerState):
        return value

    data = value if isinstance(value, dict) else {}

    last_scan_at = data.get("last_scan_at")

    if not isinstance(last_scan_at, datetime):
        last_scan_at = None

    return FXScannerState(
        initialized=_fx_bool(
            data.get("initialized"),
            False,
        ),
        ready=_fx_bool(
            data.get("ready"),
            False,
        ),
        authenticated=_fx_bool(
            data.get("authenticated"),
            False,
        ),
        status=_fx_enum(
            FXScannerStatus,
            data.get("status"),
            FXScannerStatus.IDLE,
        ),
        mode=_fx_enum(
            FXScannerMode,
            data.get("mode"),
            FXScannerMode.UNIVERSAL_FX,
        ),
        request_count=max(
            0,
            int(
                _fx_float(
                    data.get("request_count"),
                    0,
                )
            ),
        ),
        scan_count=max(
            0,
            int(
                _fx_float(
                    data.get("scan_count"),
                    0,
                )
            ),
        ),
        last_error=_fx_text(
            data.get("last_error")
        ),
        last_scan_at=last_scan_at,
        metadata=dict(
            data.get("metadata") or {}
        ),
    )


# ============================================================================
# FX SCANNER EXECUTION
# ============================================================================


def run_fx_scanner(
    request: FXScannerRequest | Dict[str, Any],
) -> FXScannerResult:

    normalized_request = normalize_fx_request(
        request
    )

    # ------------------------------------------------------------------------
    # Authentication boundary
    # ------------------------------------------------------------------------

    if not normalized_request.authenticated:

        return FXScannerResult(
            status=FXScannerStatus.BLOCKED,
            mode=normalized_request.mode,
            opportunities=[],
            total_input_opportunities=len(
                normalized_request.opportunities
            ),
            total_output_opportunities=0,
            source_available=False,
            source_errors=[
                "FX scanner requires authenticated session."
            ],
            warnings=[],
            generated_at=_fx_now(),
            metadata={
                "scanner_result": True,
                "blocked": True,
                "upstream_truth_preserved": True,
                "scanner_generated_intelligence": False,
                "scanner_generated_score": False,
                "scanner_generated_decision": False,
                "fx_algorithm_generated": False,
                "execution_authority": False,
            },
        )

    scanner_filter = normalized_request.scanner_filter

    # ------------------------------------------------------------------------
    # Universe filtering
    # ------------------------------------------------------------------------

    filtered_markets = filter_fx_markets(
        normalized_request.markets,
        scanner_filter,
    )

    filtered_instruments = filter_fx_instruments(
        normalized_request.instruments,
        scanner_filter,
    )

    # ------------------------------------------------------------------------
    # Opportunity filtering
    # ------------------------------------------------------------------------

    filtered_opportunities = (
        filter_upstream_fx_opportunities(
            normalized_request.opportunities,
            scanner_filter,
        )
    )

    warnings: List[str] = []

    # ------------------------------------------------------------------------
    # Explicit market universe
    # ------------------------------------------------------------------------

    if normalized_request.markets:

        enabled_market_ids = {
            market.market_id
            for market in filtered_markets
            if market.market_id
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
            "No explicit FX market universe supplied; "
            "scanner used upstream opportunity universe."
        )

    # ------------------------------------------------------------------------
    # Explicit instrument universe
    # ------------------------------------------------------------------------

    if normalized_request.instruments:

        enabled_instrument_ids = {
            instrument.instrument_id
            for instrument in filtered_instruments
            if instrument.instrument_id
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
            "No explicit FX instrument universe supplied; "
            "scanner used upstream opportunity universe."
        )

    # ------------------------------------------------------------------------
    # Source status
    # ------------------------------------------------------------------------

    source_errors: List[str] = []

    status = fx_scanner_source_status(
        authenticated=normalized_request.authenticated,
        opportunities=filtered_opportunities,
        source_errors=source_errors,
    )

    if status == FXScannerStatus.DEGRADED:
        warnings.append(
            "FX opportunity intelligence source is unavailable "
            "or contains no routable opportunities."
        )

    # ------------------------------------------------------------------------
    # Result
    # ------------------------------------------------------------------------

    result = build_fx_scanner_result(
        normalized_request.mode,
        filtered_opportunities,
        source_available=bool(
            normalized_request.opportunities
        ),
        source_errors=source_errors,
        warnings=warnings,
    )

    # Preserve actual source status.
    result.status = status

    result.metadata.update(
        {
            "filtered_market_count": len(
                filtered_markets
            ),
            "filtered_instrument_count": len(
                filtered_instruments
            ),
            "upstream_truth_preserved": True,
            "fx_scanner_independent": True,
            "fx_algorithm_generated": False,
            "scanner_generated_intelligence": False,
            "scanner_generated_score": False,
            "scanner_generated_decision": False,
            "equity_scanner_dependency": False,
            "index_scanner_dependency": False,
            "commodity_scanner_dependency": False,
            "crypto_scanner_dependency": False,
        }
    )

    return result


# ============================================================================
# FX SCANNER CONTROLLER
# ============================================================================


class FXScannerController:

    def __init__(
        self,
        state: FXScannerState | None = None,
    ) -> None:

        self._state = normalize_fx_scanner_state(
            state
            if state is not None
            else create_fx_scanner_state()
        )

        self._last_request: FXScannerRequest | None = None
        self._last_result: FXScannerResult | None = None

        self._request_history: List[
            FXScannerRequest
        ] = []

        self._result_history: List[
            FXScannerResult
        ] = []

    # ------------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------------

    @property
    def state(self) -> FXScannerState:
        return self._state

    @property
    def status(self) -> FXScannerStatus:
        return self._state.status

    @property
    def mode(self) -> FXScannerMode:
        return self._state.mode

    @property
    def authenticated(self) -> bool:
        return self._state.authenticated

    @property
    def last_request(
        self,
    ) -> FXScannerRequest | None:
        return self._last_request

    @property
    def last_result(
        self,
    ) -> FXScannerResult | None:
        return self._last_result

    # ------------------------------------------------------------------------
    # Initialize
    # ------------------------------------------------------------------------

    def initialize(
        self,
        *,
        authenticated: bool | None = None,
    ) -> FXScannerState:

        if authenticated is not None:
            self._state.authenticated = bool(
                authenticated
            )

        self._state.initialized = True

        if self._state.authenticated:
            self._state.status = FXScannerStatus.READY
            self._state.ready = True
        else:
            self._state.status = FXScannerStatus.BLOCKED
            self._state.ready = False

        self._state.last_error = ""

        return self._state

    # ------------------------------------------------------------------------
    # Scan
    # ------------------------------------------------------------------------

    def scan(
        self,
        request: FXScannerRequest | Dict[str, Any],
    ) -> FXScannerResult:

        normalized_request = normalize_fx_request(
            request
        )

        self._state.request_count += 1

        self._state.mode = normalized_request.mode
        self._state.authenticated = (
            normalized_request.authenticated
        )

        self._state.status = FXScannerStatus.LOADING

        self._last_request = normalized_request

        self._request_history.append(
            normalized_request
        )

        if len(self._request_history) > 500:
            self._request_history.pop(0)

        try:

            result = run_fx_scanner(
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
                in {
                    FXScannerStatus.READY,
                    FXScannerStatus.DEGRADED,
                }
            )

            self._state.last_error = (
                result.source_errors[0]
                if result.source_errors
                else ""
            )

            self._state.last_scan_at = (
                result.generated_at
            )

            return result

        except Exception as exc:

            self._state.status = FXScannerStatus.ERROR
            self._state.ready = False
            self._state.last_error = str(exc)

            raise

    # ------------------------------------------------------------------------
    # Mode
    # ------------------------------------------------------------------------

    def set_mode(
        self,
        mode: FXScannerMode,
    ) -> FXScannerState:

        self._state.mode = _fx_enum(
            FXScannerMode,
            mode,
            FXScannerMode.UNIVERSAL_FX,
        )

        return self._state

    # ------------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------------

    def set_authenticated(
        self,
        authenticated: bool,
    ) -> FXScannerState:

        self._state.authenticated = bool(
            authenticated
        )

        if self._state.authenticated:

            self._state.status = (
                FXScannerStatus.READY
                if self._state.initialized
                else FXScannerStatus.IDLE
            )

            self._state.ready = self._state.initialized

        else:

            self._state.status = FXScannerStatus.BLOCKED
            self._state.ready = False

        return self._state

    # ------------------------------------------------------------------------
    # Block
    # ------------------------------------------------------------------------

    def block(
        self,
        reason: str = "",
    ) -> FXScannerState:

        self._state.status = FXScannerStatus.BLOCKED
        self._state.ready = False
        self._state.last_error = _fx_text(
            reason,
            "FX scanner blocked.",
        )

        return self._state

    # ------------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------------

    def reset(self) -> FXScannerState:

        authenticated = self._state.authenticated

        self._state = create_fx_scanner_state(
            authenticated=authenticated,
            mode=FXScannerMode.UNIVERSAL_FX,
        )

        self._last_request = None
        self._last_result = None

        self._request_history.clear()
        self._result_history.clear()

        return self._state

    # ------------------------------------------------------------------------
    # Snapshot
    # ------------------------------------------------------------------------

    def snapshot(self) -> FXScannerSnapshot:

        request = (
            self._last_request
            if self._last_request is not None
            else FXScannerRequest(
                mode=self._state.mode,
                authenticated=self._state.authenticated,
            )
        )

        result = (
            self._last_result
            if self._last_result is not None
            else FXScannerResult(
                status=self._state.status,
                mode=self._state.mode,
                opportunities=[],
                source_available=False,
                generated_at=_fx_now(),
            )
        )

        return FXScannerSnapshot(
            request=request,
            result=result,
            captured_at=_fx_now(),
            metadata={
                "scanner_snapshot": True,
                "upstream_truth_preserved": True,
                "fx_scanner_independent": True,
                "fx_algorithm_generated": False,
                "scanner_generated_intelligence": False,
                "scanner_generated_score": False,
                "scanner_generated_decision": False,
                "equity_scanner_dependency": False,
                "index_scanner_dependency": False,
                "commodity_scanner_dependency": False,
                "crypto_scanner_dependency": False,
            },
        )

    # ------------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------------

    @property
    def request_history(
        self,
    ) -> List[FXScannerRequest]:

        return list(self._request_history)

    @property
    def result_history(
        self,
    ) -> List[FXScannerResult]:

        return list(self._result_history)


# ============================================================================
# DEFAULT CONTROLLER
# ============================================================================


_DEFAULT_FX_SCANNER = FXScannerController()


def get_fx_scanner() -> FXScannerController:
    return _DEFAULT_FX_SCANNER


def create_fx_scanner(
    *,
    authenticated: bool = False,
    mode: FXScannerMode = FXScannerMode.UNIVERSAL_FX,
) -> FXScannerController:

    return FXScannerController(
        create_fx_scanner_state(
            authenticated=authenticated,
            mode=mode,
        )
    )


# ============================================================================
# PUBLIC SCAN HELPERS
# ============================================================================


def scan_fx_market(
    opportunities: List[
        UpstreamFXOpportunity
    ],
    *,
    markets: List[FXMarketInput] | None = None,
    instruments: List[FXInstrumentInput] | None = None,
    scanner_filter: FXScannerFilter | None = None,
    mode: FXScannerMode = FXScannerMode.UNIVERSAL_FX,
    authenticated: bool = True,
) -> FXScannerResult:

    request = FXScannerRequest(
        mode=mode,
        markets=list(markets or []),
        instruments=list(instruments or []),
        opportunities=list(opportunities or []),
        scanner_filter=(
            scanner_filter
            if scanner_filter is not None
            else FXScannerFilter()
        ),
        authenticated=authenticated,
    )

    return run_fx_scanner(request)


def scan_with_fx_scanner(
    request: FXScannerRequest | Dict[str, Any],
) -> FXScannerResult:

    return get_fx_scanner().scan(request)
# app/ui/discovery/fx_scanner.py
# PART 4 — SERIALIZATION / VALIDATION / HEALTH / OPERATIONAL CHECK


# ============================================================================
# SERIALIZATION
# ============================================================================


def _serialize_fx_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, list):
        return [
            _serialize_fx_value(item)
            for item in value
        ]

    if isinstance(value, tuple):
        return [
            _serialize_fx_value(item)
            for item in value
        ]

    if isinstance(value, dict):
        return {
            str(key): _serialize_fx_value(item)
            for key, item in value.items()
        }

    if hasattr(value, "__dataclass_fields__"):
        return {
            key: _serialize_fx_value(
                getattr(value, key)
            )
            for key in value.__dataclass_fields__
        }

    return value


def serialize_fx_market(
    value: FXMarketInput,
) -> Dict[str, Any]:
    return _serialize_fx_value(value)


def serialize_fx_instrument(
    value: FXInstrumentInput,
) -> Dict[str, Any]:
    return _serialize_fx_value(value)


def serialize_upstream_fx_opportunity(
    value: UpstreamFXOpportunity,
) -> Dict[str, Any]:
    return _serialize_fx_value(value)


def serialize_fx_filter(
    value: FXScannerFilter,
) -> Dict[str, Any]:
    return _serialize_fx_value(value)


def serialize_fx_scanner_opportunity(
    value: FXScannerOpportunity,
) -> Dict[str, Any]:
    return _serialize_fx_value(value)


def serialize_fx_scanner_result(
    value: FXScannerResult,
) -> Dict[str, Any]:
    return _serialize_fx_value(value)


def serialize_fx_scanner_request(
    value: FXScannerRequest,
) -> Dict[str, Any]:
    return _serialize_fx_value(value)


def serialize_fx_scanner_snapshot(
    value: FXScannerSnapshot,
) -> Dict[str, Any]:
    return _serialize_fx_value(value)


def serialize_fx_scanner_state(
    value: FXScannerState,
) -> Dict[str, Any]:
    return _serialize_fx_value(value)


# ============================================================================
# VALIDATION — MARKET
# ============================================================================


def validate_fx_market(
    value: FXMarketInput,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(value, FXMarketInput):
        return ["Invalid FX market input type."]

    if not value.market_id:
        errors.append(
            "FX market_id is required."
        )

    if not value.market_name:
        errors.append(
            "FX market_name is required."
        )

    if not value.fx_available:
        errors.append(
            "FX market is marked unavailable."
        )

    return errors


# ============================================================================
# VALIDATION — INSTRUMENT
# ============================================================================


def validate_fx_instrument(
    value: FXInstrumentInput,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        value,
        FXInstrumentInput,
    ):
        return ["Invalid FX instrument input type."]

    if not value.instrument_id:
        errors.append(
            "FX instrument_id is required."
        )

    if not value.symbol:
        errors.append(
            "FX instrument symbol is required."
        )

    if not value.base_currency:
        errors.append(
            "FX base_currency is required."
        )

    if not value.quote_currency:
        errors.append(
            "FX quote_currency is required."
        )

    if (
        value.base_currency
        and value.quote_currency
        and value.base_currency
        == value.quote_currency
    ):
        errors.append(
            "FX base and quote currencies "
            "must not be identical."
        )

    return errors


# ============================================================================
# VALIDATION — UPSTREAM OPPORTUNITY
# ============================================================================


def validate_upstream_fx_opportunity(
    value: UpstreamFXOpportunity,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        value,
        UpstreamFXOpportunity,
    ):
        return [
            "Invalid upstream FX opportunity type."
        ]

    if not value.opportunity_id:
        errors.append(
            "FX opportunity_id is required."
        )

    if not value.symbol:
        errors.append(
            "FX opportunity symbol is required."
        )

    if not value.instrument_id:
        errors.append(
            "FX opportunity instrument_id is required."
        )

    if not value.base_currency:
        errors.append(
            "FX opportunity base_currency is required."
        )

    if not value.quote_currency:
        errors.append(
            "FX opportunity quote_currency is required."
        )

    if (
        value.base_currency
        and value.quote_currency
        and value.base_currency
        == value.quote_currency
    ):
        errors.append(
            "FX opportunity base and quote "
            "currencies must not be identical."
        )

    if not 0.0 <= value.confidence <= 1.0:
        errors.append(
            "FX opportunity confidence must be "
            "between 0 and 1."
        )

    if value.state == FXOpportunityState.UNKNOWN:
        errors.append(
            "FX opportunity state cannot be UNKNOWN."
        )

    return errors


# ============================================================================
# VALIDATION — FILTER
# ============================================================================


def validate_fx_scanner_filter(
    value: FXScannerFilter,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        value,
        FXScannerFilter,
    ):
        return ["Invalid FX scanner filter type."]

    if (
        value.favorites_only
        and value.watchlist_only
        and value.metadata.get(
            "exclusive_favorite_watchlist",
            False,
        )
    ):
        errors.append(
            "Exclusive favorite/watchlist filter "
            "cannot require both states."
        )

    return errors


# ============================================================================
# VALIDATION — SCANNER OPPORTUNITY
# ============================================================================


def validate_fx_scanner_opportunity(
    value: FXScannerOpportunity,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        value,
        FXScannerOpportunity,
    ):
        return [
            "Invalid FX scanner opportunity type."
        ]

    if not value.opportunity_id:
        errors.append(
            "Scanner opportunity_id is required."
        )

    if not value.symbol:
        errors.append(
            "Scanner opportunity symbol is required."
        )

    if not value.instrument_id:
        errors.append(
            "Scanner opportunity instrument_id "
            "is required."
        )

    if not 0.0 <= value.confidence <= 1.0:
        errors.append(
            "Scanner opportunity confidence must "
            "be between 0 and 1."
        )

    if value.metadata.get(
        "scanner_generated_intelligence",
        False,
    ):
        errors.append(
            "FX scanner must not generate intelligence."
        )

    if value.metadata.get(
        "scanner_generated_score",
        False,
    ):
        errors.append(
            "FX scanner must not generate scores."
        )

    if value.metadata.get(
        "scanner_generated_decision",
        False,
    ):
        errors.append(
            "FX scanner must not generate decisions."
        )

    if value.metadata.get(
        "fx_algorithm_generated",
        False,
    ):
        errors.append(
            "FX algorithm generation belongs upstream."
        )

    if value.metadata.get(
        "d13_modified",
        False,
    ):
        errors.append(
            "FX scanner cannot modify D13."
        )

    if value.metadata.get(
        "risk_overridden",
        False,
    ):
        errors.append(
            "FX scanner cannot override risk."
        )

    if value.metadata.get(
        "cas_bypassed",
        False,
    ):
        errors.append(
            "FX scanner cannot bypass CAS."
        )

    if value.metadata.get(
        "execution_authority",
        False,
    ):
        errors.append(
            "FX scanner cannot possess execution authority."
        )

    return errors


# ============================================================================
# VALIDATION — REQUEST
# ============================================================================


def validate_fx_scanner_request(
    value: FXScannerRequest,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        value,
        FXScannerRequest,
    ):
        return ["Invalid FX scanner request type."]

    errors.extend(
        validate_fx_scanner_filter(
            value.scanner_filter
        )
    )

    for market in value.markets:
        errors.extend(
            validate_fx_market(market)
        )

    for instrument in value.instruments:
        errors.extend(
            validate_fx_instrument(instrument)
        )

    for opportunity in value.opportunities:
        errors.extend(
            validate_upstream_fx_opportunity(
                opportunity
            )
        )

    return errors


# ============================================================================
# VALIDATION — RESULT
# ============================================================================


def validate_fx_scanner_result(
    value: FXScannerResult,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        value,
        FXScannerResult,
    ):
        return ["Invalid FX scanner result type."]

    if value.total_input_opportunities < 0:
        errors.append(
            "Input opportunity count cannot be negative."
        )

    if value.total_output_opportunities < 0:
        errors.append(
            "Output opportunity count cannot be negative."
        )

    if (
        value.total_output_opportunities
        != len(value.opportunities)
    ):
        errors.append(
            "Output opportunity count does not "
            "match result length."
        )

    for opportunity in value.opportunities:
        errors.extend(
            validate_fx_scanner_opportunity(
                opportunity
            )
        )

    if value.metadata.get(
        "scanner_generated_intelligence",
        False,
    ):
        errors.append(
            "Result cannot claim scanner-generated intelligence."
        )

    if value.metadata.get(
        "fx_algorithm_generated",
        False,
    ):
        errors.append(
            "FX algorithm must remain upstream."
        )

    return errors


# ============================================================================
# VALIDATION — STATE
# ============================================================================


def validate_fx_scanner_state(
    value: FXScannerState,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        value,
        FXScannerState,
    ):
        return ["Invalid FX scanner state type."]

    if value.request_count < 0:
        errors.append(
            "Request count cannot be negative."
        )

    if value.scan_count < 0:
        errors.append(
            "Scan count cannot be negative."
        )

    if (
        value.ready
        and not value.authenticated
    ):
        errors.append(
            "Unauthenticated FX scanner cannot "
            "be ready."
        )

    if (
        value.status == FXScannerStatus.READY
        and not value.authenticated
    ):
        errors.append(
            "READY status requires authentication."
        )

    return errors


# ============================================================================
# VALIDATION — SNAPSHOT
# ============================================================================


def validate_fx_scanner_snapshot(
    value: FXScannerSnapshot,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        value,
        FXScannerSnapshot,
    ):
        return [
            "Invalid FX scanner snapshot type."
        ]

    errors.extend(
        validate_fx_scanner_request(
            value.request
        )
    )

    errors.extend(
        validate_fx_scanner_result(
            value.result
        )
    )

    if value.metadata.get(
        "fx_algorithm_generated",
        False,
    ):
        errors.append(
            "Snapshot cannot generate FX algorithm intelligence."
        )

    if not value.metadata.get(
        "upstream_truth_preserved",
        False,
    ):
        errors.append(
            "Snapshot must preserve upstream truth."
        )

    return errors


# ============================================================================
# AUTHORITY VALIDATION
# ============================================================================


def validate_fx_scanner_authority() -> List[str]:

    errors: List[str] = []

    forbidden = [
        "fx_specific_algorithm_generation",
        "fx_signal_generation",
        "fx_score_generation",
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
    ]

    for key in forbidden:
        if FX_SCANNER_AUTHORITY.get(key):
            errors.append(
                f"Forbidden FX scanner authority enabled: {key}"
            )

    independent_flags = [
        "equity_scanner_dependency",
        "index_scanner_dependency",
        "commodity_scanner_dependency",
        "crypto_scanner_dependency",
    ]

    for key in independent_flags:
        if FX_SCANNER_AUTHORITY.get(key):
            errors.append(
                f"FX scanner dependency must remain false: {key}"
            )

    return errors


# ============================================================================
# HEALTH CONTRACT
# ============================================================================


@dataclass
class FXScannerHealth:
    engine: str
    version: str

    operational: bool
    initialized: bool
    ready: bool
    authenticated: bool

    status: FXScannerStatus

    critical_scanner: bool = True
    fx_scanner_independent: bool = True

    equity_scanner_dependency: bool = False
    index_scanner_dependency: bool = False
    commodity_scanner_dependency: bool = False
    crypto_scanner_dependency: bool = False

    # Future FX research/intelligence readiness.
    fx_pair_structure_analysis: bool = False
    fx_session_liquidity_analysis: bool = False
    fx_relative_currency_strength_analysis: bool = False
    fx_macro_event_sensitivity_analysis: bool = False
    fx_volatility_regime_analysis: bool = False
    fx_breakout_analysis: bool = False
    fx_confirmation_analysis: bool = False
    fx_exact_levels: bool = False

    errors: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    checked_at: datetime = field(
        default_factory=_fx_now
    )


def build_fx_scanner_health(
    state: FXScannerState | None = None,
) -> FXScannerHealth:

    scanner_state = (
        normalize_fx_scanner_state(state)
        if state is not None
        else create_fx_scanner_state()
    )

    errors = validate_fx_scanner_state(
        scanner_state
    )

    errors.extend(
        validate_fx_scanner_authority()
    )

    warnings: List[str] = []

    if not scanner_state.authenticated:
        warnings.append(
            "FX scanner is not authenticated."
        )

    if not scanner_state.initialized:
        warnings.append(
            "FX scanner has not been initialized."
        )

    if scanner_state.status == FXScannerStatus.DEGRADED:
        warnings.append(
            "FX scanner is operational but upstream "
            "FX opportunity intelligence is degraded."
        )

    operational = (
        not errors
        and scanner_state.status
        not in {
            FXScannerStatus.ERROR,
        }
    )

    return FXScannerHealth(
        engine=FX_SCANNER_ENGINE,
        version=FX_SCANNER_VERSION,

        operational=operational,
        initialized=scanner_state.initialized,
        ready=scanner_state.ready,
        authenticated=scanner_state.authenticated,

        status=scanner_state.status,

        critical_scanner=True,
        fx_scanner_independent=True,

        equity_scanner_dependency=False,
        index_scanner_dependency=False,
        commodity_scanner_dependency=False,
        crypto_scanner_dependency=False,

        # Research remains upstream and is not falsely marked ready.
        fx_pair_structure_analysis=False,
        fx_session_liquidity_analysis=False,
        fx_relative_currency_strength_analysis=False,
        fx_macro_event_sensitivity_analysis=False,
        fx_volatility_regime_analysis=False,
        fx_breakout_analysis=False,
        fx_confirmation_analysis=False,
        fx_exact_levels=False,

        errors=errors,
        warnings=warnings,
        checked_at=_fx_now(),
    )


def serialize_fx_scanner_health(
    value: FXScannerHealth,
) -> Dict[str, Any]:

    return _serialize_fx_value(value)


# ============================================================================
# OPERATIONAL CHECK
# ============================================================================


def fx_scanner_operational_check(
    state: FXScannerState | None = None,
) -> Dict[str, Any]:

    health = build_fx_scanner_health(
        state
    )

    return {
        "engine": FX_SCANNER_ENGINE,
        "version": FX_SCANNER_VERSION,

        "operational": health.operational,
        "initialized": health.initialized,
        "ready": health.ready,
        "authenticated": health.authenticated,

        "status": health.status.value,

        "critical_scanner": True,
        "fx_scanner_independent": True,

        "equity_scanner_dependency": False,
        "index_scanner_dependency": False,
        "commodity_scanner_dependency": False,
        "crypto_scanner_dependency": False,

        # Future research readiness — deliberately false
        # until validated FX research is implemented upstream.
        "fx_pair_structure_analysis": False,
        "fx_session_liquidity_analysis": False,
        "fx_relative_currency_strength_analysis": False,
        "fx_macro_event_sensitivity_analysis": False,
        "fx_volatility_regime_analysis": False,
        "fx_breakout_analysis": False,
        "fx_confirmation_analysis": False,
        "fx_exact_levels": False,

        # Intelligence generation remains forbidden here.
        "fx_algorithm_generated": False,
        "scanner_generated_intelligence": False,
        "scanner_generated_score": False,
        "scanner_generated_decision": False,

        "d13_modified": False,
        "risk_generated": False,
        "risk_overridden": False,
        "cas_bypassed": False,
        "execution_authority": False,

        "errors": list(
            health.errors
        ),
        "warnings": list(
            health.warnings
        ),

        "checked_at": health.checked_at.isoformat(),
    }
# app/ui/discovery/fx_scanner.py
# PART 5 — DIAGNOSTICS / CONTRACT / INTEGRITY / SELF-CHECK / EXPORTS


# ============================================================================
# DIAGNOSTICS
# ============================================================================


def diagnose_fx_scanner(
    state: FXScannerState | None = None,
    result: FXScannerResult | None = None,
) -> Dict[str, Any]:

    scanner_state = (
        normalize_fx_scanner_state(state)
        if state is not None
        else create_fx_scanner_state()
    )

    health = build_fx_scanner_health(
        scanner_state
    )

    result_errors: List[str] = []

    if result is not None:
        result_errors = validate_fx_scanner_result(
            result
        )

    return {
        "engine": FX_SCANNER_ENGINE,
        "version": FX_SCANNER_VERSION,
        "name": FX_SCANNER_NAME,

        "status": scanner_state.status.value,
        "initialized": scanner_state.initialized,
        "ready": scanner_state.ready,
        "authenticated": scanner_state.authenticated,

        "request_count": scanner_state.request_count,
        "scan_count": scanner_state.scan_count,

        "operational": health.operational,

        "critical_scanner": True,
        "fx_scanner_independent": True,

        "equity_scanner_dependency": False,
        "index_scanner_dependency": False,
        "commodity_scanner_dependency": False,
        "crypto_scanner_dependency": False,

        "upstream_truth_policy": {
            "preserved": True,
            "scanner_generates_intelligence": False,
            "scanner_generates_score": False,
            "scanner_generates_decision": False,
            "fx_algorithm_generated": False,
        },

        "authority": dict(
            FX_SCANNER_AUTHORITY
        ),

        "health_errors": list(
            health.errors
        ),

        "health_warnings": list(
            health.warnings
        ),

        "result_errors": result_errors,

        "last_error": scanner_state.last_error,

        "last_scan_at": (
            scanner_state.last_scan_at.isoformat()
            if scanner_state.last_scan_at
            else None
        ),

        "diagnostic_at": _fx_now().isoformat(),
    }


# ============================================================================
# SUMMARY
# ============================================================================


def fx_scanner_summary(
    result: FXScannerResult | None = None,
) -> Dict[str, Any]:

    if result is None:
        return {
            "engine": FX_SCANNER_ENGINE,
            "version": FX_SCANNER_VERSION,
            "status": FXScannerStatus.IDLE.value,
            "mode": FXScannerMode.UNIVERSAL_FX.value,
            "opportunity_count": 0,
            "critical_scanner": True,
            "fx_scanner_independent": True,
            "upstream_truth_preserved": True,
            "scanner_generated_intelligence": False,
            "fx_algorithm_generated": False,
        }

    priorities = {
        priority.value: 0
        for priority in FXScannerPriority
    }

    biases = {
        bias.value: 0
        for bias in FXOpportunityBias
    }

    states = {
        state.value: 0
        for state in FXOpportunityState
    }

    strengths = {
        strength.value: 0
        for strength in FXOpportunityStrength
    }

    for opportunity in result.opportunities:
        priorities[
            opportunity.priority.value
        ] += 1

        biases[
            opportunity.bias.value
        ] += 1

        states[
            opportunity.state.value
        ] += 1

        strengths[
            opportunity.strength.value
        ] += 1

    return {
        "engine": FX_SCANNER_ENGINE,
        "version": FX_SCANNER_VERSION,

        "status": result.status.value,
        "mode": result.mode.value,

        "total_input_opportunities":
            result.total_input_opportunities,

        "total_output_opportunities":
            result.total_output_opportunities,

        "source_available":
            result.source_available,

        "priority_distribution": priorities,
        "bias_distribution": biases,
        "state_distribution": states,
        "strength_distribution": strengths,

        "warning_count": len(
            result.warnings
        ),

        "source_error_count": len(
            result.source_errors
        ),

        "critical_scanner": True,
        "fx_scanner_independent": True,

        "upstream_truth_preserved": True,
        "scanner_generated_intelligence": False,
        "scanner_generated_score": False,
        "scanner_generated_decision": False,
        "fx_algorithm_generated": False,

        "equity_scanner_dependency": False,
        "index_scanner_dependency": False,
        "commodity_scanner_dependency": False,
        "crypto_scanner_dependency": False,

        "generated_at":
            result.generated_at.isoformat(),
    }


# ============================================================================
# CONTRACT MANIFEST
# ============================================================================


def fx_scanner_contract_manifest() -> Dict[str, Any]:

    return {
        "engine": FX_SCANNER_ENGINE,
        "version": FX_SCANNER_VERSION,
        "name": FX_SCANNER_NAME,
        "title": FX_SCANNER_TITLE,

        "layer": "UI_PRESENTATION",

        "role": "FX_OPPORTUNITY_SCANNER",

        "importance": "CLASS_A_DISCOVERY_COMPONENT",

        "critical_scanner": True,

        "description": FX_SCANNER_DESCRIPTION,

        # --------------------------------------------------------------------
        # Inputs
        # --------------------------------------------------------------------

        "inputs": [
            "USER_SERVICE_OUTPUT",
            "FX_MARKET_INPUT",
            "FX_INSTRUMENT_INPUT",
            "FX_SCANNER_FILTER",
            "UPSTREAM_FX_OPPORTUNITY_OUTPUT",
            "WATCHLIST_OUTPUT",
            "FAVORITES_OUTPUT",
            "APPLICATION_SESSION_STATE",
        ],

        # --------------------------------------------------------------------
        # Processing
        # --------------------------------------------------------------------

        "processing": [
            "SOURCE_NORMALIZATION",
            "FX_MARKET_FILTERING",
            "FX_REGION_FILTERING",
            "FX_SESSION_FILTERING",
            "FX_CURRENCY_FILTERING",
            "FX_PAIR_FILTERING",
            "FX_INSTRUMENT_FILTERING",
            "FX_BASE_CURRENCY_FILTERING",
            "FX_QUOTE_CURRENCY_FILTERING",
            "OPPORTUNITY_STATE_FILTERING",
            "OPPORTUNITY_BIAS_FILTERING",
            "OPPORTUNITY_STRENGTH_FILTERING",
            "FAVORITE_FILTERING",
            "WATCHLIST_FILTERING",
            "TRADABLE_FILTERING",
            "UPSTREAM_OPPORTUNITY_ROUTING",
            "RESULT_BUILDING",
            "SNAPSHOT_BUILDING",
            "SERIALIZATION",
            "VALIDATION",
            "HEALTH_CHECK",
            "DIAGNOSTICS",
        ],

        # --------------------------------------------------------------------
        # Outputs
        # --------------------------------------------------------------------

        "outputs": [
            "FX_SCANNER_RESULT",
            "FX_SCANNER_SNAPSHOT",
            "FX_SCANNER_STATE",
            "FX_SCANNER_HEALTH",
            "FX_SCANNER_DIAGNOSTICS",
        ],

        # --------------------------------------------------------------------
        # Truth policy
        # --------------------------------------------------------------------

        "truth_policy": {
            "upstream_truth_preserved": True,

            "scanner_generated_intelligence": False,
            "scanner_generated_score": False,
            "scanner_generated_decision": False,

            "fx_algorithm_generated": False,

            "d13_modified": False,

            "risk_generated": False,
            "risk_overridden": False,

            "cas_bypassed": False,

            "execution_authority": False,

            "upstream_mutation": False,
        },

        # --------------------------------------------------------------------
        # FX intelligence authority
        # --------------------------------------------------------------------

        "intelligence_authority": {
            "owner": "UPSTREAM_FX_INTELLIGENCE",

            "fx_pair_structure": (
                "UPSTREAM_FX_INTELLIGENCE"
            ),

            "session_liquidity_analysis": (
                "UPSTREAM_FX_INTELLIGENCE"
            ),

            "relative_currency_strength": (
                "UPSTREAM_FX_INTELLIGENCE"
            ),

            "macro_event_sensitivity": (
                "UPSTREAM_FX_INTELLIGENCE"
            ),

            "volatility_regime": (
                "UPSTREAM_FX_INTELLIGENCE"
            ),

            "breakout_analysis": (
                "UPSTREAM_FX_INTELLIGENCE"
            ),

            "breakout_confirmation": (
                "UPSTREAM_FX_INTELLIGENCE"
            ),

            "exact_level_calculation": (
                "UPSTREAM_FX_INTELLIGENCE"
            ),
        },

        # --------------------------------------------------------------------
        # Future research pipeline
        # --------------------------------------------------------------------

        "future_research_pipeline": [
            "FX_PAIR_STRUCTURE",
            "SESSION_LIQUIDITY_ANALYSIS",
            "RELATIVE_CURRENCY_STRENGTH",
            "MACRO_EVENT_SENSITIVITY",
            "FX_VOLATILITY_REGIME",
            "BREAKOUT_ANALYSIS",
            "BREAKOUT_CONFIRMATION",
            "EXACT_LEVEL_CALCULATION",
            "UPSTREAM_FX_INTELLIGENCE",
            "FX_SCANNER",
        ],

        "formula_authority":
            "UPSTREAM_FX_INTELLIGENCE",

        "formula_pluggable": True,

        # --------------------------------------------------------------------
        # Independence
        # --------------------------------------------------------------------

        "independence": {
            "fx_scanner_independent": True,

            "equity_scanner_dependency": False,
            "index_scanner_dependency": False,
            "commodity_scanner_dependency": False,
            "crypto_scanner_dependency": False,

            "equity_signal_required": False,
            "index_signal_required": False,
            "commodity_signal_required": False,
            "crypto_signal_required": False,
        },

        # --------------------------------------------------------------------
        # Forbidden authority
        # --------------------------------------------------------------------

        "forbidden_authority": [
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


# ============================================================================
# INTEGRITY VALIDATION
# ============================================================================


def validate_fx_scanner_integrity(
    *,
    request: FXScannerRequest | None = None,
    result: FXScannerResult | None = None,
    state: FXScannerState | None = None,
    snapshot: FXScannerSnapshot | None = None,
) -> List[str]:

    errors: List[str] = []

    errors.extend(
        validate_fx_scanner_authority()
    )

    if request is not None:
        errors.extend(
            validate_fx_scanner_request(
                request
            )
        )

    if result is not None:
        errors.extend(
            validate_fx_scanner_result(
                result
            )
        )

    if state is not None:
        errors.extend(
            validate_fx_scanner_state(
                state
            )
        )

    if snapshot is not None:
        errors.extend(
            validate_fx_scanner_snapshot(
                snapshot
            )
        )

    if result is not None:

        if not result.metadata.get(
            "upstream_truth_preserved",
            False,
        ):
            errors.append(
                "FX result must preserve upstream truth."
            )

        if result.metadata.get(
            "fx_algorithm_generated",
            False,
        ):
            errors.append(
                "FX algorithm generation cannot "
                "originate inside scanner."
            )

        for opportunity in result.opportunities:

            if not opportunity.metadata.get(
                "upstream_truth",
                False,
            ):
                errors.append(
                    "Routed FX opportunity lost "
                    "upstream truth marker."
                )

            if opportunity.metadata.get(
                "scanner_generated_intelligence",
                False,
            ):
                errors.append(
                    "Scanner-generated FX intelligence detected."
                )

            if opportunity.metadata.get(
                "scanner_generated_score",
                False,
            ):
                errors.append(
                    "Scanner-generated FX score detected."
                )

            if opportunity.metadata.get(
                "scanner_generated_decision",
                False,
            ):
                errors.append(
                    "Scanner-generated FX decision detected."
                )

    return list(dict.fromkeys(errors))


# ============================================================================
# CONTRACT VALIDATION
# ============================================================================


def validate_fx_scanner_contract() -> List[str]:

    errors: List[str] = []

    manifest = fx_scanner_contract_manifest()

    required_inputs = {
        "USER_SERVICE_OUTPUT",
        "FX_MARKET_INPUT",
        "FX_INSTRUMENT_INPUT",
        "FX_SCANNER_FILTER",
        "UPSTREAM_FX_OPPORTUNITY_OUTPUT",
        "WATCHLIST_OUTPUT",
        "FAVORITES_OUTPUT",
        "APPLICATION_SESSION_STATE",
    }

    required_outputs = {
        "FX_SCANNER_RESULT",
        "FX_SCANNER_SNAPSHOT",
        "FX_SCANNER_STATE",
        "FX_SCANNER_HEALTH",
        "FX_SCANNER_DIAGNOSTICS",
    }

    if not required_inputs.issubset(
        set(manifest["inputs"])
    ):
        errors.append(
            "FX scanner contract is missing required inputs."
        )

    if not required_outputs.issubset(
        set(manifest["outputs"])
    ):
        errors.append(
            "FX scanner contract is missing required outputs."
        )

    if manifest["layer"] != "UI_PRESENTATION":
        errors.append(
            "FX scanner must remain a UI presentation layer."
        )

    if manifest["role"] != "FX_OPPORTUNITY_SCANNER":
        errors.append(
            "Invalid FX scanner role."
        )

    if not manifest["critical_scanner"]:
        errors.append(
            "FX scanner must remain Class-A critical."
        )

    if not manifest["formula_pluggable"]:
        errors.append(
            "FX scanner formula integration must remain pluggable."
        )

    if manifest["formula_authority"] != (
        "UPSTREAM_FX_INTELLIGENCE"
    ):
        errors.append(
            "FX formula authority must remain upstream."
        )

    independence = manifest["independence"]

    if not independence[
        "fx_scanner_independent"
    ]:
        errors.append(
            "FX scanner must remain independent."
        )

    for key in (
        "equity_scanner_dependency",
        "index_scanner_dependency",
        "commodity_scanner_dependency",
        "crypto_scanner_dependency",
    ):
        if independence[key]:
            errors.append(
                f"Unexpected FX scanner dependency: {key}"
            )

    return list(dict.fromkeys(errors))


# ============================================================================
# MODULE CHECK
# ============================================================================


def fx_scanner_module_check() -> Dict[str, Any]:

    authority_errors = (
        validate_fx_scanner_authority()
    )

    contract_errors = (
        validate_fx_scanner_contract()
    )

    state = create_fx_scanner_state(
        authenticated=True
    )

    state.initialized = True
    state.ready = True
    state.status = FXScannerStatus.READY

    state_errors = validate_fx_scanner_state(
        state
    )

    health = build_fx_scanner_health(
        state
    )

    errors = list(
        dict.fromkeys(
            authority_errors
            + contract_errors
            + state_errors
            + health.errors
        )
    )

    return {
        "engine": FX_SCANNER_ENGINE,
        "version": FX_SCANNER_VERSION,
        "module": FX_SCANNER_NAME,

        "valid": not errors,

        "operational": health.operational,

        "critical_scanner": True,
        "fx_scanner_independent": True,

        "authority_valid": not authority_errors,
        "contract_valid": not contract_errors,
        "state_valid": not state_errors,

        "future_research_ready": False,

        "formula_pluggable": True,
        "formula_authority":
            "UPSTREAM_FX_INTELLIGENCE",

        "errors": errors,

        "checked_at": _fx_now().isoformat(),
    }


# ============================================================================
# SELF CHECK
# ============================================================================


def fx_scanner_self_check() -> Dict[str, Any]:

    upstream = UpstreamFXOpportunity(
        opportunity_id="FX-SELF-CHECK-001",

        symbol="EURUSD",
        instrument_id="EURUSD-SPOT",
        instrument_name="Euro / US Dollar",

        pair_type=FXPairType.MAJOR,
        instrument_type=FXInstrumentType.SPOT,

        market_id="FX-GLOBAL",

        base_currency="EUR",
        quote_currency="USD",

        country="GLOBAL",
        region="GLOBAL",
        exchange="OTC",

        session="LONDON_NEW_YORK",

        state=FXOpportunityState.QUALIFIED,
        bias=FXOpportunityBias.BULLISH,
        strength=FXOpportunityStrength.STRONG,

        summary=(
            "Upstream FX intelligence self-check opportunity."
        ),

        confidence=0.90,

        favorite=False,
        watchlisted=True,

        priority=FXScannerPriority.HIGH,

        source=FXSourceType.FX_INTELLIGENCE_ENGINE,

        metadata={
            # Simulates future upstream research output.
            "research_formula_generated": True,
            "fx_algorithm_generated": True,

            "pair_structure_analysis": True,
            "session_liquidity_analysis": True,
            "relative_currency_strength": True,
            "macro_event_sensitivity": True,
            "breakout_analysis": True,
            "breakout_confirmation": True,
            "exact_level_calculation": True,
        },
    )

    request = FXScannerRequest(
        mode=FXScannerMode.UNIVERSAL_FX,

        opportunities=[
            upstream
        ],

        scanner_filter=FXScannerFilter(),

        authenticated=True,

        metadata={
            "self_check": True
        },
    )

    result = run_fx_scanner(
        request
    )

    errors = validate_fx_scanner_integrity(
        request=request,
        result=result,
    )

    routed = (
        result.opportunities[0]
        if result.opportunities
        else None
    )

    truth_preserved = bool(
        routed
        and routed.symbol == upstream.symbol
        and routed.base_currency
        == upstream.base_currency
        and routed.quote_currency
        == upstream.quote_currency
        and routed.state == upstream.state
        and routed.bias == upstream.bias
        and routed.strength == upstream.strength
        and routed.confidence
        == upstream.confidence
        and routed.metadata.get(
            "upstream_truth"
        ) is True
    )

    scanner_did_not_generate = bool(
        routed
        and routed.metadata.get(
            "scanner_generated_intelligence"
        ) is False
        and routed.metadata.get(
            "scanner_generated_score"
        ) is False
        and routed.metadata.get(
            "scanner_generated_decision"
        ) is False
        and routed.metadata.get(
            "fx_algorithm_generated"
        ) is False
    )

    # The upstream research markers may exist in the
    # source metadata, but scanner authority remains false.
    upstream_research_seen = bool(
        routed
        and routed.metadata.get(
            "research_formula_generated"
        ) is True
        and routed.metadata.get(
            "fx_algorithm_generated"
        ) is False
    )

    return {
        "engine": FX_SCANNER_ENGINE,
        "version": FX_SCANNER_VERSION,

        "passed": (
            not errors
            and truth_preserved
            and scanner_did_not_generate
            and upstream_research_seen
        ),

        "errors": errors,

        "truth_preserved": truth_preserved,

        "scanner_did_not_generate_intelligence":
            scanner_did_not_generate,

        "upstream_research_marker_preserved":
            upstream_research_seen,

        "result_status":
            result.status.value,

        "result_count":
            len(result.opportunities),

        "fx_scanner_independent": True,

        "equity_scanner_dependency": False,
        "index_scanner_dependency": False,
        "commodity_scanner_dependency": False,
        "crypto_scanner_dependency": False,

        "formula_pluggable": True,

        "checked_at": _fx_now().isoformat(),
    }


# ============================================================================
# DEFAULT FACTORY
# ============================================================================


def create_default_fx_scanner(
    *,
    authenticated: bool = False,
) -> FXScannerController:

    controller = create_fx_scanner(
        authenticated=authenticated,
        mode=FXScannerMode.UNIVERSAL_FX,
    )

    return controller


# ============================================================================
# EXPORTS
# ============================================================================


__all__ = [
    # Constants
    "FX_SCANNER_ENGINE",
    "FX_SCANNER_VERSION",
    "FX_SCANNER_NAME",
    "FX_SCANNER_TITLE",
    "FX_SCANNER_DESCRIPTION",
    "FX_SCANNER_AUTHORITY",

    # Enums
    "FXScannerStatus",
    "FXScannerMode",
    "FXPairType",
    "FXInstrumentType",
    "FXOpportunityState",
    "FXOpportunityBias",
    "FXOpportunityStrength",
    "FXScannerPriority",
    "FXSourceType",

    # Contracts
    "FXMarketInput",
    "FXInstrumentInput",
    "UpstreamFXOpportunity",
    "FXScannerFilter",
    "FXScannerOpportunity",
    "FXScannerResult",
    "FXScannerRequest",
    "FXScannerSnapshot",
    "FXScannerState",
    "FXScannerHealth",

    # Helpers
    "normalize_fx_market",
    "normalize_fx_instrument",
    "normalize_upstream_fx_opportunity",
    "normalize_fx_filter",
    "normalize_fx_request",

    # Filtering
    "fx_opportunity_matches_filter",
    "filter_upstream_fx_opportunities",
    "filter_fx_markets",
    "filter_fx_instruments",

    # Routing / result
    "convert_upstream_fx_opportunity",
    "build_fx_scanner_result",
    "fx_scanner_source_status",
    "run_fx_scanner",

    # Controller
    "FXScannerController",
    "get_fx_scanner",
    "create_fx_scanner",
    "scan_fx_market",
    "scan_with_fx_scanner",

    # Serialization
    "serialize_fx_market",
    "serialize_fx_instrument",
    "serialize_upstream_fx_opportunity",
    "serialize_fx_filter",
    "serialize_fx_scanner_opportunity",
    "serialize_fx_scanner_result",
    "serialize_fx_scanner_request",
    "serialize_fx_scanner_snapshot",
    "serialize_fx_scanner_state",
    "serialize_fx_scanner_health",

    # Validation
    "validate_fx_market",
    "validate_fx_instrument",
    "validate_upstream_fx_opportunity",
    "validate_fx_scanner_filter",
    "validate_fx_scanner_opportunity",
    "validate_fx_scanner_request",
    "validate_fx_scanner_result",
    "validate_fx_scanner_state",
    "validate_fx_scanner_snapshot",
    "validate_fx_scanner_authority",
    "validate_fx_scanner_integrity",
    "validate_fx_scanner_contract",

    # Health / operations
    "build_fx_scanner_health",
    "fx_scanner_operational_check",

    # Diagnostics
    "diagnose_fx_scanner",
    "fx_scanner_summary",
    "fx_scanner_contract_manifest",
    "fx_scanner_module_check",
    "fx_scanner_self_check",

    # Factory
    "create_default_fx_scanner",
]
