# ============================================================
# ROBOMLM_PLUS
# app/terminal/risk_panel.py
# PART 1 — Foundation / Contracts / Authority
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


# ============================================================
# ENGINE IDENTITY
# ============================================================

RISK_PANEL_ENGINE = "ROBOMLM_TERMINAL_RISK_PANEL"
RISK_PANEL_VERSION = "1.0"


# ============================================================
# ENUMS
# ============================================================

class RiskPanelStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    READY = "READY"
    PARTIAL = "PARTIAL"
    STALE = "STALE"
    INVALID = "INVALID"
    ERROR = "ERROR"


class RiskPanelMode(str, Enum):
    PAPER = "PAPER"
    DEMO = "DEMO"
    LIVE = "LIVE"
    UNKNOWN = "UNKNOWN"


class RiskPanelPriority(str, Enum):
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskPanelSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskPanelSourceType(str, Enum):
    RISK_ENGINE = "RISK_ENGINE"
    RISK_CORTEX = "RISK_CORTEX"
    DECISION_CORTEX = "DECISION_CORTEX"
    D13 = "D13"
    MARKET_CONTEXT = "MARKET_CONTEXT"
    EVIDENCE_CORTEX = "EVIDENCE_CORTEX"
    CAS = "CAS"
    MEMORY = "MEMORY"
    EXTERNAL = "EXTERNAL"
    UNKNOWN = "UNKNOWN"


class RiskPanelContractStatus(str, Enum):
    CREATED = "CREATED"
    VALID = "VALID"
    INVALID = "INVALID"
    READY = "READY"


class RiskPanelCategory(str, Enum):
    EXPOSURE = "EXPOSURE"
    POSITION = "POSITION"
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"
    DRAWDOWN = "DRAWDOWN"
    LEVERAGE = "LEVERAGE"
    LIQUIDITY = "LIQUIDITY"
    VOLATILITY = "VOLATILITY"
    CONCENTRATION = "CONCENTRATION"
    CORRELATION = "CORRELATION"
    CAPITAL = "CAPITAL"
    PORTFOLIO = "PORTFOLIO"
    CAS = "CAS"
    RESTRICTION = "RESTRICTION"
    OTHER = "OTHER"


class RiskPanelRiskLevel(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


# ============================================================
# NORMALIZATION HELPERS
# ============================================================

def _rp_text(value: Any, default: str = "") -> str:
    if value is None:
        return default

    text = str(value).strip()

    return text if text else default


def _rp_enum(
    value: Any,
    enum_cls: Any,
    default: Any,
) -> Any:

    if isinstance(value, enum_cls):
        return value

    if value is None:
        return default

    try:
        return enum_cls(str(value).strip().upper())
    except (ValueError, TypeError):
        return default


def _rp_number(
    value: Any,
    default: Optional[float] = None,
) -> Optional[float]:

    if value is None:
        return default

    try:
        number = float(value)

        if number != number:
            return default

        return number

    except (TypeError, ValueError):
        return default


def _rp_timestamp(
    value: Any,
    default: Optional[datetime] = None,
) -> Optional[datetime]:

    if value is None:
        return default

    if isinstance(value, datetime):
        return value

    try:
        return datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        )
    except (TypeError, ValueError):
        return default


# ============================================================
# REQUEST CONTRACT
# ============================================================

@dataclass
class RiskPanelRequest:
    request_id: str = ""
    market: str = ""
    instrument: str = ""
    symbol: str = ""
    contract: str = ""
    timeframe: str = ""

    mode: RiskPanelMode = RiskPanelMode.UNKNOWN
    priority: RiskPanelPriority = RiskPanelPriority.NORMAL

    include_exposure: bool = True
    include_position: bool = True
    include_stop_loss: bool = True
    include_take_profit: bool = True
    include_drawdown: bool = True
    include_leverage: bool = True
    include_liquidity: bool = True
    include_cas: bool = True

    created_at: Optional[datetime] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# RISK ITEM
# ============================================================

@dataclass
class RiskPanelItem:
    item_id: str = ""
    label: str = ""

    category: RiskPanelCategory = RiskPanelCategory.OTHER
    risk_level: RiskPanelRiskLevel = RiskPanelRiskLevel.UNKNOWN
    severity: RiskPanelSeverity = RiskPanelSeverity.INFO
    source_type: RiskPanelSourceType = (
        RiskPanelSourceType.UNKNOWN
    )

    value: Optional[float] = None
    threshold: Optional[float] = None
    utilization: Optional[float] = None

    unit: str = ""
    status: RiskPanelStatus = RiskPanelStatus.UNKNOWN

    source: str = ""
    message: str = ""

    timestamp: Optional[datetime] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# RISK REFERENCE
# ============================================================

@dataclass
class RiskPanelReference:
    market: str = ""
    instrument: str = ""
    symbol: str = ""
    contract: str = ""
    timeframe: str = ""

    risk_source: str = ""
    cas_source: str = ""
    decision_source: str = ""
    d13_source: str = ""

    as_of: Optional[datetime] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# CONTRACT VALIDATION
# ============================================================

@dataclass
class RiskPanelContractValidation:
    status: RiskPanelContractStatus = (
        RiskPanelContractStatus.CREATED
    )

    valid: bool = False

    errors: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    checked_at: Optional[datetime] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# AUTHORITY BOUNDARY
# ============================================================

def risk_panel_authority_boundary() -> Dict[str, bool]:
    """
    Terminal Risk Panel is a presentation / aggregation layer.

    It may DISPLAY upstream risk information.

    It must NOT become the Risk Engine, CAS authority,
    D13 authority, or execution authority.
    """

    return {
        # Allowed
        "presentation_authority": True,
        "risk_display_authority": True,
        "risk_aggregation_authority": True,

        # Forbidden
        "market_data_authority": False,
        "evidence_generation_authority": False,
        "intelligence_generation_authority": False,
        "market_context_authority": False,
        "decision_generation_authority": False,
        "d13_authority": False,
        "risk_generation_authority": False,
        "risk_override_authority": False,
        "cas_authority": False,
        "cas_override_authority": False,
        "execution_authority": False,
        "order_authority": False,
        "position_authority": False,
        "upstream_mutation_authority": False,
    }


def validate_risk_panel_authority_boundary() -> bool:
    boundary = risk_panel_authority_boundary()

    forbidden_keys = (
        "market_data_authority",
        "evidence_generation_authority",
        "intelligence_generation_authority",
        "market_context_authority",
        "decision_generation_authority",
        "d13_authority",
        "risk_generation_authority",
        "risk_override_authority",
        "cas_authority",
        "cas_override_authority",
        "execution_authority",
        "order_authority",
        "position_authority",
        "upstream_mutation_authority",
    )

    return all(
        boundary.get(key) is False
        for key in forbidden_keys
    )


# ============================================================
# REQUEST NORMALIZATION
# ============================================================

def normalize_risk_panel_request(
    request: RiskPanelRequest,
) -> RiskPanelRequest:

    request.request_id = _rp_text(request.request_id)

    request.market = _rp_text(request.market).upper()
    request.instrument = _rp_text(
        request.instrument
    ).upper()
    request.symbol = _rp_text(
        request.symbol
    ).upper()
    request.contract = _rp_text(
        request.contract
    ).upper()
    request.timeframe = _rp_text(
        request.timeframe
    ).upper()

    request.mode = _rp_enum(
        request.mode,
        RiskPanelMode,
        RiskPanelMode.UNKNOWN,
    )

    request.priority = _rp_enum(
        request.priority,
        RiskPanelPriority,
        RiskPanelPriority.NORMAL,
    )

    request.include_exposure = bool(
        request.include_exposure
    )
    request.include_position = bool(
        request.include_position
    )
    request.include_stop_loss = bool(
        request.include_stop_loss
    )
    request.include_take_profit = bool(
        request.include_take_profit
    )
    request.include_drawdown = bool(
        request.include_drawdown
    )
    request.include_leverage = bool(
        request.include_leverage
    )
    request.include_liquidity = bool(
        request.include_liquidity
    )
    request.include_cas = bool(
        request.include_cas
    )

    request.created_at = _rp_timestamp(
        request.created_at
    )

    if not isinstance(request.metadata, dict):
        request.metadata = {}

    return request


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_risk_panel_request(
    request: RiskPanelRequest,
) -> RiskPanelContractValidation:

    errors: List[str] = []
    warnings: List[str] = []

    if request is None:
        return RiskPanelContractValidation(
            status=RiskPanelContractStatus.INVALID,
            valid=False,
            errors=["REQUEST_IS_NONE"],
            checked_at=datetime.utcnow(),
        )

    if not request.market:
        errors.append("MISSING_MARKET")

    if not request.instrument:
        errors.append("MISSING_INSTRUMENT")

    if not request.symbol:
        errors.append("MISSING_SYMBOL")

    if request.mode == RiskPanelMode.UNKNOWN:
        warnings.append("MODE_UNKNOWN")

    if not request.request_id:
        warnings.append("REQUEST_ID_MISSING")

    if not any(
        (
            request.include_exposure,
            request.include_position,
            request.include_stop_loss,
            request.include_take_profit,
            request.include_drawdown,
            request.include_leverage,
            request.include_liquidity,
            request.include_cas,
        )
    ):
        errors.append("NO_RISK_COMPONENT_SELECTED")

    valid = not errors

    return RiskPanelContractValidation(
        status=(
            RiskPanelContractStatus.VALID
            if valid
            else RiskPanelContractStatus.INVALID
        ),
        valid=valid,
        errors=list(dict.fromkeys(errors)),
        warnings=list(dict.fromkeys(warnings)),
        checked_at=datetime.utcnow(),
    )


