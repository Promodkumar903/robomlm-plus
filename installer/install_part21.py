"""
Revert parallel account system + connect AutoROBOMLM to existing _ACCOUNT
"""
from pathlib import Path
import shutil
import re
from datetime import datetime

ROOT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\autorobomlm")
API = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\api\v1\autorobomlm_api.py")

applied = []
skipped = []

TS = datetime.now().strftime('%Y%m%d_%H%M%S')

# ==================================================================
# 1. Remove parallel account_manager.py (move to backup)
# ==================================================================
parallel_file = ROOT / "account_manager.py"
if parallel_file.exists():
    backup = parallel_file.with_suffix(f".py.REMOVED_{TS}")
    shutil.move(str(parallel_file), str(backup))
    applied.append(f"removed: account_manager.py -> {backup.name}")
else:
    skipped.append("account_manager.py already gone")

# ==================================================================
# 2. Patch autorobomlm_api.py
# ==================================================================
if not API.exists():
    print(f"ERROR: {API} not found")
    raise SystemExit(1)

content = API.read_text(encoding="utf-8")
backup = API.with_suffix(f".py.bak_{TS}")
shutil.copy2(API, backup)
print(f"BACKUP: {backup}")

# --- 2a. Replace AccountManager import with _ACCOUNT import ---
old_import = '''from app.autorobomlm.account_manager import AccountManager
from app.autorobomlm.portfolio_tracker import PortfolioTracker

from pathlib import Path as _Path

_DATA_DIR = _Path(r"C:\\Users\\Administrator\\ROBOMLM_PLUS\\data\\autorobomlm")
_DATA_DIR.mkdir(parents=True, exist_ok=True)

_ACCOUNT_PERSIST = _DATA_DIR / "account.json"
_PORTFOLIO_PERSIST = _DATA_DIR / "portfolio.json"'''

new_import = '''from app.autorobomlm.portfolio_tracker import PortfolioTracker

# Existing account system (single source of truth)
from app.api.account_routes import _ACCOUNT

from pathlib import Path as _Path

_DATA_DIR = _Path(r"C:\\Users\\Administrator\\ROBOMLM_PLUS\\data\\autorobomlm")
_DATA_DIR.mkdir(parents=True, exist_ok=True)

_PORTFOLIO_PERSIST = _DATA_DIR / "portfolio.json"


def _get_balance() -> float:
    """Read balance from existing account state."""
    try:
        return float(_ACCOUNT.get("balance", 0.0))
    except (TypeError, ValueError):
        return 0.0


def _record_realized_pnl(pnl: float) -> None:
    """Write realized P&L into existing account state."""
    try:
        pnl = float(pnl)
    except (TypeError, ValueError):
        return
    _ACCOUNT["balance"] = float(_ACCOUNT.get("balance", 0.0)) + pnl
    _ACCOUNT["capital"] = _ACCOUNT["balance"]
    _ACCOUNT["today_pnl"] = float(_ACCOUNT.get("today_pnl", 0.0)) + pnl'''

if "def _get_balance()" in content:
    skipped.append("2a: already patched")
elif old_import in content:
    content = content.replace(old_import, new_import, 1)
    applied.append("2a: import + balance helpers")
else:
    # Fallback - try shorter marker
    marker = "from app.autorobomlm.account_manager import AccountManager"
    if marker in content:
        # Find whole block from marker to _PORTFOLIO_PERSIST
        idx_start = content.find(marker)
        idx_end = content.find('_PORTFOLIO_PERSIST = _DATA_DIR / "portfolio.json"')
        if idx_end > 0:
            idx_end += len('_PORTFOLIO_PERSIST = _DATA_DIR / "portfolio.json"')
            content = content[:idx_start] + new_import + content[idx_end:]
            applied.append("2a: import patched (fallback)")
        else:
            skipped.append("2a: portfolio marker not found")
    else:
        skipped.append("2a: import marker not found")

# --- 2b. Remove "account": None from _state ---
old_state_line = '    "account": None,\n'
if old_state_line in content:
    content = content.replace(old_state_line, "", 1)
    applied.append("2b: removed account from _state")

# --- 2c. Remove _get_account() function ---
old_get_account = '''def _get_account() -> AccountManager:
    """Singleton account ΓÇö persisted to disk."""
    if _state["account"] is None:
        _state["account"] = AccountManager(
            initial_balance=100000.0,
            persist_path=_ACCOUNT_PERSIST,
        )
    return _state["account"]'''

