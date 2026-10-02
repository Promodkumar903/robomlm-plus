"""
ROBOMLM PLUS
Market Service

Application-level service for market identity, market state,
and market-session coordination.

This layer does not place orders and does not perform broker
or exchange side effects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping, Optional



class MarketServiceError(Exception):
    """Base exception for market-service failures."""


class MarketValidationError(MarketServiceError):
    """Raised when market information is invalid."""


@dataclass
class MarketContext:
    """
    Normalized market context used by higher-level services.
    """

    market: str
    instrument: Optional[str] = None
    venue: Optional[str] = None
    contract: Optional[str] = None
    timeframe: Optional[str] = None
    market_type: Optional[str] = None
    region: Optional[str] = None
    currency: Optional[str] = None
    state: Optional[str] = None
    session: Optional[str] = None
    observed_at: Optional[datetime] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.market = str(self.market).strip()

        if not self.market:
            raise MarketValidationError("market is required")

        if self.instrument is not None:
            self.instrument = str(self.instrument).strip() or None

        if self.venue is not None:
            self.venue = str(self.venue).strip() or None

        if self.contract is not None:
            self.contract = str(self.contract).strip() or None

        if self.timeframe is not None:
            self.timeframe = str(self.timeframe).strip() or None

        if self.market_type is not None:
            self.market_type = str(self.market_type).strip() or None

        if self.region is not None:
            self.region = str(self.region).strip() or None

        if self.currency is not None:
            self.currency = str(self.currency).strip() or None

        if self.state is not None:
            self.state = str(self.state).strip() or None

        if self.session is not None:
            self.session = str(self.session).strip() or None

        if self.observed_at is not None:
            self.observed_at = _normalize_datetime(self.observed_at)

        self.metadata = dict(self.metadata or {})

    @property
    def identity(self) -> tuple[str, Optional[str], Optional[str], Optional[str]]:
        """Return the core market identity tuple."""
        return (
            self.market,
            self.instrument,
            self.venue,
            self.contract,
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable dictionary representation."""
        return {
            "market": self.market,
            "instrument": self.instrument,
            "venue": self.venue,
            "contract": self.contract,
            "timeframe": self.timeframe,
            "market_type": self.market_type,
            "region": self.region,
            "currency": self.currency,
            "state": self.state,
            "session": self.session,
            "observed_at": (
                self.observed_at.isoformat()
                if self.observed_at is not None
                else None
            ),
            "metadata": dict(self.metadata),
        }


