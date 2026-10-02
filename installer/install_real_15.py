"""Install advanced_stats_engine.py — Hurst, Entropy, Fractal, Autocorr"""
from pathlib import Path

ROOT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\intelligence\real")

FILE = '''"""
ROBOMLM_PLUS - Advanced Statistics Engine

Deeper math that quantifies market structure:

    - Hurst Exponent      : trending (>0.5) vs mean-reverting (<0.5)
    - Shannon Entropy     : randomness (high = chaos)
    - Autocorrelation     : momentum persistence
    - Fractal Dimension   : market complexity
    - Z-Score             : how far from mean
    - Skewness / Kurtosis : return distribution shape

These quantify WHAT TYPE of market we are in.
Direction comes from flow. This tells us which strategy to trust.
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite, log, sqrt, exp, pi
from typing import Optional
import statistics

from app.intelligence.real.real_market_data import get_real_market_data


@dataclass(frozen=True)
class AdvancedStatsSnapshot:
    symbol: str
    timestamp: str

    # Hurst
    hurst_exponent: Optional[float]
    hurst_interpretation: str      # TRENDING | MEAN_REVERTING | RANDOM_WALK

    # Entropy
    shannon_entropy: Optional[float]
    entropy_interpretation: str    # PREDICTABLE | MODERATE | CHAOTIC

    # Autocorrelation
    autocorr_lag1: Optional[float]
    autocorr_lag5: Optional[float]
    autocorr_interpretation: str   # PERSISTENT | ANTI_PERSISTENT | NEUTRAL

    # Fractal
    fractal_dimension: Optional[float]
    fractal_interpretation: str

    # Distribution
    mean_return: Optional[float]
    std_return: Optional[float]
    skewness: Optional[float]
    kurtosis: Optional[float]
    z_score: Optional[float]
    z_score_interpretation: str    # EXTREME_HIGH | EXTREME_LOW | NORMAL

    # Regime
    market_regime: str             # TRENDING | RANGING | CHAOTIC | TRANSITIONAL
    regime_strength: float         # 0-100

    reasons: tuple
    provenance: str = "REAL_STATS"

    def to_dict(self):
        def r(v):
            return round(v, 6) if v is not None else None
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp,
            "hurst": {
                "value": self.hurst_exponent,
                "interpretation": self.hurst_interpretation,
            },
            "entropy": {
                "value": self.shannon_entropy,
                "interpretation": self.entropy_interpretation,
            },
            "autocorrelation": {
                "lag1": self.autocorr_lag1,
                "lag5": self.autocorr_lag5,
                "interpretation": self.autocorr_interpretation,
            },
            "fractal": {
                "value": self.fractal_dimension,
                "interpretation": self.fractal_interpretation,
            },
            "distribution": {
                "mean_return": self.mean_return,
                "std_return": self.std_return,
                "skewness": self.skewness,
                "kurtosis": self.kurtosis,
                "z_score": self.z_score,
                "z_interpretation": self.z_score_interpretation,
            },
            "regime": {
                "type": self.market_regime,
                "strength": self.regime_strength,
                "reasons": list(self.reasons),
            },
        }


# ============================================================
# MATH
# ============================================================

def _log_returns(closes):
    out = []
    for i in range(1, len(closes)):
        if closes[i - 1] > 0 and closes[i] > 0:
            out.append(log(closes[i] / closes[i - 1]))
    return out


def _hurst(series, max_lag=20):
    """
    R/S analysis for Hurst exponent.
    H > 0.5  → trending (persistent)
    H = 0.5  → random walk
    H < 0.5  → mean reverting (anti-persistent)
    """
    n = len(series)
    if n < 30:
        return None
    try:
        lags = range(2, min(max_lag, n // 2))
        rs_values = []
        for lag in lags:
            chunks = [series[i:i + lag] for i in range(0, n - lag, lag)]
            rs_chunk = []
            for chunk in chunks:
                if len(chunk) < 2:
                    continue
                m = sum(chunk) / len(chunk)
                dev = [x - m for x in chunk]
                z = [sum(dev[:i+1]) for i in range(len(dev))]
                r = max(z) - min(z)
                s = sqrt(sum(d * d for d in dev) / len(dev))
                if s > 0:
                    rs_chunk.append(r / s)
            if rs_chunk:
                rs_values.append((log(lag), log(sum(rs_chunk) / len(rs_chunk))))
        if len(rs_values) < 2:
            return None
        # Linear regression slope
        x_mean = sum(x for x, _ in rs_values) / len(rs_values)
        y_mean = sum(y for _, y in rs_values) / len(rs_values)
        num = sum((x - x_mean) * (y - y_mean) for x, y in rs_values)
        den = sum((x - x_mean) ** 2 for x, _ in rs_values)
        if den == 0:
            return None
        return num / den
    except Exception:
        return None


def _shannon_entropy(series, bins=10):
    """Bin the returns and compute entropy (nats)."""
    if len(series) < 10:
        return None
    try:
        lo, hi = min(series), max(series)
        if hi <= lo:
            return 0.0
        bucket_size = (hi - lo) / bins
        counts = [0] * bins
        for v in series:
            idx = int((v - lo) / bucket_size)
            idx = max(0, min(bins - 1, idx))
            counts[idx] += 1
        total = sum(counts)
        if total == 0:
            return None
        h = 0.0
        for c in counts:
            if c > 0:
                p = c / total
                h -= p * log(p)
        return h
    except Exception:
        return None


def _autocorr(series, lag=1):
    if len(series) < lag + 3:
        return None
    try:
        n = len(series) - lag
        mean_s = sum(series) / len(series)
        num = sum((series[i] - mean_s) * (series[i + lag] - mean_s) for i in range(n))
        den = sum((x - mean_s) ** 2 for x in series)
        if den == 0:
            return None
        return num / den
    except Exception:
        return None


def _skewness(series):
    n = len(series)
    if n < 3:
        return None
    m = sum(series) / n
    s = sqrt(sum((x - m) ** 2 for x in series) / n)
    if s == 0:
        return None
    return sum(((x - m) / s) ** 3 for x in series) / n


def _kurtosis(series):
    n = len(series)
    if n < 4:
        return None
    m = sum(series) / n
    s = sqrt(sum((x - m) ** 2 for x in series) / n)
    if s == 0:
        return None
    return sum(((x - m) / s) ** 4 for x in series) / n - 3.0


# ============================================================
# ENGINE
# ============================================================

class AdvancedStatsEngine:

    def compute(self, symbol: str) -> AdvancedStatsSnapshot:

        now = datetime.now(timezone.utc)
        md = get_real_market_data()
        reasons = []

        candles, _ = md.get_candles(symbol, "15", 200)
        if not candles or len(candles) < 50:
            return self._empty(symbol, now)

        closes = [c.close for c in candles]
        returns = _log_returns(closes)

        # Hurst
        hurst = _hurst(returns, max_lag=20)
        if hurst is None:
            hurst_interp = "UNKNOWN"
        elif hurst > 0.6:
            hurst_interp = "TRENDING"
            reasons.append(f"Hurst={hurst:.3f} → persistent trend regime")
        elif hurst < 0.4:
            hurst_interp = "MEAN_REVERTING"
            reasons.append(f"Hurst={hurst:.3f} → mean reversion regime")
        else:
            hurst_interp = "RANDOM_WALK"

        # Entropy
        entropy = _shannon_entropy(returns, bins=10)
        if entropy is None:
            entropy_interp = "UNKNOWN"
        elif entropy < 1.5:
            entropy_interp = "PREDICTABLE"
            reasons.append(f"Entropy={entropy:.2f} → low randomness")
        elif entropy < 2.2:
            entropy_interp = "MODERATE"
        else:
            entropy_interp = "CHAOTIC"
            reasons.append(f"Entropy={entropy:.2f} → high chaos")

        # Autocorrelation
        ac1 = _autocorr(returns, lag=1)
        ac5 = _autocorr(returns, lag=5)

        if ac1 is None:
            ac_interp = "UNKNOWN"
        elif ac1 > 0.1:
            ac_interp = "PERSISTENT"
            reasons.append(f"Autocorr lag1={ac1:.3f} → momentum continues")
        elif ac1 < -0.1:
            ac_interp = "ANTI_PERSISTENT"
            reasons.append(f"Autocorr lag1={ac1:.3f} → reversals likely")
        else:
            ac_interp = "NEUTRAL"

        # Fractal dimension approximation: D = 2 - H
        frac_dim = 2.0 - hurst if hurst is not None else None

        if frac_dim is None:
            frac_interp = "UNKNOWN"
        elif frac_dim < 1.4:
            frac_interp = "SMOOTH_TREND"
        elif frac_dim > 1.6:
            frac_interp = "ROUGH_CHOPPY"
        else:
            frac_interp = "NORMAL"

        # Distribution
        mean_r = sum(returns) / len(returns) if returns else None
        std_r = statistics.pstdev(returns) if len(returns) > 1 else None
        skew = _skewness(returns)
        kurt = _kurtosis(returns)

        # Z-score of last return vs distribution
        z = None
        z_interp = "UNKNOWN"
        if returns and std_r and std_r > 0:
            z = returns[-1] / std_r
            if z > 2.0:
                z_interp = "EXTREME_HIGH"
            elif z < -2.0:
                z_interp = "EXTREME_LOW"
            else:
                z_interp = "NORMAL"

        # Regime classification
        if hurst is None or entropy is None:
            regime = "UNKNOWN"
            regime_strength = 0.0
        else:
            if hurst > 0.6 and entropy < 2.0:
                regime = "TRENDING"
                regime_strength = min(100.0, (hurst - 0.5) * 300)
            elif hurst < 0.4 and entropy < 2.0:
                regime = "RANGING"
                regime_strength = min(100.0, (0.5 - hurst) * 300)
            elif entropy > 2.3:
                regime = "CHAOTIC"
                regime_strength = min(100.0, (entropy - 2.0) * 100)
            else:
                regime = "TRANSITIONAL"
                regime_strength = 40.0

        return AdvancedStatsSnapshot(
            symbol=symbol,
            timestamp=now.isoformat(),
            hurst_exponent=round(hurst, 4) if hurst is not None else None,
            hurst_interpretation=hurst_interp,
            shannon_entropy=round(entropy, 4) if entropy is not None else None,
            entropy_interpretation=entropy_interp,
            autocorr_lag1=round(ac1, 4) if ac1 is not None else None,
            autocorr_lag5=round(ac5, 4) if ac5 is not None else None,
            autocorr_interpretation=ac_interp,
            fractal_dimension=round(frac_dim, 4) if frac_dim is not None else None,
            fractal_interpretation=frac_interp,
            mean_return=round(mean_r, 8) if mean_r is not None else None,
            std_return=round(std_r, 8) if std_r is not None else None,
            skewness=round(skew, 4) if skew is not None else None,
            kurtosis=round(kurt, 4) if kurt is not None else None,
            z_score=round(z, 4) if z is not None else None,
            z_score_interpretation=z_interp,
            market_regime=regime,
            regime_strength=round(regime_strength, 2),
            reasons=tuple(reasons),
        )

    def _empty(self, symbol, now):
        return AdvancedStatsSnapshot(
            symbol=symbol, timestamp=now.isoformat(),
            hurst_exponent=None, hurst_interpretation="UNKNOWN",
            shannon_entropy=None, entropy_interpretation="UNKNOWN",
            autocorr_lag1=None, autocorr_lag5=None,
            autocorr_interpretation="UNKNOWN",
            fractal_dimension=None, fractal_interpretation="UNKNOWN",
            mean_return=None, std_return=None,
            skewness=None, kurtosis=None,
            z_score=None, z_score_interpretation="UNKNOWN",
            market_regime="UNKNOWN", regime_strength=0.0,
            reasons=("INSUFFICIENT_DATA",),
        )


_engine: Optional[AdvancedStatsEngine] = None
_lock = None


def get_advanced_stats_engine() -> AdvancedStatsEngine:
    global _engine, _lock
    if _lock is None:
        from threading import RLock
        _lock = RLock()
    with _lock:
        if _engine is None:
            _engine = AdvancedStatsEngine()
        return _engine


__all__ = [
    "AdvancedStatsSnapshot",
    "AdvancedStatsEngine",
    "get_advanced_stats_engine",
]
'''

(ROOT / "advanced_stats_engine.py").write_text(FILE, encoding="utf-8")
print(f"WROTE: {ROOT / 'advanced_stats_engine.py'}")