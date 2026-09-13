"""
ROBOMLM PLUS
Data Quality - Completeness Check

Purpose:
    Measure whether a market data object contains the required
    information needed for reliable downstream intelligence.

Design:
    - Detection only.
    - No data mutation.
    - No market/exchange calls.
    - No trading or execution side effects.
    - Separates missing fields from present fields.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Optional


class CompletenessCheckError(Exception):
    """Base exception for completeness-check failures."""


@dataclass(frozen=True)
class CompletenessResult:
    """Result of a completeness evaluation."""

    complete: bool
    score: float
    required_fields: tuple[str, ...]
    present_fields: tuple[str, ...]
    missing_fields: tuple[str, ...]
    empty_fields: tuple[str, ...]
    checked_fields: int
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def missing_count(self) -> int:
        """Return number of missing fields."""

        return len(self.missing_fields)

    @property
    def empty_count(self) -> int:
        """Return number of empty fields."""

        return len(self.empty_fields)

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable representation."""

        return {
            "complete": self.complete,
            "score": self.score,
            "required_fields": list(
                self.required_fields
            ),
            "present_fields": list(
                self.present_fields
            ),
            "missing_fields": list(
                self.missing_fields
            ),
            "empty_fields": list(
                self.empty_fields
            ),
            "checked_fields": self.checked_fields,
            "missing_count": self.missing_count,
            "empty_count": self.empty_count,
            "metadata": dict(self.metadata),
        }


class CompletenessChecker:
    """
    Check whether required data fields are available.

    A field is considered:
        present -> key exists and value is meaningful.
        empty   -> key exists but value is None or empty.
        missing -> key does not exist.
    """

    DEFAULT_MARKET_FIELDS = (
        "market",
        "instrument",
        "venue",
        "observed_at",
        "price",
    )

    def __init__(
        self,
        required_fields: Optional[
            Iterable[str]
        ] = None,
    ) -> None:

        if required_fields is None:
            required_fields = (
                self.DEFAULT_MARKET_FIELDS
            )

        self.required_fields = self._normalize_fields(
            required_fields
        )

    @staticmethod
    def _normalize_fields(
        fields: Iterable[str],
    ) -> tuple[str, ...]:
        """Normalize and validate field names."""

        normalized: list[str] = []
        seen: set[str] = set()

        for field_name in fields:
            name = str(field_name).strip()

            if not name:
                raise CompletenessCheckError(
                    "Required field name cannot be empty."
                )

            if name not in seen:
                normalized.append(name)
                seen.add(name)

        if not normalized:
            raise CompletenessCheckError(
                "At least one required field is necessary."
            )

        return tuple(normalized)

    @staticmethod
    def _to_mapping(
        data: Any,
    ) -> dict[str, Any]:
        """
        Convert supported data objects into a mapping.
        """

        if isinstance(data, dict):
            return dict(data)

        if hasattr(data, "to_dict"):
            result = data.to_dict()

            if isinstance(result, dict):
                return dict(result)

        if hasattr(data, "__dict__"):
            return dict(vars(data))

        raise CompletenessCheckError(
            "Data must be a dictionary or expose "
            "to_dict()/__dict__."
        )

    @staticmethod
    def _is_empty(
        value: Any,
    ) -> bool:
        """Determine whether a field value is empty."""

        if value is None:
            return True

        if isinstance(
            value,
            str,
        ) and not value.strip():
            return True

        if isinstance(
            value,
            (list, tuple, set, dict),
        ) and len(value) == 0:
            return True

        return False

    def check(
        self,
        data: Any,
        required_fields: Optional[
            Iterable[str]
        ] = None,
    ) -> CompletenessResult:
        """
        Evaluate completeness of supplied data.
        """

        mapping = self._to_mapping(data)

        fields = (
            self.required_fields
            if required_fields is None
            else self._normalize_fields(
                required_fields
            )
        )

        present: list[str] = []
        missing: list[str] = []
        empty: list[str] = []

        for field_name in fields:

            if field_name not in mapping:
                missing.append(field_name)
                continue

            if self._is_empty(
                mapping[field_name]
            ):
                empty.append(field_name)
                continue

            present.append(field_name)

        total = len(fields)

        score = (
            (len(present) / total) * 100.0
            if total
            else 0.0
        )

        complete = (
            len(missing) == 0
            and len(empty) == 0
        )

        return CompletenessResult(
            complete=complete,
            score=round(score, 4),
            required_fields=fields,
            present_fields=tuple(present),
            missing_fields=tuple(missing),
            empty_fields=tuple(empty),
            checked_fields=total,
            metadata={
                "checker": self.__class__.__name__,
            },
        )

    def check_market_data(
        self,
        data: Any,
    ) -> CompletenessResult:
        """Run the default market-data completeness check."""

        return self.check(
            data,
            self.DEFAULT_MARKET_FIELDS,
        )

    def is_complete(
        self,
        data: Any,
        required_fields: Optional[
            Iterable[str]
        ] = None,
    ) -> bool:
        """Return True when all required fields are usable."""

        return self.check(
            data,
            required_fields,
        ).complete

    def score(
        self,
        data: Any,
        required_fields: Optional[
            Iterable[str]
        ] = None,
    ) -> float:
        """Return completeness score from 0 to 100."""

        return self.check(
            data,
            required_fields,
        ).score

    def missing_fields(
        self,
        data: Any,
        required_fields: Optional[
            Iterable[str]
        ] = None,
    ) -> tuple[str, ...]:
        """Return missing or empty required fields."""

        result = self.check(
            data,
            required_fields,
        )

        return tuple(
            list(result.missing_fields)
            + list(result.empty_fields)
        )


completeness_checker = CompletenessChecker()


def check_completeness(
    data: Any,
    required_fields: Optional[
        Iterable[str]
    ] = None,
) -> CompletenessResult:
    """Convenience function for completeness checking."""

    return completeness_checker.check(
        data,
        required_fields,
    )


__all__ = [
    "CompletenessCheckError",
    "CompletenessResult",
    "CompletenessChecker",
    "completeness_checker",
    "check_completeness",
]