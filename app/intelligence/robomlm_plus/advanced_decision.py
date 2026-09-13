# app/intelligence/robomlm_plus/advanced_decision.py

"""
ROBOMLM PLUS — Advanced Decision Engine
========================================

Part 1/5 — Foundation + Contracts

Role
----
Advanced Decision is a ROBOMLM PLUS operational intelligence layer.

It consumes already-authorized upstream intelligence and does NOT replace
the authority of D13 Decision Authority.

Primary upstream authorities:
    D13 Decision
    Risk Result
    CAS Result

Design principles:
    - Contract First
    - No toy scoring
    - No invented market intelligence
    - No D13 recalculation
    - No CAS bypass
    - Deterministic normalization
    - Explicit state handling
    - Traceable outputs
    - Fail-closed on invalid contracts

Later parts:
    Part 2 — Decision Intelligence
    Part 3 — Risk/CAS-aware Advanced Decision
    Part 4 — Advanced Decision Engine
    Part 5 — Public API + Validation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Optional
from uuid import uuid4


# ============================================================================
# PART 1 — FOUNDATION + CONTRACTS
# ============================================================================


class AdvancedDecisionStatus(str, Enum):
    """
    Operational status of the PLUS advanced-decision layer.

    This status is NOT a replacement for the D13 decision itself.
    """

    READY = "READY"
    REFINED = "REFINED"
    CONDITIONAL = "CONDITIONAL"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


class DecisionDisposition(str, Enum):
    """
    Normalized directional/action disposition.

    Directional vocabulary is intentionally limited to stable semantic
    families. Detailed D13 semantics remain upstream.
    """

    UP = "UP"
    DOWN = "DOWN"
    NEUTRAL = "NEUTRAL"
    HOLD = "HOLD"
    UNKNOWN = "UNKNOWN"


class ReadinessLevel(str, Enum):
    """
    Operational readiness produced by PLUS.

    READINESS is not permission to execute.
    CAS remains authoritative for authorization/suitability.
    """

    NOT_READY = "NOT_READY"
    ANALYSIS_READY = "ANALYSIS_READY"
    DECISION_READY = "DECISION_READY"
    EXECUTION_PREPARATION_READY = "EXECUTION_PREPARATION_READY"


class ContractValidationStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


# ----------------------------------------------------------------------------
# Immutable input contract
# ----------------------------------------------------------------------------

@dataclass(frozen=True)
class AdvancedDecisionRequest:
    """
    Contract entering Advanced Decision.

    d13_decision:
        Authoritative D13 decision payload/object.

    risk_result:
        Upstream risk-engine result.

    cas_result:
        CAS authorization/suitability result.

    market_context:
        Optional already-computed market context.

    evidence:
        Optional upstream evidence references.

    metadata:
        Trace/context information. It must not become a source of
        independent trading intelligence.
    """

    d13_decision: Any
    risk_result: Any
    cas_result: Any

    market_context: Optional[Any] = None
    evidence: Optional[Any] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    request_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def validate(self) -> tuple[bool, tuple[str, ...]]:
        """
        Validate the minimum structural contract.

        This does not validate the internal semantics of D13, Risk or CAS.
        Those remain owned by their respective authorities.
        """

        errors: list[str] = []

        if self.d13_decision is None:
            errors.append("d13_decision is required")

        if self.risk_result is None:
            errors.append("risk_result is required")

        if self.cas_result is None:
            errors.append("cas_result is required")

        if not self.request_id.strip():
            errors.append("request_id must not be empty")

        if not isinstance(self.metadata, Mapping):
            errors.append("metadata must be a mapping")

        return not errors, tuple(errors)


# ----------------------------------------------------------------------------
# Normalized decision reference
# ----------------------------------------------------------------------------

@dataclass(frozen=True)
class DecisionReference:
    """
    Read-only normalized reference to the upstream D13 decision.

    IMPORTANT:
        This object describes D13.
        It does not create or replace a D13 decision.
    """

    decision_id: Optional[str]
    direction: DecisionDisposition

    raw_decision: Any

    confidence: Optional[float] = None
    strength: Optional[float] = None
    verdict: Optional[str] = None

    source: str = "D13"


# ----------------------------------------------------------------------------
# Normalized risk reference
# ----------------------------------------------------------------------------

@dataclass(frozen=True)
class RiskReference:
    """
    Read-only reference to upstream risk intelligence.
    """

    risk_id: Optional[str]
    status: str
    raw_result: Any

    risk_score: Optional[float] = None
    exposure: Optional[float] = None
    severity: Optional[str] = None

    source: str = "RISK"


# ----------------------------------------------------------------------------
# Normalized CAS reference
# ----------------------------------------------------------------------------

@dataclass(frozen=True)
class CASReference:
    """
    Read-only reference to the CAS decision.

    CAS remains the authorization/safety authority.
    """

    cas_id: Optional[str]
    status: str
    raw_result: Any

    authorized: Optional[bool] = None
    reason: Optional[str] = None

    source: str = "CAS"


# ----------------------------------------------------------------------------
# Contract validation result
# ----------------------------------------------------------------------------

@dataclass(frozen=True)
class ContractValidationResult:
    status: ContractValidationStatus
    errors: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:
        return self.status == ContractValidationStatus.VALID


# ----------------------------------------------------------------------------
# Advanced Decision output contract
# ----------------------------------------------------------------------------

@dataclass(frozen=True)
class AdvancedDecisionResult:
    """
    Stable Part-1 output contract.

    Later parts will populate the intelligence/refinement fields without
    changing the fundamental contract boundary.
    """

    request_id: str
    result_id: str

    status: AdvancedDecisionStatus
    readiness: ReadinessLevel

    decision: DecisionReference
    risk: RiskReference
    cas: CASReference

    contract_validation: ContractValidationResult

    rationale: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    trace: Mapping[str, Any] = field(default_factory=dict)

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def is_valid(self) -> bool:
        return self.contract_validation.is_valid

    @property
    def execution_authorized(self) -> bool:
        """
        Convenience property.

        This reflects the CAS reference only.
        It does NOT grant execution permission independently.
        """

        return bool(self.cas.authorized)

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the stable output envelope.

        Raw upstream objects are intentionally not recursively serialized
        here. Their own contracts remain authoritative.
        """

        return {
            "request_id": self.request_id,
            "result_id": self.result_id,
            "status": self.status.value,
            "readiness": self.readiness.value,
            "decision": {
                "decision_id": self.decision.decision_id,
                "direction": self.decision.direction.value,
                "confidence": self.decision.confidence,
                "strength": self.decision.strength,
                "verdict": self.decision.verdict,
                "source": self.decision.source,
            },
            "risk": {
                "risk_id": self.risk.risk_id,
                "status": self.risk.status,
                "risk_score": self.risk.risk_score,
                "exposure": self.risk.exposure,
                "severity": self.risk.severity,
                "source": self.risk.source,
            },
            "cas": {
                "cas_id": self.cas.cas_id,
                "status": self.cas.status,
                "authorized": self.cas.authorized,
                "reason": self.cas.reason,
                "source": self.cas.source,
            },
            "contract_validation": {
                "status": self.contract_validation.status.value,
                "errors": list(self.contract_validation.errors),
            },
            "rationale": list(self.rationale),
            "warnings": list(self.warnings),
            "trace": dict(self.trace),
            "created_at": self.created_at.isoformat(),
        }


