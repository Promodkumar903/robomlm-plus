"""
ROBOMLM PLUS
Startup Dependency Check

Purpose:
    Validate required and optional Python/runtime dependencies
    before application startup.

Design:
    - No automatic package installation.
    - No application startup side effects.
    - Clear required vs optional dependency reporting.
    - Safe for startup diagnostics and health checks.
"""

from __future__ import annotations

import importlib
import importlib.util
import platform
import sys
from dataclasses import dataclass, field
from typing import Iterable, Optional


@dataclass(frozen=True)
class DependencyResult:
    """Result for a single dependency check."""

    name: str
    import_name: str
    required: bool
    available: bool
    version: Optional[str] = None
    error: Optional[str] = None


@dataclass
class DependencyReport:
    """Aggregated dependency validation report."""

    results: list[DependencyResult] = field(default_factory=list)

    @property
    def required_missing(self) -> list[DependencyResult]:
        return [
            result
            for result in self.results
            if result.required and not result.available
        ]

    @property
    def optional_missing(self) -> list[DependencyResult]:
        return [
            result
            for result in self.results
            if not result.required and not result.available
        ]

    @property
    def passed(self) -> bool:
        return len(self.required_missing) == 0

    def summary(self) -> dict:
        return {
            "passed": self.passed,
            "total": len(self.results),
            "available": sum(
                1 for result in self.results if result.available
            ),
            "required_missing": [
                result.name for result in self.required_missing
            ],
            "optional_missing": [
                result.name for result in self.optional_missing
            ],
        }


class DependencyCheckError(RuntimeError):
    """Raised when required dependencies are missing."""


class DependencyChecker:
    """
    Runtime dependency checker.

    This component only checks dependencies.
    It never installs packages automatically.
    """

    DEFAULT_REQUIRED = (
        ("Python Standard Library", "sys"),
        ("Pathlib", "pathlib"),
        ("Logging", "logging"),
        ("Dataclasses", "dataclasses"),
    )

    DEFAULT_OPTIONAL = (
        ("Requests", "requests"),
        ("Pandas", "pandas"),
        ("NumPy", "numpy"),
        ("Streamlit", "streamlit"),
        ("WebSockets", "websockets"),
    )

    def __init__(
        self,
        required: Optional[Iterable[tuple[str, str]]] = None,
        optional: Optional[Iterable[tuple[str, str]]] = None,
    ) -> None:
        self.required = tuple(
            required if required is not None else self.DEFAULT_REQUIRED
        )
        self.optional = tuple(
            optional if optional is not None else self.DEFAULT_OPTIONAL
        )

    @staticmethod
    def python_version() -> str:
        """Return current Python version."""
        return platform.python_version()

    @staticmethod
    def runtime_info() -> dict:
        """Return basic runtime information."""
        return {
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "platform": platform.platform(),
            "executable": sys.executable,
        }

    @staticmethod
    def _get_version(module) -> Optional[str]:
        """Safely retrieve a module/package version."""
        version = getattr(module, "__version__", None)

        if version:
            return str(version)

        package_name = getattr(module, "__name__", None)

        if package_name:
            try:
                from importlib.metadata import version as metadata_version

                root_name = package_name.split(".")[0]
                return metadata_version(root_name)
            except Exception:
                pass

        return None

    @staticmethod
    def check_import(
        name: str,
        import_name: str,
        required: bool,
    ) -> DependencyResult:
        """Check whether a Python module can be imported."""

        try:
            spec = importlib.util.find_spec(import_name)

            if spec is None:
                return DependencyResult(
                    name=name,
                    import_name=import_name,
                    required=required,
                    available=False,
                    error="Module not found",
                )

            module = importlib.import_module(import_name)

            return DependencyResult(
                name=name,
                import_name=import_name,
                required=required,
                available=True,
                version=DependencyChecker._get_version(module),
            )

        except Exception as exc:
            return DependencyResult(
                name=name,
                import_name=import_name,
                required=required,
                available=False,
                error=f"{type(exc).__name__}: {exc}",
            )

    def check(self) -> DependencyReport:
        """Run all configured dependency checks."""

        results: list[DependencyResult] = []

        for name, import_name in self.required:
            results.append(
                self.check_import(
                    name=name,
                    import_name=import_name,
                    required=True,
                )
            )

        for name, import_name in self.optional:
            results.append(
                self.check_import(
                    name=name,
                    import_name=import_name,
                    required=False,
                )
            )

        return DependencyReport(results=results)

    def validate(self) -> DependencyReport:
        """
        Run checks and raise an error if a required dependency is missing.
        """

        report = self.check()

        if not report.passed:
            missing = ", ".join(
                result.name for result in report.required_missing
            )
            raise DependencyCheckError(
                f"Required dependencies missing or unavailable: {missing}"
            )

        return report


dependency_checker = DependencyChecker()


def check_dependencies() -> DependencyReport:
    """Convenience function for dependency validation."""
    return dependency_checker.check()


def validate_dependencies() -> DependencyReport:
    """Convenience function that validates required dependencies."""
    return dependency_checker.validate()


__all__ = [
    "DependencyResult",
    "DependencyReport",
    "DependencyCheckError",
    "DependencyChecker",
    "dependency_checker",
    "check_dependencies",
    "validate_dependencies",
]