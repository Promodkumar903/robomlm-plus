# ============================================================
# ROBOMLM_PLUS
# DECISION MEMORY ENGINE
# FILE: app/intelligence/memory/decision_memory.py
# PART 1 / 5
# FOUNDATION + CONTRACTS + NORMALIZATION
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Optional
from uuid import uuid4


DECISION_MEMORY_ENGINE = "ROBOMLM_DECISION_MEMORY_ENGINE"
DECISION_MEMORY_VERSION = "1.0"


# ============================================================
# CORE ENUMS
# ============================================================

class DecisionMemoryStatus(str, Enum):
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


class DecisionMemoryType(str, Enum):
    DECISION = "DECISION"
    DECISION_STATE = "DECISION_STATE"
    DECISION_OUTLOOK = "DECISION_OUTLOOK"
    DECISION_VALIDATION = "DECISION_VALIDATION"
    DECISION_CONTEXT = "DECISION_CONTEXT"
    DECISION_TRANSITION = "DECISION_TRANSITION"
    DECISION_CONFLICT = "DECISION_CONFLICT"
    DECISION_OUTCOME = "DECISION_OUTCOME"
    DECISION_LEARNING = "DECISION_LEARNING"
    DECISION_PATTERN = "DECISION_PATTERN"
    UNKNOWN = "UNKNOWN"


class DecisionMemoryPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class DecisionMemorySourceType(str, Enum):
    DECISION_CORTEX = "DECISION_CORTEX"
    D13 = "D13"
    D14 = "D14"
    D15 = "D15"
    D16 = "D16"
    MARKET_CONTEXT = "MARKET_CONTEXT"
    EVIDENCE_CORTEX = "EVIDENCE_CORTEX"
    OUTCOME = "OUTCOME"
    RESEARCH = "RESEARCH"
    SYSTEM = "SYSTEM"
    UNKNOWN = "UNKNOWN"


