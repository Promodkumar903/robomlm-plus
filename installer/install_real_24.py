"""Install shadow_trade_recorder.py — Phase 1 X mode complete"""
from pathlib import Path

ROOT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\intelligence\real")
TARGET = ROOT / "shadow_trade_recorder.py"

if TARGET.exists():
    print(f"NOTE: exists — overwriting {TARGET}")
else:
    print(f"NEW FILE: {TARGET}")

FILE = '''"""
ROBOMLM_PLUS - Shadow Trade Recorder

Phase 1 - X mode complete.

Routes:
    A+/A  -> REAL (signal_recorder.py, existing)
    B+/B  -> SHADOW (this file)
    HOLD  -> SHADOW (as OBSERVE)

Tracks MFE / MAE / Realized R for shadow trades.
Does NOT modify signal_recorder.py.
"""

from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Optional
import csv
import json
import time


DATA_DIR = Path(r"C:\\Users\\Administrator\\ROBOMLM_PLUS\\data")
SHADOW_SIGNAL_LOG = DATA_DIR / "shadow_signals.jsonl"
SHADOW_VERIFY_LOG = DATA_DIR / "shadow_verifications.jsonl"
SHADOW_SUMMARY_CSV = DATA_DIR / "shadow_summary.csv"
REAL_VERIFY_LOG = DATA_DIR / "verifications.jsonl"

_LOCK = RLock()
SHADOW_GRADES = {"B+", "B", "HOLD"}
REAL_GRADES = {"A+", "A"}


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


def record_shadow_signal(signal) -> str:
    signal_id = f"SHDW_{signal.symbol.replace('/', '')}_{int(time.time() * 1000)}"
    record = {
        "signal_id": signal_id,
        "mode": "SHADOW",
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
    }
    _append_jsonl(SHADOW_SIGNAL_LOG, record)
    return signal_id


def record_signal_smart(symbol: str) -> dict:
    try:
        from app.intelligence.real.unified_signal import get_unified_signal_engine
        from app.intelligence.real.signal_recorder import record_signal as record_real
    except Exception as e:
        return {"mode": "ERROR", "error": str(e)[:120]}

    try:
        signal = get_unified_signal_engine().compute(symbol)
    except Exception as e:
        return {"mode": "ERROR", "error": str(e)[:120]}

    grade = signal.trade_quality

    if grade in REAL_GRADES:
        sid = record_real(signal)
        return {"mode": "REAL", "signal_id": sid, "grade": grade}
    elif grade in SHADOW_GRADES:
        sid = record_shadow_signal(signal)
        return {"mode": "SHADOW", "signal_id": sid, "grade": grade}
    else:
        return {"mode": "SKIP", "signal_id": None, "grade": grade}


def _load_latest_shadows() -> dict:
    latest = {}
    for rec in _iter_jsonl(SHADOW_SIGNAL_LOG):
        sid = rec.get("signal_id")
        if sid:
            latest[sid] = rec
    return latest


def _load_verifications_by_signal() -> dict:
    by_sig = {}
    for rec in _iter_jsonl(SHADOW_VERIFY_LOG):
        sid = rec.get("signal_id")
        if sid:
            by_sig.setdefault(sid, []).append(rec)
    return by_sig


def verify_shadow(shadow_signal: dict, by_sig_cache: Optional[dict] = None) -> dict:
    signal_id = shadow_signal.get("signal_id")
    symbol = shadow_signal.get("symbol")
    direction = shadow_signal.get("direction")
    entry = float(shadow_signal.get("entry_price") or 0.0)
    sl = shadow_signal.get("stop_loss")
    tp = shadow_signal.get("take_profit")

    try:
        from app.intelligence.real.real_market_data import get_real_market_data
        price = get_real_market_data().get_last_price(symbol)
    except Exception:
        price = None

    if price is None or price <= 0:
        result = {
            "signal_id": signal_id,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "current_price": None,
            "running_max": None,
            "running_min": None,
            "mfe_R": None,
            "mae_R": None,
            "outcome": "NO_PRICE",
        }
        _append_jsonl(SHADOW_VERIFY_LOG, result)
        if by_sig_cache is not None:
            by_sig_cache.setdefault(signal_id, []).append(result)
        return result

    if by_sig_cache is None:
        by_sig_cache = _load_verifications_by_signal()

    prev_list = by_sig_cache.get(signal_id, [])
    prev = prev_list[-1] if prev_list else None
    if prev and prev.get("running_max") is not None:
        running_max = max(prev["running_max"], price)
        running_min = min(prev["running_min"], price)
    else:
        running_max = price
        running_min = price

    mfe_R = None
    mae_R = None
    outcome = "OPEN"

    if sl is not None and tp is not None and entry > 0:
        sl = float(sl)
        tp = float(tp)
        if direction == "BULLISH":
            risk = entry - sl
            if risk > 0:
                mfe_R = (running_max - entry) / risk
                mae_R = (running_min - entry) / risk
            if price >= tp:
                outcome = "TP_HIT"
            elif price <= sl:
                outcome = "SL_HIT"
        elif direction == "BEARISH":
            risk = sl - entry
            if risk > 0:
                mfe_R = (entry - running_min) / risk
                mae_R = (entry - running_max) / risk
            if price <= tp:
                outcome = "TP_HIT"
            elif price >= sl:
                outcome = "SL_HIT"
    else:
        if entry > 0:
            move_pct = (price - entry) / entry * 100
            if direction == "BEARISH":
                move_pct = -move_pct
            if move_pct > 0.05:
                outcome = "CORRECT"
            elif move_pct < -0.05:
                outcome = "WRONG"

    result = {
        "signal_id": signal_id,
        "symbol": symbol,
        "direction": direction,
        "entry_price": entry,
        "stop_loss": sl,
        "take_profit": tp,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "current_price": price,
        "running_max": running_max,
        "running_min": running_min,
        "mfe_R": round(mfe_R, 4) if mfe_R is not None else None,
        "mae_R": round(mae_R, 4) if mae_R is not None else None,
        "outcome": outcome,
    }
    _append_jsonl(SHADOW_VERIFY_LOG, result)
    if by_sig_cache is not None:
        by_sig_cache.setdefault(signal_id, []).append(result)
    return result


def verify_all_shadows() -> list:
    shadows = _load_latest_shadows()
    by_sig = _load_verifications_by_signal()
    results = []
    for sid, sig in shadows.items():
        prev_list = by_sig.get(sid, [])
        if prev_list and prev_list[-1].get("outcome") in ("TP_HIT", "SL_HIT"):
            continue
        try:
            results.append(verify_shadow(sig, by_sig_cache=by_sig))
        except Exception:
            continue
    return results


def _empty_bucket():
    return {
        "count": 0, "resolved": 0, "wins": 0, "losses": 0, "open": 0,
        "realized_R_sum": 0.0, "mfe_sum": 0.0, "mfe_count": 0,
        "mae_sum": 0.0, "mae_count": 0,
    }


def summarize_shadow() -> dict:
    shadows = _load_latest_shadows()
    by_sig = _load_verifications_by_signal()

    by_grade = {}
    total_shadow_profitable = 0

    for sid, sig in shadows.items():
        grade = sig.get("trade_quality", "UNKNOWN")
        bucket = by_grade.setdefault(grade, _empty_bucket())
        bucket["count"] += 1

        checks = by_sig.get(sid, [])
        if not checks:
            bucket["open"] += 1
            continue

        latest = checks[-1]
        mfe_vals = [c["mfe_R"] for c in checks if c.get("mfe_R") is not None]
        mae_vals = [c["mae_R"] for c in checks if c.get("mae_R") is not None]
        best_mfe = max(mfe_vals) if mfe_vals else None
        worst_mae = min(mae_vals) if mae_vals else None

        outcome = latest.get("outcome")
        if outcome in ("TP_HIT", "SL_HIT"):
            bucket["resolved"] += 1
            if outcome == "TP_HIT":
                bucket["wins"] += 1
                bucket["realized_R_sum"] += float(sig.get("risk_reward") or 0.0)
            else:
                bucket["losses"] += 1
                bucket["realized_R_sum"] += -1.0
        else:
            bucket["open"] += 1

        if best_mfe is not None:
            bucket["mfe_sum"] += best_mfe
            bucket["mfe_count"] += 1
            if best_mfe >= 1.0:
                total_shadow_profitable += 1
        if worst_mae is not None:
            bucket["mae_sum"] += worst_mae
            bucket["mae_count"] += 1

    out = {}
    for grade, b in by_grade.items():
        resolved = b["resolved"]
        out[grade] = {
            "count": b["count"],
            "resolved": resolved,
            "wins": b["wins"],
            "losses": b["losses"],
            "open": b["open"],
            "win_rate": round(b["wins"] / resolved * 100, 2) if resolved > 0 else 0.0,
            "avg_R": round(b["realized_R_sum"] / resolved, 4) if resolved > 0 else None,
            "avg_MFE": round(b["mfe_sum"] / b["mfe_count"], 4) if b["mfe_count"] > 0 else None,
            "avg_MAE": round(b["mae_sum"] / b["mae_count"], 4) if b["mae_count"] > 0 else None,
        }

    real_wins = 0
    for rec in _iter_jsonl(REAL_VERIFY_LOG):
        if rec.get("outcome") == "TP_HIT":
            real_wins += 1

    total_profitable = real_wins + total_shadow_profitable
    capture_rate = round(real_wins / total_profitable * 100, 2) if total_profitable > 0 else 0.0

    return {
        "shadow_by_grade": out,
        "total_shadow_profitable_mfe1R": total_shadow_profitable,
        "captured_real_wins": real_wins,
        "capture_rate": capture_rate,
    }


def export_shadow_csv(path: Optional[Path] = None) -> str:
    out_path = path or SHADOW_SUMMARY_CSV
    s = summarize_shadow()
    rows = []
    for grade, b in s.get("shadow_by_grade", {}).items():
        rows.append({
            "grade": grade,
            "count": b["count"],
            "resolved": b["resolved"],
            "wins": b["wins"],
            "losses": b["losses"],
            "open": b["open"],
            "win_rate": b["win_rate"],
            "avg_R": b["avg_R"],
            "avg_MFE": b["avg_MFE"],
            "avg_MAE": b["avg_MAE"],
        })
    _ensure_dirs()
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        if rows:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    return str(out_path)


def shadow_count() -> int:
    return sum(1 for _ in _iter_jsonl(SHADOW_SIGNAL_LOG))


def shadow_verification_count() -> int:
    return sum(1 for _ in _iter_jsonl(SHADOW_VERIFY_LOG))


__all__ = [
    "record_shadow_signal",
    "record_signal_smart",
    "verify_shadow",
    "verify_all_shadows",
    "summarize_shadow",
    "export_shadow_csv",
    "shadow_count",
    "shadow_verification_count",
    "SHADOW_SIGNAL_LOG",
    "SHADOW_VERIFY_LOG",
    "SHADOW_SUMMARY_CSV",
]
'''

TARGET.write_text(FILE, encoding="utf-8")
print(f"WROTE: {TARGET}")
print()
print("Test:")
print('  python -c "from app.intelligence.real.shadow_trade_recorder import record_signal_smart; [print(s, record_signal_smart(s)) for s in [\\"BTC/USDT\\",\\"ETH/USDT\\",\\"SOL/USDT\\"]]"')