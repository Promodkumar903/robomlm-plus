# ============================================================
# ROBOMLM_PLUS
# app/terminal/intelligence_panel.py
# PART 1 / 5
# Intelligence Panel Contract + Authority Boundary
# ============================================================

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


INTELLIGENCE_PANEL_ENGINE = "ROBOMLM_TERMINAL_INTELLIGENCE_PANEL"
INTELLIGENCE_PANEL_VERSION = "1.0"


# ------------------------------------------------------------
# ENUMS
# ------------------------------------------------------------

class IntelligencePanelStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    READY = "READY"
    PARTIAL = "PARTIAL"
    STALE = "STALE"
    INVALID = "INVALID"
    ERROR = "ERROR"


class IntelligencePanelMode(str, Enum):
    PAPER = "PAPER"
    DEMO = "DEMO"
    LIVE = "LIVE"
    UNKNOWN = "UNKNOWN"


class IntelligencePanelPriority(str, Enum):
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IntelligencePanelSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IntelligencePanelSourceType(str, Enum):
    INTELLIGENCE_ENGINE = "INTELLIGENCE_ENGINE"
    EVIDENCE_CORTEX = "EVIDENCE_CORTEX"
    MARKET_CONTEXT = "MARKET_CONTEXT"
    DECISION_CORTEX = "DECISION_CORTEX"
    MEMORY = "MEMORY"
    EXTERNAL = "EXTERNAL"
    UNKNOWN = "UNKNOWN"


class IntelligencePanelContractStatus(str, Enum):
    CREATED = "CREATED"
    VALID = "VALID"
    INVALID = "INVALID"
    READY = "READY"


# ------------------------------------------------------------
# INTELLIGENCE TYPE
# ------------------------------------------------------------

class IntelligencePanelCategory(str, Enum):
    MARKET_STATE = "MARKET_STATE"
    TREND = "TREND"
    MOMENTUM = "MOMENTUM"
    PARTICIPATION = "PARTICIPATION"
    LIQUIDITY = "LIQUIDITY"
    VOLATILITY = "VOLATILITY"
    DERIVATIVE = "DERIVATIVE"
    MICROSTRUCTURE = "MICROSTRUCTURE"
    RELATIONSHIP = "RELATIONSHIP"
    REGIME = "REGIME"
    TIMING = "TIMING"
    MARKET_MEMORY = "MARKET_MEMORY"
    COMPOSITE = "COMPOSITE"
    OTHER = "OTHER"


# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------

def _ip_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def _ip_enum(value: Any, enum_cls: Any, default: Any) -> Any:
    if isinstance(value, enum_cls):
        return value

    try:
        return enum_cls(str(value).strip().upper())
    except (ValueError, TypeError):
        return default


def _ip_number(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)

        if number != number:
            return default

        return number

    except (TypeError, ValueError):
        return default


def _ip_timestamp(value: Any = None) -> datetime:
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
class IntelligencePanelRequest:
    market: str = ""
    instrument: str = ""
    symbol: str = ""
    contract: str = ""

    timeframe: str = ""
    session: str = ""
    market_phase: str = ""

    mode: IntelligencePanelMode = (
        IntelligencePanelMode.UNKNOWN
    )

    priority: IntelligencePanelPriority = (
        IntelligencePanelPriority.NORMAL
    )

    requested_categories: List[str] = field(
        default_factory=list
    )

    requested_fields: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    request_id: str = ""

    timestamp: datetime = field(
        default_factory=datetime.utcnow
    )


# ------------------------------------------------------------
# INTELLIGENCE ITEM
# ------------------------------------------------------------

@dataclass
class IntelligencePanelItem:
    intelligence_id: str = ""

    category: IntelligencePanelCategory = (
        IntelligencePanelCategory.OTHER
    )

    name: str = ""
    value: Any = None
    unit: str = ""

    interpretation: str = ""

    source: str = ""

    source_type: IntelligencePanelSourceType = (
        IntelligencePanelSourceType.UNKNOWN
    )

    status: IntelligencePanelStatus = (
        IntelligencePanelStatus.UNKNOWN
    )

    severity: IntelligencePanelSeverity = (
        IntelligencePanelSeverity.INFO
    )

    confidence: float = 0.0

    timestamp: datetime = field(
        default_factory=datetime.utcnow
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ------------------------------------------------------------
# INTELLIGENCE PANEL REFERENCE
# ------------------------------------------------------------

@dataclass
class IntelligencePanelReference:
    market: str = ""
    instrument: str = ""
    symbol: str = ""
    contract: str = ""

    timeframe: str = ""
    session: str = ""
    market_phase: str = ""

    status: IntelligencePanelStatus = (
        IntelligencePanelStatus.UNKNOWN
    )

    mode: IntelligencePanelMode = (
        IntelligencePanelMode.UNKNOWN
    )

    source: str = ""

    intelligence_count: int = 0

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = field(
        default_factory=datetime.utcnow
    )

    version: str = INTELLIGENCE_PANEL_VERSION


# ------------------------------------------------------------
# CONTRACT VALIDATION
# ------------------------------------------------------------

@dataclass
class IntelligencePanelContractValidation:
    status: IntelligencePanelContractStatus = (
        IntelligencePanelContractStatus.CREATED
    )

    valid: bool = False

    errors: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    checked_at: datetime = field(
        default_factory=datetime.utcnow
    )


# ------------------------------------------------------------
# AUTHORITY BOUNDARY
# ------------------------------------------------------------

def intelligence_panel_authority_boundary() -> Dict[str, bool]:
    """
    Intelligence Panel is a presentation/consumption surface.

    It may organize and display intelligence received from
    upstream intelligence authorities.

    It must never become the source of decision authority.
    """

    return {
        "presentation_authority": True,
        "intelligence_display_authority": True,

        # Upstream generation remains external.
        "market_data_authority": False,
        "evidence_generation_authority": False,
        "intelligence_generation_authority": False,
        "market_context_authority": False,

        # Decision authority remains upstream.
        "decision_authority": False,
        "d13_authority": False,

        # Safety authorities remain independent.
        "risk_authority": False,
        "cas_authority": False,

        # Execution remains completely outside this panel.
        "execution_authority": False,
        "order_authority": False,
        "position_authority": False,

        # No mutation of upstream intelligence.
        "upstream_mutation_authority": False,
    }


def validate_intelligence_panel_authority_boundary() -> bool:
    boundary = intelligence_panel_authority_boundary()

    required_true = (
        "presentation_authority",
        "intelligence_display_authority",
    )

    required_false = (
        "market_data_authority",
        "evidence_generation_authority",
        "intelligence_generation_authority",
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
        all(
            boundary.get(key) is True
            for key in required_true
        )
        and all(
            boundary.get(key) is False
            for key in required_false
        )
    )


# ------------------------------------------------------------
# REQUEST NORMALIZATION
# ------------------------------------------------------------

def normalize_intelligence_panel_request(
    request: IntelligencePanelRequest,
) -> IntelligencePanelRequest:

    return IntelligencePanelRequest(
        market=_ip_text(request.market),
        instrument=_ip_text(request.instrument),
        symbol=_ip_text(request.symbol),
        contract=_ip_text(request.contract),

        timeframe=_ip_text(request.timeframe),
        session=_ip_text(request.session),
        market_phase=_ip_text(request.market_phase),

        mode=_ip_enum(
            request.mode,
            IntelligencePanelMode,
            IntelligencePanelMode.UNKNOWN,
        ),

        priority=_ip_enum(
            request.priority,
            IntelligencePanelPriority,
            IntelligencePanelPriority.NORMAL,
        ),

        requested_categories=[
            _ip_text(value)
            for value in (
                request.requested_categories or []
            )
            if _ip_text(value)
        ],

        requested_fields=[
            _ip_text(value)
            for value in (
                request.requested_fields or []
            )
            if _ip_text(value)
        ],

        metadata=dict(request.metadata or {}),

        request_id=_ip_text(
            request.request_id
        ),

        timestamp=_ip_timestamp(
            request.timestamp
        ),
    )


# ------------------------------------------------------------
# REQUEST VALIDATION
# ------------------------------------------------------------

def validate_intelligence_panel_request(
    request: IntelligencePanelRequest,
) -> IntelligencePanelContractValidation:

    errors: List[str] = []
    warnings: List[str] = []

    if not _ip_text(request.market):
        errors.append("market_missing")

    if not _ip_text(request.instrument):
        errors.append("instrument_missing")

    if not _ip_text(request.symbol):
        errors.append("symbol_missing")

    if request.mode == IntelligencePanelMode.UNKNOWN:
        warnings.append("mode_unknown")

    if not _ip_text(request.request_id):
        warnings.append("request_id_missing")

    valid = len(errors) == 0

    return IntelligencePanelContractValidation(
        status=(
            IntelligencePanelContractStatus.VALID
            if valid
            else IntelligencePanelContractStatus.INVALID
        ),
        valid=valid,
        errors=errors,
        warnings=warnings,
        checked_at=datetime.utcnow(),
    )


# ------------------------------------------------------------
# REQUEST BUILDER
# ------------------------------------------------------------

def build_intelligence_panel_request(
    market: str,
    instrument: str,
    symbol: str,
    contract: str = "",
    timeframe: str = "",
    session: str = "",
    market_phase: str = "",
    mode: Any = IntelligencePanelMode.UNKNOWN,
    priority: Any = IntelligencePanelPriority.NORMAL,
    requested_categories: Optional[List[str]] = None,
    requested_fields: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    request_id: str = "",
) -> IntelligencePanelRequest:

    request = IntelligencePanelRequest(
        market=market,
        instrument=instrument,
        symbol=symbol,
        contract=contract,

        timeframe=timeframe,
        session=session,
        market_phase=market_phase,

        mode=_ip_enum(
            mode,
            IntelligencePanelMode,
            IntelligencePanelMode.UNKNOWN,
        ),

        priority=_ip_enum(
            priority,
            IntelligencePanelPriority,
            IntelligencePanelPriority.NORMAL,
        ),

        requested_categories=list(
            requested_categories or []
        ),

        requested_fields=list(
            requested_fields or []
        ),

        metadata=dict(metadata or {}),

        request_id=request_id,

        timestamp=datetime.utcnow(),
    )

    return normalize_intelligence_panel_request(
        request
    )


# ------------------------------------------------------------
# REFERENCE BUILDER
# ------------------------------------------------------------

def build_intelligence_panel_reference(
    request: IntelligencePanelRequest,
    intelligence_count: int = 0,
    status: Any = IntelligencePanelStatus.UNKNOWN,
    source: str = "",
) -> IntelligencePanelReference:

    return IntelligencePanelReference(
        market=_ip_text(request.market),
        instrument=_ip_text(request.instrument),
        symbol=_ip_text(request.symbol),
        contract=_ip_text(request.contract),

        timeframe=_ip_text(request.timeframe),
        session=_ip_text(request.session),
        market_phase=_ip_text(request.market_phase),

        status=_ip_enum(
            status,
            IntelligencePanelStatus,
            IntelligencePanelStatus.UNKNOWN,
        ),

        mode=_ip_enum(
            request.mode,
            IntelligencePanelMode,
            IntelligencePanelMode.UNKNOWN,
        ),

        source=_ip_text(source),

        intelligence_count=max(
            0,
            int(intelligence_count),
        ),

        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),

        version=INTELLIGENCE_PANEL_VERSION,
    )
