"""AutoROBOMLM installer part 7 - signal_adapter + run_demo"""
from pathlib import Path

ROOT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\autorobomlm")
ROOT.mkdir(parents=True, exist_ok=True)

FILES = {}

FILES["signal_adapter.py"] = '''"""
ROBOMLM_PLUS - AutoROBOMLM Signal Adapter

Bridges:
    live_signal.get_signal(symbol)   -> signal_provider
    LiveMarketDataService / Bybit    -> price_provider

Design:
    - Pure adapter; contains no trading logic.
    - Normalizes live_signal output so AutoROBOMLM can consume it.
    - Falls back to Bybit tickers when LiveMarketDataService
      is not available.
"""

from __future__ import annotations
from typing import Any, Callable, Optional

import json
import urllib.request


ADAPTER_NAME = "AutoROBOMLM_SignalAdapter"
ADAPTER_VERSION = "1.0"


# ---------------------------------------------------------------------
# live_signal import (defensive)
# ---------------------------------------------------------------------

def _import_live_signal_getter() -> Optional[Callable]:
    """
    Try common import paths for live_signal.get_signal.

    Returns the function on success, or None.
    """
    candidates = (
        "app.intelligence.live_signal",
        "app.intelligence.signal.live_signal",
        "intelligence.live_signal",
    )
    for path in candidates:
        try:
            module = __import__(path, fromlist=["get_signal"])
            getter = getattr(module, "get_signal", None)
            if callable(getter):
                return getter
        except Exception:
            continue
    return None


# ---------------------------------------------------------------------
# live_signal output normalization
# ---------------------------------------------------------------------

def normalize_signal(raw: Optional[dict]) -> Optional[dict]:
    """
    Flatten live_signal output so AutoROBOMLM's loop finds the score
    at a predictable top-level key.

    - Copies d13.decision_score to top-level decision_score.
    - Falls back to confidence * 100 when score is missing.
    - Never fabricates a score.
    """
    if not isinstance(raw, dict):
        return None

    out = dict(raw)

    if out.get("decision_score") is None:
        d13 = out.get("d13")
        if isinstance(d13, dict):
            d13_score = d13.get("decision_score")
            if d13_score is not None:
                out["decision_score"] = d13_score

    if out.get("decision_score") is None:
        try:
            conf = out.get("confidence")
            if conf is not None:
                out["decision_score"] = float(conf) * 100.0
        except (TypeError, ValueError):
            pass

    return out


# ---------------------------------------------------------------------
# Providers
# ---------------------------------------------------------------------

def make_live_signal_provider() -> Callable[[str], Optional[dict]]:
    """
    Return a callable suitable for AutoRobomlmLoop.signal_provider.

    Raises RuntimeError immediately if live_signal cannot be imported.
    """
    getter = _import_live_signal_getter()

    if getter is None:
        raise RuntimeError(
            "Could not import live_signal.get_signal. "
            "Check that app.intelligence.live_signal exists."
        )

    def provider(symbol: str) -> Optional[dict]:
        try:
            raw = getter(symbol)
        except Exception:
            return None
        return normalize_signal(raw)

    return provider


def _fetch_last_price_bybit(symbol: str) -> Optional[float]:
    """
    Fetch last price from Bybit spot tickers.

    Used as fallback when LiveMarketDataService is not available.
    """
    try:
        sym = symbol.replace("/", "").upper()
        url = (
            "https://api.bybit.com/v5/market/tickers"
            f"?category=spot&symbol={sym}"
        )
        with urllib.request.urlopen(url, timeout=5) as r:
            data = json.loads(r.read())
        items = ((data.get("result") or {}).get("list")) or []
        if not items:
            return None
        last = items[0].get("lastPrice")
        if last is None:
            return None
        price = float(last)
        if price <= 0.0:
            return None
        return price
    except Exception:
        return None


def make_price_provider() -> Callable[[str], Optional[float]]:
    """
    Return a callable suitable for PaperBroker.price_provider.

    Uses Bybit spot tickers. If you later wire LiveMarketDataService,
    swap this out with a service-backed provider.
    """
    return _fetch_last_price_bybit


# ---------------------------------------------------------------------
# Structured adapter (optional)
# ---------------------------------------------------------------------

class SignalAdapter:
    """
    Convenience wrapper bundling all providers.

    Not required by AutoRobomlmLoop; useful for tests and scripts.
    """

    def __init__(
        self,
        *,
        signal_provider: Optional[Callable[[str], Optional[dict]]] = None,
        price_provider: Optional[Callable[[str], Optional[float]]] = None,
    ) -> None:
        self.signal_provider = (
            signal_provider
            if signal_provider is not None
            else make_live_signal_provider()
        )
        self.price_provider = (
            price_provider
            if price_provider is not None
            else make_price_provider()
        )

    def signal(self, symbol: str) -> Optional[dict]:
        try:
            return self.signal_provider(symbol)
        except Exception:
            return None

    def price(self, symbol: str) -> Optional[float]:
        try:
            return self.price_provider(symbol)
        except Exception:
            return None

    def __repr__(self) -> str:
        return (
            f"SignalAdapter(engine={ADAPTER_NAME!r}, "
            f"version={ADAPTER_VERSION!r})"
        )


__all__ = [
    "ADAPTER_NAME", "ADAPTER_VERSION",
    "normalize_signal",
    "make_live_signal_provider",
    "make_price_provider",
    "SignalAdapter",
]
'''

FILES["run_demo.py"] = '''"""
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
'''

for filename, content in FILES.items():
    path = ROOT / filename
    path.write_text(content, encoding="utf-8")
    print(f"WROTE: {path}")

print()
print(f"DONE. Files in {ROOT}:")
for p in sorted(ROOT.glob("*.py")):
    print(f"  {p.name} ({p.stat().st_size} bytes)")