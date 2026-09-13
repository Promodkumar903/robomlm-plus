# ============================================================
# ROBOMLM — RELATIONSHIP ENGINE
# PART 1 — FOUNDATION + RAW RELATIONSHIP MEASUREMENT
# ============================================================

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import math
import statistics


# ============================================================
# ENUMS
# ============================================================

class RelationshipType(Enum):
    UNKNOWN = "UNKNOWN"
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"
    DIVERGING = "DIVERGING"


class RelationshipStrength(Enum):
    UNKNOWN = "UNKNOWN"
    VERY_WEAK = "VERY_WEAK"
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    VERY_STRONG = "VERY_STRONG"


class RelationshipQuality(Enum):
    INVALID = "INVALID"
    PARTIAL = "PARTIAL"
    USABLE = "USABLE"
    HIGH = "HIGH"


# ============================================================
# RAW RELATIONSHIP INPUT
# ============================================================

@dataclass
class RelationshipInput:
    source_instrument: str
    target_instrument: str

    timestamp: datetime

    source_prices: List[float] = field(default_factory=list)
    target_prices: List[float] = field(default_factory=list)

    source_volume: List[float] = field(default_factory=list)
    target_volume: List[float] = field(default_factory=list)

    source_oi: List[float] = field(default_factory=list)
    target_oi: List[float] = field(default_factory=list)

    source_bid: Optional[float] = None
    source_ask: Optional[float] = None

    target_bid: Optional[float] = None
    target_ask: Optional[float] = None

    market: Optional[str] = None
    exchange: Optional[str] = None

    timeframe: Optional[str] = None
    data_source: Optional[str] = None


# ============================================================
# RELATIONSHIP MEASUREMENTS
# ============================================================

@dataclass
class RelationshipMeasurements:
    sample_size: int = 0

    price_correlation: float = 0.0
    return_correlation: float = 0.0

    volume_correlation: float = 0.0
    oi_correlation: float = 0.0

    source_return: float = 0.0
    target_return: float = 0.0

    source_volume_change: float = 0.0
    target_volume_change: float = 0.0

    source_oi_change: float = 0.0
    target_oi_change: float = 0.0

    price_relationship: RelationshipType = (
        RelationshipType.UNKNOWN
    )

    return_relationship: RelationshipType = (
        RelationshipType.UNKNOWN
    )

    volume_relationship: RelationshipType = (
        RelationshipType.UNKNOWN
    )

    oi_relationship: RelationshipType = (
        RelationshipType.UNKNOWN
    )


# ============================================================
# RELATIONSHIP RESULT
# ============================================================

@dataclass
class RelationshipResult:
    source_instrument: str
    target_instrument: str
    timestamp: datetime

    relationship_type: RelationshipType
    strength: RelationshipStrength
    quality: RelationshipQuality

    relationship_score: float
    divergence_score: float

    measurements: RelationshipMeasurements

    evidence: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    market: Optional[str] = None
    exchange: Optional[str] = None
    timeframe: Optional[str] = None
    data_source: Optional[str] = None

    engine: str = "RelationshipEngine"
    engine_version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:

        return {
            "source_instrument": self.source_instrument,
            "target_instrument": self.target_instrument,
            "timestamp": (
                self.timestamp.isoformat()
                if isinstance(self.timestamp, datetime)
                else self.timestamp
            ),
            "relationship_type": (
                self.relationship_type.value
            ),
            "strength": self.strength.value,
            "quality": self.quality.value,
            "relationship_score": round(
                self.relationship_score,
                4,
            ),
            "divergence_score": round(
                self.divergence_score,
                4,
            ),
            "measurements": self.measurements.__dict__,
            "evidence": list(self.evidence),
            "warnings": list(self.warnings),
            "market": self.market,
            "exchange": self.exchange,
            "timeframe": self.timeframe,
            "data_source": self.data_source,
            "engine": self.engine,
            "engine_version": self.engine_version,
        }


# ============================================================
# RELATIONSHIP ENGINE
# ============================================================

