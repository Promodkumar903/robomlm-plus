from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class ResearchRequest:
    user_id: str
    query: str
    market: str = ""
    parameters: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ResearchResponse:
    success: bool
    action: str
    user_id: str | None = None
    query: str | None = None
    market: str | None = None
    findings: tuple[Mapping[str, Any], ...] = ()
    message: str = ""
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "action": self.action,
            "user_id": self.user_id,
            "query": self.query,
            "market": self.market,
            "findings": [dict(item) for item in self.findings],
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
        }


class ResearchAPI:
    """
    API-facing boundary for ROBOMLM Research operations.

    This layer validates research requests and provides a canonical
    response structure. Actual research execution, evidence collection,
    analysis, experimentation, and learning remain delegated to the
    corresponding application services.
    """

    def validate_request(
        self,
        request: ResearchRequest,
    ) -> ResearchResponse:
        if not isinstance(request, ResearchRequest):
            raise TypeError(
                "request must be a ResearchRequest"
            )

        self._validate_required(request.user_id, "user_id")
        self._validate_required(request.query, "query")

        return ResearchResponse(
            success=True,
            action="VALIDATE_RESEARCH_REQUEST",
            user_id=request.user_id.strip(),
            query=request.query.strip(),
            market=request.market.strip() or None,
            message="Research request is valid.",
        )

    def analyze(
        self,
        *,
        user_id: str,
        query: str,
        market: str = "",
        parameters: Mapping[str, Any] | None = None,
    ) -> ResearchResponse:
        self._validate_required(user_id, "user_id")
        self._validate_required(query, "query")

        return ResearchResponse(
            success=True,
            action="ANALYZE",
            user_id=user_id.strip(),
            query=query.strip(),
            market=market.strip() or None,
            message="Research analysis request accepted.",
        )

    def deep_analysis(
        self,
        *,
        user_id: str,
        query: str,
        market: str = "",
        evidence: Mapping[str, Any] | None = None,
    ) -> ResearchResponse:
        self._validate_required(user_id, "user_id")
        self._validate_required(query, "query")

        findings = (
            (dict(evidence),)
            if isinstance(evidence, Mapping)
            else ()
        )

        return ResearchResponse(
            success=True,
            action="DEEP_ANALYSIS",
            user_id=user_id.strip(),
            query=query.strip(),
            market=market.strip() or None,
            findings=findings,
            message="Deep research analysis request accepted.",
        )

    def submit_finding(
        self,
        *,
        user_id: str,
        query: str,
        finding: Mapping[str, Any],
        market: str = "",
    ) -> ResearchResponse:
        self._validate_required(user_id, "user_id")
        self._validate_required(query, "query")

        if not isinstance(finding, Mapping):
            raise TypeError("finding must be a mapping")

        return ResearchResponse(
            success=True,
            action="SUBMIT_FINDING",
            user_id=user_id.strip(),
            query=query.strip(),
            market=market.strip() or None,
            findings=(dict(finding),),
            message="Research finding accepted.",
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