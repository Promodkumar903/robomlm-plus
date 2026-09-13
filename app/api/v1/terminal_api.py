from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class TerminalRequest:
    user_id: str
    market: str
    instrument: str
    mode: str = "DEMO"
    parameters: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TerminalResponse:
    success: bool
    action: str
    user_id: str | None = None
    market: str | None = None
    instrument: str | None = None
    mode: str | None = None
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
            "mode": self.mode,
            "data": dict(self.data),
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
        }


class TerminalAPI:
    """
    API-facing boundary for the ROBOMLM professional terminal.

    This layer validates terminal requests and creates canonical API
    responses. Live market data, evidence, intelligence, decisions,
    risk controls, and execution remain delegated to their respective
    application services.
    """

    _VALID_MODES = {
        "PAPER",
        "DEMO",
        "LIVE",
    }

    def validate_request(
        self,
        request: TerminalRequest,
    ) -> TerminalResponse:
        if not isinstance(request, TerminalRequest):
            raise TypeError(
                "request must be a TerminalRequest"
            )

        self._validate_required(request.user_id, "user_id")
        self._validate_required(request.market, "market")
        self._validate_required(
            request.instrument,
            "instrument",
        )

        mode = self._normalize_mode(request.mode)

        return TerminalResponse(
            success=True,
            action="VALIDATE_TERMINAL_REQUEST",
            user_id=request.user_id.strip(),
            market=request.market.strip(),
            instrument=request.instrument.strip(),
            mode=mode,
            data=dict(request.parameters),
            message="Terminal request is valid.",
        )

    def open_terminal(
        self,
        *,
        user_id: str,
        market: str,
        instrument: str,
        mode: str = "DEMO",
    ) -> TerminalResponse:
        self._validate_required(user_id, "user_id")
        self._validate_required(market, "market")
        self._validate_required(
            instrument,
            "instrument",
        )

        normalized_mode = self._normalize_mode(mode)

        return TerminalResponse(
            success=True,
            action="OPEN_TERMINAL",
            user_id=user_id.strip(),
            market=market.strip(),
            instrument=instrument.strip(),
            mode=normalized_mode,
            message="Terminal open request accepted.",
        )

    def get_market_context(
        self,
        *,
        user_id: str,
        market: str,
        instrument: str,
        context: Mapping[str, Any] | None = None,
    ) -> TerminalResponse:
        self._validate_required(user_id, "user_id")
        self._validate_required(market, "market")
        self._validate_required(
            instrument,
            "instrument",
        )

        return TerminalResponse(
            success=True,
            action="GET_MARKET_CONTEXT",
            user_id=user_id.strip(),
            market=market.strip(),
            instrument=instrument.strip(),
            data=dict(context or {}),
            message="Market context request accepted.",
        )

    def get_evidence(
        self,
        *,
        user_id: str,
        market: str,
        instrument: str,
        evidence: Mapping[str, Any] | None = None,
    ) -> TerminalResponse:
        self._validate_required(user_id, "user_id")
        self._validate_required(market, "market")
        self._validate_required(
            instrument,
            "instrument",
        )

        return TerminalResponse(
            success=True,
            action="GET_EVIDENCE",
            user_id=user_id.strip(),
            market=market.strip(),
            instrument=instrument.strip(),
            data=dict(evidence or {}),
            message="Evidence request accepted.",
        )

    def get_decision(
        self,
        *,
        user_id: str,
        market: str,
        instrument: str,
        decision: Mapping[str, Any] | None = None,
    ) -> TerminalResponse:
        self._validate_required(user_id, "user_id")
        self._validate_required(market, "market")
        self._validate_required(
            instrument,
            "instrument",
        )

        return TerminalResponse(
            success=True,
            action="GET_DECISION",
            user_id=user_id.strip(),
            market=market.strip(),
            instrument=instrument.strip(),
            data=dict(decision or {}),
            message="Decision request accepted.",
        )

    def switch_mode(
        self,
        *,
        user_id: str,
        mode: str,
    ) -> TerminalResponse:
        self._validate_required(user_id, "user_id")

        normalized_mode = self._normalize_mode(mode)

        return TerminalResponse(
            success=True,
            action="SWITCH_MODE",
            user_id=user_id.strip(),
            mode=normalized_mode,
            message="Terminal mode switch request accepted.",
        )

    @classmethod
    def _normalize_mode(cls, mode: str) -> str:
        if not isinstance(mode, str) or not mode.strip():
            raise ValueError("mode must not be empty")

        normalized = mode.strip().upper()

        if normalized not in cls._VALID_MODES:
            raise ValueError(
                "mode must be one of: "
                + ", ".join(sorted(cls._VALID_MODES))
            )

        return normalized

    @staticmethod
    def _validate_required(
        value: str,
        field_name: str,
    ) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"{field_name} must not be empty"
            )