# ============================================================
# ROBOMLM_PLUS — halt_controller.py
# PART 1 / 5
# HALT CONTROLLER FOUNDATION + CONTRACTS
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

HALT_CONTROLLER_ENGINE = "ROBOMLM_PLUS_HALT_CONTROLLER"
HALT_CONTROLLER_VERSION = "1.0"


# ============================================================
# STATUS / STATE ENUMS
# ============================================================

class HaltControllerStatus(str, Enum):
    READY = "READY"
    MONITORING = "MONITORING"
    WARNING = "WARNING"
    HALT_REQUIRED = "HALT_REQUIRED"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


class HaltControllerState(str, Enum):
    NORMAL = "NORMAL"
    CAUTION = "CAUTION"
    HALT_REQUIRED = "HALT_REQUIRED"
    HALTED = "HALTED"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"


class HaltSeverity(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class HaltDisposition(str, Enum):
    CONTINUE = "CONTINUE"
    REVIEW = "REVIEW"
    HALT = "HALT"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


class HaltContractStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


# ============================================================
# REQUEST CONTRACT
# ============================================================

@dataclass(frozen=True)
class HaltControllerRequest:
    """
    Controlled input contract for Halt Controller.

    Authority:
        Emergency Control = primary halt-condition source
        Position Monitor = position safety source
        Protection = protection state source
        Reconciliation = state-integrity source
        Risk = risk authority
        D13 = decision authority
        CAS = authorization authority

    Halt Controller:
        - interprets established control states
        - identifies whether halt is required
        - does NOT create an order
        - does NOT create broker execution
        - does NOT create authorization
        - does NOT modify a position
        - does NOT override D13 / Risk / CAS
        """

    emergency_control: Any

    orchestration_state: Optional[Any] = None
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

    def validate(self) -> bool:
        if self.emergency_control is None:
            return False

        if not self.request_id or not str(self.request_id).strip():
            return False

        if not isinstance(self.metadata, Mapping):
            return False

        return True


# ============================================================
# D13 DECISION REFERENCE
# ============================================================

@dataclass(frozen=True)
class HaltDecisionReference:
    decision_id: str
    direction: str
    status: str
    confidence: Optional[float]
    strength: Optional[float]
    raw_decision: Any
    source: str = "D13"


# ============================================================
# RISK REFERENCE
# ============================================================

@dataclass(frozen=True)
class HaltRiskReference:
    risk_id: str
    status: str
    risk_score: Optional[float]
    exposure: Optional[float]
    severity: str
    raw_result: Any
    source: str = "RISK"


# ============================================================
# CAS REFERENCE
# ============================================================

@dataclass(frozen=True)
class HaltCASReference:
    cas_id: str
    status: str
    authorized: Optional[bool]
    reason: str
    raw_result: Any
    source: str = "CAS"


# ============================================================
# EMERGENCY CONTROL REFERENCE
# ============================================================

@dataclass(frozen=True)
class HaltEmergencyReference:
    emergency_id: str
    status: str
    state: str
    severity: str
    disposition: str
    emergency_triggered: bool
    halt_required: bool
    protection_required: bool
    raw_result: Any
    source: str = "EMERGENCY_CONTROL"


# ============================================================
# POSITION MONITOR REFERENCE
# ============================================================

@dataclass(frozen=True)
class HaltMonitorReference:
    monitor_id: str
    status: str
    health: str
    consistency: str
    disposition: str
    requires_halt: bool
    requires_protection: bool
    raw_result: Any
    source: str = "POSITION_MONITOR"


# ============================================================
# PROTECTION REFERENCE
# ============================================================

@dataclass(frozen=True)
class HaltProtectionReference:
    protection_id: str
    status: str
    protection_state: str
    health: str
    disposition: str
    requires_block: bool
    requires_protection: bool
    raw_result: Any
    source: str = "PROTECTION"


# ============================================================
# RECONCILIATION REFERENCE
# ============================================================

@dataclass(frozen=True)
class HaltReconciliationReference:
    reconciliation_id: str
    status: str
    reconciliation_state: str
    health: str
    disposition: str
    mismatch_type: str
    requires_block: bool
    requires_protection: bool
    requires_review: bool
    raw_result: Any
    source: str = "RECONCILIATION"


# ============================================================
# CONTRACT VALIDATION
# ============================================================

@dataclass(frozen=True)
class HaltContractValidation:
    status: HaltContractStatus
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:
        return self.status == HaltContractStatus.VALID


# ============================================================
# GENERIC VALUE READER
# ============================================================

def _hc_read_value(
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
        except AttributeError:
            continue

        if value is not None:
            return value

    return default


def _hc_text(
    source: Any,
    *names: str,
    default: str = "",
) -> str:
    value = _hc_read_value(source, *names, default=default)

    if value is None:
        return default

    if isinstance(value, Enum):
        return str(value.value)

    return str(value)


def _hc_float(
    source: Any,
    *names: str,
    default: Optional[float] = None,
) -> Optional[float]:
    value = _hc_read_value(source, *names, default=None)

    if value is None:
        return default

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _hc_bool(
    source: Any,
    *names: str,
    default: bool = False,
) -> bool:
    value = _hc_read_value(source, *names, default=None)

    if value is None:
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.strip().upper() in {
            "TRUE",
            "YES",
            "1",
            "Y",
        }

    return bool(value)


# ============================================================
# D13 ADAPTER
# ============================================================

def build_halt_decision_reference(
    decision: Any,
) -> Optional[HaltDecisionReference]:

    if decision is None:
        return None

    return HaltDecisionReference(
        decision_id=_hc_text(
            decision,
            "decision_id",
            "id",
            default="",
        ),
        direction=_hc_text(
            decision,
            "direction",
            "decision",
            "disposition",
            default="UNKNOWN",
        ),
        status=_hc_text(
            decision,
            "status",
            default="UNKNOWN",
        ),
        confidence=_hc_float(
            decision,
            "confidence",
            default=None,
        ),
        strength=_hc_float(
            decision,
            "strength",
            default=None,
        ),
        raw_decision=decision,
    )


# ============================================================
# RISK ADAPTER
# ============================================================

def build_halt_risk_reference(
    risk: Any,
) -> Optional[HaltRiskReference]:

    if risk is None:
        return None

    return HaltRiskReference(
        risk_id=_hc_text(
            risk,
            "risk_id",
            "id",
            default="",
        ),
        status=_hc_text(
            risk,
            "status",
            default="UNKNOWN",
        ),
        risk_score=_hc_float(
            risk,
            "risk_score",
            "score",
            default=None,
        ),
        exposure=_hc_float(
            risk,
            "exposure",
            "total_exposure",
            default=None,
        ),
        severity=_hc_text(
            risk,
            "severity",
            default="UNKNOWN",
        ),
        raw_result=risk,
    )


# ============================================================
# CAS ADAPTER
# ============================================================

def build_halt_cas_reference(
    cas: Any,
) -> Optional[HaltCASReference]:

    if cas is None:
        return None

    authorized_value = _hc_read_value(
        cas,
        "authorized",
        "is_authorized",
        default=None,
    )

    authorized: Optional[bool]

    if authorized_value is None:
        authorized = None
    else:
        authorized = _hc_bool(
            {"value": authorized_value},
            "value",
            default=False,
        )

    return HaltCASReference(
        cas_id=_hc_text(
            cas,
            "cas_id",
            "authorization_id",
            "id",
            default="",
        ),
        status=_hc_text(
            cas,
            "status",
            default="UNKNOWN",
        ),
        authorized=authorized,
        reason=_hc_text(
            cas,
            "reason",
            "message",
            default="",
        ),
        raw_result=cas,
    )


# ============================================================
# EMERGENCY CONTROL ADAPTER
# ============================================================

def build_halt_emergency_reference(
    emergency: Any,
) -> Optional[HaltEmergencyReference]:

    if emergency is None:
        return None

    return HaltEmergencyReference(
        emergency_id=_hc_text(
            emergency,
            "emergency_id",
            "result_id",
            "id",
            default="",
        ),
        status=_hc_text(
            emergency,
            "status",
            default="UNKNOWN",
        ),
        state=_hc_text(
            emergency,
            "state",
            default="UNKNOWN",
        ),
        severity=_hc_text(
            emergency,
            "severity",
            default="UNKNOWN",
        ),
        disposition=_hc_text(
            emergency,
            "disposition",
            default="UNKNOWN",
        ),
        emergency_triggered=_hc_bool(
            emergency,
            "emergency_triggered",
            default=False,
        ),
        halt_required=_hc_bool(
            emergency,
            "halt_required",
            "requires_halt",
            default=False,
        ),
        protection_required=_hc_bool(
            emergency,
            "protection_required",
            "requires_protection",
            default=False,
        ),
        raw_result=emergency,
    )


# ============================================================
# POSITION MONITOR ADAPTER
# ============================================================

def build_halt_monitor_reference(
    monitor: Any,
) -> Optional[HaltMonitorReference]:

    if monitor is None:
        return None

    return HaltMonitorReference(
        monitor_id=_hc_text(
            monitor,
            "monitor_id",
            "result_id",
            "id",
            default="",
        ),
        status=_hc_text(
            monitor,
            "status",
            default="UNKNOWN",
        ),
        health=_hc_text(
            monitor,
            "health",
            default="UNKNOWN",
        ),
        consistency=_hc_text(
            monitor,
            "consistency",
            default="UNKNOWN",
        ),
        disposition=_hc_text(
            monitor,
            "disposition",
            default="UNKNOWN",
        ),
        requires_halt=_hc_bool(
            monitor,
            "requires_halt",
            default=False,
        ),
        requires_protection=_hc_bool(
            monitor,
            "requires_protection",
            default=False,
        ),
        raw_result=monitor,
    )


# ============================================================
# PROTECTION ADAPTER
# ============================================================

def build_halt_protection_reference(
    protection: Any,
) -> Optional[HaltProtectionReference]:

    if protection is None:
        return None

    return HaltProtectionReference(
        protection_id=_hc_text(
            protection,
            "protection_id",
            "result_id",
            "id",
            default="",
        ),
        status=_hc_text(
            protection,
            "status",
            default="UNKNOWN",
        ),
        protection_state=_hc_text(
            protection,
            "protection_state",
            "state",
            default="UNKNOWN",
        ),
        health=_hc_text(
            protection,
            "health",
            default="UNKNOWN",
        ),
        disposition=_hc_text(
            protection,
            "disposition",
            default="UNKNOWN",
        ),
        requires_block=_hc_bool(
            protection,
            "requires_block",
            default=False,
        ),
        requires_protection=_hc_bool(
            protection,
            "requires_protection",
            default=False,
        ),
        raw_result=protection,
    )


# ============================================================
# RECONCILIATION ADAPTER
# ============================================================

def build_halt_reconciliation_reference(
    reconciliation: Any,
) -> Optional[HaltReconciliationReference]:

    if reconciliation is None:
        return None

    return HaltReconciliationReference(
        reconciliation_id=_hc_text(
            reconciliation,
            "reconciliation_id",
            "result_id",
            "id",
            default="",
        ),
        status=_hc_text(
            reconciliation,
            "status",
            default="UNKNOWN",
        ),
        reconciliation_state=_hc_text(
            reconciliation,
            "reconciliation_state",
            "state",
            default="UNKNOWN",
        ),
        health=_hc_text(
            reconciliation,
            "health",
            default="UNKNOWN",
        ),
        disposition=_hc_text(
            reconciliation,
            "disposition",
            default="UNKNOWN",
        ),
        mismatch_type=_hc_text(
            reconciliation,
            "mismatch_type",
            default="NONE",
        ),
        requires_block=_hc_bool(
            reconciliation,
            "requires_block",
            default=False,
        ),
        requires_protection=_hc_bool(
            reconciliation,
            "requires_protection",
            default=False,
        ),
        requires_review=_hc_bool(
            reconciliation,
            "requires_review",
            default=False,
        ),
        raw_result=reconciliation,
    )


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_halt_controller_request(
    request: HaltControllerRequest,
) -> HaltContractValidation:

    errors: list[str] = []
    warnings: list[str] = []

    if request is None:
        return HaltContractValidation(
            status=HaltContractStatus.INVALID,
            errors=("request is required",),
        )

    if request.emergency_control is None:
        errors.append("emergency_control is required")

    if not request.request_id:
        errors.append("request_id is required")

    if not isinstance(request.metadata, Mapping):
        errors.append("metadata must be a Mapping")

    if errors:
        return HaltContractValidation(
            status=HaltContractStatus.INVALID,
            errors=tuple(errors),
            warnings=tuple(warnings),
        )

    return HaltContractValidation(
        status=HaltContractStatus.VALID,
        errors=(),
        warnings=tuple(warnings),
    )


# ============================================================
# END OF PART 1 / 5
# ============================================================
# ============================================================
# ROBOMLM_PLUS — halt_controller.py
# PART 2 / 5
# HALT INTELLIGENCE + ASSESSMENT
# ============================================================


# ============================================================
# CONSISTENCY / DATA STATE
# ============================================================

class HaltConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONFLICTING = "CONFLICTING"
    INSUFFICIENT = "INSUFFICIENT"


class HaltDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"


# ============================================================
# REQUIREMENTS
# ============================================================

@dataclass(frozen=True)
class HaltRequirements:
    emergency_available: bool
    emergency_state_available: bool
    emergency_severity_available: bool
    halt_signal_available: bool

    monitor_available: bool
    protection_available: bool
    reconciliation_available: bool
    risk_available: bool
    decision_available: bool
    account_available: bool
    execution_available: bool

    identity_consistent: bool
    control_consistent: bool


# ============================================================
# HALT INTELLIGENCE
# ============================================================

@dataclass(frozen=True)
class HaltIntelligence:
    consistency: HaltConsistency
    data_state: HaltDataState
    state: HaltControllerState
    severity: HaltSeverity
    disposition: HaltDisposition

    halt_triggered: bool
    halt_required: bool

    emergency_triggered: bool
    protection_required: bool
    reconciliation_block: bool
    monitor_halt: bool

    rationale: str
    warnings: tuple[str, ...] = ()
    source: str = HALT_CONTROLLER_ENGINE


# ============================================================
# ASSESSMENT
# ============================================================

@dataclass(frozen=True)
class HaltAssessment:
    intelligence: HaltIntelligence
    requirements: HaltRequirements

    decision: Optional[HaltDecisionReference]
    risk: Optional[HaltRiskReference]
    cas: Optional[HaltCASReference]
    emergency: Optional[HaltEmergencyReference]
    monitor: Optional[HaltMonitorReference]
    protection: Optional[HaltProtectionReference]
    reconciliation: Optional[HaltReconciliationReference]

    rationale: str
    warnings: tuple[str, ...] = ()


# ============================================================
# NORMALIZATION HELPERS
# ============================================================

def _hc_normalized_text(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, Enum):
        value = value.value

    return str(value).strip().upper()


def _hc_status_is_blocking(value: Any) -> bool:
    status = _hc_normalized_text(value)

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
    }


def _hc_status_is_unknown(value: Any) -> bool:
    status = _hc_normalized_text(value)

    return status in {
        "",
        "UNKNOWN",
        "UNSPECIFIED",
        "NONE",
        "N/A",
        "NA",
        "NULL",
    }


def _hc_severity(value: Any) -> HaltSeverity:
    severity = _hc_normalized_text(value)

    try:
        return HaltSeverity(severity)
    except ValueError:
        return HaltSeverity.NONE


# ============================================================
# REQUIREMENT EVALUATION
# ============================================================

def evaluate_halt_requirements(
    request: HaltControllerRequest,
) -> HaltRequirements:

    emergency = build_halt_emergency_reference(
        request.emergency_control
    )

    monitor = build_halt_monitor_reference(
        request.position_monitor
    )

    protection = build_halt_protection_reference(
        request.protection_state
    )

    reconciliation = build_halt_reconciliation_reference(
        request.reconciliation_state
    )

    risk = build_halt_risk_reference(
        request.risk_state
    )

    decision = build_halt_decision_reference(
        request.decision_state
    )

    emergency_available = emergency is not None

    emergency_state_available = bool(
        emergency
        and not _hc_status_is_unknown(emergency.state)
    )

    emergency_severity_available = bool(
        emergency
        and not _hc_status_is_unknown(emergency.severity)
    )

    halt_signal_available = bool(
        emergency
        and (
            emergency.halt_required
            or emergency.emergency_triggered
        )
    )

    identity_consistent = True
    control_consistent = True

    if monitor and reconciliation:
        monitor_state = _hc_normalized_text(
            monitor.disposition
        )
        reconciliation_state = _hc_normalized_text(
            reconciliation.disposition
        )

        if (
            monitor_state == "BLOCK"
            and reconciliation_state == "ACCEPT"
        ):
            control_consistent = False

    return HaltRequirements(
        emergency_available=emergency_available,
        emergency_state_available=emergency_state_available,
        emergency_severity_available=emergency_severity_available,
        halt_signal_available=halt_signal_available,

        monitor_available=monitor is not None,
        protection_available=protection is not None,
        reconciliation_available=reconciliation is not None,
        risk_available=risk is not None,
        decision_available=decision is not None,

        account_available=request.account_state is not None,
        execution_available=request.execution_state is not None,

        identity_consistent=identity_consistent,
        control_consistent=control_consistent,
    )


# ============================================================
# DATA STATE
# ============================================================

def evaluate_halt_data_state(
    requirements: HaltRequirements,
) -> HaltDataState:

    if not requirements.emergency_available:
        return HaltDataState.MISSING

    if (
        not requirements.emergency_state_available
        or not requirements.emergency_severity_available
    ):
        return HaltDataState.PARTIAL

    if not requirements.identity_consistent:
        return HaltDataState.PARTIAL

    return HaltDataState.COMPLETE


# ============================================================
# CONSISTENCY
# ============================================================

def evaluate_halt_consistency(
    requirements: HaltRequirements,
    emergency: Optional[HaltEmergencyReference],
    monitor: Optional[HaltMonitorReference],
    protection: Optional[HaltProtectionReference],
    reconciliation: Optional[HaltReconciliationReference],
    risk: Optional[HaltRiskReference],
) -> HaltConsistency:

    if not requirements.emergency_available:
        return HaltConsistency.INSUFFICIENT

    if not requirements.control_consistent:
        return HaltConsistency.CONFLICTING

    if (
        reconciliation
        and reconciliation.requires_block
    ):
        return HaltConsistency.CONFLICTING

    if (
        protection
        and protection.requires_block
    ):
        return HaltConsistency.CONFLICTING

    if (
        risk
        and _hc_status_is_blocking(risk.status)
    ):
        return HaltConsistency.CONFLICTING

    if (
        emergency
        and emergency.halt_required
    ):
        return HaltConsistency.CONSISTENT

    if (
        monitor
        and monitor.requires_halt
    ):
        return HaltConsistency.CONSISTENT

    return HaltConsistency.CONSISTENT


# ============================================================
# HALT TRIGGER EVALUATION
# ============================================================

def evaluate_halt_trigger(
    emergency: Optional[HaltEmergencyReference],
    monitor: Optional[HaltMonitorReference],
    protection: Optional[HaltProtectionReference],
    reconciliation: Optional[HaltReconciliationReference],
    risk: Optional[HaltRiskReference],
) -> tuple[bool, bool, bool, bool, bool]:

    emergency_triggered = bool(
        emergency
        and emergency.emergency_triggered
    )

    emergency_halt = bool(
        emergency
        and emergency.halt_required
    )

    monitor_halt = bool(
        monitor
        and monitor.requires_halt
    )

    reconciliation_block = bool(
        reconciliation
        and reconciliation.requires_block
    )

    risk_critical = bool(
        risk
        and _hc_severity(risk.severity)
        in {
            HaltSeverity.CRITICAL,
        }
    )

    protection_block = bool(
        protection
        and protection.requires_block
    )

    halt_required = bool(
        emergency_halt
        or monitor_halt
        or reconciliation_block
        or risk_critical
        or protection_block
    )

    return (
        emergency_triggered,
        halt_required,
        monitor_halt,
        reconciliation_block,
        protection_block,
    )


# ============================================================
# STATE EVALUATION
# ============================================================

def evaluate_halt_state(
    data_state: HaltDataState,
    consistency: HaltConsistency,
    halt_required: bool,
    emergency_triggered: bool,
) -> HaltControllerState:

    if data_state == HaltDataState.MISSING:
        return HaltControllerState.UNKNOWN

    if consistency == HaltConsistency.CONFLICTING:
        return HaltControllerState.BLOCKED

    if emergency_triggered and halt_required:
        return HaltControllerState.HALT_REQUIRED

    if halt_required:
        return HaltControllerState.HALT_REQUIRED

    if data_state == HaltDataState.PARTIAL:
        return HaltControllerState.CAUTION

    return HaltControllerState.NORMAL


# ============================================================
# SEVERITY EVALUATION
# ============================================================

def evaluate_halt_severity(
    state: HaltControllerState,
    emergency: Optional[HaltEmergencyReference],
    risk: Optional[HaltRiskReference],
    reconciliation: Optional[HaltReconciliationReference],
    protection: Optional[HaltProtectionReference],
) -> HaltSeverity:

    severities: list[HaltSeverity] = []

    if emergency:
        severities.append(
            _hc_severity(emergency.severity)
        )

    if risk:
        severities.append(
            _hc_severity(risk.severity)
        )

    if state in {
        HaltControllerState.HALTED,
        HaltControllerState.BLOCKED,
    }:
        severities.append(HaltSeverity.CRITICAL)

    if reconciliation and reconciliation.requires_block:
        severities.append(HaltSeverity.CRITICAL)

    if protection and protection.requires_block:
        severities.append(HaltSeverity.CRITICAL)

    if not severities:
        return HaltSeverity.NONE

    return max(
        severities,
        key=lambda item: {
            HaltSeverity.NONE: 0,
            HaltSeverity.LOW: 1,
            HaltSeverity.MEDIUM: 2,
            HaltSeverity.HIGH: 3,
            HaltSeverity.CRITICAL: 4,
        }[item],
    )


# ============================================================
# DISPOSITION
# ============================================================

def evaluate_halt_disposition(
    state: HaltControllerState,
    severity: HaltSeverity,
    consistency: HaltConsistency,
) -> HaltDisposition:

    if consistency == HaltConsistency.INSUFFICIENT:
        return HaltDisposition.REVIEW

    if consistency == HaltConsistency.CONFLICTING:
        return HaltDisposition.BLOCK

    if state in {
        HaltControllerState.HALTED,
        HaltControllerState.HALT_REQUIRED,
    }:
        return HaltDisposition.HALT

    if state == HaltControllerState.BLOCKED:
        return HaltDisposition.BLOCK

    if severity == HaltSeverity.CRITICAL:
        return HaltDisposition.HALT

    if state == HaltControllerState.CAUTION:
        return HaltDisposition.REVIEW

    if state == HaltControllerState.NORMAL:
        return HaltDisposition.CONTINUE

    return HaltDisposition.UNKNOWN


# ============================================================
# INTELLIGENCE BUILDER
# ============================================================

def build_halt_intelligence(
    requirements: HaltRequirements,
    emergency: Optional[HaltEmergencyReference],
    monitor: Optional[HaltMonitorReference],
    protection: Optional[HaltProtectionReference],
    reconciliation: Optional[HaltReconciliationReference],
    risk: Optional[HaltRiskReference],
) -> HaltIntelligence:

    data_state = evaluate_halt_data_state(
        requirements
    )

    consistency = evaluate_halt_consistency(
        requirements,
        emergency,
        monitor,
        protection,
        reconciliation,
        risk,
    )

    (
        emergency_triggered,
        halt_required,
        monitor_halt,
        reconciliation_block,
        protection_block,
    ) = evaluate_halt_trigger(
        emergency,
        monitor,
        protection,
        reconciliation,
        risk,
    )

    state = evaluate_halt_state(
        data_state,
        consistency,
        halt_required,
        emergency_triggered,
    )

    severity = evaluate_halt_severity(
        state,
        emergency,
        risk,
        reconciliation,
        protection,
    )

    disposition = evaluate_halt_disposition(
        state,
        severity,
        consistency,
    )

    warnings: list[str] = []

    if data_state == HaltDataState.PARTIAL:
        warnings.append(
            "Halt Controller input context is partial."
        )

    if consistency == HaltConsistency.CONFLICTING:
        warnings.append(
            "Conflicting control state detected; fail-closed."
        )

    if halt_required:
        warnings.append(
            "HALT_REQUIRED is a control state; no halt action or order was created."
        )

    if protection_block:
        warnings.append(
            "Protection layer reported a blocking condition."
        )

    if reconciliation_block:
        warnings.append(
            "Reconciliation reported a blocking condition."
        )

    rationale_parts: list[str] = []

    if emergency_triggered:
        rationale_parts.append(
            "Emergency Control reported an emergency trigger."
        )

    if halt_required:
        rationale_parts.append(
            "Established safety conditions require halt state."
        )

    if not rationale_parts:
        rationale_parts.append(
            "No established halt condition is currently active."
        )

    return HaltIntelligence(
        consistency=consistency,
        data_state=data_state,
        state=state,
        severity=severity,
        disposition=disposition,

        halt_triggered=bool(
            emergency_triggered or halt_required
        ),
        halt_required=halt_required,

        emergency_triggered=emergency_triggered,
        protection_required=bool(
            protection
            and protection.requires_protection
        ),
        reconciliation_block=reconciliation_block,
        monitor_halt=monitor_halt,

        rationale=" ".join(rationale_parts),
        warnings=tuple(warnings),
    )


# ============================================================
# ASSESSMENT BUILDER
# ============================================================

def build_halt_assessment(
    request: HaltControllerRequest,
) -> HaltAssessment:

    requirements = evaluate_halt_requirements(
        request
    )

    decision = build_halt_decision_reference(
        request.decision_state
    )

    risk = build_halt_risk_reference(
        request.risk_state
    )

    cas = build_halt_cas_reference(
        _hc_read_value(
            request.execution_state,
            "cas",
            "cas_result",
            default=None,
        )
    )

    emergency = build_halt_emergency_reference(
        request.emergency_control
    )

    monitor = build_halt_monitor_reference(
        request.position_monitor
    )

    protection = build_halt_protection_reference(
        request.protection_state
    )

    reconciliation = build_halt_reconciliation_reference(
        request.reconciliation_state
    )

    intelligence = build_halt_intelligence(
        requirements=requirements,
        emergency=emergency,
        monitor=monitor,
        protection=protection,
        reconciliation=reconciliation,
        risk=risk,
    )

    warnings = list(intelligence.warnings)

    if cas is None:
        warnings.append(
            "CAS reference unavailable; Halt Controller does not infer authorization."
        )

    return HaltAssessment(
        intelligence=intelligence,
        requirements=requirements,

        decision=decision,
        risk=risk,
        cas=cas,
        emergency=emergency,
        monitor=monitor,
        protection=protection,
        reconciliation=reconciliation,

        rationale=intelligence.rationale,
        warnings=tuple(warnings),
    )


# ============================================================
# END OF PART 2 / 5
# ============================================================
# ============================================================
# ROBOMLM_PLUS — halt_controller.py
# PART 3 / 5
# HALT RESULT + CONTRACT + SAFETY GATE
# ============================================================


# ============================================================
# ACTION / CONTRACT STATES
# ============================================================

class HaltActionState(str, Enum):
    NONE = "NONE"
    REVIEW = "REVIEW"
    HALT = "HALT"
    BLOCK = "BLOCK"


class HaltControllerContractState(str, Enum):
    VALID = "VALID"
    INCOMPLETE = "INCOMPLETE"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


# ============================================================
# RESULT CONTRACT
# ============================================================

@dataclass(frozen=True)
class HaltControllerResult:
    request_id: str
    result_id: str

    status: HaltControllerStatus
    state: HaltControllerState
    severity: HaltSeverity
    consistency: HaltConsistency
    data_state: HaltDataState
    disposition: HaltDisposition
    action_state: HaltActionState

    halt_triggered: bool
    halt_required: bool

    emergency_triggered: bool
    protection_required: bool
    reconciliation_block: bool
    monitor_halt: bool

    decision: Optional[HaltDecisionReference]
    risk: Optional[HaltRiskReference]
    cas: Optional[HaltCASReference]
    emergency: Optional[HaltEmergencyReference]
    monitor: Optional[HaltMonitorReference]
    protection: Optional[HaltProtectionReference]
    reconciliation: Optional[HaltReconciliationReference]

    rationale: str
    warnings: tuple[str, ...] = ()

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def is_valid(self) -> bool:
        return (
            bool(self.request_id)
            and bool(self.result_id)
            and self.status != HaltControllerStatus.INVALID
            and self.state != HaltControllerState.UNKNOWN
            and self.consistency != HaltConsistency.INSUFFICIENT
        )

    @property
    def requires_review(self) -> bool:
        return (
            self.disposition == HaltDisposition.REVIEW
            or self.action_state == HaltActionState.REVIEW
        )

    @property
    def requires_halt(self) -> bool:
        return (
            self.halt_required
            or self.disposition == HaltDisposition.HALT
            or self.action_state == HaltActionState.HALT
        )

    @property
    def requires_block(self) -> bool:
        return (
            self.disposition == HaltDisposition.BLOCK
            or self.action_state == HaltActionState.BLOCK
            or self.state == HaltControllerState.BLOCKED
        )

    @property
    def is_action_request(self) -> bool:
        return False


# ============================================================
# HALT CONTRACT
# ============================================================

@dataclass(frozen=True)
class HaltControllerContract:
    halt_id: str
    request_id: str

    state: HaltControllerContractState
    result: HaltControllerResult
    action_state: HaltActionState

    rationale: str
    warnings: tuple[str, ...] = ()

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def is_valid(self) -> bool:
        return (
            bool(self.halt_id)
            and bool(self.request_id)
            and self.result.is_valid
            and self.state == HaltControllerContractState.VALID
        )

    @property
    def is_action_request(self) -> bool:
        return False


# ============================================================
# ACTION STATE
# ============================================================

def _hc_action_state(
    disposition: HaltDisposition,
) -> HaltActionState:

    if disposition == HaltDisposition.HALT:
        return HaltActionState.HALT

    if disposition == HaltDisposition.BLOCK:
        return HaltActionState.BLOCK

    if disposition == HaltDisposition.REVIEW:
        return HaltActionState.REVIEW

    return HaltActionState.NONE


# ============================================================
# RESULT STATUS
# ============================================================

def _hc_result_status(
    intelligence: HaltIntelligence,
) -> HaltControllerStatus:

    if intelligence.data_state == HaltDataState.MISSING:
        return HaltControllerStatus.INVALID

    if intelligence.consistency == HaltConsistency.CONFLICTING:
        return HaltControllerStatus.BLOCKED

    if intelligence.halt_required:
        return HaltControllerStatus.HALT_REQUIRED

    if intelligence.data_state == HaltDataState.PARTIAL:
        return HaltControllerStatus.WARNING

    if intelligence.state == HaltControllerState.CAUTION:
        return HaltControllerStatus.WARNING

    return HaltControllerStatus.READY


# ============================================================
# RESULT BUILDER
# ============================================================

def build_halt_controller_result(
    assessment: HaltAssessment,
) -> HaltControllerResult:

    intelligence = assessment.intelligence

    status = _hc_result_status(
        intelligence
    )

    action_state = _hc_action_state(
        intelligence.disposition
    )

    warnings = list(assessment.warnings)

    if intelligence.halt_required:
        warnings.append(
            "HALT_REQUIRED represents a control decision; no halt order was created."
        )

    if intelligence.consistency == HaltConsistency.CONFLICTING:
        warnings.append(
            "Conflicting safety state detected; downstream action must fail closed."
        )

    return HaltControllerResult(
        request_id="",
        result_id=str(uuid4()),

        status=status,
        state=intelligence.state,
        severity=intelligence.severity,
        consistency=intelligence.consistency,
        data_state=intelligence.data_state,
        disposition=intelligence.disposition,
        action_state=action_state,

        halt_triggered=intelligence.halt_triggered,
        halt_required=intelligence.halt_required,

        emergency_triggered=intelligence.emergency_triggered,
        protection_required=intelligence.protection_required,
        reconciliation_block=intelligence.reconciliation_block,
        monitor_halt=intelligence.monitor_halt,

        decision=assessment.decision,
        risk=assessment.risk,
        cas=assessment.cas,
        emergency=assessment.emergency,
        monitor=assessment.monitor,
        protection=assessment.protection,
        reconciliation=assessment.reconciliation,

        rationale=assessment.rationale,
        warnings=tuple(warnings),
    )


# ============================================================
# REQUEST-ID BINDING
# ============================================================

def bind_halt_request_id(
    result: HaltControllerResult,
    request_id: str,
) -> HaltControllerResult:

    return HaltControllerResult(
        request_id=request_id,
        result_id=result.result_id,

        status=result.status,
        state=result.state,
        severity=result.severity,
        consistency=result.consistency,
        data_state=result.data_state,
        disposition=result.disposition,
        action_state=result.action_state,

        halt_triggered=result.halt_triggered,
        halt_required=result.halt_required,

        emergency_triggered=result.emergency_triggered,
        protection_required=result.protection_required,
        reconciliation_block=result.reconciliation_block,
        monitor_halt=result.monitor_halt,

        decision=result.decision,
        risk=result.risk,
        cas=result.cas,
        emergency=result.emergency,
        monitor=result.monitor,
        protection=result.protection,
        reconciliation=result.reconciliation,

        rationale=result.rationale,
        warnings=result.warnings,
        created_at=result.created_at,
    )


# ============================================================
# CONTRACT STATE
# ============================================================

def _hc_contract_state(
    result: HaltControllerResult,
) -> HaltControllerContractState:

    if not result.is_valid:
        return HaltControllerContractState.INVALID

    if result.data_state == HaltDataState.MISSING:
        return HaltControllerContractState.INCOMPLETE

    if result.consistency == HaltConsistency.CONFLICTING:
        return HaltControllerContractState.BLOCKED

    if result.requires_block:
        return HaltControllerContractState.BLOCKED

    if result.data_state == HaltDataState.PARTIAL:
        return HaltControllerContractState.INCOMPLETE

    return HaltControllerContractState.VALID


# ============================================================
# CONTRACT BUILDER
# ============================================================

def build_halt_controller_contract(
    result: HaltControllerResult,
    request_id: Optional[str] = None,
) -> HaltControllerContract:

    bound_result = result

    if request_id:
        bound_result = bind_halt_request_id(
            result,
            request_id,
        )

    state = _hc_contract_state(
        bound_result
    )

    warnings = list(bound_result.warnings)

    if bound_result.requires_halt:
        warnings.append(
            "Halt state identified; execution layer must interpret control state separately."
        )

    return HaltControllerContract(
        halt_id=str(uuid4()),
        request_id=bound_result.request_id,
        state=state,
        result=bound_result,
        action_state=bound_result.action_state,
        rationale=bound_result.rationale,
        warnings=tuple(warnings),
    )


# ============================================================
# DOWNSTREAM SAFETY GATE
# ============================================================

def is_halt_controller_safe_to_forward(
    contract: Optional[HaltControllerContract],
) -> bool:

    if contract is None:
        return False

    if not contract.is_valid:
        return False

    if contract.is_action_request:
        return False

    if not contract.result.is_valid:
        return False

    if contract.result.consistency == HaltConsistency.CONFLICTING:
        return False

    if contract.result.requires_block:
        return False

    return True


# ============================================================
# RESULT VALIDATION
# ============================================================

def validate_halt_controller_result(
    result: Optional[HaltControllerResult],
) -> HaltContractValidation:

    errors: list[str] = []
    warnings: list[str] = []

    if result is None:
        return HaltContractValidation(
            status=HaltContractStatus.INVALID,
            errors=("result is required",),
        )

    if not result.request_id:
        errors.append("request_id is required")

    if not result.result_id:
        errors.append("result_id is required")

    if result.status == HaltControllerStatus.INVALID:
        errors.append("result status is INVALID")

    if result.state == HaltControllerState.UNKNOWN:
        errors.append("halt state is UNKNOWN")

    if result.consistency == HaltConsistency.INSUFFICIENT:
        errors.append(
            "halt consistency is INSUFFICIENT"
        )

    if result.requires_halt:
        warnings.append(
            "HALT_REQUIRED detected; no execution action was created."
        )

    if result.requires_block:
        warnings.append(
            "Blocking halt state detected."
        )

    if result.is_action_request:
        errors.append(
            "Halt Controller must never create an action request."
        )

    if errors:
        return HaltContractValidation(
            status=HaltContractStatus.INVALID,
            errors=tuple(errors),
            warnings=tuple(warnings),
        )

    return HaltContractValidation(
        status=HaltContractStatus.VALID,
        errors=(),
        warnings=tuple(warnings),
    )


# ============================================================
# END OF PART 3 / 5
# ============================================================
# ============================================================
# ROBOMLM_PLUS — halt_controller.py
# PART 4 / 5
# HALT CONTROLLER ENGINE + PUBLIC API
# ============================================================


# ============================================================
# HALT CONTROLLER ENGINE
# ============================================================

class HaltControllerEngine:
    """
    ROBOMLM_PLUS Halt Controller.

    Pipeline:

        Emergency Control
              ↓
        Halt Assessment
              ↓
        Halt Intelligence
              ↓
        Halt Result
              ↓
        Halt Contract
              ↓
        Downstream Control State

    Hard boundaries:
        - does not synthesize market direction
        - does not recalculate risk
        - does not create authorization
        - does not create orders
        - does not execute trades
        - does not modify positions
        - does not override D13
        - does not override Risk
        - does not override CAS
    """

    ENGINE_NAME = HALT_CONTROLLER_ENGINE
    ENGINE_VERSION = HALT_CONTROLLER_VERSION

    def validate_request(
        self,
        request: HaltControllerRequest,
    ) -> HaltContractValidation:
        return validate_halt_controller_request(request)

    def _invalid_contract(
        self,
        request: Optional[HaltControllerRequest],
        errors: tuple[str, ...],
    ) -> HaltControllerContract:

        request_id = (
            request.request_id
            if request is not None
            else ""
        )

        result = HaltControllerResult(
            request_id=request_id,
            result_id=str(uuid4()),

            status=HaltControllerStatus.INVALID,
            state=HaltControllerState.UNKNOWN,
            severity=HaltSeverity.CRITICAL,
            consistency=HaltConsistency.INSUFFICIENT,
            data_state=HaltDataState.MISSING,
            disposition=HaltDisposition.BLOCK,
            action_state=HaltActionState.BLOCK,

            halt_triggered=False,
            halt_required=False,

            emergency_triggered=False,
            protection_required=False,
            reconciliation_block=False,
            monitor_halt=False,

            decision=None,
            risk=None,
            cas=None,
            emergency=None,
            monitor=None,
            protection=None,
            reconciliation=None,

            rationale="Invalid Halt Controller request; fail-closed.",
            warnings=errors,
        )

        return HaltControllerContract(
            halt_id=str(uuid4()),
            request_id=request_id,
            state=HaltControllerContractState.INVALID,
            result=result,
            action_state=HaltActionState.BLOCK,
            rationale=result.rationale,
            warnings=errors,
        )

    def process(
        self,
        request: HaltControllerRequest,
    ) -> HaltControllerContract:

        validation = self.validate_request(request)

        if not validation.is_valid:
            return self._invalid_contract(
                request,
                validation.errors,
            )

        try:
            assessment = build_halt_assessment(
                request
            )

            result = build_halt_controller_result(
                assessment
            )

            result = bind_halt_request_id(
                result,
                request.request_id,
            )

            result_validation = validate_halt_controller_result(
                result
            )

            if not result_validation.is_valid:
                return self._invalid_contract(
                    request,
                    result_validation.errors,
                )

            contract = build_halt_controller_contract(
                result,
                request.request_id,
            )

            return contract

        except Exception as exc:
            return self._invalid_contract(
                request,
                (
                    "Halt Controller processing failed.",
                    str(exc),
                ),
            )

    def evaluate(
        self,
        request: HaltControllerRequest,
    ) -> HaltControllerContract:
        return self.process(request)

    def is_ready(
        self,
        contract: Optional[HaltControllerContract],
    ) -> bool:

        if contract is None:
            return False

        return (
            contract.is_valid
            and contract.state
            in {
                HaltControllerContractState.VALID,
                HaltControllerContractState.BLOCKED,
            }
        )

    def requires_halt(
        self,
        contract: Optional[HaltControllerContract],
    ) -> bool:

        if contract is None:
            return False

        return contract.result.requires_halt

    def requires_block(
        self,
        contract: Optional[HaltControllerContract],
    ) -> bool:

        if contract is None:
            return False

        return contract.result.requires_block

    def requires_review(
        self,
        contract: Optional[HaltControllerContract],
    ) -> bool:

        if contract is None:
            return False

        return contract.result.requires_review

    def halt_state(
        self,
        contract: Optional[HaltControllerContract],
    ) -> HaltControllerState:

        if contract is None:
            return HaltControllerState.UNKNOWN

        return contract.result.state

    def halt_severity(
        self,
        contract: Optional[HaltControllerContract],
    ) -> HaltSeverity:

        if contract is None:
            return HaltSeverity.NONE

        return contract.result.severity

    def is_safe_to_forward(
        self,
        contract: Optional[HaltControllerContract],
    ) -> bool:

        return is_halt_controller_safe_to_forward(
            contract
        )

    def audit_summary(
        self,
        contract: Optional[HaltControllerContract],
    ) -> dict[str, Any]:

        if contract is None:
            return {
                "engine": self.ENGINE_NAME,
                "version": self.ENGINE_VERSION,
                "valid": False,
                "safe_to_forward": False,
                "halt_required": False,
                "requires_block": False,
                "requires_review": False,
            }

        result = contract.result

        return {
            "engine": self.ENGINE_NAME,
            "version": self.ENGINE_VERSION,

            "halt_id": contract.halt_id,
            "request_id": contract.request_id,
            "result_id": result.result_id,

            "contract_state": contract.state.value,
            "status": result.status.value,
            "state": result.state.value,
            "severity": result.severity.value,
            "consistency": result.consistency.value,
            "data_state": result.data_state.value,
            "disposition": result.disposition.value,
            "action_state": result.action_state.value,

            "halt_triggered": result.halt_triggered,
            "halt_required": result.halt_required,
            "emergency_triggered": result.emergency_triggered,
            "protection_required": result.protection_required,
            "monitor_halt": result.monitor_halt,
            "reconciliation_block": result.reconciliation_block,

            "valid": contract.is_valid,
            "safe_to_forward": self.is_safe_to_forward(
                contract
            ),
            "requires_halt": result.requires_halt,
            "requires_block": result.requires_block,
            "requires_review": result.requires_review,

            # Hard authority invariants.
            "decision_synthesized": False,
            "risk_recalculated": False,
            "authorization_created": False,
            "execution_created": False,
            "order_created": False,
            "position_modified": False,
            "d13_overridden": False,
            "risk_overridden": False,
            "cas_overridden": False,

            "is_action_request": contract.is_action_request,
        }


# ============================================================
# PUBLIC ENGINE INSTANCE
# ============================================================

halt_controller_engine = HaltControllerEngine()


# ============================================================
# PUBLIC PROCESSING FUNCTIONS
# ============================================================

def evaluate_halt_controller(
    request: HaltControllerRequest,
) -> HaltControllerContract:
    return halt_controller_engine.evaluate(request)


def process_halt_controller(
    request: HaltControllerRequest,
) -> HaltControllerContract:
    return halt_controller_engine.process(request)


def halt_controller_ready(
    contract: Optional[HaltControllerContract],
) -> bool:
    return halt_controller_engine.is_ready(contract)


def halt_controller_requires_halt(
    contract: Optional[HaltControllerContract],
) -> bool:
    return halt_controller_engine.requires_halt(contract)


def halt_controller_requires_block(
    contract: Optional[HaltControllerContract],
) -> bool:
    return halt_controller_engine.requires_block(contract)


def halt_controller_requires_review(
    contract: Optional[HaltControllerContract],
) -> bool:
    return halt_controller_engine.requires_review(contract)


def halt_controller_state(
    contract: Optional[HaltControllerContract],
) -> HaltControllerState:
    return halt_controller_engine.halt_state(contract)


def halt_controller_severity(
    contract: Optional[HaltControllerContract],
) -> HaltSeverity:
    return halt_controller_engine.halt_severity(contract)


def halt_controller_safe(
    contract: Optional[HaltControllerContract],
) -> bool:
    return halt_controller_engine.is_safe_to_forward(contract)


def halt_controller_audit(
    contract: Optional[HaltControllerContract],
) -> dict[str, Any]:
    return halt_controller_engine.audit_summary(contract)


# ============================================================
# HEALTH CHECK
# ============================================================

def halt_controller_health_check() -> dict[str, Any]:
    return {
        "engine": HALT_CONTROLLER_ENGINE,
        "version": HALT_CONTROLLER_VERSION,
        "status": "READY",
        "contract_layer": True,
        "intelligence_layer": True,
        "result_layer": True,
        "safety_gate": True,
        "fail_closed": True,

        "decision_synthesis": False,
        "risk_recalculation": False,
        "authorization_creation": False,
        "execution_creation": False,
        "order_creation": False,
        "position_modification": False,
        "d13_override": False,
        "risk_override": False,
        "cas_override": False,
    }


def run_halt_controller_health_check() -> dict[str, Any]:
    return halt_controller_health_check()


# ============================================================
# ENGINE INFORMATION
# ============================================================

def get_halt_controller_engine_info() -> dict[str, Any]:
    return {
        "engine": HALT_CONTROLLER_ENGINE,
        "version": HALT_CONTROLLER_VERSION,
        "role": (
            "Interpret established emergency and safety "
            "conditions into a controlled halt state."
        ),
        "authority": {
            "decision": "D13",
            "risk": "RISK",
            "authorization": "CAS",
            "emergency": "EMERGENCY_CONTROL",
            "monitor": "POSITION_MONITOR",
            "protection": "PROTECTION",
            "reconciliation": "RECONCILIATION",
        },
        "creates_halt_order": False,
        "creates_execution": False,
        "creates_authorization": False,
        "modifies_position": False,
        "overrides_d13": False,
        "overrides_risk": False,
        "overrides_cas": False,
    }


# ============================================================
# ALIAS
# ============================================================

HaltController = HaltControllerEngine


# ============================================================
# END OF PART 4 / 5
# ============================================================
# ============================================================
# ROBOMLM_PLUS — halt_controller.py
# PART 5 / 5
# SERIALIZATION + VALIDATION + INTEGRITY + EXPORTS
# ============================================================


# ============================================================
# ENUM SERIALIZER
# ============================================================

def _hc_enum_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    return value


# ============================================================
# SAFE DICT CONVERTER
# ============================================================

def _hc_safe_dict(value: Any) -> Any:

    if value is None:
        return None

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, Mapping):
        return {
            str(key): _hc_safe_dict(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            _hc_safe_dict(item)
            for item in value
        ]

    if hasattr(value, "__dataclass_fields__"):
        return {
            key: _hc_safe_dict(
                getattr(value, key)
            )
            for key in value.__dataclass_fields__
        }

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, (str, int, float, bool)):
        return value

    return str(value)


