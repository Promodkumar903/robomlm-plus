"""
ROBOMLM PLUS
Market Window Schema

Purpose:
    Immutable structural representation of a market time window.

Design:
    - Structural and descriptive only.
    - Represents named temporal windows and their boundaries.
    - Can describe trading, observation, auction, break, analysis,
      settlement, expiry, or other explicitly identified windows.
    - Does not decide whether a window is favorable.
    - Does not generate trading signals.
    - Does not make trading decisions.
    - Does not execute orders.
    - No V7+ dependency.

Relationship:
    MarketCalendar = calendar/date/event structure.
    MarketSchedule = defined market schedule rules.
    MarketSession = actual/current session lifecycle.
    MarketTiming = timing state relative to schedule/session.
    MarketWindow = explicit bounded temporal interval.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime, time
from typing import Any, Mapping, Optional


MARKET_WINDOW_SCHEMA_VERSION = "1.0.0"
MARKET_WINDOW_SCHEMA = "MARKET_WINDOW"


def _non_empty(value: Any) -> bool:
    return value is not None and str(value).strip() != ""


def _valid_time(value: Optional[time]) -> bool:
    return value is None or isinstance(value, time)


def _valid_date(value: Optional[date]) -> bool:
    return value is None or isinstance(value, date)


def _valid_datetime(value: Optional[datetime]) -> bool:
    return value is None or isinstance(value, datetime)


@dataclass(frozen=True)
class MarketWindow:
    """
    Immutable structural market time-window record.

    A window is a bounded temporal interval with explicit identity,
    market context, relationships, timing measurements, and provenance.
    """

    # ------------------------------------------------------------------
    # Window identity
    # ------------------------------------------------------------------
    window_id: Optional[str] = None
    window_type: Optional[str] = None
    window_name: Optional[str] = None
    window_state: Optional[str] = None

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
    # Calendar / schedule / session relationships
    # ------------------------------------------------------------------
    calendar_id: Optional[str] = None
    schedule_id: Optional[str] = None
    session_id: Optional[str] = None
    timing_id: Optional[str] = None
    calendar_event_id: Optional[str] = None

    calendar_date: Optional[date] = None
    trading_date: Optional[date] = None

    timezone: Optional[str] = None
    locale: Optional[str] = None

    # ------------------------------------------------------------------
    # Window boundaries - time
    # ------------------------------------------------------------------
    start_time: Optional[time] = None
    end_time: Optional[time] = None

    # ------------------------------------------------------------------
    # Window boundaries - datetime
    # ------------------------------------------------------------------
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None

    # ------------------------------------------------------------------
    # Current position inside window
    # ------------------------------------------------------------------
    current_time: Optional[time] = None
    current_datetime: Optional[datetime] = None

    # ------------------------------------------------------------------
    # Duration
    # ------------------------------------------------------------------
    duration_seconds: Optional[float] = None
    duration_minutes: Optional[float] = None

    elapsed_seconds: Optional[float] = None
    elapsed_minutes: Optional[float] = None

    remaining_seconds: Optional[float] = None
    remaining_minutes: Optional[float] = None

    elapsed_ratio: Optional[float] = None
    remaining_ratio: Optional[float] = None

    # ------------------------------------------------------------------
    # Window state
    # ------------------------------------------------------------------
    is_active: Optional[bool] = None
    is_open: Optional[bool] = None
    is_closed: Optional[bool] = None
    is_started: Optional[bool] = None
    is_completed: Optional[bool] = None

    # ------------------------------------------------------------------
    # Boundary semantics
    # ------------------------------------------------------------------
    start_inclusive: Optional[bool] = None
    end_inclusive: Optional[bool] = None

    # ------------------------------------------------------------------
    # Window classification
    # ------------------------------------------------------------------
    phase: Optional[str] = None
    phase_index: Optional[int] = None

    is_pre_open: Optional[bool] = None
    is_regular_session: Optional[bool] = None
    is_post_close: Optional[bool] = None
    is_auction: Optional[bool] = None
    is_break: Optional[bool] = None
    is_settlement: Optional[bool] = None
    is_expiry_window: Optional[bool] = None

    # ------------------------------------------------------------------
    # Special session classification
    # ------------------------------------------------------------------
    is_special_session: Optional[bool] = None
    is_short_session: Optional[bool] = None
    is_extended_session: Optional[bool] = None

    window_reason: Optional[str] = None

    # ------------------------------------------------------------------
    # Parent / neighboring windows
    # ------------------------------------------------------------------
    parent_window_id: Optional[str] = None
    previous_window_id: Optional[str] = None
    next_window_id: Optional[str] = None

    related_window_ids: tuple[str, ...] = field(
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
    # Identity
    # ------------------------------------------------------------------
    def has_window_identity(self) -> bool:
        return _non_empty(self.window_id)

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
            )
        )

    def has_timezone(self) -> bool:
        return _non_empty(self.timezone)

    # ------------------------------------------------------------------
    # Boundary availability
    # ------------------------------------------------------------------
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
            self.has_time_boundaries()
            or self.has_datetime_boundaries()
        )

    # ------------------------------------------------------------------
    # Boundary ordering
    # ------------------------------------------------------------------
    def time_boundaries_ordered(self) -> bool:
        if not self.has_time_boundaries():
            return True

        return self.start_time < self.end_time

    def datetime_boundaries_ordered(self) -> bool:
        if not self.has_datetime_boundaries():
            return True

        return self.start_datetime < self.end_datetime

    # ------------------------------------------------------------------
    # Current position
    # ------------------------------------------------------------------
    def has_current_position(self) -> bool:
        return (
            self.current_time is not None
            or self.current_datetime is not None
        )

    # ------------------------------------------------------------------
    # Duration validation
    # ------------------------------------------------------------------
    def durations_non_negative(self) -> bool:
        values = (
            self.duration_seconds,
            self.duration_minutes,
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
    # Phase validation
    # ------------------------------------------------------------------
    def phase_index_valid(self) -> bool:
        if self.phase_index is None:
            return True

        return self.phase_index >= 0

    # ------------------------------------------------------------------
    # Date / datetime validation
    # ------------------------------------------------------------------
    def date_fields_valid(self) -> bool:
        return (
            _valid_date(self.expiry)
            and _valid_date(self.calendar_date)
            and _valid_date(self.trading_date)
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

    def time_fields_valid(self) -> bool:
        return all(
            _valid_time(value)
            for value in (
                self.start_time,
                self.end_time,
                self.current_time,
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
    # Window state consistency
    # ------------------------------------------------------------------
    def state_flags_consistent(self) -> bool:
        """
        Check only obvious structural contradictions.

        This does not infer the correct state.
        """

        if self.is_open is True and self.is_closed is True:
            return False

        if self.is_completed is True and self.is_started is False:
            return False

        return True

    # ------------------------------------------------------------------
    # Boundary inclusivity consistency
    # ------------------------------------------------------------------
    def boundary_flags_valid(self) -> bool:
        if self.start_inclusive is not None:
            if not isinstance(self.start_inclusive, bool):
                return False

        if self.end_inclusive is not None:
            if not isinstance(self.end_inclusive, bool):
                return False

        return True

    # ------------------------------------------------------------------
    # Related windows
    # ------------------------------------------------------------------
    def has_parent_window(self) -> bool:
        return _non_empty(self.parent_window_id)

    def has_neighboring_windows(self) -> bool:
        return any(
            _non_empty(value)
            for value in (
                self.previous_window_id,
                self.next_window_id,
            )
        )

    def has_related_windows(self) -> bool:
        return len(self.related_window_ids) > 0

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

        if not self.has_window_identity():
            issues.append("missing_window_id")

        if not self.has_market_identity():
            issues.append("missing_market_identity")

        if not self.has_temporal_context():
            issues.append("missing_temporal_context")

        if not self.has_timezone():
            issues.append("missing_timezone")

        if not self.has_any_boundaries():
            issues.append("missing_window_boundaries")

        if not self.time_fields_valid():
            issues.append("invalid_time_field")

        if not self.datetime_fields_valid():
            issues.append("invalid_datetime_field")

        if not self.date_fields_valid():
            issues.append("invalid_date_field")

        if not self.time_boundaries_ordered():
            issues.append("invalid_time_boundary_order")

        if not self.datetime_boundaries_ordered():
            issues.append("invalid_datetime_boundary_order")

        if not self.durations_non_negative():
            issues.append("negative_duration")

        if not self.ratios_valid():
            issues.append("invalid_ratio")

        if not self.phase_index_valid():
            issues.append("invalid_phase_index")

        if not self.validity_window_valid():
            issues.append("invalid_validity_window")

        if not self.state_flags_consistent():
            issues.append("inconsistent_state_flags")

        if not self.boundary_flags_valid():
            issues.append("invalid_boundary_flags")

        if self.sequence is not None and self.sequence < 0:
            issues.append("negative_sequence")

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
            "schema": MARKET_WINDOW_SCHEMA,
            "version": MARKET_WINDOW_SCHEMA_VERSION,
            "immutable": True,
            "structural_only": True,
            "temporal_interval_only": True,
            "prediction_logic": False,
            "signal_generation": False,
            "decision_logic": False,
            "execution_logic": False,
            "v7_dependency": False,
        }


def market_window_health() -> dict[str, Any]:
    """
    Return static health information for the MarketWindow schema.
    """

    return {
        "schema": MARKET_WINDOW_SCHEMA,
        "version": MARKET_WINDOW_SCHEMA_VERSION,
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
    "MARKET_WINDOW_SCHEMA_VERSION",
    "MARKET_WINDOW_SCHEMA",
    "MarketWindow",
    "market_window_health",
]