class MarketService:
    """
    Registry-like application service for market contexts.

    The service maintains in-process market contexts only.
    It intentionally does not perform network calls, broker calls,
    exchange calls, or execution operations.
    """

    def __init__(self) -> None:
        self._markets: dict[str, MarketContext] = {}

    @staticmethod
    def _key(market: str) -> str:
        value = str(market).strip()

        if not value:
            raise MarketValidationError("market is required")

        return value.upper()

    def register(self, context: MarketContext) -> MarketContext:
        """Register or replace a market context."""
        if not isinstance(context, MarketContext):
            raise MarketValidationError(
                "context must be a MarketContext instance"
            )

        key = self._key(context.market)
        self._markets[key] = context
        return context

    def register_many(
        self,
        contexts: Iterable[MarketContext],
    ) -> list[MarketContext]:
        """Register multiple market contexts."""
        registered: list[MarketContext] = []

        for context in contexts:
            registered.append(self.register(context))

        return registered

    def create(
        self,
        market: str,
        *,
        instrument: Optional[str] = None,
        venue: Optional[str] = None,
        contract: Optional[str] = None,
        timeframe: Optional[str] = None,
        market_type: Optional[str] = None,
        region: Optional[str] = None,
        currency: Optional[str] = None,
        state: Optional[str] = None,
        session: Optional[str] = None,
        observed_at: Optional[datetime] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> MarketContext:
        """Create and register a market context."""
        context = MarketContext(
            market=market,
            instrument=instrument,
            venue=venue,
            contract=contract,
            timeframe=timeframe,
            market_type=market_type,
            region=region,
            currency=currency,
            state=state,
            session=session,
            observed_at=observed_at,
            metadata=dict(metadata or {}),
        )

        return self.register(context)

    def get(self, market: str) -> Optional[MarketContext]:
        """Return a market context or None when not registered."""
        return self._markets.get(self._key(market))

    def require(self, market: str) -> MarketContext:
        """Return a market context or raise when unavailable."""
        context = self.get(market)

        if context is None:
            raise MarketServiceError(
                f"Market is not registered: {market}"
            )

        return context

    def exists(self, market: str) -> bool:
        """Return whether a market is registered."""
        return self._key(market) in self._markets

    def list_markets(self) -> list[MarketContext]:
        """Return registered market contexts."""
        return list(self._markets.values())

    def names(self) -> list[str]:
        """Return registered market names."""
        return list(self._markets.keys())

    def count(self) -> int:
        """Return the number of registered markets."""
        return len(self._markets)

    def update(
        self,
        market: str,
        **changes: Any,
    ) -> MarketContext:
        """
        Update selected fields of an existing market context.

        Unknown fields are rejected to prevent accidental schema drift.
        """
        context = self.require(market)

        allowed = {
            "instrument",
            "venue",
            "contract",
            "timeframe",
            "market_type",
            "region",
            "currency",
            "state",
            "session",
            "observed_at",
            "metadata",
        }

        unknown = set(changes) - allowed

        if unknown:
            raise MarketValidationError(
                f"Unknown market fields: {sorted(unknown)}"
            )

        values = context.to_dict()

        for key, value in changes.items():
            if key == "metadata":
                values[key] = dict(value or {})
            else:
                values[key] = value

        updated = MarketContext(
            market=context.market,
            instrument=values["instrument"],
            venue=values["venue"],
            contract=values["contract"],
            timeframe=values["timeframe"],
            market_type=values["market_type"],
            region=values["region"],
            currency=values["currency"],
            state=values["state"],
            session=values["session"],
            observed_at=_parse_optional_datetime(values["observed_at"]),
            metadata=values["metadata"],
        )

        self._markets[self._key(market)] = updated

        return updated

    def set_state(
        self,
        market: str,
        state: Optional[str],
    ) -> MarketContext:
        """Update market state."""
        return self.update(market, state=state)

    def set_session(
        self,
        market: str,
        session: Optional[str],
    ) -> MarketContext:
        """Update market session."""
        return self.update(market, session=session)

    def set_observed_at(
        self,
        market: str,
        observed_at: Optional[datetime],
    ) -> MarketContext:
        """Update the latest observation timestamp."""
        return self.update(
            market,
            observed_at=observed_at,
        )

    def remove(self, market: str) -> bool:
        """Remove a registered market."""
        key = self._key(market)

        if key not in self._markets:
            return False

        del self._markets[key]
        return True

    def clear(self) -> None:
        """Clear all in-process market contexts."""
        self._markets.clear()

    def snapshot(self) -> dict[str, dict[str, Any]]:
        """Return a dictionary snapshot of all registered markets."""
        return {
            key: context.to_dict()
            for key, context in self._markets.items()
        }

    def summary(self) -> dict[str, Any]:
        """Return a compact service summary."""
        return {
            "service": self.__class__.__name__,
            "market_count": self.count(),
            "markets": self.names(),
        }


def _normalize_datetime(value: datetime) -> datetime:
    """Normalize a datetime to timezone-aware UTC."""
    if not isinstance(value, datetime):
        raise MarketValidationError(
            "observed_at must be a datetime"
        )

    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def _parse_optional_datetime(
    value: Any,
) -> Optional[datetime]:
    """Parse an optional datetime or ISO-8601 string."""
    if value is None:
        return None

    if isinstance(value, datetime):
        return _normalize_datetime(value)

    if isinstance(value, str):
        text = value.strip()

        if not text:
            return None

        try:
            return _normalize_datetime(
                datetime.fromisoformat(text.replace("Z", "+00:00"))
            )
        except ValueError as exc:
            raise MarketValidationError(
                "Invalid observed_at datetime"
            ) from exc

    raise MarketValidationError(
        "observed_at must be datetime, ISO string, or None"
    )


market_service = MarketService()


def register_market(context: MarketContext) -> MarketContext:
    """Register a market using the global market service."""
    return market_service.register(context)


def get_market(market: str) -> Optional[MarketContext]:
    """Get a market from the global market service."""
    return market_service.get(market)


def require_market(market: str) -> MarketContext:
    """Require a market from the global market service."""
    return market_service.require(market)


def list_markets() -> list[MarketContext]:
    """List markets from the global market service."""
    return market_service.list_markets()


__all__ = [
    "MarketServiceError",
    "MarketValidationError",
    "MarketContext",
    "MarketService",
    "market_service",
    "register_market",
    "get_market",
    "require_market",
    "list_markets",
]
