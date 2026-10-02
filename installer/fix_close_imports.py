"""Add missing close imports to AutoROBOMLM page"""
from pathlib import Path
import shutil
from datetime import datetime

TSX = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\autorobomlm\index.tsx")

if not TSX.exists():
    print(f"ERROR: {TSX} not found")
    raise SystemExit(1)

content = TSX.read_text(encoding="utf-8")

# If already imported, done
if "closePosition," in content and "closeAllPositions," in content:
    print("Already imported. No change.")
    raise SystemExit(0)

backup = TSX.with_suffix(f".tsx.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(TSX, backup)
print(f"BACKUP: {backup}")

# Find the closing of the autorobomlm import block
marker = '} from "../src/api/autorobomlm";'
idx = content.find(marker)

if idx < 0:
    print("ERROR: import marker not found")
    raise SystemExit(1)

# Check if closePosition is right before the marker
before = content[max(0, idx-200):idx]
if "closePosition," in before:
    print("closePosition already in import block")
    raise SystemExit(0)

# Insert both imports right before the marker
insert = "  closePosition,\n  closeAllPositions,\n"
content = content[:idx] + insert + content[idx:]

TSX.write_text(content, encoding="utf-8")
print(f"UPDATED: {TSX}")
print()
print("Next:")
print("  cd C:\\Users\\Administrator\\ROBOMLM_PLUS\\frontend")
print("  npx tsc --noEmit")