# ----------------------------------------------------------------------------
# Foundation helpers
# ----------------------------------------------------------------------------

def _read_value(
    source: Any,
    *names: str,
    default: Any = None,
) -> Any:
    """
    Read a field from either mapping-like or object-like upstream contracts.

    No intelligence is calculated here.
    """

    if source is None:
        return default

    if isinstance(source, Mapping):
        for name in names:
            if name in source:
                return source[name]
        return default

    for name in names:
        if hasattr(source, name):
            return getattr(source, name)

    return default


def _normalize_direction(value: Any) -> DecisionDisposition:
    """
    Normalize only stable directional vocabulary.

    No directional inference is performed from price, score, confidence,
    or arbitrary numeric values.
    """

    if value is None:
        return DecisionDisposition.UNKNOWN

    normalized = str(value).strip().upper()

    mapping = {
        "UP": DecisionDisposition.UP,
        "BULLISH": DecisionDisposition.UP,
        "LONG": DecisionDisposition.UP,
        "CALL": DecisionDisposition.UP,

        "DOWN": DecisionDisposition.DOWN,
        "BEARISH": DecisionDisposition.DOWN,
        "SHORT": DecisionDisposition.DOWN,
        "PUT": DecisionDisposition.DOWN,

        "NEUTRAL": DecisionDisposition.NEUTRAL,
        "FLAT": DecisionDisposition.NEUTRAL,

        "HOLD": DecisionDisposition.HOLD,
    }

    return mapping.get(normalized, DecisionDisposition.UNKNOWN)


def _optional_float(value: Any) -> Optional[float]:
    """
    Safely normalize numeric optional values.

    Invalid values become None rather than creating false intelligence.
    """

    if value is None or isinstance(value, bool):
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


# ----------------------------------------------------------------------------
# Contract adapters
# ----------------------------------------------------------------------------

def build_decision_reference(
    d13_decision: Any,
) -> DecisionReference:
    """
    Build a read-only D13 reference.

    This function does NOT modify or recalculate D13.
    """

    decision_id = _read_value(
        d13_decision,
        "decision_id",
        "id",
        "event_id",
    )

    direction_value = _read_value(
        d13_decision,
        "direction",
        "decision",
        "action",
        "verdict",
    )

    confidence = _optional_float(
        _read_value(
            d13_decision,
            "confidence",
            "confidence_score",
        )
    )

    strength = _optional_float(
        _read_value(
            d13_decision,
            "strength",
            "decision_strength",
        )
    )

    verdict = _read_value(
        d13_decision,
        "verdict",
        "decision",
        "action",
    )

    return DecisionReference(
        decision_id=str(decision_id) if decision_id is not None else None,
        direction=_normalize_direction(direction_value),
        raw_decision=d13_decision,
        confidence=confidence,
        strength=strength,
        verdict=str(verdict) if verdict is not None else None,
    )


def build_risk_reference(
    risk_result: Any,
) -> RiskReference:
    """
    Build a read-only Risk reference.
    """

    risk_id = _read_value(
        risk_result,
        "risk_id",
        "id",
        "event_id",
    )

    status = _read_value(
        risk_result,
        "status",
        "risk_status",
        "state",
        default="UNKNOWN",
    )

    risk_score = _optional_float(
        _read_value(
            risk_result,
            "risk_score",
            "score",
        )
    )

    exposure = _optional_float(
        _read_value(
            risk_result,
            "exposure",
            "exposure_value",
        )
    )

    severity = _read_value(
        risk_result,
        "severity",
        "risk_level",
    )

    return RiskReference(
        risk_id=str(risk_id) if risk_id is not None else None,
        status=str(status).upper(),
        raw_result=risk_result,
        risk_score=risk_score,
        exposure=exposure,
        severity=str(severity).upper() if severity is not None else None,
    )


def build_cas_reference(
    cas_result: Any,
) -> CASReference:
    """
    Build a read-only CAS reference.

    No authorization is created here.
    """

    cas_id = _read_value(
        cas_result,
        "cas_id",
        "id",
        "event_id",
    )

    status = _read_value(
        cas_result,
        "status",
        "cas_status",
        "state",
        default="UNKNOWN",
    )

    authorized = _read_value(
        cas_result,
        "authorized",
        "is_authorized",
        "execution_authorized",
    )

    reason = _read_value(
        cas_result,
        "reason",
        "message",
        "decision_reason",
    )

    return CASReference(
        cas_id=str(cas_id) if cas_id is not None else None,
        status=str(status).upper(),
        raw_result=cas_result,
        authorized=(
            bool(authorized)
            if authorized is not None
            else None
        ),
        reason=str(reason) if reason is not None else None,
    )


# ----------------------------------------------------------------------------
# Foundation contract validation
# ----------------------------------------------------------------------------

def validate_advanced_decision_request(
    request: AdvancedDecisionRequest,
) -> ContractValidationResult:
    """
    Validate the Part-1 request boundary.

    Fail-closed:
        Missing mandatory upstream authority => INVALID.
    """

    valid, errors = request.validate()

    if not valid:
        return ContractValidationResult(
            status=ContractValidationStatus.INVALID,
            errors=errors,
        )

    return ContractValidationResult(
        status=ContractValidationStatus.VALID,
        errors=(),
    )


__all__ = [
    "AdvancedDecisionStatus",
    "DecisionDisposition",
    "ReadinessLevel",
    "ContractValidationStatus",
    "AdvancedDecisionRequest",
    "DecisionReference",
    "RiskReference",
    "CASReference",
    "ContractValidationResult",
    "AdvancedDecisionResult",
    "validate_advanced_decision_request",
    "build_decision_reference",
    "build_risk_reference",
    "build_cas_reference",
]
# ============================================================================
# PART 2/5 — DECISION INTELLIGENCE
# ============================================================================

class DecisionIntelligenceState(str, Enum):
    """
    Semantic state of the upstream decision as interpreted by PLUS.

    This is an interpretation/refinement state, not a replacement decision.
    """

    DIRECTIONAL = "DIRECTIONAL"
    NEUTRAL = "NEUTRAL"
    HOLD = "HOLD"
    INSUFFICIENT = "INSUFFICIENT"


class DecisionConsistency(str, Enum):
    """
    Internal consistency assessment.

    This does not compare arbitrary values using raw equality.
    """

    CONSISTENT = "CONSISTENT"
    CONFLICTING = "CONFLICTING"
    INSUFFICIENT = "INSUFFICIENT"


