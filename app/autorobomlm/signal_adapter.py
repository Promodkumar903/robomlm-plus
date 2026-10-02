"""
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
ADAPTER_VERSION = "2.0-unified"


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

# ---------------------------------------------------------------------
# unified_signal -> AutoROBOMLM dict
# ---------------------------------------------------------------------

def _unified_to_autoro_dict(sig) -> dict:
    """
    Convert a UnifiedSignal into the dict shape AutoRobomlmLoop expects.

    Fields provided:
        direction     : LONG | SHORT | NEUTRAL
        action        : BUY  | SELL  | HOLD
        decision_score: 0-100 (strength)
        confidence    : 0-100
        grade         : A+ | A | B+ | B | HOLD
        strength      : 0-100
        entry, sl, tp, rr, expected_move_pct, size_pct
        risk_level, warnings
        source        : REAL_UNIFIED_SIGNAL
    """
    direction = "NEUTRAL"
    if sig.direction == "BULLISH":
        direction = "LONG"
    elif sig.direction == "BEARISH":
        direction = "SHORT"

    return {
        "symbol": sig.symbol,
        "timestamp": sig.timestamp,
        "direction": direction,
        "action": sig.action,
        "decision_score": float(sig.strength),
        "confidence": float(sig.confidence),
        "strength": float(sig.strength),
        "grade": sig.trade_quality,
        "entry": sig.entry_price,
        "entry_price": sig.entry_price,
        "stop_loss": sig.stop_loss,
        "take_profit": sig.take_profit,
        "risk_reward": sig.risk_reward,
        "expected_move_pct": sig.expected_move_pct,
        "suggested_size_pct": sig.suggested_size_pct,
        "risk_level": sig.risk_level,
        "warnings": list(sig.warnings),
        "source": "REAL_UNIFIED_SIGNAL",
        "components": {
            "flow": float(sig.flow_score),
            "derivative": float(sig.derivative_score),
            "volume": float(sig.volume_score),
            "obstacle": float(sig.obstacle_score),
            "context": float(sig.context_score),
            "regime": float(sig.regime_score),
        },
        # keep audit for logs
        "audit": sig.audit,
    }


def _make_unified_provider():
    """
    Return a callable that uses unified_signal for a symbol.
    Returns None on failure so caller can fall back.
    """
    try:
        from app.intelligence.real.unified_signal import (
            get_unified_signal_engine,
        )
    except Exception:
        return None

    engine = get_unified_signal_engine()

    def provider(symbol: str):
        try:
            sig = engine.compute(symbol)
            return _unified_to_autoro_dict(sig)
        except Exception:
            return None

    return provider


def make_live_signal_provider() -> Callable[[str], Optional[dict]]:
    """
    Return a callable suitable for AutoRobomlmLoop.signal_provider.

    Priority:
        1. unified_signal  (REAL — all 8 engines)
        2. live_signal     (legacy fallback)

    Raises RuntimeError only if BOTH are unavailable.
    """
    # --- Try unified first ---
    unified = _make_unified_provider()

    # --- Legacy fallback getter ---
    getter = _import_live_signal_getter()

    if unified is None and getter is None:
        raise RuntimeError(
            "Neither unified_signal nor live_signal is available. "
            "Check app.intelligence.real.unified_signal and "
            "app.intelligence.live_signal."
        )

    def provider(symbol: str) -> Optional[dict]:
        # 1) unified
        if unified is not None:
            try:
                result = unified(symbol)
                if result is not None:
                    # Optionally normalize for downstream
                    return normalize_signal(result)
            except Exception:
                pass
        # 2) legacy
        if getter is not None:
            try:
                raw = getter(symbol)
                return normalize_signal(raw)
            except Exception:
                return None
        return None

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
