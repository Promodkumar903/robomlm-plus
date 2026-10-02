"""Patch auto_loop.py: signal SL/TP preference + config-driven gates (NO hardcoding)"""
from pathlib import Path
import shutil
from datetime import datetime

TARGET = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\autorobomlm\auto_loop.py")
content = TARGET.read_text(encoding="utf-8")

backup = TARGET.with_suffix(f".py.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(TARGET, backup)
print(f"BACKUP: {backup}")

if "_extract_signal_sl_tp" in content:
    print("Already patched")
    raise SystemExit(0)

# ---------- 1. Helper ----------
helper = '''    def _extract_signal_sl_tp(
        self, signal: dict, direction: str, price: float
    ):
        """Extract signal-supplied SL/TP with direction validation."""
        if not isinstance(signal, dict):
            return (None, None, None)
        try:
            sl = signal.get("stop_loss")
            tp = signal.get("take_profit")
            sl = float(sl) if sl is not None else None
            tp = float(tp) if tp is not None else None
        except (TypeError, ValueError):
            return (None, None, None)
        if sl is None or tp is None or sl <= 0 or tp <= 0 or price <= 0:
            return (None, None, None)
        if direction == "BUY" and sl < price < tp:
            return (sl, tp, "SIGNAL")
        if direction == "SELL" and sl > price > tp:
            return (sl, tp, "SIGNAL")
        return (None, None, None)

    def _kill_switch_engaged(self) -> bool:'''

content = content.replace(
    "    def _kill_switch_engaged(self) -> bool:",
    helper, 1,
)
print("Helper added")

# ---------- 2. Config-driven gates (no hardcode) ----------
old_price = '''        # Price
        price = self._price_for(symbol)
        if price is None:
            summary.skipped_gates += 1
            summary.events.append(f"{symbol}: no price")
            return
'''

new_price = '''        # Price
        price = self._price_for(symbol)
        if price is None:
            summary.skipped_gates += 1
            summary.events.append(f"{symbol}: no price")
            return

        # ---- Config-driven gates (user controls via config) ----
        try:
            _strength = float(
                signal.get("strength")
                or signal.get("decision_score")
                or 0.0
            )
        except (TypeError, ValueError):
            _strength = 0.0

        _min_strength = float(
            getattr(self.config, "min_strength_gate", 0.0) or 0.0
        )
        if _min_strength > 0.0 and _strength < _min_strength:
            summary.skipped_gates += 1
            summary.events.append(
                f"{symbol}: strength {_strength:.1f} < "
                f"gate {_min_strength:.1f}"
            )
            return

        # ---- Flow-conflict (WARN / SKIP / IGNORE) ----
        _audit = signal.get("audit") or {}
        _flow = _audit.get("flow") or {}
        _flow_dir = _flow.get("direction")
        try:
            _flow_str = float(_flow.get("strength") or 0.0)
        except (TypeError, ValueError):
            _flow_str = 0.0

        _flow_conflict_mode = str(
            getattr(self.config, "flow_conflict_action", "WARN")
        ).upper()

        if (
            _flow_conflict_mode in {"WARN", "SKIP"}
            and _flow_dir
            and _flow_str >= 40.0
            and _flow_dir != "NEUTRAL"
        ):
            expected = "BULLISH" if direction == "BUY" else "BEARISH"
            if _flow_dir != expected:
                msg = (
                    f"{symbol}: flow conflict "
                    f"({_flow_dir} str={_flow_str:.0f} vs {direction})"
                )
                if _flow_conflict_mode == "SKIP":
                    summary.skipped_gates += 1
                    summary.events.append(msg + " [SKIPPED]")
                    return
                else:  # WARN
                    summary.events.append(msg + " [WARN — proceeding]")
'''

if old_price not in content:
    print("WARN: price block not found"); raise SystemExit(1)
content = content.replace(old_price, new_price, 1)
print("Config-driven gates added")

# ---------- 3. SL/TP block ----------
old_sltp = '''        # SL/TP
        sl_tp_result = calculate_sl_tp(
            direction=SLTPDirection(direction),
            entry_price=price,
            sl_atr_multiplier=self.config.sl_atr_multiplier,
            tp_atr_multiplier=self.config.tp_atr_multiplier,
        )
        if sl_tp_result.stop_loss is None:
            summary.errors.append(
                f"{symbol}: SL/TP failed ({sl_tp_result.errors})"
            )
            return

        # Allocation
        allocation = allocate_capital(
            capital=capital,
            entry_price=price,
            stop_loss=sl_tp_result.stop_loss,
            risk_per_trade_pct=self.config.risk_per_trade_pct,
            max_position_pct=self.config.max_position_pct,
        )'''

new_sltp = '''        # SL/TP — prefer signal (structure-aware), ATR fallback
        _sig_sl, _sig_tp, _sig_src = self._extract_signal_sl_tp(
            signal, direction, price
        )

        if _sig_sl is not None and _sig_tp is not None:
            stop_loss = _sig_sl
            take_profit = _sig_tp
            sl_tp_source = _sig_src
        else:
            sl_tp_result = calculate_sl_tp(
                direction=SLTPDirection(direction),
                entry_price=price,
                sl_atr_multiplier=self.config.sl_atr_multiplier,
                tp_atr_multiplier=self.config.tp_atr_multiplier,
            )
            if sl_tp_result.stop_loss is None:
                summary.errors.append(
                    f"{symbol}: SL/TP failed "
                    f"(signal=None, atr={sl_tp_result.errors})"
                )
                return
            stop_loss = sl_tp_result.stop_loss
            take_profit = sl_tp_result.take_profit
            sl_tp_source = "ATR_FALLBACK"

        summary.events.append(
            f"{symbol}: SL/TP source={sl_tp_source} "
            f"sl={stop_loss:.6f} tp={take_profit:.6f}"
        )

        # Allocation
        allocation = allocate_capital(
            capital=capital,
            entry_price=price,
            stop_loss=stop_loss,
            risk_per_trade_pct=self.config.risk_per_trade_pct,
            max_position_pct=self.config.max_position_pct,
        )'''

if old_sltp not in content:
    print("WARN: SL/TP block not found"); raise SystemExit(1)
content = content.replace(old_sltp, new_sltp, 1)
print("SL/TP block replaced")

# ---------- 4. open_position refs ----------
old_open = '''            stop_loss=sl_tp_result.stop_loss,
            take_profit=sl_tp_result.take_profit,'''

new_open = '''            stop_loss=stop_loss,
            take_profit=take_profit,'''

if old_open in content:
    content = content.replace(old_open, new_open, 1)
    print("open_position updated")

TARGET.write_text(content, encoding="utf-8")
print()
print(f"UPDATED: {TARGET}")