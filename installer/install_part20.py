"""
AutoROBOMLM — Account + Portfolio + Fund management
+ Fix broker/account persistence across config changes
"""
from pathlib import Path
import shutil
from datetime import datetime

ROOT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\autorobomlm")
API = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\api\v1\autorobomlm_api.py")

applied = []
skipped = []

# ==================================================================
# FILE 1: account_manager.py
# ==================================================================
account_content = '''"""
ROBOMLM_PLUS - AutoROBOMLM Account Manager

Tracks cash balance, deposits, withdrawals, ledger.
Persists to JSON.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from threading import RLock
from typing import Any, Optional
from uuid import uuid4
import json


ACCOUNT_ENGINE = "AutoROBOMLM_AccountManager"
ACCOUNT_VERSION = "1.0"


class LedgerKind(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    REALIZED_PNL = "REALIZED_PNL"
    FEE = "FEE"


@dataclass
class LedgerEntry:
    entry_id: str
    kind: str
    amount: float
    balance_after: float
    note: str = ""
    created_at: str = ""

    def to_dict(self):
        return asdict(self)


class AccountManager:
    def __init__(
        self,
        *,
        initial_balance: float = 100000.0,
        persist_path: Optional[Path] = None,
    ):
        if initial_balance < 0:
            raise ValueError("initial_balance must be >= 0")

        self._lock = RLock()
        self._persist_path = persist_path
        self._balance = float(initial_balance)
        self._ledger: list[LedgerEntry] = []
        self._deposits_total = float(initial_balance)
        self._withdrawals_total = 0.0
        self._realized_pnl_total = 0.0

        if persist_path and persist_path.exists():
            self._load()

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def deposit(
        self, amount: float, note: str = ""
    ) -> LedgerEntry:
        if amount <= 0:
            raise ValueError("deposit amount must be > 0")

        with self._lock:
            self._balance += float(amount)
            self._deposits_total += float(amount)
            entry = self._record(
                LedgerKind.DEPOSIT, float(amount), note
            )
            self._save()
            return entry

    def withdraw(
        self, amount: float, note: str = ""
    ) -> LedgerEntry:
        if amount <= 0:
            raise ValueError("withdrawal amount must be > 0")
        with self._lock:
            if amount > self._balance:
                raise ValueError(
                    f"insufficient balance: {self._balance} < {amount}"
                )
            self._balance -= float(amount)
            self._withdrawals_total += float(amount)
            entry = self._record(
                LedgerKind.WITHDRAWAL, -float(amount), note
            )
            self._save()
            return entry

    def record_realized_pnl(
        self, pnl: float, note: str = ""
    ) -> LedgerEntry:
        with self._lock:
            self._balance += float(pnl)
            self._realized_pnl_total += float(pnl)
            entry = self._record(
                LedgerKind.REALIZED_PNL, float(pnl), note
            )
            self._save()
            return entry

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def balance(self) -> float:
        with self._lock:
            return self._balance

    def ledger(self, limit: int = 100) -> list[dict]:
        with self._lock:
            entries = self._ledger[-limit:]
            return [e.to_dict() for e in entries]

    def summary(self) -> dict:
        with self._lock:
            return {
                "engine": ACCOUNT_ENGINE,
                "version": ACCOUNT_VERSION,
                "balance": round(self._balance, 4),
                "deposits_total": round(self._deposits_total, 4),
                "withdrawals_total": round(self._withdrawals_total, 4),
                "realized_pnl_total": round(
                    self._realized_pnl_total, 4
                ),
                "ledger_count": len(self._ledger),
            }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _record(
        self,
        kind: LedgerKind,
        amount: float,
        note: str,
    ) -> LedgerEntry:
        entry = LedgerEntry(
            entry_id=str(uuid4()),
            kind=kind.value,
            amount=round(float(amount), 6),
            balance_after=round(self._balance, 6),
            note=str(note),
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._ledger.append(entry)
        return entry

    def _save(self):
        if not self._persist_path:
            return
        try:
            self._persist_path.parent.mkdir(
                parents=True, exist_ok=True
            )
            payload = {
                "balance": self._balance,
                "deposits_total": self._deposits_total,
                "withdrawals_total": self._withdrawals_total,
                "realized_pnl_total": self._realized_pnl_total,
                "ledger": [e.to_dict() for e in self._ledger],
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
            self._balance = float(data.get("balance", 0.0))
            self._deposits_total = float(
                data.get("deposits_total", 0.0)
            )
            self._withdrawals_total = float(
                data.get("withdrawals_total", 0.0)
            )
            self._realized_pnl_total = float(
                data.get("realized_pnl_total", 0.0)
            )
            for e in data.get("ledger", []):
                self._ledger.append(
                    LedgerEntry(
                        entry_id=e.get("entry_id", ""),
                        kind=e.get("kind", ""),
                        amount=float(e.get("amount", 0.0)),
                        balance_after=float(
                            e.get("balance_after", 0.0)
                        ),
                        note=e.get("note", ""),
                        created_at=e.get("created_at", ""),
                    )
                )
        except Exception:
            pass


__all__ = [
    "ACCOUNT_ENGINE",
    "ACCOUNT_VERSION",
    "LedgerKind",
    "LedgerEntry",
    "AccountManager",
]
'''

