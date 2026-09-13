# ============================================================
# ROBOMLM_PLUS
# regime_engine.py
#
# PART 1 — REGIME ENGINE FOUNDATION
#
# Responsibility:
#   Raw Market Data
#        ↓
#   Market Regime Measurement
#        ↓
#   Normalized Regime State
#
# IMPORTANT:
#   - This engine does NOT make final trade decisions.
#   - This engine does NOT generate BUY/SELL orders.
#   - D13 remains final decision authority.
#   - No simulated/fabricated market values.
#   - Missing inputs remain UNKNOWN rather than invented.
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence
import math
import statistics


# ============================================================
# ENUMS
# ============================================================

class RegimeType(str, Enum):
    UNKNOWN = "UNKNOWN"
    TRENDING = "TRENDING"
    RANGING = "RANGING"
    COMPRESSED = "COMPRESSED"
    EXPANDING = "EXPANDING"
    TRANSITION = "TRANSITION"


class DirectionBias(str, Enum):
    UNKNOWN = "UNKNOWN"
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


class VolatilityState(str, Enum):
    UNKNOWN = "UNKNOWN"
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


class DataQuality(str, Enum):
    INVALID = "INVALID"
    PARTIAL = "PARTIAL"
    USABLE = "USABLE"
    HIGH = "HIGH"


# ============================================================
# RAW MARKET INPUT CONTRACT
# ============================================================

@dataclass
class RegimeMarketInput:
    """
    Raw/near-raw market information supplied by the upstream
    market-data layer.

    The engine calculates regime information from these values.
    It must not manufacture missing market values.
    """

    instrument: str
    timestamp: datetime

    price: Optional[float] = None

    # OHLC if available from real candle/feed data
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    close_price: Optional[float] = None

    volume: Optional[float] = None

    # Optional derivatives / participation fields
    open_interest: Optional[float] = None

    bid_price: Optional[float] = None
    ask_price: Optional[float] = None

    # Historical observations supplied by upstream data layer.
    # These are market observations, not generated signals.
    price_history: Sequence[float] = field(default_factory=list)
    volume_history: Sequence[float] = field(default_factory=list)

    # Optional externally calculated volatility observations.
    atr: Optional[float] = None
    atr_history: Sequence[float] = field(default_factory=list)

    # Optional source/feed metadata
    market: Optional[str] = None
    exchange: Optional[str] = None
    timeframe: Optional[str] = None
    data_source: Optional[str] = None


# ============================================================
# REGIME MEASUREMENTS
# ============================================================

@dataclass
class RegimeMeasurements:
    """
    Raw calculated measurements used to classify the market state.

    These are measurements, not final trading decisions.
    """

    price_change: Optional[float] = None
    price_change_pct: Optional[float] = None

    range_value: Optional[float] = None
    range_pct: Optional[float] = None

    volatility_value: Optional[float] = None
    volatility_ratio: Optional[float] = None

    trend_strength: Optional[float] = None
    directional_efficiency: Optional[float] = None

    volume_ratio: Optional[float] = None

    spread_value: Optional[float] = None
    spread_pct: Optional[float] = None

    compression_score: Optional[float] = None
    expansion_score: Optional[float] = None

    direction_bias: DirectionBias = DirectionBias.UNKNOWN


# ============================================================
# NORMALIZED REGIME RESULT
# ============================================================

@dataclass
class RegimeResult:
    """
    Standard output contract consumed by downstream engines.

    No final BUY/SELL decision is produced here.
    """

    instrument: str
    timestamp: str

    regime: RegimeType
    direction_bias: DirectionBias
    volatility_state: VolatilityState

    regime_strength: float
    transition_score: float

    data_quality: DataQuality

    measurements: RegimeMeasurements

    evidence: List[str] = field(default_factory=list)

    warnings: List[str] = field(default_factory=list)

    source: Optional[str] = None

    engine: str = "RegimeEngine"
    engine_version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================
# REGIME ENGINE
# ============================================================