# ============================================================
# ROBOMLM_PLUS
# app/terminal/intelligence_panel.py
# PART 2 / 5
# Intelligence Panel Assessment + Readiness
# ============================================================


class IntelligencePanelDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    INVALID = "INVALID"


class IntelligencePanelConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONDITIONAL = "CONDITIONAL"
    INCONSISTENT = "INCONSISTENT"
    UNKNOWN = "UNKNOWN"


class IntelligencePanelReadiness(str, Enum):
    READY = "READY"
    CONDITIONALLY_READY = "CONDITIONALLY_READY"
    NOT_READY = "NOT_READY"
    BLOCKED = "BLOCKED"


@dataclass
class IntelligencePanelRequirements:
    require_market: bool = True
    require_instrument: bool = True
    require_symbol: bool = True
    require_intelligence: bool = True
    require_source: bool = True
    require_freshness: bool = True
    require_confidence: bool = False
    minimum_items: int = 1
    minimum_confidence: float = 0.0
    maximum_age_seconds: float = 300.0
    allow_partial: bool = True


@dataclass
class IntelligencePanelAssessment:
    data_state: IntelligencePanelDataState = IntelligencePanelDataState.MISSING
    consistency: IntelligencePanelConsistency = IntelligencePanelConsistency.UNKNOWN
    readiness: IntelligencePanelReadiness = IntelligencePanelReadiness.NOT_READY
    completeness: float = 0.0
    quality: float = 0.0
    confidence: float = 0.0
    freshness: float = 0.0
    source_quality: float = 0.0
    item_count: int = 0
    valid_item_count: int = 0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    assessed_at: datetime = field(default_factory=datetime.utcnow)


def build_intelligence_panel_requirements(
    require_market: bool = True,
    require_instrument: bool = True,
    require_symbol: bool = True,
    require_intelligence: bool = True,
    require_source: bool = True,
    require_freshness: bool = True,
    require_confidence: bool = False,
    minimum_items: int = 1,
    minimum_confidence: float = 0.0,
    maximum_age_seconds: float = 300.0,
    allow_partial: bool = True,
) -> IntelligencePanelRequirements:
    return IntelligencePanelRequirements(
        require_market=bool(require_market),
        require_instrument=bool(require_instrument),
        require_symbol=bool(require_symbol),
        require_intelligence=bool(require_intelligence),
        require_source=bool(require_source),
        require_freshness=bool(require_freshness),
        require_confidence=bool(require_confidence),
        minimum_items=max(0, int(minimum_items)),
        minimum_confidence=max(0.0, min(1.0, _ip_number(
            minimum_confidence
        ))),
        maximum_age_seconds=max(
            0.0,
            _ip_number(maximum_age_seconds, 300.0),
        ),
        allow_partial=bool(allow_partial),
    )


def evaluate_intelligence_panel_data_state(
    request: IntelligencePanelRequest,
    items: List[IntelligencePanelItem],
    requirements: IntelligencePanelRequirements,
) -> IntelligencePanelDataState:
    if not isinstance(request, IntelligencePanelRequest):
        return IntelligencePanelDataState.INVALID

    if not items:
        return IntelligencePanelDataState.MISSING

    if any(
        not isinstance(item, IntelligencePanelItem)
        for item in items
    ):
        return IntelligencePanelDataState.INVALID

    missing_required = False

    if requirements.require_market and not _ip_text(request.market):
        missing_required = True

    if requirements.require_instrument and not _ip_text(request.instrument):
        missing_required = True

    if requirements.require_symbol and not _ip_text(request.symbol):
        missing_required = True

    if requirements.require_intelligence:
        if len(items) < requirements.minimum_items:
            missing_required = True

    if missing_required:
        return (
            IntelligencePanelDataState.PARTIAL
            if requirements.allow_partial
            else IntelligencePanelDataState.MISSING
        )

    return IntelligencePanelDataState.COMPLETE


def evaluate_intelligence_panel_consistency(
    request: IntelligencePanelRequest,
    items: List[IntelligencePanelItem],
) -> IntelligencePanelConsistency:
    if not isinstance(request, IntelligencePanelRequest):
        return IntelligencePanelConsistency.UNKNOWN

    if not items:
        return IntelligencePanelConsistency.UNKNOWN

    if any(
        not isinstance(item, IntelligencePanelItem)
        for item in items
    ):
        return IntelligencePanelConsistency.INCONSISTENT

    request_symbol = _ip_text(request.symbol).upper()
    request_instrument = _ip_text(request.instrument).upper()

    conflicts = 0
    known = 0

    for item in items:
        metadata = item.metadata or {}

        item_symbol = _ip_text(
            metadata.get("symbol")
        ).upper()

        item_instrument = _ip_text(
            metadata.get("instrument")
        ).upper()

        if item_symbol:
            known += 1
            if request_symbol and item_symbol != request_symbol:
                conflicts += 1

        if item_instrument:
            known += 1
            if (
                request_instrument
                and item_instrument != request_instrument
            ):
                conflicts += 1

    if conflicts > 0:
        return IntelligencePanelConsistency.INCONSISTENT

    if known == 0:
        return IntelligencePanelConsistency.CONDITIONAL

    return IntelligencePanelConsistency.CONSISTENT


def evaluate_intelligence_panel_requirements(
    request: IntelligencePanelRequest,
    items: List[IntelligencePanelItem],
    requirements: IntelligencePanelRequirements,
) -> Dict[str, bool]:
    checks: Dict[str, bool] = {}

    checks["market"] = (
        not requirements.require_market
        or bool(_ip_text(request.market))
    )

    checks["instrument"] = (
        not requirements.require_instrument
        or bool(_ip_text(request.instrument))
    )

    checks["symbol"] = (
        not requirements.require_symbol
        or bool(_ip_text(request.symbol))
    )

    checks["minimum_items"] = (
        not requirements.require_intelligence
        or len(items) >= requirements.minimum_items
    )

    checks["source"] = (
        not requirements.require_source
        or any(_ip_text(item.source) for item in items)
    )

    return checks


