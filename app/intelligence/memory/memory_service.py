# ============================================================
# ROBOMLM_PLUS
# app/intelligence/memory/memory_service.py
# PART 1 — FOUNDATION / REQUEST / REFERENCE / CONTRACTS
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Optional, Sequence
from uuid import uuid4


MEMORY_SERVICE_ENGINE = "ROBOMLM_MEMORY_SERVICE"
MEMORY_SERVICE_VERSION = "1.0"


# ============================================================
# STATUS
# ============================================================

class MemoryServiceStatus(str, Enum):
    NEW = "NEW"
    VALIDATING = "VALIDATING"
    COLLECTING = "COLLECTING"
    AGGREGATING = "AGGREGATING"
    READY = "READY"
    CONDITIONAL = "CONDITIONAL"
    REVIEW = "REVIEW"
    HOLD = "HOLD"
    INVALID = "INVALID"
    COMPLETED = "COMPLETED"
    UNKNOWN = "UNKNOWN"


# ============================================================
# SERVICE OPERATION TYPE
# ============================================================

class MemoryServiceOperation(str, Enum):
    STORE = "STORE"
    RETRIEVE = "RETRIEVE"
    SEARCH = "SEARCH"
    CONSOLIDATE = "CONSOLIDATE"
    REVIEW = "REVIEW"
    SUMMARIZE = "SUMMARIZE"
    VALIDATE = "VALIDATE"
    UNKNOWN = "UNKNOWN"


# ============================================================
# MEMORY DOMAIN
# ============================================================

class MemoryDomain(str, Enum):
    MARKET = "MARKET"
    EVIDENCE = "EVIDENCE"
    DECISION = "DECISION"
    OUTCOME = "OUTCOME"
    PATTERN = "PATTERN"
    COMPOSITE = "COMPOSITE"
    UNKNOWN = "UNKNOWN"


# ============================================================
# PRIORITY
# ============================================================

class MemoryServicePriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


# ============================================================
# SERVICE SOURCE
# ============================================================

class MemoryServiceSourceType(str, Enum):
    MARKET_MEMORY = "MARKET_MEMORY"
    EVIDENCE_MEMORY = "EVIDENCE_MEMORY"
    DECISION_MEMORY = "DECISION_MEMORY"
    OUTCOME_MEMORY = "OUTCOME_MEMORY"
    PATTERN_MEMORY = "PATTERN_MEMORY"
    MEMORY_RETRIEVAL = "MEMORY_RETRIEVAL"
    RESEARCH = "RESEARCH"
    SYSTEM = "SYSTEM"
    UNKNOWN = "UNKNOWN"


# ============================================================
# CONTRACT STATUS
# ============================================================

class MemoryServiceContractStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


# ============================================================
# REQUEST
# ============================================================

@dataclass(frozen=True)
class MemoryServiceRequest:
    market: str

    operation: MemoryServiceOperation = (
        MemoryServiceOperation.UNKNOWN
    )

    domain: MemoryDomain = MemoryDomain.UNKNOWN

    symbol: Optional[str] = None
    timeframe: Optional[str] = None
    session: Optional[str] = None
    regime: Optional[str] = None

    memory_id: Optional[str] = None
    decision_id: Optional[str] = None
    outcome_id: Optional[str] = None
    execution_id: Optional[str] = None
    position_id: Optional[str] = None
    pattern_id: Optional[str] = None

    direction: Optional[str] = None
    state: Optional[str] = None

    min_confidence: Optional[float] = None
    min_quality: Optional[float] = None

    limit: int = 50

    priority: MemoryServicePriority = (
        MemoryServicePriority.MEDIUM
    )

    include_stale: bool = False
    include_invalid: bool = False
    include_partial: bool = True

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    request_id: str = field(
        default_factory=lambda: str(uuid4())
    )


# ============================================================
# SERVICE REFERENCE
# ============================================================

