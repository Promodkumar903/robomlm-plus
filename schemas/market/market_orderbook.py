"""
ROBOMLM PLUS
V6 Market Order Book Schema

Purpose:
    Structural representation of observed order-book information.

Rules:
    - Order-book representation only.
    - No trading decision.
    - No execution logic.
    - No order generation.
    - No prediction.
    - No V7+ dependency.
    - Bid and ask sides remain structurally distinct.
    - Observed and derived information remain distinguishable.
    - Does not mutate source data.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Optional


MARKET_ORDERBOOK_SCHEMA_VERSION = "1.0.0"
MARKET_ORDERBOOK_SCHEMA = "V6_MARKET_ORDERBOOK"


@dataclass(frozen=True)
class MarketOrderBook:
    """
    Immutable structural representation of order-book state.

    The schema describes bid/ask prices, sizes, depth, spread and
    imbalance. It does not determine trade direction or execution.
    """

    # ------------------------------------------------------------------
    # Order Book Identity
    # ------------------------------------------------------------------

    orderbook_id: Optional[str] = None
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

    # ------------------------------------------------------------------
    # Top-of-Book
    # ------------------------------------------------------------------

    bid: Optional[float] = None
    ask: Optional[float] = None
    bid_size: Optional[float] = None
    ask_size: Optional[float] = None

    # ------------------------------------------------------------------
    # Derived Top-of-Book Measurements
    # ------------------------------------------------------------------

    mid_price: Optional[float] = None
    spread: Optional[float] = None
    spread_percent: Optional[float] = None
    imbalance: Optional[float] = None
    imbalance_percent: Optional[float] = None

    # ------------------------------------------------------------------
    # Depth Measurements
    # ------------------------------------------------------------------

    bid_depth: Optional[float] = None
    ask_depth: Optional[float] = None
    total_depth: Optional[float] = None
    depth_levels: Optional[int] = None

    # ------------------------------------------------------------------
    # Multi-Level Depth
    # ------------------------------------------------------------------

    bid_levels: tuple[Mapping[str, Any], ...] = field(
        default_factory=tuple
    )
    ask_levels: tuple[Mapping[str, Any], ...] = field(
        default_factory=tuple
    )

    # ------------------------------------------------------------------
    # Structural Classification
    # ------------------------------------------------------------------

    liquidity_state: Optional[str] = None
    depth_state: Optional[str] = None
    spread_state: Optional[str] = None
    imbalance_state: Optional[str] = None

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

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
        """Validate structural order-book information."""

        if self.sequence is not None:
            if isinstance(self.sequence, bool):
                raise TypeError(
                    "MarketOrderBook.sequence must be an integer or None."
                )

            if not isinstance(self.sequence, int):
                raise TypeError(
                    "MarketOrderBook.sequence must be an integer or None."
                )

            if self.sequence < 0:
                raise ValueError(
                    "MarketOrderBook.sequence cannot be negative."
                )

        if self.depth_levels is not None:
            if isinstance(self.depth_levels, bool):
                raise TypeError(
                    "MarketOrderBook.depth_levels must be an integer "
                    "or None."
                )

            if not isinstance(self.depth_levels, int):
                raise TypeError(
                    "MarketOrderBook.depth_levels must be an integer "
                    "or None."
                )

            if self.depth_levels < 0:
                raise ValueError(
                    "MarketOrderBook.depth_levels cannot be negative."
                )

        numeric_fields = {
            "bid": self.bid,
            "ask": self.ask,
            "bid_size": self.bid_size,
            "ask_size": self.ask_size,
            "mid_price": self.mid_price,
            "spread": self.spread,
            "spread_percent": self.spread_percent,
            "imbalance": self.imbalance,
            "imbalance_percent": self.imbalance_percent,
            "bid_depth": self.bid_depth,
            "ask_depth": self.ask_depth,
            "total_depth": self.total_depth,
            "liquidity_score": self.liquidity_score,
            "confidence": self.confidence,
        }

        for field_name, value in numeric_fields.items():
            if value is None:
                continue

            if isinstance(value, bool):
                raise TypeError(
                    f"MarketOrderBook.{field_name} "
                    "must be numeric or None."
                )

            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"MarketOrderBook.{field_name} "
                    "must be numeric or None."
                )

        non_negative_fields = (
            "bid",
            "ask",
            "bid_size",
            "ask_size",
            "mid_price",
            "spread",
            "spread_percent",
            "bid_depth",
            "ask_depth",
            "total_depth",
            "liquidity_score",
            "confidence",
        )

        for field_name in non_negative_fields:
            value = getattr(self, field_name)

            if value is not None and value < 0:
                raise ValueError(
                    f"MarketOrderBook.{field_name} cannot be negative."
                )

        if self.imbalance is not None:
            if not -1.0 <= self.imbalance <= 1.0:
                raise ValueError(
                    "MarketOrderBook.imbalance must be between "
                    "-1.0 and 1.0."
                )

        if self.imbalance_percent is not None:
            if not -100.0 <= self.imbalance_percent <= 100.0:
                raise ValueError(
                    "MarketOrderBook.imbalance_percent must be between "
                    "-100 and 100."
                )

        if self.bid_levels is None:
            raise TypeError(
                "MarketOrderBook.bid_levels must be a sequence."
            )

        if self.ask_levels is None:
            raise TypeError(
                "MarketOrderBook.ask_levels must be a sequence."
            )

        if isinstance(self.bid_levels, str):
            raise TypeError(
                "MarketOrderBook.bid_levels must be a sequence."
            )

        if isinstance(self.ask_levels, str):
            raise TypeError(
                "MarketOrderBook.ask_levels must be a sequence."
            )

        for level in self.bid_levels:
            if not isinstance(level, Mapping):
                raise TypeError(
                    "Every bid level must be a mapping."
                )

        for level in self.ask_levels:
            if not isinstance(level, Mapping):
                raise TypeError(
                    "Every ask level must be a mapping."
                )

        if self.metadata is None:
            raise TypeError(
                "MarketOrderBook.metadata must be a mapping."
            )

        if not isinstance(self.metadata, Mapping):
            raise TypeError(
                "MarketOrderBook.metadata must be a mapping."
            )

        if isinstance(self.observed_fields, str):
            raise TypeError(
                "MarketOrderBook.observed_fields "
                "must be a sequence of names."
            )

        if isinstance(self.derived_fields, str):
            raise TypeError(
                "MarketOrderBook.derived_fields "
                "must be a sequence of names."
            )

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    def has_identity(self) -> bool:
        """Return True when order-book identity is available."""

        return bool(
            self.orderbook_id
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
    # Top-of-Book
    # ------------------------------------------------------------------

    def has_bid(self) -> bool:
        """Return True when bid price exists."""

        return self.bid is not None

    def has_ask(self) -> bool:
        """Return True when ask price exists."""

        return self.ask is not None

    def has_bid_size(self) -> bool:
        """Return True when bid size exists."""

        return self.bid_size is not None

    def has_ask_size(self) -> bool:
        """Return True when ask size exists."""

        return self.ask_size is not None

    def has_top_of_book(self) -> bool:
        """Return True when both bid and ask are available."""

        return (
            self.bid is not None
            and self.ask is not None
        )

    # ------------------------------------------------------------------
    # Structural Calculations
    # ------------------------------------------------------------------

    def calculate_mid_price(self) -> Optional[float]:
        """Calculate bid/ask midpoint."""

        if not self.has_top_of_book():
            return None

        return (self.bid + self.ask) / 2.0

    def calculate_spread(self) -> Optional[float]:
        """Calculate absolute bid/ask spread."""

        if not self.has_top_of_book():
            return None

        return self.ask - self.bid

    def calculate_spread_percent(self) -> Optional[float]:
        """Calculate spread as a percentage of midpoint."""

        mid_price = self.calculate_mid_price()
        spread = self.calculate_spread()

        if mid_price is None or spread is None:
            return None

        if mid_price == 0:
            return None

        return (spread / mid_price) * 100.0

    # ------------------------------------------------------------------
    # Depth
    # ------------------------------------------------------------------

    def calculate_total_depth(self) -> Optional[float]:
        """Calculate total top-level or aggregate depth."""

        if (
            self.bid_depth is not None
            and self.ask_depth is not None
        ):
            return self.bid_depth + self.ask_depth

        if (
            self.bid_size is not None
            and self.ask_size is not None
        ):
            return self.bid_size + self.ask_size

        return None

    def has_depth(self) -> bool:
        """Return True when depth information exists."""

        return any(
            value is not None
            for value in (
                self.bid_size,
                self.ask_size,
                self.bid_depth,
                self.ask_depth,
                self.total_depth,
            )
        )

    def has_multiple_levels(self) -> bool:
        """Return True when multi-level order-book data exists."""

        return bool(
            self.bid_levels
            or self.ask_levels
        )

    # ------------------------------------------------------------------
    # Imbalance
    # ------------------------------------------------------------------

    def calculate_imbalance(self) -> Optional[float]:
        """
        Calculate normalized bid/ask size imbalance.

        Formula:
            (bid_size - ask_size) / (bid_size + ask_size)
        """

        if self.bid_size is None or self.ask_size is None:
            return None

        total = self.bid_size + self.ask_size

        if total == 0:
            return None

        return (
            (self.bid_size - self.ask_size)
            / total
        )

    def calculate_imbalance_percent(self) -> Optional[float]:
        """Calculate normalized imbalance as a percentage."""

        imbalance = self.calculate_imbalance()

        if imbalance is None:
            return None

        return imbalance * 100.0

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
        Return structural order-book issues.

        Validation only. No trading decision is produced.
        """

        issues: list[str] = []

        if not self.has_identity():
            issues.append("MISSING_ORDERBOOK_IDENTITY")

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
            self.bid_size is not None
            and self.ask_size is not None
            and self.bid_size == 0
            and self.ask_size == 0
        ):
            issues.append("ZERO_TOP_LEVEL_DEPTH")

        if (
            self.bid_depth is not None
            and self.ask_depth is not None
            and self.total_depth is not None
            and self.total_depth
            != self.bid_depth + self.ask_depth
        ):
            issues.append("DEPTH_TOTAL_MISMATCH")

        if not self.has_source_reference():
            issues.append("MISSING_SOURCE_REFERENCE")

        if (
            self.derived_fields
            and not self.has_source_reference()
        ):
            issues.append(
                "DERIVED_ORDERBOOK_DATA_WITHOUT_SOURCE_REFERENCE"
            )

        return tuple(issues)

    def is_structurally_valid(self) -> bool:
        """Return True when no structural issues exist."""

        return not self.issue_flags()

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize order-book information into a mapping."""

        data = asdict(self)

        data["bid_levels"] = [
            dict(level)
            for level in self.bid_levels
        ]

        data["ask_levels"] = [
            dict(level)
            for level in self.ask_levels
        ]

        data["observed_fields"] = list(self.observed_fields)
        data["derived_fields"] = list(self.derived_fields)
        data["metadata"] = dict(self.metadata)

        return data

    @staticmethod
    def schema_info() -> dict[str, str]:
        """Return schema identity and version."""

        return {
            "schema": MARKET_ORDERBOOK_SCHEMA,
            "version": MARKET_ORDERBOOK_SCHEMA_VERSION,
        }


def market_orderbook_health() -> dict[str, Any]:
    """Return structural health information for the order-book schema."""

    return {
        "schema": MARKET_ORDERBOOK_SCHEMA,
        "version": MARKET_ORDERBOOK_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "market_identity_supported": True,
        "top_of_book_supported": True,
        "bid_side_supported": True,
        "ask_side_supported": True,
        "multi_level_depth_supported": True,
        "spread_supported": True,
        "mid_price_supported": True,
        "imbalance_supported": True,
        "liquidity_state_supported": True,
        "depth_state_supported": True,
        "provenance_supported": True,
        "source_reference_supported": True,
        "observed_derived_separation": True,
        "bid_ask_separation": True,
        "decision_logic": False,
        "execution_logic": False,
        "order_generation": False,
        "prediction_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_ORDERBOOK_SCHEMA_VERSION",
    "MARKET_ORDERBOOK_SCHEMA",
    "MarketOrderBook",
    "market_orderbook_health",
]