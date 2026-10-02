import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  ColorType,
  CandlestickSeries,
  HistogramSeries,
  createChart,
  type CandlestickData,
  type HistogramData,
  type Time,
} from "lightweight-charts";

import {
  getBuyerLiveCandles,
  type BuyerCandle,
  type BuyerMode,
} from "../src/api/buyer";

import "./buyer.css";

type BuyerTimeframe =
  | "1m"
  | "3m"
  | "5m"
  | "15m"
  | "30m"
  | "1h"
  | "4h";

interface NormalisedBuyerCandle {
  time: Time;
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
  candles: BuyerCandle[],
): NormalisedBuyerCandle[] {
  const mapped: NormalisedBuyerCandle[] = [];

  for (const candle of candles) {
    const seconds = toSeconds(
      candle.timestamp,
    );

    if (seconds === null) {
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

    mapped.push({
      time: seconds as Time,
      timestamp: seconds,
      open,
      high,
      low,
      close,
      volume: Number.isFinite(volume)
        ? volume
        : 0,
    });
  }

  mapped.sort(
    (a, b) =>
      a.timestamp - b.timestamp,
  );

  const unique = new Map<
    number,
    NormalisedBuyerCandle
  >();

  for (const candle of mapped) {
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

interface BuyerLiveChartProps {
  candles: NormalisedBuyerCandle[];
}

function BuyerLiveChart({
  candles,
}: BuyerLiveChartProps) {
  const containerRef =
    useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const container =
      containerRef.current;

    if (!container) {
      return;
    }

    const chart = createChart(
      container,
      {
        width: container.clientWidth,
        height: 500,
        layout: {
          background: {
            type: ColorType.Solid,
            color: "transparent",
          },
          textColor: "#94a3b8",
        },
        grid: {
          vertLines: {
            color:
              "rgba(148,163,184,0.08)",
          },
          horzLines: {
            color:
              "rgba(148,163,184,0.08)",
          },
        },
        rightPriceScale: {
          borderColor:
            "rgba(148,163,184,0.12)",
        },
        timeScale: {
          borderColor:
            "rgba(148,163,184,0.12)",
          timeVisible: true,
          secondsVisible: false,
        },
        crosshair: {
          vertLine: {
            color:
              "rgba(59,130,246,0.35)",
          },
          horzLine: {
            color:
              "rgba(59,130,246,0.35)",
          },
        },
      },
    );

    const candleSeries =
      chart.addSeries(
        CandlestickSeries,
        {
          upColor: "#10b981",
          downColor: "#ef4444",
          borderUpColor: "#10b981",
          borderDownColor: "#ef4444",
          wickUpColor: "#10b981",
          wickDownColor: "#ef4444",
        },
      );

    const volumeSeries =
      chart.addSeries(
        HistogramSeries,
        {
          priceFormat: {
            type: "volume",
          },
          priceScaleId: "volume",
          color:
            "rgba(59,130,246,0.35)",
        },
      );

    chart.priceScale(
      "volume",
    ).applyOptions({
      scaleMargins: {
        top: 0.82,
        bottom: 0,
      },
    });

    const candleData: CandlestickData<Time>[] =
      candles.map((candle) => ({
        time: candle.time,
        open: candle.open,
        high: candle.high,
        low: candle.low,
        close: candle.close,
      }));

    const volumeData: HistogramData<Time>[] =
      candles.map((candle) => ({
        time: candle.time,
        value: candle.volume,
        color:
          candle.close >= candle.open
            ? "rgba(16,185,129,0.35)"
            : "rgba(239,68,68,0.35)",
      }));

    candleSeries.setData(
      candleData,
    );

    volumeSeries.setData(
      volumeData,
    );

    if (candles.length > 0) {
      chart.timeScale().fitContent();
    }

    const resizeObserver =
      new ResizeObserver(() => {
        const current =
          containerRef.current;

        if (!current) {
          return;
        }

        chart.applyOptions({
          width: current.clientWidth,
        });
      });

    resizeObserver.observe(container);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
    };
  }, [candles]);

  if (candles.length === 0) {
    return (
      <div className="buyer-chart-empty">
        <span>
          No live candle data available.
        </span>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="buyer-chart-container"
    />
  );
}

export default function Buyer() {
  const [symbol, setSymbol] =
    useState("BTCUSDT");

  const [market, setMarket] =
    useState("SPOT");

  const [instrument, setInstrument] =
    useState("");

  const [contract, setContract] =
    useState("");

  const [strategy, setStrategy] =
    useState("");

  const [timeframe, setTimeframe] =
    useState<BuyerTimeframe>("1m");

  const [mode, setMode] =
    useState<BuyerMode>("ANALYSIS");

  const [activeSymbol, setActiveSymbol] =
    useState("BTCUSDT");

  const [candles, setCandles] =
    useState<NormalisedBuyerCandle[]>(
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
          await getBuyerLiveCandles(
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

  const sessionHigh = useMemo(() => {
    if (candles.length === 0) {
      return null;
    }

    return Math.max(
      ...candles.map(
        (candle) => candle.high,
      ),
    );
  }, [candles]);

  const sessionLow = useMemo(() => {
    if (candles.length === 0) {
      return null;
    }

    return Math.min(
      ...candles.map(
        (candle) => candle.low,
      ),
    );
  }, [candles]);

  const totalVolume = useMemo(() => {
    if (candles.length === 0) {
      return null;
    }

    return candles.reduce(
      (sum, candle) =>
        sum + candle.volume,
      0,
    );
  }, [candles]);

  const applySelection = () => {
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
    value: BuyerTimeframe,
  ) => {
    setTimeframe(value);

    void loadMarket(
      activeSymbol,
      value,
    );
  };

  return (
    <main className="buyer-page">
      <header className="buyer-header">
        <div>
          <p className="buyer-eyebrow">
            ROBOMLM PLUS
          </p>

          <h1>
            Buyer
          </h1>

          <p className="buyer-subtitle">
            Market observation and buyer
            workflow boundary.
          </p>
        </div>

        <div className="buyer-status">
          <span
            className={`buyer-status-dot ${
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

      <section className="buyer-panel buyer-selection">
        <div className="buyer-section-heading">
          <div>
            <span className="buyer-label">
              BUYER CONTEXT
            </span>

            <h2>
              Select market context
            </h2>
          </div>

          <span className="buyer-live-badge">
            BACKEND DATA
          </span>
        </div>

        <div className="buyer-controls">
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
                  applySelection();
                }
              }}
              placeholder="BTCUSDT"
              spellCheck={false}
            />
          </label>

          <label>
            <span>Market</span>

            <select
              value={market}
              onChange={(event) =>
                setMarket(
                  event.target.value,
                )
              }
            >
              <option value="SPOT">
                SPOT
              </option>

              <option value="FUTURES">
                FUTURES
              </option>

              <option value="OPTIONS">
                OPTIONS
              </option>

              <option value="EQUITY">
                EQUITY
              </option>
            </select>
          </label>

          <label>
            <span>Instrument</span>

            <input
              value={instrument}
              onChange={(event) =>
                setInstrument(
                  event.target.value,
                )
              }
              placeholder="Optional"
            />
          </label>

          <label>
            <span>Contract</span>

            <input
              value={contract}
              onChange={(event) =>
                setContract(
                  event.target.value,
                )
              }
              placeholder="Optional"
            />
          </label>

          <label>
            <span>Strategy</span>

            <input
              value={strategy}
              onChange={(event) =>
                setStrategy(
                  event.target.value,
                )
              }
              placeholder="Optional"
            />
          </label>

          <label>
            <span>Timeframe</span>

            <select
              value={timeframe}
              onChange={(event) =>
                handleTimeframeChange(
                  event.target
                    .value as BuyerTimeframe,
                )
              }
            >
              <option value="1m">
                1m
              </option>

              <option value="3m">
                3m
              </option>

              <option value="5m">
                5m
              </option>

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

          <label>
            <span>Mode</span>

            <select
              value={mode}
              onChange={(event) =>
                setMode(
                  event.target
                    .value as BuyerMode,
                )
              }
            >
              <option value="ANALYSIS">
                ANALYSIS
              </option>

              <option value="SIMULATION">
                SIMULATION
              </option>

              <option value="AUTHORIZED_EXECUTION">
                AUTHORIZED EXECUTION
              </option>
            </select>
          </label>

          <button
            type="button"
            className="buyer-primary-button"
            onClick={applySelection}
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
          className="buyer-error"
          role="alert"
        >
          <strong>
            Market data error
          </strong>

          <span>{error}</span>
        </div>
      )}

      <section className="buyer-market-grid">
        <article className="buyer-panel buyer-metric">
          <span className="buyer-label">
            ACTIVE SYMBOL
          </span>

          <strong>
            {activeSymbol || "--"}
          </strong>

          <small>
            {market}
          </small>
        </article>

        <article className="buyer-panel buyer-metric">
          <span className="buyer-label">
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
                  ? "buyer-positive"
                  : "buyer-negative"
                : ""
            }
          >
            {priceChange !== null
              ? `${priceChange >= 0 ? "+" : ""}${formatNumber(priceChange)} (${priceChangePercent !== null ? `${priceChangePercent >= 0 ? "+" : ""}${priceChangePercent.toFixed(2)}%` : "--"})`
              : "--"}
          </small>
        </article>

        <article className="buyer-panel buyer-metric">
          <span className="buyer-label">
            HIGH / LOW
          </span>

          <strong>
            {formatNumber(
              sessionHigh,
            )}
          </strong>

          <small>
            Low {formatNumber(sessionLow)}
          </small>
        </article>

        <article className="buyer-panel buyer-metric">
          <span className="buyer-label">
            VOLUME
          </span>

          <strong>
            {formatNumber(
              totalVolume,
            )}
          </strong>

          <small>
            {candles.length} candles
          </small>
        </article>
      </section>

      <section className="buyer-panel buyer-chart-panel">
        <div className="buyer-chart-header">
          <div>
            <span className="buyer-label">
              LIVE MARKET
            </span>

            <h2>
              {activeSymbol} · {timeframe}
            </h2>
          </div>

          <div className="buyer-chart-meta">
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

        <BuyerLiveChart
          candles={candles}
        />

        {latest && (
          <div className="buyer-chart-footer">
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

      <section className="buyer-grid">
        <article className="buyer-panel buyer-info-panel">
          <div className="buyer-section-heading">
            <div>
              <span className="buyer-label">
                BUYER INTELLIGENCE
              </span>

              <h2>
                Intelligence context
              </h2>
            </div>
          </div>

          <div className="buyer-unavailable">
            <strong>
              Backend intelligence boundary
            </strong>

            <span>
              No BUY, SELL or opportunity
              conclusion is generated by the
              frontend.
            </span>
          </div>
        </article>

        <article className="buyer-panel buyer-info-panel">
          <div className="buyer-section-heading">
            <div>
              <span className="buyer-label">
                OPPORTUNITY
              </span>

              <h2>
                Opportunity context
              </h2>
            </div>
          </div>

          <div className="buyer-unavailable">
            <strong>
              Not available
            </strong>

            <span>
              The dedicated Buyer HTTP
              intelligence boundary is not
              assumed until verified.
            </span>
          </div>
        </article>

        <article className="buyer-panel buyer-info-panel">
          <div className="buyer-section-heading">
            <div>
              <span className="buyer-label">
                DECISION
              </span>

              <h2>
                Decision context
              </h2>
            </div>
          </div>

          <div className="buyer-unavailable">
            <strong>
              Backend controlled
            </strong>

            <span>
              The frontend does not create or
              modify a trading decision.
            </span>
          </div>
        </article>

        <article className="buyer-panel buyer-info-panel">
          <div className="buyer-section-heading">
            <div>
              <span className="buyer-label">
                RISK / CAS
              </span>

              <h2>
                Safety boundary
              </h2>
            </div>
          </div>

          <div className="buyer-unavailable">
            <strong>
              Backend controlled
            </strong>

            <span>
              Risk and authorization remain
              authoritative on the backend.
            </span>
          </div>
        </article>
      </section>

      <section className="buyer-panel buyer-execution-note">
        <div>
          <strong>
            Execution boundary
          </strong>

          <p>
            Current frontend wiring is limited
            to the verified live market-data
            boundary. Selecting an execution
            mode does not submit an order or
            bypass backend authorization.
          </p>
        </div>

        <div className="buyer-authorization-chain">
          <span>BUYER</span>
          <span>→</span>
          <span>BACKEND</span>
          <span>→</span>
          <span>RISK</span>
          <span>→</span>
          <span>CAS</span>
          <span>→</span>
          <span>EXECUTION</span>
        </div>
      </section>
    </main>
  );
}