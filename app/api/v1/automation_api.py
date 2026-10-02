"""
ROBOMLM_PLUS
Automation API (AUTOROBOMLM)

Backend endpoints powering the AutoROBOMLM page.

This layer:
- Exposes real, authoritative state from automation managers.
- Never fabricates automation decisions, orders, or trade signals.
- Keeps execution authority delegated to ExecutionManager +
  AutomationRisk + KillSwitch + CAS + D13.

Endpoints:
    GET /api/automation/status
    GET /api/automation/readiness
    GET /api/automation/controls
    GET /api/automation/events
    GET /api/automation/history
    GET /api/automation/plus
    GET /api/live/candles/{symbol}
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests
from fastapi import APIRouter, HTTPException, Query


# ============================================================
# ROUTER
# ============================================================

automation_router = APIRouter(
    prefix="/automation",
    tags=["automation"],
)

router = automation_router

live_router = APIRouter(
    prefix="/live",
    tags=["live"],
)


# ============================================================
# BACKEND MANAGER IMPORTS (soft — engine may not be wired yet)
# ============================================================

def _safe_import(path: str, symbol: str) -> Any:
    try:
        module = __import__(path, fromlist=[symbol])
        return getattr(module, symbol, None)
    except Exception:
        return None


AutomationEngine = _safe_import(
    "app.autorobimlm.automation_engine",
    "AutomationEngine",
)
ExecutionManager = _safe_import(
    "app.autorobimlm.execution_manager",
    "ExecutionManager",
)
OrderManager = _safe_import(
    "app.autorobimlm.order_manager",
    "OrderManager",
)
PositionManager = _safe_import(
    "app.autorobimlm.position_manager",
    "PositionManager",
)
KillSwitch = _safe_import(
    "app.autorobimlm.kill_switch",
    "KillSwitch",
)
ReconciliationEngine = _safe_import(
    "app.autorobimlm.reconciliation_engine",
    "ReconciliationEngine",
)
AutomationRisk = _safe_import(
    "app.autorobimlm.automation_risk",
    "AutomationRisk",
)
StrategyRunner = _safe_import(
    "app.autorobimlm.strategy_runner",
    "StrategyRunner",
)
ModeManager = _safe_import(
    "app.autorobimlm.mode_manager",
    "ModeManager",
)


# ============================================================
# RUNTIME SINGLETON
# ============================================================

class AutomationRuntime:
    """
    Holds the singleton manager instances for the automation surface.

    No order is placed, no strategy is executed, no risk check is
    bypassed by holding these references. This class only gives the
    API a stable handle to query real state.
    """

    def __init__(self) -> None:
        self.automation = AutomationEngine() if AutomationEngine else None
        self.execution = ExecutionManager() if ExecutionManager else None
        self.orders = OrderManager() if OrderManager else None
        self.positions = PositionManager() if PositionManager else None
        self.kill_switch = KillSwitch() if KillSwitch else None
        self.reconciliation = (
            ReconciliationEngine() if ReconciliationEngine else None
        )
        self.risk = AutomationRisk() if AutomationRisk else None
        self.strategies = StrategyRunner() if StrategyRunner else None
        self.mode = ModeManager() if ModeManager else None

        self._event_log: List[Dict[str, Any]] = []
        self._started_at = datetime.now(timezone.utc)
        self._record(
            "SYSTEM_BOOT",
            "INFO",
            "Automation runtime initialised.",
        )

    # ------------------------------------------------------------------
    # EVENT LOG (in-memory; backend authoritative)
    # ------------------------------------------------------------------

    def _record(
        self,
        event_type: str,
        severity: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._event_log.append(
            {
                "id": f"EVT-{len(self._event_log) + 1:06d}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": event_type,
                "severity": severity,
                "message": message,
                "metadata": metadata or {},
            }
        )

    def events(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._event_log[-limit:][::-1]

    def uptime_seconds(self) -> float:
        return (
            datetime.now(timezone.utc) - self._started_at
        ).total_seconds()

    # ------------------------------------------------------------------
    # SNAPSHOT BUILDERS
    # ------------------------------------------------------------------

    def _manager_available(self) -> Dict[str, bool]:
        return {
            "automation_engine": self.automation is not None,
            "execution_manager": self.execution is not None,
            "order_manager": self.orders is not None,
            "position_manager": self.positions is not None,
            "kill_switch": self.kill_switch is not None,
            "reconciliation_engine": self.reconciliation is not None,
            "automation_risk": self.risk is not None,
            "strategy_runner": self.strategies is not None,
            "mode_manager": self.mode is not None,
        }

    def status(self) -> Dict[str, Any]:
        managers = self._manager_available()
        any_wired = any(managers.values())

        kill_enabled = False
        if self.kill_switch is not None:
            try:
                kill_enabled = bool(self.kill_switch.is_enabled())
            except Exception:
                kill_enabled = False

        current_mode = "UNKNOWN"
        if self.mode is not None:
            try:
                current_mode = self.mode.current_mode
            except Exception:
                current_mode = "UNKNOWN"

        running = any_wired and not kill_enabled

        return {
            "status": "READY" if any_wired else "NOT_INITIALIZED",
            "state": "RUNNING" if running else "IDLE",
            "running": running,
            "enabled": any_wired,
            "mode": current_mode,
            "kill_switch": {
                "enabled": kill_enabled,
            },
            "managers": managers,
            "uptime_seconds": round(self.uptime_seconds(), 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def readiness(self) -> Dict[str, Any]:
        managers = self._manager_available()

        checks = [
            {
                "id": "managers_loaded",
                "description": "Automation managers loaded",
                "passed": all(managers.values()),
            },
            {
                "id": "kill_switch",
                "description": "Kill switch available and not engaged",
                "passed": (
                    self.kill_switch is not None
                    and not self.kill_switch.is_enabled()
                ),
            },
            {
                "id": "mode_set",
                "description": "Operating mode configured",
                "passed": (
                    self.mode is not None
                    and self.mode.current_mode
                    in {"PAPER", "DEMO", "LIVE"}
                ),
            },
            {
                "id": "risk_configured",
                "description": "Automation risk layer loaded",
                "passed": self.risk is not None,
            },
            {
                "id": "execution_bound",
                "description": "Execution manager loaded",
                "passed": self.execution is not None,
            },
        ]

        blockers = [c["id"] for c in checks if not c["passed"]]
        ready = len(blockers) == 0

        return {
            "ready": ready,
            "status": "READY" if ready else "NOT_READY",
            "state": "READY" if ready else "NOT_READY",
            "checks": checks,
            "blockers": blockers,
            "reasons": [
                c["description"]
                for c in checks
                if not c["passed"]
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def controls(self) -> Dict[str, Any]:
        mode = "UNKNOWN"
        if self.mode is not None:
            try:
                mode = self.mode.current_mode
            except Exception:
                mode = "UNKNOWN"

        kill_enabled = False
        if self.kill_switch is not None:
            try:
                kill_enabled = bool(self.kill_switch.is_enabled())
            except Exception:
                kill_enabled = False

        return {
            "enabled": True,
            "running": not kill_enabled,
            "mode": mode,
            "controls": {
                "modes": ["PAPER", "DEMO", "LIVE"],
                "current_mode": mode,
                "kill_switch": kill_enabled,
                "can_execute_live": (
                    mode == "LIVE" and not kill_enabled
                ),
            },
            "permissions": {
                "place_orders": False,
                "modify_risk": False,
                "bypass_cas": False,
                "note": (
                    "Frontend is display-only. Order placement, risk "
                    "modification and CAS bypass are never permitted."
                ),
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def plus(self) -> Dict[str, Any]:
        orders_count = 0
        positions_count = 0
        tasks_count = 0
        strategies_count = 0
        if self.orders is not None:
            try:
                orders_count = self.orders.count()
            except Exception:
                orders_count = 0
        if self.positions is not None:
            try:
                positions_count = self.positions.count()
            except Exception:
                positions_count = 0
        if self.automation is not None:
            try:
                tasks_count = self.automation.task_count()
            except Exception:
                tasks_count = 0
        if self.strategies is not None:
            try:
                strategies_count = len(
                    self.strategies.registered_strategies()
                )
            except Exception:
                strategies_count = 0

        return {
            "status": self.status(),
            "readiness": self.readiness(),
            "controls": self.controls(),
            "orders_count": orders_count,
            "positions_count": positions_count,
            "tasks_count": tasks_count,
            "strategies_count": strategies_count,
            "events_count": len(self._event_log),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


runtime = AutomationRuntime()


# ============================================================
# ENDPOINTS — /api/automation
# ============================================================

@automation_router.get("/status")
def automation_status() -> Dict[str, Any]:
    return runtime.status()


@automation_router.get("/readiness")
def automation_readiness() -> Dict[str, Any]:
    return runtime.readiness()


@automation_router.get("/controls")
def automation_controls() -> Dict[str, Any]:
    return runtime.controls()


@automation_router.get("/events")
def automation_events(
    limit: int = Query(default=50, ge=1, le=500),
) -> Dict[str, Any]:
    events = runtime.events(limit=limit)
    return {
        "items": events,
        "events": events,
        "total": len(events),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@automation_router.get("/history")
def automation_history(
    limit: int = Query(default=100, ge=1, le=500),
) -> Dict[str, Any]:
    events = runtime.events(limit=limit)
    return {
        "items": events,
        "history": events,
        "total": len(events),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@automation_router.get("/plus")
def automation_plus() -> Dict[str, Any]:
    return runtime.plus()


# ============================================================
# ENDPOINT — /api/live/candles/{symbol}
# ============================================================

BINANCE_BASE = os.getenv(
    "BINANCE_BASE_URL",
    "https://api.binance.com",
)

_TIMEFRAME_MAP: Dict[str, str] = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
    "1h": "1h",
    "4h": "4h",
    "1d": "1d",
}


def _to_binance_symbol(symbol: str) -> str:
    return symbol.replace("/", "").replace("-", "").upper()


@live_router.get("/candles/{symbol}")
def live_candles(
    symbol: str,
    timeframe: str = Query(default="1m"),
    limit: int = Query(default=200, ge=10, le=1000),
) -> Dict[str, Any]:
    """
    Live candle feed for the chart.

    Currently routed to Binance public API for CRYPTO symbols.
    Non-crypto symbols will fail gracefully — the frontend
    already handles that path with an empty chart.
    """
    interval = _TIMEFRAME_MAP.get(timeframe.lower())
    if interval is None:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported timeframe: {timeframe}",
        )

    binance_symbol = _to_binance_symbol(symbol)
    url = f"{BINANCE_BASE}/api/v3/klines"

    params = {
        "symbol": binance_symbol,
        "interval": interval,
        "limit": limit,
    }

    try:
        response = requests.get(url, params=params, timeout=10.0)

        if response.status_code != 200:
            return {
                "symbol": symbol,
                "timeframe": timeframe,
                "candles": [],
                "source": "binance",
                "error": (
                    f"Provider returned HTTP {response.status_code}"
                ),
            }

        raw = response.json()

    except Exception as exc:
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "candles": [],
            "source": "binance",
            "error": str(exc),
        }

    candles: List[Dict[str, Any]] = []
    for row in raw or []:
        if not isinstance(row, list) or len(row) < 6:
            continue
        try:
            candles.append(
                {
                    "time": int(row[0]),
                    "open": float(row[1]),
                    "high": float(row[2]),
                    "low": float(row[3]),
                    "close": float(row[4]),
                    "volume": float(row[5]),
                }
            )
        except (TypeError, ValueError):
            continue

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "candles": candles,
        "source": "binance",
        "count": len(candles),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


__all__ = [
    "automation_router",
    "live_router",
    "router",
]