from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from threading import RLock
from typing import Any


@dataclass(frozen=True)
class KillSwitchState:
    enabled: bool
    reason: str | None
    changed_at: datetime

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["changed_at"] = self.changed_at.isoformat()
        return data


@dataclass(frozen=True)
class KillSwitchEvent:
    event_id: str
    action: str
    reason: str | None
    timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


class KillSwitch:
    """
    Central emergency execution-stop control for AUTOROBIMLM.

    When enabled, downstream execution orchestration must treat the
    system as blocked for new execution activity.

    This class controls the emergency state only. It does not itself
    cancel broker orders, close positions, or modify risk policy.
    """

    ENABLE_ACTION = "ENABLE"
    DISABLE_ACTION = "DISABLE"

    def __init__(self) -> None:
        timestamp = datetime.now(timezone.utc)

        self._state = KillSwitchState(
            enabled=False,
            reason=None,
            changed_at=timestamp,
        )

        self._events: list[KillSwitchEvent] = []
        self._counter = 0
        self._lock = RLock()

    @staticmethod
    def _normalize_reason(
        reason: str | None,
    ) -> str | None:
        if reason is None:
            return None

        if not isinstance(reason, str):
            raise TypeError("reason must be a string or None")

        reason = reason.strip()

        return reason or None

    def _next_event_id(self) -> str:
        self._counter += 1
        return f"KILL-{self._counter:08d}"

    def _record_event(
        self,
        action: str,
        reason: str | None,
        timestamp: datetime,
    ) -> KillSwitchEvent:
        event = KillSwitchEvent(
            event_id=self._next_event_id(),
            action=action,
            reason=reason,
            timestamp=timestamp,
        )

        self._events.append(event)
        return event

    def enable(
        self,
        reason: str | None = None,
    ) -> KillSwitchEvent:
        reason = self._normalize_reason(reason)
        timestamp = datetime.now(timezone.utc)

        with self._lock:
            self._state = KillSwitchState(
                enabled=True,
                reason=reason,
                changed_at=timestamp,
            )

            return self._record_event(
                self.ENABLE_ACTION,
                reason,
                timestamp,
            )

    def disable(
        self,
        reason: str | None = None,
    ) -> KillSwitchEvent:
        reason = self._normalize_reason(reason)
        timestamp = datetime.now(timezone.utc)

        with self._lock:
            self._state = KillSwitchState(
                enabled=False,
                reason=reason,
                changed_at=timestamp,
            )

            return self._record_event(
                self.DISABLE_ACTION,
                reason,
                timestamp,
            )

    def trigger(
        self,
        reason: str | None = None,
    ) -> KillSwitchEvent:
        return self.enable(reason)

    def reset(
        self,
        reason: str | None = None,
    ) -> KillSwitchEvent:
        return self.disable(reason)

    def is_enabled(self) -> bool:
        with self._lock:
            return self._state.enabled

    def is_active(self) -> bool:
        return self.is_enabled()

    def is_blocked(self) -> bool:
        return self.is_enabled()

    def allows_execution(self) -> bool:
        return not self.is_enabled()

    def get_state(self) -> KillSwitchState:
        with self._lock:
            return self._state

    @property
    def state(self) -> KillSwitchState:
        return self.get_state()

    @property
    def enabled(self) -> bool:
        return self.is_enabled()

    @property
    def reason(self) -> str | None:
        with self._lock:
            return self._state.reason

    def events(self) -> tuple[KillSwitchEvent, ...]:
        with self._lock:
            return tuple(self._events)

    def event_count(self) -> int:
        with self._lock:
            return len(self._events)

    def last_event(self) -> KillSwitchEvent | None:
        with self._lock:
            if not self._events:
                return None

            return self._events[-1]

    def clear_history(self) -> None:
        with self._lock:
            self._events.clear()

    def clear(self) -> None:
        timestamp = datetime.now(timezone.utc)

        with self._lock:
            self._state = KillSwitchState(
                enabled=False,
                reason=None,
                changed_at=timestamp,
            )
            self._events.clear()
            self._counter = 0

    def health_check(self) -> dict[str, Any]:
        with self._lock:
            return {
                "status": "healthy",
                "enabled": self._state.enabled,
                "blocked": self._state.enabled,
                "allows_execution": not self._state.enabled,
                "reason": self._state.reason,
                "event_count": len(self._events),
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),
            }