class RegimeEngine:
    """
    ROBOMLM Market Regime Engine.

    Purpose:
        Determine the current structural/volatility environment
        from actual market observations.

    This engine does NOT:
        - generate final BUY/SELL
        - select an option contract
        - authorize execution
        - override D13
        - fabricate missing data
    """

    ENGINE_NAME = "RegimeEngine"
    ENGINE_VERSION = "1.0.0"

    # These are initial engineering baselines only.
    # They remain configurable and must be validated against
    # real-market/BlackBox outcomes before being treated as final.
    DEFAULT_CONFIG = {
        "minimum_price_history": 10,
        "minimum_volume_history": 5,

        # Trend classification baselines
        "trend_strength_threshold": 0.55,
        "range_strength_threshold": 0.35,

        # Volatility ratio = current volatility / baseline volatility
        "volatility_low_ratio": 0.70,
        "volatility_high_ratio": 1.30,
        "volatility_extreme_ratio": 2.00,

        # Compression / expansion
        "compression_ratio": 0.70,
        "expansion_ratio": 1.30,

        # Direction
        "direction_threshold": 0.15,

        # Spread sanity threshold
        "maximum_reasonable_spread_pct": 0.50,
    }

    def __init__(
        self,
        config: Optional[Dict[str, float]] = None,
    ) -> None:

        self.config: Dict[str, float] = dict(self.DEFAULT_CONFIG)

        if config:
            self.config.update(config)

    # ========================================================
    # PUBLIC ENTRY POINT
    # ========================================================

    def evaluate(
        self,
        market_input: RegimeMarketInput,
    ) -> RegimeResult:

        quality = self._validate_input(market_input)

        measurements = self._calculate_measurements(
            market_input
        )

        volatility_state = self._classify_volatility(
            measurements.volatility_ratio
        )

        regime = self._classify_regime(
            measurements=measurements,
            volatility_state=volatility_state,
            data_quality=quality,
        )

        regime_strength = self._calculate_regime_strength(
            measurements,
            regime,
        )

        transition_score = self._calculate_transition_score(
            measurements,
            volatility_state,
        )

        evidence = self._build_evidence(
            measurements,
            regime,
            volatility_state,
        )

        warnings = self._build_warnings(
            market_input,
            measurements,
            quality,
        )

        return RegimeResult(
            instrument=market_input.instrument,
            timestamp=self._timestamp(market_input.timestamp),

            regime=regime,
            direction_bias=measurements.direction_bias,
            volatility_state=volatility_state,

            regime_strength=regime_strength,
            transition_score=transition_score,

            data_quality=quality,

            measurements=measurements,

            evidence=evidence,
            warnings=warnings,

            source=market_input.data_source,

            engine=self.ENGINE_NAME,
            engine_version=self.ENGINE_VERSION,
        )

    # ========================================================
    # INPUT VALIDATION
    # ========================================================

    def _validate_input(
        self,
        data: RegimeMarketInput,
    ) -> DataQuality:

        if not data.instrument:
            return DataQuality.INVALID

        if data.price is None:
            return DataQuality.INVALID

        if not self._is_positive(data.price):
            return DataQuality.INVALID

        history_count = len(data.price_history)

        if history_count < self.config["minimum_price_history"]:
            return DataQuality.PARTIAL

        usable_fields = 0

        if data.volume is not None:
            usable_fields += 1

        if data.volume_history:
            usable_fields += 1

        if data.atr is not None:
            usable_fields += 1

        if data.atr_history:
            usable_fields += 1

        if data.bid_price is not None:
            usable_fields += 1

        if data.ask_price is not None:
            usable_fields += 1

        if usable_fields >= 3:
            return DataQuality.HIGH

        return DataQuality.USABLE

    # ========================================================
    # MEASUREMENTS
    # ========================================================

    def _calculate_measurements(
        self,
        data: RegimeMarketInput,
    ) -> RegimeMeasurements:

        measurements = RegimeMeasurements()

        prices = self._clean_series(
            data.price_history
        )

        current_price = (
            data.close_price
            if data.close_price is not None
            else data.price
        )

        # ----------------------------------------------------
        # PRICE CHANGE
        # ----------------------------------------------------

        if prices and current_price is not None:

            previous_price = prices[-1]

            if previous_price > 0:

                measurements.price_change = (
                    current_price - previous_price
                )

                measurements.price_change_pct = (
                    measurements.price_change
                    / previous_price
                ) * 100.0

        # ----------------------------------------------------
        # CURRENT BAR RANGE
        # ----------------------------------------------------

        if (
            data.high_price is not None
            and data.low_price is not None
            and current_price is not None
        ):

            if data.high_price >= data.low_price:

                measurements.range_value = (
                    data.high_price - data.low_price
                )

                if current_price > 0:

                    measurements.range_pct = (
                        measurements.range_value
                        / current_price
                    ) * 100.0

        # ----------------------------------------------------
        # VOLATILITY
        # ----------------------------------------------------

        volatility_value = self._calculate_volatility(
            prices
        )

        if data.atr is not None and self._is_positive(data.atr):
            volatility_value = data.atr

        measurements.volatility_value = volatility_value

        measurements.volatility_ratio = (
            self._calculate_volatility_ratio(
                volatility_value,
                data.atr_history,
                prices,
            )
        )

        # ----------------------------------------------------
        # TREND / DIRECTION
        # ----------------------------------------------------

        measurements.directional_efficiency = (
            self._calculate_directional_efficiency(
                prices
            )
        )

        measurements.trend_strength = (
            self._calculate_trend_strength(
                prices
            )
        )

        measurements.direction_bias = (
            self._calculate_direction_bias(
                prices
            )
        )

        # ----------------------------------------------------
        # VOLUME
        # ----------------------------------------------------

        measurements.volume_ratio = (
            self._calculate_volume_ratio(
                data.volume,
                data.volume_history,
            )
        )

        # ----------------------------------------------------
        # SPREAD
        # ----------------------------------------------------

        if (
            data.bid_price is not None
            and data.ask_price is not None
            and current_price is not None
            and data.bid_price > 0
            and data.ask_price >= data.bid_price
        ):

            measurements.spread_value = (
                data.ask_price - data.bid_price
            )

            if current_price > 0:

                measurements.spread_pct = (
                    measurements.spread_value
                    / current_price
                ) * 100.0

        # ----------------------------------------------------
        # COMPRESSION / EXPANSION
        # ----------------------------------------------------

        (
            measurements.compression_score,
            measurements.expansion_score,
        ) = self._calculate_compression_expansion(
            measurements.volatility_ratio
        )

        return measurements

    # ========================================================
    # VOLATILITY
    # ========================================================

    def _calculate_volatility(
        self,
        prices: Sequence[float],
    ) -> Optional[float]:

        if len(prices) < 3:
            return None

        clean = self._clean_series(prices)

        if len(clean) < 3:
            return None

        returns: List[float] = []

        for previous, current in zip(
            clean[:-1],
            clean[1:],
        ):

            if previous <= 0:
                continue

            returns.append(
                (current - previous) / previous
            )

        if len(returns) < 2:
            return None

        try:
            return statistics.pstdev(returns)
        except statistics.StatisticsError:
            return None

    def _calculate_volatility_ratio(
        self,
        current_volatility: Optional[float],
        atr_history: Sequence[float],
        prices: Sequence[float],
    ) -> Optional[float]:

        if current_volatility is None:
            return None

        baseline: Optional[float] = None

        # Prefer supplied real volatility history.
        clean_atr = self._clean_series(atr_history)

        if len(clean_atr) >= 3:

            baseline = statistics.median(
                clean_atr
            )

        # If ATR history is unavailable, use rolling
        # historical return volatility as baseline.
        if baseline is None:

            clean_prices = self._clean_series(prices)

            if len(clean_prices) >= 6:

                historical_volatilities = []

                window = min(10, len(clean_prices))

                for index in range(
                    window,
                    len(clean_prices) + 1,
                ):

                    segment = clean_prices[
                        index - window:index
                    ]

                    value = self._calculate_volatility(
                        segment
                    )

                    if value is not None:
                        historical_volatilities.append(
                            value
                        )

                if historical_volatilities:

                    baseline = statistics.median(
                        historical_volatilities
                    )

        if baseline is None or baseline <= 0:
            return None

        return current_volatility / baseline

    # ========================================================
    # TREND STRENGTH
    # ========================================================

    def _calculate_directional_efficiency(
        self,
        prices: Sequence[float],
    ) -> Optional[float]:

        clean = self._clean_series(prices)

        if len(clean) < 3:
            return None

        net_move = abs(
            clean[-1] - clean[0]
        )

        path = 0.0

        for previous, current in zip(
            clean[:-1],
            clean[1:],
        ):

            path += abs(
                current - previous
            )

        if path <= 0:
            return 0.0

        # 0 = highly noisy path
        # 1 = perfectly directional path
        efficiency = net_move / path

        return self._clamp(
            efficiency,
            0.0,
            1.0,
        )

    def _calculate_trend_strength(
        self,
        prices: Sequence[float],
    ) -> Optional[float]:

        efficiency = self._calculate_directional_efficiency(
            prices
        )

        if efficiency is None:
            return None

        # Initial normalized measurement.
        # This is NOT a final probability.
        return self._clamp(
            efficiency,
            0.0,
            1.0,
        )

    # ========================================================
    # DIRECTION BIAS
    # ========================================================

    def _calculate_direction_bias(
        self,
        prices: Sequence[float],
    ) -> DirectionBias:

        clean = self._clean_series(prices)

        if len(clean) < 3:
            return DirectionBias.UNKNOWN

        first = clean[0]
        last = clean[-1]

        if first <= 0:
            return DirectionBias.UNKNOWN

        move = (
            last - first
        ) / first

        threshold = (
            self.config["direction_threshold"]
            / 100.0
        )

        if move >= threshold:
            return DirectionBias.BULLISH

        if move <= -threshold:
            return DirectionBias.BEARISH

        return DirectionBias.NEUTRAL

    # ========================================================
    # VOLUME
    # ========================================================

    def _calculate_volume_ratio(
        self,
        current_volume: Optional[float],
        volume_history: Sequence[float],
    ) -> Optional[float]:

        if current_volume is None:
            return None

        if current_volume < 0:
            return None

        history = self._clean_non_negative_series(
            volume_history
        )

        if len(history) < self.config["minimum_volume_history"]:
            return None

        baseline = statistics.median(history)

        if baseline <= 0:
            return None

        return current_volume / baseline

    # ========================================================
    # COMPRESSION / EXPANSION
    # ========================================================

    def _calculate_compression_expansion(
        self,
        volatility_ratio: Optional[float],
    ) -> tuple[Optional[float], Optional[float]]:

        if volatility_ratio is None:
            return None, None

        compression = 0.0
        expansion = 0.0

        compression_threshold = (
            self.config["compression_ratio"]
        )

        expansion_threshold = (
            self.config["expansion_ratio"]
        )

        if volatility_ratio <= compression_threshold:

            compression = self._clamp(
                1.0 - volatility_ratio,
                0.0,
                1.0,
            )

        if volatility_ratio >= expansion_threshold:

            expansion = self._clamp(
                volatility_ratio / expansion_threshold - 1.0,
                0.0,
                1.0,
            )

        return compression, expansion

    # ========================================================
    # REGIME CLASSIFICATION
    # ========================================================

    def _classify_regime(
        self,
        measurements: RegimeMeasurements,
        volatility_state: VolatilityState,
        data_quality: DataQuality,
    ) -> RegimeType:

        if data_quality == DataQuality.INVALID:
            return RegimeType.UNKNOWN

        trend_strength = measurements.trend_strength
        volatility_ratio = measurements.volatility_ratio

        if trend_strength is None:
            return RegimeType.UNKNOWN

        # ----------------------------------------------------
        # Compression has structural priority when volatility
        # is materially below its rolling baseline.
        # ----------------------------------------------------

        if (
            volatility_ratio is not None
            and volatility_ratio
            <= self.config["compression_ratio"]
        ):

            return RegimeType.COMPRESSED

        # ----------------------------------------------------
        # Expansion indicates materially increased volatility.
        # ----------------------------------------------------

        if (
            volatility_ratio is not None
            and volatility_ratio
            >= self.config["expansion_ratio"]
        ):

            if trend_strength >= (
                self.config["trend_strength_threshold"]
            ):
                return RegimeType.EXPANDING

        # ----------------------------------------------------
        # Directional trend.
        # ----------------------------------------------------

        if trend_strength >= (
            self.config["trend_strength_threshold"]
        ):

            return RegimeType.TRENDING

        # ----------------------------------------------------
        # Range / balanced condition.
        # ----------------------------------------------------

        if trend_strength <= (
            self.config["range_strength_threshold"]
        ):

            return RegimeType.RANGING

        # ----------------------------------------------------
        # Everything between strong trend and clear range
        # remains transition.
        # ----------------------------------------------------

        return RegimeType.TRANSITION

    # ========================================================
    # VOLATILITY CLASSIFICATION
    # ========================================================

    def _classify_volatility(
        self,
        volatility_ratio: Optional[float],
    ) -> VolatilityState:

        if volatility_ratio is None:
            return VolatilityState.UNKNOWN

        if volatility_ratio < (
            self.config["volatility_low_ratio"]
        ):
            return VolatilityState.LOW

        if volatility_ratio >= (
            self.config["volatility_extreme_ratio"]
        ):
            return VolatilityState.EXTREME

        if volatility_ratio > (
            self.config["volatility_high_ratio"]
        ):
            return VolatilityState.HIGH

        return VolatilityState.NORMAL

    # ========================================================
    # REGIME STRENGTH
    # ========================================================

    def _calculate_regime_strength(
        self,
        measurements: RegimeMeasurements,
        regime: RegimeType,
    ) -> float:

        trend = (
            measurements.trend_strength
            if measurements.trend_strength is not None
            else 0.0
        )

        compression = (
            measurements.compression_score
            if measurements.compression_score is not None
            else 0.0
        )

        expansion = (
            measurements.expansion_score
            if measurements.expansion_score is not None
            else 0.0
        )

        if regime == RegimeType.TRENDING:
            return self._score_0_100(trend)

        if regime == RegimeType.COMPRESSED:
            return self._score_0_100(compression)

        if regime == RegimeType.EXPANDING:
            return self._score_0_100(expansion)

        if regime == RegimeType.RANGING:
            return self._score_0_100(
                1.0 - trend
            )

        if regime == RegimeType.TRANSITION:
            return self._score_0_100(
                1.0 - abs(trend - 0.5) * 2.0
            )

        return 0.0

    # ========================================================
    # TRANSITION SCORE
    # ========================================================

    def _calculate_transition_score(
        self,
        measurements: RegimeMeasurements,
        volatility_state: VolatilityState,
    ) -> float:

        score = 0.0

        trend = measurements.trend_strength
        volatility_ratio = measurements.volatility_ratio

        if trend is not None:

            # Maximum transition uncertainty occurs around
            # middle-strength trend conditions.
            trend_transition = (
                1.0 - abs(trend - 0.5) * 2.0
            )

            score += 50.0 * self._clamp(
                trend_transition,
                0.0,
                1.0,
            )

        if volatility_ratio is not None:

            if (
                volatility_ratio < 0.85
                or volatility_ratio > 1.15
            ):
                score += 25.0

        if volatility_state in (
            VolatilityState.HIGH,
            VolatilityState.EXTREME,
        ):
            score += 15.0

        if volatility_state == VolatilityState.LOW:
            score += 10.0

        return self._clamp(
            score,
            0.0,
            100.0,
        )

    # ========================================================
    # EVIDENCE
    # ========================================================

    def _build_evidence(
        self,
        measurements: RegimeMeasurements,
        regime: RegimeType,
        volatility_state: VolatilityState,
    ) -> List[str]:

        evidence: List[str] = []

        evidence.append(
            f"REGIME={regime.value}"
        )

        evidence.append(
            f"VOLATILITY={volatility_state.value}"
        )

        if measurements.trend_strength is not None:

            evidence.append(
                "TREND_STRENGTH="
                f"{measurements.trend_strength:.4f}"
            )

        if measurements.direction_bias != (
            DirectionBias.UNKNOWN
        ):

            evidence.append(
                "DIRECTION_BIAS="
                f"{measurements.direction_bias.value}"
            )

        if measurements.volatility_ratio is not None:

            evidence.append(
                "VOLATILITY_RATIO="
                f"{measurements.volatility_ratio:.4f}"
            )

        if measurements.volume_ratio is not None:

            evidence.append(
                "VOLUME_RATIO="
                f"{measurements.volume_ratio:.4f}"
            )

        if measurements.compression_score is not None:

            evidence.append(
                "COMPRESSION_SCORE="
                f"{measurements.compression_score:.4f}"
            )

        if measurements.expansion_score is not None:

            evidence.append(
                "EXPANSION_SCORE="
                f"{measurements.expansion_score:.4f}"
            )

        return evidence

    # ========================================================
    # WARNINGS
    # ========================================================

    def _build_warnings(
        self,
        data: RegimeMarketInput,
        measurements: RegimeMeasurements,
        quality: DataQuality,
    ) -> List[str]:

        warnings: List[str] = []

        if quality == DataQuality.PARTIAL:

            warnings.append(
                "INSUFFICIENT_HISTORY_FOR_FULL_REGIME_VALIDATION"
            )

        if measurements.volatility_ratio is None:

            warnings.append(
                "VOLATILITY_BASELINE_UNAVAILABLE"
            )

        if measurements.volume_ratio is None:

            warnings.append(
                "VOLUME_BASELINE_UNAVAILABLE"
            )

        if measurements.direction_bias == (
            DirectionBias.UNKNOWN
        ):

            warnings.append(
                "DIRECTIONAL_BIAS_UNAVAILABLE"
            )

        if (
            measurements.spread_pct is not None
            and measurements.spread_pct
            > self.config["maximum_reasonable_spread_pct"]
        ):

            warnings.append(
                "WIDE_SPREAD_DETECTED"
            )

        if data.data_source is None:

            warnings.append(
                "DATA_SOURCE_NOT_IDENTIFIED"
            )

        return warnings

    # ========================================================
    # HELPERS
    # ========================================================

    @staticmethod
    def _clean_series(
        values: Sequence[float],
    ) -> List[float]:

        result: List[float] = []

        for value in values:

            if value is None:
                continue

            try:
                numeric = float(value)
            except (TypeError, ValueError):
                continue

            if math.isfinite(numeric) and numeric > 0:
                result.append(numeric)

        return result

    @staticmethod
    def _clean_non_negative_series(
        values: Sequence[float],
    ) -> List[float]:

        result: List[float] = []

        for value in values:

            if value is None:
                continue

            try:
                numeric = float(value)
            except (TypeError, ValueError):
                continue

            if math.isfinite(numeric) and numeric >= 0:
                result.append(numeric)

        return result

    @staticmethod
    def _is_positive(
        value: Optional[float],
    ) -> bool:

        if value is None:
            return False

        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return False

        return (
            math.isfinite(numeric)
            and numeric > 0
        )

    @staticmethod
    def _clamp(
        value: float,
        minimum: float,
        maximum: float,
    ) -> float:

        return max(
            minimum,
            min(maximum, value),
        )

    @staticmethod
    def _score_0_100(
        value: float,
    ) -> float:

        return round(
            max(
                0.0,
                min(100.0, value * 100.0),
            ),
            4,
        )

    @staticmethod
    def _timestamp(
        timestamp: datetime,
    ) -> str:

        if timestamp.tzinfo is None:

            timestamp = timestamp.replace(
                tzinfo=timezone.utc
            )

        return timestamp.isoformat()


# ============================================================
# FACTORY
# ============================================================

def create_regime_engine(
    config: Optional[Dict[str, float]] = None,
) -> RegimeEngine:

    return RegimeEngine(config=config)


# ============================================================
# MODULE EXPORTS
# ============================================================

__all__ = [
    "RegimeEngine",
    "RegimeMarketInput",
    "RegimeResult",
    "RegimeMeasurements",
    "RegimeType",
    "DirectionBias",
    "VolatilityState",
    "DataQuality",
    "create_regime_engine",
]
# ============================================================
# PART 2 — REGIME HISTORY + TRANSITION INTELLIGENCE
#
# Adds:
#   - Regime history
#   - Previous-regime comparison
#   - Volatility expansion/compression transition
#   - Trend strengthening / weakening
#   - Regime persistence
#   - Regime transition detection
#   - State stability measurement
#
# IMPORTANT:
#   This remains an intelligence/evidence engine.
#   It does NOT make the final D13 decision.
# ============================================================


