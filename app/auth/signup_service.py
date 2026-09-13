from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class SignupRequest:
    email: str
    password: str
    display_name: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SignupResult:
    success: bool
    user_id: str | None = None
    message: str = ""
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "user_id": self.user_id,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
        }


class SignupService:
    """
    Account registration service boundary.

    Identity persistence, password hashing, email verification, and
    entitlement provisioning are delegated to their respective services.
    This service validates registration requests and creates canonical
    signup results.
    """

    def validate_request(
        self,
        request: SignupRequest,
    ) -> SignupResult:
        if not isinstance(request, SignupRequest):
            raise TypeError(
                "request must be a SignupRequest"
            )

        self._validate_email(request.email)
        self._validate_password(request.password)

        return SignupResult(
            success=True,
            message="Signup request is valid.",
        )

    def signup(
        self,
        *,
        email: str,
        password: str,
        user_id: str | None = None,
        display_name: str = "",
        metadata: Mapping[str, Any] | None = None,
    ) -> SignupResult:
        self._validate_email(email)
        self._validate_password(password)

        if user_id is not None:
            self._validate_required(
                user_id,
                "user_id",
            )

        return SignupResult(
            success=True,
            user_id=(
                user_id.strip()
                if user_id is not None
                else None
            ),
            message="Signup request accepted.",
        )

    def check_email(
        self,
        *,
        email: str,
        available: bool = True,
    ) -> SignupResult:
        self._validate_email(email)

        if not available:
            return SignupResult(
                success=False,
                message="Email is already registered.",
            )

        return SignupResult(
            success=True,
            message="Email is available.",
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
    def _validate_password(
        password: str,
    ) -> None:
        if not isinstance(password, str):
            raise TypeError(
                "password must be a string"
            )

        if not password:
            raise ValueError(
                "password must not be empty"
            )