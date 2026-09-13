from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


# ============================================================
# ROBOMLM_PLUS — STRUCTURE INTELLIGENCE ENGINE
# Part 1 — Core Contracts / Domain Primitives
# ============================================================

STRUCTURE_ENGINE = "ROBOMLM_PLUS_STRUCTURE_ENGINE"
STRUCTURE_ENGINE_VERSION = "1.0"
STRUCTURE_ENGINE_NAME = "Structure Intelligence Engine"

STRUCTURE_ENGINE_DESCRIPTION = (
    "Core market-structure intelligence engine for identifying and "
    "normalizing price structure across multiple assets and timeframes. "
    "Research formulas remain pluggable and are owned by the upstream "
    "structure-intelligence layer."
)


# ============================================================
# AUTHORITY
# ============================================================

STRUCTURE_ENGINE_AUTHORITY = {
    "structure_analysis": True,
    "structure_normalization": True,
    "multi_timeframe_structure": True,
    "swing_structure": True,
    "high_low_structure": True,
    "trend_structure": True,
    "range_structure": True,
    "structure_state_classification": True,
    "research_formula_consumption": True,
    "research_formula_generation": False,
    "fixed_formula_assumption": False,
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
    "order_authority": False,
    "order_mutation": False,
    "position_authority": False,
    "position_mutation": False,
    "upstream_mutation": False,
}


# ============================================================
# ENUMS
# ============================================================

class StructureStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    READY = "READY"
    DEGRADED = "DEGRADED"
    INVALID = "INVALID"