class RelationshipEngine:

    """
    Measures relationships between market instruments.

    IMPORTANT:
    This engine measures relationships only.

    It does NOT:
        - issue final BUY/SELL decisions
        - override D13
        - invent missing market data
        - assume causality from correlation
        - convert correlation directly into a trade

    Downstream engines consume the normalized relationship
    intelligence.
    """

    def __init__(self):

        self.minimum_samples = 5

        # Initial engineering thresholds.
        # These are validation baselines, NOT permanent truth.
        self.very_strong_threshold = 0.80
        self.strong_threshold = 0.60
        self.moderate_threshold = 0.35
        self.weak_threshold = 0.15

        self.neutral_threshold = 0.15

        self.divergence_threshold = 0.35

        self.engine = "RelationshipEngine"
        self.engine_version = "1.0.0"


    # ========================================================
    # PUBLIC EVALUATION
    # ========================================================

    def evaluate(
        self,
        data: RelationshipInput,
    ) -> RelationshipResult:

        quality, warnings = self._validate_input(data)

        measurements = self._calculate_measurements(
            data
        )

        relationship_type = (
            self._classify_relationship(
                measurements
            )
        )

        strength = (
            self._classify_strength(
                measurements.return_correlation
            )
        )

        relationship_score = (
            self._calculate_relationship_score(
                measurements
            )
        )

        divergence_score = (
            self._calculate_divergence_score(
                measurements
            )
        )

        evidence = self._build_evidence(
            data,
            measurements,
            relationship_type,
            strength,
            divergence_score,
        )

        warnings.extend(
            self._build_warnings(
                measurements,
                quality,
            )
        )

        return RelationshipResult(
            source_instrument=data.source_instrument,
            target_instrument=data.target_instrument,
            timestamp=data.timestamp,

            relationship_type=relationship_type,
            strength=strength,
            quality=quality,

            relationship_score=relationship_score,
            divergence_score=divergence_score,

            measurements=measurements,

            evidence=evidence,
            warnings=warnings,

            market=data.market,
            exchange=data.exchange,
            timeframe=data.timeframe,
            data_source=data.data_source,

            engine=self.engine,
            engine_version=self.engine_version,
        )


    # ========================================================
    # VALIDATION
    # ========================================================

    def _validate_input(
        self,
        data: RelationshipInput,
    ) -> Tuple[
        RelationshipQuality,
        List[str],
    ]:

        warnings = []

        if not data.source_instrument:
            warnings.append(
                "Source instrument is missing."
            )

            return (
                RelationshipQuality.INVALID,
                warnings,
            )

        if not data.target_instrument:
            warnings.append(
                "Target instrument is missing."
            )

            return (
                RelationshipQuality.INVALID,
                warnings,
            )

        source = self._clean_series(
            data.source_prices
        )

        target = self._clean_series(
            data.target_prices
        )

        if len(source) < 2:
            warnings.append(
                "Insufficient source price observations."
            )

            return (
                RelationshipQuality.INVALID,
                warnings,
            )

        if len(target) < 2:
            warnings.append(
                "Insufficient target price observations."
            )

            return (
                RelationshipQuality.INVALID,
                warnings,
            )

        if len(source) != len(target):

            warnings.append(
                "Source and target price series have "
                "different lengths."
            )

            return (
                RelationshipQuality.PARTIAL,
                warnings,
            )

        if len(source) < self.minimum_samples:

            warnings.append(
                "Relationship sample size is below "
                "the minimum baseline."
            )

            return (
                RelationshipQuality.PARTIAL,
                warnings,
            )

        supporting_fields = 0

        if len(data.source_volume) >= 2:
            supporting_fields += 1

        if len(data.target_volume) >= 2:
            supporting_fields += 1

        if len(data.source_oi) >= 2:
            supporting_fields += 1

        if len(data.target_oi) >= 2:
            supporting_fields += 1

        if (
            supporting_fields >= 2
            and len(source) >= self.minimum_samples
        ):

            return (
                RelationshipQuality.HIGH,
                warnings,
            )

        return (
            RelationshipQuality.USABLE,
            warnings,
        )


    # ========================================================
    # SERIES CLEANING
    # ========================================================

    @staticmethod
    def _clean_series(
        values: List[float],
    ) -> List[float]:

        result = []

        for value in values:

            try:

                number = float(value)

                if (
                    math.isfinite(number)
                    and number > 0
                ):
                    result.append(number)

            except (
                TypeError,
                ValueError,
            ):
                continue

        return result


    # ========================================================
    # SERIES ALIGNMENT
    # ========================================================

    def _align_series(
        self,
        source: List[float],
        target: List[float],
    ) -> Tuple[
        List[float],
        List[float],
    ]:

        source_clean = self._clean_series(
            source
        )

        target_clean = self._clean_series(
            target
        )

        size = min(
            len(source_clean),
            len(target_clean),
        )

        if size <= 0:
            return [], []

        return (
            source_clean[-size:],
            target_clean[-size:],
        )


    # ========================================================
    # RETURN CALCULATION
    # ========================================================

    @staticmethod
    def _calculate_returns(
        prices: List[float],
    ) -> List[float]:

        clean = RelationshipEngine._clean_series(
            prices
        )

        if len(clean) < 2:
            return []

        returns = []

        for previous, current in zip(
            clean[:-1],
            clean[1:],
        ):

            if previous == 0:
                continue

            returns.append(
                (current - previous)
                / previous
            )

        return returns


    # ========================================================
    # CORRELATION
    # ========================================================

    @staticmethod
    def _pearson_correlation(
        x: List[float],
        y: List[float],
    ) -> float:

        if len(x) < 2 or len(y) < 2:
            return 0.0

        size = min(
            len(x),
            len(y),
        )

        x = x[-size:]
        y = y[-size:]

        mean_x = statistics.mean(x)
        mean_y = statistics.mean(y)

        numerator = sum(
            (a - mean_x)
            * (b - mean_y)
            for a, b in zip(x, y)
        )

        denominator_x = math.sqrt(
            sum(
                (a - mean_x) ** 2
                for a in x
            )
        )

        denominator_y = math.sqrt(
            sum(
                (b - mean_y) ** 2
                for b in y
            )
        )

        denominator = (
            denominator_x
            * denominator_y
        )

        if denominator == 0:
            return 0.0

        correlation = (
            numerator / denominator
        )

        return max(
            -1.0,
            min(1.0, correlation),
        )


    # ========================================================
    # MEASUREMENT ENGINE
    # ========================================================

    def _calculate_measurements(
        self,
        data: RelationshipInput,
    ) -> RelationshipMeasurements:

        source_prices, target_prices = (
            self._align_series(
                data.source_prices,
                data.target_prices,
            )
        )

        sample_size = min(
            len(source_prices),
            len(target_prices),
        )

        if sample_size < 2:

            return RelationshipMeasurements(
                sample_size=sample_size
            )

        source_returns = (
            self._calculate_returns(
                source_prices
            )
        )

        target_returns = (
            self._calculate_returns(
                target_prices
            )
        )

        price_correlation = (
            self._pearson_correlation(
                source_prices,
                target_prices,
            )
        )

        return_correlation = (
            self._pearson_correlation(
                source_returns,
                target_returns,
            )
        )

        source_volume = self._clean_series(
            data.source_volume
        )

        target_volume = self._clean_series(
            data.target_volume
        )

        volume_correlation = 0.0

        if (
            len(source_volume) >= 2
            and len(target_volume) >= 2
        ):

            volume_correlation = (
                self._pearson_correlation(
                    source_volume,
                    target_volume,
                )
            )

        source_oi = self._clean_series(
            data.source_oi
        )

        target_oi = self._clean_series(
            data.target_oi
        )

        oi_correlation = 0.0

        if (
            len(source_oi) >= 2
            and len(target_oi) >= 2
        ):

            oi_correlation = (
                self._pearson_correlation(
                    source_oi,
                    target_oi,
                )
            )

        source_return = self._latest_change(
            source_prices
        )

        target_return = self._latest_change(
            target_prices
        )

        source_volume_change = (
            self._latest_change(
                source_volume
            )
        )

        target_volume_change = (
            self._latest_change(
                target_volume
            )
        )

        source_oi_change = (
            self._latest_change(
                source_oi
            )
        )

        target_oi_change = (
            self._latest_change(
                target_oi
            )
        )

        price_relationship = (
            self._relationship_from_value(
                price_correlation
            )
        )

        return_relationship = (
            self._relationship_from_value(
                return_correlation
            )
        )

        volume_relationship = (
            self._relationship_from_value(
                volume_correlation
            )
            if volume_correlation != 0
            else RelationshipType.UNKNOWN
        )

        oi_relationship = (
            self._relationship_from_value(
                oi_correlation
            )
            if oi_correlation != 0
            else RelationshipType.UNKNOWN
        )

        return RelationshipMeasurements(
            sample_size=sample_size,

            price_correlation=price_correlation,
            return_correlation=return_correlation,

            volume_correlation=volume_correlation,
            oi_correlation=oi_correlation,

            source_return=source_return,
            target_return=target_return,

            source_volume_change=source_volume_change,
            target_volume_change=target_volume_change,

            source_oi_change=source_oi_change,
            target_oi_change=target_oi_change,

            price_relationship=price_relationship,
            return_relationship=return_relationship,

            volume_relationship=volume_relationship,
            oi_relationship=oi_relationship,
        )


    # ========================================================
    # LATEST CHANGE
    # ========================================================

    @staticmethod
    def _latest_change(
        values: List[float],
    ) -> float:

        clean = (
            RelationshipEngine._clean_series(
                values
            )
        )

        if len(clean) < 2:
            return 0.0

        previous = clean[-2]
        current = clean[-1]

        if previous == 0:
            return 0.0

        return (
            (current - previous)
            / previous
        )


    # ========================================================
    # RELATIONSHIP CLASSIFICATION
    # ========================================================

    def _relationship_from_value(
        self,
        correlation: float,
    ) -> RelationshipType:

        if not math.isfinite(correlation):
            return RelationshipType.UNKNOWN

        if abs(correlation) < self.neutral_threshold:
            return RelationshipType.NEUTRAL

        if correlation > 0:
            return RelationshipType.POSITIVE

        if correlation < 0:
            return RelationshipType.NEGATIVE

        return RelationshipType.UNKNOWN


    def _classify_relationship(
        self,
        measurements: RelationshipMeasurements,
    ) -> RelationshipType:

        correlation = (
            measurements.return_correlation
        )

        if abs(correlation) < self.neutral_threshold:

            return RelationshipType.NEUTRAL

        # Detect directional divergence.
        if (
            measurements.source_return > 0
            and measurements.target_return < 0
        ):

            return RelationshipType.DIVERGING

        if (
            measurements.source_return < 0
            and measurements.target_return > 0
        ):

            return RelationshipType.DIVERGING

        if correlation > 0:

            return RelationshipType.POSITIVE

        if correlation < 0:

            return RelationshipType.NEGATIVE

        return RelationshipType.UNKNOWN


    # ========================================================
    # STRENGTH
    # ========================================================

    def _classify_strength(
        self,
        correlation: float,
    ) -> RelationshipStrength:

        value = abs(correlation)

        if not math.isfinite(value):
            return RelationshipStrength.UNKNOWN

        if value >= self.very_strong_threshold:
            return RelationshipStrength.VERY_STRONG

        if value >= self.strong_threshold:
            return RelationshipStrength.STRONG

        if value >= self.moderate_threshold:
            return RelationshipStrength.MODERATE

        if value >= self.weak_threshold:
            return RelationshipStrength.WEAK

        return RelationshipStrength.VERY_WEAK


    # ========================================================
    # RELATIONSHIP SCORE
    # ========================================================

    def _calculate_relationship_score(
        self,
        measurements: RelationshipMeasurements,
    ) -> float:

        price_score = abs(
            measurements.price_correlation
        ) * 40.0

        return_score = abs(
            measurements.return_correlation
        ) * 40.0

        volume_score = abs(
            measurements.volume_correlation
        ) * 10.0

        oi_score = abs(
            measurements.oi_correlation
        ) * 10.0

        score = (
            price_score
            + return_score
            + volume_score
            + oi_score
        )

        return min(
            100.0,
            max(0.0, score),
        )


    # ========================================================
    # DIVERGENCE SCORE
    # ========================================================

    def _calculate_divergence_score(
        self,
        measurements: RelationshipMeasurements,
    ) -> float:

        source_return = (
            measurements.source_return
        )

        target_return = (
            measurements.target_return
        )

        # Opposite direction.
        if (
            source_return > 0
            and target_return < 0
        ) or (
            source_return < 0
            and target_return > 0
        ):

            magnitude = min(
                1.0,
                abs(source_return)
                + abs(target_return),
            )

            correlation_component = (
                abs(
                    measurements.return_correlation
                )
            )

            return min(
                100.0,
                (
                    magnitude * 500.0
                    + correlation_component * 50.0
                ),
            )

        # Same direction but correlation weakening.
        if (
            source_return != 0
            and target_return != 0
            and (
                source_return
                * target_return
            ) > 0
        ):

            correlation = abs(
                measurements.return_correlation
            )

            if correlation < self.divergence_threshold:

                return min(
                    100.0,
                    (
                        (1.0 - correlation)
                        * 60.0
                    ),
                )

        return 0.0


    # ========================================================
    # EVIDENCE
    # ========================================================

    def _build_evidence(
        self,
        data: RelationshipInput,
        measurements: RelationshipMeasurements,
        relationship_type: RelationshipType,
        strength: RelationshipStrength,
        divergence_score: float,
    ) -> List[str]:

        evidence = []

        evidence.append(
            f"Price correlation="
            f"{measurements.price_correlation:.3f}"
        )

        evidence.append(
            f"Return correlation="
            f"{measurements.return_correlation:.3f}"
        )

        evidence.append(
            f"Relationship="
            f"{relationship_type.value}"
        )

        evidence.append(
            f"Strength="
            f"{strength.value}"
        )

        if (
            measurements.volume_correlation
            != 0
        ):

            evidence.append(
                f"Volume correlation="
                f"{measurements.volume_correlation:.3f}"
            )

        if (
            measurements.oi_correlation
            != 0
        ):

            evidence.append(
                f"OI correlation="
                f"{measurements.oi_correlation:.3f}"
            )

        if divergence_score >= 50:

            evidence.append(
                "Meaningful cross-instrument divergence detected."
            )

        return evidence


    # ========================================================
    # WARNINGS
    # ========================================================

    def _build_warnings(
        self,
        measurements: RelationshipMeasurements,
        quality: RelationshipQuality,
    ) -> List[str]:

        warnings = []

        if quality in (
            RelationshipQuality.INVALID,
            RelationshipQuality.PARTIAL,
        ):

            warnings.append(
                "Relationship should not be treated as "
                "fully reliable with incomplete data."
            )

        if measurements.sample_size < 10:

            warnings.append(
                "Small sample size may make correlation unstable."
            )

        if (
            abs(measurements.return_correlation)
            < self.weak_threshold
        ):

            warnings.append(
                "Return relationship is weak or neutral."
            )

        warnings.append(
            "Correlation measures association; it does not establish causation."
        )

        return warnings


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "RelationshipType",
    "RelationshipStrength",
    "RelationshipQuality",
    "RelationshipInput",
    "RelationshipMeasurements",
    "RelationshipResult",
    "RelationshipEngine",
]
# ============================================================
# ROBOMLM — RELATIONSHIP ENGINE
# PART 2 — RELATIONSHIP HISTORY + PERSISTENCE + DYNAMICS
# ============================================================


