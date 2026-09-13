from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping

from schemas.evidence.evidence_item import EvidenceItem


@dataclass(frozen=True)
class EvidencePackage:
    """
    Structured collection of evidence supporting an intelligence context.

    The package groups evidence items and provides a single canonical
    representation for downstream intelligence and decision layers.
    """

    package_id: str
    items: tuple[EvidenceItem, ...] = field(default_factory=tuple)

    market: str | None = None
    instrument_id: str | None = None
    timeframe: str | None = None

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation."""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["items"] = [item.to_dict() for item in self.items]
        data["metadata"] = dict(self.metadata)
        return data

    def is_valid(self) -> bool:
        """Return whether the evidence package is structurally valid."""
        if not self.package_id:
            return False

        return all(item.is_valid() for item in self.items)

    def add_item(self, item: EvidenceItem) -> "EvidencePackage":
        """Return a new package containing the supplied evidence item."""
        if not isinstance(item, EvidenceItem):
            raise TypeError("item must be an EvidenceItem")

        return EvidencePackage(
            package_id=self.package_id,
            items=self.items + (item,),
            market=self.market,
            instrument_id=self.instrument_id,
            timeframe=self.timeframe,
            created_at=self.created_at,
            metadata=dict(self.metadata),
        )

    def evidence_count(self) -> int:
        """Return the number of evidence items in the package."""
        return len(self.items)