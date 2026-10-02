"""Fix unified_signal TP/SL direction + validate RR"""
from pathlib import Path
import shutil
from datetime import datetime

ROOT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\intelligence\real")
TARGET = ROOT / "unified_signal.py"

content = TARGET.read_text(encoding="utf-8")
backup = TARGET.with_suffix(f".py.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(TARGET, backup)
print(f"BACKUP: {backup}")

old_block = '''        if action in {"BUY", "SELL"} and om:
            if action == "BUY":
                # SL below nearest support
                if om.nearest_support and om.nearest_support.price:
                    sl = om.nearest_support.price * 0.999
                elif levels and levels.vwap_daily:
                    sl = levels.vwap_daily * 0.998
                # TP at nearest strong resistance
                if om.nearest_resistance and om.nearest_resistance.price:
                    tp = om.nearest_resistance.price * 0.999
            elif action == "SELL":
                if om.nearest_resistance and om.nearest_resistance.price:
                    sl = om.nearest_resistance.price * 1.001
                elif levels and levels.vwap_daily:
                    sl = levels.vwap_daily * 1.002
                if om.nearest_support and om.nearest_support.price:
                    tp = om.nearest_support.price * 1.001

            if sl and tp and entry > 0:
                risk = abs(entry - sl)
                reward = abs(tp - entry)
                rr = (reward / risk) if risk > 0 else None'''

new_block = '''        if action in {"BUY", "SELL"} and om and entry > 0:
            # -------- Fallback ATR for SL/TP distance --------
            atr_val = 0.0
            if candles_1m and len(candles_1m) >= 15:
                trs = []
                for i in range(1, 15):
                    c = candles_1m[-i]
                    prev = candles_1m[-i - 1]
                    tr = max(c.high - c.low, abs(c.high - prev.close), abs(c.low - prev.close))
                    trs.append(tr)
                atr_val = sum(trs) / len(trs)
            if atr_val <= 0:
                atr_val = entry * 0.003  # 0.3% fallback

            if action == "BUY":
                # SL below entry
                sl_candidates = []
                if om.nearest_support and om.nearest_support.price < entry:
                    sl_candidates.append(om.nearest_support.price * 0.999)
                if levels and levels.vwap_daily and levels.vwap_daily < entry:
                    sl_candidates.append(levels.vwap_daily * 0.998)
                if sl_candidates:
                    sl = max(sl_candidates)  # nearest one below entry
                else:
                    sl = entry - atr_val * 2.0

                # TP above entry
                tp_candidates = []
                if om.nearest_resistance and om.nearest_resistance.price > entry:
                    tp_candidates.append(om.nearest_resistance.price * 0.999)
                if levels and levels.vwap_upper_1 and levels.vwap_upper_1 > entry:
                    tp_candidates.append(levels.vwap_upper_1 * 0.999)
                if tp_candidates:
                    tp = min(tp_candidates)  # nearest one above entry
                else:
                    tp = entry + atr_val * 4.0

            elif action == "SELL":
                # SL above entry
                sl_candidates = []
                if om.nearest_resistance and om.nearest_resistance.price > entry:
                    sl_candidates.append(om.nearest_resistance.price * 1.001)
                if levels and levels.vwap_daily and levels.vwap_daily > entry:
                    sl_candidates.append(levels.vwap_daily * 1.002)
                if sl_candidates:
                    sl = min(sl_candidates)  # nearest one above entry
                else:
                    sl = entry + atr_val * 2.0

                # TP below entry
                tp_candidates = []
                if om.nearest_support and om.nearest_support.price < entry:
                    tp_candidates.append(om.nearest_support.price * 1.001)
                if levels and levels.vwap_lower_1 and levels.vwap_lower_1 < entry:
                    tp_candidates.append(levels.vwap_lower_1 * 1.001)
                if tp_candidates:
                    tp = max(tp_candidates)  # nearest one below entry
                else:
                    tp = entry - atr_val * 4.0

            # -------- Validate SL/TP direction --------
            valid = True
            if action == "BUY":
                if not (sl < entry < tp):
                    valid = False
            elif action == "SELL":
                if not (sl > entry > tp):
                    valid = False

            if not valid:
                # Last-resort ATR fallback in correct direction
                if action == "BUY":
                    sl = entry - atr_val * 2.0
                    tp = entry + atr_val * 4.0
                else:
                    sl = entry + atr_val * 2.0
                    tp = entry - atr_val * 4.0

            # -------- RR --------
            risk = abs(entry - sl)
            reward = abs(tp - entry)
            if risk > 0 and reward > 0:
                rr = reward / risk
            else:
                rr = None'''

if "Fallback ATR for SL/TP distance" in content:
    print("Fix already applied")
elif old_block in content:
    content = content.replace(old_block, new_block, 1)
    print("PATCH: SL/TP direction validated + ATR fallback")
else:
    print("WARNING: block not found")
    raise SystemExit(1)

TARGET.write_text(content, encoding="utf-8")
print()
print(f"UPDATED: {TARGET}")
print()
print("Test:")
print('  python -c "from app.intelligence.real.unified_signal import get_unified_signal_engine; s = get_unified_signal_engine().compute(\\"BTC/USDT\\"); print(\\"DIRECTION:\\", s.direction, \\"ACTION:\\", s.action); print(\\"ENTRY:\\", s.entry_price); print(\\"SL:\\", s.stop_loss); print(\\"TP:\\", s.take_profit); print(\\"RR:\\", s.risk_reward); print(\\"QUALITY:\\", s.trade_quality)"')