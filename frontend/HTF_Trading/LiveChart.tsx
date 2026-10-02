import React, { useEffect, useMemo, useRef } from "react";
import {
  CandlestickSeries,
  ColorType,
  createChart,
  HistogramSeries,
  type CandlestickData,
  type IChartApi,
  type ISeriesApi,
  type Time,
} from "lightweight-charts";

export interface HTFCandle {
  time: number | string;
  open: number | string;
  high: number | string;
  low: number | string;
  close: number | string;
  volume?: number | string | null;
}

interface LiveChartProps {
  candles: HTFCandle[];
  height?: number;
}

function toSeconds(value: number | string): number | null {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value > 10_000_000_000
      ? Math.floor(value / 1000)
      : Math.floor(value);
  }

  if (typeof value === "string") {
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

    if (Number.isFinite(parsed)) {
      return Math.floor(parsed / 1000);
    }
  }

  return null;
}

function toNumber(value: number | string | null | undefined): number | null {
  if (typeof value === "number") {
    return Number.isFinite(value) ? value : null;
  }

  if (typeof value === "string") {
    const parsed = Number(value.replace(/,/g, "").trim());
    return Number.isFinite(parsed) ? parsed : null;
  }

  return null;
}

function normaliseCandles(candles: HTFCandle[]): {
  candles: CandlestickData<Time>[];
  volumes: Array<{
    time: Time;
    value: number;
  }>;
} {
  const mapped = candles
    .map((candle) => {
      const time = toSeconds(candle.time);
      const open = toNumber(candle.open);
      const high = toNumber(candle.high);
      const low = toNumber(candle.low);
      const close = toNumber(candle.close);
      const volume = toNumber(candle.volume);

      if (
        time === null ||
        open === null ||
        high === null ||
        low === null ||
        close === null
      ) {
        return null;
      }

      return {
        time: time as Time,
        candle: {
          time: time as Time,
          open,
          high,
          low,
          close,
        },
        volume: volume ?? 0,
      };
    })
    .filter(
      (
        item
      ): item is {
        time: Time;
        candle: CandlestickData<Time>;
        volume: number;
      } => item !== null
    )
    .sort((a, b) => Number(a.time) - Number(b.time));

  const uniqueCandles: CandlestickData<Time>[] = [];
  const uniqueVolumes: Array<{ time: Time; value: number }> = [];
  const seen = new Set<number>();

  for (const item of mapped) {
    const numericTime = Number(item.time);

    if (seen.has(numericTime)) {
      continue;
    }

    seen.add(numericTime);
    uniqueCandles.push(item.candle);
    uniqueVolumes.push({
      time: item.time,
      value: item.volume,
    });
  }

  return {
    candles: uniqueCandles,
    volumes: uniqueVolumes,
  };
}

export default function LiveChart({
  candles,
  height = 500,
}: LiveChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef =
    useRef<ISeriesApi<"Candlestick"> | null>(null);
  const volumeSeriesRef =
    useRef<ISeriesApi<"Histogram"> | null>(null);

  const normalised = useMemo(
    () => normaliseCandles(candles),
    [candles]
  );

  useEffect(() => {
    const container = containerRef.current;

    if (!container) {
      return;
    }

    const chart = createChart(container, {
      width: container.clientWidth || 900,
      height,
      layout: {
        background: {
          type: ColorType.Solid,
          color: "transparent",
        },
        textColor: "#64748b",
      },
      grid: {
        vertLines: {
          color: "rgba(148, 163, 184, 0.06)",
        },
        horzLines: {
          color: "rgba(148, 163, 184, 0.06)",
        },
      },
      rightPriceScale: {
        borderColor: "rgba(148, 163, 184, 0.12)",
      },
      timeScale: {
        borderColor: "rgba(148, 163, 184, 0.12)",
        timeVisible: true,
        secondsVisible: false,
        rightOffset: 3,
        barSpacing: 8,
      },
      crosshair: {
        vertLine: {
          color: "rgba(148, 163, 184, 0.25)",
        },
        horzLine: {
          color: "rgba(148, 163, 184, 0.25)",
        },
      },
    });

    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: "#10b981",
      downColor: "#ef4444",
      borderUpColor: "#10b981",
      borderDownColor: "#ef4444",
      wickUpColor: "#10b981",
      wickDownColor: "#ef4444",
    });

    const volumeSeries = chart.addSeries(HistogramSeries, {
      priceFormat: {
        type: "volume",
      },
      priceScaleId: "volume",
      color: "rgba(59, 130, 246, 0.35)",
      base: 0,
    });

    volumeSeries.priceScale().applyOptions({
      scaleMargins: {
        top: 0.82,
        bottom: 0,
      },
    });

    chartRef.current = chart;
    candleSeriesRef.current = candleSeries;
    volumeSeriesRef.current = volumeSeries;

    const resizeObserver = new ResizeObserver(() => {
      if (!containerRef.current || !chartRef.current) {
        return;
      }

      chartRef.current.applyOptions({
        width: containerRef.current.clientWidth,
      });
    });

    resizeObserver.observe(container);

    return () => {
      resizeObserver.disconnect();

      chart.remove();

      chartRef.current = null;
      candleSeriesRef.current = null;
      volumeSeriesRef.current = null;
    };
  }, [height]);

  useEffect(() => {
    const candleSeries = candleSeriesRef.current;
    const volumeSeries = volumeSeriesRef.current;
    const chart = chartRef.current;

    if (!candleSeries || !volumeSeries || !chart) {
      return;
    }

    candleSeries.setData(normalised.candles);
    volumeSeries.setData(
      normalised.volumes.map((item) => ({
        time: item.time,
        value: item.value,
      }))
    );

    if (normalised.candles.length > 0) {
      chart.timeScale().fitContent();
    }
  }, [normalised]);

  return (
    <div
      className="htf-chart-wrapper"
      style={{
        position: "relative",
        width: "100%",
        minHeight: height,
      }}
    >
      <div
        ref={containerRef}
        style={{
          width: "100%",
          minHeight: height,
        }}
      />

      {normalised.candles.length === 0 && (
        <div
          className="htf-chart-empty"
          style={{
            position: "absolute",
            inset: 0,
            minHeight: height,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            pointerEvents: "none",
          }}
        >
          No market candles available
        </div>
      )}
    </div>
  );
}