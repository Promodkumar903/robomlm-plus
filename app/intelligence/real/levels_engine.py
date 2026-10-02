"""
ROBOMLM_PLUS - Levels Engine

Collects INSTITUTIONAL levels that matter to professional traders:

    - Pivot Points (Classic + Fibonacci + Camarilla)
    - Previous session H/L (Asia / London / US)
    - Previous Day / Week / Month H/L
    - VWAP (session + daily + weekly + anchored)
    - VWAP bands (1σ, 2σ, 3σ)
    - Fibonacci retracement + extension
    - Round numbers

These are HIGH-PROBABILITY levels where SL / limit orders cluster.

All values computed from real OHLCV. No hardcoding.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from math import isfinite
from typing import Optional, Sequence

from app.intelligence.real.real_market_data import (
    get_real_market_data,
    Candle,
)


# ============================================================
# RESULT
# ============================================================

@dataclass(frozen=True)
class LevelsSnapshot:
    symbol: str
    current_price: float
    timestamp: str

    # Pivot Points (Classic)
    pivot_pp: Optional[float]
    pivot_r1: Optional[float]
    pivot_r2: Optional[float]
    pivot_r3: Optional[float]
    pivot_s1: Optional[float]
    pivot_s2: Optional[float]
    pivot_s3: Optional[float]

    # Fibonacci Pivot
    fib_r1: Optional[float]
    fib_r2: Optional[float]
    fib_r3: Optional[float]
    fib_s1: Optional[float]
    fib_s2: Optional[float]
    fib_s3: Optional[float]

    # Camarilla
    cam_h3: Optional[float]
    cam_h4: Optional[float]
    cam_l3: Optional[float]
    cam_l4: Optional[float]

    # Previous periods
    prev_day_high: Optional[float]
    prev_day_low: Optional[float]
    prev_day_close: Optional[float]
    prev_week_high: Optional[float]
    prev_week_low: Optional[float]
    prev_month_high: Optional[float]
    prev_month_low: Optional[float]

    # Session levels (Asia / London / US)
    asia_high: Optional[float]
    asia_low: Optional[float]
    london_high: Optional[float]
    london_low: Optional[float]
    us_high: Optional[float]
    us_low: Optional[float]

    # VWAP
    vwap_session: Optional[float]
    vwap_daily: Optional[float]
    vwap_weekly: Optional[float]
    vwap_upper_1: Optional[float]
    vwap_upper_2: Optional[float]
    vwap_lower_1: Optional[float]
    vwap_lower_2: Optional[float]

    # Fibonacci (from last swing)
    fib_236: Optional[float]
    fib_382: Optional[float]
    fib_500: Optional[float]
    fib_618: Optional[float]
    fib_786: Optional[float]
    fib_ext_1272: Optional[float]
    fib_ext_1618: Optional[float]
    fib_ext_2000: Optional[float]

    # Swing reference
    swing_high: Optional[float]
    swing_low: Optional[float]

    # Round numbers near price
    round_numbers_near: tuple

    # Nearest levels
    nearest_level_above: Optional[float]
    nearest_level_below: Optional[float]

    reasons: tuple
    provenance: str = "REAL_LEVELS"

    def to_dict(self):
        def r(v):
            return round(v, 6) if v is not None else None
        return {
            "symbol": self.symbol,
            "current_price": self.current_price,
            "timestamp": self.timestamp,
            "pivot": {
                "pp": r(self.pivot_pp), "r1": r(self.pivot_r1),
                "r2": r(self.pivot_r2), "r3": r(self.pivot_r3),
                "s1": r(self.pivot_s1), "s2": r(self.pivot_s2),
                "s3": r(self.pivot_s3),
            },
            "fib_pivot": {
                "r1": r(self.fib_r1), "r2": r(self.fib_r2), "r3": r(self.fib_r3),
                "s1": r(self.fib_s1), "s2": r(self.fib_s2), "s3": r(self.fib_s3),
            },
            "camarilla": {
                "h3": r(self.cam_h3), "h4": r(self.cam_h4),
                "l3": r(self.cam_l3), "l4": r(self.cam_l4),
            },
            "previous": {
                "day_high": r(self.prev_day_high),
                "day_low": r(self.prev_day_low),
                "day_close": r(self.prev_day_close),
                "week_high": r(self.prev_week_high),
                "week_low": r(self.prev_week_low),
                "month_high": r(self.prev_month_high),
                "month_low": r(self.prev_month_low),
            },
            "sessions": {
                "asia": {"h": r(self.asia_high), "l": r(self.asia_low)},
                "london": {"h": r(self.london_high), "l": r(self.london_low)},
                "us": {"h": r(self.us_high), "l": r(self.us_low)},
            },
            "vwap": {
                "session": r(self.vwap_session),
                "daily": r(self.vwap_daily),
                "weekly": r(self.vwap_weekly),
                "upper_1": r(self.vwap_upper_1),
                "upper_2": r(self.vwap_upper_2),
                "lower_1": r(self.vwap_lower_1),
                "lower_2": r(self.vwap_lower_2),
            },
            "fibonacci": {
                "236": r(self.fib_236), "382": r(self.fib_382),
                "500": r(self.fib_500), "618": r(self.fib_618),
                "786": r(self.fib_786),
                "ext_1272": r(self.fib_ext_1272),
                "ext_1618": r(self.fib_ext_1618),
                "ext_2000": r(self.fib_ext_2000),
            },
            "swing": {
                "high": r(self.swing_high),
                "low": r(self.swing_low),
            },
            "round_numbers": list(self.round_numbers_near),
            "nearest": {
                "above": r(self.nearest_level_above),
                "below": r(self.nearest_level_below),
            },
            "reasons": list(self.reasons),
        }


# ============================================================
# HELPERS
# ============================================================

def _f(v, default=None):
    try:
        n = float(v)
        return n if isfinite(n) else default
    except (TypeError, ValueError):
        return default


def _classic_pivots(h, l, c):
    """Classic floor trader pivots."""
    pp = (h + l + c) / 3
    r1 = 2 * pp - l
    s1 = 2 * pp - h
    r2 = pp + (h - l)
    s2 = pp - (h - l)
    r3 = h + 2 * (pp - l)
    s3 = l - 2 * (h - pp)
    return pp, r1, r2, r3, s1, s2, s3


def _fib_pivots(h, l, c):
    """Fibonacci pivot points."""
    pp = (h + l + c) / 3
    rng = h - l
    r1 = pp + rng * 0.382
    r2 = pp + rng * 0.618
    r3 = pp + rng * 1.000
    s1 = pp - rng * 0.382
    s2 = pp - rng * 0.618
    s3 = pp - rng * 1.000
    return r1, r2, r3, s1, s2, s3


def _camarilla(h, l, c):
    """Camarilla pivots — used by intraday traders."""
    rng = h - l
    h3 = c + rng * 1.1 / 4
    h4 = c + rng * 1.1 / 2
    l3 = c - rng * 1.1 / 4
    l4 = c - rng * 1.1 / 2
    return h3, h4, l3, l4


def _vwap(candles):
    """Volume Weighted Average Price over given candles."""
    if not candles:
        return None, None, None, None, None, None, None
    total_v = 0.0
    total_vp = 0.0
    total_vp2 = 0.0
    for c in candles:
        typical = (c.high + c.low + c.close) / 3
        v = c.volume
        if v <= 0:
            continue
        total_v += v
        total_vp += typical * v
        total_vp2 += typical * typical * v

    if total_v <= 0:
        return None, None, None, None, None, None, None

    vwap_val = total_vp / total_v

    # Variance
    variance = (total_vp2 / total_v) - (vwap_val * vwap_val)
    if variance < 0:
        variance = 0
    std = variance ** 0.5

    upper_1 = vwap_val + std
    upper_2 = vwap_val + 2 * std
    lower_1 = vwap_val - std
    lower_2 = vwap_val - 2 * std

    return vwap_val, upper_1, upper_2, lower_1, lower_2, std, None


def _session_candles(candles, start_utc_hour, end_utc_hour):
    """Extract candles in UTC hour range [start, end)."""
    result = []
    for c in candles:
        try:
            dt = datetime.fromtimestamp(c.time, tz=timezone.utc)
        except Exception:
            continue
        h = dt.hour
        if start_utc_hour <= h < end_utc_hour:
            result.append(c)
    return result


def _prev_day(candles):
    """Get previous calendar day's candles (UTC)."""
    if not candles:
        return []
    today = datetime.now(timezone.utc).date()
    yesterday = today - timedelta(days=1)
    result = []
    for c in candles:
        try:
            d = datetime.fromtimestamp(c.time, tz=timezone.utc).date()
        except Exception:
            continue
        if d == yesterday:
            result.append(c)
    return result


