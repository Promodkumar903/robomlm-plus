"""
ROBOMLM PLUS
Market Interval Schema

Purpose:
    Immutable structural representation of a bounded market interval.

Design:
    - Structural and descriptive only.
    - Represents an interval between two temporal points.
    - Supports clock-time, datetime, calendar-date, and sequence context.
    - Does not represent a trading signal.
    - Does not predict market behavior.
    - Does not make trading decisions.
    - Does not execute orders.
    - No V7+ dependency.

Relationship:
    MarketWindow   = named/typed market time window.
    MarketTiming   = timing state relative to schedules/sessions.
    MarketInterval = generic bounded temporal interval.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime, time
from typing import Any, Mapping, Optional


MARKET_INTERVAL_SCHEMA_VERSION = "1.0.0"
MARKET_INTERVAL_SCHEMA = "MARKET_INTERVAL"


def _non_empty(value: Any) -> bool:
    return value is not None and str(value).strip() != ""


def _valid_date(value: Optional[date]) -> bool:
    return value is None or isinstance(value, date)


def _valid_time(value: Optional[time]) -> bool:
    return value is None or isinstance(value, time)


def _valid_datetime(value: Optional[datetime]) -> bool:
    return value is None or isinstance(value, datetime)


@dataclass(frozen=True)
class MarketInterval:
    """
    Immutable structural market interval.

    An interval describes a bounded temporal span and its context.
    It does not infer market meaning beyond explicitly supplied fields.
    """

    # ------------------------------------------------------------------
    # Interval identity
    # ------------------------------------------------------------------
    interval_id: Optional[str] = None
    interval_type: Optional[str] = None
    interval_name: Optional[str] = None
    interval_state: Optional[str] = None

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
    window_id: Optional[str] = None

    calendar_date: Optional[date] = None
    trading_date: Optional[date] = None

    timezone: Optional[str] = None
    locale: Optional[str] = None

    # ------------------------------------------------------------------
    # Date boundaries
    # ------------------------------------------------------------------
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    # ------------------------------------------------------------------
    # Time boundaries
    # ------------------------------------------------------------------
    start_time: Optional[time] = None
    end_time: Optional[time] = None

    # ------------------------------------------------------------------
    # Datetime boundaries
    # ------------------------------------------------------------------
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None

    # ------------------------------------------------------------------
    # Current reference point
    # ------------------------------------------------------------------
    current_date: Optional[date] = None
    current_time: Optional[time] = None
    current_datetime: Optional[datetime] = None

    # ------------------------------------------------------------------
    # Duration
    # ------------------------------------------------------------------
    duration_seconds: Optional[float] = None
    duration_minutes: Optional[float] = None
    duration_hours: Optional[float] = None

    # ------------------------------------------------------------------
    # Relative position
    # ------------------------------------------------------------------
    elapsed_seconds: Optional[float] = None
    elapsed_minutes: Optional[float] = None

    remaining_seconds: Optional[float] = None
    remaining_minutes: Optional[float] = None

    elapsed_ratio: Optional[float] = None
    remaining_ratio: Optional[float] = None

    # ------------------------------------------------------------------
    # Sequence / bar context
    # ------------------------------------------------------------------
    start_sequence: Optional[int] = None
    end_sequence: Optional[int] = None

    interval_index: Optional[int] = None
    interval_count: Optional[int] = None

    # ------------------------------------------------------------------
    # State flags
    # ------------------------------------------------------------------
    is_active: Optional[bool] = None
    is_completed: Optional[bool] = None
    is_open: Optional[bool] = None
    is_closed: Optional[bool] = None

    # ------------------------------------------------------------------
    # Interval classification
    # ------------------------------------------------------------------
    granularity: Optional[str] = None
    frequency: Optional[str] = None
    phase: Optional[str] = None

    is_session_interval: Optional[bool] = None
    is_observation_interval: Optional[bool] = None
    is_analysis_interval: Optional[bool] = None
    is_settlement_interval: Optional[bool] = None
    is_expiry_interval: Optional[bool] = None

    # ------------------------------------------------------------------
    # Parent / neighboring intervals
    # ------------------------------------------------------------------
    parent_interval_id: Optional[str] = None
    previous_interval_id: Optional[str] = None
    next_interval_id: Optional[str] = None

    related_interval_ids: tuple[str, ...] = field(
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
    def has_interval_identity(self) -> bool:
        return _non_empty(self.interval_id)

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
                self.current_date,
                self.current_time,
                self.current_datetime,
                self.start_date,
                self.end_date,
                self.start_time,
                self.end_time,
                self.start_datetime,
                self.end_datetime,
            )
        )

    def has_timezone(self) -> bool:
        return _non_empty(self.timezone)

    # ------------------------------------------------------------------
    # Boundary availability
    # ------------------------------------------------------------------
    def has_date_boundaries(self) -> bool:
        return (
            self.start_date is not None
            and self.end_date is not None
        )

    def has_time_boundaries(self) -> bool:
        return (
            self.start_time is not None
            and self.end_time is not None
        )

    def has_datetime_boundaries(self) -> bool:
        return (
            self.start_datetime is not None
            and self.end_datetime is not None
        )

    def has_any_boundaries(self) -> bool:
        return (
            self.has_date_boundaries()
            or self.has_time_boundaries()
            or self.has_datetime_boundaries()
        )

    # ------------------------------------------------------------------
    # Boundary ordering
    # ------------------------------------------------------------------
    def date_boundaries_ordered(self) -> bool:
        if not self.has_date_boundaries():
            return True

        return self.start_date <= self.end_date

    def time_boundaries_ordered(self) -> bool:
        if not self.has_time_boundaries():
            return True

        return self.start_time < self.end_time

    def datetime_boundaries_ordered(self) -> bool:
        if not self.has_datetime_boundaries():
            return True

        return self.start_datetime < self.end_datetime

    # ------------------------------------------------------------------
    # Duration validation
    # ------------------------------------------------------------------
    def durations_non_negative(self) -> bool:
        values = (
            self.duration_seconds,
            self.duration_minutes,
            self.duration_hours,
            self.elapsed_seconds,
            self.elapsed_minutes,
            self.remaining_seconds,
            self.remaining_minutes,
        )

        return all(
            value is None or value >= 0
            for value in values
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
    # Sequence validation
    # ------------------------------------------------------------------
    def sequence_values_valid(self) -> bool:
        values = (
            self.sequence,
            self.start_sequence,
            self.end_sequence,
            self.interval_index,
            self.interval_count,
        )

        return all(
            value is None or value >= 0
            for value in values
        )

    def sequence_boundaries_ordered(self) -> bool:
        if self.start_sequence is None or self.end_sequence is None:
            return True

        return self.start_sequence <= self.end_sequence

    # ------------------------------------------------------------------
    # Count validation
    # ------------------------------------------------------------------
    def interval_count_valid(self) -> bool:
        if self.interval_count is None:
            return True

        return self.interval_count >= 0

    # ------------------------------------------------------------------
    # Date / time type validation
    # ------------------------------------------------------------------
    def date_fields_valid(self) -> bool:
        return all(
            _valid_date(value)
            for value in (
                self.expiry,
                self.calendar_date,
                self.trading_date,
                self.start_date,
                self.end_date,
                self.current_date,
            )
        )

    def time_fields_valid(self) -> bool:
        return all(
            _valid_time(value)
            for value in (
                self.start_time,
                self.end_time,
                self.current_time,
            )
        )

    def datetime_fields_valid(self) -> bool:
        return all(
            _valid_datetime(value)
            for value in (
                self.timestamp,
                self.start_datetime,
                self.end_datetime,
                self.current_datetime,
                self.valid_from,
                self.valid_until,
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
    # State consistency
    # ------------------------------------------------------------------
    def state_flags_consistent(self) -> bool:
        if self.is_open is True and self.is_closed is True:
            return False

        if self.is_completed is True and self.is_active is True:
            return False

        return True

    # ------------------------------------------------------------------
    # Related intervals
    # ------------------------------------------------------------------
    def has_parent_interval(self) -> bool:
        return _non_empty(self.parent_interval_id)

    def has_neighboring_intervals(self) -> bool:
        return any(
            _non_empty(value)
            for value in (
                self.previous_interval_id,
                self.next_interval_id,
            )
        )

    def has_related_intervals(self) -> bool:
        return len(self.related_interval_ids) > 0

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

        if not self.has_interval_identity():
            issues.append("missing_interval_id")

        if not self.has_market_identity():
            issues.append("missing_market_identity")

        if not self.has_temporal_context():
            issues.append("missing_temporal_context")

        if not self.has_timezone():
            issues.append("missing_timezone")

        if not self.has_any_boundaries():
            issues.append("missing_interval_boundaries")

        if not self.date_fields_valid():
            issues.append("invalid_date_field")

        if not self.time_fields_valid():
            issues.append("invalid_time_field")

        if not self.datetime_fields_valid():
            issues.append("invalid_datetime_field")

        if not self.date_boundaries_ordered():
            issues.append("invalid_date_boundary_order")

        if not self.time_boundaries_ordered():
            issues.append("invalid_time_boundary_order")

        if not self.datetime_boundaries_ordered():
            issues.append("invalid_datetime_boundary_order")

        if not self.durations_non_negative():
            issues.append("negative_duration")

        if not self.ratios_valid():
            issues.append("invalid_ratio")

        if not self.sequence_values_valid():
            issues.append("invalid_sequence_value")

        if not self.sequence_boundaries_ordered():
            issues.append("invalid_sequence_boundary_order")

        if not self.interval_count_valid():
            issues.append("invalid_interval_count")

        if not self.validity_window_valid():
            issues.append("invalid_validity_window")

        if not self.state_flags_consistent():
            issues.append("inconsistent_state_flags")

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
            "schema": MARKET_INTERVAL_SCHEMA,
            "version": MARKET_INTERVAL_SCHEMA_VERSION,
            "immutable": True,
            "structural_only": True,
            "temporal_interval_only": True,
            "prediction_logic": False,
            "signal_generation": False,
            "decision_logic": False,
            "execution_logic": False,
            "v7_dependency": False,
        }


def market_interval_health() -> dict[str, Any]:
    """
    Return static health information for the MarketInterval schema.
    """

    return {
        "schema": MARKET_INTERVAL_SCHEMA,
        "version": MARKET_INTERVAL_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "structural_only": True,
        "temporal_interval_only": True,
        "prediction_logic": False,
        "signal_generation": False,
        "decision_logic": False,
        "execution_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_INTERVAL_SCHEMA_VERSION",
    "MARKET_INTERVAL_SCHEMA",
    "MarketInterval",
    "market_interval_health",
]