class RefinementDisposition(str, Enum):
    """
    PLUS refinement disposition.

    REFINE means the authoritative decision remains usable but additional
    operational interpretation is required.

    PRESERVE means the upstream decision should remain semantically unchanged.

    WITHHOLD means PLUS cannot safely produce a stronger operational state.
    """

    PRESERVE = "PRESERVE"
    REFINE = "REFINE"
    WITHHOLD = "WITHHOLD"


@dataclass(frozen=True)
class DecisionIntelligence:
    """
    Part-2 semantic interpretation of D13.

    No new market direction is invented here.
    """

    state: DecisionIntelligenceState
    consistency: DecisionConsistency
    disposition: RefinementDisposition

    direction: DecisionDisposition

    confidence: Optional[float]
    strength: Optional[float]

    rationale: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    source: str = "ROBOMLM_PLUS"


# ----------------------------------------------------------------------------
# Semantic helpers
# ----------------------------------------------------------------------------

def _decision_intelligence_state(
    direction: DecisionDisposition,
) -> DecisionIntelligenceState:
    """
    Classify the semantic state of the existing D13 direction.
    """

    if direction in (
        DecisionDisposition.UP,
        DecisionDisposition.DOWN,
    ):
        return DecisionIntelligenceState.DIRECTIONAL

    if direction == DecisionDisposition.NEUTRAL:
        return DecisionIntelligenceState.NEUTRAL

    if direction == DecisionDisposition.HOLD:
        return DecisionIntelligenceState.HOLD

    return DecisionIntelligenceState.INSUFFICIENT


def _semantic_status(value: Any) -> str:
    """
    Normalize an upstream status without assigning intelligence to it.
    """

    if value is None:
        return ""

    return str(value).strip().upper()


def _risk_is_conflicting(
    risk: RiskReference,
) -> bool:
    """
    Detect explicit negative risk states.

    Only explicit status/severity vocabulary is considered.

    No arbitrary numeric threshold is invented here.
    """

    status = _semantic_status(risk.status)
    severity = _semantic_status(risk.severity)

    blocking_values = {
        "BLOCKED",
        "REJECTED",
        "FAILED",
        "INVALID",
        "UNSAFE",
        "CRITICAL",
    }

    return (
        status in blocking_values
        or severity in blocking_values
    )


def _cas_is_conflicting(
    cas: CASReference,
) -> bool:
    """
    Detect an explicit CAS rejection/block.

    CAS remains authoritative.
    """

    status = _semantic_status(cas.status)

    blocking_values = {
        "BLOCKED",
        "REJECTED",
        "DENIED",
        "FAILED",
        "INVALID",
        "UNAUTHORIZED",
    }

    if status in blocking_values:
        return True

    if cas.authorized is False:
        return True

    return False


# ----------------------------------------------------------------------------
# Decision ↔ Risk semantic evaluation
# ----------------------------------------------------------------------------

def evaluate_decision_risk_consistency(
    decision: DecisionReference,
    risk: RiskReference,
) -> DecisionConsistency:
    """
    Evaluate whether Risk explicitly invalidates the upstream decision.

    Important:
        Risk does not create a new market direction.

        A risk state can make a decision operationally unusable, but it
        cannot silently transform UP into DOWN or DOWN into UP.
    """

    if decision.direction == DecisionDisposition.UNKNOWN:
        return DecisionConsistency.INSUFFICIENT

    if _risk_is_conflicting(risk):
        return DecisionConsistency.CONFLICTING

    if not risk.status:
        return DecisionConsistency.INSUFFICIENT

    return DecisionConsistency.CONSISTENT


# ----------------------------------------------------------------------------
# Decision ↔ CAS semantic evaluation
# ----------------------------------------------------------------------------

def evaluate_decision_cas_consistency(
    decision: DecisionReference,
    cas: CASReference,
) -> DecisionConsistency:
    """
    Evaluate CAS compatibility with the existing decision.

    CAS authorization is an operational gate.

    It does not validate whether the market direction itself is correct.
    """

    if decision.direction == DecisionDisposition.UNKNOWN:
        return DecisionConsistency.INSUFFICIENT

    if _cas_is_conflicting(cas):
        return DecisionConsistency.CONFLICTING

    if cas.authorized is None and not cas.status:
        return DecisionConsistency.INSUFFICIENT

    return DecisionConsistency.CONSISTENT


# ----------------------------------------------------------------------------
# Combined decision intelligence
# ----------------------------------------------------------------------------

def build_decision_intelligence(
    decision: DecisionReference,
    risk: RiskReference,
    cas: CASReference,
) -> DecisionIntelligence:
    """
    Construct the Part-2 intelligence interpretation.

    Priority:
        1. Preserve D13 direction.
        2. Detect explicit conflicts.
        3. Never invent a replacement direction.
        4. Produce a refinement disposition.
    """

    state = _decision_intelligence_state(decision.direction)

    risk_consistency = evaluate_decision_risk_consistency(
        decision,
        risk,
    )

    cas_consistency = evaluate_decision_cas_consistency(
        decision,
        cas,
    )

    rationale: list[str] = []
    warnings: list[str] = []

    # ------------------------------------------------------------------
    # Unknown D13 direction
    # ------------------------------------------------------------------

    if state == DecisionIntelligenceState.INSUFFICIENT:
        rationale.append(
            "D13 direction is not semantically sufficient for PLUS refinement."
        )

        return DecisionIntelligence(
            state=state,
            consistency=DecisionConsistency.INSUFFICIENT,
            disposition=RefinementDisposition.WITHHOLD,
            direction=DecisionDisposition.UNKNOWN,
            confidence=decision.confidence,
            strength=decision.strength,
            rationale=tuple(rationale),
            warnings=(
                "PLUS did not infer a replacement market direction.",
            ),
        )

    # ------------------------------------------------------------------
    # Explicit Risk conflict
    # ------------------------------------------------------------------

    if risk_consistency == DecisionConsistency.CONFLICTING:
        warnings.append(
            "Upstream Risk state conflicts with operational use of the decision."
        )

    # ------------------------------------------------------------------
    # Explicit CAS conflict
    # ------------------------------------------------------------------

    if cas_consistency == DecisionConsistency.CONFLICTING:
        warnings.append(
            "CAS does not authorize the current decision for operational use."
        )

    # ------------------------------------------------------------------
    # Determine combined semantic consistency
    # ------------------------------------------------------------------

    consistencies = (
        risk_consistency,
        cas_consistency,
    )

    if DecisionConsistency.CONFLICTING in consistencies:
        combined_consistency = DecisionConsistency.CONFLICTING
        disposition = RefinementDisposition.WITHHOLD

        rationale.append(
            "Authoritative upstream decision is preserved, "
            "but PLUS withholds stronger operational refinement."
        )

    elif DecisionConsistency.INSUFFICIENT in consistencies:
        combined_consistency = DecisionConsistency.INSUFFICIENT
        disposition = RefinementDisposition.REFINE

        rationale.append(
            "Decision direction exists, but supporting operational "
            "context is incomplete."
        )

    else:
        combined_consistency = DecisionConsistency.CONSISTENT
        disposition = RefinementDisposition.PRESERVE

        rationale.append(
            "D13 direction remains semantically usable without "
            "introducing a replacement decision."
        )

    # ------------------------------------------------------------------
    # Directional explanation
    # ------------------------------------------------------------------

    if decision.direction == DecisionDisposition.UP:
        rationale.append(
            "Existing D13 directional family is UP."
        )

    elif decision.direction == DecisionDisposition.DOWN:
        rationale.append(
            "Existing D13 directional family is DOWN."
        )

    elif decision.direction == DecisionDisposition.NEUTRAL:
        rationale.append(
            "Existing D13 state is NEUTRAL; PLUS does not manufacture direction."
        )

    elif decision.direction == DecisionDisposition.HOLD:
        rationale.append(
            "Existing D13 state is HOLD; PLUS preserves the non-directional state."
        )

    # ------------------------------------------------------------------
    # Confidence / strength are references, not fabricated scores
    # ------------------------------------------------------------------

    if decision.confidence is None:
        warnings.append(
            "D13 confidence is unavailable; PLUS does not synthesize confidence."
        )

    if decision.strength is None:
        warnings.append(
            "D13 strength is unavailable; PLUS does not synthesize strength."
        )

    return DecisionIntelligence(
        state=state,
        consistency=combined_consistency,
        disposition=disposition,
        direction=decision.direction,
        confidence=decision.confidence,
        strength=decision.strength,
        rationale=tuple(rationale),
        warnings=tuple(warnings),
    )


