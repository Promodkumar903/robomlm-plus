# patch_dynamic_watchlist.py
# 1. AutoROBOMLM watchlist = dynamic (universe se top 10)
# 2. DEEPSEEK: remove fake signal.risk_reward check (backend gives 2:1 ATR)
# Backup PEHLE.

import os, sys, shutil
from datetime import datetime

ROOT = r"C:\Users\Administrator\ROBOMLM_PLUS"
API  = os.path.join(ROOT, "app", "api", "v1", "autorobomlm_api.py")
DEEP = os.path.join(ROOT, "app", "strategies", "deepseek_strategy", "strategy.py")


def backup(path):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = path + f".bak_{ts}"
    shutil.copy2(path, bak)
    if not os.path.isfile(bak):
        return None
    print(f"BACKUP OK: {os.path.basename(bak)}")
    return bak


# ============================================================
# 1. Watchlist dynamic
# ============================================================

NEW_PROVIDER = '''

def _dynamic_watchlist() -> list:
    """Fetch top symbols from discovery universe each call."""
    try:
        import urllib.request, json as _json
        url = "http://127.0.0.1:8000/api/discovery/universe"
        with urllib.request.urlopen(url, timeout=10) as r:
            data = _json.loads(r.read().decode("utf-8"))
        insts = data.get("data", {}).get("instruments", []) or []
        ranked = []
        for inst in insts:
            sym = inst.get("symbol")
            meta = inst.get("metadata") or {}
            score = meta.get("score") or 0
            if sym:
                ranked.append((float(score), sym))
        ranked.sort(reverse=True)
        top = [s for _, s in ranked[:15]]
        return top if top else ["BTC/USDT"]
    except Exception:
        return ["BTC/USDT"]


def _build_loop(cfg: AutoRobomlmConfig) -> AutoRobomlmLoop:'''

OLD_PROVIDER_ANCHOR = "def _build_loop(cfg: AutoRobomlmConfig) -> AutoRobomlmLoop:"


def patch_watchlist():
    if not os.path.isfile(API):
        print(f"ERROR: {API} not found")
        return False

    with open(API, "r", encoding="utf-8") as f:
        src = f.read()

    if "_dynamic_watchlist" in src:
        print("WATCHLIST: already patched")
        return True

    if OLD_PROVIDER_ANCHOR not in src:
        print("WATCHLIST: _build_loop anchor not found")
        return False

    if not backup(API):
        return False

    src = src.replace(OLD_PROVIDER_ANCHOR, NEW_PROVIDER, 1)

    # Change the loop construction to use dynamic provider
    old_line = "watchlist_provider=lambda: list(symbols),"
    new_line = "watchlist_provider=_dynamic_watchlist,"
    if old_line in src:
        src = src.replace(old_line, new_line, 1)
    else:
        # try another shape
        old_line2 = "watchlist_provider=lambda: list(symbols)"
        if old_line2 in src:
            src = src.replace(old_line2, "watchlist_provider=_dynamic_watchlist", 1)
        else:
            print("WATCHLIST: watchlist_provider line not found")
            return False

    with open(API, "w", encoding="utf-8") as f:
        f.write(src)
    print("PATCHED: autorobomlm_api.py (dynamic watchlist)")
    return True


# ============================================================
# 2. DEEPSEEK: remove fake RR check
# ============================================================

DEEP_OLD = '''        # 4. Risk-reward gate
        rr = data.risk_reward
        if rr is not None and rr < self.MIN_RR:
            return self._reject(f"RR_LOW_{rr:.2f}")

'''
DEEP_NEW = '''        # 4. Risk-reward gate REMOVED.
        # Reason: signal.risk_reward is calculated by UnifiedSignal
        # but AutoROBOMLM uses ATR-based SL/TP (fixed 2:1). Signal RR
        # is not the actual trade RR. Backend guarantees 2:1.

'''


def patch_deepseek():
    if not os.path.isfile(DEEP):
        print(f"ERROR: {DEEP} not found")
        return False

    with open(DEEP, "r", encoding="utf-8") as f:
        src = f.read()

    if "Risk-reward gate REMOVED" in src:
        print("DEEPSEEK: already patched")
        return True

    if DEEP_OLD not in src:
        print("DEEPSEEK: RR anchor not found")
        return False

    if not backup(DEEP):
        return False

    src = src.replace(DEEP_OLD, DEEP_NEW, 1)

    with open(DEEP, "w", encoding="utf-8") as f:
        f.write(src)
    print("PATCHED: deepseek_strategy/strategy.py (RR check removed)")
    return True


# ============================================================

def main():
    print("=" * 60)
    print("Fix: Dynamic watchlist + remove fake RR filter")
    print("=" * 60)
    a = patch_watchlist()
    b = patch_deepseek()
    print()
    if a and b:
        print("DONE. Server restart karo.")
        print("Phir: strategy switch + loop start")
    else:
        print("Some patches failed")
        sys.exit(1)


if __name__ == "__main__":
    main()