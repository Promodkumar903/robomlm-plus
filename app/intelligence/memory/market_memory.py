# ============================================================
# ROBOMLM — MARKET MEMORY
# PART 1/5 — FOUNDATION, CONTRACTS & REFERENCES
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Optional
from uuid import uuid4


# ============================================================
# ENGINE METADATA
# ============================================================

MARKET_MEMORY_ENGINE = "ROBOMLM_MARKET_MEMORY_ENGINE"
MARKET_MEMORY_VERSION = "1.0"


# ============================================================
# ENUMS
# ============================================================

class MarketMemoryStatus(str, Enum):
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


class MarketMemoryType(str, Enum):
    MARKET_STATE = "MARKET_STATE"
    MARKET_CONTEXT = "MARKET_CONTEXT"
    MARKET_REGIME = "MARKET_REGIME"
    PRICE_ACTION = "PRICE_ACTION"
    MICROSTRUCTURE = "MICROSTRUCTURE"
    DERIVATIVE = "DERIVATIVE"
    LIQUIDITY = "LIQUIDITY"
    VOLATILITY = "VOLATILITY"
    PARTICIPATION = "PARTICIPATION"
    RELATIONSHIP = "RELATIONSHIP"
    SESSION = "SESSION"
    EVENT = "EVENT"
    UNKNOWN = "UNKNOWN"


class MarketMemoryPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class MarketMemorySourceType(str, Enum):
    LIVE_MARKET = "LIVE_MARKET"
    HISTORICAL = "HISTORICAL"
    EVIDENCE = "EVIDENCE"
    DECISION = "DECISION"
    OUTCOME = "OUTCOME"
    RESEARCH = "RESEARCH"
    SYSTEM = "SYSTEM"
    UNKNOWN = "UNKNOWN"


class MarketMemoryContractStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


# ============================================================
# REQUEST CONTRACT
# ============================================================

@dataclass(frozen=True)
class MarketMemoryRequest:
    """
    Immutable request for recording or evaluating market memory.

    This contract describes memory input only.
    It does not authorize trading or execution.
    """

    market: Any
    memory_type: MarketMemoryType = MarketMemoryType.UNKNOWN
    source: Any = None
    timestamp: Optional[datetime] = None
    symbol: Optional[str] = None
    timeframe: Optional[str] = None
    session: Optional[str] = None
    regime: Optional[str] = None
    priority: MarketMemoryPriority = MarketMemoryPriority.UNKNOWN
    metadata: Mapping[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: str(uuid4()))

    def validate(self) -> bool:
        if self.market is None:
            return False

        if not self.request_id:
            return False

        if not isinstance(self.metadata, Mapping):
            return False

        if not isinstance(self.memory_type, MarketMemoryType):
            return False

        if not isinstance(self.priority, MarketMemoryPriority):
            return False

        return True


# ============================================================
# MEMORY REFERENCE
# ============================================================

@dataclass(frozen=True)
class MarketMemoryReference:
    """
    Normalized reference to a market-memory object.
    """

    memory_id: str
    market_name: Optional[str]
    symbol: Optional[str]
    memory_type: MarketMemoryType
    status: MarketMemoryStatus
    priority: MarketMemoryPriority

    timestamp: Optional[datetime] = None
    timeframe: Optional[str] = None
    session: Optional[str] = None
    regime: Optional[str] = None
    source_type: MarketMemorySourceType = MarketMemorySourceType.UNKNOWN

    raw_market: Mapping[str, Any] = field(default_factory=dict)


# ============================================================
# SOURCE REFERENCE
# ============================================================

@dataclass(frozen=True)
class MarketMemorySourceReference:
    """
    Traceability reference for the source from which memory
    was created or derived.
    """

    source_id: Optional[str] = None
    source_name: Optional[str] = None
    source_type: MarketMemorySourceType = (
        MarketMemorySourceType.UNKNOWN
    )
    source_timestamp: Optional[datetime] = None
    provenance: Optional[str] = None
    description: Optional[str] = None
    raw_source: Mapping[str, Any] = field(default_factory=dict)


# ============================================================
# CONTRACT VALIDATION
# ============================================================

@dataclass(frozen=True)
class MarketMemoryContractValidation:
    valid: bool
    market_available: bool
    memory_type_defined: bool
    priority_defined: bool
    metadata_valid: bool
    timestamp_valid: bool

    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:
        return bool(self.valid)


# ============================================================
# SAFE READ HELPERS
# ============================================================

def _mm_read_value(
    value: Any,
    key: str,
    default: Any = None,
) -> Any:
    if value is None:
        return default

    if isinstance(value, Mapping):
        return value.get(key, default)

    return getattr(value, key, default)


def _mm_text(
    value: Any,
    default: Optional[str] = None,
) -> Optional[str]:
    if value is None:
        return default

    text = str(value).strip()

    return text if text else default


def _mm_enum(
    value: Any,
    enum_type: type[Enum],
    default: Enum,
) -> Enum:
    if isinstance(value, enum_type):
        return value

    if value is None:
        return default

    try:
        return enum_type(str(value).strip().upper())
    except (ValueError, TypeError):
        return default


def _mm_timestamp(value: Any) -> Optional[datetime]:
    if isinstance(value, datetime):
        return value

    if value is None:
        return None

    if isinstance(value, str):
        try:
            return datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
        except ValueError:
            return None

    return None


# ============================================================
# MARKET REFERENCE BUILDER
# ============================================================

