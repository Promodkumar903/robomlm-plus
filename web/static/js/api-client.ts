export class ApiRequestError extends Error {
  readonly status: number;
  readonly payload: unknown;
  constructor(message: string, status: number, payload: unknown) {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
    this.payload = payload;
  }
}
async function api<T = unknown>(
  path: string,
  init: RequestInit = {}
): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body !== undefined && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const response = await fetch(path, {
    ...init,
    headers,
    credentials: "same-origin"
  });
  const contentType = response.headers.get("content-type") || "";
  let payload: unknown;
  if (contentType.includes("application/json")) {
    payload = await response.json();
  } else {
    const text = await response.text();
    payload = text ? { raw: text } : null;
  }
  if (!response.ok) {
    let message = `HTTP ${response.status}`;
    if (typeof payload === "object" && payload !== null) {
      const value = payload as Record<string, unknown>;
      if (typeof value.message === "string") message = value.message;
      else if (typeof value.detail === "string") message = value.detail;
      else if (typeof value.error === "string") message = value.error;
    }
    throw new ApiRequestError(message, response.status, payload);
  }
  return payload as T;
}
export const backend = {
  health: () => api("/api/backend/health"),
  map: () => api("/api/backend/map"),
  decision: () => api("/api/backend/decision"),
  equations: () => api("/api/backend/equations"),
  engines: () => api("/api/backend/engines"),
  completeMap: () => api("/api/backend/complete-map"),
  completeHealth: () => api("/api/backend/complete-health"),
  finalPipeline: () => api("/api/backend/final-pipeline"),
  coverage: () => api("/api/backend/coverage"),
  frontendContract: () => api("/api/frontend/backend-contract")
};
export const terminal = {
  overview: () => api("/api/terminal"),
  context: () => api("/api/terminal/context"),
  frontendMap: () => api("/api/terminal/frontend-map"),
  evidence: () => api("/api/terminal/evidence"),
  intelligence: () => api("/api/terminal/intelligence"),
  decision: () => api("/api/terminal/decision"),
  risk: () => api("/api/terminal/risk"),
  cas: () => api("/api/terminal/cas"),
  layers: () => api("/api/terminal/decision-layers"),
  pipeline: () => api("/api/terminal/pipeline"),
  portfolio: () => api("/api/portfolio/overview"),
  positions: () => api("/api/positions")
};
export const discovery = {
  engines: () => api("/api/discovery/engines"),
  overview: () => api("/api/discovery"),
  scanner: () => api("/api/discovery/scanner"),
  opportunities: () => api("/api/discovery/opportunities"),
  top10: () => api("/api/discovery/top10"),
  asset: (symbol: string) => api(`/api/discovery/asset?symbol=${encodeURIComponent(symbol)}`),
  explain: (symbol: string) => api(`/api/discovery/explain?symbol=${encodeURIComponent(symbol)}`),
  gates: () => api("/api/discovery/gates"),
  favorites: () => api("/api/discovery/favorites"),
  provenance: () => api("/api/discovery/provenance"),
  health: () => api("/api/discovery/health")
};
export const buyer = {
  markets: () => api("/api/buyer/markets"),
  strategies: () => api("/api/buyer/strategies"),
  analyze: (body: unknown) => api("/api/buyer/analyze", { method: "POST", body: JSON.stringify(body) }),
  pipeline: () => api("/api/buyer/pipeline"),
  decision: () => api("/api/buyer/decision"),
  risk: () => api("/api/buyer/risk"),
  cas: () => api("/api/buyer/cas"),
  casGates: () => api("/api/buyer/cas/gates"),
  plus: () => api("/api/buyer/plus"),
  autorobomlm: () => api("/api/buyer/autorobomlm"),
  backendMap: () => api("/api/buyer/backend-map"),
  health: () => api("/api/buyer/health"),
  invariants: () => api("/api/buyer/invariants")
};
export const memory = {
  overview: () => api("/api/memory"),
  search: () => api("/api/memory/search"),
  decision: () => api("/api/memory/decision"),
  evidence: () => api("/api/memory/evidence"),
  outcome: () => api("/api/memory/outcome"),
  pattern: () => api("/api/memory/pattern"),
  backendMap: () => api("/api/memory/backend-map")
};
export const research = {
  overview: () => api("/api/research"),
  hypothesis: () => api("/api/research/hypothesis"),
  experiment: () => api("/api/research/experiment"),
  validation: () => api("/api/research/validation"),
  stress: () => api("/api/research/stress"),
  candidate: () => api("/api/research/candidate"),
  version: () => api("/api/research/version"),
  deployment: () => api("/api/research/deployment"),
  backendMap: () => api("/api/research/backend-map")
};
export const automation = {
  overview: () => api("/api/automation"),
  mode: () => api("/api/automation/mode"),
  execution: () => api("/api/automation/execution"),
  killSwitch: () => api("/api/automation/kill-switch"),
  reconciliation: () => api("/api/automation/reconciliation"),
  status: () => api("/api/autorobomlm/status"),
  start: () => api("/api/autorobomlm/start", { method: "POST" }),
  pause: () => api("/api/autorobomlm/pause", { method: "POST" }),
  stop: () => api("/api/autorobomlm/stop", { method: "POST" }),
  finance: () => api("/api/bot/finance"),
  trades: () => api("/api/bot/trades?status=all&limit=50"),
  activity: () => api("/api/bot/activity?limit=30")
};
export const account = {
  status: () => api("/api/account/status"),
  backendMap: () => api("/api/account/backend-map"),
  summary: () => api("/api/account/summary"),
  equity: () => api("/api/account/equity"),
  allocation: () => api("/api/account/allocation"),
  mode: (value: unknown) => api("/api/account/mode", { method: "POST", body: JSON.stringify(value) }),
  currency: (value: unknown) => api("/api/account/currency", { method: "POST", body: JSON.stringify(value) }),
  resetSeed: () => api("/api/account/reset-seed", { method: "POST" }),
  botAllocation: () => api("/api/bot/allocation")
};