# ============================================================
# RELATIONSHIP SNAPSHOT
# ============================================================

@dataclass
class RelationshipSnapshot:
    source_instrument: str
    target_instrument: str
    timestamp: datetime

    relationship_type: RelationshipType
    strength: RelationshipStrength

    relationship_score: float
    divergence_score: float

    price_correlation: float
    return_correlation: float

    source_return: float
    target_return: float

    timeframe: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:

        return {
            "source_instrument": self.source_instrument,
            "target_instrument": self.target_instrument,
            "timestamp": (
                self.timestamp.isoformat()
                if isinstance(self.timestamp, datetime)
                else self.timestamp
            ),
            "relationship_type": (
                self.relationship_type.value
            ),
            "strength": self.strength.value,
            "relationship_score": round(
                self.relationship_score,
                4,
            ),
            "divergence_score": round(
                self.divergence_score,
                4,
            ),
            "price_correlation": round(
                self.price_correlation,
                6,
            ),
            "return_correlation": round(
                self.return_correlation,
                6,
            ),
            "source_return": round(
                self.source_return,
                6,
            ),
            "target_return": round(
                self.target_return,
                6,
            ),
            "timeframe": self.timeframe,
        }


# ============================================================
# RELATIONSHIP DYNAMICS
# ============================================================