# ============================================================
# REFERENCE SERIALIZATION
# ============================================================

def _hc_reference_to_dict(
    reference: Any,
) -> Optional[dict[str, Any]]:

    if reference is None:
        return None

    return _hc_safe_dict(reference)


# ============================================================
# RESULT SERIALIZATION
# ============================================================

def halt_controller_result_to_dict(
    result: Optional[HaltControllerResult],
) -> Optional[dict[str, Any]]:

    if result is None:
        return None

    return {
        "request_id": result.request_id,
        "result_id": result.result_id,

        "status": _hc_enum_value(result.status),
        "state": _hc_enum_value(result.state),
        "severity": _hc_enum_value(result.severity),
        "consistency": _hc_enum_value(result.consistency),
        "data_state": _hc_enum_value(result.data_state),
        "disposition": _hc_enum_value(result.disposition),
        "action_state": _hc_enum_value(result.action_state),

        "halt_triggered": result.halt_triggered,
        "halt_required": result.halt_required,
        "emergency_triggered": result.emergency_triggered,
        "protection_required": result.protection_required,
        "reconciliation_block": result.reconciliation_block,
        "monitor_halt": result.monitor_halt,

        "decision": _hc_reference_to_dict(
            result.decision
        ),
        "risk": _hc_reference_to_dict(
            result.risk
        ),
        "cas": _hc_reference_to_dict(
            result.cas
        ),
        "emergency": _hc_reference_to_dict(
            result.emergency
        ),
        "monitor": _hc_reference_to_dict(
            result.monitor
        ),
        "protection": _hc_reference_to_dict(
            result.protection
        ),
        "reconciliation": _hc_reference_to_dict(
            result.reconciliation
        ),

        "rationale": result.rationale,
        "warnings": list(result.warnings),

        "created_at": result.created_at.isoformat(),

        "integrity": {
            "is_valid": result.is_valid,
            "requires_review": result.requires_review,
            "requires_halt": result.requires_halt,
            "requires_block": result.requires_block,
            "is_action_request": result.is_action_request,
        },
    }


