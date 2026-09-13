"""
ROBOMLM PLUS
Data Quality Engine

Purpose:
    Unified orchestration layer for market-data quality validation.

Checks:
    - Completeness
    - Consistency
    - Freshness
    - Latency
    - Source health

Design:
    - Detection and evaluation only.
    - No data mutation.
    - No market/exchange calls.
    - No trading or execution side effects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .completeness_check import (
    CompletenessChecker,
    CompletenessResult,
    completeness_checker,
)
from .consistency_check import (
    ConsistencyChecker,
    ConsistencyResult,
    consistency_checker,
)


class DataQualityEngineError(Exception):
    """Base exception for data-quality engine failures."""


@dataclass(frozen=True)
class DataQualityResult:
    """Combined result produced by the data-quality engine."""

    quality_score: float
    quality_state: str
    passed: bool
    completeness: Optional[CompletenessResult] = None
    consistency: Optional[ConsistencyResult] = None
    freshness: Any = None
    latency: Any = None
    source_health: Any = None
    issues: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def complete(self) -> bool:
        """Return completeness status."""

        if self.completeness is None:
            return True

        return self.completeness.complete

    @property
    def consistent(self) -> bool:
        """Return consistency status."""

        if self.consistency is None:
            return True

        return self.consistency.consistent

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable representation."""

        def serialize(value: Any) -> Any:
            if value is None:
                return None

            if hasattr(value, "to_dict"):
                return value.to_dict()

            if isinstance(value, dict):
                return dict(value)

            return value

        return {
            "quality_score": self.quality_score,
            "quality_state": self.quality_state,
            "passed": self.passed,
            "completeness": serialize(self.completeness),
            "consistency": serialize(self.consistency),
            "freshness": serialize(self.freshness),
            "latency": serialize(self.latency),
            "source_health": serialize(self.source_health),
            "issues": list(self.issues),
            "metadata": dict(self.metadata),
        }