(ROOT / "account_manager.py").write_text(
    account_content, encoding="utf-8"
)
applied.append("file: account_manager.py")


# ==================================================================
# FILE 2: portfolio_tracker.py
# ==================================================================
portfolio_content = '''"""
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
    exit_reason: str
    pnl: float
    pnl_pct: float
    opened_at: str
    closed_at: str

    def to_dict(self):
        return asdict(self)


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
'''

(ROOT / "portfolio_tracker.py").write_text(
    portfolio_content, encoding="utf-8"
)
applied.append("file: portfolio_tracker.py")


# ==================================================================
# FILE 3: Patch api v1 to wire account + portfolio + singleton broker
# ==================================================================
if API.exists():
    content = API.read_text(encoding="utf-8")
    backup = API.with_suffix(
        f".py.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    shutil.copy2(API, backup)

    # 3a — imports
    if "from app.autorobomlm.account_manager import" not in content:
        old_imports = (
            "from app.autorobomlm.signal_adapter import (\n"
            "    make_live_signal_provider,\n"
            "    make_price_provider,\n"
            ")"
        )
        new_imports = old_imports + '''


from app.autorobomlm.account_manager import AccountManager
from app.autorobomlm.portfolio_tracker import PortfolioTracker

from pathlib import Path as _Path

_DATA_DIR = _Path(r"C:\\Users\\Administrator\\ROBOMLM_PLUS\\data\\autorobomlm")
_DATA_DIR.mkdir(parents=True, exist_ok=True)

_ACCOUNT_PERSIST = _DATA_DIR / "account.json"
_PORTFOLIO_PERSIST = _DATA_DIR / "portfolio.json"'''

        if old_imports in content:
            content = content.replace(old_imports, new_imports, 1)
            applied.append("api: account+portfolio imports added")

    # 3b — singletons in _state
    if "_state[\"account\"]" not in content and "_state['account']" not in content:
        # Replace the _state initialization dict
        old_state = '''_state: dict[str, Any] = {
    "loop": None,
    "config": None,
    "api": None,
}'''
        new_state = '''_state: dict[str, Any] = {
    "loop": None,
    "config": None,
    "api": None,
    "broker": None,
    "account": None,
    "portfolio": None,
}'''

        if old_state in content:
            content = content.replace(old_state, new_state, 1)
            applied.append("api: _state extended with broker/account/portfolio")
        else:
            skipped.append("api: _state marker not found")

    # 3c — rewrite _build_loop to use singletons
    old_build = '''def _build_loop(cfg: AutoRobomlmConfig) -> AutoRobomlmLoop:
    """Create a fresh loop from config."""
    symbols = list(cfg.manual_watchlist) or ["BTC/USDT"]
    capital = 100000.0

    price_provider = make_price_provider()
    signal_provider = make_live_signal_provider()

    broker = PaperBroker(
        price_provider=price_provider,
        slippage_pct=0.0,
    )

    loop = AutoRobomlmLoop(
        config=cfg,
        signal_provider=signal_provider,
        broker=broker,
        watchlist_provider=lambda: list(symbols),
        capital_provider=lambda: float(capital),
    )
    return loop'''

    new_build = '''def _get_broker() -> PaperBroker:
    """Singleton broker — persists across config changes."""
    if _state["broker"] is None:
        _state["broker"] = PaperBroker(
            price_provider=make_price_provider(),
            slippage_pct=0.0,
        )
    return _state["broker"]


def _get_account() -> AccountManager:
    """Singleton account — persisted to disk."""
    if _state["account"] is None:
        _state["account"] = AccountManager(
            initial_balance=100000.0,
            persist_path=_ACCOUNT_PERSIST,
        )
    return _state["account"]


def _get_portfolio() -> PortfolioTracker:
    """Singleton portfolio — persisted to disk."""
    if _state["portfolio"] is None:
        _state["portfolio"] = PortfolioTracker(
            persist_path=_PORTFOLIO_PERSIST,
        )
    return _state["portfolio"]


def _build_loop(cfg: AutoRobomlmConfig) -> AutoRobomlmLoop:
    """Create a new loop, reusing singleton broker + account."""
    symbols = list(cfg.manual_watchlist) or ["BTC/USDT"]

    broker = _get_broker()
    account = _get_account()

    signal_provider = make_live_signal_provider()

    loop = AutoRobomlmLoop(
        config=cfg,
        signal_provider=signal_provider,
        broker=broker,
        watchlist_provider=lambda: list(symbols),
        capital_provider=lambda: float(account.balance()),
    )
    return loop'''

    if "def _get_broker()" in content:
        skipped.append("api: singleton broker already exists")
    elif old_build in content:
        content = content.replace(old_build, new_build, 1)
        applied.append("api: singleton broker + account + portfolio")
    else:
        skipped.append("api: _build_loop marker not found")

    # 3d — Patch close path to record to portfolio + account
    # Find the loop's _close method call — actually we can't easily do that
    # so instead patch the close endpoint (if any) or wrap broker.close_position
    # Simpler: monkey-patch inside _ensure_state
    if "# PATCH: wrap broker.close_position" not in content:
        patch_block = '''
# PATCH: wrap broker.close_position to record to portfolio + account
_original_close = None


def _install_close_hook():
    global _original_close
    broker = _get_broker()
    if _original_close is None:
        _original_close = broker.close_position

    def wrapped_close(position_id, *, reason):
        result = _original_close(position_id, reason=reason)
        # If filled, record to portfolio + account
        if result.position is not None and result.fill_price is not None:
            try:
                portfolio = _get_portfolio()
                account = _get_account()
                trade = portfolio.record_close(
                    result.position, result.fill_price
                )
                account.record_realized_pnl(
                    trade.pnl,
                    note=f"close {trade.symbol} ({trade.exit_reason})",
                )
            except Exception:
                pass
        return result

    broker.close_position = wrapped_close


'''
        # Insert before _ensure_state
        marker = "def _ensure_state() -> None:"
        if marker in content:
            content = content.replace(
                marker, patch_block + marker, 1
            )
            # Also call _install_close_hook in _ensure_state
            old_ensure = '''def _ensure_state() -> None:
    """Lazily build loop + config + api."""
    if _state["api"] is not None:
        return'''
            new_ensure = '''def _ensure_state() -> None:
    """Lazily build loop + config + api."""
    _install_close_hook()
    if _state["api"] is not None:
        return'''
            if old_ensure in content:
                content = content.replace(old_ensure, new_ensure, 1)
                applied.append("api: close hook installed")
            else:
                skipped.append("api: _ensure_state marker not matched")

    # 3e — Add account + portfolio endpoints
    if "/account/deposit" in content:
        skipped.append("api: account endpoints already exist")
    else:
        endpoints = '''

# ============================================================
# ACCOUNT ENDPOINTS
# ============================================================

@router.get("/account/balance")
def account_balance() -> dict:
    _ensure_state()
    account = _get_account()
    return {"ok": True, "account": account.summary()}


@router.get("/account/ledger")
def account_ledger(limit: int = 100) -> dict:
    _ensure_state()
    account = _get_account()
    return {"ok": True, "ledger": account.ledger(limit=limit)}


@router.post("/account/deposit")
def account_deposit(payload: dict = Body(...)) -> dict:
    _ensure_state()
    amount = payload.get("amount")
    note = str(payload.get("note") or "manual deposit")
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=400, detail="amount must be numeric"
        )
    try:
        entry = _get_account().deposit(amount, note=note)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {
        "ok": True,
        "action": "deposit",
        "entry": entry.to_dict(),
        "account": _get_account().summary(),
    }


@router.post("/account/withdraw")
def account_withdraw(payload: dict = Body(...)) -> dict:
    _ensure_state()
    amount = payload.get("amount")
    note = str(payload.get("note") or "manual withdrawal")
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=400, detail="amount must be numeric"
        )
    try:
        entry = _get_account().withdraw(amount, note=note)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {
        "ok": True,
        "action": "withdraw",
        "entry": entry.to_dict(),
        "account": _get_account().summary(),
    }


# ============================================================
# PORTFOLIO ENDPOINTS
# ============================================================

@router.get("/portfolio/summary")
def portfolio_summary() -> dict:
    _ensure_state()
    portfolio = _get_portfolio()
    account = _get_account()
    broker = _get_broker()

    # Unrealized P&L from open positions
    unrealized = 0.0
    for p in broker.get_open_positions():
        price = broker.price_provider(p.symbol)
        if price is not None:
            unrealized += p.pnl(price)

    portfolio_stats = portfolio.summary()
    account_stats = account.summary()

    equity = account_stats["balance"] + unrealized

    return {
        "ok": True,
        "portfolio": portfolio_stats,
        "account": account_stats,
        "unrealized_pnl": round(unrealized, 6),
        "equity": round(equity, 6),
    }


@router.get("/portfolio/trades")
def portfolio_trades(limit: int = 100) -> dict:
    _ensure_state()
    return {
        "ok": True,
        "trades": _get_portfolio().trades(limit=limit),
    }

'''

        # Insert before `__all__`
        marker = "\n\n__all__ = [\"router\"]"
        if marker in content:
            content = content.replace(
                marker, endpoints + "__all__ = [\"router\"]", 1
            )
            applied.append("api: account + portfolio endpoints added")
        else:
            skipped.append("api: __all__ marker not found")

    API.write_text(content, encoding="utf-8")

# ==================================================================
# Report
# ==================================================================
print()
print("APPLIED:")
for a in applied:
    print(f"  + {a}")
print("SKIPPED:")
for s in skipped:
    print(f"  - {s}")
print()
print("Files created:")
print(f"  {ROOT / 'account_manager.py'}")
print(f"  {ROOT / 'portfolio_tracker.py'}")
print()
print("Next:")
print("  1. Restart backend (Ctrl+C, then re-run uvicorn)")
print("  2. Test endpoints:")
print("     curl http://127.0.0.1:8000/api/autorobomlm/account/balance")
print("     curl http://127.0.0.1:8000/api/autorobomlm/portfolio/summary")
print("  3. Frontend wiring agla step")