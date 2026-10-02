# patch_comparison.py
# Adds strategy decision logging + metrics.
# - New files: comparison.py, metrics.py (no backup needed)
# - Existing: auto_loop.py (backup first)
# Rule: kuch delete nahi. Backup pehle.

import os, sys, shutil
from datetime import datetime

ROOT = r"C:\Users\Administrator\ROBOMLM_PLUS"
STRAT = os.path.join(ROOT, "app", "strategies")
LOOP_PY = os.path.join(ROOT, "app", "autorobomlm", "auto_loop.py")


COMPARISON_PY = '''"""Strategy comparison logger.

Appends one record per strategy decision to data/strategy_decisions.jsonl.
Never raises — logging failures must not break the trading loop.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

LOG_DIR = Path(r"C:\\Users\\Administrator\\ROBOMLM_PLUS\\data")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "strategy_decisions.jsonl"


def log_strategy_decision(
    *,
    symbol: str,
    signal: Mapping[str, Any],
    allowed: bool,
    reason: str,
    strategy_id: str,
) -> None:
    """Append one decision record. Never raises."""
    try:
        rec = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "strategy_id": str(strategy_id or "UNKNOWN"),
            "symbol": symbol,
            "allowed": bool(allowed),
            "reason": str(reason or ""),
            "direction": signal.get("direction"),
            "action": signal.get("action"),
            "strength": signal.get("strength") or signal.get("decision_score"),
            "confidence": signal.get("confidence"),
            "trade_quality": signal.get("trade_quality") or signal.get("grade"),
            "risk_level": signal.get("risk_level"),
        }
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, default=str) + "\\n")
    except Exception:
        # Never break the loop for logging.
        pass
'''


METRICS_PY = '''"""Read strategy_decisions.jsonl and print summary."""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


DEFAULT = Path(r"C:\\Users\\Administrator\\ROBOMLM_PLUS\\data\\strategy_decisions.jsonl")


def summarize(path: Path) -> dict:
    if not path.is_file():
        return {"error": f"file not found: {path}"}

    total = 0
    by_strategy = Counter()
    allowed_by_strategy = Counter()
    rejected_by_strategy = Counter()
    reject_reasons = defaultdict(Counter)
    by_symbol = Counter()

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue

            total += 1
            sid = rec.get("strategy_id", "UNKNOWN")
            sym = rec.get("symbol", "?")
            allowed = bool(rec.get("allowed"))
            reason = rec.get("reason", "")

            by_strategy[sid] += 1
            by_symbol[sym] += 1

            if allowed:
                allowed_by_strategy[sid] += 1
            else:
                rejected_by_strategy[sid] += 1
                # classify reason prefix
                prefix = reason.split(":")[0] if reason else "unknown"
                reject_reasons[sid][prefix] += 1

    out = {
        "file": str(path),
        "total_records": total,
        "by_strategy": dict(by_strategy),
        "by_symbol": dict(by_symbol.most_common(20)),
        "per_strategy": {},
    }

    for sid in by_strategy:
        tot = by_strategy[sid]
        ok = allowed_by_strategy[sid]
        rej = rejected_by_strategy[sid]
        out["per_strategy"][sid] = {
            "total": tot,
            "allowed": ok,
            "rejected": rej,
            "allow_rate_pct": round(ok / tot * 100, 2) if tot else 0.0,
            "top_reject_reasons": reject_reasons[sid].most_common(10),
        }

    return out


def main():
    p = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    result = summarize(p)

    print("=" * 60)
    print("Strategy Decision Metrics")
    print("=" * 60)
    if "error" in result:
        print(result["error"])
        sys.exit(1)

    print(f"  file            : {result['file']}")
    print(f"  total_records   : {result['total_records']}")
    print()
    for sid, stats in result["per_strategy"].items():
        print(f"  [{sid}]")
        print(f"    total         : {stats['total']}")
        print(f"    allowed       : {stats['allowed']}")
        print(f"    rejected      : {stats['rejected']}")
        print(f"    allow_rate_%  : {stats['allow_rate_pct']}")
        if stats["top_reject_reasons"]:
            print(f"    top_rejections: {stats['top_reject_reasons']}")
        print()
    print(f"  top symbols      : {result['by_symbol']}")


if __name__ == "__main__":
    main()
'''


