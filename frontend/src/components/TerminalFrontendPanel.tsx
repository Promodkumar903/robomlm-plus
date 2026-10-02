// frontend/src/components/TerminalFrontendPanel.tsx
// ROBOMLM+ Terminal — main panel
// Reads canonical backend contract: GET /api/terminal/frontend
//
// Rules honoured here:
//   • Frontend displays only — never computes
//   • CRYPTO   → BINANCE (live)
//   • Non-crypto → MASSIVE unavailable → explicit state, no fake data
//   • "—" shown where backend supplies nothing
//   • BUY/SELL/HOLD are a display surface, not authorization
//
// ⚠️ COMPLETE FILE — replace entire file. Do NOT append.

import { useEffect, useMemo, useRef, useState } from "react";
import { Chart } from "./Chart";
import { getTerminalFrontend } from "../api/terminal";
import { getApiErrorMessage } from "../api/client";
import type {
  TerminalContextResponse,
  MarketId,
  ProviderId,
  TerminalSelection,
  ProviderAvailability,
  WatchlistItem,
} from "../types/terminal";

// ===========================================================================
// STATIC CONFIG — selector options
// ===========================================================================

const MARKETS: { id: MarketId; label: string; availability: ProviderAvailability }[] = [
  { id: "CRYPTO",    label: "CRYPTO",    availability: "LIVE" },
  { id: "EQUITY",    label: "EQUITY",    availability: "UNAVAILABLE" },
  { id: "INDEX",     label: "INDEX",     availability: "UNAVAILABLE" },
  { id: "FOREX",     label: "FOREX",     availability: "UNAVAILABLE" },
  { id: "FUTURES",   label: "FUTURES",   availability: "UNAVAILABLE" },
  { id: "OPTIONS",   label: "OPTIONS",   availability: "UNAVAILABLE" },
  { id: "COMMODITY", label: "COMMODITY", availability: "UNAVAILABLE" },
];

const SEGMENTS_BY_MARKET: Record<MarketId, string[]> = {
  CRYPTO:    ["SPOT", "FUTURES", "OPTIONS"],
  EQUITY:    ["SPOT", "OPTIONS"],
  INDEX:     ["SPOT"],
  FOREX:     ["SPOT"],
  FUTURES:   ["FUTURES"],
  OPTIONS:   ["OPTIONS"],
  COMMODITY: ["SPOT", "FUTURES"],
};

const INSTRUMENTS_BY_MARKET: Record<MarketId, string[]> = {
  CRYPTO:    ["SPOT", "FUTURE", "OPTION_CE", "OPTION_PE"],
  EQUITY:    ["EQUITY", "OPTION"],
  INDEX:     ["INDEX"],
  FOREX:     ["FOREX"],
  FUTURES:   ["FUTURE"],
  OPTIONS:   ["OPTION_CE", "OPTION_PE"],
  COMMODITY: ["COMMODITY", "FUTURE"],
};

const PROVIDERS_BY_MARKET: Record<MarketId, ProviderId[]> = {
  CRYPTO:    ["BINANCE"],
  EQUITY:    ["MASSIVE"],
  INDEX:     ["MASSIVE"],
  FOREX:     ["MASSIVE"],
  FUTURES:   ["MASSIVE"],
  OPTIONS:   ["MASSIVE"],
  COMMODITY: ["MASSIVE"],
};

const SYMBOLS_BY_MARKET: Record<MarketId, string[]> = {
  CRYPTO:    ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT"],
  EQUITY:    ["AAPL", "MSFT", "TSLA", "RELIANCE", "HDFC", "TCS"],
  INDEX:     ["SPX", "NDX", "NIFTY", "BANKNIFTY"],
  FOREX:     ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD"],
  FUTURES:   ["ES", "NQ", "CL", "GC"],
  OPTIONS:   ["BTC-31DEC25-100000-C", "AAPL-16OCT25-250-C"],
  COMMODITY: ["GC", "SI", "CL", "NG"],
};

const TIMEFRAMES = ["1m", "3m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1M"];

