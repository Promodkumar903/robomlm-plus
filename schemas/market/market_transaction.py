"""
ROBOMLM PLUS
V6 Market Transaction Schema

Purpose:
    Structural representation of observed market transactions and
    transaction-flow information.

Rules:
    - Transaction representation only.
    - No trading decision.
    - No execution authorization.
    - No order generation.
    - No broker/API interaction.
    - No prediction.
    - No V7+ dependency.
    - Activity, volume, and transaction count remain distinct.
    - Observed and derived information remain distinguishable.
    - Does not mutate source data.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Optional


MARKET_TRANSACTION_SCHEMA_VERSION = "1.0.0"
MARKET_TRANSACTION_SCHEMA = "V6_MARKET_TRANSACTION"


@dataclass(frozen=True)
class MarketTransaction:
    """
    Immutable structural representation of market transaction data.

    A transaction represents an observed market trade or transaction
    record. It is deliberately separate from an order request, execution
    instruction, or trading decision.
    """

    # ------------------------------------------------------------------
    # Transaction Identity
    # ------------------------------------------------------------------

    transaction_id: Optional[str] = None
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
    # Transaction Attributes
    # ------------------------------------------------------------------

    price: Optional[float] = None
    quantity: Optional[float] = None
    value: Optional[float] = None
    side: Optional[str] = None
    trade_type: Optional[str] = None

    # ------------------------------------------------------------------
    # Market Activity Context
    # ------------------------------------------------------------------

    cumulative_volume: Optional[float] = None
    cumulative_value: Optional[float] = None
    transaction_count: Optional[int] = None
    activity_count: Optional[int] = None
    activity_rate: Optional[float] = None

    # ------------------------------------------------------------------
    # Price Context
    # ------------------------------------------------------------------

    previous_price: Optional[float] = None
    price_change: Optional[float] = None
    price_change_percent: Optional[float] = None

    # ------------------------------------------------------------------
    # Flow Context
    # ------------------------------------------------------------------

    buy_volume: Optional[float] = None
    sell_volume: Optional[float] = None
    volume_delta: Optional[float] = None
    buy_sell_ratio: Optional[float] = None
    participation_balance: Optional[float] = None

    # ------------------------------------------------------------------
    # Source References
    # ------------------------------------------------------------------

    observation_id: Optional[str] = None
    context_id: Optional[str] = None
    regime_id: Optional[str] = None
    participation_id: Optional[str] = None
    liquidity_id: Optional[str] = None

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
        """Validate structural transaction information."""

        if self.sequence is not None:
            if isinstance(self.sequence, bool):
                raise TypeError(
                    "MarketTransaction.sequence must be an integer or None."
                )

            if not isinstance(self.sequence, int):
                raise TypeError(
                    "MarketTransaction.sequence must be an integer or None."
                )

            if self.sequence < 0:
                raise ValueError(
                    "MarketTransaction.sequence cannot be negative."
                )

        if self.transaction_count is not None:
            if isinstance(self.transaction_count, bool):
                raise TypeError(
                    "MarketTransaction.transaction_count must be "
                    "an integer or None."
                )

            if not isinstance(self.transaction_count, int):
                raise TypeError(
                    "MarketTransaction.transaction_count must be "
                    "an integer or None."
                )

            if self.transaction_count < 0:
                raise ValueError(
                    "MarketTransaction.transaction_count cannot be negative."
                )

        if self.activity_count is not None:
            if isinstance(self.activity_count, bool):
                raise TypeError(
                    "MarketTransaction.activity_count must be "
                    "an integer or None."
                )

            if not isinstance(self.activity_count, int):
                raise TypeError(
                    "MarketTransaction.activity_count must be "
                    "an integer or None."
                )

            if self.activity_count < 0:
                raise ValueError(
                    "MarketTransaction.activity_count cannot be negative."
                )

        numeric_fields = {
            "price": self.price,
            "quantity": self.quantity,
            "value": self.value,
            "cumulative_volume": self.cumulative_volume,
            "cumulative_value": self.cumulative_value,
            "activity_rate": self.activity_rate,
            "previous_price": self.previous_price,
            "price_change": self.price_change,
            "price_change_percent": self.price_change_percent,
            "buy_volume": self.buy_volume,
            "sell_volume": self.sell_volume,
            "volume_delta": self.volume_delta,
            "buy_sell_ratio": self.buy_sell_ratio,
            "participation_balance": self.participation_balance,
        }

        for field_name, value in numeric_fields.items():
            if value is None:
                continue

            if isinstance(value, bool):
                raise TypeError(
                    f"MarketTransaction.{field_name} "
                    "must be numeric or None."
                )

            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"MarketTransaction.{field_name} "
                    "must be numeric or None."
                )

        non_negative_fields = (
            "price",
            "quantity",
            "value",
            "cumulative_volume",
            "cumulative_value",
            "activity_rate",
            "previous_price",
            "buy_volume",
            "sell_volume",
            "buy_sell_ratio",
        )

        for field_name in non_negative_fields:
            value = getattr(self, field_name)

            if value is not None and value < 0:
                raise ValueError(
                    f"MarketTransaction.{field_name} cannot be negative."
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
                    "MarketTransaction.side must be BUY, SELL, "
                    "UNKNOWN, or NONE when provided."
                )

        if self.metadata is None:
            raise TypeError(
                "MarketTransaction.metadata must be a mapping."
            )

        if not isinstance(self.metadata, Mapping):
            raise TypeError(
                "MarketTransaction.metadata must be a mapping."
            )

        if isinstance(self.observed_fields, str):
            raise TypeError(
                "MarketTransaction.observed_fields "
                "must be a sequence of names."
            )

        if isinstance(self.derived_fields, str):
            raise TypeError(
                "MarketTransaction.derived_fields "
                "must be a sequence of names."
            )

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    def has_identity(self) -> bool:
        """Return True when transaction identity exists."""

        return bool(
            self.transaction_id
            or self.sequence is not None
        )

    def has_market_identity(self) -> bool:
        """Return True when market identity exists."""

        return bool(
            self.market
            or self.instrument
            or self.symbol
        )

    # ------------------------------------------------------------------
    # Transaction Measurements
    # ------------------------------------------------------------------

    def has_price(self) -> bool:
        """Return True when transaction price exists."""

        return self.price is not None

    def has_quantity(self) -> bool:
        """Return True when transaction quantity exists."""

        return self.quantity is not None

    def has_transaction_value(self) -> bool:
        """Return True when transaction value exists."""

        return self.value is not None

    def calculate_transaction_value(self) -> Optional[float]:
        """
        Calculate transaction value from price and quantity.

        Structural calculation only.
        """

        if self.price is None or self.quantity is None:
            return None

        return self.price * self.quantity

    # ------------------------------------------------------------------
    # Price Change
    # ------------------------------------------------------------------

    def calculate_price_change(self) -> Optional[float]:
        """Calculate absolute price change."""

        if self.price is None or self.previous_price is None:
            return None

        return self.price - self.previous_price

    def calculate_price_change_percent(self) -> Optional[float]:
        """Calculate percentage price change."""

        if self.price is None or self.previous_price is None:
            return None

        if self.previous_price == 0:
            return None

        return (
            (self.price - self.previous_price)
            / self.previous_price
        ) * 100.0

    # ------------------------------------------------------------------
    # Flow Measurements
    # ------------------------------------------------------------------

    def has_buy_sell_volume(self) -> bool:
        """Return True when buy and sell volume are available."""

        return (
            self.buy_volume is not None
            and self.sell_volume is not None
        )

    def calculate_volume_delta(self) -> Optional[float]:
        """
        Calculate buy volume minus sell volume.

        Structural flow measurement only.
        """

        if not self.has_buy_sell_volume():
            return None

        return self.buy_volume - self.sell_volume

    def calculate_buy_sell_ratio(self) -> Optional[float]:
        """
        Calculate buy-volume / sell-volume ratio.

        Returns None when sell volume is unavailable or zero.
        """

        if not self.has_buy_sell_volume():
            return None

        if self.sell_volume == 0:
            return None

        return self.buy_volume / self.sell_volume

    def calculate_participation_balance(self) -> Optional[float]:
        """
        Calculate normalized participation balance.

        Formula:
            (buy_volume - sell_volume)
            / (buy_volume + sell_volume)
        """

        if not self.has_buy_sell_volume():
            return None

        total = self.buy_volume + self.sell_volume

        if total == 0:
            return None

        return (
            (self.buy_volume - self.sell_volume)
            / total
        )

    # ------------------------------------------------------------------
    # Activity
    # ------------------------------------------------------------------

    def has_activity_measurement(self) -> bool:
        """
        Return True when activity information exists.

        Activity is intentionally separate from volume.
        """

        return any(
            value is not None
            for value in (
                self.transaction_count,
                self.activity_count,
                self.activity_rate,
            )
        )

    def has_volume_measurement(self) -> bool:
        """Return True when volume information exists."""

        return any(
            value is not None
            for value in (
                self.quantity,
                self.cumulative_volume,
                self.buy_volume,
                self.sell_volume,
            )
        )

    # ------------------------------------------------------------------
    # Source References
    # ------------------------------------------------------------------

    def has_source_reference(self) -> bool:
        """Return True when an upstream reference exists."""

        return bool(
            self.observation_id
            or self.context_id
            or self.regime_id
            or self.participation_id
            or self.liquidity_id
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
        Return structural transaction issues.

        Validation only. No trading decision is produced.
        """

        issues: list[str] = []

        if not self.has_identity():
            issues.append("MISSING_TRANSACTION_IDENTITY")

        if not self.has_market_identity():
            issues.append("MISSING_MARKET_IDENTITY")

        if not self.timestamp:
            issues.append("MISSING_TIMESTAMP")

        if not self.source:
            issues.append("MISSING_SOURCE")

        if (
            self.price is not None
            and self.previous_price is not None
            and self.previous_price == 0
        ):
            issues.append("ZERO_PREVIOUS_PRICE")

        if (
            self.buy_volume is not None
            and self.sell_volume is not None
            and self.buy_volume == 0
            and self.sell_volume == 0
        ):
            issues.append("ZERO_BUY_SELL_VOLUME")

        if not self.has_source_reference():
            issues.append("MISSING_SOURCE_REFERENCE")

        if (
            self.derived_fields
            and not self.has_source_reference()
        ):
            issues.append(
                "DERIVED_TRANSACTION_DATA_WITHOUT_SOURCE_REFERENCE"
            )

        return tuple(issues)

    def is_structurally_valid(self) -> bool:
        """Return True when no structural issues exist."""

        return not self.issue_flags()

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize transaction information into a mapping."""

        data = asdict(self)

        data["observed_fields"] = list(self.observed_fields)
        data["derived_fields"] = list(self.derived_fields)
        data["metadata"] = dict(self.metadata)

        return data

    @staticmethod
    def schema_info() -> dict[str, str]:
        """Return schema identity and version."""

        return {
            "schema": MARKET_TRANSACTION_SCHEMA,
            "version": MARKET_TRANSACTION_SCHEMA_VERSION,
        }


def market_transaction_health() -> dict[str, Any]:
    """Return structural health information for the transaction schema."""

    return {
        "schema": MARKET_TRANSACTION_SCHEMA,
        "version": MARKET_TRANSACTION_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "transaction_identity_supported": True,
        "market_identity_supported": True,
        "price_supported": True,
        "quantity_supported": True,
        "transaction_value_supported": True,
        "activity_supported": True,
        "volume_supported": True,
        "buy_sell_flow_supported": True,
        "volume_delta_supported": True,
        "buy_sell_ratio_supported": True,
        "participation_balance_supported": True,
        "price_change_supported": True,
        "provenance_supported": True,
        "source_reference_supported": True,
        "observed_derived_separation": True,
        "activity_volume_separation": True,
        "decision_logic": False,
        "execution_logic": False,
        "order_generation": False,
        "execution_authorization": False,
        "prediction_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_TRANSACTION_SCHEMA_VERSION",
    "MARKET_TRANSACTION_SCHEMA",
    "MarketTransaction",
    "market_transaction_health",
]