"""
Complete execution loop:
  1. Position.entry_source field (MANUAL | AUTOROBOMLM)
  2. Manual endpoint sets entry_source
  3. Auto loop sets entry_source
  4. Close endpoint (single)
  5. Close-all endpoint
  6. Portfolio tracker: win rate per source
  7. Frontend Close button + Close-all wiring
  8. Tight-SL testing tool
"""
from pathlib import Path
import shutil
from datetime import datetime

ROOT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\autorobomlm")
API = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\api\v1\autorobomlm_api.py")
TSX = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\autorobomlm\index.tsx")
CLIENT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\src\api\autorobomlm.ts")

TS = datetime.now().strftime('%Y%m%d_%H%M%S')
applied = []
skipped = []

# ==================================================================
# 1. Position — add entry_source field
# ==================================================================
BROKER = ROOT / "paper_broker.py"
if BROKER.exists():
    content = BROKER.read_text(encoding="utf-8")
    backup = BROKER.with_suffix(f".py.bak_{TS}")
    shutil.copy2(BROKER, backup)

    if "entry_source" in content:
        skipped.append("1: entry_source already in broker")
    else:
        old = "    entry_grade: Optional[str] = None\n    entry_score: Optional[float] = None\n    opened_at: datetime"
        new = "    entry_grade: Optional[str] = None\n    entry_score: Optional[float] = None\n    entry_source: Optional[str] = None\n    opened_at: datetime"
        if old in content:
            content = content.replace(old, new, 1)
            applied.append("1a: Position.entry_source added")
        else:
            skipped.append("1a: Position field marker not found")

        # to_dict
        old_dict = '''            "entry_grade": self.entry_grade,
            "entry_score": self.entry_score,
            "opened_at": self.opened_at.isoformat(),'''
        new_dict = '''            "entry_grade": self.entry_grade,
            "entry_score": self.entry_score,
            "entry_source": self.entry_source,
            "opened_at": self.opened_at.isoformat(),'''
        if old_dict in content:
            content = content.replace(old_dict, new_dict, 1)
            applied.append("1b: to_dict includes entry_source")

        # open_position signature
        old_sig = '''        entry_grade: Optional[str] = None,
        entry_score: Optional[float] = None,
    ) -> FillResult:'''
        new_sig = '''        entry_grade: Optional[str] = None,
        entry_score: Optional[float] = None,
        entry_source: Optional[str] = None,
    ) -> FillResult:'''
        if old_sig in content:
            content = content.replace(old_sig, new_sig, 1)
            applied.append("1c: open_position accepts entry_source")

        # Position() call
        old_pos = '''            entry_grade=entry_grade,
            entry_score=entry_score,
        )'''
        new_pos = '''            entry_grade=entry_grade,
            entry_score=entry_score,
            entry_source=entry_source,
        )'''
        if old_pos in content:
            content = content.replace(old_pos, new_pos, 1)
            applied.append("1d: Position() passes entry_source")

        BROKER.write_text(content, encoding="utf-8")

