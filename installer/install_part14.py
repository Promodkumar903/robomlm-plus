"""Sort opportunities: strongest on top"""
from pathlib import Path
import shutil
from datetime import datetime

FILE = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\autorobomlm\index.tsx")

if not FILE.exists():
    print(f"ERROR: {FILE} not found.")
    raise SystemExit(1)

content = FILE.read_text(encoding="utf-8")

backup = FILE.with_suffix(f".tsx.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(FILE, backup)
print(f"BACKUP: {backup}")

applied = []
skipped = []

# ----------------------------------------------------------------
# FIX 1: Sort opportunities in loadAll
# ----------------------------------------------------------------
old_block = '''    if (discRes.status === "fulfilled" && discRes.value) {
      const opps = extractOpportunities(discRes.value);
      setOpportunities(opps);
      setSelected((prev) => prev ?? opps[0] ?? null);
    } else {'''

new_block = '''    if (discRes.status === "fulfilled" && discRes.value) {
      const opps = extractOpportunities(discRes.value).sort(sortOpportunities);
      setOpportunities(opps);
      setSelected((prev) => prev ?? opps[0] ?? null);
    } else {'''

if old_block in content:
    content = content.replace(old_block, new_block, 1)
    applied.append("1: sort applied at loadAll")
else:
    skipped.append("1: block not found")

# ----------------------------------------------------------------
# FIX 2: Add sortOpportunities helper before extractOpportunities
# ----------------------------------------------------------------
sort_helper = '''
/**
 * Sort opportunities:
 *   1. Directional (LONG/SHORT) before NEUTRAL
 *   2. Then by score descending
 *   3. Then alphabetically by symbol
 *
 * Strongest candidate ends up on top.
 */
function sortOpportunities(a: Opportunity, b: Opportunity): number {
  const aDir = (a.direction || "").toUpperCase();
  const bDir = (b.direction || "").toUpperCase();

  const aDirectional = aDir === "LONG" || aDir === "SHORT" ? 1 : 0;
  const bDirectional = bDir === "LONG" || bDir === "SHORT" ? 1 : 0;

  if (aDirectional !== bDirectional) {
    return bDirectional - aDirectional;
  }

  const aScore = a.score ?? -Infinity;
  const bScore = b.score ?? -Infinity;

  if (aScore !== bScore) {
    return bScore - aScore;
  }

  return a.symbol.localeCompare(b.symbol);
}

'''

# Insert before extractOpportunities function
old_marker = "function extractOpportunities(payload: AnyRecord | null): Opportunity[] {"
if "function sortOpportunities" in content:
    skipped.append("2: helper already exists")
elif old_marker in content:
    content = content.replace(old_marker, sort_helper + old_marker, 1)
    applied.append("2: sortOpportunities helper added")
else:
    skipped.append("2: extractOpportunities marker not found")

# ----------------------------------------------------------------
# Write
# ----------------------------------------------------------------
FILE.write_text(content, encoding="utf-8")

print()
print("APPLIED:")
for a in applied:
    print(f"  + {a}")
print("SKIPPED:")
for s in skipped:
    print(f"  - {s}")
print()
print(f"UPDATED: {FILE}")
print()
print("Next:")
print("  cd C:\\Users\\Administrator\\ROBOMLM_PLUS\\frontend")
print("  npx tsc --noEmit")