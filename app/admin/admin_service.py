from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class AdminOperationResult:
    """
    Standard result returned by administrative operations.
    """

    operation_id: str
    operation: str
    status: str
    message: str = ""

    target: str | None = None
    version: str | None = None

    started_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    completed_at: datetime | None = None

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "operation_id": self.operation_id,
            "operation": self.operation,
            "status": self.status,
            "message": self.message,
            "target": self.target,
            "version": self.version,
            "started_at": self.started_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat()
                if self.completed_at is not None
                else None
            ),
            "metadata": dict(self.metadata),
        }

    def is_success(self) -> bool:
        return self.status.lower() in {
            "success",
            "successful",
            "completed",
            "passed",
            "ok",
        }

    def is_failure(self) -> bool:
        return self.status.lower() in {
            "failure",
            "failed",
            "error",
            "rejected",
        }


class AdminService:
    """
    Core administrative service for ROBOMLM.

    This service provides a controlled administrative boundary.
    Specific operations such as deployment, validation, research,
    rollback, stress testing, and version management remain delegated
    to their respective admin modules.
    """

    def __init__(
        self,
        *,
        service_name: str = "ROBOMLM_ADMIN",
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        self.service_name = service_name
        self._metadata: dict[str, Any] = dict(metadata or {})
        self._operation_counter = 0

    @property
    def metadata(self) -> dict[str, Any]:
        return dict(self._metadata)

    def _next_operation_id(self, operation: str) -> str:
        self._operation_counter += 1

        normalized = operation.strip().upper().replace(" ", "_")

        return f"ADMIN-{normalized}-{self._operation_counter:06d}"

    def start_operation(
        self,
        operation: str,
        *,
        target: str | None = None,
        version: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> AdminOperationResult:
        """
        Create a new administrative operation record.

        This method does not execute the requested operation.
        Execution belongs to the dedicated admin module.
        """

        if not operation or not operation.strip():
            raise ValueError("operation must not be empty")

        operation_id = self._next_operation_id(operation)

        operation_metadata = dict(self._metadata)
        operation_metadata.update(metadata or {})

        return AdminOperationResult(
            operation_id=operation_id,
            operation=operation.strip(),
            status="STARTED",
            target=target,
            version=version,
            metadata=operation_metadata,
        )

    def complete_operation(
        self,
        result: AdminOperationResult,
        *,
        status: str = "COMPLETED",
        message: str = "",
        metadata: Mapping[str, Any] | None = None,
    ) -> AdminOperationResult:
        """
        Close an administrative operation with its final status.
        """

        if not isinstance(result, AdminOperationResult):
            raise TypeError(
                "result must be an AdminOperationResult"
            )

        if not status or not status.strip():
            raise ValueError("status must not be empty")

        updated_metadata = dict(result.metadata)
        updated_metadata.update(metadata or {})

        return AdminOperationResult(
            operation_id=result.operation_id,
            operation=result.operation,
            status=status.strip(),
            message=message,
            target=result.target,
            version=result.version,
            started_at=result.started_at,
            completed_at=datetime.now(timezone.utc),
            metadata=updated_metadata,
        )

    def fail_operation(
        self,
        result: AdminOperationResult,
        *,
        message: str,
        metadata: Mapping[str, Any] | None = None,
    ) -> AdminOperationResult:
        """
        Mark an administrative operation as failed.
        """

        return self.complete_operation(
            result,
            status="FAILED",
            message=message,
            metadata=metadata,
        )

    def health_check(self) -> dict[str, Any]:
        """
        Return administrative service health information.
        """

        return {
            "service": self.service_name,
            "status": "HEALTHY",
            "operation_count": self._operation_counter,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": dict(self._metadata),
        }