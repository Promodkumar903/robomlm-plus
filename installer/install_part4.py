"""AutoROBOMLM installer part 4 - paper_broker + auto_loop"""
from pathlib import Path

ROOT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\autorobomlm")
ROOT.mkdir(parents=True, exist_ok=True)

FILES = {}

FILES["paper_broker.py"] = '''"""
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
'''

FILES["auto_loop.py"] = '''"""
ROBOMLM_PLUS - AutoROBOMLM Main Loop

Purpose:
    Orchestrate the safety pipeline:

        Signal  ->  Grade  ->  Objective  ->  Resource
              ->  Constraint  ->  Allocate  ->  SL/TP
              ->  Paper Broker  ->  Position

    And manage open positions:
        - SL hit   -> close
        - TP hit   -> close
        - D13 flip -> close

Design:
    - All dependencies are injected (no hidden imports).
    - Thread-safe state (simple lock).
    - Kill switch + mode manager are optional hooks.
    - Loop is start/stop-able.
    - Every tick returns an auditable result.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from threading import Lock, Thread, Event
from typing import Any, Callable, Optional

from app.autorobomlm.config import (
    AutoRobomlmConfig,
    GradeBand,
    ExecutionMode,
    WatchlistSource,
)
from app.autorobomlm.grade_evaluator import (
    GradeSource,
    evaluate_grade,
)
from app.autorobomlm.objective_gate import (
    ObjectiveDefinition,
    ObjectiveType,
    evaluate_objective,
)
from app.autorobomlm.resource_gate import (
    ResourceCheck,
    ResourceKind,
    evaluate_resources,
)
from app.autorobomlm.constraint_gate import (
    ConstraintCheck,
    ConstraintDisposition,
    ConstraintKind,
    evaluate_constraints,
)
from app.autorobomlm.capital_allocator import allocate_capital
from app.autorobomlm.sl_tp_calculator import (
    TradeDirection as SLTPDirection,
    calculate_sl_tp,
)
from app.autorobomlm.paper_broker import (
    PaperBroker,
    PositionStatus,
    TradeDirection,
)


LOOP_NAME = "AutoROBOMLM_Loop"
LOOP_VERSION = "1.0"


class LoopState(str, Enum):
    STOPPED = "STOPPED"
    RUNNING = "RUNNING"
    KILLED = "KILLED"


@dataclass
class TickSummary:
    started_at: datetime
    finished_at: datetime
    scanned: int = 0
    opened: int = 0
    closed: int = 0
    skipped_grade: int = 0
    skipped_gates: int = 0
    errors: list = field(default_factory=list)
    events: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat(),
            "scanned": self.scanned,
            "opened": self.opened,
            "closed": self.closed,
            "skipped_grade": self.skipped_grade,
            "skipped_gates": self.skipped_gates,
            "errors": list(self.errors),
            "events": list(self.events),
        }


class AutoRobomlmLoop:
    def __init__(
        self,
        *,
        config: AutoRobomlmConfig,
        signal_provider: Callable[[str], Optional[dict]],
        broker: PaperBroker,
        watchlist_provider: Callable[[], list[str]],
        capital_provider: Callable[[], float],
        kill_switch_provider: Optional[Callable[[], bool]] = None,
        mode_provider: Optional[Callable[[], ExecutionMode]] = None,
        symbol_meta_provider: Optional[
            Callable[[str], Optional[dict]]
        ] = None,
    ):
        config.validate()

        if not callable(signal_provider):
            raise ValueError("signal_provider must be callable.")
        if not isinstance(broker, PaperBroker):
            raise ValueError("broker must be a PaperBroker instance.")
        if not callable(watchlist_provider):
            raise ValueError("watchlist_provider must be callable.")
        if not callable(capital_provider):
            raise ValueError("capital_provider must be callable.")

        self.config = config
        self.signal_provider = signal_provider
        self.broker = broker
        self.watchlist_provider = watchlist_provider
        self.capital_provider = capital_provider
        self.kill_switch_provider = kill_switch_provider
        self.mode_provider = mode_provider
        self.symbol_meta_provider = symbol_meta_provider

        self._state = LoopState.STOPPED
        self._lock = Lock()
        self._stop_event = Event()
        self._thread: Optional[Thread] = None
        self._last_tick: Optional[TickSummary] = None
        self._tick_count = 0

    # ------------------------------------------------------------------
    # Public lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        with self._lock:
            if self._state == LoopState.RUNNING:
                return
            self._state = LoopState.RUNNING
            self._stop_event.clear()
            self._thread = Thread(
                target=self._run, daemon=True, name="AutoRobomlmLoop"
            )
            self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        with self._lock:
            if self._state == LoopState.RUNNING:
                self._state = LoopState.STOPPED

    def kill(self) -> None:
        with self._lock:
            self._state = LoopState.KILLED
        self._stop_event.set()

    def resume(self) -> None:
        with self._lock:
            if self._state == LoopState.KILLED:
                self._state = LoopState.STOPPED

    def status(self) -> dict:
        with self._lock:
            state = self._state
        return {
            "engine": LOOP_NAME,
            "version": LOOP_VERSION,
            "state": state.value,
            "tick_count": self._tick_count,
            "last_tick": (
                self._last_tick.to_dict() if self._last_tick else None
            ),
            "config": self.config.as_dict(),
            "open_positions": len(self.broker.get_open_positions()),
            "total_positions": len(self.broker.get_all_positions()),
        }

    def active_trades(self) -> list[dict]:
        return self.broker.mark_to_market()

    # ------------------------------------------------------------------
    # One manual tick (for testing)
    # ------------------------------------------------------------------

    def tick(self) -> TickSummary:
        return self._do_tick()

    # ------------------------------------------------------------------
    # Thread body
    # ------------------------------------------------------------------

    def _run(self) -> None:
        while not self._stop_event.is_set():
            with self._lock:
                current_state = self._state

            if current_state == LoopState.KILLED:
                break
            if current_state != LoopState.RUNNING:
                break

            try:
                self._do_tick()
            except Exception as exc:  # pragma: no cover
                # Never let an exception kill the loop silently.
                with self._lock:
                    if self._last_tick is not None:
                        self._last_tick.errors.append(
                            f"tick exception: {exc!r}"
                        )

            self._stop_event.wait(self.config.loop_interval_sec)

    # ------------------------------------------------------------------
    # Core tick
    # ------------------------------------------------------------------

    def _do_tick(self) -> TickSummary:
        started = datetime.now(timezone.utc)
        summary = TickSummary(
            started_at=started, finished_at=started
        )

        # Step 1 - kill switch
        if self._kill_switch_engaged():
            summary.events.append(
                "kill_switch engaged; tick skipped"
            )
            summary.finished_at = datetime.now(timezone.utc)
            self._record_tick(summary)
            return summary

        # Step 2 - manage existing positions
        self._manage_positions(summary)

        # Step 3 - respect max positions
        if len(self.broker.get_open_positions()) >= (
            self.config.max_open_positions
        ):
            summary.events.append(
                "max_open_positions reached; scan skipped"
            )
            summary.finished_at = datetime.now(timezone.utc)
            self._record_tick(summary)
            return summary

        # Step 4 - scan watchlist
        try:
            watchlist = list(self.watchlist_provider() or [])
        except Exception as exc:
            summary.errors.append(f"watchlist error: {exc!r}")
            summary.finished_at = datetime.now(timezone.utc)
            self._record_tick(summary)
            return summary

        for symbol in watchlist:
            summary.scanned += 1

            if len(self.broker.get_open_positions()) >= (
                self.config.max_open_positions
            ):
                summary.events.append(
                    "max_open_positions reached during scan"
                )
                break

            self._evaluate_symbol(symbol, summary)

        summary.finished_at = datetime.now(timezone.utc)
        self._record_tick(summary)
        return summary

    # ------------------------------------------------------------------
    # Position management
    # ------------------------------------------------------------------

    def _manage_positions(self, summary: TickSummary) -> None:
        for position in self.broker.get_open_positions():
            price = self._price_for(position.symbol)
            if price is None:
                continue

            # Stop-loss
            if position.direction == TradeDirection.BUY:
                if price <= position.stop_loss:
                    self._close(position.position_id, "SL_HIT", summary)
                    continue
                if price >= position.take_profit:
                    self._close(position.position_id, "TP_HIT", summary)
                    continue
            else:
                if price >= position.stop_loss:
                    self._close(position.position_id, "SL_HIT", summary)
                    continue
                if price <= position.take_profit:
                    self._close(position.position_id, "TP_HIT", summary)
                    continue

            # D13 flip check
            signal = self._signal_for(position.symbol)
            if signal is None:
                continue

            signal_side = self._signal_side(signal)
            if signal_side is None:
                continue

            if signal_side != position.direction.value:
                self._close(position.position_id, "D13_FLIP", summary)
                continue

    def _close(
        self,
        position_id: str,
        reason: str,
        summary: TickSummary,
    ) -> None:
        result = self.broker.close_position(
            position_id, reason=reason
        )
        if result.status.value == "FILLED":
            summary.closed += 1
            summary.events.append(
                f"closed {position_id} ({reason})"
            )
        else:
            summary.errors.append(
                f"close failed {position_id}: {result.reason or result.errors}"
            )

    # ------------------------------------------------------------------
    # Symbol evaluation
    # ------------------------------------------------------------------

    def _evaluate_symbol(
        self, symbol: str, summary: TickSummary
    ) -> None:
        signal = self._signal_for(symbol)

        if signal is None:
            summary.events.append(f"{symbol}: no signal")
            return

        # Grade
        raw_score = self._extract_score(signal)
        if raw_score is None:
            summary.skipped_grade += 1
            summary.events.append(
                f"{symbol}: no score available"
            )
            return

        grade_result = evaluate_grade(
            score=raw_score,
            min_grade=self.config.min_grade,
            source=GradeSource.D13_DECISION,
        )

        if not grade_result.is_eligible:
            summary.skipped_grade += 1
            summary.events.append(
                f"{symbol}: grade ineligible "
                f"({grade_result.grade.value if grade_result.grade else 'NONE'})"
            )
            return

        # Direction
        direction = self._signal_side(signal)
        if direction is None:
            summary.skipped_gates += 1
            summary.events.append(f"{symbol}: no clear direction")
            return

        # Price
        price = self._price_for(symbol)
        if price is None:
            summary.skipped_gates += 1
            summary.events.append(f"{symbol}: no price")
            return

        # Objective gate
        objective_result = evaluate_objective(
            ObjectiveDefinition(
                objective_type=ObjectiveType.RISK_ADJUSTED_RETURN,
                metric="grade_score",
                version="1.0",
                thresholds={
                    "min_score": float(
                        self.config.min_score_required() or 0.0
                    ),
                    "risk_per_trade_pct": (
                        self.config.risk_per_trade_pct
                    ),
                },
                description=(
                    "AutoROBOMLM default objective: "
                    "risk-adjusted return filtered by grade."
                ),
            )
        )
        if not objective_result.passed:
            summary.skipped_gates += 1
            summary.events.append(
                f"{symbol}: objective gate closed"
            )
            return

        # Resource gate
        try:
            capital = float(self.capital_provider())
        except Exception as exc:
            summary.errors.append(f"capital error: {exc!r}")
            return

        resource_result = evaluate_resources(
            (
                ResourceCheck(
                    kind=ResourceKind.CAPITAL,
                    name="capital_available",
                    required=0.0,
                    available=max(0.0, capital),
                    unit="currency",
                ),
            )
        )
        if not resource_result.passed:
            summary.skipped_gates += 1
            summary.events.append(
                f"{symbol}: resource gate closed"
            )
            return

        # Constraint gate
        constraint_checks = [
            ConstraintCheck(
                name="mode_allows_execution",
                kind=ConstraintKind.MODE_POLICY,
                disposition=ConstraintDisposition.ALLOW,
                reason="mode policy check delegated to caller",
                source="auto_loop",
            ),
        ]

        constraint_result = evaluate_constraints(
            tuple(constraint_checks)
        )
        if not constraint_result.passed:
            summary.skipped_gates += 1
            summary.events.append(
                f"{symbol}: constraint gate closed"
            )
            return

        # SL/TP
        sl_tp_result = calculate_sl_tp(
            direction=SLTPDirection(direction),
            entry_price=price,
            sl_atr_multiplier=self.config.sl_atr_multiplier,
            tp_atr_multiplier=self.config.tp_atr_multiplier,
        )
        if sl_tp_result.stop_loss is None:
            summary.errors.append(
                f"{symbol}: SL/TP failed ({sl_tp_result.errors})"
            )
            return

        # Allocation
        allocation = allocate_capital(
            capital=capital,
            entry_price=price,
            stop_loss=sl_tp_result.stop_loss,
            risk_per_trade_pct=self.config.risk_per_trade_pct,
            max_position_pct=self.config.max_position_pct,
        )
        if allocation.quantity is None:
            summary.errors.append(
                f"{symbol}: allocation failed "
                f"({allocation.errors or allocation.reasons})"
            )
            return

        # Paper fill
        fill = self.broker.open_position(
            symbol=symbol,
            direction=TradeDirection(direction),
            quantity=allocation.quantity,
            stop_loss=sl_tp_result.stop_loss,
            take_profit=sl_tp_result.take_profit,
        )
        if fill.position is None:
            summary.errors.append(
                f"{symbol}: fill rejected ({fill.reason or fill.errors})"
            )
            return

        summary.opened += 1
        summary.events.append(
            f"{symbol}: opened {direction} "
            f"qty={allocation.quantity} at {fill.fill_price}"
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _kill_switch_engaged(self) -> bool:
        if self.kill_switch_provider is None:
            return False
        try:
            return bool(self.kill_switch_provider())
        except Exception:
            # Fail-closed: if provider errors, treat as engaged.
            return True

    def _price_for(self, symbol: str) -> Optional[float]:
        try:
            price = self.broker.price_provider(symbol)
        except Exception:
            return None
        if price is None:
            return None
        try:
            price = float(price)
        except (TypeError, ValueError):
            return None
        if price <= 0.0:
            return None
        return price

    def _signal_for(self, symbol: str) -> Optional[dict]:
        try:
            return self.signal_provider(symbol)
        except Exception:
            return None

    @staticmethod
    def _extract_score(signal: dict) -> Optional[float]:
        if not isinstance(signal, dict):
            return None
        for key in ("decision_score", "score", "confidence"):
            if key in signal:
                value = signal[key]
                try:
                    value = float(value)
                except (TypeError, ValueError):
                    continue
                if value <= 1.0 and key == "confidence":
                    value *= 100.0
                return value
        return None

    @staticmethod
    def _signal_side(signal: dict) -> Optional[str]:
        if not isinstance(signal, dict):
            return None
        for key in ("signal", "decision", "direction"):
            value = signal.get(key)
            if value is None:
                continue
            text = str(value).strip().upper()
            if text in {"BUY", "LONG"}:
                return "BUY"
            if text in {"SELL", "SHORT"}:
                return "SELL"
        return None

    def _record_tick(self, summary: TickSummary) -> None:
        with self._lock:
            self._last_tick = summary
            self._tick_count += 1


__all__ = [
    "LOOP_NAME", "LOOP_VERSION",
    "LoopState", "TickSummary", "AutoRobomlmLoop",
]
'''

for filename, content in FILES.items():
    path = ROOT / filename
    path.write_text(content, encoding="utf-8")
    print(f"WROTE: {path}")

print()
print(f"DONE. Files in {ROOT}:")
for p in sorted(ROOT.glob("*.py")):
    print(f"  {p.name} ({p.stat().st_size} bytes)")