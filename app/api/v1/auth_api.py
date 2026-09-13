from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class AuthRequest:
    email: str
    password: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AuthResponse:
    success: bool
    action: str
    user_id: str | None = None
    message: str = ""
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "action": self.action,
            "user_id": self.user_id,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
        }


class AuthAPI:
    """
    API-facing authentication boundary.

    Credential verification and session/token persistence are delegated
    to the authentication service layer. This class performs request
    validation and produces canonical API responses.
    """

    def validate_request(
        self,
        request: AuthRequest,
    ) -> AuthResponse:
        if not isinstance(request, AuthRequest):
            raise TypeError("request must be an AuthRequest")

        self._validate_email(request.email)
        self._validate_password(request.password)

        return AuthResponse(
            success=True,
            action="VALIDATE_AUTH_REQUEST",
            message="Authentication request is valid.",
        )

    def login(
        self,
        *,
        email: str,
        password: str,
        user_id: str | None = None,
    ) -> AuthResponse:
        self._validate_email(email)
        self._validate_password(password)

        return AuthResponse(
            success=True,
            action="LOGIN",
            user_id=user_id.strip() if user_id else None,
            message="Authentication request accepted.",
        )

    def signup(
        self,
        *,
        email: str,
        password: str,
        user_id: str | None = None,
    ) -> AuthResponse:
        self._validate_email(email)
        self._validate_password(password)

        return AuthResponse(
            success=True,
            action="SIGNUP",
            user_id=user_id.strip() if user_id else None,
            message="Account registration request accepted.",
        )

    def logout(
        self,
        *,
        user_id: str,
    ) -> AuthResponse:
        if not isinstance(user_id, str) or not user_id.strip():
            raise ValueError("user_id must not be empty")

        return AuthResponse(
            success=True,
            action="LOGOUT",
            user_id=user_id.strip(),
            message="Logout request accepted.",
        )

    def forgot_password(
        self,
        *,
        email: str,
    ) -> AuthResponse:
        self._validate_email(email)

        return AuthResponse(
            success=True,
            action="FORGOT_PASSWORD",
            message="Password recovery request accepted.",
        )

    @staticmethod
    def _validate_email(email: str) -> None:
        if not isinstance(email, str) or not email.strip():
            raise ValueError("email must not be empty")

        if "@" not in email.strip():
            raise ValueError("email must contain '@'")

    @staticmethod
    def _validate_password(password: str) -> None:
        if not isinstance(password, str) or not password:
            raise ValueError("password must not be empty")