"""
ROBOMLM PLUS
Market Timeframe Schema

Purpose:
    Immutable structural representation of a market timeframe.

Design:
    - Structural and descriptive only.
    - Defines timeframe identity, granularity, duration, boundaries,
      aggregation context, and temporal relationships.
    - Does not calculate trading signals.
    - Does not make trading decisions.
    - Does not execute orders.
    - No V7+ dependency.

Relationship:
    MarketInterval = bounded temporal interval.
    MarketWindow   = named/typed temporal window.
    MarketTiming   = timing state.
    MarketTimeframe = explicit temporal resolution/aggregation definition.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime, time
from typing import Any, Mapping, Optional


MARKET_TIMEFRAME_SCHEMA_VERSION = "1.0.0"
MARKET_TIMEFRAME_SCHEMA = "MARKET_TIMEFRAME"


def _non_empty(value: Any) -> bool:
    return value is not None and str(value).strip() != ""


def _valid_date(value: Optional[date]) -> bool:
    return value is None or isinstance(value, date)


def _valid_time(value: Optional[time]) -> bool:
    return value is None or isinstance(value, time)


def _valid_datetime(value: Optional[datetime]) -> bool:
    return value is None or isinstance(value, datetime)


@dataclass(frozen=True)
class MarketTimeframe:
    """
    Immutable structural market timeframe record.

    A timeframe describes the temporal resolution used to represent
    or aggregate market information.

    Examples:
        1m, 5m, 15m, 1h, 4h, 1d

    The schema records the timeframe definition and context only.
    """

    # ------------------------------------------------------------------
    # Timeframe identity
    # ------------------------------------------------------------------
    timeframe_id: Optional[str] = None
    timeframe_type: Optional[str] = None
    timeframe_name: Optional[str] = None
    timeframe_code: Optional[str] = None
    timeframe_state: Optional[str] = None

    timestamp: Optional[datetime] = None
    sequence: Optional[int] = None

    # ------------------------------------------------------------------
    # Market / instrument identity
    # ------------------------------------------------------------------
    market: Optional[str] = None
    instrument: Optional[str] = None
    symbol: Optional[str] = None
    exchange: Optional[str] = None
    venue: Optional[str] = None
    contract: Optional[str] = None
    expiry: Optional[date] = None

    # ------------------------------------------------------------------
    # Calendar / schedule / session context
    # ------------------------------------------------------------------
    calendar_id: Optional[str] = None
    schedule_id: Optional[str] = None
    session_id: Optional[str] = None
    timing_id: Optional[str] = None
    interval_id: Optional[str] = None
    window_id: Optional[str] = None

    calendar_date: Optional[date] = None
    trading_date: Optional[date] = None

    timezone: Optional[str] = None
    locale: Optional[str] = None

    # ------------------------------------------------------------------
    # Resolution definition
    # ------------------------------------------------------------------
    unit: Optional[str] = None
    duration_value: Optional[float] = None
    duration_seconds: Optional[float] = None
    duration_minutes: Optional[float] = None
    duration_hours: Optional[float] = None
    duration_days: Optional[float] = None

    # ------------------------------------------------------------------
    # Aggregation definition
    # ------------------------------------------------------------------
    aggregation_method: Optional[str] = None
    aggregation_source: Optional[str] = None
    base_timeframe_id: Optional[str] = None
    base_timeframe_code: Optional[str] = None

    aggregation_factor: Optional[float] = None

    # ------------------------------------------------------------------
    # Boundary alignment
    # ------------------------------------------------------------------
    alignment_type: Optional[str] = None
    anchor_time: Optional[time] = None
    anchor_datetime: Optional[datetime] = None

    boundary_start: Optional[time] = None
    boundary_end: Optional[time] = None

    boundary_start_datetime: Optional[datetime] = None
    boundary_end_datetime: Optional[datetime] = None

    # ------------------------------------------------------------------
    # Current timeframe position
    # ------------------------------------------------------------------
    current_time: Optional[time] = None
    current_datetime: Optional[datetime] = None

    elapsed_seconds: Optional[float] = None
    remaining_seconds: Optional[float] = None

    elapsed_ratio: Optional[float] = None
    remaining_ratio: Optional[float] = None

    # ------------------------------------------------------------------
    # Candle / bar context
    # ------------------------------------------------------------------
    bar_id: Optional[str] = None
    bar_index: Optional[int] = None
    bar_start: Optional[datetime] = None
    bar_end: Optional[datetime] = None

    is_bar_complete: Optional[bool] = None
    is_partial_bar: Optional[bool] = None

    # ------------------------------------------------------------------
    # Session relationship
    # ------------------------------------------------------------------
    session_start: Optional[datetime] = None
    session_end: Optional[datetime] = None

    session_elapsed_seconds: Optional[float] = None
    session_remaining_seconds: Optional[float] = None

    # ------------------------------------------------------------------
    # Timeframe classification
    # ------------------------------------------------------------------
    granularity: Optional[str] = None
    frequency: Optional[str] = None
    horizon: Optional[str] = None

    is_intraday: Optional[bool] = None
    is_daily: Optional[bool] = None
    is_weekly: Optional[bool] = None
    is_monthly: Optional[bool] = None
    is_session_based: Optional[bool] = None

    # ------------------------------------------------------------------
    # Multi-timeframe relationships
    # ------------------------------------------------------------------
    parent_timeframe_id: Optional[str] = None
    higher_timeframe_id: Optional[str] = None
    lower_timeframe_id: Optional[str] = None

    related_timeframe_ids: tuple[str, ...] = field(
        default_factory=tuple
    )

    # ------------------------------------------------------------------
    # Validity
    # ------------------------------------------------------------------
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None

    # ------------------------------------------------------------------
    # Provider / environment
    # ------------------------------------------------------------------
    broker: Optional[str] = None
    provider: Optional[str] = None
    environment: Optional[str] = None
    mode: Optional[str] = None

    # ------------------------------------------------------------------
    # Provenance
    # ------------------------------------------------------------------
    source: Optional[str] = None
    source_type: Optional[str] = None
    source_reference: Optional[str] = None
    provenance: Optional[str] = None

    observed_fields: tuple[str, ...] = field(
        default_factory=tuple
    )

    derived_fields: tuple[str, ...] = field(
        default_factory=tuple
    )

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    # ------------------------------------------------------------------
    # Identity checks
    # ------------------------------------------------------------------
    def has_timeframe_identity(self) -> bool:
        return _non_empty(self.timeframe_id)

    def has_timeframe_definition(self) -> bool:
        return any(
            _non_empty(value)
            for value in (
                self.timeframe_code,
                self.timeframe_name,
                self.unit,
            )
        ) or self.duration_value is not None

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

    def has_temporal_context(self) -> bool:
        return any(
            value is not None
            for value in (
                self.timestamp,
                self.calendar_date,
                self.trading_date,
                self.current_time,
                self.current_datetime,
                self.boundary_start,
                self.boundary_end,
                self.boundary_start_datetime,
                self.boundary_end_datetime,
            )
        )

    def has_timezone(self) -> bool:
        return _non_empty(self.timezone)

    # ------------------------------------------------------------------
    # Duration validation
    # ------------------------------------------------------------------
    def duration_values_non_negative(self) -> bool:
        values = (
            self.duration_value,
            self.duration_seconds,
            self.duration_minutes,
            self.duration_hours,
            self.duration_days,
            self.aggregation_factor,
            self.elapsed_seconds,
            self.remaining_seconds,
            self.session_elapsed_seconds,
            self.session_remaining_seconds,
        )

        return all(
            value is None or value >= 0
            for value in values
        )

    def has_duration(self) -> bool:
        return any(
            value is not None
            for value in (
                self.duration_seconds,
                self.duration_minutes,
                self.duration_hours,
                self.duration_days,
            )
        )

    # ------------------------------------------------------------------
    # Ratio validation
    # ------------------------------------------------------------------
    def ratios_valid(self) -> bool:
        values = (
            self.elapsed_ratio,
            self.remaining_ratio,
        )

        return all(
            value is None or 0 <= value <= 1
            for value in values
        )

    # ------------------------------------------------------------------
    # Boundary validation
    # ------------------------------------------------------------------
    def time_boundaries_ordered(self) -> bool:
        if (
            self.boundary_start is None
            or self.boundary_end is None
        ):
            return True

        return self.boundary_start < self.boundary_end

    def datetime_boundaries_ordered(self) -> bool:
        if (
            self.boundary_start_datetime is None
            or self.boundary_end_datetime is None
        ):
            return True

        return self.boundary_start_datetime < self.boundary_end_datetime

    def bar_boundaries_ordered(self) -> bool:
        if self.bar_start is None or self.bar_end is None:
            return True

        return self.bar_start < self.bar_end

    def session_boundaries_ordered(self) -> bool:
        if self.session_start is None or self.session_end is None:
            return True

        return self.session_start < self.session_end

    # ------------------------------------------------------------------
    # Type validation
    # ------------------------------------------------------------------
    def date_fields_valid(self) -> bool:
        return all(
            _valid_date(value)
            for value in (
                self.expiry,
                self.calendar_date,
                self.trading_date,
            )
        )

    def time_fields_valid(self) -> bool:
        return all(
            _valid_time(value)
            for value in (
                self.anchor_time,
                self.boundary_start,
                self.boundary_end,
                self.current_time,
            )
        )

    def datetime_fields_valid(self) -> bool:
        return all(
            _valid_datetime(value)
            for value in (
                self.timestamp,
                self.anchor_datetime,
                self.boundary_start_datetime,
                self.boundary_end_datetime,
                self.current_datetime,
                self.bar_start,
                self.bar_end,
                self.session_start,
                self.session_end,
                self.valid_from,
                self.valid_until,
            )
        )

    # ------------------------------------------------------------------
    # Sequence validation
    # ------------------------------------------------------------------
    def sequence_values_valid(self) -> bool:
        return all(
            value is None or value >= 0
            for value in (
                self.sequence,
                self.bar_index,
            )
        )

    # ------------------------------------------------------------------
    # Validity window
    # ------------------------------------------------------------------
    def validity_window_valid(self) -> bool:
        if self.valid_from is None or self.valid_until is None:
            return True

        return self.valid_from <= self.valid_until

    # ------------------------------------------------------------------
    # Multi-timeframe relationships
    # ------------------------------------------------------------------
    def has_parent_timeframe(self) -> bool:
        return _non_empty(self.parent_timeframe_id)

    def has_higher_timeframe(self) -> bool:
        return _non_empty(self.higher_timeframe_id)

    def has_lower_timeframe(self) -> bool:
        return _non_empty(self.lower_timeframe_id)

    def has_related_timeframes(self) -> bool:
        return len(self.related_timeframe_ids) > 0

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

        if not self.has_timeframe_identity():
            issues.append("missing_timeframe_id")

        if not self.has_timeframe_definition():
            issues.append("missing_timeframe_definition")

        if not self.has_market_identity():
            issues.append("missing_market_identity")

        if not self.has_temporal_context():
            issues.append("missing_temporal_context")

        if not self.has_timezone():
            issues.append("missing_timezone")

        if not self.date_fields_valid():
            issues.append("invalid_date_field")

        if not self.time_fields_valid():
            issues.append("invalid_time_field")

        if not self.datetime_fields_valid():
            issues.append("invalid_datetime_field")

        if not self.duration_values_non_negative():
            issues.append("negative_duration_or_factor")

        if not self.ratios_valid():
            issues.append("invalid_ratio")

        if not self.time_boundaries_ordered():
            issues.append("invalid_time_boundary_order")

        if not self.datetime_boundaries_ordered():
            issues.append("invalid_datetime_boundary_order")

        if not self.bar_boundaries_ordered():
            issues.append("invalid_bar_boundary_order")

        if not self.session_boundaries_ordered():
            issues.append("invalid_session_boundary_order")

        if not self.sequence_values_valid():
            issues.append("invalid_sequence_value")

        if not self.validity_window_valid():
            issues.append("invalid_validity_window")

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
    # Schema information
    # ------------------------------------------------------------------
    @classmethod
    def schema_info(cls) -> dict[str, Any]:
        return {
            "schema": MARKET_TIMEFRAME_SCHEMA,
            "version": MARKET_TIMEFRAME_SCHEMA_VERSION,
            "immutable": True,
            "structural_only": True,
            "temporal_resolution_only": True,
            "prediction_logic": False,
            "signal_generation": False,
            "decision_logic": False,
            "execution_logic": False,
            "v7_dependency": False,
        }


def market_timeframe_health() -> dict[str, Any]:
    """
    Return static health information for the MarketTimeframe schema.
    """

    return {
        "schema": MARKET_TIMEFRAME_SCHEMA,
        "version": MARKET_TIMEFRAME_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "structural_only": True,
        "temporal_resolution_only": True,
        "prediction_logic": False,
        "signal_generation": False,
        "decision_logic": False,
        "execution_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_TIMEFRAME_SCHEMA_VERSION",
    "MARKET_TIMEFRAME_SCHEMA",
    "MarketTimeframe",
    "market_timeframe_health",
]