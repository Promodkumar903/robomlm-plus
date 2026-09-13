from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class LoginRequest:
    email: str
    password: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LoginResult:
    success: bool
    user_id: str | None = None
    session_id: str | None = None
    message: str = ""
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
        }


class LoginService:
    """
    Authentication login service boundary.

    Credential verification and session creation are delegated to the
    appropriate identity/token providers. This service validates the
    login request and returns a canonical login result.
    """

    def validate_request(
        self,
        request: LoginRequest,
    ) -> LoginResult:
        if not isinstance(request, LoginRequest):
            raise TypeError(
                "request must be a LoginRequest"
            )

        self._validate_email(request.email)
        self._validate_password(request.password)

        return LoginResult(
            success=True,
            message="Login request is valid.",
        )

    def login(
        self,
        *,
        email: str,
        password: str,
        user_id: str | None = None,
        session_id: str | None = None,
        authenticated: bool = True,
    ) -> LoginResult:
        self._validate_email(email)
        self._validate_password(password)

        if not authenticated:
            return LoginResult(
                success=False,
                message="Login authentication failed.",
            )

        return LoginResult(
            success=True,
            user_id=user_id.strip() if user_id else None,
            session_id=(
                session_id.strip()
                if session_id
                else None
            ),
            message="Login successful.",
        )

    def logout(
        self,
        *,
        user_id: str,
        session_id: str | None = None,
    ) -> LoginResult:
        self._validate_required(user_id, "user_id")

        return LoginResult(
            success=True,
            user_id=user_id.strip(),
            session_id=(
                session_id.strip()
                if session_id
                else None
            ),
            message="Logout request accepted.",
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

    @staticmethod
    def _validate_password(password: str) -> None:
        if not isinstance(password, str) or not password:
            raise ValueError("password must not be empty")