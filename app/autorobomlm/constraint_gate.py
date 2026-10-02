"""
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