@dataclass(frozen=True)
class MemoryServiceReference:
    memory_id: Optional[str]

    market_name: str

    domain: MemoryDomain

    source_type: MemoryServiceSourceType

    status: MemoryServiceStatus

    priority: MemoryServicePriority

    timestamp: Optional[datetime]

    symbol: Optional[str] = None
    timeframe: Optional[str] = None
    session: Optional[str] = None
    regime: Optional[str] = None

    memory_type: Optional[str] = None

    state: Optional[str] = None
    direction: Optional[str] = None

    confidence: Optional[float] = None
    quality: Optional[float] = None

    decision_id: Optional[str] = None
    outcome_id: Optional[str] = None
    execution_id: Optional[str] = None
    position_id: Optional[str] = None
    pattern_id: Optional[str] = None

    payload: Mapping[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# SOURCE REFERENCE
# ============================================================

@dataclass(frozen=True)
class MemoryServiceSourceReference:
    source_id: Optional[str]

    source_name: str

    source_type: MemoryServiceSourceType

    timestamp: Optional[datetime]

    provenance: Optional[str] = None

    description: Optional[str] = None

    raw_source: Optional[Mapping[str, Any]] = None


# ============================================================
# CONTRACT VALIDATION
# ============================================================

@dataclass(frozen=True)
class MemoryServiceContractValidation:
    valid: bool

    market_available: bool

    operation_defined: bool

    domain_defined: bool

    request_id_available: bool

    metadata_valid: bool

    timestamp_valid: bool

    memory_id_available: bool

    symbol_available: bool

    source_available: bool

    confidence_valid: bool

    quality_valid: bool

    limit_valid: bool

    errors: Sequence[str] = field(
        default_factory=tuple
    )

    warnings: Sequence[str] = field(
        default_factory=tuple
    )

    @property
    def is_valid(self) -> bool:
        return bool(self.valid)


# ============================================================
# INTERNAL READ HELPERS
# ============================================================

def _ms_read_value(
    value: Any,
    *names: str,
    default: Any = None,
) -> Any:

    if value is None:
        return default

    if isinstance(value, Mapping):
        for name in names:
            if name in value:
                return value[name]

    for name in names:
        if hasattr(value, name):
            return getattr(value, name)

    return default


def _ms_text(value: Any) -> Optional[str]:
    if value is None:
        return None

    text = str(value).strip()

    return text if text else None


def _ms_timestamp(value: Any) -> Optional[datetime]:

    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(
                float(value),
                tz=timezone.utc,
            )
        except (ValueError, OverflowError, OSError):
            return None

    text = str(value).strip()

    if not text:
        return None

    try:
        parsed = datetime.fromisoformat(
            text.replace("Z", "+00:00")
        )

        if parsed.tzinfo is None:
            parsed = parsed.replace(
                tzinfo=timezone.utc
            )

        return parsed

    except (ValueError, TypeError):
        return None


def _ms_float(value: Any) -> Optional[float]:

    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _ms_enum(
    value: Any,
    enum_type: type[Enum],
    default: Enum,
) -> Enum:

    if isinstance(value, enum_type):
        return value

    if value is None:
        return default

    text = str(value).strip().upper()

    for member in enum_type:
        if member.value == text:
            return member

    return default


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_memory_service_request(
    request: MemoryServiceRequest,
) -> MemoryServiceContractValidation:

    errors = []
    warnings = []

    market_available = bool(
        _ms_text(request.market)
    )

    operation_defined = (
        request.operation
        != MemoryServiceOperation.UNKNOWN
    )

    domain_defined = (
        request.domain
        != MemoryDomain.UNKNOWN
    )

    request_id_available = bool(
        _ms_text(request.request_id)
    )

    metadata_valid = isinstance(
        request.metadata,
        Mapping,
    )

    limit_valid = (
        isinstance(request.limit, int)
        and 1 <= request.limit <= 10000
    )

    confidence_valid = (
        request.min_confidence is None
        or (
            isinstance(
                request.min_confidence,
                (int, float),
            )
            and 0.0
            <= float(request.min_confidence)
            <= 100.0
        )
    )

    quality_valid = (
        request.min_quality is None
        or (
            isinstance(
                request.min_quality,
                (int, float),
            )
            and 0.0
            <= float(request.min_quality)
            <= 100.0
        )
    )

    if not market_available:
        errors.append(
            "Market is required."
        )

    if not operation_defined:
        errors.append(
            "Memory service operation is undefined."
        )

    if not domain_defined:
        errors.append(
            "Memory service domain is undefined."
        )

    if not request_id_available:
        errors.append(
            "Request ID is required."
        )

    if not metadata_valid:
        errors.append(
            "Metadata must be a mapping."
        )

    if not limit_valid:
        errors.append(
            "Limit must be between 1 and 10000."
        )

    if not confidence_valid:
        errors.append(
            "Minimum confidence must be between 0 and 100."
        )

    if not quality_valid:
        errors.append(
            "Minimum quality must be between 0 and 100."
        )

    if request.include_invalid:
        warnings.append(
            "Invalid memory records are explicitly allowed."
        )

    if request.include_stale:
        warnings.append(
            "Stale memory records are explicitly allowed."
        )

    valid = not errors

    return MemoryServiceContractValidation(
        valid=valid,
        market_available=market_available,
        operation_defined=operation_defined,
        domain_defined=domain_defined,
        request_id_available=request_id_available,
        metadata_valid=metadata_valid,
        timestamp_valid=True,
        memory_id_available=bool(
            _ms_text(request.memory_id)
        ),
        symbol_available=bool(
            _ms_text(request.symbol)
        ),
        source_available=True,
        confidence_valid=confidence_valid,
        quality_valid=quality_valid,
        limit_valid=limit_valid,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


# ============================================================
# REFERENCE BUILDER
# ============================================================

def build_memory_service_reference(
    memory: Any,
    request: Optional[MemoryServiceRequest] = None,
) -> MemoryServiceReference:

    market = _ms_text(
        _ms_read_value(
            memory,
            "market_name",
            "market",
            "exchange",
            default=(
                request.market
                if request is not None
                else ""
            ),
        )
    ) or ""

    memory_id = _ms_text(
        _ms_read_value(
            memory,
            "memory_id",
            "id",
        )
    )

    timestamp = _ms_timestamp(
        _ms_read_value(
            memory,
            "timestamp",
            "created_at",
            "updated_at",
        )
    )

    domain = _ms_enum(
        _ms_read_value(
            memory,
            "domain",
            "memory_domain",
        ),
        MemoryDomain,
        (
            request.domain
            if request is not None
            else MemoryDomain.UNKNOWN
        ),
    )

    source_type = _ms_enum(
        _ms_read_value(
            memory,
            "source_type",
            "source",
        ),
        MemoryServiceSourceType,
        MemoryServiceSourceType.UNKNOWN,
    )

    status = _ms_enum(
        _ms_read_value(
            memory,
            "status",
        ),
        MemoryServiceStatus,
        MemoryServiceStatus.UNKNOWN,
    )

    priority = _ms_enum(
        _ms_read_value(
            memory,
            "priority",
        ),
        MemoryServicePriority,
        MemoryServicePriority.MEDIUM,
    )

    return MemoryServiceReference(
        memory_id=memory_id,
        market_name=market,
        domain=domain,
        source_type=source_type,
        status=status,
        priority=priority,
        timestamp=timestamp,
        symbol=_ms_text(
            _ms_read_value(memory, "symbol")
        ),
        timeframe=_ms_text(
            _ms_read_value(memory, "timeframe")
        ),
        session=_ms_text(
            _ms_read_value(memory, "session")
        ),
        regime=_ms_text(
            _ms_read_value(memory, "regime")
        ),
        memory_type=_ms_text(
            _ms_read_value(
                memory,
                "memory_type",
                "type",
            )
        ),
        state=_ms_text(
            _ms_read_value(
                memory,
                "state",
                "memory_state",
            )
        ),
        direction=_ms_text(
            _ms_read_value(memory, "direction")
        ),
        confidence=_ms_float(
            _ms_read_value(memory, "confidence")
        ),
        quality=_ms_float(
            _ms_read_value(
                memory,
                "quality",
            )
        ),
        decision_id=_ms_text(
            _ms_read_value(memory, "decision_id")
        ),
        outcome_id=_ms_text(
            _ms_read_value(memory, "outcome_id")
        ),
        execution_id=_ms_text(
            _ms_read_value(memory, "execution_id")
        ),
        position_id=_ms_text(
            _ms_read_value(memory, "position_id")
        ),
        pattern_id=_ms_text(
            _ms_read_value(memory, "pattern_id")
        ),
        payload=(
            dict(memory)
            if isinstance(memory, Mapping)
            else {}
        ),
    )
# ============================================================
# PART 2 — DATA STATE / CONSISTENCY / READINESS / ASSESSMENT
# ============================================================


# ============================================================
# DATA STATE
# ============================================================

class MemoryServiceDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    UNKNOWN = "UNKNOWN"


# ============================================================
# CONSISTENCY
# ============================================================

class MemoryServiceConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONFLICTING = "CONFLICTING"
    INSUFFICIENT = "INSUFFICIENT"
    UNKNOWN = "UNKNOWN"


# ============================================================
# READINESS
# ============================================================

class MemoryServiceReadiness(str, Enum):
    READY = "READY"
    CONDITIONAL = "CONDITIONAL"
    NOT_READY = "NOT_READY"
    UNKNOWN = "UNKNOWN"


# ============================================================
# REQUIREMENTS
# ============================================================

@dataclass(frozen=True)
class MemoryServiceRequirements:
    request_valid: bool

    memory_available: bool
    memory_id_available: bool

    market_available: bool
    domain_defined: bool
    operation_defined: bool

    symbol_available: bool
    timestamp_available: bool
    source_available: bool

    memory_type_available: bool
    state_available: bool
    direction_available: bool

    confidence_available: bool
    quality_available: bool

    decision_id_available: bool
    outcome_id_available: bool
    execution_id_available: bool
    position_id_available: bool
    pattern_id_available: bool

    timeframe_available: bool
    session_available: bool
    regime_available: bool

    data_state: MemoryServiceDataState
    consistency: MemoryServiceConsistency
    readiness: MemoryServiceReadiness

    completeness_score: float

    warnings: Sequence[str] = field(
        default_factory=tuple
    )


# ============================================================
# ASSESSMENT
# ============================================================

@dataclass(frozen=True)
class MemoryServiceAssessment:
    readiness: MemoryServiceReadiness

    data_state: MemoryServiceDataState

    consistency: MemoryServiceConsistency

    confidence_score: float

    completeness_score: float

    strengths: Sequence[str] = field(
        default_factory=tuple
    )

    weaknesses: Sequence[str] = field(
        default_factory=tuple
    )

    rationale: str = ""


# ============================================================
# BOOLEAN HELPER
# ============================================================

def _ms_bool(value: Any) -> bool:
    return bool(value)


# ============================================================
# CONFLICT DETECTION
# ============================================================

def _ms_conflict_detected(
    reference: MemoryServiceReference,
) -> bool:

    payload = reference.payload

    if not isinstance(payload, Mapping):
        return False

    conflict_keys = (
        "conflict",
        "has_conflict",
        "is_conflicting",
        "data_conflict",
        "memory_conflict",
        "validation_conflict",
    )

    for key in conflict_keys:
        if key in payload:
            try:
                if bool(payload[key]):
                    return True
            except Exception:
                return True

    confidence = reference.confidence

    if confidence is not None:
        if confidence < 0.0 or confidence > 100.0:
            return True

    quality = reference.quality

    if quality is not None:
        if quality < 0.0 or quality > 100.0:
            return True

    return False


# ============================================================
# DATA STATE EVALUATION
# ============================================================

def evaluate_memory_service_data_state(
    reference: MemoryServiceReference,
) -> MemoryServiceDataState:

    components = (
        reference.memory_id,
        reference.market_name,
        reference.domain,
        reference.source_type,
        reference.timestamp,
        reference.symbol,
        reference.memory_type,
        reference.state,
        reference.direction,
        reference.confidence,
        reference.quality,
        reference.status,
    )

    available = sum(
        1
        for value in components
        if value is not None
        and value != ""
        and value not in {
            MemoryDomain.UNKNOWN,
            MemoryServiceSourceType.UNKNOWN,
            MemoryServiceStatus.UNKNOWN,
        }
    )

    total = len(components)

    if available == 0:
        return MemoryServiceDataState.MISSING

    if available == total:
        return MemoryServiceDataState.COMPLETE

    if available >= total * 0.50:
        return MemoryServiceDataState.PARTIAL

    return MemoryServiceDataState.UNKNOWN


# ============================================================
# CONSISTENCY EVALUATION
# ============================================================

def evaluate_memory_service_consistency(
    reference: MemoryServiceReference,
) -> MemoryServiceConsistency:

    if _ms_conflict_detected(reference):
        return MemoryServiceConsistency.CONFLICTING

    if reference.status == MemoryServiceStatus.INVALID:
        return MemoryServiceConsistency.CONFLICTING

    if reference.status == MemoryServiceStatus.UNKNOWN:
        return MemoryServiceConsistency.INSUFFICIENT

    if not reference.memory_id:
        return MemoryServiceConsistency.INSUFFICIENT

    if not reference.market_name:
        return MemoryServiceConsistency.INSUFFICIENT

    if reference.domain == MemoryDomain.UNKNOWN:
        return MemoryServiceConsistency.INSUFFICIENT

    if reference.source_type == MemoryServiceSourceType.UNKNOWN:
        return MemoryServiceConsistency.INSUFFICIENT

    return MemoryServiceConsistency.CONSISTENT


# ============================================================
# COMPLETENESS
# ============================================================

def calculate_memory_service_completeness(
    *,
    memory_available: bool,
    memory_id_available: bool,
    market_available: bool,
    domain_defined: bool,
    operation_defined: bool,
    symbol_available: bool,
    timestamp_available: bool,
    source_available: bool,
    memory_type_available: bool,
    state_available: bool,
    direction_available: bool,
    confidence_available: bool,
    quality_available: bool,
    decision_id_available: bool,
    outcome_id_available: bool,
    execution_id_available: bool,
    position_id_available: bool,
    pattern_id_available: bool,
    timeframe_available: bool,
    session_available: bool,
    regime_available: bool,
) -> float:

    checks = (
        memory_available,
        memory_id_available,
        market_available,
        domain_defined,
        operation_defined,
        symbol_available,
        timestamp_available,
        source_available,
        memory_type_available,
        state_available,
        direction_available,
        confidence_available,
        quality_available,
        decision_id_available,
        outcome_id_available,
        execution_id_available,
        position_id_available,
        pattern_id_available,
        timeframe_available,
        session_available,
        regime_available,
    )

    if not checks:
        return 0.0

    return round(
        (sum(1 for item in checks if item) / len(checks))
        * 100.0,
        2,
    )


# ============================================================
# READINESS EVALUATION
# ============================================================

def evaluate_memory_service_readiness(
    *,
    request_valid: bool,
    data_state: MemoryServiceDataState,
    consistency: MemoryServiceConsistency,
    completeness_score: float,
) -> MemoryServiceReadiness:

    if not request_valid:
        return MemoryServiceReadiness.NOT_READY

    if consistency == MemoryServiceConsistency.CONFLICTING:
        return MemoryServiceReadiness.NOT_READY

    if data_state == MemoryServiceDataState.MISSING:
        return MemoryServiceReadiness.NOT_READY

    if data_state == MemoryServiceDataState.UNKNOWN:
        return MemoryServiceReadiness.UNKNOWN

    if completeness_score >= 85.0:
        return MemoryServiceReadiness.READY

    if completeness_score >= 50.0:
        return MemoryServiceReadiness.CONDITIONAL

    return MemoryServiceReadiness.NOT_READY


# ============================================================
# CONFIDENCE
# ============================================================

def calculate_memory_service_confidence(
    *,
    completeness_score: float,
    consistency: MemoryServiceConsistency,
    data_state: MemoryServiceDataState,
) -> float:

    score = float(completeness_score)

    if consistency == MemoryServiceConsistency.CONSISTENT:
        score += 5.0

    elif consistency == MemoryServiceConsistency.CONFLICTING:
        score -= 30.0

    elif consistency == MemoryServiceConsistency.INSUFFICIENT:
        score -= 10.0

    if data_state == MemoryServiceDataState.MISSING:
        score -= 20.0

    elif data_state == MemoryServiceDataState.UNKNOWN:
        score -= 15.0

    elif data_state == MemoryServiceDataState.PARTIAL:
        score -= 5.0

    return round(
        max(0.0, min(100.0, score)),
        2,
    )


# ============================================================
# REQUIREMENTS BUILDER
# ============================================================

def evaluate_memory_service_requirements(
    request: MemoryServiceRequest,
    reference: MemoryServiceReference,
) -> MemoryServiceRequirements:

    request_validation = validate_memory_service_request(
        request
    )

    data_state = evaluate_memory_service_data_state(
        reference
    )

    consistency = evaluate_memory_service_consistency(
        reference
    )

    memory_available = bool(reference)

    memory_id_available = bool(
        reference.memory_id
    )

    market_available = bool(
        reference.market_name
    )

    domain_defined = (
        reference.domain
        != MemoryDomain.UNKNOWN
    )

    operation_defined = (
        request.operation
        != MemoryServiceOperation.UNKNOWN
    )

    symbol_available = bool(
        reference.symbol
    )

    timestamp_available = (
        reference.timestamp is not None
    )

    source_available = (
        reference.source_type
        != MemoryServiceSourceType.UNKNOWN
    )

    memory_type_available = bool(
        reference.memory_type
    )

    state_available = bool(
        reference.state
    )

    direction_available = bool(
        reference.direction
    )

    confidence_available = (
        reference.confidence is not None
    )

    quality_available = (
        reference.quality is not None
    )

    decision_id_available = bool(
        reference.decision_id
    )

    outcome_id_available = bool(
        reference.outcome_id
    )

    execution_id_available = bool(
        reference.execution_id
    )

    position_id_available = bool(
        reference.position_id
    )

    pattern_id_available = bool(
        reference.pattern_id
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

    completeness_score = (
        calculate_memory_service_completeness(
            memory_available=memory_available,
            memory_id_available=memory_id_available,
            market_available=market_available,
            domain_defined=domain_defined,
            operation_defined=operation_defined,
            symbol_available=symbol_available,
            timestamp_available=timestamp_available,
            source_available=source_available,
            memory_type_available=memory_type_available,
            state_available=state_available,
            direction_available=direction_available,
            confidence_available=confidence_available,
            quality_available=quality_available,
            decision_id_available=decision_id_available,
            outcome_id_available=outcome_id_available,
            execution_id_available=execution_id_available,
            position_id_available=position_id_available,
            pattern_id_available=pattern_id_available,
            timeframe_available=timeframe_available,
            session_available=session_available,
            regime_available=regime_available,
        )
    )

    readiness = evaluate_memory_service_readiness(
        request_valid=request_validation.valid,
        data_state=data_state,
        consistency=consistency,
        completeness_score=completeness_score,
    )

    warnings = list(
        request_validation.warnings
    )

    if data_state == MemoryServiceDataState.PARTIAL:
        warnings.append(
            "Memory service reference is partially populated."
        )

    if consistency == MemoryServiceConsistency.INSUFFICIENT:
        warnings.append(
            "Memory service consistency cannot be fully established."
        )

    if not symbol_available:
        warnings.append(
            "Symbol is unavailable."
        )

    if not timestamp_available:
        warnings.append(
            "Timestamp is unavailable."
        )

    return MemoryServiceRequirements(
        request_valid=request_validation.valid,
        memory_available=memory_available,
        memory_id_available=memory_id_available,
        market_available=market_available,
        domain_defined=domain_defined,
        operation_defined=operation_defined,
        symbol_available=symbol_available,
        timestamp_available=timestamp_available,
        source_available=source_available,
        memory_type_available=memory_type_available,
        state_available=state_available,
        direction_available=direction_available,
        confidence_available=confidence_available,
        quality_available=quality_available,
        decision_id_available=decision_id_available,
        outcome_id_available=outcome_id_available,
        execution_id_available=execution_id_available,
        position_id_available=position_id_available,
        pattern_id_available=pattern_id_available,
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
# ASSESSMENT BUILDER
# ============================================================

def build_memory_service_assessment(
    requirements: MemoryServiceRequirements,
    confidence_score: float,
) -> MemoryServiceAssessment:

    strengths = []
    weaknesses = []

    if requirements.request_valid:
        strengths.append(
            "Service request is structurally valid."
        )

    if requirements.memory_available:
        strengths.append(
            "Memory reference is available."
        )

    if requirements.market_available:
        strengths.append(
            "Market context is available."
        )

    if requirements.source_available:
        strengths.append(
            "Memory source is identified."
        )

    if requirements.consistency == (
        MemoryServiceConsistency.CONSISTENT
    ):
        strengths.append(
            "Memory reference is internally consistent."
        )

    if requirements.completeness_score >= 85.0:
        strengths.append(
            "Memory service contract is substantially complete."
        )

    missing_fields = []

    checks = (
        ("memory_id", requirements.memory_id_available),
        ("symbol", requirements.symbol_available),
        ("timestamp", requirements.timestamp_available),
        ("source", requirements.source_available),
        ("memory_type", requirements.memory_type_available),
        ("state", requirements.state_available),
        ("direction", requirements.direction_available),
        ("confidence", requirements.confidence_available),
        ("quality", requirements.quality_available),
    )

    for name, available in checks:
        if not available:
            missing_fields.append(name)

    if missing_fields:
        weaknesses.append(
            "Missing fields: "
            + ", ".join(missing_fields)
            + "."
        )

    if requirements.consistency == (
        MemoryServiceConsistency.CONFLICTING
    ):
        weaknesses.append(
            "Conflicting memory state detected."
        )

    if requirements.readiness == (
        MemoryServiceReadiness.CONDITIONAL
    ):
        weaknesses.append(
            "Service state is conditional."
        )

    if requirements.readiness == (
        MemoryServiceReadiness.NOT_READY
    ):
        weaknesses.append(
            "Memory service state is not ready."
        )

    if requirements.readiness == (
        MemoryServiceReadiness.READY
    ):
        rationale = (
            "Memory service reference is structurally complete, "
            "consistent and ready for the requested service operation."
        )

    elif requirements.readiness == (
        MemoryServiceReadiness.CONDITIONAL
    ):
        rationale = (
            "Memory service reference is partially complete and "
            "may proceed only through a conditional service path."
        )

    elif requirements.readiness == (
        MemoryServiceReadiness.NOT_READY
    ):
        rationale = (
            "Memory service request/reference is insufficient, "
            "conflicting or incomplete."
        )

    else:
        rationale = (
            "Memory service state could not be fully established."
        )

    return MemoryServiceAssessment(
        readiness=requirements.readiness,
        data_state=requirements.data_state,
        consistency=requirements.consistency,
        confidence_score=confidence_score,
        completeness_score=requirements.completeness_score,
        strengths=tuple(strengths),
        weaknesses=tuple(weaknesses),
        rationale=rationale,
    )
# ============================================================
# PART 3 — ACTION / RESULT / CONTRACT / ENGINE
# ============================================================


# ============================================================
# ACTION STATE
# ============================================================

class MemoryServiceActionState(str, Enum):
    NONE = "NONE"
    STORE = "STORE"
    RETRIEVE = "RETRIEVE"
    SEARCH = "SEARCH"
    CONSOLIDATE = "CONSOLIDATE"
    REVIEW = "REVIEW"
    VALIDATE = "VALIDATE"
    HOLD = "HOLD"
    INVALIDATE = "INVALIDATE"
    COMPLETE = "COMPLETE"


# ============================================================
# CONTRACT STATE
# ============================================================

class MemoryServiceContractState(str, Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


# ============================================================
# RESULT STATUS
# ============================================================

class MemoryServiceResultStatus(str, Enum):
    STORED = "STORED"
    FOUND = "FOUND"
    PARTIAL = "PARTIAL"
    CONSOLIDATED = "CONSOLIDATED"
    REVIEW = "REVIEW"
    HOLD = "HOLD"
    INVALIDATED = "INVALIDATED"
    COMPLETED = "COMPLETED"
    EMPTY = "EMPTY"
    INVALID = "INVALID"


# ============================================================
# ACTION
# ============================================================

@dataclass(frozen=True)
class MemoryServiceAction:
    state: MemoryServiceActionState

    action_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    reason: str = ""

    is_action_request: bool = False


# ============================================================
# RESULT
# ============================================================

@dataclass(frozen=True)
class MemoryServiceResult:
    status: MemoryServiceResultStatus

    result_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    request_id: str = ""

    reference: Optional[MemoryServiceReference] = None

    references: Sequence[MemoryServiceReference] = field(
        default_factory=tuple
    )

    assessment: Optional[MemoryServiceAssessment] = None

    action: Optional[MemoryServiceAction] = None

    matched_count: int = 0

    returned_count: int = 0

    warnings: Sequence[str] = field(
        default_factory=tuple
    )

    errors: Sequence[str] = field(
        default_factory=tuple
    )

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# ============================================================
# CONTRACT
# ============================================================

@dataclass(frozen=True)
class MemoryServiceContract:
    state: MemoryServiceContractState

    contract_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    request_id: str = ""

    result_id: str = ""

    valid: bool = False

    request_valid: bool = False

    assessment_available: bool = False

    result_available: bool = False

    reference_available: bool = False

    errors: Sequence[str] = field(
        default_factory=tuple
    )

    warnings: Sequence[str] = field(
        default_factory=tuple
    )


# ============================================================
# RESULT STATUS BUILDER
# ============================================================

def determine_memory_service_result_status(
    request: MemoryServiceRequest,
    assessment: MemoryServiceAssessment,
    references: Sequence[MemoryServiceReference] = (),
) -> MemoryServiceResultStatus:

    if assessment.consistency == (
        MemoryServiceConsistency.CONFLICTING
    ):
        return MemoryServiceResultStatus.INVALIDATED

    if assessment.readiness == (
        MemoryServiceReadiness.NOT_READY
    ):
        return MemoryServiceResultStatus.HOLD

    if assessment.readiness == (
        MemoryServiceReadiness.UNKNOWN
    ):
        return MemoryServiceResultStatus.REVIEW

    if request.operation == MemoryServiceOperation.STORE:
        if assessment.readiness == MemoryServiceReadiness.READY:
            return MemoryServiceResultStatus.STORED

        return MemoryServiceResultStatus.PARTIAL

    if request.operation in {
        MemoryServiceOperation.RETRIEVE,
        MemoryServiceOperation.SEARCH,
    }:
        if references:
            if assessment.readiness == (
                MemoryServiceReadiness.READY
            ):
                return MemoryServiceResultStatus.FOUND

            return MemoryServiceResultStatus.PARTIAL

        return MemoryServiceResultStatus.EMPTY

    if request.operation == MemoryServiceOperation.CONSOLIDATE:
        if assessment.readiness == MemoryServiceReadiness.READY:
            return MemoryServiceResultStatus.CONSOLIDATED

        return MemoryServiceResultStatus.PARTIAL

    if request.operation == MemoryServiceOperation.REVIEW:
        return MemoryServiceResultStatus.REVIEW

    if request.operation == MemoryServiceOperation.VALIDATE:
        if assessment.readiness == MemoryServiceReadiness.READY:
            return MemoryServiceResultStatus.COMPLETED

        return MemoryServiceResultStatus.REVIEW

    if request.operation == MemoryServiceOperation.SUMMARIZE:
        if references:
            return MemoryServiceResultStatus.COMPLETED

        return MemoryServiceResultStatus.EMPTY

    return MemoryServiceResultStatus.REVIEW


# ============================================================
# ACTION BUILDER
# ============================================================

def build_memory_service_action(
    request: MemoryServiceRequest,
    status: MemoryServiceResultStatus,
) -> MemoryServiceAction:

    if status == MemoryServiceResultStatus.STORED:
        return MemoryServiceAction(
            state=MemoryServiceActionState.STORE,
            reason="Memory record passed service validation.",
        )

    if status == MemoryServiceResultStatus.FOUND:
        return MemoryServiceAction(
            state=MemoryServiceActionState.RETRIEVE,
            reason="Requested memory records are available.",
        )

    if status == MemoryServiceResultStatus.PARTIAL:
        if request.operation == MemoryServiceOperation.STORE:
            state = MemoryServiceActionState.STORE
        elif request.operation in {
            MemoryServiceOperation.RETRIEVE,
            MemoryServiceOperation.SEARCH,
        }:
            state = MemoryServiceActionState.RETRIEVE
        elif request.operation == MemoryServiceOperation.CONSOLIDATE:
            state = MemoryServiceActionState.CONSOLIDATE
        else:
            state = MemoryServiceActionState.REVIEW

        return MemoryServiceAction(
            state=state,
            reason="Service operation is conditionally available.",
        )

    if status == MemoryServiceResultStatus.CONSOLIDATED:
        return MemoryServiceAction(
            state=MemoryServiceActionState.CONSOLIDATE,
            reason="Memory consolidation passed service assessment.",
        )

    if status == MemoryServiceResultStatus.REVIEW:
        return MemoryServiceAction(
            state=MemoryServiceActionState.REVIEW,
            reason="Memory service result requires review.",
        )

    if status == MemoryServiceResultStatus.HOLD:
        return MemoryServiceAction(
            state=MemoryServiceActionState.HOLD,
            reason="Memory service operation cannot safely advance.",
        )

    if status == MemoryServiceResultStatus.INVALIDATED:
        return MemoryServiceAction(
            state=MemoryServiceActionState.INVALIDATE,
            reason="Memory service state is conflicting or invalid.",
        )

    if status == MemoryServiceResultStatus.COMPLETED:
        return MemoryServiceAction(
            state=MemoryServiceActionState.COMPLETE,
            reason="Memory service operation completed.",
        )

    if status == MemoryServiceResultStatus.EMPTY:
        return MemoryServiceAction(
            state=MemoryServiceActionState.SEARCH,
            reason="No qualifying memory record was available.",
        )

    return MemoryServiceAction(
        state=MemoryServiceActionState.NONE,
        reason="No service action determined.",
    )


# ============================================================
# RESULT BUILDER
# ============================================================

def build_memory_service_result(
    request: MemoryServiceRequest,
    assessment: MemoryServiceAssessment,
    references: Sequence[MemoryServiceReference] = (),
) -> MemoryServiceResult:

    refs = tuple(references)

    status = determine_memory_service_result_status(
        request=request,
        assessment=assessment,
        references=refs,
    )

    action = build_memory_service_action(
        request=request,
        status=status,
    )

    errors = []

    if assessment.consistency == (
        MemoryServiceConsistency.CONFLICTING
    ):
        errors.append(
            "Conflicting memory service state detected."
        )

    if status == MemoryServiceResultStatus.INVALIDATED:
        errors.append(
            "Memory service result invalidated."
        )

    return MemoryServiceResult(
        status=status,
        request_id=request.request_id,
        reference=refs[0] if refs else None,
        references=refs[:request.limit],
        assessment=assessment,
        action=action,
        matched_count=len(refs),
        returned_count=min(
            len(refs),
            request.limit,
        ),
        warnings=tuple(
            assessment.weaknesses
        ),
        errors=tuple(errors),
    )


# ============================================================
# CONTRACT BUILDER
# ============================================================

def build_memory_service_contract(
    request: MemoryServiceRequest,
    result: MemoryServiceResult,
) -> MemoryServiceContract:

    validation = validate_memory_service_request(
        request
    )

    errors = list(result.errors)
    warnings = list(result.warnings)

    request_valid = bool(validation.valid)

    assessment_available = (
        result.assessment is not None
    )

    result_available = (
        result.status
        not in {
            MemoryServiceResultStatus.INVALID,
            MemoryServiceResultStatus.INVALIDATED,
        }
    )

    reference_available = bool(
        result.reference
        or result.references
    )

    if not request_valid:
        errors.extend(validation.errors)

    if not request_valid:
        state = MemoryServiceContractState.INVALID
        valid = False

    elif result.status == (
        MemoryServiceResultStatus.INVALIDATED
    ):
        state = MemoryServiceContractState.INVALID
        valid = False

    elif result.status == MemoryServiceResultStatus.HOLD:
        state = MemoryServiceContractState.BLOCKED
        valid = False

    elif not assessment_available:
        state = MemoryServiceContractState.INCOMPLETE
        valid = False

    elif result.status == MemoryServiceResultStatus.REVIEW:
        state = MemoryServiceContractState.INCOMPLETE
        valid = False

    else:
        state = MemoryServiceContractState.COMPLETE
        valid = True

    return MemoryServiceContract(
        state=state,
        request_id=request.request_id,
        result_id=result.result_id,
        valid=valid,
        request_valid=request_valid,
        assessment_available=assessment_available,
        result_available=result_available,
        reference_available=reference_available,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


# ============================================================
# MEMORY SERVICE ENGINE
# ============================================================

class MemoryServiceEngine:
    """
    Unified Memory Service.

    Responsibilities:
    - validate service requests
    - normalize memory records
    - evaluate memory state
    - evaluate consistency
    - assess readiness
    - route memory operations
    - build service result
    - build service contract

    The service coordinates memory subsystems.

    It does NOT:
    - generate trading decisions
    - modify D13
    - override Risk
    - override CAS
    - authorize execution
    - execute orders
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    @property
    def engine_name(self) -> str:
        return MEMORY_SERVICE_ENGINE

    @property
    def version(self) -> str:
        return MEMORY_SERVICE_VERSION

    def evaluate(
        self,
        request: MemoryServiceRequest,
        memory: Any,
    ) -> MemoryServiceResult:

        validation = validate_memory_service_request(
            request
        )

        if not validation.valid:

            assessment = MemoryServiceAssessment(
                readiness=MemoryServiceReadiness.NOT_READY,
                data_state=MemoryServiceDataState.UNKNOWN,
                consistency=MemoryServiceConsistency.INSUFFICIENT,
                confidence_score=0.0,
                completeness_score=0.0,
                strengths=(),
                weaknesses=tuple(
                    validation.errors
                ),
                rationale=(
                    "Memory service request validation failed."
                ),
            )

            return MemoryServiceResult(
                status=MemoryServiceResultStatus.INVALID,
                request_id=request.request_id,
                assessment=assessment,
                action=MemoryServiceAction(
                    state=MemoryServiceActionState.INVALIDATE,
                    reason=(
                        "Invalid memory service request."
                    ),
                ),
                errors=tuple(
                    validation.errors
                ),
            )

        reference = build_memory_service_reference(
            memory=memory,
            request=request,
        )

        data_state = evaluate_memory_service_data_state(
            reference
        )

        consistency = evaluate_memory_service_consistency(
            reference
        )

        requirements = evaluate_memory_service_requirements(
            request=request,
            reference=reference,
        )

        confidence_score = (
            calculate_memory_service_confidence(
                completeness_score=(
                    requirements.completeness_score
                ),
                consistency=consistency,
                data_state=data_state,
            )
        )

        assessment = build_memory_service_assessment(
            requirements=requirements,
            confidence_score=confidence_score,
        )

        return build_memory_service_result(
            request=request,
            assessment=assessment,
            references=(reference,),
        )

    def search(
        self,
        request: MemoryServiceRequest,
        memories: Sequence[Any],
    ) -> MemoryServiceResult:

        validation = validate_memory_service_request(
            request
        )

        if not validation.valid:
            return self.evaluate(
                request=request,
                memory={},
            )

        references = []

        for memory in memories:

            reference = build_memory_service_reference(
                memory=memory,
                request=request,
            )

            data_state = (
                evaluate_memory_service_data_state(
                    reference
                )
            )

            consistency = (
                evaluate_memory_service_consistency(
                    reference
                )
            )

            if consistency == (
                MemoryServiceConsistency.CONFLICTING
            ):
                continue

            if data_state == (
                MemoryServiceDataState.MISSING
            ):
                continue

            if (
                reference.status
                == MemoryServiceStatus.INVALID
                and not request.include_invalid
            ):
                continue

            if (
                reference.status
                == MemoryServiceStatus.UNKNOWN
            ):
                continue

            if (
                reference.status
                == MemoryServiceStatus.READY
                or reference.status
                == MemoryServiceStatus.COMPLETED
                or reference.status
                == MemoryServiceStatus.CONDITIONAL
            ):
                references.append(reference)

            if len(references) >= request.limit:
                break

        if references:

            primary = references[0]

            requirements = (
                evaluate_memory_service_requirements(
                    request=request,
                    reference=primary,
                )
            )

            confidence_score = (
                calculate_memory_service_confidence(
                    completeness_score=(
                        requirements.completeness_score
                    ),
                    consistency=(
                        requirements.consistency
                    ),
                    data_state=(
                        requirements.data_state
                    ),
                )
            )

            assessment = (
                build_memory_service_assessment(
                    requirements=requirements,
                    confidence_score=confidence_score,
                )
            )

        else:

            assessment = MemoryServiceAssessment(
                readiness=MemoryServiceReadiness.NOT_READY,
                data_state=MemoryServiceDataState.MISSING,
                consistency=MemoryServiceConsistency.INSUFFICIENT,
                confidence_score=0.0,
                completeness_score=0.0,
                strengths=(),
                weaknesses=(
                    "No qualifying memory records found.",
                ),
                rationale=(
                    "No memory record satisfied the "
                    "requested service constraints."
                ),
            )

        return build_memory_service_result(
            request=request,
            assessment=assessment,
            references=tuple(references),
        )

    def retrieve(
        self,
        request: MemoryServiceRequest,
        memories: Sequence[Any],
    ) -> MemoryServiceResult:

        return self.search(
            request=request,
            memories=memories,
        )

    def store(
        self,
        request: MemoryServiceRequest,
        memory: Any,
    ) -> MemoryServiceResult:

        store_request = MemoryServiceRequest(
            market=request.market,
            operation=MemoryServiceOperation.STORE,
            domain=request.domain,
            symbol=request.symbol,
            timeframe=request.timeframe,
            session=request.session,
            regime=request.regime,
            memory_id=request.memory_id,
            decision_id=request.decision_id,
            outcome_id=request.outcome_id,
            execution_id=request.execution_id,
            position_id=request.position_id,
            pattern_id=request.pattern_id,
            direction=request.direction,
            state=request.state,
            min_confidence=request.min_confidence,
            min_quality=request.min_quality,
            limit=request.limit,
            priority=request.priority,
            include_stale=request.include_stale,
            include_invalid=request.include_invalid,
            include_partial=request.include_partial,
            metadata=request.metadata,
            request_id=request.request_id,
        )

        return self.evaluate(
            request=store_request,
            memory=memory,
        )

    def review(
        self,
        result: MemoryServiceResult,
    ) -> MemoryServiceResult:

        if result.status in {
            MemoryServiceResultStatus.INVALID,
            MemoryServiceResultStatus.INVALIDATED,
        }:
            return result

        return MemoryServiceResult(
            status=MemoryServiceResultStatus.REVIEW,
            result_id=result.result_id,
            request_id=result.request_id,
            reference=result.reference,
            references=tuple(result.references),
            assessment=result.assessment,
            action=MemoryServiceAction(
                state=MemoryServiceActionState.REVIEW,
                reason=(
                    "Memory service result explicitly "
                    "placed into review."
                ),
            ),
            matched_count=result.matched_count,
            returned_count=result.returned_count,
            warnings=result.warnings,
            errors=result.errors,
            timestamp=result.timestamp,
        )


# ============================================================
# SINGLETON
# ============================================================

_MEMORY_SERVICE_ENGINE = MemoryServiceEngine()


# ============================================================
# PUBLIC OPERATIONS
# ============================================================

def evaluate_memory_service(
    request: MemoryServiceRequest,
    memory: Any,
) -> MemoryServiceResult:

    return _MEMORY_SERVICE_ENGINE.evaluate(
        request=request,
        memory=memory,
    )


def search_memory_service(
    request: MemoryServiceRequest,
    memories: Sequence[Any],
) -> MemoryServiceResult:

    return _MEMORY_SERVICE_ENGINE.search(
        request=request,
        memories=memories,
    )


def retrieve_memory_service(
    request: MemoryServiceRequest,
    memories: Sequence[Any],
) -> MemoryServiceResult:

    return _MEMORY_SERVICE_ENGINE.retrieve(
        request=request,
        memories=memories,
    )


def store_memory_service(
    request: MemoryServiceRequest,
    memory: Any,
) -> MemoryServiceResult:

    return _MEMORY_SERVICE_ENGINE.store(
        request=request,
        memory=memory,
    )


def review_memory_service(
    result: MemoryServiceResult,
) -> MemoryServiceResult:

    return _MEMORY_SERVICE_ENGINE.review(result)


def get_memory_service_engine() -> MemoryServiceEngine:

    return _MEMORY_SERVICE_ENGINE
# ============================================================
# MEMORY SERVICE — PART 4/5
# Validation • Readiness • Accessors • Audit • Safety • Authority
# ============================================================


def validate_memory_service_result(
    result: Optional[MemoryServiceResult],
) -> bool:
    """Validate a MemoryServiceResult without granting execution authority."""

    if not isinstance(result, MemoryServiceResult):
        return False

    if not result.result_id or not result.request_id:
        return False

    if result.returned_count < 0:
        return False

    if result.matched_count < 0:
        return False

    if result.returned_count > result.matched_count:
        return False

    if result.returned_count != len(result.references):
        return False

    if result.status in {
        MemoryServiceResultStatus.INVALID,
        MemoryServiceResultStatus.INVALIDATED,
    }:
        return False

    if result.assessment is None:
        return False

    return True


def validate_memory_service_contract(
    contract: Optional[MemoryServiceContract],
) -> bool:
    """Validate the memory-service contract itself."""

    if not isinstance(contract, MemoryServiceContract):
        return False

    if not contract.contract_id or not contract.request_id:
        return False

    if contract.valid and contract.state != MemoryServiceContractState.COMPLETE:
        return False

    if contract.state in {
        MemoryServiceContractState.INVALID,
        MemoryServiceContractState.BLOCKED,
    }:
        return False

    return True


def memory_service_ready(
    result: Optional[MemoryServiceResult],
) -> bool:
    """
    Strict memory-service readiness gate.

    READY means the memory result is structurally reliable enough
    to be consumed as historical/contextual memory.

    This function NEVER authorizes a trade, order, position change,
    execution, D13 override, Risk override, or CAS override.
    """

    if not validate_memory_service_result(result):
        return False

    assessment = result.assessment
    requirements = result.requirements

    if assessment is None or requirements is None:
        return False

    if result.status not in {
        MemoryServiceResultStatus.STORED,
        MemoryServiceResultStatus.FOUND,
        MemoryServiceResultStatus.CONSOLIDATED,
        MemoryServiceResultStatus.COMPLETED,
    }:
        return False

    if assessment.readiness != MemoryServiceReadiness.READY:
        return False

    if assessment.consistency != MemoryServiceConsistency.CONSISTENT:
        return False

    if assessment.data_state != MemoryServiceDataState.COMPLETE:
        return False

    if assessment.confidence_score < 80.0:
        return False

    if assessment.completeness_score < 85.0:
        return False

    if not requirements.request_valid:
        return False

    if not requirements.memory_available:
        return False

    if not requirements.memory_id_available:
        return False

    if not requirements.market_available:
        return False

    if not requirements.domain_defined:
        return False

    if not requirements.source_available:
        return False

    if not requirements.timestamp_available:
        return False

    if not result.references:
        return False

    return True


def memory_service_can_advance(
    result: Optional[MemoryServiceResult],
) -> bool:
    """
    Determine whether memory-service output may move to the next
    non-authoritative processing stage.
    """

    if not validate_memory_service_result(result):
        return False

    assessment = result.assessment

    if assessment is None:
        return False

    if result.status in {
        MemoryServiceResultStatus.INVALID,
        MemoryServiceResultStatus.INVALIDATED,
        MemoryServiceResultStatus.HOLD,
    }:
        return False

    if assessment.consistency == MemoryServiceConsistency.CONFLICTING:
        return False

    if assessment.data_state in {
        MemoryServiceDataState.MISSING,
        MemoryServiceDataState.UNKNOWN,
    }:
        return False

    if assessment.confidence_score < 50.0:
        return False

    if assessment.completeness_score < 50.0:
        return False

    if assessment.readiness not in {
        MemoryServiceReadiness.READY,
        MemoryServiceReadiness.CONDITIONAL,
    }:
        return False

    return True


# ------------------------------------------------------------
# ACCESSORS
# ------------------------------------------------------------

def get_memory_service_status(
    result: Optional[MemoryServiceResult],
) -> MemoryServiceResultStatus:
    if not isinstance(result, MemoryServiceResult):
        return MemoryServiceResultStatus.INVALID
    return result.status


def get_memory_service_readiness(
    result: Optional[MemoryServiceResult],
) -> MemoryServiceReadiness:
    if not isinstance(result, MemoryServiceResult):
        return MemoryServiceReadiness.UNKNOWN
    if result.assessment is None:
        return MemoryServiceReadiness.UNKNOWN
    return result.assessment.readiness


def get_memory_service_data_state(
    result: Optional[MemoryServiceResult],
) -> MemoryServiceDataState:
    if not isinstance(result, MemoryServiceResult):
        return MemoryServiceDataState.UNKNOWN
    if result.assessment is None:
        return MemoryServiceDataState.UNKNOWN
    return result.assessment.data_state


def get_memory_service_consistency(
    result: Optional[MemoryServiceResult],
) -> MemoryServiceConsistency:
    if not isinstance(result, MemoryServiceResult):
        return MemoryServiceConsistency.UNKNOWN
    if result.assessment is None:
        return MemoryServiceConsistency.UNKNOWN
    return result.assessment.consistency


def get_memory_service_confidence(
    result: Optional[MemoryServiceResult],
) -> float:
    if not isinstance(result, MemoryServiceResult):
        return 0.0
    if result.assessment is None:
        return 0.0
    return float(result.assessment.confidence_score)


def get_memory_service_completeness(
    result: Optional[MemoryServiceResult],
) -> float:
    if not isinstance(result, MemoryServiceResult):
        return 0.0
    if result.assessment is None:
        return 0.0
    return float(result.assessment.completeness_score)


def get_memory_service_primary_reference(
    result: Optional[MemoryServiceResult],
) -> Optional[MemoryServiceReference]:
    if not isinstance(result, MemoryServiceResult):
        return None

    if not result.references:
        return None

    return result.references[0]


def get_memory_service_reference_count(
    result: Optional[MemoryServiceResult],
) -> int:
    if not isinstance(result, MemoryServiceResult):
        return 0
    return len(result.references)


def get_memory_service_memory_ids(
    result: Optional[MemoryServiceResult],
) -> tuple[str, ...]:
    if not isinstance(result, MemoryServiceResult):
        return ()

    return tuple(
        ref.memory_id
        for ref in result.references
        if ref.memory_id
    )


def get_memory_service_decision_ids(
    result: Optional[MemoryServiceResult],
) -> tuple[str, ...]:
    if not isinstance(result, MemoryServiceResult):
        return ()

    return tuple(
        ref.decision_id
        for ref in result.references
        if ref.decision_id
    )


def get_memory_service_outcome_ids(
    result: Optional[MemoryServiceResult],
) -> tuple[str, ...]:
    if not isinstance(result, MemoryServiceResult):
        return ()

    return tuple(
        ref.outcome_id
        for ref in result.references
        if ref.outcome_id
    )


def get_memory_service_execution_ids(
    result: Optional[MemoryServiceResult],
) -> tuple[str, ...]:
    if not isinstance(result, MemoryServiceResult):
        return ()

    return tuple(
        ref.execution_id
        for ref in result.references
        if ref.execution_id
    )


def get_memory_service_position_ids(
    result: Optional[MemoryServiceResult],
) -> tuple[str, ...]:
    if not isinstance(result, MemoryServiceResult):
        return ()

    return tuple(
        ref.position_id
        for ref in result.references
        if ref.position_id
    )


def get_memory_service_pattern_ids(
    result: Optional[MemoryServiceResult],
) -> tuple[str, ...]:
    if not isinstance(result, MemoryServiceResult):
        return ()

    return tuple(
        ref.pattern_id
        for ref in result.references
        if ref.pattern_id
    )


def get_memory_service_directions(
    result: Optional[MemoryServiceResult],
) -> tuple[str, ...]:
    if not isinstance(result, MemoryServiceResult):
        return ()

    return tuple(
        ref.direction
        for ref in result.references
        if ref.direction
    )


# ------------------------------------------------------------
# AUDIT
# ------------------------------------------------------------

def audit_memory_service(
    result: Optional[MemoryServiceResult],
) -> dict[str, Any]:
    """Return a non-authoritative audit snapshot."""

    if not isinstance(result, MemoryServiceResult):
        return {
            "valid_result": False,
            "status": MemoryServiceResultStatus.INVALID.value,
            "ready": False,
            "can_advance": False,
            "safe": False,
        }

    assessment = result.assessment

    return {
        "engine": MEMORY_SERVICE_ENGINE,
        "version": MEMORY_SERVICE_VERSION,
        "result_id": result.result_id,
        "request_id": result.request_id,
        "status": result.status.value,
        "valid_result": validate_memory_service_result(result),
        "readiness": (
            assessment.readiness.value
            if assessment is not None
            else MemoryServiceReadiness.UNKNOWN.value
        ),
        "data_state": (
            assessment.data_state.value
            if assessment is not None
            else MemoryServiceDataState.UNKNOWN.value
        ),
        "consistency": (
            assessment.consistency.value
            if assessment is not None
            else MemoryServiceConsistency.UNKNOWN.value
        ),
        "confidence": get_memory_service_confidence(result),
        "completeness": get_memory_service_completeness(result),
        "reference_count": get_memory_service_reference_count(result),
        "ready": memory_service_ready(result),
        "can_advance": memory_service_can_advance(result),
        "safe": memory_service_is_safe(result),
        "conflict": memory_service_has_conflict(result),

        # Authority boundaries
        "generates_decision": memory_service_generates_decision(),
        "modifies_d13": memory_service_modifies_d13(),
        "overrides_d13": memory_service_overrides_d13(),
        "overrides_risk": memory_service_overrides_risk(),
        "overrides_cas": memory_service_overrides_cas(),
        "authorizes_execution": memory_service_authorizes_execution(),
        "allows_order": memory_service_allows_order(),
        "allows_trade": memory_service_allows_trade(),
        "allows_position_change": memory_service_allows_position_change(),
        "execution_authority": memory_service_execution_authority(),
    }


# ------------------------------------------------------------
# SAFETY / CONFLICT / REVIEW
# ------------------------------------------------------------

def memory_service_is_safe(
    result: Optional[MemoryServiceResult],
) -> bool:
    if not validate_memory_service_result(result):
        return False

    if result.status in {
        MemoryServiceResultStatus.INVALID,
        MemoryServiceResultStatus.INVALIDATED,
    }:
        return False

    if memory_service_has_conflict(result):
        return False

    return True


def memory_service_has_conflict(
    result: Optional[MemoryServiceResult],
) -> bool:
    if not isinstance(result, MemoryServiceResult):
        return True

    if result.assessment is None:
        return True

    return (
        result.assessment.consistency
        == MemoryServiceConsistency.CONFLICTING
    )


def memory_service_requires_review(
    result: Optional[MemoryServiceResult],
) -> bool:
    if not isinstance(result, MemoryServiceResult):
        return True

    if result.status in {
        MemoryServiceResultStatus.REVIEW,
        MemoryServiceResultStatus.PARTIAL,
    }:
        return True

    if result.assessment is None:
        return True

    return result.assessment.readiness in {
        MemoryServiceReadiness.CONDITIONAL,
        MemoryServiceReadiness.NOT_READY,
        MemoryServiceReadiness.UNKNOWN,
    }


# ------------------------------------------------------------
# AUTHORITY BOUNDARIES
# ------------------------------------------------------------

def memory_service_generates_decision() -> bool:
    return False


def memory_service_modifies_d13() -> bool:
    return False


def memory_service_overrides_d13() -> bool:
    return False


def memory_service_overrides_risk() -> bool:
    return False


def memory_service_overrides_cas() -> bool:
    return False


def memory_service_authorizes_execution() -> bool:
    return False


def memory_service_allows_order() -> bool:
    return False


def memory_service_allows_trade() -> bool:
    return False


def memory_service_allows_position_change() -> bool:
    return False


def memory_service_execution_authority() -> bool:
    return False


def memory_service_can_execute(
    result: Optional[MemoryServiceResult],
) -> bool:
    """
    Explicit hard-stop.

    Memory Service can NEVER become an execution authority,
    regardless of result quality or readiness.
    """
    return False


# ------------------------------------------------------------
# ENGINE INFORMATION / HEALTH
# ------------------------------------------------------------

def get_memory_service_engine_info() -> dict[str, Any]:
    return {
        "engine": MEMORY_SERVICE_ENGINE,
        "version": MEMORY_SERVICE_VERSION,
        "status": MemoryServiceStatus.READY.value,
        "domains": [domain.value for domain in MemoryDomain],
        "operations": [
            operation.value
            for operation in MemoryServiceOperation
        ],
        "decision_authority": False,
        "risk_authority": False,
        "cas_authority": False,
        "execution_authority": False,
        "d13_override": False,
    }


def memory_service_health_check() -> dict[str, Any]:
    return {
        "healthy": True,
        "engine": MEMORY_SERVICE_ENGINE,
        "version": MEMORY_SERVICE_VERSION,
        "contract_validation": True,
        "readiness_gate": True,
        "safety_boundary": True,
        "decision_authority": False,
        "risk_authority": False,
        "cas_authority": False,
        "execution_authority": False,
    }
# ============================================================
# MEMORY SERVICE — PART 5/5
# Lifecycle • Serialization • Integrity • Freeze • Retain
# Reject • Authority Statement • Public Exports
# ============================================================


# ------------------------------------------------------------
# LIFECYCLE HELPERS
# ------------------------------------------------------------

def memory_service_is_stored(
    result: Optional[MemoryServiceResult],
) -> bool:
    if not isinstance(result, MemoryServiceResult):
        return False

    return result.status == MemoryServiceResultStatus.STORED


def memory_service_is_found(
    result: Optional[MemoryServiceResult],
) -> bool:
    if not isinstance(result, MemoryServiceResult):
        return False

    return result.status == MemoryServiceResultStatus.FOUND


def memory_service_is_partial(
    result: Optional[MemoryServiceResult],
) -> bool:
    if not isinstance(result, MemoryServiceResult):
        return False

    return result.status == MemoryServiceResultStatus.PARTIAL


def memory_service_is_consolidated(
    result: Optional[MemoryServiceResult],
) -> bool:
    if not isinstance(result, MemoryServiceResult):
        return False

    return result.status == MemoryServiceResultStatus.CONSOLIDATED


def memory_service_is_completed(
    result: Optional[MemoryServiceResult],
) -> bool:
    if not isinstance(result, MemoryServiceResult):
        return False

    return result.status == MemoryServiceResultStatus.COMPLETED


def memory_service_is_empty(
    result: Optional[MemoryServiceResult],
) -> bool:
    if not isinstance(result, MemoryServiceResult):
        return False

    return result.status == MemoryServiceResultStatus.EMPTY


def memory_service_is_invalid(
    result: Optional[MemoryServiceResult],
) -> bool:
    if not isinstance(result, MemoryServiceResult):
        return True

    return result.status in {
        MemoryServiceResultStatus.INVALID,
        MemoryServiceResultStatus.INVALIDATED,
    }


def memory_service_lifecycle_state(
    result: Optional[MemoryServiceResult],
) -> str:
    if not isinstance(result, MemoryServiceResult):
        return MemoryServiceResultStatus.INVALID.value

    return result.status.value


# ------------------------------------------------------------
# SERIALIZATION HELPERS
# ------------------------------------------------------------

def _ms_iso(value: Any) -> Optional[str]:
    if value is None:
        return None

    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat()

    return str(value)


def serialize_memory_service_reference(
    reference: Optional[MemoryServiceReference],
) -> dict[str, Any]:
    if not isinstance(reference, MemoryServiceReference):
        return {}

    return {
        "memory_id": reference.memory_id,
        "market_name": reference.market_name,
        "domain": reference.domain.value,
        "source_type": reference.source_type.value,
        "status": reference.status,
        "priority": reference.priority.value,
        "timestamp": _ms_iso(reference.timestamp),
        "symbol": reference.symbol,
        "timeframe": reference.timeframe,
        "session": reference.session,
        "regime": reference.regime,
        "memory_type": reference.memory_type,
        "state": reference.state,
        "direction": reference.direction,
        "confidence": reference.confidence,
        "quality": reference.quality,
        "decision_id": reference.decision_id,
        "outcome_id": reference.outcome_id,
        "execution_id": reference.execution_id,
        "position_id": reference.position_id,
        "pattern_id": reference.pattern_id,
        "payload": dict(reference.payload),
    }


def serialize_memory_service_result(
    result: Optional[MemoryServiceResult],
) -> dict[str, Any]:
    if not isinstance(result, MemoryServiceResult):
        return {}

    assessment = result.assessment
    requirements = result.requirements

    return {
        "result_id": result.result_id,
        "request_id": result.request_id,
        "status": result.status.value,
        "action": (
            result.action.action.value
            if result.action is not None
            else MemoryServiceActionState.NONE.value
        ),
        "matched_count": result.matched_count,
        "returned_count": result.returned_count,
        "references": [
            serialize_memory_service_reference(ref)
            for ref in result.references
        ],
        "assessment": (
            {
                "readiness": assessment.readiness.value,
                "data_state": assessment.data_state.value,
                "consistency": assessment.consistency.value,
                "confidence_score": assessment.confidence_score,
                "completeness_score": assessment.completeness_score,
                "strengths": list(assessment.strengths),
                "weaknesses": list(assessment.weaknesses),
                "rationale": assessment.rationale,
            }
            if assessment is not None
            else None
        ),
        "requirements": (
            {
                "request_valid": requirements.request_valid,
                "memory_available": requirements.memory_available,
                "memory_id_available": requirements.memory_id_available,
                "market_available": requirements.market_available,
                "domain_defined": requirements.domain_defined,
                "operation_defined": requirements.operation_defined,
                "symbol_available": requirements.symbol_available,
                "timestamp_available": requirements.timestamp_available,
                "source_available": requirements.source_available,
                "memory_type_available": requirements.memory_type_available,
                "state_available": requirements.state_available,
                "direction_available": requirements.direction_available,
                "confidence_available": requirements.confidence_available,
                "quality_available": requirements.quality_available,
                "decision_id_available": requirements.decision_id_available,
                "outcome_id_available": requirements.outcome_id_available,
                "execution_id_available": requirements.execution_id_available,
                "position_id_available": requirements.position_id_available,
                "pattern_id_available": requirements.pattern_id_available,
                "timeframe_available": requirements.timeframe_available,
                "session_available": requirements.session_available,
                "regime_available": requirements.regime_available,
                "data_state": requirements.data_state.value,
                "consistency": requirements.consistency.value,
                "readiness": requirements.readiness.value,
                "completeness_score": requirements.completeness_score,
                "warnings": list(requirements.warnings),
            }
            if requirements is not None
            else None
        ),
        "metadata": dict(result.metadata),
    }


def serialize_memory_service_contract(
    contract: Optional[MemoryServiceContract],
) -> dict[str, Any]:
    if not isinstance(contract, MemoryServiceContract):
        return {}

    return {
        "contract_id": contract.contract_id,
        "request_id": contract.request_id,
        "state": contract.state.value,
        "valid": contract.valid,
        "result_available": contract.result_available,
        "errors": list(contract.errors),
        "warnings": list(contract.warnings),
    }


# ------------------------------------------------------------
# INTEGRITY
# ------------------------------------------------------------

def memory_service_integrity_check(
    result: Optional[MemoryServiceResult],
) -> dict[str, Any]:
    """
    Structural integrity check.

    Integrity does not imply trading correctness or execution authority.
    """

    if not isinstance(result, MemoryServiceResult):
        return {
            "valid": False,
            "integrity": False,
            "errors": ["Invalid MemoryServiceResult"],
        }

    errors: list[str] = []

    if not result.result_id:
        errors.append("Missing result_id")

    if not result.request_id:
        errors.append("Missing request_id")

    if result.returned_count != len(result.references):
        errors.append("returned_count mismatch")

    if result.returned_count > result.matched_count:
        errors.append("returned_count exceeds matched_count")

    if result.assessment is None:
        errors.append("Missing assessment")

    if result.requirements is None:
        errors.append("Missing requirements")

    if result.status in {
        MemoryServiceResultStatus.INVALID,
        MemoryServiceResultStatus.INVALIDATED,
    }:
        errors.append("Result is invalidated/invalid")

    return {
        "valid": len(errors) == 0,
        "integrity": len(errors) == 0,
        "errors": errors,
    }


# ------------------------------------------------------------
# SUMMARY
# ------------------------------------------------------------

def summarize_memory_service(
    result: Optional[MemoryServiceResult],
) -> dict[str, Any]:
    if not isinstance(result, MemoryServiceResult):
        return {
            "valid": False,
            "status": MemoryServiceResultStatus.INVALID.value,
        }

    assessment = result.assessment

    return {
        "engine": MEMORY_SERVICE_ENGINE,
        "version": MEMORY_SERVICE_VERSION,
        "result_id": result.result_id,
        "request_id": result.request_id,
        "status": result.status.value,
        "readiness": (
            assessment.readiness.value
            if assessment is not None
            else MemoryServiceReadiness.UNKNOWN.value
        ),
        "data_state": (
            assessment.data_state.value
            if assessment is not None
            else MemoryServiceDataState.UNKNOWN.value
        ),
        "consistency": (
            assessment.consistency.value
            if assessment is not None
            else MemoryServiceConsistency.UNKNOWN.value
        ),
        "confidence": get_memory_service_confidence(result),
        "completeness": get_memory_service_completeness(result),
        "matched_count": result.matched_count,
        "returned_count": result.returned_count,
        "memory_ids": list(get_memory_service_memory_ids(result)),
        "decision_ids": list(get_memory_service_decision_ids(result)),
        "outcome_ids": list(get_memory_service_outcome_ids(result)),
        "execution_ids": list(get_memory_service_execution_ids(result)),
        "position_ids": list(get_memory_service_position_ids(result)),
        "pattern_ids": list(get_memory_service_pattern_ids(result)),
        "directions": list(get_memory_service_directions(result)),
        "ready": memory_service_ready(result),
        "can_advance": memory_service_can_advance(result),
        "safe": memory_service_is_safe(result),
    }


# ------------------------------------------------------------
# FREEZE / RETAIN / REJECT
# ------------------------------------------------------------

def freeze_memory_service(
    result: Optional[MemoryServiceResult],
) -> Optional[MemoryServiceResult]:
    """
    Freeze a valid memory-service result as completed historical
    processing output.

    Freeze does not make the result authoritative.
    """

    if not isinstance(result, MemoryServiceResult):
        return None

    if memory_service_is_invalid(result):
        return result

    return MemoryServiceResult(
        result_id=result.result_id,
        request_id=result.request_id,
        status=MemoryServiceResultStatus.COMPLETED,
        action=MemoryServiceAction(
            action=MemoryServiceActionState.COMPLETE,
            reason="Memory service result frozen",
            is_action_request=False,
        ),
        matched_count=result.matched_count,
        returned_count=result.returned_count,
        references=result.references,
        assessment=result.assessment,
        requirements=result.requirements,
        metadata=result.metadata,
    )


def retain_memory_service(
    result: Optional[MemoryServiceResult],
) -> Optional[MemoryServiceResult]:
    """
    Retain only structurally safe memory-service output.
    """

    if not isinstance(result, MemoryServiceResult):
        return None

    if not memory_service_is_safe(result):
        return None

    return result


def reject_memory_service(
    result: Optional[MemoryServiceResult],
    reason: str = "Memory service result rejected",
) -> Optional[MemoryServiceResult]:
    """
    Reject invalid/conflicting memory output.

    Rejection is a memory lifecycle operation only.
    It does not invalidate D13 or any trading decision.
    """

    if not isinstance(result, MemoryServiceResult):
        return None

    return MemoryServiceResult(
        result_id=result.result_id,
        request_id=result.request_id,
        status=MemoryServiceResultStatus.INVALIDATED,
        action=MemoryServiceAction(
            action=MemoryServiceActionState.INVALIDATE,
            reason=reason,
            is_action_request=False,
        ),
        matched_count=result.matched_count,
        returned_count=result.returned_count,
        references=result.references,
        assessment=result.assessment,
        requirements=result.requirements,
        metadata=result.metadata,
    )


# ------------------------------------------------------------
# AUTHORITY STATEMENT
# ------------------------------------------------------------

def memory_service_authority_statement() -> str:
    return (
        "Memory Service is a non-authoritative memory orchestration layer. "
        "It validates, normalizes, stores, retrieves, searches, consolidates "
        "and reviews historical/contextual memory records. "
        "It does not generate authoritative trading decisions, modify or "
        "override D13, override Risk, override CAS, authorize execution, "
        "place orders, execute trades, or change positions. "
        "D13 remains the decision authority; Risk remains the risk authority; "
        "CAS remains the authorization and execution-safety authority."
    )


# ------------------------------------------------------------
# PUBLIC EXPORTS
# ------------------------------------------------------------

__all__ = [
    # Constants
    "MEMORY_SERVICE_ENGINE",
    "MEMORY_SERVICE_VERSION",

    # Enums
    "MemoryServiceStatus",
    "MemoryServiceOperation",
    "MemoryDomain",
    "MemoryServicePriority",
    "MemoryServiceSourceType",
    "MemoryServiceContractStatus",
    "MemoryServiceDataState",
    "MemoryServiceConsistency",
    "MemoryServiceReadiness",
    "MemoryServiceActionState",
    "MemoryServiceContractState",
    "MemoryServiceResultStatus",

    # Contracts
    "MemoryServiceRequest",
    "MemoryServiceReference",
    "MemoryServiceSourceReference",
    "MemoryServiceContractValidation",
    "MemoryServiceRequirements",
    "MemoryServiceAssessment",
    "MemoryServiceAction",
    "MemoryServiceResult",
    "MemoryServiceContract",

    # Builders / validation
    "validate_memory_service_request",
    "build_memory_service_reference",
    "evaluate_memory_service_data_state",
    "evaluate_memory_service_consistency",
    "calculate_memory_service_completeness",
    "evaluate_memory_service_readiness",
    "calculate_memory_service_confidence",
    "evaluate_memory_service_requirements",
    "build_memory_service_assessment",
    "determine_memory_service_result_status",
    "build_memory_service_action",
    "build_memory_service_result",
    "build_memory_service_contract",
    "validate_memory_service_result",
    "validate_memory_service_contract",

    # Engine
    "MemoryServiceEngine",
    "get_memory_service_engine",
    "evaluate_memory_service",
    "search_memory_service",
    "retrieve_memory_service",
    "store_memory_service",
    "review_memory_service",

    # Readiness / state
    "memory_service_ready",
    "memory_service_can_advance",
    "memory_service_is_safe",
    "memory_service_has_conflict",
    "memory_service_requires_review",

    # Accessors
    "get_memory_service_status",
    "get_memory_service_readiness",
    "get_memory_service_data_state",
    "get_memory_service_consistency",
    "get_memory_service_confidence",
    "get_memory_service_completeness",
    "get_memory_service_primary_reference",
    "get_memory_service_reference_count",
    "get_memory_service_memory_ids",
    "get_memory_service_decision_ids",
    "get_memory_service_outcome_ids",
    "get_memory_service_execution_ids",
    "get_memory_service_position_ids",
    "get_memory_service_pattern_ids",
    "get_memory_service_directions",

    # Audit
    "audit_memory_service",

    # Safety / authority
    "memory_service_generates_decision",
    "memory_service_modifies_d13",
    "memory_service_overrides_d13",
    "memory_service_overrides_risk",
    "memory_service_overrides_cas",
    "memory_service_authorizes_execution",
    "memory_service_allows_order",
    "memory_service_allows_trade",
    "memory_service_allows_position_change",
    "memory_service_execution_authority",
    "memory_service_can_execute",

    # Engine info
    "get_memory_service_engine_info",
    "memory_service_health_check",

    # Lifecycle
    "memory_service_is_stored",
    "memory_service_is_found",
    "memory_service_is_partial",
    "memory_service_is_consolidated",
    "memory_service_is_completed",
    "memory_service_is_empty",
    "memory_service_is_invalid",
    "memory_service_lifecycle_state",

    # Serialization
    "serialize_memory_service_reference",
    "serialize_memory_service_result",
    "serialize_memory_service_contract",

    # Integrity / summary
    "memory_service_integrity_check",
    "summarize_memory_service",

    # Lifecycle operations
    "freeze_memory_service",
    "retain_memory_service",
    "reject_memory_service",

    # Authority
    "memory_service_authority_statement",
]