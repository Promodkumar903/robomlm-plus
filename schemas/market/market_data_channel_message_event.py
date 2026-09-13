"""
ROBOMLM PLUS
Market Data Channel Message Event Schema

Purpose:
    Represents an operational event associated with a message
    transported through a market-data channel.

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


MARKET_DATA_CHANNEL_MESSAGE_EVENT_VERSION = "1.0.0"
MARKET_DATA_CHANNEL_MESSAGE_EVENT_SCHEMA = (
    "MARKET_DATA_CHANNEL_MESSAGE_EVENT"
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class MarketDataChannelMessageEvent:
    """
    Immutable event associated with a market-data channel message.
    """

    event_id: str
    message_id: str
    channel_id: str
    event_type: str

    timestamp: Optional[datetime] = None

    status: Optional[str] = None
    source: Optional[str] = None

    message: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.event_id:
            raise ValueError("event_id is required.")

        if not self.message_id:
            raise ValueError("message_id is required.")

        if not self.channel_id:
            raise ValueError("channel_id is required.")

        if not self.event_type:
            raise ValueError("event_type is required.")

        if self.timestamp is None:
            object.__setattr__(self, "timestamp", _utc_now())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def is_error(self) -> bool:
        """
        Return True when the event represents an error condition.
        """

        if self.error_code or self.error_message:
            return True

        return str(self.status or "").upper() in {
            "ERROR",
            "FAILED",
            "FAILURE",
            "REJECTED",
        }

    def is_success(self) -> bool:
        """
        Return True when the event represents a successful condition.
        """

        return str(self.status or "").upper() in {
            "SUCCESS",
            "OK",
            "RECEIVED",
            "PROCESSED",
            "ACKNOWLEDGED",
        }


def create_market_data_channel_message_event(
    event_id: str,
    message_id: str,
    channel_id: str,
    event_type: str,
    *,
    timestamp: Optional[datetime] = None,
    status: Optional[str] = None,
    source: Optional[str] = None,
    message: Optional[str] = None,
    error_code: Optional[str] = None,
    error_message: Optional[str] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> MarketDataChannelMessageEvent:
    """
    Factory for creating a market-data channel message event.
    """

    return MarketDataChannelMessageEvent(
        event_id=event_id,
        message_id=message_id,
        channel_id=channel_id,
        event_type=event_type,
        timestamp=timestamp,
        status=status,
        source=source,
        message=message,
        error_code=error_code,
        error_message=error_message,
        metadata=dict(metadata or {}),
    )


def market_data_channel_message_event_health() -> dict[str, Any]:
    """
    Return schema health information.
    """

    return {
        "schema": MARKET_DATA_CHANNEL_MESSAGE_EVENT_SCHEMA,
        "version": MARKET_DATA_CHANNEL_MESSAGE_EVENT_VERSION,
        "status": "ready",
        "immutable": True,
        "error_classification_supported": True,
        "decision_logic": False,
        "execution_logic": False,
        "broker_dependency": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_DATA_CHANNEL_MESSAGE_EVENT_VERSION",
    "MARKET_DATA_CHANNEL_MESSAGE_EVENT_SCHEMA",
    "MarketDataChannelMessageEvent",
    "create_market_data_channel_message_event",
    "market_data_channel_message_event_health",
]