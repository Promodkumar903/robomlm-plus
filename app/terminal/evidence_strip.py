# ============================================================
# ROBOMLM_PLUS
# app/terminal/evidence_strip.py
# PART 1 / 5
# Evidence Strip Contract + Authority Boundary
# ============================================================

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


EVIDENCE_STRIP_ENGINE = "ROBOMLM_TERMINAL_EVIDENCE_STRIP"
EVIDENCE_STRIP_VERSION = "1.0"


# ------------------------------------------------------------
# ENUMS
# ------------------------------------------------------------

class EvidenceStripStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    READY = "READY"
    PARTIAL = "PARTIAL"
    STALE = "STALE"
    INVALID = "INVALID"
    ERROR = "ERROR"


class EvidenceStripMode(str, Enum):
    PAPER = "PAPER"
    DEMO = "DEMO"
    LIVE = "LIVE"
    UNKNOWN = "UNKNOWN"


class EvidenceStripPriority(str, Enum):
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EvidenceStripSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EvidenceStripSourceType(str, Enum):
    MARKET_DATA = "MARKET_DATA"
    EVIDENCE_ENGINE = "EVIDENCE_ENGINE"
    DERIVATIVE_ENGINE = "DERIVATIVE_ENGINE"
    MICROSTRUCTURE_ENGINE = "MICROSTRUCTURE_ENGINE"
    MEMORY_ENGINE = "MEMORY_ENGINE"
    EXTERNAL = "EXTERNAL"
    UNKNOWN = "UNKNOWN"


class EvidenceStripContractStatus(str, Enum):
    CREATED = "CREATED"
    VALID = "VALID"
    INVALID = "INVALID"
    READY = "READY"


# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------

def _es_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def _es_enum(value: Any, enum_cls: Any, default: Any) -> Any:
    if isinstance(value, enum_cls):
        return value
    try:
        return enum_cls(str(value).strip().upper())
    except (ValueError, TypeError):
        return default


def _es_number(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
        if number != number:
            return default
        return number
    except (TypeError, ValueError):
        return default


def _es_timestamp(value: Any = None) -> datetime:
    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            pass

    return datetime.utcnow()


# ------------------------------------------------------------
# REQUEST CONTRACT
# ------------------------------------------------------------

@dataclass
class EvidenceStripRequest:
    market: str = ""
    instrument: str = ""
    symbol: str = ""
    contract: str = ""
    timeframe: str = ""
    session: str = ""
    market_phase: str = ""

    mode: EvidenceStripMode = EvidenceStripMode.UNKNOWN
    priority: EvidenceStripPriority = EvidenceStripPriority.NORMAL

    requested_categories: List[str] = field(default_factory=list)
    requested_sources: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    request_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)


# ------------------------------------------------------------
# EVIDENCE ITEM
# ------------------------------------------------------------

@dataclass
class EvidenceStripItem:
    evidence_id: str = ""

    category: str = ""
    name: str = ""
    value: Any = None
    unit: str = ""

    source: str = ""
    source_type: EvidenceStripSourceType = (
        EvidenceStripSourceType.UNKNOWN
    )

    status: EvidenceStripStatus = EvidenceStripStatus.UNKNOWN
    severity: EvidenceStripSeverity = EvidenceStripSeverity.INFO

    confidence: float = 0.0
    freshness_seconds: Optional[float] = None

    timestamp: datetime = field(default_factory=datetime.utcnow)

    metadata: Dict[str, Any] = field(default_factory=dict)


# ------------------------------------------------------------
# EVIDENCE STRIP REFERENCE
# ------------------------------------------------------------

@dataclass
class EvidenceStripReference:
    market: str = ""
    instrument: str = ""
    symbol: str = ""
    contract: str = ""
    timeframe: str = ""
    session: str = ""
    market_phase: str = ""

    status: EvidenceStripStatus = EvidenceStripStatus.UNKNOWN
    mode: EvidenceStripMode = EvidenceStripMode.UNKNOWN

    source: str = ""
    evidence_count: int = 0

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    version: str = EVIDENCE_STRIP_VERSION


# ------------------------------------------------------------
# CONTRACT VALIDATION
# ------------------------------------------------------------

@dataclass
class EvidenceStripContractValidation:
    status: EvidenceStripContractStatus = (
        EvidenceStripContractStatus.CREATED
    )

    valid: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    checked_at: datetime = field(default_factory=datetime.utcnow)


# ------------------------------------------------------------
# AUTHORITY BOUNDARY
# ------------------------------------------------------------

def evidence_strip_authority_boundary() -> Dict[str, bool]:
    """
    Evidence Strip is a presentation/aggregation surface.

    It may organize and expose upstream evidence.
    It must not become an intelligence or decision authority.
    """
    return {
        "presentation_authority": True,
        "evidence_display_authority": True,

        # Upstream authority remains external.
        "market_data_authority": False,
        "evidence_generation_authority": False,
        "market_intelligence_authority": False,
        "market_context_authority": False,
        "decision_authority": False,
        "d13_authority": False,
        "risk_authority": False,
        "cas_authority": False,
        "execution_authority": False,
        "order_authority": False,
        "position_authority": False,

        # No mutation of upstream intelligence.
        "upstream_mutation_authority": False,
    }


def validate_evidence_strip_authority_boundary() -> bool:
    boundary = evidence_strip_authority_boundary()

    required_true = (
        "presentation_authority",
        "evidence_display_authority",
    )

    required_false = (
        "market_data_authority",
        "evidence_generation_authority",
        "market_intelligence_authority",
        "market_context_authority",
        "decision_authority",
        "d13_authority",
        "risk_authority",
        "cas_authority",
        "execution_authority",
        "order_authority",
        "position_authority",
        "upstream_mutation_authority",
    )

    return (
        all(boundary.get(key) is True for key in required_true)
        and all(boundary.get(key) is False for key in required_false)
    )


# ------------------------------------------------------------
# NORMALIZATION
# ------------------------------------------------------------

def normalize_evidence_strip_request(
    request: EvidenceStripRequest,
) -> EvidenceStripRequest:
    return EvidenceStripRequest(
        market=_es_text(request.market),
        instrument=_es_text(request.instrument),
        symbol=_es_text(request.symbol),
        contract=_es_text(request.contract),
        timeframe=_es_text(request.timeframe),
        session=_es_text(request.session),
        market_phase=_es_text(request.market_phase),

        mode=_es_enum(
            request.mode,
            EvidenceStripMode,
            EvidenceStripMode.UNKNOWN,
        ),

        priority=_es_enum(
            request.priority,
            EvidenceStripPriority,
            EvidenceStripPriority.NORMAL,
        ),

        requested_categories=[
            _es_text(x)
            for x in (request.requested_categories or [])
            if _es_text(x)
        ],

        requested_sources=[
            _es_text(x)
            for x in (request.requested_sources or [])
            if _es_text(x)
        ],

        metadata=dict(request.metadata or {}),
        request_id=_es_text(request.request_id),
        timestamp=_es_timestamp(request.timestamp),
    )


# ------------------------------------------------------------
# REQUEST VALIDATION
# ------------------------------------------------------------

