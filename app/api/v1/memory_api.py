from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class MemoryRequest:
    user_id: str
    market: str
    query: str = ""
    filters: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MemoryResponse:
    success: bool
    action: str
    user_id: str | None = None
    market: str | None = None
    records: tuple[Mapping[str, Any], ...] = ()
    message: str = ""
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "action": self.action,
            "user_id": self.user_id,
            "market": self.market,
            "records": [dict(record) for record in self.records],
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
        }


class MemoryAPI:
    """
    API-facing boundary for ROBOMLM Market Memory operations.

    This layer validates memory requests and provides a canonical
    response structure. Actual memory storage, retrieval, indexing,
    historical reconstruction, and learning remain delegated to the
    corresponding application services.
    """

    def validate_request(
        self,
        request: MemoryRequest,
    ) -> MemoryResponse:
        if not isinstance(request, MemoryRequest):
            raise TypeError(
                "request must be a MemoryRequest"
            )

        self._validate_required(request.user_id, "user_id")
        self._validate_required(request.market, "market")

        return MemoryResponse(
            success=True,
            action="VALIDATE_MEMORY_REQUEST",
            user_id=request.user_id.strip(),
            market=request.market.strip(),
            message="Memory request is valid.",
        )

    def search(
        self,
        *,
        user_id: str,
        market: str,
        query: str = "",
        filters: Mapping[str, Any] | None = None,
    ) -> MemoryResponse:
        self._validate_required(user_id, "user_id")
        self._validate_required(market, "market")

        return MemoryResponse(
            success=True,
            action="SEARCH_MEMORY",
            user_id=user_id.strip(),
            market=market.strip(),
            message="Memory search request accepted.",
        )

    def store(
        self,
        *,
        user_id: str,
        market: str,
        record: Mapping[str, Any],
    ) -> MemoryResponse:
        self._validate_required(user_id, "user_id")
        self._validate_required(market, "market")

        if not isinstance(record, Mapping):
            raise TypeError("record must be a mapping")

        return MemoryResponse(
            success=True,
            action="STORE_MEMORY",
            user_id=user_id.strip(),
            market=market.strip(),
            records=(dict(record),),
            message="Memory record accepted.",
        )

    def retrieve(
        self,
        *,
        user_id: str,
        market: str,
        records: list[Mapping[str, Any]],
    ) -> MemoryResponse:
        self._validate_required(user_id, "user_id")
        self._validate_required(market, "market")

        if not isinstance(records, list):
            raise TypeError("records must be a list")

        normalized = tuple(
            dict(record)
            for record in records
            if isinstance(record, Mapping)
        )

        return MemoryResponse(
            success=True,
            action="RETRIEVE_MEMORY",
            user_id=user_id.strip(),
            market=market.strip(),
            records=normalized,
            message="Memory records retrieved successfully.",
        )

    @staticmethod
    def _validate_required(
        value: str,
        field_name: str,
    ) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"{field_name} must not be empty"
            )