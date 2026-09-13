from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Callable


@dataclass(frozen=True)
class AutomationTask:
    task_id: str
    name: str
    status: str
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        return data


@dataclass(frozen=True)
class AutomationResult:
    success: bool
    task_id: str | None
    status: str
    message: str
    timestamp: datetime
    output: Any = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


class AutomationEngine:
    """
    Core orchestration layer for AUTOROBIMLM.

    The engine manages automation tasks and their lifecycle.
    Actual market execution remains delegated to execution/risk
    components rather than being performed directly here.
    """

    VALID_STATUSES = {
        "queued",
        "running",
        "completed",
        "failed",
        "cancelled",
    }

    def __init__(self) -> None:
        self._tasks: dict[str, AutomationTask] = {}
        self._handlers: dict[str, Callable[[AutomationTask], Any]] = {}
        self._counter = 0
        self._lock = RLock()

    @staticmethod
    def _normalize(value: str, field: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{field} must be a string")

        value = value.strip()

        if not value:
            raise ValueError(f"{field} is required")

        return value

    def _next_task_id(self) -> str:
        self._counter += 1
        return f"AUTO-{self._counter:08d}"

    def register_handler(
        self,
        name: str,
        handler: Callable[[AutomationTask], Any],
    ) -> None:
        name = self._normalize(name, "name")

        if not callable(handler):
            raise TypeError("handler must be callable")

        with self._lock:
            self._handlers[name] = handler

    def unregister_handler(self, name: str) -> bool:
        name = self._normalize(name, "name")

        with self._lock:
            return self._handlers.pop(name, None) is not None

    def create_task(
        self,
        name: str,
        metadata: dict[str, Any] | None = None,
    ) -> AutomationTask:
        name = self._normalize(name, "name")
        timestamp = datetime.now(timezone.utc)

        with self._lock:
            task = AutomationTask(
                task_id=self._next_task_id(),
                name=name,
                status="queued",
                created_at=timestamp,
                updated_at=timestamp,
                metadata=dict(metadata) if metadata else None,
            )

            self._tasks[task.task_id] = task

        return task

    def get_task(self, task_id: str) -> AutomationTask | None:
        task_id = self._normalize(task_id, "task_id")

        with self._lock:
            return self._tasks.get(task_id)

    def _update_status(
        self,
        task_id: str,
        status: str,
    ) -> AutomationTask:
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid task status: {status}")

        task_id = self._normalize(task_id, "task_id")

        with self._lock:
            task = self._tasks.get(task_id)

            if task is None:
                raise KeyError(f"Unknown task: {task_id}")

            updated = AutomationTask(
                task_id=task.task_id,
                name=task.name,
                status=status,
                created_at=task.created_at,
                updated_at=datetime.now(timezone.utc),
                metadata=task.metadata,
            )

            self._tasks[task_id] = updated
            return updated

    def start(self, task_id: str) -> AutomationResult:
        timestamp = datetime.now(timezone.utc)

        try:
            task = self._update_status(task_id, "running")
        except (KeyError, ValueError) as exc:
            return AutomationResult(
                success=False,
                task_id=task_id,
                status="failed",
                message=str(exc),
                timestamp=timestamp,
            )

        handler = self._handlers.get(task.name)

        if handler is None:
            return AutomationResult(
                success=True,
                task_id=task.task_id,
                status=task.status,
                message="Task started; no execution handler registered",
                timestamp=timestamp,
            )

        try:
            output = handler(task)
            completed = self._update_status(
                task.task_id,
                "completed",
            )

            return AutomationResult(
                success=True,
                task_id=completed.task_id,
                status=completed.status,
                message="Automation task completed",
                timestamp=datetime.now(timezone.utc),
                output=output,
            )

        except Exception as exc:
            self._update_status(task.task_id, "failed")

            return AutomationResult(
                success=False,
                task_id=task.task_id,
                status="failed",
                message=f"Automation handler failed: {exc}",
                timestamp=datetime.now(timezone.utc),
            )

    def cancel(self, task_id: str) -> AutomationResult:
        timestamp = datetime.now(timezone.utc)

        try:
            task = self.get_task(task_id)

            if task is None:
                raise KeyError(f"Unknown task: {task_id}")

            if task.status in {"completed", "failed", "cancelled"}:
                return AutomationResult(
                    success=False,
                    task_id=task.task_id,
                    status=task.status,
                    message="Task cannot be cancelled in its current state",
                    timestamp=timestamp,
                )

            cancelled = self._update_status(
                task.task_id,
                "cancelled",
            )

            return AutomationResult(
                success=True,
                task_id=cancelled.task_id,
                status=cancelled.status,
                message="Automation task cancelled",
                timestamp=datetime.now(timezone.utc),
            )

        except KeyError as exc:
            return AutomationResult(
                success=False,
                task_id=task_id,
                status="failed",
                message=str(exc),
                timestamp=timestamp,
            )

    def list_tasks(
        self,
        status: str | None = None,
    ) -> tuple[AutomationTask, ...]:
        if status is not None and status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid task status: {status}")

        with self._lock:
            tasks = tuple(self._tasks.values())

            if status is None:
                return tasks

            return tuple(
                task for task in tasks
                if task.status == status
            )

    def task_count(self) -> int:
        with self._lock:
            return len(self._tasks)

    def active_task_count(self) -> int:
        with self._lock:
            return sum(
                1
                for task in self._tasks.values()
                if task.status in {"queued", "running"}
            )

    def clear(self) -> None:
        with self._lock:
            self._tasks.clear()
            self._handlers.clear()
            self._counter = 0

    def health_check(self) -> dict[str, Any]:
        with self._lock:
            return {
                "status": "healthy",
                "task_count": len(self._tasks),
                "active_task_count": sum(
                    1
                    for task in self._tasks.values()
                    if task.status in {"queued", "running"}
                ),
                "handler_count": len(self._handlers),
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),
            }