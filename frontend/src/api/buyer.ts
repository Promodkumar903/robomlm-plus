import { get } from "./client";

export type BuyerMode =
  | "ANALYSIS"
  | "SIMULATION"
  | "AUTHORIZED_EXECUTION";

export interface BuyerSelection {
  symbol: string;
  market: string;
  instrument: string;
  contract: string;
  strategy: string;
  timeframe: string;
  mode: BuyerMode;
}

export interface BuyerCandle {
  timestamp: number | string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number | null;
}

export interface BuyerCandlesResponse {
  symbol?: string;
  timeframe?: string;
  candles?: BuyerCandle[];
  data?: BuyerCandle[];
  series?: BuyerCandle[];
}

export interface BuyerPipelineResponse {
  status?: string;
  success?: boolean;
  symbol?: string;
  market?: string;
  instrument?: string;
  selection?: Record<string, unknown>;
  pipeline?: Record<string, unknown>;
  authorization?: Record<string, unknown>;
  safety?: Record<string, unknown>;
  data?: unknown;
  message?: string;
  timestamp?: string;
}

// ------------------------------------------------------------
// Response normalizer
// Handles: array of objects, array of arrays, various key names
// ------------------------------------------------------------

function pickNumber(...vals: unknown[]): number | null {
  for (const v of vals) {
    if (v === null || v === undefined) continue;
    const n = typeof v === "number" ? v : Number(String(v));
    if (Number.isFinite(n)) return n;
  }
  return null;
}

function pickTimestamp(
  ...vals: unknown[]
): number | string | null {
  for (const v of vals) {
    if (v === null || v === undefined) continue;
    if (typeof v === "number" && Number.isFinite(v)) return v;
    if (typeof v === "string" && v.trim().length > 0) return v;
  }
  return null;
}

function normalizeOne(raw: unknown): BuyerCandle | null {
  // Form 1: [openTime, open, high, low, close, volume, ...]
  if (Array.isArray(raw)) {
    const ts = pickTimestamp(raw[0]);
    const o = pickNumber(raw[1]);
    const h = pickNumber(raw[2]);
    const l = pickNumber(raw[3]);
    const c = pickNumber(raw[4]);
    const v = pickNumber(raw[5]) ?? 0;
    if (ts === null || o === null || h === null || l === null || c === null) {
      return null;
    }
    return { timestamp: ts, open: o, high: h, low: l, close: c, volume: v };
  }

  if (!raw || typeof raw !== "object") return null;

  // Form 2: object with various key names
  const r = raw as Record<string, unknown>;
  const ts = pickTimestamp(
    r.timestamp, r.time, r.t, r.ts, r.date, r.datetime,
    r.open_time, r.openTime, r.open_time_ms,
  );
  const o = pickNumber(r.open, r.o, r.Open);
  const h = pickNumber(r.high, r.h, r.High);
  const l = pickNumber(r.low, r.l, r.Low);
  const c = pickNumber(r.close, r.c, r.Close);
  const v = pickNumber(r.volume, r.v, r.Volume, r.vol) ?? 0;

  if (ts === null || o === null || h === null || l === null || c === null) {
    return null;
  }
  return { timestamp: ts, open: o, high: h, low: l, close: c, volume: v };
}

function extractRawArray(resp: unknown): unknown[] {
  if (!resp) return [];
  if (Array.isArray(resp)) return resp;
  if (typeof resp !== "object") return [];
  const r = resp as Record<string, unknown>;
  const keys = [
    "candles", "data", "series", "items", "ohlcv",
    "result", "klines", "rows", "bars",
  ];
  for (const k of keys) {
    if (Array.isArray(r[k])) return r[k] as unknown[];
  }
  return [];
}

function normalizeCandles(resp: unknown): BuyerCandle[] {
  const arr = extractRawArray(resp);
  const out: BuyerCandle[] = [];
  for (const raw of arr) {
    const c = normalizeOne(raw);
    if (c) out.push(c);
  }
  return out;
}

/**
 * Verified frontend boundary:
 *
 * GET /api/live/candles/{symbol}?timeframe={timeframe}
 *
 * Buyer does not manufacture intelligence, decisions,
 * risk or execution state in the browser.
 */
export async function getBuyerLiveCandles(
  symbol: string,
  timeframe: string,
): Promise<BuyerCandlesResponse> {
  const cleanSymbol = symbol.trim();

  if (!cleanSymbol) {
    throw new Error("Buyer market symbol is required.");
  }

  const cleanTimeframe = timeframe.trim() || "1m";

  const raw = await get<unknown>(
    `/api/live/candles/${encodeURIComponent(
      cleanSymbol,
    )}?timeframe=${encodeURIComponent(cleanTimeframe)}`,
  );

  const candles = normalizeCandles(raw);
  return { candles };
}
