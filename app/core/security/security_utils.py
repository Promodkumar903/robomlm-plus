"""
ROBOMLM PLUS
Security Utilities
Module: app/core/security/security_utils.py

Purpose:
    Common security validation and normalization utilities.

    This module provides reusable security checks for authentication,
    authorization and application services.

    It does not perform authentication or authorization itself.
"""

from __future__ import annotations

import hmac
import re
from typing import Final, Optional


MIN_PASSWORD_LENGTH: Final[int] = 8
MAX_PASSWORD_LENGTH: Final[int] = 128

MIN_USERNAME_LENGTH: Final[int] = 3
MAX_USERNAME_LENGTH: Final[int] = 64

MIN_TOKEN_LENGTH: Final[int] = 16

USERNAME_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9_.-]*$"
)

EMAIL_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)


class SecurityValidationError(Exception):
    """Base exception for security validation failures."""


def normalize_username(
    username: str,
) -> str:
    """
    Normalize a username for consistent application handling.
    """
    if not isinstance(username, str):
        raise SecurityValidationError(
            "Username must be a string."
        )

    normalized = username.strip().lower()

    if not normalized:
        raise SecurityValidationError(
            "Username cannot be empty."
        )

    return normalized


def validate_username(
    username: str,
) -> bool:
    """
    Validate username structure and length.
    """
    try:
        normalized = normalize_username(username)
    except SecurityValidationError:
        return False

    if not (
        MIN_USERNAME_LENGTH
        <= len(normalized)
        <= MAX_USERNAME_LENGTH
    ):
        return False

    return bool(USERNAME_PATTERN.fullmatch(normalized))


def normalize_email(
    email: str,
) -> str:
    """
    Normalize an email address for application use.
    """
    if not isinstance(email, str):
        raise SecurityValidationError(
            "Email must be a string."
        )

    normalized = email.strip().lower()

    if not normalized:
        raise SecurityValidationError(
            "Email cannot be empty."
        )

    return normalized


def validate_email(
    email: str,
) -> bool:
    """
    Validate basic email address structure.

    This intentionally performs structural validation only.
    Actual ownership verification belongs to the authentication
    or account-verification workflow.
    """
    try:
        normalized = normalize_email(email)
    except SecurityValidationError:
        return False

    if len(normalized) > 254:
        return False

    return bool(EMAIL_PATTERN.fullmatch(normalized))


def validate_password(
    password: str,
) -> bool:
    """
    Validate password policy.

    The password must:
        - be a string
        - be within the configured length range
        - contain no leading/trailing whitespace
        - contain at least one uppercase character
        - contain at least one lowercase character
        - contain at least one digit
        - contain at least one special character
    """
    if not isinstance(password, str):
        return False

    if not (
        MIN_PASSWORD_LENGTH
        <= len(password)
        <= MAX_PASSWORD_LENGTH
    ):
        return False

    if password != password.strip():
        return False

    if not re.search(r"[A-Z]", password):
        return False

    if not re.search(r"[a-z]", password):
        return False

    if not re.search(r"\d", password):
        return False

    if not re.search(
        r"[^A-Za-z0-9]",
        password,
    ):
        return False

    return True


def password_validation_errors(
    password: str,
) -> list[str]:
    """
    Return human-readable password policy failures.

    No password value is included in the returned messages.
    """
    errors: list[str] = []

    if not isinstance(password, str):
        return ["Password must be a string."]

    if len(password) < MIN_PASSWORD_LENGTH:
        errors.append(
            f"Password must contain at least "
            f"{MIN_PASSWORD_LENGTH} characters."
        )

    if len(password) > MAX_PASSWORD_LENGTH:
        errors.append(
            f"Password must not exceed "
            f"{MAX_PASSWORD_LENGTH} characters."
        )

    if password != password.strip():
        errors.append(
            "Password must not start or end with whitespace."
        )

    if not re.search(r"[A-Z]", password):
        errors.append(
            "Password must contain an uppercase letter."
        )

    if not re.search(r"[a-z]", password):
        errors.append(
            "Password must contain a lowercase letter."
        )

    if not re.search(r"\d", password):
        errors.append(
            "Password must contain a digit."
        )

    if not re.search(
        r"[^A-Za-z0-9]",
        password,
    ):
        errors.append(
            "Password must contain a special character."
        )

    return errors


