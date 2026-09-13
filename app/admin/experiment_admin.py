from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class ExperimentRecord:
    """
    Immutable record describing a ROBOMLM administrative experiment.
    """

    experiment_id: str
    name: str
    status: str

    description: str = ""
    hypothesis: str | None = None
    target: str | None = None
    version: str | None = None

    started_at: datetime | None = None
    completed_at: datetime | None = None

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "name": self.name,
            "status": self.status,
            "description": self.description,
            "hypothesis": self.hypothesis,
            "target": self.target,
            "version": self.version,
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
        return self.status.upper() in {
            "RUNNING",
            "ACTIVE",
        }

    def is_completed(self) -> bool:
        return self.status.upper() in {
            "COMPLETED",
            "PASSED",
            "FAILED",
            "CANCELLED",
        }

    def is_valid(self) -> bool:
        if not self.experiment_id:
            return False

        if not self.name:
            return False

        if not self.status:
            return False

        if (
            self.started_at is not None
            and self.completed_at is not None
            and self.completed_at < self.started_at
        ):
            return False

        return True


class ExperimentAdmin:
    """
    Administrative lifecycle manager for controlled experiments.

    This class manages experiment identity and lifecycle state.
    It does not execute experiment logic itself.
    """

    def __init__(
        self,
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        self._metadata: dict[str, Any] = dict(metadata or {})
        self._experiment_counter = 0
        self._experiments: dict[str, ExperimentRecord] = {}

    @property
    def metadata(self) -> dict[str, Any]:
        return dict(self._metadata)

    def _next_experiment_id(self) -> str:
        self._experiment_counter += 1
        return f"EXPERIMENT-{self._experiment_counter:06d}"

    def create_experiment(
        self,
        *,
        name: str,
        description: str = "",
        hypothesis: str | None = None,
        target: str | None = None,
        version: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ExperimentRecord:
        """
        Create a new experiment in PLANNED state.
        """

        if not name or not name.strip():
            raise ValueError("name must not be empty")

        experiment_metadata = dict(self._metadata)
        experiment_metadata.update(metadata or {})

        record = ExperimentRecord(
            experiment_id=self._next_experiment_id(),
            name=name.strip(),
            status="PLANNED",
            description=description,
            hypothesis=hypothesis,
            target=target,
            version=version,
            metadata=experiment_metadata,
        )

        self._experiments[record.experiment_id] = record

        return record

    def start_experiment(
        self,
        experiment: ExperimentRecord,
    ) -> ExperimentRecord:
        """
        Move an experiment into RUNNING state.
        """

        self._validate_record(experiment)

        if experiment.is_running():
            raise ValueError("experiment is already running")

        if experiment.is_completed():
            raise ValueError("completed experiment cannot be started")

        started = ExperimentRecord(
            experiment_id=experiment.experiment_id,
            name=experiment.name,
            status="RUNNING",
            description=experiment.description,
            hypothesis=experiment.hypothesis,
            target=experiment.target,
            version=experiment.version,
            started_at=datetime.now(timezone.utc),
            completed_at=None,
            metadata=dict(experiment.metadata),
        )

        self._experiments[started.experiment_id] = started

        return started

    def complete_experiment(
        self,
        experiment: ExperimentRecord,
        *,
        status: str = "COMPLETED",
        metadata: Mapping[str, Any] | None = None,
    ) -> ExperimentRecord:
        """
        Complete an experiment with a final lifecycle status.
        """

        self._validate_record(experiment)

        if not experiment.started_at:
            raise ValueError("experiment has not been started")

        final_status = status.strip().upper()

        if final_status not in {
            "COMPLETED",
            "PASSED",
            "FAILED",
            "CANCELLED",
        }:
            raise ValueError(
                "invalid completion status"
            )

        updated_metadata = dict(experiment.metadata)
        updated_metadata.update(metadata or {})

        completed = ExperimentRecord(
            experiment_id=experiment.experiment_id,
            name=experiment.name,
            status=final_status,
            description=experiment.description,
            hypothesis=experiment.hypothesis,
            target=experiment.target,
            version=experiment.version,
            started_at=experiment.started_at,
            completed_at=datetime.now(timezone.utc),
            metadata=updated_metadata,
        )

        self._experiments[completed.experiment_id] = completed

        return completed

    def cancel_experiment(
        self,
        experiment: ExperimentRecord,
        *,
        reason: str | None = None,
    ) -> ExperimentRecord:
        """
        Cancel a planned or running experiment.
        """

        self._validate_record(experiment)

        if experiment.is_completed():
            raise ValueError("completed experiment cannot be cancelled")

        metadata = dict(experiment.metadata)

        if reason:
            metadata["cancellation_reason"] = reason

        cancelled = ExperimentRecord(
            experiment_id=experiment.experiment_id,
            name=experiment.name,
            status="CANCELLED",
            description=experiment.description,
            hypothesis=experiment.hypothesis,
            target=experiment.target,
            version=experiment.version,
            started_at=experiment.started_at,
            completed_at=datetime.now(timezone.utc),
            metadata=metadata,
        )

        self._experiments[cancelled.experiment_id] = cancelled

        return cancelled

    def get_experiment(
        self,
        experiment_id: str,
    ) -> ExperimentRecord | None:
        """
        Retrieve an experiment by its identifier.
        """

        return self._experiments.get(experiment_id)

    def list_experiments(self) -> tuple[ExperimentRecord, ...]:
        """
        Return all known experiments in creation order.
        """

        return tuple(self._experiments.values())

    def _validate_record(
        self,
        experiment: ExperimentRecord,
    ) -> None:
        if not isinstance(experiment, ExperimentRecord):
            raise TypeError(
                "experiment must be an ExperimentRecord"
            )

        if not experiment.is_valid():
            raise ValueError("invalid experiment record")