@dataclass
class RegimeStateSnapshot:
    """
    Immutable-style snapshot of a previously observed regime.
    Used for transition analysis.
    """

    timestamp: str
    instrument: str

    regime: RegimeType
    direction_bias: DirectionBias
    volatility_state: VolatilityState

    regime_strength: float
    transition_score: float

    trend_strength: Optional[float] = None
    volatility_ratio: Optional[float] = None
    volume_ratio: Optional[float] = None

    data_quality: DataQuality = DataQuality.INVALID


@dataclass
class RegimeTransition:
    """
    Describes how the market regime has changed between
    the previous observation and the current observation.
    """

    detected: bool

    previous_regime: RegimeType
    current_regime: RegimeType

    previous_direction: DirectionBias
    current_direction: DirectionBias

    previous_volatility: VolatilityState
    current_volatility: VolatilityState

    trend_change: Optional[float]
    volatility_change: Optional[float]
    volume_change: Optional[float]

    transition_type: str
    transition_strength: float

    evidence: List[str] = field(default_factory=list)


@dataclass
class RegimeStability:
    """
    Measures whether the current regime is persisting or
    changing frequently.

    Stability is descriptive only.
    It is not a trade-quality score.
    """

    observation_count: int
    same_regime_count: int
    persistence_ratio: float

    direction_consistency: float
    volatility_consistency: float

    stability_score: float

    stable: bool
    unstable: bool

    evidence: List[str] = field(default_factory=list)


# ============================================================
# EXTEND REGIME ENGINE
# ============================================================

def _regime_engine_init_history(
    self: RegimeEngine,
    history_size: int = 100,
) -> None:
    """
    Initialize bounded regime history.

    Kept separate so Part 2 can be integrated without changing
    the Part 1 constructor structure.
    """

    self._regime_history: List[RegimeStateSnapshot] = []
    self._regime_history_size = max(
        10,
        int(history_size),
    )


def _regime_engine_record_state(
    self: RegimeEngine,
    result: RegimeResult,
) -> RegimeStateSnapshot:
    """
    Record current regime observation.

    Only valid/usable observations are stored.
    """

    snapshot = RegimeStateSnapshot(
        timestamp=result.timestamp,
        instrument=result.instrument,

        regime=result.regime,
        direction_bias=result.direction_bias,
        volatility_state=result.volatility_state,

        regime_strength=result.regime_strength,
        transition_score=result.transition_score,

        trend_strength=result.measurements.trend_strength,
        volatility_ratio=result.measurements.volatility_ratio,
        volume_ratio=result.measurements.volume_ratio,

        data_quality=result.data_quality,
    )

    if not hasattr(self, "_regime_history"):
        _regime_engine_init_history(self)

    self._regime_history.append(snapshot)

    if len(self._regime_history) > self._regime_history_size:
        self._regime_history = (
            self._regime_history[
                -self._regime_history_size:
            ]
        )

    return snapshot


def _regime_engine_previous_state(
    self: RegimeEngine,
    instrument: Optional[str] = None,
) -> Optional[RegimeStateSnapshot]:

    if not hasattr(self, "_regime_history"):
        return None

    history = self._regime_history

    if instrument is not None:
        history = [
            item
            for item in history
            if item.instrument == instrument
        ]

    if len(history) < 2:
        return None

    return history[-2]


def _regime_engine_transition(
    self: RegimeEngine,
    current: RegimeStateSnapshot,
    previous: Optional[RegimeStateSnapshot],
) -> RegimeTransition:

    if previous is None:

        return RegimeTransition(
            detected=False,

            previous_regime=RegimeType.UNKNOWN,
            current_regime=current.regime,

            previous_direction=DirectionBias.UNKNOWN,
            current_direction=current.direction_bias,

            previous_volatility=VolatilityState.UNKNOWN,
            current_volatility=current.volatility_state,

            trend_change=None,
            volatility_change=None,
            volume_change=None,

            transition_type="INITIAL_STATE",
            transition_strength=0.0,

            evidence=[
                "NO_PREVIOUS_REGIME_STATE"
            ],
        )

    trend_change = None

    if (
        previous.trend_strength is not None
        and current.trend_strength is not None
    ):
        trend_change = (
            current.trend_strength
            - previous.trend_strength
        )

    volatility_change = None

    if (
        previous.volatility_ratio is not None
        and current.volatility_ratio is not None
    ):
        volatility_change = (
            current.volatility_ratio
            - previous.volatility_ratio
        )

    volume_change = None

    if (
        previous.volume_ratio is not None
        and current.volume_ratio is not None
    ):
        volume_change = (
            current.volume_ratio
            - previous.volume_ratio
        )

    regime_changed = (
        previous.regime != current.regime
    )

    direction_changed = (
        previous.direction_bias
        != current.direction_bias
        and current.direction_bias
        != DirectionBias.UNKNOWN
    )

    volatility_changed = (
        previous.volatility_state
        != current.volatility_state
        and current.volatility_state
        != VolatilityState.UNKNOWN
    )

    detected = (
        regime_changed
        or direction_changed
        or volatility_changed
    )

    transition_type = self._identify_transition_type(
        previous,
        current,
        trend_change,
        volatility_change,
        direction_changed,
    )

    strength = self._transition_strength(
        regime_changed=regime_changed,
        direction_changed=direction_changed,
        volatility_changed=volatility_changed,
        trend_change=trend_change,
        volatility_change=volatility_change,
    )

    evidence: List[str] = []

    if regime_changed:
        evidence.append(
            f"REGIME_CHANGED:"
            f"{previous.regime.value}"
            f"->{current.regime.value}"
        )

    if direction_changed:
        evidence.append(
            f"DIRECTION_CHANGED:"
            f"{previous.direction_bias.value}"
            f"->{current.direction_bias.value}"
        )

    if volatility_changed:
        evidence.append(
            f"VOLATILITY_CHANGED:"
            f"{previous.volatility_state.value}"
            f"->{current.volatility_state.value}"
        )

    if trend_change is not None:
        evidence.append(
            f"TREND_DELTA={trend_change:.4f}"
        )

    if volatility_change is not None:
        evidence.append(
            f"VOLATILITY_DELTA={volatility_change:.4f}"
        )

    if volume_change is not None:
        evidence.append(
            f"VOLUME_DELTA={volume_change:.4f}"
        )

    if not evidence:
        evidence.append(
            "REGIME_STATE_PERSISTING"
        )

    return RegimeTransition(
        detected=detected,

        previous_regime=previous.regime,
        current_regime=current.regime,

        previous_direction=previous.direction_bias,
        current_direction=current.direction_bias,

        previous_volatility=previous.volatility_state,
        current_volatility=current.volatility_state,

        trend_change=trend_change,
        volatility_change=volatility_change,
        volume_change=volume_change,

        transition_type=transition_type,
        transition_strength=strength,

        evidence=evidence,
    )


def _regime_engine_identify_transition_type(
    self: RegimeEngine,
    previous: RegimeStateSnapshot,
    current: RegimeStateSnapshot,
    trend_change: Optional[float],
    volatility_change: Optional[float],
    direction_changed: bool,
) -> str:

    # --------------------------------------------------------
    # Compression -> Expansion
    # --------------------------------------------------------

    if (
        previous.regime == RegimeType.COMPRESSED
        and current.regime == RegimeType.EXPANDING
    ):
        return "COMPRESSION_TO_EXPANSION"

    # --------------------------------------------------------
    # Expansion -> Compression
    # --------------------------------------------------------

    if (
        previous.regime == RegimeType.EXPANDING
        and current.regime == RegimeType.COMPRESSED
    ):
        return "EXPANSION_TO_COMPRESSION"

    # --------------------------------------------------------
    # Range -> Trend
    # --------------------------------------------------------

    if (
        previous.regime == RegimeType.RANGING
        and current.regime == RegimeType.TRENDING
    ):
        return "RANGE_TO_TREND"

    # --------------------------------------------------------
    # Trend -> Range
    # --------------------------------------------------------

    if (
        previous.regime == RegimeType.TRENDING
        and current.regime == RegimeType.RANGING
    ):
        return "TREND_TO_RANGE"

    # --------------------------------------------------------
    # Direction reversal
    # --------------------------------------------------------

    if direction_changed:

        if (
            previous.direction_bias == DirectionBias.BULLISH
            and current.direction_bias == DirectionBias.BEARISH
        ):
            return "BULLISH_TO_BEARISH"

        if (
            previous.direction_bias == DirectionBias.BEARISH
            and current.direction_bias == DirectionBias.BULLISH
        ):
            return "BEARISH_TO_BULLISH"

        return "DIRECTION_REVERSAL"

    # --------------------------------------------------------
    # Trend strengthening
    # --------------------------------------------------------

    if (
        trend_change is not None
        and trend_change >= 0.10
    ):
        return "TREND_STRENGTHENING"

    # --------------------------------------------------------
    # Trend weakening
    # --------------------------------------------------------

    if (
        trend_change is not None
        and trend_change <= -0.10
    ):
        return "TREND_WEAKENING"

    # --------------------------------------------------------
    # Volatility expansion
    # --------------------------------------------------------

    if (
        volatility_change is not None
        and volatility_change >= 0.25
    ):
        return "VOLATILITY_EXPANSION"

    # --------------------------------------------------------
    # Volatility contraction
    # --------------------------------------------------------

    if (
        volatility_change is not None
        and volatility_change <= -0.25
    ):
        return "VOLATILITY_CONTRACTION"

    # --------------------------------------------------------
    # Generic regime transition
    # --------------------------------------------------------

    if previous.regime != current.regime:
        return "REGIME_TRANSITION"

    return "STATE_PERSISTENCE"


def _regime_engine_transition_strength(
    self: RegimeEngine,
    regime_changed: bool,
    direction_changed: bool,
    volatility_changed: bool,
    trend_change: Optional[float],
    volatility_change: Optional[float],
) -> float:

    score = 0.0

    if regime_changed:
        score += 35.0

    if direction_changed:
        score += 30.0

    if volatility_changed:
        score += 20.0

    if trend_change is not None:
        score += min(
            10.0,
            abs(trend_change) * 50.0,
        )

    if volatility_change is not None:
        score += min(
            10.0,
            abs(volatility_change) * 20.0,
        )

    return self._clamp(
        score,
        0.0,
        100.0,
    )


def _regime_engine_stability(
    self: RegimeEngine,
    instrument: Optional[str] = None,
    lookback: int = 10,
) -> RegimeStability:

    if not hasattr(self, "_regime_history"):

        return RegimeStability(
            observation_count=0,
            same_regime_count=0,
            persistence_ratio=0.0,
            direction_consistency=0.0,
            volatility_consistency=0.0,
            stability_score=0.0,
            stable=False,
            unstable=False,
            evidence=[
                "REGIME_HISTORY_NOT_INITIALIZED"
            ],
        )

    history = self._regime_history

    if instrument is not None:

        history = [
            item
            for item in history
            if item.instrument == instrument
        ]

    history = history[-max(2, lookback):]

    if len(history) < 2:

        return RegimeStability(
            observation_count=len(history),
            same_regime_count=0,
            persistence_ratio=0.0,
            direction_consistency=0.0,
            volatility_consistency=0.0,
            stability_score=0.0,
            stable=False,
            unstable=False,
            evidence=[
                "INSUFFICIENT_REGIME_HISTORY"
            ],
        )

    current_regime = history[-1].regime

    same_regime_count = sum(
        1
        for item in history
        if item.regime == current_regime
    )

    persistence_ratio = (
        same_regime_count
        / len(history)
    )

    # --------------------------------------------------------
    # Direction consistency
    # --------------------------------------------------------

    known_direction = [
        item.direction_bias
        for item in history
        if item.direction_bias
        != DirectionBias.UNKNOWN
    ]

    if known_direction:

        direction_counts: Dict[
            DirectionBias,
            int,
        ] = {}

        for direction in known_direction:
            direction_counts[direction] = (
                direction_counts.get(direction, 0)
                + 1
            )

        direction_consistency = (
            max(direction_counts.values())
            / len(known_direction)
        )

    else:
        direction_consistency = 0.0

    # --------------------------------------------------------
    # Volatility consistency
    # --------------------------------------------------------

    known_volatility = [
        item.volatility_state
        for item in history
        if item.volatility_state
        != VolatilityState.UNKNOWN
    ]

    if known_volatility:

        volatility_counts: Dict[
            VolatilityState,
            int,
        ] = {}

        for state in known_volatility:
            volatility_counts[state] = (
                volatility_counts.get(state, 0)
                + 1
            )

        volatility_consistency = (
            max(volatility_counts.values())
            / len(known_volatility)
        )

    else:
        volatility_consistency = 0.0

    # --------------------------------------------------------
    # Combined stability
    # --------------------------------------------------------

    stability_score = (
        persistence_ratio * 50.0
        + direction_consistency * 25.0
        + volatility_consistency * 25.0
    )

    stability_score = self._clamp(
        stability_score,
        0.0,
        100.0,
    )

    stable = stability_score >= 70.0
    unstable = stability_score <= 35.0

    evidence = [
        f"REGIME_PERSISTENCE={persistence_ratio:.4f}",
        f"DIRECTION_CONSISTENCY={direction_consistency:.4f}",
        f"VOLATILITY_CONSISTENCY="
        f"{volatility_consistency:.4f}",
        f"STABILITY_SCORE={stability_score:.2f}",
    ]

    return RegimeStability(
        observation_count=len(history),
        same_regime_count=same_regime_count,
        persistence_ratio=round(
            persistence_ratio,
            6,
        ),
        direction_consistency=round(
            direction_consistency,
            6,
        ),
        volatility_consistency=round(
            volatility_consistency,
            6,
        ),
        stability_score=round(
            stability_score,
            4,
        ),
        stable=stable,
        unstable=unstable,
        evidence=evidence,
    )


