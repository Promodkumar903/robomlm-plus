/**
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
  entry_grade?: string | null;
  entry_score?: number | null;
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

// ============================================================
// BACKWARD COMPAT SHIMS
// ============================================================
//
// The existing page at frontend/autorobomlm/index.tsx was written
// against an older API surface. These shims map the old names
// to the current backend. Sections not yet implemented return
// safe empty shapes with an explicit "not_implemented" flag.
//

export interface AutoRobomlmStatus {
  status?: string;
  state?: string;
  enabled?: boolean;
  running?: boolean;
  active?: boolean;
  mode?: string;
  [key: string]: unknown;
}

export interface AutoRobomlmReadiness {
  ready?: boolean;
  status?: string;
  state?: string;
  not_implemented?: boolean;
  checks?: unknown;
  blockers?: unknown;
  reasons?: unknown;
  [key: string]: unknown;
}

export interface AutoRobomlmControls {
  enabled?: boolean;
  running?: boolean;
  mode?: string;
  not_implemented?: boolean;
  controls?: unknown;
  permissions?: unknown;
  [key: string]: unknown;
}

export interface AutoRobomlmEvent {
  id?: string | number;
  event_id?: string | number;
  timestamp?: string | number;
  time?: string | number;
  type?: string;
  event_type?: string;
  status?: string;
  message?: string;
  detail?: string;
  [key: string]: unknown;
}

export interface AutoRobomlmHistory {
  items?: AutoRobomlmEvent[];
  events?: AutoRobomlmEvent[];
  history?: AutoRobomlmEvent[];
  total?: number;
  not_implemented?: boolean;
  [key: string]: unknown;
}

export interface AutoRobomlmPlus {
  status?: unknown;
  readiness?: unknown;
  controls?: unknown;
  events?: unknown;
  history?: unknown;
  not_implemented?: boolean;
  [key: string]: unknown;
}

/**
 * Backward-compat: maps old getAutoRobomlmStatus name to /status.
 */
export async function getAutoRobomlmStatus(): Promise<AutoRobomlmStatus> {
  const res = await getStatus();
  return res.status as unknown as AutoRobomlmStatus;
}

/**
 * Backward-compat: readiness not yet implemented on backend.
 */
export async function getAutoRobomlmReadiness(): Promise<AutoRobomlmReadiness> {
  return {
    ready: false,
    state: "NOT_IMPLEMENTED",
    not_implemented: true,
    reasons: [
      "Readiness endpoint is not yet wired in this backend build.",
    ],
  };
}

/**
 * Backward-compat: controls not yet implemented on backend.
 */
export async function getAutoRobomlmControls(): Promise<AutoRobomlmControls> {
  try {
    const res = await getStatus();
    return {
      enabled: res.status.state !== "STOPPED",
      running: res.status.state === "RUNNING",
      mode: res.status.config.execution_mode,
      not_implemented: true,
      controls: {
        state: res.status.state,
        can_start: res.status.state === "STOPPED",
        can_stop: res.status.state === "RUNNING",
        can_kill: res.status.state !== "KILLED",
      },
    };
  } catch {
    return { not_implemented: true };
  }
}

/**
 * Backward-compat: events stream not yet implemented.
 * Returns the last tick's events if available.
 */
export async function getAutoRobomlmEvents(): Promise<
  AutoRobomlmEvent[] | AutoRobomlmHistory
> {
  try {
    const res = await getStatus();
    const lastTick = res.status.last_tick;
    if (!lastTick) return [];
    const events: AutoRobomlmEvent[] = [
      ...lastTick.events.map((message, idx) => ({
        id: `tick-${res.status.tick_count}-${idx}`,
        event_type: "TICK_EVENT",
        message,
        timestamp: lastTick.finished_at,
      })),
      ...lastTick.errors.map((message, idx) => ({
        id: `err-${res.status.tick_count}-${idx}`,
        event_type: "TICK_ERROR",
        message,
        timestamp: lastTick.finished_at,
      })),
    ];
    return events;
  } catch {
    return [];
  }
}

/**
 * Backward-compat: history not yet implemented.
 */
export async function getAutoRobomlmHistory(): Promise<
  AutoRobomlmHistory | AutoRobomlmEvent[]
> {
  return {
    not_implemented: true,
    items: [],
    total: 0,
  };
}

/**
 * Backward-compat: plus endpoint not yet implemented.
 */
export async function getAutoRobomlmPlus(): Promise<AutoRobomlmPlus> {
  return {
    not_implemented: true,
  };
}

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
}

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

