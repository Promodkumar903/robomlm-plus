from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class IntelligenceResult:
    """
    Canonical result produced by the ROBOMLM Intelligence layer.

    The class carries intelligence as a structured result rather than
    embedding decision, execution, or broker-specific behavior.
    """

    result_id: str
    status: str
    intelligence_type: str

    summary: str = ""
    confidence: float | None = None

    market: str | None = None
    instrument: str | None = None
    timeframe: str | None = None

    direction: str | None = None
    bias: str | None = None

    evidence_ids: tuple[str, ...] = field(default_factory=tuple)
    context_ids: tuple[str, ...] = field(default_factory=tuple)

    observations: tuple[str, ...] = field(default_factory=tuple)
    insights: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)

    generated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation."""
        data = asdict(self)
        data["generated_at"] = self.generated_at.isoformat()
        data["evidence_ids"] = list(self.evidence_ids)
        data["context_ids"] = list(self.context_ids)
        data["observations"] = list(self.observations)
        data["insights"] = list(self.insights)
        data["warnings"] = list(self.warnings)
        data["metadata"] = dict(self.metadata)
        return data

    def is_valid(self) -> bool:
        """Return whether the core intelligence result is structurally valid."""
        if not self.result_id:
            return False

        if not self.status:
            return False

        if not self.intelligence_type:
            return False

        if self.confidence is not None:
            if not 0.0 <= self.confidence <= 100.0:
                return False

        return True