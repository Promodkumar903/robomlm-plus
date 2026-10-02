"""Rewrite obstacle_mapper with score-based ranking (raw-first)"""
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

# Patch 1 — Reduce FVG gap threshold further (0.08%)
old = 'def _detect_fvg(candles, min_gap_pct=0.05):'
new = 'def _detect_fvg(candles, min_gap_pct=0.08):'
if old in content:
    content = content.replace(old, new, 1)
    print("PATCH 1: FVG min_gap 0.05 → 0.08")

# Patch 2 — Better clustering: use ATR-based band, NOT fixed 0.15%
old_cluster = '''        # --- Cluster nearby obstacles (0.15% band) ---
        cluster_band_pct = 0.15
        cluster_band = current_price * cluster_band_pct / 100'''

new_cluster = '''        # --- Cluster nearby obstacles (ATR-based band) ---
        # Smaller of: ATR * 0.4 OR 0.08% of price
        _atr = _compute_atr(candles, 14) or (current_price * 0.003)
        cluster_band = min(_atr * 0.4, current_price * 0.0008)'''

if "cluster_band = min(_atr * 0.4, current_price * 0.0008)" in content:
    print("PATCH 2 already applied")
elif old_cluster in content:
    content = content.replace(old_cluster, new_cluster, 1)
    print("PATCH 2: cluster band → ATR-based, tighter")

# Patch 3 — Replace _merge_cluster with score-based merge
old_merge = '''        def _merge_cluster(items):
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
            )'''

new_merge = '''        # Type weights — how important each kind is
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
            )'''

if "_score_obstacle" in content:
    print("PATCH 3 already applied")
elif old_merge in content:
    content = content.replace(old_merge, new_merge, 1)
    print("PATCH 3: type-weighted score system")
else:
    print("PATCH 3 skipped (marker not found)")

# Patch 4 — Sort by score instead of price
old_final = '''        # --- Distance filter: only keep nearest 3% ---
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

new_final = '''        # --- Distance filter: nearest 3% only ---
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
        nearest_support = below[0] if below else None'''

if "_score_of" in content:
    print("PATCH 4 already applied")
elif old_final in content:
    content = content.replace(old_final, new_final, 1)
    print("PATCH 4: sort by score")
else:
    print("PATCH 4 skipped (marker not found)")

# Patch 5 — Fix side classification epsilon
old_side = '''        side = "ABOVE" if price > current else "BELOW"'''
new_side = '''        # Epsilon: 0.01% — same level treated as ABOVE
        epsilon = current * 0.0001
        side = "ABOVE" if price >= current - epsilon else "BELOW"'''
if "epsilon = current * 0.0001" in content:
    print("PATCH 5 already applied")
elif old_side in content:
    content = content.replace(old_side, new_side, 1)
    print("PATCH 5: epsilon tolerance for side")

TARGET.write_text(content, encoding="utf-8")
print()
print(f"UPDATED: {TARGET}")
print()
print("Test:")
print('  python -c "from app.intelligence.real.real_market_data import get_real_market_data; from app.intelligence.real.obstacle_mapper import get_obstacle_mapper; m = get_real_market_data(); c, _ = m.get_candles(\\"BTC/USDT\\", \\"15\\", 200); om = get_obstacle_mapper().build(\\"BTC/USDT\\", c); print(f\\"FVG:\\", om.fvg_count, \\"| above:\\", len(om.above), \\"| below:\\", len(om.below)); print(); [print(f\\"{o.kind:24} {o.price:>12} str={o.strength:>3} dist={o.distance_pct:>6.3f}% touches={o.touches} score={o.metadata.get(\\\\\\"score\\\\\\", 0)}\\") for o in om.above[:6]]"')