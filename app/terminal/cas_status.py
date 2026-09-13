# ============================================================
# CAS STATUS — PART 1
# CONTRACTS + ENUMS + REQUEST / ITEM / REFERENCE
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


# ============================================================
# CONSTANTS
# ============================================================

CAS_STATUS_ENGINE = "ROBOMLM_TERMINAL_CAS_STATUS"
CAS_STATUS_VERSION = "1.0"


# ============================================================
# ENUMS
# ============================================================

class CASStatus(Enum):
    UNKNOWN = "UNKNOWN"
    READY = "READY"
    PARTIAL = "PARTIAL"
    STALE = "STALE"
    INVALID = "INVALID"
    ERROR = "ERROR"


class CASMode(Enum):
    PAPER = "PAPER"
    DEMO = "DEMO"
    LIVE = "LIVE"
    UNKNOWN = "UNKNOWN"


class CASPriority(Enum):
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CASSeverity(Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CASSourceType(Enum):
    CAS = "CAS"
    SUITABILITY_GATE = "SUITABILITY_GATE"
    RISK_GATE = "RISK_GATE"
    EXPOSURE_GATE = "EXPOSURE_GATE"
    POSITION_GATE = "POSITION_GATE"
    EXECUTION_SAFETY_GATE = "EXECUTION_SAFETY_GATE"
    COMPLIANCE_GATE = "COMPLIANCE_GATE"
    RESTRICTION_ENGINE = "RESTRICTION_ENGINE"
    DECISION_CORTEX = "DECISION_CORTEX"
    D13 = "D13"
    RISK = "RISK"
    EXTERNAL = "EXTERNAL"
    UNKNOWN = "UNKNOWN"


class CASContractStatus(Enum):
    CREATED = "CREATED"
    VALID = "VALID"
    INVALID = "INVALID"
    READY = "READY"


class CASCategory(Enum):
    SUITABILITY = "SUITABILITY"
    RISK = "RISK"
    EXPOSURE = "EXPOSURE"
    POSITION = "POSITION"
    EXECUTION_SAFETY = "EXECUTION_SAFETY"
    COMPLIANCE = "COMPLIANCE"
    RESTRICTION = "RESTRICTION"
    CAPITAL = "CAPITAL"
    LEVERAGE = "LEVERAGE"
    LIQUIDITY = "LIQUIDITY"
    CONCENTRATION = "CONCENTRATION"
    PORTFOLIO = "PORTFOLIO"
    SYSTEM = "SYSTEM"
    OTHER = "OTHER"


class CASGateState(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    BLOCK = "BLOCK"
    NOT_EVALUATED = "NOT_EVALUATED"
    UNKNOWN = "UNKNOWN"


class CASDecision(Enum):
    ALLOW = "ALLOW"
    ALLOW_WITH_RESTRICTION = "ALLOW_WITH_RESTRICTION"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


# ============================================================
# HELPERS
# ============================================================

def _cas_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _cas_enum(
    value: Any,
    enum_type: type[Enum],
    default: Enum,
) -> Enum:
    if isinstance(value, enum_type):
        return value

    if value is None:
        return default

    text = _cas_text(value).strip().upper()

    for member in enum_type:
        if member.value == text:
            return member

    return default


def _cas_number(
    value: Any,
    default: float = 0.0,
) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _cas_timestamp(
    value: Any,
) -> Optional[datetime]:
    if isinstance(value, datetime):
        return value

    if not value:
        return None

    try:
        return datetime.fromisoformat(
            _cas_text(value)
        )
    except (TypeError, ValueError):
        return None


# ============================================================
# REQUEST CONTRACT
# ============================================================

@dataclass
class CASStatusRequest:
    request_id: str = ""
    market: str = ""
    instrument: str = ""
    symbol: str = ""
    contract: str = ""
    timeframe: str = ""
    mode: CASMode = CASMode.UNKNOWN
    priority: CASPriority = CASPriority.NORMAL

    include_suitability: bool = True
    include_risk: bool = True
    include_exposure: bool = True
    include_position: bool = True
    include_execution_safety: bool = True
    include_compliance: bool = True
    include_restrictions: bool = True

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# CAS GATE ITEM
# ============================================================

@dataclass
class CASGateItem:
    gate_id: str = ""
    label: str = ""

    category: CASCategory = CASCategory.OTHER
    state: CASGateState = CASGateState.UNKNOWN
    decision: CASDecision = CASDecision.UNKNOWN

    severity: CASSeverity = CASSeverity.INFO
    source_type: CASSourceType = CASSourceType.UNKNOWN

    value: Any = None
    threshold: Any = None
    utilization: Optional[float] = None

    unit: str = ""
    status: CASStatus = CASStatus.UNKNOWN
    source: str = ""

    message: str = ""
    restriction: str = ""

    timestamp: Optional[datetime] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# CAS REFERENCE
# ============================================================

@dataclass
class CASStatusReference:
    market: str = ""
    instrument: str = ""
    symbol: str = ""
    contract: str = ""
    timeframe: str = ""

    cas_source: str = "app.cas"
    suitability_source: str = "app.cas.suitability_gate"
    risk_source: str = "app.cas.risk_gate"
    exposure_source: str = "app.cas.exposure_gate"
    position_source: str = "app.cas.position_gate"
    execution_safety_source: str = (
        "app.cas.execution_safety_gate"
    )
    compliance_source: str = (
        "app.cas.compliance_gate"
    )
    restriction_source: str = (
        "app.cas.restriction_engine"
    )

    decision_source: str = (
        "app.intelligence.decision"
    )
    d13_source: str = (
        "app.intelligence.decision.d13"
    )

    as_of: Optional[datetime] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# CONTRACT VALIDATION
# ============================================================

@dataclass
class CASContractValidation:
    status: CASContractStatus = (
        CASContractStatus.CREATED
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

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# AUTHORITY BOUNDARY
# ============================================================

CAS_STATUS_AUTHORITY = {
    "presentation_authority": True,
    "cas_display_authority": True,
    "cas_status_aggregation_authority": True,

    # CAS authority itself remains upstream.
    "cas_generation_authority": False,
    "cas_override_authority": False,

    # Other upstream authorities remain untouched.
    "market_data_authority": False,
    "evidence_generation_authority": False,
    "intelligence_generation_authority": False,
    "market_context_authority": False,
    "decision_generation_authority": False,
    "d13_authority": False,
    "d13_mutation": False,
    "risk_authority": False,
    "risk_override": False,

    # Execution boundary.
    "execution_authority": False,
    "order_authority": False,
    "position_authority": False,

    # No upstream mutation.
    "upstream_mutation_authority": False,
}


# ============================================================
# REQUEST NORMALIZATION
# ============================================================

def normalize_cas_status_request(
    request: CASStatusRequest,
) -> CASStatusRequest:

    request.request_id = _cas_text(
        request.request_id
    ).strip()

    request.market = _cas_text(
        request.market
    ).strip()

    request.instrument = _cas_text(
        request.instrument
    ).strip()

    request.symbol = _cas_text(
        request.symbol
    ).strip()

    request.contract = _cas_text(
        request.contract
    ).strip()

    request.timeframe = _cas_text(
        request.timeframe
    ).strip()

    request.mode = _cas_enum(
        request.mode,
        CASMode,
        CASMode.UNKNOWN,
    )

    request.priority = _cas_enum(
        request.priority,
        CASPriority,
        CASPriority.NORMAL,
    )

    return request


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_cas_status_request(
    request: CASStatusRequest,
) -> CASContractValidation:

    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(
        request,
        CASStatusRequest,
    ):
        return CASContractValidation(
            status=CASContractStatus.INVALID,
            valid=False,
            errors=[
                "request must be CASStatusRequest"
            ],
        )

    normalize_cas_status_request(request)

    if not request.market:
        errors.append("market is required")

    if not request.instrument:
        errors.append(
            "instrument is required"
        )

    if not request.symbol:
        errors.append("symbol is required")

    if not request.request_id:
        warnings.append(
            "request_id is empty"
        )

    if request.mode == CASMode.UNKNOWN:
        warnings.append(
            "mode is UNKNOWN"
        )

    if errors:
        status = CASContractStatus.INVALID
        valid = False
    else:
        status = CASContractStatus.READY
        valid = True

    return CASContractValidation(
        status=status,
        valid=valid,
        errors=errors,
        warnings=warnings,
    )


# ============================================================
# REQUEST BUILDER
# ============================================================

def build_cas_status_request(
    market: str,
    instrument: str,
    symbol: str,
    contract: str = "",
    timeframe: str = "",
    mode: CASMode = CASMode.UNKNOWN,
    priority: CASPriority = CASPriority.NORMAL,
    request_id: str = "",
    metadata: Optional[Dict[str, Any]] = None,
) -> CASStatusRequest:

    request = CASStatusRequest(
        request_id=request_id,
        market=market,
        instrument=instrument,
        symbol=symbol,
        contract=contract,
        timeframe=timeframe,
        mode=mode,
        priority=priority,
        metadata=dict(metadata or {}),
    )

    return normalize_cas_status_request(
        request
    )


# ============================================================
# REFERENCE BUILDER
# ============================================================

def build_cas_status_reference(
    request: CASStatusRequest,
    *,
    as_of: Optional[datetime] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> CASStatusReference:

    return CASStatusReference(
        market=request.market,
        instrument=request.instrument,
        symbol=request.symbol,
        contract=request.contract,
        timeframe=request.timeframe,
        cas_source="app.cas",
        suitability_source=(
            "app.cas.suitability_gate"
        ),
        risk_source="app.cas.risk_gate",
        exposure_source=(
            "app.cas.exposure_gate"
        ),
        position_source=(
            "app.cas.position_gate"
        ),
        execution_safety_source=(
            "app.cas.execution_safety_gate"
        ),
        compliance_source=(
            "app.cas.compliance_gate"
        ),
        restriction_source=(
            "app.cas.restriction_engine"
        ),
        decision_source=(
            "app.intelligence.decision"
        ),
        d13_source=(
            "app.intelligence.decision.d13"
        ),
        as_of=as_of,
        metadata=dict(metadata or {}),
    )
# ============================================================
# CAS STATUS — PART 2
# REQUIREMENTS + ASSESSMENT + READINESS
# ============================================================


# ============================================================
# DATA / CONSISTENCY / READINESS ENUMS
# ============================================================

class CASDataState(Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    INVALID = "INVALID"


class CASConsistency(Enum):
    CONSISTENT = "CONSISTENT"
    CONDITIONAL = "CONDITIONAL"
    INCONSISTENT = "INCONSISTENT"
    UNKNOWN = "UNKNOWN"


class CASReadiness(Enum):
    READY = "READY"
    CONDITIONALLY_READY = "CONDITIONALLY_READY"
    NOT_READY = "NOT_READY"
    BLOCKED = "BLOCKED"


# ============================================================
# REQUIREMENTS
# ============================================================

@dataclass
class CASStatusRequirements:
    require_cas_source: bool = True
    require_reference: bool = True
    require_gate_items: bool = True

    require_suitability: bool = True
    require_risk: bool = True
    require_exposure: bool = True
    require_position: bool = True
    require_execution_safety: bool = True
    require_compliance: bool = True
    require_restrictions: bool = True

    minimum_completeness: float = 0.70
    minimum_freshness: float = 0.70
    minimum_confidence: float = 0.70
    minimum_quality: float = 0.70

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class CASStatusAssessment:
    data_state: CASDataState = CASDataState.MISSING
    consistency: CASConsistency = CASConsistency.UNKNOWN
    readiness: CASReadiness = CASReadiness.NOT_READY

    completeness_score: float = 0.0
    freshness_score: float = 0.0
    confidence_score: float = 0.0
    quality_score: float = 0.0

    gate_count: int = 0
    requirements_met: bool = False

    flags: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# REQUIREMENT BUILDER
# ============================================================

def build_cas_status_requirements(
    request: CASStatusRequest,
) -> CASStatusRequirements:

    return CASStatusRequirements(
        require_cas_source=True,
        require_reference=True,
        require_gate_items=True,

        require_suitability=(
            request.include_suitability
        ),
        require_risk=request.include_risk,
        require_exposure=request.include_exposure,
        require_position=request.include_position,
        require_execution_safety=(
            request.include_execution_safety
        ),
        require_compliance=(
            request.include_compliance
        ),
        require_restrictions=(
            request.include_restrictions
        ),
    )


# ============================================================
# DATA STATE
# ============================================================

def evaluate_cas_data_state(
    reference: CASStatusReference,
    items: Optional[List[CASGateItem]],
) -> CASDataState:

    if not isinstance(
        reference,
        CASStatusReference,
    ):
        return CASDataState.INVALID

    if not reference.cas_source:
        return CASDataState.MISSING

    if items is None:
        return CASDataState.MISSING

    if not isinstance(items, list):
        return CASDataState.INVALID

    if not items:
        return CASDataState.MISSING

    invalid_items = [
        item
        for item in items
        if not isinstance(item, CASGateItem)
    ]

    if invalid_items:
        return CASDataState.INVALID

    if any(
        item.status == CASStatus.INVALID
        for item in items
    ):
        return CASDataState.INVALID

    if any(
        item.state == CASGateState.UNKNOWN
        for item in items
    ):
        return CASDataState.PARTIAL

    if any(
        item.status in (
            CASStatus.PARTIAL,
            CASStatus.STALE,
        )
        for item in items
    ):
        return CASDataState.PARTIAL

    return CASDataState.COMPLETE


# ============================================================
# CONSISTENCY
# ============================================================

def evaluate_cas_consistency(
    items: Optional[List[CASGateItem]],
) -> CASConsistency:

    if items is None:
        return CASConsistency.UNKNOWN

    if not items:
        return CASConsistency.UNKNOWN

    if any(
        not isinstance(item, CASGateItem)
        for item in items
    ):
        return CASConsistency.INCONSISTENT

    if any(
        item.state == CASGateState.BLOCK
        and item.decision == CASDecision.ALLOW
        for item in items
    ):
        return CASConsistency.INCONSISTENT

    if any(
        item.state == CASGateState.FAIL
        and item.decision == CASDecision.ALLOW
        for item in items
    ):
        return CASConsistency.INCONSISTENT

    if any(
        item.state == CASGateState.WARN
        and item.decision == CASDecision.ALLOW
        for item in items
    ):
        return CASConsistency.CONDITIONAL

    if any(
        item.state == CASGateState.UNKNOWN
        or item.decision == CASDecision.UNKNOWN
        for item in items
    ):
        return CASConsistency.CONDITIONAL

    return CASConsistency.CONSISTENT


# ============================================================
# REQUIREMENT EVALUATION
# ============================================================

def evaluate_cas_requirements(
    request: CASStatusRequest,
    reference: CASStatusReference,
    items: Optional[List[CASGateItem]],
    requirements: CASStatusRequirements,
) -> tuple[bool, List[str]]:

    flags: List[str] = []

    if requirements.require_cas_source:
        if not reference.cas_source:
            flags.append("missing_cas_source")

    if requirements.require_reference:
        if (
            not reference.market
            or not reference.instrument
            or not reference.symbol
        ):
            flags.append("incomplete_reference")

    if requirements.require_gate_items:
        if not items:
            flags.append("missing_gate_items")

    category_map = {
        CASCategory.SUITABILITY:
            requirements.require_suitability,
        CASCategory.RISK:
            requirements.require_risk,
        CASCategory.EXPOSURE:
            requirements.require_exposure,
        CASCategory.POSITION:
            requirements.require_position,
        CASCategory.EXECUTION_SAFETY:
            requirements.require_execution_safety,
        CASCategory.COMPLIANCE:
            requirements.require_compliance,
        CASCategory.RESTRICTION:
            requirements.require_restrictions,
    }

    existing_categories = {
        item.category
        for item in (items or [])
        if isinstance(item, CASGateItem)
    }

    for category, required in category_map.items():
        if required and category not in existing_categories:
            flags.append(
                f"missing_{category.value.lower()}_gate"
            )

    return not flags, flags


# ============================================================
# FRESHNESS
# ============================================================

def evaluate_cas_freshness(
    items: Optional[List[CASGateItem]],
    now: Optional[datetime] = None,
) -> float:

    if not items:
        return 0.0

    current_time = now or datetime.utcnow()
    scores: List[float] = []

    for item in items:
        if not item.timestamp:
            scores.append(0.0)
            continue

        age = (
            current_time - item.timestamp
        ).total_seconds()

        if age < 0:
            age = 0

        if age <= 5:
            score = 1.0
        elif age <= 30:
            score = 0.95
        elif age <= 60:
            score = 0.90
        elif age <= 120:
            score = 0.80
        elif age <= 300:
            score = 0.65
        elif age <= 600:
            score = 0.45
        elif age <= 1800:
            score = 0.25
        else:
            score = 0.0

        scores.append(score)

    return sum(scores) / len(scores)


# ============================================================
# COMPLETENESS
# ============================================================

def evaluate_cas_completeness(
    items: Optional[List[CASGateItem]],
    requirements: CASStatusRequirements,
) -> float:

    if not items:
        return 0.0

    required_categories = []

    if requirements.require_suitability:
        required_categories.append(
            CASCategory.SUITABILITY
        )

    if requirements.require_risk:
        required_categories.append(
            CASCategory.RISK
        )

    if requirements.require_exposure:
        required_categories.append(
            CASCategory.EXPOSURE
        )

    if requirements.require_position:
        required_categories.append(
            CASCategory.POSITION
        )

    if requirements.require_execution_safety:
        required_categories.append(
            CASCategory.EXECUTION_SAFETY
        )

    if requirements.require_compliance:
        required_categories.append(
            CASCategory.COMPLIANCE
        )

    if requirements.require_restrictions:
        required_categories.append(
            CASCategory.RESTRICTION
        )

    if not required_categories:
        return 1.0

    existing_categories = {
        item.category
        for item in items
        if isinstance(item, CASGateItem)
    }

    matched = sum(
        1
        for category in required_categories
        if category in existing_categories
    )

    return matched / len(required_categories)


# ============================================================
# CONFIDENCE
# ============================================================

def evaluate_cas_confidence(
    items: Optional[List[CASGateItem]],
) -> float:

    if not items:
        return 0.0

    scores: List[float] = []

    for item in items:
        score = 1.0

        if item.state == CASGateState.UNKNOWN:
            score -= 0.35

        if item.decision == CASDecision.UNKNOWN:
            score -= 0.20

        if item.status in (
            CASStatus.UNKNOWN,
            CASStatus.PARTIAL,
        ):
            score -= 0.20

        if not item.source:
            score -= 0.15

        if not item.message:
            score -= 0.05

        scores.append(
            max(0.0, min(1.0, score))
        )

    return sum(scores) / len(scores)


# ============================================================
# QUALITY
# ============================================================

def evaluate_cas_quality(
    completeness_score: float,
    freshness_score: float,
    confidence_score: float,
    consistency: CASConsistency,
) -> float:

    consistency_score = {
        CASConsistency.CONSISTENT: 1.0,
        CASConsistency.CONDITIONAL: 0.70,
        CASConsistency.UNKNOWN: 0.40,
        CASConsistency.INCONSISTENT: 0.0,
    }.get(consistency, 0.0)

    quality = (
        completeness_score * 0.30
        + freshness_score * 0.25
        + confidence_score * 0.25
        + consistency_score * 0.20
    )

    return max(
        0.0,
        min(1.0, quality),
    )


# ============================================================
# READINESS
# ============================================================

def evaluate_cas_readiness(
    data_state: CASDataState,
    consistency: CASConsistency,
    requirements_met: bool,
    completeness_score: float,
    freshness_score: float,
    confidence_score: float,
    quality_score: float,
    requirements: CASStatusRequirements,
) -> CASReadiness:

    if data_state in (
        CASDataState.INVALID,
        CASDataState.MISSING,
    ):
        return CASReadiness.BLOCKED

    if consistency == CASConsistency.INCONSISTENT:
        return CASReadiness.BLOCKED

    if quality_score < 0.50:
        return CASReadiness.NOT_READY

    if not requirements_met:
        if quality_score >= requirements.minimum_quality:
            return CASReadiness.CONDITIONALLY_READY
        return CASReadiness.NOT_READY

    if (
        completeness_score < requirements.minimum_completeness
        or freshness_score < requirements.minimum_freshness
        or confidence_score < requirements.minimum_confidence
        or quality_score < requirements.minimum_quality
    ):
        return CASReadiness.CONDITIONALLY_READY

    if consistency == CASConsistency.CONDITIONAL:
        return CASReadiness.CONDITIONALLY_READY

    if data_state == CASDataState.PARTIAL:
        return CASReadiness.CONDITIONALLY_READY

    return CASReadiness.READY


# ============================================================
# ASSESSMENT BUILDER
# ============================================================

def build_cas_status_assessment(
    request: CASStatusRequest,
    reference: CASStatusReference,
    items: Optional[List[CASGateItem]],
    requirements: Optional[
        CASStatusRequirements
    ] = None,
) -> CASStatusAssessment:

    req = requirements or build_cas_status_requirements(
        request
    )

    data_state = evaluate_cas_data_state(
        reference,
        items,
    )

    consistency = evaluate_cas_consistency(
        items
    )

    requirements_met, requirement_flags = (
        evaluate_cas_requirements(
            request,
            reference,
            items,
            req,
        )
    )

    freshness = evaluate_cas_freshness(
        items
    )

    completeness = evaluate_cas_completeness(
        items,
        req,
    )

    confidence = evaluate_cas_confidence(
        items
    )

    quality = evaluate_cas_quality(
        completeness,
        freshness,
        confidence,
        consistency,
    )

    readiness = evaluate_cas_readiness(
        data_state=data_state,
        consistency=consistency,
        requirements_met=requirements_met,
        completeness_score=completeness,
        freshness_score=freshness,
        confidence_score=confidence,
        quality_score=quality,
        requirements=req,
    )

    flags = list(requirement_flags)

    if freshness < req.minimum_freshness:
        flags.append("low_freshness")

    if completeness < req.minimum_completeness:
        flags.append("low_completeness")

    if confidence < req.minimum_confidence:
        flags.append("low_confidence")

    if quality < req.minimum_quality:
        flags.append("low_quality")

    if consistency == CASConsistency.CONDITIONAL:
        flags.append("conditional_consistency")

    if data_state == CASDataState.PARTIAL:
        flags.append("partial_data")

    if data_state == CASDataState.MISSING:
        flags.append("missing_data")

    if data_state == CASDataState.INVALID:
        flags.append("invalid_data")

    return CASStatusAssessment(
        data_state=data_state,
        consistency=consistency,
        readiness=readiness,
        completeness_score=completeness,
        freshness_score=freshness,
        confidence_score=confidence,
        quality_score=quality,
        gate_count=len(items or []),
        requirements_met=requirements_met,
        flags=flags,
        metadata={
            "assessment_only": True,
            "cas_generation": False,
            "cas_override": False,
            "d13_mutation": False,
            "risk_override": False,
            "execution": False,
            "upstream_authority_preserved": True,
        },
    )
# ============================================================
# CAS STATUS — PART 3
# RESOLUTION + PRESENTATION + RESULT + AUTHORITY
# ============================================================


# ============================================================
# RESOLUTION ENUMS
# ============================================================

class CASResolutionStatus(Enum):
    RESOLVED = "RESOLVED"
    CONDITIONAL = "CONDITIONAL"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"


# ============================================================
# RESOLUTION RULES
# ============================================================

@dataclass
class CASResolutionRules:
    allow_when_ready: bool = True
    allow_when_conditionally_ready: bool = True
    review_when_not_ready: bool = True

    block_when_invalid: bool = True
    block_when_inconsistent: bool = True
    block_on_authority_violation: bool = True

    require_cas_source: bool = True
    require_all_declared_gates: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# PRESENTATION CONTRACT
# ============================================================

@dataclass
class CASStatusPresentation:
    title: str = "CAS Status"

    overall_state: CASGateState = (
        CASGateState.UNKNOWN
    )

    overall_decision: CASDecision = (
        CASDecision.UNKNOWN
    )

    gates: List[CASGateItem] = field(
        default_factory=list
    )

    cas_source: str = ""
    decision_source: str = ""
    d13_source: str = ""

    status: CASStatus = CASStatus.UNKNOWN
    resolution: CASResolutionStatus = (
        CASResolutionStatus.BLOCKED
    )

    restrictions: List[str] = field(
        default_factory=list
    )

    flags: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# RESULT CONTRACT
# ============================================================

@dataclass
class CASStatusResult:
    request: CASStatusRequest
    reference: CASStatusReference
    assessment: CASStatusAssessment
    presentation: CASStatusPresentation

    decision: CASDecision = CASDecision.UNKNOWN
    resolution: CASResolutionStatus = (
        CASResolutionStatus.BLOCKED
    )

    flags: List[str] = field(
        default_factory=list
    )

    restrictions: List[str] = field(
        default_factory=list
    )

    authority_valid: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# SOURCE MAP
# ============================================================

@dataclass
class CASStatusSourceMap:
    cas_status_engine: str = CAS_STATUS_ENGINE

    cas_source: str = "app.cas"
    suitability_source: str = (
        "app.cas.suitability_gate"
    )
    risk_source: str = "app.cas.risk_gate"
    exposure_source: str = (
        "app.cas.exposure_gate"
    )
    position_source: str = (
        "app.cas.position_gate"
    )
    execution_safety_source: str = (
        "app.cas.execution_safety_gate"
    )
    compliance_source: str = (
        "app.cas.compliance_gate"
    )
    restriction_source: str = (
        "app.cas.restriction_engine"
    )

    decision_source: str = (
        "app.intelligence.decision"
    )
    d13_source: str = (
        "app.intelligence.decision.d13"
    )

    risk_panel_source: str = (
        "app.terminal.risk_panel"
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# RESOLUTION RULE BUILDER
# ============================================================

def build_cas_resolution_rules(
    request: CASStatusRequest,
) -> CASResolutionRules:

    return CASResolutionRules(
        allow_when_ready=True,
        allow_when_conditionally_ready=True,
        review_when_not_ready=True,
        block_when_invalid=True,
        block_when_inconsistent=True,
        block_on_authority_violation=True,
        require_cas_source=True,
        require_all_declared_gates=True,
        metadata={
            "presentation_only": True,
            "cas_generation": False,
            "cas_override": False,
            "d13_mutation": False,
        },
    )


# ============================================================
# RESOLUTION FLAGS
# ============================================================

def collect_cas_resolution_flags(
    assessment: CASStatusAssessment,
) -> List[str]:

    flags = list(assessment.flags)

    if assessment.data_state == CASDataState.INVALID:
        if "invalid_data" not in flags:
            flags.append("invalid_data")

    if assessment.data_state == CASDataState.MISSING:
        if "missing_data" not in flags:
            flags.append("missing_data")

    if (
        assessment.consistency
        == CASConsistency.INCONSISTENT
    ):
        if "inconsistent_data" not in flags:
            flags.append("inconsistent_data")

    if (
        assessment.readiness
        == CASReadiness.NOT_READY
    ):
        if "not_ready" not in flags:
            flags.append("not_ready")

    if (
        assessment.readiness
        == CASReadiness.CONDITIONALLY_READY
    ):
        if "conditional_readiness" not in flags:
            flags.append("conditional_readiness")

    return flags


# ============================================================
# RESTRICTIONS
# ============================================================

def collect_cas_restrictions(
    assessment: CASStatusAssessment,
    items: Optional[List[CASGateItem]],
) -> List[str]:

    restrictions: List[str] = []

    for item in items or []:
        if not isinstance(item, CASGateItem):
            continue

        if item.restriction:
            restrictions.append(
                item.restriction
            )

        if item.state == CASGateState.WARN:
            restrictions.append(
                f"{item.label}: warning"
            )

        if item.decision == (
            CASDecision.ALLOW_WITH_RESTRICTION
        ):
            restrictions.append(
                f"{item.label}: restricted"
            )

    if (
        assessment.readiness
        == CASReadiness.CONDITIONALLY_READY
    ):
        restrictions.append(
            "CAS status is conditionally ready"
        )

    return list(dict.fromkeys(restrictions))


# ============================================================
# GATE STATE AGGREGATION
# ============================================================

def _aggregate_cas_gate_state(
    items: Optional[List[CASGateItem]],
) -> CASGateState:

    if not items:
        return CASGateState.UNKNOWN

    priority = {
        CASGateState.BLOCK: 5,
        CASGateState.FAIL: 4,
        CASGateState.WARN: 3,
        CASGateState.NOT_EVALUATED: 2,
        CASGateState.PASS: 1,
        CASGateState.UNKNOWN: 0,
    }

    valid_states = [
        item.state
        for item in items
        if isinstance(item, CASGateItem)
    ]

    if not valid_states:
        return CASGateState.UNKNOWN

    return max(
        valid_states,
        key=lambda state: priority.get(
            state,
            0,
        ),
    )


# ============================================================
# DECISION AGGREGATION
# ============================================================

def _aggregate_cas_decision(
    items: Optional[List[CASGateItem]],
) -> CASDecision:

    if not items:
        return CASDecision.UNKNOWN

    priority = {
        CASDecision.BLOCK: 5,
        CASDecision.REVIEW_REQUIRED: 4,
        CASDecision.ALLOW_WITH_RESTRICTION: 3,
        CASDecision.ALLOW: 2,
        CASDecision.UNKNOWN: 0,
    }

    decisions = [
        item.decision
        for item in items
        if isinstance(item, CASGateItem)
    ]

    if not decisions:
        return CASDecision.UNKNOWN

    return max(
        decisions,
        key=lambda decision: priority.get(
            decision,
            0,
        ),
    )


# ============================================================
# PRESENTATION BUILDER
# ============================================================

def build_cas_status_presentation(
    request: CASStatusRequest,
    reference: CASStatusReference,
    assessment: CASStatusAssessment,
    items: Optional[List[CASGateItem]],
    resolution: CASResolutionStatus,
    decision: CASDecision,
    flags: Optional[List[str]] = None,
    restrictions: Optional[List[str]] = None,
) -> CASStatusPresentation:

    gates = list(items or [])

    overall_state = _aggregate_cas_gate_state(
        gates
    )

    status = CASStatus.UNKNOWN

    if assessment.data_state == CASDataState.INVALID:
        status = CASStatus.INVALID
    elif assessment.data_state == CASDataState.MISSING:
        status = CASStatus.PARTIAL
    elif assessment.readiness == CASReadiness.BLOCKED:
        status = CASStatus.ERROR
    elif assessment.readiness == (
        CASReadiness.CONDITIONALLY_READY
    ):
        status = CASStatus.PARTIAL
    elif assessment.readiness == CASReadiness.NOT_READY:
        status = CASStatus.STALE
    else:
        status = CASStatus.READY

    return CASStatusPresentation(
        title=(
            f"CAS Status — "
            f"{request.symbol or 'UNKNOWN'}"
        ),
        overall_state=overall_state,
        overall_decision=decision,
        gates=gates,
        cas_source=reference.cas_source,
        decision_source=reference.decision_source,
        d13_source=reference.d13_source,
        status=status,
        resolution=resolution,
        restrictions=list(
            restrictions or []
        ),
        flags=list(flags or []),
        metadata={
            "presentation_only": True,
            "cas_generation": False,
            "cas_override": False,
            "d13_mutation": False,
            "risk_override": False,
            "execution": False,
            "upstream_authority_preserved": True,
        },
    )


# ============================================================
# RESOLVER
# ============================================================

def resolve_cas_status(
    request: CASStatusRequest,
    reference: CASStatusReference,
    assessment: CASStatusAssessment,
    items: Optional[List[CASGateItem]] = None,
    rules: Optional[CASResolutionRules] = None,
) -> CASStatusResult:

    resolution_rules = (
        rules
        or build_cas_resolution_rules(request)
    )

    flags = collect_cas_resolution_flags(
        assessment
    )

    restrictions = collect_cas_restrictions(
        assessment,
        items,
    )

    authority_valid = True

    # Terminal CAS status must never claim CAS
    # generation or override authority.
    if (
        assessment.metadata.get(
            "cas_generation",
            False,
        )
        or assessment.metadata.get(
            "cas_override",
            False,
        )
        or assessment.metadata.get(
            "d13_mutation",
            False,
        )
    ):
        authority_valid = False
        flags.append(
            "authority_violation"
        )

    if not reference.cas_source:
        authority_valid = False
        flags.append(
            "missing_cas_source"
        )

    if not authority_valid:
        decision = CASDecision.BLOCK
        resolution = CASResolutionStatus.BLOCKED

    elif (
        assessment.data_state
        == CASDataState.INVALID
    ):
        decision = CASDecision.BLOCK
        resolution = CASResolutionStatus.BLOCKED

    elif (
        assessment.consistency
        == CASConsistency.INCONSISTENT
    ):
        decision = CASDecision.BLOCK
        resolution = CASResolutionStatus.BLOCKED

    elif (
        assessment.readiness
        == CASReadiness.BLOCKED
    ):
        decision = CASDecision.BLOCK
        resolution = CASResolutionStatus.BLOCKED

    elif (
        assessment.readiness
        == CASReadiness.NOT_READY
    ):
        decision = CASDecision.REVIEW_REQUIRED
        resolution = (
            CASResolutionStatus.REVIEW_REQUIRED
        )

    elif (
        assessment.readiness
        == CASReadiness.CONDITIONALLY_READY
    ):
        decision = (
            CASDecision.ALLOW_WITH_RESTRICTION
        )
        resolution = (
            CASResolutionStatus.CONDITIONAL
        )

    else:
        decision = CASDecision.ALLOW
        resolution = CASResolutionStatus.RESOLVED

    presentation = build_cas_status_presentation(
        request=request,
        reference=reference,
        assessment=assessment,
        items=items,
        resolution=resolution,
        decision=decision,
        flags=flags,
        restrictions=restrictions,
    )

    return CASStatusResult(
        request=request,
        reference=reference,
        assessment=assessment,
        presentation=presentation,
        decision=decision,
        resolution=resolution,
        flags=flags,
        restrictions=restrictions,
        authority_valid=authority_valid,
        metadata={
            "presentation_only": True,
            "cas_generation": False,
            "cas_override": False,
            "d13_mutation": False,
            "risk_override": False,
            "execution": False,
            "upstream_authority_preserved": True,
            "resolution_authority": (
                "terminal_presentation_only"
            ),
        },
    )


# ============================================================
# RESULT VALIDATION
# ============================================================

def validate_cas_status_result(
    result: CASStatusResult,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        result,
        CASStatusResult,
    ):
        return [
            "result must be CASStatusResult"
        ]

    if not isinstance(
        result.request,
        CASStatusRequest,
    ):
        errors.append(
            "invalid request"
        )

    if not isinstance(
        result.reference,
        CASStatusReference,
    ):
        errors.append(
            "invalid reference"
        )

    if not isinstance(
        result.assessment,
        CASStatusAssessment,
    ):
        errors.append(
            "invalid assessment"
        )

    if not isinstance(
        result.presentation,
        CASStatusPresentation,
    ):
        errors.append(
            "invalid presentation"
        )

    if not isinstance(
        result.decision,
        CASDecision,
    ):
        errors.append(
            "invalid decision"
        )

    if not isinstance(
        result.resolution,
        CASResolutionStatus,
    ):
        errors.append(
            "invalid resolution"
        )

    errors.extend(
        validate_cas_status_result_authority(
            result
        )
    )

    return errors


# ============================================================
# AUTHORITY VALIDATION
# ============================================================

def validate_cas_status_result_authority(
    result: CASStatusResult,
) -> List[str]:

    errors: List[str] = []

    if not result.authority_valid:
        errors.append(
            "result authority_valid is false"
        )

    forbidden_keys = (
        "cas_generation",
        "cas_override",
        "d13_mutation",
        "risk_override",
        "execution",
        "upstream_mutation",
    )

    sources = [
        result.metadata,
        result.assessment.metadata,
        result.presentation.metadata,
    ]

    for source in sources:
        for key in forbidden_keys:
            if source.get(key, False) is True:
                errors.append(
                    f"forbidden authority flag: {key}"
                )

    return list(dict.fromkeys(errors))
# ============================================================
# CAS STATUS — PART 4
# REGISTRY + SERVICE + OPERATIONAL HELPERS
# ============================================================


# ============================================================
# REGISTRY CONTRACTS
# ============================================================

@dataclass
class CASStatusRegistryEntry:
    key: str
    reference: CASStatusReference

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )
    updated_at: datetime = field(
        default_factory=datetime.utcnow
    )

    active: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class CASStatusRegistrySnapshot:
    engine: str
    version: str

    entries: List[CASStatusRegistryEntry]

    count: int

    captured_at: datetime = field(
        default_factory=datetime.utcnow
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class CASStatusServiceResult:
    request_id: str

    reference: Optional[CASStatusReference]
    assessment: Optional[CASStatusAssessment]
    result: Optional[CASStatusResult]

    success: bool

    errors: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# REGISTRY KEY
# ============================================================

def _cas_status_registry_key(
    reference: CASStatusReference,
) -> str:

    parts = [
        reference.market,
        reference.instrument,
        reference.symbol,
        reference.contract,
        reference.timeframe,
    ]

    normalized: List[str] = []

    for value in parts:
        text = _cas_text(value).strip().upper()

        normalized.append(
            text if text else "-"
        )

    return ":".join(normalized)


# ============================================================
# CAS STATUS REGISTRY
# ============================================================

class CASStatusRegistry:
    """
    Registry for Terminal CAS Status references.

    Registry authority is limited to reference management.

    It does NOT:
        - generate CAS decisions
        - modify CAS gates
        - override CAS
        - modify D13
        - modify Risk
        - execute orders
        - modify positions
        - mutate upstream systems
    """

    def __init__(self) -> None:
        self._entries: Dict[
            str,
            CASStatusRegistryEntry,
        ] = {}

    def exists(
        self,
        reference: CASStatusReference,
    ) -> bool:

        key = _cas_status_registry_key(
            reference
        )

        return key in self._entries

    def get(
        self,
        reference: CASStatusReference,
    ) -> Optional[CASStatusReference]:

        key = _cas_status_registry_key(
            reference
        )

        entry = self._entries.get(key)

        if entry is None:
            return None

        return entry.reference

    def get_entry(
        self,
        reference: CASStatusReference,
    ) -> Optional[CASStatusRegistryEntry]:

        key = _cas_status_registry_key(
            reference
        )

        return self._entries.get(key)

    def add(
        self,
        reference: CASStatusReference,
    ) -> CASStatusRegistryEntry:

        key = _cas_status_registry_key(
            reference
        )

        if key in self._entries:
            raise ValueError(
                f"CAS Status reference already exists: {key}"
            )

        now = datetime.utcnow()

        entry = CASStatusRegistryEntry(
            key=key,
            reference=reference,
            created_at=now,
            updated_at=now,
            active=True,
        )

        self._entries[key] = entry

        return entry

    def replace(
        self,
        reference: CASStatusReference,
    ) -> CASStatusRegistryEntry:

        key = _cas_status_registry_key(
            reference
        )

        now = datetime.utcnow()

        existing = self._entries.get(key)

        entry = CASStatusRegistryEntry(
            key=key,
            reference=reference,
            created_at=(
                existing.created_at
                if existing
                else now
            ),
            updated_at=now,
            active=True,
            metadata=(
                dict(existing.metadata)
                if existing
                else {}
            ),
        )

        self._entries[key] = entry

        return entry

    def remove(
        self,
        reference: CASStatusReference,
    ) -> bool:

        key = _cas_status_registry_key(
            reference
        )

        if key not in self._entries:
            return False

        del self._entries[key]

        return True

    def list_references(
        self,
    ) -> List[CASStatusReference]:

        return [
            entry.reference
            for entry in self._entries.values()
            if entry.active
        ]

    def snapshot(
        self,
    ) -> CASStatusRegistrySnapshot:

        return CASStatusRegistrySnapshot(
            engine=CAS_STATUS_ENGINE,
            version=CAS_STATUS_VERSION,
            entries=list(
                self._entries.values()
            ),
            count=len(self._entries),
        )

    def count(self) -> int:
        return len(self._entries)


# ============================================================
# REGISTRY VALIDATION
# ============================================================

def validate_cas_status_registry(
    registry: CASStatusRegistry,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        registry,
        CASStatusRegistry,
    ):
        return [
            "registry must be CASStatusRegistry"
        ]

    for key, entry in registry._entries.items():

        if not key:
            errors.append(
                "registry contains empty key"
            )

        if not isinstance(
            entry,
            CASStatusRegistryEntry,
        ):
            errors.append(
                f"invalid registry entry: {key}"
            )
            continue

        if not isinstance(
            entry.reference,
            CASStatusReference,
        ):
            errors.append(
                f"invalid reference: {key}"
            )
            continue

        expected_key = (
            _cas_status_registry_key(
                entry.reference
            )
        )

        if key != expected_key:
            errors.append(
                f"registry key mismatch: {key}"
            )

    return errors


# ============================================================
# REGISTRY HEALTH
# ============================================================

def cas_status_registry_health(
    registry: CASStatusRegistry,
) -> Dict[str, Any]:

    errors = validate_cas_status_registry(
        registry
    )

    if isinstance(
        registry,
        CASStatusRegistry,
    ):
        count = registry.count()
    else:
        count = 0

    return {
        "engine": CAS_STATUS_ENGINE,
        "version": CAS_STATUS_VERSION,
        "healthy": not errors,
        "count": count,
        "errors": errors,

        "cas_generation": False,
        "cas_override": False,
        "d13_mutation": False,
        "risk_override": False,
        "execution": False,
        "upstream_mutation": False,
    }


# ============================================================
# CAS STATUS SERVICE
# ============================================================

class CASStatusService:
    """
    Application service for Terminal CAS Status.

    Flow:

        app.cas
           ↓
        CAS Status Service
           ↓
        Terminal CAS Presentation

    The service consumes CAS information.
    It does not become the CAS authority.
    """

    def __init__(
        self,
        registry: Optional[
            CASStatusRegistry
        ] = None,
    ) -> None:

        self.registry = (
            registry
            or CASStatusRegistry()
        )

    # --------------------------------------------------------
    # RESOLVE
    # --------------------------------------------------------

    def resolve(
        self,
        request: CASStatusRequest,
        reference: CASStatusReference,
        assessment: CASStatusAssessment,
        items: Optional[
            List[CASGateItem]
        ] = None,
    ) -> CASStatusServiceResult:

        try:

            result = resolve_cas_status(
                request=request,
                reference=reference,
                assessment=assessment,
                items=items,
            )

            return CASStatusServiceResult(
                request_id=request.request_id,
                reference=reference,
                assessment=assessment,
                result=result,
                success=True,
                metadata={
                    "presentation_only": True,
                    "cas_generation": False,
                    "cas_override": False,
                    "d13_mutation": False,
                    "risk_override": False,
                    "execution": False,
                    "upstream_authority_preserved": True,
                },
            )

        except Exception as exc:

            return CASStatusServiceResult(
                request_id=request.request_id,
                reference=reference,
                assessment=assessment,
                result=None,
                success=False,
                errors=[str(exc)],
                metadata={
                    "presentation_only": True,
                    "cas_generation": False,
                    "cas_override": False,
                    "d13_mutation": False,
                    "risk_override": False,
                    "execution": False,
                },
            )

    # --------------------------------------------------------
    # ASSESS
    # --------------------------------------------------------

    def assess(
        self,
        request: CASStatusRequest,
        reference: CASStatusReference,
        items: Optional[
            List[CASGateItem]
        ] = None,
    ) -> CASStatusServiceResult:

        try:

            assessment = (
                build_cas_status_assessment(
                    request=request,
                    reference=reference,
                    items=items,
                )
            )

            return CASStatusServiceResult(
                request_id=request.request_id,
                reference=reference,
                assessment=assessment,
                result=None,
                success=True,
                metadata={
                    "assessment_only": True,
                    "cas_generation": False,
                    "cas_override": False,
                    "d13_mutation": False,
                    "risk_override": False,
                    "execution": False,
                    "upstream_authority_preserved": True,
                },
            )

        except Exception as exc:

            return CASStatusServiceResult(
                request_id=request.request_id,
                reference=reference,
                assessment=None,
                result=None,
                success=False,
                errors=[str(exc)],
            )

    # --------------------------------------------------------
    # REGISTER
    # --------------------------------------------------------

    def register(
        self,
        reference: CASStatusReference,
        replace: bool = False,
    ) -> CASStatusRegistryEntry:

        if replace:
            return self.registry.replace(
                reference
            )

        return self.registry.add(
            reference
        )

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    def get(
        self,
        reference: CASStatusReference,
    ) -> Optional[CASStatusReference]:

        return self.registry.get(
            reference
        )

    # --------------------------------------------------------
    # LIST
    # --------------------------------------------------------

    def list_references(
        self,
    ) -> List[CASStatusReference]:

        return self.registry.list_references()

    # --------------------------------------------------------
    # SNAPSHOT
    # --------------------------------------------------------

    def snapshot(
        self,
    ) -> CASStatusRegistrySnapshot:

        return self.registry.snapshot()

    # --------------------------------------------------------
    # HEALTH
    # --------------------------------------------------------

    def health(
        self,
    ) -> Dict[str, Any]:

        return cas_status_registry_health(
            self.registry
        )

    # --------------------------------------------------------
    # INTEGRITY
    # --------------------------------------------------------

    def integrity(
        self,
    ) -> List[str]:

        return validate_cas_status_registry(
            self.registry
        )

    # --------------------------------------------------------
    # INFO
    # --------------------------------------------------------

    def info(
        self,
    ) -> Dict[str, Any]:

        return {
            "engine": CAS_STATUS_ENGINE,
            "version": CAS_STATUS_VERSION,

            "role": (
                "terminal_cas_status_presentation_service"
            ),

            "authority": {
                "presentation": True,
                "cas_display": True,
                "cas_status_aggregation": True,

                "cas_generation": False,
                "cas_override": False,

                "d13_authority": False,
                "d13_mutation": False,

                "risk_authority": False,
                "risk_override": False,

                "execution": False,
                "order_authority": False,
                "position_authority": False,

                "upstream_mutation": False,
            },

            "registry_count": (
                self.registry.count()
            ),
        }


# ============================================================
# SINGLETON SERVICE
# ============================================================

_CAS_STATUS_SERVICE = CASStatusService()


# ============================================================
# SERVICE ACCESSOR
# ============================================================

def get_cas_status_service() -> CASStatusService:
    return _CAS_STATUS_SERVICE


# ============================================================
# RESOLVE HELPER
# ============================================================

def resolve_terminal_cas_status(
    request: CASStatusRequest,
    reference: CASStatusReference,
    assessment: CASStatusAssessment,
    items: Optional[
        List[CASGateItem]
    ] = None,
) -> CASStatusServiceResult:

    return _CAS_STATUS_SERVICE.resolve(
        request=request,
        reference=reference,
        assessment=assessment,
        items=items,
    )


# ============================================================
# REFERENCE HELPER
# ============================================================

def get_terminal_cas_status_reference(
    reference: CASStatusReference,
) -> Optional[CASStatusReference]:

    return _CAS_STATUS_SERVICE.get(
        reference
    )


# ============================================================
# SNAPSHOT HELPER
# ============================================================

def terminal_cas_status_snapshot(
) -> CASStatusRegistrySnapshot:

    return _CAS_STATUS_SERVICE.snapshot()


# ============================================================
# COUNT HELPER
# ============================================================

def terminal_cas_status_count() -> int:

    return _CAS_STATUS_SERVICE.registry.count()


# ============================================================
# HEALTH HELPER
# ============================================================

def terminal_cas_status_health(
) -> Dict[str, Any]:

    return _CAS_STATUS_SERVICE.health()


# ============================================================
# INTEGRITY HELPER
# ============================================================

def terminal_cas_status_integrity(
) -> List[str]:

    return _CAS_STATUS_SERVICE.integrity()


# ============================================================
# OPERATIONAL CHECK
# ============================================================

def terminal_cas_status_operational_check(
) -> Dict[str, Any]:

    health = _CAS_STATUS_SERVICE.health()

    authority_preserved = (
        health["cas_generation"] is False
        and health["cas_override"] is False
        and health["d13_mutation"] is False
        and health["risk_override"] is False
        and health["execution"] is False
        and health["upstream_mutation"] is False
    )

    return {
        "engine": CAS_STATUS_ENGINE,
        "version": CAS_STATUS_VERSION,

        "operational": health["healthy"],

        "registry_count": health["count"],

        "errors": health["errors"],

        "authority_preserved": (
            authority_preserved
        ),
    }


# ============================================================
# SERVICE INFO HELPER
# ============================================================

def terminal_cas_status_service_info(
) -> Dict[str, Any]:

    return _CAS_STATUS_SERVICE.info()
# ============================================================
# PART 5 — SERIALIZATION / INTEGRITY / SUMMARY / EXPORTS
# ============================================================

def _cas_serialize_datetime(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _cas_serialize_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value

    if isinstance(value, datetime):
        return value.isoformat()

    if hasattr(value, "__dataclass_fields__"):
        return {
            key: _cas_serialize_value(val)
            for key, val in value.__dict__.items()
        }

    if isinstance(value, dict):
        return {
            str(key): _cas_serialize_value(val)
            for key, val in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [_cas_serialize_value(item) for item in value]

    return value


def serialize_cas_gate_item(
    item: CASGateItem,
) -> Dict[str, Any]:
    return _cas_serialize_value(item)


def serialize_cas_status_reference(
    reference: CASStatusReference,
) -> Dict[str, Any]:
    return _cas_serialize_value(reference)


def serialize_cas_status_assessment(
    assessment: CASStatusAssessment,
) -> Dict[str, Any]:
    return _cas_serialize_value(assessment)


def serialize_cas_status_presentation(
    presentation: CASStatusPresentation,
) -> Dict[str, Any]:
    return _cas_serialize_value(presentation)


def serialize_cas_status_result(
    result: CASStatusResult,
) -> Dict[str, Any]:
    return _cas_serialize_value(result)


def serialize_cas_status_service_result(
    service_result: CASStatusServiceResult,
) -> Dict[str, Any]:
    return _cas_serialize_value(service_result)


def serialize_cas_status_source_map(
    source_map: CASStatusSourceMap,
) -> Dict[str, Any]:
    return _cas_serialize_value(source_map)


def serialize_cas_status_registry_snapshot(
    snapshot: CASStatusRegistrySnapshot,
) -> Dict[str, Any]:
    return _cas_serialize_value(snapshot)


# ------------------------------------------------------------
# INTEGRITY VALIDATION
# ------------------------------------------------------------

def validate_cas_gate_item_integrity(
    item: CASGateItem,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(item, CASGateItem):
        return ["gate_item must be CASGateItem"]

    if not _cas_text(item.gate_id):
        errors.append("gate_id is required")

    if not _cas_text(item.label):
        errors.append("label is required")

    if not isinstance(item.category, CASCategory):
        errors.append("category is invalid")

    if not isinstance(item.state, CASGateState):
        errors.append("state is invalid")

    if not isinstance(item.decision, CASDecision):
        errors.append("decision is invalid")

    if not isinstance(item.severity, CASSeverity):
        errors.append("severity is invalid")

    if not isinstance(item.source_type, CASSourceType):
        errors.append("source_type is invalid")

    if not _cas_text(item.source):
        errors.append("source is required")

    return errors


def validate_cas_status_reference_integrity(
    reference: CASStatusReference,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(reference, CASStatusReference):
        return ["reference must be CASStatusReference"]

    if not _cas_text(reference.market):
        errors.append("market is required")

    if not _cas_text(reference.instrument):
        errors.append("instrument is required")

    if not _cas_text(reference.symbol):
        errors.append("symbol is required")

    if reference.cas_source != "app.cas":
        errors.append("cas_source must remain app.cas")

    if reference.decision_source != "app.intelligence.decision":
        errors.append(
            "decision_source must remain app.intelligence.decision"
        )

    if reference.d13_source != "app.intelligence.decision.d13":
        errors.append(
            "d13_source must remain app.intelligence.decision.d13"
        )

    return errors


def validate_cas_status_assessment_integrity(
    assessment: CASStatusAssessment,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(assessment, CASStatusAssessment):
        return ["assessment must be CASStatusAssessment"]

    scores = (
        ("completeness_score", assessment.completeness_score),
        ("freshness_score", assessment.freshness_score),
        ("confidence_score", assessment.confidence_score),
        ("quality_score", assessment.quality_score),
    )

    for name, value in scores:
        if not isinstance(value, (int, float)):
            errors.append(f"{name} must be numeric")
        elif value < 0.0 or value > 1.0:
            errors.append(f"{name} must be between 0 and 1")

    if assessment.gate_count < 0:
        errors.append("gate_count cannot be negative")

    if assessment.metadata.get("cas_generation") is True:
        errors.append("assessment cannot generate CAS")

    if assessment.metadata.get("cas_override") is True:
        errors.append("assessment cannot override CAS")

    if assessment.metadata.get("d13_mutation") is True:
        errors.append("assessment cannot mutate D13")

    if assessment.metadata.get("risk_override") is True:
        errors.append("assessment cannot override risk")

    if assessment.metadata.get("execution") is True:
        errors.append("assessment cannot execute")

    return errors


def validate_cas_status_presentation_integrity(
    presentation: CASStatusPresentation,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(presentation, CASStatusPresentation):
        return ["presentation must be CASStatusPresentation"]

    if not _cas_text(presentation.title):
        errors.append("title is required")

    if not isinstance(presentation.overall_state, CASGateState):
        errors.append("overall_state is invalid")

    if not isinstance(presentation.overall_decision, CASDecision):
        errors.append("overall_decision is invalid")

    if not isinstance(presentation.gates, list):
        errors.append("gates must be a list")
    else:
        for item in presentation.gates:
            if not isinstance(item, CASGateItem):
                errors.append("presentation contains invalid gate item")
                break

    if presentation.cas_source != "app.cas":
        errors.append("presentation cas_source must remain app.cas")

    if presentation.metadata.get("cas_generation") is True:
        errors.append("presentation cannot generate CAS")

    if presentation.metadata.get("cas_override") is True:
        errors.append("presentation cannot override CAS")

    if presentation.metadata.get("d13_mutation") is True:
        errors.append("presentation cannot mutate D13")

    if presentation.metadata.get("execution") is True:
        errors.append("presentation cannot execute")

    return errors


def validate_cas_status_result_integrity(
    result: CASStatusResult,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(result, CASStatusResult):
        return ["result must be CASStatusResult"]

    errors.extend(
        validate_cas_status_reference_integrity(result.reference)
    )
    errors.extend(
        validate_cas_status_assessment_integrity(result.assessment)
    )
    errors.extend(
        validate_cas_status_presentation_integrity(result.presentation)
    )

    if not isinstance(result.decision, CASDecision):
        errors.append("decision is invalid")

    if not isinstance(result.resolution, CASResolutionStatus):
        errors.append("resolution is invalid")

    if result.authority_valid is not True:
        errors.append("authority_valid must be true")

    forbidden = (
        "cas_generation",
        "cas_override",
        "d13_mutation",
        "risk_override",
        "execution",
        "upstream_mutation",
    )

    for key in forbidden:
        if result.metadata.get(key) is True:
            errors.append(
                f"result cannot enable forbidden authority: {key}"
            )

    return errors


def validate_cas_status_registry_snapshot_integrity(
    snapshot: CASStatusRegistrySnapshot,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(snapshot, CASStatusRegistrySnapshot):
        return ["snapshot must be CASStatusRegistrySnapshot"]

    if snapshot.engine != CAS_STATUS_ENGINE:
        errors.append("snapshot engine mismatch")

    if snapshot.version != CAS_STATUS_VERSION:
        errors.append("snapshot version mismatch")

    if snapshot.count != len(snapshot.entries):
        errors.append("snapshot count mismatch")

    for entry in snapshot.entries:
        if not isinstance(entry, CASStatusRegistryEntry):
            errors.append("snapshot contains invalid registry entry")
            break

        errors.extend(
            validate_cas_status_reference_integrity(entry.reference)
        )

    return errors


def validate_cas_status_service_result_integrity(
    service_result: CASStatusServiceResult,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(service_result, CASStatusServiceResult):
        return ["service_result must be CASStatusServiceResult"]

    if service_result.result is not None:
        errors.extend(
            validate_cas_status_result_integrity(
                service_result.result
            )
        )

    if service_result.assessment is not None:
        errors.extend(
            validate_cas_status_assessment_integrity(
                service_result.assessment
            )
        )

    if service_result.success and service_result.result is None:
        errors.append(
            "successful service result requires result"
        )

    return errors


# ------------------------------------------------------------
# TERMINAL SUMMARY
# ------------------------------------------------------------

def build_cas_status_summary(
    result: CASStatusResult,
) -> Dict[str, Any]:
    if not isinstance(result, CASStatusResult):
        return {
            "status": "INVALID",
            "decision": CASDecision.BLOCK.value,
            "resolution": CASResolutionStatus.BLOCKED.value,
            "gate_count": 0,
            "restrictions": [],
            "flags": ["invalid_result"],
        }

    assessment = result.assessment
    presentation = result.presentation

    return {
        "engine": CAS_STATUS_ENGINE,
        "version": CAS_STATUS_VERSION,
        "market": result.reference.market,
        "instrument": result.reference.instrument,
        "symbol": result.reference.symbol,
        "contract": result.reference.contract,
        "timeframe": result.reference.timeframe,
        "decision": result.decision.value,
        "resolution": result.resolution.value,
        "status": presentation.status.value,
        "overall_state": presentation.overall_state.value,
        "overall_decision": presentation.overall_decision.value,
        "readiness": assessment.readiness.value,
        "data_state": assessment.data_state.value,
        "consistency": assessment.consistency.value,
        "gate_count": assessment.gate_count,
        "completeness_score": round(
            assessment.completeness_score, 6
        ),
        "freshness_score": round(
            assessment.freshness_score, 6
        ),
        "confidence_score": round(
            assessment.confidence_score, 6
        ),
        "quality_score": round(
            assessment.quality_score, 6
        ),
        "requirements_met": assessment.requirements_met,
        "authority_valid": result.authority_valid,
        "restrictions": list(result.restrictions),
        "flags": list(result.flags),
        "cas_source": result.reference.cas_source,
        "decision_source": result.reference.decision_source,
        "d13_source": result.reference.d13_source,
        "metadata": _cas_serialize_value(result.metadata),
    }


# ------------------------------------------------------------
# PUBLIC EXPORTS
# ------------------------------------------------------------

__all__ = [
    # Constants
    "CAS_STATUS_ENGINE",
    "CAS_STATUS_VERSION",
    "CAS_STATUS_AUTHORITY",

    # Enums
    "CASStatus",
    "CASMode",
    "CASPriority",
    "CASSeverity",
    "CASSourceType",
    "CASContractStatus",
    "CASCategory",
    "CASGateState",
    "CASDecision",
    "CASDataState",
    "CASConsistency",
    "CASReadiness",
    "CASResolutionStatus",

    # Core contracts
    "CASStatusRequest",
    "CASGateItem",
    "CASStatusReference",
    "CASContractValidation",
    "CASStatusRequirements",
    "CASStatusAssessment",
    "CASResolutionRules",
    "CASStatusPresentation",
    "CASStatusResult",
    "CASStatusSourceMap",

    # Registry / service
    "CASStatusRegistryEntry",
    "CASStatusRegistrySnapshot",
    "CASStatusServiceResult",
    "CASStatusRegistry",
    "CASStatusService",

    # Builders / validators
    "normalize_cas_status_request",
    "validate_cas_status_request",
    "build_cas_status_request",
    "build_cas_status_reference",
    "build_cas_status_requirements",
    "validate_cas_status_result",
    "validate_cas_status_result_authority",
    "validate_cas_status_registry",
    "cas_status_registry_health",

    # Service helpers
    "get_cas_status_service",
    "resolve_terminal_cas_status",
    "get_terminal_cas_status_reference",
    "terminal_cas_status_snapshot",
    "terminal_cas_status_count",
    "terminal_cas_status_health",
    "terminal_cas_status_integrity",
    "terminal_cas_status_operational_check",
    "terminal_cas_status_service_info",

    # Serialization
    "serialize_cas_gate_item",
    "serialize_cas_status_reference",
    "serialize_cas_status_assessment",
    "serialize_cas_status_presentation",
    "serialize_cas_status_result",
    "serialize_cas_status_service_result",
    "serialize_cas_status_source_map",
    "serialize_cas_status_registry_snapshot",

    # Integrity
    "validate_cas_gate_item_integrity",
    "validate_cas_status_reference_integrity",
    "validate_cas_status_assessment_integrity",
    "validate_cas_status_presentation_integrity",
    "validate_cas_status_result_integrity",
    "validate_cas_status_registry_snapshot_integrity",
    "validate_cas_status_service_result_integrity",

    # Summary
    "build_cas_status_summary",
]