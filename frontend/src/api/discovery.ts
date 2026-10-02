import { get } from "./client";

export type DiscoveryQuery = {
  market?: string;
  instrument?: string;
  timeframe?: string;
  limit?: number;
};

function buildQuery(
  params: Record<string, string | number | undefined>,
): string {
  const query = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (
      value !== undefined &&
      value !== null &&
      String(value).length > 0 &&
      String(value) !== "ALL"
    ) {
      query.set(key, String(value));
    }
  });

  const encoded = query.toString();

  return encoded ? `?${encoded}` : "";
}

export async function getDiscovery(
  params: DiscoveryQuery = {},
) {
  const query = buildQuery({
    market: params.market,
    instrument: params.instrument,
    timeframe: params.timeframe ?? "1h",
    limit: params.limit ?? 10,
  });

  return get(`/api/discovery${query}`);
}

export async function getDiscoveryUniverse(
  params: DiscoveryQuery = {},
) {
  const query = buildQuery({
    market: params.market,
    instrument: params.instrument,
    timeframe: params.timeframe ?? "1h",
    limit: params.limit ?? 10,
  });

  return get(`/api/discovery/universe${query}`);
}

export async function getDiscoveryLiquidity(
  params: DiscoveryQuery = {},
) {
  const query = buildQuery({
    market: params.market,
    instrument: params.instrument,
    timeframe: params.timeframe ?? "1h",
    limit: params.limit ?? 10,
  });

  return get(`/api/discovery/liquidity${query}`);
}

export async function getDiscoveryRisk(
  params: DiscoveryQuery = {},
) {
  const query = buildQuery({
    market: params.market,
    instrument: params.instrument,
    timeframe: params.timeframe ?? "1h",
    limit: params.limit ?? 10,
  });

  return get(`/api/discovery/risk${query}`);
}

export async function getDiscoveryTiming(
  params: DiscoveryQuery = {},
) {
  const query = buildQuery({
    market: params.market,
    instrument: params.instrument,
    timeframe: params.timeframe ?? "1h",
    limit: params.limit ?? 10,
  });

  return get(`/api/discovery/timing${query}`);
}

export async function getDiscoveryScanner(
  params: DiscoveryQuery = {},
) {
  const query = buildQuery({
    market: params.market,
    instrument: params.instrument,
    timeframe: params.timeframe ?? "1h",
    limit: params.limit ?? 10,
  });

  return get(`/api/discovery/scanner${query}`);
}

export async function getDiscoveryRanking(
  params: DiscoveryQuery = {},
) {
  const query = buildQuery({
    market: params.market,
    instrument: params.instrument,
    timeframe: params.timeframe ?? "1h",
    limit: params.limit ?? 10,
  });

  return get(`/api/discovery/ranking${query}`);
}

export async function getDiscoveryTop10(
  params: DiscoveryQuery = {},
) {
  const query = buildQuery({
    market: params.market,
    instrument: params.instrument,
    timeframe: params.timeframe ?? "1h",
    limit: params.limit ?? 10,
  });

  return get(`/api/discovery/top10${query}`);
}

export async function getDiscoveryOpportunity(
  symbol: string,
) {
  return get(
    `/api/discovery/opportunity/${encodeURIComponent(symbol)}`,
  );
}

export async function getDiscoveryIntraday(
  params: DiscoveryQuery = {},
) {
  const query = buildQuery({
    market: params.market,
    instrument: params.instrument,
    timeframe: params.timeframe ?? "1h",
    limit: params.limit ?? 10,
  });

  return get(`/api/discovery/intraday${query}`);
}

export async function getDiscoveryBackendMap() {
  return get("/api/discovery/backend-map");
}

export async function getDiscoveryHealth() {
  return get("/api/discovery/health");
}

export async function getAssetMarketData(
  symbol: string,
  timeframe: string,
) {
  const query = buildQuery({
    symbol,
    timeframe,
  });

  return get(`/api/terminal/market-data${query}`);
}

export async function getAssetIntelligence(
  symbol: string,
  timeframe: string,
) {
  const query = buildQuery({
    symbol,
    timeframe,
  });

  return get(`/api/terminal/intelligence${query}`);
}

export async function getAssetEvidence(
  symbol: string,
  timeframe: string,
) {
  const query = buildQuery({
    symbol,
    timeframe,
  });

  return get(`/api/terminal/evidence${query}`);
}

export async function getAssetDecisionLayers(
  symbol: string,
  timeframe: string,
) {
  const query = buildQuery({
    symbol,
    timeframe,
  });

  return get(`/api/terminal/decision-layers${query}`);
}