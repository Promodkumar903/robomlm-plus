// frontend/src/components/Chart.tsx
// ROBOMLM+ Terminal — Price Chart
// lightweight-charts v5 compatible
//
// ⚠️ COMPLETE FILE — replace entire file. Do NOT append.

import { useEffect, useMemo, useRef, useState } from "react";
import {
  createChart,
  CandlestickSeries,
  HistogramSeries,
  ColorType,
  CrosshairMode,
  type IChartApi,
  type ISeriesApi,
  type UTCTimestamp,
} from "lightweight-charts";

import type { ChartCandle } from "../types/terminal";

export interface ChartProps {
  symbol: string;
  timeframe?: string;
  height?: number;
  className?: string;
}

const BINANCE_BASE = "https://api.binance.com";
const DEFAULT_LIMIT = 200;

const TIMEFRAME_MAP: Record<string, string> = {
  "1m": "1m", "3m": "3m", "5m": "5m", "15m": "15m", "30m": "30m",
  "1h": "1h", "2h": "2h", "4h": "4h", "1d": "1d", "1w": "1w", "1M": "1M",
};

function toBinanceSymbol(symbol: string): string {
  return symbol.replace(/[/-]/g, "").toUpperCase();
}

function isCryptoSymbol(symbol: string): boolean {
  const s = symbol.toUpperCase();
  return (
    s.includes("/USDT") || s.includes("/USDC") || s.includes("/BUSD") ||
    s.endsWith("USDT") || s.endsWith("USDC") || s.endsWith("BUSD")
  );
}

async function fetchBinanceKlines(
  symbol: string,
  interval: string,
  limit: number,
  signal: AbortSignal,
): Promise<ChartCandle[]> {
  const binanceSymbol = toBinanceSymbol(symbol);
  const url =
    `${BINANCE_BASE}/api/v3/klines` +
    `?symbol=${encodeURIComponent(binanceSymbol)}` +
    `&interval=${encodeURIComponent(interval)}` +
    `&limit=${limit}`;

  const res = await fetch(url, { signal });
  if (!res.ok) {
    throw new Error(`Binance klines failed: ${res.status} ${res.statusText}`);
  }

  const raw = (await res.json()) as unknown;
  if (!Array.isArray(raw)) {
    throw new Error("Binance klines: unexpected response shape");
  }

  const candles: ChartCandle[] = [];
  for (const row of raw) {
    if (!Array.isArray(row) || row.length < 6) continue;
    const openTime = Number(row[0]);
    const open = Number(row[1]);
    const high = Number(row[2]);
    const low = Number(row[3]);
    const close = Number(row[4]);
    const volume = Number(row[5]);
    if (
      !Number.isFinite(openTime) || !Number.isFinite(open) ||
      !Number.isFinite(high) || !Number.isFinite(low) ||
      !Number.isFinite(close) || !Number.isFinite(volume)
    ) continue;
    candles.push({
      time: Math.floor(openTime / 1000),
      open, high, low, close, volume,
    });
  }
  return candles;
}

