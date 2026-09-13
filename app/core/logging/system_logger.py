"""
ROBOMLM PLUS
System Logger
Module: app/core/logging/system_logger.py

Purpose:
    System-level logging for ROBOMLM PLUS.

    This logger is responsible for startup, shutdown, dependency,
    health, configuration and infrastructure events.

    It is intentionally separate from application, audit and
    blackbox logging.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Mapping, Optional


LOGGER_NAME = "ROBOMLM.system"


def get_system_logger(
    name: Optional[str] = None,
) -> logging.Logger:
    """Return the dedicated system logger."""
    if name:
        return logging.getLogger(f"{LOGGER_NAME}.{name}")

    return logging.getLogger(LOGGER_NAME)


def _utc_timestamp() -> str:
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def _serialize(value: Any) -> Any:
    """Convert common Python values into JSON-safe values."""
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


class SystemLogger:
    """
    Structured system-event logging facade.

    Intended for infrastructure and lifecycle events such as:

        - startup
        - shutdown
        - dependency checks
        - configuration checks
        - health checks
        - connection state
        - infrastructure errors
    """

    def __init__(
        self,
        name: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self._logger = logger or get_system_logger(name)

    @property
    def logger(self) -> logging.Logger:
        """Return the underlying Python logger."""
        return self._logger

    def record(
        self,
        event_type: str,
        *,
        status: Optional[str] = None,
        component: Optional[str] = None,
        message: Optional[str] = None,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
        level: int = logging.INFO,
    ) -> dict[str, Any]:
        """
        Record a structured system event.

        Returns the event dictionary submitted to the logger.
        """

        event: dict[str, Any] = {
            "timestamp": _utc_timestamp(),
            "event_type": event_type,
            "status": status,
            "component": component,
            "message": message,
            "request_id": request_id,
            "session_id": session_id,
            "metadata": _serialize(metadata or {}),
        }

        serialized = json.dumps(
            event,
            ensure_ascii=False,
            sort_keys=True,
            default=str,
        )

        self._logger.log(level, serialized)

        return event

    def startup(
        self,
        *,
        component: Optional[str] = None,
        status: Optional[str] = None,
        message: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        """Record a startup event."""
        return self.record(
            "SYSTEM_STARTUP",
            status=status,
            component=component,
            message=message,
            metadata=metadata,
        )

    def shutdown(
        self,
        *,
        component: Optional[str] = None,
        status: Optional[str] = None,
        message: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        """Record a shutdown event."""
        return self.record(
            "SYSTEM_SHUTDOWN",
            status=status,
            component=component,
            message=message,
            metadata=metadata,
        )

    def dependency(
        self,
        dependency: str,
        *,
        status: Optional[str] = None,
        message: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        """Record a dependency-check event."""
        return self.record(
            "DEPENDENCY_CHECK",
            status=status,
            component=dependency,
            message=message,
            metadata=metadata,
        )

    def configuration(
        self,
        *,
        status: Optional[str] = None,
        message: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        """Record a configuration event."""
        return self.record(
            "CONFIGURATION_CHECK",
            status=status,
            component="CONFIGURATION",
            message=message,
            metadata=metadata,
        )

    def health(
        self,
        component: str,
        *,
        status: Optional[str] = None,
        message: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        """Record a component health event."""
        return self.record(
            "HEALTH_CHECK",
            status=status,
            component=component,
            message=message,
            metadata=metadata,
        )

    def connection(
        self,
        component: str,
        *,
        status: Optional[str] = None,
        message: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        """Record a connection lifecycle event."""
        return self.record(
            "CONNECTION_STATUS",
            status=status,
            component=component,
            message=message,
            metadata=metadata,
        )

    def warning(
        self,
        event_type: str,
        *,
        component: Optional[str] = None,
        message: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        """Record a system warning."""
        return self.record(
            event_type,
            status="WARNING",
            component=component,
            message=message,
            metadata=metadata,
            level=logging.WARNING,
        )

    def error(
        self,
        event_type: str,
        *,
        component: Optional[str] = None,
        message: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        """Record a system error."""
        return self.record(
            event_type,
            status="ERROR",
            component=component,
            message=message,
            metadata=metadata,
            level=logging.ERROR,
        )

    def critical(
        self,
        event_type: str,
        *,
        component: Optional[str] = None,
        message: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        """Record a critical system event."""
        return self.record(
            event_type,
            status="CRITICAL",
            component=component,
            message=message,
            metadata=metadata,
            level=logging.CRITICAL,
        )


system_logger = SystemLogger()


def record_system_event(
    event_type: str,
    *,
    status: Optional[str] = None,
    component: Optional[str] = None,
    message: Optional[str] = None,
    request_id: Optional[str] = None,
    session_id: Optional[str] = None,
    metadata: Optional[Mapping[str, Any]] = None,
    level: int = logging.INFO,
) -> dict[str, Any]:
    """Convenience function for recording a system event."""
    return system_logger.record(
        event_type,
        status=status,
        component=component,
        message=message,
        request_id=request_id,
        session_id=session_id,
        metadata=metadata,
        level=level,
    )