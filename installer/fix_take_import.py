"""Fix: add missing takeOpportunity import"""
from pathlib import Path
import shutil
from datetime import datetime
import re

FILE = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\autorobomlm\index.tsx")

if not FILE.exists():
    print(f"ERROR: {FILE} not found.")
    raise SystemExit(1)

content = FILE.read_text(encoding="utf-8")

if "takeOpportunity," in content:
    print("Already imported. No change.")
    raise SystemExit(0)

backup = FILE.with_suffix(f".tsx.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(FILE, backup)
print(f"BACKUP: {backup}")

# Find the import block from "../src/api/autorobomlm"
# Strategy: find '} from "../src/api/autorobomlm"' and inject before it
marker = '} from "../src/api/autorobomlm";'
idx = content.find(marker)

if idx < 0:
    print("ERROR: import marker not found")
    raise SystemExit(1)

# Insert '  takeOpportunity,\n' right before the marker
insert = "  takeOpportunity,\n"
content = content[:idx] + insert + content[idx:]

FILE.write_text(content, encoding="utf-8")
print(f"UPDATED: {FILE}")
print()
print("Next:")
print("  cd C:\\Users\\Administrator\\ROBOMLM_PLUS\\frontend")
print("  npx tsc --noEmit")