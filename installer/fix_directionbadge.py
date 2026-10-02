"""Fix broken DirectionBadge — find and repair"""
from pathlib import Path
import shutil
from datetime import datetime

TSX = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\autorobomlm\index.tsx")

if not TSX.exists():
    print(f"ERROR: {TSX} not found")
    raise SystemExit(1)

content = TSX.read_text(encoding="utf-8")
backup = TSX.with_suffix(f".tsx.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(TSX, backup)
print(f"BACKUP: {backup}")

lines = content.split("\n")

# Show lines 355-375 to see the broken section
print()
print("BROKEN SECTION (lines 355-375):")
print("-" * 60)
for i in range(354, min(375, len(lines))):
    print(f"{i+1:4}: {lines[i]}")
print("-" * 60)

# Look for the orphan fragment
target = "}: { direction: string }) {"
target_line = None
for i, line in enumerate(lines):
    if target in line and i > 340:
        target_line = i
        break

if target_line is None:
    print()
    print("Orphan line not found. Showing 340-365:")
    for i in range(339, min(366, len(lines))):
        print(f"{i+1:4}: {lines[i]}")
    raise SystemExit(0)

print()
print(f"Found orphan at line {target_line + 1}: {lines[target_line]}")

# Strategy: find the new DirectionBadge start (with normalized code)
new_start = None
for i in range(len(lines)):
    if "const raw = String(direction ?? \"\").trim().toUpperCase();" in lines[i]:
        # Look backwards to find function start
        for j in range(i, max(0, i-10), -1):
            if "function DirectionBadge" in lines[j]:
                new_start = j
                break
        break

if new_start is None:
    print("New DirectionBadge start not found")
    raise SystemExit(1)

print(f"New DirectionBadge starts at line {new_start + 1}: {lines[new_start]}")

# Find the closing brace of new function (should have "return <span" then "}")
new_end = None
for i in range(new_start, min(new_start + 40, len(lines))):
    if lines[i].strip() == "}" and i > new_start + 5:
        # check if previous non-empty line has "return <span"
        for j in range(i-1, new_start, -1):
            if lines[j].strip():
                if "return <span" in lines[j]:
                    new_end = i
                    break
                break
        if new_end is not None:
            break

if new_end is None:
    print("New DirectionBadge end not found")
    raise SystemExit(1)

print(f"New DirectionBadge ends at line {new_end + 1}")

# Now find the orphan block — from target_line, find next "}" that closes it
orphan_start = target_line - 1  # go 1 line back for safety
# Actually orphan starts where "}: { direction: string }) {" is and goes to next "}"
orphan_end = None
for i in range(target_line, min(target_line + 60, len(lines))):
    if lines[i].strip() == "}" and i > target_line + 2:
        # make sure next non-empty line is a new function or export
        for j in range(i+1, min(i+5, len(lines))):
            nxt = lines[j].strip()
            if nxt:
                if nxt.startswith("function ") or nxt.startswith("export ") or nxt.startswith("const "):
                    orphan_end = i
                    break
                break
        if orphan_end is not None:
            break

if orphan_end is None:
    print("Could not find orphan end. Showing context:")
    for i in range(target_line, min(target_line + 30, len(lines))):
        print(f"{i+1:4}: {lines[i]}")
    raise SystemExit(1)

print(f"Orphan block: lines {target_line + 1} to {orphan_end + 1}")
print()
print("Orphan content to remove:")
for i in range(target_line, orphan_end + 1):
    print(f"  {lines[i]}")

# Remove the orphan block
new_lines = lines[:target_line] + lines[orphan_end + 1:]
new_content = "\n".join(new_lines)

TSX.write_text(new_content, encoding="utf-8")
print()
print(f"FIXED: removed {orphan_end - target_line + 1} orphan lines")
print()
print("Next:")
print("  cd C:\\Users\\Administrator\\ROBOMLM_PLUS\\frontend")
print("  npx tsc --noEmit")