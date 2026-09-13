from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class EvidenceItem:
    """
    Canonical unit of evidence used by ROBOMLM intelligence.

    Evidence describes an observed or derived fact. It does not itself
    make a trading decision or perform execution.
    """

    evidence_id: str
    evidence_type: str
    source: str

    value: Any = None
    observed_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    market: str | None = None
    instrument_id: str | None = None
    timeframe: str | None = None

    confidence: float | None = None
    quality: str | None = None

    description: str | None = None

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation."""
        data = asdict(self)
        data["observed_at"] = self.observed_at.isoformat()
        data["metadata"] = dict(self.metadata)
        return data

    def is_valid(self) -> bool:
        """Return whether the evidence item is structurally valid."""
        if not self.evidence_id:
            return False

        if not self.evidence_type:
            return False

        if not self.source:
            return False

        if self.confidence is not None:
            if not 0.0 <= self.confidence <= 100.0:
                return False

        return True