@dataclass
class RelationshipDynamics:
    relationship_velocity: float = 0.0
    relationship_acceleration: float = 0.0

    correlation_velocity: float = 0.0
    divergence_velocity: float = 0.0

    persistence_score: float = 0.0
    stability_score: float = 0.0

    strengthening: bool = False
    weakening: bool = False
    diverging: bool = False
    converging: bool = False

    relationship_change: str = "STABLE"

    evidence: List[str] = field(
        default_factory=list
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "relationship_velocity": round(
                self.relationship_velocity,
                4,
            ),
            "relationship_acceleration": round(
                self.relationship_acceleration,
                4,
            ),
            "correlation_velocity": round(
                self.correlation_velocity,
                4,
            ),
            "divergence_velocity": round(
                self.divergence_velocity,
                4,
            ),
            "persistence_score": round(
                self.persistence_score,
                2,
            ),
            "stability_score": round(
                self.stability_score,
                2,
            ),
            "strengthening": self.strengthening,
            "weakening": self.weakening,
            "diverging": self.diverging,
            "converging": self.converging,
            "relationship_change": self.relationship_change,
            "evidence": list(self.evidence),
        }


# ============================================================
# RELATIONSHIP STATE
# ============================================================

@dataclass
class RelationshipState:
    source_instrument: str
    target_instrument: str
    timestamp: datetime

    current: RelationshipResult
    previous: Optional[RelationshipSnapshot]

    dynamics: RelationshipDynamics

    observation_count: int
    consecutive_same_type: int
    consecutive_same_direction: int

    state_quality: float

    evidence: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "source_instrument": self.source_instrument,
            "target_instrument": self.target_instrument,
            "timestamp": (
                self.timestamp.isoformat()
                if isinstance(self.timestamp, datetime)
                else self.timestamp
            ),
            "current": self.current.to_dict(),
            "previous": (
                self.previous.to_dict()
                if self.previous
                else None
            ),
            "dynamics": self.dynamics.to_dict(),
            "observation_count": self.observation_count,
            "consecutive_same_type": (
                self.consecutive_same_type
            ),
            "consecutive_same_direction": (
                self.consecutive_same_direction
            ),
            "state_quality": round(
                self.state_quality,
                2,
            ),
            "evidence": list(self.evidence),
            "warnings": list(self.warnings),
        }


# ============================================================
# ENGINE HISTORY INITIALIZER
# ============================================================

def _relationship_init_history(
    self,
):

    if not hasattr(
        self,
        "_relationship_history",
    ):

        self._relationship_history = {}


    if not hasattr(
        self,
        "_relationship_max_history",
    ):

        self._relationship_max_history = 100


# ============================================================
# RELATIONSHIP KEY
# ============================================================

def _relationship_key(
    self,
    source_instrument: str,
    target_instrument: str,
) -> str:

    return (
        f"{source_instrument}"
        f"::"
        f"{target_instrument}"
    )


# ============================================================
# RECORD RELATIONSHIP STATE
# ============================================================

def record_relationship(
    self,
    result: RelationshipResult,
) -> RelationshipSnapshot:

    self._relationship_init_history()

    key = self._relationship_key(
        result.source_instrument,
        result.target_instrument,
    )

    snapshot = RelationshipSnapshot(
        source_instrument=(
            result.source_instrument
        ),
        target_instrument=(
            result.target_instrument
        ),
        timestamp=result.timestamp,

        relationship_type=(
            result.relationship_type
        ),
        strength=result.strength,

        relationship_score=(
            result.relationship_score
        ),
        divergence_score=(
            result.divergence_score
        ),

        price_correlation=(
            result.measurements.price_correlation
        ),
        return_correlation=(
            result.measurements.return_correlation
        ),

        source_return=(
            result.measurements.source_return
        ),
        target_return=(
            result.measurements.target_return
        ),

        timeframe=result.timeframe,
    )

    history = self._relationship_history.setdefault(
        key,
        [],
    )

    history.append(snapshot)

    if len(history) > self._relationship_max_history:

        del history[
            :len(history)
            - self._relationship_max_history
        ]

    return snapshot


# ============================================================
# GET RELATIONSHIP HISTORY
# ============================================================

def get_relationship_history(
    self,
    source_instrument: str,
    target_instrument: str,
    limit: Optional[int] = None,
) -> List[RelationshipSnapshot]:

    self._relationship_init_history()

    key = self._relationship_key(
        source_instrument,
        target_instrument,
    )

    history = self._relationship_history.get(
        key,
        [],
    )

    if limit is None:
        return list(history)

    if limit <= 0:
        return []

    return list(history[-limit:])


# ============================================================
# PREVIOUS RELATIONSHIP
# ============================================================

def get_previous_relationship(
    self,
    source_instrument: str,
    target_instrument: str,
) -> Optional[RelationshipSnapshot]:

    history = self.get_relationship_history(
        source_instrument,
        target_instrument,
    )

    if len(history) < 2:
        return None

    return history[-2]


# ============================================================
# CLEAR HISTORY
# ============================================================

def clear_relationship_history(
    self,
    source_instrument: Optional[str] = None,
    target_instrument: Optional[str] = None,
):

    self._relationship_init_history()

    if (
        source_instrument is None
        and target_instrument is None
    ):

        self._relationship_history.clear()
        return

    key = self._relationship_key(
        source_instrument,
        target_instrument,
    )

    self._relationship_history.pop(
        key,
        None,
    )


# ============================================================
# SAME RELATIONSHIP COUNT
# ============================================================

def _count_same_relationship(
    self,
    history: List[RelationshipSnapshot],
    current: RelationshipSnapshot,
) -> int:

    if not history:
        return 0

    count = 0

    for snapshot in reversed(history):

        if (
            snapshot.relationship_type
            == current.relationship_type
        ):

            count += 1

        else:
            break

    return count


# ============================================================
# SAME DIRECTION COUNT
# ============================================================

def _count_same_direction(
    self,
    history: List[RelationshipSnapshot],
    current: RelationshipSnapshot,
) -> int:

    if not history:
        return 0

    def direction(
        relationship: RelationshipType,
    ) -> str:

        if relationship == RelationshipType.POSITIVE:
            return "POSITIVE"

        if relationship == RelationshipType.NEGATIVE:
            return "NEGATIVE"

        if relationship == RelationshipType.DIVERGING:
            return "DIVERGING"

        return "NEUTRAL"

    current_direction = direction(
        current.relationship_type
    )

    count = 0

    for snapshot in reversed(history):

        if (
            direction(
                snapshot.relationship_type
            )
            == current_direction
        ):

            count += 1

        else:
            break

    return count


# ============================================================
# RELATIONSHIP DYNAMICS
# ============================================================

