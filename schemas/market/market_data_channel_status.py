"""
ROBOMLM PLUS
Market Data Channel Status Schema

Purpose:
    Defines the lifecycle status of a market-data channel.

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


MARKET_DATA_CHANNEL_STATUS_VERSION = "1.0.0"
MARKET_DATA_CHANNEL_STATUS_SCHEMA = "MARKET_DATA_CHANNEL_STATUS"


class MarketDataChannelStatus(str, Enum):
    """
    Lifecycle states for a market-data channel.
    """

    INITIALIZING = "INITIALIZING"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DEGRADED = "DEGRADED"
    DISCONNECTED = "DISCONNECTED"
    CLOSED = "CLOSED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


def normalize_channel_status(
    status: MarketDataChannelStatus | str | None,
) -> MarketDataChannelStatus:
    """
    Convert a raw status value into the canonical enum.

    Unknown or invalid values resolve to UNKNOWN.
    """

    if status is None:
        return MarketDataChannelStatus.UNKNOWN

    if isinstance(status, MarketDataChannelStatus):
        return status

    try:
        return MarketDataChannelStatus(
            str(status).strip().upper()
        )
    except ValueError:
        return MarketDataChannelStatus.UNKNOWN


def is_active_status(
    status: MarketDataChannelStatus | str | None,
) -> bool:
    """
    Return True when the channel is actively delivering data.
    """

    return normalize_channel_status(status) == (
        MarketDataChannelStatus.ACTIVE
    )


def is_initializing_status(
    status: MarketDataChannelStatus | str | None,
) -> bool:
    """
    Return True when the channel is still initializing.
    """

    return normalize_channel_status(status) == (
        MarketDataChannelStatus.INITIALIZING
    )


def is_paused_status(
    status: MarketDataChannelStatus | str | None,
) -> bool:
    """
    Return True when the channel is temporarily paused.
    """

    return normalize_channel_status(status) == (
        MarketDataChannelStatus.PAUSED
    )


def is_degraded_status(
    status: MarketDataChannelStatus | str | None,
) -> bool:
    """
    Return True when the channel remains available but degraded.
    """

    return normalize_channel_status(status) == (
        MarketDataChannelStatus.DEGRADED
    )


def is_disconnected_status(
    status: MarketDataChannelStatus | str | None,
) -> bool:
    """
    Return True when the channel is disconnected.
    """

    return normalize_channel_status(status) == (
        MarketDataChannelStatus.DISCONNECTED
    )


def is_terminal_status(
    status: MarketDataChannelStatus | str | None,
) -> bool:
    """
    Return True when the channel has reached a terminal state.
    """

    return normalize_channel_status(status) in {
        MarketDataChannelStatus.CLOSED,
        MarketDataChannelStatus.FAILED,
    }


def is_failure_status(
    status: MarketDataChannelStatus | str | None,
) -> bool:
    """
    Return True for channel failure.
    """

    return normalize_channel_status(status) == (
        MarketDataChannelStatus.FAILED
    )


def market_data_channel_status_health() -> dict[str, object]:
    """
    Return schema health information.
    """

    return {
        "schema": MARKET_DATA_CHANNEL_STATUS_SCHEMA,
        "version": MARKET_DATA_CHANNEL_STATUS_VERSION,
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
    "MARKET_DATA_CHANNEL_STATUS_VERSION",
    "MARKET_DATA_CHANNEL_STATUS_SCHEMA",
    "MarketDataChannelStatus",
    "normalize_channel_status",
    "is_active_status",
    "is_initializing_status",
    "is_paused_status",
    "is_degraded_status",
    "is_disconnected_status",
    "is_terminal_status",
    "is_failure_status",
    "market_data_channel_status_health",
]