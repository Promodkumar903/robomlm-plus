"""Fix: pending count in accuracy_report"""
from pathlib import Path
import shutil
from datetime import datetime

TARGET = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\intelligence\real\signal_recorder.py")

backup = TARGET.with_suffix(f".py.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(TARGET, backup)
print(f"BACKUP: {backup}")

content = TARGET.read_text(encoding="utf-8")

old = '''    # Accuracy from ACTIONABLE outcomes only
    actionable_outcomes = {
        k: v for k, v in outcome_counts.items()
        if k in ("TP_HIT", "SL_HIT", "CORRECT", "WRONG")
    }
    resolved = sum(actionable_outcomes.values())
    wins = (
        actionable_outcomes.get("TP_HIT", 0)
        + actionable_outcomes.get("CORRECT", 0)
    )
    accuracy_pct = round(wins / resolved * 100, 2) if resolved > 0 else 0.0'''

new = '''    # Accuracy from RESOLVED actionable outcomes only
    # OPEN is excluded from accuracy (still pending)
    resolved_outcomes = {
        k: v for k, v in outcome_counts.items()
        if k in ("TP_HIT", "SL_HIT", "CORRECT", "WRONG")
    }
    resolved = sum(resolved_outcomes.values())
    wins = (
        resolved_outcomes.get("TP_HIT", 0)
        + resolved_outcomes.get("CORRECT", 0)
    )
    losses = (
        resolved_outcomes.get("SL_HIT", 0)
        + resolved_outcomes.get("WRONG", 0)
    )
    pending = outcome_counts.get("OPEN", 0)
    accuracy_pct = round(wins / resolved * 100, 2) if resolved > 0 else 0.0'''

if "resolved_outcomes" in content:
    print("Fix already applied")
    raise SystemExit(0)

if old not in content:
    print("WARNING: marker not found")
    raise SystemExit(1)

content = content.replace(old, new, 1)

# Replace return block to use new vars
old_ret = '''        "resolved": resolved,
        "wins": wins,
        "losses": (
            actionable_outcomes.get("SL_HIT", 0)
            + actionable_outcomes.get("WRONG", 0)
        ),
        "pending": actionable_outcomes.get("OPEN", 0),
        "accuracy_pct": accuracy_pct,'''

new_ret = '''        "resolved": resolved,
        "wins": wins,
        "losses": losses,
        "pending": pending,
        "accuracy_pct": accuracy_pct,'''

if old_ret in content:
    content = content.replace(old_ret, new_ret, 1)
    print("Return block updated")
else:
    print("WARNING: return block not found — fallback")
    content = content.replace(
        'actionable_outcomes.get("SL_HIT", 0)',
        'resolved_outcomes.get("SL_HIT", 0)',
        1,
    )
    content = content.replace(
        'actionable_outcomes.get("WRONG", 0)',
        'resolved_outcomes.get("WRONG", 0)',
        1,
    )
    content = content.replace(
        '"pending": actionable_outcomes.get("OPEN", 0),',
        '"pending": outcome_counts.get("OPEN", 0),',
        1,
    )

TARGET.write_text(content, encoding="utf-8")
print(f"UPDATED: {TARGET}")
print()
print("Test:")
print('  python -c "from app.intelligence.real.signal_recorder import accuracy_report; import json; print(json.dumps(accuracy_report(), indent=2))"')