"""
ROBOMLM PLUS
Data Quality - Latency Check

Purpose:
    Measure and classify data-delivery latency.

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


class LatencyCheckError(Exception):
    """Base exception for latency-check failures."""


@dataclass(frozen=True)
class LatencyResult:
    """Result of a latency evaluation."""

    valid: bool
    passed: bool
    latency_ms: Optional[float]
    score: float
    threshold_ms: float
    state: str
    message: str
    measured_at: Optional[datetime] = None
    source_timestamp: Optional[datetime] = None
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def latency_score(self) -> float:
        """Alias for score."""

        return self.score

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable representation."""

        return {
            "valid": self.valid,
            "passed": self.passed,
            "latency_ms": self.latency_ms,
            "score": self.score,
            "latency_score": self.latency_score,
            "threshold_ms": self.threshold_ms,
            "state": self.state,
            "message": self.message,
            "measured_at": (
                self.measured_at.isoformat()
                if self.measured_at is not None
                else None
            ),
            "source_timestamp": (
                self.source_timestamp.isoformat()
                if self.source_timestamp is not None
                else None
            ),
            "metadata": dict(self.metadata),
        }


class LatencyChecker:
    """
    Evaluate delivery latency.

    Latency may be supplied directly in milliseconds or calculated
    from a source timestamp and measurement timestamp.

    Score:
        latency <= threshold:
            100

        latency > threshold:
            score decays linearly until zero at the configured
            maximum-latency multiplier.
    """

    STATE_EXCELLENT = "EXCELLENT"
    STATE_ACCEPTABLE = "ACCEPTABLE"
    STATE_HIGH = "HIGH"
    STATE_CRITICAL = "CRITICAL"
    STATE_UNKNOWN = "UNKNOWN"
    STATE_INVALID = "INVALID"

    DEFAULT_THRESHOLD_MS = 500.0
    DEFAULT_MIN_SCORE = 80.0
    DEFAULT_CRITICAL_MULTIPLIER = 5.0

    def __init__(
        self,
        threshold_ms: float = DEFAULT_THRESHOLD_MS,
        min_score: float = DEFAULT_MIN_SCORE,
        critical_multiplier: float = (
            DEFAULT_CRITICAL_MULTIPLIER
        ),
    ) -> None:
        self.threshold_ms = float(
            threshold_ms
        )
        self.min_score = float(
            min_score
        )
        self.critical_multiplier = float(
            critical_multiplier
        )

        if self.threshold_ms <= 0:
            raise LatencyCheckError(
                "threshold_ms must be greater than zero."
            )

        if not (
            0.0
            <= self.min_score
            <= 100.0
        ):
            raise LatencyCheckError(
                "min_score must be between 0 and 100."
            )

        if self.critical_multiplier <= 1.0:
            raise LatencyCheckError(
                "critical_multiplier must be greater than 1."
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

        raise LatencyCheckError(
            "Data must be a dictionary or expose "
            "to_dict()/__dict__."
        )

    @staticmethod
    def _parse_datetime(
        value: Any,
    ) -> datetime:
        """Parse a supported datetime value."""

        if isinstance(value, datetime):
            result = value

        elif isinstance(value, str):
            text = value.strip()

            if not text:
                raise LatencyCheckError(
                    "Timestamp cannot be empty."
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
                raise LatencyCheckError(
                    "Timestamp must be a valid "
                    "ISO-8601 datetime."
                ) from exc

        else:
            raise LatencyCheckError(
                "Timestamp must be a datetime "
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
    def _finite_number(
        value: Any,
    ) -> Optional[float]:
        """Convert a value to a finite float when possible."""

        if isinstance(value, bool):
            return None

        try:
            number = float(value)
        except (
            TypeError,
            ValueError,
        ):
            return None

        if number != number:
            return None

        if abs(number) == float("inf"):
            return None

        return number

    def _calculate_score(
        self,
        latency_ms: float,
        threshold_ms: float,
    ) -> float:
        """Calculate bounded latency score."""

        if latency_ms <= threshold_ms:
            return 100.0

        maximum_latency = (
            threshold_ms
            * self.critical_multiplier
        )

        if latency_ms >= maximum_latency:
            return 0.0

        excess = (
            latency_ms
            - threshold_ms
        )

        available_range = (
            maximum_latency
            - threshold_ms
        )

        score = 100.0 - (
            excess
            / available_range
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
        latency_ms: float,
        threshold_ms: float,
        score: float,
    ) -> str:
        """Determine latency state."""

        if latency_ms <= threshold_ms:
            if score >= 95.0:
                return self.STATE_EXCELLENT

            return self.STATE_ACCEPTABLE

        if score >= self.min_score:
            return self.STATE_ACCEPTABLE

        if latency_ms < (
            threshold_ms
            * self.critical_multiplier
        ):
            return self.STATE_HIGH

        return self.STATE_CRITICAL

    def check(
        self,
        data: Any = None,
        *,
        latency_ms: Optional[float] = None,
        source_timestamp: Any = None,
        measured_at: Any = None,
        latency_field: str = "latency_ms",
        source_timestamp_field: str = "observed_at",
        measured_at_field: str = "received_at",
        threshold_ms: Optional[float] = None,
    ) -> LatencyResult:
        """
        Evaluate latency.

        Priority:
            1. Explicit latency_ms argument.
            2. latency field from data.
            3. source_timestamp -> measured_at difference.

        If no usable latency information exists, the result is
        UNKNOWN rather than silently assuming zero latency.
        """

        mapping: dict[str, Any] = {}

        if data is not None:
            mapping = self._to_mapping(data)

        threshold = (
            self.threshold_ms
            if threshold_ms is None
            else float(threshold_ms)
        )

        if threshold <= 0:
            raise LatencyCheckError(
                "threshold_ms must be greater than zero."
            )

        resolved_latency = latency_ms

        if resolved_latency is None:
            resolved_latency = mapping.get(
                latency_field
            )

        numeric_latency = self._finite_number(
            resolved_latency
        )

        resolved_source_timestamp = (
            source_timestamp
        )

        if resolved_source_timestamp is None:
            resolved_source_timestamp = mapping.get(
                source_timestamp_field
            )

        resolved_measured_at = measured_at

        if resolved_measured_at is None:
            resolved_measured_at = mapping.get(
                measured_at_field
            )

        parsed_source_timestamp: Optional[
            datetime
        ] = None

        parsed_measured_at: Optional[
            datetime
        ] = None

        if (
            numeric_latency is None
            and resolved_source_timestamp is not None
            and resolved_measured_at is not None
        ):
            parsed_source_timestamp = (
                self._parse_datetime(
                    resolved_source_timestamp
                )
            )

            parsed_measured_at = (
                self._parse_datetime(
                    resolved_measured_at
                )
            )

            calculated_latency = (
                parsed_measured_at
                - parsed_source_timestamp
            ).total_seconds() * 1000.0

            numeric_latency = calculated_latency

        elif resolved_source_timestamp is not None:
            parsed_source_timestamp = (
                self._parse_datetime(
                    resolved_source_timestamp
                )
            )

        elif resolved_measured_at is not None:
            parsed_measured_at = (
                self._parse_datetime(
                    resolved_measured_at
                )
            )

        if numeric_latency is None:
            return LatencyResult(
                valid=False,
                passed=False,
                latency_ms=None,
                score=0.0,
                threshold_ms=threshold,
                state=self.STATE_UNKNOWN,
                message=(
                    "No usable latency measurement "
                    "was supplied."
                ),
                measured_at=parsed_measured_at,
                source_timestamp=(
                    parsed_source_timestamp
                ),
                metadata={
                    "checker": self.__class__.__name__,
                    "reason": "missing_latency",
                },
            )

        if numeric_latency < 0:
            return LatencyResult(
                valid=False,
                passed=False,
                latency_ms=numeric_latency,
                score=0.0,
                threshold_ms=threshold,
                state=self.STATE_INVALID,
                message=(
                    "Latency cannot be negative."
                ),
                measured_at=parsed_measured_at,
                source_timestamp=(
                    parsed_source_timestamp
                ),
                metadata={
                    "checker": self.__class__.__name__,
                    "reason": "negative_latency",
                },
            )

        score = self._calculate_score(
            numeric_latency,
            threshold,
        )

        state = self._state(
            numeric_latency,
            threshold,
            score,
        )

        passed = (
            numeric_latency <= threshold
            and score >= self.min_score
        )

        if passed:
            message = (
                "Latency is within the configured "
                "quality threshold."
            )
        elif state == self.STATE_HIGH:
            message = (
                "Latency is above the configured "
                "quality threshold."
            )
        else:
            message = (
                "Latency is critically high."
            )

        return LatencyResult(
            valid=True,
            passed=passed,
            latency_ms=round(
                numeric_latency,
                6,
            ),
            score=round(
                score,
                4,
            ),
            threshold_ms=threshold,
            state=state,
            message=message,
            measured_at=parsed_measured_at,
            source_timestamp=(
                parsed_source_timestamp
            ),
            metadata={
                "checker": self.__class__.__name__,
                "min_score": self.min_score,
                "critical_multiplier": (
                    self.critical_multiplier
                ),
                "latency_source": (
                    "explicit"
                    if latency_ms is not None
                    else (
                        "field"
                        if mapping.get(
                            latency_field
                        )
                        is not None
                        else "timestamps"
                    )
                ),
            },
        )

    def is_valid(
        self,
        data: Any = None,
        **kwargs: Any,
    ) -> bool:
        """Return whether the latency measurement is valid."""

        return self.check(
            data,
            **kwargs,
        ).valid

    def is_acceptable(
        self,
        data: Any = None,
        **kwargs: Any,
    ) -> bool:
        """Return whether latency passes the quality gate."""

        return self.check(
            data,
            **kwargs,
        ).passed

    def score(
        self,
        data: Any = None,
        **kwargs: Any,
    ) -> float:
        """Return the latency score."""

        return self.check(
            data,
            **kwargs,
        ).score


latency_checker = LatencyChecker()


def check_latency(
    data: Any = None,
    **kwargs: Any,
) -> LatencyResult:
    """Convenience function for latency checking."""

    return latency_checker.check(
        data,
        **kwargs,
    )


__all__ = [
    "LatencyCheckError",
    "LatencyResult",
    "LatencyChecker",
    "latency_checker",
    "check_latency",
]