# ============================================================
# REQUEST BUILDER
# ============================================================

def build_risk_panel_request(
    market: str,
    instrument: str,
    symbol: str,
    contract: str = "",
    timeframe: str = "",
    mode: RiskPanelMode = RiskPanelMode.UNKNOWN,
    priority: RiskPanelPriority = (
        RiskPanelPriority.NORMAL
    ),
    request_id: str = "",
    metadata: Optional[Dict[str, Any]] = None,
) -> RiskPanelRequest:

    request = RiskPanelRequest(
        request_id=request_id,
        market=market,
        instrument=instrument,
        symbol=symbol,
        contract=contract,
        timeframe=timeframe,
        mode=mode,
        priority=priority,
        created_at=datetime.utcnow(),
        metadata=dict(metadata or {}),
    )

    return normalize_risk_panel_request(request)


# ============================================================
# REFERENCE BUILDER
# ============================================================

def build_risk_panel_reference(
    request: RiskPanelRequest,
    risk_source: str = "app.intelligence.risk",
    cas_source: str = "app.cas",
    decision_source: str = "app.intelligence.decision",
    d13_source: str = "app.intelligence.decision.d13",
    as_of: Optional[datetime] = None,
) -> RiskPanelReference:

    return RiskPanelReference(
        market=request.market,
        instrument=request.instrument,
        symbol=request.symbol,
        contract=request.contract,
        timeframe=request.timeframe,
        risk_source=_rp_text(risk_source),
        cas_source=_rp_text(cas_source),
        decision_source=_rp_text(decision_source),
        d13_source=_rp_text(d13_source),
        as_of=as_of or datetime.utcnow(),
        metadata={
            "engine": RISK_PANEL_ENGINE,
            "version": RISK_PANEL_VERSION,
            "upstream_risk_required": True,
            "risk_generation": False,
            "risk_override": False,
            "d13_mutation": False,
            "cas_override": False,
        },
    )
# ============================================================
# RISK PANEL — PART 2
# Requirements / Assessment / Readiness
# ============================================================


class RiskPanelDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    INVALID = "INVALID"


class RiskPanelConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONDITIONAL = "CONDITIONAL"
    INCONSISTENT = "INCONSISTENT"
    UNKNOWN = "UNKNOWN"


class RiskPanelReadiness(str, Enum):
    READY = "READY"
    CONDITIONALLY_READY = "CONDITIONALLY_READY"
    NOT_READY = "NOT_READY"
    BLOCKED = "BLOCKED"


@dataclass
class RiskPanelRequirements:
    require_risk_source: bool = True
    require_reference: bool = True
    require_risk_items: bool = True

    require_exposure: bool = True
    require_position: bool = True
    require_stop_loss: bool = True
    require_take_profit: bool = True
    require_drawdown: bool = True
    require_leverage: bool = True
    require_liquidity: bool = False
    require_cas: bool = True

    minimum_completeness: float = 0.70
    minimum_freshness: float = 0.70
    minimum_confidence: float = 0.70
    minimum_quality: float = 0.70

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class RiskPanelAssessment:
    data_state: RiskPanelDataState = (
        RiskPanelDataState.MISSING
    )

    consistency: RiskPanelConsistency = (
        RiskPanelConsistency.UNKNOWN
    )

    readiness: RiskPanelReadiness = (
        RiskPanelReadiness.BLOCKED
    )

    completeness_score: float = 0.0
    freshness_score: float = 0.0
    confidence_score: float = 0.0
    quality_score: float = 0.0

    item_count: int = 0

    requirements_met: bool = False

    flags: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def build_risk_panel_requirements(
    request: RiskPanelRequest,
) -> RiskPanelRequirements:

    return RiskPanelRequirements(
        require_risk_source=True,
        require_reference=True,
        require_risk_items=True,

        require_exposure=request.include_exposure,
        require_position=request.include_position,
        require_stop_loss=request.include_stop_loss,
        require_take_profit=request.include_take_profit,
        require_drawdown=request.include_drawdown,
        require_leverage=request.include_leverage,
        require_liquidity=request.include_liquidity,
        require_cas=request.include_cas,

        metadata={
            "engine": RISK_PANEL_ENGINE,
            "version": RISK_PANEL_VERSION,
        },
    )


def evaluate_risk_panel_data_state(
    reference: RiskPanelReference,
    items: List[RiskPanelItem],
) -> RiskPanelDataState:

    if reference is None:
        return RiskPanelDataState.MISSING

    if not reference.market:
        return RiskPanelDataState.INVALID

    if not reference.instrument:
        return RiskPanelDataState.INVALID

    if not reference.symbol:
        return RiskPanelDataState.INVALID

    if not reference.risk_source:
        return RiskPanelDataState.PARTIAL

    if not items:
        return RiskPanelDataState.MISSING

    invalid_items = False

    for item in items:
        if item is None:
            invalid_items = True
            break

        if not item.item_id or not item.label:
            invalid_items = True
            break

        if not isinstance(
            item.category,
            RiskPanelCategory,
        ):
            invalid_items = True
            break

    if invalid_items:
        return RiskPanelDataState.INVALID

    return RiskPanelDataState.COMPLETE


def evaluate_risk_panel_consistency(
    reference: RiskPanelReference,
    items: List[RiskPanelItem],
) -> RiskPanelConsistency:

    if reference is None:
        return RiskPanelConsistency.UNKNOWN

    if not items:
        return RiskPanelConsistency.UNKNOWN

    if not reference.risk_source:
        return RiskPanelConsistency.CONDITIONAL

    for item in items:

        if item is None:
            return RiskPanelConsistency.INCONSISTENT

        if (
            item.status == RiskPanelStatus.INVALID
            or item.status == RiskPanelStatus.ERROR
        ):
            return RiskPanelConsistency.INCONSISTENT

        if (
            item.risk_level
            == RiskPanelRiskLevel.UNKNOWN
        ):
            return RiskPanelConsistency.CONDITIONAL

    return RiskPanelConsistency.CONSISTENT


def evaluate_risk_panel_requirements(
    request: RiskPanelRequest,
    reference: RiskPanelReference,
    items: List[RiskPanelItem],
    requirements: RiskPanelRequirements,
) -> tuple[bool, List[str]]:

    unmet: List[str] = []

    if (
        requirements.require_reference
        and reference is None
    ):
        unmet.append("REFERENCE_REQUIRED")

    if (
        requirements.require_risk_source
        and (
            reference is None
            or not reference.risk_source
        )
    ):
        unmet.append("RISK_SOURCE_REQUIRED")

    if (
        requirements.require_risk_items
        and not items
    ):
        unmet.append("RISK_ITEMS_REQUIRED")

    categories = {
        item.category
        for item in items
        if item is not None
    }

    category_requirements = (
        (
            requirements.require_exposure,
            RiskPanelCategory.EXPOSURE,
            "EXPOSURE_REQUIRED",
        ),
        (
            requirements.require_position,
            RiskPanelCategory.POSITION,
            "POSITION_REQUIRED",
        ),
        (
            requirements.require_stop_loss,
            RiskPanelCategory.STOP_LOSS,
            "STOP_LOSS_REQUIRED",
        ),
        (
            requirements.require_take_profit,
            RiskPanelCategory.TAKE_PROFIT,
            "TAKE_PROFIT_REQUIRED",
        ),
        (
            requirements.require_drawdown,
            RiskPanelCategory.DRAWDOWN,
            "DRAWDOWN_REQUIRED",
        ),
        (
            requirements.require_leverage,
            RiskPanelCategory.LEVERAGE,
            "LEVERAGE_REQUIRED",
        ),
        (
            requirements.require_liquidity,
            RiskPanelCategory.LIQUIDITY,
            "LIQUIDITY_REQUIRED",
        ),
        (
            requirements.require_cas,
            RiskPanelCategory.CAS,
            "CAS_REQUIRED",
        ),
    )

    for required, category, message in category_requirements:
        if required and category not in categories:
            unmet.append(message)

    return (
        not unmet,
        list(dict.fromkeys(unmet)),
    )


