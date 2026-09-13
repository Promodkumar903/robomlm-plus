# ============================================================
# ROBOMLM_PLUS
# Accumulation Intelligence Engine
# Part 1 / 5
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


# ============================================================
# ENGINE IDENTITY
# ============================================================

ACCUMULATION_ENGINE = "ROBOMLM_PLUS_ACCUMULATION_ENGINE"
ACCUMULATION_ENGINE_VERSION = "1.0"
ACCUMULATION_ENGINE_NAME = "Accumulation Intelligence Engine"

ACCUMULATION_ENGINE_DESCRIPTION = (
    "Research-driven accumulation intelligence engine for identifying "
    "validated accumulation characteristics from normalized market "
    "observations and upstream structure intelligence."
)


# ============================================================
# AUTHORITY
# ============================================================

ACCUMULATION_ENGINE_AUTHORITY: Dict[str, bool] = {
    # Owned capabilities
    "accumulation_analysis": True,
    "accumulation_normalization": True,
    "volume_behavior_analysis": True,
    "price_behavior_analysis": True,
    "range_behavior_analysis": True,
    "structure_context_consumption": True,
    "multi_timeframe_accumulation": True,
    "research_formula_consumption": True,

    # Formula authority remains external
    "research_formula_generation": False,
    "fixed_formula_assumption": False,
    "guessed_formula": False,
    "silent_formula_substitution": False,

    # Intelligence boundaries
    "distribution_generation": False,
    "breakout_generation": False,
    "confirmation_generation": False,
    "opportunity_generation": False,
    "scanner_generation": False,

    # Decision authority
    "decision_generation": False,
    "d13_generation": False,
    "d13_modification": False,

    # Risk / safety
    "risk_generation": False,
    "risk_override": False,
    "cas_generation": False,
    "cas_bypass": False,

    # Execution
    "execution": False,
    "order_authority": False,
    "order_mutation": False,
    "position_authority": False,
    "position_mutation": False,
    "portfolio_mutation": False,

    # Upstream truth protection
    "upstream_mutation": False,
}


# ============================================================
# ENUMS
# ============================================================

class AccumulationStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    READY = "READY"
    DEGRADED = "DEGRADED"
    INVALID = "INVALID"


class AccumulationState(str, Enum):
    UNKNOWN = "UNKNOWN"
    ABSENT = "ABSENT"
    POSSIBLE = "POSSIBLE"
    DEVELOPING = "DEVELOPING"
    CONFIRMED = "CONFIRMED"
    INVALIDATED = "INVALIDATED"