# Also try with regular dash
old_get_account2 = '''def _get_account() -> AccountManager:
    """Singleton account — persisted to disk."""
    if _state["account"] is None:
        _state["account"] = AccountManager(
            initial_balance=100000.0,
            persist_path=_ACCOUNT_PERSIST,
        )
    return _state["account"]'''

if old_get_account in content:
    content = content.replace(old_get_account, "", 1)
    applied.append("2c: removed _get_account (dash variant)")
elif old_get_account2 in content:
    content = content.replace(old_get_account2, "", 1)
    applied.append("2c: removed _get_account")

# --- 2d. Patch _build_loop ---
old_build = '''    symbols = list(cfg.manual_watchlist) or ["BTC/USDT"]

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

new_build = '''    symbols = list(cfg.manual_watchlist) or ["BTC/USDT"]

    broker = _get_broker()

    signal_provider = make_live_signal_provider()

    loop = AutoRobomlmLoop(
        config=cfg,
        signal_provider=signal_provider,
        broker=broker,
        watchlist_provider=lambda: list(symbols),
        capital_provider=lambda: _get_balance(),
    )
    return loop'''

if old_build in content:
    content = content.replace(old_build, new_build, 1)
    applied.append("2d: _build_loop uses _ACCOUNT")
else:
    skipped.append("2d: _build_loop pattern not found")

# --- 2e. Patch close hook ---
old_hook = '''    def wrapped_close(position_id, *, reason):
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
        return result'''

new_hook = '''    def wrapped_close(position_id, *, reason):
        result = _original_close(position_id, reason=reason)
        if result.position is not None and result.fill_price is not None:
            try:
                portfolio = _get_portfolio()
                trade = portfolio.record_close(
                    result.position, result.fill_price
                )
                _record_realized_pnl(trade.pnl)
            except Exception:
                pass
        return result'''

if old_hook in content:
    content = content.replace(old_hook, new_hook, 1)
    applied.append("2e: close hook uses _ACCOUNT")
else:
    skipped.append("2e: close hook pattern not found")

# --- 2f. Remove parallel /account/balance, /account/ledger, /account/deposit, /account/withdraw ---
# Find the ACCOUNT ENDPOINTS block and remove it (up to PORTFOLIO ENDPOINTS)
start_marker = "# ============================================================\n# ACCOUNT ENDPOINTS"
end_marker = "# ============================================================\n# PORTFOLIO ENDPOINTS"

sidx = content.find(start_marker)
eidx = content.find(end_marker)

if sidx >= 0 and eidx > sidx:
    content = content[:sidx] + content[eidx:]
    applied.append("2f: removed parallel /account/* endpoints")
else:
    skipped.append("2f: parallel account endpoints not found")

# --- 2g. Fix portfolio_summary to use _get_balance ---
old_sum = '''    portfolio_stats = portfolio.summary()
    account_stats = account.summary()

    equity = account_stats["balance"] + unrealized

    return {
        "ok": True,
        "portfolio": portfolio_stats,
        "account": account_stats,
        "unrealized_pnl": round(unrealized, 6),
        "equity": round(equity, 6),
    }'''

new_sum = '''    portfolio_stats = portfolio.summary()
    balance = _get_balance()
    equity = balance + unrealized

    return {
        "ok": True,
        "portfolio": portfolio_stats,
        "account": {
            "balance": balance,
            "mode": _ACCOUNT.get("mode", "PAPER"),
            "currency": _ACCOUNT.get("currency", "INR"),
            "today_pnl": _ACCOUNT.get("today_pnl", 0.0),
        },
        "unrealized_pnl": round(unrealized, 6),
        "equity": round(equity, 6),
    }'''

if old_sum in content:
    content = content.replace(old_sum, new_sum, 1)
    applied.append("2g: portfolio_summary uses _ACCOUNT")
else:
    skipped.append("2g: portfolio_summary pattern not found")

# --- 2h. Remove account variable usage in portfolio_summary ---
old_line = "    account = _get_account()\n"
if old_line in content:
    content = content.replace(old_line, "", 1)
    applied.append("2h: removed _get_account call")

# Write
API.write_text(content, encoding="utf-8")

# ==================================================================
# 3. Report
# ==================================================================
print()
print("APPLIED:")
for a in applied:
    print(f"  + {a}")
print("SKIPPED:")
for s in skipped:
    print(f"  - {s}")
print()
print(f"UPDATED: {API}")
print()
print("Next:")
print("  1. Restart backend (Ctrl+C, then re-run uvicorn)")
print("  2. Test:")
print("     curl http://127.0.0.1:8000/api/account/summary")
print("     curl http://127.0.0.1:8000/api/autorobomlm/portfolio/summary")