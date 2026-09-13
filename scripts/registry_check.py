# ============================================================
# ROBOMLM_PLUS
# REGISTRY CHECK
# PART 1
# ============================================================
#
# Purpose:
#   Central validation entry-point for ROBOMLM registries.
#
# This script validates registry structure/governance only.
#
# It does NOT:
#   - generate market intelligence
#   - calculate trading formulas
#   - generate signals
#   - make trading decisions
#   - execute trades
#   - authorize users
#   - process subscriptions
#   - perform CAS decisions
#
# Registry layer currently governed:
#   - Engine Registry
#   - Feature Registry
#   - Permission Registry
#   - Plan Registry
#   - Strategy Registry
#   - Vision Registry
#
# ============================================================

from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# CONSTANTS
# ============================================================

SCRIPT_NAME = "registry_check"
SCRIPT_VERSION = "1.0.0"

REGISTRY_PACKAGE = "registries"

EXPECTED_REGISTRIES = (
    "engine_registry",
    "feature_registry",
    "permission_registry",
    "plan_registry",
    "strategy_registry",
    "vision_registry",
)


# ============================================================
# CHECK STATUS
# ============================================================

STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_WARN = "WARN"


# ============================================================
# RESULT MODEL
# ============================================================

@dataclass(frozen=True)
class RegistryCheckResult:
    """
    Immutable result for one registry validation check.
    """

    registry_name: str
    status: str
    message: str
    details: Optional[dict[str, Any]] = None

    @property
    def passed(self) -> bool:
        return self.status == STATUS_PASS

    @property
    def failed(self) -> bool:
        return self.status == STATUS_FAIL

    @property
    def warning(self) -> bool:
        return self.status == STATUS_WARN


# ============================================================
# CHECK REPORT
# ============================================================

@dataclass
class RegistryCheckReport:
    """
    Aggregate report for registry validation.
    """

    script_name: str = SCRIPT_NAME
    script_version: str = SCRIPT_VERSION

    results: list[RegistryCheckResult] = None

    def __post_init__(self) -> None:
        if self.results is None:
            self.results = []

    @property
    def passed_count(self) -> int:
        return sum(
            result.passed
            for result in self.results
        )

    @property
    def failed_count(self) -> int:
        return sum(
            result.failed
            for result in self.results
        )

    @property
    def warning_count(self) -> int:
        return sum(
            result.warning
            for result in self.results
        )

    @property
    def healthy(self) -> bool:
        return self.failed_count == 0

    def add(
        self,
        result: RegistryCheckResult,
    ) -> None:
        self.results.append(result)


# ============================================================
# IMPORT REGISTRY MODULE
# ============================================================

def import_registry_module(
    registry_name: str,
) -> tuple[Optional[Any], Optional[str]]:
    """
    Import one registry module safely.

    Returns:
        (module, None) on success
        (None, error_message) on failure
    """

    module_name = (
        f"{REGISTRY_PACKAGE}.{registry_name}"
    )

    try:
        module = importlib.import_module(
            module_name
        )

        return module, None

    except Exception as exc:

        return None, (
            f"{type(exc).__name__}: {exc}"
        )


# ============================================================
# BASIC MODULE CHECK
# ============================================================

def check_registry_module(
    registry_name: str,
) -> RegistryCheckResult:
    """
    Verify that a registry module can be imported.
    """

    module, error = import_registry_module(
        registry_name
    )

    if module is None:

        return RegistryCheckResult(
            registry_name=registry_name,
            status=STATUS_FAIL,
            message=(
                "Registry module import failed"
            ),
            details={
                "error": error,
                "module": (
                    f"{REGISTRY_PACKAGE}."
                    f"{registry_name}"
                ),
            },
        )

    return RegistryCheckResult(
        registry_name=registry_name,
        status=STATUS_PASS,
        message=(
            "Registry module imported successfully"
        ),
        details={
            "module": module.__name__,
            "file": getattr(
                module,
                "__file__",
                None,
            ),
        },
    )


# ============================================================
# GLOBAL REGISTRY OBJECT CHECK
# ============================================================

def check_registry_object(
    registry_name: str,
) -> RegistryCheckResult:
    """
    Verify that the expected global registry object exists.

    Expected naming convention:
        engine_registry
        feature_registry
        permission_registry
        plan_registry
        strategy_registry
        vision_registry
    """

    module, error = import_registry_module(
        registry_name
    )

    if module is None:

        return RegistryCheckResult(
            registry_name=registry_name,
            status=STATUS_FAIL,
            message=(
                "Cannot inspect registry object "
                "because module import failed"
            ),
            details={
                "error": error,
            },
        )

    expected_object_name = registry_name

    registry_object = getattr(
        module,
        expected_object_name,
        None,
    )

    if registry_object is None:

        return RegistryCheckResult(
            registry_name=registry_name,
            status=STATUS_FAIL,
            message=(
                "Expected global registry object "
                "was not found"
            ),
            details={
                "expected_object": (
                    expected_object_name
                ),
            },
        )

    return RegistryCheckResult(
        registry_name=registry_name,
        status=STATUS_PASS,
        message=(
            "Global registry object found"
        ),
        details={
            "object_name": expected_object_name,
            "object_type": type(
                registry_object
            ).__name__,
        },
    )


# ============================================================
# BASIC API CHECK
# ============================================================

