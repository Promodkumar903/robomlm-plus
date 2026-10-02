"""
AutoROBOMLM file installer.
Run: python install_autorobomlm.py
"""
from pathlib import Path

ROOT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\autorobomlm")
ROOT.mkdir(parents=True, exist_ok=True)

FILES = {}

FILES["__init__.py"] = '''"""
ROBOMLM_PLUS — AutoROBOMLM package.
Safety pipeline between D13 decision and execution.
"""

from app.autorobomlm.config import (
    AutoRobomlmConfig,
    GradeBand,
    GradeBands,
    WatchlistSource,
    ExecutionMode,
    DEFAULT_GRADE_BANDS,
)

from app.autorobomlm.grade_evaluator import (
    GradeEvaluator,
    GradeInput,
    GradeResult,
    GradeSource,
    GradeStatus,
    evaluate_grade,
)

from app.autorobomlm.objective_gate import (
    ObjectiveGate,
    ObjectiveDefinition,
    ObjectiveGateResult,
    ObjectiveGateStatus,
    ObjectiveType,
    evaluate_objective,
)

from app.autorobomlm.resource_gate import (
    ResourceGate,
    ResourceCheck,
    ResourceGateResult,
    ResourceGateStatus,
    ResourceKind,
    evaluate_resources,
)

from app.autorobomlm.constraint_gate import (
    ConstraintGate,
    ConstraintCheck,
    ConstraintDisposition,
    ConstraintGateResult,
    ConstraintGateStatus,
    ConstraintKind,
    evaluate_constraints,
)

__all__ = [
    "AutoRobomlmConfig", "GradeBand", "GradeBands",
    "WatchlistSource", "ExecutionMode", "DEFAULT_GRADE_BANDS",
    "GradeEvaluator", "GradeInput", "GradeResult",
    "GradeSource", "GradeStatus", "evaluate_grade",
    "ObjectiveGate", "ObjectiveDefinition",
    "ObjectiveGateResult", "ObjectiveGateStatus",
    "ObjectiveType", "evaluate_objective",
    "ResourceGate", "ResourceCheck",
    "ResourceGateResult", "ResourceGateStatus",
    "ResourceKind", "evaluate_resources",
    "ConstraintGate", "ConstraintCheck",
    "ConstraintDisposition", "ConstraintGateResult",
    "ConstraintGateStatus", "ConstraintKind",
    "evaluate_constraints",
]
'''

FILES["objective_gate.py"] = '''"""
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
'''