# ----------------------------------------------------------------------------
# Part-2 refinement application
# ----------------------------------------------------------------------------

def apply_decision_intelligence(
    result: AdvancedDecisionResult,
    intelligence: DecisionIntelligence,
) -> AdvancedDecisionResult:
    """
    Attach Part-2 intelligence to the stable result envelope.

    The fundamental result contract remains intact.

    This function does not mutate the frozen result.
    """

    trace = dict(result.trace)

    trace["decision_intelligence"] = {
        "state": intelligence.state.value,
        "consistency": intelligence.consistency.value,
        "disposition": intelligence.disposition.value,
        "direction": intelligence.direction.value,
        "confidence": intelligence.confidence,
        "strength": intelligence.strength,
        "source": intelligence.source,
    }

    status = result.status
    readiness = result.readiness

    if intelligence.disposition == RefinementDisposition.WITHHOLD:
        status = AdvancedDecisionStatus.CONDITIONAL
        readiness = ReadinessLevel.NOT_READY

    elif intelligence.disposition == RefinementDisposition.REFINE:
        status = AdvancedDecisionStatus.REFINED
        readiness = ReadinessLevel.ANALYSIS_READY

    elif intelligence.disposition == RefinementDisposition.PRESERVE:
        status = AdvancedDecisionStatus.REFINED
        readiness = ReadinessLevel.DECISION_READY

    combined_rationale = tuple(
        dict.fromkeys(
            (
                *result.rationale,
                *intelligence.rationale,
            )
        )
    )

    combined_warnings = tuple(
        dict.fromkeys(
            (
                *result.warnings,
                *intelligence.warnings,
            )
        )
    )

    return AdvancedDecisionResult(
        request_id=result.request_id,
        result_id=result.result_id,
        status=status,
        readiness=readiness,
        decision=result.decision,
        risk=result.risk,
        cas=result.cas,
        contract_validation=result.contract_validation,
        rationale=combined_rationale,
        warnings=combined_warnings,
        trace=trace,
        created_at=result.created_at,
    )
# ============================================================
# ROBOMLM PLUS — ADVANCED DECISION ENGINE
# Part 3/5 — Risk + CAS Aware Advanced Decision Integration
# ============================================================

@dataclass(frozen=True)
class RiskCASAssessment:
    """
    Normalized operational assessment of Risk + CAS.

    IMPORTANT:
    - This class does NOT replace Risk Engine authority.
    - This class does NOT replace CAS authority.
    - It does NOT calculate a new risk score.
    - It does NOT create execution authorization.
    """

    risk_consistency: DecisionConsistency
    cas_consistency: DecisionConsistency

    risk_status: str
    cas_status: str

    risk_blocking: bool
    cas_blocking: bool

    cas_authorized: Optional[bool]

    operational_state: str
    rationale: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class AdvancedOperationalAssessment:
    """
    Combined Advanced Decision operational assessment.

    This is a refinement layer above D13 + Risk + CAS.
    It does not become a new decision authority.
    """

    decision_intelligence: DecisionIntelligence
    risk_cas: RiskCASAssessment

    final_disposition: RefinementDisposition
    readiness: ReadinessLevel

    direction_preserved: bool
    execution_permission_preserved: bool

    rationale: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


def _safe_status(value: Any, default: str = "UNKNOWN") -> str:
    """
    Normalize status-like values without assigning intelligence meaning.
    """
    if value is None:
        return default

    text = str(value).strip().upper()

    if not text:
        return default

    return text


def _extract_optional_bool(
    source: Any,
    *names: str,
) -> Optional[bool]:
    """
    Extract a boolean without coercing arbitrary values.

    Only explicit boolean values and recognized boolean strings
    are accepted. Numeric values are intentionally NOT interpreted
    as authorization/state.
    """
    value = _read_value(source, *names, default=None)

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        normalized = value.strip().upper()

        if normalized in {
            "TRUE",
            "YES",
            "Y",
            "AUTHORIZED",
            "ALLOWED",
            "APPROVED",
        }:
            return True

        if normalized in {
            "FALSE",
            "NO",
            "N",
            "UNAUTHORIZED",
            "DENIED",
            "REJECTED",
            "BLOCKED",
        }:
            return False

    return None


def _risk_has_explicit_block(
    risk: RiskReference,
) -> bool:
    """
    Detect explicit Risk-layer blocking states.

    No numeric threshold is introduced here.
    """
    return _risk_is_conflicting(risk)


def _cas_has_explicit_block(
    cas: CASReference,
) -> bool:
    """
    Detect explicit CAS blocking states.

    CAS remains the authorization authority.
    """
    return _cas_is_conflicting(cas)