# ============================================================
# CONTRACT SERIALIZATION
# ============================================================

def halt_controller_to_dict(
    contract: Optional[HaltControllerContract],
) -> Optional[dict[str, Any]]:

    if contract is None:
        return None

    return {
        "halt_id": contract.halt_id,
        "request_id": contract.request_id,

        "state": _hc_enum_value(
            contract.state
        ),
        "action_state": _hc_enum_value(
            contract.action_state
        ),

        "result": halt_controller_result_to_dict(
            contract.result
        ),

        "rationale": contract.rationale,
        "warnings": list(contract.warnings),

        "created_at": contract.created_at.isoformat(),

        "contract": {
            "is_valid": contract.is_valid,
            "is_action_request": contract.is_action_request,
        },
    }


# ============================================================
# CONTRACT VALIDATION
# ============================================================

def validate_halt_controller_contract(
    contract: Optional[HaltControllerContract],
) -> HaltContractValidation:

    errors: list[str] = []
    warnings: list[str] = []

    if contract is None:
        return HaltContractValidation(
            status=HaltContractStatus.INVALID,
            errors=("contract is required",),
        )

    if not contract.halt_id:
        errors.append("halt_id is required")

    if not contract.request_id:
        errors.append("request_id is required")

    if contract.result is None:
        errors.append("result is required")

    else:
        result_validation = (
            validate_halt_controller_result(
                contract.result
            )
        )

        errors.extend(
            result_validation.errors
        )

        warnings.extend(
            result_validation.warnings
        )

        if (
            contract.request_id
            != contract.result.request_id
        ):
            errors.append(
                "contract/result request_id mismatch"
            )

    if contract.is_action_request:
        errors.append(
            "Halt Controller contract cannot be an action request"
        )

    if contract.state == HaltControllerContractState.INVALID:
        errors.append(
            "contract state is INVALID"
        )

    if (
        contract.result is not None
        and contract.result.requires_halt
    ):
        warnings.append(
            "HALT_REQUIRED is a control state only; "
            "no halt order or execution action exists."
        )

    if errors:
        return HaltContractValidation(
            status=HaltContractStatus.INVALID,
            errors=tuple(errors),
            warnings=tuple(warnings),
        )

    return HaltContractValidation(
        status=HaltContractStatus.VALID,
        errors=(),
        warnings=tuple(warnings),
    )


