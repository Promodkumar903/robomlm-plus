# ============================================================
# ROBOMLM_PLUS
# app/terminal/decision_outlook.py
# PART 1 / 5
# Decision Outlook Contract + Authority Boundary
# ============================================================

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


DECISION_OUTLOOK_ENGINE = "ROBOMLM_TERMINAL_DECISION_OUTLOOK"
DECISION_OUTLOOK_VERSION = "1.0"


class DecisionOutlookStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    READY = "READY"
    PARTIAL = "PARTIAL"
    STALE = "STALE"
    INVALID = "INVALID"
    ERROR = "ERROR"


class DecisionOutlookMode(str, Enum):
    PAPER = "PAPER"
    DEMO = "DEMO"
    LIVE = "LIVE"
    UNKNOWN = "UNKNOWN"


class DecisionOutlookPriority(str, Enum):
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DecisionOutlookSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DecisionOutlookSourceType(str, Enum):
    DECISION_CORTEX = "DECISION_CORTEX"
    D13 = "D13"
    MARKET_CONTEXT = "MARKET_CONTEXT"
    EVIDENCE_CORTEX = "EVIDENCE_CORTEX"
    RISK = "RISK"
    MEMORY = "MEMORY"
    EXTERNAL = "EXTERNAL"
    UNKNOWN = "UNKNOWN"


class DecisionOutlookContractStatus(str, Enum):
    CREATED = "CREATED"
    VALID = "VALID"
    INVALID = "INVALID"
    READY = "READY"


class DecisionOutlookDirection(str, Enum):
    UP = "UP"
    DOWN = "DOWN"
    SIDEWAYS = "SIDEWAYS"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"


class DecisionOutlookAction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    WAIT = "WAIT"
    NO_TRADE = "NO_TRADE"
    REVIEW = "REVIEW"
    UNKNOWN = "UNKNOWN"


class DecisionOutlookCategory(str, Enum):
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    CONFIRMATION = "CONFIRMATION"
    WARNING = "WARNING"
    RISK = "RISK"
    TIMING = "TIMING"
    SCENARIO = "SCENARIO"
    OTHER = "OTHER"


def _do_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def _do_enum(value: Any, enum_cls: Any, default: Any) -> Any:
    if isinstance(value, enum_cls):
        return value

    try:
        return enum_cls(
            str(value).strip().upper()
        )
    except (ValueError, TypeError):
        return default


def _do_number(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)

        if number != number:
            return default

        return number

    except (TypeError, ValueError):
        return default


def _do_timestamp(value: Any = None) -> datetime:
    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            pass

    return datetime.utcnow()


