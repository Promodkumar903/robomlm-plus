from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from threading import RLock
from typing import Any


@dataclass(frozen=True)
class Position:
    position_id: str
    symbol: str
    side: str
    quantity: float
    average_price: float
    opened_at: datetime
    updated_at: datetime
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["opened_at"] = self.opened_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        return data


@dataclass(frozen=True)
class PositionUpdate:
    position_id: str
    action: str
    quantity: float
    price: float
    timestamp: datetime
    message: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


class PositionManager:
    """
    Position state manager for AUTOROBIMLM.

    Maintains open positions and applies position changes resulting
    from execution events. It does not submit orders and does not
    bypass execution, authorization, risk, or kill-switch controls.
    """

    VALID_SIDES = frozenset({"LONG", "SHORT"})
    VALID_ACTIONS = frozenset({"OPEN", "ADD", "REDUCE", "CLOSE"})

    def __init__(self) -> None:
        self._positions: dict[str, Position] = {}
        self._history: dict[str, list[PositionUpdate]] = {}
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

    def _next_position_id(self) -> str:
        self._counter += 1
        return f"POS-{self._counter:08d}"

    @staticmethod
    def _weighted_average(
        current_quantity: float,
        current_price: float,
        added_quantity: float,
        added_price: float,
    ) -> float:
        total = current_quantity + added_quantity

        if total <= 0:
            raise ValueError(
                "Combined position quantity must be greater than zero"
            )

        return (
            current_quantity * current_price
            + added_quantity * added_price
        ) / total

    def open(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        metadata: dict[str, Any] | None = None,
    ) -> Position:
        symbol = self._normalize(symbol, "symbol")
        side = self._normalize(side, "side").upper()

        if side not in self.VALID_SIDES:
            raise ValueError(
                f"Unsupported position side: {side}"
            )

        quantity = self._positive(quantity, "quantity")
        price = self._positive(price, "price")

        timestamp = datetime.now(timezone.utc)

        with self._lock:
            position = Position(
                position_id=self._next_position_id(),
                symbol=symbol,
                side=side,
                quantity=quantity,
                average_price=price,
                opened_at=timestamp,
                updated_at=timestamp,
                metadata=dict(metadata)
                if metadata
                else None,
            )

            self._positions[position.position_id] = position
            self._history[position.position_id] = [
                PositionUpdate(
                    position_id=position.position_id,
                    action="OPEN",
                    quantity=quantity,
                    price=price,
                    timestamp=timestamp,
                    message="Position opened",
                )
            ]

            return position

    def get(
        self,
        position_id: str,
    ) -> Position | None:
        position_id = self._normalize(
            position_id,
            "position_id",
        )

        with self._lock:
            return self._positions.get(position_id)

    def update(
        self,
        position_id: str,
        action: str,
        quantity: float,
        price: float,
    ) -> Position:
        position_id = self._normalize(
            position_id,
            "position_id",
        )
        action = self._normalize(
            action,
            "action",
        ).upper()

        if action not in self.VALID_ACTIONS:
            raise ValueError(
                f"Unsupported position action: {action}"
            )

        quantity = self._positive(quantity, "quantity")
        price = self._positive(price, "price")

        timestamp = datetime.now(timezone.utc)

        with self._lock:
            position = self._positions.get(position_id)

            if position is None:
                raise KeyError(
                    f"Position not found: {position_id}"
                )

            if action == "OPEN":
                raise ValueError(
                    "OPEN is only valid when creating a new position"
                )

            if action == "ADD":
                average_price = self._weighted_average(
                    position.quantity,
                    position.average_price,
                    quantity,
                    price,
                )

                updated = Position(
                    position_id=position.position_id,
                    symbol=position.symbol,
                    side=position.side,
                    quantity=position.quantity + quantity,
                    average_price=average_price,
                    opened_at=position.opened_at,
                    updated_at=timestamp,
                    metadata=dict(position.metadata)
                    if position.metadata
                    else None,
                )

                message = "Position increased"

            elif action in {"REDUCE", "CLOSE"}:
                if quantity > position.quantity:
                    raise ValueError(
                        "Reduction quantity cannot exceed "
                        "current position quantity"
                    )

                remaining = position.quantity - quantity

                if action == "CLOSE":
                    remaining = 0.0

                if remaining == 0:
                    del self._positions[position_id]

                    update = PositionUpdate(
                        position_id=position_id,
                        action="CLOSE",
                        quantity=position.quantity,
                        price=price,
                        timestamp=timestamp,
                        message="Position closed",
                    )

                    self._history[position_id].append(update)

                    return position

                updated = Position(
                    position_id=position.position_id,
                    symbol=position.symbol,
                    side=position.side,
                    quantity=remaining,
                    average_price=position.average_price,
                    opened_at=position.opened_at,
                    updated_at=timestamp,
                    metadata=dict(position.metadata)
                    if position.metadata
                    else None,
                )

                message = "Position reduced"

            else:
                raise ValueError(
                    f"Unsupported position action: {action}"
                )

            self._positions[position_id] = updated

            self._history[position_id].append(
                PositionUpdate(
                    position_id=position_id,
                    action=action,
                    quantity=quantity,
                    price=price,
                    timestamp=timestamp,
                    message=message,
                )
            )

            return updated

    def add(
        self,
        position_id: str,
        quantity: float,
        price: float,
    ) -> Position:
        return self.update(
            position_id,
            "ADD",
            quantity,
            price,
        )

    def reduce(
        self,
        position_id: str,
        quantity: float,
        price: float,
    ) -> Position:
        return self.update(
            position_id,
            "REDUCE",
            quantity,
            price,
        )

    def close(
        self,
        position_id: str,
        price: float,
    ) -> Position:
        position = self.get(position_id)

        if position is None:
            raise KeyError(
                f"Position not found: {position_id}"
            )

        return self.update(
            position_id,
            "CLOSE",
            position.quantity,
            price,
        )

    def positions(
        self,
        symbol: str | None = None,
    ) -> tuple[Position, ...]:
        with self._lock:
            values = tuple(self._positions.values())

        if symbol is None:
            return values

        symbol = self._normalize(symbol, "symbol")

        return tuple(
            position
            for position in values
            if position.symbol == symbol
        )

    def history(
        self,
        position_id: str,
    ) -> tuple[PositionUpdate, ...]:
        position_id = self._normalize(
            position_id,
            "position_id",
        )

        with self._lock:
            if position_id not in self._history:
                raise KeyError(
                    f"Position not found: {position_id}"
                )

            return tuple(
                self._history[position_id]
            )

    def exists(
        self,
        position_id: str,
    ) -> bool:
        return self.get(position_id) is not None

    def count(self) -> int:
        with self._lock:
            return len(self._positions)

    def symbols(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(
                sorted(
                    {
                        position.symbol
                        for position in self._positions.values()
                    }
                )
            )

    def total_quantity(
        self,
        symbol: str | None = None,
    ) -> float:
        return sum(
            position.quantity
            for position in self.positions(symbol)
        )

    def clear(self) -> None:
        with self._lock:
            self._positions.clear()
            self._history.clear()
            self._counter = 0

    def health_check(self) -> dict[str, Any]:
        with self._lock:
            return {
                "status": "healthy",
                "position_count": len(self._positions),
                "symbol_count": len(
                    {
                        position.symbol
                        for position in self._positions.values()
                    }
                ),
                "history_records": sum(
                    len(records)
                    for records in self._history.values()
                ),
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),
            }