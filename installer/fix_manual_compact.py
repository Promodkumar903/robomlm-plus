"""
Redesign manual panel:
  - Compact horizontal layout
  - Add quantity input
  - Smaller buttons
  - Backend accepts quantity override
"""
from pathlib import Path
import shutil
from datetime import datetime

TSX = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\autorobomlm\index.tsx")
CSS = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\autorobomlm\autorobomlm.css")
API = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\api\v1\autorobomlm_api.py")

TS = datetime.now().strftime('%Y%m%d_%H%M%S')
applied = []
skipped = []

# ==================================================================
# 1. Backend — accept quantity_override in /manual
# ==================================================================
if API.exists():
    api_content = API.read_text(encoding="utf-8")
    api_backup = API.with_suffix(f".py.bak_{TS}")
    shutil.copy2(API, api_backup)

    if "quantity_override" in api_content:
        skipped.append("1: quantity_override already exists")
    else:
        # Find where allocation happens
        old_alloc = '''    allocation = allocate_capital(
        capital=capital,
        entry_price=price,
        stop_loss=sl_tp.stop_loss,
        risk_per_trade_pct=loop.config.risk_per_trade_pct,
        max_position_pct=loop.config.max_position_pct,
    )
    if allocation.quantity is None:
        raise HTTPException(
            status_code=400,
            detail="Allocation failed: "
            + "; ".join(allocation.errors or allocation.reasons),
        )'''

        new_alloc = '''    # Quantity override from caller
    quantity_override = payload.get("quantity")
    override_qty: Optional[float] = None
    if quantity_override is not None:
        try:
            q = float(quantity_override)
            if q > 0:
                override_qty = q
        except (TypeError, ValueError):
            pass

    if override_qty is not None:
        # Build a synthetic allocation result
        from app.autorobomlm.capital_allocator import AllocationResult, AllocatorStatus
        allocation = AllocationResult(
            status=AllocatorStatus.VALID,
            quantity=override_qty,
            position_value=override_qty * price,
            risk_amount=abs(price - sl_tp.stop_loss) * override_qty,
            stop_distance=abs(price - sl_tp.stop_loss),
            stop_distance_pct=(abs(price - sl_tp.stop_loss) / price * 100.0),
            capped_by_max_position=False,
            reasons=(f"Manual quantity override: {override_qty}",),
        )
    else:
        allocation = allocate_capital(
            capital=capital,
            entry_price=price,
            stop_loss=sl_tp.stop_loss,
            risk_per_trade_pct=loop.config.risk_per_trade_pct,
            max_position_pct=loop.config.max_position_pct,
        )
        if allocation.quantity is None:
            raise HTTPException(
                status_code=400,
                detail="Allocation failed: "
                + "; ".join(allocation.errors or allocation.reasons),
            )'''

        if old_alloc in api_content:
            api_content = api_content.replace(old_alloc, new_alloc, 1)
            applied.append("1: backend accepts quantity override")
        else:
            skipped.append("1: allocation block not found")

        # Make sure Optional is imported (usually already is)
        if "from typing import" in api_content and "Optional" not in api_content.split("from typing import")[1].split("\n")[0]:
            # Skip — Optional is imported via `from typing import Any, Optional` typically
            pass

    API.write_text(api_content, encoding="utf-8")

# ==================================================================
# 2. TSX — Redesign panel + quantity state
# ==================================================================
if not TSX.exists():
    print(f"ERROR: {TSX} not found")
    raise SystemExit(1)

content = TSX.read_text(encoding="utf-8")
backup = TSX.with_suffix(f".tsx.bak_{TS}")
shutil.copy2(TSX, backup)
print(f"BACKUP: {backup}")

# 2a. Add manualQty state if missing
if "const [manualQty" in content:
    skipped.append("2a: manualQty state exists")
else:
    marker = '  const [manualSymbol, setManualSymbol] = useState("");'
    if marker in content:
        content = content.replace(
            marker,
            marker + '\n  const [manualQty, setManualQty] = useState("");',
            1,
        )
        applied.append("2a: manualQty state added")
    else:
        skipped.append("2a: manualSymbol state not found")

# 2b. Update handleManualTrade to pass quantity
old_handler = '''  const handleManualTrade = useCallback(
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
  );'''

