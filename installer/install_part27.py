"""
Fix DirectionBadge + add Manual Trade panel (no regex)
"""
from pathlib import Path
import shutil
from datetime import datetime

TSX = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\autorobomlm\index.tsx")
CSS = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\autorobomlm\autorobomlm.css")

TS = datetime.now().strftime('%Y%m%d_%H%M%S')
applied = []
skipped = []

if not TSX.exists():
    print(f"ERROR: {TSX} not found")
    raise SystemExit(1)

content = TSX.read_text(encoding="utf-8")
backup = TSX.with_suffix(f".tsx.bak_{TS}")
shutil.copy2(TSX, backup)
print(f"BACKUP: {backup}")

# ==================================================================
# FIX 1 — DirectionBadge (find by brace counting, replace)
# ==================================================================
if "auto-direction-long" in content:
    skipped.append("1: DirectionBadge already normalized")
else:
    # Locate function start
    start_marker = "function DirectionBadge("
    sidx = content.find(start_marker)

    if sidx < 0:
        skipped.append("1: DirectionBadge not found")
    else:
        # Find the body opening brace
        open_idx = content.find("{", sidx + len(start_marker))
        if open_idx < 0:
            skipped.append("1: body brace not found")
        else:
            # Balance braces to find function end
            depth = 0
            end_idx = None
            for i in range(open_idx, len(content)):
                ch = content[i]
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        end_idx = i
                        break

            if end_idx is None:
                skipped.append("1: matching brace not found")
            else:
                # Find line start of function
                line_start = content.rfind("\n", 0, sidx) + 1

                new_badge = '''function DirectionBadge({ direction }: { direction: string }) {
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

                content = content[:line_start] + new_badge + content[end_idx + 1:]
                applied.append("1: DirectionBadge normalized")

# ==================================================================
# FIX 2 — Manual trade state
# ==================================================================
if "manualSymbol" in content:
    skipped.append("2a: manual state already exists")
else:
    m1 = '  const [positions, setPositions] = useState<AutoRobomlmPosition[]>([]);'
    if m1 in content:
        content = content.replace(
            m1,
            m1 + '''

  const [manualSymbol, setManualSymbol] = useState("");
  const [manualDirection, setManualDirection] = useState<"LONG" | "SHORT">("LONG");
  const [manualQty, setManualQty] = useState("");''',
            1,
        )
        applied.append("2a: manual state added")
    else:
        skipped.append("2a: positions state marker not found")

# ==================================================================
# FIX 2b — Manual trade handler
# ==================================================================
if "handleManualTrade" in content:
    skipped.append("2b: handler already exists")
else:
    m2 = "  const handleClosePosition = useCallback("
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
    if m2 in content:
        content = content.replace(m2, handler, 1)
        applied.append("2b: handleManualTrade added")
    else:
        skipped.append("2b: close handler marker not found")

# ==================================================================
# FIX 2c — Manual panel JSX (insert before NEXT BEST section)
# ==================================================================
if 'className="auto-manual-panel"' in content:
    skipped.append("2c: manual panel already exists")
else:
    # Marker: the comment before NEXT BEST or the section header
    markers_to_try = [
        '      {/* NEXT BEST OPPORTUNITIES */}',
        '<span className="auto-eyebrow">NEXT BEST</span>',
    ]

    inserted = False
    for marker in markers_to_try:
        if marker in content:
            manual_panel = '''      {/* MANUAL TRADE PANEL */}
      <section className="auto-panel auto-manual-panel">
        <div className="auto-panel-head">
          <div>
            <span className="auto-eyebrow">MANUAL</span>
            <h2>Manual trade</h2>
          </div>
        </div>

        <div className="auto-manual-body">
          <div className="auto-manual-input-group">
            <label className="auto-manual-label">Symbol</label>
            <input
              type="text"
              className="auto-manual-input"
              placeholder="e.g. BTC/USDT, ETH/USDT"
              value={manualSymbol}
              onChange={(e) =>
                setManualSymbol(e.target.value.toUpperCase())
              }
              disabled={busy}
            />
          </div>

          <div className="auto-manual-actions">
            <button
              type="button"
              className="auto-btn auto-manual-btn auto-manual-btn-buy"
              onClick={() => handleManualTrade("LONG")}
              disabled={busy || !manualSymbol.trim()}
            >
              BUY / LONG
            </button>

            <button
              type="button"
              className="auto-btn auto-manual-btn auto-manual-btn-sell"
              onClick={() => handleManualTrade("SHORT")}
              disabled={busy || !manualSymbol.trim()}
            >
              SELL / SHORT
            </button>
          </div>

          <p className="auto-manual-hint">
            Manual trade bypasses grade gate but still passes through
            objective, resource, constraint gates, capital allocator,
            SL/TP calculator and paper broker.
          </p>
        </div>
      </section>

'''
            if marker.startswith("      {/*"):
                content = content.replace(marker, manual_panel + marker, 1)
            else:
                # Insert before the NEXT BEST section opening
                # Find opening <section before this marker
                marker_idx = content.find(marker)
                section_idx = content.rfind("<section", 0, marker_idx)
                if section_idx > 0:
                    content = (
                        content[:section_idx]
                        + manual_panel
                        + content[section_idx:]
                    )

            applied.append(f"2c: manual panel inserted before '{marker[:40]}'")
            inserted = True
            break

    if not inserted:
        skipped.append("2c: no insertion marker found")

TSX.write_text(content, encoding="utf-8")

# ==================================================================
# FIX 3 — CSS
# ==================================================================
if CSS.exists():
    css_content = CSS.read_text(encoding="utf-8")
    css_backup = CSS.with_suffix(f".css.bak_{TS}")
    shutil.copy2(CSS, css_backup)

    if ".auto-manual-panel" in css_content:
        skipped.append("3: manual panel css already exists")
    else:
        css = '''

/* ============================================================
   MANUAL TRADE PANEL
   ============================================================ */

.auto-manual-panel {
  border-color: #334155;
  background: linear-gradient(
    135deg,
    rgba(30, 41, 59, 0.6) 0%,
    rgba(15, 23, 42, 0.6) 100%
  );
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

.auto-manual-input:disabled {
  opacity: 0.55;
}

.auto-manual-input::placeholder {
  color: #475569;
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
  transition: all 0.15s ease !important;
  border: 1px solid transparent !important;
}

.auto-manual-btn-buy {
  background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
  color: #ffffff !important;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
}

.auto-manual-btn-buy:hover:not(:disabled) {
  background: linear-gradient(135deg, #047857 0%, #059669 100%) !important;
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
}

.auto-manual-btn-sell {
  background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%) !important;
  color: #ffffff !important;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.25);
}

.auto-manual-btn-sell:hover:not(:disabled) {
  background: linear-gradient(135deg, #b91c1c 0%, #dc2626 100%) !important;
  box-shadow: 0 6px 16px rgba(239, 68, 68, 0.4);
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

/* ============================================================
   DIRECTION BADGES
   ============================================================ */

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
        css_content = css_content.rstrip() + css + "\n"
        CSS.write_text(css_content, encoding="utf-8")
        applied.append("3: manual panel + direction css")

# ==================================================================
# Report
# ==================================================================
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