# ============================================================
# REGIME ENGINE ANALYSIS WRAPPER
# ============================================================

def _regime_engine_analyze(
    self: RegimeEngine,
    market_input: RegimeMarketInput,
) -> Dict[str, Any]:
    """
    Full Part-2 analysis wrapper.

    Performs:
        1. Current regime evaluation
        2. State recording
        3. Previous-state comparison
        4. Transition detection
        5. Stability analysis
    """

    result = self.evaluate(market_input)

    current_state = _regime_engine_record_state(
        self,
        result,
    )

    previous_state = _regime_engine_previous_state(
        self,
        market_input.instrument,
    )

    transition = _regime_engine_transition(
        self,
        current_state,
        previous_state,
    )

    stability = _regime_engine_stability(
        self,
        market_input.instrument,
    )

    return {
        "result": result,
        "current_state": current_state,
        "previous_state": previous_state,
        "transition": transition,
        "stability": stability,
    }


# ============================================================
# PUBLIC HISTORY / ANALYSIS METHODS
# ============================================================

def _regime_engine_get_history(
    self: RegimeEngine,
    instrument: Optional[str] = None,
) -> List[RegimeStateSnapshot]:

    if not hasattr(self, "_regime_history"):
        return []

    if instrument is None:
        return list(self._regime_history)

    return [
        item
        for item in self._regime_history
        if item.instrument == instrument
    ]


def _regime_engine_clear_history(
    self: RegimeEngine,
    instrument: Optional[str] = None,
) -> None:

    if not hasattr(self, "_regime_history"):
        return

    if instrument is None:
        self._regime_history.clear()
        return

    self._regime_history = [
        item
        for item in self._regime_history
        if item.instrument != instrument
    ]


# ============================================================
# ATTACH PART-2 METHODS TO ENGINE
# ============================================================

# History
RegimeEngine._init_history = _regime_engine_init_history
RegimeEngine.record_state = _regime_engine_record_state
RegimeEngine.get_history = _regime_engine_get_history
RegimeEngine.clear_history = _regime_engine_clear_history

# Transition intelligence
RegimeEngine.get_previous_state = (
    _regime_engine_previous_state
)

RegimeEngine.detect_transition = (
    _regime_engine_transition
)

RegimeEngine.identify_transition_type = (
    _regime_engine_identify_transition_type
)

RegimeEngine.calculate_transition_strength = (
    _regime_engine_transition_strength
)

# Stability
RegimeEngine.analyze_stability = (
    _regime_engine_stability
)

# Complete Part-2 analysis
RegimeEngine.analyze = (
    _regime_engine_analyze
)


# ============================================================
# PART-2 EXPORTS
# ============================================================

__all__.extend([
    "RegimeStateSnapshot",
    "RegimeTransition",
    "RegimeStability",
])
# ============================================================
# PART 3 — MULTI-TIMEFRAME REGIME CONTEXT
#
# Adds:
#   - Timeframe-specific regime observations
#   - Cross-timeframe agreement / conflict
#   - Higher-timeframe context
#   - Lower-timeframe transition awareness
#   - Regime alignment measurement
#   - MTF regime context contract
#
# IMPORTANT:
#   - No BUY/SELL decision here.
#   - No fabricated timeframe data.
#   - A missing timeframe remains UNKNOWN.
#   - D13 remains final decision authority.
# ============================================================


@dataclass
class TimeframeRegimeObservation:
    """
    Regime observation for one actual market timeframe.

    The observation must originate from real market data processed
    through RegimeEngine.
    """

    timeframe: str
    regime: RegimeType
    direction_bias: DirectionBias
    volatility_state: VolatilityState

    regime_strength: float
    transition_score: float
    stability_score: float

    data_quality: DataQuality

    trend_strength: Optional[float] = None
    volatility_ratio: Optional[float] = None
    volume_ratio: Optional[float] = None

    transition_type: Optional[str] = None

    timestamp: Optional[str] = None


@dataclass
class MTFRegimeContext:
    """
    Aggregated multi-timeframe regime context.

    This describes market alignment/conflict.
    It does NOT produce a final trade signal.
    """

    instrument: str
    timestamp: str

    observations: List[TimeframeRegimeObservation]

    dominant_regime: RegimeType
    dominant_direction: DirectionBias

    alignment_score: float
    regime_alignment_score: float
    direction_alignment_score: float
    volatility_alignment_score: float

    conflict_score: float
    transition_score: float

    higher_timeframe_regime: RegimeType
    lower_timeframe_regime: RegimeType

    context_quality: DataQuality

    evidence: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


# ============================================================
# TIMEFRAME ORDER
# ============================================================

_REGIME_TIMEFRAME_ORDER = {
    "tick": 0,
    "1s": 1,
    "5s": 2,
    "10s": 3,
    "15s": 4,
    "30s": 5,
    "1m": 10,
    "3m": 20,
    "5m": 30,
    "10m": 40,
    "15m": 50,
    "30m": 60,
    "1h": 70,
    "2h": 80,
    "4h": 90,
    "6h": 100,
    "12h": 110,
    "1d": 120,
    "1w": 130,
    "1mo": 140,
}


def _regime_normalize_timeframe(
    timeframe: Optional[str],
) -> str:

    if timeframe is None:
        return "unknown"

    value = str(timeframe).strip().lower()

    aliases = {
        "1min": "1m",
        "minute": "1m",
        "1minute": "1m",
        "5min": "5m",
        "5minute": "5m",
        "10min": "10m",
        "15min": "15m",
        "30min": "30m",
        "60min": "1h",
        "60m": "1h",
        "hour": "1h",
        "daily": "1d",
        "day": "1d",
        "weekly": "1w",
        "week": "1w",
        "monthly": "1mo",
    }

    return aliases.get(value, value)


def _regime_timeframe_rank(
    timeframe: str,
) -> int:

    normalized = _regime_normalize_timeframe(
        timeframe
    )

    return _REGIME_TIMEFRAME_ORDER.get(
        normalized,
        -1,
    )


# ============================================================
# ADD TIMEFRAME OBSERVATION
# ============================================================

def _regime_engine_add_timeframe_observation(
    self: RegimeEngine,
    result: RegimeResult,
    timeframe: Optional[str] = None,
    transition: Optional[RegimeTransition] = None,
    stability: Optional[RegimeStability] = None,
) -> TimeframeRegimeObservation:
    """
    Convert a RegimeResult into an MTF observation.

    Only calculated values from the actual engine result are used.
    """

    tf = _regime_normalize_timeframe(
        timeframe
        if timeframe is not None
        else "unknown"
    )

    stability_score = (
        stability.stability_score
        if stability is not None
        else 0.0
    )

    transition_type = (
        transition.transition_type
        if transition is not None
        else None
    )

    observation = TimeframeRegimeObservation(
        timeframe=tf,

        regime=result.regime,
        direction_bias=result.direction_bias,
        volatility_state=result.volatility_state,

        regime_strength=result.regime_strength,
        transition_score=result.transition_score,
        stability_score=stability_score,

        data_quality=result.data_quality,

        trend_strength=result.measurements.trend_strength,
        volatility_ratio=result.measurements.volatility_ratio,
        volume_ratio=result.measurements.volume_ratio,

        transition_type=transition_type,

        timestamp=result.timestamp,
    )

    if not hasattr(self, "_mtf_regime_observations"):
        self._mtf_regime_observations = {}

    instrument = result.instrument

    if instrument not in self._mtf_regime_observations:
        self._mtf_regime_observations[instrument] = {}

    self._mtf_regime_observations[instrument][tf] = (
        observation
    )

    return observation


# ============================================================
# GET TIMEFRAME OBSERVATIONS
# ============================================================

def _regime_engine_get_timeframe_observations(
    self: RegimeEngine,
    instrument: str,
) -> List[TimeframeRegimeObservation]:

    if not hasattr(
        self,
        "_mtf_regime_observations",
    ):
        return []

    observations = self._mtf_regime_observations.get(
        instrument,
        {},
    )

    result = list(observations.values())

    result.sort(
        key=lambda item: _regime_timeframe_rank(
            item.timeframe
        )
    )

    return result


# ============================================================
# SELECT HIGHER / LOWER TIMEFRAME
# ============================================================

def _regime_engine_select_mtf_extremes(
    self: RegimeEngine,
    observations: List[TimeframeRegimeObservation],
) -> tuple[
    Optional[TimeframeRegimeObservation],
    Optional[TimeframeRegimeObservation],
]:

    valid = [
        item
        for item in observations
        if item.timeframe != "unknown"
        and item.data_quality
        != DataQuality.INVALID
    ]

    if not valid:
        return None, None

    valid.sort(
        key=lambda item: _regime_timeframe_rank(
            item.timeframe
        )
    )

    lower = valid[0]
    higher = valid[-1]

    return higher, lower


# ============================================================
# REGIME AGREEMENT
# ============================================================

def _regime_compare_regimes(
    first: RegimeType,
    second: RegimeType,
) -> float:

    if (
        first == RegimeType.UNKNOWN
        or second == RegimeType.UNKNOWN
    ):
        return 0.0

    if first == second:
        return 1.0

    # Related states are partial agreement rather than full
    # agreement.
    related_groups = [
        {
            RegimeType.TRENDING,
            RegimeType.EXPANDING,
        },
        {
            RegimeType.COMPRESSED,
            RegimeType.RANGING,
        },
        {
            RegimeType.TRANSITION,
            RegimeType.RANGING,
        },
        {
            RegimeType.TRANSITION,
            RegimeType.EXPANDING,
        },
    ]

    for group in related_groups:
        if first in group and second in group:
            return 0.5

    return 0.0


def _regime_compare_direction(
    first: DirectionBias,
    second: DirectionBias,
) -> float:

    if (
        first == DirectionBias.UNKNOWN
        or second == DirectionBias.UNKNOWN
    ):
        return 0.0

    if first == second:
        return 1.0

    if (
        first == DirectionBias.NEUTRAL
        or second == DirectionBias.NEUTRAL
    ):
        return 0.5

    return 0.0


def _regime_compare_volatility(
    first: VolatilityState,
    second: VolatilityState,
) -> float:

    if (
        first == VolatilityState.UNKNOWN
        or second == VolatilityState.UNKNOWN
    ):
        return 0.0

    if first == second:
        return 1.0

    adjacent = [
        {
            VolatilityState.LOW,
            VolatilityState.NORMAL,
        },
        {
            VolatilityState.NORMAL,
            VolatilityState.HIGH,
        },
        {
            VolatilityState.HIGH,
            VolatilityState.EXTREME,
        },
    ]

    for group in adjacent:
        if first in group and second in group:
            return 0.5

    return 0.0


