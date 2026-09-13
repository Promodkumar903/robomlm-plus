"""
ROBOMLM PLUS
Startup Checks

Purpose:
    Coordinate non-destructive startup validation before the
    main application is launched.

Checks:
    1. Python/runtime dependencies
    2. Runtime folders
    3. Configuration
    4. Environment
    5. Basic project structure

Design:
    - Validation only.
    - No package installation.
    - No broker/exchange connection.
    - No order execution.
    - No market-data subscription.
    - No destructive filesystem operations.
"""

from __future__ import annotations

import platform
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from app.core.config.config_loader import (
    ConfigurationError,
    get_config,
)
from app.core.startup.dependency_check import (
    DependencyReport,
    check_dependencies,
)
from app.core.startup.folder_manager import (
    FolderResult,
    ensure_runtime_folders,
)


class StartupCheckError(RuntimeError):
    """Raised when startup validation fails."""


@dataclass(frozen=True)
class CheckResult:
    """Result of one startup check."""

    name: str
    passed: bool
    message: str
    details: dict = field(default_factory=dict)


@dataclass
class StartupReport:
    """Complete startup validation report."""

    checks: list[CheckResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)

    @property
    def failed_checks(self) -> list[CheckResult]:
        return [
            check
            for check in self.checks
            if not check.passed
        ]

    def summary(self) -> dict:
        return {
            "passed": self.passed,
            "total_checks": len(self.checks),
            "passed_checks": sum(
                1
                for check in self.checks
                if check.passed
            ),
            "failed_checks": [
                check.name
                for check in self.failed_checks
            ],
        }


