"""AutoROBOMLM installer part 8 - FastAPI router"""
from pathlib import Path

# Create the api/v1 directory path
API_DIR = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\api\v1")
API_DIR.mkdir(parents=True, exist_ok=True)

FILES = {}

FILES["autorobomlm_api.py"] = '''"""
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
        sl_atr_multiplier=1.5,
        tp_atr_multiplier=3.0,
        loop_interval_sec=60,
    )
    cfg.validate()
    return cfg


def _build_loop(cfg: AutoRobomlmConfig) -> AutoRobomlmLoop:
    """Create a fresh loop from config."""
    symbols = list(cfg.manual_watchlist) or ["BTC/USDT"]
    capital = 100000.0

    price_provider = make_price_provider()
    signal_provider = make_live_signal_provider()

    broker = PaperBroker(
        price_provider=price_provider,
        slippage_pct=0.0,
    )

    loop = AutoRobomlmLoop(
        config=cfg,
        signal_provider=signal_provider,
        broker=broker,
        watchlist_provider=lambda: list(symbols),
        capital_provider=lambda: float(capital),
    )
    return loop


def _ensure_state() -> None:
    """Lazily build loop + config + api."""
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


__all__ = ["router"]
'''

# Write
for filename, content in FILES.items():
    path = API_DIR / filename
    path.write_text(content, encoding="utf-8")
    print(f"WROTE: {path}")

print()
print("Done. Files created:")
for p in sorted(API_DIR.glob("autorobomlm_api.py")):
    print(f"  {p.name} ({p.stat().st_size} bytes)")

print()
print("Next steps:")
print("  1. Register router in your FastAPI main.py")
print("  2. Restart backend")
print("  3. Test:  curl http://127.0.0.1:8000/api/autorobomlm/health")
print()
print("To register:")
print("  In your FastAPI main.py (or wherever you include routers):")
print('      from app.api.v1.autorobomlm_api import router as autorobomlm_router')
print('      app.include_router(autorobomlm_router)')