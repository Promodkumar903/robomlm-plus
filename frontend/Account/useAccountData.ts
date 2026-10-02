/**
 * Account data hook — wires Account page to backend.
 *
 * Endpoints:
 *   GET /api/account/summary           — balance, mode, currency
 *   GET /api/autorobomlm/portfolio/summary — equity, unrealized, realized
 *   GET /api/autorobomlm/positions     — open positions
 *   GET /api/bot/allocation            — auto vs mission split
 *   POST /api/account/mode             — set PAPER/LIVE
 *   POST /api/account/currency         — set INR/USD
 */

import { useCallback, useEffect, useState } from "react";

export type AccountMode = "REAL" | "DEMO";
export type Currency = "USD" | "USDT" | "INR";

export interface AccountSnapshot {
  balance: number | null;
  available: number | null;
  equity: number | null;
  margin: number | null;
  unrealizedPnl: number | null;
  realizedPnl: number | null;
}

export interface Position {
  symbol: string;
  side: string;
  quantity: number | null;
  entryPrice: number | null;
  markPrice: number | null;
  pnl: number | null;
  status: string;
}

export interface BrokerState {
  connected: boolean | null;
  provider: string;
  account: string;
  status: string;
}

export interface AllocationState {
  autoPct: number | null;
  missionPct: number | null;
  autoCapital: number | null;
  missionCapital: number | null;
}

export interface AccountData {
  snapshot: AccountSnapshot;
  broker: BrokerState;
  positions: Position[];
  allocation: AllocationState;
  mode: AccountMode;
  currency: Currency;
  loading: boolean;
  error: string | null;
  lastUpdated: string | null;
  refresh: () => Promise<void>;
  setMode: (mode: AccountMode) => Promise<void>;
  setCurrency: (currency: Currency) => Promise<void>;
}

const EMPTY_SNAPSHOT: AccountSnapshot = {
  balance: null,
  available: null,
  equity: null,
  margin: null,
  unrealizedPnl: null,
  realizedPnl: null,
};

const EMPTY_BROKER: BrokerState = {
  connected: null,
  provider: "Backend controlled",
  account: "\u2014",
  status: "NOT AVAILABLE",
};

const EMPTY_ALLOCATION: AllocationState = {
  autoPct: null,
  missionPct: null,
  autoCapital: null,
  missionCapital: null,
};

// Backend mode: PAPER | LIVE
// Frontend mode: DEMO | REAL
function backendToFrontendMode(raw: string): AccountMode {
  return raw.toUpperCase() === "LIVE" ? "REAL" : "DEMO";
}

function frontendToBackendMode(mode: AccountMode): string {
  return mode === "REAL" ? "LIVE" : "PAPER";
}

// Backend currency: INR | USD (USDT → USD)
function backendToFrontendCurrency(raw: string): Currency {
  const c = raw.toUpperCase();
  if (c === "INR") return "INR";
  return "USD";
}

function frontendToBackendCurrency(c: Currency): string {
  return c === "INR" ? "INR" : "USD";
}

