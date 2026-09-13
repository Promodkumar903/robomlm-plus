"""
ROBOMLM PLUS
Market Data Channel Type Schema

Purpose:
    Defines the canonical types of logical channels used for
    market-data transport and delivery.

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


MARKET_DATA_CHANNEL_TYPE_VERSION = "1.0.0"
MARKET_DATA_CHANNEL_TYPE_SCHEMA = "MARKET_DATA_CHANNEL_TYPE"


class MarketDataChannelType(str, Enum):
    """
    Canonical market-data channel categories.
    """

    STREAM = "STREAM"
    SNAPSHOT = "SNAPSHOT"
    QUOTE = "QUOTE"
    TRADE = "TRADE"
    ORDERBOOK = "ORDERBOOK"
    DEPTH = "DEPTH"
    CANDLE = "CANDLE"
    TICK = "TICK"
    REFERENCE = "REFERENCE"
    STATUS = "STATUS"
    UNKNOWN = "UNKNOWN"


def normalize_channel_type(
    channel_type: MarketDataChannelType | str | None,
) -> MarketDataChannelType:
    """
    Convert a raw channel type into the canonical enum.

    Unknown or invalid values resolve to UNKNOWN.
    """

    if channel_type is None:
        return MarketDataChannelType.UNKNOWN

    if isinstance(channel_type, MarketDataChannelType):
        return channel_type

    try:
        return MarketDataChannelType(
            str(channel_type).strip().upper()
        )
    except ValueError:
        return MarketDataChannelType.UNKNOWN


def is_stream_type(
    channel_type: MarketDataChannelType | str | None,
) -> bool:
    return normalize_channel_type(channel_type) == (
        MarketDataChannelType.STREAM
    )


def is_snapshot_type(
    channel_type: MarketDataChannelType | str | None,
) -> bool:
    return normalize_channel_type(channel_type) == (
        MarketDataChannelType.SNAPSHOT
    )


def is_quote_type(
    channel_type: MarketDataChannelType | str | None,
) -> bool:
    return normalize_channel_type(channel_type) == (
        MarketDataChannelType.QUOTE
    )


def is_trade_type(
    channel_type: MarketDataChannelType | str | None,
) -> bool:
    return normalize_channel_type(channel_type) == (
        MarketDataChannelType.TRADE
    )


def is_orderbook_type(
    channel_type: MarketDataChannelType | str | None,
) -> bool:
    return normalize_channel_type(channel_type) in {
        MarketDataChannelType.ORDERBOOK,
        MarketDataChannelType.DEPTH,
    }


def is_candle_type(
    channel_type: MarketDataChannelType | str | None,
) -> bool:
    return normalize_channel_type(channel_type) == (
        MarketDataChannelType.CANDLE
    )


def is_tick_type(
    channel_type: MarketDataChannelType | str | None,
) -> bool:
    return normalize_channel_type(channel_type) == (
        MarketDataChannelType.TICK
    )


def is_reference_type(
    channel_type: MarketDataChannelType | str | None,
) -> bool:
    return normalize_channel_type(channel_type) == (
        MarketDataChannelType.REFERENCE
    )


def is_status_type(
    channel_type: MarketDataChannelType | str | None,
) -> bool:
    return normalize_channel_type(channel_type) == (
        MarketDataChannelType.STATUS
    )


def market_data_channel_type_health() -> dict[str, object]:
    """
    Return schema health information.
    """

    return {
        "schema": MARKET_DATA_CHANNEL_TYPE_SCHEMA,
        "version": MARKET_DATA_CHANNEL_TYPE_VERSION,
        "status": "ready",
        "enum_based": True,
        "canonical_types_defined": True,
        "decision_logic": False,
        "execution_logic": False,
        "broker_dependency": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_DATA_CHANNEL_TYPE_VERSION",
    "MARKET_DATA_CHANNEL_TYPE_SCHEMA",
    "MarketDataChannelType",
    "normalize_channel_type",
    "is_stream_type",
    "is_snapshot_type",
    "is_quote_type",
    "is_trade_type",
    "is_orderbook_type",
    "is_candle_type",
    "is_tick_type",
    "is_reference_type",
    "is_status_type",
    "market_data_channel_type_health",
]