import type {
  BackendHealth,
  TerminalResponse,
  PortfolioOverview,
  PositionsResponse,
  DecisionResponse,
  RiskResponse,
  CasResponse,
  PipelineResponse,
  DiscoveryResponse,
  DiscoveryOpportunitiesResponse,
  DiscoveryTop10Response,
  BuyerMarketsResponse,
  BuyerStrategiesResponse,
  BuyerPipelineResponse,
  MemoryResponse,
  MemoryDecisionResponse,
  MemoryEvidenceResponse,
  MemoryOutcomeResponse,
  MemoryPatternResponse,
  ResearchResponse,
  ResearchHypothesisResponse,
  ResearchValidationResponse,
  ResearchVersionResponse,
  ResearchDeploymentResponse,
  AutomationResponse,
  AutomationModeResponse,
  AutomationExecutionResponse,
  AutomationKillSwitchResponse,
  AutomationReconciliationResponse,
  AccountSummary,
  AccountAllocation,
  ApiError
} from "./types";

export class ApiRequestError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly payload?: ApiError | unknown
  ) {
    super(message);
    this.name = "ApiRequestError";
  }
}

async function decode(response: Response): Promise<unknown> {
  const text = await response.text();

  if (!text) return {};

  try {
    return JSON.parse(text);
  } catch {
    return { raw: text };
  }
}

export async function api<T>(
  path: string,
  init: RequestInit = {}
): Promise<T> {
  const headers = new Headers(init.headers);

  headers.set("Accept", "application/json");

  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(path, {
    ...init,
    credentials: "same-origin",
    headers
  });

  const payload = await decode(response);

  if (!response.ok) {
    const body = payload as any;

    throw new ApiRequestError(
      body?.message ||
      body?.detail ||
      body?.error ||
      `HTTP ${response.status}`,
      response.status,
      payload
    );
  }

  return payload as T;
}

/* ---------- Backend ---------- */

export const backend = {
  health: () =>
    api<BackendHealth>("/api/backend/health"),

  map: () =>
    api("/api/backend/map"),

  decision: () =>
    api<DecisionResponse>("/api/backend/decision"),

  equations: () =>
    api("/api/backend/equations"),

  engines: () =>
    api("/api/backend/engines"),

  completeMap: () =>
    api("/api/backend/complete-map"),

  completeHealth: () =>
    api("/api/backend/complete-health"),

  finalPipeline: () =>
    api("/api/backend/final-pipeline"),

  coverage: () =>
    api("/api/backend/coverage"),

  frontendContract: () =>
    api("/api/frontend/backend-contract")
};

/* ---------- Terminal ---------- */

export const terminal = {
  overview: () =>
    api<TerminalResponse>("/api/terminal"),

  context: () =>
    api("/api/terminal/context"),

  evidence: () =>
    api("/api/terminal/evidence"),

  intelligence: () =>
    api("/api/terminal/intelligence"),

  decision: () =>
    api<DecisionResponse>("/api/terminal/decision"),

  risk: () =>
    api<RiskResponse>("/api/terminal/risk"),

  cas: () =>
    api<CasResponse>("/api/terminal/cas"),

  layers: () =>
    api("/api/terminal/decision-layers"),

  pipeline: () =>
    api<PipelineResponse>("/api/terminal/pipeline"),

  portfolio: () =>
    api<PortfolioOverview>("/api/portfolio/overview"),

  positions: () =>
    api<PositionsResponse>("/api/positions"),

  price: (symbol: string) =>
    api(`/api/live/price/${encodeURIComponent(symbol)}`),

  candles: (symbol: string) =>
    api(`/api/live/candles/${encodeURIComponent(symbol)}`)
};

/* ---------- Discovery ---------- */

