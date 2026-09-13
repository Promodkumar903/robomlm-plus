"""
ROBOMLM PLUS
Evidence Database Model

Purpose:
    Define the persistent structure for evidence records used by
    the ROBOMLM Evidence Cortex.

Design:
    - Evidence is stored independently from decisions.
    - Supports source, observation, normalization, confidence,
      reliability and conflict metadata.
    - No decision-generation logic.
    - No market-data connection.
    - No execution logic.
    - Persistence is handled by repository/database layers.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Optional
from uuid import uuid4


@dataclass
class EvidenceRecord:
    """Structured ROBOMLM evidence record."""

    evidence_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    evidence_type: str = ""
    evidence_state: str = ""

    source: str = ""
    source_type: Optional[str] = None
    source_reliability: Optional[float] = None

    market: Optional[str] = None
    instrument: Optional[str] = None
    venue: Optional[str] = None
    timeframe: Optional[str] = None

    observation: Optional[str] = None
    value: Any = None
    unit: Optional[str] = None

    confidence: Optional[float] = None
    quality_score: Optional[float] = None

    observed_at: Optional[datetime] = None

    is_derived: bool = False
    derivation_method: Optional[str] = None
    parent_evidence_ids: list[str] = field(default_factory=list)

    conflict_group: Optional[str] = None
    conflict_status: Optional[str] = None

    metadata: dict[str, Any] = field(default_factory=dict)

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        """Normalize and validate evidence fields."""

        self.evidence_id = str(self.evidence_id).strip()

        if not self.evidence_id:
            raise ValueError("evidence_id cannot be empty.")

        self.evidence_type = str(self.evidence_type).strip()
        self.evidence_state = str(self.evidence_state).strip()
        self.source = str(self.source).strip()

        if self.source_type is not None:
            self.source_type = str(self.source_type).strip() or None

        if self.market is not None:
            self.market = str(self.market).strip() or None

        if self.instrument is not None:
            self.instrument = str(self.instrument).strip() or None

        if self.venue is not None:
            self.venue = str(self.venue).strip() or None

        if self.timeframe is not None:
            self.timeframe = str(self.timeframe).strip() or None

        if self.observation is not None:
            self.observation = str(self.observation)

        if self.unit is not None:
            self.unit = str(self.unit).strip() or None

        if self.derivation_method is not None:
            self.derivation_method = (
                str(self.derivation_method).strip() or None
            )

        if self.conflict_group is not None:
            self.conflict_group = (
                str(self.conflict_group).strip() or None
            )

        if self.conflict_status is not None:
            self.conflict_status = (
                str(self.conflict_status).strip() or None
            )

        self.parent_evidence_ids = [
            str(item).strip()
            for item in self.parent_evidence_ids
            if str(item).strip()
        ]

        if not isinstance(self.metadata, dict):
            self.metadata = dict(self.metadata)

        self.source_reliability = self._validate_score(
            self.source_reliability,
            "source_reliability",
        )

        self.confidence = self._validate_score(
            self.confidence,
            "confidence",
        )

        self.quality_score = self._validate_score(
            self.quality_score,
            "quality_score",
        )

        self.timestamp = self._normalize_datetime(
            self.timestamp
        )

        if self.observed_at is not None:
            self.observed_at = self._normalize_datetime(
                self.observed_at
            )

        self.created_at = self._normalize_datetime(
            self.created_at
        )

        self.updated_at = self._normalize_datetime(
            self.updated_at
        )

        if self.is_derived and not self.derivation_method:
            raise ValueError(
                "derivation_method is required for derived evidence."
            )

    @staticmethod
    def _validate_score(
        value: Optional[float],
        field_name: str,
    ) -> Optional[float]:
        """Validate a score represented on a 0-100 scale."""

        if value is None:
            return None

        if isinstance(value, bool):
            raise TypeError(
                f"{field_name} must be numeric, not boolean."
            )

        try:
            numeric_value = float(value)
        except (TypeError, ValueError) as exc:
            raise TypeError(
                f"{field_name} must be numeric."
            ) from exc

        if not 0.0 <= numeric_value <= 100.0:
            raise ValueError(
                f"{field_name} must be between 0 and 100."
            )

        return numeric_value

    @staticmethod
    def _normalize_datetime(
        value: datetime,
    ) -> datetime:
        """Ensure datetime values are timezone-aware UTC."""

        if not isinstance(value, datetime):
            raise TypeError(
                "Datetime value must be a datetime instance."
            )

        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)

    def touch(self) -> None:
        """Update the modification timestamp."""

        self.updated_at = datetime.now(timezone.utc)

    def add_parent_evidence(
        self,
        evidence_id: str,
    ) -> None:
        """Attach a parent evidence identifier."""

        evidence_id = str(evidence_id).strip()

        if not evidence_id:
            raise ValueError(
                "evidence_id cannot be empty."
            )

        if evidence_id not in self.parent_evidence_ids:
            self.parent_evidence_ids.append(evidence_id)

        self.touch()

    def remove_parent_evidence(
        self,
        evidence_id: str,
    ) -> bool:
        """Remove a parent evidence identifier."""

        evidence_id = str(evidence_id).strip()

        if evidence_id in self.parent_evidence_ids:
            self.parent_evidence_ids.remove(evidence_id)
            self.touch()
            return True

        return False

    def mark_derived(
        self,
        derivation_method: str,
    ) -> None:
        """Mark this evidence as derived."""

        derivation_method = str(
            derivation_method
        ).strip()

        if not derivation_method:
            raise ValueError(
                "derivation_method cannot be empty."
            )

        self.is_derived = True
        self.derivation_method = derivation_method
        self.touch()

    def set_conflict(
        self,
        conflict_group: str,
        conflict_status: str,
    ) -> None:
        """Assign conflict information."""

        conflict_group = str(
            conflict_group
        ).strip()

        conflict_status = str(
            conflict_status
        ).strip()

        if not conflict_group:
            raise ValueError(
                "conflict_group cannot be empty."
            )

        if not conflict_status:
            raise ValueError(
                "conflict_status cannot be empty."
            )

        self.conflict_group = conflict_group
        self.conflict_status = conflict_status
        self.touch()

    def clear_conflict(self) -> None:
        """Clear conflict information."""

        self.conflict_group = None
        self.conflict_status = None
        self.touch()

    def with_metadata(
        self,
        key: str,
        value: Any,
    ) -> "EvidenceRecord":
        """
        Return a copy with additional metadata.

        The original record is not modified.
        """

        key = str(key).strip()

        if not key:
            raise ValueError(
                "Metadata key cannot be empty."
            )

        copied_metadata = dict(self.metadata)
        copied_metadata[key] = value

        return EvidenceRecord(
            evidence_id=self.evidence_id,
            timestamp=self.timestamp,
            evidence_type=self.evidence_type,
            evidence_state=self.evidence_state,
            source=self.source,
            source_type=self.source_type,
            source_reliability=self.source_reliability,
            market=self.market,
            instrument=self.instrument,
            venue=self.venue,
            timeframe=self.timeframe,
            observation=self.observation,
            value=self.value,
            unit=self.unit,
            confidence=self.confidence,
            quality_score=self.quality_score,
            observed_at=self.observed_at,
            is_derived=self.is_derived,
            derivation_method=self.derivation_method,
            parent_evidence_ids=list(
                self.parent_evidence_ids
            ),
            conflict_group=self.conflict_group,
            conflict_status=self.conflict_status,
            metadata=copied_metadata,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable dictionary representation."""

        data = asdict(self)

        data["timestamp"] = self.timestamp.isoformat()
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()

        if self.observed_at is not None:
            data["observed_at"] = self.observed_at.isoformat()

        return data

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "EvidenceRecord":
        """Create an evidence record from a mapping."""

        if not isinstance(data, Mapping):
            raise TypeError(
                "data must be a mapping."
            )

        values = dict(data)

        for field_name in (
            "timestamp",
            "observed_at",
            "created_at",
            "updated_at",
        ):
            value = values.get(field_name)

            if isinstance(value, str):
                values[field_name] = (
                    datetime.fromisoformat(value)
                )

        return cls(**values)


