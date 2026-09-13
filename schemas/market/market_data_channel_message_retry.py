"""
ROBOMLM PLUS
Market Data Channel Message Retry Schema

Purpose:
    Represents retry information for a market-data channel message.

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


MARKET_DATA_CHANNEL_MESSAGE_RETRY_VERSION = "1.0.0"
MARKET_DATA_CHANNEL_MESSAGE_RETRY_SCHEMA = (
    "MARKET_DATA_CHANNEL_MESSAGE_RETRY"
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class MarketDataChannelMessageRetry:
    """
    Immutable retry state for a market-data channel message.
    """

    retry_id: str
    message_id: str
    channel_id: str

    attempt_number: int = 1
    max_attempts: int = 3

    retryable: bool = True
    exhausted: bool = False

    timestamp: Optional[datetime] = None
    next_retry_at: Optional[datetime] = None

    reason: Optional[str] = None
    error_code: Optional[str] = None

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.retry_id:
            raise ValueError("retry_id is required.")

        if not self.message_id:
            raise ValueError("message_id is required.")

        if not self.channel_id:
            raise ValueError("channel_id is required.")

        if self.attempt_number < 1:
            raise ValueError("attempt_number must be at least 1.")

        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1.")

        if self.attempt_number > self.max_attempts:
            object.__setattr__(self, "exhausted", True)

        if self.timestamp is None:
            object.__setattr__(self, "timestamp", _utc_now())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def attempts_remaining(self) -> int:
        return max(
            0,
            self.max_attempts - self.attempt_number,
        )

    def can_retry(self) -> bool:
        return (
            self.retryable
            and not self.exhausted
            and self.attempt_number < self.max_attempts
        )

    def is_exhausted(self) -> bool:
        return (
            self.exhausted
            or self.attempt_number >= self.max_attempts
        )


def create_market_data_channel_message_retry(
    retry_id: str,
    message_id: str,
    channel_id: str,
    *,
    attempt_number: int = 1,
    max_attempts: int = 3,
    retryable: bool = True,
    exhausted: bool = False,
    timestamp: Optional[datetime] = None,
    next_retry_at: Optional[datetime] = None,
    reason: Optional[str] = None,
    error_code: Optional[str] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> MarketDataChannelMessageRetry:
    """
    Factory for creating a channel-message retry record.
    """

    return MarketDataChannelMessageRetry(
        retry_id=retry_id,
        message_id=message_id,
        channel_id=channel_id,
        attempt_number=attempt_number,
        max_attempts=max_attempts,
        retryable=retryable,
        exhausted=exhausted,
        timestamp=timestamp,
        next_retry_at=next_retry_at,
        reason=reason,
        error_code=error_code,
        metadata=dict(metadata or {}),
    )


def market_data_channel_message_retry_health() -> dict[str, Any]:
    """
    Return schema health information.
    """

    return {
        "schema": MARKET_DATA_CHANNEL_MESSAGE_RETRY_SCHEMA,
        "version": MARKET_DATA_CHANNEL_MESSAGE_RETRY_VERSION,
        "status": "ready",
        "immutable": True,
        "attempt_tracking_supported": True,
        "retry_exhaustion_supported": True,
        "decision_logic": False,
        "execution_logic": False,
        "broker_dependency": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_DATA_CHANNEL_MESSAGE_RETRY_VERSION",
    "MARKET_DATA_CHANNEL_MESSAGE_RETRY_SCHEMA",
    "MarketDataChannelMessageRetry",
    "create_market_data_channel_message_retry",
    "market_data_channel_message_retry_health",
]