from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class DecisionResult:
    """
    Canonical decision produced by the ROBOMLM Decision layer.

    A DecisionResult represents the decision state derived from
    intelligence and supporting evidence. It does not execute orders.
    """

    decision_id: str
    decision: str
    status: str

    market: str | None = None
    instrument_id: str | None = None
    timeframe: str | None = None

    direction: str | None = None

    confidence: float | None = None
    score: float | None = None

    rationale: str | None = None

    evidence_ids: tuple[str, ...] = field(default_factory=tuple)
    intelligence_ids: tuple[str, ...] = field(default_factory=tuple)

    entry_allowed: bool = False
    execution_allowed: bool = False

    risk_level: str | None = None

    constraints: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    decided_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation."""
        data = asdict(self)

        data["decided_at"] = self.decided_at.isoformat()
        data["evidence_ids"] = list(self.evidence_ids)
        data["intelligence_ids"] = list(self.intelligence_ids)
        data["constraints"] = dict(self.constraints)
        data["metadata"] = dict(self.metadata)

        return data

    def is_valid(self) -> bool:
        """Return whether the decision result is structurally valid."""
        if not self.decision_id:
            return False

        if not self.decision:
            return False

        if not self.status:
            return False

        if self.confidence is not None:
            if not 0.0 <= self.confidence <= 100.0:
                return False

        if self.score is not None:
            if not 0.0 <= self.score <= 100.0:
                return False

        if self.execution_allowed and not self.entry_allowed:
            return False

        return True

    def is_actionable(self) -> bool:
        """
        Return whether the decision is explicitly permitted to proceed
        toward execution.
        """
        return (
            self.is_valid()
            and self.entry_allowed
            and self.execution_allowed
        )