"""
ROBOMLM PLUS
Graceful Shutdown Manager

Purpose:
    Provide a controlled and idempotent application shutdown mechanism.

Design:
    - Callback based shutdown.
    - Safe repeated shutdown requests.
    - LIFO callback execution.
    - Exceptions in one callback do not prevent remaining cleanup.
    - No forced process termination.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Callable, Optional


ShutdownCallback = Callable[[], None]


class ShutdownError(RuntimeError):
    """Raised when shutdown management encounters a critical error."""


@dataclass(frozen=True)
class ShutdownCallbackResult:
    """Result of executing one shutdown callback."""

    name: str
    success: bool
    error: Optional[str] = None


@dataclass(frozen=True)
class ShutdownResult:
    """Final shutdown execution result."""

    requested: bool
    completed: bool
    callbacks_executed: int
    callbacks_failed: int
    callback_results: tuple[ShutdownCallbackResult, ...]


class ShutdownManager:
    """
    Central graceful shutdown coordinator.

    Components register cleanup callbacks during startup.
    During shutdown, callbacks execute in reverse registration order.
    """

    def __init__(self) -> None:
        self._callbacks: list[tuple[str, ShutdownCallback]] = []
        self._shutdown_requested = False
        self._shutdown_completed = False
        self._lock = threading.RLock()

    @property
    def shutdown_requested(self) -> bool:
        with self._lock:
            return self._shutdown_requested

    @property
    def shutdown_completed(self) -> bool:
        with self._lock:
            return self._shutdown_completed

    @property
    def callback_count(self) -> int:
        with self._lock:
            return len(self._callbacks)

    def register(
        self,
        callback: ShutdownCallback,
        name: Optional[str] = None,
    ) -> None:
        """
        Register a shutdown callback.

        Callbacks are executed in reverse registration order.
        """

        if not callable(callback):
            raise ShutdownError("Shutdown callback must be callable.")

        callback_name = name or getattr(
            callback,
            "__name__",
            "anonymous_callback",
        )

        with self._lock:
            if self._shutdown_requested:
                raise ShutdownError(
                    "Cannot register callback after shutdown has been requested."
                )

            self._callbacks.append((callback_name, callback))

    def unregister(self, callback: ShutdownCallback) -> bool:
        """Remove a previously registered callback."""

        with self._lock:
            for index, (_, registered_callback) in enumerate(self._callbacks):
                if registered_callback is callback:
                    self._callbacks.pop(index)
                    return True

        return False

    def request_shutdown(self) -> bool:
        """
        Mark shutdown as requested.

        Returns True only when this call changes the state.
        """

        with self._lock:
            if self._shutdown_requested:
                return False

            self._shutdown_requested = True
            return True

    def execute(self) -> ShutdownResult:
        """
        Execute all registered shutdown callbacks.

        Repeated calls after completion return the existing completed state.
        """

        with self._lock:
            if self._shutdown_completed:
                return ShutdownResult(
                    requested=self._shutdown_requested,
                    completed=True,
                    callbacks_executed=0,
                    callbacks_failed=0,
                    callback_results=(),
                )

            self._shutdown_requested = True

            callbacks = list(reversed(self._callbacks))

        results: list[ShutdownCallbackResult] = []

        for name, callback in callbacks:
            try:
                callback()

                results.append(
                    ShutdownCallbackResult(
                        name=name,
                        success=True,
                    )
                )

            except Exception as exc:
                results.append(
                    ShutdownCallbackResult(
                        name=name,
                        success=False,
                        error=f"{type(exc).__name__}: {exc}",
                    )
                )

        with self._lock:
            self._shutdown_completed = True

        failed = sum(
            1
            for result in results
            if not result.success
        )

        return ShutdownResult(
            requested=True,
            completed=failed == 0,
            callbacks_executed=len(results),
            callbacks_failed=failed,
            callback_results=tuple(results),
        )

    def reset(self) -> None:
        """
        Reset shutdown state.

        Intended for controlled test/reinitialization scenarios.
        """

        with self._lock:
            self._shutdown_requested = False
            self._shutdown_completed = False

    def clear_callbacks(self) -> None:
        """Remove all registered callbacks."""

        with self._lock:
            self._callbacks.clear()

    def summary(self) -> dict:
        """Return current shutdown manager state."""

        with self._lock:
            return {
                "shutdown_requested": self._shutdown_requested,
                "shutdown_completed": self._shutdown_completed,
                "callback_count": len(self._callbacks),
                "callbacks": [
                    name
                    for name, _ in self._callbacks
                ],
            }


shutdown_manager = ShutdownManager()


def register_shutdown_callback(
    callback: ShutdownCallback,
    name: Optional[str] = None,
) -> None:
    """Convenience function for callback registration."""

    shutdown_manager.register(
        callback=callback,
        name=name,
    )


def request_shutdown() -> bool:
    """Request graceful shutdown."""

    return shutdown_manager.request_shutdown()


def execute_shutdown() -> ShutdownResult:
    """Execute graceful shutdown."""

    return shutdown_manager.execute()


__all__ = [
    "ShutdownCallback",
    "ShutdownError",
    "ShutdownCallbackResult",
    "ShutdownResult",
    "ShutdownManager",
    "shutdown_manager",
    "register_shutdown_callback",
    "request_shutdown",
    "execute_shutdown",
]