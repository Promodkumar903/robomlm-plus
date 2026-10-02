"""Manually fix DirectionBadge by showing exact content"""
from pathlib import Path
import shutil
from datetime import datetime

TSX = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\autorobomlm\index.tsx")

if not TSX.exists():
    print(f"ERROR: {TSX} not found")
    raise SystemExit(1)

content = TSX.read_text(encoding="utf-8")
lines = content.split("\n")

backup = TSX.with_suffix(f".tsx.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(TSX, backup)
print(f"BACKUP: {backup}")
print()

print("=" * 60)
print("LINES 330-385 (current state):")
print("=" * 60)
for i in range(329, min(385, len(lines))):
    marker = " <<<" if i in (337, 360, 369) else ""
    print(f"{i+1:4}: {lines[i]}{marker}")

print("=" * 60)
print()

# Strategy: replace lines from the FIRST "function DirectionBadge" 
# to the NEXT "function " or "export default" that follows.

# Find first DirectionBadge
start = None
for i, line in enumerate(lines):
    if line.strip().startswith("function DirectionBadge("):
        start = i
        break

if start is None:
    print("ERROR: DirectionBadge not found")
    raise SystemExit(1)

# Find the next top-level function/export after DirectionBadge start
# Skip at least 5 lines to avoid matching inside
end = None
for i in range(start + 5, len(lines)):
    stripped = lines[i].strip()
    if (stripped.startswith("function ")
            or stripped.startswith("export default")
            or stripped.startswith("export function ")
            or stripped.startswith("const ")
            or stripped.startswith("// ---")):
        end = i
        break

if end is None:
    print("ERROR: next function not found")
    raise SystemExit(1)

print(f"DirectionBadge: lines {start+1} to {end} (will be replaced)")
print()
print("Content being replaced:")
for i in range(start, end):
    print(f"  {lines[i]}")

# New DirectionBadge
new_fn = '''function DirectionBadge({ direction }: { direction: string }) {
  const raw = String(direction ?? "").trim().toUpperCase();
  let normalized = raw;
  if (raw === "BUY") normalized = "LONG";
  else if (raw === "SELL") normalized = "SHORT";
  else if (raw === "NEUTRAL" || raw === "") normalized = "NEUTRAL";

  const cls =
    normalized === "LONG"
      ? "auto-direction auto-direction-long"
      : normalized === "SHORT"
        ? "auto-direction auto-direction-short"
        : "auto-direction auto-direction-neutral";

  const label =
    normalized === "LONG"
      ? "UP LONG"
      : normalized === "SHORT"
        ? "DOWN SHORT"
        : "NEUTRAL";

  return <span className={cls}>{label}</span>;
}

'''

new_lines = lines[:start] + new_fn.split("\n") + lines[end:]
new_content = "\n".join(new_lines)

TSX.write_text(new_content, encoding="utf-8")
print()
print(f"FIXED: DirectionBadge replaced")
print(f"  Old: lines {start+1} to {end}")
print(f"  New: 21 lines")
print()
print("Next:")
print("  cd C:\\Users\\Administrator\\ROBOMLM_PLUS\\frontend")
print("  npx tsc --noEmit")
print()
print("If clean, verify with:")
print("  findstr /N \"auto-manual-panel\" C:\\Users\\Administrator\\ROBOMLM_PLUS\\frontend\\autorobomlm\\index.tsx")