"""
ROBOMLM PLUS
Audit Database Model

Purpose:
    Define the persistent audit-event data structure.

Design:
    - Structured audit records.
    - Immutable event identity after creation.
    - Supports authentication, authorization, security,
      administration and execution audit events.
    - No trading logic.
    - No direct database connection.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Optional
from uuid import uuid4


@dataclass
class AuditRecord:
    """
    Structured audit record.

    This model represents an audit event only.
    Persistence is handled by repository/database layers.
    """

    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    event_type: str = ""
    action: str = ""
    status: str = ""

    source: str = ""
    component: str = ""

    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None

    mode: Optional[str] = None

    market: Optional[str] = None
    instrument: Optional[str] = None
    venue: Optional[str] = None

    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    details: dict[str, Any] = field(default_factory=dict)

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        """Normalize and validate basic model fields."""

        self.event_id = str(self.event_id).strip()

        if not self.event_id:
            raise ValueError("event_id cannot be empty.")

        self.event_type = str(self.event_type).strip()
        self.action = str(self.action).strip()
        self.status = str(self.status).strip()
        self.source = str(self.source).strip()
        self.component = str(self.component).strip()

        if self.user_id is not None:
            self.user_id = str(self.user_id).strip() or None

        if self.session_id is not None:
            self.session_id = str(self.session_id).strip() or None

        if self.request_id is not None:
            self.request_id = str(self.request_id).strip() or None

        if self.mode is not None:
            self.mode = str(self.mode).strip() or None

        if self.market is not None:
            self.market = str(self.market).strip() or None

        if self.instrument is not None:
            self.instrument = str(self.instrument).strip() or None

        if self.venue is not None:
            self.venue = str(self.venue).strip() or None

        if not isinstance(self.details, dict):
            self.details = dict(self.details)

        self.timestamp = self._normalize_datetime(self.timestamp)
        self.created_at = self._normalize_datetime(self.created_at)

    @staticmethod
    def _normalize_datetime(value: datetime) -> datetime:
        """Ensure timestamps are timezone-aware UTC datetimes."""

        if not isinstance(value, datetime):
            raise TypeError("Timestamp must be a datetime instance.")

        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable dictionary representation."""

        data = asdict(self)

        data["timestamp"] = self.timestamp.isoformat()
        data["created_at"] = self.created_at.isoformat()

        return data

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "AuditRecord":
        """Create an audit record from a mapping."""

        if not isinstance(data, Mapping):
            raise TypeError("data must be a mapping.")

        values = dict(data)

        timestamp = values.get("timestamp")

        if isinstance(timestamp, str):
            values["timestamp"] = datetime.fromisoformat(timestamp)

        created_at = values.get("created_at")

        if isinstance(created_at, str):
            values["created_at"] = datetime.fromisoformat(created_at)

        return cls(**values)

    def with_detail(
        self,
        key: str,
        value: Any,
    ) -> "AuditRecord":
        """
        Return a new record containing an additional detail.

        The original record is not modified.
        """

        key = str(key).strip()

        if not key:
            raise ValueError("Detail key cannot be empty.")

        copied_details = dict(self.details)
        copied_details[key] = value

        return AuditRecord(
            event_id=self.event_id,
            timestamp=self.timestamp,
            event_type=self.event_type,
            action=self.action,
            status=self.status,
            source=self.source,
            component=self.component,
            user_id=self.user_id,
            session_id=self.session_id,
            request_id=self.request_id,
            mode=self.mode,
            market=self.market,
            instrument=self.instrument,
            venue=self.venue,
            ip_address=self.ip_address,
            user_agent=self.user_agent,
            details=copied_details,
            created_at=self.created_at,
        )


def create_audit_record(
    *,
    event_type: str,
    action: str,
    status: str,
    source: str,
    component: str,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    request_id: Optional[str] = None,
    mode: Optional[str] = None,
    market: Optional[str] = None,
    instrument: Optional[str] = None,
    venue: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[Mapping[str, Any]] = None,
) -> AuditRecord:
    """Convenience factory for creating audit records."""

    return AuditRecord(
        event_type=event_type,
        action=action,
        status=status,
        source=source,
        component=component,
        user_id=user_id,
        session_id=session_id,
        request_id=request_id,
        mode=mode,
        market=market,
        instrument=instrument,
        venue=venue,
        ip_address=ip_address,
        user_agent=user_agent,
        details=dict(details or {}),
    )


__all__ = [
    "AuditRecord",
    "create_audit_record",
]