def check_registry_api(
    registry_name: str,
) -> RegistryCheckResult:
    """
    Verify minimum registry API surface.

    This is intentionally structural.
    """

    module, error = import_registry_module(
        registry_name
    )

    if module is None:

        return RegistryCheckResult(
            registry_name=registry_name,
            status=STATUS_FAIL,
            message=(
                "Cannot inspect registry API"
            ),
            details={
                "error": error,
            },
        )

    registry_object = getattr(
        module,
        registry_name,
        None,
    )

    if registry_object is None:

        return RegistryCheckResult(
            registry_name=registry_name,
            status=STATUS_FAIL,
            message=(
                "Registry object missing"
            ),
        )

    required_methods = (
        "register",
        "get",
        "exists",
        "count",
        "list_all",
    )

    missing_methods = [
        method
        for method in required_methods
        if not callable(
            getattr(
                registry_object,
                method,
                None,
            )
        )
    ]

    if missing_methods:

        return RegistryCheckResult(
            registry_name=registry_name,
            status=STATUS_FAIL,
            message=(
                "Required registry API is incomplete"
            ),
            details={
                "missing_methods": missing_methods,
            },
        )

    return RegistryCheckResult(
        registry_name=registry_name,
        status=STATUS_PASS,
        message=(
            "Minimum registry API is available"
        ),
        details={
            "checked_methods": list(
                required_methods
            ),
        },
    )


# ============================================================
# REGISTRY VERSION CHECK
# ============================================================

def check_registry_version(
    registry_name: str,
) -> RegistryCheckResult:
    """
    Verify that the registry exposes its registry version.
    """

    module, error = import_registry_module(
        registry_name
    )

    if module is None:

        return RegistryCheckResult(
            registry_name=registry_name,
            status=STATUS_FAIL,
            message=(
                "Cannot inspect registry version"
            ),
            details={
                "error": error,
            },
        )

    version = getattr(
        module,
        "REGISTRY_VERSION",
        None,
    )

    if not isinstance(version, str) or not version:

        return RegistryCheckResult(
            registry_name=registry_name,
            status=STATUS_FAIL,
            message=(
                "REGISTRY_VERSION is missing "
                "or invalid"
            ),
        )

    return RegistryCheckResult(
        registry_name=registry_name,
        status=STATUS_PASS,
        message=(
            "Registry version is declared"
        ),
        details={
            "registry_version": version,
        },
    )


# ============================================================
# SINGLE REGISTRY AUDIT
# ============================================================

def audit_registry(
    registry_name: str,
) -> list[RegistryCheckResult]:
    """
    Run all Part-1 structural checks for one registry.
    """

    results: list[RegistryCheckResult] = []

    results.append(
        check_registry_module(
            registry_name
        )
    )

    results.append(
        check_registry_object(
            registry_name
        )
    )

    results.append(
        check_registry_api(
            registry_name
        )
    )

    results.append(
        check_registry_version(
            registry_name
        )
    )

    return results


# ============================================================
# ALL REGISTRY AUDIT
# ============================================================

def audit_all_registries() -> RegistryCheckReport:
    """
    Audit all expected ROBOMLM registries.
    """

    report = RegistryCheckReport()

    for registry_name in EXPECTED_REGISTRIES:

        results = audit_registry(
            registry_name
        )

        for result in results:
            report.add(result)

    return report


# ============================================================
# REPORT SERIALIZATION
# ============================================================

def report_to_dict(
    report: RegistryCheckReport,
) -> dict[str, Any]:
    """
    Convert report into a serializable dictionary.
    """

    return {
        "script_name": report.script_name,
        "script_version": report.script_version,
        "healthy": report.healthy,
        "passed_count": report.passed_count,
        "failed_count": report.failed_count,
        "warning_count": report.warning_count,
        "results": [
            {
                "registry_name": result.registry_name,
                "status": result.status,
                "message": result.message,
                "details": result.details,
            }
            for result in report.results
        ],
    }


# ============================================================
# CONSOLE REPORT
# ============================================================

def print_report(
    report: RegistryCheckReport,
) -> None:
    """
    Print a human-readable registry audit report.
    """

    print("=" * 72)
    print("ROBOMLM_PLUS REGISTRY CHECK")
    print("=" * 72)

    print(
        f"Script   : {report.script_name}"
    )

    print(
        f"Version  : {report.script_version}"
    )

    print(
        f"Status   : "
        f"{'HEALTHY' if report.healthy else 'FAILED'}"
    )

    print(
        f"PASS     : {report.passed_count}"
    )

    print(
        f"FAIL     : {report.failed_count}"
    )

    print(
        f"WARN     : {report.warning_count}"
    )

    print("-" * 72)

    for result in report.results:

        print(
            f"[{result.status}] "
            f"{result.registry_name}: "
            f"{result.message}"
        )

        if result.details:

            for key, value in result.details.items():

                print(
                    f"    {key}: {value}"
                )

    print("=" * 72)


# ============================================================
# EXIT CODE
# ============================================================

def get_exit_code(
    report: RegistryCheckReport,
) -> int:
    """
    Convert registry health into process exit code.

    0 = healthy
    1 = failed
    """

    return 0 if report.healthy else 1


# ============================================================
# MAIN
# ============================================================

def main() -> int:
    """
    Execute registry structural validation.
    """

    report = audit_all_registries()

    print_report(report)

    return get_exit_code(report)


# ============================================================
# SCRIPT ENTRY POINT
# ============================================================

if __name__ == "__main__":
    raise SystemExit(
        main()
    )


# ============================================================
# END — REGISTRY CHECK PART 1
# ============================================================
