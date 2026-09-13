"""
ROBOMLM PLUS
V6 Market Position Schema

Purpose:
    Structural representation of a market position and its observable
    position state.

Rules:
    - Position representation only.
    - No trading decision.
    - No order generation.
    - No execution authorization.
    - No broker/API interaction.
    - No prediction.
    - No V7+ dependency.
    - Position state remains distinct from order and execution state.
    - Observed and derived information remain distinguishable.
    - Does not mutate source data.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from math import isfinite
from typing import Any, Mapping, Optional


MARKET_POSITION_SCHEMA_VERSION = "1.0.0"
MARKET_POSITION_SCHEMA = "V6_MARKET_POSITION"


@dataclass(frozen=True)
class MarketPosition:
    """
    Immutable structural representation of market-position information.

    A position describes current exposure and its measurable state. It does
    not create, modify, close, or authorize a position.
    """

    # ------------------------------------------------------------------
    # Position Identity
    # ------------------------------------------------------------------

    position_id: Optional[str] = None
    timestamp: Optional[str] = None
    sequence: Optional[int] = None

    # ------------------------------------------------------------------
    # Market Identity
    # ------------------------------------------------------------------

    market: Optional[str] = None
    instrument: Optional[str] = None
    symbol: Optional[str] = None
    exchange: Optional[str] = None
    venue: Optional[str] = None
    contract: Optional[str] = None
    expiry: Optional[str] = None

    # ------------------------------------------------------------------
    # Position Classification
    # ------------------------------------------------------------------

    side: Optional[str] = None
    position_status: Optional[str] = None
    position_mode: Optional[str] = None

    # ------------------------------------------------------------------
    # Exposure
    # ------------------------------------------------------------------

    quantity: Optional[float] = None
    average_entry_price: Optional[float] = None
    current_price: Optional[float] = None
    market_value: Optional[float] = None

    # ------------------------------------------------------------------
    # P&L Measurements
    # ------------------------------------------------------------------

    unrealized_pnl: Optional[float] = None
    realized_pnl: Optional[float] = None
    total_pnl: Optional[float] = None
    pnl_percent: Optional[float] = None

    # ------------------------------------------------------------------
    # Risk / Protection State
    # ------------------------------------------------------------------

    stop_price: Optional[float] = None
    target_price: Optional[float] = None
    risk_value: Optional[float] = None
    reward_value: Optional[float] = None

    # ------------------------------------------------------------------
    # Position Lifecycle
    # ------------------------------------------------------------------

    opened_at: Optional[str] = None
    updated_at: Optional[str] = None
    closed_at: Optional[str] = None

    # ------------------------------------------------------------------
    # Related References
    # ------------------------------------------------------------------

    order_id: Optional[str] = None
    execution_id: Optional[str] = None
    transaction_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None

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
        """Validate structural position information."""

        if self.sequence is not None:
            if isinstance(self.sequence, bool):
                raise TypeError(
                    "MarketPosition.sequence must be an integer or None."
                )

            if not isinstance(self.sequence, int):
                raise TypeError(
                    "MarketPosition.sequence must be an integer or None."
                )

            if self.sequence < 0:
                raise ValueError(
                    "MarketPosition.sequence cannot be negative."
                )

        numeric_fields = {
            "quantity": self.quantity,
            "average_entry_price": self.average_entry_price,
            "current_price": self.current_price,
            "market_value": self.market_value,
            "unrealized_pnl": self.unrealized_pnl,
            "realized_pnl": self.realized_pnl,
            "total_pnl": self.total_pnl,
            "pnl_percent": self.pnl_percent,
            "stop_price": self.stop_price,
            "target_price": self.target_price,
            "risk_value": self.risk_value,
            "reward_value": self.reward_value,
        }

        for field_name, value in numeric_fields.items():
            if value is None:
                continue

            if isinstance(value, bool):
                raise TypeError(
                    f"MarketPosition.{field_name} must be numeric or None."
                )

            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"MarketPosition.{field_name} must be numeric or None."
                )

            if not isfinite(float(value)):
                raise ValueError(
                    f"MarketPosition.{field_name} "
                    "must be finite when provided."
                )

        non_negative_fields = (
            "quantity",
            "average_entry_price",
            "current_price",
            "market_value",
            "stop_price",
            "target_price",
            "risk_value",
            "reward_value",
        )

        for field_name in non_negative_fields:
            value = getattr(self, field_name)

            if value is not None and value < 0:
                raise ValueError(
                    f"MarketPosition.{field_name} cannot be negative."
                )

        if self.side is not None:
            normalized_side = self.side.upper()

            if normalized_side not in {
                "LONG",
                "SHORT",
                "BUY",
                "SELL",
                "FLAT",
                "UNKNOWN",
                "NONE",
            }:
                raise ValueError(
                    "MarketPosition.side must be LONG, SHORT, BUY, SELL, "
                    "FLAT, UNKNOWN, or NONE when provided."
                )

        if self.metadata is None:
            raise TypeError(
                "MarketPosition.metadata must be a mapping."
            )

        if not isinstance(self.metadata, Mapping):
            raise TypeError(
                "MarketPosition.metadata must be a mapping."
            )

        if isinstance(self.observed_fields, str):
            raise TypeError(
                "MarketPosition.observed_fields must be a sequence of names."
            )

        if isinstance(self.derived_fields, str):
            raise TypeError(
                "MarketPosition.derived_fields must be a sequence of names."
            )

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    def has_identity(self) -> bool:
        """Return True when position identity exists."""

        return bool(self.position_id)

    def has_market_identity(self) -> bool:
        """Return True when market identity exists."""

        return bool(
            self.market
            or self.instrument
            or self.symbol
        )

    # ------------------------------------------------------------------
    # Position State
    # ------------------------------------------------------------------

    def has_side(self) -> bool:
        """Return True when position side exists."""

        return self.side is not None

    def has_exposure(self) -> bool:
        """Return True when position quantity exists."""

        return self.quantity is not None

    def is_flat(self) -> bool:
        """
        Return True when position represents no exposure.

        Explicit FLAT side is supported, as is zero quantity.
        """

        if self.side is not None and self.side.upper() == "FLAT":
            return True

        return self.quantity == 0

    # ------------------------------------------------------------------
    # Market Value
    # ------------------------------------------------------------------

    def calculate_market_value(self) -> Optional[float]:
        """
        Calculate current market value from quantity and current price.
        """

        if self.quantity is None or self.current_price is None:
            return None

        return self.quantity * self.current_price

    # ------------------------------------------------------------------
    # P&L
    # ------------------------------------------------------------------

    def calculate_unrealized_pnl(self) -> Optional[float]:
        """
        Calculate unrealized P&L from entry and current price.

        LONG / BUY:
            (current - entry) * quantity

        SHORT / SELL:
            (entry - current) * quantity
        """

        if (
            self.quantity is None
            or self.average_entry_price is None
            or self.current_price is None
        ):
            return None

        side = (self.side or "").upper()

        if side in {"LONG", "BUY"}:
            return (
                self.current_price - self.average_entry_price
            ) * self.quantity

        if side in {"SHORT", "SELL"}:
            return (
                self.average_entry_price - self.current_price
            ) * self.quantity

        return None

    def calculate_pnl_percent(self) -> Optional[float]:
        """
        Calculate unrealized P&L percentage against entry value.
        """

        pnl = self.calculate_unrealized_pnl()

        if pnl is None:
            return None

        if (
            self.average_entry_price is None
            or self.quantity is None
        ):
            return None

        entry_value = (
            self.average_entry_price * self.quantity
        )

        if entry_value == 0:
            return None

        return (pnl / entry_value) * 100.0

    # ------------------------------------------------------------------
    # Risk / Reward
    # ------------------------------------------------------------------

    def calculate_risk_value(self) -> Optional[float]:
        """
        Calculate absolute distance from entry to stop multiplied by
        position quantity.
        """

        if (
            self.average_entry_price is None
            or self.stop_price is None
            or self.quantity is None
        ):
            return None

        return (
            abs(
                self.average_entry_price
                - self.stop_price
            )
            * self.quantity
        )

    def calculate_reward_value(self) -> Optional[float]:
        """
        Calculate absolute distance from entry to target multiplied by
        position quantity.
        """

        if (
            self.average_entry_price is None
            or self.target_price is None
            or self.quantity is None
        ):
            return None

        return (
            abs(
                self.target_price
                - self.average_entry_price
            )
            * self.quantity
        )

    # ------------------------------------------------------------------
    # Related References
    # ------------------------------------------------------------------

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
        Return structural position issues.

        Validation only. No trading decision is produced.
        """

        issues: list[str] = []

        if not self.has_identity():
            issues.append("MISSING_POSITION_IDENTITY")

        if not self.has_market_identity():
            issues.append("MISSING_MARKET_IDENTITY")

        if not self.timestamp:
            issues.append("MISSING_TIMESTAMP")

        if not self.source:
            issues.append("MISSING_SOURCE")

        if (
            self.quantity is not None
            and self.quantity == 0
            and self.side is not None
            and self.side.upper() not in {"FLAT", "NONE", "UNKNOWN"}
        ):
            issues.append("ZERO_QUANTITY_WITH_NON_FLAT_SIDE")

        if (
            self.position_status
            and self.position_status.upper() == "OPEN"
            and self.quantity == 0
        ):
            issues.append("OPEN_POSITION_WITH_ZERO_QUANTITY")

        if (
            self.derived_fields
            and not self.has_source_reference()
        ):
            issues.append(
                "DERIVED_POSITION_DATA_WITHOUT_SOURCE_REFERENCE"
            )

        return tuple(issues)

    def is_structurally_valid(self) -> bool:
        """Return True when no structural issues exist."""

        return not self.issue_flags()

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize position information into a mapping."""

        data = asdict(self)

        data["observed_fields"] = list(self.observed_fields)
        data["derived_fields"] = list(self.derived_fields)
        data["metadata"] = dict(self.metadata)

        return data

    @staticmethod
    def schema_info() -> dict[str, str]:
        """Return schema identity and version."""

        return {
            "schema": MARKET_POSITION_SCHEMA,
            "version": MARKET_POSITION_SCHEMA_VERSION,
        }


def market_position_health() -> dict[str, Any]:
    """Return structural health information for the position schema."""

    return {
        "schema": MARKET_POSITION_SCHEMA,
        "version": MARKET_POSITION_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "position_identity_supported": True,
        "market_identity_supported": True,
        "side_supported": True,
        "position_status_supported": True,
        "exposure_supported": True,
        "market_value_supported": True,
        "unrealized_pnl_supported": True,
        "realized_pnl_supported": True,
        "pnl_percent_supported": True,
        "risk_reward_measurements_supported": True,
        "order_reference_supported": True,
        "execution_reference_supported": True,
        "transaction_reference_supported": True,
        "source_reference_supported": True,
        "provenance_supported": True,
        "observed_derived_separation": True,
        "position_order_separation": True,
        "position_execution_separation": True,
        "decision_logic": False,
        "order_generation": False,
        "execution_authorization": False,
        "broker_interaction": False,
        "prediction_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_POSITION_SCHEMA_VERSION",
    "MARKET_POSITION_SCHEMA",
    "MarketPosition",
    "market_position_health",
]