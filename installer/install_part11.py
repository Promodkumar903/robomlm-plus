"""Add backward-compat shims to src/api/autorobomlm.ts"""
from pathlib import Path

TARGET = Path(
    r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\src\api\autorobomlm.ts"
)

if not TARGET.exists():
    print(f"ERROR: {TARGET} not found.")
    raise SystemExit(1)

content = TARGET.read_text(encoding="utf-8")

if "BACKWARD COMPAT" in content:
    print("Already has compat shims. No change.")
    raise SystemExit(0)

SHIMS = '''

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
'''

content = content.rstrip() + SHIMS + "\n"

TARGET.write_text(content, encoding="utf-8")
print(f"UPDATED: {TARGET}")
print(f"  ({TARGET.stat().st_size} bytes)")
print()
print("Now run:")
print("  cd C:\\Users\\Administrator\\ROBOMLM_PLUS\\frontend")
print("  npx tsc --noEmit")