# ------------------------------------------------------------
# auto_loop.py patch: add logging call inside _apply_strategy
# ------------------------------------------------------------

OLD_BLOCK = '''        if not out.entry_permission:
            reasons = ",".join(out.reason_codes) if out.reason_codes else "unknown"
            return False, f"strategy_reject:{reasons}"

        return True, f"strategy_pass:{out.strategy_score}"'''

NEW_BLOCK = '''        if not out.entry_permission:
            reasons = ",".join(out.reason_codes) if out.reason_codes else "unknown"
            reason_text = f"strategy_reject:{reasons}"
            try:
                from app.strategies.comparison import log_strategy_decision
                log_strategy_decision(
                    symbol=symbol,
                    signal=signal,
                    allowed=False,
                    reason=reason_text,
                    strategy_id=sid,
                )
            except Exception:
                pass
            return False, reason_text

        reason_text = f"strategy_pass:{out.strategy_score}"
        try:
            from app.strategies.comparison import log_strategy_decision
            log_strategy_decision(
                symbol=symbol,
                signal=signal,
                allowed=True,
                reason=reason_text,
                strategy_id=sid,
            )
        except Exception:
            pass
        return True, reason_text'''

# Also log OLD path
OLD_OLD = '''        if sid == "OLD":
            return True, "strategy_OLD_allow"'''

NEW_OLD = '''        if sid == "OLD":
            try:
                from app.strategies.comparison import log_strategy_decision
                log_strategy_decision(
                    symbol=symbol,
                    signal=signal,
                    allowed=True,
                    reason="strategy_OLD_allow",
                    strategy_id="OLD",
                )
            except Exception:
                pass
            return True, "strategy_OLD_allow"'''


def backup(path):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = path + f".bak_{ts}"
    shutil.copy2(path, bak)
    if not os.path.isfile(bak):
        return None
    print(f"BACKUP OK: {os.path.basename(bak)}")
    return bak


def write_new(path, content, label):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"CREATED: {label}")


def patch_loop():
    if not os.path.isfile(LOOP_PY):
        print(f"ERROR: {LOOP_PY} not found")
        return False

    with open(LOOP_PY, "r", encoding="utf-8") as f:
        src = f.read()

    if "log_strategy_decision" in src:
        print("auto_loop.py: ALREADY PATCHED")
        return True

    if OLD_BLOCK not in src:
        print("auto_loop.py: strategy_reject anchor not found")
        return False
    if OLD_OLD not in src:
        print("auto_loop.py: OLD anchor not found")
        return False

    src = src.replace(OLD_BLOCK, NEW_BLOCK, 1)
    src = src.replace(OLD_OLD, NEW_OLD, 1)

    if not backup(LOOP_PY):
        print("auto_loop.py: backup failed. Abort.")
        return False

    with open(LOOP_PY, "w", encoding="utf-8") as f:
        f.write(src)
    print("PATCHED: auto_loop.py")
    return True


def main():
    print("=" * 60)
    print("Comparison framework patcher")
    print("=" * 60)

    # New files
    write_new(os.path.join(STRAT, "comparison.py"), COMPARISON_PY, "strategies/comparison.py")
    write_new(os.path.join(STRAT, "metrics.py"), METRICS_PY, "strategies/metrics.py")

    # Patch auto_loop
    ok = patch_loop()

    print()
    if ok:
        print("DONE.")
        print()
        print("Server restart karo (uvicorn Ctrl+C, phir dobara).")
        print("Phir kuch ticks chalao:")
        print('  curl -X POST http://127.0.0.1:8000/api/autorobomlm/tick')
        print()
        print("Summary dekhne ke liye:")
        print("  python -m app.strategies.metrics")
    else:
        print("Patch failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()