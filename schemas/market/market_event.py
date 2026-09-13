"""
ROBOMLM PLUS
V6 Market Event Schema

Purpose:
    Structural representation of a market event and its provenance.

Rules:
    - Event representation only.
    - Preserves observed event information.
    - No trading decisions.
    - No execution logic.
    - No intelligence generation.
    - No V7+ dependency.
    - Does not mutate source data.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Optional


MARKET_EVENT_SCHEMA_VERSION = "1.0.0"
MARKET_EVENT_SCHEMA = "V6_MARKET_EVENT"


@dataclass(frozen=True)
class MarketEvent:
    """
    Immutable representation of a market event.

    The event keeps identity, timing, event classification, observed
    values, provenance, and metadata structurally separated.
    """

    # ------------------------------------------------------------------
    # Event Identity
    # ------------------------------------------------------------------

    event_id: Optional[str] = None
    event_type: Optional[str] = None
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
    # Event Timing
    # ------------------------------------------------------------------

    timestamp: Optional[str] = None
    session_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Observed Event Values
    # ------------------------------------------------------------------

    price: Optional[float] = None
    volume: Optional[float] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    side: Optional[str] = None

    # ------------------------------------------------------------------
    # Provenance
    # ------------------------------------------------------------------

    source: Optional[str] = None
    source_type: Optional[str] = None

    # ------------------------------------------------------------------
    # Additional Metadata
    # ------------------------------------------------------------------

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate structural market-event information."""

        if self.sequence is not None:
            if isinstance(self.sequence, bool):
                raise TypeError(
                    "MarketEvent.sequence must be an integer or None."
                )

            if not isinstance(self.sequence, int):
                raise TypeError(
                    "MarketEvent.sequence must be an integer or None."
                )

            if self.sequence < 0:
                raise ValueError(
                    "MarketEvent.sequence cannot be negative."
                )

        numeric_fields = {
            "price": self.price,
            "volume": self.volume,
            "bid": self.bid,
            "ask": self.ask,
        }

        for field_name, value in numeric_fields.items():
            if value is None:
                continue

            if isinstance(value, bool):
                raise TypeError(
                    f"MarketEvent.{field_name} must be numeric or None."
                )

            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"MarketEvent.{field_name} must be numeric or None."
                )

        if self.volume is not None and self.volume < 0:
            raise ValueError(
                "MarketEvent.volume cannot be negative."
            )

        if self.metadata is None:
            raise TypeError(
                "MarketEvent.metadata must be a mapping."
            )

        if not isinstance(self.metadata, Mapping):
            raise TypeError(
                "MarketEvent.metadata must be a mapping."
            )

    # ------------------------------------------------------------------
    # Structural Checks
    # ------------------------------------------------------------------

    def has_identity(self) -> bool:
        """
        Return True when a market/instrument identifier exists.
        """

        return bool(
            self.market
            or self.instrument
            or self.symbol
        )

    def has_event_identity(self) -> bool:
        """
        Return True when an event identifier or event type exists.
        """

        return bool(
            self.event_id
            or self.event_type
        )

    def has_observed_data(self) -> bool:
        """
        Return True when at least one primary observed value exists.
        """

        return any(
            value is not None
            for value in (
                self.price,
                self.volume,
                self.bid,
                self.ask,
                self.side,
            )
        )

    def spread(self) -> Optional[float]:
        """
        Return the observed bid/ask spread when both are available.
        """

        if self.bid is None or self.ask is None:
            return None

        return self.ask - self.bid

    def issue_flags(self) -> tuple[str, ...]:
        """
        Return structural event issues.

        This method does not interpret the event as a trading signal.
        """

        issues: list[str] = []

        if not self.has_event_identity():
            issues.append("MISSING_EVENT_IDENTITY")

        if not self.has_identity():
            issues.append("MISSING_MARKET_IDENTITY")

        if not self.timestamp:
            issues.append("MISSING_TIMESTAMP")

        if not self.has_observed_data():
            issues.append("MISSING_OBSERVED_DATA")

        if (
            self.bid is not None
            and self.ask is not None
            and self.ask < self.bid
        ):
            issues.append("INVALID_BID_ASK_RELATION")

        return tuple(issues)

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the market event into a JSON-safe mapping.
        """

        data = asdict(self)
        data["metadata"] = dict(self.metadata)

        return data

    @staticmethod
    def schema_info() -> dict[str, str]:
        """Return schema identity and version."""

        return {
            "schema": MARKET_EVENT_SCHEMA,
            "version": MARKET_EVENT_SCHEMA_VERSION,
        }


def market_event_health() -> dict[str, Any]:
    """
    Return structural health information for the V6 event schema.
    """

    return {
        "schema": MARKET_EVENT_SCHEMA,
        "version": MARKET_EVENT_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "event_identity_supported": True,
        "market_identity_supported": True,
        "observed_data_supported": True,
        "provenance_supported": True,
        "decision_logic": False,
        "execution_logic": False,
        "intelligence_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_EVENT_SCHEMA_VERSION",
    "MARKET_EVENT_SCHEMA",
    "MarketEvent",
    "market_event_health",
]