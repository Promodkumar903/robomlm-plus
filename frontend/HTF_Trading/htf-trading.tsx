import React, {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import LiveChart from "./LiveChart";
import {
  getHTFLiveCandles,
  type HTFCandle,
} from "../src/api/htfTrading";

import "./htf_trading.css";

type HTFTimeframe =
  | "15m"
  | "30m"
  | "1h"
  | "4h";

interface NormalisedHTFCandle {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

function toSeconds(
  value: number | string | undefined | null,
): number | null {
  if (value === null || value === undefined) {
    return null;
  }

  if (typeof value === "number") {
    if (!Number.isFinite(value)) {
      return null;
    }

    return value > 10_000_000_000
      ? Math.floor(value / 1000)
      : Math.floor(value);
  }

  const trimmed = value.trim();

  if (!trimmed) {
    return null;
  }

  const numeric = Number(trimmed);

  if (Number.isFinite(numeric)) {
    return numeric > 10_000_000_000
      ? Math.floor(numeric / 1000)
      : Math.floor(numeric);
  }

  const parsed = Date.parse(trimmed);

  if (!Number.isFinite(parsed)) {
    return null;
  }

  return Math.floor(parsed / 1000);
}

function normaliseCandles(
  candles: HTFCandle[],
): NormalisedHTFCandle[] {
  const result: NormalisedHTFCandle[] = [];

  for (const candle of candles) {
    const timestamp = toSeconds(
      candle.timestamp,
    );

    if (timestamp === null) {
      continue;
    }

    const open = Number(candle.open);
    const high = Number(candle.high);
    const low = Number(candle.low);
    const close = Number(candle.close);

    if (
      !Number.isFinite(open) ||
      !Number.isFinite(high) ||
      !Number.isFinite(low) ||
      !Number.isFinite(close)
    ) {
      continue;
    }

    const volume =
      candle.volume === null ||
      candle.volume === undefined
        ? 0
        : Number(candle.volume);

    result.push({
      timestamp,
      open,
      high,
      low,
      close,
      volume: Number.isFinite(volume)
        ? volume
        : 0,
    });
  }

  result.sort(
    (a, b) =>
      a.timestamp - b.timestamp,
  );

  const unique = new Map<
    number,
    NormalisedHTFCandle
  >();

  for (const candle of result) {
    unique.set(
      candle.timestamp,
      candle,
    );
  }

  return Array.from(
    unique.values(),
  );
}

function formatNumber(
  value: number | null | undefined,
): string {
  if (
    value === null ||
    value === undefined ||
    !Number.isFinite(value)
  ) {
    return "--";
  }

  if (Math.abs(value) >= 1000) {
    return value.toLocaleString(
      undefined,
      {
        maximumFractionDigits: 2,
      },
    );
  }

  if (Math.abs(value) >= 1) {
    return value.toLocaleString(
      undefined,
      {
        maximumFractionDigits: 4,
      },
    );
  }

  return value.toLocaleString(
    undefined,
    {
      maximumFractionDigits: 8,
    },
  );
}

function formatTime(
  timestamp: number | null,
): string {
  if (
    timestamp === null ||
    !Number.isFinite(timestamp)
  ) {
    return "--";
  }

  return new Date(
    timestamp * 1000,
  ).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export default function HTFTrading() {
  const [symbol, setSymbol] =
    useState("BTCUSDT");

  const [activeSymbol, setActiveSymbol] =
    useState("BTCUSDT");

  const [timeframe, setTimeframe] =
    useState<HTFTimeframe>("1h");

  const [candles, setCandles] =
    useState<NormalisedHTFCandle[]>(
      [],
    );

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const [lastUpdated, setLastUpdated] =
    useState<number | null>(null);

  const loadMarket = useCallback(
    async (
      requestedSymbol = activeSymbol,
      requestedTimeframe = timeframe,
    ) => {
      const cleanSymbol =
        requestedSymbol.trim();

      if (!cleanSymbol) {
        setError(
          "Enter a symbol before loading market data.",
        );
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const response =
          await getHTFLiveCandles(
            cleanSymbol,
            requestedTimeframe,
          );

        const raw =
          response.candles ??
          response.data ??
          response.series ??
          [];

        const normalised =
          normaliseCandles(raw);

        setCandles(normalised);
        setActiveSymbol(cleanSymbol);
        setLastUpdated(Date.now());

        if (normalised.length === 0) {
          setError(
            "The backend returned no usable candle records.",
          );
        }
      } catch (requestError) {
        const message =
          requestError instanceof Error
            ? requestError.message
            : "Unable to load live market data.";

        setError(message);
        setCandles([]);
      } finally {
        setLoading(false);
      }
    },
    [activeSymbol, timeframe],
  );

  useEffect(() => {
    void loadMarket();
  }, [loadMarket]);

  const latest =
    candles.length > 0
      ? candles[candles.length - 1]
      : null;

  const previous =
    candles.length > 1
      ? candles[candles.length - 2]
      : null;

  const priceChange =
    latest && previous
      ? latest.close - previous.close
      : null;

  const priceChangePercent =
    latest &&
    previous &&
    previous.close !== 0
      ? (priceChange! /
          previous.close) *
        100
      : null;

  const high = useMemo(() => {
    if (candles.length === 0) {
      return null;
    }

    return Math.max(
      ...candles.map(
        (candle) => candle.high,
      ),
    );
  }, [candles]);

  const low = useMemo(() => {
    if (candles.length === 0) {
      return null;
    }

    return Math.min(
      ...candles.map(
        (candle) => candle.low,
      ),
    );
  }, [candles]);

  const volume = useMemo(() => {
    if (candles.length === 0) {
      return null;
    }

    return candles.reduce(
      (sum, candle) =>
        sum + candle.volume,
      0,
    );
  }, [candles]);

  const applyMarket = () => {
    const cleanSymbol =
      symbol.trim().toUpperCase();

    if (!cleanSymbol) {
      setError(
        "Enter a valid symbol.",
      );
      return;
    }

    setSymbol(cleanSymbol);

    void loadMarket(
      cleanSymbol,
      timeframe,
    );
  };

  const handleTimeframeChange = (
    value: HTFTimeframe,
  ) => {
    setTimeframe(value);

    void loadMarket(
      activeSymbol,
      value,
    );
  };

  return (
    <main className="htf-page">
      <header className="htf-header">
        <div>
          <p className="htf-eyebrow">
            ROBOMLM PLUS
          </p>

          <h1>
            HTF Trading
          </h1>

          <p className="htf-subtitle">
            Higher-timeframe market observation
            using backend-authoritative data.
          </p>
        </div>

        <div className="htf-provider-status">
          <span
            className={`htf-status-dot ${
              loading
                ? "loading"
                : error
                  ? "error"
                  : "live"
            }`}
          />

          <span>
            {loading
              ? "LOADING"
              : error
                ? "ERROR"
                : "LIVE DATA"}
          </span>
        </div>
      </header>

      <section className="htf-panel htf-selection">
        <div className="htf-section-heading">
          <div>
            <span className="htf-label">
              MARKET SELECTION
            </span>

            <h2>
              Configure HTF observation
            </h2>
          </div>

          <span className="htf-live-badge">
            BACKEND DATA
          </span>
        </div>

        <div className="htf-controls">
          <label>
            <span>Symbol</span>

            <input
              value={symbol}
              onChange={(event) =>
                setSymbol(
                  event.target.value,
                )
              }
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  applyMarket();
                }
              }}
              placeholder="BTCUSDT"
              spellCheck={false}
            />
          </label>

          <label>
            <span>Timeframe</span>

            <select
              value={timeframe}
              onChange={(event) =>
                handleTimeframeChange(
                  event.target
                    .value as HTFTimeframe,
                )
              }
            >
              <option value="15m">
                15m
              </option>

              <option value="30m">
                30m
              </option>

              <option value="1h">
                1h
              </option>

              <option value="4h">
                4h
              </option>
            </select>
          </label>

          <button
            type="button"
            onClick={applyMarket}
            disabled={loading}
          >
            {loading
              ? "Loading..."
              : "Load Market"}
          </button>
        </div>
      </section>

      {error && (
        <div
          className="htf-error"
          role="alert"
        >
          <strong>
            Market data error
          </strong>

          <span>{error}</span>
        </div>
      )}

      <section className="htf-market-grid">
        <article className="htf-panel htf-market-card">
          <span className="htf-label">
            ACTIVE SYMBOL
          </span>

          <strong>
            {activeSymbol || "--"}
          </strong>

          <small>
            {timeframe}
          </small>
        </article>

        <article className="htf-panel htf-market-card">
          <span className="htf-label">
            LAST PRICE
          </span>

          <strong>
            {formatNumber(
              latest?.close,
            )}
          </strong>

          <small
            className={
              priceChange !== null
                ? priceChange >= 0
                  ? "htf-positive"
                  : "htf-negative"
                : ""
            }
          >
            {priceChange !== null
              ? `${priceChange >= 0 ? "+" : ""}${formatNumber(priceChange)} (${priceChangePercent !== null ? `${priceChangePercent >= 0 ? "+" : ""}${priceChangePercent.toFixed(2)}%` : "--"})`
              : "--"}
          </small>
        </article>

        <article className="htf-panel htf-market-card">
          <span className="htf-label">
            HIGH / LOW
          </span>

          <strong>
            {formatNumber(high)}
          </strong>

          <small>
            Low {formatNumber(low)}
          </small>
        </article>

        <article className="htf-panel htf-market-card">
          <span className="htf-label">
            VOLUME
          </span>

          <strong>
            {formatNumber(volume)}
          </strong>

          <small>
            {candles.length} candles
          </small>
        </article>
      </section>

      <section className="htf-panel htf-live-chart">
        <div className="htf-chart-header">
          <div>
            <span className="htf-label">
              LIVE MARKET CHART
            </span>

            <h2>
              {activeSymbol} Ã‚Â· {timeframe}
            </h2>
          </div>

          <div className="htf-chart-meta">
            <span>
              {candles.length} candles
            </span>

            <span>
              Updated{" "}
              {lastUpdated
                ? new Date(
                    lastUpdated,
                  ).toLocaleTimeString()
                : "--"}
            </span>
          </div>
        </div>

                   <LiveChart
          candles={candles.map((candle) => ({
            time: candle.timestamp,
            open: candle.open,
            high: candle.high,
            low: candle.low,
            close: candle.close,
            volume: candle.volume,
          }))}
        />
        

        {latest && (
          <div className="htf-chart-footer">
            <span>
              Last candle{" "}
              {formatTime(
                latest.timestamp,
              )}
            </span>

            <span>
              O {formatNumber(latest.open)}
            </span>

            <span>
              H {formatNumber(latest.high)}
            </span>

            <span>
              L {formatNumber(latest.low)}
            </span>

            <span>
              C {formatNumber(latest.close)}
            </span>
          </div>
        )}
      </section>

      <section className="htf-grid">
        <article className="htf-panel">
          <div className="htf-section-heading">
            <div>
              <span className="htf-label">
                HTF CONTEXT
              </span>

              <h2>
                Market context
              </h2>
            </div>
          </div>

          <div className="htf-unavailable">
            <strong>
              Backend intelligence remains
              authoritative.
            </strong>

            <span>
              This frontend does not calculate
              an independent HTF signal.
            </span>
          </div>
        </article>

        <article className="htf-panel">
          <div className="htf-section-heading">
            <div>
              <span className="htf-label">
                D13 OUTLOOK
              </span>

              <h2>
                Decision outlook
              </h2>
            </div>
          </div>

          <div className="htf-unavailable">
            <strong>
              Not available through the
              verified frontend HTTP boundary.
            </strong>

            <span>
              No BUY, SELL or HOLD conclusion is
              manufactured in the browser.
            </span>
          </div>
        </article>

        <article className="htf-panel">
          <div className="htf-section-heading">
            <div>
              <span className="htf-label">
                RISK
              </span>

              <h2>
                Risk context
              </h2>
            </div>
          </div>

          <div className="htf-unavailable">
            <strong>
              Backend controlled
            </strong>

            <span>
              Risk calculations remain owned by
              the backend risk boundary.
            </span>
          </div>
        </article>

        <article className="htf-panel">
          <div className="htf-section-heading">
            <div>
              <span className="htf-label">
                CAS
              </span>

              <h2>
                Authorization
              </h2>
            </div>
          </div>

          <div className="htf-unavailable">
            <strong>
              Backend controlled
            </strong>

            <span>
              Frontend does not bypass CAS or
              execution authorization.
            </span>
          </div>
        </article>
      </section>

      <section className="htf-panel htf-note">
        <strong>
          HTF execution boundary
        </strong>

        <p>
          This page displays authoritative
          market data. It does not create
          trading decisions, submit orders, or
          replace the backend HTF intelligence,
          risk, CAS, or execution boundaries.
        </p>
      </section>
    </main>
  );
}