class StructureDirection(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"


class StructureType(str, Enum):
    TRENDING = "TRENDING"
    RANGING = "RANGING"
    TRANSITION = "TRANSITION"
    EXPANSION = "EXPANSION"
    CONTRACTION = "CONTRACTION"
    UNKNOWN = "UNKNOWN"


class StructurePhase(str, Enum):
    EARLY = "EARLY"
    DEVELOPING = "DEVELOPING"
    MATURE = "MATURE"
    TRANSITION = "TRANSITION"
    UNKNOWN = "UNKNOWN"


class SwingType(str, Enum):
    HIGH = "HIGH"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class Timeframe(str, Enum):
    M5 = "5M"
    M15 = "15M"
    H1 = "1H"
    H4 = "4H"
    D1 = "1D"
    W1 = "1W"
    MN1 = "1MN"
    UNKNOWN = "UNKNOWN"


class StructureRelation(str, Enum):
    ALIGNED = "ALIGNED"
    DIVERGENT = "DIVERGENT"
    CONFLICTING = "CONFLICTING"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"


class StructureConfidence(str, Enum):
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"
    UNKNOWN = "UNKNOWN"


# ============================================================
# HELPERS
# ============================================================

def _structure_text(value: Any, default: str = "") -> str:
    if value is None:
        return default

    text = str(value).strip()
    return text if text else default


def _structure_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        value = value.strip().lower()

        if value in {"true", "1", "yes", "y", "on"}:
            return True

        if value in {"false", "0", "no", "n", "off"}:
            return False

    return bool(value)


def _structure_float(
    value: Any,
    default: Optional[float] = None,
) -> Optional[float]:
    if value is None:
        return default

    try:
        result = float(value)

        if result != result:
            return default

        return result
    except (TypeError, ValueError):
        return default


def _structure_int(
    value: Any,
    default: int = 0,
) -> int:
    if value is None:
        return default

    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _structure_enum(
    enum_type: Any,
    value: Any,
    default: Any,
) -> Any:
    if isinstance(value, enum_type):
        return value

    try:
        return enum_type(str(value).strip().upper())
    except (ValueError, TypeError):
        return default


def _structure_now() -> datetime:
    return datetime.now(timezone.utc)


# ============================================================
# PRICE / SWING PRIMITIVES
# ============================================================

@dataclass
class StructurePoint:
    """
    Normalized structural price point.

    This is a mathematical/data primitive only.
    It does not decide whether the point is a trade opportunity.
    """

    timestamp: Optional[datetime] = None
    price: Optional[float] = None
    swing_type: SwingType = SwingType.UNKNOWN
    timeframe: Timeframe = Timeframe.UNKNOWN
    sequence: int = 0
    confirmed: bool = False
    strength: Optional[float] = None
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StructureLeg:
    """
    Price movement between two structural points.
    """

    start: Optional[StructurePoint] = None
    end: Optional[StructurePoint] = None

    direction: StructureDirection = StructureDirection.UNKNOWN

    price_change: Optional[float] = None
    price_change_pct: Optional[float] = None

    duration_bars: int = 0

    confirmed: bool = False

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StructureWindow:
    """
    Normalized observation window used by structure analysis.
    """

    instrument_id: str = ""
    symbol: str = ""

    timeframe: Timeframe = Timeframe.UNKNOWN

    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    bars_count: int = 0

    high: Optional[float] = None
    low: Optional[float] = None

    first_price: Optional[float] = None
    last_price: Optional[float] = None

    source: str = ""

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# STRUCTURE INPUT
# ============================================================

@dataclass
class StructureInput:
    """
    Input contract for structure analysis.

    Raw market data remains upstream.
    This contract accepts already available normalized observations.
    """

    instrument_id: str = ""
    symbol: str = ""

    asset_class: str = ""
    market_id: str = ""
    exchange: str = ""

    timeframe: Timeframe = Timeframe.UNKNOWN

    timestamps: List[datetime] = field(default_factory=list)
    opens: List[float] = field(default_factory=list)
    highs: List[float] = field(default_factory=list)
    lows: List[float] = field(default_factory=list)
    closes: List[float] = field(default_factory=list)
    volumes: List[float] = field(default_factory=list)

    source: str = ""

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MultiTimeframeStructureInput:
    """
    Multi-timeframe structure input.

    Designed from the beginning for:
        5M / 15M / 1H
        4H / 1D / 1W / 1MN
    """

    instrument_id: str = ""
    symbol: str = ""

    structures: Dict[str, StructureInput] = field(
        default_factory=dict
    )

    primary_timeframe: Timeframe = Timeframe.UNKNOWN

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# STRUCTURE OUTPUT
# ============================================================

@dataclass
class StructureAnalysis:
    """
    Upstream structural intelligence output.

    IMPORTANT:
    This contract intentionally does not contain a fabricated
    trading score or fixed research formula.
    """

    instrument_id: str = ""
    symbol: str = ""

    timeframe: Timeframe = Timeframe.UNKNOWN

    status: StructureStatus = StructureStatus.UNKNOWN

    direction: StructureDirection = StructureDirection.UNKNOWN
    structure_type: StructureType = StructureType.UNKNOWN
    phase: StructurePhase = StructurePhase.UNKNOWN

    swing_highs: List[StructurePoint] = field(
        default_factory=list
    )
    swing_lows: List[StructurePoint] = field(
        default_factory=list
    )

    legs: List[StructureLeg] = field(
        default_factory=list
    )

    structure_window: Optional[StructureWindow] = None

    confidence: Optional[float] = None
    confidence_class: StructureConfidence = (
        StructureConfidence.UNKNOWN
    )

    formula_id: str = ""
    formula_version: str = ""

    research_validated: bool = False

    generated_at: datetime = field(
        default_factory=_structure_now
    )

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# MULTI-TIMEFRAME OUTPUT
# ============================================================

@dataclass
class MultiTimeframeStructure:
    """
    Aggregated structural state across timeframes.

    This does not make a trade decision.
    It only preserves structural observations and their relations.
    """

    instrument_id: str = ""
    symbol: str = ""

    timeframe_structures: Dict[
        str,
        StructureAnalysis,
    ] = field(default_factory=dict)

    primary_timeframe: Timeframe = Timeframe.UNKNOWN

    dominant_direction: StructureDirection = (
        StructureDirection.UNKNOWN
    )

    relation: StructureRelation = StructureRelation.UNKNOWN

    confidence: Optional[float] = None

    research_validated: bool = False

    generated_at: datetime = field(
        default_factory=_structure_now
    )

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# ENGINE RESULT
# ============================================================

@dataclass
class StructureEngineResult:
    """
    Engine-level result contract.

    The result is structural intelligence only.
    Opportunity generation belongs to Opportunity Engine.
    """

    status: StructureStatus = StructureStatus.UNKNOWN

    structure: Optional[StructureAnalysis] = None

    multi_timeframe: Optional[MultiTimeframeStructure] = None

    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    formula_id: str = ""
    formula_version: str = ""

    research_formula_available: bool = False
    research_formula_validated: bool = False

    generated_at: datetime = field(
        default_factory=_structure_now
    )

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# ENGINE REQUEST
# ============================================================

@dataclass
class StructureEngineRequest:
    """
    Execution request for structure analysis.

    Formula selection is explicit and pluggable.
    The engine must never silently invent a formula.
    """

    input_data: Optional[StructureInput] = None

    multi_timeframe_input: Optional[
        MultiTimeframeStructureInput
    ] = None

    requested_timeframes: List[Timeframe] = field(
        default_factory=lambda: [
            Timeframe.M5,
            Timeframe.M15,
            Timeframe.H1,
            Timeframe.H4,
            Timeframe.D1,
            Timeframe.W1,
            Timeframe.MN1,
        ]
    )

    formula_id: str = ""
    formula_version: str = ""

    require_validated_formula: bool = True

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# ENGINE SNAPSHOT
# ============================================================

@dataclass(frozen=True)
class StructureEngineSnapshot:
    """
    Immutable engine snapshot contract.
    """

    request: StructureEngineRequest
    result: StructureEngineResult

    captured_at: datetime = field(
        default_factory=_structure_now
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# PART-1 CONTRACT MANIFEST
# ============================================================

STRUCTURE_ENGINE_CONTRACT = {
    "engine": STRUCTURE_ENGINE,
    "version": STRUCTURE_ENGINE_VERSION,
    "layer": "INTELLIGENCE_ENGINE",
    "role": "MARKET_STRUCTURE_INTELLIGENCE",

    "inputs": [
        "NORMALIZED_OHLCV_INPUT",
        "MULTI_TIMEFRAME_MARKET_INPUT",
        "FORMULA_REGISTRY_REFERENCE",
        "RESEARCH_VALIDATION_STATE",
    ],

    "outputs": [
        "STRUCTURE_ANALYSIS",
        "MULTI_TIMEFRAME_STRUCTURE",
        "STRUCTURE_ENGINE_RESULT",
        "STRUCTURE_ENGINE_SNAPSHOT",
    ],

    "supported_timeframes": [
        "5M",
        "15M",
        "1H",
        "4H",
        "1D",
        "1W",
        "1MN",
    ],

    "authority_owner": (
        "UPSTREAM_STRUCTURE_INTELLIGENCE"
    ),

    "formula_policy": {
        "formula_pluggable": True,
        "formula_must_be_explicit": True,
        "formula_must_be_research_validated": True,
        "silent_formula_generation": False,
        "fixed_formula_assumption": False,
    },

    "downstream_consumers": [
        "ACCUMULATION_ENGINE",
        "DISTRIBUTION_ENGINE",
        "BOUNDARY_ENGINE",
        "BREAKOUT_ENGINE",
        "CONFIRMATION_ENGINE",
        "RELATIONSHIP_ENGINE",
        "REGIME_ENGINE",
        "OPPORTUNITY_ENGINE",
        "EQUITY_SCANNER",
        "FUTURE_SCANNER",
    ],

    "forbidden_authority": [
        "OPPORTUNITY_GENERATION",
        "DECISION_GENERATION",
        "D13_MODIFICATION",
        "RISK_OVERRIDE",
        "CAS_BYPASS",
        "ORDER_MUTATION",
        "POSITION_MUTATION",
        "EXECUTION",
        "UPSTREAM_MUTATION",
    ],
}


# ============================================================
# AUTHORITY CHECK
# ============================================================

def validate_structure_authority() -> bool:
    """
    Ensures Part-1 engine boundary remains intact.
    """

    required_false = [
        "research_formula_generation",
        "fixed_formula_assumption",
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
        "upstream_mutation",
    ]

    return all(
        STRUCTURE_ENGINE_AUTHORITY.get(flag) is False
        for flag in required_false
    )


# ============================================================
# MODULE SUMMARY
# ============================================================

def structure_engine_summary() -> Dict[str, Any]:
    return {
        "engine": STRUCTURE_ENGINE,
        "version": STRUCTURE_ENGINE_VERSION,
        "name": STRUCTURE_ENGINE_NAME,
        "authority_valid": validate_structure_authority(),
        "formula_pluggable": True,
        "research_formula_required": True,
        "opportunity_generation": False,
        "decision_generation": False,
        "d13_modification": False,
        "risk_override": False,
        "cas_bypass": False,
        "execution": False,
        "supported_timeframes": [
            timeframe.value
            for timeframe in Timeframe
            if timeframe != Timeframe.UNKNOWN
        ],
    }


__all__ = [
    # Constants
    "STRUCTURE_ENGINE",
    "STRUCTURE_ENGINE_VERSION",
    "STRUCTURE_ENGINE_NAME",
    "STRUCTURE_ENGINE_DESCRIPTION",
    "STRUCTURE_ENGINE_AUTHORITY",
    "STRUCTURE_ENGINE_CONTRACT",

    # Enums
    "StructureStatus",
    "StructureDirection",
    "StructureType",
    "StructurePhase",
    "SwingType",
    "Timeframe",
    "StructureRelation",
    "StructureConfidence",

    # Primitives
    "StructurePoint",
    "StructureLeg",
    "StructureWindow",

    # Inputs
    "StructureInput",
    "MultiTimeframeStructureInput",

    # Outputs
    "StructureAnalysis",
    "MultiTimeframeStructure",
    "StructureEngineResult",

    # Request / Snapshot
    "StructureEngineRequest",
    "StructureEngineSnapshot",

    # Validation / Summary
    "validate_structure_authority",
    "structure_engine_summary",
]
# ============================================================
# PART 2 — NORMALIZATION / STRUCTURAL PRIMITIVES
# ============================================================

def _normalize_price_series(
    values: List[Any],
) -> List[float]:
    result: List[float] = []

    for value in values:
        parsed = _structure_float(value)

        if parsed is not None:
            result.append(parsed)

    return result


def _normalize_timestamps(
    values: List[Any],
) -> List[datetime]:
    result: List[datetime] = []

    for value in values:
        if isinstance(value, datetime):
            result.append(value)
            continue

        if isinstance(value, str):
            try:
                parsed = datetime.fromisoformat(
                    value.replace("Z", "+00:00")
                )
                result.append(parsed)
            except ValueError:
                continue

    return result


def normalize_structure_input(
    value: Optional[StructureInput],
) -> StructureInput:
    if value is None:
        return StructureInput()

    timestamps = _normalize_timestamps(value.timestamps)

    opens = _normalize_price_series(value.opens)
    highs = _normalize_price_series(value.highs)
    lows = _normalize_price_series(value.lows)
    closes = _normalize_price_series(value.closes)
    volumes = _normalize_price_series(value.volumes)

    return StructureInput(
        instrument_id=_structure_text(value.instrument_id),
        symbol=_structure_text(value.symbol),
        asset_class=_structure_text(value.asset_class),
        market_id=_structure_text(value.market_id),
        exchange=_structure_text(value.exchange),
        timeframe=_structure_enum(
            Timeframe,
            value.timeframe,
            Timeframe.UNKNOWN,
        ),
        timestamps=timestamps,
        opens=opens,
        highs=highs,
        lows=lows,
        closes=closes,
        volumes=volumes,
        source=_structure_text(value.source),
        metadata=dict(value.metadata or {}),
    )


def normalize_multitimeframe_input(
    value: Optional[MultiTimeframeStructureInput],
) -> MultiTimeframeStructureInput:
    if value is None:
        return MultiTimeframeStructureInput()

    normalized: Dict[str, StructureInput] = {}

    for key, structure_input in (
        value.structures or {}
    ).items():

        normalized_key = _structure_text(key).upper()

        normalized[normalized_key] = (
            normalize_structure_input(structure_input)
        )

    return MultiTimeframeStructureInput(
        instrument_id=_structure_text(value.instrument_id),
        symbol=_structure_text(value.symbol),
        structures=normalized,
        primary_timeframe=_structure_enum(
            Timeframe,
            value.primary_timeframe,
            Timeframe.UNKNOWN,
        ),
        metadata=dict(value.metadata or {}),
    )


# ============================================================
# INPUT VALIDATION
# ============================================================

def validate_structure_input(
    value: StructureInput,
) -> Tuple[bool, List[str]]:

    errors: List[str] = []

    if not value.instrument_id and not value.symbol:
        errors.append(
            "Structure input requires instrument_id or symbol."
        )

    lengths = {
        "timestamps": len(value.timestamps),
        "opens": len(value.opens),
        "highs": len(value.highs),
        "lows": len(value.lows),
        "closes": len(value.closes),
    }

    non_zero_lengths = [
        length
        for length in lengths.values()
        if length > 0
    ]

    if not non_zero_lengths:
        errors.append(
            "No OHLC observations supplied."
        )
        return False, errors

    if len(set(non_zero_lengths)) != 1:
        errors.append(
            "OHLC/timestamp series lengths are inconsistent."
        )

    if value.highs and value.lows:
        for index, (high, low) in enumerate(
            zip(value.highs, value.lows)
        ):
            if high < low:
                errors.append(
                    f"High below low at observation {index}."
                )
                break

    return not errors, errors


# ============================================================
# STRUCTURE WINDOW BUILDER
# ============================================================

def build_structure_window(
    value: StructureInput,
) -> StructureWindow:

    normalized = normalize_structure_input(value)

    highs = normalized.highs
    lows = normalized.lows
    closes = normalized.closes

    high = max(highs) if highs else None
    low = min(lows) if lows else None

    first_price = (
        closes[0]
        if closes
        else None
    )

    last_price = (
        closes[-1]
        if closes
        else None
    )

    start_time = (
        normalized.timestamps[0]
        if normalized.timestamps
        else None
    )

    end_time = (
        normalized.timestamps[-1]
        if normalized.timestamps
        else None
    )

    return StructureWindow(
        instrument_id=normalized.instrument_id,
        symbol=normalized.symbol,
        timeframe=normalized.timeframe,
        start_time=start_time,
        end_time=end_time,
        bars_count=len(closes),
        high=high,
        low=low,
        first_price=first_price,
        last_price=last_price,
        source=normalized.source,
        metadata={
            **normalized.metadata,
            "normalized": True,
            "formula_generated": False,
        },
    )


# ============================================================
# STRUCTURE POINT FACTORY
# ============================================================

def create_structure_point(
    *,
    timestamp: Optional[datetime],
    price: Optional[float],
    swing_type: SwingType,
    timeframe: Timeframe,
    sequence: int = 0,
    confirmed: bool = False,
    strength: Optional[float] = None,
    source: str = "",
    metadata: Optional[Dict[str, Any]] = None,
) -> StructurePoint:

    return StructurePoint(
        timestamp=timestamp,
        price=price,
        swing_type=swing_type,
        timeframe=timeframe,
        sequence=sequence,
        confirmed=confirmed,
        strength=strength,
        source=_structure_text(source),
        metadata=dict(metadata or {}),
    )


# ============================================================
# STRUCTURE LEG FACTORY
# ============================================================

def create_structure_leg(
    start: StructurePoint,
    end: StructurePoint,
) -> StructureLeg:

    start_price = start.price
    end_price = end.price

    direction = StructureDirection.UNKNOWN
    price_change = None
    price_change_pct = None

    if (
        start_price is not None
        and end_price is not None
    ):
        price_change = end_price - start_price

        if start_price != 0:
            price_change_pct = (
                (end_price - start_price)
                / abs(start_price)
            ) * 100.0

        if end_price > start_price:
            direction = StructureDirection.BULLISH
        elif end_price < start_price:
            direction = StructureDirection.BEARISH
        else:
            direction = StructureDirection.NEUTRAL

    duration_bars = max(
        0,
        end.sequence - start.sequence,
    )

    return StructureLeg(
        start=start,
        end=end,
        direction=direction,
        price_change=price_change,
        price_change_pct=price_change_pct,
        duration_bars=duration_bars,
        confirmed=start.confirmed and end.confirmed,
        metadata={
            "derived_from_points": True,
            "formula_generated": False,
        },
    )


# ============================================================
# BASIC STRUCTURAL OBSERVATION HELPERS
# ============================================================

def extract_observation_points(
    value: StructureInput,
) -> List[StructurePoint]:

    normalized = normalize_structure_input(value)

    count = min(
        len(normalized.highs),
        len(normalized.lows),
        len(normalized.closes),
    )

    points: List[StructurePoint] = []

    for index in range(count):

        timestamp = (
            normalized.timestamps[index]
            if index < len(normalized.timestamps)
            else None
        )

        high = normalized.highs[index]
        low = normalized.lows[index]

        points.append(
            create_structure_point(
                timestamp=timestamp,
                price=high,
                swing_type=SwingType.HIGH,
                timeframe=normalized.timeframe,
                sequence=index,
                confirmed=False,
                source=normalized.source,
                metadata={
                    "observation_point": True,
                    "candidate_only": True,
                },
            )
        )

        points.append(
            create_structure_point(
                timestamp=timestamp,
                price=low,
                swing_type=SwingType.LOW,
                timeframe=normalized.timeframe,
                sequence=index,
                confirmed=False,
                source=normalized.source,
                metadata={
                    "observation_point": True,
                    "candidate_only": True,
                },
            )
        )

    return points


# ============================================================
# MULTI-TIMEFRAME NORMALIZATION
# ============================================================

def normalize_requested_timeframes(
    values: List[Any],
) -> List[Timeframe]:

    result: List[Timeframe] = []

    for value in values:
        timeframe = _structure_enum(
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


def build_multitimeframe_input(
    structures: Dict[Any, StructureInput],
    *,
    instrument_id: str = "",
    symbol: str = "",
    primary_timeframe: Timeframe = Timeframe.UNKNOWN,
) -> MultiTimeframeStructureInput:

    normalized: Dict[str, StructureInput] = {}

    for timeframe, structure_input in (
        structures or {}
    ).items():

        normalized_timeframe = _structure_enum(
            Timeframe,
            timeframe,
            Timeframe.UNKNOWN,
        )

        if normalized_timeframe == Timeframe.UNKNOWN:
            continue

        normalized[
            normalized_timeframe.value
        ] = normalize_structure_input(
            structure_input
        )

    return MultiTimeframeStructureInput(
        instrument_id=_structure_text(instrument_id),
        symbol=_structure_text(symbol),
        structures=normalized,
        primary_timeframe=_structure_enum(
            Timeframe,
            primary_timeframe,
            Timeframe.UNKNOWN,
        ),
    )


# ============================================================
# FORMULA PLUGIN CONTRACT
# ============================================================

@dataclass(frozen=True)
class StructureFormulaDescriptor:
    """
    Metadata-only contract for a validated research formula.

    The actual mathematical formula is intentionally not defined here.
    """

    formula_id: str = ""
    formula_version: str = ""

    name: str = ""
    description: str = ""

    supported_asset_classes: Tuple[str, ...] = ()
    supported_timeframes: Tuple[str, ...] = ()

    validated: bool = False
    enabled: bool = False

    owner: str = (
        "UPSTREAM_STRUCTURE_INTELLIGENCE"
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


class StructureFormulaProvider:
    """
    Pluggable interface for future validated structure research.

    No default intelligence formula is supplied.
    """

    def describe(self) -> StructureFormulaDescriptor:
        raise NotImplementedError

    def analyze(
        self,
        value: StructureInput,
    ) -> StructureAnalysis:
        raise NotImplementedError


# ============================================================
# FORMULA REGISTRY HOOK
# ============================================================

class StructureFormulaRegistry:
    """
    Lightweight local registry boundary.

    Registration does not mean formula validation.
    Validation authority remains upstream research.
    """

    def __init__(self) -> None:
        self._formulas: Dict[
            str,
            StructureFormulaProvider,
        ] = {}

    def register(
        self,
        provider: StructureFormulaProvider,
    ) -> bool:

        descriptor = provider.describe()

        formula_id = _structure_text(
            descriptor.formula_id
        )

        if not formula_id:
            return False

        self._formulas[formula_id] = provider
        return True

    def unregister(
        self,
        formula_id: str,
    ) -> bool:

        formula_id = _structure_text(formula_id)

        if formula_id not in self._formulas:
            return False

        del self._formulas[formula_id]
        return True

    def get(
        self,
        formula_id: str,
    ) -> Optional[StructureFormulaProvider]:

        return self._formulas.get(
            _structure_text(formula_id)
        )

    def descriptors(
        self,
    ) -> List[StructureFormulaDescriptor]:

        return [
            provider.describe()
            for provider in self._formulas.values()
        ]

    def clear(self) -> None:
        self._formulas.clear()

    def __len__(self) -> int:
        return len(self._formulas)


_DEFAULT_STRUCTURE_FORMULA_REGISTRY = (
    StructureFormulaRegistry()
)


def get_structure_formula_registry(
) -> StructureFormulaRegistry:

    return _DEFAULT_STRUCTURE_FORMULA_REGISTRY


# ============================================================
# FORMULA RESOLUTION
# ============================================================

def resolve_structure_formula(
    formula_id: str,
    *,
    require_validated: bool = True,
) -> Optional[StructureFormulaProvider]:

    registry = get_structure_formula_registry()

    provider = registry.get(formula_id)

    if provider is None:
        return None

    descriptor = provider.describe()

    if require_validated and not descriptor.validated:
        return None

    if not descriptor.enabled:
        return None

    return provider


# ============================================================
# PART-2 DATA READINESS
# ============================================================

def structure_input_readiness(
    value: Optional[StructureInput],
) -> Dict[str, Any]:

    if value is None:
        return {
            "ready": False,
            "reason": "No structure input.",
            "bars": 0,
            "ohlc_complete": False,
        }

    normalized = normalize_structure_input(value)

    valid, errors = validate_structure_input(
        normalized
    )

    bars = len(normalized.closes)

    ohlc_complete = (
        bars > 0
        and len(normalized.opens) == bars
        and len(normalized.highs) == bars
        and len(normalized.lows) == bars
    )

    return {
        "ready": valid and ohlc_complete,
        "reason": (
            "READY"
            if valid and ohlc_complete
            else "INPUT_NOT_READY"
        ),
        "bars": bars,
        "ohlc_complete": ohlc_complete,
        "errors": errors,
        "formula_generated": False,
    }


# ============================================================
# PART-2 CONTRACT EXTENSION
# ============================================================

STRUCTURE_ENGINE_PART2_CONTRACT = {
    "normalization": {
        "ohlcv_normalization": True,
        "timestamp_normalization": True,
        "structure_window": True,
        "observation_points": True,
        "structure_legs": True,
    },

    "formula_layer": {
        "registry_hook": True,
        "plugin_interface": True,
        "formula_pluggable": True,
        "default_formula": False,
        "guessed_formula": False,
        "silent_formula": False,
    },

    "research_authority": (
        "UPSTREAM_STRUCTURE_INTELLIGENCE"
    ),

    "output_policy": {
        "intelligence_generated": False,
        "opportunity_generated": False,
        "signal_generated": False,
        "score_generated": False,
        "decision_generated": False,
        "d13_modified": False,
        "risk_generated": False,
        "cas_bypassed": False,
        "execution_authority": False,
    },
}


# ============================================================
# PART-2 VALIDATION
# ============================================================

def validate_structure_part2() -> bool:

    forbidden = (
        STRUCTURE_ENGINE_PART2_CONTRACT[
            "output_policy"
        ]
    )

    return all(
        value is False
        for value in forbidden.values()
    )


# ============================================================
# UPDATE EXPORTS
# ============================================================

__all__.extend(
    [
        # Normalization
        "normalize_structure_input",
        "normalize_multitimeframe_input",
        "normalize_requested_timeframes",

        # Validation / readiness
        "validate_structure_input",
        "structure_input_readiness",

        # Structural primitives
        "build_structure_window",
        "create_structure_point",
        "create_structure_leg",
        "extract_observation_points",

        # Multi-timeframe
        "build_multitimeframe_input",

        # Formula plugin architecture
        "StructureFormulaDescriptor",
        "StructureFormulaProvider",
        "StructureFormulaRegistry",
        "get_structure_formula_registry",
        "resolve_structure_formula",

        # Contract / validation
        "STRUCTURE_ENGINE_PART2_CONTRACT",
        "validate_structure_part2",
    ]
)
# ============================================================
# PART 3 — ENGINE EXECUTION / MULTI-TIMEFRAME ORCHESTRATION
# ============================================================

def _structure_formula_metadata(
    provider: Optional[StructureFormulaProvider],
) -> Dict[str, Any]:

    if provider is None:
        return {
            "formula_available": False,
            "formula_validated": False,
            "formula_id": "",
            "formula_version": "",
        }

    descriptor = provider.describe()

    return {
        "formula_available": True,
        "formula_validated": bool(descriptor.validated),
        "formula_id": descriptor.formula_id,
        "formula_version": descriptor.formula_version,
    }


# ============================================================
# SINGLE TIMEFRAME EXECUTION
# ============================================================

def analyze_structure(
    value: StructureInput,
    *,
    formula_id: str = "",
    formula_version: str = "",
    require_validated_formula: bool = True,
) -> StructureEngineResult:

    normalized = normalize_structure_input(value)

    readiness = structure_input_readiness(
        normalized
    )

    if not readiness["ready"]:
        return StructureEngineResult(
            status=(
                StructureStatus.INSUFFICIENT_DATA
            ),
            warnings=[
                readiness.get(
                    "reason",
                    "Structure input not ready.",
                )
            ],
            errors=list(
                readiness.get("errors", [])
            ),
            formula_id=_structure_text(
                formula_id
            ),
            formula_version=_structure_text(
                formula_version
            ),
            research_formula_available=False,
            research_formula_validated=False,
            metadata={
                "engine_generated_intelligence": False,
                "formula_required": True,
                "formula_execution": False,
            },
        )

    if not formula_id:
        return StructureEngineResult(
            status=StructureStatus.DEGRADED,
            warnings=[
                "No structure research formula selected."
            ],
            formula_id="",
            formula_version="",
            research_formula_available=False,
            research_formula_validated=False,
            metadata={
                "formula_required": True,
                "formula_missing": True,
                "intelligence_generated": False,
            },
        )

    provider = resolve_structure_formula(
        formula_id,
        require_validated=require_validated_formula,
    )

    if provider is None:
        return StructureEngineResult(
            status=StructureStatus.DEGRADED,
            warnings=[
                "Requested structure formula is unavailable, "
                "disabled, or not validated."
            ],
            formula_id=_structure_text(
                formula_id
            ),
            formula_version=_structure_text(
                formula_version
            ),
            research_formula_available=False,
            research_formula_validated=False,
            metadata={
                "formula_required": True,
                "formula_execution": False,
                "intelligence_generated": False,
            },
        )

    descriptor = provider.describe()

    if (
        formula_version
        and descriptor.formula_version
        and formula_version
        != descriptor.formula_version
    ):
        return StructureEngineResult(
            status=StructureStatus.INVALID,
            errors=[
                "Requested formula version does not "
                "match registered formula."
            ],
            formula_id=descriptor.formula_id,
            formula_version=descriptor.formula_version,
            research_formula_available=True,
            research_formula_validated=bool(
                descriptor.validated
            ),
            metadata={
                "formula_version_mismatch": True,
                "formula_execution": False,
            },
        )

    try:
        analysis = provider.analyze(
            normalized
        )
    except Exception as exc:
        return StructureEngineResult(
            status=StructureStatus.INVALID,
            errors=[
                f"Structure formula execution failed: {exc}"
            ],
            formula_id=descriptor.formula_id,
            formula_version=descriptor.formula_version,
            research_formula_available=True,
            research_formula_validated=bool(
                descriptor.validated
            ),
            metadata={
                "formula_execution": False,
                "formula_execution_error": True,
            },
        )

    if not isinstance(
        analysis,
        StructureAnalysis,
    ):
        return StructureEngineResult(
            status=StructureStatus.INVALID,
            errors=[
                "Structure formula returned an invalid "
                "StructureAnalysis contract."
            ],
            formula_id=descriptor.formula_id,
            formula_version=descriptor.formula_version,
            research_formula_available=True,
            research_formula_validated=bool(
                descriptor.validated
            ),
        )

    analysis.instrument_id = (
        analysis.instrument_id
        or normalized.instrument_id
    )

    analysis.symbol = (
        analysis.symbol
        or normalized.symbol
    )

    analysis.timeframe = (
        analysis.timeframe
        if analysis.timeframe
        != Timeframe.UNKNOWN
        else normalized.timeframe
    )

    analysis.formula_id = (
        analysis.formula_id
        or descriptor.formula_id
    )

    analysis.formula_version = (
        analysis.formula_version
        or descriptor.formula_version
    )

    analysis.research_validated = bool(
        descriptor.validated
    )

    analysis.structure_window = (
        analysis.structure_window
        or build_structure_window(
            normalized
        )
    )

    analysis.metadata = {
        **analysis.metadata,
        "upstream_formula": True,
        "formula_pluggable": True,
        "engine_invented_formula": False,
        "scanner_generated_intelligence": False,
        "opportunity_generated": False,
        "decision_generated": False,
        "d13_modified": False,
    }

    return StructureEngineResult(
        status=(
            analysis.status
            if analysis.status
            != StructureStatus.UNKNOWN
            else StructureStatus.READY
        ),
        structure=analysis,
        formula_id=descriptor.formula_id,
        formula_version=descriptor.formula_version,
        research_formula_available=True,
        research_formula_validated=bool(
            descriptor.validated
        ),
        metadata={
            "formula_execution": True,
            "research_validated": bool(
                descriptor.validated
            ),
            "engine_invented_formula": False,
            "opportunity_generation": False,
            "decision_generation": False,
        },
    )


# ============================================================
# STRUCTURAL RELATION
# ============================================================

def classify_structure_relation(
    structures: Dict[str, StructureAnalysis],
) -> StructureRelation:

    valid_structures = [
        value
        for value in structures.values()
        if isinstance(
            value,
            StructureAnalysis,
        )
        and value.direction
        != StructureDirection.UNKNOWN
    ]

    if not valid_structures:
        return StructureRelation.UNKNOWN

    directions = {
        item.direction
        for item in valid_structures
    }

    if len(directions) == 1:
        direction = next(iter(directions))

        if direction in {
            StructureDirection.BULLISH,
            StructureDirection.BEARISH,
        }:
            return StructureRelation.ALIGNED

        if direction == StructureDirection.NEUTRAL:
            return StructureRelation.NEUTRAL

    if (
        StructureDirection.BULLISH in directions
        and StructureDirection.BEARISH in directions
    ):
        return StructureRelation.CONFLICTING

    if (
        StructureDirection.MIXED in directions
        or StructureDirection.NEUTRAL in directions
    ):
        return StructureRelation.DIVERGENT

    return StructureRelation.UNKNOWN


# ============================================================
# DOMINANT DIRECTION
# ============================================================

def determine_dominant_structure_direction(
    structures: Dict[str, StructureAnalysis],
) -> StructureDirection:

    directions = [
        item.direction
        for item in structures.values()
        if isinstance(
            item,
            StructureAnalysis,
        )
    ]

    bullish = directions.count(
        StructureDirection.BULLISH
    )

    bearish = directions.count(
        StructureDirection.BEARISH
    )

    neutral = directions.count(
        StructureDirection.NEUTRAL
    )

    if bullish > bearish and bullish > neutral:
        return StructureDirection.BULLISH

    if bearish > bullish and bearish > neutral:
        return StructureDirection.BEARISH

    if (
        neutral > bullish
        and neutral > bearish
    ):
        return StructureDirection.NEUTRAL

    if (
        bullish == bearish
        and bullish > 0
    ):
        return StructureDirection.MIXED

    return StructureDirection.UNKNOWN


# ============================================================
# MULTI-TIMEFRAME EXECUTION
# ============================================================

def analyze_multitimeframe_structure(
    value: MultiTimeframeStructureInput,
    *,
    formula_ids: Optional[Dict[str, str]] = None,
    formula_versions: Optional[Dict[str, str]] = None,
    require_validated_formula: bool = True,
) -> StructureEngineResult:

    normalized = normalize_multitimeframe_input(
        value
    )

    if not normalized.structures:
        return StructureEngineResult(
            status=StructureStatus.INSUFFICIENT_DATA,
            warnings=[
                "No timeframe structures supplied."
            ],
            metadata={
                "multi_timeframe": True,
                "formula_execution": False,
            },
        )

    formula_ids = formula_ids or {}
    formula_versions = formula_versions or {}

    analyses: Dict[
        str,
        StructureAnalysis,
    ] = {}

    warnings: List[str] = []
    errors: List[str] = []

    formula_available = False
    formula_validated = False

    for timeframe_key, structure_input in (
        normalized.structures.items()
    ):

        formula_id = _structure_text(
            formula_ids.get(
                timeframe_key,
                "",
            )
        )

        formula_version = _structure_text(
            formula_versions.get(
                timeframe_key,
                "",
            )
        )

        result = analyze_structure(
            structure_input,
            formula_id=formula_id,
            formula_version=formula_version,
            require_validated_formula=(
                require_validated_formula
            ),
        )

        if result.structure is not None:
            analyses[timeframe_key] = (
                result.structure
            )

        warnings.extend(result.warnings)
        errors.extend(result.errors)

        formula_available = (
            formula_available
            or result.research_formula_available
        )

        formula_validated = (
            formula_validated
            or result.research_formula_validated
        )

    if not analyses:
        return StructureEngineResult(
            status=(
                StructureStatus.DEGRADED
                if not errors
                else StructureStatus.INVALID
            ),
            warnings=warnings,
            errors=errors,
            research_formula_available=(
                formula_available
            ),
            research_formula_validated=(
                formula_validated
            ),
            metadata={
                "multi_timeframe": True,
                "analysis_count": 0,
                "formula_execution": False,
            },
        )

    relation = classify_structure_relation(
        analyses
    )

    dominant_direction = (
        determine_dominant_structure_direction(
            analyses
        )
    )

    primary_key = (
        normalized.primary_timeframe.value
        if normalized.primary_timeframe
        != Timeframe.UNKNOWN
        else ""
    )

    if (
        primary_key
        and primary_key not in analyses
    ):
        primary_key = ""

    if not primary_key:
        primary_key = next(
            iter(analyses)
        )

    primary_structure = analyses[
        primary_key
    ]

    multi = MultiTimeframeStructure(
        instrument_id=(
            normalized.instrument_id
            or primary_structure.instrument_id
        ),
        symbol=(
            normalized.symbol
            or primary_structure.symbol
        ),
        timeframe_structures=analyses,
        primary_timeframe=(
            _structure_enum(
                Timeframe,
                primary_key,
                Timeframe.UNKNOWN,
            )
        ),
        dominant_direction=dominant_direction,
        relation=relation,
        confidence=primary_structure.confidence,
        research_validated=formula_validated,
        metadata={
            "multi_timeframe": True,
            "primary_structure": primary_key,
            "formula_pluggable": True,
            "engine_invented_formula": False,
            "opportunity_generation": False,
            "decision_generation": False,
        },
    )

    return StructureEngineResult(
        status=(
            StructureStatus.READY
            if not errors
            else StructureStatus.DEGRADED
        ),
        multi_timeframe=multi,
        warnings=warnings,
        errors=errors,
        research_formula_available=(
            formula_available
        ),
        research_formula_validated=(
            formula_validated
        ),
        metadata={
            "multi_timeframe": True,
            "analysis_count": len(analyses),
            "relation": relation.value,
            "dominant_direction": (
                dominant_direction.value
            ),
            "formula_execution": bool(
                analyses
            ),
            "engine_invented_formula": False,
        },
    )


# ============================================================
# REQUEST ORCHESTRATOR
# ============================================================

def run_structure_engine(
    request: StructureEngineRequest,
) -> StructureEngineResult:

    if request is None:
        return StructureEngineResult(
            status=StructureStatus.INVALID,
            errors=[
                "Structure engine request is required."
            ],
        )

    requested = normalize_requested_timeframes(
        request.requested_timeframes
    )

    if request.multi_timeframe_input is not None:

        mtf_input = (
            normalize_multitimeframe_input(
                request.multi_timeframe_input
            )
        )

        if requested:
            allowed = {
                timeframe.value
                for timeframe in requested
            }

            mtf_input.structures = {
                key: value
                for key, value
                in mtf_input.structures.items()
                if key in allowed
            }

        formula_ids = {}

        formula_versions = {}

        if request.formula_id:
            for key in mtf_input.structures:
                formula_ids[key] = (
                    request.formula_id
                )

        if request.formula_version:
            for key in mtf_input.structures:
                formula_versions[key] = (
                    request.formula_version
                )

        metadata_formula_ids = (
            request.metadata.get(
                "formula_ids",
                {},
            )
            if request.metadata
            else {}
        )

        metadata_formula_versions = (
            request.metadata.get(
                "formula_versions",
                {},
            )
            if request.metadata
            else {}
        )

        formula_ids.update(
            metadata_formula_ids
        )

        formula_versions.update(
            metadata_formula_versions
        )

        return analyze_multitimeframe_structure(
            mtf_input,
            formula_ids=formula_ids,
            formula_versions=formula_versions,
            require_validated_formula=(
                request.require_validated_formula
            ),
        )

    if request.input_data is None:
        return StructureEngineResult(
            status=StructureStatus.INVALID,
            errors=[
                "No single-timeframe or "
                "multi-timeframe input supplied."
            ],
        )

    input_data = normalize_structure_input(
        request.input_data
    )

    return analyze_structure(
        input_data,
        formula_id=request.formula_id,
        formula_version=request.formula_version,
        require_validated_formula=(
            request.require_validated_formula
        ),
    )


# ============================================================
# ENGINE SNAPSHOT
# ============================================================

def build_structure_engine_snapshot(
    request: StructureEngineRequest,
    result: StructureEngineResult,
) -> StructureEngineSnapshot:

    return StructureEngineSnapshot(
        request=request,
        result=result,
        captured_at=_structure_now(),
        metadata={
            "snapshot": True,
            "upstream_truth_preserved": True,
            "formula_pluggable": True,
            "engine_invented_formula": False,
            "opportunity_generation": False,
            "decision_generation": False,
            "d13_modified": False,
            "risk_override": False,
            "cas_bypass": False,
            "execution": False,
        },
    )


# ============================================================
# PART-3 CONTRACT
# ============================================================

STRUCTURE_ENGINE_PART3_CONTRACT = {
    "execution": {
        "single_timeframe": True,
        "multi_timeframe": True,
        "formula_resolution": True,
        "formula_version_check": True,
        "research_validation_check": True,
    },

    "multi_timeframe": {
        "5M": True,
        "15M": True,
        "1H": True,
        "4H": True,
        "1D": True,
        "1W": True,
        "1MN": True,
        "relation_analysis": True,
        "dominant_direction": True,
    },

    "formula_policy": {
        "formula_pluggable": True,
        "formula_required": True,
        "validated_formula_required": True,
        "default_formula": False,
        "guessed_formula": False,
        "silent_formula": False,
    },

    "authority": {
        "structure_engine": True,
        "opportunity_engine": False,
        "scanner": False,
        "decision_cortex": False,
        "d13": False,
        "risk": False,
        "cas": False,
        "execution": False,
    },
}


def validate_structure_part3() -> bool:

    formula_policy = (
        STRUCTURE_ENGINE_PART3_CONTRACT[
            "formula_policy"
        ]
    )

    forbidden = [
        "default_formula",
        "guessed_formula",
        "silent_formula",
    ]

    return all(
        formula_policy.get(
            key
        ) is False
        for key in forbidden
    )


# ============================================================
# PART-3 EXPORTS
# ============================================================

__all__.extend(
    [
        "analyze_structure",
        "classify_structure_relation",
        "determine_dominant_structure_direction",
        "analyze_multitimeframe_structure",
        "run_structure_engine",
        "build_structure_engine_snapshot",
        "STRUCTURE_ENGINE_PART3_CONTRACT",
        "validate_structure_part3",
    ]
)
# ============================================================
# PART 4 — SERIALIZATION / VALIDATION / HEALTH / DIAGNOSTICS
# ============================================================

def _serialize_structure_value(
    value: Any,
) -> Any:

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, list):
        return [
            _serialize_structure_value(item)
            for item in value
        ]

    if isinstance(value, tuple):
        return [
            _serialize_structure_value(item)
            for item in value
        ]

    if isinstance(value, dict):
        return {
            str(key): _serialize_structure_value(item)
            for key, item in value.items()
        }

    if hasattr(value, "__dataclass_fields__"):
        return {
            key: _serialize_structure_value(
                getattr(value, key)
            )
            for key in value.__dataclass_fields__
        }

    return value


# ============================================================
# SERIALIZERS
# ============================================================

def serialize_structure_point(
    value: StructurePoint,
) -> Dict[str, Any]:
    return _serialize_structure_value(value)


def serialize_structure_leg(
    value: StructureLeg,
) -> Dict[str, Any]:
    return _serialize_structure_value(value)


def serialize_structure_window(
    value: StructureWindow,
) -> Dict[str, Any]:
    return _serialize_structure_value(value)


def serialize_structure_input(
    value: StructureInput,
) -> Dict[str, Any]:
    return _serialize_structure_value(value)


def serialize_structure_analysis(
    value: StructureAnalysis,
) -> Dict[str, Any]:
    return _serialize_structure_value(value)


def serialize_multitimeframe_structure(
    value: MultiTimeframeStructure,
) -> Dict[str, Any]:
    return _serialize_structure_value(value)


def serialize_structure_result(
    value: StructureEngineResult,
) -> Dict[str, Any]:
    return _serialize_structure_value(value)


def serialize_structure_request(
    value: StructureEngineRequest,
) -> Dict[str, Any]:
    return _serialize_structure_value(value)


def serialize_structure_snapshot(
    value: StructureEngineSnapshot,
) -> Dict[str, Any]:
    return _serialize_structure_value(value)


def serialize_structure_formula_descriptor(
    value: StructureFormulaDescriptor,
) -> Dict[str, Any]:
    return _serialize_structure_value(value)


# ============================================================
# STRUCTURE POINT VALIDATION
# ============================================================

def validate_structure_point(
    value: StructurePoint,
) -> Tuple[bool, List[str]]:

    errors: List[str] = []

    if not isinstance(
        value,
        StructurePoint,
    ):
        return False, [
            "Invalid StructurePoint contract."
        ]

    if value.price is not None:
        if value.price <= 0:
            errors.append(
                "Structure point price must be positive."
            )

    if value.sequence < 0:
        errors.append(
            "Structure point sequence cannot be negative."
        )

    if value.strength is not None:
        if not 0.0 <= value.strength <= 1.0:
            errors.append(
                "Structure point strength must be "
                "between 0 and 1."
            )

    return not errors, errors


# ============================================================
# STRUCTURE LEG VALIDATION
# ============================================================

def validate_structure_leg(
    value: StructureLeg,
) -> Tuple[bool, List[str]]:

    errors: List[str] = []

    if not isinstance(
        value,
        StructureLeg,
    ):
        return False, [
            "Invalid StructureLeg contract."
        ]

    if value.start is None:
        errors.append(
            "Structure leg requires start point."
        )

    if value.end is None:
        errors.append(
            "Structure leg requires end point."
        )

    if value.duration_bars < 0:
        errors.append(
            "Structure leg duration cannot be negative."
        )

    if (
        value.start is not None
        and value.end is not None
    ):
        if (
            value.end.sequence
            < value.start.sequence
        ):
            errors.append(
                "Structure leg end sequence precedes start."
            )

    return not errors, errors


# ============================================================
# STRUCTURE ANALYSIS VALIDATION
# ============================================================

def validate_structure_analysis(
    value: StructureAnalysis,
) -> Tuple[bool, List[str]]:

    errors: List[str] = []

    if not isinstance(
        value,
        StructureAnalysis,
    ):
        return False, [
            "Invalid StructureAnalysis contract."
        ]

    if (
        value.confidence is not None
        and not 0.0 <= value.confidence <= 1.0
    ):
        errors.append(
            "Structure confidence must be "
            "between 0 and 1."
        )

    for point in value.swing_highs:
        valid, point_errors = (
            validate_structure_point(point)
        )

        if not valid:
            errors.extend(point_errors)

    for point in value.swing_lows:
        valid, point_errors = (
            validate_structure_point(point)
        )

        if not valid:
            errors.extend(point_errors)

    for leg in value.legs:
        valid, leg_errors = (
            validate_structure_leg(leg)
        )

        if not valid:
            errors.extend(leg_errors)

    if (
        value.formula_id
        and not value.research_validated
    ):
        errors.append(
            "Formula-linked structure must identify "
            "research validation state."
        )

    return not errors, errors


# ============================================================
# MULTI-TIMEFRAME VALIDATION
# ============================================================

def validate_multitimeframe_structure(
    value: MultiTimeframeStructure,
) -> Tuple[bool, List[str]]:

    errors: List[str] = []

    if not isinstance(
        value,
        MultiTimeframeStructure,
    ):
        return False, [
            "Invalid MultiTimeframeStructure contract."
        ]

    for key, structure in (
        value.timeframe_structures or {}
    ).items():

        if not key:
            errors.append(
                "Multi-timeframe structure contains "
                "an empty timeframe key."
            )
            continue

        valid, structure_errors = (
            validate_structure_analysis(
                structure
            )
        )

        if not valid:
            errors.extend(structure_errors)

    if (
        value.primary_timeframe
        != Timeframe.UNKNOWN
        and value.primary_timeframe.value
        not in value.timeframe_structures
    ):
        errors.append(
            "Primary timeframe is not present in "
            "timeframe_structures."
        )

    if (
        value.confidence is not None
        and not 0.0 <= value.confidence <= 1.0
    ):
        errors.append(
            "Multi-timeframe confidence must be "
            "between 0 and 1."
        )

    return not errors, errors


# ============================================================
# RESULT VALIDATION
# ============================================================

def validate_structure_result(
    value: StructureEngineResult,
) -> Tuple[bool, List[str]]:

    errors: List[str] = []

    if not isinstance(
        value,
        StructureEngineResult,
    ):
        return False, [
            "Invalid StructureEngineResult contract."
        ]

    if value.structure is not None:
        valid, structure_errors = (
            validate_structure_analysis(
                value.structure
            )
        )

        if not valid:
            errors.extend(structure_errors)

    if value.multi_timeframe is not None:
        valid, mtf_errors = (
            validate_multitimeframe_structure(
                value.multi_timeframe
            )
        )

        if not valid:
            errors.extend(mtf_errors)

    if (
        value.research_formula_validated
        and not value.research_formula_available
    ):
        errors.append(
            "Validated formula cannot exist without "
            "formula availability."
        )

    return not errors, errors


# ============================================================
# FORMULA DESCRIPTOR VALIDATION
# ============================================================

def validate_structure_formula_descriptor(
    value: StructureFormulaDescriptor,
) -> Tuple[bool, List[str]]:

    errors: List[str] = []

    if not isinstance(
        value,
        StructureFormulaDescriptor,
    ):
        return False, [
            "Invalid StructureFormulaDescriptor."
        ]

    if value.validated and not value.formula_id:
        errors.append(
            "Validated formula requires formula_id."
        )

    if value.enabled and not value.formula_id:
        errors.append(
            "Enabled formula requires formula_id."
        )

    if value.validated and not value.owner:
        errors.append(
            "Validated formula requires an authority owner."
        )

    if value.owner != (
        "UPSTREAM_STRUCTURE_INTELLIGENCE"
    ):
        errors.append(
            "Structure formula owner must remain "
            "UPSTREAM_STRUCTURE_INTELLIGENCE."
        )

    return not errors, errors


# ============================================================
# AUTHORITY VALIDATION
# ============================================================

def validate_structure_engine_integrity() -> bool:

    if not validate_structure_authority():
        return False

    if not validate_structure_part2():
        return False

    if not validate_structure_part3():
        return False

    forbidden = {
        "opportunity_generation": False,
        "decision_generation": False,
        "d13_modification": False,
        "risk_override": False,
        "cas_bypass": False,
        "execution": False,
        "upstream_mutation": False,
    }

    for key, expected in forbidden.items():
        if (
            STRUCTURE_ENGINE_AUTHORITY.get(key)
            is not expected
        ):
            return False

    return True


# ============================================================
# STRUCTURE ENGINE HEALTH
# ============================================================

@dataclass
class StructureEngineHealth:
    engine: str = STRUCTURE_ENGINE
    version: str = STRUCTURE_ENGINE_VERSION

    operational: bool = False
    authority_valid: bool = False

    input_normalization_ready: bool = True
    multi_timeframe_ready: bool = True

    formula_registry_ready: bool = True
    validated_formula_available: bool = False

    research_formula_required: bool = True
    research_formula_generated_here: bool = False

    intelligence_generated_here: bool = False
    opportunity_generated_here: bool = False
    decision_generated_here: bool = False

    d13_modified: bool = False
    risk_overridden: bool = False
    cas_bypassed: bool = False
    execution_authority: bool = False

    warnings: List[str] = field(
        default_factory=list
    )

    errors: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def build_structure_engine_health(
    result: Optional[StructureEngineResult] = None,
) -> StructureEngineHealth:

    warnings: List[str] = []
    errors: List[str] = []

    authority_valid = (
        validate_structure_engine_integrity()
    )

    if not authority_valid:
        errors.append(
            "Structure engine authority contract invalid."
        )

    validated_formula_available = False

    if result is not None:
        validated_formula_available = (
            result.research_formula_available
            and result.research_formula_validated
        )

        warnings.extend(result.warnings)
        errors.extend(result.errors)

    operational = (
        authority_valid
        and not errors
    )

    return StructureEngineHealth(
        operational=operational,
        authority_valid=authority_valid,
        validated_formula_available=(
            validated_formula_available
        ),
        warnings=warnings,
        errors=errors,
        metadata={
            "formula_pluggable": True,
            "formula_generated_here": False,
            "intelligence_generated_here": False,
            "opportunity_generated_here": False,
            "decision_generated_here": False,
            "d13_modified": False,
            "risk_overridden": False,
            "cas_bypassed": False,
            "execution_authority": False,
        },
    )


def serialize_structure_engine_health(
    value: StructureEngineHealth,
) -> Dict[str, Any]:

    return _serialize_structure_value(value)


# ============================================================
# OPERATIONAL CHECK
# ============================================================

def structure_engine_operational_check(
) -> Dict[str, Any]:

    authority_valid = (
        validate_structure_engine_integrity()
    )

    registry = get_structure_formula_registry()

    descriptors = registry.descriptors()

    validated_enabled = [
        descriptor
        for descriptor in descriptors
        if descriptor.validated
        and descriptor.enabled
    ]

    return {
        "engine": STRUCTURE_ENGINE,
        "version": STRUCTURE_ENGINE_VERSION,
        "operational": authority_valid,
        "authority_valid": authority_valid,

        "formula_registry_ready": True,
        "registered_formula_count": len(
            descriptors
        ),
        "validated_enabled_formula_count": len(
            validated_enabled
        ),

        "formula_required": True,
        "formula_pluggable": True,
        "formula_generated_here": False,

        "structure_analysis": True,
        "opportunity_generation": False,
        "decision_generation": False,
        "d13_modification": False,
        "risk_override": False,
        "cas_bypass": False,
        "execution": False,
    }


# ============================================================
# DIAGNOSTICS
# ============================================================

def diagnose_structure_engine(
    result: Optional[StructureEngineResult] = None,
) -> Dict[str, Any]:

    health = build_structure_engine_health(
        result
    )

    diagnosis = {
        "engine": STRUCTURE_ENGINE,
        "version": STRUCTURE_ENGINE_VERSION,
        "operational": health.operational,
        "authority_valid": health.authority_valid,
        "formula_required": (
            health.research_formula_required
        ),
        "validated_formula_available": (
            health.validated_formula_available
        ),
        "warnings": list(
            health.warnings
        ),
        "errors": list(
            health.errors
        ),
        "formula_pluggable": True,
        "intelligence_generated_here": False,
        "opportunity_generated_here": False,
        "decision_generated_here": False,
        "d13_modified": False,
        "risk_overridden": False,
        "cas_bypassed": False,
        "execution_authority": False,
    }

    if result is None:
        diagnosis["state"] = (
            "NO_RESULT"
        )
    elif result.structure is not None:
        diagnosis["state"] = (
            "STRUCTURE_AVAILABLE"
        )
    elif result.multi_timeframe is not None:
        diagnosis["state"] = (
            "MULTI_TIMEFRAME_AVAILABLE"
        )
    else:
        diagnosis["state"] = (
            "NO_STRUCTURE_AVAILABLE"
        )

    return diagnosis


# ============================================================
# CONTRACT MANIFEST
# ============================================================

def structure_engine_contract_manifest(
) -> Dict[str, Any]:

    return {
        **STRUCTURE_ENGINE_CONTRACT,

        "part2": STRUCTURE_ENGINE_PART2_CONTRACT,

        "part3": STRUCTURE_ENGINE_PART3_CONTRACT,

        "part4": {
            "serialization": True,
            "validation": True,
            "health": True,
            "diagnostics": True,
            "authority_integrity": True,
        },

        "truth_policy": {
            "formula_must_be_research_validated": True,
            "engine_invented_formula": False,
            "scanner_generated_intelligence": False,
            "opportunity_generated": False,
            "decision_generated": False,
            "d13_modified": False,
            "risk_overridden": False,
            "cas_bypassed": False,
            "execution_authority": False,
        },
    }


# ============================================================
# PART-4 SELF CHECK
# ============================================================

def structure_engine_part4_self_check(
) -> Dict[str, Any]:

    authority_ok = (
        validate_structure_engine_integrity()
    )

    sample_input = StructureInput(
        instrument_id="SELF_CHECK",
        symbol="TEST",
        asset_class="EQUITY",
        timeframe=Timeframe.D1,
        timestamps=[
            datetime(
                2026,
                1,
                1,
                tzinfo=timezone.utc,
            ),
            datetime(
                2026,
                1,
                2,
                tzinfo=timezone.utc,
            ),
        ],
        opens=[100.0, 102.0],
        highs=[103.0, 105.0],
        lows=[99.0, 101.0],
        closes=[102.0, 104.0],
        volumes=[1000.0, 1200.0],
        source="SELF_CHECK",
    )

    normalized = normalize_structure_input(
        sample_input
    )

    valid, errors = validate_structure_input(
        normalized
    )

    window = build_structure_window(
        normalized
    )

    return {
        "engine": STRUCTURE_ENGINE,
        "version": STRUCTURE_ENGINE_VERSION,
        "authority_valid": authority_ok,
        "input_valid": valid,
        "input_errors": errors,
        "window_bars": window.bars_count,
        "formula_registry_ready": (
            get_structure_formula_registry()
            is not None
        ),
        "formula_generated_here": False,
        "intelligence_generated_here": False,
        "opportunity_generated_here": False,
        "decision_generated_here": False,
        "d13_modified": False,
        "risk_overridden": False,
        "cas_bypassed": False,
        "execution_authority": False,
        "status": (
            "PASS"
            if authority_ok and valid
            else "FAIL"
        ),
    }


# ============================================================
# PART-4 EXPORTS
# ============================================================

__all__.extend(
    [
        # Serialization
        "_serialize_structure_value",
        "serialize_structure_point",
        "serialize_structure_leg",
        "serialize_structure_window",
        "serialize_structure_input",
        "serialize_structure_analysis",
        "serialize_multitimeframe_structure",
        "serialize_structure_result",
        "serialize_structure_request",
        "serialize_structure_snapshot",
        "serialize_structure_formula_descriptor",

        # Validation
        "validate_structure_point",
        "validate_structure_leg",
        "validate_structure_analysis",
        "validate_multitimeframe_structure",
        "validate_structure_result",
        "validate_structure_formula_descriptor",
        "validate_structure_engine_integrity",

        # Health
        "StructureEngineHealth",
        "build_structure_engine_health",
        "serialize_structure_engine_health",
        "structure_engine_operational_check",

        # Diagnostics
        "diagnose_structure_engine",
        "structure_engine_contract_manifest",
        "structure_engine_part4_self_check",
    ]
)
# ============================================================
# PART 5 — FINAL INTEGRATION / FACTORY / SELF-CHECK / EXPORTS
# ============================================================


# ============================================================
# SAFE REQUEST FACTORY
# ============================================================

def create_structure_request(
    *,
    input_data: Optional[StructureInput] = None,
    multi_timeframe_input: Optional[
        MultiTimeframeStructureInput
    ] = None,
    requested_timeframes: Optional[
        List[Timeframe]
    ] = None,
    formula_id: str = "",
    formula_version: str = "",
    require_validated_formula: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
) -> StructureEngineRequest:

    if requested_timeframes is None:
        requested_timeframes = [
            Timeframe.M5,
            Timeframe.M15,
            Timeframe.H1,
            Timeframe.H4,
            Timeframe.D1,
            Timeframe.W1,
            Timeframe.MN1,
        ]

    return StructureEngineRequest(
        input_data=(
            normalize_structure_input(input_data)
            if input_data is not None
            else None
        ),
        multi_timeframe_input=(
            normalize_multitimeframe_input(
                multi_timeframe_input
            )
            if multi_timeframe_input is not None
            else None
        ),
        requested_timeframes=(
            normalize_requested_timeframes(
                requested_timeframes
            )
        ),
        formula_id=_structure_text(
            formula_id
        ),
        formula_version=_structure_text(
            formula_version
        ),
        require_validated_formula=(
            bool(require_validated_formula)
        ),
        metadata=dict(metadata or {}),
    )


# ============================================================
# SAFE ENGINE EXECUTION
# ============================================================

def execute_structure_request(
    request: Optional[
        StructureEngineRequest
    ],
) -> StructureEngineResult:

    if request is None:
        return StructureEngineResult(
            status=StructureStatus.INVALID,
            errors=[
                "StructureEngineRequest is required."
            ],
            metadata={
                "safe_execution": True,
                "exception": False,
            },
        )

    try:
        return run_structure_engine(
            request
        )

    except Exception as exc:
        return StructureEngineResult(
            status=StructureStatus.INVALID,
            errors=[
                f"Unhandled structure engine error: {exc}"
            ],
            metadata={
                "safe_execution": True,
                "exception": True,
                "engine_invented_formula": False,
            },
        )


# ============================================================
# RESULT STATUS HELPERS
# ============================================================

def structure_result_is_ready(
    result: Optional[
        StructureEngineResult
    ],
) -> bool:

    if result is None:
        return False

    if result.status != StructureStatus.READY:
        return False

    return (
        result.structure is not None
        or result.multi_timeframe is not None
    )


def structure_result_has_validated_research(
    result: Optional[
        StructureEngineResult
    ],
) -> bool:

    if result is None:
        return False

    return bool(
        result.research_formula_available
        and result.research_formula_validated
    )


def structure_result_has_errors(
    result: Optional[
        StructureEngineResult
    ],
) -> bool:

    if result is None:
        return True

    return bool(result.errors)


# ============================================================
# STRUCTURE ANALYSIS SUMMARY
# ============================================================

def summarize_structure_analysis(
    value: Optional[
        StructureAnalysis
    ],
) -> Dict[str, Any]:

    if value is None:
        return {
            "available": False,
            "direction": StructureDirection.UNKNOWN.value,
            "structure_type": StructureType.UNKNOWN.value,
            "phase": StructurePhase.UNKNOWN.value,
            "confidence": None,
            "timeframe": Timeframe.UNKNOWN.value,
        }

    return {
        "available": True,
        "instrument_id": value.instrument_id,
        "symbol": value.symbol,
        "timeframe": value.timeframe.value,
        "status": value.status.value,
        "direction": value.direction.value,
        "structure_type": value.structure_type.value,
        "phase": value.phase.value,
        "swing_high_count": len(
            value.swing_highs
        ),
        "swing_low_count": len(
            value.swing_lows
        ),
        "leg_count": len(
            value.legs
        ),
        "confidence": value.confidence,
        "confidence_class": (
            value.confidence_class.value
        ),
        "formula_id": value.formula_id,
        "formula_version": value.formula_version,
        "research_validated": (
            value.research_validated
        ),
    }


# ============================================================
# MULTI-TIMEFRAME SUMMARY
# ============================================================

def summarize_multitimeframe_structure(
    value: Optional[
        MultiTimeframeStructure
    ],
) -> Dict[str, Any]:

    if value is None:
        return {
            "available": False,
            "timeframes": [],
            "dominant_direction": (
                StructureDirection.UNKNOWN.value
            ),
            "relation": (
                StructureRelation.UNKNOWN.value
            ),
        }

    return {
        "available": True,
        "instrument_id": value.instrument_id,
        "symbol": value.symbol,
        "timeframes": list(
            value.timeframe_structures.keys()
        ),
        "primary_timeframe": (
            value.primary_timeframe.value
        ),
        "dominant_direction": (
            value.dominant_direction.value
        ),
        "relation": value.relation.value,
        "confidence": value.confidence,
        "research_validated": (
            value.research_validated
        ),
    }


# ============================================================
# RESULT SUMMARY
# ============================================================

def structure_result_summary(
    result: Optional[
        StructureEngineResult
    ],
) -> Dict[str, Any]:

    if result is None:
        return {
            "available": False,
            "status": StructureStatus.UNKNOWN.value,
            "errors": [
                "No structure result."
            ],
        }

    return {
        "available": (
            result.structure is not None
            or result.multi_timeframe is not None
        ),
        "status": result.status.value,
        "formula_id": result.formula_id,
        "formula_version": result.formula_version,
        "research_formula_available": (
            result.research_formula_available
        ),
        "research_formula_validated": (
            result.research_formula_validated
        ),
        "single_timeframe": (
            summarize_structure_analysis(
                result.structure
            )
        ),
        "multi_timeframe": (
            summarize_multitimeframe_structure(
                result.multi_timeframe
            )
        ),
        "warnings": list(
            result.warnings
        ),
        "errors": list(
            result.errors
        ),
        "engine_invented_formula": False,
        "opportunity_generation": False,
        "decision_generation": False,
        "d13_modified": False,
        "risk_override": False,
        "cas_bypass": False,
        "execution_authority": False,
    }


# ============================================================
# FORMULA REGISTRY SUMMARY
# ============================================================

def structure_formula_registry_summary(
) -> Dict[str, Any]:

    registry = (
        get_structure_formula_registry()
    )

    descriptors = registry.descriptors()

    return {
        "registry_ready": True,
        "formula_count": len(
            descriptors
        ),
        "validated_count": sum(
            1
            for item in descriptors
            if item.validated
        ),
        "enabled_count": sum(
            1
            for item in descriptors
            if item.enabled
        ),
        "validated_enabled_count": sum(
            1
            for item in descriptors
            if item.validated
            and item.enabled
        ),
        "formulas": [
            serialize_structure_formula_descriptor(
                item
            )
            for item in descriptors
        ],
        "formula_authority": (
            "UPSTREAM_STRUCTURE_INTELLIGENCE"
        ),
    }


# ============================================================
# CONTRACT INTEGRITY
# ============================================================

def validate_structure_contract_integrity(
) -> Dict[str, Any]:

    authority = validate_structure_authority()

    part2 = validate_structure_part2()

    part3 = validate_structure_part3()

    full_integrity = (
        validate_structure_engine_integrity()
    )

    return {
        "engine": STRUCTURE_ENGINE,
        "version": STRUCTURE_ENGINE_VERSION,
        "authority_valid": authority,
        "part2_valid": part2,
        "part3_valid": part3,
        "full_integrity": full_integrity,
        "formula_pluggable": True,
        "formula_generated_here": False,
        "opportunity_generated_here": False,
        "decision_generated_here": False,
        "d13_modified": False,
        "risk_overridden": False,
        "cas_bypassed": False,
        "execution_authority": False,
    }


# ============================================================
# DEFAULT ENGINE CHECK
# ============================================================

def structure_engine_module_check(
) -> Dict[str, Any]:

    contract = (
        validate_structure_contract_integrity()
    )

    operational = (
        structure_engine_operational_check()
    )

    return {
        "module": STRUCTURE_ENGINE,
        "version": STRUCTURE_ENGINE_VERSION,
        "module_ready": bool(
            contract["full_integrity"]
        ),
        "operational": bool(
            operational["operational"]
        ),
        "contract": contract,
        "operational_check": operational,
        "formula_registry": (
            structure_formula_registry_summary()
        ),
    }


# ============================================================
# FULL SELF CHECK
# ============================================================

def structure_engine_self_check(
) -> Dict[str, Any]:

    part4 = (
        structure_engine_part4_self_check()
    )

    module_check = (
        structure_engine_module_check()
    )

    request = create_structure_request(
        input_data=StructureInput(
            instrument_id="SELF_CHECK",
            symbol="SELF_CHECK",
            asset_class="EQUITY",
            timeframe=Timeframe.D1,
            timestamps=[
                datetime(
                    2026,
                    1,
                    1,
                    tzinfo=timezone.utc,
                ),
                datetime(
                    2026,
                    1,
                    2,
                    tzinfo=timezone.utc,
                ),
                datetime(
                    2026,
                    1,
                    3,
                    tzinfo=timezone.utc,
                ),
            ],
            opens=[
                100.0,
                102.0,
                104.0,
            ],
            highs=[
                103.0,
                105.0,
                107.0,
            ],
            lows=[
                99.0,
                101.0,
                103.0,
            ],
            closes=[
                102.0,
                104.0,
                106.0,
            ],
            volumes=[
                1000.0,
                1200.0,
                1300.0,
            ],
            source="SELF_CHECK",
        ),
        formula_id="",
        require_validated_formula=True,
    )

    result = execute_structure_request(
        request
    )

    # No formula exists in the default registry.
    # Therefore the engine must NOT fabricate intelligence.
    no_formula_safe = (
        result.status
        in {
            StructureStatus.DEGRADED,
            StructureStatus.INSUFFICIENT_DATA,
        }
        and result.structure is None
    )

    authority_safe = (
        not result.metadata.get(
            "engine_invented_formula",
            False,
        )
    )

    passed = (
        bool(
            part4["status"] == "PASS"
        )
        and bool(
            module_check["module_ready"]
        )
        and bool(
            module_check["operational"]
        )
        and no_formula_safe
        and authority_safe
    )

    return {
        "engine": STRUCTURE_ENGINE,
        "version": STRUCTURE_ENGINE_VERSION,
        "status": (
            "PASS"
            if passed
            else "FAIL"
        ),
        "part4_self_check": part4,
        "module_check": module_check,
        "default_execution_status": (
            result.status.value
        ),
        "default_registry_has_formula": (
            bool(
                get_structure_formula_registry()
            )
        ),
        "no_formula_fabrication": (
            no_formula_safe
        ),
        "authority_safe": authority_safe,
        "formula_pluggable": True,
        "research_formula_generated_here": False,
        "opportunity_generated_here": False,
        "decision_generated_here": False,
        "d13_modified": False,
        "risk_overridden": False,
        "cas_bypassed": False,
        "execution_authority": False,
    }


# ============================================================
# DEFAULT FACTORY
# ============================================================

def create_default_structure_engine_request(
) -> StructureEngineRequest:

    return create_structure_request(
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
            "formula_required": True,
            "research_first": True,
            "engine_invented_formula": False,
        },
    )


# ============================================================
# PUBLIC CONVENIENCE FUNCTIONS
# ============================================================

def analyze_single_timeframe_structure(
    input_data: StructureInput,
    *,
    formula_id: str,
    formula_version: str = "",
    require_validated_formula: bool = True,
) -> StructureEngineResult:

    request = create_structure_request(
        input_data=input_data,
        formula_id=formula_id,
        formula_version=formula_version,
        require_validated_formula=(
            require_validated_formula
        ),
    )

    return execute_structure_request(
        request
    )


def analyze_structure_timeframes(
    input_data: MultiTimeframeStructureInput,
    *,
    formula_ids: Optional[
        Dict[str, str]
    ] = None,
    formula_versions: Optional[
        Dict[str, str]
    ] = None,
    require_validated_formula: bool = True,
) -> StructureEngineResult:

    request = create_structure_request(
        multi_timeframe_input=input_data,
        require_validated_formula=(
            require_validated_formula
        ),
        metadata={
            "formula_ids": dict(
                formula_ids or {}
            ),
            "formula_versions": dict(
                formula_versions or {}
            ),
        },
    )

    return execute_structure_request(
        request
    )


# ============================================================
# FINAL ENGINE MANIFEST
# ============================================================

STRUCTURE_ENGINE_FINAL_MANIFEST = {
    "engine": STRUCTURE_ENGINE,
    "version": STRUCTURE_ENGINE_VERSION,

    "layer": "INTELLIGENCE_ENGINE",

    "role": (
        "MARKET_STRUCTURE_INTELLIGENCE"
    ),

    "primary_mission": (
        "Convert normalized market observations "
        "into validated structural intelligence."
    ),

    "supported_timeframes": [
        "5M",
        "15M",
        "1H",
        "4H",
        "1D",
        "1W",
        "1MN",
    ],

    "research_pipeline": [
        "RAW_MARKET_DATA",
        "NORMALIZED_MARKET_DATA",
        "STRUCTURE_INPUT",
        "VALIDATED_STRUCTURE_FORMULA",
        "STRUCTURE_ANALYSIS",
        "MULTI_TIMEFRAME_STRUCTURE",
        "DOWNSTREAM_INTELLIGENCE",
    ],

    "downstream_pipeline": [
        "ACCUMULATION_ENGINE",
        "DISTRIBUTION_ENGINE",
        "BOUNDARY_ENGINE",
        "BREAKOUT_ENGINE",
        "CONFIRMATION_ENGINE",
        "RELATIONSHIP_ENGINE",
        "REGIME_ENGINE",
        "OPPORTUNITY_ENGINE",
        "EQUITY_SCANNER",
        "FUTURE_SCANNER",
    ],

    "formula_policy": {
        "formula_pluggable": True,
        "formula_registry": True,
        "validated_formula_required": True,
        "formula_version_traceability": True,
        "default_formula": False,
        "guessed_formula": False,
        "silent_formula": False,
    },

    "authority": {
        "structure_analysis": True,
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
        "order_mutation": False,
        "position_mutation": False,
        "upstream_mutation": False,
    },

    "truth_policy": {
        "math_first": True,
        "research_first": True,
        "structure_is_not_signal": True,
        "structure_is_not_decision": True,
        "pattern_layer_can_validate": True,
        "pattern_layer_cannot_override_math": True,
        "scanner_does_not_invent_intelligence": True,
    },

    "future_research_hooks": [
        "SWING_STRUCTURE_FORMULA",
        "HH_HL_LH_LL_FORMALIZATION",
        "STRUCTURE_TRANSITION_FORMULA",
        "STRUCTURE_COMPRESSION_FORMULA",
        "STRUCTURE_EXPANSION_FORMULA",
        "STRUCTURE_STRENGTH_FORMULA",
        "MULTI_TIMEFRAME_RELATION_FORMULA",
        "STRUCTURE_INVALIDATION_FORMULA",
    ],
}


# ============================================================
# FINAL EXPORTS
# ============================================================

__all__.extend(
    [
        # Factories
        "create_structure_request",
        "create_default_structure_engine_request",

        # Execution
        "execute_structure_request",
        "analyze_single_timeframe_structure",
        "analyze_structure_timeframes",

        # Result helpers
        "structure_result_is_ready",
        "structure_result_has_validated_research",
        "structure_result_has_errors",

        # Summaries
        "summarize_structure_analysis",
        "summarize_multitimeframe_structure",
        "structure_result_summary",
        "structure_formula_registry_summary",

        # Integrity / diagnostics
        "validate_structure_contract_integrity",
        "structure_engine_module_check",
        "structure_engine_self_check",

        # Final manifest
        "STRUCTURE_ENGINE_FINAL_MANIFEST",
    ]
)