from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from threading import RLock
from typing import Any


@dataclass(frozen=True)
class ReconciliationDifference:
    field: str
    expected: Any
    actual: Any
    difference: Any
    severity: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReconciliationResult:
    reconciliation_id: str
    matched: bool
    difference_count: int
    differences: tuple[ReconciliationDifference, ...]
    timestamp: datetime
    message: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["differences"] = [
            difference.to_dict()
            for difference in self.differences
        ]
        return data


class ReconciliationEngine:
    """
    Reconciliation engine for AUTOROBIMLM.

    Compares expected internal state with observed external state
    and records deterministic differences.

    This component does not modify broker state, positions, orders,
    balances, or execution state. It reports discrepancies only.
    """

    SEVERITIES = frozenset({
        "INFO",
        "WARNING",
        "CRITICAL",
    })

    def __init__(self) -> None:
        self._results: dict[str, ReconciliationResult] = {}
        self._counter = 0
        self._lock = RLock()

    @staticmethod
    def _normalize(value: str, field: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{field} must be a string")

        value = value.strip()

        if not value:
            raise ValueError(f"{field} is required")

        return value

    def _next_id(self) -> str:
        self._counter += 1
        return f"RECON-{self._counter:08d}"

    @staticmethod
    def _severity(
        field: str,
        expected: Any,
        actual: Any,
    ) -> str:
        field_lower = field.lower()

        if any(
            keyword in field_lower
            for keyword in (
                "balance",
                "quantity",
                "position",
                "order",
                "execution",
            )
        ):
            return "CRITICAL"

        if isinstance(expected, (int, float)) and isinstance(
            actual,
            (int, float),
        ):
            return "WARNING"

        return "INFO"

    @staticmethod
    def _numeric_difference(
        expected: Any,
        actual: Any,
    ) -> Any:
        if isinstance(expected, (int, float)) and isinstance(
            actual,
            (int, float),
        ):
            return actual - expected

        return None

    def compare(
        self,
        expected: dict[str, Any],
        actual: dict[str, Any],
        reconciliation_id: str | None = None,
    ) -> ReconciliationResult:
        if not isinstance(expected, dict):
            raise TypeError("expected must be a dictionary")

        if not isinstance(actual, dict):
            raise TypeError("actual must be a dictionary")

        if reconciliation_id is None:
            with self._lock:
                reconciliation_id = self._next_id()
        else:
            reconciliation_id = self._normalize(
                reconciliation_id,
                "reconciliation_id",
            )

        differences: list[ReconciliationDifference] = []

        fields = sorted(
            set(expected.keys()) | set(actual.keys())
        )

        for field in fields:
            expected_value = expected.get(field)
            actual_value = actual.get(field)

            if expected_value == actual_value:
                continue

            severity = self._severity(
                str(field),
                expected_value,
                actual_value,
            )

            difference = ReconciliationDifference(
                field=str(field),
                expected=expected_value,
                actual=actual_value,
                difference=self._numeric_difference(
                    expected_value,
                    actual_value,
                ),
                severity=severity,
            )

            differences.append(difference)

        timestamp = datetime.now(timezone.utc)

        matched = not differences

        if matched:
            message = "Expected and actual states match"
        else:
            message = (
                f"Reconciliation detected "
                f"{len(differences)} difference(s)"
            )

        result = ReconciliationResult(
            reconciliation_id=reconciliation_id,
            matched=matched,
            difference_count=len(differences),
            differences=tuple(differences),
            timestamp=timestamp,
            message=message,
        )

        with self._lock:
            self._results[reconciliation_id] = result

        return result

    def reconcile(
        self,
        expected: dict[str, Any],
        actual: dict[str, Any],
    ) -> ReconciliationResult:
        return self.compare(expected, actual)

    def get(
        self,
        reconciliation_id: str,
    ) -> ReconciliationResult | None:
        reconciliation_id = self._normalize(
            reconciliation_id,
            "reconciliation_id",
        )

        with self._lock:
            return self._results.get(reconciliation_id)

    def results(self) -> tuple[ReconciliationResult, ...]:
        with self._lock:
            return tuple(self._results.values())

    def latest(self) -> ReconciliationResult | None:
        with self._lock:
            if not self._results:
                return None

            return next(
                reversed(self._results.values())
            )

    def mismatch_count(self) -> int:
        with self._lock:
            return sum(
                1
                for result in self._results.values()
                if not result.matched
            )

    def matched_count(self) -> int:
        with self._lock:
            return sum(
                1
                for result in self._results.values()
                if result.matched
            )

    def critical_mismatch_count(self) -> int:
        with self._lock:
            return sum(
                1
                for result in self._results.values()
                if any(
                    difference.severity == "CRITICAL"
                    for difference in result.differences
                )
            )

    def clear(self) -> None:
        with self._lock:
            self._results.clear()
            self._counter = 0

    def health_check(self) -> dict[str, Any]:
        with self._lock:
            results = tuple(self._results.values())

            return {
                "status": "healthy",
                "reconciliation_count": len(results),
                "matched_count": sum(
                    1
                    for result in results
                    if result.matched
                ),
                "mismatch_count": sum(
                    1
                    for result in results
                    if not result.matched
                ),
                "critical_mismatch_count": sum(
                    1
                    for result in results
                    if any(
                        difference.severity == "CRITICAL"
                        for difference
                        in result.differences
                    )
                ),
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),
            }