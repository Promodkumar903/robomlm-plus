"""Full state scan — verify everything we built in session"""
import sys, json
from pathlib import Path

ROOT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS")

print("=" * 70)
print("ROBOMLM_PLUS — FULL STATE SCAN")
print("=" * 70)
print()

# -------- 1. FILES CREATED --------
print("[1] NEW FILES CREATED IN SESSION")
print("-" * 70)
files_to_check = [
    "app/intelligence/real/unified_signal.py",
    "app/intelligence/real/real_discovery_bridge.py",
]
for f in files_to_check:
    p = ROOT / f
    if p.exists():
        size = p.stat().st_size
        lines = len(p.read_text(encoding="utf-8").splitlines())
        print(f"  [OK]  {f}  ({lines} lines, {size} bytes)")
    else:
        print(f"  [MISS] {f}")
print()

# -------- 2. FILES PATCHED --------
print("[2] FILES PATCHED IN SESSION")
print("-" * 70)
patches = [
    ("app/intelligence/opportunity/universe_seed.py", "real_discovery_bridge"),
    ("app/autorobomlm/signal_adapter.py", "_make_unified_provider"),
    ("app/intelligence/real/unified_signal.py", "Fallback ATR for SL/TP distance"),
    ("app/intelligence/real/unified_signal.py", "base_grade_score = strength"),
    ("app/intelligence/real/unified_signal.py", "conf_cap = min(100.0, strength * 1.5)"),
    ("app/intelligence/real/real_discovery_bridge.py", "ThreadPoolExecutor"),
    ("app/intelligence/real/real_discovery_bridge.py", "_CACHE"),
]
for path, marker in patches:
    p = ROOT / path
    if not p.exists():
        print(f"  [MISS] {path}")
        continue
    c = p.read_text(encoding="utf-8")
    if marker in c:
        print(f"  [OK]  {path}  ← '{marker[:40]}'")
    else:
        print(f"  [WARN] {path}  ← '{marker[:40]}' NOT FOUND")
print()

# -------- 3. ENGINE IMPORTS --------
print("[3] ENGINE IMPORTS")
print("-" * 70)
sys.path.insert(0, str(ROOT))
engines = [
    "app.intelligence.real.real_market_data",
    "app.intelligence.real.order_flow_engine",
    "app.intelligence.real.obstacle_mapper",
    "app.intelligence.real.derivatives_engine",
    "app.intelligence.real.levels_engine",
    "app.intelligence.real.volume_engine",
    "app.intelligence.real.market_context_engine",
    "app.intelligence.real.advanced_stats_engine",
    "app.intelligence.real.unified_signal",
    "app.intelligence.real.real_discovery_bridge",
    "app.autorobomlm.signal_adapter",
    "app.autorobomlm.auto_loop",
]
for mod in engines:
    try:
        __import__(mod)
        print(f"  [OK]  {mod}")
    except Exception as e:
        print(f"  [FAIL] {mod}  → {e}")
print()

# -------- 4. UNIFIED SIGNAL LIVE TEST --------
print("[4] UNIFIED SIGNAL — LIVE TEST (BTC)")
print("-" * 70)
try:
    from app.intelligence.real.unified_signal import get_unified_signal_engine
    s = get_unified_signal_engine().compute("BTC/USDT")
    print(f"  direction  : {s.direction}")
    print(f"  action     : {s.action}")
    print(f"  strength   : {s.strength}")
    print(f"  confidence : {s.confidence}")
    print(f"  grade      : {s.trade_quality}")
    print(f"  entry      : {s.entry_price}")
    print(f"  stop_loss  : {s.stop_loss}")
    print(f"  take_profit: {s.take_profit}")
    print(f"  risk_reward: {s.risk_reward}")
    print(f"  components : flow={s.flow_score} vol={s.volume_score} deriv={s.derivative_score} obs={s.obstacle_score}")
except Exception as e:
    print(f"  [FAIL] {e}")
print()

