"""
ROBOMLM PLUS
Market Session

Provides deterministic session-state helpers for market operating
hours and session lifecycle. This module does not connect to a
broker/exchange and does not place orders.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Mapping, Optional


class MarketSessionError(Exception):
    """Base exception for market-session failures."""


class MarketSessionValidationError(MarketSessionError):
    """Raised when session configuration or input is invalid."""


SESSION_OPEN = "OPEN"
SESSION_CLOSED = "CLOSED"
SESSION_PRE_OPEN = "PRE_OPEN"
SESSION_POST_CLOSE = "POST_CLOSE"
SESSION_UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class SessionWindow:
    """Represents one local-time market session window."""

    name: str
    open_time: time
    close_time: time
    timezone_name: str = "UTC"

    def __post_init__(self) -> None:
        if not str(self.name).strip():
            raise MarketSessionValidationError(
                "Session name is required"
            )

        if not isinstance(self.open_time, time):
            raise MarketSessionValidationError(
                "open_time must be a datetime.time"
            )

        if not isinstance(self.close_time, time):
            raise MarketSessionValidationError(
                "close_time must be a datetime.time"
            )

        if not str(self.timezone_name).strip():
            raise MarketSessionValidationError(
                "timezone_name is required"
            )

    @property
    def crosses_midnight(self) -> bool:
        """Return whether the session closes on the following day."""
        return self.close_time <= self.open_time

    def contains(self, local_time: time) -> bool:
        """Return whether a local clock time falls inside the window."""
        if not isinstance(local_time, time):
            raise MarketSessionValidationError(
                "local_time must be a datetime.time"
            )

        current = local_time.replace(tzinfo=None)
        opening = self.open_time.replace(tzinfo=None)
        closing = self.close_time.replace(tzinfo=None)

        if not self.crosses_midnight:
            return opening <= current < closing

        return current >= opening or current < closing


@dataclass(frozen=True)
class MarketSessionState:
    """Point-in-time evaluation of a market session."""

    market: str
    state: str
    session_name: Optional[str]
    evaluated_at: datetime
    window_open: Optional[datetime] = None
    window_close: Optional[datetime] = None
    timezone_name: str = "UTC"
    reason: Optional[str] = None

    @property
    def is_open(self) -> bool:
        return self.state == SESSION_OPEN

    @property
    def is_closed(self) -> bool:
        return self.state == SESSION_CLOSED

    @property
    def is_pre_open(self) -> bool:
        return self.state == SESSION_PRE_OPEN

    @property
    def is_post_close(self) -> bool:
        return self.state == SESSION_POST_CLOSE

    def to_dict(self) -> dict[str, Any]:
        return {
            "market": self.market,
            "state": self.state,
            "session_name": self.session_name,
            "evaluated_at": self.evaluated_at.isoformat(),
            "window_open": (
                self.window_open.isoformat()
                if self.window_open is not None
                else None
            ),
            "window_close": (
                self.window_close.isoformat()
                if self.window_close is not None
                else None
            ),
            "timezone_name": self.timezone_name,
            "reason": self.reason,
        }


class MarketSession:
    """
    Deterministic market-session evaluator.

    Session definitions are supplied explicitly by the application
    or registry layer. No external calendar or network access is
    performed here.
    """

    def __init__(
        self,
        market: str,
        *,
        timezone_name: str = "UTC",
        windows: Optional[list[SessionWindow]] = None,
        holidays: Optional[set[date]] = None,
    ) -> None:
        self.market = str(market).strip()

        if not self.market:
            raise MarketSessionValidationError(
                "market is required"
            )

        self.timezone_name = str(timezone_name).strip()

        if not self.timezone_name:
            raise MarketSessionValidationError(
                "timezone_name is required"
            )

        self._windows: list[SessionWindow] = list(windows or [])
        self._holidays: set[date] = set(holidays or set())

    def add_window(self, window: SessionWindow) -> SessionWindow:
        """Add a session window."""
        if not isinstance(window, SessionWindow):
            raise MarketSessionValidationError(
                "window must be a SessionWindow"
            )

        self._windows.append(window)
        return window

    def remove_window(self, name: str) -> bool:
        """Remove all windows matching the supplied name."""
        target = str(name).strip().upper()

        original_count = len(self._windows)

        self._windows = [
            window
            for window in self._windows
            if window.name.strip().upper() != target
        ]

        return len(self._windows) != original_count

    def windows(self) -> list[SessionWindow]:
        """Return configured session windows."""
        return list(self._windows)

    def set_holidays(self, holidays: set[date]) -> None:
        """Replace the configured holiday set."""
        self._holidays = set(holidays)

    def add_holiday(self, holiday: date) -> None:
        """Add a market holiday."""
        if not isinstance(holiday, date):
            raise MarketSessionValidationError(
                "holiday must be a datetime.date"
            )

        self._holidays.add(holiday)

    def remove_holiday(self, holiday: date) -> bool:
        """Remove a market holiday."""
        if holiday not in self._holidays:
            return False

        self._holidays.remove(holiday)
        return True

    def is_holiday(self, value: date) -> bool:
        """Return whether a date is configured as a holiday."""
        if not isinstance(value, date):
            raise MarketSessionValidationError(
                "value must be a datetime.date"
            )

        return value in self._holidays

    def evaluate(
        self,
        at: Optional[datetime] = None,
    ) -> MarketSessionState:
        """
        Evaluate the configured market session at a given timestamp.

        The timestamp is normalized to UTC for deterministic internal
        handling. The configured timezone name is retained as metadata;
        this module intentionally does not depend on external timezone
        databases.
        """
        evaluated_at = _normalize_datetime(at or datetime.now(timezone.utc))

        if evaluated_at.date() in self._holidays:
            return MarketSessionState(
                market=self.market,
                state=SESSION_CLOSED,
                session_name=None,
                evaluated_at=evaluated_at,
                timezone_name=self.timezone_name,
                reason="market_holiday",
            )

        if not self._windows:
            return MarketSessionState(
                market=self.market,
                state=SESSION_UNKNOWN,
                session_name=None,
                evaluated_at=evaluated_at,
                timezone_name=self.timezone_name,
                reason="no_session_windows_configured",
            )

        current_time = evaluated_at.time()

        for window in self._windows:
            if window.contains(current_time):
                opening, closing = self._window_datetimes(
                    evaluated_at,
                    window,
                )

                return MarketSessionState(
                    market=self.market,
                    state=SESSION_OPEN,
                    session_name=window.name,
                    evaluated_at=evaluated_at,
                    window_open=opening,
                    window_close=closing,
                    timezone_name=window.timezone_name,
                    reason="inside_session_window",
                )

        next_window = self._next_window(evaluated_at)

        if next_window is not None:
            opening, closing = self._window_datetimes(
                evaluated_at,
                next_window,
            )

            if opening <= evaluated_at:
                opening += timedelta(days=1)
                closing += timedelta(days=1)

            return MarketSessionState(
                market=self.market,
                state=SESSION_PRE_OPEN,
                session_name=next_window.name,
                evaluated_at=evaluated_at,
                window_open=opening,
                window_close=closing,
                timezone_name=next_window.timezone_name,
                reason="before_next_session",
            )

        return MarketSessionState(
            market=self.market,
            state=SESSION_POST_CLOSE,
            session_name=None,
            evaluated_at=evaluated_at,
            timezone_name=self.timezone_name,
            reason="after_configured_sessions",
        )

    def is_open(self, at: Optional[datetime] = None) -> bool:
        """Return whether the market is currently inside a session."""
        return self.evaluate(at).is_open

    def current_session(
        self,
        at: Optional[datetime] = None,
    ) -> Optional[str]:
        """Return the active session name, if any."""
        return self.evaluate(at).session_name

    def summary(self) -> dict[str, Any]:
        """Return a compact configuration summary."""
        return {
            "market": self.market,
            "timezone_name": self.timezone_name,
            "window_count": len(self._windows),
            "windows": [
                {
                    "name": window.name,
                    "open_time": window.open_time.isoformat(),
                    "close_time": window.close_time.isoformat(),
                    "timezone_name": window.timezone_name,
                    "crosses_midnight": window.crosses_midnight,
                }
                for window in self._windows
            ],
            "holiday_count": len(self._holidays),
        }


    def _next_window(
        self,
        evaluated_at: datetime,
    ) -> Optional[SessionWindow]:
        """Find the next configured session window."""
        current = evaluated_at.time().replace(tzinfo=None)

        candidates = [
            window
            for window in self._windows
            if window.open_time.replace(tzinfo=None) > current
        ]

        if candidates:
            return min(
                candidates,
                key=lambda item: item.open_time,
            )

        return None

    @staticmethod
    def _window_datetimes(
        evaluated_at: datetime,
        window: SessionWindow,
    ) -> tuple[datetime, datetime]:
        """Build opening and closing datetimes for a session."""
        base_date = evaluated_at.date()

        opening = datetime.combine(
            base_date,
            window.open_time,
            tzinfo=evaluated_at.tzinfo,
        )

        closing = datetime.combine(
            base_date,
            window.close_time,
            tzinfo=evaluated_at.tzinfo,
        )

        if window.crosses_midnight:
            closing += timedelta(days=1)

        return opening, closing


class MarketSessionRegistry:
    """In-process registry of market-session evaluators."""

    def __init__(self) -> None:
        self._sessions: dict[str, MarketSession] = {}

    @staticmethod
    def _key(market: str) -> str:
        value = str(market).strip()

        if not value:
            raise MarketSessionValidationError(
                "market is required"
            )

        return value.upper()

    def register(self, session: MarketSession) -> MarketSession:
        """Register or replace a market-session evaluator."""
        if not isinstance(session, MarketSession):
            raise MarketSessionValidationError(
                "session must be a MarketSession"
            )

        self._sessions[self._key(session.market)] = session
        return session

    def get(self, market: str) -> Optional[MarketSession]:
        """Return a registered session evaluator."""
        return self._sessions.get(self._key(market))

    def require(self, market: str) -> MarketSession:
        """Require a registered session evaluator."""
        session = self.get(market)

        if session is None:
            raise MarketSessionError(
                f"Market session is not registered: {market}"
            )

        return session

    def exists(self, market: str) -> bool:
        """Return whether a market session is registered."""
        return self._key(market) in self._sessions

    def remove(self, market: str) -> bool:
        """Remove a registered market session."""
        key = self._key(market)

        if key not in self._sessions:
            return False

        del self._sessions[key]
        return True

    def clear(self) -> None:
        """Clear all registered market sessions."""
        self._sessions.clear()

    def names(self) -> list[str]:
        """Return registered market names."""
        return list(self._sessions.keys())

    def count(self) -> int:
        """Return the number of registered sessions."""
        return len(self._sessions)

    def evaluate(
        self,
        market: str,
        at: Optional[datetime] = None,
    ) -> MarketSessionState:
        """Evaluate one registered market session."""
        return self.require(market).evaluate(at)

    def summary(self) -> dict[str, Any]:
        """Return registry summary."""
        return {
            "registry": self.__class__.__name__,
            "session_count": self.count(),
            "markets": self.names(),
        }


def _normalize_datetime(value: datetime) -> datetime:
    """Normalize a datetime to timezone-aware UTC."""
    if not isinstance(value, datetime):
        raise MarketSessionValidationError(
            "timestamp must be a datetime"
        )

    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


market_session_registry = MarketSessionRegistry()


def register_market_session(
    session: MarketSession,
) -> MarketSession:
    """Register a market session in the global registry."""
    return market_session_registry.register(session)


def get_market_session(
    market: str,
) -> Optional[MarketSession]:
    """Get a market session from the global registry."""
    return market_session_registry.get(market)


def require_market_session(
    market: str,
) -> MarketSession:
    """Require a market session from the global registry."""
    return market_session_registry.require(market)


def evaluate_market_session(
    market: str,
    at: Optional[datetime] = None,
) -> MarketSessionState:
    """Evaluate a market session using the global registry."""
    return market_session_registry.evaluate(market, at)


__all__ = [
    "MarketSessionError",
    "MarketSessionValidationError",
    "SESSION_OPEN",
    "SESSION_CLOSED",
    "SESSION_PRE_OPEN",
    "SESSION_POST_CLOSE",
    "SESSION_UNKNOWN",
    "SessionWindow",
    "MarketSessionState",
    "MarketSession",
    "MarketSessionRegistry",
    "market_session_registry",
    "register_market_session",
    "get_market_session",
    "require_market_session",
    "evaluate_market_session",
]