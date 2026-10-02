"""
ROBOMLM_PLUS - AutoROBOMLM Portfolio Tracker

Records closed trades and computes P&L statistics.
Persists to JSON.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Optional
from uuid import uuid4
import json


PORTFOLIO_ENGINE = "AutoROBOMLM_PortfolioTracker"
PORTFOLIO_VERSION = "1.0"


@dataclass
class ClosedTrade:
    trade_id: str
    position_id: str
    symbol: str
    direction: str
    quantity: float
    entry_price: float
    exit_price: float
    stop_loss: float
    take_profit: float
    entry_grade: Optional[str]
    entry_score: Optional[float]
    entry_source: Optional[str]
    exit_reason: str
    pnl: float
    pnl_pct: float
    opened_at: str
    closed_at: str

    def to_dict(self):
        return asdict(self)


def _stats_by_source(trades: list) -> dict:
    """Group closed trades by entry_source. Per-source stats."""
    buckets: dict = {}
    for t in trades:
        src = (getattr(t, "entry_source", None) or "UNKNOWN")
        buckets.setdefault(src, []).append(t)

    out = {}
    for src, group in buckets.items():
        total = len(group)
        wins = [t for t in group if t.pnl > 0]
        losses = [t for t in group if t.pnl < 0]
        breakeven = total - len(wins) - len(losses)
        realized = sum(t.pnl for t in group)
        gross_profit = sum(t.pnl for t in wins)
        gross_loss = abs(sum(t.pnl for t in losses))
        profit_factor = (
            gross_profit / gross_loss if gross_loss > 0 else 0.0
        )

        out[src] = {
            "trades_total": total,
            "wins": len(wins),
            "losses": len(losses),
            "breakeven": breakeven,
            "win_rate": (
                round(len(wins) / total * 100.0, 4)
                if total else 0.0
            ),
            "realized_pnl": round(realized, 6),
            "avg_win": (
                round(gross_profit / len(wins), 6)
                if wins else 0.0
            ),
            "avg_loss": (
                round(-gross_loss / len(losses), 6)
                if losses else 0.0
            ),
            "profit_factor": round(profit_factor, 6),
        }
    return out


class PortfolioTracker:
    def __init__(
        self,
        *,
        persist_path: Optional[Path] = None,
    ):
        self._lock = RLock()
        self._persist_path = persist_path
        self._closed: list[ClosedTrade] = []
        if persist_path and persist_path.exists():
            self._load()

    # ------------------------------------------------------------------

    def record_close(self, position: Any, exit_price: float) -> ClosedTrade:
        """
        Record a closed position. `position` must expose:
        position_id, symbol, direction, quantity, entry_price,
        stop_loss, take_profit, entry_grade, entry_score, opened_at
        """
        direction = str(getattr(position, "direction", ""))
        # direction may be enum or str
        if hasattr(position.direction, "value"):
            direction = str(position.direction.value)

        qty = float(position.quantity)
        entry = float(position.entry_price)
        exit_ = float(exit_price)

        if direction.upper() in {"BUY", "LONG"}:
            pnl = (exit_ - entry) * qty
            pnl_pct = ((exit_ - entry) / entry * 100.0) if entry else 0.0
        else:
            pnl = (entry - exit_) * qty
            pnl_pct = ((entry - exit_) / entry * 100.0) if entry else 0.0

        trade = ClosedTrade(
            trade_id=str(uuid4()),
            position_id=str(
                getattr(position, "position_id", "")
            ),
            symbol=str(getattr(position, "symbol", "")),
            direction=direction,
            quantity=round(qty, 8),
            entry_price=round(entry, 8),
            exit_price=round(exit_, 8),
            stop_loss=float(getattr(position, "stop_loss", 0.0)),
            take_profit=float(
                getattr(position, "take_profit", 0.0)
            ),
            entry_grade=getattr(position, "entry_grade", None),
            entry_score=getattr(position, "entry_score", None),
            entry_source=getattr(position, "entry_source", None),
            exit_reason=str(
                getattr(position, "exit_reason", "") or ""
            ),
            pnl=round(pnl, 6),
            pnl_pct=round(pnl_pct, 6),
            opened_at=str(
                getattr(position, "opened_at", "")
            ),
            closed_at=datetime.now(timezone.utc).isoformat(),
        )

        with self._lock:
            self._closed.append(trade)
            self._save()

        return trade

    # ------------------------------------------------------------------

    def trades(self, limit: int = 100) -> list[dict]:
        with self._lock:
            return [t.to_dict() for t in self._closed[-limit:]]

    def summary(self) -> dict:
        with self._lock:
            trades = list(self._closed)

        total = len(trades)
        if total == 0:
            return {
                "engine": PORTFOLIO_ENGINE,
                "version": PORTFOLIO_VERSION,
                "trades_total": 0,
                "wins": 0,
                "losses": 0,
                "breakeven": 0,
                "win_rate": 0.0,
                "realized_pnl": 0.0,
                "avg_win": 0.0,
                "avg_loss": 0.0,
                "profit_factor": 0.0,
                "max_win": 0.0,
                "max_loss": 0.0,
            }

        wins = [t for t in trades if t.pnl > 0]
        losses = [t for t in trades if t.pnl < 0]
        breakeven = total - len(wins) - len(losses)

        gross_profit = sum(t.pnl for t in wins)
        gross_loss = abs(sum(t.pnl for t in losses))

        realized = sum(t.pnl for t in trades)

        avg_win = (
            gross_profit / len(wins) if wins else 0.0
        )
        avg_loss = (
            -gross_loss / len(losses) if losses else 0.0
        )
        profit_factor = (
            gross_profit / gross_loss if gross_loss > 0 else 0.0
        )

        return {
            "engine": PORTFOLIO_ENGINE,
            "version": PORTFOLIO_VERSION,
            "trades_total": total,
            "wins": len(wins),
            "losses": len(losses),
            "breakeven": breakeven,
            "win_rate": round(
                len(wins) / total * 100.0, 4
            ) if total else 0.0,
            "realized_pnl": round(realized, 6),
            "avg_win": round(avg_win, 6),
            "avg_loss": round(avg_loss, 6),
            "profit_factor": round(profit_factor, 6),
            "max_win": round(
                max((t.pnl for t in trades), default=0.0), 6
            ),
            "max_loss": round(
                min((t.pnl for t in trades), default=0.0), 6
            ),
            "by_source": _stats_by_source(trades),
        }

    # ------------------------------------------------------------------

    def _save(self):
        if not self._persist_path:
            return
        try:
            self._persist_path.parent.mkdir(
                parents=True, exist_ok=True
            )
            payload = {
                "closed": [t.to_dict() for t in self._closed]
            }
            self._persist_path.write_text(
                json.dumps(payload, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

    def _load(self):
        try:
            data = json.loads(
                self._persist_path.read_text(encoding="utf-8")
            )
            for t in data.get("closed", []):
                self._closed.append(
                    ClosedTrade(
                        trade_id=t.get("trade_id", ""),
                        position_id=t.get("position_id", ""),
                        symbol=t.get("symbol", ""),
                        direction=t.get("direction", ""),
                        quantity=float(t.get("quantity", 0.0)),
                        entry_price=float(
                            t.get("entry_price", 0.0)
                        ),
                        exit_price=float(
                            t.get("exit_price", 0.0)
                        ),
                        stop_loss=float(t.get("stop_loss", 0.0)),
                        take_profit=float(
                            t.get("take_profit", 0.0)
                        ),
                        entry_grade=t.get("entry_grade"),
                        entry_score=t.get("entry_score"),
                        entry_source=t.get("entry_source"),
                        exit_reason=t.get("exit_reason", ""),
                        pnl=float(t.get("pnl", 0.0)),
                        pnl_pct=float(t.get("pnl_pct", 0.0)),
                        opened_at=t.get("opened_at", ""),
                        closed_at=t.get("closed_at", ""),
                    )
                )
        except Exception:
            pass


__all__ = [
    "PORTFOLIO_ENGINE",
    "PORTFOLIO_VERSION",
    "ClosedTrade",
    "PortfolioTracker",
]
