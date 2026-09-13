# ============================================================
# PLUS_ORCHESTRATOR.PY — PART 1/5
# FOUNDATION + CONTRACTS + AUTHORITY BOUNDARIES
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Optional
from uuid import uuid4


# ============================================================
# ENGINE IDENTITY
# ============================================================

PLUS_ORCHESTRATOR_ENGINE = "ROBOMLM_PLUS_ORCHESTRATOR"
PLUS_ORCHESTRATOR_VERSION = "1.0"


# ============================================================
# STATUS / STATE ENUMS
# ============================================================

class OrchestratorStatus(str, Enum):
    READY = "READY"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    WARNING = "WARNING"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


class OrchestratorState(str, Enum):
    INITIALIZED = "INITIALIZED"
    DECISION_READY = "DECISION_READY"
    PREPARATION_READY = "PREPARATION_READY"
    MONITORING_READY = "MONITORING_READY"
    PROTECTION_READY = "PROTECTION_READY"
    RECONCILIATION_READY = "RECONCILIATION_READY"
    COMPLETE = "COMPLETE"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"


class OrchestratorDisposition(str, Enum):
    CONTINUE = "CONTINUE"
    REVIEW = "REVIEW"
    PROTECT = "PROTECT"
    BLOCK = "BLOCK"
    HOLD = "HOLD"
    UNKNOWN = "UNKNOWN"


class OrchestratorContractStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


class OrchestratorReadiness(str, Enum):
    NOT_READY = "NOT_READY"
    PARTIAL = "PARTIAL"
    READY = "READY"
    BLOCKED = "BLOCKED"


# ============================================================
# REQUEST CONTRACT
# ============================================================

@dataclass(frozen=True)
class PlusOrchestratorRequest:
    """
    Top-level ROBOMLM PLUS orchestration request.

    Upstream authority:
        D13 Decision
        Risk
        CAS

    PLUS role:
        Coordinate/refine downstream intelligence and
        operational state without replacing authority.
    """

    advanced_decision: Any

    execution_preparation: Optional[Any] = None
    position_monitor: Optional[Any] = None
    protection: Optional[Any] = None
    reconciliation: Optional[Any] = None

    market_context: Optional[Any] = None
    account_state: Optional[Any] = None
    execution_state: Optional[Any] = None

    metadata: Mapping[str, Any] = field(default_factory=dict)

    request_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []

        if self.advanced_decision is None:
            errors.append(
                "advanced_decision is required."
            )

        if not self.request_id:
            errors.append(
                "request_id is required."
            )

        if not isinstance(self.metadata, Mapping):
            errors.append(
                "metadata must be a Mapping."
            )

        return tuple(errors)


# ============================================================
# AUTHORITY REFERENCES
# ============================================================

@dataclass(frozen=True)
class OrchestratorDecisionReference:
    decision_id: Optional[str]
    direction: Optional[str]
    status: Optional[str]
    confidence: Optional[float]
    strength: Optional[float]
    raw_decision: Any
    source: str = "D13"


@dataclass(frozen=True)
class OrchestratorRiskReference:
    risk_id: Optional[str]
    status: Optional[str]
    risk_score: Optional[float]
    exposure: Optional[float]
    severity: Optional[str]
    raw_result: Any
    source: str = "RISK"


@dataclass(frozen=True)
class OrchestratorCASReference:
    cas_id: Optional[str]
    status: Optional[str]
    authorized: Optional[bool]
    reason: Optional[str]
    raw_result: Any
    source: str = "CAS"


# ============================================================
# DOWNSTREAM ENGINE REFERENCES
# ============================================================

@dataclass(frozen=True)
class OrchestratorPreparationReference:
    preparation_id: Optional[str]
    status: Optional[str]
    readiness: Optional[str]
    intent: Optional[str]
    raw_result: Any
    source: str = "EXECUTION_PREPARATION"


@dataclass(frozen=True)
class OrchestratorMonitorReference:
    monitor_id: Optional[str]
    status: Optional[str]
    health: Optional[str]
    disposition: Optional[str]
    requires_protection: bool
    requires_halt: bool
    raw_result: Any
    source: str = "POSITION_MONITOR"


@dataclass(frozen=True)
class OrchestratorProtectionReference:
    protection_id: Optional[str]
    status: Optional[str]
    protection_state: Optional[str]
    health: Optional[str]
    disposition: Optional[str]
    requires_protection: bool
    requires_block: bool
    raw_result: Any
    source: str = "PROTECTION"


@dataclass(frozen=True)
class OrchestratorReconciliationReference:
    reconciliation_id: Optional[str]
    status: Optional[str]
    reconciliation_state: Optional[str]
    health: Optional[str]
    disposition: Optional[str]
    requires_review: bool
    requires_protection: bool
    requires_block: bool
    raw_result: Any
    source: str = "RECONCILIATION"


# ============================================================
# CONTRACT VALIDATION
# ============================================================

@dataclass(frozen=True)
class OrchestratorContractValidation:
    status: OrchestratorContractStatus
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:
        return self.status == OrchestratorContractStatus.VALID


# ============================================================
# HELPER READERS
# ============================================================

def _po_read_value(
    source: Any,
    *names: str,
    default: Any = None,
) -> Any:
    if source is None:
        return default

    if isinstance(source, Mapping):
        for name in names:
            if name in source:
                return source[name]

    for name in names:
        try:
            value = getattr(source, name)
        except Exception:
            continue

        if value is not None:
            return value

    return default


def _po_text(
    value: Any,
) -> Optional[str]:
    if value is None:
        return None

    text = str(value).strip()

    return text if text else None


def _po_float(
    value: Any,
) -> Optional[float]:
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _po_bool(
    value: Any,
) -> Optional[bool]:
    if value is None:
        return None

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        normalized = value.strip().upper()

        if normalized in {
            "TRUE",
            "YES",
            "AUTHORIZED",
            "ALLOW",
            "ALLOWED",
        }:
            return True

        if normalized in {
            "FALSE",
            "NO",
            "DENIED",
            "BLOCKED",
            "REJECTED",
        }:
            return False

    return None


# ============================================================
# AUTHORITY ADAPTERS
# ============================================================

def build_orchestrator_decision_reference(
    decision: Any,
) -> OrchestratorDecisionReference:
    return OrchestratorDecisionReference(
        decision_id=_po_text(
            _po_read_value(
                decision,
                "decision_id",
                "id",
            )
        ),
        direction=_po_text(
            _po_read_value(
                decision,
                "direction",
                "decision",
                "disposition",
            )
        ),
        status=_po_text(
            _po_read_value(
                decision,
                "status",
            )
        ),
        confidence=_po_float(
            _po_read_value(
                decision,
                "confidence",
            )
        ),
        strength=_po_float(
            _po_read_value(
                decision,
                "strength",
            )
        ),
        raw_decision=decision,
    )


