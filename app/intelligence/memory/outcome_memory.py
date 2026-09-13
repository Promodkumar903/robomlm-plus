# app/intelligence/memory/outcome_memory.py

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Optional
from uuid import uuid4


OUTCOME_MEMORY_ENGINE = "ROBOMLM_OUTCOME_MEMORY_ENGINE"
OUTCOME_MEMORY_VERSION = "1.0"


# ============================================================
# OUTCOME MEMORY STATUS
# ============================================================

class OutcomeMemoryStatus(str, Enum):
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


# ============================================================
# OUTCOME MEMORY TYPE
# ============================================================

class OutcomeMemoryType(str, Enum):
    TRADE_OUTCOME = "TRADE_OUTCOME"
    DECISION_OUTCOME = "DECISION_OUTCOME"
    EXECUTION_OUTCOME = "EXECUTION_OUTCOME"
    RISK_OUTCOME = "RISK_OUTCOME"
    CAS_OUTCOME = "CAS_OUTCOME"
    MARKET_OUTCOME = "MARKET_OUTCOME"
    POSITION_OUTCOME = "POSITION_OUTCOME"
    SESSION_OUTCOME = "SESSION_OUTCOME"
    PERFORMANCE_OUTCOME = "PERFORMANCE_OUTCOME"
    FAILURE_OUTCOME = "FAILURE_OUTCOME"
    LEARNING_OUTCOME = "LEARNING_OUTCOME"
    UNKNOWN = "UNKNOWN"


# ============================================================
# PRIORITY
# ============================================================

class OutcomeMemoryPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


# ============================================================
# SOURCE TYPE
# ============================================================

class OutcomeMemorySourceType(str, Enum):
    EXECUTION = "EXECUTION"
    TRADE = "TRADE"
    POSITION = "POSITION"
    DECISION_CORTEX = "DECISION_CORTEX"
    D13 = "D13"
    RISK = "RISK"
    CAS = "CAS"
    MARKET = "MARKET"
    RESEARCH = "RESEARCH"
    LEARNING = "LEARNING"
    SYSTEM = "SYSTEM"
    UNKNOWN = "UNKNOWN"


# ============================================================
# OUTCOME QUALITY
# ============================================================

