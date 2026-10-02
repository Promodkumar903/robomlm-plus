import { useCallback, useEffect, useMemo, useState } from "react";
import { Chart } from "../src/components/Chart";
import "./discovery.css";

const API_BASE =
  (import.meta as ImportMeta & { env?: Record<string, string> }).env
    ?.VITE_API_BASE_URL || "http://127.0.0.1:8000";

type TabId = "scanner" | "top10" | "intraday" | "favorites";
type AnyRecord = Record<string, any>;

type PipelineStage = {
  stage: string;
  status: string;
  produces_trade_instruction?: boolean;
  data?: AnyRecord;
};

type DiscoveryResponse = {
  status?: string;
  stage?: string;
  surface?: string;
  pipeline_order?: string[];
  stages?: PipelineStage[];
  data?: AnyRecord;
  candidates?: AnyRecord[];
  top10?: AnyRecord[] | AnyRecord;
  opportunities?: AnyRecord[];
  [key: string]: any;
};

type Candidate = AnyRecord & {
  __index?: number;
  __symbol?: string;
  __score?: number | null;
  __confidence?: number | null;
  __status?: string;
  __market?: string;
  __venue?: string;
  __rank?: number | null;
  __direction?: string | null;
  __volume_ratio?: number | null;
};

const TABS: { id: TabId; label: string; hint: string }[] = [
  { id: "scanner", label: "SCANNER", hint: "Full market scan — backend order" },
  { id: "top10", label: "TOP 10", hint: "Best opportunities — highest score first" },
  { id: "intraday", label: "INTRADAY", hint: "High-activity short-term candidates" },
  { id: "favorites", label: "FAVORITES", hint: "Your starred symbols" },
];

const FAVORITES_STORAGE_KEY = "robomlm.discovery.favorites";

// ---------------------------------------------------------------------------
// FAVORITES (localStorage)
// ---------------------------------------------------------------------------

function loadFavorites(): string[] {
  try {
    const raw = localStorage.getItem(FAVORITES_STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (Array.isArray(parsed)) {
      return parsed.filter((s): s is string => typeof s === "string");
    }
  } catch {
    /* noop */
  }
  return [];
}

function saveFavorites(symbols: string[]): void {
  try {
    localStorage.setItem(FAVORITES_STORAGE_KEY, JSON.stringify(symbols));
  } catch {
    /* noop */
  }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function isRecord(value: unknown): value is AnyRecord {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function asNumber(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string" && value.trim() !== "") {
    const n = Number(value);
    return Number.isFinite(n) ? n : null;
  }
  return null;
}

function firstNumber(record: AnyRecord, names: string[]): number | null {
  for (const name of names) {
    const value = asNumber(record[name]);
    if (value !== null) return value;
  }
  return null;
}

function firstString(record: AnyRecord, names: string[]): string | null {
  for (const name of names) {
    const value = record[name];
    if (typeof value === "string" && value.trim()) return value;
    if (typeof value === "number") return String(value);
  }
  return null;
}

function formatNumber(value: number | null, digits = 2): string {
  if (value === null) return "—";
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: digits,
  }).format(value);
}

function formatPercent(value: number | null): string {
  if (value === null) return "—";
  const normalized = Math.abs(value) <= 1 ? value * 100 : value;
  return `${formatNumber(normalized, 2)}%`;
}

function toneForStatus(status: string): "ok" | "warn" | "bad" | "muted" {
  const s = status.toUpperCase();
  if (s.includes("ERROR") || s.includes("INVALID") || s.includes("FAIL")) return "bad";
  if (s.includes("EMPTY") || s.includes("WAIT") || s.includes("UNKNOWN") || s.includes("NOT")) return "warn";
  if (s.includes("COMPLETE") || s.includes("READY") || s.includes("OK")) return "ok";
  return "muted";
}

