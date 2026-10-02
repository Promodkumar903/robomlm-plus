"""Restore the autorobomlm page folder, but delete the stub .ts file"""
from pathlib import Path
import shutil

FRONTEND = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend")
BAK = FRONTEND / "autorobomlm_bak_20260923_233338"
TARGET = FRONTEND / "autorobomlm"

if not BAK.exists():
    print(f"ERROR: backup folder not found: {BAK}")
    raise SystemExit(1)

if TARGET.exists():
    print(f"TARGET already exists: {TARGET}")
    print("Nothing to do.")
    raise SystemExit(0)

# Rename back
shutil.move(str(BAK), str(TARGET))
print(f"RESTORED: {TARGET}")

# Now delete the stub file(s) that were causing TS errors
stub_candidates = list(TARGET.glob("autorobomlm.ts*"))
for f in stub_candidates:
    # Skip backups of the CSS/TSX just in case
    if f.name.endswith(".css.bak") or f.name.endswith(".tsx.bak"):
        continue
    print(f"DELETING stub: {f.name}")
    f.unlink()

print()
print("Contents of restored folder:")
for f in sorted(TARGET.iterdir()):
    if f.is_file():
        print(f"  {f.name} ({f.stat().st_size} bytes)")
    else:
        print(f"  [DIR] {f.name}")

print()
print("Now run:")
print("  cd C:\\Users\\Administrator\\ROBOMLM_PLUS\\frontend")
print("  npx tsc --noEmit")