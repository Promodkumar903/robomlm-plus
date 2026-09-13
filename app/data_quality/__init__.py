"""
ROBOMLM PLUS
Data Quality Package

Exports the unified data-quality engine and all currently
implemented quality-check components.
"""

from .completeness_check import (
    CompletenessCheckError,
    CompletenessResult,
    CompletenessChecker,
    completeness_checker,
    check_completeness,
)

from .consistency_check import (
    ConsistencyCheckError,
    ConsistencyIssue,
    ConsistencyResult,
    ConsistencyChecker,
    consistency_checker,
    check_consistency,
)

from .data_quality_engine import (
    DataQualityEngineError,
    DataQualityResult,
    DataQualityEngine,
    data_quality_engine,
    evaluate_data_quality,
    check_data_quality,
)

from .freshness_check import (
    FreshnessCheckError,
    FreshnessResult,
    FreshnessChecker,
    freshness_checker,
    check_freshness,
)

from .latency_check import (
    LatencyCheckError,
    LatencyResult,
    LatencyChecker,
    latency_checker,
    check_latency,
)

from .source_health import (
    SourceHealthCheckError,
    SourceHealthResult,
    SourceHealthChecker,
    source_health_checker,
    check_source_health,
)


DATA_QUALITY_PACKAGE = "app.data_quality"


__all__ = [
    "DATA_QUALITY_PACKAGE",

    # Completeness
    "CompletenessCheckError",
    "CompletenessResult",
    "CompletenessChecker",
    "completeness_checker",
    "check_completeness",

    # Consistency
    "ConsistencyCheckError",
    "ConsistencyIssue",
    "ConsistencyResult",
    "ConsistencyChecker",
    "consistency_checker",
    "check_consistency",

    # Unified engine
    "DataQualityEngineError",
    "DataQualityResult",
    "DataQualityEngine",
    "data_quality_engine",
    "evaluate_data_quality",
    "check_data_quality",

    # Freshness
    "FreshnessCheckError",
    "FreshnessResult",
    "FreshnessChecker",
    "freshness_checker",
    "check_freshness",

    # Latency
    "LatencyCheckError",
    "LatencyResult",
    "LatencyChecker",
    "latency_checker",
    "check_latency",

    # Source health
    "SourceHealthCheckError",
    "SourceHealthResult",
    "SourceHealthChecker",
    "source_health_checker",
    "check_source_health",
]