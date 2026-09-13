# ============================================================
# EMERGENCY_CONTROL.PY
# PART 1/5 — FOUNDATION + CONTRACTS
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

EMERGENCY_CONTROL_ENGINE = "ROBOMLM_PLUS_EMERGENCY_CONTROL"
EMERGENCY_CONTROL_VERSION = "1.0"


# ============================================================
# ENUMS
# ============================================================

class EmergencyControlStatus(str, Enum):
    READY = "READY"
    MONITORING = "MONITORING"
    WARNING = "WARNING"
    EMERGENCY = "EMERGENCY"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


class EmergencyControlState(str, Enum):
    NORMAL = "NORMAL"
    CAUTION = "CAUTION"
    PROTECT = "PROTECT"
    EMERGENCY = "EMERGENCY"
    HALT_REQUIRED = "HALT_REQUIRED"
    UNKNOWN = "UNKNOWN"


class EmergencySeverity(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EmergencyDisposition(str, Enum):
    CONTINUE = "CONTINUE"
    REVIEW = "REVIEW"
    PROTECT = "PROTECT"
    HALT = "HALT"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


class EmergencyContractStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


# ============================================================
# REQUEST CONTRACT
# ============================================================

@dataclass(frozen=True)
class EmergencyControlRequest:
    """
    Emergency Control receives already-established authority/context.

    This engine:
    - does not create a trading decision
    - does not calculate risk
    - does not create authorization
    - does not place orders
    - does not modify positions
    - does not override D13/Risk/CAS
    """

    orchestration_state: Any
    position_monitor: Optional[Any] = None
    protection_state: Optional[Any] = None
    reconciliation_state: Optional[Any] = None
    risk_state: Optional[Any] = None
    decision_state: Optional[Any] = None
    account_state: Optional[Any] = None
    execution_state: Optional[Any] = None
    market_context: Optional[Any] = None

    metadata: Mapping[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []

        if self.orchestration_state is None:
            errors.append("missing_orchestration_state")

        if not self.request_id:
            errors.append("missing_request_id")

        if not isinstance(self.metadata, Mapping):
            errors.append("metadata_must_be_mapping")

        return tuple(errors)


# ============================================================
# AUTHORITY REFERENCES
# ============================================================

@dataclass(frozen=True)
class EmergencyDecisionReference:
    decision_id: Optional[str]
    direction: Optional[str]
    status: Optional[str]
    confidence: Optional[float]
    strength: Optional[float]
    raw_decision: Any
    source: str = "D13"


@dataclass(frozen=True)
class EmergencyRiskReference:
    risk_id: Optional[str]
    status: Optional[str]
    risk_score: Optional[float]
    exposure: Optional[float]
    severity: Optional[str]
    raw_result: Any
    source: str = "RISK"


@dataclass(frozen=True)
class EmergencyCASReference:
    cas_id: Optional[str]
    status: Optional[str]
    authorized: Optional[bool]
    reason: Optional[str]
    raw_result: Any
    source: str = "CAS"


# ============================================================
# CONTROL CONTEXT REFERENCES
# ============================================================

@dataclass(frozen=True)
class EmergencyMonitorReference:
    monitor_id: Optional[str]
    status: Optional[str]
    health: Optional[str]
    consistency: Optional[str]
    disposition: Optional[str]
    action_state: Optional[str]
    requires_protection: bool
    requires_halt: bool
    raw_result: Any
    source: str = "POSITION_MONITOR"


@dataclass(frozen=True)
class EmergencyProtectionReference:
    protection_id: Optional[str]
    status: Optional[str]
    protection_state: Optional[str]
    health: Optional[str]
    disposition: Optional[str]
    requires_protection: bool
    requires_block: bool
    stop_loss: Optional[float]
    take_profit: Optional[float]
    raw_result: Any
    source: str = "PROTECTION"


@dataclass(frozen=True)
class EmergencyReconciliationReference:
    reconciliation_id: Optional[str]
    status: Optional[str]
    reconciliation_state: Optional[str]
    health: Optional[str]
    disposition: Optional[str]
    mismatch_type: Optional[str]
    requires_review: bool
    requires_protection: bool
    requires_block: bool
    raw_result: Any
    source: str = "RECONCILIATION"


# ============================================================
# CONTRACT VALIDATION
# ============================================================

@dataclass(frozen=True)
class EmergencyContractValidation:
    status: EmergencyContractStatus
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:
        return self.status == EmergencyContractStatus.VALID


# ============================================================
# SAFE READ HELPERS
# ============================================================

def _ec_read_value(
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


def _ec_text(
    source: Any,
    *names: str,
    default: Optional[str] = None,
) -> Optional[str]:
    value = _ec_read_value(source, *names, default=default)

    if value is None:
        return default

    if isinstance(value, Enum):
        return value.value

    text = str(value).strip()
    return text if text else default


def _ec_float(
    source: Any,
    *names: str,
    default: Optional[float] = None,
) -> Optional[float]:
    value = _ec_read_value(source, *names, default=default)

    if value is None:
        return default

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _ec_bool(
    source: Any,
    *names: str,
    default: Optional[bool] = None,
) -> Optional[bool]:
    value = _ec_read_value(source, *names, default=default)

    if value is None:
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        text = value.strip().upper()

        if text in {"TRUE", "YES", "1", "AUTHORIZED"}:
            return True

        if text in {"FALSE", "NO", "0", "DENIED", "UNAUTHORIZED"}:
            return False

    return default


# ============================================================
# REFERENCE BUILDERS
# ============================================================

def build_emergency_decision_reference(
    decision: Any,
) -> EmergencyDecisionReference:
    return EmergencyDecisionReference(
        decision_id=_ec_text(decision, "decision_id", "id"),
        direction=_ec_text(decision, "direction", "decision"),
        status=_ec_text(decision, "status"),
        confidence=_ec_float(decision, "confidence"),
        strength=_ec_float(decision, "strength"),
        raw_decision=decision,
    )


def build_emergency_risk_reference(
    risk: Any,
) -> EmergencyRiskReference:
    return EmergencyRiskReference(
        risk_id=_ec_text(risk, "risk_id", "id"),
        status=_ec_text(risk, "status"),
        risk_score=_ec_float(risk, "risk_score", "score"),
        exposure=_ec_float(risk, "exposure"),
        severity=_ec_text(risk, "severity"),
        raw_result=risk,
    )


def build_emergency_cas_reference(
    cas: Any,
) -> EmergencyCASReference:
    return EmergencyCASReference(
        cas_id=_ec_text(cas, "cas_id", "id"),
        status=_ec_text(cas, "status"),
        authorized=_ec_bool(cas, "authorized"),
        reason=_ec_text(cas, "reason", "message"),
        raw_result=cas,
    )


def build_emergency_monitor_reference(
    monitor: Any,
) -> EmergencyMonitorReference:
    return EmergencyMonitorReference(
        monitor_id=_ec_text(monitor, "monitor_id", "id"),
        status=_ec_text(monitor, "status"),
        health=_ec_text(monitor, "health"),
        consistency=_ec_text(monitor, "consistency"),
        disposition=_ec_text(monitor, "disposition"),
        action_state=_ec_text(monitor, "action_state"),
        requires_protection=bool(
            _ec_bool(monitor, "requires_protection", default=False)
        ),
        requires_halt=bool(
            _ec_bool(monitor, "requires_halt", default=False)
        ),
        raw_result=monitor,
    )


def build_emergency_protection_reference(
    protection: Any,
) -> EmergencyProtectionReference:
    return EmergencyProtectionReference(
        protection_id=_ec_text(protection, "protection_id", "id"),
        status=_ec_text(protection, "status"),
        protection_state=_ec_text(
            protection,
            "protection_state",
            "state",
        ),
        health=_ec_text(protection, "health"),
        disposition=_ec_text(protection, "disposition"),
        requires_protection=bool(
            _ec_bool(protection, "requires_protection", default=False)
        ),
        requires_block=bool(
            _ec_bool(protection, "requires_block", default=False)
        ),
        stop_loss=_ec_float(protection, "stop_loss", "sl"),
        take_profit=_ec_float(
            protection,
            "take_profit",
            "tp",
        ),
        raw_result=protection,
    )


def build_emergency_reconciliation_reference(
    reconciliation: Any,
) -> EmergencyReconciliationReference:
    return EmergencyReconciliationReference(
        reconciliation_id=_ec_text(
            reconciliation,
            "reconciliation_id",
            "id",
        ),
        status=_ec_text(reconciliation, "status"),
        reconciliation_state=_ec_text(
            reconciliation,
            "reconciliation_state",
            "state",
        ),
        health=_ec_text(reconciliation, "health"),
        disposition=_ec_text(reconciliation, "disposition"),
        mismatch_type=_ec_text(
            reconciliation,
            "mismatch_type",
        ),
        requires_review=bool(
            _ec_bool(
                reconciliation,
                "requires_review",
                default=False,
            )
        ),
        requires_protection=bool(
            _ec_bool(
                reconciliation,
                "requires_protection",
                default=False,
            )
        ),
        requires_block=bool(
            _ec_bool(
                reconciliation,
                "requires_block",
                default=False,
            )
        ),
        raw_result=reconciliation,
    )


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_emergency_control_request(
    request: EmergencyControlRequest,
) -> EmergencyContractValidation:
    if request is None:
        return EmergencyContractValidation(
            status=EmergencyContractStatus.INVALID,
            errors=("request_is_none",),
        )

    errors = request.validate()

    if errors:
        return EmergencyContractValidation(
            status=EmergencyContractStatus.INVALID,
            errors=errors,
        )

    return EmergencyContractValidation(
        status=EmergencyContractStatus.VALID,
        errors=(),
    )


# ============================================================
# END OF PART 1/5
# ============================================================
# ============================================================
# PART 2/5 — EMERGENCY INTELLIGENCE + EVALUATION
# ============================================================

class EmergencyConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONFLICTING = "CONFLICTING"
    INSUFFICIENT = "INSUFFICIENT"


class EmergencyDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"


@dataclass(frozen=True)
class EmergencyRequirements:
    orchestration_available: bool
    decision_available: bool
    risk_available: bool
    cas_available: bool
    monitor_available: bool
    protection_available: bool
    reconciliation_available: bool
    account_available: bool
    execution_available: bool
    market_context_available: bool
    authority_consistent: bool = False


@dataclass(frozen=True)
class EmergencyIntelligence:
    consistency: EmergencyConsistency
    data_state: EmergencyDataState
    state: EmergencyControlState
    severity: EmergencySeverity
    disposition: EmergencyDisposition

    decision: Optional[EmergencyDecisionReference]
    risk: Optional[EmergencyRiskReference]
    cas: Optional[EmergencyCASReference]
    monitor: Optional[EmergencyMonitorReference]
    protection: Optional[EmergencyProtectionReference]
    reconciliation: Optional[EmergencyReconciliationReference]

    emergency_triggered: bool
    halt_required: bool
    protection_required: bool

    rationale: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    source: str = EMERGENCY_CONTROL_ENGINE


@dataclass(frozen=True)
class EmergencyAssessment:
    intelligence: EmergencyIntelligence
    requirements: EmergencyRequirements

    decision: Optional[EmergencyDecisionReference]
    risk: Optional[EmergencyRiskReference]
    cas: Optional[EmergencyCASReference]
    monitor: Optional[EmergencyMonitorReference]
    protection: Optional[EmergencyProtectionReference]
    reconciliation: Optional[EmergencyReconciliationReference]

    rationale: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


# ============================================================
# NORMALIZATION HELPERS
# ============================================================

def _ec_normalized_text(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, Enum):
        value = value.value

    return str(value).strip().upper()


def _ec_status_is_blocking(value: Any) -> bool:
    status = _ec_normalized_text(value)

    return status in {
        "BLOCKED",
        "DENIED",
        "REJECTED",
        "FAILED",
        "INVALID",
        "UNSAFE",
        "CRITICAL",
        "HALTED",
        "STOPPED",
        "EMERGENCY",
    }


def _ec_status_is_unknown(value: Any) -> bool:
    status = _ec_normalized_text(value)

    return status in {
        "",
        "UNKNOWN",
        "UNSPECIFIED",
        "N/A",
        "NA",
        "NONE",
        "NULL",
    }


def _ec_severity(value: Any) -> EmergencySeverity:
    severity = _ec_normalized_text(value)

    mapping = {
        "NONE": EmergencySeverity.NONE,
        "LOW": EmergencySeverity.LOW,
        "MEDIUM": EmergencySeverity.MEDIUM,
        "HIGH": EmergencySeverity.HIGH,
        "CRITICAL": EmergencySeverity.CRITICAL,
    }

    return mapping.get(
        severity,
        EmergencySeverity.NONE,
    )


def _ec_disposition_for(
    state: EmergencyControlState,
) -> EmergencyDisposition:
    mapping = {
        EmergencyControlState.NORMAL:
            EmergencyDisposition.CONTINUE,
        EmergencyControlState.CAUTION:
            EmergencyDisposition.REVIEW,
        EmergencyControlState.PROTECT:
            EmergencyDisposition.PROTECT,
        EmergencyControlState.EMERGENCY:
            EmergencyDisposition.HALT,
        EmergencyControlState.HALT_REQUIRED:
            EmergencyDisposition.HALT,
        EmergencyControlState.UNKNOWN:
            EmergencyDisposition.UNKNOWN,
    }

    return mapping[state]


# ============================================================
# REQUIREMENTS EVALUATION
# ============================================================

def evaluate_emergency_requirements(
    request: EmergencyControlRequest,
) -> EmergencyRequirements:
    orchestration_available = (
        request.orchestration_state is not None
    )

    decision_source = request.decision_state
    risk_source = request.risk_state
    cas_source = None

    if decision_source is not None:
        cas_source = _ec_read_value(
            decision_source,
            "cas",
            "cas_result",
        )

        if risk_source is None:
            risk_source = _ec_read_value(
                decision_source,
                "risk",
                "risk_result",
            )

    if cas_source is None:
        cas_source = _ec_read_value(
            request.orchestration_state,
            "cas",
            "cas_result",
        )

    decision_available = decision_source is not None
    risk_available = risk_source is not None
    cas_available = cas_source is not None
    monitor_available = request.position_monitor is not None
    protection_available = request.protection_state is not None
    reconciliation_available = (
        request.reconciliation_state is not None
    )
    account_available = request.account_state is not None
    execution_available = request.execution_state is not None
    market_context_available = request.market_context is not None

    authority_consistent = True

    if decision_source is not None:
        decision_status = _ec_text(
            decision_source,
            "status",
        )

        if _ec_status_is_blocking(decision_status):
            authority_consistent = False

    if risk_source is not None:
        risk_status = _ec_text(
            risk_source,
            "status",
        )

        if _ec_status_is_blocking(risk_status):
            authority_consistent = False

    if cas_source is not None:
        cas_status = _ec_text(
            cas_source,
            "status",
        )
        cas_authorized = _ec_bool(
            cas_source,
            "authorized",
        )

        if _ec_status_is_blocking(cas_status):
            authority_consistent = False

        if cas_authorized is False:
            authority_consistent = False

    return EmergencyRequirements(
        orchestration_available=orchestration_available,
        decision_available=decision_available,
        risk_available=risk_available,
        cas_available=cas_available,
        monitor_available=monitor_available,
        protection_available=protection_available,
        reconciliation_available=reconciliation_available,
        account_available=account_available,
        execution_available=execution_available,
        market_context_available=market_context_available,
        authority_consistent=authority_consistent,
    )


# ============================================================
# DATA STATE
# ============================================================

def evaluate_emergency_data_state(
    requirements: EmergencyRequirements,
) -> EmergencyDataState:
    if not requirements.orchestration_available:
        return EmergencyDataState.MISSING

    if not requirements.decision_available:
        return EmergencyDataState.PARTIAL

    if not requirements.risk_available:
        return EmergencyDataState.PARTIAL

    if not requirements.cas_available:
        return EmergencyDataState.PARTIAL

    if not requirements.authority_consistent:
        return EmergencyDataState.PARTIAL

    return EmergencyDataState.COMPLETE


# ============================================================
# CONSISTENCY EVALUATION
# ============================================================

def evaluate_emergency_consistency(
    *,
    decision: Optional[EmergencyDecisionReference],
    risk: Optional[EmergencyRiskReference],
    cas: Optional[EmergencyCASReference],
    monitor: Optional[EmergencyMonitorReference],
    protection: Optional[EmergencyProtectionReference],
    reconciliation: Optional[EmergencyReconciliationReference],
) -> EmergencyConsistency:

    if decision is None:
        return EmergencyConsistency.INSUFFICIENT

    if risk is not None and _ec_status_is_blocking(
        risk.status
    ):
        return EmergencyConsistency.CONFLICTING

    if cas is not None:
        if cas.authorized is False:
            return EmergencyConsistency.CONFLICTING

        if _ec_status_is_blocking(cas.status):
            return EmergencyConsistency.CONFLICTING

    if monitor is not None:
        if monitor.requires_halt:
            return EmergencyConsistency.CONFLICTING

        if _ec_status_is_blocking(monitor.status):
            return EmergencyConsistency.CONFLICTING

    if protection is not None:
        if protection.requires_block:
            return EmergencyConsistency.CONFLICTING

        if _ec_status_is_blocking(protection.status):
            return EmergencyConsistency.CONFLICTING

    if reconciliation is not None:
        if reconciliation.requires_block:
            return EmergencyConsistency.CONFLICTING

        if _ec_status_is_blocking(
            reconciliation.status
        ):
            return EmergencyConsistency.CONFLICTING

    return EmergencyConsistency.CONSISTENT


# ============================================================
# EMERGENCY TRIGGER EVALUATION
# ============================================================

def evaluate_emergency_trigger(
    *,
    monitor: Optional[EmergencyMonitorReference],
    protection: Optional[EmergencyProtectionReference],
    reconciliation: Optional[EmergencyReconciliationReference],
    risk: Optional[EmergencyRiskReference],
) -> tuple[bool, bool, bool]:
    """
    Returns:
        emergency_triggered,
        halt_required,
        protection_required
    """

    emergency_triggered = False
    halt_required = False
    protection_required = False

    if monitor is not None:
        if monitor.requires_halt:
            emergency_triggered = True
            halt_required = True

        if monitor.requires_protection:
            protection_required = True

        if _ec_status_is_blocking(monitor.status):
            emergency_triggered = True

    if protection is not None:
        if protection.requires_block:
            emergency_triggered = True
            halt_required = True

        if protection.requires_protection:
            protection_required = True

        if _ec_status_is_blocking(protection.status):
            emergency_triggered = True

    if reconciliation is not None:
        if reconciliation.requires_block:
            emergency_triggered = True
            halt_required = True

        if reconciliation.requires_protection:
            protection_required = True

        if _ec_status_is_blocking(
            reconciliation.status
        ):
            emergency_triggered = True

    if risk is not None:
        severity = _ec_severity(risk.severity)

        if severity == EmergencySeverity.CRITICAL:
            emergency_triggered = True
            halt_required = True

        elif severity == EmergencySeverity.HIGH:
            protection_required = True

        if _ec_status_is_blocking(risk.status):
            emergency_triggered = True
            halt_required = True

    return (
        emergency_triggered,
        halt_required,
        protection_required,
    )


# ============================================================
# STATE + SEVERITY
# ============================================================

def evaluate_emergency_state(
    *,
    data_state: EmergencyDataState,
    consistency: EmergencyConsistency,
    emergency_triggered: bool,
    halt_required: bool,
    protection_required: bool,
) -> EmergencyControlState:

    if data_state == EmergencyDataState.MISSING:
        return EmergencyControlState.UNKNOWN

    if consistency == EmergencyConsistency.CONFLICTING:
        return EmergencyControlState.EMERGENCY

    if halt_required:
        return EmergencyControlState.HALT_REQUIRED

    if emergency_triggered:
        return EmergencyControlState.EMERGENCY

    if protection_required:
        return EmergencyControlState.PROTECT

    if data_state == EmergencyDataState.PARTIAL:
        return EmergencyControlState.CAUTION

    return EmergencyControlState.NORMAL


def evaluate_emergency_severity(
    *,
    state: EmergencyControlState,
    risk: Optional[EmergencyRiskReference],
    reconciliation: Optional[EmergencyReconciliationReference],
) -> EmergencySeverity:

    if state in {
        EmergencyControlState.EMERGENCY,
        EmergencyControlState.HALT_REQUIRED,
    }:
        return EmergencySeverity.CRITICAL

    if risk is not None:
        risk_severity = _ec_severity(risk.severity)

        if risk_severity in {
            EmergencySeverity.CRITICAL,
            EmergencySeverity.HIGH,
        }:
            return risk_severity

    if reconciliation is not None:
        if reconciliation.requires_block:
            return EmergencySeverity.CRITICAL

        if reconciliation.requires_protection:
            return EmergencySeverity.HIGH

    if state == EmergencyControlState.PROTECT:
        return EmergencySeverity.HIGH

    if state == EmergencyControlState.CAUTION:
        return EmergencySeverity.MEDIUM

    return EmergencySeverity.NONE


# ============================================================
# DISPOSITION
# ============================================================

def evaluate_emergency_disposition(
    *,
    state: EmergencyControlState,
) -> EmergencyDisposition:
    return _ec_disposition_for(state)


# ============================================================
# END OF PART 2/5
# ============================================================
# ============================================================
# PART 3/5 — RESULT + CONTROL CONTRACT + SAFETY GATE
# ============================================================

class EmergencyActionState(str, Enum):
    NONE = "NONE"
    REVIEW = "REVIEW"
    PROTECT = "PROTECT"
    HALT = "HALT"
    BLOCK = "BLOCK"


class EmergencyControlContractState(str, Enum):
    VALID = "VALID"
    INCOMPLETE = "INCOMPLETE"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


# ============================================================
# RESULT CONTRACT
# ============================================================

@dataclass(frozen=True)
class EmergencyControlResult:
    request_id: str
    result_id: str

    status: EmergencyControlStatus
    state: EmergencyControlState
    severity: EmergencySeverity
    consistency: EmergencyConsistency
    data_state: EmergencyDataState
    disposition: EmergencyDisposition
    action_state: EmergencyActionState

    emergency_triggered: bool
    halt_required: bool
    protection_required: bool

    decision: Optional[EmergencyDecisionReference]
    risk: Optional[EmergencyRiskReference]
    cas: Optional[EmergencyCASReference]
    monitor: Optional[EmergencyMonitorReference]
    protection: Optional[EmergencyProtectionReference]
    reconciliation: Optional[EmergencyReconciliationReference]

    rationale: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def is_valid(self) -> bool:
        return bool(
            self.request_id
            and self.result_id
            and self.status != EmergencyControlStatus.INVALID
        )

    @property
    def requires_review(self) -> bool:
        return self.disposition == EmergencyDisposition.REVIEW

    @property
    def requires_protection(self) -> bool:
        return bool(
            self.protection_required
            or self.disposition == EmergencyDisposition.PROTECT
        )

    @property
    def requires_halt(self) -> bool:
        return bool(
            self.halt_required
            or self.disposition == EmergencyDisposition.HALT
        )

    @property
    def requires_block(self) -> bool:
        return self.disposition == EmergencyDisposition.BLOCK

    @property
    def is_action_request(self) -> bool:
        # Emergency Control evaluates control state only.
        return False


# ============================================================
# FINAL CONTRACT
# ============================================================

@dataclass(frozen=True)
class EmergencyControlContract:
    emergency_control_id: str
    request_id: str

    state: EmergencyControlContractState
    result: EmergencyControlResult
    action_state: EmergencyActionState

    rationale: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def is_valid(self) -> bool:
        return bool(
            self.emergency_control_id
            and self.request_id
            and self.result is not None
            and self.result.is_valid
            and self.state == EmergencyControlContractState.VALID
        )

    @property
    def is_action_request(self) -> bool:
        # Hard boundary: no halt order/action is created here.
        return False


# ============================================================
# ACTION STATE
# ============================================================

def _ec_action_state(
    disposition: EmergencyDisposition,
) -> EmergencyActionState:

    mapping = {
        EmergencyDisposition.CONTINUE:
            EmergencyActionState.NONE,
        EmergencyDisposition.REVIEW:
            EmergencyActionState.REVIEW,
        EmergencyDisposition.PROTECT:
            EmergencyActionState.PROTECT,
        EmergencyDisposition.HALT:
            EmergencyActionState.HALT,
        EmergencyDisposition.BLOCK:
            EmergencyActionState.BLOCK,
        EmergencyDisposition.UNKNOWN:
            EmergencyActionState.NONE,
    }

    return mapping.get(
        disposition,
        EmergencyActionState.NONE,
    )


# ============================================================
# RESULT STATUS
# ============================================================

def _ec_result_status(
    *,
    data_state: EmergencyDataState,
    consistency: EmergencyConsistency,
    state: EmergencyControlState,
) -> EmergencyControlStatus:

    if data_state == EmergencyDataState.MISSING:
        return EmergencyControlStatus.INVALID

    if consistency == EmergencyConsistency.CONFLICTING:
        return EmergencyControlStatus.EMERGENCY

    if state in {
        EmergencyControlState.EMERGENCY,
        EmergencyControlState.HALT_REQUIRED,
    }:
        return EmergencyControlStatus.EMERGENCY

    if state == EmergencyControlState.PROTECT:
        return EmergencyControlStatus.WARNING

    if state == EmergencyControlState.CAUTION:
        return EmergencyControlStatus.WARNING

    if data_state == EmergencyDataState.PARTIAL:
        return EmergencyControlStatus.WARNING

    return EmergencyControlStatus.READY


# ============================================================
# BUILD INTELLIGENCE
# ============================================================

def build_emergency_intelligence(
    request: EmergencyControlRequest,
) -> EmergencyIntelligence:

    requirements = evaluate_emergency_requirements(request)

    decision_source = request.decision_state
    risk_source = request.risk_state

    if risk_source is None:
        risk_source = _ec_read_value(
            decision_source,
            "risk",
            "risk_result",
        )

    cas_source = _ec_read_value(
        decision_source,
        "cas",
        "cas_result",
    )

    if cas_source is None:
        cas_source = _ec_read_value(
            request.orchestration_state,
            "cas",
            "cas_result",
        )

    decision = (
        build_emergency_decision_reference(decision_source)
        if decision_source is not None
        else None
    )

    risk = (
        build_emergency_risk_reference(risk_source)
        if risk_source is not None
        else None
    )

    cas = (
        build_emergency_cas_reference(cas_source)
        if cas_source is not None
        else None
    )

    monitor = (
        build_emergency_monitor_reference(
            request.position_monitor
        )
        if request.position_monitor is not None
        else None
    )

    protection = (
        build_emergency_protection_reference(
            request.protection_state
        )
        if request.protection_state is not None
        else None
    )

    reconciliation = (
        build_emergency_reconciliation_reference(
            request.reconciliation_state
        )
        if request.reconciliation_state is not None
        else None
    )

    data_state = evaluate_emergency_data_state(
        requirements
    )

    consistency = evaluate_emergency_consistency(
        decision=decision,
        risk=risk,
        cas=cas,
        monitor=monitor,
        protection=protection,
        reconciliation=reconciliation,
    )

    (
        emergency_triggered,
        halt_required,
        protection_required,
    ) = evaluate_emergency_trigger(
        monitor=monitor,
        protection=protection,
        reconciliation=reconciliation,
        risk=risk,
    )

    state = evaluate_emergency_state(
        data_state=data_state,
        consistency=consistency,
        emergency_triggered=emergency_triggered,
        halt_required=halt_required,
        protection_required=protection_required,
    )

    severity = evaluate_emergency_severity(
        state=state,
        risk=risk,
        reconciliation=reconciliation,
    )

    disposition = evaluate_emergency_disposition(
        state=state
    )

    rationale: list[str] = [
        "Emergency Control evaluates established control and safety state.",
        "D13 remains the decision authority.",
        "Risk remains the risk authority.",
        "CAS remains the authorization authority.",
        "Emergency Control does not create trading authorization.",
        "Emergency Control does not create an order or position action.",
    ]

    warnings: list[str] = []

    if data_state == EmergencyDataState.PARTIAL:
        warnings.append(
            "Emergency assessment has partial upstream/context data."
        )

    if consistency == EmergencyConsistency.CONFLICTING:
        warnings.append(
            "Conflicting safety/control state detected."
        )

    if halt_required:
        warnings.append(
            "HALT_REQUIRED is a control state; no halt order is created."
        )

    if protection_required:
        warnings.append(
            "Protection is required; no protection parameters are calculated."
        )

    return EmergencyIntelligence(
        consistency=consistency,
        data_state=data_state,
        state=state,
        severity=severity,
        disposition=disposition,
        decision=decision,
        risk=risk,
        cas=cas,
        monitor=monitor,
        protection=protection,
        reconciliation=reconciliation,
        emergency_triggered=emergency_triggered,
        halt_required=halt_required,
        protection_required=protection_required,
        rationale=tuple(rationale),
        warnings=tuple(warnings),
    )


# ============================================================
# ASSESSMENT
# ============================================================

def build_emergency_assessment(
    request: EmergencyControlRequest,
) -> EmergencyAssessment:

    intelligence = build_emergency_intelligence(request)

    requirements = evaluate_emergency_requirements(
        request
    )

    return EmergencyAssessment(
        intelligence=intelligence,
        requirements=requirements,
        decision=intelligence.decision,
        risk=intelligence.risk,
        cas=intelligence.cas,
        monitor=intelligence.monitor,
        protection=intelligence.protection,
        reconciliation=intelligence.reconciliation,
        rationale=intelligence.rationale,
        warnings=intelligence.warnings,
    )


# ============================================================
# BUILD RESULT
# ============================================================

def build_emergency_control_result(
    request: EmergencyControlRequest,
    assessment: EmergencyAssessment,
) -> EmergencyControlResult:

    intelligence = assessment.intelligence

    status = _ec_result_status(
        data_state=intelligence.data_state,
        consistency=intelligence.consistency,
        state=intelligence.state,
    )

    action_state = _ec_action_state(
        intelligence.disposition
    )

    return EmergencyControlResult(
        request_id=request.request_id,
        result_id=str(uuid4()),
        status=status,
        state=intelligence.state,
        severity=intelligence.severity,
        consistency=intelligence.consistency,
        data_state=intelligence.data_state,
        disposition=intelligence.disposition,
        action_state=action_state,
        emergency_triggered=intelligence.emergency_triggered,
        halt_required=intelligence.halt_required,
        protection_required=intelligence.protection_required,
        decision=intelligence.decision,
        risk=intelligence.risk,
        cas=intelligence.cas,
        monitor=intelligence.monitor,
        protection=intelligence.protection,
        reconciliation=intelligence.reconciliation,
        rationale=intelligence.rationale,
        warnings=intelligence.warnings,
    )


# ============================================================
# CONTRACT STATE
# ============================================================

def _ec_contract_state(
    result: EmergencyControlResult,
) -> EmergencyControlContractState:

    if not result.is_valid:
        return EmergencyControlContractState.INVALID

    if result.data_state == EmergencyDataState.MISSING:
        return EmergencyControlContractState.INVALID

    if result.requires_block:
        return EmergencyControlContractState.BLOCKED

    if result.consistency == EmergencyConsistency.CONFLICTING:
        return EmergencyControlContractState.BLOCKED

    if result.data_state == EmergencyDataState.PARTIAL:
        return EmergencyControlContractState.INCOMPLETE

    return EmergencyControlContractState.VALID


# ============================================================
# BUILD FINAL CONTRACT
# ============================================================

def build_emergency_control_contract(
    request: EmergencyControlRequest,
    result: EmergencyControlResult,
) -> EmergencyControlContract:

    state = _ec_contract_state(result)

    return EmergencyControlContract(
        emergency_control_id=str(uuid4()),
        request_id=request.request_id,
        state=state,
        result=result,
        action_state=result.action_state,
        rationale=result.rationale,
        warnings=result.warnings,
    )


# ============================================================
# DOWNSTREAM SAFETY GATE
# ============================================================

def is_emergency_control_safe_to_forward(
    contract: EmergencyControlContract,
) -> bool:
    """
    Forwarding means passing control-state information to the
    appropriate downstream controller.

    It NEVER means executing a trade or creating an order.
    """

    if contract is None:
        return False

    if not contract.is_valid:
        return False

    if contract.is_action_request:
        return False

    result = contract.result

    if result is None or not result.is_valid:
        return False

    if result.consistency == EmergencyConsistency.CONFLICTING:
        return False

    if result.requires_block:
        return False

    if contract.state != EmergencyControlContractState.VALID:
        return False

    return True


# ============================================================
# RESULT VALIDATION
# ============================================================

def validate_emergency_control_result(
    result: EmergencyControlResult,
) -> EmergencyContractValidation:

    errors: list[str] = []
    warnings: list[str] = []

    if result is None:
        return EmergencyContractValidation(
            status=EmergencyContractStatus.INVALID,
            errors=("result_is_none",),
        )

    if not result.request_id:
        errors.append("missing_request_id")

    if not result.result_id:
        errors.append("missing_result_id")

    if result.status == EmergencyControlStatus.INVALID:
        errors.append("result_status_invalid")

    if result.consistency == EmergencyConsistency.CONFLICTING:
        warnings.append("result_has_conflicting_control_state")

    if result.requires_halt:
        warnings.append(
            "halt_required_but_no_halt_action_created"
        )

    if result.requires_protection:
        warnings.append(
            "protection_required_but_no_protection_action_created"
        )

    if result.is_action_request:
        errors.append("action_request_created")

    if errors:
        return EmergencyContractValidation(
            status=EmergencyContractStatus.INVALID,
            errors=tuple(dict.fromkeys(errors)),
            warnings=tuple(dict.fromkeys(warnings)),
        )

    return EmergencyContractValidation(
        status=EmergencyContractStatus.VALID,
        errors=(),
        warnings=tuple(dict.fromkeys(warnings)),
    )


# ============================================================
# END OF PART 3/5
# ============================================================
# ============================================================
# PART 4/5 — EMERGENCY CONTROL ENGINE + PROCESSING
# ============================================================

class EmergencyControlEngine:
    """
    ROBOMLM PLUS Emergency Control Engine.

    Role:
        Evaluate emergency/control conditions from already-established
        Decision, Risk, CAS, Position Monitor, Protection and
        Reconciliation states.

    Hard boundaries:
        - D13 remains decision authority.
        - Risk remains risk authority.
        - CAS remains authorization authority.
        - No decision synthesis.
        - No risk recalculation.
        - No authorization creation.
        - No order creation.
        - No position modification.
        - No broker execution.
    """

    ENGINE_NAME = EMERGENCY_CONTROL_ENGINE
    ENGINE_VERSION = EMERGENCY_CONTROL_VERSION

    def validate_request(
        self,
        request: EmergencyControlRequest,
    ) -> EmergencyContractValidation:
        return validate_emergency_control_request(request)

    def _invalid_contract(
        self,
        request: Optional[EmergencyControlRequest],
        errors: tuple[str, ...],
    ) -> EmergencyControlContract:

        request_id = (
            request.request_id
            if request is not None and request.request_id
            else str(uuid4())
        )

        result = EmergencyControlResult(
            request_id=request_id,
            result_id=str(uuid4()),
            status=EmergencyControlStatus.INVALID,
            state=EmergencyControlState.UNKNOWN,
            severity=EmergencySeverity.CRITICAL,
            consistency=EmergencyConsistency.INSUFFICIENT,
            data_state=EmergencyDataState.MISSING,
            disposition=EmergencyDisposition.BLOCK,
            action_state=EmergencyActionState.BLOCK,
            emergency_triggered=True,
            halt_required=True,
            protection_required=True,
            decision=None,
            risk=None,
            cas=None,
            monitor=None,
            protection=None,
            reconciliation=None,
            rationale=(
                "Emergency Control failed closed.",
                "Invalid input cannot be treated as safe.",
                "No emergency action or order was created.",
            ),
            warnings=errors,
        )

        return EmergencyControlContract(
            emergency_control_id=str(uuid4()),
            request_id=request_id,
            state=EmergencyControlContractState.INVALID,
            result=result,
            action_state=EmergencyActionState.BLOCK,
            rationale=result.rationale,
            warnings=errors,
        )

    def process(
        self,
        request: EmergencyControlRequest,
    ) -> EmergencyControlContract:

        validation = self.validate_request(request)

        if not validation.is_valid:
            return self._invalid_contract(
                request,
                validation.errors,
            )

        try:
            assessment = build_emergency_assessment(request)

            result = build_emergency_control_result(
                request,
                assessment,
            )

            result_validation = validate_emergency_control_result(
                result
            )

            if not result_validation.is_valid:
                return self._invalid_contract(
                    request,
                    result_validation.errors,
                )

            contract = build_emergency_control_contract(
                request,
                result,
            )

            # Emergency/control conflicts must remain blocked.
            if (
                result.requires_halt
                or result.consistency
                == EmergencyConsistency.CONFLICTING
            ):
                contract = EmergencyControlContract(
                    emergency_control_id=contract.emergency_control_id,
                    request_id=contract.request_id,
                    state=EmergencyControlContractState.BLOCKED,
                    result=contract.result,
                    action_state=EmergencyActionState.HALT,
                    rationale=contract.rationale,
                    warnings=contract.warnings,
                    created_at=contract.created_at,
                )

            return contract

        except Exception as exc:
            return self._invalid_contract(
                request,
                (
                    "emergency_control_processing_failed",
                    f"{type(exc).__name__}: {exc}",
                ),
            )

    def evaluate(
        self,
        request: EmergencyControlRequest,
    ) -> EmergencyControlContract:
        return self.process(request)

    def is_ready(
        self,
        contract: EmergencyControlContract,
    ) -> bool:
        return is_emergency_control_safe_to_forward(contract)

    def requires_halt(
        self,
        contract: EmergencyControlContract,
    ) -> bool:
        if contract is None or contract.result is None:
            return True

        return contract.result.requires_halt

    def requires_protection(
        self,
        contract: EmergencyControlContract,
    ) -> bool:
        if contract is None or contract.result is None:
            return True

        return contract.result.requires_protection

    def requires_review(
        self,
        contract: EmergencyControlContract,
    ) -> bool:
        if contract is None or contract.result is None:
            return True

        return contract.result.requires_review

    def emergency_state(
        self,
        contract: EmergencyControlContract,
    ) -> EmergencyControlState:

        if contract is None or contract.result is None:
            return EmergencyControlState.UNKNOWN

        return contract.result.state

    def emergency_severity(
        self,
        contract: EmergencyControlContract,
    ) -> EmergencySeverity:

        if contract is None or contract.result is None:
            return EmergencySeverity.CRITICAL

        return contract.result.severity

    def audit_summary(
        self,
        contract: EmergencyControlContract,
    ) -> dict[str, Any]:

        if contract is None:
            return {
                "engine": self.ENGINE_NAME,
                "version": self.ENGINE_VERSION,
                "valid": False,
                "safe_to_forward": False,
                "requires_halt": True,
                "requires_protection": True,
                "requires_review": True,
            }

        result = contract.result

        return {
            "engine": self.ENGINE_NAME,
            "version": self.ENGINE_VERSION,
            "valid": contract.is_valid,
            "contract_state": (
                contract.state.value
                if isinstance(
                    contract.state,
                    Enum,
                )
                else contract.state
            ),
            "state": (
                result.state.value
                if result is not None
                and isinstance(result.state, Enum)
                else None
            ),
            "severity": (
                result.severity.value
                if result is not None
                and isinstance(result.severity, Enum)
                else None
            ),
            "disposition": (
                result.disposition.value
                if result is not None
                and isinstance(result.disposition, Enum)
                else None
            ),
            "safe_to_forward": (
                is_emergency_control_safe_to_forward(contract)
            ),
            "requires_halt": self.requires_halt(contract),
            "requires_protection": self.requires_protection(
                contract
            ),
            "requires_review": self.requires_review(contract),
            "authority": {
                "d13_is_decision_authority": True,
                "risk_is_risk_authority": True,
                "cas_is_authorization_authority": True,
                "emergency_control_is_control_layer": True,
            },
            "forbidden_actions": {
                "decision_synthesis": False,
                "risk_recalculation": False,
                "authorization_creation": False,
                "execution_creation": False,
                "order_creation": False,
                "position_modification": False,
                "d13_override": False,
                "risk_override": False,
                "cas_override": False,
            },
        }


# ============================================================
# PUBLIC ENGINE INSTANCE
# ============================================================

emergency_control_engine = EmergencyControlEngine()


# ============================================================
# PUBLIC API
# ============================================================

def evaluate_emergency_control(
    request: EmergencyControlRequest,
) -> EmergencyControlContract:
    return emergency_control_engine.evaluate(request)


def process_emergency_control(
    request: EmergencyControlRequest,
) -> EmergencyControlContract:
    return emergency_control_engine.process(request)


def emergency_control_ready(
    contract: EmergencyControlContract,
) -> bool:
    return emergency_control_engine.is_ready(contract)


def emergency_control_requires_halt(
    contract: EmergencyControlContract,
) -> bool:
    return emergency_control_engine.requires_halt(contract)


def emergency_control_requires_protection(
    contract: EmergencyControlContract,
) -> bool:
    return emergency_control_engine.requires_protection(contract)


def emergency_control_requires_review(
    contract: EmergencyControlContract,
) -> bool:
    return emergency_control_engine.requires_review(contract)


def emergency_control_state(
    contract: EmergencyControlContract,
) -> EmergencyControlState:
    return emergency_control_engine.emergency_state(contract)


def emergency_control_severity(
    contract: EmergencyControlContract,
) -> EmergencySeverity:
    return emergency_control_engine.emergency_severity(contract)


def emergency_control_audit(
    contract: EmergencyControlContract,
) -> dict[str, Any]:
    return emergency_control_engine.audit_summary(contract)


# ============================================================
# HEALTH / ENGINE INFORMATION
# ============================================================

def emergency_control_health_check() -> dict[str, Any]:
    return {
        "engine": EMERGENCY_CONTROL_ENGINE,
        "version": EMERGENCY_CONTROL_VERSION,
        "status": "HEALTHY",
        "contract_layer": True,
        "intelligence_layer": True,
        "emergency_detection": True,
        "halt_state_detection": True,
        "protection_state_detection": True,
        "fail_closed": True,
        "d13_override": False,
        "risk_override": False,
        "cas_override": False,
        "authorization_created": False,
        "execution_created": False,
        "order_created": False,
        "position_modified": False,
    }


def get_emergency_control_engine_info() -> dict[str, Any]:
    return {
        "engine": EMERGENCY_CONTROL_ENGINE,
        "version": EMERGENCY_CONTROL_VERSION,
        "role": (
            "Emergency/control-state evaluation and "
            "safe downstream control signaling."
        ),
        "authority": {
            "decision": "D13",
            "risk": "RISK",
            "authorization": "CAS",
            "control": "EMERGENCY_CONTROL",
        },
        "execution": False,
        "order_creation": False,
        "position_modification": False,
    }


# ============================================================
# COMPATIBILITY ALIAS
# ============================================================

EmergencyControl = EmergencyControlEngine


# ============================================================
# END OF PART 4/5
# ============================================================
# ============================================================
# PART 5/5 — SERIALIZATION + INTEGRITY + EXPORTS
# ============================================================

def _ec_enum_value(value: Any) -> Any:
    return value.value if isinstance(value, Enum) else value


def _ec_safe_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}

    if isinstance(value, Mapping):
        return dict(value)

    if hasattr(value, "to_dict"):
        try:
            data = value.to_dict()
            return dict(data) if isinstance(data, Mapping) else {}
        except Exception:
            return {}

    if hasattr(value, "__dict__"):
        try:
            return dict(value.__dict__)
        except Exception:
            return {}

    return {}


# ============================================================
# SERIALIZATION
# ============================================================

def emergency_control_to_dict(
    contract: EmergencyControlContract,
) -> dict[str, Any]:
    """Stable, read-only serialization of Emergency Control."""

    if contract is None:
        return {
            "valid": False,
            "error": "contract_is_none",
        }

    result = contract.result

    return {
        "emergency_control_id": contract.emergency_control_id,
        "request_id": contract.request_id,
        "state": _ec_enum_value(contract.state),
        "action_state": _ec_enum_value(contract.action_state),
        "is_valid": contract.is_valid,
        "is_action_request": contract.is_action_request,

        "result": {
            "result_id": result.result_id,
            "request_id": result.request_id,
            "status": _ec_enum_value(result.status),
            "state": _ec_enum_value(result.state),
            "severity": _ec_enum_value(result.severity),
            "consistency": _ec_enum_value(result.consistency),
            "data_state": _ec_enum_value(result.data_state),
            "disposition": _ec_enum_value(result.disposition),
            "action_state": _ec_enum_value(result.action_state),

            "emergency_triggered": result.emergency_triggered,
            "halt_required": result.halt_required,
            "protection_required": result.protection_required,

            "decision": _ec_safe_dict(result.decision),
            "risk": _ec_safe_dict(result.risk),
            "cas": _ec_safe_dict(result.cas),
            "monitor": _ec_safe_dict(result.monitor),
            "protection": _ec_safe_dict(result.protection),
            "reconciliation": _ec_safe_dict(
                result.reconciliation
            ),

            "rationale": list(result.rationale),
            "warnings": list(result.warnings),
        },

        "rationale": list(contract.rationale),
        "warnings": list(contract.warnings),

        "integrity": {
            "decision_synthesized": False,
            "risk_recalculated": False,
            "authorization_created": False,
            "execution_created": False,
            "order_created": False,
            "position_modified": False,
            "d13_overridden": False,
            "risk_overridden": False,
            "cas_overridden": False,
        },
    }


# ============================================================
# FINAL CONTRACT VALIDATION
# ============================================================

def validate_emergency_control_contract(
    contract: EmergencyControlContract,
) -> EmergencyContractValidation:
    errors: list[str] = []
    warnings: list[str] = []

    if contract is None:
        return EmergencyContractValidation(
            status=EmergencyContractStatus.INVALID,
            errors=("contract_is_none",),
        )

    if not contract.emergency_control_id:
        errors.append("missing_emergency_control_id")

    if not contract.request_id:
        errors.append("missing_request_id")

    if contract.result is None:
        errors.append("missing_result")
    else:
        if contract.result.request_id != contract.request_id:
            errors.append("request_id_mismatch")

        result_validation = validate_emergency_control_result(
            contract.result
        )

        errors.extend(result_validation.errors)
        warnings.extend(result_validation.warnings)

        if contract.result.is_action_request:
            errors.append("action_request_created")

    if contract.is_action_request:
        errors.append("action_request_created")

    if contract.state == EmergencyControlContractState.INVALID:
        errors.append("contract_state_invalid")

    if errors:
        return EmergencyContractValidation(
            status=EmergencyContractStatus.INVALID,
            errors=tuple(dict.fromkeys(errors)),
            warnings=tuple(dict.fromkeys(warnings)),
        )

    return EmergencyContractValidation(
        status=EmergencyContractStatus.VALID,
        errors=(),
        warnings=tuple(dict.fromkeys(warnings)),
    )


# ============================================================
# INTEGRITY CHECK
# ============================================================

def emergency_control_integrity_check(
    contract: EmergencyControlContract,
) -> dict[str, Any]:
    """Final structural and authority-boundary audit."""

    validation = validate_emergency_control_contract(
        contract
    )

    if contract is None:
        return {
            "engine": EMERGENCY_CONTROL_ENGINE,
            "version": EMERGENCY_CONTROL_VERSION,
            "valid": False,
            "safe_to_forward": False,
            "errors": list(validation.errors),
            "warnings": list(validation.warnings),
        }

    result = contract.result

    safe = is_emergency_control_safe_to_forward(
        contract
    )

    return {
        "engine": EMERGENCY_CONTROL_ENGINE,
        "version": EMERGENCY_CONTROL_VERSION,

        "valid": validation.is_valid,
        "contract_state": _ec_enum_value(contract.state),

        "state": (
            _ec_enum_value(result.state)
            if result is not None
            else None
        ),
        "severity": (
            _ec_enum_value(result.severity)
            if result is not None
            else None
        ),
        "disposition": (
            _ec_enum_value(result.disposition)
            if result is not None
            else None
        ),
        "consistency": (
            _ec_enum_value(result.consistency)
            if result is not None
            else None
        ),

        "safe_to_forward": safe,

        "emergency_triggered": bool(
            result.emergency_triggered
            if result is not None
            else True
        ),
        "requires_halt": bool(
            result.requires_halt
            if result is not None
            else True
        ),
        "requires_protection": bool(
            result.requires_protection
            if result is not None
            else True
        ),
        "requires_review": bool(
            result.requires_review
            if result is not None
            else True
        ),

        "authority": {
            "d13_is_decision_authority": True,
            "risk_is_risk_authority": True,
            "cas_is_authorization_authority": True,
            "emergency_control_is_control_layer": True,
        },

        "forbidden_actions": {
            "decision_synthesis": False,
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


def verify_emergency_control_integrity(
    contract: EmergencyControlContract,
) -> bool:
    """Boolean integrity gate."""

    audit = emergency_control_integrity_check(
        contract
    )

    return bool(
        audit["valid"]
        and audit["safe_to_forward"]
    )


# ============================================================
# HEALTH WRAPPER
# ============================================================

def run_emergency_control_health_check() -> dict[str, Any]:
    return {
        **emergency_control_health_check(),
        "serialization_present": True,
        "contract_validation_present": True,
        "integrity_check_present": True,
        "fail_closed": True,
    }


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [
    # Identity
    "EMERGENCY_CONTROL_ENGINE",
    "EMERGENCY_CONTROL_VERSION",

    # Enums
    "EmergencyControlStatus",
    "EmergencyControlState",
    "EmergencySeverity",
    "EmergencyDisposition",
    "EmergencyContractStatus",
    "EmergencyConsistency",
    "EmergencyDataState",
    "EmergencyActionState",
    "EmergencyControlContractState",

    # Contracts
    "EmergencyControlRequest",
    "EmergencyContractValidation",
    "EmergencyRequirements",
    "EmergencyIntelligence",
    "EmergencyAssessment",
    "EmergencyControlResult",
    "EmergencyControlContract",

    # References
    "EmergencyDecisionReference",
    "EmergencyRiskReference",
    "EmergencyCASReference",
    "EmergencyMonitorReference",
    "EmergencyProtectionReference",
    "EmergencyReconciliationReference",

    # Reference builders
    "build_emergency_decision_reference",
    "build_emergency_risk_reference",
    "build_emergency_cas_reference",
    "build_emergency_monitor_reference",
    "build_emergency_protection_reference",
    "build_emergency_reconciliation_reference",

    # Validation
    "validate_emergency_control_request",
    "validate_emergency_control_result",
    "validate_emergency_control_contract",

    # Evaluation
    "evaluate_emergency_requirements",
    "evaluate_emergency_data_state",
    "evaluate_emergency_consistency",
    "evaluate_emergency_trigger",
    "evaluate_emergency_state",
    "evaluate_emergency_severity",
    "evaluate_emergency_disposition",

    # Assessment / builders
    "build_emergency_intelligence",
    "build_emergency_assessment",
    "build_emergency_control_result",
    "build_emergency_control_contract",

    # Safety
    "is_emergency_control_safe_to_forward",

    # Engine
    "EmergencyControlEngine",
    "emergency_control_engine",

    # Public API
    "evaluate_emergency_control",
    "process_emergency_control",
    "emergency_control_ready",
    "emergency_control_requires_halt",
    "emergency_control_requires_protection",
    "emergency_control_requires_review",
    "emergency_control_state",
    "emergency_control_severity",
    "emergency_control_audit",

    # Health / information
    "emergency_control_health_check",
    "run_emergency_control_health_check",
    "get_emergency_control_engine_info",

    # Serialization / integrity
    "emergency_control_to_dict",
    "emergency_control_integrity_check",
    "verify_emergency_control_integrity",

    # Alias
    "EmergencyControl",
]

# ============================================================
# EMERGENCY_CONTROL.PY — COMPLETE 5/5
# ============================================================