def evaluate_intelligence_panel_freshness(
    items: List[IntelligencePanelItem],
    maximum_age_seconds: float = 300.0,
) -> float:
    if not items:
        return 0.0

    now = datetime.utcnow()
    max_age = max(0.0, _ip_number(maximum_age_seconds, 300.0))

    scores: List[float] = []

    for item in items:
        timestamp = item.timestamp

        if not isinstance(timestamp, datetime):
            scores.append(0.0)
            continue

        age = max(0.0, (now - timestamp).total_seconds())

        if max_age <= 0.0:
            score = 1.0 if age <= 0.0 else 0.0
        elif age <= max_age:
            score = max(0.0, 1.0 - (age / max_age))
        else:
            score = 0.0

        scores.append(score)

    return sum(scores) / len(scores) if scores else 0.0


def evaluate_intelligence_panel_completeness(
    request: IntelligencePanelRequest,
    items: List[IntelligencePanelItem],
    requirements: IntelligencePanelRequirements,
) -> float:
    checks = evaluate_intelligence_panel_requirements(
        request,
        items,
        requirements,
    )

    if not checks:
        return 0.0

    passed = sum(
        1
        for value in checks.values()
        if value is True
    )

    return passed / len(checks)


def evaluate_intelligence_panel_quality(
    items: List[IntelligencePanelItem],
    freshness: float,
    completeness: float,
) -> float:
    if not items:
        return 0.0

    valid_items = [
        item
        for item in items
        if isinstance(item, IntelligencePanelItem)
        and item.status not in (
            IntelligencePanelStatus.INVALID,
            IntelligencePanelStatus.ERROR,
        )
    ]

    if not valid_items:
        return 0.0

    source_score = sum(
        1.0 if _ip_text(item.source) else 0.0
        for item in valid_items
    ) / len(valid_items)

    confidence_score = sum(
        max(0.0, min(1.0, _ip_number(item.confidence)))
        for item in valid_items
    ) / len(valid_items)

    return max(
        0.0,
        min(
            1.0,
            (
                completeness * 0.30
                + freshness * 0.25
                + confidence_score * 0.25
                + source_score * 0.20
            ),
        ),
    )


def evaluate_intelligence_panel_confidence(
    items: List[IntelligencePanelItem],
) -> float:
    valid_items = [
        item
        for item in items
        if isinstance(item, IntelligencePanelItem)
        and item.status not in (
            IntelligencePanelStatus.INVALID,
            IntelligencePanelStatus.ERROR,
        )
    ]

    if not valid_items:
        return 0.0

    values = [
        max(
            0.0,
            min(
                1.0,
                _ip_number(item.confidence),
            ),
        )
        for item in valid_items
    ]

    return sum(values) / len(values)


def evaluate_intelligence_panel_readiness(
    data_state: IntelligencePanelDataState,
    consistency: IntelligencePanelConsistency,
    completeness: float,
    quality: float,
    confidence: float,
    requirements: IntelligencePanelRequirements,
) -> IntelligencePanelReadiness:
    if data_state == IntelligencePanelDataState.INVALID:
        return IntelligencePanelReadiness.BLOCKED

    if consistency == IntelligencePanelConsistency.INCONSISTENT:
        return IntelligencePanelReadiness.BLOCKED

    if data_state == IntelligencePanelDataState.MISSING:
        return IntelligencePanelReadiness.NOT_READY

    if completeness < 1.0:
        if not requirements.allow_partial:
            return IntelligencePanelReadiness.NOT_READY
        return IntelligencePanelReadiness.CONDITIONALLY_READY

    if requirements.require_confidence:
        if confidence < requirements.minimum_confidence:
            return IntelligencePanelReadiness.CONDITIONALLY_READY

    if quality <= 0.0:
        return IntelligencePanelReadiness.NOT_READY

    if consistency == IntelligencePanelConsistency.CONDITIONAL:
        return IntelligencePanelReadiness.CONDITIONALLY_READY

    return IntelligencePanelReadiness.READY


def build_intelligence_panel_assessment(
    request: IntelligencePanelRequest,
    items: Optional[List[IntelligencePanelItem]] = None,
    requirements: Optional[IntelligencePanelRequirements] = None,
) -> IntelligencePanelAssessment:
    normalized_request = normalize_intelligence_panel_request(request)

    panel_items = list(items or [])

    panel_requirements = (
        requirements
        if isinstance(
            requirements,
            IntelligencePanelRequirements,
        )
        else build_intelligence_panel_requirements()
    )

    data_state = evaluate_intelligence_panel_data_state(
        normalized_request,
        panel_items,
        panel_requirements,
    )

    consistency = evaluate_intelligence_panel_consistency(
        normalized_request,
        panel_items,
    )

    completeness = evaluate_intelligence_panel_completeness(
        normalized_request,
        panel_items,
        panel_requirements,
    )

    freshness = evaluate_intelligence_panel_freshness(
        panel_items,
        panel_requirements.maximum_age_seconds,
    )

    confidence = evaluate_intelligence_panel_confidence(
        panel_items,
    )

    quality = evaluate_intelligence_panel_quality(
        panel_items,
        freshness,
        completeness,
    )

    readiness = evaluate_intelligence_panel_readiness(
        data_state=data_state,
        consistency=consistency,
        completeness=completeness,
        quality=quality,
        confidence=confidence,
        requirements=panel_requirements,
    )

    warnings: List[str] = []
    errors: List[str] = []

    if data_state == IntelligencePanelDataState.PARTIAL:
        warnings.append("intelligence_data_partial")

    if consistency == IntelligencePanelConsistency.CONDITIONAL:
        warnings.append("intelligence_consistency_conditional")

    if freshness < 1.0:
        warnings.append("intelligence_freshness_degraded")

    if confidence < panel_requirements.minimum_confidence:
        warnings.append("intelligence_confidence_below_requirement")

    if data_state == IntelligencePanelDataState.INVALID:
        errors.append("intelligence_data_invalid")

    if consistency == IntelligencePanelConsistency.INCONSISTENT:
        errors.append("intelligence_data_inconsistent")

    return IntelligencePanelAssessment(
        data_state=data_state,
        consistency=consistency,
        readiness=readiness,
        completeness=max(0.0, min(1.0, completeness)),
        quality=max(0.0, min(1.0, quality)),
        confidence=max(0.0, min(1.0, confidence)),
        freshness=max(0.0, min(1.0, freshness)),
        source_quality=(
            sum(
                1.0
                for item in panel_items
                if isinstance(item, IntelligencePanelItem)
                and _ip_text(item.source)
            ) / len(panel_items)
            if panel_items
            else 0.0
        ),
        item_count=len(panel_items),
        valid_item_count=sum(
            1
            for item in panel_items
            if isinstance(item, IntelligencePanelItem)
            and item.status not in (
                IntelligencePanelStatus.INVALID,
                IntelligencePanelStatus.ERROR,
            )
        ),
        warnings=warnings,
        errors=errors,
        assessed_at=datetime.utcnow(),
    )
# ============================================================
# ROBOMLM_PLUS
# app/terminal/intelligence_panel.py
# PART 3 / 5
# Intelligence Panel Resolution + Presentation
# ============================================================


class IntelligencePanelDecision(str, Enum):
    ALLOW = "ALLOW"
    ALLOW_WITH_RESTRICTION = "ALLOW_WITH_RESTRICTION"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCK = "BLOCK"


class IntelligencePanelResolutionStatus(str, Enum):
    RESOLVED = "RESOLVED"
    CONDITIONAL = "CONDITIONAL"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"


@dataclass
class IntelligencePanelResolutionRules:
    allow_ready: bool = True
    allow_conditional: bool = True
    allow_restricted: bool = True
    require_review_on_low_quality: bool = True
    minimum_quality: float = 0.50
    minimum_confidence: float = 0.0
    block_on_invalid: bool = True
    block_on_inconsistent: bool = True


@dataclass
class IntelligencePanelPresentation:
    title: str = "Intelligence"
    subtitle: str = ""
    status: IntelligencePanelStatus = IntelligencePanelStatus.UNKNOWN
    readiness: IntelligencePanelReadiness = IntelligencePanelReadiness.NOT_READY
    headline: str = ""
    items: List[IntelligencePanelItem] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntelligencePanelResult:
    decision: IntelligencePanelDecision = IntelligencePanelDecision.BLOCK
    resolution_status: IntelligencePanelResolutionStatus = (
        IntelligencePanelResolutionStatus.BLOCKED
    )
    assessment: Optional[IntelligencePanelAssessment] = None
    presentation: Optional[IntelligencePanelPresentation] = None
    restrictions: List[str] = field(default_factory=list)
    flags: List[str] = field(default_factory=list)
    resolved_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class IntelligencePanelSourceMap:
    intelligence_panel_engine: str = INTELLIGENCE_PANEL_ENGINE
    intelligence_source: str = "app.intelligence"
    evidence_source: str = "app.intelligence.evidence"
    market_context_source: str = "app.intelligence.market_context"
    decision_source: str = "app.intelligence.decision"
    memory_source: str = "app.intelligence.memory"
    risk_source: str = "app.intelligence.risk"
    cas_source: str = "app.cas"
    metadata: Dict[str, Any] = field(default_factory=dict)


