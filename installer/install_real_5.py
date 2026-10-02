"""Improve obstacle_mapper: filters, clustering, dedup"""
from pathlib import Path
import shutil
from datetime import datetime

ROOT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\intelligence\real")
TARGET = ROOT / "obstacle_mapper.py"

if not TARGET.exists():
    print(f"ERROR: {TARGET} not found")
    raise SystemExit(1)

content = TARGET.read_text(encoding="utf-8")
backup = TARGET.with_suffix(f".py.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(TARGET, backup)
print(f"BACKUP: {backup}")

# Patch 1 — FVG minimum gap filter
old_fvg = '''def _detect_fvg(candles):
    """3-candle Fair Value Gap detection."""
    fvgs = []
    if len(candles) < 3:
        return fvgs
    for i in range(2, len(candles)):
        c1 = candles[i - 2]
        c2 = candles[i - 1]
        c3 = candles[i]
        # Bullish FVG: c1.high < c3.low (gap between)
        if c1.high < c3.low:
            fvgs.append({
                "kind": "FVG_BULL",
                "top": c3.low,
                "bottom": c1.high,
                "mid": (c3.low + c1.high) / 2,
                "index": i,
            })
        # Bearish FVG: c1.low > c3.high
        elif c1.low > c3.high:
            fvgs.append({
                "kind": "FVG_BEAR",
                "top": c1.low,
                "bottom": c3.high,
                "mid": (c1.low + c3.high) / 2,
                "index": i,
            })
    return fvgs'''

new_fvg = '''def _detect_fvg(candles, min_gap_pct=0.05):
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
    return fvgs'''

if "min_gap_pct=0.05" in content:
    print("FVG patch already applied")
elif old_fvg in content:
    content = content.replace(old_fvg, new_fvg, 1)
    print("PATCH 1: FVG minimum gap filter")
else:
    print("PATCH 1 skipped (marker not found)")

# Patch 2 — Swing minimum size filter (ATR-based)
old_swings = '''        swing_highs, swing_lows = _detect_swings(candles, lookback=3)
        for idx, price in swing_highs[-8:]:
            obstacles.append(self._mk(
                ObstacleKind.SWING_HIGH, price, current_price,
                strength=65, meta={"index": idx},
            ))
        for idx, price in swing_lows[-8:]:
            obstacles.append(self._mk(
                ObstacleKind.SWING_LOW, price, current_price,
                strength=65, meta={"index": idx},
            ))'''

new_swings = '''        swing_highs, swing_lows = _detect_swings(candles, lookback=3)
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
            ))'''

if "min_swing_size = atr_val * 0.5" in content:
    print("Swing patch already applied")
elif old_swings in content:
    content = content.replace(old_swings, new_swings, 1)
    print("PATCH 2: swing minimum size filter")
else:
    print("PATCH 2 skipped (marker not found)")

# Patch 3 — Add cluster + distance filter
old_sort = '''        # --- Sort into above/below ---
        above = sorted(
            [o for o in obstacles if o.side == "ABOVE"],
            key=lambda o: o.price,
        )
        below = sorted(
            [o for o in obstacles if o.side == "BELOW"],
            key=lambda o: -o.price,
        )

        nearest_resistance = above[0] if above else None
        nearest_support = below[0] if below else None'''

new_sort = '''        # --- Cluster nearby obstacles (0.15% band) ---
        cluster_band_pct = 0.15
        cluster_band = current_price * cluster_band_pct / 100

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

        def _merge_cluster(items):
            """Combines obstacles within a cluster."""
            if len(items) == 1:
                return items[0]
            # Strongest one leads, but boost strength for cluster count
            strongest = max(items, key=lambda o: o.strength)
            boost = min(15, (len(items) - 1) * 3)
            kinds = sorted(set(o.kind for o in items))
            return Obstacle(
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

        above_raw = [o for o in obstacles if o.side == "ABOVE"]
        below_raw = [o for o in obstacles if o.side == "BELOW"]

        above_clustered = cluster(above_raw)
        below_clustered = cluster(below_raw)

        # --- Distance filter: only keep nearest 3% ---
        max_dist_pct = 3.0
        above = sorted(
            [o for o in above_clustered if o.distance_pct <= max_dist_pct],
            key=lambda o: o.price,
        )
        below = sorted(
            [o for o in below_clustered if o.distance_pct <= max_dist_pct],
            key=lambda o: -o.price,
        )

        nearest_resistance = above[0] if above else None
        nearest_support = below[0] if below else None'''

if "cluster_band_pct = 0.15" in content:
    print("Cluster patch already applied")
elif old_sort in content:
    content = content.replace(old_sort, new_sort, 1)
    print("PATCH 3: clustering + distance filter")
else:
    print("PATCH 3 skipped (marker not found)")

TARGET.write_text(content, encoding="utf-8")
print()
print(f"UPDATED: {TARGET}")
print()
print("Test:")
print('  python -c "from app.intelligence.real.real_market_data import get_real_market_data; from app.intelligence.real.obstacle_mapper import get_obstacle_mapper; m = get_real_market_data(); c, _ = m.get_candles(\\"BTC/USDT\\", \\"15\\", 200); om = get_obstacle_mapper().build(\\"BTC/USDT\\", c); print(\\"FVG:\\", om.fvg_count, \\"| above:\\", len(om.above), \\"| below:\\", len(om.below)); print(); [print(f\\"{o.kind:24} {o.price:>12} str={o.strength:>3} dist={o.distance_pct:>6.3f}% touches={o.touches}\\") for o in om.above[:5]]"')