def analyze_relationship_dynamics(
    self,
    source_instrument: str,
    target_instrument: str,
    lookback: int = 8,
) -> RelationshipDynamics:

    history = self.get_relationship_history(
        source_instrument,
        target_instrument,
        limit=max(lookback, 3),
    )

    if len(history) < 2:

        return RelationshipDynamics(
            evidence=[
                "Insufficient relationship history "
                "for dynamic analysis."
            ]
        )

    current = history[-1]

    previous = history[-2]

    relationship_velocity = (
        current.relationship_score
        - previous.relationship_score
    )

    correlation_velocity = (
        current.return_correlation
        - previous.return_correlation
    )

    divergence_velocity = (
        current.divergence_score
        - previous.divergence_score
    )

    relationship_acceleration = 0.0

    if len(history) >= 3:

        prior = history[-3]

        previous_velocity = (
            previous.relationship_score
            - prior.relationship_score
        )

        relationship_acceleration = (
            relationship_velocity
            - previous_velocity
        )

    strengthening = (
        relationship_velocity >= 3.0
        and relationship_acceleration >= -2.0
    )

    weakening = (
        relationship_velocity <= -3.0
        or relationship_acceleration <= -5.0
    )

    diverging = (
        divergence_velocity >= 5.0
        or current.divergence_score >= 60.0
    )

    converging = (
        divergence_velocity <= -5.0
        and current.divergence_score < 60.0
    )

    # --------------------------------------------------------
    # PERSISTENCE
    # --------------------------------------------------------

    same_type_count = (
        self._count_same_relationship(
            history,
            current,
        )
    )

    persistence_score = min(
        100.0,
        (
            same_type_count
            / max(1, len(history))
        ) * 100.0,
    )

    # --------------------------------------------------------
    # STABILITY
    # --------------------------------------------------------

    if len(history) >= 3:

        relationship_values = [
            snapshot.relationship_score
            for snapshot in history
        ]

        try:

            dispersion = (
                statistics.pstdev(
                    relationship_values
                )
            )

        except statistics.StatisticsError:

            dispersion = 0.0

        stability_score = max(
            0.0,
            min(
                100.0,
                100.0 - dispersion,
            ),
        )

    else:

        stability_score = 50.0

    # --------------------------------------------------------
    # CHANGE STATE
    # --------------------------------------------------------

    relationship_change = "STABLE"

    if diverging:

        relationship_change = "DIVERGING"

    elif converging:

        relationship_change = "CONVERGING"

    elif strengthening:

        relationship_change = "STRENGTHENING"

    elif weakening:

        relationship_change = "WEAKENING"

    evidence = [
        f"Relationship velocity="
        f"{relationship_velocity:.2f}",
        f"Correlation velocity="
        f"{correlation_velocity:.4f}",
        f"Divergence velocity="
        f"{divergence_velocity:.2f}",
        f"Persistence="
        f"{persistence_score:.2f}",
        f"Stability="
        f"{stability_score:.2f}",
    ]

    if strengthening:

        evidence.append(
            "Relationship strength is increasing."
        )

    if weakening:

        evidence.append(
            "Relationship strength is decreasing."
        )

    if diverging:

        evidence.append(
            "Cross-instrument divergence is increasing."
        )

    if converging:

        evidence.append(
            "Cross-instrument divergence is decreasing."
        )

    return RelationshipDynamics(
        relationship_velocity=(
            relationship_velocity
        ),
        relationship_acceleration=(
            relationship_acceleration
        ),
        correlation_velocity=(
            correlation_velocity
        ),
        divergence_velocity=(
            divergence_velocity
        ),
        persistence_score=persistence_score,
        stability_score=stability_score,
        strengthening=strengthening,
        weakening=weakening,
        diverging=diverging,
        converging=converging,
        relationship_change=relationship_change,
        evidence=evidence,
    )


# ============================================================
# RELATIONSHIP STATE ANALYSIS
# ============================================================

def analyze_relationship_state(
    self,
    result: RelationshipResult,
) -> RelationshipState:

    self._relationship_init_history()

    previous = self.get_previous_relationship(
        result.source_instrument,
        result.target_instrument,
    )

    self.record_relationship(result)

    history = self.get_relationship_history(
        result.source_instrument,
        result.target_instrument,
    )

    current = history[-1]

    dynamics = (
        self.analyze_relationship_dynamics(
            result.source_instrument,
            result.target_instrument,
        )
    )

    same_type_count = (
        self._count_same_relationship(
            history,
            current,
        )
    )

    same_direction_count = (
        self._count_same_direction(
            history,
            current,
        )
    )

    # --------------------------------------------------------
    # STATE QUALITY
    # --------------------------------------------------------

    quality_map = {
        RelationshipQuality.INVALID: 0.0,
        RelationshipQuality.PARTIAL: 40.0,
        RelationshipQuality.USABLE: 70.0,
        RelationshipQuality.HIGH: 90.0,
    }

    base_quality = quality_map.get(
        result.quality,
        0.0,
    )

    state_quality = (
        base_quality * 0.45
        + result.relationship_score * 0.25
        + dynamics.persistence_score * 0.15
        + dynamics.stability_score * 0.15
    )

    if dynamics.diverging:

        state_quality *= 0.90

    state_quality = min(
        100.0,
        max(0.0, state_quality),
    )

    evidence = [
        f"Observation count="
        f"{len(history)}",
        f"Same relationship persistence="
        f"{same_type_count}",
        f"Same directional state persistence="
        f"{same_direction_count}",
    ]

    evidence.extend(
        dynamics.evidence
    )

    warnings = []

    if len(history) < 3:

        warnings.append(
            "Relationship history is short; "
            "persistence is not yet strongly established."
        )

    if dynamics.diverging:

        warnings.append(
            "Divergence is active; relationship should "
            "not be assumed stable."
        )

    if dynamics.weakening:

        warnings.append(
            "Relationship strength is weakening."
        )

    return RelationshipState(
        source_instrument=(
            result.source_instrument
        ),
        target_instrument=(
            result.target_instrument
        ),
        timestamp=result.timestamp,

        current=result,
        previous=previous,

        dynamics=dynamics,

        observation_count=len(history),
        consecutive_same_type=same_type_count,
        consecutive_same_direction=(
            same_direction_count
        ),

        state_quality=state_quality,

        evidence=evidence,
        warnings=warnings,
    )


# ============================================================
# HIGH-LEVEL ANALYZE API
# ============================================================

def analyze_relationship(
    self,
    data: RelationshipInput,
) -> RelationshipState:

    result = self.evaluate(data)

    return self.analyze_relationship_state(
        result
    )


# ============================================================
# ATTACH METHODS
# ============================================================

RelationshipEngine._relationship_init_history = (
    _relationship_init_history
)

RelationshipEngine._relationship_key = (
    _relationship_key
)

RelationshipEngine.record_relationship = (
    record_relationship
)

RelationshipEngine.get_relationship_history = (
    get_relationship_history
)

