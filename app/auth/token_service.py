from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from secrets import token_urlsafe
from threading import RLock
from typing import Any


@dataclass(frozen=True)
class TokenRecord:
    token_id: str
    user_id: str
    issued_at: datetime
    expires_at: datetime
    revoked: bool = False
    metadata: dict[str, Any] | None = None

    def is_expired(self, now: datetime | None = None) -> bool:
        current = now or datetime.now(timezone.utc)
        return current >= self.expires_at

    def is_active(self, now: datetime | None = None) -> bool:
        return not self.revoked and not self.is_expired(now)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["issued_at"] = self.issued_at.isoformat()
        data["expires_at"] = self.expires_at.isoformat()
        return data


@dataclass(frozen=True)
class TokenResult:
    success: bool
    user_id: str | None
    token: str | None
    expires_at: datetime | None
    message: str
    timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "user_id": self.user_id,
            "token": self.token,
            "expires_at": (
                self.expires_at.isoformat()
                if self.expires_at is not None
                else None
            ),
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
        }


class TokenService:
    """
    In-memory authentication token service.

    Responsibilities:
    - Secure token creation
    - Token hashing before storage
    - Expiration enforcement
    - Token validation
    - Individual token revocation
    - User-wide token revocation
    - Expired-token cleanup
    - Active-token statistics

    Raw token values are never stored in the registry.
    """

    DEFAULT_TTL_SECONDS = 3600
    MIN_TTL_SECONDS = 60
    MAX_TTL_SECONDS = 86400

    def __init__(self, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> None:
        if not isinstance(ttl_seconds, int):
            raise TypeError("ttl_seconds must be an integer")

        if not (
            self.MIN_TTL_SECONDS
            <= ttl_seconds
            <= self.MAX_TTL_SECONDS
        ):
            raise ValueError(
                f"ttl_seconds must be between "
                f"{self.MIN_TTL_SECONDS} and "
                f"{self.MAX_TTL_SECONDS}"
            )

        self.ttl_seconds = ttl_seconds
        self._tokens: dict[str, TokenRecord] = {}
        self._lock = RLock()

    # ------------------------------------------------------------------
    # Token creation
    # ------------------------------------------------------------------

    def issue(
        self,
        user_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> TokenResult:
        timestamp = self._utc_now()

        validation_error = self._validate_user_id(user_id)
        if validation_error:
            return self._failure(
                message=validation_error,
                timestamp=timestamp,
            )

        raw_token = token_urlsafe(32)
        token_id = self._fingerprint(raw_token)
        expires_at = timestamp + timedelta(seconds=self.ttl_seconds)

        record = TokenRecord(
            token_id=token_id,
            user_id=user_id.strip(),
            issued_at=timestamp,
            expires_at=expires_at,
            revoked=False,
            metadata=dict(metadata) if metadata else None,
        )

        with self._lock:
            self._tokens[token_id] = record

        return TokenResult(
            success=True,
            user_id=record.user_id,
            token=raw_token,
            expires_at=expires_at,
            message="Token issued successfully",
            timestamp=timestamp,
        )

    # ------------------------------------------------------------------
    # Token validation
    # ------------------------------------------------------------------

    def validate(self, token: str) -> TokenResult:
        timestamp = self._utc_now()

        validation_error = self._validate_token(token)
        if validation_error:
            return self._failure(
                message=validation_error,
                timestamp=timestamp,
            )

        token_id = self._fingerprint(token)

        with self._lock:
            record = self._tokens.get(token_id)

            if record is None:
                return self._failure(
                    message="Token not found",
                    timestamp=timestamp,
                )

            if record.revoked:
                return self._failure(
                    user_id=record.user_id,
                    expires_at=record.expires_at,
                    message="Token has been revoked",
                    timestamp=timestamp,
                )

            if record.is_expired(timestamp):
                return self._failure(
                    user_id=record.user_id,
                    expires_at=record.expires_at,
                    message="Token has expired",
                    timestamp=timestamp,
                )

            return TokenResult(
                success=True,
                user_id=record.user_id,
                token=None,
                expires_at=record.expires_at,
                message="Token is valid",
                timestamp=timestamp,
            )

    def is_valid(self, token: str) -> bool:
        return self.validate(token).success

    # ------------------------------------------------------------------
    # Individual revocation
    # ------------------------------------------------------------------

    def revoke(self, token: str) -> TokenResult:
        timestamp = self._utc_now()

        validation_error = self._validate_token(token)
        if validation_error:
            return self._failure(
                message=validation_error,
                timestamp=timestamp,
            )

        token_id = self._fingerprint(token)

        with self._lock:
            record = self._tokens.get(token_id)

            if record is None:
                return self._failure(
                    message="Token not found",
                    timestamp=timestamp,
                )

            if record.revoked:
                return self._failure(
                    user_id=record.user_id,
                    expires_at=record.expires_at,
                    message="Token is already revoked",
                    timestamp=timestamp,
                )

            revoked_record = TokenRecord(
                token_id=record.token_id,
                user_id=record.user_id,
                issued_at=record.issued_at,
                expires_at=record.expires_at,
                revoked=True,
                metadata=record.metadata,
            )

            self._tokens[token_id] = revoked_record

        return TokenResult(
            success=True,
            user_id=record.user_id,
            token=None,
            expires_at=record.expires_at,
            message="Token revoked successfully",
            timestamp=timestamp,
        )

    # ------------------------------------------------------------------
    # User-wide revocation
    # ------------------------------------------------------------------

    def revoke_all_for_user(self, user_id: str) -> int:
        validation_error = self._validate_user_id(user_id)
        if validation_error:
            raise ValueError(validation_error)

        normalized_user_id = user_id.strip()
        revoked_count = 0

        with self._lock:
            for token_id, record in list(self._tokens.items()):
                if (
                    record.user_id == normalized_user_id
                    and not record.revoked
                ):
                    self._tokens[token_id] = TokenRecord(
                        token_id=record.token_id,
                        user_id=record.user_id,
                        issued_at=record.issued_at,
                        expires_at=record.expires_at,
                        revoked=True,
                        metadata=record.metadata,
                    )
                    revoked_count += 1

        return revoked_count

    # ------------------------------------------------------------------
    # Registry inspection
    # ------------------------------------------------------------------

    def get_record(self, token: str) -> TokenRecord | None:
        validation_error = self._validate_token(token)
        if validation_error:
            return None

        token_id = self._fingerprint(token)

        with self._lock:
            return self._tokens.get(token_id)

    def active_token_count(self) -> int:
        now = self._utc_now()

        with self._lock:
            return sum(
                1
                for record in self._tokens.values()
                if record.is_active(now)
            )

    def token_count_for_user(
        self,
        user_id: str,
        active_only: bool = True,
    ) -> int:
        validation_error = self._validate_user_id(user_id)
        if validation_error:
            raise ValueError(validation_error)

        normalized_user_id = user_id.strip()
        now = self._utc_now()

        with self._lock:
            if active_only:
                return sum(
                    1
                    for record in self._tokens.values()
                    if (
                        record.user_id == normalized_user_id
                        and record.is_active(now)
                    )
                )

            return sum(
                1
                for record in self._tokens.values()
                if record.user_id == normalized_user_id
            )

    def cleanup_expired(self) -> int:
        now = self._utc_now()
        removed_count = 0

        with self._lock:
            expired_ids = [
                token_id
                for token_id, record in self._tokens.items()
                if record.is_expired(now)
            ]

            for token_id in expired_ids:
                del self._tokens[token_id]
                removed_count += 1

        return removed_count

    def clear(self) -> None:
        with self._lock:
            self._tokens.clear()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _fingerprint(token: str) -> str:
        return sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def _validate_user_id(user_id: str) -> str | None:
        if not isinstance(user_id, str):
            return "user_id must be a string"

        if not user_id.strip():
            return "user_id is required"

        return None

    @staticmethod
    def _validate_token(token: str) -> str | None:
        if not isinstance(token, str):
            return "token must be a string"

        if not token.strip():
            return "token is required"

        return None

    @staticmethod
    def _failure(
        message: str,
        timestamp: datetime,
        user_id: str | None = None,
        expires_at: datetime | None = None,
    ) -> TokenResult:
        return TokenResult(
            success=False,
            user_id=user_id,
            token=None,
            expires_at=expires_at,
            message=message,
            timestamp=timestamp,
        )