new_handler = '''  const handleManualTrade = useCallback(
    async (direction: "LONG" | "SHORT") => {
      const sym = manualSymbol.trim().toUpperCase();
      if (!sym) {
        alert("Enter a symbol first (e.g. BTC/USDT)");
        return;
      }

      // Parse quantity (optional)
      let qty: number | undefined;
      const qtyRaw = manualQty.trim();
      if (qtyRaw) {
        const parsed = Number(qtyRaw);
        if (!Number.isFinite(parsed) || parsed <= 0) {
          alert("Quantity must be a positive number (or empty for auto).");
          return;
        }
        qty = parsed;
      }

      const confirmed = confirm(
        qty !== undefined
          ? `Open ${direction} ${qty} x ${sym} at market price?`
          : `Open ${direction} ${sym} (auto quantity) at market price?`,
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
            qty,
          ),
        `Manual ${direction} ${sym}`,
      );
    },
    [withBusy, manualSymbol, manualQty, pendingMinGrade],
  );'''

if "qty: number | undefined" in content:
    skipped.append("2b: handler already has qty")
elif old_handler in content:
    content = content.replace(old_handler, new_handler, 1)
    applied.append("2b: handler passes quantity")
else:
    skipped.append("2b: old handler pattern not found")

# 2c. Replace the whole manual panel JSX with compact layout
old_panel_start = "      {/* MANUAL TRADE PANEL */}"
old_panel_end = "      {/* NEXT BEST OPPORTUNITIES */}"

sidx = content.find(old_panel_start)
eidx = content.find(old_panel_end)

if sidx < 0 or eidx < 0:
    skipped.append("2c: manual panel markers not found")
else:
    new_panel = '''      {/* MANUAL TRADE PANEL */}
      <section className="auto-panel auto-manual-panel">
        <div className="auto-panel-head">
          <div>
            <span className="auto-eyebrow">MANUAL</span>
            <h2>Manual trade</h2>
          </div>
        </div>

        <div className="auto-manual-row">
          <div className="auto-manual-input-group">
            <label className="auto-manual-label">Symbol</label>
            <input
              type="text"
              className="auto-manual-input"
              placeholder="BTC/USDT"
              value={manualSymbol}
              onChange={(e) =>
                setManualSymbol(e.target.value.toUpperCase())
              }
              disabled={busy}
            />
          </div>

          <div className="auto-manual-input-group auto-manual-qty-group">
            <label className="auto-manual-label">Quantity</label>
            <input
              type="text"
              className="auto-manual-input"
              placeholder="auto"
              value={manualQty}
              onChange={(e) => setManualQty(e.target.value)}
              disabled={busy}
            />
          </div>

          <div className="auto-manual-btns">
            <button
              type="button"
              className="auto-manual-btn auto-manual-btn-buy"
              onClick={() => handleManualTrade("LONG")}
              disabled={busy || !manualSymbol.trim()}
              title="Open LONG position"
            >
              BUY
            </button>

            <button
              type="button"
              className="auto-manual-btn auto-manual-btn-sell"
              onClick={() => handleManualTrade("SHORT")}
              disabled={busy || !manualSymbol.trim()}
              title="Open SHORT position"
            >
              SELL
            </button>
          </div>
        </div>

        <p className="auto-manual-hint">
          Leave quantity empty for auto (1% risk sizing) · Manual trades still
          pass all gates except grade.
        </p>
      </section>

'''
    content = content[:sidx] + new_panel + content[eidx:]
    applied.append("2c: compact manual panel JSX")

TSX.write_text(content, encoding="utf-8")

