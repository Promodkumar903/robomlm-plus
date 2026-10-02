"""Read strategy_decisions.jsonl and print summary."""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


DEFAULT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\data\strategy_decisions.jsonl")


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
