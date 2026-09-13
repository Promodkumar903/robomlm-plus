"""
ROBOMLM PLUS
Market Data Channel Message Error Schema

Purpose:
    Represents an error associated with a market-data channel message.

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


MARKET_DATA_CHANNEL_MESSAGE_ERROR_VERSION = "1.0.0"
MARKET_DATA_CHANNEL_MESSAGE_ERROR_SCHEMA = (
    "MARKET_DATA_CHANNEL_MESSAGE_ERROR"
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class MarketDataChannelMessageError:
    """
    Immutable error record associated with a channel message.
    """

    error_id: str
    message_id: str
    channel_id: str

    error_code: str
    error_message: str

    timestamp: Optional[datetime] = None

    severity: Optional[str] = None
    source: Optional[str] = None

    retryable: bool = False
    resolved: bool = False

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.error_id:
            raise ValueError("error_id is required.")

        if not self.message_id:
            raise ValueError("message_id is required.")

        if not self.channel_id:
            raise ValueError("channel_id is required.")

        if not self.error_code:
            raise ValueError("error_code is required.")

        if not self.error_message:
            raise ValueError("error_message is required.")

        if self.timestamp is None:
            object.__setattr__(self, "timestamp", _utc_now())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def is_retryable(self) -> bool:
        return self.retryable

    def is_resolved(self) -> bool:
        return self.resolved

    def is_unresolved(self) -> bool:
        return not self.resolved


def create_market_data_channel_message_error(
    error_id: str,
    message_id: str,
    channel_id: str,
    error_code: str,
    error_message: str,
    *,
    timestamp: Optional[datetime] = None,
    severity: Optional[str] = None,
    source: Optional[str] = None,
    retryable: bool = False,
    resolved: bool = False,
    metadata: Optional[Mapping[str, Any]] = None,
) -> MarketDataChannelMessageError:
    """
    Factory for creating a channel-message error record.
    """

    return MarketDataChannelMessageError(
        error_id=error_id,
        message_id=message_id,
        channel_id=channel_id,
        error_code=error_code,
        error_message=error_message,
        timestamp=timestamp,
        severity=severity,
        source=source,
        retryable=retryable,
        resolved=resolved,
        metadata=dict(metadata or {}),
    )


def market_data_channel_message_error_health() -> dict[str, Any]:
    """
    Return schema health information.
    """

    return {
        "schema": MARKET_DATA_CHANNEL_MESSAGE_ERROR_SCHEMA,
        "version": MARKET_DATA_CHANNEL_MESSAGE_ERROR_VERSION,
        "status": "ready",
        "immutable": True,
        "error_identity_supported": True,
        "retryability_supported": True,
        "resolution_state_supported": True,
        "decision_logic": False,
        "execution_logic": False,
        "broker_dependency": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_DATA_CHANNEL_MESSAGE_ERROR_VERSION",
    "MARKET_DATA_CHANNEL_MESSAGE_ERROR_SCHEMA",
    "MarketDataChannelMessageError",
    "create_market_data_channel_message_error",
    "market_data_channel_message_error_health",
]