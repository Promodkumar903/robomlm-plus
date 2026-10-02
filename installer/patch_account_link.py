# patch_account_link.py
# Links account summary to portfolio realized_pnl + live positions.
# Backup PEHLE. Existing logic chhua nahi (sirf summary() extend karta hai).

import os, sys, shutil
from datetime import datetime

TARGET = r"C:\Users\Administrator\ROBOMLM_PLUS\app\api\account_routes.py"

OLD_SUMMARY = '''@router.get("/summary")
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


NEW_SUMMARY = '''def _portfolio_snapshot():
    """Try to read live portfolio + open positions. Never raises."""
    realized = 0.0
    unrealized = 0.0
    open_count = 0
    trades_total = 0
    wins = 0
    losses = 0
    breakeven = 0
    try:
        from app.api.v1.autorobomlm_api import _state
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
        from app.api.v1.autorobomlm_api import _state
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

    return JSONResponse(payload)'''


def main():
    if not os.path.isfile(TARGET):
        print(f"ERROR: not found: {TARGET}")
        sys.exit(1)

    with open(TARGET, "r", encoding="utf-8") as f:
        src = f.read()

    if "_portfolio_snapshot" in src:
        print("ALREADY PATCHED. Skipping.")
        sys.exit(0)

    if OLD_SUMMARY not in src:
        print("ERROR: account_summary anchor not found.")
        sys.exit(1)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET + f".bak_{ts}"
    shutil.copy2(TARGET, bak)
    if not os.path.isfile(bak):
        print("ERROR: backup not verified. Abort.")
        sys.exit(1)
    print(f"BACKUP OK: {os.path.basename(bak)}")

    new_src = src.replace(OLD_SUMMARY, NEW_SUMMARY, 1)

    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(new_src)

    print(f"PATCHED: {TARGET}")
    print()
    print("Rollback:")
    print(f'  copy /Y "{bak}" "{TARGET}"')


if __name__ == "__main__":
    main()