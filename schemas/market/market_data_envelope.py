"""
ROBOMLM PLUS
Market Data Envelope Schema

Purpose:
    Canonical transport envelope for carrying market-data payloads with
    identity, source, timing, sequencing, and integrity metadata.

Design rules:
    - Defines transport and contextual structure only.
    - Does not make trading decisions.
    - Does not contain execution logic.
    - Does not contain risk logic.
    - Does not contain intelligence logic.
    - Preserves the original payload without interpreting it.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Mapping, Optional


MARKET_DATA_ENVELOPE_SCHEMA_VERSION = "1.0.0"


@dataclass(frozen=True)
class MarketDataEnvelope:
    """
    Canonical market-data transport envelope.
    """

    envelope_id: str

    payload: Any = None

    source_id: Optional[str] = None
    market: Optional[str] = None
    instrument: Optional[str] = None
    exchange: Optional[str] = None
    venue: Optional[str] = None

    created_at: Optional[datetime] = None
    observed_at: Optional[datetime] = None
    received_at: Optional[datetime] = None

    sequence: Optional[int] = None

    payload_type: Optional[str] = None
    content_type: Optional[str] = None
    schema_version: Optional[str] = None

    valid: Optional[bool] = None
    complete: Optional[bool] = None
    quality: Optional[str] = None

    checksum: Optional[str] = None

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

        if isinstance(self.received_at, datetime):
            data["received_at"] = self.received_at.isoformat()

        data["metadata"] = dict(self.metadata)

        return data

    def has_payload(self) -> bool:
        """
        Return whether the envelope contains a payload.
        """

        return self.payload is not None

    def is_valid(self) -> bool:
        """
        Return whether the envelope is structurally valid.
        """

        if not self.envelope_id:
            return False

        if self.valid is False:
            return False

        return True


def create_market_data_envelope(
    envelope_id: str,
    payload: Any = None,
    **kwargs: Any,
) -> MarketDataEnvelope:
    """
    Construct a MarketDataEnvelope using canonical fields.
    """

    return MarketDataEnvelope(
        envelope_id=envelope_id,
        payload=payload,
        **kwargs,
    )


def market_data_envelope_from_mapping(
    data: Mapping[str, Any],
) -> MarketDataEnvelope:
    """
    Build a MarketDataEnvelope from a mapping.

    Unknown fields are preserved inside metadata.
    """

    known_fields = {
        "envelope_id",
        "payload",
        "source_id",
        "market",
        "instrument",
        "exchange",
        "venue",
        "created_at",
        "observed_at",
        "received_at",
        "sequence",
        "payload_type",
        "content_type",
        "schema_version",
        "valid",
        "complete",
        "quality",
        "checksum",
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

    return MarketDataEnvelope(**values)


def validate_market_data_envelope(
    envelope: MarketDataEnvelope,
) -> dict[str, Any]:
    """
    Return structural validation information.
    """

    missing: list[str] = []
    invalid_reasons: list[str] = []

    if not envelope.envelope_id:
        missing.append("envelope_id")

    if envelope.valid is False:
        invalid_reasons.append("envelope_marked_invalid")

    return {
        "valid": not missing and not invalid_reasons,
        "missing_fields": missing,
        "invalid_reasons": invalid_reasons,
        "has_payload": envelope.has_payload(),
        "schema_version": MARKET_DATA_ENVELOPE_SCHEMA_VERSION,
    }


def market_data_envelope_schema() -> dict[str, Any]:
    """
    Return schema metadata.
    """

    return {
        "schema": "MarketDataEnvelope",
        "version": MARKET_DATA_ENVELOPE_SCHEMA_VERSION,
        "layer": "MARKET_DATA_ENVELOPE",
        "decision_logic": False,
        "execution_logic": False,
        "risk_logic": False,
        "intelligence_logic": False,
    }