"""
ROBOMLM_PLUS
app/api/v1/memory_api.py

Memory API boundary.

Flow:

Frontend
    ->
Memory HTTP API
    ->
RobomlmApplication.memory()
    ->
Existing ROBOMLM memory engines
    ->
Outcome Memory
    ->
Pattern Memory
    ->
Learning
    ->
Intelligence
    ->
Frontend

This module does NOT own:
    - memory storage
    - memory indexing
    - learning calculations
    - pattern calculations
    - intelligence calculations
    - database implementation

Existing memory engines remain authoritative.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.application.robomlm_application import get_application


LOGGER = logging.getLogger(__name__)


# ============================================================
# HTTP ROUTER
# ============================================================

router = APIRouter(
    prefix="/memory",
    tags=["memory"],
)


memory_router = router


# ============================================================
# EXISTING MEMORY REQUEST CONTRACT
# ============================================================

@dataclass(frozen=True)
class MemoryRequest:
    user_id: str
    market: str
    query: str = ""
    filters: Mapping[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# EXISTING MEMORY RESPONSE CONTRACT
# ============================================================

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
            "records": [
                dict(record)
                for record in self.records
            ],
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
        }


# ============================================================
# EXISTING MEMORY API BOUNDARY
# ============================================================

class MemoryAPI:
    """
    API-facing boundary for ROBOMLM Market Memory operations.

    This class remains available for existing backend callers.

    Actual memory storage, retrieval, indexing, historical
    reconstruction, and learning remain delegated to the
    corresponding application/backend services.
    """

    def validate_request(
        self,
        request: MemoryRequest,
    ) -> MemoryResponse:

        if not isinstance(
            request,
            MemoryRequest,
        ):
            raise TypeError(
                "request must be a MemoryRequest"
            )

        self._validate_required(
            request.user_id,
            "user_id",
        )

        self._validate_required(
            request.market,
            "market",
        )

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

        self._validate_required(
            user_id,
            "user_id",
        )

        self._validate_required(
            market,
            "market",
        )

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

        self._validate_required(
            user_id,
            "user_id",
        )

        self._validate_required(
            market,
            "market",
        )

        if not isinstance(
            record,
            Mapping,
        ):
            raise TypeError(
                "record must be a mapping"
            )

        return MemoryResponse(
            success=True,
            action="STORE_MEMORY",
            user_id=user_id.strip(),
            market=market.strip(),
            records=(
                dict(record),
            ),
            message="Memory record accepted.",
        )

    def retrieve(
        self,
        *,
        user_id: str,
        market: str,
        records: list[Mapping[str, Any]],
    ) -> MemoryResponse:

        self._validate_required(
            user_id,
            "user_id",
        )

        self._validate_required(
            market,
            "market",
        )

        if not isinstance(
            records,
            list,
        ):
            raise TypeError(
                "records must be a list"
            )

        normalized = tuple(
            dict(record)
            for record in records
            if isinstance(
                record,
                Mapping,
            )
        )

        return MemoryResponse(
            success=True,
            action="RETRIEVE_MEMORY",
            user_id=user_id.strip(),
            market=market.strip(),
            records=normalized,
            message=(
                "Memory records retrieved successfully."
            ),
        )

    @staticmethod
    def _validate_required(
        value: str,
        field_name: str,
    ) -> None:

        if (
            not isinstance(
                value,
                str,
            )
            or not value.strip()
        ):
            raise ValueError(
                f"{field_name} must not be empty"
            )


# ============================================================
# HTTP REQUEST MODEL
# ============================================================

class MemorySearchRequest(BaseModel):
    """
    Frontend/application search contract.

    These fields map directly to the verified
    RobomlmApplication.memory() signature.
    """

    symbol: str | None = Field(
        default=None,
        max_length=100,
    )

    query: str | None = Field(
        default=None,
        max_length=500,
    )

    limit: int = Field(
        default=50,
        ge=1,
        le=500,
    )


# ============================================================
# APPLICATION ACCESS
# ============================================================

def _application():
    """
    Resolve the single ROBOMLM application facade.

    No memory engine is instantiated here.
    """

    try:
        return get_application()

    except Exception as exc:
        LOGGER.exception(
            "Unable to resolve ROBOMLM application"
        )

        raise HTTPException(
            status_code=503,
            detail={
                "error": (
                    "APPLICATION_SERVICE_UNAVAILABLE"
                ),
                "message": str(exc),
            },
        )


# ============================================================
# RESULT NORMALISATION
# ============================================================

def _normalise_memory_result(
    result: Any,
) -> dict[str, Any]:

    if isinstance(
        result,
        dict,
    ):
        return result

    return {
        "status": "READY",
        "result": result,
    }


# ============================================================
# MEMORY GET
# ============================================================

@router.get(
    "",
    summary="Read ROBOMLM Memory",
)
def memory_get(
    symbol: str | None = Query(
        default=None,
        max_length=100,
    ),
    query: str | None = Query(
        default=None,
        max_length=500,
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=500,
    ),
):
    """
    Read/search existing ROBOMLM memory.

    The application facade remains the owner of memory
    retrieval and delegates to the existing memory engines.

    No synthetic records are created by this endpoint.
    """

    app = _application()

    try:
        result = app.memory(
            symbol=symbol,
            query=query,
            limit=limit,
        )

        return _normalise_memory_result(
            result
        )

    except HTTPException:
        raise

    except Exception as exc:
        LOGGER.exception(
            "Memory retrieval failed"
        )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "MEMORY_RETRIEVAL_FAILED",
                "message": str(exc),
                "symbol": symbol,
                "query": query,
                "limit": limit,
            },
        )


# ============================================================
# MEMORY POST
# ============================================================

@router.post(
    "",
    summary="Query ROBOMLM Memory",
)
def memory_post(
    request: MemorySearchRequest,
):
    """
    POST-compatible Memory endpoint.

    It uses the same application memory owner as GET.

    This endpoint is read/query oriented. It does not store
    or mutate memory records.
    """

    app = _application()

    try:
        result = app.memory(
            symbol=request.symbol,
            query=request.query,
            limit=request.limit,
        )

        return _normalise_memory_result(
            result
        )

    except HTTPException:
        raise

    except Exception as exc:
        LOGGER.exception(
            "Memory query failed"
        )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "MEMORY_QUERY_FAILED",
                "message": str(exc),
                "symbol": request.symbol,
                "query": request.query,
                "limit": request.limit,
            },
        )


# ============================================================
# MEMORY HEALTH
# ============================================================

@router.get(
    "/health",
    summary="Memory backend health",
)
def memory_health():
    """
    Read memory availability through the application facade.

    No synthetic health state is created.
    """

    app = _application()

    try:
        result = app.memory(
            symbol=None,
            query=None,
            limit=1,
        )

        result = _normalise_memory_result(
            result
        )

        status = str(
            result.get(
                "status",
                "UNKNOWN",
            )
        )

        return {
            "status": status,
            "memory": {
                "available": (
                    status.upper()
                    == "READY"
                ),
            },
        }

    except HTTPException:
        raise

    except Exception as exc:
        LOGGER.exception(
            "Memory health check failed"
        )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "MEMORY_HEALTH_FAILED",
                "message": str(exc),
            },
        )


# ============================================================
# ROUTER EXPORT
# ============================================================

memory_router = router