def build_orchestrator_risk_reference(
    risk: Any,
) -> OrchestratorRiskReference:
    return OrchestratorRiskReference(
        risk_id=_po_text(
            _po_read_value(
                risk,
                "risk_id",
                "id",
            )
        ),
        status=_po_text(
            _po_read_value(
                risk,
                "status",
            )
        ),
        risk_score=_po_float(
            _po_read_value(
                risk,
                "risk_score",
                "score",
            )
        ),
        exposure=_po_float(
            _po_read_value(
                risk,
                "exposure",
            )
        ),
        severity=_po_text(
            _po_read_value(
                risk,
                "severity",
            )
        ),
        raw_result=risk,
    )


def build_orchestrator_cas_reference(
    cas: Any,
) -> OrchestratorCASReference:
    return OrchestratorCASReference(
        cas_id=_po_text(
            _po_read_value(
                cas,
                "cas_id",
                "id",
            )
        ),
        status=_po_text(
            _po_read_value(
                cas,
                "status",
            )
        ),
        authorized=_po_bool(
            _po_read_value(
                cas,
                "authorized",
                "is_authorized",
            )
        ),
        reason=_po_text(
            _po_read_value(
                cas,
                "reason",
                "message",
            )
        ),
        raw_result=cas,
    )


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_plus_orchestrator_request(
    request: PlusOrchestratorRequest,
) -> OrchestratorContractValidation:
    if request is None:
        return OrchestratorContractValidation(
            status=OrchestratorContractStatus.INVALID,
            errors=("Request is None.",),
        )

    errors = request.validate()

    return OrchestratorContractValidation(
        status=(
            OrchestratorContractStatus.VALID
            if not errors
            else OrchestratorContractStatus.INVALID
        ),
        errors=errors,
    )


# ============================================================
# HARD AUTHORITY INVARIANTS
# ============================================================

ORCHESTRATOR_AUTHORITY_RULES = {
    "d13_is_decision_authority": True,
    "risk_is_risk_authority": True,
    "cas_is_authorization_authority": True,
    "plus_is_orchestration_layer": True,

    "direction_synthesis": False,
    "risk_recalculation": False,
    "authorization_creation": False,
    "execution_creation": False,
    "order_creation": False,
    "position_modification": False,
    "d13_override": False,
    "risk_override": False,
    "cas_override": False,
}


# ============================================================
# END OF PART 1/5
# ============================================================
# ============================================================
# PLUS_ORCHESTRATOR.PY — PART 2/5
# DOWNSTREAM REFERENCES + REQUIREMENTS + INTELLIGENCE
# ============================================================


# ============================================================
# DOWNSTREAM REFERENCE BUILDERS
# ============================================================

def build_orchestrator_preparation_reference(
    preparation: Any,
) -> OrchestratorPreparationReference:
    return OrchestratorPreparationReference(
        preparation_id=_po_text(
            _po_read_value(
                preparation,
                "preparation_id",
                "contract_id",
                "id",
            )
        ),
        status=_po_text(
            _po_read_value(preparation, "status")
        ),
        readiness=_po_text(
            _po_read_value(
                preparation,
                "readiness",
            )
        ),
        intent=_po_text(
            _po_read_value(
                preparation,
                "intent",
                "execution_intent",
            )
        ),
        raw_result=preparation,
    )


def build_orchestrator_monitor_reference(
    monitor: Any,
) -> OrchestratorMonitorReference:
    return OrchestratorMonitorReference(
        monitor_id=_po_text(
            _po_read_value(
                monitor,
                "monitor_id",
                "result_id",
                "id",
            )
        ),
        status=_po_text(
            _po_read_value(monitor, "status")
        ),
        health=_po_text(
            _po_read_value(monitor, "health")
        ),
        disposition=_po_text(
            _po_read_value(monitor, "disposition")
        ),
        requires_protection=bool(
            _po_bool(
                _po_read_value(
                    monitor,
                    "requires_protection",
                )
            )
        ),
        requires_halt=bool(
            _po_bool(
                _po_read_value(
                    monitor,
                    "requires_halt",
                )
            )
        ),
        raw_result=monitor,
    )


def build_orchestrator_protection_reference(
    protection: Any,
) -> OrchestratorProtectionReference:
    return OrchestratorProtectionReference(
        protection_id=_po_text(
            _po_read_value(
                protection,
                "protection_id",
                "result_id",
                "id",
            )
        ),
        status=_po_text(
            _po_read_value(protection, "status")
        ),
        protection_state=_po_text(
            _po_read_value(
                protection,
                "protection_state",
            )
        ),
        health=_po_text(
            _po_read_value(protection, "health")
        ),
        disposition=_po_text(
            _po_read_value(
                protection,
                "disposition",
            )
        ),
        requires_protection=bool(
            _po_bool(
                _po_read_value(
                    protection,
                    "requires_protection",
                )
            )
        ),
        requires_block=bool(
            _po_bool(
                _po_read_value(
                    protection,
                    "requires_block",
                )
            )
        ),
        raw_result=protection,
    )


def build_orchestrator_reconciliation_reference(
    reconciliation: Any,
) -> OrchestratorReconciliationReference:
    return OrchestratorReconciliationReference(
        reconciliation_id=_po_text(
            _po_read_value(
                reconciliation,
                "reconciliation_id",
                "result_id",
                "id",
            )
        ),
        status=_po_text(
            _po_read_value(
                reconciliation,
                "status",
            )
        ),
        reconciliation_state=_po_text(
            _po_read_value(
                reconciliation,
                "reconciliation_state",
            )
        ),
        health=_po_text(
            _po_read_value(
                reconciliation,
                "health",
            )
        ),
        disposition=_po_text(
            _po_read_value(
                reconciliation,
                "disposition",
            )
        ),
        requires_review=bool(
            _po_bool(
                _po_read_value(
                    reconciliation,
                    "requires_review",
                )
            )
        ),
        requires_protection=bool(
            _po_bool(
                _po_read_value(
                    reconciliation,
                    "requires_protection",
                )
            )
        ),
        requires_block=bool(
            _po_bool(
                _po_read_value(
                    reconciliation,
                    "requires_block",
                )
            )
        ),
        raw_result=reconciliation,
    )


# ============================================================
# ORCHESTRATION CONSISTENCY / DATA STATE
# ============================================================

class OrchestratorConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONFLICTING = "CONFLICTING"
    INSUFFICIENT = "INSUFFICIENT"


class OrchestratorDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"


@dataclass(frozen=True)
class OrchestratorRequirements:
    decision_available: bool
    risk_available: bool
    cas_available: bool

    preparation_available: bool
    monitor_available: bool
    protection_available: bool
    reconciliation_available: bool

    market_context_available: bool
    account_context_available: bool
    execution_context_available: bool

    decision_authority_valid: bool = False
    risk_authority_valid: bool = False
    cas_authority_valid: bool = False


@dataclass(frozen=True)
class OrchestratorIntelligence:
    consistency: OrchestratorConsistency
    data_state: OrchestratorDataState
    state: OrchestratorState
    readiness: OrchestratorReadiness
    disposition: OrchestratorDisposition

    decision: Optional[OrchestratorDecisionReference]
    risk: Optional[OrchestratorRiskReference]
    cas: Optional[OrchestratorCASReference]

    preparation: Optional[OrchestratorPreparationReference]
    monitor: Optional[OrchestratorMonitorReference]
    protection: Optional[OrchestratorProtectionReference]
    reconciliation: Optional[OrchestratorReconciliationReference]

    rationale: str
    warnings: tuple[str, ...] = ()
    source: str = PLUS_ORCHESTRATOR_ENGINE


