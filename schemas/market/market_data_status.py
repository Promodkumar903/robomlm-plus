"""
ROBOMLM PLUS
Market Data Status Schema

Purpose:
    Canonical schema for describing the operational status and quality
    state of a market-data source or feed.

Design rules:
    - Describes data status only.
    - Does not make trading decisions.
    - Does not contain execution logic.
    - Does not contain risk logic.
    - Does not contain intelligence logic.
    - Separates operational status from data-quality observations.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Mapping, Optional


MARKET_DATA_STATUS_SCHEMA_VERSION = "1.0.0"


@dataclass(frozen=True)
class MarketDataStatus:
    """
    Canonical market-data operational status.
    """

    source_id: str

    status: str

    available: Optional[bool] = None
    connected: Optional[bool] = None
    live: Optional[bool] = None

    quality: Optional[str] = None
    freshness: Optional[str] = None
    latency_ms: Optional[float] = None

    last_update_at: Optional[datetime] = None
    checked_at: Optional[datetime] = None

    message: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Return a JSON-friendly dictionary representation.
        """

        data = asdict(self)

        if isinstance(self.last_update_at, datetime):
            data["last_update_at"] = self.last_update_at.isoformat()

        if isinstance(self.checked_at, datetime):
            data["checked_at"] = self.checked_at.isoformat()

        data["metadata"] = dict(self.metadata)

        return data

    def is_operational(self) -> bool:
        """
        Return whether the source is currently considered operational.
        """

        return (
            self.available is True
            and self.connected is True
        )

    def has_error(self) -> bool:
        """
        Return whether an explicit error is present.
        """

        return bool(
            self.error_code
            or self.error_message
        )


def create_market_data_status(
    source_id: str,
    status: str,
    **kwargs: Any,
) -> MarketDataStatus:
    """
    Construct a MarketDataStatus using canonical fields.
    """

    return MarketDataStatus(
        source_id=source_id,
        status=status,
        **kwargs,
    )


def market_data_status_from_mapping(
    data: Mapping[str, Any],
) -> MarketDataStatus:
    """
    Build a MarketDataStatus from a mapping.

    Unknown fields are preserved inside metadata.
    """

    known_fields = {
        "source_id",
        "status",
        "available",
        "connected",
        "live",
        "quality",
        "freshness",
        "latency_ms",
        "last_update_at",
        "checked_at",
        "message",
        "error_code",
        "error_message",
        "metadata",
    }

    values = {
        key: value
        for key, value in data.items()
        if key in known_fields
    }

    extra_fields = {
        key: value
        for key, value in data.items()
        if key not in known_fields
    }

    existing_metadata = dict(values.get("metadata") or {})
    existing_metadata.update(extra_fields)
    values["metadata"] = existing_metadata

    return MarketDataStatus(**values)


def validate_market_data_status(
    status: MarketDataStatus,
) -> dict[str, Any]:
    """
    Return structural validation information.
    """

    missing: list[str] = []

    if not status.source_id:
        missing.append("source_id")

    if not status.status:
        missing.append("status")

    return {
        "valid": not missing,
        "missing_fields": missing,
        "has_error": status.has_error(),
        "schema_version": MARKET_DATA_STATUS_SCHEMA_VERSION,
    }


def market_data_status_schema() -> dict[str, Any]:
    """
    Return schema metadata.
    """

    return {
        "schema": "MarketDataStatus",
        "version": MARKET_DATA_STATUS_SCHEMA_VERSION,
        "layer": "MARKET_DATA_STATUS",
        "decision_logic": False,
        "execution_logic": False,
        "risk_logic": False,
        "intelligence_logic": False,
    }