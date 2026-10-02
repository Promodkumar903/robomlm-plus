"""
ROBOMLM_PLUS - AutoROBOMLM REST API

Endpoints (FastAPI-style router, framework-agnostic via plain dicts):
    POST /api/autorobomlm/start
    POST /api/autorobomlm/stop
    POST /api/autorobomlm/kill
    POST /api/autorobomlm/resume
    POST /api/autorobomlm/tick       (one manual tick)
    POST /api/autorobomlm/config     (update config)
    GET  /api/autorobomlm/status
    GET  /api/autorobomlm/positions
    GET  /api/autorobomlm/config

The API layer is thin: it does not contain trading logic.
All behavior is delegated to AutoRobomlmLoop.
"""

from __future__ import annotations
from typing import Any, Callable, Optional

from app.autorobomlm.auto_loop import AutoRobomlmLoop
from app.autorobomlm.config import (
    AutoRobomlmConfig,
    GradeBand,
    WatchlistSource,
    ExecutionMode,
)


API_NAME = "AutoROBOMLM_API"
API_VERSION = "1.0"


class AutoRobomlmAPI:
    """
    Thin API wrapper around AutoRobomlmLoop.

    This class is intentionally framework-agnostic.
    A FastAPI router can be attached later without
    changing any business logic here.
    """

    def __init__(
        self,
        *,
        loop: AutoRobomlmLoop,
        config: AutoRobomlmConfig,
        on_config_change: Optional[Callable[[AutoRobomlmConfig], None]] = None,
    ):
        if not isinstance(loop, AutoRobomlmLoop):
            raise ValueError("loop must be an AutoRobomlmLoop.")
        if not isinstance(config, AutoRobomlmConfig):
            raise ValueError("config must be an AutoRobomlmConfig.")

        self.loop = loop
        self.config = config
        self.on_config_change = on_config_change

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> dict[str, Any]:
        self.loop.start()
        return {
            "ok": True,
            "action": "start",
            "status": self.loop.status(),
        }

    def stop(self) -> dict[str, Any]:
        self.loop.stop()
        return {
            "ok": True,
            "action": "stop",
            "status": self.loop.status(),
        }

    def kill(self) -> dict[str, Any]:
        self.loop.kill()
        return {
            "ok": True,
            "action": "kill",
            "status": self.loop.status(),
        }

    def resume(self) -> dict[str, Any]:
        self.loop.resume()
        return {
            "ok": True,
            "action": "resume",
            "status": self.loop.status(),
        }

    def tick(self) -> dict[str, Any]:
        summary = self.loop.tick()
        return {
            "ok": True,
            "action": "tick",
            "summary": summary.to_dict(),
        }

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    def status(self) -> dict[str, Any]:
        return {
            "ok": True,
            "status": self.loop.status(),
        }

    def positions(self) -> dict[str, Any]:
        return {
            "ok": True,
            "positions": self.loop.active_trades(),
            "all_positions": [
                p.to_dict()
                for p in self.loop.broker.get_all_positions()
            ],
        }

    def get_config(self) -> dict[str, Any]:
        return {
            "ok": True,
            "config": self.config.as_dict(),
        }

    # ------------------------------------------------------------------
    # Config update
    # ------------------------------------------------------------------

    def update_config(
        self, payload: dict[str, Any]
    ) -> dict[str, Any]:
        try:
            new_config = AutoRobomlmConfig.from_dict(payload)
        except Exception as exc:
            return {
                "ok": False,
                "action": "config",
                "error": str(exc),
            }

        self.config = new_config
        self.loop.config = new_config

        if self.on_config_change is not None:
            try:
                self.on_config_change(new_config)
            except Exception:
                pass

        return {
            "ok": True,
            "action": "config",
            "config": new_config.as_dict(),
        }

    # ------------------------------------------------------------------
    # Endpoint contract (for FastAPI wiring later)
    # ------------------------------------------------------------------

    @staticmethod
    def endpoints() -> list[dict[str, Any]]:
        """
        Describe available endpoints for registration.
        """
        return [
            {"method": "POST", "path": "/api/autorobomlm/start"},
            {"method": "POST", "path": "/api/autorobomlm/stop"},
            {"method": "POST", "path": "/api/autorobomlm/kill"},
            {"method": "POST", "path": "/api/autorobomlm/resume"},
            {"method": "POST", "path": "/api/autorobomlm/tick"},
            {"method": "POST", "path": "/api/autorobomlm/config"},
            {"method": "GET",  "path": "/api/autorobomlm/status"},
            {"method": "GET",  "path": "/api/autorobomlm/positions"},
            {"method": "GET",  "path": "/api/autorobomlm/config"},
        ]

    def dispatch(
        self,
        method: str,
        path: str,
        payload: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Minimal dispatcher for manual testing without FastAPI.

        Returns a dict response; never raises.
        """
        method = method.strip().upper()
        path = path.strip().rstrip("/")
        payload = payload or {}

        try:
            if method == "POST" and path.endswith("/start"):
                return self.start()
            if method == "POST" and path.endswith("/stop"):
                return self.stop()
            if method == "POST" and path.endswith("/kill"):
                return self.kill()
            if method == "POST" and path.endswith("/resume"):
                return self.resume()
            if method == "POST" and path.endswith("/tick"):
                return self.tick()
            if method == "POST" and path.endswith("/config"):
                return self.update_config(payload)
            if method == "GET" and path.endswith("/status"):
                return self.status()
            if method == "GET" and path.endswith("/positions"):
                return self.positions()
            if method == "GET" and path.endswith("/config"):
                return self.get_config()
        except Exception as exc:
            return {
                "ok": False,
                "error": str(exc),
                "method": method,
                "path": path,
            }

        return {
            "ok": False,
            "error": f"Unknown route: {method} {path}",
        }


__all__ = [
    "API_NAME", "API_VERSION",
    "AutoRobomlmAPI",
]