# ============================================================
# CALCULATE PAIRWISE ALIGNMENT
# ============================================================

def _regime_engine_pairwise_alignment(
    self: RegimeEngine,
    observations: List[TimeframeRegimeObservation],
) -> tuple[float, float, float, float, float]:

    valid = [
        item
        for item in observations
        if item.data_quality
        != DataQuality.INVALID
    ]

    if len(valid) < 2:
        return (
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
        )

    regime_scores: List[float] = []
    direction_scores: List[float] = []
    volatility_scores: List[float] = []

    for index in range(len(valid)):

        for other_index in range(
            index + 1,
            len(valid),
        ):

            first = valid[index]
            second = valid[other_index]

            regime_scores.append(
                _regime_compare_regimes(
                    first.regime,
                    second.regime,
                )
            )

            direction_scores.append(
                _regime_compare_direction(
                    first.direction_bias,
                    second.direction_bias,
                )
            )

            volatility_scores.append(
                _regime_compare_volatility(
                    first.volatility_state,
                    second.volatility_state,
                )
            )

    regime_alignment = (
        statistics.mean(regime_scores)
        if regime_scores
        else 0.0
    )

    direction_alignment = (
        statistics.mean(direction_scores)
        if direction_scores
        else 0.0
    )

    volatility_alignment = (
        statistics.mean(volatility_scores)
        if volatility_scores
        else 0.0
    )

    alignment = (
        regime_alignment * 0.40
        + direction_alignment * 0.40
        + volatility_alignment * 0.20
    )

    conflict = 1.0 - alignment

    return (
        alignment * 100.0,
        regime_alignment * 100.0,
        direction_alignment * 100.0,
        volatility_alignment * 100.0,
        conflict * 100.0,
    )


# ============================================================
# DOMINANT REGIME
# ============================================================

def _regime_engine_dominant_regime(
    self: RegimeEngine,
    observations: List[TimeframeRegimeObservation],
) -> RegimeType:

    valid = [
        item
        for item in observations
        if item.regime != RegimeType.UNKNOWN
        and item.data_quality
        != DataQuality.INVALID
    ]

    if not valid:
        return RegimeType.UNKNOWN

    weighted_votes: Dict[
        RegimeType,
        float,
    ] = {}

    for observation in valid:

        rank = _regime_timeframe_rank(
            observation.timeframe
        )

        # Higher timeframe receives greater contextual weight.
        if rank < 0:
            weight = 1.0
        else:
            weight = 1.0 + (
                min(rank, 140) / 140.0
            )

        weight *= max(
            0.25,
            observation.regime_strength / 100.0,
        )

        weighted_votes[observation.regime] = (
            weighted_votes.get(
                observation.regime,
                0.0,
            )
            + weight
        )

    if not weighted_votes:
        return RegimeType.UNKNOWN

    return max(
        weighted_votes,
        key=weighted_votes.get,
    )


# ============================================================
# DOMINANT DIRECTION
# ============================================================

def _regime_engine_dominant_direction(
    self: RegimeEngine,
    observations: List[TimeframeRegimeObservation],
) -> DirectionBias:

    valid = [
        item
        for item in observations
        if item.direction_bias
        != DirectionBias.UNKNOWN
        and item.data_quality
        != DataQuality.INVALID
    ]

    if not valid:
        return DirectionBias.UNKNOWN

    weighted_votes: Dict[
        DirectionBias,
        float,
    ] = {}

    for observation in valid:

        rank = _regime_timeframe_rank(
            observation.timeframe
        )

        if rank < 0:
            weight = 1.0
        else:
            weight = 1.0 + (
                min(rank, 140) / 140.0
            )

        weight *= max(
            0.25,
            observation.regime_strength / 100.0,
        )

        weighted_votes[
            observation.direction_bias
        ] = (
            weighted_votes.get(
                observation.direction_bias,
                0.0,
            )
            + weight
        )

    return max(
        weighted_votes,
        key=weighted_votes.get,
    )


# ============================================================
# CONTEXT QUALITY
# ============================================================

def _regime_engine_context_quality(
    self: RegimeEngine,
    observations: List[TimeframeRegimeObservation],
) -> DataQuality:

    if not observations:
        return DataQuality.INVALID

    valid_count = sum(
        1
        for item in observations
        if item.data_quality
        != DataQuality.INVALID
    )

    high_count = sum(
        1
        for item in observations
        if item.data_quality == DataQuality.HIGH
    )

    if valid_count == 0:
        return DataQuality.INVALID

    if valid_count >= 3 and high_count >= 2:
        return DataQuality.HIGH

    if valid_count >= 2:
        return DataQuality.USABLE

    return DataQuality.PARTIAL


# ============================================================
# TRANSITION AGGREGATION
# ============================================================

def _regime_engine_mtf_transition_score(
    self: RegimeEngine,
    observations: List[TimeframeRegimeObservation],
) -> float:

    valid = [
        item
        for item in observations
        if item.data_quality
        != DataQuality.INVALID
    ]

    if not valid:
        return 0.0

    values = [
        item.transition_score
        for item in valid
    ]

    return self._clamp(
        statistics.mean(values),
        0.0,
        100.0,
    )


# ============================================================
# BUILD MTF EVIDENCE
# ============================================================

def _regime_engine_build_mtf_evidence(
    self: RegimeEngine,
    observations: List[TimeframeRegimeObservation],
    dominant_regime: RegimeType,
    dominant_direction: DirectionBias,
    alignment_score: float,
    conflict_score: float,
) -> List[str]:

    evidence: List[str] = []

    evidence.append(
        f"MTF_OBSERVATIONS={len(observations)}"
    )

    evidence.append(
        f"DOMINANT_REGIME={dominant_regime.value}"
    )

    evidence.append(
        f"DOMINANT_DIRECTION="
        f"{dominant_direction.value}"
    )

    evidence.append(
        f"MTF_ALIGNMENT={alignment_score:.2f}"
    )

    evidence.append(
        f"MTF_CONFLICT={conflict_score:.2f}"
    )

    for observation in observations:

        evidence.append(
            f"{observation.timeframe}:"
            f"{observation.regime.value}/"
            f"{observation.direction_bias.value}/"
            f"{observation.volatility_state.value}"
        )

    return evidence


# ============================================================
# BUILD MTF WARNINGS
# ============================================================

def _regime_engine_build_mtf_warnings(
    self: RegimeEngine,
    observations: List[TimeframeRegimeObservation],
    alignment_score: float,
    conflict_score: float,
) -> List[str]:

    warnings: List[str] = []

    if len(observations) < 2:

        warnings.append(
            "MULTI_TIMEFRAME_CONTEXT_INCOMPLETE"
        )

    valid_count = sum(
        1
        for item in observations
        if item.data_quality
        != DataQuality.INVALID
    )

    if valid_count < 2:

        warnings.append(
            "INSUFFICIENT_VALID_TIMEFRAMES"
        )

    if conflict_score >= 60.0:

        warnings.append(
            "MULTI_TIMEFRAME_REGIME_CONFLICT"
        )

    if alignment_score <= 35.0 and valid_count >= 2:

        warnings.append(
            "LOW_MULTI_TIMEFRAME_ALIGNMENT"
        )

    unknown_count = sum(
        1
        for item in observations
        if (
            item.regime == RegimeType.UNKNOWN
            or item.direction_bias
            == DirectionBias.UNKNOWN
        )
    )

    if unknown_count:

        warnings.append(
            "UNKNOWN_TIMEFRAME_COMPONENTS_PRESENT"
        )

    return warnings


# ============================================================
# BUILD MTF CONTEXT
# ============================================================

def _regime_engine_build_mtf_context(
    self: RegimeEngine,
    instrument: str,
) -> MTFRegimeContext:

    observations = (
        self.get_timeframe_observations(
            instrument
        )
    )

    now = datetime.now(
        timezone.utc
    ).isoformat()

    if not observations:

        return MTFRegimeContext(
            instrument=instrument,
            timestamp=now,

            observations=[],

            dominant_regime=RegimeType.UNKNOWN,
            dominant_direction=DirectionBias.UNKNOWN,

            alignment_score=0.0,
            regime_alignment_score=0.0,
            direction_alignment_score=0.0,
            volatility_alignment_score=0.0,

            conflict_score=0.0,
            transition_score=0.0,

            higher_timeframe_regime=RegimeType.UNKNOWN,
            lower_timeframe_regime=RegimeType.UNKNOWN,

            context_quality=DataQuality.INVALID,

            evidence=[
                "NO_MTF_REGIME_OBSERVATIONS"
            ],

            warnings=[
                "MULTI_TIMEFRAME_CONTEXT_UNAVAILABLE"
            ],
        )

    (
        alignment_score,
        regime_alignment_score,
        direction_alignment_score,
        volatility_alignment_score,
        conflict_score,
    ) = self._calculate_mtf_alignment(
        observations
    )

    dominant_regime = (
        self.get_dominant_regime(
            observations
        )
    )

    dominant_direction = (
        self.get_dominant_direction(
            observations
        )
    )

    higher, lower = (
        self._select_mtf_extremes(
            observations
        )
    )

    transition_score = (
        self._calculate_mtf_transition_score(
            observations
        )
    )

    context_quality = (
        self._calculate_context_quality(
            observations
        )
    )

    evidence = self._build_mtf_evidence(
        observations,
        dominant_regime,
        dominant_direction,
        alignment_score,
        conflict_score,
    )

    warnings = self._build_mtf_warnings(
        observations,
        alignment_score,
        conflict_score,
    )

    return MTFRegimeContext(
        instrument=instrument,
        timestamp=now,

        observations=observations,

        dominant_regime=dominant_regime,
        dominant_direction=dominant_direction,

        alignment_score=round(
            alignment_score,
            4,
        ),

        regime_alignment_score=round(
            regime_alignment_score,
            4,
        ),

        direction_alignment_score=round(
            direction_alignment_score,
            4,
        ),

        volatility_alignment_score=round(
            volatility_alignment_score,
            4,
        ),

        conflict_score=round(
            conflict_score,
            4,
        ),

        transition_score=round(
            transition_score,
            4,
        ),

        higher_timeframe_regime=(
            higher.regime
            if higher is not None
            else RegimeType.UNKNOWN
        ),

        lower_timeframe_regime=(
            lower.regime
            if lower is not None
            else RegimeType.UNKNOWN
        ),

        context_quality=context_quality,

        evidence=evidence,
        warnings=warnings,
    )


# ============================================================
# COMPLETE MTF UPDATE
# ============================================================

def _regime_engine_update_timeframe(
    self: RegimeEngine,
    market_input: RegimeMarketInput,
) -> TimeframeRegimeObservation:
    """
    Evaluate one real timeframe and store its regime context.
    """

    result = self.evaluate(
        market_input
    )

    current_state = (
        self.record_state(result)
    )

    previous_state = (
        self.get_previous_state(
            market_input.instrument
        )
    )

    transition = (
        self.detect_transition(
            current_state,
            previous_state,
        )
    )

    stability = (
        self.analyze_stability(
            market_input.instrument
        )
    )

    timeframe = (
        market_input.timeframe
        if market_input.timeframe is not None
        else "unknown"
    )

    return self.add_timeframe_observation(
        result=result,
        timeframe=timeframe,
        transition=transition,
        stability=stability,
    )


# ============================================================
# MTF RESET
# ============================================================

def _regime_engine_clear_mtf(
    self: RegimeEngine,
    instrument: Optional[str] = None,
) -> None:

    if not hasattr(
        self,
        "_mtf_regime_observations",
    ):
        return

    if instrument is None:

        self._mtf_regime_observations.clear()
        return

    self._mtf_regime_observations.pop(
        instrument,
        None,
    )


# ============================================================
# ATTACH PART-3 METHODS
# ============================================================

RegimeEngine.add_timeframe_observation = (
    _regime_engine_add_timeframe_observation
)

RegimeEngine.get_timeframe_observations = (
    _regime_engine_get_timeframe_observations
)

RegimeEngine._select_mtf_extremes = (
    _regime_engine_select_mtf_extremes
)

RegimeEngine._calculate_mtf_alignment = (
    _regime_engine_pairwise_alignment
)

