from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class ValidationRecord:
    """
    Immutable record describing a ROBOMLM administrative validation.
    """

    validation_id: str
    target: str
    status: str

    version: str | None = None
    scope: str | None = None

    passed: bool | None = None
    checks: tuple[str, ...] = field(default_factory=tuple)
    failures: tuple[str, ...] = field(default_factory=tuple)

    started_at: datetime | None = None
    completed_at: datetime | None = None

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "validation_id": self.validation_id,
            "target": self.target,
            "status": self.status,
            "version": self.version,
            "scope": self.scope,
            "passed": self.passed,
            "checks": list(self.checks),
            "failures": list(self.failures),
            "started_at": (
                self.started_at.isoformat()
                if self.started_at is not None
                else None
            ),
            "completed_at": (
                self.completed_at.isoformat()
                if self.completed_at is not None
                else None
            ),
            "metadata": dict(self.metadata),
        }

    def is_running(self) -> bool:
        return self.status.upper() == "RUNNING"

    def is_completed(self) -> bool:
        return self.status.upper() in {
            "PASSED",
            "FAILED",
            "CANCELLED",
        }

    def is_valid(self) -> bool:
        if not self.validation_id:
            return False

        if not self.target:
            return False

        if not self.status:
            return False

        if (
            self.completed_at is not None
            and self.started_at is not None
            and self.completed_at < self.started_at
        ):
            return False

        if self.is_completed() and self.passed is None:
            return False

        return True


class ValidationAdmin:
    """
    Administrative lifecycle manager for controlled validations.

    This class manages validation identity, lifecycle state, checks,
    and failures. It does not execute the validation logic itself.
    """

    def __init__(
        self,
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        self._metadata: dict[str, Any] = dict(metadata or {})
        self._validation_counter = 0
        self._validations: dict[str, ValidationRecord] = {}

    @property
    def metadata(self) -> dict[str, Any]:
        return dict(self._metadata)

    def _next_validation_id(self) -> str:
        self._validation_counter += 1
        return f"VALIDATION-{self._validation_counter:06d}"

    def create_validation(
        self,
        *,
        target: str,
        version: str | None = None,
        scope: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ValidationRecord:
        """
        Create a new validation in PLANNED state.
        """

        if not target or not target.strip():
            raise ValueError("target must not be empty")

        validation_metadata = dict(self._metadata)
        validation_metadata.update(metadata or {})

        record = ValidationRecord(
            validation_id=self._next_validation_id(),
            target=target.strip(),
            status="PLANNED",
            version=version,
            scope=scope,
            metadata=validation_metadata,
        )

        self._validations[record.validation_id] = record

        return record

    def start_validation(
        self,
        validation: ValidationRecord,
    ) -> ValidationRecord:
        """
        Move a planned validation into RUNNING state.
        """

        self._validate_record(validation)

        if validation.is_running():
            raise ValueError("validation is already running")

        if validation.is_completed():
            raise ValueError(
                "completed validation cannot be started"
            )

        started = ValidationRecord(
            validation_id=validation.validation_id,
            target=validation.target,
            status="RUNNING",
            version=validation.version,
            scope=validation.scope,
            passed=None,
            checks=validation.checks,
            failures=validation.failures,
            started_at=datetime.now(timezone.utc),
            completed_at=None,
            metadata=dict(validation.metadata),
        )

        self._validations[started.validation_id] = started

        return started

    def add_check(
        self,
        validation: ValidationRecord,
        check: str,
    ) -> ValidationRecord:
        """
        Register a validation check.
        """

        self._validate_record(validation)

        if validation.is_completed():
            raise ValueError(
                "completed validation cannot be modified"
            )

        if not check or not check.strip():
            raise ValueError("check must not be empty")

        updated = ValidationRecord(
            validation_id=validation.validation_id,
            target=validation.target,
            status=validation.status,
            version=validation.version,
            scope=validation.scope,
            passed=validation.passed,
            checks=validation.checks + (check.strip(),),
            failures=validation.failures,
            started_at=validation.started_at,
            completed_at=validation.completed_at,
            metadata=dict(validation.metadata),
        )

        self._validations[updated.validation_id] = updated

        return updated

    def add_failure(
        self,
        validation: ValidationRecord,
        failure: str,
    ) -> ValidationRecord:
        """
        Register a validation failure.
        """

        self._validate_record(validation)

        if validation.is_completed():
            raise ValueError(
                "completed validation cannot be modified"
            )

        if not failure or not failure.strip():
            raise ValueError("failure must not be empty")

        updated = ValidationRecord(
            validation_id=validation.validation_id,
            target=validation.target,
            status=validation.status,
            version=validation.version,
            scope=validation.scope,
            passed=validation.passed,
            checks=validation.checks,
            failures=validation.failures + (failure.strip(),),
            started_at=validation.started_at,
            completed_at=validation.completed_at,
            metadata=dict(validation.metadata),
        )

        self._validations[updated.validation_id] = updated

        return updated

    def complete_validation(
        self,
        validation: ValidationRecord,
        *,
        passed: bool,
        metadata: Mapping[str, Any] | None = None,
    ) -> ValidationRecord:
        """
        Complete validation with an explicit pass/fail result.
        """

        self._validate_record(validation)

        if validation.is_completed():
            raise ValueError(
                "validation is already completed"
            )

        if validation.started_at is None:
            raise ValueError(
                "validation has not been started"
            )

        final_status = "PASSED" if passed else "FAILED"

        updated_metadata = dict(validation.metadata)
        updated_metadata.update(metadata or {})

        completed = ValidationRecord(
            validation_id=validation.validation_id,
            target=validation.target,
            status=final_status,
            version=validation.version,
            scope=validation.scope,
            passed=passed,
            checks=validation.checks,
            failures=validation.failures,
            started_at=validation.started_at,
            completed_at=datetime.now(timezone.utc),
            metadata=updated_metadata,
        )

        self._validations[completed.validation_id] = completed

        return completed

    def cancel_validation(
        self,
        validation: ValidationRecord,
        *,
        reason: str | None = None,
    ) -> ValidationRecord:
        """
        Cancel a planned or running validation.
        """

        self._validate_record(validation)

        if validation.is_completed():
            raise ValueError(
                "completed validation cannot be cancelled"
            )

        updated_metadata = dict(validation.metadata)

        if reason:
            updated_metadata["cancellation_reason"] = reason

        cancelled = ValidationRecord(
            validation_id=validation.validation_id,
            target=validation.target,
            status="CANCELLED",
            version=validation.version,
            scope=validation.scope,
            passed=False,
            checks=validation.checks,
            failures=validation.failures,
            started_at=validation.started_at,
            completed_at=datetime.now(timezone.utc),
            metadata=updated_metadata,
        )

        self._validations[cancelled.validation_id] = cancelled

        return cancelled

    def get_validation(
        self,
        validation_id: str,
    ) -> ValidationRecord | None:
        """
        Retrieve a validation by identifier.
        """

        return self._validations.get(validation_id)

    def list_validations(self) -> tuple[ValidationRecord, ...]:
        """
        Return all validations in creation order.
        """

        return tuple(self._validations.values())

    def _validate_record(
        self,
        validation: ValidationRecord,
    ) -> None:
        if not isinstance(validation, ValidationRecord):
            raise TypeError(
                "validation must be a ValidationRecord"
            )

        if not validation.is_valid():
            raise ValueError("invalid validation record")