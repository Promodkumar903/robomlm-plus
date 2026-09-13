"""
ROBOMLM PLUS
Market Data Channel Message Status Schema

Purpose:
    Defines the lifecycle status of a message transported through
    a market-data channel.

Rules:
    - Schema only.
    - No trading intelligence.
    - No decision logic.
    - No execution logic.
    - No broker-specific behavior.
    - No V7+ dependency.
"""

from __future__ import annotations

from enum import Enum


MARKET_DATA_CHANNEL_MESSAGE_STATUS_VERSION = "1.0.0"
MARKET_DATA_CHANNEL_MESSAGE_STATUS_SCHEMA = (
    "MARKET_DATA_CHANNEL_MESSAGE_STATUS"
)


class MarketDataChannelMessageStatus(str, Enum):
    """
    Canonical lifecycle states for market-data channel messages.
    """

    CREATED = "CREATED"
    QUEUED = "QUEUED"
    SENT = "SENT"
    RECEIVED = "RECEIVED"
    PROCESSED = "PROCESSED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"
    UNKNOWN = "UNKNOWN"


def normalize_message_status(
    status: MarketDataChannelMessageStatus | str | None,
) -> MarketDataChannelMessageStatus:
    """
    Convert a raw message status into the canonical enum.

    Unknown or invalid values resolve to UNKNOWN.
    """

    if status is None:
        return MarketDataChannelMessageStatus.UNKNOWN

    if isinstance(status, MarketDataChannelMessageStatus):
        return status

    try:
        return MarketDataChannelMessageStatus(
            str(status).strip().upper()
        )
    except ValueError:
        return MarketDataChannelMessageStatus.UNKNOWN


def is_created_status(
    status: MarketDataChannelMessageStatus | str | None,
) -> bool:
    return normalize_message_status(status) == (
        MarketDataChannelMessageStatus.CREATED
    )


def is_queued_status(
    status: MarketDataChannelMessageStatus | str | None,
) -> bool:
    return normalize_message_status(status) == (
        MarketDataChannelMessageStatus.QUEUED
    )


def is_sent_status(
    status: MarketDataChannelMessageStatus | str | None,
) -> bool:
    return normalize_message_status(status) == (
        MarketDataChannelMessageStatus.SENT
    )


def is_received_status(
    status: MarketDataChannelMessageStatus | str | None,
) -> bool:
    return normalize_message_status(status) == (
        MarketDataChannelMessageStatus.RECEIVED
    )


def is_processed_status(
    status: MarketDataChannelMessageStatus | str | None,
) -> bool:
    return normalize_message_status(status) == (
        MarketDataChannelMessageStatus.PROCESSED
    )


def is_acknowledged_status(
    status: MarketDataChannelMessageStatus | str | None,
) -> bool:
    return normalize_message_status(status) == (
        MarketDataChannelMessageStatus.ACKNOWLEDGED
    )


def is_success_status(
    status: MarketDataChannelMessageStatus | str | None,
) -> bool:
    """
    Return True when the message reached a successful processing state.
    """

    return normalize_message_status(status) in {
        MarketDataChannelMessageStatus.RECEIVED,
        MarketDataChannelMessageStatus.PROCESSED,
        MarketDataChannelMessageStatus.ACKNOWLEDGED,
    }


def is_failure_status(
    status: MarketDataChannelMessageStatus | str | None,
) -> bool:
    """
    Return True for rejected, failed, or expired messages.
    """

    return normalize_message_status(status) in {
        MarketDataChannelMessageStatus.REJECTED,
        MarketDataChannelMessageStatus.FAILED,
        MarketDataChannelMessageStatus.EXPIRED,
    }


def is_terminal_status(
    status: MarketDataChannelMessageStatus | str | None,
) -> bool:
    """
    Return True when the message lifecycle has reached a terminal state.
    """

    return normalize_message_status(status) in {
        MarketDataChannelMessageStatus.ACKNOWLEDGED,
        MarketDataChannelMessageStatus.REJECTED,
        MarketDataChannelMessageStatus.FAILED,
        MarketDataChannelMessageStatus.EXPIRED,
    }


def market_data_channel_message_status_health() -> dict[str, object]:
    """
    Return schema health information.
    """

    return {
        "schema": MARKET_DATA_CHANNEL_MESSAGE_STATUS_SCHEMA,
        "version": MARKET_DATA_CHANNEL_MESSAGE_STATUS_VERSION,
        "status": "ready",
        "enum_based": True,
        "lifecycle_states_defined": True,
        "terminal_states_defined": True,
        "decision_logic": False,
        "execution_logic": False,
        "broker_dependency": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_DATA_CHANNEL_MESSAGE_STATUS_VERSION",
    "MARKET_DATA_CHANNEL_MESSAGE_STATUS_SCHEMA",
    "MarketDataChannelMessageStatus",
    "normalize_message_status",
    "is_created_status",
    "is_queued_status",
    "is_sent_status",
    "is_received_status",
    "is_processed_status",
    "is_acknowledged_status",
    "is_success_status",
    "is_failure_status",
    "is_terminal_status",
    "market_data_channel_message_status_health",
]