FILES["resource_gate.py"] = '''"""
AutoROBOMLM — Resource Gate (AIC-007)
No commitment without sufficient resources to complete it safely.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from math import isfinite
from typing import Any, Mapping, Optional

RESOURCE_GATE_NAME = "AutoROBOMLM_ResourceGate"
RESOURCE_GATE_VERSION = "1.0"
AIC_REFERENCE = "AIC-007"


class ResourceGateStatus(str, Enum):
    OPEN = "OPEN"
    LIMITED = "LIMITED"
    CLOSED = "CLOSED"


class ResourceKind(str, Enum):
    CAPITAL = "CAPITAL"
    TIME = "TIME"
    COMPUTE = "COMPUTE"
    NETWORK = "NETWORK"
    LIQUIDITY = "LIQUIDITY"
    CUSTOM = "CUSTOM"


@dataclass(frozen=True)
class ResourceCheck:
    kind: ResourceKind
    name: str
    required: float
    available: float
    unit: Optional[str] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def is_sufficient(self) -> bool:
        return float(self.available) >= float(self.required)

    def deficit(self) -> float:
        return max(0.0, float(self.required) - float(self.available))


@dataclass(frozen=True)
class ResourceGateResult:
    status: ResourceGateStatus
    passed: bool
    checks: tuple[ResourceCheck, ...] = ()
    reasons: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()
    engine: str = RESOURCE_GATE_NAME
    version: str = RESOURCE_GATE_VERSION
    aic_reference: str = AIC_REFERENCE

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "passed": self.passed,
            "checks": [
                {
                    "kind": c.kind.value,
                    "name": c.name,
                    "required": c.required,
                    "available": c.available,
                    "sufficient": c.is_sufficient(),
                    "deficit": c.deficit(),
                    "unit": c.unit,
                } for c in self.checks
            ],
            "reasons": list(self.reasons),
            "errors": list(self.errors),
            "engine": self.engine,
            "version": self.version,
            "aic_reference": self.aic_reference,
        }


class ResourceGate:
    def evaluate(
        self,
        checks: Optional[tuple[ResourceCheck, ...]] = None,
    ) -> ResourceGateResult:
        if not checks:
            return ResourceGateResult(
                status=ResourceGateStatus.CLOSED,
                passed=False,
                checks=(),
                reasons=(
                    "No resource checks supplied. AIC-007 requires "
                    "resource evaluation before commitment.",
                ),
            )
        errors: list[str] = []
        for check in checks:
            if not isinstance(check, ResourceCheck):
                errors.append(
                    "All checks must be ResourceCheck instances."
                )
                continue
            if not check.name or not str(check.name).strip():
                errors.append("ResourceCheck.name is required.")
            for label, value in (
                ("required", check.required),
                ("available", check.available),
            ):
                if isinstance(value, bool):
                    errors.append(
                        f"{check.name}.{label} cannot be boolean."
                    )
                    continue
                if not isinstance(value, (int, float)):
                    errors.append(
                        f"{check.name}.{label} must be numeric."
                    )
                    continue
                if not isfinite(float(value)):
                    errors.append(
                        f"{check.name}.{label} must be finite."
                    )
                    continue
                if float(value) < 0.0:
                    errors.append(
                        f"{check.name}.{label} cannot be negative."
                    )
        if errors:
            return ResourceGateResult(
                status=ResourceGateStatus.CLOSED,
                passed=False,
                checks=tuple(checks),
                errors=tuple(errors),
                reasons=("One or more resource checks are invalid.",),
            )
        insufficient = [c for c in checks if not c.is_sufficient()]
        if insufficient:
            reasons = tuple(
                f"{c.name}: available {c.available} "
                f"< required {c.required}"
                + (f" {c.unit}" if c.unit else "")
                for c in insufficient
            )
            return ResourceGateResult(
                status=ResourceGateStatus.CLOSED,
                passed=False,
                checks=tuple(checks),
                reasons=reasons,
            )
        return ResourceGateResult(
            status=ResourceGateStatus.OPEN,
            passed=True,
            checks=tuple(checks),
            reasons=("All supplied resources are sufficient.",),
        )


def evaluate_resources(
    checks: Optional[tuple[ResourceCheck, ...]] = None,
) -> ResourceGateResult:
    return ResourceGate().evaluate(checks)


__all__ = [
    "RESOURCE_GATE_NAME", "RESOURCE_GATE_VERSION", "AIC_REFERENCE",
    "ResourceGateStatus", "ResourceKind",
    "ResourceCheck", "ResourceGateResult",
    "ResourceGate", "evaluate_resources",
]
'''

