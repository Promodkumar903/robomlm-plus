# app/intelligence/memory/pattern_memory.py

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Optional
from uuid import uuid4


PATTERN_MEMORY_ENGINE = "ROBOMLM_PATTERN_MEMORY_ENGINE"
PATTERN_MEMORY_VERSION = "1.0"


# ============================================================
# PATTERN MEMORY STATUS
# ============================================================

class PatternMemoryStatus(str, Enum):
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
# PATTERN MEMORY TYPE
# ============================================================

class PatternMemoryType(str, Enum):
    PRICE_PATTERN = "PRICE_PATTERN"
    MARKET_PATTERN = "MARKET_PATTERN"
    MICROSTRUCTURE_PATTERN = "MICROSTRUCTURE_PATTERN"
    LIQUIDITY_PATTERN = "LIQUIDITY_PATTERN"
    VOLUME_PATTERN = "VOLUME_PATTERN"
    VOLATILITY_PATTERN = "VOLATILITY_PATTERN"
    DERIVATIVE_PATTERN = "DERIVATIVE_PATTERN"
    PARTICIPATION_PATTERN = "PARTICIPATION_PATTERN"
    RELATIONSHIP_PATTERN = "RELATIONSHIP_PATTERN"
    REGIME_PATTERN = "REGIME_PATTERN"
    TIMING_PATTERN = "TIMING_PATTERN"
    BEHAVIOR_PATTERN = "BEHAVIOR_PATTERN"
    DECISION_PATTERN = "DECISION_PATTERN"
    OUTCOME_PATTERN = "OUTCOME_PATTERN"
    COMPOSITE_PATTERN = "COMPOSITE_PATTERN"
    UNKNOWN = "UNKNOWN"


# ============================================================
# PRIORITY
# ============================================================

class PatternMemoryPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


# ============================================================
# SOURCE TYPE
# ============================================================

class PatternMemorySourceType(str, Enum):
    MARKET = "MARKET"
    EVIDENCE = "EVIDENCE"
    DECISION = "DECISION"
    OUTCOME = "OUTCOME"
    RESEARCH = "RESEARCH"
    MEMORY = "MEMORY"
    LEARNING = "LEARNING"
    SYSTEM = "SYSTEM"
    UNKNOWN = "UNKNOWN"


# ============================================================
# PATTERN QUALITY
# ============================================================