def evaluate_risk_panel_freshness(
    reference: RiskPanelReference,
    items: List[RiskPanelItem],
    now: Optional[datetime] = None,
) -> float:

    if reference is None:
        return 0.0

    current_time = now or datetime.utcnow()

    timestamps: List[datetime] = []

    if reference.as_of is not None:
        timestamps.append(reference.as_of)

    for item in items:
        if item is not None and item.timestamp is not None:
            timestamps.append(item.timestamp)

    if not timestamps:
        return 0.0

    ages: List[float] = []

    for timestamp in timestamps:
        try:
            age_seconds = (
                current_time - timestamp
            ).total_seconds()

            age_seconds = max(
                0.0,
                age_seconds,
            )

            ages.append(age_seconds)

        except TypeError:
            return 0.0

    if not ages:
        return 0.0

    average_age = sum(ages) / len(ages)

    # Presentation freshness decay.
    # This is NOT a market-risk formula.
    if average_age <= 5:
        return 1.0

    if average_age <= 30:
        return 0.95

    if average_age <= 60:
        return 0.90

    if average_age <= 120:
        return 0.80

    if average_age <= 300:
        return 0.65

    if average_age <= 600:
        return 0.45

    if average_age <= 1800:
        return 0.25

    return 0.0


def evaluate_risk_panel_completeness(
    request: RiskPanelRequest,
    items: List[RiskPanelItem],
) -> float:

    if request is None:
        return 0.0

    required_categories: List[RiskPanelCategory] = []

    if request.include_exposure:
        required_categories.append(
            RiskPanelCategory.EXPOSURE
        )

    if request.include_position:
        required_categories.append(
            RiskPanelCategory.POSITION
        )

    if request.include_stop_loss:
        required_categories.append(
            RiskPanelCategory.STOP_LOSS
        )

    if request.include_take_profit:
        required_categories.append(
            RiskPanelCategory.TAKE_PROFIT
        )

    if request.include_drawdown:
        required_categories.append(
            RiskPanelCategory.DRAWDOWN
        )

    if request.include_leverage:
        required_categories.append(
            RiskPanelCategory.LEVERAGE
        )

    if request.include_liquidity:
        required_categories.append(
            RiskPanelCategory.LIQUIDITY
        )

    if request.include_cas:
        required_categories.append(
            RiskPanelCategory.CAS
        )

    if not required_categories:
        return 1.0

    available_categories = {
        item.category
        for item in items
        if item is not None
    }

    matched = sum(
        1
        for category in required_categories
        if category in available_categories
    )

    return matched / len(required_categories)


def evaluate_risk_panel_confidence(
    items: List[RiskPanelItem],
) -> float:

    if not items:
        return 0.0

    scores: List[float] = []

    for item in items:

        if item is None:
            scores.append(0.0)
            continue

        score = 1.0

        if item.risk_level == RiskPanelRiskLevel.UNKNOWN:
            score -= 0.35

        if item.status in (
            RiskPanelStatus.UNKNOWN,
            RiskPanelStatus.PARTIAL,
        ):
            score -= 0.20

        if not item.source:
            score -= 0.20

        if not item.message:
            score -= 0.05

        scores.append(
            max(0.0, min(1.0, score))
        )

    return sum(scores) / len(scores)


def evaluate_risk_panel_quality(
    completeness_score: float,
    freshness_score: float,
    confidence_score: float,
    consistency: RiskPanelConsistency,
) -> float:

    consistency_score = {
        RiskPanelConsistency.CONSISTENT: 1.0,
        RiskPanelConsistency.CONDITIONAL: 0.70,
        RiskPanelConsistency.UNKNOWN: 0.40,
        RiskPanelConsistency.INCONSISTENT: 0.0,
    }.get(consistency, 0.0)

    # Terminal presentation-quality contract only.
    # It does NOT represent trading-risk quality,
    # expected return, win probability, or alpha.
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


def evaluate_risk_panel_readiness(
    data_state: RiskPanelDataState,
    consistency: RiskPanelConsistency,
    requirements_met: bool,
    quality_score: float,
    requirements: RiskPanelRequirements,
) -> RiskPanelReadiness:

    if data_state == RiskPanelDataState.INVALID:
        return RiskPanelReadiness.BLOCKED

    if consistency == RiskPanelConsistency.INCONSISTENT:
        return RiskPanelReadiness.BLOCKED

    if data_state == RiskPanelDataState.MISSING:
        return RiskPanelReadiness.BLOCKED

    if not requirements_met:
        if quality_score >= requirements.minimum_quality:
            return RiskPanelReadiness.CONDITIONALLY_READY

        return RiskPanelReadiness.NOT_READY

    if quality_score < 0.50:
        return RiskPanelReadiness.NOT_READY

    if (
        quality_score < requirements.minimum_quality
        or consistency
        == RiskPanelConsistency.CONDITIONAL
        or data_state
        == RiskPanelDataState.PARTIAL
    ):
        return RiskPanelReadiness.CONDITIONALLY_READY

    return RiskPanelReadiness.READY


def build_risk_panel_assessment(
    request: RiskPanelRequest,
    reference: RiskPanelReference,
    items: Optional[List[RiskPanelItem]] = None,
    requirements: Optional[RiskPanelRequirements] = None,
) -> RiskPanelAssessment:

    resolved_items = list(items or [])

    resolved_requirements = (
        requirements
        or build_risk_panel_requirements(request)
    )

    data_state = evaluate_risk_panel_data_state(
        reference,
        resolved_items,
    )

    consistency = evaluate_risk_panel_consistency(
        reference,
        resolved_items,
    )

    requirements_met, unmet = (
        evaluate_risk_panel_requirements(
            request,
            reference,
            resolved_items,
            resolved_requirements,
        )
    )

    completeness = evaluate_risk_panel_completeness(
        request,
        resolved_items,
    )

    freshness = evaluate_risk_panel_freshness(
        reference,
        resolved_items,
    )

    confidence = evaluate_risk_panel_confidence(
        resolved_items,
    )

    quality = evaluate_risk_panel_quality(
        completeness_score=completeness,
        freshness_score=freshness,
        confidence_score=confidence,
        consistency=consistency,
    )

    readiness = evaluate_risk_panel_readiness(
        data_state=data_state,
        consistency=consistency,
        requirements_met=requirements_met,
        quality_score=quality,
        requirements=resolved_requirements,
    )

    flags: List[str] = list(unmet)

    if freshness < resolved_requirements.minimum_freshness:
        flags.append("LOW_FRESHNESS")

    if confidence < resolved_requirements.minimum_confidence:
        flags.append("LOW_CONFIDENCE")

    if completeness < resolved_requirements.minimum_completeness:
        flags.append("LOW_COMPLETENESS")

    if quality < resolved_requirements.minimum_quality:
        flags.append("LOW_QUALITY")

    if consistency == RiskPanelConsistency.CONDITIONAL:
        flags.append("CONDITIONAL_CONSISTENCY")

    if data_state == RiskPanelDataState.PARTIAL:
        flags.append("PARTIAL_DATA")

    return RiskPanelAssessment(
        data_state=data_state,
        consistency=consistency,
        readiness=readiness,
        completeness_score=round(
            completeness,
            6,
        ),
        freshness_score=round(
            freshness,
            6,
        ),
        confidence_score=round(
            confidence,
            6,
        ),
        quality_score=round(
            quality,
            6,
        ),
        item_count=len(resolved_items),
        requirements_met=requirements_met,
        flags=list(dict.fromkeys(flags)),
        metadata={
            "engine": RISK_PANEL_ENGINE,
            "version": RISK_PANEL_VERSION,
            "assessment_only": True,
            "risk_generation": False,
            "risk_override": False,
            "d13_mutation": False,
            "cas_override": False,
        },
    )
