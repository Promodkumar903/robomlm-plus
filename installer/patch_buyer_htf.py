# patch_buyer_htf.py
# Fix: Buyer + HTF pages "Cannot read properties of undefined (reading 'trim')"
#
# 1. Backs up 4 files
# 2. Adds response normalizer to both API clients
# 3. Adds null-safe check to toSeconds in both page files
#
# Rule: backup fail => patch abort. Kuch delete nahi hota.

import os
import sys
import shutil
from datetime import datetime

ROOT = r"C:\Users\Administrator\ROBOMLM_PLUS"

BUYER_API = os.path.join(ROOT, "frontend", "src", "api", "buyer.ts")
HTF_API = os.path.join(ROOT, "frontend", "src", "api", "htfTrading.ts")
BUYER_PAGE = os.path.join(ROOT, "frontend", "Buyer", "index.tsx")
HTF_PAGE = os.path.join(ROOT, "frontend", "HTF_Trading", "htf-trading.tsx")

# ------------------------------------------------------------
# 1) buyer.ts - full rewrite
# ------------------------------------------------------------

BUYER_TS = r'''import { get } from "./client";

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
'''

# ------------------------------------------------------------
# 2) htfTrading.ts - full rewrite
# ------------------------------------------------------------

HTF_TS = r'''import { get } from "./client";

export interface HTFCandle {
  timestamp: number | string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number | null;
}

export interface HTFCandlesResponse {
  candles?: HTFCandle[];
  data?: HTFCandle[];
  series?: HTFCandle[];
}

// ------------------------------------------------------------
// Response normalizer (same logic as buyer.ts)
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

function normalizeOne(raw: unknown): HTFCandle | null {
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

function normalizeCandles(resp: unknown): HTFCandle[] {
  const arr = extractRawArray(resp);
  const out: HTFCandle[] = [];
  for (const raw of arr) {
    const c = normalizeOne(raw);
    if (c) out.push(c);
  }
  return out;
}

export async function getHTFLiveCandles(
  symbol: string,
  timeframe: string,
): Promise<HTFCandlesResponse> {
  const raw = await get<unknown>(
    `/api/live/candles/${encodeURIComponent(
      symbol.trim(),
    )}?timeframe=${encodeURIComponent(timeframe)}`,
  );
  const candles = normalizeCandles(raw);
  return { candles };
}
'''

# ------------------------------------------------------------
# 3) Page .tsx files - null-safe toSeconds
# ------------------------------------------------------------

OLD_SIG = """function toSeconds(
  value: number | string,
): number | null {
  if (typeof value === "number") {"""

NEW_SIG = """function toSeconds(
  value: number | string | undefined | null,
): number | null {
  if (value === null || value === undefined) {
    return null;
  }

  if (typeof value === "number") {"""

# ------------------------------------------------------------
# Helper
# ------------------------------------------------------------

def backup_only(path):
    if not os.path.isfile(path):
        print(f"SKIP (not found): {path}")
        return None
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = path + f".bak_{ts}"
    try:
        shutil.copy2(path, bak)
    except Exception as e:
        print(f"ERROR: backup failed -> {e}")
        return None
    if not os.path.isfile(bak):
        print("ERROR: backup not verified")
        return None
    return bak


def write_new(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def patch_tsx(path, label):
    if not os.path.isfile(path):
        print(f"SKIP (not found): {path}")
        return False

    with open(path, "r", encoding="utf-8") as f:
        src = f.read()

    if "value === null || value === undefined" in src and "undefined | null" in src:
        print(f"ALREADY PATCHED: {label}")
        return True

    if OLD_SIG not in src:
        print(f"WARN: signature block not found in {label} - skipping")
        return False

    new_src = src.replace(OLD_SIG, NEW_SIG, 1)

    bak = backup_only(path)
    if not bak:
        print(f"ABORT: {label} - no backup")
        return False

    write_new(path, new_src)
    print(f"PATCHED: {label}  (backup: {os.path.basename(bak)})")
    return True


def patch_api(path, content, label):
    if not os.path.isfile(path):
        print(f"SKIP (not found): {path}")
        return False

    bak = backup_only(path)
    if not bak:
        print(f"ABORT: {label} - no backup")
        return False

    write_new(path, content)
    print(f"PATCHED: {label}  (backup: {os.path.basename(bak)})")
    return True


def main():
    print("=" * 60)
    print("Patch: Buyer + HTF market data (trim crash fix)")
    print("=" * 60)

    results = []
    results.append(("buyer.ts", patch_api(BUYER_API, BUYER_TS, "frontend/src/api/buyer.ts")))
    results.append(("htfTrading.ts", patch_api(HTF_API, HTF_TS, "frontend/src/api/htfTrading.ts")))
    results.append(("Buyer/index.tsx", patch_tsx(BUYER_PAGE, "frontend/Buyer/index.tsx")))
    results.append(("HTF htf-trading.tsx", patch_tsx(HTF_PAGE, "frontend/HTF_Trading/htf-trading.tsx")))

    print()
    print("SUMMARY:")
    for name, ok in results:
        print(f"  {'OK ' if ok else 'FAIL'} {name}")

    print()
    print("Next: frontend restart karo (npm run dev)")
    print("Phir browser me reload karo.")


if __name__ == "__main__":
    main()