# ============================================================
# INTEGRITY CHECK
# ============================================================

def halt_controller_integrity_check(
    contract: Optional[HaltControllerContract],
) -> dict[str, Any]:

    validation = validate_halt_controller_contract(
        contract
    )

    if contract is None:
        return {
            "engine": HALT_CONTROLLER_ENGINE,
            "version": HALT_CONTROLLER_VERSION,
            "valid": False,
            "safe_to_forward": False,
            "errors": list(validation.errors),
            "warnings": list(validation.warnings),
        }

    result = contract.result

    safe_to_forward = (
        is_halt_controller_safe_to_forward(
            contract
        )
    )

    return {
        "engine": HALT_CONTROLLER_ENGINE,
        "version": HALT_CONTROLLER_VERSION,

        "halt_id": contract.halt_id,
        "request_id": contract.request_id,

        "contract_state": _hc_enum_value(
            contract.state
        ),
        "action_state": _hc_enum_value(
            contract.action_state
        ),

        "valid": validation.is_valid,
        "safe_to_forward": safe_to_forward,

        "halt_required": result.requires_halt,
        "requires_block": result.requires_block,
        "requires_review": result.requires_review,

        "state": _hc_enum_value(result.state),
        "severity": _hc_enum_value(result.severity),
        "consistency": _hc_enum_value(
            result.consistency
        ),
        "data_state": _hc_enum_value(
            result.data_state
        ),
        "disposition": _hc_enum_value(
            result.disposition
        ),

        "errors": list(validation.errors),
        "warnings": list(validation.warnings),

        # ====================================================
        # HARD AUTHORITY INVARIANTS
        # ====================================================

        "decision_synthesized": False,
        "risk_recalculated": False,
        "authorization_created": False,
        "execution_created": False,
        "order_created": False,
        "position_modified": False,

        "d13_overridden": False,
        "risk_overridden": False,
        "cas_overridden": False,

        "halt_action_created": False,
        "broker_halt_submitted": False,
    }


