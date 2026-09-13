"""
ROBOMLM PLUS
User Repository

Purpose:
    Persistence operations for UserRecord objects.

Design:
    - Repository layer only.
    - No authentication logic.
    - No password or secret storage.
    - JSONL persistence.
    - Supports account lookup, filtering and lifecycle updates.
"""

from __future__ import annotations

import json
from pathlib import Path
from threading import RLock
from typing import Iterable, Optional

from app.database.models.user_model import UserRecord


class UserRepositoryError(Exception):
    """Base exception for user repository errors."""


class UserNotFoundError(UserRepositoryError):
    """Raised when a requested user does not exist."""


class DuplicateUserError(UserRepositoryError):
    """Raised when a unique username or email already exists."""


class UserRepository:
    """Persistent repository for UserRecord objects."""

    FILE_NAME = "users.jsonl"

    def __init__(
        self,
        storage_dir: Optional[str | Path] = None,
    ) -> None:
        if storage_dir is None:
            storage_dir = (
                Path(__file__).resolve().parents[3]
                / "robomlm_data"
                / "accounts"
            )

        self.storage_dir = Path(storage_dir)
        self.file_path = self.storage_dir / self.FILE_NAME
        self._lock = RLock()

        self._ensure_storage()

    def _ensure_storage(self) -> None:
        """Initialize repository storage."""

        try:
            self.storage_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            if not self.file_path.exists():
                self.file_path.touch()

        except OSError as exc:
            raise UserRepositoryError(
                f"Unable to initialize user storage: {exc}"
            ) from exc

    def _append_record(
        self,
        record: UserRecord,
    ) -> None:
        """Append a user record to JSONL storage."""

        try:
            with self.file_path.open(
                "a",
                encoding="utf-8",
            ) as handle:
                handle.write(
                    json.dumps(
                        record.to_dict(),
                        ensure_ascii=False,
                        separators=(",", ":"),
                    )
                    + "\n"
                )

        except OSError as exc:
            raise UserRepositoryError(
                f"Unable to write user record: {exc}"
            ) from exc

        except (TypeError, ValueError) as exc:
            raise UserRepositoryError(
                f"Unable to serialize user record: {exc}"
            ) from exc

    def _read_all(self) -> list[UserRecord]:
        """Read all user records."""

        records: list[UserRecord] = []

        if not self.file_path.exists():
            return records

        try:
            with self.file_path.open(
                "r",
                encoding="utf-8",
            ) as handle:

                for line_number, line in enumerate(
                    handle,
                    start=1,
                ):
                    line = line.strip()

                    if not line:
                        continue

                    try:
                        payload = json.loads(line)

                        records.append(
                            UserRecord.from_dict(
                                payload
                            )
                        )

                    except (
                        json.JSONDecodeError,
                        TypeError,
                        ValueError,
                    ) as exc:
                        raise UserRepositoryError(
                            "Invalid user record at "
                            f"line {line_number}: {exc}"
                        ) from exc

        except OSError as exc:
            raise UserRepositoryError(
                f"Unable to read user storage: {exc}"
            ) from exc

        return records

    def _rewrite(
        self,
        records: Iterable[UserRecord],
    ) -> None:
        """Rewrite user storage safely."""

        temp_path = (
            self.storage_dir
            / f"{self.FILE_NAME}.tmp"
        )

        try:
            with temp_path.open(
                "w",
                encoding="utf-8",
            ) as handle:

                for record in records:
                    handle.write(
                        json.dumps(
                            record.to_dict(),
                            ensure_ascii=False,
                            separators=(",", ":"),
                        )
                        + "\n"
                    )

            temp_path.replace(
                self.file_path
            )

        except OSError as exc:
            try:
                if temp_path.exists():
                    temp_path.unlink()
            except OSError:
                pass

            raise UserRepositoryError(
                f"Unable to rewrite user storage: {exc}"
            ) from exc

    def _username_exists(
        self,
        username: str,
        records: list[UserRecord],
        exclude_user_id: Optional[str] = None,
    ) -> bool:
        """Check username uniqueness."""

        username = username.strip().lower()

        return any(
            record.username.strip().lower() == username
            and record.user_id != exclude_user_id
            for record in records
        )

    def _email_exists(
        self,
        email: str,
        records: list[UserRecord],
        exclude_user_id: Optional[str] = None,
    ) -> bool:
        """Check email uniqueness."""

        email = email.strip().lower()

        return any(
            record.email.strip().lower() == email
            and record.user_id != exclude_user_id
            for record in records
        )

    def save(
        self,
        record: UserRecord,
    ) -> UserRecord:
        """Persist a new user."""

        if not isinstance(
            record,
            UserRecord,
        ):
            raise TypeError(
                "record must be a UserRecord."
            )

        with self._lock:
            records = self._read_all()

            if self._username_exists(
                record.username,
                records,
            ):
                raise DuplicateUserError(
                    f"Username already exists: "
                    f"{record.username}"
                )

            if self._email_exists(
                record.email,
                records,
            ):
                raise DuplicateUserError(
                    f"Email already exists: "
                    f"{record.email}"
                )

            self._append_record(record)

        return record

    def create(
        self,
        record: UserRecord,
    ) -> UserRecord:
        """Alias for save()."""

        return self.save(record)

    def get_by_id(
        self,
        user_id: str,
    ) -> Optional[UserRecord]:
        """Return a user by ID."""

        user_id = str(user_id).strip()

        if not user_id:
            raise ValueError(
                "user_id cannot be empty."
            )

        with self._lock:
            records = self._read_all()

        for record in reversed(records):
            if record.user_id == user_id:
                return record

        return None

    def require_by_id(
        self,
        user_id: str,
    ) -> UserRecord:
        """Return a user or raise if absent."""

        record = self.get_by_id(user_id)

        if record is None:
            raise UserNotFoundError(
                f"User not found: {user_id}"
            )

        return record

    def exists(
        self,
        user_id: str,
    ) -> bool:
        """Check whether a user exists."""

        return self.get_by_id(user_id) is not None

    def get_by_username(
        self,
        username: str,
    ) -> Optional[UserRecord]:
        """Find a user by username."""

        username = str(username).strip().lower()

        if not username:
            raise ValueError(
                "username cannot be empty."
            )

        with self._lock:
            records = self._read_all()

        for record in reversed(records):
            if record.username.strip().lower() == username:
                return record

        return None

    def require_by_username(
        self,
        username: str,
    ) -> UserRecord:
        """Find a user by username or raise."""

        record = self.get_by_username(username)

        if record is None:
            raise UserNotFoundError(
                f"User not found for username: {username}"
            )

        return record

    def get_by_email(
        self,
        email: str,
    ) -> Optional[UserRecord]:
        """Find a user by email."""

        email = str(email).strip().lower()

        if not email:
            raise ValueError(
                "email cannot be empty."
            )

        with self._lock:
            records = self._read_all()

        for record in reversed(records):
            if record.email.strip().lower() == email:
                return record

        return None

    def require_by_email(
        self,
        email: str,
    ) -> UserRecord:
        """Find a user by email or raise."""

        record = self.get_by_email(email)

        if record is None:
            raise UserNotFoundError(
                f"User not found for email: {email}"
            )

        return record

    def list_all(self) -> list[UserRecord]:
        """Return all users."""

        with self._lock:
            return self._read_all()

    def count(self) -> int:
        """Return total user count."""

        with self._lock:
            return len(self._read_all())

    def find_by_status(
        self,
        status: str,
    ) -> list[UserRecord]:
        """Return users with a specific account status."""

        status = str(status).strip().lower()

        if not status:
            raise ValueError(
                "status cannot be empty."
            )

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if record.status.lower() == status
        ]

    def find_by_user_type(
        self,
        user_type: str,
    ) -> list[UserRecord]:
        """Return users of a specific user type."""

        user_type = str(user_type).strip().upper()

        if not user_type:
            raise ValueError(
                "user_type cannot be empty."
            )

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if record.user_type.upper() == user_type
        ]

    def find_by_country(
        self,
        country: str,
    ) -> list[UserRecord]:
        """Return users for a country."""

        country = str(country).strip()

        if not country:
            raise ValueError(
                "country cannot be empty."
            )

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if record.country == country
        ]

    def find_verified(self) -> list[UserRecord]:
        """Return verified users."""

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if record.is_verified
        ]

    def find_unverified(self) -> list[UserRecord]:
        """Return unverified users."""

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if not record.is_verified
        ]

    def find_active(self) -> list[UserRecord]:
        """Return active users."""

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if record.is_active
        ]

    def find_suspended(self) -> list[UserRecord]:
        """Return suspended users."""

        with self._lock:
            records = self._read_all()

        return [
            record
            for record in records
            if record.is_suspended
        ]

    def update(
        self,
        record: UserRecord,
    ) -> UserRecord:
        """Replace an existing user record."""

        if not isinstance(
            record,
            UserRecord,
        ):
            raise TypeError(
                "record must be a UserRecord."
            )

        with self._lock:
            records = self._read_all()

            if self._username_exists(
                record.username,
                records,
                exclude_user_id=record.user_id,
            ):
                raise DuplicateUserError(
                    f"Username already exists: "
                    f"{record.username}"
                )

            if self._email_exists(
                record.email,
                records,
                exclude_user_id=record.user_id,
            ):
                raise DuplicateUserError(
                    f"Email already exists: "
                    f"{record.email}"
                )

            found = False
            updated: list[UserRecord] = []

            for existing in records:
                if existing.user_id == record.user_id:
                    updated.append(record)
                    found = True
                else:
                    updated.append(existing)

            if not found:
                raise UserNotFoundError(
                    f"User not found: {record.user_id}"
                )

            self._rewrite(updated)

        return record

    def replace(
        self,
        record: UserRecord,
    ) -> UserRecord:
        """Alias for update()."""

        return self.update(record)

    def activate(
        self,
        user_id: str,
    ) -> UserRecord:
        """Activate a user."""

        record = self.require_by_id(user_id)

        record.activate()

        return self.update(record)

    def suspend(
        self,
        user_id: str,
    ) -> UserRecord:
        """Suspend a user."""

        record = self.require_by_id(user_id)

        record.suspend()

        return self.update(record)

    def verify(
        self,
        user_id: str,
    ) -> UserRecord:
        """Mark a user as verified."""

        record = self.require_by_id(user_id)

        record.verify()

        return self.update(record)

    def record_login(
        self,
        user_id: str,
    ) -> UserRecord:
        """Record successful user activity/login."""

        record = self.require_by_id(user_id)

        record.record_login()

        return self.update(record)

    def update_activity(
        self,
        user_id: str,
    ) -> UserRecord:
        """Update the user's activity timestamp."""

        record = self.require_by_id(user_id)

        record.update_activity()

        return self.update(record)

    def set_profile(
        self,
        user_id: str,
        display_name: Optional[str] = None,
        timezone: Optional[str] = None,
        locale: Optional[str] = None,
        country: Optional[str] = None,
    ) -> UserRecord:
        """Update safe profile fields."""

        record = self.require_by_id(user_id)

        record.set_profile(
            display_name=display_name,
            timezone=timezone,
            locale=locale,
            country=country,
        )

        return self.update(record)

    def add_metadata(
        self,
        user_id: str,
        key: str,
        value: object,
    ) -> UserRecord:
        """Add or update user metadata."""

        record = self.require_by_id(user_id)

        record.add_metadata(
            key,
            value,
        )

        return self.update(record)

    def delete(
        self,
        user_id: str,
    ) -> bool:
        """Delete a user record."""

        user_id = str(user_id).strip()

        if not user_id:
            raise ValueError(
                "user_id cannot be empty."
            )

        with self._lock:
            records = self._read_all()

            remaining = [
                record
                for record in records
                if record.user_id != user_id
            ]

            if len(remaining) == len(records):
                return False

            self._rewrite(remaining)

            return True

    def latest(
        self,
        limit: int = 10,
    ) -> list[UserRecord]:
        """Return latest users."""

        limit = int(limit)

        if limit <= 0:
            raise ValueError(
                "limit must be greater than zero."
            )

        with self._lock:
            records = self._read_all()

        records.sort(
            key=lambda record: (
                record.created_at
            )
        )

        return records[-limit:][::-1]

    def clear(self) -> None:
        """Clear all users. Administrative/destructive operation."""

        with self._lock:
            self._rewrite([])


user_repository = UserRepository()


def get_user_repository() -> UserRepository:
    """Return the global user repository."""

    return user_repository


__all__ = [
    "UserRepositoryError",
    "UserNotFoundError",
    "DuplicateUserError",
    "UserRepository",
    "user_repository",
    "get_user_repository",
]