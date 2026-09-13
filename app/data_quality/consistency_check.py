"""
ROBOMLM PLUS
Data Quality - Consistency Check

Purpose:
    Detect logical contradictions and invalid relationships inside
    market-data records.

Design:
    - Detection only.
    - No data mutation.
    - No market/exchange calls.
    - No trading or execution side effects.
    - Separates structural inconsistencies from valid observations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Optional


class ConsistencyCheckError(Exception):
    """Base exception for consistency-check failures."""


@dataclass(frozen=True)
class ConsistencyIssue:
    """One detected consistency issue."""

    field: str
    rule: str
    message: str
    severity: str = "ERROR"
    observed: Any = None
    expected: Any = None

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable representation."""

        return {
            "field": self.field,
            "rule": self.rule,
            "message": self.message,
            "severity": self.severity,
            "observed": self.observed,
            "expected": self.expected,
        }


@dataclass(frozen=True)
class ConsistencyResult:
    """Result of a consistency evaluation."""

    consistent: bool
    score: float
    checked_rules: int
    passed_rules: int
    failed_rules: int
    issues: tuple[ConsistencyIssue, ...] = ()
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def issue_count(self) -> int:
        """Return total number of issues."""

        return len(self.issues)

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable representation."""

        return {
            "consistent": self.consistent,
            "score": self.score,
            "checked_rules": self.checked_rules,
            "passed_rules": self.passed_rules,
            "failed_rules": self.failed_rules,
            "issue_count": self.issue_count,
            "issues": [
                issue.to_dict()
                for issue in self.issues
            ],
            "metadata": dict(self.metadata),
        }


class ConsistencyChecker:
    """
    Validate logical relationships in supplied data.

    Supported market-data rules include:
        - OHLC ordering
        - bid/ask relationship
        - non-negative sizes
        - non-negative volume
        - non-negative turnover
        - non-negative volatility
        - non-negative spread
        - bid <= ask
        - low <= high
        - low <= open/close <= high
    """

    NUMERIC_FIELDS = (
        "open",
        "high",
        "low",
        "close",
        "price",
        "bid",
        "ask",
        "bid_size",
        "ask_size",
        "volume",
        "turnover",
        "volatility",
        "spread",
    )

    NON_NEGATIVE_FIELDS = (
        "bid_size",
        "ask_size",
        "volume",
        "turnover",
        "volatility",
        "spread",
    )

    def __init__(
        self,
        strict: bool = False,
    ) -> None:
        self.strict = bool(strict)

    @staticmethod
    def _to_mapping(
        data: Any,
    ) -> dict[str, Any]:
        """Convert supported objects into a dictionary."""

        if isinstance(data, dict):
            return dict(data)

        if hasattr(data, "to_dict"):
            result = data.to_dict()

            if isinstance(result, dict):
                return dict(result)

        if hasattr(data, "__dict__"):
            return dict(vars(data))

        raise ConsistencyCheckError(
            "Data must be a dictionary or expose "
            "to_dict()/__dict__."
        )

    @staticmethod
    def _numeric(
        value: Any,
    ) -> bool:
        """Return whether a value is a usable finite number."""

        if isinstance(
            value,
            bool,
        ):
            return False

        try:
            number = float(value)
        except (
            TypeError,
            ValueError,
        ):
            return False

        return number == number and abs(number) != float("inf")

    @staticmethod
    def _number(
        value: Any,
    ) -> float:
        """Convert a validated numeric value to float."""

        return float(value)

    def _issue(
        self,
        issues: list[ConsistencyIssue],
        field: str,
        rule: str,
        message: str,
        observed: Any = None,
        expected: Any = None,
        severity: str = "ERROR",
    ) -> None:
        """Append a consistency issue."""

        issues.append(
            ConsistencyIssue(
                field=field,
                rule=rule,
                message=message,
                severity=severity,
                observed=observed,
                expected=expected,
            )
        )

    def _check_numeric_types(
        self,
        data: dict[str, Any],
        issues: list[ConsistencyIssue],
    ) -> int:
        """Check numeric market fields for invalid values."""

        checked = 0

        for field_name in self.NUMERIC_FIELDS:

            if field_name not in data:
                continue

            value = data[field_name]

            if value is None:
                continue

            checked += 1

            if not self._numeric(value):
                self._issue(
                    issues=issues,
                    field=field_name,
                    rule="numeric_value",
                    message=(
                        f"{field_name} must be a finite "
                        "numeric value."
                    ),
                    observed=value,
                    expected="finite numeric value",
                )

        return checked

    def _check_non_negative(
        self,
        data: dict[str, Any],
        issues: list[ConsistencyIssue],
    ) -> int:
        """Check fields that cannot be negative."""

        checked = 0

        for field_name in self.NON_NEGATIVE_FIELDS:

            if field_name not in data:
                continue

            value = data[field_name]

            if value is None:
                continue

            checked += 1

            if not self._numeric(value):
                continue

            number = self._number(value)

            if number < 0:
                self._issue(
                    issues=issues,
                    field=field_name,
                    rule="non_negative",
                    message=(
                        f"{field_name} cannot be negative."
                    ),
                    observed=number,
                    expected=">= 0",
                )

        return checked

    def _check_ohlc(
        self,
        data: dict[str, Any],
        issues: list[ConsistencyIssue],
    ) -> int:
        """Validate OHLC relationships."""

        available = {
            name: data.get(name)
            for name in (
                "open",
                "high",
                "low",
                "close",
            )
        }

        numeric_values = {
            name: self._number(value)
            for name, value in available.items()
            if value is not None
            and self._numeric(value)
        }

        if len(numeric_values) < 2:
            return 0

        checked = 0

        if (
            "low" in numeric_values
            and "high" in numeric_values
        ):
            checked += 1

            if (
                numeric_values["low"]
                > numeric_values["high"]
            ):
                self._issue(
                    issues=issues,
                    field="low/high",
                    rule="low_lte_high",
                    message="Low cannot be greater than high.",
                    observed={
                        "low": numeric_values["low"],
                        "high": numeric_values["high"],
                    },
                    expected="low <= high",
                )

        if (
            "open" in numeric_values
            and "low" in numeric_values
            and "high" in numeric_values
        ):
            checked += 1

            if not (
                numeric_values["low"]
                <= numeric_values["open"]
                <= numeric_values["high"]
            ):
                self._issue(
                    issues=issues,
                    field="open",
                    rule="open_inside_range",
                    message=(
                        "Open must be between low and high."
                    ),
                    observed=numeric_values["open"],
                    expected={
                        "low": numeric_values["low"],
                        "high": numeric_values["high"],
                    },
                )

        if (
            "close" in numeric_values
            and "low" in numeric_values
            and "high" in numeric_values
        ):
            checked += 1

            if not (
                numeric_values["low"]
                <= numeric_values["close"]
                <= numeric_values["high"]
            ):
                self._issue(
                    issues=issues,
                    field="close",
                    rule="close_inside_range",
                    message=(
                        "Close must be between low and high."
                    ),
                    observed=numeric_values["close"],
                    expected={
                        "low": numeric_values["low"],
                        "high": numeric_values["high"],
                    },
                )

        return checked

    def _check_bid_ask(
        self,
        data: dict[str, Any],
        issues: list[ConsistencyIssue],
    ) -> int:
        """Validate bid/ask relationships."""

        if (
            "bid" not in data
            or "ask" not in data
        ):
            return 0

        bid = data.get("bid")
        ask = data.get("ask")

        if (
            bid is None
            or ask is None
            or not self._numeric(bid)
            or not self._numeric(ask)
        ):
            return 0

        checked = 1

        bid_value = self._number(bid)
        ask_value = self._number(ask)

        if bid_value > ask_value:
            self._issue(
                issues=issues,
                field="bid/ask",
                rule="bid_lte_ask",
                message="Bid cannot be greater than ask.",
                observed={
                    "bid": bid_value,
                    "ask": ask_value,
                },
                expected="bid <= ask",
            )

        return checked

    def _check_price_against_bid_ask(
        self,
        data: dict[str, Any],
        issues: list[ConsistencyIssue],
    ) -> int:
        """Check price against a valid bid/ask range."""

        required = (
            "price",
            "bid",
            "ask",
        )

        if not all(
            field_name in data
            for field_name in required
        ):
            return 0

        price = data.get("price")
        bid = data.get("bid")
        ask = data.get("ask")

        if not all(
            self._numeric(value)
            for value in (
                price,
                bid,
                ask,
            )
        ):
            return 0

        price_value = self._number(price)
        bid_value = self._number(bid)
        ask_value = self._number(ask)

        if bid_value > ask_value:
            return 0

        checked = 1

        if not (
            bid_value
            <= price_value
            <= ask_value
        ):
            self._issue(
                issues=issues,
                field="price",
                rule="price_inside_bid_ask",
                message=(
                    "Price is outside the supplied bid/ask range."
                ),
                observed=price_value,
                expected={
                    "bid": bid_value,
                    "ask": ask_value,
                },
                severity="WARNING",
            )

        return checked

    def check(
        self,
        data: Any,
    ) -> ConsistencyResult:
        """Run all applicable consistency checks."""

        mapping = self._to_mapping(data)

        issues: list[ConsistencyIssue] = []

        checked_rules = 0

        checked_rules += self._check_numeric_types(
            mapping,
            issues,
        )

        checked_rules += self._check_non_negative(
            mapping,
            issues,
        )

        checked_rules += self._check_ohlc(
            mapping,
            issues,
        )

        checked_rules += self._check_bid_ask(
            mapping,
            issues,
        )

        checked_rules += self._check_price_against_bid_ask(
            mapping,
            issues,
        )

        failed_rules = len(issues)

        passed_rules = max(
            checked_rules - failed_rules,
            0,
        )

        if checked_rules:
            score = (
                passed_rules
                / checked_rules
            ) * 100.0
        else:
            score = 100.0

        if self.strict:
            consistent = failed_rules == 0
        else:
            consistent = not any(
                issue.severity == "ERROR"
                for issue in issues
            )

        return ConsistencyResult(
            consistent=consistent,
            score=round(score, 4),
            checked_rules=checked_rules,
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            issues=tuple(issues),
            metadata={
                "checker": self.__class__.__name__,
                "strict": self.strict,
            },
        )

    def is_consistent(
        self,
        data: Any,
    ) -> bool:
        """Return whether data passes consistency checks."""

        return self.check(data).consistent

    def score(
        self,
        data: Any,
    ) -> float:
        """Return consistency score from 0 to 100."""

        return self.check(data).score

    def issues(
        self,
        data: Any,
    ) -> tuple[ConsistencyIssue, ...]:
        """Return detected consistency issues."""

        return self.check(data).issues


consistency_checker = ConsistencyChecker()


def check_consistency(
    data: Any,
) -> ConsistencyResult:
    """Convenience function for consistency checking."""

    return consistency_checker.check(data)


__all__ = [
    "ConsistencyCheckError",
    "ConsistencyIssue",
    "ConsistencyResult",
    "ConsistencyChecker",
    "consistency_checker",
    "check_consistency",
]