RegimeEngine.get_dominant_regime = (
    _regime_engine_dominant_regime
)

RegimeEngine.get_dominant_direction = (
    _regime_engine_dominant_direction
)

RegimeEngine._calculate_context_quality = (
    _regime_engine_context_quality
)

RegimeEngine._calculate_mtf_transition_score = (
    _regime_engine_mtf_transition_score
)

RegimeEngine._build_mtf_evidence = (
    _regime_engine_build_mtf_evidence
)

RegimeEngine._build_mtf_warnings = (
    _regime_engine_build_mtf_warnings
)

RegimeEngine.build_mtf_context = (
    _regime_engine_build_mtf_context
)

RegimeEngine.update_timeframe = (
    _regime_engine_update_timeframe
)

RegimeEngine.clear_mtf = (
    _regime_engine_clear_mtf
)


# ============================================================
# PART-3 EXPORTS
# ============================================================

__all__.extend([
    "TimeframeRegimeObservation",
    "MTFRegimeContext",
])
# ============================================================
# PART 4 — REGIME QUALITY, CHANGE VELOCITY & MARKET STATE
#
# Adds:
#   - Regime change velocity
#   - Trend acceleration / deceleration
#   - Volatility acceleration
#   - Direction persistence
#   - Regime maturity
#   - Regime exhaustion / transition pressure
#   - Composite market-state context
#
# IMPORTANT:
#   This is measurement/intelligence only.
#   No BUY/SELL decision.
#   No execution authority.
#   D13 remains final decision authority.
# ============================================================


@dataclass
class RegimeDynamics:
    """
    Describes how quickly the current market regime is changing.
    """

    trend_velocity: float
    volatility_velocity: float
    volume_velocity: float

    trend_acceleration: float
    volatility_acceleration: float

    direction_persistence: float
    regime_persistence: float

    change_velocity: float
    transition_pressure: float

    strengthening: bool
    weakening: bool
    accelerating: bool
    decelerating: bool

    evidence: List[str] = field(default_factory=list)


@dataclass
class RegimeMaturity:
    """
    Estimates how mature the current regime is based on the
    observed regime history.

    This is NOT a prediction of reversal.
    """

    observation_count: int
    consecutive_same_regime: int

    maturity_score: float
    early_stage_score: float
    mature_stage_score: float

    regime_age_ratio: float

    evidence: List[str] = field(default_factory=list)


@dataclass
class MarketStateContext:
    """
    Higher-level regime context consumed by downstream
    intelligence engines.

    It describes the environment; it does not decide the trade.
    """

    instrument: str
    timestamp: str

    regime: RegimeType
    direction_bias: DirectionBias
    volatility_state: VolatilityState

    regime_strength: float
    transition_score: float

    mtf_alignment: float
    mtf_conflict: float

    dynamics: RegimeDynamics
    maturity: RegimeMaturity

    state_quality: DataQuality

    environment_description: str

    evidence: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


# ============================================================
# DYNAMICS HELPERS
# ============================================================

def _regime_safe_delta(
    current: Optional[float],
    previous: Optional[float],
) -> float:

    if current is None or previous is None:
        return 0.0

    return current - previous


def _regime_normalized_velocity(
    values: Sequence[float],
) -> float:

    if len(values) < 2:
        return 0.0

    current = values[-1]
    previous = values[-2]

    denominator = max(
        abs(previous),
        1e-12,
    )

    return (
        (current - previous)
        / denominator
    )


def _regime_direction_persistence(
    history: Sequence[RegimeStateSnapshot],
) -> float:

    valid = [
        item
        for item in history
        if item.direction_bias
        != DirectionBias.UNKNOWN
    ]

    if len(valid) < 2:
        return 0.0

    current = valid[-1].direction_bias

    same = sum(
        1
        for item in valid
        if item.direction_bias == current
    )

    return same / len(valid)


def _regime_same_count(
    history: Sequence[RegimeStateSnapshot],
) -> int:

    if not history:
        return 0

    current = history[-1].regime
    count = 0

    for item in reversed(history):

        if item.regime != current:
            break

        count += 1

    return count


# ============================================================
# REGIME DYNAMICS
# ============================================================

def _regime_engine_analyze_dynamics(
    self: RegimeEngine,
    instrument: str,
    lookback: int = 8,
) -> RegimeDynamics:

    history = self.get_history(
        instrument
    )

    history = history[-max(3, lookback):]

    if len(history) < 2:

        return RegimeDynamics(
            trend_velocity=0.0,
            volatility_velocity=0.0,
            volume_velocity=0.0,

            trend_acceleration=0.0,
            volatility_acceleration=0.0,

            direction_persistence=0.0,
            regime_persistence=0.0,

            change_velocity=0.0,
            transition_pressure=0.0,

            strengthening=False,
            weakening=False,
            accelerating=False,
            decelerating=False,

            evidence=[
                "INSUFFICIENT_REGIME_HISTORY"
            ],
        )

    # --------------------------------------------------------
    # Trend velocity
    # --------------------------------------------------------

    trend_values = [
        item.trend_strength
        for item in history
        if item.trend_strength is not None
    ]

    if len(trend_values) >= 2:

        trend_velocity = (
            trend_values[-1]
            - trend_values[-2]
        )

    else:
        trend_velocity = 0.0

    # --------------------------------------------------------
    # Volatility velocity
    # --------------------------------------------------------

    volatility_values = [
        item.volatility_ratio
        for item in history
        if item.volatility_ratio is not None
    ]

    if len(volatility_values) >= 2:

        volatility_velocity = (
            volatility_values[-1]
            - volatility_values[-2]
        )

    else:
        volatility_velocity = 0.0

    # --------------------------------------------------------
    # Volume velocity
    # --------------------------------------------------------

    volume_values = [
        item.volume_ratio
        for item in history
        if item.volume_ratio is not None
    ]

    if len(volume_values) >= 2:

        volume_velocity = (
            volume_values[-1]
            - volume_values[-2]
        )

    else:
        volume_velocity = 0.0

    # --------------------------------------------------------
    # Trend acceleration
    # --------------------------------------------------------

    if len(trend_values) >= 3:

        previous_velocity = (
            trend_values[-2]
            - trend_values[-3]
        )

        trend_acceleration = (
            trend_velocity
            - previous_velocity
        )

    else:
        trend_acceleration = 0.0

    # --------------------------------------------------------
    # Volatility acceleration
    # --------------------------------------------------------

    if len(volatility_values) >= 3:

        previous_velocity = (
            volatility_values[-2]
            - volatility_values[-3]
        )

        volatility_acceleration = (
            volatility_velocity
            - previous_velocity
        )

    else:
        volatility_acceleration = 0.0

    # --------------------------------------------------------
    # Persistence
    # --------------------------------------------------------

    direction_persistence = (
        _regime_direction_persistence(
            history
        )
    )

    same_count = _regime_same_count(
        history
    )

    regime_persistence = (
        same_count
        / len(history)
    )

    # --------------------------------------------------------
    # Overall change velocity
    # --------------------------------------------------------

    change_components = [
        abs(trend_velocity),
        abs(volatility_velocity),
        abs(volume_velocity),
    ]

    change_velocity = (
        statistics.mean(
            change_components
        )
        if change_components
        else 0.0
    )

    # --------------------------------------------------------
    # Transition pressure
    # --------------------------------------------------------

    transition_pressure = 0.0

    transition_pressure += min(
        35.0,
        abs(trend_velocity) * 100.0,
    )

    transition_pressure += min(
        35.0,
        abs(volatility_velocity) * 50.0,
    )

    transition_pressure += min(
        15.0,
        abs(trend_acceleration) * 100.0,
    )

    transition_pressure += min(
        15.0,
        abs(volatility_acceleration) * 25.0,
    )

    transition_pressure = self._clamp(
        transition_pressure,
        0.0,
        100.0,
    )

    # --------------------------------------------------------
    # State interpretation
    # --------------------------------------------------------

    strengthening = (
        trend_velocity >= 0.05
        and trend_acceleration >= 0.0
    )

    weakening = (
        trend_velocity <= -0.05
        or trend_acceleration <= -0.05
    )

    accelerating = (
        trend_acceleration >= 0.03
        or volatility_acceleration >= 0.10
    )

    decelerating = (
        trend_acceleration <= -0.03
        and volatility_acceleration <= 0.05
    )

    evidence = [
        f"TREND_VELOCITY={trend_velocity:.5f}",
        f"VOLATILITY_VELOCITY="
        f"{volatility_velocity:.5f}",
        f"VOLUME_VELOCITY={volume_velocity:.5f}",
        f"TREND_ACCELERATION="
        f"{trend_acceleration:.5f}",
        f"VOLATILITY_ACCELERATION="
        f"{volatility_acceleration:.5f}",
        f"DIRECTION_PERSISTENCE="
        f"{direction_persistence:.4f}",
        f"REGIME_PERSISTENCE="
        f"{regime_persistence:.4f}",
        f"CHANGE_VELOCITY="
        f"{change_velocity:.5f}",
        f"TRANSITION_PRESSURE="
        f"{transition_pressure:.2f}",
    ]

    return RegimeDynamics(
        trend_velocity=round(
            trend_velocity,
            6,
        ),

        volatility_velocity=round(
            volatility_velocity,
            6,
        ),

        volume_velocity=round(
            volume_velocity,
            6,
        ),

        trend_acceleration=round(
            trend_acceleration,
            6,
        ),

        volatility_acceleration=round(
            volatility_acceleration,
            6,
        ),

        direction_persistence=round(
            direction_persistence,
            6,
        ),

        regime_persistence=round(
            regime_persistence,
            6,
        ),

        change_velocity=round(
            change_velocity,
            6,
        ),

        transition_pressure=round(
            transition_pressure,
            4,
        ),

        strengthening=strengthening,
        weakening=weakening,
        accelerating=accelerating,
        decelerating=decelerating,

        evidence=evidence,
    )


# ============================================================
# REGIME MATURITY
# ============================================================

def _regime_engine_analyze_maturity(
    self: RegimeEngine,
    instrument: str,
    lookback: int = 20,
) -> RegimeMaturity:

    history = self.get_history(
        instrument
    )

    history = history[-max(2, lookback):]

    if not history:

        return RegimeMaturity(
            observation_count=0,
            consecutive_same_regime=0,

            maturity_score=0.0,
            early_stage_score=0.0,
            mature_stage_score=0.0,

            regime_age_ratio=0.0,

            evidence=[
                "NO_REGIME_HISTORY"
            ],
        )

    same_count = _regime_same_count(
        history
    )

    age_ratio = (
        same_count
        / len(history)
    )

    # Maturity is deliberately bounded. A long-lasting regime
    # does not automatically mean a reversal is coming.
    maturity_score = self._clamp(
        age_ratio * 100.0,
        0.0,
        100.0,
    )

    early_stage_score = (
        100.0
        - maturity_score
    )

    mature_stage_score = maturity_score

    evidence = [
        f"REGIME_AGE={same_count}",
        f"REGIME_AGE_RATIO={age_ratio:.4f}",
        f"MATURITY_SCORE={maturity_score:.2f}",
    ]

    return RegimeMaturity(
        observation_count=len(history),
        consecutive_same_regime=same_count,

        maturity_score=round(
            maturity_score,
            4,
        ),

        early_stage_score=round(
            early_stage_score,
            4,
        ),

        mature_stage_score=round(
            mature_stage_score,
            4,
        ),

        regime_age_ratio=round(
            age_ratio,
            6,
        ),

        evidence=evidence,
    )


# ============================================================
# ENVIRONMENT DESCRIPTION
# ============================================================

