# ============================================================
# ROBOMLM MEMORY RETRIEVAL
# PART 1/5
# Request / Reference / Source / Contract Foundation
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Optional, Sequence
from uuid import uuid4


MEMORY_RETRIEVAL_ENGINE = "ROBOMLM_MEMORY_RETRIEVAL_ENGINE"
MEMORY_RETRIEVAL_VERSION = "1.0"


# ============================================================
# ENUMS
# ============================================================


class MemoryRetrievalStatus(str, Enum):
    NEW = "NEW"
    SEARCHING = "SEARCHING"
    FOUND = "FOUND"
    PARTIAL = "PARTIAL"
    EMPTY = "EMPTY"
    REVIEW = "REVIEW"
    INVALID = "INVALID"
    STALE = "STALE"
    COMPLETED = "COMPLETED"
    UNKNOWN = "UNKNOWN"


class MemoryRetrievalType(str, Enum):
    MARKET = "MARKET"
    EVIDENCE = "EVIDENCE"
    DECISION = "DECISION"
    OUTCOME = "OUTCOME"
    PATTERN = "PATTERN"
    COMPOSITE = "COMPOSITE"
    UNKNOWN = "UNKNOWN"


class MemoryRetrievalPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class MemoryRetrievalSourceType(str, Enum):
    MARKET_MEMORY = "MARKET_MEMORY"
    EVIDENCE_MEMORY = "EVIDENCE_MEMORY"
    DECISION_MEMORY = "DECISION_MEMORY"
    OUTCOME_MEMORY = "OUTCOME_MEMORY"
    PATTERN_MEMORY = "PATTERN_MEMORY"
    MEMORY_SERVICE = "MEMORY_SERVICE"
    RESEARCH = "RESEARCH"
    SYSTEM = "SYSTEM"
    UNKNOWN = "UNKNOWN"


class MemoryRetrievalContractStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


# ============================================================
# REQUEST CONTRACT
# ============================================================


