"""
ROBOMLM_PLUS - Real Discovery Bridge

Converts UnifiedSignal output into the Discovery OpportunityEngine format.

This is the SINGLE source of truth:
    - Terminal uses it (via unified_signal)
    - Discovery uses it (via this bridge)
    - AutoROBOMLM uses it (via unified_signal)

No more hardcoded universe_seed for direction/score.
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from app.intelligence.real.unified_signal import (
    get_unified_signal_engine,
    UnifiedSignal,
)


DEFAULT_WATCHLIST = {
    "CRYPTO": [
        "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT",
        "ADA/USDT", "DOGE/USDT", "MATIC/USDT", "DOT/USDT", "LINK/USDT",
    ],
}

# ============================================================
# 60-second CACHE
# ============================================================
_CACHE: dict = {}
_CACHE_TTL = 60  # seconds




def _direction_to_opportunity(signal: UnifiedSignal) -> str:
    """Map signal direction to opportunity direction."""
    if signal.direction == "BULLISH":
        return "LONG"
    if signal.direction == "BEARISH":
        return "SHORT"
    return "NEUTRAL"


def _grade_from_quality(quality: str) -> str:
    """Map A+/A/B+/B/HOLD to discovery grade."""
    return quality


def signal_to_opportunity(signal: UnifiedSignal) -> dict:
    """
    Convert UnifiedSignal to a Discovery-compatible opportunity dict.
    """
    direction = _direction_to_opportunity(signal)
    if direction == "LONG":
        type_ = "TREND" if signal.confidence >= 70 else "DEVELOPING"
    elif direction == "SHORT":
        type_ = "REVERSAL" if signal.confidence >= 70 else "DEVELOPING"
    else:
        type_ = "WATCHLIST"

    return {
        "instrument_id": signal.symbol.replace("/", ""),
        "symbol": signal.symbol,
        "market_id": "CRYPTO",
        "venue_id": "BINANCE",
        "instrument_type": "CRYPTO",
        "status": "ACTIVE",
        "tradable": True,
        "enabled": True,
        "eligible": signal.action in {"BUY", "SELL"},

        # Core direction/quality
        "direction": direction,
        "opportunity_type": type_,
        "source": "REAL_UNIFIED_SIGNAL",

        # Score (for compatibility with existing frontend)
        "score": signal.strength,
        "confidence": signal.confidence,
        "grade": signal.trade_quality,

        # Components (real from audit)
        "eqe": signal.flow_score,
        "pfs": signal.volume_score,
        "mci": signal.regime_score,
        "mts": signal.derivative_score,
        "lqs": signal.obstacle_score,
        "mcs": signal.levels_score if hasattr(signal, "levels_score") else 50.0,

        # Trade guidance
        "entry_price": signal.entry_price,
        "stop_loss": signal.stop_loss,
        "take_profit": signal.take_profit,
        "risk_reward": signal.risk_reward,
        "expected_move_pct": signal.expected_move_pct,
        "suggested_size_pct": signal.suggested_size_pct,

        # Meta
        "risk_level": signal.risk_level,
        "warnings": list(signal.warnings),
        "timestamp": signal.timestamp,
        "provenance": "REAL_DISCOVERY_BRIDGE_V1",
        "audit": signal.audit,
    }


def _compute_one(symbol: str) -> Optional[dict]:
    """Compute one symbol's opportunity — thread-safe wrapper."""
    try:
        engine = get_unified_signal_engine()
        signal = engine.compute(symbol)
        return signal_to_opportunity(signal)
    except Exception:
        return None


def get_real_crypto_opportunities(
    market: str = "CRYPTO",
    limit: int = 10,
    max_workers: int = 10,
) -> list[dict]:
    """
    Compute real opportunities using parallel fetch with 60s cache.

    Cache hit: returns immediately (< 0.01s)
    Cache miss: parallel fetch (~30s)
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import time

    # ---- CACHE CHECK ----
    cache_key = f"{market.upper()}:{limit}"
    now = time.time()

    cached = _CACHE.get(cache_key)
    if cached is not None:
        expires_at, data = cached
        if now < expires_at:
            return data

    watchlist = DEFAULT_WATCHLIST.get(market.upper(), DEFAULT_WATCHLIST["CRYPTO"])

    opportunities: list[dict] = []
    started = time.time()

    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(_compute_one, symbol): symbol
                for symbol in watchlist
            }
            for future in as_completed(futures, timeout=90):
                try:
                    result = future.result(timeout=60)
                    if result is not None:
                        opportunities.append(result)
                except Exception:
                    continue
    except Exception:
        # Timeout or executor failure — return whatever we got
        pass

    elapsed = time.time() - started

    # Sort by strength descending
    opportunities.sort(
        key=lambda o: o.get("strength", o.get("score", 0)),
        reverse=True,
    )

    # Attach timing metadata to each opportunity
    for opp in opportunities:
        opp["_parallel_fetch_seconds"] = round(elapsed, 2)

    result = opportunities[:limit]

    # ---- STORE CACHE ----
    _CACHE[cache_key] = (now + _CACHE_TTL, result)

    return result


def clear_cache() -> None:
    """Clear the discovery cache."""
    _CACHE.clear()


def cache_info() -> dict:
    """Return cache metadata."""
    import time
    now = time.time()
    return {
        "entries": len(_CACHE),
        "ttl_seconds": _CACHE_TTL,
        "keys": list(_CACHE.keys()),
        "details": {
            key: {
                "expires_in_seconds": round(max(0, exp - now), 1),
                "fresh": now < exp,
            }
            for key, (exp, _) in _CACHE.items()
        },
    }


__all__ = [
    "signal_to_opportunity",
    "get_real_crypto_opportunities",
    "clear_cache",
    "cache_info",
    "DEFAULT_WATCHLIST",
]
