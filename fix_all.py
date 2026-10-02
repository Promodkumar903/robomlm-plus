"""Restore index.tsx from good backup + apply DirectionBadge fix correctly"""
from pathlib import Path
import shutil
from datetime import datetime

FRONTEND = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\autorobomlm")
TSX = FRONTEND / "index.tsx"
CSS = FRONTEND / "autorobomlm.css"

print("=" * 60)
print("STEP 1: List backups")
print("=" * 60)

backups = sorted(FRONTEND.glob("index.tsx.bak_*"), reverse=True)
for b in backups:
    size = b.stat().st_size
    print(f"  {b.name} ({size} bytes)")

if not backups:
    print("ERROR: no backups found")
    raise SystemExit(1)

# Pick backup from BEFORE the broken fix (part27 ran at 01:39:21)
target_backup = None
for b in backups:
    if "20260924_013921" in b.name:
        target_backup = b
        break

if target_backup is None:
    # Fallback: pick the second most recent
    target_backup = backups[1] if len(backups) > 1 else backups[0]

print()
print(f"Using: {target_backup.name}")

# Save current broken state
broken_backup = TSX.with_suffix(f".tsx.BROKEN_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(TSX, broken_backup)
print(f"Saved broken: {broken_backup.name}")

# Restore
shutil.copy2(target_backup, TSX)
print(f"RESTORED: {TSX.name}")

# ==================================================================
# STEP 2: Apply DirectionBadge fix (line-based)
# ==================================================================
content = TSX.read_text(encoding="utf-8")
lines = content.split("\n")

# Find "function DirectionBadge"
start_line = None
for i, line in enumerate(lines):
    if line.strip().startswith("function DirectionBadge("):
        start_line = i
        break

if start_line is None:
    print("ERROR: DirectionBadge not found in restored backup")
    raise SystemExit(1)

print()
print(f"DirectionBadge starts at line {start_line + 1}:")
print(f"  {lines[start_line]}")

# Find function end: starting from start_line, count braces properly
# Skip the parameters first — find ")" that closes "function DirectionBadge(...)"
paren_depth = 0
params_end = None
for i in range(start_line, min(start_line + 5, len(lines))):
    line = lines[i]
    for ch in line:
        if ch == "(":
            paren_depth += 1
        elif ch == ")":
            paren_depth -= 1
            if paren_depth == 0:
                params_end = i
                break
    if params_end is not None:
        break

if params_end is None:
    print("ERROR: cannot find parameter close")
    raise SystemExit(1)

# Now find the function body — the next { after params_end
body_start = None
for i in range(params_end, min(params_end + 3, len(lines))):
    if "{" in lines[i]:
        body_start = i
        break

if body_start is None:
    print("ERROR: cannot find function body start")
    raise SystemExit(1)

# Now count braces from body_start to find end
brace_depth = 0
function_end = None
for i in range(body_start, len(lines)):
    line = lines[i]
    # Skip strings/comments roughly (this is fine for our simple code)
    for ch in line:
        if ch == "{":
            brace_depth += 1
        elif ch == "}":
            brace_depth -= 1
            if brace_depth == 0:
                function_end = i
                break
    if function_end is not None:
        break

if function_end is None:
    print("ERROR: cannot find function end")
    raise SystemExit(1)

print(f"DirectionBadge ends at line {function_end + 1}")

# New function replacement
new_function = '''function DirectionBadge({ direction }: { direction: string }) {
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
}'''

# Replace lines from start_line to function_end
new_lines = lines[:start_line] + new_function.split("\n") + lines[function_end + 1:]
new_content = "\n".join(new_lines)

# Save
TSX.write_text(new_content, encoding="utf-8")
print(f"DirectionBadge replaced")

# ==================================================================
# STEP 3: Verify Manual panel CSS exists
# ==================================================================
if CSS.exists():
    css_content = CSS.read_text(encoding="utf-8")
    if ".auto-manual-panel" in css_content:
        print("CSS: manual panel already present")
    else:
        print("CSS: adding manual panel styles...")
        css_add = '''

/* MANUAL TRADE PANEL */
.auto-manual-panel {
  border-color: #334155;
}
.auto-manual-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 8px 0 4px;
}
.auto-manual-input-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.auto-manual-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: #94a3b8;
}
.auto-manual-input {
  width: 100%;
  padding: 10px 14px;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 8px;
  color: #e2e8f0;
  font-size: 14px;
  font-weight: 600;
  outline: none;
}
.auto-manual-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}
.auto-manual-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.auto-manual-btn {
  padding: 14px 20px !important;
  font-size: 15px !important;
  font-weight: 800 !important;
  letter-spacing: 0.5px !important;
  border-radius: 8px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  border: 1px solid transparent !important;
}
.auto-manual-btn-buy {
  background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
  color: #ffffff !important;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
}
.auto-manual-btn-sell {
  background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%) !important;
  color: #ffffff !important;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.25);
}
.auto-manual-btn:disabled {
  opacity: 0.4 !important;
  cursor: not-allowed !important;
}
.auto-manual-hint {
  margin: 8px 0 0;
  font-size: 11px;
  color: #64748b;
  line-height: 1.5;
}

/* DIRECTION BADGES */
.auto-direction {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.5px;
  border: 1px solid transparent;
}
.auto-direction-long {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
  border-color: rgba(52, 211, 153, 0.4);
}
.auto-direction-short {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
  border-color: rgba(248, 113, 113, 0.4);
}
.auto-direction-neutral {
  background: rgba(148, 163, 184, 0.12);
  color: #94a3b8;
  border-color: rgba(148, 163, 184, 0.3);
}
'''
        css_content = css_content.rstrip() + css_add + "\n"
        CSS.write_text(css_content, encoding="utf-8")
        print("CSS: manual panel + direction badges added")

print()
print("=" * 60)
print("DONE")
print("=" * 60)
print()
print("Next:")
print("  cd C:\\Users\\Administrator\\ROBOMLM_PLUS\\frontend")
print("  npx tsc --noEmit")
print()
print("If tsc is clean, also need to add manual panel JSX.")
print("Run the diagnostic to check:")
print("  findstr /N \"auto-manual-panel\" C:\\Users\\Administrator\\ROBOMLM_PLUS\\frontend\\autorobomlm\\index.tsx")