def _regime_engine_describe_environment(
    self: RegimeEngine,
    regime: RegimeType,
    direction: DirectionBias,
    volatility: VolatilityState,
    dynamics: RegimeDynamics,
) -> str:

    if regime == RegimeType.UNKNOWN:
        return "MARKET_ENVIRONMENT_UNKNOWN"

    if regime == RegimeType.COMPRESSED:

        if direction == DirectionBias.BULLISH:
            return "BULLISH_COMPRESSION"

        if direction == DirectionBias.BEARISH:
            return "BEARISH_COMPRESSION"

        return "NEUTRAL_COMPRESSION"

    if regime == RegimeType.TRENDING:

        if direction == DirectionBias.BULLISH:

            if dynamics.strengthening:
                return "BULLISH_TREND_STRENGTHENING"

            if dynamics.weakening:
                return "BULLISH_TREND_WEAKENING"

            return "BULLISH_TREND"

        if direction == DirectionBias.BEARISH:

            if dynamics.strengthening:
                return "BEARISH_TREND_STRENGTHENING"

            if dynamics.weakening:
                return "BEARISH_TREND_WEAKENING"

            return "BEARISH_TREND"

        return "DIRECTIONLESS_TREND_ENVIRONMENT"

    if regime == RegimeType.EXPANDING:

        if direction == DirectionBias.BULLISH:
            return "BULLISH_VOLATILITY_EXPANSION"

        if direction == DirectionBias.BEARISH:
            return "BEARISH_VOLATILITY_EXPANSION"

        return "DIRECTIONLESS_VOLATILITY_EXPANSION"

    if regime == RegimeType.RANGING:

        return "RANGE_BOUND_ENVIRONMENT"

    if regime == RegimeType.TRANSITION:

        if direction == DirectionBias.BULLISH:
            return "BULLISH_TRANSITION"

        if direction == DirectionBias.BEARISH:
            return "BEARISH_TRANSITION"

        return "REGIME_TRANSITION"

    return "MARKET_STATE_UNDEFINED"


# ============================================================
# MARKET STATE QUALITY
# ============================================================

def _regime_engine_state_quality(
    self: RegimeEngine,
    result: RegimeResult,
    mtf_context: Optional[MTFRegimeContext],
    dynamics: RegimeDynamics,
) -> DataQuality:

    if result.data_quality == DataQuality.INVALID:
        return DataQuality.INVALID

    quality_score = 0.0

    # Current-state data quality
    if result.data_quality == DataQuality.HIGH:
        quality_score += 35.0
    elif result.data_quality == DataQuality.USABLE:
        quality_score += 25.0
    else:
        quality_score += 10.0

    # Volatility availability
    if result.measurements.volatility_ratio is not None:
        quality_score += 15.0

    # Trend availability
    if result.measurements.trend_strength is not None:
        quality_score += 15.0

    # MTF context
    if mtf_context is not None:

        if mtf_context.context_quality == DataQuality.HIGH:
            quality_score += 25.0

        elif mtf_context.context_quality == DataQuality.USABLE:
            quality_score += 15.0

        else:
            quality_score += 5.0

    # Dynamics availability
    if (
        dynamics.change_velocity != 0.0
        or dynamics.transition_pressure != 0.0
    ):
        quality_score += 10.0

    if quality_score >= 80.0:
        return DataQuality.HIGH

    if quality_score >= 55.0:
        return DataQuality.USABLE

    return DataQuality.PARTIAL


# ============================================================
# MARKET STATE EVIDENCE
# ============================================================

def _regime_engine_state_evidence(
    self: RegimeEngine,
    result: RegimeResult,
    mtf_context: Optional[MTFRegimeContext],
    dynamics: RegimeDynamics,
    maturity: RegimeMaturity,
) -> List[str]:

    evidence: List[str] = []

    evidence.extend(
        result.evidence
    )

    evidence.extend(
        dynamics.evidence
    )

    evidence.extend(
        maturity.evidence
    )

    if mtf_context is not None:

        evidence.append(
            f"MTF_ALIGNMENT="
            f"{mtf_context.alignment_score:.2f}"
        )

        evidence.append(
            f"MTF_CONFLICT="
            f"{mtf_context.conflict_score:.2f}"
        )

        evidence.append(
            f"MTF_DOMINANT_REGIME="
            f"{mtf_context.dominant_regime.value}"
        )

        evidence.append(
            f"MTF_DOMINANT_DIRECTION="
            f"{mtf_context.dominant_direction.value}"
        )

    return evidence


# ============================================================
# MARKET STATE WARNINGS
# ============================================================

def _regime_engine_state_warnings(
    self: RegimeEngine,
    result: RegimeResult,
    mtf_context: Optional[MTFRegimeContext],
    dynamics: RegimeDynamics,
    maturity: RegimeMaturity,
) -> List[str]:

    warnings: List[str] = []

    warnings.extend(
        result.warnings
    )

    if mtf_context is not None:

        warnings.extend(
            mtf_context.warnings
        )

    if dynamics.transition_pressure >= 70.0:

        warnings.append(
            "HIGH_REGIME_TRANSITION_PRESSURE"
        )

    if dynamics.weakening:

        warnings.append(
            "REGIME_STRENGTH_WEAKENING"
        )

    if dynamics.accelerating:

        warnings.append(
            "MARKET_STATE_ACCELERATING"
        )

    if dynamics.decelerating:

        warnings.append(
            "MARKET_STATE_DECELERATING"
        )

    if maturity.mature_stage_score >= 80.0:

        warnings.append(
            "MATURE_REGIME_OBSERVATION"
        )

    # Important:
    # maturity itself is NOT a reversal signal.
    if maturity.mature_stage_score >= 80.0:

        warnings.append(
            "REGIME_MATURITY_IS_NOT_REVERSAL_PROOF"
        )

    return list(
        dict.fromkeys(warnings)
    )


# ============================================================
# COMPLETE MARKET STATE ANALYSIS
# ============================================================

def _regime_engine_market_state(
    self: RegimeEngine,
    market_input: RegimeMarketInput,
) -> MarketStateContext:

    # --------------------------------------------------------
    # Current regime
    # --------------------------------------------------------

    result = self.evaluate(
        market_input
    )

    # --------------------------------------------------------
    # Record actual observation
    # --------------------------------------------------------

    current_state = (
        self.record_state(result)
    )

    # --------------------------------------------------------
    # Transition
    # --------------------------------------------------------

    previous_state = (
        self.get_previous_state(
            market_input.instrument
        )
    )

    transition = (
        self.detect_transition(
            current_state,
            previous_state,
        )
    )

    # --------------------------------------------------------
    # Stability
    # --------------------------------------------------------

    stability = (
        self.analyze_stability(
            market_input.instrument
        )
    )

    # --------------------------------------------------------
    # Store timeframe observation if timeframe exists
    # --------------------------------------------------------

    timeframe = (
        market_input.timeframe
        if market_input.timeframe
        else "unknown"
    )

    if timeframe != "unknown":

        self.add_timeframe_observation(
            result=result,
            timeframe=timeframe,
            transition=transition,
            stability=stability,
        )

    # --------------------------------------------------------
    # MTF context
    # --------------------------------------------------------

    mtf_context = (
        self.build_mtf_context(
            market_input.instrument
        )
    )

    # --------------------------------------------------------
    # Dynamics
    # --------------------------------------------------------

    dynamics = (
        self.analyze_dynamics(
            market_input.instrument
        )
    )

    # --------------------------------------------------------
    # Maturity
    # --------------------------------------------------------

    maturity = (
        self.analyze_maturity(
            market_input.instrument
        )
    )

    # --------------------------------------------------------
    # Environment description
    # --------------------------------------------------------

    description = (
        self.describe_environment(
            regime=result.regime,
            direction=result.direction_bias,
            volatility=result.volatility_state,
            dynamics=dynamics,
        )
    )

    # --------------------------------------------------------
    # State quality
    # --------------------------------------------------------

    state_quality = (
        self.calculate_state_quality(
            result=result,
            mtf_context=mtf_context,
            dynamics=dynamics,
        )
    )

    # --------------------------------------------------------
    # Evidence
    # --------------------------------------------------------

    evidence = (
        self.build_state_evidence(
            result=result,
            mtf_context=mtf_context,
            dynamics=dynamics,
            maturity=maturity,
        )
    )

    # --------------------------------------------------------
    # Warnings
    # --------------------------------------------------------

    warnings = (
        self.build_state_warnings(
            result=result,
            mtf_context=mtf_context,
            dynamics=dynamics,
            maturity=maturity,
        )
    )

    return MarketStateContext(
        instrument=market_input.instrument,
        timestamp=result.timestamp,

        regime=result.regime,
        direction_bias=result.direction_bias,
        volatility_state=result.volatility_state,

        regime_strength=result.regime_strength,
        transition_score=result.transition_score,

        mtf_alignment=(
            mtf_context.alignment_score
            if mtf_context is not None
            else 0.0
        ),

        mtf_conflict=(
            mtf_context.conflict_score
            if mtf_context is not None
            else 0.0
        ),

        dynamics=dynamics,
        maturity=maturity,

        state_quality=state_quality,

        environment_description=description,

        evidence=evidence,
        warnings=warnings,
    )


# ============================================================
# PUBLIC METHOD ATTACHMENTS
# ============================================================

RegimeEngine.analyze_dynamics = (
    _regime_engine_analyze_dynamics
)

RegimeEngine.analyze_maturity = (
    _regime_engine_analyze_maturity
)

RegimeEngine.describe_environment = (
    _regime_engine_describe_environment
)

RegimeEngine.calculate_state_quality = (
    _regime_engine_state_quality
)

RegimeEngine.build_state_evidence = (
    _regime_engine_state_evidence
)

RegimeEngine.build_state_warnings = (
    _regime_engine_state_warnings
)

RegimeEngine.market_state = (
    _regime_engine_market_state
)


# ============================================================
# PART-4 EXPORTS
# ============================================================

__all__.extend([
    "RegimeDynamics",
    "RegimeMaturity",
    "MarketStateContext",
])
# ============================================================
# REGIME ENGINE — PART 5
# Regime Transition Forecast + Actionable Regime Intelligence
# ============================================================

@dataclass
class RegimeForecast:
    instrument: str
    timestamp: datetime
    current_regime: RegimeType
    current_direction: DirectionBias

    next_regime: RegimeType
    next_direction: DirectionBias

    transition_probability: float
    continuation_probability: float
    reversal_pressure: float
    expansion_pressure: float
    compression_pressure: float

    forecast_horizon: str
    confidence: float

    evidence: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "instrument": self.instrument,
            "timestamp": self.timestamp.isoformat()
            if isinstance(self.timestamp, datetime)
            else self.timestamp,
            "current_regime": self.current_regime.value,
            "current_direction": self.current_direction.value,
            "next_regime": self.next_regime.value,
            "next_direction": self.next_direction.value,
            "transition_probability": round(
                self.transition_probability, 2
            ),
            "continuation_probability": round(
                self.continuation_probability, 2
            ),
            "reversal_pressure": round(
                self.reversal_pressure, 2
            ),
            "expansion_pressure": round(
                self.expansion_pressure, 2
            ),
            "compression_pressure": round(
                self.compression_pressure, 2
            ),
            "forecast_horizon": self.forecast_horizon,
            "confidence": round(self.confidence, 2),
            "evidence": list(self.evidence),
            "warnings": list(self.warnings),
        }


@dataclass
class RegimeIntelligence:
    instrument: str
    timestamp: datetime

    regime: RegimeType
    direction: DirectionBias
    volatility: VolatilityState

    environment: str

    continuation_bias: float
    transition_bias: float
    expansion_bias: float
    reversal_bias: float

    opportunity_state: str
    readiness_score: float
    intelligence_quality: float

    forecast: Optional[RegimeForecast] = None

    evidence: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "instrument": self.instrument,
            "timestamp": self.timestamp.isoformat()
            if isinstance(self.timestamp, datetime)
            else self.timestamp,
            "regime": self.regime.value,
            "direction": self.direction.value,
            "volatility": self.volatility.value,
            "environment": self.environment,
            "continuation_bias": round(
                self.continuation_bias, 2
            ),
            "transition_bias": round(
                self.transition_bias, 2
            ),
            "expansion_bias": round(
                self.expansion_bias, 2
            ),
            "reversal_bias": round(
                self.reversal_bias, 2
            ),
            "opportunity_state": self.opportunity_state,
            "readiness_score": round(
                self.readiness_score, 2
            ),
            "intelligence_quality": round(
                self.intelligence_quality, 2
            ),
            "forecast": (
                self.forecast.to_dict()
                if self.forecast is not None
                else None
            ),
            "evidence": list(self.evidence),
            "warnings": list(self.warnings),
        }


# ============================================================
# REGIME FORECAST HELPERS
# ============================================================

