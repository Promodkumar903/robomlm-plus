"""
Split _ACCOUNT into DEMO + REAL sub-accounts.
DEMO: paper capital 100k (testing)
REAL: 0 until broker sync
Also add /api/account/real/* endpoints for future broker wiring.
"""
from pathlib import Path
import shutil
from datetime import datetime

ROUTES = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\api\account_routes.py")

if not ROUTES.exists():
    print(f"ERROR: {ROUTES} not found")
    raise SystemExit(1)

content = ROUTES.read_text(encoding="utf-8")
backup = ROUTES.with_suffix(f".py.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(ROUTES, backup)
print(f"BACKUP: {backup}")

applied = []
skipped = []

# ---- 1. Replace _ACCOUNT structure ----
old_state = '''_ACCOUNT = {
    "seed_inr": 100000.0,
    "seed_usd": 1200.0,
    "capital": 100000.0,
    "balance": 100000.0,
    "today_pnl": 0.0,
    "open_positions": 0,
    "mode": "PAPER",
    "currency": "INR",
    "usd_inr_rate": 83.33,
    "auto_alloc_pct": 50.0,
    "mission_alloc_pct": 50.0,
}'''

new_state = '''_ACCOUNT = {
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
    _ACCOUNT[side][key] = float(value)'''

if "def _active_side()" in content:
    skipped.append("1: already split")
elif old_state in content:
    content = content.replace(old_state, new_state, 1)
    applied.append("1: _ACCOUNT split into demo+real")
else:
    skipped.append("1: _ACCOUNT pattern not found")

# ---- 2. Rewrite /summary ----
old_summary = '''@router.get("/summary")
def account_summary():
    return JSONResponse({
        "ok": True,
        "capital": _ACCOUNT["capital"],
        "balance": _ACCOUNT["balance"],
        "today_pnl": _ACCOUNT["today_pnl"],
        "open_positions": _ACCOUNT["open_positions"],
        "mode": _ACCOUNT["mode"],
        "currency": _ACCOUNT["currency"],
        "usd_inr_rate": _ACCOUNT["usd_inr_rate"],
        "seed_inr": _ACCOUNT["seed_inr"],
        "seed_usd": _ACCOUNT["seed_usd"],
    })'''

new_summary = '''@router.get("/summary")
def account_summary():
    side = _active_side()
    sub = _ACCOUNT[side]
    balance = _active_balance()

    payload = {
        "ok": True,
        "capital": balance,
        "balance": balance,
        "today_pnl": sub.get("today_pnl", 0.0),
        "open_positions": sub.get("open_positions", 0),
        "mode": _ACCOUNT["mode"],
        "currency": _ACCOUNT["currency"],
        "usd_inr_rate": _ACCOUNT["usd_inr_rate"],
    }

    if side == "demo":
        payload["seed_inr"] = sub["seed_inr"]
        payload["seed_usd"] = sub["seed_usd"]
        payload["account_side"] = "DEMO"
    else:
        payload["account_side"] = "REAL"
        payload["broker_connected"] = sub.get("broker_connected", False)
        payload["broker_provider"] = sub.get("broker_provider")

    return JSONResponse(payload)'''

if "_active_side()" in content and "account_side" in content:
    skipped.append("2: already rewritten")
elif old_summary in content:
    content = content.replace(old_summary, new_summary, 1)
    applied.append("2: /summary rewritten")
else:
    skipped.append("2: /summary pattern not found")

# ---- 3. Rewrite /currency ----
old_currency = '''@router.post("/currency")
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

    if currency == "INR":
        _ACCOUNT["capital"] = _ACCOUNT["seed_inr"]
        _ACCOUNT["balance"] = _ACCOUNT["seed_inr"]
    else:
        _ACCOUNT["capital"] = _ACCOUNT["seed_usd"]
        _ACCOUNT["balance"] = _ACCOUNT["seed_usd"]

    return JSONResponse({
        "ok": True,
        "currency": currency,
        "capital": _ACCOUNT["capital"],
        "balance": _ACCOUNT["balance"],
    })'''

new_currency = '''@router.post("/currency")
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
    })'''

if "balance = _active_balance()" in content and "currency must be INR or USD" in content and 'if currency == "INR":' not in content:
    skipped.append("3: already rewritten")
elif old_currency in content:
    content = content.replace(old_currency, new_currency, 1)
    applied.append("3: /currency rewritten")
else:
    skipped.append("3: /currency pattern not found")

# ---- 4. Rewrite /reset-seed ----
old_reset = '''@router.post("/reset-seed")
def reset_seed():
    if _ACCOUNT["currency"] == "INR":
        value = _ACCOUNT["seed_inr"]
    else:
        value = _ACCOUNT["seed_usd"]

    _ACCOUNT["capital"] = value
    _ACCOUNT["balance"] = value
    _ACCOUNT["today_pnl"] = 0.0

    return JSONResponse({
        "ok": True,
        "capital": _ACCOUNT["capital"],
        "balance": _ACCOUNT["balance"],
    })'''

new_reset = '''@router.post("/reset-seed")
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
    })'''

if "Reset DEMO account to seed" in content:
    skipped.append("4: already rewritten")
elif old_reset in content:
    content = content.replace(old_reset, new_reset, 1)
    applied.append("4: /reset-seed rewritten")
else:
    skipped.append("4: /reset-seed pattern not found")

# ---- 5. Rewrite /equity capital reference ----
if "running = float(_ACCOUNT[\"capital\"])" in content:
    content = content.replace(
        'running = float(_ACCOUNT["capital"])',
        'running = _active_balance()',
        1,
    )
    applied.append("5: /equity capital ref")

# ---- 6. Fix bot_allocation ----
old_bot = '''@bot_router.get("/allocation")
def bot_allocation():
    capital = float(_ACCOUNT["capital"])
    auto_pct = float(_ACCOUNT["auto_alloc_pct"])
    mission_pct = float(_ACCOUNT["mission_alloc_pct"])'''

new_bot = '''@bot_router.get("/allocation")
def bot_allocation():
    capital = _active_balance()
    auto_pct = float(_ACCOUNT["auto_alloc_pct"])
    mission_pct = float(_ACCOUNT["mission_alloc_pct"])'''

if "capital = _active_balance()" in content and "@bot_router.get" in content:
    skipped.append("6: bot_allocation already fixed")
elif old_bot in content:
    content = content.replace(old_bot, new_bot, 1)
    applied.append("6: bot_allocation uses _active_balance")
else:
    skipped.append("6: bot_allocation pattern not found")

# ---- 7. Add REAL account management endpoints ----
if "/real/sync" in content:
    skipped.append("7: real endpoints already exist")
else:
    real_endpoints = '''

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

'''

    # Insert before BOT ALLOCATION header
    marker = "# ============================================================\n# BOT ALLOCATION"
    if marker in content:
        content = content.replace(marker, real_endpoints + marker, 1)
        applied.append("7: real account endpoints added")
    else:
        skipped.append("7: BOT ALLOCATION marker not found")

# Write
ROUTES.write_text(content, encoding="utf-8")

# ==================================================================
# 8. Patch AutoROBOMLM API to use _active_balance()
# ==================================================================
API = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\api\v1\autorobomlm_api.py")
if API.exists():
    api_content = API.read_text(encoding="utf-8")
    api_backup = API.with_suffix(f".py.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    shutil.copy2(API, api_backup)

    old_helper = '''def _get_balance() -> float:
    """Read balance from existing account state."""
    try:
        return float(_ACCOUNT.get("balance", 0.0))
    except (TypeError, ValueError):
        return 0.0'''

    new_helper = '''def _get_balance() -> float:
    """Read active-mode balance from existing account state."""
    try:
        from app.api.account_routes import _active_balance
        return float(_active_balance())
    except Exception:
        try:
            return float(_ACCOUNT.get("balance", 0.0))
        except (TypeError, ValueError):
            return 0.0'''

    if "from app.api.account_routes import _active_balance" in api_content:
        skipped.append("8: api already uses _active_balance")
    elif old_helper in api_content:
        api_content = api_content.replace(old_helper, new_helper, 1)
        API.write_text(api_content, encoding="utf-8")
        applied.append("8: autorobomlm api uses _active_balance")
    else:
        skipped.append("8: _get_balance pattern not found")

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
print(f"UPDATED: {ROUTES}")
print()
print("Next:")
print("  1. Backend auto-reloads")
print("  2. Test:")
print("     curl http://127.0.0.1:8000/api/account/summary       # DEMO: 100000")
print("     curl -X POST http://127.0.0.1:8000/api/account/mode -H \"Content-Type: application/json\" -d \"{\\\"mode\\\":\\\"LIVE\\\"}\"")
print("     curl http://127.0.0.1:8000/api/account/summary       # REAL: 0")
print("     curl -X POST http://127.0.0.1:8000/api/account/mode -H \"Content-Type: application/json\" -d \"{\\\"mode\\\":\\\"PAPER\\\"}\"")