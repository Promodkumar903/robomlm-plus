"""
ROBOMLM_PLUS
AutoROBOMLM — Grade Evaluator

Purpose:
    Convert a decision signal into a grade band.

    The evaluator is deliberately pluggable:
        - First version consumes D13 decision_score.
        - Future versions may consume scanner/trade
          calculation outputs without changing the
          public contract.

Grade bands (canonical):
    A+   : 75 - 100
    A    : 55 - 75
    B+   : 45 - 55
    B    : 30 - 45
    HOLD : < 30

Design:
    - No fabricated values.
    - Missing input -> HOLD (never guessed).
    - Invalid input -> INVALID result.
    - No execution authority.
    - No BUY/SELL generation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import isfinite
from typing import Any, Mapping, Optional

from app.autorobomlm.config import (
    DEFAULT_GRADE_BANDS,
    GradeBand,
    GradeBands,
)


# ============================================================================
# ENGINE IDENTITY
# ============================================================================

GRADE_ENGINE_NAME = "AutoROBOMLM_GradeEvaluator"
GRADE_ENGINE_VERSION = "1.0"


# ============================================================================
# STATUS
# ============================================================================

class GradeStatus(str, Enum):
    VALID = "VALID"
    INSUFFICIENT = "INSUFFICIENT"
    INVALID = "INVALID"


# ============================================================================
# SOURCE
# ============================================================================

class GradeSource(str, Enum):
    """
    Where the grade score came from.

    This makes the origin auditable.
    """

    D13_DECISION = "D13_DECISION"
    SCANNER = "SCANNER"
    COMPOSITE = "COMPOSITE"
    UNKNOWN = "UNKNOWN"


# ============================================================================
# INPUT
# ============================================================================

@dataclass(frozen=True)
class GradeInput:
    """
    Input to the grade evaluator.

    score:
        Canonical 0..100 grade score.

    source:
        Where the score came from.

    components:
        Optional per-source breakdown for auditability.
    """

    score: Optional[float]

    source: GradeSource = GradeSource.UNKNOWN

    components: Mapping[str, float] = field(
        default_factory=dict
    )

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )


# ============================================================================
# RESULT
# ============================================================================

@dataclass(frozen=True)
class GradeResult:
    """
    Result of grade evaluation.

    Fields:
        status          - VALID / INSUFFICIENT / INVALID
        grade           - A+ / A / B+ / B / HOLD (when VALID)
        score           - the numeric score used
        source          - origin of the score
        is_eligible     - user min_grade gate
        min_required    - numeric threshold used
        reasons         - human-readable reasons
        components      - per-source contribution (audit)
    """

    status: GradeStatus

    grade: Optional[GradeBand]
    score: Optional[float]

    source: GradeSource

    is_eligible: bool
    min_required: Optional[float]

    reasons: tuple[str, ...] = ()
    components: Mapping[str, float] = field(
        default_factory=dict
    )
    errors: tuple[str, ...] = ()

    engine: str = GRADE_ENGINE_NAME
    version: str = GRADE_ENGINE_VERSION

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "grade": (
                self.grade.value
                if self.grade is not None
                else None
            ),
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


# ============================================================================
# ENGINE
# ============================================================================

class GradeEvaluator:
    """
    Grade evaluator.

    Responsibilities:
        - Validate score input.
        - Classify score into canonical grade band.
        - Apply user min_grade gate.
        - Return explainable result.

    Non-responsibilities:
        - computing the score itself (source provides it)
        - deciding direction
        - checking resources or constraints
        - executing trades
    """

    def __init__(
        self,
        *,
        grade_bands: GradeBands = DEFAULT_GRADE_BANDS,
    ) -> None:
        grade_bands.validate()
        self.grade_bands = grade_bands

    # ------------------------------------------------------------------
    # PUBLIC
    # ------------------------------------------------------------------

    def evaluate(
        self,
        grade_input: GradeInput,
        *,
        min_grade: GradeBand,
    ) -> GradeResult:
        """
        Evaluate a grade input against a user min_grade.

        min_grade = HOLD always returns not eligible.
        """

        if not isinstance(min_grade, GradeBand):
            return self._invalid(
                "min_grade must be a GradeBand.",
                source=grade_input.source,
                components=grade_input.components,
            )

        if min_grade == GradeBand.HOLD:
            # Explicit user choice: never take a trade.
            return GradeResult(
                status=GradeStatus.VALID,
                grade=None,
                score=None,
                source=grade_input.source,
                is_eligible=False,
                min_required=None,
                reasons=(
                    "User selected HOLD. No trade is permitted.",
                ),
                components=dict(grade_input.components),
            )

        score = grade_input.score

        # ----------------------------------------------------------
        # Missing score -> INSUFFICIENT (never guessed)
        # ----------------------------------------------------------

        if score is None:
            return GradeResult(
                status=GradeStatus.INSUFFICIENT,
                grade=None,
                score=None,
                source=grade_input.source,
                is_eligible=False,
                min_required=self.grade_bands.min_score_for(
                    min_grade
                ),
                reasons=(
                    "Grade score was not supplied. "
                    "Grade cannot be inferred.",
                ),
                components=dict(grade_input.components),
            )

        # ----------------------------------------------------------
        # Validate numeric score
        # ----------------------------------------------------------

        error = self._validate_score(score)

        if error:
            return self._invalid(
                error,
                source=grade_input.source,
                components=grade_input.components,
            )

        numeric_score = float(score)

        # ----------------------------------------------------------
        # Classify
        # ----------------------------------------------------------

        grade = self.grade_bands.classify(numeric_score)

        min_required = self.grade_bands.min_score_for(min_grade)

        is_eligible = (
            grade != GradeBand.HOLD
            and min_required is not None
            and numeric_score >= min_required
        )

        reasons: list[str] = []

        reasons.append(
            f"Score {numeric_score:.2f} classified as {grade.value}."
        )

        if grade == GradeBand.HOLD:
            reasons.append(
                "Score is below the minimum trade band."
            )

        if min_required is not None:
            reasons.append(
                f"User minimum grade is {min_grade.value} "
                f"(min score {min_required:.2f})."
            )

        if not is_eligible and grade != GradeBand.HOLD:
            reasons.append(
                "Grade is valid but below user-selected minimum."
            )

        return GradeResult(
            status=GradeStatus.VALID,
            grade=grade,
            score=numeric_score,
            source=grade_input.source,
            is_eligible=is_eligible,
            min_required=min_required,
            reasons=tuple(reasons),
            components=dict(grade_input.components),
        )

    # ------------------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_score(score: Any) -> Optional[str]:
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
    def _invalid(
        error: str,
        *,
        source: GradeSource,
        components: Mapping[str, float],
    ) -> GradeResult:
        return GradeResult(
            status=GradeStatus.INVALID,
            grade=None,
            score=None,
            source=source,
            is_eligible=False,
            min_required=None,
            reasons=(),
            components=dict(components),
            errors=(error,),
        )


# ============================================================================
# CONVENIENCE
# ============================================================================

def evaluate_grade(
    *,
    score: Optional[float],
    min_grade: GradeBand,
    source: GradeSource = GradeSource.UNKNOWN,
    grade_bands: GradeBands = DEFAULT_GRADE_BANDS,
    components: Optional[Mapping[str, float]] = None,
) -> GradeResult:
    """
    Functional convenience wrapper.
    """

    evaluator = GradeEvaluator(grade_bands=grade_bands)

    return evaluator.evaluate(
        GradeInput(
            score=score,
            source=source,
            components=dict(components or {}),
        ),
        min_grade=min_grade,
    )


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "GRADE_ENGINE_NAME",
    "GRADE_ENGINE_VERSION",

    "GradeStatus",
    "GradeSource",

    "GradeInput",
    "GradeResult",

    "GradeEvaluator",

    "evaluate_grade",
]