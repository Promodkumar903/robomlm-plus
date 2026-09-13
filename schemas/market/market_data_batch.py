"""
ROBOMLM PLUS
Market Data Batch Schema

Purpose:
    Immutable structural representation of a bounded batch of market
    data points.

Design:
    - Groups atomic MarketDataPoint records into a defined batch.
    - Preserves ordering, coverage, source, quality, and batch identity.
    - Structural representation only.
    - Does not generate signals.
    - Does not make trading decisions.
    - Does not execute orders.
    - No V7+ dependency.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Any, Mapping, Optional, Sequence


MARKET_DATA_BATCH_SCHEMA_VERSION = "1.0.0"
MARKET_DATA_BATCH_SCHEMA = "MARKET_DATA_BATCH"


def _non_empty(value: Any) -> bool:
    return value is not None and str(value).strip() != ""


def _non_negative(value: Optional[float | int]) -> bool:
    return value is None or value >= 0


@dataclass(frozen=True)
class MarketDataBatch:
    """
    Immutable structural market-data batch.

    The batch describes a collection of market data points and its
    structural context. It intentionally does not interpret the data.
    """

    # ------------------------------------------------------------------
    # Batch identity
    # ------------------------------------------------------------------
    batch_id: Optional[str] = None
    batch_type: Optional[str] = None
    batch_name: Optional[str] = None
    batch_code: Optional[str] = None
    batch_state: Optional[str] = None

    # ------------------------------------------------------------------
    # Market identity
    # ------------------------------------------------------------------
    market: Optional[str] = None
    instrument: Optional[str] = None
    symbol: Optional[str] = None
    exchange: Optional[str] = None
    venue: Optional[str] = None
    contract: Optional[str] = None
    expiry: Optional[date] = None

    # ------------------------------------------------------------------
    # Structural references
    # ------------------------------------------------------------------
    series_id: Optional[str] = None
    timeframe_id: Optional[str] = None
    interval_id: Optional[str] = None
    window_id: Optional[str] = None
    session_id: Optional[str] = None
    calendar_id: Optional[str] = None
    schedule_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Batch ordering
    # ------------------------------------------------------------------
    sequence: Optional[int] = None
    first_sequence: Optional[int] = None
    last_sequence: Optional[int] = None

    order_field: Optional[str] = None
    order_direction: Optional[str] = None

    # ------------------------------------------------------------------
    # Batch size
    # ------------------------------------------------------------------
    point_count: Optional[int] = None
    expected_point_count: Optional[int] = None

    # ------------------------------------------------------------------
    # Temporal coverage
    # ------------------------------------------------------------------
    timestamp: Optional[datetime] = None

    start_timestamp: Optional[datetime] = None
    end_timestamp: Optional[datetime] = None

    first_point_timestamp: Optional[datetime] = None
    last_point_timestamp: Optional[datetime] = None

    trading_date: Optional[date] = None
    timezone: Optional[str] = None

    # ------------------------------------------------------------------
    # Coverage duration
    # ------------------------------------------------------------------
    coverage_seconds: Optional[float] = None
    coverage_minutes: Optional[float] = None
    coverage_hours: Optional[float] = None
    coverage_days: Optional[float] = None

    # ------------------------------------------------------------------
    # Data characteristics
    # ------------------------------------------------------------------
    data_type: Optional[str] = None
    observation_type: Optional[str] = None
    measurement_type: Optional[str] = None

    source_schema: Optional[str] = None
    source_version: Optional[str] = None

    # ------------------------------------------------------------------
    # Quality / continuity
    # ------------------------------------------------------------------
    quality_status: Optional[str] = None
    quality_score: Optional[float] = None
    completeness_status: Optional[str] = None
    continuity_status: Optional[str] = None
    validation_status: Optional[str] = None

    missing_point_count: Optional[int] = None
    duplicate_point_count: Optional[int] = None
    out_of_order_count: Optional[int] = None
    gap_count: Optional[int] = None
    overlap_count: Optional[int] = None

    # ------------------------------------------------------------------
    # Source / provenance
    # ------------------------------------------------------------------
    source: Optional[str] = None
    source_type: Optional[str] = None
    source_reference: Optional[str] = None
    provider: Optional[str] = None
    broker: Optional[str] = None
    provenance: Optional[str] = None

    # ------------------------------------------------------------------
    # Transport / ingestion context
    # ------------------------------------------------------------------
    ingestion_id: Optional[str] = None
    request_id: Optional[str] = None
    session_request_id: Optional[str] = None

    received_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None

    latency_ms: Optional[float] = None

    # ------------------------------------------------------------------
    # Environment
    # ------------------------------------------------------------------
    environment: Optional[str] = None
    mode: Optional[str] = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    is_complete: Optional[bool] = None
    is_live: Optional[bool] = None
    is_final: Optional[bool] = None

    # ------------------------------------------------------------------
    # Point references
    #
    # References are IDs only. The batch schema does not mutate or own
    # the underlying MarketDataPoint objects.
    # ------------------------------------------------------------------
    point_ids: tuple[str, ...] = field(
        default_factory=tuple
    )

    # ------------------------------------------------------------------
    # Field lineage
    # ------------------------------------------------------------------
    observed_fields: tuple[str, ...] = field(
        default_factory=tuple
    )

    derived_fields: tuple[str, ...] = field(
        default_factory=tuple
    )

    # ------------------------------------------------------------------
    # Additional metadata
    # ------------------------------------------------------------------
    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    # ------------------------------------------------------------------
    # Identity checks
    # ------------------------------------------------------------------
    def has_batch_identity(self) -> bool:
        return _non_empty(self.batch_id)

    def has_market_identity(self) -> bool:
        return any(
            _non_empty(value)
            for value in (
                self.market,
                self.instrument,
                self.symbol,
                self.exchange,
                self.venue,
                self.contract,
            )
        )

    def has_structure_identity(self) -> bool:
        return any(
            _non_empty(value)
            for value in (
                self.series_id,
                self.timeframe_id,
                self.interval_id,
                self.window_id,
                self.session_id,
            )
        )

    def has_temporal_coverage(self) -> bool:
        return any(
            value is not None
            for value in (
                self.timestamp,
                self.start_timestamp,
                self.end_timestamp,
                self.first_point_timestamp,
                self.last_point_timestamp,
                self.trading_date,
            )
        )

    def has_source_identity(self) -> bool:
        return any(
            _non_empty(value)
            for value in (
                self.source,
                self.source_type,
                self.source_reference,
                self.provider,
                self.broker,
            )
        )

    # ------------------------------------------------------------------
    # Count validation
    # ------------------------------------------------------------------
    def counts_valid(self) -> bool:
        values = (
            self.sequence,
            self.first_sequence,
            self.last_sequence,
            self.point_count,
            self.expected_point_count,
            self.missing_point_count,
            self.duplicate_point_count,
            self.out_of_order_count,
            self.gap_count,
            self.overlap_count,
        )

        return all(
            _non_negative(value)
            for value in values
        )

    def sequence_order_valid(self) -> bool:
        if (
            self.first_sequence is None
            or self.last_sequence is None
        ):
            return True

        return self.first_sequence <= self.last_sequence

    def point_count_valid(self) -> bool:
        if (
            self.point_count is None
            or self.expected_point_count is None
        ):
            return True

        return self.point_count <= self.expected_point_count

    def point_ids_count_consistent(self) -> bool:
        if self.point_count is None:
            return True

        return len(self.point_ids) == self.point_count

    # ------------------------------------------------------------------
    # Timestamp validation
    # ------------------------------------------------------------------
    def timestamp_order_valid(self) -> bool:
        pairs = (
            (
                self.start_timestamp,
                self.end_timestamp,
            ),
            (
                self.first_point_timestamp,
                self.last_point_timestamp,
            ),
            (
                self.created_at,
                self.updated_at,
            ),
            (
                self.received_at,
                self.processed_at,
            ),
        )

        for start, end in pairs:
            if start is not None and end is not None:
                if start > end:
                    return False

        return True

    # ------------------------------------------------------------------
    # Coverage validation
    # ------------------------------------------------------------------
    def coverage_values_valid(self) -> bool:
        values = (
            self.coverage_seconds,
            self.coverage_minutes,
            self.coverage_hours,
            self.coverage_days,
            self.latency_ms,
        )

        return all(
            _non_negative(value)
            for value in values
        )

    # ------------------------------------------------------------------
    # Ordering validation
    # ------------------------------------------------------------------
    def ordering_defined(self) -> bool:
        if not _non_empty(self.order_field):
            return False

        if not _non_empty(self.order_direction):
            return False

        return self.order_direction.upper() in {
            "ASC",
            "DESC",
            "ASCENDING",
            "DESCENDING",
        }

    # ------------------------------------------------------------------
    # Quality validation
    # ------------------------------------------------------------------
    def quality_score_valid(self) -> bool:
        if self.quality_score is None:
            return True

        return 0 <= self.quality_score <= 100

    # ------------------------------------------------------------------
    # Point reference validation
    # ------------------------------------------------------------------
    def point_ids_valid(self) -> bool:
        return all(
            _non_empty(point_id)
            for point_id in self.point_ids
        )

    def point_ids_unique(self) -> bool:
        return len(self.point_ids) == len(set(self.point_ids))

    # ------------------------------------------------------------------
    # Structural issue collection
    # ------------------------------------------------------------------
    def issue_flags(self) -> list[str]:
        issues: list[str] = []

        if not self.has_batch_identity():
            issues.append("missing_batch_id")

        if not self.has_market_identity():
            issues.append("missing_market_identity")

        if not self.has_structure_identity():
            issues.append("missing_structure_identity")

        if not self.has_temporal_coverage():
            issues.append("missing_temporal_coverage")

        if not self.has_source_identity():
            issues.append("missing_source_identity")

        if not self.counts_valid():
            issues.append("invalid_count")

        if not self.sequence_order_valid():
            issues.append("invalid_sequence_order")

        if not self.point_count_valid():
            issues.append("invalid_point_count")

        if not self.point_ids_count_consistent():
            issues.append("point_count_reference_mismatch")

        if not self.point_ids_valid():
            issues.append("invalid_point_reference")

        if not self.point_ids_unique():
            issues.append("duplicate_point_reference")

        if not self.timestamp_order_valid():
            issues.append("invalid_timestamp_order")

        if not self.coverage_values_valid():
            issues.append("invalid_coverage_value")

        if (
            self.order_field is not None
            or self.order_direction is not None
        ):
            if not self.ordering_defined():
                issues.append("invalid_ordering_definition")

        if not self.quality_score_valid():
            issues.append("invalid_quality_score")

        return issues

    # ------------------------------------------------------------------
    # Structural validity
    # ------------------------------------------------------------------
    def is_structurally_valid(self) -> bool:
        return len(self.issue_flags()) == 0

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    # ------------------------------------------------------------------
    # Schema metadata
    # ------------------------------------------------------------------
    @classmethod
    def schema_info(cls) -> dict[str, Any]:
        return {
            "schema": MARKET_DATA_BATCH_SCHEMA,
            "version": MARKET_DATA_BATCH_SCHEMA_VERSION,
            "immutable": True,
            "structural_only": True,
            "bounded_collection": True,
            "ordered_data": True,
            "point_references_only": True,
            "signal_generation": False,
            "decision_logic": False,
            "execution_logic": False,
            "v7_dependency": False,
        }


def market_data_batch_health() -> dict[str, Any]:
    """
    Return static health information for the MarketDataBatch schema.
    """

    return {
        "schema": MARKET_DATA_BATCH_SCHEMA,
        "version": MARKET_DATA_BATCH_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "structural_only": True,
        "bounded_collection": True,
        "ordered_data": True,
        "point_references_only": True,
        "signal_generation": False,
        "decision_logic": False,
        "execution_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_DATA_BATCH_SCHEMA_VERSION",
    "MARKET_DATA_BATCH_SCHEMA",
    "MarketDataBatch",
    "market_data_batch_health",
]