# ==================================================================
# 3. Client — takeOpportunity accepts quantity
# ==================================================================
CLIENT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\src\api\autorobomlm.ts")
if CLIENT.exists():
    cl_content = CLIENT.read_text(encoding="utf-8")
    cl_backup = CLIENT.with_suffix(f".ts.bak_{TS}")
    shutil.copy2(CLIENT, cl_backup)

    old_fn = '''export async function takeOpportunity(
  symbol: string,
  direction: "LONG" | "SHORT" | "BUY" | "SELL",
  entryGrade?: string,
  entryScore?: number,
  minGrade?: string,
): Promise<ManualTradeResponse> {
  return post<ManualTradeResponse>(`${BASE}/manual`, {
    symbol,
    direction,
    entry_grade: entryGrade,
    entry_score: entryScore,
    min_grade: minGrade,
  });
}'''

    new_fn = '''export async function takeOpportunity(
  symbol: string,
  direction: "LONG" | "SHORT" | "BUY" | "SELL",
  entryGrade?: string,
  entryScore?: number,
  minGrade?: string,
  quantity?: number,
): Promise<ManualTradeResponse> {
  const body: Record<string, unknown> = {
    symbol,
    direction,
    entry_grade: entryGrade,
    entry_score: entryScore,
    min_grade: minGrade,
  };
  if (quantity !== undefined) {
    body.quantity = quantity;
  }
  return post<ManualTradeResponse>(`${BASE}/manual`, body);
}'''

    if "quantity?: number," in cl_content:
        skipped.append("3: client already has quantity param")
    elif old_fn in cl_content:
        cl_content = cl_content.replace(old_fn, new_fn, 1)
        CLIENT.write_text(cl_content, encoding="utf-8")
        applied.append("3: client takeOpportunity +quantity")
    else:
        skipped.append("3: client function pattern not found")

# ==================================================================
# 4. CSS — compact layout
# ==================================================================
if CSS.exists():
    css_content = CSS.read_text(encoding="utf-8")
    css_backup = CSS.with_suffix(f".css.bak_{TS}")
    shutil.copy2(CSS, css_backup)

    # Remove old bulky rules and add compact
    if ".auto-manual-row" in css_content:
        skipped.append("4: compact css already exists")
    else:
        css_add = '''

/* ============================================================
   MANUAL TRADE PANEL — COMPACT
   ============================================================ */

.auto-manual-panel {
  padding: 18px 20px;
}

.auto-manual-row {
  display: grid;
  grid-template-columns: 1.6fr 1fr auto;
  gap: 12px;
  align-items: end;
}

.auto-manual-input-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.auto-manual-qty-group {
  max-width: 140px;
}

.auto-manual-label {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: #94a3b8;
}

.auto-manual-input {
  width: 100%;
  padding: 9px 12px;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 6px;
  color: #e2e8f0;
  font-size: 13px;
  font-weight: 600;
  outline: none;
}

.auto-manual-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15);
}

.auto-manual-input:disabled {
  opacity: 0.5;
}

.auto-manual-input::placeholder {
  color: #475569;
  font-weight: 400;
}

.auto-manual-btns {
  display: flex;
  gap: 8px;
  padding-bottom: 1px;
}

.auto-manual-btn {
  padding: 10px 18px !important;
  font-size: 12px !important;
  font-weight: 800 !important;
  letter-spacing: 0.6px !important;
  border-radius: 6px !important;
  border: 1px solid transparent !important;
  cursor: pointer;
  transition: all 0.15s ease;
  min-width: 80px;
}

.auto-manual-btn-buy {
  background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
  color: #ffffff !important;
}

.auto-manual-btn-buy:hover:not(:disabled) {
  background: linear-gradient(135deg, #047857 0%, #059669 100%) !important;
}

.auto-manual-btn-sell {
  background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%) !important;
  color: #ffffff !important;
}

.auto-manual-btn-sell:hover:not(:disabled) {
  background: linear-gradient(135deg, #b91c1c 0%, #dc2626 100%) !important;
}

.auto-manual-btn:disabled {
  opacity: 0.4 !important;
  cursor: not-allowed !important;
}

.auto-manual-hint {
  margin: 10px 0 0;
  font-size: 11px;
  color: #64748b;
  line-height: 1.5;
}

@media (max-width: 900px) {
  .auto-manual-row {
    grid-template-columns: 1fr;
  }
  .auto-manual-qty-group {
    max-width: 100%;
  }
  .auto-manual-btns {
    justify-content: stretch;
  }
  .auto-manual-btn {
    flex: 1;
  }
}
'''
        css_content = css_content.rstrip() + css_add + "\n"
        CSS.write_text(css_content, encoding="utf-8")
        applied.append("4: compact CSS added")

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
print("  1. Backend auto-reload (watch uvicorn terminal)")
print("  2. cd C:\\Users\\Administrator\\ROBOMLM_PLUS\\frontend")
print("     npx tsc --noEmit")
print("  3. Ctrl+Shift+R in browser")