function num(v: unknown): number | null {
  if (v === null || v === undefined) return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

const REFRESH_MS = 10_000;

export function useAccountData(): AccountData {
  const [snapshot, setSnapshot] = useState<AccountSnapshot>(EMPTY_SNAPSHOT);
  const [broker, setBroker] = useState<BrokerState>(EMPTY_BROKER);
  const [positions, setPositions] = useState<Position[]>([]);
  const [allocation, setAllocation] = useState<AllocationState>(EMPTY_ALLOCATION);
  const [mode, setModeState] = useState<AccountMode>("DEMO");
  const [currency, setCurrencyState] = useState<Currency>("INR");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      setError(null);

      const [
        summaryRes,
        portfolioRes,
        positionsRes,
        allocationRes,
      ] = await Promise.allSettled([
        fetch("/api/account/summary").then((r) => r.json()),
        fetch("/api/autorobomlm/portfolio/summary").then((r) => r.json()),
        fetch("/api/autorobomlm/positions").then((r) => r.json()),
        fetch("/api/bot/allocation").then((r) => r.json()),
      ]);

      let balance: number | null = null;
      let backendMode = "PAPER";
      let backendCurrency = "INR";

      if (summaryRes.status === "fulfilled" && summaryRes.value?.ok) {
        const s = summaryRes.value;
        balance = num(s.balance);
        backendMode = String(s.mode ?? "PAPER");
        backendCurrency = String(s.currency ?? "INR");
      }

      let equity: number | null = null;
      let unrealized: number | null = null;
      let realized: number | null = null;

      if (portfolioRes.status === "fulfilled" && portfolioRes.value?.ok) {
        const p = portfolioRes.value;
        equity = num(p.equity);
        unrealized = num(p.unrealized_pnl);
        realized = num(p?.portfolio?.realized_pnl);
      }

      let posList: Position[] = [];
      if (positionsRes.status === "fulfilled" && positionsRes.value?.ok) {
        const raw = positionsRes.value.positions ?? [];
        posList = raw.map((p: any) => ({
          symbol: String(p.symbol ?? ""),
          side: String(p.direction ?? ""),
          quantity: num(p.quantity),
          entryPrice: num(p.entry_price),
          markPrice: num(p.current_price),
          pnl: num(p.pnl),
          status: String(p.status ?? ""),
        }));
      }

      let autoPct: number | null = null;
      let missionPct: number | null = null;
      let autoCapital: number | null = null;
      let missionCapital: number | null = null;

      if (allocationRes.status === "fulfilled" && allocationRes.value?.ok) {
        const a = allocationRes.value;
        autoPct = num(a.auto_alloc_pct);
        missionPct = num(a.mission_alloc_pct);
        autoCapital = num(a.auto_capital);
        missionCapital = num(a.mission_capital);
      }

      // Available = allocated to auto bot
      const available =
        balance !== null && autoPct !== null
          ? (balance * autoPct) / 100
          : balance;

      setSnapshot({
        balance,
        available,
        equity,
        margin: null,
        unrealizedPnl: unrealized,
        realizedPnl: realized,
      });

      setBroker({
        connected: balance !== null,
        provider: "Backend controlled",
        account: "\u2014",
        status: balance !== null ? "CONNECTED" : "NOT AVAILABLE",
      });

      setPositions(posList);
      setAllocation({ autoPct, missionPct, autoCapital, missionCapital });

      setModeState(backendToFrontendMode(backendMode));
      setCurrencyState(backendToFrontendCurrency(backendCurrency));
      setLastUpdated(new Date().toISOString());
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
      setLoading(false);
    }
  }, []);

  const pushMode = useCallback(
    async (next: AccountMode) => {
      const backend = frontendToBackendMode(next);
      try {
        await fetch("/api/account/mode", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ mode: backend }),
        });
        setModeState(next);
        await refresh();
      } catch (err) {
        setError(err instanceof Error ? err.message : "Mode change failed");
      }
    },
    [refresh],
  );

  const pushCurrency = useCallback(
    async (next: Currency) => {
      const backend = frontendToBackendCurrency(next);
      try {
        await fetch("/api/account/currency", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ currency: backend }),
        });
        setCurrencyState(next);
        await refresh();
      } catch (err) {
        setError(err instanceof Error ? err.message : "Currency change failed");
      }
    },
    [refresh],
  );

  useEffect(() => {
    void refresh();
    const id = setInterval(() => {
      void refresh();
    }, REFRESH_MS);
    return () => clearInterval(id);
  }, [refresh]);

  return {
    snapshot,
    broker,
    positions,
    allocation,
    mode,
    currency,
    loading,
    error,
    lastUpdated,
    refresh,
    setMode: pushMode,
    setCurrency: pushCurrency,
  };
}
