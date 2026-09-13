from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class BuyerRequest:
    user_id: str
    market: str
    instrument: str
    parameters: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BuyerResponse:
    success: bool
    action: str
    user_id: str | None = None
    market: str | None = None
    instrument: str | None = None
    data: Mapping[str, Any] = field(default_factory=dict)
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
            "instrument": self.instrument,
            "data": dict(self.data),
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
        }


class BuyerAPI:
    """
    API-facing boundary for ROBOMLM buyer intelligence operations.

    The API validates buyer requests and returns canonical responses.
    Actual market intelligence, evidence processing, decision generation,
    and execution remain delegated to their respective application layers.
    """

    def validate_request(
        self,
        request: BuyerRequest,
    ) -> BuyerResponse:
        if not isinstance(request, BuyerRequest):
            raise TypeError("request must be a BuyerRequest")

        self._validate_required(request.user_id, "user_id")
        self._validate_required(request.market, "market")
        self._validate_required(request.instrument, "instrument")

        return BuyerResponse(
            success=True,
            action="VALIDATE_BUYER_REQUEST",
            user_id=request.user_id.strip(),
            market=request.market.strip(),
            instrument=request.instrument.strip(),
            data=dict(request.parameters),
            message="Buyer request is valid.",
        )

    def get_market_intelligence(
        self,
        *,
        user_id: str,
        market: str,
        instrument: str,
        context: Mapping[str, Any] | None = None,
    ) -> BuyerResponse:
        self._validate_required(user_id, "user_id")
        self._validate_required(market, "market")
        self._validate_required(instrument, "instrument")

        return BuyerResponse(
            success=True,
            action="GET_MARKET_INTELLIGENCE",
            user_id=user_id.strip(),
            market=market.strip(),
            instrument=instrument.strip(),
            data=dict(context or {}),
            message="Market intelligence request accepted.",
        )

    def get_opportunity(
        self,
        *,
        user_id: str,
        market: str,
        instrument: str,
        filters: Mapping[str, Any] | None = None,
    ) -> BuyerResponse:
        self._validate_required(user_id, "user_id")
        self._validate_required(market, "market")
        self._validate_required(instrument, "instrument")

        return BuyerResponse(
            success=True,
            action="GET_OPPORTUNITY",
            user_id=user_id.strip(),
            market=market.strip(),
            instrument=instrument.strip(),
            data=dict(filters or {}),
            message="Opportunity discovery request accepted.",
        )

    def get_decision_context(
        self,
        *,
        user_id: str,
        market: str,
        instrument: str,
        evidence: Mapping[str, Any] | None = None,
    ) -> BuyerResponse:
        self._validate_required(user_id, "user_id")
        self._validate_required(market, "market")
        self._validate_required(instrument, "instrument")

        return BuyerResponse(
            success=True,
            action="GET_DECISION_CONTEXT",
            user_id=user_id.strip(),
            market=market.strip(),
            instrument=instrument.strip(),
            data=dict(evidence or {}),
            message="Decision context request accepted.",
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