function normalizeCandidate(
  value: unknown,
  index: number,
  fallbackMarket: string,
  fallbackVenue: string,
): Candidate | null {
  if (!isRecord(value)) return null;

  const symbol =
    firstString(value, [
      "symbol", "ticker", "instrument_symbol",
      "exchange_symbol", "asset", "name",
    ]) || "UNKNOWN";

  const score = firstNumber(value, [
    "score", "ranking_score", "normalized_score",
    "rank_score", "opportunity_score",
    "eqe", "pfs", "mci",
  ]);

  const confidence = firstNumber(value, [
    "confidence", "confidence_score", "confidence_pct",
    "evidence_completeness",
  ]);

  const status =
    firstString(value, [
      "status", "state", "decision", "eligibility", "opportunity_status",
    ]) || "AVAILABLE";

  const direction = firstString(value, ["direction", "bias", "signal"]);
  const rank = firstNumber(value, ["rank", "ranking"]);

  const volumeRatio = firstNumber(value, [
    "volume_ratio", "volumeRatio", "vol_ratio",
  ]);

  const market =
    firstString(value, ["market", "market_id", "asset_class"]) || fallbackMarket;

  const venue =
    firstString(value, [
      "venue", "venue_id", "exchange", "exchange_name", "primary_exchange",
    ]) || fallbackVenue;

  return {
    ...value,
    __index: index,
    __symbol: symbol,
    __score: score,
    __confidence: confidence,
    __status: status,
    __market: market,
    __venue: venue,
    __rank: rank,
    __direction: direction,
    __volume_ratio: volumeRatio,
  };
}

