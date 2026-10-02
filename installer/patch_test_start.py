# patch_test_start.py
# 1. DEEPSEEK v1.2 (grade check fix + relax confluence)
# 2. Watchlist expand (10 symbols)
# Backup PEHLE har file ka.

import os, sys, shutil
from datetime import datetime

ROOT = r"C:\Users\Administrator\ROBOMLM_PLUS"
DEEP = os.path.join(ROOT, "app", "strategies", "deepseek_strategy", "strategy.py")
API  = os.path.join(ROOT, "app", "api", "v1", "autorobomlm_api.py")


def backup(path):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = path + f".bak_{ts}"
    shutil.copy2(path, bak)
    if not os.path.isfile(bak):
        return None
    print(f"BACKUP OK: {os.path.basename(bak)}")
    return bak


# ============================================================
# 1. DEEPSEEK v1.2
# ============================================================

DEEP_OLD1 = '''        # 2. Trade quality
        if data.trade_quality not in self.ALLOWED_GRADES:
            return self._reject(f"GRADE_{data.trade_quality or 'UNKNOWN'}")

'''

DEEP_NEW1 = '''        # 2. Trade quality — trust pipeline. Only block if
        #    trade_quality is HOLD AND strength is also low.
        if (data.trade_quality == "HOLD") and (data.strength < 40.0):
            return self._reject("GRADE_HOLD_LOW_STRENGTH")

'''

DEEP_OLD2 = '''    MIN_CONTEXT = 35.0
    MIN_CONFLUENCE = 3              # out of 6 components'''

DEEP_NEW2 = '''    MIN_CONTEXT = 30.0
    MIN_CONFLUENCE = 2              # out of 6 components
    CONFLUENCE_COMPONENT_MIN = 35.0'''

DEEP_OLD3 = '''        aligned = sum(1 for s in scores if s >= 45.0)'''

DEEP_NEW3 = '''        aligned = sum(1 for s in scores if s >= self.CONFLUENCE_COMPONENT_MIN)'''


def patch_deepseek():
    if not os.path.isfile(DEEP):
        print(f"ERROR: {DEEP} not found")
        return False

    with open(DEEP, "r", encoding="utf-8") as f:
        src = f.read()

    if "CONFLUENCE_COMPONENT_MIN" in src:
        print("DEEPSEEK: ALREADY PATCHED v1.2")
        return True

    for old in (DEEP_OLD1, DEEP_OLD2, DEEP_OLD3):
        if old not in src:
            print(f"DEEPSEEK: anchor not found: {old[:60]!r}")
            return False

    if not backup(DEEP):
        print("DEEPSEEK: backup failed")
        return False

    src = src.replace(DEEP_OLD1, DEEP_NEW1, 1)
    src = src.replace(DEEP_OLD2, DEEP_NEW2, 1)
    src = src.replace(DEEP_OLD3, DEEP_NEW3, 1)

    with open(DEEP, "w", encoding="utf-8") as f:
        f.write(src)
    print("PATCHED: deepseek_strategy/strategy.py")
    return True


# ============================================================
# 2. Watchlist expand
# ============================================================

API_OLD = '''    config = AutoRobomlmConfig(
        min_grade=GradeBand.B,
        execution_mode=ExecutionMode.DEMO,
        watchlist_source=WatchlistSource.MANUAL,
        manual_watchlist=("BTC/USDT",),'''

API_NEW = '''    config = AutoRobomlmConfig(
        min_grade=GradeBand.B,
        execution_mode=ExecutionMode.DEMO,
        watchlist_source=WatchlistSource.MANUAL,
        manual_watchlist=(
            "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT",
            "XRP/USDT", "ADA/USDT", "DOGE/USDT", "DOT/USDT",
            "LINK/USDT", "MATIC/USDT",
        ),'''


def patch_watchlist():
    if not os.path.isfile(API):
        print(f"ERROR: {API} not found")
        return False

    with open(API, "r", encoding="utf-8") as f:
        src = f.read()

    if '"MATIC/USDT"' in src:
        print("WATCHLIST: ALREADY EXPANDED")
        return True

    if API_OLD not in src:
        print("WATCHLIST: anchor not found")
        return False

    if not backup(API):
        print("WATCHLIST: backup failed")
        return False

    src = src.replace(API_OLD, API_NEW, 1)

    with open(API, "w", encoding="utf-8") as f:
        f.write(src)
    print("PATCHED: autorobomlm_api.py (watchlist expanded)")
    return True


# ============================================================

def main():
    print("=" * 60)
    print("Test start patcher: DEEPSEEK v1.2 + watchlist expand")
    print("=" * 60)
    a = patch_deepseek()
    b = patch_watchlist()
    print()
    if a and b:
        print("DONE. Server restart karo, phir:")
        print('  curl -X POST http://127.0.0.1:8000/api/autorobomlm/strategy -H "Content-Type: application/json" -d "{\\"strategy_id\\":\\"DEEPSEEK\\"}"')
        print('  curl -X POST http://127.0.0.1:8000/api/autorobomlm/start')
    else:
        print("Some patches failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()