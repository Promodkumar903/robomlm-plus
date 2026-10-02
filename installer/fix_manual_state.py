"""Add manual trade state + handler to AutoRobomlmPage component"""
from pathlib import Path
import shutil
from datetime import datetime

TSX = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\autorobomlm\index.tsx")

if not TSX.exists():
    print(f"ERROR: {TSX} not found")
    raise SystemExit(1)

content = TSX.read_text(encoding="utf-8")

if "manualSymbol" in content and "const [manualSymbol" in content:
    print("State already exists.")
    raise SystemExit(0)

backup = TSX.with_suffix(f".tsx.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(TSX, backup)
print(f"BACKUP: {backup}")

applied = []
skipped = []

# ---- 1. Add state after positions useState ----
if "const [manualSymbol" in content:
    skipped.append("1: manual state already exists")
else:
    marker = '  const [positions, setPositions] = useState<AutoRobomlmPosition[]>([]);'
    if marker in content:
        content = content.replace(
            marker,
            marker + '''

  const [manualSymbol, setManualSymbol] = useState("");
  const [manualDirection, setManualDirection] = useState<"LONG" | "SHORT">("LONG");''',
            1,
        )
        applied.append("1: manual state added")
    else:
        # Fallback
        m2 = '  const [busy, setBusy] = useState(false);'
        if m2 in content:
            content = content.replace(
                m2,
                m2 + '''

  const [manualSymbol, setManualSymbol] = useState("");
  const [manualDirection, setManualDirection] = useState<"LONG" | "SHORT">("LONG");''',
                1,
            )
            applied.append("1: manual state added (fallback)")
        else:
            skipped.append("1: state marker not found")

# ---- 2. Add handler before handleClosePosition ----
if "handleManualTrade" in content:
    skipped.append("2: handler already exists")
else:
    marker = "  const handleClosePosition = useCallback("
    handler = '''  const handleManualTrade = useCallback(
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

  const handleClosePosition = useCallback('''
    if marker in content:
        content = content.replace(marker, handler, 1)
        applied.append("2: handleManualTrade added")
    else:
        # Fallback: before handleCloseAll
        m2 = "  const handleCloseAll = useCallback("
        if m2 in content:
            content = content.replace(
                m2,
                '''  const handleManualTrade = useCallback(
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

''' + m2,
                1,
            )
            applied.append("2: handleManualTrade added (fallback)")
        else:
            skipped.append("2: handler marker not found")

# ---- 3. Ensure takeOpportunity imported ----
if "takeOpportunity," in content:
    skipped.append("3: takeOpportunity already imported")
else:
    marker = '  runTick,'
    if marker in content:
        content = content.replace(
            marker,
            marker + '\n  takeOpportunity,',
            1,
        )
        applied.append("3: takeOpportunity import added")
    else:
        skipped.append("3: runTick import marker not found")

TSX.write_text(content, encoding="utf-8")

print()
print("APPLIED:")
for a in applied:
    print(f"  + {a}")
print("SKIPPED:")
for s in skipped:
    print(f"  - {s}")
print()
print("Next:")
print("  cd C:\\Users\\Administrator\\ROBOMLM_PLUS\\frontend")
print("  npx tsc --noEmit")
print("  Ctrl+Shift+R in browser")