def validate_token(
    token: str,
    *,
    minimum_length: int = MIN_TOKEN_LENGTH,
) -> bool:
    """
    Validate the basic structure of a token.

    This does not verify whether the token is authentic,
    expired or authorized.
    """
    if not isinstance(token, str):
        return False

    if len(token) < minimum_length:
        return False

    if not token.strip():
        return False

    if token != token.strip():
        return False

    return True


def safe_compare(
    first: str,
    second: str,
) -> bool:
    """
    Compare two security-sensitive strings using constant-time
    comparison.
    """
    if not isinstance(first, str):
        return False

    if not isinstance(second, str):
        return False

    return hmac.compare_digest(
        first,
        second,
    )


def mask_secret(
    value: Optional[str],
    *,
    visible_prefix: int = 3,
    visible_suffix: int = 2,
    mask_character: str = "*",
) -> str:
    """
    Safely mask a secret for diagnostics or UI display.

    The original secret is never returned in full.
    """
    if value is None:
        return ""

    if not isinstance(value, str):
        return ""

    if not value:
        return ""

    if not isinstance(visible_prefix, int):
        raise SecurityValidationError(
            "visible_prefix must be an integer."
        )

    if not isinstance(visible_suffix, int):
        raise SecurityValidationError(
            "visible_suffix must be an integer."
        )

    if visible_prefix < 0 or visible_suffix < 0:
        raise SecurityValidationError(
            "Visible prefix and suffix cannot be negative."
        )

    if not isinstance(mask_character, str) or not mask_character:
        raise SecurityValidationError(
            "Mask character must be a non-empty string."
        )

    total_visible = visible_prefix + visible_suffix

    if len(value) <= total_visible:
        return mask_character * len(value)

    prefix = value[:visible_prefix] if visible_prefix else ""
    suffix = value[-visible_suffix:] if visible_suffix else ""

    mask_length = max(
        4,
        len(value) - total_visible,
    )

    return (
        prefix
        + (mask_character * mask_length)
        + suffix
    )


def is_safe_identifier(
    value: str,
) -> bool:
    """
    Validate a generic application identifier.

    Only alphanumeric characters, underscore, hyphen and period
    are permitted.
    """
    if not isinstance(value, str):
        return False

    if not value:
        return False

    if len(value) > 128:
        return False

    return bool(
        re.fullmatch(
            r"[A-Za-z0-9_.-]+",
            value,
        )
    )


def sanitize_identifier(
    value: str,
) -> str:
    """
    Normalize a generic application identifier.

    Unsafe characters are replaced with underscores.
    """
    if not isinstance(value, str):
        raise SecurityValidationError(
            "Identifier must be a string."
        )

    value = value.strip()

    if not value:
        raise SecurityValidationError(
            "Identifier cannot be empty."
        )

    sanitized = re.sub(
        r"[^A-Za-z0-9_.-]",
        "_",
        value,
    )

    return sanitized[:128]


def is_safe_path_component(
    value: str,
) -> bool:
    """
    Validate a value intended to be used as one path component.

    Path separators and traversal sequences are rejected.
    """
    if not isinstance(value, str):
        return False

    if not value:
        return False

    if value in {".", ".."}:
        return False

    if "/" in value or "\\" in value:
        return False

    if ".." in value:
        return False

    return True


def require_safe_path_component(
    value: str,
) -> str:
    """
    Validate and return a safe path component.

    Raises SecurityValidationError on invalid input.
    """
    if not is_safe_path_component(value):
        raise SecurityValidationError(
            "Unsafe path component."
        )

    return value


def validate_integer_range(
    value: int,
    *,
    minimum: int,
    maximum: int,
) -> bool:
    """
    Validate that an integer falls inside an inclusive range.
    """
    if not isinstance(value, int):
        return False

    return minimum <= value <= maximum


__all__ = [
    "SecurityValidationError",
    "MIN_PASSWORD_LENGTH",
    "MAX_PASSWORD_LENGTH",
    "MIN_USERNAME_LENGTH",
    "MAX_USERNAME_LENGTH",
    "MIN_TOKEN_LENGTH",
    "normalize_username",
    "validate_username",
    "normalize_email",
    "validate_email",
    "validate_password",
    "password_validation_errors",
    "validate_token",
    "safe_compare",
    "mask_secret",
    "is_safe_identifier",
    "sanitize_identifier",
    "is_safe_path_component",
    "require_safe_path_component",
    "validate_integer_range",
]