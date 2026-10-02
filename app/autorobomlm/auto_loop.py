"""
ROBOMLM_PLUS - AutoROBOMLM Main Loop

Purpose:
    Orchestrate the safety pipeline:

        Signal  ->  Grade  ->  Objective  ->  Resource
              ->  Constraint  ->  Allocate  ->  SL/TP
              ->  Paper Broker  ->  Position

    And manage open positions:
        - SL hit   -> close
        - TP hit   -> close
        - D13 flip -> close

Design:
    - All dependencies are injected (no hidden imports).
    - Thread-safe state (simple lock).
    - Kill switch + mode manager are optional hooks.
    - Loop is start/stop-able.
    - Every tick returns an auditable result.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from threading import Lock, Thread, Event
from typing import Any, Callable, Optional

from app.autorobomlm.config import (
    AutoRobomlmConfig,
    GradeBand,
    ExecutionMode,
    WatchlistSource,
)
from app.autorobomlm.grade_evaluator import (
    GradeSource,
    evaluate_grade,
)
from app.autorobomlm.objective_gate import (
    ObjectiveDefinition,
    ObjectiveType,
    evaluate_objective,
)
from app.autorobomlm.resource_gate import (
    ResourceCheck,
    ResourceKind,
    evaluate_resources,
)
from app.autorobomlm.constraint_gate import (
    ConstraintCheck,
    ConstraintDisposition,
    ConstraintKind,
    evaluate_constraints,
)
from app.autorobomlm.capital_allocator import allocate_capital
from app.autorobomlm.sl_tp_calculator import (
    TradeDirection as SLTPDirection,
    calculate_sl_tp,
)
from app.autorobomlm.paper_broker import (
    PaperBroker,
    PositionStatus,
    TradeDirection,
)


LOOP_NAME = "AutoROBOMLM_Loop"
LOOP_VERSION = "1.0"


class LoopState(str, Enum):
    STOPPED = "STOPPED"
    RUNNING = "RUNNING"
    KILLED = "KILLED"


@dataclass
class TickSummary:
    started_at: datetime
    finished_at: datetime
    scanned: int = 0
    opened: int = 0
    closed: int = 0
    skipped_grade: int = 0
    skipped_gates: int = 0
    errors: list = field(default_factory=list)
    events: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat(),
            "scanned": self.scanned,
            "opened": self.opened,
            "closed": self.closed,
            "skipped_grade": self.skipped_grade,
            "skipped_gates": self.skipped_gates,
            "errors": list(self.errors),
            "events": list(self.events),
        }


class AutoRobomlmLoop:
    def __init__(
        self,
        *,
        config: AutoRobomlmConfig,
        signal_provider: Callable[[str], Optional[dict]],
        broker: PaperBroker,
        watchlist_provider: Callable[[], list[str]],
        capital_provider: Callable[[], float],
        kill_switch_provider: Optional[Callable[[], bool]] = None,
        mode_provider: Optional[Callable[[], ExecutionMode]] = None,
        symbol_meta_provider: Optional[
            Callable[[str], Optional[dict]]
        ] = None,
    ):
        config.validate()

        if not callable(signal_provider):
            raise ValueError("signal_provider must be callable.")
        if not isinstance(broker, PaperBroker):
            raise ValueError("broker must be a PaperBroker instance.")
        if not callable(watchlist_provider):
            raise ValueError("watchlist_provider must be callable.")
        if not callable(capital_provider):
            raise ValueError("capital_provider must be callable.")

        self.config = config
        self.signal_provider = signal_provider
        self.broker = broker
        self.watchlist_provider = watchlist_provider
        self.capital_provider = capital_provider
        self.kill_switch_provider = kill_switch_provider
        self.mode_provider = mode_provider
        self.symbol_meta_provider = symbol_meta_provider

        self._state = LoopState.STOPPED
        self._lock = Lock()
        self._stop_event = Event()
        self._thread: Optional[Thread] = None
        self._last_tick: Optional[TickSummary] = None
        self._tick_count = 0

    # ------------------------------------------------------------------
    # Public lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        with self._lock:
            if self._state == LoopState.RUNNING:
                return
            self._state = LoopState.RUNNING
            self._stop_event.clear()
            self._thread = Thread(
                target=self._run, daemon=True, name="AutoRobomlmLoop"
            )
            self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        with self._lock:
            if self._state == LoopState.RUNNING:
                self._state = LoopState.STOPPED

    def kill(self) -> None:
        with self._lock:
            self._state = LoopState.KILLED
        self._stop_event.set()

    def resume(self) -> None:
        with self._lock:
            if self._state == LoopState.KILLED:
                self._state = LoopState.STOPPED

    def status(self) -> dict:
        with self._lock:
            state = self._state
        return {
            "engine": LOOP_NAME,
            "version": LOOP_VERSION,
            "state": state.value,
            "tick_count": self._tick_count,
            "last_tick": (
                self._last_tick.to_dict() if self._last_tick else None
            ),
            "config": self.config.as_dict(),
            "open_positions": len(self.broker.get_open_positions()),
            "total_positions": len(self.broker.get_all_positions()),
        }

    def active_trades(self) -> list[dict]:
        return self.broker.mark_to_market()

    # ------------------------------------------------------------------
    # One manual tick (for testing)
    # ------------------------------------------------------------------

    def tick(self) -> TickSummary:
        return self._do_tick()

    # ------------------------------------------------------------------
    # Thread body
    # ------------------------------------------------------------------

    def _run(self) -> None:
        while not self._stop_event.is_set():
            with self._lock:
                current_state = self._state

            if current_state == LoopState.KILLED:
                break
            if current_state != LoopState.RUNNING:
                break

            try:
                self._do_tick()
            except Exception as exc:  # pragma: no cover
                # Never let an exception kill the loop silently.
                with self._lock:
                    if self._last_tick is not None:
                        self._last_tick.errors.append(
                            f"tick exception: {exc!r}"
                        )

            self._stop_event.wait(self.config.loop_interval_sec)

    # ------------------------------------------------------------------
    # Core tick
    # ------------------------------------------------------------------

    def _do_tick(self) -> TickSummary:
        started = datetime.now(timezone.utc)
        summary = TickSummary(
            started_at=started, finished_at=started
        )

        # Step 1 - kill switch
        if self._kill_switch_engaged():
            summary.events.append(
                "kill_switch engaged; tick skipped"
            )
            summary.finished_at = datetime.now(timezone.utc)
            self._record_tick(summary)
            return summary

        # Step 2 - manage existing positions
        self._manage_positions(summary)

        # Step 3 - respect max positions
        if len(self.broker.get_open_positions()) >= (
            self.config.max_open_positions
        ):
            summary.events.append(
                "max_open_positions reached; scan skipped"
            )
            summary.finished_at = datetime.now(timezone.utc)
            self._record_tick(summary)
            return summary

        # Step 4 - scan watchlist
        try:
            watchlist = list(self.watchlist_provider() or [])
        except Exception as exc:
            summary.errors.append(f"watchlist error: {exc!r}")
            summary.finished_at = datetime.now(timezone.utc)
            self._record_tick(summary)
            return summary

        # NEW: rank universe, process best-first
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

        summary.finished_at = datetime.now(timezone.utc)
        self._record_tick(summary)
        return summary

    # ------------------------------------------------------------------
    # Position management
    # ------------------------------------------------------------------

    def _manage_positions(self, summary: TickSummary) -> None:
        for position in self.broker.get_open_positions():
            price = self._price_for(position.symbol)
            if price is None:
                continue

            # Stop-loss
            if position.direction == TradeDirection.BUY:
                if price <= position.stop_loss:
                    self._close(position.position_id, "SL_HIT", summary)
                    continue
                if price >= position.take_profit:
                    self._close(position.position_id, "TP_HIT", summary)
                    continue
            else:
                if price >= position.stop_loss:
                    self._close(position.position_id, "SL_HIT", summary)
                    continue
                if price <= position.take_profit:
                    self._close(position.position_id, "TP_HIT", summary)
                    continue

            # D13 flip check
            signal = self._signal_for(position.symbol)
            if signal is None:
                continue

            signal_side = self._signal_side(signal)
            if signal_side is None:
                continue

            if signal_side != position.direction.value:
                # MIN HOLD: 5 min (noise filter)
                hold_ok = False
                try:
                    from datetime import datetime as _dt, timezone as _tz
                    opened_str = str(getattr(position, "opened_at", "") or "")
                    if opened_str:
                        opened = _dt.fromisoformat(
                            opened_str.replace("Z", "+00:00")
                        )
                        age_sec = (
                            _dt.now(_tz.utc) - opened
                        ).total_seconds()
                        hold_ok = age_sec >= 300.0
                except Exception:
                    hold_ok = True

                if not hold_ok:
                    continue

                # STRENGTH filter: only strong flip
                try:
                    flip_strength = float(
                        signal.get("strength")
                        or signal.get("decision_score")
                        or 0.0
                    )
                except (TypeError, ValueError):
                    flip_strength = 0.0

                if flip_strength < 55.0:
                    continue

                self._close(position.position_id, "D13_FLIP", summary)
                continue

    def _close(
        self,
        position_id: str,
        reason: str,
        summary: TickSummary,
    ) -> None:
        result = self.broker.close_position(
            position_id, reason=reason
        )
        if result.status.value == "FILLED":
            summary.closed += 1
            summary.events.append(
                f"closed {position_id} ({reason})"
            )
        else:
            summary.errors.append(
                f"close failed {position_id}: {result.reason or result.errors}"
            )

    # ------------------------------------------------------------------
    # Symbol evaluation
    # ------------------------------------------------------------------


    def _apply_strategy(self, signal: dict, symbol: str) -> tuple:
        """Strategy gate. Returns (allowed: bool, reason: str).

        Default strategy_id = "OLD" -> always allow (existing behavior).
        "DEEPSEEK" -> uses app.strategies.deepseek_strategy.DeepSeekStrategy.
        """
        sid = str(getattr(self.config, "strategy_id", "OLD") or "OLD").upper()

        if sid not in ("OLD", "DEEPSEEK"):
            return True, f"strategy_unknown_allow:{sid}"

        try:
            from app.strategies.base import StrategyInput
            if sid == "OLD":
                from app.strategies.chatgpt_strategy import ChatGPTStrategy
            else:
                from app.strategies.deepseek_strategy import DeepSeekStrategy
        except Exception as exc:
            return True, f"strategy_import_failed:{exc!r}"

        def _f(v, d=0.0):
            try:
                return float(v)
            except (TypeError, ValueError):
                return d

        direction_raw = str(signal.get("direction", "NEUTRAL")).upper()
        if direction_raw == "LONG":
            direction = "BULLISH"
        elif direction_raw == "SHORT":
            direction = "BEARISH"
        else:
            direction = "NEUTRAL"

        comps = signal.get("components") or {}
        sl_raw = signal.get("stop_loss")
        tp_raw = signal.get("take_profit")
        rr_raw = signal.get("risk_reward")

        inp = StrategyInput(
            symbol=symbol,
            timeframe=str(signal.get("timeframe", "1m")),
            direction=direction,
            action=str(signal.get("action", "HOLD")).upper(),
            strength=_f(signal.get("strength", signal.get("decision_score"))),
            confidence=_f(signal.get("confidence")),
            trade_quality=str(signal.get("trade_quality") or signal.get("grade") or "HOLD"),
            risk_level=str(signal.get("risk_level") or "LOW"),
            entry_price=_f(signal.get("entry_price")),
            stop_loss=_f(sl_raw) if sl_raw is not None else None,
            take_profit=_f(tp_raw) if tp_raw is not None else None,
            risk_reward=_f(rr_raw) if rr_raw is not None else None,
            expected_move_pct=_f(signal.get("expected_move_pct")),
            components={
                "flow": _f(comps.get("flow")),
                "derivative": _f(comps.get("derivative")),
                "volume": _f(comps.get("volume")),
                "obstacle": _f(comps.get("obstacle")),
                "context": _f(comps.get("context")),
                "regime": _f(comps.get("regime")),
            },
            warnings=tuple(signal.get("warnings") or ()),
            metadata={},
        )

        try:
            if sid == "OLD":
                out = ChatGPTStrategy().decide(inp)
            else:
                out = DeepSeekStrategy().decide(inp)
        except Exception as exc:
            return True, f"strategy_exception_allow:{exc!r}"

        if not out.entry_permission:
            reasons = ",".join(out.reason_codes) if out.reason_codes else "unknown"
            reason_text = f"strategy_reject:{reasons}"
            try:
                from app.strategies.comparison import log_strategy_decision
                log_strategy_decision(
                    symbol=symbol,
                    signal=signal,
                    allowed=False,
                    reason=reason_text,
                    strategy_id=sid,
                )
            except Exception:
                pass
            return False, reason_text

        reason_text = f"strategy_pass:{out.strategy_score}"
        try:
            from app.strategies.comparison import log_strategy_decision
            log_strategy_decision(
                symbol=symbol,
                signal=signal,
                allowed=True,
                reason=reason_text,
                strategy_id=sid,
            )
        except Exception:
            pass
        return True, reason_text


    def _entry_source(self) -> str:
        """Tag trades by active strategy. OLD keeps legacy tag."""
        sid = str(getattr(self.config, "strategy_id", "OLD") or "OLD").upper()
        if sid == "OLD":
            return "AUTOROBOMLM"
        return f"AUTOROBOMLM_{sid}"

    # ============================================================
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

        if signal is None:
            summary.events.append(f"{symbol}: no signal")
            return

        # Grade
        raw_score = self._extract_score(signal)
        if raw_score is None:
            summary.skipped_grade += 1
            summary.events.append(
                f"{symbol}: no score available"
            )
            return

        grade_result = evaluate_grade(
            score=raw_score,
            min_grade=self.config.min_grade,
            source=GradeSource.D13_DECISION,
        )

        if not grade_result.is_eligible:
            summary.skipped_grade += 1
            summary.events.append(
                f"{symbol}: grade ineligible "
                f"({grade_result.grade.value if grade_result.grade else 'NONE'})"
            )
            return

        # Direction
        direction = self._signal_side(signal)
        if direction is None:
            summary.skipped_gates += 1
            summary.events.append(f"{symbol}: no clear direction")
            return

        # Strategy gate (NEW; default OLD = pass-through)
        strategy_ok, strategy_reason = self._apply_strategy(signal, symbol)
        if not strategy_ok:
            summary.skipped_gates += 1
            summary.events.append(f"{symbol}: {strategy_reason}")
            return

        # Price
        price = self._price_for(symbol)
        if price is None:
            summary.skipped_gates += 1
            summary.events.append(f"{symbol}: no price")
            return

        # Objective gate
        objective_result = evaluate_objective(
            ObjectiveDefinition(
                objective_type=ObjectiveType.RISK_ADJUSTED_RETURN,
                metric="grade_score",
                version="1.0",
                thresholds={
                    "min_score": float(
                        self.config.min_score_required() or 0.0
                    ),
                    "risk_per_trade_pct": (
                        self.config.risk_per_trade_pct
                    ),
                },
                description=(
                    "AutoROBOMLM default objective: "
                    "risk-adjusted return filtered by grade."
                ),
            )
        )
        if not objective_result.passed:
            summary.skipped_gates += 1
            summary.events.append(
                f"{symbol}: objective gate closed"
            )
            return

        # Resource gate
        try:
            capital = float(self.capital_provider())
        except Exception as exc:
            summary.errors.append(f"capital error: {exc!r}")
            return

        resource_result = evaluate_resources(
            (
                ResourceCheck(
                    kind=ResourceKind.CAPITAL,
                    name="capital_available",
                    required=0.0,
                    available=max(0.0, capital),
                    unit="currency",
                ),
            )
        )
        if not resource_result.passed:
            summary.skipped_gates += 1
            summary.events.append(
                f"{symbol}: resource gate closed"
            )
            return

        # Constraint gate
        constraint_checks = [
            ConstraintCheck(
                name="mode_allows_execution",
                kind=ConstraintKind.MODE_POLICY,
                disposition=ConstraintDisposition.ALLOW,
                reason="mode policy check delegated to caller",
                source="auto_loop",
            ),
        ]

        constraint_result = evaluate_constraints(
            tuple(constraint_checks)
        )
        if not constraint_result.passed:
            summary.skipped_gates += 1
            summary.events.append(
                f"{symbol}: constraint gate closed"
            )
            return

        # SL/TP
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
        _risk_pct = self.config.risk_per_trade_pct
        if size_override_pct is not None and size_override_pct > 0.0:
            _risk_pct = float(size_override_pct)
        allocation = allocate_capital(
            capital=capital,
            entry_price=price,
            stop_loss=sl_tp_result.stop_loss,
            risk_per_trade_pct=_risk_pct,
            max_position_pct=self.config.max_position_pct,
        )
        if allocation.quantity is None:
            summary.errors.append(
                f"{symbol}: allocation failed "
                f"({allocation.errors or allocation.reasons})"
            )
            return

        # Paper fill
        fill = self.broker.open_position(
            symbol=symbol,
            direction=TradeDirection(direction),
            quantity=allocation.quantity,
            stop_loss=sl_tp_result.stop_loss,
            take_profit=sl_tp_result.take_profit,
            entry_grade=(
                grade_result.grade.value
                if grade_result.grade is not None
                else None
            ),
            entry_score=raw_score,
            entry_source=self._entry_source(),
        )
        if fill.position is None:
            summary.errors.append(
                f"{symbol}: fill rejected ({fill.reason or fill.errors})"
            )
            return

        summary.opened += 1
        summary.events.append(
            f"{symbol}: opened {direction} "
            f"qty={allocation.quantity} at {fill.fill_price}"
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _kill_switch_engaged(self) -> bool:
        if self.kill_switch_provider is None:
            return False
        try:
            return bool(self.kill_switch_provider())
        except Exception:
            # Fail-closed: if provider errors, treat as engaged.
            return True

    def _price_for(self, symbol: str) -> Optional[float]:
        try:
            price = self.broker.price_provider(symbol)
        except Exception:
            return None
        if price is None:
            return None
        try:
            price = float(price)
        except (TypeError, ValueError):
            return None
        if price <= 0.0:
            return None
        return price

    def _signal_for(self, symbol: str) -> Optional[dict]:
        try:
            return self.signal_provider(symbol)
        except Exception:
            return None

    @staticmethod
    def _extract_score(signal: dict) -> Optional[float]:
        if not isinstance(signal, dict):
            return None
        for key in ("decision_score", "score", "confidence"):
            if key in signal:
                value = signal[key]
                try:
                    value = float(value)
                except (TypeError, ValueError):
                    continue
                if value <= 1.0 and key == "confidence":
                    value *= 100.0
                return value
        return None

    @staticmethod
    def _signal_side(signal: dict) -> Optional[str]:
        if not isinstance(signal, dict):
            return None
        for key in ("signal", "decision", "direction"):
            value = signal.get(key)
            if value is None:
                continue
            text = str(value).strip().upper()
            if text in {"BUY", "LONG"}:
                return "BUY"
            if text in {"SELL", "SHORT"}:
                return "SELL"
        return None

    def _record_tick(self, summary: TickSummary) -> None:
        with self._lock:
            self._last_tick = summary
            self._tick_count += 1


__all__ = [
    "LOOP_NAME", "LOOP_VERSION",
    "LoopState", "TickSummary", "AutoRobomlmLoop",
]
