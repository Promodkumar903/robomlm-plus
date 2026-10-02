"""Recorder upgrade: flip_rate + multi-TF + stability"""
from pathlib import Path
import shutil
from datetime import datetime

ROOT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\intelligence\real")
TARGET = ROOT / "signal_recorder.py"

backup = TARGET.with_suffix(f".py.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(TARGET, backup)
print(f"BACKUP: {backup}")

content = TARGET.read_text(encoding="utf-8")

# ---------- 1. Add helpers before record_signal ----------
if "_direction_flips" in content:
    print("Helpers already present")
else:
    marker = "# ============================================================\n# RECORD (unchanged)"
    helpers = '''# ============================================================
# SIGNAL STABILITY HELPERS
# ============================================================

def _direction_flips(symbol: str, lookback: int = 10) -> int:
    """Count direction changes in last N signals for symbol."""
    signals = list(_iter_jsonl(SIGNAL_LOG))
    dirs = [
        s.get("direction") for s in signals
        if s.get("symbol") == symbol
    ]
    recent = dirs[-lookback:]
    flips = 0
    for i in range(1, len(recent)):
        if recent[i] != recent[i-1]:
            flips += 1
    return flips


def _tf_directions(symbol: str) -> dict:
    """Get direction from 5m / 15m / 1h via existing structure_analyzer."""
    try:
        from app.intelligence.real.real_market_data import (
            get_real_market_data,
        )
        from app.intelligence.real.structure_analyzer import (
            get_structure_analyzer,
        )
        md = get_real_market_data()
        sa = get_structure_analyzer()
        result = {}
        for tf_name, tf_code in (("5m", "5"), ("15m", "15"), ("1h", "60")):
            candles, _ = md.get_candles(symbol, tf_code, 100)
            if candles and len(candles) >= 30:
                r = sa.analyze(symbol, tf_name, candles)
                result[tf_name] = r.direction
        return result
    except Exception:
        return {}


def _stability_label(flips: int, tf_dirs: dict) -> str:
    """
    STABLE      = few flips AND multi-TF aligned
    UNSTABLE    = many flips
    MIXED       = multi-TF disagrees
    DEVELOPING  = in between
    """
    dirs = [
        d for d in tf_dirs.values()
        if d in ("BULLISH", "BEARISH")
    ]
    aligned = len(dirs) >= 2 and len(set(dirs)) == 1

    if flips >= 5:
        return "UNSTABLE"
    if flips <= 2 and aligned:
        return "STABLE"
    if dirs and not aligned:
        return "MIXED"
    return "DEVELOPING"


'''
    if marker in content:
        content = content.replace(marker, helpers + marker, 1)
        print("Helpers added")

# ---------- 2. Patch record_signal to add new fields ----------
old_record = '''    record = {
        "signal_id": signal_id,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "signal_ts": signal.timestamp,
        "symbol": signal.symbol,
        "direction": signal.direction,
        "action": signal.action,
        "confidence": signal.confidence,
        "strength": signal.strength,
        "entry_price": signal.entry_price,
        "stop_loss": signal.stop_loss,
        "take_profit": signal.take_profit,
        "risk_reward": signal.risk_reward,
        "expected_move_pct": signal.expected_move_pct,
        "trade_quality": signal.trade_quality,
        "risk_level": signal.risk_level,
        "components": {
            "flow": signal.flow_score,
            "derivative": signal.derivative_score,
            "volume": signal.volume_score,
            "obstacle": signal.obstacle_score,
            "context": signal.context_score,
            "regime": signal.regime_score,
        },
        "modifiers": (
            signal.audit.get("modifiers", {})
            if signal.audit else {}
        ),
    }'''

new_record = '''    # Stability context (uses existing engines, no new fetch logic)
    try:
        flips = _direction_flips(signal.symbol, lookback=10)
        tf_dirs = _tf_directions(signal.symbol)
        stability = _stability_label(flips, tf_dirs)
    except Exception:
        flips = None
        tf_dirs = {}
        stability = "UNKNOWN"

    record = {
        "signal_id": signal_id,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "signal_ts": signal.timestamp,
        "symbol": signal.symbol,
        "direction": signal.direction,
        "action": signal.action,
        "confidence": signal.confidence,
        "strength": signal.strength,
        "entry_price": signal.entry_price,
        "stop_loss": signal.stop_loss,
        "take_profit": signal.take_profit,
        "risk_reward": signal.risk_reward,
        "expected_move_pct": signal.expected_move_pct,
        "trade_quality": signal.trade_quality,
        "risk_level": signal.risk_level,
        "components": {
            "flow": signal.flow_score,
            "derivative": signal.derivative_score,
            "volume": signal.volume_score,
            "obstacle": signal.obstacle_score,
            "context": signal.context_score,
            "regime": signal.regime_score,
        },
        "modifiers": (
            signal.audit.get("modifiers", {})
            if signal.audit else {}
        ),
        # NEW: stability fields
        "direction_flips_last_10": flips,
        "tf_directions": tf_dirs,
        "stability": stability,
    }'''

if "direction_flips_last_10" in content:
    print("Record patch already applied")
elif old_record in content:
    content = content.replace(old_record, new_record, 1)
    print("Record patch applied")
else:
    print("WARNING: record block not found")

# ---------- 3. Report: add by_stability ----------
old_rep = '''        quality = sig.get("trade_quality", "UNKNOWN")
        by_quality.setdefault(quality, {})
        by_quality[quality][outcome] = (
            by_quality[quality].get(outcome, 0) + 1
        )'''

new_rep = '''        quality = sig.get("trade_quality", "UNKNOWN")
        by_quality.setdefault(quality, {})
        by_quality[quality][outcome] = (
            by_quality[quality].get(outcome, 0) + 1
        )

        stability = sig.get("stability", "UNKNOWN")
        by_stability.setdefault(stability, {})
        by_stability[stability][outcome] = (
            by_stability[stability].get(outcome, 0) + 1
        )'''

if "by_stability" in content:
    print("Report patch already applied")
elif old_rep in content:
    content = content.replace(old_rep, new_rep, 1)
    print("Report patch applied")
else:
    print("WARNING: report block not found")

# ---------- 4. Declare by_stability dict ----------
old_decl = '''    outcome_counts: dict[str, int] = {}
    by_direction: dict[str, dict] = {}
    by_quality: dict[str, dict] = {}'''

new_decl = '''    outcome_counts: dict[str, int] = {}
    by_direction: dict[str, dict] = {}
    by_quality: dict[str, dict] = {}
    by_stability: dict[str, dict] = {}'''

if "by_stability: dict[str, dict] = {}" in content:
    print("Decl already present")
elif old_decl in content:
    content = content.replace(old_decl, new_decl, 1)
    print("Decl added")
else:
    print("WARNING: decl block not found")

# ---------- 5. Add to return dict ----------
old_ret = '''        "outcome_counts": outcome_counts,
        "by_direction": by_direction,
        "by_quality": by_quality,
    }'''

new_ret = '''        "outcome_counts": outcome_counts,
        "by_direction": by_direction,
        "by_quality": by_quality,
        "by_stability": by_stability,
    }'''

if '"by_stability": by_stability,' in content:
    print("Return already has by_stability")
elif old_ret in content:
    content = content.replace(old_ret, new_ret, 1)
    print("Return updated")
else:
    print("WARNING: return block not found")

TARGET.write_text(content, encoding="utf-8")
print()
print(f"UPDATED: {TARGET}")
print()
print("Test:")
print('  python -c "from app.intelligence.real.signal_recorder import compute_and_record, accuracy_report; compute_and_record(\'BTC/USDT\'); import json; print(json.dumps(accuracy_report(), indent=2))"')