# ==================================================================
# 2. Portfolio tracker — add source to ClosedTrade + per-source stats
# ==================================================================
PORTFOLIO = ROOT / "portfolio_tracker.py"
if PORTFOLIO.exists():
    content = PORTFOLIO.read_text(encoding="utf-8")
    backup = PORTFOLIO.with_suffix(f".py.bak_{TS}")
    shutil.copy2(PORTFOLIO, backup)

    if "entry_source" in content:
        skipped.append("2: portfolio already has entry_source")
    else:
        # Add field to ClosedTrade
        old = "    entry_grade: Optional[str]\n    entry_score: Optional[float]\n    exit_reason: str"
        new = "    entry_grade: Optional[str]\n    entry_score: Optional[float]\n    entry_source: Optional[str]\n    exit_reason: str"
        if old in content:
            content = content.replace(old, new, 1)
            applied.append("2a: ClosedTrade.entry_source added")

        # Add to record_close
        old_rec = '''            entry_grade=getattr(position, "entry_grade", None),
            entry_score=getattr(position, "entry_score", None),
            exit_reason=str('''
        new_rec = '''            entry_grade=getattr(position, "entry_grade", None),
            entry_score=getattr(position, "entry_score", None),
            entry_source=getattr(position, "entry_source", None),
            exit_reason=str('''
        if old_rec in content:
            content = content.replace(old_rec, new_rec, 1)
            applied.append("2b: record_close captures entry_source")

        # Add to _load
        old_load = '''                        entry_grade=t.get("entry_grade"),
                        entry_score=t.get("entry_score"),
                        exit_reason=t.get("exit_reason", ""),'''
        new_load = '''                        entry_grade=t.get("entry_grade"),
                        entry_score=t.get("entry_score"),
                        entry_source=t.get("entry_source"),
                        exit_reason=t.get("exit_reason", ""),'''
        if old_load in content:
            content = content.replace(old_load, new_load, 1)
            applied.append("2c: _load restores entry_source")

        # Add per-source breakdown to summary
        old_summary_end = '''            "max_loss": round(
                min((t.pnl for t in trades), default=0.0), 6
            ),
        }'''
        new_summary_end = '''            "max_loss": round(
                min((t.pnl for t in trades), default=0.0), 6
            ),
            "by_source": _stats_by_source(trades),
        }'''

        if old_summary_end in content and "by_source" not in content:
            content = content.replace(old_summary_end, new_summary_end, 1)
            applied.append("2d: summary has by_source breakdown")

        # Add helper function
        helper = '''

def _stats_by_source(trades):
    """Group trade stats by entry_source."""
    groups = {}
    for t in trades:
        src = (t.entry_source or "UNKNOWN").upper()
        groups.setdefault(src, []).append(t)

    out = {}
    for src, items in groups.items():
        wins = [t for t in items if t.pnl > 0]
        losses = [t for t in items if t.pnl < 0]
        gross_profit = sum(t.pnl for t in wins)
        gross_loss = abs(sum(t.pnl for t in losses))
        total = len(items)

        out[src] = {
            "trades_total": total,
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": round(
                len(wins) / total * 100.0, 4
            ) if total else 0.0,
            "realized_pnl": round(
                sum(t.pnl for t in items), 6
            ),
            "avg_win": round(
                gross_profit / len(wins), 6
            ) if wins else 0.0,
            "avg_loss": round(
                -gross_loss / len(losses), 6
            ) if losses else 0.0,
            "profit_factor": round(
                gross_profit / gross_loss, 6
            ) if gross_loss > 0 else 0.0,
        }
    return out

'''
        # Insert before __all__
        marker = "\n\n__all__ = ["
        if marker in content and "_stats_by_source" not in content:
            content = content.replace(
                marker, helper + "__all__ = [", 1
            )
            applied.append("2e: _stats_by_source helper added")

        PORTFOLIO.write_text(content, encoding="utf-8")

# ==================================================================
# 3. API endpoints — close, close-all, tight-sl test
# ==================================================================
if not API.exists():
    print(f"ERROR: {API} not found")
    raise SystemExit(1)

content = API.read_text(encoding="utf-8")
backup = API.with_suffix(f".py.bak_{TS}")
shutil.copy2(API, backup)
print(f"BACKUP: {backup}")

# 3a. Manual endpoint — set entry_source
old_manual = '''        stop_loss=sl_tp.stop_loss,
        take_profit=sl_tp.take_profit,
        entry_grade=entry_grade,
        entry_score=(
            float(entry_score) if entry_score is not None else None
        ),
    )'''
new_manual = '''        stop_loss=sl_tp.stop_loss,
        take_profit=sl_tp.take_profit,
        entry_grade=entry_grade,
        entry_score=(
            float(entry_score) if entry_score is not None else None
        ),
        entry_source="MANUAL",
    )'''
