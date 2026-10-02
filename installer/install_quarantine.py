"""Quarantine my duplicate files — MOVE (not delete). Restore possible."""
from pathlib import Path
import shutil
from datetime import datetime

ROOT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS")
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
QUAR = ROOT / f"_quarantine_{TS}"

files = [
    # (relative path, is_directory)
    ("app/adapters/massive/massive_bars.py", False),
    ("app/adapters/massive/massive_bars.py.bak_20260924_234455", False),
    ("app/adapters/massive/massive_candle_bridge.py", False),
    ("app/adapters/massive/massive_engine_runner.py", False),
    ("test_massive_all.py", False),
    ("test_massive_both.py", False),
    ("test_massive_markets.py", False),
    ("install_real_24.py", False),
    ("install_real_24b.py", False),
    ("install_real_25.py", False),
    ("install_real_26.py", False),
    ("dry_run_check.py", False),
    # pyc files
    ("app/adapters/massive/__pycache__/massive_bars.cpython-314.pyc", False),
    ("app/adapters/massive/__pycache__/massive_candle_bridge.cpython-314.pyc", False),
    ("app/adapters/massive/__pycache__/massive_engine_runner.cpython-314.pyc", False),
]

print("=" * 70)
print(f"QUARANTINE → {QUAR}")
print("=" * 70)
print()

QUAR.mkdir(parents=True, exist_ok=True)

# Save manifest for restore
manifest = QUAR / "_MANIFEST.txt"
manifest_lines = [
    f"Quarantine created: {TS}",
    f"Source root: {ROOT}",
    "",
    "Files moved here:",
]

moved = 0
not_found = 0
for rel, _ in files:
    src = ROOT / rel
    if not src.exists():
        print(f"  [skip]  {rel}  (not found)")
        not_found += 1
        continue

    dst = QUAR / rel
    dst.parent.mkdir(parents=True, exist_ok=True)

    try:
        shutil.move(str(src), str(dst))
        print(f"  [moved] {rel}")
        manifest_lines.append(f"  {rel}")
        moved += 1
    except Exception as e:
        print(f"  [FAIL]  {rel}  → {e}")

manifest.write_text("\n".join(manifest_lines), encoding="utf-8")

print()
print("=" * 70)
print(f"MOVED:     {moved}")
print(f"NOT FOUND: {not_found}")
print("=" * 70)
print()
print(f"Quarantine folder: {QUAR}")
print(f"Manifest saved:    {manifest}")
print()
print("=" * 70)
print("RESTORE COMMAND (if needed):")
print("=" * 70)
print()
print(f'  python -c "import shutil; from pathlib import Path; Q=Path(r\'{QUAR}\'); R=Path(r\'{ROOT}\'); [shutil.move(str(Q/f), str(R/f)) for f in Q.rglob(\'*\') if f.is_file() and f.name != \'_MANIFEST.txt\']; print(\'restored\')"')
print()
print("Verify:")
print("  dir app\\adapters\\massive\\*.py")