@dataclass(frozen=True)
class PlusOrchestratorAssessment:
    intelligence: OrchestratorIntelligence
    requirements: OrchestratorRequirements

    decision: Optional[OrchestratorDecisionReference]
    risk: Optional[OrchestratorRiskReference]
    cas: Optional[OrchestratorCASReference]

    preparation: Optional[OrchestratorPreparationReference]
    monitor: Optional[OrchestratorMonitorReference]
    protection: Optional[OrchestratorProtectionReference]
    reconciliation: Optional[OrchestratorReconciliationReference]

    rationale: str
    warnings: tuple[str, ...] = ()


# ============================================================
# STATUS HELPERS
# ============================================================

def _po_normalized_text(
    value: Any,
) -> str:
    return str(value).strip().upper() if value is not None else ""


def _po_status_is_blocking(
    value: Any,
) -> bool:
    return _po_normalized_text(value) in {
        "BLOCKED",
        "DENIED",
        "REJECTED",
        "FAILED",
        "INVALID",
        "UNSAFE",
        "CRITICAL",
        "HALTED",
        "STOPPED",
    }


def _po_status_is_unknown(
    value: Any,
) -> bool:
    return _po_normalized_text(value) in {
        "",
        "UNKNOWN",
        "UNSPECIFIED",
        "NONE",
        "N/A",
        "NA",
    }


def _po_direction(
    value: Any,
) -> Optional[str]:
    direction = _po_normalized_text(value)

    if direction in {
        "UP",
        "LONG",
        "BULLISH",
        "BUY",
        "CALL",
    }:
        return "UP"

    if direction in {
        "DOWN",
        "SHORT",
        "BEARISH",
        "SELL",
        "PUT",
    }:
        return "DOWN"

    if direction in {
        "NEUTRAL",
        "FLAT",
    }:
        return "NEUTRAL"

    if direction == "HOLD":
        return "HOLD"

    return None


# ============================================================
# REQUIREMENTS EVALUATION
# ============================================================

def evaluate_orchestrator_requirements(
    request: PlusOrchestratorRequest,
) -> OrchestratorRequirements:
    decision = build_orchestrator_decision_reference(
        request.advanced_decision
    )

    risk_source = _po_read_value(
        request.advanced_decision,
        "risk",
        "risk_result",
    )

    cas_source = _po_read_value(
        request.advanced_decision,
        "cas",
        "cas_result",
    )

    risk_available = (
        risk_source is not None
        or request.metadata.get("risk") is not None
    )

    cas_available = (
        cas_source is not None
        or request.metadata.get("cas") is not None
    )

    decision_valid = (
        decision.raw_decision is not None
        and decision.direction is not None
        and not _po_status_is_blocking(decision.status)
    )

    risk_valid = (
        risk_available
        and not _po_status_is_blocking(
            _po_read_value(
                risk_source,
                "status",
            )
        )
    )

    cas_authorized = _po_bool(
        _po_read_value(
            cas_source,
            "authorized",
            "is_authorized",
        )
    )

    cas_valid = (
        cas_available
        and not _po_status_is_blocking(
            _po_read_value(
                cas_source,
                "status",
            )
        )
        and cas_authorized is not False
    )

    return OrchestratorRequirements(
        decision_available=request.advanced_decision is not None,
        risk_available=risk_available,
        cas_available=cas_available,
        preparation_available=(
            request.execution_preparation is not None
        ),
        monitor_available=(
            request.position_monitor is not None
        ),
        protection_available=(
            request.protection is not None
        ),
        reconciliation_available=(
            request.reconciliation is not None
        ),
        market_context_available=(
            request.market_context is not None
        ),
        account_context_available=(
            request.account_state is not None
        ),
        execution_context_available=(
            request.execution_state is not None
        ),
        decision_authority_valid=decision_valid,
        risk_authority_valid=risk_valid,
        cas_authority_valid=cas_valid,
    )


# ============================================================
# DATA STATE EVALUATION
# ============================================================

def evaluate_orchestrator_data_state(
    requirements: OrchestratorRequirements,
) -> OrchestratorDataState:
    if not requirements.decision_available:
        return OrchestratorDataState.MISSING

    if not requirements.risk_available:
        return OrchestratorDataState.PARTIAL

    if not requirements.cas_available:
        return OrchestratorDataState.PARTIAL

    if not requirements.decision_authority_valid:
        return OrchestratorDataState.PARTIAL

    if not requirements.risk_authority_valid:
        return OrchestratorDataState.PARTIAL

    if not requirements.cas_authority_valid:
        return OrchestratorDataState.PARTIAL

    return OrchestratorDataState.COMPLETE


# ============================================================
# CROSS-LAYER CONSISTENCY
# ============================================================

def evaluate_orchestrator_consistency(
    decision: Optional[OrchestratorDecisionReference],
    risk: Optional[OrchestratorRiskReference],
    cas: Optional[OrchestratorCASReference],
    preparation: Optional[OrchestratorPreparationReference],
    monitor: Optional[OrchestratorMonitorReference],
    protection: Optional[OrchestratorProtectionReference],
    reconciliation: Optional[OrchestratorReconciliationReference],
) -> OrchestratorConsistency:

    if decision is None:
        return OrchestratorConsistency.INSUFFICIENT

    if risk is not None and _po_status_is_blocking(risk.status):
        return OrchestratorConsistency.CONFLICTING

    if cas is not None:
        if _po_status_is_blocking(cas.status):
            return OrchestratorConsistency.CONFLICTING

        if cas.authorized is False:
            return OrchestratorConsistency.CONFLICTING

    if preparation is not None:
        if _po_status_is_blocking(preparation.status):
            return OrchestratorConsistency.CONFLICTING

    if monitor is not None:
        if (
            monitor.requires_halt
            or _po_status_is_blocking(monitor.status)
        ):
            return OrchestratorConsistency.CONFLICTING

    if protection is not None:
        if (
            protection.requires_block
            or _po_status_is_blocking(protection.status)
        ):
            return OrchestratorConsistency.CONFLICTING

    if reconciliation is not None:
        if (
            reconciliation.requires_block
            or _po_status_is_blocking(
                reconciliation.status
            )
        ):
            return OrchestratorConsistency.CONFLICTING

    return OrchestratorConsistency.CONSISTENT


# ============================================================
# ORCHESTRATOR STATE
# ============================================================

def evaluate_orchestrator_state(
    data_state: OrchestratorDataState,
    consistency: OrchestratorConsistency,
    preparation: Optional[OrchestratorPreparationReference],
    monitor: Optional[OrchestratorMonitorReference],
    protection: Optional[OrchestratorProtectionReference],
    reconciliation: Optional[OrchestratorReconciliationReference],
) -> OrchestratorState:

    if data_state == OrchestratorDataState.MISSING:
        return OrchestratorState.UNKNOWN

    if consistency == OrchestratorConsistency.CONFLICTING:
        return OrchestratorState.BLOCKED

    if preparation is not None:
        if (
            _po_normalized_text(preparation.readiness)
            in {
                "EXECUTION_READY",
                "PREPARATION_READY",
            }
        ):
            state = OrchestratorState.PREPARATION_READY
        else:
            state = OrchestratorState.DECISION_READY
    else:
        state = OrchestratorState.DECISION_READY

    if monitor is not None:
        state = OrchestratorState.MONITORING_READY

    if protection is not None:
        state = OrchestratorState.PROTECTION_READY

    if reconciliation is not None:
        state = OrchestratorState.RECONCILIATION_READY

    return state


