from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class AuthenticatedUser:
    user_id: str
    email: str
    active: bool = True
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "active": self.active,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class AuthResult:
    success: bool
    user: AuthenticatedUser | None = None
    message: str = ""
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "user": (
                self.user.to_dict()
                if self.user is not None
                else None
            ),
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
        }


class AuthService:
    """
    Core authentication service boundary.

    Credential verification is intentionally delegated to the concrete
    identity/password providers. This service owns authentication-state
    validation and canonical result construction.
    """

    def authenticate(
        self,
        *,
        user_id: str,
        email: str,
        authenticated: bool = True,
        active: bool = True,
        metadata: Mapping[str, Any] | None = None,
    ) -> AuthResult:
        self._validate_required(user_id, "user_id")
        self._validate_email(email)

        if not authenticated:
            return AuthResult(
                success=False,
                message="Authentication failed.",
            )

        if not active:
            return AuthResult(
                success=False,
                message="User account is inactive.",
            )

        user = AuthenticatedUser(
            user_id=user_id.strip(),
            email=email.strip(),
            active=True,
            metadata=dict(metadata or {}),
        )

        return AuthResult(
            success=True,
            user=user,
            message="Authentication successful.",
        )

    def validate_user(
        self,
        user: AuthenticatedUser,
    ) -> AuthResult:
        if not isinstance(user, AuthenticatedUser):
            raise TypeError(
                "user must be an AuthenticatedUser"
            )

        if not user.active:
            return AuthResult(
                success=False,
                message="User account is inactive.",
            )

        return AuthResult(
            success=True,
            user=user,
            message="Authenticated user is valid.",
        )

    def deactivate(
        self,
        user: AuthenticatedUser,
    ) -> AuthResult:
        if not isinstance(user, AuthenticatedUser):
            raise TypeError(
                "user must be an AuthenticatedUser"
            )

        inactive_user = AuthenticatedUser(
            user_id=user.user_id,
            email=user.email,
            active=False,
            metadata=dict(user.metadata),
        )

        return AuthResult(
            success=True,
            user=inactive_user,
            message="User deactivation accepted.",
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
    def _validate_email(email: str) -> None:
        if not isinstance(email, str) or not email.strip():
            raise ValueError("email must not be empty")

        if "@" not in email.strip():
            raise ValueError("email must contain '@'")