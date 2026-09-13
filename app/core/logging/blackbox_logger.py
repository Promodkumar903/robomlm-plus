"""
ROBOMLM PLUS
Blackbox Logger
Module: app/core/logging/blackbox_logger.py

Purpose:
    Immutable-style event recording interface for ROBOMLM PLUS.

    The blackbox layer captures system events for reconstruction,
    diagnostics, decision tracing, execution tracing and post-event
    analysis.

    This module records events only.
    It does not make decisions, authorize actions or execute trades.
"""

from __future__ import annotations

import json
import logging
import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Mapping, Optional


LOGGER_NAME = "ROBOMLM.blackbox"


def get_blackbox_logger(
    name: Optional[str] = None,
) -> logging.Logger:
    """Return the dedicated blackbox logger."""
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


class BlackboxLogger:
    """
    Structured blackbox event recorder.

    Each event receives a unique Event_ID unless one is explicitly
    supplied by the caller.

    The sequence number provides deterministic ordering within the
    current process.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self._logger = logger or get_blackbox_logger(name)
        self._lock = threading.Lock()
        self._sequence = 0

    @property
    def logger(self) -> logging.Logger:
        """Return the underlying blackbox logger."""
        return self._logger

    @property
    def sequence(self) -> int:
        """Return the latest sequence number."""
        with self._lock:
            return self._sequence

    def _next_sequence(self) -> int:
        """Generate the next process-local sequence number."""
        with self._lock:
            self._sequence += 1
            return self._sequence

    def record(
        self,
        event_type: str,
        *,
        event_id: Optional[str] = None,
        source: Optional[str] = None,
        component: Optional[str] = None,
        action: Optional[str] = None,
        status: Optional[str] = None,
        mode: Optional[str] = None,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        market: Optional[str] = None,
        instrument: Optional[str] = None,
        venue: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
        level: int = logging.INFO,
    ) -> dict[str, Any]:
        """
        Record a structured blackbox event.

        Returns the exact event dictionary submitted to the logger.
        """

        sequence = self._next_sequence()

        event: dict[str, Any] = {
            "Event_ID": event_id or str(uuid.uuid4()),
            "Sequence": sequence,
            "Timestamp": _utc_timestamp(),
            "Event_Type": event_type,
            "Source": source,
            "Component": component,
            "Action": action,
            "Status": status,
            "Mode": mode,
            "Request_ID": request_id,
            "Session_ID": session_id,
            "User_ID": user_id,
            "Market": market,
            "Instrument": instrument,
            "Venue": venue,
            "Metadata": _serialize(metadata or {}),
        }

        serialized = json.dumps(
            event,
            ensure_ascii=False,
            sort_keys=True,
            default=str,
        )

        self._logger.log(level, serialized)

        return event

    def system(
        self,
        event_type: str,
        *,
        status: Optional[str] = None,
        component: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        """Record a system-level event."""
        return self.record(
            event_type,
            source="SYSTEM",
            component=component,
            status=status,
            metadata=metadata,
        )

    def market(
        self,
        event_type: str,
        *,
        market: Optional[str] = None,
        instrument: Optional[str] = None,
        venue: Optional[str] = None,
        status: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        """Record a market/data event."""
        return self.record(
            event_type,
            source="MARKET",
            market=market,
            instrument=instrument,
            venue=venue,
            status=status,
            metadata=metadata,
        )

    def evidence(
        self,
        event_type: str,
        *,
        instrument: Optional[str] = None,
        status: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        """Record an evidence-layer event."""
        return self.record(
            event_type,
            source="EVIDENCE",
            instrument=instrument,
            status=status,
            metadata=metadata,
        )

    def decision(
        self,
        event_type: str,
        *,
        instrument: Optional[str] = None,
        status: Optional[str] = None,
        mode: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        """Record a decision-layer event."""
        return self.record(
            event_type,
            source="DECISION",
            instrument=instrument,
            status=status,
            mode=mode,
            metadata=metadata,
        )

    def execution(
        self,
        event_type: str,
        *,
        instrument: Optional[str] = None,
        venue: Optional[str] = None,
        action: Optional[str] = None,
        status: Optional[str] = None,
        mode: Optional[str] = None,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Record an execution-layer event.

        Recording an execution event does not submit or modify an
        order by itself.
        """
        return self.record(
            event_type,
            source="EXECUTION",
            instrument=instrument,
            venue=venue,
            action=action,
            status=status,
            mode=mode,
            request_id=request_id,
            session_id=session_id,
            metadata=metadata,
        )

    def risk(
        self,
        event_type: str,
        *,
        instrument: Optional[str] = None,
        status: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        """Record a risk-layer event."""
        return self.record(
            event_type,
            source="RISK",
            instrument=instrument,
            status=status,
            metadata=metadata,
        )

    def automation(
        self,
        event_type: str,
        *,
        instrument: Optional[str] = None,
        status: Optional[str] = None,
        mode: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        """Record an AUTOROBIMLM automation event."""
        return self.record(
            event_type,
            source="AUTOROBIMLM",
            instrument=instrument,
            status=status,
            mode=mode,
            session_id=session_id,
            metadata=metadata,
        )

    def error(
        self,
        event_type: str,
        *,
        source: Optional[str] = None,
        component: Optional[str] = None,
        status: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        """Record an error event at ERROR level."""
        return self.record(
            event_type,
            source=source,
            component=component,
            status=status,
            metadata=metadata,
            level=logging.ERROR,
        )


blackbox_logger = BlackboxLogger()


def record_blackbox_event(
    event_type: str,
    *,
    event_id: Optional[str] = None,
    source: Optional[str] = None,
    component: Optional[str] = None,
    action: Optional[str] = None,
    status: Optional[str] = None,
    mode: Optional[str] = None,
    request_id: Optional[str] = None,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    market: Optional[str] = None,
    instrument: Optional[str] = None,
    venue: Optional[str] = None,
    metadata: Optional[Mapping[str, Any]] = None,
    level: int = logging.INFO,
) -> dict[str, Any]:
    """Convenience function for recording a blackbox event."""
    return blackbox_logger.record(
        event_type,
        event_id=event_id,
        source=source,
        component=component,
        action=action,
        status=status,
        mode=mode,
        request_id=request_id,
        session_id=session_id,
        user_id=user_id,
        market=market,
        instrument=instrument,
        venue=venue,
        metadata=metadata,
        level=level,
    )