from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from threading import RLock
from typing import Any


@dataclass(frozen=True)
class Order:
    order_id: str
    symbol: str
    side: str
    quantity: float
    order_type: str
    price: float | None
    status: str
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        return data


@dataclass(frozen=True)
class OrderUpdate:
    order_id: str
    previous_status: str
    current_status: str
    message: str
    timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


class OrderManager:
    """
    Order lifecycle manager for AUTOROBIMLM.

    Responsibilities:
    - Validate order structure.
    - Create and track orders.
    - Maintain deterministic order lifecycle.
    - Record status transitions.
    - Provide lookup and operational statistics.

    This class does not execute orders and does not bypass
    authorization, risk, or kill-switch controls.
    """

    VALID_SIDES = frozenset({"BUY", "SELL"})

    VALID_ORDER_TYPES = frozenset({
        "MARKET",
        "LIMIT",
        "STOP",
        "STOP_LIMIT",
    })

    VALID_STATUSES = frozenset({
        "CREATED",
        "PENDING",
        "SUBMITTED",
        "PARTIAL",
        "FILLED",
        "CANCELLED",
        "REJECTED",
        "FAILED",
    })

    TERMINAL_STATUSES = frozenset({
        "FILLED",
        "CANCELLED",
        "REJECTED",
        "FAILED",
    })

    ALLOWED_TRANSITIONS = {
        "CREATED": frozenset({
            "PENDING",
            "SUBMITTED",
            "CANCELLED",
            "REJECTED",
            "FAILED",
        }),
        "PENDING": frozenset({
            "SUBMITTED",
            "PARTIAL",
            "FILLED",
            "CANCELLED",
            "REJECTED",
            "FAILED",
        }),
        "SUBMITTED": frozenset({
            "PARTIAL",
            "FILLED",
            "CANCELLED",
            "REJECTED",
            "FAILED",
        }),
        "PARTIAL": frozenset({
            "PARTIAL",
            "FILLED",
            "CANCELLED",
            "FAILED",
        }),
        "FILLED": frozenset(),
        "CANCELLED": frozenset(),
        "REJECTED": frozenset(),
        "FAILED": frozenset(),
    }

    def __init__(self) -> None:
        self._orders: dict[str, Order] = {}
        self._history: dict[str, list[OrderUpdate]] = {}
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

    @staticmethod
    def _positive(value: float, field: str) -> float:
        if not isinstance(value, (int, float)):
            raise TypeError(f"{field} must be numeric")

        value = float(value)

        if value <= 0:
            raise ValueError(
                f"{field} must be greater than zero"
            )

        return value

    def _next_order_id(self) -> str:
        self._counter += 1
        return f"ORD-{self._counter:08d}"

    def create_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "MARKET",
        price: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Order:
        symbol = self._normalize(symbol, "symbol")
        side = self._normalize(side, "side").upper()
        order_type = self._normalize(
            order_type,
            "order_type",
        ).upper()

        if side not in self.VALID_SIDES:
            raise ValueError(
                f"Unsupported side: {side}"
            )

        if order_type not in self.VALID_ORDER_TYPES:
            raise ValueError(
                f"Unsupported order type: {order_type}"
            )

        quantity = self._positive(
            quantity,
            "quantity",
        )

        if order_type in {"LIMIT", "STOP_LIMIT"}:
            if price is None:
                raise ValueError(
                    "price is required for limit orders"
                )

        if price is not None:
            price = self._positive(
                price,
                "price",
            )

        timestamp = datetime.now(timezone.utc)

        with self._lock:
            order = Order(
                order_id=self._next_order_id(),
                symbol=symbol,
                side=side,
                quantity=quantity,
                order_type=order_type,
                price=price,
                status="CREATED",
                created_at=timestamp,
                updated_at=timestamp,
                metadata=dict(metadata)
                if metadata
                else None,
            )

            self._orders[order.order_id] = order
            self._history[order.order_id] = []

            return order

    def get_order(
        self,
        order_id: str,
    ) -> Order | None:
        order_id = self._normalize(
            order_id,
            "order_id",
        )

        with self._lock:
            return self._orders.get(order_id)

    def update_status(
        self,
        order_id: str,
        new_status: str,
        message: str = "",
    ) -> OrderUpdate:
        order_id = self._normalize(
            order_id,
            "order_id",
        )

        new_status = self._normalize(
            new_status,
            "new_status",
        ).upper()

        if new_status not in self.VALID_STATUSES:
            raise ValueError(
                f"Unsupported status: {new_status}"
            )

        timestamp = datetime.now(timezone.utc)

        with self._lock:
            order = self._orders.get(order_id)

            if order is None:
                raise KeyError(
                    f"Order not found: {order_id}"
                )

            previous_status = order.status

            if new_status == previous_status:
                update = OrderUpdate(
                    order_id=order_id,
                    previous_status=previous_status,
                    current_status=new_status,
                    message=message or "Status unchanged",
                    timestamp=timestamp,
                )

                self._history[order_id].append(update)
                return update

            allowed = self.ALLOWED_TRANSITIONS.get(
                previous_status,
                frozenset(),
            )

            if new_status not in allowed:
                raise ValueError(
                    f"Invalid order transition: "
                    f"{previous_status} -> {new_status}"
                )

            updated_order = Order(
                order_id=order.order_id,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                order_type=order.order_type,
                price=order.price,
                status=new_status,
                created_at=order.created_at,
                updated_at=timestamp,
                metadata=dict(order.metadata)
                if order.metadata
                else None,
            )

            self._orders[order_id] = updated_order

            update = OrderUpdate(
                order_id=order_id,
                previous_status=previous_status,
                current_status=new_status,
                message=message
                or f"Order status changed to {new_status}",
                timestamp=timestamp,
            )

            self._history[order_id].append(update)

            return update

    def submit(
        self,
        order_id: str,
    ) -> OrderUpdate:
        return self.update_status(
            order_id,
            "SUBMITTED",
            "Order submitted for execution",
        )

    def mark_pending(
        self,
        order_id: str,
    ) -> OrderUpdate:
        return self.update_status(
            order_id,
            "PENDING",
            "Order placed in pending state",
        )

    def mark_partial(
        self,
        order_id: str,
    ) -> OrderUpdate:
        return self.update_status(
            order_id,
            "PARTIAL",
            "Order partially filled",
        )

    def mark_filled(
        self,
        order_id: str,
    ) -> OrderUpdate:
        return self.update_status(
            order_id,
            "FILLED",
            "Order fully filled",
        )

    def cancel(
        self,
        order_id: str,
    ) -> OrderUpdate:
        return self.update_status(
            order_id,
            "CANCELLED",
            "Order cancelled",
        )

    def reject(
        self,
        order_id: str,
        reason: str = "Order rejected",
    ) -> OrderUpdate:
        return self.update_status(
            order_id,
            "REJECTED",
            reason,
        )

    def fail(
        self,
        order_id: str,
        reason: str = "Order failed",
    ) -> OrderUpdate:
        return self.update_status(
            order_id,
            "FAILED",
            reason,
        )

    def is_terminal(
        self,
        order_id: str,
    ) -> bool:
        order = self.get_order(order_id)

        if order is None:
            return False

        return order.status in self.TERMINAL_STATUSES

    def history(
        self,
        order_id: str,
    ) -> tuple[OrderUpdate, ...]:
        order_id = self._normalize(
            order_id,
            "order_id",
        )

        with self._lock:
            if order_id not in self._orders:
                raise KeyError(
                    f"Order not found: {order_id}"
                )

            return tuple(
                self._history.get(order_id, [])
            )

    def orders(
        self,
        status: str | None = None,
    ) -> tuple[Order, ...]:
        with self._lock:
            values = tuple(self._orders.values())

        if status is None:
            return values

        status = self._normalize(
            status,
            "status",
        ).upper()

        if status not in self.VALID_STATUSES:
            raise ValueError(
                f"Unsupported status: {status}"
            )

        return tuple(
            order
            for order in values
            if order.status == status
        )

    def active_orders(self) -> tuple[Order, ...]:
        with self._lock:
            return tuple(
                order
                for order in self._orders.values()
                if order.status
                not in self.TERMINAL_STATUSES
            )

    def count(
        self,
        status: str | None = None,
    ) -> int:
        return len(self.orders(status))

    def terminal_count(self) -> int:
        with self._lock:
            return sum(
                1
                for order in self._orders.values()
                if order.status in self.TERMINAL_STATUSES
            )

    def clear(self) -> None:
        with self._lock:
            self._orders.clear()
            self._history.clear()
            self._counter = 0

    def health_check(self) -> dict[str, Any]:
        with self._lock:
            status_counts = {
                status: 0
                for status in self.VALID_STATUSES
            }

            for order in self._orders.values():
                status_counts[order.status] += 1

            return {
                "status": "healthy",
                "order_count": len(self._orders),
                "active_order_count": sum(
                    count
                    for status, count
                    in status_counts.items()
                    if status
                    not in self.TERMINAL_STATUSES
                ),
                "terminal_order_count": sum(
                    count
                    for status, count
                    in status_counts.items()
                    if status
                    in self.TERMINAL_STATUSES
                ),
                "status_counts": status_counts,
                "history_records": sum(
                    len(records)
                    for records in self._history.values()
                ),
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),
            }