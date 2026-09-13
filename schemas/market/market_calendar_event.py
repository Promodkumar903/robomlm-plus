"""
ROBOMLM PLUS
V6 Market Calendar Event Schema

Purpose:
Structural representation of calendar-driven market events such as
holidays, special sessions, auctions, expiry dates, settlement dates,
scheduled closures and other market-calendar events.

Rules:
- Structural schema only.
- No trading decisions.
- No execution logic.
- No risk authorization.
- No V7+ dependency.
- Immutable data representation.
- Event timing is descriptive, not predictive.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from math import isfinite
from numbers import Real
from typing import Any, Optional


@dataclass(frozen=True)
class MarketCalendarEvent:
    """
    Immutable structural representation of a market-calendar event.
    """

    # ------------------------------------------------------------------
    # Event identity
    # ------------------------------------------------------------------
    event_id: str
    event_type: str
    event_state: str = "SCHEDULED"
    event_category: Optional[str] = None
    timestamp: Optional[datetime] = None
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
    expiry: Optional[date] = None

    # ------------------------------------------------------------------
    # Calendar identity
    # ------------------------------------------------------------------
    calendar_id: Optional[str] = None
    calendar_date: Optional[date] = None
    trading_date: Optional[date] = None
    timezone: Optional[str] = None
    locale: Optional[str] = None

    # ------------------------------------------------------------------
    # Event naming
    # ------------------------------------------------------------------
    event_name: Optional[str] = None
    event_description: Optional[str] = None
    event_reason: Optional[str] = None

    # ------------------------------------------------------------------
    # Event timing
    # ------------------------------------------------------------------
    event_date: Optional[date] = None
    event_time: Optional[Any] = None
    event_timestamp: Optional[datetime] = None
    start_time: Optional[Any] = None
    end_time: Optional[Any] = None
    start_timestamp: Optional[datetime] = None
    end_timestamp: Optional[datetime] = None
    duration_seconds: Optional[float] = None

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------
    holiday_type: Optional[str] = None
    special_session_type: Optional[str] = None
    auction_type: Optional[str] = None
    expiry_type: Optional[str] = None
    settlement_type: Optional[str] = None
    closure_type: Optional[str] = None

    # ------------------------------------------------------------------
    # Effects
    # ------------------------------------------------------------------
    affects_trading: bool = False
    affects_session: bool = False
    affects_settlement: bool = False
    affects_expiry: bool = False
    market_open_affected: bool = False
    market_close_affected: bool = False
    is_holiday: bool = False
    is_special_session: bool = False
    is_expiry_event: bool = False
    is_settlement_event: bool = False

    # ------------------------------------------------------------------
    # Schedule
    # ------------------------------------------------------------------
    regular_open: Optional[Any] = None
    regular_close: Optional[Any] = None
    effective_open: Optional[Any] = None
    effective_close: Optional[Any] = None

    # ------------------------------------------------------------------
    # Expiry / contract
    # ------------------------------------------------------------------
    expiry_date: Optional[date] = None
    days_to_expiry: Optional[int] = None
    contract_month: Optional[int] = None
    contract_year: Optional[int] = None

    # ------------------------------------------------------------------
    # Sequencing
    # ------------------------------------------------------------------
    previous_event_id: Optional[str] = None
    next_event_id: Optional[str] = None
    parent_event_id: Optional[str] = None

    # ------------------------------------------------------------------
    # References
    # ------------------------------------------------------------------
    session_id: Optional[str] = None
    observation_id: Optional[str] = None
    context_id: Optional[str] = None
    regime_id: Optional[str] = None
    timing_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Environment
    # ------------------------------------------------------------------
    broker: Optional[str] = None
    provider: Optional[str] = None
    environment: Optional[str] = None
    mode: Optional[str] = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    request_id: Optional[str] = None
    lifecycle_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Provenance
    # ------------------------------------------------------------------
    source: Optional[str] = None
    source_type: Optional[str] = None
    source_reference: Optional[str] = None
    provenance: dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Observed / derived field tracking
    # ------------------------------------------------------------------
    observed_fields: tuple[str, ...] = field(default_factory=tuple)
    derived_fields: tuple[str, ...] = field(default_factory=tuple)

    # ------------------------------------------------------------------
    # Additional metadata
    # ------------------------------------------------------------------
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # --------------------------------------------------------------
        # Required identity
        # --------------------------------------------------------------
        if not isinstance(self.event_id, str) or not self.event_id.strip():
            raise ValueError("event_id must be a non-empty string")

        if not isinstance(self.event_type, str) or not self.event_type.strip():
            raise ValueError("event_type must be a non-empty string")

        # --------------------------------------------------------------
        # Sequence
        # --------------------------------------------------------------
        if self.sequence is not None:
            if isinstance(self.sequence, bool):
                raise TypeError("sequence must be an integer or None")
            if not isinstance(self.sequence, int):
                raise TypeError("sequence must be an integer or None")
            if self.sequence < 0:
                raise ValueError("sequence must be non-negative")

        # --------------------------------------------------------------
        # Duration
        # --------------------------------------------------------------
        if self.duration_seconds is not None:
            if isinstance(self.duration_seconds, bool):
                raise TypeError("duration_seconds must be a real number or None")
            if not isinstance(self.duration_seconds, Real):
                raise TypeError("duration_seconds must be a real number or None")
            if not isfinite(float(self.duration_seconds)):
                raise ValueError("duration_seconds must be finite")
            if self.duration_seconds < 0:
                raise ValueError("duration_seconds must be non-negative")

        # --------------------------------------------------------------
        # Days to expiry
        # --------------------------------------------------------------
        if self.days_to_expiry is not None:
            if isinstance(self.days_to_expiry, bool):
                raise TypeError("days_to_expiry must be an integer or None")
            if not isinstance(self.days_to_expiry, int):
                raise TypeError("days_to_expiry must be an integer or None")
            if self.days_to_expiry < 0:
                raise ValueError("days_to_expiry must be non-negative")

        # --------------------------------------------------------------
        # Contract year
        # --------------------------------------------------------------
        if self.contract_year is not None:
            if isinstance(self.contract_year, bool):
                raise TypeError("contract_year must be an integer or None")
            if not isinstance(self.contract_year, int):
                raise TypeError("contract_year must be an integer or None")

        # --------------------------------------------------------------
        # Contract month
        # --------------------------------------------------------------
        if self.contract_month is not None:
            if isinstance(self.contract_month, bool):
                raise TypeError("contract_month must be an integer or None")
            if not isinstance(self.contract_month, int):
                raise TypeError("contract_month must be an integer or None")
            if not 1 <= self.contract_month <= 12:
                raise ValueError("contract_month must be within 1..12")

        # --------------------------------------------------------------
        # Boolean effect fields
        # --------------------------------------------------------------
        boolean_fields = (
            "affects_trading",
            "affects_session",
            "affects_settlement",
            "affects_expiry",
            "market_open_affected",
            "market_close_affected",
            "is_holiday",
            "is_special_session",
            "is_expiry_event",
            "is_settlement_event",
        )

        for field_name in boolean_fields:
            value = getattr(self, field_name)
            if not isinstance(value, bool):
                raise TypeError(f"{field_name} must be a boolean")

        # --------------------------------------------------------------
        # Mapping fields
        # --------------------------------------------------------------
        if not isinstance(self.provenance, dict):
            raise TypeError("provenance must be a dictionary")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary")

        # --------------------------------------------------------------
        # Field collections
        # --------------------------------------------------------------
        if not isinstance(self.observed_fields, tuple):
            raise TypeError("observed_fields must be a tuple")

        if not isinstance(self.derived_fields, tuple):
            raise TypeError("derived_fields must be a tuple")

        for field_name in ("observed_fields", "derived_fields"):
            values = getattr(self, field_name)
            for value in values:
                if not isinstance(value, str) or not value.strip():
                    raise ValueError(
                        f"{field_name} must contain only non-empty strings"
                    )

    # ------------------------------------------------------------------
    # Identity helpers
    # ------------------------------------------------------------------

    def identity(self) -> str:
        return self.event_id

    def has_identity(self) -> bool:
        return bool(self.event_id and self.event_type)

    # ------------------------------------------------------------------
    # Classification helpers
    # ------------------------------------------------------------------

    def classification(self) -> Optional[str]:
        return self.event_category

    def is_calendar_event(self) -> bool:
        return True

    def is_scheduled(self) -> bool:
        return self.event_state.upper() == "SCHEDULED"

    def is_active(self) -> bool:
        return self.event_state.upper() == "ACTIVE"

    def is_completed(self) -> bool:
        return self.event_state.upper() in {"COMPLETED", "CLOSED", "ENDED"}

    # ------------------------------------------------------------------
    # Timing helpers
    # ------------------------------------------------------------------

    def has_timing(self) -> bool:
        return any(
            value is not None
            for value in (
                self.timestamp,
                self.event_timestamp,
                self.start_timestamp,
                self.end_timestamp,
                self.start_time,
                self.end_time,
                self.event_time,
            )
        )

    def has_duration(self) -> bool:
        return self.duration_seconds is not None

    def calculated_duration_seconds(self) -> Optional[float]:
        if self.duration_seconds is not None:
            return float(self.duration_seconds)

        if self.start_timestamp is not None and self.end_timestamp is not None:
            seconds = (
                self.end_timestamp - self.start_timestamp
            ).total_seconds()

            if seconds < 0:
                return None

            return float(seconds)

        return None

    # ------------------------------------------------------------------
    # Effect helpers
    # ------------------------------------------------------------------

    def affects_market(self) -> bool:
        return any(
            (
                self.affects_trading,
                self.affects_session,
                self.affects_settlement,
                self.affects_expiry,
                self.market_open_affected,
                self.market_close_affected,
            )
        )

    def is_market_closure(self) -> bool:
        return (
            self.closure_type is not None
            or (
                self.affects_trading
                and self.is_holiday
                and not self.is_special_session
            )
        )

    # ------------------------------------------------------------------
    # Category helpers
    # ------------------------------------------------------------------

    def category_flags(self) -> dict[str, bool]:
        return {
            "holiday": self.is_holiday,
            "special_session": self.is_special_session,
            "expiry": self.is_expiry_event,
            "settlement": self.is_settlement_event,
            "auction": self.auction_type is not None,
            "closure": self.closure_type is not None,
        }

    # ------------------------------------------------------------------
    # Expiry helpers
    # ------------------------------------------------------------------

    def has_expiry(self) -> bool:
        return (
            self.expiry_date is not None
            or self.expiry is not None
            or self.is_expiry_event
        )

    def expiry_reference(self) -> Optional[date]:
        return self.expiry_date or self.expiry

    # ------------------------------------------------------------------
    # Schedule helpers
    # ------------------------------------------------------------------

    def has_regular_schedule(self) -> bool:
        return self.regular_open is not None or self.regular_close is not None

    def has_effective_schedule(self) -> bool:
        return self.effective_open is not None or self.effective_close is not None

    def effective_schedule_changed(self) -> bool:
        return (
            self.effective_open != self.regular_open
            or self.effective_close != self.regular_close
        )

    # ------------------------------------------------------------------
    # Reference helpers
    # ------------------------------------------------------------------

    def references(self) -> dict[str, Optional[str]]:
        return {
            "session_id": self.session_id,
            "observation_id": self.observation_id,
            "context_id": self.context_id,
            "regime_id": self.regime_id,
            "timing_id": self.timing_id,
            "previous_event_id": self.previous_event_id,
            "next_event_id": self.next_event_id,
            "parent_event_id": self.parent_event_id,
        }

    # ------------------------------------------------------------------
    # Structural validation
    # ------------------------------------------------------------------

    def is_structurally_valid(self) -> bool:
        return len(self.issue_flags()) == 0

    def issue_flags(self) -> list[str]:
        issues: list[str] = []

        if not self.event_id.strip():
            issues.append("missing_event_id")

        if not self.event_type.strip():
            issues.append("missing_event_type")

        if self.timezone is None:
            issues.append("missing_timezone")

        if self.is_holiday and self.is_special_session:
            if not self.special_session_type:
                issues.append("special_session_type_missing")

        if self.affects_trading and self.is_holiday and not self.is_special_session:
            issues.append("holiday_marked_trading_without_special_session")

        if self.is_holiday and self.calendar_date is not None:
            if self.calendar_date.weekday() >= 5 and self.affects_trading:
                issues.append("holiday_weekend_marked_as_trading_day")

        if self.expiry_date is not None and self.days_to_expiry is not None:
            if self.days_to_expiry < 0:
                issues.append("expiry_day_with_negative_days_to_expiry")

        if self.is_expiry_event and self.expiry_reference() is None:
            issues.append("expiry_event_without_expiry_date")

        if self.is_settlement_event and not self.settlement_type:
            issues.append("settlement_event_without_settlement_type")

        if self.is_special_session and not self.special_session_type:
            issues.append("special_session_type_missing")

        if self.closure_type is not None and not self.affects_trading:
            issues.append("closure_without_trading_effect")

        if (
            self.start_timestamp is not None
            and self.end_timestamp is not None
            and self.end_timestamp < self.start_timestamp
        ):
            issues.append("end_before_start")

        return issues

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)

        for key in (
            "timestamp",
            "event_timestamp",
            "start_timestamp",
            "end_timestamp",
        ):
            value = data.get(key)
            if isinstance(value, datetime):
                data[key] = value.isoformat()

        for key in (
            "expiry",
            "calendar_date",
            "trading_date",
            "event_date",
            "expiry_date",
        ):
            value = data.get(key)
            if isinstance(value, date):
                data[key] = value.isoformat()

        return data

    # ------------------------------------------------------------------
    # Schema metadata
    # ------------------------------------------------------------------

    @classmethod
    def schema_info(cls) -> dict[str, Any]:
        return {
            "name": cls.__name__,
            "version": "V6",
            "purpose": "Structural market calendar event representation",
            "decision_authority": False,
            "execution_authority": False,
            "risk_authority": False,
            "predictive": False,
            "immutable": True,
        }


def market_calendar_event_health() -> dict[str, Any]:
    """
    Lightweight structural health check.
    """
    try:
        event = MarketCalendarEvent(
            event_id="HEALTH-001",
            event_type="HEALTH_CHECK",
            event_state="SCHEDULED",
            timezone="UTC",
            source="health_check",
            source_type="internal",
        )

        return {
            "status": "PASS",
            "schema": "MarketCalendarEvent",
            "structurally_valid": event.is_structurally_valid(),
            "issue_flags": event.issue_flags(),
        }
    except Exception as exc:
        return {
            "status": "FAIL",
            "schema": "MarketCalendarEvent",
            "error": f"{type(exc).__name__}: {exc}",
        }


__all__ = [
    "MarketCalendarEvent",
    "market_calendar_event_health",
]