def assess_risk_and_cas(
    decision: DecisionReference,
    risk: RiskReference,
    cas: CASReference,
) -> RiskCASAssessment:
    """
    Build a normalized Risk + CAS operational assessment.

    Architecture:
        D13 Decision
             ↓
        Risk Assessment
             ↓
        CAS Authorization
             ↓
        ROBOMLM PLUS refinement

    ROBOMLM PLUS can refine readiness/disposition,
    but cannot create or override authority.
    """

    risk_consistency = evaluate_decision_risk_consistency(
        decision,
        risk,
    )

    cas_consistency = evaluate_decision_cas_consistency(
        decision,
        cas,
    )

    risk_blocking = _risk_has_explicit_block(risk)
    cas_blocking = _cas_has_explicit_block(cas)

    rationale: list[str] = []
    warnings: list[str] = []

    # --------------------------------------------------------
    # Risk assessment
    # --------------------------------------------------------

    if risk_blocking:
        rationale.append(
            "Risk layer contains an explicit blocking state."
        )

    elif risk_consistency is DecisionConsistency.INSUFFICIENT:
        warnings.append(
            "Risk context is insufficient for stronger operational refinement."
        )

    else:
        rationale.append(
            "Risk layer does not expose an explicit blocking state."
        )

    # --------------------------------------------------------
    # CAS assessment
    # --------------------------------------------------------

    if cas_blocking:
        rationale.append(
            "CAS contains an explicit operational authorization conflict."
        )

    elif cas_consistency is DecisionConsistency.INSUFFICIENT:
        warnings.append(
            "CAS context is insufficient for stronger authorization-aware refinement."
        )

    else:
        rationale.append(
            "CAS context is operationally consistent with the supplied decision."
        )

    # --------------------------------------------------------
    # Operational state
    # --------------------------------------------------------

    if risk_blocking or cas_blocking:
        operational_state = "BLOCKED"

    elif (
        risk_consistency is DecisionConsistency.INSUFFICIENT
        or cas_consistency is DecisionConsistency.INSUFFICIENT
    ):
        operational_state = "INCOMPLETE"

    else:
        operational_state = "CLEAR"

    # --------------------------------------------------------
    # Authorization preservation
    # --------------------------------------------------------

    cas_authorized = _extract_optional_bool(
        cas.raw_result,
        "authorized",
        "is_authorized",
        "execution_authorized",
        "permission_granted",
    )

    return RiskCASAssessment(
        risk_consistency=risk_consistency,
        cas_consistency=cas_consistency,
        risk_status=_safe_status(risk.status),
        cas_status=_safe_status(cas.status),
        risk_blocking=risk_blocking,
        cas_blocking=cas_blocking,
        cas_authorized=cas_authorized,
        operational_state=operational_state,
        rationale=tuple(rationale),
        warnings=tuple(warnings),
    )


def build_advanced_operational_assessment(
    decision_intelligence: DecisionIntelligence,
    risk_cas: RiskCASAssessment,
) -> AdvancedOperationalAssessment:
    """
    Combine Decision Intelligence with Risk + CAS state.

    Rules:
    1. Never change D13 direction.
    2. Never synthesize a new direction.
    3. Never override Risk.
    4. Never override CAS.
    5. Explicit blocking state => WITHHOLD.
    6. Missing supporting authority => REFINE.
    7. Clear supporting state => preserve D13 decision.
    """

    rationale = list(decision_intelligence.rationale)
    warnings = list(decision_intelligence.warnings)

    rationale.extend(risk_cas.rationale)
    warnings.extend(risk_cas.warnings)

    direction_preserved = (
        decision_intelligence.direction
        in {
            DecisionDisposition.UP,
            DecisionDisposition.DOWN,
            DecisionDisposition.NEUTRAL,
            DecisionDisposition.HOLD,
        }
    )

    # --------------------------------------------------------
    # Hard operational block
    # --------------------------------------------------------

    if (
        risk_cas.risk_blocking
        or risk_cas.cas_blocking
        or decision_intelligence.disposition
        is RefinementDisposition.WITHHOLD
    ):
        final_disposition = RefinementDisposition.WITHHOLD
        readiness = ReadinessLevel.NOT_READY

        rationale.append(
            "Advanced Decision preserves upstream authority but withholds "
            "stronger operational refinement because an authority layer "
            "contains a blocking condition."
        )

    # --------------------------------------------------------
    # Incomplete authority/context
    # --------------------------------------------------------

    elif (
        risk_cas.risk_consistency is DecisionConsistency.INSUFFICIENT
        or risk_cas.cas_consistency is DecisionConsistency.INSUFFICIENT
        or decision_intelligence.disposition
        is RefinementDisposition.REFINE
    ):
        final_disposition = RefinementDisposition.REFINE
        readiness = ReadinessLevel.ANALYSIS_READY

        rationale.append(
            "Advanced Decision remains refinement-capable, but supporting "
            "authority/context is incomplete."
        )

    # --------------------------------------------------------
    # Fully consistent upstream state
    # --------------------------------------------------------

    else:
        final_disposition = RefinementDisposition.PRESERVE

        if risk_cas.cas_authorized is True:
            readiness = ReadinessLevel.EXECUTION_PREPARATION_READY

            rationale.append(
                "Upstream Decision, Risk and CAS context are consistent; "
                "CAS authorization is preserved as supplied."
            )

        else:
            readiness = ReadinessLevel.DECISION_READY

            rationale.append(
                "Upstream Decision, Risk and CAS context are consistent; "
                "execution authorization is not independently granted."
            )

    # --------------------------------------------------------
    # Explicit protection against authority mutation
    # --------------------------------------------------------

    if decision_intelligence.direction is DecisionDisposition.UNKNOWN:
        direction_preserved = False
        final_disposition = RefinementDisposition.WITHHOLD
        readiness = ReadinessLevel.NOT_READY

        warnings.append(
            "D13 direction is unavailable; ROBOMLM PLUS will not synthesize "
            "a replacement direction."
        )

    execution_permission_preserved = True

    return AdvancedOperationalAssessment(
        decision_intelligence=decision_intelligence,
        risk_cas=risk_cas,
        final_disposition=final_disposition,
        readiness=readiness,
        direction_preserved=direction_preserved,
        execution_permission_preserved=execution_permission_preserved,
        rationale=tuple(dict.fromkeys(rationale)),
        warnings=tuple(dict.fromkeys(warnings)),
    )


