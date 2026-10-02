# ============================================================
# ROBOMLM — CAS ORCHESTRATOR
# Part 1: Core Constants / Enums / Request Contracts
# ============================================================

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Mapping, Optional, Tuple


# ============================================================
# ENGINE IDENTITY
# ============================================================

CAS_ORCHESTRATOR_ENGINE = "ROBOMLM_CAS_ORCHESTRATOR"
CAS_ORCHESTRATOR_VERSION = "1.0"


# ============================================================
# CAS STATUS
# ============================================================

class CASStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    READY = "READY"
    CONDITIONAL = "CONDITIONAL"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    RESTRICTED = "RESTRICTED"
    AUTHORIZED = "AUTHORIZED"
    BLOCKED = "BLOCKED"
    ERROR = "ERROR"


class CASDecision(str, Enum):
    ALLOW = "ALLOW"
    ALLOW_WITH_RESTRICTION = "ALLOW_WITH_RESTRICTION"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCK = "BLOCK"


class CASMode(str, Enum):
    PAPER = "PAPER"
    DEMO = "DEMO"
    LIVE = "LIVE"
    UNKNOWN = "UNKNOWN"


class CASPriority(str, Enum):
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CASContractStatus(str, Enum):
    CREATED = "CREATED"
    VALID = "VALID"
    INVALID = "INVALID"
    ASSESSED = "ASSESSED"
    READY = "READY"
    RESTRICTED = "RESTRICTED"
    REVIEW = "REVIEW"
    AUTHORIZED = "AUTHORIZED"
    BLOCKED = "BLOCKED"


# ============================================================
# CAS PATHWAY
# ============================================================

class CASPathway(str, Enum):
    NEW_ENTRY = "NEW_ENTRY"
    ENTRY = "ENTRY"

    ADD = "ADD"
    ADD_TO_POSITION = "ADD_TO_POSITION"
    SCALE_IN = "SCALE_IN"

    HOLD = "HOLD"
    RETAIN = "RETAIN"
    MAINTAIN = "MAINTAIN"
    WAIT = "WAIT"
    WATCH = "WATCH"

    REDUCE = "REDUCE"
    PARTIAL_EXIT = "PARTIAL_EXIT"
    EXIT = "EXIT"
    CLOSE = "CLOSE"
    CLOSE_POSITION = "CLOSE_POSITION"
    PROFIT_BOOK = "PROFIT_BOOK"

    NEXT_SESSION_PLAN = "NEXT_SESSION_PLAN"
    PLAN = "PLAN"
    PREPARE = "PREPARE"
    PREPARE_ENTRY = "PREPARE_ENTRY"

    NO_ACTION = "NO_ACTION"
    UNKNOWN = "UNKNOWN"


# ============================================================
# CAS GATE NAMES
# ============================================================

class CASGateName(str, Enum):
    SUITABILITY = "SUITABILITY"
    RISK = "RISK"
    EXPOSURE = "EXPOSURE"
    POSITION = "POSITION"
    EXECUTION_SAFETY = "EXECUTION_SAFETY"
    COMPLIANCE = "COMPLIANCE"
    RESTRICTION = "RESTRICTION"


CAS_GATE_ORDER = (
    CASGateName.SUITABILITY,
    CASGateName.RISK,
    CASGateName.EXPOSURE,
    CASGateName.POSITION,
    CASGateName.EXECUTION_SAFETY,
    CASGateName.COMPLIANCE,
    CASGateName.RESTRICTION,
)


# ============================================================
# CAS REQUEST
# ============================================================

@dataclass(frozen=True)
class CASRequest:
    """
    Unified authorization request entering CAS.

    CAS receives a proposed pathway and its relevant context.
    CAS does NOT generate the underlying market decision.
    """

    market: Optional[str] = None
    instrument: Optional[str] = None
    contract: Optional[str] = None

    user_id: Optional[str] = None
    account_id: Optional[str] = None
    plan_id: Optional[str] = None

    action: Optional[str] = None
    direction: Optional[str] = None

    mode: CASMode = CASMode.UNKNOWN
    strategy: Optional[str] = None
    timeframe: Optional[str] = None
    priority: CASPriority = CASPriority.NORMAL

    # --------------------------------------------------------
    # Decision context supplied by upstream authority.
    # CAS consumes; it does not replace D13.
    # --------------------------------------------------------

    decision_id: Optional[str] = None
    decision_direction: Optional[str] = None
    decision_state: Optional[str] = None
    decision_confidence: Optional[float] = None

    # --------------------------------------------------------
    # Risk context supplied by Risk Authority.
    # --------------------------------------------------------

    risk_id: Optional[str] = None
    risk_status: Optional[str] = None
    risk_decision: Optional[str] = None
    risk_score: Optional[float] = None
    risk_confidence: Optional[float] = None

    # --------------------------------------------------------
    # Position / exposure context.
    # --------------------------------------------------------

    current_position: Optional[float] = None
    proposed_position: Optional[float] = None

    current_exposure: Optional[float] = None
    proposed_exposure: Optional[float] = None

    # --------------------------------------------------------
    # Execution context.
    # --------------------------------------------------------

    broker: Optional[str] = None
    venue: Optional[str] = None
    execution_channel: Optional[str] = None

    order_type: Optional[str] = None
    quantity: Optional[float] = None
    price: Optional[float] = None

    reduce_only: bool = False
    close_only: bool = False

    # --------------------------------------------------------
    # Session / transition context.
    # --------------------------------------------------------

    session: Optional[str] = None
    market_phase: Optional[str] = None
    closing_window: bool = False
    expiry_window: bool = False

    # --------------------------------------------------------
    # Control metadata.
    # --------------------------------------------------------

    metadata: Mapping[str, Any] = field(default_factory=dict)
    request_id: Optional[str] = None
    timestamp: Optional[datetime] = None


# ============================================================
# GATE INPUT CONTEXT
# ============================================================

@dataclass(frozen=True)
class CASGateContext:
    """
    Normalized context passed to the individual CAS gates.

    This is orchestration context only. Each gate retains
    its own authority boundary.
    """

    request: CASRequest

    market: Optional[str]
    instrument: Optional[str]
    contract: Optional[str]

    user_id: Optional[str]
    account_id: Optional[str]
    plan_id: Optional[str]

    action: str
    direction: str
    pathway: CASPathway

    mode: CASMode
    strategy: Optional[str]
    timeframe: Optional[str]
    priority: CASPriority

    decision_id: Optional[str]
    decision_direction: Optional[str]
    decision_state: Optional[str]
    decision_confidence: Optional[float]

    risk_id: Optional[str]
    risk_status: Optional[str]
    risk_decision: Optional[str]
    risk_score: Optional[float]
    risk_confidence: Optional[float]

    current_position: Optional[float]
    proposed_position: Optional[float]

    current_exposure: Optional[float]
    proposed_exposure: Optional[float]

    broker: Optional[str]
    venue: Optional[str]
    execution_channel: Optional[str]

    order_type: Optional[str]
    quantity: Optional[float]
    price: Optional[float]

    reduce_only: bool
    close_only: bool

    session: Optional[str]
    market_phase: Optional[str]
    closing_window: bool
    expiry_window: bool

    metadata: Mapping[str, Any] = field(default_factory=dict)


# ============================================================
# CAS GATE RESULT REFERENCE
# ============================================================

@dataclass(frozen=True)
class CASGateResult:
    """
    Lightweight orchestration reference.

    Individual gate contracts remain authoritative for their
    own domain. CAS only aggregates their externally exposed
    decision state.
    """

    gate: CASGateName

    status: str
    decision: str

    allowed: bool
    restricted: bool
    review_required: bool
    blocked: bool

    score: Optional[float] = None
    confidence: Optional[float] = None

    flags: Tuple[str, ...] = field(default_factory=tuple)
    restrictions: Tuple[str, ...] = field(default_factory=tuple)

    reason: str = ""


# ============================================================
# CAS CONTRACT VALIDATION
# ============================================================

@dataclass(frozen=True)
class CASContractValidation:
    valid: bool

    errors: Tuple[str, ...] = field(default_factory=tuple)
    warnings: Tuple[str, ...] = field(default_factory=tuple)

    checked_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# ============================================================
# BASIC HELPERS
# ============================================================

def _cas_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _cas_action(value: Any) -> str:
    return _cas_text(value).upper()