def build_intelligence_panel_resolution_rules(
    allow_ready: bool = True,
    allow_conditional: bool = True,
    allow_restricted: bool = True,
    require_review_on_low_quality: bool = True,
    minimum_quality: float = 0.50,
    minimum_confidence: float = 0.0,
    block_on_invalid: bool = True,
    block_on_inconsistent: bool = True,
) -> IntelligencePanelResolutionRules:
    return IntelligencePanelResolutionRules(
        allow_ready=bool(allow_ready),
        allow_conditional=bool(allow_conditional),
        allow_restricted=bool(allow_restricted),
        require_review_on_low_quality=bool(
            require_review_on_low_quality
        ),
        minimum_quality=max(
            0.0,
            min(1.0, _ip_number(minimum_quality, 0.50)),
        ),
        minimum_confidence=max(
            0.0,
            min(1.0, _ip_number(minimum_confidence)),
        ),
        block_on_invalid=bool(block_on_invalid),
        block_on_inconsistent=bool(block_on_inconsistent),
    )


def build_intelligence_panel_source_map(
    metadata: Optional[Dict[str, Any]] = None,
) -> IntelligencePanelSourceMap:
    return IntelligencePanelSourceMap(
        intelligence_panel_engine=INTELLIGENCE_PANEL_ENGINE,
        intelligence_source="app.intelligence",
        evidence_source="app.intelligence.evidence",
        market_context_source="app.intelligence.market_context",
        decision_source="app.intelligence.decision",
        memory_source="app.intelligence.memory",
        risk_source="app.intelligence.risk",
        cas_source="app.cas",
        metadata=dict(metadata or {}),
    )


def collect_intelligence_panel_resolution_flags(
    assessment: IntelligencePanelAssessment,
) -> List[str]:
    flags: List[str] = []

    if assessment.data_state == IntelligencePanelDataState.PARTIAL:
        flags.append("DATA_PARTIAL")

    if assessment.data_state == IntelligencePanelDataState.MISSING:
        flags.append("DATA_MISSING")

    if assessment.data_state == IntelligencePanelDataState.INVALID:
        flags.append("DATA_INVALID")

    if (
        assessment.consistency
        == IntelligencePanelConsistency.CONDITIONAL
    ):
        flags.append("CONSISTENCY_CONDITIONAL")

    if (
        assessment.consistency
        == IntelligencePanelConsistency.INCONSISTENT
    ):
        flags.append("CONSISTENCY_INCONSISTENT")

    if assessment.freshness < 1.0:
        flags.append("FRESHNESS_DEGRADED")

    if assessment.quality < 0.50:
        flags.append("QUALITY_LOW")

    if assessment.errors:
        flags.append("ASSESSMENT_ERRORS")

    if assessment.warnings:
        flags.append("ASSESSMENT_WARNINGS")

    return list(dict.fromkeys(flags))


def collect_intelligence_panel_restrictions(
    assessment: IntelligencePanelAssessment,
    rules: IntelligencePanelResolutionRules,
) -> List[str]:
    restrictions: List[str] = []

    if assessment.data_state == IntelligencePanelDataState.PARTIAL:
        restrictions.append("PARTIAL_INTELLIGENCE_DATA")

    if (
        assessment.consistency
        == IntelligencePanelConsistency.CONDITIONAL
    ):
        restrictions.append("CONDITIONAL_INTELLIGENCE_CONTEXT")

    if assessment.freshness < 1.0:
        restrictions.append("STALE_OR_DEGRADED_INTELLIGENCE")

    if assessment.quality < rules.minimum_quality:
        restrictions.append("LOW_INTELLIGENCE_PRESENTATION_QUALITY")

    if assessment.confidence < rules.minimum_confidence:
        restrictions.append("LOW_UPSTREAM_CONFIDENCE")

    return list(dict.fromkeys(restrictions))


def build_intelligence_panel_presentation(
    request: IntelligencePanelRequest,
    items: Optional[List[IntelligencePanelItem]] = None,
    assessment: Optional[IntelligencePanelAssessment] = None,
) -> IntelligencePanelPresentation:
    panel_items = list(items or [])

    current_assessment = assessment or build_intelligence_panel_assessment(
        request,
        panel_items,
    )

    status = IntelligencePanelStatus.UNKNOWN

    if current_assessment.errors:
        status = IntelligencePanelStatus.INVALID
    elif (
        current_assessment.readiness
        == IntelligencePanelReadiness.READY
    ):
        status = IntelligencePanelStatus.READY
    elif (
        current_assessment.readiness
        == IntelligencePanelReadiness.CONDITIONALLY_READY
    ):
        status = IntelligencePanelStatus.PARTIAL
    elif (
        current_assessment.readiness
        == IntelligencePanelReadiness.BLOCKED
    ):
        status = IntelligencePanelStatus.INVALID
    else:
        status = IntelligencePanelStatus.PARTIAL

    symbol = _ip_text(request.symbol)
    instrument = _ip_text(request.instrument)

    subtitle_parts = [
        value
        for value in (
            instrument,
            symbol,
            _ip_text(request.timeframe),
            _ip_text(request.market_phase),
        )
        if value
    ]

    subtitle = " • ".join(subtitle_parts)

    if status == IntelligencePanelStatus.READY:
        headline = "Intelligence context ready"
    elif status == IntelligencePanelStatus.PARTIAL:
        headline = "Intelligence context partially available"
    elif status == IntelligencePanelStatus.INVALID:
        headline = "Intelligence context requires review"
    else:
        headline = "Intelligence context unavailable"

    return IntelligencePanelPresentation(
        title="Intelligence",
        subtitle=subtitle,
        status=status,
        readiness=current_assessment.readiness,
        headline=headline,
        items=panel_items,
        warnings=list(current_assessment.warnings),
        errors=list(current_assessment.errors),
        metadata={
            "market": _ip_text(request.market),
            "instrument": instrument,
            "symbol": symbol,
            "timeframe": _ip_text(request.timeframe),
            "session": _ip_text(request.session),
            "market_phase": _ip_text(request.market_phase),
            "mode": _ip_enum(
                request.mode,
                IntelligencePanelMode,
                IntelligencePanelMode.UNKNOWN,
            ).value,
            "engine": INTELLIGENCE_PANEL_ENGINE,
            "version": INTELLIGENCE_PANEL_VERSION,
        },
    )


