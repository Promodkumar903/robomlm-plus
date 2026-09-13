from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from math import isfinite
from statistics import mean
from typing import Any, Mapping, Optional, Sequence


@dataclass(frozen=True)
class RelationshipAssessment:
    timestamp: str
    primary_symbol: str
    related_symbol: str

    relationship_score: float
    relationship_strength: float
    confidence_score: float
    stability_score: float

    correlation_score: float
    relative_strength_score: float
    lead_lag_score: float
    intermarket_score: float
    confirmation_score: float
    divergence_score: float

    primary_direction: str
    related_direction: str
    relationship_direction: str

    state: str
    contradiction: bool
    contradiction_reasons: tuple[str, ...]

    observed: Mapping[str, Any] = field(default_factory=dict)
    derived: Mapping[str, Any] = field(default_factory=dict)
    evidence: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RelationshipIntelligence:
    """
    ROBOMLM Relationship Intelligence Engine.

    Purpose
    -------
    Converts cross-market observations into structured relationship
    intelligence suitable for Evidence / Context / Decision layers.

    Relationship dimensions
    -----------------------
    1. Correlation
    2. Relative strength
    3. Lead / lag
    4. Intermarket relationship
    5. Confirmation
    6. Divergence

    The engine preserves observed inputs separately from derived values.

    It does not:
        - place orders
        - authorize execution
        - modify positions
        - bypass risk controls
        - bypass kill-switch controls
        - act as a broker
    """

    VERSION = "ROBOMLM-RELATIONSHIP-2.0"

    WEIGHTS = {
        "correlation": 0.20,
        "relative_strength": 0.20,
        "lead_lag": 0.15,
        "intermarket": 0.15,
        "confirmation": 0.15,
        "divergence": 0.15,
    }

    STATES = (
        "STRONG_CONFIRMATION",
        "CONFIRMATION",
        "WEAK_CONFIRMATION",
        "NEUTRAL",
        "DIVERGENCE",
        "STRONG_DIVERGENCE",
        "CONFLICTED",
        "INSUFFICIENT",
    )

    def __init__(self, history_limit: int = 500) -> None:
        if history_limit < 1:
            raise ValueError("history_limit must be >= 1")

        self.history_limit = int(history_limit)
        self._history: list[RelationshipAssessment] = []

    # ------------------------------------------------------------------
    # Numeric primitives
    # ------------------------------------------------------------------

    @staticmethod
    def _clamp(
        value: float,
        low: float = 0.0,
        high: float = 100.0,
    ) -> float:
        if not isfinite(value):
            return low

        return max(
            low,
            min(high, float(value)),
        )

    @classmethod
    def _score(
        cls,
        value: Any,
        default: float = 0.0,
    ) -> float:
        if value is None:
            return cls._clamp(default)

        if isinstance(value, bool):
            return 100.0 if value else 0.0

        try:
            number = float(value)
        except (TypeError, ValueError):
            return cls._clamp(default)

        if not isfinite(number):
            return cls._clamp(default)

        return cls._clamp(number)

    @classmethod
    def _signed(
        cls,
        value: Any,
    ) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return 0.0

        if not isfinite(number):
            return 0.0

        return max(
            -100.0,
            min(100.0, number),
        )

    @staticmethod
    def _get(
        data: Mapping[str, Any],
        *keys: str,
        default: Any = None,
    ) -> Any:
        for key in keys:
            if key in data and data[key] is not None:
                return data[key]

        return default

    # ------------------------------------------------------------------
    # Direction
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_direction(value: Any) -> str:
        text = str(value or "").strip().upper()

        if text in {
            "BUY",
            "BULLISH",
            "LONG",
            "UP",
            "POSITIVE",
        }:
            return "BUY"

        if text in {
            "SELL",
            "BEARISH",
            "SHORT",
            "DOWN",
            "NEGATIVE",
        }:
            return "SELL"

        return "NEUTRAL"

    @classmethod
    def _direction_sign(
        cls,
        value: Any,
    ) -> int:
        direction = cls._normalize_direction(value)

        if direction == "BUY":
            return 1

        if direction == "SELL":
            return -1

        return 0

    # ------------------------------------------------------------------
    # Correlation
    # ------------------------------------------------------------------

    def _correlation(
        self,
        data: Mapping[str, Any],
    ) -> tuple[float, float]:
        """
        Returns:

            correlation_strength [0,100]
            signed_correlation [-100,100]
        """

        explicit_score = self._get(
            data,
            "correlation_score",
            "correlation_strength",
            default=None,
        )

        raw = self._get(
            data,
            "correlation",
            "pearson_correlation",
            "rolling_correlation",
            default=None,
        )

        if explicit_score is not None:
            score = self._score(
                explicit_score
            )

            raw_signed = (
                self._signed(raw)
                if raw is not None
                else 0.0
            )

            if raw_signed != 0.0:
                if abs(raw_signed) <= 1.0:
                    raw_signed *= 100.0
            else:
                raw_signed = score

            return score, self._signed(
                raw_signed
            )

        if raw is None:
            return 0.0, 0.0

        try:
            correlation = float(raw)
        except (TypeError, ValueError):
            return 0.0, 0.0

        if not isfinite(correlation):
            return 0.0, 0.0

        if -1.0 <= correlation <= 1.0:
            signed = correlation * 100.0
        else:
            signed = max(
                -100.0,
                min(100.0, correlation),
            )

        return (
            abs(signed),
            signed,
        )

    # ------------------------------------------------------------------
    # Relative strength
    # ------------------------------------------------------------------

    def _relative_strength(
        self,
        data: Mapping[str, Any],
    ) -> tuple[float, float]:
        """
        Relative strength measures whether the primary instrument is
        outperforming or underperforming the related instrument.

        A supplied relative-strength score is preferred.

        Otherwise:
            primary_return - related_return
        is normalized into [-100,100].
        """

        explicit = self._get(
            data,
            "relative_strength_score",
            "relative_strength",
            default=None,
        )

        if explicit is not None:
            signed = self._signed(
                explicit
            )

            if abs(signed) <= 1.0:
                signed *= 100.0

            return (
                abs(signed),
                self._signed(signed),
            )

        primary_return = self._get(
            data,
            "primary_return_pct",
            "primary_change_pct",
            "primary_return",
            default=None,
        )

        related_return = self._get(
            data,
            "related_return_pct",
            "related_change_pct",
            "related_return",
            default=None,
        )

        if primary_return is None or related_return is None:
            return 0.0, 0.0

        try:
            difference = (
                float(primary_return)
                - float(related_return)
            )
        except (TypeError, ValueError):
            return 0.0, 0.0

        if not isfinite(difference):
            return 0.0, 0.0

        # 5 percentage points of relative outperformance is treated
        # as maximum normalized relative strength.
        normalized = self._clamp(
            difference * 20.0,
            -100.0,
            100.0,
        )

        return (
            abs(normalized),
            normalized,
        )

    # ------------------------------------------------------------------
    # Lead / lag
    # ------------------------------------------------------------------

    def _lead_lag(
        self,
        data: Mapping[str, Any],
    ) -> tuple[float, str]:
        """
        Lead/lag strength is represented separately from direction.

        Supported input:
            lead_lag_score
            lead_lag
            lag_score
            lead_symbol

        A positive signed lead/lag score means the related instrument
        leads in the direction represented by the supplied value.
        """

        explicit = self._get(
            data,
            "lead_lag_score",
            "lead_lag_strength",
            "lead_lag",
            default=None,
        )

        lead_symbol = str(
            self._get(
                data,
                "lead_symbol",
                default="",
            )
        )

        primary_symbol = str(
            self._get(
                data,
                "primary_symbol",
                "symbol",
                default="",
            )
        )

        if explicit is not None:
            signed = self._signed(
                explicit
            )

            if abs(signed) <= 1.0:
                signed *= 100.0

            score = abs(signed)

            if lead_symbol:
                return score, lead_symbol

            return score, ""

        lag_score = self._score(
            self._get(
                data,
                "lag_score",
                "lead_score",
                default=0.0,
            )
        )

        if lead_symbol:
            return lag_score, lead_symbol

        return lag_score, primary_symbol

    # ------------------------------------------------------------------
    # Intermarket relationship
    # ------------------------------------------------------------------

    def _intermarket(
        self,
        data: Mapping[str, Any],
    ) -> tuple[float, str]:
        explicit = self._get(
            data,
            "intermarket_score",
            "cross_market_score",
            "intermarket_strength",
            default=None,
        )

        direction = self._normalize_direction(
            self._get(
                data,
                "intermarket_direction",
                "cross_market_direction",
                default="",
            )
        )

        if explicit is not None:
            return (
                self._score(explicit),
                direction,
            )

        confirmations = self._get(
            data,
            "intermarket_confirmations",
            "cross_market_confirmations",
            default=None,
        )

        if isinstance(confirmations, Sequence) and not isinstance(
            confirmations,
            (str, bytes),
        ):
            values: list[float] = []

            for item in confirmations:
                if isinstance(item, Mapping):
                    value = self._get(
                        item,
                        "score",
                        "strength",
                        default=0.0,
                    )
                else:
                    value = item

                values.append(
                    self._score(value)
                )

            if values:
                return (
                    self._clamp(mean(values)),
                    direction,
                )

        return 0.0, direction

    # ------------------------------------------------------------------
    # Confirmation
    # ------------------------------------------------------------------

    def _confirmation(
        self,
        data: Mapping[str, Any],
        correlation_score: float,
        relative_score: float,
        intermarket_score: float,
    ) -> tuple[float, str]:
        explicit = self._get(
            data,
            "confirmation_score",
            "relationship_confirmation",
            default=None,
        )

        direction = self._normalize_direction(
            self._get(
                data,
                "confirmation_direction",
                "relationship_direction",
                default="",
            )
        )

        if explicit is not None:
            return (
                self._score(explicit),
                direction,
            )

        values = [
            value
            for value in (
                correlation_score,
                relative_score,
                intermarket_score,
            )
            if value > 0.0
        ]

        if not values:
            return 0.0, direction

        confirmation = mean(values)

        return (
            self._clamp(confirmation),
            direction,
        )

    # ------------------------------------------------------------------
    # Divergence
    # ------------------------------------------------------------------

    def _divergence(
        self,
        data: Mapping[str, Any],
        *,
        correlation_signed: float,
        relative_signed: float,
        primary_direction: str,
        related_direction: str,
    ) -> float:
        explicit = self._get(
            data,
            "divergence_score",
            "divergence_strength",
            default=None,
        )

        if explicit is not None:
            return self._score(explicit)

        if (
            primary_direction == "NEUTRAL"
            or related_direction == "NEUTRAL"
        ):
            direction_divergence = 0.0
        else:
            direction_divergence = (
                100.0
                if primary_direction
                != related_direction
                else 0.0
            )

        correlation_divergence = 0.0

        # Positive correlation + opposite direction is a divergence.
        if (
            correlation_signed >= 40.0
            and primary_direction != "NEUTRAL"
            and related_direction != "NEUTRAL"
            and primary_direction
            != related_direction
        ):
            correlation_divergence = (
                abs(correlation_signed)
            )

        # Negative correlation + same direction is also divergence
        # relative to the expected inverse relationship.
        if (
            correlation_signed <= -40.0
            and primary_direction != "NEUTRAL"
            and related_direction != "NEUTRAL"
            and primary_direction
            == related_direction
        ):
            correlation_divergence = (
                abs(correlation_signed)
            )

        relative_divergence = 0.0

        if (
            abs(relative_signed) >= 30.0
            and primary_direction != "NEUTRAL"
            and related_direction != "NEUTRAL"
        ):
            expected_sign = (
                1
                if primary_direction == "BUY"
                else -1
            )

            if (
                relative_signed * expected_sign
                < 0
            ):
                relative_divergence = (
                    abs(relative_signed)
                )

        return self._clamp(
            max(
                direction_divergence,
                correlation_divergence,
                relative_divergence,
            )
        )

    # ------------------------------------------------------------------
    # Relationship score
    # ------------------------------------------------------------------

    def calculate_relationship_score(
        self,
        *,
        correlation: float,
        relative_strength: float,
        lead_lag: float,
        intermarket: float,
        confirmation: float,
        divergence: float,
    ) -> float:
        """
        Relationship Intelligence composite:

            RI =
                Correlation       * 0.20
              + Relative Strength* 0.20
              + Lead/Lag         * 0.15
              + Intermarket      * 0.15
              + Confirmation     * 0.15
              + (100-Divergence) * 0.15
        """

        score = (
            self._score(correlation)
            * self.WEIGHTS["correlation"]
            + self._score(relative_strength)
            * self.WEIGHTS["relative_strength"]
            + self._score(lead_lag)
            * self.WEIGHTS["lead_lag"]
            + self._score(intermarket)
            * self.WEIGHTS["intermarket"]
            + self._score(confirmation)
            * self.WEIGHTS["confirmation"]
            + (
                100.0
                - self._score(divergence)
            )
            * self.WEIGHTS["divergence"]
        )

        return self._clamp(score)

    # ------------------------------------------------------------------
    # Directional relationship
    # ------------------------------------------------------------------

    def _relationship_direction(
        self,
        *,
        correlation_signed: float,
        relative_signed: float,
        primary_direction: str,
        related_direction: str,
    ) -> str:
        if (
            primary_direction == "NEUTRAL"
            or related_direction == "NEUTRAL"
        ):
            if relative_signed > 25.0:
                return "BUY"

            if relative_signed < -25.0:
                return "SELL"

            return "NEUTRAL"

        primary_sign = (
            1
            if primary_direction == "BUY"
            else -1
        )

        related_sign = (
            1
            if related_direction == "BUY"
            else -1
        )

        if correlation_signed >= 40.0:
            if primary_sign == related_sign:
                return primary_direction

            return "CONFLICTED"

        if correlation_signed <= -40.0:
            if primary_sign != related_sign:
                return primary_direction

            return "CONFLICTED"

        if relative_signed > 30.0:
            return "BUY"

        if relative_signed < -30.0:
            return "SELL"

        return "NEUTRAL"

    # ------------------------------------------------------------------
    # Contradiction
    # ------------------------------------------------------------------

    def _contradiction(
        self,
        *,
        correlation_signed: float,
        primary_direction: str,
        related_direction: str,
        confirmation_score: float,
        divergence_score: float,
        relationship_direction: str,
    ) -> tuple[bool, tuple[str, ...]]:
        reasons: list[str] = []

        if (
            correlation_signed >= 50.0
            and primary_direction != "NEUTRAL"
            and related_direction != "NEUTRAL"
            and primary_direction
            != related_direction
        ):
            reasons.append(
                "positive_correlation_direction_mismatch"
            )

        if (
            correlation_signed <= -50.0
            and primary_direction != "NEUTRAL"
            and related_direction != "NEUTRAL"
            and primary_direction
            == related_direction
        ):
            reasons.append(
                "inverse_correlation_direction_mismatch"
            )

        if (
            divergence_score >= 70.0
            and confirmation_score >= 60.0
        ):
            reasons.append(
                "confirmation_and_divergence_overlap"
            )

        if relationship_direction == "CONFLICTED":
            reasons.append(
                "relationship_direction_conflicted"
            )

        return (
            bool(reasons),
            tuple(reasons),
        )

    # ------------------------------------------------------------------
    # Stability
    # ------------------------------------------------------------------

    def _stability(
        self,
        current_score: float,
        previous: Optional[RelationshipAssessment],
    ) -> float:
        if previous is None:
            return 50.0

        change = abs(
            current_score
            - previous.relationship_score
        )

        direction_change = (
            previous.relationship_direction
            != ""
        )

        stability = self._clamp(
            100.0
            - change * 2.0
        )

        if direction_change:
            if (
                previous.relationship_direction
                != self._history_direction_placeholder(
                    previous
                )
            ):
                pass

        return self._clamp(stability)

    @staticmethod
    def _history_direction_placeholder(
        record: RelationshipAssessment,
    ) -> str:
        return record.relationship_direction

    # ------------------------------------------------------------------
    # Confidence
    # ------------------------------------------------------------------

    def _confidence(
        self,
        data: Mapping[str, Any],
        *,
        component_scores: Sequence[float],
        stability_score: float,
        contradiction: bool,
    ) -> float:
        nonzero = sum(
            1
            for value in component_scores
            if value > 0.0
        )

        coverage = self._clamp(
            nonzero
            / len(component_scores)
            * 100.0
        )

        data_quality = self._score(
            self._get(
                data,
                "data_quality_score",
                "quality_score",
                default=0.0,
            )
        )

        source_reliability = self._score(
            self._get(
                data,
                "source_reliability_score",
                "source_reliability",
                default=0.0,
            )
        )

        if data_quality == 0.0:
            data_quality = coverage

        if source_reliability == 0.0:
            source_reliability = data_quality

        if component_scores:
            dispersion = (
                max(component_scores)
                - min(component_scores)
            )
        else:
            dispersion = 100.0

        consistency = self._clamp(
            100.0 - dispersion
        )

        confidence = (
            coverage * 0.25
            + data_quality * 0.25
            + source_reliability * 0.20
            + consistency * 0.15
            + stability_score * 0.15
        )

        if contradiction:
            confidence *= 0.70

        return self._clamp(confidence)

    # ------------------------------------------------------------------
    # State classification
    # ------------------------------------------------------------------

    def _classify(
        self,
        *,
        relationship_score: float,
        confidence_score: float,
        divergence_score: float,
        confirmation_score: float,
        contradiction: bool,
    ) -> str:
        if confidence_score < 30.0:
            return "INSUFFICIENT"

        if contradiction:
            return "CONFLICTED"

        if divergence_score >= 80.0:
            return "STRONG_DIVERGENCE"

        if divergence_score >= 60.0:
            return "DIVERGENCE"

        if (
            confirmation_score >= 80.0
            and relationship_score >= 75.0
        ):
            return "STRONG_CONFIRMATION"

        if (
            confirmation_score >= 60.0
            and relationship_score >= 55.0
        ):
            return "CONFIRMATION"

        if (
            confirmation_score >= 40.0
            and relationship_score >= 40.0
        ):
            return "WEAK_CONFIRMATION"

        return "NEUTRAL"

    # ------------------------------------------------------------------
    # Public assessment
    # ------------------------------------------------------------------

    def assess(
        self,
        relationship_data: Mapping[str, Any],
        *,
        primary_symbol: Optional[str] = None,
        related_symbol: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> RelationshipAssessment:
        if not isinstance(
            relationship_data,
            Mapping,
        ):
            raise TypeError(
                "relationship_data must be a mapping"
            )

        resolved_primary = str(
            primary_symbol
            or self._get(
                relationship_data,
                "primary_symbol",
                "symbol",
                default="UNKNOWN",
            )
        )

        resolved_related = str(
            related_symbol
            or self._get(
                relationship_data,
                "related_symbol",
                "reference_symbol",
                "benchmark",
                default="UNKNOWN",
            )
        )

        resolved_timestamp = (
            timestamp
            or self._get(
                relationship_data,
                "timestamp",
                "observed_at",
                default=None,
            )
            or datetime.now(
                timezone.utc
            ).isoformat()
        )

        correlation_score, correlation_signed = (
            self._correlation(
                relationship_data
            )
        )

        relative_score, relative_signed = (
            self._relative_strength(
                relationship_data
            )
        )

        lead_lag_score, lead_symbol = (
            self._lead_lag(
                relationship_data
            )
        )

        intermarket_score, intermarket_direction = (
            self._intermarket(
                relationship_data
            )
        )

        confirmation_score, confirmation_direction = (
            self._confirmation(
                relationship_data,
                correlation_score,
                relative_score,
                intermarket_score,
            )
        )

        primary_direction = self._normalize_direction(
            self._get(
                relationship_data,
                "primary_direction",
                "direction",
                default="",
            )
        )

        related_direction = self._normalize_direction(
            self._get(
                relationship_data,
                "related_direction",
                "reference_direction",
                default="",
            )
        )

        divergence_score = self._divergence(
            relationship_data,
            correlation_signed=correlation_signed,
            relative_signed=relative_signed,
            primary_direction=primary_direction,
            related_direction=related_direction,
        )

        relationship_score = (
            self.calculate_relationship_score(
                correlation=correlation_score,
                relative_strength=relative_score,
                lead_lag=lead_lag_score,
                intermarket=intermarket_score,
                confirmation=confirmation_score,
                divergence=divergence_score,
            )
        )

        relationship_direction = (
            self._relationship_direction(
                correlation_signed=correlation_signed,
                relative_signed=relative_signed,
                primary_direction=primary_direction,
                related_direction=related_direction,
            )
        )

        contradiction, contradiction_reasons = (
            self._contradiction(
                correlation_signed=correlation_signed,
                primary_direction=primary_direction,
                related_direction=related_direction,
                confirmation_score=confirmation_score,
                divergence_score=divergence_score,
                relationship_direction=relationship_direction,
            )
        )

        previous = (
            self._history[-1]
            if self._history
            else None
        )

        stability_score = self._stability(
            relationship_score,
            previous,
        )

        confidence_score = self._confidence(
            relationship_data,
            component_scores=(
                correlation_score,
                relative_score,
                lead_lag_score,
                intermarket_score,
                confirmation_score,
                divergence_score,
            ),
            stability_score=stability_score,
            contradiction=contradiction,
        )

        state = self._classify(
            relationship_score=relationship_score,
            confidence_score=confidence_score,
            divergence_score=divergence_score,
            confirmation_score=confirmation_score,
            contradiction=contradiction,
        )

        observed = dict(
            relationship_data
        )

        derived = {
            "formula": dict(
                self.WEIGHTS
            ),
            "relationship_score": round(
                relationship_score,
                4,
            ),
            "correlation_signed": round(
                correlation_signed,
                4,
            ),
            "relative_strength_signed": round(
                relative_signed,
                4,
            ),
            "lead_symbol": lead_symbol,
            "intermarket_direction": (
                intermarket_direction
            ),
            "confirmation_direction": (
                confirmation_direction
            ),
            "component_scores": {
                "correlation": round(
                    correlation_score,
                    4,
                ),
                "relative_strength": round(
                    relative_score,
                    4,
                ),
                "lead_lag": round(
                    lead_lag_score,
                    4,
                ),
                "intermarket": round(
                    intermarket_score,
                    4,
                ),
                "confirmation": round(
                    confirmation_score,
                    4,
                ),
                "divergence": round(
                    divergence_score,
                    4,
                ),
            },
        }

        evidence = {
            "engine": self.VERSION,
            "primary_symbol": resolved_primary,
            "related_symbol": resolved_related,
            "timestamp": str(
                resolved_timestamp
            ),
            "observed_fields": tuple(
                sorted(
                    observed.keys()
                )
            ),
            "derived_fields": tuple(
                sorted(
                    derived.keys()
                )
            ),
        }

        assessment = RelationshipAssessment(
            timestamp=str(
                resolved_timestamp
            ),
            primary_symbol=resolved_primary,
            related_symbol=resolved_related,
            relationship_score=round(
                relationship_score,
                4,
            ),
            relationship_strength=round(
                relationship_score,
                4,
            ),
            confidence_score=round(
                confidence_score,
                4,
            ),
            stability_score=round(
                stability_score,
                4,
            ),
            correlation_score=round(
                correlation_score,
                4,
            ),
            relative_strength_score=round(
                relative_score,
                4,
            ),
            lead_lag_score=round(
                lead_lag_score,
                4,
            ),
            intermarket_score=round(
                intermarket_score,
                4,
            ),
            confirmation_score=round(
                confirmation_score,
                4,
            ),
            divergence_score=round(
                divergence_score,
                4,
            ),
            primary_direction=primary_direction,
            related_direction=related_direction,
            relationship_direction=relationship_direction,
            state=state,
            contradiction=contradiction,
            contradiction_reasons=(
                contradiction_reasons
            ),
            observed=observed,
            derived=derived,
            evidence=evidence,
        )

        self._history.append(
            assessment
        )

        if len(self._history) > self.history_limit:
            del self._history[
                :len(self._history)
                - self.history_limit
            ]

        return assessment

    # ------------------------------------------------------------------
    # History / memory
    # ------------------------------------------------------------------

    def latest(
        self,
    ) -> Optional[RelationshipAssessment]:
        return (
            self._history[-1]
            if self._history
            else None
        )

    def history(
        self,
        limit: Optional[int] = None,
    ) -> tuple[RelationshipAssessment, ...]:
        if limit is None:
            return tuple(
                self._history
            )

        if limit < 1:
            return ()

        return tuple(
            self._history[-limit:]
        )

    def average_score(
        self,
        limit: Optional[int] = None,
    ) -> float:
        records = self.history(
            limit
        )

        if not records:
            return 0.0

        return round(
            mean(
                record.relationship_score
                for record in records
            ),
            4,
        )

    def detect_transition(
        self,
    ) -> dict[str, Any]:
        if len(self._history) < 2:
            latest = self.latest()

            return {
                "transition": False,
                "from_state": None,
                "to_state": (
                    latest.state
                    if latest
                    else None
                ),
                "score_change": 0.0,
            }

        previous = self._history[-2]
        current = self._history[-1]

        return {
            "transition": (
                previous.state
                != current.state
            ),
            "from_state": previous.state,
            "to_state": current.state,
            "score_change": round(
                current.relationship_score
                - previous.relationship_score,
                4,
            ),
            "direction_change": (
                previous.relationship_direction
                != current.relationship_direction
            ),
        }

    def clear_history(self) -> None:
        self._history.clear()

    def health_check(self) -> dict[str, Any]:
        weight_sum = sum(
            self.WEIGHTS.values()
        )

        return {
            "engine": self.VERSION,
            "healthy": (
                abs(
                    weight_sum - 1.0
                )
                < 1e-9
            ),
            "weight_sum": round(
                weight_sum,
                10,
            ),
            "history_size": len(
                self._history
            ),
            "history_limit": (
                self.history_limit
            ),
            "latest_available": (
                self.latest()
                is not None
            ),
        }


# Integration aliases.
RelationshipEngine = RelationshipIntelligence
MarketRelationshipIntelligence = RelationshipIntelligence


__all__ = [
    "RelationshipAssessment",
    "RelationshipIntelligence",
    "RelationshipEngine",
    "MarketRelationshipIntelligence",
]