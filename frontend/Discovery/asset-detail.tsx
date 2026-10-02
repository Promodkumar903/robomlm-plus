import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { ApiError } from "../src/api/client";
import {
  getAssetDecisionLayers,
  getAssetEvidence,
  getAssetIntelligence,
  getAssetMarketData,
  getDiscoveryOpportunity,
} from "../src/api/discovery";
import { Chart } from "../src/components/Chart";
import "./discovery.css";

type LoadResult = {
  value: unknown | null;
  error: string | null;
};

function readString(value: unknown, fallback = "—"): string {
  if (value === undefined || value === null) return fallback;
  if (typeof value === "string") return value.trim() || fallback;
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  return fallback;
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined) return "—";
  if (
    typeof value === "string" ||
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return String(value);
  }
  if (Array.isArray(value)) {
    return value.map((item) => formatValue(item)).join(" • ");
  }
  try {
    return JSON.stringify(value);
  } catch {
    return "—";
  }
}

function formatPercent(value: unknown): string {
  const numeric =
    typeof value === "number"
      ? value
      : typeof value === "string"
        ? Number(value)
        : NaN;

  if (!Number.isFinite(numeric)) return "—";

  const percent = Math.abs(numeric) <= 1 ? numeric * 100 : numeric;
  return `${percent.toFixed(2)}%`;
}

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return `${error.message} (HTTP ${error.status})`;
  }
  if (error instanceof Error) return error.message;
  return "Request failed.";
}

function getObject(value: unknown): Record<string, unknown> | null {
  if (value && typeof value === "object" && !Array.isArray(value)) {
    return value as Record<string, unknown>;
  }
  return null;
}

function extractObject(
  payload: unknown,
  keys: string[],
): Record<string, unknown> | null {
  const root = getObject(payload);
  if (!root) return null;
  for (const key of keys) {
    const value = getObject(root[key]);
    if (value) return value;
  }
  return root;
}

function DataGrid({ data }: { data: Record<string, unknown> | null }) {
  if (!data) {
    return <div className="discovery-empty">No structured data returned.</div>;
  }

  const entries = Object.entries(data);
  if (!entries.length) {
    return <div className="discovery-empty">No data returned.</div>;
  }

  return (
    <div className="discovery-data-grid">
      {entries.map(([key, value]) => (
        <div className="discovery-data-field" key={key}>
          <span className="discovery-data-label">{key.replace(/_/g, " ")}</span>
          <strong className="discovery-data-value">{formatValue(value)}</strong>
        </div>
      ))}
    </div>
  );
}

function PayloadBlock({
  title,
  result,
}: {
  title: string;
  result: LoadResult;
}) {
  return (
    <section className="discovery-section">
      <div className="discovery-section-header">
        <h2>{title}</h2>
        <span
          className={
            result.error ? "discovery-status error" : "discovery-status"
          }
        >
          {result.error ? "Unavailable" : "Loaded"}
        </span>
      </div>

      {result.error ? (
        <div className="discovery-error">{result.error}</div>
      ) : (
        <DataGrid
          data={extractObject(result.value, [
            "data", "result", "payload", "response",
          ])}
        />
      )}
    </section>
  );
}