def verify_halt_controller_integrity(
    contract: Optional[HaltControllerContract],
) -> bool:

    audit = halt_controller_integrity_check(
        contract
    )

    return bool(
        audit.get("valid")
        and (
            audit.get("decision_synthesized")
            is False
        )
        and (
            audit.get("risk_recalculated")
            is False
        )
        and (
            audit.get("authorization_created")
            is False
        )
        and (
            audit.get("execution_created")
            is False
        )
        and (
            audit.get("order_created")
            is False
        )
        and (
            audit.get("position_modified")
            is False
        )
        and (
            audit.get("d13_overridden")
            is False
        )
        and (
            audit.get("risk_overridden")
            is False
        )
        and (
            audit.get("cas_overridden")
            is False
        )
        and (
            audit.get("halt_action_created")
            is False
        )
        and (
            audit.get("broker_halt_submitted")
            is False
        )
    )


# ============================================================
# HEALTH CHECK — FINAL
# ============================================================

def final_halt_controller_health_check() -> dict[str, Any]:
    return {
        "engine": HALT_CONTROLLER_ENGINE,
        "version": HALT_CONTROLLER_VERSION,

        "foundation": True,
        "references": True,
        "intelligence": True,
        "assessment": True,
        "result": True,
        "contract": True,
        "validation": True,
        "integrity": True,
        "fail_closed": True,

        "halt_state_only": True,
        "halt_action_created": False,
        "order_created": False,
        "execution_created": False,
        "authorization_created": False,
        "position_modified": False,

        "d13_override": False,
        "risk_override": False,
        "cas_override": False,

        "status": "READY",
    }


