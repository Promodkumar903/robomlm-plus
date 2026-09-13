"""
ROBOMLM PLUS
Market Data Source Schema

Purpose:
    Canonical schema for identifying the source from which market data
    originates or is delivered.

Design rules:
    - Describes data origin and delivery source only.
    - Does not contain trading decisions.
    - Does not contain execution logic.
    - Does not contain risk logic.
    - Does not contain intelligence logic.
    - Preserves observed source identity separately from derived metadata.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Mapping, Optional


MARKET_DATA_SOURCE_SCHEMA_VERSION = "1.0.0"


@dataclass(frozen=True)
class MarketDataSource:
    """
    Canonical market-data source descriptor.
    """

    source_id: str
    source_name: str

    source_type: Optional[str] = None
    provider: Optional[str] = None
    exchange: Optional[str] = None
    venue: Optional[str] = None
    market: Optional[str] = None
    instrument: Optional[str] = None

    connection_type: Optional[str] = None
    feed_type: Optional[str] = None
    endpoint: Optional[str] = None

    is_live: Optional[bool] = None
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None

    observed_at: Optional[datetime] = None

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

    def identity(self) -> dict[str, Optional[str]]:
        """
        Return only source identity fields.
        """

        return {
            "source_id": self.source_id,
            "source_name": self.source_name,
            "source_type": self.source_type,
            "provider": self.provider,
            "exchange": self.exchange,
            "venue": self.venue,
            "market": self.market,
            "instrument": self.instrument,
        }

    def is_valid(self) -> bool:
        """
        Validate the minimum source identity.
        """

        return bool(
            self.source_id
            and self.source_name
        )


def create_market_data_source(
    source_id: str,
    source_name: str,
    **kwargs: Any,
) -> MarketDataSource:
    """
    Construct a MarketDataSource using canonical fields.
    """

    return MarketDataSource(
        source_id=source_id,
        source_name=source_name,
        **kwargs,
    )


def market_data_source_from_mapping(
    data: Mapping[str, Any],
) -> MarketDataSource:
    """
    Build a MarketDataSource from a mapping.

    Unknown fields are preserved inside metadata rather than discarded.
    """

    known_fields = {
        "source_id",
        "source_name",
        "source_type",
        "provider",
        "exchange",
        "venue",
        "market",
        "instrument",
        "connection_type",
        "feed_type",
        "endpoint",
        "is_live",
        "is_primary",
        "is_active",
        "observed_at",
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

    return MarketDataSource(**values)


def validate_market_data_source(
    source: MarketDataSource,
) -> dict[str, Any]:
    """
    Return structural validation information.
    """

    missing: list[str] = []

    if not source.source_id:
        missing.append("source_id")

    if not source.source_name:
        missing.append("source_name")

    return {
        "valid": not missing,
        "missing_fields": missing,
        "schema_version": MARKET_DATA_SOURCE_SCHEMA_VERSION,
    }


def market_data_source_schema() -> dict[str, Any]:
    """
    Return schema metadata.
    """

    return {
        "schema": "MarketDataSource",
        "version": MARKET_DATA_SOURCE_SCHEMA_VERSION,
        "layer": "MARKET_DATA_SOURCE",
        "decision_logic": False,
        "execution_logic": False,
        "risk_logic": False,
        "intelligence_logic": False,
    }