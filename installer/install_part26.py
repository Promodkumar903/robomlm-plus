"""
1. Fix DirectionBadge — BUY→LONG, SELL→SHORT
2. Add Manual Trade panel (symbol input + Buy/Sell buttons)
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
# FIX 1 — DirectionBadge normalizes BUY/SELL
# ==================================================================
# Find the existing DirectionBadge function and replace
import re

pattern = re.compile(
    r"function DirectionBadge\(\{ direction \}: \{ direction: string \}\) \{[\s\S]*?\n\}",
    re.MULTILINE,
)

new_badge = '''function DirectionBadge({ direction }: { direction: string }) {
  const raw = String(direction ?? "").trim().toUpperCase();

  // Normalize: BUY → LONG, SELL → SHORT, rest stay
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
      ? "\\u2191 LONG"
      : normalized === "SHORT"
        ? "\\u2193 SHORT"
        : "\\u2014 NEUTRAL";

  return <span className={cls}>{label}</span>;
}'''

if "auto-direction-long" in content:
    skipped.append("1: DirectionBadge already normalized")
elif pattern.search(content):
    content = pattern.sub(new_badge, content, count=1)
    applied.append("1: DirectionBadge normalized")
else:
    skipped.append("1: DirectionBadge pattern not found")

# ==================================================================
# FIX 2 — Add Manual Trade panel (JSX)
# ==================================================================
# Add a state for manual trade inputs after existing state declarations
if "manualSymbol" in content:
    skipped.append("2a: manual state already exists")
else:
    marker = '  const [pendingMinGrade, setPendingMinGrade] = useState<GradeBand>("B");'
    manual_state = marker + '''
  const [manualSymbol, setManualSymbol] = useState("");
  const [manualDirection, setManualDirection] = useState<"LONG" | "SHORT">("LONG");
  const [manualQty, setManualQty] = useState("");'''

    if marker in content:
        content = content.replace(marker, manual_state, 1)
        applied.append("2a: manual state added")
    else:
        # Fallback - find any state marker
        m2 = '  const [positions, setPositions] = useState<AutoRobomlmPosition[]>([]);'
        if m2 in content:
            content = content.replace(
                m2,
                m2 + '''
  const [manualSymbol, setManualSymbol] = useState("");
  const [manualDirection, setManualDirection] = useState<"LONG" | "SHORT">("LONG");
  const [manualQty, setManualQty] = useState("");''',
                1,
            )
            applied.append("2a: manual state added (fallback)")
        else:
            skipped.append("2a: state marker not found")

# ==================================================================
# FIX 2b — Add manual trade handler
# ==================================================================
if "handleManualTrade" in content:
    skipped.append("2b: manual handler already exists")
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
        `Open ${direction} trade on ${sym}?\\n\\n` +
        `Entry: market price\\nSL/TP: auto-calculated\\n` +
        `Quantity: auto-allocated (${manualQty || "default"})`,
      );
      if (!confirmed) return;
      await withBusy(
        () => takeOpportunity(sym, direction, "MANUAL", undefined, pendingMinGrade),
        `Manual ${direction} ${sym}`,
      );
    },
    [withBusy, manualSymbol, manualQty, pendingMinGrade],
  );

  const handleClosePosition = useCallback('''
    if marker in content:
        content = content.replace(marker, handler, 1)
        applied.append("2b: handleManualTrade added")
    else:
        skipped.append("2b: close handler marker not found")

# ==================================================================
# FIX 2c — Add Manual Trade panel JSX before "Available opportunities"
# ==================================================================
if 'className="auto-manual-panel"' in content:
    skipped.append("2c: manual panel already exists")
else:
    # Find the "ACTIVE TRADES" section start (before NEXT BEST)
    marker = '''      {/* NEXT BEST OPPORTUNITIES */}'''
    if marker not in content:
        marker = '<section className="auto-panel">\n        <div className="auto-panel-head">\n          <div>\n            <span className="auto-eyebrow">NEXT BEST</span>'

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

          <div className="auto-manual-input-group">
            <label className="auto-manual-label">Quantity</label>
            <input
              type="text"
              className="auto-manual-input"
              placeholder="auto (from capital)"
              value={manualQty}
              onChange={(e) => setManualQty(e.target.value)}
              disabled={busy}
            />
          </div>

          <div className="auto-manual-actions">
            <button
              type="button"
              className="auto-btn auto-manual-btn auto-manual-btn-buy"
              onClick={() => handleManualTrade("LONG")}
              disabled={busy || !manualSymbol.trim()}
              title="Open LONG position at market price"
            >
              <span className="auto-manual-btn-arrow">&#x2191;</span>
              BUY / LONG
            </button>

            <button
              type="button"
              className="auto-btn auto-manual-btn auto-manual-btn-sell"
              onClick={() => handleManualTrade("SHORT")}
              disabled={busy || !manualSymbol.trim()}
              title="Open SHORT position at market price"
            >
              <span className="auto-manual-btn-arrow">&#x2193;</span>
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

    # Try inserting before NEXT BEST section
    if marker in content:
        content = content.replace(marker, manual_panel + marker, 1)
        applied.append("2c: manual trade panel added")
    else:
        skipped.append("2c: NEXT BEST marker not found")

TSX.write_text(content, encoding="utf-8")

# ==================================================================
# FIX 3 — CSS for manual panel + direction badges
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
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.auto-manual-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.auto-manual-input:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.auto-manual-input::placeholder {
  color: #475569;
  font-weight: 400;
}

.auto-manual-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 4px;
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
  gap: 8px !important;
  transition: all 0.15s ease !important;
  border: 1px solid transparent !important;
}

.auto-manual-btn-arrow {
  font-size: 18px;
  font-weight: 900;
}

.auto-manual-btn-buy {
  background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
  color: #ffffff !important;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
}

.auto-manual-btn-buy:hover:not(:disabled) {
  background: linear-gradient(135deg, #047857 0%, #059669 100%) !important;
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
  transform: translateY(-1px);
}

.auto-manual-btn-sell {
  background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%) !important;
  color: #ffffff !important;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.25);
}

.auto-manual-btn-sell:hover:not(:disabled) {
  background: linear-gradient(135deg, #b91c1c 0%, #dc2626 100%) !important;
  box-shadow: 0 6px 16px rgba(239, 68, 68, 0.4);
  transform: translateY(-1px);
}

.auto-manual-btn:disabled {
  opacity: 0.4 !important;
  cursor: not-allowed !important;
  box-shadow: none !important;
  transform: none !important;
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
        applied.append("3: manual panel + direction badges css")

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
print(f"UPDATED: {TSX}")
print()
print("Next:")
print("  cd C:\\Users\\Administrator\\ROBOMLM_PLUS\\frontend")
print("  npx tsc --noEmit")
print("  Ctrl+Shift+R in browser")