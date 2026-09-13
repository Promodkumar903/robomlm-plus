# ============================================================
# ROBOMLM_PLUS
# EVIDENCE MEMORY ENGINE
# FILE: app/intelligence/memory/evidence_memory.py
# PART 1 / 5
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

EVIDENCE_MEMORY_ENGINE = "ROBOMLM_EVIDENCE_MEMORY_ENGINE"
EVIDENCE_MEMORY_VERSION = "1.0"


# ============================================================
# ENUMS
# ============================================================

class EvidenceMemoryStatus(str, Enum):
    NEW = "NEW"
    CAPTURING = "CAPTURING"
    STORED = "STORED"
    RETRIEVING = "RETRIEVING"
    VALIDATING = "VALIDATING"
    CONSOLIDATED = "CONSOLIDATED"
    STALE = "STALE"
    INVALID = "INVALID"
    ARCHIVED = "ARCHIVED"
    UNKNOWN = "UNKNOWN"


class EvidenceMemoryType(str, Enum):
    MARKET_EVIDENCE = "MARKET_EVIDENCE"
    TECHNICAL_EVIDENCE = "TECHNICAL_EVIDENCE"
    MICROSTRUCTURE_EVIDENCE = "MICROSTRUCTURE_EVIDENCE"
    DERIVATIVE_EVIDENCE = "DERIVATIVE_EVIDENCE"
    LIQUIDITY_EVIDENCE = "LIQUIDITY_EVIDENCE"
    VOLATILITY_EVIDENCE = "VOLATILITY_EVIDENCE"
    PARTICIPATION_EVIDENCE = "PARTICIPATION_EVIDENCE"
    RELATIONSHIP_EVIDENCE = "RELATIONSHIP_EVIDENCE"
    CONTEXT_EVIDENCE = "CONTEXT_EVIDENCE"
    EVENT_EVIDENCE = "EVENT_EVIDENCE"
    DECISION_EVIDENCE = "DECISION_EVIDENCE"
    OUTCOME_EVIDENCE = "OUTCOME_EVIDENCE"
    RESEARCH_EVIDENCE = "RESEARCH_EVIDENCE"
    UNKNOWN = "UNKNOWN"


class EvidenceMemoryPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class EvidenceMemorySourceType(str, Enum):
    LIVE_MARKET = "LIVE_MARKET"
    HISTORICAL = "HISTORICAL"
    EVIDENCE_CORTEX = "EVIDENCE_CORTEX"
    DECISION_CORTEX = "DECISION_CORTEX"
    OUTCOME = "OUTCOME"
    RESEARCH = "RESEARCH"
    SYSTEM = "SYSTEM"
    UNKNOWN = "UNKNOWN"


