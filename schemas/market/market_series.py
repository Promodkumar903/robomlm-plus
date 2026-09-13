"""
ROBOMLM PLUS
Market Series Schema

Purpose:
    Immutable structural representation of a time-ordered market series.

Design:
    - Stores a series identity and its temporal structure.
    - Describes the relationship between a series and its observations,
      intervals, windows, and timeframes.
    - Does not generate signals.
    - Does not make trading decisions.
    - Does not execute orders.
    - Does not contain V7+ intelligence.

Relationship:
    MarketTimeframe = temporal resolution.
    MarketInterval  = bounded temporal interval.
    MarketWindow    = named/typed temporal window.
    MarketSeries    = ordered collection identity and structural context.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Any, Mapping, Optional


MARKET_SERIES_SCHEMA_VERSION = "1.0.0"
MARKET_SERIES_SCHEMA = "MARKET_SERIES"


def _non_empty(value: Any) -> bool:
    return value is not None and str(value).strip() != ""


def _non_negative(value: Optional[float | int]) -> bool:
    return value is None or value >= 0


@dataclass(frozen=True)
class MarketSeries:
    """
    Immutable structural market-series record.

    A MarketSeries identifies an ordered stream of market observations
    at a defined temporal resolution.

    It describes the series; it does not calculate or interpret the
    observations themselves.
    """

    # ------------------------------------------------------------------
    # Series identity
    # ------------------------------------------------------------------
    series_id: Optional[str] = None
    series_name: Optional[str] = None
    series_type: Optional[str] = None
    series_code: Optional[str] = None
    series_state: Optional[str] = None

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
    # Series structure
    # ------------------------------------------------------------------
    timeframe_id: Optional[str] = None
    timeframe_code: Optional[str] = None
    interval_id: Optional[str] = None
    window_id: Optional[str] = None
    calendar_id: Optional[str] = None
    schedule_id: Optional[str] = None
    session_id: Optional[str] = None

    frequency: Optional[str] = None
    granularity: Optional[str] = None
    aggregation_method: Optional[str] = None
    aggregation_source: Optional[str] = None

    # ------------------------------------------------------------------
    # Ordering
    # ------------------------------------------------------------------
    order_field: Optional[str] = None
    order_direction: Optional[str] = None

    first_sequence: Optional[int] = None
    last_sequence: Optional[int] = None

    observation_count: Optional[int] = None
    expected_count: Optional[int] = None

    # ------------------------------------------------------------------
    # Temporal boundaries
    # ------------------------------------------------------------------
    start_timestamp: Optional[datetime] = None
    end_timestamp: Optional[datetime] = None

    first_observation_timestamp: Optional[datetime] = None
    last_observation_timestamp: Optional[datetime] = None

    timezone: Optional[str] = None
    trading_date: Optional[date] = None

    # ------------------------------------------------------------------
    # Coverage
    # ------------------------------------------------------------------
    coverage_start: Optional[datetime] = None
    coverage_end: Optional[datetime] = None

    coverage_seconds: Optional[float] = None
    coverage_minutes: Optional[float] = None
    coverage_hours: Optional[float] = None
    coverage_days: Optional[float] = None

    # ------------------------------------------------------------------
    # Observation structure
    # ------------------------------------------------------------------
    observation_type: Optional[str] = None
    observation_schema: Optional[str] = None
    observation_version: Optional[str] = None

    value_field: Optional[str] = None
    timestamp_field: Optional[str] = None

    # ------------------------------------------------------------------
    # Data quality / continuity
    # ------------------------------------------------------------------
    continuity_status: Optional[str] = None
    completeness_status: Optional[str] = None
    quality_status: Optional[str] = None

    missing_observation_count: Optional[int] = None
    duplicate_observation_count: Optional[int] = None
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
    # Environment
    # ------------------------------------------------------------------
    environment: Optional[str] = None
    mode: Optional[str] = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None

    is_active: Optional[bool] = None
    is_complete: Optional[bool] = None
    is_live: Optional[bool] = None

    # ------------------------------------------------------------------
    # Related series
    # ------------------------------------------------------------------
    parent_series_id: Optional[str] = None
    source_series_id: Optional[str] = None

    related_series_ids: tuple[str, ...] = field(
        default_factory=tuple
    )

    # ------------------------------------------------------------------
    # Field provenance
    # ------------------------------------------------------------------
    observed_fields: tuple[str, ...] = field(
        default_factory=tuple
    )

    derived_fields: tuple[str, ...] = field(
        default_factory=tuple
    )

    # ------------------------------------------------------------------
    # Additional structural metadata
    # ------------------------------------------------------------------
    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------
    def has_series_identity(self) -> bool:
        return _non_empty(self.series_id)

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

    def has_temporal_definition(self) -> bool:
        return any(
            _non_empty(value)
            for value in (
                self.timeframe_id,
                self.timeframe_code,
                self.interval_id,
                self.window_id,
                self.frequency,
                self.granularity,
            )
        )

    def has_temporal_coverage(self) -> bool:
        return any(
            value is not None
            for value in (
                self.start_timestamp,
                self.end_timestamp,
                self.first_observation_timestamp,
                self.last_observation_timestamp,
                self.coverage_start,
                self.coverage_end,
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
            self.first_sequence,
            self.last_sequence,
            self.observation_count,
            self.expected_count,
            self.missing_observation_count,
            self.duplicate_observation_count,
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

    def observation_count_valid(self) -> bool:
        if (
            self.observation_count is None
            or self.expected_count is None
        ):
            return True

        return self.observation_count <= self.expected_count

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
                self.first_observation_timestamp,
                self.last_observation_timestamp,
            ),
            (
                self.coverage_start,
                self.coverage_end,
            ),
            (
                self.valid_from,
                self.valid_until,
            ),
            (
                self.created_at,
                self.updated_at,
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
        )

        return all(
            _non_negative(value)
            for value in values
        )

    # ------------------------------------------------------------------
    # Ordering definition
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
    # Related series
    # ------------------------------------------------------------------
    def has_parent_series(self) -> bool:
        return _non_empty(self.parent_series_id)

    def has_source_series(self) -> bool:
        return _non_empty(self.source_series_id)

    def has_related_series(self) -> bool:
        return len(self.related_series_ids) > 0

    # ------------------------------------------------------------------
    # Provenance
    # ------------------------------------------------------------------
    def has_provenance(self) -> bool:
        return any(
            _non_empty(value)
            for value in (
                self.source,
                self.source_type,
                self.source_reference,
                self.provenance,
            )
        )

    # ------------------------------------------------------------------
    # Structural issue collection
    # ------------------------------------------------------------------
    def issue_flags(self) -> list[str]:
        issues: list[str] = []

        if not self.has_series_identity():
            issues.append("missing_series_id")

        if not self.has_market_identity():
            issues.append("missing_market_identity")

        if not self.has_temporal_definition():
            issues.append("missing_temporal_definition")

        if not self.has_temporal_coverage():
            issues.append("missing_temporal_coverage")

        if not self.has_source_identity():
            issues.append("missing_source_identity")

        if not self.counts_valid():
            issues.append("invalid_count")

        if not self.sequence_order_valid():
            issues.append("invalid_sequence_order")

        if not self.observation_count_valid():
            issues.append("invalid_observation_count")

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
            "schema": MARKET_SERIES_SCHEMA,
            "version": MARKET_SERIES_SCHEMA_VERSION,
            "immutable": True,
            "structural_only": True,
            "ordered_series": True,
            "observation_definition_only": True,
            "signal_generation": False,
            "decision_logic": False,
            "execution_logic": False,
            "v7_dependency": False,
        }


def market_series_health() -> dict[str, Any]:
    """
    Return static health information for the MarketSeries schema.
    """

    return {
        "schema": MARKET_SERIES_SCHEMA,
        "version": MARKET_SERIES_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "structural_only": True,
        "ordered_series": True,
        "observation_definition_only": True,
        "signal_generation": False,
        "decision_logic": False,
        "execution_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_SERIES_SCHEMA_VERSION",
    "MARKET_SERIES_SCHEMA",
    "MarketSeries",
    "market_series_health",
]