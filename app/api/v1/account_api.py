from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class AccountProfile:
    user_id: str
    email: str
    display_name: str = ""
    plan: str = "FREE"
    active: bool = True
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "display_name": self.display_name,
            "plan": self.plan,
            "active": self.active,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class AccountResponse:
    success: bool
    action: str
    account: AccountProfile | None = None
    message: str = ""
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "action": self.action,
            "account": (
                self.account.to_dict()
                if self.account is not None
                else None
            ),
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
        }


class AccountAPI:
    """
    Account API boundary for account/profile operations.

    This layer contains API-facing validation and response construction.
    Authentication, persistence, billing, and external identity providers
    remain outside this boundary.
    """

    def get_profile(
        self,
        *,
        user_id: str,
        email: str,
        display_name: str = "",
        plan: str = "FREE",
        active: bool = True,
        metadata: Mapping[str, Any] | None = None,
    ) -> AccountResponse:
        self._validate_user_id(user_id)
        self._validate_email(email)

        profile = AccountProfile(
            user_id=user_id.strip(),
            email=email.strip(),
            display_name=display_name.strip(),
            plan=plan.strip().upper() or "FREE",
            active=bool(active),
            metadata=dict(metadata or {}),
        )

        return AccountResponse(
            success=True,
            action="GET_PROFILE",
            account=profile,
            message="Account profile retrieved successfully.",
        )

    def update_profile(
        self,
        *,
        user_id: str,
        email: str | None = None,
        display_name: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> AccountResponse:
        self._validate_user_id(user_id)

        if email is not None:
            self._validate_email(email)

        profile = AccountProfile(
            user_id=user_id.strip(),
            email=email.strip() if email is not None else "",
            display_name=(
                display_name.strip()
                if display_name is not None
                else ""
            ),
            metadata=dict(metadata or {}),
        )

        return AccountResponse(
            success=True,
            action="UPDATE_PROFILE",
            account=profile,
            message="Account profile updated successfully.",
        )

    def deactivate_account(
        self,
        *,
        user_id: str,
        email: str,
    ) -> AccountResponse:
        self._validate_user_id(user_id)
        self._validate_email(email)

        profile = AccountProfile(
            user_id=user_id.strip(),
            email=email.strip(),
            active=False,
        )

        return AccountResponse(
            success=True,
            action="DEACTIVATE_ACCOUNT",
            account=profile,
            message="Account deactivation requested successfully.",
        )

    @staticmethod
    def _validate_user_id(user_id: str) -> None:
        if not isinstance(user_id, str) or not user_id.strip():
            raise ValueError("user_id must not be empty")

    @staticmethod
    def _validate_email(email: str) -> None:
        if not isinstance(email, str) or not email.strip():
            raise ValueError("email must not be empty")

        normalized = email.strip()

        if "@" not in normalized:
            raise ValueError("email must contain '@'")