# ============================================================
# END OF PART 2/5
# ============================================================
# ============================================================
# PLUS_ORCHESTRATOR.PY — PART 3/5
# ASSESSMENT + RESULT + CONTRACT
# ============================================================


# ============================================================
# ORCHESTRATOR RESULT STATE
# ============================================================

class OrchestratorActionState(str, Enum):
    NONE = "NONE"
    REVIEW = "REVIEW"
    PROTECT = "PROTECT"
    BLOCK = "BLOCK"


class OrchestratorContractState(str, Enum):
    VALID = "VALID"
    INCOMPLETE = "INCOMPLETE"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


# ============================================================
# RESULT CONTRACT
# ============================================================

@dataclass(frozen=True)
class PlusOrchestratorResult:
    request_id: str
    result_id: str

    status: OrchestratorStatus
    state: OrchestratorState
    readiness: OrchestratorReadiness
    consistency: OrchestratorConsistency
    data_state: OrchestratorDataState
    disposition: OrchestratorDisposition
    action_state: OrchestratorActionState

    decision: Optional[OrchestratorDecisionReference]
    risk: Optional[OrchestratorRiskReference]
    cas: Optional[OrchestratorCASReference]

    preparation: Optional[OrchestratorPreparationReference]
    monitor: Optional[OrchestratorMonitorReference]
    protection: Optional[OrchestratorProtectionReference]
    reconciliation: Optional[OrchestratorReconciliationReference]

    rationale: str
    warnings: tuple[str, ...] = ()

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def is_valid(self) -> bool:
        return bool(
            self.request_id
            and self.result_id
            and self.status != OrchestratorStatus.INVALID
            and self.decision is not None
        )

    @property
    def requires_review(self) -> bool:
        return self.disposition == OrchestratorDisposition.REVIEW

    @property
    def requires_protection(self) -> bool:
        return self.disposition == OrchestratorDisposition.PROTECT

    @property
    def requires_block(self) -> bool:
        return (
            self.disposition == OrchestratorDisposition.BLOCK
            or self.state == OrchestratorState.BLOCKED
        )

    @property
    def is_execution_request(self) -> bool:
        return False


@dataclass(frozen=True)
class PlusOrchestratorContract:
    orchestrator_id: str
    request_id: str

    state: OrchestratorContractState
    result: PlusOrchestratorResult
    action_state: OrchestratorActionState

    rationale: str
    warnings: tuple[str, ...] = ()

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def is_valid(self) -> bool:
        return bool(
            self.orchestrator_id
            and self.request_id
            and self.result is not None
            and self.result.is_valid
            and self.state == OrchestratorContractState.VALID
        )

    @property
    def is_action_request(self) -> bool:
        return False


# ============================================================
# READINESS / DISPOSITION EVALUATION
# ============================================================

def evaluate_orchestrator_readiness(
    data_state: OrchestratorDataState,
    consistency: OrchestratorConsistency,
    requirements: OrchestratorRequirements,
) -> OrchestratorReadiness:

    if consistency == OrchestratorConsistency.CONFLICTING:
        return OrchestratorReadiness.BLOCKED

    if data_state == OrchestratorDataState.MISSING:
        return OrchestratorReadiness.NOT_READY

    if data_state == OrchestratorDataState.PARTIAL:
        return OrchestratorReadiness.PARTIAL

    if not requirements.decision_authority_valid:
        return OrchestratorReadiness.PARTIAL

    if not requirements.risk_authority_valid:
        return OrchestratorReadiness.PARTIAL

    if not requirements.cas_authority_valid:
        return OrchestratorReadiness.PARTIAL

    return OrchestratorReadiness.READY


def evaluate_orchestrator_disposition(
    consistency: OrchestratorConsistency,
    readiness: OrchestratorReadiness,
    monitor: Optional[OrchestratorMonitorReference],
    protection: Optional[OrchestratorProtectionReference],
    reconciliation: Optional[OrchestratorReconciliationReference],
) -> OrchestratorDisposition:

    if consistency == OrchestratorConsistency.CONFLICTING:
        return OrchestratorDisposition.BLOCK

    if readiness == OrchestratorReadiness.BLOCKED:
        return OrchestratorDisposition.BLOCK

    if monitor is not None:
        if monitor.requires_halt:
            return OrchestratorDisposition.BLOCK

        if monitor.requires_protection:
            return OrchestratorDisposition.PROTECT

    if protection is not None:
        if protection.requires_block:
            return OrchestratorDisposition.BLOCK

        if protection.requires_protection:
            return OrchestratorDisposition.PROTECT

    if reconciliation is not None:
        if reconciliation.requires_block:
            return OrchestratorDisposition.BLOCK

        if reconciliation.requires_protection:
            return OrchestratorDisposition.PROTECT

        if reconciliation.requires_review:
            return OrchestratorDisposition.REVIEW

    if readiness == OrchestratorReadiness.PARTIAL:
        return OrchestratorDisposition.REVIEW

    if readiness == OrchestratorReadiness.NOT_READY:
        return OrchestratorDisposition.HOLD

    return OrchestratorDisposition.CONTINUE


def _po_action_state(
    disposition: OrchestratorDisposition,
) -> OrchestratorActionState:

    if disposition == OrchestratorDisposition.BLOCK:
        return OrchestratorActionState.BLOCK

    if disposition == OrchestratorDisposition.PROTECT:
        return OrchestratorActionState.PROTECT

    if disposition == OrchestratorDisposition.REVIEW:
        return OrchestratorActionState.REVIEW

    return OrchestratorActionState.NONE


# ============================================================
# INTELLIGENCE BUILDER
# ============================================================