def resolve_intelligence_panel(
    assessment: IntelligencePanelAssessment,
    presentation: Optional[IntelligencePanelPresentation] = None,
    rules: Optional[IntelligencePanelResolutionRules] = None,
) -> IntelligencePanelResult:
    resolution_rules = (
        rules
        if isinstance(
            rules,
            IntelligencePanelResolutionRules,
        )
        else build_intelligence_panel_resolution_rules()
    )

    current_presentation = presentation

    flags = collect_intelligence_panel_resolution_flags(
        assessment
    )

    restrictions = collect_intelligence_panel_restrictions(
        assessment,
        resolution_rules,
    )

    if (
        resolution_rules.block_on_invalid
        and assessment.data_state
        == IntelligencePanelDataState.INVALID
    ):
        return IntelligencePanelResult(
            decision=IntelligencePanelDecision.BLOCK,
            resolution_status=(
                IntelligencePanelResolutionStatus.BLOCKED
            ),
            assessment=assessment,
            presentation=current_presentation,
            restrictions=restrictions,
            flags=flags,
            resolved_at=datetime.utcnow(),
        )

    if (
        resolution_rules.block_on_inconsistent
        and assessment.consistency
        == IntelligencePanelConsistency.INCONSISTENT
    ):
        return IntelligencePanelResult(
            decision=IntelligencePanelDecision.BLOCK,
            resolution_status=(
                IntelligencePanelResolutionStatus.BLOCKED
            ),
            assessment=assessment,
            presentation=current_presentation,
            restrictions=restrictions,
            flags=flags,
            resolved_at=datetime.utcnow(),
        )

    if (
        assessment.readiness
        == IntelligencePanelReadiness.BLOCKED
    ):
        return IntelligencePanelResult(
            decision=IntelligencePanelDecision.BLOCK,
            resolution_status=(
                IntelligencePanelResolutionStatus.BLOCKED
            ),
            assessment=assessment,
            presentation=current_presentation,
            restrictions=restrictions,
            flags=flags,
            resolved_at=datetime.utcnow(),
        )

    if (
        assessment.readiness
        == IntelligencePanelReadiness.NOT_READY
    ):
        return IntelligencePanelResult(
            decision=IntelligencePanelDecision.REVIEW_REQUIRED,
            resolution_status=(
                IntelligencePanelResolutionStatus.REVIEW_REQUIRED
            ),
            assessment=assessment,
            presentation=current_presentation,
            restrictions=restrictions,
            flags=flags,
            resolved_at=datetime.utcnow(),
        )

    if (
        resolution_rules.require_review_on_low_quality
        and assessment.quality
        < resolution_rules.minimum_quality
    ):
        return IntelligencePanelResult(
            decision=IntelligencePanelDecision.REVIEW_REQUIRED,
            resolution_status=(
                IntelligencePanelResolutionStatus.REVIEW_REQUIRED
            ),
            assessment=assessment,
            presentation=current_presentation,
            restrictions=restrictions,
            flags=flags,
            resolved_at=datetime.utcnow(),
        )

    if (
        assessment.readiness
        == IntelligencePanelReadiness.CONDITIONALLY_READY
    ):
        if not resolution_rules.allow_conditional:
            return IntelligencePanelResult(
                decision=IntelligencePanelDecision.REVIEW_REQUIRED,
                resolution_status=(
                    IntelligencePanelResolutionStatus.REVIEW_REQUIRED
                ),
                assessment=assessment,
                presentation=current_presentation,
                restrictions=restrictions,
                flags=flags,
                resolved_at=datetime.utcnow(),
            )

        return IntelligencePanelResult(
            decision=(
                IntelligencePanelDecision.ALLOW_WITH_RESTRICTION
                if restrictions
                else IntelligencePanelDecision.ALLOW
            ),
            resolution_status=(
                IntelligencePanelResolutionStatus.CONDITIONAL
            ),
            assessment=assessment,
            presentation=current_presentation,
            restrictions=restrictions,
            flags=flags,
            resolved_at=datetime.utcnow(),
        )

    if assessment.readiness == IntelligencePanelReadiness.READY:
        if restrictions:
            if not resolution_rules.allow_restricted:
                return IntelligencePanelResult(
                    decision=(
                        IntelligencePanelDecision.REVIEW_REQUIRED
                    ),
                    resolution_status=(
                        IntelligencePanelResolutionStatus.REVIEW_REQUIRED
                    ),
                    assessment=assessment,
                    presentation=current_presentation,
                    restrictions=restrictions,
                    flags=flags,
                    resolved_at=datetime.utcnow(),
                )

            return IntelligencePanelResult(
                decision=(
                    IntelligencePanelDecision.ALLOW_WITH_RESTRICTION
                ),
                resolution_status=(
                    IntelligencePanelResolutionStatus.RESOLVED
                ),
                assessment=assessment,
                presentation=current_presentation,
                restrictions=restrictions,
                flags=flags,
                resolved_at=datetime.utcnow(),
            )

        if resolution_rules.allow_ready:
            return IntelligencePanelResult(
                decision=IntelligencePanelDecision.ALLOW,
                resolution_status=(
                    IntelligencePanelResolutionStatus.RESOLVED
                ),
                assessment=assessment,
                presentation=current_presentation,
                restrictions=[],
                flags=flags,
                resolved_at=datetime.utcnow(),
            )

    return IntelligencePanelResult(
        decision=IntelligencePanelDecision.REVIEW_REQUIRED,
        resolution_status=(
            IntelligencePanelResolutionStatus.REVIEW_REQUIRED
        ),
        assessment=assessment,
        presentation=current_presentation,
        restrictions=restrictions,
        flags=flags,
        resolved_at=datetime.utcnow(),
    )


def validate_intelligence_panel_result(
    result: IntelligencePanelResult,
) -> bool:
    if not isinstance(result, IntelligencePanelResult):
        return False

    if result.assessment is None:
        return False

    valid_decisions = {
        IntelligencePanelDecision.ALLOW,
        IntelligencePanelDecision.ALLOW_WITH_RESTRICTION,
        IntelligencePanelDecision.REVIEW_REQUIRED,
        IntelligencePanelDecision.BLOCK,
    }

    valid_statuses = {
        IntelligencePanelResolutionStatus.RESOLVED,
        IntelligencePanelResolutionStatus.CONDITIONAL,
        IntelligencePanelResolutionStatus.REVIEW_REQUIRED,
        IntelligencePanelResolutionStatus.BLOCKED,
    }

    return (
        result.decision in valid_decisions
        and result.resolution_status in valid_statuses
    )


def validate_intelligence_panel_result_authority(
    result: IntelligencePanelResult,
) -> bool:
    if not validate_intelligence_panel_result(result):
        return False

    boundary = intelligence_panel_authority_boundary()

    forbidden = (
        "market_data_authority",
        "evidence_generation_authority",
        "intelligence_generation_authority",
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

    return all(boundary.get(key) is False for key in forbidden)
# ============================================================
# ROBOMLM_PLUS
# app/terminal/intelligence_panel.py
# PART 4 / 5
# Intelligence Panel Registry + Service
# ============================================================


@dataclass
class IntelligencePanelRegistryEntry:
    key: str = ""
    reference: Optional[IntelligencePanelReference] = None
    assessment: Optional[IntelligencePanelAssessment] = None
    presentation: Optional[IntelligencePanelPresentation] = None
    result: Optional[IntelligencePanelResult] = None
    source_map: Optional[IntelligencePanelSourceMap] = None
    registered_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class IntelligencePanelRegistrySnapshot:
    engine: str = INTELLIGENCE_PANEL_ENGINE
    version: str = INTELLIGENCE_PANEL_VERSION
    entries: List[IntelligencePanelRegistryEntry] = field(
        default_factory=list
    )
    generated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class IntelligencePanelServiceResult:
    success: bool = False
    request_id: str = ""
    reference: Optional[IntelligencePanelReference] = None
    assessment: Optional[IntelligencePanelAssessment] = None
    presentation: Optional[IntelligencePanelPresentation] = None
    result: Optional[IntelligencePanelResult] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)


def _intelligence_panel_registry_key(
    request: IntelligencePanelRequest,
) -> str:
    parts = (
        _ip_text(request.market),
        _ip_text(request.instrument),
        _ip_text(request.symbol),
        _ip_text(request.contract),
        _ip_text(request.timeframe),
    )

    return ":".join(
        value.upper() if value else "-"
        for value in parts
    )


class IntelligencePanelRegistry:
    def __init__(self) -> None:
        self._entries: Dict[str, IntelligencePanelRegistryEntry] = {}

    def exists(self, key: str) -> bool:
        return _ip_text(key) in self._entries

    def get(
        self,
        key: str,
    ) -> Optional[IntelligencePanelRegistryEntry]:
        return self._entries.get(_ip_text(key))

    def get_entry(
        self,
        request: IntelligencePanelRequest,
    ) -> Optional[IntelligencePanelRegistryEntry]:
        return self.get(
            _intelligence_panel_registry_key(request)
        )

    def add(
        self,
        request: IntelligencePanelRequest,
        reference: IntelligencePanelReference,
        assessment: Optional[IntelligencePanelAssessment] = None,
        presentation: Optional[IntelligencePanelPresentation] = None,
        result: Optional[IntelligencePanelResult] = None,
        source_map: Optional[IntelligencePanelSourceMap] = None,
    ) -> IntelligencePanelRegistryEntry:
        key = _intelligence_panel_registry_key(request)

        if key in self._entries:
            raise ValueError(
                f"intelligence_panel_registry_key_exists:{key}"
            )

        now = datetime.utcnow()

        entry = IntelligencePanelRegistryEntry(
            key=key,
            reference=reference,
            assessment=assessment,
            presentation=presentation,
            result=result,
            source_map=source_map,
            registered_at=now,
            updated_at=now,
        )

        self._entries[key] = entry
        return entry

    def replace(
        self,
        request: IntelligencePanelRequest,
        reference: IntelligencePanelReference,
        assessment: Optional[IntelligencePanelAssessment] = None,
        presentation: Optional[IntelligencePanelPresentation] = None,
        result: Optional[IntelligencePanelResult] = None,
        source_map: Optional[IntelligencePanelSourceMap] = None,
    ) -> IntelligencePanelRegistryEntry:
        key = _intelligence_panel_registry_key(request)
        now = datetime.utcnow()

        existing = self._entries.get(key)

        entry = IntelligencePanelRegistryEntry(
            key=key,
            reference=reference,
            assessment=assessment,
            presentation=presentation,
            result=result,
            source_map=source_map,
            registered_at=(
                existing.registered_at
                if existing is not None
                else now
            ),
            updated_at=now,
        )

        self._entries[key] = entry
        return entry

    def remove(
        self,
        request: IntelligencePanelRequest,
    ) -> bool:
        key = _intelligence_panel_registry_key(request)

        if key not in self._entries:
            return False

        del self._entries[key]
        return True

    def list_references(
        self,
    ) -> List[IntelligencePanelReference]:
        return [
            entry.reference
            for entry in self._entries.values()
            if entry.reference is not None
        ]

    def snapshot(self) -> IntelligencePanelRegistrySnapshot:
        return IntelligencePanelRegistrySnapshot(
            engine=INTELLIGENCE_PANEL_ENGINE,
            version=INTELLIGENCE_PANEL_VERSION,
            entries=list(self._entries.values()),
            generated_at=datetime.utcnow(),
        )

    def count(self) -> int:
        return len(self._entries)


