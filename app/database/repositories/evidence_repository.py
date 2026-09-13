"""
ROBOMLM PLUS
Evidence Repository

Purpose:
    Provide persistence operations for EvidenceRecord objects.

Design:
    - Repository layer only.
    - No evidence generation or intelligence logic.
    - No trading or execution side effects.
    - Uses JSONL storage for the initial implementation.
    - Preserves observed/derived evidence structure.
    - Keeps evidence persistence isolated from the Evidence Cortex.
"""

from __future__ import annotations

import json
from pathlib import Path
from threading import RLock
from typing import Any, Iterable, Optional

from app.database.models.evidence_model import (
    EvidenceRecord,
)


class EvidenceRepositoryError(Exception):
    """Base exception for evidence repository errors."""


class EvidenceNotFoundError(EvidenceRepositoryError):
    """Raised when a requested evidence record does not exist."""


class EvidenceRepository:
    """Persistent repository for evidence records."""

    FILE_NAME = "evidence.jsonl"

    def __init__(
        self,
        storage_dir: Optional[str | Path] = None,
    ) -> None:
        if storage_dir is None:
            storage_dir = (
                Path(__file__).resolve().parents[3]
                / "robomlm_data"
                / "evidence"
            )

        self.storage_dir = Path(storage_dir)
        self.file_path = (
            self.storage_dir / self.FILE_NAME
        )

        self._lock = RLock()

        self._ensure_storage()

    def _ensure_storage(self) -> None:
        """Create repository storage if required."""

        try:
            self.storage_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            if not self.file_path.exists():
                self.file_path.touch()

        except OSError as exc:
            raise EvidenceRepositoryError(
                f"Unable to initialize evidence storage: {exc}"
            ) from exc

    def _append_record(
        self,
        record: EvidenceRecord,
    ) -> None:
        """Append an evidence record to JSONL storage."""

        try:
            with self.file_path.open(
                "a",
                encoding="utf-8",
            ) as handle:
                handle.write(
                    json.dumps(
                        record.to_dict(),
                        ensure_ascii=False,
                        separators=(",", ":"),
                    )
                    + "\n"
                )

        except OSError as exc:
            raise EvidenceRepositoryError(
                f"Unable to write evidence record: {exc}"
            ) from exc

        except (TypeError, ValueError) as exc:
            raise EvidenceRepositoryError(
                f"Unable to serialize evidence record: {exc}"
            ) from exc

    def _read_all(
        self,
    ) -> list[EvidenceRecord]:
        """Read all stored evidence records."""

        records: list[EvidenceRecord] = []

        if not self.file_path.exists():
            return records

        try:
            with self.file_path.open(
                "r",
                encoding="utf-8",
            ) as handle:

                for line_number, line in enumerate(
                    handle,
                    start=1,
                ):
                    line = line.strip()

                    if not line:
                        continue

                    try:
                        payload = json.loads(line)

                        records.append(
                            EvidenceRecord.from_dict(
                                payload
                            )
                        )

                    except (
                        json.JSONDecodeError,
                        TypeError,
                        ValueError,
                    ) as exc:
                        raise EvidenceRepositoryError(
                            "Invalid evidence record at "
                            f"line {line_number}: {exc}"
                        ) from exc

        except OSError as exc:
            raise EvidenceRepositoryError(
                f"Unable to read evidence storage: {exc}"
            ) from exc

        return records

    def _rewrite(
        self,
        records: Iterable[EvidenceRecord],
    ) -> None:
        """Rewrite repository storage through a temporary file."""

        temp_path = (
            self.storage_dir
            / f"{self.FILE_NAME}.tmp"
        )

        try:
            with temp_path.open(
                "w",
                encoding="utf-8",
            ) as handle:

                for record in records:
                    handle.write(
                        json.dumps(
                            record.to_dict(),
                            ensure_ascii=False,
                            separators=(",", ":"),
                        )
                        + "\n"
                    )

            temp_path.replace(
                self.file_path
            )

        except OSError as exc:
            try:
                if temp_path.exists():
                    temp_path.unlink()
            except OSError:
                pass

            raise EvidenceRepositoryError(
                f"Unable to rewrite evidence storage: {exc}"
            ) from exc

    def save(
        self,
        record: EvidenceRecord,
    ) -> EvidenceRecord:
        """Persist a new evidence record."""

        if not isinstance(
            record,
            EvidenceRecord,
        ):
            raise TypeError(
                "record must be an EvidenceRecord."
            )

        with self._lock:
            self._append_record(record)

        return record

    def create(
        self,
        record: EvidenceRecord,
    ) -> EvidenceRecord:
        """Alias for save()."""

        return self.save(record)

    def get_by_id(
        self,
        evidence_id: str,
    ) -> Optional[EvidenceRecord]:
        """Return evidence by ID."""

        evidence_id = str(
            evidence_id
        ).strip()

        if not evidence_id:
            raise ValueError(
                "evidence_id cannot be empty."
            )

        with self._lock:
            records = self._read_all()

        for record in reversed(records):
            if record.evidence_id == evidence_id:
                return record

        return None

    def require_by_id(
        self,
        evidence_id: str,
    ) -> EvidenceRecord:
        """Return evidence or raise if it does not exist."""

        record = self.get_by_id(
            evidence_id
        )

        if record is None:
            raise EvidenceNotFoundError(
                f"Evidence not found: {evidence_id}"
            )

        return record

    def exists(
        self,
        evidence_id: str,
    ) -> bool:
        """Check whether evidence exists."""

        return (
            self.get_by_id(evidence_id)
            is not None
        )

    def list_all(
        self,
    ) -> list[EvidenceRecord]:
        """Return all evidence records."""

        with self._lock:
            return self._read_all()

    def count(self) -> int:
        """Return the total number of evidence records."""

        with self._lock:
            return len(
                self._read_all()
            )

    def find_by_user(
        self,
        user_id: str,
    ) -> list[EvidenceRecord]:
        """Return evidence associated with a user."""

        user_id = str(
            user_id
        ).strip()

        if not user_id:
            raise ValueError(
                "user_id cannot be empty."
            )

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if record.user_id == user_id
        ]

    def find_by_market(
        self,
        market: str,
    ) -> list[EvidenceRecord]:
        """Return evidence for a market."""

        market = str(
            market
        ).strip()

        if not market:
            raise ValueError(
                "market cannot be empty."
            )

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if record.market == market
        ]

    def find_by_instrument(
        self,
        instrument: str,
    ) -> list[EvidenceRecord]:
        """Return evidence for an instrument."""

        instrument = str(
            instrument
        ).strip()

        if not instrument:
            raise ValueError(
                "instrument cannot be empty."
            )

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if record.instrument == instrument
        ]

    def find_by_venue(
        self,
        venue: str,
    ) -> list[EvidenceRecord]:
        """Return evidence for a venue."""

        venue = str(
            venue
        ).strip()

        if not venue:
            raise ValueError(
                "venue cannot be empty."
            )

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if record.venue == venue
        ]

    def find_by_type(
        self,
        evidence_type: str,
    ) -> list[EvidenceRecord]:
        """Return evidence of a specific type."""

        evidence_type = str(
            evidence_type
        ).strip()

        if not evidence_type:
            raise ValueError(
                "evidence_type cannot be empty."
            )

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if record.evidence_type
            == evidence_type
        ]

    def find_by_state(
        self,
        state: str,
    ) -> list[EvidenceRecord]:
        """Return evidence in a specific state."""

        state = str(
            state
        ).strip().lower()

        if not state:
            raise ValueError(
                "state cannot be empty."
            )

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if record.state.lower() == state
        ]

    def find_by_source(
        self,
        source: str,
    ) -> list[EvidenceRecord]:
        """Return evidence produced by a source."""

        source = str(
            source
        ).strip()

        if not source:
            raise ValueError(
                "source cannot be empty."
            )

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if record.source == source
        ]

    def find_by_timeframe(
        self,
        timeframe: str,
    ) -> list[EvidenceRecord]:
        """Return evidence for a timeframe."""

        timeframe = str(
            timeframe
        ).strip()

        if not timeframe:
            raise ValueError(
                "timeframe cannot be empty."
            )

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if record.timeframe == timeframe
        ]

    def find_derived(
        self,
    ) -> list[EvidenceRecord]:
        """Return derived evidence records."""

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if record.is_derived
        ]

    def find_observed(
        self,
    ) -> list[EvidenceRecord]:
        """Return directly observed evidence."""

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if not record.is_derived
        ]

    def find_by_conflict_group(
        self,
        conflict_group: str,
    ) -> list[EvidenceRecord]:
        """Return evidence belonging to a conflict group."""

        conflict_group = str(
            conflict_group
        ).strip()

        if not conflict_group:
            raise ValueError(
                "conflict_group cannot be empty."
            )

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if record.conflict_group
            == conflict_group
        ]

    def find_conflicted(
        self,
    ) -> list[EvidenceRecord]:
        """Return evidence records marked as conflicted."""

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if record.conflict_status
            in {
                "conflict",
                "conflicted",
            }
        ]

    def find_by_reliability_range(
        self,
        minimum: float = 0.0,
        maximum: float = 100.0,
    ) -> list[EvidenceRecord]:
        """Return evidence within a source-reliability range."""

        minimum = float(minimum)
        maximum = float(maximum)

        if minimum > maximum:
            raise ValueError(
                "minimum cannot exceed maximum."
            )

        if minimum < 0 or maximum > 100:
            raise ValueError(
                "Reliability range must be between 0 and 100."
            )

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if minimum
            <= record.source_reliability
            <= maximum
        ]

    def find_by_confidence_range(
        self,
        minimum: float = 0.0,
        maximum: float = 100.0,
    ) -> list[EvidenceRecord]:
        """Return evidence within a confidence range."""

        minimum = float(minimum)
        maximum = float(maximum)

        if minimum > maximum:
            raise ValueError(
                "minimum cannot exceed maximum."
            )

        if minimum < 0 or maximum > 100:
            raise ValueError(
                "Confidence range must be between 0 and 100."
            )

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if minimum
            <= record.confidence
            <= maximum
        ]

    def find_by_quality_range(
        self,
        minimum: float = 0.0,
        maximum: float = 100.0,
    ) -> list[EvidenceRecord]:
        """Return evidence within a quality-score range."""

        minimum = float(minimum)
        maximum = float(maximum)

        if minimum > maximum:
            raise ValueError(
                "minimum cannot exceed maximum."
            )

        if minimum < 0 or maximum > 100:
            raise ValueError(
                "Quality range must be between 0 and 100."
            )

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if minimum
            <= record.quality
            <= maximum
        ]

    def find_by_parent(
        self,
        parent_evidence_id: str,
    ) -> list[EvidenceRecord]:
        """Return derived evidence linked to a parent."""

        parent_evidence_id = str(
            parent_evidence_id
        ).strip()

        if not parent_evidence_id:
            raise ValueError(
                "parent_evidence_id cannot be empty."
            )

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if parent_evidence_id
            in record.parent_evidence_ids
        ]

    def latest(
        self,
        limit: int = 10,
    ) -> list[EvidenceRecord]:
        """Return the latest evidence records."""

        limit = int(limit)

        if limit <= 0:
            raise ValueError(
                "limit must be greater than zero."
            )

        with self._lock:
            records = self._read_all()

        records.sort(
            key=lambda record: record.observed_at
        )

        return records[-limit:][::-1]

    def replace(
        self,
        record: EvidenceRecord,
    ) -> EvidenceRecord:
        """Replace an existing evidence record."""

        if not isinstance(
            record,
            EvidenceRecord,
        ):
            raise TypeError(
                "record must be an EvidenceRecord."
            )

        with self._lock:
            records = self._read_all()

            found = False
            updated_records: list[
                EvidenceRecord
            ] = []

            for existing in records:
                if (
                    existing.evidence_id
                    == record.evidence_id
                ):
                    updated_records.append(
                        record
                    )
                    found = True
                else:
                    updated_records.append(
                        existing
                    )

            if not found:
                raise EvidenceNotFoundError(
                    f"Evidence not found: "
                    f"{record.evidence_id}"
                )

            self._rewrite(
                updated_records
            )

        return record

    def add_parent(
        self,
        evidence_id: str,
        parent_evidence_id: str,
    ) -> EvidenceRecord:
        """Attach a parent evidence ID."""

        record = self.require_by_id(
            evidence_id
        )

        record.add_parent_evidence(
            parent_evidence_id
        )

        return self.replace(
            record
        )

    def update_conflict_status(
        self,
        evidence_id: str,
        conflict_status: str,
    ) -> EvidenceRecord:
        """Update conflict status."""

        record = self.require_by_id(
            evidence_id
        )

        record.set_conflict_status(
            conflict_status
        )

        return self.replace(
            record
        )

    def delete(
        self,
        evidence_id: str,
    ) -> bool:
        """
        Delete an evidence record.

        Intended for administrative/data-maintenance use.
        """

        evidence_id = str(
            evidence_id
        ).strip()

        if not evidence_id:
            raise ValueError(
                "evidence_id cannot be empty."
            )

        with self._lock:
            records = self._read_all()

            remaining = [
                record
                for record in records
                if record.evidence_id
                != evidence_id
            ]

            if len(remaining) == len(records):
                return False

            self._rewrite(
                remaining
            )

            return True

    def clear(self) -> None:
        """
        Clear all evidence records.

        Destructive administrative operation.
        """

        with self._lock:
            self._rewrite([])


evidence_repository = EvidenceRepository()


def get_evidence_repository() -> EvidenceRepository:
    """Return the global evidence repository."""

    return evidence_repository


__all__ = [
    "EvidenceRepositoryError",
    "EvidenceNotFoundError",
    "EvidenceRepository",
    "evidence_repository",
    "get_evidence_repository",
]