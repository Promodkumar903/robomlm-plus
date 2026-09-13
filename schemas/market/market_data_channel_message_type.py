"""
ROBOMLM PLUS
Market Data Channel Message Type Schema

Purpose:
    Defines canonical message types transported through market-data
    channels.

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


MARKET_DATA_CHANNEL_MESSAGE_TYPE_VERSION = "1.0.0"
MARKET_DATA_CHANNEL_MESSAGE_TYPE_SCHEMA = (
    "MARKET_DATA_CHANNEL_MESSAGE_TYPE"
)


class MarketDataChannelMessageType(str, Enum):
    """
    Canonical market-data channel message categories.
    """

    SNAPSHOT = "SNAPSHOT"
    UPDATE = "UPDATE"
    QUOTE = "QUOTE"
    TRADE = "TRADE"
    ORDERBOOK = "ORDERBOOK"
    DEPTH = "DEPTH"
    CANDLE = "CANDLE"
    TICK = "TICK"
    REFERENCE = "REFERENCE"
    STATUS = "STATUS"
    HEARTBEAT = "HEARTBEAT"
    ACKNOWLEDGEMENT = "ACKNOWLEDGEMENT"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


def normalize_message_type(
    message_type: MarketDataChannelMessageType | str | None,
) -> MarketDataChannelMessageType:
    """
    Convert a raw message type into the canonical enum.

    Unknown or invalid values resolve to UNKNOWN.
    """

    if message_type is None:
        return MarketDataChannelMessageType.UNKNOWN

    if isinstance(message_type, MarketDataChannelMessageType):
        return message_type

    try:
        return MarketDataChannelMessageType(
            str(message_type).strip().upper()
        )
    except ValueError:
        return MarketDataChannelMessageType.UNKNOWN


def is_snapshot_type(
    message_type: MarketDataChannelMessageType | str | None,
) -> bool:
    return normalize_message_type(message_type) == (
        MarketDataChannelMessageType.SNAPSHOT
    )


def is_update_type(
    message_type: MarketDataChannelMessageType | str | None,
) -> bool:
    return normalize_message_type(message_type) == (
        MarketDataChannelMessageType.UPDATE
    )


def is_quote_type(
    message_type: MarketDataChannelMessageType | str | None,
) -> bool:
    return normalize_message_type(message_type) == (
        MarketDataChannelMessageType.QUOTE
    )


def is_trade_type(
    message_type: MarketDataChannelMessageType | str | None,
) -> bool:
    return normalize_message_type(message_type) == (
        MarketDataChannelMessageType.TRADE
    )


def is_orderbook_type(
    message_type: MarketDataChannelMessageType | str | None,
) -> bool:
    return normalize_message_type(message_type) in {
        MarketDataChannelMessageType.ORDERBOOK,
        MarketDataChannelMessageType.DEPTH,
    }


def is_candle_type(
    message_type: MarketDataChannelMessageType | str | None,
) -> bool:
    return normalize_message_type(message_type) == (
        MarketDataChannelMessageType.CANDLE
    )


def is_tick_type(
    message_type: MarketDataChannelMessageType | str | None,
) -> bool:
    return normalize_message_type(message_type) == (
        MarketDataChannelMessageType.TICK
    )


def is_reference_type(
    message_type: MarketDataChannelMessageType | str | None,
) -> bool:
    return normalize_message_type(message_type) == (
        MarketDataChannelMessageType.REFERENCE
    )


def is_status_type(
    message_type: MarketDataChannelMessageType | str | None,
) -> bool:
    return normalize_message_type(message_type) == (
        MarketDataChannelMessageType.STATUS
    )


def is_heartbeat_type(
    message_type: MarketDataChannelMessageType | str | None,
) -> bool:
    return normalize_message_type(message_type) == (
        MarketDataChannelMessageType.HEARTBEAT
    )


def is_acknowledgement_type(
    message_type: MarketDataChannelMessageType | str | None,
) -> bool:
    return normalize_message_type(message_type) == (
        MarketDataChannelMessageType.ACKNOWLEDGEMENT
    )


def is_error_type(
    message_type: MarketDataChannelMessageType | str | None,
) -> bool:
    return normalize_message_type(message_type) == (
        MarketDataChannelMessageType.ERROR
    )


def market_data_channel_message_type_health() -> dict[str, object]:
    """
    Return schema health information.
    """

    return {
        "schema": MARKET_DATA_CHANNEL_MESSAGE_TYPE_SCHEMA,
        "version": MARKET_DATA_CHANNEL_MESSAGE_TYPE_VERSION,
        "status": "ready",
        "enum_based": True,
        "canonical_types_defined": True,
        "decision_logic": False,
        "execution_logic": False,
        "broker_dependency": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_DATA_CHANNEL_MESSAGE_TYPE_VERSION",
    "MARKET_DATA_CHANNEL_MESSAGE_TYPE_SCHEMA",
    "MarketDataChannelMessageType",
    "normalize_message_type",
    "is_snapshot_type",
    "is_update_type",
    "is_quote_type",
    "is_trade_type",
    "is_orderbook_type",
    "is_candle_type",
    "is_tick_type",
    "is_reference_type",
    "is_status_type",
    "is_heartbeat_type",
    "is_acknowledgement_type",
    "is_error_type",
    "market_data_channel_message_type_health",
]