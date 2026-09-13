from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from math import exp, isfinite
from statistics import mean
from typing import Any, Mapping


class TimingState(str, Enum):
    OPTIMAL = "OPTIMAL"
    FAVORABLE = "FAVORABLE"
    NEUTRAL = "NEUTRAL"
    WEAK = "WEAK"
    AVOID = "AVOID"
    INSUFFICIENT = "INSUFFICIENT"
    CONFLICTED = "CONFLICTED"


class TimingPhase(str, Enum):
    PRE_OPEN = "PRE_OPEN"
    OPENING = "OPENING"
    MORNING = "MORNING"
    MIDDAY = "MIDDAY"
    AFTERNOON = "AFTERNOON"
    CLOSING = "CLOSING"
    POST_CLOSE = "POST_CLOSE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class TimingAssessment:
    timing_score: float
    state: str
    phase: str
    session_quality: float
    liquidity_quality: float
    volatility_quality: float
    momentum_quality: float
    participation_quality: float
    event_quality: float
    persistence_quality: float
    directional_bias: str
    confidence: float
    decision_ready: bool
    expected_window_score: float
    decay_factor: float
    contradictions: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()
    risk_flags: tuple[str, ...] = ()
    evidence: Mapping[str, Any] = field(default_factory=dict)
    timestamp: str = ""


