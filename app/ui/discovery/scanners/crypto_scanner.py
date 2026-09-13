# app/ui/discovery/crypto_scanner.py

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List


# ============================================================
# CORE CONTRACT
# ============================================================

CRYPTO_SCANNER_ENGINE = "ROBOMLM_PLUS_CRYPTO_SCANNER"
CRYPTO_SCANNER_VERSION = "1.0"
CRYPTO_SCANNER_NAME = "Crypto Opportunity Scanner"
CRYPTO_SCANNER_TITLE = "Crypto Market Opportunity Scanner"
CRYPTO_SCANNER_DESCRIPTION = (
    "Dedicated crypto discovery scanner for presenting and routing "
    "upstream crypto opportunity intelligence across supported "
    "markets, exchanges, pairs and crypto instruments."
)


# ============================================================
# AUTHORITY BOUNDARY
# ============================================================

CRYPTO_SCANNER_AUTHORITY = {
    # Allowed presentation/orchestration authority
    "scanner_orchestration": True,
    "crypto_opportunity_presentation": True,
    "market_filtering": True,
    "region_filtering": True,
    "exchange_filtering": True,
    "asset_filtering": True,
    "pair_filtering": True,
    "instrument_filtering": True,
    "category_filtering": True,
    "quote_currency_filtering": True,
    "upstream_opportunity_consumption": True,
    "crypto_specific_intelligence_consumption": True,

    # Crypto intelligence itself belongs upstream
    "crypto_specific_algorithm_generation": False,
    "crypto_signal_generation": False,
    "crypto_score_generation": False,

    # Cross-scanner independence
    "equity_scanner_dependency": False,
    "equity_scanner_authority": False,
    "index_scanner_dependency": False,
    "index_scanner_authority": False,
    "commodity_scanner_dependency": False,
    "commodity_scanner_authority": False,
    "fx_scanner_dependency": False,
    "fx_scanner_authority": False,

    # Forbidden core authority
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

class CryptoScannerStatus(str, Enum):
    IDLE = "IDLE"
    LOADING = "LOADING"
    READY = "READY"
    DEGRADED = "DEGRADED"
    BLOCKED = "BLOCKED"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class CryptoScannerMode(str, Enum):
    UNIVERSAL_CRYPTO = "UNIVERSAL_CRYPTO"
    MARKET = "MARKET"
    EXCHANGE = "EXCHANGE"
    ASSET = "ASSET"
    PAIR = "PAIR"
    CATEGORY = "CATEGORY"
    QUOTE_CURRENCY = "QUOTE_CURRENCY"
    FAVORITES = "FAVORITES"
    WATCHLIST = "WATCHLIST"
    UNKNOWN = "UNKNOWN"


class CryptoAssetType(str, Enum):
    COIN = "COIN"
    TOKEN = "TOKEN"
    STABLECOIN = "STABLECOIN"
    DEFI = "DEFI"
    MEME = "MEME"
    LAYER1 = "LAYER1"
    LAYER2 = "LAYER2"
    OTHER_CRYPTO = "OTHER_CRYPTO"
    UNKNOWN = "UNKNOWN"


class CryptoInstrumentType(str, Enum):
    SPOT = "SPOT"
    PERPETUAL = "PERPETUAL"
    FUTURE = "FUTURE"
    OPTION = "OPTION"
    OTHER_DERIVATIVE = "OTHER_DERIVATIVE"
    UNKNOWN = "UNKNOWN"


class CryptoOpportunityState(str, Enum):
    UNKNOWN = "UNKNOWN"
    WATCH = "WATCH"
    DEVELOPING = "DEVELOPING"
    QUALIFIED = "QUALIFIED"
    INVALIDATED = "INVALIDATED"
    EXPIRED = "EXPIRED"


class CryptoOpportunityBias(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"


class CryptoOpportunityStrength(str, Enum):
    VERY_WEAK = "VERY_WEAK"
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    VERY_STRONG = "VERY_STRONG"
    UNKNOWN = "UNKNOWN"


class CryptoScannerPriority(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CryptoSourceType(str, Enum):
    UPSTREAM_OPPORTUNITY_ENGINE = "UPSTREAM_OPPORTUNITY_ENGINE"
    CRYPTO_OPPORTUNITY_ENGINE = "CRYPTO_OPPORTUNITY_ENGINE"
    DISCOVERY_ENGINE = "DISCOVERY_ENGINE"
    UNKNOWN = "UNKNOWN"


# ============================================================
# HELPERS
# ============================================================

def _crypto_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def _crypto_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default

    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "y", "on"}:
            return True
        if normalized in {"false", "0", "no", "n", "off"}:
            return False

    return bool(value)


def _crypto_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _crypto_enum(
    enum_type: type[Enum],
    value: Any,
    default: Enum,
) -> Enum:
    if isinstance(value, enum_type):
        return value

    text = _crypto_text(value).upper()

    if text:
        for member in enum_type:
            if member.value == text or member.name == text:
                return member

    return default


def _crypto_now() -> datetime:
    return datetime.now(timezone.utc)


# ============================================================
# MARKET / INSTRUMENT INPUT CONTRACTS
# ============================================================

@dataclass
class CryptoMarketInput:
    market_id: str
    market_name: str
    country: str = ""
    region: str = ""
    exchange: str = ""
    timezone: str = ""
    enabled: bool = True
    selected: bool = False
    crypto_available: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CryptoInstrumentInput:
    instrument_id: str
    symbol: str
    display_name: str = ""
    asset_type: CryptoAssetType = CryptoAssetType.UNKNOWN
    instrument_type: CryptoInstrumentType = CryptoInstrumentType.UNKNOWN
    market_id: str = ""
    exchange: str = ""
    base_asset: str = ""
    quote_asset: str = ""
    category: str = ""
    sector: str = ""
    enabled: bool = True
    selected: bool = False
    tradable: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# UPSTREAM CRYPTO OPPORTUNITY CONTRACT
# ============================================================

@dataclass
class UpstreamCryptoOpportunity:
    opportunity_id: str
    symbol: str
    instrument_id: str = ""
    instrument_name: str = ""

    asset_type: CryptoAssetType = CryptoAssetType.UNKNOWN
    instrument_type: CryptoInstrumentType = CryptoInstrumentType.UNKNOWN

    market_id: str = ""
    country: str = ""
    region: str = ""
    exchange: str = ""

    base_asset: str = ""
    quote_asset: str = ""
    category: str = ""
    sector: str = ""

    state: CryptoOpportunityState = CryptoOpportunityState.UNKNOWN
    bias: CryptoOpportunityBias = CryptoOpportunityBias.UNKNOWN
    strength: CryptoOpportunityStrength = CryptoOpportunityStrength.UNKNOWN

    summary: str = ""
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=lambda: _crypto_now())

    favorite: bool = False
    watchlisted: bool = False

    priority: CryptoScannerPriority = CryptoScannerPriority.NORMAL

    source: CryptoSourceType = CryptoSourceType.UNKNOWN

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# SCANNER FILTER CONTRACT
# ============================================================

@dataclass
class CryptoScannerFilter:
    market_ids: List[str] = field(default_factory=list)
    countries: List[str] = field(default_factory=list)
    regions: List[str] = field(default_factory=list)
    exchange_names: List[str] = field(default_factory=list)

    instrument_ids: List[str] = field(default_factory=list)
    symbols: List[str] = field(default_factory=list)

    asset_types: List[CryptoAssetType] = field(default_factory=list)
    instrument_types: List[CryptoInstrumentType] = field(default_factory=list)

    base_assets: List[str] = field(default_factory=list)
    quote_assets: List[str] = field(default_factory=list)

    categories: List[str] = field(default_factory=list)
    sectors: List[str] = field(default_factory=list)

    states: List[CryptoOpportunityState] = field(default_factory=list)
    biases: List[CryptoOpportunityBias] = field(default_factory=list)
    strengths: List[CryptoOpportunityStrength] = field(default_factory=list)

    favorites_only: bool = False
    watchlist_only: bool = False
    tradable_only: bool = False

    include_invalidated: bool = False
    include_expired: bool = False

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# ROUTED SCANNER OPPORTUNITY
# ============================================================

@dataclass
class CryptoScannerOpportunity:
    opportunity_id: str
    symbol: str
    instrument_id: str = ""
    instrument_name: str = ""

    asset_type: CryptoAssetType = CryptoAssetType.UNKNOWN
    instrument_type: CryptoInstrumentType = CryptoInstrumentType.UNKNOWN

    market_id: str = ""
    country: str = ""
    region: str = ""
    exchange: str = ""

    base_asset: str = ""
    quote_asset: str = ""
    category: str = ""
    sector: str = ""

    state: CryptoOpportunityState = CryptoOpportunityState.UNKNOWN
    bias: CryptoOpportunityBias = CryptoOpportunityBias.UNKNOWN
    strength: CryptoOpportunityStrength = CryptoOpportunityStrength.UNKNOWN

    summary: str = ""
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=lambda: _crypto_now())

    favorite: bool = False
    watchlisted: bool = False

    priority: CryptoScannerPriority = CryptoScannerPriority.NORMAL

    source: CryptoSourceType = CryptoSourceType.UNKNOWN

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# RESULT / REQUEST / SNAPSHOT CONTRACTS
# ============================================================

@dataclass
class CryptoScannerResult:
    status: CryptoScannerStatus
    mode: CryptoScannerMode

    opportunities: List[CryptoScannerOpportunity] = field(
        default_factory=list
    )

    total_input_opportunities: int = 0
    total_output_opportunities: int = 0

    source_available: bool = False
    source_errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    generated_at: datetime = field(default_factory=lambda: _crypto_now())

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CryptoScannerRequest:
    mode: CryptoScannerMode = CryptoScannerMode.UNIVERSAL_CRYPTO

    markets: List[CryptoMarketInput] = field(default_factory=list)
    instruments: List[CryptoInstrumentInput] = field(
        default_factory=list
    )
    opportunities: List[UpstreamCryptoOpportunity] = field(
        default_factory=list
    )

    scanner_filter: CryptoScannerFilter = field(
        default_factory=CryptoScannerFilter
    )

    authenticated: bool = False

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CryptoScannerSnapshot:
    request: CryptoScannerRequest
    result: CryptoScannerResult

    captured_at: datetime = field(default_factory=lambda: _crypto_now())

    metadata: Dict[str, Any] = field(default_factory=dict)
