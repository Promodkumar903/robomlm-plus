"""
ROBOMLM_PLUS - AutoROBOMLM Configuration Schema

Modes:
    DEMO  = paper trading (fake money, real prices) - testing
    LIVE  = real money (real broker)

LIVE requires explicit user confirmation (live_confirmed=True).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

CONFIG_ENGINE_NAME = "AutoROBOMLM_Config"
CONFIG_ENGINE_VERSION = "1.1"


class GradeBand(str, Enum):
    A_PLUS = "A+"
    A = "A"
    B_PLUS = "B+"
    B = "B"
    HOLD = "HOLD"


class WatchlistSource(str, Enum):
    FAVORITES = "FAVORITES"
    DISCOVERY_TOP10 = "DISCOVERY_TOP10"
    MANUAL = "MANUAL"


class ExecutionMode(str, Enum):
    """
    Execution mode.

    DEMO = paper trading, fake money, real prices (safe default)
    LIVE = real money (requires explicit confirmation)
    """

    DEMO = "DEMO"
    LIVE = "LIVE"


@dataclass(frozen=True)
class GradeBands:
    a_plus_min: float = 75.0
    a_min: float = 55.0
    b_plus_min: float = 45.0
    b_min: float = 30.0

    def validate(self) -> None:
        values = (
            self.a_plus_min, self.a_min,
            self.b_plus_min, self.b_min,
        )
        for value in values:
            if not (0.0 <= value <= 100.0):
                raise ValueError("Grade band thresholds must be 0..100.")
        if not (
            self.a_plus_min > self.a_min
            > self.b_plus_min > self.b_min
        ):
            raise ValueError("Grade bands must be strictly descending.")

    def classify(self, score: float) -> GradeBand:
        if score >= self.a_plus_min:
            return GradeBand.A_PLUS
        if score >= self.a_min:
            return GradeBand.A
        if score >= self.b_plus_min:
            return GradeBand.B_PLUS
        if score >= self.b_min:
            return GradeBand.B
        return GradeBand.HOLD

    def min_score_for(self, grade: GradeBand):
        if grade == GradeBand.A_PLUS:
            return self.a_plus_min
        if grade == GradeBand.A:
            return self.a_min
        if grade == GradeBand.B_PLUS:
            return self.b_plus_min
        if grade == GradeBand.B:
            return self.b_min
        return None

    def as_dict(self):
        return {
            "A+": (self.a_plus_min, 100.0),
            "A": (self.a_min, self.a_plus_min),
            "B+": (self.b_plus_min, self.a_min),
            "B": (self.b_min, self.b_plus_min),
            "HOLD": (0.0, self.b_min),
        }


DEFAULT_GRADE_BANDS = GradeBands()


@dataclass
class AutoRobomlmConfig:
    min_grade: GradeBand = GradeBand.A

    # NEW: strategy selector. OLD = existing behavior. DEEPSEEK = strategy layer.
    strategy_id: str = "OLD"

    execution_mode: ExecutionMode = ExecutionMode.DEMO

    # LIVE mode requires explicit user confirmation.
    # This is a safety gate. Do not flip it in code paths
    # other than the config update endpoint with user intent.
    live_confirmed: bool = False

    watchlist_source: WatchlistSource = WatchlistSource.FAVORITES
    manual_watchlist: tuple = ()

    max_open_positions: int = 5
    risk_per_trade_pct: float = 1.0
    max_position_pct: float = 10.0

    sl_atr_multiplier: float = 2.0
    tp_atr_multiplier: float = 4.0

    loop_interval_sec: int = 60

    grade_bands: GradeBands = field(
        default_factory=lambda: DEFAULT_GRADE_BANDS
    )
    metadata: Mapping = field(default_factory=dict)

    def validate(self) -> None:
        if not isinstance(self.min_grade, GradeBand):
            raise ValueError("min_grade must be a GradeBand.")
        if not isinstance(self.execution_mode, ExecutionMode):
            raise ValueError(
                "execution_mode must be an ExecutionMode."
            )
        if not isinstance(self.watchlist_source, WatchlistSource):
            raise ValueError(
                "watchlist_source must be a WatchlistSource."
            )
        if (
            self.watchlist_source == WatchlistSource.MANUAL
            and not self.manual_watchlist
        ):
            raise ValueError(
                "manual_watchlist cannot be empty when "
                "watchlist_source is MANUAL."
            )
        if self.max_open_positions < 1:
            raise ValueError("max_open_positions must be >= 1.")
        if not (0.0 < self.risk_per_trade_pct <= 100.0):
            raise ValueError("risk_per_trade_pct must be (0, 100].")
        if not (0.0 < self.max_position_pct <= 100.0):
            raise ValueError("max_position_pct must be (0, 100].")
        if self.risk_per_trade_pct > self.max_position_pct:
            raise ValueError(
                "risk_per_trade_pct cannot exceed max_position_pct."
            )
        if self.sl_atr_multiplier <= 0.0:
            raise ValueError("sl_atr_multiplier must be > 0.")
        if self.tp_atr_multiplier <= 0.0:
            raise ValueError("tp_atr_multiplier must be > 0.")
        if self.loop_interval_sec < 1:
            raise ValueError("loop_interval_sec must be >= 1.")

        # LIVE safety gate
        if (
            self.execution_mode == ExecutionMode.LIVE
            and not self.live_confirmed
        ):
            raise ValueError(
                "LIVE mode requires live_confirmed=True. "
                "This is a safety gate."
            )

        self.grade_bands.validate()

    def min_score_required(self):
        return self.grade_bands.min_score_for(self.min_grade)

    def is_score_eligible(self, score: float) -> bool:
        required = self.min_score_required()
        if required is None:
            return False
        return float(score) >= required

    def is_live(self) -> bool:
        return self.execution_mode == ExecutionMode.LIVE

    def is_demo(self) -> bool:
        return self.execution_mode == ExecutionMode.DEMO

    def as_dict(self):
        return {
            "engine": CONFIG_ENGINE_NAME,
            "version": CONFIG_ENGINE_VERSION,
            "min_grade": self.min_grade.value,
            "strategy_id": self.strategy_id,
            "execution_mode": self.execution_mode.value,
            "live_confirmed": self.live_confirmed,
            "watchlist_source": self.watchlist_source.value,
            "manual_watchlist": list(self.manual_watchlist),
            "max_open_positions": self.max_open_positions,
            "risk_per_trade_pct": self.risk_per_trade_pct,
            "max_position_pct": self.max_position_pct,
            "sl_atr_multiplier": self.sl_atr_multiplier,
            "tp_atr_multiplier": self.tp_atr_multiplier,
            "loop_interval_sec": self.loop_interval_sec,
            "grade_bands": self.grade_bands.as_dict(),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data):
        gb_data = data.get("grade_bands")
        if gb_data is None:
            grade_bands = DEFAULT_GRADE_BANDS
        else:
            grade_bands = GradeBands(
                a_plus_min=float(gb_data.get("a_plus_min", 75.0)),
                a_min=float(gb_data.get("a_min", 55.0)),
                b_plus_min=float(gb_data.get("b_plus_min", 45.0)),
                b_min=float(gb_data.get("b_min", 30.0)),
            )

        # Backward compat: PAPER -> DEMO
        mode_raw = str(
            data.get("execution_mode", ExecutionMode.DEMO.value)
        ).upper()
        if mode_raw == "PAPER":
            mode_raw = "DEMO"

        config = cls(
            min_grade=GradeBand(
                data.get("min_grade", GradeBand.A.value)
            ),
            strategy_id=str(data.get("strategy_id", "OLD")),
            execution_mode=ExecutionMode(mode_raw),
            live_confirmed=bool(data.get("live_confirmed", False)),
            watchlist_source=WatchlistSource(
                data.get(
                    "watchlist_source",
                    WatchlistSource.FAVORITES.value,
                )
            ),
            manual_watchlist=tuple(
                data.get("manual_watchlist", ())
            ),
            max_open_positions=int(
                data.get("max_open_positions", 5)
            ),
            risk_per_trade_pct=float(
                data.get("risk_per_trade_pct", 1.0)
            ),
            max_position_pct=float(
                data.get("max_position_pct", 10.0)
            ),
            sl_atr_multiplier=float(
                data.get("sl_atr_multiplier", 1.5)
            ),
            tp_atr_multiplier=float(
                data.get("tp_atr_multiplier", 3.0)
            ),
            loop_interval_sec=int(
                data.get("loop_interval_sec", 60)
            ),
            grade_bands=grade_bands,
            metadata=dict(data.get("metadata", {})),
        )
        config.validate()
        return config


__all__ = [
    "CONFIG_ENGINE_NAME", "CONFIG_ENGINE_VERSION",
    "GradeBand", "WatchlistSource", "ExecutionMode",
    "GradeBands", "DEFAULT_GRADE_BANDS",
    "AutoRobomlmConfig",
]
