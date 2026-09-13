from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from threading import RLock
from typing import Any


@dataclass(frozen=True)
class ModeState:
    mode: str
    changed_at: datetime
    reason: str
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["changed_at"] = self.changed_at.isoformat()
        return data


@dataclass(frozen=True)
class ModeChangeResult:
    success: bool
    previous_mode: str
    current_mode: str
    message: str
    timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


class ModeManager:
    """
    Controls AUTOROBIMLM operating modes.

    PAPER:
        Internal/paper operation. No real execution should be assumed.

    DEMO:
        Demonstration or simulation operation.

    LIVE:
        Live operational mode. This class only controls the mode state;
        execution authorization remains the responsibility of the
        execution/risk/kill-switch layers.
    """

    MODES = frozenset({"PAPER", "DEMO", "LIVE"})

    def __init__(
        self,
        initial_mode: str = "PAPER",
    ) -> None:
        initial_mode = self._normalize_mode(initial_mode)
        timestamp = datetime.now(timezone.utc)

        self._state = ModeState(
            mode=initial_mode,
            changed_at=timestamp,
            reason="Initial mode",
            metadata=None,
        )
        self._history: list[ModeState] = [self._state]
        self._lock = RLock()

    @classmethod
    def _normalize_mode(cls, mode: str) -> str:
        if not isinstance(mode, str):
            raise TypeError("mode must be a string")

        normalized = mode.strip().upper()

        if normalized not in cls.MODES:
            raise ValueError(
                f"Unsupported mode: {mode}. "
                f"Allowed modes: {sorted(cls.MODES)}"
            )

        return normalized

    @staticmethod
    def _normalize_reason(reason: str) -> str:
        if not isinstance(reason, str):
            raise TypeError("reason must be a string")

        reason = reason.strip()

        if not reason:
            raise ValueError("reason is required")

        return reason

    @property
    def current_mode(self) -> str:
        with self._lock:
            return self._state.mode

    def get_state(self) -> ModeState:
        with self._lock:
            return self._state

    def set_mode(
        self,
        mode: str,
        reason: str,
        metadata: dict[str, Any] | None = None,
    ) -> ModeChangeResult:
        mode = self._normalize_mode(mode)
        reason = self._normalize_reason(reason)
        timestamp = datetime.now(timezone.utc)

        with self._lock:
            previous_mode = self._state.mode

            if previous_mode == mode:
                return ModeChangeResult(
                    success=False,
                    previous_mode=previous_mode,
                    current_mode=previous_mode,
                    message="Requested mode is already active",
                    timestamp=timestamp,
                )

            new_state = ModeState(
                mode=mode,
                changed_at=timestamp,
                reason=reason,
                metadata=dict(metadata) if metadata else None,
            )

            self._state = new_state
            self._history.append(new_state)

            return ModeChangeResult(
                success=True,
                previous_mode=previous_mode,
                current_mode=mode,
                message="Operating mode changed successfully",
                timestamp=timestamp,
            )

    def switch_to_paper(
        self,
        reason: str = "Manual switch to PAPER",
    ) -> ModeChangeResult:
        return self.set_mode("PAPER", reason)

    def switch_to_demo(
        self,
        reason: str = "Manual switch to DEMO",
    ) -> ModeChangeResult:
        return self.set_mode("DEMO", reason)

    def switch_to_live(
        self,
        reason: str = "Manual switch to LIVE",
    ) -> ModeChangeResult:
        return self.set_mode("LIVE", reason)

    def is_paper(self) -> bool:
        return self.current_mode == "PAPER"

    def is_demo(self) -> bool:
        return self.current_mode == "DEMO"

    def is_live(self) -> bool:
        return self.current_mode == "LIVE"

    def can_execute_live(self) -> bool:
        """
        Indicates whether the mode itself permits live execution.

        This does not authorize an actual trade. Additional gates such
        as risk controls, permissions and kill-switch state must still
        approve the operation.
        """
        return self.is_live()

    def history(self) -> tuple[ModeState, ...]:
        with self._lock:
            return tuple(self._history)

    def transition_count(self) -> int:
        with self._lock:
            return max(0, len(self._history) - 1)

    def reset(
        self,
        mode: str = "PAPER",
        reason: str = "Mode manager reset",
    ) -> ModeChangeResult:
        mode = self._normalize_mode(mode)
        reason = self._normalize_reason(reason)
        timestamp = datetime.now(timezone.utc)

        with self._lock:
            previous_mode = self._state.mode

            state = ModeState(
                mode=mode,
                changed_at=timestamp,
                reason=reason,
                metadata=None,
            )

            self._state = state
            self._history = [state]

            return ModeChangeResult(
                success=previous_mode != mode,
                previous_mode=previous_mode,
                current_mode=mode,
                message="Mode manager reset",
                timestamp=timestamp,
            )

    def health_check(self) -> dict[str, Any]:
        with self._lock:
            return {
                "status": "healthy",
                "current_mode": self._state.mode,
                "transition_count": max(
                    0,
                    len(self._history) - 1,
                ),
                "supported_modes": sorted(self.MODES),
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),
            }