class TimingIntelligence:
    """
    ROBOMLM Timing Intelligence Engine.

    Timing is modeled as a multi-dimensional state, not as a clock-only
    rule.

    Core model:

        T = Sw*0.20
          + Lq*0.15
          + Vq*0.15
          + Mq*0.15
          + Pq*0.15
          + Eq*0.10
          + Pq2*0.10

    Where:

        Sw  = Session/Window Quality
        Lq  = Liquidity Quality
        Vq  = Volatility Quality
        Mq  = Momentum Quality
        Pq  = Participation Quality
        Eq  = Event Quality
        Pq2 = Persistence Quality

    Additional timing mathematics:

        Activity = (Volume / BaselineVolume) *
                   (Range / BaselineRange)

        LiquidityRatio = CurrentLiquidity / BaselineLiquidity

        VolumeRatio = CurrentVolume / BaselineVolume

        RangeRatio = CurrentRange / BaselineRange

        MomentumPersistence =
            directional persistence over supplied observations

        Decay(t) = exp(-lambda * elapsed_fraction)

    The engine does not execute trades and does not bypass risk,
    authorization, kill-switch or execution controls.
    """

    VERSION = "ROBOMLM-TIMING-2.0"

    WEIGHTS = {
        "session_quality": 0.20,
        "liquidity_quality": 0.15,
        "volatility_quality": 0.15,
        "momentum_quality": 0.15,
        "participation_quality": 0.15,
        "event_quality": 0.10,
        "persistence_quality": 0.10,
    }

    OPTIMAL_THRESHOLD = 85.0
    FAVORABLE_THRESHOLD = 70.0
    NEUTRAL_THRESHOLD = 50.0
    WEAK_THRESHOLD = 35.0

    MIN_LIQUIDITY = 30.0
    MIN_PARTICIPATION = 30.0
    MIN_PERSISTENCE = 30.0
    MIN_DECISION_SCORE = 70.0

    # Session windows expressed as minutes after midnight.
    DEFAULT_WINDOWS = {
        "PRE_OPEN": (0, 9 * 60 + 15),
        "OPENING": (9 * 60 + 15, 10 * 60),
        "MORNING": (10 * 60, 11 * 60 + 30),
        "MIDDAY": (11 * 60 + 30, 13 * 60),
        "AFTERNOON": (13 * 60, 15 * 60),
        "CLOSING": (15 * 60, 15 * 60 + 30),
        "POST_CLOSE": (15 * 60 + 30, 24 * 60),
    }

    def __init__(
        self,
        *,
        decay_lambda: float = 1.0,
        windows: Mapping[str, tuple[int, int]] | None = None,
    ) -> None:
        if not isfinite(decay_lambda) or decay_lambda < 0.0:
            raise ValueError("decay_lambda must be finite and >= 0")

        self.decay_lambda = float(decay_lambda)
        self.windows = dict(windows or self.DEFAULT_WINDOWS)
        self._history: list[TimingAssessment] = []

    # ------------------------------------------------------------------
    # Generic mathematical helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _number(value: Any, default: float = 0.0) -> float:
        try:
            number = float(value)
            return number if isfinite(number) else default
        except (TypeError, ValueError):
            return default

    @classmethod
    def _score(cls, value: Any, default: float = 50.0) -> float:
        """
        Convert a score to the canonical 0..100 domain.

        If input is in [-1, +1], map it to [0,100]:

            score = (x + 1) * 50
        """
        number = cls._number(value, default)

        if -1.0 <= number <= 1.0:
            number = (number + 1.0) * 50.0

        return max(0.0, min(100.0, number))

    @staticmethod
    def _text(value: Any) -> str:
        return "" if value is None else str(value).strip().upper()

    @staticmethod
    def _value(
        data: Mapping[str, Any] | None,
        *keys: str,
        default: Any = None,
    ) -> Any:
        if not data:
            return default

        for key in keys:
            value = data.get(key)
            if value is not None:
                return value

        return default

    # ------------------------------------------------------------------
    # Ratios
    # ------------------------------------------------------------------

    @classmethod
    def _safe_ratio(
        cls,
        numerator: Any,
        denominator: Any,
        *,
        default: float = 1.0,
    ) -> float:
        num = cls._number(numerator, 0.0)
        den = cls._number(denominator, 0.0)

        if den <= 0.0:
            return default

        ratio = num / den

        if not isfinite(ratio):
            return default

        return max(0.0, ratio)

    @staticmethod
    def _ratio_to_score(
        ratio: float,
        *,
        low: float = 0.50,
        ideal: float = 1.00,
        high: float = 2.00,
    ) -> float:
        """
        Piecewise quality function.

        Below low:
            linear deterioration toward 0.

        low..ideal:
            linear rise toward 70.

        ideal..high:
            linear rise toward 100.

        Above high:
            cap at 100.

        This avoids treating infinitely increasing activity as infinitely
        better timing.
        """
        if ratio <= 0.0:
            return 0.0

        if ratio < low:
            return max(0.0, 70.0 * ratio / low)

        if ratio <= ideal:
            return 70.0 * (
                (ratio - low) / (ideal - low)
            )

        if ratio <= high:
            return 70.0 + 30.0 * (
                (ratio - ideal) / (high - ideal)
            )

        return 100.0

    # ------------------------------------------------------------------
    # Clock / phase
    # ------------------------------------------------------------------

    @staticmethod
    def _minute_of_day(hour: int, minute: int) -> int:
        return hour * 60 + minute

    def phase_from_clock(
        self,
        hour: int,
        minute: int,
    ) -> TimingPhase:
        minute_of_day = self._minute_of_day(hour, minute)

        for name, (start, end) in self.windows.items():
            if start <= minute_of_day < end:
                try:
                    return TimingPhase(name)
                except ValueError:
                    return TimingPhase.UNKNOWN

        return TimingPhase.UNKNOWN

    def _extract_phase(
        self,
        context: Mapping[str, Any],
    ) -> TimingPhase:
        explicit = self._text(
            self._value(
                context,
                "phase",
                "timing_phase",
                default="",
            )
        )

        if explicit:
            try:
                return TimingPhase(explicit)
            except ValueError:
                pass

        hour = self._value(context, "hour", default=None)
        minute = self._value(context, "minute", default=None)

        if hour is not None and minute is not None:
            return self.phase_from_clock(
                int(self._number(hour)),
                int(self._number(minute)),
            )

        return TimingPhase.UNKNOWN

    # ------------------------------------------------------------------
    # Session quality
    # ------------------------------------------------------------------

    def _session_quality(
        self,
        context: Mapping[str, Any],
        phase: TimingPhase,
    ) -> float:
        explicit = self._value(
            context,
            "session_quality",
            "timing_score",
            default=None,
        )

        if explicit is not None:
            return self._score(explicit)

        phase_scores = {
            TimingPhase.PRE_OPEN: 20.0,
            TimingPhase.OPENING: 90.0,
            TimingPhase.MORNING: 85.0,
            TimingPhase.MIDDAY: 45.0,
            TimingPhase.AFTERNOON: 80.0,
            TimingPhase.CLOSING: 75.0,
            TimingPhase.POST_CLOSE: 10.0,
            TimingPhase.UNKNOWN: 50.0,
        }

        base = phase_scores[phase]

        session = self._text(
            self._value(
                context,
                "session",
                "market_session",
                default="",
            )
        )

        session_adjustments = {
            "OPEN": 10.0,
            "ACTIVE": 10.0,
            "OVERLAP": 10.0,
            "QUIET": -15.0,
            "THIN": -25.0,
        }

        return max(
            0.0,
            min(
                100.0,
                base + session_adjustments.get(session, 0.0),
            ),
        )

    # ------------------------------------------------------------------
    # Liquidity mathematics
    # ------------------------------------------------------------------

    def _liquidity_quality(
        self,
        context: Mapping[str, Any],
    ) -> float:
        explicit = self._value(
            context,
            "liquidity_quality",
            "liquidity_score",
            default=None,
        )

        if explicit is not None:
            return self._score(explicit)

        current = self._value(
            context,
            "liquidity",
            "current_liquidity",
            default=None,
        )

        baseline = self._value(
            context,
            "baseline_liquidity",
            "average_liquidity",
            default=None,
        )

        if current is None or baseline is None:
            return 50.0

        ratio = self._safe_ratio(current, baseline)
        return self._ratio_to_score(
            ratio,
            low=0.40,
            ideal=1.00,
            high=1.75,
        )

    # ------------------------------------------------------------------
    # Volatility mathematics
    # ------------------------------------------------------------------

    def _volatility_quality(
        self,
        context: Mapping[str, Any],
    ) -> float:
        explicit = self._value(
            context,
            "volatility_quality",
            "volatility_score",
            default=None,
        )

        if explicit is not None:
            return self._score(explicit)

        current = self._value(
            context,
            "volatility",
            "current_volatility",
            "atr",
            default=None,
        )

        baseline = self._value(
            context,
            "baseline_volatility",
            "average_volatility",
            "atr_baseline",
            default=None,
        )

        if current is None or baseline is None:
            return 50.0

        ratio = self._safe_ratio(current, baseline)

        # Excessive volatility can reduce timing quality.
        if ratio <= 0.75:
            return max(0.0, ratio / 0.75 * 55.0)

        if ratio <= 1.25:
            return 55.0 + (
                (ratio - 0.75) / 0.50
            ) * 45.0

        if ratio <= 2.0:
            return 100.0 - (
                (ratio - 1.25) / 0.75
            ) * 55.0

        return 35.0

    # ------------------------------------------------------------------
    # Momentum mathematics
    # ------------------------------------------------------------------

    def _momentum_quality(
        self,
        context: Mapping[str, Any],
    ) -> float:
        explicit = self._value(
            context,
            "momentum_quality",
            "momentum_score",
            default=None,
        )

        if explicit is not None:
            return self._score(explicit)

        momentum = self._value(
            context,
            "momentum",
            "momentum_strength",
            default=None,
        )

        if momentum is not None:
            return self._score(momentum)

        returns = self._value(
            context,
            "returns",
            "return_series",
            default=None,
        )

        if not isinstance(returns, (list, tuple)) or len(returns) < 2:
            return 50.0

        values = [
            self._number(item, 0.0)
            for item in returns
        ]

        nonzero = [
            value
            for value in values
            if value != 0.0
        ]

        if not nonzero:
            return 0.0

        positive = sum(1 for value in nonzero if value > 0)
        negative = sum(1 for value in nonzero if value < 0)

        persistence = max(positive, negative) / len(nonzero)

        average_abs = mean(abs(value) for value in nonzero)

        if average_abs <= 0.0:
            magnitude_factor = 0.0
        else:
            magnitude_factor = min(1.0, average_abs / 0.01)

        return max(
            0.0,
            min(
                100.0,
                persistence * 70.0
                + magnitude_factor * 30.0,
            ),
        )

    # ------------------------------------------------------------------
    # Participation mathematics
    # ------------------------------------------------------------------

    def _participation_quality(
        self,
        context: Mapping[str, Any],
    ) -> float:
        explicit = self._value(
            context,
            "participation_quality",
            "participation_score",
            default=None,
        )

        if explicit is not None:
            return self._score(explicit)

        current = self._value(
            context,
            "volume",
            "current_volume",
            default=None,
        )

        baseline = self._value(
            context,
            "baseline_volume",
            "average_volume",
            default=None,
        )

        breadth = self._value(
            context,
            "breadth",
            "participation_breadth",
            default=None,
        )

        volume_score = 50.0

        if current is not None and baseline is not None:
            volume_ratio = self._safe_ratio(
                current,
                baseline,
            )
            volume_score = self._ratio_to_score(
                volume_ratio,
                low=0.40,
                ideal=1.00,
                high=2.00,
            )

        breadth_score = (
            self._score(breadth)
            if breadth is not None
            else 50.0
        )

        return (
            volume_score * 0.60
            + breadth_score * 0.40
        )

    # ------------------------------------------------------------------
    # Event quality
    # ------------------------------------------------------------------

    def _event_quality(
        self,
        context: Mapping[str, Any],
    ) -> float:
        explicit = self._value(
            context,
            "event_quality",
            "event_score",
            default=None,
        )

        if explicit is not None:
            return self._score(explicit)

        event_risk = self._value(
            context,
            "event_risk",
            "news_risk",
            default=None,
        )

        if event_risk is None:
            return 70.0

        # Risk is inverted because this dimension measures timing quality.
        return 100.0 - self._score(event_risk, 30.0)

    # ------------------------------------------------------------------
    # Persistence mathematics
    # ------------------------------------------------------------------

    def _persistence_quality(
        self,
        context: Mapping[str, Any],
    ) -> float:
        explicit = self._value(
            context,
            "persistence_quality",
            "persistence_score",
            default=None,
        )

        if explicit is not None:
            return self._score(explicit)

        observations = self._value(
            context,
            "direction_series",
            "directions",
            default=None,
        )

        if not isinstance(observations, (list, tuple)):
            return 50.0

        directions = [
            self._direction(item)
            for item in observations
        ]

        directions = [
            item
            for item in directions
            if item in {"BUY", "SELL"}
        ]

        if len(directions) < 2:
            return 50.0

        longest = 1
        current = 1

        for index in range(1, len(directions)):
            if directions[index] == directions[index - 1]:
                current += 1
            else:
                longest = max(longest, current)
                current = 1

        longest = max(longest, current)

        persistence_ratio = longest / len(directions)

        return min(100.0, persistence_ratio * 100.0)

    # ------------------------------------------------------------------
    # Direction
    # ------------------------------------------------------------------

    @staticmethod
    def _direction(value: Any) -> str:
        text = "" if value is None else str(value).strip().upper()

        if text in {"BUY", "LONG", "UP", "BULLISH"}:
            return "BUY"

        if text in {"SELL", "SHORT", "DOWN", "BEARISH"}:
            return "SELL"

        if text in {"HOLD", "NEUTRAL", "FLAT", ""}:
            return "NEUTRAL"

        return text

    def _directional_bias(
        self,
        context: Mapping[str, Any],
    ) -> str:
        directions: list[str] = []

        for key in (
            "direction",
            "bias",
            "trend_direction",
            "momentum_direction",
            "intelligence_bias",
        ):
            value = self._value(context, key, default=None)

            if value is None:
                continue

            direction = self._direction(value)

            if direction in {"BUY", "SELL"}:
                directions.append(direction)

        if not directions:
            return "NEUTRAL"

        buy_count = directions.count("BUY")
        sell_count = directions.count("SELL")

        if buy_count > sell_count:
            return "BUY"

        if sell_count > buy_count:
            return "SELL"

        return "CONFLICTED"

    # ------------------------------------------------------------------
    # Activity / opportunity window
    # ------------------------------------------------------------------

    def activity_ratio(
        self,
        *,
        current_volume: float,
        baseline_volume: float,
        current_range: float,
        baseline_range: float,
    ) -> float:
        """
        Activity intensity:

            A = (V / Vb) * (R / Rb)

        where:
            V  = current volume
            Vb = baseline volume
            R  = current range
            Rb = baseline range
        """
        volume_ratio = self._safe_ratio(
            current_volume,
            baseline_volume,
            default=0.0,
        )

        range_ratio = self._safe_ratio(
            current_range,
            baseline_range,
            default=0.0,
        )

        return round(
            max(0.0, volume_ratio * range_ratio),
            6,
        )

    def expected_window_score(
        self,
        *,
        volume_ratio: float,
        range_ratio: float,
        liquidity_ratio: float,
    ) -> float:
        """
        Expected-window score:

            W = 0.40*Vq + 0.35*Rq + 0.25*Lq
        """
        volume_quality = self._ratio_to_score(
            max(0.0, volume_ratio),
            low=0.40,
            ideal=1.00,
            high=2.00,
        )

        range_quality = self._ratio_to_score(
            max(0.0, range_ratio),
            low=0.40,
            ideal=1.00,
            high=2.00,
        )

        liquidity_quality = self._ratio_to_score(
            max(0.0, liquidity_ratio),
            low=0.40,
            ideal=1.00,
            high=1.75,
        )

        return round(
            volume_quality * 0.40
            + range_quality * 0.35
            + liquidity_quality * 0.25,
            4,
        )

    # ------------------------------------------------------------------
    # Decay
    # ------------------------------------------------------------------

    def decay_factor(
        self,
        *,
        elapsed_fraction: float,
    ) -> float:
        """
        Exponential persistence decay:

            D(t) = e^(-lambda*t)

        elapsed_fraction:
            0.0 = no decay
            1.0 = one normalized timing window elapsed
        """
        elapsed = max(0.0, self._number(elapsed_fraction, 0.0))

        return round(
            exp(-self.decay_lambda * elapsed),
            6,
        )

    # ------------------------------------------------------------------
    # Composite
    # ------------------------------------------------------------------

    def calculate_timing(
        self,
        *,
        session_quality: float,
        liquidity_quality: float,
        volatility_quality: float,
        momentum_quality: float,
        participation_quality: float,
        event_quality: float,
        persistence_quality: float,
    ) -> float:
        """
        Canonical timing equation:

            T =
                Sw*0.20
              + Lq*0.15
              + Vq*0.15
              + Mq*0.15
              + Pq*0.15
              + Eq*0.10
              + Ps*0.10
        """
        score = (
            session_quality * self.WEIGHTS["session_quality"]
            + liquidity_quality * self.WEIGHTS["liquidity_quality"]
            + volatility_quality * self.WEIGHTS["volatility_quality"]
            + momentum_quality * self.WEIGHTS["momentum_quality"]
            + participation_quality * self.WEIGHTS["participation_quality"]
            + event_quality * self.WEIGHTS["event_quality"]
            + persistence_quality * self.WEIGHTS["persistence_quality"]
        )

        return round(
            max(0.0, min(100.0, score)),
            4,
        )

    # ------------------------------------------------------------------
    # Contradictions
    # ------------------------------------------------------------------

    def _contradictions(
        self,
        context: Mapping[str, Any],
        components: Mapping[str, float],
        directional_bias: str,
    ) -> list[str]:
        contradictions: list[str] = []

        if components["liquidity_quality"] < self.MIN_LIQUIDITY:
            contradictions.append("low_liquidity")

        if components["participation_quality"] < self.MIN_PARTICIPATION:
            contradictions.append("weak_participation")

        if components["persistence_quality"] < self.MIN_PERSISTENCE:
            contradictions.append("weak_directional_persistence")

        phase = self._extract_phase(context)

        if phase in {
            TimingPhase.PRE_OPEN,
            TimingPhase.POST_CLOSE,
        }:
            contradictions.append("outside_primary_execution_window")

        if components["volatility_quality"] < 25.0:
            contradictions.append("volatility_quality_weak")

        if components["event_quality"] < 30.0:
            contradictions.append("event_risk_degrades_timing")

        if directional_bias == "CONFLICTED":
            contradictions.append("directional_conflict")

        explicit = self._value(
            context,
            "timing_conflict",
            "conflicted",
            "contradiction",
            default=False,
        )

        if bool(explicit):
            contradictions.append("upstream_timing_conflict")

        return contradictions

    # ------------------------------------------------------------------
    # Confidence
    # ------------------------------------------------------------------

    def _confidence(
        self,
        components: Mapping[str, float],
        score: float,
        contradictions: list[str],
    ) -> float:
        values = list(components.values())

        if not values:
            return 0.0

        average = mean(values)
        minimum = min(values)
        spread = max(values) - minimum

        confidence = (
            average * 0.45
            + minimum * 0.30
            + score * 0.25
        )

        if spread > 60.0:
            confidence -= 15.0
        elif spread > 40.0:
            confidence -= 8.0

        confidence -= len(contradictions) * 8.0

        return round(
            max(0.0, min(100.0, confidence)),
            4,
        )

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------

    def classify(
        self,
        score: float,
        contradictions: list[str],
    ) -> TimingState:
        if contradictions:
            if score >= self.FAVORABLE_THRESHOLD:
                return TimingState.CONFLICTED

        if score >= self.OPTIMAL_THRESHOLD:
            return TimingState.OPTIMAL

        if score >= self.FAVORABLE_THRESHOLD:
            return TimingState.FAVORABLE

        if score >= self.NEUTRAL_THRESHOLD:
            return TimingState.NEUTRAL

        if score >= self.WEAK_THRESHOLD:
            return TimingState.WEAK

        return TimingState.AVOID

    # ------------------------------------------------------------------
    # Main assessment
    # ------------------------------------------------------------------

    def assess(
        self,
        context: Mapping[str, Any] | None = None,
    ) -> TimingAssessment:
        context = dict(context or {})

        phase = self._extract_phase(context)

        session_quality = self._session_quality(
            context,
            phase,
        )

        liquidity_quality = self._liquidity_quality(context)
        volatility_quality = self._volatility_quality(context)
        momentum_quality = self._momentum_quality(context)
        participation_quality = self._participation_quality(context)
        event_quality = self._event_quality(context)
        persistence_quality = self._persistence_quality(context)

        components = {
            "session_quality": session_quality,
            "liquidity_quality": liquidity_quality,
            "volatility_quality": volatility_quality,
            "momentum_quality": momentum_quality,
            "participation_quality": participation_quality,
            "event_quality": event_quality,
            "persistence_quality": persistence_quality,
        }

        timing_score = self.calculate_timing(**components)

        directional_bias = self._directional_bias(context)

        contradictions = self._contradictions(
            context,
            components,
            directional_bias,
        )

        state = self.classify(
            timing_score,
            contradictions,
        )

        volume_ratio = self._safe_ratio(
            self._value(
                context,
                "volume",
                "current_volume",
                default=0.0,
            ),
            self._value(
                context,
                "baseline_volume",
                "average_volume",
                default=1.0,
            ),
        )

        range_ratio = self._safe_ratio(
            self._value(
                context,
                "range",
                "current_range",
                default=0.0,
            ),
            self._value(
                context,
                "baseline_range",
                "average_range",
                default=1.0,
            ),
        )

        liquidity_ratio = self._safe_ratio(
            self._value(
                context,
                "liquidity",
                "current_liquidity",
                default=0.0,
            ),
            self._value(
                context,
                "baseline_liquidity",
                "average_liquidity",
                default=1.0,
            ),
        )

        window_score = self.expected_window_score(
            volume_ratio=volume_ratio,
            range_ratio=range_ratio,
            liquidity_ratio=liquidity_ratio,
        )

        elapsed_fraction = self._number(
            self._value(
                context,
                "elapsed_fraction",
                "window_elapsed_fraction",
                default=0.0,
            ),
            0.0,
        )

        decay = self.decay_factor(
            elapsed_fraction=elapsed_fraction,
        )

        confidence = self._confidence(
            components,
            timing_score,
            contradictions,
        )

        evidence_score = self._score(
            self._value(
                context,
                "evidence_score",
                "evidence_quality",
                default=50.0,
            ),
            50.0,
        )

        decision_ready = (
            timing_score >= self.MIN_DECISION_SCORE
            and evidence_score >= 40.0
            and liquidity_quality >= self.MIN_LIQUIDITY
            and participation_quality >= self.MIN_PARTICIPATION
            and persistence_quality >= self.MIN_PERSISTENCE
            and not contradictions
            and directional_bias in {"BUY", "SELL", "NEUTRAL"}
        )

        reasons: list[str] = []

        if session_quality >= 70.0:
            reasons.append("session_window_supportive")

        if liquidity_quality >= 70.0:
            reasons.append("liquidity_supportive")

        if volatility_quality >= 70.0:
            reasons.append("volatility_profile_supportive")

        if momentum_quality >= 70.0:
            reasons.append("momentum_supportive")

        if participation_quality >= 70.0:
            reasons.append("participation_supportive")

        if event_quality >= 70.0:
            reasons.append("event_environment_supportive")

        if persistence_quality >= 70.0:
            reasons.append("directional_persistence_supportive")

        if window_score >= 70.0:
            reasons.append("activity_window_supportive")

        if decay < 0.50:
            reasons.append("timing_edge_under_decay_pressure")

        risk_flags: list[str] = []

        if liquidity_quality < self.MIN_LIQUIDITY:
            risk_flags.append("LOW_LIQUIDITY")

        if participation_quality < self.MIN_PARTICIPATION:
            risk_flags.append("LOW_PARTICIPATION")

        if persistence_quality < self.MIN_PERSISTENCE:
            risk_flags.append("LOW_PERSISTENCE")

        if event_quality < 30.0:
            risk_flags.append("HIGH_EVENT_RISK")

        if phase in {
            TimingPhase.PRE_OPEN,
            TimingPhase.POST_CLOSE,
        }:
            risk_flags.append("OUTSIDE_PRIMARY_WINDOW")

        if contradictions:
            risk_flags.append("TIMING_CONTRADICTION")

        if directional_bias == "CONFLICTED":
            risk_flags.append("DIRECTIONAL_CONFLICT")

        timestamp = datetime.now(timezone.utc).isoformat()

        assessment = TimingAssessment(
            timing_score=timing_score,
            state=state.value,
            phase=phase.value,
            session_quality=round(session_quality, 4),
            liquidity_quality=round(liquidity_quality, 4),
            volatility_quality=round(volatility_quality, 4),
            momentum_quality=round(momentum_quality, 4),
            participation_quality=round(participation_quality, 4),
            event_quality=round(event_quality, 4),
            persistence_quality=round(persistence_quality, 4),
            directional_bias=directional_bias,
            confidence=confidence,
            decision_ready=decision_ready,
            expected_window_score=window_score,
            decay_factor=decay,
            contradictions=tuple(dict.fromkeys(contradictions)),
            reasons=tuple(dict.fromkeys(reasons)),
            risk_flags=tuple(dict.fromkeys(risk_flags)),
            evidence={
                "components": dict(components),
                "weights": dict(self.WEIGHTS),
                "formula": (
                    "T = Sw*0.20 + Lq*0.15 + Vq*0.15 + "
                    "Mq*0.15 + Pq*0.15 + Eq*0.10 + Ps*0.10"
                ),
                "ratios": {
                    "volume_ratio": round(volume_ratio, 6),
                    "range_ratio": round(range_ratio, 6),
                    "liquidity_ratio": round(liquidity_ratio, 6),
                },
                "activity_formula": (
                    "A = (Volume/BaselineVolume) * "
                    "(Range/BaselineRange)"
                ),
                "decay_formula": "D(t) = exp(-lambda*t)",
            },
            timestamp=timestamp,
        )

        self._history.append(assessment)

        return assessment

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------

    @property
    def history(self) -> tuple[TimingAssessment, ...]:
        return tuple(self._history)

    @property
    def latest(self) -> TimingAssessment | None:
        return self._history[-1] if self._history else None

    def average_score(self) -> float:
        if not self._history:
            return 0.0

        return round(
            mean(item.timing_score for item in self._history),
            4,
        )

    def clear(self) -> None:
        self._history.clear()

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    def health_check(self) -> dict[str, Any]:
        weight_sum = sum(self.WEIGHTS.values())

        return {
            "engine": "TimingIntelligence",
            "version": self.VERSION,
            "healthy": abs(weight_sum - 1.0) < 1e-9,
            "weight_sum": weight_sum,
            "history_size": len(self._history),
            "decay_lambda": self.decay_lambda,
            "thresholds": {
                "optimal": self.OPTIMAL_THRESHOLD,
                "favorable": self.FAVORABLE_THRESHOLD,
                "neutral": self.NEUTRAL_THRESHOLD,
                "weak": self.WEAK_THRESHOLD,
            },
            "gates": {
                "minimum_liquidity": self.MIN_LIQUIDITY,
                "minimum_participation": self.MIN_PARTICIPATION,
                "minimum_persistence": self.MIN_PERSISTENCE,
                "minimum_decision_score": self.MIN_DECISION_SCORE,
            },
        }


TimingEngine = TimingIntelligence
MarketTimingIntelligence = TimingIntelligence


__all__ = [
    "TimingState",
    "TimingPhase",
    "TimingAssessment",
    "TimingIntelligence",
    "TimingEngine",
    "MarketTimingIntelligence",
]