def create_evidence_record(
    *,
    evidence_type: str,
    evidence_state: str,
    source: str,
    source_type: Optional[str] = None,
    source_reliability: Optional[float] = None,
    market: Optional[str] = None,
    instrument: Optional[str] = None,
    venue: Optional[str] = None,
    timeframe: Optional[str] = None,
    observation: Optional[str] = None,
    value: Any = None,
    unit: Optional[str] = None,
    confidence: Optional[float] = None,
    quality_score: Optional[float] = None,
    observed_at: Optional[datetime] = None,
    is_derived: bool = False,
    derivation_method: Optional[str] = None,
    parent_evidence_ids: Optional[list[str]] = None,
    conflict_group: Optional[str] = None,
    conflict_status: Optional[str] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> EvidenceRecord:
    """Convenience factory for creating evidence records."""

    return EvidenceRecord(
        evidence_type=evidence_type,
        evidence_state=evidence_state,
        source=source,
        source_type=source_type,
        source_reliability=source_reliability,
        market=market,
        instrument=instrument,
        venue=venue,
        timeframe=timeframe,
        observation=observation,
        value=value,
        unit=unit,
        confidence=confidence,
        quality_score=quality_score,
        observed_at=observed_at,
        is_derived=is_derived,
        derivation_method=derivation_method,
        parent_evidence_ids=list(
            parent_evidence_ids or []
        ),
        conflict_group=conflict_group,
        conflict_status=conflict_status,
        metadata=dict(metadata or {}),
    )


__all__ = [
    "EvidenceRecord",
    "create_evidence_record",
]