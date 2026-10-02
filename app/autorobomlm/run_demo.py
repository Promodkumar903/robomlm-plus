"""
ROBOMLM_PLUS - AutoROBOMLM DEMO Runner

Purpose:
    End-to-end demo wiring:
        live_signal   -> signal_provider
        Bybit tickers -> price_provider
        PaperBroker   -> execution
        AutoRobomlmLoop

Usage:
    python -m app.autorobomlm.run_demo
    or
    python app/autorobomlm/run_demo.py
"""

from __future__ import annotations

from typing import Optional, Sequence

from app.autorobomlm.config import (
    AutoRobomlmConfig,
    ExecutionMode,
    GradeBand,
    WatchlistSource,
)
from app.autorobomlm.paper_broker import PaperBroker
from app.autorobomlm.auto_loop import AutoRobomlmLoop
from app.autorobomlm.signal_adapter import (
    make_live_signal_provider,
    make_price_provider,
)


DEFAULT_SYMBOLS = ("BTC/USDT",)


def build_demo_loop(
    symbols: Sequence[str] = DEFAULT_SYMBOLS,
    *,
    capital: float = 100000.0,
    min_grade: GradeBand = GradeBand.B,
    loop_interval_sec: int = 60,
    max_open_positions: int = 3,
) -> AutoRobomlmLoop:
    """
    Build a DEMO-mode AutoRobomlmLoop fully wired to
    live signal + live prices.
    """
    config = AutoRobomlmConfig(
        min_grade=min_grade,
        execution_mode=ExecutionMode.DEMO,
        watchlist_source=WatchlistSource.MANUAL,
        manual_watchlist=tuple(symbols),
        max_open_positions=max_open_positions,
        risk_per_trade_pct=1.0,
        max_position_pct=10.0,
        sl_atr_multiplier=1.5,
        tp_atr_multiplier=3.0,
        loop_interval_sec=loop_interval_sec,
    )
    config.validate()

    price_provider = make_price_provider()
    signal_provider = make_live_signal_provider()

    broker = PaperBroker(
        price_provider=price_provider,
        slippage_pct=0.0,
    )

    loop = AutoRobomlmLoop(
        config=config,
        signal_provider=signal_provider,
        broker=broker,
        watchlist_provider=lambda: list(symbols),
        capital_provider=lambda: float(capital),
    )

    return loop


def run_one_tick(
    symbols: Sequence[str] = DEFAULT_SYMBOLS,
    *,
    capital: float = 100000.0,
    min_grade: GradeBand = GradeBand.B,
) -> dict:
    """Run exactly one tick and return an audit dict."""
    loop = build_demo_loop(
        symbols=symbols, capital=capital, min_grade=min_grade
    )
    summary = loop.tick()
    return {
        "summary": summary.to_dict(),
        "active_trades": loop.active_trades(),
    }


def run_continuous(
    symbols: Sequence[str] = DEFAULT_SYMBOLS,
    *,
    capital: float = 100000.0,
    min_grade: GradeBand = GradeBand.B,
    loop_interval_sec: int = 60,
) -> None:
    """Run the loop in DEMO mode until Ctrl+C."""
    loop = build_demo_loop(
        symbols=symbols,
        capital=capital,
        min_grade=min_grade,
        loop_interval_sec=loop_interval_sec,
    )

    print("=" * 60)
    print("AutoROBOMLM DEMO loop starting")
    print(f"  symbols: {list(symbols)}")
    print(f"  capital: {capital}")
    print(f"  min_grade: {min_grade.value}")
    print(f"  interval: {loop_interval_sec}s")
    print("  press Ctrl+C to stop")
    print("=" * 60)

    loop.start()

    try:
        import time
        while True:
            time.sleep(5)
            status = loop.status()
            print(
                f"[state={status['state']}] "
                f"ticks={status['tick_count']} "
                f"open={status['open_positions']}"
            )
    except KeyboardInterrupt:
        print()
        print("Stopping...")
        loop.stop()
        print("Stopped.")


if __name__ == "__main__":
    import sys

    mode = "tick"
    if len(sys.argv) > 1:
        mode = sys.argv[1].strip().lower()

    if mode == "continuous":
        run_continuous()
    else:
        result = run_one_tick()
        print("=" * 60)
        print("One-tick demo run")
        print("=" * 60)
        print("summary:")
        for key, value in result["summary"].items():
            print(f"  {key}: {value}")
        print("active trades:")
        for trade in result["active_trades"]:
            print(f"  {trade}")
