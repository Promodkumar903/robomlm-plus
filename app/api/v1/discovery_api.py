from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class DiscoveryRequest:
    user_id: str
    market: str
    filters: Mapping[str, Any] = field(default_factory=dict)
    limit: int = 20


@dataclass(frozen=True)
class DiscoveryResponse:
    success: bool
    action: str
    user_id: str | None = None
    market: str | None = None
    opportunities: tuple[Mapping[str, Any], ...] = ()
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
            "opportunities": [
                dict(item) for item in self.opportunities
            ],
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
        }


class DiscoveryAPI:
    """
    API-facing boundary for ROBOMLM opportunity discovery.

    This layer validates discovery requests and provides a canonical
    response structure. Actual scanning, ranking, filtering, evidence
    evaluation, and intelligence generation remain delegated to the
    discovery/intelligence services.
    """

    def validate_request(
        self,
        request: DiscoveryRequest,
    ) -> DiscoveryResponse:
        if not isinstance(request, DiscoveryRequest):
            raise TypeError(
                "request must be a DiscoveryRequest"
            )

        self._validate_required(request.user_id, "user_id")
        self._validate_required(request.market, "market")
        self._validate_limit(request.limit)

        return DiscoveryResponse(
            success=True,
            action="VALIDATE_DISCOVERY_REQUEST",
            user_id=request.user_id.strip(),
            market=request.market.strip(),
            message="Discovery request is valid.",
        )

    def scan(
        self,
        *,
        user_id: str,
        market: str,
        filters: Mapping[str, Any] | None = None,
        limit: int = 20,
    ) -> DiscoveryResponse:
        self._validate_required(user_id, "user_id")
        self._validate_required(market, "market")
        self._validate_limit(limit)

        return DiscoveryResponse(
            success=True,
            action="SCAN_OPPORTUNITIES",
            user_id=user_id.strip(),
            market=market.strip(),
            message="Opportunity scan request accepted.",
        )

    def rank(
        self,
        *,
        user_id: str,
        market: str,
        opportunities: list[Mapping[str, Any]],
    ) -> DiscoveryResponse:
        self._validate_required(user_id, "user_id")
        self._validate_required(market, "market")

        if not isinstance(opportunities, list):
            raise TypeError(
                "opportunities must be a list"
            )

        normalized = tuple(
            dict(item)
            for item in opportunities
            if isinstance(item, Mapping)
        )

        return DiscoveryResponse(
            success=True,
            action="RANK_OPPORTUNITIES",
            user_id=user_id.strip(),
            market=market.strip(),
            opportunities=normalized,
            message="Opportunity ranking request accepted.",
        )

    def filter(
        self,
        *,
        user_id: str,
        market: str,
        opportunities: list[Mapping[str, Any]],
        filters: Mapping[str, Any] | None = None,
    ) -> DiscoveryResponse:
        self._validate_required(user_id, "user_id")
        self._validate_required(market, "market")

        if not isinstance(opportunities, list):
            raise TypeError(
                "opportunities must be a list"
            )

        normalized = tuple(
            dict(item)
            for item in opportunities
            if isinstance(item, Mapping)
        )

        return DiscoveryResponse(
            success=True,
            action="FILTER_OPPORTUNITIES",
            user_id=user_id.strip(),
            market=market.strip(),
            opportunities=normalized,
            message="Opportunity filtering request accepted.",
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

    @staticmethod
    def _validate_limit(limit: int) -> None:
        if not isinstance(limit, int):
            raise TypeError("limit must be an integer")

        if limit < 1:
            raise ValueError("limit must be greater than zero")