"""Add manual trade panel JSX (only missing piece)"""
from pathlib import Path
import shutil
from datetime import datetime

TSX = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\autorobomlm\index.tsx")

if not TSX.exists():
    print(f"ERROR: {TSX} not found")
    raise SystemExit(1)

content = TSX.read_text(encoding="utf-8")

if "auto-manual-panel" in content:
    print("Manual panel JSX already present.")
    raise SystemExit(0)

backup = TSX.with_suffix(f".tsx.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(TSX, backup)
print(f"BACKUP: {backup}")

# Anchor: the NEXT BEST section comment
marker = "      {/* NEXT BEST OPPORTUNITIES */}"

if marker not in content:
    print("ERROR: NEXT BEST marker not found")
    print("Searching for alternative markers...")

    # Try the eyebrow span
    alt = '<span className="auto-eyebrow">NEXT BEST</span>'
    if alt in content:
        # Find the section opening before this
        idx = content.find(alt)
        # Find nearest <section before this
        s_idx = content.rfind("<section", 0, idx)
        if s_idx > 0:
            marker = None
            insert_at = s_idx
            print(f"  Using <section at position {s_idx}")
        else:
            print("ERROR: cannot locate section")
            raise SystemExit(1)
    else:
        print("ERROR: no anchor found")
        raise SystemExit(1)
else:
    insert_at = content.find(marker)

# Manual panel JSX
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

if marker:
    content = content.replace(marker, manual_panel + marker, 1)
    print(f"Inserted before: {marker[:50]}")
else:
    content = content[:insert_at] + manual_panel + content[insert_at:]
    print(f"Inserted at position: {insert_at}")

TSX.write_text(content, encoding="utf-8")
print()
print("DONE. Manual panel added.")
print()
print("Next:")
print("  cd C:\\Users\\Administrator\\ROBOMLM_PLUS\\frontend")
print("  npx tsc --noEmit")
print("  Ctrl+Shift+R in browser")