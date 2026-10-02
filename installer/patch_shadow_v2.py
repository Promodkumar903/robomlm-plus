# patch_shadow_v2.py
# Safe patcher: backup banata hai, phir verify_shadow ko replace karta hai.
# Backup fail ho to code change NAHI karta.

import os
import re
import sys
import shutil
from datetime import datetime

TARGET = r"C:\Users\Administrator\ROBOMLM_PLUS\app\intelligence\real\shadow_trade_recorder.py"

NEW_VERIFY = r'''def verify_shadow(sig: dict, by_sig_cache=None) -> dict:
    sid = sig.get("signal_id") or sig.get("id")
    symbol = sig.get("symbol")
    direction = (sig.get("direction") or "BULLISH").upper()
    entry_price = float(sig.get("entry_price") or 0.0)
    stop_loss = sig.get("stop_loss")
    take_profit = sig.get("take_profit")

    # ---- Guard: SL missing => R compute nahi ho sakta ----
    if stop_loss is None:
        rec = {
            "signal_id": sid,
            "symbol": symbol,
            "direction": direction,
            "entry_price": entry_price,
            "stop_loss": None,
            "take_profit": take_profit,
            "checked_at": _utcnow_iso(),
            "current_price": None,
            "running_max": None,
            "running_min": None,
            "mfe_R": None,
            "mae_R": None,
            "outcome": "NO_RISK",
        }
        _append_jsonl(VERIFY_LOG, rec)
        return rec

    stop_loss = float(stop_loss)
    risk = abs(entry_price - stop_loss)
    if risk <= 0:
        return {"signal_id": sid, "outcome": "BAD_RISK"}

    # ---- Current price ----
    current_price = _get_current_price(symbol)
    if current_price is None:
        return {"signal_id": sid, "outcome": "NO_PRICE"}
    current_price = float(current_price)

    # ---- Previous verification (running_max/min carry karne ke liye) ----
    prev = None
    if by_sig_cache is not None:
        lst = by_sig_cache.get(sid, [])
        if lst:
            prev = lst[-1]
    else:
        lst = _load_verifications_for_signal(sid)
        if lst:
            prev = lst[-1]

    # ---- Running max/min: ENTRY se init (current se nahi) ----
    if prev and prev.get("running_max") is not None:
        running_max = max(float(prev["running_max"]), current_price)
    else:
        running_max = max(entry_price, current_price)

    if prev and prev.get("running_min") is not None:
        running_min = min(float(prev["running_min"]), current_price)
    else:
        running_min = min(entry_price, current_price)

    # ---- MFE / MAE in R (direction-aware) ----
    if direction in ("BULLISH", "LONG", "BUY"):
        mfe_R = (running_max - entry_price) / risk
        mae_R = (running_min - entry_price) / risk
    else:  # BEARISH / SHORT
        mfe_R = (entry_price - running_min) / risk
        mae_R = (entry_price - running_max) / risk

    mfe_R = max(0.0, round(mfe_R, 4))   # MFE kabhi negative nahi
    mae_R = min(0.0, round(mae_R, 4))   # MAE kabhi positive nahi

    # ---- Outcome ----
    outcome = "OPEN"
    if direction in ("BULLISH", "LONG", "BUY"):
        if current_price <= stop_loss:
            outcome = "SL_HIT"
        elif take_profit is not None and current_price >= float(take_profit):
            outcome = "TP_HIT"
    else:
        if current_price >= stop_loss:
            outcome = "SL_HIT"
        elif take_profit is not None and current_price <= float(take_profit):
            outcome = "TP_HIT"

    rec = {
        "signal_id": sid,
        "symbol": symbol,
        "direction": direction,
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "checked_at": _utcnow_iso(),
        "current_price": current_price,
        "running_max": running_max,
        "running_min": running_min,
        "mfe_R": mfe_R,
        "mae_R": mae_R,
        "outcome": outcome,
    }
    _append_jsonl(VERIFY_LOG, rec)
    return rec
'''


def find_function_block(src: str, func_name: str):
    """Return (start_idx, end_idx) of a top-level function definition."""
    pattern = re.compile(
        r'^def\s+' + re.escape(func_name) + r'\s*\(.*?\)\s*(?:->.*?)?\s*:\s*$',
        re.MULTILINE,
    )
    m = pattern.search(src)
    if not m:
        return None
    start = m.start()
    # find next top-level def/class/comment-at-col-0 after this
    rest = src[m.end():]
    nxt = re.search(r'^(?=def\s|class\s|@\w)', rest, re.MULTILINE)
    end = m.end() + (nxt.start() if nxt else len(rest))
    return (start, end)


def main():
    if not os.path.isfile(TARGET):
        print(f"ERROR: target file not found: {TARGET}")
        sys.exit(1)

    with open(TARGET, "r", encoding="utf-8") as f:
        src = f.read()

    if "def verify_shadow" not in src:
        print("ERROR: 'def verify_shadow' not found in target. Abort.")
        sys.exit(1)

    # ---- STEP 1: BACKUP (pehle) ----
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = TARGET + f".bak_{ts}"
    try:
        shutil.copy2(TARGET, backup)
    except Exception as e:
        print(f"ERROR: backup failed -> {e}")
        print("Backup ke bina code change NAHI kiya jaayega. Abort.")
        sys.exit(1)

    if not os.path.isfile(backup):
        print("ERROR: backup file verify nahi hui. Abort.")
        sys.exit(1)

    print(f"BACKUP OK: {backup}")

    # ---- STEP 2: Replace verify_shadow ----
    block = find_function_block(src, "verify_shadow")
    if not block:
        print("ERROR: verify_shadow block parse nahi hua. Abort (backup safe hai).")
        sys.exit(1)

    start, end = block
    new_src = src[:start] + NEW_VERIFY + "\n\n" + src[end:]

    if new_src == src:
        print("WARN: koi change nahi hua (already patched?).")
        sys.exit(0)

    # ---- STEP 3: Write ----
    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(new_src)

    print(f"PATCHED: {TARGET}")
    print("verify_shadow replaced. Backup yahan hai:")
    print(f"  {backup}")
    print()
    print("Rollback karna ho to:")
    print(f'  copy /Y "{backup}" "{TARGET}"')


if __name__ == "__main__":
    main()