# ============================================================
# RISK PANEL — PART 3
# Resolution / Presentation / Result / Source Mapping
# ============================================================


class RiskPanelDecision(str, Enum):
    ALLOW = "ALLOW"
    ALLOW_WITH_RESTRICTION = "ALLOW_WITH_RESTRICTION"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCK = "BLOCK"


class RiskPanelResolutionStatus(str, Enum):
    RESOLVED = "RESOLVED"
    CONDITIONAL = "CONDITIONAL"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"


@dataclass
class RiskPanelResolutionRules:
    allow_when_ready: bool = True
    allow_when_conditionally_ready: bool = True
    review_when_not_ready: bool = True
    block_when_invalid: bool = True
    block_when_inconsistent: bool = True
    block_on_authority_violation: bool = True

    require_risk_source: bool = True
    require_cas_when_declared: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class RiskPanelPresentation:
    title: str = "Risk Panel"

    overall_risk_level: RiskPanelRiskLevel = (
        RiskPanelRiskLevel.UNKNOWN
    )

    items: List[RiskPanelItem] = field(
        default_factory=list
    )

    risk_source: str = ""
    cas_source: str = ""
    decision_source: str = ""
    d13_present: bool = False

    status: RiskPanelStatus = (
        RiskPanelStatus.UNKNOWN
    )

    resolution: RiskPanelResolutionStatus = (
        RiskPanelResolutionStatus.REVIEW_REQUIRED
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


@dataclass
class RiskPanelResult:
    request: RiskPanelRequest
    reference: RiskPanelReference
    assessment: RiskPanelAssessment
    presentation: RiskPanelPresentation

    decision: RiskPanelDecision = (
        RiskPanelDecision.REVIEW_REQUIRED
    )

    resolution: RiskPanelResolutionStatus = (
        RiskPanelResolutionStatus.REVIEW_REQUIRED
    )

    flags: List[str] = field(
        default_factory=list
    )

    restrictions: List[str] = field(
        default_factory=list
    )

    authority_valid: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class RiskPanelSourceMap:
    risk_panel_engine: str = RISK_PANEL_ENGINE

    risk_source: str = "app.intelligence.risk"
    risk_cortex_source: str = "app.intelligence.risk"
    decision_source: str = "app.intelligence.decision"
    d13_source: str = "app.intelligence.decision.d13"

    market_context_source: str = (
        "app.intelligence.market_context"
    )

    evidence_source: str = (
        "app.intelligence.evidence"
    )

    cas_source: str = "app.cas"
    memory_source: str = "app.intelligence.memory"

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# RESOLUTION RULES
# ============================================================

def build_risk_panel_resolution_rules(
    request: RiskPanelRequest,
) -> RiskPanelResolutionRules:

    return RiskPanelResolutionRules(
        allow_when_ready=True,
        allow_when_conditionally_ready=True,
        review_when_not_ready=True,
        block_when_invalid=True,
        block_when_inconsistent=True,
        block_on_authority_violation=True,
        require_risk_source=True,
        require_cas_when_declared=bool(
            request.include_cas
        ),
        metadata={
            "engine": RISK_PANEL_ENGINE,
            "version": RISK_PANEL_VERSION,
        },
    )


# ============================================================
# RESOLUTION FLAGS
# ============================================================

def collect_risk_panel_resolution_flags(
    assessment: RiskPanelAssessment,
    reference: RiskPanelReference,
    rules: RiskPanelResolutionRules,
) -> List[str]:

    flags: List[str] = []

    if assessment.data_state == RiskPanelDataState.INVALID:
        flags.append("INVALID_DATA")

    if (
        assessment.consistency
        == RiskPanelConsistency.INCONSISTENT
    ):
        flags.append(
            "INCONSISTENT_UPSTREAM_RISK_STATE"
        )

    if (
        assessment.readiness
        == RiskPanelReadiness.NOT_READY
    ):
        flags.append("NOT_READY")

    if (
        assessment.readiness
        == RiskPanelReadiness.BLOCKED
    ):
        flags.append("BLOCKED")

    if rules.require_risk_source:
        if (
            reference is None
            or not reference.risk_source
        ):
            flags.append("MISSING_RISK_SOURCE")

    if (
        rules.require_cas_when_declared
        and (
            reference is None
            or not reference.cas_source
        )
    ):
        flags.append("MISSING_CAS_SOURCE")

    if assessment.freshness_score < 0.50:
        flags.append("STALE_OR_LOW_FRESHNESS")

    if assessment.confidence_score < 0.50:
        flags.append("LOW_CONFIDENCE")

    if assessment.completeness_score < 0.50:
        flags.append("LOW_COMPLETENESS")

    return list(dict.fromkeys(flags))


# ============================================================
# RESTRICTIONS
# ============================================================

def collect_risk_panel_restrictions(
    assessment: RiskPanelAssessment,
    reference: RiskPanelReference,
) -> List[str]:

    restrictions: List[str] = []

    if (
        assessment.readiness
        == RiskPanelReadiness.CONDITIONALLY_READY
    ):
        restrictions.append(
            "CONDITIONAL_READINESS"
        )

    if assessment.freshness_score < 0.75:
        restrictions.append(
            "FRESHNESS_RESTRICTION"
        )

    if assessment.confidence_score < 0.75:
        restrictions.append(
            "CONFIDENCE_RESTRICTION"
        )

    if assessment.completeness_score < 0.75:
        restrictions.append(
            "COMPLETENESS_RESTRICTION"
        )

    if reference is None or not reference.cas_source:
        restrictions.append(
            "CAS_STATUS_NOT_AVAILABLE"
        )

    return list(dict.fromkeys(restrictions))


# ============================================================
# OVERALL RISK LEVEL — DISPLAY AGGREGATION ONLY
# ============================================================

def _aggregate_risk_panel_level(
    items: List[RiskPanelItem],
) -> RiskPanelRiskLevel:

    if not items:
        return RiskPanelRiskLevel.UNKNOWN

    levels = [
        item.risk_level
        for item in items
        if item is not None
    ]

    if not levels:
        return RiskPanelRiskLevel.UNKNOWN

    priority = {
        RiskPanelRiskLevel.NONE: 0,
        RiskPanelRiskLevel.LOW: 1,
        RiskPanelRiskLevel.MODERATE: 2,
        RiskPanelRiskLevel.HIGH: 3,
        RiskPanelRiskLevel.CRITICAL: 4,
        RiskPanelRiskLevel.UNKNOWN: -1,
    }

    valid_levels = [
        level
        for level in levels
        if level != RiskPanelRiskLevel.UNKNOWN
    ]

    if not valid_levels:
        return RiskPanelRiskLevel.UNKNOWN

    return max(
        valid_levels,
        key=lambda level: priority[level],
    )


# ============================================================
# PRESENTATION BUILDER
# ============================================================

def build_risk_panel_presentation(
    request: RiskPanelRequest,
    reference: RiskPanelReference,
    assessment: RiskPanelAssessment,
    items: Optional[List[RiskPanelItem]] = None,
    flags: Optional[List[str]] = None,
    restrictions: Optional[List[str]] = None,
) -> RiskPanelPresentation:

    resolved_items = list(items or [])
    resolved_flags = list(flags or [])
    resolved_restrictions = list(
        restrictions or []
    )

    if (
        assessment.readiness
        == RiskPanelReadiness.READY
    ):
        status = RiskPanelStatus.READY
        resolution = (
            RiskPanelResolutionStatus.RESOLVED
        )

    elif (
        assessment.readiness
        == RiskPanelReadiness.CONDITIONALLY_READY
    ):
        status = RiskPanelStatus.PARTIAL
        resolution = (
            RiskPanelResolutionStatus.CONDITIONAL
        )

    elif (
        assessment.readiness
        == RiskPanelReadiness.BLOCKED
    ):
        status = RiskPanelStatus.INVALID
        resolution = (
            RiskPanelResolutionStatus.BLOCKED
        )

    else:
        status = RiskPanelStatus.PARTIAL
        resolution = (
            RiskPanelResolutionStatus.REVIEW_REQUIRED
        )

    d13_present = bool(
        reference
        and reference.d13_source
    )

    return RiskPanelPresentation(
        title="Risk Panel",
        overall_risk_level=_aggregate_risk_panel_level(
            resolved_items
        ),
        items=resolved_items,
        risk_source=(
            reference.risk_source
            if reference
            else ""
        ),
        cas_source=(
            reference.cas_source
            if reference
            else ""
        ),
        decision_source=(
            reference.decision_source
            if reference
            else ""
        ),
        d13_present=d13_present,
        status=status,
        resolution=resolution,
        restrictions=resolved_restrictions,
        flags=resolved_flags,
        metadata={
            "engine": RISK_PANEL_ENGINE,
            "version": RISK_PANEL_VERSION,

            # Critical architectural boundaries.
            "display_aggregation_only": True,
            "risk_generation": False,
            "risk_override": False,
            "d13_mutation": False,
            "decision_generation": False,
            "cas_override": False,
            "execution": False,
        },
    )


# ============================================================
# RESULT RESOLUTION
# ============================================================

def resolve_risk_panel(
    request: RiskPanelRequest,
    reference: RiskPanelReference,
    assessment: RiskPanelAssessment,
    items: Optional[List[RiskPanelItem]] = None,
    rules: Optional[RiskPanelResolutionRules] = None,
) -> RiskPanelResult:

    resolved_rules = (
        rules
        or build_risk_panel_resolution_rules(
            request
        )
    )

    resolved_items = list(items or [])

    flags = collect_risk_panel_resolution_flags(
        assessment=assessment,
        reference=reference,
        rules=resolved_rules,
    )

    restrictions = collect_risk_panel_restrictions(
        assessment=assessment,
        reference=reference,
    )

    authority_valid = (
        validate_risk_panel_authority_boundary()
    )

    if not authority_valid:
        flags.append(
            "AUTHORITY_BOUNDARY_INVALID"
        )

    # --------------------------------------------------------
    # HARD BLOCKS
    # --------------------------------------------------------

    if (
        resolved_rules.block_on_authority_violation
        and not authority_valid
    ):
        decision = RiskPanelDecision.BLOCK
        resolution = (
            RiskPanelResolutionStatus.BLOCKED
        )

    elif (
        assessment.data_state
        == RiskPanelDataState.INVALID
        or assessment.consistency
        == RiskPanelConsistency.INCONSISTENT
    ):
        decision = RiskPanelDecision.BLOCK
        resolution = (
            RiskPanelResolutionStatus.BLOCKED
        )

    elif (
        assessment.readiness
        == RiskPanelReadiness.BLOCKED
    ):
        decision = RiskPanelDecision.BLOCK
        resolution = (
            RiskPanelResolutionStatus.BLOCKED
        )

    # --------------------------------------------------------
    # REVIEW
    # --------------------------------------------------------

    elif (
        assessment.readiness
        == RiskPanelReadiness.NOT_READY
    ):
        decision = (
            RiskPanelDecision.REVIEW_REQUIRED
        )
        resolution = (
            RiskPanelResolutionStatus.REVIEW_REQUIRED
        )

    # --------------------------------------------------------
    # CONDITIONAL
    # --------------------------------------------------------

    elif (
        assessment.readiness
        == RiskPanelReadiness.CONDITIONALLY_READY
    ):
        decision = (
            RiskPanelDecision.ALLOW_WITH_RESTRICTION
        )
        resolution = (
            RiskPanelResolutionStatus.CONDITIONAL
        )

    # --------------------------------------------------------
    # READY
    # --------------------------------------------------------

    else:
        decision = RiskPanelDecision.ALLOW
        resolution = (
            RiskPanelResolutionStatus.RESOLVED
        )

    presentation = build_risk_panel_presentation(
        request=request,
        reference=reference,
        assessment=assessment,
        items=resolved_items,
        flags=flags,
        restrictions=restrictions,
    )

    return RiskPanelResult(
        request=request,
        reference=reference,
        assessment=assessment,
        presentation=presentation,
        decision=decision,
        resolution=resolution,
        flags=list(
            dict.fromkeys(flags)
        ),
        restrictions=list(
            dict.fromkeys(restrictions)
        ),
        authority_valid=authority_valid,
        metadata={
            "engine": RISK_PANEL_ENGINE,
            "version": RISK_PANEL_VERSION,

            # This terminal component cannot create
            # or modify upstream risk/decision authority.
            "risk_generation": False,
            "risk_override": False,
            "d13_mutation": False,
            "cas_override": False,
            "execution": False,
            "upstream_authority_preserved": True,
        },
    )


# ============================================================
# RESULT VALIDATION
# ============================================================

def validate_risk_panel_result(
    result: RiskPanelResult,
) -> List[str]:

    errors: List[str] = []

    if result is None:
        return ["RESULT_IS_NONE"]

    if result.request is None:
        errors.append("MISSING_REQUEST")

    if result.reference is None:
        errors.append("MISSING_REFERENCE")

    if result.assessment is None:
        errors.append("MISSING_ASSESSMENT")

    if result.presentation is None:
        errors.append("MISSING_PRESENTATION")

    if result.decision == RiskPanelDecision.ALLOW:
        if (
            result.resolution
            != RiskPanelResolutionStatus.RESOLVED
        ):
            errors.append(
                "ALLOW_REQUIRES_RESOLVED"
            )

    if (
        result.decision
        == RiskPanelDecision.ALLOW_WITH_RESTRICTION
    ):
        if (
            result.resolution
            != RiskPanelResolutionStatus.CONDITIONAL
        ):
            errors.append(
                "RESTRICTED_ALLOW_REQUIRES_CONDITIONAL"
            )

    if (
        result.decision
        == RiskPanelDecision.REVIEW_REQUIRED
    ):
        if (
            result.resolution
            != RiskPanelResolutionStatus.REVIEW_REQUIRED
        ):
            errors.append(
                "REVIEW_REQUIRES_REVIEW_STATUS"
            )

    if result.decision == RiskPanelDecision.BLOCK:
        if (
            result.resolution
            != RiskPanelResolutionStatus.BLOCKED
        ):
            errors.append(
                "BLOCK_REQUIRES_BLOCKED_STATUS"
            )

    if not result.authority_valid:
        errors.append(
            "AUTHORITY_INVALID"
        )

    return list(dict.fromkeys(errors))


# ============================================================
# AUTHORITY VALIDATION
# ============================================================

def validate_risk_panel_result_authority(
    result: RiskPanelResult,
) -> bool:

    if result is None:
        return False

    if not result.authority_valid:
        return False

    boundary = (
        risk_panel_authority_boundary()
    )

    forbidden = (
        "market_data_authority",
        "evidence_generation_authority",
        "intelligence_generation_authority",
        "market_context_authority",
        "decision_generation_authority",
        "d13_authority",
        "risk_generation_authority",
        "risk_override_authority",
        "cas_authority",
        "cas_override_authority",
        "execution_authority",
        "order_authority",
        "position_authority",
        "upstream_mutation_authority",
    )

    return all(
        boundary.get(key) is False
        for key in forbidden
    )
# ============================================================
# RISK PANEL — PART 4
# REGISTRY + SERVICE + OPERATIONAL HELPERS
# ============================================================

@dataclass
class RiskPanelRegistryEntry:
    key: str
    reference: RiskPanelReference
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RiskPanelRegistrySnapshot:
    engine: str
    version: str
    entries: List[RiskPanelRegistryEntry]
    count: int
    captured_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RiskPanelServiceResult:
    request_id: str
    reference: Optional[RiskPanelReference]
    assessment: Optional[RiskPanelAssessment]
    result: Optional[RiskPanelResult]
    success: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


def _risk_panel_registry_key(
    reference: RiskPanelReference,
) -> str:
    parts = [
        reference.market,
        reference.instrument,
        reference.symbol,
        reference.contract,
        reference.timeframe,
    ]

    normalized = []
    for value in parts:
        text = _rp_text(value).strip().upper()
        normalized.append(text if text else "-")

    return ":".join(normalized)


class RiskPanelRegistry:
    """
    Reference registry only.

    This registry does not:
    - generate risk
    - modify risk
    - override D13
    - override CAS
    - execute orders
    - modify positions
    """

    def __init__(self) -> None:
        self._entries: Dict[str, RiskPanelRegistryEntry] = {}

    def exists(self, reference: RiskPanelReference) -> bool:
        return _risk_panel_registry_key(reference) in self._entries

    def get(
        self,
        reference: RiskPanelReference,
    ) -> Optional[RiskPanelReference]:
        key = _risk_panel_registry_key(reference)
        entry = self._entries.get(key)
        return entry.reference if entry else None

    def get_entry(
        self,
        reference: RiskPanelReference,
    ) -> Optional[RiskPanelRegistryEntry]:
        return self._entries.get(_risk_panel_registry_key(reference))

    def add(
        self,
        reference: RiskPanelReference,
    ) -> RiskPanelRegistryEntry:
        key = _risk_panel_registry_key(reference)

        if key in self._entries:
            raise ValueError(
                f"Risk Panel reference already exists: {key}"
            )

        now = datetime.utcnow()

        entry = RiskPanelRegistryEntry(
            key=key,
            reference=reference,
            created_at=now,
            updated_at=now,
        )

        self._entries[key] = entry
        return entry

    def replace(
        self,
        reference: RiskPanelReference,
    ) -> RiskPanelRegistryEntry:
        key = _risk_panel_registry_key(reference)
        now = datetime.utcnow()

        existing = self._entries.get(key)

        entry = RiskPanelRegistryEntry(
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
        reference: RiskPanelReference,
    ) -> bool:
        key = _risk_panel_registry_key(reference)

        if key not in self._entries:
            return False

        del self._entries[key]
        return True

    def list_references(self) -> List[RiskPanelReference]:
        return [
            entry.reference
            for entry in self._entries.values()
            if entry.active
        ]

    def snapshot(self) -> RiskPanelRegistrySnapshot:
        return RiskPanelRegistrySnapshot(
            engine=RISK_PANEL_ENGINE,
            version=RISK_PANEL_VERSION,
            entries=list(self._entries.values()),
            count=len(self._entries),
        )

    def count(self) -> int:
        return len(self._entries)


def validate_risk_panel_registry(
    registry: RiskPanelRegistry,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(registry, RiskPanelRegistry):
        return ["registry must be RiskPanelRegistry"]

    for key, entry in registry._entries.items():
        if not key:
            errors.append("registry contains empty key")

        if not isinstance(entry, RiskPanelRegistryEntry):
            errors.append(
                f"invalid registry entry for key: {key}"
            )
            continue

        expected_key = _risk_panel_registry_key(
            entry.reference
        )

        if key != expected_key:
            errors.append(
                f"registry key mismatch: {key}"
            )

    return errors


def risk_panel_registry_health(
    registry: RiskPanelRegistry,
) -> Dict[str, Any]:
    errors = validate_risk_panel_registry(registry)

    return {
        "engine": RISK_PANEL_ENGINE,
        "version": RISK_PANEL_VERSION,
        "healthy": not errors,
        "count": registry.count()
        if isinstance(registry, RiskPanelRegistry)
        else 0,
        "errors": errors,
        "risk_generation": False,
        "risk_override": False,
        "d13_mutation": False,
        "cas_override": False,
        "execution": False,
    }


class RiskPanelService:
    """
    Application service for Terminal Risk Panel.

    Authority boundary:
        Upstream Risk/CAS/D13
                ↓
        Risk Panel Service
                ↓
        Presentation / readiness / display

    No upstream intelligence or risk mutation is permitted.
    """

    def __init__(
        self,
        registry: Optional[RiskPanelRegistry] = None,
    ) -> None:
        self.registry = registry or RiskPanelRegistry()

    def resolve(
        self,
        request: RiskPanelRequest,
        reference: RiskPanelReference,
        assessment: RiskPanelAssessment,
        items: Optional[List[RiskPanelItem]] = None,
    ) -> RiskPanelServiceResult:

        try:
            result = resolve_risk_panel(
                request=request,
                reference=reference,
                assessment=assessment,
                items=items,
            )

            return RiskPanelServiceResult(
                request_id=request.request_id,
                reference=reference,
                assessment=assessment,
                result=result,
                success=True,
                metadata={
                    "risk_generation": False,
                    "risk_override": False,
                    "d13_mutation": False,
                    "cas_override": False,
                    "execution": False,
                },
            )

        except Exception as exc:
            return RiskPanelServiceResult(
                request_id=request.request_id,
                reference=reference,
                assessment=assessment,
                result=None,
                success=False,
                errors=[str(exc)],
                metadata={
                    "risk_generation": False,
                    "risk_override": False,
                    "d13_mutation": False,
                    "cas_override": False,
                    "execution": False,
                },
            )

    def assess(
        self,
        request: RiskPanelRequest,
        reference: RiskPanelReference,
        items: Optional[List[RiskPanelItem]] = None,
    ) -> RiskPanelServiceResult:

        try:
            assessment = build_risk_panel_assessment(
                request=request,
                reference=reference,
                items=items,
            )

            return RiskPanelServiceResult(
                request_id=request.request_id,
                reference=reference,
                assessment=assessment,
                result=None,
                success=True,
                metadata={
                    "assessment_only": True,
                    "risk_generation": False,
                    "risk_override": False,
                    "d13_mutation": False,
                    "cas_override": False,
                },
            )

        except Exception as exc:
            return RiskPanelServiceResult(
                request_id=request.request_id,
                reference=reference,
                assessment=None,
                result=None,
                success=False,
                errors=[str(exc)],
            )

    def register(
        self,
        reference: RiskPanelReference,
        replace: bool = False,
    ) -> RiskPanelRegistryEntry:

        if replace:
            return self.registry.replace(reference)

        return self.registry.add(reference)

    def get(
        self,
        reference: RiskPanelReference,
    ) -> Optional[RiskPanelReference]:
        return self.registry.get(reference)

    def list_references(
        self,
    ) -> List[RiskPanelReference]:
        return self.registry.list_references()

    def snapshot(
        self,
    ) -> RiskPanelRegistrySnapshot:
        return self.registry.snapshot()

    def health(self) -> Dict[str, Any]:
        return risk_panel_registry_health(
            self.registry
        )

    def integrity(self) -> List[str]:
        return validate_risk_panel_registry(
            self.registry
        )

    def info(self) -> Dict[str, Any]:
        return {
            "engine": RISK_PANEL_ENGINE,
            "version": RISK_PANEL_VERSION,
            "role": "terminal_risk_presentation_service",
            "authority": {
                "presentation": True,
                "risk_display": True,
                "risk_aggregation": True,
                "risk_generation": False,
                "risk_override": False,
                "d13_authority": False,
                "d13_mutation": False,
                "cas_authority": False,
                "cas_override": False,
                "execution": False,
                "order_authority": False,
                "position_authority": False,
                "upstream_mutation": False,
            },
            "registry_count": self.registry.count(),
        }


# ============================================================
# SINGLETON SERVICE
# ============================================================

_RISK_PANEL_SERVICE = RiskPanelService()


def get_risk_panel_service() -> RiskPanelService:
    return _RISK_PANEL_SERVICE


def resolve_terminal_risk_panel(
    request: RiskPanelRequest,
    reference: RiskPanelReference,
    assessment: RiskPanelAssessment,
    items: Optional[List[RiskPanelItem]] = None,
) -> RiskPanelServiceResult:
    return _RISK_PANEL_SERVICE.resolve(
        request=request,
        reference=reference,
        assessment=assessment,
        items=items,
    )


def get_terminal_risk_panel_reference(
    reference: RiskPanelReference,
) -> Optional[RiskPanelReference]:
    return _RISK_PANEL_SERVICE.get(reference)


def terminal_risk_panel_snapshot() -> RiskPanelRegistrySnapshot:
    return _RISK_PANEL_SERVICE.snapshot()


def terminal_risk_panel_count() -> int:
    return _RISK_PANEL_SERVICE.registry.count()


def terminal_risk_panel_health() -> Dict[str, Any]:
    return _RISK_PANEL_SERVICE.health()


def terminal_risk_panel_integrity() -> List[str]:
    return _RISK_PANEL_SERVICE.integrity()


def terminal_risk_panel_operational_check() -> Dict[str, Any]:
    health = _RISK_PANEL_SERVICE.health()

    return {
        "engine": RISK_PANEL_ENGINE,
        "version": RISK_PANEL_VERSION,
        "operational": health["healthy"],
        "registry_count": health["count"],
        "errors": health["errors"],
        "authority_preserved": (
            health["risk_generation"] is False
            and health["risk_override"] is False
            and health["d13_mutation"] is False
            and health["cas_override"] is False
            and health["execution"] is False
        ),
    }


def terminal_risk_panel_service_info() -> Dict[str, Any]:
    return _RISK_PANEL_SERVICE.info()
# ============================================================
# RISK PANEL — PART 5
# SERIALIZATION + INTEGRITY + SUMMARY + EXPORTS
# ============================================================

def _rp_serialize_datetime(
    value: Optional[datetime],
) -> Optional[str]:
    if value is None:
        return None
    return value.isoformat()


def _rp_serialize_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, list):
        return [
            _rp_serialize_value(item)
            for item in value
        ]

    if isinstance(value, dict):
        return {
            str(key): _rp_serialize_value(val)
            for key, val in value.items()
        }

    return value


def serialize_risk_panel_item(
    item: RiskPanelItem,
) -> Dict[str, Any]:
    return {
        "item_id": item.item_id,
        "label": item.label,
        "category": item.category.value,
        "risk_level": item.risk_level.value,
        "severity": item.severity.value,
        "source_type": item.source_type.value,
        "value": _rp_serialize_value(item.value),
        "threshold": _rp_serialize_value(item.threshold),
        "utilization": item.utilization,
        "unit": item.unit,
        "status": item.status.value,
        "source": item.source,
        "message": item.message,
        "timestamp": _rp_serialize_datetime(
            item.timestamp
        ),
        "metadata": _rp_serialize_value(item.metadata),
    }


def serialize_risk_panel_reference(
    reference: RiskPanelReference,
) -> Dict[str, Any]:
    return {
        "market": reference.market,
        "instrument": reference.instrument,
        "symbol": reference.symbol,
        "contract": reference.contract,
        "timeframe": reference.timeframe,
        "risk_source": reference.risk_source,
        "cas_source": reference.cas_source,
        "decision_source": reference.decision_source,
        "d13_source": reference.d13_source,
        "as_of": _rp_serialize_datetime(
            reference.as_of
        ),
        "metadata": _rp_serialize_value(
            reference.metadata
        ),
    }


def serialize_risk_panel_assessment(
    assessment: RiskPanelAssessment,
) -> Dict[str, Any]:
    return {
        "data_state": assessment.data_state.value,
        "consistency": assessment.consistency.value,
        "readiness": assessment.readiness.value,
        "completeness_score": assessment.completeness_score,
        "freshness_score": assessment.freshness_score,
        "confidence_score": assessment.confidence_score,
        "quality_score": assessment.quality_score,
        "item_count": assessment.item_count,
        "requirements_met": assessment.requirements_met,
        "flags": list(assessment.flags),
        "metadata": _rp_serialize_value(
            assessment.metadata
        ),
    }


def serialize_risk_panel_presentation(
    presentation: RiskPanelPresentation,
) -> Dict[str, Any]:
    return {
        "title": presentation.title,
        "overall_risk_level": (
            presentation.overall_risk_level.value
        ),
        "items": [
            serialize_risk_panel_item(item)
            for item in presentation.items
        ],
        "risk_source": presentation.risk_source,
        "cas_source": presentation.cas_source,
        "decision_source": presentation.decision_source,
        "d13_present": presentation.d13_present,
        "status": presentation.status.value,
        "resolution": presentation.resolution.value,
        "restrictions": list(
            presentation.restrictions
        ),
        "flags": list(presentation.flags),
        "metadata": _rp_serialize_value(
            presentation.metadata
        ),
    }


def serialize_risk_panel_result(
    result: RiskPanelResult,
) -> Dict[str, Any]:
    return {
        "request": _rp_serialize_value(
            result.request.__dict__
        ),
        "reference": serialize_risk_panel_reference(
            result.reference
        ),
        "assessment": serialize_risk_panel_assessment(
            result.assessment
        ),
        "presentation": serialize_risk_panel_presentation(
            result.presentation
        ),
        "decision": result.decision.value,
        "resolution": result.resolution.value,
        "flags": list(result.flags),
        "restrictions": list(result.restrictions),
        "authority_valid": result.authority_valid,
        "metadata": _rp_serialize_value(
            result.metadata
        ),
    }


def serialize_risk_panel_service_result(
    service_result: RiskPanelServiceResult,
) -> Dict[str, Any]:
    return {
        "request_id": service_result.request_id,
        "reference": (
            serialize_risk_panel_reference(
                service_result.reference
            )
            if service_result.reference
            else None
        ),
        "assessment": (
            serialize_risk_panel_assessment(
                service_result.assessment
            )
            if service_result.assessment
            else None
        ),
        "result": (
            serialize_risk_panel_result(
                service_result.result
            )
            if service_result.result
            else None
        ),
        "success": service_result.success,
        "errors": list(service_result.errors),
        "warnings": list(service_result.warnings),
        "metadata": _rp_serialize_value(
            service_result.metadata
        ),
    }


def serialize_risk_panel_source_map(
    source_map: RiskPanelSourceMap,
) -> Dict[str, Any]:
    return {
        "risk_panel_engine": source_map.risk_panel_engine,
        "risk_source": source_map.risk_source,
        "risk_cortex_source": source_map.risk_cortex_source,
        "decision_source": source_map.decision_source,
        "d13_source": source_map.d13_source,
        "market_context_source": (
            source_map.market_context_source
        ),
        "evidence_source": source_map.evidence_source,
        "cas_source": source_map.cas_source,
        "memory_source": source_map.memory_source,
        "metadata": _rp_serialize_value(
            source_map.metadata
        ),
    }


def serialize_risk_panel_registry_snapshot(
    snapshot: RiskPanelRegistrySnapshot,
) -> Dict[str, Any]:
    return {
        "engine": snapshot.engine,
        "version": snapshot.version,
        "entries": [
            {
                "key": entry.key,
                "reference": serialize_risk_panel_reference(
                    entry.reference
                ),
                "created_at": _rp_serialize_datetime(
                    entry.created_at
                ),
                "updated_at": _rp_serialize_datetime(
                    entry.updated_at
                ),
                "active": entry.active,
                "metadata": _rp_serialize_value(
                    entry.metadata
                ),
            }
            for entry in snapshot.entries
        ],
        "count": snapshot.count,
        "captured_at": _rp_serialize_datetime(
            snapshot.captured_at
        ),
        "metadata": _rp_serialize_value(
            snapshot.metadata
        ),
    }


# ============================================================
# INTEGRITY VALIDATION
# ============================================================

def validate_risk_panel_item_integrity(
    item: RiskPanelItem,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(item, RiskPanelItem):
        return ["item must be RiskPanelItem"]

    if not item.item_id:
        errors.append("item_id is required")

    if not item.label:
        errors.append("label is required")

    if not isinstance(
        item.category,
        RiskPanelCategory,
    ):
        errors.append("invalid category")

    if not isinstance(
        item.risk_level,
        RiskPanelRiskLevel,
    ):
        errors.append("invalid risk_level")

    if not isinstance(
        item.severity,
        RiskPanelSeverity,
    ):
        errors.append("invalid severity")

    if not isinstance(
        item.source_type,
        RiskPanelSourceType,
    ):
        errors.append("invalid source_type")

    if not isinstance(
        item.status,
        RiskPanelStatus,
    ):
        errors.append("invalid status")

    return errors


def validate_risk_panel_reference_integrity(
    reference: RiskPanelReference,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(
        reference,
        RiskPanelReference,
    ):
        return ["reference must be RiskPanelReference"]

    if not reference.market:
        errors.append("market is required")

    if not reference.instrument:
        errors.append("instrument is required")

    if not reference.symbol:
        errors.append("symbol is required")

    if not reference.risk_source:
        errors.append("risk_source is required")

    if not reference.cas_source:
        errors.append("cas_source is required")

    if not reference.decision_source:
        errors.append("decision_source is required")

    if not reference.d13_source:
        errors.append("d13_source is required")

    return errors


def validate_risk_panel_assessment_integrity(
    assessment: RiskPanelAssessment,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(
        assessment,
        RiskPanelAssessment,
    ):
        return ["assessment must be RiskPanelAssessment"]

    for name in (
        "completeness_score",
        "freshness_score",
        "confidence_score",
        "quality_score",
    ):
        value = getattr(assessment, name)

        if not isinstance(value, (int, float)):
            errors.append(
                f"{name} must be numeric"
            )
        elif not 0.0 <= float(value) <= 1.0:
            errors.append(
                f"{name} must be between 0 and 1"
            )

    if assessment.item_count < 0:
        errors.append(
            "item_count cannot be negative"
        )

    if not isinstance(
        assessment.flags,
        list,
    ):
        errors.append("flags must be list")

    return errors


def validate_risk_panel_presentation_integrity(
    presentation: RiskPanelPresentation,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(
        presentation,
        RiskPanelPresentation,
    ):
        return [
            "presentation must be RiskPanelPresentation"
        ]

    if not presentation.title:
        errors.append("title is required")

    if not isinstance(
        presentation.items,
        list,
    ):
        errors.append("items must be list")
    else:
        for item in presentation.items:
            errors.extend(
                validate_risk_panel_item_integrity(item)
            )

    if not presentation.risk_source:
        errors.append("risk_source is required")

    if not presentation.decision_source:
        errors.append("decision_source is required")

    if not isinstance(
        presentation.d13_present,
        bool,
    ):
        errors.append("d13_present must be bool")

    if not isinstance(
        presentation.restrictions,
        list,
    ):
        errors.append("restrictions must be list")

    if not isinstance(
        presentation.flags,
        list,
    ):
        errors.append("flags must be list")

    return errors


def validate_risk_panel_result_integrity(
    result: RiskPanelResult,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(
        result,
        RiskPanelResult,
    ):
        return ["result must be RiskPanelResult"]

    if not isinstance(
        result.request,
        RiskPanelRequest,
    ):
        errors.append("invalid request")

    errors.extend(
        validate_risk_panel_reference_integrity(
            result.reference
        )
    )

    errors.extend(
        validate_risk_panel_assessment_integrity(
            result.assessment
        )
    )

    errors.extend(
        validate_risk_panel_presentation_integrity(
            result.presentation
        )
    )

    if not isinstance(
        result.decision,
        RiskPanelDecision,
    ):
        errors.append("invalid decision")

    if not isinstance(
        result.resolution,
        RiskPanelResolutionStatus,
    ):
        errors.append("invalid resolution")

    if not isinstance(
        result.authority_valid,
        bool,
    ):
        errors.append(
            "authority_valid must be bool"
        )

    authority_errors = (
        validate_risk_panel_result_authority(result)
    )

    errors.extend(authority_errors)

    return errors


def validate_risk_panel_registry_snapshot_integrity(
    snapshot: RiskPanelRegistrySnapshot,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(
        snapshot,
        RiskPanelRegistrySnapshot,
    ):
        return [
            "snapshot must be RiskPanelRegistrySnapshot"
        ]

    if snapshot.engine != RISK_PANEL_ENGINE:
        errors.append("engine mismatch")

    if snapshot.version != RISK_PANEL_VERSION:
        errors.append("version mismatch")

    if snapshot.count != len(snapshot.entries):
        errors.append("snapshot count mismatch")

    seen_keys = set()

    for entry in snapshot.entries:
        if not isinstance(
            entry,
            RiskPanelRegistryEntry,
        ):
            errors.append(
                "invalid registry entry"
            )
            continue

        if entry.key in seen_keys:
            errors.append(
                f"duplicate registry key: {entry.key}"
            )

        seen_keys.add(entry.key)

        expected = _risk_panel_registry_key(
            entry.reference
        )

        if entry.key != expected:
            errors.append(
                f"registry key mismatch: {entry.key}"
            )

    return errors


def validate_risk_panel_service_result_integrity(
    service_result: RiskPanelServiceResult,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(
        service_result,
        RiskPanelServiceResult,
    ):
        return [
            "service_result must be RiskPanelServiceResult"
        ]

    if service_result.reference:
        errors.extend(
            validate_risk_panel_reference_integrity(
                service_result.reference
            )
        )

    if service_result.assessment:
        errors.extend(
            validate_risk_panel_assessment_integrity(
                service_result.assessment
            )
        )

    if service_result.result:
        errors.extend(
            validate_risk_panel_result_integrity(
                service_result.result
            )
        )

    if service_result.success:
        if service_result.result is None:
            if service_result.assessment is None:
                errors.append(
                    "successful service result requires "
                    "result or assessment"
                )

    if not isinstance(
        service_result.errors,
        list,
    ):
        errors.append("errors must be list")

    if not isinstance(
        service_result.warnings,
        list,
    ):
        errors.append("warnings must be list")

    return errors


# ============================================================
# SUMMARY
# ============================================================

def build_risk_panel_summary(
    result: RiskPanelResult,
) -> Dict[str, Any]:
    if not isinstance(
        result,
        RiskPanelResult,
    ):
        return {
            "valid": False,
            "errors": [
                "result must be RiskPanelResult"
            ],
        }

    integrity_errors = (
        validate_risk_panel_result_integrity(result)
    )

    return {
        "engine": RISK_PANEL_ENGINE,
        "version": RISK_PANEL_VERSION,
        "valid": not integrity_errors,
        "market": result.reference.market,
        "instrument": result.reference.instrument,
        "symbol": result.reference.symbol,
        "contract": result.reference.contract,
        "timeframe": result.reference.timeframe,
        "risk_level": (
            result.presentation
            .overall_risk_level.value
        ),
        "decision": result.decision.value,
        "resolution": result.resolution.value,
        "readiness": (
            result.assessment.readiness.value
        ),
        "data_state": (
            result.assessment.data_state.value
        ),
        "consistency": (
            result.assessment.consistency.value
        ),
        "quality_score": (
            result.assessment.quality_score
        ),
        "item_count": (
            result.assessment.item_count
        ),
        "flags": list(result.flags),
        "restrictions": list(
            result.restrictions
        ),
        "authority_valid": result.authority_valid,
        "authority_boundary": {
            "risk_generation": False,
            "risk_override": False,
            "d13_mutation": False,
            "cas_override": False,
            "execution": False,
            "upstream_mutation": False,
        },
        "errors": integrity_errors,
    }


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [
    # Constants
    "RISK_PANEL_ENGINE",
    "RISK_PANEL_VERSION",

    # Enums
    "RiskPanelStatus",
    "RiskPanelMode",
    "RiskPanelPriority",
    "RiskPanelSeverity",
    "RiskPanelSourceType",
    "RiskPanelContractStatus",
    "RiskPanelCategory",
    "RiskPanelRiskLevel",
    "RiskPanelDataState",
    "RiskPanelConsistency",
    "RiskPanelReadiness",
    "RiskPanelDecision",
    "RiskPanelResolutionStatus",

    # Contracts
    "RiskPanelRequest",
    "RiskPanelItem",
    "RiskPanelReference",
    "RiskPanelContractValidation",
    "RiskPanelRequirements",
    "RiskPanelAssessment",
    "RiskPanelResolutionRules",
    "RiskPanelPresentation",
    "RiskPanelResult",
    "RiskPanelSourceMap",

    # Registry
    "RiskPanelRegistryEntry",
    "RiskPanelRegistrySnapshot",
    "RiskPanelServiceResult",
    "RiskPanelRegistry",
    "validate_risk_panel_registry",
    "risk_panel_registry_health",

    # Request / reference
    "normalize_risk_panel_request",
    "validate_risk_panel_request",
    "build_risk_panel_request",
    "build_risk_panel_reference",

    # Assessment
    "build_risk_panel_requirements",
    "evaluate_risk_panel_data_state",
    "evaluate_risk_panel_consistency",
    "evaluate_risk_panel_requirements",
    "evaluate_risk_panel_freshness",
    "evaluate_risk_panel_completeness",
    "evaluate_risk_panel_confidence",
    "evaluate_risk_panel_quality",
    "evaluate_risk_panel_readiness",
    "build_risk_panel_assessment",

    # Resolution / presentation
    "build_risk_panel_resolution_rules",
    "collect_risk_panel_resolution_flags",
    "collect_risk_panel_restrictions",
    "build_risk_panel_presentation",
    "resolve_risk_panel",
    "validate_risk_panel_result",
    "validate_risk_panel_result_authority",

    # Service
    "RiskPanelService",
    "get_risk_panel_service",
    "resolve_terminal_risk_panel",
    "get_terminal_risk_panel_reference",
    "terminal_risk_panel_snapshot",
    "terminal_risk_panel_count",
    "terminal_risk_panel_health",
    "terminal_risk_panel_integrity",
    "terminal_risk_panel_operational_check",
    "terminal_risk_panel_service_info",

    # Serialization
    "serialize_risk_panel_item",
    "serialize_risk_panel_reference",
    "serialize_risk_panel_assessment",
    "serialize_risk_panel_presentation",
    "serialize_risk_panel_result",
    "serialize_risk_panel_service_result",
    "serialize_risk_panel_source_map",
    "serialize_risk_panel_registry_snapshot",

    # Integrity
    "validate_risk_panel_item_integrity",
    "validate_risk_panel_reference_integrity",
    "validate_risk_panel_assessment_integrity",
    "validate_risk_panel_presentation_integrity",
    "validate_risk_panel_result_integrity",
    "validate_risk_panel_registry_snapshot_integrity",
    "validate_risk_panel_service_result_integrity",

    # Summary
    "build_risk_panel_summary",
]