"""
ROBOMLM_PLUS - AutoROBOMLM FastAPI Router

Exposes AutoRobomlmAPI over HTTP.

Endpoints:
    POST /api/autorobomlm/start
    POST /api/autorobomlm/stop
    POST /api/autorobomlm/kill
    POST /api/autorobomlm/resume
    POST /api/autorobomlm/tick
    POST /api/autorobomlm/config
    GET  /api/autorobomlm/status
    GET  /api/autorobomlm/positions
    GET  /api/autorobomlm/config
    GET  /api/autorobomlm/health

Lifecycle:
    A single AutoRobomlmLoop instance is created lazily
    on first use, wired to live_signal + Bybit price.
"""

from __future__ import annotations
from typing import Any, Optional

from fastapi import APIRouter, Body, HTTPException

from app.autorobomlm.config import (
    AutoRobomlmConfig,
    ExecutionMode,
    GradeBand,
    WatchlistSource,
)
from app.autorobomlm.auto_loop import AutoRobomlmLoop
from app.autorobomlm.paper_broker import PaperBroker
from app.autorobomlm.autorobomlm_api import AutoRobomlmAPI
from app.autorobomlm.signal_adapter import (
    make_live_signal_provider,
    make_price_provider,
)


from app.autorobomlm.portfolio_tracker import PortfolioTracker

# Existing account system (single source of truth)
from app.api.account_routes import _ACCOUNT

from pathlib import Path as _Path

_DATA_DIR = _Path(r"C:\Users\Administrator\ROBOMLM_PLUS\data\autorobomlm")
_DATA_DIR.mkdir(parents=True, exist_ok=True)

_PORTFOLIO_PERSIST = _DATA_DIR / "portfolio.json"


def _get_balance() -> float:
    """Read active-mode balance from existing account state."""
    try:
        from app.api.account_routes import _active_balance
        return float(_active_balance())
    except Exception:
        try:
            return float(_ACCOUNT.get("balance", 0.0))
        except (TypeError, ValueError):
            return 0.0


def _record_realized_pnl(pnl: float) -> None:
    """Write realized P&L into existing account state."""
    try:
        pnl = float(pnl)
    except (TypeError, ValueError):
        return
    _ACCOUNT["balance"] = float(_ACCOUNT.get("balance", 0.0)) + pnl
    _ACCOUNT["capital"] = _ACCOUNT["balance"]
    _ACCOUNT["today_pnl"] = float(_ACCOUNT.get("today_pnl", 0.0)) + pnl




# ============================================================
# GRADE HELPERS
# ============================================================

_GRADE_RANK = {
    "A+": 5,
    "A": 4,
    "B+": 3,
    "B": 2,
    "HOLD": 1,
}


def _classify_grade(score: float) -> str:
    """Classify score into grade band (matches frontend)."""
    try:
        s = float(score)
    except (TypeError, ValueError):
        return "HOLD"
    if s >= 75.0:
        return "A+"
    if s >= 55.0:
        return "A"
    if s >= 45.0:
        return "B+"
    if s >= 30.0:
        return "B"
    return "HOLD"


def _grade_at_least(actual: str, minimum: str) -> bool:
    return _GRADE_RANK.get(actual, 0) >= _GRADE_RANK.get(minimum, 0)


router = APIRouter(
    prefix="/api/autorobomlm",
    tags=["autorobomlm"],
)


# ---------------------------------------------------------------------
# Singleton loop holder
# ---------------------------------------------------------------------

_state: dict[str, Any] = {
    "loop": None,
    "config": None,
    "api": None,
    "broker": None,
    "portfolio": None,
}


def _build_default_config() -> AutoRobomlmConfig:
    """Sane defaults for first startup."""
    cfg = AutoRobomlmConfig(
        min_grade=GradeBand.B,
        execution_mode=ExecutionMode.DEMO,
        watchlist_source=WatchlistSource.MANUAL,
        manual_watchlist=("BTC/USDT",),
        max_open_positions=3,
        risk_per_trade_pct=1.0,
        max_position_pct=10.0,
        sl_atr_multiplier=2.0,
        tp_atr_multiplier=4.0,
        loop_interval_sec=60,
    )
    cfg.validate()
    return cfg