def build_market_memory_reference(
    market: Any,
    request: Optional[MarketMemoryRequest] = None,
) -> MarketMemoryReference:

    source = (
        request.source
        if request is not None
        else _mm_read_value(market, "source")
    )

    memory_id = _mm_text(
        _mm_read_value(market, "memory_id")
        or _mm_read_value(market, "id")
    )

    if not memory_id:
        memory_id = str(uuid4())

    market_name = _mm_text(
        _mm_read_value(market, "market_name")
        or _mm_read_value(market, "market")
        or _mm_read_value(market, "name")
    )

    symbol = _mm_text(
        (
            request.symbol
            if request is not None
            else _mm_read_value(market, "symbol")
        )
    )

    memory_type = (
        request.memory_type
        if request is not None
        else _mm_enum(
            _mm_read_value(market, "memory_type"),
            MarketMemoryType,
            MarketMemoryType.UNKNOWN,
        )
    )

    status = _mm_enum(
        _mm_read_value(market, "status"),
        MarketMemoryStatus,
        MarketMemoryStatus.NEW,
    )

    priority = (
        request.priority
        if request is not None
        else _mm_enum(
            _mm_read_value(market, "priority"),
            MarketMemoryPriority,
            MarketMemoryPriority.UNKNOWN,
        )
    )

    timestamp = (
        request.timestamp
        if request is not None and request.timestamp is not None
        else _mm_timestamp(
            _mm_read_value(market, "timestamp")
        )
    )

    timeframe = _mm_text(
        (
            request.timeframe
            if request is not None
            else _mm_read_value(market, "timeframe")
        )
    )

    session = _mm_text(
        (
            request.session
            if request is not None
            else _mm_read_value(market, "session")
        )
    )

    regime = _mm_text(
        (
            request.regime
            if request is not None
            else _mm_read_value(market, "regime")
        )
    )

    source_type = _mm_enum(
        _mm_read_value(source, "source_type"),
        MarketMemorySourceType,
        MarketMemorySourceType.UNKNOWN,
    )

    raw_market = (
        dict(market)
        if isinstance(market, Mapping)
        else {}
    )

    return MarketMemoryReference(
        memory_id=memory_id,
        market_name=market_name,
        symbol=symbol,
        memory_type=memory_type,
        status=status,
        priority=priority,
        timestamp=timestamp,
        timeframe=timeframe,
        session=session,
        regime=regime,
        source_type=source_type,
        raw_market=raw_market,
    )


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_market_memory_request(
    request: Any,
) -> MarketMemoryContractValidation:

    if not isinstance(request, MarketMemoryRequest):
        return MarketMemoryContractValidation(
            valid=False,
            market_available=False,
            memory_type_defined=False,
            priority_defined=False,
            metadata_valid=False,
            timestamp_valid=False,
            errors=("request must be MarketMemoryRequest",),
        )

    errors: list[str] = []
    warnings: list[str] = []

    market_available = request.market is not None
    memory_type_defined = (
        request.memory_type != MarketMemoryType.UNKNOWN
    )
    priority_defined = (
        request.priority != MarketMemoryPriority.UNKNOWN
    )
    metadata_valid = isinstance(
        request.metadata,
        Mapping,
    )

    timestamp_valid = (
        request.timestamp is None
        or isinstance(request.timestamp, datetime)
    )

    if not market_available:
        errors.append("market is required")

    if not request.request_id:
        errors.append("request_id is required")

    if not memory_type_defined:
        warnings.append("memory_type is UNKNOWN")

    if not priority_defined:
        warnings.append("priority is UNKNOWN")

    if not metadata_valid:
        errors.append("metadata must be Mapping")

    if not timestamp_valid:
        errors.append("timestamp must be datetime or None")

    valid = (
        len(errors) == 0
        and request.validate()
    )

    return MarketMemoryContractValidation(
        valid=valid,
        market_available=market_available,
        memory_type_defined=memory_type_defined,
        priority_defined=priority_defined,
        metadata_valid=metadata_valid,
        timestamp_valid=timestamp_valid,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )
# ============================================================
# PART 2/5 — DATA STATE, CONSISTENCY, READINESS & ASSESSMENT
# ============================================================


class MarketMemoryDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    UNKNOWN = "UNKNOWN"


class MarketMemoryConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONFLICTING = "CONFLICTING"
    INSUFFICIENT = "INSUFFICIENT"
    UNKNOWN = "UNKNOWN"


class MarketMemoryReadiness(str, Enum):
    READY = "READY"
    CONDITIONAL = "CONDITIONAL"
    NOT_READY = "NOT_READY"
    UNKNOWN = "UNKNOWN"


