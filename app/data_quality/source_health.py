"""
ROBOMLM PLUS
Data Quality - Source Health

Purpose:
    Evaluate the operational health of a market-data source from
    already-available health observations.

Design:
    - Detection/evaluation only.
    - No external calls.
    - No connection management.
    - No data mutation.
    - No trading or execution side effects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Optional


class SourceHealthCheckError(Exception):
    """Base exception for source-health failures."""


@dataclass(frozen=True)
class SourceHealthResult:
    """Result of a source-health evaluation."""

    healthy: bool
    score: float
    state: str
    source: Optional[str]
    checks_total: int
    checks_passed: int
    checks_failed: int
    issues: tuple[str, ...] = ()
    message: str = ""
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def health_score(self) -> float:
        """Alias for score."""

        return self.score

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable representation."""

        return {
            "healthy": self.healthy,
            "score": self.score,
            "health_score": self.health_score,
            "state": self.state,
            "source": self.source,
            "checks_total": self.checks_total,
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed,
            "issues": list(self.issues),
            "message": self.message,
            "metadata": dict(self.metadata),
        }


class SourceHealthChecker:
    """
    Evaluate the health of a market-data source.

    The checker can evaluate:
        - source availability
        - source enabled state
        - connection state
        - authentication state
        - error state
        - stale state
        - repeated failure counts
        - latency
        - optional custom health score

    It never attempts to repair or reconnect a source.
    """

    STATE_HEALTHY = "HEALTHY"
    STATE_DEGRADED = "DEGRADED"
    STATE_UNHEALTHY = "UNHEALTHY"
    STATE_UNKNOWN = "UNKNOWN"

    DEFAULT_MIN_SCORE = 80.0
    DEFAULT_MAX_FAILURES = 3
    DEFAULT_MAX_LATENCY_MS = 1000.0

    def __init__(
        self,
        min_score: float = DEFAULT_MIN_SCORE,
        max_failures: int = DEFAULT_MAX_FAILURES,
        max_latency_ms: float = DEFAULT_MAX_LATENCY_MS,
    ) -> None:
        self.min_score = float(min_score)
        self.max_failures = int(max_failures)
        self.max_latency_ms = float(max_latency_ms)

        if not (
            0.0
            <= self.min_score
            <= 100.0
        ):
            raise SourceHealthCheckError(
                "min_score must be between 0 and 100."
            )

        if self.max_failures < 0:
            raise SourceHealthCheckError(
                "max_failures cannot be negative."
            )

        if self.max_latency_ms <= 0:
            raise SourceHealthCheckError(
                "max_latency_ms must be greater than zero."
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

        raise SourceHealthCheckError(
            "Data must be a dictionary or expose "
            "to_dict()/__dict__."
        )

    @staticmethod
    def _finite_number(
        value: Any,
    ) -> Optional[float]:
        """Return a finite float or None."""

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

    @staticmethod
    def _optional_bool(
        data: dict[str, Any],
        names: Iterable[str],
    ) -> Optional[bool]:
        """Return the first available boolean field."""

        for name in names:
            if name not in data:
                continue

            value = data[name]

            if value is None:
                continue

            if isinstance(value, bool):
                return value

            if isinstance(value, str):
                normalized = value.strip().lower()

                if normalized in {
                    "true",
                    "yes",
                    "1",
                    "up",
                    "online",
                    "connected",
                    "healthy",
                    "active",
                    "available",
                    "ok",
                }:
                    return True

                if normalized in {
                    "false",
                    "no",
                    "0",
                    "down",
                    "offline",
                    "disconnected",
                    "unhealthy",
                    "inactive",
                    "unavailable",
                    "error",
                    "failed",
                }:
                    return False

        return None

    @staticmethod
    def _optional_text(
        data: dict[str, Any],
        names: Iterable[str],
    ) -> Optional[str]:
        """Return the first usable text field."""

        for name in names:
            if name not in data:
                continue

            value = data[name]

            if value is None:
                continue

            text = str(value).strip()

            if text:
                return text

        return None

    def _add_check(
        self,
        issues: list[str],
        *,
        condition: Optional[bool],
        message: str,
        counters: list[int],
    ) -> None:
        """
        Record a health check.

        counters:
            [total, passed, failed]
        """

        if condition is None:
            return

        counters[0] += 1

        if condition:
            counters[1] += 1
        else:
            counters[2] += 1
            issues.append(message)

    def _score_from_counters(
        self,
        counters: list[int],
    ) -> float:
        """Calculate score from completed checks."""

        total = counters[0]

        if total == 0:
            return 0.0

        return (
            counters[1]
            / total
            * 100.0
        )

    def _state(
        self,
        score: float,
        failed: int,
    ) -> str:
        """Determine source-health state."""

        if failed == 0 and score >= 95.0:
            return self.STATE_HEALTHY

        if score >= self.min_score:
            return self.STATE_DEGRADED

        return self.STATE_UNHEALTHY

    def check(
        self,
        data: Any = None,
        *,
        source: Optional[str] = None,
        available: Optional[bool] = None,
        enabled: Optional[bool] = None,
        connected: Optional[bool] = None,
        authenticated: Optional[bool] = None,
        healthy: Optional[bool] = None,
        stale: Optional[bool] = None,
        error: Optional[bool] = None,
        failure_count: Optional[int] = None,
        latency_ms: Optional[float] = None,
        health_score: Optional[float] = None,
        strict: bool = False,
    ) -> SourceHealthResult:
        """
        Evaluate source health.

        Explicit keyword arguments take precedence over values found
        in the supplied data object.
        """

        mapping: dict[str, Any] = {}

        if data is not None:
            mapping = self._to_mapping(data)

        resolved_source = source

        if resolved_source is None:
            resolved_source = self._optional_text(
                mapping,
                (
                    "source",
                    "source_name",
                    "provider",
                    "adapter",
                    "data_source",
                ),
            )

        if available is None:
            available = self._optional_bool(
                mapping,
                (
                    "available",
                    "is_available",
                ),
            )

        if enabled is None:
            enabled = self._optional_bool(
                mapping,
                (
                    "enabled",
                    "is_enabled",
                ),
            )

        if connected is None:
            connected = self._optional_bool(
                mapping,
                (
                    "connected",
                    "is_connected",
                    "connection_healthy",
                ),
            )

        if authenticated is None:
            authenticated = self._optional_bool(
                mapping,
                (
                    "authenticated",
                    "is_authenticated",
                    "auth_healthy",
                ),
            )

        if healthy is None:
            healthy = self._optional_bool(
                mapping,
                (
                    "healthy",
                    "is_healthy",
                ),
            )

        if stale is None:
            stale = self._optional_bool(
                mapping,
                (
                    "stale",
                    "is_stale",
                ),
            )

        if error is None:
            error = self._optional_bool(
                mapping,
                (
                    "error",
                    "has_error",
                    "error_state",
                ),
            )

        if failure_count is None:
            raw_failure_count = mapping.get(
                "failure_count",
                mapping.get(
                    "failures"
                ),
            )

            if raw_failure_count is not None:
                try:
                    failure_count = int(
                        raw_failure_count
                    )
                except (
                    TypeError,
                    ValueError,
                ):
                    failure_count = None

        if latency_ms is None:
            raw_latency = mapping.get(
                "latency_ms"
            )

            if raw_latency is not None:
                latency_ms = (
                    self._finite_number(
                        raw_latency
                    )
                )

        if health_score is None:
            raw_health_score = mapping.get(
                "health_score",
                mapping.get(
                    "score"
                ),
            )

            if raw_health_score is not None:
                health_score = (
                    self._finite_number(
                        raw_health_score
                    )
                )

        issues: list[str] = []
        counters = [0, 0, 0]

        self._add_check(
            issues,
            condition=available,
            message="Source is unavailable.",
            counters=counters,
        )

        self._add_check(
            issues,
            condition=enabled,
            message="Source is disabled.",
            counters=counters,
        )

        self._add_check(
            issues,
            condition=connected,
            message="Source connection is not healthy.",
            counters=counters,
        )

        self._add_check(
            issues,
            condition=authenticated,
            message="Source authentication is not healthy.",
            counters=counters,
        )

        self._add_check(
            issues,
            condition=healthy,
            message="Source reported an unhealthy state.",
            counters=counters,
        )

        if stale is not None:
            self._add_check(
                issues,
                condition=not stale,
                message="Source data is marked stale.",
                counters=counters,
            )

        if error is not None:
            self._add_check(
                issues,
                condition=not error,
                message="Source reported an error.",
                counters=counters,
            )

        if failure_count is not None:
            if failure_count < 0:
                issues.append(
                    "Failure count cannot be negative."
                )
            else:
                self._add_check(
                    issues,
                    condition=(
                        failure_count
                        <= self.max_failures
                    ),
                    message=(
                        "Source failure count exceeds "
                        "the configured limit."
                    ),
                    counters=counters,
                )

        if latency_ms is not None:
            if latency_ms < 0:
                issues.append(
                    "Latency cannot be negative."
                )
            else:
                self._add_check(
                    issues,
                    condition=(
                        latency_ms
                        <= self.max_latency_ms
                    ),
                    message=(
                        "Source latency exceeds "
                        "the configured limit."
                    ),
                    counters=counters,
                )

        calculated_score = (
            self._score_from_counters(
                counters
            )
        )

        if health_score is not None:
            if not (
                0.0
                <= health_score
                <= 100.0
            ):
                issues.append(
                    "Health score must be between 0 and 100."
                )
            else:
                calculated_score = float(
                    health_score
                )

        if (
            counters[0] == 0
            and health_score is None
        ):
            state = self.STATE_UNKNOWN
            healthy_result = False
            message = (
                "Insufficient source-health information."
            )

        else:
            state = self._state(
                calculated_score,
                len(issues),
            )

            explicit_failure = any(
                issue
                in {
                    "Source is unavailable.",
                    "Source is disabled.",
                    "Source connection is not healthy.",
                    "Source authentication is not healthy.",
                    "Source reported an unhealthy state.",
                    "Source data is marked stale.",
                    "Source reported an error.",
                }
                for issue in issues
            )

            if strict:
                healthy_result = (
                    len(issues) == 0
                    and calculated_score >= self.min_score
                )
            else:
                healthy_result = (
                    not explicit_failure
                    and calculated_score >= self.min_score
                )

            if healthy_result:
                message = (
                    "Source health is within the "
                    "configured quality threshold."
                )
            elif state == self.STATE_DEGRADED:
                message = (
                    "Source is operational but "
                    "health is degraded."
                )
            else:
                message = (
                    "Source health is below the "
                    "configured quality threshold."
                )

        return SourceHealthResult(
            healthy=healthy_result,
            score=round(
                max(
                    0.0,
                    min(
                        100.0,
                        calculated_score,
                    ),
                ),
                4,
            ),
            state=state,
            source=resolved_source,
            checks_total=counters[0],
            checks_passed=counters[1],
            checks_failed=counters[2],
            issues=tuple(issues),
            message=message,
            metadata={
                "checker": self.__class__.__name__,
                "min_score": self.min_score,
                "max_failures": self.max_failures,
                "max_latency_ms": self.max_latency_ms,
                "strict": strict,
            },
        )

    def is_healthy(
        self,
        data: Any = None,
        **kwargs: Any,
    ) -> bool:
        """Return whether the source passes the health gate."""

        return self.check(
            data,
            **kwargs,
        ).healthy

    def score(
        self,
        data: Any = None,
        **kwargs: Any,
    ) -> float:
        """Return the source-health score."""

        return self.check(
            data,
            **kwargs,
        ).score

    def issues(
        self,
        data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, ...]:
        """Return detected source-health issues."""

        return self.check(
            data,
            **kwargs,
        ).issues


source_health_checker = SourceHealthChecker()


def check_source_health(
    data: Any = None,
    **kwargs: Any,
) -> SourceHealthResult:
    """Convenience function for source-health checking."""

    return source_health_checker.check(
        data,
        **kwargs,
    )


__all__ = [
    "SourceHealthCheckError",
    "SourceHealthResult",
    "SourceHealthChecker",
    "source_health_checker",
    "check_source_health",
]