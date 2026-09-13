"""
ROBOMLM PLUS
Market Data Channel Message Schema

Purpose:
    Represents a message transported through a market-data channel.

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
from datetime import datetime, timezone
from typing import Any, Mapping, Optional


MARKET_DATA_CHANNEL_MESSAGE_VERSION = "1.0.0"
MARKET_DATA_CHANNEL_MESSAGE_SCHEMA = "MARKET_DATA_CHANNEL_MESSAGE"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class MarketDataChannelMessage:
    """
    Immutable market-data channel message.
    """

    message_id: str
    channel_id: str
    message_type: str

    timestamp: Optional[datetime] = None

    sequence: Optional[int] = None

    symbol: Optional[str] = None
    market: Optional[str] = None
    exchange: Optional[str] = None
    instrument: Optional[str] = None
    venue: Optional[str] = None

    payload: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.message_id:
            raise ValueError("message_id is required.")

        if not self.channel_id:
            raise ValueError("channel_id is required.")

        if not self.message_type:
            raise ValueError("message_type is required.")

        if self.sequence is not None and self.sequence < 0:
            raise ValueError("sequence cannot be negative.")

        if self.timestamp is None:
            object.__setattr__(self, "timestamp", _utc_now())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def has_payload(self) -> bool:
        return bool(self.payload)

    def has_sequence(self) -> bool:
        return self.sequence is not None


def create_market_data_channel_message(
    message_id: str,
    channel_id: str,
    message_type: str,
    *,
    timestamp: Optional[datetime] = None,
    sequence: Optional[int] = None,
    symbol: Optional[str] = None,
    market: Optional[str] = None,
    exchange: Optional[str] = None,
    instrument: Optional[str] = None,
    venue: Optional[str] = None,
    payload: Optional[Mapping[str, Any]] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> MarketDataChannelMessage:
    """
    Factory for creating a market-data channel message.
    """

    return MarketDataChannelMessage(
        message_id=message_id,
        channel_id=channel_id,
        message_type=message_type,
        timestamp=timestamp,
        sequence=sequence,
        symbol=symbol,
        market=market,
        exchange=exchange,
        instrument=instrument,
        venue=venue,
        payload=dict(payload or {}),
        metadata=dict(metadata or {}),
    )


def market_data_channel_message_health() -> dict[str, Any]:
    """
    Return schema health information.
    """

    return {
        "schema": MARKET_DATA_CHANNEL_MESSAGE_SCHEMA,
        "version": MARKET_DATA_CHANNEL_MESSAGE_VERSION,
        "status": "ready",
        "immutable": True,
        "sequence_supported": True,
        "payload_supported": True,
        "decision_logic": False,
        "execution_logic": False,
        "broker_dependency": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_DATA_CHANNEL_MESSAGE_VERSION",
    "MARKET_DATA_CHANNEL_MESSAGE_SCHEMA",
    "MarketDataChannelMessage",
    "create_market_data_channel_message",
    "market_data_channel_message_health",
]