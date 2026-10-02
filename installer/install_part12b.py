"""Wire autorobomlm page to real backend - FIXED"""
from pathlib import Path
import re
import shutil
from datetime import datetime

FILE = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\autorobomlm\index.tsx")

if not FILE.exists():
    print(f"ERROR: {FILE} not found.")
    raise SystemExit(1)

content = FILE.read_text(encoding="utf-8")

# Backup (skip if already did)
backup = FILE.with_suffix(f".tsx.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(FILE, backup)
print(f"BACKUP: {backup}")

applied = []
skipped = []

# ----------------------------------------------------------------
# CHANGE 1: Add real imports
# ----------------------------------------------------------------
if "getPositions," not in content:
    old = '} from "../src/api/autorobomlm";'
    new = '''} from "../src/api/autorobomlm";

import {
  getPositions,
  startLoop,
  stopLoop,
  killSwitch,
  resumeLoop,
  runTick,
  type AutoRobomlmPosition,
} from "../src/api/autorobomlm";'''
    parts = content.rsplit(old, 1)
    if len(parts) == 2:
        content = parts[0] + new + parts[1]
        applied.append("1: imports")
    else:
        skipped.append("1: marker not found")
else:
    skipped.append("1: already applied")

# ----------------------------------------------------------------
# CHANGE 2: activeTrades real state
# ----------------------------------------------------------------
old2 = "  const activeTrades: ActiveTrade[] = useMemo(() => [], []);"
if "const [positions, setPositions] = useState<AutoRobomlmPosition[]>([]);" in content:
    skipped.append("2: already applied")
elif old2 in content:
    new2 = '''  // Real positions from backend
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
    content = content.replace(old2, new2, 1)
    applied.append("2: activeTrades")
else:
    skipped.append("2: target line not found")

# ----------------------------------------------------------------
# CHANGE 3: positions fetch
# ----------------------------------------------------------------
if "getPositions()," in content:
    skipped.append("3a: already applied")
else:
    old3 = "      getAutoRobomlmEvents(),\n      fetchDiscovery(market),\n    ]);"
    if old3 in content:
        new3 = "      getAutoRobomlmEvents(),\n      fetchDiscovery(market),\n      getPositions(),\n    ]);"
        content = content.replace(old3, new3, 1)
        applied.append("3a: fetch")
    else:
        skipped.append("3a: block not found")

if "posRes" in content and "[sRes, rRes, pRes, eRes, discRes, posRes]" in content:
    skipped.append("3b: already applied")
else:
    old3b = "    const [sRes, rRes, pRes, eRes, discRes] = await Promise.allSettled(["
    new3b = "    const [sRes, rRes, pRes, eRes, discRes, posRes] = await Promise.allSettled(["
    if old3b in content:
        content = content.replace(old3b, new3b, 1)
        applied.append("3b: destructure")
    else:
        skipped.append("3b: not found")

if 'failures.push("Positions: "' in content:
    skipped.append("3c: already applied")
else:
    old3c = '    else failures.push("Events: " + describeAutoRobomlmError(eRes.reason));'
    new3c = '''    else failures.push("Events: " + describeAutoRobomlmError(eRes.reason));

    if (posRes.status === "fulfilled") {
      const posPayload = posRes.value as unknown as {
        positions?: AutoRobomlmPosition[];
        all_positions?: AutoRobomlmPosition[];
      };
      setPositions(posPayload.all_positions ?? posPayload.positions ?? []);
    } else {
      failures.push("Positions: " + describeAutoRobomlmError(posRes.reason));
    }'''
    if old3c in content:
        content = content.replace(old3c, new3c, 1)
        applied.append("3c: handler")
    else:
        skipped.append("3c: not found")

# ----------------------------------------------------------------
# CHANGE 4: derived state
# ----------------------------------------------------------------
if 'const loopState = ((status as AnyRecord | null)?.state as string)' in content:
    skipped.append("4: already applied")
else:
    pat4 = re.compile(
        r"  // Derived state\n"
        r"  const mode = useMemo\(\(\) => \{[\s\S]*?\}, \[plus\]\);\n"
        r"\n"
        r"  const isRunning = useMemo\(\(\) => \{[\s\S]*?\}, \[plus\]\);\n"
        r"\n"
        r"  const killEnabled = useMemo\(\(\) => \{[\s\S]*?\}, \[plus\]\);",
        re.MULTILINE,
    )
    new4 = '''  // Derived state from real /status
  const loopState = ((status as AnyRecord | null)?.state as string) ?? "STOPPED";
  const mode =
    (((status as AnyRecord | null)?.config as AnyRecord)
      ?.execution_mode as string) ?? "DEMO";
  const isRunning = loopState === "RUNNING";
  const killEnabled = loopState === "KILLED";'''
    if pat4.search(content):
        content = pat4.sub(new4, content, count=1)
        applied.append("4: derived")
    else:
        skipped.append("4: pattern not found")

# ----------------------------------------------------------------
# CHANGE 5: handlers
# ----------------------------------------------------------------
if "const handleStart = useCallback" in content:
    skipped.append("5: already applied")
else:
    pat5 = re.compile(
        r"  const handleKill = useCallback\(\(\) => \{[\s\S]*?\}, \[\]\);\n"
        r"\n"
        r"  const handlePause = useCallback\(\(\) => \{[\s\S]*?\}, \[\]\);",
        re.MULTILINE,
    )
    new5 = '''  const withBusy = useCallback(
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
    const confirmed = confirm(
      "Kill switch will stop all automation activity. This is a safety control. Proceed?",
    );
    if (!confirmed) return;
    await withBusy(() => killSwitch(), "Kill");
  }, [withBusy]);'''
    if pat5.search(content):
        content = pat5.sub(new5, content, count=1)
        applied.append("5: handlers")
    else:
        skipped.append("5: pattern not found")

# ----------------------------------------------------------------
# CHANGE 6: header buttons (find/replace by anchors)
# ----------------------------------------------------------------
if 'onClick={handleStart}' in content and 'onClick={handleTick}' in content:
    skipped.append("6: already applied")
else:
    start_marker = '<span className="auto-mode-tag">{mode}</span>'
    start_idx = content.find(start_marker)

    if start_idx < 0:
        skipped.append("6: start marker not found")
    else:
        # Find handleKill reference then the closing </button>
        kill_ref_idx = content.find("onClick={handleKill}", start_idx)
        if kill_ref_idx < 0:
            skipped.append("6: kill ref not found")
        else:
            end_idx = content.find("</button>", kill_ref_idx)
            if end_idx < 0:
                skipped.append("6: closing button not found")
            else:
                end_idx = end_idx + len("</button>")

                new_buttons = '''<span className="auto-mode-tag">{mode}</span>

          <button
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
            Kill
          </button>'''

                content = content[:start_idx] + new_buttons + content[end_idx:]
                applied.append("6: buttons")

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
print(f"  ({FILE.stat().st_size} bytes)")
print()
print("Next:")
print("  cd C:\\Users\\Administrator\\ROBOMLM_PLUS\\frontend")
print("  npx tsc --noEmit")