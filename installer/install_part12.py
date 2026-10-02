"""Wire autorobomlm page to real backend"""
from pathlib import Path
import re
import shutil
from datetime import datetime

FILE = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\autorobomlm\index.tsx")

if not FILE.exists():
    print(f"ERROR: {FILE} not found.")
    raise SystemExit(1)

content = FILE.read_text(encoding="utf-8")

# Backup
backup = FILE.with_suffix(f".tsx.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(FILE, backup)
print(f"BACKUP: {backup}")

# ----------------------------------------------------------------
# CHANGE 1: Add real imports after existing import block
# ----------------------------------------------------------------
old_import_end = '} from "../src/api/autorobomlm";'
new_import_end = '''} from "../src/api/autorobomlm";

import {
  getPositions,
  startLoop,
  stopLoop,
  killSwitch,
  resumeLoop,
  runTick,
  type AutoRobomlmPosition,
} from "../src/api/autorobomlm";'''

count = content.count(old_import_end)
print(f"Found import end marker: {count} time(s)")

if count >= 1:
    # Only replace the LAST occurrence (which closes the main import)
    # Actually the marker might appear multiple times; use rsplit
    parts = content.rsplit(old_import_end, 1)
    content = parts[0] + new_import_end + parts[1]
    print("CHANGE 1 OK: new imports added")
else:
    print("CHANGE 1 SKIP: marker not found")

# ----------------------------------------------------------------
# CHANGE 2: Replace activeTrades stub with real state
# ----------------------------------------------------------------
old_line = "  const activeTrades: ActiveTrade[] = useMemo(() => [], []);"
new_block = '''  // Real positions from backend
  const [positions, setPositions] = useState<AutoRobomlmPosition[]>([]);
  const [busy, setBusy] = useState(false);

  // Map backend positions to page ActiveTrade shape
  const activeTrades: ActiveTrade[] = useMemo(() => {
    return positions
      .filter((p) => p.status === "OPEN")
      .map((p) => ({
        id: p.position_id,
        symbol: p.symbol,
        direction: p.direction,
        entry: p.entry_price,
        current: p.current_price ?? null,
        stopLoss: p.stop_loss,
        takeProfit: p.take_profit,
        pnl: p.pnl ?? null,
        pnlPct: p.pnl_pct ?? null,
        openedAt: p.opened_at,
      }));
  }, [positions]);'''

if old_line in content:
    content = content.replace(old_line, new_block, 1)
    print("CHANGE 2 OK: activeTrades wired to real state")
else:
    print("CHANGE 2 SKIP: activeTrades line not found")

# ----------------------------------------------------------------
# CHANGE 3: Add positions fetch to loadAll
# ----------------------------------------------------------------
old_promise = "      getAutoRobomlmEvents(),\n      fetchDiscovery(market),\n    ]);"
new_promise = "      getAutoRobomlmEvents(),\n      fetchDiscovery(market),\n      getPositions(),\n    ]);"

if old_promise in content:
    content = content.replace(old_promise, new_promise, 1)
    print("CHANGE 3a OK: positions fetch added to Promise.allSettled")
else:
    print("CHANGE 3a SKIP: Promise block not found")

# Add positions handling after events handling
old_handler = '    if (eRes.status === "fulfilled") setEventsPayload(eRes.value);'
new_handler = '''    if (eRes.status === "fulfilled") setEventsPayload(eRes.value);
'''

# The Promise returns 5 items currently -> we added a 6th -> need to update destructuring
old_destructure = "    const [sRes, rRes, pRes, eRes, discRes] = await Promise.allSettled(["
new_destructure = "    const [sRes, rRes, pRes, eRes, discRes, posRes] = await Promise.allSettled(["

if old_destructure in content:
    content = content.replace(old_destructure, new_destructure, 1)
    print("CHANGE 3b OK: destructuring updated for 6 promises")
else:
    print("CHANGE 3b SKIP: destructure not found")

# Insert positions handling after events line
old_ev_line = '    else failures.push("Events: " + describeAutoRobomlmError(eRes.reason));'
new_ev_block = '''    else failures.push("Events: " + describeAutoRobomlmError(eRes.reason));

    if (posRes.status === "fulfilled") {
      const posPayload = posRes.value as unknown as {
        positions?: AutoRobomlmPosition[];
        all_positions?: AutoRobomlmPosition[];
      };
      setPositions(posPayload.all_positions ?? posPayload.positions ?? []);
    } else {
      failures.push("Positions: " + describeAutoRobomlmError(posRes.reason));
    }'''

if old_ev_line in content:
    content = content.replace(old_ev_line, new_ev_block, 1)
    print("CHANGE 3c OK: positions handling added")
else:
    print("CHANGE 3c SKIP: events line not found")

# ----------------------------------------------------------------
# CHANGE 4: Update derived state (mode / isRunning / killEnabled)
# ----------------------------------------------------------------
pattern_derived = re.compile(
    r"  // Derived state\n"
    r"  const mode = useMemo\(\(\) => \{[\s\S]*?\}, \[plus\]\);\n"
    r"\n"
    r"  const isRunning = useMemo\(\(\) => \{[\s\S]*?\}, \[plus\]\);\n"
    r"\n"
    r"  const killEnabled = useMemo\(\(\) => \{[\s\S]*?\}, \[plus\]\);",
    re.MULTILINE,
)

new_derived = '''  // Derived state from real /status
  const loopState = ((status as AnyRecord | null)?.state as string) ?? "STOPPED";
  const mode =
    (((status as AnyRecord | null)?.config as AnyRecord)
      ?.execution_mode as string) ?? "DEMO";
  const isRunning = loopState === "RUNNING";
  const killEnabled = loopState === "KILLED";'''

if pattern_derived.search(content):
    content = pattern_derived.sub(new_derived, content, count=1)
    print("CHANGE 4 OK: derived state updated")
else:
    print("CHANGE 4 SKIP: derived state block not found")

# ----------------------------------------------------------------
# CHANGE 5: Replace handlers block
# ----------------------------------------------------------------
pattern_handlers = re.compile(
    r"  const handleKill = useCallback\(\(\) => \{[\s\S]*?\}, \[\]\);\n"
    r"\n"
    r"  const handlePause = useCallback\(\(\) => \{[\s\S]*?\}, \[\]\);",
    re.MULTILINE,
)

new_handlers = '''  // -------------------------------------------------------------------------
  // Action handlers - real backend calls
  // -------------------------------------------------------------------------

  const withBusy = useCallback(
    async (fn: () => Promise<unknown>, label: string) => {
      if (busy) return null;
      setBusy(true);
      setError(null);
      try {
        const result = await fn();
        await loadAll();
        return result;
      } catch (err) {
        setError(`${label}: ${describeAutoRobomlmError(err)}`);
        return null;
      } finally {
        setBusy(false);
      }
    },
    [busy, loadAll],
  );

  const handleStart = useCallback(async () => {
    await withBusy(() => startLoop(), "Start");
  }, [withBusy]);

  const handleStop = useCallback(async () => {
    await withBusy(() => stopLoop(), "Stop");
  }, [withBusy]);

  const handleResume = useCallback(async () => {
    await withBusy(() => resumeLoop(), "Resume");
  }, [withBusy]);

  const handleTick = useCallback(async () => {
    await withBusy(() => runTick(), "Tick");
  }, [withBusy]);

  const handleKill = useCallback(async () => {
    // eslint-disable-next-line no-alert
    const confirmed = confirm(
      "Kill switch will stop all automation activity. This is a safety control. Proceed?",
    );
    if (!confirmed) return;
    await withBusy(() => killSwitch(), "Kill");
  }, [withBusy]);'''

if pattern_handlers.search(content):
    content = pattern_handlers.sub(new_handlers, content, count=1)
    print("CHANGE 5 OK: handlers replaced")
else:
    print("CHANGE 5 SKIP: handlers block not found")

# ----------------------------------------------------------------
# CHANGE 6: Replace header buttons (Start + Stop + Tick + Resume + Kill)
# ----------------------------------------------------------------
pattern_buttons = re.compile(
    r'          <button\s+type="button"\s+className="auto-btn auto-btn-ghost"\s+onClick=\{handlePause\}[\s\S]*?</button>\s*'
    r'<button\s+type="button"\s+className="auto-btn auto-btn-danger"\s+onClick=\{handleKill\}[\s\S]*?</button>',
    re.MULTILINE,
)

new_buttons = '''          <button
            type="button"
            className="auto-btn auto-btn-primary"
            onClick={handleStart}
            disabled={busy || isRunning || killEnabled}
          >
            {busy ? "..." : "\\u25B6 Start"}
          </button>

          <button
            type="button"
            className="auto-btn auto-btn-ghost"
            onClick={handleStop}
            disabled={busy || !isRunning}
          >
            \\u23F8 Stop
          </button>

          <button
            type="button"
            className="auto-btn auto-btn-ghost"
            onClick={handleTick}
            disabled={busy}
          >
            \\u21BB Tick
          </button>

          <button
            type="button"
            className="auto-btn auto-btn-ghost"
            onClick={handleResume}
            disabled={busy || !killEnabled}
          >
            \\u27F2 Resume
          </button>

          <button
            type="button"
            className="auto-btn auto-btn-danger"
            onClick={handleKill}
            disabled={busy || killEnabled}
          >
            \\u{1F6D1} Kill
          </button>'''

# Unescape the unicode escapes for actual file content
new_buttons = new_buttons.replace("\\\\u", "\\u")

if pattern_buttons.search(content):
    content = pattern_buttons.sub(new_buttons, content, count=1)
    print("CHANGE 6 OK: header buttons replaced")
else:
    print("CHANGE 6 SKIP: header buttons not matched")

FILE.write_text(content, encoding="utf-8")
print()
print(f"UPDATED: {FILE}")
print(f"  ({FILE.stat().st_size} bytes)")
print()
print("Next:")
print("  cd C:\\Users\\Administrator\\ROBOMLM_PLUS\\frontend")
print("  npx tsc --noEmit")