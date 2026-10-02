"""
AutoROBOMLM — Objective Gate (AIC-009)
No optimization is meaningful without a clearly defined objective.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Optional

OBJECTIVE_GATE_NAME = "AutoROBOMLM_ObjectiveGate"
OBJECTIVE_GATE_VERSION = "1.0"
AIC_REFERENCE = "AIC-009"


class ObjectiveType(str, Enum):
    CAPITAL_PRESERVATION = "CAPITAL_PRESERVATION"
    RISK_ADJUSTED_RETURN = "RISK_ADJUSTED_RETURN"
    MAXIMUM_RETURN = "MAXIMUM_RETURN"
    HIGHEST_QUALITY_TRADE = "HIGHEST_QUALITY_TRADE"
    CUSTOM = "CUSTOM"


class ObjectiveGateStatus(str, Enum):
    OPEN = "OPEN"
    LIMITED = "LIMITED"
    CLOSED = "CLOSED"


@dataclass(frozen=True)
class ObjectiveDefinition:
    objective_type: ObjectiveType
    metric: str
    version: str
    thresholds: Mapping[str, float] = field(default_factory=dict)
    description: str = ""

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not isinstance(self.objective_type, ObjectiveType):
            errors.append("objective_type must be an ObjectiveType.")
        if not self.metric or not str(self.metric).strip():
            errors.append("metric is required.")
        if not self.version or not str(self.version).strip():
            errors.append("version is required.")
        for key, value in self.thresholds.items():
            if not isinstance(value, (int, float)):
                errors.append(f"threshold {key} must be numeric.")
        return tuple(errors)


@dataclass(frozen=True)
class ObjectiveGateResult:
    status: ObjectiveGateStatus
    objective: Optional[ObjectiveDefinition]
    passed: bool
    reasons: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()
    engine: str = OBJECTIVE_GATE_NAME
    version: str = OBJECTIVE_GATE_VERSION
    aic_reference: str = AIC_REFERENCE

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "objective": (
                {
                    "objective_type": self.objective.objective_type.value,
                    "metric": self.objective.metric,
                    "version": self.objective.version,
                    "thresholds": dict(self.objective.thresholds),
                    "description": self.objective.description,
                }
                if self.objective is not None else None
            ),
            "passed": self.passed,
            "reasons": list(self.reasons),
            "errors": list(self.errors),
            "engine": self.engine,
            "version": self.version,
            "aic_reference": self.aic_reference,
        }


class ObjectiveGate:
    def __init__(self, *, allow_custom: bool = True) -> None:
        self.allow_custom = bool(allow_custom)

    def evaluate(
        self, objective: Optional[ObjectiveDefinition]
    ) -> ObjectiveGateResult:
        if objective is None:
            return ObjectiveGateResult(
                status=ObjectiveGateStatus.CLOSED,
                objective=None,
                passed=False,
                reasons=(
                    "No objective defined. AIC-009 requires "
                    "an explicit objective before commitment.",
                ),
            )
        errors = objective.validate()
        if errors:
            return ObjectiveGateResult(
                status=ObjectiveGateStatus.CLOSED,
                objective=objective,
                passed=False,
                errors=errors,
                reasons=(
                    "Objective definition is incomplete or invalid.",
                ),
            )
        if (
            objective.objective_type == ObjectiveType.CUSTOM
            and not self.allow_custom
        ):
            return ObjectiveGateResult(
                status=ObjectiveGateStatus.CLOSED,
                objective=objective,
                passed=False,
                reasons=("Custom objectives are disabled by policy.",),
            )
        if not objective.thresholds:
            return ObjectiveGateResult(
                status=ObjectiveGateStatus.LIMITED,
                objective=objective,
                passed=True,
                reasons=(
                    "Objective is defined but has no explicit thresholds.",
                ),
            )
        return ObjectiveGateResult(
            status=ObjectiveGateStatus.OPEN,
            objective=objective,
            passed=True,
            reasons=(
                "Objective is defined, measurable and versioned.",
            ),
        )


def evaluate_objective(
    objective: Optional[ObjectiveDefinition],
    *, allow_custom: bool = True,
) -> ObjectiveGateResult:
    return ObjectiveGate(
        allow_custom=allow_custom
    ).evaluate(objective)


__all__ = [
    "OBJECTIVE_GATE_NAME", "OBJECTIVE_GATE_VERSION", "AIC_REFERENCE",
    "ObjectiveType", "ObjectiveGateStatus",
    "ObjectiveDefinition", "ObjectiveGateResult",
    "ObjectiveGate", "evaluate_objective",
]
