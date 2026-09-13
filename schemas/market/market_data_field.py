"""
ROBOMLM PLUS
Market Data Field Schema

Purpose:
    Canonical schema for describing an individual field contained within
    market data.

Design rules:
    - Describes field identity and value characteristics only.
    - Does not make trading decisions.
    - Does not contain execution logic.
    - Does not contain risk logic.
    - Does not contain intelligence logic.
    - Preserves observed value separately from derived metadata.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Mapping, Optional


MARKET_DATA_FIELD_SCHEMA_VERSION = "1.0.0"


@dataclass(frozen=True)
class MarketDataField:
    """
    Canonical market-data field descriptor.
    """

    name: str

    value: Any = None

    field_type: Optional[str] = None
    unit: Optional[str] = None
    source: Optional[str] = None

    observed_at: Optional[datetime] = None

    required: bool = False
    nullable: bool = True

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

        data["metadata"] = dict(self.metadata)

        return data

    def is_valid(self) -> bool:
        """
        Return whether the field is structurally valid.
        """

        if not self.name:
            return False

        if self.value is None and self.required and not self.nullable:
            return False

        if self.valid is False:
            return False

        return True


def create_market_data_field(
    name: str,
    value: Any = None,
    **kwargs: Any,
) -> MarketDataField:
    """
    Construct a MarketDataField using canonical fields.
    """

    return MarketDataField(
        name=name,
        value=value,
        **kwargs,
    )


def market_data_field_from_mapping(
    data: Mapping[str, Any],
) -> MarketDataField:
    """
    Build a MarketDataField from a mapping.

    Unknown fields are preserved inside metadata.
    """

    known_fields = {
        "name",
        "value",
        "field_type",
        "unit",
        "source",
        "observed_at",
        "required",
        "nullable",
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

    return MarketDataField(**values)


def validate_market_data_field(
    field_value: MarketDataField,
) -> dict[str, Any]:
    """
    Return structural validation information.
    """

    missing: list[str] = []

    if not field_value.name:
        missing.append("name")

    null_violation = (
        field_value.value is None
        and field_value.required
        and not field_value.nullable
    )

    return {
        "valid": not missing and not null_violation and field_value.valid is not False,
        "missing_fields": missing,
        "null_violation": null_violation,
        "schema_version": MARKET_DATA_FIELD_SCHEMA_VERSION,
    }


def market_data_field_schema() -> dict[str, Any]:
    """
    Return schema metadata.
    """

    return {
        "schema": "MarketDataField",
        "version": MARKET_DATA_FIELD_SCHEMA_VERSION,
        "layer": "MARKET_DATA_FIELD",
        "decision_logic": False,
        "execution_logic": False,
        "risk_logic": False,
        "intelligence_logic": False,
    }