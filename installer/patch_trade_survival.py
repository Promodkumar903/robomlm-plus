# patch_trade_survival.py
# 1. Config: SL/TP wider (2.0/4.0 ATR) - trade gets room
# 2. auto_loop: min hold 5 min + flip strength filter
# Backup PEHLE. Kuch delete nahi.

import os, sys, shutil
from datetime import datetime

ROOT = r"C:\Users\Administrator\ROBOMLM_PLUS"
CONFIG = os.path.join(ROOT, "app", "autorobomlm", "config.py")
LOOP = os.path.join(ROOT, "app", "autorobomlm", "auto_loop.py")


def backup(path):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = path + f".bak_{ts}"
    shutil.copy2(path, bak)
    if not os.path.isfile(bak):
        return None
    print(f"BACKUP OK: {os.path.basename(bak)}")
    return bak


# ---------- CONFIG ----------
CFG_OLD = '''    sl_atr_multiplier: float = 1.5
    tp_atr_multiplier: float = 3.0'''
CFG_NEW = '''    sl_atr_multiplier: float = 2.0
    tp_atr_multiplier: float = 4.0'''


# ---------- LOOP ----------
LOOP_OLD = '''        if signal_side != position.direction.value:
            self._close(position.position_id, "D13_FLIP", summary)
            continue'''

LOOP_NEW = '''        if signal_side != position.direction.value:
            # MIN HOLD: don't flip-close young trades (noise filter)
            hold_ok = False
            try:
                from datetime import datetime as _dt, timezone as _tz
                opened_str = str(getattr(position, "opened_at", "") or "")
                if opened_str:
                    opened = _dt.fromisoformat(
                        opened_str.replace("Z", "+00:00")
                    )
                    age_sec = (
                        _dt.now(_tz.utc) - opened
                    ).total_seconds()
                    hold_ok = age_sec >= 300.0  # 5 min minimum
            except Exception:
                hold_ok = True

            if not hold_ok:
                continue

            # STRENGTH filter: only strong reversals close
            try:
                flip_strength = float(
                    signal.get("strength")
                    or signal.get("decision_score")
                    or 0.0
                )
            except (TypeError, ValueError):
                flip_strength = 0.0

            if flip_strength < 55.0:
                continue

            self._close(position.position_id, "D13_FLIP", summary)
            continue'''


def patch_config():
    if not os.path.isfile(CONFIG):
        print(f"ERROR: {CONFIG} not found")
        return False

    with open(CONFIG, "r", encoding="utf-8") as f:
        src = f.read()

    if "sl_atr_multiplier: float = 2.0" in src:
        print("CONFIG: already patched")
        return True

    if CFG_OLD not in src:
        print("CONFIG: anchor not found.")
        for i, line in enumerate(src.splitlines(), 1):
            if "sl_atr_multiplier" in line or "tp_atr_multiplier" in line:
                print(f"  L{i}: {line}")
        return False

    if not backup(CONFIG):
        return False

    src = src.replace(CFG_OLD, CFG_NEW, 1)
    with open(CONFIG, "w", encoding="utf-8") as f:
        f.write(src)
    print("PATCHED: config.py (SL 1.5->2.0, TP 3.0->4.0)")
    return True


def patch_loop():
    if not os.path.isfile(LOOP):
        print(f"ERROR: {LOOP} not found")
        return False

    with open(LOOP, "r", encoding="utf-8") as f:
        src = f.read()

    if "MIN HOLD: don't flip-close young trades" in src:
        print("LOOP: already patched")
        return True

    if LOOP_OLD not in src:
        print("LOOP: anchor not found. Showing D13_FLIP context:")
        idx = src.find("D13_FLIP")
        if idx >= 0:
            print(repr(src[max(0, idx-400):idx+100]))
        return False

    if not backup(LOOP):
        return False

    src = src.replace(LOOP_OLD, LOOP_NEW, 1)
    with open(LOOP, "w", encoding="utf-8") as f:
        f.write(src)
    print("PATCHED: auto_loop.py (min hold 5min + flip strength 55)")
    return True


def main():
    print("=" * 60)
    print("Patch Trade Survival: wider SL/TP + D13_FLIP fix")
    print("=" * 60)
    a = patch_config()
    b = patch_loop()
    print()
    if a and b:
        print("DONE.")
        print()
        print("Next:")
        print("  1. Server restart")
        print("  2. Close all existing positions")
        print("  3. Loop start (fresh test)")
    else:
        print("Some patches failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()