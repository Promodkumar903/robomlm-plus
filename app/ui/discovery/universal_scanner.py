# ============================================================
# ROBOMLM_PLUS — UNIVERSAL DISCOVERY SCANNER
# PART 1 — CORE CONTRACT / AUTHORITY / SCHEMAS
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


# ============================================================
# MODULE IDENTITY
# ============================================================

UNIVERSAL_SCANNER_ENGINE = "ROBOMLM_PLUS_UNIVERSAL_SCANNER"
UNIVERSAL_SCANNER_VERSION = "1.0"
UNIVERSAL_SCANNER_NAME = "Universal Opportunity Scanner"
UNIVERSAL_SCANNER_TITLE = "Universal Market Opportunity Scanner"
UNIVERSAL_SCANNER_DESCRIPTION = (
    "Universal discovery scanner for presenting and routing "
    "upstream opportunity intelligence across supported asset classes."
)


# ============================================================
# AUTHORITY CONTRACT
# ============================================================

UNIVERSAL_SCANNER_AUTHORITY = {
    "scanner_orchestration": True,
    "opportunity_presentation": True,
    "market_filtering": True,
    "instrument_filtering": True,
    "asset_class_filtering": True,
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


# ============================================================
# ENUMS
# ============================================================

class ScannerStatus(str, Enum):
    IDLE = "IDLE"
    LOADING = "LOADING"
    READY = "READY"
    DEGRADED = "DEGRADED"
    BLOCKED = "BLOCKED"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class ScannerMode(str, Enum):
    UNIVERSAL = "UNIVERSAL"
    MARKET = "MARKET"
    ASSET_CLASS = "ASSET_CLASS"
    INSTRUMENT = "INSTRUMENT"
    FAVORITES = "FAVORITES"
    WATCHLIST = "WATCHLIST"
    UNKNOWN = "UNKNOWN"


class AssetClass(str, Enum):
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


class ScannerPriority(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ScannerSourceType(str, Enum):
    UPSTREAM_OPPORTUNITY_ENGINE = "UPSTREAM_OPPORTUNITY_ENGINE"
    DISCOVERY_ENGINE = "DISCOVERY_ENGINE"
    SCANNER_LAYER = "SCANNER_LAYER"
    UNKNOWN = "UNKNOWN"


# ============================================================
# HELPERS
# ============================================================

def _scanner_text(
    value: Any,
    default: str = "",
) -> str:
    if value is None:
        return default

    text = str(value).strip()

    return text if text else default


def _scanner_bool(
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


def _scanner_float(
    value: Any,
    default: float = 0.0,
) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _scanner_enum(
    value: Any,
    enum_type: type[Enum],
    default: Enum,
) -> Enum:
    if isinstance(value, enum_type):
        return value

    try:
        return enum_type(value)
    except (TypeError, ValueError):
        return default


def _scanner_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ============================================================
# CORE INPUT CONTRACTS
# ============================================================

@dataclass
class ScannerMarketInput:
    market_id: str
    market_name: str
    region: str = ""
    timezone: str = ""
    asset_classes: List[AssetClass] = field(
        default_factory=list
    )
    selected: bool = False
    enabled: bool = True
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class ScannerInstrumentInput:
    instrument_id: str
    symbol: str
    display_name: str = ""
    asset_class: AssetClass = AssetClass.UNKNOWN
    exchange: str = ""
    currency: str = ""
    market_id: str = ""
    selected: bool = False
    enabled: bool = True
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class UpstreamOpportunity:
    opportunity_id: str
    symbol: str
    instrument_id: str = ""
    instrument_name: str = ""
    market_id: str = ""
    asset_class: AssetClass = AssetClass.UNKNOWN

    state: OpportunityState = OpportunityState.UNKNOWN
    bias: OpportunityBias = OpportunityBias.UNKNOWN
    strength: OpportunityStrength = (
        OpportunityStrength.UNKNOWN
    )

    summary: str = ""
    confidence: float = 0.0
    timestamp: str = ""

    favorite: bool = False
    watchlisted: bool = False
    priority: ScannerPriority = ScannerPriority.NORMAL

    source: ScannerSourceType = (
        ScannerSourceType.UPSTREAM_OPPORTUNITY_ENGINE
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class ScannerFilter:
    asset_classes: List[AssetClass] = field(
        default_factory=list
    )
    market_ids: List[str] = field(
        default_factory=list
    )
    instrument_ids: List[str] = field(
        default_factory=list
    )
    symbols: List[str] = field(
        default_factory=list
    )

    states: List[OpportunityState] = field(
        default_factory=list
    )

    biases: List[OpportunityBias] = field(
        default_factory=list
    )

    strengths: List[OpportunityStrength] = field(
        default_factory=list
    )

    favorites_only: bool = False
    watchlist_only: bool = False
    include_invalidated: bool = False
    include_expired: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# SCANNER OUTPUT CONTRACT
# ============================================================

@dataclass
class ScannerOpportunity:
    opportunity_id: str
    symbol: str
    instrument_id: str
    instrument_name: str
    market_id: str
    asset_class: AssetClass

    state: OpportunityState
    bias: OpportunityBias
    strength: OpportunityStrength

    summary: str
    confidence: float
    timestamp: str

    favorite: bool
    watchlisted: bool
    priority: ScannerPriority

    source: ScannerSourceType

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class ScannerResult:
    status: ScannerStatus
    mode: ScannerMode

    opportunities: List[ScannerOpportunity] = (
        field(default_factory=list)
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


@dataclass
class UniversalScannerRequest:
    mode: ScannerMode = ScannerMode.UNIVERSAL

    markets: List[ScannerMarketInput] = field(
        default_factory=list
    )

    instruments: List[ScannerInstrumentInput] = field(
        default_factory=list
    )

    opportunities: List[UpstreamOpportunity] = field(
        default_factory=list
    )

    scanner_filter: ScannerFilter = field(
        default_factory=ScannerFilter
    )

    authenticated: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class UniversalScannerSnapshot:
    request: UniversalScannerRequest
    result: ScannerResult
    captured_at: str
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )
# ============================================================
# ROBOMLM_PLUS — UNIVERSAL DISCOVERY SCANNER
# PART 2 — NORMALIZATION / FILTERING / RESULT PREPARATION
# ============================================================


def normalize_scanner_market(
    value: ScannerMarketInput,
) -> ScannerMarketInput:
    return ScannerMarketInput(
        market_id=_scanner_text(value.market_id),
        market_name=_scanner_text(value.market_name),
        region=_scanner_text(value.region),
        timezone=_scanner_text(value.timezone),
        asset_classes=[
            _scanner_enum(
                item,
                AssetClass,
                AssetClass.UNKNOWN,
            )
            for item in (value.asset_classes or [])
        ],
        selected=_scanner_bool(value.selected),
        enabled=_scanner_bool(value.enabled, True),
        metadata=dict(value.metadata or {}),
    )


def normalize_scanner_instrument(
    value: ScannerInstrumentInput,
) -> ScannerInstrumentInput:
    return ScannerInstrumentInput(
        instrument_id=_scanner_text(value.instrument_id),
        symbol=_scanner_text(value.symbol),
        display_name=_scanner_text(value.display_name),
        asset_class=_scanner_enum(
            value.asset_class,
            AssetClass,
            AssetClass.UNKNOWN,
        ),
        exchange=_scanner_text(value.exchange),
        currency=_scanner_text(value.currency),
        market_id=_scanner_text(value.market_id),
        selected=_scanner_bool(value.selected),
        enabled=_scanner_bool(value.enabled, True),
        metadata=dict(value.metadata or {}),
    )


def normalize_upstream_opportunity(
    value: UpstreamOpportunity,
) -> UpstreamOpportunity:
    return UpstreamOpportunity(
        opportunity_id=_scanner_text(
            value.opportunity_id
        ),
        symbol=_scanner_text(value.symbol),
        instrument_id=_scanner_text(
            value.instrument_id
        ),
        instrument_name=_scanner_text(
            value.instrument_name
        ),
        market_id=_scanner_text(value.market_id),
        asset_class=_scanner_enum(
            value.asset_class,
            AssetClass,
            AssetClass.UNKNOWN,
        ),
        state=_scanner_enum(
            value.state,
            OpportunityState,
            OpportunityState.UNKNOWN,
        ),
        bias=_scanner_enum(
            value.bias,
            OpportunityBias,
            OpportunityBias.UNKNOWN,
        ),
        strength=_scanner_enum(
            value.strength,
            OpportunityStrength,
            OpportunityStrength.UNKNOWN,
        ),
        summary=_scanner_text(value.summary),
        confidence=_scanner_float(
            value.confidence
        ),
        timestamp=_scanner_text(value.timestamp),
        favorite=_scanner_bool(value.favorite),
        watchlisted=_scanner_bool(value.watchlisted),
        priority=_scanner_enum(
            value.priority,
            ScannerPriority,
            ScannerPriority.NORMAL,
        ),
        source=_scanner_enum(
            value.source,
            ScannerSourceType,
            ScannerSourceType.UNKNOWN,
        ),
        metadata=dict(value.metadata or {}),
    )


def normalize_scanner_filter(
    value: Optional[ScannerFilter] = None,
) -> ScannerFilter:
    if value is None:
        return ScannerFilter()

    return ScannerFilter(
        asset_classes=[
            _scanner_enum(
                item,
                AssetClass,
                AssetClass.UNKNOWN,
            )
            for item in (value.asset_classes or [])
        ],
        market_ids=[
            _scanner_text(item)
            for item in (value.market_ids or [])
            if _scanner_text(item)
        ],
        instrument_ids=[
            _scanner_text(item)
            for item in (value.instrument_ids or [])
            if _scanner_text(item)
        ],
        symbols=[
            _scanner_text(item)
            for item in (value.symbols or [])
            if _scanner_text(item)
        ],
        states=[
            _scanner_enum(
                item,
                OpportunityState,
                OpportunityState.UNKNOWN,
            )
            for item in (value.states or [])
        ],
        biases=[
            _scanner_enum(
                item,
                OpportunityBias,
                OpportunityBias.UNKNOWN,
            )
            for item in (value.biases or [])
        ],
        strengths=[
            _scanner_enum(
                item,
                OpportunityStrength,
                OpportunityStrength.UNKNOWN,
            )
            for item in (value.strengths or [])
        ],
        favorites_only=_scanner_bool(
            value.favorites_only
        ),
        watchlist_only=_scanner_bool(
            value.watchlist_only
        ),
        include_invalidated=_scanner_bool(
            value.include_invalidated
        ),
        include_expired=_scanner_bool(
            value.include_expired
        ),
        metadata=dict(value.metadata or {}),
    )


def normalize_scanner_request(
    request: UniversalScannerRequest,
) -> UniversalScannerRequest:
    return UniversalScannerRequest(
        mode=_scanner_enum(
            request.mode,
            ScannerMode,
            ScannerMode.UNIVERSAL,
        ),
        markets=[
            normalize_scanner_market(item)
            for item in (request.markets or [])
        ],
        instruments=[
            normalize_scanner_instrument(item)
            for item in (request.instruments or [])
        ],
        opportunities=[
            normalize_upstream_opportunity(item)
            for item in (request.opportunities or [])
        ],
        scanner_filter=normalize_scanner_filter(
            request.scanner_filter
        ),
        authenticated=_scanner_bool(
            request.authenticated
        ),
        metadata=dict(request.metadata or {}),
    )


def _matches_list(
    value: Any,
    allowed: List[Any],
) -> bool:
    if not allowed:
        return True

    return value in allowed


def opportunity_matches_filter(
    opportunity: UpstreamOpportunity,
    scanner_filter: ScannerFilter,
) -> bool:
    if not _matches_list(
        opportunity.asset_class,
        scanner_filter.asset_classes,
    ):
        return False

    if not _matches_list(
        opportunity.market_id,
        scanner_filter.market_ids,
    ):
        return False

    if not _matches_list(
        opportunity.instrument_id,
        scanner_filter.instrument_ids,
    ):
        return False

    if scanner_filter.symbols:
        if opportunity.symbol not in scanner_filter.symbols:
            return False

    if not _matches_list(
        opportunity.state,
        scanner_filter.states,
    ):
        return False

    if not _matches_list(
        opportunity.bias,
        scanner_filter.biases,
    ):
        return False

    if not _matches_list(
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
        == OpportunityState.INVALIDATED
    ):
        return False

    if (
        not scanner_filter.include_expired
        and opportunity.state
        == OpportunityState.EXPIRED
    ):
        return False

    return True


def filter_upstream_opportunities(
    opportunities: List[UpstreamOpportunity],
    scanner_filter: ScannerFilter,
) -> List[UpstreamOpportunity]:
    return [
        opportunity
        for opportunity in opportunities
        if opportunity_matches_filter(
            opportunity,
            scanner_filter,
        )
    ]


def filter_markets(
    markets: List[ScannerMarketInput],
    scanner_filter: ScannerFilter,
) -> List[ScannerMarketInput]:
    result = [
        item
        for item in markets
        if item.enabled
    ]

    if scanner_filter.market_ids:
        result = [
            item
            for item in result
            if item.market_id
            in scanner_filter.market_ids
        ]

    if scanner_filter.asset_classes:
        result = [
            item
            for item in result
            if any(
                asset in scanner_filter.asset_classes
                for asset in item.asset_classes
            )
        ]

    return result


def filter_instruments(
    instruments: List[ScannerInstrumentInput],
    scanner_filter: ScannerFilter,
) -> List[ScannerInstrumentInput]:
    result = [
        item
        for item in instruments
        if item.enabled
    ]

    if scanner_filter.instrument_ids:
        result = [
            item
            for item in result
            if item.instrument_id
            in scanner_filter.instrument_ids
        ]

    if scanner_filter.market_ids:
        result = [
            item
            for item in result
            if item.market_id
            in scanner_filter.market_ids
        ]

    if scanner_filter.asset_classes:
        result = [
            item
            for item in result
            if item.asset_class
            in scanner_filter.asset_classes
        ]

    return result


def convert_upstream_opportunity(
    value: UpstreamOpportunity,
) -> ScannerOpportunity:
    return ScannerOpportunity(
        opportunity_id=value.opportunity_id,
        symbol=value.symbol,
        instrument_id=value.instrument_id,
        instrument_name=value.instrument_name,
        market_id=value.market_id,
        asset_class=value.asset_class,
        state=value.state,
        bias=value.bias,
        strength=value.strength,
        summary=value.summary,
        confidence=value.confidence,
        timestamp=value.timestamp,
        favorite=value.favorite,
        watchlisted=value.watchlisted,
        priority=value.priority,
        source=value.source,
        metadata={
            **dict(value.metadata or {}),
            "upstream_truth": True,
            "scanner_generated_intelligence": False,
            "scanner_generated_score": False,
        },
    )


def build_scanner_result(
    request: UniversalScannerRequest,
    filtered_opportunities: List[UpstreamOpportunity],
    status: ScannerStatus = ScannerStatus.READY,
    source_available: bool = True,
    source_errors: Optional[List[str]] = None,
    warnings: Optional[List[str]] = None,
) -> ScannerResult:
    normalized = [
        convert_upstream_opportunity(item)
        for item in filtered_opportunities
    ]

    return ScannerResult(
        status=status,
        mode=request.mode,
        opportunities=normalized,
        total_input_opportunities=len(
            request.opportunities
        ),
        total_output_opportunities=len(
            normalized
        ),
        source_available=source_available,
        source_errors=list(source_errors or []),
        warnings=list(warnings or []),
        generated_at=_scanner_now(),
        metadata={
            "result_type": "UPSTREAM_OPPORTUNITY_ROUTING",
            "presentation_orchestration": True,
            "upstream_truth_preserved": True,
            "opportunity_generation": False,
            "scanner_score_generation": False,
            "confidence_generation": False,
            "bias_generation": False,
            "strength_generation": False,
            "intelligence_generation": False,
            "decision_generation": False,
            "d13_modification": False,
            "risk_override": False,
            "cas_bypass": False,
            "execution": False,
            "upstream_mutation": False,
        },
    )


def scanner_source_status(
    request: UniversalScannerRequest,
) -> ScannerStatus:
    if not request.authenticated:
        return ScannerStatus.BLOCKED

    if not request.opportunities:
        return ScannerStatus.DEGRADED

    return ScannerStatus.READY
# ============================================================
# ROBOMLM_PLUS — UNIVERSAL DISCOVERY SCANNER
# PART 3 — ORCHESTRATION / CONTROLLER / STATE
# ============================================================

@dataclass
class UniversalScannerState:
    initialized: bool = False
    ready: bool = False
    authenticated: bool = False
    status: ScannerStatus = ScannerStatus.IDLE
    mode: ScannerMode = ScannerMode.UNIVERSAL
    request_count: int = 0
    scan_count: int = 0
    last_error: str = ""
    last_scan_at: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


def create_universal_scanner_state(
    authenticated: bool = False,
    mode: ScannerMode = ScannerMode.UNIVERSAL,
) -> UniversalScannerState:
    return UniversalScannerState(
        initialized=False,
        ready=False,
        authenticated=_scanner_bool(authenticated),
        status=ScannerStatus.IDLE,
        mode=_scanner_enum(mode, ScannerMode, ScannerMode.UNIVERSAL),
    )


def normalize_scanner_state(
    value: Any = None,
) -> UniversalScannerState:
    if isinstance(value, UniversalScannerState):
        return value

    if not isinstance(value, dict):
        return create_universal_scanner_state()

    return UniversalScannerState(
        initialized=_scanner_bool(value.get("initialized")),
        ready=_scanner_bool(value.get("ready")),
        authenticated=_scanner_bool(value.get("authenticated")),
        status=_scanner_enum(
            value.get("status"),
            ScannerStatus,
            ScannerStatus.IDLE,
        ),
        mode=_scanner_enum(
            value.get("mode"),
            ScannerMode,
            ScannerMode.UNIVERSAL,
        ),
        request_count=max(0, int(_scanner_float(value.get("request_count"), 0))),
        scan_count=max(0, int(_scanner_float(value.get("scan_count"), 0))),
        last_error=_scanner_text(value.get("last_error")),
        last_scan_at=_scanner_text(value.get("last_scan_at")),
        metadata=dict(value.get("metadata") or {}),
    )


def run_universal_scanner(
    request: Any = None,
) -> ScannerResult:
    """
    Execute universal discovery filtering/orchestration.

    IMPORTANT:
    This function consumes upstream opportunity intelligence.
    It does not generate intelligence, scores, decisions, D13,
    risk, CAS, or execution instructions.
    """
    normalized = normalize_scanner_request(request)

    if not normalized.authenticated:
        return build_scanner_result(
            normalized,
            [],
            status=ScannerStatus.BLOCKED,
            source_available=False,
            source_errors=["Scanner access requires authentication."],
            warnings=[],
        )

    markets = filter_markets(
        normalized.markets,
        normalized.scanner_filter,
    )

    instruments = filter_instruments(
        normalized.instruments,
        normalized.scanner_filter,
    )

    opportunities = filter_upstream_opportunities(
        normalized.opportunities,
        normalized.scanner_filter,
    )

    source_status = scanner_source_status(normalized)

    warnings: List[str] = []

    if normalized.opportunities and not opportunities:
        warnings.append(
            "No upstream opportunities matched the active scanner filters."
        )

    if normalized.markets and not markets:
        warnings.append(
            "No enabled markets matched the active scanner filters."
        )

    if normalized.instruments and not instruments:
        warnings.append(
            "No enabled instruments matched the active scanner filters."
        )

    if source_status == ScannerStatus.DEGRADED:
        return build_scanner_result(
            normalized,
            opportunities,
            status=ScannerStatus.DEGRADED,
            source_available=False,
            source_errors=["Upstream opportunity source is unavailable."],
            warnings=warnings,
        )

    return build_scanner_result(
        normalized,
        opportunities,
        status=ScannerStatus.READY,
        source_available=True,
        source_errors=[],
        warnings=warnings,
    )


class UniversalScannerController:
    """
    Presentation/application controller for Universal Scanner.

    Authority boundary:
    - consumes upstream opportunity intelligence
    - applies presentation/discovery filters
    - exposes scanner state/results

    It does NOT:
    - generate market intelligence
    - generate evidence
    - generate decisions
    - modify D13
    - generate or override risk
    - bypass CAS
    - execute orders
    - mutate positions
    """

    def __init__(
        self,
        state: Optional[UniversalScannerState] = None,
    ):
        self._state = normalize_scanner_state(state)
        self._last_request: Optional[UniversalScannerRequest] = None
        self._last_result: Optional[ScannerResult] = None
        self._request_history: List[UniversalScannerRequest] = []
        self._result_history: List[ScannerResult] = []

    @property
    def state(self) -> UniversalScannerState:
        return self._state

    @property
    def status(self) -> ScannerStatus:
        return self._state.status

    @property
    def mode(self) -> ScannerMode:
        return self._state.mode

    @property
    def authenticated(self) -> bool:
        return self._state.authenticated

    @property
    def last_request(self) -> Optional[UniversalScannerRequest]:
        return self._last_request

    @property
    def last_result(self) -> Optional[ScannerResult]:
        return self._last_result

    def initialize(
        self,
        request: Any = None,
    ) -> ScannerResult:
        normalized = normalize_scanner_request(request)

        self._state.initialized = True
        self._state.authenticated = normalized.authenticated
        self._state.mode = normalized.mode
        self._state.status = ScannerStatus.LOADING
        self._state.ready = False
        self._state.request_count += 1

        self._last_request = normalized
        self._request_history.append(normalized)
        self._request_history = self._request_history[-500:]

        result = run_universal_scanner(normalized)

        self._last_result = result
        self._result_history.append(result)
        self._result_history = self._result_history[-500:]

        self._state.status = result.status
        self._state.ready = result.status in {
            ScannerStatus.READY,
            ScannerStatus.DEGRADED,
        }
        self._state.last_scan_at = result.generated_at

        if result.source_errors:
            self._state.last_error = result.source_errors[-1]
        else:
            self._state.last_error = ""

        self._state.scan_count += 1
        return result

    def scan(
        self,
        request: Any = None,
    ) -> ScannerResult:
        if request is None:
            request = self._last_request

        if request is None:
            request = UniversalScannerRequest(
                authenticated=self._state.authenticated,
                mode=self._state.mode,
            )

        return self.initialize(request)

    def set_mode(
        self,
        mode: ScannerMode,
    ) -> UniversalScannerState:
        self._state.mode = _scanner_enum(
            mode,
            ScannerMode,
            ScannerMode.UNIVERSAL,
        )
        return self._state

    def set_authenticated(
        self,
        authenticated: bool,
    ) -> UniversalScannerState:
        self._state.authenticated = _scanner_bool(authenticated)

        if not self._state.authenticated:
            self._state.ready = False
            self._state.status = ScannerStatus.BLOCKED

        return self._state

    def block(self) -> UniversalScannerState:
        self._state.status = ScannerStatus.BLOCKED
        self._state.ready = False
        return self._state

    def reset(self) -> UniversalScannerState:
        self._state = create_universal_scanner_state(
            authenticated=self._state.authenticated,
            mode=self._state.mode,
        )
        self._last_request = None
        self._last_result = None
        self._request_history.clear()
        self._result_history.clear()
        return self._state

    def snapshot(self) -> "UniversalScannerSnapshot":
        request = self._last_request or UniversalScannerRequest(
            authenticated=self._state.authenticated,
            mode=self._state.mode,
        )

        result = self._last_result or ScannerResult(
            status=self._state.status,
            mode=self._state.mode,
            generated_at=_scanner_now(),
        )

        return UniversalScannerSnapshot(
            request=request,
            result=result,
            captured_at=_scanner_now(),
            metadata={
                "ui_only": True,
                "upstream_truth_consumed": True,
                "scanner_generated_intelligence": False,
                "scanner_generated_score": False,
                "decision_authority": False,
                "d13_authority": False,
                "risk_authority": False,
                "cas_authority": False,
                "execution_authority": False,
            },
        )

    def request_history(self) -> List[UniversalScannerRequest]:
        return list(self._request_history)

    def result_history(self) -> List[ScannerResult]:
        return list(self._result_history)


_DEFAULT_UNIVERSAL_SCANNER = UniversalScannerController()


def get_universal_scanner() -> UniversalScannerController:
    return _DEFAULT_UNIVERSAL_SCANNER


def create_universal_scanner(
    authenticated: bool = False,
    mode: ScannerMode = ScannerMode.UNIVERSAL,
) -> UniversalScannerController:
    return UniversalScannerController(
        create_universal_scanner_state(
            authenticated=authenticated,
            mode=mode,
        )
    )


def scan_universal_market(
    request: Any = None,
) -> ScannerResult:
    return run_universal_scanner(request)


def scan_with_universal_scanner(
    request: Any = None,
) -> ScannerResult:
    return get_universal_scanner().scan(request)
# ============================================================
# ROBOMLM_PLUS — UNIVERSAL DISCOVERY SCANNER
# PART 4 — SERIALIZATION / VALIDATION / HEALTH
# ============================================================

def _serialize_scanner_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, list):
        return [_serialize_scanner_value(v) for v in value]
    if isinstance(value, tuple):
        return [_serialize_scanner_value(v) for v in value]
    if isinstance(value, dict):
        return {
            str(k): _serialize_scanner_value(v)
            for k, v in value.items()
        }
    if hasattr(value, "__dataclass_fields__"):
        return {
            key: _serialize_scanner_value(getattr(value, key))
            for key in value.__dataclass_fields__
        }
    return value


def serialize_scanner_market(value: ScannerMarketInput) -> Dict[str, Any]:
    return _serialize_scanner_value(value)


def serialize_scanner_instrument(
    value: ScannerInstrumentInput,
) -> Dict[str, Any]:
    return _serialize_scanner_value(value)


def serialize_upstream_opportunity(
    value: UpstreamOpportunity,
) -> Dict[str, Any]:
    return _serialize_scanner_value(value)


def serialize_scanner_filter(
    value: ScannerFilter,
) -> Dict[str, Any]:
    return _serialize_scanner_value(value)


def serialize_scanner_opportunity(
    value: ScannerOpportunity,
) -> Dict[str, Any]:
    return _serialize_scanner_value(value)


def serialize_scanner_result(
    value: ScannerResult,
) -> Dict[str, Any]:
    return _serialize_scanner_value(value)


def serialize_scanner_request(
    value: UniversalScannerRequest,
) -> Dict[str, Any]:
    return _serialize_scanner_value(value)


def serialize_scanner_state(
    value: UniversalScannerState,
) -> Dict[str, Any]:
    return _serialize_scanner_value(value)


def serialize_scanner_snapshot(
    value: UniversalScannerSnapshot,
) -> Dict[str, Any]:
    return _serialize_scanner_value(value)


def validate_scanner_market(
    value: ScannerMarketInput,
) -> List[str]:
    errors: List[str] = []

    if not _scanner_text(value.market_id):
        errors.append("market_id is required.")

    if not _scanner_text(value.market_name):
        errors.append("market_name is required.")

    return errors


def validate_scanner_instrument(
    value: ScannerInstrumentInput,
) -> List[str]:
    errors: List[str] = []

    if not _scanner_text(value.instrument_id):
        errors.append("instrument_id is required.")

    if not _scanner_text(value.symbol):
        errors.append("symbol is required.")

    return errors


def validate_upstream_opportunity(
    value: UpstreamOpportunity,
) -> List[str]:
    errors: List[str] = []

    if not _scanner_text(value.opportunity_id):
        errors.append("opportunity_id is required.")

    if not _scanner_text(value.symbol):
        errors.append("symbol is required.")

    if not 0.0 <= float(value.confidence) <= 1.0:
        errors.append("confidence must be between 0 and 1.")

    if value.source == ScannerSourceType.UNKNOWN:
        errors.append("source must identify an upstream source.")

    return errors


def validate_scanner_filter(
    value: ScannerFilter,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(value.asset_classes, list):
        errors.append("asset_classes must be a list.")

    if not isinstance(value.market_ids, list):
        errors.append("market_ids must be a list.")

    if not isinstance(value.instrument_ids, list):
        errors.append("instrument_ids must be a list.")

    if not isinstance(value.symbols, list):
        errors.append("symbols must be a list.")

    return errors


def validate_scanner_opportunity(
    value: ScannerOpportunity,
) -> List[str]:
    errors: List[str] = []

    if not _scanner_text(value.opportunity_id):
        errors.append("opportunity_id is required.")

    if not _scanner_text(value.symbol):
        errors.append("symbol is required.")

    if not 0.0 <= float(value.confidence) <= 1.0:
        errors.append("confidence must be between 0 and 1.")

    if value.source == ScannerSourceType.UNKNOWN:
        errors.append("source must identify an upstream source.")

    if value.metadata.get("scanner_generated_intelligence", False):
        errors.append(
            "Scanner cannot mark intelligence as scanner-generated."
        )

    if value.metadata.get("scanner_generated_score", False):
        errors.append(
            "Scanner cannot mark score as scanner-generated."
        )

    return errors


def validate_scanner_request(
    value: UniversalScannerRequest,
) -> List[str]:
    errors: List[str] = []

    errors.extend(validate_scanner_filter(value.scanner_filter))

    for market in value.markets:
        errors.extend(validate_scanner_market(market))

    for instrument in value.instruments:
        errors.extend(validate_scanner_instrument(instrument))

    for opportunity in value.opportunities:
        errors.extend(validate_upstream_opportunity(opportunity))

    return errors


def validate_scanner_result(
    value: ScannerResult,
) -> List[str]:
    errors: List[str] = []

    if value.total_input_opportunities < 0:
        errors.append("total_input_opportunities cannot be negative.")

    if value.total_output_opportunities < 0:
        errors.append("total_output_opportunities cannot be negative.")

    if value.total_output_opportunities != len(value.opportunities):
        errors.append(
            "total_output_opportunities must match opportunities length."
        )

    if value.total_output_opportunities > value.total_input_opportunities:
        errors.append(
            "Output opportunities cannot exceed input opportunities."
        )

    for opportunity in value.opportunities:
        errors.extend(validate_scanner_opportunity(opportunity))

    return errors


def validate_scanner_state(
    value: UniversalScannerState,
) -> List[str]:
    errors: List[str] = []

    if value.request_count < 0:
        errors.append("request_count cannot be negative.")

    if value.scan_count < 0:
        errors.append("scan_count cannot be negative.")

    if value.status == ScannerStatus.READY and not value.ready:
        errors.append("READY scanner must have ready=True.")

    if value.status == ScannerStatus.BLOCKED and value.ready:
        errors.append("BLOCKED scanner cannot have ready=True.")

    return errors


def validate_scanner_snapshot(
    value: UniversalScannerSnapshot,
) -> List[str]:
    errors: List[str] = []

    errors.extend(validate_scanner_request(value.request))
    errors.extend(validate_scanner_result(value.result))

    if not _scanner_text(value.captured_at):
        errors.append("captured_at is required.")

    return errors


def validate_universal_scanner_authority(
    value: Optional[Dict[str, Any]] = None,
) -> List[str]:
    authority = value or UNIVERSAL_SCANNER_AUTHORITY
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
                f"Forbidden authority must remain False: {key}"
            )

    return errors


@dataclass
class UniversalScannerHealth:
    status: ScannerStatus
    initialized: bool
    ready: bool
    authenticated: bool
    request_count: int
    scan_count: int
    last_error: str = ""
    checks: Dict[str, bool] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    generated_at: str = ""


def build_universal_scanner_health(
    scanner: Optional[UniversalScannerController] = None,
) -> UniversalScannerHealth:
    controller = scanner or get_universal_scanner()
    state = controller.state

    checks = {
        "initialized_state_valid": not validate_scanner_state(state),
        "authority_valid": not validate_universal_scanner_authority(),
        "status_known": state.status != ScannerStatus.UNKNOWN,
        "mode_known": state.mode != ScannerMode.UNKNOWN,
    }

    errors: List[str] = []
    for name, passed in checks.items():
        if not passed:
            errors.append(f"Health check failed: {name}")

    warnings: List[str] = []

    if not state.authenticated:
        warnings.append("Scanner is not authenticated.")

    if state.status == ScannerStatus.DEGRADED:
        warnings.append("Upstream opportunity source is degraded.")

    return UniversalScannerHealth(
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
        generated_at=_scanner_now(),
    )


def serialize_universal_scanner_health(
    value: UniversalScannerHealth,
) -> Dict[str, Any]:
    return _serialize_scanner_value(value)


def universal_scanner_operational_check(
    scanner: Optional[UniversalScannerController] = None,
) -> Dict[str, Any]:
    health = build_universal_scanner_health(scanner)

    operational = (
        not health.errors
        and all(health.checks.values())
    )

    return {
        "engine": UNIVERSAL_SCANNER_ENGINE,
        "version": UNIVERSAL_SCANNER_VERSION,
        "name": UNIVERSAL_SCANNER_NAME,
        "operational": operational,
        "status": health.status.value,
        "initialized": health.initialized,
        "ready": health.ready,
        "authenticated": health.authenticated,
        "checks": health.checks,
        "errors": health.errors,
        "warnings": health.warnings,
        "authority": dict(UNIVERSAL_SCANNER_AUTHORITY),
        "generated_at": health.generated_at,
    }
# ============================================================
# ROBOMLM_PLUS — UNIVERSAL DISCOVERY SCANNER
# PART 5 — DIAGNOSTICS / CONTRACT / SELF-CHECK / EXPORTS
# ============================================================

def diagnose_universal_scanner(
    scanner: Optional[UniversalScannerController] = None,
) -> Dict[str, Any]:
    controller = scanner or get_universal_scanner()
    state = controller.state
    result = controller.last_result

    health = build_universal_scanner_health(controller)

    diagnostics = {
        "engine": UNIVERSAL_SCANNER_ENGINE,
        "version": UNIVERSAL_SCANNER_VERSION,
        "name": UNIVERSAL_SCANNER_NAME,
        "status": state.status.value,
        "mode": state.mode.value,
        "initialized": state.initialized,
        "ready": state.ready,
        "authenticated": state.authenticated,
        "request_count": state.request_count,
        "scan_count": state.scan_count,
        "last_error": state.last_error,
        "last_scan_at": state.last_scan_at,
        "health": serialize_universal_scanner_health(health),
        "last_result": (
            serialize_scanner_result(result)
            if result is not None
            else None
        ),
        "authority": dict(UNIVERSAL_SCANNER_AUTHORITY),
    }

    return diagnostics


def universal_scanner_summary(
    scanner: Optional[UniversalScannerController] = None,
) -> Dict[str, Any]:
    controller = scanner or get_universal_scanner()
    state = controller.state
    result = controller.last_result

    return {
        "engine": UNIVERSAL_SCANNER_ENGINE,
        "version": UNIVERSAL_SCANNER_VERSION,
        "name": UNIVERSAL_SCANNER_NAME,
        "status": state.status.value,
        "mode": state.mode.value,
        "initialized": state.initialized,
        "ready": state.ready,
        "authenticated": state.authenticated,
        "scan_count": state.scan_count,
        "opportunity_count": (
            result.total_output_opportunities
            if result is not None
            else 0
        ),
        "source_available": (
            result.source_available
            if result is not None
            else False
        ),
        "intelligence_generation": False,
        "score_generation": False,
        "decision_generation": False,
        "d13_modification": False,
        "risk_override": False,
        "cas_bypass": False,
        "execution": False,
    }


def universal_scanner_contract_manifest() -> Dict[str, Any]:
    return {
        "engine": UNIVERSAL_SCANNER_ENGINE,
        "version": UNIVERSAL_SCANNER_VERSION,
        "name": UNIVERSAL_SCANNER_NAME,
        "layer": "UI_PRESENTATION",
        "role": "UNIVERSAL_OPPORTUNITY_SCANNER",
        "purpose": (
            "Present and route upstream opportunity intelligence "
            "across supported markets, asset classes and instruments."
        ),
        "inputs": [
            "UPSTREAM_OPPORTUNITY_ENGINE_OUTPUT",
            "DISCOVERY_MARKET_OUTPUT",
            "DISCOVERY_INSTRUMENT_OUTPUT",
            "WATCHLIST_OUTPUT",
            "FAVORITES_OUTPUT",
            "APPLICATION_SESSION_STATE",
            "SCANNER_FILTER_STATE",
        ],
        "processing": [
            "REQUEST_NORMALIZATION",
            "MARKET_FILTERING",
            "INSTRUMENT_FILTERING",
            "OPPORTUNITY_FILTERING",
            "ASSET_CLASS_FILTERING",
            "STATE_FILTERING",
            "BIAS_FILTERING",
            "STRENGTH_FILTERING",
            "FAVORITE_FILTERING",
            "WATCHLIST_FILTERING",
            "UPSTREAM_OPPORTUNITY_CONVERSION",
            "RESULT_ORCHESTRATION",
            "PRESENTATION_VALIDATION",
            "DIAGNOSTICS",
        ],
        "outputs": [
            "SCANNER_RESULT",
            "SCANNER_SNAPSHOT",
            "SCANNER_STATE",
            "SCANNER_HEALTH",
            "SCANNER_DIAGNOSTICS",
        ],
        "authority_owners": {
            "market_data": "UPSTREAM_MARKET_DATA_LAYER",
            "evidence": "EVIDENCE_CORTEX",
            "intelligence": "INTELLIGENCE_LAYER",
            "opportunity": "OPPORTUNITY_ENGINE",
            "decision": "DECISION_CORTEX",
            "d13": "D13_DECISION_AUTHORITY",
            "risk": "RISK_ENGINE",
            "cas": "CAS",
            "execution": "EXECUTION_LAYER",
            "orders": "ORDER_AUTHORITY",
            "positions": "POSITION_AUTHORITY",
        },
        "scanner_authority": {
            "consume_upstream_truth": True,
            "filter_upstream_truth": True,
            "present_upstream_truth": True,
            "generate_intelligence": False,
            "generate_score": False,
            "generate_decision": False,
            "modify_d13": False,
            "generate_risk": False,
            "override_risk": False,
            "bypass_cas": False,
            "execute_orders": False,
            "mutate_orders": False,
            "mutate_positions": False,
            "mutate_portfolio": False,
            "mutate_upstream": False,
        },
        "forbidden_operations": [
            "MARKET_DATA_GENERATION",
            "EVIDENCE_GENERATION",
            "INTELLIGENCE_GENERATION",
            "SCANNER_INTELLIGENCE_GENERATION",
            "SCANNER_SCORE_GENERATION",
            "DECISION_GENERATION",
            "D13_MODIFICATION",
            "RISK_GENERATION",
            "RISK_OVERRIDE",
            "CAS_GENERATION",
            "CAS_BYPASS",
            "ORDER_EXECUTION",
            "ORDER_MUTATION",
            "POSITION_MUTATION",
            "PORTFOLIO_MUTATION",
            "UPSTREAM_MUTATION",
        ],
    }


def validate_universal_scanner_integrity(
    scanner: Optional[UniversalScannerController] = None,
) -> Dict[str, Any]:
    controller = scanner or get_universal_scanner()

    state_errors = validate_scanner_state(controller.state)
    authority_errors = validate_universal_scanner_authority()

    request_errors: List[str] = []
    result_errors: List[str] = []

    if controller.last_request is not None:
        request_errors = validate_scanner_request(
            controller.last_request
        )

    if controller.last_result is not None:
        result_errors = validate_scanner_result(
            controller.last_result
        )

    errors = (
        state_errors
        + authority_errors
        + request_errors
        + result_errors
    )

    return {
        "valid": not errors,
        "errors": errors,
        "checks": {
            "state": not state_errors,
            "authority": not authority_errors,
            "request": not request_errors,
            "result": not result_errors,
        },
    }


def validate_universal_scanner_contract() -> Dict[str, Any]:
    manifest = universal_scanner_contract_manifest()

    required_fields = {
        "engine",
        "version",
        "name",
        "layer",
        "role",
        "purpose",
        "inputs",
        "processing",
        "outputs",
        "authority_owners",
        "scanner_authority",
        "forbidden_operations",
    }

    missing = [
        field_name
        for field_name in required_fields
        if field_name not in manifest
    ]

    forbidden = manifest["scanner_authority"]

    required_false = {
        "generate_intelligence",
        "generate_score",
        "generate_decision",
        "modify_d13",
        "generate_risk",
        "override_risk",
        "bypass_cas",
        "execute_orders",
        "mutate_orders",
        "mutate_positions",
        "mutate_portfolio",
        "mutate_upstream",
    }

    authority_errors = [
        key
        for key in required_false
        if forbidden.get(key) is not False
    ]

    errors = []

    if missing:
        errors.append(
            f"Missing contract fields: {', '.join(missing)}"
        )

    if authority_errors:
        errors.append(
            "Forbidden authority violation: "
            + ", ".join(authority_errors)
        )

    return {
        "valid": not errors,
        "errors": errors,
        "manifest_fields": sorted(manifest.keys()),
        "authority_valid": not authority_errors,
    }


def universal_scanner_module_check(
    scanner: Optional[UniversalScannerController] = None,
) -> Dict[str, Any]:
    controller = scanner or get_universal_scanner()

    integrity = validate_universal_scanner_integrity(controller)
    contract = validate_universal_scanner_contract()
    operational = universal_scanner_operational_check(controller)

    valid = (
        integrity["valid"]
        and contract["valid"]
    )

    return {
        "module": UNIVERSAL_SCANNER_NAME,
        "engine": UNIVERSAL_SCANNER_ENGINE,
        "version": UNIVERSAL_SCANNER_VERSION,
        "valid": valid,
        "integrity": integrity,
        "contract": contract,
        "operational": operational,
        "authority_boundary_intact": (
            integrity["checks"]["authority"]
            and contract["authority_valid"]
        ),
    }


def universal_scanner_self_check() -> Dict[str, Any]:
    scanner = create_universal_scanner(authenticated=True)

    sample_request = UniversalScannerRequest(
        mode=ScannerMode.UNIVERSAL,
        authenticated=True,
        opportunities=[
            UpstreamOpportunity(
                opportunity_id="SELF_CHECK_OPPORTUNITY",
                symbol="SELF_CHECK",
                instrument_id="SELF_CHECK_INSTRUMENT",
                instrument_name="Self Check Instrument",
                market_id="SELF_CHECK_MARKET",
                asset_class=AssetClass.INDEX,
                state=OpportunityState.WATCH,
                bias=OpportunityBias.NEUTRAL,
                strength=OpportunityStrength.MODERATE,
                summary="Upstream self-check opportunity.",
                confidence=0.50,
                timestamp=_scanner_now(),
                source=ScannerSourceType.UPSTREAM_OPPORTUNITY_ENGINE,
                metadata={
                    "upstream_truth": True,
                    "scanner_generated_intelligence": False,
                    "scanner_generated_score": False,
                },
            )
        ],
    )

    result = scanner.scan(sample_request)
    module_check = universal_scanner_module_check(scanner)

    result_valid = not validate_scanner_result(result)

    return {
        "passed": (
            module_check["valid"]
            and result_valid
            and result.total_output_opportunities == 1
            and result.opportunities[0].metadata.get(
                "upstream_truth"
            ) is True
        ),
        "module_check": module_check,
        "result_valid": result_valid,
        "result": serialize_scanner_result(result),
    }


def create_default_universal_scanner() -> UniversalScannerController:
    return create_universal_scanner(
        authenticated=False,
        mode=ScannerMode.UNIVERSAL,
    )


__all__ = [
    # Constants
    "UNIVERSAL_SCANNER_ENGINE",
    "UNIVERSAL_SCANNER_VERSION",
    "UNIVERSAL_SCANNER_NAME",
    "UNIVERSAL_SCANNER_TITLE",
    "UNIVERSAL_SCANNER_DESCRIPTION",
    "UNIVERSAL_SCANNER_AUTHORITY",

    # Enums
    "ScannerStatus",
    "ScannerMode",
    "AssetClass",
    "OpportunityState",
    "OpportunityBias",
    "OpportunityStrength",
    "ScannerPriority",
    "ScannerSourceType",

    # Contracts
    "ScannerMarketInput",
    "ScannerInstrumentInput",
    "UpstreamOpportunity",
    "ScannerFilter",
    "ScannerOpportunity",
    "ScannerResult",
    "UniversalScannerRequest",
    "UniversalScannerSnapshot",
    "UniversalScannerState",
    "UniversalScannerHealth",

    # Normalization / filtering
    "normalize_scanner_market",
    "normalize_scanner_instrument",
    "normalize_upstream_opportunity",
    "normalize_scanner_filter",
    "normalize_scanner_request",
    "opportunity_matches_filter",
    "filter_upstream_opportunities",
    "filter_markets",
    "filter_instruments",
    "convert_upstream_opportunity",
    "build_scanner_result",
    "scanner_source_status",

    # Orchestration
    "run_universal_scanner",
    "UniversalScannerController",
    "get_universal_scanner",
    "create_universal_scanner",
    "scan_universal_market",
    "scan_with_universal_scanner",

    # State
    "create_universal_scanner_state",
    "normalize_scanner_state",

    # Serialization
    "serialize_scanner_market",
    "serialize_scanner_instrument",
    "serialize_upstream_opportunity",
    "serialize_scanner_filter",
    "serialize_scanner_opportunity",
    "serialize_scanner_result",
    "serialize_scanner_request",
    "serialize_scanner_state",
    "serialize_scanner_snapshot",

    # Validation
    "validate_scanner_market",
    "validate_scanner_instrument",
    "validate_upstream_opportunity",
    "validate_scanner_filter",
    "validate_scanner_opportunity",
    "validate_scanner_request",
    "validate_scanner_result",
    "validate_scanner_state",
    "validate_scanner_snapshot",
    "validate_universal_scanner_authority",

    # Health / diagnostics
    "build_universal_scanner_health",
    "serialize_universal_scanner_health",
    "universal_scanner_operational_check",
    "diagnose_universal_scanner",
    "universal_scanner_summary",

    # Contract / integrity
    "universal_scanner_contract_manifest",
    "validate_universal_scanner_integrity",
    "validate_universal_scanner_contract",
    "universal_scanner_module_check",

    # Factory / self-check
    "universal_scanner_self_check",
    "create_default_universal_scanner",
]