"""
ROBOMLM PLUS
V6 Market Account Schema

Purpose:
    Structural representation of account-level market and trading
    state required by the V6 intelligence boundary.

Rules:
    - Account representation only.
    - No trading decision.
    - No order generation.
    - No execution authorization.
    - No broker/API interaction.
    - No fund transfer.
    - No prediction.
    - No V7+ dependency.
    - Balance, equity, margin, exposure, and P&L remain distinct.
    - Observed and derived information remain distinguishable.
    - Does not mutate source data.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from math import isfinite
from numbers import Real
from typing import Any, Mapping, Optional


MARKET_ACCOUNT_SCHEMA_VERSION = "1.0.0"
MARKET_ACCOUNT_SCHEMA = "V6_MARKET_ACCOUNT"


@dataclass(frozen=True)
class MarketAccount:
    """
    Immutable structural representation of account state.

    This schema describes account measurements and references. It does not
    manage an account, place orders, transfer funds, or authorize execution.
    """

    # ------------------------------------------------------------------
    # Account Identity
    # ------------------------------------------------------------------

    account_id: Optional[str] = None
    timestamp: Optional[str] = None
    sequence: Optional[int] = None

    # ------------------------------------------------------------------
    # Account / Environment Identity
    # ------------------------------------------------------------------

    account_type: Optional[str] = None
    broker: Optional[str] = None
    provider: Optional[str] = None
    venue: Optional[str] = None
    base_currency: Optional[str] = None
    environment: Optional[str] = None
    mode: Optional[str] = None

    # ------------------------------------------------------------------
    # Account Financial State
    # ------------------------------------------------------------------

    balance: Optional[float] = None
    equity: Optional[float] = None
    available_balance: Optional[float] = None
    available_margin: Optional[float] = None
    used_margin: Optional[float] = None
    maintenance_margin: Optional[float] = None
    margin_ratio: Optional[float] = None

    # ------------------------------------------------------------------
    # P&L State
    # ------------------------------------------------------------------

    realized_pnl: Optional[float] = None
    unrealized_pnl: Optional[float] = None
    total_pnl: Optional[float] = None
    daily_pnl: Optional[float] = None

    # ------------------------------------------------------------------
    # Exposure State
    # ------------------------------------------------------------------

    gross_exposure: Optional[float] = None
    net_exposure: Optional[float] = None
    position_count: Optional[int] = None
    open_order_count: Optional[int] = None

    # ------------------------------------------------------------------
    # Risk / Limits State
    # ------------------------------------------------------------------

    max_position_value: Optional[float] = None
    max_order_value: Optional[float] = None
    risk_limit: Optional[float] = None
    exposure_limit: Optional[float] = None
    drawdown_value: Optional[float] = None
    drawdown_percent: Optional[float] = None

    # ------------------------------------------------------------------
    # Lifecycle / Session State
    # ------------------------------------------------------------------

    session_id: Optional[str] = None
    request_id: Optional[str] = None
    opened_at: Optional[str] = None
    updated_at: Optional[str] = None

    # ------------------------------------------------------------------
    # Related References
    # ------------------------------------------------------------------

    position_id: Optional[str] = None
    order_id: Optional[str] = None
    execution_id: Optional[str] = None
    transaction_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Source References
    # ------------------------------------------------------------------

    observation_id: Optional[str] = None
    context_id: Optional[str] = None
    regime_id: Optional[str] = None
    execution_ref: Optional[str] = None

    # ------------------------------------------------------------------
    # Provenance
    # ------------------------------------------------------------------

    source: Optional[str] = None
    source_type: Optional[str] = None

    # ------------------------------------------------------------------
    # Observed / Derived Separation
    # ------------------------------------------------------------------

    observed_fields: tuple[str, ...] = field(default_factory=tuple)
    derived_fields: tuple[str, ...] = field(default_factory=tuple)

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate structural account information."""

        # --------------------------------------------------------------
        # Sequence
        # --------------------------------------------------------------

        if self.sequence is not None:
            if isinstance(self.sequence, bool):
                raise TypeError(
                    "MarketAccount.sequence must be an integer or None."
                )

            if not isinstance(self.sequence, int):
                raise TypeError(
                    "MarketAccount.sequence must be an integer or None."
                )

            if self.sequence < 0:
                raise ValueError(
                    "MarketAccount.sequence cannot be negative."
                )

        # --------------------------------------------------------------
        # Integer Fields
        # --------------------------------------------------------------

        integer_fields = {
            "position_count": self.position_count,
            "open_order_count": self.open_order_count,
        }

        for field_name, value in integer_fields.items():
            if value is None:
                continue

            if isinstance(value, bool):
                raise TypeError(
                    f"MarketAccount.{field_name} must be an integer or None."
                )

            if not isinstance(value, int):
                raise TypeError(
                    f"MarketAccount.{field_name} must be an integer or None."
                )

            if value < 0:
                raise ValueError(
                    f"MarketAccount.{field_name} cannot be negative."
                )

        # --------------------------------------------------------------
        # Numeric Fields
        #
        # P&L and net exposure remain signed.
        # All numeric fields must be genuine finite numeric values.
        # --------------------------------------------------------------

        numeric_fields = {
            "balance": self.balance,
            "equity": self.equity,
            "available_balance": self.available_balance,
            "available_margin": self.available_margin,
            "used_margin": self.used_margin,
            "maintenance_margin": self.maintenance_margin,
            "margin_ratio": self.margin_ratio,
            "realized_pnl": self.realized_pnl,
            "unrealized_pnl": self.unrealized_pnl,
            "total_pnl": self.total_pnl,
            "daily_pnl": self.daily_pnl,
            "gross_exposure": self.gross_exposure,
            "net_exposure": self.net_exposure,
            "max_position_value": self.max_position_value,
            "max_order_value": self.max_order_value,
            "risk_limit": self.risk_limit,
            "exposure_limit": self.exposure_limit,
            "drawdown_value": self.drawdown_value,
            "drawdown_percent": self.drawdown_percent,
        }

        for field_name, value in numeric_fields.items():
            if value is None:
                continue

            if isinstance(value, bool):
                raise TypeError(
                    f"MarketAccount.{field_name} must be numeric or None."
                )

            if not isinstance(value, Real):
                raise TypeError(
                    f"MarketAccount.{field_name} must be numeric or None."
                )

            if not isfinite(float(value)):
                raise ValueError(
                    f"MarketAccount.{field_name} "
                    "must be finite when provided."
                )

        # --------------------------------------------------------------
        # Non-negative Financial / Risk Fields
        # --------------------------------------------------------------

        non_negative_fields = (
            "balance",
            "equity",
            "available_balance",
            "available_margin",
            "used_margin",
            "maintenance_margin",
            "margin_ratio",
            "gross_exposure",
            "max_position_value",
            "max_order_value",
            "risk_limit",
            "exposure_limit",
            "drawdown_value",
        )

        for field_name in non_negative_fields:
            value = getattr(self, field_name)

            if value is not None and value < 0:
                raise ValueError(
                    f"MarketAccount.{field_name} cannot be negative."
                )

        # --------------------------------------------------------------
        # Metadata
        # --------------------------------------------------------------

        if self.metadata is None:
            raise TypeError(
                "MarketAccount.metadata must be a mapping."
            )

        if not isinstance(self.metadata, Mapping):
            raise TypeError(
                "MarketAccount.metadata must be a mapping."
            )

        # --------------------------------------------------------------
        # Observed / Derived Field Containers
        # --------------------------------------------------------------

        if isinstance(self.observed_fields, str):
            raise TypeError(
                "MarketAccount.observed_fields must be a sequence of names."
            )

        if isinstance(self.derived_fields, str):
            raise TypeError(
                "MarketAccount.derived_fields must be a sequence of names."
            )

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    def has_identity(self) -> bool:
        """Return True when account identity exists."""

        return bool(self.account_id)

    def has_environment_identity(self) -> bool:
        """Return True when account environment is identifiable."""

        return bool(
            self.broker
            or self.provider
            or self.venue
            or self.environment
            or self.mode
        )

    # ------------------------------------------------------------------
    # Financial State
    # ------------------------------------------------------------------

    def has_balance(self) -> bool:
        """Return True when account balance exists."""

        return self.balance is not None

    def has_equity(self) -> bool:
        """Return True when account equity exists."""

        return self.equity is not None

    def has_margin_state(self) -> bool:
        """Return True when margin information exists."""

        return any(
            value is not None
            for value in (
                self.available_margin,
                self.used_margin,
                self.maintenance_margin,
                self.margin_ratio,
            )
        )

    # ------------------------------------------------------------------
    # P&L
    # ------------------------------------------------------------------

    def calculate_total_pnl(self) -> Optional[float]:
        """Calculate total P&L from realized and unrealized P&L."""

        if (
            self.realized_pnl is None
            or self.unrealized_pnl is None
        ):
            return None

        return self.realized_pnl + self.unrealized_pnl

    # ------------------------------------------------------------------
    # Margin
    # ------------------------------------------------------------------

    def calculate_margin_ratio(self) -> Optional[float]:
        """
        Calculate equity / used margin as a ratio.

        Returns None when required measurements are unavailable or used
        margin is zero.
        """

        if self.equity is None or self.used_margin is None:
            return None

        if self.used_margin == 0:
            return None

        return self.equity / self.used_margin

    # ------------------------------------------------------------------
    # Exposure
    # ------------------------------------------------------------------

    def has_exposure(self) -> bool:
        """Return True when exposure information exists."""

        return any(
            value is not None
            for value in (
                self.gross_exposure,
                self.net_exposure,
            )
        )

    def has_position_state(self) -> bool:
        """Return True when position count is available."""

        return self.position_count is not None

    def has_order_state(self) -> bool:
        """Return True when open-order count is available."""

        return self.open_order_count is not None

    # ------------------------------------------------------------------
    # Risk Measurements
    # ------------------------------------------------------------------

    def calculate_drawdown_percent(
        self,
        reference_equity: Optional[float] = None,
    ) -> Optional[float]:
        """
        Calculate drawdown percentage against a supplied reference equity.

        No risk decision is produced.
        """

        if reference_equity is None:
            return None

        if reference_equity <= 0:
            return None

        if self.equity is None:
            return None

        drawdown = reference_equity - self.equity

        return (drawdown / reference_equity) * 100.0

    # ------------------------------------------------------------------
    # Related References
    # ------------------------------------------------------------------

    def has_position_reference(self) -> bool:
        """Return True when a position reference exists."""

        return bool(self.position_id)

    def has_order_reference(self) -> bool:
        """Return True when an order reference exists."""

        return bool(self.order_id)

    def has_execution_reference(self) -> bool:
        """Return True when an execution reference exists."""

        return bool(
            self.execution_id
            or self.execution_ref
        )

    def has_transaction_reference(self) -> bool:
        """Return True when a transaction reference exists."""

        return bool(self.transaction_id)

    # ------------------------------------------------------------------
    # Source References
    # ------------------------------------------------------------------

    def has_source_reference(self) -> bool:
        """Return True when an upstream source reference exists."""

        return bool(
            self.observation_id
            or self.context_id
            or self.regime_id
            or self.execution_ref
        )

    # ------------------------------------------------------------------
    # Provenance
    # ------------------------------------------------------------------

    def observed_field_names(self) -> tuple[str, ...]:
        """Return explicitly observed field names."""

        return tuple(self.observed_fields)

    def derived_field_names(self) -> tuple[str, ...]:
        """Return explicitly derived field names."""

        return tuple(self.derived_fields)

    # ------------------------------------------------------------------
    # Structural Validation
    # ------------------------------------------------------------------

    def issue_flags(self) -> tuple[str, ...]:
        """
        Return structural account issues.

        Validation only. No trading decision is produced.
        """

        issues: list[str] = []

        if not self.has_identity():
            issues.append("MISSING_ACCOUNT_IDENTITY")

        if not self.timestamp:
            issues.append("MISSING_TIMESTAMP")

        if not self.source:
            issues.append("MISSING_SOURCE")

        if (
            self.available_balance is not None
            and self.balance is not None
            and self.available_balance > self.balance
        ):
            issues.append(
                "AVAILABLE_BALANCE_EXCEEDS_BALANCE"
            )

        if (
            self.used_margin is not None
            and self.equity is not None
            and self.used_margin > self.equity
        ):
            issues.append(
                "USED_MARGIN_EXCEEDS_EQUITY"
            )

        if (
            self.position_count is not None
            and self.position_count == 0
            and self.gross_exposure is not None
            and self.gross_exposure > 0
        ):
            issues.append(
                "EXPOSURE_WITH_ZERO_POSITION_COUNT"
            )

        if (
            self.derived_fields
            and not self.has_source_reference()
        ):
            issues.append(
                "DERIVED_ACCOUNT_DATA_WITHOUT_SOURCE_REFERENCE"
            )

        return tuple(issues)

    def is_structurally_valid(self) -> bool:
        """Return True when no structural issues exist."""

        return not self.issue_flags()

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize account information into a mapping."""

        data = asdict(self)

        data["observed_fields"] = list(self.observed_fields)
        data["derived_fields"] = list(self.derived_fields)
        data["metadata"] = dict(self.metadata)

        return data

    @staticmethod
    def schema_info() -> dict[str, str]:
        """Return schema identity and version."""

        return {
            "schema": MARKET_ACCOUNT_SCHEMA,
            "version": MARKET_ACCOUNT_SCHEMA_VERSION,
        }


def market_account_health() -> dict[str, Any]:
    """Return structural health information for the account schema."""

    return {
        "schema": MARKET_ACCOUNT_SCHEMA,
        "version": MARKET_ACCOUNT_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "account_identity_supported": True,
        "environment_identity_supported": True,
        "balance_supported": True,
        "equity_supported": True,
        "available_balance_supported": True,
        "margin_state_supported": True,
        "pnl_supported": True,
        "exposure_supported": True,
        "position_state_supported": True,
        "order_state_supported": True,
        "risk_measurements_supported": True,
        "position_reference_supported": True,
        "order_reference_supported": True,
        "execution_reference_supported": True,
        "transaction_reference_supported": True,
        "source_reference_supported": True,
        "provenance_supported": True,
        "observed_derived_separation": True,
        "balance_equity_separation": True,
        "margin_measurement_only": True,
        "decision_logic": False,
        "order_generation": False,
        "execution_authorization": False,
        "broker_interaction": False,
        "fund_transfer": False,
        "prediction_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_ACCOUNT_SCHEMA_VERSION",
    "MARKET_ACCOUNT_SCHEMA",
    "MarketAccount",
    "market_account_health",
]