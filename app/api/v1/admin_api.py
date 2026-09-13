from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class AdminAction:
    action_id: str
    action_type: str
    target: str
    parameters: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "action_type": self.action_type,
            "target": self.target,
            "parameters": dict(self.parameters),
        }


@dataclass(frozen=True)
class AdminResponse:
    success: bool
    action: AdminAction | None = None
    message: str = ""
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "action": (
                self.action.to_dict()
                if self.action is not None
                else None
            ),
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
        }


class AdminAPI:
    """
    API-facing boundary for administrative operations.

    This layer validates and describes administrative requests.
    Actual authorization, persistence, deployment, rollback, and
    infrastructure execution remain delegated to their respective
    application services.
    """

    def create_action(
        self,
        *,
        action_id: str,
        action_type: str,
        target: str,
        parameters: Mapping[str, Any] | None = None,
    ) -> AdminResponse:
        self._validate_required(action_id, "action_id")
        self._validate_required(action_type, "action_type")
        self._validate_required(target, "target")

        action = AdminAction(
            action_id=action_id.strip(),
            action_type=action_type.strip().upper(),
            target=target.strip(),
            parameters=dict(parameters or {}),
        )

        return AdminResponse(
            success=True,
            action=action,
            message="Administrative action created successfully.",
        )

    def validate_action(
        self,
        action: AdminAction,
    ) -> AdminResponse:
        if not isinstance(action, AdminAction):
            raise TypeError("action must be an AdminAction")

        self._validate_required(action.action_id, "action_id")
        self._validate_required(action.action_type, "action_type")
        self._validate_required(action.target, "target")

        return AdminResponse(
            success=True,
            action=action,
            message="Administrative action is valid.",
        )

    def reject_action(
        self,
        *,
        action_id: str,
        reason: str,
    ) -> AdminResponse:
        self._validate_required(action_id, "action_id")
        self._validate_required(reason, "reason")

        action = AdminAction(
            action_id=action_id.strip(),
            action_type="REJECT",
            target="ADMIN_ACTION",
            parameters={"reason": reason.strip()},
        )

        return AdminResponse(
            success=False,
            action=action,
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