const QUICK_CHIPS: { label: string; market: MarketId; symbol: string; availability: ProviderAvailability }[] = [
  { label: "BTC",       market: "CRYPTO",    symbol: "BTC/USDT", availability: "LIVE" },
  { label: "ETH",       market: "CRYPTO",    symbol: "ETH/USDT", availability: "LIVE" },
  { label: "AAPL",      market: "EQUITY",    symbol: "AAPL",     availability: "UNAVAILABLE" },
  { label: "RELIANCE",  market: "EQUITY",    symbol: "RELIANCE", availability: "UNAVAILABLE" },
  { label: "HDFC",      market: "EQUITY",    symbol: "HDFC",     availability: "UNAVAILABLE" },
  { label: "EUR/USD",   market: "FOREX",     symbol: "EUR/USD",  availability: "UNAVAILABLE" },
  { label: "SPX",       market: "INDEX",     symbol: "SPX",      availability: "UNAVAILABLE" },
];

// ===========================================================================
// HELPERS
// ===========================================================================

function availabilityFor(market: MarketId): ProviderAvailability {
  return market === "CRYPTO" ? "LIVE" : "UNAVAILABLE";
}

function fmtPrice(v: string | number | null | undefined): string {
  if (v === null || v === undefined || v === "") return "—";
  const n = typeof v === "number" ? v : Number(v);
  if (!Number.isFinite(n)) return "—";
  return n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function fmtPercent(v: number | null | undefined): string {
  if (v === null || v === undefined) return "—";
  if (!Number.isFinite(v)) return "—";
  const sign = v >= 0 ? "+" : "";
  return `${sign}${v.toFixed(2)}%`;
}

function statusTone(status: string | null | undefined): "ok" | "warn" | "bad" | "muted" {
  const s = String(status ?? "").toUpperCase();
  if (["VALID", "LIVE", "READY", "APPROVED", "AUTHORIZED"].includes(s)) return "ok";
  if (["REVIEW", "REVIEW_REQUIRED", "INSUFFICIENT", "WAIT", "UNKNOWN", "NOT_READY"].includes(s)) return "warn";
  if (["INVALID", "BLOCKED", "REJECTED", "UNAVAILABLE", "NOT_SUPPORTED"].includes(s)) return "bad";
  return "muted";
}

// ===========================================================================
// SUB-COMPONENTS (inline)
// ===========================================================================

function Dot({ tone }: { tone: "ok" | "warn" | "bad" | "muted" }) {
  const color =
    tone === "ok" ? "#22c55e" :
    tone === "warn" ? "#f59e0b" :
    tone === "bad" ? "#ef4444" :
    "#4a5568";
  return (
    <span
      style={{
        display: "inline-block",
        width: 6,
        height: 6,
        borderRadius: "50%",
        background: color,
        boxShadow: tone === "ok" ? `0 0 6px ${color}` : undefined,
      }}
    />
  );
}

function StripRow({
  label,
  items,
}: {
  label: string;
  items: { label: string; value: string; tone?: "ok" | "warn" | "bad" | "muted" }[];
}) {
  return (
    <div className="rbm-strip">
      <div className="rbm-strip-label">{label}</div>
      <div className="rbm-strip-items">
        {items.map((it) => {
          const tone = it.tone ?? statusTone(it.value);
          return (
            <div key={it.label} className="rbm-strip-item">
              <span className="rbm-strip-item-label">{it.label}</span>
              <span className={`rbm-strip-item-value rbm-tone-${tone}`}>
                <Dot tone={tone} />
                <span>{it.value}</span>
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ===========================================================================
// MAIN PANEL
// ===========================================================================

export default function TerminalFrontendPanel() {
  // ---- Selection state -------------------------------------------------
  const [selection, setSelection] = useState<TerminalSelection>({
    market: "CRYPTO",
    segment: "SPOT",
    instrument: "SPOT",
    provider: "BINANCE",
    symbol: "BTC/USDT",
    timeframe: "1m",
  });

  // ---- Backend contract state -----------------------------------------
  const [contract, setContract] = useState<TerminalContextResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ---- Search / watchlist ---------------------------------------------
  const [searchQuery, setSearchQuery] = useState("");
  const [searchOpen, setSearchOpen] = useState(false);
  const searchInputRef = useRef<HTMLInputElement | null>(null);

  const [watchlist] = useState<WatchlistItem[]>([
    { symbol: "BTC/USDT", market: "CRYPTO", provider: "BINANCE" },
    { symbol: "ETH/USDT", market: "CRYPTO", provider: "BINANCE" },
    { symbol: "SOL/USDT", market: "CRYPTO", provider: "BINANCE" },
  ]);

  const [recent, setRecent] = useState<string[]>([
    "AAPL", "RELIANCE", "EUR/USD",
  ]);

  const isLive = availabilityFor(selection.market) === "LIVE";

  // ---- Fetch on selection change --------------------------------------
  useEffect(() => {
    if (!isLive || !selection.symbol) {
      setContract(null);
      setLoading(false);
      setError(null);
      return;
    }

    let cancelled = false;
    setLoading(true);
    setError(null);

    getTerminalFrontend({
      symbol: selection.symbol,
      timeframe: selection.timeframe,
      market: selection.market,
      instrument: selection.instrument,
    })
      .then((data) => {
        if (cancelled) return;
        setContract(data);
        setLoading(false);
      })
      .catch((err) => {
        if (cancelled) return;
        setError(getApiErrorMessage(err));
        setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [
    isLive,
    selection.symbol,
    selection.timeframe,
    selection.market,
    selection.instrument,
  ]);

  // ---- Derived data ----------------------------------------------------
  const snapshot = contract?.sections?.market?.data?.snapshot;
  const health = contract?.sections?.market?.data?.health;

  const ev = contract?.sections?.evidence?.data;
  const intel = contract?.sections?.intelligence?.data;
  const dec = contract?.sections?.decision?.data;
  const risk = contract?.sections?.risk?.data;
  const cas = contract?.sections?.cas?.data;

  const evidenceStrip = useMemo(() => {
    const r = ev?.result;
    return [
      { label: "AVAILABLE", value: ev?.available ? "YES" : "NO", tone: ev?.available ? "ok" as const : "bad" as const },
      { label: "STATUS", value: String(r?.status ?? "—") },
      { label: "PACKAGE", value: String(r?.package_result?.status ?? "—") },
      { label: "INPUTS", value: String(r?.input_count ?? "—"), tone: "muted" as const },
      { label: "ACCEPTED", value: String(r?.accepted_count ?? "—"), tone: "muted" as const },
      { label: "REJECTED", value: String(r?.rejected_count ?? "—"), tone: "muted" as const },
    ];
  }, [ev]);

  const intelligenceStrip = useMemo(() => {
    const r = intel?.result;
    return [
      { label: "STATE", value: String(r?.state ?? "—") },
      { label: "EVIDENCE", value: r?.evidence_score !== undefined ? String(r.evidence_score) : "—", tone: "muted" as const },
      { label: "CONTEXT", value: r?.context_score !== undefined ? String(r.context_score) : "—", tone: "muted" as const },
      { label: "SPECIALIZED", value: r?.specialized_score !== undefined ? String(r.specialized_score) : "—", tone: "muted" as const },
      { label: "CONFIDENCE", value: r?.confidence_score !== undefined ? String(r.confidence_score) : "—", tone: "muted" as const },
      { label: "COMMITMENT", value: r?.commitment_score !== undefined ? String(r.commitment_score) : "—", tone: "muted" as const },
    ];
  }, [intel]);

  const engineStrip = useMemo(() => {
    const engines = [
      { id: "EQE", status: "—" },
      { id: "MCT", status: "—" },
      { id: "LQS", status: "—" },
      { id: "MTS", status: "—" },
      { id: "REL", status: "—" },
      { id: "REG", status: "—" },
      { id: "MAG", status: "—" },
      { id: "STR", status: "—" },
      { id: "RSK", status: String(risk?.result?.contract_state ?? "—") },
      { id: "CAS", status: String(cas?.result?.status ?? "—") },
    ];
    return engines;
  }, [risk, cas]);

  const pipelineRows = useMemo(() => {
    return [
      { label: "Market Data",  value: health?.status ?? (isLive ? "—" : "UNAVAILABLE") },
      { label: "Evidence",     value: String(ev?.result?.status ?? (isLive ? "—" : "UNAVAILABLE")) },
      { label: "Intelligence", value: String(intel?.result?.state ?? (isLive ? "—" : "UNAVAILABLE")) },
      { label: "Decision",     value: String(dec?.result?.decision ?? (isLive ? "—" : "UNAVAILABLE")) },
      { label: "Risk",         value: String(risk?.result?.contract_state ?? (isLive ? "—" : "UNAVAILABLE")) },
      { label: "CAS",          value: String(cas?.result?.status ?? (isLive ? "—" : "UNAVAILABLE")) },
      { label: "Execution",    value: "UNAVAILABLE" },
    ];
  }, [health, ev, intel, dec, risk, cas, isLive]);

  // ---- Handlers --------------------------------------------------------
  const applySelection = (partial: Partial<TerminalSelection>) => {
    setSelection((prev) => {
      const next = { ...prev, ...partial };

      // Cascade resets if market changed
      if (partial.market && partial.market !== prev.market) {
        const market = partial.market;
        next.segment = SEGMENTS_BY_MARKET[market][0];
        next.instrument = INSTRUMENTS_BY_MARKET[market][0];
        next.provider = PROVIDERS_BY_MARKET[market][0];
        next.symbol = SYMBOLS_BY_MARKET[market][0] ?? "";
      }

      return next;
    });
  };

  const openSymbol = (market: MarketId, symbol: string) => {
    setRecent((prev) => {
      const filtered = prev.filter((s) => s !== symbol);
      return [symbol, ...filtered].slice(0, 5);
    });
    applySelection({ market, symbol });
    setSearchOpen(false);
    setSearchQuery("");
  };

  const submitSearch = () => {
    const q = searchQuery.trim();
    if (!q) return;

    // Naive resolution — will be replaced when backend symbol search exists.
    for (const market of Object.keys(SYMBOLS_BY_MARKET) as MarketId[]) {
      if (SYMBOLS_BY_MARKET[market].some((s) => s.toUpperCase() === q.toUpperCase())) {
        openSymbol(market, SYMBOLS_BY_MARKET[market].find((s) => s.toUpperCase() === q.toUpperCase())!);
        return;
      }
    }
    // Fallback: treat as CRYPTO pair
    openSymbol("CRYPTO", q);
  };

  // ---- Search suggestions ---------------------------------------------
  const searchResults = useMemo(() => {
    const q = searchQuery.trim().toUpperCase();
    if (!q) return [];

    const out: { market: MarketId; symbol: string; availability: ProviderAvailability }[] = [];
    for (const market of Object.keys(SYMBOLS_BY_MARKET) as MarketId[]) {
      for (const sym of SYMBOLS_BY_MARKET[market]) {
        if (sym.toUpperCase().includes(q)) {
          out.push({ market, symbol: sym, availability: availabilityFor(market) });
        }
      }
    }
    return out.slice(0, 12);
  }, [searchQuery]);

  // ---- Render ----------------------------------------------------------
  return (
    <div className="rbm-terminal">
      {/* ---------- HEADER ---------- */}
      <header className="rbm-header">
        <div className="rbm-logo">
          <span className="rbm-logo-mark">ROBOMLM+</span>
          <span className="rbm-logo-sub">TERMINAL</span>
        </div>

        <div className="rbm-search" ref={searchInputRef as never}>
          <span className="rbm-search-icon">⌕</span>
          <input
            className="rbm-search-input"
            placeholder="Search any symbol — BTC/USDT, AAPL, RELIANCE, EUR/USD…"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={() => setSearchOpen(true)}
            onBlur={() => setTimeout(() => setSearchOpen(false), 150)}
            onKeyDown={(e) => {
              if (e.key === "Enter") submitSearch();
              if (e.key === "Escape") setSearchOpen(false);
            }}
          />
          {searchOpen && searchResults.length > 0 && (
            <div className="rbm-search-results">
              {searchResults.map((r) => (
                <button
                  key={`${r.market}:${r.symbol}`}
                  className="rbm-search-result"
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={() => openSymbol(r.market, r.symbol)}
                >
                  <span className="rbm-search-result-symbol">{r.symbol}</span>
                  <span className="rbm-search-result-market">{r.market}</span>
                  <span className={`rbm-search-result-tag rbm-tone-${r.availability === "LIVE" ? "ok" : "warn"}`}>
                    {r.availability === "LIVE" ? "LIVE" : "UNAVAILABLE"}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="rbm-header-status">
          <span className="rbm-status-live">
            <Dot tone={isLive ? "ok" : "bad"} />
            {isLive ? "LIVE" : "OFFLINE"}
          </span>
          <span className="rbm-status-provider">
            {selection.provider}
          </span>
        </div>
      </header>

      {/* ---------- QUICK CHIPS ---------- */}
      <div className="rbm-chips">
        {QUICK_CHIPS.map((c) => (
          <button
            key={c.label}
            className={`rbm-chip ${selection.symbol === c.symbol ? "rbm-chip-active" : ""}`}
            onClick={() => openSymbol(c.market, c.symbol)}
            title={c.availability === "LIVE" ? "Live" : "Provider unavailable"}
          >
            {c.label}
            {c.availability !== "LIVE" && <span className="rbm-chip-warn">⚠</span>}
          </button>
        ))}
      </div>

      {/* ---------- LAYOUT ---------- */}
      <div className="rbm-layout">
        {/* ----- SIDEBAR: watchlist + recent ----- */}
        <aside className="rbm-sidebar">
          <div className="rbm-sidebar-block">
            <div className="rbm-sidebar-title">WATCHLIST</div>
            {watchlist.map((w) => (
              <button
                key={w.symbol}
                className="rbm-sidebar-item"
                onClick={() => openSymbol(w.market, w.symbol)}
              >
                <span className="rbm-sidebar-symbol">{w.symbol}</span>
                <span className="rbm-sidebar-market">{w.market}</span>
              </button>
            ))}
          </div>

          <div className="rbm-sidebar-block">
            <div className="rbm-sidebar-title">RECENT</div>
            {recent.map((s) => (
              <button
                key={s}
                className="rbm-sidebar-item"
                onClick={() => {
                  // Find market for this symbol
                  for (const market of Object.keys(SYMBOLS_BY_MARKET) as MarketId[]) {
                    if (SYMBOLS_BY_MARKET[market].includes(s)) {
                      openSymbol(market, s);
                      return;
                    }
                  }
                }}
              >
                <span className="rbm-sidebar-symbol">{s}</span>
              </button>
            ))}
          </div>
        </aside>

        {/* ----- MAIN ----- */}
        <main className="rbm-main">
          {/* SELECTOR BAR */}
          <div className="rbm-selector-bar">
            <Select
              label="MARKET"
              value={selection.market}
              options={MARKETS.map((m) => ({
                value: m.id,
                label: m.label + (m.availability === "LIVE" ? "" : " ⚠"),
              }))}
              onChange={(v) => applySelection({ market: v as MarketId })}
            />
            <Select
              label="SEGMENT"
              value={selection.segment}
              options={SEGMENTS_BY_MARKET[selection.market].map((s) => ({ value: s, label: s }))}
              onChange={(v) => applySelection({ segment: v })}
            />
            <Select
              label="INSTRUMENT"
              value={selection.instrument}
              options={INSTRUMENTS_BY_MARKET[selection.market].map((s) => ({ value: s, label: s }))}
              onChange={(v) => applySelection({ instrument: v })}
            />
            <Select
              label="PROVIDER"
              value={selection.provider}
              options={PROVIDERS_BY_MARKET[selection.market].map((p) => ({ value: p, label: p }))}
              onChange={(v) => applySelection({ provider: v as ProviderId })}
            />
            <Select
              label="SYMBOL"
              value={selection.symbol}
              options={SYMBOLS_BY_MARKET[selection.market].map((s) => ({ value: s, label: s }))}
              onChange={(v) => applySelection({ symbol: v })}
            />
            <Select
              label="TIMEFRAME"
              value={selection.timeframe}
              options={TIMEFRAMES.map((t) => ({ value: t, label: t }))}
              onChange={(v) => applySelection({ timeframe: v })}
            />
          </div>

          {/* BREADCRUMB */}
          <div className="rbm-breadcrumb">
            {[selection.market, selection.segment, selection.instrument, selection.provider, selection.symbol, selection.timeframe]
              .filter(Boolean)
              .join(" • ")}
            {" • "}
            <span className={isLive ? "rbm-tone-ok" : "rbm-tone-bad"}>
              {isLive ? "LIVE" : "UNAVAILABLE"}
            </span>
          </div>

          {/* NON-LIVE EXPLANATION */}
          {!isLive && (
            <div className="rbm-unavailable-card">
              <div className="rbm-unavailable-title">PROVIDER UNAVAILABLE</div>
              <div className="rbm-unavailable-body">
                {selection.market} market requires <strong>MASSIVE</strong> provider.
                MASSIVE API key is not configured on this backend.
                Select <strong>CRYPTO</strong> for live data, or configure MASSIVE on the server.
              </div>
            </div>
          )}

          {/* ERROR */}
          {isLive && error && (
            <div className="rbm-error-card">
              <div className="rbm-error-title">TERMINAL DATA UNAVAILABLE</div>
              <div className="rbm-error-body">{error}</div>
            </div>
          )}

          {/* LOADING */}
          {isLive && loading && !contract && (
            <div className="rbm-loading">Loading terminal context…</div>
          )}

          {/* CHART ROW */}
          <div className="rbm-chart-row">
            <div className="rbm-chart-col">
              <Chart
                symbol={selection.symbol}
                timeframe={selection.timeframe}
                height={420}
              />
            </div>

            <div className="rbm-snapshot-col">
              <div className="rbm-snapshot">
                <div className="rbm-snapshot-title">MARKET SNAPSHOT</div>
                <SnapRow label="Market"     value={snapshot?.market?.market ?? selection.market} />
                <SnapRow label="Segment"    value={snapshot?.market?.segment ?? selection.segment} />
                <SnapRow label="Instrument" value={snapshot?.instrument?.instrument_type ?? selection.instrument} />
                <SnapRow label="Provider"   value={snapshot?.venue?.venue ?? selection.provider} />
                <SnapRow label="Venue"      value={snapshot?.venue?.venue_id ?? "—"} />
                <SnapRow label="Symbol"     value={snapshot?.instrument?.symbol ?? selection.symbol} />
                <div className="rbm-snap-divider" />
                <SnapRow label="Last"       value={fmtPrice(snapshot?.observation?.price)} strong />
                <SnapRow label="High"       value={fmtPrice(snapshot?.observation?.high)} />
                <SnapRow label="Low"        value={fmtPrice(snapshot?.observation?.low)} />
                <SnapRow label="Volume"     value={fmtPrice(snapshot?.observation?.volume)} />
                <SnapRow label="Data"       value={health?.status ?? "—"} tone={statusTone(health?.status)} />
              </div>
            </div>
          </div>

          {/* STRIPS */}
          <StripRow label="EVIDENCE" items={evidenceStrip} />
          <StripRow label="INTELLIGENCE" items={intelligenceStrip} />

          {/* ENGINE STRIP */}
          <div className="rbm-engines">
            <div className="rbm-engines-label">ENGINES</div>
            <div className="rbm-engines-items">
              {engineStrip.map((e) => (
                <div key={e.id} className="rbm-engine">
                  <span className="rbm-engine-id">{e.id}</span>
                  <span className={`rbm-engine-status rbm-tone-${statusTone(e.status)}`}>
                    <Dot tone={statusTone(e.status)} />
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* DECISION + AUTHORIZATION */}
          <div className="rbm-decision-row">
            <div className="rbm-decision-box">
              <div className="rbm-box-title">DECISION OUTLOOK</div>
              <div className={`rbm-decision-signal rbm-tone-${statusTone(dec?.result?.decision)}`}>
                {String(dec?.result?.decision ?? "—")}
              </div>
              <div className="rbm-decision-rows">
                <SnapRow label="Direction"     value={String(dec?.result?.direction ?? "—")} />
                <SnapRow label="State"         value={String(intel?.result?.state ?? "—")} tone={statusTone(intel?.result?.state)} />
                <SnapRow label="Decision Ready" value={intel?.result?.decision_ready ? "YES" : "NO"} tone={intel?.result?.decision_ready ? "ok" : "warn"} />
                <SnapRow label="Authority"     value={contract?.authority?.decision_authority ?? "D13"} />
                <SnapRow label="Confidence"    value={String(dec?.result?.confidence ?? "—")} tone="muted" />
              </div>
            </div>

            <div className="rbm-auth-box">
              <div className="rbm-box-title">AUTHORIZATION</div>
              <div className="rbm-decision-rows">
                <SnapRow label="CAS STATUS"          value={String(cas?.result?.status ?? "—")} tone={statusTone(cas?.result?.status)} />
                <SnapRow label="Execution Authority" value={contract?.authority?.execution_authority ?? "CAS"} />
                <SnapRow label="D13 Context"         value={contract?.authority?.frontend_can_decide ? "—" : "REQUIRED"} tone="muted" />
                <SnapRow label="Risk"                value={String(risk?.result?.contract_state ?? "—")} tone={statusTone(risk?.result?.contract_state)} />
                <SnapRow label="Risk State"          value={String(risk?.result?.result?.risk_status ?? "—")} tone={statusTone(risk?.result?.result?.risk_status)} />
              </div>
            </div>
          </div>

          {/* ACTION BAR */}
          <div className="rbm-action-bar">
            <ActionButton label="BUY"  state={contract?.authority?.frontend_can_execute ? "active" : "blocked"} />
            <ActionButton label="SELL" state={contract?.authority?.frontend_can_execute ? "active" : "blocked"} />
            <ActionButton label="HOLD" state="active" />
          </div>

          {/* WHY */}
          <div className="rbm-why">
            <div className="rbm-box-title">WHY</div>
            <div className="rbm-why-body">
              {dec?.result?.gate_reasons?.length
                ? dec.result.gate_reasons.join(" ")
                : "No explanation available from backend."}
            </div>
          </div>

          {/* CONTRADICTIONS */}
          <div className="rbm-contradictions">
            <div className="rbm-box-title">CONTRADICTIONS</div>
            <div className="rbm-contradictions-body">
              {intel?.result?.contradiction
                ? `Contradiction detected: ${(intel.result.contradiction_flags ?? []).join(", ")}`
                : "No active contradiction"}
            </div>
          </div>

          {/* PIPELINE */}
          <div className="rbm-pipeline">
            <div className="rbm-box-title">PIPELINE STATUS</div>
            <div className="rbm-pipeline-rows">
              {pipelineRows.map((p) => {
                const tone = statusTone(p.value);
                return (
                  <div key={p.label} className="rbm-pipeline-row">
                    <span className="rbm-pipeline-label">{p.label}</span>
                    <span className={`rbm-pipeline-value rbm-tone-${tone}`}>
                      <Dot tone={tone} />
                      {p.value}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

// ===========================================================================
// Small presentational components
// ===========================================================================

function Select({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: { value: string; label: string }[];
  onChange: (v: string) => void;
}) {
  return (
    <label className="rbm-selector">
      <span className="rbm-selector-label">{label}</span>
      <select
        className="rbm-selector-input"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </label>
  );
}

function SnapRow({
  label,
  value,
  strong,
  tone,
}: {
  label: string;
  value: string;
  strong?: boolean;
  tone?: "ok" | "warn" | "bad" | "muted";
}) {
  const cls = tone ? `rbm-tone-${tone}` : strong ? "rbm-value-strong" : "";
  return (
    <div className="rbm-snap-row">
      <span className="rbm-snap-label">{label}</span>
      <span className={`rbm-snap-value ${cls}`}>{value || "—"}</span>
    </div>
  );
}

function ActionButton({
  label,
  state,
}: {
  label: "BUY" | "SELL" | "HOLD";
  state: "active" | "blocked";
}) {
  const cls = `rbm-action-btn rbm-action-${label.toLowerCase()} rbm-action-${state}`;
  return (
    <button className={cls} disabled={state === "blocked"}>
      <span className="rbm-action-label">{label}</span>
      {state === "blocked" && <span className="rbm-action-hint">BLOCKED</span>}
    </button>
  );
}