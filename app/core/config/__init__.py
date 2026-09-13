"""
ROBOMLM PLUS
Configuration Package
"""

from .settings import (
    CONFIG,
    SystemConfig,
    AppConfig,
    DatabaseConfig,
    AuthConfig,
    MarketConfig,
)

from .config_loader import (
    ConfigLoader,
    ConfigurationError,
    config_loader,
    get_config,
)

from .environment import (
    Environment,
    EnvironmentManager,
    environment_manager,
    get_environment,
    get_environment_name,
    is_development,
    is_test,
    is_staging,
    is_production,
)


__all__ = [
    "CONFIG",
    "SystemConfig",
    "AppConfig",
    "DatabaseConfig",
    "AuthConfig",
    "MarketConfig",
    "ConfigLoader",
    "ConfigurationError",
    "config_loader",
    "get_config",
    "Environment",
    "EnvironmentManager",
    "environment_manager",
    "get_environment",
    "get_environment_name",
    "is_development",
    "is_test",
    "is_staging",
    "is_production",
]