def build_orchestrator_intelligence(
    request: PlusOrchestratorRequest,
    requirements: OrchestratorRequirements,
) -> OrchestratorIntelligence:

    decision = build_orchestrator_decision_reference(
        request.advanced_decision
    )

    risk_source = _po_read_value(
        request.advanced_decision,
        "risk",
        "risk_result",
    )

    cas_source = _po_read_value(
        request.advanced_decision,
        "cas",
        "cas_result",
    )

    # Metadata is an optional transport path only.
    if risk_source is None:
        risk_source = request.metadata.get("risk")

    if cas_source is None:
        cas_source = request.metadata.get("cas")

    risk = (
        build_orchestrator_risk_reference(risk_source)
        if risk_source is not None
        else None
    )

    cas = (
        build_orchestrator_cas_reference(cas_source)
        if cas_source is not None
        else None
    )

    preparation = (
        build_orchestrator_preparation_reference(
            request.execution_preparation
        )
        if request.execution_preparation is not None
        else None
    )

    monitor = (
        build_orchestrator_monitor_reference(
            request.position_monitor
        )
        if request.position_monitor is not None
        else None
    )

    protection = (
        build_orchestrator_protection_reference(
            request.protection
        )
        if request.protection is not None
        else None
    )

    reconciliation = (
        build_orchestrator_reconciliation_reference(
            request.reconciliation
        )
        if request.reconciliation is not None
        else None
    )

    data_state = evaluate_orchestrator_data_state(
        requirements
    )

    consistency = evaluate_orchestrator_consistency(
        decision=decision,
        risk=risk,
        cas=cas,
        preparation=preparation,
        monitor=monitor,
        protection=protection,
        reconciliation=reconciliation,
    )

    state = evaluate_orchestrator_state(
        data_state=data_state,
        consistency=consistency,
        preparation=preparation,
        monitor=monitor,
        protection=protection,
        reconciliation=reconciliation,
    )

    readiness = evaluate_orchestrator_readiness(
        data_state=data_state,
        consistency=consistency,
        requirements=requirements,
    )

    disposition = evaluate_orchestrator_disposition(
        consistency=consistency,
        readiness=readiness,
        monitor=monitor,
        protection=protection,
        reconciliation=reconciliation,
    )

    warnings: list[str] = []

    if data_state == OrchestratorDataState.PARTIAL:
        warnings.append(
            "Orchestration context is partially available."
        )

    if consistency == OrchestratorConsistency.CONFLICTING:
        warnings.append(
            "A blocking or conflicting downstream state was detected."
        )

    if disposition == OrchestratorDisposition.PROTECT:
        warnings.append(
            "Protection control signal detected; no protection "
            "action is created by the orchestrator."
        )

    if disposition == OrchestratorDisposition.BLOCK:
        warnings.append(
            "BLOCK control signal detected; no halt or execution "
            "action is created by the orchestrator."
        )

    if cas is not None and cas.authorized is True:
        warnings.append(
            "CAS authorization is preserved as upstream authority; "
            "orchestrator does not create authorization."
        )

    rationale = (
        "ROBOMLM PLUS orchestration preserves upstream D13, Risk, "
        "and CAS authority while coordinating downstream "
        "preparation, monitoring, protection, and reconciliation."
    )

    return OrchestratorIntelligence(
        consistency=consistency,
        data_state=data_state,
        state=state,
        readiness=readiness,
        disposition=disposition,
        decision=decision,
        risk=risk,
        cas=cas,
        preparation=preparation,
        monitor=monitor,
        protection=protection,
        reconciliation=reconciliation,
        rationale=rationale,
        warnings=tuple(warnings),
        source=PLUS_ORCHESTRATOR_ENGINE,
    )


# ============================================================
# ASSESSMENT BUILDER
# ============================================================

def build_plus_orchestrator_assessment(
    request: PlusOrchestratorRequest,
) -> PlusOrchestratorAssessment:

    requirements = evaluate_orchestrator_requirements(
        request
    )

    intelligence = build_orchestrator_intelligence(
        request=request,
        requirements=requirements,
    )

    return PlusOrchestratorAssessment(
        intelligence=intelligence,
        requirements=requirements,

        decision=intelligence.decision,
        risk=intelligence.risk,
        cas=intelligence.cas,

        preparation=intelligence.preparation,
        monitor=intelligence.monitor,
        protection=intelligence.protection,
        reconciliation=intelligence.reconciliation,

        rationale=intelligence.rationale,
        warnings=intelligence.warnings,
    )


# ============================================================
# RESULT BUILDER
# ============================================================

def _po_result_status(
    intelligence: OrchestratorIntelligence,
) -> OrchestratorStatus:

    if intelligence.consistency == (
        OrchestratorConsistency.CONFLICTING
    ):
        return OrchestratorStatus.BLOCKED

    if intelligence.data_state == OrchestratorDataState.MISSING:
        return OrchestratorStatus.INVALID

    if intelligence.disposition == OrchestratorDisposition.BLOCK:
        return OrchestratorStatus.BLOCKED

    if intelligence.disposition in {
        OrchestratorDisposition.REVIEW,
        OrchestratorDisposition.PROTECT,
    }:
        return OrchestratorStatus.WARNING

    return OrchestratorStatus.COMPLETED


def build_plus_orchestrator_result(
    request: PlusOrchestratorRequest,
    assessment: PlusOrchestratorAssessment,
) -> PlusOrchestratorResult:

    intelligence = assessment.intelligence

    return PlusOrchestratorResult(
        request_id=request.request_id,
        result_id=str(uuid4()),
        status=_po_result_status(intelligence),
        state=intelligence.state,
        readiness=intelligence.readiness,
        consistency=intelligence.consistency,
        data_state=intelligence.data_state,
        disposition=intelligence.disposition,
        action_state=_po_action_state(
            intelligence.disposition
        ),
        decision=assessment.decision,
        risk=assessment.risk,
        cas=assessment.cas,
        preparation=assessment.preparation,
        monitor=assessment.monitor,
        protection=assessment.protection,
        reconciliation=assessment.reconciliation,
        rationale=assessment.rationale,
        warnings=assessment.warnings,
    )


# ============================================================
# CONTRACT BUILDER
# ============================================================

def _po_contract_state(
    result: PlusOrchestratorResult,
) -> OrchestratorContractState:

    if not result.is_valid:
        return OrchestratorContractState.INVALID

    if result.requires_block:
        return OrchestratorContractState.BLOCKED

    if result.data_state in {
        OrchestratorDataState.MISSING,
        OrchestratorDataState.PARTIAL,
    }:
        return OrchestratorContractState.INCOMPLETE

    return OrchestratorContractState.VALID


def build_plus_orchestrator_contract(
    request: PlusOrchestratorRequest,
    result: PlusOrchestratorResult,
) -> PlusOrchestratorContract:

    return PlusOrchestratorContract(
        orchestrator_id=str(uuid4()),
        request_id=request.request_id,
        state=_po_contract_state(result),
        result=result,
        action_state=result.action_state,
        rationale=result.rationale,
        warnings=result.warnings,
    )


# ============================================================
# DOWNSTREAM SAFETY GATE
# ============================================================

def is_plus_orchestrator_safe_to_forward(
    contract: PlusOrchestratorContract,
) -> bool:

    if contract is None or not contract.is_valid:
        return False

    if contract.is_action_request:
        return False

    if contract.result.requires_block:
        return False

    if contract.result.consistency == (
        OrchestratorConsistency.CONFLICTING
    ):
        return False

    if contract.result.readiness != OrchestratorReadiness.READY:
        return False

    return contract.state == OrchestratorContractState.VALID


# ============================================================
# RESULT VALIDATION
# ============================================================

