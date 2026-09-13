"""
ROBOMLM PLUS
Environment Configuration
Module: app/core/config/environment.py

Purpose:
    Environment identification, normalization and environment-specific
    behavior flags.

Supported environments:
    DEV
    TEST
    STAGING
    PROD
"""

from __future__ import annotations

from enum import Enum
import os


# --------------------------------------------------
# ENVIRONMENT TYPES
# --------------------------------------------------

class Environment(str, Enum):
    DEV = "DEV"
    TEST = "TEST"
    STAGING = "STAGING"
    PROD = "PROD"


# --------------------------------------------------
# ENVIRONMENT MANAGER
# --------------------------------------------------

class EnvironmentManager:
    """
    Central environment management layer.

    This module determines which operational environment
    ROBOMLM PLUS is currently running in.

    It does not contain application business logic.
    """

    ENV_VARIABLE = "APP_ENV"

    def __init__(self, value: str | None = None) -> None:
        raw_value = value if value is not None else os.getenv(
            self.ENV_VARIABLE,
            Environment.DEV.value,
        )

        self._environment = self._normalize(raw_value)

    # --------------------------------------------------
    # NORMALIZATION
    # --------------------------------------------------

    @staticmethod
    def _normalize(value: str) -> Environment:
        """
        Normalize environment input.

        Accepted aliases:
            DEVELOPMENT -> DEV
            DEVELOP -> DEV
            TESTING -> TEST
            STAGE -> STAGING
            PRODUCTION -> PROD
        """

        if not isinstance(value, str):
            raise ValueError("Environment value must be a string.")

        normalized = value.strip().upper()

        aliases = {
            "DEVELOPMENT": Environment.DEV,
            "DEVELOP": Environment.DEV,
            "TESTING": Environment.TEST,
            "STAGE": Environment.STAGING,
            "PRODUCTION": Environment.PROD,
        }

        if normalized in aliases:
            return aliases[normalized]

        try:
            return Environment(normalized)
        except ValueError as exc:
            valid = ", ".join(environment.value for environment in Environment)

            raise ValueError(
                f"Invalid APP_ENV '{value}'. "
                f"Supported environments: {valid}"
            ) from exc

    # --------------------------------------------------
    # CURRENT ENVIRONMENT
    # --------------------------------------------------

    @property
    def current(self) -> Environment:
        """Return the current environment."""
        return self._environment

    @property
    def name(self) -> str:
        """Return the current environment name."""
        return self._environment.value

    # --------------------------------------------------
    # ENVIRONMENT FLAGS
    # --------------------------------------------------

    @property
    def is_dev(self) -> bool:
        return self._environment == Environment.DEV

    @property
    def is_test(self) -> bool:
        return self._environment == Environment.TEST

    @property
    def is_staging(self) -> bool:
        return self._environment == Environment.STAGING

    @property
    def is_prod(self) -> bool:
        return self._environment == Environment.PROD

    @property
    def is_non_production(self) -> bool:
        return not self.is_prod

    # --------------------------------------------------
    # OPERATIONAL FLAGS
    # --------------------------------------------------

    @property
    def debug_allowed(self) -> bool:
        """
        Debugging is allowed only outside production.
        """

        return self.is_non_production

    @property
    def live_operations_allowed(self) -> bool:
        """
        Indicates whether the environment is capable of
        supporting production/live operational configuration.

        This is an environment capability flag only.

        It does NOT authorize trading or order execution.
        Actual execution authorization belongs to the
        authorization / execution / risk layers.
        """

        return self.is_prod

    @property
    def research_allowed(self) -> bool:
        """
        Research and experimentation are available in
        development, test and staging environments.

        Production research capability may still exist,
        but controlled through the research layer.
        """

        return True

    # --------------------------------------------------
    # SAFE REPRESENTATION
    # --------------------------------------------------

    def summary(self) -> dict[str, object]:
        """
        Return a safe environment summary for diagnostics.
        """

        return {
            "environment": self.name,
            "is_dev": self.is_dev,
            "is_test": self.is_test,
            "is_staging": self.is_staging,
            "is_prod": self.is_prod,
            "is_non_production": self.is_non_production,
            "debug_allowed": self.debug_allowed,
            "live_operations_allowed": self.live_operations_allowed,
            "research_allowed": self.research_allowed,
        }


# --------------------------------------------------
# GLOBAL ENVIRONMENT MANAGER
# --------------------------------------------------

environment_manager = EnvironmentManager()


# --------------------------------------------------
# CONVENIENCE FUNCTIONS
# --------------------------------------------------

def get_environment() -> Environment:
    """Return the current environment."""
    return environment_manager.current


def get_environment_name() -> str:
    """Return the current environment name."""
    return environment_manager.name


def is_development() -> bool:
    return environment_manager.is_dev


def is_test() -> bool:
    return environment_manager.is_test


def is_staging() -> bool:
    return environment_manager.is_staging


def is_production() -> bool:
    return environment_manager.is_prod