def validate_evidence_strip_request(
    request: EvidenceStripRequest,
) -> EvidenceStripContractValidation:
    errors: List[str] = []
    warnings: List[str] = []

    if not _es_text(request.market):
        errors.append("market_missing")

    if not _es_text(request.instrument):
        errors.append("instrument_missing")

    if not _es_text(request.symbol):
        errors.append("symbol_missing")

    if request.mode == EvidenceStripMode.UNKNOWN:
        warnings.append("mode_unknown")

    if not request.request_id:
        warnings.append("request_id_missing")

    valid = len(errors) == 0

    return EvidenceStripContractValidation(
        status=(
            EvidenceStripContractStatus.VALID
            if valid
            else EvidenceStripContractStatus.INVALID
        ),
        valid=valid,
        errors=errors,
        warnings=warnings,
        checked_at=datetime.utcnow(),
    )


# ------------------------------------------------------------
# REQUEST BUILDER
# ------------------------------------------------------------

def build_evidence_strip_request(
    market: str,
    instrument: str,
    symbol: str,
    contract: str = "",
    timeframe: str = "",
    session: str = "",
    market_phase: str = "",
    mode: Any = EvidenceStripMode.UNKNOWN,
    priority: Any = EvidenceStripPriority.NORMAL,
    requested_categories: Optional[List[str]] = None,
    requested_sources: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    request_id: str = "",
) -> EvidenceStripRequest:

    request = EvidenceStripRequest(
        market=market,
        instrument=instrument,
        symbol=symbol,
        contract=contract,
        timeframe=timeframe,
        session=session,
        market_phase=market_phase,
        mode=_es_enum(
            mode,
            EvidenceStripMode,
            EvidenceStripMode.UNKNOWN,
        ),
        priority=_es_enum(
            priority,
            EvidenceStripPriority,
            EvidenceStripPriority.NORMAL,
        ),
        requested_categories=list(requested_categories or []),
        requested_sources=list(requested_sources or []),
        metadata=dict(metadata or {}),
        request_id=request_id,
        timestamp=datetime.utcnow(),
    )

    return normalize_evidence_strip_request(request)


# ------------------------------------------------------------
# REFERENCE BUILDER
# ------------------------------------------------------------

def build_evidence_strip_reference(
    request: EvidenceStripRequest,
    evidence_count: int = 0,
    status: Any = EvidenceStripStatus.UNKNOWN,
    source: str = "",
) -> EvidenceStripReference:

    return EvidenceStripReference(
        market=_es_text(request.market),
        instrument=_es_text(request.instrument),
        symbol=_es_text(request.symbol),
        contract=_es_text(request.contract),
        timeframe=_es_text(request.timeframe),
        session=_es_text(request.session),
        market_phase=_es_text(request.market_phase),

        status=_es_enum(
            status,
            EvidenceStripStatus,
            EvidenceStripStatus.UNKNOWN,
        ),

        mode=_es_enum(
            request.mode,
            EvidenceStripMode,
            EvidenceStripMode.UNKNOWN,
        ),

        source=_es_text(source),
        evidence_count=max(0, int(evidence_count)),

        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        version=EVIDENCE_STRIP_VERSION,
    )
# ============================================================
# PART 2 / 5
# Evidence State + Quality + Assessment
# ============================================================

class EvidenceStripDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    INVALID = "INVALID"


class EvidenceStripConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONDITIONAL = "CONDITIONAL"
    INCONSISTENT = "INCONSISTENT"
    UNKNOWN = "UNKNOWN"


class EvidenceStripReadiness(str, Enum):
    READY = "READY"
    CONDITIONALLY_READY = "CONDITIONALLY_READY"
    NOT_READY = "NOT_READY"
    BLOCKED = "BLOCKED"


@dataclass
class EvidenceStripRequirements:
    require_market: bool = True
    require_instrument: bool = True
    require_symbol: bool = True

    minimum_evidence_count: int = 1
    minimum_quality: float = 50.0
    ready_quality: float = 80.0

    allow_partial: bool = True
    allow_stale: bool = True
    allow_unknown_source: bool = True


@dataclass
class EvidenceStripAssessment:
    data_state: EvidenceStripDataState = (
        EvidenceStripDataState.MISSING
    )

    consistency: EvidenceStripConsistency = (
        EvidenceStripConsistency.UNKNOWN
    )

    readiness: EvidenceStripReadiness = (
        EvidenceStripReadiness.NOT_READY
    )

    completeness: float = 0.0
    quality: float = 0.0
    confidence: float = 0.0

    evidence_count: int = 0
    fresh_evidence_count: int = 0
    stale_evidence_count: int = 0
    invalid_evidence_count: int = 0

    flags: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    unmet_requirements: List[str] = field(default_factory=list)

    market: str = ""
    instrument: str = ""
    symbol: str = ""
    status: EvidenceStripStatus = EvidenceStripStatus.UNKNOWN
    mode: EvidenceStripMode = EvidenceStripMode.UNKNOWN
    source: str = ""

    timestamp: datetime = field(default_factory=datetime.utcnow)


def build_evidence_strip_requirements(
    minimum_evidence_count: int = 1,
    minimum_quality: float = 50.0,
    ready_quality: float = 80.0,
) -> EvidenceStripRequirements:
    return EvidenceStripRequirements(
        minimum_evidence_count=max(0, int(minimum_evidence_count)),
        minimum_quality=max(0.0, min(100.0, float(minimum_quality))),
        ready_quality=max(0.0, min(100.0, float(ready_quality))),
    )


def evaluate_evidence_strip_data_state(
    items: List[EvidenceStripItem],
) -> EvidenceStripDataState:
    items = list(items or [])

    if not items:
        return EvidenceStripDataState.MISSING

    invalid = 0

    for item in items:
        if not _es_text(item.evidence_id):
            invalid += 1
        if not _es_text(item.category):
            invalid += 1
        if item.status == EvidenceStripStatus.INVALID:
            invalid += 1

    if invalid == len(items):
        return EvidenceStripDataState.INVALID

    if invalid > 0:
        return EvidenceStripDataState.PARTIAL

    return EvidenceStripDataState.COMPLETE


def evaluate_evidence_strip_consistency(
    items: List[EvidenceStripItem],
) -> EvidenceStripConsistency:
    items = list(items or [])

    if not items:
        return EvidenceStripConsistency.UNKNOWN

    symbols = {
        _es_text(item.metadata.get("symbol"))
        for item in items
        if _es_text(item.metadata.get("symbol"))
    }

    timestamps = [
        item.timestamp
        for item in items
        if isinstance(item.timestamp, datetime)
    ]

    if len(symbols) > 1:
        return EvidenceStripConsistency.INCONSISTENT

    if len(timestamps) >= 2:
        oldest = min(timestamps)
        newest = max(timestamps)

        if (newest - oldest).total_seconds() > 3600:
            return EvidenceStripConsistency.CONDITIONAL

    for item in items:
        if item.status == EvidenceStripStatus.INVALID:
            return EvidenceStripConsistency.INCONSISTENT

    return EvidenceStripConsistency.CONSISTENT


def evaluate_evidence_strip_requirements(
    request: EvidenceStripRequest,
    items: List[EvidenceStripItem],
    requirements: Optional[EvidenceStripRequirements] = None,
) -> List[str]:
    requirements = (
        requirements
        if requirements is not None
        else EvidenceStripRequirements()
    )

    unmet: List[str] = []

    if requirements.require_market and not _es_text(request.market):
        unmet.append("market_missing")

    if (
        requirements.require_instrument
        and not _es_text(request.instrument)
    ):
        unmet.append("instrument_missing")

    if requirements.require_symbol and not _es_text(request.symbol):
        unmet.append("symbol_missing")

    if len(items or []) < requirements.minimum_evidence_count:
        unmet.append("minimum_evidence_missing")

    return unmet