def validate_intelligence_panel_registry(
    registry: IntelligencePanelRegistry,
) -> bool:
    if not isinstance(registry, IntelligencePanelRegistry):
        return False

    for key, entry in registry._entries.items():
        if not _ip_text(key):
            return False

        if not isinstance(
            entry,
            IntelligencePanelRegistryEntry,
        ):
            return False

        if entry.reference is None:
            return False

    return True


def intelligence_panel_registry_health(
    registry: IntelligencePanelRegistry,
) -> Dict[str, Any]:
    valid = validate_intelligence_panel_registry(registry)

    entries = list(registry._entries.values())

    references = sum(
        1
        for entry in entries
        if entry.reference is not None
    )

    assessments = sum(
        1
        for entry in entries
        if entry.assessment is not None
    )

    presentations = sum(
        1
        for entry in entries
        if entry.presentation is not None
    )

    results = sum(
        1
        for entry in entries
        if entry.result is not None
    )

    return {
        "engine": INTELLIGENCE_PANEL_ENGINE,
        "version": INTELLIGENCE_PANEL_VERSION,
        "valid": valid,
        "entry_count": len(entries),
        "reference_count": references,
        "assessment_count": assessments,
        "presentation_count": presentations,
        "result_count": results,
        "healthy": (
            valid
            and references == len(entries)
        ),
        "checked_at": datetime.utcnow(),
    }


class IntelligencePanelService:
    def __init__(
        self,
        registry: Optional[IntelligencePanelRegistry] = None,
    ) -> None:
        self.registry = (
            registry
            if isinstance(
                registry,
                IntelligencePanelRegistry,
            )
            else IntelligencePanelRegistry()
        )

    def resolve(
        self,
        request: IntelligencePanelRequest,
        items: Optional[List[IntelligencePanelItem]] = None,
        requirements: Optional[IntelligencePanelRequirements] = None,
        rules: Optional[IntelligencePanelResolutionRules] = None,
    ) -> IntelligencePanelServiceResult:
        normalized = normalize_intelligence_panel_request(
            request
        )

        validation = validate_intelligence_panel_request(
            normalized
        )

        if not validation.valid:
            return IntelligencePanelServiceResult(
                success=False,
                request_id=normalized.request_id,
                errors=list(validation.errors),
                warnings=list(validation.warnings),
                generated_at=datetime.utcnow(),
            )

        panel_items = list(items or [])

        assessment = build_intelligence_panel_assessment(
            normalized,
            panel_items,
            requirements,
        )

        presentation = build_intelligence_panel_presentation(
            normalized,
            panel_items,
            assessment,
        )

        result = resolve_intelligence_panel(
            assessment,
            presentation,
            rules,
        )

        reference = build_intelligence_panel_reference(
            normalized,
            intelligence_count=len(panel_items),
            status=presentation.status,
            source=INTELLIGENCE_PANEL_ENGINE,
        )

        source_map = build_intelligence_panel_source_map()

        self.registry.replace(
            normalized,
            reference=reference,
            assessment=assessment,
            presentation=presentation,
            result=result,
            source_map=source_map,
        )

        return IntelligencePanelServiceResult(
            success=validate_intelligence_panel_result(result),
            request_id=normalized.request_id,
            reference=reference,
            assessment=assessment,
            presentation=presentation,
            result=result,
            errors=list(assessment.errors),
            warnings=list(assessment.warnings),
            generated_at=datetime.utcnow(),
        )

    def assess(
        self,
        request: IntelligencePanelRequest,
        items: Optional[List[IntelligencePanelItem]] = None,
        requirements: Optional[IntelligencePanelRequirements] = None,
    ) -> IntelligencePanelAssessment:
        return build_intelligence_panel_assessment(
            normalize_intelligence_panel_request(request),
            list(items or []),
            requirements,
        )

    def register(
        self,
        request: IntelligencePanelRequest,
        reference: IntelligencePanelReference,
        assessment: Optional[IntelligencePanelAssessment] = None,
        presentation: Optional[IntelligencePanelPresentation] = None,
        result: Optional[IntelligencePanelResult] = None,
        source_map: Optional[IntelligencePanelSourceMap] = None,
    ) -> IntelligencePanelRegistryEntry:
        normalized = normalize_intelligence_panel_request(
            request
        )

        return self.registry.replace(
            normalized,
            reference=reference,
            assessment=assessment,
            presentation=presentation,
            result=result,
            source_map=source_map,
        )

    def get(
        self,
        request: IntelligencePanelRequest,
    ) -> Optional[IntelligencePanelRegistryEntry]:
        normalized = normalize_intelligence_panel_request(
            request
        )
        return self.registry.get_entry(normalized)

    def list_references(
        self,
    ) -> List[IntelligencePanelReference]:
        return self.registry.list_references()

    def snapshot(self) -> IntelligencePanelRegistrySnapshot:
        return self.registry.snapshot()

    def health(self) -> Dict[str, Any]:
        return intelligence_panel_registry_health(
            self.registry
        )

    def integrity(self) -> bool:
        return validate_intelligence_panel_registry(
            self.registry
        )

    def info(self) -> Dict[str, Any]:
        return {
            "engine": INTELLIGENCE_PANEL_ENGINE,
            "version": INTELLIGENCE_PANEL_VERSION,
            "registry_count": self.registry.count(),
            "authority_boundary_valid": (
                validate_intelligence_panel_authority_boundary()
            ),
            "registry_integrity": self.integrity(),
        }


_INTELLIGENCE_PANEL_SERVICE = IntelligencePanelService()


def get_intelligence_panel_service() -> IntelligencePanelService:
    return _INTELLIGENCE_PANEL_SERVICE


def resolve_terminal_intelligence(
    request: IntelligencePanelRequest,
    items: Optional[List[IntelligencePanelItem]] = None,
    requirements: Optional[IntelligencePanelRequirements] = None,
    rules: Optional[IntelligencePanelResolutionRules] = None,
) -> IntelligencePanelServiceResult:
    return _INTELLIGENCE_PANEL_SERVICE.resolve(
        request=request,
        items=items,
        requirements=requirements,
        rules=rules,
    )


def get_terminal_intelligence_reference(
    request: IntelligencePanelRequest,
) -> Optional[IntelligencePanelReference]:
    entry = _INTELLIGENCE_PANEL_SERVICE.get(request)
    return entry.reference if entry else None


def terminal_intelligence_panel_snapshot() -> IntelligencePanelRegistrySnapshot:
    return _INTELLIGENCE_PANEL_SERVICE.snapshot()


def terminal_intelligence_panel_count() -> int:
    return _INTELLIGENCE_PANEL_SERVICE.registry.count()


def terminal_intelligence_panel_health() -> Dict[str, Any]:
    return _INTELLIGENCE_PANEL_SERVICE.health()


def terminal_intelligence_panel_integrity() -> bool:
    return _INTELLIGENCE_PANEL_SERVICE.integrity()


def terminal_intelligence_panel_operational_check() -> Dict[str, Any]:
    service = get_intelligence_panel_service()

    return {
        "engine": INTELLIGENCE_PANEL_ENGINE,
        "version": INTELLIGENCE_PANEL_VERSION,
        "authority_boundary_valid": (
            validate_intelligence_panel_authority_boundary()
        ),
        "registry_integrity": service.integrity(),
        "health": service.health(),
        "operational": (
            validate_intelligence_panel_authority_boundary()
            and service.integrity()
        ),
        "checked_at": datetime.utcnow(),
    }


def terminal_intelligence_panel_service_info() -> Dict[str, Any]:
    return _INTELLIGENCE_PANEL_SERVICE.info()
# ============================================================
# ROBOMLM_PLUS
# app/terminal/intelligence_panel.py
# PART 5 / 5
# Serialization + Integrity + Summary + Exports
# ============================================================


def _ip_serialize_datetime(value: Any) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    return _ip_timestamp(value).isoformat()


def _ip_serialize_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            str(key): _ip_serialize_value(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            _ip_serialize_value(item)
            for item in value
        ]

    return value


def serialize_intelligence_panel_item(
    item: IntelligencePanelItem,
) -> Dict[str, Any]:
    return {
        "intelligence_id": _ip_text(item.intelligence_id),
        "category": item.category.value,
        "name": _ip_text(item.name),
        "value": _ip_serialize_value(item.value),
        "unit": _ip_text(item.unit),
        "interpretation": _ip_text(item.interpretation),
        "source": _ip_text(item.source),
        "source_type": item.source_type.value,
        "status": item.status.value,
        "severity": item.severity.value,
        "confidence": max(
            0.0,
            min(1.0, _ip_number(item.confidence)),
        ),
        "timestamp": _ip_serialize_datetime(item.timestamp),
        "metadata": _ip_serialize_value(item.metadata),
    }


