"""
ROBOMLM PLUS
V6 Market Margin Schema

Purpose:
    Structural representation of margin state and margin components.

Design rules:
    - Immutable schema.
    - Currency agnostic: INR, USD, USDT, etc.
    - Margin is distinct from account balance and equity.
    - Margin describes financing/collateral usage only.
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


MARKET_MARGIN_SCHEMA_VERSION = "1.0.0"
MARKET_MARGIN_SCHEMA = "V6_MARKET_MARGIN"


@dataclass(frozen=True)
class MarketMargin:
    """
    Immutable structural representation of margin state.

    Supports:
        - Initial margin
        - Maintenance margin
        - Used margin
        - Free margin
        - Margin balance
        - Margin ratio
        - Margin utilization
        - Margin requirement
    """

    # ------------------------------------------------------------------
    # Margin identity
    # ------------------------------------------------------------------
    margin_id: Optional[str] = None
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
    # Margin type / state
    # ------------------------------------------------------------------
    margin_type: Optional[str] = None
    margin_mode: Optional[str] = None
    margin_state: Optional[str] = None

    # ------------------------------------------------------------------
    # Margin components
    # ------------------------------------------------------------------
    margin_balance: Optional[float] = None
    initial_margin: Optional[float] = None
    maintenance_margin: Optional[float] = None
    margin_requirement: Optional[float] = None
    used_margin: Optional[float] = None
    free_margin: Optional[float] = None

    # ------------------------------------------------------------------
    # Margin metrics
    # ------------------------------------------------------------------
    margin_ratio: Optional[float] = None
    margin_utilization: Optional[float] = None

    # ------------------------------------------------------------------
    # Supporting account values
    # ------------------------------------------------------------------
    account_equity: Optional[float] = None
    available_balance: Optional[float] = None

    # ------------------------------------------------------------------
    # Exposure context
    # ------------------------------------------------------------------
    gross_exposure: Optional[float] = None
    net_exposure: Optional[float] = None

    # ------------------------------------------------------------------
    # Related references
    # ------------------------------------------------------------------
    position_id: Optional[str] = None
    order_id: Optional[str] = None
    execution_id: Optional[str] = None
    transaction_id: Optional[str] = None

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
            "margin_balance",
            "initial_margin",
            "maintenance_margin",
            "margin_requirement",
            "used_margin",
            "free_margin",
            "margin_ratio",
            "margin_utilization",
            "account_equity",
            "available_balance",
            "gross_exposure",
            "net_exposure",
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

                if field_name not in {
                    "margin_ratio",
                    "margin_utilization",
                    "net_exposure",
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
        return bool(self.margin_id)

    def has_margin_identity(self) -> bool:
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
    # Margin components
    # ------------------------------------------------------------------

    def has_margin_balance(self) -> bool:
        return self.margin_balance is not None

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

    def has_margin_components(self) -> bool:
        return any(
            value is not None
            for value in (
                self.margin_balance,
                self.initial_margin,
                self.maintenance_margin,
                self.margin_requirement,
                self.used_margin,
                self.free_margin,
            )
        )

    # ------------------------------------------------------------------
    # Margin metrics
    # ------------------------------------------------------------------

    def has_margin_ratio(self) -> bool:
        return self.margin_ratio is not None

    def has_margin_utilization(self) -> bool:
        return self.margin_utilization is not None

    # ------------------------------------------------------------------
    # Structural calculations
    # ------------------------------------------------------------------

    def calculate_free_margin(self) -> Optional[float]:
        """
        Calculate free margin from margin balance minus used margin.
        """

        if self.margin_balance is None:
            return None

        return float(self.margin_balance) - float(
            self.used_margin or 0.0
        )

    def calculate_used_margin(self) -> Optional[float]:
        """
        Calculate used margin from margin balance minus free margin.
        """

        if self.margin_balance is None or self.free_margin is None:
            return None

        return float(self.margin_balance) - float(self.free_margin)

    def calculate_margin_ratio(self) -> Optional[float]:
        """
        Calculate margin ratio as:

            equity / used_margin

        when used margin is greater than zero.

        This is a structural metric only. Broker-specific liquidation
        rules are intentionally outside this schema.
        """

        if self.account_equity is None or self.used_margin is None:
            return None

        used = float(self.used_margin)

        if used <= 0:
            return None

        return float(self.account_equity) / used

    def calculate_margin_utilization(self) -> Optional[float]:
        """
        Calculate margin utilization as:

            used_margin / margin_balance

        expressed as a decimal ratio.
        """

        if self.margin_balance is None or self.used_margin is None:
            return None

        balance = float(self.margin_balance)

        if balance <= 0:
            return None

        return float(self.used_margin) / balance

    def calculate_margin_headroom(self) -> Optional[float]:
        """
        Calculate remaining margin headroom.
        """

        if self.margin_balance is None:
            return None

        required = self.margin_requirement

        if required is None:
            required = self.used_margin

        if required is None:
            return None

        return float(self.margin_balance) - float(required)

    # ------------------------------------------------------------------
    # Supporting account state
    # ------------------------------------------------------------------

    def has_account_equity(self) -> bool:
        return self.account_equity is not None

    def has_available_balance(self) -> bool:
        return self.available_balance is not None

    def has_exposure(self) -> bool:
        return (
            self.gross_exposure is not None
            or self.net_exposure is not None
        )

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

        if not self.margin_id:
            issues.append("MISSING_MARGIN_ID")

        if not self.account_id:
            issues.append("MISSING_ACCOUNT_ID")

        if not self.timestamp:
            issues.append("MISSING_TIMESTAMP")

        if not self.currency and not self.base_currency:
            issues.append("MISSING_CURRENCY")

        if (
            self.maintenance_margin is not None
            and self.initial_margin is not None
            and self.maintenance_margin > self.initial_margin
        ):
            issues.append("MAINTENANCE_MARGIN_EXCEEDS_INITIAL_MARGIN")

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
            self.margin_utilization is not None
            and self.margin_utilization < 0
        ):
            issues.append("NEGATIVE_MARGIN_UTILIZATION")

        if (
            self.margin_ratio is not None
            and self.margin_ratio < 0
        ):
            issues.append("NEGATIVE_MARGIN_RATIO")

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
            "schema": MARKET_MARGIN_SCHEMA,
            "version": MARKET_MARGIN_SCHEMA_VERSION,
            "immutable": True,
            "currency_agnostic": True,
            "supports_inr": True,
            "supports_usd": True,
            "supports_usdt": True,
            "balance_separated": True,
            "equity_separated": True,
            "risk_decision_logic": False,
            "execution_authorization": False,
            "v7_dependency": False,
        }


# ----------------------------------------------------------------------
# Health
# ----------------------------------------------------------------------

def market_margin_health() -> dict[str, Any]:
    return {
        "schema": MARKET_MARGIN_SCHEMA,
        "version": MARKET_MARGIN_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "currency_agnostic": True,
        "supports_inr": True,
        "supports_usd": True,
        "supports_usdt": True,
        "initial_margin_supported": True,
        "maintenance_margin_supported": True,
        "free_margin_supported": True,
        "used_margin_supported": True,
        "margin_ratio_supported": True,
        "margin_utilization_supported": True,
        "balance_equity_separation": True,
        "observed_derived_separation": True,
        "provenance_supported": True,
        "decision_logic": False,
        "execution_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_MARGIN_SCHEMA_VERSION",
    "MARKET_MARGIN_SCHEMA",
    "MarketMargin",
    "market_margin_health",
]