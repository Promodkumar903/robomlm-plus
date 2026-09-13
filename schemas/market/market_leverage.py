"""
ROBOMLM PLUS
V6 Market Leverage Schema

Purpose:
    Structural representation of leverage state and leverage measurements.

Design rules:
    - Immutable schema.
    - Currency agnostic: INR, USD, USDT, etc.
    - Leverage is distinct from margin and account balance.
    - Supports observed and derived leverage values.
    - No trading decisions.
    - No execution authorization.
    - No risk decisions.
    - No V7+ dependency.
    - Broker/provider-specific rules remain outside this schema.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional


MARKET_LEVERAGE_SCHEMA_VERSION = "1.0.0"
MARKET_LEVERAGE_SCHEMA = "V6_MARKET_LEVERAGE"


@dataclass(frozen=True)
class MarketLeverage:
    """
    Immutable structural representation of leverage.

    Supports:
        - Leverage identity
        - Market/account context
        - Gross/net exposure
        - Collateral
        - Initial/maintenance margin
        - Used/free margin
        - Leverage ratio
        - Maximum/reference leverage
    """

    # ------------------------------------------------------------------
    # Leverage identity
    # ------------------------------------------------------------------
    leverage_id: Optional[str] = None
    account_id: Optional[str] = None
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
    # Leverage classification
    # ------------------------------------------------------------------
    leverage_type: Optional[str] = None
    leverage_mode: Optional[str] = None
    leverage_state: Optional[str] = None

    # ------------------------------------------------------------------
    # Exposure
    # ------------------------------------------------------------------
    gross_exposure: Optional[float] = None
    net_exposure: Optional[float] = None
    long_exposure: Optional[float] = None
    short_exposure: Optional[float] = None

    # ------------------------------------------------------------------
    # Collateral / capital base
    # ------------------------------------------------------------------
    collateral_value: Optional[float] = None
    account_equity: Optional[float] = None
    margin_balance: Optional[float] = None
    available_balance: Optional[float] = None

    # ------------------------------------------------------------------
    # Margin context
    # ------------------------------------------------------------------
    initial_margin: Optional[float] = None
    maintenance_margin: Optional[float] = None
    margin_requirement: Optional[float] = None
    used_margin: Optional[float] = None
    free_margin: Optional[float] = None

    # ------------------------------------------------------------------
    # Leverage measurements
    # ------------------------------------------------------------------
    leverage_ratio: Optional[float] = None
    gross_leverage: Optional[float] = None
    net_leverage: Optional[float] = None
    maximum_leverage: Optional[float] = None
    reference_leverage: Optional[float] = None

    # ------------------------------------------------------------------
    # Related references
    # ------------------------------------------------------------------
    position_id: Optional[str] = None
    order_id: Optional[str] = None
    execution_id: Optional[str] = None
    transaction_id: Optional[str] = None
    margin_id: Optional[str] = None

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

        if self.sequence is not None and self.sequence < 0:
            raise ValueError("sequence must be non-negative.")

        numeric_fields = (
            "gross_exposure",
            "net_exposure",
            "long_exposure",
            "short_exposure",
            "collateral_value",
            "account_equity",
            "margin_balance",
            "available_balance",
            "initial_margin",
            "maintenance_margin",
            "margin_requirement",
            "used_margin",
            "free_margin",
            "leverage_ratio",
            "gross_leverage",
            "net_leverage",
            "maximum_leverage",
            "reference_leverage",
        )

        for field_name in numeric_fields:
            value = getattr(self, field_name)

            if value is None:
                continue

            try:
                numeric_value = float(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"{field_name} must be numeric when provided."
                ) from exc

            if field_name not in {
                "net_exposure",
                "short_exposure",
                "net_leverage",
            } and numeric_value < 0:
                raise ValueError(
                    f"{field_name} cannot be negative."
                )

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
        return bool(self.leverage_id)

    def has_leverage_identity(self) -> bool:
        return self.has_identity()

    def has_account_identity(self) -> bool:
        return bool(self.account_id)

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
        return (
            self.gross_exposure is not None
            or self.net_exposure is not None
            or self.long_exposure is not None
            or self.short_exposure is not None
        )

    # ------------------------------------------------------------------
    # Collateral / capital
    # ------------------------------------------------------------------

    def has_collateral(self) -> bool:
        return self.collateral_value is not None

    def has_account_equity(self) -> bool:
        return self.account_equity is not None

    def has_margin_balance(self) -> bool:
        return self.margin_balance is not None

    def has_available_balance(self) -> bool:
        return self.available_balance is not None

    # ------------------------------------------------------------------
    # Margin
    # ------------------------------------------------------------------

    def has_initial_margin(self) -> bool:
        return self.initial_margin is not None

    def has_maintenance_margin(self) -> bool:
        return self.maintenance_margin is not None

    def has_margin_requirement(self) -> bool:
        return self.margin_requirement is not None

    def has_used_margin(self) -> bool:
        return self.used_margin is not None

    def has_free_margin(self) -> bool:
        return self.free_margin is not None

    # ------------------------------------------------------------------
    # Leverage
    # ------------------------------------------------------------------

    def has_leverage_ratio(self) -> bool:
        return self.leverage_ratio is not None

    def has_gross_leverage(self) -> bool:
        return self.gross_leverage is not None

    def has_net_leverage(self) -> bool:
        return self.net_leverage is not None

    def has_maximum_leverage(self) -> bool:
        return self.maximum_leverage is not None

    # ------------------------------------------------------------------
    # Structural calculations
    # ------------------------------------------------------------------

    def calculate_leverage(
        self,
        *,
        exposure: Optional[float] = None,
        collateral: Optional[float] = None,
    ) -> Optional[float]:
        """
        Calculate leverage as exposure divided by collateral.

        If explicit arguments are not supplied, the method uses:
            exposure  -> gross_exposure
            collateral -> collateral_value

        No trading or risk decision is made.
        """

        exposure_value = (
            exposure
            if exposure is not None
            else self.gross_exposure
        )

        collateral_value = (
            collateral
            if collateral is not None
            else self.collateral_value
        )

        if exposure_value is None or collateral_value is None:
            return None

        collateral_numeric = float(collateral_value)

        if collateral_numeric <= 0:
            return None

        return float(exposure_value) / collateral_numeric

    def calculate_gross_leverage(self) -> Optional[float]:
        """
        Calculate gross leverage from gross exposure and collateral.
        """

        return self.calculate_leverage(
            exposure=self.gross_exposure,
            collateral=self.collateral_value,
        )

    def calculate_net_leverage(self) -> Optional[float]:
        """
        Calculate net leverage from net exposure and collateral.

        The absolute value is used because net exposure may be negative.
        """

        if self.net_exposure is None or self.collateral_value is None:
            return None

        collateral = float(self.collateral_value)

        if collateral <= 0:
            return None

        return abs(float(self.net_exposure)) / collateral

    def calculate_leverage_from_equity(self) -> Optional[float]:
        """
        Calculate gross leverage using account equity as the capital base.
        """

        if self.gross_exposure is None or self.account_equity is None:
            return None

        equity = float(self.account_equity)

        if equity <= 0:
            return None

        return float(self.gross_exposure) / equity

    def calculate_free_margin(self) -> Optional[float]:
        """
        Calculate free margin from margin balance minus used margin.
        """

        if self.margin_balance is None:
            return None

        return float(self.margin_balance) - float(
            self.used_margin or 0.0
        )

    def calculate_margin_utilization(self) -> Optional[float]:
        """
        Calculate margin utilization as used margin / margin balance.
        """

        if self.margin_balance is None or self.used_margin is None:
            return None

        balance = float(self.margin_balance)

        if balance <= 0:
            return None

        return float(self.used_margin) / balance

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

        if not self.leverage_id:
            issues.append("MISSING_LEVERAGE_ID")

        if not self.account_id:
            issues.append("MISSING_ACCOUNT_ID")

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
            self.free_margin is not None
            and self.margin_balance is not None
            and self.free_margin > self.margin_balance
        ):
            issues.append("FREE_MARGIN_EXCEEDS_MARGIN_BALANCE")

        if (
            self.maximum_leverage is not None
            and self.maximum_leverage <= 0
        ):
            issues.append("INVALID_MAXIMUM_LEVERAGE")

        if (
            self.reference_leverage is not None
            and self.reference_leverage <= 0
        ):
            issues.append("INVALID_REFERENCE_LEVERAGE")

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
            "schema": MARKET_LEVERAGE_SCHEMA,
            "version": MARKET_LEVERAGE_SCHEMA_VERSION,
            "immutable": True,
            "currency_agnostic": True,
            "supports_inr": True,
            "supports_usd": True,
            "supports_usdt": True,
            "exposure_supported": True,
            "collateral_supported": True,
            "margin_context_supported": True,
            "gross_leverage_supported": True,
            "net_leverage_supported": True,
            "maximum_leverage_supported": True,
            "observed_derived_separation": True,
            "provenance_supported": True,
            "decision_logic": False,
            "execution_authorization": False,
            "v7_dependency": False,
        }


# ----------------------------------------------------------------------
# Health
# ----------------------------------------------------------------------

def market_leverage_health() -> dict[str, Any]:
    return {
        "schema": MARKET_LEVERAGE_SCHEMA,
        "version": MARKET_LEVERAGE_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "currency_agnostic": True,
        "supports_inr": True,
        "supports_usd": True,
        "supports_usdt": True,
        "exposure_supported": True,
        "collateral_supported": True,
        "margin_context_supported": True,
        "leverage_ratio_supported": True,
        "gross_leverage_supported": True,
        "net_leverage_supported": True,
        "maximum_leverage_supported": True,
        "observed_derived_separation": True,
        "provenance_supported": True,
        "decision_logic": False,
        "execution_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_LEVERAGE_SCHEMA_VERSION",
    "MARKET_LEVERAGE_SCHEMA",
    "MarketLeverage",
    "market_leverage_health",
]