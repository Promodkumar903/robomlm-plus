"""Fix volume_engine: candle-based delta + real tape snapshot"""
from pathlib import Path
import shutil
from datetime import datetime

ROOT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\intelligence\real")
TARGET = ROOT / "volume_engine.py"

if not TARGET.exists():
    print(f"ERROR: {TARGET} not found")
    raise SystemExit(1)

content = TARGET.read_text(encoding="utf-8")
backup = TARGET.with_suffix(f".py.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(TARGET, backup)
print(f"BACKUP: {backup}")

# Add candle-based delta helper before class VolumeEngine
helper = '''

# ============================================================
# CANDLE-BASED DELTA PROXY
# ============================================================

def _candle_delta(candles):
    """
    Approximate buy/sell volume from candle body ratio.
    Bullish candle with large body = strong buying.
    Bearish candle with large body = strong selling.
    
    Returns (buy_vol, sell_vol, net_delta) — real math from OHLCV.
    """
    buy_total = 0.0
    sell_total = 0.0
    for c in candles:
        v = c.volume
        if v <= 0:
            continue
        rng = c.high - c.low
        if rng <= 0:
            buy_total += v * 0.5
            sell_total += v * 0.5
            continue
        body_ratio = (c.close - c.open) / rng
        # Clamp to [-1, 1]
        body_ratio = max(-1.0, min(1.0, body_ratio))
        # buy share goes from 0 (all sell) to 1 (all buy)
        buy_share = (body_ratio + 1.0) * 0.5
        sell_share = 1.0 - buy_share
        buy_total += v * buy_share
        sell_total += v * sell_share
    return buy_total, sell_total, buy_total - sell_total


def _delta_windows_from_candles(candles_1m):
    """
    Compute delta over 1m / 5m / 15m / 1h windows using 1m candles.
    """
    def last_n(n):
        if len(candles_1m) < n:
            return None
        _, _, net = _candle_delta(candles_1m[-n:])
        return net

    return {
        "1m": last_n(1),
        "5m": last_n(5),
        "15m": last_n(15),
        "1h": last_n(60),
    }

'''

# Insert helper before class VolumeEngine
marker = "class VolumeEngine:"
if "def _candle_delta(" in content:
    print("Helper already present")
elif marker in content:
    content = content.replace(marker, helper + marker, 1)
    print("PATCH 1: candle delta helper added")
else:
    print("WARNING: marker not found")
    raise SystemExit(1)

# Replace the delta computation block
old_delta_block = '''        def delta_window(seconds):
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
        delta_1h, total_1h = delta_window(3600)'''

new_delta_block = '''        # Candle-based delta windows (real math from OHLCV)
        delta_windows = _delta_windows_from_candles(candles_1m)
        delta_1m = delta_windows.get("1m") or 0.0
        delta_5m = delta_windows.get("5m") or 0.0
        delta_15m = delta_windows.get("15m") or 0.0
        delta_1h = delta_windows.get("1h") or 0.0'''

if "Candle-based delta windows" in content:
    print("Delta block already patched")
elif old_delta_block in content:
    content = content.replace(old_delta_block, new_delta_block, 1)
    print("PATCH 2: delta windows from candles")
else:
    print("WARNING: delta block not found")

# Fix taker ratio — use candle delta for total split
old_taker = '''        total_buy = sum(t.size for t in trades if t.side == "Buy")
        total_sell = sum(t.size for t in trades if t.side == "Sell")
        total_vol = total_buy + total_sell
        taker_buy_ratio = (total_buy / total_vol) if total_vol > 0 else 0.5'''

new_taker = '''        # Taker ratio — use candles for stable read, tape as overlay
        candle_buy, candle_sell, _ = _candle_delta(candles_1m[-15:])
        candle_total = candle_buy + candle_sell
        candle_ratio = (candle_buy / candle_total) if candle_total > 0 else 0.5

        # Tape ratio (may be noisy — 1-sec snapshot)
        tape_buy = sum(t.size for t in trades if t.side == "Buy")
        tape_sell = sum(t.size for t in trades if t.side == "Sell")
        tape_total = tape_buy + tape_sell
        tape_ratio = (tape_buy / tape_total) if tape_total > 0 else candle_ratio

        # Weight: 70% candles (stable), 30% tape (live)
        taker_buy_ratio = candle_ratio * 0.7 + tape_ratio * 0.3'''

if "candle_buy, candle_sell, _ = _candle_delta" in content:
    print("Taker fix already applied")
elif old_taker in content:
    content = content.replace(old_taker, new_taker, 1)
    print("PATCH 3: taker ratio uses candles + tape blend")
else:
    print("WARNING: taker block not found")

TARGET.write_text(content, encoding="utf-8")
print()
print(f"UPDATED: {TARGET}")
print()
print("Test:")
print('  python -c "from app.intelligence.real.volume_engine import get_volume_engine; v = get_volume_engine().compute(\\"BTC/USDT\\"); print(\\"delta 1m/5m/15m/1h:\\", v.delta_1m, v.delta_5m, v.delta_15m, v.delta_1h); print(\\"delta trend:\\", v.delta_trend); print(\\"taker ratio:\\", v.taker_buy_ratio, v.taker_interpretation); print(\\"vol ratio:\\", v.volume_ratio, v.volume_state); print(\\"roc:\\", v.roc_1m, v.roc_5m, v.roc_15m, v.roc_1h); print(\\"divergence:\\", v.delta_divergence, v.divergence_type); print(\\"verdict:\\", v.volume_direction, v.volume_strength); [print(\\"  -\\", r) for r in v.reasons]"')