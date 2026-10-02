"""Install volume_engine.py — Cumulative delta + whale buckets + taker flow"""
from pathlib import Path

ROOT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\intelligence\real")

FILE = '''"""
ROBOMLM_PLUS - Volume Engine

Real volume intelligence:

    - Cumulative Delta (buy volume - sell volume) at multiple windows
    - Taker buy/sell ratio (aggressive flow)
    - Trade size buckets (retail vs whale)
    - Volume acceleration (recent vs baseline)
    - Rate of Change (ROC) at multiple windows
    - Volume profile (POC, VAH, VAL)
    - Delta divergence (price up but delta down = bearish)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from math import isfinite
from typing import Optional, Sequence

from app.intelligence.real.real_market_data import (
    get_real_market_data,
    Candle,
    RecentTrade,
)


@dataclass(frozen=True)
class TradeBucket:
    label: str
    min_usd: float
    max_usd: Optional[float]
    buy_volume: float
    sell_volume: float
    trade_count: int

    @property
    def net_volume(self) -> float:
        return self.buy_volume - self.sell_volume

    def to_dict(self):
        return {
            "label": self.label,
            "min_usd": self.min_usd,
            "max_usd": self.max_usd,
            "buy_volume": round(self.buy_volume, 4),
            "sell_volume": round(self.sell_volume, 4),
            "net_volume": round(self.net_volume, 4),
            "trade_count": self.trade_count,
        }


@dataclass(frozen=True)
class VolumeSnapshot:
    symbol: str
    timestamp: str

    # Cumulative delta over time windows
    delta_1m: Optional[float]           # last 1 min net (buy-sell)
    delta_5m: Optional[float]
    delta_15m: Optional[float]
    delta_1h: Optional[float]
    delta_trend: str                    # ACCELERATING | DECELERATING | STABLE | REVERSING

    # Taker ratio
    taker_buy_ratio: float              # buy_vol / total_vol
    taker_interpretation: str           # AGGRESSIVE_BUY | AGGRESSIVE_SELL | BALANCED

    # Whale vs retail
    buckets: tuple                      # tuple[TradeBucket]
    whale_net_usd: Optional[float]      # net whale flow (buy-sell) in USD
    whale_direction: str                # BUYING | SELLING | NEUTRAL
    retail_direction: str               # BUYING | SELLING | NEUTRAL
    smart_money_signal: str             # FOLLOW_WHALES | FADE_WHALES | NEUTRAL

    # Volume acceleration
    vol_recent_avg: float               # last 5 candles
    vol_baseline_avg: float             # prev 20 candles
    volume_ratio: float                 # recent / baseline
    volume_state: str                   # EXPANDING | CONTRACTING | NORMAL

    # Rate of change
    roc_1m: Optional[float]             # % price change
    roc_5m: Optional[float]
    roc_15m: Optional[float]
    roc_1h: Optional[float]
    roc_acceleration: Optional[float]   # 2nd derivative
    roc_signal: str                     # ACCELERATING_UP | ACCELERATING_DOWN | DECELERATING | STABLE

    # Delta divergence
    delta_divergence: bool
    divergence_type: str                # BULLISH | BEARISH | NONE

    # Volume profile (from candles)
    volume_poc: Optional[float]
    volume_vah: Optional[float]
    volume_val: Optional[float]

    # Verdict
    volume_direction: str               # BULLISH | BEARISH | NEUTRAL
    volume_strength: float              # 0-100
    reasons: tuple

    provenance: str = "REAL_VOLUME"

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp,
            "delta": {
                "1m": self.delta_1m,
                "5m": self.delta_5m,
                "15m": self.delta_15m,
                "1h": self.delta_1h,
                "trend": self.delta_trend,
            },
            "taker": {
                "buy_ratio": self.taker_buy_ratio,
                "interpretation": self.taker_interpretation,
            },
            "buckets": [b.to_dict() for b in self.buckets],
            "whales": {
                "net_usd": self.whale_net_usd,
                "direction": self.whale_direction,
                "retail_direction": self.retail_direction,
                "smart_money": self.smart_money_signal,
            },
            "volume": {
                "recent_avg": self.vol_recent_avg,
                "baseline_avg": self.vol_baseline_avg,
                "ratio": self.volume_ratio,
                "state": self.volume_state,
            },
            "roc": {
                "1m": self.roc_1m,
                "5m": self.roc_5m,
                "15m": self.roc_15m,
                "1h": self.roc_1h,
                "acceleration": self.roc_acceleration,
                "signal": self.roc_signal,
            },
            "divergence": {
                "detected": self.delta_divergence,
                "type": self.divergence_type,
            },
            "volume_profile": {
                "poc": self.volume_poc,
                "vah": self.volume_vah,
                "val": self.volume_val,
            },
            "verdict": {
                "direction": self.volume_direction,
                "strength": self.volume_strength,
                "reasons": list(self.reasons),
            },
        }


def _f(v, default=None):
    try:
        n = float(v)
        return n if isfinite(n) else default
    except (TypeError, ValueError):
        return default


def _volume_profile(candles, bins=30):
    if not candles:
        return None, None, None
    lows = [c.low for c in candles]
    highs = [c.high for c in candles]
    p_min = min(lows)
    p_max = max(highs)
    if p_max <= p_min:
        return None, None, None
    bucket_size = (p_max - p_min) / bins
    buckets = [0.0] * bins
    for c in candles:
        low_idx = max(0, min(bins - 1, int((c.low - p_min) / bucket_size)))
        high_idx = max(0, min(bins - 1, int((c.high - p_min) / bucket_size)))
        span = high_idx - low_idx + 1
        share = c.volume / span if span > 0 else 0
        for idx in range(low_idx, high_idx + 1):
            buckets[idx] += share
    total = sum(buckets)
    if total <= 0:
        return None, None, None
    poc_idx = buckets.index(max(buckets))
    poc = p_min + (poc_idx + 0.5) * bucket_size
    sorted_idx = sorted(range(bins), key=lambda i: buckets[i], reverse=True)
    cumulative = 0
    va_idx = []
    target = total * 0.70
    for i in sorted_idx:
        cumulative += buckets[i]
        va_idx.append(i)
        if cumulative >= target:
            break
    vah = p_min + (max(va_idx) + 1) * bucket_size
    val = p_min + min(va_idx) * bucket_size
    return round(poc, 6), round(vah, 6), round(val, 6)


class VolumeEngine:

    def compute(self, symbol: str) -> VolumeSnapshot:

        now = datetime.now(timezone.utc)
        md = get_real_market_data()
        reasons = []

        # Load candles at 1m for ROC/delta
        candles_1m, _ = md.get_candles(symbol, "1", 200)
        if not candles_1m or len(candles_1m) < 30:
            return self._empty(symbol, now, "INSUFFICIENT_CANDLES")

        # Get fresh trades (up to 500)
        trades, _ = md.get_recent_trades(symbol, limit=500)

        current_price = candles_1m[-1].close
        now_sec = int(now.timestamp())

        # ------------------------------------------------------
        # 1. CUMULATIVE DELTA
        # ------------------------------------------------------
        def delta_window(seconds):
            cutoff = now_sec - seconds
            buy = sell = 0.0
            for t in trades:
                if t.time < cutoff:
                    continue
                if t.side == "Buy":
                    buy += t.size
                elif t.side == "Sell":
                    sell += t.size
            return buy - sell, buy + sell

        delta_1m, total_1m = delta_window(60)
        delta_5m, total_5m = delta_window(300)
        delta_15m, total_15m = delta_window(900)
        delta_1h, total_1h = delta_window(3600)

        # Delta trend: compare consecutive windows
        # If short delta > long delta directionally → accelerating
        if delta_1m > 0 and delta_5m > 0 and delta_15m > 0:
            delta_trend = "ACCELERATING_UP"
            reasons.append(f"Delta positive across windows (1m={delta_1m:.2f} 5m={delta_5m:.2f})")
        elif delta_1m < 0 and delta_5m < 0 and delta_15m < 0:
            delta_trend = "ACCELERATING_DOWN"
            reasons.append(f"Delta negative across windows (1m={delta_1m:.2f} 5m={delta_5m:.2f})")
        elif (delta_1m > 0) != (delta_5m > 0):
            delta_trend = "REVERSING"
            reasons.append("Delta reversing — short vs long window differ")
        else:
            delta_trend = "STABLE"

        # ------------------------------------------------------
        # 2. TAKER RATIO (aggressive buy flow)
        # ------------------------------------------------------
        total_buy = sum(t.size for t in trades if t.side == "Buy")
        total_sell = sum(t.size for t in trades if t.side == "Sell")
        total_vol = total_buy + total_sell
        taker_buy_ratio = (total_buy / total_vol) if total_vol > 0 else 0.5

        if taker_buy_ratio > 0.60:
            taker_interp = "AGGRESSIVE_BUY"
        elif taker_buy_ratio < 0.40:
            taker_interp = "AGGRESSIVE_SELL"
        else:
            taker_interp = "BALANCED"

        # ------------------------------------------------------
        # 3. TRADE SIZE BUCKETS
        # ------------------------------------------------------
        buckets_def = [
            ("RETAIL", 0.0, 1_000.0),
            ("SMALL", 1_000.0, 10_000.0),
            ("MEDIUM", 10_000.0, 50_000.0),
            ("LARGE", 50_000.0, 500_000.0),
            ("WHALE", 500_000.0, None),
        ]

        bucket_accum = {label: {"buy": 0.0, "sell": 0.0, "count": 0}
                        for label, _, _ in buckets_def}

        for t in trades:
            usd = t.price * t.size
            for label, lo, hi in buckets_def:
                if usd >= lo and (hi is None or usd < hi):
                    if t.side == "Buy":
                        bucket_accum[label]["buy"] += t.size
                    elif t.side == "Sell":
                        bucket_accum[label]["sell"] += t.size
                    bucket_accum[label]["count"] += 1
                    break

        buckets = tuple(
            TradeBucket(
                label=label,
                min_usd=lo,
                max_usd=hi,
                buy_volume=bucket_accum[label]["buy"],
                sell_volume=bucket_accum[label]["sell"],
                trade_count=bucket_accum[label]["count"],
            )
            for label, lo, hi in buckets_def
        )

        # Whale net flow (in USD roughly)
        whale_buy = bucket_accum["WHALE"]["buy"] + bucket_accum["LARGE"]["buy"]
        whale_sell = bucket_accum["WHALE"]["sell"] + bucket_accum["LARGE"]["sell"]
        whale_net = (whale_buy - whale_sell) * current_price

        retail_buy = bucket_accum["RETAIL"]["buy"] + bucket_accum["SMALL"]["buy"]
        retail_sell = bucket_accum["RETAIL"]["sell"] + bucket_accum["SMALL"]["sell"]
        retail_net = retail_buy - retail_sell

        if whale_net > 0:
            whale_dir = "BUYING"
        elif whale_net < 0:
            whale_dir = "SELLING"
        else:
            whale_dir = "NEUTRAL"

        if retail_net > 0:
            retail_dir = "BUYING"
        elif retail_net < 0:
            retail_dir = "SELLING"
        else:
            retail_dir = "NEUTRAL"

        # Smart money: if whales and retail diverge → follow whales
        if whale_dir == "BUYING" and retail_dir == "SELLING":
            smart_signal = "FOLLOW_WHALES_BULL"
            reasons.append("Whales buying while retail selling → bullish")
        elif whale_dir == "SELLING" and retail_dir == "BUYING":
            smart_signal = "FOLLOW_WHALES_BEAR"
            reasons.append("Whales selling while retail buying → bearish")
        else:
            smart_signal = "NEUTRAL"

        # ------------------------------------------------------
        # 4. VOLUME ACCELERATION
        # ------------------------------------------------------
        vols = [c.volume for c in candles_1m]
        vol_recent = sum(vols[-5:]) / 5
        vol_baseline = sum(vols[-25:-5]) / 20 if len(vols) >= 25 else vol_recent
        volume_ratio = (vol_recent / vol_baseline) if vol_baseline > 0 else 1.0

        if volume_ratio > 1.5:
            volume_state = "EXPANDING"
        elif volume_ratio < 0.7:
            volume_state = "CONTRACTING"
        else:
            volume_state = "NORMAL"

        # ------------------------------------------------------
        # 5. RATE OF CHANGE
        # ------------------------------------------------------
        def roc(minutes):
            if len(candles_1m) < minutes + 1:
                return None
            old = candles_1m[-minutes - 1].close
            new = candles_1m[-1].close
            if old <= 0:
                return None
            return (new - old) / old * 100

        roc_1m = roc(1)
        roc_5m = roc(5)
        roc_15m = roc(15)
        roc_1h = roc(60)

        # ROC acceleration: (1m - 5m/5) * 5 = rough 2nd derivative
        roc_acc = None
        if roc_1m is not None and roc_5m is not None:
            roc_acc = roc_1m - (roc_5m / 5)

        if roc_1m is not None and roc_5m is not None and roc_15m is not None:
            if roc_1m > 0 and roc_5m > 0 and roc_15m > 0 and roc_acc and roc_acc > 0:
                roc_signal = "ACCELERATING_UP"
            elif roc_1m < 0 and roc_5m < 0 and roc_15m < 0 and roc_acc and roc_acc < 0:
                roc_signal = "ACCELERATING_DOWN"
            elif (roc_1m > 0) != (roc_5m > 0):
                roc_signal = "DECELERATING"
            else:
                roc_signal = "STABLE"
        else:
            roc_signal = "STABLE"

        # ------------------------------------------------------
        # 6. DELTA DIVERGENCE
        # ------------------------------------------------------
        # If price up but delta negative → bearish divergence (bulls losing steam)
        # If price down but delta positive → bullish divergence (bears losing steam)
        divergence = False
        div_type = "NONE"

        if roc_5m is not None and delta_5m != 0:
            if roc_5m > 0.1 and delta_5m < 0:
                divergence = True
                div_type = "BEARISH"
                reasons.append("Price rising but delta negative → bearish divergence")
            elif roc_5m < -0.1 and delta_5m > 0:
                divergence = True
                div_type = "BULLISH"
                reasons.append("Price falling but delta positive → bullish divergence")

        # ------------------------------------------------------
        # 7. VOLUME PROFILE
        # ------------------------------------------------------
        poc, vah, val = _volume_profile(candles_1m, bins=30)

        # ------------------------------------------------------
        # 8. VERDICT
        # ------------------------------------------------------
        bull = 0.0
        bear = 0.0

        # Delta trend
        if delta_trend == "ACCELERATING_UP":
            bull += 25
        elif delta_trend == "ACCELERATING_DOWN":
            bear += 25
        elif delta_trend == "REVERSING":
            # Short window predicts future direction
            if delta_1m > 0:
                bull += 10
            else:
                bear += 10

        # Taker
        if taker_interp == "AGGRESSIVE_BUY":
            bull += 20
        elif taker_interp == "AGGRESSIVE_SELL":
            bear += 20

        # Whales
        if smart_signal == "FOLLOW_WHALES_BULL":
            bull += 25
        elif smart_signal == "FOLLOW_WHALES_BEAR":
            bear += 25

        # Volume expansion
        if volume_state == "EXPANDING":
            if roc_5m is not None and roc_5m > 0:
                bull += 15
            elif roc_5m is not None and roc_5m < 0:
                bear += 15

        # ROC
        if roc_signal == "ACCELERATING_UP":
            bull += 15
        elif roc_signal == "ACCELERATING_DOWN":
            bear += 15

        # Divergence
        if div_type == "BULLISH":
            bull += 20
        elif div_type == "BEARISH":
            bear += 20

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

        return VolumeSnapshot(
            symbol=symbol,
            timestamp=now.isoformat(),
            delta_1m=round(delta_1m, 6) if delta_1m else 0.0,
            delta_5m=round(delta_5m, 6),
            delta_15m=round(delta_15m, 6),
            delta_1h=round(delta_1h, 6),
            delta_trend=delta_trend,
            taker_buy_ratio=round(taker_buy_ratio, 4),
            taker_interpretation=taker_interp,
            buckets=buckets,
            whale_net_usd=round(whale_net, 2),
            whale_direction=whale_dir,
            retail_direction=retail_dir,
            smart_money_signal=smart_signal,
            vol_recent_avg=round(vol_recent, 6),
            vol_baseline_avg=round(vol_baseline, 6),
            volume_ratio=round(volume_ratio, 4),
            volume_state=volume_state,
            roc_1m=round(roc_1m, 4) if roc_1m is not None else None,
            roc_5m=round(roc_5m, 4) if roc_5m is not None else None,
            roc_15m=round(roc_15m, 4) if roc_15m is not None else None,
            roc_1h=round(roc_1h, 4) if roc_1h is not None else None,
            roc_acceleration=round(roc_acc, 6) if roc_acc is not None else None,
            roc_signal=roc_signal,
            delta_divergence=divergence,
            divergence_type=div_type,
            volume_poc=poc,
            volume_vah=vah,
            volume_val=val,
            volume_direction=direction,
            volume_strength=strength,
            reasons=tuple(reasons),
        )

    def _empty(self, symbol, now, reason):
        return VolumeSnapshot(
            symbol=symbol, timestamp=now.isoformat(),
            delta_1m=None, delta_5m=None, delta_15m=None, delta_1h=None,
            delta_trend="STABLE",
            taker_buy_ratio=0.5, taker_interpretation="BALANCED",
            buckets=(), whale_net_usd=None,
            whale_direction="NEUTRAL", retail_direction="NEUTRAL",
            smart_money_signal="NEUTRAL",
            vol_recent_avg=0.0, vol_baseline_avg=0.0,
            volume_ratio=1.0, volume_state="NORMAL",
            roc_1m=None, roc_5m=None, roc_15m=None, roc_1h=None,
            roc_acceleration=None, roc_signal="STABLE",
            delta_divergence=False, divergence_type="NONE",
            volume_poc=None, volume_vah=None, volume_val=None,
            volume_direction="NEUTRAL", volume_strength=0.0,
            reasons=(reason,),
        )


_engine: Optional[VolumeEngine] = None
_lock = None


def get_volume_engine() -> VolumeEngine:
    global _engine, _lock
    if _lock is None:
        from threading import RLock
        _lock = RLock()
    with _lock:
        if _engine is None:
            _engine = VolumeEngine()
        return _engine


__all__ = [
    "TradeBucket",
    "VolumeSnapshot",
    "VolumeEngine",
    "get_volume_engine",
]
'''

(ROOT / "volume_engine.py").write_text(FILE, encoding="utf-8")
print(f"WROTE: {ROOT / 'volume_engine.py'}")
print()
print("Test:")
print('  python -c "from app.intelligence.real.volume_engine import get_volume_engine; v = get_volume_engine().compute(\\"BTC/USDT\\"); print(\\"delta 1m/5m/15m/1h:\\", v.delta_1m, v.delta_5m, v.delta_15m, v.delta_1h); print(\\"delta trend:\\", v.delta_trend); print(\\"taker ratio:\\", v.taker_buy_ratio, v.taker_interpretation); print(\\"whale net USD:\\", v.whale_net_usd, v.whale_direction); print(\\"smart money:\\", v.smart_money_signal); print(\\"vol ratio:\\", v.volume_ratio, v.volume_state); print(\\"roc 1m/5m/15m:\\", v.roc_1m, v.roc_5m, v.roc_15m); print(\\"divergence:\\", v.delta_divergence, v.divergence_type); print(\\"verdict:\\", v.volume_direction, v.volume_strength); [print(\\"  -\\", r) for r in v.reasons]"')