export function Chart({
  symbol,
  timeframe = "1m",
  height = 420,
  className,
}: ChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<"Histogram"> | null>(null);

  const [candles, setCandles] = useState<ChartCandle[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const resolvedInterval = useMemo(
    () => TIMEFRAME_MAP[timeframe] ?? "1m",
    [timeframe],
  );

  // Create chart once
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const chart = createChart(container, {
      width: container.clientWidth,
      height,
      layout: {
        background: { type: ColorType.Solid, color: "#0a0e14" },
        textColor: "#8899a8",
        fontFamily: "'JetBrains Mono', 'SF Mono', Menlo, monospace",
        fontSize: 11,
      },
      grid: {
        vertLines: { color: "#131820" },
        horzLines: { color: "#131820" },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: { color: "#3b82f6", width: 1, style: 3, labelBackgroundColor: "#1e2633" },
        horzLine: { color: "#3b82f6", width: 1, style: 3, labelBackgroundColor: "#1e2633" },
      },
      rightPriceScale: {
        borderColor: "#1e2633",
        scaleMargins: { top: 0.08, bottom: 0.25 },
      },
      timeScale: {
        borderColor: "#1e2633",
        timeVisible: true,
        secondsVisible: false,
      },
    });

    // v5 API — addSeries(SeriesDefinition, options)
    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: "#22c55e",
      downColor: "#ef4444",
      borderUpColor: "#22c55e",
      borderDownColor: "#ef4444",
      wickUpColor: "#22c55e",
      wickDownColor: "#ef4444",
    });

    const volumeSeries = chart.addSeries(HistogramSeries, {
      priceFormat: { type: "volume" },
      priceScaleId: "",
    });

    volumeSeries.priceScale().applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 },
    });

    chartRef.current = chart;
    candleSeriesRef.current = candleSeries;
    volumeSeriesRef.current = volumeSeries;

    const handleResize = () => {
      if (!containerRef.current) return;
      chart.applyOptions({ width: containerRef.current.clientWidth });
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
      chartRef.current = null;
      candleSeriesRef.current = null;
      volumeSeriesRef.current = null;
    };
  }, [height]);

  // Fetch candles on symbol/timeframe change
  useEffect(() => {
    const candleSeries = candleSeriesRef.current;
    const volumeSeries = volumeSeriesRef.current;
    if (!candleSeries || !volumeSeries) return;

    const controller = new AbortController();
    setLoading(true);
    setError(null);
    setCandles([]);

    candleSeries.setData([]);
    volumeSeries.setData([]);

    if (!isCryptoSymbol(symbol)) {
      setLoading(false);
      setError(
        `Chart data unavailable for ${symbol} — backend candle feed for this market is not configured yet.`,
      );
      return () => controller.abort();
    }

    fetchBinanceKlines(symbol, resolvedInterval, DEFAULT_LIMIT, controller.signal)
      .then((data) => {
        setCandles(data);
        setLoading(false);
      })
      .catch((err: unknown) => {
        if (controller.signal.aborted) return;
        const msg = err instanceof Error ? err.message : "Unknown chart data error";
        setError(msg);
        setLoading(false);
      });

    return () => controller.abort();
  }, [symbol, resolvedInterval]);

  // Push candles
  useEffect(() => {
    const candleSeries = candleSeriesRef.current;
    const volumeSeries = volumeSeriesRef.current;
    const chart = chartRef.current;
    if (!candleSeries || !volumeSeries || !chart) return;

    if (candles.length === 0) {
      candleSeries.setData([]);
      volumeSeries.setData([]);
      return;
    }

    candleSeries.setData(
      candles.map((c) => ({
        time: c.time as UTCTimestamp,
        open: c.open, high: c.high, low: c.low, close: c.close,
      })),
    );

    volumeSeries.setData(
      candles.map((c) => ({
        time: c.time as UTCTimestamp,
        value: c.volume,
        color: c.close >= c.open
          ? "rgba(34, 197, 94, 0.35)"
          : "rgba(239, 68, 68, 0.35)",
      })),
    );

    chart.timeScale().fitContent();
  }, [candles]);

  return (
    <div
      className={className}
      style={{
        position: "relative",
        width: "100%",
        height,
        background: "#0a0e14",
        border: "1px solid #1e2633",
        borderRadius: 10,
        overflow: "hidden",
      }}
    >
      <div ref={containerRef} style={{ width: "100%", height: "100%" }} />

      {loading && (
        <div style={overlayStyle}>
          <span style={overlayTextStyle}>Loading chart…</span>
        </div>
      )}

      {!loading && error && (
        <div style={overlayStyle}>
          <div style={errorBoxStyle}>
            <div style={errorTitleStyle}>CHART DATA UNAVAILABLE</div>
            <div style={errorBodyStyle}>{error}</div>
          </div>
        </div>
      )}

      {!loading && !error && candles.length === 0 && (
        <div style={overlayStyle}>
          <span style={overlayTextStyle}>No candle data</span>
        </div>
      )}
    </div>
  );
}

const overlayStyle: React.CSSProperties = {
  position: "absolute",
  inset: 0,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  background: "rgba(10, 14, 20, 0.85)",
  pointerEvents: "none",
};
const overlayTextStyle: React.CSSProperties = {
  color: "#8899a8", fontSize: 12,
  letterSpacing: "0.05em", textTransform: "uppercase",
};
const errorBoxStyle: React.CSSProperties = {
  maxWidth: 420, padding: "16px 20px",
  border: "1px solid #ef4444", borderRadius: 8,
  background: "rgba(239, 68, 68, 0.06)", textAlign: "center",
};
const errorTitleStyle: React.CSSProperties = {
  color: "#ef4444", fontSize: 11, letterSpacing: "0.08em",
  fontWeight: 600, marginBottom: 8,
};
const errorBodyStyle: React.CSSProperties = {
  color: "#8899a8", fontSize: 12, lineHeight: 1.5,
};

export default Chart;