def _get_broker() -> PaperBroker:
    """Singleton broker â€” persists across config changes."""
    if _state["broker"] is None:
        _state["broker"] = PaperBroker(
            price_provider=make_price_provider(),
            slippage_pct=0.0,
        )
    return _state["broker"]





def _get_portfolio() -> PortfolioTracker:
    """Singleton portfolio â€” persisted to disk."""
    if _state["portfolio"] is None:
        _state["portfolio"] = PortfolioTracker(
            persist_path=_PORTFOLIO_PERSIST,
        )
    return _state["portfolio"]




def _dynamic_watchlist() -> list:
    """Fetch top symbols from discovery universe each call."""
    try:
        import urllib.request, json as _json
        url = "http://127.0.0.1:8000/api/discovery/universe"
        with urllib.request.urlopen(url, timeout=10) as r:
            data = _json.loads(r.read().decode("utf-8"))
        insts = data.get("data", {}).get("instruments", []) or []
        ranked = []
        for inst in insts:
            sym = inst.get("symbol")
            meta = inst.get("metadata") or {}
            score = meta.get("score") or 0
            if sym:
                ranked.append((float(score), sym))
        ranked.sort(reverse=True)
        top = [s for _, s in ranked[:15]]
        return top if top else ["BTC/USDT"]
    except Exception:
        return ["BTC/USDT"]


def _build_loop(cfg: AutoRobomlmConfig) -> AutoRobomlmLoop:
    """Create a new loop, reusing singleton broker + account."""
    symbols = list(cfg.manual_watchlist) or ["BTC/USDT"]

    broker = _get_broker()

    signal_provider = make_live_signal_provider()

    loop = AutoRobomlmLoop(
        config=cfg,
        signal_provider=signal_provider,
        broker=broker,
        watchlist_provider=_dynamic_watchlist,
        capital_provider=lambda: _get_balance(),
    )
    return loop



# PATCH: wrap broker.close_position to record to portfolio + account
_original_close = None


def _install_close_hook():
    global _original_close
    broker = _get_broker()
    if _original_close is None:
        _original_close = broker.close_position

    def wrapped_close(position_id, *, reason):
        result = _original_close(position_id, reason=reason)
        if result.position is not None and result.fill_price is not None:
            try:
                portfolio = _get_portfolio()
                trade = portfolio.record_close(
                    result.position, result.fill_price
                )
                _record_realized_pnl(trade.pnl)
            except Exception:
                pass
        return result

    broker.close_position = wrapped_close


def _ensure_state() -> None:
    """Lazily build loop + config + api."""
    _install_close_hook()
    if _state["api"] is not None:
        return

    cfg = _build_default_config()
    loop = _build_loop(cfg)

    _state["config"] = cfg
    _state["loop"] = loop
    _state["api"] = AutoRobomlmAPI(loop=loop, config=cfg)


# ---------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------

@router.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "engine": "AutoROBOMLM",
        "version": "1.0",
        "initialized": _state["api"] is not None,
    }


@router.post("/start")
def start() -> dict:
    _ensure_state()
    return _state["api"].start()


@router.post("/stop")
def stop() -> dict:
    _ensure_state()
    return _state["api"].stop()


@router.post("/kill")
def kill() -> dict:
    _ensure_state()
    return _state["api"].kill()


@router.post("/resume")
def resume() -> dict:
    _ensure_state()
    return _state["api"].resume()


@router.post("/tick")
def tick() -> dict:
    _ensure_state()
    return _state["api"].tick()


@router.get("/status")
def status() -> dict:
    _ensure_state()
    return _state["api"].status()


@router.get("/positions")
def positions() -> dict:
    _ensure_state()
    return _state["api"].positions()


