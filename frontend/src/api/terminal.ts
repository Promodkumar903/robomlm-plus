// frontend/src/api/terminal.ts
// ROBOMLM+ Terminal API client
// Backend contract: ROBOMLM-TERMINAL-UI-1.0
//
// ⚠️ COMPLETE FILE — replace entire file. Do NOT append.

import { get, post } from "./client";
import type {
  TerminalContextResponse,
} from "../types/terminal";

// ===========================================================================
// CANONICAL — Terminal Frontend Contract
// ===========================================================================

/**
 * Canonical Terminal response — the one the UI reads.
 *
 * Backend: GET /api/terminal/frontend
 *
 * Params:
 *   symbol    — required  (e.g. "BTC/USDT")
 *   timeframe — optional  (default "1m")
 *   market    — optional  (e.g. "CRYPTO", "EQUITY")
 *   instrument— optional  (e.g. "SPOT", "FUTURE")
 */
export async function getTerminalFrontend(params: {
  symbol: string;
  timeframe?: string;
  market?: string;
  instrument?: string;
}): Promise<TerminalContextResponse> {
  const search = new URLSearchParams();
  search.set("symbol", params.symbol);

  if (params.timeframe) {
    search.set("timeframe", params.timeframe);
  }
  if (params.market) {
    search.set("market", params.market);
  }
  if (params.instrument) {
    search.set("instrument", params.instrument);
  }

  return get<TerminalContextResponse>(
    `/api/terminal/frontend?${search.toString()}`,
  );
}

// ===========================================================================
// MARKET DATA — standalone snapshot (candles source for chart fallback)
// ===========================================================================

/**
 * GET /api/terminal/market-data
 *
 * Currently backend accepts only `symbol` (no market/timeframe).
 * This endpoint is used as the market-data / snapshot source.
 */
export async function getTerminalMarketData(symbol: string) {
  const search = new URLSearchParams();
  search.set("symbol", symbol);

  return get<unknown>(
    `/api/terminal/market-data?${search.toString()}`,
  );
}

// ===========================================================================
// STAGE ENDPOINTS — individual reads (same application owner as POST)
// ===========================================================================

export async function getTerminalEvidence(
  symbol: string,
  timeframe: string = "1m",
) {
  const search = new URLSearchParams();
  search.set("symbol", symbol);
  search.set("timeframe", timeframe);

  return get<unknown>(
    `/api/terminal/evidence?${search.toString()}`,
  );
}

export async function getTerminalIntelligence(
  symbol: string,
  timeframe: string = "1m",
) {
  const search = new URLSearchParams();
  search.set("symbol", symbol);
  search.set("timeframe", timeframe);

  return get<unknown>(
    `/api/terminal/intelligence?${search.toString()}`,
  );
}

export async function getTerminalDecision(
  symbol: string,
  timeframe: string = "1m",
) {
  const search = new URLSearchParams();
  search.set("symbol", symbol);
  search.set("timeframe", timeframe);

  return get<unknown>(
    `/api/terminal/decision?${search.toString()}`,
  );
}

export async function getTerminalRisk(
  symbol: string,
  timeframe: string = "1m",
) {
  const search = new URLSearchParams();
  search.set("symbol", symbol);
  search.set("timeframe", timeframe);

  return get<unknown>(
    `/api/terminal/risk?${search.toString()}`,
  );
}

export async function getTerminalCas(
  symbol: string,
  timeframe: string = "1m",
) {
  const search = new URLSearchParams();
  search.set("symbol", symbol);
  search.set("timeframe", timeframe);

  return get<unknown>(
    `/api/terminal/cas?${search.toString()}`,
  );
}

export async function getTerminalPipeline(
  symbol: string,
  timeframe: string = "1m",
) {
  const search = new URLSearchParams();
  search.set("symbol", symbol);
  search.set("timeframe", timeframe);

  return get<unknown>(
    `/api/terminal/pipeline?${search.toString()}`,
  );
}

export async function getTerminalDecisionLayers(
  symbol: string,
  timeframe: string = "1m",
) {
  const search = new URLSearchParams();
  search.set("symbol", symbol);
  search.set("timeframe", timeframe);

  return get<unknown>(
    `/api/terminal/decision-layers?${search.toString()}`,
  );
}

// ===========================================================================
// PIPELINE RUNNER — POST /api/terminal (analysis only, no execution)
// ===========================================================================

export interface TerminalRunRequest {
  symbol: string;
  timeframe?: string;
  metadata?: Record<string, unknown>;
}

export async function runTerminalPipeline(
  body: TerminalRunRequest,
) {
  return post<unknown>("/api/terminal", {
    symbol: body.symbol,
    timeframe: body.timeframe ?? "1m",
    metadata: body.metadata ?? {},
  });
}

// ===========================================================================
// SIMPLE READ — GET /api/terminal (query form)
// ===========================================================================

export async function getTerminalSummary(
  symbol: string,
  timeframe: string = "1m",
) {
  const search = new URLSearchParams();
  search.set("symbol", symbol);
  search.set("timeframe", timeframe);

  return get<unknown>(
    `/api/terminal?${search.toString()}`,
  );
}

// ===========================================================================
// SYSTEM
// ===========================================================================

export async function getTerminalHealth() {
  return get<unknown>("/api/terminal/health");
}

export async function getTerminalFrontendMap() {
  return get<unknown>("/api/terminal/frontend/map");
}

// ===========================================================================
// DISCOVERY — used by symbol search / universe lookups
// ===========================================================================

export async function getDiscoveryUniverse(params?: {
  market?: string;
  instrument?: string;
  timeframe?: string;
  limit?: number;
}) {
  const search = new URLSearchParams();

  if (params?.market) search.set("market", params.market);
  if (params?.instrument) search.set("instrument", params.instrument);
  if (params?.timeframe) search.set("timeframe", params.timeframe);
  if (params?.limit !== undefined) search.set("limit", String(params.limit));

  const qs = search.toString();
  return get<unknown>(
    qs ? `/api/discovery/universe?${qs}` : "/api/discovery/universe",
  );
}

export async function getDiscoveryScanner(params?: {
  market?: string;
  instrument?: string;
  timeframe?: string;
  limit?: number;
}) {
  const search = new URLSearchParams();

  if (params?.market) search.set("market", params.market);
  if (params?.instrument) search.set("instrument", params.instrument);
  if (params?.timeframe) search.set("timeframe", params.timeframe);
  if (params?.limit !== undefined) search.set("limit", String(params.limit));

  const qs = search.toString();
  return get<unknown>(
    qs ? `/api/discovery/scanner?${qs}` : "/api/discovery/scanner",
  );
}

export async function getDiscoveryOpportunity(symbol: string) {
  return get<unknown>(
    `/api/discovery/opportunity/${encodeURIComponent(symbol)}`,
  );
}

export async function getDiscoveryTop10(params?: {
  market?: string;
  instrument?: string;
  timeframe?: string;
  limit?: number;
}) {
  const search = new URLSearchParams();

  if (params?.market) search.set("market", params.market);
  if (params?.instrument) search.set("instrument", params.instrument);
  if (params?.timeframe) search.set("timeframe", params.timeframe);
  if (params?.limit !== undefined) search.set("limit", String(params.limit));

  const qs = search.toString();
  return get<unknown>(
    qs ? `/api/discovery/top10?${qs}` : "/api/discovery/top10",
  );
}