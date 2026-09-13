"""
ROBOMLM PLUS
V6 Market Order Schema

Purpose:
    Structural representation of an observed or referenced market order.

Rules:
    - Order representation only.
    - No trading decision.
    - No order generation.
    - No execution authorization.
    - No broker/API interaction.
    - No prediction.
    - No V7+ dependency.
    - Order state remains distinct from execution/fill state.
    - Observed and derived information remain distinguishable.
    - Does not mutate source data.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Optional


MARKET_ORDER_SCHEMA_VERSION = "1.0.0"
MARKET_ORDER_SCHEMA = "V6_MARKET_ORDER"


@dataclass(frozen=True)
class MarketOrder:
    """
    Immutable structural representation of market-order information.

    This schema describes an order and its observable state. It does not
    create, submit, modify, cancel, or authorize an order.
    """

    # ------------------------------------------------------------------
    # Order Identity
    # ------------------------------------------------------------------

    order_id: Optional[str] = None
    client_order_id: Optional[str] = None
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
    # Order Classification
    # ------------------------------------------------------------------

    side: Optional[str] = None
    order_type: Optional[str] = None
    time_in_force: Optional[str] = None
    order_status: Optional[str] = None

    # ------------------------------------------------------------------
    # Quantity / Price
    # ------------------------------------------------------------------

    quantity: Optional[float] = None
    filled_quantity: Optional[float] = None
    remaining_quantity: Optional[float] = None

    price: Optional[float] = None
    average_price: Optional[float] = None
    trigger_price: Optional[float] = None

    # ------------------------------------------------------------------
    # Value / Execution State
    # ------------------------------------------------------------------

    notional_value: Optional[float] = None
    filled_value: Optional[float] = None
    remaining_value: Optional[float] = None

    fill_count: Optional[int] = None
    last_fill_price: Optional[float] = None
    last_fill_quantity: Optional[float] = None

    # ------------------------------------------------------------------
    # Execution Context
    # ------------------------------------------------------------------

    execution_id: Optional[str] = None
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    execution_mode: Optional[str] = None

    # ------------------------------------------------------------------
    # Source References
    # ------------------------------------------------------------------

    observation_id: Optional[str] = None
    context_id: Optional[str] = None
    transaction_id: Optional[str] = None
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
        """Validate structural order information."""

        if self.sequence is not None:
            if isinstance(self.sequence, bool):
                raise TypeError(
                    "MarketOrder.sequence must be an integer or None."
                )

            if not isinstance(self.sequence, int):
                raise TypeError(
                    "MarketOrder.sequence must be an integer or None."
                )

            if self.sequence < 0:
                raise ValueError(
                    "MarketOrder.sequence cannot be negative."
                )

        if self.fill_count is not None:
            if isinstance(self.fill_count, bool):
                raise TypeError(
                    "MarketOrder.fill_count must be an integer or None."
                )

            if not isinstance(self.fill_count, int):
                raise TypeError(
                    "MarketOrder.fill_count must be an integer or None."
                )

            if self.fill_count < 0:
                raise ValueError(
                    "MarketOrder.fill_count cannot be negative."
                )

        numeric_fields = {
            "quantity": self.quantity,
            "filled_quantity": self.filled_quantity,
            "remaining_quantity": self.remaining_quantity,
            "price": self.price,
            "average_price": self.average_price,
            "trigger_price": self.trigger_price,
            "notional_value": self.notional_value,
            "filled_value": self.filled_value,
            "remaining_value": self.remaining_value,
            "last_fill_price": self.last_fill_price,
            "last_fill_quantity": self.last_fill_quantity,
        }

        for field_name, value in numeric_fields.items():
            if value is None:
                continue

            if isinstance(value, bool):
                raise TypeError(
                    f"MarketOrder.{field_name} must be numeric or None."
                )

            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"MarketOrder.{field_name} must be numeric or None."
                )

        non_negative_fields = (
            "quantity",
            "filled_quantity",
            "remaining_quantity",
            "price",
            "average_price",
            "trigger_price",
            "notional_value",
            "filled_value",
            "remaining_value",
            "last_fill_price",
            "last_fill_quantity",
        )

        for field_name in non_negative_fields:
            value = getattr(self, field_name)

            if value is not None and value < 0:
                raise ValueError(
                    f"MarketOrder.{field_name} cannot be negative."
                )

        if self.side is not None:
            normalized_side = self.side.upper()

            if normalized_side not in {
                "BUY",
                "SELL",
                "UNKNOWN",
                "NONE",
            }:
                raise ValueError(
                    "MarketOrder.side must be BUY, SELL, UNKNOWN, "
                    "or NONE when provided."
                )

        if self.metadata is None:
            raise TypeError(
                "MarketOrder.metadata must be a mapping."
            )

        if not isinstance(self.metadata, Mapping):
            raise TypeError(
                "MarketOrder.metadata must be a mapping."
            )

        if isinstance(self.observed_fields, str):
            raise TypeError(
                "MarketOrder.observed_fields must be a sequence of names."
            )

        if isinstance(self.derived_fields, str):
            raise TypeError(
                "MarketOrder.derived_fields must be a sequence of names."
            )

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    def has_identity(self) -> bool:
        """Return True when order identity exists."""

        return bool(
            self.order_id
            or self.client_order_id
        )

    def has_market_identity(self) -> bool:
        """Return True when market identity exists."""

        return bool(
            self.market
            or self.instrument
            or self.symbol
        )

    # ------------------------------------------------------------------
    # Order Classification
    # ------------------------------------------------------------------

    def has_side(self) -> bool:
        """Return True when order side exists."""

        return self.side is not None

    def has_order_type(self) -> bool:
        """Return True when order type exists."""

        return self.order_type is not None

    def has_status(self) -> bool:
        """Return True when order status exists."""

        return self.order_status is not None

    # ------------------------------------------------------------------
    # Quantity
    # ------------------------------------------------------------------

    def has_quantity(self) -> bool:
        """Return True when requested quantity exists."""

        return self.quantity is not None

    def has_fill_information(self) -> bool:
        """Return True when fill information exists."""

        return any(
            value is not None
            for value in (
                self.filled_quantity,
                self.fill_count,
                self.last_fill_price,
                self.last_fill_quantity,
            )
        )

    def calculate_remaining_quantity(self) -> Optional[float]:
        """
        Calculate remaining quantity from requested and filled quantity.
        """

        if self.quantity is None or self.filled_quantity is None:
            return None

        return max(
            self.quantity - self.filled_quantity,
            0.0,
        )

    def fill_ratio(self) -> Optional[float]:
        """Calculate filled quantity / requested quantity."""

        if self.quantity is None:
            return None

        if self.quantity == 0:
            return None

        if self.filled_quantity is None:
            return None

        return self.filled_quantity / self.quantity

    # ------------------------------------------------------------------
    # Price / Value
    # ------------------------------------------------------------------

    def calculate_notional_value(self) -> Optional[float]:
        """Calculate order notional value from price and quantity."""

        if self.price is None or self.quantity is None:
            return None

        return self.price * self.quantity

    def calculate_filled_value(self) -> Optional[float]:
        """Calculate filled value from average price and filled quantity."""

        if self.average_price is None:
            return None

        if self.filled_quantity is None:
            return None

        return self.average_price * self.filled_quantity

    def calculate_remaining_value(self) -> Optional[float]:
        """Calculate remaining value from price and remaining quantity."""

        remaining = self.remaining_quantity

        if remaining is None:
            remaining = self.calculate_remaining_quantity()

        if self.price is None or remaining is None:
            return None

        return self.price * remaining

    # ------------------------------------------------------------------
    # Execution References
    # ------------------------------------------------------------------

    def has_execution_reference(self) -> bool:
        """Return True when an execution reference exists."""

        return bool(
            self.execution_id
            or self.execution_ref
            or self.request_id
        )

    # ------------------------------------------------------------------
    # Source References
    # ------------------------------------------------------------------

    def has_source_reference(self) -> bool:
        """Return True when an upstream reference exists."""

        return bool(
            self.observation_id
            or self.context_id
            or self.transaction_id
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
        Return structural order issues.

        Validation only. No trading decision is produced.
        """

        issues: list[str] = []

        if not self.has_identity():
            issues.append("MISSING_ORDER_IDENTITY")

        if not self.has_market_identity():
            issues.append("MISSING_MARKET_IDENTITY")

        if not self.timestamp:
            issues.append("MISSING_TIMESTAMP")

        if not self.source:
            issues.append("MISSING_SOURCE")

        if self.quantity is not None and self.quantity == 0:
            issues.append("ZERO_ORDER_QUANTITY")

        if (
            self.filled_quantity is not None
            and self.quantity is not None
            and self.filled_quantity > self.quantity
        ):
            issues.append("FILLED_QUANTITY_EXCEEDS_ORDER_QUANTITY")

        if (
            self.remaining_quantity is not None
            and self.quantity is not None
            and self.remaining_quantity > self.quantity
        ):
            issues.append("REMAINING_QUANTITY_EXCEEDS_ORDER_QUANTITY")

        if (
            self.filled_quantity is not None
            and self.remaining_quantity is not None
            and self.quantity is not None
            and (
                self.filled_quantity + self.remaining_quantity
                > self.quantity
            )
        ):
            issues.append("QUANTITY_STATE_INCONSISTENCY")

        if (
            self.derived_fields
            and not self.has_source_reference()
        ):
            issues.append(
                "DERIVED_ORDER_DATA_WITHOUT_SOURCE_REFERENCE"
            )

        return tuple(issues)

    def is_structurally_valid(self) -> bool:
        """Return True when no structural issues exist."""

        return not self.issue_flags()

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize order information into a mapping."""

        data = asdict(self)

        data["observed_fields"] = list(self.observed_fields)
        data["derived_fields"] = list(self.derived_fields)
        data["metadata"] = dict(self.metadata)

        return data

    @staticmethod
    def schema_info() -> dict[str, str]:
        """Return schema identity and version."""

        return {
            "schema": MARKET_ORDER_SCHEMA,
            "version": MARKET_ORDER_SCHEMA_VERSION,
        }


def market_order_health() -> dict[str, Any]:
    """Return structural health information for the order schema."""

    return {
        "schema": MARKET_ORDER_SCHEMA,
        "version": MARKET_ORDER_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "order_identity_supported": True,
        "market_identity_supported": True,
        "side_supported": True,
        "order_type_supported": True,
        "order_status_supported": True,
        "quantity_supported": True,
        "fill_state_supported": True,
        "price_supported": True,
        "notional_value_supported": True,
        "execution_reference_supported": True,
        "source_reference_supported": True,
        "provenance_supported": True,
        "observed_derived_separation": True,
        "order_execution_separation": True,
        "decision_logic": False,
        "order_generation": False,
        "execution_authorization": False,
        "broker_interaction": False,
        "prediction_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_ORDER_SCHEMA_VERSION",
    "MARKET_ORDER_SCHEMA",
    "MarketOrder",
    "market_order_health",
]