def serialize_intelligence_panel_reference(
    reference: IntelligencePanelReference,
) -> Dict[str, Any]:
    return {
        "market": _ip_text(reference.market),
        "instrument": _ip_text(reference.instrument),
        "symbol": _ip_text(reference.symbol),
        "contract": _ip_text(reference.contract),
        "timeframe": _ip_text(reference.timeframe),
        "session": _ip_text(reference.session),
        "market_phase": _ip_text(reference.market_phase),
        "status": reference.status.value,
        "mode": reference.mode.value,
        "source": _ip_text(reference.source),
        "intelligence_count": max(
            0,
            int(reference.intelligence_count),
        ),
        "created_at": _ip_serialize_datetime(
            reference.created_at
        ),
        "updated_at": _ip_serialize_datetime(
            reference.updated_at
        ),
        "version": _ip_text(reference.version),
    }


def serialize_intelligence_panel_assessment(
    assessment: IntelligencePanelAssessment,
) -> Dict[str, Any]:
    return {
        "data_state": assessment.data_state.value,
        "consistency": assessment.consistency.value,
        "readiness": assessment.readiness.value,
        "completeness": max(
            0.0,
            min(1.0, _ip_number(assessment.completeness)),
        ),
        "quality": max(
            0.0,
            min(1.0, _ip_number(assessment.quality)),
        ),
        "confidence": max(
            0.0,
            min(1.0, _ip_number(assessment.confidence)),
        ),
        "freshness": max(
            0.0,
            min(1.0, _ip_number(assessment.freshness)),
        ),
        "source_quality": max(
            0.0,
            min(1.0, _ip_number(assessment.source_quality)),
        ),
        "item_count": max(
            0,
            int(assessment.item_count),
        ),
        "valid_item_count": max(
            0,
            int(assessment.valid_item_count),
        ),
        "warnings": list(assessment.warnings),
        "errors": list(assessment.errors),
        "assessed_at": _ip_serialize_datetime(
            assessment.assessed_at
        ),
    }


def serialize_intelligence_panel_presentation(
    presentation: IntelligencePanelPresentation,
) -> Dict[str, Any]:
    return {
        "title": _ip_text(presentation.title),
        "subtitle": _ip_text(presentation.subtitle),
        "status": presentation.status.value,
        "readiness": presentation.readiness.value,
        "headline": _ip_text(presentation.headline),
        "items": [
            serialize_intelligence_panel_item(item)
            for item in presentation.items
        ],
        "warnings": list(presentation.warnings),
        "errors": list(presentation.errors),
        "metadata": _ip_serialize_value(
            presentation.metadata
        ),
    }


def serialize_intelligence_panel_result(
    result: IntelligencePanelResult,
) -> Dict[str, Any]:
    return {
        "decision": result.decision.value,
        "resolution_status": result.resolution_status.value,
        "assessment": (
            serialize_intelligence_panel_assessment(
                result.assessment
            )
            if result.assessment is not None
            else None
        ),
        "presentation": (
            serialize_intelligence_panel_presentation(
                result.presentation
            )
            if result.presentation is not None
            else None
        ),
        "restrictions": list(result.restrictions),
        "flags": list(result.flags),
        "resolved_at": _ip_serialize_datetime(
            result.resolved_at
        ),
    }


def serialize_intelligence_panel_service_result(
    service_result: IntelligencePanelServiceResult,
) -> Dict[str, Any]:
    return {
        "success": bool(service_result.success),
        "request_id": _ip_text(service_result.request_id),
        "reference": (
            serialize_intelligence_panel_reference(
                service_result.reference
            )
            if service_result.reference is not None
            else None
        ),
        "assessment": (
            serialize_intelligence_panel_assessment(
                service_result.assessment
            )
            if service_result.assessment is not None
            else None
        ),
        "presentation": (
            serialize_intelligence_panel_presentation(
                service_result.presentation
            )
            if service_result.presentation is not None
            else None
        ),
        "result": (
            serialize_intelligence_panel_result(
                service_result.result
            )
            if service_result.result is not None
            else None
        ),
        "errors": list(service_result.errors),
        "warnings": list(service_result.warnings),
        "generated_at": _ip_serialize_datetime(
            service_result.generated_at
        ),
    }


def serialize_intelligence_panel_source_map(
    source_map: IntelligencePanelSourceMap,
) -> Dict[str, Any]:
    return {
        "intelligence_panel_engine": _ip_text(
            source_map.intelligence_panel_engine
        ),
        "intelligence_source": _ip_text(
            source_map.intelligence_source
        ),
        "evidence_source": _ip_text(
            source_map.evidence_source
        ),
        "market_context_source": _ip_text(
            source_map.market_context_source
        ),
        "decision_source": _ip_text(
            source_map.decision_source
        ),
        "memory_source": _ip_text(
            source_map.memory_source
        ),
        "risk_source": _ip_text(
            source_map.risk_source
        ),
        "cas_source": _ip_text(
            source_map.cas_source
        ),
        "metadata": _ip_serialize_value(
            source_map.metadata
        ),
    }


def serialize_intelligence_panel_snapshot(
    snapshot: IntelligencePanelRegistrySnapshot,
) -> Dict[str, Any]:
    return {
        "engine": _ip_text(snapshot.engine),
        "version": _ip_text(snapshot.version),
        "entries": [
            {
                "key": _ip_text(entry.key),
                "reference": (
                    serialize_intelligence_panel_reference(
                        entry.reference
                    )
                    if entry.reference is not None
                    else None
                ),
                "assessment": (
                    serialize_intelligence_panel_assessment(
                        entry.assessment
                    )
                    if entry.assessment is not None
                    else None
                ),
                "presentation": (
                    serialize_intelligence_panel_presentation(
                        entry.presentation
                    )
                    if entry.presentation is not None
                    else None
                ),
                "result": (
                    serialize_intelligence_panel_result(
                        entry.result
                    )
                    if entry.result is not None
                    else None
                ),
                "source_map": (
                    serialize_intelligence_panel_source_map(
                        entry.source_map
                    )
                    if entry.source_map is not None
                    else None
                ),
                "registered_at": _ip_serialize_datetime(
                    entry.registered_at
                ),
                "updated_at": _ip_serialize_datetime(
                    entry.updated_at
                ),
            }
            for entry in snapshot.entries
        ],
        "generated_at": _ip_serialize_datetime(
            snapshot.generated_at
        ),
    }


def validate_intelligence_panel_item_integrity(
    item: IntelligencePanelItem,
) -> bool:
    if not isinstance(item, IntelligencePanelItem):
        return False

    if not _ip_text(item.intelligence_id):
        return False

    if not _ip_text(item.name):
        return False

    if not isinstance(
        item.category,
        IntelligencePanelCategory,
    ):
        return False

    if not isinstance(
        item.source_type,
        IntelligencePanelSourceType,
    ):
        return False

    if not isinstance(
        item.status,
        IntelligencePanelStatus,
    ):
        return False

    if not isinstance(
        item.severity,
        IntelligencePanelSeverity,
    ):
        return False

    confidence = _ip_number(item.confidence, -1.0)

    return 0.0 <= confidence <= 1.0


def validate_intelligence_panel_reference_integrity(
    reference: IntelligencePanelReference,
) -> bool:
    if not isinstance(
        reference,
        IntelligencePanelReference,
    ):
        return False

    if not _ip_text(reference.market):
        return False

    if not _ip_text(reference.instrument):
        return False

    if not _ip_text(reference.symbol):
        return False

    if not isinstance(
        reference.status,
        IntelligencePanelStatus,
    ):
        return False

    if not isinstance(
        reference.mode,
        IntelligencePanelMode,
    ):
        return False

    if reference.intelligence_count < 0:
        return False

    if not _ip_text(reference.version):
        return False

    return True


def validate_intelligence_panel_assessment_integrity(
    assessment: IntelligencePanelAssessment,
) -> bool:
    if not isinstance(
        assessment,
        IntelligencePanelAssessment,
    ):
        return False

    bounded_values = (
        assessment.completeness,
        assessment.quality,
        assessment.confidence,
        assessment.freshness,
        assessment.source_quality,
    )

    if any(
        not 0.0 <= _ip_number(value, -1.0) <= 1.0
        for value in bounded_values
    ):
        return False

    if assessment.item_count < 0:
        return False

    if assessment.valid_item_count < 0:
        return False

    if assessment.valid_item_count > assessment.item_count:
        return False

    return (
        isinstance(
            assessment.data_state,
            IntelligencePanelDataState,
        )
        and isinstance(
            assessment.consistency,
            IntelligencePanelConsistency,
        )
        and isinstance(
            assessment.readiness,
            IntelligencePanelReadiness,
        )
    )