def evaluate_evidence_strip_freshness(
    items: List[EvidenceStripItem],
    stale_after_seconds: float = 300.0,
    now: Optional[datetime] = None,
) -> Dict[str, int]:
    now = now or datetime.utcnow()

    fresh = 0
    stale = 0
    invalid = 0

    for item in list(items or []):
        if item.status == EvidenceStripStatus.INVALID:
            invalid += 1
            continue

        if not isinstance(item.timestamp, datetime):
            stale += 1
            continue

        age = max(
            0.0,
            (now - item.timestamp).total_seconds(),
        )

        if age <= max(0.0, float(stale_after_seconds)):
            fresh += 1
        else:
            stale += 1

    return {
        "fresh": fresh,
        "stale": stale,
        "invalid": invalid,
    }


def evaluate_evidence_strip_completeness(
    items: List[EvidenceStripItem],
    requirements: Optional[EvidenceStripRequirements] = None,
) -> float:
    requirements = (
        requirements
        if requirements is not None
        else EvidenceStripRequirements()
    )

    items = list(items or [])

    if not items:
        return 0.0

    valid_count = sum(
        1
        for item in items
        if item.status != EvidenceStripStatus.INVALID
    )

    count_score = min(
        100.0,
        (
            valid_count
            / max(1, requirements.minimum_evidence_count)
        ) * 100.0,
    )

    field_score = sum(
        bool(
            _es_text(item.evidence_id)
            and _es_text(item.category)
            and _es_text(item.source)
        )
        for item in items
    ) / max(1, len(items)) * 100.0

    return round(
        (count_score * 0.5) + (field_score * 0.5),
        2,
    )


def evaluate_evidence_strip_quality(
    items: List[EvidenceStripItem],
    freshness: Optional[Dict[str, int]] = None,
) -> float:
    items = list(items or [])

    if not items:
        return 0.0

    freshness = freshness or evaluate_evidence_strip_freshness(items)

    valid_items = [
        item
        for item in items
        if item.status != EvidenceStripStatus.INVALID
    ]

    if not valid_items:
        return 0.0

    confidence_score = sum(
        max(0.0, min(100.0, float(item.confidence)))
        for item in valid_items
    ) / len(valid_items)

    fresh_count = freshness.get("fresh", 0)
    total = len(valid_items)

    freshness_score = (
        fresh_count / max(1, total)
    ) * 100.0

    source_score = sum(
        1
        for item in valid_items
        if _es_text(item.source)
        and item.source_type != EvidenceStripSourceType.UNKNOWN
    ) / max(1, total) * 100.0

    quality = (
        confidence_score * 0.50
        + freshness_score * 0.30
        + source_score * 0.20
    )

    return round(max(0.0, min(100.0, quality)), 2)


def evaluate_evidence_strip_confidence(
    items: List[EvidenceStripItem],
) -> float:
    valid_items = [
        item
        for item in list(items or [])
        if item.status != EvidenceStripStatus.INVALID
    ]

    if not valid_items:
        return 0.0

    values = [
        max(0.0, min(100.0, float(item.confidence)))
        for item in valid_items
    ]

    return round(sum(values) / len(values), 2)


def evaluate_evidence_strip_readiness(
    data_state: EvidenceStripDataState,
    consistency: EvidenceStripConsistency,
    quality: float,
    unmet_requirements: List[str],
    requirements: EvidenceStripRequirements,
    freshness: Dict[str, int],
) -> EvidenceStripReadiness:

    if data_state == EvidenceStripDataState.INVALID:
        return EvidenceStripReadiness.BLOCKED

    if consistency == EvidenceStripConsistency.INCONSISTENT:
        return EvidenceStripReadiness.BLOCKED

    if unmet_requirements:
        return EvidenceStripReadiness.NOT_READY

    if quality < requirements.minimum_quality:
        return EvidenceStripReadiness.NOT_READY

    if (
        consistency == EvidenceStripConsistency.CONDITIONAL
        or freshness.get("stale", 0) > 0
    ):
        return EvidenceStripReadiness.CONDITIONALLY_READY

    if quality >= requirements.ready_quality:
        return EvidenceStripReadiness.READY

    return EvidenceStripReadiness.CONDITIONALLY_READY


def build_evidence_strip_assessment(
    request: EvidenceStripRequest,
    items: List[EvidenceStripItem],
    requirements: Optional[EvidenceStripRequirements] = None,
) -> EvidenceStripAssessment:

    request = normalize_evidence_strip_request(request)

    requirements = (
        requirements
        if requirements is not None
        else EvidenceStripRequirements()
    )

    items = list(items or [])

    data_state = evaluate_evidence_strip_data_state(items)

    consistency = evaluate_evidence_strip_consistency(items)

    unmet = evaluate_evidence_strip_requirements(
        request,
        items,
        requirements,
    )

    freshness = evaluate_evidence_strip_freshness(items)

    completeness = evaluate_evidence_strip_completeness(
        items,
        requirements,
    )

    quality = evaluate_evidence_strip_quality(
        items,
        freshness,
    )

    confidence = evaluate_evidence_strip_confidence(items)

    readiness = evaluate_evidence_strip_readiness(
        data_state,
        consistency,
        quality,
        unmet,
        requirements,
        freshness,
    )

    flags: List[str] = []
    warnings: List[str] = []

    if data_state == EvidenceStripDataState.PARTIAL:
        flags.append("PARTIAL_EVIDENCE")

    if data_state == EvidenceStripDataState.MISSING:
        flags.append("EVIDENCE_MISSING")

    if data_state == EvidenceStripDataState.INVALID:
        flags.append("INVALID_EVIDENCE")

    if consistency == EvidenceStripConsistency.CONDITIONAL:
        flags.append("CONDITIONAL_CONSISTENCY")

    if consistency == EvidenceStripConsistency.INCONSISTENT:
        flags.append("INCONSISTENT_EVIDENCE")

    if freshness.get("stale", 0) > 0:
        warnings.append("STALE_EVIDENCE_PRESENT")

    if freshness.get("invalid", 0) > 0:
        warnings.append("INVALID_EVIDENCE_PRESENT")

    return EvidenceStripAssessment(
        data_state=data_state,
        consistency=consistency,
        readiness=readiness,

        completeness=completeness,
        quality=quality,
        confidence=confidence,

        evidence_count=len(items),
        fresh_evidence_count=freshness.get("fresh", 0),
        stale_evidence_count=freshness.get("stale", 0),
        invalid_evidence_count=freshness.get("invalid", 0),

        flags=flags,
        warnings=warnings,
        unmet_requirements=unmet,

        market=request.market,
        instrument=request.instrument,
        symbol=request.symbol,
        status=(
            EvidenceStripStatus.READY
            if readiness == EvidenceStripReadiness.READY
            else EvidenceStripStatus.PARTIAL
        ),
        mode=request.mode,
        source="",
        timestamp=datetime.utcnow(),
    )
# ============================================================
# PART 3 / 5
# Evidence Resolution + Presentation + Result
# ============================================================

class EvidenceStripDecision(str, Enum):
    ALLOW = "ALLOW"
    ALLOW_WITH_RESTRICTION = "ALLOW_WITH_RESTRICTION"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCK = "BLOCK"


class EvidenceStripResolutionStatus(str, Enum):
    RESOLVED = "RESOLVED"
    CONDITIONAL = "CONDITIONAL"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"