if 'entry_source="MANUAL"' in content:
    skipped.append("3a: manual already tags entry_source")
elif old_manual in content:
    content = content.replace(old_manual, new_manual, 1)
    applied.append("3a: manual endpoint tags entry_source")
else:
    skipped.append("3a: manual broker call not found")

# 3b. Add close + close-all + tight-sl endpoints
if "/close-all" in content:
    skipped.append("3b: close endpoints already exist")
else:
    new_endpoints = '''

# ============================================================
# POSITION CLOSE ENDPOINTS
# ============================================================

@router.post("/close")
def close_position(payload: dict = Body(...)) -> dict:
    """
    Manually close a single position.

    Body: {"position_id": "...", "reason": "MANUAL_CLOSE"}
    """
    _ensure_state()

    position_id = str(payload.get("position_id") or "").strip()
    reason = str(payload.get("reason") or "MANUAL_CLOSE")

    if not position_id:
        raise HTTPException(
            status_code=400, detail="position_id is required"
        )

    loop = _state["loop"]
    broker = loop.broker

    existing = broker.get_position(position_id)
    if existing is None:
        raise HTTPException(
            status_code=404,
            detail=f"Position not found: {position_id}",
        )
    if existing.status.value == "CLOSED":
        raise HTTPException(
            status_code=400, detail="Position already closed"
        )

    result = broker.close_position(position_id, reason=reason)
    if result.position is None:
        raise HTTPException(
            status_code=400,
            detail="Close failed: " + (result.reason or "unknown"),
        )

    return {
        "ok": True,
        "action": "close",
        "position": result.position.to_dict(),
        "fill_price": result.fill_price,
        "reason": result.reason,
    }


@router.post("/close-all")
def close_all_positions(payload: dict = Body(default={})) -> dict:
    """
    Close ALL open positions. Emergency control.

    Body (optional): {"reason": "EMERGENCY_CLOSE"}
    """
    _ensure_state()

    reason = str(payload.get("reason") or "CLOSE_ALL")

    loop = _state["loop"]
    broker = loop.broker

    open_positions = list(broker.get_open_positions())
    results = []
    failed = []

    for pos in open_positions:
        res = broker.close_position(pos.position_id, reason=reason)
        if res.position is not None:
            results.append(
                {
                    "position_id": pos.position_id,
                    "symbol": pos.symbol,
                    "pnl": res.position.pnl(
                        res.fill_price or pos.entry_price
                    ),
                    "fill_price": res.fill_price,
                }
            )
        else:
            failed.append(
                {
                    "position_id": pos.position_id,
                    "reason": res.reason or "unknown",
                }
            )

    return {
        "ok": True,
        "action": "close_all",
        "closed_count": len(results),
        "failed_count": len(failed),
        "closed": results,
        "failed": failed,
    }


# ============================================================
# TESTING TOOL — tight SL for auto-exit validation
# ============================================================

@router.post("/debug/tight-sl")
def debug_tight_sl(payload: dict = Body(...)) -> dict:
    """
    Open a position with a very tight stop-loss (0.1% away)
    so the auto-loop should close it within seconds.

    Body: {"symbol": "BTC/USDT", "direction": "LONG"}
    """
    _ensure_state()

    symbol = str(payload.get("symbol") or "BTC/USDT").strip()
    direction_raw = str(payload.get("direction") or "LONG").strip().upper()

    if direction_raw not in {"LONG", "SHORT", "BUY", "SELL"}:
        raise HTTPException(
            status_code=400, detail="direction must be LONG/SHORT"
        )

    trade_direction = (
        "BUY" if direction_raw in {"LONG", "BUY"} else "SELL"
    )

    loop = _state["loop"]
    broker = loop.broker

    price = loop._price_for(symbol)
    if price is None:
        raise HTTPException(
            status_code=400, detail=f"No price for {symbol}"
        )

    # Tight SL: 0.1% from entry
    tight_distance = price * 0.001

    if trade_direction == "BUY":
        stop_loss = price - tight_distance
        take_profit = price + tight_distance * 5
    else:
        stop_loss = price + tight_distance
        take_profit = price - tight_distance * 5

    # Small qty so risk is trivial
    qty = 0.001

    fill = broker.open_position(
        symbol=symbol,
        direction=broker._open_position_direction(trade_direction)
        if hasattr(broker, "_open_position_direction")
        else __import__(
            "app.autorobomlm.paper_broker",
            fromlist=["TradeDirection"],
        ).TradeDirection(trade_direction),
        quantity=qty,
        stop_loss=stop_loss,
        take_profit=take_profit,
        entry_grade="DEBUG",
        entry_score=0.0,
        entry_source="DEBUG",
    )

    if fill.position is None:
        raise HTTPException(
            status_code=400,
            detail="Fill failed: " + (fill.reason or "unknown"),
        )

    return {
        "ok": True,
        "action": "debug_tight_sl",
        "position": fill.position.to_dict(current_price=price),
        "fill_price": fill.fill_price,
        "hint": (
            "SL is ~0.1% away. Start loop or run tick; "
            "auto-exit should close this quickly."
        ),
    }

'''

    marker = '\n\n__all__ = ["router"]'
    if marker in content:
        content = content.replace(
            marker, new_endpoints + '__all__ = ["router"]', 1
        )
        applied.append("3b: close + close-all + tight-sl endpoints added")
    else:
        skipped.append("3b: __all__ marker not found")

