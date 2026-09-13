# ============================================================
# ROBOMLM_PLUS
# BOUNDARY INTELLIGENCE ENGINE
# PART 1 / 5
# ============================================================

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
)


# ============================================================
# ENGINE IDENTITY
# ============================================================

BOUNDARY_ENGINE = "ROBOMLM_PLUS_BOUNDARY_ENGINE"
BOUNDARY_ENGINE_VERSION = "1.0"
BOUNDARY_ENGINE_NAME = "Boundary Intelligence Engine"

BOUNDARY_ENGINE_DESCRIPTION = (
    "Research-driven boundary intelligence engine responsible for "
    "identifying and validating mathematically derived market boundaries "
    "from normalized market data, structure context, accumulation/"
    "distribution intelligence, and validated upstream research formulas."
)


# ============================================================
# AUTHORITY
# ============================================================

BOUNDARY_ENGINE_AUTHORITY = {
    # Core authority
    "boundary_analysis": True,
    "support_boundary_analysis": True,
    "resistance_boundary_analysis": True,
    "range_boundary_analysis": True,
    "breakout_boundary_analysis": True,
    "breakdown_boundary_analysis": True,
    "structure_context_consumption": True,
    "accumulation_context_consumption": True,
    "distribution_context_consumption": True,
    "multi_timeframe_boundary_analysis": True,
    "research_formula_consumption": True,

    # Formula authority
    "research_formula_generation": False,
    "fixed_formula_assumption": False,
    "guessed_formula": False,
    "silent_formula_substitution": False,
    "default_formula": False,

    # Downstream intelligence
    "breakout_generation": False,
    "breakdown_generation": False,
    "confirmation_generation": False,
    "relationship_generation": False,
    "opportunity_generation": False,
    "scanner_generation": False,

    # Decision authority
    "decision_generation": False,
    "d13_generation": False,

    # Safety / action authority
    "risk_generation": False,
    "cas_generation": False,
    "execution_generation": False,
    "order_generation": False,
    "position_generation": False,

    # Architecture protection
    "upstream_mutation": False,
}


# ============================================================
# ENUMS
# ============================================================

class BoundaryStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    READY = "READY"
    DEGRADED = "DEGRADED"
    INVALID = "INVALID"


class BoundaryType(str, Enum):
    SUPPORT = "SUPPORT"
    RESISTANCE = "RESISTANCE"
    RANGE_HIGH = "RANGE_HIGH"
    RANGE_LOW = "RANGE_LOW"
    BREAKOUT_BOUNDARY = "BREAKOUT_BOUNDARY"
    BREAKDOWN_BOUNDARY = "BREAKDOWN_BOUNDARY"
    INVALIDATION = "INVALIDATION"
    UNKNOWN = "UNKNOWN"


class BoundaryDirection(str, Enum):
    UPSIDE = "UPSIDE"
    DOWNSIDE = "DOWNSIDE"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"


class BoundaryState(str, Enum):
    UNKNOWN = "UNKNOWN"
    ABSENT = "ABSENT"
    POSSIBLE = "POSSIBLE"
    DEVELOPING = "DEVELOPING"
    ESTABLISHED = "ESTABLISHED"
    TESTING = "TESTING"
    BROKEN = "BROKEN"
    INVALIDATED = "INVALIDATED"


class BoundaryStrength(str, Enum):
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"
    UNKNOWN = "UNKNOWN"


class BoundaryConfidence(str, Enum):
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"
    UNKNOWN = "UNKNOWN"


class BoundaryPhase(str, Enum):
    FORMING = "FORMING"
    DEVELOPING = "DEVELOPING"
    ESTABLISHED = "ESTABLISHED"
    TESTING = "TESTING"
    BREAKING = "BREAKING"
    INVALIDATED = "INVALIDATED"
    UNKNOWN = "UNKNOWN"


class BoundaryRelation(str, Enum):
    ALIGNED = "ALIGNED"
    DIVERGENT = "DIVERGENT"
    CONFLICTING = "CONFLICTING"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"


class Timeframe(str, Enum):
    M5 = "M5"
    M15 = "M15"
    H1 = "H1"
    H4 = "H4"
    D1 = "D1"
    W1 = "W1"
    MN1 = "MN1"
    UNKNOWN = "UNKNOWN"


class BoundarySourceType(str, Enum):
    STRUCTURE = "STRUCTURE"
    ACCUMULATION = "ACCUMULATION"
    DISTRIBUTION = "DISTRIBUTION"
    RESEARCH_FORMULA = "RESEARCH_FORMULA"
    MULTI_TIMEFRAME = "MULTI_TIMEFRAME"
    UNKNOWN = "UNKNOWN"


# ============================================================
# CORE DATA MODELS
# ============================================================

@dataclass
class BoundaryPoint:
    price: float
    timestamp: Optional[Any] = None
    boundary_type: BoundaryType = BoundaryType.UNKNOWN
    direction: BoundaryDirection = BoundaryDirection.UNKNOWN
    source_type: BoundarySourceType = BoundarySourceType.UNKNOWN
    strength: BoundaryStrength = BoundaryStrength.UNKNOWN
    confidence: BoundaryConfidence = BoundaryConfidence.UNKNOWN
    validated: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BoundaryInput:
    instrument_id: Optional[str] = None
    symbol: Optional[str] = None
    asset_class: Optional[str] = None
    market_id: Optional[str] = None
    exchange: Optional[str] = None

    timeframe: Timeframe = Timeframe.UNKNOWN

    timestamps: List[Any] = field(default_factory=list)
    opens: List[float] = field(default_factory=list)
    highs: List[float] = field(default_factory=list)
    lows: List[float] = field(default_factory=list)
    closes: List[float] = field(default_factory=list)
    volumes: List[float] = field(default_factory=list)

    structure_context: Optional[Mapping[str, Any]] = None
    accumulation_context: Optional[Mapping[str, Any]] = None
    distribution_context: Optional[Mapping[str, Any]] = None

    source: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MultiTimeframeBoundaryInput:
    instrument_id: Optional[str] = None
    symbol: Optional[str] = None

    inputs: Dict[Timeframe, BoundaryInput] = field(
        default_factory=dict
    )

    requested_timeframes: List[Timeframe] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BoundaryMeasurement:
    name: str
    value: Any
    unit: Optional[str] = None
    interpretation: Optional[str] = None

    source: BoundarySourceType = BoundarySourceType.UNKNOWN

    formula_id: Optional[str] = None
    formula_version: Optional[str] = None
    research_validated: bool = False

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BoundaryWindow:
    observation_count: int = 0

    first_close: Optional[float] = None
    last_close: Optional[float] = None

    highest_price: Optional[float] = None
    lowest_price: Optional[float] = None

    total_volume: Optional[float] = None
    average_volume: Optional[float] = None

    start_timestamp: Optional[Any] = None
    end_timestamp: Optional[Any] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# BOUNDARY ANALYSIS
# ============================================================

@dataclass
class BoundaryAnalysis:
    status: BoundaryStatus = BoundaryStatus.UNKNOWN

    boundary_state: BoundaryState = BoundaryState.UNKNOWN
    boundary_type: BoundaryType = BoundaryType.UNKNOWN
    direction: BoundaryDirection = BoundaryDirection.UNKNOWN
    phase: BoundaryPhase = BoundaryPhase.UNKNOWN

    strength: BoundaryStrength = BoundaryStrength.UNKNOWN
    confidence: BoundaryConfidence = BoundaryConfidence.UNKNOWN

    timeframe: Timeframe = Timeframe.UNKNOWN

    instrument_id: Optional[str] = None
    symbol: Optional[str] = None

    window: Optional[BoundaryWindow] = None

    boundaries: List[BoundaryPoint] = field(
        default_factory=list
    )

    measurements: List[BoundaryMeasurement] = field(
        default_factory=list
    )

    primary_boundary: Optional[BoundaryPoint] = None

    formula_id: Optional[str] = None
    formula_version: Optional[str] = None
    formula_name: Optional[str] = None
    formula_owner: Optional[str] = None
    formula_registry_key: Optional[str] = None

    research_validated: bool = False

    # Boundary intelligence is NOT a trade signal.
    is_signal: bool = False
    is_opportunity: bool = False
    is_decision: bool = False

    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# MULTI-TIMEFRAME ANALYSIS
# ============================================================

@dataclass
class MultiTimeframeBoundary:
    status: BoundaryStatus = BoundaryStatus.UNKNOWN

    instrument_id: Optional[str] = None
    symbol: Optional[str] = None

    analyses: Dict[Timeframe, BoundaryAnalysis] = field(
        default_factory=dict
    )

    relation: BoundaryRelation = BoundaryRelation.UNKNOWN

    dominant_boundary_type: BoundaryType = BoundaryType.UNKNOWN
    dominant_direction: BoundaryDirection = BoundaryDirection.UNKNOWN

    strongest_boundary: Optional[BoundaryPoint] = None

    average_confidence: BoundaryConfidence = (
        BoundaryConfidence.UNKNOWN
    )

    research_validated: bool = False

    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# ENGINE RESULT
# ============================================================

@dataclass
class BoundaryEngineResult:
    status: BoundaryStatus = BoundaryStatus.UNKNOWN

    analysis: Optional[BoundaryAnalysis] = None

    multi_timeframe: Optional[MultiTimeframeBoundary] = None

    instrument_id: Optional[str] = None
    symbol: Optional[str] = None

    research_validated: bool = False

    formula_id: Optional[str] = None
    formula_version: Optional[str] = None

    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BoundaryEngineRequest:
    input_data: Optional[BoundaryInput] = None

    multi_timeframe_input: Optional[
        MultiTimeframeBoundaryInput
    ] = None

    formula_id: Optional[str] = None
    formula_version: Optional[str] = None

    formula_map: Dict[Timeframe, str] = field(
        default_factory=dict
    )

    formula_version_map: Dict[Timeframe, str] = field(
        default_factory=dict
    )

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# IMMUTABLE SNAPSHOT
# ============================================================

@dataclass(frozen=True)
class BoundaryEngineSnapshot:
    engine: str
    version: str

    instrument_id: Optional[str]
    symbol: Optional[str]

    status: BoundaryStatus

    formula_id: Optional[str]
    formula_version: Optional[str]

    research_validated: bool

    analysis: Optional[BoundaryAnalysis]
    multi_timeframe: Optional[MultiTimeframeBoundary]

    metadata: Tuple[Tuple[str, Any], ...] = ()


# ============================================================
# ENGINE CONTRACT
# ============================================================

BOUNDARY_ENGINE_CONTRACT = {
    "engine": BOUNDARY_ENGINE,
    "version": BOUNDARY_ENGINE_VERSION,

    "layer": "INTELLIGENCE_ENGINE",
    "role": "BOUNDARY_INTELLIGENCE",

    "authority_owner": (
        "UPSTREAM_BOUNDARY_INTELLIGENCE"
    ),

    "inputs": [
        "NORMALIZED_OHLCV",
        "STRUCTURE_INTELLIGENCE",
        "ACCUMULATION_INTELLIGENCE",
        "DISTRIBUTION_INTELLIGENCE",
        "MULTI_TIMEFRAME_CONTEXT",
        "RESEARCH_FORMULA_REGISTRY",
        "RESEARCH_VALIDATION_METADATA",
    ],

    "outputs": [
        "SUPPORT_BOUNDARY",
        "RESISTANCE_BOUNDARY",
        "RANGE_BOUNDARY",
        "BREAKOUT_BOUNDARY",
        "BREAKDOWN_BOUNDARY",
        "INVALIDATION_BOUNDARY",
        "MULTI_TIMEFRAME_BOUNDARY",
        "BOUNDARY_ANALYSIS",
        "BOUNDARY_ENGINE_RESULT",
        "BOUNDARY_ENGINE_SNAPSHOT",
    ],

    "supported_timeframes": [
        timeframe.value
        for timeframe in Timeframe
        if timeframe != Timeframe.UNKNOWN
    ],

    "formula_policy": {
        "pluggable": True,
        "registry_based": True,
        "explicit_selection": True,
        "validated_required": True,
        "version_traceability": True,
        "default_formula_allowed": False,
        "guessing_allowed": False,
        "silent_substitution_allowed": False,
        "engine_generates_formula": False,
    },

    "downstream_consumers": [
        "BREAKOUT_ENGINE",
        "CONFIRMATION_ENGINE",
        "RELATIONSHIP_ENGINE",
        "OPPORTUNITY_ENGINE",
        "EQUITY_SCANNER",
        "FUTURE_SCANNER",
    ],

    "forbidden_responsibilities": [
        "FORMULA_GENERATION",
        "BREAKOUT_DECISION",
        "SIGNAL_GENERATION",
        "OPPORTUNITY_GENERATION",
        "DECISION_GENERATION",
        "D13_GENERATION",
        "RISK_GENERATION",
        "CAS_GENERATION",
        "EXECUTION",
        "ORDER_GENERATION",
        "POSITION_GENERATION",
        "UPSTREAM_MUTATION",
    ],
}


# ============================================================
# AUTHORITY VALIDATION
# ============================================================

def validate_boundary_authority() -> bool:
    """
    Validate that Boundary Engine authority is limited to
    boundary intelligence and research-formula consumption.
    """

    required_true = [
        "boundary_analysis",
        "support_boundary_analysis",
        "resistance_boundary_analysis",
        "range_boundary_analysis",
        "breakout_boundary_analysis",
        "breakdown_boundary_analysis",
        "research_formula_consumption",
    ]

    required_false = [
        "research_formula_generation",
        "fixed_formula_assumption",
        "guessed_formula",
        "silent_formula_substitution",
        "default_formula",
        "breakout_generation",
        "breakdown_generation",
        "confirmation_generation",
        "opportunity_generation",
        "scanner_generation",
        "decision_generation",
        "d13_generation",
        "risk_generation",
        "cas_generation",
        "execution_generation",
        "order_generation",
        "position_generation",
        "upstream_mutation",
    ]

    return (
        all(
            BOUNDARY_ENGINE_AUTHORITY.get(key) is True
            for key in required_true
        )
        and
        all(
            BOUNDARY_ENGINE_AUTHORITY.get(key) is False
            for key in required_false
        )
    )


# ============================================================
# ENGINE SUMMARY
# ============================================================

