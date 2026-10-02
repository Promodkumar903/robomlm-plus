"""AutoROBOMLM installer part 2 - config + grade_evaluator"""
from pathlib import Path

ROOT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\autorobomlm")
ROOT.mkdir(parents=True, exist_ok=True)

FILES = {}

FILES["config.py"] = '''"""
ROBOMLM_PLUS - AutoROBOMLM Configuration Schema
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

CONFIG_ENGINE_NAME = "AutoROBOMLM_Config"
CONFIG_ENGINE_VERSION = "1.0"


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
    PAPER = "PAPER"
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
    execution_mode: ExecutionMode = ExecutionMode.PAPER
    watchlist_source: WatchlistSource = WatchlistSource.FAVORITES
    manual_watchlist: tuple = ()
    max_open_positions: int = 5
    risk_per_trade_pct: float = 1.0
    max_position_pct: float = 10.0
    sl_atr_multiplier: float = 1.5
    tp_atr_multiplier: float = 3.0
    loop_interval_sec: int = 60
    grade_bands: GradeBands = field(
        default_factory=lambda: DEFAULT_GRADE_BANDS
    )
    metadata: Mapping = field(default_factory=dict)

    def validate(self) -> None:
        if not isinstance(self.min_grade, GradeBand):
            raise ValueError("min_grade must be a GradeBand.")
        if not isinstance(self.execution_mode, ExecutionMode):
            raise ValueError("execution_mode must be an ExecutionMode.")
        if not isinstance(self.watchlist_source, WatchlistSource):
            raise ValueError("watchlist_source must be a WatchlistSource.")
        if (
            self.watchlist_source == WatchlistSource.MANUAL
            and not self.manual_watchlist
        ):
            raise ValueError(
                "manual_watchlist cannot be empty when source is MANUAL."
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
        self.grade_bands.validate()

    def min_score_required(self):
        return self.grade_bands.min_score_for(self.min_grade)

    def is_score_eligible(self, score: float) -> bool:
        required = self.min_score_required()
        if required is None:
            return False
        return float(score) >= required

    def as_dict(self):
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
        config = cls(
            min_grade=GradeBand(data.get("min_grade", GradeBand.A.value)),
            execution_mode=ExecutionMode(
                data.get("execution_mode", ExecutionMode.PAPER.value)
            ),
            watchlist_source=WatchlistSource(
                data.get("watchlist_source", WatchlistSource.FAVORITES.value)
            ),
            manual_watchlist=tuple(data.get("manual_watchlist", ())),
            max_open_positions=int(data.get("max_open_positions", 5)),
            risk_per_trade_pct=float(data.get("risk_per_trade_pct", 1.0)),
            max_position_pct=float(data.get("max_position_pct", 10.0)),
            sl_atr_multiplier=float(data.get("sl_atr_multiplier", 1.5)),
            tp_atr_multiplier=float(data.get("tp_atr_multiplier", 3.0)),
            loop_interval_sec=int(data.get("loop_interval_sec", 60)),
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
'''