class PatternMemoryQuality(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


# ============================================================
# CONTRACT STATUS
# ============================================================

class PatternMemoryContractStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


# ============================================================
# REQUEST CONTRACT
# ============================================================

@dataclass(frozen=True)
class PatternMemoryRequest:
    market: str

    pattern_type: PatternMemoryType = PatternMemoryType.UNKNOWN
    source: str = ""

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    symbol: str = ""
    timeframe: str = ""
    session: str = ""
    regime: str = ""

    pattern_id: str = ""

    pattern_name: str = ""
    pattern_state: str = ""
    direction: str = ""

    confidence: Optional[float] = None
    occurrence_count: Optional[int] = None
    success_count: Optional[int] = None
    failure_count: Optional[int] = None

    priority: PatternMemoryPriority = (
        PatternMemoryPriority.UNKNOWN
    )

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

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

        if not isinstance(
            self.pattern_type,
            PatternMemoryType,
        ):
            return False

        if not isinstance(
            self.priority,
            PatternMemoryPriority,
        ):
            return False

        if self.confidence is not None:
            try:
                confidence = float(self.confidence)
            except (TypeError, ValueError):
                return False

            if confidence < 0.0 or confidence > 100.0:
                return False

        count_values = (
            self.occurrence_count,
            self.success_count,
            self.failure_count,
        )

        for value in count_values:
            if value is None:
                continue

            try:
                count = int(value)
            except (TypeError, ValueError):
                return False

            if count < 0:
                return False

        return True


# ============================================================
# PATTERN MEMORY REFERENCE
# ============================================================

@dataclass(frozen=True)
class PatternMemoryReference:
    memory_id: str
    pattern_id: str

    market_name: str
    symbol: str

    pattern_type: PatternMemoryType
    status: PatternMemoryStatus
    priority: PatternMemoryPriority

    timestamp: datetime

    timeframe: str
    session: str
    regime: str

    source_type: PatternMemorySourceType

    pattern_name: str = ""
    pattern_state: str = ""
    direction: str = ""

    confidence: Optional[float] = None

    occurrence_count: Optional[int] = None
    success_count: Optional[int] = None
    failure_count: Optional[int] = None

    pattern: Mapping[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# SOURCE REFERENCE
# ============================================================

@dataclass(frozen=True)
class PatternMemorySourceReference:
    source_id: str
    source_name: str

    source_type: PatternMemorySourceType

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
class PatternMemoryContractValidation:
    valid: bool

    market_available: bool
    pattern_type_defined: bool
    priority_defined: bool

    metadata_valid: bool
    timestamp_valid: bool

    pattern_id_available: bool
    pattern_name_available: bool
    pattern_state_available: bool
    direction_available: bool

    symbol_available: bool
    source_available: bool

    confidence_valid: bool
    occurrence_count_valid: bool
    success_count_valid: bool
    failure_count_valid: bool

    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:
        return self.valid


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _pm_read_value(
    source: Any,
    key: str,
    default: Any = None,
) -> Any:
    if isinstance(source, Mapping):
        return source.get(key, default)

    return getattr(source, key, default)


def _pm_text(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip()


def _pm_timestamp(value: Any) -> datetime:
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


def _pm_float(
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


def _pm_int(
    value: Any,
    minimum: Optional[int] = None,
) -> Optional[int]:
    if value is None:
        return None

    try:
        number = int(value)
    except (TypeError, ValueError):
        return None

    if minimum is not None and number < minimum:
        return None

    return number


def _pm_enum(
    value: Any,
    enum_type: type[Enum],
    default: Enum,
) -> Enum:
    if isinstance(value, enum_type):
        return value

    text = _pm_text(value).upper()

    if not text:
        return default

    for member in enum_type:
        if member.value == text:
            return member

    return default


# ============================================================
# BUILD PATTERN MEMORY REFERENCE
# ============================================================

def build_pattern_memory_reference(
    pattern: Any,
    request: Optional[PatternMemoryRequest] = None,
) -> PatternMemoryReference:

    source = pattern

    market = _pm_text(
        _pm_read_value(
            source,
            "market",
            _pm_read_value(
                source,
                "market_name",
                "",
            ),
        )
    )

    symbol = _pm_text(
        _pm_read_value(
            source,
            "symbol",
            request.symbol if request else "",
        )
    )

    pattern_id = _pm_text(
        _pm_read_value(
            source,
            "pattern_id",
            request.pattern_id if request else "",
        )
    )

    memory_id = _pm_text(
        _pm_read_value(
            source,
            "memory_id",
            "",
        )
    )

    if not memory_id:
        memory_id = str(uuid4())

    pattern_type = _pm_enum(
        _pm_read_value(
            source,
            "pattern_type",
        ),
        PatternMemoryType,
        (
            request.pattern_type
            if request is not None
            else PatternMemoryType.UNKNOWN
        ),
    )

    priority = _pm_enum(
        _pm_read_value(
            source,
            "priority",
        ),
        PatternMemoryPriority,
        (
            request.priority
            if request is not None
            else PatternMemoryPriority.UNKNOWN
        ),
    )

    status = _pm_enum(
        _pm_read_value(
            source,
            "status",
        ),
        PatternMemoryStatus,
        PatternMemoryStatus.NEW,
    )

    source_type = _pm_enum(
        _pm_read_value(
            source,
            "source_type",
        ),
        PatternMemorySourceType,
        PatternMemorySourceType.UNKNOWN,
    )

    timestamp = _pm_timestamp(
        _pm_read_value(
            source,
            "timestamp",
            request.timestamp
            if request is not None
            else None,
        )
    )

    confidence = _pm_float(
        _pm_read_value(
            source,
            "confidence",
            request.confidence
            if request is not None
            else None,
        ),
        minimum=0.0,
        maximum=100.0,
    )

    occurrence_count = _pm_int(
        _pm_read_value(
            source,
            "occurrence_count",
            request.occurrence_count
            if request is not None
            else None,
        ),
        minimum=0,
    )

    success_count = _pm_int(
        _pm_read_value(
            source,
            "success_count",
            request.success_count
            if request is not None
            else None,
        ),
        minimum=0,
    )

    failure_count = _pm_int(
        _pm_read_value(
            source,
            "failure_count",
            request.failure_count
            if request is not None
            else None,
        ),
        minimum=0,
    )

    pattern_payload = (
        dict(source)
        if isinstance(source, Mapping)
        else {}
    )

    return PatternMemoryReference(
        memory_id=memory_id,
        pattern_id=pattern_id,
        market_name=market,
        symbol=symbol,
        pattern_type=pattern_type,
        status=status,
        priority=priority,
        timestamp=timestamp,
        timeframe=_pm_text(
            _pm_read_value(
                source,
                "timeframe",
                request.timeframe
                if request else "",
            )
        ),
        session=_pm_text(
            _pm_read_value(
                source,
                "session",
                request.session
                if request else "",
            )
        ),
        regime=_pm_text(
            _pm_read_value(
                source,
                "regime",
                request.regime
                if request else "",
            )
        ),
        source_type=source_type,
        pattern_name=_pm_text(
            _pm_read_value(
                source,
                "pattern_name",
                request.pattern_name
                if request else "",
            )
        ),
        pattern_state=_pm_text(
            _pm_read_value(
                source,
                "pattern_state",
                request.pattern_state
                if request else "",
            )
        ),
        direction=_pm_text(
            _pm_read_value(
                source,
                "direction",
                request.direction
                if request else "",
            )
        ),
        confidence=confidence,
        occurrence_count=occurrence_count,
        success_count=success_count,
        failure_count=failure_count,
        pattern=pattern_payload,
    )


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_pattern_memory_request(
    request: PatternMemoryRequest,
) -> PatternMemoryContractValidation:

    errors: list[str] = []
    warnings: list[str] = []

    market_available = bool(
        request.market.strip()
    )

    pattern_type_defined = (
        request.pattern_type
        != PatternMemoryType.UNKNOWN
    )

    priority_defined = (
        request.priority
        != PatternMemoryPriority.UNKNOWN
    )

    metadata_valid = isinstance(
        request.metadata,
        Mapping,
    )

    timestamp_valid = isinstance(
        request.timestamp,
        datetime,
    )

    pattern_id_available = bool(
        request.pattern_id.strip()
    )

    pattern_name_available = bool(
        request.pattern_name.strip()
    )

    pattern_state_available = bool(
        request.pattern_state.strip()
    )

    direction_available = bool(
        request.direction.strip()
    )

    symbol_available = bool(
        request.symbol.strip()
    )

    source_available = bool(
        request.source.strip()
    )

    confidence_valid = True

    if request.confidence is not None:
        try:
            confidence = float(
                request.confidence
            )
            confidence_valid = (
                0.0 <= confidence <= 100.0
            )
        except (TypeError, ValueError):
            confidence_valid = False

    def _valid_count(value: Any) -> bool:
        if value is None:
            return True

        try:
            return int(value) >= 0
        except (TypeError, ValueError):
            return False

    occurrence_count_valid = _valid_count(
        request.occurrence_count
    )

    success_count_valid = _valid_count(
        request.success_count
    )

    failure_count_valid = _valid_count(
        request.failure_count
    )

    if not market_available:
        errors.append("market_missing")

    if not pattern_type_defined:
        warnings.append("pattern_type_unknown")

    if not priority_defined:
        warnings.append("priority_unknown")

    if not metadata_valid:
        errors.append("metadata_invalid")

    if not timestamp_valid:
        errors.append("timestamp_invalid")

    if not pattern_id_available:
        warnings.append("pattern_id_missing")

    if not pattern_name_available:
        warnings.append("pattern_name_missing")

    if not pattern_state_available:
        warnings.append("pattern_state_missing")

    if not direction_available:
        warnings.append("direction_missing")

    if not symbol_available:
        warnings.append("symbol_missing")

    if not source_available:
        warnings.append("source_missing")

    if not confidence_valid:
        errors.append("confidence_invalid")

    if not occurrence_count_valid:
        errors.append("occurrence_count_invalid")

    if not success_count_valid:
        errors.append("success_count_invalid")

    if not failure_count_valid:
        errors.append("failure_count_invalid")

    valid = (
        not errors
        and market_available
        and metadata_valid
        and timestamp_valid
        and confidence_valid
        and occurrence_count_valid
        and success_count_valid
        and failure_count_valid
    )

    return PatternMemoryContractValidation(
        valid=valid,
        market_available=market_available,
        pattern_type_defined=pattern_type_defined,
        priority_defined=priority_defined,
        metadata_valid=metadata_valid,
        timestamp_valid=timestamp_valid,
        pattern_id_available=pattern_id_available,
        pattern_name_available=pattern_name_available,
        pattern_state_available=pattern_state_available,
        direction_available=direction_available,
        symbol_available=symbol_available,
        source_available=source_available,
        confidence_valid=confidence_valid,
        occurrence_count_valid=occurrence_count_valid,
        success_count_valid=success_count_valid,
        failure_count_valid=failure_count_valid,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )
# ============================================================
# PATTERN MEMORY — PART 2/5
# Data State / Consistency / Requirements / Assessment
# ============================================================

class PatternMemoryDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    UNKNOWN = "UNKNOWN"


class PatternMemoryConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONFLICTING = "CONFLICTING"
    INSUFFICIENT = "INSUFFICIENT"
    UNKNOWN = "UNKNOWN"


class PatternMemoryReadiness(str, Enum):
    READY = "READY"
    CONDITIONAL = "CONDITIONAL"
    NOT_READY = "NOT_READY"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class PatternMemoryRequirements:
    memory_available: bool
    pattern_available: bool
    market_available: bool
    pattern_type_defined: bool
    pattern_id_available: bool
    symbol_available: bool
    timestamp_available: bool
    source_available: bool
    pattern_name_available: bool
    pattern_state_available: bool
    direction_available: bool
    confidence_available: bool
    occurrence_count_available: bool
    success_count_available: bool
    failure_count_available: bool
    timeframe_available: bool
    session_available: bool
    regime_available: bool
    data_state: PatternMemoryDataState
    consistency: PatternMemoryConsistency
    readiness: PatternMemoryReadiness
    completeness_score: float
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class PatternMemoryAssessment:
    readiness: PatternMemoryReadiness
    data_state: PatternMemoryDataState
    consistency: PatternMemoryConsistency
    quality: PatternMemoryQuality
    confidence_score: float
    completeness_score: float
    strengths: tuple[str, ...] = ()
    weaknesses: tuple[str, ...] = ()
    rationale: str = ""


def _pm_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip().lower() in {
            "1",
            "true",
            "yes",
            "y",
            "available",
            "valid",
            "complete",
        }
    return bool(value)


def _pm_conflict_detected(
    pattern: Any,
    request: Optional[PatternMemoryRequest] = None,
) -> bool:
    """
    Detect explicit pattern-memory conflicts.

    Conflict detection is semantic:
    - explicit conflict flags
    - contradictory state markers
    - invalid success/failure accounting
    - impossible count relationships

    This function does NOT infer market direction or generate
    trading decisions.
    """
    sources = [pattern]

    if request is not None:
        sources.append(request)

    for source in sources:
        if source is None:
            continue

        for key in (
            "conflict",
            "has_conflict",
            "pattern_conflict",
            "data_conflict",
            "memory_conflict",
        ):
            value = _pm_read_value(source, key, None)
            if _pm_bool(value):
                return True

        state = _pm_text(_pm_read_value(source, "pattern_state", ""))
        if state.upper() in {
            "CONFLICT",
            "CONFLICTING",
            "INVALID",
            "INCONSISTENT",
        }:
            return True

    occurrence = _pm_int(
        _pm_read_value(pattern, "occurrence_count", None)
    )
    success = _pm_int(
        _pm_read_value(pattern, "success_count", None)
    )
    failure = _pm_int(
        _pm_read_value(pattern, "failure_count", None)
    )

    if occurrence is not None and occurrence < 0:
        return True

    if success is not None and success < 0:
        return True

    if failure is not None and failure < 0:
        return True

    if (
        occurrence is not None
        and success is not None
        and failure is not None
        and success + failure > occurrence
    ):
        return True

    return False


def evaluate_pattern_memory_data_state(
    reference: PatternMemoryReference,
) -> PatternMemoryDataState:
    """
    Evaluate structural availability of pattern memory.

    Structural fields:
    memory_id, pattern_id, market, pattern_type, symbol,
    timestamp, source, pattern_state, direction,
    confidence, occurrence_count, success_count, failure_count.
    """
    checks = (
        bool(_pm_text(reference.memory_id)),
        bool(_pm_text(reference.pattern_id)),
        bool(_pm_text(reference.market_name)),
        reference.pattern_type != PatternMemoryType.UNKNOWN,
        bool(_pm_text(reference.symbol)),
        isinstance(reference.timestamp, datetime),
        reference.source_type != PatternMemorySourceType.UNKNOWN,
        bool(_pm_text(reference.pattern_state)),
        bool(_pm_text(reference.direction)),
        reference.confidence is not None,
        reference.occurrence_count is not None,
        reference.success_count is not None,
        reference.failure_count is not None,
    )

    available = sum(1 for item in checks if item)

    if available == len(checks):
        return PatternMemoryDataState.COMPLETE

    if available == 0:
        return PatternMemoryDataState.MISSING

    return PatternMemoryDataState.PARTIAL


def evaluate_pattern_memory_consistency(
    reference: PatternMemoryReference,
    request: Optional[PatternMemoryRequest] = None,
) -> PatternMemoryConsistency:
    """
    Evaluate semantic consistency without generating any
    trading interpretation.
    """
    if _pm_conflict_detected(reference, request):
        return PatternMemoryConsistency.CONFLICTING

    values = (
        reference.market_name,
        reference.pattern_id,
        reference.symbol,
        reference.pattern_name,
        reference.pattern_state,
        reference.direction,
    )

    if not any(_pm_text(value) for value in values):
        return PatternMemoryConsistency.INSUFFICIENT

    if (
        reference.occurrence_count is not None
        and reference.success_count is not None
        and reference.failure_count is not None
        and (
            reference.success_count < 0
            or reference.failure_count < 0
            or reference.occurrence_count < 0
            or reference.success_count + reference.failure_count
            > reference.occurrence_count
        )
    ):
        return PatternMemoryConsistency.CONFLICTING

    return PatternMemoryConsistency.CONSISTENT


def evaluate_pattern_memory_requirements(
    reference: PatternMemoryReference,
    request: Optional[PatternMemoryRequest] = None,
) -> PatternMemoryRequirements:
    """
    Evaluate the complete Pattern Memory contract.

    The completeness score measures availability of required
    pattern-memory attributes. It is not a trading score.
    """
    data_state = evaluate_pattern_memory_data_state(reference)
    consistency = evaluate_pattern_memory_consistency(
        reference,
        request,
    )

    checks = {
        "memory_available": bool(_pm_text(reference.memory_id)),
        "pattern_available": bool(_pm_text(reference.pattern_id)),
        "market_available": bool(_pm_text(reference.market_name)),
        "pattern_type_defined":
            reference.pattern_type != PatternMemoryType.UNKNOWN,
        "pattern_id_available":
            bool(_pm_text(reference.pattern_id)),
        "symbol_available":
            bool(_pm_text(reference.symbol)),
        "timestamp_available":
            isinstance(reference.timestamp, datetime),
        "source_available":
            reference.source_type != PatternMemorySourceType.UNKNOWN,
        "pattern_name_available":
            bool(_pm_text(reference.pattern_name)),
        "pattern_state_available":
            bool(_pm_text(reference.pattern_state)),
        "direction_available":
            bool(_pm_text(reference.direction)),
        "confidence_available":
            reference.confidence is not None,
        "occurrence_count_available":
            reference.occurrence_count is not None,
        "success_count_available":
            reference.success_count is not None,
        "failure_count_available":
            reference.failure_count is not None,
        "timeframe_available":
            bool(_pm_text(reference.timeframe)),
        "session_available":
            bool(_pm_text(reference.session)),
        "regime_available":
            bool(_pm_text(reference.regime)),
    }

    total = len(checks)
    available = sum(
        1 for value in checks.values() if value
    )

    completeness_score = round(
        (available / total) * 100.0,
        2,
    ) if total else 0.0

    warnings: list[str] = []

    if not checks["pattern_id_available"]:
        warnings.append("pattern_id_missing")

    if not checks["pattern_name_available"]:
        warnings.append("pattern_name_missing")

    if not checks["pattern_state_available"]:
        warnings.append("pattern_state_missing")

    if not checks["direction_available"]:
        warnings.append("direction_missing")

    if not checks["confidence_available"]:
        warnings.append("confidence_missing")

    if not checks["occurrence_count_available"]:
        warnings.append("occurrence_count_missing")

    if not checks["success_count_available"]:
        warnings.append("success_count_missing")

    if not checks["failure_count_available"]:
        warnings.append("failure_count_missing")

    if not checks["timeframe_available"]:
        warnings.append("timeframe_missing")

    if not checks["session_available"]:
        warnings.append("session_missing")

    if not checks["regime_available"]:
        warnings.append("regime_missing")

    readiness = evaluate_pattern_memory_readiness(
        data_state=data_state,
        consistency=consistency,
        completeness_score=completeness_score,
    )

    return PatternMemoryRequirements(
        memory_available=checks["memory_available"],
        pattern_available=checks["pattern_available"],
        market_available=checks["market_available"],
        pattern_type_defined=checks["pattern_type_defined"],
        pattern_id_available=checks["pattern_id_available"],
        symbol_available=checks["symbol_available"],
        timestamp_available=checks["timestamp_available"],
        source_available=checks["source_available"],
        pattern_name_available=checks["pattern_name_available"],
        pattern_state_available=checks["pattern_state_available"],
        direction_available=checks["direction_available"],
        confidence_available=checks["confidence_available"],
        occurrence_count_available=checks["occurrence_count_available"],
        success_count_available=checks["success_count_available"],
        failure_count_available=checks["failure_count_available"],
        timeframe_available=checks["timeframe_available"],
        session_available=checks["session_available"],
        regime_available=checks["regime_available"],
        data_state=data_state,
        consistency=consistency,
        readiness=readiness,
        completeness_score=completeness_score,
        warnings=tuple(warnings),
    )


def evaluate_pattern_memory_readiness(
    data_state: PatternMemoryDataState,
    consistency: PatternMemoryConsistency,
    completeness_score: float,
) -> PatternMemoryReadiness:
    """
    Pattern Memory readiness gate.

    Conflict always blocks readiness.
    Complete high-quality structural data is READY.
    Partial but usable data is CONDITIONAL.
    Missing data is NOT_READY.
    """
    if consistency == PatternMemoryConsistency.CONFLICTING:
        return PatternMemoryReadiness.NOT_READY

    if data_state == PatternMemoryDataState.MISSING:
        return PatternMemoryReadiness.NOT_READY

    if data_state == PatternMemoryDataState.UNKNOWN:
        return PatternMemoryReadiness.UNKNOWN

    if completeness_score >= 85.0:
        return PatternMemoryReadiness.READY

    if completeness_score >= 50.0:
        return PatternMemoryReadiness.CONDITIONAL

    return PatternMemoryReadiness.NOT_READY


def calculate_pattern_memory_confidence(
    requirements: PatternMemoryRequirements,
) -> float:
    """
    Calculate confidence in the integrity/completeness of
    the stored pattern-memory record.

    This is memory confidence, NOT market prediction confidence.
    """
    score = float(requirements.completeness_score)

    if requirements.consistency == PatternMemoryConsistency.CONSISTENT:
        score += 5.0

    elif requirements.consistency == PatternMemoryConsistency.CONFLICTING:
        score -= 30.0

    elif requirements.consistency == PatternMemoryConsistency.INSUFFICIENT:
        score -= 10.0

    elif requirements.consistency == PatternMemoryConsistency.UNKNOWN:
        score -= 20.0

    if requirements.data_state == PatternMemoryDataState.MISSING:
        score -= 20.0

    elif requirements.data_state == PatternMemoryDataState.UNKNOWN:
        score -= 20.0

    return round(
        max(0.0, min(100.0, score)),
        2,
    )


def classify_pattern_memory_quality(
    confidence_score: float,
    consistency: PatternMemoryConsistency,
) -> PatternMemoryQuality:
    """
    Classify memory-record quality.
    """
    if consistency == PatternMemoryConsistency.CONFLICTING:
        return PatternMemoryQuality.LOW

    if confidence_score >= 90.0:
        return PatternMemoryQuality.CRITICAL

    if confidence_score >= 75.0:
        return PatternMemoryQuality.HIGH

    if confidence_score >= 50.0:
        return PatternMemoryQuality.MODERATE

    if confidence_score > 0.0:
        return PatternMemoryQuality.LOW

    return PatternMemoryQuality.UNKNOWN


def build_pattern_memory_assessment(
    reference: PatternMemoryReference,
    requirements: Optional[PatternMemoryRequirements] = None,
    request: Optional[PatternMemoryRequest] = None,
) -> PatternMemoryAssessment:
    """
    Build the normalized Pattern Memory assessment.
    """
    if requirements is None:
        requirements = evaluate_pattern_memory_requirements(
            reference,
            request,
        )

    confidence_score = calculate_pattern_memory_confidence(
        requirements
    )

    quality = classify_pattern_memory_quality(
        confidence_score,
        requirements.consistency,
    )

    strengths: list[str] = []
    weaknesses: list[str] = []

    if requirements.memory_available:
        strengths.append("memory_identity_available")

    if requirements.pattern_available:
        strengths.append("pattern_identity_available")

    if requirements.market_available:
        strengths.append("market_available")

    if requirements.pattern_type_defined:
        strengths.append("pattern_type_defined")

    if requirements.consistency == PatternMemoryConsistency.CONSISTENT:
        strengths.append("pattern_consistency_valid")

    if requirements.confidence_available:
        strengths.append("pattern_confidence_available")

    if requirements.occurrence_count_available:
        strengths.append("occurrence_history_available")

    if requirements.success_count_available:
        strengths.append("success_history_available")

    if requirements.failure_count_available:
        strengths.append("failure_history_available")

    for warning in requirements.warnings:
        weaknesses.append(warning)

    if requirements.consistency == PatternMemoryConsistency.CONFLICTING:
        weaknesses.append("pattern_memory_conflict")

    if requirements.data_state == PatternMemoryDataState.MISSING:
        weaknesses.append("pattern_memory_data_missing")

    rationale = (
        "Pattern memory is structurally complete and internally "
        "consistent."
        if requirements.readiness == PatternMemoryReadiness.READY
        else
        "Pattern memory is partially available and may require "
        "additional validation before consolidation."
        if requirements.readiness ==
        PatternMemoryReadiness.CONDITIONAL
        else
        "Pattern memory is not sufficiently complete or consistent "
        "for reliable memory validation."
    )

    return PatternMemoryAssessment(
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
# PATTERN MEMORY — PART 3/5
# Action / Result / Contract / Engine
# ============================================================


class PatternMemoryActionState(str, Enum):
    NONE = "NONE"
    STORE = "STORE"
    RETRIEVE = "RETRIEVE"
    CONSOLIDATE = "CONSOLIDATE"
    REVIEW = "REVIEW"
    HOLD = "HOLD"
    INVALIDATE = "INVALIDATE"
    ARCHIVE = "ARCHIVE"


class PatternMemoryContractState(str, Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


class PatternMemoryResultStatus(str, Enum):
    STORED = "STORED"
    CONDITIONAL = "CONDITIONAL"
    REVIEW = "REVIEW"
    HOLD = "HOLD"
    INVALIDATED = "INVALIDATED"
    ARCHIVED = "ARCHIVED"
    INVALID = "INVALID"


@dataclass(frozen=True)
class PatternMemoryAction:
    state: PatternMemoryActionState
    name: str
    reason: str = ""
    allowed: bool = False
    is_action_request: bool = False


@dataclass(frozen=True)
class PatternMemoryResult:
    status: PatternMemoryResultStatus
    reference: PatternMemoryReference
    requirements: PatternMemoryRequirements
    assessment: PatternMemoryAssessment
    action: PatternMemoryAction
    message: str = ""
    result_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    @property
    def is_valid(self) -> bool:
        return self.status != PatternMemoryResultStatus.INVALID


@dataclass(frozen=True)
class PatternMemoryContract:
    state: PatternMemoryContractState
    valid: bool
    reference_valid: bool
    requirements_valid: bool
    assessment_valid: bool
    result_status: PatternMemoryResultStatus
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


def _determine_pattern_memory_result_status(
    requirements: PatternMemoryRequirements,
    assessment: PatternMemoryAssessment,
) -> PatternMemoryResultStatus:

    if (
        requirements.consistency
        == PatternMemoryConsistency.CONFLICTING
    ):
        return PatternMemoryResultStatus.INVALIDATED

    if (
        assessment.readiness
        == PatternMemoryReadiness.READY
    ):
        return PatternMemoryResultStatus.STORED

    if (
        assessment.readiness
        == PatternMemoryReadiness.CONDITIONAL
    ):
        return PatternMemoryResultStatus.CONDITIONAL

    if (
        assessment.readiness
        == PatternMemoryReadiness.NOT_READY
    ):
        return PatternMemoryResultStatus.HOLD

    return PatternMemoryResultStatus.REVIEW


def build_pattern_memory_action(
    status: PatternMemoryResultStatus,
) -> PatternMemoryAction:

    if status == PatternMemoryResultStatus.STORED:
        return PatternMemoryAction(
            state=PatternMemoryActionState.STORE,
            name="STORE",
            reason="Pattern memory record is ready for storage.",
            allowed=True,
            is_action_request=False,
        )

    if status == PatternMemoryResultStatus.CONDITIONAL:
        return PatternMemoryAction(
            state=PatternMemoryActionState.REVIEW,
            name="REVIEW",
            reason=(
                "Pattern memory is conditionally complete "
                "and requires validation/review."
            ),
            allowed=True,
            is_action_request=False,
        )

    if status == PatternMemoryResultStatus.REVIEW:
        return PatternMemoryAction(
            state=PatternMemoryActionState.REVIEW,
            name="REVIEW",
            reason="Pattern memory requires review.",
            allowed=True,
            is_action_request=False,
        )

    if status == PatternMemoryResultStatus.HOLD:
        return PatternMemoryAction(
            state=PatternMemoryActionState.HOLD,
            name="HOLD",
            reason=(
                "Pattern memory is not sufficiently complete "
                "for reliable storage."
            ),
            allowed=False,
            is_action_request=False,
        )

    if status == PatternMemoryResultStatus.INVALIDATED:
        return PatternMemoryAction(
            state=PatternMemoryActionState.INVALIDATE,
            name="INVALIDATE",
            reason=(
                "Pattern memory contains a structural or "
                "semantic conflict."
            ),
            allowed=False,
            is_action_request=False,
        )

    if status == PatternMemoryResultStatus.ARCHIVED:
        return PatternMemoryAction(
            state=PatternMemoryActionState.ARCHIVE,
            name="ARCHIVE",
            reason="Pattern memory record is archived.",
            allowed=False,
            is_action_request=False,
        )

    return PatternMemoryAction(
        state=PatternMemoryActionState.NONE,
        name="NONE",
        reason="No valid pattern-memory lifecycle action.",
        allowed=False,
        is_action_request=False,
    )


def build_pattern_memory_result(
    reference: PatternMemoryReference,
    requirements: PatternMemoryRequirements,
    assessment: PatternMemoryAssessment,
) -> PatternMemoryResult:

    status = _determine_pattern_memory_result_status(
        requirements,
        assessment,
    )

    action = build_pattern_memory_action(status)

    if status == PatternMemoryResultStatus.STORED:
        message = (
            "Pattern memory validated and marked STORED."
        )

    elif status == PatternMemoryResultStatus.CONDITIONAL:
        message = (
            "Pattern memory is conditionally valid and "
            "requires review before consolidation."
        )

    elif status == PatternMemoryResultStatus.HOLD:
        message = (
            "Pattern memory is incomplete and remains on HOLD."
        )

    elif status == PatternMemoryResultStatus.INVALIDATED:
        message = (
            "Pattern memory is invalidated because a conflict "
            "was detected."
        )

    elif status == PatternMemoryResultStatus.REVIEW:
        message = (
            "Pattern memory requires additional review."
        )

    else:
        message = (
            "Pattern memory lifecycle status evaluated."
        )

    return PatternMemoryResult(
        status=status,
        reference=reference,
        requirements=requirements,
        assessment=assessment,
        action=action,
        message=message,
    )


def build_pattern_memory_contract(
    result: PatternMemoryResult,
) -> PatternMemoryContract:

    errors: list[str] = []
    warnings: list[str] = []

    reference_valid = True
    requirements_valid = True
    assessment_valid = True

    if not result.reference.memory_id.strip():
        reference_valid = False
        errors.append("memory_id_missing")

    if not result.reference.pattern_id.strip():
        reference_valid = False
        warnings.append("pattern_id_missing")

    if not result.reference.market_name.strip():
        reference_valid = False
        errors.append("market_missing")

    if (
        result.reference.pattern_type
        == PatternMemoryType.UNKNOWN
    ):
        reference_valid = False
        errors.append("pattern_type_unknown")

    if result.requirements.completeness_score < 0.0:
        requirements_valid = False
        errors.append("invalid_completeness_score")

    if result.requirements.completeness_score > 100.0:
        requirements_valid = False
        errors.append("invalid_completeness_score")

    if not isinstance(
        result.assessment.readiness,
        PatternMemoryReadiness,
    ):
        assessment_valid = False
        errors.append("invalid_readiness")

    if not isinstance(
        result.assessment.quality,
        PatternMemoryQuality,
    ):
        assessment_valid = False
        errors.append("invalid_quality")

    valid = (
        reference_valid
        and requirements_valid
        and assessment_valid
        and result.status
        != PatternMemoryResultStatus.INVALID
    )

    if not valid:
        state = PatternMemoryContractState.INVALID

    elif (
        result.status
        == PatternMemoryResultStatus.INVALIDATED
        or result.assessment.consistency
        == PatternMemoryConsistency.CONFLICTING
    ):
        state = PatternMemoryContractState.BLOCKED

    elif (
        result.assessment.readiness
        == PatternMemoryReadiness.CONDITIONAL
    ):
        state = PatternMemoryContractState.INCOMPLETE

    elif (
        result.assessment.readiness
        == PatternMemoryReadiness.NOT_READY
    ):
        state = PatternMemoryContractState.INCOMPLETE

    else:
        state = PatternMemoryContractState.COMPLETE

    return PatternMemoryContract(
        state=state,
        valid=valid,
        reference_valid=reference_valid,
        requirements_valid=requirements_valid,
        assessment_valid=assessment_valid,
        result_status=result.status,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


class PatternMemoryEngine:
    """
    Pattern Memory lifecycle engine.

    Responsibilities:
    - normalize pattern-memory records
    - evaluate structural completeness
    - evaluate consistency
    - assess memory quality
    - produce normalized lifecycle results

    Non-responsibilities:
    - no trading decision generation
    - no D13 modification
    - no risk authorization
    - no CAS authorization
    - no order/execution authority
    """

    engine_name = PATTERN_MEMORY_ENGINE
    version = PATTERN_MEMORY_VERSION

    def __init__(self) -> None:
        self.engine_name = PATTERN_MEMORY_ENGINE
        self.version = PATTERN_MEMORY_VERSION

    def evaluate(
        self,
        pattern: Any,
        request: Optional[PatternMemoryRequest] = None,
    ) -> PatternMemoryResult:

        reference = build_pattern_memory_reference(
            pattern,
            request,
        )

        requirements = evaluate_pattern_memory_requirements(
            reference,
            request,
        )

        assessment = build_pattern_memory_assessment(
            reference,
            requirements,
            request,
        )

        return build_pattern_memory_result(
            reference,
            requirements,
            assessment,
        )

    def analyze(
        self,
        pattern: Any,
        request: Optional[PatternMemoryRequest] = None,
    ) -> PatternMemoryResult:

        return self.evaluate(
            pattern,
            request,
        )

    def review(
        self,
        pattern: Any,
        request: Optional[PatternMemoryRequest] = None,
    ) -> PatternMemoryResult:

        return self.evaluate(
            pattern,
            request,
        )


pattern_memory_engine = PatternMemoryEngine()


def evaluate_pattern_memory(
    pattern: Any,
    request: Optional[PatternMemoryRequest] = None,
) -> PatternMemoryResult:

    return pattern_memory_engine.evaluate(
        pattern,
        request,
    )


def analyze_pattern_memory(
    pattern: Any,
    request: Optional[PatternMemoryRequest] = None,
) -> PatternMemoryResult:

    return pattern_memory_engine.analyze(
        pattern,
        request,
    )


def review_pattern_memory(
    pattern: Any,
    request: Optional[PatternMemoryRequest] = None,
) -> PatternMemoryResult:

    return pattern_memory_engine.review(
        pattern,
        request,
    )
# ============================================================
# PATTERN MEMORY — PART 4/5
# Validation / Readiness Gates / Accessors / Audit / Safety
# ============================================================


def validate_pattern_memory_result(
    result: PatternMemoryResult,
) -> bool:
    """
    Validate the normalized Pattern Memory result contract.
    """

    if not isinstance(result, PatternMemoryResult):
        return False

    if not isinstance(
        result.status,
        PatternMemoryResultStatus,
    ):
        return False

    if not isinstance(
        result.reference,
        PatternMemoryReference,
    ):
        return False

    if not isinstance(
        result.requirements,
        PatternMemoryRequirements,
    ):
        return False

    if not isinstance(
        result.assessment,
        PatternMemoryAssessment,
    ):
        return False

    if not isinstance(
        result.action,
        PatternMemoryAction,
    ):
        return False

    if not result.result_id.strip():
        return False

    if (
        result.requirements.completeness_score < 0.0
        or result.requirements.completeness_score > 100.0
    ):
        return False

    if (
        result.assessment.confidence_score < 0.0
        or result.assessment.confidence_score > 100.0
    ):
        return False

    if (
        result.assessment.completeness_score < 0.0
        or result.assessment.completeness_score > 100.0
    ):
        return False

    return True


def validate_pattern_memory_contract(
    contract: PatternMemoryContract,
) -> bool:
    """
    Validate the Pattern Memory contract state.
    """

    if not isinstance(contract, PatternMemoryContract):
        return False

    if not isinstance(
        contract.state,
        PatternMemoryContractState,
    ):
        return False

    if not isinstance(
        contract.result_status,
        PatternMemoryResultStatus,
    ):
        return False

    if contract.valid:
        if not contract.reference_valid:
            return False

        if not contract.requirements_valid:
            return False

        if not contract.assessment_valid:
            return False

    return True


def pattern_memory_ready(
    result: PatternMemoryResult,
) -> bool:
    """
    Strict Pattern Memory readiness gate.

    READY means the historical pattern record is sufficiently
    complete, consistent and identifiable for trusted memory use.

    This does NOT authorize trading, execution or decisions.
    """

    if not validate_pattern_memory_result(result):
        return False

    reference = result.reference
    requirements = result.requirements
    assessment = result.assessment

    if result.status != PatternMemoryResultStatus.STORED:
        return False

    if assessment.readiness != PatternMemoryReadiness.READY:
        return False

    if assessment.data_state != PatternMemoryDataState.COMPLETE:
        return False

    if (
        assessment.consistency
        != PatternMemoryConsistency.CONSISTENT
    ):
        return False

    if not reference.memory_id.strip():
        return False

    if not reference.pattern_id.strip():
        return False

    if not reference.market_name.strip():
        return False

    if not reference.symbol.strip():
        return False

    if (
        reference.pattern_type
        == PatternMemoryType.UNKNOWN
    ):
        return False

    if (
        reference.source_type
        == PatternMemorySourceType.UNKNOWN
    ):
        return False

    if not reference.pattern_name.strip():
        return False

    if not reference.pattern_state.strip():
        return False

    if not reference.direction.strip():
        return False

    if reference.timestamp is None:
        return False

    if reference.confidence is None:
        return False

    if reference.occurrence_count is None:
        return False

    if reference.success_count is None:
        return False

    if reference.failure_count is None:
        return False

    if not requirements.memory_available:
        return False

    if not requirements.pattern_available:
        return False

    if not requirements.market_available:
        return False

    if not requirements.pattern_type_defined:
        return False

    if not requirements.pattern_id_available:
        return False

    if not requirements.symbol_available:
        return False

    if not requirements.timestamp_available:
        return False

    if not requirements.source_available:
        return False

    if not requirements.pattern_name_available:
        return False

    if not requirements.pattern_state_available:
        return False

    if not requirements.direction_available:
        return False

    if not requirements.confidence_available:
        return False

    if not requirements.occurrence_count_available:
        return False

    if not requirements.success_count_available:
        return False

    if not requirements.failure_count_available:
        return False

    if assessment.confidence_score < 80.0:
        return False

    return True


def pattern_memory_can_advance(
    result: PatternMemoryResult,
) -> bool:
    """
    Controlled lifecycle gate.

    A CONDITIONAL record may advance to review/consolidation
    but is not considered fully trusted Pattern Memory.

    No trading or execution authority is granted.
    """

    if not validate_pattern_memory_result(result):
        return False

    if (
        result.status
        == PatternMemoryResultStatus.INVALIDATED
    ):
        return False

    if (
        result.assessment.consistency
        == PatternMemoryConsistency.CONFLICTING
    ):
        return False

    if (
        result.assessment.data_state
        == PatternMemoryDataState.MISSING
    ):
        return False

    reference = result.reference
    assessment = result.assessment

    if not reference.memory_id.strip():
        return False

    if not reference.pattern_id.strip():
        return False

    if not reference.market_name.strip():
        return False

    if (
        reference.pattern_type
        == PatternMemoryType.UNKNOWN
    ):
        return False

    if assessment.confidence_score < 50.0:
        return False

    return assessment.readiness in {
        PatternMemoryReadiness.READY,
        PatternMemoryReadiness.CONDITIONAL,
    }


def pattern_memory_status(
    result: PatternMemoryResult,
) -> PatternMemoryResultStatus:
    return result.status


def pattern_memory_type(
    result: PatternMemoryResult,
) -> PatternMemoryType:
    return result.reference.pattern_type


def pattern_memory_readiness(
    result: PatternMemoryResult,
) -> PatternMemoryReadiness:
    return result.assessment.readiness


def pattern_memory_confidence(
    result: PatternMemoryResult,
) -> float:
    return result.assessment.confidence_score


def pattern_memory_quality(
    result: PatternMemoryResult,
) -> PatternMemoryQuality:
    return result.assessment.quality


def pattern_memory_completeness(
    result: PatternMemoryResult,
) -> float:
    return result.assessment.completeness_score


def pattern_memory_identity(
    result: PatternMemoryResult,
) -> str:
    return result.reference.memory_id


def pattern_memory_pattern_id(
    result: PatternMemoryResult,
) -> str:
    return result.reference.pattern_id


def pattern_memory_pattern_name(
    result: PatternMemoryResult,
) -> str:
    return result.reference.pattern_name


def pattern_memory_pattern_state(
    result: PatternMemoryResult,
) -> str:
    return result.reference.pattern_state


def pattern_memory_direction(
    result: PatternMemoryResult,
) -> str:
    return result.reference.direction


def pattern_memory_occurrence_count(
    result: PatternMemoryResult,
) -> int:
    return result.reference.occurrence_count


def pattern_memory_success_count(
    result: PatternMemoryResult,
) -> int:
    return result.reference.success_count


def pattern_memory_failure_count(
    result: PatternMemoryResult,
) -> int:
    return result.reference.failure_count


def pattern_memory_audit(
    result: PatternMemoryResult,
) -> dict[str, Any]:
    """
    Return a complete diagnostic audit.

    Audit information is observational and does not create
    authority over D13, Risk or CAS.
    """

    valid = validate_pattern_memory_result(result)

    return {
        "engine": PATTERN_MEMORY_ENGINE,
        "version": PATTERN_MEMORY_VERSION,
        "valid": valid,
        "result_id": result.result_id,
        "status": result.status.value,
        "pattern_type": result.reference.pattern_type.value,
        "pattern_id": result.reference.pattern_id,
        "pattern_name": result.reference.pattern_name,
        "pattern_state": result.reference.pattern_state,
        "market": result.reference.market_name,
        "symbol": result.reference.symbol,
        "timeframe": result.reference.timeframe,
        "session": result.reference.session,
        "regime": result.reference.regime,
        "source_type": result.reference.source_type.value,
        "direction": result.reference.direction,
        "confidence": result.reference.confidence,
        "occurrence_count": result.reference.occurrence_count,
        "success_count": result.reference.success_count,
        "failure_count": result.reference.failure_count,
        "data_state": result.assessment.data_state.value,
        "consistency": result.assessment.consistency.value,
        "readiness": result.assessment.readiness.value,
        "quality": result.assessment.quality.value,
        "confidence_score": result.assessment.confidence_score,
        "completeness_score": result.assessment.completeness_score,
        "ready": pattern_memory_ready(result),
        "can_advance": pattern_memory_can_advance(result),
        "warnings": result.requirements.warnings,
        "strengths": result.assessment.strengths,
        "weaknesses": result.assessment.weaknesses,
        "rationale": result.assessment.rationale,
        "safe_for_memory_use":
            pattern_memory_safe(result),
        "allows_execution":
            pattern_memory_allows_execution(result),
        "allows_trade":
            pattern_memory_allows_trade(result),
        "allows_order":
            pattern_memory_allows_order(result),
        "allows_position_change":
            pattern_memory_allows_position_change(result),
        "allows_authorization":
            pattern_memory_allows_authorization(result),
        "overrides_d13":
            pattern_memory_overrides_d13(result),
        "overrides_risk":
            pattern_memory_overrides_risk(result),
        "overrides_cas":
            pattern_memory_overrides_cas(result),
    }


def pattern_memory_safe(
    result: PatternMemoryResult,
) -> bool:
    """
    Memory-safety gate.

    Safe means the record is not structurally invalidated
    or explicitly conflicting.
    """

    if not validate_pattern_memory_result(result):
        return False

    if result.status in {
        PatternMemoryResultStatus.INVALID,
        PatternMemoryResultStatus.INVALIDATED,
    }:
        return False

    if (
        result.assessment.consistency
        == PatternMemoryConsistency.CONFLICTING
    ):
        return False

    return True


# ------------------------------------------------------------
# AUTHORITY BOUNDARIES
# ------------------------------------------------------------

def pattern_memory_allows_execution(
    result: PatternMemoryResult,
) -> bool:
    return False


def pattern_memory_allows_trade(
    result: PatternMemoryResult,
) -> bool:
    return False


def pattern_memory_allows_order(
    result: PatternMemoryResult,
) -> bool:
    return False


def pattern_memory_allows_position_change(
    result: PatternMemoryResult,
) -> bool:
    return False


def pattern_memory_allows_authorization(
    result: PatternMemoryResult,
) -> bool:
    return False


def pattern_memory_overrides_d13(
    result: PatternMemoryResult,
) -> bool:
    return False


def pattern_memory_overrides_risk(
    result: PatternMemoryResult,
) -> bool:
    return False


def pattern_memory_overrides_cas(
    result: PatternMemoryResult,
) -> bool:
    return False


def pattern_memory_engine_info() -> dict[str, Any]:
    return {
        "engine": PATTERN_MEMORY_ENGINE,
        "version": PATTERN_MEMORY_VERSION,
        "domain": "PATTERN_MEMORY",
        "purpose": (
            "Historical pattern preservation, validation, "
            "assessment and lifecycle support."
        ),
        "decision_authority": False,
        "risk_authority": False,
        "cas_authority": False,
        "execution_authority": False,
        "d13_override": False,
        "risk_override": False,
        "cas_override": False,
    }


def pattern_memory_health() -> dict[str, Any]:
    return {
        "engine": PATTERN_MEMORY_ENGINE,
        "version": PATTERN_MEMORY_VERSION,
        "status": "HEALTHY",
        "operational": True,
        "decision_authority": False,
        "execution_authority": False,
        "authorization_authority": False,
        "d13_override": False,
        "risk_override": False,
        "cas_override": False,
    }
# ============================================================
# PATTERN MEMORY — PART 5/5
# Lifecycle / Serialization / Integrity / Summary / Exports
# ============================================================


def pattern_memory_requires_review(
    result: PatternMemoryResult,
) -> bool:
    return result.status in {
        PatternMemoryResultStatus.CONDITIONAL,
        PatternMemoryResultStatus.REVIEW,
    }


def pattern_memory_requires_hold(
    result: PatternMemoryResult,
) -> bool:
    return (
        result.status
        == PatternMemoryResultStatus.HOLD
    )


def pattern_memory_is_invalid(
    result: PatternMemoryResult,
) -> bool:
    return result.status in {
        PatternMemoryResultStatus.INVALID,
        PatternMemoryResultStatus.INVALIDATED,
    }


def pattern_memory_is_stored(
    result: PatternMemoryResult,
) -> bool:
    return (
        result.status
        == PatternMemoryResultStatus.STORED
    )


def pattern_memory_is_conditional(
    result: PatternMemoryResult,
) -> bool:
    return (
        result.status
        == PatternMemoryResultStatus.CONDITIONAL
    )


def pattern_memory_is_archived(
    result: PatternMemoryResult,
) -> bool:
    return (
        result.status
        == PatternMemoryResultStatus.ARCHIVED
    )


def pattern_memory_lifecycle_state(
    result: PatternMemoryResult,
) -> str:
    """
    Return normalized lifecycle state without granting
    execution or decision authority.
    """

    if pattern_memory_is_invalid(result):
        return "INVALIDATED"

    if pattern_memory_is_archived(result):
        return "ARCHIVED"

    if pattern_memory_is_stored(result):
        return "STORED"

    if pattern_memory_is_conditional(result):
        return "CONDITIONAL"

    if pattern_memory_requires_review(result):
        return "REVIEW"

    if pattern_memory_requires_hold(result):
        return "HOLD"

    return "UNKNOWN"


def _pm_iso(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None

    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)

    return value.isoformat()


def serialize_pattern_memory_reference(
    reference: PatternMemoryReference,
) -> dict[str, Any]:
    """
    Convert Pattern Memory reference into a JSON-safe mapping.
    """

    return {
        "memory_id": reference.memory_id,
        "pattern_id": reference.pattern_id,
        "market_name": reference.market_name,
        "symbol": reference.symbol,
        "pattern_type": reference.pattern_type.value,
        "status": reference.status.value,
        "priority": reference.priority.value,
        "timestamp": _pm_iso(reference.timestamp),
        "timeframe": reference.timeframe,
        "session": reference.session,
        "regime": reference.regime,
        "source_type": reference.source_type.value,
        "pattern_name": reference.pattern_name,
        "pattern_state": reference.pattern_state,
        "direction": reference.direction,
        "confidence": reference.confidence,
        "occurrence_count": reference.occurrence_count,
        "success_count": reference.success_count,
        "failure_count": reference.failure_count,
        "pattern": dict(reference.pattern),
    }


def serialize_pattern_memory_result(
    result: PatternMemoryResult,
) -> dict[str, Any]:
    """
    Convert the complete Pattern Memory result into a
    JSON-safe diagnostic representation.
    """

    return {
        "engine": PATTERN_MEMORY_ENGINE,
        "version": PATTERN_MEMORY_VERSION,
        "result_id": result.result_id,
        "status": result.status.value,
        "message": result.message,
        "reference": serialize_pattern_memory_reference(
            result.reference
        ),
        "requirements": {
            "memory_available":
                result.requirements.memory_available,
            "pattern_available":
                result.requirements.pattern_available,
            "market_available":
                result.requirements.market_available,
            "pattern_type_defined":
                result.requirements.pattern_type_defined,
            "pattern_id_available":
                result.requirements.pattern_id_available,
            "symbol_available":
                result.requirements.symbol_available,
            "timestamp_available":
                result.requirements.timestamp_available,
            "source_available":
                result.requirements.source_available,
            "pattern_name_available":
                result.requirements.pattern_name_available,
            "pattern_state_available":
                result.requirements.pattern_state_available,
            "direction_available":
                result.requirements.direction_available,
            "confidence_available":
                result.requirements.confidence_available,
            "occurrence_count_available":
                result.requirements.occurrence_count_available,
            "success_count_available":
                result.requirements.success_count_available,
            "failure_count_available":
                result.requirements.failure_count_available,
            "timeframe_available":
                result.requirements.timeframe_available,
            "session_available":
                result.requirements.session_available,
            "regime_available":
                result.requirements.regime_available,
            "data_state":
                result.requirements.data_state.value,
            "consistency":
                result.requirements.consistency.value,
            "readiness":
                result.requirements.readiness.value,
            "completeness_score":
                result.requirements.completeness_score,
            "warnings":
                list(result.requirements.warnings),
        },
        "assessment": {
            "readiness":
                result.assessment.readiness.value,
            "data_state":
                result.assessment.data_state.value,
            "consistency":
                result.assessment.consistency.value,
            "quality":
                result.assessment.quality.value,
            "confidence_score":
                result.assessment.confidence_score,
            "completeness_score":
                result.assessment.completeness_score,
            "strengths":
                list(result.assessment.strengths),
            "weaknesses":
                list(result.assessment.weaknesses),
            "rationale":
                result.assessment.rationale,
        },
        "action": {
            "state":
                result.action.state.value,
            "name":
                result.action.name,
            "reason":
                result.action.reason,
            "allowed":
                result.action.allowed,
            "is_action_request":
                result.action.is_action_request,
        },
    }


def pattern_memory_integrity_check(
    result: PatternMemoryResult,
) -> dict[str, Any]:
    """
    Verify structural integrity of a Pattern Memory result.
    """

    result_valid = validate_pattern_memory_result(
        result
    )

    contract = build_pattern_memory_contract(
        result
    )

    contract_valid = validate_pattern_memory_contract(
        contract
    )

    safe = pattern_memory_safe(result)

    return {
        "engine": PATTERN_MEMORY_ENGINE,
        "version": PATTERN_MEMORY_VERSION,
        "result_valid": result_valid,
        "contract_valid": contract_valid,
        "contract_state": contract.state.value,
        "contract_errors": contract.errors,
        "contract_warnings": contract.warnings,
        "safe": safe,
        "ready": pattern_memory_ready(result),
        "can_advance":
            pattern_memory_can_advance(result),
        "lifecycle":
            pattern_memory_lifecycle_state(result),
        "integrity_pass":
            result_valid and contract_valid and safe,
    }


def pattern_memory_summary(
    result: PatternMemoryResult,
) -> dict[str, Any]:
    """
    Compact Pattern Memory summary for downstream memory
    services, diagnostics and blackbox logging.
    """

    return {
        "engine": PATTERN_MEMORY_ENGINE,
        "version": PATTERN_MEMORY_VERSION,
        "result_id": result.result_id,
        "memory_id": result.reference.memory_id,
        "pattern_id": result.reference.pattern_id,
        "pattern_name": result.reference.pattern_name,
        "market": result.reference.market_name,
        "symbol": result.reference.symbol,
        "pattern_type":
            result.reference.pattern_type.value,
        "pattern_state": result.reference.pattern_state,
        "direction": result.reference.direction,
        "status": result.status.value,
        "readiness":
            result.assessment.readiness.value,
        "quality":
            result.assessment.quality.value,
        "confidence":
            result.assessment.confidence_score,
        "completeness":
            result.assessment.completeness_score,
        "occurrence_count":
            result.reference.occurrence_count,
        "success_count":
            result.reference.success_count,
        "failure_count":
            result.reference.failure_count,
        "safe":
            pattern_memory_safe(result),
        "ready":
            pattern_memory_ready(result),
    }


def pattern_memory_freeze(
    result: PatternMemoryResult,
) -> PatternMemoryResult:
    """
    Freeze a valid Pattern Memory record into STORED state.

    Freeze only affects the memory lifecycle representation.
    It does not modify D13, Risk or CAS authority.
    """

    if not validate_pattern_memory_result(result):
        return result

    if pattern_memory_is_invalid(result):
        return result

    reference = PatternMemoryReference(
        memory_id=result.reference.memory_id,
        pattern_id=result.reference.pattern_id,
        market_name=result.reference.market_name,
        symbol=result.reference.symbol,
        pattern_type=result.reference.pattern_type,
        status=PatternMemoryStatus.STORED,
        priority=result.reference.priority,
        timestamp=result.reference.timestamp,
        timeframe=result.reference.timeframe,
        session=result.reference.session,
        regime=result.reference.regime,
        source_type=result.reference.source_type,
        pattern_name=result.reference.pattern_name,
        pattern_state=result.reference.pattern_state,
        direction=result.reference.direction,
        confidence=result.reference.confidence,
        occurrence_count=result.reference.occurrence_count,
        success_count=result.reference.success_count,
        failure_count=result.reference.failure_count,
        pattern=dict(result.reference.pattern),
    )

    requirements = evaluate_pattern_memory_requirements(
        reference
    )

    assessment = build_pattern_memory_assessment(
        reference,
        requirements,
    )

    return build_pattern_memory_result(
        reference,
        requirements,
        assessment,
    )


def pattern_memory_retain(
    result: PatternMemoryResult,
) -> PatternMemoryResult:
    """
    Retain a safe historical pattern-memory record.

    Retention does not upgrade a record's readiness or quality.
    """

    if not validate_pattern_memory_result(result):
        return result

    if not pattern_memory_safe(result):
        return result

    return result


def pattern_memory_reject(
    result: PatternMemoryResult,
    reason: str = "",
) -> PatternMemoryResult:
    """
    Reject a Pattern Memory record by transitioning its
    lifecycle result to INVALIDATED.

    This is memory lifecycle control only.
    """

    if not validate_pattern_memory_result(result):
        return result

    action = PatternMemoryAction(
        state=PatternMemoryActionState.INVALIDATE,
        name="INVALIDATE",
        reason=(
            reason.strip()
            if reason and reason.strip()
            else "Pattern memory record rejected."
        ),
        allowed=False,
        is_action_request=False,
    )

    return PatternMemoryResult(
        status=PatternMemoryResultStatus.INVALIDATED,
        reference=result.reference,
        requirements=result.requirements,
        assessment=result.assessment,
        action=action,
        message=(
            reason.strip()
            if reason and reason.strip()
            else "Pattern memory record invalidated."
        ),
    )


def pattern_memory_authority_statement() -> str:
    return (
        "Pattern Memory preserves, validates, assesses, retrieves "
        "and supports learning from historical pattern records. "
        "It does not generate, alter, override, authorize or "
        "execute authoritative trading decisions. D13 remains "
        "the decision authority; Risk remains the risk authority; "
        "CAS remains the authorization and execution-safety "
        "authority."
    )


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [
    # Constants
    "PATTERN_MEMORY_ENGINE",
    "PATTERN_MEMORY_VERSION",

    # Status / classification enums
    "PatternMemoryStatus",
    "PatternMemoryType",
    "PatternMemoryPriority",
    "PatternMemorySourceType",
    "PatternMemoryQuality",
    "PatternMemoryContractStatus",

    # Request / reference / source contracts
    "PatternMemoryRequest",
    "PatternMemoryReference",
    "PatternMemorySourceReference",
    "PatternMemoryContractValidation",

    # Assessment enums
    "PatternMemoryDataState",
    "PatternMemoryConsistency",
    "PatternMemoryReadiness",

    # Assessment contracts
    "PatternMemoryRequirements",
    "PatternMemoryAssessment",

    # Lifecycle contracts
    "PatternMemoryActionState",
    "PatternMemoryContractState",
    "PatternMemoryResultStatus",
    "PatternMemoryAction",
    "PatternMemoryResult",
    "PatternMemoryContract",

    # Builders / validators
    "build_pattern_memory_reference",
    "validate_pattern_memory_request",
    "evaluate_pattern_memory_data_state",
    "evaluate_pattern_memory_consistency",
    "evaluate_pattern_memory_requirements",
    "evaluate_pattern_memory_readiness",
    "calculate_pattern_memory_confidence",
    "classify_pattern_memory_quality",
    "build_pattern_memory_assessment",
    "build_pattern_memory_action",
    "build_pattern_memory_result",
    "build_pattern_memory_contract",
    "validate_pattern_memory_result",
    "validate_pattern_memory_contract",

    # Engine
    "PatternMemoryEngine",
    "pattern_memory_engine",
    "evaluate_pattern_memory",
    "analyze_pattern_memory",
    "review_pattern_memory",

    # Readiness / lifecycle
    "pattern_memory_ready",
    "pattern_memory_can_advance",
    "pattern_memory_requires_review",
    "pattern_memory_requires_hold",
    "pattern_memory_is_invalid",
    "pattern_memory_is_stored",
    "pattern_memory_is_conditional",
    "pattern_memory_is_archived",
    "pattern_memory_lifecycle_state",

    # Accessors
    "pattern_memory_status",
    "pattern_memory_type",
    "pattern_memory_readiness",
    "pattern_memory_confidence",
    "pattern_memory_quality",
    "pattern_memory_completeness",
    "pattern_memory_identity",
    "pattern_memory_pattern_id",
    "pattern_memory_pattern_name",
    "pattern_memory_pattern_state",
    "pattern_memory_direction",
    "pattern_memory_occurrence_count",
    "pattern_memory_success_count",
    "pattern_memory_failure_count",

    # Audit / serialization / integrity
    "pattern_memory_audit",
    "serialize_pattern_memory_reference",
    "serialize_pattern_memory_result",
    "pattern_memory_integrity_check",
    "pattern_memory_summary",

    # Lifecycle operations
    "pattern_memory_freeze",
    "pattern_memory_retain",
    "pattern_memory_reject",

    # Safety / authority
    "pattern_memory_safe",
    "pattern_memory_allows_execution",
    "pattern_memory_allows_trade",
    "pattern_memory_allows_order",
    "pattern_memory_allows_position_change",
    "pattern_memory_allows_authorization",
    "pattern_memory_overrides_d13",
    "pattern_memory_overrides_risk",
    "pattern_memory_overrides_cas",
    "pattern_memory_engine_info",
    "pattern_memory_health",
    "pattern_memory_authority_statement",
]