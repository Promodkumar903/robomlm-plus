"""
ROBOMLM PLUS
Market Data Record Schema

Purpose:
    Canonical schema for representing one complete market-data record
    composed of one or more named market-data fields.

Design rules:
    - Represents structured market data only.
    - Does not make trading decisions.
    - Does not contain execution logic.
    - Does not contain risk logic.
    - Does not contain intelligence logic.
    - Preserves source identity, observation time, and field values.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Mapping, Optional


MARKET_DATA_RECORD_SCHEMA_VERSION = "1.0.0"


@dataclass(frozen=True)
class MarketDataRecord:
    """
    Canonical market-data record.
    """

    record_id: str

    source_id: Optional[str] = None
    market: Optional[str] = None
    instrument: Optional[str] = None
    exchange: Optional[str] = None
    venue: Optional[str] = None

    observed_at: Optional[datetime] = None

    fields: Mapping[str, Any] = field(default_factory=dict)

    sequence: Optional[int] = None
    record_type: Optional[str] = None

    valid: Optional[bool] = None
    quality: Optional[str] = None

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Return a JSON-friendly dictionary representation.
        """

        data = asdict(self)

        if isinstance(self.observed_at, datetime):
            data["observed_at"] = self.observed_at.isoformat()

        data["fields"] = dict(self.fields)
        data["metadata"] = dict(self.metadata)

        return data

    def is_valid(self) -> bool:
        """
        Return whether the record is structurally valid.
        """

        if not self.record_id:
            return False

        if self.valid is False:
            return False

        return True

    def has_fields(self) -> bool:
        """
        Return whether the record contains market-data fields.
        """

        return bool(self.fields)

    def get_field(
        self,
        name: str,
        default: Any = None,
    ) -> Any:
        """
        Return a field value by name.
        """

        return self.fields.get(name, default)


def create_market_data_record(
    record_id: str,
    **kwargs: Any,
) -> MarketDataRecord:
    """
    Construct a MarketDataRecord using canonical fields.
    """

    return MarketDataRecord(
        record_id=record_id,
        **kwargs,
    )


def market_data_record_from_mapping(
    data: Mapping[str, Any],
) -> MarketDataRecord:
    """
    Build a MarketDataRecord from a mapping.

    Unknown fields are preserved inside metadata.
    """

    known_fields = {
        "record_id",
        "source_id",
        "market",
        "instrument",
        "exchange",
        "venue",
        "observed_at",
        "fields",
        "sequence",
        "record_type",
        "valid",
        "quality",
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

    return MarketDataRecord(**values)


def validate_market_data_record(
    record: MarketDataRecord,
) -> dict[str, Any]:
    """
    Return structural validation information.
    """

    missing: list[str] = []

    if not record.record_id:
        missing.append("record_id")

    invalid_reasons: list[str] = []

    if record.valid is False:
        invalid_reasons.append("record_marked_invalid")

    return {
        "valid": not missing and not invalid_reasons,
        "missing_fields": missing,
        "invalid_reasons": invalid_reasons,
        "has_fields": record.has_fields(),
        "field_count": len(record.fields),
        "schema_version": MARKET_DATA_RECORD_SCHEMA_VERSION,
    }


def market_data_record_schema() -> dict[str, Any]:
    """
    Return schema metadata.
    """

    return {
        "schema": "MarketDataRecord",
        "version": MARKET_DATA_RECORD_SCHEMA_VERSION,
        "layer": "MARKET_DATA_RECORD",
        "decision_logic": False,
        "execution_logic": False,
        "risk_logic": False,
        "intelligence_logic": False,
    }