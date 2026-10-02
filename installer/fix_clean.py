"""Clean DirectionBadge: replace everything between DirectionBadge and MetricCard"""
from pathlib import Path
import shutil
from datetime import datetime

TSX = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\autorobomlm\index.tsx")

content = TSX.read_text(encoding="utf-8")
lines = content.split("\n")

backup = TSX.with_suffix(f".tsx.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(TSX, backup)
print(f"BACKUP: {backup}")

# Find DirectionBadge start
start = None
for i, line in enumerate(lines):
    if line.strip().startswith("function DirectionBadge("):
        start = i
        break

# Find MetricCard start
end = None
for i, line in enumerate(lines):
    if line.strip().startswith("function MetricCard("):
        end = i
        break

if start is None or end is None:
    print(f"ERROR: start={start}, end={end}")
    raise SystemExit(1)

if end <= start:
    print(f"ERROR: MetricCard ({end}) is before DirectionBadge ({start})")
    raise SystemExit(1)

print(f"Replacing lines {start+1} to {end} ({end-start} lines)")

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

# Remove any double blank lines created
new_content = "\n".join(new_lines)
TSX.write_text(new_content, encoding="utf-8")

print(f"FIXED: DirectionBadge cleanly replaced")
print(f"  Replaced: {end - start} lines with 23 lines")
print()
print("Next:")
print("  cd C:\\Users\\Administrator\\ROBOMLM_PLUS\\frontend")
print("  npx tsc --noEmit")