from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class AutomationRequest:
    automation_id: str
    action: str
    parameters: Mapping[str, Any] = field(default_factory=dict)
    enabled: bool = True


@dataclass(frozen=True)
class AutomationResponse:
    success: bool
    action: str
    automation_id: str | None = None
    enabled: bool = False
    message: str = ""
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "action": self.action,
            "automation_id": self.automation_id,
            "enabled": self.enabled,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
        }


class AutomationAPI:
    """
    API-facing boundary for AUTOROBOMLM automation requests.

    This layer validates and describes automation operations.
    Actual execution, authorization, risk gates, and broker/execution
    integration remain delegated to their respective services.
    """

    def validate_request(
        self,
        request: AutomationRequest,
    ) -> AutomationResponse:
        if not isinstance(request, AutomationRequest):
            raise TypeError(
                "request must be an AutomationRequest"
            )

        self._validate_required(
            request.automation_id,
            "automation_id",
        )
        self._validate_required(
            request.action,
            "action",
        )

        return AutomationResponse(
            success=True,
            action="VALIDATE_AUTOMATION",
            automation_id=request.automation_id.strip(),
            enabled=request.enabled,
            message="Automation request is valid.",
        )

    def create(
        self,
        *,
        automation_id: str,
        action: str,
        parameters: Mapping[str, Any] | None = None,
    ) -> AutomationResponse:
        self._validate_required(
            automation_id,
            "automation_id",
        )
        self._validate_required(action, "action")

        return AutomationResponse(
            success=True,
            action="CREATE_AUTOMATION",
            automation_id=automation_id.strip(),
            enabled=True,
            message="Automation request created successfully.",
        )

    def enable(
        self,
        *,
        automation_id: str,
    ) -> AutomationResponse:
        self._validate_required(
            automation_id,
            "automation_id",
        )

        return AutomationResponse(
            success=True,
            action="ENABLE_AUTOMATION",
            automation_id=automation_id.strip(),
            enabled=True,
            message="Automation enable request accepted.",
        )

    def disable(
        self,
        *,
        automation_id: str,
    ) -> AutomationResponse:
        self._validate_required(
            automation_id,
            "automation_id",
        )

        return AutomationResponse(
            success=True,
            action="DISABLE_AUTOMATION",
            automation_id=automation_id.strip(),
            enabled=False,
            message="Automation disable request accepted.",
        )

    def reject(
        self,
        *,
        automation_id: str,
        reason: str,
    ) -> AutomationResponse:
        self._validate_required(
            automation_id,
            "automation_id",
        )
        self._validate_required(reason, "reason")

        return AutomationResponse(
            success=False,
            action="REJECT_AUTOMATION",
            automation_id=automation_id.strip(),
            enabled=False,
            message=reason.strip(),
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