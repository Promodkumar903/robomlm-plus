# patch_portfolio_fix.py
# Adds missing _stats_by_source() function to portfolio_tracker.py.
# Backup PEHLE. Kuch delete nahi.

import os, sys, shutil
from datetime import datetime

TARGET = r"C:\Users\Administrator\ROBOMLM_PLUS\app\autorobomlm\portfolio_tracker.py"

FUNC = '''def _stats_by_source(trades: list) -> dict:
    """Group closed trades by entry_source. Per-source stats."""
    buckets: dict = {}
    for t in trades:
        src = (getattr(t, "entry_source", None) or "UNKNOWN")
        buckets.setdefault(src, []).append(t)

    out = {}
    for src, group in buckets.items():
        total = len(group)
        wins = [t for t in group if t.pnl > 0]
        losses = [t for t in group if t.pnl < 0]
        breakeven = total - len(wins) - len(losses)
        realized = sum(t.pnl for t in group)
        gross_profit = sum(t.pnl for t in wins)
        gross_loss = abs(sum(t.pnl for t in losses))
        profit_factor = (
            gross_profit / gross_loss if gross_loss > 0 else 0.0
        )

        out[src] = {
            "trades_total": total,
            "wins": len(wins),
            "losses": len(losses),
            "breakeven": breakeven,
            "win_rate": (
                round(len(wins) / total * 100.0, 4)
                if total else 0.0
            ),
            "realized_pnl": round(realized, 6),
            "avg_win": (
                round(gross_profit / len(wins), 6)
                if wins else 0.0
            ),
            "avg_loss": (
                round(-gross_loss / len(losses), 6)
                if losses else 0.0
            ),
            "profit_factor": round(profit_factor, 6),
        }
    return out


'''

ANCHOR = "class PortfolioTracker:"


def main():
    if not os.path.isfile(TARGET):
        print(f"ERROR: not found: {TARGET}")
        sys.exit(1)

    with open(TARGET, "r", encoding="utf-8") as f:
        src = f.read()

    if "def _stats_by_source(" in src:
        print("ALREADY PATCHED. Skipping.")
        sys.exit(0)

    if ANCHOR not in src:
        print(f"ERROR: anchor '{ANCHOR}' not found.")
        sys.exit(1)

    # Backup FIRST
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET + f".bak_{ts}"
    shutil.copy2(TARGET, bak)
    if not os.path.isfile(bak):
        print("ERROR: backup not verified. Abort.")
        sys.exit(1)
    print(f"BACKUP OK: {os.path.basename(bak)}")

    # Insert function before class
    new_src = src.replace(ANCHOR, FUNC + ANCHOR, 1)

    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(new_src)

    print(f"PATCHED: {TARGET}")
    print()
    print("Rollback:")
    print(f'  copy /Y "{bak}" "{TARGET}"')


if __name__ == "__main__":
    main()