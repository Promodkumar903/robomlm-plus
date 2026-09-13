"""
ROBOMLM PLUS
Configuration Loader
Module: app/core/config/config_loader.py

Purpose:
    Centralized loading, validation and access of system configuration.

Flow:
    Environment Variables
            ↓
    settings.py CONFIG
            ↓
    ConfigLoader
            ↓
    Validated System Configuration
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Optional
import os

from .settings import (
    CONFIG,
    SystemConfig,
    AppConfig,
    DatabaseConfig,
    AuthConfig,
    MarketConfig,
)


class ConfigurationError(Exception):
    """Raised when ROBOMLM PLUS configuration is invalid."""


class ConfigLoader:
    """
    Central configuration access layer.

    This class does not contain business logic.
    It only loads, validates and exposes application configuration.
    """

    def __init__(self, config: Optional[SystemConfig] = None) -> None:
        self._config = config or CONFIG
        self.validate()

    # --------------------------------------------------
    # CONFIG ACCESS
    # --------------------------------------------------

    @property
    def config(self) -> SystemConfig:
        """Return the complete system configuration."""
        return self._config

    @property
    def app(self) -> AppConfig:
        """Return application configuration."""
        return self._config.app

    @property
    def database(self) -> DatabaseConfig:
        """Return database configuration."""
        return self._config.database

    @property
    def auth(self) -> AuthConfig:
        """Return authentication configuration."""
        return self._config.auth

    @property
    def market(self) -> MarketConfig:
        """Return market configuration."""
        return self._config.market

    # --------------------------------------------------
    # ENVIRONMENT
    # --------------------------------------------------

    @property
    def environment(self) -> str:
        """Return active application environment."""
        return self._config.app.environment

    @property
    def is_development(self) -> bool:
        """Return True when running in DEV environment."""
        return self.environment.upper() == "DEV"

    @property
    def is_test(self) -> bool:
        """Return True when running in TEST environment."""
        return self.environment.upper() == "TEST"

    @property
    def is_staging(self) -> bool:
        """Return True when running in STAGING environment."""
        return self.environment.upper() == "STAGING"

    @property
    def is_production(self) -> bool:
        """Return True when running in PROD/PRODUCTION environment."""
        return self.environment.upper() in {"PROD", "PRODUCTION"}

    # --------------------------------------------------
    # VALIDATION
    # --------------------------------------------------

    def validate(self) -> None:
        """
        Validate the complete configuration.

        Raises:
            ConfigurationError:
                When a required or invalid configuration value is detected.
        """

        self._validate_app()
        self._validate_database()
        self._validate_auth()
        self._validate_market()

    def _validate_app(self) -> None:
        app = self._config.app

        if not app.app_name.strip():
            raise ConfigurationError("APP_NAME cannot be empty.")

        if not app.app_version.strip():
            raise ConfigurationError("APP_VERSION cannot be empty.")

        if not app.environment.strip():
            raise ConfigurationError("APP_ENV cannot be empty.")

        if not app.timezone.strip():
            raise ConfigurationError("TIMEZONE cannot be empty.")

    def _validate_database(self) -> None:
        database = self._config.database

        if not database.host.strip():
            raise ConfigurationError("DB_HOST cannot be empty.")

        if not 1 <= database.port <= 65535:
            raise ConfigurationError(
                f"DB_PORT must be between 1 and 65535. "
                f"Received: {database.port}"
            )

        if not database.name.strip():
            raise ConfigurationError("DB_NAME cannot be empty.")

        if not database.user.strip():
            raise ConfigurationError("DB_USER cannot be empty.")

    def _validate_auth(self) -> None:
        auth = self._config.auth

        if not auth.jwt_secret.strip():
            raise ConfigurationError("JWT_SECRET cannot be empty.")

        if auth.jwt_secret == "CHANGE_ME":
            if self.is_production:
                raise ConfigurationError(
                    "Default JWT_SECRET cannot be used in production."
                )

        if auth.token_expiry_hours <= 0:
            raise ConfigurationError(
                "TOKEN_EXPIRY_HOURS must be greater than zero."
            )

    def _validate_market(self) -> None:
        market = self._config.market

        if market.refresh_interval <= 0:
            raise ConfigurationError(
                "REFRESH_INTERVAL must be greater than zero."
            )

        if market.max_stale_seconds <= 0:
            raise ConfigurationError(
                "MAX_STALE_SECONDS must be greater than zero."
            )

        if market.max_stale_seconds < market.refresh_interval:
            raise ConfigurationError(
                "MAX_STALE_SECONDS cannot be smaller than "
                "REFRESH_INTERVAL."
            )

    # --------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """
        Return configuration as a dictionary.

        Sensitive values such as JWT_SECRET and DB_PASSWORD
        are masked before returning the result.
        """

        data = asdict(self._config)

        data["database"]["password"] = self._mask_secret(
            data["database"]["password"]
        )

        data["auth"]["jwt_secret"] = self._mask_secret(
            data["auth"]["jwt_secret"]
        )

        return data

    @staticmethod
    def _mask_secret(value: str) -> str:
        """Mask sensitive configuration values."""

        if not value:
            return ""

        if len(value) <= 4:
            return "*" * len(value)

        return f"{value[:2]}{'*' * (len(value) - 4)}{value[-2:]}"

    # --------------------------------------------------
    # ENVIRONMENT VARIABLE HELPERS
    # --------------------------------------------------

    @staticmethod
    def get_env(
        key: str,
        default: Optional[str] = None,
    ) -> Optional[str]:
        """Read a raw environment variable."""

        value = os.getenv(key)

        if value is None:
            return default

        return value

    @staticmethod
    def require_env(key: str) -> str:
        """
        Read a required environment variable.

        Raises:
            ConfigurationError:
                When the variable does not exist or is empty.
        """

        value = os.getenv(key)

        if value is None or not value.strip():
            raise ConfigurationError(
                f"Required environment variable '{key}' is missing."
            )

        return value

    # --------------------------------------------------
    # SUMMARY
    # --------------------------------------------------

    def summary(self) -> dict[str, Any]:
        """
        Return a safe operational configuration summary.

        This method is intended for diagnostics, startup checks
        and health checks.
        """

        return {
            "app_name": self.app.app_name,
            "app_version": self.app.app_version,
            "environment": self.environment,
            "debug": self.app.debug,
            "timezone": self.app.timezone,
            "database_host": self.database.host,
            "database_port": self.database.port,
            "database_name": self.database.name,
            "database_user": self.database.user,
            "token_expiry_hours": self.auth.token_expiry_hours,
            "market_refresh_interval": self.market.refresh_interval,
            "market_max_stale_seconds": self.market.max_stale_seconds,
        }


# --------------------------------------------------
# GLOBAL CONFIG LOADER
# --------------------------------------------------

config_loader = ConfigLoader()


# --------------------------------------------------
# CONVENIENCE FUNCTION
# --------------------------------------------------

def get_config() -> SystemConfig:
    """
    Return the validated global system configuration.
    """

    return config_loader.config