def _prev_week(candles):
    """Get last week's candles."""
    if not candles:
        return []
    now = datetime.now(timezone.utc)
    week_start = (now - timedelta(days=now.weekday() + 7)).date()
    week_end = week_start + timedelta(days=7)
    result = []
    for c in candles:
        try:
            d = datetime.fromtimestamp(c.time, tz=timezone.utc).date()
        except Exception:
            continue
        if week_start <= d < week_end:
            result.append(c)
    return result


def _prev_month(candles):
    """Get last month's candles."""
    if not candles:
        return []
    now = datetime.now(timezone.utc)
    if now.month == 1:
        m, y = 12, now.year - 1
    else:
        m, y = now.month - 1, now.year
    result = []
    for c in candles:
        try:
            dt = datetime.fromtimestamp(c.time, tz=timezone.utc)
        except Exception:
            continue
        if dt.year == y and dt.month == m:
            result.append(c)
    return result


def _hl(candles):
    if not candles:
        return None, None
    return (
        max(c.high for c in candles),
        min(c.low for c in candles),
    )


def _swing_ref(candles, lookback=20):
    """Find most recent significant swing high and low."""
    if len(candles) < lookback:
        return None, None
    recent = candles[-lookback:]
    hi = max(recent, key=lambda c: c.high)
    lo = min(recent, key=lambda c: c.low)
    return hi.high, lo.low