class StartupChecker:
    """
    Central startup validation coordinator.

    This class validates system readiness without starting
    live trading, market streaming, order execution, or automation.
    """

    REQUIRED_PROJECT_PATHS = (
        "app",
        "schemas",
        "registries",
        "robomlm_data",
    )

    def __init__(
        self,
        project_root: Optional[Path | str] = None,
    ) -> None:
        self.project_root = (
            Path(project_root).resolve()
            if project_root is not None
            else self._detect_project_root()
        )

    @staticmethod
    def _detect_project_root() -> Path:
        """
        startup_checks.py
            startup/
            core/
            app/
            ROBOMLM_PLUS/
        """

        return Path(__file__).resolve().parents[3]

    def check_python_runtime(self) -> CheckResult:
        """Validate the Python runtime."""

        version_info = sys.version_info

        # ROBOMLM PLUS requires Python 3.10+.
        minimum_version = (3, 10)
        current_version = (
            version_info.major,
            version_info.minor,
        )

        passed = current_version >= minimum_version

        return CheckResult(
            name="python_runtime",
            passed=passed,
            message=(
                f"Python {platform.python_version()} "
                f"runtime is supported."
                if passed
                else
                f"Python {platform.python_version()} is below "
                f"the required Python 3.10 runtime."
            ),
            details={
                "version": platform.python_version(),
                "implementation": platform.python_implementation(),
                "executable": sys.executable,
            },
        )

    def check_dependencies(self) -> CheckResult:
        """Validate required Python dependencies."""

        try:
            report: DependencyReport = check_dependencies()

            missing = [
                result.name
                for result in report.required_missing
            ]

            return CheckResult(
                name="dependencies",
                passed=report.passed,
                message=(
                    "All required dependencies are available."
                    if report.passed
                    else
                    "Required dependencies are missing or unavailable."
                ),
                details={
                    "summary": report.summary(),
                    "missing_required": missing,
                },
            )

        except Exception as exc:
            return CheckResult(
                name="dependencies",
                passed=False,
                message="Dependency validation failed.",
                details={
                    "error": f"{type(exc).__name__}: {exc}",
                },
            )

    def check_configuration(self) -> CheckResult:
        """Validate application configuration."""

        try:
            config = get_config()

            return CheckResult(
                name="configuration",
                passed=True,
                message="Application configuration is valid.",
                details=config.to_dict(),
            )

        except ConfigurationError as exc:
            return CheckResult(
                name="configuration",
                passed=False,
                message="Application configuration is invalid.",
                details={
                    "error": str(exc),
                },
            )

        except Exception as exc:
            return CheckResult(
                name="configuration",
                passed=False,
                message="Configuration validation failed.",
                details={
                    "error": f"{type(exc).__name__}: {exc}",
                },
            )

    def check_runtime_folders(self) -> CheckResult:
        """Ensure required runtime folders exist and are writable."""

        try:
            results: list[FolderResult] = ensure_runtime_folders()

            failures = [
                result
                for result in results
                if not result.writable
            ]

            return CheckResult(
                name="runtime_folders",
                passed=len(failures) == 0,
                message=(
                    "Runtime folders are ready."
                    if not failures
                    else
                    "One or more runtime folders are unavailable."
                ),
                details={
                    "project_root": str(self.project_root),
                    "folders": [
                        {
                            "name": result.name,
                            "path": str(result.path),
                            "created": result.created,
                            "writable": result.writable,
                            "error": result.error,
                        }
                        for result in results
                    ],
                },
            )

        except Exception as exc:
            return CheckResult(
                name="runtime_folders",
                passed=False,
                message="Runtime folder preparation failed.",
                details={
                    "error": f"{type(exc).__name__}: {exc}",
                },
            )

    def check_project_structure(self) -> CheckResult:
        """Validate critical project directories."""

        missing: list[str] = []

        for relative_path in self.REQUIRED_PROJECT_PATHS:
            path = self.project_root / relative_path

            if not path.exists() or not path.is_dir():
                missing.append(relative_path)

        return CheckResult(
            name="project_structure",
            passed=len(missing) == 0,
            message=(
                "Critical project structure is available."
                if not missing
                else
                "Critical project directories are missing."
            ),
            details={
                "project_root": str(self.project_root),
                "required_paths": list(
                    self.REQUIRED_PROJECT_PATHS
                ),
                "missing_paths": missing,
            },
        )

    def check_environment(self) -> CheckResult:
        """
        Validate environment state.

        Environment validation is intentionally informational here.
        Authorization for live operations belongs to the authorization
        and execution layers.
        """

        try:
            config = get_config()

            environment = getattr(
                config,
                "environment",
                None,
            )

            return CheckResult(
                name="environment",
                passed=True,
                message="Application environment is readable.",
                details={
                    "environment": str(environment)
                    if environment is not None
                    else None,
                },
            )

        except Exception as exc:
            return CheckResult(
                name="environment",
                passed=False,
                message="Environment validation failed.",
                details={
                    "error": f"{type(exc).__name__}: {exc}",
                },
            )

    def run(self) -> StartupReport:
        """Run the complete startup validation sequence."""

        checks: list[CheckResult] = []

        check_functions: tuple[
            Callable[[], CheckResult],
            ...
        ] = (
            self.check_python_runtime,
            self.check_project_structure,
            self.check_dependencies,
            self.check_configuration,
            self.check_environment,
            self.check_runtime_folders,
        )

        for check_function in check_functions:
            checks.append(check_function())

        return StartupReport(checks=checks)

    def validate(self) -> StartupReport:
        """
        Run startup checks and raise StartupCheckError on failure.
        """

        report = self.run()

        if not report.passed:
            failures = "; ".join(
                f"{check.name}: {check.message}"
                for check in report.failed_checks
            )

            raise StartupCheckError(
                f"Startup validation failed: {failures}"
            )

        return report


startup_checker = StartupChecker()


def run_startup_checks() -> StartupReport:
    """Run all startup checks."""
    return startup_checker.run()


def validate_startup() -> StartupReport:
    """Validate startup readiness."""
    return startup_checker.validate()


__all__ = [
    "StartupCheckError",
    "CheckResult",
    "StartupReport",
    "StartupChecker",
    "startup_checker",
    "run_startup_checks",
    "validate_startup",
]