def boundary_engine_summary() -> Dict[str, Any]:
    return {
        "engine": BOUNDARY_ENGINE,
        "version": BOUNDARY_ENGINE_VERSION,
        "name": BOUNDARY_ENGINE_NAME,
        "description": BOUNDARY_ENGINE_DESCRIPTION,
        "layer": BOUNDARY_ENGINE_CONTRACT["layer"],
        "role": BOUNDARY_ENGINE_CONTRACT["role"],
        "authority_owner": (
            BOUNDARY_ENGINE_CONTRACT["authority_owner"]
        ),
        "authority_valid": validate_boundary_authority(),
        "formula_policy": dict(
            BOUNDARY_ENGINE_CONTRACT["formula_policy"]
        ),
        "supported_timeframes": list(
            BOUNDARY_ENGINE_CONTRACT["supported_timeframes"]
        ),
        "downstream_consumers": list(
            BOUNDARY_ENGINE_CONTRACT["downstream_consumers"]
        ),
        "forbidden_responsibilities": list(
            BOUNDARY_ENGINE_CONTRACT[
                "forbidden_responsibilities"
            ]
        ),
    }


# ============================================================
# PART 1 CONTRACT CHECK
# ============================================================

def boundary_part1_contract_check() -> Dict[str, Any]:
    checks = {
        "engine_identity": bool(
            BOUNDARY_ENGINE
            and BOUNDARY_ENGINE_VERSION
            and BOUNDARY_ENGINE_NAME
        ),
        "authority_valid": validate_boundary_authority(),
        "contract_available": bool(
            BOUNDARY_ENGINE_CONTRACT
        ),
        "boundary_input_available": True,
        "boundary_analysis_available": True,
        "mtf_boundary_available": True,
        "engine_result_available": True,
        "request_available": True,
        "snapshot_available": True,
        "formula_policy_available": bool(
            BOUNDARY_ENGINE_CONTRACT.get(
                "formula_policy"
            )
        ),
        "no_formula_generation": (
            BOUNDARY_ENGINE_AUTHORITY[
                "research_formula_generation"
            ] is False
        ),
        "no_guessed_formula": (
            BOUNDARY_ENGINE_AUTHORITY[
                "guessed_formula"
            ] is False
        ),
        "no_decision_authority": (
            BOUNDARY_ENGINE_AUTHORITY[
                "decision_generation"
            ] is False
            and
            BOUNDARY_ENGINE_AUTHORITY[
                "d13_generation"
            ] is False
        ),
        "no_execution_authority": (
            BOUNDARY_ENGINE_AUTHORITY[
                "execution_generation"
            ] is False
        ),
    }

    errors = [
        key
        for key, value in checks.items()
        if not value
    ]

    return {
        "engine": BOUNDARY_ENGINE,
        "version": BOUNDARY_ENGINE_VERSION,
        "part": 1,
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "checks": checks,
        "errors": errors,
    }
# ============================================================
# BOUNDARY INTELLIGENCE ENGINE
# PART 2 / 5
# Normalization + Input Validation + Formula Registry
# ============================================================


# ============================================================
# NORMALIZATION HELPERS
# ============================================================

def _normalize_boundary_series(
    values: Optional[Sequence[Any]],
) -> List[Any]:
    """
    Normalize a market-data series without creating intelligence.

    Only converts the supplied sequence into a safe list.
    No interpolation, prediction, or formula is applied.
    """

    if values is None:
        return []

    if isinstance(values, (str, bytes)):
        return [values]

    try:
        return list(values)
    except TypeError:
        return [values]


def _normalize_boundary_timestamps(
    values: Optional[Sequence[Any]],
) -> List[Any]:
    """
    Normalize timestamps without altering their semantic meaning.
    """

    return _normalize_boundary_series(values)


def normalize_boundary_input(
    input_data: BoundaryInput,
) -> BoundaryInput:
    """
    Normalize BoundaryInput.

    This function does NOT calculate support, resistance,
    breakout levels, or any market intelligence.
    """

    if not isinstance(input_data, BoundaryInput):
        raise TypeError(
            "input_data must be BoundaryInput"
        )

    metadata = dict(input_data.metadata or {})
    metadata["normalized"] = True
    metadata["normalization_engine"] = BOUNDARY_ENGINE

    return replace(
        input_data,
        timestamps=_normalize_boundary_timestamps(
            input_data.timestamps
        ),
        opens=_normalize_boundary_series(
            input_data.opens
        ),
        highs=_normalize_boundary_series(
            input_data.highs
        ),
        lows=_normalize_boundary_series(
            input_data.lows
        ),
        closes=_normalize_boundary_series(
            input_data.closes
        ),
        volumes=_normalize_boundary_series(
            input_data.volumes
        ),
        metadata=metadata,
    )


def normalize_multitimeframe_boundary_input(
    input_data: MultiTimeframeBoundaryInput,
) -> MultiTimeframeBoundaryInput:
    """
    Normalize all supplied timeframe inputs.
    """

    if not isinstance(
        input_data,
        MultiTimeframeBoundaryInput,
    ):
        raise TypeError(
            "input_data must be MultiTimeframeBoundaryInput"
        )

    normalized_inputs: Dict[
        Timeframe,
        BoundaryInput,
    ] = {}

    for timeframe, boundary_input in (
        input_data.inputs or {}
    ).items():
        normalized_inputs[timeframe] = (
            normalize_boundary_input(boundary_input)
        )

    metadata = dict(input_data.metadata or {})
    metadata["normalized"] = True
    metadata["normalization_engine"] = BOUNDARY_ENGINE

    return replace(
        input_data,
        inputs=normalized_inputs,
        requested_timeframes=list(
            input_data.requested_timeframes or []
        ),
        metadata=metadata,
    )


# ============================================================
# INPUT VALIDATION
# ============================================================

def validate_boundary_input(
    input_data: BoundaryInput,
) -> Dict[str, Any]:
    """
    Validate structural integrity of boundary input.

    Validation does not determine a boundary.
    """

    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(input_data, BoundaryInput):
        return {
            "valid": False,
            "ready": False,
            "errors": [
                "input_data must be BoundaryInput"
            ],
            "warnings": [],
        }

    if not input_data.instrument_id and not input_data.symbol:
        errors.append(
            "instrument_id or symbol is required"
        )

    if not input_data.asset_class:
        errors.append("asset_class is required")

    if not input_data.market_id:
        errors.append("market_id is required")

    series = {
        "opens": input_data.opens,
        "highs": input_data.highs,
        "lows": input_data.lows,
        "closes": input_data.closes,
    }

    present_lengths = [
        len(values)
        for values in series.values()
        if values
    ]

    if not present_lengths:
        errors.append(
            "at least one OHLC series is required"
        )

    expected_length = (
        present_lengths[0]
        if present_lengths
        else 0
    )

    for name, values in series.items():
        if values and len(values) != expected_length:
            errors.append(
                f"{name} length does not match OHLC length"
            )

    if input_data.volumes:
        if len(input_data.volumes) != expected_length:
            errors.append(
                "volumes length does not match OHLC length"
            )

        for index, volume in enumerate(
            input_data.volumes
        ):
            try:
                if float(volume) < 0:
                    errors.append(
                        f"negative volume at index {index}"
                    )
            except (TypeError, ValueError):
                errors.append(
                    f"invalid volume at index {index}"
                )
    else:
        warnings.append(
            "volume data is unavailable"
        )

    if input_data.timestamps:
        if len(input_data.timestamps) != expected_length:
            errors.append(
                "timestamps length does not match OHLC length"
            )
    else:
        warnings.append(
            "timestamp data is unavailable"
        )

    if input_data.highs and input_data.lows:
        for index, (high, low) in enumerate(
            zip(input_data.highs, input_data.lows)
        ):
            try:
                high_value = float(high)
                low_value = float(low)

                if high_value <= 0 or low_value <= 0:
                    errors.append(
                        f"non-positive price at index {index}"
                    )

                if high_value < low_value:
                    errors.append(
                        f"high below low at index {index}"
                    )

            except (TypeError, ValueError):
                errors.append(
                    f"invalid high/low value at index {index}"
                )

    for name, values in series.items():
        for index, value in enumerate(values):
            try:
                if float(value) <= 0:
                    errors.append(
                        f"non-positive {name} at index {index}"
                    )
            except (TypeError, ValueError):
                errors.append(
                    f"invalid {name} at index {index}"
                )

    return {
        "valid": len(errors) == 0,
        "ready": (
            len(errors) == 0
            and expected_length > 0
        ),
        "observation_count": expected_length,
        "errors": errors,
        "warnings": warnings,
    }


def boundary_input_readiness(
    input_data: BoundaryInput,
) -> Dict[str, Any]:
    """
    Describe whether enough input exists to request
    boundary intelligence.

    This function does not manufacture missing data.
    """

    validation = validate_boundary_input(
        input_data
    )

    missing: List[str] = []

    if not input_data.opens:
        missing.append("opens")

    if not input_data.highs:
        missing.append("highs")

    if not input_data.lows:
        missing.append("lows")

    if not input_data.closes:
        missing.append("closes")

    if not input_data.volumes:
        missing.append("volumes")

    if not input_data.timestamps:
        missing.append("timestamps")

    if (
        input_data.structure_context is None
    ):
        missing.append("structure_context")

    if (
        input_data.accumulation_context is None
    ):
        missing.append("accumulation_context")

    if (
        input_data.distribution_context is None
    ):
        missing.append("distribution_context")

    return {
        "ready": bool(validation["ready"]),
        "valid": bool(validation["valid"]),
        "observation_count": validation.get(
            "observation_count",
            0,
        ),
        "missing": missing,
        "errors": list(
            validation.get("errors", [])
        ),
        "warnings": list(
            validation.get("warnings", [])
        ),
        "context": {
            "structure_available": (
                input_data.structure_context
                is not None
            ),
            "accumulation_available": (
                input_data.accumulation_context
                is not None
            ),
            "distribution_available": (
                input_data.distribution_context
                is not None
            ),
        },
    }


# ============================================================
# DESCRIPTIVE MARKET WINDOW
# ============================================================

def build_boundary_window(
    input_data: BoundaryInput,
) -> BoundaryWindow:
    """
    Build descriptive statistics from supplied data.

    IMPORTANT:
    This is NOT boundary intelligence.

    No support/resistance formula is applied here.
    """

    normalized = normalize_boundary_input(
        input_data
    )

    closes = [
        float(value)
        for value in normalized.closes
    ]

    highs = [
        float(value)
        for value in normalized.highs
    ]

    lows = [
        float(value)
        for value in normalized.lows
    ]

    volumes = [
        float(value)
        for value in normalized.volumes
    ]

    observation_count = max(
        len(closes),
        len(highs),
        len(lows),
    )

    first_close = (
        closes[0]
        if closes
        else None
    )

    last_close = (
        closes[-1]
        if closes
        else None
    )

    highest_price = (
        max(highs)
        if highs
        else None
    )

    lowest_price = (
        min(lows)
        if lows
        else None
    )

    total_volume = (
        sum(volumes)
        if volumes
        else None
    )

    average_volume = (
        total_volume / len(volumes)
        if volumes
        else None
    )

    timestamps = normalized.timestamps

    start_timestamp = (
        timestamps[0]
        if timestamps
        else None
    )

    end_timestamp = (
        timestamps[-1]
        if timestamps
        else None
    )

    return BoundaryWindow(
        observation_count=observation_count,
        first_close=first_close,
        last_close=last_close,
        highest_price=highest_price,
        lowest_price=lowest_price,
        total_volume=total_volume,
        average_volume=average_volume,
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
        metadata={
            "descriptive_only": True,
            "intelligence_generated": False,
        },
    )


# ============================================================
# MEASUREMENT FACTORY
# ============================================================

def create_boundary_measurement(
    name: str,
    value: Any,
    unit: Optional[str] = None,
    interpretation: Optional[str] = None,
    source: BoundarySourceType = (
        BoundarySourceType.UNKNOWN
    ),
    formula_id: Optional[str] = None,
    formula_version: Optional[str] = None,
    research_validated: bool = False,
    metadata: Optional[Mapping[str, Any]] = None,
) -> BoundaryMeasurement:
    """
    Create a traceable boundary measurement.

    A measurement alone is not a signal or decision.
    """

    return BoundaryMeasurement(
        name=name,
        value=value,
        unit=unit,
        interpretation=interpretation,
        source=source,
        formula_id=formula_id,
        formula_version=formula_version,
        research_validated=research_validated,
        metadata=dict(metadata or {}),
    )


# ============================================================
# TIMEFRAME NORMALIZATION
# ============================================================

def normalize_requested_boundary_timeframes(
    timeframes: Optional[
        Iterable[Any]
    ],
) -> List[Timeframe]:
    """
    Normalize requested timeframe values.
    """

    if timeframes is None:
        return []

    result: List[Timeframe] = []

    for value in timeframes:
        if isinstance(value, Timeframe):
            timeframe = value
        else:
            try:
                timeframe = Timeframe(
                    str(value).upper()
                )
            except ValueError:
                timeframe = Timeframe.UNKNOWN

        if timeframe not in result:
            result.append(timeframe)

    return result