def validate_plus_orchestrator_result(
    result: PlusOrchestratorResult,
) -> OrchestratorContractValidation:

    errors: list[str] = []
    warnings: list[str] = []

    if result is None:
        return OrchestratorContractValidation(
            status=OrchestratorContractStatus.INVALID,
            errors=("Result is None.",),
        )

    if not result.request_id:
        errors.append("Missing request_id.")

    if not result.result_id:
        errors.append("Missing result_id.")

    if result.decision is None:
        errors.append(
            "D13 decision reference is required."
        )

    if result.status == OrchestratorStatus.INVALID:
        errors.append(
            "Orchestrator result is INVALID."
        )

    if result.consistency == (
        OrchestratorConsistency.CONFLICTING
    ):
        warnings.append(
            "Orchestrator detected a conflicting authority/state."
        )

    if result.requires_block:
        warnings.append(
            "Orchestrator requires blocking; no execution action "
            "has been created."
        )

    if result.is_execution_request:
        errors.append(
            "Orchestrator result cannot be an execution request."
        )

    return OrchestratorContractValidation(
        status=(
            OrchestratorContractStatus.VALID
            if not errors
            else OrchestratorContractStatus.INVALID
        ),
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


# ============================================================
# END OF PART 3/5
# ============================================================
# ============================================================
# PLUS_ORCHESTRATOR.PY — PART 4/5
# ENGINE + ORCHESTRATION PIPELINE + PUBLIC ENGINE
# ============================================================


class PlusOrchestratorEngine:
    """
    ROBOMLM PLUS top-level orchestration engine.

    Pipeline:
        D13 / Risk / CAS
              ↓
        Advanced Decision
              ↓
        Execution Preparation
              ↓
        Position Monitor
              ↓
        Protection
              ↓
        Reconciliation
              ↓
        Orchestrated Control State

    This engine coordinates state only.

    It does NOT:
        - create orders
        - execute trades
        - create authorization
        - modify positions
        - calculate SL/TP
        - calculate quantity
        - override D13
        - override Risk
        - override CAS
    """

    ENGINE_NAME = PLUS_ORCHESTRATOR_ENGINE
    ENGINE_VERSION = PLUS_ORCHESTRATOR_VERSION

    def validate_request(
        self,
        request: PlusOrchestratorRequest,
    ) -> OrchestratorContractValidation:
        return validate_plus_orchestrator_request(request)

    def _invalid_contract(
        self,
        request: PlusOrchestratorRequest,
        errors: tuple[str, ...],
    ) -> PlusOrchestratorContract:

        now = datetime.now(timezone.utc)

        decision = (
            build_orchestrator_decision_reference(
                request.advanced_decision
            )
            if request is not None
            and request.advanced_decision is not None
            else None
        )

        result = PlusOrchestratorResult(
            request_id=(
                request.request_id
                if request is not None
                else ""
            ),
            result_id=str(uuid4()),
            status=OrchestratorStatus.INVALID,
            state=OrchestratorState.UNKNOWN,
            readiness=OrchestratorReadiness.NOT_READY,
            consistency=OrchestratorConsistency.INSUFFICIENT,
            data_state=OrchestratorDataState.MISSING,
            disposition=OrchestratorDisposition.HOLD,
            action_state=OrchestratorActionState.NONE,
            decision=decision,
            risk=None,
            cas=None,
            preparation=None,
            monitor=None,
            protection=None,
            reconciliation=None,
            rationale="Invalid PLUS orchestrator request.",
            warnings=tuple(errors),
            created_at=now,
        )

        return PlusOrchestratorContract(
            orchestrator_id=str(uuid4()),
            request_id=(
                request.request_id
                if request is not None
                else ""
            ),
            state=OrchestratorContractState.INVALID,
            result=result,
            action_state=OrchestratorActionState.NONE,
            rationale="PLUS orchestrator validation failed.",
            warnings=tuple(errors),
            created_at=now,
        )

    def process(
        self,
        request: PlusOrchestratorRequest,
    ) -> PlusOrchestratorContract:
        try:
            validation = self.validate_request(request)

            if not validation.is_valid:
                return self._invalid_contract(
                    request,
                    validation.errors,
                )

            assessment = build_plus_orchestrator_assessment(
                request
            )

            result = build_plus_orchestrator_result(
                request=request,
                assessment=assessment,
            )

            result_validation = (
                validate_plus_orchestrator_result(result)
            )

            if not result_validation.is_valid:
                return self._invalid_contract(
                    request,
                    result_validation.errors,
                )

            contract = build_plus_orchestrator_contract(
                request=request,
                result=result,
            )

            # A contract cannot claim VALID if its own
            # downstream state is blocked.
            if result.requires_block:
                contract = PlusOrchestratorContract(
                    orchestrator_id=contract.orchestrator_id,
                    request_id=contract.request_id,
                    state=OrchestratorContractState.BLOCKED,
                    result=contract.result,
                    action_state=OrchestratorActionState.BLOCK,
                    rationale=contract.rationale,
                    warnings=contract.warnings,
                    created_at=contract.created_at,
                )

            return contract

        except Exception as exc:
            return self._invalid_contract(
                request,
                (
                    f"PLUS orchestration processing failure: "
                    f"{exc}",
                ),
            )

    def evaluate(
        self,
        request: PlusOrchestratorRequest,
    ) -> PlusOrchestratorContract:
        return self.process(request)

    def is_ready(
        self,
        contract: PlusOrchestratorContract,
    ) -> bool:
        if contract is None or not contract.is_valid:
            return False

        return (
            contract.result.readiness
            == OrchestratorReadiness.READY
        )

    def is_safe_to_forward(
        self,
        contract: PlusOrchestratorContract,
    ) -> bool:
        return is_plus_orchestrator_safe_to_forward(
            contract
        )

    def requires_review(
        self,
        contract: PlusOrchestratorContract,
    ) -> bool:
        if contract is None or not contract.is_valid:
            return True

        return contract.result.requires_review

    def requires_protection(
        self,
        contract: PlusOrchestratorContract,
    ) -> bool:
        if contract is None or not contract.is_valid:
            return False

        return contract.result.requires_protection

    def requires_block(
        self,
        contract: PlusOrchestratorContract,
    ) -> bool:
        if contract is None or not contract.is_valid:
            return True

        return contract.result.requires_block

    def orchestration_state(
        self,
        contract: PlusOrchestratorContract,
    ) -> OrchestratorState:
        if contract is None or contract.result is None:
            return OrchestratorState.UNKNOWN

        return contract.result.state

    def audit_summary(
        self,
        contract: Optional[PlusOrchestratorContract] = None,
    ) -> dict[str, Any]:

        if contract is None:
            return {
                "engine": self.ENGINE_NAME,
                "version": self.ENGINE_VERSION,
                "status": "READY",
                "contract_valid": False,
                "ready": False,
                "safe_for_downstream": False,
                "requires_review": False,
                "requires_protection": False,
                "requires_block": False,

                # Hard invariants.
                "direction_synthesized": False,
                "risk_recalculated": False,
                "authorization_created": False,
                "execution_created": False,
                "order_created": False,
                "position_modified": False,
                "d13_overridden": False,
                "risk_overridden": False,
                "cas_overridden": False,
            }

        result = contract.result

        return {
            "engine": self.ENGINE_NAME,
            "version": self.ENGINE_VERSION,

            "status": result.status.value,
            "contract_state": contract.state.value,
            "orchestrator_state": result.state.value,
            "readiness": result.readiness.value,
            "consistency": result.consistency.value,
            "data_state": result.data_state.value,
            "disposition": result.disposition.value,
            "action_state": result.action_state.value,

            "contract_valid": contract.is_valid,
            "result_valid": result.is_valid,
            "ready": self.is_ready(contract),
            "safe_for_downstream": (
                self.is_safe_to_forward(contract)
            ),

            "requires_review": self.requires_review(contract),
            "requires_protection": (
                self.requires_protection(contract)
            ),
            "requires_block": self.requires_block(contract),

            # Authority preservation.
            "d13_authority_preserved": True,
            "risk_authority_preserved": True,
            "cas_authority_preserved": True,
            "plus_is_orchestration_layer": True,

            # Hard safety invariants.
            "direction_synthesized": False,
            "risk_recalculated": False,
            "authorization_created": False,
            "execution_created": False,
            "order_created": False,
            "position_modified": False,
            "correction_created": False,
            "trading_parameter_calculated": False,
            "d13_overridden": False,
            "risk_overridden": False,
            "cas_overridden": False,
        }


# ============================================================
# PUBLIC ENGINE INSTANCE
# ============================================================

plus_orchestrator_engine = PlusOrchestratorEngine()


# ============================================================
# PUBLIC PROCESSING API
# ============================================================

def orchestrate_plus(
    request: PlusOrchestratorRequest,
) -> PlusOrchestratorContract:
    return plus_orchestrator_engine.process(request)


def evaluate_plus_orchestration(
    request: PlusOrchestratorRequest,
) -> PlusOrchestratorContract:
    return plus_orchestrator_engine.evaluate(request)


def plus_orchestration_ready(
    contract: PlusOrchestratorContract,
) -> bool:
    return plus_orchestrator_engine.is_ready(contract)


def plus_orchestration_safe(
    contract: PlusOrchestratorContract,
) -> bool:
    return plus_orchestrator_engine.is_safe_to_forward(
        contract
    )


def plus_orchestration_requires_review(
    contract: PlusOrchestratorContract,
) -> bool:
    return plus_orchestrator_engine.requires_review(
        contract
    )


def plus_orchestration_requires_protection(
    contract: PlusOrchestratorContract,
) -> bool:
    return plus_orchestrator_engine.requires_protection(
        contract
    )


def plus_orchestration_requires_block(
    contract: PlusOrchestratorContract,
) -> bool:
    return plus_orchestrator_engine.requires_block(
        contract
    )


def plus_orchestration_state(
    contract: PlusOrchestratorContract,
) -> OrchestratorState:
    return plus_orchestrator_engine.orchestration_state(
        contract
    )


def plus_orchestration_audit(
    contract: Optional[PlusOrchestratorContract] = None,
) -> dict[str, Any]:
    return plus_orchestrator_engine.audit_summary(
        contract
    )


# ============================================================
# ENGINE HEALTH / INFORMATION
# ============================================================

def plus_orchestrator_health_check() -> dict[str, Any]:
    return {
        "engine": PLUS_ORCHESTRATOR_ENGINE,
        "version": PLUS_ORCHESTRATOR_VERSION,
        "status": "READY",

        "pipeline": (
            "D13_RISK_CAS"
            "->ADVANCED_DECISION"
            "->EXECUTION_PREPARATION"
            "->POSITION_MONITOR"
            "->PROTECTION"
            "->RECONCILIATION"
        ),

        "d13_authority_preserved": True,
        "risk_authority_preserved": True,
        "cas_authority_preserved": True,

        "direction_synthesis": False,
        "risk_recalculation": False,
        "authorization_creation": False,
        "execution_creation": False,
        "order_creation": False,
        "position_modification": False,
        "d13_override": False,
        "risk_override": False,
        "cas_override": False,

        "fail_closed": True,
    }


def get_plus_orchestrator_engine_info() -> dict[str, Any]:
    return {
        "engine": PLUS_ORCHESTRATOR_ENGINE,
        "version": PLUS_ORCHESTRATOR_VERSION,
        "role": (
            "ROBOMLM_PLUS_TOP_LEVEL_ORCHESTRATION"
        ),
        "layer": "ROBOMLM_PLUS",
        "authority": "COORDINATION_ONLY",

        "upstream_authorities": [
            "D13",
            "RISK",
            "CAS",
        ],

        "downstream_layers": [
            "ADVANCED_DECISION",
            "EXECUTION_PREPARATION",
            "POSITION_MONITOR",
            "PROTECTION",
            "RECONCILIATION",
        ],

        "creates_execution": False,
        "creates_order": False,
        "creates_authorization": False,
        "modifies_position": False,
        "calculates_trading_parameters": False,
        "overrides_d13": False,
        "overrides_risk": False,
        "overrides_cas": False,
        "fail_closed": True,
    }


# Compatibility alias.
PlusOrchestrator = PlusOrchestratorEngine


# ============================================================
# END OF PART 4/5
# ============================================================
# ============================================================
# PART 5/5 — SERIALIZATION • INTEGRITY • HEALTH • EXPORTS
# ============================================================

def _po_enum_value(value: Any) -> Any:
    """Return stable enum/string representation."""
    return value.value if isinstance(value, Enum) else value


def _po_safe_dict(value: Any) -> dict[str, Any]:
    """Best-effort stable mapping conversion."""
    if value is None:
        return {}
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "to_dict"):
        try:
            result = value.to_dict()
            return dict(result) if isinstance(result, Mapping) else {}
        except Exception:
            return {}
    if hasattr(value, "__dict__"):
        try:
            return dict(value.__dict__)
        except Exception:
            return {}
    return {}