API.write_text(content, encoding="utf-8")

# ==================================================================
# 4. Auto loop — tag auto-opened positions as AUTOROBOMLM
# ==================================================================
LOOP = ROOT / "auto_loop.py"
if LOOP.exists():
    loop_content = LOOP.read_text(encoding="utf-8")
    loop_backup = LOOP.with_suffix(f".py.bak_{TS}")
    shutil.copy2(LOOP, loop_backup)

    old_call = '''        fill = self.broker.open_position(
            symbol=symbol,
            direction=TradeDirection(direction),
            quantity=allocation.quantity,
            stop_loss=sl_tp_result.stop_loss,
            take_profit=sl_tp_result.take_profit,
        )'''

    new_call = '''        fill = self.broker.open_position(
            symbol=symbol,
            direction=TradeDirection(direction),
            quantity=allocation.quantity,
            stop_loss=sl_tp_result.stop_loss,
            take_profit=sl_tp_result.take_profit,
            entry_grade=(
                grade_result.grade.value
                if grade_result.grade is not None
                else None
            ),
            entry_score=raw_score,
            entry_source="AUTOROBOMLM",
        )'''

    if 'entry_source="AUTOROBOMLM"' in loop_content:
        skipped.append("4: auto loop already tagged")
    elif old_call in loop_content:
        loop_content = loop_content.replace(old_call, new_call, 1)
        LOOP.write_text(loop_content, encoding="utf-8")
        applied.append("4: auto loop tags AUTOROBOMLM source")
    else:
        skipped.append("4: auto loop open_position call not found")

