"""Fix - remove/rename conflicting placeholder file"""
from pathlib import Path
import shutil
from datetime import datetime

FRONTEND = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend")

# Candidate conflicting paths
candidates = [
    FRONTEND / "autorobomlm",
    FRONTEND / "src" / "autorobomlm",
]

found_any = False

for folder in candidates:
    if not folder.exists():
        print(f"NOT FOUND: {folder}")
        continue

    found_any = True
    print(f"FOUND: {folder}")

    # Backup the folder by renaming
    backup = folder.with_name(
        folder.name + f"_bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    shutil.move(str(folder), str(backup))
    print(f"  RENAMED TO: {backup}")

if not found_any:
    print()
    print("No conflicting folder found at the checked locations.")
    print("Checking other suspicious locations...")

# Also look for any stray autorobomlm.ts outside src/
for stray in FRONTEND.rglob("autorobomlm.ts"):
    if "src" in stray.parts and "api" in stray.parts:
        # This is our file, skip
        continue
    if ".bak" in stray.name:
        continue
    print(f"STRAY: {stray}")
    backup = stray.with_suffix(
        f".ts.stray_bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    shutil.move(str(stray), str(backup))
    print(f"  RENAMED TO: {backup}")

print()
print("Done. Now run:")
print("  cd C:\\Users\\Administrator\\ROBOMLM_PLUS\\frontend")
print("  npx tsc --noEmit")