@dataclass
class DecisionOutlookRequest:
    market: str = ""
    instrument: str = ""
    symbol: str = ""
    contract: str = ""
    timeframe: str = ""
    session: str = ""
    market_phase: str = ""
    mode: DecisionOutlookMode = DecisionOutlookMode.UNKNOWN
    priority: DecisionOutlookPriority = (
        DecisionOutlookPriority.NORMAL
    )
    requested_scenarios: List[str] = field(
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


@dataclass
class DecisionOutlookItem:
    decision_id: str = ""
    category: DecisionOutlookCategory = (
        DecisionOutlookCategory.OTHER
    )
    name: str = ""
    direction: DecisionOutlookDirection = (
        DecisionOutlookDirection.UNKNOWN
    )
    action: DecisionOutlookAction = (
        DecisionOutlookAction.UNKNOWN
    )
    value: Any = None
    interpretation: str = ""
    rationale: str = ""
    source: str = ""
    source_type: DecisionOutlookSourceType = (
        DecisionOutlookSourceType.UNKNOWN
    )
    status: DecisionOutlookStatus = (
        DecisionOutlookStatus.UNKNOWN
    )
    severity: DecisionOutlookSeverity = (
        DecisionOutlookSeverity.INFO
    )
    confidence: float = 0.0
    timestamp: datetime = field(
        default_factory=datetime.utcnow
    )
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class DecisionOutlookReference:
    market: str = ""
    instrument: str = ""
    symbol: str = ""
    contract: str = ""
    timeframe: str = ""
    session: str = ""
    market_phase: str = ""
    status: DecisionOutlookStatus = (
        DecisionOutlookStatus.UNKNOWN
    )
    mode: DecisionOutlookMode = (
        DecisionOutlookMode.UNKNOWN
    )
    source: str = ""
    decision_count: int = 0
    primary_direction: DecisionOutlookDirection = (
        DecisionOutlookDirection.UNKNOWN
    )
    primary_action: DecisionOutlookAction = (
        DecisionOutlookAction.UNKNOWN
    )
    created_at: datetime = field(
        default_factory=datetime.utcnow
    )
    updated_at: datetime = field(
        default_factory=datetime.utcnow
    )
    version: str = DECISION_OUTLOOK_VERSION


@dataclass
class DecisionOutlookContractValidation:
    status: DecisionOutlookContractStatus = (
        DecisionOutlookContractStatus.CREATED
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


def decision_outlook_authority_boundary() -> Dict[str, bool]:
    return {
        "presentation_authority": True,
        "decision_display_authority": True,
        "decision_outlook_aggregation_authority": True,
        "market_data_authority": False,
        "evidence_generation_authority": False,
        "intelligence_generation_authority": False,
        "market_context_authority": False,
        "decision_generation_authority": False,
        "d13_authority": False,
        "risk_authority": False,
        "cas_authority": False,
        "execution_authority": False,
        "order_authority": False,
        "position_authority": False,
        "upstream_mutation_authority": False,
    }


def validate_decision_outlook_authority_boundary() -> bool:
    boundary = decision_outlook_authority_boundary()

    required_true = (
        "presentation_authority",
        "decision_display_authority",
        "decision_outlook_aggregation_authority",
    )

    required_false = (
        "market_data_authority",
        "evidence_generation_authority",
        "intelligence_generation_authority",
        "market_context_authority",
        "decision_generation_authority",
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


def normalize_decision_outlook_request(
    request: DecisionOutlookRequest,
) -> DecisionOutlookRequest:
    return DecisionOutlookRequest(
        market=_do_text(request.market),
        instrument=_do_text(request.instrument),
        symbol=_do_text(request.symbol),
        contract=_do_text(request.contract),
        timeframe=_do_text(request.timeframe),
        session=_do_text(request.session),
        market_phase=_do_text(request.market_phase),
        mode=_do_enum(
            request.mode,
            DecisionOutlookMode,
            DecisionOutlookMode.UNKNOWN,
        ),
        priority=_do_enum(
            request.priority,
            DecisionOutlookPriority,
            DecisionOutlookPriority.NORMAL,
        ),
        requested_scenarios=[
            _do_text(value)
            for value in (
                request.requested_scenarios or []
            )
            if _do_text(value)
        ],
        requested_fields=[
            _do_text(value)
            for value in (
                request.requested_fields or []
            )
            if _do_text(value)
        ],
        metadata=dict(request.metadata or {}),
        request_id=_do_text(request.request_id),
        timestamp=_do_timestamp(request.timestamp),
    )


def validate_decision_outlook_request(
    request: DecisionOutlookRequest,
) -> DecisionOutlookContractValidation:
    errors: List[str] = []
    warnings: List[str] = []

    if not _do_text(request.market):
        errors.append("market_missing")

    if not _do_text(request.instrument):
        errors.append("instrument_missing")

    if not _do_text(request.symbol):
        errors.append("symbol_missing")

    if request.mode == DecisionOutlookMode.UNKNOWN:
        warnings.append("mode_unknown")

    if not _do_text(request.request_id):
        warnings.append("request_id_missing")

    valid = len(errors) == 0

    return DecisionOutlookContractValidation(
        status=(
            DecisionOutlookContractStatus.VALID
            if valid
            else DecisionOutlookContractStatus.INVALID
        ),
        valid=valid,
        errors=errors,
        warnings=warnings,
        checked_at=datetime.utcnow(),
    )


def build_decision_outlook_request(
    market: str,
    instrument: str,
    symbol: str,
    contract: str = "",
    timeframe: str = "",
    session: str = "",
    market_phase: str = "",
    mode: Any = DecisionOutlookMode.UNKNOWN,
    priority: Any = DecisionOutlookPriority.NORMAL,
    requested_scenarios: Optional[List[str]] = None,
    requested_fields: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    request_id: str = "",
) -> DecisionOutlookRequest:
    request = DecisionOutlookRequest(
        market=market,
        instrument=instrument,
        symbol=symbol,
        contract=contract,
        timeframe=timeframe,
        session=session,
        market_phase=market_phase,
        mode=_do_enum(
            mode,
            DecisionOutlookMode,
            DecisionOutlookMode.UNKNOWN,
        ),
        priority=_do_enum(
            priority,
            DecisionOutlookPriority,
            DecisionOutlookPriority.NORMAL,
        ),
        requested_scenarios=list(
            requested_scenarios or []
        ),
        requested_fields=list(
            requested_fields or []
        ),
        metadata=dict(metadata or {}),
        request_id=request_id,
        timestamp=datetime.utcnow(),
    )

    return normalize_decision_outlook_request(
        request
    )


def build_decision_outlook_reference(
    request: DecisionOutlookRequest,
    decision_count: int = 0,
    primary_direction: Any = (
        DecisionOutlookDirection.UNKNOWN
    ),
    primary_action: Any = DecisionOutlookAction.UNKNOWN,
    status: Any = DecisionOutlookStatus.UNKNOWN,
    source: str = "",
) -> DecisionOutlookReference:
    return DecisionOutlookReference(
        market=_do_text(request.market),
        instrument=_do_text(request.instrument),
        symbol=_do_text(request.symbol),
        contract=_do_text(request.contract),
        timeframe=_do_text(request.timeframe),
        session=_do_text(request.session),
        market_phase=_do_text(request.market_phase),
        status=_do_enum(
            status,
            DecisionOutlookStatus,
            DecisionOutlookStatus.UNKNOWN,
        ),
        mode=_do_enum(
            request.mode,
            DecisionOutlookMode,
            DecisionOutlookMode.UNKNOWN,
        ),
        source=_do_text(source),
        decision_count=max(
            0,
            int(decision_count),
        ),
        primary_direction=_do_enum(
            primary_direction,
            DecisionOutlookDirection,
            DecisionOutlookDirection.UNKNOWN,
        ),
        primary_action=_do_enum(
            primary_action,
            DecisionOutlookAction,
            DecisionOutlookAction.UNKNOWN,
        ),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        version=DECISION_OUTLOOK_VERSION,
    )
# ============================================================
# ROBOMLM_PLUS
# app/terminal/decision_outlook.py
# PART 2 / 5
# Decision Outlook Assessment + Readiness
# ============================================================


class DecisionOutlookDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    INVALID = "INVALID"


class DecisionOutlookConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONDITIONAL = "CONDITIONAL"
    INCONSISTENT = "INCONSISTENT"
    UNKNOWN = "UNKNOWN"


class DecisionOutlookReadiness(str, Enum):
    READY = "READY"
    CONDITIONALLY_READY = "CONDITIONALLY_READY"
    NOT_READY = "NOT_READY"
    BLOCKED = "BLOCKED"


@dataclass
class DecisionOutlookRequirements:
    require_market: bool = True
    require_instrument: bool = True
    require_symbol: bool = True
    require_decision: bool = True
    require_source: bool = True
    require_freshness: bool = True
    require_confidence: bool = False
    minimum_items: int = 1
    minimum_confidence: float = 0.0
    maximum_age_seconds: float = 300.0
    allow_partial: bool = True


@dataclass
class DecisionOutlookAssessment:
    data_state: DecisionOutlookDataState = (
        DecisionOutlookDataState.MISSING
    )
    consistency: DecisionOutlookConsistency = (
        DecisionOutlookConsistency.UNKNOWN
    )
    readiness: DecisionOutlookReadiness = (
        DecisionOutlookReadiness.NOT_READY
    )
    completeness: float = 0.0
    quality: float = 0.0
    confidence: float = 0.0
    freshness: float = 0.0
    source_quality: float = 0.0
    item_count: int = 0
    valid_item_count: int = 0
    warnings: List[str] = field(
        default_factory=list
    )
    errors: List[str] = field(
        default_factory=list
    )
    assessed_at: datetime = field(
        default_factory=datetime.utcnow
    )


def build_decision_outlook_requirements(
    require_market: bool = True,
    require_instrument: bool = True,
    require_symbol: bool = True,
    require_decision: bool = True,
    require_source: bool = True,
    require_freshness: bool = True,
    require_confidence: bool = False,
    minimum_items: int = 1,
    minimum_confidence: float = 0.0,
    maximum_age_seconds: float = 300.0,
    allow_partial: bool = True,
) -> DecisionOutlookRequirements:
    return DecisionOutlookRequirements(
        require_market=bool(require_market),
        require_instrument=bool(require_instrument),
        require_symbol=bool(require_symbol),
        require_decision=bool(require_decision),
        require_source=bool(require_source),
        require_freshness=bool(require_freshness),
        require_confidence=bool(require_confidence),
        minimum_items=max(
            0,
            int(minimum_items),
        ),
        minimum_confidence=max(
            0.0,
            min(
                1.0,
                _do_number(
                    minimum_confidence
                ),
            ),
        ),
        maximum_age_seconds=max(
            0.0,
            _do_number(
                maximum_age_seconds,
                300.0,
            ),
        ),
        allow_partial=bool(allow_partial),
    )


def evaluate_decision_outlook_data_state(
    request: DecisionOutlookRequest,
    items: List[DecisionOutlookItem],
    requirements: DecisionOutlookRequirements,
) -> DecisionOutlookDataState:
    if not isinstance(
        request,
        DecisionOutlookRequest,
    ):
        return DecisionOutlookDataState.INVALID

    if not items:
        return DecisionOutlookDataState.MISSING

    if any(
        not isinstance(
            item,
            DecisionOutlookItem,
        )
        for item in items
    ):
        return DecisionOutlookDataState.INVALID

    missing_required = False

    if (
        requirements.require_market
        and not _do_text(request.market)
    ):
        missing_required = True

    if (
        requirements.require_instrument
        and not _do_text(request.instrument)
    ):
        missing_required = True

    if (
        requirements.require_symbol
        and not _do_text(request.symbol)
    ):
        missing_required = True

    if (
        requirements.require_decision
        and len(items) < requirements.minimum_items
    ):
        missing_required = True

    if missing_required:
        return (
            DecisionOutlookDataState.PARTIAL
            if requirements.allow_partial
            else DecisionOutlookDataState.MISSING
        )

    return DecisionOutlookDataState.COMPLETE


def evaluate_decision_outlook_consistency(
    request: DecisionOutlookRequest,
    items: List[DecisionOutlookItem],
) -> DecisionOutlookConsistency:
    if not isinstance(
        request,
        DecisionOutlookRequest,
    ):
        return DecisionOutlookConsistency.UNKNOWN

    if not items:
        return DecisionOutlookConsistency.UNKNOWN

    if any(
        not isinstance(
            item,
            DecisionOutlookItem,
        )
        for item in items
    ):
        return DecisionOutlookConsistency.INCONSISTENT

    request_symbol = _do_text(
        request.symbol
    ).upper()

    request_instrument = _do_text(
        request.instrument
    ).upper()

    conflicts = 0
    known = 0

    for item in items:
        metadata = item.metadata or {}

        item_symbol = _do_text(
            metadata.get("symbol")
        ).upper()

        item_instrument = _do_text(
            metadata.get("instrument")
        ).upper()

        if item_symbol:
            known += 1

            if (
                request_symbol
                and item_symbol != request_symbol
            ):
                conflicts += 1

        if item_instrument:
            known += 1

            if (
                request_instrument
                and item_instrument != request_instrument
            ):
                conflicts += 1

    if conflicts > 0:
        return DecisionOutlookConsistency.INCONSISTENT

    if known == 0:
        return DecisionOutlookConsistency.CONDITIONAL

    return DecisionOutlookConsistency.CONSISTENT


def evaluate_decision_outlook_requirements(
    request: DecisionOutlookRequest,
    items: List[DecisionOutlookItem],
    requirements: DecisionOutlookRequirements,
) -> Dict[str, bool]:
    checks: Dict[str, bool] = {}

    checks["market"] = (
        not requirements.require_market
        or bool(_do_text(request.market))
    )

    checks["instrument"] = (
        not requirements.require_instrument
        or bool(_do_text(request.instrument))
    )

    checks["symbol"] = (
        not requirements.require_symbol
        or bool(_do_text(request.symbol))
    )

    checks["minimum_items"] = (
        not requirements.require_decision
        or len(items) >= requirements.minimum_items
    )

    checks["source"] = (
        not requirements.require_source
        or any(
            _do_text(item.source)
            for item in items
            if isinstance(
                item,
                DecisionOutlookItem,
            )
        )
    )

    return checks


def evaluate_decision_outlook_freshness(
    items: List[DecisionOutlookItem],
    maximum_age_seconds: float = 300.0,
) -> float:
    if not items:
        return 0.0

    now = datetime.utcnow()

    max_age = max(
        0.0,
        _do_number(
            maximum_age_seconds,
            300.0,
        ),
    )

    scores: List[float] = []

    for item in items:
        timestamp = item.timestamp

        if not isinstance(
            timestamp,
            datetime,
        ):
            scores.append(0.0)
            continue

        age = max(
            0.0,
            (now - timestamp).total_seconds(),
        )

        if max_age <= 0.0:
            score = (
                1.0
                if age <= 0.0
                else 0.0
            )
        elif age <= max_age:
            score = max(
                0.0,
                1.0 - (age / max_age),
            )
        else:
            score = 0.0

        scores.append(score)

    return (
        sum(scores) / len(scores)
        if scores
        else 0.0
    )


def evaluate_decision_outlook_completeness(
    request: DecisionOutlookRequest,
    items: List[DecisionOutlookItem],
    requirements: DecisionOutlookRequirements,
) -> float:
    checks = evaluate_decision_outlook_requirements(
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


def evaluate_decision_outlook_confidence(
    items: List[DecisionOutlookItem],
) -> float:
    valid_items = [
        item
        for item in items
        if isinstance(
            item,
            DecisionOutlookItem,
        )
        and item.status not in (
            DecisionOutlookStatus.INVALID,
            DecisionOutlookStatus.ERROR,
        )
    ]

    if not valid_items:
        return 0.0

    values = [
        max(
            0.0,
            min(
                1.0,
                _do_number(
                    item.confidence
                ),
            ),
        )
        for item in valid_items
    ]

    return (
        sum(values) / len(values)
        if values
        else 0.0
    )


def evaluate_decision_outlook_quality(
    items: List[DecisionOutlookItem],
    freshness: float,
    completeness: float,
) -> float:
    if not items:
        return 0.0

    valid_items = [
        item
        for item in items
        if isinstance(
            item,
            DecisionOutlookItem,
        )
        and item.status not in (
            DecisionOutlookStatus.INVALID,
            DecisionOutlookStatus.ERROR,
        )
    ]

    if not valid_items:
        return 0.0

    source_score = (
        sum(
            1.0
            for item in valid_items
            if _do_text(item.source)
        )
        / len(valid_items)
    )

    confidence_score = (
        sum(
            max(
                0.0,
                min(
                    1.0,
                    _do_number(
                        item.confidence
                    ),
                ),
            )
            for item in valid_items
        )
        / len(valid_items)
    )

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


def evaluate_decision_outlook_readiness(
    data_state: DecisionOutlookDataState,
    consistency: DecisionOutlookConsistency,
    completeness: float,
    quality: float,
    confidence: float,
    requirements: DecisionOutlookRequirements,
) -> DecisionOutlookReadiness:
    if data_state == DecisionOutlookDataState.INVALID:
        return DecisionOutlookReadiness.BLOCKED

    if (
        consistency
        == DecisionOutlookConsistency.INCONSISTENT
    ):
        return DecisionOutlookReadiness.BLOCKED

    if data_state == DecisionOutlookDataState.MISSING:
        return DecisionOutlookReadiness.NOT_READY

    if completeness < 1.0:
        if not requirements.allow_partial:
            return DecisionOutlookReadiness.NOT_READY

        return DecisionOutlookReadiness.CONDITIONALLY_READY

    if requirements.require_confidence:
        if confidence < requirements.minimum_confidence:
            return DecisionOutlookReadiness.CONDITIONALLY_READY

    if quality <= 0.0:
        return DecisionOutlookReadiness.NOT_READY

    if (
        consistency
        == DecisionOutlookConsistency.CONDITIONAL
    ):
        return DecisionOutlookReadiness.CONDITIONALLY_READY

    return DecisionOutlookReadiness.READY


def build_decision_outlook_assessment(
    request: DecisionOutlookRequest,
    items: Optional[List[DecisionOutlookItem]] = None,
    requirements: Optional[DecisionOutlookRequirements] = None,
) -> DecisionOutlookAssessment:
    normalized_request = (
        normalize_decision_outlook_request(
            request
        )
    )

    outlook_items = list(items or [])

    outlook_requirements = (
        requirements
        if isinstance(
            requirements,
            DecisionOutlookRequirements,
        )
        else build_decision_outlook_requirements()
    )

    data_state = (
        evaluate_decision_outlook_data_state(
            normalized_request,
            outlook_items,
            outlook_requirements,
        )
    )

    consistency = (
        evaluate_decision_outlook_consistency(
            normalized_request,
            outlook_items,
        )
    )

    completeness = (
        evaluate_decision_outlook_completeness(
            normalized_request,
            outlook_items,
            outlook_requirements,
        )
    )

    freshness = (
        evaluate_decision_outlook_freshness(
            outlook_items,
            outlook_requirements.maximum_age_seconds,
        )
    )

    confidence = (
        evaluate_decision_outlook_confidence(
            outlook_items
        )
    )

    quality = (
        evaluate_decision_outlook_quality(
            outlook_items,
            freshness,
            completeness,
        )
    )

    readiness = (
        evaluate_decision_outlook_readiness(
            data_state=data_state,
            consistency=consistency,
            completeness=completeness,
            quality=quality,
            confidence=confidence,
            requirements=outlook_requirements,
        )
    )

    warnings: List[str] = []
    errors: List[str] = []

    if data_state == DecisionOutlookDataState.PARTIAL:
        warnings.append(
            "decision_outlook_data_partial"
        )

    if (
        consistency
        == DecisionOutlookConsistency.CONDITIONAL
    ):
        warnings.append(
            "decision_outlook_consistency_conditional"
        )

    if freshness < 1.0:
        warnings.append(
            "decision_outlook_freshness_degraded"
        )

    if (
        confidence
        < outlook_requirements.minimum_confidence
    ):
        warnings.append(
            "decision_outlook_confidence_below_requirement"
        )

    if data_state == DecisionOutlookDataState.INVALID:
        errors.append(
            "decision_outlook_data_invalid"
        )

    if (
        consistency
        == DecisionOutlookConsistency.INCONSISTENT
    ):
        errors.append(
            "decision_outlook_data_inconsistent"
        )

    valid_item_count = sum(
        1
        for item in outlook_items
        if isinstance(
            item,
            DecisionOutlookItem,
        )
        and item.status not in (
            DecisionOutlookStatus.INVALID,
            DecisionOutlookStatus.ERROR,
        )
    )

    source_quality = (
        sum(
            1.0
            for item in outlook_items
            if isinstance(
                item,
                DecisionOutlookItem,
            )
            and _do_text(item.source)
        )
        / len(outlook_items)
        if outlook_items
        else 0.0
    )

    return DecisionOutlookAssessment(
        data_state=data_state,
        consistency=consistency,
        readiness=readiness,
        completeness=max(
            0.0,
            min(
                1.0,
                completeness,
            ),
        ),
        quality=max(
            0.0,
            min(
                1.0,
                quality,
            ),
        ),
        confidence=max(
            0.0,
            min(
                1.0,
                confidence,
            ),
        ),
        freshness=max(
            0.0,
            min(
                1.0,
                freshness,
            ),
        ),
        source_quality=max(
            0.0,
            min(
                1.0,
                source_quality,
            ),
        ),
        item_count=len(outlook_items),
        valid_item_count=valid_item_count,
        warnings=warnings,
        errors=errors,
        assessed_at=datetime.utcnow(),
    )
# ============================================================
# DECISION OUTLOOK — PART 3
# Resolution / Presentation / Result / Source Mapping
# ============================================================

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class DecisionOutlookDecision(str, Enum):
    ALLOW = "ALLOW"
    ALLOW_WITH_RESTRICTION = "ALLOW_WITH_RESTRICTION"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCK = "BLOCK"


class DecisionOutlookResolutionStatus(str, Enum):
    RESOLVED = "RESOLVED"
    CONDITIONAL = "CONDITIONAL"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class DecisionOutlookResolutionRules:
    allow_when_ready: bool = True
    allow_when_conditionally_ready: bool = True
    review_when_not_ready: bool = True
    block_when_invalid: bool = True
    block_when_inconsistent: bool = True
    block_on_authority_violation: bool = True
    require_upstream_decision: bool = True
    require_d13_when_declared: bool = True


@dataclass
class DecisionOutlookPresentation:
    title: str = "Decision Outlook"
    primary_direction: DecisionOutlookDirection = (
        DecisionOutlookDirection.UNKNOWN
    )
    primary_action: DecisionOutlookAction = DecisionOutlookAction.UNKNOWN

    items: List[DecisionOutlookItem] = field(default_factory=list)

    decision_source: str = ""
    d13_present: bool = False

    status: DecisionOutlookStatus = DecisionOutlookStatus.UNKNOWN
    resolution: DecisionOutlookResolutionStatus = (
        DecisionOutlookResolutionStatus.REVIEW_REQUIRED
    )

    restrictions: List[str] = field(default_factory=list)
    flags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DecisionOutlookResult:
    request: DecisionOutlookRequest
    reference: DecisionOutlookReference
    assessment: DecisionOutlookAssessment
    presentation: DecisionOutlookPresentation

    decision: DecisionOutlookDecision = DecisionOutlookDecision.REVIEW_REQUIRED
    resolution: DecisionOutlookResolutionStatus = (
        DecisionOutlookResolutionStatus.REVIEW_REQUIRED
    )

    flags: List[str] = field(default_factory=list)
    restrictions: List[str] = field(default_factory=list)
    authority_valid: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DecisionOutlookSourceMap:
    decision_outlook_engine: str = DECISION_OUTLOOK_ENGINE
    decision_source: str = "app.intelligence.decision"
    d13_source: str = "app.intelligence.decision.d13"
    market_context_source: str = "app.intelligence.market_context"
    evidence_source: str = "app.intelligence.evidence"
    risk_source: str = "app.intelligence.risk"
    memory_source: str = "app.intelligence.memory"
    cas_source: str = "app.cas"
    metadata: Dict[str, Any] = field(default_factory=dict)


def build_decision_outlook_resolution_rules(
    request: DecisionOutlookRequest,
) -> DecisionOutlookResolutionRules:
    return DecisionOutlookResolutionRules(
        require_upstream_decision=True,
        require_d13_when_declared=bool(
            getattr(request, "include_d13", False)
        ),
    )


def collect_decision_outlook_resolution_flags(
    assessment: DecisionOutlookAssessment,
    reference: DecisionOutlookReference,
    rules: DecisionOutlookResolutionRules,
) -> List[str]:
    flags: List[str] = []

    if assessment.data_state == DecisionOutlookDataState.INVALID:
        flags.append("INVALID_DATA")

    if assessment.consistency == DecisionOutlookConsistency.INCONSISTENT:
        flags.append("INCONSISTENT_UPSTREAM_STATE")

    if assessment.readiness == DecisionOutlookReadiness.NOT_READY:
        flags.append("NOT_READY")

    if assessment.readiness == DecisionOutlookReadiness.BLOCKED:
        flags.append("BLOCKED")

    if assessment.freshness_score < 0.50:
        flags.append("STALE_OR_LOW_FRESHNESS")

    if assessment.confidence_score < 0.50:
        flags.append("LOW_CONFIDENCE")

    if rules.require_upstream_decision and not reference.decision_source:
        flags.append("MISSING_DECISION_SOURCE")

    if (
        rules.require_d13_when_declared
        and not reference.d13_source
    ):
        flags.append("MISSING_D13_SOURCE")

    return list(dict.fromkeys(flags))


def collect_decision_outlook_restrictions(
    assessment: DecisionOutlookAssessment,
    reference: DecisionOutlookReference,
) -> List[str]:
    restrictions: List[str] = []

    if assessment.readiness == DecisionOutlookReadiness.CONDITIONALLY_READY:
        restrictions.append("CONDITIONAL_READINESS")

    if assessment.freshness_score < 0.75:
        restrictions.append("FRESHNESS_RESTRICTION")

    if assessment.confidence_score < 0.75:
        restrictions.append("CONFIDENCE_RESTRICTION")

    if assessment.completeness_score < 0.75:
        restrictions.append("COMPLETENESS_RESTRICTION")

    if not reference.d13_source:
        restrictions.append("D13_NOT_AVAILABLE")

    return list(dict.fromkeys(restrictions))


def _extract_upstream_outlook(
    items: List[DecisionOutlookItem],
) -> Dict[str, Any]:
    """
    Extracts already-existing upstream decision information.

    IMPORTANT:
    This function does NOT calculate a decision.
    It only reads explicitly supplied outlook items.
    """

    primary_direction = DecisionOutlookDirection.UNKNOWN
    primary_action = DecisionOutlookAction.UNKNOWN
    decision_source = ""
    d13_present = False

    for item in items:
        source_type = getattr(item, "source_type", None)
        category = getattr(item, "category", None)

        if source_type == DecisionOutlookSourceType.D13:
            d13_present = True

        source_value = getattr(item, "source", "") or ""
        if source_value and not decision_source:
            decision_source = source_value

        item_direction = getattr(
            item,
            "direction",
            DecisionOutlookDirection.UNKNOWN,
        )

        item_action = getattr(
            item,
            "action",
            DecisionOutlookAction.UNKNOWN,
        )

        if (
            primary_direction == DecisionOutlookDirection.UNKNOWN
            and item_direction != DecisionOutlookDirection.UNKNOWN
        ):
            primary_direction = item_direction

        if (
            primary_action == DecisionOutlookAction.UNKNOWN
            and item_action != DecisionOutlookAction.UNKNOWN
        ):
            primary_action = item_action

        if category == DecisionOutlookCategory.PRIMARY:
            if item_direction != DecisionOutlookDirection.UNKNOWN:
                primary_direction = item_direction

            if item_action != DecisionOutlookAction.UNKNOWN:
                primary_action = item_action

    return {
        "primary_direction": primary_direction,
        "primary_action": primary_action,
        "decision_source": decision_source,
        "d13_present": d13_present,
    }


def build_decision_outlook_presentation(
    request: DecisionOutlookRequest,
    reference: DecisionOutlookReference,
    assessment: DecisionOutlookAssessment,
    items: Optional[List[DecisionOutlookItem]] = None,
    flags: Optional[List[str]] = None,
    restrictions: Optional[List[str]] = None,
) -> DecisionOutlookPresentation:

    resolved_items = list(items or [])
    resolved_flags = list(flags or [])
    resolved_restrictions = list(restrictions or [])

    upstream = _extract_upstream_outlook(resolved_items)

    if assessment.readiness == DecisionOutlookReadiness.READY:
        status = DecisionOutlookStatus.READY
        resolution = DecisionOutlookResolutionStatus.RESOLVED

    elif assessment.readiness == DecisionOutlookReadiness.CONDITIONALLY_READY:
        status = DecisionOutlookStatus.PARTIAL
        resolution = DecisionOutlookResolutionStatus.CONDITIONAL

    elif assessment.readiness == DecisionOutlookReadiness.BLOCKED:
        status = DecisionOutlookStatus.INVALID
        resolution = DecisionOutlookResolutionStatus.BLOCKED

    else:
        status = DecisionOutlookStatus.PARTIAL
        resolution = DecisionOutlookResolutionStatus.REVIEW_REQUIRED

    return DecisionOutlookPresentation(
        title="Decision Outlook",
        primary_direction=upstream["primary_direction"],
        primary_action=upstream["primary_action"],
        items=resolved_items,
        decision_source=upstream["decision_source"],
        d13_present=upstream["d13_present"],
        status=status,
        resolution=resolution,
        restrictions=resolved_restrictions,
        flags=resolved_flags,
        metadata={
            "engine": DECISION_OUTLOOK_ENGINE,
            "version": DECISION_OUTLOOK_VERSION,
            "aggregation_only": True,
            "decision_generation": False,
            "d13_override": False,
        },
    )


def resolve_decision_outlook(
    request: DecisionOutlookRequest,
    reference: DecisionOutlookReference,
    assessment: DecisionOutlookAssessment,
    items: Optional[List[DecisionOutlookItem]] = None,
    rules: Optional[DecisionOutlookResolutionRules] = None,
) -> DecisionOutlookResult:

    resolved_rules = rules or build_decision_outlook_resolution_rules(
        request
    )

    resolved_items = list(items or [])

    flags = collect_decision_outlook_resolution_flags(
        assessment,
        reference,
        resolved_rules,
    )

    restrictions = collect_decision_outlook_restrictions(
        assessment,
        reference,
    )

    authority_valid = True

    if not validate_decision_outlook_authority_boundary():
        authority_valid = False
        flags.append("AUTHORITY_BOUNDARY_INVALID")

    if (
        resolved_rules.block_on_authority_violation
        and not authority_valid
    ):
        decision = DecisionOutlookDecision.BLOCK
        resolution = DecisionOutlookResolutionStatus.BLOCKED

    elif (
        assessment.data_state == DecisionOutlookDataState.INVALID
        or assessment.consistency
        == DecisionOutlookConsistency.INCONSISTENT
    ):
        decision = DecisionOutlookDecision.BLOCK
        resolution = DecisionOutlookResolutionStatus.BLOCKED

    elif assessment.readiness == DecisionOutlookReadiness.BLOCKED:
        decision = DecisionOutlookDecision.BLOCK
        resolution = DecisionOutlookResolutionStatus.BLOCKED

    elif assessment.readiness == DecisionOutlookReadiness.NOT_READY:
        decision = DecisionOutlookDecision.REVIEW_REQUIRED
        resolution = DecisionOutlookResolutionStatus.REVIEW_REQUIRED

    elif assessment.readiness == (
        DecisionOutlookReadiness.CONDITIONALLY_READY
    ):
        decision = DecisionOutlookDecision.ALLOW_WITH_RESTRICTION
        resolution = DecisionOutlookResolutionStatus.CONDITIONAL

    else:
        decision = DecisionOutlookDecision.ALLOW
        resolution = DecisionOutlookResolutionStatus.RESOLVED

    presentation = build_decision_outlook_presentation(
        request=request,
        reference=reference,
        assessment=assessment,
        items=resolved_items,
        flags=flags,
        restrictions=restrictions,
    )

    return DecisionOutlookResult(
        request=request,
        reference=reference,
        assessment=assessment,
        presentation=presentation,
        decision=decision,
        resolution=resolution,
        flags=list(dict.fromkeys(flags)),
        restrictions=list(dict.fromkeys(restrictions)),
        authority_valid=authority_valid,
        metadata={
            "engine": DECISION_OUTLOOK_ENGINE,
            "version": DECISION_OUTLOOK_VERSION,
            "decision_generation": False,
            "upstream_authority_preserved": True,
            "d13_mutation": False,
        },
    )


def validate_decision_outlook_result(
    result: DecisionOutlookResult,
) -> List[str]:
    errors: List[str] = []

    if not result.request:
        errors.append("MISSING_REQUEST")

    if not result.reference:
        errors.append("MISSING_REFERENCE")

    if not result.assessment:
        errors.append("MISSING_ASSESSMENT")

    if not result.presentation:
        errors.append("MISSING_PRESENTATION")

    if result.decision == DecisionOutlookDecision.ALLOW:
        if result.resolution != DecisionOutlookResolutionStatus.RESOLVED:
            errors.append("ALLOW_REQUIRES_RESOLVED")

    if result.decision == DecisionOutlookDecision.ALLOW_WITH_RESTRICTION:
        if result.resolution != DecisionOutlookResolutionStatus.CONDITIONAL:
            errors.append("RESTRICTED_ALLOW_REQUIRES_CONDITIONAL")

    if result.decision == DecisionOutlookDecision.REVIEW_REQUIRED:
        if result.resolution != (
            DecisionOutlookResolutionStatus.REVIEW_REQUIRED
        ):
            errors.append("REVIEW_REQUIRES_REVIEW_STATUS")

    if result.decision == DecisionOutlookDecision.BLOCK:
        if result.resolution != DecisionOutlookResolutionStatus.BLOCKED:
            errors.append("BLOCK_REQUIRES_BLOCKED_STATUS")

    if not result.authority_valid:
        errors.append("AUTHORITY_INVALID")

    return list(dict.fromkeys(errors))


def validate_decision_outlook_result_authority(
    result: DecisionOutlookResult,
) -> bool:
    if not result.authority_valid:
        return False

    boundary = decision_outlook_authority_boundary()

    forbidden = (
        "market_data_authority",
        "evidence_generation_authority",
        "intelligence_generation_authority",
        "market_context_authority",
        "decision_generation_authority",
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
# DECISION OUTLOOK — PART 4
# Registry / Service / Operational Helpers
# ============================================================

@dataclass
class DecisionOutlookRegistryEntry:
    key: str
    reference: DecisionOutlookReference
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DecisionOutlookRegistrySnapshot:
    engine: str
    version: str
    count: int
    entries: List[DecisionOutlookRegistryEntry] = field(
        default_factory=list
    )
    generated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DecisionOutlookServiceResult:
    request: DecisionOutlookRequest
    result: Optional[DecisionOutlookResult] = None
    success: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


def _decision_outlook_registry_key(
    reference: DecisionOutlookReference,
) -> str:
    market = str(getattr(reference, "market", "") or "-").upper()
    instrument = str(
        getattr(reference, "instrument", "") or "-"
    ).upper()
    symbol = str(
        getattr(reference, "symbol", "") or "-"
    ).upper()
    contract = str(
        getattr(reference, "contract", "") or "-"
    ).upper()
    timeframe = str(
        getattr(reference, "timeframe", "") or "-"
    ).upper()

    return (
        f"{market}:{instrument}:{symbol}:"
        f"{contract}:{timeframe}"
    )


class DecisionOutlookRegistry:
    def __init__(self) -> None:
        self._entries: Dict[str, DecisionOutlookRegistryEntry] = {}

    def exists(
        self,
        reference: DecisionOutlookReference,
    ) -> bool:
        return _decision_outlook_registry_key(reference) in self._entries

    def get(
        self,
        reference: DecisionOutlookReference,
    ) -> Optional[DecisionOutlookReference]:
        entry = self._entries.get(
            _decision_outlook_registry_key(reference)
        )
        return entry.reference if entry else None

    def get_entry(
        self,
        reference: DecisionOutlookReference,
    ) -> Optional[DecisionOutlookRegistryEntry]:
        return self._entries.get(
            _decision_outlook_registry_key(reference)
        )

    def add(
        self,
        reference: DecisionOutlookReference,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DecisionOutlookRegistryEntry:

        key = _decision_outlook_registry_key(reference)

        if key in self._entries:
            raise ValueError(
                f"Decision outlook already registered: {key}"
            )

        entry = DecisionOutlookRegistryEntry(
            key=key,
            reference=reference,
            metadata=dict(metadata or {}),
        )

        self._entries[key] = entry
        return entry

    def replace(
        self,
        reference: DecisionOutlookReference,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DecisionOutlookRegistryEntry:

        key = _decision_outlook_registry_key(reference)

        entry = DecisionOutlookRegistryEntry(
            key=key,
            reference=reference,
            metadata=dict(metadata or {}),
        )

        self._entries[key] = entry
        return entry

    def remove(
        self,
        reference: DecisionOutlookReference,
    ) -> bool:

        key = _decision_outlook_registry_key(reference)

        if key not in self._entries:
            return False

        del self._entries[key]
        return True

    def list_references(self) -> List[DecisionOutlookReference]:
        return [
            entry.reference
            for entry in self._entries.values()
        ]

    def snapshot(self) -> DecisionOutlookRegistrySnapshot:
        return DecisionOutlookRegistrySnapshot(
            engine=DECISION_OUTLOOK_ENGINE,
            version=DECISION_OUTLOOK_VERSION,
            count=len(self._entries),
            entries=list(self._entries.values()),
            metadata={
                "registry": "decision_outlook",
            },
        )

    def count(self) -> int:
        return len(self._entries)


def validate_decision_outlook_registry(
    registry: DecisionOutlookRegistry,
) -> List[str]:

    errors: List[str] = []
    seen_keys = set()

    for key, entry in registry._entries.items():

        if key in seen_keys:
            errors.append(f"DUPLICATE_KEY:{key}")

        seen_keys.add(key)

        if not entry.reference:
            errors.append(f"MISSING_REFERENCE:{key}")

        expected_key = _decision_outlook_registry_key(
            entry.reference
        )

        if key != expected_key:
            errors.append(
                f"KEY_MISMATCH:{key}:{expected_key}"
            )

    return list(dict.fromkeys(errors))


def decision_outlook_registry_health(
    registry: DecisionOutlookRegistry,
) -> Dict[str, Any]:

    errors = validate_decision_outlook_registry(registry)

    return {
        "engine": DECISION_OUTLOOK_ENGINE,
        "version": DECISION_OUTLOOK_VERSION,
        "healthy": not errors,
        "count": registry.count(),
        "errors": errors,
    }


class DecisionOutlookService:

    def __init__(
        self,
        registry: Optional[DecisionOutlookRegistry] = None,
    ) -> None:
        self.registry = registry or DecisionOutlookRegistry()

    def resolve(
        self,
        request: DecisionOutlookRequest,
        reference: DecisionOutlookReference,
        assessment: DecisionOutlookAssessment,
        items: Optional[List[DecisionOutlookItem]] = None,
        rules: Optional[DecisionOutlookResolutionRules] = None,
    ) -> DecisionOutlookServiceResult:

        try:
            result = resolve_decision_outlook(
                request=request,
                reference=reference,
                assessment=assessment,
                items=items,
                rules=rules,
            )

            errors = validate_decision_outlook_result(result)

            return DecisionOutlookServiceResult(
                request=request,
                result=result,
                success=not errors,
                errors=errors,
                metadata={
                    "operation": "resolve",
                },
            )

        except Exception as exc:
            return DecisionOutlookServiceResult(
                request=request,
                success=False,
                errors=[str(exc)],
                metadata={
                    "operation": "resolve",
                    "exception": type(exc).__name__,
                },
            )

    def assess(
        self,
        reference: DecisionOutlookReference,
        items: Optional[List[DecisionOutlookItem]] = None,
    ) -> DecisionOutlookAssessment:

        return build_decision_outlook_assessment(
            reference=reference,
            items=list(items or []),
        )

    def register(
        self,
        reference: DecisionOutlookReference,
        replace: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DecisionOutlookRegistryEntry:

        if replace:
            return self.registry.replace(
                reference,
                metadata=metadata,
            )

        return self.registry.add(
            reference,
            metadata=metadata,
        )

    def get(
        self,
        reference: DecisionOutlookReference,
    ) -> Optional[DecisionOutlookReference]:

        return self.registry.get(reference)

    def list_references(
        self,
    ) -> List[DecisionOutlookReference]:

        return self.registry.list_references()

    def snapshot(
        self,
    ) -> DecisionOutlookRegistrySnapshot:

        return self.registry.snapshot()

    def health(self) -> Dict[str, Any]:
        return decision_outlook_registry_health(
            self.registry
        )

    def integrity(self) -> List[str]:
        return validate_decision_outlook_registry(
            self.registry
        )

    def info(self) -> Dict[str, Any]:
        return {
            "engine": DECISION_OUTLOOK_ENGINE,
            "version": DECISION_OUTLOOK_VERSION,
            "registry_count": self.registry.count(),
            "authority": {
                "decision_generation": False,
                "d13_authority": False,
                "d13_mutation": False,
                "execution": False,
                "risk_override": False,
                "cas_override": False,
            },
        }


_DECISION_OUTLOOK_SERVICE = DecisionOutlookService()


def get_decision_outlook_service() -> DecisionOutlookService:
    return _DECISION_OUTLOOK_SERVICE


def resolve_terminal_decision_outlook(
    request: DecisionOutlookRequest,
    reference: DecisionOutlookReference,
    assessment: DecisionOutlookAssessment,
    items: Optional[List[DecisionOutlookItem]] = None,
    rules: Optional[DecisionOutlookResolutionRules] = None,
) -> DecisionOutlookServiceResult:

    return _DECISION_OUTLOOK_SERVICE.resolve(
        request=request,
        reference=reference,
        assessment=assessment,
        items=items,
        rules=rules,
    )


def get_terminal_decision_outlook_reference(
    reference: DecisionOutlookReference,
) -> Optional[DecisionOutlookReference]:

    return _DECISION_OUTLOOK_SERVICE.get(reference)


def terminal_decision_outlook_snapshot() -> DecisionOutlookRegistrySnapshot:
    return _DECISION_OUTLOOK_SERVICE.snapshot()


def terminal_decision_outlook_count() -> int:
    return _DECISION_OUTLOOK_SERVICE.registry.count()


def terminal_decision_outlook_health() -> Dict[str, Any]:
    return _DECISION_OUTLOOK_SERVICE.health()


def terminal_decision_outlook_integrity() -> List[str]:
    return _DECISION_OUTLOOK_SERVICE.integrity()


def terminal_decision_outlook_operational_check() -> Dict[str, Any]:

    health = terminal_decision_outlook_health()
    authority = validate_decision_outlook_authority_boundary()

    return {
        "engine": DECISION_OUTLOOK_ENGINE,
        "version": DECISION_OUTLOOK_VERSION,
        "healthy": bool(health.get("healthy")),
        "authority_valid": authority,
        "operational": bool(
            health.get("healthy") and authority
        ),
        "registry_count": terminal_decision_outlook_count(),
    }


def terminal_decision_outlook_service_info() -> Dict[str, Any]:
    return _DECISION_OUTLOOK_SERVICE.info()
# ============================================================
# DECISION OUTLOOK — PART 5
# Serialization / Integrity / Summary / Public API
# ============================================================


def _do_serialize_datetime(value: Any) -> Any:
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.isoformat()

    return value


def _do_serialize_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, list):
        return [_do_serialize_value(v) for v in value]

    if isinstance(value, tuple):
        return [_do_serialize_value(v) for v in value]

    if isinstance(value, dict):
        return {
            str(k): _do_serialize_value(v)
            for k, v in value.items()
        }

    if hasattr(value, "__dataclass_fields__"):
        return {
            name: _do_serialize_value(
                getattr(value, name)
            )
            for name in value.__dataclass_fields__
        }

    return value


def serialize_decision_outlook_item(
    item: DecisionOutlookItem,
) -> Dict[str, Any]:
    return _do_serialize_value(item)


def serialize_decision_outlook_reference(
    reference: DecisionOutlookReference,
) -> Dict[str, Any]:
    return _do_serialize_value(reference)


def serialize_decision_outlook_assessment(
    assessment: DecisionOutlookAssessment,
) -> Dict[str, Any]:
    return _do_serialize_value(assessment)


def serialize_decision_outlook_presentation(
    presentation: DecisionOutlookPresentation,
) -> Dict[str, Any]:
    return _do_serialize_value(presentation)


def serialize_decision_outlook_result(
    result: DecisionOutlookResult,
) -> Dict[str, Any]:
    return _do_serialize_value(result)


def serialize_decision_outlook_service_result(
    result: DecisionOutlookServiceResult,
) -> Dict[str, Any]:
    return _do_serialize_value(result)


def serialize_decision_outlook_source_map(
    source_map: DecisionOutlookSourceMap,
) -> Dict[str, Any]:
    return _do_serialize_value(source_map)


def serialize_decision_outlook_registry_snapshot(
    snapshot: DecisionOutlookRegistrySnapshot,
) -> Dict[str, Any]:
    return _do_serialize_value(snapshot)


def validate_decision_outlook_item_integrity(
    item: DecisionOutlookItem,
) -> List[str]:

    errors: List[str] = []

    if item is None:
        return ["ITEM_IS_NONE"]

    if not str(getattr(item, "item_id", "") or "").strip():
        errors.append("MISSING_ITEM_ID")

    if not str(getattr(item, "label", "") or "").strip():
        errors.append("MISSING_ITEM_LABEL")

    direction = getattr(
        item,
        "direction",
        DecisionOutlookDirection.UNKNOWN,
    )

    action = getattr(
        item,
        "action",
        DecisionOutlookAction.UNKNOWN,
    )

    if not isinstance(direction, DecisionOutlookDirection):
        errors.append("INVALID_DIRECTION")

    if not isinstance(action, DecisionOutlookAction):
        errors.append("INVALID_ACTION")

    source_type = getattr(
        item,
        "source_type",
        DecisionOutlookSourceType.UNKNOWN,
    )

    if not isinstance(source_type, DecisionOutlookSourceType):
        errors.append("INVALID_SOURCE_TYPE")

    return list(dict.fromkeys(errors))


def validate_decision_outlook_reference_integrity(
    reference: DecisionOutlookReference,
) -> List[str]:

    errors: List[str] = []

    if reference is None:
        return ["REFERENCE_IS_NONE"]

    required_fields = (
        "market",
        "instrument",
        "symbol",
    )

    for field_name in required_fields:
        value = getattr(reference, field_name, None)

        if value is None or not str(value).strip():
            errors.append(
                f"MISSING_REFERENCE_{field_name.upper()}"
            )

    return list(dict.fromkeys(errors))


def validate_decision_outlook_assessment_integrity(
    assessment: DecisionOutlookAssessment,
) -> List[str]:

    errors: List[str] = []

    if assessment is None:
        return ["ASSESSMENT_IS_NONE"]

    for field_name in (
        "completeness_score",
        "freshness_score",
        "confidence_score",
        "quality_score",
    ):
        value = getattr(assessment, field_name, None)

        if value is None:
            errors.append(
                f"MISSING_{field_name.upper()}"
            )
            continue

        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            errors.append(
                f"INVALID_{field_name.upper()}"
            )
            continue

        if not 0.0 <= numeric_value <= 1.0:
            errors.append(
                f"OUT_OF_RANGE_{field_name.upper()}"
            )

    data_state = getattr(
        assessment,
        "data_state",
        DecisionOutlookDataState.INVALID,
    )

    consistency = getattr(
        assessment,
        "consistency",
        DecisionOutlookConsistency.UNKNOWN,
    )

    readiness = getattr(
        assessment,
        "readiness",
        DecisionOutlookReadiness.BLOCKED,
    )

    if not isinstance(
        data_state,
        DecisionOutlookDataState,
    ):
        errors.append("INVALID_DATA_STATE")

    if not isinstance(
        consistency,
        DecisionOutlookConsistency,
    ):
        errors.append("INVALID_CONSISTENCY")

    if not isinstance(
        readiness,
        DecisionOutlookReadiness,
    ):
        errors.append("INVALID_READINESS")

    return list(dict.fromkeys(errors))


def validate_decision_outlook_presentation_integrity(
    presentation: DecisionOutlookPresentation,
) -> List[str]:

    errors: List[str] = []

    if presentation is None:
        return ["PRESENTATION_IS_NONE"]

    if not str(
        getattr(presentation, "title", "") or ""
    ).strip():
        errors.append("MISSING_TITLE")

    direction = getattr(
        presentation,
        "primary_direction",
        DecisionOutlookDirection.UNKNOWN,
    )

    action = getattr(
        presentation,
        "primary_action",
        DecisionOutlookAction.UNKNOWN,
    )

    if not isinstance(
        direction,
        DecisionOutlookDirection,
    ):
        errors.append("INVALID_PRIMARY_DIRECTION")

    if not isinstance(
        action,
        DecisionOutlookAction,
    ):
        errors.append("INVALID_PRIMARY_ACTION")

    items = getattr(presentation, "items", None)

    if items is None:
        errors.append("MISSING_ITEMS")
    else:
        for index, item in enumerate(items):
            item_errors = (
                validate_decision_outlook_item_integrity(
                    item
                )
            )

            errors.extend(
                f"ITEM_{index}:{error}"
                for error in item_errors
            )

    if not isinstance(
        getattr(
            presentation,
            "status",
            DecisionOutlookStatus.UNKNOWN,
        ),
        DecisionOutlookStatus,
    ):
        errors.append("INVALID_PRESENTATION_STATUS")

    if not isinstance(
        getattr(
            presentation,
            "resolution",
            DecisionOutlookResolutionStatus.REVIEW_REQUIRED,
        ),
        DecisionOutlookResolutionStatus,
    ):
        errors.append("INVALID_PRESENTATION_RESOLUTION")

    return list(dict.fromkeys(errors))


def validate_decision_outlook_result_integrity(
    result: DecisionOutlookResult,
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

    if result.reference is not None:
        errors.extend(
            f"REFERENCE:{error}"
            for error in
            validate_decision_outlook_reference_integrity(
                result.reference
            )
        )

    if result.assessment is not None:
        errors.extend(
            f"ASSESSMENT:{error}"
            for error in
            validate_decision_outlook_assessment_integrity(
                result.assessment
            )
        )

    if result.presentation is not None:
        errors.extend(
            f"PRESENTATION:{error}"
            for error in
            validate_decision_outlook_presentation_integrity(
                result.presentation
            )
        )

    if not isinstance(
        result.decision,
        DecisionOutlookDecision,
    ):
        errors.append("INVALID_DECISION")

    if not isinstance(
        result.resolution,
        DecisionOutlookResolutionStatus,
    ):
        errors.append("INVALID_RESOLUTION")

    if not isinstance(result.authority_valid, bool):
        errors.append("INVALID_AUTHORITY_FLAG")

    errors.extend(
        validate_decision_outlook_result(result)
    )

    if not validate_decision_outlook_result_authority(
        result
    ):
        errors.append("AUTHORITY_BOUNDARY_FAILED")

    return list(dict.fromkeys(errors))


def validate_decision_outlook_registry_snapshot_integrity(
    snapshot: DecisionOutlookRegistrySnapshot,
) -> List[str]:

    errors: List[str] = []

    if snapshot is None:
        return ["SNAPSHOT_IS_NONE"]

    if snapshot.engine != DECISION_OUTLOOK_ENGINE:
        errors.append("ENGINE_MISMATCH")

    if snapshot.version != DECISION_OUTLOOK_VERSION:
        errors.append("VERSION_MISMATCH")

    entries = getattr(snapshot, "entries", None)

    if entries is None:
        errors.append("MISSING_ENTRIES")
        return list(dict.fromkeys(errors))

    if snapshot.count != len(entries):
        errors.append("COUNT_MISMATCH")

    seen_keys = set()

    for index, entry in enumerate(entries):

        if entry is None:
            errors.append(
                f"ENTRY_{index}_IS_NONE"
            )
            continue

        if not str(
            getattr(entry, "key", "") or ""
        ).strip():
            errors.append(
                f"ENTRY_{index}_MISSING_KEY"
            )

        if entry.key in seen_keys:
            errors.append(
                f"ENTRY_{index}_DUPLICATE_KEY"
            )

        seen_keys.add(entry.key)

        if entry.reference is None:
            errors.append(
                f"ENTRY_{index}_MISSING_REFERENCE"
            )
            continue

        expected_key = _decision_outlook_registry_key(
            entry.reference
        )

        if entry.key != expected_key:
            errors.append(
                f"ENTRY_{index}_KEY_MISMATCH"
            )

    return list(dict.fromkeys(errors))


def validate_decision_outlook_service_result_integrity(
    service_result: DecisionOutlookServiceResult,
) -> List[str]:

    errors: List[str] = []

    if service_result is None:
        return ["SERVICE_RESULT_IS_NONE"]

    if service_result.request is None:
        errors.append("MISSING_REQUEST")

    if not isinstance(
        service_result.success,
        bool,
    ):
        errors.append("INVALID_SUCCESS_FLAG")

    if service_result.result is not None:
        result_errors = (
            validate_decision_outlook_result_integrity(
                service_result.result
            )
        )

        errors.extend(
            f"RESULT:{error}"
            for error in result_errors
        )

    if service_result.success and service_result.errors:
        errors.append(
            "SUCCESS_RESULT_CONTAINS_ERRORS"
        )

    if not service_result.success and not service_result.errors:
        errors.append(
            "FAILED_RESULT_MISSING_ERRORS"
        )

    return list(dict.fromkeys(errors))


def build_decision_outlook_summary(
    result: Optional[DecisionOutlookResult] = None,
) -> Dict[str, Any]:

    if result is None:
        return {
            "engine": DECISION_OUTLOOK_ENGINE,
            "version": DECISION_OUTLOOK_VERSION,
            "status": "NO_RESULT",
            "decision": DecisionOutlookDecision.REVIEW_REQUIRED.value,
            "resolution": (
                DecisionOutlookResolutionStatus.REVIEW_REQUIRED.value
            ),
            "authority_valid": False,
        }

    presentation = result.presentation

    return {
        "engine": DECISION_OUTLOOK_ENGINE,
        "version": DECISION_OUTLOOK_VERSION,
        "status": (
            presentation.status.value
            if isinstance(
                presentation.status,
                DecisionOutlookStatus,
            )
            else str(presentation.status)
        ),
        "decision": (
            result.decision.value
            if isinstance(
                result.decision,
                DecisionOutlookDecision,
            )
            else str(result.decision)
        ),
        "resolution": (
            result.resolution.value
            if isinstance(
                result.resolution,
                DecisionOutlookResolutionStatus,
            )
            else str(result.resolution)
        ),
        "primary_direction": (
            presentation.primary_direction.value
            if isinstance(
                presentation.primary_direction,
                DecisionOutlookDirection,
            )
            else str(presentation.primary_direction)
        ),
        "primary_action": (
            presentation.primary_action.value
            if isinstance(
                presentation.primary_action,
                DecisionOutlookAction,
            )
            else str(presentation.primary_action)
        ),
        "item_count": len(
            presentation.items or []
        ),
        "d13_present": bool(
            presentation.d13_present
        ),
        "restrictions": list(
            result.restrictions or []
        ),
        "flags": list(
            result.flags or []
        ),
        "authority_valid": bool(
            result.authority_valid
        ),
        "metadata": {
            "aggregation_only": True,
            "decision_generation": False,
            "d13_mutation": False,
            "upstream_authority_preserved": True,
        },
    }


__all__ = [
    # Constants
    "DECISION_OUTLOOK_ENGINE",
    "DECISION_OUTLOOK_VERSION",

    # Enums
    "DecisionOutlookStatus",
    "DecisionOutlookMode",
    "DecisionOutlookPriority",
    "DecisionOutlookSeverity",
    "DecisionOutlookSourceType",
    "DecisionOutlookContractStatus",
    "DecisionOutlookDirection",
    "DecisionOutlookAction",
    "DecisionOutlookCategory",
    "DecisionOutlookDataState",
    "DecisionOutlookConsistency",
    "DecisionOutlookReadiness",
    "DecisionOutlookDecision",
    "DecisionOutlookResolutionStatus",

    # Contracts
    "DecisionOutlookRequest",
    "DecisionOutlookItem",
    "DecisionOutlookReference",
    "DecisionOutlookContractValidation",
    "DecisionOutlookRequirements",
    "DecisionOutlookAssessment",
    "DecisionOutlookResolutionRules",
    "DecisionOutlookPresentation",
    "DecisionOutlookResult",
    "DecisionOutlookSourceMap",
    "DecisionOutlookRegistryEntry",
    "DecisionOutlookRegistrySnapshot",
    "DecisionOutlookServiceResult",

    # Authority
    "decision_outlook_authority_boundary",
    "validate_decision_outlook_authority_boundary",

    # Request / Reference
    "normalize_decision_outlook_request",
    "validate_decision_outlook_request",
    "build_decision_outlook_request",
    "build_decision_outlook_reference",

    # Assessment
    "build_decision_outlook_requirements",
    "evaluate_decision_outlook_data_state",
    "evaluate_decision_outlook_consistency",
    "evaluate_decision_outlook_requirements",
    "evaluate_decision_outlook_freshness",
    "evaluate_decision_outlook_completeness",
    "evaluate_decision_outlook_confidence",
    "evaluate_decision_outlook_quality",
    "evaluate_decision_outlook_readiness",
    "build_decision_outlook_assessment",

    # Resolution
    "build_decision_outlook_resolution_rules",
    "collect_decision_outlook_resolution_flags",
    "collect_decision_outlook_restrictions",
    "build_decision_outlook_presentation",
    "resolve_decision_outlook",
    "validate_decision_outlook_result",
    "validate_decision_outlook_result_authority",

    # Registry
    "DecisionOutlookRegistry",
    "validate_decision_outlook_registry",
    "decision_outlook_registry_health",

    # Service
    "DecisionOutlookService",
    "get_decision_outlook_service",
    "resolve_terminal_decision_outlook",
    "get_terminal_decision_outlook_reference",
    "terminal_decision_outlook_snapshot",
    "terminal_decision_outlook_count",
    "terminal_decision_outlook_health",
    "terminal_decision_outlook_integrity",
    "terminal_decision_outlook_operational_check",
    "terminal_decision_outlook_service_info",

    # Serialization
    "serialize_decision_outlook_item",
    "serialize_decision_outlook_reference",
    "serialize_decision_outlook_assessment",
    "serialize_decision_outlook_presentation",
    "serialize_decision_outlook_result",
    "serialize_decision_outlook_service_result",
    "serialize_decision_outlook_source_map",
    "serialize_decision_outlook_registry_snapshot",

    # Integrity
    "validate_decision_outlook_item_integrity",
    "validate_decision_outlook_reference_integrity",
    "validate_decision_outlook_assessment_integrity",
    "validate_decision_outlook_presentation_integrity",
    "validate_decision_outlook_result_integrity",
    "validate_decision_outlook_registry_snapshot_integrity",
    "validate_decision_outlook_service_result_integrity",

    # Summary
    "build_decision_outlook_summary",
]