@dataclass
class EvidenceStripResolutionRules:
    allow_partial: bool = True
    allow_stale_for_display: bool = True
    allow_conditional: bool = True

    block_invalid: bool = True
    block_inconsistent: bool = True

    minimum_display_quality: float = 50.0
    minimum_ready_quality: float = 80.0


@dataclass
class EvidenceStripPresentation:
    market: str = ""
    instrument: str = ""
    symbol: str = ""
    contract: str = ""
    timeframe: str = ""
    session: str = ""
    market_phase: str = ""

    mode: EvidenceStripMode = EvidenceStripMode.UNKNOWN
    status: EvidenceStripStatus = EvidenceStripStatus.UNKNOWN

    evidence_count: int = 0
    fresh_evidence_count: int = 0
    stale_evidence_count: int = 0

    completeness: float = 0.0
    quality: float = 0.0
    confidence: float = 0.0

    items: List[EvidenceStripItem] = field(default_factory=list)

    flags: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    source: str = ""
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EvidenceStripResult:
    decision: EvidenceStripDecision = EvidenceStripDecision.BLOCK
    status: EvidenceStripResolutionStatus = (
        EvidenceStripResolutionStatus.BLOCKED
    )

    allowed: bool = False
    restricted: bool = False
    review_required: bool = False
    blocked: bool = True

    assessment: Optional[EvidenceStripAssessment] = None
    presentation: Optional[EvidenceStripPresentation] = None

    flags: List[str] = field(default_factory=list)
    restrictions: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    reason: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EvidenceStripSourceMap:
    evidence_strip_engine: str = EVIDENCE_STRIP_ENGINE
    evidence_source: str = "app.intelligence.evidence"
    market_data_source: str = "market_data"
    context_source: str = "app.intelligence.market_context"
    decision_source: str = "app.intelligence.decision"
    risk_source: str = "app.intelligence.risk"
    cas_source: str = "app.cas"

    metadata: Dict[str, Any] = field(default_factory=dict)


def build_evidence_strip_resolution_rules(
    allow_partial: bool = True,
    allow_stale_for_display: bool = True,
    allow_conditional: bool = True,
    block_invalid: bool = True,
    block_inconsistent: bool = True,
    minimum_display_quality: float = 50.0,
    minimum_ready_quality: float = 80.0,
) -> EvidenceStripResolutionRules:
    return EvidenceStripResolutionRules(
        allow_partial=bool(allow_partial),
        allow_stale_for_display=bool(allow_stale_for_display),
        allow_conditional=bool(allow_conditional),
        block_invalid=bool(block_invalid),
        block_inconsistent=bool(block_inconsistent),
        minimum_display_quality=max(
            0.0,
            min(100.0, float(minimum_display_quality)),
        ),
        minimum_ready_quality=max(
            0.0,
            min(100.0, float(minimum_ready_quality)),
        ),
    )


def build_evidence_strip_source_map(
    metadata: Optional[Dict[str, Any]] = None,
) -> EvidenceStripSourceMap:
    return EvidenceStripSourceMap(
        metadata=dict(metadata or {})
    )


def collect_evidence_strip_resolution_flags(
    assessment: EvidenceStripAssessment,
) -> List[str]:
    flags = list(assessment.flags or [])

    if assessment.data_state == EvidenceStripDataState.PARTIAL:
        if "PARTIAL_EVIDENCE" not in flags:
            flags.append("PARTIAL_EVIDENCE")

    if assessment.data_state == EvidenceStripDataState.MISSING:
        if "EVIDENCE_MISSING" not in flags:
            flags.append("EVIDENCE_MISSING")

    if assessment.data_state == EvidenceStripDataState.INVALID:
        if "INVALID_EVIDENCE" not in flags:
            flags.append("INVALID_EVIDENCE")

    if assessment.consistency == EvidenceStripConsistency.INCONSISTENT:
        if "INCONSISTENT_EVIDENCE" not in flags:
            flags.append("INCONSISTENT_EVIDENCE")

    if assessment.stale_evidence_count > 0:
        if "STALE_EVIDENCE_PRESENT" not in flags:
            flags.append("STALE_EVIDENCE_PRESENT")

    return flags


def collect_evidence_strip_restrictions(
    assessment: EvidenceStripAssessment,
) -> List[str]:
    restrictions: List[str] = []

    if assessment.data_state == EvidenceStripDataState.PARTIAL:
        restrictions.append("PARTIAL_EVIDENCE_DISPLAY")

    if assessment.consistency == EvidenceStripConsistency.CONDITIONAL:
        restrictions.append("CONDITIONAL_EVIDENCE_CONTEXT")

    if assessment.stale_evidence_count > 0:
        restrictions.append("STALE_EVIDENCE_DISPLAY")

    if assessment.quality < 80.0:
        restrictions.append("QUALITY_BELOW_READY_THRESHOLD")

    return restrictions


def build_evidence_strip_presentation(
    request: EvidenceStripRequest,
    items: List[EvidenceStripItem],
    assessment: EvidenceStripAssessment,
    source: str = "",
) -> EvidenceStripPresentation:

    return EvidenceStripPresentation(
        market=request.market,
        instrument=request.instrument,
        symbol=request.symbol,
        contract=request.contract,
        timeframe=request.timeframe,
        session=request.session,
        market_phase=request.market_phase,

        mode=request.mode,
        status=assessment.status,

        evidence_count=assessment.evidence_count,
        fresh_evidence_count=assessment.fresh_evidence_count,
        stale_evidence_count=assessment.stale_evidence_count,

        completeness=assessment.completeness,
        quality=assessment.quality,
        confidence=assessment.confidence,

        items=list(items or []),

        flags=list(assessment.flags or []),
        warnings=list(assessment.warnings or []),

        source=_es_text(source),
        updated_at=datetime.utcnow(),
    )


