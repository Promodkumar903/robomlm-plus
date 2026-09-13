"""
ROBOMLM PLUS
Market Data Value Schema

Purpose:
    Canonical schema for representing a market-data value together with
    its semantic type, unit, observation state, and provenance metadata.

Design rules:
    - Represents data values only.
    - Does not make trading decisions.
    - Does not contain execution logic.
    - Does not contain risk logic.
    - Does not contain intelligence logic.
    - Keeps the observed value distinct from metadata and interpretation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Mapping, Optional


MARKET_DATA_VALUE_SCHEMA_VERSION = "1.0.0"


@dataclass(frozen=True)
class MarketDataValue:
    """
    Canonical market-data value representation.
    """

    value: Any = None

    value_type: Optional[str] = None
    unit: Optional[str] = None
    field_name: Optional[str] = None

    source_id: Optional[str] = None
    observed_at: Optional[datetime] = None

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

    def is_present(self) -> bool:
        """
        Return whether a value is present.
        """

        return self.value is not None

    def is_valid(self) -> bool:
        """
        Return whether the value is structurally valid.
        """

        if self.valid is False:
            return False

        return self.value is not None


def create_market_data_value(
    value: Any = None,
    **kwargs: Any,
) -> MarketDataValue:
    """
    Construct a MarketDataValue using canonical fields.
    """

    return MarketDataValue(
        value=value,
        **kwargs,
    )


def market_data_value_from_mapping(
    data: Mapping[str, Any],
) -> MarketDataValue:
    """
    Build a MarketDataValue from a mapping.

    Unknown fields are preserved inside metadata.
    """

    known_fields = {
        "value",
        "value_type",
        "unit",
        "field_name",
        "source_id",
        "observed_at",
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

    return MarketDataValue(**values)


def validate_market_data_value(
    data_value: MarketDataValue,
) -> dict[str, Any]:
    """
    Return structural validation information.
    """

    invalid_reasons: list[str] = []

    if data_value.value is None:
        invalid_reasons.append("value_missing")

    if data_value.valid is False:
        invalid_reasons.append("value_marked_invalid")

    return {
        "valid": not invalid_reasons,
        "invalid_reasons": invalid_reasons,
        "has_value": data_value.is_present(),
        "schema_version": MARKET_DATA_VALUE_SCHEMA_VERSION,
    }


def market_data_value_schema() -> dict[str, Any]:
    """
    Return schema metadata.
    """

    return {
        "schema": "MarketDataValue",
        "version": MARKET_DATA_VALUE_SCHEMA_VERSION,
        "layer": "MARKET_DATA_VALUE",
        "decision_logic": False,
        "execution_logic": False,
        "risk_logic": False,
        "intelligence_logic": False,
    }