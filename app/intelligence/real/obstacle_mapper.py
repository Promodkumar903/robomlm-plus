"""
ROBOMLM_PLUS - Obstacle Mapper

Maps ALL price levels where orders are likely concentrated.
Combines:

  Layer A: Static levels (Day HL, Prev close, Round numbers)
  Layer B: Structure (Swing highs/lows)
  Layer C: SMC (FVG, BOS, CHOCH, Order Blocks, Demand/Supply)
  Layer D: Volume profile (POC, VAH, VAL)
  Layer E: SL cluster inference

No hardcoding. All values from real candles.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from math import isfinite
from typing import Optional, Sequence

from app.intelligence.real.real_market_data import Candle


# ============================================================
# TYPES
# ============================================================

class ObstacleKind(str, Enum):
    DAY_HIGH = "DAY_HIGH"
    DAY_LOW = "DAY_LOW"
    PREV_CLOSE = "PREV_CLOSE"
    ROUND_NUMBER = "ROUND_NUMBER"

    SWING_HIGH = "SWING_HIGH"
    SWING_LOW = "SWING_LOW"

    FVG_BULL = "FVG_BULL"
    FVG_BEAR = "FVG_BEAR"

    BOS_BULL = "BOS_BULL"
    BOS_BEAR = "BOS_BEAR"

    CHOCH_BULL = "CHOCH_BULL"
    CHOCH_BEAR = "CHOCH_BEAR"

    ORDER_BLOCK_BULL = "ORDER_BLOCK_BULL"
    ORDER_BLOCK_BEAR = "ORDER_BLOCK_BEAR"

    DEMAND_ZONE = "DEMAND_ZONE"
    SUPPLY_ZONE = "SUPPLY_ZONE"

    VOLUME_POC = "VOLUME_POC"
    VOLUME_VAH = "VOLUME_VAH"
    VOLUME_VAL = "VOLUME_VAL"

    SL_CLUSTER_ABOVE = "SL_CLUSTER_ABOVE"
    SL_CLUSTER_BELOW = "SL_CLUSTER_BELOW"


class ObstacleSide(str, Enum):
    ABOVE = "ABOVE"   # resistance
    BELOW = "BELOW"   # support


@dataclass(frozen=True)
class Obstacle:
    kind: str
    side: str
    price: float
    strength: float            # 0-100
    distance_pct: float        # % from current price
    touches: int = 0
    metadata: dict = field(default_factory=dict)

    def to_dict(self):
        return {
            "kind": self.kind,
            "side": self.side,
            "price": self.price,
            "strength": self.strength,
            "distance_pct": self.distance_pct,
            "touches": self.touches,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class ObstacleMap:
    symbol: str
    current_price: float

    above: tuple           # tuple[Obstacle]
    below: tuple

    nearest_resistance: Optional[Obstacle]
    nearest_support: Optional[Obstacle]

    day_high: Optional[float]
    day_low: Optional[float]
    day_range_pct: Optional[float]

    bos_detected: bool
    choch_detected: bool

    fvg_count: int
    order_block_count: int
    demand_supply_count: int

    candle_count: int
    provenance: str
    computed_at: datetime

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "current_price": self.current_price,
            "above": [o.to_dict() for o in self.above],
            "below": [o.to_dict() for o in self.below],
            "nearest_resistance": (
                self.nearest_resistance.to_dict()
                if self.nearest_resistance else None
            ),
            "nearest_support": (
                self.nearest_support.to_dict()
                if self.nearest_support else None
            ),
            "day_high": self.day_high,
            "day_low": self.day_low,
            "day_range_pct": self.day_range_pct,
            "bos_detected": self.bos_detected,
            "choch_detected": self.choch_detected,
            "fvg_count": self.fvg_count,
            "order_block_count": self.order_block_count,
            "demand_supply_count": self.demand_supply_count,
            "candle_count": self.candle_count,
            "provenance": self.provenance,
            "computed_at": self.computed_at.isoformat(),
        }


# ============================================================
# MATH PRIMITIVES
# ============================================================

def _finite(v):
    try:
        n = float(v)
        return n if isfinite(n) else None
    except (TypeError, ValueError):
        return None


def _detect_swings(candles, lookback=3):
    highs = []
    lows = []
    if len(candles) < lookback * 2 + 1:
        return highs, lows
    for i in range(lookback, len(candles) - lookback):
        window = candles[i - lookback : i + lookback + 1]
        h_i = candles[i].high
        l_i = candles[i].low
        if h_i == max(c.high for c in window):
            highs.append((i, h_i))
        if l_i == min(c.low for c in window):
            lows.append((i, l_i))
    return highs, lows


def _round_number_levels(price, spread_pct=5.0):
    """Generate round-number levels near current price."""
    levels = []
    if price <= 0:
        return levels
    # Magnitude of round number
    magnitude = 10 ** (len(str(int(price))) - 1)
    # 1000 for prices ~10k, 100 for ~1k, etc.
    for multiplier in (1000, 500, 100, 50, 10):
        step = multiplier
        if step >= price * 0.001:
            low = price * (1 - spread_pct / 100)
            high = price * (1 + spread_pct / 100)
            base = int(low / step) * step
            while base <= high:
                if base > 0:
                    levels.append(base)
                base += step
    return sorted(set(levels))


def _compute_atr(candles, period=14):
    if len(candles) < period + 1:
        return None
    trs = []
    for i in range(1, len(candles)):
        trs.append(max(
            candles[i].high - candles[i].low,
            abs(candles[i].high - candles[i - 1].close),
            abs(candles[i].low - candles[i - 1].close),
        ))
    atr = sum(trs[:period]) / period
    for i in range(period, len(trs)):
        atr = (atr * (period - 1) + trs[i]) / period
    return atr


def _volume_profile(candles, bins=30):
    """Simple volume profile by price bucket."""
    if not candles:
        return None, None, None
    prices = [c.close for c in candles]
    lows = [c.low for c in candles]
    highs = [c.high for c in candles]
    p_min = min(lows)
    p_max = max(highs)
    if p_max <= p_min:
        return None, None, None
    bucket_size = (p_max - p_min) / bins
    buckets = [0.0] * bins
    for c in candles:
        # allocate volume to bucket(s) covering candle range
        low_idx = int((c.low - p_min) / bucket_size)
        high_idx = int((c.high - p_min) / bucket_size)
        low_idx = max(0, min(bins - 1, low_idx))
        high_idx = max(0, min(bins - 1, high_idx))
        span = high_idx - low_idx + 1
        share = c.volume / span if span > 0 else 0
        for idx in range(low_idx, high_idx + 1):
            buckets[idx] += share

    total = sum(buckets)
    if total <= 0:
        return None, None, None

    # POC = bucket with max volume
    poc_idx = buckets.index(max(buckets))
    poc_price = p_min + (poc_idx + 0.5) * bucket_size

    # Value area (70% of total volume)
    sorted_idx = sorted(range(bins), key=lambda i: buckets[i], reverse=True)
    cumulative = 0
    va_idx = []
    target = total * 0.70
    for i in sorted_idx:
        cumulative += buckets[i]
        va_idx.append(i)
        if cumulative >= target:
            break
    vah_price = p_min + (max(va_idx) + 1) * bucket_size
    val_price = p_min + min(va_idx) * bucket_size

    return poc_price, vah_price, val_price


def _detect_fvg(candles, min_gap_pct=0.08):
    """
    3-candle Fair Value Gap detection.
    min_gap_pct: minimum gap size as % of price.
    Filters out micro-gaps that are not real FVGs.
    """
    fvgs = []
    if len(candles) < 3:
        return fvgs
    for i in range(2, len(candles)):
        c1 = candles[i - 2]
        c3 = candles[i]
        ref_price = c3.close
        if ref_price <= 0:
            continue

        # Bullish FVG: c1.high < c3.low
        if c1.high < c3.low:
            gap = c3.low - c1.high
            gap_pct = gap / ref_price * 100
            if gap_pct < min_gap_pct:
                continue
            fvgs.append({
                "kind": "FVG_BULL",
                "top": c3.low,
                "bottom": c1.high,
                "mid": (c3.low + c1.high) / 2,
                "gap_pct": gap_pct,
                "index": i,
            })
        # Bearish FVG: c1.low > c3.high
        elif c1.low > c3.high:
            gap = c1.low - c3.high
            gap_pct = gap / ref_price * 100
            if gap_pct < min_gap_pct:
                continue
            fvgs.append({
                "kind": "FVG_BEAR",
                "top": c1.low,
                "bottom": c3.high,
                "mid": (c1.low + c3.high) / 2,
                "gap_pct": gap_pct,
                "index": i,
            })
    return fvgs


def _detect_bos_choch(candles, swing_highs, swing_lows):
    """BOS and CHOCH from swing structure."""
    if len(swing_highs) < 2 or len(swing_lows) < 2:
        return False, False, None, None

    last_close = candles[-1].close
    last_high = swing_highs[-1][1]
    prev_high = swing_highs[-2][1]
    last_low = swing_lows[-1][1]
    prev_low = swing_lows[-2][1]

    # BOS bullish = close above recent swing high
    bos_bull = last_close > last_high and last_high > prev_high
    # BOS bearish = close below recent swing low
    bos_bear = last_close < last_low and last_low < prev_low

    # CHOCH = change of character (reversal signal)
    # Bullish CHOCH: was making lower highs, now breaks above last swing high
    choch_bull = last_close > last_high and last_high < prev_high
    # Bearish CHOCH: was making higher lows, now breaks below last swing low
    choch_bear = last_close < last_low and last_low > prev_low

    bos = bos_bull or bos_bear
    choch = choch_bull or choch_bear

    bos_level = last_high if bos_bull else (last_low if bos_bear else None)
    choch_level = last_high if choch_bull else (last_low if choch_bear else None)

    return bos, choch, bos_level, choch_level


def _detect_order_blocks(candles, lookback=20):
    """Order Block = last opposite-color candle before strong displacement."""
    obs = []
    if len(candles) < 5:
        return obs
    recent = candles[-lookback:]
    for i in range(1, len(recent) - 2):
        prev = recent[i - 1]
        current = recent[i]
        nxt = recent[i + 1]

        body_current = abs(current.close - current.open)
        body_next = abs(nxt.close - nxt.open)

        # Bullish OB: bearish candle followed by strong bullish move
        if (current.close < current.open  # red candle
                and nxt.close > nxt.open  # green candle
                and body_next > body_current * 1.5):
            obs.append({
                "kind": "ORDER_BLOCK_BULL",
                "top": current.high,
                "bottom": current.low,
                "mid": (current.high + current.low) / 2,
            })

        # Bearish OB: bullish candle followed by strong bearish move
        elif (current.close > current.open  # green
              and nxt.close < nxt.open  # red
              and body_next > body_current * 1.5):
            obs.append({
                "kind": "ORDER_BLOCK_BEAR",
                "top": current.high,
                "bottom": current.low,
                "mid": (current.high + current.low) / 2,
            })
    return obs


def _detect_demand_supply(candles, lookback=30):
    """Demand zone = base + strong rally. Supply = base + strong drop."""
    zones = []
    if len(candles) < 10:
        return zones
    recent = candles[-lookback:]
    for i in range(2, len(recent) - 2):
        base_start = recent[i - 2]
        base_end = recent[i]
        # Small base (tight range)
        base_range = abs(base_end.high - base_start.low)
        body_avg = sum(
            abs(c.close - c.open) for c in recent[max(0, i-5):i]
        ) / min(5, i)
        if base_range > body_avg * 0.8:
            continue
        # Strong move after
        next_c = recent[i + 1]
        next_body = abs(next_c.close - next_c.open)
        if next_body > base_range * 2.0:
            if next_c.close > next_c.open:
                zones.append({
                    "kind": "DEMAND_ZONE",
                    "top": base_end.high,
                    "bottom": base_start.low,
                    "mid": (base_end.high + base_start.low) / 2,
                })
            else:
                zones.append({
                    "kind": "SUPPLY_ZONE",
                    "top": base_end.high,
                    "bottom": base_start.low,
                    "mid": (base_end.high + base_start.low) / 2,
                })
    return zones


# ============================================================
# OBSTACLE MAPPER
# ============================================================

class ObstacleMapper:

    def build(
        self,
        symbol: str,
        candles: Sequence[Candle],
    ) -> ObstacleMap:

        now = datetime.now(timezone.utc)

        if not candles:
            return ObstacleMap(
                symbol=symbol, current_price=0.0,
                above=(), below=(),
                nearest_resistance=None, nearest_support=None,
                day_high=None, day_low=None, day_range_pct=None,
                bos_detected=False, choch_detected=False,
                fvg_count=0, order_block_count=0,
                demand_supply_count=0,
                candle_count=0,
                provenance="NO_CANDLES",
                computed_at=now,
            )

        current_price = candles[-1].close
        if current_price <= 0:
            current_price = 1e-9

        obstacles = []

        # --- Day High/Low ---
        day_high = max(c.high for c in candles)
        day_low = min(c.low for c in candles)
        day_range_pct = (
            (day_high - day_low) / day_low * 100 if day_low > 0 else 0
        )

        obstacles.append(self._mk(
            ObstacleKind.DAY_HIGH, day_high, current_price,
            strength=90, meta={"note": "period high"},
        ))
        obstacles.append(self._mk(
            ObstacleKind.DAY_LOW, day_low, current_price,
            strength=90, meta={"note": "period low"},
        ))

        # --- Prev Close ---
        if len(candles) >= 2:
            prev_close = candles[-2].close
            obstacles.append(self._mk(
                ObstacleKind.PREV_CLOSE, prev_close, current_price,
                strength=60, meta={},
            ))

        # --- Round numbers ---
        for rn in _round_number_levels(current_price, spread_pct=3.0):
            obstacles.append(self._mk(
                ObstacleKind.ROUND_NUMBER, rn, current_price,
                strength=45, meta={"note": "psychological level"},
            ))

        # --- Swings ---
        swing_highs, swing_lows = _detect_swings(candles, lookback=3)
        atr_val = _compute_atr(candles, 14) or (current_price * 0.005)
        min_swing_size = atr_val * 0.5

        # Filter: only meaningful swings (bigger than min_swing_size apart)
        filtered_highs = []
        for idx, price in swing_highs:
            if not filtered_highs:
                filtered_highs.append((idx, price))
            else:
                prev_price = filtered_highs[-1][1]
                if abs(price - prev_price) >= min_swing_size:
                    filtered_highs.append((idx, price))

        filtered_lows = []
        for idx, price in swing_lows:
            if not filtered_lows:
                filtered_lows.append((idx, price))
            else:
                prev_price = filtered_lows[-1][1]
                if abs(price - prev_price) >= min_swing_size:
                    filtered_lows.append((idx, price))

        for idx, price in filtered_highs[-5:]:
            obstacles.append(self._mk(
                ObstacleKind.SWING_HIGH, price, current_price,
                strength=65, meta={"index": idx},
            ))
        for idx, price in filtered_lows[-5:]:
            obstacles.append(self._mk(
                ObstacleKind.SWING_LOW, price, current_price,
                strength=65, meta={"index": idx},
            ))

        # --- FVG ---
        fvgs = _detect_fvg(candles)
        for fvg in fvgs[-10:]:
            kind = ObstacleKind.FVG_BULL if fvg["kind"] == "FVG_BULL" else ObstacleKind.FVG_BEAR
            obstacles.append(self._mk(
                kind, fvg["mid"], current_price,
                strength=55,
                meta={"top": fvg["top"], "bottom": fvg["bottom"]},
            ))

        # --- BOS / CHOCH ---
        bos, choch, bos_level, choch_level = _detect_bos_choch(
            candles, swing_highs, swing_lows
        )
        if bos and bos_level:
            # Determine bull or bear from last close
            kind = (
                ObstacleKind.BOS_BULL
                if candles[-1].close > bos_level
                else ObstacleKind.BOS_BEAR
            )
            obstacles.append(self._mk(
                kind, bos_level, current_price,
                strength=85, meta={"note": "break of structure"},
            ))
        if choch and choch_level:
            kind = (
                ObstacleKind.CHOCH_BULL
                if candles[-1].close > choch_level
                else ObstacleKind.CHOCH_BEAR
            )
            obstacles.append(self._mk(
                kind, choch_level, current_price,
                strength=80, meta={"note": "change of character"},
            ))

        # --- Order Blocks ---
        obs = _detect_order_blocks(candles)
        for ob in obs[-6:]:
            kind = (
                ObstacleKind.ORDER_BLOCK_BULL
                if ob["kind"] == "ORDER_BLOCK_BULL"
                else ObstacleKind.ORDER_BLOCK_BEAR
            )
            obstacles.append(self._mk(
                kind, ob["mid"], current_price,
                strength=70,
                meta={"top": ob["top"], "bottom": ob["bottom"]},
            ))

        # --- Demand/Supply ---
        zones = _detect_demand_supply(candles)
        for z in zones[-6:]:
            kind = (
                ObstacleKind.DEMAND_ZONE
                if z["kind"] == "DEMAND_ZONE"
                else ObstacleKind.SUPPLY_ZONE
            )
            obstacles.append(self._mk(
                kind, z["mid"], current_price,
                strength=75,
                meta={"top": z["top"], "bottom": z["bottom"]},
            ))

        # --- Volume Profile ---
        poc, vah, val = _volume_profile(candles)
        if poc:
            obstacles.append(self._mk(
                ObstacleKind.VOLUME_POC, poc, current_price,
                strength=80, meta={},
            ))
        if vah:
            obstacles.append(self._mk(
                ObstacleKind.VOLUME_VAH, vah, current_price,
                strength=70, meta={"note": "value area high"},
            ))
        if val:
            obstacles.append(self._mk(
                ObstacleKind.VOLUME_VAL, val, current_price,
                strength=70, meta={"note": "value area low"},
            ))

        # --- SL clusters (inferred) ---
        # Rule: just beyond swing highs / round numbers likely have SLs
        sl_above = self._infer_sl_cluster(swing_highs, "ABOVE", current_price)
        sl_below = self._infer_sl_cluster(swing_lows, "BELOW", current_price)
        for price, strength in sl_above:
            obstacles.append(self._mk(
                ObstacleKind.SL_CLUSTER_ABOVE, price, current_price,
                strength=strength, meta={"note": "inferred SL pool"},
            ))
        for price, strength in sl_below:
            obstacles.append(self._mk(
                ObstacleKind.SL_CLUSTER_BELOW, price, current_price,
                strength=strength, meta={"note": "inferred SL pool"},
            ))

        # --- Cluster nearby obstacles (ATR-based band) ---
        # Smaller of: ATR * 0.4 OR 0.08% of price
        _atr = _compute_atr(candles, 14) or (current_price * 0.003)
        cluster_band = min(_atr * 0.4, current_price * 0.0008)

        def cluster(items):
            """Merge obstacles within cluster_band, keep strongest."""
            if not items:
                return []
            sorted_items = sorted(items, key=lambda o: o.price)
            merged = []
            current_cluster = [sorted_items[0]]
            for o in sorted_items[1:]:
                if abs(o.price - current_cluster[-1].price) <= cluster_band:
                    current_cluster.append(o)
                else:
                    merged.append(_merge_cluster(current_cluster))
                    current_cluster = [o]
            merged.append(_merge_cluster(current_cluster))
            return merged

        # Type weights — how important each kind is
        TYPE_WEIGHTS = {
            "DAY_HIGH": 1.0,
            "DAY_LOW": 1.0,
            "VOLUME_POC": 0.95,
            "VOLUME_VAH": 0.85,
            "VOLUME_VAL": 0.85,
            "BOS_BULL": 0.95,
            "BOS_BEAR": 0.95,
            "CHOCH_BULL": 0.90,
            "CHOCH_BEAR": 0.90,
            "ORDER_BLOCK_BULL": 0.85,
            "ORDER_BLOCK_BEAR": 0.85,
            "DEMAND_ZONE": 0.85,
            "SUPPLY_ZONE": 0.85,
            "SL_CLUSTER_ABOVE": 0.90,
            "SL_CLUSTER_BELOW": 0.90,
            "SWING_HIGH": 0.70,
            "SWING_LOW": 0.70,
            "FVG_BULL": 0.60,
            "FVG_BEAR": 0.60,
            "PREV_CLOSE": 0.65,
            "ROUND_NUMBER": 0.50,
        }

        def _score_obstacle(o):
            """Higher = stronger. Combines type, strength, touches, proximity."""
            tw = TYPE_WEIGHTS.get(o.kind, 0.5)
            # touches boost (log scale)
            import math as _m
            touch_boost = 1.0 + _m.log10(max(1, o.touches) + 1) * 0.5
            # proximity — closer to price = more relevant
            if o.distance_pct <= 0.05:
                prox = 1.0
            elif o.distance_pct <= 0.20:
                prox = 0.90
            elif o.distance_pct <= 0.50:
                prox = 0.75
            elif o.distance_pct <= 1.00:
                prox = 0.55
            else:
                prox = 0.35
            return round(tw * o.strength * touch_boost * prox, 2)

        def _merge_cluster(items):
            """Combines obstacles within a cluster, keeps strongest."""
            if len(items) == 1:
                return items[0]
            strongest = max(items, key=lambda o: o.strength)
            boost = min(20, (len(items) - 1) * 4)
            kinds = sorted(set(o.kind for o in items))
            merged = Obstacle(
                kind=strongest.kind,
                side=strongest.side,
                price=strongest.price,
                strength=min(100, strongest.strength + boost),
                distance_pct=strongest.distance_pct,
                touches=len(items),
                metadata={
                    "cluster_kinds": kinds,
                    "cluster_size": len(items),
                },
            )
            # attach score
            return Obstacle(
                kind=merged.kind,
                side=merged.side,
                price=merged.price,
                strength=merged.strength,
                distance_pct=merged.distance_pct,
                touches=merged.touches,
                metadata={**merged.metadata, "score": _score_obstacle(merged)},
            )

        above_raw = [o for o in obstacles if o.side == "ABOVE"]
        below_raw = [o for o in obstacles if o.side == "BELOW"]

        above_clustered = cluster(above_raw)
        below_clustered = cluster(below_raw)

        # --- Distance filter: nearest 3% only ---
        max_dist_pct = 3.0
        above_filtered = [o for o in above_clustered if o.distance_pct <= max_dist_pct]
        below_filtered = [o for o in below_clustered if o.distance_pct <= max_dist_pct]

        # --- Sort by SCORE (not price) ---
        def _score_of(o):
            return o.metadata.get("score", o.strength)

        # Above: nearest by price (first 5 strongest by score, then sort by price)
        above_by_score = sorted(above_filtered, key=_score_of, reverse=True)
        top_above = above_by_score[:10]
        above = sorted(top_above, key=lambda o: o.price)

        below_by_score = sorted(below_filtered, key=_score_of, reverse=True)
        top_below = below_by_score[:10]
        below = sorted(top_below, key=lambda o: -o.price)

        nearest_resistance = above[0] if above else None
        nearest_support = below[0] if below else None

        return ObstacleMap(
            symbol=symbol,
            current_price=current_price,
            above=tuple(above),
            below=tuple(below),
            nearest_resistance=nearest_resistance,
            nearest_support=nearest_support,
            day_high=day_high,
            day_low=day_low,
            day_range_pct=round(day_range_pct, 4),
            bos_detected=bos,
            choch_detected=choch,
            fvg_count=len(fvgs),
            order_block_count=len(obs),
            demand_supply_count=len(zones),
            candle_count=len(candles),
            provenance="REAL_CANDLES",
            computed_at=now,
        )

    @staticmethod
    def _mk(kind, price, current, strength, meta):
        kind_str = kind.value if hasattr(kind, "value") else str(kind)
        # Epsilon: 0.01% — same level treated as ABOVE
        epsilon = current * 0.0001
        side = "ABOVE" if price >= current - epsilon else "BELOW"
        dist = abs(price - current) / current * 100 if current > 0 else 0
        return Obstacle(
            kind=kind_str,
            side=side,
            price=round(price, 6),
            strength=strength,
            distance_pct=round(dist, 4),
            touches=0,
            metadata=meta,
        )

    @staticmethod
    def _infer_sl_cluster(swings, side, current, band_pct=0.15):
        """SL cluster just beyond swing levels."""
        if not swings:
            return []
        results = []
        band = current * band_pct / 100
        seen = set()
        for _, price in swings[-5:]:
            if side == "ABOVE":
                cluster_price = price + band
            else:
                cluster_price = price - band
            key = round(cluster_price, 2)
            if key in seen:
                continue
            seen.add(key)
            results.append((cluster_price, 55))
        return results


_engine: Optional[ObstacleMapper] = None


def get_obstacle_mapper() -> ObstacleMapper:
    global _engine
    if _engine is None:
        _engine = ObstacleMapper()
    return _engine


__all__ = [
    "ObstacleKind",
    "ObstacleSide",
    "Obstacle",
    "ObstacleMap",
    "ObstacleMapper",
    "get_obstacle_mapper",
]
