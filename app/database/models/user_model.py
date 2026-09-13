"""
ROBOMLM PLUS
User Database Model

Purpose:
    Define the persistent identity and account state of a ROBOMLM user.

Design:
    - Stores application-level user identity and account metadata.
    - Authentication secrets are NOT stored here.
    - Password hashing belongs to the security/authentication layer.
    - Authorization and entitlement decisions belong to their respective services.
    - No broker/exchange interaction.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Optional
from uuid import uuid4


@dataclass
class UserRecord:
    """Structured application user record."""

    user_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    username: str = ""

    email: str = ""

    display_name: Optional[str] = None

    status: str = "active"

    user_type: str = "buyer"

    email_verified: bool = False

    phone_verified: bool = False

    timezone: str = "UTC"

    locale: str = "en-IN"

    country: Optional[str] = None

    last_login_at: Optional[datetime] = None

    last_activity_at: Optional[datetime] = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        """Normalize and validate user fields."""

        self.user_id = str(
            self.user_id
        ).strip()

        self.username = str(
            self.username
        ).strip()

        self.email = str(
            self.email
        ).strip().lower()

        self.status = str(
            self.status
        ).strip().lower()

        self.user_type = str(
            self.user_type
        ).strip().lower()

        self.timezone = str(
            self.timezone
        ).strip() or "UTC"

        self.locale = str(
            self.locale
        ).strip() or "en-IN"

        if not self.user_id:
            raise ValueError(
                "user_id cannot be empty."
            )

        if not self.username:
            raise ValueError(
                "username cannot be empty."
            )

        if not self.email:
            raise ValueError(
                "email cannot be empty."
            )

        if not self.status:
            raise ValueError(
                "status cannot be empty."
            )

        if not self.user_type:
            raise ValueError(
                "user_type cannot be empty."
            )

        self.display_name = (
            self._clean_optional(
                self.display_name
            )
        )

        self.country = (
            self._clean_optional(
                self.country
            )
        )

        if not isinstance(
            self.email_verified,
            bool,
        ):
            raise TypeError(
                "email_verified must be a boolean."
            )

        if not isinstance(
            self.phone_verified,
            bool,
        ):
            raise TypeError(
                "phone_verified must be a boolean."
            )

        if not isinstance(self.metadata, dict):
            self.metadata = dict(
                self.metadata
            )

        self.last_login_at = (
            self._normalize_optional_datetime(
                self.last_login_at
            )
        )

        self.last_activity_at = (
            self._normalize_optional_datetime(
                self.last_activity_at
            )
        )

        self.created_at = (
            self._normalize_datetime(
                self.created_at
            )
        )

        self.updated_at = (
            self._normalize_datetime(
                self.updated_at
            )
        )

    @staticmethod
    def _clean_optional(
        value: Optional[Any],
    ) -> Optional[str]:
        """Normalize an optional string."""

        if value is None:
            return None

        cleaned = str(value).strip()

        return cleaned or None

    @staticmethod
    def _normalize_datetime(
        value: datetime,
    ) -> datetime:
        """Normalize datetime to timezone-aware UTC."""

        if not isinstance(value, datetime):
            raise TypeError(
                "Datetime value must be a datetime instance."
            )

        if value.tzinfo is None:
            return value.replace(
                tzinfo=timezone.utc
            )

        return value.astimezone(
            timezone.utc
        )

    @classmethod
    def _normalize_optional_datetime(
        cls,
        value: Optional[datetime],
    ) -> Optional[datetime]:
        """Normalize an optional datetime."""

        if value is None:
            return None

        return cls._normalize_datetime(value)

    @property
    def is_active(self) -> bool:
        """Return whether the user account is active."""

        return self.status in {
            "active",
            "enabled",
        }

    @property
    def is_disabled(self) -> bool:
        """Return whether the account is disabled."""

        return self.status in {
            "disabled",
            "suspended",
            "locked",
        }

    @property
    def is_verified(self) -> bool:
        """Return whether the email address is verified."""

        return self.email_verified

    def activate(self) -> None:
        """Activate the user account."""

        self.status = "active"
        self.touch()

    def disable(self) -> None:
        """Disable the user account."""

        self.status = "disabled"
        self.touch()

    def suspend(self) -> None:
        """Suspend the user account."""

        self.status = "suspended"
        self.touch()

    def verify_email(self) -> None:
        """Mark the user's email as verified."""

        self.email_verified = True
        self.touch()

    def unverify_email(self) -> None:
        """Remove the email verification state."""

        self.email_verified = False
        self.touch()

    def verify_phone(self) -> None:
        """Mark the user's phone as verified."""

        self.phone_verified = True
        self.touch()

    def unverify_phone(self) -> None:
        """Remove the phone verification state."""

        self.phone_verified = False
        self.touch()

    def record_login(
        self,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Record a successful login."""

        login_time = (
            self._normalize_datetime(timestamp)
            if timestamp is not None
            else datetime.now(timezone.utc)
        )

        self.last_login_at = login_time
        self.last_activity_at = login_time

        self.touch()

    def record_activity(
        self,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Record user activity."""

        self.last_activity_at = (
            self._normalize_datetime(timestamp)
            if timestamp is not None
            else datetime.now(timezone.utc)
        )

        self.touch()

    def update_display_name(
        self,
        display_name: Optional[str],
    ) -> None:
        """Update the display name."""

        self.display_name = (
            self._clean_optional(
                display_name
            )
        )

        self.touch()

    def update_email(
        self,
        email: str,
    ) -> None:
        """Update email and reset email verification."""

        email = str(email).strip().lower()

        if not email:
            raise ValueError(
                "email cannot be empty."
            )

        self.email = email
        self.email_verified = False

        self.touch()

    def update_username(
        self,
        username: str,
    ) -> None:
        """Update username."""

        username = str(username).strip()

        if not username:
            raise ValueError(
                "username cannot be empty."
            )

        self.username = username

        self.touch()

    def update_locale(
        self,
        locale: str,
    ) -> None:
        """Update locale."""

        locale = str(locale).strip()

        if not locale:
            raise ValueError(
                "locale cannot be empty."
            )

        self.locale = locale

        self.touch()

    def update_timezone(
        self,
        timezone_name: str,
    ) -> None:
        """Update timezone identifier."""

        timezone_name = str(
            timezone_name
        ).strip()

        if not timezone_name:
            raise ValueError(
                "timezone cannot be empty."
            )

        self.timezone = timezone_name

        self.touch()

    def add_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Add or replace user metadata."""

        key = str(key).strip()

        if not key:
            raise ValueError(
                "Metadata key cannot be empty."
            )

        self.metadata[key] = value

        self.touch()

    def remove_metadata(
        self,
        key: str,
    ) -> bool:
        """Remove metadata if present."""

        key = str(key).strip()

        if key in self.metadata:
            del self.metadata[key]
            self.touch()
            return True

        return False

    def touch(self) -> None:
        """Update modification timestamp."""

        self.updated_at = datetime.now(
            timezone.utc
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable dictionary."""

        data = asdict(self)

        for field_name in (
            "last_login_at",
            "last_activity_at",
            "created_at",
            "updated_at",
        ):
            value = getattr(self, field_name)

            if value is not None:
                data[field_name] = value.isoformat()

        return data

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "UserRecord":
        """Create a user record from a mapping."""

        if not isinstance(data, Mapping):
            raise TypeError(
                "data must be a mapping."
            )

        values = dict(data)

        for field_name in (
            "last_login_at",
            "last_activity_at",
            "created_at",
            "updated_at",
        ):
            value = values.get(field_name)

            if isinstance(value, str):
                values[field_name] = (
                    datetime.fromisoformat(value)
                )

        return cls(**values)


def create_user_record(
    *,
    username: str,
    email: str,
    user_type: str = "buyer",
    status: str = "active",
    display_name: Optional[str] = None,
    email_verified: bool = False,
    phone_verified: bool = False,
    timezone: str = "UTC",
    locale: str = "en-IN",
    country: Optional[str] = None,
    metadata: Optional[
        Mapping[str, Any]
    ] = None,
) -> UserRecord:
    """Convenience factory for creating a user record."""

    return UserRecord(
        username=username,
        email=email,
        user_type=user_type,
        status=status,
        display_name=display_name,
        email_verified=email_verified,
        phone_verified=phone_verified,
        timezone=timezone,
        locale=locale,
        country=country,
        metadata=dict(
            metadata or {}
        ),
    )


__all__ = [
    "UserRecord",
    "create_user_record",
]