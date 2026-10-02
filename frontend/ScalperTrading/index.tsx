import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  createChart,
  ColorType,
  CandlestickSeries,
  HistogramSeries,
  type CandlestickData,
  type HistogramData,
  type Time,
} from "lightweight-charts";

import {
  getScalperLiveCandles,
  type LiveCandle,
  type ScalperMarket,
  type ScalperOptionSide,
} from "../src/api/scalperTrading";

import "./scalper_trading.css";

type ScalperTimeframe =
  | "1m"
  | "3m"
  | "5m"
  | "15m"
  | "30m"
  | "1h";

interface NormalisedCandle {
  time: Time;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

function toSeconds(
  value: number | string,
): number | null {
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
  candles: LiveCandle[],
): NormalisedCandle[] {
  const result: NormalisedCandle[] = [];

  for (const candle of candles) {
    const seconds = toSeconds(candle.timestamp);

    if (seconds === null) {
      continue;
    }

    if (
      !Number.isFinite(candle.open) ||
      !Number.isFinite(candle.high) ||
      !Number.isFinite(candle.low) ||
      !Number.isFinite(candle.close)
    ) {
      continue;
    }

    const volume =
      candle.volume !== null &&
      candle.volume !== undefined &&
      Number.isFinite(Number(candle.volume))
        ? Number(candle.volume)
        : 0;

    result.push({
      time: seconds as Time,
      open: Number(candle.open),
      high: Number(candle.high),
      low: Number(candle.low),
      close: Number(candle.close),
      volume,
    });
  }

  result.sort((a, b) => {
    return Number(a.time) - Number(b.time);
  });

  const unique = new Map<
    number,
    NormalisedCandle
  >();

  for (const candle of result) {
    unique.set(Number(candle.time), candle);
  }

  return Array.from(unique.values());
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
  value: number | string,
): string {
  const seconds = toSeconds(value);

  if (seconds === null) {
    return "--";
  }

  return new Date(
    seconds * 1000,
  ).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

interface ScalperChartProps {
  candles: NormalisedCandle[];
}

function ScalperChart({
  candles,
}: ScalperChartProps) {
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
            color: "rgba(148,163,184,0.08)",
          },
          horzLines: {
            color: "rgba(148,163,184,0.08)",
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

    chart.priceScale("volume").applyOptions({
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

    candleSeries.setData(candleData);
    volumeSeries.setData(volumeData);

    if (candles.length > 0) {
      chart.timeScale().fitContent();
    }

    const resizeObserver =
      new ResizeObserver(() => {
        if (!containerRef.current) {
          return;
        }

        chart.applyOptions({
          width:
            containerRef.current.clientWidth,
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
      <div className="scalper-chart-empty">
        <span>
          No live candle data available.
        </span>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="scalper-chart-container"
    />
  );
}

export default function ScalperTrading() {
  const [market, setMarket] =
    useState<ScalperMarket>("SPOT");

  const [optionSide, setOptionSide] =
    useState<ScalperOptionSide>("CE");

  const [symbol, setSymbol] =
    useState("BTCUSDT");

  const [activeSymbol, setActiveSymbol] =
    useState("BTCUSDT");

  const [timeframe, setTimeframe] =
    useState<ScalperTimeframe>("1m");

  const [expiry, setExpiry] =
    useState("");

  const [strike, setStrike] =
    useState("");

  const [instrument, setInstrument] =
    useState("");

  const [candles, setCandles] =
    useState<NormalisedCandle[]>([]);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const [lastUpdated, setLastUpdated] =
    useState<number | null>(null);

  const loadChart = useCallback(
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
          await getScalperLiveCandles(
            cleanSymbol,
            requestedTimeframe,
          );

        const rawCandles =
          response.candles ??
          response.data ??
          response.series ??
          [];

        const normalised =
          normaliseCandles(rawCandles);

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
    void loadChart();
  }, [loadChart]);

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
      ? (priceChange! / previous.close) *
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
    setActiveSymbol(cleanSymbol);
    void loadChart(
      cleanSymbol,
      timeframe,
    );
  };

  const handleTimeframeChange = (
    value: ScalperTimeframe,
  ) => {
    setTimeframe(value);
    void loadChart(
      activeSymbol,
      value,
    );
  };

  return (
    <main className="scalper-page">
      <header className="scalper-header">
        <div>
          <p className="scalper-eyebrow">
            ROBOMLM PLUS
          </p>

          <h1>
            Scalper Trading
          </h1>

          <p className="scalper-subtitle">
            Live market observation boundary
            for short-timeframe analysis.
          </p>
        </div>

        <div className="scalper-provider-status">
          <span
            className={`scalper-status-dot ${
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

      <section className="scalper-panel scalper-selection">
        <div className="scalper-section-heading">
          <div>
            <span className="scalper-label">
              MARKET SELECTION
            </span>

            <h2>
              Configure observation
            </h2>
          </div>

          <span className="scalper-live-badge">
            BACKEND DATA
          </span>
        </div>

        <div className="scalper-controls">
          <label>
            <span>Market</span>

            <select
              value={market}
              onChange={(event) =>
                setMarket(
                  event.target
                    .value as ScalperMarket,
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
            </select>
          </label>

          {market === "OPTIONS" && (
            <>
              <label>
                <span>Option Side</span>

                <select
                  value={optionSide}
                  onChange={(event) =>
                    setOptionSide(
                      event.target
                        .value as ScalperOptionSide,
                    )
                  }
                >
                  <option value="CE">
                    CE
                  </option>

                  <option value="PE">
                    PE
                  </option>
                </select>
              </label>

              <label>
                <span>Expiry</span>

                <input
                  value={expiry}
                  onChange={(event) =>
                    setExpiry(
                      event.target.value,
                    )
                  }
                  placeholder="YYYY-MM-DD"
                />
              </label>

              <label>
                <span>Strike</span>

                <input
                  value={strike}
                  onChange={(event) =>
                    setStrike(
                      event.target.value,
                    )
                  }
                  placeholder="Strike"
                />
              </label>
            </>
          )}

          <label>
            <span>Symbol</span>

            <input
              value={symbol}
              onChange={(event) =>
                setSymbol(
                  event.target.value,
                )
              }
              placeholder="BTCUSDT"
              spellCheck={false}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  applyMarket();
                }
              }}
            />
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
            <span>Timeframe</span>

            <select
              value={timeframe}
              onChange={(event) =>
                handleTimeframeChange(
                  event.target
                    .value as ScalperTimeframe,
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
            </select>
          </label>

          <button
            type="button"
            className="scalper-primary-button"
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
          className="scalper-error"
          role="alert"
        >
          <strong>
            Market data error
          </strong>

          <span>{error}</span>
        </div>
      )}

      <section className="scalper-market-grid">
        <article className="scalper-panel scalper-market-card">
          <span className="scalper-label">
            ACTIVE SYMBOL
          </span>

          <strong>
            {activeSymbol || "--"}
          </strong>

          <small>
            {market}
            {market === "OPTIONS"
              ? ` · ${optionSide}`
              : ""}
          </small>
        </article>

        <article className="scalper-panel scalper-market-card">
          <span className="scalper-label">
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
                  ? "scalper-positive"
                  : "scalper-negative"
                : ""
            }
          >
            {priceChange !== null
              ? `${priceChange >= 0 ? "+" : ""}${formatNumber(priceChange)} (${priceChangePercent !== null ? `${priceChangePercent >= 0 ? "+" : ""}${priceChangePercent.toFixed(2)}%` : "--"})`
              : "--"}
          </small>
        </article>

        <article className="scalper-panel scalper-market-card">
          <span className="scalper-label">
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

        <article className="scalper-panel scalper-market-card">
          <span className="scalper-label">
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

      <section className="scalper-panel scalper-chart-panel">
        <div className="scalper-chart-header">
          <div>
            <span className="scalper-label">
              LIVE MARKET CHART
            </span>

            <h2>
              {activeSymbol} · {timeframe}
            </h2>
          </div>

          <div className="scalper-chart-meta">
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

        <ScalperChart
          candles={candles}
        />

        {latest && (
          <div className="scalper-chart-footer">
            <span>
              Last candle{" "}
              {formatTime(
                latest.time as number,
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

      <section className="scalper-grid">
        <article className="scalper-panel">
          <div className="scalper-section-heading">
            <div>
              <span className="scalper-label">
                INTELLIGENCE
              </span>

              <h2>
                Backend intelligence
              </h2>
            </div>
          </div>

          <div className="scalper-unavailable">
            <strong>
              Not available through the
              current verified HTTP boundary.
            </strong>

            <span>
              No synthetic signal is generated
              by the frontend. Backend
              intelligence remains authoritative.
            </span>
          </div>
        </article>

        <article className="scalper-panel">
          <div className="scalper-section-heading">
            <div>
              <span className="scalper-label">
                DECISION
              </span>

              <h2>
                Decision context
              </h2>
            </div>
          </div>

          <div className="scalper-unavailable">
            <strong>
              Not available
            </strong>

            <span>
              The frontend does not manufacture
              BUY, SELL or HOLD decisions.
            </span>
          </div>
        </article>

        <article className="scalper-panel">
          <div className="scalper-section-heading">
            <div>
              <span className="scalper-label">
                RISK
              </span>

              <h2>
                Risk context
              </h2>
            </div>
          </div>

          <div className="scalper-unavailable">
            <strong>
              Not available
            </strong>

            <span>
              Risk ownership remains on the
              backend intelligence and risk
              boundaries.
            </span>
          </div>
        </article>

        <article className="scalper-panel">
          <div className="scalper-section-heading">
            <div>
              <span className="scalper-label">
                CAS
              </span>

              <h2>
                Authorization
              </h2>
            </div>
          </div>

          <div className="scalper-unavailable">
            <strong>
              Backend controlled
            </strong>

            <span>
              The frontend cannot bypass the
              authorization and execution
              boundaries.
            </span>
          </div>
        </article>
      </section>

      <section className="scalper-panel scalper-note">
        <strong>
          Execution boundary
        </strong>

        <p>
          This page observes authoritative
          market data. It does not create
          orders, fabricate signals, or bypass
          backend risk and authorization
          controls.
        </p>
      </section>
    </main>
  );
}