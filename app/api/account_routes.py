from pathlib import Path
import csv

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response


router = APIRouter(prefix="/api/account", tags=["account"])
bot_router = APIRouter(prefix="/api/bot", tags=["bot"])


# ============================================================
# ACCOUNT TEST STATE
# ============================================================

_ACCOUNT = {
    # ---------- DEMO (paper) ----------
    "demo": {
        "seed_inr": 100000.0,
        "seed_usd": 1200.0,
        "balance_inr": 100000.0,
        "balance_usd": 1200.0,
        "today_pnl": 0.0,
        "open_positions": 0,
    },
    # ---------- REAL (broker-backed) ----------
    "real": {
        "balance_inr": 0.0,
        "balance_usd": 0.0,
        "today_pnl": 0.0,
        "open_positions": 0,
        "broker_connected": False,
        "broker_provider": None,
        "last_sync": None,
    },
    # ---------- ROUTING ----------
    "mode": "PAPER",          # PAPER | LIVE
    "currency": "INR",
    "usd_inr_rate": 83.33,
    "auto_alloc_pct": 50.0,
    "mission_alloc_pct": 50.0,
}


def _active_side() -> str:
    """Return 'real' if LIVE mode else 'demo'."""
    return "real" if _ACCOUNT["mode"] == "LIVE" else "demo"


def _active_balance() -> float:
    """Return balance for the active mode/currency."""
    side = _active_side()
    cur = _ACCOUNT["currency"]
    key = "balance_inr" if cur == "INR" else "balance_usd"
    return float(_ACCOUNT[side][key])


def _set_active_balance(value: float) -> None:
    side = _active_side()
    cur = _ACCOUNT["currency"]
    key = "balance_inr" if cur == "INR" else "balance_usd"
    _ACCOUNT[side][key] = float(value)


_CSV_DIR = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\robomlm_data\csv")
_CSV_DIR.mkdir(parents=True, exist_ok=True)

_CSV_FILES = [
    "trade_history.csv",
    "decision_lifecycle.csv",
    "position_history.csv",
    "reject_log.csv",
    "eqe_history.csv",
    "mtf_history.csv",
    "tick_snapshot.csv",
    "phase_history.csv",
    "learning_journal.csv",
]


# ============================================================
# ACCOUNT
# ============================================================

def _portfolio_snapshot():
    """Try to read live portfolio + open positions. Never raises."""
    realized = 0.0
    unrealized = 0.0
    open_count = 0
    trades_total = 0
    wins = 0
    losses = 0
    breakeven = 0
    try:
        from app.api.v1.autorobomlm_api import _ensure_state, _state
        _ensure_state()
        port = _state.get("portfolio") if isinstance(_state, dict) else None
        if port is not None:
            s = port.summary()
            realized = float(s.get("realized_pnl") or 0.0)
            trades_total = int(s.get("trades_total") or 0)
            wins = int(s.get("wins") or 0)
            losses = int(s.get("losses") or 0)
            breakeven = int(s.get("breakeven") or 0)
    except Exception:
        pass
    try:
        from app.api.v1.autorobomlm_api import _ensure_state, _state
        _ensure_state()
        loop = _state.get("loop") if isinstance(_state, dict) else None
        if loop is not None:
            acts = loop.active_trades() or []
            open_count = len(acts)
            for p in acts:
                try:
                    unrealized += float(p.get("pnl") or 0.0)
                except Exception:
                    pass
    except Exception:
        pass
    return {
        "realized": realized,
        "unrealized": unrealized,
        "open_count": open_count,
        "trades_total": trades_total,
        "wins": wins,
        "losses": losses,
        "breakeven": breakeven,
    }


