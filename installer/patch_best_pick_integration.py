# patch_best_pick_integration.py
# Integrates BestPickEngine into auto_loop.
# - Ranks universe each tick
# - Processes BEST first, not FIRST
# - Uses position size from engine
# Backup PEHLE. Kuch delete nahi.

import os, sys, shutil
from datetime import datetime

TARGET = r"C:\Users\Administrator\ROBOMLM_PLUS\app\autorobomlm\auto_loop.py"


# ---------- NEW METHODS + SIGNATURE ----------

NEW_METHODS = '''    # ============================================================
    # BEST-PICK RANKING (NEW)
    # ============================================================

    def _signal_to_candidate(self, symbol: str, signal: dict):
        """Map raw signal dict -> SignalCandidate. None if unusable."""
        try:
            from app.strategies.best_pick_engine import SignalCandidate
        except Exception:
            return None
        try:
            d = str(signal.get("direction", "NEUTRAL")).upper()
            if d == "LONG":
                d = "BULLISH"
            elif d == "SHORT":
                d = "BEARISH"

            grade = str(
                signal.get("trade_quality")
                or signal.get("grade")
                or "HOLD"
            )
            confidence = float(signal.get("confidence") or 0.0)
            strength = float(
                signal.get("strength")
                or signal.get("decision_score")
                or 0.0
            )

            age_min = 0.0
            ts_str = signal.get("timestamp") or signal.get("signal_ts")
            if ts_str:
                try:
                    from datetime import datetime as _dt, timezone as _tz
                    ts = _dt.fromisoformat(str(ts_str).replace("Z", "+00:00"))
                    now = _dt.now(_tz.utc)
                    age_min = max(0.0, (now - ts).total_seconds() / 60.0)
                except Exception:
                    age_min = 0.0

            # Backend ATR-based RR is 2:1
            rr_actual = 2.0

            mtf_15m = d
            mtf_1h = d
            mtf_4h = d
            for item in (signal.get("mtf") or []):
                tf = str(item.get("tf", "")).lower()
                sig = str(item.get("signal", "HOLD")).upper()
                m = "BULLISH" if sig == "BUY" else (
                    "BEARISH" if sig == "SELL" else "NEUTRAL"
                )
                if tf == "15m":
                    mtf_15m = m
                elif tf in ("1h",):
                    mtf_1h = m
                elif tf == "4h":
                    mtf_4h = m

            audit = signal.get("audit") or {}
            flow = audit.get("flow") or {}
            vol_data = audit.get("volume") or {}
            deriv = audit.get("derivatives") or {}

            def _f(v, default=0.0):
                try:
                    return float(v)
                except (TypeError, ValueError):
                    return default

            mm_footprint = abs(_f(flow.get("book_imbalance"))) > 0.15
            wall_break = False
            vol_change = _f(vol_data.get("roc_pct"))
            oi_change = _f(deriv.get("oi_change_pct"))
            vol_ratio = _f(audit.get("volatility_ratio"), 1.0) or 1.0

            trend_cont = 0.0
            for r in (audit.get("reasons") or []):
                rs = str(r).lower()
                if "persistent" in rs or "aligned" in rs or "continuation" in rs:
                    trend_cont += 0.35
            trend_cont = min(1.0, trend_cont)

            return SignalCandidate(
                symbol=symbol,
                direction=d,
                action=str(signal.get("action", "HOLD")).upper(),
                grade=grade,
                confidence=confidence,
                strength=strength,
                rr_actual=rr_actual,
                age_minutes=age_min,
                mtf_15m=mtf_15m,
                mtf_1h=mtf_1h,
                mtf_4h=mtf_4h,
                mm_footprint=mm_footprint,
                wall_break=wall_break,
                volume_change_pct=vol_change,
                oi_change_pct=oi_change,
                volatility_ratio=vol_ratio,
                trend_continuation=trend_cont,
            )
        except Exception:
            return None

    def _rank_watchlist(self, watchlist, summary):
        """Return list of (symbol, signal, size_pct) ordered best-first."""
        try:
            from app.strategies.best_pick_engine import BestPickEngine
            engine = BestPickEngine()
        except Exception as exc:
            summary.errors.append(f"bestpick_import: {exc!r}")
            out = []
            for sym in watchlist:
                sig = self._signal_for(sym)
                if sig is not None:
                    out.append((sym, sig, None))
            return out

        pairs = []
        for sym in watchlist:
            sig = self._signal_for(sym)
            if sig is None:
                continue
            cand = self._signal_to_candidate(sym, sig)
            if cand is None:
                continue
            pairs.append((sym, sig, cand))

        if not pairs:
            return []

        ranked = engine.rank([c for (_, _, c) in pairs])

        sym_to_pair = {p[0]: (p[0], p[1]) for p in pairs}
        out = []
        for r in ranked:
            s = r.candidate.symbol
            if s in sym_to_pair:
                sym, sig = sym_to_pair[s]
                out.append((sym, sig, r.position_size_pct))

        if out:
            top = ranked[0]
            summary.events.append(
                f"ranked {len(out)}/{len(pairs)}; "
                f"top={top.candidate.symbol} "
                f"score={top.rank_score:.3f} "
                f"size={top.position_size_pct}% "
                f"dur={top.duration_estimate_min}m"
            )
        return out

    # ============================================================
    # EVALUATE (modded: accepts pre-computed signal + size override)
    # ============================================================

    def _evaluate_symbol(
        self,
        symbol: str,
        summary: TickSummary,
        signal: dict | None = None,
        size_override_pct: float | None = None,
    ) -> None:
        if signal is None:
            signal = self._signal_for(symbol)
'''

