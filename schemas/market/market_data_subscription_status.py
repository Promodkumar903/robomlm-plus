"""
ROBOMLM PLUS
Market Data Subscription Status Schema

Purpose:
    Defines the lifecycle status of a market-data subscription.

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


MARKET_DATA_SUBSCRIPTION_STATUS_VERSION = "1.0.0"
MARKET_DATA_SUBSCRIPTION_STATUS_SCHEMA = (
    "MARKET_DATA_SUBSCRIPTION_STATUS"
)


class MarketDataSubscriptionStatus(str, Enum):
    """
    Lifecycle states for a market-data subscription.
    """

    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"


def normalize_status(
    status: MarketDataSubscriptionStatus | str | None,
) -> MarketDataSubscriptionStatus:
    """
    Convert a raw status value into the canonical enum.
    """

    if status is None:
        return MarketDataSubscriptionStatus.UNKNOWN

    if isinstance(status, MarketDataSubscriptionStatus):
        return status

    try:
        return MarketDataSubscriptionStatus(
            str(status).strip().upper()
        )
    except ValueError:
        return MarketDataSubscriptionStatus.UNKNOWN


def is_active_status(
    status: MarketDataSubscriptionStatus | str | None,
) -> bool:
    """
    Return True only when the subscription is active.
    """

    return normalize_status(status) == (
        MarketDataSubscriptionStatus.ACTIVE
    )


def is_pending_status(
    status: MarketDataSubscriptionStatus | str | None,
) -> bool:
    """
    Return True when the subscription is awaiting activation.
    """

    return normalize_status(status) == (
        MarketDataSubscriptionStatus.PENDING
    )


def is_paused_status(
    status: MarketDataSubscriptionStatus | str | None,
) -> bool:
    """
    Return True when the subscription is temporarily paused.
    """

    return normalize_status(status) == (
        MarketDataSubscriptionStatus.PAUSED
    )


def is_terminal_status(
    status: MarketDataSubscriptionStatus | str | None,
) -> bool:
    """
    Return True when the subscription has reached a terminal state.
    """

    return normalize_status(status) in {
        MarketDataSubscriptionStatus.CANCELLED,
        MarketDataSubscriptionStatus.EXPIRED,
        MarketDataSubscriptionStatus.FAILED,
        MarketDataSubscriptionStatus.REJECTED,
    }


def is_failure_status(
    status: MarketDataSubscriptionStatus | str | None,
) -> bool:
    """
    Return True for failed or rejected subscriptions.
    """

    return normalize_status(status) in {
        MarketDataSubscriptionStatus.FAILED,
        MarketDataSubscriptionStatus.REJECTED,
    }


def market_data_subscription_status_health() -> dict[str, object]:
    """
    Return schema health information.
    """

    return {
        "schema": MARKET_DATA_SUBSCRIPTION_STATUS_SCHEMA,
        "version": MARKET_DATA_SUBSCRIPTION_STATUS_VERSION,
        "status": "ready",
        "enum_based": True,
        "lifecycle_states_defined": True,
        "decision_logic": False,
        "execution_logic": False,
        "broker_dependency": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_DATA_SUBSCRIPTION_STATUS_VERSION",
    "MARKET_DATA_SUBSCRIPTION_STATUS_SCHEMA",
    "MarketDataSubscriptionStatus",
    "normalize_status",
    "is_active_status",
    "is_pending_status",
    "is_paused_status",
    "is_terminal_status",
    "is_failure_status",
    "market_data_subscription_status_health",
]