def _round_numbers_near(price, count=6, min_distance_pct=0.1):
    """Round numbers within reasonable distance."""
    if price <= 0:
        return ()
    levels = set()
    # Determine magnitude
    magnitude = 10 ** (len(str(int(price))) - 1)
    for mult in (magnitude, magnitude // 2, magnitude // 5, magnitude // 10):
        if mult <= 0:
            continue
        base = int(price / mult) * mult
        for offset in range(-3, 4):
            lvl = base + offset * mult
            if lvl > 0:
                dist_pct = abs(lvl - price) / price * 100
                if dist_pct <= 2.0:
                    levels.add(round(lvl, 4))
    return tuple(sorted(levels))


# ============================================================
# ENGINE
# ============================================================

class LevelsEngine:

    def compute(self, symbol: str) -> LevelsSnapshot:

        now = datetime.now(timezone.utc)
        md = get_real_market_data()

        # Load candles at multiple TFs
        # 1m for VWAP + sessions
        candles_1m, _ = md.get_candles(symbol, "1", 500)
        # 1h for pivots + prev day
        candles_1h, _ = md.get_candles(symbol, "60", 500)
        # daily for prev week/month
        candles_1d, _ = md.get_candles(symbol, "D", 100)

        if not candles_1m and not candles_1h:
            return self._empty(symbol, now)

        current_price = (
            candles_1m[-1].close if candles_1m
            else (candles_1h[-1].close if candles_1h else 0.0)
        )
        reasons = []

        # ---- Pivot Points from prev day (1h candles → group) ----
        prev_day_candles = _prev_day(candles_1h) if candles_1h else []
        if prev_day_candles:
            dh, dl = _hl(prev_day_candles)
            dc = prev_day_candles[-1].close
        elif len(candles_1h) >= 24:
            # Use last 24 hourly candles
            dh, dl = _hl(candles_1h[-24:])
            dc = candles_1h[-1].close
        else:
            dh = dl = dc = None

        pp = r1 = r2 = r3 = s1 = s2 = s3 = None
        fib_r1 = fib_r2 = fib_r3 = fib_s1 = fib_s2 = fib_s3 = None
        cam_h3 = cam_h4 = cam_l3 = cam_l4 = None

        if dh and dl and dc:
            pp, r1, r2, r3, s1, s2, s3 = _classic_pivots(dh, dl, dc)
            fib_r1, fib_r2, fib_r3, fib_s1, fib_s2, fib_s3 = _fib_pivots(dh, dl, dc)
            cam_h3, cam_h4, cam_l3, cam_l4 = _camarilla(dh, dl, dc)
            reasons.append(f"Pivots computed from prev session H={dh:.2f} L={dl:.2f}")

        # ---- Previous periods ----
        pd_high = pd_low = pd_close = None
        if prev_day_candles:
            pd_high, pd_low = _hl(prev_day_candles)
            pd_close = prev_day_candles[-1].close

        pw_high = pw_low = None
        prev_week = _prev_week(candles_1d) if candles_1d else []
        if prev_week:
            pw_high, pw_low = _hl(prev_week)

        pm_high = pm_low = None
        prev_month = _prev_month(candles_1d) if candles_1d else []
        if prev_month:
            pm_high, pm_low = _hl(prev_month)

        # ---- Session levels ----
        # Asia: 00-08 UTC, London: 08-16, US: 13-22
        asia_h = asia_l = london_h = london_l = us_h = us_l = None
        if candles_1m:
            asia = _session_candles(candles_1m, 0, 8)
            london = _session_candles(candles_1m, 8, 16)
            us = _session_candles(candles_1m, 13, 22)
            if asia:
                asia_h, asia_l = _hl(asia)
            if london:
                london_h, london_l = _hl(london)
            if us:
                us_h, us_l = _hl(us)

        # ---- VWAP ----
        vwap_sess = vwap_d = vwap_w = None
        vwap_u1 = vwap_u2 = vwap_l1 = vwap_l2 = None

        if candles_1m:
            # Daily VWAP = today's candles
            today = datetime.now(timezone.utc).date()
            today_candles = [
                c for c in candles_1m
                if datetime.fromtimestamp(c.time, tz=timezone.utc).date() == today
            ]
            if today_candles:
                vwap_d, vwap_u1, vwap_u2, vwap_l1, vwap_l2, _, _ = _vwap(today_candles)
                vwap_sess = vwap_d

        if candles_1h:
            # Weekly VWAP
            vwap_w, _, _, _, _, _, _ = _vwap(candles_1h[-168:])

        # ---- Fibonacci from last swing ----
        swing_h = swing_l = None
        fib_236 = fib_382 = fib_500 = fib_618 = fib_786 = None
        fib_e1272 = fib_e1618 = fib_e2000 = None

        if candles_1h and len(candles_1h) >= 50:
            swing_h, swing_l = _swing_ref(candles_1h, lookback=50)
            if swing_h and swing_l and swing_h > swing_l:
                rng = swing_h - swing_l
                fib_236 = swing_h - rng * 0.236
                fib_382 = swing_h - rng * 0.382
                fib_500 = swing_h - rng * 0.500
                fib_618 = swing_h - rng * 0.618
                fib_786 = swing_h - rng * 0.786
                fib_e1272 = swing_h + rng * 0.272
                fib_e1618 = swing_h + rng * 0.618
                fib_e2000 = swing_h + rng * 1.0

        # ---- Round numbers ----
        round_near = _round_numbers_near(current_price)

        # ---- Nearest ----
        all_above = []
        all_below = []
        candidates = [
            r1, r2, r3, s1, s2, s3,
            fib_r1, fib_r2, fib_s1, fib_s2,
            cam_h3, cam_h4, cam_l3, cam_l4,
            pd_high, pd_low, pw_high, pw_low, pm_high, pm_low,
            asia_h, asia_l, london_h, london_l, us_h, us_l,
            vwap_d, vwap_u1, vwap_u2, vwap_l1, vwap_l2,
            fib_236, fib_382, fib_500, fib_618, fib_786,
        ]
        for lvl in candidates:
            if lvl is None or lvl <= 0:
                continue
            if lvl > current_price:
                all_above.append(lvl)
            elif lvl < current_price:
                all_below.append(lvl)

        nearest_above = min(all_above) if all_above else None
        nearest_below = max(all_below) if all_below else None

        return LevelsSnapshot(
            symbol=symbol,
            current_price=round(current_price, 6),
            timestamp=now.isoformat(),
            pivot_pp=_f(pp), pivot_r1=_f(r1), pivot_r2=_f(r2), pivot_r3=_f(r3),
            pivot_s1=_f(s1), pivot_s2=_f(s2), pivot_s3=_f(s3),
            fib_r1=_f(fib_r1), fib_r2=_f(fib_r2), fib_r3=_f(fib_r3),
            fib_s1=_f(fib_s1), fib_s2=_f(fib_s2), fib_s3=_f(fib_s3),
            cam_h3=_f(cam_h3), cam_h4=_f(cam_h4),
            cam_l3=_f(cam_l3), cam_l4=_f(cam_l4),
            prev_day_high=_f(pd_high), prev_day_low=_f(pd_low),
            prev_day_close=_f(pd_close),
            prev_week_high=_f(pw_high), prev_week_low=_f(pw_low),
            prev_month_high=_f(pm_high), prev_month_low=_f(pm_low),
            asia_high=_f(asia_h), asia_low=_f(asia_l),
            london_high=_f(london_h), london_low=_f(london_l),
            us_high=_f(us_h), us_low=_f(us_l),
            vwap_session=_f(vwap_sess), vwap_daily=_f(vwap_d),
            vwap_weekly=_f(vwap_w),
            vwap_upper_1=_f(vwap_u1), vwap_upper_2=_f(vwap_u2),
            vwap_lower_1=_f(vwap_l1), vwap_lower_2=_f(vwap_l2),
            fib_236=_f(fib_236), fib_382=_f(fib_382),
            fib_500=_f(fib_500), fib_618=_f(fib_618),
            fib_786=_f(fib_786),
            fib_ext_1272=_f(fib_e1272),
            fib_ext_1618=_f(fib_e1618),
            fib_ext_2000=_f(fib_e2000),
            swing_high=_f(swing_h), swing_low=_f(swing_l),
            round_numbers_near=round_near,
            nearest_level_above=_f(nearest_above),
            nearest_level_below=_f(nearest_below),
            reasons=tuple(reasons),
        )

    def _empty(self, symbol, now):
        return LevelsSnapshot(
            symbol=symbol, current_price=0.0, timestamp=now.isoformat(),
            pivot_pp=None, pivot_r1=None, pivot_r2=None, pivot_r3=None,
            pivot_s1=None, pivot_s2=None, pivot_s3=None,
            fib_r1=None, fib_r2=None, fib_r3=None,
            fib_s1=None, fib_s2=None, fib_s3=None,
            cam_h3=None, cam_h4=None, cam_l3=None, cam_l4=None,
            prev_day_high=None, prev_day_low=None, prev_day_close=None,
            prev_week_high=None, prev_week_low=None,
            prev_month_high=None, prev_month_low=None,
            asia_high=None, asia_low=None,
            london_high=None, london_low=None,
            us_high=None, us_low=None,
            vwap_session=None, vwap_daily=None, vwap_weekly=None,
            vwap_upper_1=None, vwap_upper_2=None,
            vwap_lower_1=None, vwap_lower_2=None,
            fib_236=None, fib_382=None, fib_500=None,
            fib_618=None, fib_786=None,
            fib_ext_1272=None, fib_ext_1618=None, fib_ext_2000=None,
            swing_high=None, swing_low=None,
            round_numbers_near=(),
            nearest_level_above=None, nearest_level_below=None,
            reasons=("NO_CANDLES",),
        )


_engine: Optional[LevelsEngine] = None
_lock = None


def get_levels_engine() -> LevelsEngine:
    global _engine, _lock
    if _lock is None:
        from threading import RLock
        _lock = RLock()
    with _lock:
        if _engine is None:
            _engine = LevelsEngine()
        return _engine


__all__ = [
    "LevelsSnapshot",
    "LevelsEngine",
    "get_levels_engine",
]
