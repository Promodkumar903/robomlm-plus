# patch_deepseek_debug.py
# Adds debug.py — shows what's actually IN signals.jsonl
# Rule: nayi file, koi backup nahi.

import os
from datetime import datetime

TARGET = r"C:\Users\Administrator\ROBOMLM_PLUS\app\strategies\deepseek_strategy\debug.py"

DEBUG = '''"""DeepSeek — Debug: inspect signals.jsonl contents."""

from __future__ import annotations
import json
import sys
from collections import Counter
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m app.strategies.deepseek_strategy.debug <log.jsonl>")
        sys.exit(1)

    p = Path(sys.argv[1])
    if not p.is_file():
        print(f"Not found: {p}")
        sys.exit(1)

    grades = Counter()
    directions = Counter()
    actions = Counter()
    strengths = []
    confidences = []
    rrs = []

    samples = []

    with p.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError:
                continue

            verdict = raw.get("verdict") or {}
            quality = raw.get("quality") or {}
            trade = raw.get("trade") or {}

            g = quality.get("grade") or raw.get("trade_quality") or "?"
            d = (verdict.get("direction") or raw.get("direction") or "?").upper()
            a = (verdict.get("action") or raw.get("action") or "?").upper()

            grades[g] += 1
            directions[d] += 1
            actions[a] += 1

            try:
                strengths.append(float(verdict.get("strength") or raw.get("strength") or 0))
                confidences.append(float(verdict.get("confidence") or raw.get("confidence") or 0))
            except (TypeError, ValueError):
                pass

            rr = trade.get("risk_reward") or raw.get("risk_reward")
            if rr is not None:
                try:
                    rrs.append(float(rr))
                except (TypeError, ValueError):
                    pass

            if i < 3:
                samples.append(raw)

    print("=" * 60)
    print(f"File: {p}")
    print("=" * 60)
    print()
    print("GRADE DISTRIBUTION:")
    for g, n in grades.most_common():
        print(f"  {g:6s} : {n}")
    print()
    print("DIRECTION DISTRIBUTION:")
    for d, n in directions.most_common():
        print(f"  {d:10s} : {n}")
    print()
    print("ACTION DISTRIBUTION:")
    for a, n in actions.most_common():
        print(f"  {a:6s} : {n}")
    print()
    if strengths:
        print(f"STRENGTH   : min={min(strengths):.1f}  max={max(strengths):.1f}  avg={sum(strengths)/len(strengths):.1f}")
    if confidences:
        print(f"CONFIDENCE : min={min(confidences):.1f}  max={max(confidences):.1f}  avg={sum(confidences)/len(confidences):.1f}")
    if rrs:
        print(f"RR         : min={min(rrs):.2f}  max={max(rrs):.2f}  avg={sum(rrs)/len(rrs):.2f}  (n={len(rrs)})")
    print()
    print("=" * 60)
    print("SAMPLE RECORDS (first 3):")
    print("=" * 60)
    for i, s in enumerate(samples):
        print(f"--- sample {i+1} ---")
        print(json.dumps(s, indent=2)[:1200])
        print()


if __name__ == "__main__":
    main()
'''


def main():
    os.makedirs(os.path.dirname(TARGET), exist_ok=True)
    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(DEBUG)
    print(f"CREATED: {TARGET}")
    print()
    print("Run:")
    print("  python -m app.strategies.deepseek_strategy.debug data\\signals.jsonl")


if __name__ == "__main__":
    main()