def plus_orchestrator_to_dict(
    contract: PlusOrchestratorContract,
) -> dict[str, Any]:
    """Serialize orchestrator contract without creating any action."""
    if contract is None:
        return {
            "valid": False,
            "error": "contract_is_none",
        }

    result = contract.result

    return {
        "orchestrator_id": contract.orchestrator_id,
        "request_id": contract.request_id,
        "state": _po_enum_value(contract.state),
        "action_state": _po_enum_value(contract.action_state),
        "is_valid": contract.is_valid,
        "is_action_request": contract.is_action_request,
        "result": {
            "result_id": result.result_id,
            "request_id": result.request_id,
            "status": _po_enum_value(result.status),
            "state": _po_enum_value(result.state),
            "readiness": _po_enum_value(result.readiness),
            "consistency": _po_enum_value(result.consistency),
            "data_state": _po_enum_value(result.data_state),
            "disposition": _po_enum_value(result.disposition),
            "action_state": _po_enum_value(result.action_state),
            "decision": _po_safe_dict(result.decision),
            "risk": _po_safe_dict(result.risk),
            "cas": _po_safe_dict(result.cas),
            "preparation": _po_safe_dict(result.preparation),
            "monitor": _po_safe_dict(result.monitor),
            "protection": _po_safe_dict(result.protection),
            "reconciliation": _po_safe_dict(result.reconciliation),
            "rationale": list(result.rationale),
            "warnings": list(result.warnings),
        },
        "rationale": list(contract.rationale),
        "warnings": list(contract.warnings),
        "integrity": {
            "d13_override": False,
            "risk_override": False,
            "cas_override": False,
            "direction_synthesized": False,
            "authorization_created": False,
            "execution_created": False,
            "order_created": False,
            "position_modified": False,
        },
    }