def resolve_evidence_strip(
    request: EvidenceStripRequest,
    items: Optional[List[EvidenceStripItem]] = None,
    requirements: Optional[EvidenceStripRequirements] = None,
    rules: Optional[EvidenceStripResolutionRules] = None,
    source: str = "",
) -> EvidenceStripResult:

    request = normalize_evidence_strip_request(request)
    items = list(items or [])

    requirements = (
        requirements
        if requirements is not None
        else EvidenceStripRequirements()
    )

    rules = (
        rules
        if rules is not None
        else EvidenceStripResolutionRules()
    )

    assessment = build_evidence_strip_assessment(
        request,
        items,
        requirements,
    )

    flags = collect_evidence_strip_resolution_flags(
        assessment
    )

    restrictions = collect_evidence_strip_restrictions(
        assessment
    )

    errors: List[str] = []
    warnings = list(assessment.warnings or [])

    decision = EvidenceStripDecision.REVIEW_REQUIRED
    resolution_status = (
        EvidenceStripResolutionStatus.REVIEW_REQUIRED
    )

    if (
        assessment.data_state == EvidenceStripDataState.INVALID
        and rules.block_invalid
    ):
        decision = EvidenceStripDecision.BLOCK
        resolution_status = EvidenceStripResolutionStatus.BLOCKED
        errors.append("invalid_evidence")

    elif (
        assessment.consistency
        == EvidenceStripConsistency.INCONSISTENT
        and rules.block_inconsistent
    ):
        decision = EvidenceStripDecision.BLOCK
        resolution_status = EvidenceStripResolutionStatus.BLOCKED
        errors.append("inconsistent_evidence")

    elif assessment.unmet_requirements:
        decision = EvidenceStripDecision.REVIEW_REQUIRED
        resolution_status = (
            EvidenceStripResolutionStatus.REVIEW_REQUIRED
        )

    elif assessment.quality < rules.minimum_display_quality:
        decision = EvidenceStripDecision.REVIEW_REQUIRED
        resolution_status = (
            EvidenceStripResolutionStatus.REVIEW_REQUIRED
        )

    elif (
        assessment.data_state == EvidenceStripDataState.PARTIAL
        and not rules.allow_partial
    ):
        decision = EvidenceStripDecision.REVIEW_REQUIRED
        resolution_status = (
            EvidenceStripResolutionStatus.REVIEW_REQUIRED
        )

    elif (
        assessment.stale_evidence_count > 0
        and not rules.allow_stale_for_display
    ):
        decision = EvidenceStripDecision.REVIEW_REQUIRED
        resolution_status = (
            EvidenceStripResolutionStatus.REVIEW_REQUIRED
        )

    elif (
        assessment.consistency
        == EvidenceStripConsistency.CONDITIONAL
        and not rules.allow_conditional
    ):
        decision = EvidenceStripDecision.REVIEW_REQUIRED
        resolution_status = (
            EvidenceStripResolutionStatus.REVIEW_REQUIRED
        )

    elif (
        assessment.readiness
        == EvidenceStripReadiness.READY
        and assessment.quality >= rules.minimum_ready_quality
    ):
        decision = EvidenceStripDecision.ALLOW
        resolution_status = EvidenceStripResolutionStatus.RESOLVED

    else:
        decision = EvidenceStripDecision.ALLOW_WITH_RESTRICTION
        resolution_status = (
            EvidenceStripResolutionStatus.CONDITIONAL
        )

    presentation = build_evidence_strip_presentation(
        request=request,
        items=items,
        assessment=assessment,
        source=source,
    )

    allowed = decision in (
        EvidenceStripDecision.ALLOW,
        EvidenceStripDecision.ALLOW_WITH_RESTRICTION,
    )

    restricted = (
        decision == EvidenceStripDecision.ALLOW_WITH_RESTRICTION
    )

    review_required = (
        decision == EvidenceStripDecision.REVIEW_REQUIRED
    )

    blocked = decision == EvidenceStripDecision.BLOCK

    if blocked:
        reason = "Evidence strip blocked by evidence integrity rules."
    elif review_required:
        reason = "Evidence strip requires review."
    elif restricted:
        reason = "Evidence strip available with restrictions."
    else:
        reason = "Evidence strip resolved and ready."

    return EvidenceStripResult(
        decision=decision,
        status=resolution_status,

        allowed=allowed,
        restricted=restricted,
        review_required=review_required,
        blocked=blocked,

        assessment=assessment,
        presentation=presentation,

        flags=flags,
        restrictions=restrictions,
        errors=errors,
        warnings=warnings,

        reason=reason,
        timestamp=datetime.utcnow(),
    )


def validate_evidence_strip_result(
    result: EvidenceStripResult,
) -> bool:
    if result.decision not in EvidenceStripDecision:
        return False

    if result.status not in EvidenceStripResolutionStatus:
        return False

    states = [
        bool(result.allowed),
        bool(result.review_required),
        bool(result.blocked),
    ]

    if sum(states) != 1:
        return False

    if result.restricted and not result.allowed:
        return False

    if result.decision == EvidenceStripDecision.BLOCK:
        if not result.blocked:
            return False

    if result.decision == EvidenceStripDecision.REVIEW_REQUIRED:
        if not result.review_required:
            return False

    if result.decision in (
        EvidenceStripDecision.ALLOW,
        EvidenceStripDecision.ALLOW_WITH_RESTRICTION,
    ):
        if not result.allowed:
            return False

    return True


def validate_evidence_strip_result_authority(
    result: EvidenceStripResult,
) -> bool:
    """
    Result validation must remain presentation-level.
    Evidence Strip cannot authorize decisions, risk, CAS, or execution.
    """
    if not validate_evidence_strip_result(result):
        return False

    boundary = evidence_strip_authority_boundary()

    return (
        boundary["presentation_authority"] is True
        and boundary["evidence_display_authority"] is True
        and boundary["decision_authority"] is False
        and boundary["d13_authority"] is False
        and boundary["risk_authority"] is False
        and boundary["cas_authority"] is False
        and boundary["execution_authority"] is False
    )
# ============================================================
# PART 4 / 5
# Evidence Registry + Service Facade
# ============================================================

@dataclass
class EvidenceStripRegistryEntry:
    reference: EvidenceStripReference
    revision: int = 1
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EvidenceStripRegistrySnapshot:
    total: int = 0
    ready: int = 0
    partial: int = 0
    stale: int = 0
    invalid: int = 0
    error: int = 0

    references: List[EvidenceStripReference] = field(
        default_factory=list
    )

    timestamp: datetime = field(default_factory=datetime.utcnow)


class EvidenceStripRegistry:
    """Registry for terminal evidence-strip references."""

    def __init__(self) -> None:
        self._entries: Dict[str, EvidenceStripRegistryEntry] = {}

    @staticmethod
    def _key(reference: EvidenceStripReference) -> str:
        return ":".join(
            [
                _es_text(reference.market),
                _es_text(reference.instrument),
                _es_text(reference.symbol),
                _es_text(reference.contract),
                _es_text(reference.timeframe),
            ]
        )

    def exists(self, reference: EvidenceStripReference) -> bool:
        return self._key(reference) in self._entries

    def get(
        self,
        reference: EvidenceStripReference,
    ) -> Optional[EvidenceStripReference]:
        entry = self._entries.get(self._key(reference))
        return entry.reference if entry else None

    def get_entry(
        self,
        reference: EvidenceStripReference,
    ) -> Optional[EvidenceStripRegistryEntry]:
        return self._entries.get(self._key(reference))

    def add(
        self,
        reference: EvidenceStripReference,
    ) -> EvidenceStripRegistryEntry:
        validation = validate_evidence_strip_reference(reference)

        if not validation.valid:
            raise ValueError(
                "Invalid evidence-strip reference: "
                + ", ".join(validation.errors)
            )

        key = self._key(reference)

        if key in self._entries:
            raise ValueError(
                f"Evidence-strip reference already exists: {key}"
            )

        entry = EvidenceStripRegistryEntry(
            reference=reference,
            revision=1,
            updated_at=datetime.utcnow(),
        )

        self._entries[key] = entry
        return entry

    def replace(
        self,
        reference: EvidenceStripReference,
    ) -> EvidenceStripRegistryEntry:
        validation = validate_evidence_strip_reference(reference)

        if not validation.valid:
            raise ValueError(
                "Invalid evidence-strip reference: "
                + ", ".join(validation.errors)
            )

        key = self._key(reference)
        current = self._entries.get(key)

        revision = (
            current.revision + 1
            if current is not None
            else 1
        )

        entry = EvidenceStripRegistryEntry(
            reference=reference,
            revision=revision,
            updated_at=datetime.utcnow(),
        )

        self._entries[key] = entry
        return entry

    def remove(
        self,
        reference: EvidenceStripReference,
    ) -> bool:
        key = self._key(reference)

        if key not in self._entries:
            return False

        del self._entries[key]
        return True

    def list_references(
        self,
        market: str = "",
        instrument: str = "",
        symbol: str = "",
        timeframe: str = "",
        status: Optional[EvidenceStripStatus] = None,
    ) -> List[EvidenceStripReference]:

        references = []

        for entry in self._entries.values():
            ref = entry.reference

            if market and ref.market != market:
                continue

            if instrument and ref.instrument != instrument:
                continue

            if symbol and ref.symbol != symbol:
                continue

            if timeframe and ref.timeframe != timeframe:
                continue

            if status is not None and ref.status != status:
                continue

            references.append(ref)

        return references

    def snapshot(self) -> EvidenceStripRegistrySnapshot:
        references = self.list_references()

        ready = sum(
            1
            for ref in references
            if ref.status == EvidenceStripStatus.READY
        )

        partial = sum(
            1
            for ref in references
            if ref.status == EvidenceStripStatus.PARTIAL
        )

        stale = sum(
            1
            for ref in references
            if ref.status == EvidenceStripStatus.STALE
        )

        invalid = sum(
            1
            for ref in references
            if ref.status == EvidenceStripStatus.INVALID
        )

        error = sum(
            1
            for ref in references
            if ref.status == EvidenceStripStatus.ERROR
        )

        return EvidenceStripRegistrySnapshot(
            total=len(references),
            ready=ready,
            partial=partial,
            stale=stale,
            invalid=invalid,
            error=error,
            references=references,
            timestamp=datetime.utcnow(),
        )

    def count(self) -> int:
        return len(self._entries)


