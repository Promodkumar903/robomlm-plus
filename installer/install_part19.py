"""
Wire grade system: min_grade dropdown + grade badges + entry grade tracking
"""
from pathlib import Path
import shutil
from datetime import datetime

TSX = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\autorobomlm\index.tsx")
CLIENT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\src\api\autorobomlm.ts")
BROKER = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\autorobomlm\paper_broker.py")
API = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\api\v1\autorobomlm_api.py")

applied = []
skipped = []

# ==================================================================
# BACKEND 1 — Add entry_grade to Position dataclass
# ==================================================================
if BROKER.exists():
    content = BROKER.read_text(encoding="utf-8")

    if "entry_grade" in content:
        skipped.append("broker: entry_grade already exists")
    else:
        backup = BROKER.with_suffix(f".py.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        shutil.copy2(BROKER, backup)

        # Add field after take_profit
        old_field = "    take_profit: float\n    opened_at: datetime"
        new_field = "    take_profit: float\n    entry_grade: Optional[str] = None\n    entry_score: Optional[float] = None\n    opened_at: datetime"

        if old_field in content:
            content = content.replace(old_field, new_field, 1)
            BROKER.write_text(content, encoding="utf-8")
            applied.append("broker: entry_grade + entry_score fields added")
        else:
            skipped.append("broker: field marker not found")

# ==================================================================
# BACKEND 2 — Update paper_broker.open_position to accept grade
# ==================================================================
if BROKER.exists():
    content = BROKER.read_text(encoding="utf-8")

    old_sig = '''        quantity: float,
        stop_loss: float,
        take_profit: float,
    ) -> FillResult:'''

    new_sig = '''        quantity: float,
        stop_loss: float,
        take_profit: float,
        entry_grade: Optional[str] = None,
        entry_score: Optional[float] = None,
    ) -> FillResult:'''

    if "entry_grade: Optional[str] = None,\n        entry_score" in content and "open_position" in content:
        skipped.append("broker: open_position signature already updated")
    elif old_sig in content:
        content = content.replace(old_sig, new_sig, 1)

        # Also update Position creation
        old_pos = '''        position = Position(
            position_id=str(uuid4()),
            symbol=symbol,
            direction=direction,
            quantity=float(quantity),
            entry_price=fill_price,
            stop_loss=float(stop_loss),
            take_profit=float(take_profit),
        )'''

        new_pos = '''        position = Position(
            position_id=str(uuid4()),
            symbol=symbol,
            direction=direction,
            quantity=float(quantity),
            entry_price=fill_price,
            stop_loss=float(stop_loss),
            take_profit=float(take_profit),
            entry_grade=entry_grade,
            entry_score=entry_score,
        )'''

        if old_pos in content:
            content = content.replace(old_pos, new_pos, 1)
            BROKER.write_text(content, encoding="utf-8")
            applied.append("broker: open_position stores grade")
        else:
            skipped.append("broker: Position() call not found")
    else:
        skipped.append("broker: open_position signature not found")

# ==================================================================
# BACKEND 3 — Update Position.to_dict to include grade
# ==================================================================
if BROKER.exists():
    content = BROKER.read_text(encoding="utf-8")

    old_dict = '''            "take_profit": self.take_profit,
            "opened_at": self.opened_at.isoformat(),'''

    new_dict = '''            "take_profit": self.take_profit,
            "entry_grade": self.entry_grade,
            "entry_score": self.entry_score,
            "opened_at": self.opened_at.isoformat(),'''

    if '"entry_grade": self.entry_grade' in content:
        skipped.append("broker: to_dict already has grade")
    elif old_dict in content:
        content = content.replace(old_dict, new_dict, 1)
        BROKER.write_text(content, encoding="utf-8")
        applied.append("broker: to_dict includes grade")
    else:
        skipped.append("broker: to_dict marker not found")

# ==================================================================
# BACKEND 4 — Update /manual to accept and validate grade
# ==================================================================
if API.exists():
    content = API.read_text(encoding="utf-8")

    if "def _grade_rank" in content:
        skipped.append("api: grade helpers already exist")
    else:
        backup = API.with_suffix(f".py.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        shutil.copy2(API, backup)

        # Insert grade helpers before router
        grade_helpers = '''

# ============================================================
# GRADE HELPERS
# ============================================================

_GRADE_RANK = {
    "A+": 5,
    "A": 4,
    "B+": 3,
    "B": 2,
    "HOLD": 1,
}


def _classify_grade(score: float) -> str:
    """Classify score into grade band (matches frontend)."""
    try:
        s = float(score)
    except (TypeError, ValueError):
        return "HOLD"
    if s >= 75.0:
        return "A+"
    if s >= 55.0:
        return "A"
    if s >= 45.0:
        return "B+"
    if s >= 30.0:
        return "B"
    return "HOLD"


def _grade_at_least(actual: str, minimum: str) -> bool:
    return _GRADE_RANK.get(actual, 0) >= _GRADE_RANK.get(minimum, 0)


'''

        # Insert before "router = APIRouter"
        marker = "router = APIRouter("
        if marker in content:
            content = content.replace(marker, grade_helpers + marker, 1)
            applied.append("api: grade helpers inserted")
        else:
            skipped.append("api: router marker not found")

        # Update manual_trade signature
        old_sig = '''    symbol = str(payload.get("symbol") or "").strip()
    direction_raw = str(payload.get("direction") or "").strip().upper()'''

        new_sig = '''    symbol = str(payload.get("symbol") or "").strip()
    direction_raw = str(payload.get("direction") or "").strip().upper()

    # Grade info from caller (optional but recommended)
    entry_score = payload.get("entry_score")
    requested_min_grade = str(payload.get("min_grade") or "").strip().upper()

    entry_grade: Optional[str] = None
    if entry_score is not None:
        try:
            entry_grade = _classify_grade(float(entry_score))
        except (TypeError, ValueError):
            entry_grade = None

    # Grade gate: if both known, enforce
    if entry_grade and requested_min_grade in _GRADE_RANK:
        if not _grade_at_least(entry_grade, requested_min_grade):
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Grade {entry_grade} below minimum {requested_min_grade}. "
                    "Manual trade rejected by grade policy."
                ),
            )'''

        if "requested_min_grade" in content:
            skipped.append("api: manual_trade signature already updated")
        elif old_sig in content:
            content = content.replace(old_sig, new_sig, 1)
            applied.append("api: manual_trade grade validation added")
        else:
            skipped.append("api: manual_trade signature not found")

        # Update broker.open_position call to pass grade
        old_call = '''    fill = loop.broker.open_position(
        symbol=symbol,
        direction=BrokerDirection(trade_direction),
        quantity=allocation.quantity,
        stop_loss=sl_tp.stop_loss,
        take_profit=sl_tp.take_profit,
    )'''

        new_call = '''    fill = loop.broker.open_position(
        symbol=symbol,
        direction=BrokerDirection(trade_direction),
        quantity=allocation.quantity,
        stop_loss=sl_tp.stop_loss,
        take_profit=sl_tp.take_profit,
        entry_grade=entry_grade,
        entry_score=(
            float(entry_score) if entry_score is not None else None
        ),
    )'''

        if "entry_grade=entry_grade" in content:
            skipped.append("api: broker call already passes grade")
        elif old_call in content:
            content = content.replace(old_call, new_call, 1)
            applied.append("api: broker call passes grade")
        else:
            skipped.append("api: broker call not found")

        API.write_text(content, encoding="utf-8")

# ==================================================================
# FRONTEND — Add grade helpers, state, dropdown, badges
# ==================================================================
if TSX.exists():
    content = TSX.read_text(encoding="utf-8")
    backup = TSX.with_suffix(f".tsx.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    shutil.copy2(TSX, backup)

    # --- 1. Add types + helpers after AnyRecord ---
    if "type GradeBand" in content:
        skipped.append("tsx: GradeBand type already exists")
    else:
        old_any = "type AnyRecord = Record<string, any>;"
        new_any = '''type AnyRecord = Record<string, any>;

type GradeBand = "A+" | "A" | "B+" | "B" | "HOLD";

const GRADE_RANK: Record<GradeBand, number> = {
  "A+": 5,
  A: 4,
  "B+": 3,
  B: 2,
  HOLD: 1,
};

function computeGrade(score: number | null | undefined): GradeBand {
  if (score === null || score === undefined) return "HOLD";
  const s = Number(score);
  if (!Number.isFinite(s)) return "HOLD";
  if (s >= 75) return "A+";
  if (s >= 55) return "A";
  if (s >= 45) return "B+";
  if (s >= 30) return "B";
  return "HOLD";
}

function gradeAtLeast(actual: GradeBand, minimum: GradeBand): boolean {
  return GRADE_RANK[actual] >= GRADE_RANK[minimum];
}

function gradeTone(g: GradeBand): string {
  if (g === "A+") return "grade-ap";
  if (g === "A") return "grade-a";
  if (g === "B+") return "grade-bp";
  if (g === "B") return "grade-b";
  return "grade-hold";
}'''

        if old_any in content:
            content = content.replace(old_any, new_any, 1)
            applied.append("tsx: grade helpers added")

    # --- 2. Add pendingMinGrade state ---
    if "pendingMinGrade" in content:
        skipped.append("tsx: pendingMinGrade already exists")
    else:
        marker = '  const [pendingMode, setPendingMode] = useState<"DEMO" | "LIVE">("DEMO");'
        if marker in content:
            content = content.replace(
                marker,
                marker + '\n  const [pendingMinGrade, setPendingMinGrade] = useState<GradeBand>("B");',
                1,
            )
            applied.append("tsx: pendingMinGrade state added")

    # --- 3. Sync pendingMinGrade from backend config ---
    if "setPendingMinGrade(" in content and "const pendingMinGrade" in content:
        sync_marker = "  // Sync pendingMode with backend when idle"
        if sync_marker in content:
            sync_add = '''  // Sync pendingMinGrade with backend
  useEffect(() => {
    const cfgMinGrade = ((status as AnyRecord | null)?.config as AnyRecord)
      ?.min_grade as GradeBand | undefined;
    if (cfgMinGrade && !isRunning) {
      setPendingMinGrade(cfgMinGrade);
    }
  }, [status, isRunning]);

  // Sync pendingMode with backend when idle'''
            if "Sync pendingMinGrade" not in content:
                content = content.replace(sync_marker, sync_add, 1)
                applied.append("tsx: pendingMinGrade sync effect")

    # --- 4. handleStart also pushes min_grade ---
    old_config_push = '''          updateConfig({
            execution_mode: pendingMode,
            live_confirmed: pendingMode === "LIVE",
          }),'''

    new_config_push = '''          updateConfig({
            execution_mode: pendingMode,
            live_confirmed: pendingMode === "LIVE",
            min_grade: pendingMinGrade,
          }),'''

    if "min_grade: pendingMinGrade" in content:
        skipped.append("tsx: min_grade already in config push")
    elif old_config_push in content:
        content = content.replace(old_config_push, new_config_push, 1)
        applied.append("tsx: min_grade pushed on Start")

    # --- 5. Add min_grade dropdown next to mode dropdown ---
    if 'className="auto-select auto-select-mode"' in content and 'auto-select-grade' not in content:
        # Find the mode select closing tag
        mode_select_close = '''            <option value="LIVE">LIVE</option>
          </select>'''

        grade_dropdown = '''            <option value="LIVE">LIVE</option>
          </select>

          <select
            className="auto-select auto-select-mode auto-select-grade"
            value={pendingMinGrade}
            onChange={(e) =>
              setPendingMinGrade(e.target.value as GradeBand)
            }
            disabled={busy}
            title="Minimum grade for trades"
          >
            <option value="A+">A+ (75+)</option>
            <option value="A">A (55+)</option>
            <option value="B+">B+ (45+)</option>
            <option value="B">B (30+)</option>
            <option value="HOLD">OFF</option>
          </select>'''

        if mode_select_close in content and "auto-select-grade" not in content:
            content = content.replace(mode_select_close, grade_dropdown, 1)
            applied.append("tsx: min_grade dropdown added")

    # --- 6. Add Grade column to opportunities table ---
    old_opp_header = '''                  <th>Score</th>
                  <th>Why</th>'''
    new_opp_header = '''                  <th>Score</th>
                  <th>Grade</th>
                  <th>Why</th>'''

    if "<th>Grade</th>" in content:
        skipped.append("tsx: Grade header already exists")
    elif old_opp_header in content:
        content = content.replace(old_opp_header, new_opp_header, 1)
        applied.append("tsx: Grade header added to opportunities")

    # --- 7. Add grade cell to opportunity row ---
    old_score_cell = '''                      <td className="auto-reason">{opp.reason}</td>'''
    new_score_cell = '''                      <td>
                        <span
                          className={`auto-grade-badge ${gradeTone(computeGrade(opp.score))}`}
                        >
                          {computeGrade(opp.score)}
                        </span>
                      </td>
                      <td className="auto-reason">{opp.reason}</td>'''

    if "auto-grade-badge" in content:
        skipped.append("tsx: grade badge already in row")
    elif old_score_cell in content and "computeGrade(opp.score)" not in content:
        content = content.replace(old_score_cell, new_score_cell, 1)
        applied.append("tsx: grade badge added to opp rows")

    # --- 8. Disable Take if grade below minimum ---
    old_disabled = '''                          disabled={
                            busy ||
                            !opp.direction ||
                            opp.direction.toUpperCase() === "NEUTRAL"
                          }'''

    new_disabled = '''                          disabled={
                            busy ||
                            !opp.direction ||
                            opp.direction.toUpperCase() === "NEUTRAL" ||
                            !gradeAtLeast(
                              computeGrade(opp.score),
                              pendingMinGrade,
                            )
                          }'''

    if "gradeAtLeast(" in content and "pendingMinGrade," in content:
        skipped.append("tsx: Take already grade-gated")
    elif old_disabled in content:
        content = content.replace(old_disabled, new_disabled, 1)
        applied.append("tsx: Take button grade-gated")

    # --- 9. Pass grade in takeOpportunity call ---
    old_call = "() => takeOpportunity(opp.symbol, dir),"
    new_call = '''() =>
                                takeOpportunity(
                                  opp.symbol,
                                  dir,
                                  computeGrade(opp.score),
                                  opp.score ?? undefined,
                                  pendingMinGrade,
                                ),'''

    if "computeGrade(opp.score)," in content:
        skipped.append("tsx: takeOpportunity already passes grade")
    elif old_call in content:
        content = content.replace(old_call, new_call, 1)
        applied.append("tsx: takeOpportunity passes grade")

    # --- 10. Add Grade column to Active trades table ---
    old_active_header = '''                  <th>Direction</th>
                  <th>Entry</th>'''
    new_active_header = '''                  <th>Direction</th>
                  <th>Grade</th>
                  <th>Entry</th>'''

    if "<th>Grade</th>" in content and content.count("<th>Grade</th>") >= 2:
        skipped.append("tsx: Active trades grade header exists")
    elif old_active_header in content:
        content = content.replace(old_active_header, new_active_header, 1)
        applied.append("tsx: Grade header added to active trades")

    # --- 11. Add grade cell to active trade row ---
    old_active_dir = '''                    <td>
                      <DirectionBadge direction={trade.direction} />
                    </td>
                    <td>{fmtNum(trade.entry)}</td>'''
    new_active_dir = '''                    <td>
                      <DirectionBadge direction={trade.direction} />
                    </td>
                    <td>
                      {trade.entryGrade ? (
                        <span
                          className={`auto-grade-badge ${gradeTone(trade.entryGrade as GradeBand)}`}
                        >
                          {trade.entryGrade}
                        </span>
                      ) : (
                        <span className="auto-muted">—</span>
                      )}
                    </td>
                    <td>{fmtNum(trade.entry)}</td>'''

    if "trade.entryGrade" in content:
        skipped.append("tsx: active trade grade cell exists")
    elif old_active_dir in content:
        content = content.replace(old_active_dir, new_active_dir, 1)
        applied.append("tsx: active trade grade cell added")

    # --- 12. Extend ActiveTrade interface with entryGrade ---
    old_interface = '''  pnl: number | null;
  pnlPct: number | null;
  openedAt: string;
}'''
    new_interface = '''  pnl: number | null;
  pnlPct: number | null;
  openedAt: string;
  entryGrade: string | null;
}'''

    if "entryGrade: string | null;" in content:
        skipped.append("tsx: ActiveTrade.entryGrade already exists")
    elif old_interface in content:
        content = content.replace(old_interface, new_interface, 1)
        applied.append("tsx: ActiveTrade interface extended")

    # --- 13. Map entryGrade in activeTrades useMemo ---
    old_map = '''        pnl: p.pnl ?? null,
        pnlPct: p.pnl_pct ?? null,
        openedAt: p.opened_at,
      }));'''
    new_map = '''        pnl: p.pnl ?? null,
        pnlPct: p.pnl_pct ?? null,
        openedAt: p.opened_at,
        entryGrade: (p as unknown as { entry_grade?: string | null })
          .entry_grade ?? null,
      }));'''

    if "entry_grade ?? null" in content:
        skipped.append("tsx: entryGrade mapping exists")
    elif old_map in content:
        content = content.replace(old_map, new_map, 1)
        applied.append("tsx: entryGrade mapping added")

    TSX.write_text(content, encoding="utf-8")

# ==================================================================
# FRONTEND CLIENT — Update takeOpportunity signature
# ==================================================================
if CLIENT.exists():
    content = CLIENT.read_text(encoding="utf-8")
    backup = CLIENT.with_suffix(f".ts.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    shutil.copy2(CLIENT, backup)

    old_fn = '''export async function takeOpportunity(
  symbol: string,
  direction: "LONG" | "SHORT" | "BUY" | "SELL",
): Promise<ManualTradeResponse> {
  return post<ManualTradeResponse>(`${BASE}/manual`, {
    symbol,
    direction,
  });
}'''

    new_fn = '''export async function takeOpportunity(
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

    if "entry_grade: entryGrade" in content:
        skipped.append("client: takeOpportunity already extended")
    elif old_fn in content:
        content = content.replace(old_fn, new_fn, 1)
        applied.append("client: takeOpportunity extended")
    else:
        skipped.append("client: takeOpportunity signature not matched")

    # Also add entry_grade to position type
    if "entry_grade?: string | null;" not in content:
        old_pos = '''  status: "OPEN" | "CLOSED";
  exit_price: number | null;'''
        new_pos = '''  status: "OPEN" | "CLOSED";
  entry_grade?: string | null;
  entry_score?: number | null;
  exit_price: number | null;'''
        if old_pos in content:
            content = content.replace(old_pos, new_pos, 1)
            applied.append("client: position type extended")

    CLIENT.write_text(content, encoding="utf-8")

# ==================================================================
# CSS — Grade badge styling
# ==================================================================
CSS = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\autorobomlm\autorobomlm.css")
if CSS.exists():
    content = CSS.read_text(encoding="utf-8")
    backup = CSS.with_suffix(f".css.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    shutil.copy2(CSS, backup)

    if ".auto-grade-badge" in content:
        skipped.append("css: grade badge already exists")
    else:
        grade_css = '''

/* ============================================================
   GRADE BADGES
   ============================================================ */

.auto-grade-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.6px;
  border: 1px solid transparent;
}

.auto-grade-badge.grade-ap {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
  border-color: rgba(52, 211, 153, 0.4);
}

.auto-grade-badge.grade-a {
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
  border-color: rgba(96, 165, 250, 0.4);
}

.auto-grade-badge.grade-bp {
  background: rgba(168, 85, 247, 0.15);
  color: #c084fc;
  border-color: rgba(192, 132, 252, 0.4);
}

.auto-grade-badge.grade-b {
  background: rgba(245, 158, 11, 0.15);
  color: #fbbf24;
  border-color: rgba(251, 191, 36, 0.4);
}

.auto-grade-badge.grade-hold {
  background: rgba(148, 163, 184, 0.12);
  color: #94a3b8;
  border-color: rgba(148, 163, 184, 0.3);
}

.auto-muted {
  color: #64748b;
  font-size: 12px;
}

.auto-select-grade {
  min-width: 110px;
}
'''
        content = content.rstrip() + grade_css + "\n"
        CSS.write_text(content, encoding="utf-8")
        applied.append("css: grade badge styles added")

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
print("  1. Restart backend (Ctrl+C in uvicorn, then re-run uvicorn)")
print("  2. cd C:\\Users\\Administrator\\ROBOMLM_PLUS\\frontend")
print("     npx tsc --noEmit")
print("  3. Ctrl+Shift+R in browser")