class DecisionMemoryQuality(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class DecisionMemoryContractStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


# ============================================================
# REQUEST CONTRACT
# ============================================================

@dataclass(frozen=True)
class DecisionMemoryRequest:
    market: str
    decision_type: DecisionMemoryType = DecisionMemoryType.UNKNOWN
    source: str = ""
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    symbol: str = ""
    timeframe: str = ""
    session: str = ""
    regime: str = ""
    decision_id: str = ""
    decision_state: str = ""
    direction: str = ""
    confidence: Optional[float] = None
    priority: DecisionMemoryPriority = DecisionMemoryPriority.UNKNOWN
    metadata: Mapping[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: str(uuid4()))

    def validate(self) -> bool:
        if not self.market.strip():
            return False

        if not self.request_id.strip():
            return False

        if not isinstance(self.metadata, Mapping):
            return False

        if not isinstance(self.decision_type, DecisionMemoryType):
            return False

        if not isinstance(self.priority, DecisionMemoryPriority):
            return False

        if self.confidence is not None:
            try:
                score = float(self.confidence)
            except (TypeError, ValueError):
                return False

            if score < 0.0 or score > 100.0:
                return False

        return True


# ============================================================
# MEMORY REFERENCE
# ============================================================

@dataclass(frozen=True)
class DecisionMemoryReference:
    memory_id: str
    decision_id: str
    market_name: str
    symbol: str

    decision_type: DecisionMemoryType
    status: DecisionMemoryStatus
    priority: DecisionMemoryPriority

    timestamp: datetime

    timeframe: str
    session: str
    regime: str

    source_type: DecisionMemorySourceType

    decision_state: str = ""
    direction: str = ""
    confidence: Optional[float] = None

    decision: Mapping[str, Any] = field(default_factory=dict)


# ============================================================
# SOURCE REFERENCE
# ============================================================

@dataclass(frozen=True)
class DecisionMemorySourceReference:
    source_id: str
    source_name: str
    source_type: DecisionMemorySourceType

    timestamp: Optional[datetime] = None

    provenance: str = ""
    description: str = ""

    raw_source: Mapping[str, Any] = field(default_factory=dict)


# ============================================================
# CONTRACT VALIDATION
# ============================================================

@dataclass(frozen=True)
class DecisionMemoryContractValidation:
    valid: bool

    market_available: bool
    decision_type_defined: bool
    priority_defined: bool

    metadata_valid: bool
    timestamp_valid: bool

    decision_id_available: bool
    decision_state_available: bool
    direction_available: bool
    confidence_valid: bool

    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:
        return self.valid


# ============================================================
# NORMALIZATION HELPERS
# ============================================================

def _dm_read_value(
    source: Any,
    key: str,
    default: Any = None,
) -> Any:
    if source is None:
        return default

    if isinstance(source, Mapping):
        return source.get(key, default)

    return getattr(source, key, default)


def _dm_text(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip()


def _dm_timestamp(value: Any) -> Optional[datetime]:
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


def _dm_float(value: Any) -> Optional[float]:
    if value is None:
        return None

    try:
        score = float(value)
    except (TypeError, ValueError):
        return None

    if score < 0.0 or score > 100.0:
        return None

    return score


def _dm_enum(
    value: Any,
    enum_type: type[Enum],
    default: Enum,
) -> Enum:
    if isinstance(value, enum_type):
        return value

    if value is None:
        return default

    text = _dm_text(value)

    if not text:
        return default

    for member in enum_type:
        if member.value.upper() == text.upper():
            return member

    return default


# ============================================================
# DECISION MEMORY REFERENCE BUILDER
# ============================================================

def build_decision_memory_reference(
    decision: Any,
    request: Optional[DecisionMemoryRequest] = None,
) -> DecisionMemoryReference:

    market = _dm_text(
        _dm_read_value(
            decision,
            "market",
            request.market if request else "",
        )
    )

    symbol = _dm_text(
        _dm_read_value(
            decision,
            "symbol",
            request.symbol if request else "",
        )
    )

    decision_id = _dm_text(
        _dm_read_value(
            decision,
            "decision_id",
            request.decision_id if request else "",
        )
    )

    if not decision_id:
        decision_id = str(uuid4())

    memory_id = str(uuid4())

    timestamp = _dm_timestamp(
        _dm_read_value(
            decision,
            "timestamp",
            request.timestamp if request else None,
        )
    )

    if timestamp is None:
        timestamp = datetime.now(timezone.utc)

    decision_type = _dm_enum(
        _dm_read_value(
            decision,
            "decision_type",
            request.decision_type if request else None,
        ),
        DecisionMemoryType,
        DecisionMemoryType.UNKNOWN,
    )

    priority = _dm_enum(
        _dm_read_value(
            decision,
            "priority",
            request.priority if request else None,
        ),
        DecisionMemoryPriority,
        DecisionMemoryPriority.UNKNOWN,
    )

    source_type = _dm_enum(
        _dm_read_value(
            decision,
            "source_type",
            DecisionMemorySourceType.DECISION_CORTEX,
        ),
        DecisionMemorySourceType,
        DecisionMemorySourceType.UNKNOWN,
    )

    status = _dm_enum(
        _dm_read_value(
            decision,
            "status",
            DecisionMemoryStatus.NEW,
        ),
        DecisionMemoryStatus,
        DecisionMemoryStatus.NEW,
    )

    confidence = _dm_float(
        _dm_read_value(
            decision,
            "confidence",
            request.confidence if request else None,
        )
    )

    raw_decision = (
        dict(decision)
        if isinstance(decision, Mapping)
        else {}
    )

    return DecisionMemoryReference(
        memory_id=memory_id,
        decision_id=decision_id,
        market_name=market,
        symbol=symbol,
        decision_type=decision_type,
        status=status,
        priority=priority,
        timestamp=timestamp,
        timeframe=_dm_text(
            _dm_read_value(
                decision,
                "timeframe",
                request.timeframe if request else "",
            )
        ),
        session=_dm_text(
            _dm_read_value(
                decision,
                "session",
                request.session if request else "",
            )
        ),
        regime=_dm_text(
            _dm_read_value(
                decision,
                "regime",
                request.regime if request else "",
            )
        ),
        source_type=source_type,
        decision_state=_dm_text(
            _dm_read_value(
                decision,
                "decision_state",
                request.decision_state if request else "",
            )
        ),
        direction=_dm_text(
            _dm_read_value(
                decision,
                "direction",
                request.direction if request else "",
            )
        ),
        confidence=confidence,
        decision=raw_decision,
    )


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_decision_memory_request(
    request: Optional[DecisionMemoryRequest],
) -> DecisionMemoryContractValidation:

    errors: list[str] = []
    warnings: list[str] = []

    if request is None:
        return DecisionMemoryContractValidation(
            valid=False,
            market_available=False,
            decision_type_defined=False,
            priority_defined=False,
            metadata_valid=False,
            timestamp_valid=False,
            decision_id_available=False,
            decision_state_available=False,
            direction_available=False,
            confidence_valid=False,
            errors=("decision_memory_request_missing",),
            warnings=(),
        )

    market_available = bool(request.market.strip())

    decision_type_defined = (
        request.decision_type != DecisionMemoryType.UNKNOWN
    )

    priority_defined = (
        request.priority != DecisionMemoryPriority.UNKNOWN
    )

    metadata_valid = isinstance(
        request.metadata,
        Mapping,
    )

    timestamp_valid = (
        _dm_timestamp(request.timestamp) is not None
    )

    decision_id_available = bool(
        request.decision_id.strip()
    )

    decision_state_available = bool(
        request.decision_state.strip()
    )

    direction_available = bool(
        request.direction.strip()
    )

    confidence_valid = True

    if request.confidence is not None:
        confidence_valid = (
            _dm_float(request.confidence) is not None
        )

    if not market_available:
        errors.append("market_missing")

    if not decision_type_defined:
        warnings.append("decision_type_undefined")

    if not priority_defined:
        warnings.append("priority_undefined")

    if not metadata_valid:
        errors.append("metadata_invalid")

    if not timestamp_valid:
        errors.append("timestamp_invalid")

    if not request.request_id.strip():
        errors.append("request_id_missing")

    if not confidence_valid:
        errors.append("confidence_invalid")

    if not decision_id_available:
        warnings.append("decision_id_missing")

    if not decision_state_available:
        warnings.append("decision_state_missing")

    if not direction_available:
        warnings.append("direction_missing")

    return DecisionMemoryContractValidation(
        valid=not errors,
        market_available=market_available,
        decision_type_defined=decision_type_defined,
        priority_defined=priority_defined,
        metadata_valid=metadata_valid,
        timestamp_valid=timestamp_valid,
        decision_id_available=decision_id_available,
        decision_state_available=decision_state_available,
        direction_available=direction_available,
        confidence_valid=confidence_valid,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )
# ============================================================
# ROBOMLM_PLUS
# DECISION MEMORY ENGINE
# FILE: app/intelligence/memory/decision_memory.py
# PART 2 / 5
# STRUCTURAL REQUIREMENTS + CONSISTENCY + ASSESSMENT
# ============================================================


# ============================================================
# DATA / CONSISTENCY / READINESS ENUMS
# ============================================================

class DecisionMemoryDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    UNKNOWN = "UNKNOWN"


class DecisionMemoryConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONFLICTING = "CONFLICTING"
    INSUFFICIENT = "INSUFFICIENT"
    UNKNOWN = "UNKNOWN"


class DecisionMemoryReadiness(str, Enum):
    READY = "READY"
    CONDITIONAL = "CONDITIONAL"
    NOT_READY = "NOT_READY"
    UNKNOWN = "UNKNOWN"


# ============================================================
# REQUIREMENTS CONTRACT
# ============================================================

@dataclass(frozen=True)
class DecisionMemoryRequirements:
    memory_available: bool
    decision_available: bool
    market_available: bool

    decision_type_defined: bool
    decision_id_available: bool
    symbol_available: bool

    timestamp_available: bool
    source_available: bool

    decision_state_available: bool
    direction_available: bool
    confidence_available: bool

    timeframe_available: bool
    session_available: bool
    regime_available: bool

    data_state: DecisionMemoryDataState
    consistency: DecisionMemoryConsistency
    readiness: DecisionMemoryReadiness

    completeness_score: float = 0.0
    warnings: tuple[str, ...] = ()


# ============================================================
# ASSESSMENT CONTRACT
# ============================================================

@dataclass(frozen=True)
class DecisionMemoryAssessment:
    readiness: DecisionMemoryReadiness
    data_state: DecisionMemoryDataState
    consistency: DecisionMemoryConsistency
    quality: DecisionMemoryQuality

    confidence_score: float
    completeness_score: float

    strengths: tuple[str, ...] = ()
    weaknesses: tuple[str, ...] = ()

    rationale: str = ""


# ============================================================
# BOOLEAN NORMALIZATION
# ============================================================

def _dm_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    if value is None:
        return False

    if isinstance(value, (int, float)):
        return value != 0

    text = _dm_text(value).lower()

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
        "confirmed",
    }


# ============================================================
# CONFLICT DETECTION
# ============================================================

def _dm_conflict_detected(source: Any) -> bool:
    candidates = (
        "conflict",
        "conflicted",
        "conflicting",
        "has_conflict",
        "decision_conflict",
        "decision_conflicted",
        "consistency_conflict",
    )

    for key in candidates:
        value = _dm_read_value(source, key, None)

        if _dm_bool(value):
            return True

    consistency = _dm_text(
        _dm_read_value(
            source,
            "consistency",
            "",
        )
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

def evaluate_decision_memory_data_state(
    reference: Optional[DecisionMemoryReference],
) -> DecisionMemoryDataState:

    if reference is None:
        return DecisionMemoryDataState.MISSING

    components = (
        bool(reference.memory_id),
        bool(reference.decision_id),
        bool(reference.market_name),
        reference.decision_type != DecisionMemoryType.UNKNOWN,
        bool(reference.symbol),
        reference.timestamp is not None,
        reference.source_type != DecisionMemorySourceType.UNKNOWN,
        bool(reference.decision_state),
        bool(reference.direction),
        reference.confidence is not None,
    )

    available = sum(components)

    if available == len(components):
        return DecisionMemoryDataState.COMPLETE

    if available == 0:
        return DecisionMemoryDataState.MISSING

    return DecisionMemoryDataState.PARTIAL


# ============================================================
# CONSISTENCY EVALUATION
# ============================================================

def evaluate_decision_memory_consistency(
    decision: Any,
) -> DecisionMemoryConsistency:

    if decision is None:
        return DecisionMemoryConsistency.INSUFFICIENT

    if _dm_conflict_detected(decision):
        return DecisionMemoryConsistency.CONFLICTING

    consistency = _dm_text(
        _dm_read_value(
            decision,
            "consistency",
            "",
        )
    ).lower()

    if consistency in {
        "consistent",
        "valid",
        "aligned",
        "pass",
        "passed",
        "confirmed",
    }:
        return DecisionMemoryConsistency.CONSISTENT

    if consistency in {
        "conflicting",
        "conflict",
        "contradictory",
        "contradiction",
    }:
        return DecisionMemoryConsistency.CONFLICTING

    if consistency in {
        "insufficient",
        "unknown",
        "unavailable",
        "missing",
    }:
        return DecisionMemoryConsistency.INSUFFICIENT

    return DecisionMemoryConsistency.UNKNOWN


# ============================================================
# REQUIREMENTS EVALUATION
# ============================================================

def evaluate_decision_memory_requirements(
    reference: Optional[DecisionMemoryReference],
    decision: Any = None,
) -> DecisionMemoryRequirements:

    if reference is None:
        return DecisionMemoryRequirements(
            memory_available=False,
            decision_available=False,
            market_available=False,
            decision_type_defined=False,
            decision_id_available=False,
            symbol_available=False,
            timestamp_available=False,
            source_available=False,
            decision_state_available=False,
            direction_available=False,
            confidence_available=False,
            timeframe_available=False,
            session_available=False,
            regime_available=False,
            data_state=DecisionMemoryDataState.MISSING,
            consistency=DecisionMemoryConsistency.INSUFFICIENT,
            readiness=DecisionMemoryReadiness.NOT_READY,
            completeness_score=0.0,
            warnings=("decision_memory_reference_missing",),
        )

    memory_available = bool(reference.memory_id)

    decision_available = bool(reference.decision)

    market_available = bool(reference.market_name)

    decision_type_defined = (
        reference.decision_type != DecisionMemoryType.UNKNOWN
    )

    decision_id_available = bool(
        reference.decision_id
    )

    symbol_available = bool(
        reference.symbol
    )

    timestamp_available = (
        reference.timestamp is not None
    )

    source_available = (
        reference.source_type
        != DecisionMemorySourceType.UNKNOWN
    )

    decision_state_available = bool(
        reference.decision_state
    )

    direction_available = bool(
        reference.direction
    )

    confidence_available = (
        reference.confidence is not None
    )

    timeframe_available = bool(
        reference.timeframe
    )

    session_available = bool(
        reference.session
    )

    regime_available = bool(
        reference.regime
    )

    data_state = evaluate_decision_memory_data_state(
        reference
    )

    consistency = evaluate_decision_memory_consistency(
        decision if decision is not None else reference.decision
    )

    completeness_components = (
        memory_available,
        decision_available,
        market_available,
        decision_type_defined,
        decision_id_available,
        symbol_available,
        timestamp_available,
        source_available,
        decision_state_available,
        direction_available,
        confidence_available,
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

    if not decision_available:
        warnings.append("decision_payload_missing")

    if not symbol_available:
        warnings.append("symbol_missing")

    if not timestamp_available:
        warnings.append("timestamp_missing")

    if not source_available:
        warnings.append("source_missing")

    if not decision_state_available:
        warnings.append("decision_state_missing")

    if not direction_available:
        warnings.append("direction_missing")

    if not confidence_available:
        warnings.append("confidence_missing")

    if not timeframe_available:
        warnings.append("timeframe_missing")

    if not session_available:
        warnings.append("session_missing")

    if not regime_available:
        warnings.append("regime_missing")

    if consistency == DecisionMemoryConsistency.CONFLICTING:
        warnings.append("decision_conflict_detected")

    # --------------------------------------------------------
    # READINESS
    # --------------------------------------------------------

    if (
        data_state == DecisionMemoryDataState.COMPLETE
        and consistency != DecisionMemoryConsistency.CONFLICTING
    ):
        readiness = DecisionMemoryReadiness.READY

    elif data_state == DecisionMemoryDataState.PARTIAL:
        readiness = DecisionMemoryReadiness.CONDITIONAL

    elif data_state == DecisionMemoryDataState.MISSING:
        readiness = DecisionMemoryReadiness.NOT_READY

    else:
        readiness = DecisionMemoryReadiness.UNKNOWN

    if consistency == DecisionMemoryConsistency.CONFLICTING:
        readiness = DecisionMemoryReadiness.NOT_READY

    return DecisionMemoryRequirements(
        memory_available=memory_available,
        decision_available=decision_available,
        market_available=market_available,
        decision_type_defined=decision_type_defined,
        decision_id_available=decision_id_available,
        symbol_available=symbol_available,
        timestamp_available=timestamp_available,
        source_available=source_available,
        decision_state_available=decision_state_available,
        direction_available=direction_available,
        confidence_available=confidence_available,
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
# READINESS
# ============================================================

def evaluate_decision_memory_readiness(
    requirements: DecisionMemoryRequirements,
) -> DecisionMemoryReadiness:

    if (
        requirements.consistency
        == DecisionMemoryConsistency.CONFLICTING
    ):
        return DecisionMemoryReadiness.NOT_READY

    if (
        requirements.data_state
        == DecisionMemoryDataState.COMPLETE
    ):
        return DecisionMemoryReadiness.READY

    if (
        requirements.data_state
        == DecisionMemoryDataState.PARTIAL
    ):
        return DecisionMemoryReadiness.CONDITIONAL

    if (
        requirements.data_state
        == DecisionMemoryDataState.MISSING
    ):
        return DecisionMemoryReadiness.NOT_READY

    return DecisionMemoryReadiness.UNKNOWN


# ============================================================
# CONFIDENCE
# ============================================================

def calculate_decision_memory_confidence(
    requirements: DecisionMemoryRequirements,
) -> float:

    score = float(
        requirements.completeness_score
    )

    if (
        requirements.consistency
        == DecisionMemoryConsistency.CONSISTENT
    ):
        score += 5.0

    elif (
        requirements.consistency
        == DecisionMemoryConsistency.CONFLICTING
    ):
        score -= 30.0

    elif (
        requirements.consistency
        == DecisionMemoryConsistency.INSUFFICIENT
    ):
        score -= 10.0

    if (
        requirements.data_state
        == DecisionMemoryDataState.MISSING
    ):
        score -= 20.0

    return max(
        0.0,
        min(100.0, score),
    )


# ============================================================
# QUALITY
# ============================================================

def determine_decision_memory_quality(
    confidence_score: float,
    consistency: DecisionMemoryConsistency,
) -> DecisionMemoryQuality:

    if consistency == DecisionMemoryConsistency.CONFLICTING:
        return DecisionMemoryQuality.LOW

    if confidence_score >= 90.0:
        return DecisionMemoryQuality.CRITICAL

    if confidence_score >= 75.0:
        return DecisionMemoryQuality.HIGH

    if confidence_score >= 50.0:
        return DecisionMemoryQuality.MODERATE

    if confidence_score > 0.0:
        return DecisionMemoryQuality.LOW

    return DecisionMemoryQuality.UNKNOWN


# ============================================================
# ASSESSMENT BUILDER
# ============================================================

def build_decision_memory_assessment(
    requirements: DecisionMemoryRequirements,
) -> DecisionMemoryAssessment:

    readiness = evaluate_decision_memory_readiness(
        requirements
    )

    confidence_score = calculate_decision_memory_confidence(
        requirements
    )

    quality = determine_decision_memory_quality(
        confidence_score,
        requirements.consistency,
    )

    strengths: list[str] = []
    weaknesses: list[str] = []

    if requirements.memory_available:
        strengths.append("memory_identity_available")

    if requirements.decision_available:
        strengths.append("decision_payload_available")

    if requirements.market_available:
        strengths.append("market_available")

    if requirements.decision_type_defined:
        strengths.append("decision_type_defined")

    if requirements.decision_id_available:
        strengths.append("decision_id_available")

    if requirements.decision_state_available:
        strengths.append("decision_state_available")

    if requirements.direction_available:
        strengths.append("direction_available")

    if requirements.confidence_available:
        strengths.append("confidence_available")

    if requirements.source_available:
        strengths.append("source_available")

    if (
        requirements.consistency
        == DecisionMemoryConsistency.CONSISTENT
    ):
        strengths.append("decision_consistency_confirmed")

    if not requirements.symbol_available:
        weaknesses.append("symbol_missing")

    if not requirements.timestamp_available:
        weaknesses.append("timestamp_missing")

    if not requirements.source_available:
        weaknesses.append("source_missing")

    if not requirements.decision_available:
        weaknesses.append("decision_payload_missing")

    if not requirements.decision_state_available:
        weaknesses.append("decision_state_missing")

    if not requirements.direction_available:
        weaknesses.append("direction_missing")

    if not requirements.confidence_available:
        weaknesses.append("confidence_missing")

    if (
        requirements.consistency
        == DecisionMemoryConsistency.CONFLICTING
    ):
        weaknesses.append("decision_conflict_detected")

    if readiness == DecisionMemoryReadiness.READY:
        rationale = (
            "Decision memory has complete structural "
            "requirements and no detected decision conflict."
        )

    elif readiness == DecisionMemoryReadiness.CONDITIONAL:
        rationale = (
            "Decision memory is structurally partial "
            "and may require additional decision context "
            "before full readiness."
        )

    elif readiness == DecisionMemoryReadiness.NOT_READY:
        rationale = (
            "Decision memory is not ready because required "
            "structure is missing or decision consistency "
            "is unacceptable."
        )

    else:
        rationale = (
            "Decision memory readiness could not be determined."
        )

    return DecisionMemoryAssessment(
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
# ROBOMLM_PLUS
# DECISION MEMORY ENGINE
# FILE: app/intelligence/memory/decision_memory.py
# PART 3 / 5
# ACTION + RESULT + CONTRACT + ENGINE
# ============================================================


# ============================================================
# ACTION STATE
# ============================================================

class DecisionMemoryActionState(str, Enum):
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

class DecisionMemoryContractState(str, Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


# ============================================================
# RESULT STATUS
# ============================================================

class DecisionMemoryResultStatus(str, Enum):
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
class DecisionMemoryAction:
    state: DecisionMemoryActionState
    memory_id: str = ""
    rationale: str = ""
    warnings: tuple[str, ...] = ()

    @property
    def is_action_request(self) -> bool:
        # Memory lifecycle instruction is NOT an execution request.
        return False


# ============================================================
# RESULT CONTRACT
# ============================================================

@dataclass(frozen=True)
class DecisionMemoryResult:
    request_id: str
    result_id: str

    status: DecisionMemoryResultStatus

    memory: Optional[DecisionMemoryReference]

    requirements: DecisionMemoryRequirements
    assessment: DecisionMemoryAssessment

    action: DecisionMemoryAction

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
            and self.status != DecisionMemoryResultStatus.INVALID
        )

    @property
    def stored(self) -> bool:
        return (
            self.is_valid
            and self.status == DecisionMemoryResultStatus.STORED
        )

    @property
    def is_conditional(self) -> bool:
        return (
            self.status
            == DecisionMemoryResultStatus.CONDITIONAL
        )

    @property
    def requires_review(self) -> bool:
        return (
            self.status
            == DecisionMemoryResultStatus.REVIEW
            or self.action.state
            == DecisionMemoryActionState.REVIEW
        )

    @property
    def requires_hold(self) -> bool:
        return (
            self.status
            == DecisionMemoryResultStatus.HOLD
            or self.action.state
            == DecisionMemoryActionState.HOLD
        )

    @property
    def is_invalidated(self) -> bool:
        return (
            self.status
            == DecisionMemoryResultStatus.INVALIDATED
            or self.action.state
            == DecisionMemoryActionState.INVALIDATE
        )

    @property
    def is_action_request(self) -> bool:
        return False


# ============================================================
# CONTRACT
# ============================================================

@dataclass(frozen=True)
class DecisionMemoryContract:
    request_id: str
    contract_id: str

    state: DecisionMemoryContractState

    result: DecisionMemoryResult

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
            and self.state != DecisionMemoryContractState.INVALID
        )

    @property
    def stored(self) -> bool:
        return (
            self.is_valid
            and self.state == DecisionMemoryContractState.COMPLETE
            and self.result.stored
        )

    @property
    def is_action_request(self) -> bool:
        return False


# ============================================================
# RESULT STATUS DETERMINATION
# ============================================================

def _determine_decision_memory_result_status(
    assessment: DecisionMemoryAssessment,
) -> DecisionMemoryResultStatus:

    if (
        assessment.consistency
        == DecisionMemoryConsistency.CONFLICTING
    ):
        return DecisionMemoryResultStatus.INVALIDATED

    if (
        assessment.readiness
        == DecisionMemoryReadiness.READY
    ):
        return DecisionMemoryResultStatus.STORED

    if (
        assessment.readiness
        == DecisionMemoryReadiness.CONDITIONAL
    ):
        return DecisionMemoryResultStatus.CONDITIONAL

    if (
        assessment.readiness
        == DecisionMemoryReadiness.NOT_READY
    ):
        return DecisionMemoryResultStatus.HOLD

    return DecisionMemoryResultStatus.REVIEW


# ============================================================
# ACTION BUILDER
# ============================================================

def build_decision_memory_action(
    status: DecisionMemoryResultStatus,
    memory_id: str = "",
) -> DecisionMemoryAction:

    if status == DecisionMemoryResultStatus.STORED:
        return DecisionMemoryAction(
            state=DecisionMemoryActionState.STORE,
            memory_id=memory_id,
            rationale=(
                "Decision memory is structurally ready "
                "for storage."
            ),
        )

    if status in (
        DecisionMemoryResultStatus.CONDITIONAL,
        DecisionMemoryResultStatus.REVIEW,
    ):
        return DecisionMemoryAction(
            state=DecisionMemoryActionState.REVIEW,
            memory_id=memory_id,
            rationale=(
                "Decision memory requires additional "
                "validation or decision context."
            ),
        )

    if status == DecisionMemoryResultStatus.HOLD:
        return DecisionMemoryAction(
            state=DecisionMemoryActionState.HOLD,
            memory_id=memory_id,
            rationale=(
                "Decision memory is not ready for progression."
            ),
        )

    if status == DecisionMemoryResultStatus.INVALIDATED:
        return DecisionMemoryAction(
            state=DecisionMemoryActionState.INVALIDATE,
            memory_id=memory_id,
            rationale=(
                "Decision conflict prevents trusted "
                "memory use."
            ),
        )

    if status == DecisionMemoryResultStatus.ARCHIVED:
        return DecisionMemoryAction(
            state=DecisionMemoryActionState.ARCHIVE,
            memory_id=memory_id,
            rationale="Decision memory is archived.",
        )

    return DecisionMemoryAction(
        state=DecisionMemoryActionState.NONE,
        memory_id=memory_id,
        rationale="No decision memory lifecycle action.",
    )


# ============================================================
# RESULT BUILDER
# ============================================================

def build_decision_memory_result(
    request: DecisionMemoryRequest,
    reference: Optional[DecisionMemoryReference],
    requirements: DecisionMemoryRequirements,
    assessment: DecisionMemoryAssessment,
) -> DecisionMemoryResult:

    status = _determine_decision_memory_result_status(
        assessment
    )

    memory_id = (
        reference.memory_id
        if reference is not None
        else ""
    )

    action = build_decision_memory_action(
        status,
        memory_id,
    )

    warnings = list(requirements.warnings)

    if assessment.weaknesses:
        warnings.extend(
            assessment.weaknesses
        )

    return DecisionMemoryResult(
        request_id=request.request_id,
        result_id=str(uuid4()),
        status=status,
        memory=reference,
        requirements=requirements,
        assessment=assessment,
        action=action,
        rationale=assessment.rationale,
        warnings=tuple(
            dict.fromkeys(warnings)
        ),
    )


# ============================================================
# CONTRACT STATE
# ============================================================

def _determine_decision_memory_contract_state(
    result: DecisionMemoryResult,
) -> DecisionMemoryContractState:

    if not result.is_valid:
        return DecisionMemoryContractState.INVALID

    if (
        result.status
        == DecisionMemoryResultStatus.INVALIDATED
    ):
        return DecisionMemoryContractState.BLOCKED

    if (
        result.requirements.data_state
        == DecisionMemoryDataState.COMPLETE
        and result.requirements.readiness
        == DecisionMemoryReadiness.READY
        and result.requirements.consistency
        != DecisionMemoryConsistency.CONFLICTING
    ):
        return DecisionMemoryContractState.COMPLETE

    if (
        result.requirements.data_state
        == DecisionMemoryDataState.MISSING
    ):
        return DecisionMemoryContractState.INCOMPLETE

    return DecisionMemoryContractState.INCOMPLETE


# ============================================================
# CONTRACT BUILDER
# ============================================================

def build_decision_memory_contract(
    result: DecisionMemoryResult,
) -> DecisionMemoryContract:

    state = _determine_decision_memory_contract_state(
        result
    )

    warnings = list(result.warnings)

    if state == DecisionMemoryContractState.BLOCKED:
        warnings.append(
            "decision_memory_contract_blocked"
        )

    if state == DecisionMemoryContractState.INCOMPLETE:
        warnings.append(
            "decision_memory_contract_incomplete"
        )

    return DecisionMemoryContract(
        request_id=result.request_id,
        contract_id=str(uuid4()),
        state=state,
        result=result,
        rationale=result.rationale,
        warnings=tuple(
            dict.fromkeys(warnings)
        ),
    )


# ============================================================
# ENGINE
# ============================================================

class DecisionMemoryEngine:

    name = DECISION_MEMORY_ENGINE
    version = DECISION_MEMORY_VERSION

    def validate_request(
        self,
        request: Optional[DecisionMemoryRequest],
    ) -> DecisionMemoryContractValidation:
        return validate_decision_memory_request(
            request
        )

    def _invalid_result(
        self,
        request: DecisionMemoryRequest,
        validation: DecisionMemoryContractValidation,
    ) -> DecisionMemoryResult:

        requirements = DecisionMemoryRequirements(
            memory_available=False,
            decision_available=False,
            market_available=validation.market_available,
            decision_type_defined=(
                validation.decision_type_defined
            ),
            decision_id_available=(
                validation.decision_id_available
            ),
            symbol_available=False,
            timestamp_available=(
                validation.timestamp_valid
            ),
            source_available=False,
            decision_state_available=(
                validation.decision_state_available
            ),
            direction_available=(
                validation.direction_available
            ),
            confidence_available=(
                validation.confidence_valid
            ),
            timeframe_available=False,
            session_available=False,
            regime_available=False,
            data_state=DecisionMemoryDataState.MISSING,
            consistency=(
                DecisionMemoryConsistency.INSUFFICIENT
            ),
            readiness=(
                DecisionMemoryReadiness.NOT_READY
            ),
            completeness_score=0.0,
            warnings=validation.warnings,
        )

        assessment = DecisionMemoryAssessment(
            readiness=DecisionMemoryReadiness.NOT_READY,
            data_state=DecisionMemoryDataState.MISSING,
            consistency=DecisionMemoryConsistency.INSUFFICIENT,
            quality=DecisionMemoryQuality.UNKNOWN,
            confidence_score=0.0,
            completeness_score=0.0,
            strengths=(),
            weaknesses=tuple(
                validation.errors
            ),
            rationale="Invalid decision memory request.",
        )

        action = DecisionMemoryAction(
            state=DecisionMemoryActionState.HOLD,
            rationale=(
                "Invalid decision memory request."
            ),
            warnings=tuple(
                validation.errors
            ),
        )

        return DecisionMemoryResult(
            request_id=request.request_id,
            result_id=str(uuid4()),
            status=DecisionMemoryResultStatus.INVALID,
            memory=None,
            requirements=requirements,
            assessment=assessment,
            action=action,
            rationale=(
                "Decision memory request validation failed."
            ),
            warnings=tuple(
                validation.errors
            ),
        )

    # --------------------------------------------------------
    # EVALUATE
    # --------------------------------------------------------

    def evaluate(
        self,
        request: DecisionMemoryRequest,
        decision: Any = None,
    ) -> DecisionMemoryContract:

        validation = self.validate_request(
            request
        )

        if not validation.valid:
            result = self._invalid_result(
                request,
                validation,
            )

            return build_decision_memory_contract(
                result
            )

        reference = build_decision_memory_reference(
            decision,
            request,
        )

        requirements = (
            evaluate_decision_memory_requirements(
                reference,
                decision,
            )
        )

        assessment = (
            build_decision_memory_assessment(
                requirements
            )
        )

        result = build_decision_memory_result(
            request=request,
            reference=reference,
            requirements=requirements,
            assessment=assessment,
        )

        return build_decision_memory_contract(
            result
        )


# ============================================================
# SINGLETON ENGINE
# ============================================================

decision_memory_engine = DecisionMemoryEngine()


# ============================================================
# PUBLIC OPERATIONS
# ============================================================

def evaluate_decision_memory(
    request: DecisionMemoryRequest,
    decision: Any = None,
) -> DecisionMemoryContract:
    return decision_memory_engine.evaluate(
        request,
        decision,
    )


def analyze_decision_memory(
    request: DecisionMemoryRequest,
    decision: Any = None,
) -> DecisionMemoryContract:
    return evaluate_decision_memory(
        request,
        decision,
    )


def review_decision_memory(
    request: DecisionMemoryRequest,
    decision: Any = None,
) -> DecisionMemoryContract:
    return evaluate_decision_memory(
        request,
        decision,
    )
# ============================================================
# ROBOMLM_PLUS
# DECISION MEMORY ENGINE
# FILE: app/intelligence/memory/decision_memory.py
# PART 4 / 5
# VALIDATION + READINESS + AUDIT + SAFETY + HEALTH
# ============================================================


# ============================================================
# RESULT VALIDATION
# ============================================================

def validate_decision_memory_result(
    result: Optional[DecisionMemoryResult],
) -> DecisionMemoryContractValidation:

    errors: list[str] = []
    warnings: list[str] = []

    if result is None:
        return DecisionMemoryContractValidation(
            valid=False,
            market_available=False,
            decision_type_defined=False,
            priority_defined=False,
            metadata_valid=False,
            timestamp_valid=False,
            decision_id_available=False,
            decision_state_available=False,
            direction_available=False,
            confidence_valid=False,
            errors=("decision_memory_result_missing",),
            warnings=(),
        )

    if not result.request_id.strip():
        errors.append("request_id_missing")

    if not result.result_id.strip():
        errors.append("result_id_missing")

    if result.memory is None:
        errors.append("memory_reference_missing")

        return DecisionMemoryContractValidation(
            valid=False,
            market_available=False,
            decision_type_defined=False,
            priority_defined=False,
            metadata_valid=False,
            timestamp_valid=False,
            decision_id_available=False,
            decision_state_available=False,
            direction_available=False,
            confidence_valid=False,
            errors=tuple(errors),
            warnings=tuple(warnings),
        )

    memory = result.memory

    market_available = bool(
        memory.market_name.strip()
    )

    decision_type_defined = (
        memory.decision_type
        != DecisionMemoryType.UNKNOWN
    )

    priority_defined = (
        memory.priority
        != DecisionMemoryPriority.UNKNOWN
    )

    metadata_valid = isinstance(
        memory.decision,
        Mapping,
    )

    timestamp_valid = (
        _dm_timestamp(memory.timestamp) is not None
    )

    decision_id_available = bool(
        memory.decision_id.strip()
    )

    decision_state_available = bool(
        memory.decision_state.strip()
    )

    direction_available = bool(
        memory.direction.strip()
    )

    confidence_valid = (
        memory.confidence is None
        or (
            0.0
            <= float(memory.confidence)
            <= 100.0
        )
    )

    if not market_available:
        errors.append("market_name_missing")

    if not decision_type_defined:
        errors.append("decision_type_undefined")

    if not priority_defined:
        warnings.append("priority_undefined")

    if not metadata_valid:
        errors.append("decision_payload_invalid")

    if not timestamp_valid:
        errors.append("timestamp_invalid")

    if not decision_id_available:
        errors.append("decision_id_missing")

    if not decision_state_available:
        warnings.append("decision_state_missing")

    if not direction_available:
        warnings.append("direction_missing")

    if not confidence_valid:
        errors.append("confidence_invalid")

    if result.status == DecisionMemoryResultStatus.INVALID:
        errors.append("result_status_invalid")

    return DecisionMemoryContractValidation(
        valid=not errors,
        market_available=market_available,
        decision_type_defined=decision_type_defined,
        priority_defined=priority_defined,
        metadata_valid=metadata_valid,
        timestamp_valid=timestamp_valid,
        decision_id_available=decision_id_available,
        decision_state_available=decision_state_available,
        direction_available=direction_available,
        confidence_valid=confidence_valid,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


# ============================================================
# CONTRACT VALIDATION
# ============================================================

def validate_decision_memory_contract(
    contract: Optional[DecisionMemoryContract],
) -> DecisionMemoryContractValidation:

    errors: list[str] = []
    warnings: list[str] = []

    if contract is None:
        return DecisionMemoryContractValidation(
            valid=False,
            market_available=False,
            decision_type_defined=False,
            priority_defined=False,
            metadata_valid=False,
            timestamp_valid=False,
            decision_id_available=False,
            decision_state_available=False,
            direction_available=False,
            confidence_valid=False,
            errors=("decision_memory_contract_missing",),
            warnings=(),
        )

    if not contract.request_id.strip():
        errors.append("request_id_missing")

    if not contract.contract_id.strip():
        errors.append("contract_id_missing")

    if _dm_timestamp(contract.created_at) is None:
        errors.append("created_at_invalid")

    result_validation = (
        validate_decision_memory_result(
            contract.result
        )
    )

    errors.extend(
        result_validation.errors
    )

    warnings.extend(
        result_validation.warnings
    )

    if contract.state == DecisionMemoryContractState.INVALID:
        errors.append("contract_state_invalid")

    if (
        contract.state == DecisionMemoryContractState.COMPLETE
        and not contract.result.stored
    ):
        errors.append(
            "complete_contract_not_stored"
        )

    return DecisionMemoryContractValidation(
        valid=not errors,
        market_available=result_validation.market_available,
        decision_type_defined=(
            result_validation.decision_type_defined
        ),
        priority_defined=(
            result_validation.priority_defined
        ),
        metadata_valid=(
            result_validation.metadata_valid
        ),
        timestamp_valid=(
            result_validation.timestamp_valid
        ),
        decision_id_available=(
            result_validation.decision_id_available
        ),
        decision_state_available=(
            result_validation.decision_state_available
        ),
        direction_available=(
            result_validation.direction_available
        ),
        confidence_valid=(
            result_validation.confidence_valid
        ),
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


# ============================================================
# STRICT READY GATE
# ============================================================

def decision_memory_ready(
    result: Optional[DecisionMemoryResult],
) -> bool:

    if result is None:
        return False

    validation = validate_decision_memory_result(
        result
    )

    if not validation.valid:
        return False

    if result.status != DecisionMemoryResultStatus.STORED:
        return False

    requirements = result.requirements
    assessment = result.assessment

    if requirements is None:
        return False

    if assessment is None:
        return False

    if (
        requirements.data_state
        != DecisionMemoryDataState.COMPLETE
    ):
        return False

    if (
        requirements.consistency
        == DecisionMemoryConsistency.CONFLICTING
    ):
        return False

    if (
        requirements.readiness
        != DecisionMemoryReadiness.READY
    ):
        return False

    if not requirements.memory_available:
        return False

    if not requirements.decision_available:
        return False

    if not requirements.market_available:
        return False

    if not requirements.decision_type_defined:
        return False

    if not requirements.decision_id_available:
        return False

    if not requirements.symbol_available:
        return False

    if not requirements.timestamp_available:
        return False

    if not requirements.source_available:
        return False

    if not requirements.decision_state_available:
        return False

    if not requirements.direction_available:
        return False

    if not requirements.confidence_available:
        return False

    if assessment.confidence_score < 80.0:
        return False

    return True


# ============================================================
# ADVANCE GATE
# ============================================================

def decision_memory_can_advance(
    result: Optional[DecisionMemoryResult],
) -> bool:

    if result is None:
        return False

    validation = validate_decision_memory_result(
        result
    )

    if not validation.valid:
        return False

    requirements = result.requirements
    assessment = result.assessment

    if requirements is None:
        return False

    if assessment is None:
        return False

    if (
        requirements.consistency
        == DecisionMemoryConsistency.CONFLICTING
    ):
        return False

    if (
        requirements.data_state
        == DecisionMemoryDataState.MISSING
    ):
        return False

    if not requirements.memory_available:
        return False

    if not requirements.decision_available:
        return False

    if not requirements.market_available:
        return False

    if not requirements.decision_type_defined:
        return False

    if not requirements.decision_id_available:
        return False

    if assessment.confidence_score < 50.0:
        return False

    return assessment.readiness in (
        DecisionMemoryReadiness.READY,
        DecisionMemoryReadiness.CONDITIONAL,
    )


# ============================================================
# ACCESSORS
# ============================================================

def decision_memory_status(
    result: Optional[DecisionMemoryResult],
) -> str:

    if result is None:
        return DecisionMemoryResultStatus.INVALID.value

    return result.status.value


def decision_memory_type(
    result: Optional[DecisionMemoryResult],
) -> str:

    if result is None or result.memory is None:
        return DecisionMemoryType.UNKNOWN.value

    return result.memory.decision_type.value


def decision_memory_readiness(
    result: Optional[DecisionMemoryResult],
) -> str:

    if result is None or result.assessment is None:
        return DecisionMemoryReadiness.UNKNOWN.value

    return result.assessment.readiness.value


def decision_memory_confidence(
    result: Optional[DecisionMemoryResult],
) -> float:

    if result is None or result.assessment is None:
        return 0.0

    return float(
        result.assessment.confidence_score
    )


def decision_memory_quality(
    result: Optional[DecisionMemoryResult],
) -> str:

    if result is None or result.assessment is None:
        return DecisionMemoryQuality.UNKNOWN.value

    return result.assessment.quality.value


def decision_memory_completeness(
    result: Optional[DecisionMemoryResult],
) -> float:

    if result is None or result.assessment is None:
        return 0.0

    return float(
        result.assessment.completeness_score
    )


def decision_memory_identity(
    result: Optional[DecisionMemoryResult],
) -> Optional[str]:

    if result is None or result.memory is None:
        return None

    return result.memory.memory_id


def decision_memory_decision_id(
    result: Optional[DecisionMemoryResult],
) -> Optional[str]:

    if result is None or result.memory is None:
        return None

    return result.memory.decision_id


def decision_memory_direction(
    result: Optional[DecisionMemoryResult],
) -> str:

    if result is None or result.memory is None:
        return ""

    return result.memory.direction


def decision_memory_state(
    result: Optional[DecisionMemoryResult],
) -> str:

    if result is None or result.memory is None:
        return ""

    return result.memory.decision_state


# ============================================================
# AUDIT
# ============================================================

def decision_memory_audit(
    result: Optional[DecisionMemoryResult],
) -> dict[str, Any]:

    validation = validate_decision_memory_result(
        result
    )

    if result is None:
        return {
            "engine": DECISION_MEMORY_ENGINE,
            "version": DECISION_MEMORY_VERSION,
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
        "engine": DECISION_MEMORY_ENGINE,
        "version": DECISION_MEMORY_VERSION,

        "request_id": result.request_id,
        "result_id": result.result_id,

        "valid": validation.valid,

        "status": result.status.value,

        "memory_id": (
            memory.memory_id
            if memory else None
        ),

        "decision_id": (
            memory.decision_id
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

        "decision_type": (
            memory.decision_type.value
            if memory
            else DecisionMemoryType.UNKNOWN.value
        ),

        "priority": (
            memory.priority.value
            if memory
            else DecisionMemoryPriority.UNKNOWN.value
        ),

        "decision_state": (
            memory.decision_state
            if memory else None
        ),

        "direction": (
            memory.direction
            if memory else None
        ),

        "data_state": (
            requirements.data_state.value
            if requirements
            else DecisionMemoryDataState.UNKNOWN.value
        ),

        "consistency": (
            requirements.consistency.value
            if requirements
            else DecisionMemoryConsistency.UNKNOWN.value
        ),

        "readiness": (
            assessment.readiness.value
            if assessment
            else DecisionMemoryReadiness.UNKNOWN.value
        ),

        "quality": (
            assessment.quality.value
            if assessment
            else DecisionMemoryQuality.UNKNOWN.value
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

        "ready": decision_memory_ready(result),

        "can_advance": decision_memory_can_advance(
            result
        ),

        "safe": decision_memory_is_safe(result),

        "allows_execution": (
            decision_memory_allows_execution(result)
        ),

        "allows_trade": (
            decision_memory_allows_trade(result)
        ),

        "allows_order": (
            decision_memory_allows_order(result)
        ),

        "allows_position_change": (
            decision_memory_allows_position_change(
                result
            )
        ),

        "allows_authorization": (
            decision_memory_allows_authorization(
                result
            )
        ),

        "overrides_d13": (
            decision_memory_overrides_d13(result)
        ),

        "overrides_risk": (
            decision_memory_overrides_risk(result)
        ),

        "overrides_cas": (
            decision_memory_overrides_cas(result)
        ),

        "errors": list(validation.errors),
        "warnings": list(validation.warnings),
    }


# ============================================================
# SAFETY BOUNDARIES
# ============================================================

def decision_memory_is_safe(
    result: Optional[DecisionMemoryResult],
) -> bool:

    if result is None:
        return False

    validation = validate_decision_memory_result(
        result
    )

    if not validation.valid:
        return False

    if result.status in (
        DecisionMemoryResultStatus.INVALID,
        DecisionMemoryResultStatus.INVALIDATED,
    ):
        return False

    if (
        result.requirements.consistency
        == DecisionMemoryConsistency.CONFLICTING
    ):
        return False

    return True


# ============================================================
# AUTHORITY BOUNDARIES
# ============================================================

def decision_memory_allows_execution(
    result: Optional[DecisionMemoryResult],
) -> bool:
    return False


def decision_memory_allows_trade(
    result: Optional[DecisionMemoryResult],
) -> bool:
    return False


def decision_memory_allows_order(
    result: Optional[DecisionMemoryResult],
) -> bool:
    return False


def decision_memory_allows_position_change(
    result: Optional[DecisionMemoryResult],
) -> bool:
    return False


def decision_memory_allows_authorization(
    result: Optional[DecisionMemoryResult],
) -> bool:
    return False


def decision_memory_overrides_d13(
    result: Optional[DecisionMemoryResult],
) -> bool:
    return False


def decision_memory_overrides_risk(
    result: Optional[DecisionMemoryResult],
) -> bool:
    return False


def decision_memory_overrides_cas(
    result: Optional[DecisionMemoryResult],
) -> bool:
    return False


# ============================================================
# ENGINE INFORMATION
# ============================================================

def get_decision_memory_engine_info() -> dict[str, Any]:

    return {
        "engine": DECISION_MEMORY_ENGINE,
        "version": DECISION_MEMORY_VERSION,

        "role": "decision_memory_intelligence",

        "responsibilities": [
            "decision_memory_request_validation",
            "decision_reference_normalization",
            "decision_memory_requirements_evaluation",
            "decision_consistency_evaluation",
            "decision_memory_readiness_evaluation",
            "decision_memory_assessment",
            "decision_memory_result_generation",
            "decision_memory_contract_generation",
        ],

        "non_responsibilities": [
            "decision_generation",
            "decision_override",
            "trade_execution",
            "order_creation",
            "position_modification",
            "account_authorization",
            "d13_override",
            "risk_override",
            "cas_override",
        ],

        "authority": (
            "non_authoritative_for_decision_generation_"
            "and_trade_execution"
        ),

        "d13_authority_preserved": True,
        "risk_authority_preserved": True,
        "cas_authority_preserved": True,
    }


# ============================================================
# HEALTH CHECK
# ============================================================

def decision_memory_health_check() -> dict[str, Any]:

    checks = {
        "engine_instance": isinstance(
            decision_memory_engine,
            DecisionMemoryEngine,
        ),

        "engine_name": (
            getattr(
                decision_memory_engine,
                "name",
                DECISION_MEMORY_ENGINE,
            )
            == DECISION_MEMORY_ENGINE
        ),

        "engine_version": (
            getattr(
                decision_memory_engine,
                "version",
                DECISION_MEMORY_VERSION,
            )
            == DECISION_MEMORY_VERSION
        ),

        "execution_blocked": not (
            decision_memory_allows_execution(None)
        ),

        "trade_blocked": not (
            decision_memory_allows_trade(None)
        ),

        "order_blocked": not (
            decision_memory_allows_order(None)
        ),

        "position_change_blocked": not (
            decision_memory_allows_position_change(None)
        ),

        "authorization_blocked": not (
            decision_memory_allows_authorization(None)
        ),

        "d13_override_blocked": not (
            decision_memory_overrides_d13(None)
        ),

        "risk_override_blocked": not (
            decision_memory_overrides_risk(None)
        ),

        "cas_override_blocked": not (
            decision_memory_overrides_cas(None)
        ),
    }

    return {
        "engine": DECISION_MEMORY_ENGINE,
        "version": DECISION_MEMORY_VERSION,
        "healthy": all(checks.values()),
        "checks": checks,
    }


def run_decision_memory_health_check() -> bool:
    return bool(
        decision_memory_health_check()["healthy"]
    )
# ============================================================
# ROBOMLM_PLUS
# DECISION MEMORY ENGINE
# FILE: app/intelligence/memory/decision_memory.py
# PART 5 / 5
# SERIALIZATION + LIFECYCLE + INTEGRITY + EXPORTS
# ============================================================


# ============================================================
# LIFECYCLE HELPERS
# ============================================================

def decision_memory_requires_review(
    result: Optional[DecisionMemoryResult],
) -> bool:
    if result is None:
        return False

    return (
        result.status == DecisionMemoryResultStatus.REVIEW
        or result.action.state == DecisionMemoryActionState.REVIEW
    )


def decision_memory_requires_hold(
    result: Optional[DecisionMemoryResult],
) -> bool:
    if result is None:
        return False

    return (
        result.status == DecisionMemoryResultStatus.HOLD
        or result.action.state == DecisionMemoryActionState.HOLD
    )


def decision_memory_is_invalid(
    result: Optional[DecisionMemoryResult],
) -> bool:
    if result is None:
        return True

    return (
        result.status == DecisionMemoryResultStatus.INVALID
        or result.status == DecisionMemoryResultStatus.INVALIDATED
        or result.action.state == DecisionMemoryActionState.INVALIDATE
    )


def decision_memory_is_stored(
    result: Optional[DecisionMemoryResult],
) -> bool:
    if result is None:
        return False

    return (
        result.stored
        and decision_memory_ready(result)
    )


def decision_memory_is_conditional(
    result: Optional[DecisionMemoryResult],
) -> bool:
    return (
        result is not None
        and result.status
        == DecisionMemoryResultStatus.CONDITIONAL
    )


def decision_memory_is_archived(
    result: Optional[DecisionMemoryResult],
) -> bool:
    if result is None:
        return False

    return (
        result.status
        == DecisionMemoryResultStatus.ARCHIVED
        or result.action.state
        == DecisionMemoryActionState.ARCHIVE
    )


def decision_memory_lifecycle_state(
    result: Optional[DecisionMemoryResult],
) -> str:
    if result is None:
        return DecisionMemoryStatus.INVALID.value

    if decision_memory_is_invalid(result):
        return DecisionMemoryStatus.INVALID.value

    if decision_memory_is_archived(result):
        return DecisionMemoryStatus.ARCHIVED.value

    if decision_memory_requires_hold(result):
        return DecisionMemoryStatus.VALIDATING.value

    if decision_memory_requires_review(result):
        return DecisionMemoryStatus.RETRIEVING.value

    if decision_memory_is_stored(result):
        return DecisionMemoryStatus.STORED.value

    if decision_memory_is_conditional(result):
        return DecisionMemoryStatus.CAPTURING.value

    return DecisionMemoryStatus.UNKNOWN.value


# ============================================================
# DATETIME SERIALIZATION
# ============================================================

def _dm_iso(value: Any) -> Optional[str]:
    if isinstance(value, datetime):
        return value.isoformat()

    return None


# ============================================================
# REFERENCE SERIALIZATION
# ============================================================

def serialize_decision_memory_reference(
    reference: Optional[DecisionMemoryReference],
) -> Optional[dict[str, Any]]:

    if reference is None:
        return None

    return {
        "memory_id": reference.memory_id,
        "decision_id": reference.decision_id,
        "market": reference.market_name,
        "symbol": reference.symbol,

        "decision_type": reference.decision_type.value,
        "status": reference.status.value,
        "priority": reference.priority.value,

        "timestamp": _dm_iso(reference.timestamp),

        "timeframe": reference.timeframe,
        "session": reference.session,
        "regime": reference.regime,

        "source_type": reference.source_type.value,

        "decision_state": reference.decision_state,
        "direction": reference.direction,
        "confidence": reference.confidence,

        "decision": dict(reference.decision),
    }


# ============================================================
# RESULT SERIALIZATION
# ============================================================

def serialize_decision_memory_result(
    result: Optional[DecisionMemoryResult],
) -> dict[str, Any]:

    if result is None:
        return {
            "engine": DECISION_MEMORY_ENGINE,
            "version": DECISION_MEMORY_VERSION,
            "valid": False,
            "status": DecisionMemoryResultStatus.INVALID.value,
        }

    requirements = result.requirements
    assessment = result.assessment

    return {
        "engine": DECISION_MEMORY_ENGINE,
        "version": DECISION_MEMORY_VERSION,

        "request_id": result.request_id,
        "result_id": result.result_id,

        "status": result.status.value,

        "memory": serialize_decision_memory_reference(
            result.memory
        ),

        "requirements": {
            "memory_available": requirements.memory_available,
            "decision_available": requirements.decision_available,
            "market_available": requirements.market_available,

            "decision_type_defined": (
                requirements.decision_type_defined
            ),

            "decision_id_available": (
                requirements.decision_id_available
            ),

            "symbol_available": (
                requirements.symbol_available
            ),

            "timestamp_available": (
                requirements.timestamp_available
            ),

            "source_available": (
                requirements.source_available
            ),

            "decision_state_available": (
                requirements.decision_state_available
            ),

            "direction_available": (
                requirements.direction_available
            ),

            "confidence_available": (
                requirements.confidence_available
            ),

            "timeframe_available": (
                requirements.timeframe_available
            ),

            "session_available": (
                requirements.session_available
            ),

            "regime_available": (
                requirements.regime_available
            ),

            "data_state": (
                requirements.data_state.value
            ),

            "consistency": (
                requirements.consistency.value
            ),

            "readiness": (
                requirements.readiness.value
            ),

            "completeness_score": (
                requirements.completeness_score
            ),

            "warnings": list(
                requirements.warnings
            ),
        },

        "assessment": {
            "readiness": (
                assessment.readiness.value
            ),

            "data_state": (
                assessment.data_state.value
            ),

            "consistency": (
                assessment.consistency.value
            ),

            "quality": (
                assessment.quality.value
            ),

            "confidence_score": (
                assessment.confidence_score
            ),

            "completeness_score": (
                assessment.completeness_score
            ),

            "strengths": list(
                assessment.strengths
            ),

            "weaknesses": list(
                assessment.weaknesses
            ),

            "rationale": assessment.rationale,
        },

        "action": {
            "state": result.action.state.value,
            "memory_id": result.action.memory_id,
            "rationale": result.action.rationale,
            "warnings": list(
                result.action.warnings
            ),
            "is_action_request": (
                result.action.is_action_request
            ),
        },

        "rationale": result.rationale,
        "warnings": list(result.warnings),

        "created_at": _dm_iso(
            result.created_at
        ),

        "valid": result.is_valid,
        "stored": result.stored,
        "ready": decision_memory_ready(result),
        "can_advance": decision_memory_can_advance(
            result
        ),

        "requires_review": (
            decision_memory_requires_review(result)
        ),

        "requires_hold": (
            decision_memory_requires_hold(result)
        ),

        "invalid": decision_memory_is_invalid(
            result
        ),

        "safe": decision_memory_is_safe(result),

        "allows_execution": (
            decision_memory_allows_execution(result)
        ),

        "allows_trade": (
            decision_memory_allows_trade(result)
        ),

        "allows_order": (
            decision_memory_allows_order(result)
        ),

        "allows_position_change": (
            decision_memory_allows_position_change(
                result
            )
        ),

        "allows_authorization": (
            decision_memory_allows_authorization(
                result
            )
        ),

        "overrides_d13": (
            decision_memory_overrides_d13(result)
        ),

        "overrides_risk": (
            decision_memory_overrides_risk(result)
        ),

        "overrides_cas": (
            decision_memory_overrides_cas(result)
        ),
    }


# ============================================================
# INTEGRITY CHECK
# ============================================================

def decision_memory_integrity_check(
    result: Optional[DecisionMemoryResult],
) -> dict[str, Any]:

    if result is None:
        return {
            "engine": DECISION_MEMORY_ENGINE,
            "version": DECISION_MEMORY_VERSION,
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

        if not result.memory.decision_id.strip():
            errors.append("decision_id_missing")

        if not result.memory.market_name.strip():
            errors.append("market_missing")

        if (
            result.memory.decision_type
            == DecisionMemoryType.UNKNOWN
        ):
            errors.append("decision_type_unknown")

        if (
            result.memory.source_type
            == DecisionMemorySourceType.UNKNOWN
        ):
            errors.append("source_type_unknown")

    if result.requirements is not None:

        if (
            result.requirements.completeness_score < 0.0
            or result.requirements.completeness_score > 100.0
        ):
            errors.append(
                "completeness_score_out_of_range"
            )

    if result.assessment is not None:

        if (
            result.assessment.confidence_score < 0.0
            or result.assessment.confidence_score > 100.0
        ):
            errors.append(
                "confidence_score_out_of_range"
            )

    if result.status == DecisionMemoryResultStatus.STORED:

        if not decision_memory_ready(result):
            errors.append(
                "stored_result_not_ready"
            )

    return {
        "engine": DECISION_MEMORY_ENGINE,
        "version": DECISION_MEMORY_VERSION,
        "integrity": not errors,
        "errors": list(
            dict.fromkeys(errors)
        ),
    }


# ============================================================
# SUMMARY
# ============================================================

def decision_memory_summary(
    result: Optional[DecisionMemoryResult],
) -> dict[str, Any]:

    if result is None:
        return {
            "engine": DECISION_MEMORY_ENGINE,
            "version": DECISION_MEMORY_VERSION,
            "status": DecisionMemoryResultStatus.INVALID.value,
            "valid": False,
        }

    memory = result.memory
    assessment = result.assessment

    return {
        "engine": DECISION_MEMORY_ENGINE,
        "version": DECISION_MEMORY_VERSION,

        "memory_id": (
            memory.memory_id
            if memory else None
        ),

        "decision_id": (
            memory.decision_id
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

        "decision_type": (
            memory.decision_type.value
            if memory
            else DecisionMemoryType.UNKNOWN.value
        ),

        "decision_state": (
            memory.decision_state
            if memory else None
        ),

        "direction": (
            memory.direction
            if memory else None
        ),

        "status": result.status.value,

        "lifecycle": (
            decision_memory_lifecycle_state(result)
        ),

        "readiness": (
            assessment.readiness.value
            if assessment
            else DecisionMemoryReadiness.UNKNOWN.value
        ),

        "quality": (
            assessment.quality.value
            if assessment
            else DecisionMemoryQuality.UNKNOWN.value
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

        "ready": decision_memory_ready(result),

        "can_advance": (
            decision_memory_can_advance(result)
        ),

        "requires_review": (
            decision_memory_requires_review(result)
        ),

        "requires_hold": (
            decision_memory_requires_hold(result)
        ),

        "invalid": (
            decision_memory_is_invalid(result)
        ),

        "safe": decision_memory_is_safe(result),

        # Explicit authority boundary.
        "d13_override": False,
        "risk_override": False,
        "cas_override": False,
    }


# ============================================================
# MEMORY LIFECYCLE OPERATIONS
# ============================================================

def decision_memory_freeze(
    result: Optional[DecisionMemoryResult],
) -> bool:
    """
    Freezes a valid decision-memory record for retention.
    This does not freeze or modify D13 itself.
    """

    if result is None:
        return False

    if decision_memory_is_invalid(result):
        return False

    return decision_memory_ready(result)


def decision_memory_retain(
    result: Optional[DecisionMemoryResult],
) -> bool:

    if result is None:
        return False

    return (
        decision_memory_is_stored(result)
        and not decision_memory_is_invalid(result)
    )


def decision_memory_reject(
    result: Optional[DecisionMemoryResult],
) -> bool:

    return decision_memory_is_invalid(result)


# ============================================================
# AUTHORITY STATEMENT
# ============================================================

def decision_memory_authority_statement() -> str:

    return (
        "Decision Memory preserves, validates, assesses, and "
        "retrieves historical decision-memory state. It does "
        "not generate, alter, override, authorize, execute, "
        "or invalidate an authoritative trading decision. "
        "D13 remains the decision authority. Risk remains the "
        "risk authority. CAS remains the authorization and "
        "execution-safety authority."
    )


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [

    # Constants
    "DECISION_MEMORY_ENGINE",
    "DECISION_MEMORY_VERSION",

    # Core enums
    "DecisionMemoryStatus",
    "DecisionMemoryType",
    "DecisionMemoryPriority",
    "DecisionMemorySourceType",
    "DecisionMemoryQuality",
    "DecisionMemoryContractStatus",

    # Foundation contracts
    "DecisionMemoryRequest",
    "DecisionMemoryReference",
    "DecisionMemorySourceReference",
    "DecisionMemoryContractValidation",

    # Assessment enums/contracts
    "DecisionMemoryDataState",
    "DecisionMemoryConsistency",
    "DecisionMemoryReadiness",
    "DecisionMemoryRequirements",
    "DecisionMemoryAssessment",

    # Action/result/contract
    "DecisionMemoryActionState",
    "DecisionMemoryContractState",
    "DecisionMemoryResultStatus",
    "DecisionMemoryAction",
    "DecisionMemoryResult",
    "DecisionMemoryContract",

    # Reference + validation
    "build_decision_memory_reference",
    "validate_decision_memory_request",

    # Requirements + assessment
    "evaluate_decision_memory_data_state",
    "evaluate_decision_memory_consistency",
    "evaluate_decision_memory_requirements",
    "evaluate_decision_memory_readiness",
    "calculate_decision_memory_confidence",
    "determine_decision_memory_quality",
    "build_decision_memory_assessment",

    # Result + contract
    "build_decision_memory_action",
    "build_decision_memory_result",
    "build_decision_memory_contract",

    # Engine
    "DecisionMemoryEngine",
    "decision_memory_engine",

    # Public operations
    "evaluate_decision_memory",
    "analyze_decision_memory",
    "review_decision_memory",

    # Validation + gates
    "validate_decision_memory_result",
    "validate_decision_memory_contract",
    "decision_memory_ready",
    "decision_memory_can_advance",

    # Accessors
    "decision_memory_status",
    "decision_memory_type",
    "decision_memory_readiness",
    "decision_memory_confidence",
    "decision_memory_quality",
    "decision_memory_completeness",
    "decision_memory_identity",
    "decision_memory_decision_id",
    "decision_memory_direction",
    "decision_memory_state",

    # Audit + safety
    "decision_memory_audit",
    "decision_memory_is_safe",

    # Authority boundaries
    "decision_memory_allows_execution",
    "decision_memory_allows_trade",
    "decision_memory_allows_order",
    "decision_memory_allows_position_change",
    "decision_memory_allows_authorization",
    "decision_memory_overrides_d13",
    "decision_memory_overrides_risk",
    "decision_memory_overrides_cas",

    # Engine information
    "get_decision_memory_engine_info",
    "decision_memory_health_check",
    "run_decision_memory_health_check",

    # Lifecycle
    "decision_memory_requires_review",
    "decision_memory_requires_hold",
    "decision_memory_is_invalid",
    "decision_memory_is_stored",
    "decision_memory_is_conditional",
    "decision_memory_is_archived",
    "decision_memory_lifecycle_state",

    # Serialization
    "serialize_decision_memory_reference",
    "serialize_decision_memory_result",

    # Integrity
    "decision_memory_integrity_check",
    "decision_memory_summary",

    # Lifecycle operations
    "decision_memory_freeze",
    "decision_memory_retain",
    "decision_memory_reject",

    # Authority
    "decision_memory_authority_statement",
]