def apply_operational_assessment(
    result: AdvancedDecisionResult,
    assessment: AdvancedOperationalAssessment,
) -> AdvancedDecisionResult:
    """
    Attach the Risk + CAS-aware operational assessment to the
    Advanced Decision result.

    No upstream authority is mutated.
    """

    trace = dict(result.trace)

    trace["operational_assessment"] = {
        "final_disposition": assessment.final_disposition.value,
        "readiness": assessment.readiness.value,
        "direction_preserved": assessment.direction_preserved,
        "execution_permission_preserved": (
            assessment.execution_permission_preserved
        ),
        "risk_cas": {
            "risk_consistency": assessment.risk_cas.risk_consistency.value,
            "cas_consistency": assessment.risk_cas.cas_consistency.value,
            "risk_status": assessment.risk_cas.risk_status,
            "cas_status": assessment.risk_cas.cas_status,
            "risk_blocking": assessment.risk_cas.risk_blocking,
            "cas_blocking": assessment.risk_cas.cas_blocking,
            "cas_authorized": assessment.risk_cas.cas_authorized,
            "operational_state": assessment.risk_cas.operational_state,
        },
    }

    # --------------------------------------------------------
    # Map refinement into public Advanced Decision state
    # --------------------------------------------------------

    if assessment.final_disposition is RefinementDisposition.WITHHOLD:
        status = AdvancedDecisionStatus.BLOCKED

    elif assessment.final_disposition is RefinementDisposition.REFINE:
        status = AdvancedDecisionStatus.CONDITIONAL

    else:
        status = AdvancedDecisionStatus.REFINED

    return AdvancedDecisionResult(
        request_id=result.request_id,
        result_id=result.result_id,
        status=status,
        readiness=assessment.readiness,
        decision=result.decision,
        risk=result.risk,
        cas=result.cas,
        contract_validation=result.contract_validation,
        rationale=tuple(
            dict.fromkeys(
                list(result.rationale)
                + list(assessment.rationale)
            )
        ),
        warnings=tuple(
            dict.fromkeys(
                list(result.warnings)
                + list(assessment.warnings)
            )
        ),
        trace=trace,
        created_at=result.created_at,
    )


# ============================================================
# END OF PART 3/5
# ============================================================
# ============================================================
# ROBOMLM PLUS — ADVANCED DECISION ENGINE
# Part 4/5 — Advanced Decision Engine Orchestration
# ============================================================


class AdvancedDecisionEngine:
    """
    ROBOMLM PLUS Advanced Decision Engine.

    Architectural position:

        D13 Decision Authority
                 │
                 ▼
        Advanced Decision Request
                 │
                 ├── Contract Validation
                 │
                 ├── Decision Reference
                 │
                 ├── Risk Reference
                 │
                 ├── CAS Reference
                 │
                 ▼
        Decision Intelligence
                 │
                 ▼
        Risk + CAS Assessment
                 │
                 ▼
        Advanced Operational Assessment
                 │
                 ▼
        AdvancedDecisionResult

    IMPORTANT:
    - D13 remains the decision authority.
    - Risk remains the risk authority.
    - CAS remains the authorization authority.
    - PLUS performs refinement, consistency analysis,
      readiness determination and operational orchestration.
    - PLUS does not invent market direction.
    - PLUS does not recalculate D13.
    - PLUS does not replace Risk.
    - PLUS does not bypass CAS.
    """

    ENGINE_NAME = "ROBOMLM_PLUS_ADVANCED_DECISION"
    ENGINE_VERSION = "1.0"

    def __init__(self) -> None:
        self.engine_name = self.ENGINE_NAME
        self.engine_version = self.ENGINE_VERSION

    # --------------------------------------------------------
    # Contract stage
    # --------------------------------------------------------

    def validate_request(
        self,
        request: AdvancedDecisionRequest,
    ) -> ContractValidationResult:
        """
        Validate the external request before any intelligence
        processing begins.
        """

        if not isinstance(request, AdvancedDecisionRequest):
            return ContractValidationResult(
                status=ContractValidationStatus.INVALID,
                errors=(
                    "request must be an AdvancedDecisionRequest",
                ),
            )

        return validate_advanced_decision_request(request)

    # --------------------------------------------------------
    # Reference construction stage
    # --------------------------------------------------------

    def build_references(
        self,
        request: AdvancedDecisionRequest,
    ) -> tuple[
        DecisionReference,
        RiskReference,
        CASReference,
    ]:
        """
        Convert upstream objects into stable internal references.

        Raw upstream objects remain untouched.
        """

        decision = build_decision_reference(
            request.d13_decision
        )

        risk = build_risk_reference(
            request.risk_result
        )

        cas = build_cas_reference(
            request.cas_result
        )

        return decision, risk, cas

    # --------------------------------------------------------
    # Invalid-result construction
    # --------------------------------------------------------

    def _invalid_result(
        self,
        request: AdvancedDecisionRequest,
        validation: ContractValidationResult,
    ) -> AdvancedDecisionResult:
        """
        Fail closed when the request contract is invalid.

        No partial intelligence result is presented as valid.
        """

        decision = DecisionReference(
            decision_id="INVALID",
            direction=DecisionDisposition.UNKNOWN.value,
            raw_decision=None,
            confidence=None,
            strength=None,
            verdict="INVALID",
        )

        risk = RiskReference(
            risk_id="INVALID",
            status="INVALID",
            raw_result=None,
            risk_score=None,
            exposure=None,
            severity="INVALID",
        )

        cas = CASReference(
            cas_id="INVALID",
            status="INVALID",
            raw_result=None,
            authorized=False,
            reason="Invalid Advanced Decision request",
        )

        trace = {
            "engine": self.engine_name,
            "engine_version": self.engine_version,
            "stage": "CONTRACT_VALIDATION",
            "contract_status": validation.status.value,
            "contract_errors": validation.errors,
        }

        return AdvancedDecisionResult(
            request_id=request.request_id,
            result_id=str(uuid4()),
            status=AdvancedDecisionStatus.INVALID,
            readiness=ReadinessLevel.NOT_READY,
            decision=decision,
            risk=risk,
            cas=cas,
            contract_validation=validation,
            rationale=(
                "Advanced Decision request failed contract validation.",
            ),
            warnings=validation.errors,
            trace=trace,
            created_at=datetime.now(timezone.utc),
        )

    # --------------------------------------------------------
    # Main processing pipeline
    # --------------------------------------------------------

    def process(
        self,
        request: AdvancedDecisionRequest,
    ) -> AdvancedDecisionResult:
        """
        Execute the complete Advanced Decision pipeline.

        Processing order is intentionally explicit so that
        authority boundaries remain auditable.
        """

        validation = self.validate_request(request)

        if not validation.is_valid:
            return self._invalid_result(
                request,
                validation,
            )

        # ----------------------------------------------------
        # Stage 1 — Normalize upstream authority references
        # ----------------------------------------------------

        decision, risk, cas = self.build_references(request)

        # ----------------------------------------------------
        # Stage 2 — Decision Intelligence
        # ----------------------------------------------------

        decision_intelligence = build_decision_intelligence(
            decision=decision,
            risk=risk,
            cas=cas,
        )

        # ----------------------------------------------------
        # Stage 3 — Create initial result envelope
        # ----------------------------------------------------

        initial_trace = {
            "engine": self.engine_name,
            "engine_version": self.engine_version,
            "pipeline": (
                "CONTRACT"
                "->REFERENCES"
                "->DECISION_INTELLIGENCE"
                "->RISK_CAS"
                "->OPERATIONAL_ASSESSMENT"
            ),
            "authority": {
                "decision": "D13",
                "risk": "RISK",
                "authorization": "CAS",
                "refinement": "ROBOMLM_PLUS",
            },
            "request": {
                "request_id": request.request_id,
                "timestamp": request.timestamp.isoformat(),
            },
            "upstream": {
                "decision_id": decision.decision_id,
                "risk_id": risk.risk_id,
                "cas_id": cas.cas_id,
            },
        }

        result = AdvancedDecisionResult(
            request_id=request.request_id,
            result_id=str(uuid4()),
            status=AdvancedDecisionStatus.READY,
            readiness=ReadinessLevel.ANALYSIS_READY,
            decision=decision,
            risk=risk,
            cas=cas,
            contract_validation=validation,
            rationale=(),
            warnings=(),
            trace=initial_trace,
            created_at=datetime.now(timezone.utc),
        )

        # ----------------------------------------------------
        # Stage 4 — Apply Decision Intelligence
        # ----------------------------------------------------

        result = apply_decision_intelligence(
            result=result,
            intelligence=decision_intelligence,
        )

        # ----------------------------------------------------
        # Stage 5 — Risk + CAS assessment
        # ----------------------------------------------------

        risk_cas = assess_risk_and_cas(
            decision=decision,
            risk=risk,
            cas=cas,
        )

        # ----------------------------------------------------
        # Stage 6 — Advanced operational assessment
        # ----------------------------------------------------

        operational_assessment = (
            build_advanced_operational_assessment(
                decision_intelligence=decision_intelligence,
                risk_cas=risk_cas,
            )
        )

        # ----------------------------------------------------
        # Stage 7 — Apply final assessment
        # ----------------------------------------------------

        result = apply_operational_assessment(
            result=result,
            assessment=operational_assessment,
        )

        # ----------------------------------------------------
        # Stage 8 — Final trace integrity
        # ----------------------------------------------------

        trace = dict(result.trace)

        trace["final_state"] = {
            "status": result.status.value,
            "readiness": result.readiness.value,
            "decision_direction": result.decision.direction,
            "risk_status": result.risk.status,
            "cas_status": result.cas.status,
        }

        trace["authority_integrity"] = {
            "d13_preserved": True,
            "risk_preserved": True,
            "cas_preserved": True,
            "plus_is_refinement_layer": True,
            "direction_synthesized": False,
            "authorization_synthesized": False,
        }

        return AdvancedDecisionResult(
            request_id=result.request_id,
            result_id=result.result_id,
            status=result.status,
            readiness=result.readiness,
            decision=result.decision,
            risk=result.risk,
            cas=result.cas,
            contract_validation=result.contract_validation,
            rationale=result.rationale,
            warnings=result.warnings,
            trace=trace,
            created_at=result.created_at,
        )

    # --------------------------------------------------------
    # Convenience execution method
    # --------------------------------------------------------

    def evaluate(
        self,
        request: AdvancedDecisionRequest,
    ) -> AdvancedDecisionResult:
        """
        Public semantic alias for process().

        Keeps external callers independent from the internal
        pipeline naming.
        """

        return self.process(request)

    # --------------------------------------------------------
    # Readiness helper
    # --------------------------------------------------------

    @staticmethod
    def is_operationally_ready(
        result: AdvancedDecisionResult,
    ) -> bool:
        """
        Determine whether the result reached an operationally
        meaningful readiness state.

        This does NOT mean an order may be executed.

        Execution permission remains governed by CAS and the
        downstream execution architecture.
        """

        return result.readiness in {
            ReadinessLevel.DECISION_READY,
            ReadinessLevel.EXECUTION_PREPARATION_READY,
        }

    # --------------------------------------------------------
    # Execution-preparation gate
    # --------------------------------------------------------

    @staticmethod
    def is_execution_preparation_ready(
        result: AdvancedDecisionResult,
    ) -> bool:
        """
        Narrow gate for the next ROBOMLM PLUS layer.

        Only the readiness state is evaluated here.

        This method does NOT:
        - create an order
        - create AuthorizedAction
        - bypass CAS
        - approve execution
        """

        if not result.is_valid:
            return False

        if result.status in {
            AdvancedDecisionStatus.INVALID,
            AdvancedDecisionStatus.BLOCKED,
        }:
            return False

        return (
            result.readiness
            is ReadinessLevel.EXECUTION_PREPARATION_READY
        )

    # --------------------------------------------------------
    # Audit / trace helper
    # --------------------------------------------------------

    @staticmethod
    def audit_summary(
        result: AdvancedDecisionResult,
    ) -> dict[str, Any]:
        """
        Produce a compact audit representation without exposing
        arbitrary raw upstream objects.
        """

        return {
            "request_id": result.request_id,
            "result_id": result.result_id,
            "status": result.status.value,
            "readiness": result.readiness.value,
            "decision": {
                "decision_id": result.decision.decision_id,
                "direction": result.decision.direction,
                "confidence": result.decision.confidence,
                "strength": result.decision.strength,
                "source": result.decision.source,
            },
            "risk": {
                "risk_id": result.risk.risk_id,
                "status": result.risk.status,
                "risk_score": result.risk.risk_score,
                "severity": result.risk.severity,
                "source": result.risk.source,
            },
            "cas": {
                "cas_id": result.cas.cas_id,
                "status": result.cas.status,
                "authorized": result.cas.authorized,
                "source": result.cas.source,
            },
            "execution_preparation_ready": (
                AdvancedDecisionEngine
                .is_execution_preparation_ready(result)
            ),
            "authority_integrity": {
                "d13_preserved": True,
                "risk_preserved": True,
                "cas_preserved": True,
            },
        }


