"""
ROBOMLM PLUS
V6 Market Exposure Schema

Purpose:
    Structural representation of market exposure.

Design rules:
    - Immutable schema.
    - Exposure is distinct from account balance, margin and leverage.
    - Supports gross, net, long and short exposure.
    - Currency agnostic: INR, USD, USDT, etc.
    - Observed and derived values remain explicitly separated.
    - No trading decisions.
    - No execution authorization.
    - No risk decisions.
    - No V7+ dependency.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from math import isfinite
from numbers import Real
from typing import Any, Optional


MARKET_EXPOSURE_SCHEMA_VERSION = "1.0.0"
MARKET_EXPOSURE_SCHEMA = "V6_MARKET_EXPOSURE"


@dataclass(frozen=True)
class MarketExposure:
    """
    Immutable structural representation of market exposure.

    Supports:
        - Gross exposure
        - Net exposure
        - Long exposure
        - Short exposure
        - Position count
        - Notional exposure
        - Exposure ratios
        - Market/account references
    """

    # ------------------------------------------------------------------
    # Exposure identity
    # ------------------------------------------------------------------
    exposure_id: Optional[str] = None
    account_id: Optional[str] = None
    portfolio_id: Optional[str] = None
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
    # Exposure classification
    # ------------------------------------------------------------------
    exposure_type: Optional[str] = None
    exposure_state: Optional[str] = None
    exposure_mode: Optional[str] = None
    side: Optional[str] = None

    # ------------------------------------------------------------------
    # Exposure measurements
    # ------------------------------------------------------------------
    gross_exposure: Optional[float] = None
    net_exposure: Optional[float] = None
    long_exposure: Optional[float] = None
    short_exposure: Optional[float] = None

    # ------------------------------------------------------------------
    # Notional / quantity context
    # ------------------------------------------------------------------
    quantity: Optional[float] = None
    long_quantity: Optional[float] = None
    short_quantity: Optional[float] = None
    notional_value: Optional[float] = None
    long_notional_value: Optional[float] = None
    short_notional_value: Optional[float] = None

    # ------------------------------------------------------------------
    # Capital / valuation context
    # ------------------------------------------------------------------
    account_equity: Optional[float] = None
    portfolio_value: Optional[float] = None
    collateral_value: Optional[float] = None
    margin_balance: Optional[float] = None
    used_margin: Optional[float] = None

    # ------------------------------------------------------------------
    # Exposure ratios
    # ------------------------------------------------------------------
    gross_exposure_ratio: Optional[float] = None
    net_exposure_ratio: Optional[float] = None
    long_exposure_ratio: Optional[float] = None
    short_exposure_ratio: Optional[float] = None

    # ------------------------------------------------------------------
    # Position / order context
    # ------------------------------------------------------------------
    position_count: Optional[int] = None
    open_order_count: Optional[int] = None

    # ------------------------------------------------------------------
    # Related references
    # ------------------------------------------------------------------
    position_id: Optional[str] = None
    order_id: Optional[str] = None
    execution_id: Optional[str] = None
    transaction_id: Optional[str] = None
    margin_id: Optional[str] = None
    leverage_id: Optional[str] = None

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
        # Sequence validation
        # --------------------------------------------------------------
        if self.sequence is not None:
            if isinstance(self.sequence, bool) or not isinstance(
                self.sequence, int
            ):
                raise TypeError(
                    "sequence must be an integer when provided."
                )

            if self.sequence < 0:
                raise ValueError(
                    "sequence must be non-negative."
                )

        # --------------------------------------------------------------
        # Integer field validation
        # --------------------------------------------------------------
        integer_fields = (
            "position_count",
            "open_order_count",
        )

        for field_name in integer_fields:
            value = getattr(self, field_name)

            if value is None:
                continue

            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(
                    f"{field_name} must be an integer when provided."
                )

            if value < 0:
                raise ValueError(
                    f"{field_name} cannot be negative."
                )

        # --------------------------------------------------------------
        # Numeric field validation
        #
        # Rules:
        #   - bool is not accepted as numeric data
        #   - numeric strings are rejected
        #   - NaN is rejected
        #   - +Inf/-Inf are rejected
        #   - finite real numeric values are accepted
        #
        # Net exposure and net exposure ratio may be negative because
        # they represent directional/net state.
        # --------------------------------------------------------------
        numeric_fields = (
            "gross_exposure",
            "net_exposure",
            "long_exposure",
            "short_exposure",
            "quantity",
            "long_quantity",
            "short_quantity",
            "notional_value",
            "long_notional_value",
            "short_notional_value",
            "account_equity",
            "portfolio_value",
            "collateral_value",
            "margin_balance",
            "used_margin",
            "gross_exposure_ratio",
            "net_exposure_ratio",
            "long_exposure_ratio",
            "short_exposure_ratio",
        )

        signed_numeric_fields = {
            "net_exposure",
            "net_exposure_ratio",
        }

        for field_name in numeric_fields:
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

            if (
                field_name not in signed_numeric_fields
                and numeric_value < 0
            ):
                raise ValueError(
                    f"{field_name} cannot be negative."
                )

        # --------------------------------------------------------------
        # Currency validation
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
        return bool(self.exposure_id)

    def has_exposure_identity(self) -> bool:
        return self.has_identity()

    def has_account_identity(self) -> bool:
        return bool(self.account_id)

    def has_portfolio_identity(self) -> bool:
        return bool(self.portfolio_id)

    def has_market_identity(self) -> bool:
        return bool(
            self.market
            or self.instrument
            or self.symbol
            or self.exchange
            or self.venue
        )

    def has_timestamp(self) -> bool:
        return bool(self.timestamp)

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
    # Exposure measurements
    # ------------------------------------------------------------------

    def has_gross_exposure(self) -> bool:
        return self.gross_exposure is not None

    def has_net_exposure(self) -> bool:
        return self.net_exposure is not None

    def has_long_exposure(self) -> bool:
        return self.long_exposure is not None

    def has_short_exposure(self) -> bool:
        return self.short_exposure is not None

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
    # Quantity / notional
    # ------------------------------------------------------------------

    def has_quantity(self) -> bool:
        return self.quantity is not None

    def has_notional_value(self) -> bool:
        return self.notional_value is not None

    def has_directional_quantity(self) -> bool:
        return (
            self.long_quantity is not None
            or self.short_quantity is not None
        )

    def has_directional_notional(self) -> bool:
        return (
            self.long_notional_value is not None
            or self.short_notional_value is not None
        )

    # ------------------------------------------------------------------
    # Capital context
    # ------------------------------------------------------------------

    def has_account_equity(self) -> bool:
        return self.account_equity is not None

    def has_portfolio_value(self) -> bool:
        return self.portfolio_value is not None

    def has_collateral(self) -> bool:
        return self.collateral_value is not None

    def has_margin_context(self) -> bool:
        return (
            self.margin_balance is not None
            or self.used_margin is not None
        )

    # ------------------------------------------------------------------
    # Exposure ratios
    # ------------------------------------------------------------------

    def has_exposure_ratios(self) -> bool:
        return any(
            value is not None
            for value in (
                self.gross_exposure_ratio,
                self.net_exposure_ratio,
                self.long_exposure_ratio,
                self.short_exposure_ratio,
            )
        )

    # ------------------------------------------------------------------
    # Structural calculations
    # ------------------------------------------------------------------

    def calculate_gross_exposure(self) -> Optional[float]:
        """
        Calculate gross exposure from long and short exposure.
        """

        if (
            self.long_exposure is None
            and self.short_exposure is None
        ):
            return None

        return abs(float(self.long_exposure or 0.0)) + abs(
            float(self.short_exposure or 0.0)
        )

    def calculate_net_exposure(self) -> Optional[float]:
        """
        Calculate net exposure as long exposure minus short exposure.
        """

        if (
            self.long_exposure is None
            and self.short_exposure is None
        ):
            return None

        return float(self.long_exposure or 0.0) - float(
            self.short_exposure or 0.0
        )

    def calculate_exposure_ratio(
        self,
        *,
        exposure: Optional[float] = None,
        capital_base: Optional[float] = None,
    ) -> Optional[float]:
        """
        Calculate exposure ratio as exposure / capital base.

        No leverage or risk decision is performed here.
        """

        exposure_value = (
            exposure
            if exposure is not None
            else self.gross_exposure
        )

        capital_value = (
            capital_base
            if capital_base is not None
            else self.account_equity
        )

        if exposure_value is None or capital_value is None:
            return None

        capital_numeric = float(capital_value)

        if capital_numeric <= 0:
            return None

        return float(exposure_value) / capital_numeric

    def calculate_gross_exposure_ratio(self) -> Optional[float]:
        return self.calculate_exposure_ratio(
            exposure=self.gross_exposure,
            capital_base=self.account_equity,
        )

    def calculate_net_exposure_ratio(self) -> Optional[float]:
        if self.net_exposure is None or self.account_equity is None:
            return None

        equity = float(self.account_equity)

        if equity <= 0:
            return None

        return float(self.net_exposure) / equity

    def calculate_long_exposure_ratio(self) -> Optional[float]:
        return self.calculate_exposure_ratio(
            exposure=self.long_exposure,
            capital_base=self.account_equity,
        )

    def calculate_short_exposure_ratio(self) -> Optional[float]:
        return self.calculate_exposure_ratio(
            exposure=self.short_exposure,
            capital_base=self.account_equity,
        )

    # ------------------------------------------------------------------
    # Position / order state
    # ------------------------------------------------------------------

    def has_position_count(self) -> bool:
        return self.position_count is not None

    def has_open_order_count(self) -> bool:
        return self.open_order_count is not None

    # ------------------------------------------------------------------
    # Related references
    # ------------------------------------------------------------------

    def has_position_reference(self) -> bool:
        return bool(self.position_id)

    def has_order_reference(self) -> bool:
        return bool(self.order_id)

    def has_execution_reference(self) -> bool:
        return bool(self.execution_id)

    def has_transaction_reference(self) -> bool:
        return bool(self.transaction_id)

    def has_margin_reference(self) -> bool:
        return bool(self.margin_id)

    def has_leverage_reference(self) -> bool:
        return bool(self.leverage_id)

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

        if not self.exposure_id:
            issues.append("MISSING_EXPOSURE_ID")

        if not self.account_id and not self.portfolio_id:
            issues.append("MISSING_ACCOUNT_OR_PORTFOLIO_ID")

        if not self.timestamp:
            issues.append("MISSING_TIMESTAMP")

        if not self.has_market_identity():
            issues.append("MISSING_MARKET_IDENTITY")

        if not self.currency and not self.base_currency:
            issues.append("MISSING_CURRENCY")

        if (
            self.gross_exposure is not None
            and self.gross_exposure < 0
        ):
            issues.append("NEGATIVE_GROSS_EXPOSURE")

        if (
            self.long_exposure is not None
            and self.short_exposure is not None
            and self.gross_exposure is not None
        ):
            calculated_gross = (
                abs(float(self.long_exposure))
                + abs(float(self.short_exposure))
            )

            if abs(
                float(self.gross_exposure) - calculated_gross
            ) > 1e-9:
                issues.append("GROSS_EXPOSURE_MISMATCH")

        if (
            self.account_equity is not None
            and self.account_equity < 0
        ):
            issues.append("NEGATIVE_ACCOUNT_EQUITY")

        if (
            self.used_margin is not None
            and self.margin_balance is not None
            and self.used_margin > self.margin_balance
        ):
            issues.append("USED_MARGIN_EXCEEDS_MARGIN_BALANCE")

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
            "schema": MARKET_EXPOSURE_SCHEMA,
            "version": MARKET_EXPOSURE_SCHEMA_VERSION,
            "immutable": True,
            "currency_agnostic": True,
            "supports_inr": True,
            "supports_usd": True,
            "supports_usdt": True,
            "gross_exposure_supported": True,
            "net_exposure_supported": True,
            "long_exposure_supported": True,
            "short_exposure_supported": True,
            "exposure_ratio_supported": True,
            "margin_separated": True,
            "leverage_separated": True,
            "observed_derived_separation": True,
            "provenance_supported": True,
            "decision_logic": False,
            "execution_authorization": False,
            "v7_dependency": False,
        }


# ----------------------------------------------------------------------
# Health
# ----------------------------------------------------------------------

def market_exposure_health() -> dict[str, Any]:
    return {
        "schema": MARKET_EXPOSURE_SCHEMA,
        "version": MARKET_EXPOSURE_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "currency_agnostic": True,
        "supports_inr": True,
        "supports_usd": True,
        "supports_usdt": True,
        "gross_exposure_supported": True,
        "net_exposure_supported": True,
        "long_exposure_supported": True,
        "short_exposure_supported": True,
        "exposure_ratio_supported": True,
        "position_context_supported": True,
        "margin_separation": True,
        "leverage_separation": True,
        "observed_derived_separation": True,
        "provenance_supported": True,
        "decision_logic": False,
        "execution_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_EXPOSURE_SCHEMA_VERSION",
    "MARKET_EXPOSURE_SCHEMA",
    "MarketExposure",
    "market_exposure_health",
]