def _calculate_regime_forecast(
    self,
    state: MarketStateContext,
    horizon: str = "next_observation",
) -> RegimeForecast:

    current_regime = state.regime_result.regime
    current_direction = state.regime_result.direction_bias

    dynamics = state.dynamics
    maturity = state.maturity

    transition_pressure = min(
        100.0,
        max(0.0, dynamics.transition_pressure)
    )

    trend_strength = state.regime_result.measurements.trend_strength
    volatility_ratio = (
        state.regime_result.measurements.volatility_ratio
    )

    compression_score = (
        state.regime_result.measurements.compression_score
    )

    expansion_score = (
        state.regime_result.measurements.expansion_score
    )

    continuation_probability = 50.0
    transition_probability = 50.0
    reversal_pressure = 0.0
    expansion_pressure = expansion_score
    compression_pressure = compression_score

    evidence = []
    warnings = []

    # --------------------------------------------------------
    # TREND CONTINUATION
    # --------------------------------------------------------

    if current_regime == RegimeType.TRENDING:

        continuation_probability += (
            trend_strength * 30.0
        )

        if dynamics.strengthening:
            continuation_probability += 10.0
            evidence.append(
                "Trend strength is increasing."
            )

        if dynamics.direction_persistence > 60:
            continuation_probability += 10.0
            evidence.append(
                "Directional persistence supports continuation."
            )

    # --------------------------------------------------------
    # RANGE CONTINUATION
    # --------------------------------------------------------

    elif current_regime == RegimeType.RANGING:

        continuation_probability += 20.0

        if dynamics.change_velocity < 0:
            continuation_probability += 10.0
            evidence.append(
                "Low state-change velocity supports range persistence."
            )

    # --------------------------------------------------------
    # COMPRESSION
    # --------------------------------------------------------

    if current_regime == RegimeType.COMPRESSED:

        compression_pressure = max(
            compression_pressure,
            60.0
        )

        if expansion_score > 50:
            transition_probability += 15.0
            evidence.append(
                "Compression is showing expansion pressure."
            )

    # --------------------------------------------------------
    # EXPANSION
    # --------------------------------------------------------

    if current_regime == RegimeType.EXPANDING:

        expansion_pressure = max(
            expansion_pressure,
            65.0
        )

        transition_probability += 10.0

        if dynamics.accelerating:
            expansion_pressure += 10.0
            evidence.append(
                "Volatility/trend acceleration supports expansion."
            )

    # --------------------------------------------------------
    # WEAKENING TREND
    # --------------------------------------------------------

    if dynamics.weakening:

        reversal_pressure += 20.0
        transition_probability += 15.0

        evidence.append(
            "Trend dynamics are weakening."
        )

    # --------------------------------------------------------
    # MATURITY
    # --------------------------------------------------------

    if maturity.mature_stage_score >= 70:

        reversal_pressure += 10.0
        transition_probability += 10.0

        evidence.append(
            "Current regime has reached elevated maturity."
        )

    # --------------------------------------------------------
    # DIRECTION REVERSAL PRESSURE
    # --------------------------------------------------------

    if current_direction in (
        DirectionBias.BULLISH,
        DirectionBias.BEARISH,
    ):

        if dynamics.direction_persistence < 40:

            reversal_pressure += 20.0
            transition_probability += 10.0

            evidence.append(
                "Directional persistence is deteriorating."
            )

    # --------------------------------------------------------
    # NORMALIZE
    # --------------------------------------------------------

    continuation_probability = min(
        100.0,
        max(0.0, continuation_probability)
    )

    transition_probability = min(
        100.0,
        max(0.0, transition_probability)
    )

    reversal_pressure = min(
        100.0,
        max(0.0, reversal_pressure)
    )

    expansion_pressure = min(
        100.0,
        max(0.0, expansion_pressure)
    )

    compression_pressure = min(
        100.0,
        max(0.0, compression_pressure)
    )

    # --------------------------------------------------------
    # SELECT NEXT REGIME
    # --------------------------------------------------------

    next_regime = current_regime
    next_direction = current_direction

    if current_regime == RegimeType.COMPRESSED:

        if expansion_pressure >= 65:

            next_regime = RegimeType.EXPANDING

    elif current_regime == RegimeType.RANGING:

        if trend_strength >= self.trend_strength_threshold:

            next_regime = RegimeType.TRENDING

    elif current_regime == RegimeType.TRENDING:

        if reversal_pressure >= 55:

            next_regime = RegimeType.TRANSITION

        elif dynamics.weakening:

            next_regime = RegimeType.TRANSITION

    elif current_regime == RegimeType.EXPANDING:

        if expansion_pressure < 40:

            next_regime = RegimeType.TRANSITION

    elif current_regime == RegimeType.TRANSITION:

        if trend_strength >= self.trend_strength_threshold:

            next_regime = RegimeType.TRENDING

        elif compression_pressure >= 60:

            next_regime = RegimeType.COMPRESSED

        else:
            next_regime = RegimeType.RANGING

    # --------------------------------------------------------
    # DIRECTION FORECAST
    # --------------------------------------------------------

    if current_direction == DirectionBias.BULLISH:

        if reversal_pressure >= 70:
            next_direction = DirectionBias.BEARISH
        elif reversal_pressure >= 45:
            next_direction = DirectionBias.NEUTRAL

    elif current_direction == DirectionBias.BEARISH:

        if reversal_pressure >= 70:
            next_direction = DirectionBias.BULLISH
        elif reversal_pressure >= 45:
            next_direction = DirectionBias.NEUTRAL

    # --------------------------------------------------------
    # FORECAST CONFIDENCE
    # --------------------------------------------------------

    confidence_components = [
        state.state_quality,
        state.regime_result.regime_strength,
        state.stability.stability_score,
    ]

    confidence = (
        sum(confidence_components)
        / len(confidence_components)
    )

    if state.mtf_context is not None:
        confidence = (
            confidence * 0.75
            + state.mtf_context.alignment_score * 0.25
        )

    confidence = min(
        100.0,
        max(0.0, confidence)
    )

    # Forecast is intentionally conservative when data quality
    # is insufficient.
    if state.regime_result.data_quality in (
        DataQuality.INVALID,
        DataQuality.PARTIAL,
    ):

        confidence *= 0.60

        warnings.append(
            "Forecast confidence reduced because data quality is incomplete."
        )

    if state.mtf_context is not None:

        if state.mtf_context.conflict_score >= 60:

            confidence *= 0.80

            warnings.append(
                "Multi-timeframe conflict reduces forecast reliability."
            )

    return RegimeForecast(
        instrument=state.instrument,
        timestamp=state.timestamp,
        current_regime=current_regime,
        current_direction=current_direction,
        next_regime=next_regime,
        next_direction=next_direction,
        transition_probability=transition_probability,
        continuation_probability=continuation_probability,
        reversal_pressure=reversal_pressure,
        expansion_pressure=expansion_pressure,
        compression_pressure=compression_pressure,
        forecast_horizon=horizon,
        confidence=confidence,
        evidence=evidence,
        warnings=warnings,
    )


# ============================================================
# REGIME INTELLIGENCE
# ============================================================

def _build_regime_intelligence(
    self,
    state: MarketStateContext,
) -> RegimeIntelligence:

    forecast = self._calculate_regime_forecast(state)

    dynamics = state.dynamics
    measurements = state.regime_result.measurements

    continuation_bias = min(
        100.0,
        max(
            0.0,
            (
                measurements.trend_strength * 60.0
                + dynamics.direction_persistence * 0.40
            )
        )
    )

    transition_bias = min(
        100.0,
        max(
            0.0,
            dynamics.transition_pressure
        )
    )

    expansion_bias = min(
        100.0,
        max(
            0.0,
            (
                measurements.expansion_score * 0.70
                + max(
                    0.0,
                    dynamics.volatility_velocity
                ) * 30.0
            )
        )
    )

    reversal_bias = min(
        100.0,
        max(
            0.0,
            forecast.reversal_pressure
        )
    )

    # --------------------------------------------------------
    # OPPORTUNITY STATE
    # --------------------------------------------------------

    opportunity_state = "NEUTRAL"

    if (
        state.regime_result.regime
        == RegimeType.COMPRESSED
        and expansion_bias >= 60
    ):
        opportunity_state = "EXPANSION_READY"

    elif (
        state.regime_result.regime
        == RegimeType.TRENDING
        and continuation_bias >= 65
        and reversal_bias < 45
    ):
        opportunity_state = "TREND_CONTINUATION"

    elif (
        state.regime_result.regime
        == RegimeType.EXPANDING
        and expansion_bias >= 60
    ):
        opportunity_state = "EXPANSION_ACTIVE"

    elif reversal_bias >= 65:

        opportunity_state = "REVERSAL_RISK"

    elif transition_bias >= 65:

        opportunity_state = "REGIME_TRANSITION"

    elif state.regime_result.regime == RegimeType.RANGING:

        opportunity_state = "RANGE_ENVIRONMENT"

    # --------------------------------------------------------
    # READINESS
    # --------------------------------------------------------

    readiness_score = max(
        expansion_bias,
        continuation_bias,
        transition_bias,
    )

    if state.regime_result.direction_bias == DirectionBias.UNKNOWN:

        readiness_score *= 0.75

    if state.regime_result.data_quality == DataQuality.PARTIAL:

        readiness_score *= 0.75

    readiness_score = min(
        100.0,
        max(0.0, readiness_score)
    )

    # --------------------------------------------------------
    # INTELLIGENCE QUALITY
    # --------------------------------------------------------

    quality_parts = [
        state.state_quality,
        state.regime_result.regime_strength,
        state.stability.stability_score,
        forecast.confidence,
    ]

    if state.mtf_context is not None:
        quality_parts.append(
            state.mtf_context.alignment_score
        )

    intelligence_quality = (
        sum(quality_parts)
        / len(quality_parts)
    )

    evidence = [
        f"Regime={state.regime_result.regime.value}",
        f"Direction={state.regime_result.direction_bias.value}",
        f"Volatility={state.regime_result.volatility_state.value}",
        f"OpportunityState={opportunity_state}",
    ]

    warnings = []

    if reversal_bias >= 60:

        warnings.append(
            "Meaningful reversal pressure detected."
        )

    if transition_bias >= 60:

        warnings.append(
            "Regime transition pressure is elevated."
        )

    if state.stability.stability_score < 35:

        warnings.append(
            "Current regime stability is low."
        )

    warnings.extend(forecast.warnings)

    return RegimeIntelligence(
        instrument=state.instrument,
        timestamp=state.timestamp,
        regime=state.regime_result.regime,
        direction=state.regime_result.direction_bias,
        volatility=state.regime_result.volatility_state,
        environment=state.environment,
        continuation_bias=continuation_bias,
        transition_bias=transition_bias,
        expansion_bias=expansion_bias,
        reversal_bias=reversal_bias,
        opportunity_state=opportunity_state,
        readiness_score=readiness_score,
        intelligence_quality=intelligence_quality,
        forecast=forecast,
        evidence=evidence,
        warnings=warnings,
    )


# ============================================================
# PUBLIC REGIME INTELLIGENCE API
# ============================================================

def regime_intelligence(
    self,
    data: RegimeMarketInput,
    timeframe: Optional[str] = None,
    mtf_observations: Optional[
        Dict[str, RegimeResult]
    ] = None,
) -> RegimeIntelligence:

    state = self.market_state(
        data=data,
        timeframe=timeframe,
        mtf_observations=mtf_observations,
    )

    return self._build_regime_intelligence(state)


# ============================================================
# FORECAST API
# ============================================================

def forecast_regime(
    self,
    data: RegimeMarketInput,
    timeframe: Optional[str] = None,
) -> RegimeForecast:

    state = self.market_state(
        data=data,
        timeframe=timeframe,
    )

    return self._calculate_regime_forecast(state)


# ============================================================
# ATTACH METHODS TO REGIME ENGINE
# ============================================================

RegimeEngine._calculate_regime_forecast = (
    _calculate_regime_forecast
)

RegimeEngine._build_regime_intelligence = (
    _build_regime_intelligence
)

RegimeEngine.regime_intelligence = (
    regime_intelligence
)

RegimeEngine.forecast_regime = (
    forecast_regime
)


# ============================================================
# EXPORTS
# ============================================================

__all__.extend([
    "RegimeForecast",
    "RegimeIntelligence",
])