# ============================================================
# PART 2 — NORMALIZATION / FILTERING / ROUTING
# ============================================================

def normalize_crypto_market(
    value: CryptoMarketInput | Dict[str, Any],
) -> CryptoMarketInput:
    if isinstance(value, CryptoMarketInput):
        return value

    data = dict(value or {})

    return CryptoMarketInput(
        market_id=_crypto_text(data.get("market_id")),
        market_name=_crypto_text(data.get("market_name")),
        country=_crypto_text(data.get("country")),
        region=_crypto_text(data.get("region")),
        exchange=_crypto_text(data.get("exchange")),
        timezone=_crypto_text(data.get("timezone")),
        enabled=_crypto_bool(data.get("enabled"), True),
        selected=_crypto_bool(data.get("selected")),
        crypto_available=_crypto_bool(
            data.get("crypto_available"),
            True,
        ),
        metadata=dict(data.get("metadata") or {}),
    )


def normalize_crypto_instrument(
    value: CryptoInstrumentInput | Dict[str, Any],
) -> CryptoInstrumentInput:
    if isinstance(value, CryptoInstrumentInput):
        return value

    data = dict(value or {})

    return CryptoInstrumentInput(
        instrument_id=_crypto_text(data.get("instrument_id")),
        symbol=_crypto_text(data.get("symbol")),
        display_name=_crypto_text(data.get("display_name")),
        asset_type=_crypto_enum(
            CryptoAssetType,
            data.get("asset_type"),
            CryptoAssetType.UNKNOWN,
        ),
        instrument_type=_crypto_enum(
            CryptoInstrumentType,
            data.get("instrument_type"),
            CryptoInstrumentType.UNKNOWN,
        ),
        market_id=_crypto_text(data.get("market_id")),
        exchange=_crypto_text(data.get("exchange")),
        base_asset=_crypto_text(data.get("base_asset")),
        quote_asset=_crypto_text(data.get("quote_asset")),
        category=_crypto_text(data.get("category")),
        sector=_crypto_text(data.get("sector")),
        enabled=_crypto_bool(data.get("enabled"), True),
        selected=_crypto_bool(data.get("selected")),
        tradable=_crypto_bool(data.get("tradable"), True),
        metadata=dict(data.get("metadata") or {}),
    )


def normalize_upstream_crypto_opportunity(
    value: UpstreamCryptoOpportunity | Dict[str, Any],
) -> UpstreamCryptoOpportunity:
    if isinstance(value, UpstreamCryptoOpportunity):
        return value

    data = dict(value or {})

    timestamp = data.get("timestamp")

    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(
                timestamp.replace("Z", "+00:00")
            )
        except ValueError:
            timestamp = _crypto_now()

    if not isinstance(timestamp, datetime):
        timestamp = _crypto_now()

    return UpstreamCryptoOpportunity(
        opportunity_id=_crypto_text(data.get("opportunity_id")),
        symbol=_crypto_text(data.get("symbol")),
        instrument_id=_crypto_text(data.get("instrument_id")),
        instrument_name=_crypto_text(data.get("instrument_name")),

        asset_type=_crypto_enum(
            CryptoAssetType,
            data.get("asset_type"),
            CryptoAssetType.UNKNOWN,
        ),
        instrument_type=_crypto_enum(
            CryptoInstrumentType,
            data.get("instrument_type"),
            CryptoInstrumentType.UNKNOWN,
        ),

        market_id=_crypto_text(data.get("market_id")),
        country=_crypto_text(data.get("country")),
        region=_crypto_text(data.get("region")),
        exchange=_crypto_text(data.get("exchange")),

        base_asset=_crypto_text(data.get("base_asset")),
        quote_asset=_crypto_text(data.get("quote_asset")),
        category=_crypto_text(data.get("category")),
        sector=_crypto_text(data.get("sector")),

        state=_crypto_enum(
            CryptoOpportunityState,
            data.get("state"),
            CryptoOpportunityState.UNKNOWN,
        ),
        bias=_crypto_enum(
            CryptoOpportunityBias,
            data.get("bias"),
            CryptoOpportunityBias.UNKNOWN,
        ),
        strength=_crypto_enum(
            CryptoOpportunityStrength,
            data.get("strength"),
            CryptoOpportunityStrength.UNKNOWN,
        ),

        summary=_crypto_text(data.get("summary")),
        confidence=max(
            0.0,
            min(
                1.0,
                _crypto_float(data.get("confidence")),
            ),
        ),
        timestamp=timestamp,

        favorite=_crypto_bool(data.get("favorite")),
        watchlisted=_crypto_bool(data.get("watchlisted")),

        priority=_crypto_enum(
            CryptoScannerPriority,
            data.get("priority"),
            CryptoScannerPriority.NORMAL,
        ),

        source=_crypto_enum(
            CryptoSourceType,
            data.get("source"),
            CryptoSourceType.UNKNOWN,
        ),

        metadata=dict(data.get("metadata") or {}),
    )


def _normalize_crypto_string_list(
    values: Any,
) -> List[str]:
    if values is None:
        return []

    if isinstance(values, str):
        values = [values]

    return [
        _crypto_text(value)
        for value in values
        if _crypto_text(value)
    ]


def _normalize_crypto_enum_list(
    enum_type: type[Enum],
    values: Any,
) -> List[Enum]:
    if values is None:
        return []

    if isinstance(values, (str, enum_type)):
        values = [values]

    result: List[Enum] = []

    for value in values:
        normalized = _crypto_enum(
            enum_type,
            value,
            list(enum_type)[-1],
        )

        if normalized not in result:
            result.append(normalized)

    return result


def normalize_crypto_filter(
    value: CryptoScannerFilter | Dict[str, Any] | None,
) -> CryptoScannerFilter:
    if isinstance(value, CryptoScannerFilter):
        return value

    data = dict(value or {})

    return CryptoScannerFilter(
        market_ids=_normalize_crypto_string_list(
            data.get("market_ids")
        ),
        countries=_normalize_crypto_string_list(
            data.get("countries")
        ),
        regions=_normalize_crypto_string_list(
            data.get("regions")
        ),
        exchange_names=_normalize_crypto_string_list(
            data.get("exchange_names")
        ),

        instrument_ids=_normalize_crypto_string_list(
            data.get("instrument_ids")
        ),
        symbols=_normalize_crypto_string_list(
            data.get("symbols")
        ),

        asset_types=_normalize_crypto_enum_list(
            CryptoAssetType,
            data.get("asset_types"),
        ),
        instrument_types=_normalize_crypto_enum_list(
            CryptoInstrumentType,
            data.get("instrument_types"),
        ),

        base_assets=_normalize_crypto_string_list(
            data.get("base_assets")
        ),
        quote_assets=_normalize_crypto_string_list(
            data.get("quote_assets")
        ),

        categories=_normalize_crypto_string_list(
            data.get("categories")
        ),
        sectors=_normalize_crypto_string_list(
            data.get("sectors")
        ),

        states=_normalize_crypto_enum_list(
            CryptoOpportunityState,
            data.get("states"),
        ),
        biases=_normalize_crypto_enum_list(
            CryptoOpportunityBias,
            data.get("biases"),
        ),
        strengths=_normalize_crypto_enum_list(
            CryptoOpportunityStrength,
            data.get("strengths"),
        ),

        favorites_only=_crypto_bool(
            data.get("favorites_only")
        ),
        watchlist_only=_crypto_bool(
            data.get("watchlist_only")
        ),
        tradable_only=_crypto_bool(
            data.get("tradable_only")
        ),

        include_invalidated=_crypto_bool(
            data.get("include_invalidated")
        ),
        include_expired=_crypto_bool(
            data.get("include_expired")
        ),

        metadata=dict(data.get("metadata") or {}),
    )


def normalize_crypto_request(
    value: CryptoScannerRequest | Dict[str, Any],
) -> CryptoScannerRequest:
    if isinstance(value, CryptoScannerRequest):
        return value

    data = dict(value or {})

    markets = [
        normalize_crypto_market(item)
        for item in data.get("markets", [])
    ]

    instruments = [
        normalize_crypto_instrument(item)
        for item in data.get("instruments", [])
    ]

    opportunities = [
        normalize_upstream_crypto_opportunity(item)
        for item in data.get("opportunities", [])
    ]

    return CryptoScannerRequest(
        mode=_crypto_enum(
            CryptoScannerMode,
            data.get("mode"),
            CryptoScannerMode.UNIVERSAL_CRYPTO,
        ),
        markets=markets,
        instruments=instruments,
        opportunities=opportunities,
        scanner_filter=normalize_crypto_filter(
            data.get("scanner_filter")
        ),
        authenticated=_crypto_bool(
            data.get("authenticated")
        ),
        metadata=dict(data.get("metadata") or {}),
    )


# ============================================================
# FILTER HELPERS
# ============================================================

def _crypto_matches_list(
    value: str,
    allowed: List[str],
) -> bool:
    if not allowed:
        return True

    normalized = _crypto_text(value).upper()

    return any(
        normalized == _crypto_text(item).upper()
        for item in allowed
    )


def _crypto_matches_enum_list(
    value: Enum,
    allowed: List[Enum],
) -> bool:
    if not allowed:
        return True

    return value in allowed


# ============================================================
# OPPORTUNITY FILTER
# ============================================================

