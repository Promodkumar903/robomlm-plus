"""
ROBOMLM PLUS
V6 Market Liquidity Schema

Purpose:
    Structural representation of observed and derived market liquidity
    information.

Rules:
    - Liquidity representation only.
    - No trading decision.
    - No execution logic.
    - No order generation.
    - No prediction.
    - No V7+ dependency.
    - Observed and derived information remain distinguishable.
    - Does not mutate source data.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Optional


MARKET_LIQUIDITY_SCHEMA_VERSION = "1.0.0"
MARKET_LIQUIDITY_SCHEMA = "V6_MARKET_LIQUIDITY"


@dataclass(frozen=True)
class MarketLiquidity:
    """
    Immutable structural representation of market liquidity.

    The schema describes liquidity conditions and measurements.
    It does not determine whether a trade should be taken.
    """

    # ------------------------------------------------------------------
    # Liquidity Identity
    # ------------------------------------------------------------------

    liquidity_id: Optional[str] = None
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

    # ------------------------------------------------------------------
    # Primary Observed Liquidity Values
    # ------------------------------------------------------------------

    bid: Optional[float] = None
    ask: Optional[float] = None
    bid_size: Optional[float] = None
    ask_size: Optional[float] = None

    # ------------------------------------------------------------------
    # Derived Structural Liquidity Values
    # ------------------------------------------------------------------

    spread: Optional[float] = None
    mid_price: Optional[float] = None
    depth: Optional[float] = None
    imbalance: Optional[float] = None

    # ------------------------------------------------------------------
    # Liquidity Classification
    # ------------------------------------------------------------------

    liquidity_state: Optional[str] = None
    liquidity_level: Optional[str] = None
    depth_state: Optional[str] = None
    spread_state: Optional[str] = None
    participation_state: Optional[str] = None

    # ------------------------------------------------------------------
    # Liquidity Metrics
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
    # Additional Metadata
    # ------------------------------------------------------------------

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate structural liquidity information."""

        if self.sequence is not None:
            if isinstance(self.sequence, bool):
                raise TypeError(
                    "MarketLiquidity.sequence must be an integer or None."
                )

            if not isinstance(self.sequence, int):
                raise TypeError(
                    "MarketLiquidity.sequence must be an integer or None."
                )

            if self.sequence < 0:
                raise ValueError(
                    "MarketLiquidity.sequence cannot be negative."
                )

        numeric_fields = {
            "bid": self.bid,
            "ask": self.ask,
            "bid_size": self.bid_size,
            "ask_size": self.ask_size,
            "spread": self.spread,
            "mid_price": self.mid_price,
            "depth": self.depth,
            "imbalance": self.imbalance,
            "liquidity_score": self.liquidity_score,
            "confidence": self.confidence,
        }

        for field_name, value in numeric_fields.items():
            if value is None:
                continue

            if isinstance(value, bool):
                raise TypeError(
                    f"MarketLiquidity.{field_name} must be numeric or None."
                )

            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"MarketLiquidity.{field_name} "
                    "must be numeric or None."
                )

        for field_name in (
            "bid_size",
            "ask_size",
            "spread",
            "depth",
        ):
            value = getattr(self, field_name)

            if value is not None and value < 0:
                raise ValueError(
                    f"MarketLiquidity.{field_name} cannot be negative."
                )

        if self.imbalance is not None:
            if not -1 <= self.imbalance <= 1:
                raise ValueError(
                    "MarketLiquidity.imbalance must be between -1 and 1."
                )

        for field_name in (
            "liquidity_score",
            "confidence",
        ):
            value = getattr(self, field_name)

            if value is not None and not 0 <= value <= 100:
                raise ValueError(
                    f"MarketLiquidity.{field_name} "
                    "must be between 0 and 100."
                )

        if self.metadata is None:
            raise TypeError(
                "MarketLiquidity.metadata must be a mapping."
            )

        if not isinstance(self.metadata, Mapping):
            raise TypeError(
                "MarketLiquidity.metadata must be a mapping."
            )

        if isinstance(self.observed_fields, str):
            raise TypeError(
                "MarketLiquidity.observed_fields "
                "must be a sequence of names."
            )

        if isinstance(self.derived_fields, str):
            raise TypeError(
                "MarketLiquidity.derived_fields "
                "must be a sequence of names."
            )

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    def has_identity(self) -> bool:
        """Return True when sufficient market identity exists."""

        return bool(
            self.market
            or self.instrument
            or self.symbol
        )

    def has_liquidity_identity(self) -> bool:
        """Return True when liquidity ID or timestamp exists."""

        return bool(
            self.liquidity_id
            or self.timestamp
        )

    # ------------------------------------------------------------------
    # Order Book Availability
    # ------------------------------------------------------------------

    def has_bid(self) -> bool:
        """Return True when bid price is available."""

        return self.bid is not None

    def has_ask(self) -> bool:
        """Return True when ask price is available."""

        return self.ask is not None

    def has_bid_ask(self) -> bool:
        """Return True when both bid and ask are available."""

        return (
            self.bid is not None
            and self.ask is not None
        )

    def has_bid_size(self) -> bool:
        """Return True when bid size is available."""

        return self.bid_size is not None

    def has_ask_size(self) -> bool:
        """Return True when ask size is available."""

        return self.ask_size is not None

    def has_depth(self) -> bool:
        """Return True when depth information is available."""

        return self.depth is not None

    # ------------------------------------------------------------------
    # Structural Metrics
    # ------------------------------------------------------------------

    def calculate_mid_price(self) -> Optional[float]:
        """
        Calculate mid price from observed bid and ask.

        This is a structural calculation only.
        """

        if self.bid is None or self.ask is None:
            return None

        return (self.bid + self.ask) / 2.0

    def calculate_spread(self) -> Optional[float]:
        """
        Calculate spread from observed bid and ask.

        This is a structural calculation only.
        """

        if self.bid is None or self.ask is None:
            return None

        return self.ask - self.bid

    def calculate_imbalance(self) -> Optional[float]:
        """
        Calculate bid/ask size imbalance.

        Formula:
            (bid_size - ask_size) / (bid_size + ask_size)

        Returns None when the required sizes are unavailable.
        """

        if self.bid_size is None or self.ask_size is None:
            return None

        total_size = self.bid_size + self.ask_size

        if total_size == 0:
            return None

        return (
            (self.bid_size - self.ask_size)
            / total_size
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
        Return structural liquidity issues.

        Validation only. No trading decision is produced.
        """

        issues: list[str] = []

        if not self.has_identity():
            issues.append("MISSING_MARKET_IDENTITY")

        if not self.timestamp:
            issues.append("MISSING_TIMESTAMP")

        if not self.source:
            issues.append("MISSING_SOURCE")

        if not self.has_bid_ask():
            issues.append("INCOMPLETE_BID_ASK")

        if (
            self.bid is not None
            and self.ask is not None
            and self.ask < self.bid
        ):
            issues.append("INVALID_BID_ASK_RELATION")

        if (
            self.bid_size is not None
            and self.ask_size is not None
            and self.bid_size < 0
        ):
            issues.append("INVALID_BID_SIZE")

        if (
            self.bid_size is not None
            and self.ask_size is not None
            and self.ask_size < 0
        ):
            issues.append("INVALID_ASK_SIZE")

        if (
            self.depth is not None
            and self.depth < 0
        ):
            issues.append("INVALID_DEPTH")

        if not self.has_source_reference():
            issues.append("MISSING_SOURCE_REFERENCE")

        if (
            self.derived_fields
            and not self.has_source_reference()
        ):
            issues.append(
                "DERIVED_LIQUIDITY_WITHOUT_SOURCE_REFERENCE"
            )

        return tuple(issues)

    def is_structurally_valid(self) -> bool:
        """Return True when no structural issues are present."""

        return not self.issue_flags()

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize liquidity information into a JSON-safe mapping."""

        data = asdict(self)

        data["observed_fields"] = list(self.observed_fields)
        data["derived_fields"] = list(self.derived_fields)
        data["metadata"] = dict(self.metadata)

        return data

    @staticmethod
    def schema_info() -> dict[str, str]:
        """Return schema identity and version."""

        return {
            "schema": MARKET_LIQUIDITY_SCHEMA,
            "version": MARKET_LIQUIDITY_SCHEMA_VERSION,
        }


def market_liquidity_health() -> dict[str, Any]:
    """Return structural health information for the V6 liquidity schema."""

    return {
        "schema": MARKET_LIQUIDITY_SCHEMA,
        "version": MARKET_LIQUIDITY_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "market_identity_supported": True,
        "bid_ask_supported": True,
        "bid_size_supported": True,
        "ask_size_supported": True,
        "spread_supported": True,
        "mid_price_supported": True,
        "depth_supported": True,
        "imbalance_supported": True,
        "liquidity_state_supported": True,
        "liquidity_level_supported": True,
        "depth_state_supported": True,
        "spread_state_supported": True,
        "participation_state_supported": True,
        "provenance_supported": True,
        "source_reference_supported": True,
        "observed_derived_separation": True,
        "decision_logic": False,
        "execution_logic": False,
        "order_generation": False,
        "prediction_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_LIQUIDITY_SCHEMA_VERSION",
    "MARKET_LIQUIDITY_SCHEMA",
    "MarketLiquidity",
    "market_liquidity_health",
]