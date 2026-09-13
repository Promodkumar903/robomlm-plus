"""
ROBOMLM PLUS
Security Hashing
Module: app/core/security/hashing.py

Purpose:
    Secure password hashing and verification utilities.

    Passwords must never be stored or compared as plaintext.
    This module contains hashing primitives only; authentication
    workflow belongs to the auth layer.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets as python_secrets
from typing import Final


DEFAULT_ITERATIONS: Final[int] = 600_000
SALT_BYTES: Final[int] = 32
KEY_LENGTH: Final[int] = 32
ALGORITHM: Final[str] = "sha256"
HASH_SCHEME: Final[str] = "pbkdf2_sha256"


class HashingError(Exception):
    """Base exception for hashing-related failures."""


def _validate_password(password: str) -> None:
    """Validate password input before hashing or verification."""
    if not isinstance(password, str):
        raise HashingError("Password must be a string.")

    if not password:
        raise HashingError("Password cannot be empty.")


def _validate_iterations(iterations: int) -> None:
    """Validate PBKDF2 iteration count."""
    if not isinstance(iterations, int):
        raise HashingError("Iterations must be an integer.")

    if iterations <= 0:
        raise HashingError("Iterations must be greater than zero.")


def hash_password(
    password: str,
    *,
    iterations: int = DEFAULT_ITERATIONS,
) -> str:
    """
    Hash a password using PBKDF2-HMAC-SHA256.

    Stored format:

        pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>
    """
    _validate_password(password)
    _validate_iterations(iterations)

    salt = python_secrets.token_bytes(SALT_BYTES)

    derived_key = hashlib.pbkdf2_hmac(
        ALGORITHM,
        password.encode("utf-8"),
        salt,
        iterations,
        dklen=KEY_LENGTH,
    )

    return (
        f"{HASH_SCHEME}$"
        f"{iterations}$"
        f"{salt.hex()}$"
        f"{derived_key.hex()}"
    )


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    """
    Verify a plaintext password against a stored password hash.

    Invalid or malformed hashes return False rather than exposing
    internal hashing details to the caller.
    """
    if not isinstance(password, str):
        return False

    if not isinstance(password_hash, str):
        return False

    try:
        scheme, iterations_text, salt_hex, stored_hash_hex = (
            password_hash.split("$")
        )

        if scheme != HASH_SCHEME:
            return False

        iterations = int(iterations_text)

        if iterations <= 0:
            return False

        salt = bytes.fromhex(salt_hex)
        stored_hash = bytes.fromhex(stored_hash_hex)

        derived_key = hashlib.pbkdf2_hmac(
            ALGORITHM,
            password.encode("utf-8"),
            salt,
            iterations,
            dklen=len(stored_hash),
        )

        return hmac.compare_digest(
            derived_key,
            stored_hash,
        )

    except (
        ValueError,
        TypeError,
        UnicodeError,
    ):
        return False


def needs_rehash(
    password_hash: str,
    *,
    iterations: int = DEFAULT_ITERATIONS,
) -> bool:
    """
    Determine whether a stored password hash should be regenerated.

    This is useful when the system increases its hashing cost over time.
    """
    if not isinstance(password_hash, str):
        return True

    try:
        scheme, iterations_text, salt_hex, stored_hash_hex = (
            password_hash.split("$")
        )

        if scheme != HASH_SCHEME:
            return True

        stored_iterations = int(iterations_text)

        if stored_iterations < iterations:
            return True

        if not salt_hex or not stored_hash_hex:
            return True

        return False

    except (
        ValueError,
        TypeError,
    ):
        return True


def generate_salt(
    length: int = SALT_BYTES,
) -> bytes:
    """
    Generate cryptographically secure random salt bytes.

    Primarily provided for lower-level security components.
    Password hashing generates its own salt automatically.
    """
    if not isinstance(length, int):
        raise HashingError("Salt length must be an integer.")

    if length <= 0:
        raise HashingError("Salt length must be greater than zero.")

    return python_secrets.token_bytes(length)


def constant_time_compare(
    first: str,
    second: str,
) -> bool:
    """
    Compare two strings using constant-time comparison.
    """
    if not isinstance(first, str) or not isinstance(second, str):
        return False

    return hmac.compare_digest(first, second)