# ==================================================================
# 5. Frontend client — add closePosition, closeAllPositions
# ==================================================================
if CLIENT.exists():
    content = CLIENT.read_text(encoding="utf-8")
    backup = CLIENT.with_suffix(f".ts.bak_{TS}")
    shutil.copy2(CLIENT, backup)

    if "closePosition" in content:
        skipped.append("5: close API already in client")
    else:
        new_fns = '''

// ============================================================
// Close endpoints
// ============================================================

export interface CloseResponse {
  ok: boolean;
  action: "close";
  position: AutoRobomlmPosition;
  fill_price: number;
  reason: string;
}

export interface CloseAllResponse {
  ok: boolean;
  action: "close_all";
  closed_count: number;
  failed_count: number;
  closed: Array<{
    position_id: string;
    symbol: string;
    pnl: number;
    fill_price: number;
  }>;
  failed: Array<{ position_id: string; reason: string }>;
}

export async function closePosition(
  positionId: string,
  reason: string = "MANUAL_CLOSE",
): Promise<CloseResponse> {
  return post<CloseResponse>(`${BASE}/close`, {
    position_id: positionId,
    reason,
  });
}

export async function closeAllPositions(
  reason: string = "CLOSE_ALL",
): Promise<CloseAllResponse> {
  return post<CloseAllResponse>(`${BASE}/close-all`, { reason });
}
'''
        content = content.rstrip() + new_fns + "\n"
        CLIENT.write_text(content, encoding="utf-8")
        applied.append("5: close + close-all client functions")

# ==================================================================
# 6. Frontend page — Close button + Close-all
# ==================================================================
if TSX.exists():
    content = TSX.read_text(encoding="utf-8")
    backup = TSX.with_suffix(f".tsx.bak_{TS}")
    shutil.copy2(TSX, backup)

    # 6a. Import closePosition / closeAllPositions
    if "closePosition," not in content:
        old_imp = "  takeOpportunity,\n  type AutoRobomlmPosition,"
        new_imp = "  takeOpportunity,\n  closePosition,\n  closeAllPositions,\n  type AutoRobomlmPosition,"
        if old_imp in content:
            content = content.replace(old_imp, new_imp, 1)
            applied.append("6a: close imports added")

    # 6b. Add handlers before return
    if "const handleClosePosition" not in content:
        marker = "  const handleKill = useCallback(async () => {"
        new_handlers = '''  const handleClosePosition = useCallback(
    async (positionId: string, symbol: string) => {
      const confirmed = confirm(
        `Close ${symbol}? Market order at current price.`,
      );
      if (!confirmed) return;
      await withBusy(
        () => closePosition(positionId, "MANUAL_CLOSE"),
        `Close ${symbol}`,
      );
    },
    [withBusy],
  );

  const handleCloseAll = useCallback(async () => {
    const confirmed = confirm(
      "Close ALL open positions at market? This is immediate.",
    );
    if (!confirmed) return;
    await withBusy(() => closeAllPositions("CLOSE_ALL"), "Close all");
  }, [withBusy]);

  const handleKill = useCallback(async () => {'''
        if marker in content:
            content = content.replace(marker, new_handlers, 1)
            applied.append("6b: close handlers added")

    # 6c. Add Close-all button in header (next to Kill)
    if "handleCloseAll" in content and "onClick={handleCloseAll}" not in content:
        old_kill_btn = '''          <button
            type="button"
            className="auto-btn auto-btn-danger"
            onClick={handleKill}
            disabled={busy || killEnabled}
          >
            Kill
          </button>'''
        new_kill_btn = '''          <button
            type="button"
            className="auto-btn auto-btn-ghost"
            onClick={handleCloseAll}
            disabled={busy || positions.length === 0}
            title="Close all open positions"
          >
            Close All
          </button>

          <button
            type="button"
            className="auto-btn auto-btn-danger"
            onClick={handleKill}
            disabled={busy || killEnabled}
          >
            Kill
          </button>'''
        if old_kill_btn in content:
            content = content.replace(old_kill_btn, new_kill_btn, 1)
            applied.append("6c: Close All button added to header")

    # 6d. Wire Close button in Active Trades table
    old_close_btn = '''                      <button className="auto-btn auto-btn-ghost auto-btn-sm">
                        Close
                      </button>'''
    new_close_btn = '''                      <button
                        className="auto-btn auto-btn-ghost auto-btn-sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          void handleClosePosition(
                            trade.id,
                            trade.symbol,
                          );
                        }}
                        disabled={busy}
                      >
                        Close
                      </button>'''
    if "handleClosePosition(trade.id" in content:
        skipped.append("6d: Close button already wired")
    elif old_close_btn in content:
        content = content.replace(old_close_btn, new_close_btn, 1)
        applied.append("6d: Close button wired")

    # 6e. Add Source column to Active trades table
    old_header = '''                  <th>Direction</th>
                  <th>Grade</th>'''
    new_header = '''                  <th>Direction</th>
                  <th>Source</th>
                  <th>Grade</th>'''
    if "<th>Source</th>" in content:
        skipped.append("6e: Source column already exists")
    elif old_header in content:
        content = content.replace(old_header, new_header, 1)
        applied.append("6e: Source header added")

    # 6f. Add source cell to row
    old_dir_cell = '''                    <td>
                      <DirectionBadge direction={trade.direction} />
                    </td>
                    <td>
                      {trade.entryGrade ? ('''
    new_dir_cell = '''                    <td>
                      <DirectionBadge direction={trade.direction} />
                    </td>
                    <td>
                      <span className="auto-source-tag">
                        {trade.entrySource ?? "—"}
                      </span>
                    </td>
                    <td>
                      {trade.entryGrade ? ('''
    if "trade.entrySource" in content:
        skipped.append("6f: source cell already exists")
    elif old_dir_cell in content:
        content = content.replace(old_dir_cell, new_dir_cell, 1)
        applied.append("6f: source cell added")

    # 6g. Extend ActiveTrade interface with entrySource
    old_iface = '''  openedAt: string;
  entryGrade: string | null;
}'''
    new_iface = '''  openedAt: string;
  entryGrade: string | null;
  entrySource: string | null;
}'''
    if "entrySource: string | null;" in content:
        skipped.append("6g: entrySource already in interface")
    elif old_iface in content:
        content = content.replace(old_iface, new_iface, 1)
        applied.append("6g: ActiveTrade.entrySource added")

    # 6h. Map entrySource in useMemo
    old_map = '''        entryGrade: (p as unknown as { entry_grade?: string | null })
          .entry_grade ?? null,
      }));'''
    new_map = '''        entryGrade: (p as unknown as { entry_grade?: string | null })
          .entry_grade ?? null,
        entrySource:
          (p as unknown as { entry_source?: string | null })
            .entry_source ?? null,
      }));'''
    if "entry_source ?? null" in content:
        skipped.append("6h: entrySource map already exists")
    elif old_map in content:
        content = content.replace(old_map, new_map, 1)
        applied.append("6h: entrySource mapped")

    TSX.write_text(content, encoding="utf-8")

