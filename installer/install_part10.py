"""AutoROBOMLM installer part 10 - frontend TS client"""
from pathlib import Path
import shutil
from datetime import datetime

ROOT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\src\api")
ROOT.mkdir(parents=True, exist_ok=True)

# Backup existing autorobomlm.ts
existing = ROOT / "autorobomlm.ts"
if existing.exists():
    backup = existing.with_suffix(
        f".ts.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    shutil.copy2(existing, backup)
    print(f"BACKUP: {backup}")

CLIENT_TS = '''/**
 * ROBOMLM_PLUS — AutoROBOMLM API Client
 *
 * Backend: app/api/v1/autorobomlm_api.py
 * Base path: /api/autorobomlm
 *
 * Lifecycle:
 *   - The backend keeps a single AutoRobomlmLoop instance.
 *   - `start` / `stop` / `kill` / `resume` control that loop.
 *   - `tick` runs one manual scan (useful for testing).
 *   - `config` GET/POST reads/updates runtime configuration.
 */

import {
  get,
  post,
  getApiErrorMessage,
  isApiError,
} from "./client";

// ============================================================
// Types
// ============================================================

export type GradeBand = "A+" | "A" | "B+" | "B" | "HOLD";

export type ExecutionMode = "DEMO" | "LIVE";

export type WatchlistSource =
  | "FAVORITES"
  | "DISCOVERY_TOP10"
  | "MANUAL";

export type LoopState =
  | "STOPPED"
  | "RUNNING"
  | "KILLED";

export interface GradeBands {
  "A+": [number, number];
  A: [number, number];
  "B+": [number, number];
  B: [number, number];
  HOLD: [number, number];
}

export interface AutoRobomlmConfigPayload {
  min_grade: GradeBand;
  execution_mode: ExecutionMode;
  live_confirmed: boolean;
  watchlist_source: WatchlistSource;
  manual_watchlist: string[];
  max_open_positions: number;
  risk_per_trade_pct: number;
  max_position_pct: number;
  sl_atr_multiplier: number;
  tp_atr_multiplier: number;
  loop_interval_sec: number;
  grade_bands: GradeBands;
  metadata: Record<string, unknown>;
}

export interface AutoRobomlmStatusPayload {
  engine: string;
  version: string;
  state: LoopState;
  tick_count: number;
  last_tick: AutoRobomlmTickSummary | null;
  config: AutoRobomlmConfigPayload;
  open_positions: number;
  total_positions: number;
}

export interface AutoRobomlmTickSummary {
  started_at: string;
  finished_at: string;
  scanned: number;
  opened: number;
  closed: number;
  skipped_grade: number;
  skipped_gates: number;
  errors: string[];
  events: string[];
}

export interface AutoRobomlmPosition {
  position_id: string;
  symbol: string;
  direction: "BUY" | "SELL";
  quantity: number;
  entry_price: number;
  stop_loss: number;
  take_profit: number;
  opened_at: string;
  status: "OPEN" | "CLOSED";
  exit_price: number | null;
  exit_reason: string | null;
  closed_at: string | null;
  current_price?: number;
  pnl?: number;
  pnl_pct?: number;
}

// ============================================================
// Generic response envelope
// ============================================================

export interface HealthResponse {
  ok: boolean;
  engine: string;
  version: string;
  initialized: boolean;
}

export interface StatusResponse {
  ok: boolean;
  status: AutoRobomlmStatusPayload;
}

export interface ActionResponse {
  ok: boolean;
  action: string;
  status?: AutoRobomlmStatusPayload;
  summary?: AutoRobomlmTickSummary;
}

export interface PositionsResponse {
  ok: boolean;
  positions: AutoRobomlmPosition[];
  all_positions: AutoRobomlmPosition[];
}

export interface ConfigResponse {
  ok: boolean;
  config: AutoRobomlmConfigPayload;
}

export interface ConfigUpdateResponse {
  ok: boolean;
  action: "config";
  config: AutoRobomlmConfigPayload;
}

// ============================================================
// API Functions
// ============================================================

const BASE = "/api/autorobomlm";

export function getHealth(): Promise<HealthResponse> {
  return get<HealthResponse>(`${BASE}/health`);
}

export function getStatus(): Promise<StatusResponse> {
  return get<StatusResponse>(`${BASE}/status`);
}

export function getPositions(): Promise<PositionsResponse> {
  return get<PositionsResponse>(`${BASE}/positions`);
}

export function getConfig(): Promise<ConfigResponse> {
  return get<ConfigResponse>(`${BASE}/config`);
}

export function updateConfig(
  payload: Partial<AutoRobomlmConfigPayload>
): Promise<ConfigUpdateResponse> {
  return post<ConfigUpdateResponse>(`${BASE}/config`, payload);
}

export function startLoop(): Promise<ActionResponse> {
  return post<ActionResponse>(`${BASE}/start`);
}

export function stopLoop(): Promise<ActionResponse> {
  return post<ActionResponse>(`${BASE}/stop`);
}

export function killSwitch(): Promise<ActionResponse> {
  return post<ActionResponse>(`${BASE}/kill`);
}

export function resumeLoop(): Promise<ActionResponse> {
  return post<ActionResponse>(`${BASE}/resume`);
}

export function runTick(): Promise<ActionResponse> {
  return post<ActionResponse>(`${BASE}/tick`);
}

// ============================================================
// Error helper (keeps existing usage pattern)
// ============================================================

export function describeAutoRobomlmError(error: unknown): string {
  if (isApiError(error)) {
    if (error.status === 404) {
      return "AutoROBOMLM endpoint is not available on the running backend.";
    }
    if (error.status === 401 || error.status === 403) {
      return "AutoROBOMLM access is not authorized.";
    }
    if (error.status >= 500) {
      return "AutoROBOMLM backend returned a server error.";
    }
    if (error.status === 400) {
      return error.message || "Invalid AutoROBOMLM request.";
    }
  }
  return getApiErrorMessage(
    error,
    "Unable to load AutoROBOMLM data."
  );
}
'''

target = ROOT / "autorobomlm.ts"
target.write_text(CLIENT_TS, encoding="utf-8")
print(f"WROTE: {target}")
print(f"  ({target.stat().st_size} bytes)")

print()
print("Done. autorobomlm.ts replaced.")
print()
print("Next:")
print("  1. Verify TS compiles (frontend build / vite)")
print("  2. Use in a page:  import { getStatus, startLoop, ... } from '@/api/autorobomlm'")