def validate_evidence_strip_registry(
    registry: EvidenceStripRegistry,
) -> bool:
    if not isinstance(registry, EvidenceStripRegistry):
        return False

    for entry in registry._entries.values():
        if not isinstance(entry, EvidenceStripRegistryEntry):
            return False

        validation = validate_evidence_strip_reference(
            entry.reference
        )

        if not validation.valid:
            return False

        if entry.revision < 1:
            return False

    return True


def evidence_strip_registry_health(
    registry: EvidenceStripRegistry,
) -> Dict[str, Any]:
    snapshot = registry.snapshot()

    return {
        "healthy": (
            validate_evidence_strip_registry(registry)
            and snapshot.invalid == 0
            and snapshot.error == 0
        ),
        "total": snapshot.total,
        "ready": snapshot.ready,
        "partial": snapshot.partial,
        "stale": snapshot.stale,
        "invalid": snapshot.invalid,
        "error": snapshot.error,
        "timestamp": snapshot.timestamp,
    }


# ------------------------------------------------------------
# SERVICE RESULT
# ------------------------------------------------------------

@dataclass
class EvidenceStripServiceResult:
    success: bool = False

    decision: EvidenceStripDecision = (
        EvidenceStripDecision.BLOCK
    )

    request_id: str = ""

    assessment: Optional[EvidenceStripAssessment] = None
    result: Optional[EvidenceStripResult] = None
    reference: Optional[EvidenceStripReference] = None

    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    reason: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)


# ------------------------------------------------------------
# SERVICE FACADE
# ------------------------------------------------------------

class EvidenceStripService:
    """
    Application facade for Terminal Evidence Strip.

    This service:
      - resolves evidence presentation
      - assesses evidence-display quality
      - registers references
      - exposes registry state

    It does NOT:
      - generate market intelligence
      - make D13 decisions
      - authorize risk
      - authorize CAS
      - execute orders
      - mutate positions
    """

    def __init__(
        self,
        registry: Optional[EvidenceStripRegistry] = None,
    ) -> None:
        self.registry = (
            registry
            if registry is not None
            else EvidenceStripRegistry()
        )

    def resolve(
        self,
        request: EvidenceStripRequest,
        items: Optional[List[EvidenceStripItem]] = None,
        requirements: Optional[EvidenceStripRequirements] = None,
        rules: Optional[EvidenceStripResolutionRules] = None,
        source: str = "",
    ) -> EvidenceStripServiceResult:

        request = normalize_evidence_strip_request(request)

        result = resolve_evidence_strip(
            request=request,
            items=items,
            requirements=requirements,
            rules=rules,
            source=source,
        )

        reference = build_evidence_strip_reference(
            request=request,
            evidence_count=len(items or []),
            status=(
                result.presentation.status
                if result.presentation is not None
                else EvidenceStripStatus.UNKNOWN
            ),
            source=source,
        )

        return EvidenceStripServiceResult(
            success=validate_evidence_strip_result(result),
            decision=result.decision,
            request_id=request.request_id,
            assessment=result.assessment,
            result=result,
            reference=reference,
            errors=list(result.errors),
            warnings=list(result.warnings),
            reason=result.reason,
            timestamp=datetime.utcnow(),
        )

    def assess(
        self,
        request: EvidenceStripRequest,
        items: Optional[List[EvidenceStripItem]] = None,
        requirements: Optional[EvidenceStripRequirements] = None,
    ) -> EvidenceStripAssessment:
        return build_evidence_strip_assessment(
            request=normalize_evidence_strip_request(request),
            items=list(items or []),
            requirements=requirements,
        )

    def register(
        self,
        reference: EvidenceStripReference,
    ) -> EvidenceStripRegistryEntry:
        return self.registry.replace(reference)

    def get(
        self,
        reference: EvidenceStripReference,
    ) -> Optional[EvidenceStripReference]:
        return self.registry.get(reference)

    def list_references(
        self,
        market: str = "",
        instrument: str = "",
        symbol: str = "",
        timeframe: str = "",
        status: Optional[EvidenceStripStatus] = None,
    ) -> List[EvidenceStripReference]:
        return self.registry.list_references(
            market=market,
            instrument=instrument,
            symbol=symbol,
            timeframe=timeframe,
            status=status,
        )

    def snapshot(self) -> EvidenceStripRegistrySnapshot:
        return self.registry.snapshot()

    def health(self) -> Dict[str, Any]:
        return evidence_strip_registry_health(self.registry)

    def integrity(self) -> bool:
        return validate_evidence_strip_registry(
            self.registry
        )

    def info(self) -> Dict[str, Any]:
        return {
            "engine": EVIDENCE_STRIP_ENGINE,
            "version": EVIDENCE_STRIP_VERSION,
            "authority": evidence_strip_authority_boundary(),
            "registry_count": self.registry.count(),
            "registry_healthy": self.integrity(),
        }


# ------------------------------------------------------------
# SINGLETON SERVICE
# ------------------------------------------------------------

_EVIDENCE_STRIP_SERVICE = EvidenceStripService()


def get_evidence_strip_service() -> EvidenceStripService:
    return _EVIDENCE_STRIP_SERVICE


# ------------------------------------------------------------
# CONVENIENCE APIs
# ------------------------------------------------------------

def resolve_evidence_for_terminal(
    request: EvidenceStripRequest,
    items: Optional[List[EvidenceStripItem]] = None,
    requirements: Optional[EvidenceStripRequirements] = None,
    rules: Optional[EvidenceStripResolutionRules] = None,
    source: str = "",
) -> EvidenceStripServiceResult:
    return get_evidence_strip_service().resolve(
        request=request,
        items=items,
        requirements=requirements,
        rules=rules,
        source=source,
    )


def get_terminal_evidence_reference(
    reference: EvidenceStripReference,
) -> Optional[EvidenceStripReference]:
    return get_evidence_strip_service().get(reference)


def terminal_evidence_strip_snapshot(
) -> EvidenceStripRegistrySnapshot:
    return get_evidence_strip_service().snapshot()