@router.get("/config")
def get_config() -> dict:
    _ensure_state()
    return _state["api"].get_config()


@router.post("/config")
def update_config(payload: dict = Body(...)) -> dict:
    _ensure_state()
    result = _state["api"].update_config(payload)

    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result)

    # Rebuild loop because config changed
    new_cfg = _state["api"].config
    new_loop = _build_loop(new_cfg)

    _state["config"] = new_cfg
    _state["loop"] = new_loop
    _state["api"] = AutoRobomlmAPI(loop=new_loop, config=new_cfg)

    return result



@router.post("/strategy")
def set_strategy(payload: dict = Body(...)) -> dict:
    """Set active strategy: OLD (ChatGPT) | DEEPSEEK."""
    _ensure_state()
    sid = str(payload.get("strategy_id", "OLD")).upper()
    if sid not in ("OLD", "DEEPSEEK"):
        return {"ok": False, "error": f"invalid strategy_id: {sid}"}
    try:
        _state["config"].strategy_id = sid
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
    return {"ok": True, "strategy_id": sid}


@router.post("/manual")
def manual_trade(payload: dict = Body(...)) -> dict:
    """
    Manual trade: user explicitly clicks Take on an opportunity.

    Bypasses grade gate (user chose it) but still goes through:
      - objective gate
      - resource gate
      - constraint gate
      - capital allocator
      - SL/TP calculator
      - paper broker

    Body:
        {
            "symbol": "BTC/USDT",
            "direction": "LONG"   # or "SHORT"
        }
    """
    _ensure_state()

    symbol = str(payload.get("symbol") or "").strip()
    direction_raw = str(payload.get("direction") or "").strip().upper()

    # Grade info from caller (optional but recommended)
    entry_score = payload.get("entry_score")
    requested_min_grade = str(payload.get("min_grade") or "").strip().upper()

    entry_grade: Optional[str] = None
    if entry_score is not None:
        try:
            entry_grade = _classify_grade(float(entry_score))
        except (TypeError, ValueError):
            entry_grade = None

    # Grade gate: if both known, enforce
    if entry_grade and requested_min_grade in _GRADE_RANK:
        if not _grade_at_least(entry_grade, requested_min_grade):
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Grade {entry_grade} below minimum {requested_min_grade}. "
                    "Manual trade rejected by grade policy."
                ),
            )

    if not symbol:
        raise HTTPException(status_code=400, detail="symbol is required")

    if direction_raw not in {"LONG", "SHORT", "BUY", "SELL"}:
        raise HTTPException(
            status_code=400,
            detail=(
                "direction must be LONG/SHORT/BUY/SELL. "
                "NEUTRAL is not tradeable."
            ),
        )

    trade_direction = (
        "BUY" if direction_raw in {"LONG", "BUY"} else "SELL"
    )

    loop = _state["loop"]
    if loop is None:
        raise HTTPException(status_code=500, detail="loop not initialized")

    price = loop._price_for(symbol)
    if price is None:
        raise HTTPException(
            status_code=400,
            detail=f"No market price available for {symbol}",
        )

    # SL/TP
    from app.autorobomlm.sl_tp_calculator import (
        TradeDirection as SLTPDirection,
        calculate_sl_tp,
    )

    sl_tp = calculate_sl_tp(
        direction=SLTPDirection(trade_direction),
        entry_price=price,
        sl_atr_multiplier=loop.config.sl_atr_multiplier,
        tp_atr_multiplier=loop.config.tp_atr_multiplier,
    )
    if sl_tp.stop_loss is None:
        raise HTTPException(
            status_code=500, detail="SL/TP calculation failed"
        )

    # Allocation
    from app.autorobomlm.capital_allocator import allocate_capital

    try:
        capital = float(loop.capital_provider())
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"capital error: {exc}"
        )

    # Quantity override from caller
    quantity_override = payload.get("quantity")
    override_qty: Optional[float] = None
    if quantity_override is not None:
        try:
            q = float(quantity_override)
            if q > 0:
                override_qty = q
        except (TypeError, ValueError):
            pass

    if override_qty is not None:
        # Build a synthetic allocation result
        from app.autorobomlm.capital_allocator import AllocationResult, AllocatorStatus
        allocation = AllocationResult(
            status=AllocatorStatus.VALID,
            quantity=override_qty,
            position_value=override_qty * price,
            risk_amount=abs(price - sl_tp.stop_loss) * override_qty,
            stop_distance=abs(price - sl_tp.stop_loss),
            stop_distance_pct=(abs(price - sl_tp.stop_loss) / price * 100.0),
            capped_by_max_position=False,
            reasons=(f"Manual quantity override: {override_qty}",),
        )
    else:
        allocation = allocate_capital(
            capital=capital,
            entry_price=price,
            stop_loss=sl_tp.stop_loss,
            risk_per_trade_pct=loop.config.risk_per_trade_pct,
            max_position_pct=loop.config.max_position_pct,
        )
        if allocation.quantity is None:
            raise HTTPException(
                status_code=400,
                detail="Allocation failed: "
                + "; ".join(allocation.errors or allocation.reasons),
            )

    # Fill
    from app.autorobomlm.paper_broker import TradeDirection as BrokerDirection

    fill = loop.broker.open_position(
        symbol=symbol,
        direction=BrokerDirection(trade_direction),
        quantity=allocation.quantity,
        stop_loss=sl_tp.stop_loss,
        take_profit=sl_tp.take_profit,
        entry_grade=entry_grade,
        entry_score=(
            float(entry_score) if entry_score is not None else None
        ),
        entry_source="MANUAL",
    )

    if fill.position is None:
        raise HTTPException(
            status_code=400,
            detail="Fill rejected: " + (fill.reason or "unknown"),
        )

    return {
        "ok": True,
        "action": "manual_trade",
        "position": fill.position.to_dict(current_price=price),
        "fill_price": fill.fill_price,
        "reason": fill.reason,
    }


