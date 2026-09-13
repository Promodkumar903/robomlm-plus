from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass


@dataclass(frozen=True)
class PasswordHash:
    salt: str
    digest: str
    iterations: int

    def to_dict(self) -> dict[str, str | int]:
        return {
            "salt": self.salt,
            "digest": self.digest,
            "iterations": self.iterations,
        }


class PasswordService:
    """
    Password hashing and verification boundary.

    Passwords are never stored directly. A random salt and PBKDF2-HMAC
    derived digest are used for deterministic verification.
    """

    DEFAULT_ITERATIONS = 310_000
    HASH_NAME = "sha256"

    def hash_password(
        self,
        password: str,
    ) -> PasswordHash:
        self._validate_password(password)

        salt = secrets.token_bytes(32)

        digest = hashlib.pbkdf2_hmac(
            self.HASH_NAME,
            password.encode("utf-8"),
            salt,
            self.DEFAULT_ITERATIONS,
        )

        return PasswordHash(
            salt=salt.hex(),
            digest=digest.hex(),
            iterations=self.DEFAULT_ITERATIONS,
        )

    def verify_password(
        self,
        password: str,
        password_hash: PasswordHash,
    ) -> bool:
        self._validate_password(password)

        if not isinstance(password_hash, PasswordHash):
            raise TypeError(
                "password_hash must be a PasswordHash"
            )

        try:
            salt = bytes.fromhex(password_hash.salt)
            expected_digest = bytes.fromhex(
                password_hash.digest
            )
        except ValueError:
            return False

        if password_hash.iterations <= 0:
            return False

        actual_digest = hashlib.pbkdf2_hmac(
            self.HASH_NAME,
            password.encode("utf-8"),
            salt,
            password_hash.iterations,
        )

        return hmac.compare_digest(
            actual_digest,
            expected_digest,
        )

    def validate_hash(
        self,
        password_hash: PasswordHash,
    ) -> bool:
        if not isinstance(password_hash, PasswordHash):
            raise TypeError(
                "password_hash must be a PasswordHash"
            )

        if not password_hash.salt:
            return False

        if not password_hash.digest:
            return False

        if password_hash.iterations <= 0:
            return False

        try:
            bytes.fromhex(password_hash.salt)
            bytes.fromhex(password_hash.digest)
        except ValueError:
            return False

        return True

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