"""
Add DEMO/LIVE dropdown + wire mode change
"""
from pathlib import Path
import shutil
from datetime import datetime

TSX = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\autorobomlm\index.tsx")
CSS = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\autorobomlm\autorobomlm.css")

if not TSX.exists():
    print(f"ERROR: {TSX} not found.")
    raise SystemExit(1)

applied = []
skipped = []

content = TSX.read_text(encoding="utf-8")
backup = TSX.with_suffix(f".tsx.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(TSX, backup)
print(f"BACKUP: {backup}")

# ------------------------------------------------------------
# 1. Add updateConfig to imports (if missing)
# ------------------------------------------------------------
if "updateConfig," in content:
    skipped.append("1: updateConfig already imported")
else:
    if "  runTick," in content:
        content = content.replace(
            "  runTick,",
            "  runTick,\n  updateConfig,",
            1,
        )
        applied.append("1: updateConfig import added")
    else:
        skipped.append("1: runTick import marker not found")

# ------------------------------------------------------------
# 2. Add pendingMode state (if missing)
# ------------------------------------------------------------
if "pendingMode" in content:
    skipped.append("2: pendingMode already exists")
else:
    marker = '  const [busy, setBusy] = useState(false);'
    if marker in content:
        content = content.replace(
            marker,
            marker + '\n  const [pendingMode, setPendingMode] = useState<"DEMO" | "LIVE">("DEMO");',
            1,
        )
        applied.append("2: pendingMode state added")
    else:
        skipped.append("2: busy state marker not found")

# ------------------------------------------------------------
# 3. Sync pendingMode when status loads (if missing)
# ------------------------------------------------------------
if "setPendingMode(mode" in content:
    skipped.append("3: pendingMode sync already exists")
else:
    marker = '  const killEnabled = loopState === "KILLED";'
    sync_block = '''  const killEnabled = loopState === "KILLED";

  // Sync pendingMode with backend when idle
  useEffect(() => {
    if (!isRunning && (mode === "DEMO" || mode === "LIVE")) {
      setPendingMode(mode as "DEMO" | "LIVE");
    }
  }, [mode, isRunning]);'''
    if marker in content:
        content = content.replace(marker, sync_block, 1)
        applied.append("3: pendingMode sync effect added")
    else:
        skipped.append("3: killEnabled marker not found")

# ------------------------------------------------------------
# 4. Push mode change before Start (if missing)
# ------------------------------------------------------------
if "pendingMode !== mode" in content:
    skipped.append("4: handleStart already pushes mode")
else:
    old_start = '''  const handleStart = useCallback(async () => {
    await withBusy(() => startLoop(), "Start");
  }, [withBusy]);'''

    new_start = '''  const handleStart = useCallback(async () => {
    // Push mode change if it differs from backend
    if (pendingMode !== mode) {
      const result = await withBusy(
        () =>
          updateConfig({
            execution_mode: pendingMode,
            live_confirmed: pendingMode === "LIVE",
          }),
        "Mode change",
      );
      if (result === null) return;
    }
    await withBusy(() => startLoop(), "Start");
  }, [withBusy, pendingMode, mode]);'''

    if old_start in content:
        content = content.replace(old_start, new_start, 1)
        applied.append("4: handleStart pushes mode change")
    else:
        skipped.append("4: handleStart marker not found")

# ------------------------------------------------------------
# 5. Replace mode <span> with <select> dropdown
# ------------------------------------------------------------
if '<select' in content and 'pendingMode' in content and 'onChange={(e) => setPendingMode' in content:
    skipped.append("5: dropdown already exists")
else:
    # Replace the tag span with a select
    old_span = '<span className="auto-mode-tag">{mode}</span>'
    new_select = '''<select
            className="auto-select auto-select-mode"
            value={pendingMode}
            onChange={(e) =>
              setPendingMode(e.target.value as "DEMO" | "LIVE")
            }
            disabled={busy || isRunning}
            title={
              isRunning
                ? "Stop the loop to change mode"
                : "Select execution mode"
            }
          >
            <option value="DEMO">DEMO</option>
            <option value="LIVE">LIVE</option>
          </select>'''
    if old_span in content:
        content = content.replace(old_span, new_select, 1)
        applied.append("5: mode dropdown added")
    else:
        skipped.append("5: mode span not found")

TSX.write_text(content, encoding="utf-8")

# ------------------------------------------------------------
# 6. CSS for the dropdown
# ------------------------------------------------------------
if CSS.exists():
    css_content = CSS.read_text(encoding="utf-8")
    css_backup = CSS.with_suffix(f".css.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    shutil.copy2(CSS, css_backup)

    if "auto-select-mode" in css_content:
        skipped.append("6: CSS already present")
    else:
        css_append = '''

/* ============================================================
   MODE DROPDOWN
   ============================================================ */

.auto-select-mode {
  min-width: 96px;
  padding: 6px 28px 6px 12px;
  background-color: #0f172a !important;
  color: #e2e8f0 !important;
  border: 1px solid #334155 !important;
  border-radius: 8px !important;
  font-size: 12px !important;
  font-weight: 700 !important;
  letter-spacing: 1px !important;
  text-transform: uppercase !important;
  cursor: pointer;
  appearance: none;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 10 10'><path d='M1 3l4 4 4-4' stroke='%2394a3b8' stroke-width='1.5' fill='none' stroke-linecap='round' stroke-linejoin='round'/></svg>") !important;
  background-repeat: no-repeat !important;
  background-position: right 8px center !important;
}

.auto-select-mode:hover:not(:disabled) {
  border-color: #475569 !important;
  background-color: #1e293b !important;
}

.auto-select-mode:focus {
  outline: none !important;
  border-color: #3b82f6 !important;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
}

.auto-select-mode:disabled {
  opacity: 0.55 !important;
  cursor: not-allowed !important;
}

.auto-select-mode option {
  background-color: #0f172a;
  color: #e2e8f0;
  padding: 8px;
}
'''
        css_content = css_content.rstrip() + css_append + "\n"
        CSS.write_text(css_content, encoding="utf-8")
        applied.append("6: CSS for dropdown added")
else:
    skipped.append("6: CSS file not found")

# ------------------------------------------------------------
# Report
# ------------------------------------------------------------
print()
print("APPLIED:")
for a in applied:
    print(f"  + {a}")
print("SKIPPED:")
for s in skipped:
    print(f"  - {s}")
print()
print(f"UPDATED: {TSX}")
if CSS.exists():
    print(f"UPDATED: {CSS}")
print()
print("Next:")
print("  cd C:\\Users\\Administrator\\ROBOMLM_PLUS\\frontend")
print("  npx tsc --noEmit")
print("  (then Ctrl+Shift+R in browser)")