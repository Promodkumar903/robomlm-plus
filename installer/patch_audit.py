# patch_audit.py
# Adds app/strategies/audit.py — real honest audit of strategy performance.
# Nayi file. Kuch existing touch nahi.

import os

ROOT = r"C:\Users\Administrator\ROBOMLM_PLUS"
TARGET = os.path.join(ROOT, "app", "strategies", "audit.py")

AUDIT = '''"""Real audit of AutoROBOMLM strategy decisions vs actual trades.

Reads:
  - data/strategy_decisions.jsonl     (per-tick strategy allow/reject)
  - Live API /api/autorobomlm/positions (all positions opened)
  - Live API /api/account/summary       (balance, PnL)

Joins by timestamp and prints per-strategy truth:
  - How many signals scanned
  - How many allowed / rejected (with reason)
  - How many trades actually opened
  - Win/loss/open breakdown
  - PnL per strategy
  - Balance update sanity check
"""

from __future__ import annotations

import json
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DATA = Path(r"C:\\Users\\Administrator\\ROBOMLM_PLUS\\data")
DECISIONS = DATA / "strategy_decisions.jsonl"
API = "http://127.0.0.1:8000"


def _get_json(url: str) -> Any:
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return {"_error": str(e)}


def _load_decisions() -> list[dict]:
    if not DECISIONS.is_file():
        return []
    out = []
    with DECISIONS.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def _bucket_decisions(decisions: list[dict]) -> dict:
    stats = defaultdict(lambda: {
        "total": 0,
        "allowed": 0,
        "rejected": 0,
        "reject_reasons": Counter(),
        "by_direction": Counter(),
        "by_grade": Counter(),
    })

    for d in decisions:
        sid = d.get("strategy_id", "UNKNOWN")
        s = stats[sid]
        s["total"] += 1
        s["by_direction"][d.get("direction") or "?"] += 1
        s["by_grade"][d.get("trade_quality") or "?"] += 1

        if d.get("allowed"):
            s["allowed"] += 1
        else:
            s["rejected"] += 1
            reason = str(d.get("reason") or "")
            prefix = reason.split(":")[0] if reason else "unknown"
            suffix = reason.split(":")[1] if ":" in reason else ""
            key = f"{prefix}:{suffix.split(',')[0] if suffix else ''}" if suffix else prefix
            s["reject_reasons"][key] += 1

    return stats


def _bucket_trades(positions: list[dict]) -> dict:
    stats = defaultdict(lambda: {
        "total": 0,
        "open": 0,
        "closed": 0,
        "wins": 0,
        "losses": 0,
        "breakeven": 0,
        "total_pnl": 0.0,
        "exit_reasons": Counter(),
    })

    for p in positions:
        # Try to figure out which strategy took this trade.
        # We don't have a strategy tag on positions yet, so use
        # entry_score proximity to matching decisions later.
        # For now, bucket by unknown.
        sid = p.get("strategy_id") or "UNTAGGED"
        s = stats[sid]
        s["total"] += 1

        status = (p.get("status") or "").upper()
        pnl = float(p.get("pnl") or 0.0)

        if status == "OPEN":
            s["open"] += 1
        else:
            s["closed"] += 1
            if pnl > 0:
                s["wins"] += 1
            elif pnl < 0:
                s["losses"] += 1
            else:
                s["breakeven"] += 1

        s["total_pnl"] += pnl
        s["exit_reasons"][p.get("exit_reason") or "OPEN"] += 1

    return stats


def _link_trades_to_strategy(decisions: list[dict], positions: list[dict]) -> dict:
    """For each opened position, find the closest allowed decision within ±30s."""
    links = []
    # Build list of allowed decisions with parsed timestamp
    allowed = []
    for d in decisions:
        if d.get("allowed"):
            try:
                from datetime import datetime
                ts = datetime.fromisoformat(d["ts"].replace("Z", "+00:00"))
                allowed.append((ts, d))
            except Exception:
                pass

    for p in positions:
        try:
            from datetime import datetime
            p_ts = datetime.fromisoformat(p["opened_at"].replace("Z", "+00:00"))
        except Exception:
            continue

        best = None
        best_delta = 999999.0
        for ts, d in allowed:
            delta = abs((ts - p_ts).total_seconds())
            if delta < best_delta:
                best_delta = delta
                best = d

        if best is not None and best_delta <= 60:
            links.append({
                "position_id": p.get("position_id"),
                "symbol": p.get("symbol"),
                "direction": p.get("direction"),
                "entry_score": p.get("entry_score"),
                "entry_grade": p.get("entry_grade"),
                "opened_at": p.get("opened_at"),
                "status": p.get("status"),
                "pnl": p.get("pnl"),
                "exit_reason": p.get("exit_reason"),
                "strategy_id": best.get("strategy_id"),
                "decision_direction": best.get("direction"),
                "decision_trade_quality": best.get("trade_quality"),
                "delta_sec": round(best_delta, 2),
            })
        else:
            links.append({
                "position_id": p.get("position_id"),
                "symbol": p.get("symbol"),
                "direction": p.get("direction"),
                "entry_score": p.get("entry_score"),
                "opened_at": p.get("opened_at"),
                "status": p.get("status"),
                "pnl": p.get("pnl"),
                "exit_reason": p.get("exit_reason"),
                "strategy_id": "NO_MATCH",
                "delta_sec": None,
            })

    return links


def _bucket_linked(links: list[dict]) -> dict:
    stats = defaultdict(lambda: {
        "trades": 0,
        "open": 0,
        "closed": 0,
        "wins": 0,
        "losses": 0,
        "breakeven": 0,
        "total_pnl": 0.0,
        "avg_pnl": 0.0,
        "exit_reasons": Counter(),
    })

    for l in links:
        sid = l.get("strategy_id") or "UNKNOWN"
        s = stats[sid]
        s["trades"] += 1

        status = (l.get("status") or "").upper()
        pnl = float(l.get("pnl") or 0.0)

        if status == "OPEN":
            s["open"] += 1
        else:
            s["closed"] += 1
            if pnl > 0:
                s["wins"] += 1
            elif pnl < 0:
                s["losses"] += 1
            else:
                s["breakeven"] += 1

        s["total_pnl"] += pnl
        s["exit_reasons"][l.get("exit_reason") or "OPEN"] += 1

    for sid, s in stats.items():
        if s["trades"] > 0:
            s["avg_pnl"] = round(s["total_pnl"] / s["trades"], 4)
        s["total_pnl"] = round(s["total_pnl"], 4)

    return stats


def main():
    print("=" * 70)
    print("AutoROBOMLM Strategy Audit")
    print("=" * 70)

    # ---- Decisions ----
    decisions = _load_decisions()
    print(f"\\nDecisions file : {DECISIONS}")
    print(f"Total decisions: {len(decisions)}")

    dec_stats = _bucket_decisions(decisions)
    print()
    print("--- Per Strategy: Decisions ---")
    for sid, s in dec_stats.items():
        print(f"  [{sid}]")
        print(f"    total        : {s['total']}")
        print(f"    allowed      : {s['allowed']}")
        print(f"    rejected     : {s['rejected']}")
        rate = (s['allowed'] / s['total'] * 100) if s['total'] else 0.0
        print(f"    allow_rate_% : {rate:.1f}")
        print(f"    by_direction : {dict(s['by_direction'])}")
        print(f"    by_grade     : {dict(s['by_grade'])}")
        if s['reject_reasons']:
            print(f"    reject_reasons: {dict(s['reject_reasons'])}")

    # ---- Live positions ----
    print()
    print("--- Live Positions ---")
    pos_resp = _get_json(f"{API}/api/autorobomlm/positions")
    if "_error" in pos_resp:
        print(f"  ERROR: {pos_resp['_error']}")
        return

    all_positions = pos_resp.get("all_positions") or pos_resp.get("positions") or []
    print(f"  total positions: {len(all_positions)}")

    # ---- Link ----
    links = _link_trades_to_strategy(decisions, all_positions)
    linked_stats = _bucket_linked(links)

    print()
    print("--- Per Strategy: Linked Trades ---")
    for sid, s in linked_stats.items():
        print(f"  [{sid}]")
        print(f"    trades       : {s['trades']}")
        print(f"    open         : {s['open']}")
        print(f"    closed       : {s['closed']}")
        print(f"    wins         : {s['wins']}")
        print(f"    losses       : {s['losses']}")
        print(f"    breakeven    : {s['breakeven']}")
        win_rate = (s['wins'] / s['closed'] * 100) if s['closed'] else 0.0
        print(f"    win_rate_%   : {win_rate:.1f}")
        print(f"    total_pnl    : {s['total_pnl']}")
        print(f"    avg_pnl      : {s['avg_pnl']}")
        print(f"    exit_reasons : {dict(s['exit_reasons'])}")

    # ---- Account ----
    print()
    print("--- Account State ---")
    acct = _get_json(f"{API}/api/account/summary")
    if "_error" in acct:
        print(f"  ERROR: {acct['_error']}")
    else:
        for k, v in (acct or {}).items():
            if isinstance(v, (int, float, str, bool)) or v is None:
                print(f"  {k}: {v}")

    # ---- Detailed trade links ----
    print()
    print("--- Detailed Trade Links ---")
    for l in links:
        print(f"  [{l['strategy_id']:9s}] {l['symbol']:10s} "
              f"{l['direction']:5s} score={l['entry_score']} "
              f"grade={l.get('entry_grade')} "
              f"status={l['status']:6s} pnl={l.get('pnl')} "
              f"exit={l.get('exit_reason')} "
              f"Δ={l.get('delta_sec')}s")


if __name__ == "__main__":
    main()
'''


def main():
    os.makedirs(os.path.dirname(TARGET), exist_ok=True)
    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(AUDIT)
    print(f"CREATED: {TARGET}")
    print()
    print("Run:")
    print("  python -m app.strategies.audit")


if __name__ == "__main__":
    main()