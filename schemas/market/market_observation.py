"""
ROBOMLM PLUS
V6 Market Observation Schema

Purpose:
    Structural representation of a market observation.

Rules:
    - Observation representation only.
    - Clearly separates observed values from provenance.
    - No trading decisions.
    - No execution logic.
    - No intelligence generation.
    - No V7+ dependency.
    - Does not mutate source data.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Optional


MARKET_OBSERVATION_SCHEMA_VERSION = "1.0.0"
MARKET_OBSERVATION_SCHEMA = "V6_MARKET_OBSERVATION"


@dataclass(frozen=True)
class MarketObservation:
    """
    Immutable structural representation of one market observation.

    This schema records what was observed and where it came from.
    It does not interpret the observation or produce a decision.
    """

    # ------------------------------------------------------------------
    # Observation Identity
    # ------------------------------------------------------------------

    observation_id: Optional[str] = None
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
    # Primary Observed Values
    # ------------------------------------------------------------------

    price: Optional[float] = None
    volume: Optional[float] = None
    bid: Optional[float] = None
    ask: Optional[float] = None

    # ------------------------------------------------------------------
    # Optional Observed Market Fields
    # ------------------------------------------------------------------

    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    close_price: Optional[float] = None
    open_interest: Optional[float] = None

    # ------------------------------------------------------------------
    # Observation Provenance
    # ------------------------------------------------------------------

    source: Optional[str] = None
    source_type: Optional[str] = None
    data_timestamp: Optional[str] = None

    # ------------------------------------------------------------------
    # Additional Metadata
    # ------------------------------------------------------------------

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate structural observation information."""

        if self.sequence is not None:
            if isinstance(self.sequence, bool):
                raise TypeError(
                    "MarketObservation.sequence must be an integer or None."
                )

            if not isinstance(self.sequence, int):
                raise TypeError(
                    "MarketObservation.sequence must be an integer or None."
                )

            if self.sequence < 0:
                raise ValueError(
                    "MarketObservation.sequence cannot be negative."
                )

        numeric_fields = {
            "price": self.price,
            "volume": self.volume,
            "bid": self.bid,
            "ask": self.ask,
            "open_price": self.open_price,
            "high_price": self.high_price,
            "low_price": self.low_price,
            "close_price": self.close_price,
            "open_interest": self.open_interest,
        }

        for field_name, value in numeric_fields.items():
            if value is None:
                continue

            if isinstance(value, bool):
                raise TypeError(
                    f"MarketObservation.{field_name} "
                    "must be numeric or None."
                )

            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"MarketObservation.{field_name} "
                    "must be numeric or None."
                )

        for field_name in (
            "volume",
            "open_interest",
        ):
            value = getattr(self, field_name)

            if value is not None and value < 0:
                raise ValueError(
                    f"MarketObservation.{field_name} cannot be negative."
                )

        if self.metadata is None:
            raise TypeError(
                "MarketObservation.metadata must be a mapping."
            )

        if not isinstance(self.metadata, Mapping):
            raise TypeError(
                "MarketObservation.metadata must be a mapping."
            )

    # ------------------------------------------------------------------
    # Identity Checks
    # ------------------------------------------------------------------

    def has_identity(self) -> bool:
        """Return True when market/instrument identity is available."""

        return bool(
            self.market
            or self.instrument
            or self.symbol
        )

    def has_observation_identity(self) -> bool:
        """Return True when observation ID or timestamp is available."""

        return bool(
            self.observation_id
            or self.timestamp
        )

    # ------------------------------------------------------------------
    # Observed Data Checks
    # ------------------------------------------------------------------

    def has_price(self) -> bool:
        """Return True when an observed price exists."""

        return self.price is not None

    def has_volume(self) -> bool:
        """Return True when observed volume exists."""

        return self.volume is not None

    def has_order_book(self) -> bool:
        """Return True when both bid and ask are observed."""

        return (
            self.bid is not None
            and self.ask is not None
        )

    def has_ohlc(self) -> bool:
        """Return True when at least one OHLC field is observed."""

        return any(
            value is not None
            for value in (
                self.open_price,
                self.high_price,
                self.low_price,
                self.close_price,
            )
        )

    def has_derivative_data(self) -> bool:
        """Return True when observed open interest exists."""

        return self.open_interest is not None

    # ------------------------------------------------------------------
    # Structural Calculations
    # ------------------------------------------------------------------

    def spread(self) -> Optional[float]:
        """
        Return observed bid/ask spread when both values are available.

        This is a structural calculation, not an intelligence signal.
        """

        if self.bid is None or self.ask is None:
            return None

        return self.ask - self.bid

    # ------------------------------------------------------------------
    # Structural Validation
    # ------------------------------------------------------------------

    def issue_flags(self) -> tuple[str, ...]:
        """
        Return structural observation issues.

        No trading or intelligence decision is made here.
        """

        issues: list[str] = []

        if not self.has_identity():
            issues.append("MISSING_MARKET_IDENTITY")

        if not self.timestamp:
            issues.append("MISSING_TIMESTAMP")

        if not self.has_price():
            issues.append("MISSING_PRICE")

        if not self.source:
            issues.append("MISSING_SOURCE")

        if (
            self.bid is not None
            and self.ask is not None
            and self.ask < self.bid
        ):
            issues.append("INVALID_BID_ASK_RELATION")

        if (
            self.high_price is not None
            and self.low_price is not None
            and self.high_price < self.low_price
        ):
            issues.append("INVALID_HIGH_LOW_RELATION")

        return tuple(issues)

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize observation into a JSON-safe mapping."""

        data = asdict(self)
        data["metadata"] = dict(self.metadata)

        return data

    @staticmethod
    def schema_info() -> dict[str, str]:
        """Return schema identity and version."""

        return {
            "schema": MARKET_OBSERVATION_SCHEMA,
            "version": MARKET_OBSERVATION_SCHEMA_VERSION,
        }


def market_observation_health() -> dict[str, Any]:
    """Return structural health information for the V6 observation schema."""

    return {
        "schema": MARKET_OBSERVATION_SCHEMA,
        "version": MARKET_OBSERVATION_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "market_identity_supported": True,
        "price_supported": True,
        "volume_supported": True,
        "order_book_supported": True,
        "ohlc_supported": True,
        "derivative_data_supported": True,
        "provenance_supported": True,
        "decision_logic": False,
        "execution_logic": False,
        "intelligence_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_OBSERVATION_SCHEMA_VERSION",
    "MARKET_OBSERVATION_SCHEMA",
    "MarketObservation",
    "market_observation_health",
]