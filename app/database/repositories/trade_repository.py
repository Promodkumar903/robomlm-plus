"""
ROBOMLM PLUS
Trade Repository

Purpose:
    Provide persistence operations for TradeRecord objects.

Design:
    - Repository layer only.
    - No order placement or execution logic.
    - No broker/exchange interaction.
    - Uses JSONL storage for the initial implementation.
    - Preserves complete trade lifecycle history.
    - Keeps persistence isolated from AUTOROBIMLM execution components.
"""

from __future__ import annotations

import json
from pathlib import Path
from threading import RLock
from typing import Iterable, Optional

from app.database.models.trade_model import (
    TradeRecord,
)


class TradeRepositoryError(Exception):
    """Base exception for trade repository errors."""


class TradeNotFoundError(TradeRepositoryError):
    """Raised when a requested trade does not exist."""


class TradeRepository:
    """Persistent repository for trade records."""

    FILE_NAME = "trades.jsonl"

    def __init__(
        self,
        storage_dir: Optional[str | Path] = None,
    ) -> None:
        if storage_dir is None:
            storage_dir = (
                Path(__file__).resolve().parents[3]
                / "robomlm_data"
                / "outcomes"
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
            raise TradeRepositoryError(
                f"Unable to initialize trade storage: {exc}"
            ) from exc

    def _append_record(
        self,
        record: TradeRecord,
    ) -> None:
        """Append a trade record to JSONL storage."""

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
            raise TradeRepositoryError(
                f"Unable to write trade record: {exc}"
            ) from exc

        except (TypeError, ValueError) as exc:
            raise TradeRepositoryError(
                f"Unable to serialize trade record: {exc}"
            ) from exc

    def _read_all(
        self,
    ) -> list[TradeRecord]:
        """Read all stored trade records."""

        records: list[TradeRecord] = []

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
                            TradeRecord.from_dict(
                                payload
                            )
                        )

                    except (
                        json.JSONDecodeError,
                        TypeError,
                        ValueError,
                    ) as exc:
                        raise TradeRepositoryError(
                            "Invalid trade record at "
                            f"line {line_number}: {exc}"
                        ) from exc

        except OSError as exc:
            raise TradeRepositoryError(
                f"Unable to read trade storage: {exc}"
            ) from exc

        return records

    def _rewrite(
        self,
        records: Iterable[TradeRecord],
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

            raise TradeRepositoryError(
                f"Unable to rewrite trade storage: {exc}"
            ) from exc

    def save(
        self,
        record: TradeRecord,
    ) -> TradeRecord:
        """Persist a new trade record."""

        if not isinstance(
            record,
            TradeRecord,
        ):
            raise TypeError(
                "record must be a TradeRecord."
            )

        with self._lock:
            self._append_record(record)

        return record

    def create(
        self,
        record: TradeRecord,
    ) -> TradeRecord:
        """Alias for save()."""

        return self.save(record)

    def get_by_id(
        self,
        trade_id: str,
    ) -> Optional[TradeRecord]:
        """Return a trade by ID."""

        trade_id = str(
            trade_id
        ).strip()

        if not trade_id:
            raise ValueError(
                "trade_id cannot be empty."
            )

        with self._lock:
            records = self._read_all()

        for record in reversed(records):
            if record.trade_id == trade_id:
                return record

        return None

    def require_by_id(
        self,
        trade_id: str,
    ) -> TradeRecord:
        """Return a trade or raise if it does not exist."""

        record = self.get_by_id(
            trade_id
        )

        if record is None:
            raise TradeNotFoundError(
                f"Trade not found: {trade_id}"
            )

        return record

    def exists(
        self,
        trade_id: str,
    ) -> bool:
        """Check whether a trade exists."""

        return (
            self.get_by_id(trade_id)
            is not None
        )

    def list_all(
        self,
    ) -> list[TradeRecord]:
        """Return all stored trades."""

        with self._lock:
            return self._read_all()

    def count(self) -> int:
        """Return the total number of stored trades."""

        with self._lock:
            return len(
                self._read_all()
            )

    def find_by_user(
        self,
        user_id: str,
    ) -> list[TradeRecord]:
        """Return trades belonging to a user."""

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

    def find_by_session(
        self,
        session_id: str,
    ) -> list[TradeRecord]:
        """Return trades associated with a session."""

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
            if record.session_id == session_id
        ]

    def find_by_request(
        self,
        request_id: str,
    ) -> list[TradeRecord]:
        """Return trades associated with a request."""

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
            if record.request_id == request_id
        ]

    def find_by_market(
        self,
        market: str,
    ) -> list[TradeRecord]:
        """Return trades for a market."""

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
    ) -> list[TradeRecord]:
        """Return trades for an instrument."""

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
    ) -> list[TradeRecord]:
        """Return trades for a venue."""

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

    def find_by_mode(
        self,
        mode: str,
    ) -> list[TradeRecord]:
        """Return trades for an operating mode."""

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

    def find_by_status(
        self,
        status: str,
    ) -> list[TradeRecord]:
        """Return trades with a given status."""

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
            if record.status.lower() == status
        ]

    def find_open(
        self,
    ) -> list[TradeRecord]:
        """Return currently open trades."""

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if record.is_open
        ]

    def find_closed(
        self,
    ) -> list[TradeRecord]:
        """Return closed trades."""

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if record.is_closed
        ]

    def find_by_side(
        self,
        side: str,
    ) -> list[TradeRecord]:
        """Return trades for a given side."""

        side = str(
            side
        ).strip().upper()

        if not side:
            raise ValueError(
                "side cannot be empty."
            )

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if record.side.upper() == side
        ]

    def find_by_decision(
        self,
        decision_id: str,
    ) -> list[TradeRecord]:
        """Return trades associated with a decision."""

        decision_id = str(
            decision_id
        ).strip()

        if not decision_id:
            raise ValueError(
                "decision_id cannot be empty."
            )

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if record.decision_id == decision_id
        ]

    def find_by_evidence(
        self,
        evidence_id: str,
    ) -> list[TradeRecord]:
        """Return trades linked to evidence."""

        evidence_id = str(
            evidence_id
        ).strip()

        if not evidence_id:
            raise ValueError(
                "evidence_id cannot be empty."
            )

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if evidence_id
            in record.evidence_ids
        ]

    def find_profitable(
        self,
    ) -> list[TradeRecord]:
        """Return closed trades with positive realized P&L."""

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if record.realized_pnl is not None
            and record.realized_pnl > 0
        ]

    def find_losing(
        self,
    ) -> list[TradeRecord]:
        """Return closed trades with negative realized P&L."""

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if record.realized_pnl is not None
            and record.realized_pnl < 0
        ]

    def find_breakeven(
        self,
    ) -> list[TradeRecord]:
        """Return trades with zero realized P&L."""

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if record.realized_pnl is not None
            and record.realized_pnl == 0
        ]

    def realized_pnl_total(
        self,
    ) -> float:
        """Return total realized P&L across recorded trades."""

        with self._lock:
            records = self._read_all()

        return sum(
            record.realized_pnl or 0.0
            for record in records
        )

    def fees_total(
        self,
    ) -> float:
        """Return total recorded fees."""

        with self._lock:
            records = self._read_all()

        return sum(
            record.fees
            for record in records
        )

    def net_realized_pnl_total(
        self,
    ) -> float:
        """Return total realized P&L after fees."""

        with self._lock:
            records = self._read_all()

        return sum(
            record.net_realized_pnl or 0.0
            for record in records
        )

    def latest(
        self,
        limit: int = 10,
    ) -> list[TradeRecord]:
        """Return the latest trades."""

        limit = int(limit)

        if limit <= 0:
            raise ValueError(
                "limit must be greater than zero."
            )

        with self._lock:
            records = self._read_all()

        records.sort(
            key=lambda record: (
                record.closed_at
                or record.opened_at
                or record.created_at
            )
        )

        return records[-limit:][::-1]

    def replace(
        self,
        record: TradeRecord,
    ) -> TradeRecord:
        """Replace an existing trade record."""

        if not isinstance(
            record,
            TradeRecord,
        ):
            raise TypeError(
                "record must be a TradeRecord."
            )

        with self._lock:
            records = self._read_all()

            found = False
            updated_records: list[
                TradeRecord
            ] = []

            for existing in records:
                if (
                    existing.trade_id
                    == record.trade_id
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
                raise TradeNotFoundError(
                    f"Trade not found: "
                    f"{record.trade_id}"
                )

            self._rewrite(
                updated_records
            )

        return record

    def open_trade(
        self,
        trade_id: str,
        entry_price: float,
    ) -> TradeRecord:
        """Mark an existing trade as opened."""

        record = self.require_by_id(
            trade_id
        )

        record.open_trade(
            entry_price
        )

        return self.replace(
            record
        )

    def close_trade(
        self,
        trade_id: str,
        exit_price: float,
        realized_pnl: Optional[float] = None,
        exit_reason: Optional[str] = None,
    ) -> TradeRecord:
        """Mark an existing trade as closed."""

        record = self.require_by_id(
            trade_id
        )

        record.close_trade(
            exit_price=exit_price,
            realized_pnl=realized_pnl,
            exit_reason=exit_reason,
        )

        return self.replace(
            record
        )

    def update_unrealized_pnl(
        self,
        trade_id: str,
        value: float,
    ) -> TradeRecord:
        """Update unrealized P&L."""

        record = self.require_by_id(
            trade_id
        )

        record.update_unrealized_pnl(
            value
        )

        return self.replace(
            record
        )

    def update_levels(
        self,
        trade_id: str,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
    ) -> TradeRecord:
        """Update SL/TP levels."""

        record = self.require_by_id(
            trade_id
        )

        record.update_levels(
            stop_loss=stop_loss,
            take_profit=take_profit,
        )

        return self.replace(
            record
        )

    def add_evidence(
        self,
        trade_id: str,
        evidence_id: str,
    ) -> TradeRecord:
        """Attach evidence to a trade."""

        record = self.require_by_id(
            trade_id
        )

        record.add_evidence(
            evidence_id
        )

        return self.replace(
            record
        )

    def delete(
        self,
        trade_id: str,
    ) -> bool:
        """
        Delete a trade record.

        Intended for administrative/data-maintenance use.
        """

        trade_id = str(
            trade_id
        ).strip()

        if not trade_id:
            raise ValueError(
                "trade_id cannot be empty."
            )

        with self._lock:
            records = self._read_all()

            remaining = [
                record
                for record in records
                if record.trade_id != trade_id
            ]

            if len(remaining) == len(records):
                return False

            self._rewrite(
                remaining
            )

            return True

    def clear(self) -> None:
        """
        Clear all trade records.

        Destructive administrative operation.
        """

        with self._lock:
            self._rewrite([])


trade_repository = TradeRepository()


def get_trade_repository() -> TradeRepository:
    """Return the global trade repository."""

    return trade_repository


__all__ = [
    "TradeRepositoryError",
    "TradeNotFoundError",
    "TradeRepository",
    "trade_repository",
    "get_trade_repository",
]