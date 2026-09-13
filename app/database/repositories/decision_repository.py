"""
ROBOMLM PLUS
Decision Repository

Purpose:
    Provide persistence operations for DecisionRecord objects.

Design:
    - Repository layer only.
    - No intelligence generation.
    - No trading or execution side effects.
    - Uses JSONL storage for the initial implementation.
    - Keeps storage logic isolated from decision models/services.
"""

from __future__ import annotations

import json
from pathlib import Path
from threading import RLock
from typing import Any, Iterable, Optional

from app.database.models.decision_model import (
    DecisionRecord,
)


class DecisionRepositoryError(Exception):
    """Base exception for decision repository errors."""


class DecisionNotFoundError(DecisionRepositoryError):
    """Raised when a requested decision does not exist."""


class DecisionRepository:
    """Persistent repository for decision records."""

    FILE_NAME = "decisions.jsonl"

    def __init__(
        self,
        storage_dir: Optional[str | Path] = None,
    ) -> None:
        if storage_dir is None:
            storage_dir = (
                Path(__file__).resolve().parents[3]
                / "robomlm_data"
                / "decisions"
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
            raise DecisionRepositoryError(
                f"Unable to initialize decision storage: {exc}"
            ) from exc

    def _append_record(
        self,
        record: DecisionRecord,
    ) -> None:
        """Append a decision record to JSONL storage."""

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
            raise DecisionRepositoryError(
                f"Unable to write decision record: {exc}"
            ) from exc

        except (TypeError, ValueError) as exc:
            raise DecisionRepositoryError(
                f"Unable to serialize decision record: {exc}"
            ) from exc

    def _read_all(
        self,
    ) -> list[DecisionRecord]:
        """Read all valid decision records."""

        records: list[DecisionRecord] = []

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
                            DecisionRecord.from_dict(
                                payload
                            )
                        )

                    except (
                        json.JSONDecodeError,
                        TypeError,
                        ValueError,
                    ) as exc:
                        raise DecisionRepositoryError(
                            "Invalid decision record at "
                            f"line {line_number}: {exc}"
                        ) from exc

        except OSError as exc:
            raise DecisionRepositoryError(
                f"Unable to read decision storage: {exc}"
            ) from exc

        return records

    def save(
        self,
        record: DecisionRecord,
    ) -> DecisionRecord:
        """Persist a new decision record."""

        if not isinstance(
            record,
            DecisionRecord,
        ):
            raise TypeError(
                "record must be a DecisionRecord."
            )

        with self._lock:
            self._append_record(record)

        return record

    def create(
        self,
        record: DecisionRecord,
    ) -> DecisionRecord:
        """Alias for save()."""

        return self.save(record)

    def get_by_id(
        self,
        decision_id: str,
    ) -> Optional[DecisionRecord]:
        """Return a decision by ID."""

        decision_id = str(
            decision_id
        ).strip()

        if not decision_id:
            raise ValueError(
                "decision_id cannot be empty."
            )

        with self._lock:
            records = self._read_all()

        for record in reversed(records):
            if record.decision_id == decision_id:
                return record

        return None

    def require_by_id(
        self,
        decision_id: str,
    ) -> DecisionRecord:
        """Return a decision or raise if it does not exist."""

        record = self.get_by_id(
            decision_id
        )

        if record is None:
            raise DecisionNotFoundError(
                f"Decision not found: {decision_id}"
            )

        return record

    def exists(
        self,
        decision_id: str,
    ) -> bool:
        """Check whether a decision exists."""

        return (
            self.get_by_id(decision_id)
            is not None
        )

    def list_all(
        self,
    ) -> list[DecisionRecord]:
        """Return all stored decisions."""

        with self._lock:
            return self._read_all()

    def count(self) -> int:
        """Return the total number of stored decisions."""

        with self._lock:
            return len(
                self._read_all()
            )

    def find_by_user(
        self,
        user_id: str,
    ) -> list[DecisionRecord]:
        """Return decisions belonging to a user."""

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
    ) -> list[DecisionRecord]:
        """Return decisions for a market."""

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
    ) -> list[DecisionRecord]:
        """Return decisions for an instrument."""

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
    ) -> list[DecisionRecord]:
        """Return decisions for a venue."""

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

    def find_by_status(
        self,
        status: str,
    ) -> list[DecisionRecord]:
        """Return decisions with a given state."""

        status = str(
            status
        ).strip().lower()

        if not status:
            raise ValueError(
                "status cannot be empty."
            )

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if record.state.lower() == status
        ]

    def find_by_verdict(
        self,
        verdict: str,
    ) -> list[DecisionRecord]:
        """Return decisions with a given verdict."""

        verdict = str(
            verdict
        ).strip().lower()

        if not verdict:
            raise ValueError(
                "verdict cannot be empty."
            )

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if record.verdict.lower() == verdict
        ]

    def find_by_mode(
        self,
        mode: str,
    ) -> list[DecisionRecord]:
        """Return decisions for a given operating mode."""

        mode = str(
            mode
        ).strip()

        if not mode:
            raise ValueError(
                "mode cannot be empty."
            )

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if record.mode == mode
        ]

    def find_by_direction(
        self,
        direction: str,
    ) -> list[DecisionRecord]:
        """Return decisions for a direction."""

        direction = str(
            direction
        ).strip().upper()

        if not direction:
            raise ValueError(
                "direction cannot be empty."
            )

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if record.direction.upper()
            == direction
        ]

    def find_by_decision_type(
        self,
        decision_type: str,
    ) -> list[DecisionRecord]:
        """Return decisions of a given type."""

        decision_type = str(
            decision_type
        ).strip()

        if not decision_type:
            raise ValueError(
                "decision_type cannot be empty."
            )

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if record.decision_type
            == decision_type
        ]

    def find_by_session(
        self,
        session_id: str,
    ) -> list[DecisionRecord]:
        """Return decisions associated with a session."""

        session_id = str(
            session_id
        ).strip()

        if not session_id:
            raise ValueError(
                "session_id cannot be empty."
            )

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if record.session_id
            == session_id
        ]

    def find_by_request(
        self,
        request_id: str,
    ) -> list[DecisionRecord]:
        """Return decisions associated with a request."""

        request_id = str(
            request_id
        ).strip()

        if not request_id:
            raise ValueError(
                "request_id cannot be empty."
            )

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if record.request_id
            == request_id
        ]

    def find_by_score_range(
        self,
        minimum: float = 0.0,
        maximum: float = 100.0,
    ) -> list[DecisionRecord]:
        """Return decisions whose score falls in a range."""

        minimum = float(minimum)
        maximum = float(maximum)

        if minimum > maximum:
            raise ValueError(
                "minimum cannot exceed maximum."
            )

        if minimum < 0 or maximum > 100:
            raise ValueError(
                "Score range must be between 0 and 100."
            )

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if minimum
            <= record.score
            <= maximum
        ]

    def latest(
        self,
        limit: int = 10,
    ) -> list[DecisionRecord]:
        """Return the latest decisions."""

        limit = int(limit)

        if limit <= 0:
            raise ValueError(
                "limit must be greater than zero."
            )

        with self._lock:
            records = self._read_all()

        records.sort(
            key=lambda record: record.timestamp
        )

        return records[-limit:][::-1]

    def replace(
        self,
        record: DecisionRecord,
    ) -> DecisionRecord:
        """
        Replace an existing decision record.

        JSONL storage is rebuilt atomically through a temporary file.
        """

        if not isinstance(
            record,
            DecisionRecord,
        ):
            raise TypeError(
                "record must be a DecisionRecord."
            )

        with self._lock:
            records = self._read_all()

            found = False
            updated_records: list[DecisionRecord] = []

            for existing in records:
                if (
                    existing.decision_id
                    == record.decision_id
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
                raise DecisionNotFoundError(
                    f"Decision not found: "
                    f"{record.decision_id}"
                )

            self._rewrite(
                updated_records
            )

        return record

    def update_state(
        self,
        decision_id: str,
        state: str,
    ) -> DecisionRecord:
        """Update the state of an existing decision."""

        record = self.require_by_id(
            decision_id
        )

        record.update_state(
            state
        )

        return self.replace(
            record
        )

    def add_evidence(
        self,
        decision_id: str,
        evidence_id: str,
    ) -> DecisionRecord:
        """Attach evidence to an existing decision."""

        record = self.require_by_id(
            decision_id
        )

        record.add_evidence(
            evidence_id
        )

        return self.replace(
            record
        )

    def _rewrite(
        self,
        records: Iterable[DecisionRecord],
    ) -> None:
        """Rewrite repository storage."""

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

            raise DecisionRepositoryError(
                f"Unable to rewrite decision storage: {exc}"
            ) from exc

    def delete(
        self,
        decision_id: str,
    ) -> bool:
        """
        Delete a decision record.

        Intended for administrative/data-maintenance use.
        """

        decision_id = str(
            decision_id
        ).strip()

        if not decision_id:
            raise ValueError(
                "decision_id cannot be empty."
            )

        with self._lock:
            records = self._read_all()

            remaining = [
                record
                for record in records
                if record.decision_id
                != decision_id
            ]

            if len(remaining) == len(records):
                return False

            self._rewrite(
                remaining
            )

            return True

    def clear(self) -> None:
        """
        Clear all decision records.

        This is a destructive administrative operation.
        """

        with self._lock:
            self._rewrite([])


decision_repository = DecisionRepository()


def get_decision_repository() -> DecisionRepository:
    """Return the global decision repository."""

    return decision_repository


__all__ = [
    "DecisionRepositoryError",
    "DecisionNotFoundError",
    "DecisionRepository",
    "decision_repository",
    "get_decision_repository",
]