# ============================================================
# COMPLETE EXPORT SURFACE
# ============================================================

__all__ = [
    # Constants
    "HALT_CONTROLLER_ENGINE",
    "HALT_CONTROLLER_VERSION",

    # Enums
    "HaltControllerStatus",
    "HaltControllerState",
    "HaltSeverity",
    "HaltDisposition",
    "HaltContractStatus",
    "HaltConsistency",
    "HaltDataState",
    "HaltActionState",
    "HaltControllerContractState",

    # Request
    "HaltControllerRequest",

    # References
    "HaltDecisionReference",
    "HaltRiskReference",
    "HaltCASReference",
    "HaltEmergencyReference",
    "HaltMonitorReference",
    "HaltProtectionReference",
    "HaltReconciliationReference",

    # Validation
    "HaltContractValidation",

    # Requirements / intelligence
    "HaltRequirements",
    "HaltIntelligence",
    "HaltAssessment",

    # Result / contract
    "HaltControllerResult",
    "HaltControllerContract",

    # Adapters
    "build_halt_decision_reference",
    "build_halt_risk_reference",
    "build_halt_cas_reference",
    "build_halt_emergency_reference",
    "build_halt_monitor_reference",
    "build_halt_protection_reference",
    "build_halt_reconciliation_reference",

    # Requirements / intelligence
    "evaluate_halt_requirements",
    "evaluate_halt_data_state",
    "evaluate_halt_consistency",
    "evaluate_halt_trigger",
    "evaluate_halt_state",
    "evaluate_halt_severity",
    "evaluate_halt_disposition",
    "build_halt_intelligence",
    "build_halt_assessment",

    # Result / contract
    "build_halt_controller_result",
    "bind_halt_request_id",
    "build_halt_controller_contract",
    "validate_halt_controller_result",
    "validate_halt_controller_contract",
    "is_halt_controller_safe_to_forward",

    # Engine
    "HaltControllerEngine",
    "halt_controller_engine",

    # Public API
    "evaluate_halt_controller",
    "process_halt_controller",
    "halt_controller_ready",
    "halt_controller_requires_halt",
    "halt_controller_requires_block",
    "halt_controller_requires_review",
    "halt_controller_state",
    "halt_controller_severity",
    "halt_controller_safe",
    "halt_controller_audit",

    # Serialization
    "halt_controller_result_to_dict",
    "halt_controller_to_dict",

    # Integrity
    "halt_controller_integrity_check",
    "verify_halt_controller_integrity",

    # Health / info
    "halt_controller_health_check",
    "run_halt_controller_health_check",
    "final_halt_controller_health_check",
    "get_halt_controller_engine_info",

    # Alias
    "HaltController",
]


# ============================================================
# END OF PART 5 / 5
# HALT CONTROLLER COMPLETE
# ============================================================