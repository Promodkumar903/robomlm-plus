"""
ROBOMLM PLUS
Market Data Transport Schema

Purpose:
    Canonical schema for describing the transport state of market data
    between a source and the ROBOMLM PLUS data-processing layers.

Design rules:
    - Describes transport state only.
    - Does not make trading decisions.
    - Does not contain execution logic.
    - Does not contain risk logic.
    - Does not contain intelligence logic.
    - Preserves transport identity, timing, sequencing, and status.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Mapping, Optional


MARKET_DATA_TRANSPORT_SCHEMA_VERSION = "1.0.0"


@dataclass(frozen=True)
class MarketDataTransport:
    """
    Canonical market-data transport descriptor.
    """

    transport_id: str

    source_id: Optional[str] = None
    destination: Optional[str] = None

    transport_type: Optional[str] = None
    protocol: Optional[str] = None

    status: Optional[str] = None

    connected: Optional[bool] = None
    active: Optional[bool] = None
    reliable: Optional[bool] = None

    sequence: Optional[int] = None

    sent_at: Optional[datetime] = None
    received_at: Optional[datetime] = None

    latency_ms: Optional[float] = None

    payload_count: Optional[int] = None
    payload_size: Optional[int] = None

    valid: Optional[bool] = None
    complete: Optional[bool] = None

    error_code: Optional[str] = None
    error_message: Optional[str] = None

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Return a JSON-friendly dictionary representation.
        """

        data = asdict(self)

        if isinstance(self.sent_at, datetime):
            data["sent_at"] = self.sent_at.isoformat()

        if isinstance(self.received_at, datetime):
            data["received_at"] = self.received_at.isoformat()

        data["metadata"] = dict(self.metadata)

        return data

    def is_operational(self) -> bool:
        """
        Return whether the transport is operational.
        """

        return (
            self.connected is True
            and self.active is True
        )

    def has_error(self) -> bool:
        """
        Return whether an explicit transport error exists.
        """

        return bool(
            self.error_code
            or self.error_message
        )

    def has_payload(self) -> bool:
        """
        Return whether the transport carried one or more payloads.
        """

        return (
            self.payload_count is not None
            and self.payload_count > 0
        )


def create_market_data_transport(
    transport_id: str,
    **kwargs: Any,
) -> MarketDataTransport:
    """
    Construct a MarketDataTransport using canonical fields.
    """

    return MarketDataTransport(
        transport_id=transport_id,
        **kwargs,
    )


def market_data_transport_from_mapping(
    data: Mapping[str, Any],
) -> MarketDataTransport:
    """
    Build a MarketDataTransport from a mapping.

    Unknown fields are preserved inside metadata.
    """

    known_fields = {
        "transport_id",
        "source_id",
        "destination",
        "transport_type",
        "protocol",
        "status",
        "connected",
        "active",
        "reliable",
        "sequence",
        "sent_at",
        "received_at",
        "latency_ms",
        "payload_count",
        "payload_size",
        "valid",
        "complete",
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

    return MarketDataTransport(**values)


def validate_market_data_transport(
    transport: MarketDataTransport,
) -> dict[str, Any]:
    """
    Return structural validation information.
    """

    missing: list[str] = []
    invalid_reasons: list[str] = []

    if not transport.transport_id:
        missing.append("transport_id")

    if (
        transport.latency_ms is not None
        and transport.latency_ms < 0
    ):
        invalid_reasons.append("negative_latency")

    if (
        transport.payload_count is not None
        and transport.payload_count < 0
    ):
        invalid_reasons.append("negative_payload_count")

    if (
        transport.payload_size is not None
        and transport.payload_size < 0
    ):
        invalid_reasons.append("negative_payload_size")

    if transport.valid is False:
        invalid_reasons.append("transport_marked_invalid")

    return {
        "valid": not missing and not invalid_reasons,
        "missing_fields": missing,
        "invalid_reasons": invalid_reasons,
        "operational": transport.is_operational(),
        "has_error": transport.has_error(),
        "has_payload": transport.has_payload(),
        "schema_version": MARKET_DATA_TRANSPORT_SCHEMA_VERSION,
    }


def market_data_transport_schema() -> dict[str, Any]:
    """
    Return schema metadata.
    """

    return {
        "schema": "MarketDataTransport",
        "version": MARKET_DATA_TRANSPORT_SCHEMA_VERSION,
        "layer": "MARKET_DATA_TRANSPORT",
        "decision_logic": False,
        "execution_logic": False,
        "risk_logic": False,
        "intelligence_logic": False,
    }