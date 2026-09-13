"""
ROBOMLM PLUS
Core Package

Central package exports for:
    - Configuration
    - Constants
    - Logging
    - Security
    - Startup
"""

from app.core.config import (
    AppConfig,
    ConfigurationError,
    ConfigLoader,
    Environment,
    get_config,
)

from app.core.startup.dependency_check import (
    DependencyCheckError,
    DependencyChecker,
    DependencyReport,
    DependencyResult,
    check_dependencies,
    validate_dependencies,
)

from app.core.startup.folder_manager import (
    FolderManager,
    FolderManagerError,
    FolderResult,
    ensure_runtime_folders,
    validate_runtime_folders,
)

from app.core.startup.shutdown import (
    ShutdownCallbackResult,
    ShutdownError,
    ShutdownManager,
    ShutdownResult,
    execute_shutdown,
    register_shutdown_callback,
    request_shutdown,
    shutdown_manager,
)

from app.core.startup.startup_checks import (
    CheckResult,
    StartupCheckError,
    StartupChecker,
    StartupReport,
    run_startup_checks,
    startup_checker,
    validate_startup,
)


__all__ = [
    # Configuration
    "AppConfig",
    "ConfigurationError",
    "ConfigLoader",
    "Environment",
    "get_config",

    # Dependency checks
    "DependencyCheckError",
    "DependencyChecker",
    "DependencyReport",
    "DependencyResult",
    "check_dependencies",
    "validate_dependencies",

    # Folder management
    "FolderManager",
    "FolderManagerError",
    "FolderResult",
    "ensure_runtime_folders",
    "validate_runtime_folders",

    # Shutdown
    "ShutdownCallbackResult",
    "ShutdownError",
    "ShutdownManager",
    "ShutdownResult",
    "execute_shutdown",
    "register_shutdown_callback",
    "request_shutdown",
    "shutdown_manager",

    # Startup checks
    "CheckResult",
    "StartupCheckError",
    "StartupChecker",
    "StartupReport",
    "run_startup_checks",
    "startup_checker",
    "validate_startup",
]