RelationshipEngine.get_previous_relationship = (
    get_previous_relationship
)

RelationshipEngine.clear_relationship_history = (
    clear_relationship_history
)

RelationshipEngine._count_same_relationship = (
    _count_same_relationship
)

RelationshipEngine._count_same_direction = (
    _count_same_direction
)

RelationshipEngine.analyze_relationship_dynamics = (
    analyze_relationship_dynamics
)

RelationshipEngine.analyze_relationship_state = (
    analyze_relationship_state
)

RelationshipEngine.analyze_relationship = (
    analyze_relationship
)


# ============================================================
# EXPORTS — PART 2
# ============================================================

__all__.extend([
    "RelationshipSnapshot",
    "RelationshipDynamics",
    "RelationshipState",
])
# ============================================================
# ROBOMLM — RELATIONSHIP ENGINE
# PART 3 — LEAD/LAG + INFLUENCE ANALYSIS
# ============================================================

@dataclass
class LeadLagResult:
    source_instrument: str
    target_instrument: str

    lead_instrument: Optional[str]

    lag_period: int

    lead_correlation: float
    influence_score: float

    confidence: float

    evidence: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "source_instrument":
                self.source_instrument,

            "target_instrument":
                self.target_instrument,

            "lead_instrument":
                self.lead_instrument,

            "lag_period":
                self.lag_period,

            "lead_correlation":
                round(
                    self.lead_correlation,
                    6,
                ),

            "influence_score":
                round(
                    self.influence_score,
                    2,
                ),

            "confidence":
                round(
                    self.confidence,
                    2,
                ),

            "evidence":
                list(self.evidence),

            "warnings":
                list(self.warnings),
        }


# ============================================================
# SHIFTED CORRELATION
# ============================================================

def _shifted_correlation(
    self,
    source: List[float],
    target: List[float],
    lag: int,
) -> float:

    if lag <= 0:
        return self._pearson_correlation(
            source,
            target,
        )

    if (
        len(source) <= lag
        or len(target) <= lag
    ):
        return 0.0

    shifted_source = source[:-lag]
    shifted_target = target[lag:]

    return self._pearson_correlation(
        shifted_source,
        shifted_target,
    )


# ============================================================
# LEAD/LAG DETECTION
# ============================================================

def detect_lead_lag(
    self,
    source_prices: List[float],
    target_prices: List[float],
    max_lag: int = 10,
) -> LeadLagResult:

    source_returns = (
        self._calculate_returns(
            source_prices
        )
    )

    target_returns = (
        self._calculate_returns(
            target_prices
        )
    )

    best_lag = 0
    best_corr = 0.0
    leader = None

    evidence = []
    warnings = []

    if (
        len(source_returns) < 5
        or len(target_returns) < 5
    ):

        warnings.append(
            "Insufficient observations for lead/lag analysis."
        )

        return LeadLagResult(
            source_instrument="UNKNOWN",
            target_instrument="UNKNOWN",
            lead_instrument=None,
            lag_period=0,
            lead_correlation=0.0,
            influence_score=0.0,
            confidence=0.0,
            warnings=warnings,
        )

    for lag in range(
        1,
        max_lag + 1,
    ):

        correlation = (
            self._shifted_correlation(
                source_returns,
                target_returns,
                lag,
            )
        )

        if abs(correlation) > abs(best_corr):

            best_corr = correlation
            best_lag = lag
            leader = "SOURCE"

    for lag in range(
        1,
        max_lag + 1,
    ):

        correlation = (
            self._shifted_correlation(
                target_returns,
                source_returns,
                lag,
            )
        )

        if abs(correlation) > abs(best_corr):

            best_corr = correlation
            best_lag = lag
            leader = "TARGET"

    influence_score = min(
        100.0,
        abs(best_corr) * 100.0,
    )

    confidence = influence_score

    if best_lag > 5:
        confidence *= 0.85

    if abs(best_corr) < 0.25:
        confidence *= 0.60

    if leader == "SOURCE":

        lead_instrument = "SOURCE"

        evidence.append(
            "Source instrument leads target."
        )

    elif leader == "TARGET":

        lead_instrument = "TARGET"

        evidence.append(
            "Target instrument leads source."
        )

    else:

        lead_instrument = None

        warnings.append(
            "No meaningful lead-lag structure detected."
        )

    evidence.append(
        f"Best lag={best_lag}"
    )

    evidence.append(
        f"Lead correlation={best_corr:.4f}"
    )

    return LeadLagResult(
        source_instrument="SOURCE",
        target_instrument="TARGET",

        lead_instrument=lead_instrument,

        lag_period=best_lag,

        lead_correlation=best_corr,

        influence_score=influence_score,

        confidence=confidence,

        evidence=evidence,
        warnings=warnings,
    )


# ============================================================
# RELATIONSHIP INFLUENCE
# ============================================================

@dataclass
class RelationshipInfluence:
    source_instrument: str
    target_instrument: str

    relationship_score: float

    influence_score: float
    predictive_score: float

    lead_lag: Optional[
        LeadLagResult
    ] = None

    evidence: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {
            "source_instrument":
                self.source_instrument,

            "target_instrument":
                self.target_instrument,

            "relationship_score":
                round(
                    self.relationship_score,
                    2,
                ),

            "influence_score":
                round(
                    self.influence_score,
                    2,
                ),

            "predictive_score":
                round(
                    self.predictive_score,
                    2,
                ),

            "lead_lag":
                (
                    self.lead_lag.to_dict()
                    if self.lead_lag
                    else None
                ),

            "evidence":
                list(self.evidence),

            "warnings":
                list(self.warnings),
        }


# ============================================================
# BUILD INFLUENCE
# ============================================================

def build_relationship_influence(
    self,
    state: RelationshipState,
    source_prices: List[float],
    target_prices: List[float],
) -> RelationshipInfluence:

    lead_lag = self.detect_lead_lag(
        source_prices,
        target_prices,
    )

    relationship_score = (
        state.current.relationship_score
    )

    influence_score = (
        relationship_score * 0.50
        + lead_lag.influence_score * 0.50
    )

    predictive_score = (
        influence_score
        * (
            lead_lag.confidence
            / 100.0
        )
    )

    evidence = [
        f"RelationshipScore="
        f"{relationship_score:.2f}",

        f"InfluenceScore="
        f"{influence_score:.2f}",

        f"PredictiveScore="
        f"{predictive_score:.2f}",
    ]

    evidence.extend(
        lead_lag.evidence
    )

    warnings = list(
        lead_lag.warnings
    )

    return RelationshipInfluence(
        source_instrument=(
            state.source_instrument
        ),

        target_instrument=(
            state.target_instrument
        ),

        relationship_score=(
            relationship_score
        ),

        influence_score=(
            influence_score
        ),

        predictive_score=(
            predictive_score
        ),

        lead_lag=lead_lag,

        evidence=evidence,

        warnings=warnings,
    )


