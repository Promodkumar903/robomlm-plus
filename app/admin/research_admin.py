from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class ResearchRecord:
    """
    Immutable record describing an administrative research activity.
    """

    research_id: str
    title: str
    status: str

    objective: str = ""
    target: str | None = None
    version: str | None = None

    findings: tuple[str, ...] = field(default_factory=tuple)
    conclusions: tuple[str, ...] = field(default_factory=tuple)

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    completed_at: datetime | None = None

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "research_id": self.research_id,
            "title": self.title,
            "status": self.status,
            "objective": self.objective,
            "target": self.target,
            "version": self.version,
            "findings": list(self.findings),
            "conclusions": list(self.conclusions),
            "created_at": self.created_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat()
                if self.completed_at is not None
                else None
            ),
            "metadata": dict(self.metadata),
        }

    def is_active(self) -> bool:
        return self.status.upper() in {
            "PLANNED",
            "RUNNING",
            "ACTIVE",
        }

    def is_completed(self) -> bool:
        return self.status.upper() in {
            "COMPLETED",
            "CANCELLED",
            "FAILED",
        }

    def is_valid(self) -> bool:
        if not self.research_id:
            return False

        if not self.title:
            return False

        if not self.status:
            return False

        if (
            self.completed_at is not None
            and self.completed_at < self.created_at
        ):
            return False

        return True


class ResearchAdmin:
    """
    Administrative lifecycle manager for controlled research activities.

    This class manages research identity, state, findings, and conclusions.
    It does not perform the underlying research itself.
    """

    def __init__(
        self,
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        self._metadata: dict[str, Any] = dict(metadata or {})
        self._research_counter = 0
        self._research: dict[str, ResearchRecord] = {}

    @property
    def metadata(self) -> dict[str, Any]:
        return dict(self._metadata)

    def _next_research_id(self) -> str:
        self._research_counter += 1
        return f"RESEARCH-{self._research_counter:06d}"

    def create_research(
        self,
        *,
        title: str,
        objective: str = "",
        target: str | None = None,
        version: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ResearchRecord:
        """
        Create a new research activity in PLANNED state.
        """

        if not title or not title.strip():
            raise ValueError("title must not be empty")

        research_metadata = dict(self._metadata)
        research_metadata.update(metadata or {})

        record = ResearchRecord(
            research_id=self._next_research_id(),
            title=title.strip(),
            status="PLANNED",
            objective=objective,
            target=target,
            version=version,
            metadata=research_metadata,
        )

        self._research[record.research_id] = record

        return record

    def start_research(
        self,
        research: ResearchRecord,
    ) -> ResearchRecord:
        """
        Move a planned research activity into RUNNING state.
        """

        self._validate_record(research)

        if research.is_active() and research.status.upper() == "RUNNING":
            raise ValueError("research is already running")

        if research.is_completed():
            raise ValueError("completed research cannot be started")

        started = ResearchRecord(
            research_id=research.research_id,
            title=research.title,
            status="RUNNING",
            objective=research.objective,
            target=research.target,
            version=research.version,
            findings=research.findings,
            conclusions=research.conclusions,
            created_at=research.created_at,
            completed_at=None,
            metadata=dict(research.metadata),
        )

        self._research[started.research_id] = started

        return started

    def add_finding(
        self,
        research: ResearchRecord,
        finding: str,
    ) -> ResearchRecord:
        """
        Append a validated finding to an active research activity.
        """

        self._validate_record(research)

        if research.is_completed():
            raise ValueError("completed research cannot be modified")

        if not finding or not finding.strip():
            raise ValueError("finding must not be empty")

        updated = ResearchRecord(
            research_id=research.research_id,
            title=research.title,
            status=research.status,
            objective=research.objective,
            target=research.target,
            version=research.version,
            findings=research.findings + (finding.strip(),),
            conclusions=research.conclusions,
            created_at=research.created_at,
            completed_at=research.completed_at,
            metadata=dict(research.metadata),
        )

        self._research[updated.research_id] = updated

        return updated

    def add_conclusion(
        self,
        research: ResearchRecord,
        conclusion: str,
    ) -> ResearchRecord:
        """
        Append a validated conclusion to an active research activity.
        """

        self._validate_record(research)

        if research.is_completed():
            raise ValueError("completed research cannot be modified")

        if not conclusion or not conclusion.strip():
            raise ValueError("conclusion must not be empty")

        updated = ResearchRecord(
            research_id=research.research_id,
            title=research.title,
            status=research.status,
            objective=research.objective,
            target=research.target,
            version=research.version,
            findings=research.findings,
            conclusions=research.conclusions + (conclusion.strip(),),
            created_at=research.created_at,
            completed_at=research.completed_at,
            metadata=dict(research.metadata),
        )

        self._research[updated.research_id] = updated

        return updated

    def complete_research(
        self,
        research: ResearchRecord,
        *,
        status: str = "COMPLETED",
        metadata: Mapping[str, Any] | None = None,
    ) -> ResearchRecord:
        """
        Complete a research activity with a final lifecycle status.
        """

        self._validate_record(research)

        if research.is_completed():
            raise ValueError("research is already completed")

        final_status = status.strip().upper()

        if final_status not in {
            "COMPLETED",
            "FAILED",
            "CANCELLED",
        }:
            raise ValueError("invalid completion status")

        updated_metadata = dict(research.metadata)
        updated_metadata.update(metadata or {})

        completed = ResearchRecord(
            research_id=research.research_id,
            title=research.title,
            status=final_status,
            objective=research.objective,
            target=research.target,
            version=research.version,
            findings=research.findings,
            conclusions=research.conclusions,
            created_at=research.created_at,
            completed_at=datetime.now(timezone.utc),
            metadata=updated_metadata,
        )

        self._research[completed.research_id] = completed

        return completed

    def get_research(
        self,
        research_id: str,
    ) -> ResearchRecord | None:
        """
        Retrieve research by identifier.
        """

        return self._research.get(research_id)

    def list_research(self) -> tuple[ResearchRecord, ...]:
        """
        Return all research activities in creation order.
        """

        return tuple(self._research.values())

    def _validate_record(
        self,
        research: ResearchRecord,
    ) -> None:
        if not isinstance(research, ResearchRecord):
            raise TypeError(
                "research must be a ResearchRecord"
            )

        if not research.is_valid():
            raise ValueError("invalid research record")