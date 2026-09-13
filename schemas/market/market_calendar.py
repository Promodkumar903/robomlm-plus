"""
ROBOMLM PLUS
V6 Market Calendar Schema

Purpose:
    Structural representation of market calendar, trading-day,
    holiday, session-window and schedule information.

Rules:
    - Structural schema only.
    - No trading decisions.
    - No execution logic.
    - No risk authorization.
    - No V7+ dependency.
    - Immutable data representation.
    - Calendar information is descriptive, not predictive.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from math import isfinite
from numbers import Real
from typing import Any, Optional


MARKET_CALENDAR_SCHEMA_VERSION = "1.0.0"
MARKET_CALENDAR_SCHEMA = "V6_MARKET_CALENDAR"


@dataclass(frozen=True)
class MarketCalendar:
    """
    Immutable structural representation of a market calendar state.
    """

    # ------------------------------------------------------------------
    # Calendar identity
    # ------------------------------------------------------------------
    calendar_id: Optional[str] = None
    calendar_type: Optional[str] = None
    calendar_state: Optional[str] = None

    timestamp: Optional[str] = None
    sequence: Optional[int] = None

    # ------------------------------------------------------------------
    # Market identity
    # ------------------------------------------------------------------
    market: Optional[str] = None
    instrument: Optional[str] = None
    symbol: Optional[str] = None
    exchange: Optional[str] = None
    venue: Optional[str] = None
    contract: Optional[str] = None
    expiry: Optional[str] = None

    # ------------------------------------------------------------------
    # Date / timezone identity
    # ------------------------------------------------------------------
    calendar_date: Optional[str] = None
    trading_date: Optional[str] = None
    timezone: Optional[str] = None
    locale: Optional[str] = None

    # ------------------------------------------------------------------
    # Trading-day state
    # ------------------------------------------------------------------
    is_trading_day: Optional[bool] = None
    is_holiday: Optional[bool] = None
    is_weekend: Optional[bool] = None
    is_special_session: Optional[bool] = None
    is_expiry_day: Optional[bool] = None

    # ------------------------------------------------------------------
    # Holiday / special-day information
    # ------------------------------------------------------------------
    holiday_name: Optional[str] = None
    holiday_type: Optional[str] = None
    special_day_name: Optional[str] = None
    special_day_type: Optional[str] = None

    # ------------------------------------------------------------------
    # Regular trading schedule
    # ------------------------------------------------------------------
    regular_open: Optional[str] = None
    regular_close: Optional[str] = None

    pre_open: Optional[str] = None
    post_close: Optional[str] = None

    # ------------------------------------------------------------------
    # Actual session schedule
    # ------------------------------------------------------------------
    session_open: Optional[str] = None
    session_close: Optional[str] = None

    session_open_timestamp: Optional[str] = None
    session_close_timestamp: Optional[str] = None

    # ------------------------------------------------------------------
    # Break / auction windows
    # ------------------------------------------------------------------
    auction_open: Optional[str] = None
    auction_close: Optional[str] = None

    break_start: Optional[str] = None
    break_end: Optional[str] = None

    # ------------------------------------------------------------------
    # Schedule measurements
    # ------------------------------------------------------------------
    scheduled_duration_seconds: Optional[float] = None
    actual_duration_seconds: Optional[float] = None

    # ------------------------------------------------------------------
    # Session classification
    # ------------------------------------------------------------------
    session_type: Optional[str] = None
    session_phase: Optional[str] = None
    trading_period: Optional[str] = None

    # ------------------------------------------------------------------
    # Calendar sequencing
    # ------------------------------------------------------------------
    previous_trading_date: Optional[str] = None
    next_trading_date: Optional[str] = None

    previous_calendar_id: Optional[str] = None
    next_calendar_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Contract / expiry context
    # ------------------------------------------------------------------
    expiry_type: Optional[str] = None
    expiry_date: Optional[str] = None
    days_to_expiry: Optional[int] = None

    # ------------------------------------------------------------------
    # Environment
    # ------------------------------------------------------------------
    broker: Optional[str] = None
    provider: Optional[str] = None
    environment: Optional[str] = None
    mode: Optional[str] = None

    # ------------------------------------------------------------------
    # Related references
    # ------------------------------------------------------------------
    session_id: Optional[str] = None
    observation_id: Optional[str] = None
    context_id: Optional[str] = None
    regime_id: Optional[str] = None
    transaction_id: Optional[str] = None
    request_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Provenance
    # ------------------------------------------------------------------
    source: Optional[str] = None
    source_type: Optional[str] = None
    source_reference: Optional[str] = None

    provenance: dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Observed / derived tracking
    # ------------------------------------------------------------------
    observed_fields: tuple[str, ...] = field(default_factory=tuple)
    derived_fields: tuple[str, ...] = field(default_factory=tuple)

    # ------------------------------------------------------------------
    # Additional metadata
    # ------------------------------------------------------------------
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # --------------------------------------------------------------
        # Sequence validation
        # --------------------------------------------------------------
        if self.sequence is not None:
            if isinstance(self.sequence, bool) or not isinstance(
                self.sequence, int
            ):
                raise TypeError(
                    "sequence must be an integer when provided"
                )

            if self.sequence < 0:
                raise ValueError(
                    "sequence cannot be negative"
                )

        # --------------------------------------------------------------
        # Schedule duration validation
        # --------------------------------------------------------------
        duration_fields = (
            "scheduled_duration_seconds",
            "actual_duration_seconds",
        )

        for field_name in duration_fields:
            value = getattr(self, field_name)

            if value is None:
                continue

            if isinstance(value, bool) or not isinstance(value, Real):
                raise TypeError(
                    f"{field_name} must be numeric when provided"
                )

            numeric_value = float(value)

            if not isfinite(numeric_value):
                raise ValueError(
                    f"{field_name} must be finite when provided"
                )

            if numeric_value < 0:
                raise ValueError(
                    f"{field_name} cannot be negative"
                )

        # --------------------------------------------------------------
        # Expiry sequencing validation
        # --------------------------------------------------------------
        if self.days_to_expiry is not None:
            if isinstance(self.days_to_expiry, bool) or not isinstance(
                self.days_to_expiry, int
            ):
                raise TypeError(
                    "days_to_expiry must be an integer"
                )

        # --------------------------------------------------------------
        # Boolean state validation
        # --------------------------------------------------------------
        boolean_fields = (
            "is_trading_day",
            "is_holiday",
            "is_weekend",
            "is_special_session",
            "is_expiry_day",
        )

        for field_name in boolean_fields:
            value = getattr(self, field_name)

            if value is not None and not isinstance(value, bool):
                raise TypeError(
                    f"{field_name} must be a boolean when provided"
                )

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------
    def has_identity(self) -> bool:
        return bool(self.calendar_id)

    def has_market_identity(self) -> bool:
        return bool(
            self.market
            or self.instrument
            or self.symbol
            or self.exchange
            or self.venue
            or self.contract
        )

    def has_date_identity(self) -> bool:
        return bool(
            self.calendar_date
            or self.trading_date
        )

    def has_timezone(self) -> bool:
        return bool(self.timezone)

    # ------------------------------------------------------------------
    # Trading-day state
    # ------------------------------------------------------------------
    def has_trading_day_state(self) -> bool:
        return any(
            value is not None
            for value in (
                self.is_trading_day,
                self.is_holiday,
                self.is_weekend,
                self.is_special_session,
            )
        )

    def is_trading(self) -> bool:
        return self.is_trading_day is True

    def is_non_trading(self) -> bool:
        return (
            self.is_trading_day is False
            or self.is_holiday is True
            or self.is_weekend is True
        )

    # ------------------------------------------------------------------
    # Schedule availability
    # ------------------------------------------------------------------
    def has_regular_schedule(self) -> bool:
        return bool(
            self.regular_open
            or self.regular_close
        )

    def has_session_schedule(self) -> bool:
        return bool(
            self.session_open
            or self.session_close
        )

    def has_auction_window(self) -> bool:
        return bool(
            self.auction_open
            or self.auction_close
        )

    def has_break_window(self) -> bool:
        return bool(
            self.break_start
            or self.break_end
        )

    # ------------------------------------------------------------------
    # Holiday / special session
    # ------------------------------------------------------------------
    def has_holiday_information(self) -> bool:
        return bool(
            self.holiday_name
            or self.holiday_type
        )

    def has_special_day_information(self) -> bool:
        return bool(
            self.special_day_name
            or self.special_day_type
        )

    # ------------------------------------------------------------------
    # Duration
    # ------------------------------------------------------------------
    def has_scheduled_duration(self) -> bool:
        return self.scheduled_duration_seconds is not None

    def has_actual_duration(self) -> bool:
        return self.actual_duration_seconds is not None

    # ------------------------------------------------------------------
    # Expiry
    # ------------------------------------------------------------------
    def has_expiry_information(self) -> bool:
        return bool(
            self.expiry
            or self.expiry_date
            or self.expiry_type
            or self.is_expiry_day is not None
        )

    def has_days_to_expiry(self) -> bool:
        return self.days_to_expiry is not None

    # ------------------------------------------------------------------
    # Calendar calculations
    # ------------------------------------------------------------------
    def calculate_schedule_duration_seconds(
        self,
        open_seconds: Optional[float] = None,
        close_seconds: Optional[float] = None,
    ) -> Optional[float]:
        """
        Calculate schedule duration from externally normalized
        time-of-day seconds.

        This method intentionally does not parse timezone-sensitive
        datetime strings.
        """

        if open_seconds is None or close_seconds is None:
            return None

        for field_name, value in (
            ("open_seconds", open_seconds),
            ("close_seconds", close_seconds),
        ):
            if isinstance(value, bool) or not isinstance(value, Real):
                raise TypeError(
                    f"{field_name} must be numeric when provided"
                )

            if not isfinite(float(value)):
                raise ValueError(
                    f"{field_name} must be finite when provided"
                )

        duration = float(close_seconds) - float(open_seconds)

        if duration < 0:
            duration += 24 * 60 * 60

        return duration

    # ------------------------------------------------------------------
    # Sequencing
    # ------------------------------------------------------------------
    def has_previous_trading_date(self) -> bool:
        return bool(self.previous_trading_date)

    def has_next_trading_date(self) -> bool:
        return bool(self.next_trading_date)

    def has_previous_calendar(self) -> bool:
        return bool(self.previous_calendar_id)

    def has_next_calendar(self) -> bool:
        return bool(self.next_calendar_id)

    # ------------------------------------------------------------------
    # Environment
    # ------------------------------------------------------------------
    def has_environment_identity(self) -> bool:
        return bool(
            self.broker
            or self.provider
            or self.environment
            or self.mode
        )

    # ------------------------------------------------------------------
    # Related references
    # ------------------------------------------------------------------
    def has_session_reference(self) -> bool:
        return bool(self.session_id)

    def has_observation_reference(self) -> bool:
        return bool(self.observation_id)

    def has_context_reference(self) -> bool:
        return bool(self.context_id)

    def has_regime_reference(self) -> bool:
        return bool(self.regime_id)

    def has_transaction_reference(self) -> bool:
        return bool(self.transaction_id)

    def has_request_reference(self) -> bool:
        return bool(self.request_id)

    # ------------------------------------------------------------------
    # Provenance
    # ------------------------------------------------------------------
    def has_source_reference(self) -> bool:
        return bool(
            self.source
            or self.source_type
            or self.source_reference
        )

    # ------------------------------------------------------------------
    # Observed / derived
    # ------------------------------------------------------------------
    def observed_field_names(self) -> tuple[str, ...]:
        return tuple(self.observed_fields)

    def derived_field_names(self) -> tuple[str, ...]:
        return tuple(self.derived_fields)

    # ------------------------------------------------------------------
    # Structural diagnostics
    # ------------------------------------------------------------------
    def issue_flags(self) -> list[str]:
        issues: list[str] = []

        if not self.has_identity():
            issues.append("missing_calendar_id")

        if self.timestamp is None:
            issues.append("missing_timestamp")

        if not self.has_market_identity():
            issues.append("missing_market_identity")

        if not self.has_date_identity():
            issues.append("missing_calendar_date")

        if not self.has_timezone():
            issues.append("missing_timezone")

        if (
            self.is_holiday is True
            and self.is_weekend is True
            and self.is_trading_day is True
        ):
            issues.append(
                "holiday_weekend_marked_as_trading_day"
            )

        if (
            self.is_trading_day is True
            and self.is_holiday is True
            and self.is_special_session is not True
        ):
            issues.append(
                "holiday_marked_trading_without_special_session"
            )

        if (
            self.days_to_expiry is not None
            and self.days_to_expiry < 0
            and self.is_expiry_day is True
        ):
            issues.append(
                "expiry_day_with_negative_days_to_expiry"
            )

        if (
            self.scheduled_duration_seconds is not None
            and self.actual_duration_seconds is not None
            and self.actual_duration_seconds < 0
        ):
            issues.append("negative_actual_session_duration")

        return issues

    def is_structurally_valid(self) -> bool:
        return not self.issue_flags()

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)

        data["observed_fields"] = list(self.observed_fields)
        data["derived_fields"] = list(self.derived_fields)

        return data

    def schema_info(self) -> dict[str, str]:
        return {
            "schema": MARKET_CALENDAR_SCHEMA,
            "version": MARKET_CALENDAR_SCHEMA_VERSION,
        }


# ----------------------------------------------------------------------
# Health
# ----------------------------------------------------------------------
def market_calendar_health() -> dict[str, Any]:
    return {
        "layer": MARKET_CALENDAR_SCHEMA,
        "version": MARKET_CALENDAR_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "structural_only": True,
        "decision_logic": False,
        "execution_logic": False,
        "v7_dependency": False,
        "supports_trading_day_state": True,
        "supports_holiday_state": True,
        "supports_session_schedule": True,
        "supports_auction_window": True,
        "supports_break_window": True,
        "supports_expiry_context": True,
        "supports_timezone_identity": True,
    }


__all__ = [
    "MARKET_CALENDAR_SCHEMA_VERSION",
    "MARKET_CALENDAR_SCHEMA",
    "MarketCalendar",
    "market_calendar_health",
]