# ============================================================
# ATTACH METHODS
# ============================================================

RelationshipEngine._shifted_correlation = (
    _shifted_correlation
)

RelationshipEngine.detect_lead_lag = (
    detect_lead_lag
)

RelationshipEngine.build_relationship_influence = (
    build_relationship_influence
)


# ============================================================
# EXPORTS
# ============================================================

__all__.extend([
    "LeadLagResult",
    "RelationshipInfluence",
])
# ============================================================
# ROBOMLM — RELATIONSHIP ENGINE
# PART 4 — RELATIONSHIP MATRIX
# ============================================================

@dataclass
class RelationshipMatrixNode:
    instrument: str

    relationship_count: int

    average_relationship_score: float

    average_influence_score: float

    strongest_connection: Optional[str]

    strongest_score: float

    network_strength: float

    evidence: List[str] = field(
        default_factory=list
    )

    def to_dict(self):

        return {
            "instrument":
                self.instrument,

            "relationship_count":
                self.relationship_count,

            "average_relationship_score":
                round(
                    self.average_relationship_score,
                    2,
                ),

            "average_influence_score":
                round(
                    self.average_influence_score,
                    2,
                ),

            "strongest_connection":
                self.strongest_connection,

            "strongest_score":
                round(
                    self.strongest_score,
                    2,
                ),

            "network_strength":
                round(
                    self.network_strength,
                    2,
                ),

            "evidence":
                list(self.evidence),
        }


# ============================================================
# MATRIX RESULT
# ============================================================

@dataclass
class RelationshipMatrix:

    timestamp: datetime

    instruments: List[str]

    matrix: Dict[
        str,
        Dict[str, float]
    ]

    influence_matrix: Dict[
        str,
        Dict[str, float]
    ]

    nodes: Dict[
        str,
        RelationshipMatrixNode
    ]

    total_relationships: int

    average_network_score: float

    evidence: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    def to_dict(self):

        return {
            "timestamp":
                (
                    self.timestamp.isoformat()
                    if isinstance(
                        self.timestamp,
                        datetime,
                    )
                    else self.timestamp
                ),

            "instruments":
                list(self.instruments),

            "matrix":
                self.matrix,

            "influence_matrix":
                self.influence_matrix,

            "nodes":
                {
                    k: v.to_dict()
                    for k, v in self.nodes.items()
                },

            "total_relationships":
                self.total_relationships,

            "average_network_score":
                round(
                    self.average_network_score,
                    2,
                ),

            "evidence":
                list(self.evidence),

            "warnings":
                list(self.warnings),
        }


# ============================================================
# EMPTY MATRIX
# ============================================================

def _create_empty_matrix(
    self,
    instruments: List[str],
):

    matrix = {}

    for instrument in instruments:

        matrix[instrument] = {}

        for target in instruments:

            matrix[instrument][target] = 0.0

    return matrix


# ============================================================
# BUILD MATRIX
# ============================================================

def build_relationship_matrix(
    self,
    influences: List[
        RelationshipInfluence
    ],
) -> RelationshipMatrix:

    instruments = sorted(
        list(
            set(
                (
                    influence.source_instrument
                    for influence in influences
                )
            )
            |
            set(
                (
                    influence.target_instrument
                    for influence in influences
                )
            )
        )
    )

    matrix = self._create_empty_matrix(
        instruments
    )

    influence_matrix = (
        self._create_empty_matrix(
            instruments
        )
    )

    for influence in influences:

        source = (
            influence.source_instrument
        )

        target = (
            influence.target_instrument
        )

        matrix[source][target] = (
            influence.relationship_score
        )

        influence_matrix[source][target] = (
            influence.influence_score
        )

    nodes = {}

    for instrument in instruments:

        relationship_scores = []

        influence_scores = []

        strongest_connection = None
        strongest_score = 0.0

        for target in instruments:

            if target == instrument:
                continue

            relationship_value = (
                matrix[instrument][target]
            )

            influence_value = (
                influence_matrix[instrument][target]
            )

            if relationship_value > 0:

                relationship_scores.append(
                    relationship_value
                )

            if influence_value > 0:

                influence_scores.append(
                    influence_value
                )

            if (
                relationship_value
                > strongest_score
            ):

                strongest_score = (
                    relationship_value
                )

                strongest_connection = (
                    target
                )

        avg_relationship = (
            statistics.mean(
                relationship_scores
            )
            if relationship_scores
            else 0.0
        )

        avg_influence = (
            statistics.mean(
                influence_scores
            )
            if influence_scores
            else 0.0
        )

        network_strength = (
            avg_relationship * 0.60
            + avg_influence * 0.40
        )

        nodes[instrument] = (
            RelationshipMatrixNode(
                instrument=instrument,

                relationship_count=len(
                    relationship_scores
                ),

                average_relationship_score=(
                    avg_relationship
                ),

                average_influence_score=(
                    avg_influence
                ),

                strongest_connection=(
                    strongest_connection
                ),

                strongest_score=(
                    strongest_score
                ),

                network_strength=(
                    network_strength
                ),

                evidence=[
                    (
                        f"Strongest="
                        f"{strongest_connection}"
                    )
                ],
            )
        )

    network_scores = [
        node.network_strength
        for node in nodes.values()
    ]

    average_network_score = (
        statistics.mean(
            network_scores
        )
        if network_scores
        else 0.0
    )

    evidence = [
        (
            f"Network instruments="
            f"{len(instruments)}"
        ),
        (
            f"Relationships="
            f"{len(influences)}"
        ),
        (
            f"AverageNetwork="
            f"{average_network_score:.2f}"
        ),
    ]

    return RelationshipMatrix(
        timestamp=datetime.utcnow(),

        instruments=instruments,

        matrix=matrix,

        influence_matrix=(
            influence_matrix
        ),

        nodes=nodes,

        total_relationships=len(
            influences
        ),

        average_network_score=(
            average_network_score
        ),

        evidence=evidence,
        warnings=[],
    )


# ============================================================
# TOP CONNECTED NODES
# ============================================================

def get_top_relationship_nodes(
    self,
    matrix: RelationshipMatrix,
    top_n: int = 5,
) -> List[
    RelationshipMatrixNode
]:

    nodes = list(
        matrix.nodes.values()
    )

    nodes.sort(
        key=lambda x:
        x.network_strength,
        reverse=True,
    )

    return nodes[:top_n]


# ============================================================
# STRONGEST RELATIONSHIPS
# ============================================================

def get_strongest_relationships(
    self,
    matrix: RelationshipMatrix,
    minimum_score: float = 60.0,
):

    results = []

    for source in matrix.instruments:

        for target in matrix.instruments:

            if source == target:
                continue

            score = (
                matrix.matrix[source][target]
            )

            if score >= minimum_score:

                results.append(
                    (
                        source,
                        target,
                        score,
                    )
                )

    results.sort(
        key=lambda x: x[2],
        reverse=True,
    )

    return results


# ============================================================
# ATTACH METHODS
# ============================================================

