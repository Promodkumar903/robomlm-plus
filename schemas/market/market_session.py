"""
ROBOMLM PLUS
V6 Market Session Schema

Purpose:
    Structural representation of a market session and its lifecycle.

Rules:
    - Structural schema only.
    - No trading decisions.
    - No execution logic.
    - No risk authorization.
    - No V7+ dependency.
    - Immutable data representation.
    - Supports exchange, market, instrument, venue and session identity.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional


MARKET_SESSION_SCHEMA_VERSION = "1.0.0"
MARKET_SESSION_SCHEMA = "V6_MARKET_SESSION"


@dataclass(frozen=True)
class MarketSession:
    """
    Immutable structural representation of a market session.
    """

    # ------------------------------------------------------------------
    # Session identity
    # ------------------------------------------------------------------
    session_id: Optional[str] = None
    session_type: Optional[str] = None
    session_state: Optional[str] = None
    session_phase: Optional[str] = None

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
    # Session timing
    # ------------------------------------------------------------------
    session_date: Optional[str] = None
    timezone: Optional[str] = None

    scheduled_open: Optional[str] = None
    scheduled_close: Optional[str] = None

    actual_open: Optional[str] = None
    actual_close: Optional[str] = None

    current_time: Optional[str] = None

    elapsed_seconds: Optional[float] = None
    remaining_seconds: Optional[float] = None
    duration_seconds: Optional[float] = None

    # ------------------------------------------------------------------
    # Session flags
    # ------------------------------------------------------------------
    is_open: Optional[bool] = None
    is_closed: Optional[bool] = None
    is_pre_open: Optional[bool] = None
    is_post_close: Optional[bool] = None
    is_halted: Optional[bool] = None

    # ------------------------------------------------------------------
    # Session classification
    # ------------------------------------------------------------------
    trading_day: Optional[str] = None
    trading_period: Optional[str] = None
    market_phase: Optional[str] = None
    liquidity_phase: Optional[str] = None
    volatility_phase: Optional[str] = None

    # ------------------------------------------------------------------
    # Session measurements
    # ------------------------------------------------------------------
    opening_price: Optional[float] = None
    current_price: Optional[float] = None
    session_high: Optional[float] = None
    session_low: Optional[float] = None

    session_volume: Optional[float] = None
    session_value: Optional[float] = None
    transaction_count: Optional[int] = None

    # ------------------------------------------------------------------
    # Session context
    # ------------------------------------------------------------------
    previous_session_id: Optional[str] = None
    next_session_id: Optional[str] = None
    parent_session_id: Optional[str] = None

    observation_id: Optional[str] = None
    context_id: Optional[str] = None
    regime_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Environment
    # ------------------------------------------------------------------
    broker: Optional[str] = None
    provider: Optional[str] = None
    environment: Optional[str] = None
    mode: Optional[str] = None

    # ------------------------------------------------------------------
    # Session request / lifecycle references
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
    # Observed / derived tracking
    # ------------------------------------------------------------------
    observed_fields: tuple[str, ...] = field(default_factory=tuple)
    derived_fields: tuple[str, ...] = field(default_factory=tuple)

    # ------------------------------------------------------------------
    # Additional metadata
    # ------------------------------------------------------------------
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.sequence is not None and self.sequence < 0:
            raise ValueError("sequence cannot be negative")

        numeric_fields = (
            "elapsed_seconds",
            "remaining_seconds",
            "duration_seconds",
            "opening_price",
            "current_price",
            "session_high",
            "session_low",
            "session_volume",
            "session_value",
        )

        for field_name in numeric_fields:
            value = getattr(self, field_name)

            if value is not None and not isinstance(value, (int, float)):
                raise TypeError(
                    f"{field_name} must be numeric when provided"
                )

        if (
            self.transaction_count is not None
            and self.transaction_count < 0
        ):
            raise ValueError("transaction_count cannot be negative")

        if (
            self.elapsed_seconds is not None
            and self.elapsed_seconds < 0
        ):
            raise ValueError("elapsed_seconds cannot be negative")

        if (
            self.remaining_seconds is not None
            and self.remaining_seconds < 0
        ):
            raise ValueError("remaining_seconds cannot be negative")

        if (
            self.duration_seconds is not None
            and self.duration_seconds < 0
        ):
            raise ValueError("duration_seconds cannot be negative")

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------
    def has_identity(self) -> bool:
        return bool(self.session_id)

    def has_market_identity(self) -> bool:
        return bool(
            self.market
            or self.instrument
            or self.symbol
            or self.exchange
            or self.venue
            or self.contract
        )

    # ------------------------------------------------------------------
    # Timing identity
    # ------------------------------------------------------------------
    def has_session_date(self) -> bool:
        return bool(self.session_date)

    def has_timezone(self) -> bool:
        return bool(self.timezone)

    def has_scheduled_window(self) -> bool:
        return bool(
            self.scheduled_open
            or self.scheduled_close
        )

    def has_actual_window(self) -> bool:
        return bool(
            self.actual_open
            or self.actual_close
        )

    def has_current_time(self) -> bool:
        return bool(self.current_time)

    # ------------------------------------------------------------------
    # Session state
    # ------------------------------------------------------------------
    def has_state(self) -> bool:
        return bool(
            self.session_state
            or self.session_phase
            or self.session_type
        )

    def is_active(self) -> bool:
        return self.is_open is True

    def is_inactive(self) -> bool:
        return self.is_closed is True

    # ------------------------------------------------------------------
    # Price state
    # ------------------------------------------------------------------
    def has_opening_price(self) -> bool:
        return self.opening_price is not None

    def has_current_price(self) -> bool:
        return self.current_price is not None

    def has_session_range(self) -> bool:
        return (
            self.session_high is not None
            and self.session_low is not None
        )

    # ------------------------------------------------------------------
    # Activity state
    # ------------------------------------------------------------------
    def has_volume(self) -> bool:
        return self.session_volume is not None

    def has_value(self) -> bool:
        return self.session_value is not None

    def has_transaction_count(self) -> bool:
        return self.transaction_count is not None

    # ------------------------------------------------------------------
    # Session calculations
    # ------------------------------------------------------------------
    def calculate_session_range(self) -> Optional[float]:
        if self.session_high is None or self.session_low is None:
            return None

        return self.session_high - self.session_low

    def calculate_price_change(self) -> Optional[float]:
        if (
            self.opening_price is None
            or self.current_price is None
        ):
            return None

        return self.current_price - self.opening_price

    def calculate_price_change_percent(self) -> Optional[float]:
        if (
            self.opening_price is None
            or self.current_price is None
        ):
            return None

        if self.opening_price == 0:
            return None

        return (
            (self.current_price - self.opening_price)
            / abs(self.opening_price)
        ) * 100.0

    # ------------------------------------------------------------------
    # Lifecycle references
    # ------------------------------------------------------------------
    def has_previous_session(self) -> bool:
        return bool(self.previous_session_id)

    def has_next_session(self) -> bool:
        return bool(self.next_session_id)

    def has_parent_session(self) -> bool:
        return bool(self.parent_session_id)

    def has_observation_reference(self) -> bool:
        return bool(self.observation_id)

    def has_context_reference(self) -> bool:
        return bool(self.context_id)

    def has_regime_reference(self) -> bool:
        return bool(self.regime_id)

    def has_lifecycle_reference(self) -> bool:
        return bool(self.lifecycle_id)

    def has_request_reference(self) -> bool:
        return bool(self.request_id)

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
            issues.append("missing_session_id")

        if self.timestamp is None:
            issues.append("missing_timestamp")

        if not self.has_market_identity():
            issues.append("missing_market_identity")

        if self.session_state is None and self.session_phase is None:
            issues.append("missing_session_state")

        if (
            self.session_high is not None
            and self.session_low is not None
            and self.session_low > self.session_high
        ):
            issues.append("session_low_above_session_high")

        if (
            self.opening_price is not None
            and self.session_high is not None
            and self.opening_price > self.session_high
        ):
            issues.append("opening_price_above_session_high")

        if (
            self.opening_price is not None
            and self.session_low is not None
            and self.opening_price < self.session_low
        ):
            issues.append("opening_price_below_session_low")

        if self.is_open is True and self.is_closed is True:
            issues.append("session_marked_open_and_closed")

        if self.is_pre_open is True and self.is_open is True:
            issues.append("session_marked_pre_open_and_open")

        if self.is_post_close is True and self.is_open is True:
            issues.append("session_marked_post_close_and_open")

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
            "schema": MARKET_SESSION_SCHEMA,
            "version": MARKET_SESSION_SCHEMA_VERSION,
        }


# ----------------------------------------------------------------------
# Health
# ----------------------------------------------------------------------
def market_session_health() -> dict[str, Any]:
    return {
        "layer": MARKET_SESSION_SCHEMA,
        "version": MARKET_SESSION_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "structural_only": True,
        "decision_logic": False,
        "execution_logic": False,
        "v7_dependency": False,
        "supports_market_identity": True,
        "supports_session_lifecycle": True,
        "supports_session_timing": True,
        "supports_market_activity": True,
    }


__all__ = [
    "MARKET_SESSION_SCHEMA_VERSION",
    "MARKET_SESSION_SCHEMA",
    "MarketSession",
    "market_session_health",
]