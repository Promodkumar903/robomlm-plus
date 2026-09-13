"""
ROBOMLM PLUS
V6 Market Risk Schema

Purpose:
    Structural representation of market/account risk state.

Design rules:
    - Immutable schema.
    - Risk state is represented, not decided.
    - Supports market, position, portfolio and account context.
    - Currency agnostic: INR, USD, USDT, etc.
    - Observed and derived values remain explicitly separated.
    - No trading decision logic.
    - No execution authorization.
    - No order placement.
    - No V7+ dependency.
    - Broker/provider-specific limits remain external inputs.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from math import isfinite
from numbers import Real
from typing import Any, Optional


MARKET_RISK_SCHEMA_VERSION = "1.0.0"
MARKET_RISK_SCHEMA = "V6_MARKET_RISK"


@dataclass(frozen=True)
class MarketRisk:
    """
    Immutable structural representation of risk state.

    Supports:
        - Exposure
        - Risk amount
        - Risk percentage
        - Reward amount
        - Drawdown
        - Margin context
        - Concentration
        - Stop/target reference
        - Account and portfolio risk context

    This schema does not determine whether a trade should be taken.
    """

    # ------------------------------------------------------------------
    # Risk identity
    # ------------------------------------------------------------------
    risk_id: Optional[str] = None
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
    # Risk classification
    # ------------------------------------------------------------------
    risk_type: Optional[str] = None
    risk_state: Optional[str] = None
    risk_mode: Optional[str] = None
    risk_level: Optional[str] = None

    # ------------------------------------------------------------------
    # Exposure context
    # ------------------------------------------------------------------
    gross_exposure: Optional[float] = None
    net_exposure: Optional[float] = None
    long_exposure: Optional[float] = None
    short_exposure: Optional[float] = None

    # ------------------------------------------------------------------
    # Capital / valuation context
    # ------------------------------------------------------------------
    account_equity: Optional[float] = None
    portfolio_value: Optional[float] = None
    collateral_value: Optional[float] = None
    margin_balance: Optional[float] = None
    used_margin: Optional[float] = None
    free_margin: Optional[float] = None

    # ------------------------------------------------------------------
    # Risk measurements
    # ------------------------------------------------------------------
    risk_value: Optional[float] = None
    risk_percent: Optional[float] = None
    reward_value: Optional[float] = None
    reward_percent: Optional[float] = None
    risk_reward_ratio: Optional[float] = None

    # ------------------------------------------------------------------
    # Protection / price references
    # ------------------------------------------------------------------
    entry_price: Optional[float] = None
    current_price: Optional[float] = None
    stop_price: Optional[float] = None
    target_price: Optional[float] = None

    # ------------------------------------------------------------------
    # Drawdown
    # ------------------------------------------------------------------
    drawdown_value: Optional[float] = None
    drawdown_percent: Optional[float] = None
    peak_value: Optional[float] = None

    # ------------------------------------------------------------------
    # Concentration
    # ------------------------------------------------------------------
    concentration_value: Optional[float] = None
    concentration_percent: Optional[float] = None
    largest_position_value: Optional[float] = None
    position_count: Optional[int] = None

    # ------------------------------------------------------------------
    # Margin / leverage references
    # ------------------------------------------------------------------
    margin_requirement: Optional[float] = None
    margin_ratio: Optional[float] = None
    leverage_ratio: Optional[float] = None

    # ------------------------------------------------------------------
    # Risk limits / thresholds
    # ------------------------------------------------------------------
    risk_limit: Optional[float] = None
    exposure_limit: Optional[float] = None
    drawdown_limit: Optional[float] = None
    concentration_limit: Optional[float] = None

    # ------------------------------------------------------------------
    # Related references
    # ------------------------------------------------------------------
    order_id: Optional[str] = None
    execution_id: Optional[str] = None
    transaction_id: Optional[str] = None
    observation_id: Optional[str] = None
    context_id: Optional[str] = None
    regime_id: Optional[str] = None
    margin_id: Optional[str] = None
    leverage_id: Optional[str] = None
    exposure_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Session / request references
    # ------------------------------------------------------------------
    session_id: Optional[str] = None
    request_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Source / provenance
    # ------------------------------------------------------------------
    source: Optional[str] = None
    source_type: Optional[str] = None
    source_reference: Optional[str] = None
    provenance: dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Explicit observed / derived separation
    # ------------------------------------------------------------------
    observed_fields: tuple[str, ...] = field(default_factory=tuple)
    derived_fields: tuple[str, ...] = field(default_factory=tuple)

    # ------------------------------------------------------------------
    # Additional metadata
    # ------------------------------------------------------------------
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate structural invariants."""

        # --------------------------------------------------------------
        # Sequence
        # --------------------------------------------------------------
        if self.sequence is not None:
            if (
                isinstance(self.sequence, bool)
                or not isinstance(self.sequence, int)
            ):
                raise TypeError(
                    "sequence must be an integer when provided."
                )

            if self.sequence < 0:
                raise ValueError("sequence must be non-negative.")

        # --------------------------------------------------------------
        # Position count
        # --------------------------------------------------------------
        if self.position_count is not None:
            if (
                isinstance(self.position_count, bool)
                or not isinstance(self.position_count, int)
            ):
                raise ValueError(
                    "position_count must be an integer when provided."
                )

            if self.position_count < 0:
                raise ValueError(
                    "position_count cannot be negative."
                )

        # --------------------------------------------------------------
        # Non-negative numeric fields
        # --------------------------------------------------------------
        non_negative_fields = (
            "gross_exposure",
            "long_exposure",
            "short_exposure",
            "account_equity",
            "portfolio_value",
            "collateral_value",
            "margin_balance",
            "used_margin",
            "free_margin",
            "risk_value",
            "reward_value",
            "risk_percent",
            "reward_percent",
            "risk_reward_ratio",
            "entry_price",
            "current_price",
            "stop_price",
            "target_price",
            "drawdown_value",
            "drawdown_percent",
            "peak_value",
            "concentration_value",
            "concentration_percent",
            "largest_position_value",
            "margin_requirement",
            "margin_ratio",
            "leverage_ratio",
            "risk_limit",
            "exposure_limit",
            "drawdown_limit",
            "concentration_limit",
        )

        for field_name in non_negative_fields:
            value = getattr(self, field_name)

            if value is None:
                continue

            if isinstance(value, bool) or not isinstance(value, Real):
                raise TypeError(
                    f"{field_name} must be a numeric value when provided."
                )

            numeric_value = float(value)

            if not isfinite(numeric_value):
                raise ValueError(
                    f"{field_name} must be finite when provided."
                )

            if numeric_value < 0:
                raise ValueError(
                    f"{field_name} cannot be negative."
                )

        # --------------------------------------------------------------
        # Net exposure
        # --------------------------------------------------------------
        if self.net_exposure is not None:
            if (
                isinstance(self.net_exposure, bool)
                or not isinstance(self.net_exposure, Real)
            ):
                raise TypeError(
                    "net_exposure must be a numeric value when provided."
                )

            net_exposure_numeric = float(self.net_exposure)

            if not isfinite(net_exposure_numeric):
                raise ValueError(
                    "net_exposure must be finite when provided."
                )

        # --------------------------------------------------------------
        # Currency
        # --------------------------------------------------------------
        if self.currency is not None and not str(self.currency).strip():
            raise ValueError("currency cannot be empty.")

        if (
            self.base_currency is not None
            and not str(self.base_currency).strip()
        ):
            raise ValueError("base_currency cannot be empty.")

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    def has_identity(self) -> bool:
        return bool(self.risk_id)

    def has_risk_identity(self) -> bool:
        return self.has_identity()

    def has_account_identity(self) -> bool:
        return bool(self.account_id)

    def has_portfolio_identity(self) -> bool:
        return bool(self.portfolio_id)

    def has_position_identity(self) -> bool:
        return bool(self.position_id)

    def has_timestamp(self) -> bool:
        return bool(self.timestamp)

    # ------------------------------------------------------------------
    # Market identity
    # ------------------------------------------------------------------

    def has_market_identity(self) -> bool:
        return bool(
            self.market
            or self.instrument
            or self.symbol
            or self.exchange
            or self.venue
        )

    # ------------------------------------------------------------------
    # Currency / environment
    # ------------------------------------------------------------------

    def has_currency(self) -> bool:
        return bool(self.currency or self.base_currency)

    def has_environment_identity(self) -> bool:
        return bool(
            self.broker
            or self.provider
            or self.environment
            or self.mode
            or self.venue
        )

    # ------------------------------------------------------------------
    # Exposure
    # ------------------------------------------------------------------

    def has_gross_exposure(self) -> bool:
        return self.gross_exposure is not None

    def has_net_exposure(self) -> bool:
        return self.net_exposure is not None

    def has_directional_exposure(self) -> bool:
        return (
            self.long_exposure is not None
            or self.short_exposure is not None
        )

    def has_exposure(self) -> bool:
        return any(
            value is not None
            for value in (
                self.gross_exposure,
                self.net_exposure,
                self.long_exposure,
                self.short_exposure,
            )
        )

    # ------------------------------------------------------------------
    # Capital / margin
    # ------------------------------------------------------------------

    def has_account_equity(self) -> bool:
        return self.account_equity is not None

    def has_portfolio_value(self) -> bool:
        return self.portfolio_value is not None

    def has_collateral(self) -> bool:
        return self.collateral_value is not None

    def has_margin_context(self) -> bool:
        return any(
            value is not None
            for value in (
                self.margin_balance,
                self.used_margin,
                self.free_margin,
                self.margin_requirement,
                self.margin_ratio,
            )
        )

    # ------------------------------------------------------------------
    # Risk measurements
    # ------------------------------------------------------------------

    def has_risk_value(self) -> bool:
        return self.risk_value is not None

    def has_risk_percent(self) -> bool:
        return self.risk_percent is not None

    def has_reward_value(self) -> bool:
        return self.reward_value is not None

    def has_reward_percent(self) -> bool:
        return self.reward_percent is not None

    def has_risk_reward_ratio(self) -> bool:
        return self.risk_reward_ratio is not None

    # ------------------------------------------------------------------
    # Protection / price
    # ------------------------------------------------------------------

    def has_entry_price(self) -> bool:
        return self.entry_price is not None

    def has_current_price(self) -> bool:
        return self.current_price is not None

    def has_stop_price(self) -> bool:
        return self.stop_price is not None

    def has_target_price(self) -> bool:
        return self.target_price is not None

    def has_protection_prices(self) -> bool:
        return (
            self.stop_price is not None
            or self.target_price is not None
        )

    # ------------------------------------------------------------------
    # Drawdown
    # ------------------------------------------------------------------

    def has_drawdown(self) -> bool:
        return (
            self.drawdown_value is not None
            or self.drawdown_percent is not None
        )

    def has_peak_value(self) -> bool:
        return self.peak_value is not None

    # ------------------------------------------------------------------
    # Concentration
    # ------------------------------------------------------------------

    def has_concentration(self) -> bool:
        return (
            self.concentration_value is not None
            or self.concentration_percent is not None
        )

    def has_position_count(self) -> bool:
        return self.position_count is not None

    # ------------------------------------------------------------------
    # Structural calculations
    # ------------------------------------------------------------------

    def calculate_risk_percent(
        self,
        *,
        risk_value: Optional[float] = None,
        capital_base: Optional[float] = None,
    ) -> Optional[float]:
        """
        Calculate risk percentage from risk value and capital base.

        Result is returned as a percentage, not a decimal ratio.
        """

        risk = (
            risk_value
            if risk_value is not None
            else self.risk_value
        )

        capital = (
            capital_base
            if capital_base is not None
            else self.account_equity
        )

        if risk is None or capital is None:
            return None

        capital_numeric = float(capital)

        if capital_numeric <= 0:
            return None

        return (float(risk) / capital_numeric) * 100.0

    def calculate_reward_percent(
        self,
        *,
        reward_value: Optional[float] = None,
        capital_base: Optional[float] = None,
    ) -> Optional[float]:
        """
        Calculate reward percentage from reward value and capital base.
        """

        reward = (
            reward_value
            if reward_value is not None
            else self.reward_value
        )

        capital = (
            capital_base
            if capital_base is not None
            else self.account_equity
        )

        if reward is None or capital is None:
            return None

        capital_numeric = float(capital)

        if capital_numeric <= 0:
            return None

        return (float(reward) / capital_numeric) * 100.0

    def calculate_risk_reward_ratio(self) -> Optional[float]:
        """
        Calculate reward / risk.

        Returns None when risk is zero or unavailable.
        """

        if self.reward_value is None or self.risk_value is None:
            return None

        risk = float(self.risk_value)

        if risk <= 0:
            return None

        return float(self.reward_value) / risk

    def calculate_drawdown_percent(
        self,
        *,
        drawdown_value: Optional[float] = None,
        peak_value: Optional[float] = None,
    ) -> Optional[float]:
        """
        Calculate drawdown percentage from drawdown value and peak value.
        """

        drawdown = (
            drawdown_value
            if drawdown_value is not None
            else self.drawdown_value
        )

        peak = (
            peak_value
            if peak_value is not None
            else self.peak_value
        )

        if drawdown is None or peak is None:
            return None

        peak_numeric = float(peak)

        if peak_numeric <= 0:
            return None

        return (float(drawdown) / peak_numeric) * 100.0

    def calculate_exposure_ratio(
        self,
        *,
        exposure: Optional[float] = None,
        capital_base: Optional[float] = None,
    ) -> Optional[float]:
        """
        Calculate exposure / capital base.

        This is a structural ratio only.
        """

        exposure_value = (
            exposure
            if exposure is not None
            else self.gross_exposure
        )

        capital = (
            capital_base
            if capital_base is not None
            else self.account_equity
        )

        if exposure_value is None or capital is None:
            return None

        capital_numeric = float(capital)

        if capital_numeric <= 0:
            return None

        return float(exposure_value) / capital_numeric

    def calculate_margin_utilization(self) -> Optional[float]:
        """
        Calculate used margin / margin balance.
        """

        if self.used_margin is None or self.margin_balance is None:
            return None

        balance = float(self.margin_balance)

        if balance <= 0:
            return None

        return float(self.used_margin) / balance

    # ------------------------------------------------------------------
    # Limits
    # ------------------------------------------------------------------

    def has_risk_limit(self) -> bool:
        return self.risk_limit is not None

    def has_exposure_limit(self) -> bool:
        return self.exposure_limit is not None

    def has_drawdown_limit(self) -> bool:
        return self.drawdown_limit is not None

    def has_concentration_limit(self) -> bool:
        return self.concentration_limit is not None

    # ------------------------------------------------------------------
    # Related references
    # ------------------------------------------------------------------

    def has_order_reference(self) -> bool:
        return bool(self.order_id)

    def has_execution_reference(self) -> bool:
        return bool(self.execution_id)

    def has_transaction_reference(self) -> bool:
        return bool(self.transaction_id)

    def has_observation_reference(self) -> bool:
        return bool(self.observation_id)

    def has_context_reference(self) -> bool:
        return bool(self.context_id)

    def has_regime_reference(self) -> bool:
        return bool(self.regime_id)

    def has_margin_reference(self) -> bool:
        return bool(self.margin_id)

    def has_leverage_reference(self) -> bool:
        return bool(self.leverage_id)

    def has_exposure_reference(self) -> bool:
        return bool(self.exposure_id)

    def has_session_reference(self) -> bool:
        return bool(self.session_id)

    def has_request_reference(self) -> bool:
        return bool(self.request_id)

    # ------------------------------------------------------------------
    # Source / provenance
    # ------------------------------------------------------------------

    def has_source_reference(self) -> bool:
        return bool(
            self.source
            or self.source_type
            or self.source_reference
        )

    def has_provenance(self) -> bool:
        return bool(self.provenance)

    def observed_field_names(self) -> tuple[str, ...]:
        return tuple(self.observed_fields)

    def derived_field_names(self) -> tuple[str, ...]:
        return tuple(self.derived_fields)

    # ------------------------------------------------------------------
    # Structural diagnostics
    # ------------------------------------------------------------------

    def issue_flags(self) -> list[str]:
        issues: list[str] = []

        if not self.risk_id:
            issues.append("MISSING_RISK_ID")

        if not (
            self.account_id
            or self.portfolio_id
            or self.position_id
        ):
            issues.append(
                "MISSING_ACCOUNT_PORTFOLIO_OR_POSITION_ID"
            )

        if not self.timestamp:
            issues.append("MISSING_TIMESTAMP")

        if not self.has_market_identity():
            issues.append("MISSING_MARKET_IDENTITY")

        if not self.currency and not self.base_currency:
            issues.append("MISSING_CURRENCY")

        if (
            self.used_margin is not None
            and self.margin_balance is not None
            and self.used_margin > self.margin_balance
        ):
            issues.append("USED_MARGIN_EXCEEDS_MARGIN_BALANCE")

        if (
            self.risk_limit is not None
            and self.risk_value is not None
            and self.risk_value > self.risk_limit
        ):
            issues.append("RISK_VALUE_EXCEEDS_LIMIT")

        if (
            self.exposure_limit is not None
            and self.gross_exposure is not None
            and self.gross_exposure > self.exposure_limit
        ):
            issues.append("GROSS_EXPOSURE_EXCEEDS_LIMIT")

        if (
            self.drawdown_limit is not None
            and self.drawdown_value is not None
            and self.drawdown_value > self.drawdown_limit
        ):
            issues.append("DRAWDOWN_EXCEEDS_LIMIT")

        if (
            self.concentration_limit is not None
            and self.concentration_value is not None
            and self.concentration_value > self.concentration_limit
        ):
            issues.append("CONCENTRATION_EXCEEDS_LIMIT")

        return issues

    def is_structurally_valid(self) -> bool:
        return len(self.issue_flags()) == 0

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def schema_info(self) -> dict[str, Any]:
        return {
            "schema": MARKET_RISK_SCHEMA,
            "version": MARKET_RISK_SCHEMA_VERSION,
            "immutable": True,
            "currency_agnostic": True,
            "supports_inr": True,
            "supports_usd": True,
            "supports_usdt": True,
            "exposure_supported": True,
            "risk_value_supported": True,
            "risk_percent_supported": True,
            "reward_supported": True,
            "risk_reward_supported": True,
            "drawdown_supported": True,
            "concentration_supported": True,
            "margin_context_supported": True,
            "leverage_context_supported": True,
            "limits_supported": True,
            "observed_derived_separation": True,
            "provenance_supported": True,
            "decision_logic": False,
            "execution_authorization": False,
            "order_placement": False,
            "v7_dependency": False,
        }


# ----------------------------------------------------------------------
# Health
# ----------------------------------------------------------------------

def market_risk_health() -> dict[str, Any]:
    return {
        "schema": MARKET_RISK_SCHEMA,
        "version": MARKET_RISK_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "currency_agnostic": True,
        "supports_inr": True,
        "supports_usd": True,
        "supports_usdt": True,
        "exposure_supported": True,
        "risk_measurements_supported": True,
        "reward_measurements_supported": True,
        "risk_reward_supported": True,
        "drawdown_supported": True,
        "concentration_supported": True,
        "margin_context_supported": True,
        "leverage_context_supported": True,
        "limits_supported": True,
        "observed_derived_separation": True,
        "provenance_supported": True,
        "decision_logic": False,
        "execution_logic": False,
        "order_placement": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_RISK_SCHEMA_VERSION",
    "MARKET_RISK_SCHEMA",
    "MarketRisk",
    "market_risk_health",
]