"""
ROBOMLM PLUS
Market Data Acknowledgement Status Schema

Purpose:
    Defines the lifecycle status of a market-data acknowledgement.

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


MARKET_DATA_ACKNOWLEDGEMENT_STATUS_VERSION = "1.0.0"
MARKET_DATA_ACKNOWLEDGEMENT_STATUS_SCHEMA = (
    "MARKET_DATA_ACKNOWLEDGEMENT_STATUS"
)


class MarketDataAcknowledgementStatus(str, Enum):
    """
    Lifecycle states for market-data acknowledgement.
    """

    PENDING = "PENDING"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"
    UNKNOWN = "UNKNOWN"


def is_terminal_status(
    status: MarketDataAcknowledgementStatus | str,
) -> bool:
    """
    Return True when the acknowledgement has reached a terminal state.
    """

    normalized = _normalize_status(status)

    return normalized in {
        MarketDataAcknowledgementStatus.ACKNOWLEDGED,
        MarketDataAcknowledgementStatus.REJECTED,
        MarketDataAcknowledgementStatus.FAILED,
        MarketDataAcknowledgementStatus.EXPIRED,
    }


def is_success_status(
    status: MarketDataAcknowledgementStatus | str,
) -> bool:
    """
    Return True only for a successful acknowledgement.
    """

    return _normalize_status(status) == (
        MarketDataAcknowledgementStatus.ACKNOWLEDGED
    )


def is_failure_status(
    status: MarketDataAcknowledgementStatus | str,
) -> bool:
    """
    Return True for acknowledgement failure or rejection states.
    """

    normalized = _normalize_status(status)

    return normalized in {
        MarketDataAcknowledgementStatus.REJECTED,
        MarketDataAcknowledgementStatus.FAILED,
        MarketDataAcknowledgementStatus.EXPIRED,
    }


def is_pending_status(
    status: MarketDataAcknowledgementStatus | str,
) -> bool:
    """
    Return True when acknowledgement is still pending.
    """

    return _normalize_status(status) == (
        MarketDataAcknowledgementStatus.PENDING
    )


def normalize_status(
    status: MarketDataAcknowledgementStatus | str | None,
) -> MarketDataAcknowledgementStatus:
    """
    Convert a raw status value into the canonical enum.

    Unknown or invalid values resolve to UNKNOWN.
    """

    if status is None:
        return MarketDataAcknowledgementStatus.UNKNOWN

    if isinstance(status, MarketDataAcknowledgementStatus):
        return status

    try:
        return MarketDataAcknowledgementStatus(str(status).strip().upper())
    except ValueError:
        return MarketDataAcknowledgementStatus.UNKNOWN


def _normalize_status(
    status: MarketDataAcknowledgementStatus | str | None,
) -> MarketDataAcknowledgementStatus:
    return normalize_status(status)


def market_data_acknowledgement_status_health() -> dict[str, object]:
    """
    Return schema health information.
    """

    return {
        "schema": MARKET_DATA_ACKNOWLEDGEMENT_STATUS_SCHEMA,
        "version": MARKET_DATA_ACKNOWLEDGEMENT_STATUS_VERSION,
        "status": "ready",
        "enum_based": True,
        "terminal_states_defined": True,
        "decision_logic": False,
        "execution_logic": False,
        "broker_dependency": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_DATA_ACKNOWLEDGEMENT_STATUS_VERSION",
    "MARKET_DATA_ACKNOWLEDGEMENT_STATUS_SCHEMA",
    "MarketDataAcknowledgementStatus",
    "is_terminal_status",
    "is_success_status",
    "is_failure_status",
    "is_pending_status",
    "normalize_status",
    "market_data_acknowledgement_status_health",
]