def terminal_evidence_strip_count() -> int:
    return get_evidence_strip_service().registry.count()


def terminal_evidence_strip_health() -> Dict[str, Any]:
    return get_evidence_strip_service().health()


def terminal_evidence_strip_integrity() -> bool:
    return get_evidence_strip_service().integrity()


def terminal_evidence_strip_operational_check() -> Dict[str, Any]:
    service = get_evidence_strip_service()

    return {
        "operational": (
            validate_evidence_strip_authority_boundary()
            and service.integrity()
        ),
        "authority_boundary_valid":
            validate_evidence_strip_authority_boundary(),
        "registry_healthy":
            service.integrity(),
        "count":
            service.registry.count(),
        "timestamp":
            datetime.utcnow(),
    }


def terminal_evidence_strip_service_info() -> Dict[str, Any]:
    return get_evidence_strip_service().info()
# ============================================================
# PART 5 / 5
# Serialization + Integrity + Summary + Public API
# ============================================================

def _es_iso(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _es_serialize(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()

    if hasattr(value, "value"):
        return value.value

    if hasattr(value, "__dataclass_fields__"):
        return {
            key: _es_serialize(val)
            for key, val in value.__dict__.items()
        }

    if isinstance(value, dict):
        return {
            str(key): _es_serialize(val)
            for key, val in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [_es_serialize(item) for item in value]

    return value


# ------------------------------------------------------------
# SERIALIZATION
# ------------------------------------------------------------

def serialize_evidence_strip_item(
    item: EvidenceStripItem,
) -> Dict[str, Any]:
    return _es_serialize(item)


def serialize_evidence_strip_reference(
    reference: EvidenceStripReference,
) -> Dict[str, Any]:
    return _es_serialize(reference)


def serialize_evidence_strip_assessment(
    assessment: EvidenceStripAssessment,
) -> Dict[str, Any]:
    return _es_serialize(assessment)


def serialize_evidence_strip_presentation(
    presentation: EvidenceStripPresentation,
) -> Dict[str, Any]:
    return _es_serialize(presentation)


def serialize_evidence_strip_result(
    result: EvidenceStripResult,
) -> Dict[str, Any]:
    return _es_serialize(result)


def serialize_evidence_strip_service_result(
    service_result: EvidenceStripServiceResult,
) -> Dict[str, Any]:
    return _es_serialize(service_result)


def serialize_evidence_strip_snapshot(
    snapshot: EvidenceStripRegistrySnapshot,
) -> Dict[str, Any]:
    return _es_serialize(snapshot)


# ------------------------------------------------------------
# ITEM INTEGRITY
# ------------------------------------------------------------

def validate_evidence_strip_item_integrity(
    item: EvidenceStripItem,
) -> bool:
    if not isinstance(item, EvidenceStripItem):
        return False

    if not _es_text(item.evidence_id):
        return False

    if not _es_text(item.category):
        return False

    if item.status not in EvidenceStripStatus:
        return False

    if item.source_type not in EvidenceStripSourceType:
        return False

    if item.severity not in EvidenceStripSeverity:
        return False

    if not 0.0 <= float(item.confidence) <= 100.0:
        return False

    if item.freshness_seconds is not None:
        if float(item.freshness_seconds) < 0.0:
            return False

    return True


# ------------------------------------------------------------
# REFERENCE INTEGRITY
# ------------------------------------------------------------

def validate_evidence_strip_reference_integrity(
    reference: EvidenceStripReference,
) -> bool:
    validation = validate_evidence_strip_reference(reference)

    if not validation.valid:
        return False

    if not _es_text(reference.market):
        return False

    if not _es_text(reference.instrument):
        return False

    if not _es_text(reference.symbol):
        return False

    if reference.status not in EvidenceStripStatus:
        return False

    if reference.mode not in EvidenceStripMode:
        return False

    if reference.evidence_count < 0:
        return False

    if not _es_text(reference.version):
        return False

    return True


# ------------------------------------------------------------
# ASSESSMENT INTEGRITY
# ------------------------------------------------------------

def validate_evidence_strip_assessment_integrity(
    assessment: EvidenceStripAssessment,
) -> bool:
    if not isinstance(assessment, EvidenceStripAssessment):
        return False

    if assessment.data_state not in EvidenceStripDataState:
        return False

    if assessment.consistency not in EvidenceStripConsistency:
        return False

    if assessment.readiness not in EvidenceStripReadiness:
        return False

    numeric_values = (
        assessment.completeness,
        assessment.quality,
        assessment.confidence,
    )

    if not all(
        0.0 <= float(value) <= 100.0
        for value in numeric_values
    ):
        return False

    if assessment.evidence_count < 0:
        return False

    if assessment.fresh_evidence_count < 0:
        return False

    if assessment.stale_evidence_count < 0:
        return False

    if assessment.invalid_evidence_count < 0:
        return False

    if (
        assessment.fresh_evidence_count
        + assessment.stale_evidence_count
        + assessment.invalid_evidence_count
        > assessment.evidence_count
    ):
        return False

    if assessment.status not in EvidenceStripStatus:
        return False

    if assessment.mode not in EvidenceStripMode:
        return False

    return True


# ------------------------------------------------------------
# PRESENTATION INTEGRITY
# ------------------------------------------------------------

def validate_evidence_strip_presentation_integrity(
    presentation: EvidenceStripPresentation,
) -> bool:
    if not isinstance(
        presentation,
        EvidenceStripPresentation,
    ):
        return False

    if not _es_text(presentation.market):
        return False

    if not _es_text(presentation.instrument):
        return False

    if not _es_text(presentation.symbol):
        return False

    if presentation.mode not in EvidenceStripMode:
        return False

    if presentation.status not in EvidenceStripStatus:
        return False

    values = (
        presentation.completeness,
        presentation.quality,
        presentation.confidence,
    )

    if not all(
        0.0 <= float(value) <= 100.0
        for value in values
    ):
        return False

    if presentation.evidence_count < 0:
        return False

    if presentation.fresh_evidence_count < 0:
        return False

    if presentation.stale_evidence_count < 0:
        return False

    for item in presentation.items:
        if not validate_evidence_strip_item_integrity(item):
            return False

    return True


# ------------------------------------------------------------
# RESULT INTEGRITY
# ------------------------------------------------------------

def validate_evidence_strip_result_integrity(
    result: EvidenceStripResult,
) -> bool:
    if not validate_evidence_strip_result(result):
        return False

    if result.assessment is not None:
        if not validate_evidence_strip_assessment_integrity(
            result.assessment
        ):
            return False

    if result.presentation is not None:
        if not validate_evidence_strip_presentation_integrity(
            result.presentation
        ):
            return False

    if result.decision == EvidenceStripDecision.BLOCK:
        if not result.blocked:
            return False

    elif result.decision == EvidenceStripDecision.REVIEW_REQUIRED:
        if not result.review_required:
            return False

    elif result.decision == EvidenceStripDecision.ALLOW:
        if not result.allowed or result.restricted:
            return False

    elif result.decision == EvidenceStripDecision.ALLOW_WITH_RESTRICTION:
        if not result.allowed or not result.restricted:
            return False

    return validate_evidence_strip_result_authority(result)


# ------------------------------------------------------------
# SNAPSHOT INTEGRITY
# ------------------------------------------------------------

def validate_evidence_strip_snapshot_integrity(
    snapshot: EvidenceStripRegistrySnapshot,
) -> bool:
    if not isinstance(
        snapshot,
        EvidenceStripRegistrySnapshot,
    ):
        return False

    references = list(snapshot.references or [])

    if snapshot.total != len(references):
        return False

    counts = (
        snapshot.ready,
        snapshot.partial,
        snapshot.stale,
        snapshot.invalid,
        snapshot.error,
    )

    if any(int(value) < 0 for value in counts):
        return False

    if sum(counts) != snapshot.total:
        return False

    for reference in references:
        if not validate_evidence_strip_reference_integrity(
            reference
        ):
            return False

    return True


# ------------------------------------------------------------
# SERVICE RESULT INTEGRITY
# ------------------------------------------------------------

def validate_evidence_strip_service_result_integrity(
    service_result: EvidenceStripServiceResult,
) -> bool:
    if not isinstance(
        service_result,
        EvidenceStripServiceResult,
    ):
        return False

    if not _es_text(service_result.request_id):
        return False

    if service_result.decision not in EvidenceStripDecision:
        return False

    if service_result.result is not None:
        if not validate_evidence_strip_result_integrity(
            service_result.result
        ):
            return False

    if service_result.assessment is not None:
        if not validate_evidence_strip_assessment_integrity(
            service_result.assessment
        ):
            return False

    if service_result.reference is not None:
        if not validate_evidence_strip_reference_integrity(
            service_result.reference
        ):
            return False

    if service_result.success and service_result.errors:
        return False

    return True


# ------------------------------------------------------------
# SUMMARY
# ------------------------------------------------------------

def build_evidence_strip_summary(
    result: EvidenceStripResult,
) -> Dict[str, Any]:
    assessment = result.assessment
    presentation = result.presentation

    return {
        "engine": EVIDENCE_STRIP_ENGINE,
        "version": EVIDENCE_STRIP_VERSION,

        "decision": result.decision.value,
        "resolution_status": result.status.value,

        "allowed": result.allowed,
        "restricted": result.restricted,
        "review_required": result.review_required,
        "blocked": result.blocked,

        "market": (
            presentation.market
            if presentation else
            assessment.market
            if assessment else ""
        ),

        "instrument": (
            presentation.instrument
            if presentation else
            assessment.instrument
            if assessment else ""
        ),

        "symbol": (
            presentation.symbol
            if presentation else
            assessment.symbol
            if assessment else ""
        ),

        "contract": (
            presentation.contract
            if presentation else ""
        ),

        "timeframe": (
            presentation.timeframe
            if presentation else ""
        ),

        "session": (
            presentation.session
            if presentation else ""
        ),

        "market_phase": (
            presentation.market_phase
            if presentation else ""
        ),

        "mode": (
            presentation.mode.value
            if presentation else
            assessment.mode.value
            if assessment else
            EvidenceStripMode.UNKNOWN.value
        ),

        "evidence_count": (
            presentation.evidence_count
            if presentation else
            assessment.evidence_count
            if assessment else
            0
        ),

        "fresh_evidence_count": (
            presentation.fresh_evidence_count
            if presentation else
            assessment.fresh_evidence_count
            if assessment else
            0
        ),

        "stale_evidence_count": (
            presentation.stale_evidence_count
            if presentation else
            assessment.stale_evidence_count
            if assessment else
            0
        ),

        "completeness": (
            presentation.completeness
            if presentation else
            assessment.completeness
            if assessment else
            0.0
        ),

        "quality": (
            presentation.quality
            if presentation else
            assessment.quality
            if assessment else
            0.0
        ),

        "confidence": (
            presentation.confidence
            if presentation else
            assessment.confidence
            if assessment else
            0.0
        ),

        "flags": list(result.flags),
        "restrictions": list(result.restrictions),
        "warnings": list(result.warnings),
        "errors": list(result.errors),

        "reason": result.reason,
        "timestamp": _es_iso(result.timestamp),
    }


# ------------------------------------------------------------
# FINAL PUBLIC API
# ------------------------------------------------------------

__all__ = [
    # Constants
    "EVIDENCE_STRIP_ENGINE",
    "EVIDENCE_STRIP_VERSION",

    # Enums
    "EvidenceStripStatus",
    "EvidenceStripMode",
    "EvidenceStripPriority",
    "EvidenceStripSeverity",
    "EvidenceStripSourceType",
    "EvidenceStripContractStatus",
    "EvidenceStripDataState",
    "EvidenceStripConsistency",
    "EvidenceStripReadiness",
    "EvidenceStripDecision",
    "EvidenceStripResolutionStatus",

    # Contracts
    "EvidenceStripRequest",
    "EvidenceStripItem",
    "EvidenceStripReference",
    "EvidenceStripContractValidation",
    "EvidenceStripRequirements",
    "EvidenceStripAssessment",
    "EvidenceStripResolutionRules",
    "EvidenceStripPresentation",
    "EvidenceStripResult",
    "EvidenceStripSourceMap",
    "EvidenceStripRegistryEntry",
    "EvidenceStripRegistrySnapshot",
    "EvidenceStripServiceResult",

    # Authority
    "evidence_strip_authority_boundary",
    "validate_evidence_strip_authority_boundary",

    # Request / reference
    "normalize_evidence_strip_request",
    "validate_evidence_strip_request",
    "build_evidence_strip_request",
    "build_evidence_strip_reference",
    "validate_evidence_strip_reference",

    # Assessment
    "build_evidence_strip_requirements",
    "evaluate_evidence_strip_data_state",
    "evaluate_evidence_strip_consistency",
    "evaluate_evidence_strip_requirements",
    "evaluate_evidence_strip_freshness",
    "evaluate_evidence_strip_completeness",
    "evaluate_evidence_strip_quality",
    "evaluate_evidence_strip_confidence",
    "evaluate_evidence_strip_readiness",
    "build_evidence_strip_assessment",

    # Resolution
    "build_evidence_strip_resolution_rules",
    "build_evidence_strip_source_map",
    "collect_evidence_strip_resolution_flags",
    "collect_evidence_strip_restrictions",
    "build_evidence_strip_presentation",
    "resolve_evidence_strip",
    "validate_evidence_strip_result",
    "validate_evidence_strip_result_authority",

    # Registry
    "EvidenceStripRegistry",
    "validate_evidence_strip_registry",
    "evidence_strip_registry_health",

    # Service
    "EvidenceStripService",
    "get_evidence_strip_service",

    # Convenience APIs
    "resolve_evidence_for_terminal",
    "get_terminal_evidence_reference",
    "terminal_evidence_strip_snapshot",
    "terminal_evidence_strip_count",
    "terminal_evidence_strip_health",
    "terminal_evidence_strip_integrity",
    "terminal_evidence_strip_operational_check",
    "terminal_evidence_strip_service_info",

    # Serialization
    "serialize_evidence_strip_item",
    "serialize_evidence_strip_reference",
    "serialize_evidence_strip_assessment",
    "serialize_evidence_strip_presentation",
    "serialize_evidence_strip_result",
    "serialize_evidence_strip_service_result",
    "serialize_evidence_strip_snapshot",

    # Integrity
    "validate_evidence_strip_item_integrity",
    "validate_evidence_strip_reference_integrity",
    "validate_evidence_strip_assessment_integrity",
    "validate_evidence_strip_presentation_integrity",
    "validate_evidence_strip_result_integrity",
    "validate_evidence_strip_snapshot_integrity",
    "validate_evidence_strip_service_result_integrity",

    # Summary
    "build_evidence_strip_summary",
]