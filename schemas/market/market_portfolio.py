"""
ROBOMLM PLUS
V6 Market Portfolio Schema

Purpose:
    Structural representation of portfolio-level market state,
    positions, exposure, valuation, and portfolio measurements.

Rules:
    - Portfolio representation only.
    - No trading decision.
    - No order generation.
    - No execution authorization.
    - No broker/API interaction.
    - No fund transfer.
    - No prediction.
    - No V7+ dependency.
    - Portfolio state remains distinct from account, position, order,
      transaction, and execution state.
    - Observed and derived information remain distinguishable.
    - Does not mutate source data.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Optional


MARKET_PORTFOLIO_SCHEMA_VERSION = "1.0.0"
MARKET_PORTFOLIO_SCHEMA = "V6_MARKET_PORTFOLIO"


@dataclass(frozen=True)
class MarketPortfolio:
    """
    Immutable structural representation of portfolio information.

    A portfolio describes aggregate holdings and exposure across one or
    more instruments. It does not create, modify, or close positions.
    """

    # ------------------------------------------------------------------
    # Portfolio Identity
    # ------------------------------------------------------------------

    portfolio_id: Optional[str] = None
    timestamp: Optional[str] = None
    sequence: Optional[int] = None

    # ------------------------------------------------------------------
    # Portfolio Environment
    # ------------------------------------------------------------------

    account_id: Optional[str] = None
    portfolio_type: Optional[str] = None
    base_currency: Optional[str] = None
    environment: Optional[str] = None
    mode: Optional[str] = None

    # ------------------------------------------------------------------
    # Portfolio Valuation
    # ------------------------------------------------------------------

    starting_value: Optional[float] = None
    current_value: Optional[float] = None
    market_value: Optional[float] = None
    cash_value: Optional[float] = None

    # ------------------------------------------------------------------
    # P&L
    # ------------------------------------------------------------------

    realized_pnl: Optional[float] = None
    unrealized_pnl: Optional[float] = None
    total_pnl: Optional[float] = None
    daily_pnl: Optional[float] = None
    pnl_percent: Optional[float] = None

    # ------------------------------------------------------------------
    # Exposure
    # ------------------------------------------------------------------

    gross_exposure: Optional[float] = None
    net_exposure: Optional[float] = None
    long_exposure: Optional[float] = None
    short_exposure: Optional[float] = None

    # ------------------------------------------------------------------
    # Position / Order Counts
    # ------------------------------------------------------------------

    position_count: Optional[int] = None
    long_position_count: Optional[int] = None
    short_position_count: Optional[int] = None
    open_order_count: Optional[int] = None

    # ------------------------------------------------------------------
    # Portfolio Risk Measurements
    # ------------------------------------------------------------------

    risk_value: Optional[float] = None
    exposure_limit: Optional[float] = None
    risk_limit: Optional[float] = None
    drawdown_value: Optional[float] = None
    drawdown_percent: Optional[float] = None

    # ------------------------------------------------------------------
    # Concentration Measurements
    # ------------------------------------------------------------------

    largest_position_value: Optional[float] = None
    largest_position_percent: Optional[float] = None
    concentration_ratio: Optional[float] = None

    # ------------------------------------------------------------------
    # Lifecycle / Session
    # ------------------------------------------------------------------

    opened_at: Optional[str] = None
    updated_at: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None

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

    account_ref: Optional[str] = None
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
        """Validate structural portfolio information."""

        if self.sequence is not None:
            if isinstance(self.sequence, bool):
                raise TypeError(
                    "MarketPortfolio.sequence must be an integer or None."
                )

            if not isinstance(self.sequence, int):
                raise TypeError(
                    "MarketPortfolio.sequence must be an integer or None."
                )

            if self.sequence < 0:
                raise ValueError(
                    "MarketPortfolio.sequence cannot be negative."
                )

        integer_fields = {
            "position_count": self.position_count,
            "long_position_count": self.long_position_count,
            "short_position_count": self.short_position_count,
            "open_order_count": self.open_order_count,
        }

        for field_name, value in integer_fields.items():
            if value is None:
                continue

            if isinstance(value, bool):
                raise TypeError(
                    f"MarketPortfolio.{field_name} "
                    "must be an integer or None."
                )

            if not isinstance(value, int):
                raise TypeError(
                    f"MarketPortfolio.{field_name} "
                    "must be an integer or None."
                )

            if value < 0:
                raise ValueError(
                    f"MarketPortfolio.{field_name} cannot be negative."
                )

        numeric_fields = {
            "starting_value": self.starting_value,
            "current_value": self.current_value,
            "market_value": self.market_value,
            "cash_value": self.cash_value,
            "realized_pnl": self.realized_pnl,
            "unrealized_pnl": self.unrealized_pnl,
            "total_pnl": self.total_pnl,
            "daily_pnl": self.daily_pnl,
            "pnl_percent": self.pnl_percent,
            "gross_exposure": self.gross_exposure,
            "net_exposure": self.net_exposure,
            "long_exposure": self.long_exposure,
            "short_exposure": self.short_exposure,
            "risk_value": self.risk_value,
            "exposure_limit": self.exposure_limit,
            "risk_limit": self.risk_limit,
            "drawdown_value": self.drawdown_value,
            "drawdown_percent": self.drawdown_percent,
            "largest_position_value": self.largest_position_value,
            "largest_position_percent": self.largest_position_percent,
            "concentration_ratio": self.concentration_ratio,
        }

        for field_name, value in numeric_fields.items():
            if value is None:
                continue

            if isinstance(value, bool):
                raise TypeError(
                    f"MarketPortfolio.{field_name} "
                    "must be numeric or None."
                )

            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"MarketPortfolio.{field_name} "
                    "must be numeric or None."
                )

        non_negative_fields = (
            "starting_value",
            "current_value",
            "market_value",
            "cash_value",
            "gross_exposure",
            "long_exposure",
            "short_exposure",
            "risk_value",
            "exposure_limit",
            "risk_limit",
            "drawdown_value",
            "largest_position_value",
            "largest_position_percent",
            "concentration_ratio",
        )

        for field_name in non_negative_fields:
            value = getattr(self, field_name)

            if value is not None and value < 0:
                raise ValueError(
                    f"MarketPortfolio.{field_name} cannot be negative."
                )

        if self.metadata is None:
            raise TypeError(
                "MarketPortfolio.metadata must be a mapping."
            )

        if not isinstance(self.metadata, Mapping):
            raise TypeError(
                "MarketPortfolio.metadata must be a mapping."
            )

        if isinstance(self.observed_fields, str):
            raise TypeError(
                "MarketPortfolio.observed_fields "
                "must be a sequence of names."
            )

        if isinstance(self.derived_fields, str):
            raise TypeError(
                "MarketPortfolio.derived_fields "
                "must be a sequence of names."
            )

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    def has_identity(self) -> bool:
        """Return True when portfolio identity exists."""

        return bool(self.portfolio_id)

    def has_account_reference(self) -> bool:
        """Return True when an account reference exists."""

        return bool(
            self.account_id
            or self.account_ref
        )

    # ------------------------------------------------------------------
    # Valuation
    # ------------------------------------------------------------------

    def has_valuation(self) -> bool:
        """Return True when portfolio valuation exists."""

        return any(
            value is not None
            for value in (
                self.current_value,
                self.market_value,
                self.cash_value,
            )
        )

    def calculate_current_value(self) -> Optional[float]:
        """
        Calculate portfolio current value from market value and cash.

        This is a structural valuation calculation only.
        """

        if self.market_value is None or self.cash_value is None:
            return None

        return self.market_value + self.cash_value

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

    def calculate_pnl_percent(self) -> Optional[float]:
        """
        Calculate P&L percentage against starting portfolio value.
        """

        total_pnl = self.total_pnl

        if total_pnl is None:
            total_pnl = self.calculate_total_pnl()

        if total_pnl is None or self.starting_value is None:
            return None

        if self.starting_value == 0:
            return None

        return (
            total_pnl / self.starting_value
        ) * 100.0

    # ------------------------------------------------------------------
    # Exposure
    # ------------------------------------------------------------------

    def has_exposure(self) -> bool:
        """Return True when portfolio exposure exists."""

        return any(
            value is not None
            for value in (
                self.gross_exposure,
                self.net_exposure,
                self.long_exposure,
                self.short_exposure,
            )
        )

    def calculate_net_exposure(self) -> Optional[float]:
        """
        Calculate net exposure from long and short exposure.
        """

        if (
            self.long_exposure is None
            or self.short_exposure is None
        ):
            return None

        return self.long_exposure - self.short_exposure

    def calculate_gross_exposure(self) -> Optional[float]:
        """
        Calculate gross exposure from long and short exposure.
        """

        if (
            self.long_exposure is None
            or self.short_exposure is None
        ):
            return None

        return self.long_exposure + self.short_exposure

    # ------------------------------------------------------------------
    # Position State
    # ------------------------------------------------------------------

    def has_position_state(self) -> bool:
        """Return True when position count exists."""

        return self.position_count is not None

    def has_order_state(self) -> bool:
        """Return True when open-order count exists."""

        return self.open_order_count is not None

    # ------------------------------------------------------------------
    # Concentration
    # ------------------------------------------------------------------

    def calculate_largest_position_percent(self) -> Optional[float]:
        """
        Calculate largest-position percentage against current portfolio
        value.
        """

        if (
            self.largest_position_value is None
            or self.current_value is None
        ):
            return None

        if self.current_value == 0:
            return None

        return (
            self.largest_position_value
            / self.current_value
        ) * 100.0

    def calculate_concentration_ratio(self) -> Optional[float]:
        """
        Calculate largest position / total portfolio value.

        Returned as a ratio from 0.0 to 1.0 when valid.
        """

        percentage = self.calculate_largest_position_percent()

        if percentage is None:
            return None

        return percentage / 100.0

    # ------------------------------------------------------------------
    # Drawdown
    # ------------------------------------------------------------------

    def calculate_drawdown_percent(
        self,
        reference_value: Optional[float] = None,
    ) -> Optional[float]:
        """
        Calculate drawdown against a supplied reference portfolio value.
        """

        if reference_value is None:
            return None

        if reference_value <= 0:
            return None

        if self.current_value is None:
            return None

        drawdown = reference_value - self.current_value

        return (
            drawdown / reference_value
        ) * 100.0

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
            self.account_ref
            or self.observation_id
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
        Return structural portfolio issues.

        Validation only. No trading decision is produced.
        """

        issues: list[str] = []

        if not self.has_identity():
            issues.append("MISSING_PORTFOLIO_IDENTITY")

        if not self.timestamp:
            issues.append("MISSING_TIMESTAMP")

        if not self.source:
            issues.append("MISSING_SOURCE")

        if (
            self.position_count is not None
            and self.long_position_count is not None
            and self.short_position_count is not None
            and (
                self.long_position_count
                + self.short_position_count
                > self.position_count
            )
        ):
            issues.append(
                "POSITION_COUNT_BREAKDOWN_EXCEEDS_TOTAL"
            )

        if (
            self.current_value is not None
            and self.market_value is not None
            and self.cash_value is not None
            and (
                abs(
                    self.current_value
                    - (
                        self.market_value
                        + self.cash_value
                    )
                )
                > 1e-9
            )
        ):
            issues.append(
                "PORTFOLIO_VALUE_RECONCILIATION_MISMATCH"
            )

        if (
            self.derived_fields
            and not self.has_source_reference()
        ):
            issues.append(
                "DERIVED_PORTFOLIO_DATA_WITHOUT_SOURCE_REFERENCE"
            )

        return tuple(issues)

    def is_structurally_valid(self) -> bool:
        """Return True when no structural issues exist."""

        return not self.issue_flags()

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize portfolio information into a mapping."""

        data = asdict(self)

        data["observed_fields"] = list(self.observed_fields)
        data["derived_fields"] = list(self.derived_fields)
        data["metadata"] = dict(self.metadata)

        return data

    @staticmethod
    def schema_info() -> dict[str, str]:
        """Return schema identity and version."""

        return {
            "schema": MARKET_PORTFOLIO_SCHEMA,
            "version": MARKET_PORTFOLIO_SCHEMA_VERSION,
        }


def market_portfolio_health() -> dict[str, Any]:
    """Return structural health information for the portfolio schema."""

    return {
        "schema": MARKET_PORTFOLIO_SCHEMA,
        "version": MARKET_PORTFOLIO_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "portfolio_identity_supported": True,
        "account_reference_supported": True,
        "valuation_supported": True,
        "cash_value_supported": True,
        "pnl_supported": True,
        "exposure_supported": True,
        "position_state_supported": True,
        "order_state_supported": True,
        "risk_measurements_supported": True,
        "concentration_supported": True,
        "drawdown_measurements_supported": True,
        "position_reference_supported": True,
        "order_reference_supported": True,
        "execution_reference_supported": True,
        "transaction_reference_supported": True,
        "source_reference_supported": True,
        "provenance_supported": True,
        "observed_derived_separation": True,
        "portfolio_account_separation": True,
        "portfolio_position_separation": True,
        "portfolio_order_separation": True,
        "decision_logic": False,
        "order_generation": False,
        "execution_authorization": False,
        "broker_interaction": False,
        "fund_transfer": False,
        "prediction_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_PORTFOLIO_SCHEMA_VERSION",
    "MARKET_PORTFOLIO_SCHEMA",
    "MarketPortfolio",
    "market_portfolio_health",
]