# ============================================================
# PORTFOLIO ENDPOINTS
# ============================================================

@router.get("/portfolio/summary")
def portfolio_summary() -> dict:
    _ensure_state()
    portfolio = _get_portfolio()
    broker = _get_broker()

    # Unrealized P&L from open positions
    unrealized = 0.0
    for p in broker.get_open_positions():
        price = broker.price_provider(p.symbol)
        if price is not None:
            unrealized += p.pnl(price)

    portfolio_stats = portfolio.summary()
    balance = _get_balance()
    equity = balance + unrealized

    return {
        "ok": True,
        "portfolio": portfolio_stats,
        "account": {
            "balance": balance,
            "mode": _ACCOUNT.get("mode", "PAPER"),
            "currency": _ACCOUNT.get("currency", "INR"),
            "today_pnl": _ACCOUNT.get("today_pnl", 0.0),
        },
        "unrealized_pnl": round(unrealized, 6),
        "equity": round(equity, 6),
    }


@router.get("/portfolio/trades")
def portfolio_trades(limit: int = 100) -> dict:
    _ensure_state()
    return {
        "ok": True,
        "trades": _get_portfolio().trades(limit=limit),
    }

# ============================================================
# POSITION CLOSE ENDPOINTS
# ============================================================

@router.post("/close")
def close_position(payload: dict = Body(...)) -> dict:
    """
    Manually close a single position.

    Body: {"position_id": "...", "reason": "MANUAL_CLOSE"}
    """
    _ensure_state()

    position_id = str(payload.get("position_id") or "").strip()
    reason = str(payload.get("reason") or "MANUAL_CLOSE")

    if not position_id:
        raise HTTPException(
            status_code=400, detail="position_id is required"
        )

    loop = _state["loop"]
    broker = loop.broker

    existing = broker.get_position(position_id)
    if existing is None:
        raise HTTPException(
            status_code=404,
            detail=f"Position not found: {position_id}",
        )
    if existing.status.value == "CLOSED":
        raise HTTPException(
            status_code=400, detail="Position already closed"
        )

    result = broker.close_position(position_id, reason=reason)
    if result.position is None:
        raise HTTPException(
            status_code=400,
            detail="Close failed: " + (result.reason or "unknown"),
        )

    return {
        "ok": True,
        "action": "close",
        "position": result.position.to_dict(),
        "fill_price": result.fill_price,
        "reason": result.reason,
    }