FILES["constraint_gate.py"] = '''"""
AutoROBOMLM — Constraint Gate (AIC-008)
An action may be possible but still not permissible.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Optional

CONSTRAINT_GATE_NAME = "AutoROBOMLM_ConstraintGate"
CONSTRAINT_GATE_VERSION = "1.0"
AIC_REFERENCE = "AIC-008"


class ConstraintGateStatus(str, Enum):
    OPEN = "OPEN"
    LIMITED = "LIMITED"
    CLOSED = "CLOSED"


class ConstraintKind(str, Enum):
    EXCHANGE_STATE = "EXCHANGE_STATE"
    REGULATORY = "REGULATORY"
    RISK_LIMIT = "RISK_LIMIT"
    DAILY_LOSS_LIMIT = "DAILY_LOSS_LIMIT"
    CIRCUIT_BREAKER = "CIRCUIT_BREAKER"
    STRATEGY_STATE = "STRATEGY_STATE"
    KILL_SWITCH = "KILL_SWITCH"
    MODE_POLICY = "MODE_POLICY"
    MANUAL_OVERRIDE = "MANUAL_OVERRIDE"
    INTERNAL_SAFETY = "INTERNAL_SAFETY"
    CUSTOM = "CUSTOM"


class ConstraintDisposition(str, Enum):
    ALLOW = "ALLOW"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"


@dataclass(frozen=True)
class ConstraintCheck:
    name: str
    kind: ConstraintKind
    disposition: ConstraintDisposition
    reason: str = ""
    source: Optional[str] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ConstraintGateResult:
    status: ConstraintGateStatus
    passed: bool
    checks: tuple[ConstraintCheck, ...] = ()
    blocking_reasons: tuple[str, ...] = ()
    review_reasons: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()
    engine: str = CONSTRAINT_GATE_NAME
    version: str = CONSTRAINT_GATE_VERSION
    aic_reference: str = AIC_REFERENCE

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "passed": self.passed,
            "checks": [
                {
                    "name": c.name,
                    "kind": c.kind.value,
                    "disposition": c.disposition.value,
                    "reason": c.reason,
                    "source": c.source,
                } for c in self.checks
            ],
            "blocking_reasons": list(self.blocking_reasons),
            "review_reasons": list(self.review_reasons),
            "reasons": list(self.reasons),
            "errors": list(self.errors),
            "engine": self.engine,
            "version": self.version,
            "aic_reference": self.aic_reference,
        }


class ConstraintGate:
    def evaluate(
        self,
        checks: Optional[tuple[ConstraintCheck, ...]] = None,
    ) -> ConstraintGateResult:
        if not checks:
            return ConstraintGateResult(
                status=ConstraintGateStatus.LIMITED,
                passed=False,
                checks=(),
                reasons=(
                    "No constraint checks supplied. AIC-008 cannot "
                    "declare the action permissible without "
                    "constraint information.",
                ),
            )
        errors: list[str] = []
        for check in checks:
            if not isinstance(check, ConstraintCheck):
                errors.append(
                    "All checks must be ConstraintCheck instances."
                )
                continue
            if not check.name or not str(check.name).strip():
                errors.append("ConstraintCheck.name is required.")
            if not isinstance(check.kind, ConstraintKind):
                errors.append(
                    f"{check.name}: kind must be a ConstraintKind."
                )
            if not isinstance(
                check.disposition, ConstraintDisposition
            ):
                errors.append(
                    f"{check.name}: disposition must be a "
                    "ConstraintDisposition."
                )
        if errors:
            return ConstraintGateResult(
                status=ConstraintGateStatus.CLOSED,
                passed=False,
                checks=tuple(checks),
                errors=tuple(errors),
                reasons=("One or more constraint checks are invalid.",),
            )
        blocking = tuple(
            f"{c.name}: {c.reason or 'blocked'}"
            for c in checks
            if c.disposition == ConstraintDisposition.BLOCK
        )
        reviewing = tuple(
            f"{c.name}: {c.reason or 'review required'}"
            for c in checks
            if c.disposition == ConstraintDisposition.REVIEW
        )
        if blocking:
            return ConstraintGateResult(
                status=ConstraintGateStatus.CLOSED,
                passed=False,
                checks=tuple(checks),
                blocking_reasons=blocking,
                review_reasons=reviewing,
                reasons=("At least one constraint blocks execution.",),
            )
        if reviewing:
            return ConstraintGateResult(
                status=ConstraintGateStatus.LIMITED,
                passed=True,
                checks=tuple(checks),
                review_reasons=reviewing,
                reasons=(
                    "All blocking constraints passed, "
                    "but review is required.",
                ),
            )
        return ConstraintGateResult(
            status=ConstraintGateStatus.OPEN,
            passed=True,
            checks=tuple(checks),
            reasons=("All supplied constraints allow execution.",),
        )


def evaluate_constraints(
    checks: Optional[tuple[ConstraintCheck, ...]] = None,
) -> ConstraintGateResult:
    return ConstraintGate().evaluate(checks)


__all__ = [
    "CONSTRAINT_GATE_NAME", "CONSTRAINT_GATE_VERSION", "AIC_REFERENCE",
    "ConstraintGateStatus", "ConstraintKind", "ConstraintDisposition",
    "ConstraintCheck", "ConstraintGateResult",
    "ConstraintGate", "evaluate_constraints",
]
'''

# Also save config.py and grade_evaluator.py if they don't exist
if not (ROOT / "config.py").exists():
    print("NOTE: config.py missing. Please save it manually.")
if not (ROOT / "grade_evaluator.py").exists():
    print("NOTE: grade_evaluator.py missing. Please save it manually.")

# Write files
for filename, content in FILES.items():
    path = ROOT / filename
    path.write_text(content, encoding="utf-8")
    print(f"WROTE: {path}")

print()
print(f"DONE. Files in {ROOT}:")
for p in sorted(ROOT.glob("*.py")):
    print(f"  {p.name} ({p.stat().st_size} bytes)")