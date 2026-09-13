"""
ROBOMLM PLUS
V6 Market Account Balance Schema

Purpose:
    Structural representation of account balance components
    and balance movements.

Design rules:
    - Immutable schema.
    - Balance is kept distinct from equity.
    - Balance is kept distinct from margin.
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
from numbers import Real
from typing import Any, Optional


MARKET_ACCOUNT_BALANCE_SCHEMA_VERSION = "1.0.0"
MARKET_ACCOUNT_BALANCE_SCHEMA = "V6_MARKET_ACCOUNT_BALANCE"


@dataclass(frozen=True)
class MarketAccountBalance:
    """
    Immutable structural representation of account balance state.

    This schema focuses on balance components and balance movements.
    Account-wide financial/risk state belongs to MarketAccount.
    """

    # ------------------------------------------------------------------
    # Balance identity
    # ------------------------------------------------------------------
    balance_id: Optional[str] = None
    account_id: Optional[str] = None
    timestamp: Optional[str] = None
    sequence: Optional[int] = None

    # ------------------------------------------------------------------
    # Currency / environment identity
    # ------------------------------------------------------------------
    base_currency: Optional[str] = None
    currency: Optional[str] = None
    broker: Optional[str] = None
    provider: Optional[str] = None
    venue: Optional[str] = None
    environment: Optional[str] = None
    mode: Optional[str] = None

    # ------------------------------------------------------------------
    # Balance components
    # ------------------------------------------------------------------
    cash_balance: Optional[float] = None
    available_balance: Optional[float] = None
    locked_balance: Optional[float] = None
    reserved_balance: Optional[float] = None

    # ------------------------------------------------------------------
    # Margin components
    # ------------------------------------------------------------------
    margin_balance: Optional[float] = None
    free_margin: Optional[float] = None
    used_margin: Optional[float] = None

    # ------------------------------------------------------------------
    # Balance movement components
    # ------------------------------------------------------------------
    opening_balance: Optional[float] = None
    closing_balance: Optional[float] = None
    deposit_amount: Optional[float] = None
    withdrawal_amount: Optional[float] = None
    transfer_amount: Optional[float] = None
    fees: Optional[float] = None
    funding: Optional[float] = None

    # ------------------------------------------------------------------
    # P&L contribution
    # ------------------------------------------------------------------
    realized_pnl: Optional[float] = None
    unrealized_pnl: Optional[float] = None
    net_change: Optional[float] = None

    # ------------------------------------------------------------------
    # Structural classification
    # ------------------------------------------------------------------
    balance_type: Optional[str] = None
    balance_state: Optional[str] = None

    # ------------------------------------------------------------------
    # Session / request references
    # ------------------------------------------------------------------
    session_id: Optional[str] = None
    request_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Source references
    # ------------------------------------------------------------------
    source: Optional[str] = None
    source_type: Optional[str] = None
    source_reference: Optional[str] = None

    # ------------------------------------------------------------------
    # Provenance
    # ------------------------------------------------------------------
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
        # Financial numeric validation
        # --------------------------------------------------------------
        numeric_fields = (
            "cash_balance",
            "available_balance",
            "locked_balance",
            "reserved_balance",
            "margin_balance",
            "free_margin",
            "used_margin",
            "opening_balance",
            "closing_balance",
            "deposit_amount",
            "withdrawal_amount",
            "transfer_amount",
            "fees",
            "funding",
            "realized_pnl",
            "unrealized_pnl",
            "net_change",
        )

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

        # --------------------------------------------------------------
        # Currency validation
        # --------------------------------------------------------------
        if self.currency is not None and not str(self.currency).strip():
            raise ValueError("currency cannot be empty.")

        if self.base_currency is not None and not str(
            self.base_currency
        ).strip():
            raise ValueError("base_currency cannot be empty.")

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    def has_identity(self) -> bool:
        return bool(self.balance_id)

    def has_balance_identity(self) -> bool:
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
    # Balance state
    # ------------------------------------------------------------------

    def has_cash_balance(self) -> bool:
        return self.cash_balance is not None

    def has_available_balance(self) -> bool:
        return self.available_balance is not None

    def has_locked_balance(self) -> bool:
        return self.locked_balance is not None

    def has_reserved_balance(self) -> bool:
        return self.reserved_balance is not None

    def has_balance_components(self) -> bool:
        return any(
            value is not None
            for value in (
                self.cash_balance,
                self.available_balance,
                self.locked_balance,
                self.reserved_balance,
            )
        )

    # ------------------------------------------------------------------
    # Margin state
    # ------------------------------------------------------------------

    def has_margin_balance(self) -> bool:
        return self.margin_balance is not None

    def has_free_margin(self) -> bool:
        return self.free_margin is not None

    def has_used_margin(self) -> bool:
        return self.used_margin is not None

    def has_margin_components(self) -> bool:
        return any(
            value is not None
            for value in (
                self.margin_balance,
                self.free_margin,
                self.used_margin,
            )
        )

    # ------------------------------------------------------------------
    # Balance movements
    # ------------------------------------------------------------------

    def has_opening_balance(self) -> bool:
        return self.opening_balance is not None

    def has_closing_balance(self) -> bool:
        return self.closing_balance is not None

    def has_deposit(self) -> bool:
        return self.deposit_amount is not None

    def has_withdrawal(self) -> bool:
        return self.withdrawal_amount is not None

    def has_transfer(self) -> bool:
        return self.transfer_amount is not None

    def has_balance_movements(self) -> bool:
        return any(
            value is not None
            for value in (
                self.deposit_amount,
                self.withdrawal_amount,
                self.transfer_amount,
                self.fees,
                self.funding,
            )
        )

    # ------------------------------------------------------------------
    # P&L
    # ------------------------------------------------------------------

    def has_realized_pnl(self) -> bool:
        return self.realized_pnl is not None

    def has_unrealized_pnl(self) -> bool:
        return self.unrealized_pnl is not None

    def has_net_change(self) -> bool:
        return self.net_change is not None

    # ------------------------------------------------------------------
    # Calculations
    # ------------------------------------------------------------------

    def calculate_net_change(self) -> Optional[float]:
        """
        Calculate structural net balance change from available components.

        Positive deposits/transfers increase balance.
        Withdrawals and fees reduce balance.
        Funding is treated as an explicitly signed component.
        P&L is included only when supplied.
        """

        components = (
            self.deposit_amount,
            -self.withdrawal_amount
            if self.withdrawal_amount is not None
            else None,
            self.transfer_amount,
            -self.fees if self.fees is not None else None,
            self.funding,
            self.realized_pnl,
        )

        available = [value for value in components if value is not None]

        if not available:
            if (
                self.opening_balance is not None
                and self.closing_balance is not None
            ):
                return float(self.closing_balance) - float(
                    self.opening_balance
                )

            return None

        return float(sum(available))

    def calculate_available_from_components(self) -> Optional[float]:
        """
        Calculate available balance from cash less locked/reserved amounts.

        This is structural only and does not represent broker-specific
        accounting rules.
        """

        if self.cash_balance is None:
            return None

        locked = float(self.locked_balance or 0.0)
        reserved = float(self.reserved_balance or 0.0)

        return float(self.cash_balance) - locked - reserved

    def calculate_locked_from_components(self) -> Optional[float]:
        """
        Calculate combined locked/reserved balance.
        """

        if self.locked_balance is None and self.reserved_balance is None:
            return None

        return float(self.locked_balance or 0.0) + float(
            self.reserved_balance or 0.0
        )

    def calculate_margin_free_from_components(self) -> Optional[float]:
        """
        Calculate free margin from margin balance less used margin.
        """

        if self.margin_balance is None:
            return None

        return float(self.margin_balance) - float(
            self.used_margin or 0.0
        )

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

        if not self.balance_id:
            issues.append("MISSING_BALANCE_ID")

        if not self.account_id:
            issues.append("MISSING_ACCOUNT_ID")

        if not self.timestamp:
            issues.append("MISSING_TIMESTAMP")

        if not self.currency and not self.base_currency:
            issues.append("MISSING_CURRENCY")

        if (
            self.available_balance is not None
            and self.cash_balance is not None
        ):
            if self.available_balance > self.cash_balance:
                issues.append("AVAILABLE_BALANCE_EXCEEDS_CASH")

        if (
            self.free_margin is not None
            and self.margin_balance is not None
        ):
            if self.free_margin > self.margin_balance:
                issues.append("FREE_MARGIN_EXCEEDS_MARGIN_BALANCE")

        if self.used_margin is not None and self.used_margin < 0:
            issues.append("NEGATIVE_USED_MARGIN")

        if (
            self.cash_balance is not None
            and self.locked_balance is not None
        ):
            if self.locked_balance > self.cash_balance:
                issues.append("LOCKED_BALANCE_EXCEEDS_CASH")

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
            "schema": MARKET_ACCOUNT_BALANCE_SCHEMA,
            "version": MARKET_ACCOUNT_BALANCE_SCHEMA_VERSION,
            "immutable": True,
            "balance_focused": True,
            "equity_logic": False,
            "decision_logic": False,
            "execution_authorization": False,
            "v7_dependency": False,
        }


# ----------------------------------------------------------------------
# Health
# ----------------------------------------------------------------------

def market_account_balance_health() -> dict[str, Any]:
    return {
        "schema": MARKET_ACCOUNT_BALANCE_SCHEMA,
        "version": MARKET_ACCOUNT_BALANCE_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "balance_focused": True,
        "separates_balance_from_equity": True,
        "separates_balance_from_margin": True,
        "observed_derived_separation": True,
        "provenance_supported": True,
        "decision_logic": False,
        "execution_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_ACCOUNT_BALANCE_SCHEMA_VERSION",
    "MARKET_ACCOUNT_BALANCE_SCHEMA",
    "MarketAccountBalance",
    "market_account_balance_health",
]