# ============================================================
# END OF PART 4/5
# ============================================================
# ============================================================
# ROBOMLM PLUS — ADVANCED DECISION ENGINE
# Part 5/5 — Public API + Validation + Integrity + Exports
# ============================================================


def create_advanced_decision_request(
    d13_decision: Any,
    risk_result: Any,
    cas_result: Any,
    market_context: Optional[Any] = None,
    evidence: Optional[Any] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> AdvancedDecisionRequest:
    """
    Public request factory.

    Keeps request construction consistent for application,
    service and future API layers.
    """

    return AdvancedDecisionRequest(
        d13_decision=d13_decision,
        risk_result=risk_result,
        cas_result=cas_result,
        market_context=market_context,
        evidence=evidence,
        metadata=dict(metadata or {}),
    )


def run_advanced_decision(
    d13_decision: Any,
    risk_result: Any,
    cas_result: Any,
    market_context: Optional[Any] = None,
    evidence: Optional[Any] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> AdvancedDecisionResult:
    """
    Primary public function for Advanced Decision evaluation.

    Architecture remains:

        D13
         ↓
        Risk
         ↓
        CAS
         ↓
        ROBOMLM PLUS Advanced Decision
    """

    request = create_advanced_decision_request(
        d13_decision=d13_decision,
        risk_result=risk_result,
        cas_result=cas_result,
        market_context=market_context,
        evidence=evidence,
        metadata=metadata,
    )

    engine = AdvancedDecisionEngine()

    return engine.evaluate(request)


def validate_advanced_decision_result(
    result: AdvancedDecisionResult,
) -> tuple[bool, tuple[str, ...]]:
    """
    Validate the structural integrity of a completed result.

    This is a contract/integrity check only.
    It does not re-evaluate market intelligence.
    """

    errors: list[str] = []

    if not isinstance(result, AdvancedDecisionResult):
        return (
            False,
            ("result must be an AdvancedDecisionResult",),
        )

    if not result.request_id:
        errors.append("missing request_id")

    if not result.result_id:
        errors.append("missing result_id")

    if not isinstance(
        result.decision,
        DecisionReference,
    ):
        errors.append(
            "decision reference is invalid"
        )

    if not isinstance(
        result.risk,
        RiskReference,
    ):
        errors.append(
            "risk reference is invalid"
        )

    if not isinstance(
        result.cas,
        CASReference,
    ):
        errors.append(
            "CAS reference is invalid"
        )

    if not isinstance(
        result.contract_validation,
        ContractValidationResult,
    ):
        errors.append(
            "contract validation object is invalid"
        )

    if not isinstance(result.trace, Mapping):
        errors.append("trace must be a Mapping")

    # --------------------------------------------------------
    # Authority integrity checks
    # --------------------------------------------------------

    if result.decision.source != "D13":
        errors.append(
            "decision authority must remain D13"
        )

    if result.risk.source != "RISK":
        errors.append(
            "risk authority must remain RISK"
        )

    if result.cas.source != "CAS":
        errors.append(
            "authorization authority must remain CAS"
        )

    # --------------------------------------------------------
    # Direction integrity
    # --------------------------------------------------------

    valid_directions = {
        DecisionDisposition.UP.value,
        DecisionDisposition.DOWN.value,
        DecisionDisposition.NEUTRAL.value,
        DecisionDisposition.HOLD.value,
        DecisionDisposition.UNKNOWN.value,
    }

    if result.decision.direction not in valid_directions:
        errors.append(
            "decision direction contains unsupported semantic value"
        )

    return (
        len(errors) == 0,
        tuple(errors),
    )


def advanced_decision_health_check() -> dict[str, Any]:
    """
    Static engine health/self-check.

    This verifies implementation-level integrity only.

    It intentionally does not fabricate market inputs or execute
    a synthetic trading decision.
    """

    checks: dict[str, bool] = {
        "engine_class_available": (
            AdvancedDecisionEngine is not None
        ),
        "request_contract_available": (
            AdvancedDecisionRequest is not None
        ),
        "decision_reference_available": (
            DecisionReference is not None
        ),
        "risk_reference_available": (
            RiskReference is not None
        ),
        "cas_reference_available": (
            CASReference is not None
        ),
        "decision_intelligence_available": (
            DecisionIntelligence is not None
        ),
        "risk_cas_assessment_available": (
            RiskCASAssessment is not None
        ),
        "operational_assessment_available": (
            AdvancedOperationalAssessment is not None
        ),
    }

    checks["all_core_components_available"] = all(
        checks.values()
    )

    return {
        "engine": AdvancedDecisionEngine.ENGINE_NAME,
        "version": AdvancedDecisionEngine.ENGINE_VERSION,
        "status": (
            "PASS"
            if checks["all_core_components_available"]
            else "FAIL"
        ),
        "checks": checks,
        "authority_model": {
            "decision": "D13",
            "risk": "RISK",
            "authorization": "CAS",
            "refinement": "ROBOMLM_PLUS",
        },
        "execution_authorization_created_here": False,
        "d13_recalculated_here": False,
        "synthetic_direction_created_here": False,
    }


def advanced_decision_to_dict(
    result: AdvancedDecisionResult,
) -> dict[str, Any]:
    """
    Stable public serialization boundary.

    Raw upstream objects are intentionally excluded.
    """

    valid, errors = validate_advanced_decision_result(
        result
    )

    payload = result.to_dict()

    payload["validation"] = {
        "valid": valid,
        "errors": errors,
    }

    payload["engine"] = {
        "name": AdvancedDecisionEngine.ENGINE_NAME,
        "version": AdvancedDecisionEngine.ENGINE_VERSION,
    }

    return payload


def get_advanced_decision_engine_info() -> dict[str, Any]:
    """
    Public metadata endpoint for application/API layers.
    """

    return {
        "name": AdvancedDecisionEngine.ENGINE_NAME,
        "version": AdvancedDecisionEngine.ENGINE_VERSION,
        "layer": "ROBOMLM_PLUS",
        "role": "ADVANCED_DECISION_REFINEMENT",
        "decision_authority": "D13",
        "risk_authority": "RISK",
        "authorization_authority": "CAS",
        "creates_execution_order": False,
        "creates_authorized_action": False,
        "recalculates_d13": False,
        "generates_new_direction": False,
    }


# ============================================================
# Public API aliases
# ============================================================

AdvancedDecision = AdvancedDecisionEngine


__all__ = [
    # --------------------------------------------------------
    # Enums
    # --------------------------------------------------------
    "AdvancedDecisionStatus",
    "DecisionDisposition",
    "ReadinessLevel",
    "ContractValidationStatus",
    "DecisionIntelligenceState",
    "DecisionConsistency",
    "RefinementDisposition",

    # --------------------------------------------------------
    # Contracts
    # --------------------------------------------------------
    "AdvancedDecisionRequest",
    "DecisionReference",
    "RiskReference",
    "CASReference",
    "ContractValidationResult",
    "AdvancedDecisionResult",

    # --------------------------------------------------------
    # Intelligence structures
    # --------------------------------------------------------
    "DecisionIntelligence",
    "RiskCASAssessment",
    "AdvancedOperationalAssessment",

    # --------------------------------------------------------
    # Engine
    # --------------------------------------------------------
    "AdvancedDecisionEngine",
    "AdvancedDecision",

    # --------------------------------------------------------
    # Request / processing API
    # --------------------------------------------------------
    "create_advanced_decision_request",
    "run_advanced_decision",

    # --------------------------------------------------------
    # Validation / serialization
    # --------------------------------------------------------
    "validate_advanced_decision_request",
    "validate_advanced_decision_result",
    "advanced_decision_to_dict",

    # --------------------------------------------------------
    # Intelligence functions
    # --------------------------------------------------------
    "evaluate_decision_risk_consistency",
    "evaluate_decision_cas_consistency",
    "build_decision_intelligence",
    "apply_decision_intelligence",

    # --------------------------------------------------------
    # Risk + CAS functions
    # --------------------------------------------------------
    "assess_risk_and_cas",
    "build_advanced_operational_assessment",
    "apply_operational_assessment",

    # --------------------------------------------------------
    # Engine information / health
    # --------------------------------------------------------
    "advanced_decision_health_check",
    "get_advanced_decision_engine_info",
]


# ============================================================
# END OF ADVANCED_DECISION.PY
# PART 5/5 — COMPLETE
# ============================================================