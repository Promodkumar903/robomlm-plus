import { get } from "./client";

export type ScalperMarket =
  | "SPOT"
  | "FUTURES"
  | "OPTIONS";

export type ScalperOptionSide =
  | "CE"
  | "PE";

export type ScalperTimeframe =
  | "1m"
  | "3m"
  | "5m"
  | "15m"
  | "30m"
  | "1h";

export interface LiveCandle {
  timestamp: number | string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number | null;
  turnover?: number | null;
  transactions?: number | null;
  open_interest?: number | null;
  [key: string]: unknown;
}

export interface LiveCandlesResponse {
  symbol?: string;
  timeframe?: string;
  candles?: LiveCandle[];
  data?: LiveCandle[];
  series?: LiveCandle[];
  status?: string;
  success?: boolean;
  message?: string;
  timestamp?: number | string;
  [key: string]: unknown;
}

function normaliseCandle(
  value: unknown,
): LiveCandle | null {
  if (
    !value ||
    typeof value !== "object" ||
    Array.isArray(value)
  ) {
    return null;
  }

  const item =
    value as Record<string, unknown>;

  const timestamp =
    item.timestamp ??
    item.time ??
    item.datetime ??
    item.date;

  const open = Number(item.open);
  const high = Number(item.high);
  const low = Number(item.low);
  const close = Number(item.close);

  if (
    timestamp === undefined ||
    timestamp === null ||
    !Number.isFinite(open) ||
    !Number.isFinite(high) ||
    !Number.isFinite(low) ||
    !Number.isFinite(close)
  ) {
    return null;
  }

  const volume =
    item.volume === undefined ||
    item.volume === null
      ? null
      : Number(item.volume);

  const turnover =
    item.turnover === undefined ||
    item.turnover === null
      ? null
      : Number(item.turnover);

  const transactions =
    item.transactions === undefined ||
    item.transactions === null
      ? null
      : Number(item.transactions);

  const openInterest =
    item.open_interest === undefined ||
    item.open_interest === null
      ? null
      : Number(item.open_interest);

  return {
    ...item,
    timestamp:
      typeof timestamp === "number" ||
      typeof timestamp === "string"
        ? timestamp
        : String(timestamp),
    open,
    high,
    low,
    close,
    volume:
      volume !== null &&
      Number.isFinite(volume)
        ? volume
        : null,
    turnover:
      turnover !== null &&
      Number.isFinite(turnover)
        ? turnover
        : null,
    transactions:
      transactions !== null &&
      Number.isFinite(transactions)
        ? transactions
        : null,
    open_interest:
      openInterest !== null &&
      Number.isFinite(openInterest)
        ? openInterest
        : null,
  };
}

function extractCandles(
  payload: unknown,
): LiveCandle[] {
  if (Array.isArray(payload)) {
    return payload
      .map(normaliseCandle)
      .filter(
        (item): item is LiveCandle =>
          item !== null,
      );
  }

  if (
    !payload ||
    typeof payload !== "object"
  ) {
    return [];
  }

  const response =
    payload as Record<string, unknown>;

  const candidates = [
    response.candles,
    response.data,
    response.series,
    response.items,
  ];

  for (const candidate of candidates) {
    if (!Array.isArray(candidate)) {
      continue;
    }

    const candles = candidate
      .map(normaliseCandle)
      .filter(
        (item): item is LiveCandle =>
          item !== null,
      );

    if (candles.length > 0) {
      return candles;
    }
  }

  return [];
}

function normaliseResponse(
  payload: unknown,
  symbol: string,
  timeframe: string,
): LiveCandlesResponse {
  const response =
    payload &&
    typeof payload === "object" &&
    !Array.isArray(payload)
      ? (payload as Record<string, unknown>)
      : {};

  return {
    ...response,
    symbol:
      typeof response.symbol === "string"
        ? response.symbol
        : symbol,
    timeframe:
      typeof response.timeframe === "string"
        ? response.timeframe
        : timeframe,
    candles: extractCandles(payload),
  } as LiveCandlesResponse;
}

/**
 * Fetch live candles for Scalper Trading.
 *
 * Authoritative backend boundary:
 *
 *   GET /api/live/candles/{symbol}?timeframe={timeframe}
 *
 * This API layer deliberately does not invent a
 * scalper signal, order, risk or execution endpoint.
 */
export async function getScalperLiveCandles(
  symbol: string,
  timeframe: string = "1m",
): Promise<LiveCandlesResponse> {
  const cleanSymbol = symbol.trim();
  const cleanTimeframe =
    timeframe.trim() || "1m";

  if (!cleanSymbol) {
    throw new Error(
      "Scalper Trading symbol is required.",
    );
  }

  const encodedSymbol =
    encodeURIComponent(cleanSymbol);

  const encodedTimeframe =
    encodeURIComponent(cleanTimeframe);

  const payload =
    await get<unknown>(
      `/api/live/candles/${encodedSymbol}?timeframe=${encodedTimeframe}`,
    );

  return normaliseResponse(
    payload,
    cleanSymbol,
    cleanTimeframe,
  );
}