"""
ROBOMLM PLUS
Market Data Error Schema

Purpose:
    Canonical schema for representing errors encountered while obtaining,
    transporting, validating, or processing market data.

Design rules:
    - Describes market-data errors only.
    - Does not make trading decisions.
    - Does not contain execution logic.
    - Does not contain risk logic.
    - Does not contain intelligence logic.
    - Preserves error context without changing the original data.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Mapping, Optional


MARKET_DATA_ERROR_SCHEMA_VERSION = "1.0.0"


@dataclass(frozen=True)
class MarketDataError:
    """
    Canonical market-data error descriptor.
    """

    error_id: str

    error_code: str
    message: str

    source_id: Optional[str] = None
    request_id: Optional[str] = None
    response_id: Optional[str] = None

    market: Optional[str] = None
    instrument: Optional[str] = None
    exchange: Optional[str] = None
    venue: Optional[str] = None

    error_type: Optional[str] = None
    severity: Optional[str] = None

    occurred_at: Optional[datetime] = None

    recoverable: Optional[bool] = None
    retryable: Optional[bool] = None

    field_name: Optional[str] = None

    details: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Return a JSON-friendly dictionary representation.
        """

        data = asdict(self)

        if isinstance(self.occurred_at, datetime):
            data["occurred_at"] = self.occurred_at.isoformat()

        data["details"] = dict(self.details)
        data["metadata"] = dict(self.metadata)

        return data

    def is_valid(self) -> bool:
        """
        Return whether the error descriptor contains its required identity.
        """

        return bool(
            self.error_id
            and self.error_code
            and self.message
        )

    def is_recoverable(self) -> bool:
        """
        Return whether the error is explicitly marked recoverable.
        """

        return self.recoverable is True

    def is_retryable(self) -> bool:
        """
        Return whether the error is explicitly marked retryable.
        """

        return self.retryable is True


def create_market_data_error(
    error_id: str,
    error_code: str,
    message: str,
    **kwargs: Any,
) -> MarketDataError:
    """
    Construct a MarketDataError using canonical fields.
    """

    return MarketDataError(
        error_id=error_id,
        error_code=error_code,
        message=message,
        **kwargs,
    )


def market_data_error_from_mapping(
    data: Mapping[str, Any],
) -> MarketDataError:
    """
    Build a MarketDataError from a mapping.

    Unknown fields are preserved inside metadata.
    """

    known_fields = {
        "error_id",
        "error_code",
        "message",
        "source_id",
        "request_id",
        "response_id",
        "market",
        "instrument",
        "exchange",
        "venue",
        "error_type",
        "severity",
        "occurred_at",
        "recoverable",
        "retryable",
        "field_name",
        "details",
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

    return MarketDataError(**values)


def validate_market_data_error(
    error: MarketDataError,
) -> dict[str, Any]:
    """
    Return structural validation information.
    """

    missing: list[str] = []

    if not error.error_id:
        missing.append("error_id")

    if not error.error_code:
        missing.append("error_code")

    if not error.message:
        missing.append("message")

    return {
        "valid": not missing,
        "missing_fields": missing,
        "recoverable": error.is_recoverable(),
        "retryable": error.is_retryable(),
        "schema_version": MARKET_DATA_ERROR_SCHEMA_VERSION,
    }


def market_data_error_schema() -> dict[str, Any]:
    """
    Return schema metadata.
    """

    return {
        "schema": "MarketDataError",
        "version": MARKET_DATA_ERROR_SCHEMA_VERSION,
        "layer": "MARKET_DATA_ERROR",
        "decision_logic": False,
        "execution_logic": False,
        "risk_logic": False,
        "intelligence_logic": False,
    }