class MarketMemoryStrength(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


# ============================================================
# REQUIREMENTS
# ============================================================

@dataclass(frozen=True)
class MarketMemoryRequirements:
    memory_available: bool
    market_available: bool
    memory_type_defined: bool
    symbol_available: bool
    timestamp_available: bool
    timeframe_available: bool
    source_available: bool
    regime_available: bool

    data_state: MarketMemoryDataState
    consistency: MarketMemoryConsistency
    readiness: MarketMemoryReadiness

    completeness_score: float
    warnings: tuple[str, ...] = ()


# ============================================================
# ASSESSMENT
# ============================================================

@dataclass(frozen=True)
class MarketMemoryAssessment:
    readiness: MarketMemoryReadiness
    data_state: MarketMemoryDataState
    consistency: MarketMemoryConsistency
    strength: MarketMemoryStrength

    confidence_score: float
    completeness_score: float

    strengths: tuple[str, ...] = ()
    weaknesses: tuple[str, ...] = ()
    rationale: str = ""


# ============================================================
# SAFE BOOLEAN HELPER
# ============================================================

def _mm_bool(
    value: Any,
    default: bool = False,
) -> bool:
    if isinstance(value, bool):
        return value

    if value is None:
        return default

    if isinstance(value, (int, float)):
        return bool(value)

    text = str(value).strip().lower()

    if text in {"true", "yes", "1", "valid", "available"}:
        return True

    if text in {"false", "no", "0", "invalid", "missing"}:
        return False

    return default


# ============================================================
# CONFLICT DETECTION
# ============================================================

def _mm_conflict_detected(
    market: Any,
) -> bool:

    direct_conflict = _mm_read_value(
        market,
        "conflict",
    )

    if _mm_bool(direct_conflict):
        return True

    conflicts = _mm_read_value(
        market,
        "conflicts",
    )

    if isinstance(conflicts, (list, tuple, set)):
        return len(conflicts) > 0

    if isinstance(conflicts, Mapping):
        return len(conflicts) > 0

    if isinstance(conflicts, str):
        return bool(conflicts.strip())

    consistency = _mm_read_value(
        market,
        "consistency",
    )

    if consistency is not None:
        text = str(consistency).strip().upper()

        if text in {
            "CONFLICT",
            "CONFLICTING",
            "INCONSISTENT",
            "INVALID",
        }:
            return True

    return False


# ============================================================
# DATA STATE
# ============================================================

def evaluate_market_memory_data_state(
    requirements: MarketMemoryRequirements,
) -> MarketMemoryDataState:

    components = [
        requirements.memory_available,
        requirements.market_available,
        requirements.memory_type_defined,
        requirements.symbol_available,
        requirements.timestamp_available,
        requirements.source_available,
    ]

    available = sum(bool(x) for x in components)

    if available == len(components):
        return MarketMemoryDataState.COMPLETE

    if available == 0:
        return MarketMemoryDataState.MISSING

    return MarketMemoryDataState.PARTIAL


# ============================================================
# CONSISTENCY
# ============================================================

def evaluate_market_memory_consistency(
    market: Any,
) -> MarketMemoryConsistency:

    if market is None:
        return MarketMemoryConsistency.INSUFFICIENT

    if _mm_conflict_detected(market):
        return MarketMemoryConsistency.CONFLICTING

    consistency = _mm_read_value(
        market,
        "consistency",
    )

    if consistency is not None:
        text = str(consistency).strip().upper()

        if text in {
            "CONSISTENT",
            "VALID",
            "ALIGNED",
            "PASS",
            "PASSED",
        }:
            return MarketMemoryConsistency.CONSISTENT

        if text in {
            "CONFLICT",
            "CONFLICTING",
            "INCONSISTENT",
            "INVALID",
        }:
            return MarketMemoryConsistency.CONFLICTING

        if text in {
            "INSUFFICIENT",
            "UNKNOWN",
            "UNAVAILABLE",
        }:
            return MarketMemoryConsistency.INSUFFICIENT

    return MarketMemoryConsistency.UNKNOWN


# ============================================================
# REQUIREMENT EVALUATION
# ============================================================

def evaluate_market_memory_requirements(
    reference: MarketMemoryReference,
    request: Optional[MarketMemoryRequest] = None,
) -> MarketMemoryRequirements:

    raw_market = reference.raw_market

    memory_available = bool(reference.memory_id)

    market_available = (
        reference.market_name is not None
        or bool(raw_market)
    )

    memory_type_defined = (
        reference.memory_type != MarketMemoryType.UNKNOWN
    )

    symbol_available = bool(reference.symbol)

    timestamp_available = (
        reference.timestamp is not None
    )

    timeframe_available = bool(reference.timeframe)

    source_available = (
        reference.source_type
        != MarketMemorySourceType.UNKNOWN
    )

    regime_available = bool(reference.regime)

    components = [
        memory_available,
        market_available,
        memory_type_defined,
        symbol_available,
        timestamp_available,
        timeframe_available,
        source_available,
        regime_available,
    ]

    completeness_score = (
        sum(bool(x) for x in components)
        / len(components)
        * 100.0
    )

    consistency = evaluate_market_memory_consistency(
        raw_market
    )

    warnings: list[str] = []

    if not symbol_available:
        warnings.append("symbol is unavailable")

    if not timestamp_available:
        warnings.append("timestamp is unavailable")

    if not timeframe_available:
        warnings.append("timeframe is unavailable")

    if not source_available:
        warnings.append("memory source is unavailable")

    if not regime_available:
        warnings.append("market regime is unavailable")

    if consistency == MarketMemoryConsistency.CONFLICTING:
        warnings.append("market memory contains conflicting information")

    temporary_requirements = MarketMemoryRequirements(
        memory_available=memory_available,
        market_available=market_available,
        memory_type_defined=memory_type_defined,
        symbol_available=symbol_available,
        timestamp_available=timestamp_available,
        timeframe_available=timeframe_available,
        source_available=source_available,
        regime_available=regime_available,
        data_state=MarketMemoryDataState.UNKNOWN,
        consistency=consistency,
        readiness=MarketMemoryReadiness.UNKNOWN,
        completeness_score=completeness_score,
        warnings=tuple(warnings),
    )

    data_state = evaluate_market_memory_data_state(
        temporary_requirements
    )

    if consistency == MarketMemoryConsistency.CONFLICTING:
        readiness = MarketMemoryReadiness.NOT_READY
    elif data_state == MarketMemoryDataState.COMPLETE:
        readiness = MarketMemoryReadiness.READY
    elif data_state == MarketMemoryDataState.PARTIAL:
        readiness = MarketMemoryReadiness.CONDITIONAL
    elif data_state == MarketMemoryDataState.MISSING:
        readiness = MarketMemoryReadiness.NOT_READY
    else:
        readiness = MarketMemoryReadiness.UNKNOWN

    return MarketMemoryRequirements(
        memory_available=memory_available,
        market_available=market_available,
        memory_type_defined=memory_type_defined,
        symbol_available=symbol_available,
        timestamp_available=timestamp_available,
        timeframe_available=timeframe_available,
        source_available=source_available,
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

def evaluate_market_memory_readiness(
    requirements: MarketMemoryRequirements,
) -> MarketMemoryReadiness:

    if requirements.consistency == (
        MarketMemoryConsistency.CONFLICTING
    ):
        return MarketMemoryReadiness.NOT_READY

    if requirements.data_state == (
        MarketMemoryDataState.COMPLETE
    ):
        return MarketMemoryReadiness.READY

    if requirements.data_state == (
        MarketMemoryDataState.PARTIAL
    ):
        return MarketMemoryReadiness.CONDITIONAL

    if requirements.data_state == (
        MarketMemoryDataState.MISSING
    ):
        return MarketMemoryReadiness.NOT_READY

    return MarketMemoryReadiness.UNKNOWN


# ============================================================
# CONFIDENCE
# ============================================================

def calculate_market_memory_confidence(
    requirements: MarketMemoryRequirements,
) -> float:
    """
    Structural memory confidence only.

    No trading-performance claim is generated here.
    No invented market formula is introduced.
    """

    score = float(requirements.completeness_score)

    if requirements.consistency == (
        MarketMemoryConsistency.CONSISTENT
    ):
        score += 5.0

    elif requirements.consistency == (
        MarketMemoryConsistency.CONFLICTING
    ):
        score -= 30.0

    elif requirements.consistency == (
        MarketMemoryConsistency.INSUFFICIENT
    ):
        score -= 10.0

    if requirements.data_state == (
        MarketMemoryDataState.MISSING
    ):
        score -= 20.0

    return max(0.0, min(100.0, score))


# ============================================================
# MEMORY STRENGTH
# ============================================================

def determine_market_memory_strength(
    confidence_score: float,
    requirements: MarketMemoryRequirements,
) -> MarketMemoryStrength:

    confidence_score = max(
        0.0,
        min(100.0, float(confidence_score)),
    )

    if requirements.consistency == (
        MarketMemoryConsistency.CONFLICTING
    ):
        return MarketMemoryStrength.LOW

    if confidence_score >= 90.0:
        return MarketMemoryStrength.CRITICAL

    if confidence_score >= 75.0:
        return MarketMemoryStrength.HIGH

    if confidence_score >= 50.0:
        return MarketMemoryStrength.MODERATE

    if confidence_score > 0.0:
        return MarketMemoryStrength.LOW

    return MarketMemoryStrength.UNKNOWN


# ============================================================
# ASSESSMENT BUILDER
# ============================================================

def build_market_memory_assessment(
    requirements: MarketMemoryRequirements,
) -> MarketMemoryAssessment:

    readiness = evaluate_market_memory_readiness(
        requirements
    )

    confidence_score = calculate_market_memory_confidence(
        requirements
    )

    strength = determine_market_memory_strength(
        confidence_score,
        requirements,
    )

    strengths: list[str] = []
    weaknesses: list[str] = []

    if requirements.memory_available:
        strengths.append("memory reference available")

    if requirements.memory_type_defined:
        strengths.append("memory type defined")

    if requirements.symbol_available:
        strengths.append("symbol available")

    if requirements.timestamp_available:
        strengths.append("timestamp available")

    if requirements.source_available:
        strengths.append("source traceability available")

    if requirements.regime_available:
        strengths.append("market regime available")

    if not requirements.symbol_available:
        weaknesses.append("symbol unavailable")

    if not requirements.timestamp_available:
        weaknesses.append("timestamp unavailable")

    if not requirements.source_available:
        weaknesses.append("source unavailable")

    if not requirements.regime_available:
        weaknesses.append("regime unavailable")

    if requirements.consistency == (
        MarketMemoryConsistency.CONFLICTING
    ):
        weaknesses.append("conflicting market memory")

    if readiness == MarketMemoryReadiness.READY:
        rationale = (
            "Market memory satisfies the current structural "
            "readiness requirements."
        )
    elif readiness == MarketMemoryReadiness.CONDITIONAL:
        rationale = (
            "Market memory is structurally usable but "
            "contains incomplete memory context."
        )
    elif readiness == MarketMemoryReadiness.NOT_READY:
        rationale = (
            "Market memory is not sufficiently complete or "
            "contains a blocking consistency condition."
        )
    else:
        rationale = (
            "Market memory readiness cannot be established "
            "from the supplied information."
        )

    return MarketMemoryAssessment(
        readiness=readiness,
        data_state=requirements.data_state,
        consistency=requirements.consistency,
        strength=strength,
        confidence_score=confidence_score,
        completeness_score=requirements.completeness_score,
        strengths=tuple(strengths),
        weaknesses=tuple(weaknesses),
        rationale=rationale,
    )
# ============================================================
# PART 3/5 — ACTION, RESULT, CONTRACT & ENGINE
# ============================================================


class MarketMemoryActionState(str, Enum):
    NONE = "NONE"
    STORE = "STORE"
    RETRIEVE = "RETRIEVE"
    CONSOLIDATE = "CONSOLIDATE"
    REVIEW = "REVIEW"
    HOLD = "HOLD"
    INVALIDATE = "INVALIDATE"
    ARCHIVE = "ARCHIVE"


class MarketMemoryContractState(str, Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


class MarketMemoryResultStatus(str, Enum):
    STORED = "STORED"
    CONDITIONAL = "CONDITIONAL"
    REVIEW = "REVIEW"
    HOLD = "HOLD"
    INVALIDATED = "INVALIDATED"
    ARCHIVED = "ARCHIVED"
    INVALID = "INVALID"


# ============================================================
# ACTION
# ============================================================

@dataclass(frozen=True)
class MarketMemoryAction:
    state: MarketMemoryActionState
    memory_id: str
    rationale: str = ""
    warnings: tuple[str, ...] = ()

    @property
    def is_action_request(self) -> bool:
        return False


# ============================================================
# RESULT
# ============================================================

@dataclass(frozen=True)
class MarketMemoryResult:
    request_id: str
    result_id: str
    status: MarketMemoryResultStatus

    memory: MarketMemoryReference
    requirements: MarketMemoryRequirements
    assessment: MarketMemoryAssessment

    action: MarketMemoryAction

    rationale: str = ""
    warnings: tuple[str, ...] = ()
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def is_valid(self) -> bool:
        return (
            bool(self.request_id)
            and bool(self.result_id)
            and self.status != MarketMemoryResultStatus.INVALID
            and bool(self.memory.memory_id)
        )

    @property
    def stored(self) -> bool:
        return (
            self.is_valid
            and self.status
            == MarketMemoryResultStatus.STORED
        )

    @property
    def is_conditional(self) -> bool:
        return (
            self.status
            == MarketMemoryResultStatus.CONDITIONAL
        )

    @property
    def requires_review(self) -> bool:
        return (
            self.status == MarketMemoryResultStatus.REVIEW
            or self.action.state
            == MarketMemoryActionState.REVIEW
        )

    @property
    def requires_hold(self) -> bool:
        return (
            self.status == MarketMemoryResultStatus.HOLD
            or self.action.state
            == MarketMemoryActionState.HOLD
        )

    @property
    def is_invalidated(self) -> bool:
        return (
            self.status
            == MarketMemoryResultStatus.INVALIDATED
            or self.action.state
            == MarketMemoryActionState.INVALIDATE
        )

    @property
    def is_action_request(self) -> bool:
        return False


# ============================================================
# CONTRACT
# ============================================================

@dataclass(frozen=True)
class MarketMemoryContract:
    request_id: str
    contract_id: str

    state: MarketMemoryContractState
    result: MarketMemoryResult

    rationale: str = ""
    warnings: tuple[str, ...] = ()
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def is_valid(self) -> bool:
        return (
            bool(self.request_id)
            and bool(self.contract_id)
            and self.state
            != MarketMemoryContractState.INVALID
            and self.result.is_valid
        )

    @property
    def stored(self) -> bool:
        return self.is_valid and self.result.stored

    @property
    def is_action_request(self) -> bool:
        return False


# ============================================================
# RESULT STATUS
# ============================================================

def _determine_market_memory_result_status(
    assessment: MarketMemoryAssessment,
) -> MarketMemoryResultStatus:

    if assessment.consistency == (
        MarketMemoryConsistency.CONFLICTING
    ):
        return MarketMemoryResultStatus.INVALIDATED

    if assessment.readiness == (
        MarketMemoryReadiness.READY
    ):
        return MarketMemoryResultStatus.STORED

    if assessment.readiness == (
        MarketMemoryReadiness.CONDITIONAL
    ):
        return MarketMemoryResultStatus.CONDITIONAL

    if assessment.readiness == (
        MarketMemoryReadiness.NOT_READY
    ):
        return MarketMemoryResultStatus.HOLD

    return MarketMemoryResultStatus.REVIEW


# ============================================================
# ACTION BUILDER
# ============================================================

def build_market_memory_action(
    result_status: MarketMemoryResultStatus,
    memory_id: str,
    rationale: str = "",
    warnings: tuple[str, ...] = (),
) -> MarketMemoryAction:

    if result_status == MarketMemoryResultStatus.STORED:
        state = MarketMemoryActionState.STORE

    elif result_status == MarketMemoryResultStatus.CONDITIONAL:
        state = MarketMemoryActionState.REVIEW

    elif result_status == MarketMemoryResultStatus.REVIEW:
        state = MarketMemoryActionState.REVIEW

    elif result_status == MarketMemoryResultStatus.HOLD:
        state = MarketMemoryActionState.HOLD

    elif result_status == (
        MarketMemoryResultStatus.INVALIDATED
    ):
        state = MarketMemoryActionState.INVALIDATE

    elif result_status == MarketMemoryResultStatus.ARCHIVED:
        state = MarketMemoryActionState.ARCHIVE

    else:
        state = MarketMemoryActionState.NONE

    return MarketMemoryAction(
        state=state,
        memory_id=memory_id,
        rationale=rationale,
        warnings=warnings,
    )


# ============================================================
# RESULT BUILDER
# ============================================================

def build_market_memory_result(
    request: MarketMemoryRequest,
    reference: MarketMemoryReference,
    requirements: MarketMemoryRequirements,
    assessment: MarketMemoryAssessment,
) -> MarketMemoryResult:

    status = _determine_market_memory_result_status(
        assessment
    )

    warnings = tuple(requirements.warnings)

    action = build_market_memory_action(
        result_status=status,
        memory_id=reference.memory_id,
        rationale=assessment.rationale,
        warnings=warnings,
    )

    return MarketMemoryResult(
        request_id=request.request_id,
        result_id=str(uuid4()),
        status=status,
        memory=reference,
        requirements=requirements,
        assessment=assessment,
        action=action,
        rationale=assessment.rationale,
        warnings=warnings,
    )


# ============================================================
# CONTRACT STATE
# ============================================================

def _determine_market_memory_contract_state(
    result: MarketMemoryResult,
) -> MarketMemoryContractState:

    if not result.is_valid:
        return MarketMemoryContractState.INVALID

    if result.is_invalidated:
        return MarketMemoryContractState.BLOCKED

    if result.requirements.data_state == (
        MarketMemoryDataState.COMPLETE
    ) and result.requirements.readiness == (
        MarketMemoryReadiness.READY
    ) and result.requirements.consistency != (
        MarketMemoryConsistency.CONFLICTING
    ):
        return MarketMemoryContractState.COMPLETE

    if result.requirements.data_state == (
        MarketMemoryDataState.MISSING
    ):
        return MarketMemoryContractState.INCOMPLETE

    return MarketMemoryContractState.INCOMPLETE


# ============================================================
# CONTRACT BUILDER
# ============================================================

def build_market_memory_contract(
    result: MarketMemoryResult,
) -> MarketMemoryContract:

    state = _determine_market_memory_contract_state(
        result
    )

    return MarketMemoryContract(
        request_id=result.request_id,
        contract_id=str(uuid4()),
        state=state,
        result=result,
        rationale=result.rationale,
        warnings=result.warnings,
    )


# ============================================================
# ENGINE
# ============================================================

class MarketMemoryEngine:
    """
    Core Market Memory lifecycle engine.

    Responsibilities:
        - validate memory request
        - normalize market-memory reference
        - evaluate structural memory requirements
        - evaluate consistency
        - evaluate readiness
        - produce memory result
        - produce memory contract

    Explicit non-responsibilities:
        - no trade execution
        - no order creation
        - no position modification
        - no account authorization
        - no D13 override
        - no Risk override
        - no CAS override
    """

    engine_name = MARKET_MEMORY_ENGINE
    engine_version = MARKET_MEMORY_VERSION

    def validate_request(
        self,
        request: Any,
    ) -> MarketMemoryContractValidation:
        return validate_market_memory_request(request)

    def _invalid_result(
        self,
        request: MarketMemoryRequest,
    ) -> tuple[MarketMemoryResult, MarketMemoryContract]:

        reference = build_market_memory_reference(
            request.market,
            request,
        )

        requirements = MarketMemoryRequirements(
            memory_available=False,
            market_available=False,
            memory_type_defined=False,
            symbol_available=False,
            timestamp_available=False,
            timeframe_available=False,
            source_available=False,
            regime_available=False,
            data_state=MarketMemoryDataState.MISSING,
            consistency=MarketMemoryConsistency.UNKNOWN,
            readiness=MarketMemoryReadiness.NOT_READY,
            completeness_score=0.0,
            warnings=("invalid market memory request",),
        )

        assessment = MarketMemoryAssessment(
            readiness=MarketMemoryReadiness.NOT_READY,
            data_state=MarketMemoryDataState.MISSING,
            consistency=MarketMemoryConsistency.UNKNOWN,
            strength=MarketMemoryStrength.UNKNOWN,
            confidence_score=0.0,
            completeness_score=0.0,
            weaknesses=("invalid market memory request",),
            rationale="Market memory request failed validation.",
        )

        result = MarketMemoryResult(
            request_id=request.request_id,
            result_id=str(uuid4()),
            status=MarketMemoryResultStatus.INVALID,
            memory=reference,
            requirements=requirements,
            assessment=assessment,
            action=MarketMemoryAction(
                state=MarketMemoryActionState.NONE,
                memory_id=reference.memory_id,
                rationale="Invalid request.",
            ),
            rationale="Market memory request failed validation.",
            warnings=("invalid market memory request",),
        )

        return result, build_market_memory_contract(result)

    def evaluate(
        self,
        request: MarketMemoryRequest,
    ) -> MarketMemoryContract:

        validation = self.validate_request(request)

        if not validation.is_valid:
            _, contract = self._invalid_result(request)

            return contract

        reference = build_market_memory_reference(
            request.market,
            request,
        )

        requirements = evaluate_market_memory_requirements(
            reference,
            request,
        )

        assessment = build_market_memory_assessment(
            requirements
        )

        result = build_market_memory_result(
            request=request,
            reference=reference,
            requirements=requirements,
            assessment=assessment,
        )

        return build_market_memory_contract(result)


# ============================================================
# SINGLETON ENGINE
# ============================================================

market_memory_engine = MarketMemoryEngine()


# ============================================================
# PUBLIC OPERATIONS
# ============================================================

def evaluate_market_memory(
    request: MarketMemoryRequest,
) -> MarketMemoryContract:
    return market_memory_engine.evaluate(request)


def analyze_market_memory(
    request: MarketMemoryRequest,
) -> MarketMemoryContract:
    return market_memory_engine.evaluate(request)


def review_market_memory(
    request: MarketMemoryRequest,
) -> MarketMemoryContract:
    return market_memory_engine.evaluate(request)
# ============================================================
# MARKET MEMORY ENGINE
# PART 4 / 5
# ============================================================

def validate_market_memory_result(
    result: Optional[MarketMemoryResult],
) -> MarketMemoryContractValidation:
    errors: list[str] = []
    warnings: list[str] = []

    if result is None:
        return MarketMemoryContractValidation(
            valid=False,
            market_available=False,
            memory_type_defined=False,
            priority_defined=False,
            metadata_valid=False,
            timestamp_valid=False,
            errors=["market_memory_result_missing"],
            warnings=[],
        )

    if not _mm_text(result.request_id):
        errors.append("request_id_missing")

    if not _mm_text(result.result_id):
        errors.append("result_id_missing")

    memory = result.memory
    if memory is None:
        errors.append("memory_reference_missing")
        return MarketMemoryContractValidation(
            valid=False,
            market_available=False,
            memory_type_defined=False,
            priority_defined=False,
            metadata_valid=False,
            timestamp_valid=False,
            errors=errors,
            warnings=warnings,
        )

    market_available = bool(_mm_text(memory.market_name))
    memory_type_defined = memory.memory_type != MarketMemoryType.UNKNOWN
    priority_defined = memory.priority != MarketMemoryPriority.UNKNOWN
    timestamp_valid = bool(_mm_timestamp(memory.timestamp))
    metadata_valid = isinstance(memory.raw_market, Mapping)

    if not market_available:
        errors.append("market_name_missing")

    if not memory_type_defined:
        errors.append("memory_type_undefined")

    if not priority_defined:
        warnings.append("priority_undefined")

    if not timestamp_valid:
        errors.append("timestamp_invalid")

    if not metadata_valid:
        errors.append("raw_market_invalid")

    if result.status == MarketMemoryResultStatus.INVALID:
        errors.append("result_status_invalid")

    return MarketMemoryContractValidation(
        valid=not errors,
        market_available=market_available,
        memory_type_defined=memory_type_defined,
        priority_defined=priority_defined,
        metadata_valid=metadata_valid,
        timestamp_valid=timestamp_valid,
        errors=errors,
        warnings=warnings,
    )


def validate_market_memory_contract(
    contract: Optional[MarketMemoryContract],
) -> MarketMemoryContractValidation:
    errors: list[str] = []
    warnings: list[str] = []

    if contract is None:
        return MarketMemoryContractValidation(
            valid=False,
            market_available=False,
            memory_type_defined=False,
            priority_defined=False,
            metadata_valid=False,
            timestamp_valid=False,
            errors=["market_memory_contract_missing"],
            warnings=[],
        )

    if not _mm_text(contract.request_id):
        errors.append("request_id_missing")

    if not _mm_text(contract.contract_id):
        errors.append("contract_id_missing")

    if not _mm_timestamp(contract.created_at):
        errors.append("created_at_invalid")

    result_validation = validate_market_memory_result(contract.result)

    errors.extend(result_validation.errors)
    warnings.extend(result_validation.warnings)

    if contract.state == MarketMemoryContractState.INVALID:
        errors.append("contract_state_invalid")

    return MarketMemoryContractValidation(
        valid=not errors,
        market_available=result_validation.market_available,
        memory_type_defined=result_validation.memory_type_defined,
        priority_defined=result_validation.priority_defined,
        metadata_valid=result_validation.metadata_valid,
        timestamp_valid=result_validation.timestamp_valid,
        errors=errors,
        warnings=warnings,
    )


def market_memory_ready(
    result: Optional[MarketMemoryResult],
) -> bool:
    if result is None:
        return False

    validation = validate_market_memory_result(result)

    if not validation.valid:
        return False

    if result.status != MarketMemoryResultStatus.STORED:
        return False

    requirements = result.requirements
    assessment = result.assessment

    if requirements is None or assessment is None:
        return False

    if requirements.data_state != MarketMemoryDataState.COMPLETE:
        return False

    if requirements.consistency == MarketMemoryConsistency.CONFLICTING:
        return False

    if requirements.readiness != MarketMemoryReadiness.READY:
        return False

    if not requirements.memory_available:
        return False

    if not requirements.market_available:
        return False

    if not requirements.memory_type_defined:
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


def market_memory_can_advance(
    result: Optional[MarketMemoryResult],
) -> bool:
    if result is None:
        return False

    validation = validate_market_memory_result(result)

    if not validation.valid:
        return False

    requirements = result.requirements
    assessment = result.assessment

    if requirements is None or assessment is None:
        return False

    if requirements.consistency == MarketMemoryConsistency.CONFLICTING:
        return False

    if requirements.data_state == MarketMemoryDataState.MISSING:
        return False

    if requirements.memory_available is not True:
        return False

    if requirements.market_available is not True:
        return False

    if not requirements.memory_type_defined:
        return False

    if assessment.confidence_score < 50.0:
        return False

    return (
        assessment.readiness
        in (
            MarketMemoryReadiness.READY,
            MarketMemoryReadiness.CONDITIONAL,
        )
    )


def market_memory_status(
    result: Optional[MarketMemoryResult],
) -> str:
    if result is None:
        return MarketMemoryResultStatus.INVALID.value
    return result.status.value


def market_memory_type(
    result: Optional[MarketMemoryResult],
) -> str:
    if result is None or result.memory is None:
        return MarketMemoryType.UNKNOWN.value
    return result.memory.memory_type.value


def market_memory_readiness(
    result: Optional[MarketMemoryResult],
) -> str:
    if result is None or result.assessment is None:
        return MarketMemoryReadiness.UNKNOWN.value
    return result.assessment.readiness.value


def market_memory_confidence(
    result: Optional[MarketMemoryResult],
) -> float:
    if result is None or result.assessment is None:
        return 0.0
    return float(result.assessment.confidence_score)


def market_memory_strength(
    result: Optional[MarketMemoryResult],
) -> str:
    if result is None or result.assessment is None:
        return MarketMemoryStrength.UNKNOWN.value
    return result.assessment.strength.value


def market_memory_completeness(
    result: Optional[MarketMemoryResult],
) -> float:
    if result is None or result.assessment is None:
        return 0.0
    return float(result.assessment.completeness_score)


def market_memory_audit(
    result: Optional[MarketMemoryResult],
) -> dict[str, Any]:
    validation = validate_market_memory_result(result)

    if result is None:
        return {
            "engine": MARKET_MEMORY_ENGINE,
            "version": MARKET_MEMORY_VERSION,
            "valid": False,
            "errors": validation.errors,
            "warnings": validation.warnings,
            "ready": False,
            "can_advance": False,
        }

    memory = result.memory
    requirements = result.requirements
    assessment = result.assessment

    return {
        "engine": MARKET_MEMORY_ENGINE,
        "version": MARKET_MEMORY_VERSION,
        "request_id": result.request_id,
        "result_id": result.result_id,
        "valid": validation.valid,
        "status": result.status.value,
        "memory_id": memory.memory_id if memory else None,
        "market": memory.market_name if memory else None,
        "symbol": memory.symbol if memory else None,
        "memory_type": (
            memory.memory_type.value
            if memory
            else MarketMemoryType.UNKNOWN.value
        ),
        "priority": (
            memory.priority.value
            if memory
            else MarketMemoryPriority.UNKNOWN.value
        ),
        "data_state": (
            requirements.data_state.value
            if requirements
            else MarketMemoryDataState.UNKNOWN.value
        ),
        "consistency": (
            requirements.consistency.value
            if requirements
            else MarketMemoryConsistency.UNKNOWN.value
        ),
        "readiness": (
            assessment.readiness.value
            if assessment
            else MarketMemoryReadiness.UNKNOWN.value
        ),
        "strength": (
            assessment.strength.value
            if assessment
            else MarketMemoryStrength.UNKNOWN.value
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
        "ready": market_memory_ready(result),
        "can_advance": market_memory_can_advance(result),
        "safe": market_memory_is_safe(result),
        "allows_execution": market_memory_allows_execution(result),
        "allows_trade": market_memory_allows_trade(result),
        "allows_order": market_memory_allows_order(result),
        "allows_position_change": market_memory_allows_position_change(result),
        "allows_authorization": market_memory_allows_authorization(result),
        "overrides_d13": market_memory_overrides_d13(result),
        "overrides_risk": market_memory_overrides_risk(result),
        "overrides_cas": market_memory_overrides_cas(result),
        "errors": validation.errors,
        "warnings": validation.warnings,
    }


# ============================================================
# SAFETY BOUNDARIES
# ============================================================

def market_memory_is_safe(
    result: Optional[MarketMemoryResult],
) -> bool:
    if result is None:
        return False

    validation = validate_market_memory_result(result)

    if not validation.valid:
        return False

    if result.status in (
        MarketMemoryResultStatus.INVALID,
        MarketMemoryResultStatus.INVALIDATED,
    ):
        return False

    if result.contract_state if hasattr(result, "contract_state") else False:
        return False

    if result.requirements.consistency == (
        MarketMemoryConsistency.CONFLICTING
    ):
        return False

    return True


def market_memory_allows_execution(
    result: Optional[MarketMemoryResult],
) -> bool:
    return False


def market_memory_allows_trade(
    result: Optional[MarketMemoryResult],
) -> bool:
    return False


def market_memory_allows_order(
    result: Optional[MarketMemoryResult],
) -> bool:
    return False


def market_memory_allows_position_change(
    result: Optional[MarketMemoryResult],
) -> bool:
    return False


def market_memory_allows_authorization(
    result: Optional[MarketMemoryResult],
) -> bool:
    return False


# ============================================================
# AUTHORITY BOUNDARIES
# ============================================================

def market_memory_overrides_d13(
    result: Optional[MarketMemoryResult],
) -> bool:
    return False


def market_memory_overrides_risk(
    result: Optional[MarketMemoryResult],
) -> bool:
    return False


def market_memory_overrides_cas(
    result: Optional[MarketMemoryResult],
) -> bool:
    return False


# ============================================================
# ENGINE INFORMATION
# ============================================================

def get_market_memory_engine_info() -> dict[str, Any]:
    return {
        "engine": MARKET_MEMORY_ENGINE,
        "version": MARKET_MEMORY_VERSION,
        "role": "market_memory_intelligence",
        "responsibilities": [
            "memory_request_validation",
            "market_memory_reference_normalization",
            "memory_requirements_evaluation",
            "memory_consistency_evaluation",
            "memory_readiness_evaluation",
            "memory_assessment",
            "memory_result_generation",
            "memory_contract_generation",
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


def market_memory_health_check() -> dict[str, Any]:
    checks = {
        "engine_instance": isinstance(
            market_memory_engine,
            MarketMemoryEngine,
        ),
        "engine_name": (
            getattr(market_memory_engine, "name", None)
            == MARKET_MEMORY_ENGINE
            or getattr(market_memory_engine, "engine_name", None)
            == MARKET_MEMORY_ENGINE
            or isinstance(market_memory_engine, MarketMemoryEngine)
        ),
        "version_present": bool(MARKET_MEMORY_VERSION),
        "execution_blocked": not market_memory_allows_execution(None),
        "trade_blocked": not market_memory_allows_trade(None),
        "order_blocked": not market_memory_allows_order(None),
        "position_change_blocked": not (
            market_memory_allows_position_change(None)
        ),
        "authorization_blocked": not (
            market_memory_allows_authorization(None)
        ),
        "d13_override_blocked": not market_memory_overrides_d13(None),
        "risk_override_blocked": not market_memory_overrides_risk(None),
        "cas_override_blocked": not market_memory_overrides_cas(None),
    }

    return {
        "engine": MARKET_MEMORY_ENGINE,
        "version": MARKET_MEMORY_VERSION,
        "healthy": all(checks.values()),
        "checks": checks,
    }


def run_market_memory_health_check() -> bool:
    return bool(market_memory_health_check()["healthy"])
# ============================================================
# MARKET MEMORY ENGINE
# PART 5 / 5
# FINAL SERIALIZATION + INTEGRITY + PUBLIC API
# ============================================================


def _market_memory_datetime(value: Any) -> Optional[str]:
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.isoformat()

    return _mm_text(value)


def market_memory_result_to_dict(
    result: Optional[MarketMemoryResult],
) -> dict[str, Any]:
    if result is None:
        return {}

    memory = result.memory
    requirements = result.requirements
    assessment = result.assessment
    action = result.action

    return {
        "request_id": result.request_id,
        "result_id": result.result_id,
        "status": result.status.value,
        "memory": (
            {
                "memory_id": memory.memory_id,
                "market_name": memory.market_name,
                "symbol": memory.symbol,
                "memory_type": memory.memory_type.value,
                "status": memory.status.value,
                "priority": memory.priority.value,
                "timestamp": _market_memory_datetime(memory.timestamp),
                "timeframe": memory.timeframe,
                "session": memory.session,
                "regime": memory.regime,
                "source_type": memory.source_type.value,
                "raw_market": dict(memory.raw_market),
            }
            if memory
            else None
        ),
        "requirements": (
            {
                "memory_available": requirements.memory_available,
                "market_available": requirements.market_available,
                "memory_type_defined": requirements.memory_type_defined,
                "symbol_available": requirements.symbol_available,
                "timestamp_available": requirements.timestamp_available,
                "timeframe_available": requirements.timeframe_available,
                "source_available": requirements.source_available,
                "regime_available": requirements.regime_available,
                "data_state": requirements.data_state.value,
                "consistency": requirements.consistency.value,
                "readiness": requirements.readiness.value,
                "completeness_score": requirements.completeness_score,
                "warnings": list(requirements.warnings),
            }
            if requirements
            else None
        ),
        "assessment": (
            {
                "readiness": assessment.readiness.value,
                "data_state": assessment.data_state.value,
                "consistency": assessment.consistency.value,
                "strength": assessment.strength.value,
                "confidence_score": assessment.confidence_score,
                "completeness_score": assessment.completeness_score,
                "strengths": list(assessment.strengths),
                "weaknesses": list(assessment.weaknesses),
                "rationale": assessment.rationale,
            }
            if assessment
            else None
        ),
        "action": (
            {
                "state": action.state.value,
                "memory_id": action.memory_id,
                "rationale": action.rationale,
                "warnings": list(action.warnings),
                "is_action_request": action.is_action_request,
            }
            if action
            else None
        ),
        "rationale": result.rationale,
        "warnings": list(result.warnings),
        "created_at": _market_memory_datetime(result.created_at),
        "integrity": {
            "valid": validate_market_memory_result(result).valid,
            "ready": market_memory_ready(result),
            "can_advance": market_memory_can_advance(result),
            "safe": market_memory_is_safe(result),
        },
    }


def market_memory_contract_to_dict(
    contract: Optional[MarketMemoryContract],
) -> dict[str, Any]:
    if contract is None:
        return {}

    validation = validate_market_memory_contract(contract)

    return {
        "request_id": contract.request_id,
        "contract_id": contract.contract_id,
        "state": contract.state.value,
        "result": market_memory_result_to_dict(contract.result),
        "rationale": contract.rationale,
        "warnings": list(contract.warnings),
        "created_at": _market_memory_datetime(contract.created_at),
        "validation": {
            "valid": validation.valid,
            "market_available": validation.market_available,
            "memory_type_defined": validation.memory_type_defined,
            "priority_defined": validation.priority_defined,
            "metadata_valid": validation.metadata_valid,
            "timestamp_valid": validation.timestamp_valid,
            "errors": list(validation.errors),
            "warnings": list(validation.warnings),
        },
        "is_valid": contract.is_valid,
        "stored": contract.stored,
        "is_action_request": contract.is_action_request,
    }


def market_memory_integrity_check(
    result: Optional[MarketMemoryResult],
) -> dict[str, Any]:
    validation = validate_market_memory_result(result)

    if result is None:
        return {
            "valid": False,
            "integrity": False,
            "errors": ["result_missing"],
            "warnings": [],
        }

    errors = list(validation.errors)
    warnings = list(validation.warnings)

    if result.requirements is None:
        errors.append("requirements_missing")

    if result.assessment is None:
        errors.append("assessment_missing")

    if result.action is None:
        errors.append("action_missing")

    if result.memory is None:
        errors.append("memory_missing")

    if (
        result.status == MarketMemoryResultStatus.STORED
        and not market_memory_ready(result)
    ):
        warnings.append("stored_result_not_ready")

    integrity = not errors

    return {
        "valid": validation.valid,
        "integrity": integrity,
        "errors": errors,
        "warnings": warnings,
        "request_id": result.request_id,
        "result_id": result.result_id,
        "status": result.status.value,
        "ready": market_memory_ready(result),
        "can_advance": market_memory_can_advance(result),
        "safe": market_memory_is_safe(result),
    }


def market_memory_contract_integrity_check(
    contract: Optional[MarketMemoryContract],
) -> dict[str, Any]:
    validation = validate_market_memory_contract(contract)

    if contract is None:
        return {
            "valid": False,
            "integrity": False,
            "errors": ["contract_missing"],
            "warnings": [],
        }

    result_integrity = market_memory_integrity_check(contract.result)

    errors = list(validation.errors)
    warnings = list(validation.warnings)

    if not result_integrity["integrity"]:
        errors.append("result_integrity_failed")

    if contract.state == MarketMemoryContractState.COMPLETE:
        if not market_memory_ready(contract.result):
            errors.append("complete_contract_without_ready_memory")

    if contract.state == MarketMemoryContractState.BLOCKED:
        if contract.result.status != MarketMemoryResultStatus.INVALIDATED:
            warnings.append("blocked_contract_without_invalidated_result")

    integrity = not errors

    return {
        "valid": validation.valid,
        "integrity": integrity,
        "errors": errors,
        "warnings": warnings,
        "request_id": contract.request_id,
        "contract_id": contract.contract_id,
        "state": contract.state.value,
        "result_integrity": result_integrity,
    }


def market_memory_identity(
    result: Optional[MarketMemoryResult],
) -> Optional[str]:
    if result is None or result.memory is None:
        return None

    return result.memory.memory_id


def market_memory_is_invalid(
    result: Optional[MarketMemoryResult],
) -> bool:
    if result is None:
        return True

    return result.status in (
        MarketMemoryResultStatus.INVALID,
        MarketMemoryResultStatus.INVALIDATED,
    )


def market_memory_requires_review(
    result: Optional[MarketMemoryResult],
) -> bool:
    if result is None:
        return True

    return result.requires_review


def market_memory_requires_hold(
    result: Optional[MarketMemoryResult],
) -> bool:
    if result is None:
        return True

    return result.requires_hold


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    # Constants
    "MARKET_MEMORY_ENGINE",
    "MARKET_MEMORY_VERSION",

    # Enums
    "MarketMemoryStatus",
    "MarketMemoryType",
    "MarketMemoryPriority",
    "MarketMemorySourceType",
    "MarketMemoryContractStatus",
    "MarketMemoryDataState",
    "MarketMemoryConsistency",
    "MarketMemoryReadiness",
    "MarketMemoryStrength",
    "MarketMemoryActionState",
    "MarketMemoryContractState",
    "MarketMemoryResultStatus",

    # Core contracts
    "MarketMemoryRequest",
    "MarketMemoryReference",
    "MarketMemorySourceReference",
    "MarketMemoryContractValidation",
    "MarketMemoryRequirements",
    "MarketMemoryAssessment",
    "MarketMemoryAction",
    "MarketMemoryResult",
    "MarketMemoryContract",

    # Reference / validation
    "build_market_memory_reference",
    "validate_market_memory_request",
    "validate_market_memory_result",
    "validate_market_memory_contract",

    # Intelligence evaluation
    "evaluate_market_memory_data_state",
    "evaluate_market_memory_consistency",
    "evaluate_market_memory_requirements",
    "evaluate_market_memory_readiness",
    "calculate_market_memory_confidence",
    "determine_market_memory_strength",
    "build_market_memory_assessment",

    # Result / contract construction
    "build_market_memory_action",
    "build_market_memory_result",
    "build_market_memory_contract",

    # Engine
    "MarketMemoryEngine",
    "market_memory_engine",

    # Public operations
    "evaluate_market_memory",
    "analyze_market_memory",
    "review_market_memory",

    # Readiness / lifecycle
    "market_memory_ready",
    "market_memory_can_advance",
    "market_memory_requires_review",
    "market_memory_requires_hold",
    "market_memory_is_invalid",

    # Accessors
    "market_memory_status",
    "market_memory_type",
    "market_memory_readiness",
    "market_memory_confidence",
    "market_memory_strength",
    "market_memory_completeness",
    "market_memory_identity",

    # Audit / safety
    "market_memory_audit",
    "market_memory_is_safe",
    "market_memory_allows_execution",
    "market_memory_allows_trade",
    "market_memory_allows_order",
    "market_memory_allows_position_change",
    "market_memory_allows_authorization",

    # Authority boundaries
    "market_memory_overrides_d13",
    "market_memory_overrides_risk",
    "market_memory_overrides_cas",

    # Engine information / health
    "get_market_memory_engine_info",
    "market_memory_health_check",
    "run_market_memory_health_check",

    # Serialization / integrity
    "market_memory_result_to_dict",
    "market_memory_contract_to_dict",
    "market_memory_integrity_check",
    "market_memory_contract_integrity_check",
]