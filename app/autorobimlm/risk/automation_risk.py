from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from math import isfinite
from threading import RLock
from typing import Any


@dataclass(frozen=True)
class RiskLimits:
    max_order_quantity: float | None = None
    max_position_quantity: float | None = None
    max_daily_loss: float | None = None
    max_order_value: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RiskCheckResult:
    approved: bool
    reason: str
    checks: dict[str, bool]
    timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


class AutomationRisk:
    """
    Risk gate for AUTOROBIMLM automation.

    Evaluates proposed automated orders against configured risk
    limits. It does not place orders, modify positions, authorize
    users, or override the kill switch.
    """

    def __init__(
        self,
        limits: RiskLimits | None = None,
    ) -> None:
        self._limits = limits or RiskLimits()
        self._last_result: RiskCheckResult | None = None
        self._lock = RLock()

    @staticmethod
    def _positive_or_none(
        value: float | None,
        field: str,
    ) -> float | None:
        if value is None:
            return None

        if not isinstance(value, (int, float)):
            raise TypeError(f"{field} must be numeric or None")

        value = float(value)

        if not isfinite(value):
            raise ValueError(f"{field} must be finite")

        if value <= 0:
            raise ValueError(
                f"{field} must be greater than zero"
            )

        return value

    @classmethod
    def _validate_limits(
        cls,
        limits: RiskLimits,
    ) -> RiskLimits:
        return RiskLimits(
            max_order_quantity=cls._positive_or_none(
                limits.max_order_quantity,
                "max_order_quantity",
            ),
            max_position_quantity=cls._positive_or_none(
                limits.max_position_quantity,
                "max_position_quantity",
            ),
            max_daily_loss=cls._positive_or_none(
                limits.max_daily_loss,
                "max_daily_loss",
            ),
            max_order_value=cls._positive_or_none(
                limits.max_order_value,
                "max_order_value",
            ),
        )

    @property
    def limits(self) -> RiskLimits:
        with self._lock:
            return self._limits

    def set_limits(
        self,
        limits: RiskLimits,
    ) -> RiskLimits:
        if not isinstance(limits, RiskLimits):
            raise TypeError(
                "limits must be a RiskLimits instance"
            )

        limits = self._validate_limits(limits)

        with self._lock:
            self._limits = limits

        return limits

    def check_order(
        self,
        quantity: float,
        price: float,
        current_position_quantity: float = 0.0,
        daily_loss: float = 0.0,
    ) -> RiskCheckResult:
        quantity = self._validate_number(
            quantity,
            "quantity",
        )

        price = self._validate_number(
            price,
            "price",
        )

        current_position_quantity = self._validate_number(
            current_position_quantity,
            "current_position_quantity",
            allow_zero=True,
        )

        daily_loss = self._validate_number(
            daily_loss,
            "daily_loss",
            allow_zero=True,
        )

        with self._lock:
            limits = self._limits

        order_value = quantity * price
        projected_position = (
            current_position_quantity + quantity
        )

        checks: dict[str, bool] = {}

        if limits.max_order_quantity is None:
            checks["max_order_quantity"] = True
        else:
            checks["max_order_quantity"] = (
                quantity <= limits.max_order_quantity
            )

        if limits.max_position_quantity is None:
            checks["max_position_quantity"] = True
        else:
            checks["max_position_quantity"] = (
                projected_position
                <= limits.max_position_quantity
            )

        if limits.max_order_value is None:
            checks["max_order_value"] = True
        else:
            checks["max_order_value"] = (
                order_value <= limits.max_order_value
            )

        if limits.max_daily_loss is None:
            checks["max_daily_loss"] = True
        else:
            checks["max_daily_loss"] = (
                daily_loss <= limits.max_daily_loss
            )

        approved = all(checks.values())

        if approved:
            reason = "Risk checks passed"
        else:
            failed = [
                name
                for name, passed in checks.items()
                if not passed
            ]

            reason = (
                "Risk check failed: "
                + ", ".join(failed)
            )

        result = RiskCheckResult(
            approved=approved,
            reason=reason,
            checks=dict(checks),
            timestamp=datetime.now(timezone.utc),
        )

        with self._lock:
            self._last_result = result

        return result

    def approve(
        self,
        quantity: float,
        price: float,
        current_position_quantity: float = 0.0,
        daily_loss: float = 0.0,
    ) -> bool:
        return self.check_order(
            quantity=quantity,
            price=price,
            current_position_quantity=current_position_quantity,
            daily_loss=daily_loss,
        ).approved

    def last_result(self) -> RiskCheckResult | None:
        with self._lock:
            return self._last_result

    @staticmethod
    def _validate_number(
        value: float,
        field: str,
        allow_zero: bool = False,
    ) -> float:
        if not isinstance(value, (int, float)):
            raise TypeError(
                f"{field} must be numeric"
            )

        value = float(value)

        if not isfinite(value):
            raise ValueError(
                f"{field} must be finite"
            )

        if allow_zero:
            if value < 0:
                raise ValueError(
                    f"{field} cannot be negative"
                )
        elif value <= 0:
            raise ValueError(
                f"{field} must be greater than zero"
            )

        return value

    def utilization(
        self,
        quantity: float,
        price: float,
    ) -> dict[str, float | None]:
        quantity = self._validate_number(
            quantity,
            "quantity",
        )

        price = self._validate_number(
            price,
            "price",
        )

        with self._lock:
            limits = self._limits

        order_value = quantity * price

        return {
            "order_quantity": quantity,
            "order_value": order_value,
            "quantity_utilization": (
                quantity / limits.max_order_quantity
                if limits.max_order_quantity is not None
                else None
            ),
            "value_utilization": (
                order_value / limits.max_order_value
                if limits.max_order_value is not None
                else None
            ),
        }

    def health_check(self) -> dict[str, Any]:
        with self._lock:
            limits = self._limits
            last_result = self._last_result

            return {
                "status": "healthy",
                "limits": limits.to_dict(),
                "has_last_result": last_result is not None,
                "last_result_approved": (
                    last_result.approved
                    if last_result is not None
                    else None
                ),
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),
            }

    def clear_last_result(self) -> None:
        with self._lock:
            self._last_result = None

    def reset(
        self,
        limits: RiskLimits | None = None,
    ) -> None:
        with self._lock:
            self._limits = (
                self._validate_limits(limits)
                if limits is not None
                else RiskLimits()
            )
            self._last_result = None