# ==================================================================
# 7. CSS — source tag
# ==================================================================
CSS = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\autorobomlm\autorobomlm.css")
if CSS.exists():
    content = CSS.read_text(encoding="utf-8")
    backup = CSS.with_suffix(f".css.bak_{TS}")
    shutil.copy2(CSS, backup)

    if ".auto-source-tag" in content:
        skipped.append("7: css already has source tag")
    else:
        css = '''

.auto-source-tag {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.5px;
  background: rgba(148, 163, 184, 0.15);
  color: #cbd5e1;
}
'''
        content = content.rstrip() + css + "\n"
        CSS.write_text(content, encoding="utf-8")
        applied.append("7: source tag css added")

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
print("  1. Restart backend")
print("  2. cd C:\\Users\\Administrator\\ROBOMLM_PLUS\\frontend")
print("     npx tsc --noEmit")
print("  3. Ctrl+Shift+R in browser")
print()
print("Test flow:")
print("  a) Take BTC/USDT → position opens (source=MANUAL)")
print("  b) Click Close → position closes → P&L recorded")
print("  c) curl /api/autorobomlm/portfolio/summary")
print("     → sees by_source.MANUAL.win_rate")
print("  d) /api/autorobomlm/debug/tight-sl → open tight SL")
print("  e) Start loop → auto-exit closes it (source=DEBUG)")