def crypto_opportunity_matches_filter(
    opportunity: UpstreamCryptoOpportunity,
    scanner_filter: CryptoScannerFilter,
) -> bool:

    if (
        opportunity.state
        == CryptoOpportunityState.INVALIDATED
        and not scanner_filter.include_invalidated
    ):
        return False

    if (
        opportunity.state
        == CryptoOpportunityState.EXPIRED
        and not scanner_filter.include_expired
    ):
        return False

    if not _crypto_matches_list(
        opportunity.market_id,
        scanner_filter.market_ids,
    ):
        return False

    if not _crypto_matches_list(
        opportunity.country,
        scanner_filter.countries,
    ):
        return False

    if not _crypto_matches_list(
        opportunity.region,
        scanner_filter.regions,
    ):
        return False

    if not _crypto_matches_list(
        opportunity.exchange,
        scanner_filter.exchange_names,
    ):
        return False

    if not _crypto_matches_list(
        opportunity.instrument_id,
        scanner_filter.instrument_ids,
    ):
        return False

    if not _crypto_matches_list(
        opportunity.symbol,
        scanner_filter.symbols,
    ):
        return False

    if not _crypto_matches_enum_list(
        opportunity.asset_type,
        scanner_filter.asset_types,
    ):
        return False

    if not _crypto_matches_enum_list(
        opportunity.instrument_type,
        scanner_filter.instrument_types,
    ):
        return False

    if not _crypto_matches_list(
        opportunity.base_asset,
        scanner_filter.base_assets,
    ):
        return False

    if not _crypto_matches_list(
        opportunity.quote_asset,
        scanner_filter.quote_assets,
    ):
        return False

    if not _crypto_matches_list(
        opportunity.category,
        scanner_filter.categories,
    ):
        return False

    if not _crypto_matches_list(
        opportunity.sector,
        scanner_filter.sectors,
    ):
        return False

    if not _crypto_matches_enum_list(
        opportunity.state,
        scanner_filter.states,
    ):
        return False

    if not _crypto_matches_enum_list(
        opportunity.bias,
        scanner_filter.biases,
    ):
        return False

    if not _crypto_matches_enum_list(
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

    return True


def filter_upstream_crypto_opportunities(
    opportunities: List[UpstreamCryptoOpportunity],
    scanner_filter: CryptoScannerFilter,
) -> List[UpstreamCryptoOpportunity]:

    return [
        opportunity
        for opportunity in opportunities
        if crypto_opportunity_matches_filter(
            opportunity,
            scanner_filter,
        )
    ]


# ============================================================
# MARKET FILTER
# ============================================================

def filter_crypto_markets(
    markets: List[CryptoMarketInput],
    scanner_filter: CryptoScannerFilter,
) -> List[CryptoMarketInput]:

    result: List[CryptoMarketInput] = []

    for market in markets:
        if not market.enabled:
            continue

        if not market.crypto_available:
            continue

        if not _crypto_matches_list(
            market.market_id,
            scanner_filter.market_ids,
        ):
            continue

        if not _crypto_matches_list(
            market.country,
            scanner_filter.countries,
        ):
            continue

        if not _crypto_matches_list(
            market.region,
            scanner_filter.regions,
        ):
            continue

        if not _crypto_matches_list(
            market.exchange,
            scanner_filter.exchange_names,
        ):
            continue

        result.append(market)

    return result


# ============================================================
# INSTRUMENT FILTER
# ============================================================

def filter_crypto_instruments(
    instruments: List[CryptoInstrumentInput],
    scanner_filter: CryptoScannerFilter,
) -> List[CryptoInstrumentInput]:

    result: List[CryptoInstrumentInput] = []

    for instrument in instruments:
        if not instrument.enabled:
            continue

        if (
            scanner_filter.tradable_only
            and not instrument.tradable
        ):
            continue

        if not _crypto_matches_list(
            instrument.instrument_id,
            scanner_filter.instrument_ids,
        ):
            continue

        if not _crypto_matches_list(
            instrument.symbol,
            scanner_filter.symbols,
        ):
            continue

        if not _crypto_matches_list(
            instrument.market_id,
            scanner_filter.market_ids,
        ):
            continue

        if not _crypto_matches_list(
            instrument.exchange,
            scanner_filter.exchange_names,
        ):
            continue

        if not _crypto_matches_enum_list(
            instrument.asset_type,
            scanner_filter.asset_types,
        ):
            continue

        if not _crypto_matches_enum_list(
            instrument.instrument_type,
            scanner_filter.instrument_types,
        ):
            continue

        if not _crypto_matches_list(
            instrument.base_asset,
            scanner_filter.base_assets,
        ):
            continue

        if not _crypto_matches_list(
            instrument.quote_asset,
            scanner_filter.quote_assets,
        ):
            continue

        if not _crypto_matches_list(
            instrument.category,
            scanner_filter.categories,
        ):
            continue

        if not _crypto_matches_list(
            instrument.sector,
            scanner_filter.sectors,
        ):
            continue

        result.append(instrument)

    return result


# ============================================================
# UPSTREAM → SCANNER ROUTING
# ============================================================

def convert_upstream_crypto_opportunity(
    opportunity: UpstreamCryptoOpportunity,
) -> CryptoScannerOpportunity:

    metadata = dict(opportunity.metadata or {})

    # Explicit truth-preservation contract.
    metadata.update({
        "upstream_truth": True,
        "scanner_generated_intelligence": False,
        "scanner_generated_score": False,
        "scanner_generated_decision": False,
        "crypto_algorithm_generated": False,
        "d13_modified": False,
        "risk_generated": False,
        "risk_overridden": False,
        "cas_bypassed": False,
        "execution_authority": False,
    })

    return CryptoScannerOpportunity(
        opportunity_id=opportunity.opportunity_id,
        symbol=opportunity.symbol,
        instrument_id=opportunity.instrument_id,
        instrument_name=opportunity.instrument_name,

        asset_type=opportunity.asset_type,
        instrument_type=opportunity.instrument_type,

        market_id=opportunity.market_id,
        country=opportunity.country,
        region=opportunity.region,
        exchange=opportunity.exchange,

        base_asset=opportunity.base_asset,
        quote_asset=opportunity.quote_asset,
        category=opportunity.category,
        sector=opportunity.sector,

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
# RESULT CONSTRUCTION
# ============================================================

def build_crypto_scanner_result(
    mode: CryptoScannerMode,
    input_opportunities: List[UpstreamCryptoOpportunity],
    filtered_opportunities: List[UpstreamCryptoOpportunity],
    source_available: bool,
    source_errors: List[str] | None = None,
    warnings: List[str] | None = None,
) -> CryptoScannerResult:

    routed = [
        convert_upstream_crypto_opportunity(
            opportunity
        )
        for opportunity in filtered_opportunities
    ]

    errors = list(source_errors or [])
    warning_list = list(warnings or [])

    if not input_opportunities:
        warning_list.append(
            "No upstream crypto opportunities supplied."
        )

    metadata = {
        "scanner_result": True,
        "upstream_truth_preserved": True,
        "crypto_scanner_independent": True,

        "crypto_algorithm_generated": False,
        "scanner_generated_intelligence": False,
        "scanner_generated_score": False,
        "scanner_generated_decision": False,

        "equity_scanner_dependency": False,
        "index_scanner_dependency": False,
        "commodity_scanner_dependency": False,
        "fx_scanner_dependency": False,

        "d13_modified": False,
        "risk_generated": False,
        "risk_overridden": False,
        "cas_bypassed": False,
        "execution_authority": False,
    }

    if errors:
        status = CryptoScannerStatus.DEGRADED
    elif not source_available:
        status = CryptoScannerStatus.DEGRADED
    else:
        status = CryptoScannerStatus.READY

    return CryptoScannerResult(
        status=status,
        mode=mode,
        opportunities=routed,
        total_input_opportunities=len(
            input_opportunities
        ),
        total_output_opportunities=len(routed),
        source_available=source_available,
        source_errors=errors,
        warnings=warning_list,
        generated_at=_crypto_now(),
        metadata=metadata,
    )


# ============================================================
# SOURCE STATUS
# ============================================================

def crypto_scanner_source_status(
    authenticated: bool,
    opportunities: List[UpstreamCryptoOpportunity],
    source_errors: List[str] | None = None,
) -> tuple[CryptoScannerStatus, bool]:

    if not authenticated:
        return CryptoScannerStatus.BLOCKED, False

    if source_errors:
        return CryptoScannerStatus.DEGRADED, False

    if not opportunities:
        return CryptoScannerStatus.DEGRADED, False

    return CryptoScannerStatus.READY, True
# ============================================================
# PART 3 — STATE / ORCHESTRATION / CONTROLLER
# ============================================================

@dataclass
class CryptoScannerState:
    initialized: bool = False
    ready: bool = False
    authenticated: bool = False

    status: CryptoScannerStatus = CryptoScannerStatus.IDLE
    mode: CryptoScannerMode = CryptoScannerMode.UNIVERSAL_CRYPTO

    request_count: int = 0
    scan_count: int = 0

    last_error: str = ""
    last_scan_at: datetime | None = None

    metadata: Dict[str, Any] = field(default_factory=dict)


def create_crypto_scanner_state(
    authenticated: bool = False,
    mode: CryptoScannerMode = CryptoScannerMode.UNIVERSAL_CRYPTO,
) -> CryptoScannerState:

    return CryptoScannerState(
        initialized=False,
        ready=False,
        authenticated=bool(authenticated),
        status=(
            CryptoScannerStatus.IDLE
            if authenticated
            else CryptoScannerStatus.BLOCKED
        ),
        mode=mode,
    )


def normalize_crypto_scanner_state(
    value: CryptoScannerState | Dict[str, Any],
) -> CryptoScannerState:

    if isinstance(value, CryptoScannerState):
        return value

    data = dict(value or {})

    return CryptoScannerState(
        initialized=_crypto_bool(
            data.get("initialized")
        ),
        ready=_crypto_bool(
            data.get("ready")
        ),
        authenticated=_crypto_bool(
            data.get("authenticated")
        ),
        status=_crypto_enum(
            CryptoScannerStatus,
            data.get("status"),
            CryptoScannerStatus.UNKNOWN,
        ),
        mode=_crypto_enum(
            CryptoScannerMode,
            data.get("mode"),
            CryptoScannerMode.UNIVERSAL_CRYPTO,
        ),
        request_count=int(
            _crypto_float(data.get("request_count"))
        ),
        scan_count=int(
            _crypto_float(data.get("scan_count"))
        ),
        last_error=_crypto_text(
            data.get("last_error")
        ),
        last_scan_at=data.get("last_scan_at"),
        metadata=dict(data.get("metadata") or {}),
    )


# ============================================================
# SCANNER ORCHESTRATION
# ============================================================

def run_crypto_scanner(
    request: CryptoScannerRequest | Dict[str, Any],
) -> CryptoScannerResult:

    normalized = normalize_crypto_request(request)

    scanner_filter = normalized.scanner_filter

    # --------------------------------------------------------
    # Authentication boundary
    # --------------------------------------------------------
    if not normalized.authenticated:
        return CryptoScannerResult(
            status=CryptoScannerStatus.BLOCKED,
            mode=normalized.mode,
            opportunities=[],
            total_input_opportunities=len(
                normalized.opportunities
            ),
            total_output_opportunities=0,
            source_available=False,
            source_errors=[],
            warnings=[
                "Crypto scanner requires an authenticated session."
            ],
            generated_at=_crypto_now(),
            metadata={
                "scanner_result": True,
                "blocked": True,
                "upstream_truth_preserved": True,
                "crypto_scanner_independent": True,
                "crypto_algorithm_generated": False,
                "scanner_generated_intelligence": False,
                "scanner_generated_score": False,
                "scanner_generated_decision": False,
                "d13_modified": False,
                "risk_generated": False,
                "risk_overridden": False,
                "cas_bypassed": False,
                "execution_authority": False,
            },
        )

    # --------------------------------------------------------
    # Normalize source collections
    # --------------------------------------------------------
    markets = [
        normalize_crypto_market(item)
        for item in normalized.markets
    ]

    instruments = [
        normalize_crypto_instrument(item)
        for item in normalized.instruments
    ]

    opportunities = [
        normalize_upstream_crypto_opportunity(item)
        for item in normalized.opportunities
    ]

    # --------------------------------------------------------
    # Filter supported market universe
    # --------------------------------------------------------
    filtered_markets = filter_crypto_markets(
        markets,
        scanner_filter,
    )

    # --------------------------------------------------------
    # Filter supported instrument universe
    # --------------------------------------------------------
    filtered_instruments = filter_crypto_instruments(
        instruments,
        scanner_filter,
    )

    # --------------------------------------------------------
    # Opportunity filtering
    # --------------------------------------------------------
    filtered_opportunities = (
        filter_upstream_crypto_opportunities(
            opportunities,
            scanner_filter,
        )
    )

    warnings: List[str] = []

    # --------------------------------------------------------
    # Explicit market universe restriction
    # --------------------------------------------------------
    if normalized.markets:

        enabled_market_ids = {
            market.market_id
            for market in filtered_markets
            if market.market_id
        }

        if enabled_market_ids:
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
            filtered_opportunities = []

            warnings.append(
                "No enabled crypto market matched the scanner filter."
            )

    else:
        warnings.append(
            "No explicit crypto market universe supplied; "
            "scanner is using upstream opportunity universe."
        )

    # --------------------------------------------------------
    # Explicit instrument universe restriction
    # --------------------------------------------------------
    if normalized.instruments:

        enabled_instrument_ids = {
            instrument.instrument_id
            for instrument in filtered_instruments
            if instrument.instrument_id
        }

        if enabled_instrument_ids:
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
            filtered_opportunities = []

            warnings.append(
                "No enabled crypto instrument matched "
                "the scanner filter."
            )

    else:
        warnings.append(
            "No explicit crypto instrument universe supplied; "
            "scanner is using upstream opportunity universe."
        )

    # --------------------------------------------------------
    # Source status
    # --------------------------------------------------------
    status, source_available = crypto_scanner_source_status(
        authenticated=normalized.authenticated,
        opportunities=opportunities,
        source_errors=[],
    )

    # --------------------------------------------------------
    # Build final routed result
    # --------------------------------------------------------
    result = build_crypto_scanner_result(
        mode=normalized.mode,
        input_opportunities=opportunities,
        filtered_opportunities=filtered_opportunities,
        source_available=source_available,
        source_errors=[],
        warnings=warnings,
    )

    # Preserve actual source status if authentication/source
    # state indicates a blocked/degraded condition.
    if status == CryptoScannerStatus.BLOCKED:
        result.status = status

    result.metadata.update({
        "filtered_market_count": len(filtered_markets),
        "filtered_instrument_count": len(
            filtered_instruments
        ),
        "upstream_opportunity_count": len(
            opportunities
        ),
        "routed_opportunity_count": len(
            filtered_opportunities
        ),
        "crypto_scanner_independent": True,
        "equity_scanner_dependency": False,
        "index_scanner_dependency": False,
        "commodity_scanner_dependency": False,
        "fx_scanner_dependency": False,
    })

    return result


# ============================================================
# CONTROLLER
# ============================================================

class CryptoScannerController:

    def __init__(
        self,
        state: CryptoScannerState | None = None,
    ) -> None:

        self._state = (
            normalize_crypto_scanner_state(state)
            if state is not None
            else create_crypto_scanner_state()
        )

        self._last_request: CryptoScannerRequest | None = None
        self._last_result: CryptoScannerResult | None = None

        self._request_history: List[
            CryptoScannerRequest
        ] = []

        self._result_history: List[
            CryptoScannerResult
        ] = []

    # --------------------------------------------------------
    # Properties
    # --------------------------------------------------------

    @property
    def state(self) -> CryptoScannerState:
        return self._state

    @property
    def status(self) -> CryptoScannerStatus:
        return self._state.status

    @property
    def mode(self) -> CryptoScannerMode:
        return self._state.mode

    @property
    def authenticated(self) -> bool:
        return self._state.authenticated

    @property
    def last_request(
        self,
    ) -> CryptoScannerRequest | None:
        return self._last_request

    @property
    def last_result(
        self,
    ) -> CryptoScannerResult | None:
        return self._last_result

    # --------------------------------------------------------
    # Lifecycle
    # --------------------------------------------------------

    def initialize(
        self,
        authenticated: bool | None = None,
    ) -> CryptoScannerState:

        if authenticated is not None:
            self._state.authenticated = bool(
                authenticated
            )

        self._state.initialized = True

        if not self._state.authenticated:
            self._state.ready = False
            self._state.status = (
                CryptoScannerStatus.BLOCKED
            )
            return self._state

        self._state.ready = True
        self._state.status = CryptoScannerStatus.READY
        self._state.last_error = ""

        return self._state

    # --------------------------------------------------------
    # Scan
    # --------------------------------------------------------

    def scan(
        self,
        request: CryptoScannerRequest | Dict[str, Any],
    ) -> CryptoScannerResult:

        normalized = normalize_crypto_request(request)

        self._state.request_count += 1
        self._state.status = CryptoScannerStatus.LOADING

        normalized.authenticated = (
            normalized.authenticated
            or self._state.authenticated
        )

        normalized.mode = self._state.mode

        self._last_request = normalized

        self._request_history.append(normalized)

        if len(self._request_history) > 500:
            del self._request_history[:-500]

        try:
            result = run_crypto_scanner(normalized)

            self._last_result = result
            self._result_history.append(result)

            if len(self._result_history) > 500:
                del self._result_history[:-500]

            self._state.scan_count += 1
            self._state.status = result.status
            self._state.ready = (
                result.status
                == CryptoScannerStatus.READY
            )
            self._state.last_error = ""
            self._state.last_scan_at = _crypto_now()

            return result

        except Exception as exc:
            error = _crypto_text(exc)

            self._state.status = (
                CryptoScannerStatus.ERROR
            )
            self._state.ready = False
            self._state.last_error = error

            result = CryptoScannerResult(
                status=CryptoScannerStatus.ERROR,
                mode=self._state.mode,
                opportunities=[],
                total_input_opportunities=len(
                    normalized.opportunities
                ),
                total_output_opportunities=0,
                source_available=False,
                source_errors=[error],
                warnings=[],
                generated_at=_crypto_now(),
                metadata={
                    "scanner_result": True,
                    "upstream_truth_preserved": True,
                    "crypto_algorithm_generated": False,
                    "scanner_generated_intelligence": False,
                    "scanner_generated_score": False,
                    "scanner_generated_decision": False,
                    "d13_modified": False,
                    "risk_generated": False,
                    "risk_overridden": False,
                    "cas_bypassed": False,
                    "execution_authority": False,
                },
            )

            self._last_result = result
            self._result_history.append(result)

            if len(self._result_history) > 500:
                del self._result_history[:-500]

            return result

    # --------------------------------------------------------
    # Mode
    # --------------------------------------------------------

    def set_mode(
        self,
        mode: CryptoScannerMode | str,
    ) -> CryptoScannerMode:

        self._state.mode = _crypto_enum(
            CryptoScannerMode,
            mode,
            CryptoScannerMode.UNIVERSAL_CRYPTO,
        )

        return self._state.mode

    # --------------------------------------------------------
    # Authentication
    # --------------------------------------------------------

    def set_authenticated(
        self,
        authenticated: bool,
    ) -> CryptoScannerState:

        self._state.authenticated = bool(
            authenticated
        )

        if not self._state.authenticated:
            self._state.ready = False
            self._state.status = (
                CryptoScannerStatus.BLOCKED
            )
        elif self._state.initialized:
            self._state.ready = True
            self._state.status = (
                CryptoScannerStatus.READY
            )

        return self._state

    # --------------------------------------------------------
    # Block / Reset
    # --------------------------------------------------------

    def block(self) -> CryptoScannerState:

        self._state.ready = False
        self._state.status = (
            CryptoScannerStatus.BLOCKED
        )

        return self._state

    def reset(self) -> CryptoScannerState:

        authenticated = self._state.authenticated

        self._state = create_crypto_scanner_state(
            authenticated=authenticated,
            mode=CryptoScannerMode.UNIVERSAL_CRYPTO,
        )

        self._last_request = None
        self._last_result = None

        self._request_history.clear()
        self._result_history.clear()

        return self._state

    # --------------------------------------------------------
    # Snapshot
    # --------------------------------------------------------

    def snapshot(self) -> CryptoScannerSnapshot:

        request = (
            self._last_request
            if self._last_request is not None
            else CryptoScannerRequest(
                mode=self._state.mode,
                authenticated=self._state.authenticated,
            )
        )

        result = (
            self._last_result
            if self._last_result is not None
            else CryptoScannerResult(
                status=self._state.status,
                mode=self._state.mode,
                source_available=False,
                warnings=[
                    "No crypto scan has been executed."
                ],
            )
        )

        return CryptoScannerSnapshot(
            request=request,
            result=result,
            captured_at=_crypto_now(),
            metadata={
                "scanner_snapshot": True,
                "upstream_truth_preserved": True,
                "crypto_scanner_independent": True,
                "crypto_algorithm_generated": False,
                "scanner_generated_intelligence": False,
                "scanner_generated_score": False,
                "scanner_generated_decision": False,
                "equity_scanner_dependency": False,
                "index_scanner_dependency": False,
                "commodity_scanner_dependency": False,
                "fx_scanner_dependency": False,
                "d13_modified": False,
                "risk_generated": False,
                "risk_overridden": False,
                "cas_bypassed": False,
                "execution_authority": False,
            },
        )

    # --------------------------------------------------------
    # History
    # --------------------------------------------------------

    @property
    def request_history(
        self,
    ) -> List[CryptoScannerRequest]:

        return list(self._request_history)

    @property
    def result_history(
        self,
    ) -> List[CryptoScannerResult]:

        return list(self._result_history)


# ============================================================
# DEFAULT CONTROLLER
# ============================================================

_DEFAULT_CRYPTO_SCANNER = CryptoScannerController()


def get_crypto_scanner() -> CryptoScannerController:
    return _DEFAULT_CRYPTO_SCANNER


def create_crypto_scanner(
    authenticated: bool = False,
    mode: CryptoScannerMode = CryptoScannerMode.UNIVERSAL_CRYPTO,
) -> CryptoScannerController:

    controller = CryptoScannerController(
        create_crypto_scanner_state(
            authenticated=authenticated,
            mode=mode,
        )
    )

    controller.initialize(authenticated)

    return controller


# ============================================================
# PUBLIC SCAN HELPERS
# ============================================================

def scan_crypto_market(
    opportunities: List[
        UpstreamCryptoOpportunity
    ],
    authenticated: bool = True,
    scanner_filter: CryptoScannerFilter | None = None,
    mode: CryptoScannerMode = CryptoScannerMode.UNIVERSAL_CRYPTO,
) -> CryptoScannerResult:

    request = CryptoScannerRequest(
        mode=mode,
        opportunities=opportunities,
        scanner_filter=(
            scanner_filter
            or CryptoScannerFilter()
        ),
        authenticated=authenticated,
    )

    return run_crypto_scanner(request)


def scan_with_crypto_scanner(
    request: CryptoScannerRequest | Dict[str, Any],
) -> CryptoScannerResult:

    return run_crypto_scanner(request)
# ============================================================
# PART 4 — SERIALIZATION / VALIDATION / HEALTH
# ============================================================

def _serialize_crypto_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, list):
        return [
            _serialize_crypto_value(item)
            for item in value
        ]

    if isinstance(value, tuple):
        return [
            _serialize_crypto_value(item)
            for item in value
        ]

    if isinstance(value, dict):
        return {
            str(key): _serialize_crypto_value(item)
            for key, item in value.items()
        }

    if hasattr(value, "__dataclass_fields__"):
        return {
            key: _serialize_crypto_value(
                getattr(value, key)
            )
            for key in value.__dataclass_fields__
        }

    return value


# ============================================================
# SERIALIZERS
# ============================================================

def serialize_crypto_market(
    value: CryptoMarketInput,
) -> Dict[str, Any]:
    return _serialize_crypto_value(value)


def serialize_crypto_instrument(
    value: CryptoInstrumentInput,
) -> Dict[str, Any]:
    return _serialize_crypto_value(value)


def serialize_upstream_crypto_opportunity(
    value: UpstreamCryptoOpportunity,
) -> Dict[str, Any]:
    return _serialize_crypto_value(value)


def serialize_crypto_scanner_filter(
    value: CryptoScannerFilter,
) -> Dict[str, Any]:
    return _serialize_crypto_value(value)


def serialize_crypto_scanner_opportunity(
    value: CryptoScannerOpportunity,
) -> Dict[str, Any]:
    return _serialize_crypto_value(value)


def serialize_crypto_scanner_result(
    value: CryptoScannerResult,
) -> Dict[str, Any]:
    return _serialize_crypto_value(value)


def serialize_crypto_scanner_request(
    value: CryptoScannerRequest,
) -> Dict[str, Any]:
    return _serialize_crypto_value(value)


def serialize_crypto_scanner_snapshot(
    value: CryptoScannerSnapshot,
) -> Dict[str, Any]:
    return _serialize_crypto_value(value)


def serialize_crypto_scanner_state(
    value: CryptoScannerState,
) -> Dict[str, Any]:
    return _serialize_crypto_value(value)


# ============================================================
# MARKET VALIDATION
# ============================================================

def validate_crypto_market(
    value: CryptoMarketInput,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(value, CryptoMarketInput):
        return ["Invalid CryptoMarketInput type."]

    if not value.market_id:
        errors.append("market_id is required.")

    if not value.market_name:
        errors.append("market_name is required.")

    if value.enabled and not value.crypto_available:
        errors.append(
            "Enabled crypto market must have crypto_available=True."
        )

    return errors


# ============================================================
# INSTRUMENT VALIDATION
# ============================================================

def validate_crypto_instrument(
    value: CryptoInstrumentInput,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(value, CryptoInstrumentInput):
        return ["Invalid CryptoInstrumentInput type."]

    if not value.instrument_id:
        errors.append("instrument_id is required.")

    if not value.symbol:
        errors.append("symbol is required.")

    if (
        value.tradable
        and not value.enabled
    ):
        errors.append(
            "Tradable crypto instrument cannot be disabled."
        )

    return errors


# ============================================================
# UPSTREAM OPPORTUNITY VALIDATION
# ============================================================

def validate_upstream_crypto_opportunity(
    value: UpstreamCryptoOpportunity,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        value,
        UpstreamCryptoOpportunity,
    ):
        return [
            "Invalid UpstreamCryptoOpportunity type."
        ]

    if not value.opportunity_id:
        errors.append(
            "opportunity_id is required."
        )

    if not value.symbol:
        errors.append(
            "symbol is required."
        )

    if not (
        0.0 <= value.confidence <= 1.0
    ):
        errors.append(
            "confidence must be between 0 and 1."
        )

    if (
        value.state
        == CryptoOpportunityState.UNKNOWN
    ):
        errors.append(
            "Opportunity state cannot be UNKNOWN."
        )

    return errors


# ============================================================
# FILTER VALIDATION
# ============================================================

def validate_crypto_scanner_filter(
    value: CryptoScannerFilter,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        value,
        CryptoScannerFilter,
    ):
        return [
            "Invalid CryptoScannerFilter type."
        ]

    enum_collections = (
        (
            "asset_types",
            value.asset_types,
            CryptoAssetType,
        ),
        (
            "instrument_types",
            value.instrument_types,
            CryptoInstrumentType,
        ),
        (
            "states",
            value.states,
            CryptoOpportunityState,
        ),
        (
            "biases",
            value.biases,
            CryptoOpportunityBias,
        ),
        (
            "strengths",
            value.strengths,
            CryptoOpportunityStrength,
        ),
    )

    for field_name, values, enum_type in enum_collections:
        for item in values:
            if not isinstance(item, enum_type):
                errors.append(
                    f"{field_name} contains invalid enum value."
                )

    return errors


# ============================================================
# ROUTED OPPORTUNITY VALIDATION
# ============================================================

def validate_crypto_scanner_opportunity(
    value: CryptoScannerOpportunity,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        value,
        CryptoScannerOpportunity,
    ):
        return [
            "Invalid CryptoScannerOpportunity type."
        ]

    if not value.opportunity_id:
        errors.append(
            "opportunity_id is required."
        )

    if not value.symbol:
        errors.append(
            "symbol is required."
        )

    if not (
        0.0 <= value.confidence <= 1.0
    ):
        errors.append(
            "confidence must be between 0 and 1."
        )

    metadata = value.metadata or {}

    if metadata.get("upstream_truth") is not True:
        errors.append(
            "upstream_truth must be True."
        )

    forbidden_truth_flags = (
        "scanner_generated_intelligence",
        "scanner_generated_score",
        "scanner_generated_decision",
        "crypto_algorithm_generated",
        "d13_modified",
        "risk_generated",
        "risk_overridden",
        "cas_bypassed",
        "execution_authority",
    )

    for flag in forbidden_truth_flags:
        if metadata.get(flag) is True:
            errors.append(
                f"{flag} must be False."
            )

    return errors


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_crypto_scanner_request(
    value: CryptoScannerRequest,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        value,
        CryptoScannerRequest,
    ):
        return [
            "Invalid CryptoScannerRequest type."
        ]

    errors.extend(
        validate_crypto_scanner_filter(
            value.scanner_filter
        )
    )

    for market in value.markets:
        errors.extend(
            validate_crypto_market(market)
        )

    for instrument in value.instruments:
        errors.extend(
            validate_crypto_instrument(instrument)
        )

    for opportunity in value.opportunities:
        errors.extend(
            validate_upstream_crypto_opportunity(
                opportunity
            )
        )

    return errors


# ============================================================
# RESULT VALIDATION
# ============================================================

def validate_crypto_scanner_result(
    value: CryptoScannerResult,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        value,
        CryptoScannerResult,
    ):
        return [
            "Invalid CryptoScannerResult type."
        ]

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
            "opportunity count."
        )

    for opportunity in value.opportunities:
        errors.extend(
            validate_crypto_scanner_opportunity(
                opportunity
            )
        )

    metadata = value.metadata or {}

    if metadata.get(
        "upstream_truth_preserved"
    ) is not True:
        errors.append(
            "upstream_truth_preserved must be True."
        )

    forbidden_flags = (
        "crypto_algorithm_generated",
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
            errors.append(
                f"{flag} must be False."
            )

    return errors


# ============================================================
# STATE VALIDATION
# ============================================================

def validate_crypto_scanner_state(
    value: CryptoScannerState,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        value,
        CryptoScannerState,
    ):
        return [
            "Invalid CryptoScannerState type."
        ]

    if value.request_count < 0:
        errors.append(
            "request_count cannot be negative."
        )

    if value.scan_count < 0:
        errors.append(
            "scan_count cannot be negative."
        )

    if (
        value.ready
        and not value.initialized
    ):
        errors.append(
            "Scanner cannot be ready before initialization."
        )

    if (
        value.ready
        and not value.authenticated
    ):
        errors.append(
            "Scanner cannot be ready without authentication."
        )

    if (
        not value.authenticated
        and value.status
        not in {
            CryptoScannerStatus.BLOCKED,
            CryptoScannerStatus.IDLE,
        }
    ):
        errors.append(
            "Unauthenticated scanner has invalid status."
        )

    return errors


# ============================================================
# SNAPSHOT VALIDATION
# ============================================================

def validate_crypto_scanner_snapshot(
    value: CryptoScannerSnapshot,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        value,
        CryptoScannerSnapshot,
    ):
        return [
            "Invalid CryptoScannerSnapshot type."
        ]

    errors.extend(
        validate_crypto_scanner_request(
            value.request
        )
    )

    errors.extend(
        validate_crypto_scanner_result(
            value.result
        )
    )

    metadata = value.metadata or {}

    if metadata.get(
        "scanner_snapshot"
    ) is not True:
        errors.append(
            "scanner_snapshot must be True."
        )

    if metadata.get(
        "crypto_scanner_independent"
    ) is not True:
        errors.append(
            "crypto_scanner_independent must be True."
        )

    if metadata.get(
        "upstream_truth_preserved"
    ) is not True:
        errors.append(
            "upstream_truth_preserved must be True."
        )

    return errors


# ============================================================
# AUTHORITY VALIDATION
# ============================================================

def validate_crypto_scanner_authority() -> List[str]:

    errors: List[str] = []

    required_true = (
        "scanner_orchestration",
        "crypto_opportunity_presentation",
        "market_filtering",
        "region_filtering",
        "exchange_filtering",
        "asset_filtering",
        "pair_filtering",
        "instrument_filtering",
        "category_filtering",
        "quote_currency_filtering",
        "upstream_opportunity_consumption",
        "crypto_specific_intelligence_consumption",
    )

    required_false = (
        "crypto_specific_algorithm_generation",
        "crypto_signal_generation",
        "crypto_score_generation",
        "equity_scanner_dependency",
        "equity_scanner_authority",
        "index_scanner_dependency",
        "index_scanner_authority",
        "commodity_scanner_dependency",
        "commodity_scanner_authority",
        "fx_scanner_dependency",
        "fx_scanner_authority",
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

    for key in required_true:
        if CRYPTO_SCANNER_AUTHORITY.get(key) is not True:
            errors.append(
                f"Authority flag {key} must be True."
            )

    for key in required_false:
        if CRYPTO_SCANNER_AUTHORITY.get(key) is not False:
            errors.append(
                f"Authority flag {key} must be False."
            )

    return errors


# ============================================================
# HEALTH CONTRACT
# ============================================================

@dataclass
class CryptoScannerHealth:
    engine: str = CRYPTO_SCANNER_ENGINE
    version: str = CRYPTO_SCANNER_VERSION

    operational: bool = False
    initialized: bool = False
    ready: bool = False
    authenticated: bool = False

    status: CryptoScannerStatus = (
        CryptoScannerStatus.IDLE
    )

    critical_scanner: bool = True
    crypto_scanner_independent: bool = True

    equity_scanner_dependency: bool = False
    index_scanner_dependency: bool = False
    commodity_scanner_dependency: bool = False
    fx_scanner_dependency: bool = False

    # --------------------------------------------------------
    # Future crypto intelligence research readiness
    # --------------------------------------------------------
    crypto_market_structure_analysis: bool = False
    crypto_liquidity_analysis: bool = False
    crypto_order_flow_analysis: bool = False
    crypto_funding_analysis: bool = False
    crypto_open_interest_analysis: bool = False
    crypto_liquidation_analysis: bool = False
    crypto_volatility_regime_analysis: bool = False
    crypto_breakout_analysis: bool = False
    crypto_confirmation_analysis: bool = False
    crypto_exact_levels: bool = False

    errors: List[str] = field(
        default_factory=list
    )
    warnings: List[str] = field(
        default_factory=list
    )

    checked_at: datetime = field(
        default_factory=lambda: _crypto_now()
    )


def build_crypto_scanner_health(
    state: CryptoScannerState,
) -> CryptoScannerHealth:

    errors = validate_crypto_scanner_state(
        state
    )

    authority_errors = (
        validate_crypto_scanner_authority()
    )

    errors.extend(authority_errors)

    operational = (
        not errors
        and state.initialized
        and state.authenticated
        and state.status
        not in {
            CryptoScannerStatus.ERROR,
            CryptoScannerStatus.BLOCKED,
        }
    )

    warnings: List[str] = []

    if not state.authenticated:
        warnings.append(
            "Crypto scanner is not authenticated."
        )

    warnings.append(
        "Crypto-specific intelligence algorithms "
        "remain upstream and research-pluggable."
    )

    return CryptoScannerHealth(
        engine=CRYPTO_SCANNER_ENGINE,
        version=CRYPTO_SCANNER_VERSION,
        operational=operational,
        initialized=state.initialized,
        ready=state.ready,
        authenticated=state.authenticated,
        status=state.status,

        critical_scanner=True,
        crypto_scanner_independent=True,

        equity_scanner_dependency=False,
        index_scanner_dependency=False,
        commodity_scanner_dependency=False,
        fx_scanner_dependency=False,

        crypto_market_structure_analysis=False,
        crypto_liquidity_analysis=False,
        crypto_order_flow_analysis=False,
        crypto_funding_analysis=False,
        crypto_open_interest_analysis=False,
        crypto_liquidation_analysis=False,
        crypto_volatility_regime_analysis=False,
        crypto_breakout_analysis=False,
        crypto_confirmation_analysis=False,
        crypto_exact_levels=False,

        errors=errors,
        warnings=warnings,
        checked_at=_crypto_now(),
    )


def serialize_crypto_scanner_health(
    value: CryptoScannerHealth,
) -> Dict[str, Any]:

    return _serialize_crypto_value(value)


# ============================================================
# OPERATIONAL CHECK
# ============================================================

def crypto_scanner_operational_check(
    state: CryptoScannerState | None = None,
) -> Dict[str, Any]:

    active_state = (
        state
        if state is not None
        else create_crypto_scanner_state()
    )

    health = build_crypto_scanner_health(
        active_state
    )

    return {
        "engine": CRYPTO_SCANNER_ENGINE,
        "version": CRYPTO_SCANNER_VERSION,
        "operational": health.operational,
        "initialized": health.initialized,
        "ready": health.ready,
        "authenticated": health.authenticated,
        "status": health.status.value,

        "critical_scanner": True,
        "crypto_scanner_independent": True,

        "equity_scanner_dependency": False,
        "index_scanner_dependency": False,
        "commodity_scanner_dependency": False,
        "fx_scanner_dependency": False,

        # Future research capability remains disabled
        # until validated upstream intelligence is integrated.
        "crypto_market_structure_analysis": False,
        "crypto_liquidity_analysis": False,
        "crypto_order_flow_analysis": False,
        "crypto_funding_analysis": False,
        "crypto_open_interest_analysis": False,
        "crypto_liquidation_analysis": False,
        "crypto_volatility_regime_analysis": False,
        "crypto_breakout_analysis": False,
        "crypto_confirmation_analysis": False,
        "crypto_exact_levels": False,

        # Forbidden authority
        "intelligence_generation": False,
        "decision_generation": False,
        "d13_modification": False,
        "risk_generation": False,
        "risk_override": False,
        "cas_generation": False,
        "cas_bypass": False,
        "execution": False,
        "order_authority": False,
        "position_authority": False,
        "upstream_mutation": False,

        "errors": list(health.errors),
        "warnings": list(health.warnings),
        "checked_at": health.checked_at.isoformat(),
    }
# ============================================================
# PART 5 — DIAGNOSTICS / CONTRACT / SELF-CHECK / EXPORTS
# ============================================================


def diagnose_crypto_scanner(
    state: CryptoScannerState | None = None,
    result: CryptoScannerResult | None = None,
) -> Dict[str, Any]:
    """Return a presentation-safe diagnostic report."""

    active_state = (
        state
        if state is not None
        else create_crypto_scanner_state()
    )

    health = build_crypto_scanner_health(
        active_state
    )

    result_errors: List[str] = []

    if result is not None:
        result_errors.extend(
            validate_crypto_scanner_result(result)
        )

    return {
        "engine": CRYPTO_SCANNER_ENGINE,
        "version": CRYPTO_SCANNER_VERSION,
        "status": active_state.status.value,
        "initialized": active_state.initialized,
        "ready": active_state.ready,
        "authenticated": active_state.authenticated,

        "operational": health.operational,

        "request_count": active_state.request_count,
        "scan_count": active_state.scan_count,

        "last_error": active_state.last_error,

        "result_present": result is not None,
        "result_errors": result_errors,

        "health_errors": list(health.errors),
        "health_warnings": list(health.warnings),

        "crypto_scanner_independent": True,
        "equity_scanner_dependency": False,
        "index_scanner_dependency": False,
        "commodity_scanner_dependency": False,
        "fx_scanner_dependency": False,

        "upstream_truth_policy": (
            "Scanner may filter and route upstream truth, "
            "but may not generate or alter crypto intelligence."
        ),

        "authority": dict(
            CRYPTO_SCANNER_AUTHORITY
        ),

        "checked_at": _crypto_now().isoformat(),
    }


# ============================================================
# SUMMARY
# ============================================================

def crypto_scanner_summary(
    result: CryptoScannerResult | None = None,
) -> Dict[str, Any]:

    if result is None:
        return {
            "engine": CRYPTO_SCANNER_ENGINE,
            "version": CRYPTO_SCANNER_VERSION,
            "status": CryptoScannerStatus.IDLE.value,
            "mode": CryptoScannerMode.UNIVERSAL_CRYPTO.value,
            "opportunity_count": 0,
            "qualified_count": 0,
            "developing_count": 0,
            "watch_count": 0,
            "invalidated_count": 0,
            "expired_count": 0,
            "bullish_count": 0,
            "bearish_count": 0,
            "neutral_count": 0,
            "favorite_count": 0,
            "watchlist_count": 0,
            "upstream_truth_preserved": True,
            "crypto_scanner_independent": True,
        }

    opportunities = result.opportunities

    return {
        "engine": CRYPTO_SCANNER_ENGINE,
        "version": CRYPTO_SCANNER_VERSION,

        "status": result.status.value,
        "mode": result.mode.value,

        "opportunity_count": len(opportunities),

        "qualified_count": sum(
            1
            for item in opportunities
            if item.state
            == CryptoOpportunityState.QUALIFIED
        ),

        "developing_count": sum(
            1
            for item in opportunities
            if item.state
            == CryptoOpportunityState.DEVELOPING
        ),

        "watch_count": sum(
            1
            for item in opportunities
            if item.state
            == CryptoOpportunityState.WATCH
        ),

        "invalidated_count": sum(
            1
            for item in opportunities
            if item.state
            == CryptoOpportunityState.INVALIDATED
        ),

        "expired_count": sum(
            1
            for item in opportunities
            if item.state
            == CryptoOpportunityState.EXPIRED
        ),

        "bullish_count": sum(
            1
            for item in opportunities
            if item.bias
            == CryptoOpportunityBias.BULLISH
        ),

        "bearish_count": sum(
            1
            for item in opportunities
            if item.bias
            == CryptoOpportunityBias.BEARISH
        ),

        "neutral_count": sum(
            1
            for item in opportunities
            if item.bias
            == CryptoOpportunityBias.NEUTRAL
        ),

        "favorite_count": sum(
            1
            for item in opportunities
            if item.favorite
        ),

        "watchlist_count": sum(
            1
            for item in opportunities
            if item.watchlisted
        ),

        "input_opportunity_count":
            result.total_input_opportunities,

        "output_opportunity_count":
            result.total_output_opportunities,

        "source_available":
            result.source_available,

        "upstream_truth_preserved": True,
        "crypto_scanner_independent": True,

        "crypto_algorithm_generated": False,
        "scanner_generated_intelligence": False,
        "scanner_generated_score": False,
        "scanner_generated_decision": False,

        "d13_modified": False,
        "risk_generated": False,
        "risk_overridden": False,
        "cas_bypassed": False,
        "execution_authority": False,
    }


# ============================================================
# CONTRACT MANIFEST
# ============================================================

def crypto_scanner_contract_manifest() -> Dict[str, Any]:

    return {
        "engine": CRYPTO_SCANNER_ENGINE,
        "version": CRYPTO_SCANNER_VERSION,
        "name": CRYPTO_SCANNER_NAME,
        "title": CRYPTO_SCANNER_TITLE,

        "layer": "UI_PRESENTATION",

        "role": "CRYPTO_OPPORTUNITY_SCANNER",

        "importance": "CLASS_A_DISCOVERY_COMPONENT",

        "critical_scanner": True,

        "description": CRYPTO_SCANNER_DESCRIPTION,

        # ----------------------------------------------------
        # Inputs
        # ----------------------------------------------------
        "inputs": [
            "USER_SERVICE_OUTPUT",
            "CRYPTO_MARKET_INPUT",
            "CRYPTO_INSTRUMENT_INPUT",
            "CRYPTO_SCANNER_FILTER",
            "UPSTREAM_CRYPTO_OPPORTUNITY_OUTPUT",
            "WATCHLIST_OUTPUT",
            "FAVORITES_OUTPUT",
            "APPLICATION_SESSION_STATE",
        ],

        # ----------------------------------------------------
        # Processing
        # ----------------------------------------------------
        "processing": [
            "SOURCE_NORMALIZATION",
            "CRYPTO_MARKET_FILTERING",
            "REGION_FILTERING",
            "EXCHANGE_FILTERING",
            "ASSET_FILTERING",
            "PAIR_FILTERING",
            "INSTRUMENT_FILTERING",
            "CATEGORY_FILTERING",
            "QUOTE_CURRENCY_FILTERING",
            "OPPORTUNITY_STATE_FILTERING",
            "OPPORTUNITY_BIAS_FILTERING",
            "OPPORTUNITY_STRENGTH_FILTERING",
            "FAVORITE_FILTERING",
            "WATCHLIST_FILTERING",
            "UPSTREAM_OPPORTUNITY_ROUTING",
            "RESULT_BUILDING",
            "SERIALIZATION",
            "VALIDATION",
            "HEALTH_CHECK",
            "DIAGNOSTICS",
        ],

        # ----------------------------------------------------
        # Outputs
        # ----------------------------------------------------
        "outputs": [
            "CRYPTO_SCANNER_RESULT",
            "CRYPTO_SCANNER_SNAPSHOT",
            "CRYPTO_SCANNER_STATE",
            "CRYPTO_SCANNER_HEALTH",
            "CRYPTO_SCANNER_DIAGNOSTICS",
        ],

        # ----------------------------------------------------
        # Truth policy
        # ----------------------------------------------------
        "truth_policy": {
            "upstream_truth_preserved": True,
            "scanner_generated_intelligence": False,
            "scanner_generated_score": False,
            "scanner_generated_decision": False,
            "crypto_algorithm_generated": False,
        },

        # ----------------------------------------------------
        # Intelligence ownership
        # ----------------------------------------------------
        "intelligence_authority": {
            "owner": "UPSTREAM_CRYPTO_INTELLIGENCE",

            "market_structure":
                "UPSTREAM_CRYPTO_INTELLIGENCE",

            "liquidity":
                "UPSTREAM_CRYPTO_INTELLIGENCE",

            "order_flow":
                "UPSTREAM_CRYPTO_INTELLIGENCE",

            "funding":
                "UPSTREAM_CRYPTO_INTELLIGENCE",

            "open_interest":
                "UPSTREAM_CRYPTO_INTELLIGENCE",

            "liquidation":
                "UPSTREAM_CRYPTO_INTELLIGENCE",

            "volatility_regime":
                "UPSTREAM_CRYPTO_INTELLIGENCE",

            "breakout":
                "UPSTREAM_CRYPTO_INTELLIGENCE",

            "confirmation":
                "UPSTREAM_CRYPTO_INTELLIGENCE",

            "exact_levels":
                "UPSTREAM_CRYPTO_INTELLIGENCE",
        },

        # ----------------------------------------------------
        # Future research pipeline
        # ----------------------------------------------------
        "future_research_pipeline": [
            "CRYPTO_MARKET_STRUCTURE",
            "CRYPTO_LIQUIDITY_ANALYSIS",
            "CRYPTO_ORDER_FLOW_ANALYSIS",
            "CRYPTO_FUNDING_ANALYSIS",
            "CRYPTO_OPEN_INTEREST_ANALYSIS",
            "CRYPTO_LIQUIDATION_ANALYSIS",
            "CRYPTO_VOLATILITY_REGIME_ANALYSIS",
            "CRYPTO_BREAKOUT_ANALYSIS",
            "CRYPTO_BREAKOUT_CONFIRMATION",
            "CRYPTO_EXACT_LEVEL_CALCULATION",
            "UPSTREAM_CRYPTO_INTELLIGENCE",
            "CRYPTO_SCANNER",
        ],

        "formula_authority":
            "UPSTREAM_CRYPTO_INTELLIGENCE",

        "formula_pluggable": True,

        # ----------------------------------------------------
        # Independence
        # ----------------------------------------------------
        "independence": {
            "crypto_scanner_independent": True,
            "equity_scanner_dependency": False,
            "index_scanner_dependency": False,
            "commodity_scanner_dependency": False,
            "fx_scanner_dependency": False,

            "equity_signal_required": False,
            "index_signal_required": False,
            "commodity_signal_required": False,
            "fx_signal_required": False,
        },

        # ----------------------------------------------------
        # Forbidden authority
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

def validate_crypto_scanner_integrity(
    request: CryptoScannerRequest | None = None,
    result: CryptoScannerResult | None = None,
    state: CryptoScannerState | None = None,
    snapshot: CryptoScannerSnapshot | None = None,
) -> List[str]:

    errors: List[str] = []

    if request is not None:
        errors.extend(
            validate_crypto_scanner_request(
                request
            )
        )

    if result is not None:
        errors.extend(
            validate_crypto_scanner_result(
                result
            )
        )

    if state is not None:
        errors.extend(
            validate_crypto_scanner_state(
                state
            )
        )

    if snapshot is not None:
        errors.extend(
            validate_crypto_scanner_snapshot(
                snapshot
            )
        )

    errors.extend(
        validate_crypto_scanner_authority()
    )

    # --------------------------------------------------------
    # Cross-object truth checks
    # --------------------------------------------------------
    if result is not None:

        metadata = result.metadata or {}

        if metadata.get(
            "crypto_scanner_independent"
        ) is not True:
            errors.append(
                "Crypto scanner independence contract failed."
            )

        if metadata.get(
            "upstream_truth_preserved"
        ) is not True:
            errors.append(
                "Upstream truth preservation failed."
            )

        for opportunity in result.opportunities:
            opportunity_errors = (
                validate_crypto_scanner_opportunity(
                    opportunity
                )
            )

            errors.extend(opportunity_errors)

    return errors


def validate_crypto_scanner_contract() -> List[str]:

    errors: List[str] = []

    manifest = crypto_scanner_contract_manifest()

    if manifest.get("layer") != "UI_PRESENTATION":
        errors.append(
            "Crypto scanner layer must be UI_PRESENTATION."
        )

    if manifest.get("role") != "CRYPTO_OPPORTUNITY_SCANNER":
        errors.append(
            "Invalid crypto scanner role."
        )

    if manifest.get("critical_scanner") is not True:
        errors.append(
            "Crypto scanner must remain Class-A critical."
        )

    truth_policy = manifest.get(
        "truth_policy",
        {},
    )

    if truth_policy.get(
        "upstream_truth_preserved"
    ) is not True:
        errors.append(
            "Upstream truth must be preserved."
        )

    forbidden = manifest.get(
        "forbidden",
        [],
    )

    required_forbidden = {
        "INTELLIGENCE_GENERATION",
        "DECISION_GENERATION",
        "D13_MODIFICATION",
        "RISK_OVERRIDE",
        "CAS_BYPASS",
        "EXECUTION",
        "UPSTREAM_MUTATION",
    }

    missing = required_forbidden.difference(
        forbidden
    )

    if missing:
        errors.append(
            "Missing forbidden authority entries: "
            + ", ".join(sorted(missing))
        )

    independence = manifest.get(
        "independence",
        {},
    )

    if independence.get(
        "crypto_scanner_independent"
    ) is not True:
        errors.append(
            "Crypto scanner must remain independent."
        )

    if independence.get(
        "equity_scanner_dependency"
    ) is not False:
        errors.append(
            "Crypto scanner cannot depend on equity scanner."
        )

    if independence.get(
        "index_scanner_dependency"
    ) is not False:
        errors.append(
            "Crypto scanner cannot depend on index scanner."
        )

    if independence.get(
        "commodity_scanner_dependency"
    ) is not False:
        errors.append(
            "Crypto scanner cannot depend on commodity scanner."
        )

    if independence.get(
        "fx_scanner_dependency"
    ) is not False:
        errors.append(
            "Crypto scanner cannot depend on FX scanner."
        )

    if manifest.get(
        "formula_pluggable"
    ) is not True:
        errors.append(
            "Crypto intelligence must remain formula-pluggable."
        )

    return errors


# ============================================================
# MODULE CHECK
# ============================================================

def crypto_scanner_module_check() -> Dict[str, Any]:

    contract_errors = (
        validate_crypto_scanner_contract()
    )

    authority_errors = (
        validate_crypto_scanner_authority()
    )

    default_state = (
        create_crypto_scanner_state()
    )

    state_errors = (
        validate_crypto_scanner_state(
            default_state
        )
    )

    return {
        "engine": CRYPTO_SCANNER_ENGINE,
        "version": CRYPTO_SCANNER_VERSION,

        "module_present": True,

        "contract_valid": not contract_errors,
        "authority_valid": not authority_errors,
        "default_state_valid": not state_errors,

        "contract_errors": contract_errors,
        "authority_errors": authority_errors,
        "state_errors": state_errors,

        "critical_scanner": True,
        "crypto_scanner_independent": True,

        "formula_pluggable": True,

        "upstream_truth_preserved": True,

        "scanner_generates_intelligence": False,
        "scanner_generates_score": False,
        "scanner_generates_decision": False,

        "d13_modified": False,
        "risk_overridden": False,
        "cas_bypassed": False,
        "execution_authority": False,

        "operational": (
            not contract_errors
            and not authority_errors
            and not state_errors
        ),
    }


# ============================================================
# SELF-CHECK
# ============================================================

def crypto_scanner_self_check() -> Dict[str, Any]:

    sample = UpstreamCryptoOpportunity(
        opportunity_id="CRYPTO_SELF_CHECK_001",
        symbol="BTCUSDT",

        instrument_id="BTCUSDT-SPOT",
        instrument_name="BTC/USDT",

        asset_type=CryptoAssetType.COIN,
        instrument_type=CryptoInstrumentType.SPOT,

        market_id="CRYPTO_GLOBAL",
        country="GLOBAL",
        region="GLOBAL",
        exchange="TEST_EXCHANGE",

        base_asset="BTC",
        quote_asset="USDT",

        category="LAYER1",
        sector="DIGITAL_ASSET",

        state=CryptoOpportunityState.QUALIFIED,
        bias=CryptoOpportunityBias.BULLISH,
        strength=CryptoOpportunityStrength.STRONG,

        summary="Upstream crypto opportunity self-check.",

        confidence=0.90,

        favorite=False,
        watchlisted=False,

        priority=CryptoScannerPriority.HIGH,

        source=(
            CryptoSourceType.UPSTREAM_OPPORTUNITY_ENGINE
        ),

        metadata={
            "research_formula_generated": True,
            "crypto_algorithm_generated": True,
            "upstream_test_truth": "PRESERVE",
        },
    )

    request = CryptoScannerRequest(
        mode=CryptoScannerMode.UNIVERSAL_CRYPTO,
        opportunities=[sample],
        authenticated=True,
    )

    result = run_crypto_scanner(request)

    errors = validate_crypto_scanner_result(
        result
    )

    routed = (
        result.opportunities[0]
        if result.opportunities
        else None
    )

    truth_preserved = False

    if routed is not None:
        truth_preserved = (
            routed.symbol == sample.symbol
            and routed.state == sample.state
            and routed.bias == sample.bias
            and routed.strength == sample.strength
            and routed.confidence == sample.confidence
            and routed.metadata.get(
                "upstream_truth"
            ) is True
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
                "crypto_algorithm_generated"
            ) is False
        )

    contract_errors = (
        validate_crypto_scanner_contract()
    )

    authority_errors = (
        validate_crypto_scanner_authority()
    )

    return {
        "engine": CRYPTO_SCANNER_ENGINE,
        "version": CRYPTO_SCANNER_VERSION,

        "passed": (
            not errors
            and not contract_errors
            and not authority_errors
            and truth_preserved
        ),

        "result_status": result.status.value,

        "result_errors": errors,
        "contract_errors": contract_errors,
        "authority_errors": authority_errors,

        "upstream_truth_preserved": truth_preserved,

        "research_formula_generated_upstream": True,
        "scanner_research_formula_generated": False,
        "scanner_intelligence_generated": False,
        "scanner_score_generated": False,
        "scanner_decision_generated": False,

        "crypto_scanner_independent": True,
        "equity_scanner_dependency": False,
        "index_scanner_dependency": False,
        "commodity_scanner_dependency": False,
        "fx_scanner_dependency": False,

        "d13_modified": False,
        "risk_overridden": False,
        "cas_bypassed": False,
        "execution_authority": False,

        "checked_at": _crypto_now().isoformat(),
    }


# ============================================================
# DEFAULT FACTORY
# ============================================================

def create_default_crypto_scanner(
    authenticated: bool = False,
) -> CryptoScannerController:

    return create_crypto_scanner(
        authenticated=authenticated,
        mode=CryptoScannerMode.UNIVERSAL_CRYPTO,
    )


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    # Core
    "CRYPTO_SCANNER_ENGINE",
    "CRYPTO_SCANNER_VERSION",
    "CRYPTO_SCANNER_NAME",
    "CRYPTO_SCANNER_TITLE",
    "CRYPTO_SCANNER_DESCRIPTION",
    "CRYPTO_SCANNER_AUTHORITY",

    # Enums
    "CryptoScannerStatus",
    "CryptoScannerMode",
    "CryptoAssetType",
    "CryptoInstrumentType",
    "CryptoOpportunityState",
    "CryptoOpportunityBias",
    "CryptoOpportunityStrength",
    "CryptoScannerPriority",
    "CryptoSourceType",

    # Contracts
    "CryptoMarketInput",
    "CryptoInstrumentInput",
    "UpstreamCryptoOpportunity",
    "CryptoScannerFilter",
    "CryptoScannerOpportunity",
    "CryptoScannerResult",
    "CryptoScannerRequest",
    "CryptoScannerSnapshot",
    "CryptoScannerState",
    "CryptoScannerHealth",

    # Helpers
    "normalize_crypto_market",
    "normalize_crypto_instrument",
    "normalize_upstream_crypto_opportunity",
    "normalize_crypto_filter",
    "normalize_crypto_request",

    # Filtering
    "crypto_opportunity_matches_filter",
    "filter_upstream_crypto_opportunities",
    "filter_crypto_markets",
    "filter_crypto_instruments",

    # Routing / result
    "convert_upstream_crypto_opportunity",
    "build_crypto_scanner_result",
    "crypto_scanner_source_status",
    "run_crypto_scanner",

    # Controller
    "CryptoScannerController",
    "get_crypto_scanner",
    "create_crypto_scanner",
    "scan_crypto_market",
    "scan_with_crypto_scanner",

    # Serialization
    "serialize_crypto_market",
    "serialize_crypto_instrument",
    "serialize_upstream_crypto_opportunity",
    "serialize_crypto_scanner_filter",
    "serialize_crypto_scanner_opportunity",
    "serialize_crypto_scanner_result",
    "serialize_crypto_scanner_request",
    "serialize_crypto_scanner_snapshot",
    "serialize_crypto_scanner_state",
    "serialize_crypto_scanner_health",

    # Validation
    "validate_crypto_market",
    "validate_crypto_instrument",
    "validate_upstream_crypto_opportunity",
    "validate_crypto_scanner_filter",
    "validate_crypto_scanner_opportunity",
    "validate_crypto_scanner_request",
    "validate_crypto_scanner_result",
    "validate_crypto_scanner_state",
    "validate_crypto_scanner_snapshot",
    "validate_crypto_scanner_authority",
    "validate_crypto_scanner_integrity",
    "validate_crypto_scanner_contract",

    # Health / diagnostics
    "build_crypto_scanner_health",
    "crypto_scanner_operational_check",
    "diagnose_crypto_scanner",
    "crypto_scanner_summary",
    "crypto_scanner_contract_manifest",
    "crypto_scanner_module_check",
    "crypto_scanner_self_check",

    # Factory
    "create_default_crypto_scanner",
]