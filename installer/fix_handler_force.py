"""Force insert handleManualTrade function definition"""
from pathlib import Path
import shutil
from datetime import datetime

TSX = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\autorobomlm\index.tsx")

if not TSX.exists():
    print(f"ERROR: {TSX} not found")
    raise SystemExit(1)

content = TSX.read_text(encoding="utf-8")

# Check for actual DEFINITION, not usage
if "const handleManualTrade = useCallback" in content:
    print("Handler definition already exists.")
    raise SystemExit(0)

backup = TSX.with_suffix(f".tsx.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(TSX, backup)
print(f"BACKUP: {backup}")

handler_def = '''  const handleManualTrade = useCallback(
    async (direction: "LONG" | "SHORT") => {
      const sym = manualSymbol.trim().toUpperCase();
      if (!sym) {
        alert("Enter a symbol first (e.g. BTC/USDT)");
        return;
      }
      const confirmed = confirm(
        `Open ${direction} on ${sym} at market price?`,
      );
      if (!confirmed) return;
      await withBusy(
        () =>
          takeOpportunity(
            sym,
            direction,
            "MANUAL",
            undefined,
            pendingMinGrade,
          ),
        `Manual ${direction} ${sym}`,
      );
    },
    [withBusy, manualSymbol, pendingMinGrade],
  );

'''

# Try multiple insertion points
inserted = False

# Option 1: Before handleClosePosition
marker1 = "  const handleClosePosition = useCallback("
if marker1 in content:
    content = content.replace(marker1, handler_def + marker1, 1)
    inserted = True
    print("Inserted before handleClosePosition")

# Option 2: Before handleCloseAll
if not inserted:
    marker2 = "  const handleCloseAll = useCallback("
    if marker2 in content:
        content = content.replace(marker2, handler_def + marker2, 1)
        inserted = True
        print("Inserted before handleCloseAll")

# Option 3: Before handleKill
if not inserted:
    marker3 = "  const handleKill = useCallback("
    if marker3 in content:
        content = content.replace(marker3, handler_def + marker3, 1)
        inserted = True
        print("Inserted before handleKill")

# Option 4: Before handleStart
if not inserted:
    marker4 = "  const handleStart = useCallback("
    if marker4 in content:
        content = content.replace(marker4, handler_def + marker4, 1)
        inserted = True
        print("Inserted before handleStart")

# Option 5: Before the return statement (last resort)
if not inserted:
    marker5 = "  return (\n    <main className=\"autorobomlm-page\">"
    if marker5 in content:
        content = content.replace(marker5, handler_def + marker5, 1)
        inserted = True
        print("Inserted before return statement")

if not inserted:
    print("ERROR: no insertion point found")
    print("Searching for handle* markers...")
    import re
    for m in re.finditer(r"const handle\w+ = useCallback", content):
        line_num = content[:m.start()].count("\n") + 1
        print(f"  line {line_num}: {m.group()}")
    raise SystemExit(1)

TSX.write_text(content, encoding="utf-8")
print()
print("DONE. Handler inserted.")
print()
print("Next:")
print("  cd C:\\Users\\Administrator\\ROBOMLM_PLUS\\frontend")
print("  npx tsc --noEmit")