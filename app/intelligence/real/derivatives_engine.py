"""
ROBOMLM_PLUS - Derivatives Engine

Collects REAL derivatives data from Bybit v5:
    - Basis (perp premium/discount vs spot)
    - Open Interest (current + delta history)
    - Funding Rate (current + history + trend)
    - Long/Short Ratio (retail vs top traders)
    - Liquidation flow (aggregated)

Output feeds flow_direction_engine for accurate direction.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from math import isfinite
from threading import RLock
from typing import Optional
import json
import time
import urllib.request


BYBIT_BASE = "https://api.bybit.com"
TIMEOUT = 8


# ============================================================
# RESULT
# ============================================================

@dataclass(frozen=True)
class DerivativesSnapshot:
    symbol: str
    timestamp: str

    # ---- Basis ----
    basis_pct: Optional[float]             # (perp - spot) / spot * 100
    basis_state: str                       # PREMIUM | DISCOUNT | NEUTRAL
    basis_history_1h: tuple                # last 12 points (5min)
    basis_trend: str                       # RISING | FALLING | STABLE

    # ---- Open Interest ----
    open_interest: Optional[float]
    oi_change_5m_pct: Optional[float]
    oi_change_15m_pct: Optional[float]
    oi_change_1h_pct: Optional[float]
    oi_trend: str                          # RISING | FALLING | STABLE
    oi_interpretation: str                 # NEW_LONGS | NEW_SHORTS | LONGS_CLOSING | SHORTS_CLOSING | NEUTRAL

    # ---- Funding ----
    funding_rate: Optional[float]
    funding_history_8: tuple               # last 8 funding rates
    funding_avg_8: Optional[float]
    funding_trend: str                     # RISING | FALLING | STABLE
    funding_state: str                     # LONG_HEAVY | SHORT_HEAVY | BALANCED
    funding_extreme: bool

    # ---- Long/Short Ratio ----
    ls_ratio_retail: Optional[float]
    ls_ratio_top: Optional[float]
    ls_divergence: bool                    # retail vs top diverge
    ls_signal: str                         # CROWD_LONG | CROWD_SHORT | BALANCED | CONTRARIAN_BULL | CONTRARIAN_BEAR

    # ---- Liquidations (aggregate) ----
    liq_long_24h: Optional[float]          # USD liquidated on long side
    liq_short_24h: Optional[float]
    liq_dominant_side: str                 # LONGS | SHORTS | BALANCED

    # ---- Verdict ----
    derivative_direction: str              # BULLISH | BEARISH | NEUTRAL
    derivative_strength: float             # 0-100
    reasons: tuple

    provenance: str = "BYBIT_DERIVATIVES"

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp,
            "basis": {
                "pct": self.basis_pct,
                "state": self.basis_state,
                "history_1h": list(self.basis_history_1h),
                "trend": self.basis_trend,
            },
            "open_interest": {
                "current": self.open_interest,
                "change_5m_pct": self.oi_change_5m_pct,
                "change_15m_pct": self.oi_change_15m_pct,
                "change_1h_pct": self.oi_change_1h_pct,
                "trend": self.oi_trend,
                "interpretation": self.oi_interpretation,
            },
            "funding": {
                "current": self.funding_rate,
                "history_8": list(self.funding_history_8),
                "avg_8": self.funding_avg_8,
                "trend": self.funding_trend,
                "state": self.funding_state,
                "extreme": self.funding_extreme,
            },
            "long_short": {
                "retail": self.ls_ratio_retail,
                "top": self.ls_ratio_top,
                "divergence": self.ls_divergence,
                "signal": self.ls_signal,
            },
            "liquidations": {
                "long_24h_usd": self.liq_long_24h,
                "short_24h_usd": self.liq_short_24h,
                "dominant": self.liq_dominant_side,
            },
            "verdict": {
                "direction": self.derivative_direction,
                "strength": self.derivative_strength,
                "reasons": list(self.reasons),
            },
        }


# ============================================================
# FETCH HELPERS
# ============================================================

def _get(path, params=None):
    url = BYBIT_BASE + path
    if params:
        q = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{q}"
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as r:
            return json.loads(r.read())
    except Exception:
        return None


def _f(v, default=None):
    try:
        n = float(v)
        return n if isfinite(n) else default
    except (TypeError, ValueError):
        return default


def _norm_symbol(symbol):
    """BTC/USDT -> BTCUSDT (Bybit format)"""
    return str(symbol).replace("/", "").upper()


def _get_spot_price(symbol):
    raw = _get(
        "/v5/market/tickers",
        {"category": "spot", "symbol": _norm_symbol(symbol)},
    )
    if not raw:
        return None
    items = ((raw.get("result") or {}).get("list") or [])
    if not items:
        return None
    return _f(items[0].get("lastPrice"))


def _get_perp_price(symbol):
    raw = _get(
        "/v5/market/tickers",
        {"category": "linear", "symbol": _norm_symbol(symbol)},
    )
    if not raw:
        return None
    items = ((raw.get("result") or {}).get("list") or [])
    if not items:
        return None
    return _f(items[0].get("lastPrice"))


# ============================================================
# ENGINE
# ============================================================

class DerivativesEngine:

    CACHE_TTL = 20

    def __init__(self):
        self._lock = RLock()
        self._cache = {}

    def _cached(self, key, fn):
        now = time.time()
        with self._lock:
            entry = self._cache.get(key)
            if entry and now < entry[0]:
                return entry[1]
        value = fn()
        with self._lock:
            self._cache[key] = (now + self.CACHE_TTL, value)
        return value

    # --------------------------------------------------------
    # BASIS
    # --------------------------------------------------------

    def _fetch_basis(self, symbol):
        def fetch():
            return _get(
                "/v5/market/premium-index-price-kline",
                {"category": "linear", "symbol": _norm_symbol(symbol),
                 "interval": "5", "limit": 12},
            )
        return self._cached(f"basis:{_norm_symbol(symbol)}", fetch)

    def _compute_basis(self, symbol, spot_price):
        # Get spot and perp prices
        spot = spot_price if spot_price else _get_spot_price(symbol)
        perp = _get_perp_price(symbol)

        if spot is None or perp is None or spot <= 0:
            return None, "NEUTRAL", (), "STABLE"

        basis_pct = (perp - spot) / spot * 100

        if basis_pct > 0.05:
            state = "PREMIUM"
        elif basis_pct < -0.05:
            state = "DISCOUNT"
        else:
            state = "NEUTRAL"

        # Trend from funding history (basis history not directly available)
        raw = self._fetch_funding(symbol)
        history = []
        if raw:
            items = ((raw.get("result") or {}).get("list") or [])
            for row in items:
                r = _f(row.get("fundingRate"))
                if r is not None:
                    history.append(r)

        if len(history) >= 3:
            if history[0] > history[-1] * 1.2:
                trend = "RISING"
            elif history[0] < history[-1] * 0.8:
                trend = "FALLING"
            else:
                trend = "STABLE"
        else:
            trend = "STABLE"

        return basis_pct, state, tuple(history[:12]), trend

    # --------------------------------------------------------
    # OPEN INTEREST
    # --------------------------------------------------------

    def _fetch_oi_history(self, symbol):
        def fetch():
            return _get(
                "/v5/market/open-interest",
                {"category": "linear", "symbol": _norm_symbol(symbol),
                 "intervalTime": "5min", "limit": 24},
            )
        return self._cached(f"oi_hist:{_norm_symbol(symbol)}", fetch)

    def _compute_oi(self, symbol):
        raw = self._fetch_oi_history(symbol)
        if not raw:
            return None, None, None, None, "STABLE"

        items = ((raw.get("result") or {}).get("list") or [])
        if not items:
            return None, None, None, None, "STABLE"

        try:
            latest = float(items[0].get("openInterest"))
        except (ValueError, TypeError, AttributeError):
            return None, None, None, None, "STABLE"

        # items are [latest, ..., oldest]
        changes = {}
        for label, back in (("5m", 1), ("15m", 3), ("1h", 12)):
            if len(items) > back:
                try:
                    old = float(items[back].get("openInterest"))
                    if old > 0:
                        changes[label] = (latest - old) / old * 100
                except (ValueError, TypeError, AttributeError):
                    pass

        # Trend
        c5 = changes.get("5m", 0)
        c1h = changes.get("1h", 0)
        if c5 > 0.3 or c1h > 1.0:
            trend = "RISING"
        elif c5 < -0.3 or c1h < -1.0:
            trend = "FALLING"
        else:
            trend = "STABLE"

        return (
            latest,
            changes.get("5m"),
            changes.get("15m"),
            changes.get("1h"),
            trend,
        )

    # --------------------------------------------------------
    # FUNDING
    # --------------------------------------------------------

    def _fetch_funding(self, symbol):
        def fetch():
            return _get(
                "/v5/market/funding/history",
                {"category": "linear", "symbol": _norm_symbol(symbol), "limit": 8},
            )
        return self._cached(f"funding:{_norm_symbol(symbol)}", fetch)

    def _compute_funding(self, symbol):
        raw = self._fetch_funding(symbol)
        if not raw:
            return None, (), None, "STABLE", "BALANCED", False

        items = ((raw.get("result") or {}).get("list") or [])
        if not items:
            return None, (), None, "STABLE", "BALANCED", False

        rates = []
        for row in items:
            try:
                rates.append(float(row.get("fundingRate")))
            except (ValueError, TypeError, AttributeError):
                continue

        if not rates:
            return None, (), None, "STABLE", "BALANCED", False

        current = rates[0]
        avg = sum(rates) / len(rates)

        # Trend
        if len(rates) >= 3:
            if rates[0] > rates[-1] * 1.2:
                trend = "RISING"
            elif rates[0] < rates[-1] * 0.8:
                trend = "FALLING"
            else:
                trend = "STABLE"
        else:
            trend = "STABLE"

        if current > 0.0003:
            state = "LONG_HEAVY"
        elif current < -0.0003:
            state = "SHORT_HEAVY"
        else:
            state = "BALANCED"

        extreme = abs(current) > 0.001 or abs(avg) > 0.0008

        return current, tuple(rates), avg, trend, state, extreme

    # --------------------------------------------------------
    # LONG/SHORT RATIO
    # --------------------------------------------------------

    def _fetch_ls_ratio(self, symbol):
        def fetch():
            return _get(
                "/v5/market/account-ratio",
                {"category": "linear", "symbol": _norm_symbol(symbol),
                 "period": "5min", "limit": 1},
            )
        return self._cached(f"ls_ratio:{_norm_symbol(symbol)}", fetch)

    def _compute_ls(self, symbol):
        raw = self._fetch_ls_ratio(symbol)
        if not raw:
            return None, None, False, "BALANCED"

        items = ((raw.get("result") or {}).get("list") or [])
        if not items:
            return None, None, False, "BALANCED"

        try:
            buy_ratio = float(items[0].get("buyRatio", 0))
            sell_ratio = float(items[0].get("sellRatio", 0))
            if sell_ratio > 0:
                retail_ls = buy_ratio / sell_ratio
            else:
                retail_ls = None
        except (ValueError, TypeError, AttributeError):
            return None, None, False, "BALANCED"

        # Bybit only gives one ratio via this endpoint (retail)
        top_ls = None  # Would need premium API

        divergence = False

        if retail_ls is None:
            signal = "BALANCED"
        elif retail_ls > 2.0:
            signal = "CROWD_LONG"   # Retail heavily long → contrarian bear
        elif retail_ls < 0.5:
            signal = "CROWD_SHORT"  # Retail heavily short → contrarian bull
        else:
            signal = "BALANCED"

        return retail_ls, top_ls, divergence, signal

    # --------------------------------------------------------
    # LIQUIDATIONS (aggregate — approximate from OI drops)
    # --------------------------------------------------------

    def _compute_liquidations(self, oi_current, oi_change_1h_pct):
        # Bybit liquidations only available via WS — approximate
        # If OI drops sharply + price moves, liquidations occurred
        if oi_current is None or oi_change_1h_pct is None:
            return None, None, "UNKNOWN"

        if oi_change_1h_pct < -2.0:
            # Significant OI drop = liquidations happened
            # We can't distinguish side without more data
            return None, None, "SIGNIFICANT"
        return None, None, "BALANCED"

    # --------------------------------------------------------
    # MAIN
    # --------------------------------------------------------

    def analyze(self, symbol: str, spot_price: Optional[float] = None) -> DerivativesSnapshot:

        now = datetime.now(timezone.utc)
        reasons = []

        # Basis
        basis_pct, basis_state, basis_hist, basis_trend = self._compute_basis(
            symbol, spot_price
        )

        # OI
        oi, oi_5m, oi_15m, oi_1h, oi_trend = self._compute_oi(symbol)

        # Funding
        funding, funding_hist, funding_avg, funding_trend, funding_state, funding_extreme = (
            self._compute_funding(symbol)
        )

        # L/S
        retail_ls, top_ls, ls_div, ls_signal = self._compute_ls(symbol)

        # Liquidations
        liq_long, liq_short, liq_dominant = self._compute_liquidations(oi, oi_1h)

        # ---- Interpretation ----
        oi_interp = "NEUTRAL"
        if oi_trend == "RISING" and funding_state == "LONG_HEAVY":
            oi_interp = "NEW_LONGS"
            reasons.append("OI rising + longs paying → new longs")
        elif oi_trend == "RISING" and funding_state == "SHORT_HEAVY":
            oi_interp = "NEW_SHORTS"
            reasons.append("OI rising + shorts paying → new shorts")
        elif oi_trend == "FALLING" and funding_state == "LONG_HEAVY":
            oi_interp = "LONGS_CLOSING"
            reasons.append("OI falling + longs paying → longs closing")
        elif oi_trend == "FALLING" and funding_state == "SHORT_HEAVY":
            oi_interp = "SHORTS_CLOSING"
            reasons.append("OI falling + shorts paying → shorts closing")

        # ---- Verdict ----
        bull = 0.0
        bear = 0.0

        # Basis premium = longs aggressive = bullish short-term
        # But extreme premium = crowded = contrarian
        if basis_state == "PREMIUM":
            if basis_pct and basis_pct > 0.20:
                bear += 15
                reasons.append(f"Extreme premium ({basis_pct:.3f}%) → crowd long")
            else:
                bull += 10
                reasons.append(f"Moderate premium ({basis_pct:.3f}%)")

        elif basis_state == "DISCOUNT":
            if basis_pct and basis_pct < -0.20:
                bull += 15
                reasons.append(f"Extreme discount ({basis_pct:.3f}%) → crowd short")
            else:
                bear += 10
                reasons.append(f"Moderate discount ({basis_pct:.3f}%)")

        # OI interpretation
        if oi_interp == "NEW_LONGS":
            bull += 12
        elif oi_interp == "NEW_SHORTS":
            bear += 12
        elif oi_interp == "LONGS_CLOSING":
            bear += 8
        elif oi_interp == "SHORTS_CLOSING":
            bull += 8

        # Funding extremes → contrarian
        if funding_extreme:
            if funding_state == "LONG_HEAVY":
                bear += 18
                reasons.append("Extreme positive funding → longs crowded")
            elif funding_state == "SHORT_HEAVY":
                bull += 18
                reasons.append("Extreme negative funding → shorts crowded")

        # L/S ratio
        if ls_signal == "CROWD_LONG":
            bear += 12
            reasons.append("Retail crowded long")
        elif ls_signal == "CROWD_SHORT":
            bull += 12
            reasons.append("Retail crowded short")

        total = bull + bear
        if total < 15:
            direction = "NEUTRAL"
            strength = 0.0
        elif bull > bear * 1.15:
            direction = "BULLISH"
            strength = round(bull / total * 100, 2)
        elif bear > bull * 1.15:
            direction = "BEARISH"
            strength = round(bear / total * 100, 2)
        else:
            direction = "NEUTRAL"
            strength = round(max(bull, bear) / total * 100, 2) if total > 0 else 0

        return DerivativesSnapshot(
            symbol=symbol,
            timestamp=now.isoformat(),
            basis_pct=round(basis_pct, 4) if basis_pct is not None else None,
            basis_state=basis_state,
            basis_history_1h=basis_hist,
            basis_trend=basis_trend,
            open_interest=oi,
            oi_change_5m_pct=round(oi_5m, 4) if oi_5m is not None else None,
            oi_change_15m_pct=round(oi_15m, 4) if oi_15m is not None else None,
            oi_change_1h_pct=round(oi_1h, 4) if oi_1h is not None else None,
            oi_trend=oi_trend,
            oi_interpretation=oi_interp,
            funding_rate=funding,
            funding_history_8=funding_hist,
            funding_avg_8=round(funding_avg, 8) if funding_avg is not None else None,
            funding_trend=funding_trend,
            funding_state=funding_state,
            funding_extreme=funding_extreme,
            ls_ratio_retail=round(retail_ls, 4) if retail_ls is not None else None,
            ls_ratio_top=round(top_ls, 4) if top_ls is not None else None,
            ls_divergence=ls_div,
            ls_signal=ls_signal,
            liq_long_24h=liq_long,
            liq_short_24h=liq_short,
            liq_dominant_side=liq_dominant,
            derivative_direction=direction,
            derivative_strength=strength,
            reasons=tuple(reasons),
        )


_engine: Optional[DerivativesEngine] = None
_lock = RLock()


def get_derivatives_engine() -> DerivativesEngine:
    global _engine
    with _lock:
        if _engine is None:
            _engine = DerivativesEngine()
        return _engine


__all__ = [
    "DerivativesSnapshot",
    "DerivativesEngine",
    "get_derivatives_engine",
]
