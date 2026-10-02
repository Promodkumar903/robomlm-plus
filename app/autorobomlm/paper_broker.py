"""
ROBOMLM_PLUS - AutoROBOMLM Paper Broker

Purpose:
    Simulate execution using real market prices.

Design:
    - Real prices from a price_provider callable.
    - Fills at current market price (with configurable slippage).
    - In-memory position tracking.
    - No external broker calls.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from math import isfinite
from typing import Any, Callable, Mapping, Optional
from uuid import uuid4


BROKER_NAME = "AutoROBOMLM_PaperBroker"
BROKER_VERSION = "1.0"


class TradeDirection(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class PositionStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class BrokerStatus(str, Enum):
    FILLED = "FILLED"
    REJECTED = "REJECTED"


@dataclass
class Position:
    position_id: str
    symbol: str
    direction: TradeDirection
    quantity: float
    entry_price: float
    stop_loss: float
    take_profit: float
    entry_grade: Optional[str] = None
    entry_score: Optional[float] = None
    entry_source: Optional[str] = None
    opened_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    status: PositionStatus = PositionStatus.OPEN
    exit_price: Optional[float] = None
    exit_reason: Optional[str] = None
    closed_at: Optional[datetime] = None

    def pnl(self, current_price: float) -> float:
        if current_price is None:
            return 0.0
        if self.direction == TradeDirection.BUY:
            return (current_price - self.entry_price) * self.quantity
        return (self.entry_price - current_price) * self.quantity

    def pnl_pct(self, current_price: float) -> float:
        if self.entry_price <= 0:
            return 0.0
        if self.direction == TradeDirection.BUY:
            return (current_price - self.entry_price) / self.entry_price * 100.0
        return (self.entry_price - current_price) / self.entry_price * 100.0

    def to_dict(self, current_price: Optional[float] = None) -> dict:
        payload = {
            "position_id": self.position_id,
            "symbol": self.symbol,
            "direction": self.direction.value,
            "quantity": self.quantity,
            "entry_price": self.entry_price,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "entry_grade": self.entry_grade,
            "entry_score": self.entry_score,
            "entry_source": self.entry_source,
            "opened_at": self.opened_at.isoformat(),
            "status": self.status.value,
            "exit_price": self.exit_price,
            "exit_reason": self.exit_reason,
            "closed_at": (
                self.closed_at.isoformat() if self.closed_at else None
            ),
        }
        if current_price is not None:
            payload["current_price"] = current_price
            payload["pnl"] = self.pnl(current_price)
            payload["pnl_pct"] = self.pnl_pct(current_price)
        return payload


@dataclass(frozen=True)
class FillResult:
    status: BrokerStatus
    position: Optional[Position]
    fill_price: Optional[float]
    reason: str = ""
    errors: tuple = ()

    def as_dict(self):
        return {
            "status": self.status.value,
            "position": (
                self.position.to_dict() if self.position else None
            ),
            "fill_price": self.fill_price,
            "reason": self.reason,
            "errors": list(self.errors),
        }


class PaperBroker:
    def __init__(
        self,
        *,
        price_provider: Callable[[str], Optional[float]],
        slippage_pct: float = 0.0,
    ):
        if not callable(price_provider):
            raise ValueError("price_provider must be callable.")
        if slippage_pct < 0.0:
            raise ValueError("slippage_pct must be >= 0.")
        self.price_provider = price_provider
        self.slippage_pct = float(slippage_pct)
        self.positions: dict[str, Position] = {}

    def open_position(
        self,
        *,
        symbol: str,
        direction: TradeDirection,
        quantity: float,
        stop_loss: float,
        take_profit: float,
        entry_grade: Optional[str] = None,
        entry_score: Optional[float] = None,
        entry_source: Optional[str] = None,
    ) -> FillResult:
        if not symbol or not str(symbol).strip():
            return FillResult(
                status=BrokerStatus.REJECTED,
                position=None, fill_price=None,
                errors=("symbol is required.",),
            )
        if not isinstance(direction, TradeDirection):
            return FillResult(
                status=BrokerStatus.REJECTED,
                position=None, fill_price=None,
                errors=("direction must be a TradeDirection.",),
            )
        for name, value in (
            ("quantity", quantity),
            ("stop_loss", stop_loss),
            ("take_profit", take_profit),
        ):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                return FillResult(
                    status=BrokerStatus.REJECTED,
                    position=None, fill_price=None,
                    errors=(f"{name} must be numeric.",),
                )
            if not isfinite(float(value)):
                return FillResult(
                    status=BrokerStatus.REJECTED,
                    position=None, fill_price=None,
                    errors=(f"{name} must be finite.",),
                )
            if float(value) <= 0.0:
                return FillResult(
                    status=BrokerStatus.REJECTED,
                    position=None, fill_price=None,
                    errors=(f"{name} must be > 0.",),
                )

        market_price = self.price_provider(symbol)

        if market_price is None:
            return FillResult(
                status=BrokerStatus.REJECTED,
                position=None, fill_price=None,
                reason=f"No market price available for {symbol}.",
            )
        if not isfinite(float(market_price)) or float(market_price) <= 0:
            return FillResult(
                status=BrokerStatus.REJECTED,
                position=None, fill_price=None,
                reason=f"Invalid market price for {symbol}.",
            )

        market_price = float(market_price)
        slip = market_price * self.slippage_pct / 100.0

        if direction == TradeDirection.BUY:
            fill_price = market_price + slip
        else:
            fill_price = market_price - slip

        position = Position(
            position_id=str(uuid4()),
            symbol=symbol,
            direction=direction,
            quantity=float(quantity),
            entry_price=fill_price,
            stop_loss=float(stop_loss),
            take_profit=float(take_profit),
            entry_grade=entry_grade,
            entry_score=entry_score,
            entry_source=entry_source,
        )
        self.positions[position.position_id] = position

        return FillResult(
            status=BrokerStatus.FILLED,
            position=position,
            fill_price=fill_price,
            reason=f"Paper fill at {fill_price}.",
        )

    def close_position(
        self,
        position_id: str,
        *,
        reason: str,
    ) -> FillResult:
        position = self.positions.get(position_id)
        if position is None:
            return FillResult(
                status=BrokerStatus.REJECTED,
                position=None, fill_price=None,
                errors=(f"Unknown position_id {position_id}.",),
            )
        if position.status == PositionStatus.CLOSED:
            return FillResult(
                status=BrokerStatus.REJECTED,
                position=position, fill_price=None,
                errors=("Position is already closed.",),
            )

        market_price = self.price_provider(position.symbol)
        if market_price is None:
            return FillResult(
                status=BrokerStatus.REJECTED,
                position=position, fill_price=None,
                reason=f"No market price for {position.symbol}.",
            )

        market_price = float(market_price)
        slip = market_price * self.slippage_pct / 100.0

        if position.direction == TradeDirection.BUY:
            fill_price = market_price - slip
        else:
            fill_price = market_price + slip

        position.exit_price = fill_price
        position.exit_reason = reason
        position.closed_at = datetime.now(timezone.utc)
        position.status = PositionStatus.CLOSED

        return FillResult(
            status=BrokerStatus.FILLED,
            position=position,
            fill_price=fill_price,
            reason=f"Closed at {fill_price} ({reason}).",
        )

    def get_open_positions(self) -> list[Position]:
        return [
            p for p in self.positions.values()
            if p.status == PositionStatus.OPEN
        ]

    def get_all_positions(self) -> list[Position]:
        return list(self.positions.values())

    def get_position(self, position_id: str) -> Optional[Position]:
        return self.positions.get(position_id)

    def mark_to_market(self) -> list[dict]:
        result = []
        for p in self.get_open_positions():
            price = self.price_provider(p.symbol)
            result.append(p.to_dict(current_price=price))
        return result


__all__ = [
    "BROKER_NAME", "BROKER_VERSION",
    "TradeDirection", "PositionStatus", "BrokerStatus",
    "Position", "FillResult", "PaperBroker",
]
