"""Install signal_recorder.py — accuracy measurement for existing system"""
from pathlib import Path
import shutil
from datetime import datetime

ROOT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\intelligence\real")
TARGET = ROOT / "signal_recorder.py"

if TARGET.exists():
    backup = TARGET.with_suffix(f".py.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    shutil.copy2(TARGET, backup)
    print(f"BACKUP: {backup}")
    print("NOTE: file already exists — installing updated version")
else:
    print(f"NEW FILE: {TARGET}")

FILE = '''"""
ROBOMLM_PLUS - Signal Recorder

Purpose:
    Measure REAL accuracy of the existing unified_signal engine.

Flow:
    1. compute_and_record(symbol)
         -> unified_signal.compute() 
         -> append signal to signals.jsonl

    2. verify_signal(signal_id, symbol, ...)
         -> fetch current price
         -> compare vs entry + SL + TP
         -> append outcome to verifications.jsonl

    3. accuracy_report()
         -> summary of real accuracy %

Storage:
    C:/Users/Administrator/ROBOMLM_PLUS/data/signals.jsonl
    C:/Users/Administrator/ROBOMLM_PLUS/data/verifications.jsonl

No fabrication. Missing data stays None.
"""

from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Optional
import json
import time


DATA_DIR = Path(r"C:\\Users\\Administrator\\ROBOMLM_PLUS\\data")
SIGNAL_LOG = DATA_DIR / "signals.jsonl"
VERIFY_LOG = DATA_DIR / "verifications.jsonl"

_LOCK = RLock()


def _ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _append_jsonl(path: Path, record: dict):
    _ensure_dirs()
    with _LOCK:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\\n")


def _iter_jsonl(path: Path):
    if not path.exists():
        return
    with _LOCK:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue


# ============================================================
# RECORD
# ============================================================

def record_signal(signal) -> str:
    """
    Record a UnifiedSignal. Returns signal_id.
    Uses ONLY what the signal already contains.
    """
    signal_id = (
        f"{signal.symbol.replace('/', '')}_"
        f"{int(time.time() * 1000)}"
    )

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
    }

    _append_jsonl(SIGNAL_LOG, record)
    return signal_id


def compute_and_record(symbol: str) -> Optional[str]:
    """
    Convenience: compute unified_signal for symbol, then record it.
    Returns signal_id or None on failure.
    """
    try:
        from app.intelligence.real.unified_signal import (
            get_unified_signal_engine,
        )
        signal = get_unified_signal_engine().compute(symbol)
        return record_signal(signal)
    except Exception as e:
        print(f"[recorder] compute_and_record failed for {symbol}: {e}")
        return None


# ============================================================
# VERIFY
# ============================================================

def verify_signal(
    signal_id: str,
    symbol: str,
    direction: str,
    entry_price: float,
    stop_loss: Optional[float],
    take_profit: Optional[float],
    window_minutes: int = 5,
) -> dict:
    """
    Check the actual price now vs entry.
    Determines SL_HIT / TP_HIT / OPEN / CORRECT / WRONG.
    """
    try:
        from app.intelligence.real.real_market_data import (
            get_real_market_data,
        )
        md = get_real_market_data()
        now_price = md.get_last_price(symbol)
    except Exception:
        now_price = None

    if now_price is None or now_price <= 0:
        result = {
            "signal_id": signal_id,
            "window_minutes": window_minutes,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "outcome": "NO_PRICE",
            "symbol": symbol,
            "direction": direction,
            "entry_price": entry_price,
            "current_price": None,
            "move_pct": None,
        }
        _append_jsonl(VERIFY_LOG, result)
        return result

    move_pct = (
        (now_price - entry_price) / entry_price * 100
        if entry_price > 0 else 0.0
    )

    # Signed move — SELL profits on negative
    if direction == "BEARISH":
        move_signed = -move_pct
    elif direction == "BULLISH":
        move_signed = move_pct
    else:
        move_signed = 0.0

    outcome = "NEUTRAL"

    if stop_loss is not None and take_profit is not None:
        if direction == "BULLISH":
            if now_price <= stop_loss:
                outcome = "SL_HIT"
            elif now_price >= take_profit:
                outcome = "TP_HIT"
            else:
                outcome = "OPEN"
        elif direction == "BEARISH":
            if now_price >= stop_loss:
                outcome = "SL_HIT"
            elif now_price <= take_profit:
                outcome = "TP_HIT"
            else:
                outcome = "OPEN"
    else:
        # No SL/TP — directional only
        if move_signed > 0.05:
            outcome = "CORRECT"
        elif move_signed < -0.05:
            outcome = "WRONG"

    result = {
        "signal_id": signal_id,
        "window_minutes": window_minutes,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "symbol": symbol,
        "direction": direction,
        "entry_price": entry_price,
        "current_price": now_price,
        "move_pct_raw": round(move_pct, 4),
        "move_pct_signed": round(move_signed, 4),
        "outcome": outcome,
    }
    _append_jsonl(VERIFY_LOG, result)
    return result


def verify_latest(window_minutes: int = 5) -> list[dict]:
    """
    Verify the most recent signal for each symbol in the log.
    Handy for quick accuracy checks.
    """
    signals = list(_iter_jsonl(SIGNAL_LOG))

    # Latest per symbol
    latest: dict[str, dict] = {}
    for s in signals:
        sym = s.get("symbol")
        if not sym:
            continue
        latest[sym] = s  # overwrites, keeps last

    results = []
    for sym, s in latest.items():
        r = verify_signal(
            signal_id=s["signal_id"],
            symbol=sym,
            direction=s.get("direction", "NEUTRAL"),
            entry_price=float(s.get("entry_price") or 0.0),
            stop_loss=(
                float(s["stop_loss"]) 
                if s.get("stop_loss") is not None else None
            ),
            take_profit=(
                float(s["take_profit"]) 
                if s.get("take_profit") is not None else None
            ),
            window_minutes=window_minutes,
        )
        results.append(r)
    return results


# ============================================================
# REPORT
# ============================================================

def signal_count() -> int:
    return sum(1 for _ in _iter_jsonl(SIGNAL_LOG))


def verification_count() -> int:
    return sum(1 for _ in _iter_jsonl(VERIFY_LOG))


def accuracy_report() -> dict:
    """
    Real accuracy summary based on logged signals + verifications.
    """
    signals = list(_iter_jsonl(SIGNAL_LOG))
    verifs = list(_iter_jsonl(VERIFY_LOG))

    signal_map = {s["signal_id"]: s for s in signals}

    # Group verifications by signal
    by_signal: dict[str, list] = {}
    for v in verifs:
        by_signal.setdefault(v["signal_id"], []).append(v)

    outcome_counts: dict[str, int] = {}
    by_direction: dict[str, dict] = {}
    by_quality: dict[str, dict] = {}

    for sid, checks in by_signal.items():
        sig = signal_map.get(sid)
        if not sig:
            continue

        # Use longest window per signal
        latest = max(checks, key=lambda c: c["window_minutes"])
        outcome = latest["outcome"]
        outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1

        direction = sig.get("direction", "UNKNOWN")
        by_direction.setdefault(direction, {})
        by_direction[direction][outcome] = (
            by_direction[direction].get(outcome, 0) + 1
        )

        quality = sig.get("trade_quality", "UNKNOWN")
        by_quality.setdefault(quality, {})
        by_quality[quality][outcome] = (
            by_quality[quality].get(outcome, 0) + 1
        )

    # Accuracy % (TP_HIT + CORRECT) / total resolved
    resolved = (
        outcome_counts.get("TP_HIT", 0)
        + outcome_counts.get("SL_HIT", 0)
        + outcome_counts.get("CORRECT", 0)
        + outcome_counts.get("WRONG", 0)
    )
    wins = (
        outcome_counts.get("TP_HIT", 0)
        + outcome_counts.get("CORRECT", 0)
    )

    accuracy_pct = round(wins / resolved * 100, 2) if resolved > 0 else 0.0

    return {
        "total_signals": len(signals),
        "total_verifications": len(verifs),
        "verified_signals": len(by_signal),
        "resolved": resolved,
        "wins": wins,
        "accuracy_pct": accuracy_pct,
        "outcome_counts": outcome_counts,
        "by_direction": by_direction,
        "by_quality": by_quality,
    }


__all__ = [
    "record_signal",
    "compute_and_record",
    "verify_signal",
    "verify_latest",
    "signal_count",
    "verification_count",
    "accuracy_report",
    "SIGNAL_LOG",
    "VERIFY_LOG",
    "DATA_DIR",
]
'''

TARGET.write_text(FILE, encoding="utf-8")
print()
print(f"WROTE: {TARGET}")
print()
print("Test — record 3 signals:")
print('  python -c "from app.intelligence.real.signal_recorder import compute_and_record, signal_count; [compute_and_record(s) for s in [\\"BTC/USDT\\",\\"ETH/USDT\\",\\"SOL/USDT\\"]]; print(\\"signals logged:\\", signal_count())"')