"""
ROBOMLM PLUS
V6 Market Drawdown Schema

Purpose:
    Structural representation of drawdown state across account,
    portfolio, position, and market contexts.

Rules:
    - Structural schema only.
    - No trading decisions.
    - No execution logic.
    - No risk authorization.
    - No V7+ dependency.
    - Immutable data representation.
    - INR / USD / USDT and other currencies are supported.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from math import isfinite
from numbers import Real
from typing import Any, Optional


MARKET_DRAWDOWN_SCHEMA_VERSION = "1.0.0"
MARKET_DRAWDOWN_SCHEMA = "V6_MARKET_DRAWDOWN"


@dataclass(frozen=True)
class MarketDrawdown:
    """
    Immutable structural representation of drawdown state.
    """

    # ------------------------------------------------------------------
    # Drawdown identity
    # ------------------------------------------------------------------
    drawdown_id: Optional[str] = None
    account_id: Optional[str] = None
    portfolio_id: Optional[str] = None
    position_id: Optional[str] = None
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
    # Currency / environment
    # ------------------------------------------------------------------
    currency: Optional[str] = None
    base_currency: Optional[str] = None
    broker: Optional[str] = None
    provider: Optional[str] = None
    environment: Optional[str] = None
    mode: Optional[str] = None

    # ------------------------------------------------------------------
    # Drawdown classification
    # ------------------------------------------------------------------
    drawdown_type: Optional[str] = None
    drawdown_state: Optional[str] = None
    drawdown_mode: Optional[str] = None

    # ------------------------------------------------------------------
    # Value progression
    # ------------------------------------------------------------------
    peak_value: Optional[float] = None
    current_value: Optional[float] = None
    trough_value: Optional[float] = None

    drawdown_value: Optional[float] = None
    drawdown_percent: Optional[float] = None

    recovery_value: Optional[float] = None
    recovery_percent: Optional[float] = None

    high_water_mark: Optional[float] = None
    low_water_mark: Optional[float] = None

    # ------------------------------------------------------------------
    # Drawdown timing
    # ------------------------------------------------------------------
    peak_timestamp: Optional[str] = None
    trough_timestamp: Optional[str] = None
    recovery_timestamp: Optional[str] = None

    duration_seconds: Optional[float] = None
    recovery_duration_seconds: Optional[float] = None

    # ------------------------------------------------------------------
    # Previous state
    # ------------------------------------------------------------------
    previous_peak_value: Optional[float] = None
    previous_drawdown_value: Optional[float] = None

    # ------------------------------------------------------------------
    # Financial context
    # ------------------------------------------------------------------
    account_equity: Optional[float] = None
    portfolio_value: Optional[float] = None
    market_value: Optional[float] = None

    # ------------------------------------------------------------------
    # Limits / references
    # ------------------------------------------------------------------
    risk_limit: Optional[float] = None
    drawdown_limit: Optional[float] = None
    reference_limit: Optional[float] = None

    position_count: Optional[int] = None

    # ------------------------------------------------------------------
    # Related schema references
    # ------------------------------------------------------------------
    risk_id: Optional[str] = None
    exposure_id: Optional[str] = None
    margin_id: Optional[str] = None
    leverage_id: Optional[str] = None
    position_ref: Optional[str] = None
    order_id: Optional[str] = None
    execution_id: Optional[str] = None
    transaction_id: Optional[str] = None
    context_id: Optional[str] = None
    regime_id: Optional[str] = None
    observation_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Session / request
    # ------------------------------------------------------------------
    session_id: Optional[str] = None
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
                raise ValueError("sequence cannot be negative")

        # --------------------------------------------------------------
        # Position count validation
        # --------------------------------------------------------------
        if self.position_count is not None:
            if isinstance(self.position_count, bool) or not isinstance(
                self.position_count, int
            ):
                raise TypeError(
                    "position_count must be an integer when provided"
                )

            if self.position_count < 0:
                raise ValueError("position_count cannot be negative")

        # --------------------------------------------------------------
        # Numeric field validation
        #
        # Structural numeric fields must:
        #   - be real numeric values
        #   - not be bool
        #   - not be NaN
        #   - not be +Inf/-Inf
        #
        # Numeric strings are deliberately rejected.
        # --------------------------------------------------------------
        numeric_fields = (
            "peak_value",
            "current_value",
            "trough_value",
            "drawdown_value",
            "drawdown_percent",
            "recovery_value",
            "recovery_percent",
            "high_water_mark",
            "low_water_mark",
            "duration_seconds",
            "recovery_duration_seconds",
            "previous_peak_value",
            "previous_drawdown_value",
            "account_equity",
            "portfolio_value",
            "market_value",
            "risk_limit",
            "drawdown_limit",
            "reference_limit",
        )

        for field_name in numeric_fields:
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

        # --------------------------------------------------------------
        # Duration validation
        # --------------------------------------------------------------
        if (
            self.duration_seconds is not None
            and self.duration_seconds < 0
        ):
            raise ValueError("duration_seconds cannot be negative")

        if (
            self.recovery_duration_seconds is not None
            and self.recovery_duration_seconds < 0
        ):
            raise ValueError(
                "recovery_duration_seconds cannot be negative"
            )

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------
    def has_identity(self) -> bool:
        return bool(self.drawdown_id)

    def has_account_identity(self) -> bool:
        return bool(self.account_id)

    def has_portfolio_identity(self) -> bool:
        return bool(self.portfolio_id)

    def has_position_identity(self) -> bool:
        return bool(self.position_id)

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
    # Currency / environment
    # ------------------------------------------------------------------
    def has_currency_identity(self) -> bool:
        return bool(self.currency or self.base_currency)

    def has_environment_identity(self) -> bool:
        return bool(
            self.broker
            or self.provider
            or self.environment
            or self.mode
        )

    # ------------------------------------------------------------------
    # Value availability
    # ------------------------------------------------------------------
    def has_peak_value(self) -> bool:
        return self.peak_value is not None

    def has_current_value(self) -> bool:
        return self.current_value is not None

    def has_trough_value(self) -> bool:
        return self.trough_value is not None

    def has_drawdown_value(self) -> bool:
        return self.drawdown_value is not None

    def has_drawdown_percent(self) -> bool:
        return self.drawdown_percent is not None

    def has_recovery_value(self) -> bool:
        return self.recovery_value is not None

    def has_recovery_percent(self) -> bool:
        return self.recovery_percent is not None

    def has_high_water_mark(self) -> bool:
        return self.high_water_mark is not None

    def has_low_water_mark(self) -> bool:
        return self.low_water_mark is not None

    # ------------------------------------------------------------------
    # Drawdown calculations
    # ------------------------------------------------------------------
    def calculate_drawdown_value(self) -> Optional[float]:
        if self.peak_value is None or self.current_value is None:
            return None

        return self.peak_value - self.current_value

    def calculate_drawdown_percent(self) -> Optional[float]:
        if self.peak_value is None or self.current_value is None:
            return None

        if self.peak_value == 0:
            return None

        return (
            (self.peak_value - self.current_value)
            / abs(self.peak_value)
        ) * 100.0

    # ------------------------------------------------------------------
    # Recovery calculations
    # ------------------------------------------------------------------
    def calculate_recovery_value(self) -> Optional[float]:
        if self.current_value is None or self.trough_value is None:
            return None

        return self.current_value - self.trough_value

    def calculate_recovery_percent(self) -> Optional[float]:
        if (
            self.peak_value is None
            or self.trough_value is None
            or self.current_value is None
        ):
            return None

        total_range = self.peak_value - self.trough_value

        if total_range == 0:
            return None

        return (
            (self.current_value - self.trough_value)
            / abs(total_range)
        ) * 100.0

    # ------------------------------------------------------------------
    # Duration
    # ------------------------------------------------------------------
    def has_duration(self) -> bool:
        return self.duration_seconds is not None

    def has_recovery_duration(self) -> bool:
        return self.recovery_duration_seconds is not None

    # ------------------------------------------------------------------
    # Limits
    # ------------------------------------------------------------------
    def has_limit(self) -> bool:
        return any(
            value is not None
            for value in (
                self.risk_limit,
                self.drawdown_limit,
                self.reference_limit,
            )
        )

    # ------------------------------------------------------------------
    # References
    # ------------------------------------------------------------------
    def has_risk_reference(self) -> bool:
        return bool(self.risk_id)

    def has_exposure_reference(self) -> bool:
        return bool(self.exposure_id)

    def has_margin_reference(self) -> bool:
        return bool(self.margin_id)

    def has_leverage_reference(self) -> bool:
        return bool(self.leverage_id)

    def has_position_reference(self) -> bool:
        return bool(self.position_ref or self.position_id)

    def has_order_reference(self) -> bool:
        return bool(self.order_id)

    def has_execution_reference(self) -> bool:
        return bool(self.execution_id)

    def has_transaction_reference(self) -> bool:
        return bool(self.transaction_id)

    def has_context_reference(self) -> bool:
        return bool(self.context_id)

    def has_regime_reference(self) -> bool:
        return bool(self.regime_id)

    def has_observation_reference(self) -> bool:
        return bool(self.observation_id)

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
            issues.append("missing_drawdown_id")

        if self.timestamp is None:
            issues.append("missing_timestamp")

        if not (
            self.has_account_identity()
            or self.has_portfolio_identity()
            or self.has_position_identity()
        ):
            issues.append(
                "missing_account_portfolio_position_identity"
            )

        if not self.has_currency_identity():
            issues.append("missing_currency_identity")

        if (
            self.drawdown_value is not None
            and self.drawdown_value < 0
        ):
            issues.append("negative_drawdown_value")

        if (
            self.drawdown_percent is not None
            and self.drawdown_percent < 0
        ):
            issues.append("negative_drawdown_percent")

        if (
            self.recovery_percent is not None
            and self.recovery_percent < 0
        ):
            issues.append("negative_recovery_percent")

        if (
            self.peak_value is not None
            and self.current_value is not None
            and self.current_value > self.peak_value
            and self.drawdown_value is not None
            and self.drawdown_value > 0
        ):
            issues.append(
                "current_above_peak_with_positive_drawdown"
            )

        if (
            self.peak_value is not None
            and self.trough_value is not None
            and self.trough_value > self.peak_value
        ):
            issues.append("trough_above_peak")

        if (
            self.high_water_mark is not None
            and self.low_water_mark is not None
            and self.low_water_mark > self.high_water_mark
        ):
            issues.append("low_water_mark_above_high_water_mark")

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
            "schema": MARKET_DRAWDOWN_SCHEMA,
            "version": MARKET_DRAWDOWN_SCHEMA_VERSION,
        }


# ----------------------------------------------------------------------
# Health
# ----------------------------------------------------------------------
def market_drawdown_health() -> dict[str, Any]:
    return {
        "layer": MARKET_DRAWDOWN_SCHEMA,
        "version": MARKET_DRAWDOWN_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "structural_only": True,
        "decision_logic": False,
        "execution_logic": False,
        "v7_dependency": False,
        "supports_account_drawdown": True,
        "supports_portfolio_drawdown": True,
        "supports_position_drawdown": True,
        "supports_market_context": True,
        "supports_inr_usd_usdt": True,
    }


__all__ = [
    "MARKET_DRAWDOWN_SCHEMA_VERSION",
    "MARKET_DRAWDOWN_SCHEMA",
    "MarketDrawdown",
    "market_drawdown_health",
]