class EvidenceMemoryQuality(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class EvidenceMemoryContractStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


# ============================================================
# CORE REQUEST CONTRACT
# ============================================================

@dataclass(frozen=True)
class EvidenceMemoryRequest:
    """
    Contract for storing/retrieving evidence memory.

    This layer records evidence.
    It does not make trading decisions and does not authorize action.
    """

    market: str
    evidence_type: EvidenceMemoryType = EvidenceMemoryType.UNKNOWN
    source: str = ""
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    symbol: str = ""
    timeframe: str = ""
    session: str = ""
    regime: str = ""

    priority: EvidenceMemoryPriority = EvidenceMemoryPriority.UNKNOWN

    evidence_id: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    request_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    def validate(self) -> bool:
        if not self.market.strip():
            return False

        if not self.request_id.strip():
            return False

        if not isinstance(self.metadata, Mapping):
            return False

        if not isinstance(self.evidence_type, EvidenceMemoryType):
            return False

        if not isinstance(self.priority, EvidenceMemoryPriority):
            return False

        return True


# ============================================================
# EVIDENCE MEMORY REFERENCE
# ============================================================

@dataclass(frozen=True)
class EvidenceMemoryReference:
    memory_id: str
    evidence_id: str

    market_name: str
    symbol: str

    evidence_type: EvidenceMemoryType
    status: EvidenceMemoryStatus
    priority: EvidenceMemoryPriority

    timestamp: datetime
    timeframe: str
    session: str
    regime: str

    source_type: EvidenceMemorySourceType

    evidence: Mapping[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# SOURCE REFERENCE
# ============================================================

@dataclass(frozen=True)
class EvidenceMemorySourceReference:
    source_id: str
    source_name: str
    source_type: EvidenceMemorySourceType

    timestamp: Optional[datetime] = None

    provenance: str = ""
    description: str = ""

    raw_source: Mapping[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# CONTRACT VALIDATION
# ============================================================

@dataclass(frozen=True)
class EvidenceMemoryContractValidation:
    valid: bool

    market_available: bool
    evidence_type_defined: bool
    priority_defined: bool
    metadata_valid: bool
    timestamp_valid: bool

    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:
        return self.valid


# ============================================================
# INTERNAL NORMALIZATION HELPERS
# ============================================================

def _em_read_value(
    source: Any,
    key: str,
    default: Any = None,
) -> Any:
    if source is None:
        return default

    if isinstance(source, Mapping):
        return source.get(key, default)

    return getattr(source, key, default)


def _em_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _em_timestamp(value: Any) -> Optional[datetime]:
    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        text = value.strip()

        if not text:
            return None

        try:
            return datetime.fromisoformat(
                text.replace("Z", "+00:00")
            )
        except ValueError:
            return None

    return None


def _em_enum(
    value: Any,
    enum_type: type[Enum],
    default: Enum,
) -> Enum:
    if isinstance(value, enum_type):
        return value

    if value is None:
        return default

    text = _em_text(value)

    if not text:
        return default

    for member in enum_type:
        if member.value.upper() == text.upper():
            return member

    return default


# ============================================================
# REFERENCE BUILDER
# ============================================================

def build_evidence_memory_reference(
    evidence: Any,
    request: Optional[EvidenceMemoryRequest] = None,
) -> EvidenceMemoryReference:
    """
    Normalize evidence into a stable memory reference.

    No intelligence score is generated here.
    """

    market = _em_text(
        _em_read_value(
            evidence,
            "market",
            request.market if request else "",
        )
    )

    symbol = _em_text(
        _em_read_value(
            evidence,
            "symbol",
            request.symbol if request else "",
        )
    )

    evidence_id = _em_text(
        _em_read_value(
            evidence,
            "evidence_id",
            request.evidence_id if request else "",
        )
    )

    if not evidence_id:
        evidence_id = str(uuid4())

    memory_id = str(uuid4())

    timestamp = _em_timestamp(
        _em_read_value(
            evidence,
            "timestamp",
            request.timestamp if request else None,
        )
    )

    if timestamp is None:
        timestamp = datetime.now(timezone.utc)

    evidence_type = _em_enum(
        _em_read_value(
            evidence,
            "evidence_type",
            request.evidence_type if request else None,
        ),
        EvidenceMemoryType,
        EvidenceMemoryType.UNKNOWN,
    )

    priority = _em_enum(
        _em_read_value(
            evidence,
            "priority",
            request.priority if request else None,
        ),
        EvidenceMemoryPriority,
        EvidenceMemoryPriority.UNKNOWN,
    )

    source_type = _em_enum(
        _em_read_value(
            evidence,
            "source_type",
            EvidenceMemorySourceType.EVIDENCE_CORTEX,
        ),
        EvidenceMemorySourceType,
        EvidenceMemorySourceType.UNKNOWN,
    )

    status = _em_enum(
        _em_read_value(
            evidence,
            "status",
            EvidenceMemoryStatus.NEW,
        ),
        EvidenceMemoryStatus,
        EvidenceMemoryStatus.NEW,
    )

    raw_evidence = (
        dict(evidence)
        if isinstance(evidence, Mapping)
        else {}
    )

    return EvidenceMemoryReference(
        memory_id=memory_id,
        evidence_id=evidence_id,
        market_name=market,
        symbol=symbol,
        evidence_type=evidence_type,
        status=status,
        priority=priority,
        timestamp=timestamp,
        timeframe=_em_text(
            _em_read_value(
                evidence,
                "timeframe",
                request.timeframe if request else "",
            )
        ),
        session=_em_text(
            _em_read_value(
                evidence,
                "session",
                request.session if request else "",
            )
        ),
        regime=_em_text(
            _em_read_value(
                evidence,
                "regime",
                request.regime if request else "",
            )
        ),
        source_type=source_type,
        evidence=raw_evidence,
    )


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_evidence_memory_request(
    request: Optional[EvidenceMemoryRequest],
) -> EvidenceMemoryContractValidation:
    errors: list[str] = []
    warnings: list[str] = []

    if request is None:
        return EvidenceMemoryContractValidation(
            valid=False,
            market_available=False,
            evidence_type_defined=False,
            priority_defined=False,
            metadata_valid=False,
            timestamp_valid=False,
            errors=("evidence_memory_request_missing",),
            warnings=(),
        )

    market_available = bool(request.market.strip())

    evidence_type_defined = (
        request.evidence_type
        != EvidenceMemoryType.UNKNOWN
    )

    priority_defined = (
        request.priority
        != EvidenceMemoryPriority.UNKNOWN
    )

    metadata_valid = isinstance(
        request.metadata,
        Mapping,
    )

    timestamp_valid = (
        _em_timestamp(request.timestamp) is not None
    )

    if not market_available:
        errors.append("market_missing")

    if not evidence_type_defined:
        warnings.append("evidence_type_undefined")

    if not priority_defined:
        warnings.append("priority_undefined")

    if not metadata_valid:
        errors.append("metadata_invalid")

    if not timestamp_valid:
        errors.append("timestamp_invalid")

    if not request.request_id.strip():
        errors.append("request_id_missing")

    return EvidenceMemoryContractValidation(
        valid=not errors,
        market_available=market_available,
        evidence_type_defined=evidence_type_defined,
        priority_defined=priority_defined,
        metadata_valid=metadata_valid,
        timestamp_valid=timestamp_valid,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )
# ============================================================
# EVIDENCE MEMORY ENGINE
# PART 2 / 5
# STRUCTURAL REQUIREMENTS + ASSESSMENT
# ============================================================


# ============================================================
# DATA STATE
# ============================================================

class EvidenceMemoryDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    UNKNOWN = "UNKNOWN"


class EvidenceMemoryConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONFLICTING = "CONFLICTING"
    INSUFFICIENT = "INSUFFICIENT"
    UNKNOWN = "UNKNOWN"


class EvidenceMemoryReadiness(str, Enum):
    READY = "READY"
    CONDITIONAL = "CONDITIONAL"
    NOT_READY = "NOT_READY"
    UNKNOWN = "UNKNOWN"


# ============================================================
# REQUIREMENTS CONTRACT
# ============================================================

@dataclass(frozen=True)
class EvidenceMemoryRequirements:
    memory_available: bool
    evidence_available: bool
    market_available: bool
    evidence_type_defined: bool

    evidence_id_available: bool
    symbol_available: bool
    timestamp_available: bool
    source_available: bool

    timeframe_available: bool
    session_available: bool
    regime_available: bool

    data_state: EvidenceMemoryDataState
    consistency: EvidenceMemoryConsistency
    readiness: EvidenceMemoryReadiness

    completeness_score: float = 0.0
    warnings: tuple[str, ...] = ()


# ============================================================
# ASSESSMENT CONTRACT
# ============================================================

@dataclass(frozen=True)
class EvidenceMemoryAssessment:
    readiness: EvidenceMemoryReadiness
    data_state: EvidenceMemoryDataState
    consistency: EvidenceMemoryConsistency
    quality: EvidenceMemoryQuality

    confidence_score: float
    completeness_score: float

    strengths: tuple[str, ...] = ()
    weaknesses: tuple[str, ...] = ()

    rationale: str = ""


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _em_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    if value is None:
        return False

    if isinstance(value, (int, float)):
        return value != 0

    text = _em_text(value).lower()

    return text in {
        "true",
        "1",
        "yes",
        "y",
        "available",
        "valid",
        "present",
        "pass",
        "passed",
        "consistent",
        "aligned",
    }


def _em_conflict_detected(source: Any) -> bool:
    candidates = (
        "conflict",
        "conflicted",
        "conflicting",
        "has_conflict",
        "evidence_conflict",
        "consistency_conflict",
    )

    for key in candidates:
        value = _em_read_value(source, key, None)

        if _em_bool(value):
            return True

    consistency = _em_text(
        _em_read_value(source, "consistency", "")
    ).lower()

    return consistency in {
        "conflicting",
        "conflict",
        "contradictory",
        "contradiction",
    }


# ============================================================
# DATA STATE EVALUATION
# ============================================================

def evaluate_evidence_memory_data_state(
    reference: Optional[EvidenceMemoryReference],
) -> EvidenceMemoryDataState:

    if reference is None:
        return EvidenceMemoryDataState.MISSING

    components = (
        bool(reference.memory_id),
        bool(reference.evidence_id),
        bool(reference.market_name),
        reference.evidence_type
        != EvidenceMemoryType.UNKNOWN,
        bool(reference.symbol),
        reference.timestamp is not None,
        bool(reference.source_type)
        and reference.source_type
        != EvidenceMemorySourceType.UNKNOWN,
    )

    available = sum(components)

    if available == len(components):
        return EvidenceMemoryDataState.COMPLETE

    if available == 0:
        return EvidenceMemoryDataState.MISSING

    return EvidenceMemoryDataState.PARTIAL


# ============================================================
# CONSISTENCY EVALUATION
# ============================================================

def evaluate_evidence_memory_consistency(
    evidence: Any,
) -> EvidenceMemoryConsistency:

    if evidence is None:
        return EvidenceMemoryConsistency.INSUFFICIENT

    if _em_conflict_detected(evidence):
        return EvidenceMemoryConsistency.CONFLICTING

    consistency = _em_text(
        _em_read_value(evidence, "consistency", "")
    ).lower()

    if consistency in {
        "consistent",
        "valid",
        "aligned",
        "pass",
        "passed",
        "confirmed",
    }:
        return EvidenceMemoryConsistency.CONSISTENT

    if consistency in {
        "conflicting",
        "conflict",
        "contradictory",
        "contradiction",
    }:
        return EvidenceMemoryConsistency.CONFLICTING

    if consistency in {
        "insufficient",
        "unknown",
        "unavailable",
        "missing",
    }:
        return EvidenceMemoryConsistency.INSUFFICIENT

    return EvidenceMemoryConsistency.UNKNOWN


# ============================================================
# REQUIREMENTS EVALUATION
# ============================================================

def evaluate_evidence_memory_requirements(
    reference: Optional[EvidenceMemoryReference],
    evidence: Any = None,
) -> EvidenceMemoryRequirements:

    if reference is None:
        return EvidenceMemoryRequirements(
            memory_available=False,
            evidence_available=False,
            market_available=False,
            evidence_type_defined=False,
            evidence_id_available=False,
            symbol_available=False,
            timestamp_available=False,
            source_available=False,
            timeframe_available=False,
            session_available=False,
            regime_available=False,
            data_state=EvidenceMemoryDataState.MISSING,
            consistency=EvidenceMemoryConsistency.INSUFFICIENT,
            readiness=EvidenceMemoryReadiness.NOT_READY,
            completeness_score=0.0,
            warnings=("evidence_memory_reference_missing",),
        )

    memory_available = bool(reference.memory_id)
    evidence_available = bool(reference.evidence)
    market_available = bool(reference.market_name)

    evidence_type_defined = (
        reference.evidence_type
        != EvidenceMemoryType.UNKNOWN
    )

    evidence_id_available = bool(reference.evidence_id)
    symbol_available = bool(reference.symbol)
    timestamp_available = reference.timestamp is not None

    source_available = (
        reference.source_type
        != EvidenceMemorySourceType.UNKNOWN
    )

    timeframe_available = bool(reference.timeframe)
    session_available = bool(reference.session)
    regime_available = bool(reference.regime)

    data_state = evaluate_evidence_memory_data_state(
        reference
    )

    consistency = evaluate_evidence_memory_consistency(
        evidence if evidence is not None else reference.evidence
    )

    completeness_components = (
        memory_available,
        evidence_available,
        market_available,
        evidence_type_defined,
        evidence_id_available,
        symbol_available,
        timestamp_available,
        source_available,
        timeframe_available,
        session_available,
        regime_available,
    )

    completeness_score = (
        sum(completeness_components)
        / len(completeness_components)
        * 100.0
    )

    warnings: list[str] = []

    if not evidence_available:
        warnings.append("evidence_payload_missing")

    if not symbol_available:
        warnings.append("symbol_missing")

    if not timestamp_available:
        warnings.append("timestamp_missing")

    if not source_available:
        warnings.append("source_missing")

    if not timeframe_available:
        warnings.append("timeframe_missing")

    if not session_available:
        warnings.append("session_missing")

    if not regime_available:
        warnings.append("regime_missing")

    if consistency == EvidenceMemoryConsistency.CONFLICTING:
        warnings.append("evidence_conflict_detected")

    if (
        data_state == EvidenceMemoryDataState.COMPLETE
        and consistency != EvidenceMemoryConsistency.CONFLICTING
    ):
        readiness = EvidenceMemoryReadiness.READY

    elif data_state == EvidenceMemoryDataState.PARTIAL:
        readiness = EvidenceMemoryReadiness.CONDITIONAL

    elif data_state == EvidenceMemoryDataState.MISSING:
        readiness = EvidenceMemoryReadiness.NOT_READY

    else:
        readiness = EvidenceMemoryReadiness.UNKNOWN

    if consistency == EvidenceMemoryConsistency.CONFLICTING:
        readiness = EvidenceMemoryReadiness.NOT_READY

    return EvidenceMemoryRequirements(
        memory_available=memory_available,
        evidence_available=evidence_available,
        market_available=market_available,
        evidence_type_defined=evidence_type_defined,
        evidence_id_available=evidence_id_available,
        symbol_available=symbol_available,
        timestamp_available=timestamp_available,
        source_available=source_available,
        timeframe_available=timeframe_available,
        session_available=session_available,
        regime_available=regime_available,
        data_state=data_state,
        consistency=consistency,
        readiness=readiness,
        completeness_score=completeness_score,
        warnings=tuple(warnings),
    )


# ============================================================
# READINESS EVALUATION
# ============================================================

def evaluate_evidence_memory_readiness(
    requirements: EvidenceMemoryRequirements,
) -> EvidenceMemoryReadiness:

    if requirements.consistency == (
        EvidenceMemoryConsistency.CONFLICTING
    ):
        return EvidenceMemoryReadiness.NOT_READY

    if requirements.data_state == (
        EvidenceMemoryDataState.COMPLETE
    ):
        return EvidenceMemoryReadiness.READY

    if requirements.data_state == (
        EvidenceMemoryDataState.PARTIAL
    ):
        return EvidenceMemoryReadiness.CONDITIONAL

    if requirements.data_state == (
        EvidenceMemoryDataState.MISSING
    ):
        return EvidenceMemoryReadiness.NOT_READY

    return EvidenceMemoryReadiness.UNKNOWN


# ============================================================
# CONFIDENCE CALCULATION
# ============================================================

def calculate_evidence_memory_confidence(
    requirements: EvidenceMemoryRequirements,
) -> float:

    score = float(requirements.completeness_score)

    if requirements.consistency == (
        EvidenceMemoryConsistency.CONSISTENT
    ):
        score += 5.0

    elif requirements.consistency == (
        EvidenceMemoryConsistency.CONFLICTING
    ):
        score -= 30.0

    elif requirements.consistency == (
        EvidenceMemoryConsistency.INSUFFICIENT
    ):
        score -= 10.0

    if requirements.data_state == (
        EvidenceMemoryDataState.MISSING
    ):
        score -= 20.0

    return max(0.0, min(100.0, score))


# ============================================================
# QUALITY DETERMINATION
# ============================================================

def determine_evidence_memory_quality(
    confidence_score: float,
    consistency: EvidenceMemoryConsistency,
) -> EvidenceMemoryQuality:

    if consistency == EvidenceMemoryConsistency.CONFLICTING:
        return EvidenceMemoryQuality.LOW

    if confidence_score >= 90.0:
        return EvidenceMemoryQuality.CRITICAL

    if confidence_score >= 75.0:
        return EvidenceMemoryQuality.HIGH

    if confidence_score >= 50.0:
        return EvidenceMemoryQuality.MODERATE

    if confidence_score > 0.0:
        return EvidenceMemoryQuality.LOW

    return EvidenceMemoryQuality.UNKNOWN


# ============================================================
# ASSESSMENT BUILDER
# ============================================================

def build_evidence_memory_assessment(
    requirements: EvidenceMemoryRequirements,
) -> EvidenceMemoryAssessment:

    readiness = evaluate_evidence_memory_readiness(
        requirements
    )

    confidence_score = calculate_evidence_memory_confidence(
        requirements
    )

    quality = determine_evidence_memory_quality(
        confidence_score,
        requirements.consistency,
    )

    strengths: list[str] = []
    weaknesses: list[str] = []

    if requirements.memory_available:
        strengths.append("memory_identity_available")

    if requirements.evidence_available:
        strengths.append("evidence_payload_available")

    if requirements.market_available:
        strengths.append("market_available")

    if requirements.evidence_type_defined:
        strengths.append("evidence_type_defined")

    if requirements.source_available:
        strengths.append("source_available")

    if requirements.consistency == (
        EvidenceMemoryConsistency.CONSISTENT
    ):
        strengths.append("evidence_consistency_confirmed")

    if not requirements.symbol_available:
        weaknesses.append("symbol_missing")

    if not requirements.timestamp_available:
        weaknesses.append("timestamp_missing")

    if not requirements.source_available:
        weaknesses.append("source_missing")

    if not requirements.evidence_available:
        weaknesses.append("evidence_payload_missing")

    if requirements.consistency == (
        EvidenceMemoryConsistency.CONFLICTING
    ):
        weaknesses.append("evidence_conflict_detected")

    if readiness == EvidenceMemoryReadiness.READY:
        rationale = (
            "Evidence memory has complete structural requirements "
            "and no detected evidence conflict."
        )

    elif readiness == EvidenceMemoryReadiness.CONDITIONAL:
        rationale = (
            "Evidence memory is structurally partial and may require "
            "additional evidence before full readiness."
        )

    elif readiness == EvidenceMemoryReadiness.NOT_READY:
        rationale = (
            "Evidence memory is not ready because required structure "
            "is missing or evidence consistency is unacceptable."
        )

    else:
        rationale = (
            "Evidence memory readiness could not be determined."
        )

    return EvidenceMemoryAssessment(
        readiness=readiness,
        data_state=requirements.data_state,
        consistency=requirements.consistency,
        quality=quality,
        confidence_score=confidence_score,
        completeness_score=requirements.completeness_score,
        strengths=tuple(strengths),
        weaknesses=tuple(weaknesses),
        rationale=rationale,
    )
# ============================================================
# EVIDENCE MEMORY ENGINE
# PART 3 / 5
# ACTION + RESULT + CONTRACT + ENGINE
# ============================================================


# ============================================================
# ACTION STATE
# ============================================================

class EvidenceMemoryActionState(str, Enum):
    NONE = "NONE"
    STORE = "STORE"
    RETRIEVE = "RETRIEVE"
    CONSOLIDATE = "CONSOLIDATE"
    REVIEW = "REVIEW"
    HOLD = "HOLD"
    INVALIDATE = "INVALIDATE"
    ARCHIVE = "ARCHIVE"


# ============================================================
# CONTRACT STATE
# ============================================================

class EvidenceMemoryContractState(str, Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


# ============================================================
# RESULT STATUS
# ============================================================

class EvidenceMemoryResultStatus(str, Enum):
    STORED = "STORED"
    CONDITIONAL = "CONDITIONAL"
    REVIEW = "REVIEW"
    HOLD = "HOLD"
    INVALIDATED = "INVALIDATED"
    ARCHIVED = "ARCHIVED"
    INVALID = "INVALID"


# ============================================================
# ACTION CONTRACT
# ============================================================

@dataclass(frozen=True)
class EvidenceMemoryAction:
    state: EvidenceMemoryActionState
    memory_id: str = ""
    rationale: str = ""
    warnings: tuple[str, ...] = ()

    @property
    def is_action_request(self) -> bool:
        return False


# ============================================================
# RESULT CONTRACT
# ============================================================

@dataclass(frozen=True)
class EvidenceMemoryResult:
    request_id: str
    result_id: str

    status: EvidenceMemoryResultStatus

    memory: Optional[EvidenceMemoryReference]
    requirements: EvidenceMemoryRequirements
    assessment: EvidenceMemoryAssessment
    action: EvidenceMemoryAction

    rationale: str = ""
    warnings: tuple[str, ...] = ()

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def is_valid(self) -> bool:
        return bool(
            self.request_id
            and self.result_id
            and self.memory is not None
            and self.status
            != EvidenceMemoryResultStatus.INVALID
        )

    @property
    def stored(self) -> bool:
        return (
            self.is_valid
            and self.status
            == EvidenceMemoryResultStatus.STORED
        )

    @property
    def is_conditional(self) -> bool:
        return (
            self.status
            == EvidenceMemoryResultStatus.CONDITIONAL
        )

    @property
    def requires_review(self) -> bool:
        return (
            self.status
            == EvidenceMemoryResultStatus.REVIEW
            or self.action.state
            == EvidenceMemoryActionState.REVIEW
        )

    @property
    def requires_hold(self) -> bool:
        return (
            self.status
            == EvidenceMemoryResultStatus.HOLD
            or self.action.state
            == EvidenceMemoryActionState.HOLD
        )

    @property
    def is_invalidated(self) -> bool:
        return (
            self.status
            == EvidenceMemoryResultStatus.INVALIDATED
            or self.action.state
            == EvidenceMemoryActionState.INVALIDATE
        )

    @property
    def is_action_request(self) -> bool:
        return False


# ============================================================
# CONTRACT
# ============================================================

@dataclass(frozen=True)
class EvidenceMemoryContract:
    request_id: str
    contract_id: str

    state: EvidenceMemoryContractState

    result: EvidenceMemoryResult

    rationale: str = ""
    warnings: tuple[str, ...] = ()

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def is_valid(self) -> bool:
        return bool(
            self.request_id
            and self.contract_id
            and self.result.is_valid
            and self.state
            != EvidenceMemoryContractState.INVALID
        )

    @property
    def stored(self) -> bool:
        return (
            self.is_valid
            and self.state
            == EvidenceMemoryContractState.COMPLETE
            and self.result.stored
        )

    @property
    def is_action_request(self) -> bool:
        return False


# ============================================================
# RESULT STATUS DETERMINATION
# ============================================================

def _determine_evidence_memory_result_status(
    assessment: EvidenceMemoryAssessment,
) -> EvidenceMemoryResultStatus:

    if assessment.consistency == (
        EvidenceMemoryConsistency.CONFLICTING
    ):
        return EvidenceMemoryResultStatus.INVALIDATED

    if assessment.readiness == (
        EvidenceMemoryReadiness.READY
    ):
        return EvidenceMemoryResultStatus.STORED

    if assessment.readiness == (
        EvidenceMemoryReadiness.CONDITIONAL
    ):
        return EvidenceMemoryResultStatus.CONDITIONAL

    if assessment.readiness == (
        EvidenceMemoryReadiness.NOT_READY
    ):
        return EvidenceMemoryResultStatus.HOLD

    return EvidenceMemoryResultStatus.REVIEW


# ============================================================
# ACTION BUILDER
# ============================================================

def build_evidence_memory_action(
    status: EvidenceMemoryResultStatus,
    memory_id: str = "",
) -> EvidenceMemoryAction:

    if status == EvidenceMemoryResultStatus.STORED:
        return EvidenceMemoryAction(
            state=EvidenceMemoryActionState.STORE,
            memory_id=memory_id,
            rationale="Evidence memory is structurally ready.",
        )

    if status in (
        EvidenceMemoryResultStatus.CONDITIONAL,
        EvidenceMemoryResultStatus.REVIEW,
    ):
        return EvidenceMemoryAction(
            state=EvidenceMemoryActionState.REVIEW,
            memory_id=memory_id,
            rationale=(
                "Evidence memory requires additional validation "
                "or evidence before full readiness."
            ),
        )

    if status == EvidenceMemoryResultStatus.HOLD:
        return EvidenceMemoryAction(
            state=EvidenceMemoryActionState.HOLD,
            memory_id=memory_id,
            rationale=(
                "Evidence memory is not ready for progression."
            ),
        )

    if status == EvidenceMemoryResultStatus.INVALIDATED:
        return EvidenceMemoryAction(
            state=EvidenceMemoryActionState.INVALIDATE,
            memory_id=memory_id,
            rationale=(
                "Evidence conflict prevents trusted memory use."
            ),
        )

    if status == EvidenceMemoryResultStatus.ARCHIVED:
        return EvidenceMemoryAction(
            state=EvidenceMemoryActionState.ARCHIVE,
            memory_id=memory_id,
            rationale="Evidence memory is archived.",
        )

    return EvidenceMemoryAction(
        state=EvidenceMemoryActionState.NONE,
        memory_id=memory_id,
        rationale="No evidence memory lifecycle action.",
    )


# ============================================================
# RESULT BUILDER
# ============================================================

def build_evidence_memory_result(
    request: EvidenceMemoryRequest,
    reference: Optional[EvidenceMemoryReference],
    requirements: EvidenceMemoryRequirements,
    assessment: EvidenceMemoryAssessment,
) -> EvidenceMemoryResult:

    status = _determine_evidence_memory_result_status(
        assessment
    )

    memory_id = (
        reference.memory_id
        if reference is not None
        else ""
    )

    action = build_evidence_memory_action(
        status,
        memory_id,
    )

    warnings = list(requirements.warnings)

    if assessment.weaknesses:
        warnings.extend(assessment.weaknesses)

    return EvidenceMemoryResult(
        request_id=request.request_id,
        result_id=str(uuid4()),
        status=status,
        memory=reference,
        requirements=requirements,
        assessment=assessment,
        action=action,
        rationale=assessment.rationale,
        warnings=tuple(dict.fromkeys(warnings)),
    )


# ============================================================
# CONTRACT STATE
# ============================================================

def _determine_evidence_memory_contract_state(
    result: EvidenceMemoryResult,
) -> EvidenceMemoryContractState:

    if not result.is_valid:
        return EvidenceMemoryContractState.INVALID

    if result.status == (
        EvidenceMemoryResultStatus.INVALIDATED
    ):
        return EvidenceMemoryContractState.BLOCKED

    if (
        result.requirements.data_state
        == EvidenceMemoryDataState.COMPLETE
        and result.requirements.readiness
        == EvidenceMemoryReadiness.READY
        and result.requirements.consistency
        != EvidenceMemoryConsistency.CONFLICTING
    ):
        return EvidenceMemoryContractState.COMPLETE

    if result.requirements.data_state == (
        EvidenceMemoryDataState.MISSING
    ):
        return EvidenceMemoryContractState.INCOMPLETE

    return EvidenceMemoryContractState.INCOMPLETE


# ============================================================
# CONTRACT BUILDER
# ============================================================

def build_evidence_memory_contract(
    result: EvidenceMemoryResult,
) -> EvidenceMemoryContract:

    state = _determine_evidence_memory_contract_state(
        result
    )

    warnings = list(result.warnings)

    if state == EvidenceMemoryContractState.BLOCKED:
        warnings.append("evidence_memory_contract_blocked")

    if state == EvidenceMemoryContractState.INCOMPLETE:
        warnings.append("evidence_memory_contract_incomplete")

    return EvidenceMemoryContract(
        request_id=result.request_id,
        contract_id=str(uuid4()),
        state=state,
        result=result,
        rationale=result.rationale,
        warnings=tuple(dict.fromkeys(warnings)),
    )


# ============================================================
# ENGINE
# ============================================================

class EvidenceMemoryEngine:
    """
    Evidence Memory orchestration engine.

    Responsibilities:
        - validate evidence-memory request
        - normalize evidence reference
        - evaluate structural requirements
        - evaluate evidence consistency
        - evaluate readiness
        - build evidence-memory assessment
        - build result
        - build contract

    Non-responsibilities:
        - trade execution
        - order creation
        - position modification
        - account authorization
        - D13 override
        - Risk override
        - CAS override
    """

    name = EVIDENCE_MEMORY_ENGINE
    version = EVIDENCE_MEMORY_VERSION

    def validate_request(
        self,
        request: Optional[EvidenceMemoryRequest],
    ) -> EvidenceMemoryContractValidation:
        return validate_evidence_memory_request(request)

    def _invalid_result(
        self,
        request: EvidenceMemoryRequest,
        validation: EvidenceMemoryContractValidation,
    ) -> EvidenceMemoryResult:

        requirements = EvidenceMemoryRequirements(
            memory_available=False,
            evidence_available=False,
            market_available=validation.market_available,
            evidence_type_defined=(
                validation.evidence_type_defined
            ),
            evidence_id_available=False,
            symbol_available=False,
            timestamp_available=validation.timestamp_valid,
            source_available=False,
            timeframe_available=False,
            session_available=False,
            regime_available=False,
            data_state=EvidenceMemoryDataState.MISSING,
            consistency=EvidenceMemoryConsistency.INSUFFICIENT,
            readiness=EvidenceMemoryReadiness.NOT_READY,
            completeness_score=0.0,
            warnings=validation.warnings,
        )

        assessment = EvidenceMemoryAssessment(
            readiness=EvidenceMemoryReadiness.NOT_READY,
            data_state=EvidenceMemoryDataState.MISSING,
            consistency=EvidenceMemoryConsistency.INSUFFICIENT,
            quality=EvidenceMemoryQuality.UNKNOWN,
            confidence_score=0.0,
            completeness_score=0.0,
            strengths=(),
            weaknesses=tuple(validation.errors),
            rationale="Invalid evidence memory request.",
        )

        action = EvidenceMemoryAction(
            state=EvidenceMemoryActionState.HOLD,
            rationale="Invalid evidence memory request.",
            warnings=tuple(validation.errors),
        )

        return EvidenceMemoryResult(
            request_id=request.request_id,
            result_id=str(uuid4()),
            status=EvidenceMemoryResultStatus.INVALID,
            memory=None,
            requirements=requirements,
            assessment=assessment,
            action=action,
            rationale="Evidence memory request validation failed.",
            warnings=tuple(validation.errors),
        )

    def evaluate(
        self,
        request: EvidenceMemoryRequest,
        evidence: Any = None,
    ) -> EvidenceMemoryContract:

        validation = self.validate_request(request)

        if not validation.valid:
            result = self._invalid_result(
                request,
                validation,
            )
            return build_evidence_memory_contract(result)

        reference = build_evidence_memory_reference(
            evidence,
            request,
        )

        requirements = evaluate_evidence_memory_requirements(
            reference,
            evidence,
        )

        assessment = build_evidence_memory_assessment(
            requirements
        )

        result = build_evidence_memory_result(
            request=request,
            reference=reference,
            requirements=requirements,
            assessment=assessment,
        )

        return build_evidence_memory_contract(result)


# ============================================================
# SINGLETON
# ============================================================

evidence_memory_engine = EvidenceMemoryEngine()


# ============================================================
# PUBLIC OPERATIONS
# ============================================================

def evaluate_evidence_memory(
    request: EvidenceMemoryRequest,
    evidence: Any = None,
) -> EvidenceMemoryContract:
    return evidence_memory_engine.evaluate(
        request,
        evidence,
    )


def analyze_evidence_memory(
    request: EvidenceMemoryRequest,
    evidence: Any = None,
) -> EvidenceMemoryContract:
    return evaluate_evidence_memory(
        request,
        evidence,
    )


def review_evidence_memory(
    request: EvidenceMemoryRequest,
    evidence: Any = None,
) -> EvidenceMemoryContract:
    return evaluate_evidence_memory(
        request,
        evidence,
    )
# ============================================================
# EVIDENCE MEMORY ENGINE
# PART 4 / 5
# VALIDATION + READINESS + AUDIT + SAFETY + HEALTH
# ============================================================


# ============================================================
# RESULT VALIDATION
# ============================================================

def validate_evidence_memory_result(
    result: Optional[EvidenceMemoryResult],
) -> EvidenceMemoryContractValidation:

    errors: list[str] = []
    warnings: list[str] = []

    if result is None:
        return EvidenceMemoryContractValidation(
            valid=False,
            market_available=False,
            evidence_type_defined=False,
            priority_defined=False,
            metadata_valid=False,
            timestamp_valid=False,
            errors=("evidence_memory_result_missing",),
            warnings=(),
        )

    if not result.request_id.strip():
        errors.append("request_id_missing")

    if not result.result_id.strip():
        errors.append("result_id_missing")

    if result.memory is None:
        errors.append("memory_reference_missing")
        return EvidenceMemoryContractValidation(
            valid=False,
            market_available=False,
            evidence_type_defined=False,
            priority_defined=False,
            metadata_valid=False,
            timestamp_valid=False,
            errors=tuple(errors),
            warnings=tuple(warnings),
        )

    memory = result.memory

    market_available = bool(memory.market_name.strip())

    evidence_type_defined = (
        memory.evidence_type
        != EvidenceMemoryType.UNKNOWN
    )

    priority_defined = (
        memory.priority
        != EvidenceMemoryPriority.UNKNOWN
    )

    metadata_valid = isinstance(
        memory.evidence,
        Mapping,
    )

    timestamp_valid = (
        _em_timestamp(memory.timestamp) is not None
    )

    if not market_available:
        errors.append("market_name_missing")

    if not evidence_type_defined:
        errors.append("evidence_type_undefined")

    if not priority_defined:
        warnings.append("priority_undefined")

    if not metadata_valid:
        errors.append("evidence_payload_invalid")

    if not timestamp_valid:
        errors.append("timestamp_invalid")

    if result.status == EvidenceMemoryResultStatus.INVALID:
        errors.append("result_status_invalid")

    return EvidenceMemoryContractValidation(
        valid=not errors,
        market_available=market_available,
        evidence_type_defined=evidence_type_defined,
        priority_defined=priority_defined,
        metadata_valid=metadata_valid,
        timestamp_valid=timestamp_valid,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


# ============================================================
# CONTRACT VALIDATION
# ============================================================

def validate_evidence_memory_contract(
    contract: Optional[EvidenceMemoryContract],
) -> EvidenceMemoryContractValidation:

    errors: list[str] = []
    warnings: list[str] = []

    if contract is None:
        return EvidenceMemoryContractValidation(
            valid=False,
            market_available=False,
            evidence_type_defined=False,
            priority_defined=False,
            metadata_valid=False,
            timestamp_valid=False,
            errors=("evidence_memory_contract_missing",),
            warnings=(),
        )

    if not contract.request_id.strip():
        errors.append("request_id_missing")

    if not contract.contract_id.strip():
        errors.append("contract_id_missing")

    if _em_timestamp(contract.created_at) is None:
        errors.append("created_at_invalid")

    result_validation = validate_evidence_memory_result(
        contract.result
    )

    errors.extend(result_validation.errors)
    warnings.extend(result_validation.warnings)

    if contract.state == EvidenceMemoryContractState.INVALID:
        errors.append("contract_state_invalid")

    return EvidenceMemoryContractValidation(
        valid=not errors,
        market_available=result_validation.market_available,
        evidence_type_defined=(
            result_validation.evidence_type_defined
        ),
        priority_defined=result_validation.priority_defined,
        metadata_valid=result_validation.metadata_valid,
        timestamp_valid=result_validation.timestamp_valid,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


# ============================================================
# READINESS GATES
# ============================================================

def evidence_memory_ready(
    result: Optional[EvidenceMemoryResult],
) -> bool:

    if result is None:
        return False

    validation = validate_evidence_memory_result(result)

    if not validation.valid:
        return False

    if result.status != EvidenceMemoryResultStatus.STORED:
        return False

    requirements = result.requirements
    assessment = result.assessment

    if requirements is None or assessment is None:
        return False

    if requirements.data_state != (
        EvidenceMemoryDataState.COMPLETE
    ):
        return False

    if requirements.consistency == (
        EvidenceMemoryConsistency.CONFLICTING
    ):
        return False

    if requirements.readiness != (
        EvidenceMemoryReadiness.READY
    ):
        return False

    if not requirements.memory_available:
        return False

    if not requirements.evidence_available:
        return False

    if not requirements.market_available:
        return False

    if not requirements.evidence_type_defined:
        return False

    if not requirements.evidence_id_available:
        return False

    if not requirements.symbol_available:
        return False

    if not requirements.timestamp_available:
        return False

    if not requirements.source_available:
        return False

    if assessment.confidence_score < 80.0:
        return False

    return True


def evidence_memory_can_advance(
    result: Optional[EvidenceMemoryResult],
) -> bool:

    if result is None:
        return False

    validation = validate_evidence_memory_result(result)

    if not validation.valid:
        return False

    requirements = result.requirements
    assessment = result.assessment

    if requirements is None or assessment is None:
        return False

    if requirements.consistency == (
        EvidenceMemoryConsistency.CONFLICTING
    ):
        return False

    if requirements.data_state == (
        EvidenceMemoryDataState.MISSING
    ):
        return False

    if not requirements.memory_available:
        return False

    if not requirements.evidence_available:
        return False

    if not requirements.market_available:
        return False

    if not requirements.evidence_type_defined:
        return False

    if assessment.confidence_score < 50.0:
        return False

    return (
        assessment.readiness
        in (
            EvidenceMemoryReadiness.READY,
            EvidenceMemoryReadiness.CONDITIONAL,
        )
    )


# ============================================================
# ACCESSORS
# ============================================================

def evidence_memory_status(
    result: Optional[EvidenceMemoryResult],
) -> str:

    if result is None:
        return EvidenceMemoryResultStatus.INVALID.value

    return result.status.value


def evidence_memory_type(
    result: Optional[EvidenceMemoryResult],
) -> str:

    if result is None or result.memory is None:
        return EvidenceMemoryType.UNKNOWN.value

    return result.memory.evidence_type.value


def evidence_memory_readiness(
    result: Optional[EvidenceMemoryResult],
) -> str:

    if result is None or result.assessment is None:
        return EvidenceMemoryReadiness.UNKNOWN.value

    return result.assessment.readiness.value


def evidence_memory_confidence(
    result: Optional[EvidenceMemoryResult],
) -> float:

    if result is None or result.assessment is None:
        return 0.0

    return float(result.assessment.confidence_score)


def evidence_memory_quality(
    result: Optional[EvidenceMemoryResult],
) -> str:

    if result is None or result.assessment is None:
        return EvidenceMemoryQuality.UNKNOWN.value

    return result.assessment.quality.value


def evidence_memory_completeness(
    result: Optional[EvidenceMemoryResult],
) -> float:

    if result is None or result.assessment is None:
        return 0.0

    return float(result.assessment.completeness_score)


def evidence_memory_identity(
    result: Optional[EvidenceMemoryResult],
) -> Optional[str]:

    if result is None or result.memory is None:
        return None

    return result.memory.memory_id


# ============================================================
# AUDIT
# ============================================================

def evidence_memory_audit(
    result: Optional[EvidenceMemoryResult],
) -> dict[str, Any]:

    validation = validate_evidence_memory_result(result)

    if result is None:
        return {
            "engine": EVIDENCE_MEMORY_ENGINE,
            "version": EVIDENCE_MEMORY_VERSION,
            "valid": False,
            "ready": False,
            "can_advance": False,
            "errors": list(validation.errors),
            "warnings": list(validation.warnings),
        }

    memory = result.memory
    requirements = result.requirements
    assessment = result.assessment

    return {
        "engine": EVIDENCE_MEMORY_ENGINE,
        "version": EVIDENCE_MEMORY_VERSION,
        "request_id": result.request_id,
        "result_id": result.result_id,
        "valid": validation.valid,
        "status": result.status.value,

        "memory_id": (
            memory.memory_id
            if memory else None
        ),
        "evidence_id": (
            memory.evidence_id
            if memory else None
        ),
        "market": (
            memory.market_name
            if memory else None
        ),
        "symbol": (
            memory.symbol
            if memory else None
        ),
        "evidence_type": (
            memory.evidence_type.value
            if memory
            else EvidenceMemoryType.UNKNOWN.value
        ),
        "priority": (
            memory.priority.value
            if memory
            else EvidenceMemoryPriority.UNKNOWN.value
        ),

        "data_state": (
            requirements.data_state.value
            if requirements
            else EvidenceMemoryDataState.UNKNOWN.value
        ),
        "consistency": (
            requirements.consistency.value
            if requirements
            else EvidenceMemoryConsistency.UNKNOWN.value
        ),
        "readiness": (
            assessment.readiness.value
            if assessment
            else EvidenceMemoryReadiness.UNKNOWN.value
        ),
        "quality": (
            assessment.quality.value
            if assessment
            else EvidenceMemoryQuality.UNKNOWN.value
        ),
        "confidence": (
            float(assessment.confidence_score)
            if assessment
            else 0.0
        ),
        "completeness": (
            float(assessment.completeness_score)
            if assessment
            else 0.0
        ),

        "ready": evidence_memory_ready(result),
        "can_advance": evidence_memory_can_advance(result),

        "safe": evidence_memory_is_safe(result),

        "allows_execution": (
            evidence_memory_allows_execution(result)
        ),
        "allows_trade": (
            evidence_memory_allows_trade(result)
        ),
        "allows_order": (
            evidence_memory_allows_order(result)
        ),
        "allows_position_change": (
            evidence_memory_allows_position_change(result)
        ),
        "allows_authorization": (
            evidence_memory_allows_authorization(result)
        ),

        "overrides_d13": (
            evidence_memory_overrides_d13(result)
        ),
        "overrides_risk": (
            evidence_memory_overrides_risk(result)
        ),
        "overrides_cas": (
            evidence_memory_overrides_cas(result)
        ),

        "errors": list(validation.errors),
        "warnings": list(validation.warnings),
    }


# ============================================================
# SAFETY BOUNDARIES
# ============================================================

def evidence_memory_is_safe(
    result: Optional[EvidenceMemoryResult],
) -> bool:

    if result is None:
        return False

    validation = validate_evidence_memory_result(result)

    if not validation.valid:
        return False

    if result.status in (
        EvidenceMemoryResultStatus.INVALID,
        EvidenceMemoryResultStatus.INVALIDATED,
    ):
        return False

    if result.requirements.consistency == (
        EvidenceMemoryConsistency.CONFLICTING
    ):
        return False

    return True


def evidence_memory_allows_execution(
    result: Optional[EvidenceMemoryResult],
) -> bool:
    return False


def evidence_memory_allows_trade(
    result: Optional[EvidenceMemoryResult],
) -> bool:
    return False


def evidence_memory_allows_order(
    result: Optional[EvidenceMemoryResult],
) -> bool:
    return False


def evidence_memory_allows_position_change(
    result: Optional[EvidenceMemoryResult],
) -> bool:
    return False


def evidence_memory_allows_authorization(
    result: Optional[EvidenceMemoryResult],
) -> bool:
    return False


# ============================================================
# AUTHORITY BOUNDARIES
# ============================================================

def evidence_memory_overrides_d13(
    result: Optional[EvidenceMemoryResult],
) -> bool:
    return False


def evidence_memory_overrides_risk(
    result: Optional[EvidenceMemoryResult],
) -> bool:
    return False


def evidence_memory_overrides_cas(
    result: Optional[EvidenceMemoryResult],
) -> bool:
    return False


# ============================================================
# ENGINE INFORMATION
# ============================================================

def get_evidence_memory_engine_info() -> dict[str, Any]:

    return {
        "engine": EVIDENCE_MEMORY_ENGINE,
        "version": EVIDENCE_MEMORY_VERSION,
        "role": "evidence_memory_intelligence",

        "responsibilities": [
            "evidence_memory_request_validation",
            "evidence_reference_normalization",
            "evidence_memory_requirements_evaluation",
            "evidence_consistency_evaluation",
            "evidence_memory_readiness_evaluation",
            "evidence_memory_assessment",
            "evidence_memory_result_generation",
            "evidence_memory_contract_generation",
        ],

        "non_responsibilities": [
            "trade_execution",
            "order_creation",
            "position_modification",
            "account_authorization",
            "d13_override",
            "risk_override",
            "cas_override",
        ],

        "authority": "non_authoritative_for_trade_execution",
    }


# ============================================================
# HEALTH CHECK
# ============================================================

def evidence_memory_health_check() -> dict[str, Any]:

    checks = {
        "engine_instance": isinstance(
            evidence_memory_engine,
            EvidenceMemoryEngine,
        ),

        "engine_name": (
            getattr(
                evidence_memory_engine,
                "name",
                EVIDENCE_MEMORY_ENGINE,
            )
            == EVIDENCE_MEMORY_ENGINE
        ),

        "engine_version": (
            getattr(
                evidence_memory_engine,
                "version",
                EVIDENCE_MEMORY_VERSION,
            )
            == EVIDENCE_MEMORY_VERSION
        ),

        "execution_blocked": not (
            evidence_memory_allows_execution(None)
        ),

        "trade_blocked": not (
            evidence_memory_allows_trade(None)
        ),

        "order_blocked": not (
            evidence_memory_allows_order(None)
        ),

        "position_change_blocked": not (
            evidence_memory_allows_position_change(None)
        ),

        "authorization_blocked": not (
            evidence_memory_allows_authorization(None)
        ),

        "d13_override_blocked": not (
            evidence_memory_overrides_d13(None)
        ),

        "risk_override_blocked": not (
            evidence_memory_overrides_risk(None)
        ),

        "cas_override_blocked": not (
            evidence_memory_overrides_cas(None)
        ),
    }

    return {
        "engine": EVIDENCE_MEMORY_ENGINE,
        "version": EVIDENCE_MEMORY_VERSION,
        "healthy": all(checks.values()),
        "checks": checks,
    }


def run_evidence_memory_health_check() -> bool:
    return bool(
        evidence_memory_health_check()["healthy"]
    )
# ============================================================
# ROBOMLM_PLUS
# EVIDENCE MEMORY ENGINE
# FILE: app/intelligence/memory/evidence_memory.py
# PART 5 / 5
# SERIALIZATION + LIFECYCLE + INTEGRITY + EXPORTS
# ============================================================

def evidence_memory_requires_review(
    result: Optional[EvidenceMemoryResult],
) -> bool:
    if result is None:
        return False
    return (
        result.status == EvidenceMemoryResultStatus.REVIEW
        or result.action.state == EvidenceMemoryActionState.REVIEW
    )


def evidence_memory_requires_hold(
    result: Optional[EvidenceMemoryResult],
) -> bool:
    if result is None:
        return False
    return (
        result.status == EvidenceMemoryResultStatus.HOLD
        or result.action.state == EvidenceMemoryActionState.HOLD
    )


def evidence_memory_is_invalid(
    result: Optional[EvidenceMemoryResult],
) -> bool:
    if result is None:
        return True
    return (
        result.status == EvidenceMemoryResultStatus.INVALID
        or result.status == EvidenceMemoryResultStatus.INVALIDATED
        or result.action.state == EvidenceMemoryActionState.INVALIDATE
    )


def evidence_memory_is_stored(
    result: Optional[EvidenceMemoryResult],
) -> bool:
    if result is None:
        return False
    return result.stored and evidence_memory_ready(result)


def evidence_memory_is_conditional(
    result: Optional[EvidenceMemoryResult],
) -> bool:
    return (
        result is not None
        and result.status == EvidenceMemoryResultStatus.CONDITIONAL
    )


def evidence_memory_is_archived(
    result: Optional[EvidenceMemoryResult],
) -> bool:
    if result is None:
        return False
    return (
        result.status == EvidenceMemoryResultStatus.ARCHIVED
        or result.action.state == EvidenceMemoryActionState.ARCHIVE
    )


def evidence_memory_lifecycle_state(
    result: Optional[EvidenceMemoryResult],
) -> str:
    if result is None:
        return EvidenceMemoryStatus.INVALID.value

    if evidence_memory_is_invalid(result):
        return EvidenceMemoryStatus.INVALID.value

    if evidence_memory_is_archived(result):
        return EvidenceMemoryStatus.ARCHIVED.value

    if evidence_memory_requires_hold(result):
        return EvidenceMemoryStatus.VALIDATING.value

    if evidence_memory_requires_review(result):
        return EvidenceMemoryStatus.RETRIEVING.value

    if evidence_memory_is_stored(result):
        return EvidenceMemoryStatus.STORED.value

    if evidence_memory_is_conditional(result):
        return EvidenceMemoryStatus.CAPTURING.value

    return EvidenceMemoryStatus.UNKNOWN.value


def _em_iso(value: Any) -> Optional[str]:
    if isinstance(value, datetime):
        return value.isoformat()
    return None


def serialize_evidence_memory_reference(
    reference: Optional[EvidenceMemoryReference],
) -> Optional[dict[str, Any]]:
    if reference is None:
        return None

    return {
        "memory_id": reference.memory_id,
        "evidence_id": reference.evidence_id,
        "market": reference.market_name,
        "symbol": reference.symbol,
        "evidence_type": reference.evidence_type.value,
        "status": reference.status.value,
        "priority": reference.priority.value,
        "timestamp": _em_iso(reference.timestamp),
        "timeframe": reference.timeframe,
        "session": reference.session,
        "regime": reference.regime,
        "source_type": reference.source_type.value,
        "evidence": dict(reference.evidence),
    }


def serialize_evidence_memory_result(
    result: Optional[EvidenceMemoryResult],
) -> dict[str, Any]:
    if result is None:
        return {
            "engine": EVIDENCE_MEMORY_ENGINE,
            "version": EVIDENCE_MEMORY_VERSION,
            "valid": False,
            "status": EvidenceMemoryResultStatus.INVALID.value,
        }

    requirements = result.requirements
    assessment = result.assessment

    return {
        "engine": EVIDENCE_MEMORY_ENGINE,
        "version": EVIDENCE_MEMORY_VERSION,
        "request_id": result.request_id,
        "result_id": result.result_id,
        "status": result.status.value,
        "memory": serialize_evidence_memory_reference(result.memory),
        "requirements": {
            "memory_available": requirements.memory_available,
            "evidence_available": requirements.evidence_available,
            "market_available": requirements.market_available,
            "evidence_type_defined": requirements.evidence_type_defined,
            "evidence_id_available": requirements.evidence_id_available,
            "symbol_available": requirements.symbol_available,
            "timestamp_available": requirements.timestamp_available,
            "source_available": requirements.source_available,
            "timeframe_available": requirements.timeframe_available,
            "session_available": requirements.session_available,
            "regime_available": requirements.regime_available,
            "data_state": requirements.data_state.value,
            "consistency": requirements.consistency.value,
            "readiness": requirements.readiness.value,
            "completeness_score": requirements.completeness_score,
            "warnings": list(requirements.warnings),
        },
        "assessment": {
            "readiness": assessment.readiness.value,
            "data_state": assessment.data_state.value,
            "consistency": assessment.consistency.value,
            "quality": assessment.quality.value,
            "confidence_score": assessment.confidence_score,
            "completeness_score": assessment.completeness_score,
            "strengths": list(assessment.strengths),
            "weaknesses": list(assessment.weaknesses),
            "rationale": assessment.rationale,
        },
        "action": {
            "state": result.action.state.value,
            "memory_id": result.action.memory_id,
            "rationale": result.action.rationale,
            "warnings": list(result.action.warnings),
            "is_action_request": result.action.is_action_request,
        },
        "rationale": result.rationale,
        "warnings": list(result.warnings),
        "created_at": _em_iso(result.created_at),
        "valid": result.is_valid,
        "stored": result.stored,
        "ready": evidence_memory_ready(result),
        "can_advance": evidence_memory_can_advance(result),
        "requires_review": evidence_memory_requires_review(result),
        "requires_hold": evidence_memory_requires_hold(result),
        "invalid": evidence_memory_is_invalid(result),
        "safe": evidence_memory_is_safe(result),
        "allows_execution": evidence_memory_allows_execution(result),
        "allows_trade": evidence_memory_allows_trade(result),
        "allows_order": evidence_memory_allows_order(result),
        "allows_position_change": evidence_memory_allows_position_change(result),
        "allows_authorization": evidence_memory_allows_authorization(result),
    }


def evidence_memory_integrity_check(
    result: Optional[EvidenceMemoryResult],
) -> dict[str, Any]:
    if result is None:
        return {
            "engine": EVIDENCE_MEMORY_ENGINE,
            "version": EVIDENCE_MEMORY_VERSION,
            "integrity": False,
            "errors": ["result_missing"],
        }

    errors: list[str] = []

    if not result.request_id.strip():
        errors.append("request_id_missing")

    if not result.result_id.strip():
        errors.append("result_id_missing")

    if result.memory is None:
        errors.append("memory_reference_missing")

    if result.requirements is None:
        errors.append("requirements_missing")

    if result.assessment is None:
        errors.append("assessment_missing")

    if result.action is None:
        errors.append("action_missing")

    if result.memory is not None:
        if not result.memory.memory_id.strip():
            errors.append("memory_id_missing")
        if not result.memory.evidence_id.strip():
            errors.append("evidence_id_missing")
        if not result.memory.market_name.strip():
            errors.append("market_missing")
        if result.memory.evidence_type == EvidenceMemoryType.UNKNOWN:
            errors.append("evidence_type_unknown")
        if result.memory.source_type == EvidenceMemorySourceType.UNKNOWN:
            errors.append("source_type_unknown")

    if result.requirements is not None:
        if (
            result.requirements.completeness_score < 0.0
            or result.requirements.completeness_score > 100.0
        ):
            errors.append("completeness_score_out_of_range")

    if result.assessment is not None:
        if (
            result.assessment.confidence_score < 0.0
            or result.assessment.confidence_score > 100.0
        ):
            errors.append("confidence_score_out_of_range")

    if result.status == EvidenceMemoryResultStatus.STORED:
        if not evidence_memory_ready(result):
            errors.append("stored_result_not_ready")

    return {
        "engine": EVIDENCE_MEMORY_ENGINE,
        "version": EVIDENCE_MEMORY_VERSION,
        "integrity": not errors,
        "errors": list(dict.fromkeys(errors)),
    }


def evidence_memory_summary(
    result: Optional[EvidenceMemoryResult],
) -> dict[str, Any]:
    if result is None:
        return {
            "engine": EVIDENCE_MEMORY_ENGINE,
            "version": EVIDENCE_MEMORY_VERSION,
            "status": EvidenceMemoryResultStatus.INVALID.value,
            "valid": False,
        }

    memory = result.memory
    assessment = result.assessment

    return {
        "engine": EVIDENCE_MEMORY_ENGINE,
        "version": EVIDENCE_MEMORY_VERSION,
        "memory_id": memory.memory_id if memory else None,
        "evidence_id": memory.evidence_id if memory else None,
        "market": memory.market_name if memory else None,
        "symbol": memory.symbol if memory else None,
        "evidence_type": (
            memory.evidence_type.value
            if memory
            else EvidenceMemoryType.UNKNOWN.value
        ),
        "status": result.status.value,
        "lifecycle": evidence_memory_lifecycle_state(result),
        "readiness": (
            assessment.readiness.value
            if assessment
            else EvidenceMemoryReadiness.UNKNOWN.value
        ),
        "quality": (
            assessment.quality.value
            if assessment
            else EvidenceMemoryQuality.UNKNOWN.value
        ),
        "confidence": (
            float(assessment.confidence_score)
            if assessment
            else 0.0
        ),
        "completeness": (
            float(assessment.completeness_score)
            if assessment
            else 0.0
        ),
        "ready": evidence_memory_ready(result),
        "can_advance": evidence_memory_can_advance(result),
        "requires_review": evidence_memory_requires_review(result),
        "requires_hold": evidence_memory_requires_hold(result),
        "invalid": evidence_memory_is_invalid(result),
        "safe": evidence_memory_is_safe(result),
    }


def evidence_memory_freeze(result: Optional[EvidenceMemoryResult]) -> bool:
    """
    Memory freeze is a lifecycle/read-only concept.
    It does not grant execution or authorization authority.
    """
    if result is None:
        return False
    if evidence_memory_is_invalid(result):
        return False
    return evidence_memory_ready(result)


def evidence_memory_retain(
    result: Optional[EvidenceMemoryResult],
) -> bool:
    if result is None:
        return False
    return (
        evidence_memory_is_stored(result)
        and not evidence_memory_is_invalid(result)
    )


def evidence_memory_reject(
    result: Optional[EvidenceMemoryResult],
) -> bool:
    return evidence_memory_is_invalid(result)


def evidence_memory_authority_statement() -> str:
    return (
        "Evidence Memory preserves, validates, assesses, and retrieves "
        "evidence-memory state. It is not decision authority, risk authority, "
        "CAS authority, execution authority, order authority, or authorization authority. "
        "D13, Risk, and CAS remain authoritative within their respective domains."
    )


__all__ = [
    "EVIDENCE_MEMORY_ENGINE",
    "EVIDENCE_MEMORY_VERSION",

    "EvidenceMemoryStatus",
    "EvidenceMemoryType",
    "EvidenceMemoryPriority",
    "EvidenceMemorySourceType",
    "EvidenceMemoryQuality",
    "EvidenceMemoryContractStatus",

    "EvidenceMemoryRequest",
    "EvidenceMemoryReference",
    "EvidenceMemorySourceReference",
    "EvidenceMemoryContractValidation",

    "EvidenceMemoryDataState",
    "EvidenceMemoryConsistency",
    "EvidenceMemoryReadiness",
    "EvidenceMemoryRequirements",
    "EvidenceMemoryAssessment",

    "EvidenceMemoryActionState",
    "EvidenceMemoryContractState",
    "EvidenceMemoryResultStatus",
    "EvidenceMemoryAction",
    "EvidenceMemoryResult",
    "EvidenceMemoryContract",

    "build_evidence_memory_reference",
    "validate_evidence_memory_request",
    "evaluate_evidence_memory_data_state",
    "evaluate_evidence_memory_consistency",
    "evaluate_evidence_memory_requirements",
    "evaluate_evidence_memory_readiness",
    "calculate_evidence_memory_confidence",
    "determine_evidence_memory_quality",
    "build_evidence_memory_assessment",

    "build_evidence_memory_action",
    "build_evidence_memory_result",
    "build_evidence_memory_contract",

    "EvidenceMemoryEngine",
    "evidence_memory_engine",
    "evaluate_evidence_memory",
    "analyze_evidence_memory",
    "review_evidence_memory",

    "validate_evidence_memory_result",
    "validate_evidence_memory_contract",
    "evidence_memory_ready",
    "evidence_memory_can_advance",
    "evidence_memory_status",
    "evidence_memory_type",
    "evidence_memory_readiness",
    "evidence_memory_confidence",
    "evidence_memory_quality",
    "evidence_memory_completeness",
    "evidence_memory_identity",
    "evidence_memory_audit",
    "evidence_memory_is_safe",

    "evidence_memory_allows_execution",
    "evidence_memory_allows_trade",
    "evidence_memory_allows_order",
    "evidence_memory_allows_position_change",
    "evidence_memory_allows_authorization",

    "evidence_memory_overrides_d13",
    "evidence_memory_overrides_risk",
    "evidence_memory_overrides_cas",

    "get_evidence_memory_engine_info",
    "evidence_memory_health_check",
    "run_evidence_memory_health_check",

    "evidence_memory_requires_review",
    "evidence_memory_requires_hold",
    "evidence_memory_is_invalid",
    "evidence_memory_is_stored",
    "evidence_memory_is_conditional",
    "evidence_memory_is_archived",
    "evidence_memory_lifecycle_state",

    "serialize_evidence_memory_reference",
    "serialize_evidence_memory_result",
    "evidence_memory_integrity_check",
    "evidence_memory_summary",

    "evidence_memory_freeze",
    "evidence_memory_retain",
    "evidence_memory_reject",
    "evidence_memory_authority_statement",
]