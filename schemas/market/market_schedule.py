"""
ROBOMLM PLUS
Market Schedule Schema

Purpose:
    Immutable structural representation of market schedule rules
    and effective trading schedules.

Design:
    - Structural and descriptive only.
    - Distinct from MarketCalendar:
        MarketCalendar = calendar/date/day/event state.
    - Distinct from MarketSession:
        MarketSession = actual/current session lifecycle state.
    - MarketSchedule = defined schedule rules and effective time windows.
    - No prediction.
    - No trading decision.
    - No execution logic.
    - No V7+ dependency.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime, time
from typing import Any, Mapping, Optional


MARKET_SCHEDULE_SCHEMA_VERSION = "1.0.0"
MARKET_SCHEDULE_SCHEMA = "MARKET_SCHEDULE"


def _non_empty(value: Any) -> bool:
    return value is not None and str(value).strip() != ""


def _valid_time(value: Optional[time]) -> bool:
    return value is None or isinstance(value, time)


def _valid_date(value: Optional[date]) -> bool:
    return value is None or isinstance(value, date)


def _valid_datetime(value: Optional[datetime]) -> bool:
    return value is None or isinstance(value, datetime)


@dataclass(frozen=True)
class MarketSchedule:
    """
    Immutable structural market schedule.

    This schema describes when a market or instrument is scheduled
    to operate, including regular hours, pre/post sessions, auctions,
    breaks, special-session overrides, and schedule validity.

    It does not determine whether a trade should occur.
    """

    # ------------------------------------------------------------------
    # Schedule identity
    # ------------------------------------------------------------------
    schedule_id: Optional[str] = None
    schedule_type: Optional[str] = None
    schedule_state: Optional[str] = None

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
    # Calendar relationship
    # ------------------------------------------------------------------
    calendar_id: Optional[str] = None
    calendar_date: Optional[date] = None
    trading_date: Optional[date] = None
    timezone: Optional[str] = None
    locale: Optional[str] = None

    # ------------------------------------------------------------------
    # Regular session
    # ------------------------------------------------------------------
    regular_open: Optional[time] = None
    regular_close: Optional[time] = None

    # ------------------------------------------------------------------
    # Pre-market / pre-open
    # ------------------------------------------------------------------
    pre_open_start: Optional[time] = None
    pre_open_end: Optional[time] = None

    # ------------------------------------------------------------------
    # Post-market / post-close
    # ------------------------------------------------------------------
    post_close_start: Optional[time] = None
    post_close_end: Optional[time] = None

    # ------------------------------------------------------------------
    # Auction windows
    # ------------------------------------------------------------------
    auction_open_start: Optional[time] = None
    auction_open_end: Optional[time] = None
    auction_close_start: Optional[time] = None
    auction_close_end: Optional[time] = None

    # ------------------------------------------------------------------
    # Break window
    # ------------------------------------------------------------------
    break_start: Optional[time] = None
    break_end: Optional[time] = None

    additional_breaks: tuple[Mapping[str, Any], ...] = field(
        default_factory=tuple
    )

    # ------------------------------------------------------------------
    # Effective schedule
    # ------------------------------------------------------------------
    effective_open: Optional[time] = None
    effective_close: Optional[time] = None

    effective_open_datetime: Optional[datetime] = None
    effective_close_datetime: Optional[datetime] = None

    # ------------------------------------------------------------------
    # Duration information
    # ------------------------------------------------------------------
    regular_duration_minutes: Optional[float] = None
    effective_duration_minutes: Optional[float] = None
    pre_open_duration_minutes: Optional[float] = None
    post_close_duration_minutes: Optional[float] = None

    # ------------------------------------------------------------------
    # Day-specific rules
    # ------------------------------------------------------------------
    weekday: Optional[int] = None
    weekday_name: Optional[str] = None
    is_weekday_schedule: Optional[bool] = None
    is_weekend_schedule: Optional[bool] = None

    # ------------------------------------------------------------------
    # Special schedule conditions
    # ------------------------------------------------------------------
    is_holiday_override: Optional[bool] = None
    is_special_session: Optional[bool] = None
    is_short_session: Optional[bool] = None
    is_extended_session: Optional[bool] = None

    special_session_reason: Optional[str] = None
    holiday_reference: Optional[str] = None
    special_session_reference: Optional[str] = None

    # ------------------------------------------------------------------
    # Schedule validity window
    # ------------------------------------------------------------------
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None

    # ------------------------------------------------------------------
    # Schedule relationships
    # ------------------------------------------------------------------
    previous_schedule_id: Optional[str] = None
    next_schedule_id: Optional[str] = None
    parent_schedule_id: Optional[str] = None

    session_id: Optional[str] = None
    calendar_event_id: Optional[str] = None
    timing_id: Optional[str] = None

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

    observed_fields: tuple[str, ...] = field(default_factory=tuple)
    derived_fields: tuple[str, ...] = field(default_factory=tuple)

    metadata: Mapping[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Identity validation
    # ------------------------------------------------------------------
    def has_schedule_identity(self) -> bool:
        return _non_empty(self.schedule_id)

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

    def has_calendar_identity(self) -> bool:
        return any(
            value is not None
            for value in (
                self.calendar_id,
                self.calendar_date,
                self.trading_date,
            )
        )

    def has_timezone(self) -> bool:
        return _non_empty(self.timezone)

    # ------------------------------------------------------------------
    # Regular schedule validation
    # ------------------------------------------------------------------
    def has_regular_schedule(self) -> bool:
        return (
            self.regular_open is not None
            and self.regular_close is not None
        )

    def has_effective_schedule(self) -> bool:
        return (
            self.effective_open is not None
            and self.effective_close is not None
        )

    def regular_schedule_ordered(self) -> bool:
        if not self.has_regular_schedule():
            return True
        return self.regular_open < self.regular_close

    def effective_schedule_ordered(self) -> bool:
        if not self.has_effective_schedule():
            return True
        return self.effective_open < self.effective_close

    # ------------------------------------------------------------------
    # Pre / post session checks
    # ------------------------------------------------------------------
    def has_pre_open_window(self) -> bool:
        return (
            self.pre_open_start is not None
            and self.pre_open_end is not None
        )

    def has_post_close_window(self) -> bool:
        return (
            self.post_close_start is not None
            and self.post_close_end is not None
        )

    def pre_open_ordered(self) -> bool:
        if not self.has_pre_open_window():
            return True
        return self.pre_open_start < self.pre_open_end

    def post_close_ordered(self) -> bool:
        if not self.has_post_close_window():
            return True
        return self.post_close_start < self.post_close_end

    # ------------------------------------------------------------------
    # Auction checks
    # ------------------------------------------------------------------
    def has_open_auction(self) -> bool:
        return (
            self.auction_open_start is not None
            and self.auction_open_end is not None
        )

    def has_close_auction(self) -> bool:
        return (
            self.auction_close_start is not None
            and self.auction_close_end is not None
        )

    def auction_windows_ordered(self) -> bool:
        open_ok = (
            not self.has_open_auction()
            or self.auction_open_start < self.auction_open_end
        )

        close_ok = (
            not self.has_close_auction()
            or self.auction_close_start < self.auction_close_end
        )

        return open_ok and close_ok

    # ------------------------------------------------------------------
    # Break checks
    # ------------------------------------------------------------------
    def has_break(self) -> bool:
        return (
            self.break_start is not None
            and self.break_end is not None
        )

    def break_ordered(self) -> bool:
        if not self.has_break():
            return True
        return self.break_start < self.break_end

    # ------------------------------------------------------------------
    # Validity window
    # ------------------------------------------------------------------
    def validity_window_valid(self) -> bool:
        if self.valid_from is None or self.valid_until is None:
            return True

        return self.valid_from <= self.valid_until

    def applies_to_date(self, target_date: Optional[date]) -> bool:
        if target_date is None:
            return False

        if self.valid_from is not None and target_date < self.valid_from:
            return False

        if self.valid_until is not None and target_date > self.valid_until:
            return False

        return True

    # ------------------------------------------------------------------
    # Date / weekday checks
    # ------------------------------------------------------------------
    def weekday_valid(self) -> bool:
        if self.weekday is None:
            return True

        return 0 <= self.weekday <= 6

    def calendar_date_weekday_matches(self) -> bool:
        if self.calendar_date is None or self.weekday is None:
            return True

        return self.calendar_date.weekday() == self.weekday

    # ------------------------------------------------------------------
    # Duration checks
    # ------------------------------------------------------------------
    def durations_non_negative(self) -> bool:
        durations = (
            self.regular_duration_minutes,
            self.effective_duration_minutes,
            self.pre_open_duration_minutes,
            self.post_close_duration_minutes,
        )

        return all(
            value is None or value >= 0
            for value in durations
        )

    # ------------------------------------------------------------------
    # Datetime type checks
    # ------------------------------------------------------------------
    def datetime_fields_valid(self) -> bool:
        return (
            _valid_datetime(self.timestamp)
            and _valid_datetime(self.effective_open_datetime)
            and _valid_datetime(self.effective_close_datetime)
        )

    def date_fields_valid(self) -> bool:
        return (
            _valid_date(self.expiry)
            and _valid_date(self.calendar_date)
            and _valid_date(self.trading_date)
            and _valid_date(self.valid_from)
            and _valid_date(self.valid_until)
        )

    def time_fields_valid(self) -> bool:
        values = (
            self.regular_open,
            self.regular_close,
            self.pre_open_start,
            self.pre_open_end,
            self.post_close_start,
            self.post_close_end,
            self.auction_open_start,
            self.auction_open_end,
            self.auction_close_start,
            self.auction_close_end,
            self.break_start,
            self.break_end,
            self.effective_open,
            self.effective_close,
        )

        return all(_valid_time(value) for value in values)

    # ------------------------------------------------------------------
    # Relationship checks
    # ------------------------------------------------------------------
    def has_related_schedule(self) -> bool:
        return any(
            _non_empty(value)
            for value in (
                self.previous_schedule_id,
                self.next_schedule_id,
                self.parent_schedule_id,
            )
        )

    def has_related_context(self) -> bool:
        return any(
            _non_empty(value)
            for value in (
                self.session_id,
                self.calendar_event_id,
                self.timing_id,
            )
        )

    # ------------------------------------------------------------------
    # Provenance checks
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

        if not self.has_schedule_identity():
            issues.append("missing_schedule_id")

        if not self.has_market_identity():
            issues.append("missing_market_identity")

        if not self.has_calendar_identity():
            issues.append("missing_calendar_identity")

        if not self.has_timezone():
            issues.append("missing_timezone")

        if not self.time_fields_valid():
            issues.append("invalid_time_field")

        if not self.date_fields_valid():
            issues.append("invalid_date_field")

        if not self.datetime_fields_valid():
            issues.append("invalid_datetime_field")

        if not self.weekday_valid():
            issues.append("invalid_weekday")

        if not self.calendar_date_weekday_matches():
            issues.append("calendar_weekday_mismatch")

        if not self.regular_schedule_ordered():
            issues.append("invalid_regular_schedule_order")

        if not self.effective_schedule_ordered():
            issues.append("invalid_effective_schedule_order")

        if not self.pre_open_ordered():
            issues.append("invalid_pre_open_order")

        if not self.post_close_ordered():
            issues.append("invalid_post_close_order")

        if not self.auction_windows_ordered():
            issues.append("invalid_auction_order")

        if not self.break_ordered():
            issues.append("invalid_break_order")

        if not self.validity_window_valid():
            issues.append("invalid_validity_window")

        if not self.durations_non_negative():
            issues.append("negative_duration")

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
            "schema": MARKET_SCHEDULE_SCHEMA,
            "version": MARKET_SCHEDULE_SCHEMA_VERSION,
            "immutable": True,
            "structural_only": True,
            "prediction_logic": False,
            "decision_logic": False,
            "execution_logic": False,
            "v7_dependency": False,
        }


def market_schedule_health() -> dict[str, Any]:
    """
    Return static health information for the MarketSchedule schema.
    """

    return {
        "schema": MARKET_SCHEDULE_SCHEMA,
        "version": MARKET_SCHEDULE_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "structural_only": True,
        "prediction_logic": False,
        "decision_logic": False,
        "execution_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_SCHEDULE_SCHEMA_VERSION",
    "MARKET_SCHEDULE_SCHEMA",
    "MarketSchedule",
    "market_schedule_health",
]