# -------- 5. DISCOVERY BRIDGE TEST --------
print("[5] DISCOVERY BRIDGE — LIVE TEST (parallel fetch, 5 symbols)")
print("-" * 70)
try:
    from app.intelligence.real.real_discovery_bridge import (
        get_real_crypto_opportunities, cache_info
    )
    import time
    t = time.time()
    opps = get_real_crypto_opportunities("CRYPTO", 5)
    dt = time.time() - t
    print(f"  fetched {len(opps)} symbols in {dt:.1f}s")
    for o in opps:
        print(f"    {o['symbol']:12} {o['direction']:8} "
              f"str={o['score']:6.2f} grade={o['grade']:5} "
              f"src={o.get('source','')}")
    print(f"  cache: {cache_info()}")
except Exception as e:
    print(f"  [FAIL] {e}")
print()

# -------- 6. SIGNAL ADAPTER (AutoROBOMLM input) --------
print("[6] AUTO-ROBOMLM SIGNAL PROVIDER TEST")
print("-" * 70)
try:
    from app.autorobomlm.signal_adapter import make_live_signal_provider
    p = make_live_signal_provider()
    s = p("BTC/USDT")
    print(f"  direction  : {s.get('direction')}")
    print(f"  action     : {s.get('action')}")
    print(f"  strength   : {s.get('strength')}")
    print(f"  confidence : {s.get('confidence')}")
    print(f"  grade      : {s.get('grade')}")
    print(f"  stop_loss  : {s.get('stop_loss')}")
    print(f"  take_profit: {s.get('take_profit')}")
    print(f"  source     : {s.get('source')}")
except Exception as e:
    print(f"  [FAIL] {e}")
print()

# -------- 7. UNIVERSE SEED WIRING --------
print("[7] UNIVERSE_SEED WIRING CHECK")
print("-" * 70)
try:
    from app.intelligence.opportunity.universe_seed import get_universe_seed
    u = get_universe_seed("CRYPTO")
    if u and u[0].get("source") == "REAL_UNIFIED_SIGNAL":
        print(f"  [OK]  get_universe_seed returns REAL data ({len(u)} items)")
        print(f"        first: {u[0]['symbol']} src={u[0].get('source')}")
    else:
        print(f"  [WARN] get_universe_seed returned static seed")
        if u:
            print(f"         first item source: {u[0].get('source', 'N/A')}")
except Exception as e:
    print(f"  [FAIL] {e}")
print()

# -------- 8. AUTO_LOOP CURRENT STATE --------
print("[8] AUTO_LOOP — CURRENT SL/TP SOURCE")
print("-" * 70)
p = ROOT / "app/autorobomlm/auto_loop.py"
if p.exists():
    c = p.read_text(encoding="utf-8")
    if "_extract_signal_sl_tp" in c:
        print("  [OK]  Signal SL/TP extraction is ACTIVE")
    else:
        print("  [OLD] Still using ATR-based SL/TP (calculate_sl_tp only)")
    if "sl_tp_result.stop_loss" in c and "_sig_sl" not in c:
        print("  [OLD] open_position still uses sl_tp_result")
    if "signal.stop_loss" in c or "signal.get('stop_loss')" in c:
        print("  [OK]  Signal stop_loss referenced")
print()

# -------- 9. CONFIG STATE --------
print("[9] CONFIG STATE")
print("-" * 70)
try:
    from app.autorobomlm.config import AutoRobomlmConfig
    cfg = AutoRobomlmConfig()
    print(f"  min_grade            : {cfg.min_grade.value}")
    print(f"  max_open_positions   : {cfg.max_open_positions}")
    print(f"  sl_atr_multiplier    : {cfg.sl_atr_multiplier}")
    print(f"  tp_atr_multiplier    : {cfg.tp_atr_multiplier}")
    print(f"  loop_interval_sec    : {cfg.loop_interval_sec}")
except Exception as e:
    print(f"  [FAIL] {e}")
print()

print("=" * 70)
print("SCAN COMPLETE")
print("=" * 70)