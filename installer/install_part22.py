"""Register account_routes + bot_router in main.py"""
from pathlib import Path
import shutil
import re
from datetime import datetime

MAIN = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\main.py")

if not MAIN.exists():
    print(f"ERROR: {MAIN} not found")
    raise SystemExit(1)

content = MAIN.read_text(encoding="utf-8")
backup = MAIN.with_suffix(f".py.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(MAIN, backup)
print(f"BACKUP: {backup}")

applied = []
skipped = []

# ---- 1. Add import for account_routes ----
if "from app.api.account_routes import" in content:
    skipped.append("1: account_routes import already exists")
else:
    # Insert after the autorobomlm import
    marker = "from app.api.v1.autorobomlm_api import router as autorobomlm_router"
    if marker in content:
        new_line = (
            marker
            + "\nfrom app.api.account_routes import (\n"
            + "    router as account_router,\n"
            + "    bot_router as bot_router,\n"
            + ")"
        )
        content = content.replace(marker, new_line, 1)
        applied.append("1: account_routes import added")
    else:
        skipped.append("1: autorobomlm import marker not found")

# ---- 2. Add include_router calls ----
if "app.include_router(account_router)" in content:
    skipped.append("2: account_router already included")
else:
    marker = "app.include_router(autorobomlm_router)"
    if marker in content:
        new_line = (
            marker
            + "\napp.include_router(account_router)"
            + "\napp.include_router(bot_router)"
        )
        content = content.replace(marker, new_line, 1)
        applied.append("2: include_router calls added")
    else:
        skipped.append("2: include marker not found")

MAIN.write_text(content, encoding="utf-8")

print()
print("APPLIED:")
for a in applied:
    print(f"  + {a}")
print("SKIPPED:")
for s in skipped:
    print(f"  - {s}")
print()
print(f"UPDATED: {MAIN}")
print()
print("Next:")
print("  1. Backend will auto-reload (--reload is on)")
print("  2. Test:")
print("     curl http://127.0.0.1:8000/api/account/summary")
print("     curl http://127.0.0.1:8000/api/bot/allocation")