@router.get("/summary")
def account_summary():
    side = _active_side()
    sub = _ACCOUNT[side]
    seed = float(_active_balance())
    snap = _portfolio_snapshot()

    # For DEMO: balance = seed + realized_pnl
    # For REAL: keep synced balance untouched
    if side == "demo":
        balance = seed + snap["realized"]
        equity = balance + snap["unrealized"]
    else:
        balance = seed
        equity = balance + snap["unrealized"]

    payload = {
        "ok": True,
        "capital": balance,
        "balance": balance,
        "equity": equity,
        "unrealized_pnl": snap["unrealized"],
        "realized_pnl": snap["realized"],
        "today_pnl": sub.get("today_pnl", 0.0),
        "open_positions": snap["open_count"],
        "mode": _ACCOUNT["mode"],
        "currency": _ACCOUNT["currency"],
        "usd_inr_rate": _ACCOUNT["usd_inr_rate"],
        "trades_total": snap["trades_total"],
        "wins": snap["wins"],
        "losses": snap["losses"],
        "breakeven": snap["breakeven"],
    }

    if side == "demo":
        payload["seed_inr"] = sub["seed_inr"]
        payload["seed_usd"] = sub["seed_usd"]
        payload["account_side"] = "DEMO"
    else:
        payload["account_side"] = "REAL"
        payload["broker_connected"] = sub.get("broker_connected", False)
        payload["broker_provider"] = sub.get("broker_provider")

    return JSONResponse(payload)


@router.get("/equity")
def account_equity():
    points = []

    try:
        path = _CSV_DIR / "trade_history.csv"

        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))

            running = _active_balance()

            for row in rows[-90:]:
                try:
                    running += float(row.get("pnl") or 0)
                    points.append({
                        "t": row.get("timestamp", ""),
                        "v": round(running, 4),
                    })
                except Exception:
                    continue
    except Exception:
        pass

    if not points:
        points = [{
            "t": "",
            "v": _ACCOUNT["capital"],
        }]

    return JSONResponse({
        "ok": True,
        "points": points,
    })


@router.get("/allocation")
def account_allocation():
    return JSONResponse({
        "ok": True,
        "allocation": {
            "crypto": 0,
            "fx": 0,
            "commodity": 0,
            "equity": 0,
            "index": 0,
        },
    })


@router.post("/mode")
async def account_mode(request: Request):
    body = await request.json()
    mode = str(body.get("mode", "PAPER")).upper().strip()

    if mode not in {"PAPER", "LIVE"}:
        return JSONResponse(
            {
                "ok": False,
                "error": "mode must be PAPER or LIVE",
            },
            status_code=400,
        )

    _ACCOUNT["mode"] = mode

    return JSONResponse({
        "ok": True,
        "mode": mode,
    })


@router.post("/currency")
async def account_currency(request: Request):
    body = await request.json()
    currency = str(body.get("currency", "INR")).upper().strip()

    if currency not in {"INR", "USD"}:
        return JSONResponse(
            {
                "ok": False,
                "error": "currency must be INR or USD",
            },
            status_code=400,
        )

    _ACCOUNT["currency"] = currency
    balance = _active_balance()

    return JSONResponse({
        "ok": True,
        "currency": currency,
        "capital": balance,
        "balance": balance,
    })


@router.post("/reset-seed")
def reset_seed():
    """Reset DEMO account to seed. REAL account is untouched."""
    cur = _ACCOUNT["currency"]
    demo = _ACCOUNT["demo"]

    if cur == "INR":
        demo["balance_inr"] = demo["seed_inr"]
    else:
        demo["balance_usd"] = demo["seed_usd"]

    demo["today_pnl"] = 0.0
    demo["open_positions"] = 0

    return JSONResponse({
        "ok": True,
        "capital": _active_balance(),
        "balance": _active_balance(),
    })


@router.get("/download/{filename}")
def account_download(filename: str):
    if filename not in _CSV_FILES:
        return JSONResponse(
            {
                "ok": False,
                "error": "unknown file",
            },
            status_code=404,
        )

    path = _CSV_DIR / filename

    if not path.exists():
        return JSONResponse(
            {
                "ok": False,
                "error": "file missing",
            },
            status_code=404,
        )

    return Response(
        content=path.read_text(encoding="utf-8"),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )




# ============================================================
# REAL ACCOUNT (broker-backed)
# ============================================================

@router.get("/real/status")
def real_status():
    real = _ACCOUNT["real"]
    return JSONResponse({
        "ok": True,
        "real": {
            "balance_inr": real.get("balance_inr", 0.0),
            "balance_usd": real.get("balance_usd", 0.0),
            "today_pnl": real.get("today_pnl", 0.0),
            "open_positions": real.get("open_positions", 0),
            "broker_connected": real.get("broker_connected", False),
            "broker_provider": real.get("broker_provider"),
            "last_sync": real.get("last_sync"),
        },
    })


@router.post("/real/sync")
async def real_sync(request: Request):
    """
    Sync REAL account from external broker.

    Body:
        {
            "provider": "ZERODHA" | "BINANCE" | "IBKR" | ...,
            "balance_inr": float,
            "balance_usd": float,
            "today_pnl": float
        }

    This is a manual/scheduler endpoint. In production, a broker
    adapter will call this automatically after authenticating
    with the broker's API.
    """
    body = await request.json()

    provider = str(body.get("provider") or "").strip().upper()
    if not provider:
        return JSONResponse(
            {"ok": False, "error": "provider is required"},
            status_code=400,
        )

    try:
        balance_inr = float(body.get("balance_inr") or 0.0)
        balance_usd = float(body.get("balance_usd") or 0.0)
        today_pnl = float(body.get("today_pnl") or 0.0)
    except (TypeError, ValueError):
        return JSONResponse(
            {"ok": False, "error": "numeric values required"},
            status_code=400,
        )

    real = _ACCOUNT["real"]
    real["balance_inr"] = balance_inr
    real["balance_usd"] = balance_usd
    real["today_pnl"] = today_pnl
    real["broker_connected"] = True
    real["broker_provider"] = provider
    real["last_sync"] = __import__("datetime").datetime.utcnow().isoformat()

    return JSONResponse({
        "ok": True,
        "real": real,
    })


@router.post("/real/disconnect")
def real_disconnect():
    """Mark REAL broker as disconnected (funds remain visible)."""
    real = _ACCOUNT["real"]
    real["broker_connected"] = False
    real["broker_provider"] = None
    return JSONResponse({"ok": True, "real": real})

# ============================================================
# BOT ALLOCATION
# ============================================================

@bot_router.get("/allocation")
def bot_allocation():
    capital = _active_balance()
    auto_pct = float(_ACCOUNT["auto_alloc_pct"])
    mission_pct = float(_ACCOUNT["mission_alloc_pct"])

    return JSONResponse({
        "ok": True,
        "total_capital": capital,
        "currency": _ACCOUNT["currency"],
        "auto_alloc_pct": auto_pct,
        "mission_alloc_pct": mission_pct,
        "auto_capital": round(capital * auto_pct / 100, 2),
        "mission_capital": round(capital * mission_pct / 100, 2),
        "unallocated_pct": round(100 - auto_pct - mission_pct, 2),
        "unallocated_capital": round(
            capital * (1 - (auto_pct + mission_pct) / 100),
            2,
        ),
    })


@bot_router.post("/allocation")
async def save_bot_allocation(request: Request):
    body = await request.json()

    try:
        auto = float(body.get("auto_alloc_pct", 50))
        mission = float(body.get("mission_alloc_pct", 50))
    except Exception:
        return JSONResponse(
            {
                "ok": False,
                "error": "Allocation values must be numeric.",
            },
            status_code=400,
        )

    if auto < 0 or mission < 0 or auto + mission > 100:
        return JSONResponse(
            {
                "ok": False,
                "error": "Allocation cannot exceed 100%.",
            },
            status_code=400,
        )

    _ACCOUNT["auto_alloc_pct"] = auto
    _ACCOUNT["mission_alloc_pct"] = mission

    return JSONResponse({
        "ok": True,
        "auto_alloc_pct": auto,
        "mission_alloc_pct": mission,
    })