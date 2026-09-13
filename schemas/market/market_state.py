from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class MarketSessionState(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    PRE_OPEN = "pre_open"
    POST_CLOSE = "post_close"
    HALTED = "halted"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class MarketState:
    """
    Canonical market-state contract.

    Responsibility:
        Describe the current operational state of a market/instrument.

    This schema deliberately does NOT:
        - calculate intelligence
        - calculate scores
        - decide BUY/SELL
        - apply risk thresholds
        - authorize execution
        - assume universal market hours

    Venue/session services are responsible for determining the state.
    """

    session: MarketSessionState

    tradable: bool
    halted: bool = False

    state_reason: Optional[str] = None

    state_observed_at: Optional[datetime] = None

    session_open_at: Optional[datetime] = None
    session_close_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        # HALTED is an explicit hard operational restriction.
        if self.halted and self.tradable:
            raise ValueError(
                "Invalid MarketState: halted=True cannot coexist with tradable=True"
            )

        # A halted state must carry the halted semantic.
        if self.session == MarketSessionState.HALTED and not self.halted:
            raise ValueError(
                "Invalid MarketState: session=HALTED requires halted=True"
            )

        # Timestamp validation.
        for name, value in (
            ("state_observed_at", self.state_observed_at),
            ("session_open_at", self.session_open_at),
            ("session_close_at", self.session_close_at),
        ):
            if value is not None:
                if value.tzinfo is None or value.utcoffset() is None:
                    raise ValueError(
                        f"{name} must be timezone-aware"
                    )

        # A defined session interval cannot be reversed.
        if (
            self.session_open_at is not None
            and self.session_close_at is not None
            and self.session_close_at < self.session_open_at
        ):
            raise ValueError(
                "session_close_at cannot be earlier than session_open_at"
            )

        # State reason must not be an empty semantic value.
        if self.state_reason is not None and not self.state_reason.strip():
            raise ValueError(
                "state_reason cannot be empty when supplied"
            )

    @property
    def execution_blocked(self) -> bool:
        """
        Operational availability only.

        This is NOT an execution authorization decision.
        CAS / execution safety remains responsible for authorization.
        """
        return self.halted or not self.tradable

    @property
    def is_open(self) -> bool:
        return self.session == MarketSessionState.OPEN

    @property
    def is_closed(self) -> bool:
        return self.session == MarketSessionState.CLOSED

    @property
    def is_unknown(self) -> bool:
        return self.session == MarketSessionState.UNKNOWN

    def normalized(self) -> "MarketState":
        """
        Return an equivalent state with timestamps normalized to UTC.
        """
        def to_utc(value: Optional[datetime]) -> Optional[datetime]:
            if value is None:
                return None
            return value.astimezone(timezone.utc)

        return MarketState(
            session=self.session,
            tradable=self.tradable,
            halted=self.halted,
            state_reason=self.state_reason,
            state_observed_at=to_utc(self.state_observed_at),
            session_open_at=to_utc(self.session_open_at),
            session_close_at=to_utc(self.session_close_at),
        )

    def to_dict(self) -> dict:
        return {
            "session": self.session.value,
            "tradable": self.tradable,
            "halted": self.halted,
            "execution_blocked": self.execution_blocked,
            "state_reason": self.state_reason,
            "state_observed_at": (
                self.state_observed_at.isoformat()
                if self.state_observed_at is not None
                else None
            ),
            "session_open_at": (
                self.session_open_at.isoformat()
                if self.session_open_at is not None
                else None
            ),
            "session_close_at": (
                self.session_close_at.isoformat()
                if self.session_close_at is not None
                else None
            ),
        }


__all__ = [
    "MarketSessionState",
    "MarketState",
]