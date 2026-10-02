"""
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