def validate_plus_orchestrator_contract(
    contract: PlusOrchestratorContract,
) -> OrchestratorContractValidation:
    """Validate final orchestration contract and authority boundaries."""
    errors: list[str] = []
    warnings: list[str] = []

    if contract is None:
        return OrchestratorContractValidation(
            status=OrchestratorContractStatus.INVALID,
            errors=("contract_is_none",),
        )

    if not contract.orchestrator_id:
        errors.append("missing_orchestrator_id")

    if not contract.request_id:
        errors.append("missing_request_id")

    if contract.result is None:
        errors.append("missing_result")
    else:
        if contract.result.request_id != contract.request_id:
            errors.append("request_id_mismatch")

        result_check = validate_plus_orchestrator_result(contract.result)
        errors.extend(result_check.errors)
        warnings.extend(result_check.warnings)

        if contract.result.is_execution_request:
            errors.append("execution_request_created")

        if contract.result.requires_block:
            warnings.append("orchestration_requires_block")

        if contract.result.requires_review:
            warnings.append("orchestration_requires_review")

        if contract.result.requires_protection:
            warnings.append("orchestration_requires_protection")

    if contract.is_action_request:
        errors.append("action_request_created")

    if contract.state == OrchestratorContractState.INVALID:
        errors.append("contract_state_invalid")

    if errors:
        return OrchestratorContractValidation(
            status=OrchestratorContractStatus.INVALID,
            errors=tuple(dict.fromkeys(errors)),
        )

    return OrchestratorContractValidation(
        status=OrchestratorContractStatus.VALID,
        errors=(),
    )


def plus_orchestrator_integrity_check(
    contract: PlusOrchestratorContract,
) -> dict[str, Any]:
    """Final non-executing integrity audit."""
    validation = validate_plus_orchestrator_contract(contract)

    if contract is None:
        return {
            "engine": PLUS_ORCHESTRATOR_ENGINE,
            "version": PLUS_ORCHESTRATOR_VERSION,
            "valid": False,
            "safe_to_forward": False,
            "errors": list(validation.errors),
            "warnings": list(validation.warnings),
        }

    result = contract.result

    safe = is_plus_orchestrator_safe_to_forward(contract)

    return {
        "engine": PLUS_ORCHESTRATOR_ENGINE,
        "version": PLUS_ORCHESTRATOR_VERSION,
        "valid": validation.is_valid,
        "contract_state": _po_enum_value(contract.state),
        "orchestrator_state": (
            _po_enum_value(result.state) if result else None
        ),
        "readiness": (
            _po_enum_value(result.readiness) if result else None
        ),
        "consistency": (
            _po_enum_value(result.consistency) if result else None
        ),
        "disposition": (
            _po_enum_value(result.disposition) if result else None
        ),
        "safe_to_forward": safe,
        "requires_review": bool(
            result.requires_review if result else False
        ),
        "requires_protection": bool(
            result.requires_protection if result else False
        ),
        "requires_block": bool(
            result.requires_block if result else False
        ),
        "authority": {
            "d13_is_decision_authority": True,
            "risk_is_risk_authority": True,
            "cas_is_authorization_authority": True,
            "plus_is_orchestration_layer": True,
        },
        "forbidden_actions": {
            "direction_synthesis": False,
            "risk_recalculation": False,
            "authorization_creation": False,
            "execution_creation": False,
            "order_creation": False,
            "position_modification": False,
            "d13_override": False,
            "risk_override": False,
            "cas_override": False,
        },
        "errors": list(validation.errors),
        "warnings": list(validation.warnings),
    }


def verify_plus_orchestrator_integrity(
    contract: PlusOrchestratorContract,
) -> bool:
    """Boolean integrity gate."""
    audit = plus_orchestrator_integrity_check(contract)
    return bool(audit["valid"] and audit["safe_to_forward"])


def run_plus_orchestrator_health_check() -> dict[str, Any]:
    """Runtime-independent structural health check."""
    health = plus_orchestrator_health_check()

    return {
        **health,
        "integrity_layer_present": True,
        "serialization_present": True,
        "contract_validation_present": True,
        "fail_closed": True,
    }


__all__ = [
    # Constants
    "PLUS_ORCHESTRATOR_ENGINE",
    "PLUS_ORCHESTRATOR_VERSION",

    # Enums
    "OrchestratorStatus",
    "OrchestratorState",
    "OrchestratorDisposition",
    "OrchestratorContractStatus",
    "OrchestratorReadiness",
    "OrchestratorConsistency",
    "OrchestratorDataState",
    "OrchestratorActionState",
    "OrchestratorContractState",

    # Contracts / requests
    "PlusOrchestratorRequest",
    "OrchestratorContractValidation",
    "PlusOrchestratorResult",
    "PlusOrchestratorContract",

    # References
    "OrchestratorDecisionReference",
    "OrchestratorRiskReference",
    "OrchestratorCASReference",
    "OrchestratorPreparationReference",
    "OrchestratorMonitorReference",
    "OrchestratorProtectionReference",
    "OrchestratorReconciliationReference",

    # Assessment / intelligence
    "OrchestratorRequirements",
    "OrchestratorIntelligence",
    "PlusOrchestratorAssessment",

    # Authority rules
    "ORCHESTRATOR_AUTHORITY_RULES",

    # Reference builders
    "build_orchestrator_decision_reference",
    "build_orchestrator_risk_reference",
    "build_orchestrator_cas_reference",
    "build_orchestrator_preparation_reference",
    "build_orchestrator_monitor_reference",
    "build_orchestrator_protection_reference",
    "build_orchestrator_reconciliation_reference",

    # Evaluation
    "validate_plus_orchestrator_request",
    "evaluate_orchestrator_requirements",
    "evaluate_orchestrator_data_state",
    "evaluate_orchestrator_consistency",
    "evaluate_orchestrator_state",
    "evaluate_orchestrator_readiness",
    "evaluate_orchestrator_disposition",

    # Builders
    "build_orchestrator_intelligence",
    "build_plus_orchestrator_assessment",
    "build_plus_orchestrator_result",
    "build_plus_orchestrator_contract",

    # Safety / validation
    "is_plus_orchestrator_safe_to_forward",
    "validate_plus_orchestrator_result",
    "validate_plus_orchestrator_contract",

    # Engine
    "PlusOrchestratorEngine",
    "plus_orchestrator_engine",

    # Public API
    "orchestrate_plus",
    "evaluate_plus_orchestration",
    "plus_orchestration_ready",
    "plus_orchestration_safe",
    "plus_orchestration_requires_review",
    "plus_orchestration_requires_protection",
    "plus_orchestration_requires_block",
    "plus_orchestration_state",
    "plus_orchestration_audit",

    # Health / information
    "plus_orchestrator_health_check",
    "run_plus_orchestrator_health_check",
    "get_plus_orchestrator_engine_info",

    # Serialization / integrity
    "plus_orchestrator_to_dict",
    "plus_orchestrator_integrity_check",
    "verify_plus_orchestrator_integrity",

    # Alias
    "PlusOrchestrator",
]

# END OF PART 5/5
# ============================================================
# PLUS_ORCHESTRATOR.PY COMPLETE
# ============================================================