class AccumulationDirection(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"


class AccumulationPhase(str, Enum):
    EARLY = "EARLY"
    DEVELOPING = "DEVELOPING"
    MATURE = "MATURE"
    TRANSITION = "TRANSITION"
    UNKNOWN = "UNKNOWN"


class AccumulationStrength(str, Enum):
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"
    UNKNOWN = "UNKNOWN"


class AccumulationConfidence(str, Enum):
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"
    UNKNOWN = "UNKNOWN"


class Timeframe(str, Enum):
    M5 = "5m"
    M15 = "15m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"
    W1 = "1w"
    MN1 = "1mo"
    UNKNOWN = "UNKNOWN"


class AccumulationRelation(str, Enum):
    ALIGNED = "ALIGNED"
    DIVERGENT = "DIVERGENT"
    CONFLICTING = "CONFLICTING"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"


# ============================================================
# SAFE NORMALIZATION HELPERS
# ============================================================

def _accumulation_text(
    value: Any,
    default: str = "",
) -> str:
    if value is None:
        return default

    try:
        text = str(value).strip()
    except Exception:
        return default

    return text if text else default


def _accumulation_bool(
    value: Any,
    default: bool = False,
) -> bool:
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

    return default


def _accumulation_float(
    value: Any,
    default: float = 0.0,
) -> float:
    if value is None:
        return default

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _accumulation_int(
    value: Any,
    default: int = 0,
) -> int:
    if value is None:
        return default

    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _accumulation_enum(
    enum_type: Any,
    value: Any,
    default: Any,
) -> Any:
    if isinstance(value, enum_type):
        return value

    try:
        return enum_type(value)
    except (TypeError, ValueError):
        return default


def _accumulation_now() -> datetime:
    return datetime.now(timezone.utc)


# ============================================================
# CORE INPUT CONTRACT
# ============================================================

@dataclass
class AccumulationInput:
    instrument_id: str = ""
    symbol: str = ""

    asset_class: str = ""
    market_id: str = ""
    exchange: str = ""

    timeframe: Timeframe = Timeframe.UNKNOWN

    timestamps: List[Any] = field(default_factory=list)

    opens: List[float] = field(default_factory=list)
    highs: List[float] = field(default_factory=list)
    lows: List[float] = field(default_factory=list)
    closes: List[float] = field(default_factory=list)
    volumes: List[float] = field(default_factory=list)

    # Optional upstream structure context.
    structure_context: Optional[Any] = None

    source: str = ""

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MultiTimeframeAccumulationInput:
    instrument_id: str = ""
    symbol: str = ""

    inputs: List[AccumulationInput] = field(default_factory=list)

    primary_timeframe: Timeframe = Timeframe.UNKNOWN

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# SUPPORTING MEASUREMENT CONTRACTS
# ============================================================

@dataclass
class AccumulationMeasurement:
    name: str = ""
    value: Optional[float] = None
    normalized_value: Optional[float] = None

    available: bool = False
    valid: bool = False

    source: str = ""

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AccumulationWindow:
    instrument_id: str = ""
    symbol: str = ""

    timeframe: Timeframe = Timeframe.UNKNOWN

    start_time: Optional[Any] = None
    end_time: Optional[Any] = None

    bars_count: int = 0

    high: Optional[float] = None
    low: Optional[float] = None

    first_price: Optional[float] = None
    last_price: Optional[float] = None

    total_volume: Optional[float] = None
    average_volume: Optional[float] = None

    source: str = ""

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# ACCUMULATION ANALYSIS CONTRACT
# ============================================================

@dataclass
class AccumulationAnalysis:
    instrument_id: str = ""
    symbol: str = ""

    timeframe: Timeframe = Timeframe.UNKNOWN

    status: AccumulationStatus = AccumulationStatus.UNKNOWN

    state: AccumulationState = AccumulationState.UNKNOWN
    direction: AccumulationDirection = AccumulationDirection.UNKNOWN
    phase: AccumulationPhase = AccumulationPhase.UNKNOWN
    strength: AccumulationStrength = AccumulationStrength.UNKNOWN
    confidence_class: AccumulationConfidence = (
        AccumulationConfidence.UNKNOWN
    )

    confidence: float = 0.0

    measurements: List[AccumulationMeasurement] = field(
        default_factory=list
    )

    accumulation_window: Optional[AccumulationWindow] = None

    # Research traceability.
    formula_id: str = ""
    formula_version: str = ""

    research_validated: bool = False

    generated_at: datetime = field(
        default_factory=_accumulation_now
    )

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# MULTI-TIMEFRAME RESULT
# ============================================================

@dataclass
class MultiTimeframeAccumulation:
    instrument_id: str = ""
    symbol: str = ""

    timeframe_analyses: List[AccumulationAnalysis] = field(
        default_factory=list
    )

    primary_timeframe: Timeframe = Timeframe.UNKNOWN

    dominant_state: AccumulationState = AccumulationState.UNKNOWN
    dominant_direction: AccumulationDirection = (
        AccumulationDirection.UNKNOWN
    )

    relation: AccumulationRelation = AccumulationRelation.UNKNOWN

    confidence: float = 0.0

    research_validated: bool = False

    generated_at: datetime = field(
        default_factory=_accumulation_now
    )

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# ENGINE RESULT
# ============================================================

@dataclass
class AccumulationEngineResult:
    status: AccumulationStatus = AccumulationStatus.UNKNOWN

    analysis: Optional[AccumulationAnalysis] = None
    multi_timeframe: Optional[MultiTimeframeAccumulation] = None

    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    formula_id: str = ""
    formula_version: str = ""

    research_formula_available: bool = False
    research_formula_validated: bool = False

    generated_at: datetime = field(
        default_factory=_accumulation_now
    )

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# REQUEST / SNAPSHOT
# ============================================================

@dataclass
class AccumulationEngineRequest:
    input_data: Optional[AccumulationInput] = None

    multi_timeframe_input: Optional[
        MultiTimeframeAccumulationInput
    ] = None

    requested_timeframes: List[Timeframe] = field(
        default_factory=list
    )

    formula_id: str = ""
    formula_version: str = ""

    require_validated_formula: bool = True

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AccumulationEngineSnapshot:
    request: AccumulationEngineRequest
    result: AccumulationEngineResult

    captured_at: datetime = field(
        default_factory=_accumulation_now
    )

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# ENGINE CONTRACT
# ============================================================

ACCUMULATION_ENGINE_CONTRACT: Dict[str, Any] = {
    "layer": "INTELLIGENCE_ENGINE",
    "role": "ACCUMULATION_INTELLIGENCE",

    "mission": (
        "Convert normalized market observations and validated "
        "upstream structure context into traceable accumulation "
        "intelligence."
    ),

    "inputs": [
        "NORMALIZED_OHLCV_INPUT",
        "STRUCTURE_INTELLIGENCE_OUTPUT",
        "MULTI_TIMEFRAME_MARKET_INPUT",
        "FORMULA_REGISTRY_REFERENCE",
        "RESEARCH_VALIDATION_STATE",
    ],

    "outputs": [
        "ACCUMULATION_ANALYSIS",
        "MULTI_TIMEFRAME_ACCUMULATION",
        "ACCUMULATION_ENGINE_RESULT",
        "ACCUMULATION_ENGINE_SNAPSHOT",
    ],

    "supported_timeframes": [
        "5m",
        "15m",
        "1h",
        "4h",
        "1d",
        "1w",
        "1mo",
    ],

    "authority_owner": "UPSTREAM_ACCUMULATION_INTELLIGENCE",

    "formula_policy": {
        "formula_pluggable": True,
        "formula_registry_required": True,
        "formula_explicit": True,
        "validated_formula_required": True,
        "formula_version_traceability": True,
        "default_formula": False,
        "guessed_formula": False,
        "silent_substitution": False,
    },

    "downstream_consumers": [
        "BOUNDARY_ENGINE",
        "BREAKOUT_ENGINE",
        "CONFIRMATION_ENGINE",
        "RELATIONSHIP_ENGINE",
        "OPPORTUNITY_ENGINE",
        "EQUITY_SCANNER",
        "FUTURE_SCANNER",
    ],

    "forbidden_authority": [
        "DISTRIBUTION_GENERATION",
        "BREAKOUT_GENERATION",
        "CONFIRMATION_GENERATION",
        "OPPORTUNITY_GENERATION",
        "SCANNER_GENERATION",
        "DECISION_GENERATION",
        "D13_GENERATION",
        "D13_MODIFICATION",
        "RISK_GENERATION",
        "RISK_OVERRIDE",
        "CAS_GENERATION",
        "CAS_BYPASS",
        "EXECUTION",
        "ORDER_AUTHORITY",
        "POSITION_AUTHORITY",
        "UPSTREAM_MUTATION",
    ],
}


# ============================================================
# AUTHORITY VALIDATION
# ============================================================

def validate_accumulation_authority() -> bool:
    """
    Validate that the accumulation engine does not claim
    authority outside its architectural boundary.
    """

    required_false = [
        "research_formula_generation",
        "fixed_formula_assumption",
        "guessed_formula",
        "silent_formula_substitution",
        "distribution_generation",
        "breakout_generation",
        "confirmation_generation",
        "opportunity_generation",
        "scanner_generation",
        "decision_generation",
        "d13_generation",
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
    ]

    return all(
        ACCUMULATION_ENGINE_AUTHORITY.get(
            key,
            False,
        ) is False
        for key in required_false
    )


def accumulation_engine_summary() -> Dict[str, Any]:
    return {
        "engine": ACCUMULATION_ENGINE,
        "version": ACCUMULATION_ENGINE_VERSION,
        "name": ACCUMULATION_ENGINE_NAME,
        "role": ACCUMULATION_ENGINE_CONTRACT["role"],
        "layer": ACCUMULATION_ENGINE_CONTRACT["layer"],
        "authority_owner": ACCUMULATION_ENGINE_CONTRACT[
            "authority_owner"
        ],
        "formula_pluggable": True,
        "validated_formula_required": True,
        "research_formula_generation": False,
        "opportunity_generation": False,
        "decision_generation": False,
        "d13_modification": False,
        "risk_override": False,
        "cas_bypass": False,
        "execution": False,
        "upstream_mutation": False,
    }


# ============================================================
# PUBLIC EXPORTS — PART 1
# ============================================================

__all__ = [
    # Identity
    "ACCUMULATION_ENGINE",
    "ACCUMULATION_ENGINE_VERSION",
    "ACCUMULATION_ENGINE_NAME",
    "ACCUMULATION_ENGINE_DESCRIPTION",

    # Authority
    "ACCUMULATION_ENGINE_AUTHORITY",
    "ACCUMULATION_ENGINE_CONTRACT",

    # Enums
    "AccumulationStatus",
    "AccumulationState",
    "AccumulationDirection",
    "AccumulationPhase",
    "AccumulationStrength",
    "AccumulationConfidence",
    "Timeframe",
    "AccumulationRelation",

    # Inputs / measurements
    "AccumulationInput",
    "MultiTimeframeAccumulationInput",
    "AccumulationMeasurement",
    "AccumulationWindow",

    # Analysis / result
    "AccumulationAnalysis",
    "MultiTimeframeAccumulation",
    "AccumulationEngineResult",
    "AccumulationEngineRequest",
    "AccumulationEngineSnapshot",

    # Validation / summary
    "validate_accumulation_authority",
    "accumulation_engine_summary",
]
# ============================================================
# ROBOMLM_PLUS
# Accumulation Intelligence Engine
# Part 2 / 5
# ============================================================

from abc import ABC, abstractmethod


# ============================================================
# NORMALIZATION
# ============================================================

def _normalize_accumulation_series(
    values: Any,
) -> List[float]:
    if values is None:
        return []

    if not isinstance(values, (list, tuple)):
        return []

    result: List[float] = []

    for value in values:
        try:
            result.append(float(value))
        except (TypeError, ValueError):
            continue

    return result


def _normalize_accumulation_timestamps(
    values: Any,
) -> List[Any]:
    if values is None:
        return []

    if not isinstance(values, (list, tuple)):
        return []

    return list(values)


def normalize_accumulation_input(
    value: Any,
) -> AccumulationInput:
    if isinstance(value, AccumulationInput):
        source = value
    elif isinstance(value, dict):
        source = AccumulationInput(
            instrument_id=_accumulation_text(
                value.get("instrument_id")
            ),
            symbol=_accumulation_text(
                value.get("symbol")
            ),
            asset_class=_accumulation_text(
                value.get("asset_class")
            ),
            market_id=_accumulation_text(
                value.get("market_id")
            ),
            exchange=_accumulation_text(
                value.get("exchange")
            ),
            timeframe=_accumulation_enum(
                Timeframe,
                value.get("timeframe"),
                Timeframe.UNKNOWN,
            ),
            timestamps=_normalize_accumulation_timestamps(
                value.get("timestamps")
            ),
            opens=_normalize_accumulation_series(
                value.get("opens")
            ),
            highs=_normalize_accumulation_series(
                value.get("highs")
            ),
            lows=_normalize_accumulation_series(
                value.get("lows")
            ),
            closes=_normalize_accumulation_series(
                value.get("closes")
            ),
            volumes=_normalize_accumulation_series(
                value.get("volumes")
            ),
            structure_context=value.get(
                "structure_context"
            ),
            source=_accumulation_text(
                value.get("source")
            ),
            metadata=dict(
                value.get("metadata") or {}
            ),
        )
    else:
        source = AccumulationInput()

    source.instrument_id = _accumulation_text(
        source.instrument_id
    )
    source.symbol = _accumulation_text(
        source.symbol
    )
    source.asset_class = _accumulation_text(
        source.asset_class
    )
    source.market_id = _accumulation_text(
        source.market_id
    )
    source.exchange = _accumulation_text(
        source.exchange
    )

    source.timeframe = _accumulation_enum(
        Timeframe,
        source.timeframe,
        Timeframe.UNKNOWN,
    )

    source.timestamps = _normalize_accumulation_timestamps(
        source.timestamps
    )

    source.opens = _normalize_accumulation_series(
        source.opens
    )
    source.highs = _normalize_accumulation_series(
        source.highs
    )
    source.lows = _normalize_accumulation_series(
        source.lows
    )
    source.closes = _normalize_accumulation_series(
        source.closes
    )
    source.volumes = _normalize_accumulation_series(
        source.volumes
    )

    source.metadata = dict(source.metadata or {})

    return source


def normalize_multitimeframe_accumulation_input(
    value: Any,
) -> MultiTimeframeAccumulationInput:
    if isinstance(
        value,
        MultiTimeframeAccumulationInput,
    ):
        source = value

    elif isinstance(value, dict):
        raw_inputs = value.get("inputs") or []

        source = MultiTimeframeAccumulationInput(
            instrument_id=_accumulation_text(
                value.get("instrument_id")
            ),
            symbol=_accumulation_text(
                value.get("symbol")
            ),
            inputs=[
                normalize_accumulation_input(item)
                for item in raw_inputs
            ],
            primary_timeframe=_accumulation_enum(
                Timeframe,
                value.get("primary_timeframe"),
                Timeframe.UNKNOWN,
            ),
            metadata=dict(
                value.get("metadata") or {}
            ),
        )

    else:
        source = MultiTimeframeAccumulationInput()

    source.instrument_id = _accumulation_text(
        source.instrument_id
    )
    source.symbol = _accumulation_text(
        source.symbol
    )

    source.inputs = [
        normalize_accumulation_input(item)
        for item in (source.inputs or [])
    ]

    source.primary_timeframe = _accumulation_enum(
        Timeframe,
        source.primary_timeframe,
        Timeframe.UNKNOWN,
    )

    source.metadata = dict(
        source.metadata or {}
    )

    return source


# ============================================================
# INPUT VALIDATION
# ============================================================

def validate_accumulation_input(
    value: Any,
) -> bool:
    data = normalize_accumulation_input(value)

    if not data.instrument_id and not data.symbol:
        return False

    lengths = [
        len(data.opens),
        len(data.highs),
        len(data.lows),
        len(data.closes),
    ]

    non_zero = [
        length
        for length in lengths
        if length > 0
    ]

    if not non_zero:
        return False

    if len(set(non_zero)) > 1:
        return False

    if data.volumes and len(data.volumes) != non_zero[0]:
        return False

    if data.timestamps and len(data.timestamps) != non_zero[0]:
        return False

    for index in range(len(data.highs)):
        if index >= len(data.lows):
            return False

        high = data.highs[index]
        low = data.lows[index]

        if high < low:
            return False

        if high <= 0 or low <= 0:
            return False

    return True


def accumulation_input_readiness(
    value: Any,
) -> Dict[str, Any]:
    data = normalize_accumulation_input(value)

    valid = validate_accumulation_input(data)

    observation_count = max(
        len(data.closes),
        len(data.highs),
        len(data.lows),
    )

    missing = []

    if not data.instrument_id and not data.symbol:
        missing.append("instrument_id_or_symbol")

    if observation_count == 0:
        missing.append("ohlc_observations")

    if not data.volumes:
        missing.append("volume_series")

    return {
        "ready": valid,
        "valid": valid,
        "observation_count": observation_count,
        "volume_available": bool(data.volumes),
        "structure_context_available": (
            data.structure_context is not None
        ),
        "missing": missing,
    }


# ============================================================
# WINDOW BUILDING
# ============================================================

def build_accumulation_window(
    value: Any,
) -> AccumulationWindow:
    data = normalize_accumulation_input(value)

    count = max(
        len(data.closes),
        len(data.highs),
        len(data.lows),
    )

    high = (
        max(data.highs)
        if data.highs
        else None
    )

    low = (
        min(data.lows)
        if data.lows
        else None
    )

    first_price = (
        data.closes[0]
        if data.closes
        else None
    )

    last_price = (
        data.closes[-1]
        if data.closes
        else None
    )

    total_volume = (
        sum(data.volumes)
        if data.volumes
        else None
    )

    average_volume = (
        total_volume / len(data.volumes)
        if data.volumes
        else None
    )

    start_time = (
        data.timestamps[0]
        if data.timestamps
        else None
    )

    end_time = (
        data.timestamps[-1]
        if data.timestamps
        else None
    )

    return AccumulationWindow(
        instrument_id=data.instrument_id,
        symbol=data.symbol,
        timeframe=data.timeframe,
        start_time=start_time,
        end_time=end_time,
        bars_count=count,
        high=high,
        low=low,
        first_price=first_price,
        last_price=last_price,
        total_volume=total_volume,
        average_volume=average_volume,
        source=data.source,
        metadata={
            "window_generated": True,
            "research_formula_generated": False,
        },
    )


# ============================================================
# MEASUREMENT HELPERS
# ============================================================

def create_accumulation_measurement(
    name: str,
    value: Optional[float] = None,
    normalized_value: Optional[float] = None,
    available: bool = False,
    valid: bool = False,
    source: str = "",
    metadata: Optional[Dict[str, Any]] = None,
) -> AccumulationMeasurement:
    return AccumulationMeasurement(
        name=_accumulation_text(name),
        value=value,
        normalized_value=normalized_value,
        available=bool(available),
        valid=bool(valid),
        source=_accumulation_text(source),
        metadata=dict(metadata or {}),
    )


# ============================================================
# REQUESTED TIMEFRAME NORMALIZATION
# ============================================================

def normalize_requested_timeframes(
    values: Any,
) -> List[Timeframe]:
    if values is None:
        return []

    if not isinstance(values, (list, tuple)):
        values = [values]

    result: List[Timeframe] = []

    for value in values:
        timeframe = _accumulation_enum(
            Timeframe,
            value,
            Timeframe.UNKNOWN,
        )

        if (
            timeframe != Timeframe.UNKNOWN
            and timeframe not in result
        ):
            result.append(timeframe)

    return result


def build_multitimeframe_accumulation_input(
    inputs: Any,
    primary_timeframe: Any = Timeframe.UNKNOWN,
) -> MultiTimeframeAccumulationInput:
    normalized = [
        normalize_accumulation_input(item)
        for item in (inputs or [])
    ]

    return MultiTimeframeAccumulationInput(
        instrument_id=(
            normalized[0].instrument_id
            if normalized
            else ""
        ),
        symbol=(
            normalized[0].symbol
            if normalized
            else ""
        ),
        inputs=normalized,
        primary_timeframe=_accumulation_enum(
            Timeframe,
            primary_timeframe,
            Timeframe.UNKNOWN,
        ),
        metadata={
            "multitimeframe_input": True,
        },
    )


# ============================================================
# RESEARCH FORMULA CONTRACT
# ============================================================

@dataclass
class AccumulationFormulaDescriptor:
    formula_id: str = ""
    formula_version: str = ""

    name: str = ""
    description: str = ""

    supported_asset_classes: List[str] = field(
        default_factory=list
    )

    supported_timeframes: List[Timeframe] = field(
        default_factory=list
    )

    validated: bool = False
    enabled: bool = False

    owner: str = (
        "UPSTREAM_ACCUMULATION_INTELLIGENCE"
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


class AccumulationFormulaProvider(ABC):
    """
    Interface for externally validated accumulation
    research formulas.

    The engine does not define the research formula.
    """

    @abstractmethod
    def describe(
        self,
    ) -> AccumulationFormulaDescriptor:
        raise NotImplementedError

    @abstractmethod
    def analyze(
        self,
        value: AccumulationInput,
    ) -> AccumulationAnalysis:
        raise NotImplementedError


# ============================================================
# FORMULA REGISTRY
# ============================================================

class AccumulationFormulaRegistry:
    def __init__(self) -> None:
        self._providers: Dict[
            str,
            AccumulationFormulaProvider,
        ] = {}

    def register(
        self,
        provider: AccumulationFormulaProvider,
    ) -> None:
        descriptor = provider.describe()

        formula_id = _accumulation_text(
            descriptor.formula_id
        )

        if not formula_id:
            raise ValueError(
                "Accumulation formula_id is required."
            )

        self._providers[formula_id] = provider

    def get(
        self,
        formula_id: str,
    ) -> Optional[
        AccumulationFormulaProvider
    ]:
        return self._providers.get(
            _accumulation_text(formula_id)
        )

    def unregister(
        self,
        formula_id: str,
    ) -> None:
        self._providers.pop(
            _accumulation_text(formula_id),
            None,
        )

    def descriptors(
        self,
    ) -> List[AccumulationFormulaDescriptor]:
        return [
            provider.describe()
            for provider in self._providers.values()
        ]

    def clear(self) -> None:
        self._providers.clear()

    def __len__(self) -> int:
        return len(self._providers)


_DEFAULT_ACCUMULATION_FORMULA_REGISTRY = (
    AccumulationFormulaRegistry()
)


def get_accumulation_formula_registry(
) -> AccumulationFormulaRegistry:
    return _DEFAULT_ACCUMULATION_FORMULA_REGISTRY


def resolve_accumulation_formula(
    formula_id: str,
    formula_version: str = "",
) -> Optional[
    AccumulationFormulaProvider
]:
    provider = (
        get_accumulation_formula_registry().get(
            formula_id
        )
    )

    if provider is None:
        return None

    descriptor = provider.describe()

    if formula_version:
        if (
            descriptor.formula_version
            != formula_version
        ):
            return None

    return provider


# ============================================================
# FORMULA AVAILABILITY
# ============================================================

def accumulation_formula_readiness(
    formula_id: str = "",
    formula_version: str = "",
    require_validated: bool = True,
) -> Dict[str, Any]:
    formula_id = _accumulation_text(
        formula_id
    )

    if not formula_id:
        return {
            "available": False,
            "validated": False,
            "formula_id": "",
            "formula_version": "",
            "reason": "NO_FORMULA_SELECTED",
        }

    provider = resolve_accumulation_formula(
        formula_id,
        formula_version,
    )

    if provider is None:
        return {
            "available": False,
            "validated": False,
            "formula_id": formula_id,
            "formula_version": formula_version,
            "reason": "FORMULA_NOT_FOUND_OR_VERSION_MISMATCH",
        }

    descriptor = provider.describe()

    if require_validated and not descriptor.validated:
        return {
            "available": False,
            "validated": False,
            "formula_id": descriptor.formula_id,
            "formula_version": descriptor.formula_version,
            "reason": "FORMULA_NOT_VALIDATED",
        }

    if not descriptor.enabled:
        return {
            "available": False,
            "validated": bool(descriptor.validated),
            "formula_id": descriptor.formula_id,
            "formula_version": descriptor.formula_version,
            "reason": "FORMULA_DISABLED",
        }

    return {
        "available": True,
        "validated": bool(descriptor.validated),
        "formula_id": descriptor.formula_id,
        "formula_version": descriptor.formula_version,
        "reason": "READY",
    }


# ============================================================
# PART 2 CONTRACT
# ============================================================

ACCUMULATION_ENGINE_PART2_CONTRACT: Dict[str, Any] = {
    "normalization": True,
    "input_validation": True,
    "window_building": True,
    "measurement_contract": True,

    "formula_registry": True,
    "formula_plugin": True,
    "formula_pluggable": True,

    "validated_formula_required": True,
    "formula_version_required_for_traceability": True,

    "default_formula": False,
    "guessed_formula": False,
    "fixed_formula_assumption": False,
    "silent_formula_substitution": False,

    "intelligence_generated_here": False,
    "opportunity_generated_here": False,
    "decision_generated_here": False,
    "d13_modified_here": False,
    "risk_generated_here": False,
    "cas_bypassed_here": False,
    "execution_here": False,
}


# ============================================================
# PART 2 VALIDATION
# ============================================================

def validate_accumulation_part2() -> bool:
    forbidden = [
        "default_formula",
        "guessed_formula",
        "fixed_formula_assumption",
        "silent_formula_substitution",
        "intelligence_generated_here",
        "opportunity_generated_here",
        "decision_generated_here",
        "d13_modified_here",
        "risk_generated_here",
        "cas_bypassed_here",
        "execution_here",
    ]

    return all(
        ACCUMULATION_ENGINE_PART2_CONTRACT.get(
            key,
            False,
        ) is False
        for key in forbidden
    )


# ============================================================
# EXPORTS — PART 2
# ============================================================

__all__.extend([
    # Normalization
    "normalize_accumulation_input",
    "normalize_multitimeframe_accumulation_input",

    # Validation/readiness
    "validate_accumulation_input",
    "accumulation_input_readiness",

    # Window / measurements
    "build_accumulation_window",
    "create_accumulation_measurement",

    # Timeframes
    "normalize_requested_timeframes",
    "build_multitimeframe_accumulation_input",

    # Formula architecture
    "AccumulationFormulaDescriptor",
    "AccumulationFormulaProvider",
    "AccumulationFormulaRegistry",
    "get_accumulation_formula_registry",
    "resolve_accumulation_formula",
    "accumulation_formula_readiness",

    # Contract
    "ACCUMULATION_ENGINE_PART2_CONTRACT",
    "validate_accumulation_part2",
])
# ============================================================
# ROBOMLM_PLUS
# Accumulation Intelligence Engine
# Part 3 / 5
# ============================================================


# ============================================================
# FORMULA METADATA
# ============================================================

def _accumulation_formula_metadata(
    descriptor: Optional[
        AccumulationFormulaDescriptor
    ],
) -> Dict[str, Any]:
    if descriptor is None:
        return {
            "formula_available": False,
            "formula_validated": False,
            "research_formula_generated": False,
            "formula_id": "",
            "formula_version": "",
        }

    return {
        "formula_available": True,
        "formula_validated": bool(
            descriptor.validated
        ),
        "research_formula_generated": True,
        "formula_id": descriptor.formula_id,
        "formula_version": descriptor.formula_version,
        "formula_owner": descriptor.owner,
    }


# ============================================================
# SINGLE TIMEFRAME ANALYSIS
# ============================================================

def analyze_accumulation(
    value: Any,
    formula_id: str = "",
    formula_version: str = "",
    require_validated_formula: bool = True,
) -> AccumulationEngineResult:

    data = normalize_accumulation_input(value)

    readiness = accumulation_input_readiness(data)

    if not readiness["ready"]:
        return AccumulationEngineResult(
            status=AccumulationStatus.INSUFFICIENT_DATA,
            warnings=[
                "Accumulation input is not ready."
            ],
            errors=list(
                readiness.get("missing", [])
            ),
            formula_id=_accumulation_text(
                formula_id
            ),
            formula_version=_accumulation_text(
                formula_version
            ),
            research_formula_available=False,
            research_formula_validated=False,
            metadata={
                "intelligence_generated": False,
                "research_formula_generated": False,
            },
        )

    formula_state = accumulation_formula_readiness(
        formula_id=formula_id,
        formula_version=formula_version,
        require_validated=require_validated_formula,
    )

    if not formula_state["available"]:
        return AccumulationEngineResult(
            status=AccumulationStatus.DEGRADED,
            warnings=[
                formula_state["reason"]
            ],
            errors=[],
            formula_id=formula_state[
                "formula_id"
            ],
            formula_version=formula_state[
                "formula_version"
            ],
            research_formula_available=False,
            research_formula_validated=bool(
                formula_state["validated"]
            ),
            metadata={
                "intelligence_generated": False,
                "research_formula_generated": False,
                "formula_required": True,
            },
        )

    provider = resolve_accumulation_formula(
        formula_id=formula_id,
        formula_version=formula_version,
    )

    if provider is None:
        return AccumulationEngineResult(
            status=AccumulationStatus.DEGRADED,
            warnings=[
                "Accumulation formula provider unavailable."
            ],
            formula_id=_accumulation_text(
                formula_id
            ),
            formula_version=_accumulation_text(
                formula_version
            ),
            metadata={
                "intelligence_generated": False,
                "research_formula_generated": False,
            },
        )

    descriptor = provider.describe()

    try:
        analysis = provider.analyze(data)
    except Exception as exc:
        return AccumulationEngineResult(
            status=AccumulationStatus.INVALID,
            warnings=[],
            errors=[
                f"Accumulation formula execution failed: {exc}"
            ],
            formula_id=descriptor.formula_id,
            formula_version=descriptor.formula_version,
            research_formula_available=True,
            research_formula_validated=bool(
                descriptor.validated
            ),
            metadata={
                "intelligence_generated": False,
                "formula_execution_failed": True,
                "research_formula_generated": False,
            },
        )

    if not isinstance(
        analysis,
        AccumulationAnalysis,
    ):
        return AccumulationEngineResult(
            status=AccumulationStatus.INVALID,
            errors=[
                "Accumulation formula returned an invalid analysis type."
            ],
            formula_id=descriptor.formula_id,
            formula_version=descriptor.formula_version,
            research_formula_available=True,
            research_formula_validated=bool(
                descriptor.validated
            ),
            metadata={
                "intelligence_generated": False,
                "research_formula_generated": False,
            },
        )

    # --------------------------------------------------------
    # Fill traceability fields without changing research truth.
    # --------------------------------------------------------

    if not analysis.instrument_id:
        analysis.instrument_id = data.instrument_id

    if not analysis.symbol:
        analysis.symbol = data.symbol

    if analysis.timeframe == Timeframe.UNKNOWN:
        analysis.timeframe = data.timeframe

    if not analysis.formula_id:
        analysis.formula_id = descriptor.formula_id

    if not analysis.formula_version:
        analysis.formula_version = (
            descriptor.formula_version
        )

    analysis.research_validated = bool(
        descriptor.validated
    )

    if analysis.accumulation_window is None:
        analysis.accumulation_window = (
            build_accumulation_window(data)
        )

    analysis.metadata = {
        **dict(analysis.metadata or {}),
        "upstream_research_formula": True,
        "research_formula_generated": True,
        "formula_id": descriptor.formula_id,
        "formula_version": descriptor.formula_version,
        "formula_owner": descriptor.owner,
        "engine_generated_guess": False,
        "engine_generated_formula": False,
    }

    return AccumulationEngineResult(
        status=(
            analysis.status
            if analysis.status != AccumulationStatus.UNKNOWN
            else AccumulationStatus.READY
        ),
        analysis=analysis,
        formula_id=descriptor.formula_id,
        formula_version=descriptor.formula_version,
        research_formula_available=True,
        research_formula_validated=bool(
            descriptor.validated
        ),
        metadata={
            **_accumulation_formula_metadata(
                descriptor
            ),
            "intelligence_generated": True,
            "engine_generated_formula": False,
            "upstream_truth_preserved": True,
        },
    )


# ============================================================
# RELATION EVALUATION
# ============================================================

def classify_accumulation_relation(
    analyses: List[AccumulationAnalysis],
) -> AccumulationRelation:

    valid = [
        item
        for item in analyses
        if isinstance(
            item,
            AccumulationAnalysis,
        )
        and item.status
        in {
            AccumulationStatus.READY,
            AccumulationStatus.DEGRADED,
        }
    ]

    if not valid:
        return AccumulationRelation.UNKNOWN

    states = {
        item.state
        for item in valid
        if item.state != AccumulationState.UNKNOWN
    }

    directions = {
        item.direction
        for item in valid
        if item.direction
        != AccumulationDirection.UNKNOWN
    }

    # Strong state conflict.
    if (
        AccumulationState.CONFIRMED in states
        and AccumulationState.INVALIDATED in states
    ):
        return AccumulationRelation.CONFLICTING

    # Direction conflict.
    if (
        AccumulationDirection.BULLISH in directions
        and AccumulationDirection.BEARISH in directions
    ):
        return AccumulationRelation.CONFLICTING

    if len(states) == 1 and len(directions) <= 1:
        only_state = next(iter(states))

        if only_state == AccumulationState.ABSENT:
            return AccumulationRelation.NEUTRAL

        return AccumulationRelation.ALIGNED

    if (
        AccumulationDirection.NEUTRAL in directions
        and len(directions) > 1
    ):
        return AccumulationRelation.DIVERGENT

    if len(states) > 1 or len(directions) > 1:
        return AccumulationRelation.DIVERGENT

    return AccumulationRelation.NEUTRAL


# ============================================================
# DOMINANT ACCUMULATION STATE
# ============================================================

def determine_dominant_accumulation_state(
    analyses: List[AccumulationAnalysis],
) -> AccumulationState:

    priority = {
        AccumulationState.CONFIRMED: 5,
        AccumulationState.DEVELOPING: 4,
        AccumulationState.POSSIBLE: 3,
        AccumulationState.ABSENT: 2,
        AccumulationState.INVALIDATED: 1,
        AccumulationState.UNKNOWN: 0,
    }

    valid = [
        item
        for item in analyses
        if isinstance(
            item,
            AccumulationAnalysis,
        )
    ]

    if not valid:
        return AccumulationState.UNKNOWN

    ranked = sorted(
        valid,
        key=lambda item: priority.get(
            item.state,
            0,
        ),
        reverse=True,
    )

    return ranked[0].state


# ============================================================
# DOMINANT DIRECTION
# ============================================================

def determine_dominant_accumulation_direction(
    analyses: List[AccumulationAnalysis],
) -> AccumulationDirection:

    counts = {
        AccumulationDirection.BULLISH: 0,
        AccumulationDirection.BEARISH: 0,
        AccumulationDirection.NEUTRAL: 0,
        AccumulationDirection.MIXED: 0,
    }

    for analysis in analyses:
        direction = analysis.direction

        if direction in counts:
            counts[direction] += 1

    maximum = max(
        counts.values(),
        default=0,
    )

    if maximum == 0:
        return AccumulationDirection.UNKNOWN

    leaders = [
        direction
        for direction, count in counts.items()
        if count == maximum
    ]

    if len(leaders) > 1:
        if (
            AccumulationDirection.BULLISH in leaders
            and AccumulationDirection.BEARISH in leaders
        ):
            return AccumulationDirection.MIXED

        return AccumulationDirection.NEUTRAL

    return leaders[0]


# ============================================================
# MULTI-TIMEFRAME ANALYSIS
# ============================================================

def analyze_multitimeframe_accumulation(
    value: Any,
    formula_id: str = "",
    formula_version: str = "",
    require_validated_formula: bool = True,
    formula_map: Optional[
        Dict[str, str]
    ] = None,
    formula_version_map: Optional[
        Dict[str, str]
    ] = None,
) -> AccumulationEngineResult:

    mtf = normalize_multitimeframe_accumulation_input(
        value
    )

    if not mtf.inputs:
        return AccumulationEngineResult(
            status=AccumulationStatus.INSUFFICIENT_DATA,
            warnings=[
                "No accumulation timeframes supplied."
            ],
            metadata={
                "intelligence_generated": False,
            },
        )

    analyses: List[
        AccumulationAnalysis
    ] = []

    warnings: List[str] = []
    errors: List[str] = []

    formula_map = dict(formula_map or {})
    formula_version_map = dict(
        formula_version_map or {}
    )

    for input_data in mtf.inputs:

        timeframe_key = input_data.timeframe.value

        selected_formula = (
            formula_map.get(
                timeframe_key,
                formula_id,
            )
        )

        selected_version = (
            formula_version_map.get(
                timeframe_key,
                formula_version,
            )
        )

        result = analyze_accumulation(
            value=input_data,
            formula_id=selected_formula,
            formula_version=selected_version,
            require_validated_formula=(
                require_validated_formula
            ),
        )

        warnings.extend(result.warnings)
        errors.extend(result.errors)

        if result.analysis is not None:
            analyses.append(result.analysis)

    if not analyses:
        return AccumulationEngineResult(
            status=AccumulationStatus.DEGRADED,
            warnings=warnings,
            errors=errors,
            metadata={
                "intelligence_generated": False,
                "upstream_truth_preserved": False,
            },
        )

    relation = classify_accumulation_relation(
        analyses
    )

    dominant_state = (
        determine_dominant_accumulation_state(
            analyses
        )
    )

    dominant_direction = (
        determine_dominant_accumulation_direction(
            analyses
        )
    )

    primary = mtf.primary_timeframe

    if primary == Timeframe.UNKNOWN:
        primary = analyses[0].timeframe

    validated_count = sum(
        1
        for item in analyses
        if item.research_validated
    )

    confidence_values = [
        max(
            0.0,
            min(
                1.0,
                float(item.confidence),
            ),
        )
        for item in analyses
    ]

    confidence = (
        sum(confidence_values)
        / len(confidence_values)
        if confidence_values
        else 0.0
    )

    mtf_result = MultiTimeframeAccumulation(
        instrument_id=(
            mtf.instrument_id
            or analyses[0].instrument_id
        ),
        symbol=(
            mtf.symbol
            or analyses[0].symbol
        ),
        timeframe_analyses=analyses,
        primary_timeframe=primary,
        dominant_state=dominant_state,
        dominant_direction=dominant_direction,
        relation=relation,
        confidence=confidence,
        research_validated=(
            validated_count == len(analyses)
            and len(analyses) > 0
        ),
        metadata={
            "multitimeframe_analysis": True,
            "upstream_truth_preserved": True,
            "engine_generated_formula": False,
            "research_formula_generated": (
                validated_count > 0
            ),
        },
    )

    status = (
        AccumulationStatus.READY
        if mtf_result.research_validated
        else AccumulationStatus.DEGRADED
    )

    return AccumulationEngineResult(
        status=status,
        analysis=None,
        multi_timeframe=mtf_result,
        warnings=warnings,
        errors=errors,
        research_formula_available=(
            validated_count > 0
        ),
        research_formula_validated=(
            validated_count == len(analyses)
        ),
        metadata={
            "multitimeframe": True,
            "intelligence_generated": True,
            "upstream_truth_preserved": True,
            "research_formula_generated": (
                validated_count > 0
            ),
            "engine_generated_formula": False,
        },
    )


# ============================================================
# ENGINE REQUEST EXECUTION
# ============================================================

def run_accumulation_engine(
    request: AccumulationEngineRequest,
) -> AccumulationEngineResult:

    if not isinstance(
        request,
        AccumulationEngineRequest,
    ):
        return AccumulationEngineResult(
            status=AccumulationStatus.INVALID,
            errors=[
                "Invalid accumulation engine request."
            ],
            metadata={
                "intelligence_generated": False,
            },
        )

    if request.multi_timeframe_input is not None:
        return analyze_multitimeframe_accumulation(
            value=request.multi_timeframe_input,
            formula_id=request.formula_id,
            formula_version=request.formula_version,
            require_validated_formula=(
                request.require_validated_formula
            ),
            formula_map=request.metadata.get(
                "formula_map",
                {},
            ),
            formula_version_map=request.metadata.get(
                "formula_version_map",
                {},
            ),
        )

    if request.input_data is None:
        return AccumulationEngineResult(
            status=AccumulationStatus.INSUFFICIENT_DATA,
            errors=[
                "No accumulation input supplied."
            ],
            metadata={
                "intelligence_generated": False,
            },
        )

    return analyze_accumulation(
        value=request.input_data,
        formula_id=request.formula_id,
        formula_version=request.formula_version,
        require_validated_formula=(
            request.require_validated_formula
        ),
    )


# ============================================================
# SNAPSHOT
# ============================================================

def build_accumulation_engine_snapshot(
    request: AccumulationEngineRequest,
    result: AccumulationEngineResult,
) -> AccumulationEngineSnapshot:

    return AccumulationEngineSnapshot(
        request=request,
        result=result,
        captured_at=_accumulation_now(),
        metadata={
            "snapshot": True,
            "upstream_truth_preserved": True,
            "engine_generated_formula": False,
            "decision_authority": False,
            "d13_modified": False,
            "risk_override": False,
            "cas_bypass": False,
            "execution": False,
        },
    )


# ============================================================
# PART 3 CONTRACT
# ============================================================

ACCUMULATION_ENGINE_PART3_CONTRACT: Dict[str, Any] = {
    "single_timeframe_execution": True,
    "multi_timeframe_execution": True,

    "formula_resolution": True,
    "formula_version_resolution": True,
    "validated_formula_enforcement": True,

    "structure_context_consumption": True,

    "dominant_state_orchestration": True,
    "dominant_direction_orchestration": True,
    "relation_orchestration": True,

    "default_formula": False,
    "guessed_formula": False,
    "silent_formula_substitution": False,

    "engine_generated_formula": False,
    "opportunity_generated": False,
    "decision_generated": False,
    "d13_modified": False,
    "risk_generated": False,
    "cas_bypassed": False,
    "execution": False,

    "upstream_truth_preserved": True,
}


def validate_accumulation_part3() -> bool:
    forbidden = [
        "default_formula",
        "guessed_formula",
        "silent_formula_substitution",
        "engine_generated_formula",
        "opportunity_generated",
        "decision_generated",
        "d13_modified",
        "risk_generated",
        "cas_bypassed",
        "execution",
    ]

    return all(
        ACCUMULATION_ENGINE_PART3_CONTRACT.get(
            key,
            False,
        ) is False
        for key in forbidden
    )


# ============================================================
# EXPORTS — PART 3
# ============================================================

__all__.extend([
    "_accumulation_formula_metadata",

    "analyze_accumulation",

    "classify_accumulation_relation",
    "determine_dominant_accumulation_state",
    "determine_dominant_accumulation_direction",

    "analyze_multitimeframe_accumulation",

    "run_accumulation_engine",
    "build_accumulation_engine_snapshot",

    "ACCUMULATION_ENGINE_PART3_CONTRACT",
    "validate_accumulation_part3",
])
# ============================================================
# ROBOMLM_PLUS
# Accumulation Intelligence Engine
# Part 4 / 5
# ============================================================


# ============================================================
# SERIALIZATION
# ============================================================

def _serialize_accumulation_value(
    value: Any,
) -> Any:

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            str(key): _serialize_accumulation_value(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            _serialize_accumulation_value(item)
            for item in value
        ]

    if hasattr(value, "__dataclass_fields__"):
        return {
            key: _serialize_accumulation_value(
                getattr(value, key)
            )
            for key in value.__dataclass_fields__
        }

    return value


def serialize_accumulation_input(
    value: AccumulationInput,
) -> Dict[str, Any]:
    return _serialize_accumulation_value(value)


def serialize_accumulation_measurement(
    value: AccumulationMeasurement,
) -> Dict[str, Any]:
    return _serialize_accumulation_value(value)


def serialize_accumulation_window(
    value: AccumulationWindow,
) -> Dict[str, Any]:
    return _serialize_accumulation_value(value)


def serialize_accumulation_analysis(
    value: AccumulationAnalysis,
) -> Dict[str, Any]:
    return _serialize_accumulation_value(value)


def serialize_multitimeframe_accumulation(
    value: MultiTimeframeAccumulation,
) -> Dict[str, Any]:
    return _serialize_accumulation_value(value)


def serialize_accumulation_result(
    value: AccumulationEngineResult,
) -> Dict[str, Any]:
    return _serialize_accumulation_value(value)


def serialize_accumulation_request(
    value: AccumulationEngineRequest,
) -> Dict[str, Any]:
    return _serialize_accumulation_value(value)


def serialize_accumulation_snapshot(
    value: AccumulationEngineSnapshot,
) -> Dict[str, Any]:
    return _serialize_accumulation_value(value)


def serialize_accumulation_formula_descriptor(
    value: AccumulationFormulaDescriptor,
) -> Dict[str, Any]:
    return _serialize_accumulation_value(value)


# ============================================================
# VALIDATORS
# ============================================================

def validate_accumulation_measurement(
    value: Any,
) -> bool:

    if not isinstance(
        value,
        AccumulationMeasurement,
    ):
        return False

    if not value.name:
        return False

    if value.normalized_value is not None:
        if not 0.0 <= float(
            value.normalized_value
        ) <= 1.0:
            return False

    return True


def validate_accumulation_window(
    value: Any,
) -> bool:

    if not isinstance(
        value,
        AccumulationWindow,
    ):
        return False

    if value.bars_count < 0:
        return False

    if (
        value.high is not None
        and value.high <= 0
    ):
        return False

    if (
        value.low is not None
        and value.low <= 0
    ):
        return False

    if (
        value.high is not None
        and value.low is not None
        and value.high < value.low
    ):
        return False

    if (
        value.average_volume is not None
        and value.average_volume < 0
    ):
        return False

    if (
        value.total_volume is not None
        and value.total_volume < 0
    ):
        return False

    return True


def validate_accumulation_analysis(
    value: Any,
) -> bool:

    if not isinstance(
        value,
        AccumulationAnalysis,
    ):
        return False

    if not value.instrument_id and not value.symbol:
        return False

    if not 0.0 <= float(
        value.confidence
    ) <= 1.0:
        return False

    if value.accumulation_window is not None:
        if not validate_accumulation_window(
            value.accumulation_window
        ):
            return False

    for measurement in value.measurements:
        if not validate_accumulation_measurement(
            measurement
        ):
            return False

    # Formula traceability rule.
    if value.formula_id:
        if not value.formula_version:
            return False

        if not value.research_validated:
            return False

    return True


def validate_multitimeframe_accumulation(
    value: Any,
) -> bool:

    if not isinstance(
        value,
        MultiTimeframeAccumulation,
    ):
        return False

    if not value.instrument_id and not value.symbol:
        return False

    if (
        value.primary_timeframe
        == Timeframe.UNKNOWN
    ):
        return False

    if not 0.0 <= float(
        value.confidence
    ) <= 1.0:
        return False

    if not value.timeframe_analyses:
        return False

    for analysis in value.timeframe_analyses:
        if not validate_accumulation_analysis(
            analysis
        ):
            return False

    if (
        value.research_validated
        and not all(
            item.research_validated
            for item in value.timeframe_analyses
        )
    ):
        return False

    return True


def validate_accumulation_result(
    value: Any,
) -> bool:

    if not isinstance(
        value,
        AccumulationEngineResult,
    ):
        return False

    if value.analysis is not None:
        if not validate_accumulation_analysis(
            value.analysis
        ):
            return False

    if value.multi_timeframe is not None:
        if not validate_multitimeframe_accumulation(
            value.multi_timeframe
        ):
            return False

    if (
        value.research_formula_validated
        and not value.research_formula_available
    ):
        return False

    return True


def validate_accumulation_formula_descriptor(
    value: Any,
) -> bool:

    if not isinstance(
        value,
        AccumulationFormulaDescriptor,
    ):
        return False

    if value.validated and not value.formula_id:
        return False

    if value.validated and not value.formula_version:
        return False

    if value.validated and not value.owner:
        return False

    if (
        value.owner
        != "UPSTREAM_ACCUMULATION_INTELLIGENCE"
    ):
        return False

    return True


# ============================================================
# ENGINE INTEGRITY
# ============================================================

def validate_accumulation_engine_integrity() -> bool:

    if not validate_accumulation_authority():
        return False

    if not validate_accumulation_part2():
        return False

    if not validate_accumulation_part3():
        return False

    forbidden = [
        "research_formula_generation",
        "fixed_formula_assumption",
        "guessed_formula",
        "silent_formula_substitution",
        "distribution_generation",
        "breakout_generation",
        "confirmation_generation",
        "opportunity_generation",
        "scanner_generation",
        "decision_generation",
        "d13_generation",
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
    ]

    return all(
        ACCUMULATION_ENGINE_AUTHORITY.get(
            key,
            False,
        ) is False
        for key in forbidden
    )


# ============================================================
# HEALTH CONTRACT
# ============================================================

@dataclass
class AccumulationEngineHealth:
    engine: str = ACCUMULATION_ENGINE
    version: str = ACCUMULATION_ENGINE_VERSION

    operational: bool = False
    authority_valid: bool = False

    input_normalization_ready: bool = False
    multitimeframe_ready: bool = False
    formula_registry_ready: bool = False

    validated_formula_available: bool = False

    research_formula_required: bool = True

    research_formula_generated_here: bool = False

    accumulation_intelligence_generated: bool = False
    opportunity_generated_here: bool = False
    decision_generated_here: bool = False

    d13_modified_here: bool = False

    risk_generated_here: bool = False
    risk_override_here: bool = False

    cas_generated_here: bool = False
    cas_bypass_here: bool = False

    execution_here: bool = False

    warnings: List[str] = field(
        default_factory=list
    )

    errors: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def build_accumulation_engine_health(
    formula_id: str = "",
    formula_version: str = "",
) -> AccumulationEngineHealth:

    authority_valid = (
        validate_accumulation_engine_integrity()
    )

    registry_ready = (
        get_accumulation_formula_registry()
        is not None
    )

    formula_state = accumulation_formula_readiness(
        formula_id=formula_id,
        formula_version=formula_version,
        require_validated=True,
    )

    warnings: List[str] = []
    errors: List[str] = []

    if not formula_state["available"]:
        warnings.append(
            formula_state["reason"]
        )

    if not authority_valid:
        errors.append(
            "Accumulation engine authority validation failed."
        )

    operational = (
        authority_valid
        and registry_ready
    )

    return AccumulationEngineHealth(
        operational=operational,
        authority_valid=authority_valid,
        input_normalization_ready=True,
        multitimeframe_ready=True,
        formula_registry_ready=registry_ready,
        validated_formula_available=bool(
            formula_state["available"]
        ),
        research_formula_required=True,
        research_formula_generated_here=False,
        accumulation_intelligence_generated=False,
        opportunity_generated_here=False,
        decision_generated_here=False,
        d13_modified_here=False,
        risk_generated_here=False,
        risk_override_here=False,
        cas_generated_here=False,
        cas_bypass_here=False,
        execution_here=False,
        warnings=warnings,
        errors=errors,
        metadata={
            "engine": ACCUMULATION_ENGINE,
            "formula_id": formula_state[
                "formula_id"
            ],
            "formula_version": formula_state[
                "formula_version"
            ],
            "formula_pluggable": True,
            "upstream_formula_authority": (
                "UPSTREAM_ACCUMULATION_INTELLIGENCE"
            ),
        },
    )


def serialize_accumulation_engine_health(
    value: AccumulationEngineHealth,
) -> Dict[str, Any]:
    return _serialize_accumulation_value(value)


# ============================================================
# OPERATIONAL CHECK
# ============================================================

def accumulation_engine_operational_check(
    formula_id: str = "",
    formula_version: str = "",
) -> Dict[str, Any]:

    health = build_accumulation_engine_health(
        formula_id=formula_id,
        formula_version=formula_version,
    )

    return {
        "engine": ACCUMULATION_ENGINE,
        "version": ACCUMULATION_ENGINE_VERSION,

        "operational": health.operational,
        "authority_valid": health.authority_valid,

        "input_normalization_ready": (
            health.input_normalization_ready
        ),

        "multitimeframe_ready": (
            health.multitimeframe_ready
        ),

        "formula_registry_ready": (
            health.formula_registry_ready
        ),

        "validated_formula_available": (
            health.validated_formula_available
        ),

        "research_formula_required": True,

        "research_formula_generated_here": False,

        "accumulation_intelligence_generated_here": (
            health.accumulation_intelligence_generated
        ),

        "opportunity_generated_here": False,
        "decision_generated_here": False,
        "d13_modified_here": False,
        "risk_override_here": False,
        "cas_bypass_here": False,
        "execution_here": False,

        "warnings": health.warnings,
        "errors": health.errors,
    }


# ============================================================
# DIAGNOSTICS
# ============================================================

def diagnose_accumulation_engine(
    formula_id: str = "",
    formula_version: str = "",
) -> Dict[str, Any]:

    health = build_accumulation_engine_health(
        formula_id=formula_id,
        formula_version=formula_version,
    )

    registry = (
        get_accumulation_formula_registry()
    )

    return {
        "engine": ACCUMULATION_ENGINE,
        "version": ACCUMULATION_ENGINE_VERSION,

        "operational": health.operational,
        "authority_valid": health.authority_valid,

        "formula_registry_count": len(
            registry
        ),

        "formula_id": formula_id,
        "formula_version": formula_version,

        "validated_formula_available": (
            health.validated_formula_available
        ),

        "research_formula_required": True,

        "research_formula_generated_here": False,

        "intelligence_generation_allowed": True,
        "opportunity_generation_allowed": False,
        "decision_generation_allowed": False,

        "d13_modification_allowed": False,
        "risk_override_allowed": False,
        "cas_bypass_allowed": False,
        "execution_allowed": False,

        "warnings": health.warnings,
        "errors": health.errors,
    }


# ============================================================
# PART 4 SELF CHECK
# ============================================================

def accumulation_engine_part4_self_check() -> Dict[str, Any]:

    sample = AccumulationInput(
        instrument_id="SELF_CHECK",
        symbol="TEST",
        asset_class="EQUITY",
        market_id="TEST_MARKET",
        exchange="TEST_EXCHANGE",
        timeframe=Timeframe.D1,
        timestamps=[
            "2026-01-01",
            "2026-01-02",
            "2026-01-03",
        ],
        opens=[
            100.0,
            101.0,
            100.5,
        ],
        highs=[
            102.0,
            103.0,
            102.5,
        ],
        lows=[
            99.0,
            100.0,
            99.5,
        ],
        closes=[
            101.0,
            102.0,
            101.5,
        ],
        volumes=[
            1000.0,
            1200.0,
            1100.0,
        ],
        source="SELF_CHECK",
    )

    input_valid = validate_accumulation_input(
        sample
    )

    window = build_accumulation_window(
        sample
    )

    window_valid = validate_accumulation_window(
        window
    )

    authority_valid = (
        validate_accumulation_engine_integrity()
    )

    part2_valid = validate_accumulation_part2()
    part3_valid = validate_accumulation_part3()

    return {
        "engine": ACCUMULATION_ENGINE,
        "input_valid": input_valid,
        "window_valid": window_valid,
        "authority_valid": authority_valid,
        "part2_valid": part2_valid,
        "part3_valid": part3_valid,

        "formula_registry_count": len(
            get_accumulation_formula_registry()
        ),

        "research_formula_generated_here": False,
        "guessed_formula": False,
        "default_formula": False,
        "upstream_mutation": False,

        "passed": all([
            input_valid,
            window_valid,
            authority_valid,
            part2_valid,
            part3_valid,
        ]),
    }


# ============================================================
# EXPORTS — PART 4
# ============================================================

__all__.extend([
    # Serialization
    "serialize_accumulation_input",
    "serialize_accumulation_measurement",
    "serialize_accumulation_window",
    "serialize_accumulation_analysis",
    "serialize_multitimeframe_accumulation",
    "serialize_accumulation_result",
    "serialize_accumulation_request",
    "serialize_accumulation_snapshot",
    "serialize_accumulation_formula_descriptor",

    # Validators
    "validate_accumulation_measurement",
    "validate_accumulation_window",
    "validate_accumulation_analysis",
    "validate_multitimeframe_accumulation",
    "validate_accumulation_result",
    "validate_accumulation_formula_descriptor",
    "validate_accumulation_engine_integrity",

    # Health
    "AccumulationEngineHealth",
    "build_accumulation_engine_health",
    "serialize_accumulation_engine_health",
    "accumulation_engine_operational_check",

    # Diagnostics
    "diagnose_accumulation_engine",
    "accumulation_engine_part4_self_check",
])
# ============================================================
# ROBOMLM_PLUS
# Accumulation Intelligence Engine
# Part 5 / 5 — FINAL
# ============================================================


# ============================================================
# REQUEST FACTORY
# ============================================================

def create_accumulation_request(
    input_data: Optional[Any] = None,
    multi_timeframe_input: Optional[Any] = None,
    requested_timeframes: Optional[List[Any]] = None,
    formula_id: str = "",
    formula_version: str = "",
    require_validated_formula: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
) -> AccumulationEngineRequest:

    normalized_input = None

    if input_data is not None:
        normalized_input = normalize_accumulation_input(
            input_data
        )

    normalized_mtf = None

    if multi_timeframe_input is not None:
        normalized_mtf = (
            normalize_multitimeframe_accumulation_input(
                multi_timeframe_input
            )
        )

    return AccumulationEngineRequest(
        input_data=normalized_input,
        multi_timeframe_input=normalized_mtf,
        requested_timeframes=(
            normalize_requested_timeframes(
                requested_timeframes
            )
        ),
        formula_id=_accumulation_text(
            formula_id
        ),
        formula_version=_accumulation_text(
            formula_version
        ),
        require_validated_formula=bool(
            require_validated_formula
        ),
        metadata=dict(metadata or {}),
    )


# ============================================================
# SAFE EXECUTION WRAPPER
# ============================================================

def execute_accumulation_request(
    request: AccumulationEngineRequest,
) -> AccumulationEngineResult:

    try:
        return run_accumulation_engine(
            request
        )

    except Exception as exc:
        return AccumulationEngineResult(
            status=AccumulationStatus.INVALID,
            errors=[
                f"Accumulation engine execution failed: {exc}"
            ],
            metadata={
                "engine_exception": True,
                "intelligence_generated": False,
                "research_formula_generated": False,
            },
        )


# ============================================================
# RESULT STATE HELPERS
# ============================================================

def accumulation_result_is_ready(
    result: Optional[
        AccumulationEngineResult
    ],
) -> bool:

    if not isinstance(
        result,
        AccumulationEngineResult,
    ):
        return False

    return (
        result.status
        == AccumulationStatus.READY
    )


def accumulation_result_has_validated_research(
    result: Optional[
        AccumulationEngineResult
    ],
) -> bool:

    if not isinstance(
        result,
        AccumulationEngineResult,
    ):
        return False

    if result.research_formula_validated:
        return True

    if result.analysis is not None:
        return bool(
            result.analysis.research_validated
        )

    if result.multi_timeframe is not None:
        return bool(
            result.multi_timeframe.research_validated
        )

    return False


def accumulation_result_has_errors(
    result: Optional[
        AccumulationEngineResult
    ],
) -> bool:

    if not isinstance(
        result,
        AccumulationEngineResult,
    ):
        return True

    return bool(result.errors)


def accumulation_result_has_warnings(
    result: Optional[
        AccumulationEngineResult
    ],
) -> bool:

    if not isinstance(
        result,
        AccumulationEngineResult,
    ):
        return True

    return bool(result.warnings)


# ============================================================
# ANALYSIS SUMMARY
# ============================================================

def summarize_accumulation_analysis(
    analysis: Optional[
        AccumulationAnalysis
    ],
) -> Dict[str, Any]:

    if analysis is None:
        return {
            "available": False,
            "state": AccumulationState.UNKNOWN.value,
            "direction": (
                AccumulationDirection.UNKNOWN.value
            ),
        }

    return {
        "available": True,
        "instrument_id": analysis.instrument_id,
        "symbol": analysis.symbol,
        "timeframe": analysis.timeframe.value,
        "status": analysis.status.value,
        "state": analysis.state.value,
        "direction": analysis.direction.value,
        "phase": analysis.phase.value,
        "strength": analysis.strength.value,
        "confidence_class": (
            analysis.confidence_class.value
        ),
        "confidence": analysis.confidence,
        "formula_id": analysis.formula_id,
        "formula_version": analysis.formula_version,
        "research_validated": (
            analysis.research_validated
        ),
        "measurement_count": len(
            analysis.measurements
        ),
        "upstream_research_formula": (
            analysis.metadata.get(
                "upstream_research_formula",
                False,
            )
        ),
        "engine_generated_formula": (
            analysis.metadata.get(
                "engine_generated_formula",
                False,
            )
        ),
    }


# ============================================================
# MULTI-TIMEFRAME SUMMARY
# ============================================================

def summarize_multitimeframe_accumulation(
    value: Optional[
        MultiTimeframeAccumulation
    ],
) -> Dict[str, Any]:

    if value is None:
        return {
            "available": False,
            "relation": (
                AccumulationRelation.UNKNOWN.value
            ),
        }

    return {
        "available": True,
        "instrument_id": value.instrument_id,
        "symbol": value.symbol,
        "primary_timeframe": (
            value.primary_timeframe.value
        ),
        "timeframe_count": len(
            value.timeframe_analyses
        ),
        "dominant_state": (
            value.dominant_state.value
        ),
        "dominant_direction": (
            value.dominant_direction.value
        ),
        "relation": value.relation.value,
        "confidence": value.confidence,
        "research_validated": (
            value.research_validated
        ),
        "timeframes": [
            item.timeframe.value
            for item in value.timeframe_analyses
        ],
    }


# ============================================================
# RESULT SUMMARY
# ============================================================

def accumulation_result_summary(
    result: Optional[
        AccumulationEngineResult
    ],
) -> Dict[str, Any]:

    if not isinstance(
        result,
        AccumulationEngineResult,
    ):
        return {
            "valid": False,
            "status": AccumulationStatus.INVALID.value,
        }

    return {
        "valid": True,
        "engine": ACCUMULATION_ENGINE,
        "version": ACCUMULATION_ENGINE_VERSION,
        "status": result.status.value,

        "analysis": summarize_accumulation_analysis(
            result.analysis
        ),

        "multi_timeframe": (
            summarize_multitimeframe_accumulation(
                result.multi_timeframe
            )
        ),

        "formula_id": result.formula_id,
        "formula_version": result.formula_version,

        "research_formula_available": (
            result.research_formula_available
        ),

        "research_formula_validated": (
            result.research_formula_validated
        ),

        "validated_research": (
            accumulation_result_has_validated_research(
                result
            )
        ),

        "warnings": list(result.warnings),
        "errors": list(result.errors),

        "upstream_truth_preserved": (
            result.metadata.get(
                "upstream_truth_preserved",
                False,
            )
        ),

        "engine_generated_formula": (
            result.metadata.get(
                "engine_generated_formula",
                False,
            )
        ),

        "intelligence_generated": (
            result.metadata.get(
                "intelligence_generated",
                False,
            )
        ),

        "opportunity_generated": False,
        "decision_generated": False,
        "d13_modified": False,
        "risk_override": False,
        "cas_bypass": False,
        "execution": False,
    }


# ============================================================
# FORMULA REGISTRY SUMMARY
# ============================================================

def accumulation_formula_registry_summary(
) -> Dict[str, Any]:

    registry = (
        get_accumulation_formula_registry()
    )

    descriptors = registry.descriptors()

    return {
        "registry_available": registry is not None,
        "formula_count": len(registry),

        "validated_formula_count": sum(
            1
            for item in descriptors
            if item.validated
        ),

        "enabled_formula_count": sum(
            1
            for item in descriptors
            if item.enabled
        ),

        "formulas": [
            {
                "formula_id": item.formula_id,
                "formula_version": item.formula_version,
                "name": item.name,
                "validated": item.validated,
                "enabled": item.enabled,
                "owner": item.owner,
                "supported_asset_classes": list(
                    item.supported_asset_classes
                ),
                "supported_timeframes": [
                    timeframe.value
                    for timeframe
                    in item.supported_timeframes
                ],
            }
            for item in descriptors
        ],
    }


# ============================================================
# CONTRACT INTEGRITY
# ============================================================

def validate_accumulation_contract_integrity(
) -> bool:

    if not validate_accumulation_engine_integrity():
        return False

    required_contract_keys = [
        "layer",
        "role",
        "mission",
        "inputs",
        "outputs",
        "authority_owner",
        "formula_policy",
        "downstream_consumers",
        "forbidden_authority",
    ]

    if not all(
        key in ACCUMULATION_ENGINE_CONTRACT
        for key in required_contract_keys
    ):
        return False

    formula_policy = (
        ACCUMULATION_ENGINE_CONTRACT[
            "formula_policy"
        ]
    )

    if not formula_policy.get(
        "formula_pluggable",
        False,
    ):
        return False

    if formula_policy.get(
        "default_formula",
        True,
    ):
        return False

    if formula_policy.get(
        "guessed_formula",
        True,
    ):
        return False

    if formula_policy.get(
        "silent_substitution",
        True,
    ):
        return False

    if (
        ACCUMULATION_ENGINE_CONTRACT[
            "authority_owner"
        ]
        != "UPSTREAM_ACCUMULATION_INTELLIGENCE"
    ):
        return False

    return True


# ============================================================
# CONTRACT MANIFEST
# ============================================================

def accumulation_engine_contract_manifest(
) -> Dict[str, Any]:

    return {
        "engine": ACCUMULATION_ENGINE,
        "version": ACCUMULATION_ENGINE_VERSION,

        "layer": "INTELLIGENCE_ENGINE",
        "role": "ACCUMULATION_INTELLIGENCE",

        "importance": "CLASS_A_INTELLIGENCE_COMPONENT",

        "mission": (
            "Identify validated accumulation characteristics "
            "from normalized market observations without "
            "inventing research formulas."
        ),

        "pipeline": [
            "RAW_MARKET_DATA",
            "NORMALIZED_MARKET_DATA",
            "STRUCTURE_INTELLIGENCE",
            "ACCUMULATION_INPUT",
            "VALIDATED_ACCUMULATION_FORMULA",
            "ACCUMULATION_ANALYSIS",
            "MULTI_TIMEFRAME_ACCUMULATION",
            "BOUNDARY_INTELLIGENCE",
            "BREAKOUT_INTELLIGENCE",
            "OPPORTUNITY_INTELLIGENCE",
            "EQUITY_SCANNER",
            "FUTURE_SCANNER",
        ],

        "supported_timeframes": [
            "5m",
            "15m",
            "1h",
            "4h",
            "1d",
            "1w",
            "1mo",
        ],

        "formula_policy": {
            "formula_pluggable": True,
            "registry_based": True,
            "validated_formula_required": True,
            "formula_version_traceability": True,
            "no_default_formula": True,
            "no_guessed_formula": True,
            "no_silent_substitution": True,
        },

        "authority": {
            "accumulation_analysis": True,
            "structure_context_consumption": True,
            "multi_timeframe_analysis": True,

            "distribution_generation": False,
            "breakout_generation": False,
            "confirmation_generation": False,
            "opportunity_generation": False,
            "scanner_generation": False,
            "decision_generation": False,
            "d13_generation": False,
            "d13_modification": False,
            "risk_generation": False,
            "risk_override": False,
            "cas_generation": False,
            "cas_bypass": False,
            "execution": False,
            "upstream_mutation": False,
        },

        "truth_policy": {
            "math_first": True,
            "research_first": True,
            "formula_traceability_required": True,
            "upstream_truth_preserved": True,
            "accumulation_is_not_breakout": True,
            "accumulation_is_not_signal": True,
            "accumulation_is_not_decision": True,
            "pattern_layer_is_secondary": True,
            "pattern_layer_cannot_override_math": True,
        },

        "downstream": [
            "BOUNDARY_ENGINE",
            "BREAKOUT_ENGINE",
            "CONFIRMATION_ENGINE",
            "RELATIONSHIP_ENGINE",
            "OPPORTUNITY_ENGINE",
            "EQUITY_SCANNER",
            "FUTURE_SCANNER",
        ],

        "research_hooks": [
            "ACCUMULATION_STRUCTURE_FORMULA",
            "ACCUMULATION_VOLUME_FORMULA",
            "ACCUMULATION_PRICE_BEHAVIOR_FORMULA",
            "ACCUMULATION_RANGE_BEHAVIOR_FORMULA",
            "ACCUMULATION_PARTICIPATION_FORMULA",
            "ACCUMULATION_QUALITY_FORMULA",
            "ACCUMULATION_INVALIDATION_FORMULA",
            "MULTI_TIMEFRAME_ACCUMULATION_FORMULA",
        ],

        "formula_authority": (
            "UPSTREAM_ACCUMULATION_INTELLIGENCE"
        ),

        "formula_pluggable": True,
    }


# ============================================================
# MODULE INTEGRITY
# ============================================================

def validate_accumulation_module_integrity(
) -> bool:

    if not validate_accumulation_contract_integrity():
        return False

    if not validate_accumulation_part2():
        return False

    if not validate_accumulation_part3():
        return False

    return True


# ============================================================
# MODULE CHECK
# ============================================================

def accumulation_engine_module_check(
) -> Dict[str, Any]:

    integrity = (
        validate_accumulation_module_integrity()
    )

    health = build_accumulation_engine_health()

    return {
        "engine": ACCUMULATION_ENGINE,
        "version": ACCUMULATION_ENGINE_VERSION,

        "integrity_valid": integrity,
        "authority_valid": (
            health.authority_valid
        ),

        "normalization_ready": (
            health.input_normalization_ready
        ),

        "multitimeframe_ready": (
            health.multitimeframe_ready
        ),

        "formula_registry_ready": (
            health.formula_registry_ready
        ),

        "validated_formula_available": (
            health.validated_formula_available
        ),

        "research_formula_generated_here": False,

        "opportunity_generated_here": False,
        "decision_generated_here": False,
        "d13_modified_here": False,
        "risk_override_here": False,
        "cas_bypass_here": False,
        "execution_here": False,

        "passed": (
            integrity
            and health.authority_valid
        ),
    }


# ============================================================
# COMPLETE SELF CHECK
# ============================================================

def accumulation_engine_self_check(
) -> Dict[str, Any]:

    part4 = (
        accumulation_engine_part4_self_check()
    )

    module = (
        accumulation_engine_module_check()
    )

    sample_request = create_accumulation_request(
        input_data=AccumulationInput(
            instrument_id="SELF_CHECK",
            symbol="TEST",
            asset_class="EQUITY",
            market_id="TEST_MARKET",
            exchange="TEST_EXCHANGE",
            timeframe=Timeframe.D1,
            timestamps=[
                "2026-01-01",
                "2026-01-02",
                "2026-01-03",
            ],
            opens=[
                100.0,
                101.0,
                100.5,
            ],
            highs=[
                102.0,
                103.0,
                102.5,
            ],
            lows=[
                99.0,
                100.0,
                99.5,
            ],
            closes=[
                101.0,
                102.0,
                101.5,
            ],
            volumes=[
                1000.0,
                1200.0,
                1100.0,
            ],
            source="SELF_CHECK",
        ),
        formula_id="",
        formula_version="",
        require_validated_formula=True,
    )

    result = execute_accumulation_request(
        sample_request
    )

    # With no registered formula, the engine MUST NOT
    # fabricate accumulation intelligence.
    no_fabrication = (
        result.analysis is None
        and result.multi_timeframe is None
        and not result.metadata.get(
            "intelligence_generated",
            False,
        )
    )

    contract_valid = (
        validate_accumulation_contract_integrity()
    )

    passed = all([
        part4.get("passed", False),
        module.get("passed", False),
        contract_valid,
        no_fabrication,
    ])

    return {
        "engine": ACCUMULATION_ENGINE,
        "version": ACCUMULATION_ENGINE_VERSION,

        "part4_passed": part4.get(
            "passed",
            False,
        ),

        "module_passed": module.get(
            "passed",
            False,
        ),

        "contract_valid": contract_valid,

        "formula_registry_count": len(
            get_accumulation_formula_registry()
        ),

        "validated_formula_available": (
            False
            if len(
                get_accumulation_formula_registry()
            ) == 0
            else None
        ),

        "no_fabricated_intelligence": (
            no_fabrication
        ),

        "research_formula_generated_here": False,
        "guessed_formula": False,
        "default_formula": False,
        "silent_formula_substitution": False,

        "opportunity_generated": False,
        "decision_generated": False,
        "d13_modified": False,
        "risk_override": False,
        "cas_bypass": False,
        "execution": False,
        "upstream_mutation": False,

        "passed": passed,
    }


# ============================================================
# DEFAULT REQUEST
# ============================================================

def create_default_accumulation_engine_request(
) -> AccumulationEngineRequest:

    return create_accumulation_request(
        input_data=None,
        multi_timeframe_input=None,
        requested_timeframes=[
            Timeframe.M5,
            Timeframe.M15,
            Timeframe.H1,
            Timeframe.H4,
            Timeframe.D1,
            Timeframe.W1,
            Timeframe.MN1,
        ],
        formula_id="",
        formula_version="",
        require_validated_formula=True,
        metadata={
            "default_request": True,
            "research_formula_required": True,
            "formula_pluggable": True,
            "no_default_formula": True,
            "no_guessed_formula": True,
        },
    )


# ============================================================
# CONVENIENCE HELPERS
# ============================================================

def analyze_single_timeframe_accumulation(
    input_data: Any,
    formula_id: str,
    formula_version: str = "",
    require_validated_formula: bool = True,
) -> AccumulationEngineResult:

    request = create_accumulation_request(
        input_data=input_data,
        formula_id=formula_id,
        formula_version=formula_version,
        require_validated_formula=(
            require_validated_formula
        ),
    )

    return execute_accumulation_request(
        request
    )


def analyze_accumulation_timeframes(
    inputs: List[Any],
    formula_id: str = "",
    formula_version: str = "",
    require_validated_formula: bool = True,
    formula_map: Optional[
        Dict[str, str]
    ] = None,
    formula_version_map: Optional[
        Dict[str, str]
    ] = None,
    primary_timeframe: Any = Timeframe.UNKNOWN,
) -> AccumulationEngineResult:

    mtf_input = (
        build_multitimeframe_accumulation_input(
            inputs=inputs,
            primary_timeframe=primary_timeframe,
        )
    )

    request = create_accumulation_request(
        multi_timeframe_input=mtf_input,
        formula_id=formula_id,
        formula_version=formula_version,
        require_validated_formula=(
            require_validated_formula
        ),
        metadata={
            "formula_map": dict(
                formula_map or {}
            ),
            "formula_version_map": dict(
                formula_version_map or {}
            ),
        },
    )

    return execute_accumulation_request(
        request
    )


# ============================================================
# FINAL MANIFEST
# ============================================================

ACCUMULATION_ENGINE_FINAL_MANIFEST: Dict[str, Any] = {
    "engine": ACCUMULATION_ENGINE,
    "version": ACCUMULATION_ENGINE_VERSION,

    "layer": "INTELLIGENCE_ENGINE",
    "role": "ACCUMULATION_INTELLIGENCE",

    "mission": (
        "Provide mathematically and research validated "
        "accumulation intelligence as an upstream component "
        "for boundary, breakout and opportunity reasoning."
    ),

    "architecture": [
        "NORMALIZED_MARKET_DATA",
        "STRUCTURE_INTELLIGENCE",
        "ACCUMULATION_INPUT",
        "VALIDATED_RESEARCH_FORMULA",
        "ACCUMULATION_ANALYSIS",
        "MULTI_TIMEFRAME_ACCUMULATION",
        "BOUNDARY_ENGINE",
        "BREAKOUT_ENGINE",
        "CONFIRMATION_ENGINE",
        "OPPORTUNITY_ENGINE",
        "EQUITY_SCANNER",
        "FUTURE_SCANNER",
    ],

    "formula_policy": {
        "formula_pluggable": True,
        "registry_based": True,
        "validated_formula_required": True,
        "formula_id_traceability": True,
        "formula_version_traceability": True,
        "no_formula_guessing": True,
        "no_default_formula": True,
        "no_silent_substitution": True,
    },

    "timeframes": [
        "5m",
        "15m",
        "1h",
        "4h",
        "1d",
        "1w",
        "1mo",
    ],

    "authority_owner": (
        "UPSTREAM_ACCUMULATION_INTELLIGENCE"
    ),

    "truth_policy": {
        "math_first": True,
        "research_first": True,
        "structure_context_is_input": True,
        "accumulation_is_not_breakout": True,
        "accumulation_is_not_signal": True,
        "accumulation_is_not_decision": True,
        "pattern_is_secondary_validation": True,
        "pattern_cannot_override_math": True,
        "upstream_truth_preserved": True,
    },

    "future_research": {
        "structure_interaction": True,
        "price_behavior": True,
        "volume_behavior": True,
        "range_behavior": True,
        "participation": True,
        "quality": True,
        "invalidation": True,
        "multi_timeframe": True,
    },

    "downstream_consumers": [
        "BOUNDARY_ENGINE",
        "BREAKOUT_ENGINE",
        "CONFIRMATION_ENGINE",
        "RELATIONSHIP_ENGINE",
        "OPPORTUNITY_ENGINE",
        "EQUITY_SCANNER",
        "FUTURE_SCANNER",
    ],

    "forbidden": [
        "DISTRIBUTION_GENERATION",
        "BREAKOUT_GENERATION",
        "CONFIRMATION_GENERATION",
        "OPPORTUNITY_GENERATION",
        "SCANNER_GENERATION",
        "DECISION_GENERATION",
        "D13_GENERATION",
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


# ============================================================
# FINAL EXPORTS
# ============================================================

__all__.extend([
    # Request / execution
    "create_accumulation_request",
    "execute_accumulation_request",

    # Result helpers
    "accumulation_result_is_ready",
    "accumulation_result_has_validated_research",
    "accumulation_result_has_errors",
    "accumulation_result_has_warnings",

    # Summaries
    "summarize_accumulation_analysis",
    "summarize_multitimeframe_accumulation",
    "accumulation_result_summary",
    "accumulation_formula_registry_summary",

    # Contract / integrity
    "validate_accumulation_contract_integrity",
    "accumulation_engine_contract_manifest",
    "validate_accumulation_module_integrity",

    # Module / self checks
    "accumulation_engine_module_check",
    "accumulation_engine_self_check",

    # Defaults / convenience
    "create_default_accumulation_engine_request",
    "analyze_single_timeframe_accumulation",
    "analyze_accumulation_timeframes",

    # Final manifest
    "ACCUMULATION_ENGINE_FINAL_MANIFEST",
])