FILES["grade_evaluator.py"] = '''"""
ROBOMLM_PLUS - AutoROBOMLM Grade Evaluator
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from math import isfinite
from typing import Any, Mapping, Optional

from app.autorobomlm.config import (
    DEFAULT_GRADE_BANDS, GradeBand, GradeBands,
)

GRADE_ENGINE_NAME = "AutoROBOMLM_GradeEvaluator"
GRADE_ENGINE_VERSION = "1.0"


class GradeStatus(str, Enum):
    VALID = "VALID"
    INSUFFICIENT = "INSUFFICIENT"
    INVALID = "INVALID"


class GradeSource(str, Enum):
    D13_DECISION = "D13_DECISION"
    SCANNER = "SCANNER"
    COMPOSITE = "COMPOSITE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class GradeInput:
    score: Optional[float]
    source: GradeSource = GradeSource.UNKNOWN
    components: Mapping = field(default_factory=dict)
    metadata: Mapping = field(default_factory=dict)


@dataclass(frozen=True)
class GradeResult:
    status: GradeStatus
    grade: Optional[GradeBand]
    score: Optional[float]
    source: GradeSource
    is_eligible: bool
    min_required: Optional[float]
    reasons: tuple = ()
    components: Mapping = field(default_factory=dict)
    errors: tuple = ()
    engine: str = GRADE_ENGINE_NAME
    version: str = GRADE_ENGINE_VERSION

    def as_dict(self):
        return {
            "status": self.status.value,
            "grade": self.grade.value if self.grade else None,
            "score": self.score,
            "source": self.source.value,
            "is_eligible": self.is_eligible,
            "min_required": self.min_required,
            "reasons": list(self.reasons),
            "components": dict(self.components),
            "errors": list(self.errors),
            "engine": self.engine,
            "version": self.version,
        }


class GradeEvaluator:
    def __init__(self, *, grade_bands: GradeBands = DEFAULT_GRADE_BANDS):
        grade_bands.validate()
        self.grade_bands = grade_bands

    def evaluate(
        self, grade_input: GradeInput, *, min_grade: GradeBand,
    ) -> GradeResult:
        if not isinstance(min_grade, GradeBand):
            return self._invalid(
                "min_grade must be a GradeBand.",
                source=grade_input.source,
                components=grade_input.components,
            )
        if min_grade == GradeBand.HOLD:
            return GradeResult(
                status=GradeStatus.VALID,
                grade=None, score=None,
                source=grade_input.source,
                is_eligible=False, min_required=None,
                reasons=(
                    "User selected HOLD. No trade is permitted.",
                ),
                components=dict(grade_input.components),
            )
        score = grade_input.score
        if score is None:
            return GradeResult(
                status=GradeStatus.INSUFFICIENT,
                grade=None, score=None,
                source=grade_input.source,
                is_eligible=False,
                min_required=self.grade_bands.min_score_for(min_grade),
                reasons=(
                    "Grade score was not supplied. "
                    "Grade cannot be inferred.",
                ),
                components=dict(grade_input.components),
            )
        error = self._validate_score(score)
        if error:
            return self._invalid(
                error,
                source=grade_input.source,
                components=grade_input.components,
            )
        numeric_score = float(score)
        grade = self.grade_bands.classify(numeric_score)
        min_required = self.grade_bands.min_score_for(min_grade)
        is_eligible = (
            grade != GradeBand.HOLD
            and min_required is not None
            and numeric_score >= min_required
        )
        reasons = []
        reasons.append(
            f"Score {numeric_score:.2f} classified as {grade.value}."
        )
        if grade == GradeBand.HOLD:
            reasons.append("Score is below the minimum trade band.")
        if min_required is not None:
            reasons.append(
                f"User minimum grade is {min_grade.value} "
                f"(min score {min_required:.2f})."
            )
        if not is_eligible and grade != GradeBand.HOLD:
            reasons.append("Grade is valid but below user minimum.")
        return GradeResult(
            status=GradeStatus.VALID,
            grade=grade, score=numeric_score,
            source=grade_input.source,
            is_eligible=is_eligible,
            min_required=min_required,
            reasons=tuple(reasons),
            components=dict(grade_input.components),
        )

    @staticmethod
    def _validate_score(score):
        if isinstance(score, bool):
            return "Score cannot be boolean."
        if not isinstance(score, (int, float)):
            return "Score must be numeric."
        numeric = float(score)
        if not isfinite(numeric):
            return "Score must be finite."
        if not (0.0 <= numeric <= 100.0):
            return "Score must be within 0..100."
        return None

    @staticmethod
    def _invalid(error, *, source, components):
        return GradeResult(
            status=GradeStatus.INVALID,
            grade=None, score=None, source=source,
            is_eligible=False, min_required=None,
            reasons=(), components=dict(components),
            errors=(error,),
        )


def evaluate_grade(
    *, score, min_grade,
    source: GradeSource = GradeSource.UNKNOWN,
    grade_bands: GradeBands = DEFAULT_GRADE_BANDS,
    components=None,
) -> GradeResult:
    evaluator = GradeEvaluator(grade_bands=grade_bands)
    return evaluator.evaluate(
        GradeInput(
            score=score, source=source,
            components=dict(components or {}),
        ),
        min_grade=min_grade,
    )


__all__ = [
    "GRADE_ENGINE_NAME", "GRADE_ENGINE_VERSION",
    "GradeStatus", "GradeSource",
    "GradeInput", "GradeResult",
    "GradeEvaluator", "evaluate_grade",
]
'''

for filename, content in FILES.items():
    path = ROOT / filename
    path.write_text(content, encoding="utf-8")
    print(f"WROTE: {path}")

print()
print(f"DONE. Files in {ROOT}:")
for p in sorted(ROOT.glob("*.py")):
    print(f"  {p.name} ({p.stat().st_size} bytes)")