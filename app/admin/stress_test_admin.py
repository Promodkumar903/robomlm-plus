from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class StressTestRecord:
    """
    Immutable record describing a ROBOMLM stress-test lifecycle.
    """

    test_id: str
    name: str
    status: str

    target: str | None = None
    version: str | None = None
    scenario: str | None = None

    passed: bool | None = None
    findings: tuple[str, ...] = field(default_factory=tuple)

    started_at: datetime | None = None
    completed_at: datetime | None = None

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "test_id": self.test_id,
            "name": self.name,
            "status": self.status,
            "target": self.target,
            "version": self.version,
            "scenario": self.scenario,
            "passed": self.passed,
            "findings": list(self.findings),
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
        if not self.test_id:
            return False

        if not self.name:
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


class StressTestAdmin:
    """
    Administrative lifecycle manager for controlled stress tests.

    This class manages test identity, lifecycle state, and findings.
    It does not execute the actual stress-test workload.
    """

    def __init__(
        self,
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        self._metadata: dict[str, Any] = dict(metadata or {})
        self._test_counter = 0
        self._tests: dict[str, StressTestRecord] = {}

    @property
    def metadata(self) -> dict[str, Any]:
        return dict(self._metadata)

    def _next_test_id(self) -> str:
        self._test_counter += 1
        return f"STRESS-{self._test_counter:06d}"

    def create_test(
        self,
        *,
        name: str,
        target: str | None = None,
        version: str | None = None,
        scenario: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> StressTestRecord:
        """
        Create a new stress test in PLANNED state.
        """

        if not name or not name.strip():
            raise ValueError("name must not be empty")

        test_metadata = dict(self._metadata)
        test_metadata.update(metadata or {})

        record = StressTestRecord(
            test_id=self._next_test_id(),
            name=name.strip(),
            status="PLANNED",
            target=target,
            version=version,
            scenario=scenario,
            metadata=test_metadata,
        )

        self._tests[record.test_id] = record

        return record

    def start_test(
        self,
        test: StressTestRecord,
    ) -> StressTestRecord:
        """
        Move a planned stress test into RUNNING state.
        """

        self._validate_record(test)

        if test.is_running():
            raise ValueError("stress test is already running")

        if test.is_completed():
            raise ValueError("completed stress test cannot be started")

        started = StressTestRecord(
            test_id=test.test_id,
            name=test.name,
            status="RUNNING",
            target=test.target,
            version=test.version,
            scenario=test.scenario,
            passed=None,
            findings=test.findings,
            started_at=datetime.now(timezone.utc),
            completed_at=None,
            metadata=dict(test.metadata),
        )

        self._tests[started.test_id] = started

        return started

    def add_finding(
        self,
        test: StressTestRecord,
        finding: str,
    ) -> StressTestRecord:
        """
        Append a finding to a non-completed stress test.
        """

        self._validate_record(test)

        if test.is_completed():
            raise ValueError(
                "completed stress test cannot be modified"
            )

        if not finding or not finding.strip():
            raise ValueError("finding must not be empty")

        updated = StressTestRecord(
            test_id=test.test_id,
            name=test.name,
            status=test.status,
            target=test.target,
            version=test.version,
            scenario=test.scenario,
            passed=test.passed,
            findings=test.findings + (finding.strip(),),
            started_at=test.started_at,
            completed_at=test.completed_at,
            metadata=dict(test.metadata),
        )

        self._tests[updated.test_id] = updated

        return updated

    def complete_test(
        self,
        test: StressTestRecord,
        *,
        passed: bool,
        metadata: Mapping[str, Any] | None = None,
    ) -> StressTestRecord:
        """
        Complete a stress test with an explicit pass/fail result.
        """

        self._validate_record(test)

        if test.is_completed():
            raise ValueError("stress test is already completed")

        if test.started_at is None:
            raise ValueError("stress test has not been started")

        final_status = "PASSED" if passed else "FAILED"

        updated_metadata = dict(test.metadata)
        updated_metadata.update(metadata or {})

        completed = StressTestRecord(
            test_id=test.test_id,
            name=test.name,
            status=final_status,
            target=test.target,
            version=test.version,
            scenario=test.scenario,
            passed=passed,
            findings=test.findings,
            started_at=test.started_at,
            completed_at=datetime.now(timezone.utc),
            metadata=updated_metadata,
        )

        self._tests[completed.test_id] = completed

        return completed

    def cancel_test(
        self,
        test: StressTestRecord,
        *,
        reason: str | None = None,
    ) -> StressTestRecord:
        """
        Cancel a planned or running stress test.
        """

        self._validate_record(test)

        if test.is_completed():
            raise ValueError(
                "completed stress test cannot be cancelled"
            )

        updated_metadata = dict(test.metadata)

        if reason:
            updated_metadata["cancellation_reason"] = reason

        cancelled = StressTestRecord(
            test_id=test.test_id,
            name=test.name,
            status="CANCELLED",
            target=test.target,
            version=test.version,
            scenario=test.scenario,
            passed=False,
            findings=test.findings,
            started_at=test.started_at,
            completed_at=datetime.now(timezone.utc),
            metadata=updated_metadata,
        )

        self._tests[cancelled.test_id] = cancelled

        return cancelled

    def get_test(
        self,
        test_id: str,
    ) -> StressTestRecord | None:
        """
        Retrieve a stress test by identifier.
        """

        return self._tests.get(test_id)

    def list_tests(self) -> tuple[StressTestRecord, ...]:
        """
        Return all stress tests in creation order.
        """

        return tuple(self._tests.values())

    def _validate_record(
        self,
        test: StressTestRecord,
    ) -> None:
        if not isinstance(test, StressTestRecord):
            raise TypeError(
                "test must be a StressTestRecord"
            )

        if not test.is_valid():
            raise ValueError("invalid stress test record")