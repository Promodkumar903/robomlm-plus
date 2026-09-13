"""
ROBOMLM PLUS
Market Data Packet Schema

Purpose:
    Canonical schema for transporting one or more market-data records
    together with source, timing, sequence, and packet metadata.

Design rules:
    - Represents data transport structure only.
    - Does not make trading decisions.
    - Does not contain execution logic.
    - Does not contain risk logic.
    - Does not contain intelligence logic.
    - Preserves packet identity and record ordering.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Mapping, Optional, Sequence


MARKET_DATA_PACKET_SCHEMA_VERSION = "1.0.0"


@dataclass(frozen=True)
class MarketDataPacket:
    """
    Canonical market-data packet.
    """

    packet_id: str

    source_id: Optional[str] = None
    market: Optional[str] = None
    instrument: Optional[str] = None
    exchange: Optional[str] = None
    venue: Optional[str] = None

    created_at: Optional[datetime] = None
    observed_at: Optional[datetime] = None

    records: Sequence[Mapping[str, Any]] = field(default_factory=tuple)

    sequence_start: Optional[int] = None
    sequence_end: Optional[int] = None

    packet_type: Optional[str] = None

    complete: Optional[bool] = None
    valid: Optional[bool] = None
    quality: Optional[str] = None

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Return a JSON-friendly dictionary representation.
        """

        data = asdict(self)

        if isinstance(self.created_at, datetime):
            data["created_at"] = self.created_at.isoformat()

        if isinstance(self.observed_at, datetime):
            data["observed_at"] = self.observed_at.isoformat()

        data["records"] = [
            dict(record)
            for record in self.records
        ]

        data["metadata"] = dict(self.metadata)

        return data

    def is_valid(self) -> bool:
        """
        Return whether the packet is structurally valid.
        """

        if not self.packet_id:
            return False

        if self.valid is False:
            return False

        return True

    def record_count(self) -> int:
        """
        Return the number of records contained in the packet.
        """

        return len(self.records)

    def is_empty(self) -> bool:
        """
        Return whether the packet contains no records.
        """

        return self.record_count() == 0


def create_market_data_packet(
    packet_id: str,
    **kwargs: Any,
) -> MarketDataPacket:
    """
    Construct a MarketDataPacket using canonical fields.
    """

    return MarketDataPacket(
        packet_id=packet_id,
        **kwargs,
    )


def market_data_packet_from_mapping(
    data: Mapping[str, Any],
) -> MarketDataPacket:
    """
    Build a MarketDataPacket from a mapping.

    Unknown fields are preserved inside metadata.
    """

    known_fields = {
        "packet_id",
        "source_id",
        "market",
        "instrument",
        "exchange",
        "venue",
        "created_at",
        "observed_at",
        "records",
        "sequence_start",
        "sequence_end",
        "packet_type",
        "complete",
        "valid",
        "quality",
        "metadata",
    }

    values = {
        key: value
        for key, value in data.items()
        if key in known_fields
    }

    if "records" in values:
        values["records"] = tuple(
            dict(record)
            for record in (values["records"] or ())
        )

    extra_fields = {
        key: value
        for key, value in data.items()
        if key not in known_fields
    }

    existing_metadata = dict(values.get("metadata") or {})
    existing_metadata.update(extra_fields)
    values["metadata"] = existing_metadata

    return MarketDataPacket(**values)


def validate_market_data_packet(
    packet: MarketDataPacket,
) -> dict[str, Any]:
    """
    Return structural validation information.
    """

    missing: list[str] = []
    invalid_reasons: list[str] = []

    if not packet.packet_id:
        missing.append("packet_id")

    if packet.valid is False:
        invalid_reasons.append("packet_marked_invalid")

    if (
        packet.sequence_start is not None
        and packet.sequence_end is not None
        and packet.sequence_start > packet.sequence_end
    ):
        invalid_reasons.append("invalid_sequence_range")

    return {
        "valid": not missing and not invalid_reasons,
        "missing_fields": missing,
        "invalid_reasons": invalid_reasons,
        "record_count": packet.record_count(),
        "empty": packet.is_empty(),
        "schema_version": MARKET_DATA_PACKET_SCHEMA_VERSION,
    }


def market_data_packet_schema() -> dict[str, Any]:
    """
    Return schema metadata.
    """

    return {
        "schema": "MarketDataPacket",
        "version": MARKET_DATA_PACKET_SCHEMA_VERSION,
        "layer": "MARKET_DATA_PACKET",
        "decision_logic": False,
        "execution_logic": False,
        "risk_logic": False,
        "intelligence_logic": False,
    }