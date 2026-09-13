"""
ROBOMLM PLUS
Audit Logger
Module: app/core/logging/audit_logger.py

Purpose:
    Dedicated audit-event logging for ROBOMLM PLUS.

    Audit logging records security-relevant and accountability-relevant
    events separately from ordinary application diagnostics.

    This module does not decide whether an action is authorized.
    Authorization belongs to the authorization layer.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Mapping, Optional


LOGGER_NAME = "ROBOMLM.audit"


def get_audit_logger(
    name: Optional[str] = None,
) -> logging.Logger:
    """Return the dedicated audit logger."""
    if name:
        return logging.getLogger(f"{LOGGER_NAME}.{name}")

    return logging.getLogger(LOGGER_NAME)


def _utc_timestamp() -> str:
    """Return the current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


def _serialize(value: Any) -> Any:
    """
    Convert common Python values into JSON-safe representations.
    """
    if value is None:
        return None

    if isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, Mapping):
        return {
            str(key): _serialize(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [_serialize(item) for item in value]

    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except (AttributeError, TypeError, ValueError):
            pass

    return str(value)


class AuditLogger:
    """
    Structured audit logging facade.

    Audit events are represented as JSON so downstream storage,
    search and analysis systems can consume a consistent structure.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self._logger = logger or get_audit_logger(name)

    @property
    def logger(self) -> logging.Logger:
        """Return the underlying audit logger."""
        return self._logger

    def record(
        self,
        event: str,
        *,
        actor_id: Optional[str] = None,
        actor_type: Optional[str] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        resource_id: Optional[str] = None,
        status: Optional[str] = None,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
        level: int = logging.INFO,
    ) -> dict[str, Any]:
        """
        Record a structured audit event.

        Returns the exact structured event that was submitted
        to the logger.
        """
        audit_event: dict[str, Any] = {
            "timestamp": _utc_timestamp(),
            "event": event,
            "actor_id": actor_id,
            "actor_type": actor_type,
            "action": action,
            "resource": resource,
            "resource_id": resource_id,
            "status": status,
            "request_id": request_id,
            "session_id": session_id,
            "metadata": _serialize(metadata or {}),
        }

        serialized = json.dumps(
            audit_event,
            ensure_ascii=False,
            sort_keys=True,
            default=str,
        )

        self._logger.log(level, serialized)

        return audit_event

    def authentication(
        self,
        event: str,
        *,
        actor_id: Optional[str] = None,
        status: Optional[str] = None,
        request_id: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        """Record an authentication-related audit event."""
        return self.record(
            event,
            actor_id=actor_id,
            actor_type="USER",
            action="AUTHENTICATION",
            resource="AUTH",
            status=status,
            request_id=request_id,
            metadata=metadata,
        )

    def authorization(
        self,
        event: str,
        *,
        actor_id: Optional[str] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        status: Optional[str] = None,
        request_id: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        """Record an authorization-related audit event."""
        return self.record(
            event,
            actor_id=actor_id,
            actor_type="USER",
            action=action,
            resource=resource,
            status=status,
            request_id=request_id,
            metadata=metadata,
        )

    def security(
        self,
        event: str,
        *,
        actor_id: Optional[str] = None,
        action: Optional[str] = None,
        status: Optional[str] = None,
        request_id: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        """Record a security-related audit event."""
        return self.record(
            event,
            actor_id=actor_id,
            actor_type="USER",
            action=action,
            resource="SECURITY",
            status=status,
            request_id=request_id,
            metadata=metadata,
        )

    def admin(
        self,
        event: str,
        *,
        actor_id: Optional[str] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        resource_id: Optional[str] = None,
        status: Optional[str] = None,
        request_id: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        """Record an administrative audit event."""
        return self.record(
            event,
            actor_id=actor_id,
            actor_type="ADMIN",
            action=action,
            resource=resource,
            resource_id=resource_id,
            status=status,
            request_id=request_id,
            metadata=metadata,
        )

    def execution(
        self,
        event: str,
        *,
        actor_id: Optional[str] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        resource_id: Optional[str] = None,
        status: Optional[str] = None,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Record an execution-related audit event.

        This only records the event. It does not authorize or submit
        an order.
        """
        return self.record(
            event,
            actor_id=actor_id,
            actor_type="SYSTEM_OR_USER",
            action=action,
            resource=resource,
            resource_id=resource_id,
            status=status,
            request_id=request_id,
            session_id=session_id,
            metadata=metadata,
        )


audit_logger = AuditLogger()


def record_audit_event(
    event: str,
    *,
    actor_id: Optional[str] = None,
    actor_type: Optional[str] = None,
    action: Optional[str] = None,
    resource: Optional[str] = None,
    resource_id: Optional[str] = None,
    status: Optional[str] = None,
    request_id: Optional[str] = None,
    session_id: Optional[str] = None,
    metadata: Optional[Mapping[str, Any]] = None,
    level: int = logging.INFO,
) -> dict[str, Any]:
    """Convenience function for recording an audit event."""
    return audit_logger.record(
        event,
        actor_id=actor_id,
        actor_type=actor_type,
        action=action,
        resource=resource,
        resource_id=resource_id,
        status=status,
        request_id=request_id,
        session_id=session_id,
        metadata=metadata,
        level=level,
    )