export default function AssetDetail() {
  const [searchParams] = useSearchParams();

  const symbol = (searchParams.get("symbol") ?? "").trim();
  const market = searchParams.get("market") ?? "EQUITY";
  const venue = searchParams.get("venue") ?? "MASSIVE";
  const timeframe = searchParams.get("timeframe") ?? "1h";

  const [opportunity, setOpportunity] = useState<LoadResult>({
    value: null, error: null,
  });
  const [marketData, setMarketData] = useState<LoadResult>({
    value: null, error: null,
  });
  const [intelligence, setIntelligence] = useState<LoadResult>({
    value: null, error: null,
  });
  const [evidence, setEvidence] = useState<LoadResult>({
    value: null, error: null,
  });
  const [decisionLayers, setDecisionLayers] = useState<LoadResult>({
    value: null, error: null,
  });

  const [loading, setLoading] = useState(false);
  const [pageError, setPageError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      if (!symbol) {
        setPageError("No discovery symbol was supplied.");
        return;
      }

      setLoading(true);
      setPageError(null);

      const [
        opportunityResult,
        marketResult,
        intelligenceResult,
        evidenceResult,
        decisionResult,
      ] = await Promise.all([
        getDiscoveryOpportunity(symbol)
          .then((value) => ({ value, error: null }))
          .catch((error) => ({ value: null, error: getErrorMessage(error) })),

        getAssetMarketData(symbol, timeframe)
          .then((value) => ({ value, error: null }))
          .catch((error) => ({ value: null, error: getErrorMessage(error) })),

        getAssetIntelligence(symbol, timeframe)
          .then((value) => ({ value, error: null }))
          .catch((error) => ({ value: null, error: getErrorMessage(error) })),

        getAssetEvidence(symbol, timeframe)
          .then((value) => ({ value, error: null }))
          .catch((error) => ({ value: null, error: getErrorMessage(error) })),

        getAssetDecisionLayers(symbol, timeframe)
          .then((value) => ({ value, error: null }))
          .catch((error) => ({ value: null, error: getErrorMessage(error) })),
      ]);

      if (cancelled) return;

      setOpportunity(opportunityResult);
      setMarketData(marketResult);
      setIntelligence(intelligenceResult);
      setEvidence(evidenceResult);
      setDecisionLayers(decisionResult);

      const successful =
        opportunityResult.value !== null ||
        marketResult.value !== null ||
        intelligenceResult.value !== null ||
        evidenceResult.value !== null ||
        decisionResult.value !== null;

      if (!successful) {
        setPageError(
          "No Discovery detail data could be loaded from the backend.",
        );
      }

      setLoading(false);
    }

    void load();

    return () => {
      cancelled = true;
    };
  }, [symbol, market, venue, timeframe]);

  const opportunityObject = useMemo(
    () =>
      extractObject(opportunity.value, [
        "opportunity", "result", "data", "payload",
      ]),
    [opportunity.value],
  );

  const marketObject = useMemo(
    () =>
      extractObject(marketData.value, [
        "market", "market_data", "snapshot", "data", "result",
      ]),
    [marketData.value],
  );

  const price = useMemo(() => {
    if (!marketObject) return null;
    return (
      marketObject.price ??
      marketObject.last_price ??
      marketObject.close ??
      marketObject.last
    );
  }, [marketObject]);

  const change = useMemo(() => {
    if (!marketObject) return null;
    return (
      marketObject.change_percent ??
      marketObject.change_pct ??
      marketObject.percent_change ??
      marketObject.change
    );
  }, [marketObject]);

  if (!symbol) {
    return (
      <main className="discovery-page">
        <section className="discovery-section">
          <h1>Discovery Asset</h1>
          <div className="discovery-error">No symbol was provided.</div>
          <a className="discovery-link-button" href="/discovery">
            ← Back to Discovery
          </a>
        </section>
      </main>
    );
  }

  return (
    <main className="discovery-page">
      <header className="discovery-header">
        <div>
          <div className="discovery-eyebrow">DISCOVERY / OPPORTUNITY</div>
          <h1>{symbol}</h1>
          <p>Backend-generated opportunity detail and supporting context.</p>
        </div>

        <div className="discovery-header-actions">
          <span className="discovery-chip">{market}</span>
          <span className="discovery-chip">{venue}</span>
          <span className="discovery-chip">{timeframe}</span>
          <a className="discovery-link-button" href="/discovery">
            ← Discovery
          </a>
        </div>
      </header>

      {loading ? (
        <div className="discovery-loading">
          Loading backend opportunity data…
        </div>
      ) : null}

      {pageError ? (
        <div className="discovery-error">{pageError}</div>
      ) : null}

      <section className="discovery-asset-hero">
        <div>
          <span className="discovery-label">SYMBOL</span>
          <strong className="discovery-symbol">{symbol}</strong>
        </div>
        <div>
          <span className="discovery-label">LAST PRICE</span>
          <strong className="discovery-value">{formatValue(price)}</strong>
        </div>
        <div>
          <span className="discovery-label">CHANGE</span>
          <strong
            className={
              typeof change === "number" && change < 0
                ? "discovery-negative"
                : "discovery-positive"
            }
          >
            {formatPercent(change)}
          </strong>
        </div>
        <div>
          <span className="discovery-label">STATUS</span>
          <strong className="discovery-value">
            {loading
              ? "Loading"
              : opportunity.error
                ? "Opportunity unavailable"
                : "Available"}
          </strong>
        </div>
      </section>

      <section className="discovery-section">
        <div className="discovery-section-header">
          <h2>Price Chart</h2>
          <span className="discovery-muted">{timeframe}</span>
        </div>
        <Chart symbol={symbol} timeframe={timeframe} height={420} />
      </section>

      <PayloadBlock title="Opportunity" result={opportunity} />
      <PayloadBlock title="Market Data" result={marketData} />
      <PayloadBlock title="Intelligence" result={intelligence} />
      <PayloadBlock title="Evidence" result={evidence} />
      <PayloadBlock title="Decision Layers" result={decisionLayers} />

      {opportunityObject ? null : null}
    </main>
  );
}