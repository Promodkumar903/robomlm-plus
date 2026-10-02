"""
AutoROBOMLM comprehensive fix:
  1. Backend: add POST /api/autorobomlm/manual endpoint
  2. Frontend: fix unicode button labels
  3. Frontend: add takeOpportunity() API
  4. Frontend: wire Take button
"""
from pathlib import Path
import shutil
import re
from datetime import datetime

API_ROUTER = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\api\v1\autorobomlm_api.py")
FRONTEND_CLIENT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\src\api\autorobomlm.ts")
FRONTEND_PAGE = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\autorobomlm\index.tsx")

applied = []
skipped = []

# ============================================================
# PART 1 — Backend: add /manual endpoint
# ============================================================
if API_ROUTER.exists():
    content = API_ROUTER.read_text(encoding="utf-8")

    if "/manual" in content and "def manual_trade" in content:
        skipped.append("backend: /manual already exists")
    else:
        # Backup
        backup = API_ROUTER.with_suffix(
            f".py.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        shutil.copy2(API_ROUTER, backup)

        # Add manual endpoint right before __all__
        manual_block = '''


@router.post("/manual")
def manual_trade(payload: dict = Body(...)) -> dict:
    """
    Manual trade: user explicitly clicks Take on an opportunity.

    Bypasses grade gate (user chose it) but still goes through:
      - objective gate
      - resource gate
      - constraint gate
      - capital allocator
      - SL/TP calculator
      - paper broker

    Body:
        {
            "symbol": "BTC/USDT",
            "direction": "LONG"   # or "SHORT"
        }
    """
    _ensure_state()

    symbol = str(payload.get("symbol") or "").strip()
    direction_raw = str(payload.get("direction") or "").strip().upper()

    if not symbol:
        raise HTTPException(status_code=400, detail="symbol is required")

    if direction_raw not in {"LONG", "SHORT", "BUY", "SELL"}:
        raise HTTPException(
            status_code=400,
            detail=(
                "direction must be LONG/SHORT/BUY/SELL. "
                "NEUTRAL is not tradeable."
            ),
        )

    trade_direction = (
        "BUY" if direction_raw in {"LONG", "BUY"} else "SELL"
    )

    loop = _state["loop"]
    if loop is None:
        raise HTTPException(status_code=500, detail="loop not initialized")

    price = loop._price_for(symbol)
    if price is None:
        raise HTTPException(
            status_code=400,
            detail=f"No market price available for {symbol}",
        )

    # SL/TP
    from app.autorobomlm.sl_tp_calculator import (
        TradeDirection as SLTPDirection,
        calculate_sl_tp,
    )

    sl_tp = calculate_sl_tp(
        direction=SLTPDirection(trade_direction),
        entry_price=price,
        sl_atr_multiplier=loop.config.sl_atr_multiplier,
        tp_atr_multiplier=loop.config.tp_atr_multiplier,
    )
    if sl_tp.stop_loss is None:
        raise HTTPException(
            status_code=500, detail="SL/TP calculation failed"
        )

    # Allocation
    from app.autorobomlm.capital_allocator import allocate_capital

    try:
        capital = float(loop.capital_provider())
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"capital error: {exc}"
        )

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
        )

    # Fill
    from app.autorobomlm.paper_broker import TradeDirection as BrokerDirection

    fill = loop.broker.open_position(
        symbol=symbol,
        direction=BrokerDirection(trade_direction),
        quantity=allocation.quantity,
        stop_loss=sl_tp.stop_loss,
        take_profit=sl_tp.take_profit,
    )

    if fill.position is None:
        raise HTTPException(
            status_code=400,
            detail="Fill rejected: " + (fill.reason or "unknown"),
        )

    return {
        "ok": True,
        "action": "manual_trade",
        "position": fill.position.to_dict(current_price=price),
        "fill_price": fill.fill_price,
        "reason": fill.reason,
    }


'''

        # Insert before __all__
        marker = "\n\n__all__ = [\"router\"]"
        if marker in content:
            content = content.replace(
                marker,
                manual_block + "__all__ = [\"router\"]",
                1,
            )
            API_ROUTER.write_text(content, encoding="utf-8")
            applied.append("backend: /manual endpoint added")
        else:
            skipped.append("backend: __all__ marker not found")

# ============================================================
# PART 2 — Frontend client: add takeOpportunity()
# ============================================================
if FRONTEND_CLIENT.exists():
    content = FRONTEND_CLIENT.read_text(encoding="utf-8")

    if "takeOpportunity" in content:
        skipped.append("client: takeOpportunity already exists")
    else:
        backup = FRONTEND_CLIENT.with_suffix(
            f".ts.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        shutil.copy2(FRONTEND_CLIENT, backup)

        take_fn = '''

// ============================================================
// Manual Trade
// ============================================================

export interface ManualTradeResponse {
  ok: boolean;
  action: "manual_trade";
  position?: AutoRobomlmPosition;
  fill_price?: number;
  reason?: string;
}

export async function takeOpportunity(
  symbol: string,
  direction: "LONG" | "SHORT" | "BUY" | "SELL",
): Promise<ManualTradeResponse> {
  return post<ManualTradeResponse>(`${BASE}/manual`, {
    symbol,
    direction,
  });
}
'''

        content = content.rstrip() + take_fn + "\n"
        FRONTEND_CLIENT.write_text(content, encoding="utf-8")
        applied.append("client: takeOpportunity() added")

# ============================================================
# PART 3 — Frontend page: unicode buttons + wire Take
# ============================================================
if FRONTEND_PAGE.exists():
    content = FRONTEND_PAGE.read_text(encoding="utf-8")

    backup = FRONTEND_PAGE.with_suffix(
        f".tsx.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    shutil.copy2(FRONTEND_PAGE, backup)

    # --- Fix 3a: unicode button labels ---
    unicode_map = {
        '{"\\u25B6 Start"}': '"Start"',
        '{busy ? "..." : "\\u25B6 Start"}': '{busy ? "..." : "Start"}',
        '\\u25B6 Start': 'Start',
        '\\u23F8 Stop': 'Stop',
        '\\u21BB Tick': 'Tick',
        '\\u27F2 Resume': 'Resume',
    }

    fixed_count = 0
    for old, new in unicode_map.items():
        if old in content:
            content = content.replace(old, new)
            fixed_count += 1

    if fixed_count > 0:
        applied.append(f"page: fixed {fixed_count} unicode escapes")

    # --- Fix 3b: import takeOpportunity ---
    if "takeOpportunity" not in content.split("from \"../src/api/autorobomlm\"")[0]:
        old_imp = '''  runTick,
  updateConfig,
  type AutoRobomlmPosition,
} from "../src/api/autorobomlm";'''
        new_imp = '''  runTick,
  updateConfig,
  takeOpportunity,
  type AutoRobomlmPosition,
} from "../src/api/autorobomlm";'''
        if old_imp in content:
            content = content.replace(old_imp, new_imp, 1)
            applied.append("page: takeOpportunity import added")

    # --- Fix 3c: wire Take button handler ---
    old_take = '''                        <button
                          className="auto-btn auto-btn-primary auto-btn-sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            // TODO: backend execute endpoint
                          }}
                        >
                          Take
                        </button>'''

    new_take = '''                        <button
                          className="auto-btn auto-btn-primary auto-btn-sm"
                          disabled={
                            busy ||
                            !opp.direction ||
                            opp.direction.toUpperCase() === "NEUTRAL"
                          }
                          onClick={async (e) => {
                            e.stopPropagation();
                            if (
                              !opp.direction ||
                              opp.direction.toUpperCase() === "NEUTRAL"
                            ) {
                              return;
                            }
                            const dir = opp.direction.toUpperCase();
                            if (dir !== "LONG" && dir !== "SHORT") return;
                            await withBusy(
                              () => takeOpportunity(opp.symbol, dir),
                              `Take ${opp.symbol}`,
                            );
                          }}
                        >
                          Take
                        </button>'''

    if "takeOpportunity(opp.symbol" in content:
        skipped.append("page: Take button already wired")
    elif old_take in content:
        content = content.replace(old_take, new_take, 1)
        applied.append("page: Take button wired")
    else:
        skipped.append("page: Take button pattern not found")

    FRONTEND_PAGE.write_text(content, encoding="utf-8")

# ============================================================
# Report
# ============================================================
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
print()
print("Then restart backend (Ctrl+C in uvicorn terminal, then:)")
print("  cd C:\\Users\\Administrator\\ROBOMLM_PLUS")
print("  python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000")