"""Install market_context_engine.py — session, weekday, vol regime, correlations"""
from pathlib import Path

ROOT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\intelligence\real")

FILE = '''"""
ROBOMLM_PLUS - Market Context Engine

Context around the market:
    - Session (Asia / London / US / Overlap)
    - Weekday bias
    - Realized volatility (5m / 1h / 24h)
    - Volatility regime (LOW / NORMAL / HIGH / EXTREME)
    - Correlation (BTC reference pairs)
    - Time to funding
    - Hours to weekly close
    - Market activity score
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from math import isfinite, sqrt
from typing import Optional

from app.intelligence.real.real_market_data import get_real_market_data


@dataclass(frozen=True)
class MarketContextSnapshot:
    symbol: str
    timestamp: str

    # Session
    session: str                   # ASIA | LONDON | US | OVERLAP | CLOSED
    session_note: str
    hours_to_next_funding: Optional[float]

    # Weekday
    weekday: str                   # MON..SUN
    weekday_note: str

    # Realized volatility
    realized_vol_5m: Optional[float]
    realized_vol_1h: Optional[float]
    realized_vol_24h: Optional[float]
    vol_regime: str                # LOW | NORMAL | HIGH | EXTREME
    vol_trend: str                 # EXPANDING | CONTRACTING | STABLE

    # Correlations (approx from last 100 1h candles)
    corr_btc: Optional[float]
    corr_eth: Optional[float]
    corr_sol: Optional[float]
    correlation_note: str

    # Activity
    activity_score: float          # 0-100 from vol + volume
    activity_note: str

    # Verdict
    context_bias: str              # BULLISH | BEARISH | NEUTRAL
    context_strength: float        # 0-100
    reasons: tuple

    provenance: str = "REAL_CONTEXT"

    def to_dict(self):
        def r(v):
            return round(v, 6) if v is not None else None
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp,
            "session": {
                "current": self.session,
                "note": self.session_note,
                "hours_to_funding": self.hours_to_next_funding,
            },
            "weekday": {
                "day": self.weekday,
                "note": self.weekday_note,
            },
            "volatility": {
                "realized_5m": self.realized_vol_5m,
                "realized_1h": self.realized_vol_1h,
                "realized_24h": self.realized_vol_24h,
                "regime": self.vol_regime,
                "trend": self.vol_trend,
            },
            "correlation": {
                "btc": self.corr_btc,
                "eth": self.corr_eth,
                "sol": self.corr_sol,
                "note": self.correlation_note,
            },
            "activity": {
                "score": self.activity_score,
                "note": self.activity_note,
            },
            "verdict": {
                "bias": self.context_bias,
                "strength": self.context_strength,
                "reasons": list(self.reasons),
            },
        }


def _realized_vol(closes):
    """Annualized realized vol from log returns."""
    if len(closes) < 3:
        return None
    import math
    log_returns = []
    for i in range(1, len(closes)):
        if closes[i] > 0 and closes[i - 1] > 0:
            log_returns.append(math.log(closes[i] / closes[i - 1]))
    if len(log_returns) < 2:
        return None
    mean_r = sum(log_returns) / len(log_returns)
    variance = sum((r - mean_r) ** 2 for r in log_returns) / len(log_returns)
    return sqrt(variance) * 100  # in %


def _correlation(series_a, series_b):
    """Pearson correlation."""
    n = min(len(series_a), len(series_b))
    if n < 5:
        return None
    a = series_a[-n:]
    b = series_b[-n:]
    mean_a = sum(a) / n
    mean_b = sum(b) / n
    num = sum((x - mean_a) * (y - mean_b) for x, y in zip(a, b))
    den_a = sqrt(sum((x - mean_a) ** 2 for x in a))
    den_b = sqrt(sum((y - mean_b) ** 2 for y in b))
    if den_a == 0 or den_b == 0:
        return None
    return num / (den_a * den_b)


def _returns(closes):
    if len(closes) < 2:
        return []
    out = []
    for i in range(1, len(closes)):
        if closes[i-1] > 0:
            out.append((closes[i] - closes[i-1]) / closes[i-1])
    return out


class MarketContextEngine:

    def compute(self, symbol: str) -> MarketContextSnapshot:

        now = datetime.now(timezone.utc)
        md = get_real_market_data()
        reasons = []

        candles_1m, _ = md.get_candles(symbol, "1", 100)
        candles_1h, _ = md.get_candles(symbol, "60", 200)

        # ---- SESSION ----
        hour = now.hour
        weekday_idx = now.weekday()
        weekday_names = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        weekday = weekday_names[weekday_idx]

        # Crypto: Asia 00-08, London 08-16, US 13-22, Overlap 13-16
        if 13 <= hour < 16:
            session = "OVERLAP"
            session_note = "London + US overlap — highest liquidity"
        elif 0 <= hour < 8:
            session = "ASIA"
            session_note = "Asia session — moderate activity"
        elif 8 <= hour < 16:
            session = "LONDON"
            session_note = "London session — high activity"
        elif 13 <= hour < 22:
            session = "US"
            session_note = "US session — high activity"
        else:
            session = "QUIET"
            session_note = "Low liquidity window"

        # Funding time: Bybit every 8 hours (00, 08, 16 UTC)
        next_funding_hour = ((hour // 8) + 1) * 8
        if next_funding_hour >= 24:
            next_funding_hour -= 24
        hours_to_funding = (next_funding_hour - hour) % 24
        if hours_to_funding == 0:
            hours_to_funding = 8

        # ---- WEEKDAY ----
        weekday_notes = {
            "MON": "Monday gap potential",
            "TUE": "Early-week trend",
            "WED": "Mid-week pivot",
            "THU": "Often strongest trend day",
            "FRI": "Friday profit-taking",
            "SAT": "Weekend low liquidity",
            "SUN": "Weekend low liquidity",
        }
        weekday_note = weekday_notes.get(weekday, "")

        # ---- REALIZED VOL ----
        vol_5m = vol_1h = vol_24h = None
        if candles_1m and len(candles_1m) >= 5:
            vol_5m = _realized_vol([c.close for c in candles_1m[-6:]])
        if candles_1m and len(candles_1m) >= 61:
            vol_1h = _realized_vol([c.close for c in candles_1m[-61:]])
        if candles_1h and len(candles_1h) >= 25:
            vol_24h = _realized_vol([c.close for c in candles_1h[-25:]])

        # Vol regime
        vol_regime = "UNKNOWN"
        vol_trend = "STABLE"
        if vol_1h is not None:
            if vol_1h > 1.5:
                vol_regime = "EXTREME"
            elif vol_1h > 0.6:
                vol_regime = "HIGH"
            elif vol_1h > 0.2:
                vol_regime = "NORMAL"
            else:
                vol_regime = "LOW"

        if vol_5m is not None and vol_1h is not None and vol_1h > 0:
            ratio = vol_5m / vol_1h
            if ratio > 1.3:
                vol_trend = "EXPANDING"
            elif ratio < 0.7:
                vol_trend = "CONTRACTING"

        # ---- CORRELATIONS ----
        corr_btc = corr_eth = corr_sol = None

        base_symbol = symbol.replace("/", "").upper()

        ref_pairs = {
            "btc": "BTC/USDT",
            "eth": "ETH/USDT",
            "sol": "SOL/USDT",
        }

        base_closes = [c.close for c in candles_1h[-50:]] if candles_1h else []
        base_returns = _returns(base_closes)

        for key, ref_symbol in ref_pairs.items():
            if ref_symbol.replace("/", "").upper() == base_symbol:
                continue
            ref_candles, _ = md.get_candles(ref_symbol, "60", 60)
            if not ref_candles:
                continue
            ref_closes = [c.close for c in ref_candles[-50:]]
            ref_returns = _returns(ref_closes)
            c = _correlation(base_returns, ref_returns)
            if key == "btc":
                corr_btc = c
            elif key == "eth":
                corr_eth = c
            elif key == "sol":
                corr_sol = c

        corr_note = ""
        if corr_btc is not None and corr_btc > 0.7:
            corr_note = "High BTC correlation"
        elif corr_btc is not None and corr_btc < 0.3:
            corr_note = "Decoupled from BTC"

        # ---- ACTIVITY SCORE ----
        activity = 0.0
        if vol_1h is not None:
            activity += min(50.0, vol_1h * 50)
        if session in {"LONDON", "US", "OVERLAP"}:
            activity += 30
        elif session == "ASIA":
            activity += 20
        else:
            activity += 10
        if weekday in {"SAT", "SUN"}:
            activity -= 15
        activity = max(0.0, min(100.0, activity))

        if activity > 70:
            activity_note = "High market activity — good liquidity"
        elif activity > 40:
            activity_note = "Moderate activity"
        else:
            activity_note = "Low activity — wide spreads likely"

        # ---- VERDICT ----
        # Context doesn't give direction — but it modifies confidence
        # Higher activity → more reliable signals
        # Extreme vol → risky to trade
        bull = 0.0
        bear = 0.0

        # Vol regime affects caution, not direction
        if vol_regime == "EXTREME":
            reasons.append("Extreme volatility — reduce size")
        elif vol_regime == "HIGH":
            reasons.append("High volatility — wider stops needed")

        if session == "OVERLAP":
            reasons.append("Overlap session — highest liquidity")
        elif session == "QUIET":
            reasons.append("Quiet session — avoid market orders")

        # Context bias: neutral unless strong signal
        context_bias = "NEUTRAL"
        context_strength = activity  # Strength = activity quality

        return MarketContextSnapshot(
            symbol=symbol,
            timestamp=now.isoformat(),
            session=session,
            session_note=session_note,
            hours_to_next_funding=float(hours_to_funding),
            weekday=weekday,
            weekday_note=weekday_note,
            realized_vol_5m=round(vol_5m, 6) if vol_5m is not None else None,
            realized_vol_1h=round(vol_1h, 6) if vol_1h is not None else None,
            realized_vol_24h=round(vol_24h, 6) if vol_24h is not None else None,
            vol_regime=vol_regime,
            vol_trend=vol_trend,
            corr_btc=round(corr_btc, 4) if corr_btc is not None else None,
            corr_eth=round(corr_eth, 4) if corr_eth is not None else None,
            corr_sol=round(corr_sol, 4) if corr_sol is not None else None,
            correlation_note=corr_note,
            activity_score=round(activity, 2),
            activity_note=activity_note,
            context_bias=context_bias,
            context_strength=round(context_strength, 2),
            reasons=tuple(reasons),
        )


_engine: Optional[MarketContextEngine] = None
_lock = None


def get_market_context_engine() -> MarketContextEngine:
    global _engine, _lock
    if _lock is None:
        from threading import RLock
        _lock = RLock()
    with _lock:
        if _engine is None:
            _engine = MarketContextEngine()
        return _engine


__all__ = [
    "MarketContextSnapshot",
    "MarketContextEngine",
    "get_market_context_engine",
]
'''

(ROOT / "market_context_engine.py").write_text(FILE, encoding="utf-8")
print(f"WROTE: {ROOT / 'market_context_engine.py'}")