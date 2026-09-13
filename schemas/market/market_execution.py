"""
ROBOMLM PLUS
V6 Market Execution Schema

Purpose:
    Structural representation of execution-related market observations.

Rules:
    - Execution information representation only.
    - No order placement.
    - No broker/API execution.
    - No trading decision.
    - No position sizing.
    - No execution authorization.
    - No V7+ dependency.
    - Observed and derived information remain distinguishable.
    - Market execution state and actual order execution remain separate.
    - Does not mutate source data.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Optional


MARKET_EXECUTION_SCHEMA_VERSION = "1.0.0"
MARKET_EXECUTION_SCHEMA = "V6_MARKET_EXECUTION"


@dataclass(frozen=True)
class MarketExecution:
    """
    Immutable structural representation of execution-related market data.

    This schema describes execution conditions, observed execution
    measurements, and execution-state information. It does not execute
    orders or authorize execution.
    """

    # ------------------------------------------------------------------
    # Execution Identity
    # ------------------------------------------------------------------

    execution_id: Optional[str] = None
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
    # Source References
    # ------------------------------------------------------------------

    observation_id: Optional[str] = None
    context_id: Optional[str] = None
    regime_id: Optional[str] = None
    liquidity_id: Optional[str] = None
    orderbook_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Execution Environment
    # ------------------------------------------------------------------

    mode: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Market Execution Conditions
    # ------------------------------------------------------------------

    last_price: Optional[float] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    mid_price: Optional[float] = None
    spread: Optional[float] = None

    # ------------------------------------------------------------------
    # Transaction / Activity Measurements
    # ------------------------------------------------------------------

    trade_price: Optional[float] = None
    trade_size: Optional[float] = None
    traded_volume: Optional[float] = None
    transaction_count: Optional[int] = None

    # ------------------------------------------------------------------
    # Execution Quality Measurements
    # ------------------------------------------------------------------

    requested_price: Optional[float] = None
    executed_price: Optional[float] = None
    price_deviation: Optional[float] = None
    price_deviation_percent: Optional[float] = None

    requested_quantity: Optional[float] = None
    executed_quantity: Optional[float] = None
    remaining_quantity: Optional[float] = None
    fill_ratio: Optional[float] = None

    # ------------------------------------------------------------------
    # Timing Measurements
    # ------------------------------------------------------------------

    observed_latency_ms: Optional[float] = None
    market_data_latency_ms: Optional[float] = None
    execution_latency_ms: Optional[float] = None

    # ------------------------------------------------------------------
    # Execution State
    # ------------------------------------------------------------------

    execution_state: Optional[str] = None
    fill_state: Optional[str] = None
    liquidity_state: Optional[str] = None
    slippage_state: Optional[str] = None

    # ------------------------------------------------------------------
    # Structural Metrics
    # ------------------------------------------------------------------

    execution_score: Optional[float] = None
    liquidity_score: Optional[float] = None
    confidence: Optional[float] = None

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
        """Validate structural execution information."""

        if self.sequence is not None:
            if isinstance(self.sequence, bool):
                raise TypeError(
                    "MarketExecution.sequence must be an integer or None."
                )

            if not isinstance(self.sequence, int):
                raise TypeError(
                    "MarketExecution.sequence must be an integer or None."
                )

            if self.sequence < 0:
                raise ValueError(
                    "MarketExecution.sequence cannot be negative."
                )

        if self.transaction_count is not None:
            if isinstance(self.transaction_count, bool):
                raise TypeError(
                    "MarketExecution.transaction_count must be "
                    "an integer or None."
                )

            if not isinstance(self.transaction_count, int):
                raise TypeError(
                    "MarketExecution.transaction_count must be "
                    "an integer or None."
                )

            if self.transaction_count < 0:
                raise ValueError(
                    "MarketExecution.transaction_count cannot be negative."
                )

        numeric_fields = {
            "last_price": self.last_price,
            "bid": self.bid,
            "ask": self.ask,
            "mid_price": self.mid_price,
            "spread": self.spread,
            "trade_price": self.trade_price,
            "trade_size": self.trade_size,
            "traded_volume": self.traded_volume,
            "requested_price": self.requested_price,
            "executed_price": self.executed_price,
            "price_deviation": self.price_deviation,
            "price_deviation_percent": self.price_deviation_percent,
            "requested_quantity": self.requested_quantity,
            "executed_quantity": self.executed_quantity,
            "remaining_quantity": self.remaining_quantity,
            "fill_ratio": self.fill_ratio,
            "observed_latency_ms": self.observed_latency_ms,
            "market_data_latency_ms": self.market_data_latency_ms,
            "execution_latency_ms": self.execution_latency_ms,
            "execution_score": self.execution_score,
            "liquidity_score": self.liquidity_score,
            "confidence": self.confidence,
        }

        for field_name, value in numeric_fields.items():
            if value is None:
                continue

            if isinstance(value, bool):
                raise TypeError(
                    f"MarketExecution.{field_name} "
                    "must be numeric or None."
                )

            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"MarketExecution.{field_name} "
                    "must be numeric or None."
                )

        non_negative_fields = (
            "last_price",
            "bid",
            "ask",
            "mid_price",
            "spread",
            "trade_price",
            "trade_size",
            "traded_volume",
            "requested_price",
            "executed_price",
            "requested_quantity",
            "executed_quantity",
            "remaining_quantity",
            "observed_latency_ms",
            "market_data_latency_ms",
            "execution_latency_ms",
            "execution_score",
            "liquidity_score",
            "confidence",
        )

        for field_name in non_negative_fields:
            value = getattr(self, field_name)

            if value is not None and value < 0:
                raise ValueError(
                    f"MarketExecution.{field_name} cannot be negative."
                )

        if self.fill_ratio is not None:
            if not 0.0 <= self.fill_ratio <= 1.0:
                raise ValueError(
                    "MarketExecution.fill_ratio must be between "
                    "0.0 and 1.0."
                )

        if self.bid is not None and self.ask is not None:
            if self.ask < self.bid:
                raise ValueError(
                    "MarketExecution.ask cannot be lower than bid."
                )

        if self.metadata is None:
            raise TypeError(
                "MarketExecution.metadata must be a mapping."
            )

        if not isinstance(self.metadata, Mapping):
            raise TypeError(
                "MarketExecution.metadata must be a mapping."
            )

        if isinstance(self.observed_fields, str):
            raise TypeError(
                "MarketExecution.observed_fields "
                "must be a sequence of names."
            )

        if isinstance(self.derived_fields, str):
            raise TypeError(
                "MarketExecution.derived_fields "
                "must be a sequence of names."
            )

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    def has_identity(self) -> bool:
        """Return True when execution identity exists."""

        return bool(
            self.execution_id
            or self.instrument
            or self.symbol
        )

    def has_market_identity(self) -> bool:
        """Return True when market identity exists."""

        return bool(
            self.market
            or self.instrument
            or self.symbol
        )

    # ------------------------------------------------------------------
    # Market Price
    # ------------------------------------------------------------------

    def has_market_price(self) -> bool:
        """Return True when a market price exists."""

        return any(
            value is not None
            for value in (
                self.last_price,
                self.bid,
                self.ask,
                self.mid_price,
            )
        )

    def has_trade_observation(self) -> bool:
        """Return True when trade price or size exists."""

        return (
            self.trade_price is not None
            or self.trade_size is not None
        )

    # ------------------------------------------------------------------
    # Order-Book Relationship
    # ------------------------------------------------------------------

    def has_bid_ask(self) -> bool:
        """Return True when both bid and ask exist."""

        return (
            self.bid is not None
            and self.ask is not None
        )

    def calculate_mid_price(self) -> Optional[float]:
        """Calculate the bid/ask midpoint."""

        if not self.has_bid_ask():
            return None

        return (self.bid + self.ask) / 2.0

    def calculate_spread(self) -> Optional[float]:
        """Calculate absolute bid/ask spread."""

        if not self.has_bid_ask():
            return None

        return self.ask - self.bid

    # ------------------------------------------------------------------
    # Execution Measurements
    # ------------------------------------------------------------------

    def has_requested_price(self) -> bool:
        """Return True when requested price exists."""

        return self.requested_price is not None

    def has_executed_price(self) -> bool:
        """Return True when executed price exists."""

        return self.executed_price is not None

    def has_quantity_measurement(self) -> bool:
        """Return True when quantity information exists."""

        return any(
            value is not None
            for value in (
                self.requested_quantity,
                self.executed_quantity,
                self.remaining_quantity,
            )
        )

    def calculate_price_deviation(self) -> Optional[float]:
        """
        Calculate executed price deviation from requested price.

        Structural measurement only.
        """

        if (
            self.requested_price is None
            or self.executed_price is None
        ):
            return None

        return self.executed_price - self.requested_price

    def calculate_price_deviation_percent(self) -> Optional[float]:
        """
        Calculate executed-price deviation percentage.

        Returns None when requested price is unavailable or zero.
        """

        if (
            self.requested_price is None
            or self.executed_price is None
        ):
            return None

        if self.requested_price == 0:
            return None

        return (
            (
                self.executed_price
                - self.requested_price
            )
            / self.requested_price
        ) * 100.0

    def calculate_fill_ratio(self) -> Optional[float]:
        """
        Calculate executed quantity / requested quantity.

        Returns None when requested quantity is unavailable or zero.
        """

        if (
            self.requested_quantity is None
            or self.executed_quantity is None
        ):
            return None

        if self.requested_quantity == 0:
            return None

        return (
            self.executed_quantity
            / self.requested_quantity
        )

    def calculate_remaining_quantity(self) -> Optional[float]:
        """
        Calculate unfilled quantity.

        Structural calculation only.
        """

        if (
            self.requested_quantity is None
            or self.executed_quantity is None
        ):
            return None

        return max(
            self.requested_quantity
            - self.executed_quantity,
            0.0,
        )

    # ------------------------------------------------------------------
    # Latency
    # ------------------------------------------------------------------

    def has_latency_measurement(self) -> bool:
        """Return True when any latency measurement exists."""

        return any(
            value is not None
            for value in (
                self.observed_latency_ms,
                self.market_data_latency_ms,
                self.execution_latency_ms,
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
            or self.liquidity_id
            or self.orderbook_id
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
        Return structural execution issues.

        Validation only. No execution authorization is produced.
        """

        issues: list[str] = []

        if not self.has_identity():
            issues.append("MISSING_EXECUTION_IDENTITY")

        if not self.has_market_identity():
            issues.append("MISSING_MARKET_IDENTITY")

        if not self.timestamp:
            issues.append("MISSING_TIMESTAMP")

        if not self.source:
            issues.append("MISSING_SOURCE")

        if (
            self.bid is not None
            and self.ask is not None
            and self.ask < self.bid
        ):
            issues.append("INVALID_BID_ASK_RELATION")

        if (
            self.requested_quantity is not None
            and self.executed_quantity is not None
            and self.executed_quantity > self.requested_quantity
        ):
            issues.append("EXECUTED_QUANTITY_EXCEEDS_REQUESTED")

        if (
            self.executed_quantity is not None
            and self.executed_quantity < 0
        ):
            issues.append("INVALID_EXECUTED_QUANTITY")

        if (
            self.remaining_quantity is not None
            and self.requested_quantity is not None
            and self.remaining_quantity > self.requested_quantity
        ):
            issues.append("REMAINING_QUANTITY_EXCEEDS_REQUESTED")

        if not self.has_source_reference():
            issues.append("MISSING_SOURCE_REFERENCE")

        if (
            self.derived_fields
            and not self.has_source_reference()
        ):
            issues.append(
                "DERIVED_EXECUTION_DATA_WITHOUT_SOURCE_REFERENCE"
            )

        return tuple(issues)

    def is_structurally_valid(self) -> bool:
        """Return True when no structural issues exist."""

        return not self.issue_flags()

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize execution information into a mapping."""

        data = asdict(self)

        data["observed_fields"] = list(self.observed_fields)
        data["derived_fields"] = list(self.derived_fields)
        data["metadata"] = dict(self.metadata)

        return data

    @staticmethod
    def schema_info() -> dict[str, str]:
        """Return schema identity and version."""

        return {
            "schema": MARKET_EXECUTION_SCHEMA,
            "version": MARKET_EXECUTION_SCHEMA_VERSION,
        }


def market_execution_health() -> dict[str, Any]:
    """Return structural health information for the execution schema."""

    return {
        "schema": MARKET_EXECUTION_SCHEMA,
        "version": MARKET_EXECUTION_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "market_identity_supported": True,
        "execution_identity_supported": True,
        "market_price_supported": True,
        "bid_ask_supported": True,
        "trade_observation_supported": True,
        "quantity_measurement_supported": True,
        "fill_ratio_supported": True,
        "price_deviation_supported": True,
        "latency_supported": True,
        "execution_state_supported": True,
        "liquidity_state_supported": True,
        "provenance_supported": True,
        "source_reference_supported": True,
        "observed_derived_separation": True,
        "order_placement": False,
        "execution_authorization": False,
        "decision_logic": False,
        "position_sizing": False,
        "prediction_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_EXECUTION_SCHEMA_VERSION",
    "MARKET_EXECUTION_SCHEMA",
    "MarketExecution",
    "market_execution_health",
]