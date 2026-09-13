"""
ROBOMLM PLUS
Market Data Response Schema

Purpose:
    Canonical schema for representing the result returned in response to
    a market-data request.

Design rules:
    - Describes response state and returned data only.
    - Does not make trading decisions.
    - Does not contain execution logic.
    - Does not contain risk logic.
    - Does not contain intelligence logic.
    - Preserves request identity, source identity, response status,
      records, and response metadata.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Mapping, Optional, Sequence


MARKET_DATA_RESPONSE_SCHEMA_VERSION = "1.0.0"


@dataclass(frozen=True)
class MarketDataResponse:
    """
    Canonical market-data response.
    """

    response_id: str

    request_id: Optional[str] = None
    source_id: Optional[str] = None

    market: Optional[str] = None
    instrument: Optional[str] = None
    exchange: Optional[str] = None
    venue: Optional[str] = None

    status: str = "UNKNOWN"

    records: Sequence[Mapping[str, Any]] = field(default_factory=tuple)

    received_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    record_count: Optional[int] = None

    complete: Optional[bool] = None
    valid: Optional[bool] = None

    quality: Optional[str] = None

    error_code: Optional[str] = None
    error_message: Optional[str] = None

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Return a JSON-friendly dictionary representation.
        """

        data = asdict(self)

        if isinstance(self.received_at, datetime):
            data["received_at"] = self.received_at.isoformat()

        if isinstance(self.completed_at, datetime):
            data["completed_at"] = self.completed_at.isoformat()

        data["records"] = [
            dict(record)
            for record in self.records
        ]

        data["metadata"] = dict(self.metadata)

        return data

    def is_success(self) -> bool:
        """
        Return whether the response indicates success.
        """

        return self.status.upper() in {
            "SUCCESS",
            "OK",
            "COMPLETED",
        }

    def has_error(self) -> bool:
        """
        Return whether an explicit response error exists.
        """

        return bool(
            self.error_code
            or self.error_message
        )

    def has_records(self) -> bool:
        """
        Return whether records are present.
        """

        return bool(self.records)


def create_market_data_response(
    response_id: str,
    **kwargs: Any,
) -> MarketDataResponse:
    """
    Construct a MarketDataResponse using canonical fields.
    """

    return MarketDataResponse(
        response_id=response_id,
        **kwargs,
    )


def market_data_response_from_mapping(
    data: Mapping[str, Any],
) -> MarketDataResponse:
    """
    Build a MarketDataResponse from a mapping.

    Unknown fields are preserved inside metadata.
    """

    known_fields = {
        "response_id",
        "request_id",
        "source_id",
        "market",
        "instrument",
        "exchange",
        "venue",
        "status",
        "records",
        "received_at",
        "completed_at",
        "record_count",
        "complete",
        "valid",
        "quality",
        "error_code",
        "error_message",
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

    return MarketDataResponse(**values)


def validate_market_data_response(
    response: MarketDataResponse,
) -> dict[str, Any]:
    """
    Return structural validation information.
    """

    missing: list[str] = []
    invalid_reasons: list[str] = []

    if not response.response_id:
        missing.append("response_id")

    if not response.status:
        missing.append("status")

    if response.valid is False:
        invalid_reasons.append("response_marked_invalid")

    if (
        response.record_count is not None
        and response.record_count < 0
    ):
        invalid_reasons.append("negative_record_count")

    if (
        response.record_count is not None
        and response.record_count != len(response.records)
    ):
        invalid_reasons.append("record_count_mismatch")

    return {
        "valid": not missing and not invalid_reasons,
        "missing_fields": missing,
        "invalid_reasons": invalid_reasons,
        "success": response.is_success(),
        "has_error": response.has_error(),
        "has_records": response.has_records(),
        "schema_version": MARKET_DATA_RESPONSE_SCHEMA_VERSION,
    }


def market_data_response_schema() -> dict[str, Any]:
    """
    Return schema metadata.
    """

    return {
        "schema": "MarketDataResponse",
        "version": MARKET_DATA_RESPONSE_SCHEMA_VERSION,
        "layer": "MARKET_DATA_RESPONSE",
        "decision_logic": False,
        "execution_logic": False,
        "risk_logic": False,
        "intelligence_logic": False,
    }