def build_multitimeframe_boundary_input(
    inputs: Mapping[Any, BoundaryInput],
    instrument_id: Optional[str] = None,
    symbol: Optional[str] = None,
    requested_timeframes: Optional[
        Iterable[Any]
    ] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> MultiTimeframeBoundaryInput:
    """
    Build normalized multi-timeframe boundary input.
    """

    normalized_inputs: Dict[
        Timeframe,
        BoundaryInput,
    ] = {}

    for key, value in inputs.items():
        if not isinstance(value, BoundaryInput):
            raise TypeError(
                "all timeframe inputs must be BoundaryInput"
            )

        if isinstance(key, Timeframe):
            timeframe = key
        else:
            try:
                timeframe = Timeframe(
                    str(key).upper()
                )
            except ValueError:
                timeframe = Timeframe.UNKNOWN

        normalized_inputs[timeframe] = (
            normalize_boundary_input(value)
        )

    normalized_requested = (
        normalize_requested_boundary_timeframes(
            requested_timeframes
        )
    )

    if not normalized_requested:
        normalized_requested = list(
            normalized_inputs.keys()
        )

    return MultiTimeframeBoundaryInput(
        instrument_id=instrument_id,
        symbol=symbol,
        inputs=normalized_inputs,
        requested_timeframes=normalized_requested,
        metadata=dict(metadata or {}),
    )


# ============================================================
# RESEARCH FORMULA DESCRIPTOR
# ============================================================

@dataclass(frozen=True)
class BoundaryFormulaDescriptor:
    """
    Metadata describing an upstream validated formula.

    This descriptor does not contain the formula implementation.
    """

    formula_id: str
    formula_version: str

    name: str
    description: str

    supported_asset_classes: Tuple[
        str, ...
    ] = ()

    supported_timeframes: Tuple[
        str, ...
    ] = ()

    validated: bool = False
    enabled: bool = True

    owner: str = (
        "UPSTREAM_BOUNDARY_INTELLIGENCE"
    )

    metadata: Tuple[
        Tuple[str, Any], ...
    ] = ()


# ============================================================
# FORMULA PROVIDER
# ============================================================

class BoundaryFormulaProvider(ABC):
    """
    Abstract provider for validated upstream
    boundary research formulas.
    """

    @abstractmethod
    def describe(
        self,
    ) -> BoundaryFormulaDescriptor:
        """
        Return formula metadata and validation state.
        """
        raise NotImplementedError

    @abstractmethod
    def analyze(
        self,
        input_data: BoundaryInput,
    ) -> BoundaryAnalysis:
        """
        Execute an already validated research formula.

        Boundary Engine does not define the mathematical
        formula itself.
        """
        raise NotImplementedError


# ============================================================
# FORMULA REGISTRY
# ============================================================

class BoundaryFormulaRegistry:
    """
    Registry for explicit, versioned, validated
    upstream boundary formulas.
    """

    def __init__(self) -> None:
        self._providers: Dict[
            str,
            BoundaryFormulaProvider,
        ] = {}

    def register(
        self,
        provider: BoundaryFormulaProvider,
        *,
        replace_existing: bool = False,
    ) -> BoundaryFormulaDescriptor:
        if not isinstance(
            provider,
            BoundaryFormulaProvider,
        ):
            raise TypeError(
                "provider must implement "
                "BoundaryFormulaProvider"
            )

        descriptor = provider.describe()

        if not isinstance(
            descriptor,
            BoundaryFormulaDescriptor,
        ):
            raise TypeError(
                "provider.describe() must return "
                "BoundaryFormulaDescriptor"
            )

        key = descriptor.formula_id

        if (
            key in self._providers
            and not replace_existing
        ):
            raise ValueError(
                f"formula already registered: {key}"
            )

        self._providers[key] = provider

        return descriptor

    def get(
        self,
        formula_id: str,
    ) -> Optional[BoundaryFormulaProvider]:
        return self._providers.get(formula_id)

    def unregister(
        self,
        formula_id: str,
    ) -> bool:
        if formula_id in self._providers:
            del self._providers[formula_id]
            return True

        return False

    def descriptors(
        self,
    ) -> List[BoundaryFormulaDescriptor]:
        result = []

        for provider in self._providers.values():
            descriptor = provider.describe()

            if isinstance(
                descriptor,
                BoundaryFormulaDescriptor,
            ):
                result.append(descriptor)

        return result

    def clear(self) -> None:
        self._providers.clear()

    def __len__(self) -> int:
        return len(self._providers)


# ============================================================
# DEFAULT REGISTRY
# ============================================================

_DEFAULT_BOUNDARY_FORMULA_REGISTRY = (
    BoundaryFormulaRegistry()
)


def get_default_boundary_formula_registry() -> (
    BoundaryFormulaRegistry
):
    return _DEFAULT_BOUNDARY_FORMULA_REGISTRY


# ============================================================
# FORMULA RESOLUTION
# ============================================================

def resolve_boundary_formula(
    formula_id: Optional[str],
    registry: Optional[
        BoundaryFormulaRegistry
    ] = None,
) -> Optional[BoundaryFormulaProvider]:
    """
    Resolve an explicitly requested formula.

    No default formula is selected.
    """

    if not formula_id:
        return None

    registry = (
        registry
        or get_default_boundary_formula_registry()
    )

    return registry.get(formula_id)


def boundary_formula_readiness(
    registry: Optional[
        BoundaryFormulaRegistry
    ] = None,
) -> Dict[str, Any]:
    """
    Inspect formula registry state without creating
    any intelligence.
    """

    registry = (
        registry
        or get_default_boundary_formula_registry()
    )

    descriptors = registry.descriptors()

    validated = [
        descriptor
        for descriptor in descriptors
        if descriptor.validated
        and descriptor.enabled
    ]

    return {
        "registry_available": True,
        "formula_count": len(descriptors),
        "validated_formula_count": len(
            validated
        ),
        "validated_formula_available": bool(
            validated
        ),
        "formulas": [
            {
                "formula_id": descriptor.formula_id,
                "formula_version": (
                    descriptor.formula_version
                ),
                "name": descriptor.name,
                "validated": descriptor.validated,
                "enabled": descriptor.enabled,
                "owner": descriptor.owner,
            }
            for descriptor in descriptors
        ],
    }


# ============================================================
# MULTI-TIMEFRAME INPUT VALIDATION
# ============================================================

def validate_multitimeframe_boundary_input(
    input_data: MultiTimeframeBoundaryInput,
) -> Dict[str, Any]:
    """
    Validate all timeframe inputs independently.
    """

    if not isinstance(
        input_data,
        MultiTimeframeBoundaryInput,
    ):
        return {
            "valid": False,
            "ready": False,
            "errors": [
                "input_data must be "
                "MultiTimeframeBoundaryInput"
            ],
            "warnings": [],
            "timeframes": {},
        }

    errors: List[str] = []
    warnings: List[str] = []
    timeframe_results: Dict[
        str,
        Any,
    ] = {}

    if not input_data.inputs:
        errors.append(
            "at least one timeframe input is required"
        )

    for timeframe, boundary_input in (
        input_data.inputs.items()
    ):
        result = validate_boundary_input(
            boundary_input
        )

        timeframe_results[
            timeframe.value
            if isinstance(timeframe, Timeframe)
            else str(timeframe)
        ] = result

        errors.extend(
            [
                (
                    f"{timeframe}: {message}"
                )
                for message in result.get(
                    "errors",
                    [],
                )
            ]
        )

        warnings.extend(
            [
                (
                    f"{timeframe}: {message}"
                )
                for message in result.get(
                    "warnings",
                    [],
                )
            ]
        )

    return {
        "valid": len(errors) == 0,
        "ready": (
            len(errors) == 0
            and bool(input_data.inputs)
        ),
        "errors": errors,
        "warnings": warnings,
        "timeframes": timeframe_results,
    }


# ============================================================
# PART 2 CONTRACT CHECK
# ============================================================

def boundary_part2_contract_check(
    registry: Optional[
        BoundaryFormulaRegistry
    ] = None,
) -> Dict[str, Any]:
    registry = (
        registry
        or get_default_boundary_formula_registry()
    )

    checks = {
        "normalization_available": callable(
            normalize_boundary_input
        ),
        "mtf_normalization_available": callable(
            normalize_multitimeframe_boundary_input
        ),
        "input_validation_available": callable(
            validate_boundary_input
        ),
        "mtf_validation_available": callable(
            validate_multitimeframe_boundary_input
        ),
        "readiness_available": callable(
            boundary_input_readiness
        ),
        "window_builder_available": callable(
            build_boundary_window
        ),
        "measurement_factory_available": callable(
            create_boundary_measurement
        ),
        "formula_descriptor_available": True,
        "formula_provider_available": True,
        "formula_registry_available": isinstance(
            registry,
            BoundaryFormulaRegistry,
        ),
        "formula_resolution_available": callable(
            resolve_boundary_formula
        ),
        "no_default_formula": (
            BOUNDARY_ENGINE_AUTHORITY[
                "default_formula"
            ] is False
        ),
        "no_formula_guessing": (
            BOUNDARY_ENGINE_AUTHORITY[
                "guessed_formula"
            ] is False
        ),
        "no_silent_substitution": (
            BOUNDARY_ENGINE_AUTHORITY[
                "silent_formula_substitution"
            ] is False
        ),
    }

    errors = [
        key
        for key, value in checks.items()
        if not value
    ]

    return {
        "engine": BOUNDARY_ENGINE,
        "version": BOUNDARY_ENGINE_VERSION,
        "part": 2,
        "valid": not errors,
        "status": (
            "PASS"
            if not errors
            else "FAIL"
        ),
        "checks": checks,
        "errors": errors,
        "formula_registry": (
            boundary_formula_readiness(registry)
        ),
    }
# ============================================================
# BOUNDARY INTELLIGENCE ENGINE
# PART 3 / 5
# Formula Resolution + Boundary Analysis + MTF Orchestration
# ============================================================


# ============================================================
# FORMULA METADATA
# ============================================================

def _boundary_formula_metadata(
    descriptor: BoundaryFormulaDescriptor,
) -> Dict[str, Any]:
    """
    Convert validated formula descriptor into traceability
    metadata.

    The engine records provenance but does not alter the
    mathematical formula.
    """

    return {
        "formula_id": descriptor.formula_id,
        "formula_version": descriptor.formula_version,
        "formula_name": descriptor.name,
        "formula_owner": descriptor.owner,
        "formula_registry_key": descriptor.formula_id,
        "research_validated": descriptor.validated,
        "formula_enabled": descriptor.enabled,
        "upstream_research_formula": True,
        "engine_generated_formula": False,
    }


# ============================================================
# SINGLE-TIMEFRAME BOUNDARY ANALYSIS
# ============================================================

def analyze_boundary(
    input_data: BoundaryInput,
    formula_id: Optional[str] = None,
    formula_version: Optional[str] = None,
    registry: Optional[
        BoundaryFormulaRegistry
    ] = None,
) -> BoundaryEngineResult:
    """
    Execute a validated upstream boundary formula.

    Boundary Engine responsibilities:
        - normalize input
        - validate input
        - resolve explicit formula
        - verify formula validation/version
        - execute provider
        - preserve traceability

    Boundary Engine does NOT:
        - invent formulas
        - guess support/resistance
        - create signals
        - create opportunities
        - make decisions
        - generate D13
    """

    registry = (
        registry
        or get_default_boundary_formula_registry()
    )

    if not isinstance(
        input_data,
        BoundaryInput,
    ):
        return BoundaryEngineResult(
            status=BoundaryStatus.INVALID,
            research_validated=False,
            errors=[
                "input_data must be BoundaryInput"
            ],
        )

    normalized = normalize_boundary_input(
        input_data
    )

    validation = validate_boundary_input(
        normalized
    )

    if not validation["valid"]:
        return BoundaryEngineResult(
            status=BoundaryStatus.INVALID,
            instrument_id=normalized.instrument_id,
            symbol=normalized.symbol,
            research_validated=False,
            warnings=list(
                validation.get(
                    "warnings",
                    [],
                )
            ),
            errors=list(
                validation.get(
                    "errors",
                    [],
                )
            ),
            metadata={
                "input_validation_failed": True,
                "intelligence_generated": False,
            },
        )

    if not formula_id:
        return BoundaryEngineResult(
            status=BoundaryStatus.DEGRADED,
            instrument_id=normalized.instrument_id,
            symbol=normalized.symbol,
            research_validated=False,
            warnings=[
                "no boundary research formula selected"
            ],
            metadata={
                "formula_required": True,
                "intelligence_generated": False,
            },
        )

    provider = resolve_boundary_formula(
        formula_id=formula_id,
        registry=registry,
    )

    if provider is None:
        return BoundaryEngineResult(
            status=BoundaryStatus.DEGRADED,
            instrument_id=normalized.instrument_id,
            symbol=normalized.symbol,
            research_validated=False,
            errors=[
                f"boundary formula not found: {formula_id}"
            ],
            metadata={
                "formula_resolution_failed": True,
                "intelligence_generated": False,
            },
        )

    try:
        descriptor = provider.describe()
    except Exception as exc:
        return BoundaryEngineResult(
            status=BoundaryStatus.INVALID,
            instrument_id=normalized.instrument_id,
            symbol=normalized.symbol,
            research_validated=False,
            errors=[
                "formula descriptor failed: "
                + str(exc)
            ],
            metadata={
                "formula_descriptor_error": True,
            },
        )

    if not isinstance(
        descriptor,
        BoundaryFormulaDescriptor,
    ):
        return BoundaryEngineResult(
            status=BoundaryStatus.INVALID,
            instrument_id=normalized.instrument_id,
            symbol=normalized.symbol,
            research_validated=False,
            errors=[
                "formula provider returned invalid descriptor"
            ],
        )

    if not descriptor.enabled:
        return BoundaryEngineResult(
            status=BoundaryStatus.DEGRADED,
            instrument_id=normalized.instrument_id,
            symbol=normalized.symbol,
            research_validated=False,
            warnings=[
                "selected boundary formula is disabled"
            ],
            formula_id=descriptor.formula_id,
            formula_version=descriptor.formula_version,
        )

    if not descriptor.validated:
        return BoundaryEngineResult(
            status=BoundaryStatus.DEGRADED,
            instrument_id=normalized.instrument_id,
            symbol=normalized.symbol,
            research_validated=False,
            warnings=[
                "selected boundary formula is not "
                "research validated"
            ],
            formula_id=descriptor.formula_id,
            formula_version=descriptor.formula_version,
        )

    if (
        formula_version is not None
        and formula_version
        != descriptor.formula_version
    ):
        return BoundaryEngineResult(
            status=BoundaryStatus.DEGRADED,
            instrument_id=normalized.instrument_id,
            symbol=normalized.symbol,
            research_validated=False,
            errors=[
                "boundary formula version mismatch: "
                f"requested={formula_version}, "
                f"available={descriptor.formula_version}"
            ],
            formula_id=descriptor.formula_id,
            formula_version=descriptor.formula_version,
        )

    try:
        analysis = provider.analyze(
            normalized
        )
    except Exception as exc:
        return BoundaryEngineResult(
            status=BoundaryStatus.INVALID,
            instrument_id=normalized.instrument_id,
            symbol=normalized.symbol,
            research_validated=False,
            formula_id=descriptor.formula_id,
            formula_version=descriptor.formula_version,
            errors=[
                "boundary formula execution failed: "
                + str(exc)
            ],
            metadata={
                "formula_execution_error": True,
            },
        )

    if not isinstance(
        analysis,
        BoundaryAnalysis,
    ):
        return BoundaryEngineResult(
            status=BoundaryStatus.INVALID,
            instrument_id=normalized.instrument_id,
            symbol=normalized.symbol,
            research_validated=False,
            formula_id=descriptor.formula_id,
            formula_version=descriptor.formula_version,
            errors=[
                "boundary formula returned invalid "
                "BoundaryAnalysis"
            ],
        )

    formula_metadata = (
        _boundary_formula_metadata(
            descriptor
        )
    )

    existing_metadata = dict(
        analysis.metadata or {}
    )

    existing_metadata.update(
        formula_metadata
    )

    # Provider output becomes traceable to the validated
    # upstream formula. No intelligence value is fabricated.
    analysis = replace(
        analysis,
        instrument_id=(
            analysis.instrument_id
            or normalized.instrument_id
        ),
        symbol=(
            analysis.symbol
            or normalized.symbol
        ),
        timeframe=(
            analysis.timeframe
            if analysis.timeframe
            != Timeframe.UNKNOWN
            else normalized.timeframe
        ),
        formula_id=descriptor.formula_id,
        formula_version=descriptor.formula_version,
        formula_name=descriptor.name,
        formula_owner=descriptor.owner,
        formula_registry_key=descriptor.formula_id,
        research_validated=True,

        # Hard architectural boundary.
        is_signal=False,
        is_opportunity=False,
        is_decision=False,

        metadata=existing_metadata,
    )

    final_status = (
        BoundaryStatus.READY
        if analysis.status
        not in (
            BoundaryStatus.INVALID,
            BoundaryStatus.INSUFFICIENT_DATA,
        )
        else analysis.status
    )

    return BoundaryEngineResult(
        status=final_status,
        analysis=analysis,
        instrument_id=(
            analysis.instrument_id
            or normalized.instrument_id
        ),
        symbol=(
            analysis.symbol
            or normalized.symbol
        ),
        research_validated=True,
        formula_id=descriptor.formula_id,
        formula_version=descriptor.formula_version,
        warnings=list(
            validation.get(
                "warnings",
                []
            )
        ) + list(
            analysis.warnings or []
        ),
        errors=list(
            analysis.errors or []
        ),
        metadata={
            **formula_metadata,
            "boundary_intelligence_generated": True,
            "engine_generated_formula": False,
            "upstream_truth_preserved": True,
        },
    )


# ============================================================
# BOUNDARY RELATION
# ============================================================

def classify_boundary_relation(
    analyses: Sequence[BoundaryAnalysis],
) -> BoundaryRelation:
    """
    Classify semantic relation across validated boundary
    analyses.

    This is orchestration only. It does not replace a
    validated multi-timeframe research formula.
    """

    valid = [
        analysis
        for analysis in analyses
        if isinstance(
            analysis,
            BoundaryAnalysis,
        )
        and analysis.research_validated
    ]

    if not valid:
        return BoundaryRelation.UNKNOWN

    directions = {
        analysis.direction
        for analysis in valid
        if analysis.direction
        != BoundaryDirection.UNKNOWN
    }

    boundary_types = {
        analysis.boundary_type
        for analysis in valid
        if analysis.boundary_type
        != BoundaryType.UNKNOWN
    }

    states = {
        analysis.boundary_state
        for analysis in valid
        if analysis.boundary_state
        != BoundaryState.UNKNOWN
    }

    # Explicit semantic conflict.
    if (
        BoundaryDirection.UPSIDE in directions
        and BoundaryDirection.DOWNSIDE in directions
    ):
        return BoundaryRelation.CONFLICTING

    if (
        BoundaryState.BROKEN in states
        and BoundaryState.ESTABLISHED in states
    ):
        return BoundaryRelation.CONFLICTING

    if (
        len(directions) == 1
        and len(boundary_types) <= 1
    ):
        return BoundaryRelation.ALIGNED

    if len(directions) <= 1 and len(states) <= 1:
        return BoundaryRelation.NEUTRAL

    if (
        len(directions) > 1
        or len(boundary_types) > 1
    ):
        return BoundaryRelation.DIVERGENT

    return BoundaryRelation.UNKNOWN


# ============================================================
# DOMINANT BOUNDARY TYPE
# ============================================================

def determine_dominant_boundary_type(
    analyses: Sequence[BoundaryAnalysis],
) -> BoundaryType:
    """
    Determine the dominant boundary type using descriptive
    precedence.

    This is not a replacement for a validated research
    weighting formula.
    """

    priority = [
        BoundaryType.BREAKOUT_BOUNDARY,
        BoundaryType.BREAKDOWN_BOUNDARY,
        BoundaryType.RESISTANCE,
        BoundaryType.SUPPORT,
        BoundaryType.RANGE_HIGH,
        BoundaryType.RANGE_LOW,
        BoundaryType.INVALIDATION,
    ]

    valid = [
        analysis
        for analysis in analyses
        if isinstance(
            analysis,
            BoundaryAnalysis,
        )
        and analysis.research_validated
    ]

    if not valid:
        return BoundaryType.UNKNOWN

    counts: Dict[
        BoundaryType,
        int,
    ] = {}

    for analysis in valid:
        boundary_type = analysis.boundary_type

        if (
            boundary_type
            != BoundaryType.UNKNOWN
        ):
            counts[boundary_type] = (
                counts.get(
                    boundary_type,
                    0,
                )
                + 1
            )

    if not counts:
        return BoundaryType.UNKNOWN

    highest_count = max(
        counts.values()
    )

    candidates = {
        boundary_type
        for boundary_type, count
        in counts.items()
        if count == highest_count
    }

    for boundary_type in priority:
        if boundary_type in candidates:
            return boundary_type

    return BoundaryType.UNKNOWN


# ============================================================
# DOMINANT DIRECTION
# ============================================================

def determine_dominant_boundary_direction(
    analyses: Sequence[BoundaryAnalysis],
) -> BoundaryDirection:
    """
    Determine descriptive dominant direction.

    No trading signal is created.
    """

    counts = {
        BoundaryDirection.UPSIDE: 0,
        BoundaryDirection.DOWNSIDE: 0,
        BoundaryDirection.NEUTRAL: 0,
    }

    for analysis in analyses:
        if not isinstance(
            analysis,
            BoundaryAnalysis,
        ):
            continue

        if not analysis.research_validated:
            continue

        direction = analysis.direction

        if direction in counts:
            counts[direction] += 1

    if sum(counts.values()) == 0:
        return BoundaryDirection.UNKNOWN

    highest = max(
        counts.values()
    )

    leaders = [
        direction
        for direction, count
        in counts.items()
        if count == highest
    ]

    if (
        BoundaryDirection.UPSIDE in leaders
        and BoundaryDirection.DOWNSIDE in leaders
    ):
        return BoundaryDirection.NEUTRAL

    if len(leaders) > 1:
        return BoundaryDirection.NEUTRAL

    return leaders[0]


# ============================================================
# CONFIDENCE RANKING
# ============================================================

def _boundary_confidence_rank(
    confidence: BoundaryConfidence,
) -> int:
    ranks = {
        BoundaryConfidence.VERY_LOW: 1,
        BoundaryConfidence.LOW: 2,
        BoundaryConfidence.MODERATE: 3,
        BoundaryConfidence.HIGH: 4,
        BoundaryConfidence.VERY_HIGH: 5,
        BoundaryConfidence.UNKNOWN: 0,
    }

    return ranks.get(
        confidence,
        0,
    )


def _boundary_confidence_from_rank(
    rank: float,
) -> BoundaryConfidence:
    if rank <= 0:
        return BoundaryConfidence.UNKNOWN

    if rank < 1.5:
        return BoundaryConfidence.VERY_LOW

    if rank < 2.5:
        return BoundaryConfidence.LOW

    if rank < 3.5:
        return BoundaryConfidence.MODERATE

    if rank < 4.5:
        return BoundaryConfidence.HIGH

    return BoundaryConfidence.VERY_HIGH


def _average_boundary_confidence(
    analyses: Sequence[BoundaryAnalysis],
) -> BoundaryConfidence:
    ranks = [
        _boundary_confidence_rank(
            analysis.confidence
        )
        for analysis in analyses
        if isinstance(
            analysis,
            BoundaryAnalysis,
        )
        and analysis.research_validated
        and analysis.confidence
        != BoundaryConfidence.UNKNOWN
    ]

    if not ranks:
        return BoundaryConfidence.UNKNOWN

    return _boundary_confidence_from_rank(
        sum(ranks) / len(ranks)
    )


# ============================================================
# STRONGEST BOUNDARY
# ============================================================

def determine_strongest_boundary(
    analyses: Sequence[BoundaryAnalysis],
) -> Optional[BoundaryPoint]:
    """
    Select the strongest explicitly validated boundary point
    using confidence/strength metadata.

    This is descriptive orchestration only.
    """

    candidates: List[
        BoundaryPoint
    ] = []

    for analysis in analyses:
        if not isinstance(
            analysis,
            BoundaryAnalysis,
        ):
            continue

        if not analysis.research_validated:
            continue

        if analysis.primary_boundary:
            candidates.append(
                analysis.primary_boundary
            )

        candidates.extend(
            boundary
            for boundary
            in analysis.boundaries
            if boundary.validated
        )

    if not candidates:
        return None

    strength_rank = {
        BoundaryStrength.VERY_LOW: 1,
        BoundaryStrength.LOW: 2,
        BoundaryStrength.MODERATE: 3,
        BoundaryStrength.HIGH: 4,
        BoundaryStrength.VERY_HIGH: 5,
        BoundaryStrength.UNKNOWN: 0,
    }

    confidence_rank = {
        BoundaryConfidence.VERY_LOW: 1,
        BoundaryConfidence.LOW: 2,
        BoundaryConfidence.MODERATE: 3,
        BoundaryConfidence.HIGH: 4,
        BoundaryConfidence.VERY_HIGH: 5,
        BoundaryConfidence.UNKNOWN: 0,
    }

    return max(
        candidates,
        key=lambda boundary: (
            strength_rank.get(
                boundary.strength,
                0,
            ),
            confidence_rank.get(
                boundary.confidence,
                0,
            ),
        ),
    )


# ============================================================
# MULTI-TIMEFRAME ANALYSIS
# ============================================================

def analyze_multitimeframe_boundary(
    input_data: MultiTimeframeBoundaryInput,
    formula_map: Optional[
        Mapping[Timeframe, str]
    ] = None,
    formula_version_map: Optional[
        Mapping[Timeframe, str]
    ] = None,
    registry: Optional[
        BoundaryFormulaRegistry
    ] = None,
) -> BoundaryEngineResult:
    """
    Analyze boundaries across multiple timeframes.

    Each timeframe must explicitly resolve to a validated
    research formula.
    """

    registry = (
        registry
        or get_default_boundary_formula_registry()
    )

    if not isinstance(
        input_data,
        MultiTimeframeBoundaryInput,
    ):
        return BoundaryEngineResult(
            status=BoundaryStatus.INVALID,
            research_validated=False,
            errors=[
                "input_data must be "
                "MultiTimeframeBoundaryInput"
            ],
        )

    normalized = (
        normalize_multitimeframe_boundary_input(
            input_data
        )
    )

    validation = (
        validate_multitimeframe_boundary_input(
            normalized
        )
    )

    if not validation["valid"]:
        return BoundaryEngineResult(
            status=BoundaryStatus.INVALID,
            instrument_id=(
                normalized.instrument_id
            ),
            symbol=normalized.symbol,
            research_validated=False,
            warnings=list(
                validation.get(
                    "warnings",
                    [],
                )
            ),
            errors=list(
                validation.get(
                    "errors",
                    [],
                )
            ),
        )

    formula_map = dict(
        formula_map or {}
    )

    formula_version_map = dict(
        formula_version_map or {}
    )

    analyses: Dict[
        Timeframe,
        BoundaryAnalysis,
    ] = {}

    warnings: List[str] = []
    errors: List[str] = []

    for timeframe, boundary_input in (
        normalized.inputs.items()
    ):
        selected_formula = formula_map.get(
            timeframe
        )

        selected_version = (
            formula_version_map.get(
                timeframe
            )
        )

        result = analyze_boundary(
            input_data=boundary_input,
            formula_id=selected_formula,
            formula_version=selected_version,
            registry=registry,
        )

        warnings.extend(
            [
                f"{timeframe.value}: {warning}"
                for warning in result.warnings
            ]
        )

        errors.extend(
            [
                f"{timeframe.value}: {error}"
                for error in result.errors
            ]
        )

        if result.analysis is not None:
            analyses[timeframe] = (
                result.analysis
            )

    ordered_analyses = list(
        analyses.values()
    )

    all_validated = bool(
        ordered_analyses
        and len(ordered_analyses)
        == len(normalized.inputs)
        and all(
            analysis.research_validated
            for analysis
            in ordered_analyses
        )
    )

    relation = classify_boundary_relation(
        ordered_analyses
    )

    dominant_type = (
        determine_dominant_boundary_type(
            ordered_analyses
        )
    )

    dominant_direction = (
        determine_dominant_boundary_direction(
            ordered_analyses
        )
    )

    strongest_boundary = (
        determine_strongest_boundary(
            ordered_analyses
        )
    )

    average_confidence = (
        _average_boundary_confidence(
            ordered_analyses
        )
    )

    mtf_status = (
        BoundaryStatus.READY
        if all_validated
        else BoundaryStatus.DEGRADED
    )

    mtf = MultiTimeframeBoundary(
        status=mtf_status,
        instrument_id=(
            normalized.instrument_id
        ),
        symbol=normalized.symbol,
        analyses=analyses,
        relation=relation,
        dominant_boundary_type=dominant_type,
        dominant_direction=dominant_direction,
        strongest_boundary=strongest_boundary,
        average_confidence=average_confidence,
        research_validated=all_validated,
        warnings=warnings,
        errors=errors,
        metadata={
            "multi_timeframe": True,
            "formula_map_explicit": True,
            "research_formula_required": True,
            "upstream_truth_preserved": True,
            "engine_generated_formula": False,
        },
    )

    return BoundaryEngineResult(
        status=mtf_status,
        multi_timeframe=mtf,
        instrument_id=(
            normalized.instrument_id
        ),
        symbol=normalized.symbol,
        research_validated=all_validated,
        warnings=warnings,
        errors=errors,
        metadata={
            "multi_timeframe": True,
            "analysis_count": len(
                ordered_analyses
            ),
            "validated_analysis_count": sum(
                1
                for analysis
                in ordered_analyses
                if analysis.research_validated
            ),
            "boundary_intelligence_generated": (
                all_validated
            ),
        },
    )


# ============================================================
# ENGINE RUNNER
# ============================================================

def run_boundary_engine(
    input_data: Optional[BoundaryInput] = None,
    multi_timeframe_input: Optional[
        MultiTimeframeBoundaryInput
    ] = None,
    formula_id: Optional[str] = None,
    formula_version: Optional[str] = None,
    formula_map: Optional[
        Mapping[Timeframe, str]
    ] = None,
    formula_version_map: Optional[
        Mapping[Timeframe, str]
    ] = None,
    registry: Optional[
        BoundaryFormulaRegistry
    ] = None,
) -> BoundaryEngineResult:
    """
    Main Boundary Engine execution entry point.
    """

    if (
        input_data is not None
        and multi_timeframe_input is not None
    ):
        return BoundaryEngineResult(
            status=BoundaryStatus.INVALID,
            research_validated=False,
            errors=[
                "provide either input_data or "
                "multi_timeframe_input, not both"
            ],
        )

    if multi_timeframe_input is not None:
        return analyze_multitimeframe_boundary(
            input_data=multi_timeframe_input,
            formula_map=formula_map,
            formula_version_map=(
                formula_version_map
            ),
            registry=registry,
        )

    if input_data is not None:
        return analyze_boundary(
            input_data=input_data,
            formula_id=formula_id,
            formula_version=formula_version,
            registry=registry,
        )

    return BoundaryEngineResult(
        status=BoundaryStatus.INSUFFICIENT_DATA,
        research_validated=False,
        warnings=[
            "no boundary input supplied"
        ],
        metadata={
            "intelligence_generated": False
        },
    )


# ============================================================
# SNAPSHOT BUILDER
# ============================================================

def build_boundary_engine_snapshot(
    result: BoundaryEngineResult,
) -> BoundaryEngineSnapshot:
    """
    Create an immutable engine snapshot from a result.
    """

    if not isinstance(
        result,
        BoundaryEngineResult,
    ):
        raise TypeError(
            "result must be BoundaryEngineResult"
        )

    metadata = tuple(
        sorted(
            (
                str(key),
                value,
            )
            for key, value
            in (result.metadata or {}).items()
            if isinstance(key, str)
        )
    )

    return BoundaryEngineSnapshot(
        engine=BOUNDARY_ENGINE,
        version=BOUNDARY_ENGINE_VERSION,
        instrument_id=result.instrument_id,
        symbol=result.symbol,
        status=result.status,
        formula_id=result.formula_id,
        formula_version=result.formula_version,
        research_validated=result.research_validated,
        analysis=result.analysis,
        multi_timeframe=result.multi_timeframe,
        metadata=metadata,
    )


# ============================================================
# PART 3 CONTRACT CHECK
# ============================================================

def boundary_part3_contract_check(
    registry: Optional[
        BoundaryFormulaRegistry
    ] = None,
) -> Dict[str, Any]:
    registry = (
        registry
        or get_default_boundary_formula_registry()
    )

    checks = {
        "formula_metadata_available": callable(
            _boundary_formula_metadata
        ),
        "single_analysis_available": callable(
            analyze_boundary
        ),
        "relation_analysis_available": callable(
            classify_boundary_relation
        ),
        "dominant_type_available": callable(
            determine_dominant_boundary_type
        ),
        "dominant_direction_available": callable(
            determine_dominant_boundary_direction
        ),
        "strongest_boundary_available": callable(
            determine_strongest_boundary
        ),
        "mtf_analysis_available": callable(
            analyze_multitimeframe_boundary
        ),
        "engine_runner_available": callable(
            run_boundary_engine
        ),
        "snapshot_available": callable(
            build_boundary_engine_snapshot
        ),
        "validated_formula_required": (
            BOUNDARY_ENGINE_CONTRACT[
                "formula_policy"
            ][
                "validated_required"
            ]
            is True
        ),
        "no_formula_guessing": (
            BOUNDARY_ENGINE_AUTHORITY[
                "guessed_formula"
            ]
            is False
        ),
        "no_signal_generation": (
            BOUNDARY_ENGINE_AUTHORITY[
                "confirmation_generation"
            ]
            is False
        ),
        "no_opportunity_generation": (
            BOUNDARY_ENGINE_AUTHORITY[
                "opportunity_generation"
            ]
            is False
        ),
        "no_decision_generation": (
            BOUNDARY_ENGINE_AUTHORITY[
                "decision_generation"
            ]
            is False
        ),
        "no_d13_generation": (
            BOUNDARY_ENGINE_AUTHORITY[
                "d13_generation"
            ]
            is False
        ),
        "no_execution_generation": (
            BOUNDARY_ENGINE_AUTHORITY[
                "execution_generation"
            ]
            is False
        ),
    }

    errors = [
        key
        for key, value
        in checks.items()
        if not value
    ]

    return {
        "engine": BOUNDARY_ENGINE,
        "version": BOUNDARY_ENGINE_VERSION,
        "part": 3,
        "valid": not errors,
        "status": (
            "PASS"
            if not errors
            else "FAIL"
        ),
        "checks": checks,
        "errors": errors,
        "formula_registry_count": len(
            registry
        ),
    }
# ============================================================
# ROBOMLM_PLUS — BOUNDARY INTELLIGENCE ENGINE
# PART 4 / 5
# Serialization • Validation • Integrity • Health • Diagnostics
# ============================================================

from dataclasses import dataclass, asdict, is_dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


# ============================================================
# 4.1 GENERIC SERIALIZATION
# ============================================================

def _serialize_boundary_value(value: Any) -> Any:
    """Recursively serialize Boundary Engine values."""

    if isinstance(value, Enum):
        return value.value

    if is_dataclass(value):
        return {
            key: _serialize_boundary_value(val)
            for key, val in asdict(value).items()
        }

    if isinstance(value, dict):
        return {
            str(key): _serialize_boundary_value(val)
            for key, val in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            _serialize_boundary_value(item)
            for item in value
        ]

    return value


# ============================================================
# 4.2 INPUT SERIALIZERS
# ============================================================

def serialize_boundary_input(
    input_data: BoundaryInput,
) -> Dict[str, Any]:

    return _serialize_boundary_value(input_data)


def serialize_multitimeframe_boundary_input(
    input_data: MultiTimeframeBoundaryInput,
) -> Dict[str, Any]:

    return _serialize_boundary_value(input_data)


# ============================================================
# 4.3 COMPONENT SERIALIZERS
# ============================================================

def serialize_boundary_point(
    point: BoundaryPoint,
) -> Dict[str, Any]:

    return _serialize_boundary_value(point)


def serialize_boundary_measurement(
    measurement: BoundaryMeasurement,
) -> Dict[str, Any]:

    return _serialize_boundary_value(measurement)


def serialize_boundary_window(
    window: BoundaryWindow,
) -> Dict[str, Any]:

    return _serialize_boundary_value(window)


# ============================================================
# 4.4 ANALYSIS SERIALIZERS
# ============================================================

def serialize_boundary_analysis(
    analysis: BoundaryAnalysis,
) -> Dict[str, Any]:

    return _serialize_boundary_value(analysis)


def serialize_multitimeframe_boundary(
    result: MultiTimeframeBoundary,
) -> Dict[str, Any]:

    return _serialize_boundary_value(result)


def serialize_boundary_engine_result(
    result: BoundaryEngineResult,
) -> Dict[str, Any]:

    return _serialize_boundary_value(result)


def serialize_boundary_engine_request(
    request: BoundaryEngineRequest,
) -> Dict[str, Any]:

    return _serialize_boundary_value(request)


def serialize_boundary_engine_snapshot(
    snapshot: BoundaryEngineSnapshot,
) -> Dict[str, Any]:

    return _serialize_boundary_value(snapshot)


def serialize_boundary_formula_descriptor(
    descriptor: BoundaryFormulaDescriptor,
) -> Dict[str, Any]:

    return _serialize_boundary_value(descriptor)


# ============================================================
# 4.5 BOUNDARY POINT VALIDATION
# ============================================================

def validate_boundary_point(
    point: BoundaryPoint,
) -> Dict[str, Any]:

    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(point, BoundaryPoint):
        return {
            "valid": False,
            "errors": ["point must be BoundaryPoint"],
            "warnings": [],
        }

    if point.price is None:
        errors.append("boundary price is required")
    else:
        try:
            price = float(point.price)

            if price <= 0:
                errors.append(
                    "boundary price must be positive"
                )

        except (TypeError, ValueError):
            errors.append(
                "boundary price must be numeric"
            )

    if not isinstance(
        point.boundary_type,
        BoundaryType,
    ):
        errors.append(
            "invalid boundary_type"
        )

    if not isinstance(
        point.direction,
        BoundaryDirection,
    ):
        errors.append(
            "invalid boundary direction"
        )

    if not isinstance(
        point.source_type,
        BoundarySourceType,
    ):
        errors.append(
            "invalid boundary source type"
        )

    if not isinstance(
        point.strength,
        BoundaryStrength,
    ):
        errors.append(
            "invalid boundary strength"
        )

    if not isinstance(
        point.confidence,
        BoundaryConfidence,
    ):
        errors.append(
            "invalid boundary confidence"
        )

    if point.validated is not True:
        warnings.append(
            "boundary point is not explicitly validated"
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


# ============================================================
# 4.6 MEASUREMENT VALIDATION
# ============================================================

def validate_boundary_measurement(
    measurement: BoundaryMeasurement,
) -> Dict[str, Any]:

    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(
        measurement,
        BoundaryMeasurement,
    ):
        return {
            "valid": False,
            "errors": [
                "measurement must be BoundaryMeasurement"
            ],
            "warnings": [],
        }

    if not measurement.name:
        errors.append(
            "measurement name is required"
        )

    if measurement.value is None:
        errors.append(
            "measurement value is required"
        )

    if not measurement.unit:
        warnings.append(
            "measurement unit is missing"
        )

    if measurement.research_validated:
        if not measurement.formula_id:
            errors.append(
                "validated measurement requires formula_id"
            )

        if not measurement.formula_version:
            errors.append(
                "validated measurement requires formula_version"
            )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


# ============================================================
# 4.7 WINDOW VALIDATION
# ============================================================

def validate_boundary_window(
    window: BoundaryWindow,
) -> Dict[str, Any]:

    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(
        window,
        BoundaryWindow,
    ):
        return {
            "valid": False,
            "errors": [
                "window must be BoundaryWindow"
            ],
            "warnings": [],
        }

    if window.observation_count < 0:
        errors.append(
            "observation_count cannot be negative"
        )

    if (
        window.highest_price is not None
        and window.lowest_price is not None
    ):
        if (
            window.highest_price
            < window.lowest_price
        ):
            errors.append(
                "highest_price cannot be below lowest_price"
            )

    if window.observation_count == 0:
        warnings.append(
            "boundary window contains no observations"
        )

    if window.total_volume is not None:
        try:
            if float(window.total_volume) < 0:
                errors.append(
                    "total_volume cannot be negative"
                )
        except (TypeError, ValueError):
            errors.append(
                "total_volume must be numeric"
            )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


# ============================================================
# 4.8 ANALYSIS VALIDATION
# ============================================================

def validate_boundary_analysis(
    analysis: BoundaryAnalysis,
) -> Dict[str, Any]:

    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(
        analysis,
        BoundaryAnalysis,
    ):
        return {
            "valid": False,
            "errors": [
                "analysis must be BoundaryAnalysis"
            ],
            "warnings": [],
        }

    if not analysis.instrument_id and not analysis.symbol:
        errors.append(
            "analysis requires instrument_id or symbol"
        )

    if not isinstance(
        analysis.status,
        BoundaryStatus,
    ):
        errors.append(
            "invalid analysis status"
        )

    if not isinstance(
        analysis.boundary_state,
        BoundaryState,
    ):
        errors.append(
            "invalid boundary state"
        )

    if not isinstance(
        analysis.boundary_type,
        BoundaryType,
    ):
        errors.append(
            "invalid boundary type"
        )

    if not isinstance(
        analysis.direction,
        BoundaryDirection,
    ):
        errors.append(
            "invalid boundary direction"
        )

    if not isinstance(
        analysis.phase,
        BoundaryPhase,
    ):
        errors.append(
            "invalid boundary phase"
        )

    if not isinstance(
        analysis.strength,
        BoundaryStrength,
    ):
        errors.append(
            "invalid boundary strength"
        )

    if not isinstance(
        analysis.confidence,
        BoundaryConfidence,
    ):
        errors.append(
            "invalid boundary confidence"
        )

    window_result = validate_boundary_window(
        analysis.window
    )

    errors.extend(
        window_result["errors"]
    )

    warnings.extend(
        window_result["warnings"]
    )

    for point in analysis.boundaries:

        point_result = validate_boundary_point(
            point
        )

        errors.extend(
            point_result["errors"]
        )

        warnings.extend(
            point_result["warnings"]
        )

    for measurement in analysis.measurements:

        measurement_result = (
            validate_boundary_measurement(
                measurement
            )
        )

        errors.extend(
            measurement_result["errors"]
        )

        warnings.extend(
            measurement_result["warnings"]
        )

    # --------------------------------------------------------
    # Research traceability
    # --------------------------------------------------------

    if analysis.research_validated:

        if not analysis.formula_id:
            errors.append(
                "validated analysis requires formula_id"
            )

        if not analysis.formula_version:
            errors.append(
                "validated analysis requires formula_version"
            )

        if not analysis.formula_name:
            errors.append(
                "validated analysis requires formula_name"
            )

        if not analysis.formula_owner:
            errors.append(
                "validated analysis requires formula_owner"
            )

        if not analysis.formula_registry_key:
            errors.append(
                "validated analysis requires formula_registry_key"
            )

    # --------------------------------------------------------
    # Boundary engine authority protection
    # --------------------------------------------------------

    if analysis.is_signal:
        errors.append(
            "boundary analysis cannot become a signal"
        )

    if analysis.is_opportunity:
        errors.append(
            "boundary analysis cannot become an opportunity"
        )

    if analysis.is_decision:
        errors.append(
            "boundary analysis cannot become a decision"
        )

    if (
        analysis.primary_boundary is not None
        and not isinstance(
            analysis.primary_boundary,
            BoundaryPoint,
        )
    ):
        errors.append(
            "primary_boundary must be BoundaryPoint"
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


# ============================================================
# 4.9 MULTI-TIMEFRAME VALIDATION
# ============================================================

def validate_multitimeframe_boundary(
    result: MultiTimeframeBoundary,
) -> Dict[str, Any]:

    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(
        result,
        MultiTimeframeBoundary,
    ):
        return {
            "valid": False,
            "errors": [
                "result must be MultiTimeframeBoundary"
            ],
            "warnings": [],
        }

    if not result.instrument_id and not result.symbol:
        errors.append(
            "multi-timeframe result requires instrument_id or symbol"
        )

    if not result.analyses:
        warnings.append(
            "multi-timeframe result contains no analyses"
        )

    for timeframe, analysis in result.analyses.items():

        if not isinstance(
            timeframe,
            Timeframe,
        ):
            errors.append(
                "invalid timeframe key in analyses"
            )

        analysis_result = (
            validate_boundary_analysis(
                analysis
            )
        )

        errors.extend(
            analysis_result["errors"]
        )

        warnings.extend(
            analysis_result["warnings"]
        )

    if result.research_validated:

        if not result.analyses:
            errors.append(
                "validated multi-timeframe result requires analyses"
            )

        if not all(
            analysis.research_validated
            for analysis in result.analyses.values()
        ):
            errors.append(
                "all MTF analyses must be research validated"
            )

    if result.strongest_boundary is not None:

        strongest_result = validate_boundary_point(
            result.strongest_boundary
        )

        errors.extend(
            strongest_result["errors"]
        )

        warnings.extend(
            strongest_result["warnings"]
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


# ============================================================
# 4.10 ENGINE RESULT VALIDATION
# ============================================================

def validate_boundary_engine_result(
    result: BoundaryEngineResult,
) -> Dict[str, Any]:

    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(
        result,
        BoundaryEngineResult,
    ):
        return {
            "valid": False,
            "errors": [
                "result must be BoundaryEngineResult"
            ],
            "warnings": [],
        }

    if (
        result.analysis is not None
        and result.multi_timeframe is not None
    ):
        errors.append(
            "result cannot contain both single-timeframe "
            "analysis and multi-timeframe analysis"
        )

    if result.analysis is not None:

        analysis_result = validate_boundary_analysis(
            result.analysis
        )

        errors.extend(
            analysis_result["errors"]
        )

        warnings.extend(
            analysis_result["warnings"]
        )

    if result.multi_timeframe is not None:

        mtf_result = validate_multitimeframe_boundary(
            result.multi_timeframe
        )

        errors.extend(
            mtf_result["errors"]
        )

        warnings.extend(
            mtf_result["warnings"]
        )

    if result.research_validated:

        if not result.formula_id:
            errors.append(
                "validated result requires formula_id"
            )

        if not result.formula_version:
            errors.append(
                "validated result requires formula_version"
            )

        if (
            result.analysis is not None
            and not result.analysis.research_validated
        ):
            errors.append(
                "validated result cannot contain "
                "non-validated analysis"
            )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


# ============================================================
# 4.11 FORMULA DESCRIPTOR VALIDATION
# ============================================================

def validate_boundary_formula_descriptor(
    descriptor: BoundaryFormulaDescriptor,
) -> Dict[str, Any]:

    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(
        descriptor,
        BoundaryFormulaDescriptor,
    ):
        return {
            "valid": False,
            "errors": [
                "descriptor must be BoundaryFormulaDescriptor"
            ],
            "warnings": [],
        }

    if not descriptor.formula_id:
        errors.append(
            "formula_id is required"
        )

    if not descriptor.formula_version:
        errors.append(
            "formula_version is required"
        )

    if not descriptor.name:
        errors.append(
            "formula name is required"
        )

    if not descriptor.owner:
        errors.append(
            "formula owner is required"
        )

    if not descriptor.supported_asset_classes:
        warnings.append(
            "formula has no declared asset classes"
        )

    if not descriptor.supported_timeframes:
        warnings.append(
            "formula has no declared timeframes"
        )

    if not descriptor.enabled:
        warnings.append(
            "formula descriptor is disabled"
        )

    if not descriptor.validated:
        warnings.append(
            "formula descriptor is not research validated"
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


# ============================================================
# 4.12 COMPLETE ENGINE INTEGRITY
# ============================================================

def validate_boundary_engine_integrity(
    result: Optional[BoundaryEngineResult] = None,
    descriptor: Optional[BoundaryFormulaDescriptor] = None,
) -> Dict[str, Any]:

    errors: List[str] = []
    warnings: List[str] = []

    # --------------------------------------------------------
    # Authority
    # --------------------------------------------------------

    authority = validate_boundary_authority()

    if not authority:
        errors.append(
            "boundary engine authority validation failed"
        )

    # --------------------------------------------------------
    # Contract
    # --------------------------------------------------------

    if not BOUNDARY_ENGINE_CONTRACT:
        errors.append(
            "boundary engine contract is missing"
        )

    # --------------------------------------------------------
    # Formula policy
    # --------------------------------------------------------

    contract = BOUNDARY_ENGINE_CONTRACT

    if contract.get(
        "default_formula_allowed",
        True,
    ):
        errors.append(
            "default formula must not be allowed"
        )

    if contract.get(
        "guessing_allowed",
        True,
    ):
        errors.append(
            "formula guessing must not be allowed"
        )

    if contract.get(
        "silent_substitution_allowed",
        True,
    ):
        errors.append(
            "silent formula substitution must not be allowed"
        )

    if contract.get(
        "engine_generates_formula",
        True,
    ):
        errors.append(
            "boundary engine must not generate formulas"
        )

    # --------------------------------------------------------
    # Optional descriptor validation
    # --------------------------------------------------------

    if descriptor is not None:

        descriptor_result = (
            validate_boundary_formula_descriptor(
                descriptor
            )
        )

        errors.extend(
            descriptor_result["errors"]
        )

        warnings.extend(
            descriptor_result["warnings"]
        )

    # --------------------------------------------------------
    # Optional result validation
    # --------------------------------------------------------

    if result is not None:

        result_validation = (
            validate_boundary_engine_result(
                result
            )
        )

        errors.extend(
            result_validation["errors"]
        )

        warnings.extend(
            result_validation["warnings"]
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


# ============================================================
# 4.13 ENGINE HEALTH
# ============================================================

@dataclass(frozen=True)
class BoundaryEngineHealth:
    engine: str
    version: str

    operational: bool
    authority_valid: bool

    input_normalization_available: bool
    multi_timeframe_available: bool
    formula_registry_available: bool
    validated_formula_available: bool

    research_formula_required: bool
    research_formula_generated_here: bool

    boundary_intelligence_generated: bool

    opportunity_generation: bool
    decision_generation: bool
    d13_generation: bool
    risk_generation: bool
    cas_generation: bool
    execution_generation: bool

    warnings: List[str]
    errors: List[str]

    metadata: Dict[str, Any]


# ============================================================
# 4.14 HEALTH BUILDER
# ============================================================

def build_boundary_engine_health(
    registry: Optional[BoundaryFormulaRegistry] = None,
) -> BoundaryEngineHealth:

    warnings: List[str] = []
    errors: List[str] = []

    authority_valid = validate_boundary_authority()

    if not authority_valid:
        errors.append(
            "boundary authority contract failed"
        )

    if registry is None:
        registry = get_boundary_formula_registry()

    registry_available = (
        registry is not None
    )

    if not registry_available:
        errors.append(
            "boundary formula registry unavailable"
        )

    validated_formula_available = False

    if registry_available:

        try:
            descriptors = registry.descriptors()

            validated_formula_available = any(
                descriptor.enabled
                and descriptor.validated
                for descriptor in descriptors
            )

        except Exception as exc:
            errors.append(
                f"formula registry inspection failed: {exc}"
            )

    if not validated_formula_available:
        warnings.append(
            "no validated boundary research formula "
            "is currently registered"
        )

    operational = (
        authority_valid
        and registry_available
        and callable(normalize_boundary_input)
        and callable(run_boundary_engine)
    )

    return BoundaryEngineHealth(
        engine=BOUNDARY_ENGINE,
        version=BOUNDARY_ENGINE_VERSION,

        operational=operational,
        authority_valid=authority_valid,

        input_normalization_available=True,
        multi_timeframe_available=True,
        formula_registry_available=registry_available,
        validated_formula_available=validated_formula_available,

        research_formula_required=True,
        research_formula_generated_here=False,

        boundary_intelligence_generated=True,

        opportunity_generation=False,
        decision_generation=False,
        d13_generation=False,
        risk_generation=False,
        cas_generation=False,
        execution_generation=False,

        warnings=warnings,
        errors=errors,

        metadata={
            "health_layer": "BOUNDARY_INTELLIGENCE",
            "research_first": True,
            "math_first": True,
            "formula_pluggable": True,
            "formula_registry_based": True,
            "upstream_truth_preserved": True,
        },
    )


# ============================================================
# 4.15 HEALTH SERIALIZER
# ============================================================

def serialize_boundary_engine_health(
    health: BoundaryEngineHealth,
) -> Dict[str, Any]:

    return _serialize_boundary_value(health)


# ============================================================
# 4.16 OPERATIONAL CHECK
# ============================================================

def boundary_engine_operational_check(
    registry: Optional[BoundaryFormulaRegistry] = None,
) -> Dict[str, Any]:

    health = build_boundary_engine_health(
        registry=registry
    )

    return {
        "engine": health.engine,
        "version": health.version,
        "operational": health.operational,
        "authority_valid": health.authority_valid,
        "input_normalization_available":
            health.input_normalization_available,
        "multi_timeframe_available":
            health.multi_timeframe_available,
        "formula_registry_available":
            health.formula_registry_available,
        "validated_formula_available":
            health.validated_formula_available,
        "research_formula_required":
            health.research_formula_required,
        "research_formula_generated_here":
            health.research_formula_generated_here,
        "boundary_intelligence_generated":
            health.boundary_intelligence_generated,
        "warnings": list(health.warnings),
        "errors": list(health.errors),
    }


# ============================================================
# 4.17 DIAGNOSTICS
# ============================================================

def boundary_engine_diagnostics(
    registry: Optional[BoundaryFormulaRegistry] = None,
) -> Dict[str, Any]:

    if registry is None:
        registry = get_boundary_formula_registry()

    authority_valid = validate_boundary_authority()

    registry_descriptors: List[Dict[str, Any]] = []

    if registry is not None:

        try:
            for descriptor in registry.descriptors():

                descriptor_result = (
                    validate_boundary_formula_descriptor(
                        descriptor
                    )
                )

                registry_descriptors.append({
                    "descriptor":
                        serialize_boundary_formula_descriptor(
                            descriptor
                        ),
                    "validation":
                        descriptor_result,
                })

        except Exception as exc:

            registry_descriptors.append({
                "descriptor": None,
                "validation": {
                    "valid": False,
                    "errors": [
                        f"registry diagnostics failed: {exc}"
                    ],
                    "warnings": [],
                },
            })

    health = build_boundary_engine_health(
        registry=registry
    )

    return {
        "engine": BOUNDARY_ENGINE,
        "version": BOUNDARY_ENGINE_VERSION,

        "authority": {
            "valid": authority_valid,
            "contract":
                _serialize_boundary_value(
                    BOUNDARY_ENGINE_CONTRACT
                ),
        },

        "health":
            serialize_boundary_engine_health(
                health
            ),

        "formula_registry": {
            "available": registry is not None,
            "descriptors": registry_descriptors,
        },

        "intelligence_boundary": {
            "boundary_intelligence": True,
            "signal_generation": False,
            "opportunity_generation": False,
            "decision_generation": False,
            "d13_generation": False,
            "risk_generation": False,
            "cas_generation": False,
            "execution_generation": False,
        },

        "truth_policy": {
            "math_first": True,
            "research_first": True,
            "upstream_truth_preserved": True,
            "boundary_is_not_signal": True,
            "boundary_is_not_decision": True,
        },
    }


# ============================================================
# 4.18 PART-4 SELF CHECK
# ============================================================

def boundary_part4_self_check() -> Dict[str, Any]:

    checks: Dict[str, bool] = {}

    # Core classes
    checks["boundary_point_class"] = (
        BoundaryPoint is not None
    )

    checks["boundary_measurement_class"] = (
        BoundaryMeasurement is not None
    )

    checks["boundary_window_class"] = (
        BoundaryWindow is not None
    )

    checks["boundary_analysis_class"] = (
        BoundaryAnalysis is not None
    )

    checks["multitimeframe_class"] = (
        MultiTimeframeBoundary is not None
    )

    checks["engine_result_class"] = (
        BoundaryEngineResult is not None
    )

    checks["engine_request_class"] = (
        BoundaryEngineRequest is not None
    )

    checks["snapshot_class"] = (
        BoundaryEngineSnapshot is not None
    )

    # Serializers
    checks["input_serializer"] = callable(
        serialize_boundary_input
    )

    checks["analysis_serializer"] = callable(
        serialize_boundary_analysis
    )

    checks["result_serializer"] = callable(
        serialize_boundary_engine_result
    )

    checks["snapshot_serializer"] = callable(
        serialize_boundary_engine_snapshot
    )

    # Validators
    checks["point_validator"] = callable(
        validate_boundary_point
    )

    checks["measurement_validator"] = callable(
        validate_boundary_measurement
    )

    checks["window_validator"] = callable(
        validate_boundary_window
    )

    checks["analysis_validator"] = callable(
        validate_boundary_analysis
    )

    checks["mtf_validator"] = callable(
        validate_multitimeframe_boundary
    )

    checks["result_validator"] = callable(
        validate_boundary_engine_result
    )

    checks["formula_validator"] = callable(
        validate_boundary_formula_descriptor
    )

    # Engine integrity
    checks["engine_integrity_validator"] = callable(
        validate_boundary_engine_integrity
    )

    # Health
    checks["health_class"] = (
        BoundaryEngineHealth is not None
    )

    checks["health_builder"] = callable(
        build_boundary_engine_health
    )

    checks["operational_check"] = callable(
        boundary_engine_operational_check
    )

    checks["diagnostics"] = callable(
        boundary_engine_diagnostics
    )

    # Authority
    checks["authority_valid"] = (
        validate_boundary_authority()
    )

    # Contract
    checks["contract_present"] = bool(
        BOUNDARY_ENGINE_CONTRACT
    )

    checks["formula_generation_forbidden"] = (
        BOUNDARY_ENGINE_AUTHORITY.get(
            "research_formula_generation"
        )
        is False
    )

    checks["signal_generation_forbidden"] = (
        BOUNDARY_ENGINE_AUTHORITY.get(
            "breakout_generation"
        )
        is False
    )

    checks["decision_generation_forbidden"] = (
        BOUNDARY_ENGINE_AUTHORITY.get(
            "decision_generation"
        )
        is False
    )

    checks["d13_generation_forbidden"] = (
        BOUNDARY_ENGINE_AUTHORITY.get(
            "d13_generation"
        )
        is False
    )

    checks["risk_generation_forbidden"] = (
        BOUNDARY_ENGINE_AUTHORITY.get(
            "risk_generation"
        )
        is False
    )

    checks["execution_generation_forbidden"] = (
        BOUNDARY_ENGINE_AUTHORITY.get(
            "execution_generation"
        )
        is False
    )

    passed = all(checks.values())

    return {
        "engine": BOUNDARY_ENGINE,
        "version": BOUNDARY_ENGINE_VERSION,
        "part": 4,
        "passed": passed,
        "checks": checks,
    }


# ============================================================
# 4.19 PART-4 CONTRACT CHECK
# ============================================================

def boundary_part4_contract_check() -> Dict[str, Any]:

    self_check = boundary_part4_self_check()

    integrity = validate_boundary_engine_integrity()

    health = build_boundary_engine_health()

    passed = (
        self_check["passed"]
        and integrity["valid"]
        and health.authority_valid
        and health.research_formula_generated_here is False
        and health.opportunity_generation is False
        and health.decision_generation is False
        and health.d13_generation is False
        and health.risk_generation is False
        and health.cas_generation is False
        and health.execution_generation is False
    )

    return {
        "engine": BOUNDARY_ENGINE,
        "version": BOUNDARY_ENGINE_VERSION,
        "part": 4,
        "passed": passed,

        "self_check": self_check,
        "integrity": integrity,
        "health":
            serialize_boundary_engine_health(
                health
            ),

        "truth": {
            "formula_generated_here": False,
            "signal_generated_here": False,
            "opportunity_generated_here": False,
            "decision_generated_here": False,
            "d13_generated_here": False,
            "risk_generated_here": False,
            "cas_generated_here": False,
            "execution_generated_here": False,
        },
    }
# ============================================================
# ROBOMLM_PLUS — BOUNDARY INTELLIGENCE ENGINE
# PART 5 / 5
# Request • Execution • Summaries • Manifest • Final Check
# ============================================================


# ============================================================
# 5.1 REQUEST FACTORY
# ============================================================

def create_boundary_request(
    input_data: Optional[BoundaryInput] = None,
    multi_timeframe_input: Optional[
        MultiTimeframeBoundaryInput
    ] = None,
    formula_id: Optional[str] = None,
    formula_version: Optional[str] = None,
    formula_map: Optional[
        Dict[Timeframe, str]
    ] = None,
    formula_version_map: Optional[
        Dict[Timeframe, str]
    ] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> BoundaryEngineRequest:

    if (
        input_data is not None
        and multi_timeframe_input is not None
    ):
        raise ValueError(
            "request cannot contain both "
            "single-timeframe and multi-timeframe input"
        )

    return BoundaryEngineRequest(
        input_data=input_data,
        multi_timeframe_input=multi_timeframe_input,
        formula_id=formula_id,
        formula_version=formula_version,
        formula_map=formula_map or {},
        formula_version_map=formula_version_map or {},
        metadata=metadata or {},
    )


# ============================================================
# 5.2 REQUEST EXECUTOR
# ============================================================

def execute_boundary_request(
    request: BoundaryEngineRequest,
    registry: Optional[
        BoundaryFormulaRegistry
    ] = None,
) -> BoundaryEngineResult:

    if not isinstance(
        request,
        BoundaryEngineRequest,
    ):
        raise TypeError(
            "request must be BoundaryEngineRequest"
        )

    if request.input_data is not None:

        return run_boundary_engine(
            input_data=request.input_data,
            formula_id=request.formula_id,
            formula_version=request.formula_version,
            registry=registry,
        )

    if request.multi_timeframe_input is not None:

        return run_boundary_engine(
            multi_timeframe_input=
                request.multi_timeframe_input,
            formula_map=request.formula_map,
            formula_version_map=
                request.formula_version_map,
            registry=registry,
        )

    return BoundaryEngineResult(
        status=BoundaryStatus.INSUFFICIENT_DATA,
        analysis=None,
        multi_timeframe=None,
        instrument_id=None,
        symbol=None,
        research_validated=False,
        formula_id=None,
        formula_version=None,
        warnings=[
            "no boundary input supplied"
        ],
        errors=[],
        metadata={
            "request_execution": True,
            "intelligence_generated": False,
        },
    )


# ============================================================
# 5.3 RESULT STATUS HELPERS
# ============================================================

def boundary_result_is_ready(
    result: Optional[BoundaryEngineResult],
) -> bool:

    if not isinstance(
        result,
        BoundaryEngineResult,
    ):
        return False

    return result.status == BoundaryStatus.READY


def boundary_result_has_validated_research(
    result: Optional[BoundaryEngineResult],
) -> bool:

    if not isinstance(
        result,
        BoundaryEngineResult,
    ):
        return False

    if not result.research_validated:
        return False

    if result.analysis is not None:
        return result.analysis.research_validated

    if result.multi_timeframe is not None:
        return result.multi_timeframe.research_validated

    return False


def boundary_result_has_errors(
    result: Optional[BoundaryEngineResult],
) -> bool:

    if not isinstance(
        result,
        BoundaryEngineResult,
    ):
        return True

    return bool(result.errors)


def boundary_result_has_warnings(
    result: Optional[BoundaryEngineResult],
) -> bool:

    if not isinstance(
        result,
        BoundaryEngineResult,
    ):
        return True

    return bool(result.warnings)


# ============================================================
# 5.4 SINGLE ANALYSIS SUMMARY
# ============================================================

def summarize_boundary_analysis(
    analysis: Optional[BoundaryAnalysis],
) -> Dict[str, Any]:

    if analysis is None:
        return {
            "available": False,
            "status": BoundaryStatus.INSUFFICIENT_DATA.value,
        }

    primary_price = None

    if analysis.primary_boundary is not None:
        primary_price = (
            analysis.primary_boundary.price
        )

    return {
        "available": True,
        "status": analysis.status.value,
        "instrument_id": analysis.instrument_id,
        "symbol": analysis.symbol,
        "timeframe": analysis.timeframe.value,

        "boundary_state":
            analysis.boundary_state.value,

        "boundary_type":
            analysis.boundary_type.value,

        "direction":
            analysis.direction.value,

        "phase":
            analysis.phase.value,

        "strength":
            analysis.strength.value,

        "confidence":
            analysis.confidence.value,

        "primary_boundary":
            primary_price,

        "boundary_count":
            len(analysis.boundaries),

        "measurement_count":
            len(analysis.measurements),

        "formula": {
            "id": analysis.formula_id,
            "version": analysis.formula_version,
            "name": analysis.formula_name,
            "owner": analysis.formula_owner,
            "registry_key":
                analysis.formula_registry_key,
            "research_validated":
                analysis.research_validated,
        },

        "authority": {
            "is_signal":
                analysis.is_signal,
            "is_opportunity":
                analysis.is_opportunity,
            "is_decision":
                analysis.is_decision,
        },

        "warnings":
            list(analysis.warnings),

        "errors":
            list(analysis.errors),
    }


# ============================================================
# 5.5 MULTI-TIMEFRAME SUMMARY
# ============================================================

def summarize_multitimeframe_boundary(
    result: Optional[MultiTimeframeBoundary],
) -> Dict[str, Any]:

    if result is None:
        return {
            "available": False,
            "status": BoundaryStatus.INSUFFICIENT_DATA.value,
        }

    strongest_price = None

    if result.strongest_boundary is not None:
        strongest_price = (
            result.strongest_boundary.price
        )

    return {
        "available": True,

        "status":
            result.status.value,

        "instrument_id":
            result.instrument_id,

        "symbol":
            result.symbol,

        "timeframes": [
            timeframe.value
            if isinstance(timeframe, Timeframe)
            else str(timeframe)
            for timeframe in result.analyses.keys()
        ],

        "analysis_count":
            len(result.analyses),

        "relation":
            result.relation.value,

        "dominant_boundary_type":
            result.dominant_boundary_type.value,

        "dominant_direction":
            result.dominant_direction.value,

        "strongest_boundary":
            strongest_price,

        "average_confidence":
            result.average_confidence.value,

        "research_validated":
            result.research_validated,

        "warnings":
            list(result.warnings),

        "errors":
            list(result.errors),
    }


# ============================================================
# 5.6 RESULT SUMMARY
# ============================================================

def boundary_result_summary(
    result: Optional[BoundaryEngineResult],
) -> Dict[str, Any]:

    if result is None:
        return {
            "available": False,
            "status": BoundaryStatus.INSUFFICIENT_DATA.value,
        }

    summary = {
        "available": True,

        "engine":
            BOUNDARY_ENGINE,

        "version":
            BOUNDARY_ENGINE_VERSION,

        "status":
            result.status.value,

        "instrument_id":
            result.instrument_id,

        "symbol":
            result.symbol,

        "research_validated":
            result.research_validated,

        "formula": {
            "id":
                result.formula_id,
            "version":
                result.formula_version,
        },

        "single_timeframe":
            summarize_boundary_analysis(
                result.analysis
            ),

        "multi_timeframe":
            summarize_multitimeframe_boundary(
                result.multi_timeframe
            ),

        "warnings":
            list(result.warnings),

        "errors":
            list(result.errors),

        "authority": {
            "boundary_intelligence":
                True,
            "signal":
                False,
            "opportunity":
                False,
            "decision":
                False,
            "d13":
                False,
            "risk":
                False,
            "cas":
                False,
            "execution":
                False,
        },
    }

    return summary


# ============================================================
# 5.7 FORMULA REGISTRY SUMMARY
# ============================================================

def boundary_formula_registry_summary(
    registry: Optional[
        BoundaryFormulaRegistry
    ] = None,
) -> Dict[str, Any]:

    if registry is None:
        registry = get_boundary_formula_registry()

    if registry is None:
        return {
            "available": False,
            "count": 0,
            "validated_count": 0,
            "enabled_count": 0,
            "descriptors": [],
        }

    descriptors = registry.descriptors()

    serialized = []

    for descriptor in descriptors:

        serialized.append(
            serialize_boundary_formula_descriptor(
                descriptor
            )
        )

    return {
        "available": True,
        "count": len(descriptors),

        "validated_count": sum(
            1
            for descriptor in descriptors
            if descriptor.validated
        ),

        "enabled_count": sum(
            1
            for descriptor in descriptors
            if descriptor.enabled
        ),

        "validated_and_enabled_count": sum(
            1
            for descriptor in descriptors
            if descriptor.validated
            and descriptor.enabled
        ),

        "descriptors": serialized,
    }


# ============================================================
# 5.8 CONTRACT INTEGRITY
# ============================================================

def validate_boundary_contract_integrity() -> Dict[str, Any]:

    errors: List[str] = []
    warnings: List[str] = []

    required_authority = {
        "boundary_analysis": True,
        "support_boundary_analysis": True,
        "resistance_boundary_analysis": True,
        "range_boundary_analysis": True,
        "breakout_boundary_analysis": True,
        "breakdown_boundary_analysis": True,
        "research_formula_consumption": True,

        "research_formula_generation": False,
        "fixed_formula_assumption": False,
        "guessed_formula": False,
        "silent_formula_substitution": False,

        "breakout_generation": False,
        "confirmation_generation": False,
        "opportunity_generation": False,
        "decision_generation": False,
        "d13_generation": False,
        "risk_generation": False,
        "cas_generation": False,
        "execution_generation": False,
        "order_generation": False,
        "position_generation": False,
        "upstream_mutation": False,
    }

    for key, expected in required_authority.items():

        actual = BOUNDARY_ENGINE_AUTHORITY.get(
            key
        )

        if actual is not expected:
            errors.append(
                f"authority mismatch: {key} "
                f"expected={expected} actual={actual}"
            )

    contract = BOUNDARY_ENGINE_CONTRACT

    if contract.get(
        "default_formula_allowed"
    ) is not False:
        errors.append(
            "default formula policy is invalid"
        )

    if contract.get(
        "guessing_allowed"
    ) is not False:
        errors.append(
            "formula guessing policy is invalid"
        )

    if contract.get(
        "silent_substitution_allowed"
    ) is not False:
        errors.append(
            "silent substitution policy is invalid"
        )

    if contract.get(
        "engine_generates_formula"
    ) is not False:
        errors.append(
            "engine formula generation policy is invalid"
        )

    if contract.get(
        "validated_required"
    ) is not True:
        errors.append(
            "validated research formula must be required"
        )

    if contract.get(
        "version_traceability"
    ) is not True:
        errors.append(
            "formula version traceability must be required"
        )

    if not contract.get("downstream"):
        warnings.append(
            "no downstream consumers declared"
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


# ============================================================
# 5.9 MASTER CONTRACT MANIFEST
# ============================================================

def boundary_engine_contract_manifest() -> Dict[str, Any]:

    return {
        "engine":
            BOUNDARY_ENGINE,

        "version":
            BOUNDARY_ENGINE_VERSION,

        "name":
            BOUNDARY_ENGINE_NAME,

        "layer":
            "INTELLIGENCE_ENGINE",

        "role":
            "BOUNDARY_INTELLIGENCE",

        "authority_owner":
            "UPSTREAM_BOUNDARY_INTELLIGENCE",

        "importance":
            "CLASS_A_INTELLIGENCE_COMPONENT",

        "pipeline": [
            "RAW_MARKET_DATA",
            "NORMALIZED_MARKET_DATA",
            "STRUCTURE_INTELLIGENCE",
            "ACCUMULATION_INTELLIGENCE",
            "DISTRIBUTION_INTELLIGENCE",
            "BOUNDARY_INPUT",
            "VALIDATED_RESEARCH_FORMULA",
            "BOUNDARY_ANALYSIS",
            "MULTI_TIMEFRAME_BOUNDARY",
            "BREAKOUT_ENGINE",
            "CONFIRMATION_ENGINE",
            "OPPORTUNITY_ENGINE",
            "EQUITY_SCANNER",
            "FUTURE_SCANNER",
        ],

        "inputs": [
            "NORMALIZED_OHLCV",
            "STRUCTURE_INTELLIGENCE",
            "ACCUMULATION_INTELLIGENCE",
            "DISTRIBUTION_INTELLIGENCE",
            "MULTI_TIMEFRAME_CONTEXT",
            "RESEARCH_FORMULA_REGISTRY",
            "RESEARCH_VALIDATION_METADATA",
        ],

        "outputs": [
            "SUPPORT_BOUNDARY",
            "RESISTANCE_BOUNDARY",
            "RANGE_HIGH",
            "RANGE_LOW",
            "BREAKOUT_BOUNDARY",
            "BREAKDOWN_BOUNDARY",
            "INVALIDATION_BOUNDARY",
            "MULTI_TIMEFRAME_BOUNDARY",
            "BOUNDARY_ANALYSIS",
            "BOUNDARY_ENGINE_RESULT",
            "BOUNDARY_ENGINE_SNAPSHOT",
        ],

        "formula_policy": {
            "registry_based": True,
            "pluggable": True,
            "explicit_selection": True,
            "validated_required": True,
            "version_traceability": True,
            "default_formula_allowed": False,
            "formula_guessing_allowed": False,
            "silent_substitution_allowed": False,
            "engine_generates_formula": False,
        },

        "truth_policy": {
            "math_first": True,
            "research_first": True,

            "structure_context_is_input": True,
            "accumulation_context_is_input": True,
            "distribution_context_is_input": True,

            "boundary_is_not_breakout": True,
            "boundary_is_not_signal": True,
            "boundary_is_not_decision": True,

            "pattern_secondary": True,
            "pattern_cannot_override_math": True,

            "upstream_truth_preserved": True,
        },

        "research_hooks": [
            "SUPPORT_BOUNDARY_FORMULA",
            "RESISTANCE_BOUNDARY_FORMULA",
            "RANGE_BOUNDARY_FORMULA",
            "BREAKOUT_BOUNDARY_FORMULA",
            "BREAKDOWN_BOUNDARY_FORMULA",
            "BOUNDARY_STRENGTH_FORMULA",
            "BOUNDARY_QUALITY_FORMULA",
            "BOUNDARY_INVALIDATION_FORMULA",
            "MULTI_TIMEFRAME_BOUNDARY_FORMULA",
        ],

        "forbidden_authority": [
            "FORMULA_GENERATION",
            "BREAKOUT_GENERATION",
            "CONFIRMATION_GENERATION",
            "OPPORTUNITY_GENERATION",
            "SIGNAL_GENERATION",
            "DECISION_GENERATION",
            "D13_GENERATION",
            "RISK_GENERATION",
            "CAS_GENERATION",
            "EXECUTION_GENERATION",
            "ORDER_GENERATION",
            "POSITION_GENERATION",
            "UPSTREAM_MUTATION",
        ],
    }


# ============================================================
# 5.10 MODULE INTEGRITY
# ============================================================

def validate_boundary_module_integrity() -> Dict[str, Any]:

    errors: List[str] = []
    warnings: List[str] = []

    contract_check = (
        validate_boundary_contract_integrity()
    )

    errors.extend(
        contract_check["errors"]
    )

    warnings.extend(
        contract_check["warnings"]
    )

    part4_check = (
        boundary_part4_contract_check()
    )

    if not part4_check["passed"]:
        errors.append(
            "Part 4 contract check failed"
        )

    required_callables = [
        normalize_boundary_input,
        normalize_multitimeframe_boundary_input,
        validate_boundary_input,
        build_boundary_window,
        create_boundary_measurement,

        analyze_boundary,
        analyze_multitimeframe_boundary,
        run_boundary_engine,

        serialize_boundary_input,
        serialize_boundary_analysis,
        serialize_boundary_engine_result,

        validate_boundary_analysis,
        validate_multitimeframe_boundary,
        validate_boundary_engine_result,

        build_boundary_engine_health,
        boundary_engine_operational_check,
        boundary_engine_diagnostics,

        create_boundary_request,
        execute_boundary_request,

        boundary_result_is_ready,
        boundary_result_has_validated_research,

        summarize_boundary_analysis,
        summarize_multitimeframe_boundary,
        boundary_result_summary,

        validate_boundary_contract_integrity,
        boundary_engine_contract_manifest,
    ]

    for function in required_callables:

        if not callable(function):
            errors.append(
                f"required callable unavailable: {function}"
            )

    manifest = boundary_engine_contract_manifest()

    if manifest["engine"] != BOUNDARY_ENGINE:
        errors.append(
            "manifest engine mismatch"
        )

    if manifest["version"] != BOUNDARY_ENGINE_VERSION:
        errors.append(
            "manifest version mismatch"
        )

    if manifest["role"] != "BOUNDARY_INTELLIGENCE":
        errors.append(
            "manifest role mismatch"
        )

    if manifest["formula_policy"][
        "engine_generates_formula"
    ]:
        errors.append(
            "manifest permits engine-generated formula"
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "manifest":
            manifest,
    }


# ============================================================
# 5.11 MODULE CHECK
# ============================================================

def boundary_engine_module_check() -> Dict[str, Any]:

    integrity = (
        validate_boundary_module_integrity()
    )

    health = (
        build_boundary_engine_health()
    )

    return {
        "engine":
            BOUNDARY_ENGINE,

        "version":
            BOUNDARY_ENGINE_VERSION,

        "module_integrity":
            integrity["valid"],

        "authority_valid":
            health.authority_valid,

        "operational":
            health.operational,

        "validated_formula_available":
            health.validated_formula_available,

        "research_formula_generated_here":
            health.research_formula_generated_here,

        "opportunity_generation":
            health.opportunity_generation,

        "decision_generation":
            health.decision_generation,

        "d13_generation":
            health.d13_generation,

        "risk_generation":
            health.risk_generation,

        "cas_generation":
            health.cas_generation,

        "execution_generation":
            health.execution_generation,

        "errors":
            integrity["errors"]
            + health.errors,

        "warnings":
            integrity["warnings"]
            + health.warnings,
    }


# ============================================================
# 5.12 FINAL ENGINE SELF CHECK
# ============================================================

def boundary_engine_self_check() -> Dict[str, Any]:

    part4 = boundary_part4_contract_check()

    contract = validate_boundary_contract_integrity()

    module = validate_boundary_module_integrity()

    manifest = boundary_engine_contract_manifest()

    checks = {
        "part4_passed":
            part4["passed"],

        "contract_integrity":
            contract["valid"],

        "module_integrity":
            module["valid"],

        "authority_valid":
            validate_boundary_authority(),

        "manifest_engine_correct":
            manifest["engine"] == BOUNDARY_ENGINE,

        "manifest_version_correct":
            manifest["version"]
            == BOUNDARY_ENGINE_VERSION,

        "formula_registry_based":
            manifest["formula_policy"][
                "registry_based"
            ],

        "validated_formula_required":
            manifest["formula_policy"][
                "validated_required"
            ],

        "version_traceability":
            manifest["formula_policy"][
                "version_traceability"
            ],

        "no_default_formula":
            manifest["formula_policy"][
                "default_formula_allowed"
            ] is False,

        "no_formula_guessing":
            manifest["formula_policy"][
                "formula_guessing_allowed"
            ] is False,

        "no_silent_substitution":
            manifest["formula_policy"][
                "silent_substitution_allowed"
            ] is False,

        "engine_does_not_generate_formula":
            manifest["formula_policy"][
                "engine_generates_formula"
            ] is False,

        "boundary_not_breakout":
            manifest["truth_policy"][
                "boundary_is_not_breakout"
            ],

        "boundary_not_signal":
            manifest["truth_policy"][
                "boundary_is_not_signal"
            ],

        "boundary_not_decision":
            manifest["truth_policy"][
                "boundary_is_not_decision"
            ],

        "math_first":
            manifest["truth_policy"][
                "math_first"
            ],

        "research_first":
            manifest["truth_policy"][
                "research_first"
            ],

        "pattern_cannot_override_math":
            manifest["truth_policy"][
                "pattern_cannot_override_math"
            ],

        "upstream_truth_preserved":
            manifest["truth_policy"][
                "upstream_truth_preserved"
            ],

        "opportunity_generation_forbidden":
            BOUNDARY_ENGINE_AUTHORITY[
                "opportunity_generation"
            ] is False,

        "decision_generation_forbidden":
            BOUNDARY_ENGINE_AUTHORITY[
                "decision_generation"
            ] is False,

        "d13_generation_forbidden":
            BOUNDARY_ENGINE_AUTHORITY[
                "d13_generation"
            ] is False,

        "risk_generation_forbidden":
            BOUNDARY_ENGINE_AUTHORITY[
                "risk_generation"
            ] is False,

        "execution_generation_forbidden":
            BOUNDARY_ENGINE_AUTHORITY[
                "execution_generation"
            ] is False,
    }

    passed = all(checks.values())

    return {
        "engine":
            BOUNDARY_ENGINE,

        "version":
            BOUNDARY_ENGINE_VERSION,

        "passed":
            passed,

        "checks":
            checks,

        "contract":
            contract,

        "module":
            module,

        "manifest":
            manifest,
    }


# ============================================================
# 5.13 DEFAULT REQUEST
# ============================================================

def create_default_boundary_engine_request(
    instrument_id: str = "UNKNOWN",
    symbol: str = "UNKNOWN",
    asset_class: str = "UNKNOWN",
    market_id: str = "UNKNOWN",
    timeframe: Timeframe = Timeframe.M15,
) -> BoundaryEngineRequest:

    input_data = BoundaryInput(
        instrument_id=instrument_id,
        symbol=symbol,
        asset_class=asset_class,
        market_id=market_id,
        exchange=None,
        timeframe=timeframe,

        timestamps=[],
        opens=[],
        highs=[],
        lows=[],
        closes=[],
        volumes=[],

        structure_context=None,
        accumulation_context=None,
        distribution_context=None,

        source="DEFAULT_REQUEST",
        metadata={
            "default_request": True,
            "intelligence_generated": False,
        },
    )

    return create_boundary_request(
        input_data=input_data,
        metadata={
            "default_request": True,
            "formula_required": True,
            "research_validated_formula_required": True,
        },
    )


# ============================================================
# 5.14 SINGLE-TIMEFRAME CONVENIENCE API
# ============================================================

def analyze_single_timeframe_boundary(
    input_data: BoundaryInput,
    formula_id: str,
    formula_version: Optional[str] = None,
    registry: Optional[
        BoundaryFormulaRegistry
    ] = None,
) -> BoundaryEngineResult:

    request = create_boundary_request(
        input_data=input_data,
        formula_id=formula_id,
        formula_version=formula_version,
    )

    return execute_boundary_request(
        request,
        registry=registry,
    )


# ============================================================
# 5.15 MULTI-TIMEFRAME CONVENIENCE API
# ============================================================

def analyze_boundary_timeframes(
    input_data: MultiTimeframeBoundaryInput,
    formula_map: Dict[Timeframe, str],
    formula_version_map: Optional[
        Dict[Timeframe, str]
    ] = None,
    registry: Optional[
        BoundaryFormulaRegistry
    ] = None,
) -> BoundaryEngineResult:

    request = create_boundary_request(
        multi_timeframe_input=input_data,
        formula_map=formula_map,
        formula_version_map=
            formula_version_map or {},
    )

    return execute_boundary_request(
        request,
        registry=registry,
    )


# ============================================================
# 5.16 PART-5 CONTRACT CHECK
# ============================================================

def boundary_part5_contract_check() -> Dict[str, Any]:

    checks = {
        "request_factory":
            callable(create_boundary_request),

        "request_executor":
            callable(execute_boundary_request),

        "result_ready_helper":
            callable(boundary_result_is_ready),

        "validated_research_helper":
            callable(
                boundary_result_has_validated_research
            ),

        "summary_api":
            callable(boundary_result_summary),

        "registry_summary":
            callable(
                boundary_formula_registry_summary
            ),

        "contract_manifest":
            callable(
                boundary_engine_contract_manifest
            ),

        "module_integrity":
            callable(
                validate_boundary_module_integrity
            ),

        "module_check":
            callable(
                boundary_engine_module_check
            ),

        "engine_self_check":
            callable(
                boundary_engine_self_check
            ),

        "default_request":
            callable(
                create_default_boundary_engine_request
            ),

        "single_timeframe_api":
            callable(
                analyze_single_timeframe_boundary
            ),

        "multi_timeframe_api":
            callable(
                analyze_boundary_timeframes
            ),

        "formula_generation_forbidden":
            BOUNDARY_ENGINE_AUTHORITY[
                "research_formula_generation"
            ] is False,

        "opportunity_generation_forbidden":
            BOUNDARY_ENGINE_AUTHORITY[
                "opportunity_generation"
            ] is False,

        "decision_generation_forbidden":
            BOUNDARY_ENGINE_AUTHORITY[
                "decision_generation"
            ] is False,

        "d13_generation_forbidden":
            BOUNDARY_ENGINE_AUTHORITY[
                "d13_generation"
            ] is False,

        "risk_generation_forbidden":
            BOUNDARY_ENGINE_AUTHORITY[
                "risk_generation"
            ] is False,

        "execution_generation_forbidden":
            BOUNDARY_ENGINE_AUTHORITY[
                "execution_generation"
            ] is False,
    }

    return {
        "engine":
            BOUNDARY_ENGINE,

        "version":
            BOUNDARY_ENGINE_VERSION,

        "part":
            5,

        "passed":
            all(checks.values()),

        "checks":
            checks,
    }


# ============================================================
# 5.17 FINAL MODULE MANIFEST
# ============================================================

BOUNDARY_ENGINE_MODULE_MANIFEST = {
    "module":
        "app.ui.discovery.engines.boundary_engine",

    "engine":
        BOUNDARY_ENGINE,

    "version":
        BOUNDARY_ENGINE_VERSION,

    "name":
        BOUNDARY_ENGINE_NAME,

    "layer":
        "INTELLIGENCE_ENGINE",

    "role":
        "BOUNDARY_INTELLIGENCE",

    "importance":
        "CLASS_A_INTELLIGENCE_COMPONENT",

    "parts_completed": [
        "PART_1_CONTRACT",
        "PART_2_NORMALIZATION_FORMULA_REGISTRY",
        "PART_3_INTELLIGENCE_ORCHESTRATION",
        "PART_4_VALIDATION_HEALTH_DIAGNOSTICS",
        "PART_5_EXECUTION_MANIFEST_FINAL_CHECK",
    ],

    "pipeline": [
        "RAW_MARKET_DATA",
        "NORMALIZED_MARKET_DATA",
        "STRUCTURE_INTELLIGENCE",
        "ACCUMULATION_INTELLIGENCE",
        "DISTRIBUTION_INTELLIGENCE",
        "BOUNDARY_INPUT",
        "VALIDATED_RESEARCH_FORMULA",
        "BOUNDARY_ANALYSIS",
        "MULTI_TIMEFRAME_BOUNDARY",
        "BREAKOUT_ENGINE",
        "CONFIRMATION_ENGINE",
        "OPPORTUNITY_ENGINE",
        "EQUITY_SCANNER",
        "FUTURE_SCANNER",
    ],

    "formula_policy": {
        "registry_based": True,
        "pluggable": True,
        "explicit_selection": True,
        "validated_required": True,
        "version_traceability": True,
        "default_formula_allowed": False,
        "formula_guessing_allowed": False,
        "silent_substitution_allowed": False,
        "engine_generates_formula": False,
    },

    "truth_policy": {
        "math_first": True,
        "research_first": True,

        "structure_context_is_input": True,
        "accumulation_context_is_input": True,
        "distribution_context_is_input": True,

        "boundary_is_not_breakout": True,
        "boundary_is_not_signal": True,
        "boundary_is_not_decision": True,

        "pattern_secondary": True,
        "pattern_cannot_override_math": True,

        "upstream_truth_preserved": True,
    },

    "research_hooks": [
        "SUPPORT_BOUNDARY_FORMULA",
        "RESISTANCE_BOUNDARY_FORMULA",
        "RANGE_BOUNDARY_FORMULA",
        "BREAKOUT_BOUNDARY_FORMULA",
        "BREAKDOWN_BOUNDARY_FORMULA",
        "BOUNDARY_STRENGTH_FORMULA",
        "BOUNDARY_QUALITY_FORMULA",
        "BOUNDARY_INVALIDATION_FORMULA",
        "MULTI_TIMEFRAME_BOUNDARY_FORMULA",
    ],

    "authority": {
        "boundary_intelligence": True,
        "formula_generation": False,
        "breakout_generation": False,
        "confirmation_generation": False,
        "opportunity_generation": False,
        "signal_generation": False,
        "decision_generation": False,
        "d13_generation": False,
        "risk_generation": False,
        "cas_generation": False,
        "execution_generation": False,
        "order_generation": False,
        "position_generation": False,
        "upstream_mutation": False,
    },

    "downstream": [
        "BREAKOUT_ENGINE",
        "CONFIRMATION_ENGINE",
        "RELATIONSHIP_ENGINE",
        "OPPORTUNITY_ENGINE",
        "EQUITY_SCANNER",
        "FUTURE_SCANNER",
    ],
}


# ============================================================
# 5.18 FINAL ASSERTION
# ============================================================

if __name__ == "__main__":

    final_check = boundary_engine_self_check()

    if not final_check["passed"]:
        raise RuntimeError(
            "BOUNDARY ENGINE FINAL SELF-CHECK FAILED: "
            + str(final_check)
        )

    print(
        f"{BOUNDARY_ENGINE} "
        f"v{BOUNDARY_ENGINE_VERSION} "
        f"FINAL SELF-CHECK: PASSED"
    )