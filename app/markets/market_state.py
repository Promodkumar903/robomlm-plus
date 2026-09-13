"""
ROBOMLM PLUS
Market State

Canonical in-process representation of the current operating state
of a market. This module is detection/state-management only and does
not perform broker, exchange, or order-execution operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Optional


class MarketStateError(Exception):
    """Base exception for market-state failures."""


class MarketStateValidationError(MarketStateError):
    """Raised when market-state data is invalid."""


MARKET_STATE_UNKNOWN = "UNKNOWN"
MARKET_STATE_PRE_OPEN = "PRE_OPEN"
MARKET_STATE_OPEN = "OPEN"
MARKET_STATE_PAUSED = "PAUSED"
MARKET_STATE_CLOSED = "CLOSED"
MARKET_STATE_POST_CLOSE = "POST_CLOSE"
MARKET_STATE_HALTED = "HALTED"
MARKET_STATE_ERROR = "ERROR"


VALID_MARKET_STATES = frozenset(
    {
        MARKET_STATE_UNKNOWN,
        MARKET_STATE_PRE_OPEN,
        MARKET_STATE_OPEN,
        MARKET_STATE_PAUSED,
        MARKET_STATE_CLOSED,
        MARKET_STATE_POST_CLOSE,
        MARKET_STATE_HALTED,
        MARKET_STATE_ERROR,
    }
)


@dataclass
class MarketStateSnapshot:
    """
    Point-in-time market operating-state snapshot.
    """

    market: str
    state: str = MARKET_STATE_UNKNOWN
    session: Optional[str] = None
    reason: Optional[str] = None
    observed_at: Optional[datetime] = None
    source: Optional[str] = None
    data_quality: Optional[str] = None
    is_tradable: Optional[bool] = None
    is_quote_available: Optional[bool] = None
    is_order_entry_allowed: Optional[bool] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.market = str(self.market).strip()

        if not self.market:
            raise MarketStateValidationError(
                "market is required"
            )

        self.state = normalize_market_state(self.state)

        if self.session is not None:
            self.session = str(self.session).strip() or None

        if self.reason is not None:
            self.reason = str(self.reason).strip() or None

        if self.source is not None:
            self.source = str(self.source).strip() or None

        if self.data_quality is not None:
            self.data_quality = (
                str(self.data_quality).strip() or None
            )

        if self.observed_at is not None:
            self.observed_at = _normalize_datetime(
                self.observed_at
            )

        if self.is_tradable is not None:
            self.is_tradable = bool(self.is_tradable)

        if self.is_quote_available is not None:
            self.is_quote_available = bool(
                self.is_quote_available
            )

        if self.is_order_entry_allowed is not None:
            self.is_order_entry_allowed = bool(
                self.is_order_entry_allowed
            )

        self.metadata = dict(self.metadata or {})

    @property
    def is_open(self) -> bool:
        return self.state == MARKET_STATE_OPEN

    @property
    def is_closed(self) -> bool:
        return self.state == MARKET_STATE_CLOSED

    @property
    def is_paused(self) -> bool:
        return self.state == MARKET_STATE_PAUSED

    @property
    def is_halted(self) -> bool:
        return self.state == MARKET_STATE_HALTED

    @property
    def is_operational(self) -> bool:
        return self.state in {
            MARKET_STATE_PRE_OPEN,
            MARKET_STATE_OPEN,
            MARKET_STATE_POST_CLOSE,
        }

    @property
    def is_restricted(self) -> bool:
        return self.state in {
            MARKET_STATE_PAUSED,
            MARKET_STATE_HALTED,
            MARKET_STATE_ERROR,
        }

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable dictionary representation."""
        return {
            "market": self.market,
            "state": self.state,
            "session": self.session,
            "reason": self.reason,
            "observed_at": (
                self.observed_at.isoformat()
                if self.observed_at is not None
                else None
            ),
            "source": self.source,
            "data_quality": self.data_quality,
            "is_tradable": self.is_tradable,
            "is_quote_available": self.is_quote_available,
            "is_order_entry_allowed": (
                self.is_order_entry_allowed
            ),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_mapping(
        cls,
        value: Mapping[str, Any],
    ) -> "MarketStateSnapshot":
        """Create a snapshot from a mapping."""
        if not isinstance(value, Mapping):
            raise MarketStateValidationError(
                "value must be a mapping"
            )

        return cls(
            market=value.get("market", ""),
            state=value.get("state", MARKET_STATE_UNKNOWN),
            session=value.get("session"),
            reason=value.get("reason"),
            observed_at=_parse_datetime(
                value.get("observed_at")
            ),
            source=value.get("source"),
            data_quality=value.get("data_quality"),
            is_tradable=value.get("is_tradable"),
            is_quote_available=value.get(
                "is_quote_available"
            ),
            is_order_entry_allowed=value.get(
                "is_order_entry_allowed"
            ),
            metadata=dict(value.get("metadata") or {}),
        )


def normalize_market_state(value: Any) -> str:
    """Normalize and validate a market state."""
    state = str(value).strip().upper()

    if not state:
        return MARKET_STATE_UNKNOWN

    if state not in VALID_MARKET_STATES:
        raise MarketStateValidationError(
            f"Unknown market state: {value}"
        )

    return state


class MarketStateManager:
    """
    In-process market-state manager.

    The manager stores the latest state per market and provides
    deterministic state transitions. It intentionally performs no
    external I/O or trading operations.
    """

    def __init__(self) -> None:
        self._states: dict[str, MarketStateSnapshot] = {}

    @staticmethod
    def _key(market: str) -> str:
        value = str(market).strip()

        if not value:
            raise MarketStateValidationError(
                "market is required"
            )

        return value.upper()

    def set_state(
        self,
        market: str,
        state: str,
        *,
        session: Optional[str] = None,
        reason: Optional[str] = None,
        observed_at: Optional[datetime] = None,
        source: Optional[str] = None,
        data_quality: Optional[str] = None,
        is_tradable: Optional[bool] = None,
        is_quote_available: Optional[bool] = None,
        is_order_entry_allowed: Optional[bool] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> MarketStateSnapshot:
        """Create and store a new market-state snapshot."""
        snapshot = MarketStateSnapshot(
            market=market,
            state=state,
            session=session,
            reason=reason,
            observed_at=observed_at,
            source=source,
            data_quality=data_quality,
            is_tradable=is_tradable,
            is_quote_available=is_quote_available,
            is_order_entry_allowed=is_order_entry_allowed,
            metadata=dict(metadata or {}),
        )

        self._states[self._key(market)] = snapshot

        return snapshot

    def update(
        self,
        market: str,
        **changes: Any,
    ) -> MarketStateSnapshot:
        """
        Update an existing state snapshot.

        Unknown fields are rejected to prevent accidental state-schema
        drift.
        """
        current = self.require(market)

        allowed = {
            "state",
            "session",
            "reason",
            "observed_at",
            "source",
            "data_quality",
            "is_tradable",
            "is_quote_available",
            "is_order_entry_allowed",
            "metadata",
        }

        unknown = set(changes) - allowed

        if unknown:
            raise MarketStateValidationError(
                f"Unknown market-state fields: {sorted(unknown)}"
            )

        values = current.to_dict()

        for key, value in changes.items():
            values[key] = value

        updated = MarketStateSnapshot.from_mapping(
            {
                "market": current.market,
                **values,
            }
        )

        self._states[self._key(market)] = updated

        return updated

    def get(
        self,
        market: str,
    ) -> Optional[MarketStateSnapshot]:
        """Return the latest state for a market."""
        return self._states.get(self._key(market))

    def require(
        self,
        market: str,
    ) -> MarketStateSnapshot:
        """Return the latest state or raise if unavailable."""
        snapshot = self.get(market)

        if snapshot is None:
            raise MarketStateError(
                f"Market state is not available: {market}"
            )

        return snapshot

    def exists(self, market: str) -> bool:
        """Return whether a market has a stored state."""
        return self._key(market) in self._states

    def remove(self, market: str) -> bool:
        """Remove a market state."""
        key = self._key(market)

        if key not in self._states:
            return False

        del self._states[key]
        return True

    def clear(self) -> None:
        """Clear all stored market states."""
        self._states.clear()

    def markets(self) -> list[str]:
        """Return all markets with stored states."""
        return list(self._states.keys())

    def count(self) -> int:
        """Return the number of stored market states."""
        return len(self._states)

    def list_states(self) -> list[MarketStateSnapshot]:
        """Return all latest market-state snapshots."""
        return list(self._states.values())

    def is_open(self, market: str) -> bool:
        """Return whether the market is OPEN."""
        return self.require(market).is_open

    def is_tradable(self, market: str) -> bool:
        """Return the explicit tradability flag."""
        snapshot = self.require(market)

        if snapshot.is_tradable is not None:
            return snapshot.is_tradable

        return snapshot.state == MARKET_STATE_OPEN

    def is_restricted(self, market: str) -> bool:
        """Return whether the market is in a restricted state."""
        return self.require(market).is_restricted

    def transition(
        self,
        market: str,
        new_state: str,
        *,
        reason: Optional[str] = None,
        observed_at: Optional[datetime] = None,
        source: Optional[str] = None,
    ) -> MarketStateSnapshot:
        """
        Perform a controlled state transition.

        This method records the requested state; it does not authorize
        orders or execution.
        """
        current = self.get(market)

        if current is None:
            return self.set_state(
                market,
                new_state,
                reason=reason,
                observed_at=observed_at,
                source=source,
            )

        return self.update(
            market,
            state=new_state,
            reason=reason,
            observed_at=observed_at,
            source=source,
        )

    def pause(
        self,
        market: str,
        *,
        reason: Optional[str] = None,
        observed_at: Optional[datetime] = None,
        source: Optional[str] = None,
    ) -> MarketStateSnapshot:
        """Set market state to PAUSED."""
        return self.transition(
            market,
            MARKET_STATE_PAUSED,
            reason=reason or "market_paused",
            observed_at=observed_at,
            source=source,
        )

    def halt(
        self,
        market: str,
        *,
        reason: Optional[str] = None,
        observed_at: Optional[datetime] = None,
        source: Optional[str] = None,
    ) -> MarketStateSnapshot:
        """Set market state to HALTED."""
        return self.transition(
            market,
            MARKET_STATE_HALTED,
            reason=reason or "market_halted",
            observed_at=observed_at,
            source=source,
        )

    def close(
        self,
        market: str,
        *,
        reason: Optional[str] = None,
        observed_at: Optional[datetime] = None,
        source: Optional[str] = None,
    ) -> MarketStateSnapshot:
        """Set market state to CLOSED."""
        return self.transition(
            market,
            MARKET_STATE_CLOSED,
            reason=reason or "market_closed",
            observed_at=observed_at,
            source=source,
        )

    def open(
        self,
        market: str,
        *,
        session: Optional[str] = None,
        reason: Optional[str] = None,
        observed_at: Optional[datetime] = None,
        source: Optional[str] = None,
    ) -> MarketStateSnapshot:
        """Set market state to OPEN."""
        current = self.get(market)

        if current is None:
            return self.set_state(
                market,
                MARKET_STATE_OPEN,
                session=session,
                reason=reason or "market_open",
                observed_at=observed_at,
                source=source,
            )

        return self.update(
            market,
            state=MARKET_STATE_OPEN,
            session=session
            if session is not None
            else current.session,
            reason=reason or "market_open",
            observed_at=observed_at,
            source=source,
        )

    def summary(self) -> dict[str, Any]:
        """Return a compact manager summary."""
        state_counts: dict[str, int] = {}

        for snapshot in self._states.values():
            state_counts[snapshot.state] = (
                state_counts.get(snapshot.state, 0) + 1
            )

        return {
            "manager": self.__class__.__name__,
            "market_count": self.count(),
            "markets": self.markets(),
            "state_counts": state_counts,
        }


def _normalize_datetime(value: datetime) -> datetime:
    """Normalize datetime to timezone-aware UTC."""
    if not isinstance(value, datetime):
        raise MarketStateValidationError(
            "observed_at must be a datetime"
        )

    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def _parse_datetime(value: Any) -> Optional[datetime]:
    """Parse optional datetime or ISO-8601 value."""
    if value is None:
        return None

    if isinstance(value, datetime):
        return _normalize_datetime(value)

    if isinstance(value, str):
        text = value.strip()

        if not text:
            return None

        try:
            parsed = datetime.fromisoformat(
                text.replace("Z", "+00:00")
            )
            return _normalize_datetime(parsed)
        except ValueError as exc:
            raise MarketStateValidationError(
                "Invalid observed_at datetime"
            ) from exc

    raise MarketStateValidationError(
        "observed_at must be datetime, ISO string, or None"
    )


market_state_manager = MarketStateManager()


def set_market_state(
    market: str,
    state: str,
    **kwargs: Any,
) -> MarketStateSnapshot:
    """Set market state using the global manager."""
    return market_state_manager.set_state(
        market,
        state,
        **kwargs,
    )


def get_market_state(
    market: str,
) -> Optional[MarketStateSnapshot]:
    """Get market state using the global manager."""
    return market_state_manager.get(market)


def require_market_state(
    market: str,
) -> MarketStateSnapshot:
    """Require market state using the global manager."""
    return market_state_manager.require(market)


def is_market_open(market: str) -> bool:
    """Return whether a market is open."""
    return market_state_manager.is_open(market)


def is_market_tradable(market: str) -> bool:
    """Return whether a market is explicitly tradable."""
    return market_state_manager.is_tradable(market)


__all__ = [
    "MarketStateError",
    "MarketStateValidationError",
    "MARKET_STATE_UNKNOWN",
    "MARKET_STATE_PRE_OPEN",
    "MARKET_STATE_OPEN",
    "MARKET_STATE_PAUSED",
    "MARKET_STATE_CLOSED",
    "MARKET_STATE_POST_CLOSE",
    "MARKET_STATE_HALTED",
    "MARKET_STATE_ERROR",
    "VALID_MARKET_STATES",
    "MarketStateSnapshot",
    "MarketStateManager",
    "market_state_manager",
    "normalize_market_state",
    "set_market_state",
    "get_market_state",
    "require_market_state",
    "is_market_open",
    "is_market_tradable",
]