def _cas_float(value: Any) -> Optional[float]:
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _cas_timestamp(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value

    return datetime.now(timezone.utc)


# ============================================================
# PATHWAY NORMALIZATION
# ============================================================

def normalize_cas_pathway(
    action: Any,
) -> CASPathway:

    value = _cas_action(action)

    if not value:
        return CASPathway.UNKNOWN

    try:
        return CASPathway(value)
    except ValueError:
        return CASPathway.UNKNOWN


# ============================================================
# REQUEST BUILDER
# ============================================================

def build_cas_request(
    data: Optional[Mapping[str, Any]] = None,
    **kwargs: Any,
) -> CASRequest:

    payload: Dict[str, Any] = {}

    if data:
        payload.update(dict(data))

    payload.update(kwargs)

    mode = payload.get("mode", CASMode.UNKNOWN)

    if not isinstance(mode, CASMode):
        try:
            mode = CASMode(_cas_action(mode))
        except ValueError:
            mode = CASMode.UNKNOWN

    priority = payload.get(
        "priority",
        CASPriority.NORMAL,
    )

    if not isinstance(priority, CASPriority):
        try:
            priority = CASPriority(_cas_action(priority))
        except ValueError:
            priority = CASPriority.NORMAL

    timestamp = payload.get("timestamp")

    if timestamp is not None and not isinstance(timestamp, datetime):
        timestamp = None

    return CASRequest(
        market=payload.get("market"),
        instrument=payload.get("instrument"),
        contract=payload.get("contract"),

        user_id=payload.get("user_id"),
        account_id=payload.get("account_id"),
        plan_id=payload.get("plan_id"),

        action=payload.get("action"),
        direction=payload.get("direction"),

        mode=mode,
        strategy=payload.get("strategy"),
        timeframe=payload.get("timeframe"),
        priority=priority,

        decision_id=payload.get("decision_id"),
        decision_direction=payload.get("decision_direction"),
        decision_state=payload.get("decision_state"),
        decision_confidence=_cas_float(
            payload.get("decision_confidence")
        ),

        risk_id=payload.get("risk_id"),
        risk_status=payload.get("risk_status"),
        risk_decision=payload.get("risk_decision"),
        risk_score=_cas_float(payload.get("risk_score")),
        risk_confidence=_cas_float(
            payload.get("risk_confidence")
        ),

        current_position=_cas_float(
            payload.get("current_position")
        ),
        proposed_position=_cas_float(
            payload.get("proposed_position")
        ),

        current_exposure=_cas_float(
            payload.get("current_exposure")
        ),
        proposed_exposure=_cas_float(
            payload.get("proposed_exposure")
        ),

        broker=payload.get("broker"),
        venue=payload.get("venue"),
        execution_channel=payload.get(
            "execution_channel"
        ),

        order_type=payload.get("order_type"),
        quantity=_cas_float(payload.get("quantity")),
        price=_cas_float(payload.get("price")),

        reduce_only=bool(
            payload.get("reduce_only", False)
        ),
        close_only=bool(
            payload.get("close_only", False)
        ),

        session=payload.get("session"),
        market_phase=payload.get("market_phase"),
        closing_window=bool(
            payload.get("closing_window", False)
        ),
        expiry_window=bool(
            payload.get("expiry_window", False)
        ),

        metadata=dict(
            payload.get("metadata") or {}
        ),

        request_id=payload.get("request_id"),

        timestamp=timestamp,
    )


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_cas_request(
    request: CASRequest,
) -> CASContractValidation:

    errors = []
    warnings = []

    if request is None:
        return CASContractValidation(
            valid=False,
            errors=("CAS_REQUEST_REQUIRED",),
        )

    if not _cas_text(request.market):
        errors.append("MARKET_REQUIRED")

    if not _cas_text(request.instrument):
        errors.append("INSTRUMENT_REQUIRED")

    if not _cas_text(request.action):
        errors.append("ACTION_REQUIRED")

    if not _cas_text(request.direction):
        warnings.append("DIRECTION_NOT_SUPPLIED")

    if not _cas_text(request.user_id):
        warnings.append("USER_ID_NOT_SUPPLIED")

    if not _cas_text(request.account_id):
        warnings.append("ACCOUNT_ID_NOT_SUPPLIED")

    if not _cas_text(request.plan_id):
        warnings.append("PLAN_ID_NOT_SUPPLIED")

    if request.quantity is not None and request.quantity < 0:
        errors.append("NEGATIVE_QUANTITY")

    if request.price is not None and request.price < 0:
        errors.append("NEGATIVE_PRICE")

    if request.current_exposure is not None:
        if request.current_exposure < 0:
            errors.append("NEGATIVE_CURRENT_EXPOSURE")

    if request.proposed_exposure is not None:
        if request.proposed_exposure < 0:
            errors.append("NEGATIVE_PROPOSED_EXPOSURE")

    if (
        request.decision_confidence is not None
        and not 0.0 <= request.decision_confidence <= 100.0
    ):
        errors.append("INVALID_DECISION_CONFIDENCE")

    if (
        request.risk_confidence is not None
        and not 0.0 <= request.risk_confidence <= 100.0
    ):
        errors.append("INVALID_RISK_CONFIDENCE")

    return CASContractValidation(
        valid=len(errors) == 0,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


# ============================================================
# GATE CONTEXT BUILDER
# ============================================================

def build_cas_gate_context(
    request: CASRequest,
) -> CASGateContext:

    if request is None:
        raise ValueError("CASRequest is required.")

    action = _cas_action(request.action)
    direction = _cas_action(request.direction)

    return CASGateContext(
        request=request,

        market=request.market,
        instrument=request.instrument,
        contract=request.contract,

        user_id=request.user_id,
        account_id=request.account_id,
        plan_id=request.plan_id,

        action=action,
        direction=direction,
        pathway=normalize_cas_pathway(action),

        mode=request.mode,
        strategy=request.strategy,
        timeframe=request.timeframe,
        priority=request.priority,

        decision_id=request.decision_id,
        decision_direction=request.decision_direction,
        decision_state=request.decision_state,
        decision_confidence=request.decision_confidence,

        risk_id=request.risk_id,
        risk_status=request.risk_status,
        risk_decision=request.risk_decision,
        risk_score=request.risk_score,
        risk_confidence=request.risk_confidence,

        current_position=request.current_position,
        proposed_position=request.proposed_position,

        current_exposure=request.current_exposure,
        proposed_exposure=request.proposed_exposure,

        broker=request.broker,
        venue=request.venue,
        execution_channel=request.execution_channel,

        order_type=request.order_type,
        quantity=request.quantity,
        price=request.price,

        reduce_only=request.reduce_only,
        close_only=request.close_only,

        session=request.session,
        market_phase=request.market_phase,
        closing_window=request.closing_window,
        expiry_window=request.expiry_window,

        metadata=dict(request.metadata or {}),
    )
# ============================================================
# ROBOMLM — CAS ORCHESTRATOR
# Part 2: Gate Requirements / Gate Requests / Gate Preparation
# ============================================================


# ============================================================
# GATE REQUIREMENTS
# ============================================================

@dataclass(frozen=True)
class CASGateRequirements:
    """
    Controls which CAS gates are required for a request.

    Defaults intentionally require every CAS safety/control
    domain. Individual gates remain independent authorities.
    """

    require_suitability: bool = True
    require_risk: bool = True
    require_exposure: bool = True
    require_position: bool = True
    require_execution_safety: bool = True
    require_compliance: bool = True
    require_restriction: bool = True

    stop_on_block: bool = True
    stop_on_review: bool = True

    allow_restricted_result: bool = True
    allow_unknown_gate: bool = False

    require_d13_context: bool = False
    require_risk_context: bool = False


# ============================================================
# GATE REQUIREMENT HELPERS
# ============================================================

def build_cas_gate_requirements(
    data: Optional[Mapping[str, Any]] = None,
    **kwargs: Any,
) -> CASGateRequirements:

    payload: Dict[str, Any] = {}

    if data:
        payload.update(dict(data))

    payload.update(kwargs)

    return CASGateRequirements(
        require_suitability=bool(
            payload.get("require_suitability", True)
        ),
        require_risk=bool(
            payload.get("require_risk", True)
        ),
        require_exposure=bool(
            payload.get("require_exposure", True)
        ),
        require_position=bool(
            payload.get("require_position", True)
        ),
        require_execution_safety=bool(
            payload.get("require_execution_safety", True)
        ),
        require_compliance=bool(
            payload.get("require_compliance", True)
        ),
        require_restriction=bool(
            payload.get("require_restriction", True)
        ),
        stop_on_block=bool(
            payload.get("stop_on_block", True)
        ),
        stop_on_review=bool(
            payload.get("stop_on_review", True)
        ),
        allow_restricted_result=bool(
            payload.get("allow_restricted_result", True)
        ),
        allow_unknown_gate=bool(
            payload.get("allow_unknown_gate", False)
        ),
        require_d13_context=bool(
            payload.get("require_d13_context", False)
        ),
        require_risk_context=bool(
            payload.get("require_risk_context", False)
        ),
    )


# ============================================================
# REQUIRED GATES
# ============================================================

def get_required_cas_gates(
    requirements: CASGateRequirements,
) -> Tuple[CASGateName, ...]:

    if requirements is None:
        requirements = CASGateRequirements()

    gates = []

    if requirements.require_suitability:
        gates.append(CASGateName.SUITABILITY)

    if requirements.require_risk:
        gates.append(CASGateName.RISK)

    if requirements.require_exposure:
        gates.append(CASGateName.EXPOSURE)

    if requirements.require_position:
        gates.append(CASGateName.POSITION)

    if requirements.require_execution_safety:
        gates.append(CASGateName.EXECUTION_SAFETY)

    if requirements.require_compliance:
        gates.append(CASGateName.COMPLIANCE)

    if requirements.require_restriction:
        gates.append(CASGateName.RESTRICTION)

    return tuple(gates)


# ============================================================
# GATE PRESENCE
# ============================================================

def cas_gate_is_required(
    gate: CASGateName,
    requirements: CASGateRequirements,
) -> bool:

    return gate in get_required_cas_gates(requirements)


# ============================================================
# DECISION / RISK CONTEXT VALIDATION
# ============================================================

def validate_cas_authority_context(
    context: CASGateContext,
    requirements: CASGateRequirements,
) -> CASContractValidation:

    errors = []
    warnings = []

    if context is None:
        return CASContractValidation(
            valid=False,
            errors=("CAS_GATE_CONTEXT_REQUIRED",),
        )

    if requirements.require_d13_context:

        if not context.decision_id:
            errors.append("D13_CONTEXT_REQUIRED")

        if not context.decision_direction:
            errors.append("D13_DIRECTION_REQUIRED")

        if context.decision_confidence is None:
            warnings.append("D13_CONFIDENCE_NOT_SUPPLIED")

    else:
        if not context.decision_id:
            warnings.append("D13_CONTEXT_NOT_SUPPLIED")

    if requirements.require_risk_context:

        if not context.risk_id:
            errors.append("RISK_CONTEXT_REQUIRED")

        if not context.risk_decision:
            errors.append("RISK_DECISION_REQUIRED")

    else:
        if not context.risk_id:
            warnings.append("RISK_CONTEXT_NOT_SUPPLIED")

    return CASContractValidation(
        valid=len(errors) == 0,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


# ============================================================
# SUITABILITY REQUEST PREPARATION
# ============================================================

def build_suitability_gate_request(
    context: CASGateContext,
) -> Dict[str, Any]:

    return {
        "market": context.market,
        "instrument": context.instrument,
        "contract": context.contract,

        "user_id": context.user_id,
        "account_id": context.account_id,
        "plan_id": context.plan_id,

        "action": context.action,
        "direction": context.direction,

        "mode": context.mode,
        "strategy": context.strategy,
        "timeframe": context.timeframe,
        "priority": context.priority,

        "metadata": dict(context.metadata),
        "request_id": context.request.request_id,
        "timestamp": context.request.timestamp,
    }


# ============================================================
# RISK REQUEST PREPARATION
# ============================================================

def build_risk_gate_request(
    context: CASGateContext,
) -> Dict[str, Any]:

    return {
        "market": context.market,
        "instrument": context.instrument,
        "contract": context.contract,

        "user_id": context.user_id,
        "account_id": context.account_id,
        "plan_id": context.plan_id,

        "action": context.action,
        "direction": context.direction,

        "mode": context.mode,
        "strategy": context.strategy,
        "timeframe": context.timeframe,
        "priority": context.priority,

        "quantity": context.quantity,
        "price": context.price,

        "current_exposure": context.current_exposure,
        "proposed_exposure": context.proposed_exposure,

        "metadata": dict(context.metadata),
        "request_id": context.request.request_id,
        "timestamp": context.request.timestamp,
    }


# ============================================================
# EXPOSURE REQUEST PREPARATION
# ============================================================

def build_exposure_gate_request(
    context: CASGateContext,
) -> Dict[str, Any]:

    return {
        "market": context.market,
        "instrument": context.instrument,
        "contract": context.contract,

        "user_id": context.user_id,
        "account_id": context.account_id,
        "plan_id": context.plan_id,

        "action": context.action,
        "direction": context.direction,

        "mode": context.mode,
        "strategy": context.strategy,
        "timeframe": context.timeframe,
        "priority": context.priority,

        "current_exposure": context.current_exposure,
        "proposed_exposure": context.proposed_exposure,

        "quantity": context.quantity,
        "price": context.price,

        "metadata": dict(context.metadata),
        "request_id": context.request.request_id,
        "timestamp": context.request.timestamp,
    }


# ============================================================
# POSITION REQUEST PREPARATION
# ============================================================

def build_position_gate_request(
    context: CASGateContext,
) -> Dict[str, Any]:

    return {
        "market": context.market,
        "instrument": context.instrument,
        "contract": context.contract,

        "user_id": context.user_id,
        "account_id": context.account_id,
        "plan_id": context.plan_id,

        "action": context.action,
        "direction": context.direction,

        "mode": context.mode,
        "strategy": context.strategy,
        "timeframe": context.timeframe,
        "priority": context.priority,

        "current_position": context.current_position,
        "proposed_position": context.proposed_position,

        "quantity": context.quantity,
        "price": context.price,

        "reduce_only": context.reduce_only,
        "close_only": context.close_only,

        "metadata": dict(context.metadata),
        "request_id": context.request.request_id,
        "timestamp": context.request.timestamp,
    }


# ============================================================
# EXECUTION SAFETY REQUEST PREPARATION
# ============================================================

def build_execution_safety_gate_request(
    context: CASGateContext,
) -> Dict[str, Any]:

    return {
        "market": context.market,
        "instrument": context.instrument,
        "contract": context.contract,

        "user_id": context.user_id,
        "account_id": context.account_id,
        "plan_id": context.plan_id,

        "action": context.action,
        "direction": context.direction,

        "mode": context.mode,
        "strategy": context.strategy,
        "timeframe": context.timeframe,
        "priority": context.priority,

        "broker": context.broker,
        "venue": context.venue,
        "execution_channel": context.execution_channel,

        "order_type": context.order_type,
        "quantity": context.quantity,
        "price": context.price,

        "reduce_only": context.reduce_only,
        "close_only": context.close_only,

        "metadata": dict(context.metadata),
        "request_id": context.request.request_id,
        "timestamp": context.request.timestamp,
    }


# ============================================================
# COMPLIANCE REQUEST PREPARATION
# ============================================================

def build_compliance_gate_request(
    context: CASGateContext,
) -> Dict[str, Any]:

    return {
        "market": context.market,
        "instrument": context.instrument,
        "contract": context.contract,

        "user_id": context.user_id,
        "account_id": context.account_id,
        "plan_id": context.plan_id,

        "action": context.action,
        "direction": context.direction,

        "mode": context.mode,
        "strategy": context.strategy,
        "timeframe": context.timeframe,
        "priority": context.priority,

        "broker": context.broker,
        "venue": context.venue,

        "metadata": dict(context.metadata),
        "request_id": context.request.request_id,
        "timestamp": context.request.timestamp,
    }


# ============================================================
# RESTRICTION REQUEST PREPARATION
# ============================================================

def build_restriction_gate_request(
    context: CASGateContext,
) -> Dict[str, Any]:

    return {
        "market": context.market,
        "instrument": context.instrument,
        "contract": context.contract,

        "user_id": context.user_id,
        "account_id": context.account_id,
        "plan_id": context.plan_id,

        "action": context.action,
        "direction": context.direction,

        "mode": context.mode,
        "strategy": context.strategy,
        "timeframe": context.timeframe,
        "priority": context.priority,

        "closing_window_restricted": bool(
            context.closing_window
        ),
        "expiry_restricted": bool(
            context.expiry_window
        ),

        "reduce_only": context.reduce_only,
        "close_only": context.close_only,

        "metadata": dict(context.metadata),
        "request_id": context.request.request_id,
        "timestamp": context.request.timestamp,
    }


# ============================================================
# GATE REQUEST MAP
# ============================================================

def build_cas_gate_requests(
    context: CASGateContext,
) -> Dict[CASGateName, Dict[str, Any]]:

    if context is None:
        raise ValueError("CASGateContext is required.")

    return {
        CASGateName.SUITABILITY:
            build_suitability_gate_request(context),

        CASGateName.RISK:
            build_risk_gate_request(context),

        CASGateName.EXPOSURE:
            build_exposure_gate_request(context),

        CASGateName.POSITION:
            build_position_gate_request(context),

        CASGateName.EXECUTION_SAFETY:
            build_execution_safety_gate_request(context),

        CASGateName.COMPLIANCE:
            build_compliance_gate_request(context),

        CASGateName.RESTRICTION:
            build_restriction_gate_request(context),
    }


# ============================================================
# GATE ORDER VALIDATION
# ============================================================

def validate_cas_gate_order() -> bool:

    return CAS_GATE_ORDER == (
        CASGateName.SUITABILITY,
        CASGateName.RISK,
        CASGateName.EXPOSURE,
        CASGateName.POSITION,
        CASGateName.EXECUTION_SAFETY,
        CASGateName.COMPLIANCE,
        CASGateName.RESTRICTION,
    )


# ============================================================
# PATHWAY CLASSIFICATION
# ============================================================

def classify_cas_pathway(
    context: CASGateContext,
) -> str:

    if context is None:
        return "UNKNOWN"

    pathway = context.pathway

    if pathway in {
        CASPathway.NEW_ENTRY,
        CASPathway.ENTRY,
        CASPathway.ADD,
        CASPathway.ADD_TO_POSITION,
        CASPathway.SCALE_IN,
    }:
        return "EXPANSION"

    if pathway in {
        CASPathway.REDUCE,
        CASPathway.PARTIAL_EXIT,
        CASPathway.EXIT,
        CASPathway.CLOSE,
        CASPathway.CLOSE_POSITION,
        CASPathway.PROFIT_BOOK,
    }:
        return "REDUCTION"

    if pathway in {
        CASPathway.HOLD,
        CASPathway.RETAIN,
        CASPathway.MAINTAIN,
        CASPathway.WAIT,
        CASPathway.WATCH,
    }:
        return "HOLD"

    if pathway in {
        CASPathway.NEXT_SESSION_PLAN,
        CASPathway.PLAN,
        CASPathway.PREPARE,
        CASPathway.PREPARE_ENTRY,
    }:
        return "PLANNING"

    if pathway == CASPathway.NO_ACTION:
        return "NO_ACTION"

    return "UNKNOWN"


# ============================================================
# CAS CONTEXT SUMMARY
# ============================================================

def summarize_cas_gate_context(
    context: CASGateContext,
) -> Dict[str, Any]:

    if context is None:
        return {
            "valid": False,
            "reason": "CAS gate context missing.",
        }

    return {
        "valid": True,

        "market": context.market,
        "instrument": context.instrument,
        "contract": context.contract,

        "action": context.action,
        "direction": context.direction,

        "pathway": context.pathway.value,
        "pathway_class": classify_cas_pathway(context),

        "mode": context.mode.value,
        "strategy": context.strategy,
        "timeframe": context.timeframe,

        "decision": {
            "decision_id": context.decision_id,
            "direction": context.decision_direction,
            "state": context.decision_state,
            "confidence": context.decision_confidence,
        },

        "risk": {
            "risk_id": context.risk_id,
            "status": context.risk_status,
            "decision": context.risk_decision,
            "score": context.risk_score,
            "confidence": context.risk_confidence,
        },

        "position": {
            "current": context.current_position,
            "proposed": context.proposed_position,
        },

        "exposure": {
            "current": context.current_exposure,
            "proposed": context.proposed_exposure,
        },

        "execution": {
            "broker": context.broker,
            "venue": context.venue,
            "channel": context.execution_channel,
            "order_type": context.order_type,
            "quantity": context.quantity,
            "price": context.price,
        },

        "session": {
            "session": context.session,
            "market_phase": context.market_phase,
            "closing_window": context.closing_window,
            "expiry_window": context.expiry_window,
        },
    }
# ============================================================
# CAS ORCHESTRATOR — PART 3
# Gate Execution + Result Normalization
# ============================================================

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple


# ------------------------------------------------------------
# GATE IMPORTS
# ------------------------------------------------------------

from .suitability_gate import (
    build_suitability_request,
    evaluate_suitability,
)

from .risk_gate import (
    build_risk_request,
    evaluate_risk,
)

from .exposure_gate import (
    build_exposure_request,
    evaluate_exposure,
)

from .position_gate import (
    build_position_request,
    evaluate_position,
)

from .execution_safety_gate import (
    build_execution_safety_request,
    evaluate_execution_safety,
)

from .compliance_gate import (
    build_compliance_request,
    evaluate_compliance,
)

from .restriction_engine import (
    build_restriction_request,
    evaluate_restriction,
)


# ------------------------------------------------------------
# CAS GATE EXECUTION RECORD
# ------------------------------------------------------------

@dataclass(frozen=True)
class CASGateExecution:
    gate: CASGateName
    status: str
    decision: str
    allowed: bool
    restricted: bool
    review_required: bool
    blocked: bool
    score: Optional[float]
    confidence: Optional[float]
    flags: Tuple[str, ...]
    restrictions: Tuple[str, ...]
    reason: str
    raw_result: Any = None


# ------------------------------------------------------------
# ENUM SAFE VALUE
# ------------------------------------------------------------

def _cas_enum_value(value: Any, default: str = "UNKNOWN") -> str:
    if value is None:
        return default

    raw = getattr(value, "value", value)

    try:
        text = str(raw).strip()
    except Exception:
        return default

    return text if text else default


# ------------------------------------------------------------
# GENERIC RESULT EXTRACTION
# ------------------------------------------------------------

def _extract_gate_result(
    gate: CASGateName,
    result: Any,
) -> CASGateExecution:

    status = _cas_enum_value(
        getattr(result, "status", None)
    )

    decision = _cas_enum_value(
        getattr(result, "decision", None)
    )

    allowed = bool(
        getattr(result, "allowed", False)
    )

    restricted = bool(
        getattr(result, "restricted", False)
    )

    review_required = bool(
        getattr(result, "review_required", False)
    )

    blocked = bool(
        getattr(result, "blocked", False)
    )

    score = getattr(
        result,
        "score",
        None,
    )

    confidence = getattr(
        result,
        "confidence",
        None,
    )

    flags = tuple(
        str(x)
        for x in (
            getattr(result, "flags", None)
            or ()
        )
    )

    restrictions = tuple(
        str(x)
        for x in (
            getattr(result, "restrictions", None)
            or ()
        )
    )

    reason = str(
        getattr(result, "reason", "")
        or ""
    )

    return CASGateExecution(
        gate=gate,
        status=status,
        decision=decision,
        allowed=allowed,
        restricted=restricted,
        review_required=review_required,
        blocked=blocked,
        score=score,
        confidence=confidence,
        flags=flags,
        restrictions=restrictions,
        reason=reason,
        raw_result=result,
    )


# ------------------------------------------------------------
# INDIVIDUAL GATE EXECUTION
# ------------------------------------------------------------

def execute_suitability_gate(
    request: CASRequest,
) -> CASGateExecution:
    context = build_cas_gate_context(request)
    payload = build_suitability_gate_request(context)
    gate_request = build_suitability_request(**payload)
    result = evaluate_suitability(gate_request)
    return _extract_gate_result(CASGateName.SUITABILITY, result)


def execute_risk_gate(
    request: CASRequest,
) -> CASGateExecution:
    context = build_cas_gate_context(request)
    payload = build_risk_gate_request(context)
    gate_request = build_risk_request(**payload)
    result = evaluate_risk(gate_request)
    return _extract_gate_result(CASGateName.RISK, result)


def execute_exposure_gate(
    request: CASRequest,
) -> CASGateExecution:
    context = build_cas_gate_context(request)
    payload = build_exposure_gate_request(context)
    gate_request = build_exposure_request(**payload)
    result = evaluate_exposure(gate_request)
    return _extract_gate_result(CASGateName.EXPOSURE, result)


def execute_position_gate(
    request: CASRequest,
) -> CASGateExecution:
    context = build_cas_gate_context(request)
    payload = build_position_gate_request(context)
    gate_request = build_position_request(**payload)
    result = evaluate_position(gate_request)
    return _extract_gate_result(CASGateName.POSITION, result)


def execute_execution_safety_gate(
    request: CASRequest,
) -> CASGateExecution:
    context = build_cas_gate_context(request)
    payload = build_execution_safety_gate_request(context)
    gate_request = build_execution_safety_request(**payload)
    result = evaluate_execution_safety(gate_request)
    return _extract_gate_result(CASGateName.EXECUTION_SAFETY, result)


def execute_compliance_gate(
    request: CASRequest,
) -> CASGateExecution:
    context = build_cas_gate_context(request)
    payload = build_compliance_gate_request(context)
    gate_request = build_compliance_request(**payload)
    result = evaluate_compliance(gate_request)
    return _extract_gate_result(CASGateName.COMPLIANCE, result)


def execute_restriction_gate(
    request: CASRequest,
) -> CASGateExecution:
    context = build_cas_gate_context(request)
    payload = build_restriction_gate_request(context)
    gate_request = build_restriction_request(**payload)
    result = evaluate_restriction(gate_request)
    return _extract_gate_result(CASGateName.RESTRICTION, result)


# ------------------------------------------------------------
# GATE DISPATCHER
# ------------------------------------------------------------

def execute_cas_gate(
    gate: CASGateName,
    request: CASRequest,
) -> CASGateExecution:

    if gate == CASGateName.SUITABILITY:
        return execute_suitability_gate(request)

    if gate == CASGateName.RISK:
        return execute_risk_gate(request)

    if gate == CASGateName.EXPOSURE:
        return execute_exposure_gate(request)

    if gate == CASGateName.POSITION:
        return execute_position_gate(request)

    if gate == CASGateName.EXECUTION_SAFETY:
        return execute_execution_safety_gate(request)

    if gate == CASGateName.COMPLIANCE:
        return execute_compliance_gate(request)

    if gate == CASGateName.RESTRICTION:
        return execute_restriction_gate(request)

    raise ValueError(
        f"Unsupported CAS gate: {gate}"
    )


# ------------------------------------------------------------
# GATE STOP CONDITIONS
# ------------------------------------------------------------

def cas_gate_should_stop(
    execution: CASGateExecution,
    requirements: CASGateRequirements,
) -> bool:

    if execution.blocked:
        return requirements.stop_on_block

    if execution.review_required:
        return requirements.stop_on_review

    return False


# ------------------------------------------------------------
# EXECUTE REQUIRED CAS GATES
# ------------------------------------------------------------

def execute_required_cas_gates(
    request: CASRequest,
    requirements: Optional[CASGateRequirements] = None,
) -> Tuple[CASGateExecution, ...]:

    requirements = (
        requirements
        or build_cas_gate_requirements()
    )

    executions = []

    for gate in CAS_GATE_ORDER:

        if not cas_gate_is_required(
            gate,
            requirements,
        ):
            continue

        execution = execute_cas_gate(
            gate,
            request,
        )

        executions.append(
            execution
        )

        if cas_gate_should_stop(
            execution,
            requirements,
        ):
            break

    return tuple(executions)


# ------------------------------------------------------------
# GATE RESULT AGGREGATION HELPERS
# ------------------------------------------------------------

def collect_cas_gate_flags(
    executions: Tuple[CASGateExecution, ...],
) -> Tuple[str, ...]:

    values = []

    for execution in executions:
        values.extend(
            execution.flags
        )

    return tuple(
        dict.fromkeys(values)
    )


def collect_cas_gate_restrictions(
    executions: Tuple[CASGateExecution, ...],
) -> Tuple[str, ...]:

    values = []

    for execution in executions:
        values.extend(
            execution.restrictions
        )

    return tuple(
        dict.fromkeys(values)
    )


def cas_has_blocked_gate(
    executions: Tuple[CASGateExecution, ...],
) -> bool:

    return any(
        execution.blocked
        for execution in executions
    )


def cas_has_review_gate(
    executions: Tuple[CASGateExecution, ...],
) -> bool:

    return any(
        execution.review_required
        for execution in executions
    )


def cas_has_restricted_gate(
    executions: Tuple[CASGateExecution, ...],
) -> bool:

    return any(
        execution.restricted
        for execution in executions
    )


def cas_all_gates_allowed(
    executions: Tuple[CASGateExecution, ...],
) -> bool:

    if not executions:
        return False

    return all(
        execution.allowed
        and not execution.blocked
        and not execution.review_required
        for execution in executions
    )


# ------------------------------------------------------------
# AGGREGATE SCORE
# ------------------------------------------------------------

def calculate_cas_gate_score(
    executions: Tuple[CASGateExecution, ...],
) -> Optional[float]:

    scores = [
        float(execution.score)
        for execution in executions
        if execution.score is not None
    ]

    if not scores:
        return None

    return sum(scores) / len(scores)


# ------------------------------------------------------------
# AGGREGATE CONFIDENCE
# ------------------------------------------------------------

def calculate_cas_gate_confidence(
    executions: Tuple[CASGateExecution, ...],
) -> Optional[float]:

    confidences = [
        float(execution.confidence)
        for execution in executions
        if execution.confidence is not None
    ]

    if not confidences:
        return None

    return sum(confidences) / len(confidences)


# ------------------------------------------------------------
# CAS-LEVEL DECISION PREVIEW
# ------------------------------------------------------------

def preview_cas_decision(
    executions: Tuple[CASGateExecution, ...],
) -> CASDecision:

    if not executions:
        return CASDecision.REVIEW_REQUIRED

    if cas_has_blocked_gate(
        executions
    ):
        return CASDecision.BLOCK

    if cas_has_review_gate(
        executions
    ):
        return CASDecision.REVIEW_REQUIRED

    if cas_has_restricted_gate(
        executions
    ):
        return CASDecision.ALLOW_WITH_RESTRICTION

    if cas_all_gates_allowed(
        executions
    ):
        return CASDecision.ALLOW

    return CASDecision.REVIEW_REQUIRED


# ------------------------------------------------------------
# CAS STATUS PREVIEW
# ------------------------------------------------------------

def preview_cas_status(
    executions: Tuple[CASGateExecution, ...],
) -> CASStatus:

    decision = preview_cas_decision(
        executions
    )

    if decision == CASDecision.BLOCK:
        return CASStatus.BLOCKED

    if decision == CASDecision.REVIEW_REQUIRED:
        return CASStatus.REVIEW_REQUIRED

    if decision == CASDecision.ALLOW_WITH_RESTRICTION:
        return CASStatus.RESTRICTED

    if decision == CASDecision.ALLOW:
        return CASStatus.AUTHORIZED

    return CASStatus.UNKNOWN


# ------------------------------------------------------------
# GATE EXECUTION SUMMARY
# ------------------------------------------------------------

def summarize_cas_gate_executions(
    executions: Tuple[CASGateExecution, ...],
) -> Dict[str, Any]:

    return {
        "gate_count": len(executions),
        "gates_executed": [
            execution.gate.value
            for execution in executions
        ],
        "blocked": cas_has_blocked_gate(
            executions
        ),
        "review_required": cas_has_review_gate(
            executions
        ),
        "restricted": cas_has_restricted_gate(
            executions
        ),
        "all_allowed": cas_all_gates_allowed(
            executions
        ),
        "decision_preview": preview_cas_decision(
            executions
        ).value,
        "status_preview": preview_cas_status(
            executions
        ).value,
        "score": calculate_cas_gate_score(
            executions
        ),
        "confidence": calculate_cas_gate_confidence(
            executions
        ),
        "flags": collect_cas_gate_flags(
            executions
        ),
        "restrictions": collect_cas_gate_restrictions(
            executions
        ),
    }


# ------------------------------------------------------------
# PUBLIC PART-3 VALIDATION
# ------------------------------------------------------------

def validate_cas_gate_execution(
    execution: CASGateExecution,
) -> bool:

    if not isinstance(
        execution,
        CASGateExecution,
    ):
        return False

    if execution.blocked and execution.allowed:
        return False

    if execution.review_required and execution.allowed:
        return False

    return True


def validate_cas_gate_executions(
    executions: Tuple[CASGateExecution, ...],
) -> bool:

    if not isinstance(
        executions,
        tuple,
    ):
        return False

    return all(
        validate_cas_gate_execution(
            execution
        )
        for execution in executions
    )
# ============================================================
# CAS ORCHESTRATOR — PART 4
# Final Aggregation + Authorization Contract + Audit
# ============================================================

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple


# ------------------------------------------------------------
# FINAL CAS RESULT
# ------------------------------------------------------------

@dataclass(frozen=True)
class CASResult:
    status: CASStatus
    decision: CASDecision
    allowed: bool
    restricted: bool
    review_required: bool
    blocked: bool

    pathway: CASPathway

    score: Optional[float]
    confidence: Optional[float]

    gates_executed: Tuple[str, ...]
    flags: Tuple[str, ...]
    restrictions: Tuple[str, ...]

    blocking_gates: Tuple[str, ...]
    review_gates: Tuple[str, ...]

    reason: str
    request_id: Optional[str] = None


# ------------------------------------------------------------
# CAS CONTRACT
# ------------------------------------------------------------

@dataclass(frozen=True)
class CASContract:
    status: CASContractStatus
    request: CASRequest
    gate_executions: Tuple[CASGateExecution, ...]
    result: CASResult
    created_at: Any
    evaluated_at: Any


# ------------------------------------------------------------
# FINAL DECISION
# ------------------------------------------------------------

def determine_cas_decision(
    executions: Tuple[CASGateExecution, ...],
) -> CASDecision:

    if not executions:
        return CASDecision.REVIEW_REQUIRED

    if cas_has_blocked_gate(executions):
        return CASDecision.BLOCK

    if cas_has_review_gate(executions):
        return CASDecision.REVIEW_REQUIRED

    if cas_has_restricted_gate(executions):
        return CASDecision.ALLOW_WITH_RESTRICTION

    if cas_all_gates_allowed(executions):
        return CASDecision.ALLOW

    return CASDecision.REVIEW_REQUIRED


# ------------------------------------------------------------
# FINAL STATUS
# ------------------------------------------------------------

def determine_cas_status(
    decision: CASDecision,
) -> CASStatus:

    if decision == CASDecision.ALLOW:
        return CASStatus.AUTHORIZED

    if decision == CASDecision.ALLOW_WITH_RESTRICTION:
        return CASStatus.RESTRICTED

    if decision == CASDecision.REVIEW_REQUIRED:
        return CASStatus.REVIEW_REQUIRED

    if decision == CASDecision.BLOCK:
        return CASStatus.BLOCKED

    return CASStatus.UNKNOWN


# ------------------------------------------------------------
# GATE NAME COLLECTION
# ------------------------------------------------------------

def collect_blocking_gates(
    executions: Tuple[CASGateExecution, ...],
) -> Tuple[str, ...]:

    return tuple(
        execution.gate.value
        for execution in executions
        if execution.blocked
    )


def collect_review_gates(
    executions: Tuple[CASGateExecution, ...],
) -> Tuple[str, ...]:

    return tuple(
        execution.gate.value
        for execution in executions
        if execution.review_required
    )


# ------------------------------------------------------------
# FINAL REASON
# ------------------------------------------------------------

def build_cas_reason(
    decision: CASDecision,
    executions: Tuple[CASGateExecution, ...],
) -> str:

    if decision == CASDecision.BLOCK:
        gates = collect_blocking_gates(executions)
        return (
            "CAS BLOCK: one or more mandatory gates "
            f"blocked the pathway: {', '.join(gates)}."
        )

    if decision == CASDecision.REVIEW_REQUIRED:
        gates = collect_review_gates(executions)
        if gates:
            return (
                "CAS REVIEW_REQUIRED: one or more mandatory "
                f"gates require review: {', '.join(gates)}."
            )

        return (
            "CAS REVIEW_REQUIRED: gate state is insufficient "
            "for final authorization."
        )

    if decision == CASDecision.ALLOW_WITH_RESTRICTION:
        restrictions = collect_cas_gate_restrictions(
            executions
        )

        if restrictions:
            return (
                "CAS ALLOW_WITH_RESTRICTION: pathway is "
                "permitted subject to supplied restrictions."
            )

        return (
            "CAS ALLOW_WITH_RESTRICTION: conditional "
            "gate state requires restriction handling."
        )

    if decision == CASDecision.ALLOW:
        return (
            "CAS ALLOW: all executed mandatory gates "
            "passed without blocking or review state."
        )

    return "CAS state unresolved."


# ------------------------------------------------------------
# FINAL RESULT BUILDER
# ------------------------------------------------------------

def build_cas_result(
    request: CASRequest,
    executions: Tuple[CASGateExecution, ...],
) -> CASResult:

    decision = determine_cas_decision(
        executions
    )

    status = determine_cas_status(
        decision
    )

    pathway = classify_cas_pathway(
        request.action
    )

    return CASResult(
        status=status,
        decision=decision,

        allowed=(
            decision in (
                CASDecision.ALLOW,
                CASDecision.ALLOW_WITH_RESTRICTION,
            )
        ),

        restricted=(
            decision
            == CASDecision.ALLOW_WITH_RESTRICTION
        ),

        review_required=(
            decision
            == CASDecision.REVIEW_REQUIRED
        ),

        blocked=(
            decision
            == CASDecision.BLOCK
        ),

        pathway=pathway,

        score=calculate_cas_gate_score(
            executions
        ),

        confidence=calculate_cas_gate_confidence(
            executions
        ),

        gates_executed=tuple(
            execution.gate.value
            for execution in executions
        ),

        flags=collect_cas_gate_flags(
            executions
        ),

        restrictions=collect_cas_gate_restrictions(
            executions
        ),

        blocking_gates=collect_blocking_gates(
            executions
        ),

        review_gates=collect_review_gates(
            executions
        ),

        reason=build_cas_reason(
            decision,
            executions,
        ),

        request_id=request.request_id,
    )


# ------------------------------------------------------------
# CAS CONTRACT STATE
# ------------------------------------------------------------

def determine_cas_contract_status(
    result: CASResult,
) -> CASContractStatus:

    if result.blocked:
        return CASContractStatus.BLOCKED

    if result.review_required:
        return CASContractStatus.REVIEW

    if result.restricted:
        return CASContractStatus.RESTRICTED

    if result.allowed:
        return CASContractStatus.AUTHORIZED

    return CASContractStatus.INVALID


# ------------------------------------------------------------
# CAS CONTRACT BUILDER
# ------------------------------------------------------------

def build_cas_contract(
    request: CASRequest,
    executions: Tuple[CASGateExecution, ...],
) -> CASContract:

    result = build_cas_result(
        request,
        executions,
    )

    now = _cas_timestamp(
        getattr(request, "timestamp", None)
    )

    return CASContract(
        status=determine_cas_contract_status(
            result
        ),
        request=request,
        gate_executions=executions,
        result=result,
        created_at=now,
        evaluated_at=now,
    )


# ------------------------------------------------------------
# CAS CONTRACT VALIDATION
# ------------------------------------------------------------

def validate_cas_result(
    result: CASResult,
) -> bool:

    if not isinstance(
        result,
        CASResult,
    ):
        return False

    if result.allowed and result.blocked:
        return False

    if result.allowed and result.review_required:
        return False

    if result.blocked and result.restricted:
        return False

    if result.blocked:
        if result.decision != CASDecision.BLOCK:
            return False

    if result.review_required:
        if result.decision != CASDecision.REVIEW_REQUIRED:
            return False

    return True


def validate_cas_contract(
    contract: CASContract,
) -> bool:

    if not isinstance(
        contract,
        CASContract,
    ):
        return False

    if not validate_cas_result(
        contract.result
    ):
        return False

    if not validate_cas_gate_executions(
        contract.gate_executions
    ):
        return False

    if (
        contract.status
        != determine_cas_contract_status(
            contract.result
        )
    ):
        return False

    return True


# ------------------------------------------------------------
# AUTHORIZATION SAFETY
# ------------------------------------------------------------

def cas_is_authorized(
    result: CASResult,
) -> bool:

    return (
        validate_cas_result(result)
        and result.decision == CASDecision.ALLOW
        and result.status == CASStatus.AUTHORIZED
        and result.allowed
        and not result.restricted
        and not result.review_required
        and not result.blocked
    )


def cas_is_restricted(
    result: CASResult,
) -> bool:

    return (
        validate_cas_result(result)
        and result.decision
        == CASDecision.ALLOW_WITH_RESTRICTION
        and result.restricted
        and result.allowed
        and not result.blocked
    )


def cas_requires_review(
    result: CASResult,
) -> bool:

    return (
        validate_cas_result(result)
        and result.decision
        == CASDecision.REVIEW_REQUIRED
        and result.review_required
    )


def cas_is_blocked(
    result: CASResult,
) -> bool:

    return (
        validate_cas_result(result)
        and result.decision
        == CASDecision.BLOCK
        and result.blocked
    )


# ------------------------------------------------------------
# EXECUTION AUTHORITY BOUNDARY
# ------------------------------------------------------------

def cas_authorizes_execution(
    result: CASResult,
) -> bool:

    """
    CAS may authorize a pathway only after all mandatory
    CAS gates pass.

    This does NOT place an order.
    """

    return cas_is_authorized(result)


def cas_places_orders() -> bool:
    return False


def cas_changes_position() -> bool:
    return False


def cas_generates_market_decision() -> bool:
    return False


def cas_generates_alpha() -> bool:
    return False


def cas_modifies_d13() -> bool:
    return False


def cas_overrides_d13() -> bool:
    return False


def cas_replaces_risk_authority() -> bool:
    return False


def cas_overrides_risk_authority() -> bool:
    return False


def cas_bypasses_gate() -> bool:
    return False


# ------------------------------------------------------------
# AUTHORITY INTEGRITY
# ------------------------------------------------------------

def cas_authority_integrity_ok() -> bool:

    return (
        not cas_places_orders()
        and not cas_changes_position()
        and not cas_generates_market_decision()
        and not cas_generates_alpha()
        and not cas_modifies_d13()
        and not cas_overrides_d13()
        and not cas_replaces_risk_authority()
        and not cas_overrides_risk_authority()
        and not cas_bypasses_gate()
    )


def cas_has_authority_conflict() -> bool:
    return not cas_authority_integrity_ok()


# ------------------------------------------------------------
# STOP / CONTINUE SEMANTICS
# ------------------------------------------------------------

def cas_can_continue(
    result: CASResult,
) -> bool:

    return (
        result.decision
        in (
            CASDecision.ALLOW,
            CASDecision.ALLOW_WITH_RESTRICTION,
        )
        and not result.blocked
        and not result.review_required
    )


def cas_must_stop(
    result: CASResult,
) -> bool:

    return (
        result.blocked
        or result.review_required
    )


# ------------------------------------------------------------
# PATHWAY SAFETY
# ------------------------------------------------------------

def cas_pathway_authorized(
    result: CASResult,
    pathway: CASPathway,
) -> bool:

    if not cas_can_continue(result):
        return False

    if result.pathway != pathway:
        return False

    return True


# ------------------------------------------------------------
# FULL CAS EVALUATION
# ------------------------------------------------------------

def evaluate_cas(
    request: CASRequest,
    requirements: Optional[CASGateRequirements] = None,
) -> CASContract:

    if not validate_cas_request(request):
        empty = tuple()

        result = CASResult(
            status=CASStatus.ERROR,
            decision=CASDecision.REVIEW_REQUIRED,
            allowed=False,
            restricted=False,
            review_required=True,
            blocked=False,
            pathway=classify_cas_pathway(
                request.action
            ),
            score=None,
            confidence=None,
            gates_executed=tuple(),
            flags=("INVALID_CAS_REQUEST",),
            restrictions=tuple(),
            blocking_gates=tuple(),
            review_gates=tuple(),
            reason="CAS request validation failed.",
            request_id=request.request_id,
        )

        now = _cas_timestamp(
            getattr(request, "timestamp", None)
        )

        return CASContract(
            status=CASContractStatus.INVALID,
            request=request,
            gate_executions=empty,
            result=result,
            created_at=now,
            evaluated_at=now,
        )

    requirements = (
        requirements
        or build_cas_gate_requirements()
    )

    authority_context = build_cas_gate_context(
        request
    )

    authority_validation = validate_cas_authority_context(
        authority_context,
        requirements,
    )

    if not authority_validation.valid:
        executions = tuple()

        result = CASResult(
            status=CASStatus.ERROR,
            decision=CASDecision.BLOCK,
            allowed=False,
            restricted=False,
            review_required=False,
            blocked=True,
            pathway=classify_cas_pathway(
                request.action
            ),
            score=None,
            confidence=None,
            gates_executed=tuple(),
            flags=("CAS_AUTHORITY_CONTEXT_INVALID",),
            restrictions=tuple(),
            blocking_gates=("CAS",),
            review_gates=tuple(),
            reason=(
                "CAS authority context is invalid. "
                "Final authorization is blocked."
            ),
            request_id=request.request_id,
        )

        now = _cas_timestamp(
            getattr(request, "timestamp", None)
        )

        return CASContract(
            status=CASContractStatus.BLOCKED,
            request=request,
            gate_executions=executions,
            result=result,
            created_at=now,
            evaluated_at=now,
        )

    executions = execute_required_cas_gates(
        request,
        requirements,
    )

    return build_cas_contract(
        request,
        executions,
    )


# ------------------------------------------------------------
# CAS AUDIT RECORD
# ------------------------------------------------------------

@dataclass(frozen=True)
class CASAudiRecord:
    request_id: Optional[str]
    pathway: str
    decision: str
    status: str
    allowed: bool
    restricted: bool
    review_required: bool
    blocked: bool
    gates_executed: Tuple[str, ...]
    blocking_gates: Tuple[str, ...]
    review_gates: Tuple[str, ...]
    flags: Tuple[str, ...]
    restrictions: Tuple[str, ...]
    score: Optional[float]
    confidence: Optional[float]
    reason: str
    authority_integrity_ok: bool
    timestamp: Any


# ------------------------------------------------------------
# AUDIT BUILDER
# ------------------------------------------------------------

def build_cas_audit(
    contract: CASContract,
) -> CASAudiRecord:

    result = contract.result

    return CASAudiRecord(
        request_id=result.request_id,
        pathway=result.pathway.value,
        decision=result.decision.value,
        status=result.status.value,
        allowed=result.allowed,
        restricted=result.restricted,
        review_required=result.review_required,
        blocked=result.blocked,
        gates_executed=result.gates_executed,
        blocking_gates=result.blocking_gates,
        review_gates=result.review_gates,
        flags=result.flags,
        restrictions=result.restrictions,
        score=result.score,
        confidence=result.confidence,
        reason=result.reason,
        authority_integrity_ok=cas_authority_integrity_ok(),
        timestamp=contract.evaluated_at,
    )


# ------------------------------------------------------------
# SERIALIZATION
# ------------------------------------------------------------

def cas_result_to_dict(
    result: CASResult,
) -> Dict[str, Any]:

    return {
        "status": result.status.value,
        "decision": result.decision.value,
        "allowed": result.allowed,
        "restricted": result.restricted,
        "review_required": result.review_required,
        "blocked": result.blocked,
        "pathway": result.pathway.value,
        "score": result.score,
        "confidence": result.confidence,
        "gates_executed": list(
            result.gates_executed
        ),
        "flags": list(result.flags),
        "restrictions": list(
            result.restrictions
        ),
        "blocking_gates": list(
            result.blocking_gates
        ),
        "review_gates": list(
            result.review_gates
        ),
        "reason": result.reason,
        "request_id": result.request_id,
    }


def cas_contract_to_dict(
    contract: CASContract,
) -> Dict[str, Any]:

    return {
        "status": contract.status.value,
        "result": cas_result_to_dict(
            contract.result
        ),
        "gate_executions": [
            {
                "gate": execution.gate.value,
                "status": execution.status,
                "decision": execution.decision,
                "allowed": execution.allowed,
                "restricted": execution.restricted,
                "review_required": execution.review_required,
                "blocked": execution.blocked,
                "score": execution.score,
                "confidence": execution.confidence,
                "flags": list(
                    execution.flags
                ),
                "restrictions": list(
                    execution.restrictions
                ),
                "reason": execution.reason,
            }
            for execution
            in contract.gate_executions
        ],
        "created_at": contract.created_at,
        "evaluated_at": contract.evaluated_at,
    }


# ------------------------------------------------------------
# CAS SUMMARY
# ------------------------------------------------------------

def summarize_cas(
    contract: CASContract,
) -> Dict[str, Any]:

    result = contract.result

    return {
        "status": result.status.value,
        "decision": result.decision.value,
        "pathway": result.pathway.value,
        "allowed": result.allowed,
        "restricted": result.restricted,
        "review_required": result.review_required,
        "blocked": result.blocked,
        "score": result.score,
        "confidence": result.confidence,
        "gates": list(
            result.gates_executed
        ),
        "blocking_gates": list(
            result.blocking_gates
        ),
        "review_gates": list(
            result.review_gates
        ),
        "restrictions": list(
            result.restrictions
        ),
        "reason": result.reason,
    }


# ------------------------------------------------------------
# OPERATIONAL CHECK
# ------------------------------------------------------------

def cas_operational() -> bool:

    return (
        cas_authority_integrity_ok()
        and callable(evaluate_cas)
        and callable(build_cas_result)
        and callable(build_cas_contract)
        and callable(validate_cas_contract)
        and callable(build_cas_audit)
    )


def validate_cas(
    contract: CASContract,
) -> bool:

    return (
        cas_operational()
        and validate_cas_contract(contract)
    )


# ------------------------------------------------------------
# SNAPSHOT
# ------------------------------------------------------------

def cas_snapshot(
    contract: CASContract,
) -> Dict[str, Any]:

    return {
        "engine": CAS_ORCHESTRATOR_ENGINE,
        "version": CAS_ORCHESTRATOR_VERSION,
        "operational": cas_operational(),
        "authority_integrity_ok":
            cas_authority_integrity_ok(),
        "contract_valid":
            validate_cas_contract(contract),
        "summary":
            summarize_cas(contract),
    }
# ============================================================
# CAS ORCHESTRATOR — PART 5
# Lifecycle + Engine + Public API + Health + Exports
# ============================================================


# ------------------------------------------------------------
# CAS LIFECYCLE
# ------------------------------------------------------------

class CASLifecycleState(str):
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
    RETAINED = "RETAINED"
    REJECTED = "REJECTED"


def determine_cas_lifecycle(
    result: CASResult,
) -> str:

    if result.blocked:
        return CASLifecycleState.REJECTED

    if result.review_required:
        return CASLifecycleState.ACTIVE

    if result.restricted:
        return CASLifecycleState.ACTIVE

    if result.allowed:
        return CASLifecycleState.ACTIVE

    return CASLifecycleState.REJECTED


def freeze_cas(
    contract: CASContract,
) -> CASContract:

    if not validate_cas_contract(contract):
        return contract

    return contract


def retain_cas(
    contract: CASContract,
) -> CASContract:

    if not validate_cas_contract(contract):
        return contract

    return contract


def reject_cas(
    contract: CASContract,
) -> CASContract:

    if not validate_cas_contract(contract):
        return contract

    return contract


# ------------------------------------------------------------
# CAS AUTHORITY STATEMENT
# ------------------------------------------------------------

def get_cas_authority_statement() -> str:
    return (
        "CAS is the authorization and execution-safety authority. "
        "CAS consumes D13 decision context and Risk context, "
        "evaluates mandatory safety/control gates, and returns "
        "ALLOW, ALLOW_WITH_RESTRICTION, REVIEW_REQUIRED, or BLOCK. "
        "CAS does not generate alpha, does not create the market "
        "decision, does not modify or override D13, does not "
        "replace Risk authority, and does not place orders."
    )


# ------------------------------------------------------------
# CAS ENGINE HEALTH
# ------------------------------------------------------------

@dataclass(frozen=True)
class CASEngineHealth:
    engine: str
    version: str
    operational: bool
    authority_integrity_ok: bool
    gate_order_valid: bool
    gate_count: int
    callable_evaluator: bool
    callable_validator: bool
    callable_audit: bool
    healthy: bool


def get_cas_engine_health() -> CASEngineHealth:

    authority_ok = (
        cas_authority_integrity_ok()
    )

    gate_order_ok = (
        validate_cas_gate_order()
    )

    evaluator_ok = callable(
        evaluate_cas
    )

    validator_ok = callable(
        validate_cas
    )

    audit_ok = callable(
        build_cas_audit
    )

    operational = (
        authority_ok
        and gate_order_ok
        and evaluator_ok
        and validator_ok
        and audit_ok
    )

    return CASEngineHealth(
        engine=CAS_ORCHESTRATOR_ENGINE,
        version=CAS_ORCHESTRATOR_VERSION,
        operational=operational,
        authority_integrity_ok=authority_ok,
        gate_order_valid=gate_order_ok,
        gate_count=len(CAS_GATE_ORDER),
        callable_evaluator=evaluator_ok,
        callable_validator=validator_ok,
        callable_audit=audit_ok,
        healthy=operational,
    )


# ------------------------------------------------------------
# CAS ENGINE INFO
# ------------------------------------------------------------

def get_cas_engine_info() -> Dict[str, Any]:

    return {
        "engine": CAS_ORCHESTRATOR_ENGINE,
        "version": CAS_ORCHESTRATOR_VERSION,
        "role": (
            "Authorization and execution-safety "
            "orchestration authority"
        ),
        "gate_order": [
            gate.value
            for gate in CAS_GATE_ORDER
        ],
        "gate_count": len(
            CAS_GATE_ORDER
        ),
        "decision_states": [
            decision.value
            for decision in CASDecision
        ],
        "status_states": [
            status.value
            for status in CASStatus
        ],
        "pathways": [
            pathway.value
            for pathway in CASPathway
        ],
        "authority_statement":
            get_cas_authority_statement(),
    }


# ------------------------------------------------------------
# GATE INTEGRITY
# ------------------------------------------------------------

def cas_gate_integrity_ok() -> bool:

    required = {
        CASGateName.SUITABILITY,
        CASGateName.RISK,
        CASGateName.EXPOSURE,
        CASGateName.POSITION,
        CASGateName.EXECUTION_SAFETY,
        CASGateName.COMPLIANCE,
        CASGateName.RESTRICTION,
    }

    actual = set(
        CAS_GATE_ORDER
    )

    return (
        actual == required
        and len(CAS_GATE_ORDER) == 7
        and validate_cas_gate_order()
    )


def cas_integrity_ok() -> bool:

    return (
        cas_authority_integrity_ok()
        and cas_gate_integrity_ok()
        and cas_operational()
    )


# ------------------------------------------------------------
# SINGLETON ENGINE
# ------------------------------------------------------------

class CASOrchestrator:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(
                cls
            )
        return cls._instance

    def evaluate(
        self,
        request: CASRequest,
        requirements: Optional[
            CASGateRequirements
        ] = None,
    ) -> CASContract:

        return evaluate_cas(
            request,
            requirements,
        )

    def check(
        self,
        request: CASRequest,
        requirements: Optional[
            CASGateRequirements
        ] = None,
    ) -> CASResult:

        contract = self.evaluate(
            request,
            requirements,
        )

        return contract.result

    def authorize(
        self,
        request: CASRequest,
        requirements: Optional[
            CASGateRequirements
        ] = None,
    ) -> bool:

        result = self.check(
            request,
            requirements,
        )

        return cas_authorizes_execution(
            result
        )

    def review(
        self,
        request: CASRequest,
        requirements: Optional[
            CASGateRequirements
        ] = None,
    ) -> CASContract:

        requirements = (
            requirements
            or build_cas_gate_requirements()
        )

        contract = self.evaluate(
            request,
            requirements,
        )

        return contract

    def audit(
        self,
        contract: CASContract,
    ) -> CASAudiRecord:

        return build_cas_audit(
            contract
        )

    def health(
        self,
    ) -> CASEngineHealth:

        return get_cas_engine_health()

    def info(
        self,
    ) -> Dict[str, Any]:

        return get_cas_engine_info()


# ------------------------------------------------------------
# SINGLETON ACCESSOR
# ------------------------------------------------------------

_CAS_ENGINE: Optional[
    CASOrchestrator
] = None


def get_cas_orchestrator() -> CASOrchestrator:

    global _CAS_ENGINE

    if _CAS_ENGINE is None:
        _CAS_ENGINE = CASOrchestrator()

    return _CAS_ENGINE


# ------------------------------------------------------------
# PUBLIC EVALUATION API
# ------------------------------------------------------------

def evaluate_cas_request(
    request: CASRequest,
    requirements: Optional[
        CASGateRequirements
    ] = None,
) -> CASContract:

    return get_cas_orchestrator().evaluate(
        request,
        requirements,
    )


def check_cas_request(
    request: CASRequest,
    requirements: Optional[
        CASGateRequirements
    ] = None,
) -> CASResult:

    return get_cas_orchestrator().check(
        request,
        requirements,
    )


def authorize_cas_request(
    request: CASRequest,
    requirements: Optional[
        CASGateRequirements
    ] = None,
) -> bool:

    return get_cas_orchestrator().authorize(
        request,
        requirements,
    )


def review_cas_request(
    request: CASRequest,
    requirements: Optional[
        CASGateRequirements
    ] = None,
) -> CASContract:

    return get_cas_orchestrator().review(
        request,
        requirements,
    )


# ------------------------------------------------------------
# RESULT ACCESSORS
# ------------------------------------------------------------

def get_cas_decision(
    result: CASResult,
) -> CASDecision:

    return result.decision


def get_cas_status(
    result: CASResult,
) -> CASStatus:

    return result.status


def get_cas_pathway(
    result: CASResult,
) -> CASPathway:

    return result.pathway


def get_cas_score(
    result: CASResult,
) -> Optional[float]:

    return result.score


def get_cas_confidence(
    result: CASResult,
) -> Optional[float]:

    return result.confidence


# ------------------------------------------------------------
# RESULT STATE HELPERS
# ------------------------------------------------------------

def cas_result_is_terminal(
    result: CASResult,
) -> bool:

    return (
        result.decision
        in (
            CASDecision.ALLOW,
            CASDecision.BLOCK,
        )
    )


def cas_result_needs_human_review(
    result: CASResult,
) -> bool:

    return (
        result.decision
        == CASDecision.REVIEW_REQUIRED
    )


def cas_result_has_restrictions(
    result: CASResult,
) -> bool:

    return (
        result.restricted
        or bool(result.restrictions)
    )


# ------------------------------------------------------------
# CONTRACT STATE HELPERS
# ------------------------------------------------------------

def cas_contract_is_valid(
    contract: CASContract,
) -> bool:

    return validate_cas_contract(
        contract
    )


def cas_contract_is_authorized(
    contract: CASContract,
) -> bool:

    return (
        cas_contract_is_valid(contract)
        and cas_is_authorized(
            contract.result
        )
    )


def cas_contract_is_blocked(
    contract: CASContract,
) -> bool:

    return (
        cas_contract_is_valid(contract)
        and cas_is_blocked(
            contract.result
        )
    )


def cas_contract_requires_review(
    contract: CASContract,
) -> bool:

    return (
        cas_contract_is_valid(contract)
        and cas_requires_review(
            contract.result
        )
    )


# ------------------------------------------------------------
# FINAL CAS SNAPSHOT
# ------------------------------------------------------------

def build_cas_system_snapshot(
    contract: Optional[CASContract] = None,
) -> Dict[str, Any]:

    health = get_cas_engine_health()

    snapshot = {
        "engine": CAS_ORCHESTRATOR_ENGINE,
        "version": CAS_ORCHESTRATOR_VERSION,
        "health": {
            "operational":
                health.operational,
            "healthy":
                health.healthy,
            "authority_integrity_ok":
                health.authority_integrity_ok,
            "gate_order_valid":
                health.gate_order_valid,
            "gate_count":
                health.gate_count,
        },
        "integrity": {
            "cas_integrity_ok":
                cas_integrity_ok(),
            "authority_integrity_ok":
                cas_authority_integrity_ok(),
            "gate_integrity_ok":
                cas_gate_integrity_ok(),
        },
        "authority": {
            "generates_alpha":
                cas_generates_alpha(),
            "generates_market_decision":
                cas_generates_market_decision(),
            "modifies_d13":
                cas_modifies_d13(),
            "overrides_d13":
                cas_overrides_d13(),
            "replaces_risk_authority":
                cas_replaces_risk_authority(),
            "overrides_risk_authority":
                cas_overrides_risk_authority(),
            "places_orders":
                cas_places_orders(),
            "changes_position":
                cas_changes_position(),
            "bypasses_gate":
                cas_bypasses_gate(),
        },
    }

    if contract is not None:
        snapshot["contract"] = (
            cas_contract_to_dict(
                contract
            )
        )

    return snapshot


# ------------------------------------------------------------
# FINAL PUBLIC EXPORTS
# ------------------------------------------------------------

__all__ = [
    # Constants
    "CAS_ORCHESTRATOR_ENGINE",
    "CAS_ORCHESTRATOR_VERSION",
    "CAS_GATE_ORDER",

    # Enums
    "CASStatus",
    "CASDecision",
    "CASMode",
    "CASPriority",
    "CASContractStatus",
    "CASPathway",
    "CASGateName",

    # Contracts
    "CASRequest",
    "CASGateContext",
    "CASGateRequirements",
    "CASGateResult",
    "CASContractValidation",
    "CASGateExecution",
    "CASResult",
    "CASContract",
    "CASAudiRecord",
    "CASELifecycleState",
    "CASEngineHealth",

    # Request / context
    "build_cas_request",
    "validate_cas_request",
    "build_cas_gate_context",
    "build_cas_gate_requirements",
    "get_required_cas_gates",
    "cas_gate_is_required",
    "validate_cas_authority_context",
    "build_cas_gate_requests",
    "validate_cas_gate_order",
    "classify_cas_pathway",
    "summarize_cas_gate_context",

    # Gate execution
    "execute_suitability_gate",
    "execute_risk_gate",
    "execute_exposure_gate",
    "execute_position_gate",
    "execute_execution_safety_gate",
    "execute_compliance_gate",
    "execute_restriction_gate",
    "execute_cas_gate",
    "execute_required_cas_gates",

    # Gate aggregation
    "collect_cas_gate_flags",
    "collect_cas_gate_restrictions",
    "cas_has_blocked_gate",
    "cas_has_review_gate",
    "cas_has_restricted_gate",
    "cas_all_gates_allowed",
    "calculate_cas_gate_score",
    "calculate_cas_gate_confidence",
    "preview_cas_decision",
    "preview_cas_status",
    "summarize_cas_gate_executions",
    "validate_cas_gate_execution",
    "validate_cas_gate_executions",

    # Final result / contract
    "determine_cas_decision",
    "determine_cas_status",
    "collect_blocking_gates",
    "collect_review_gates",
    "build_cas_reason",
    "build_cas_result",
    "determine_cas_contract_status",
    "build_cas_contract",
    "validate_cas_result",
    "validate_cas_contract",

    # Authorization
    "cas_is_authorized",
    "cas_is_restricted",
    "cas_requires_review",
    "cas_is_blocked",
    "cas_can_continue",
    "cas_must_stop",
    "cas_pathway_authorized",
    "cas_authorizes_execution",

    # Authority boundaries
    "cas_places_orders",
    "cas_changes_position",
    "cas_generates_market_decision",
    "cas_generates_alpha",
    "cas_modifies_d13",
    "cas_overrides_d13",
    "cas_replaces_risk_authority",
    "cas_overrides_risk_authority",
    "cas_bypasses_gate",
    "cas_authority_integrity_ok",
    "cas_has_authority_conflict",

    # Lifecycle
    "determine_cas_lifecycle",
    "freeze_cas",
    "retain_cas",
    "reject_cas",

    # Audit / serialization
    "build_cas_audit",
    "cas_result_to_dict",
    "cas_contract_to_dict",
    "summarize_cas",
    "cas_snapshot",

    # Engine
    "CASOrchestrator",
    "get_cas_orchestrator",

    # Public APIs
    "evaluate_cas",
    "evaluate_cas_request",
    "check_cas_request",
    "authorize_cas_request",
    "review_cas_request",

    # Accessors
    "get_cas_decision",
    "get_cas_status",
    "get_cas_pathway",
    "get_cas_score",
    "get_cas_confidence",

    # State helpers
    "cas_result_is_terminal",
    "cas_result_needs_human_review",
    "cas_result_has_restrictions",
    "cas_contract_is_valid",
    "cas_contract_is_authorized",
    "cas_contract_is_blocked",
    "cas_contract_requires_review",

    # Health / integrity
    "cas_operational",
    "validate_cas",
    "get_cas_engine_health",
    "get_cas_engine_info",
    "cas_gate_integrity_ok",
    "cas_integrity_ok",
    "get_cas_authority_statement",
    "build_cas_system_snapshot",
]