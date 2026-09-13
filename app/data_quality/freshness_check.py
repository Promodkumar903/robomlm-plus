"""
ROBOMLM PLUS
Data Quality - Freshness Check

Purpose:
    Measure how recent an observation is relative to a reference time.

Design:
    - Detection/evaluation only.
    - No data mutation.
    - No external calls.
    - No trading or execution side effects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


class FreshnessCheckError(Exception):
    """Base exception for freshness-check failures."""


@dataclass(frozen=True)
class FreshnessResult:
    """Result of a freshness evaluation."""

    fresh: bool
    score: float
    age_seconds: Optional[float]
    threshold_seconds: float
    observed_at: Optional[datetime]
    reference_time: datetime
    state: str
    message: str
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def freshness_score(self) -> float:
        """Alias for score."""

        return self.score

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable representation."""

        return {
            "fresh": self.fresh,
            "score": self.score,
            "freshness_score": self.freshness_score,
            "age_seconds": self.age_seconds,
            "threshold_seconds": self.threshold_seconds,
            "observed_at": (
                self.observed_at.isoformat()
                if self.observed_at is not None
                else None
            ),
            "reference_time": self.reference_time.isoformat(),
            "state": self.state,
            "message": self.message,
            "metadata": dict(self.metadata),
        }


class FreshnessChecker:
    """
    Evaluate whether market observations are sufficiently recent.

    Freshness score:
        age <= threshold:
            100

        age > threshold:
            score decreases linearly toward 0.

    A configurable minimum score can be used as the freshness gate.
    """

    STATE_FRESH = "FRESH"
    STATE_AGING = "AGING"
    STATE_STALE = "STALE"
    STATE_UNKNOWN = "UNKNOWN"
    STATE_INVALID = "INVALID"

    DEFAULT_THRESHOLD_SECONDS = 5.0
    DEFAULT_MIN_SCORE = 80.0

    def __init__(
        self,
        threshold_seconds: float = DEFAULT_THRESHOLD_SECONDS,
        min_score: float = DEFAULT_MIN_SCORE,
        aging_multiplier: float = 2.0,
    ) -> None:
        self.threshold_seconds = float(
            threshold_seconds
        )
        self.min_score = float(min_score)
        self.aging_multiplier = float(
            aging_multiplier
        )

        if self.threshold_seconds <= 0:
            raise FreshnessCheckError(
                "threshold_seconds must be greater than zero."
            )

        if not (
            0.0
            <= self.min_score
            <= 100.0
        ):
            raise FreshnessCheckError(
                "min_score must be between 0 and 100."
            )

        if self.aging_multiplier <= 1.0:
            raise FreshnessCheckError(
                "aging_multiplier must be greater than 1."
            )

    @staticmethod
    def _to_mapping(
        data: Any,
    ) -> dict[str, Any]:
        """Convert supported objects to a dictionary."""

        if isinstance(data, dict):
            return dict(data)

        if hasattr(data, "to_dict"):
            result = data.to_dict()

            if isinstance(result, dict):
                return dict(result)

        if hasattr(data, "__dict__"):
            return dict(vars(data))

        raise FreshnessCheckError(
            "Data must be a dictionary or expose "
            "to_dict()/__dict__."
        )

    @staticmethod
    def _parse_datetime(
        value: Any,
    ) -> datetime:
        """Parse supported datetime representations."""

        if isinstance(value, datetime):
            result = value
        elif isinstance(value, str):
            text = value.strip()

            if not text:
                raise FreshnessCheckError(
                    "observed_at cannot be empty."
                )

            if text.endswith("Z"):
                text = (
                    text[:-1]
                    + "+00:00"
                )

            try:
                result = datetime.fromisoformat(
                    text
                )
            except ValueError as exc:
                raise FreshnessCheckError(
                    "observed_at must be a valid "
                    "ISO-8601 datetime."
                ) from exc
        else:
            raise FreshnessCheckError(
                "observed_at must be a datetime "
                "or ISO-8601 string."
            )

        if result.tzinfo is None:
            result = result.replace(
                tzinfo=timezone.utc
            )

        return result.astimezone(
            timezone.utc
        )

    @staticmethod
    def _reference_time(
        value: Optional[datetime],
    ) -> datetime:
        """Normalize the reference time to UTC."""

        if value is None:
            return datetime.now(
                timezone.utc
            )

        if not isinstance(
            value,
            datetime,
        ):
            raise FreshnessCheckError(
                "reference_time must be a datetime."
            )

        if value.tzinfo is None:
            value = value.replace(
                tzinfo=timezone.utc
            )

        return value.astimezone(
            timezone.utc
        )

    def _score(
        self,
        age_seconds: float,
    ) -> float:
        """Calculate a bounded freshness score."""

        if age_seconds <= self.threshold_seconds:
            return 100.0

        excess = (
            age_seconds
            - self.threshold_seconds
        )

        decay_range = (
            self.threshold_seconds
            * (
                self.aging_multiplier
                - 1.0
            )
        )

        score = 100.0 - (
            excess
            / decay_range
            * 100.0
        )

        return max(
            0.0,
            min(
                100.0,
                score,
            ),
        )

    def _state(
        self,
        age_seconds: float,
        score: float,
    ) -> str:
        """Determine freshness state."""

        if age_seconds <= self.threshold_seconds:
            return self.STATE_FRESH

        if (
            age_seconds
            <= self.threshold_seconds
            * self.aging_multiplier
            and score >= self.min_score
        ):
            return self.STATE_AGING

        return self.STATE_STALE

    def check(
        self,
        data: Any,
        *,
        reference_time: Optional[datetime] = None,
        observed_at_field: str = "observed_at",
        threshold_seconds: Optional[float] = None,
    ) -> FreshnessResult:
        """
        Evaluate freshness of an observation.

        The observation timestamp is read from the supplied data.
        """

        mapping = self._to_mapping(data)

        if observed_at_field not in mapping:
            reference = self._reference_time(
                reference_time
            )

            return FreshnessResult(
                fresh=False,
                score=0.0,
                age_seconds=None,
                threshold_seconds=(
                    self.threshold_seconds
                    if threshold_seconds is None
                    else float(threshold_seconds)
                ),
                observed_at=None,
                reference_time=reference,
                state=self.STATE_UNKNOWN,
                message=(
                    f"Missing required field: "
                    f"{observed_at_field}"
                ),
                metadata={
                    "checker": self.__class__.__name__,
                    "reason": "missing_timestamp",
                },
            )

        raw_observed_at = mapping.get(
            observed_at_field
        )

        if raw_observed_at is None:
            reference = self._reference_time(
                reference_time
            )

            return FreshnessResult(
                fresh=False,
                score=0.0,
                age_seconds=None,
                threshold_seconds=(
                    self.threshold_seconds
                    if threshold_seconds is None
                    else float(threshold_seconds)
                ),
                observed_at=None,
                reference_time=reference,
                state=self.STATE_UNKNOWN,
                message=(
                    f"{observed_at_field} is None."
                ),
                metadata={
                    "checker": self.__class__.__name__,
                    "reason": "null_timestamp",
                },
            )

        observed_at = self._parse_datetime(
            raw_observed_at
        )

        reference = self._reference_time(
            reference_time
        )

        threshold = (
            self.threshold_seconds
            if threshold_seconds is None
            else float(threshold_seconds)
        )

        if threshold <= 0:
            raise FreshnessCheckError(
                "threshold_seconds must be greater than zero."
            )

        age_seconds = (
            reference - observed_at
        ).total_seconds()

        if age_seconds < 0:
            return FreshnessResult(
                fresh=False,
                score=0.0,
                age_seconds=age_seconds,
                threshold_seconds=threshold,
                observed_at=observed_at,
                reference_time=reference,
                state=self.STATE_INVALID,
                message=(
                    "Observation timestamp is in "
                    "the future relative to reference time."
                ),
                metadata={
                    "checker": self.__class__.__name__,
                    "reason": "future_timestamp",
                },
            )

        score = self._score(
            age_seconds
        )

        state = self._state(
            age_seconds,
            score,
        )

        fresh = (
            age_seconds <= threshold
            and score >= self.min_score
        )

        if fresh:
            message = (
                "Observation is fresh."
            )
        elif state == self.STATE_AGING:
            message = (
                "Observation is aging but "
                "remains within the configured "
                "quality tolerance."
            )
        else:
            message = (
                "Observation is stale."
            )

        return FreshnessResult(
            fresh=fresh,
            score=round(
                score,
                4,
            ),
            age_seconds=round(
                age_seconds,
                6,
            ),
            threshold_seconds=threshold,
            observed_at=observed_at,
            reference_time=reference,
            state=state,
            message=message,
            metadata={
                "checker": self.__class__.__name__,
                "min_score": self.min_score,
                "aging_multiplier": (
                    self.aging_multiplier
                ),
                "observed_at_field": (
                    observed_at_field
                ),
            },
        )

    def is_fresh(
        self,
        data: Any,
        **kwargs: Any,
    ) -> bool:
        """Return whether the observation passes freshness."""

        return self.check(
            data,
            **kwargs,
        ).fresh

    def score(
        self,
        data: Any,
        **kwargs: Any,
    ) -> float:
        """Return the freshness score."""

        return self.check(
            data,
            **kwargs,
        ).score

    def age_seconds(
        self,
        data: Any,
        **kwargs: Any,
    ) -> Optional[float]:
        """Return observation age in seconds."""

        return self.check(
            data,
            **kwargs,
        ).age_seconds


freshness_checker = FreshnessChecker()


def check_freshness(
    data: Any,
    **kwargs: Any,
) -> FreshnessResult:
    """Convenience function for freshness checking."""

    return freshness_checker.check(
        data,
        **kwargs,
    )


__all__ = [
    "FreshnessCheckError",
    "FreshnessResult",
    "FreshnessChecker",
    "freshness_checker",
    "check_freshness",
]