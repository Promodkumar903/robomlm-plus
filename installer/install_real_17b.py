"""Install real_discovery_bridge.py — wire unified_signal to Discovery"""
from pathlib import Path

ROOT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\intelligence\real")

FILE = '''"""
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


def get_real_crypto_opportunities(
    market: str = "CRYPTO",
    limit: int = 10,
) -> list[dict]:
    """
    Compute real opportunities for the given market using unified_signal.
    """
    engine = get_unified_signal_engine()
    watchlist = DEFAULT_WATCHLIST.get(market.upper(), DEFAULT_WATCHLIST["CRYPTO"])

    opportunities = []
    for symbol in watchlist:
        try:
            signal = engine.compute(symbol)
            opp = signal_to_opportunity(signal)
            opportunities.append(opp)
        except Exception as e:
            # Don't fabricate — skip on error
            continue

    # Sort by strength descending
    opportunities.sort(key=lambda o: o.get("strength", o.get("score", 0)), reverse=True)
    return opportunities[:limit]


__all__ = [
    "signal_to_opportunity",
    "get_real_crypto_opportunities",
    "DEFAULT_WATCHLIST",
]
'''

(ROOT / "real_discovery_bridge.py").write_text(FILE, encoding="utf-8")
print(f"WROTE: {ROOT / 'real_discovery_bridge.py'}")
print()
print("Test:")
print('  python -c "from app.intelligence.real.real_discovery_bridge import get_real_crypto_opportunities; opps = get_real_crypto_opportunities(\\"CRYPTO\\", 5); [print(f\\"{o[\\"symbol\\"]:12} {o[\\"direction\\"]:8} score={o[\\"score\\"]:6.2f} grade={o[\\"grade\\"]:5} RR={o.get(\\"risk_reward\\")} action_eligible={o[\\"eligible\\"]}\\") for o in opps]"')