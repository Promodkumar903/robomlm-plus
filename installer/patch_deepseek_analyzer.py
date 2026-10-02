# patch_deepseek_analyzer.py
# Adds analyzer.py inside deepseek_strategy folder.
# Koi existing file touch nahi.

import os, sys, shutil
from datetime import datetime

ROOT = r"C:\Users\Administrator\ROBOMLM_PLUS"
DEEP = os.path.join(ROOT, "app", "strategies", "deepseek_strategy")
TARGET = os.path.join(DEEP, "analyzer.py")

ANALYZER = '''"""DeepSeek Strategy — Signal Log Analyzer.

Purpose
-------
Read a JSONL log of UnifiedSignal outputs (from live_signal or
signal_recorder), run DeepSeek strategy on each, and produce a
report of allow/reject decisions with reasons.

Does NOT touch AutoROBOMLM, does NOT place trades.
Standalone analysis tool.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from app.strategies.base import StrategyInput
from app.strategies.deepseek_strategy import DeepSeekStrategy


def _map_signal_to_input(raw: dict) -> StrategyInput | None:
    """Map one raw signal dict to StrategyInput. Returns None if unusable."""
    if not isinstance(raw, dict):
        return None

    symbol = raw.get("symbol")
    if not symbol:
        return None

    # UnifiedSignal.to_dict() shape: {"verdict": {...}, "components": {...}, ...}
    verdict = raw.get("verdict") or {}
    comps = raw.get("components") or {}
    trade = raw.get("trade") or {}
    quality = raw.get("quality") or {}
    risk = raw.get("risk") or {}

    direction = str(verdict.get("direction") or raw.get("direction") or "NEUTRAL").upper()
    if direction == "LONG":
        direction = "BULLISH"
    if direction == "SHORT":
        direction = "BEARISH"

    action = str(verdict.get("action") or raw.get("action") or "HOLD").upper()

    try:
        strength = float(verdict.get("strength", raw.get("strength", 0.0)) or 0.0)
        confidence = float(verdict.get("confidence", raw.get("confidence", 0.0)) or 0.0)
        entry = float(trade.get("entry", raw.get("entry_price", 0.0)) or 0.0)
    except (TypeError, ValueError):
        return None

    def _f(v):
        if v is None:
            return None
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    return StrategyInput(
        symbol=symbol,
        timeframe=str(raw.get("timeframe") or raw.get("tf") or "1m"),
        direction=direction,
        action=action,
        strength=strength,
        confidence=confidence,
        trade_quality=str(quality.get("grade") or raw.get("trade_quality") or "HOLD"),
        risk_level=str(risk.get("level") or raw.get("risk_level") or "LOW"),
        entry_price=entry,
        stop_loss=_f(trade.get("stop_loss") if trade else raw.get("stop_loss")),
        take_profit=_f(trade.get("take_profit") if trade else raw.get("take_profit")),
        risk_reward=_f(trade.get("risk_reward") if trade else raw.get("risk_reward")),
        expected_move_pct=_f(trade.get("expected_move_pct") if trade else raw.get("expected_move_pct")) or 0.0,
        components={
            "flow": _f(comps.get("flow")) or 0.0,
            "derivative": _f(comps.get("derivative")) or 0.0,
            "volume": _f(comps.get("volume")) or 0.0,
            "obstacle": _f(comps.get("obstacle")) or 0.0,
            "context": _f(comps.get("context")) or 0.0,
            "regime": _f(comps.get("regime")) or 0.0,
        },
        warnings=tuple(raw.get("warnings") or ()),
        metadata=raw.get("metadata") or {},
    )


def analyze(log_path: str) -> dict[str, Any]:
    """Read JSONL log, run strategy, produce metrics."""
    p = Path(log_path)
    if not p.is_file():
        return {"error": f"file not found: {log_path}"}

    strategy = DeepSeekStrategy()

    total = 0
    skipped = 0
    allowed = 0
    rejected = 0
    reason_counter: Counter = Counter()
    symbol_counter: Counter = Counter()
    direction_counter: Counter = Counter()
    scores: list[float] = []

    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError:
                skipped += 1
                continue

            inp = _map_signal_to_input(raw)
            if inp is None:
                skipped += 1
                continue

            total += 1
            symbol_counter[inp.symbol] += 1
            direction_counter[inp.direction] += 1

            out = strategy.decide(inp)

            if out.entry_permission:
                allowed += 1
                scores.append(out.strategy_score)
            else:
                rejected += 1
                for r in out.reason_codes:
                    reason_counter[r.split("_")[0] if "_" in r else r] += 1

    return {
        "file": str(p),
        "total_signals": total,
        "skipped": skipped,
        "allowed": allowed,
        "rejected": rejected,
        "allow_rate_pct": round(allowed / total * 100, 2) if total else 0.0,
        "avg_score_allowed": round(sum(scores) / len(scores), 2) if scores else 0.0,
        "top_reject_reasons": reason_counter.most_common(10),
        "by_symbol": symbol_counter.most_common(10),
        "by_direction": direction_counter.most_common(5),
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m app.strategies.deepseek_strategy.analyzer <log.jsonl>")
        sys.exit(1)

    result = analyze(sys.argv[1])

    print("=" * 60)
    print("DeepSeek Strategy — Signal Log Analysis")
    print("=" * 60)
    for k, v in result.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
'''


def main():
    os.makedirs(DEEP, exist_ok=True)

    # Existing file? -> backup
    if os.path.isfile(TARGET):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        bak = TARGET + f".bak_{ts}"
        shutil.copy2(TARGET, bak)
        print(f"BACKUP OK: {os.path.basename(bak)}")

    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(ANALYZER)

    print(f"CREATED/PATCHED: {TARGET}")
    print()
    print("Usage:")
    print("  python -m app.strategies.deepseek_strategy.analyzer data\\signals.jsonl")


if __name__ == "__main__":
    main()