@router.post("/close-all")
def close_all_positions(payload: dict = Body(default={})) -> dict:
    """
    Close ALL open positions. Emergency control.

    Body (optional): {"reason": "EMERGENCY_CLOSE"}
    """
    _ensure_state()

    reason = str(payload.get("reason") or "CLOSE_ALL")

    loop = _state["loop"]
    broker = loop.broker

    open_positions = list(broker.get_open_positions())
    results = []
    failed = []

    for pos in open_positions:
        res = broker.close_position(pos.position_id, reason=reason)
        if res.position is not None:
            results.append(
                {
                    "position_id": pos.position_id,
                    "symbol": pos.symbol,
                    "pnl": res.position.pnl(
                        res.fill_price or pos.entry_price
                    ),
                    "fill_price": res.fill_price,
                }
            )
        else:
            failed.append(
                {
                    "position_id": pos.position_id,
                    "reason": res.reason or "unknown",
                }
            )

    return {
        "ok": True,
        "action": "close_all",
        "closed_count": len(results),
        "failed_count": len(failed),
        "closed": results,
        "failed": failed,
    }


# ============================================================
# TESTING TOOL â€” tight SL for auto-exit validation
# ============================================================

@router.post("/debug/tight-sl")
def debug_tight_sl(payload: dict = Body(...)) -> dict:
    """
    Open a position with a very tight stop-loss (0.1% away)
    so the auto-loop should close it within seconds.

    Body: {"symbol": "BTC/USDT", "direction": "LONG"}
    """
    _ensure_state()

    symbol = str(payload.get("symbol") or "BTC/USDT").strip()
    direction_raw = str(payload.get("direction") or "LONG").strip().upper()

    if direction_raw not in {"LONG", "SHORT", "BUY", "SELL"}:
        raise HTTPException(
            status_code=400, detail="direction must be LONG/SHORT"
        )

    trade_direction = (
        "BUY" if direction_raw in {"LONG", "BUY"} else "SELL"
    )

    loop = _state["loop"]
    broker = loop.broker

    price = loop._price_for(symbol)
    if price is None:
        raise HTTPException(
            status_code=400, detail=f"No price for {symbol}"
        )

    # Tight SL: 0.1% from entry
    tight_distance = price * 0.001

    if trade_direction == "BUY":
        stop_loss = price - tight_distance
        take_profit = price + tight_distance * 5
    else:
        stop_loss = price + tight_distance
        take_profit = price - tight_distance * 5

    # Small qty so risk is trivial
    qty = 0.001

    fill = broker.open_position(
        symbol=symbol,
        direction=broker._open_position_direction(trade_direction)
        if hasattr(broker, "_open_position_direction")
        else __import__(
            "app.autorobomlm.paper_broker",
            fromlist=["TradeDirection"],
        ).TradeDirection(trade_direction),
        quantity=qty,
        stop_loss=stop_loss,
        take_profit=take_profit,
        entry_grade="DEBUG",
        entry_score=0.0,
        entry_source="DEBUG",
    )

    if fill.position is None:
        raise HTTPException(
            status_code=400,
            detail="Fill failed: " + (fill.reason or "unknown"),
        )

    return {
        "ok": True,
        "action": "debug_tight_sl",
        "position": fill.position.to_dict(current_price=price),
        "fill_price": fill.fill_price,
        "hint": (
            "SL is ~0.1% away. Start loop or run tick; "
            "auto-exit should close this quickly."
        ),
    }

__all__ = ["router"]

