"""
ROBOMLM PLUS
V6 Market Cashflow Schema

Purpose:
    Structural representation of account-level cash and balance movements.

Design rules:
    - Immutable schema.
    - Currency agnostic: INR, USD, USDT, etc.
    - One record represents one cashflow event or movement.
    - Cashflow is distinct from account balance snapshot.
    - No trading decisions.
    - No execution authorization.
    - No risk decisions.
    - No V7+ dependency.
    - Observed and derived values remain explicitly separated.
    - Provenance is preserved.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from math import isfinite
from types import MappingProxyType
from typing import Any, Mapping, Optional


MARKET_CASHFLOW_SCHEMA_VERSION = "1.0.0"
MARKET_CASHFLOW_SCHEMA = "V6_MARKET_CASHFLOW"


_INFLOW_DIRECTIONS = {
    "IN",
    "INFLOW",
    "CREDIT",
    "POSITIVE",
}

_OUTFLOW_DIRECTIONS = {
    "OUT",
    "OUTFLOW",
    "DEBIT",
    "NEGATIVE",
}


@dataclass(frozen=True)
class MarketCashflow:
    """
    Immutable structural representation of a cashflow movement.

    Examples:
        - DEPOSIT
        - WITHDRAWAL
        - TRANSFER_IN
        - TRANSFER_OUT
        - FEE
        - FUNDING
        - REALIZED_PNL
        - ADJUSTMENT
    """

    # ------------------------------------------------------------------
    # Cashflow identity
    # ------------------------------------------------------------------
    cashflow_id: Optional[str] = None
    account_id: Optional[str] = None
    timestamp: Optional[str] = None
    sequence: Optional[int] = None

    # ------------------------------------------------------------------
    # Currency / environment identity
    # ------------------------------------------------------------------
    currency: Optional[str] = None
    base_currency: Optional[str] = None
    broker: Optional[str] = None
    provider: Optional[str] = None
    venue: Optional[str] = None
    environment: Optional[str] = None
    mode: Optional[str] = None

    # ------------------------------------------------------------------
    # Cashflow classification
    # ------------------------------------------------------------------
    cashflow_type: Optional[str] = None
    cashflow_state: Optional[str] = None
    direction: Optional[str] = None

    # ------------------------------------------------------------------
    # Amount
    # ------------------------------------------------------------------
    amount: Optional[float] = None
    signed_amount: Optional[float] = None
    gross_amount: Optional[float] = None
    fee_amount: Optional[float] = None
    net_amount: Optional[float] = None

    # ------------------------------------------------------------------
    # Balance context
    # ------------------------------------------------------------------
    balance_before: Optional[float] = None
    balance_after: Optional[float] = None

    # ------------------------------------------------------------------
    # Transfer / external references
    # ------------------------------------------------------------------
    transfer_id: Optional[str] = None
    transaction_id: Optional[str] = None
    order_id: Optional[str] = None
    execution_id: Optional[str] = None

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
    provenance: Mapping[str, Any] = field(
        default_factory=dict,
        repr=True,
        compare=True,
    )

    # ------------------------------------------------------------------
    # Explicit observed / derived separation
    # ------------------------------------------------------------------
    observed_fields: tuple[str, ...] = field(default_factory=tuple)
    derived_fields: tuple[str, ...] = field(default_factory=tuple)

    # ------------------------------------------------------------------
    # Additional metadata
    # ------------------------------------------------------------------
    metadata: Mapping[str, Any] = field(
        default_factory=dict,
        repr=True,
        compare=True,
    )

    def __post_init__(self) -> None:
        """Validate and normalize structural invariants."""

        # --------------------------------------------------------------
        # Sequence
        # --------------------------------------------------------------
        if self.sequence is not None:
            if isinstance(self.sequence, bool):
                raise ValueError("sequence must be an integer.")

            try:
                sequence_value = int(self.sequence)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    "sequence must be an integer."
                ) from exc

            if sequence_value != self.sequence:
                raise ValueError("sequence must be an integer.")

            if sequence_value < 0:
                raise ValueError("sequence must be non-negative.")

        # --------------------------------------------------------------
        # Numeric fields
        # --------------------------------------------------------------
        numeric_fields = (
            "amount",
            "signed_amount",
            "gross_amount",
            "fee_amount",
            "net_amount",
            "balance_before",
            "balance_after",
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

            if not isfinite(numeric_value):
                raise ValueError(
                    f"{field_name} must be finite when provided."
                )

        # --------------------------------------------------------------
        # Absolute amount invariants
        # --------------------------------------------------------------
        if self.amount is not None and float(self.amount) < 0:
            raise ValueError("amount must be non-negative.")

        if self.fee_amount is not None and float(self.fee_amount) < 0:
            raise ValueError("fee_amount must be non-negative.")

        # --------------------------------------------------------------
        # Currency invariants
        # --------------------------------------------------------------
        if self.currency is not None and not str(self.currency).strip():
            raise ValueError("currency cannot be empty.")

        if (
            self.base_currency is not None
            and not str(self.base_currency).strip()
        ):
            raise ValueError("base_currency cannot be empty.")

        # --------------------------------------------------------------
        # Immutable structural containers
        # --------------------------------------------------------------
        object.__setattr__(
            self,
            "observed_fields",
            tuple(self.observed_fields),
        )

        object.__setattr__(
            self,
            "derived_fields",
            tuple(self.derived_fields),
        )

        object.__setattr__(
            self,
            "provenance",
            MappingProxyType(dict(self.provenance)),
        )

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    def has_identity(self) -> bool:
        return bool(self.cashflow_id)

    def has_cashflow_identity(self) -> bool:
        return self.has_identity()

    def has_account_identity(self) -> bool:
        return bool(self.account_id)

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
            or self.venue
            or self.environment
            or self.mode
        )

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------

    def has_type(self) -> bool:
        return bool(self.cashflow_type)

    def has_state(self) -> bool:
        return bool(self.cashflow_state)

    def has_direction(self) -> bool:
        return bool(self.direction)

    def is_inflow(self) -> bool:
        if self.signed_amount is not None:
            return float(self.signed_amount) > 0

        return str(self.direction or "").strip().upper() in (
            _INFLOW_DIRECTIONS
        )

    def is_outflow(self) -> bool:
        if self.signed_amount is not None:
            return float(self.signed_amount) < 0

        return str(self.direction or "").strip().upper() in (
            _OUTFLOW_DIRECTIONS
        )

    # ------------------------------------------------------------------
    # Amount state
    # ------------------------------------------------------------------

    def has_amount(self) -> bool:
        return self.amount is not None

    def has_signed_amount(self) -> bool:
        return self.signed_amount is not None

    def has_net_amount(self) -> bool:
        return self.net_amount is not None

    def has_balance_context(self) -> bool:
        return (
            self.balance_before is not None
            or self.balance_after is not None
        )

    # ------------------------------------------------------------------
    # Calculations
    # ------------------------------------------------------------------

    def calculate_signed_amount(self) -> Optional[float]:
        """
        Derive a signed amount from amount and direction.

        Positive = inflow.
        Negative = outflow.

        If signed_amount is already supplied, it is returned unchanged.

        If direction is missing or unrecognized, no directional assumption
        is made and None is returned.
        """

        if self.signed_amount is not None:
            return float(self.signed_amount)

        if self.amount is None:
            return None

        direction = str(self.direction or "").strip().upper()

        if direction in _OUTFLOW_DIRECTIONS:
            return -abs(float(self.amount))

        if direction in _INFLOW_DIRECTIONS:
            return abs(float(self.amount))

        return None

    def calculate_net_amount(self) -> Optional[float]:
        """
        Derive net cashflow amount from gross amount and fee.

        Fees are treated as deductions when fee_amount is supplied.

        For positive gross values:
            net = gross - fee

        For negative gross values:
            net = gross + fee
        """

        if self.net_amount is not None:
            return float(self.net_amount)

        if self.gross_amount is None and self.amount is None:
            return None

        gross = (
            float(self.gross_amount)
            if self.gross_amount is not None
            else float(self.amount)
        )

        if self.fee_amount is None:
            return gross

        fee = abs(float(self.fee_amount))

        if gross >= 0:
            return gross - fee

        return gross + fee

    def calculate_balance_change(self) -> Optional[float]:
        """
        Calculate balance change from before/after balances.
        """

        if (
            self.balance_before is None
            or self.balance_after is None
        ):
            return None

        return (
            float(self.balance_after)
            - float(self.balance_before)
        )

    # ------------------------------------------------------------------
    # Reference state
    # ------------------------------------------------------------------

    def has_transfer_reference(self) -> bool:
        return bool(self.transfer_id)

    def has_transaction_reference(self) -> bool:
        return bool(self.transaction_id)

    def has_order_reference(self) -> bool:
        return bool(self.order_id)

    def has_execution_reference(self) -> bool:
        return bool(self.execution_id)

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

        if not self.cashflow_id:
            issues.append("MISSING_CASHFLOW_ID")

        if not self.account_id:
            issues.append("MISSING_ACCOUNT_ID")

        if not self.timestamp:
            issues.append("MISSING_TIMESTAMP")

        if not self.currency and not self.base_currency:
            issues.append("MISSING_CURRENCY")

        if self.amount is not None and float(self.amount) < 0:
            issues.append("NEGATIVE_ABSOLUTE_AMOUNT")

        if self.fee_amount is not None and float(self.fee_amount) < 0:
            issues.append("NEGATIVE_FEE_AMOUNT")

        if (
            self.balance_before is not None
            and self.balance_after is not None
            and self.signed_amount is not None
        ):
            balance_change = self.calculate_balance_change()
            signed_amount = float(self.signed_amount)

            if balance_change is not None:
                if abs(
                    float(balance_change) - signed_amount
                ) > 1e-9:
                    issues.append("BALANCE_CHANGE_MISMATCH")

        return issues

    def is_structurally_valid(self) -> bool:
        return len(self.issue_flags()) == 0

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """
        Return a plain serializable dictionary.

        Internal immutable mappings are converted to ordinary dictionaries
        at the serialization boundary.
        """
        return {
        "cashflow_id": self.cashflow_id,
        "account_id": self.account_id,
        "timestamp": self.timestamp,
        "sequence": self.sequence,
        "currency": self.currency,
        "broker": self.broker,
        "provider": self.provider,
        "venue": self.venue,
        "environment": self.environment,
        "mode": self.mode,
        "cashflow_type": self.cashflow_type,
        "cashflow_state": self.cashflow_state,
        "direction": self.direction,
        "amount": self.amount,
        "signed_amount": self.signed_amount,
        "gross_amount": self.gross_amount,
        "fee_amount": self.fee_amount,
        "net_amount": self.net_amount,
        "balance_before": self.balance_before,
        "balance_after": self.balance_after,
        "transfer_id": self.transfer_id,
        "transaction_id": self.transaction_id,
        "order_id": self.order_id,
        "execution_id": self.execution_id,
        "session_id": self.session_id,
        "request_id": self.request_id,
        "source": self.source,
        "source_type": self.source_type,
        "source_reference": self.source_reference,
        "provenance": dict(self.provenance),
        "observed_fields": tuple(self.observed_fields),
        "derived_fields": tuple(self.derived_fields),
        "metadata": dict(self.metadata),
    }
    def schema_info(self) -> dict[str, Any]:
        return {
            "schema": MARKET_CASHFLOW_SCHEMA,
            "version": MARKET_CASHFLOW_SCHEMA_VERSION,
            "immutable": True,
            "currency_agnostic": True,
            "balance_snapshot_logic": False,
            "decision_logic": False,
            "execution_authorization": False,
            "v7_dependency": False,
        }


# ----------------------------------------------------------------------
# Health
# ----------------------------------------------------------------------

def market_cashflow_health() -> dict[str, Any]:
    return {
        "schema": MARKET_CASHFLOW_SCHEMA,
        "version": MARKET_CASHFLOW_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "currency_agnostic": True,
        "supports_inr": True,
        "supports_usd": True,
        "supports_usdt": True,
        "balance_snapshot_separated": True,
        "observed_derived_separation": True,
        "provenance_supported": True,
        "decision_logic": False,
        "execution_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_CASHFLOW_SCHEMA_VERSION",
    "MARKET_CASHFLOW_SCHEMA",
    "MarketCashflow",
    "market_cashflow_health",
]