class DataQualityEngine:
    """
    Unified data-quality orchestration engine.

    The engine accepts already-available data-quality results for
    checks whose dedicated modules are implemented separately.

    This keeps the engine decoupled from external data providers and
    prevents accidental network or execution side effects.
    """

    QUALITY_PASS_THRESHOLD = 80.0
    QUALITY_WARNING_THRESHOLD = 60.0

    STATE_EXCELLENT = "EXCELLENT"
    STATE_GOOD = "GOOD"
    STATE_WARNING = "WARNING"
    STATE_FAIL = "FAIL"
    STATE_UNKNOWN = "UNKNOWN"

    def __init__(
        self,
        completeness_checker_instance: Optional[
            CompletenessChecker
        ] = None,
        consistency_checker_instance: Optional[
            ConsistencyChecker
        ] = None,
        pass_threshold: float = QUALITY_PASS_THRESHOLD,
        warning_threshold: float = QUALITY_WARNING_THRESHOLD,
    ) -> None:
        self.completeness_checker = (
            completeness_checker_instance
            or completeness_checker
        )

        self.consistency_checker = (
            consistency_checker_instance
            or consistency_checker
        )

        self.pass_threshold = float(pass_threshold)
        self.warning_threshold = float(warning_threshold)

        if not (
            0.0
            <= self.warning_threshold
            <= self.pass_threshold
            <= 100.0
        ):
            raise DataQualityEngineError(
                "Thresholds must satisfy "
                "0 <= warning <= pass <= 100."
            )

    @staticmethod
    def _clamp_score(
        score: float,
    ) -> float:
        """Clamp a quality score to 0-100."""

        return max(
            0.0,
            min(
                100.0,
                float(score),
            ),
        )

    @staticmethod
    def _extract_score(
        result: Any,
    ) -> Optional[float]:
        """Extract a numeric score from a result object."""

        if result is None:
            return None

        if isinstance(result, dict):
            for key in (
                "quality_score",
                "score",
                "freshness_score",
                "latency_score",
                "health_score",
            ):
                if key in result:
                    value = result[key]

                    try:
                        return float(value)
                    except (
                        TypeError,
                        ValueError,
                    ):
                        return None

            return None

        for attribute in (
            "quality_score",
            "score",
            "freshness_score",
            "latency_score",
            "health_score",
        ):
            if hasattr(result, attribute):
                value = getattr(
                    result,
                    attribute,
                )

                try:
                    return float(value)
                except (
                    TypeError,
                    ValueError,
                ):
                    continue

        return None

    @staticmethod
    def _extract_passed(
        result: Any,
    ) -> Optional[bool]:
        """Extract pass/fail state from a result object."""

        if result is None:
            return None

        if isinstance(result, dict):
            for key in (
                "passed",
                "valid",
                "consistent",
                "complete",
                "healthy",
            ):
                if key in result:
                    return bool(result[key])

            return None

        for attribute in (
            "passed",
            "valid",
            "consistent",
            "complete",
            "healthy",
        ):
            if hasattr(result, attribute):
                return bool(
                    getattr(
                        result,
                        attribute,
                    )
                )

        return None

    def _quality_state(
        self,
        score: float,
    ) -> str:
        """Translate a score into a quality state."""

        if score >= 90.0:
            return self.STATE_EXCELLENT

        if score >= self.pass_threshold:
            return self.STATE_GOOD

        if score >= self.warning_threshold:
            return self.STATE_WARNING

        return self.STATE_FAIL

    def evaluate(
        self,
        data: Any,
        *,
        freshness: Any = None,
        latency: Any = None,
        source_health: Any = None,
        include_optional: bool = True,
    ) -> DataQualityResult:
        """
        Evaluate available data-quality dimensions.

        Freshness, latency, and source-health results can be supplied
        by their dedicated engines without this class creating any
        external dependency or network call.
        """

        completeness_result = (
            self.completeness_checker.check(data)
        )

        consistency_result = (
            self.consistency_checker.check(data)
        )

        dimension_results = [
            completeness_result,
            consistency_result,
        ]

        if include_optional:
            dimension_results.extend(
                [
                    freshness,
                    latency,
                    source_health,
                ]
            )

        scores: list[float] = []

        for result in dimension_results:
            score = self._extract_score(result)

            if score is not None:
                scores.append(
                    self._clamp_score(score)
                )

        if scores:
            quality_score = sum(scores) / len(scores)
        else:
            quality_score = 0.0

        quality_score = self._clamp_score(
            quality_score
        )

        issues: list[str] = []

        if not completeness_result.complete:
            issues.append(
                "Completeness check failed."
            )

        if not consistency_result.consistent:
            issues.append(
                "Consistency check failed."
            )

        optional_results = (
            (
                "freshness",
                freshness,
            ),
            (
                "latency",
                latency,
            ),
            (
                "source_health",
                source_health,
            ),
        )

        if include_optional:
            for name, result in optional_results:
                passed = self._extract_passed(result)

                if passed is False:
                    issues.append(
                        f"{name.replace('_', ' ').title()} "
                        "check failed."
                    )

        quality_state = self._quality_state(
            quality_score
        )

        passed = (
            quality_score >= self.pass_threshold
            and completeness_result.complete
            and consistency_result.consistent
        )

        return DataQualityResult(
            quality_score=round(
                quality_score,
                4,
            ),
            quality_state=quality_state,
            passed=passed,
            completeness=completeness_result,
            consistency=consistency_result,
            freshness=freshness,
            latency=latency,
            source_health=source_health,
            issues=tuple(issues),
            metadata={
                "engine": self.__class__.__name__,
                "dimensions_evaluated": len(
                    [
                        result
                        for result in dimension_results
                        if result is not None
                    ]
                ),
                "pass_threshold": self.pass_threshold,
                "warning_threshold": self.warning_threshold,
            },
        )

    def check(
        self,
        data: Any,
        **kwargs: Any,
    ) -> DataQualityResult:
        """Alias for evaluate()."""

        return self.evaluate(
            data,
            **kwargs,
        )

    def score(
        self,
        data: Any,
        **kwargs: Any,
    ) -> float:
        """Return the combined quality score."""

        return self.evaluate(
            data,
            **kwargs,
        ).quality_score

    def passes(
        self,
        data: Any,
        **kwargs: Any,
    ) -> bool:
        """Return whether the data passes the quality gate."""

        return self.evaluate(
            data,
            **kwargs,
        ).passed

    def summary(
        self,
        data: Any,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Return a compact quality summary."""

        result = self.evaluate(
            data,
            **kwargs,
        )

        return {
            "quality_score": result.quality_score,
            "quality_state": result.quality_state,
            "passed": result.passed,
            "complete": result.complete,
            "consistent": result.consistent,
            "issue_count": len(result.issues),
            "issues": list(result.issues),
        }


data_quality_engine = DataQualityEngine()


def evaluate_data_quality(
    data: Any,
    **kwargs: Any,
) -> DataQualityResult:
    """Convenience function for combined data-quality evaluation."""

    return data_quality_engine.evaluate(
        data,
        **kwargs,
    )


def check_data_quality(
    data: Any,
    **kwargs: Any,
) -> DataQualityResult:
    """Convenience alias for evaluate_data_quality()."""

    return evaluate_data_quality(
        data,
        **kwargs,
    )


__all__ = [
    "DataQualityEngineError",
    "DataQualityResult",
    "DataQualityEngine",
    "data_quality_engine",
    "evaluate_data_quality",
    "check_data_quality",
]