function extractCandidates(payload: DiscoveryResponse): Candidate[] {
  const sources: unknown[] = [
    payload.data?.candidates,
    payload.data?.top10?.candidates,
    payload.candidates,
    payload.opportunities,
    payload.results,
    payload.assets,
    payload.items,
  ];

  if (Array.isArray(payload.top10)) {
    sources.push(payload.top10);
  } else if (isRecord(payload.top10)) {
    sources.push(payload.top10.candidates);
    sources.push(payload.top10.ranked);
    sources.push(payload.top10.decisions);
  }

  const found: unknown[] = [];
  for (const source of sources) {
    if (Array.isArray(source)) found.push(...source);
  }

  const market = firstString(payload, ["market", "market_id"]) || "UNKNOWN";
  const venue = firstString(payload, ["venue", "venue_id", "exchange"]) || "UNKNOWN";

  const normalized = found
    .map((item, index) => normalizeCandidate(item, index, market, venue))
    .filter((item): item is Candidate => item !== null);

  const seen = new Set<string>();
  return normalized.filter((c) => {
    const key = `${c.__symbol}|${c.__market}|${c.__venue}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function calculatePriceChange(candidate: Candidate): number | null {
  const open = firstNumber(candidate, ["open", "o"]);
  const close = firstNumber(candidate, ["close", "c", "price", "last"]);
  if (open === null || close === null || open === 0) return null;
  return ((close - open) / open) * 100;
}

function extractStages(payload: DiscoveryResponse): PipelineStage[] {
  if (Array.isArray(payload.stages)) return payload.stages;
  return [];
}

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url, {
    method: "GET",
    headers: { Accept: "application/json" },
  });

  const text = await response.text();
  let data: any = {};
  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    throw new Error(`Non-JSON response (${response.status}).`);
  }

  if (!response.ok) {
    const message =
      firstString(data, ["detail", "message", "error"]) ||
      `Request failed with HTTP ${response.status}.`;
    throw new Error(message);
  }

  return data as T;
}

// ---------------------------------------------------------------------------
// Market data enrichment (real prices)
// ---------------------------------------------------------------------------

interface MarketDataSnapshot {
  price: number | null;
  change: number | null;
  high: number | null;
  low: number | null;
  volume: number | null;
}

async function fetchMarketDataForSymbol(
  symbol: string,
): Promise<MarketDataSnapshot | null> {
  try {
    const url = `${API_BASE}/api/terminal/market-data?symbol=${encodeURIComponent(symbol)}`;
    const res = await fetch(url, {
      method: "GET",
      headers: { Accept: "application/json" },
    });

    if (!res.ok) return null;

    const data: any = await res.json();
    const obs = data?.market_snapshot?.observation;
    if (!obs) return null;

    const price = obs.price != null ? Number(obs.price) : null;
    const high = obs.high != null ? Number(obs.high) : null;
    const low = obs.low != null ? Number(obs.low) : null;
    const volume = obs.volume != null ? Number(obs.volume) : null;

    let change: number | null = null;
    if (price != null && high != null && low != null && low > 0) {
      change = ((price - low) / low) * 100;
    }

    return {
      price: Number.isFinite(price as number) ? price : null,
      change: Number.isFinite(change as number) ? change : null,
      high: Number.isFinite(high as number) ? high : null,
      low: Number.isFinite(low as number) ? low : null,
      volume: Number.isFinite(volume as number) ? volume : null,
    };
  } catch {
    return null;
  }
}

// ---------------------------------------------------------------------------
// Backend calls
// ---------------------------------------------------------------------------

async function getDiscovery(
  market: string,
  venue: string,
  timeframe: string,
  limit: number,
): Promise<DiscoveryResponse> {
  const params = new URLSearchParams();
  if (market) params.set("market", market);
  if (venue) params.set("venue", venue);
  if (timeframe) params.set("timeframe", timeframe);
  params.set("limit", String(limit));
  return fetchJson<DiscoveryResponse>(`${API_BASE}/api/discovery?${params.toString()}`);
}

async function getPipeline(
  market: string,
  venue: string,
  timeframe: string,
  limit: number,
): Promise<PipelineStage[]> {
  const params = new URLSearchParams();
  if (market) params.set("market", market);
  if (venue) params.set("venue", venue);
  if (timeframe) params.set("timeframe", timeframe);
  params.set("limit", String(limit));
  const data = await fetchJson<DiscoveryResponse>(
    `${API_BASE}/api/discovery?${params.toString()}`,
  );
  return extractStages(data);
}

// ---------------------------------------------------------------------------
// Tab-specific transforms
// ---------------------------------------------------------------------------

function sortByScoreDesc(rows: Candidate[]): Candidate[] {
  return [...rows].sort((a, b) => {
    const sa = a.__score ?? -Infinity;
    const sb = b.__score ?? -Infinity;
    if (sb !== sa) return sb - sa;
    return (a.__symbol ?? "").localeCompare(b.__symbol ?? "");
  });
}

function applyTabTransform(
  tab: TabId,
  raw: Candidate[],
  favorites: string[],
  limit: number,
): Candidate[] {
  switch (tab) {
    case "scanner":
      // Backend order, as-is.
      return raw.slice(0, limit);

    case "top10":
      // Highest score first, only top 10.
      return sortByScoreDesc(raw).slice(0, 10);

    case "intraday": {
      // High-activity candidates. Filter by volume ratio > 1.2 if present.
      const filtered = raw.filter((c) => {
        const vr = c.__volume_ratio;
        if (vr === null || vr === undefined) return true; // keep if unknown
        return vr >= 1.2;
      });
      return sortByScoreDesc(filtered).slice(0, limit);
    }

    case "favorites": {
      const favSet = new Set(favorites);
      return raw.filter((c) => favSet.has(c.__symbol || ""));
    }

    default:
      return raw;
  }
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function DiscoveryScanner() {
  const [tab, setTab] = useState<TabId>("scanner");
  const [market, setMarket] = useState("CRYPTO");
  const [venue, setVenue] = useState("BINANCE");
  const [instrument, setInstrument] = useState("");
  const [timeframe, setTimeframe] = useState("1h");
  const [limit, setLimit] = useState(10);

  const [data, setData] = useState<DiscoveryResponse | null>(null);
  const [stages, setStages] = useState<PipelineStage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState<Candidate | null>(null);
  const [notExposed, setNotExposed] = useState(false);

  const [enrichedMap, setEnrichedMap] = useState<
    Record<string, MarketDataSnapshot>
  >({});

  const [favorites, setFavorites] = useState<string[]>(() => loadFavorites());

  // Persist favorites
  useEffect(() => {
    saveFavorites(favorites);
  }, [favorites]);

  const toggleFavorite = useCallback((symbol: string) => {
    setFavorites((prev) => {
      if (prev.includes(symbol)) {
        return prev.filter((s) => s !== symbol);
      }
      return [...prev, symbol];
    });
  }, []);

  const runDiscovery = useCallback(async () => {
    setLoading(true);
    setError("");
    setNotExposed(false);

    try {
      const [tabResult, pipelineResult] = await Promise.all([
        getDiscovery(market, venue, timeframe, limit),
        getPipeline(market, venue, timeframe, limit).catch(
          () => [] as PipelineStage[],
        ),
      ]);

      if (tabResult.status === "NOT_EXPOSED") {
        setNotExposed(true);
        setData(null);
        setEnrichedMap({});
      } else {
        setData(tabResult);

        // Fetch real market data for candidates in parallel.
        const raw = extractCandidates(tabResult);
        const map: Record<string, MarketDataSnapshot> = {};

        await Promise.all(
          raw.map(async (c) => {
            if (!c.__symbol) return;
            const md = await fetchMarketDataForSymbol(c.__symbol);
            if (md) map[c.__symbol] = md;
          }),
        );

        setEnrichedMap(map);
      }

      setStages(pipelineResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load Discovery.");
      setData(null);
      setEnrichedMap({});
    } finally {
      setLoading(false);
    }
  }, [market, venue, timeframe, limit]);

  useEffect(() => {
    runDiscovery();
  }, [runDiscovery]);

  // Full candidate list (with prices merged)
  const allCandidates = useMemo(() => {
    if (!data) return [];
    const raw = extractCandidates(data);
    return raw.map((c) => {
      const md = enrichedMap[c.__symbol || ""];
      if (!md) return c;
      return {
        ...c,
        price: md.price,
        change_pct: md.change,
        high: md.high,
        low: md.low,
        volume: md.volume,
      };
    });
  }, [data, enrichedMap]);

  // Tab-specific view
  const candidates = useMemo(
    () => applyTabTransform(tab, allCandidates, favorites, limit),
    [tab, allCandidates, favorites, limit],
  );

  // Auto-select first row on tab/data change
  useEffect(() => {
    if (candidates.length > 0) {
      setSelected(candidates[0]);
    } else {
      setSelected(null);
    }
  }, [candidates]);

  const activeTabHint = TABS.find((t) => t.id === tab)?.hint ?? "";

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------

  return (
    <div className="discovery-page">
      <header className="discovery-header">
        <div>
          <div className="eyebrow">ROBOMLM</div>
          <h1>DISCOVERY</h1>
          <p>Cross-market opportunity scanner</p>
        </div>
        <div className="discovery-header-status">
          <span
            className={
              loading
                ? "status-dot loading"
                : error
                  ? "status-dot error"
                  : "status-dot ready"
            }
          />
          {loading ? "LOADING" : error ? "ERROR" : "BACKEND CONNECTED"}
        </div>
      </header>

      {/* FILTERS */}
      <section className="discovery-controls">
        <label>
          <span>Market</span>
          <select value={market} onChange={(e) => setMarket(e.target.value)}>
            <option value="CRYPTO">CRYPTO</option>
            <option value="EQUITY">EQUITY</option>
            <option value="FOREX">FOREX</option>
            <option value="OPTIONS">OPTIONS</option>
            <option value="FUTURES">FUTURES</option>
            <option value="INDEX">INDEX</option>
            <option value="COMMODITY">COMMODITY</option>
          </select>
        </label>

        <label>
          <span>Venue</span>
          <select value={venue} onChange={(e) => setVenue(e.target.value)}>
            <option value="BINANCE">BINANCE</option>
            <option value="MASSIVE">MASSIVE</option>
          </select>
        </label>

        <label>
          <span>Instrument</span>
          <input
            value={instrument}
            onChange={(e) => setInstrument(e.target.value)}
            placeholder="Optional"
          />
        </label>

        <label>
          <span>Timeframe</span>
          <select value={timeframe} onChange={(e) => setTimeframe(e.target.value)}>
            <option value="1m">1m</option>
            <option value="5m">5m</option>
            <option value="15m">15m</option>
            <option value="1h">1h</option>
            <option value="4h">4h</option>
            <option value="1d">1d</option>
          </select>
        </label>

        <label>
          <span>Limit</span>
          <select value={limit} onChange={(e) => setLimit(Number(e.target.value))}>
            <option value={10}>10</option>
            <option value={25}>25</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
          </select>
        </label>

        <button className="discovery-run" onClick={runDiscovery} disabled={loading}>
          {loading ? "LOADING..." : "RUN DISCOVERY"}
        </button>
      </section>

      {/* TABS */}
      <div className="discovery-tabs">
        {TABS.map((t) => (
          <button
            key={t.id}
            className={`discovery-tab ${tab === t.id ? "discovery-tab-active" : ""}`}
            onClick={() => setTab(t.id)}
          >
            {t.label}
            {t.id === "favorites" && favorites.length > 0 && (
              <span className="tab-badge">{favorites.length}</span>
            )}
          </button>
        ))}
      </div>

      {/* TAB HINT */}
      <div className="discovery-tab-hint">{activeTabHint}</div>

      {/* PIPELINE */}
      {stages.length > 0 && (
        <div className="discovery-pipeline-strip">
          <span className="pipeline-strip-label">PIPELINE</span>
          {stages.map((s) => {
            const tone = toneForStatus(s.status || "UNKNOWN");
            return (
              <span key={s.stage} className={`pipeline-dot pipeline-dot-${tone}`}>
                <span className="pipeline-dot-mark" />
                <span className="pipeline-dot-name">{s.stage}</span>
              </span>
            );
          })}
        </div>
      )}

      {/* ERROR */}
      {error && (
        <section className="discovery-error">
          <strong>BACKEND ERROR</strong>
          <span>{error}</span>
        </section>
      )}

      {/* TABLE + CHART */}
      <section className="discovery-results">
        <div className="section-heading">
          <div>
            <span className="eyebrow">BACKEND RESULT</span>
            <h2>
              {tab === "top10"
                ? "TOP 10 OPPORTUNITIES"
                : tab === "intraday"
                  ? "INTRADAY CANDIDATES"
                  : tab === "favorites"
                    ? "FAVORITES"
                    : "SCANNER CANDIDATES"}
            </h2>
          </div>
          <span className="result-status">
            {data?.status || (notExposed ? "NOT EXPOSED" : "WAITING")}
          </span>
        </div>

        <div className="discovery-split">
          <div className="discovery-table-wrap">
            {notExposed ? (
              <div className="empty-state">
                <strong>ENDPOINT NOT EXPOSED</strong>
                <span>
                  The backend reports this discovery view as NOT_EXPOSED.
                </span>
              </div>
            ) : candidates.length === 0 ? (
              <div className="empty-state">
                {tab === "favorites" ? (
                  <>
                    <strong>NO FAVORITES YET</strong>
                    <span>
                      Click the ☆ star on any row to add it to favorites.
                    </span>
                  </>
                ) : tab === "intraday" ? (
                  <>
                    <strong>NO INTRADAY CANDIDATES</strong>
                    <span>
                      No candidates met the intraday criteria for this market.
                      Try a different market or timeframe.
                    </span>
                  </>
                ) : (
                  <>
                    <strong>NO CANDIDATES RECEIVED</strong>
                    <span>
                      Frontend will not create or invent candidates.
                      When the backend/provider returns instruments, they will appear here.
                    </span>
                  </>
                )}
              </div>
            ) : (
              <table className="discovery-table">
                <thead>
                  <tr>
                    <th>{tab === "top10" ? "RANK" : "#"}</th>
                    <th>ASSET</th>
                    <th>MARKET</th>
                    <th>VENUE</th>
                    <th>PRICE</th>
                    <th>CHANGE</th>
                    <th>SCORE</th>
                    <th>CONF</th>
                    <th>STATUS</th>
                    <th title="Favorite">★</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {candidates.map((candidate, index) => {
                    const price = firstNumber(candidate, ["price", "last", "close", "c"]);
                    const change =
                      firstNumber(candidate, [
                        "change_pct", "changePercent", "percent_change", "pct_change",
                      ]) ?? calculatePriceChange(candidate);

                    const isSelected =
                      selected?.__symbol === candidate.__symbol &&
                      selected?.__market === candidate.__market;

                    const isFavorite = favorites.includes(candidate.__symbol || "");

                    const changeClass =
                      change === null
                        ? "td-num"
                        : change >= 0
                          ? "td-num td-pos"
                          : "td-num td-neg";

                    return (
                      <tr
                        key={`${candidate.__symbol}-${index}`}
                        className={isSelected ? "row-selected" : ""}
                        onClick={() => setSelected(candidate)}
                      >
                        <td className="td-rank">
                          {tab === "top10" ? index + 1 : index + 1}
                        </td>
                        <td className="td-symbol">{candidate.__symbol}</td>
                        <td className="td-muted">{candidate.__market}</td>
                        <td className="td-muted">{candidate.__venue}</td>
                        <td className="td-num">{formatNumber(price)}</td>
                        <td className={changeClass}>{formatPercent(change)}</td>
                        <td className="td-num">{formatNumber(candidate.__score ?? null)}</td>
                        <td className="td-num">{formatPercent(candidate.__confidence ?? null)}</td>
                        <td>
                          <span className="candidate-status">
                            {candidate.__status}
                          </span>
                        </td>
                        <td>
                          <button
                            className={`star-button ${isFavorite ? "star-on" : "star-off"}`}
                            title={isFavorite ? "Remove from favorites" : "Add to favorites"}
                            onClick={(e) => {
                              e.stopPropagation();
                              toggleFavorite(candidate.__symbol || "");
                            }}
                          >
                            {isFavorite ? "★" : "☆"}
                          </button>
                        </td>
                        <td>
                          <button
                            className="open-button"
                            onClick={(e) => {
                              e.stopPropagation();
                              const params = new URLSearchParams({
                                symbol: candidate.__symbol || "",
                                timeframe,
                                market: candidate.__market || market,
                                venue: candidate.__venue || venue,
                              });
                              window.location.href = `/discovery/asset?${params.toString()}`;
                            }}
                          >
                            →
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>

          {/* CHART PANEL */}
          <aside className="discovery-chart-panel">
            {selected ? (
              <>
                <div className="chart-panel-head">
                  <div>
                    <div className="chart-panel-symbol">{selected.__symbol}</div>
                    <div className="chart-panel-meta">
                      {selected.__market} • {selected.__venue} • {timeframe}
                    </div>
                  </div>
                  <button
                    className={`star-button-lg ${favorites.includes(selected.__symbol || "") ? "star-on" : "star-off"}`}
                    onClick={() => toggleFavorite(selected.__symbol || "")}
                    title={
                      favorites.includes(selected.__symbol || "")
                        ? "Remove from favorites"
                        : "Add to favorites"
                    }
                  >
                    {favorites.includes(selected.__symbol || "") ? "★" : "☆"}
                  </button>
                </div>

                <Chart
                  symbol={selected.__symbol || ""}
                  timeframe={timeframe}
                  height={300}
                />

                <div className="chart-intelligence">
                  <div className="chart-intelligence-title">INTELLIGENCE</div>

                  <div className="ci-row">
                    <span className="ci-label">SIGNAL</span>
                    <span className="ci-value">{selected.__direction ?? "—"}</span>
                  </div>

                  <div className="ci-row">
                    <span className="ci-label">SCORE</span>
                    <span className="ci-value">
                      <span className="ci-bar">
                        <span
                          className="ci-bar-fill"
                          style={{
                            width: `${Math.min(100, Math.max(0, selected.__score ?? 0))}%`,
                          }}
                        />
                      </span>
                      {formatNumber(selected.__score ?? null)}
                    </span>
                  </div>

                  <div className="ci-row">
                    <span className="ci-label">CONFIDENCE</span>
                    <span className="ci-value">
                      <span className="ci-bar">
                        <span
                          className="ci-bar-fill"
                          style={{
                            width: `${Math.min(100, Math.max(0, (selected.__confidence ?? 0) <= 1 ? (selected.__confidence ?? 0) * 100 : (selected.__confidence ?? 0)))}%`,
                          }}
                        />
                      </span>
                      {formatPercent(selected.__confidence ?? null)}
                    </span>
                  </div>

                  <div className="ci-row">
                    <span className="ci-label">RANK</span>
                    <span className="ci-value">{selected.__rank ?? "—"}</span>
                  </div>

                  <div className="ci-row">
                    <span className="ci-label">STATUS</span>
                    <span className="ci-value">{selected.__status ?? "—"}</span>
                  </div>
                </div>

                <button
                  className="chart-open-detail"
                  onClick={() => {
                    const params = new URLSearchParams({
                      symbol: selected.__symbol || "",
                      timeframe,
                      market: selected.__market || market,
                      venue: selected.__venue || venue,
                    });
                    window.location.href = `/discovery/asset?${params.toString()}`;
                  }}
                >
                  OPEN DETAIL →
                </button>
              </>
            ) : (
              <div className="chart-panel-empty">
                <strong>SELECT A ROW</strong>
                <span>Click any row to view chart and intelligence.</span>
              </div>
            )}
          </aside>
        </div>
      </section>

      <section className="discovery-note">
        <strong>DATA RULE</strong>
        <span>
          Values come from backend. Frontend never fabricates prices,
          candidates, scores, confidence, or trades.
        </span>
      </section>
    </div>
  );
}