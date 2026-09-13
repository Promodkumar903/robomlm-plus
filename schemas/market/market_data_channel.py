"""
ROBOMLM PLUS
Market Data Channel Schema

Purpose:
    Represents the logical channel through which market data is
    transported or received.

Rules:
    - Schema only.
    - No trading intelligence.
    - No decision logic.
    - No execution logic.
    - No broker-specific behavior.
    - No V7+ dependency.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Optional


MARKET_DATA_CHANNEL_VERSION = "1.0.0"
MARKET_DATA_CHANNEL_SCHEMA = "MARKET_DATA_CHANNEL"


@dataclass(frozen=True)
class MarketDataChannel:
    """
    Immutable logical market-data channel definition.
    """

    channel_id: str

    name: Optional[str] = None
    channel_type: Optional[str] = None

    source: Optional[str] = None
    market: Optional[str] = None
    exchange: Optional[str] = None
    venue: Optional[str] = None

    data_type: Optional[str] = None
    protocol: Optional[str] = None

    active: bool = True

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.channel_id:
            raise ValueError("channel_id is required.")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def is_active(self) -> bool:
        return self.active

    def matches(
        self,
        *,
        channel_type: Optional[str] = None,
        source: Optional[str] = None,
        market: Optional[str] = None,
        exchange: Optional[str] = None,
        venue: Optional[str] = None,
        data_type: Optional[str] = None,
        protocol: Optional[str] = None,
    ) -> bool:
        """
        Check whether supplied channel criteria match this channel.

        None criteria are treated as wildcards.
        """

        checks = (
            (self.channel_type, channel_type),
            (self.source, source),
            (self.market, market),
            (self.exchange, exchange),
            (self.venue, venue),
            (self.data_type, data_type),
            (self.protocol, protocol),
        )

        for current, requested in checks:
            if requested is None:
                continue

            if current is None:
                return False

            if str(current).upper() != str(requested).upper():
                return False

        return True


def create_market_data_channel(
    channel_id: str,
    *,
    name: Optional[str] = None,
    channel_type: Optional[str] = None,
    source: Optional[str] = None,
    market: Optional[str] = None,
    exchange: Optional[str] = None,
    venue: Optional[str] = None,
    data_type: Optional[str] = None,
    protocol: Optional[str] = None,
    active: bool = True,
    metadata: Optional[Mapping[str, Any]] = None,
) -> MarketDataChannel:
    """
    Factory for creating a market-data channel.
    """

    return MarketDataChannel(
        channel_id=channel_id,
        name=name,
        channel_type=channel_type,
        source=source,
        market=market,
        exchange=exchange,
        venue=venue,
        data_type=data_type,
        protocol=protocol,
        active=active,
        metadata=dict(metadata or {}),
    )


def market_data_channel_health() -> dict[str, Any]:
    """
    Return schema health information.
    """

    return {
        "schema": MARKET_DATA_CHANNEL_SCHEMA,
        "version": MARKET_DATA_CHANNEL_VERSION,
        "status": "ready",
        "immutable": True,
        "matching_supported": True,
        "decision_logic": False,
        "execution_logic": False,
        "broker_dependency": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_DATA_CHANNEL_VERSION",
    "MARKET_DATA_CHANNEL_SCHEMA",
    "MarketDataChannel",
    "create_market_data_channel",
    "market_data_channel_health",
]