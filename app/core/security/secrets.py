"""
ROBOMLM PLUS
Security Secrets
Module: app/core/security/secrets.py

Purpose:
    Secure secret generation and environment-backed secret access.

    This module provides utilities for application secrets, tokens,
    identifiers and cryptographic random values.

    Secrets are never logged or exposed by this module.
"""

from __future__ import annotations

import base64
import hashlib
import os
import secrets as python_secrets
from typing import Final, Optional


DEFAULT_TOKEN_BYTES: Final[int] = 32
DEFAULT_SECRET_BYTES: Final[int] = 32
DEFAULT_NONCE_BYTES: Final[int] = 32


class SecretError(Exception):
    """Base exception for secret-related failures."""


def _validate_length(length: int) -> None:
    """Validate a byte-length argument."""
    if not isinstance(length, int):
        raise SecretError("Length must be an integer.")

    if length <= 0:
        raise SecretError("Length must be greater than zero.")


def generate_secret(
    length: int = DEFAULT_SECRET_BYTES,
) -> str:
    """
    Generate a cryptographically secure hexadecimal secret.
    """
    _validate_length(length)

    return python_secrets.token_hex(length)


def generate_token(
    length: int = DEFAULT_TOKEN_BYTES,
) -> str:
    """
    Generate a cryptographically secure URL-safe token.
    """
    _validate_length(length)

    return python_secrets.token_urlsafe(length)


def generate_nonce(
    length: int = DEFAULT_NONCE_BYTES,
) -> str:
    """
    Generate a cryptographically secure nonce.
    """
    _validate_length(length)

    return python_secrets.token_urlsafe(length)


def generate_api_key(
    length: int = DEFAULT_TOKEN_BYTES,
) -> str:
    """
    Generate a cryptographically secure API-key value.

    The returned value is suitable for application-level API
    credential generation. Storage and authorization are handled
    elsewhere.
    """
    _validate_length(length)

    return f"rmlm_{python_secrets.token_urlsafe(length)}"


def generate_session_secret(
    length: int = DEFAULT_SECRET_BYTES,
) -> str:
    """
    Generate a secret suitable for a session-level cryptographic
    value.
    """
    _validate_length(length)

    return python_secrets.token_urlsafe(length)


def generate_numeric_code(
    digits: int = 6,
) -> str:
    """
    Generate a cryptographically secure numeric verification code.
    """
    if not isinstance(digits, int):
        raise SecretError("Digits must be an integer.")

    if digits <= 0:
        raise SecretError("Digits must be greater than zero.")

    minimum = 10 ** (digits - 1)
    maximum = (10 ** digits) - 1

    if digits == 1:
        minimum = 0

    return str(
        python_secrets.randbelow(
            maximum - minimum + 1
        ) + minimum
    )


def get_secret_from_env(
    name: str,
    *,
    required: bool = False,
    default: Optional[str] = None,
) -> Optional[str]:
    """
    Read a secret from an environment variable.

    When required=True, a missing or empty value raises SecretError.
    """
    if not isinstance(name, str) or not name.strip():
        raise SecretError("Environment variable name is required.")

    value = os.getenv(name)

    if value is None or value == "":
        if required:
            raise SecretError(
                f"Required secret environment variable is missing: {name}"
            )

        return default

    return value


def require_secret_from_env(name: str) -> str:
    """
    Read a required secret from an environment variable.
    """
    value = get_secret_from_env(
        name,
        required=True,
    )

    if value is None:
        raise SecretError(
            f"Required secret environment variable is missing: {name}"
        )

    return value


def encode_secret(value: str) -> str:
    """
    Encode a string using URL-safe Base64.

    This is encoding, not encryption.
    """
    if not isinstance(value, str):
        raise SecretError("Value must be a string.")

    return base64.urlsafe_b64encode(
        value.encode("utf-8")
    ).decode("ascii")


def decode_secret(value: str) -> str:
    """
    Decode a URL-safe Base64 encoded string.
    """
    if not isinstance(value, str):
        raise SecretError("Encoded value must be a string.")

    try:
        return base64.urlsafe_b64decode(
            value.encode("ascii")
        ).decode("utf-8")

    except (
        ValueError,
        UnicodeError,
        base64.binascii.Error,
    ) as exc:
        raise SecretError(
            "Invalid encoded secret."
        ) from exc


def fingerprint_secret(
    secret: str,
) -> str:
    """
    Return a non-reversible SHA-256 fingerprint of a secret.

    Useful for safe identification or comparison in diagnostics.
    The original secret is never returned.
    """
    if not isinstance(secret, str):
        raise SecretError("Secret must be a string.")

    if not secret:
        raise SecretError("Secret cannot be empty.")

    return hashlib.sha256(
        secret.encode("utf-8")
    ).hexdigest()


def is_secret_configured(
    name: str,
) -> bool:
    """
    Return True when an environment-backed secret exists and
    contains a non-empty value.
    """
    value = os.getenv(name)

    return bool(value)


__all__ = [
    "SecretError",
    "generate_secret",
    "generate_token",
    "generate_nonce",
    "generate_api_key",
    "generate_session_secret",
    "generate_numeric_code",
    "get_secret_from_env",
    "require_secret_from_env",
    "encode_secret",
    "decode_secret",
    "fingerprint_secret",
    "is_secret_configured",
]