export const discovery = {
  overview: () =>
    api<DiscoveryResponse>("/api/discovery"),

  engines: () =>
    api("/api/discovery/engines"),

  scanner: () =>
    api("/api/discovery/scanner"),

  opportunities: () =>
    api<DiscoveryOpportunitiesResponse>("/api/discovery/opportunities"),

  top10: () =>
    api<DiscoveryTop10Response>("/api/discovery/top10"),

  asset: () =>
    api("/api/discovery/asset"),

  explain: () =>
    api("/api/discovery/explain"),

  gates: () =>
    api("/api/discovery/gates"),

  favorites: () =>
    api("/api/discovery/favorites"),

  provenance: () =>
    api("/api/discovery/provenance"),

  health: () =>
    api("/api/discovery/health")
};

/* ---------- Buyer ---------- */

export const buyer = {
  markets: () =>
    api<BuyerMarketsResponse>("/api/buyer/markets"),

  strategies: () =>
    api<BuyerStrategiesResponse>("/api/buyer/strategies"),

  analyze: <TRequest, TResponse = unknown>(
    body: TRequest
  ) =>
    api<TResponse>("/api/buyer/analyze", {
      method: "POST",
      body: JSON.stringify(body)
    }),

  pipeline: () =>
    api<BuyerPipelineResponse>("/api/buyer/pipeline"),

  decision: () =>
    api<DecisionResponse>("/api/buyer/decision"),

  risk: () =>
    api<RiskResponse>("/api/buyer/risk"),

  cas: () =>
    api<CasResponse>("/api/buyer/cas"),

  casGates: () =>
    api("/api/buyer/cas/gates"),

  plus: () =>
    api("/api/buyer/plus"),

  autorobomlm: () =>
    api("/api/buyer/autorobomlm"),

  backendMap: () =>
    api("/api/buyer/backend-map"),

  health: () =>
    api("/api/buyer/health"),

  invariants: () =>
    api("/api/buyer/invariants")
};

/* ---------- Memory ---------- */

export const memory = {
  overview: () =>
    api<MemoryResponse>("/api/memory"),

  search: () =>
    api("/api/memory/search"),

  decision: () =>
    api<MemoryDecisionResponse>("/api/memory/decision"),

  evidence: () =>
    api<MemoryEvidenceResponse>("/api/memory/evidence"),

  outcome: () =>
    api<MemoryOutcomeResponse>("/api/memory/outcome"),

  pattern: () =>
    api<MemoryPatternResponse>("/api/memory/pattern"),

  backendMap: () =>
    api("/api/memory/backend-map")
};

/* ---------- Research ---------- */

export const research = {
  overview: () =>
    api<ResearchResponse>("/api/research"),

  hypothesis: () =>
    api<ResearchHypothesisResponse>("/api/research/hypothesis"),

  experiment: () =>
    api("/api/research/experiment"),

  validation: () =>
    api<ResearchValidationResponse>("/api/research/validation"),

  stress: () =>
    api("/api/research/stress"),

  candidate: () =>
    api("/api/research/candidate"),

  version: () =>
    api<ResearchVersionResponse>("/api/research/version"),

  deployment: () =>
    api<ResearchDeploymentResponse>("/api/research/deployment"),

  backendMap: () =>
    api("/api/research/backend-map")
};

/* ---------- Automation ---------- */

export const automation = {
  overview: () =>
    api<AutomationResponse>("/api/automation"),

  mode: () =>
    api<AutomationModeResponse>("/api/automation/mode"),

  execution: () =>
    api<AutomationExecutionResponse>("/api/automation/execution"),

  killSwitch: () =>
    api<AutomationKillSwitchResponse>("/api/automation/kill-switch"),

  reconciliation: () =>
    api<AutomationReconciliationResponse>(
      "/api/automation/reconciliation"
    )
};

/* ---------- Account ---------- */

export const account = {
  summary: () =>
    api<AccountSummary>("/api/account/summary"),

  equity: () =>
    api("/api/account/equity"),

  allocation: () =>
    api<AccountAllocation>("/api/account/allocation"),

  status: () =>
    api("/api/account/status"),

  backendMap: () =>
    api("/api/account/backend-map")
};