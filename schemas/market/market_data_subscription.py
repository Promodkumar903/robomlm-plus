"""
ROBOMLM PLUS
Market Data Subscription Schema

Purpose:
    Represents a subscription definition for receiving market-data
    streams or updates.

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


MARKET_DATA_SUBSCRIPTION_VERSION = "1.0.0"
MARKET_DATA_SUBSCRIPTION_SCHEMA = "MARKET_DATA_SUBSCRIPTION"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class MarketDataSubscription:
    """
    Immutable market-data subscription definition.
    """

    subscription_id: str

    symbol: Optional[str] = None
    market: Optional[str] = None
    exchange: Optional[str] = None
    instrument: Optional[str] = None
    venue: Optional[str] = None

    data_type: Optional[str] = None
    frequency: Optional[str] = None

    active: bool = True

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.subscription_id:
            raise ValueError("subscription_id is required.")

        now = _utc_now()

        if self.created_at is None:
            object.__setattr__(self, "created_at", now)

        if self.updated_at is None:
            object.__setattr__(self, "updated_at", now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def is_active(self) -> bool:
        return self.active

    def matches(
        self,
        *,
        symbol: Optional[str] = None,
        market: Optional[str] = None,
        exchange: Optional[str] = None,
        instrument: Optional[str] = None,
        venue: Optional[str] = None,
        data_type: Optional[str] = None,
        frequency: Optional[str] = None,
    ) -> bool:
        """
        Check whether supplied criteria match this subscription.

        None criteria are treated as wildcards.
        """

        checks = (
            (self.symbol, symbol),
            (self.market, market),
            (self.exchange, exchange),
            (self.instrument, instrument),
            (self.venue, venue),
            (self.data_type, data_type),
            (self.frequency, frequency),
        )

        for current, requested in checks:
            if requested is None:
                continue

            if current is None:
                return False

            if str(current).upper() != str(requested).upper():
                return False

        return True


def create_market_data_subscription(
    subscription_id: str,
    *,
    symbol: Optional[str] = None,
    market: Optional[str] = None,
    exchange: Optional[str] = None,
    instrument: Optional[str] = None,
    venue: Optional[str] = None,
    data_type: Optional[str] = None,
    frequency: Optional[str] = None,
    active: bool = True,
    created_at: Optional[datetime] = None,
    updated_at: Optional[datetime] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> MarketDataSubscription:
    """
    Factory for creating a market-data subscription.
    """

    return MarketDataSubscription(
        subscription_id=subscription_id,
        symbol=symbol,
        market=market,
        exchange=exchange,
        instrument=instrument,
        venue=venue,
        data_type=data_type,
        frequency=frequency,
        active=active,
        created_at=created_at,
        updated_at=updated_at,
        metadata=dict(metadata or {}),
    )


def market_data_subscription_health() -> dict[str, Any]:
    """
    Return schema health information.
    """

    return {
        "schema": MARKET_DATA_SUBSCRIPTION_SCHEMA,
        "version": MARKET_DATA_SUBSCRIPTION_VERSION,
        "status": "ready",
        "immutable": True,
        "matching_supported": True,
        "decision_logic": False,
        "execution_logic": False,
        "broker_dependency": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_DATA_SUBSCRIPTION_VERSION",
    "MARKET_DATA_SUBSCRIPTION_SCHEMA",
    "MarketDataSubscription",
    "create_market_data_subscription",
    "market_data_subscription_health",
]