class OutcomeMemoryQuality(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


# ============================================================
# CONTRACT STATUS
# ============================================================

class OutcomeMemoryContractStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


# ============================================================
# REQUEST CONTRACT
# ============================================================

@dataclass(frozen=True)
class OutcomeMemoryRequest:
    market: str

    outcome_type: OutcomeMemoryType = OutcomeMemoryType.UNKNOWN
    source: str = ""

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    symbol: str = ""
    timeframe: str = ""
    session: str = ""
    regime: str = ""

    outcome_id: str = ""
    decision_id: str = ""
    execution_id: str = ""
    position_id: str = ""

    outcome_state: str = ""
    result: str = ""
    direction: str = ""

    pnl: Optional[float] = None
    return_pct: Optional[float] = None
    confidence: Optional[float] = None

    priority: OutcomeMemoryPriority = OutcomeMemoryPriority.UNKNOWN

    metadata: Mapping[str, Any] = field(default_factory=dict)

    request_id: str = field(default_factory=lambda: str(uuid4()))

    def validate(self) -> bool:
        if not self.market.strip():
            return False

        if not self.request_id.strip():
            return False

        if not isinstance(self.metadata, Mapping):
            return False

        if not isinstance(self.outcome_type, OutcomeMemoryType):
            return False

        if not isinstance(self.priority, OutcomeMemoryPriority):
            return False

        if self.confidence is not None:
            try:
                confidence = float(self.confidence)
            except (TypeError, ValueError):
                return False

            if confidence < 0.0 or confidence > 100.0:
                return False

        if self.return_pct is not None:
            try:
                float(self.return_pct)
            except (TypeError, ValueError):
                return False

        if self.pnl is not None:
            try:
                float(self.pnl)
            except (TypeError, ValueError):
                return False

        return True


# ============================================================
# MEMORY REFERENCE
# ============================================================

@dataclass(frozen=True)
class OutcomeMemoryReference:
    memory_id: str

    outcome_id: str
    decision_id: str
    execution_id: str
    position_id: str

    market_name: str
    symbol: str

    outcome_type: OutcomeMemoryType
    status: OutcomeMemoryStatus
    priority: OutcomeMemoryPriority

    timestamp: datetime

    timeframe: str
    session: str
    regime: str

    source_type: OutcomeMemorySourceType

    outcome_state: str = ""
    result: str = ""
    direction: str = ""

    pnl: Optional[float] = None
    return_pct: Optional[float] = None
    confidence: Optional[float] = None

    outcome: Mapping[str, Any] = field(default_factory=dict)


# ============================================================
# SOURCE REFERENCE
# ============================================================

@dataclass(frozen=True)
class OutcomeMemorySourceReference:
    source_id: str
    source_name: str

    source_type: OutcomeMemorySourceType

    timestamp: Optional[datetime] = None

    provenance: str = ""
    description: str = ""

    raw_source: Mapping[str, Any] = field(default_factory=dict)


# ============================================================
# CONTRACT VALIDATION
# ============================================================

@dataclass(frozen=True)
class OutcomeMemoryContractValidation:
    valid: bool

    market_available: bool
    outcome_type_defined: bool
    priority_defined: bool

    metadata_valid: bool
    timestamp_valid: bool

    outcome_id_available: bool
    decision_id_available: bool
    execution_id_available: bool
    position_id_available: bool

    outcome_state_available: bool
    result_available: bool
    direction_available: bool

    confidence_valid: bool
    pnl_valid: bool
    return_valid: bool

    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:
        return self.valid


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _om_read_value(
    source: Any,
    key: str,
    default: Any = None,
) -> Any:
    if isinstance(source, Mapping):
        return source.get(key, default)

    return getattr(source, key, default)


def _om_text(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip()


def _om_timestamp(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        text = value.strip()

        if text:
            try:
                return datetime.fromisoformat(
                    text.replace("Z", "+00:00")
                )
            except ValueError:
                pass

    return datetime.now(timezone.utc)


def _om_float(
    value: Any,
    minimum: Optional[float] = None,
    maximum: Optional[float] = None,
) -> Optional[float]:
    if value is None:
        return None

    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    if minimum is not None and number < minimum:
        return None

    if maximum is not None and number > maximum:
        return None

    return number


def _om_enum(
    value: Any,
    enum_type: type[Enum],
    default: Enum,
) -> Enum:
    if isinstance(value, enum_type):
        return value

    text = _om_text(value).upper()

    if not text:
        return default

    for member in enum_type:
        if member.value == text:
            return member

    return default


# ============================================================
# BUILD OUTCOME MEMORY REFERENCE
# ============================================================

def build_outcome_memory_reference(
    outcome: Any,
    request: Optional[OutcomeMemoryRequest] = None,
) -> OutcomeMemoryReference:
    source = outcome

    market = _om_text(
        _om_read_value(
            source,
            "market",
            _om_read_value(source, "market_name", ""),
        )
    )

    symbol = _om_text(
        _om_read_value(source, "symbol", "")
    )

    outcome_id = _om_text(
        _om_read_value(source, "outcome_id", "")
    )

    if not outcome_id and request is not None:
        outcome_id = request.outcome_id

    memory_id = _om_text(
        _om_read_value(source, "memory_id", "")
    )

    if not memory_id:
        memory_id = str(uuid4())

    outcome_type = _om_enum(
        _om_read_value(source, "outcome_type"),
        OutcomeMemoryType,
        (
            request.outcome_type
            if request is not None
            else OutcomeMemoryType.UNKNOWN
        ),
    )

    priority = _om_enum(
        _om_read_value(source, "priority"),
        OutcomeMemoryPriority,
        (
            request.priority
            if request is not None
            else OutcomeMemoryPriority.UNKNOWN
        ),
    )

    status = _om_enum(
        _om_read_value(source, "status"),
        OutcomeMemoryStatus,
        OutcomeMemoryStatus.NEW,
    )

    source_type = _om_enum(
        _om_read_value(source, "source_type"),
        OutcomeMemorySourceType,
        OutcomeMemorySourceType.UNKNOWN,
    )

    timestamp = _om_timestamp(
        _om_read_value(
            source,
            "timestamp",
            request.timestamp if request is not None else None,
        )
    )

    pnl = _om_float(
        _om_read_value(source, "pnl")
    )

    return_pct = _om_float(
        _om_read_value(source, "return_pct")
    )

    confidence = _om_float(
        _om_read_value(source, "confidence"),
        minimum=0.0,
        maximum=100.0,
    )

    outcome_payload = (
        dict(source)
        if isinstance(source, Mapping)
        else {}
    )

    return OutcomeMemoryReference(
        memory_id=memory_id,
        outcome_id=outcome_id,
        decision_id=_om_text(
            _om_read_value(
                source,
                "decision_id",
                request.decision_id if request else "",
            )
        ),
        execution_id=_om_text(
            _om_read_value(
                source,
                "execution_id",
                request.execution_id if request else "",
            )
        ),
        position_id=_om_text(
            _om_read_value(
                source,
                "position_id",
                request.position_id if request else "",
            )
        ),
        market_name=market,
        symbol=symbol,
        outcome_type=outcome_type,
        status=status,
        priority=priority,
        timestamp=timestamp,
        timeframe=_om_text(
            _om_read_value(
                source,
                "timeframe",
                request.timeframe if request else "",
            )
        ),
        session=_om_text(
            _om_read_value(
                source,
                "session",
                request.session if request else "",
            )
        ),
        regime=_om_text(
            _om_read_value(
                source,
                "regime",
                request.regime if request else "",
            )
        ),
        source_type=source_type,
        outcome_state=_om_text(
            _om_read_value(
                source,
                "outcome_state",
                request.outcome_state if request else "",
            )
        ),
        result=_om_text(
            _om_read_value(
                source,
                "result",
                request.result if request else "",
            )
        ),
        direction=_om_text(
            _om_read_value(
                source,
                "direction",
                request.direction if request else "",
            )
        ),
        pnl=pnl,
        return_pct=return_pct,
        confidence=confidence,
        outcome=outcome_payload,
    )


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_outcome_memory_request(
    request: OutcomeMemoryRequest,
) -> OutcomeMemoryContractValidation:
    errors: list[str] = []
    warnings: list[str] = []

    market_available = bool(request.market.strip())

    outcome_type_defined = (
        request.outcome_type != OutcomeMemoryType.UNKNOWN
    )

    priority_defined = (
        request.priority != OutcomeMemoryPriority.UNKNOWN
    )

    metadata_valid = isinstance(
        request.metadata,
        Mapping,
    )

    timestamp_valid = isinstance(
        request.timestamp,
        datetime,
    )

    outcome_id_available = bool(
        request.outcome_id.strip()
    )

    decision_id_available = bool(
        request.decision_id.strip()
    )

    execution_id_available = bool(
        request.execution_id.strip()
    )

    position_id_available = bool(
        request.position_id.strip()
    )

    outcome_state_available = bool(
        request.outcome_state.strip()
    )

    result_available = bool(
        request.result.strip()
    )

    direction_available = bool(
        request.direction.strip()
    )

    confidence_valid = True
    if request.confidence is not None:
        try:
            confidence = float(request.confidence)
            confidence_valid = 0.0 <= confidence <= 100.0
        except (TypeError, ValueError):
            confidence_valid = False

    pnl_valid = True
    if request.pnl is not None:
        try:
            float(request.pnl)
        except (TypeError, ValueError):
            pnl_valid = False

    return_valid = True
    if request.return_pct is not None:
        try:
            float(request.return_pct)
        except (TypeError, ValueError):
            return_valid = False

    if not market_available:
        errors.append("market_missing")

    if not outcome_type_defined:
        warnings.append("outcome_type_unknown")

    if not priority_defined:
        warnings.append("priority_unknown")

    if not metadata_valid:
        errors.append("metadata_invalid")

    if not timestamp_valid:
        errors.append("timestamp_invalid")

    if not outcome_id_available:
        warnings.append("outcome_id_missing")

    if not decision_id_available:
        warnings.append("decision_id_missing")

    if not execution_id_available:
        warnings.append("execution_id_missing")

    if not position_id_available:
        warnings.append("position_id_missing")

    if not outcome_state_available:
        warnings.append("outcome_state_missing")

    if not result_available:
        warnings.append("result_missing")

    if not direction_available:
        warnings.append("direction_missing")

    if not confidence_valid:
        errors.append("confidence_invalid")

    if not pnl_valid:
        errors.append("pnl_invalid")

    if not return_valid:
        errors.append("return_pct_invalid")

    valid = (
        not errors
        and market_available
        and metadata_valid
        and timestamp_valid
        and confidence_valid
        and pnl_valid
        and return_valid
    )

    return OutcomeMemoryContractValidation(
        valid=valid,
        market_available=market_available,
        outcome_type_defined=outcome_type_defined,
        priority_defined=priority_defined,
        metadata_valid=metadata_valid,
        timestamp_valid=timestamp_valid,
        outcome_id_available=outcome_id_available,
        decision_id_available=decision_id_available,
        execution_id_available=execution_id_available,
        position_id_available=position_id_available,
        outcome_state_available=outcome_state_available,
        result_available=result_available,
        direction_available=direction_available,
        confidence_valid=confidence_valid,
        pnl_valid=pnl_valid,
        return_valid=return_valid,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )
# ============================================================
# OUTCOME MEMORY DATA STATE
# ============================================================

class OutcomeMemoryDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    UNKNOWN = "UNKNOWN"


class OutcomeMemoryConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONFLICTING = "CONFLICTING"
    INSUFFICIENT = "INSUFFICIENT"
    UNKNOWN = "UNKNOWN"


class OutcomeMemoryReadiness(str, Enum):
    READY = "READY"
    CONDITIONAL = "CONDITIONAL"
    NOT_READY = "NOT_READY"
    UNKNOWN = "UNKNOWN"


# ============================================================
# REQUIREMENTS CONTRACT
# ============================================================

@dataclass(frozen=True)
class OutcomeMemoryRequirements:
    memory_available: bool
    outcome_available: bool

    market_available: bool
    outcome_type_defined: bool

    outcome_id_available: bool
    decision_id_available: bool
    execution_id_available: bool
    position_id_available: bool

    symbol_available: bool
    timestamp_available: bool
    source_available: bool

    outcome_state_available: bool
    result_available: bool
    direction_available: bool

    pnl_available: bool
    return_available: bool
    confidence_available: bool

    timeframe_available: bool
    session_available: bool
    regime_available: bool

    data_state: OutcomeMemoryDataState
    consistency: OutcomeMemoryConsistency
    readiness: OutcomeMemoryReadiness

    completeness_score: float

    warnings: tuple[str, ...] = ()


# ============================================================
# ASSESSMENT CONTRACT
# ============================================================

@dataclass(frozen=True)
class OutcomeMemoryAssessment:
    readiness: OutcomeMemoryReadiness
    data_state: OutcomeMemoryDataState
    consistency: OutcomeMemoryConsistency

    quality: OutcomeMemoryQuality

    confidence_score: float
    completeness_score: float

    strengths: tuple[str, ...] = ()
    weaknesses: tuple[str, ...] = ()

    rationale: str = ""


# ============================================================
# INTERNAL BOOLEAN NORMALIZER
# ============================================================

def _om_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    if value is None:
        return False

    if isinstance(value, (int, float)):
        return bool(value)

    text = str(value).strip().lower()

    return text in {
        "true",
        "1",
        "yes",
        "y",
        "available",
        "present",
        "valid",
        "complete",
    }


# ============================================================
# CONFLICT DETECTION
# ============================================================

def _om_conflict_detected(
    outcome: Any,
) -> bool:
    explicit = _om_read_value(
        outcome,
        "conflict",
        None,
    )

    if explicit is not None and _om_bool(explicit):
        return True

    explicit = _om_read_value(
        outcome,
        "conflicting",
        None,
    )

    if explicit is not None and _om_bool(explicit):
        return True

    consistency = _om_text(
        _om_read_value(
            outcome,
            "consistency",
            "",
        )
    ).upper()

    return consistency in {
        "CONFLICTING",
        "CONFLICT",
        "INVALID",
    }


# ============================================================
# DATA STATE EVALUATION
# ============================================================

def evaluate_outcome_memory_data_state(
    memory: OutcomeMemoryReference,
) -> OutcomeMemoryDataState:
    components = (
        bool(memory.memory_id.strip()),
        bool(memory.outcome_id.strip()),
        bool(memory.market_name.strip()),
        memory.outcome_type != OutcomeMemoryType.UNKNOWN,
        bool(memory.symbol.strip()),
        isinstance(memory.timestamp, datetime),
        memory.source_type != OutcomeMemorySourceType.UNKNOWN,
        bool(memory.outcome_state.strip()),
        bool(memory.result.strip()),
        bool(memory.direction.strip()),
        memory.pnl is not None,
        memory.return_pct is not None,
        memory.confidence is not None,
    )

    available = sum(
        1 for item in components if item
    )

    if available == len(components):
        return OutcomeMemoryDataState.COMPLETE

    if available == 0:
        return OutcomeMemoryDataState.MISSING

    return OutcomeMemoryDataState.PARTIAL


# ============================================================
# CONSISTENCY EVALUATION
# ============================================================

def evaluate_outcome_memory_consistency(
    outcome: Any,
    *,
    data_state: Optional[OutcomeMemoryDataState] = None,
) -> OutcomeMemoryConsistency:

    if _om_conflict_detected(outcome):
        return OutcomeMemoryConsistency.CONFLICTING

    state = data_state

    if state is None:
        if isinstance(outcome, OutcomeMemoryReference):
            state = evaluate_outcome_memory_data_state(
                outcome
            )
        else:
            state = OutcomeMemoryDataState.UNKNOWN

    if state == OutcomeMemoryDataState.MISSING:
        return OutcomeMemoryConsistency.INSUFFICIENT

    if state == OutcomeMemoryDataState.UNKNOWN:
        return OutcomeMemoryConsistency.UNKNOWN

    return OutcomeMemoryConsistency.CONSISTENT


# ============================================================
# REQUIREMENTS EVALUATION
# ============================================================

def evaluate_outcome_memory_requirements(
    memory: OutcomeMemoryReference,
) -> OutcomeMemoryRequirements:

    data_state = evaluate_outcome_memory_data_state(
        memory
    )

    consistency = evaluate_outcome_memory_consistency(
        memory,
        data_state=data_state,
    )

    memory_available = bool(
        memory.memory_id.strip()
    )

    outcome_available = bool(
        memory.outcome_id.strip()
    )

    market_available = bool(
        memory.market_name.strip()
    )

    outcome_type_defined = (
        memory.outcome_type
        != OutcomeMemoryType.UNKNOWN
    )

    outcome_id_available = bool(
        memory.outcome_id.strip()
    )

    decision_id_available = bool(
        memory.decision_id.strip()
    )

    execution_id_available = bool(
        memory.execution_id.strip()
    )

    position_id_available = bool(
        memory.position_id.strip()
    )

    symbol_available = bool(
        memory.symbol.strip()
    )

    timestamp_available = isinstance(
        memory.timestamp,
        datetime,
    )

    source_available = (
        memory.source_type
        != OutcomeMemorySourceType.UNKNOWN
    )

    outcome_state_available = bool(
        memory.outcome_state.strip()
    )

    result_available = bool(
        memory.result.strip()
    )

    direction_available = bool(
        memory.direction.strip()
    )

    pnl_available = memory.pnl is not None
    return_available = memory.return_pct is not None
    confidence_available = memory.confidence is not None

    timeframe_available = bool(
        memory.timeframe.strip()
    )

    session_available = bool(
        memory.session.strip()
    )

    regime_available = bool(
        memory.regime.strip()
    )

    components = (
        memory_available,
        outcome_available,
        market_available,
        outcome_type_defined,
        outcome_id_available,
        decision_id_available,
        execution_id_available,
        position_id_available,
        symbol_available,
        timestamp_available,
        source_available,
        outcome_state_available,
        result_available,
        direction_available,
        pnl_available,
        return_available,
        confidence_available,
        timeframe_available,
        session_available,
        regime_available,
    )

    completeness_score = (
        sum(1 for item in components if item)
        / len(components)
        * 100.0
    )

    warnings: list[str] = []

    optional_fields = (
        ("decision_id", decision_id_available),
        ("execution_id", execution_id_available),
        ("position_id", position_id_available),
        ("outcome_state", outcome_state_available),
        ("result", result_available),
        ("direction", direction_available),
        ("pnl", pnl_available),
        ("return_pct", return_available),
        ("confidence", confidence_available),
        ("timeframe", timeframe_available),
        ("session", session_available),
        ("regime", regime_available),
    )

    for name, available in optional_fields:
        if not available:
            warnings.append(
                f"{name}_missing"
            )

    readiness = evaluate_outcome_memory_readiness(
        data_state=data_state,
        consistency=consistency,
        completeness_score=completeness_score,
    )

    return OutcomeMemoryRequirements(
        memory_available=memory_available,
        outcome_available=outcome_available,
        market_available=market_available,
        outcome_type_defined=outcome_type_defined,
        outcome_id_available=outcome_id_available,
        decision_id_available=decision_id_available,
        execution_id_available=execution_id_available,
        position_id_available=position_id_available,
        symbol_available=symbol_available,
        timestamp_available=timestamp_available,
        source_available=source_available,
        outcome_state_available=outcome_state_available,
        result_available=result_available,
        direction_available=direction_available,
        pnl_available=pnl_available,
        return_available=return_available,
        confidence_available=confidence_available,
        timeframe_available=timeframe_available,
        session_available=session_available,
        regime_available=regime_available,
        data_state=data_state,
        consistency=consistency,
        readiness=readiness,
        completeness_score=round(
            completeness_score,
            2,
        ),
        warnings=tuple(warnings),
    )


# ============================================================
# READINESS EVALUATION
# ============================================================

def evaluate_outcome_memory_readiness(
    *,
    data_state: OutcomeMemoryDataState,
    consistency: OutcomeMemoryConsistency,
    completeness_score: float,
) -> OutcomeMemoryReadiness:

    if consistency == OutcomeMemoryConsistency.CONFLICTING:
        return OutcomeMemoryReadiness.NOT_READY

    if data_state == OutcomeMemoryDataState.MISSING:
        return OutcomeMemoryReadiness.NOT_READY

    if data_state == OutcomeMemoryDataState.UNKNOWN:
        return OutcomeMemoryReadiness.UNKNOWN

    if completeness_score >= 85.0:
        return OutcomeMemoryReadiness.READY

    if completeness_score >= 50.0:
        return OutcomeMemoryReadiness.CONDITIONAL

    return OutcomeMemoryReadiness.NOT_READY


# ============================================================
# CONFIDENCE CALCULATION
# ============================================================

def calculate_outcome_memory_confidence(
    requirements: OutcomeMemoryRequirements,
) -> float:

    score = requirements.completeness_score

    if requirements.consistency == (
        OutcomeMemoryConsistency.CONSISTENT
    ):
        score += 5.0

    elif requirements.consistency == (
        OutcomeMemoryConsistency.CONFLICTING
    ):
        score -= 30.0

    elif requirements.consistency == (
        OutcomeMemoryConsistency.INSUFFICIENT
    ):
        score -= 10.0

    elif requirements.consistency == (
        OutcomeMemoryConsistency.UNKNOWN
    ):
        score -= 20.0

    if requirements.data_state == (
        OutcomeMemoryDataState.MISSING
    ):
        score -= 20.0

    return round(
        max(0.0, min(100.0, score)),
        2,
    )


# ============================================================
# QUALITY CALCULATION
# ============================================================

def calculate_outcome_memory_quality(
    confidence_score: float,
    consistency: OutcomeMemoryConsistency,
) -> OutcomeMemoryQuality:

    if consistency == OutcomeMemoryConsistency.CONFLICTING:
        return OutcomeMemoryQuality.LOW

    if confidence_score >= 90.0:
        return OutcomeMemoryQuality.CRITICAL

    if confidence_score >= 75.0:
        return OutcomeMemoryQuality.HIGH

    if confidence_score >= 50.0:
        return OutcomeMemoryQuality.MODERATE

    if confidence_score > 0.0:
        return OutcomeMemoryQuality.LOW

    return OutcomeMemoryQuality.UNKNOWN


# ============================================================
# COMPLETE ASSESSMENT
# ============================================================

def build_outcome_memory_assessment(
    requirements: OutcomeMemoryRequirements,
) -> OutcomeMemoryAssessment:

    confidence_score = (
        calculate_outcome_memory_confidence(
            requirements
        )
    )

    quality = calculate_outcome_memory_quality(
        confidence_score,
        requirements.consistency,
    )

    strengths: list[str] = []
    weaknesses: list[str] = []

    if requirements.market_available:
        strengths.append("market_available")

    if requirements.outcome_available:
        strengths.append("outcome_identified")

    if requirements.outcome_type_defined:
        strengths.append("outcome_type_defined")

    if requirements.outcome_id_available:
        strengths.append("outcome_id_available")

    if requirements.symbol_available:
        strengths.append("symbol_available")

    if requirements.timestamp_available:
        strengths.append("timestamp_available")

    if requirements.source_available:
        strengths.append("source_available")

    if requirements.consistency == (
        OutcomeMemoryConsistency.CONSISTENT
    ):
        strengths.append("consistent")

    if requirements.consistency == (
        OutcomeMemoryConsistency.CONFLICTING
    ):
        weaknesses.append("conflicting_data")

    if requirements.data_state == (
        OutcomeMemoryDataState.PARTIAL
    ):
        weaknesses.append("partial_data")

    if requirements.data_state == (
        OutcomeMemoryDataState.MISSING
    ):
        weaknesses.append("missing_data")

    weaknesses.extend(
        requirements.warnings
    )

    rationale = (
        f"Outcome memory readiness="
        f"{requirements.readiness.value}; "
        f"data_state="
        f"{requirements.data_state.value}; "
        f"consistency="
        f"{requirements.consistency.value}; "
        f"completeness="
        f"{requirements.completeness_score:.2f}; "
        f"confidence="
        f"{confidence_score:.2f}."
    )

    return OutcomeMemoryAssessment(
        readiness=requirements.readiness,
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
# OUTCOME MEMORY ACTION STATE
# ============================================================

class OutcomeMemoryActionState(str, Enum):
    NONE = "NONE"
    STORE = "STORE"
    RETRIEVE = "RETRIEVE"
    CONSOLIDATE = "CONSOLIDATE"
    REVIEW = "REVIEW"
    HOLD = "HOLD"
    INVALIDATE = "INVALIDATE"
    ARCHIVE = "ARCHIVE"


# ============================================================
# OUTCOME MEMORY CONTRACT STATE
# ============================================================

class OutcomeMemoryContractState(str, Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


# ============================================================
# OUTCOME MEMORY RESULT STATUS
# ============================================================

class OutcomeMemoryResultStatus(str, Enum):
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
class OutcomeMemoryAction:
    state: OutcomeMemoryActionState
    reason: str = ""
    requires_review: bool = False
    requires_hold: bool = False
    is_action_request: bool = False


# ============================================================
# RESULT CONTRACT
# ============================================================

@dataclass(frozen=True)
class OutcomeMemoryResult:
    memory: OutcomeMemoryReference
    requirements: OutcomeMemoryRequirements
    assessment: OutcomeMemoryAssessment

    status: OutcomeMemoryResultStatus
    action: OutcomeMemoryAction

    success: bool
    message: str = ""

    result_id: str = field(
        default_factory=lambda: str(uuid4())
    )


# ============================================================
# COMPLETE CONTRACT
# ============================================================

@dataclass(frozen=True)
class OutcomeMemoryContract:
    result: OutcomeMemoryResult

    state: OutcomeMemoryContractState

    valid: bool
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    contract_id: str = field(
        default_factory=lambda: str(uuid4())
    )


# ============================================================
# RESULT STATUS DETERMINATION
# ============================================================

def _determine_outcome_memory_result_status(
    assessment: OutcomeMemoryAssessment,
) -> OutcomeMemoryResultStatus:

    if assessment.consistency == (
        OutcomeMemoryConsistency.CONFLICTING
    ):
        return OutcomeMemoryResultStatus.INVALIDATED

    if assessment.readiness == (
        OutcomeMemoryReadiness.READY
    ):
        return OutcomeMemoryResultStatus.STORED

    if assessment.readiness == (
        OutcomeMemoryReadiness.CONDITIONAL
    ):
        return OutcomeMemoryResultStatus.CONDITIONAL

    if assessment.readiness == (
        OutcomeMemoryReadiness.NOT_READY
    ):
        return OutcomeMemoryResultStatus.HOLD

    return OutcomeMemoryResultStatus.REVIEW


# ============================================================
# ACTION DETERMINATION
# ============================================================

def _build_outcome_memory_action(
    status: OutcomeMemoryResultStatus,
) -> OutcomeMemoryAction:

    if status == OutcomeMemoryResultStatus.STORED:
        return OutcomeMemoryAction(
            state=OutcomeMemoryActionState.STORE,
            reason="Outcome memory is valid and ready for storage.",
        )

    if status == OutcomeMemoryResultStatus.CONDITIONAL:
        return OutcomeMemoryAction(
            state=OutcomeMemoryActionState.REVIEW,
            reason="Outcome memory is conditionally complete and requires review.",
            requires_review=True,
        )

    if status == OutcomeMemoryResultStatus.REVIEW:
        return OutcomeMemoryAction(
            state=OutcomeMemoryActionState.REVIEW,
            reason="Outcome memory requires review before lifecycle advancement.",
            requires_review=True,
        )

    if status == OutcomeMemoryResultStatus.HOLD:
        return OutcomeMemoryAction(
            state=OutcomeMemoryActionState.HOLD,
            reason="Outcome memory is not ready and must remain on hold.",
            requires_hold=True,
        )

    if status == OutcomeMemoryResultStatus.INVALIDATED:
        return OutcomeMemoryAction(
            state=OutcomeMemoryActionState.INVALIDATE,
            reason="Outcome memory contains conflicting or invalid information.",
        )

    if status == OutcomeMemoryResultStatus.ARCHIVED:
        return OutcomeMemoryAction(
            state=OutcomeMemoryActionState.ARCHIVE,
            reason="Outcome memory is archived.",
        )

    return OutcomeMemoryAction(
        state=OutcomeMemoryActionState.INVALIDATE,
        reason="Outcome memory is invalid.",
    )


# ============================================================
# RESULT BUILDER
# ============================================================

def build_outcome_memory_result(
    memory: OutcomeMemoryReference,
    requirements: OutcomeMemoryRequirements,
    assessment: OutcomeMemoryAssessment,
) -> OutcomeMemoryResult:

    status = _determine_outcome_memory_result_status(
        assessment
    )

    action = _build_outcome_memory_action(
        status
    )

    success = status in {
        OutcomeMemoryResultStatus.STORED,
        OutcomeMemoryResultStatus.CONDITIONAL,
    }

    if status == OutcomeMemoryResultStatus.STORED:
        message = "Outcome memory validated and stored."

    elif status == OutcomeMemoryResultStatus.CONDITIONAL:
        message = "Outcome memory is conditionally valid."

    elif status == OutcomeMemoryResultStatus.HOLD:
        message = "Outcome memory is held pending required information."

    elif status == OutcomeMemoryResultStatus.INVALIDATED:
        message = "Outcome memory invalidated because of conflicting information."

    elif status == OutcomeMemoryResultStatus.REVIEW:
        message = "Outcome memory requires review."

    else:
        message = "Outcome memory is invalid."

    return OutcomeMemoryResult(
        memory=memory,
        requirements=requirements,
        assessment=assessment,
        status=status,
        action=action,
        success=success,
        message=message,
    )


# ============================================================
# CONTRACT STATE BUILDER
# ============================================================

def build_outcome_memory_contract_state(
    result: OutcomeMemoryResult,
) -> OutcomeMemoryContractState:

    if result.status == (
        OutcomeMemoryResultStatus.INVALIDATED
    ):
        return OutcomeMemoryContractState.INVALID

    if result.status == (
        OutcomeMemoryResultStatus.INVALID
    ):
        return OutcomeMemoryContractState.INVALID

    if result.status == (
        OutcomeMemoryResultStatus.HOLD
    ):
        return OutcomeMemoryContractState.BLOCKED

    if result.status == (
        OutcomeMemoryResultStatus.STORED
    ):
        return OutcomeMemoryContractState.COMPLETE

    if result.status in {
        OutcomeMemoryResultStatus.CONDITIONAL,
        OutcomeMemoryResultStatus.REVIEW,
    }:
        return OutcomeMemoryContractState.INCOMPLETE

    return OutcomeMemoryContractState.INCOMPLETE


# ============================================================
# OUTCOME MEMORY ENGINE
# ============================================================

class OutcomeMemoryEngine:
    """
    Outcome Memory is a historical outcome preservation,
    validation and retrieval layer.

    It does not generate trading decisions and does not
    authorize or execute any market action.
    """

    engine_name = OUTCOME_MEMORY_ENGINE
    version = OUTCOME_MEMORY_VERSION

    def evaluate(
        self,
        outcome: Any,
        request: Optional[OutcomeMemoryRequest] = None,
    ) -> OutcomeMemoryAssessment:

        memory = build_outcome_memory_reference(
            outcome,
            request=request,
        )

        requirements = evaluate_outcome_memory_requirements(
            memory
        )

        return build_outcome_memory_assessment(
            requirements
        )

    def analyze(
        self,
        outcome: Any,
        request: Optional[OutcomeMemoryRequest] = None,
    ) -> OutcomeMemoryResult:

        memory = build_outcome_memory_reference(
            outcome,
            request=request,
        )

        requirements = evaluate_outcome_memory_requirements(
            memory
        )

        assessment = build_outcome_memory_assessment(
            requirements
        )

        return build_outcome_memory_result(
            memory=memory,
            requirements=requirements,
            assessment=assessment,
        )

    def review(
        self,
        outcome: Any,
        request: Optional[OutcomeMemoryRequest] = None,
    ) -> OutcomeMemoryContract:

        validation = (
            validate_outcome_memory_request(request)
            if request is not None
            else None
        )

        memory = build_outcome_memory_reference(
            outcome,
            request=request,
        )

        requirements = evaluate_outcome_memory_requirements(
            memory
        )

        assessment = build_outcome_memory_assessment(
            requirements
        )

        result = build_outcome_memory_result(
            memory=memory,
            requirements=requirements,
            assessment=assessment,
        )

        errors = list(
            validation.errors
            if validation is not None
            else ()
        )

        warnings = list(
            validation.warnings
            if validation is not None
            else requirements.warnings
        )

        state = build_outcome_memory_contract_state(
            result
        )

        valid = (
            validation.valid
            if validation is not None
            else state != OutcomeMemoryContractState.INVALID
        )

        if errors:
            state = OutcomeMemoryContractState.INVALID
            valid = False

        return OutcomeMemoryContract(
            result=result,
            state=state,
            valid=valid,
            errors=tuple(errors),
            warnings=tuple(warnings),
        )


# ============================================================
# SINGLETON ENGINE
# ============================================================

outcome_memory_engine = OutcomeMemoryEngine()


# ============================================================
# PUBLIC FUNCTIONS
# ============================================================

def evaluate_outcome_memory(
    outcome: Any,
    request: Optional[OutcomeMemoryRequest] = None,
) -> OutcomeMemoryAssessment:
    return outcome_memory_engine.evaluate(
        outcome,
        request=request,
    )


def analyze_outcome_memory(
    outcome: Any,
    request: Optional[OutcomeMemoryRequest] = None,
) -> OutcomeMemoryResult:
    return outcome_memory_engine.analyze(
        outcome,
        request=request,
    )


def review_outcome_memory(
    outcome: Any,
    request: Optional[OutcomeMemoryRequest] = None,
) -> OutcomeMemoryContract:
    return outcome_memory_engine.review(
        outcome,
        request=request,
    )
# ============================================================
# RESULT VALIDATION
# ============================================================

def validate_outcome_memory_result(
    result: OutcomeMemoryResult,
) -> bool:
    if not isinstance(result, OutcomeMemoryResult):
        return False

    if not isinstance(
        result.memory,
        OutcomeMemoryReference,
    ):
        return False

    if not isinstance(
        result.requirements,
        OutcomeMemoryRequirements,
    ):
        return False

    if not isinstance(
        result.assessment,
        OutcomeMemoryAssessment,
    ):
        return False

    if not isinstance(
        result.status,
        OutcomeMemoryResultStatus,
    ):
        return False

    if not isinstance(
        result.action,
        OutcomeMemoryAction,
    ):
        return False

    if not result.result_id.strip():
        return False

    return True


# ============================================================
# CONTRACT VALIDATION
# ============================================================

def validate_outcome_memory_contract(
    contract: OutcomeMemoryContract,
) -> bool:
    if not isinstance(
        contract,
        OutcomeMemoryContract,
    ):
        return False

    if not validate_outcome_memory_result(
        contract.result
    ):
        return False

    if not isinstance(
        contract.state,
        OutcomeMemoryContractState,
    ):
        return False

    if not contract.contract_id.strip():
        return False

    if contract.state == OutcomeMemoryContractState.INVALID:
        return not contract.valid

    return True


# ============================================================
# STRICT OUTCOME MEMORY READINESS
# ============================================================

def outcome_memory_ready(
    result: OutcomeMemoryResult,
) -> bool:
    if not validate_outcome_memory_result(result):
        return False

    memory = result.memory
    requirements = result.requirements
    assessment = result.assessment

    if result.status != OutcomeMemoryResultStatus.STORED:
        return False

    if assessment.readiness != OutcomeMemoryReadiness.READY:
        return False

    if assessment.data_state != OutcomeMemoryDataState.COMPLETE:
        return False

    if assessment.consistency != (
        OutcomeMemoryConsistency.CONSISTENT
    ):
        return False

    required_values = (
        memory.memory_id,
        memory.outcome_id,
        memory.market_name,
        memory.symbol,
        memory.outcome_state,
        memory.result,
        memory.direction,
    )

    if not all(
        isinstance(value, str) and value.strip()
        for value in required_values
    ):
        return False

    if memory.outcome_type == OutcomeMemoryType.UNKNOWN:
        return False

    if memory.source_type == OutcomeMemorySourceType.UNKNOWN:
        return False

    if not isinstance(memory.timestamp, datetime):
        return False

    if memory.pnl is None:
        return False

    if memory.return_pct is None:
        return False

    if memory.confidence is None:
        return False

    if not requirements.market_available:
        return False

    if not requirements.outcome_available:
        return False

    if not requirements.outcome_id_available:
        return False

    if not requirements.symbol_available:
        return False

    if not requirements.timestamp_available:
        return False

    if not requirements.source_available:
        return False

    if not requirements.outcome_state_available:
        return False

    if not requirements.result_available:
        return False

    if not requirements.direction_available:
        return False

    if not requirements.pnl_available:
        return False

    if not requirements.return_available:
        return False

    if not requirements.confidence_available:
        return False

    if assessment.confidence_score < 80.0:
        return False

    return True


# ============================================================
# ADVANCE GATE
# ============================================================

def outcome_memory_can_advance(
    result: OutcomeMemoryResult,
) -> bool:
    if not validate_outcome_memory_result(result):
        return False

    assessment = result.assessment
    requirements = result.requirements

    if assessment.consistency == (
        OutcomeMemoryConsistency.CONFLICTING
    ):
        return False

    if assessment.data_state == (
        OutcomeMemoryDataState.MISSING
    ):
        return False

    if assessment.confidence_score < 50.0:
        return False

    if not requirements.memory_available:
        return False

    if not requirements.outcome_available:
        return False

    if not requirements.market_available:
        return False

    if not requirements.outcome_type_defined:
        return False

    if not requirements.outcome_id_available:
        return False

    return assessment.readiness in {
        OutcomeMemoryReadiness.READY,
        OutcomeMemoryReadiness.CONDITIONAL,
    }


# ============================================================
# ACCESSORS
# ============================================================

def outcome_memory_status(
    result: OutcomeMemoryResult,
) -> OutcomeMemoryResultStatus:
    return result.status


def outcome_memory_type(
    result: OutcomeMemoryResult,
) -> OutcomeMemoryType:
    return result.memory.outcome_type


def outcome_memory_readiness(
    result: OutcomeMemoryResult,
) -> OutcomeMemoryReadiness:
    return result.assessment.readiness


def outcome_memory_confidence(
    result: OutcomeMemoryResult,
) -> float:
    return result.assessment.confidence_score


def outcome_memory_quality(
    result: OutcomeMemoryResult,
) -> OutcomeMemoryQuality:
    return result.assessment.quality


def outcome_memory_completeness(
    result: OutcomeMemoryResult,
) -> float:
    return result.assessment.completeness_score


def outcome_memory_identity(
    result: OutcomeMemoryResult,
) -> str:
    return result.memory.memory_id


def outcome_memory_outcome_id(
    result: OutcomeMemoryResult,
) -> str:
    return result.memory.outcome_id


def outcome_memory_decision_id(
    result: OutcomeMemoryResult,
) -> str:
    return result.memory.decision_id


def outcome_memory_execution_id(
    result: OutcomeMemoryResult,
) -> str:
    return result.memory.execution_id


def outcome_memory_position_id(
    result: OutcomeMemoryResult,
) -> str:
    return result.memory.position_id


def outcome_memory_result_state(
    result: OutcomeMemoryResult,
) -> str:
    return result.memory.outcome_state


def outcome_memory_direction(
    result: OutcomeMemoryResult,
) -> str:
    return result.memory.direction


def outcome_memory_pnl(
    result: OutcomeMemoryResult,
) -> Optional[float]:
    return result.memory.pnl


# ============================================================
# AUDIT
# ============================================================

def outcome_memory_audit(
    result: OutcomeMemoryResult,
) -> dict[str, Any]:

    return {
        "engine": OUTCOME_MEMORY_ENGINE,
        "version": OUTCOME_MEMORY_VERSION,
        "result_id": result.result_id,
        "memory_id": result.memory.memory_id,
        "outcome_id": result.memory.outcome_id,
        "decision_id": result.memory.decision_id,
        "execution_id": result.memory.execution_id,
        "position_id": result.memory.position_id,
        "market": result.memory.market_name,
        "symbol": result.memory.symbol,
        "outcome_type": result.memory.outcome_type.value,
        "status": result.status.value,
        "action": result.action.state.value,
        "readiness": result.assessment.readiness.value,
        "data_state": result.assessment.data_state.value,
        "consistency": result.assessment.consistency.value,
        "quality": result.assessment.quality.value,
        "confidence": result.assessment.confidence_score,
        "completeness": result.assessment.completeness_score,
        "success": result.success,
        "safe": outcome_memory_is_safe(result),
        "can_advance": outcome_memory_can_advance(result),
        "ready": outcome_memory_ready(result),
        "allows_execution": (
            outcome_memory_allows_execution(result)
        ),
        "allows_trade": (
            outcome_memory_allows_trade(result)
        ),
        "allows_order": (
            outcome_memory_allows_order(result)
        ),
        "allows_position_change": (
            outcome_memory_allows_position_change(result)
        ),
        "allows_authorization": (
            outcome_memory_allows_authorization(result)
        ),
        "overrides_d13": (
            outcome_memory_overrides_d13(result)
        ),
        "overrides_risk": (
            outcome_memory_overrides_risk(result)
        ),
        "overrides_cas": (
            outcome_memory_overrides_cas(result)
        ),
    }


# ============================================================
# SAFETY BOUNDARY
# ============================================================

def outcome_memory_is_safe(
    result: OutcomeMemoryResult,
) -> bool:
    if not validate_outcome_memory_result(result):
        return False

    if result.status in {
        OutcomeMemoryResultStatus.INVALID,
        OutcomeMemoryResultStatus.INVALIDATED,
    }:
        return False

    if result.assessment.consistency == (
        OutcomeMemoryConsistency.CONFLICTING
    ):
        return False

    return True


# ============================================================
# AUTHORITY BOUNDARIES
# ============================================================

def outcome_memory_allows_execution(
    result: OutcomeMemoryResult,
) -> bool:
    return False


def outcome_memory_allows_trade(
    result: OutcomeMemoryResult,
) -> bool:
    return False


def outcome_memory_allows_order(
    result: OutcomeMemoryResult,
) -> bool:
    return False


def outcome_memory_allows_position_change(
    result: OutcomeMemoryResult,
) -> bool:
    return False


def outcome_memory_allows_authorization(
    result: OutcomeMemoryResult,
) -> bool:
    return False


def outcome_memory_overrides_d13(
    result: OutcomeMemoryResult,
) -> bool:
    return False


def outcome_memory_overrides_risk(
    result: OutcomeMemoryResult,
) -> bool:
    return False


def outcome_memory_overrides_cas(
    result: OutcomeMemoryResult,
) -> bool:
    return False


# ============================================================
# ENGINE INFORMATION
# ============================================================

def outcome_memory_engine_info() -> dict[str, str]:
    return {
        "engine": OUTCOME_MEMORY_ENGINE,
        "version": OUTCOME_MEMORY_VERSION,
        "role": (
            "Historical outcome preservation, "
            "validation, assessment and retrieval"
        ),
        "decision_authority": "NONE",
        "risk_authority": "NONE",
        "cas_authority": "NONE",
        "execution_authority": "NONE",
    }


# ============================================================
# HEALTH CHECK
# ============================================================

def outcome_memory_health_check() -> dict[str, Any]:
    return {
        "engine": OUTCOME_MEMORY_ENGINE,
        "version": OUTCOME_MEMORY_VERSION,
        "status": "HEALTHY",
        "contract_layer": "AVAILABLE",
        "assessment_layer": "AVAILABLE",
        "lifecycle_layer": "AVAILABLE",
        "execution_authority": False,
        "decision_override": False,
        "risk_override": False,
        "cas_override": False,
    }
# ============================================================
# LIFECYCLE HELPERS
# ============================================================

def outcome_memory_requires_review(
    result: OutcomeMemoryResult,
) -> bool:
    return result.status in {
        OutcomeMemoryResultStatus.CONDITIONAL,
        OutcomeMemoryResultStatus.REVIEW,
    }


def outcome_memory_requires_hold(
    result: OutcomeMemoryResult,
) -> bool:
    return result.status == OutcomeMemoryResultStatus.HOLD


def outcome_memory_is_invalid(
    result: OutcomeMemoryResult,
) -> bool:
    return result.status in {
        OutcomeMemoryResultStatus.INVALID,
        OutcomeMemoryResultStatus.INVALIDATED,
    }


def outcome_memory_is_stored(
    result: OutcomeMemoryResult,
) -> bool:
    return result.status == OutcomeMemoryResultStatus.STORED


def outcome_memory_is_conditional(
    result: OutcomeMemoryResult,
) -> bool:
    return result.status == OutcomeMemoryResultStatus.CONDITIONAL


def outcome_memory_is_archived(
    result: OutcomeMemoryResult,
) -> bool:
    return result.status == OutcomeMemoryResultStatus.ARCHIVED


def outcome_memory_lifecycle_state(
    result: OutcomeMemoryResult,
) -> str:
    if outcome_memory_is_invalid(result):
        return "INVALIDATED"

    if outcome_memory_is_archived(result):
        return "ARCHIVED"

    if outcome_memory_is_stored(result):
        return "STORED"

    if outcome_memory_requires_hold(result):
        return "HOLD"

    if outcome_memory_requires_review(result):
        return "REVIEW"

    return "UNKNOWN"


# ============================================================
# DATETIME SERIALIZATION
# ============================================================

def _om_iso(
    value: Optional[datetime],
) -> Optional[str]:
    if value is None:
        return None

    return value.isoformat()


# ============================================================
# REFERENCE SERIALIZATION
# ============================================================

def serialize_outcome_memory_reference(
    memory: OutcomeMemoryReference,
) -> dict[str, Any]:

    return {
        "memory_id": memory.memory_id,
        "outcome_id": memory.outcome_id,
        "decision_id": memory.decision_id,
        "execution_id": memory.execution_id,
        "position_id": memory.position_id,
        "market_name": memory.market_name,
        "symbol": memory.symbol,
        "outcome_type": memory.outcome_type.value,
        "status": memory.status.value,
        "priority": memory.priority.value,
        "timestamp": _om_iso(memory.timestamp),
        "timeframe": memory.timeframe,
        "session": memory.session,
        "regime": memory.regime,
        "source_type": memory.source_type.value,
        "outcome_state": memory.outcome_state,
        "result": memory.result,
        "direction": memory.direction,
        "pnl": memory.pnl,
        "return_pct": memory.return_pct,
        "confidence": memory.confidence,
        "outcome": dict(memory.outcome),
    }


# ============================================================
# RESULT SERIALIZATION
# ============================================================

def serialize_outcome_memory_result(
    result: OutcomeMemoryResult,
) -> dict[str, Any]:

    assessment = result.assessment
    requirements = result.requirements

    return {
        "result_id": result.result_id,
        "memory": serialize_outcome_memory_reference(
            result.memory
        ),
        "status": result.status.value,
        "success": result.success,
        "message": result.message,
        "action": {
            "state": result.action.state.value,
            "reason": result.action.reason,
            "requires_review": result.action.requires_review,
            "requires_hold": result.action.requires_hold,
            "is_action_request": result.action.is_action_request,
        },
        "requirements": {
            "memory_available": requirements.memory_available,
            "outcome_available": requirements.outcome_available,
            "market_available": requirements.market_available,
            "outcome_type_defined": requirements.outcome_type_defined,
            "outcome_id_available": requirements.outcome_id_available,
            "decision_id_available": requirements.decision_id_available,
            "execution_id_available": requirements.execution_id_available,
            "position_id_available": requirements.position_id_available,
            "symbol_available": requirements.symbol_available,
            "timestamp_available": requirements.timestamp_available,
            "source_available": requirements.source_available,
            "outcome_state_available": requirements.outcome_state_available,
            "result_available": requirements.result_available,
            "direction_available": requirements.direction_available,
            "pnl_available": requirements.pnl_available,
            "return_available": requirements.return_available,
            "confidence_available": requirements.confidence_available,
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
    }


# ============================================================
# INTEGRITY CHECK
# ============================================================

def outcome_memory_integrity_check(
    result: OutcomeMemoryResult,
) -> dict[str, Any]:

    result_valid = validate_outcome_memory_result(
        result
    )

    strict_ready = (
        outcome_memory_ready(result)
        if result_valid
        else False
    )

    advance_allowed = (
        outcome_memory_can_advance(result)
        if result_valid
        else False
    )

    safe = (
        outcome_memory_is_safe(result)
        if result_valid
        else False
    )

    return {
        "valid_result": result_valid,
        "safe": safe,
        "ready": strict_ready,
        "can_advance": advance_allowed,
        "invalid": (
            outcome_memory_is_invalid(result)
            if result_valid
            else True
        ),
        "requires_review": (
            outcome_memory_requires_review(result)
            if result_valid
            else False
        ),
        "requires_hold": (
            outcome_memory_requires_hold(result)
            if result_valid
            else True
        ),
        "authority_violation": (
            outcome_memory_allows_execution(result)
            or outcome_memory_allows_trade(result)
            or outcome_memory_allows_order(result)
            or outcome_memory_allows_position_change(result)
            or outcome_memory_allows_authorization(result)
            or outcome_memory_overrides_d13(result)
            or outcome_memory_overrides_risk(result)
            or outcome_memory_overrides_cas(result)
        ),
    }


# ============================================================
# SUMMARY
# ============================================================

def outcome_memory_summary(
    result: OutcomeMemoryResult,
) -> dict[str, Any]:

    return {
        "engine": OUTCOME_MEMORY_ENGINE,
        "version": OUTCOME_MEMORY_VERSION,
        "memory_id": result.memory.memory_id,
        "outcome_id": result.memory.outcome_id,
        "decision_id": result.memory.decision_id,
        "execution_id": result.memory.execution_id,
        "position_id": result.memory.position_id,
        "market": result.memory.market_name,
        "symbol": result.memory.symbol,
        "outcome_type": result.memory.outcome_type.value,
        "status": result.status.value,
        "lifecycle": outcome_memory_lifecycle_state(
            result
        ),
        "readiness": result.assessment.readiness.value,
        "quality": result.assessment.quality.value,
        "confidence": result.assessment.confidence_score,
        "completeness": result.assessment.completeness_score,
        "pnl": result.memory.pnl,
        "return_pct": result.memory.return_pct,
        "safe": outcome_memory_is_safe(result),
        "ready": outcome_memory_ready(result),
        "can_advance": outcome_memory_can_advance(result),
    }


# ============================================================
# FREEZE
# ============================================================

def outcome_memory_freeze(
    result: OutcomeMemoryResult,
) -> OutcomeMemoryResult:

    if outcome_memory_is_invalid(result):
        return result

    memory = result.memory

    frozen_memory = OutcomeMemoryReference(
        memory_id=memory.memory_id,
        outcome_id=memory.outcome_id,
        decision_id=memory.decision_id,
        execution_id=memory.execution_id,
        position_id=memory.position_id,
        market_name=memory.market_name,
        symbol=memory.symbol,
        outcome_type=memory.outcome_type,
        status=OutcomeMemoryStatus.STORED,
        priority=memory.priority,
        timestamp=memory.timestamp,
        timeframe=memory.timeframe,
        session=memory.session,
        regime=memory.regime,
        source_type=memory.source_type,
        outcome_state=memory.outcome_state,
        result=memory.result,
        direction=memory.direction,
        pnl=memory.pnl,
        return_pct=memory.return_pct,
        confidence=memory.confidence,
        outcome=memory.outcome,
    )

    requirements = evaluate_outcome_memory_requirements(
        frozen_memory
    )

    assessment = build_outcome_memory_assessment(
        requirements
    )

    return build_outcome_memory_result(
        memory=frozen_memory,
        requirements=requirements,
        assessment=assessment,
    )


# ============================================================
# RETAIN
# ============================================================

def outcome_memory_retain(
    result: OutcomeMemoryResult,
) -> OutcomeMemoryResult:

    if not outcome_memory_is_safe(result):
        return result

    return result


# ============================================================
# REJECT
# ============================================================

def outcome_memory_reject(
    result: OutcomeMemoryResult,
    reason: str = "",
) -> OutcomeMemoryResult:

    action = OutcomeMemoryAction(
        state=OutcomeMemoryActionState.INVALIDATE,
        reason=(
            reason.strip()
            or "Outcome memory rejected."
        ),
        requires_review=False,
        requires_hold=False,
        is_action_request=False,
    )

    return OutcomeMemoryResult(
        memory=result.memory,
        requirements=result.requirements,
        assessment=result.assessment,
        status=OutcomeMemoryResultStatus.INVALIDATED,
        action=action,
        success=False,
        message=(
            reason.strip()
            or "Outcome memory rejected."
        ),
        result_id=result.result_id,
    )


# ============================================================
# AUTHORITY STATEMENT
# ============================================================

def outcome_memory_authority_statement() -> str:
    return (
        "Outcome Memory preserves, validates, assesses, "
        "retrieves and retains historical outcome information. "
        "It does not generate, alter, override, authorize or "
        "execute trading decisions. D13 remains the authoritative "
        "decision layer; Risk remains the authoritative risk layer; "
        "CAS remains the authoritative authorization and execution-"
        "safety layer."
    )


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [
    # Constants
    "OUTCOME_MEMORY_ENGINE",
    "OUTCOME_MEMORY_VERSION",

    # Enums
    "OutcomeMemoryStatus",
    "OutcomeMemoryType",
    "OutcomeMemoryPriority",
    "OutcomeMemorySourceType",
    "OutcomeMemoryQuality",
    "OutcomeMemoryContractStatus",
    "OutcomeMemoryDataState",
    "OutcomeMemoryConsistency",
    "OutcomeMemoryReadiness",
    "OutcomeMemoryActionState",
    "OutcomeMemoryContractState",
    "OutcomeMemoryResultStatus",

    # Contracts
    "OutcomeMemoryRequest",
    "OutcomeMemoryReference",
    "OutcomeMemorySourceReference",
    "OutcomeMemoryContractValidation",
    "OutcomeMemoryRequirements",
    "OutcomeMemoryAssessment",
    "OutcomeMemoryAction",
    "OutcomeMemoryResult",
    "OutcomeMemoryContract",

    # Builders / validation
    "build_outcome_memory_reference",
    "validate_outcome_memory_request",
    "evaluate_outcome_memory_data_state",
    "evaluate_outcome_memory_consistency",
    "evaluate_outcome_memory_requirements",
    "evaluate_outcome_memory_readiness",
    "calculate_outcome_memory_confidence",
    "calculate_outcome_memory_quality",
    "build_outcome_memory_assessment",
    "build_outcome_memory_result",
    "build_outcome_memory_contract_state",
    "validate_outcome_memory_result",
    "validate_outcome_memory_contract",

    # Engine
    "OutcomeMemoryEngine",
    "outcome_memory_engine",
    "evaluate_outcome_memory",
    "analyze_outcome_memory",
    "review_outcome_memory",

    # Gates / accessors
    "outcome_memory_ready",
    "outcome_memory_can_advance",
    "outcome_memory_status",
    "outcome_memory_type",
    "outcome_memory_readiness",
    "outcome_memory_confidence",
    "outcome_memory_quality",
    "outcome_memory_completeness",
    "outcome_memory_identity",
    "outcome_memory_outcome_id",
    "outcome_memory_decision_id",
    "outcome_memory_execution_id",
    "outcome_memory_position_id",
    "outcome_memory_result_state",
    "outcome_memory_direction",
    "outcome_memory_pnl",

    # Audit / safety / authority
    "outcome_memory_audit",
    "outcome_memory_is_safe",
    "outcome_memory_allows_execution",
    "outcome_memory_allows_trade",
    "outcome_memory_allows_order",
    "outcome_memory_allows_position_change",
    "outcome_memory_allows_authorization",
    "outcome_memory_overrides_d13",
    "outcome_memory_overrides_risk",
    "outcome_memory_overrides_cas",
    "outcome_memory_engine_info",
    "outcome_memory_health_check",

    # Lifecycle
    "outcome_memory_requires_review",
    "outcome_memory_requires_hold",
    "outcome_memory_is_invalid",
    "outcome_memory_is_stored",
    "outcome_memory_is_conditional",
    "outcome_memory_is_archived",
    "outcome_memory_lifecycle_state",

    # Serialization / integrity
    "serialize_outcome_memory_reference",
    "serialize_outcome_memory_result",
    "outcome_memory_integrity_check",
    "outcome_memory_summary",

    # Lifecycle operations
    "outcome_memory_freeze",
    "outcome_memory_retain",
    "outcome_memory_reject",

    # Authority
    "outcome_memory_authority_statement",
]