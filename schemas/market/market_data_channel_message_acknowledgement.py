"""
ROBOMLM PLUS
Market Data Channel Message Acknowledgement Schema

Purpose:
    Represents acknowledgement information for a message transported
    through a market-data channel.

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


MARKET_DATA_CHANNEL_MESSAGE_ACKNOWLEDGEMENT_VERSION = "1.0.0"
MARKET_DATA_CHANNEL_MESSAGE_ACKNOWLEDGEMENT_SCHEMA = (
    "MARKET_DATA_CHANNEL_MESSAGE_ACKNOWLEDGEMENT"
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class MarketDataChannelMessageAcknowledgement:
    """
    Immutable acknowledgement record for a channel message.
    """

    acknowledgement_id: str
    message_id: str
    channel_id: str

    acknowledged: bool = False
    status: str = "PENDING"

    timestamp: Optional[datetime] = None

    source: Optional[str] = None
    destination: Optional[str] = None

    error_code: Optional[str] = None
    error_message: Optional[str] = None

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.acknowledgement_id:
            raise ValueError("acknowledgement_id is required.")

        if not self.message_id:
            raise ValueError("message_id is required.")

        if not self.channel_id:
            raise ValueError("channel_id is required.")

        if self.timestamp is None:
            object.__setattr__(self, "timestamp", _utc_now())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def is_successful(self) -> bool:
        """
        Return True when the message was successfully acknowledged.
        """

        return self.acknowledged and str(self.status).upper() in {
            "ACKNOWLEDGED",
            "SUCCESS",
            "OK",
        }

    def is_failed(self) -> bool:
        """
        Return True when acknowledgement failed or was rejected.
        """

        return str(self.status).upper() in {
            "FAILED",
            "ERROR",
            "REJECTED",
            "EXPIRED",
        }

    def is_pending(self) -> bool:
        """
        Return True when acknowledgement is still pending.
        """

        return str(self.status).upper() == "PENDING"


def create_market_data_channel_message_acknowledgement(
    acknowledgement_id: str,
    message_id: str,
    channel_id: str,
    *,
    acknowledged: bool = False,
    status: str = "PENDING",
    timestamp: Optional[datetime] = None,
    source: Optional[str] = None,
    destination: Optional[str] = None,
    error_code: Optional[str] = None,
    error_message: Optional[str] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> MarketDataChannelMessageAcknowledgement:
    """
    Factory for creating a channel-message acknowledgement.
    """

    return MarketDataChannelMessageAcknowledgement(
        acknowledgement_id=acknowledgement_id,
        message_id=message_id,
        channel_id=channel_id,
        acknowledged=acknowledged,
        status=status,
        timestamp=timestamp,
        source=source,
        destination=destination,
        error_code=error_code,
        error_message=error_message,
        metadata=dict(metadata or {}),
    )


def market_data_channel_message_acknowledgement_health() -> dict[str, Any]:
    """
    Return schema health information.
    """

    return {
        "schema": MARKET_DATA_CHANNEL_MESSAGE_ACKNOWLEDGEMENT_SCHEMA,
        "version": MARKET_DATA_CHANNEL_MESSAGE_ACKNOWLEDGEMENT_VERSION,
        "status": "ready",
        "immutable": True,
        "message_identity_supported": True,
        "channel_identity_supported": True,
        "decision_logic": False,
        "execution_logic": False,
        "broker_dependency": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_DATA_CHANNEL_MESSAGE_ACKNOWLEDGEMENT_VERSION",
    "MARKET_DATA_CHANNEL_MESSAGE_ACKNOWLEDGEMENT_SCHEMA",
    "MarketDataChannelMessageAcknowledgement",
    "create_market_data_channel_message_acknowledgement",
    "market_data_channel_message_acknowledgement_health",
]