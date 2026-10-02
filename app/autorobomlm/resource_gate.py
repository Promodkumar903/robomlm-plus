"""
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