def validate_intelligence_panel_presentation_integrity(
    presentation: IntelligencePanelPresentation,
) -> bool:
    if not isinstance(
        presentation,
        IntelligencePanelPresentation,
    ):
        return False

    if not _ip_text(presentation.title):
        return False

    if not isinstance(
        presentation.status,
        IntelligencePanelStatus,
    ):
        return False

    if not isinstance(
        presentation.readiness,
        IntelligencePanelReadiness,
    ):
        return False

    return all(
        isinstance(item, IntelligencePanelItem)
        and validate_intelligence_panel_item_integrity(item)
        for item in presentation.items
    )


def validate_intelligence_panel_result_integrity(
    result: IntelligencePanelResult,
) -> bool:
    if not validate_intelligence_panel_result(result):
        return False

    if result.assessment is None:
        return False

    if not validate_intelligence_panel_assessment_integrity(
        result.assessment
    ):
        return False

    if result.presentation is not None:
        if not validate_intelligence_panel_presentation_integrity(
            result.presentation
        ):
            return False

    if result.decision == IntelligencePanelDecision.BLOCK:
        if (
            result.resolution_status
            != IntelligencePanelResolutionStatus.BLOCKED
        ):
            return False

    if result.decision == IntelligencePanelDecision.ALLOW:
        if result.resolution_status not in (
            IntelligencePanelResolutionStatus.RESOLVED,
            IntelligencePanelResolutionStatus.CONDITIONAL,
        ):
            return False

    return validate_intelligence_panel_result_authority(result)


def validate_intelligence_panel_snapshot_integrity(
    snapshot: IntelligencePanelRegistrySnapshot,
) -> bool:
    if not isinstance(
        snapshot,
        IntelligencePanelRegistrySnapshot,
    ):
        return False

    if snapshot.engine != INTELLIGENCE_PANEL_ENGINE:
        return False

    if snapshot.version != INTELLIGENCE_PANEL_VERSION:
        return False

    for entry in snapshot.entries:
        if not isinstance(
            entry,
            IntelligencePanelRegistryEntry,
        ):
            return False

        if not _ip_text(entry.key):
            return False

        if entry.reference is None:
            return False

        if not validate_intelligence_panel_reference_integrity(
            entry.reference
        ):
            return False

        if entry.assessment is not None:
            if not validate_intelligence_panel_assessment_integrity(
                entry.assessment
            ):
                return False

        if entry.presentation is not None:
            if not validate_intelligence_panel_presentation_integrity(
                entry.presentation
            ):
                return False

        if entry.result is not None:
            if not validate_intelligence_panel_result_integrity(
                entry.result
            ):
                return False

    return True


def validate_intelligence_panel_service_result_integrity(
    service_result: IntelligencePanelServiceResult,
) -> bool:
    if not isinstance(
        service_result,
        IntelligencePanelServiceResult,
    ):
        return False

    if not _ip_text(service_result.request_id):
        return False

    if service_result.success:
        if service_result.reference is None:
            return False

        if service_result.assessment is None:
            return False

        if service_result.result is None:
            return False

        if not validate_intelligence_panel_reference_integrity(
            service_result.reference
        ):
            return False

        if not validate_intelligence_panel_assessment_integrity(
            service_result.assessment
        ):
            return False

        if not validate_intelligence_panel_result_integrity(
            service_result.result
        ):
            return False

    return True


def build_intelligence_panel_summary(
    request: IntelligencePanelRequest,
    items: Optional[List[IntelligencePanelItem]] = None,
    assessment: Optional[IntelligencePanelAssessment] = None,
    result: Optional[IntelligencePanelResult] = None,
) -> Dict[str, Any]:
    panel_items = list(items or [])

    current_assessment = assessment or build_intelligence_panel_assessment(
        request,
        panel_items,
    )

    summary: Dict[str, Any] = {
        "engine": INTELLIGENCE_PANEL_ENGINE,
        "version": INTELLIGENCE_PANEL_VERSION,
        "market": _ip_text(request.market),
        "instrument": _ip_text(request.instrument),
        "symbol": _ip_text(request.symbol),
        "timeframe": _ip_text(request.timeframe),
        "item_count": len(panel_items),
        "valid_item_count": current_assessment.valid_item_count,
        "data_state": current_assessment.data_state.value,
        "consistency": current_assessment.consistency.value,
        "readiness": current_assessment.readiness.value,
        "completeness": current_assessment.completeness,
        "quality": current_assessment.quality,
        "confidence": current_assessment.confidence,
        "freshness": current_assessment.freshness,
        "warnings": list(current_assessment.warnings),
        "errors": list(current_assessment.errors),
    }

    if result is not None:
        summary["decision"] = result.decision.value
        summary["resolution_status"] = (
            result.resolution_status.value
        )
        summary["restrictions"] = list(
            result.restrictions
        )
        summary["flags"] = list(result.flags)

    return summary


__all__ = [
    # Constants
    "INTELLIGENCE_PANEL_ENGINE",
    "INTELLIGENCE_PANEL_VERSION",

    # Enums
    "IntelligencePanelStatus",
    "IntelligencePanelMode",
    "IntelligencePanelPriority",
    "IntelligencePanelSeverity",
    "IntelligencePanelSourceType",
    "IntelligencePanelContractStatus",
    "IntelligencePanelCategory",
    "IntelligencePanelDataState",
    "IntelligencePanelConsistency",
    "IntelligencePanelReadiness",
    "IntelligencePanelDecision",
    "IntelligencePanelResolutionStatus",

    # Contracts
    "IntelligencePanelRequest",
    "IntelligencePanelItem",
    "IntelligencePanelReference",
    "IntelligencePanelContractValidation",
    "IntelligencePanelRequirements",
    "IntelligencePanelAssessment",
    "IntelligencePanelResolutionRules",
    "IntelligencePanelPresentation",
    "IntelligencePanelResult",
    "IntelligencePanelSourceMap",
    "IntelligencePanelRegistryEntry",
    "IntelligencePanelRegistrySnapshot",
    "IntelligencePanelServiceResult",

    # Authority
    "intelligence_panel_authority_boundary",
    "validate_intelligence_panel_authority_boundary",

    # Request
    "normalize_intelligence_panel_request",
    "validate_intelligence_panel_request",
    "build_intelligence_panel_request",
    "build_intelligence_panel_reference",

    # Assessment
    "build_intelligence_panel_requirements",
    "evaluate_intelligence_panel_data_state",
    "evaluate_intelligence_panel_consistency",
    "evaluate_intelligence_panel_requirements",
    "evaluate_intelligence_panel_freshness",
    "evaluate_intelligence_panel_completeness",
    "evaluate_intelligence_panel_quality",
    "evaluate_intelligence_panel_confidence",
    "evaluate_intelligence_panel_readiness",
    "build_intelligence_panel_assessment",

    # Resolution
    "build_intelligence_panel_resolution_rules",
    "build_intelligence_panel_source_map",
    "collect_intelligence_panel_resolution_flags",
    "collect_intelligence_panel_restrictions",
    "build_intelligence_panel_presentation",
    "resolve_intelligence_panel",
    "validate_intelligence_panel_result",
    "validate_intelligence_panel_result_authority",

    # Registry / Service
    "IntelligencePanelRegistry",
    "validate_intelligence_panel_registry",
    "intelligence_panel_registry_health",
    "IntelligencePanelService",
    "get_intelligence_panel_service",
    "resolve_terminal_intelligence",
    "get_terminal_intelligence_reference",
    "terminal_intelligence_panel_snapshot",
    "terminal_intelligence_panel_count",
    "terminal_intelligence_panel_health",
    "terminal_intelligence_panel_integrity",
    "terminal_intelligence_panel_operational_check",
    "terminal_intelligence_panel_service_info",

    # Serialization
    "serialize_intelligence_panel_item",
    "serialize_intelligence_panel_reference",
    "serialize_intelligence_panel_assessment",
    "serialize_intelligence_panel_presentation",
    "serialize_intelligence_panel_result",
    "serialize_intelligence_panel_service_result",
    "serialize_intelligence_panel_source_map",
    "serialize_intelligence_panel_snapshot",

    # Integrity
    "validate_intelligence_panel_item_integrity",
    "validate_intelligence_panel_reference_integrity",
    "validate_intelligence_panel_assessment_integrity",
    "validate_intelligence_panel_presentation_integrity",
    "validate_intelligence_panel_result_integrity",
    "validate_intelligence_panel_snapshot_integrity",
    "validate_intelligence_panel_service_result_integrity",

    # Summary
    "build_intelligence_panel_summary",
]