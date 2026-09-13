from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class RollbackRecord:
    """
    Immutable record describing a ROBOMLM rollback operation.
    """

    rollback_id: str
    target: str
    from_version: str
    to_version: str
    status: str

    reason: str = ""

    requested_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    completed_at: datetime | None = None

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rollback_id": self.rollback_id,
            "target": self.target,
            "from_version": self.from_version,
            "to_version": self.to_version,
            "status": self.status,
            "reason": self.reason,
            "requested_at": self.requested_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat()
                if self.completed_at is not None
                else None
            ),
            "metadata": dict(self.metadata),
        }

    def is_pending(self) -> bool:
        return self.status.upper() in {
            "PENDING",
            "ROLLBACK_PENDING",
        }

    def is_completed(self) -> bool:
        return self.status.upper() in {
            "COMPLETED",
            "SUCCESS",
            "FAILED",
            "CANCELLED",
        }

    def is_valid(self) -> bool:
        if not self.rollback_id:
            return False

        if not self.target:
            return False

        if not self.from_version:
            return False

        if not self.to_version:
            return False

        if not self.status:
            return False

        if (
            self.completed_at is not None
            and self.completed_at < self.requested_at
        ):
            return False

        return True


class RollbackAdmin:
    """
    Administrative lifecycle manager for controlled rollbacks.

    This class records rollback intent and state. It does not perform
    infrastructure-level rollback operations itself.
    """

    def __init__(
        self,
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        self._metadata: dict[str, Any] = dict(metadata or {})
        self._rollback_counter = 0
        self._rollbacks: dict[str, RollbackRecord] = {}

    @property
    def metadata(self) -> dict[str, Any]:
        return dict(self._metadata)

    def _next_rollback_id(self) -> str:
        self._rollback_counter += 1
        return f"ROLLBACK-{self._rollback_counter:06d}"

    def request_rollback(
        self,
        *,
        target: str,
        from_version: str,
        to_version: str,
        reason: str = "",
        metadata: Mapping[str, Any] | None = None,
    ) -> RollbackRecord:
        """
        Create a rollback request in PENDING state.
        """

        if not target or not target.strip():
            raise ValueError("target must not be empty")

        if not from_version or not from_version.strip():
            raise ValueError("from_version must not be empty")

        if not to_version or not to_version.strip():
            raise ValueError("to_version must not be empty")

        if from_version.strip() == to_version.strip():
            raise ValueError(
                "from_version and to_version must differ"
            )

        rollback_metadata = dict(self._metadata)
        rollback_metadata.update(metadata or {})

        record = RollbackRecord(
            rollback_id=self._next_rollback_id(),
            target=target.strip(),
            from_version=from_version.strip(),
            to_version=to_version.strip(),
            status="PENDING",
            reason=reason,
            metadata=rollback_metadata,
        )

        self._rollbacks[record.rollback_id] = record

        return record

    def complete_rollback(
        self,
        rollback: RollbackRecord,
        *,
        status: str = "COMPLETED",
        metadata: Mapping[str, Any] | None = None,
    ) -> RollbackRecord:
        """
        Close a rollback request with a final state.
        """

        self._validate_record(rollback)

        if rollback.is_completed():
            raise ValueError("rollback is already completed")

        final_status = status.strip().upper()

        if final_status not in {
            "COMPLETED",
            "SUCCESS",
            "FAILED",
            "CANCELLED",
        }:
            raise ValueError("invalid rollback completion status")

        updated_metadata = dict(rollback.metadata)
        updated_metadata.update(metadata or {})

        completed = RollbackRecord(
            rollback_id=rollback.rollback_id,
            target=rollback.target,
            from_version=rollback.from_version,
            to_version=rollback.to_version,
            status=final_status,
            reason=rollback.reason,
            requested_at=rollback.requested_at,
            completed_at=datetime.now(timezone.utc),
            metadata=updated_metadata,
        )

        self._rollbacks[completed.rollback_id] = completed

        return completed

    def cancel_rollback(
        self,
        rollback: RollbackRecord,
        *,
        reason: str | None = None,
    ) -> RollbackRecord:
        """
        Cancel a pending rollback request.
        """

        self._validate_record(rollback)

        if rollback.is_completed():
            raise ValueError(
                "completed rollback cannot be cancelled"
            )

        updated_metadata = dict(rollback.metadata)

        if reason:
            updated_metadata["cancellation_reason"] = reason

        cancelled = RollbackRecord(
            rollback_id=rollback.rollback_id,
            target=rollback.target,
            from_version=rollback.from_version,
            to_version=rollback.to_version,
            status="CANCELLED",
            reason=rollback.reason,
            requested_at=rollback.requested_at,
            completed_at=datetime.now(timezone.utc),
            metadata=updated_metadata,
        )

        self._rollbacks[cancelled.rollback_id] = cancelled

        return cancelled

    def get_rollback(
        self,
        rollback_id: str,
    ) -> RollbackRecord | None:
        """
        Retrieve a rollback record by identifier.
        """

        return self._rollbacks.get(rollback_id)

    def list_rollbacks(self) -> tuple[RollbackRecord, ...]:
        """
        Return all rollback records in creation order.
        """

        return tuple(self._rollbacks.values())

    def _validate_record(
        self,
        rollback: RollbackRecord,
    ) -> None:
        if not isinstance(rollback, RollbackRecord):
            raise TypeError(
                "rollback must be a RollbackRecord"
            )

        if not rollback.is_valid():
            raise ValueError("invalid rollback record")