@dataclass(frozen=True)
class MemoryRetrievalRequest:
    """
    Canonical request for retrieving historical memory.

    Retrieval criteria describe WHAT historical information is
    requested. They do not represent a trading instruction.
    """

    market: str

    retrieval_type: MemoryRetrievalType = (
        MemoryRetrievalType.UNKNOWN
    )

    symbol: str = ""
    timeframe: str = ""
    session: str = ""
    regime: str = ""

    pattern_type: str = ""
    decision_type: str = ""
    outcome_type: str = ""
    evidence_type: str = ""
    market_memory_type: str = ""

    memory_id: str = ""
    decision_id: str = ""
    outcome_id: str = ""
    execution_id: str = ""
    position_id: str = ""

    direction: str = ""
    state: str = ""

    min_confidence: Optional[float] = None
    min_quality: Optional[float] = None
    limit: int = 50

    priority: MemoryRetrievalPriority = (
        MemoryRetrievalPriority.MEDIUM
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

    def validate(self) -> bool:
        if not self.market.strip():
            return False

        if not self.request_id.strip():
            return False

        if not isinstance(
            self.metadata,
            Mapping,
        ):
            return False

        if not isinstance(
            self.retrieval_type,
            MemoryRetrievalType,
        ):
            return False

        if not isinstance(
            self.priority,
            MemoryRetrievalPriority,
        ):
            return False

        if self.limit < 1:
            return False

        if self.limit > 10000:
            return False

        if self.min_confidence is not None:
            try:
                confidence = float(
                    self.min_confidence
                )
            except (TypeError, ValueError):
                return False

            if confidence < 0.0 or confidence > 100.0:
                return False

        if self.min_quality is not None:
            try:
                quality = float(
                    self.min_quality
                )
            except (TypeError, ValueError):
                return False

            if quality < 0.0 or quality > 100.0:
                return False

        return True


# ============================================================
# RETRIEVAL REFERENCE
# ============================================================


@dataclass(frozen=True)
class MemoryRetrievalReference:
    """
    Normalized identity and classification of a retrieved
    historical memory record.
    """

    memory_id: str
    market_name: str
    symbol: str

    retrieval_type: MemoryRetrievalType
    source_type: MemoryRetrievalSourceType

    status: MemoryRetrievalStatus
    priority: MemoryRetrievalPriority

    timestamp: datetime

    timeframe: str = ""
    session: str = ""
    regime: str = ""

    memory_type: str = ""
    state: str = ""
    direction: str = ""

    confidence: Optional[float] = None
    quality: Optional[float] = None

    decision_id: str = ""
    outcome_id: str = ""
    execution_id: str = ""
    position_id: str = ""

    payload: Mapping[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# SOURCE REFERENCE
# ============================================================


@dataclass(frozen=True)
class MemoryRetrievalSourceReference:
    """
    Provenance information for the memory source.
    """

    source_id: str
    source_name: str
    source_type: MemoryRetrievalSourceType

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
class MemoryRetrievalContractValidation:
    valid: bool

    market_available: bool
    retrieval_type_defined: bool
    priority_defined: bool

    symbol_available: bool
    timestamp_valid: bool

    memory_id_available: bool
    source_available: bool

    confidence_valid: bool
    quality_valid: bool

    limit_valid: bool

    filters_valid: bool

    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:
        return self.valid


# ============================================================
# NORMALIZATION HELPERS
# ============================================================


def _mr_read_value(
    source: Any,
    key: str,
    default: Any = None,
) -> Any:
    if source is None:
        return default

    if isinstance(source, Mapping):
        return source.get(key, default)

    return getattr(
        source,
        key,
        default,
    )


def _mr_text(value: Any) -> str:
    if value is None:
        return ""

    try:
        return str(value).strip()
    except Exception:
        return ""


def _mr_timestamp(
    value: Any,
) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(
                tzinfo=timezone.utc
            )
        return value

    if value is not None:
        text = _mr_text(value)

        if text:
            try:
                parsed = datetime.fromisoformat(
                    text.replace(
                        "Z",
                        "+00:00",
                    )
                )

                if parsed.tzinfo is None:
                    parsed = parsed.replace(
                        tzinfo=timezone.utc
                    )

                return parsed

            except ValueError:
                pass

    return datetime.now(timezone.utc)


def _mr_float(
    value: Any,
) -> Optional[float]:
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _mr_enum(
    value: Any,
    enum_type: type[Enum],
    default: Enum,
) -> Enum:
    if isinstance(
        value,
        enum_type,
    ):
        return value

    if value is None:
        return default

    text = _mr_text(value).upper()

    for member in enum_type:
        if text in {
            member.name.upper(),
            str(member.value).upper(),
        }:
            return member

    return default


# ============================================================
# BUILD RETRIEVAL REFERENCE
# ============================================================


def build_memory_retrieval_reference(
    memory: Any,
    request: Optional[MemoryRetrievalRequest] = None,
) -> MemoryRetrievalReference:
    """
    Normalize a historical memory object into the common
    retrieval reference contract.

    Supports Market / Evidence / Decision / Outcome / Pattern
    memory without changing the underlying memory semantics.
    """

    request = request or MemoryRetrievalRequest(
        market=_mr_text(
            _mr_read_value(
                memory,
                "market",
                _mr_read_value(
                    memory,
                    "market_name",
                    "",
                ),
            )
        )
    )

    memory_id = _mr_text(
        _mr_read_value(
            memory,
            "memory_id",
            request.memory_id,
        )
    )

    market_name = _mr_text(
        _mr_read_value(
            memory,
            "market_name",
            _mr_read_value(
                memory,
                "market",
                request.market,
            ),
        )
    )

    symbol = _mr_text(
        _mr_read_value(
            memory,
            "symbol",
            request.symbol,
        )
    )

    retrieval_type = _mr_enum(
        _mr_read_value(
            memory,
            "retrieval_type",
            request.retrieval_type,
        ),
        MemoryRetrievalType,
        MemoryRetrievalType.UNKNOWN,
    )

    source_type = _mr_enum(
        _mr_read_value(
            memory,
            "source_type",
            MemoryRetrievalSourceType.UNKNOWN,
        ),
        MemoryRetrievalSourceType,
        MemoryRetrievalSourceType.UNKNOWN,
    )

    status = _mr_enum(
        _mr_read_value(
            memory,
            "status",
            MemoryRetrievalStatus.FOUND,
        ),
        MemoryRetrievalStatus,
        MemoryRetrievalStatus.FOUND,
    )

    priority = _mr_enum(
        _mr_read_value(
            memory,
            "priority",
            request.priority,
        ),
        MemoryRetrievalPriority,
        MemoryRetrievalPriority.MEDIUM,
    )

    timestamp = _mr_timestamp(
        _mr_read_value(
            memory,
            "timestamp",
            None,
        )
    )

    confidence = _mr_float(
        _mr_read_value(
            memory,
            "confidence",
            None,
        )
    )

    quality = _mr_float(
        _mr_read_value(
            memory,
            "quality",
            None,
        )
    )

    memory_type = _mr_text(
        _mr_read_value(
            memory,
            "memory_type",
            _mr_read_value(
                memory,
                "pattern_type",
                _mr_read_value(
                    memory,
                    "decision_type",
                    _mr_read_value(
                        memory,
                        "outcome_type",
                        _mr_read_value(
                            memory,
                            "evidence_type",
                            request.market_memory_type,
                        ),
                    ),
                ),
            ),
        )
    )

    state = _mr_text(
        _mr_read_value(
            memory,
            "state",
            _mr_read_value(
                memory,
                "pattern_state",
                _mr_read_value(
                    memory,
                    "decision_state",
                    _mr_read_value(
                        memory,
                        "outcome_state",
                        request.state,
                    ),
                ),
            ),
        )
    )

    direction = _mr_text(
        _mr_read_value(
            memory,
            "direction",
            request.direction,
        )
    )

    decision_id = _mr_text(
        _mr_read_value(
            memory,
            "decision_id",
            request.decision_id,
        )
    )

    outcome_id = _mr_text(
        _mr_read_value(
            memory,
            "outcome_id",
            request.outcome_id,
        )
    )

    execution_id = _mr_text(
        _mr_read_value(
            memory,
            "execution_id",
            request.execution_id,
        )
    )

    position_id = _mr_text(
        _mr_read_value(
            memory,
            "position_id",
            request.position_id,
        )
    )

    if isinstance(memory, Mapping):
        payload = dict(memory)
    else:
        payload = {}

        for key in (
            "memory_id",
            "market",
            "market_name",
            "symbol",
            "timestamp",
            "memory_type",
            "pattern_type",
            "decision_type",
            "outcome_type",
            "evidence_type",
            "state",
            "pattern_state",
            "decision_state",
            "outcome_state",
            "direction",
            "confidence",
            "quality",
            "decision_id",
            "outcome_id",
            "execution_id",
            "position_id",
        ):
            value = _mr_read_value(
                memory,
                key,
                None,
            )

            if value is not None:
                payload[key] = value

    return MemoryRetrievalReference(
        memory_id=memory_id,
        market_name=market_name,
        symbol=symbol,
        retrieval_type=retrieval_type,
        source_type=source_type,
        status=status,
        priority=priority,
        timestamp=timestamp,
        timeframe=_mr_text(
            _mr_read_value(
                memory,
                "timeframe",
                request.timeframe,
            )
        ),
        session=_mr_text(
            _mr_read_value(
                memory,
                "session",
                request.session,
            )
        ),
        regime=_mr_text(
            _mr_read_value(
                memory,
                "regime",
                request.regime,
            )
        ),
        memory_type=memory_type,
        state=state,
        direction=direction,
        confidence=confidence,
        quality=quality,
        decision_id=decision_id,
        outcome_id=outcome_id,
        execution_id=execution_id,
        position_id=position_id,
        payload=payload,
    )


# ============================================================
# REQUEST VALIDATION
# ============================================================


def validate_memory_retrieval_request(
    request: MemoryRetrievalRequest,
) -> MemoryRetrievalContractValidation:
    errors: list[str] = []
    warnings: list[str] = []

    market_available = bool(
        _mr_text(request.market)
    )

    retrieval_type_defined = (
        request.retrieval_type
        != MemoryRetrievalType.UNKNOWN
    )

    priority_defined = (
        request.priority
        != MemoryRetrievalPriority.UNKNOWN
    )

    symbol_available = bool(
        _mr_text(request.symbol)
    )

    timestamp_valid = True

    memory_id_available = bool(
        _mr_text(request.memory_id)
    )

    source_available = True

    confidence_valid = True
    quality_valid = True

    limit_valid = (
        isinstance(request.limit, int)
        and 1 <= request.limit <= 10000
    )

    filters_valid = True

    if not market_available:
        errors.append("market_missing")

    if not request.request_id.strip():
        errors.append("request_id_missing")

    if not retrieval_type_defined:
        warnings.append(
            "retrieval_type_unspecified"
        )

    if not priority_defined:
        warnings.append(
            "priority_unspecified"
        )

    if request.min_confidence is not None:
        try:
            confidence = float(
                request.min_confidence
            )

            if not 0.0 <= confidence <= 100.0:
                confidence_valid = False
                errors.append(
                    "min_confidence_out_of_range"
                )

        except (TypeError, ValueError):
            confidence_valid = False
            errors.append(
                "min_confidence_invalid"
            )

    if request.min_quality is not None:
        try:
            quality = float(
                request.min_quality
            )

            if not 0.0 <= quality <= 100.0:
                quality_valid = False
                errors.append(
                    "min_quality_out_of_range"
                )

        except (TypeError, ValueError):
            quality_valid = False
            errors.append(
                "min_quality_invalid"
            )

    if not limit_valid:
        errors.append("limit_invalid")

    if not symbol_available:
        warnings.append("symbol_filter_not_set")

    if request.include_invalid:
        warnings.append(
            "invalid_memory_records_requested"
        )

    if request.include_stale:
        warnings.append(
            "stale_memory_records_requested"
        )

    valid = (
        market_available
        and confidence_valid
        and quality_valid
        and limit_valid
        and filters_valid
        and isinstance(
            request.metadata,
            Mapping,
        )
    )

    return MemoryRetrievalContractValidation(
        valid=valid,
        market_available=market_available,
        retrieval_type_defined=retrieval_type_defined,
        priority_defined=priority_defined,
        symbol_available=symbol_available,
        timestamp_valid=timestamp_valid,
        memory_id_available=memory_id_available,
        source_available=source_available,
        confidence_valid=confidence_valid,
        quality_valid=quality_valid,
        limit_valid=limit_valid,
        filters_valid=filters_valid,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )
# ============================================================
# MEMORY RETRIEVAL — PART 2/5
# Data State / Match Quality / Consistency / Requirements
# Readiness / Confidence / Assessment
# ============================================================


class MemoryRetrievalDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    UNKNOWN = "UNKNOWN"


class MemoryRetrievalMatchQuality(str, Enum):
    EXACT = "EXACT"
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    WEAK = "WEAK"
    NONE = "NONE"
    UNKNOWN = "UNKNOWN"


class MemoryRetrievalConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONFLICTING = "CONFLICTING"
    INSUFFICIENT = "INSUFFICIENT"
    UNKNOWN = "UNKNOWN"


class MemoryRetrievalReadiness(str, Enum):
    READY = "READY"
    CONDITIONAL = "CONDITIONAL"
    NOT_READY = "NOT_READY"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class MemoryRetrievalRequirements:
    request_valid: bool
    market_available: bool
    symbol_available: bool
    retrieval_type_defined: bool
    priority_defined: bool

    memory_available: bool
    memory_id_available: bool
    source_available: bool
    timestamp_available: bool

    timeframe_available: bool
    session_available: bool
    regime_available: bool

    state_available: bool
    direction_available: bool

    confidence_available: bool
    quality_available: bool

    data_state: MemoryRetrievalDataState
    match_quality: MemoryRetrievalMatchQuality
    consistency: MemoryRetrievalConsistency
    readiness: MemoryRetrievalReadiness

    completeness_score: float
    match_score: float

    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class MemoryRetrievalAssessment:
    readiness: MemoryRetrievalReadiness
    data_state: MemoryRetrievalDataState
    match_quality: MemoryRetrievalMatchQuality
    consistency: MemoryRetrievalConsistency

    confidence_score: float
    completeness_score: float
    match_score: float

    matched_fields: tuple[str, ...] = ()
    unmatched_fields: tuple[str, ...] = ()

    strengths: tuple[str, ...] = ()
    weaknesses: tuple[str, ...] = ()

    rationale: str = ""


def _mr_bool(value: Any) -> bool:
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
            "match",
            "matched",
        }

    return bool(value)


def _mr_conflict_detected(
    reference: MemoryRetrievalReference,
    request: Optional[MemoryRetrievalRequest] = None,
) -> bool:
    """
    Detect explicit retrieval conflicts.

    Retrieval conflict means the requested historical context
    cannot be interpreted consistently against the retrieved
    record.

    This function does not infer a trading decision.
    """

    payload = reference.payload

    for key in (
        "conflict",
        "has_conflict",
        "memory_conflict",
        "retrieval_conflict",
        "data_conflict",
    ):
        if _mr_bool(payload.get(key)):
            return True

    if (
        reference.confidence is not None
        and (
            reference.confidence < 0.0
            or reference.confidence > 100.0
        )
    ):
        return True

    if (
        reference.quality is not None
        and (
            reference.quality < 0.0
            or reference.quality > 100.0
        )
    ):
        return True

    if request is not None:
        if (
            request.min_confidence is not None
            and reference.confidence is not None
            and reference.confidence
            < request.min_confidence
        ):
            return False

        if (
            request.min_quality is not None
            and reference.quality is not None
            and reference.quality
            < request.min_quality
        ):
            return False

    return False


def evaluate_memory_retrieval_data_state(
    reference: MemoryRetrievalReference,
) -> MemoryRetrievalDataState:
    """
    Evaluate structural availability of a retrieved memory.
    """

    checks = (
        bool(reference.memory_id.strip()),
        bool(reference.market_name.strip()),
        bool(reference.symbol.strip()),
        reference.retrieval_type
        != MemoryRetrievalType.UNKNOWN,
        reference.source_type
        != MemoryRetrievalSourceType.UNKNOWN,
        isinstance(reference.timestamp, datetime),
    )

    available = sum(
        1 for item in checks if item
    )

    if available == len(checks):
        return MemoryRetrievalDataState.COMPLETE

    if available == 0:
        return MemoryRetrievalDataState.MISSING

    return MemoryRetrievalDataState.PARTIAL


def _mr_field_match(
    request_value: Any,
    memory_value: Any,
) -> Optional[bool]:
    """
    Return:
        True  -> explicit match
        False -> explicit mismatch
        None  -> filter not supplied
    """

    request_text = _mr_text(request_value)

    if not request_text:
        return None

    memory_text = _mr_text(memory_value)

    if not memory_text:
        return False

    return (
        request_text.casefold()
        == memory_text.casefold()
    )


def evaluate_memory_retrieval_match(
    request: MemoryRetrievalRequest,
    reference: MemoryRetrievalReference,
) -> tuple[
    MemoryRetrievalMatchQuality,
    float,
    tuple[str, ...],
    tuple[str, ...],
]:
    """
    Evaluate how closely a retrieved memory matches the
    explicit retrieval request.

    Only explicit request filters participate.
    """

    comparisons: list[tuple[str, Optional[bool]]] = [
        (
            "market",
            _mr_field_match(
                request.market,
                reference.market_name,
            ),
        ),
        (
            "symbol",
            _mr_field_match(
                request.symbol,
                reference.symbol,
            ),
        ),
        (
            "timeframe",
            _mr_field_match(
                request.timeframe,
                reference.timeframe,
            ),
        ),
        (
            "session",
            _mr_field_match(
                request.session,
                reference.session,
            ),
        ),
        (
            "regime",
            _mr_field_match(
                request.regime,
                reference.regime,
            ),
        ),
        (
            "direction",
            _mr_field_match(
                request.direction,
                reference.direction,
            ),
        ),
        (
            "state",
            _mr_field_match(
                request.state,
                reference.state,
            ),
        ),
        (
            "memory_id",
            _mr_field_match(
                request.memory_id,
                reference.memory_id,
            ),
        ),
        (
            "decision_id",
            _mr_field_match(
                request.decision_id,
                reference.decision_id,
            ),
        ),
        (
            "outcome_id",
            _mr_field_match(
                request.outcome_id,
                reference.outcome_id,
            ),
        ),
        (
            "execution_id",
            _mr_field_match(
                request.execution_id,
                reference.execution_id,
            ),
        ),
        (
            "position_id",
            _mr_field_match(
                request.position_id,
                reference.position_id,
            ),
        ),
    ]

    if (
        request.retrieval_type
        != MemoryRetrievalType.UNKNOWN
    ):
        comparisons.append(
            (
                "retrieval_type",
                request.retrieval_type
                == reference.retrieval_type,
            )
        )

    if request.market_memory_type:
        comparisons.append(
            (
                "memory_type",
                _mr_field_match(
                    request.market_memory_type,
                    reference.memory_type,
                ),
            )
        )

    if request.pattern_type:
        comparisons.append(
            (
                "pattern_type",
                _mr_field_match(
                    request.pattern_type,
                    reference.memory_type,
                ),
            )
        )

    if request.decision_type:
        comparisons.append(
            (
                "decision_type",
                _mr_field_match(
                    request.decision_type,
                    reference.memory_type,
                ),
            )
        )

    if request.outcome_type:
        comparisons.append(
            (
                "outcome_type",
                _mr_field_match(
                    request.outcome_type,
                    reference.memory_type,
                ),
            )
        )

    if request.evidence_type:
        comparisons.append(
            (
                "evidence_type",
                _mr_field_match(
                    request.evidence_type,
                    reference.memory_type,
                ),
            )
        )

    matched_fields: list[str] = []
    unmatched_fields: list[str] = []

    explicit_results: list[bool] = []

    for field_name, matched in comparisons:
        if matched is None:
            continue

        explicit_results.append(matched)

        if matched:
            matched_fields.append(field_name)
        else:
            unmatched_fields.append(field_name)

    if not explicit_results:
        return (
            MemoryRetrievalMatchQuality.UNKNOWN,
            0.0,
            tuple(),
            tuple(),
        )

    matched = sum(
        1 for value in explicit_results
        if value
    )

    total = len(explicit_results)

    match_score = round(
        (matched / total) * 100.0,
        2,
    )

    if match_score >= 100.0:
        quality = MemoryRetrievalMatchQuality.EXACT

    elif match_score >= 80.0:
        quality = MemoryRetrievalMatchQuality.STRONG

    elif match_score >= 60.0:
        quality = MemoryRetrievalMatchQuality.MODERATE

    elif match_score > 0.0:
        quality = MemoryRetrievalMatchQuality.WEAK

    else:
        quality = MemoryRetrievalMatchQuality.NONE

    return (
        quality,
        match_score,
        tuple(matched_fields),
        tuple(unmatched_fields),
    )


def evaluate_memory_retrieval_consistency(
    reference: MemoryRetrievalReference,
    request: Optional[MemoryRetrievalRequest] = None,
) -> MemoryRetrievalConsistency:
    """
    Evaluate consistency of retrieved memory and explicit
    retrieval criteria.
    """

    if _mr_conflict_detected(
        reference,
        request,
    ):
        return MemoryRetrievalConsistency.CONFLICTING

    if (
        reference.status
        == MemoryRetrievalStatus.INVALID
    ):
        return MemoryRetrievalConsistency.CONFLICTING

    if (
        reference.status
        == MemoryRetrievalStatus.EMPTY
    ):
        return MemoryRetrievalConsistency.INSUFFICIENT

    structural_values = (
        reference.memory_id,
        reference.market_name,
        reference.symbol,
    )

    if not any(
        _mr_text(value)
        for value in structural_values
    ):
        return MemoryRetrievalConsistency.INSUFFICIENT

    if (
        reference.retrieval_type
        == MemoryRetrievalType.UNKNOWN
    ):
        return MemoryRetrievalConsistency.INSUFFICIENT

    return MemoryRetrievalConsistency.CONSISTENT


def evaluate_memory_retrieval_requirements(
    request: MemoryRetrievalRequest,
    reference: MemoryRetrievalReference,
) -> MemoryRetrievalRequirements:
    """
    Build normalized retrieval requirements.
    """

    request_validation = (
        validate_memory_retrieval_request(request)
    )

    data_state = evaluate_memory_retrieval_data_state(
        reference
    )

    (
        match_quality,
        match_score,
        matched_fields,
        unmatched_fields,
    ) = evaluate_memory_retrieval_match(
        request,
        reference,
    )

    consistency = evaluate_memory_retrieval_consistency(
        reference,
        request,
    )

    checks = {
        "market_available":
            bool(reference.market_name.strip()),

        "symbol_available":
            bool(reference.symbol.strip()),

        "retrieval_type_defined":
            reference.retrieval_type
            != MemoryRetrievalType.UNKNOWN,

        "priority_defined":
            reference.priority
            != MemoryRetrievalPriority.UNKNOWN,

        "memory_available":
            bool(reference.memory_id.strip()),

        "memory_id_available":
            bool(reference.memory_id.strip()),

        "source_available":
            reference.source_type
            != MemoryRetrievalSourceType.UNKNOWN,

        "timestamp_available":
            isinstance(
                reference.timestamp,
                datetime,
            ),

        "timeframe_available":
            bool(reference.timeframe.strip()),

        "session_available":
            bool(reference.session.strip()),

        "regime_available":
            bool(reference.regime.strip()),

        "state_available":
            bool(reference.state.strip()),

        "direction_available":
            bool(reference.direction.strip()),

        "confidence_available":
            reference.confidence is not None,

        "quality_available":
            reference.quality is not None,
    }

    available = sum(
        1
        for value in checks.values()
        if value
    )

    total = len(checks)

    completeness_score = round(
        (available / total) * 100.0,
        2,
    ) if total else 0.0

    warnings: list[str] = []

    if not checks["symbol_available"]:
        warnings.append("symbol_missing")

    if not checks["source_available"]:
        warnings.append("source_missing")

    if not checks["timeframe_available"]:
        warnings.append("timeframe_missing")

    if not checks["session_available"]:
        warnings.append("session_missing")

    if not checks["regime_available"]:
        warnings.append("regime_missing")

    if not checks["confidence_available"]:
        warnings.append("confidence_missing")

    if not checks["quality_available"]:
        warnings.append("quality_missing")

    if unmatched_fields:
        warnings.append(
            "retrieval_filter_mismatch"
        )

    readiness = evaluate_memory_retrieval_readiness(
        request_valid=request_validation.valid,
        data_state=data_state,
        consistency=consistency,
        match_quality=match_quality,
        completeness_score=completeness_score,
        match_score=match_score,
    )

    return MemoryRetrievalRequirements(
        request_valid=request_validation.valid,
        market_available=checks["market_available"],
        symbol_available=checks["symbol_available"],
        retrieval_type_defined=
            checks["retrieval_type_defined"],
        priority_defined=
            checks["priority_defined"],
        memory_available=
            checks["memory_available"],
        memory_id_available=
            checks["memory_id_available"],
        source_available=
            checks["source_available"],
        timestamp_available=
            checks["timestamp_available"],
        timeframe_available=
            checks["timeframe_available"],
        session_available=
            checks["session_available"],
        regime_available=
            checks["regime_available"],
        state_available=
            checks["state_available"],
        direction_available=
            checks["direction_available"],
        confidence_available=
            checks["confidence_available"],
        quality_available=
            checks["quality_available"],
        data_state=data_state,
        match_quality=match_quality,
        consistency=consistency,
        readiness=readiness,
        completeness_score=completeness_score,
        match_score=match_score,
        warnings=tuple(warnings),
    )


def evaluate_memory_retrieval_readiness(
    request_valid: bool,
    data_state: MemoryRetrievalDataState,
    consistency: MemoryRetrievalConsistency,
    match_quality: MemoryRetrievalMatchQuality,
    completeness_score: float,
    match_score: float,
) -> MemoryRetrievalReadiness:
    """
    Retrieval readiness gate.

    Retrieval readiness is about the integrity and relevance
    of historical memory retrieval, not trading readiness.
    """

    if not request_valid:
        return MemoryRetrievalReadiness.NOT_READY

    if (
        consistency
        == MemoryRetrievalConsistency.CONFLICTING
    ):
        return MemoryRetrievalReadiness.NOT_READY

    if (
        data_state
        == MemoryRetrievalDataState.MISSING
    ):
        return MemoryRetrievalReadiness.NOT_READY

    if (
        match_quality
        == MemoryRetrievalMatchQuality.NONE
    ):
        return MemoryRetrievalReadiness.NOT_READY

    if (
        completeness_score >= 85.0
        and match_score >= 80.0
    ):
        return MemoryRetrievalReadiness.READY

    if (
        completeness_score >= 50.0
        and match_score >= 50.0
    ):
        return MemoryRetrievalReadiness.CONDITIONAL

    if (
        match_quality
        == MemoryRetrievalMatchQuality.UNKNOWN
    ):
        return MemoryRetrievalReadiness.UNKNOWN

    return MemoryRetrievalReadiness.NOT_READY


def calculate_memory_retrieval_confidence(
    requirements: MemoryRetrievalRequirements,
) -> float:
    """
    Calculate confidence in retrieval integrity/relevance.

    This is retrieval confidence, not market prediction
    confidence.
    """

    score = (
        requirements.completeness_score * 0.45
        + requirements.match_score * 0.55
    )

    if (
        requirements.consistency
        == MemoryRetrievalConsistency.CONSISTENT
    ):
        score += 5.0

    elif (
        requirements.consistency
        == MemoryRetrievalConsistency.CONFLICTING
    ):
        score -= 30.0

    elif (
        requirements.consistency
        == MemoryRetrievalConsistency.INSUFFICIENT
    ):
        score -= 15.0

    if (
        requirements.data_state
        == MemoryRetrievalDataState.MISSING
    ):
        score -= 20.0

    elif (
        requirements.data_state
        == MemoryRetrievalDataState.UNKNOWN
    ):
        score -= 20.0

    return round(
        max(
            0.0,
            min(100.0, score),
        ),
        2,
    )


def classify_memory_retrieval_confidence(
    confidence_score: float,
) -> MemoryRetrievalMatchQuality:
    """
    Classify retrieval confidence/relevance.
    """

    if confidence_score >= 90.0:
        return MemoryRetrievalMatchQuality.EXACT

    if confidence_score >= 75.0:
        return MemoryRetrievalMatchQuality.STRONG

    if confidence_score >= 50.0:
        return MemoryRetrievalMatchQuality.MODERATE

    if confidence_score > 0.0:
        return MemoryRetrievalMatchQuality.WEAK

    return MemoryRetrievalMatchQuality.NONE


def build_memory_retrieval_assessment(
    request: MemoryRetrievalRequest,
    reference: MemoryRetrievalReference,
    requirements: Optional[
        MemoryRetrievalRequirements
    ] = None,
) -> MemoryRetrievalAssessment:
    """
    Build the normalized retrieval assessment.
    """

    if requirements is None:
        requirements = (
            evaluate_memory_retrieval_requirements(
                request,
                reference,
            )
        )

    confidence_score = (
        calculate_memory_retrieval_confidence(
            requirements
        )
    )

    (
        match_quality,
        match_score,
        matched_fields,
        unmatched_fields,
    ) = evaluate_memory_retrieval_match(
        request,
        reference,
    )

    strengths: list[str] = []
    weaknesses: list[str] = []

    if requirements.market_available:
        strengths.append("market_match_available")

    if requirements.symbol_available:
        strengths.append("symbol_available")

    if requirements.memory_available:
        strengths.append("memory_identity_available")

    if requirements.source_available:
        strengths.append("source_provenance_available")

    if requirements.timestamp_available:
        strengths.append("timestamp_available")

    if (
        requirements.consistency
        == MemoryRetrievalConsistency.CONSISTENT
    ):
        strengths.append("retrieval_consistency_valid")

    if matched_fields:
        strengths.append(
            "explicit_filters_matched"
        )

    for warning in requirements.warnings:
        weaknesses.append(warning)

    if (
        requirements.consistency
        == MemoryRetrievalConsistency.CONFLICTING
    ):
        weaknesses.append(
            "retrieval_conflict"
        )

    if (
        requirements.match_quality
        == MemoryRetrievalMatchQuality.NONE
    ):
        weaknesses.append(
            "no_matching_memory"
        )

    if (
        requirements.data_state
        == MemoryRetrievalDataState.MISSING
    ):
        weaknesses.append(
            "retrieval_data_missing"
        )

    if (
        requirements.readiness
        == MemoryRetrievalReadiness.READY
    ):
        rationale = (
            "Historical memory retrieval is structurally "
            "complete, consistent and strongly matched to "
            "the explicit retrieval criteria."
        )

    elif (
        requirements.readiness
        == MemoryRetrievalReadiness.CONDITIONAL
    ):
        rationale = (
            "Historical memory retrieval is partially matched "
            "and should be treated as conditional context."
        )

    elif (
        requirements.readiness
        == MemoryRetrievalReadiness.NOT_READY
    ):
        rationale = (
            "Historical memory retrieval is insufficient, "
            "conflicting or not sufficiently matched."
        )

    else:
        rationale = (
            "Historical memory retrieval state could not be "
            "fully established."
        )

    return MemoryRetrievalAssessment(
        readiness=requirements.readiness,
        data_state=requirements.data_state,
        match_quality=match_quality,
        consistency=requirements.consistency,
        confidence_score=confidence_score,
        completeness_score=
            requirements.completeness_score,
        match_score=match_score,
        matched_fields=matched_fields,
        unmatched_fields=unmatched_fields,
        strengths=tuple(strengths),
        weaknesses=tuple(weaknesses),
        rationale=rationale,
    )
# ============================================================
# ROBOMLM_PLUS
# app/intelligence/memory/memory_retrieval.py
# PART 3 — ACTION / RESULT / CONTRACT / ENGINE
# ============================================================

class MemoryRetrievalActionState(str, Enum):
    NONE = "NONE"
    SEARCH = "SEARCH"
    RETRIEVE = "RETRIEVE"
    REVIEW = "REVIEW"
    HOLD = "HOLD"
    INVALIDATE = "INVALIDATE"
    COMPLETE = "COMPLETE"


class MemoryRetrievalContractState(str, Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


class MemoryRetrievalResultStatus(str, Enum):
    FOUND = "FOUND"
    PARTIAL = "PARTIAL"
    REVIEW = "REVIEW"
    EMPTY = "EMPTY"
    HOLD = "HOLD"
    INVALIDATED = "INVALIDATED"
    COMPLETED = "COMPLETED"
    INVALID = "INVALID"


@dataclass(frozen=True)
class MemoryRetrievalAction:
    state: MemoryRetrievalActionState = MemoryRetrievalActionState.NONE
    action_id: str = field(default_factory=lambda: str(uuid4()))
    reason: str = ""
    is_action_request: bool = False


@dataclass(frozen=True)
class MemoryRetrievalResult:
    status: MemoryRetrievalResultStatus
    result_id: str = field(default_factory=lambda: str(uuid4()))
    request_id: str = ""
    reference: Optional[MemoryRetrievalReference] = None
    assessment: Optional[MemoryRetrievalAssessment] = None
    action: Optional[MemoryRetrievalAction] = None
    matched_count: int = 0
    returned_count: int = 0
    references: Sequence[MemoryRetrievalReference] = field(
        default_factory=tuple
    )
    warnings: Sequence[str] = field(default_factory=tuple)
    errors: Sequence[str] = field(default_factory=tuple)
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass(frozen=True)
class MemoryRetrievalContract:
    state: MemoryRetrievalContractState
    contract_id: str = field(default_factory=lambda: str(uuid4()))
    request_id: str = ""
    result_id: str = ""
    valid: bool = False
    request_valid: bool = False
    assessment_available: bool = False
    result_available: bool = False
    references_available: bool = False
    errors: Sequence[str] = field(default_factory=tuple)
    warnings: Sequence[str] = field(default_factory=tuple)


# ------------------------------------------------------------
# RESULT STATUS
# ------------------------------------------------------------

def determine_memory_retrieval_result_status(
    assessment: MemoryRetrievalAssessment,
    references: Sequence[MemoryRetrievalReference] = (),
    request_valid: bool = True,
) -> MemoryRetrievalResultStatus:

    if not request_valid:
        return MemoryRetrievalResultStatus.INVALID

    if assessment.consistency == MemoryRetrievalConsistency.CONFLICTING:
        return MemoryRetrievalResultStatus.INVALIDATED

    if assessment.data_state == MemoryRetrievalDataState.MISSING:
        return MemoryRetrievalResultStatus.EMPTY

    if assessment.match_quality == MemoryRetrievalMatchQuality.NONE:
        return MemoryRetrievalResultStatus.EMPTY

    if assessment.readiness == MemoryRetrievalReadiness.NOT_READY:
        if references:
            return MemoryRetrievalResultStatus.HOLD
        return MemoryRetrievalResultStatus.EMPTY

    if assessment.readiness == MemoryRetrievalReadiness.CONDITIONAL:
        return MemoryRetrievalResultStatus.PARTIAL

    if assessment.readiness == MemoryRetrievalReadiness.READY:
        if references:
            return MemoryRetrievalResultStatus.FOUND
        return MemoryRetrievalResultStatus.EMPTY

    return MemoryRetrievalResultStatus.REVIEW


# ------------------------------------------------------------
# ACTION BUILDER
# ------------------------------------------------------------

def build_memory_retrieval_action(
    status: MemoryRetrievalResultStatus,
) -> MemoryRetrievalAction:

    if status == MemoryRetrievalResultStatus.FOUND:
        return MemoryRetrievalAction(
            state=MemoryRetrievalActionState.RETRIEVE,
            reason="Valid retrieval result available.",
        )

    if status == MemoryRetrievalResultStatus.PARTIAL:
        return MemoryRetrievalAction(
            state=MemoryRetrievalActionState.REVIEW,
            reason="Retrieval is conditional and requires contextual review.",
        )

    if status == MemoryRetrievalResultStatus.REVIEW:
        return MemoryRetrievalAction(
            state=MemoryRetrievalActionState.REVIEW,
            reason="Retrieval state requires review.",
        )

    if status == MemoryRetrievalResultStatus.EMPTY:
        return MemoryRetrievalAction(
            state=MemoryRetrievalActionState.SEARCH,
            reason="No sufficiently matched memory was returned.",
        )

    if status == MemoryRetrievalResultStatus.HOLD:
        return MemoryRetrievalAction(
            state=MemoryRetrievalActionState.HOLD,
            reason="Retrieval cannot safely advance.",
        )

    if status == MemoryRetrievalResultStatus.INVALIDATED:
        return MemoryRetrievalAction(
            state=MemoryRetrievalActionState.INVALIDATE,
            reason="Retrieval contains conflicting or invalid memory state.",
        )

    if status == MemoryRetrievalResultStatus.COMPLETED:
        return MemoryRetrievalAction(
            state=MemoryRetrievalActionState.COMPLETE,
            reason="Retrieval lifecycle completed.",
        )

    return MemoryRetrievalAction(
        state=MemoryRetrievalActionState.NONE,
        reason="No retrieval action determined.",
    )


# ------------------------------------------------------------
# RESULT BUILDER
# ------------------------------------------------------------

def build_memory_retrieval_result(
    request: MemoryRetrievalRequest,
    assessment: MemoryRetrievalAssessment,
    references: Sequence[MemoryRetrievalReference] = (),
) -> MemoryRetrievalResult:

    refs = tuple(references)

    status = determine_memory_retrieval_result_status(
        assessment=assessment,
        references=refs,
        request_valid=True,
    )

    action = build_memory_retrieval_action(status)

    warnings = list(assessment.weaknesses)
    errors = []

    if assessment.consistency == MemoryRetrievalConsistency.CONFLICTING:
        errors.append(
            "Conflicting memory retrieval state detected."
        )

    if status == MemoryRetrievalResultStatus.INVALIDATED:
        errors.append(
            "Retrieval result invalidated because consistency failed."
        )

    return MemoryRetrievalResult(
        status=status,
        request_id=request.request_id,
        reference=refs[0] if refs else None,
        assessment=assessment,
        action=action,
        matched_count=len(refs),
        returned_count=min(len(refs), request.limit),
        references=refs[: request.limit],
        warnings=tuple(warnings),
        errors=tuple(errors),
    )


# ------------------------------------------------------------
# CONTRACT BUILDER
# ------------------------------------------------------------

def build_memory_retrieval_contract(
    request: MemoryRetrievalRequest,
    result: MemoryRetrievalResult,
) -> MemoryRetrievalContract:

    errors = list(result.errors)
    warnings = list(result.warnings)

    request_validation = validate_memory_retrieval_request(request)

    request_valid = bool(request_validation.valid)
    assessment_available = result.assessment is not None
    result_available = result.status != MemoryRetrievalResultStatus.INVALID
    references_available = bool(result.references)

    if not request_valid:
        errors.extend(request_validation.errors)

    if result.status == MemoryRetrievalResultStatus.INVALIDATED:
        state = MemoryRetrievalContractState.INVALID
        valid = False

    elif not request_valid:
        state = MemoryRetrievalContractState.INVALID
        valid = False

    elif not assessment_available:
        state = MemoryRetrievalContractState.INCOMPLETE
        valid = False

    elif result.status == MemoryRetrievalResultStatus.HOLD:
        state = MemoryRetrievalContractState.BLOCKED
        valid = False

    elif result.status == MemoryRetrievalResultStatus.REVIEW:
        state = MemoryRetrievalContractState.INCOMPLETE
        valid = False

    else:
        state = MemoryRetrievalContractState.COMPLETE
        valid = True

    return MemoryRetrievalContract(
        state=state,
        request_id=request.request_id,
        result_id=result.result_id,
        valid=valid,
        request_valid=request_valid,
        assessment_available=assessment_available,
        result_available=result_available,
        references_available=references_available,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


# ------------------------------------------------------------
# ENGINE
# ------------------------------------------------------------

class MemoryRetrievalEngine:
    """
    Memory Retrieval Engine.

    Responsibilities:
    - validate retrieval request
    - normalize memory records
    - evaluate match
    - evaluate consistency
    - assess retrieval readiness
    - build retrieval result
    - build retrieval contract

    This engine retrieves memory.
    It does NOT:
    - generate trading decisions
    - modify D13
    - override Risk
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
        return MEMORY_RETRIEVAL_ENGINE

    @property
    def version(self) -> str:
        return MEMORY_RETRIEVAL_VERSION

    def evaluate(
        self,
        request: MemoryRetrievalRequest,
        memory: Any,
    ) -> MemoryRetrievalResult:

        validation = validate_memory_retrieval_request(request)

        if not validation.valid:
            empty_assessment = MemoryRetrievalAssessment(
                readiness=MemoryRetrievalReadiness.NOT_READY,
                data_state=MemoryRetrievalDataState.UNKNOWN,
                match_quality=MemoryRetrievalMatchQuality.NONE,
                consistency=MemoryRetrievalConsistency.INSUFFICIENT,
                confidence_score=0.0,
                completeness_score=0.0,
                match_score=0.0,
                matched_fields=(),
                unmatched_fields=(),
                strengths=(),
                weaknesses=tuple(validation.errors),
                rationale="Retrieval request validation failed.",
            )

            result = MemoryRetrievalResult(
                status=MemoryRetrievalResultStatus.INVALID,
                request_id=request.request_id,
                assessment=empty_assessment,
                action=build_memory_retrieval_action(
                    MemoryRetrievalResultStatus.INVALID
                ),
                errors=tuple(validation.errors),
            )

            return result

        reference = build_memory_retrieval_reference(
            memory=memory,
            request=request,
        )

        data_state = evaluate_memory_retrieval_data_state(reference)
        match_quality, match_score, matched_fields, unmatched_fields = (
            evaluate_memory_retrieval_match(
                request=request,
                reference=reference,
            )
        )

        consistency = evaluate_memory_retrieval_consistency(
            request=request,
            reference=reference,
        )

        requirements = evaluate_memory_retrieval_requirements(
            request=request,
            reference=reference,
            data_state=data_state,
            match_quality=match_quality,
            consistency=consistency,
        )

        confidence_score = calculate_memory_retrieval_confidence(
            completeness_score=requirements.completeness_score,
            match_score=requirements.match_score,
            consistency=consistency,
            data_state=data_state,
        )

        assessment = build_memory_retrieval_assessment(
            request=request,
            reference=reference,
            requirements=requirements,
            confidence_score=confidence_score,
        )

        return build_memory_retrieval_result(
            request=request,
            assessment=assessment,
            references=(reference,),
        )

    def search(
        self,
        request: MemoryRetrievalRequest,
        memories: Sequence[Any],
    ) -> MemoryRetrievalResult:

        validation = validate_memory_retrieval_request(request)

        if not validation.valid:
            return self.evaluate(
                request=request,
                memory={},
            )

        references = []

        for memory in memories:
            reference = build_memory_retrieval_reference(
                memory=memory,
                request=request,
            )

            data_state = evaluate_memory_retrieval_data_state(
                reference
            )

            match_quality, match_score, _, _ = (
                evaluate_memory_retrieval_match(
                    request=request,
                    reference=reference,
                )
            )

            consistency = evaluate_memory_retrieval_consistency(
                request=request,
                reference=reference,
            )

            if consistency == MemoryRetrievalConsistency.CONFLICTING:
                continue

            if data_state == MemoryRetrievalDataState.MISSING:
                continue

            if match_quality == MemoryRetrievalMatchQuality.NONE:
                continue

            if match_score < 50.0:
                continue

            if (
                reference.status == MemoryRetrievalStatus.INVALID
                and not request.include_invalid
            ):
                continue

            if (
                reference.status == MemoryRetrievalStatus.STALE
                and not request.include_stale
            ):
                continue

            references.append(reference)

        references = tuple(
            references[: request.limit]
        )

        if references:
            primary = references[0]

            data_state = evaluate_memory_retrieval_data_state(
                primary
            )

            match_quality, match_score, _, _ = (
                evaluate_memory_retrieval_match(
                    request=request,
                    reference=primary,
                )
            )

            consistency = evaluate_memory_retrieval_consistency(
                request=request,
                reference=primary,
            )

            requirements = evaluate_memory_retrieval_requirements(
                request=request,
                reference=primary,
                data_state=data_state,
                match_quality=match_quality,
                consistency=consistency,
            )

            confidence_score = calculate_memory_retrieval_confidence(
                completeness_score=requirements.completeness_score,
                match_score=match_score,
                consistency=consistency,
                data_state=data_state,
            )

            assessment = build_memory_retrieval_assessment(
                request=request,
                reference=primary,
                requirements=requirements,
                confidence_score=confidence_score,
            )
        else:
            assessment = MemoryRetrievalAssessment(
                readiness=MemoryRetrievalReadiness.NOT_READY,
                data_state=MemoryRetrievalDataState.MISSING,
                match_quality=MemoryRetrievalMatchQuality.NONE,
                consistency=MemoryRetrievalConsistency.INSUFFICIENT,
                confidence_score=0.0,
                completeness_score=0.0,
                match_score=0.0,
                matched_fields=(),
                unmatched_fields=(),
                strengths=(),
                weaknesses=("No sufficiently matched memory found.",),
                rationale="No memory record satisfied retrieval constraints.",
            )

        return build_memory_retrieval_result(
            request=request,
            assessment=assessment,
            references=references,
        )

    def retrieve(
        self,
        request: MemoryRetrievalRequest,
        memories: Sequence[Any],
    ) -> MemoryRetrievalResult:
        return self.search(
            request=request,
            memories=memories,
        )

    def review(
        self,
        result: MemoryRetrievalResult,
    ) -> MemoryRetrievalResult:

        if result.status in {
            MemoryRetrievalResultStatus.INVALID,
            MemoryRetrievalResultStatus.INVALIDATED,
        }:
            return result

        if result.assessment is None:
            return MemoryRetrievalResult(
                status=MemoryRetrievalResultStatus.REVIEW,
                result_id=result.result_id,
                request_id=result.request_id,
                references=result.references,
                warnings=result.warnings,
                errors=("Retrieval assessment is unavailable.",),
            )

        return MemoryRetrievalResult(
            status=MemoryRetrievalResultStatus.REVIEW,
            result_id=result.result_id,
            request_id=result.request_id,
            reference=result.reference,
            assessment=result.assessment,
            action=MemoryRetrievalAction(
                state=MemoryRetrievalActionState.REVIEW,
                reason="Retrieval explicitly placed into review.",
            ),
            matched_count=result.matched_count,
            returned_count=result.returned_count,
            references=result.references,
            warnings=result.warnings,
            errors=result.errors,
        )


# ------------------------------------------------------------
# SINGLETON + PUBLIC OPERATIONS
# ------------------------------------------------------------

_MEMORY_RETRIEVAL_ENGINE = MemoryRetrievalEngine()


def evaluate_memory_retrieval(
    request: MemoryRetrievalRequest,
    memory: Any,
) -> MemoryRetrievalResult:
    return _MEMORY_RETRIEVAL_ENGINE.evaluate(
        request=request,
        memory=memory,
    )


def search_memory(
    request: MemoryRetrievalRequest,
    memories: Sequence[Any],
) -> MemoryRetrievalResult:
    return _MEMORY_RETRIEVAL_ENGINE.search(
        request=request,
        memories=memories,
    )


def retrieve_memory(
    request: MemoryRetrievalRequest,
    memories: Sequence[Any],
) -> MemoryRetrievalResult:
    return _MEMORY_RETRIEVAL_ENGINE.retrieve(
        request=request,
        memories=memories,
    )


def review_memory_retrieval(
    result: MemoryRetrievalResult,
) -> MemoryRetrievalResult:
    return _MEMORY_RETRIEVAL_ENGINE.review(result)


def get_memory_retrieval_engine() -> MemoryRetrievalEngine:
    return _MEMORY_RETRIEVAL_ENGINE
# ============================================================
# PART 4 — VALIDATION / READINESS / ACCESSORS / SAFETY
# ============================================================

def validate_memory_retrieval_result(
    result: MemoryRetrievalResult,
) -> bool:
    if not isinstance(result, MemoryRetrievalResult):
        return False

    if not result.result_id:
        return False

    if not result.request_id:
        return False

    if result.matched_count < 0 or result.returned_count < 0:
        return False

    if result.returned_count > result.matched_count:
        return False

    if result.returned_count != len(result.references):
        return False

    if result.status == MemoryRetrievalResultStatus.INVALID:
        return False

    if result.status == MemoryRetrievalResultStatus.INVALIDATED:
        return False

    return True


def validate_memory_retrieval_contract(
    contract: MemoryRetrievalContract,
) -> bool:
    if not isinstance(contract, MemoryRetrievalContract):
        return False

    if not contract.contract_id:
        return False

    if not contract.request_id:
        return False

    if contract.valid and contract.state != (
        MemoryRetrievalContractState.COMPLETE
    ):
        return False

    if contract.state == MemoryRetrievalContractState.INVALID:
        return False

    if contract.state == MemoryRetrievalContractState.BLOCKED:
        return False

    return True


# ------------------------------------------------------------
# STRICT READY GATE
# ------------------------------------------------------------

def memory_retrieval_ready(
    result: MemoryRetrievalResult,
) -> bool:
    if not validate_memory_retrieval_result(result):
        return False

    if result.status != MemoryRetrievalResultStatus.FOUND:
        return False

    if result.assessment is None:
        return False

    assessment = result.assessment

    if assessment.readiness != MemoryRetrievalReadiness.READY:
        return False

    if assessment.data_state != (
        MemoryRetrievalDataState.COMPLETE
    ):
        return False

    if assessment.consistency != (
        MemoryRetrievalConsistency.CONSISTENT
    ):
        return False

    if assessment.match_quality not in {
        MemoryRetrievalMatchQuality.EXACT,
        MemoryRetrievalMatchQuality.STRONG,
    }:
        return False

    if assessment.confidence_score < 80.0:
        return False

    if assessment.completeness_score < 85.0:
        return False

    if assessment.match_score < 80.0:
        return False

    if not result.references:
        return False

    return True


# ------------------------------------------------------------
# ADVANCE GATE
# ------------------------------------------------------------

def memory_retrieval_can_advance(
    result: MemoryRetrievalResult,
) -> bool:
    if not validate_memory_retrieval_result(result):
        return False

    if result.status in {
        MemoryRetrievalResultStatus.INVALID,
        MemoryRetrievalResultStatus.INVALIDATED,
        MemoryRetrievalResultStatus.HOLD,
    }:
        return False

    if result.assessment is None:
        return False

    assessment = result.assessment

    if assessment.consistency == (
        MemoryRetrievalConsistency.CONFLICTING
    ):
        return False

    if assessment.data_state in {
        MemoryRetrievalDataState.MISSING,
        MemoryRetrievalDataState.UNKNOWN,
    }:
        return False

    if assessment.confidence_score < 50.0:
        return False

    if assessment.match_score < 50.0:
        return False

    if assessment.readiness not in {
        MemoryRetrievalReadiness.READY,
        MemoryRetrievalReadiness.CONDITIONAL,
    }:
        return False

    return True


# ------------------------------------------------------------
# ACCESSORS
# ------------------------------------------------------------

def get_memory_retrieval_status(
    result: MemoryRetrievalResult,
) -> MemoryRetrievalResultStatus:
    return result.status


def get_memory_retrieval_readiness(
    result: MemoryRetrievalResult,
) -> MemoryRetrievalReadiness:

    if result.assessment is None:
        return MemoryRetrievalReadiness.UNKNOWN

    return result.assessment.readiness


def get_memory_retrieval_data_state(
    result: MemoryRetrievalResult,
) -> MemoryRetrievalDataState:

    if result.assessment is None:
        return MemoryRetrievalDataState.UNKNOWN

    return result.assessment.data_state


def get_memory_retrieval_match_quality(
    result: MemoryRetrievalResult,
) -> MemoryRetrievalMatchQuality:

    if result.assessment is None:
        return MemoryRetrievalMatchQuality.UNKNOWN

    return result.assessment.match_quality


def get_memory_retrieval_consistency(
    result: MemoryRetrievalResult,
) -> MemoryRetrievalConsistency:

    if result.assessment is None:
        return MemoryRetrievalConsistency.UNKNOWN

    return result.assessment.consistency


def get_memory_retrieval_confidence(
    result: MemoryRetrievalResult,
) -> float:

    if result.assessment is None:
        return 0.0

    return float(result.assessment.confidence_score)


def get_memory_retrieval_completeness(
    result: MemoryRetrievalResult,
) -> float:

    if result.assessment is None:
        return 0.0

    return float(result.assessment.completeness_score)


def get_memory_retrieval_match_score(
    result: MemoryRetrievalResult,
) -> float:

    if result.assessment is None:
        return 0.0

    return float(result.assessment.match_score)


def get_memory_retrieval_references(
    result: MemoryRetrievalResult,
) -> tuple[MemoryRetrievalReference, ...]:
    return tuple(result.references)


def get_primary_memory_reference(
    result: MemoryRetrievalResult,
) -> Optional[MemoryRetrievalReference]:

    if result.reference is not None:
        return result.reference

    if result.references:
        return result.references[0]

    return None


def get_memory_retrieval_count(
    result: MemoryRetrievalResult,
) -> int:
    return int(result.returned_count)


# ------------------------------------------------------------
# IDENTITY ACCESSORS
# ------------------------------------------------------------

def get_retrieved_memory_id(
    result: MemoryRetrievalResult,
) -> Optional[str]:

    reference = get_primary_memory_reference(result)

    if reference is None:
        return None

    return reference.memory_id


def get_retrieved_decision_id(
    result: MemoryRetrievalResult,
) -> Optional[str]:

    reference = get_primary_memory_reference(result)

    if reference is None:
        return None

    return reference.decision_id


def get_retrieved_outcome_id(
    result: MemoryRetrievalResult,
) -> Optional[str]:

    reference = get_primary_memory_reference(result)

    if reference is None:
        return None

    return reference.outcome_id


def get_retrieved_execution_id(
    result: MemoryRetrievalResult,
) -> Optional[str]:

    reference = get_primary_memory_reference(result)

    if reference is None:
        return None

    return reference.execution_id


def get_retrieved_position_id(
    result: MemoryRetrievalResult,
) -> Optional[str]:

    reference = get_primary_memory_reference(result)

    if reference is None:
        return None

    return reference.position_id


def get_retrieved_direction(
    result: MemoryRetrievalResult,
) -> Optional[str]:

    reference = get_primary_memory_reference(result)

    if reference is None:
        return None

    return reference.direction


# ------------------------------------------------------------
# AUDIT
# ------------------------------------------------------------

def audit_memory_retrieval(
    result: MemoryRetrievalResult,
) -> Mapping[str, Any]:

    assessment = result.assessment

    return {
        "engine": MEMORY_RETRIEVAL_ENGINE,
        "version": MEMORY_RETRIEVAL_VERSION,
        "result_id": result.result_id,
        "request_id": result.request_id,
        "status": result.status.value,
        "matched_count": result.matched_count,
        "returned_count": result.returned_count,
        "validation": validate_memory_retrieval_result(result),
        "ready": memory_retrieval_ready(result),
        "can_advance": memory_retrieval_can_advance(result),
        "readiness": (
            assessment.readiness.value
            if assessment else
            MemoryRetrievalReadiness.UNKNOWN.value
        ),
        "data_state": (
            assessment.data_state.value
            if assessment else
            MemoryRetrievalDataState.UNKNOWN.value
        ),
        "match_quality": (
            assessment.match_quality.value
            if assessment else
            MemoryRetrievalMatchQuality.UNKNOWN.value
        ),
        "consistency": (
            assessment.consistency.value
            if assessment else
            MemoryRetrievalConsistency.UNKNOWN.value
        ),
        "confidence_score": (
            assessment.confidence_score
            if assessment else 0.0
        ),
        "completeness_score": (
            assessment.completeness_score
            if assessment else 0.0
        ),
        "match_score": (
            assessment.match_score
            if assessment else 0.0
        ),
        "authority": {
            "decision_generation": False,
            "decision_override": False,
            "risk_override": False,
            "cas_override": False,
            "execution_authorization": False,
            "order_execution": False,
        },
    }


# ------------------------------------------------------------
# SAFETY BOUNDARY
# ------------------------------------------------------------

def memory_retrieval_is_safe(
    result: MemoryRetrievalResult,
) -> bool:

    if not validate_memory_retrieval_result(result):
        return False

    if result.status in {
        MemoryRetrievalResultStatus.INVALID,
        MemoryRetrievalResultStatus.INVALIDATED,
    }:
        return False

    if result.assessment is None:
        return False

    if result.assessment.consistency == (
        MemoryRetrievalConsistency.CONFLICTING
    ):
        return False

    return True


def memory_retrieval_has_conflict(
    result: MemoryRetrievalResult,
) -> bool:

    if result.assessment is None:
        return True

    return (
        result.assessment.consistency
        == MemoryRetrievalConsistency.CONFLICTING
    )


def memory_retrieval_requires_review(
    result: MemoryRetrievalResult,
) -> bool:

    if result.assessment is None:
        return True

    return (
        result.status
        in {
            MemoryRetrievalResultStatus.REVIEW,
            MemoryRetrievalResultStatus.PARTIAL,
        }
        or result.assessment.readiness
        == MemoryRetrievalReadiness.CONDITIONAL
    )


# ------------------------------------------------------------
# AUTHORITY BOUNDARIES
# ------------------------------------------------------------

def memory_retrieval_generates_decision() -> bool:
    return False


def memory_retrieval_modifies_d13() -> bool:
    return False


def memory_retrieval_overrides_d13() -> bool:
    return False


def memory_retrieval_overrides_risk() -> bool:
    return False


def memory_retrieval_overrides_cas() -> bool:
    return False


def memory_retrieval_authorizes_execution() -> bool:
    return False


def memory_retrieval_allows_order() -> bool:
    return False


def memory_retrieval_allows_trade() -> bool:
    return False


def memory_retrieval_allows_position_change() -> bool:
    return False


def memory_retrieval_is_execution_authority() -> bool:
    return False


# ------------------------------------------------------------
# ENGINE INFORMATION
# ------------------------------------------------------------

def get_memory_retrieval_engine_info() -> Mapping[str, Any]:
    return {
        "engine": MEMORY_RETRIEVAL_ENGINE,
        "version": MEMORY_RETRIEVAL_VERSION,
        "purpose": (
            "Retrieve, match, validate and assess historical "
            "market intelligence memory."
        ),
        "decision_authority": False,
        "risk_authority": False,
        "cas_authority": False,
        "execution_authority": False,
    }


def memory_retrieval_health_check() -> Mapping[str, Any]:
    engine = get_memory_retrieval_engine()

    return {
        "healthy": (
            engine is not None
            and engine.engine_name == MEMORY_RETRIEVAL_ENGINE
            and engine.version == MEMORY_RETRIEVAL_VERSION
        ),
        "engine": engine.engine_name,
        "version": engine.version,
        "singleton": (
            engine is get_memory_retrieval_engine()
        ),
    }
# ============================================================
# PART 5 — LIFECYCLE / SERIALIZATION / INTEGRITY / EXPORTS
# ============================================================

def memory_retrieval_is_found(
    result: MemoryRetrievalResult,
) -> bool:
    return (
        validate_memory_retrieval_result(result)
        and result.status == MemoryRetrievalResultStatus.FOUND
    )


def memory_retrieval_is_partial(
    result: MemoryRetrievalResult,
) -> bool:
    return (
        validate_memory_retrieval_result(result)
        and result.status == MemoryRetrievalResultStatus.PARTIAL
    )


def memory_retrieval_is_empty(
    result: MemoryRetrievalResult,
) -> bool:
    return (
        result.status == MemoryRetrievalResultStatus.EMPTY
    )


def memory_retrieval_is_invalid(
    result: MemoryRetrievalResult,
) -> bool:
    return (
        result.status
        in {
            MemoryRetrievalResultStatus.INVALID,
            MemoryRetrievalResultStatus.INVALIDATED,
        }
    )


def memory_retrieval_is_completed(
    result: MemoryRetrievalResult,
) -> bool:
    return (
        result.status == MemoryRetrievalResultStatus.COMPLETED
    )


def memory_retrieval_lifecycle_state(
    result: MemoryRetrievalResult,
) -> str:

    if memory_retrieval_is_invalid(result):
        return "INVALIDATED"

    if memory_retrieval_is_found(result):
        return "FOUND"

    if memory_retrieval_is_partial(result):
        return "PARTIAL"

    if memory_retrieval_is_empty(result):
        return "EMPTY"

    if memory_retrieval_requires_review(result):
        return "REVIEW"

    if memory_retrieval_can_advance(result):
        return "ADVANCE"

    return "HOLD"


# ------------------------------------------------------------
# SERIALIZATION
# ------------------------------------------------------------

def _mr_iso(value: Any) -> Optional[str]:
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.isoformat()

    return str(value)


def serialize_memory_retrieval_reference(
    reference: MemoryRetrievalReference,
) -> Mapping[str, Any]:

    return {
        "memory_id": reference.memory_id,
        "market_name": reference.market_name,
        "symbol": reference.symbol,
        "retrieval_type": reference.retrieval_type.value,
        "source_type": reference.source_type.value,
        "status": reference.status.value,
        "priority": reference.priority.value,
        "timestamp": _mr_iso(reference.timestamp),
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
        "payload": dict(reference.payload),
    }


def serialize_memory_retrieval_result(
    result: MemoryRetrievalResult,
) -> Mapping[str, Any]:

    assessment = result.assessment

    return {
        "result_id": result.result_id,
        "request_id": result.request_id,
        "status": result.status.value,
        "matched_count": result.matched_count,
        "returned_count": result.returned_count,
        "timestamp": _mr_iso(result.timestamp),
        "reference": (
            serialize_memory_retrieval_reference(result.reference)
            if result.reference is not None
            else None
        ),
        "references": [
            serialize_memory_retrieval_reference(ref)
            for ref in result.references
        ],
        "assessment": (
            {
                "readiness": assessment.readiness.value,
                "data_state": assessment.data_state.value,
                "match_quality": assessment.match_quality.value,
                "consistency": assessment.consistency.value,
                "confidence_score": assessment.confidence_score,
                "completeness_score": assessment.completeness_score,
                "match_score": assessment.match_score,
                "matched_fields": list(
                    assessment.matched_fields
                ),
                "unmatched_fields": list(
                    assessment.unmatched_fields
                ),
                "strengths": list(assessment.strengths),
                "weaknesses": list(assessment.weaknesses),
                "rationale": assessment.rationale,
            }
            if assessment is not None
            else None
        ),
        "action": (
            {
                "state": result.action.state.value,
                "action_id": result.action.action_id,
                "reason": result.action.reason,
                "is_action_request": result.action.is_action_request,
            }
            if result.action is not None
            else None
        ),
        "warnings": list(result.warnings),
        "errors": list(result.errors),
    }


def serialize_memory_retrieval_contract(
    contract: MemoryRetrievalContract,
) -> Mapping[str, Any]:

    return {
        "contract_id": contract.contract_id,
        "request_id": contract.request_id,
        "result_id": contract.result_id,
        "state": contract.state.value,
        "valid": contract.valid,
        "request_valid": contract.request_valid,
        "assessment_available": contract.assessment_available,
        "result_available": contract.result_available,
        "references_available": contract.references_available,
        "errors": list(contract.errors),
        "warnings": list(contract.warnings),
    }


# ------------------------------------------------------------
# INTEGRITY
# ------------------------------------------------------------

def check_memory_retrieval_integrity(
    result: MemoryRetrievalResult,
) -> Mapping[str, Any]:

    validation_ok = validate_memory_retrieval_result(result)

    assessment_ok = (
        result.assessment is not None
    )

    references_ok = (
        result.returned_count
        == len(result.references)
    )

    count_ok = (
        result.returned_count
        <= result.matched_count
    )

    conflict_ok = not memory_retrieval_has_conflict(result)

    return {
        "valid": (
            validation_ok
            and assessment_ok
            and references_ok
            and count_ok
        ),
        "validation": validation_ok,
        "assessment": assessment_ok,
        "references": references_ok,
        "counts": count_ok,
        "conflict_free": conflict_ok,
        "ready": memory_retrieval_ready(result),
        "can_advance": memory_retrieval_can_advance(result),
    }


# ------------------------------------------------------------
# SUMMARY
# ------------------------------------------------------------

def summarize_memory_retrieval(
    result: MemoryRetrievalResult,
) -> Mapping[str, Any]:

    assessment = result.assessment

    return {
        "engine": MEMORY_RETRIEVAL_ENGINE,
        "version": MEMORY_RETRIEVAL_VERSION,
        "result_id": result.result_id,
        "status": result.status.value,
        "lifecycle": memory_retrieval_lifecycle_state(result),
        "matched_count": result.matched_count,
        "returned_count": result.returned_count,
        "readiness": (
            assessment.readiness.value
            if assessment
            else MemoryRetrievalReadiness.UNKNOWN.value
        ),
        "match_quality": (
            assessment.match_quality.value
            if assessment
            else MemoryRetrievalMatchQuality.UNKNOWN.value
        ),
        "confidence": (
            assessment.confidence_score
            if assessment
            else 0.0
        ),
        "completeness": (
            assessment.completeness_score
            if assessment
            else 0.0
        ),
        "match_score": (
            assessment.match_score
            if assessment
            else 0.0
        ),
        "ready": memory_retrieval_ready(result),
        "can_advance": memory_retrieval_can_advance(result),
        "safe": memory_retrieval_is_safe(result),
        "requires_review": memory_retrieval_requires_review(result),
    }


# ------------------------------------------------------------
# RETENTION / FREEZE / REJECT
# ------------------------------------------------------------

def freeze_memory_retrieval(
    result: MemoryRetrievalResult,
) -> MemoryRetrievalResult:

    if memory_retrieval_is_invalid(result):
        return result

    return MemoryRetrievalResult(
        status=MemoryRetrievalResultStatus.COMPLETED,
        result_id=result.result_id,
        request_id=result.request_id,
        reference=result.reference,
        assessment=result.assessment,
        action=MemoryRetrievalAction(
            state=MemoryRetrievalActionState.COMPLETE,
            reason="Retrieval result lifecycle frozen.",
        ),
        matched_count=result.matched_count,
        returned_count=result.returned_count,
        references=tuple(result.references),
        warnings=tuple(result.warnings),
        errors=tuple(result.errors),
        timestamp=result.timestamp,
    )


def retain_memory_retrieval(
    result: MemoryRetrievalResult,
) -> MemoryRetrievalResult:

    if not memory_retrieval_is_safe(result):
        return result

    return result


def reject_memory_retrieval(
    result: MemoryRetrievalResult,
    reason: str = "Retrieval rejected.",
) -> MemoryRetrievalResult:

    return MemoryRetrievalResult(
        status=MemoryRetrievalResultStatus.INVALIDATED,
        result_id=result.result_id,
        request_id=result.request_id,
        reference=result.reference,
        assessment=result.assessment,
        action=MemoryRetrievalAction(
            state=MemoryRetrievalActionState.INVALIDATE,
            reason=reason,
        ),
        matched_count=result.matched_count,
        returned_count=result.returned_count,
        references=tuple(result.references),
        warnings=tuple(result.warnings),
        errors=tuple(result.errors) + (reason,),
        timestamp=result.timestamp,
    )


# ------------------------------------------------------------
# AUTHORITY STATEMENT
# ------------------------------------------------------------

def memory_retrieval_authority_statement() -> str:
    return (
        "Memory Retrieval preserves, retrieves, matches and assesses "
        "historical memory records. It does not generate, modify, "
        "override, authorize or execute trading decisions. D13 remains "
        "the decision authority; Risk remains the risk authority; CAS "
        "remains the authorization and execution-safety authority."
    )


# ------------------------------------------------------------
# PUBLIC EXPORTS
# ------------------------------------------------------------

__all__ = [
    # constants
    "MEMORY_RETRIEVAL_ENGINE",
    "MEMORY_RETRIEVAL_VERSION",

    # enums
    "MemoryRetrievalStatus",
    "MemoryRetrievalType",
    "MemoryRetrievalPriority",
    "MemoryRetrievalSourceType",
    "MemoryRetrievalContractStatus",
    "MemoryRetrievalDataState",
    "MemoryRetrievalMatchQuality",
    "MemoryRetrievalConsistency",
    "MemoryRetrievalReadiness",
    "MemoryRetrievalActionState",
    "MemoryRetrievalContractState",
    "MemoryRetrievalResultStatus",

    # request/reference/contracts
    "MemoryRetrievalRequest",
    "MemoryRetrievalReference",
    "MemoryRetrievalSourceReference",
    "MemoryRetrievalContractValidation",
    "MemoryRetrievalRequirements",
    "MemoryRetrievalAssessment",
    "MemoryRetrievalAction",
    "MemoryRetrievalResult",
    "MemoryRetrievalContract",

    # builders / validation
    "build_memory_retrieval_reference",
    "validate_memory_retrieval_request",
    "determine_memory_retrieval_result_status",
    "build_memory_retrieval_action",
    "build_memory_retrieval_result",
    "build_memory_retrieval_contract",

    # evaluation
    "evaluate_memory_retrieval",
    "search_memory",
    "retrieve_memory",
    "review_memory_retrieval",

    # engine
    "MemoryRetrievalEngine",
    "get_memory_retrieval_engine",

    # validation / gates
    "validate_memory_retrieval_result",
    "validate_memory_retrieval_contract",
    "memory_retrieval_ready",
    "memory_retrieval_can_advance",

    # accessors
    "get_memory_retrieval_status",
    "get_memory_retrieval_readiness",
    "get_memory_retrieval_data_state",
    "get_memory_retrieval_match_quality",
    "get_memory_retrieval_consistency",
    "get_memory_retrieval_confidence",
    "get_memory_retrieval_completeness",
    "get_memory_retrieval_match_score",
    "get_memory_retrieval_references",
    "get_primary_memory_reference",
    "get_memory_retrieval_count",
    "get_retrieved_memory_id",
    "get_retrieved_decision_id",
    "get_retrieved_outcome_id",
    "get_retrieved_execution_id",
    "get_retrieved_position_id",
    "get_retrieved_direction",

    # audit / safety
    "audit_memory_retrieval",
    "memory_retrieval_is_safe",
    "memory_retrieval_has_conflict",
    "memory_retrieval_requires_review",

    # authority boundaries
    "memory_retrieval_generates_decision",
    "memory_retrieval_modifies_d13",
    "memory_retrieval_overrides_d13",
    "memory_retrieval_overrides_risk",
    "memory_retrieval_overrides_cas",
    "memory_retrieval_authorizes_execution",
    "memory_retrieval_allows_order",
    "memory_retrieval_allows_trade",
    "memory_retrieval_allows_position_change",
    "memory_retrieval_is_execution_authority",

    # engine info
    "get_memory_retrieval_engine_info",
    "memory_retrieval_health_check",

    # lifecycle
    "memory_retrieval_is_found",
    "memory_retrieval_is_partial",
    "memory_retrieval_is_empty",
    "memory_retrieval_is_invalid",
    "memory_retrieval_is_completed",
    "memory_retrieval_lifecycle_state",

    # serialization / integrity
    "serialize_memory_retrieval_reference",
    "serialize_memory_retrieval_result",
    "serialize_memory_retrieval_contract",
    "check_memory_retrieval_integrity",
    "summarize_memory_retrieval",

    # retention
    "freeze_memory_retrieval",
    "retain_memory_retrieval",
    "reject_memory_retrieval",

    # authority
    "memory_retrieval_authority_statement",
]