"""
ROBOMLM PLUS
Market Data Request Schema

Purpose:
    Canonical schema for requesting market data from a defined source,
    market, instrument, venue, and time/context scope.

Design rules:
    - Describes data requirements only.
    - Does not make trading decisions.
    - Does not contain execution logic.
    - Does not contain risk logic.
    - Does not contain intelligence logic.
    - Keeps requested scope explicit and machine-readable.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Mapping, Optional, Sequence


MARKET_DATA_REQUEST_SCHEMA_VERSION = "1.0.0"


@dataclass(frozen=True)
class MarketDataRequest:
    """
    Canonical market-data request.
    """

    request_id: str

    source_id: Optional[str] = None
    market: Optional[str] = None
    instrument: Optional[str] = None
    exchange: Optional[str] = None
    venue: Optional[str] = None

    data_types: Sequence[str] = field(default_factory=tuple)

    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None

    interval: Optional[str] = None
    timeframe: Optional[str] = None

    limit: Optional[int] = None

    live: Optional[bool] = None

    priority: Optional[str] = None

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Return a JSON-friendly dictionary representation.
        """

        data = asdict(self)

        data["data_types"] = list(self.data_types)

        if isinstance(self.start_at, datetime):
            data["start_at"] = self.start_at.isoformat()

        if isinstance(self.end_at, datetime):
            data["end_at"] = self.end_at.isoformat()

        data["metadata"] = dict(self.metadata)

        return data

    def has_scope(self) -> bool:
        """
        Return whether the request identifies at least one data scope.
        """

        return bool(
            self.source_id
            or self.market
            or self.instrument
            or self.exchange
            or self.venue
            or self.data_types
        )

    def has_time_range(self) -> bool:
        """
        Return whether both range boundaries are present.
        """

        return (
            self.start_at is not None
            and self.end_at is not None
        )


def create_market_data_request(
    request_id: str,
    **kwargs: Any,
) -> MarketDataRequest:
    """
    Construct a MarketDataRequest using canonical fields.
    """

    return MarketDataRequest(
        request_id=request_id,
        **kwargs,
    )


def market_data_request_from_mapping(
    data: Mapping[str, Any],
) -> MarketDataRequest:
    """
    Build a MarketDataRequest from a mapping.

    Unknown fields are preserved inside metadata.
    """

    known_fields = {
        "request_id",
        "source_id",
        "market",
        "instrument",
        "exchange",
        "venue",
        "data_types",
        "start_at",
        "end_at",
        "interval",
        "timeframe",
        "limit",
        "live",
        "priority",
        "metadata",
    }

    values = {
        key: value
        for key, value in data.items()
        if key in known_fields
    }

    if "data_types" in values:
        values["data_types"] = tuple(
            values["data_types"] or ()
        )

    extra_fields = {
        key: value
        for key, value in data.items()
        if key not in known_fields
    }

    existing_metadata = dict(values.get("metadata") or {})
    existing_metadata.update(extra_fields)
    values["metadata"] = existing_metadata

    return MarketDataRequest(**values)


def validate_market_data_request(
    request: MarketDataRequest,
) -> dict[str, Any]:
    """
    Return structural validation information.
    """

    missing: list[str] = []
    invalid_reasons: list[str] = []

    if not request.request_id:
        missing.append("request_id")

    if (
        request.start_at is not None
        and request.end_at is not None
        and request.start_at > request.end_at
    ):
        invalid_reasons.append("invalid_time_range")

    if request.limit is not None and request.limit <= 0:
        invalid_reasons.append("invalid_limit")

    return {
        "valid": not missing and not invalid_reasons,
        "missing_fields": missing,
        "invalid_reasons": invalid_reasons,
        "has_scope": request.has_scope(),
        "has_time_range": request.has_time_range(),
        "schema_version": MARKET_DATA_REQUEST_SCHEMA_VERSION,
    }


def market_data_request_schema() -> dict[str, Any]:
    """
    Return schema metadata.
    """

    return {
        "schema": "MarketDataRequest",
        "version": MARKET_DATA_REQUEST_SCHEMA_VERSION,
        "layer": "MARKET_DATA_REQUEST",
        "decision_logic": False,
        "execution_logic": False,
        "risk_logic": False,
        "intelligence_logic": False,
    }