RelationshipEngine._create_empty_matrix = (
    _create_empty_matrix
)

RelationshipEngine.build_relationship_matrix = (
    build_relationship_matrix
)

RelationshipEngine.get_top_relationship_nodes = (
    get_top_relationship_nodes
)

RelationshipEngine.get_strongest_relationships = (
    get_strongest_relationships
)


# ============================================================
# EXPORTS
# ============================================================

__all__.extend([
    "RelationshipMatrixNode",
    "RelationshipMatrix",
])
# ============================================================
# ROBOMLM — RELATIONSHIP ENGINE
# PART 5 — INTELLIGENCE FEED LAYER
# ============================================================

@dataclass
class RelationshipIntelligence:

    timestamp: datetime

    network_score: float
    confidence_score: float

    strongest_node: Optional[str]

    strongest_relationships: List[
        Dict[str, Any]
    ] = field(
        default_factory=list
    )

    market_leaders: List[str] = field(
        default_factory=list
    )

    market_laggards: List[str] = field(
        default_factory=list
    )

    influence_ranking: List[
        Dict[str, Any]
    ] = field(
        default_factory=list
    )

    relationship_bias: str = "NEUTRAL"

    evidence: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    def to_dict(self):

        return {
            "timestamp":
                (
                    self.timestamp.isoformat()
                    if isinstance(
                        self.timestamp,
                        datetime,
                    )
                    else self.timestamp
                ),

            "network_score":
                round(
                    self.network_score,
                    2,
                ),

            "confidence_score":
                round(
                    self.confidence_score,
                    2,
                ),

            "strongest_node":
                self.strongest_node,

            "strongest_relationships":
                self.strongest_relationships,

            "market_leaders":
                list(self.market_leaders),

            "market_laggards":
                list(self.market_laggards),

            "influence_ranking":
                self.influence_ranking,

            "relationship_bias":
                self.relationship_bias,

            "evidence":
                list(self.evidence),

            "warnings":
                list(self.warnings),
        }


# ============================================================
# BUILD INTELLIGENCE
# ============================================================

def build_relationship_intelligence(
    self,
    matrix: RelationshipMatrix,
) -> RelationshipIntelligence:

    ranked_nodes = sorted(
        matrix.nodes.values(),
        key=lambda x:
        x.network_strength,
        reverse=True,
    )

    strongest_node = None

    if ranked_nodes:
        strongest_node = (
            ranked_nodes[0].instrument
        )

    strongest_relationships = []

    raw_relationships = (
        self.get_strongest_relationships(
            matrix,
            minimum_score=50.0,
        )
    )

    for source, target, score in (
        raw_relationships[:10]
    ):

        strongest_relationships.append(
            {
                "source": source,
                "target": target,
                "score": round(
                    score,
                    2,
                ),
            }
        )

    influence_ranking = []

    for node in ranked_nodes:

        influence_ranking.append(
            {
                "instrument":
                    node.instrument,

                "network_strength":
                    round(
                        node.network_strength,
                        2,
                    ),

                "relationship_count":
                    node.relationship_count,
            }
        )

    market_leaders = [
        node.instrument
        for node in ranked_nodes[:5]
    ]

    market_laggards = [
        node.instrument
        for node in ranked_nodes[-5:]
    ]

    network_score = (
        matrix.average_network_score
    )

    confidence_score = (
        min(
            100.0,
            (
                network_score * 0.70
                +
                min(
                    30.0,
                    len(
                        matrix.instruments
                    ) * 2.0
                )
            )
        )
    )

    relationship_bias = "NEUTRAL"

    if network_score >= 75:

        relationship_bias = (
            "HIGH_ALIGNMENT"
        )

    elif network_score >= 55:

        relationship_bias = (
            "MODERATE_ALIGNMENT"
        )

    elif network_score <= 30:

        relationship_bias = (
            "FRAGMENTED"
        )

    evidence = [
        (
            f"NetworkScore="
            f"{network_score:.2f}"
        ),
        (
            f"Confidence="
            f"{confidence_score:.2f}"
        ),
        (
            f"StrongestNode="
            f"{strongest_node}"
        ),
        (
            f"Instruments="
            f"{len(matrix.instruments)}"
        ),
    ]

    warnings = []

    if network_score < 40:

        warnings.append(
            "Relationship network is weak."
        )

    if len(matrix.instruments) < 3:

        warnings.append(
            "Network coverage is limited."
        )

    return RelationshipIntelligence(
        timestamp=datetime.utcnow(),

        network_score=network_score,

        confidence_score=(
            confidence_score
        ),

        strongest_node=(
            strongest_node
        ),

        strongest_relationships=(
            strongest_relationships
        ),

        market_leaders=(
            market_leaders
        ),

        market_laggards=(
            market_laggards
        ),

        influence_ranking=(
            influence_ranking
        ),

        relationship_bias=(
            relationship_bias
        ),

        evidence=evidence,

        warnings=warnings,
    )


# ============================================================
# D13 FEED
# ============================================================

def export_d13_feed(
    self,
    intelligence:
    RelationshipIntelligence,
) -> Dict[str, Any]:

    return {

        "engine":
            "RelationshipEngine",

        "network_score":
            intelligence.network_score,

        "confidence_score":
            intelligence.confidence_score,

        "relationship_bias":
            intelligence.relationship_bias,

        "strongest_node":
            intelligence.strongest_node,

        "leaders":
            intelligence.market_leaders,

        "laggards":
            intelligence.market_laggards,

        "top_relationships":
            intelligence.strongest_relationships,

        "timestamp":
            intelligence.timestamp.isoformat(),
    }


# ============================================================
# OPPORTUNITY FEED
# ============================================================

def export_opportunity_feed(
    self,
    intelligence:
    RelationshipIntelligence,
) -> Dict[str, Any]:

    return {

        "relationship_network":
            intelligence.network_score,

        "relationship_confidence":
            intelligence.confidence_score,

        "relationship_bias":
            intelligence.relationship_bias,

        "strongest_node":
            intelligence.strongest_node,

        "top_relationships":
            intelligence.strongest_relationships,
    }


# ============================================================
# REGIME FEED
# ============================================================

def export_regime_feed(
    self,
    intelligence:
    RelationshipIntelligence,
) -> Dict[str, Any]:

    return {

        "network_strength":
            intelligence.network_score,

        "alignment":
            intelligence.relationship_bias,

        "confidence":
            intelligence.confidence_score,
    }


# ============================================================
# ATTACH METHODS
# ============================================================

RelationshipEngine.build_relationship_intelligence = (
    build_relationship_intelligence
)

RelationshipEngine.export_d13_feed = (
    export_d13_feed
)

RelationshipEngine.export_opportunity_feed = (
    export_opportunity_feed
)

RelationshipEngine.export_regime_feed = (
    export_regime_feed
)


# ============================================================
# EXPORTS
# ============================================================

__all__.extend([
    "RelationshipIntelligence",
])