# Old signature block
OLD_SIG = '''    def _evaluate_symbol(
        self, symbol: str, summary: TickSummary
    ) -> None:
        signal = self._signal_for(symbol)
'''


# ---------- SCAN LOOP ----------

OLD_SCAN = '''        for symbol in watchlist:
            summary.scanned += 1

            if len(self.broker.get_open_positions()) >= (
                self.config.max_open_positions
            ):
                summary.events.append(
                    "max_open_positions reached during scan"
                )
                break

            self._evaluate_symbol(symbol, summary)
'''

NEW_SCAN = '''        # NEW: rank universe, process best-first
        ranked = self._rank_watchlist(watchlist, summary)

        if ranked:
            for (symbol, signal, size_pct) in ranked:
                summary.scanned += 1
                if len(self.broker.get_open_positions()) >= (
                    self.config.max_open_positions
                ):
                    summary.events.append(
                        "max_open_positions reached during scan"
                    )
                    break
                self._evaluate_symbol(
                    symbol,
                    summary,
                    signal=signal,
                    size_override_pct=size_pct,
                )
        else:
            # Fallback to original order
            for symbol in watchlist:
                summary.scanned += 1
                if len(self.broker.get_open_positions()) >= (
                    self.config.max_open_positions
                ):
                    summary.events.append(
                        "max_open_positions reached during scan"
                    )
                    break
                self._evaluate_symbol(symbol, summary)
'''


# ---------- ALLOCATION ----------

OLD_ALLOC = '''        # Allocation
        allocation = allocate_capital(
            capital=capital,
            entry_price=price,
            stop_loss=sl_tp_result.stop_loss,
            risk_per_trade_pct=self.config.risk_per_trade_pct,
            max_position_pct=self.config.max_position_pct,
        )'''

NEW_ALLOC = '''        # Allocation
        _risk_pct = self.config.risk_per_trade_pct
        if size_override_pct is not None and size_override_pct > 0.0:
            _risk_pct = float(size_override_pct)
        allocation = allocate_capital(
            capital=capital,
            entry_price=price,
            stop_loss=sl_tp_result.stop_loss,
            risk_per_trade_pct=_risk_pct,
            max_position_pct=self.config.max_position_pct,
        )'''


def main():
    if not os.path.isfile(TARGET):
        print(f"ERROR: not found: {TARGET}")
        sys.exit(1)

    with open(TARGET, "r", encoding="utf-8") as f:
        src = f.read()

    if "_rank_watchlist" in src:
        print("ALREADY PATCHED. Skipping.")
        sys.exit(0)

    for name, anchor in (
        ("SIGNATURE", OLD_SIG),
        ("SCAN", OLD_SCAN),
        ("ALLOC", OLD_ALLOC),
    ):
        if anchor not in src:
            print(f"ERROR: {name} anchor not found.")
            sys.exit(1)

    # Backup
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET + f".bak_{ts}"
    shutil.copy2(TARGET, bak)
    print(f"BACKUP OK: {os.path.basename(bak)}")

    # Apply patches (order: SIGNATURE first, then SCAN, then ALLOC)
    src = src.replace(OLD_SIG, NEW_METHODS, 1)
    src = src.replace(OLD_SCAN, NEW_SCAN, 1)
    src = src.replace(OLD_ALLOC, NEW_ALLOC, 1)

    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(src)

    print(f"PATCHED: {TARGET}")
    print()
    print("Rollback:")
    print(f'  copy /Y "{bak}" "{TARGET}"')
    print()
    print("Next: server restart karo, phir tick chalao.")


if __name__ == "__main__":
    main()