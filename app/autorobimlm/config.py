"""
ROBOMLM_PLUS
AutoROBOMLM — Configuration Schema

Purpose:
    User-facing configuration for AutoROBOMLM.

    Defines:
        - Grade bands (A+ / A / B+ / B / HOLD)
        - User min_grade selection
        - Risk parameters
        - SL/TP parameters
        - Loop parameters
        - Watchlist source

Design:
    - No fabricated defaults that change meaning
    - Explicit validation
    - Serializable for API
    - Frozen where immutable
    - No execution authority
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Optional


# ============================================================================
# ENGINE IDENTITY
# ============================================================================

CONFIG_ENGINE_NAME = "AutoROBOMLM_Config"
CONFIG_ENGINE_VERSION = "1.0"


# ============================================================================
# ENUMS
# ============================================================================

class GradeBand(str, Enum):
    """
    User-facing quality band.

    Higher is stricter.

    HOLD means no trade is taken regardless of score.
    """

    A_PLUS = "A+"
    A = "A"
    B_PLUS = "B+"
    B = "B"
    HOLD = "HOLD"


class WatchlistSource(str, Enum):
    """
    Where AutoROBOMLM picks symbols to scan.
    """

    FAVORITES = "FAVORITES"
    DISCOVERY_TOP10 = "DISCOVERY_TOP10"
    MANUAL = "MANUAL"


class ExecutionMode(str, Enum):
    """
    Execution mode.

    Mirrors the existing ModeManager contract.
    """

    PAPER = "PAPER"
    DEMO = "DEMO"
    LIVE = "LIVE"


# ============================================================================
# GRADE BANDS (IMMUTABLE CANONICAL DEFINITION)
# ============================================================================

@dataclass(frozen=True)
class GradeBands:
    """
    Canonical grade thresholds.

    These are the user's stated thresholds:

        A+ : 75 - 100
        A  : 55 - 75
        B+ : 45 - 55
        B  : 30 - 45
        HOLD : < 30

    These values are intentionally NOT configurable
    per-user in the first version. Changing them changes
    the meaning of "A+", which would break comparability
    across users and across sessions.

    If future versions allow override, that override must
    be versioned and logged.
    """

    a_plus_min: float = 75.0
    a_min: float = 55.0
    b_plus_min: float = 45.0
    b_min: float = 30.0

    def validate(self) -> None:
        values = (
            self.a_plus_min,
            self.a_min,
            self.b_plus_min,
            self.b_min,
        )

        for value in values:
            if not (0.0 <= value <= 100.0):
                raise ValueError(
                    "Grade band thresholds must be within 0..100."
                )

        if not (
            self.a_plus_min
            > self.a_min
            > self.b_plus_min
            > self.b_min
        ):
            raise ValueError(
                "Grade band thresholds must be strictly descending."
            )

    def classify(self, score: float) -> GradeBand:
        """
        Classify a 0..100 score into a canonical grade band.
        """

        if score >= self.a_plus_min:
            return GradeBand.A_PLUS

        if score >= self.a_min:
            return GradeBand.A

        if score >= self.b_plus_min:
            return GradeBand.B_PLUS

        if score >= self.b_min:
            return GradeBand.B

        return GradeBand.HOLD

    def min_score_for(
        self,
        grade: GradeBand,
    ) -> Optional[float]:
        """
        Return the minimum score required for a grade.

        HOLD returns None because it is not a trade grade.
        """

        if grade == GradeBand.A_PLUS:
            return self.a_plus_min

        if grade == GradeBand.A:
            return self.a_min

        if grade == GradeBand.B_PLUS:
            return self.b_plus_min

        if grade == GradeBand.B:
            return self.b_min

        return None

    def as_dict(self) -> dict[str, Any]:
        return {
            "A+": (self.a_plus_min, 100.0),
            "A": (self.a_min, self.a_plus_min),
            "B+": (self.b_plus_min, self.a_min),
            "B": (self.b_min, self.b_plus_min),
            "HOLD": (0.0, self.b_min),
        }


# Canonical defaults (single source of truth).
DEFAULT_GRADE_BANDS = GradeBands()


# ============================================================================
# USER CONFIG
# ============================================================================

@dataclass
class AutoRobomlmConfig:
    """
    AutoROBOMLM runtime configuration.

    This object is what the user controls through the UI:

        min_grade          -> dropdown
        execution_mode     -> PAPER / DEMO / LIVE
        watchlist_source   -> FAVORITES / DISCOVERY_TOP10 / MANUAL
        max_open_positions -> integer
        risk_per_trade_pct -> float (percent of capital)
        max_position_pct   -> float (per-position cap)
        sl_atr_multiplier  -> float
        tp_atr_multiplier  -> float
        loop_interval_sec  -> integer

    No defaults are fabricated where they would
    change trading meaning. Defaults that are provided
    are conservative and explicit.
    """

    min_grade: GradeBand = GradeBand.A

    execution_mode: ExecutionMode = ExecutionMode.PAPER

    watchlist_source: WatchlistSource = WatchlistSource.FAVORITES

    manual_watchlist: tuple[str, ...] = ()

    max_open_positions: int = 5

    risk_per_trade_pct: float = 1.0

    max_position_pct: float = 10.0

    sl_atr_multiplier: float = 1.5

    tp_atr_multiplier: float = 3.0

    loop_interval_sec: int = 60

    grade_bands: GradeBands = field(
        default_factory=lambda: DEFAULT_GRADE_BANDS
    )

    metadata: Mapping[str, Any] = field(default_factory=dict)

    # --------------------------------------------------------------
    # Validation
    # --------------------------------------------------------------

    def validate(self) -> None:
        """
        Validate all config fields.

        Raises ValueError with a clear reason on failure.

        No field is silently corrected.
        """

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
            raise ValueError(
                "max_open_positions must be >= 1."
            )

        if not (0.0 < self.risk_per_trade_pct <= 100.0):
            raise ValueError(
                "risk_per_trade_pct must be within (0, 100]."
            )

        if not (0.0 < self.max_position_pct <= 100.0):
            raise ValueError(
                "max_position_pct must be within (0, 100]."
            )

        if self.risk_per_trade_pct > self.max_position_pct:
            raise ValueError(
                "risk_per_trade_pct cannot exceed max_position_pct."
            )

        if self.sl_atr_multiplier <= 0.0:
            raise ValueError(
                "sl_atr_multiplier must be > 0."
            )

        if self.tp_atr_multiplier <= 0.0:
            raise ValueError(
                "tp_atr_multiplier must be > 0."
            )

        if self.loop_interval_sec < 1:
            raise ValueError(
                "loop_interval_sec must be >= 1."
            )

        self.grade_bands.validate()

    # --------------------------------------------------------------
    # Derived
    # --------------------------------------------------------------

    def min_score_required(self) -> Optional[float]:
        """
        Return the minimum grade score required by the
        user's selected min_grade.

        Returns None if min_grade is HOLD (no trade).
        """

        return self.grade_bands.min_score_for(self.min_grade)

    def is_score_eligible(self, score: float) -> bool:
        """
        Return True if a grade score is eligible for
        execution under this config.

        HOLD never qualifies.
        """

        required = self.min_score_required()

        if required is None:
            return False

        return float(score) >= required

    # --------------------------------------------------------------
    # Serialization
    # --------------------------------------------------------------

    def as_dict(self) -> dict[str, Any]:
        return {
            "engine": CONFIG_ENGINE_NAME,
            "version": CONFIG_ENGINE_VERSION,

            "min_grade": self.min_grade.value,
            "execution_mode": self.execution_mode.value,
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
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "AutoRobomlmConfig":
        """
        Build config from a mapping.

        Validates on construction.
        """

        grade_bands_data = data.get("grade_bands")

        if grade_bands_data is None:
            grade_bands = DEFAULT_GRADE_BANDS
        else:
            grade_bands = GradeBands(
                a_plus_min=float(
                    grade_bands_data.get("a_plus_min", 75.0)
                ),
                a_min=float(
                    grade_bands_data.get("a_min", 55.0)
                ),
                b_plus_min=float(
                    grade_bands_data.get("b_plus_min", 45.0)
                ),
                b_min=float(
                    grade_bands_data.get("b_min", 30.0)
                ),
            )

        config = cls(
            min_grade=GradeBand(
                data.get("min_grade", GradeBand.A.value)
            ),
            execution_mode=ExecutionMode(
                data.get("execution_mode", ExecutionMode.PAPER.value)
            ),
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


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "CONFIG_ENGINE_NAME",
    "CONFIG_ENGINE_VERSION",

    "GradeBand",
    "WatchlistSource",
    "ExecutionMode",

    "GradeBands",
    "DEFAULT_GRADE_BANDS",

    "AutoRobomlmConfig",
]