"""
ROBOMLM PLUS
V6 Market Fee Schema

Purpose:
    Structural representation of fees and charges associated with
    market, trading, brokerage, exchange, funding, settlement, and
    other account-related activities.

Design rules:
    - Immutable schema.
    - Currency agnostic: INR, USD, USDT, etc.
    - Fee structure is distinct from cashflow and account balance.
    - No trading decisions.
    - No execution authorization.
    - No risk decisions.
    - No V7+ dependency.
    - Observed and derived values remain explicitly separated.
    - Provenance is preserved.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional


MARKET_FEE_SCHEMA_VERSION = "1.0.0"
MARKET_FEE_SCHEMA = "V6_MARKET_FEE"


@dataclass(frozen=True)
class MarketFee:
    """
    Immutable structural representation of a fee or charge.

    Examples:
        - BROKERAGE
        - EXCHANGE_FEE
        - TRANSACTION_FEE
        - FUNDING_FEE
        - COMMISSION
        - TAX
        - SETTLEMENT_FEE
        - DATA_FEE
        - OTHER
    """

    # ------------------------------------------------------------------
    # Fee identity
    # ------------------------------------------------------------------
    fee_id: Optional[str] = None
    account_id: Optional[str] = None
    timestamp: Optional[str] = None
    sequence: Optional[int] = None

    # ------------------------------------------------------------------
    # Currency identity
    # ------------------------------------------------------------------
    currency: Optional[str] = None
    base_currency: Optional[str] = None

    # ------------------------------------------------------------------
    # Market / environment identity
    # ------------------------------------------------------------------
    market: Optional[str] = None
    instrument: Optional[str] = None
    symbol: Optional[str] = None
    exchange: Optional[str] = None
    venue: Optional[str] = None
    broker: Optional[str] = None
    provider: Optional[str] = None
    environment: Optional[str] = None
    mode: Optional[str] = None

    # ------------------------------------------------------------------
    # Fee classification
    # ------------------------------------------------------------------
    fee_type: Optional[str] = None
    fee_category: Optional[str] = None
    fee_state: Optional[str] = None
    direction: Optional[str] = None

    # ------------------------------------------------------------------
    # Fee amount
    # ------------------------------------------------------------------
    amount: Optional[float] = None
    gross_amount: Optional[float] = None
    net_amount: Optional[float] = None
    rate: Optional[float] = None

    # ------------------------------------------------------------------
    # Fee calculation context
    # ------------------------------------------------------------------
    calculation_base: Optional[float] = None
    quantity: Optional[float] = None
    price: Optional[float] = None
    minimum_fee: Optional[float] = None
    maximum_fee: Optional[float] = None

    # ------------------------------------------------------------------
    # Related transaction context
    # ------------------------------------------------------------------
    transaction_id: Optional[str] = None
    order_id: Optional[str] = None
    execution_id: Optional[str] = None
    cashflow_id: Optional[str] = None

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
            "amount",
            "gross_amount",
            "net_amount",
            "rate",
            "calculation_base",
            "quantity",
            "price",
            "minimum_fee",
            "maximum_fee",
        )

        for field_name in numeric_fields:
            value = getattr(self, field_name)

            if value is not None:
                try:
                    numeric_value = float(value)
                except (TypeError, ValueError) as exc:
                    raise ValueError(
                        f"{field_name} must be numeric when provided."
                    ) from exc

                if field_name in {
                    "amount",
                    "gross_amount",
                    "net_amount",
                    "calculation_base",
                    "quantity",
                    "price",
                    "minimum_fee",
                    "maximum_fee",
                } and numeric_value < 0:
                    raise ValueError(
                        f"{field_name} cannot be negative."
                    )

                if field_name == "rate" and numeric_value < 0:
                    raise ValueError("rate cannot be negative.")

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
        return bool(self.fee_id)

    def has_fee_identity(self) -> bool:
        return self.has_identity()

    def has_account_identity(self) -> bool:
        return bool(self.account_id)

    def has_timestamp(self) -> bool:
        return bool(self.timestamp)

    # ------------------------------------------------------------------
    # Currency
    # ------------------------------------------------------------------

    def has_currency(self) -> bool:
        return bool(self.currency or self.base_currency)

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
    # Fee classification
    # ------------------------------------------------------------------

    def has_type(self) -> bool:
        return bool(self.fee_type)

    def has_category(self) -> bool:
        return bool(self.fee_category)

    def has_state(self) -> bool:
        return bool(self.fee_state)

    def has_direction(self) -> bool:
        return bool(self.direction)

    def is_inflow(self) -> bool:
        return str(self.direction or "").upper() in {
            "IN",
            "INFLOW",
            "CREDIT",
            "POSITIVE",
        }

    def is_outflow(self) -> bool:
        return str(self.direction or "").upper() in {
            "OUT",
            "OUTFLOW",
            "DEBIT",
            "NEGATIVE",
        }

    # ------------------------------------------------------------------
    # Amount state
    # ------------------------------------------------------------------

    def has_amount(self) -> bool:
        return self.amount is not None

    def has_rate(self) -> bool:
        return self.rate is not None

    def has_calculation_base(self) -> bool:
        return self.calculation_base is not None

    # ------------------------------------------------------------------
    # Fee calculation
    # ------------------------------------------------------------------

    def calculate_fee_from_rate(self) -> Optional[float]:
        """
        Calculate fee from calculation_base and rate.

        Rate is interpreted as a decimal rate.

        Example:
            calculation_base = 100000
            rate = 0.001
            fee = 100
        """

        if self.calculation_base is None or self.rate is None:
            return None

        return float(self.calculation_base) * float(self.rate)

    def calculate_fee_from_rate_percent(self) -> Optional[float]:
        """
        Calculate fee when rate is represented as a percentage.

        Example:
            calculation_base = 100000
            rate = 0.1
            fee = 100
        """

        if self.calculation_base is None or self.rate is None:
            return None

        return (
            float(self.calculation_base)
            * float(self.rate)
            / 100.0
        )

    def calculate_notional(self) -> Optional[float]:
        """
        Calculate quantity × price when both are available.
        """

        if self.quantity is None or self.price is None:
            return None

        return float(self.quantity) * float(self.price)

    def calculate_capped_fee(
        self,
        calculated_fee: Optional[float] = None,
    ) -> Optional[float]:
        """
        Apply optional minimum and maximum fee boundaries.

        This is a structural calculation only.
        """

        value = (
            calculated_fee
            if calculated_fee is not None
            else self.calculate_fee_from_rate()
        )

        if value is None:
            return None

        result = float(value)

        if self.minimum_fee is not None:
            result = max(result, float(self.minimum_fee))

        if self.maximum_fee is not None:
            result = min(result, float(self.maximum_fee))

        return result

    # ------------------------------------------------------------------
    # Related references
    # ------------------------------------------------------------------

    def has_transaction_reference(self) -> bool:
        return bool(self.transaction_id)

    def has_order_reference(self) -> bool:
        return bool(self.order_id)

    def has_execution_reference(self) -> bool:
        return bool(self.execution_id)

    def has_cashflow_reference(self) -> bool:
        return bool(self.cashflow_id)

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

        if not self.fee_id:
            issues.append("MISSING_FEE_ID")

        if not self.account_id:
            issues.append("MISSING_ACCOUNT_ID")

        if not self.timestamp:
            issues.append("MISSING_TIMESTAMP")

        if not self.currency and not self.base_currency:
            issues.append("MISSING_CURRENCY")

        if self.maximum_fee is not None and self.minimum_fee is not None:
            if self.maximum_fee < self.minimum_fee:
                issues.append("MAXIMUM_FEE_BELOW_MINIMUM_FEE")

        if self.amount is not None and self.net_amount is not None:
            if self.net_amount > self.amount:
                issues.append("NET_FEE_EXCEEDS_AMOUNT")

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
            "schema": MARKET_FEE_SCHEMA,
            "version": MARKET_FEE_SCHEMA_VERSION,
            "immutable": True,
            "currency_agnostic": True,
            "supports_inr": True,
            "supports_usd": True,
            "supports_usdt": True,
            "fee_separated_from_cashflow": True,
            "fee_separated_from_account_balance": True,
            "decision_logic": False,
            "execution_authorization": False,
            "v7_dependency": False,
        }


# ----------------------------------------------------------------------
# Health
# ----------------------------------------------------------------------

def market_fee_health() -> dict[str, Any]:
    return {
        "schema": MARKET_FEE_SCHEMA,
        "version": MARKET_FEE_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "currency_agnostic": True,
        "supports_inr": True,
        "supports_usd": True,
        "supports_usdt": True,
        "rate_calculation_supported": True,
        "minimum_maximum_fee_supported": True,
        "transaction_reference_supported": True,
        "execution_reference_supported": True,
        "cashflow_reference_supported": True,
        "observed_derived_separation": True,
        "provenance_supported": True,
        "decision_logic": False,
        "execution_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_FEE_SCHEMA_VERSION",
    "MARKET_FEE_SCHEMA",
    "MarketFee",
    "market_fee_health",
]