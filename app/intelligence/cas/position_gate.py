# ============================================================
# ROBOMLM CAS — POSITION GATE
# PART 1
# Contract • Enums • Request • Reference • Validation
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Mapping, Optional


# ============================================================
# ENGINE IDENTITY
# ============================================================

POSITION_GATE_ENGINE = "ROBOMLM_CAS_POSITION_GATE"
POSITION_GATE_VERSION = "1.0"


# ============================================================
# ENUMS
# ============================================================

class PositionStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    READY = "READY"
    NOT_READY = "NOT_READY"
    RESTRICTED = "RESTRICTED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"


class PositionDecision(str, Enum):
    ALLOW = "ALLOW"
    ALLOW_WITH_RESTRICTION = "ALLOW_WITH_RESTRICTION"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCK = "BLOCK"


class PositionMode(str, Enum):
    PAPER = "PAPER"
    DEMO = "DEMO"
    LIVE = "LIVE"
    MANUAL = "MANUAL"
    UNKNOWN = "UNKNOWN"


class PositionPriority(str, Enum):
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class PositionContractStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    ACTIVE = "ACTIVE"
    COMPLETE = "COMPLETE"
    REJECTED = "REJECTED"


# ============================================================
# POSITION REQUEST
# ============================================================

@dataclass(frozen=True)
class PositionRequest:
    """
    CAS Position Gate input contract.

    Position Gate evaluates whether the requested pathway is
    structurally compatible with the current position state.

    It does NOT create the market decision and does NOT modify
    D13, Risk Authority, or execution state.
    """

    market: str = ""
    instrument: str = ""
    contract: str = ""

    user_id: str = ""
    account_id: str = ""
    plan_id: str = ""

    action: str = ""
    direction: str = ""

    mode: PositionMode = PositionMode.UNKNOWN
    strategy: str = ""
    timeframe: str = ""

    priority: PositionPriority = PositionPriority.NORMAL

    # Current position state
    current_position: float = 0.0
    current_position_side: str = ""
    current_position_value: float = 0.0

    # Requested position change
    proposed_position: float = 0.0
    proposed_position_change: float = 0.0
    proposed_position_value: float = 0.0

    # Position boundaries
    max_position: Optional[float] = None
    min_position: Optional[float] = None

    # Quantity / pricing
    quantity: float = 0.0
    price: Optional[float] = None

    # Position lifecycle controls
    reduce_only: bool = False
    close_only: bool = False
    allow_new_position: bool = True
    allow_add_to_position: bool = True

    # Position state flags
    position_open: bool = False
    position_closing: bool = False
    position_locked: bool = False

    # Metadata
    metadata: Mapping[str, Any] = field(default_factory=dict)
    request_id: str = ""

    # Timestamp
    timestamp: Optional[str] = None


# ============================================================
# POSITION REFERENCE
# ============================================================

@dataclass(frozen=True)
class PositionReference:
    """
    Reference information used for position-state evaluation.
    """

    instrument: str = ""
    current_position: float = 0.0
    current_position_side: str = ""
    current_position_value: float = 0.0

    proposed_position: float = 0.0
    proposed_position_change: float = 0.0
    proposed_position_value: float = 0.0

    max_position: Optional[float] = None
    min_position: Optional[float] = None

    position_open: bool = False
    position_closing: bool = False
    position_locked: bool = False


# ============================================================
# CONTRACT VALIDATION
# ============================================================

@dataclass(frozen=True)
class PositionContractValidation:
    valid: bool
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    checked_at: str = ""


# ============================================================
# SAFE READ HELPERS
# ============================================================

def _pg_read_value(
    source: Any,
    key: str,
    default: Any = None,
) -> Any:
    if source is None:
        return default

    if isinstance(source, Mapping):
        return source.get(key, default)

    return getattr(source, key, default)


def _pg_text(
    value: Any,
    default: str = "",
) -> str:
    if value is None:
        return default

    return str(value).strip()


def _pg_enum(
    enum_type,
    value: Any,
    default,
):
    if isinstance(value, enum_type):
        return value

    if value is None:
        return default

    try:
        return enum_type(str(value).upper())
    except (ValueError, TypeError):
        return default


def _pg_number(
    value: Any,
    default: Optional[float] = None,
) -> Optional[float]:
    if value is None:
        return default

    if isinstance(value, bool):
        return default

    try:
        number = float(value)

        if number != number:
            return default

        return number
    except (TypeError, ValueError):
        return default


def _pg_bool(
    value: Any,
    default: bool = False,
) -> bool:
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        normalized = value.strip().lower()

        if normalized in {"true", "1", "yes", "y", "on"}:
            return True

        if normalized in {"false", "0", "no", "n", "off"}:
            return False

    return bool(value)


def _pg_timestamp(
    value: Any = None,
) -> str:
    if value:
        return str(value)

    return datetime.utcnow().isoformat()


# ============================================================
# REQUEST BUILDER
# ============================================================

def build_position_request(
    source: Any = None,
    **kwargs: Any,
) -> PositionRequest:
    """
    Build a normalized PositionRequest from mapping/object data.
    """

    def value(key: str, default: Any = None) -> Any:
        if key in kwargs:
            return kwargs[key]

        return _pg_read_value(source, key, default)

    return PositionRequest(
        market=_pg_text(value("market")),
        instrument=_pg_text(value("instrument")),
        contract=_pg_text(value("contract")),

        user_id=_pg_text(value("user_id")),
        account_id=_pg_text(value("account_id")),
        plan_id=_pg_text(value("plan_id")),

        action=_pg_text(value("action")).upper(),
        direction=_pg_text(value("direction")).upper(),

        mode=_pg_enum(
            PositionMode,
            value("mode"),
            PositionMode.UNKNOWN,
        ),

        strategy=_pg_text(value("strategy")),
        timeframe=_pg_text(value("timeframe")),

        priority=_pg_enum(
            PositionPriority,
            value("priority"),
            PositionPriority.NORMAL,
        ),

        current_position=_pg_number(
            value("current_position"),
            0.0,
        ) or 0.0,

        current_position_side=_pg_text(
            value("current_position_side")
        ).upper(),

        current_position_value=_pg_number(
            value("current_position_value"),
            0.0,
        ) or 0.0,

        proposed_position=_pg_number(
            value("proposed_position"),
            0.0,
        ) or 0.0,

        proposed_position_change=_pg_number(
            value("proposed_position_change"),
            0.0,
        ) or 0.0,

        proposed_position_value=_pg_number(
            value("proposed_position_value"),
            0.0,
        ) or 0.0,

        max_position=_pg_number(
            value("max_position")
        ),

        min_position=_pg_number(
            value("min_position")
        ),

        quantity=_pg_number(
            value("quantity"),
            0.0,
        ) or 0.0,

        price=_pg_number(
            value("price")
        ),

        reduce_only=_pg_bool(
            value("reduce_only"),
            False,
        ),

        close_only=_pg_bool(
            value("close_only"),
            False,
        ),

        allow_new_position=_pg_bool(
            value("allow_new_position"),
            True,
        ),

        allow_add_to_position=_pg_bool(
            value("allow_add_to_position"),
            True,
        ),

        position_open=_pg_bool(
            value("position_open"),
            False,
        ),

        position_closing=_pg_bool(
            value("position_closing"),
            False,
        ),

        position_locked=_pg_bool(
            value("position_locked"),
            False,
        ),

        metadata=value("metadata", {}) or {},
        request_id=_pg_text(value("request_id")),

        timestamp=_pg_timestamp(
            value("timestamp")
        ),
    )


# ============================================================
# NUMERIC VALIDATION
# ============================================================

def validate_position_numeric_inputs(
    request: PositionRequest,
) -> tuple[str, ...]:
    errors: list[str] = []

    numeric_fields = {
        "current_position": request.current_position,
        "current_position_value": request.current_position_value,
        "proposed_position": request.proposed_position,
        "proposed_position_change": request.proposed_position_change,
        "proposed_position_value": request.proposed_position_value,
        "quantity": request.quantity,
    }

    optional_numeric_fields = {
        "max_position": request.max_position,
        "min_position": request.min_position,
        "price": request.price,
    }

    for name, value in numeric_fields.items():
        if value is None:
            errors.append(f"{name}:MISSING")
            continue

        if isinstance(value, bool):
            errors.append(f"{name}:BOOLEAN_NOT_ALLOWED")
            continue

        try:
            number = float(value)

            if number != number:
                errors.append(f"{name}:NAN")

        except (TypeError, ValueError):
            errors.append(f"{name}:NOT_NUMERIC")

    for name, value in optional_numeric_fields.items():
        if value is None:
            continue

        if isinstance(value, bool):
            errors.append(f"{name}:BOOLEAN_NOT_ALLOWED")
            continue

        try:
            number = float(value)

            if number != number:
                errors.append(f"{name}:NAN")

        except (TypeError, ValueError):
            errors.append(f"{name}:NOT_NUMERIC")

    return tuple(errors)


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_position_request(
    request: PositionRequest,
) -> PositionContractValidation:

    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(request, PositionRequest):
        return PositionContractValidation(
            valid=False,
            errors=("REQUEST_TYPE_INVALID",),
            checked_at=_pg_timestamp(),
        )

    if not request.instrument:
        errors.append("INSTRUMENT_MISSING")

    if not request.action:
        errors.append("ACTION_MISSING")

    if request.mode == PositionMode.UNKNOWN:
        warnings.append("POSITION_MODE_UNKNOWN")

    errors.extend(
        validate_position_numeric_inputs(request)
    )

    if request.max_position is not None:
        if request.max_position < 0:
            errors.append("MAX_POSITION_NEGATIVE")

    if request.min_position is not None:
        if request.min_position < 0:
            errors.append("MIN_POSITION_NEGATIVE")

    if (
        request.min_position is not None
        and request.max_position is not None
        and request.min_position > request.max_position
    ):
        errors.append("POSITION_LIMIT_RANGE_INVALID")

    if request.quantity < 0:
        errors.append("QUANTITY_NEGATIVE")

    if request.price is not None and request.price <= 0:
        errors.append("PRICE_NON_POSITIVE")

    # A reduction/close pathway requires an existing position
    reduction_actions = {
        "REDUCE",
        "EXIT",
        "PROFIT_BOOK",
        "PARTIAL_EXIT",
        "CLOSE",
        "CLOSE_POSITION",
    }

    if (
        request.action in reduction_actions
        and not request.position_open
        and abs(request.current_position) <= 0
    ):
        warnings.append("REDUCTION_WITHOUT_OPEN_POSITION")

    # Position lock is a hard structural condition.
    if request.position_locked:
        warnings.append("POSITION_LOCKED")

    return PositionContractValidation(
        valid=len(errors) == 0,
        errors=tuple(errors),
        warnings=tuple(warnings),
        checked_at=_pg_timestamp(),
    )
# ============================================================
# POSITION GATE — PART 2
# Data State • Consistency • Readiness • Requirements
# Assessment • Position Semantics
# ============================================================


# ============================================================
# DATA STATE
# ============================================================

class PositionDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    INSUFFICIENT = "INSUFFICIENT"
    INVALID = "INVALID"


class PositionConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    INCONSISTENT = "INCONSISTENT"
    UNKNOWN = "UNKNOWN"


class PositionReadiness(str, Enum):
    READY = "READY"
    CONDITIONALLY_READY = "CONDITIONALLY_READY"
    NOT_READY = "NOT_READY"
    BLOCKED = "BLOCKED"


# ============================================================
# REQUIREMENTS
# ============================================================

@dataclass(frozen=True)
class PositionRequirements:
    """
    Structural requirements for Position Gate evaluation.
    """

    require_instrument: bool = True
    require_action: bool = True

    require_position_state: bool = True
    require_position_side_for_open: bool = False

    require_quantity_for_change: bool = False
    require_price_for_value: bool = False

    require_position_limits: bool = False

    allow_new_position: bool = True
    allow_add_to_position: bool = True

    allow_reduce_only: bool = True
    allow_close_only: bool = True


# ============================================================
# ASSESSMENT
# ============================================================

@dataclass(frozen=True)
class PositionAssessment:
    data_state: PositionDataState
    consistency: PositionConsistency
    readiness: PositionReadiness

    completeness: float
    requirements_met: bool

    current_position: float
    proposed_position: float
    projected_position: float
    position_change: float

    position_open: bool
    position_closing: bool
    position_locked: bool

    flags: tuple[str, ...] = ()
    restrictions: tuple[str, ...] = ()

    position_score: float = 0.0
    position_confidence: float = 0.0


# ============================================================
# ACTION SEMANTICS
# ============================================================

_POSITION_REDUCTION_ACTIONS = {
    "REDUCE",
    "EXIT",
    "PROFIT_BOOK",
    "PARTIAL_EXIT",
    "CLOSE",
    "CLOSE_POSITION",
}

_POSITION_EXPANSION_ACTIONS = {
    "NEW_ENTRY",
    "ENTRY",
    "ADD",
    "ADD_TO_POSITION",
    "SCALE_IN",
}

_POSITION_HOLD_ACTIONS = {
    "HOLD",
    "RETAIN",
    "MAINTAIN",
    "WAIT",
    "WATCH",
}

_POSITION_PLANNING_ACTIONS = {
    "NEXT_SESSION_PLAN",
    "PLAN",
    "PREPARE",
    "PREPARE_ENTRY",
}


def _pg_is_reduction_action(action: str) -> bool:
    return action.upper() in _POSITION_REDUCTION_ACTIONS


def _pg_is_expansion_action(action: str) -> bool:
    return action.upper() in _POSITION_EXPANSION_ACTIONS


def _pg_is_hold_action(action: str) -> bool:
    return action.upper() in _POSITION_HOLD_ACTIONS


def _pg_is_planning_action(action: str) -> bool:
    return action.upper() in _POSITION_PLANNING_ACTIONS


# ============================================================
# DATA STATE EVALUATION
# ============================================================

def evaluate_position_data_state(
    request: PositionRequest,
) -> PositionDataState:

    validation = validate_position_request(request)

    if not validation.valid:
        return PositionDataState.INVALID

    required_values = (
        request.instrument,
        request.action,
    )

    if not all(required_values):
        return PositionDataState.INSUFFICIENT

    position_state_present = any(
        (
            request.position_open,
            request.position_closing,
            request.position_locked,
            abs(request.current_position) > 0,
            abs(request.current_position_value) > 0,
        )
    )

    if not position_state_present:
        return PositionDataState.PARTIAL

    optional_missing = 0

    if request.current_position_side == "":
        optional_missing += 1

    if request.request_id == "":
        optional_missing += 1

    if optional_missing >= 2:
        return PositionDataState.PARTIAL

    return PositionDataState.COMPLETE


# ============================================================
# CONSISTENCY EVALUATION
# ============================================================

def evaluate_position_consistency(
    request: PositionRequest,
) -> PositionConsistency:

    if not isinstance(request, PositionRequest):
        return PositionConsistency.INCONSISTENT

    if validate_position_request(request).valid is False:
        return PositionConsistency.INCONSISTENT

    current = float(request.current_position)
    proposed = float(request.proposed_position)
    change = float(request.proposed_position_change)

    # The projected position must be coherent with the
    # explicitly supplied current position + proposed change.
    calculated_projected = current + change

    if abs(proposed) > 0:
        if abs(proposed - calculated_projected) > max(
            1e-9,
            abs(proposed) * 1e-6,
        ):
            return PositionConsistency.INCONSISTENT

    action = request.action.upper()

    # Reduction pathway:
    # reduction of an existing position is valid even when
    # projected exposure/position becomes smaller.
    if _pg_is_reduction_action(action):
        if abs(current) <= 0:
            return PositionConsistency.UNKNOWN

        if abs(change) > 0:
            if abs(calculated_projected) > abs(current):
                return PositionConsistency.INCONSISTENT

    # Expansion pathway:
    # increasing absolute position is valid only as an
    # expansion pathway.
    elif _pg_is_expansion_action(action):
        if abs(calculated_projected) < abs(current):
            return PositionConsistency.INCONSISTENT

    # Hold pathway:
    elif _pg_is_hold_action(action):
        if abs(change) > max(
            1e-9,
            abs(current) * 1e-6,
        ):
            return PositionConsistency.INCONSISTENT

    return PositionConsistency.CONSISTENT


# ============================================================
# COMPLETENESS
# ============================================================

def calculate_position_completeness(
    request: PositionRequest,
) -> float:

    checks = [
        bool(request.instrument),
        bool(request.action),
        request.mode != PositionMode.UNKNOWN,
        bool(request.strategy),
        bool(request.timeframe),
        bool(request.request_id),
        any(
            (
                request.position_open,
                request.position_closing,
                request.position_locked,
                abs(request.current_position) > 0,
            )
        ),
        request.current_position_side != "",
    ]

    if not checks:
        return 0.0

    return round(
        (sum(bool(x) for x in checks) / len(checks)) * 100.0,
        2,
    )


# ============================================================
# READINESS
# ============================================================

def evaluate_position_readiness(
    request: PositionRequest,
    data_state: Optional[PositionDataState] = None,
    consistency: Optional[PositionConsistency] = None,
) -> PositionReadiness:

    if data_state is None:
        data_state = evaluate_position_data_state(request)

    if consistency is None:
        consistency = evaluate_position_consistency(request)

    if data_state == PositionDataState.INVALID:
        return PositionReadiness.BLOCKED

    if consistency == PositionConsistency.INCONSISTENT:
        return PositionReadiness.BLOCKED

    if request.position_locked:
        return PositionReadiness.BLOCKED

    if data_state == PositionDataState.INSUFFICIENT:
        return PositionReadiness.NOT_READY

    if consistency == PositionConsistency.UNKNOWN:
        return PositionReadiness.CONDITIONALLY_READY

    if data_state == PositionDataState.PARTIAL:
        return PositionReadiness.CONDITIONALLY_READY

    return PositionReadiness.READY


# ============================================================
# REQUIREMENT EVALUATION
# ============================================================

def evaluate_position_requirements(
    request: PositionRequest,
    requirements: Optional[PositionRequirements] = None,
) -> tuple[bool, tuple[str, ...], tuple[str, ...]]:

    requirements = requirements or PositionRequirements()

    flags: list[str] = []
    restrictions: list[str] = []

    if requirements.require_instrument:
        if not request.instrument:
            flags.append("INSTRUMENT_MISSING")

    if requirements.require_action:
        if not request.action:
            flags.append("ACTION_MISSING")

    if requirements.require_position_state:
        if (
            not request.position_open
            and abs(request.current_position) <= 0
            and not request.position_closing
        ):
            if _pg_is_reduction_action(request.action):
                flags.append("POSITION_STATE_MISSING")

    if requirements.require_position_side_for_open:
        if request.position_open and not request.current_position_side:
            flags.append("POSITION_SIDE_MISSING")

    if requirements.require_quantity_for_change:
        if abs(request.proposed_position_change) > 0:
            if request.quantity <= 0:
                flags.append("QUANTITY_REQUIRED")

    if requirements.require_price_for_value:
        if (
            abs(request.proposed_position_value) > 0
            and request.price is None
        ):
            flags.append("PRICE_REQUIRED")

    if requirements.require_position_limits:
        if (
            request.max_position is None
            and request.min_position is None
        ):
            restrictions.append("POSITION_LIMITS_UNAVAILABLE")

    action = request.action.upper()

    # --------------------------------------------------------
    # NEW POSITION CONTROL
    # --------------------------------------------------------

    if _pg_is_expansion_action(action):

        if not requirements.allow_new_position:
            restrictions.append("NO_NEW_POSITION")

        if (
            request.position_open
            and not requirements.allow_add_to_position
        ):
            restrictions.append("NO_ADD_TO_POSITION")

        if not request.allow_new_position:
            restrictions.append("NEW_POSITION_DISABLED")

        if (
            request.position_open
            and not request.allow_add_to_position
        ):
            restrictions.append("ADD_TO_POSITION_DISABLED")

    # --------------------------------------------------------
    # REDUCTION CONTROL
    # --------------------------------------------------------

    if _pg_is_reduction_action(action):

        if request.reduce_only:
            if not requirements.allow_reduce_only:
                restrictions.append("REDUCE_ONLY_RESTRICTED")

        if request.close_only:
            if not requirements.allow_close_only:
                restrictions.append("CLOSE_ONLY_RESTRICTED")

    # --------------------------------------------------------
    # POSITION LIMITS
    # --------------------------------------------------------

    projected = (
        request.proposed_position
        if abs(request.proposed_position) > 0
        else request.current_position
        + request.proposed_position_change
    )

    if request.max_position is not None:
        if abs(projected) > abs(request.max_position):
            flags.append("MAX_POSITION_BREACH")

    if request.min_position is not None:
        if abs(projected) < abs(request.min_position):
            if _pg_is_expansion_action(action):
                flags.append("MIN_POSITION_BREACH")

    # --------------------------------------------------------
    # POSITION LOCK
    # --------------------------------------------------------

    if request.position_locked:
        flags.append("POSITION_LOCKED")

    requirements_met = len(flags) == 0

    return (
        requirements_met,
        tuple(flags),
        tuple(restrictions),
    )


# ============================================================
# FLAG EXTRACTION
# ============================================================

def extract_position_flags(
    request: PositionRequest,
    requirements: Optional[PositionRequirements] = None,
) -> tuple[str, ...]:

    _, flags, _ = evaluate_position_requirements(
        request,
        requirements,
    )

    return flags


def extract_position_restrictions(
    request: PositionRequest,
    requirements: Optional[PositionRequirements] = None,
) -> tuple[str, ...]:

    _, _, restrictions = evaluate_position_requirements(
        request,
        requirements,
    )

    result = list(restrictions)

    action = request.action.upper()

    if request.reduce_only:
        result.append("REDUCE_ONLY")

    if request.close_only:
        result.append("CLOSE_ONLY")

    if (
        _pg_is_expansion_action(action)
        and not request.allow_new_position
    ):
        result.append("NO_NEW_POSITION")

    if (
        request.position_open
        and _pg_is_expansion_action(action)
        and not request.allow_add_to_position
    ):
        result.append("NO_ADD_TO_POSITION")

    return tuple(dict.fromkeys(result))


# ============================================================
# POSITION SCORE
# ============================================================

def calculate_position_score(
    request: PositionRequest,
    data_state: Optional[PositionDataState] = None,
    consistency: Optional[PositionConsistency] = None,
    readiness: Optional[PositionReadiness] = None,
) -> float:

    data_state = (
        data_state
        or evaluate_position_data_state(request)
    )

    consistency = (
        consistency
        or evaluate_position_consistency(request)
    )

    readiness = (
        readiness
        or evaluate_position_readiness(
            request,
            data_state,
            consistency,
        )
    )

    score = 100.0

    if data_state == PositionDataState.PARTIAL:
        score -= 15.0
    elif data_state == PositionDataState.INSUFFICIENT:
        score -= 50.0
    elif data_state == PositionDataState.INVALID:
        score = 0.0

    if consistency == PositionConsistency.UNKNOWN:
        score -= 15.0
    elif consistency == PositionConsistency.INCONSISTENT:
        score = 0.0

    if readiness == PositionReadiness.CONDITIONALLY_READY:
        score -= 10.0
    elif readiness == PositionReadiness.NOT_READY:
        score -= 40.0
    elif readiness == PositionReadiness.BLOCKED:
        score = 0.0

    flags = extract_position_flags(request)

    if flags:
        score -= min(
            40.0,
            len(flags) * 10.0,
        )

    return round(
        max(0.0, min(100.0, score)),
        2,
    )


# ============================================================
# POSITION CONFIDENCE
# ============================================================

def calculate_position_confidence(
    request: PositionRequest,
    data_state: Optional[PositionDataState] = None,
    consistency: Optional[PositionConsistency] = None,
) -> float:

    data_state = (
        data_state
        or evaluate_position_data_state(request)
    )

    consistency = (
        consistency
        or evaluate_position_consistency(request)
    )

    completeness = calculate_position_completeness(
        request
    )

    confidence = completeness

    if consistency == PositionConsistency.CONSISTENT:
        confidence += 10.0
    elif consistency == PositionConsistency.UNKNOWN:
        confidence -= 15.0
    elif consistency == PositionConsistency.INCONSISTENT:
        confidence -= 50.0

    if data_state == PositionDataState.INVALID:
        confidence = 0.0

    return round(
        max(0.0, min(100.0, confidence)),
        2,
    )


# ============================================================
# ASSESSMENT BUILDER
# ============================================================

def build_position_assessment(
    request: PositionRequest,
    requirements: Optional[PositionRequirements] = None,
) -> PositionAssessment:

    data_state = evaluate_position_data_state(request)

    consistency = evaluate_position_consistency(request)

    readiness = evaluate_position_readiness(
        request,
        data_state,
        consistency,
    )

    requirements_met, requirement_flags, requirement_restrictions = (
        evaluate_position_requirements(
            request,
            requirements,
        )
    )

    flags = list(requirement_flags)

    restrictions = list(
        requirement_restrictions
    )

    # Additional structural flags
    if consistency == PositionConsistency.INCONSISTENT:
        flags.append("POSITION_STATE_INCONSISTENT")

    if consistency == PositionConsistency.UNKNOWN:
        flags.append("POSITION_STATE_UNCERTAIN")

    if data_state == PositionDataState.PARTIAL:
        flags.append("POSITION_DATA_PARTIAL")

    if data_state == PositionDataState.INSUFFICIENT:
        flags.append("POSITION_DATA_INSUFFICIENT")

    # --------------------------------------------------------
    # Projected position
    # --------------------------------------------------------

    projected_position = (
        request.proposed_position
        if abs(request.proposed_position) > 0
        else request.current_position
        + request.proposed_position_change
    )

    completeness = calculate_position_completeness(
        request
    )

    position_score = calculate_position_score(
        request,
        data_state,
        consistency,
        readiness,
    )

    position_confidence = calculate_position_confidence(
        request,
        data_state,
        consistency,
    )

    return PositionAssessment(
        data_state=data_state,
        consistency=consistency,
        readiness=readiness,

        completeness=completeness,
        requirements_met=requirements_met,

        current_position=request.current_position,
        proposed_position=request.proposed_position,
        projected_position=projected_position,
        position_change=request.proposed_position_change,

        position_open=request.position_open,
        position_closing=request.position_closing,
        position_locked=request.position_locked,

        flags=tuple(dict.fromkeys(flags)),
        restrictions=tuple(
            dict.fromkeys(restrictions)
        ),

        position_score=position_score,
        position_confidence=position_confidence,
    )
# ============================================================
# POSITION GATE — PART 3
# Action • Result • Contract • Decision Engine
# ============================================================


# ============================================================
# ACTION STATE
# ============================================================

class PositionActionState(str, Enum):
    ALLOW = "ALLOW"
    ALLOW_WITH_RESTRICTION = "ALLOW_WITH_RESTRICTION"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"
    NO_ACTION = "NO_ACTION"


class PositionContractState(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    ACTIVE = "ACTIVE"
    RESTRICTED = "RESTRICTED"
    REVIEW = "REVIEW"
    BLOCKED = "BLOCKED"
    COMPLETE = "COMPLETE"


class PositionResultStatus(str, Enum):
    SUCCESS = "SUCCESS"
    RESTRICTED = "RESTRICTED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"
    ERROR = "ERROR"


# ============================================================
# POSITION ACTION
# ============================================================

@dataclass(frozen=True)
class PositionAction:
    action: str
    action_state: PositionActionState
    decision: PositionDecision
    status: PositionStatus

    restrictions: tuple[str, ...] = ()
    flags: tuple[str, ...] = ()

    position_change: float = 0.0
    projected_position: float = 0.0


# ============================================================
# POSITION RESULT
# ============================================================

@dataclass(frozen=True)
class PositionResult:
    result_status: PositionResultStatus
    status: PositionStatus
    decision: PositionDecision

    action: PositionAction
    assessment: PositionAssessment


# ============================================================
# POSITION CONTRACT
# ============================================================

@dataclass(frozen=True)
class PositionContract:
    contract_status: PositionContractStatus

    request: PositionRequest
    assessment: PositionAssessment
    result: PositionResult


# ============================================================
# RESULT STATUS
# ============================================================

def determine_position_result_status(
    assessment: PositionAssessment,
    decision: PositionDecision,
) -> PositionResultStatus:

    if assessment.data_state == PositionDataState.INVALID:
        return PositionResultStatus.INVALID

    if decision == PositionDecision.BLOCK:
        return PositionResultStatus.BLOCKED

    if decision == PositionDecision.REVIEW_REQUIRED:
        return PositionResultStatus.REVIEW_REQUIRED

    if decision == PositionDecision.ALLOW_WITH_RESTRICTION:
        return PositionResultStatus.RESTRICTED

    if decision == PositionDecision.ALLOW:
        return PositionResultStatus.SUCCESS

    return PositionResultStatus.ERROR


# ============================================================
# POSITION STATUS
# ============================================================

def determine_position_status(
    assessment: PositionAssessment,
    decision: PositionDecision,
) -> PositionStatus:

    if assessment.data_state == PositionDataState.INVALID:
        return PositionStatus.INVALID

    if decision == PositionDecision.BLOCK:
        return PositionStatus.BLOCKED

    if decision == PositionDecision.REVIEW_REQUIRED:
        return PositionStatus.REVIEW_REQUIRED

    if decision == PositionDecision.ALLOW_WITH_RESTRICTION:
        return PositionStatus.RESTRICTED

    if assessment.readiness in (
        PositionReadiness.NOT_READY,
        PositionReadiness.BLOCKED,
    ):
        return PositionStatus.NOT_READY

    return PositionStatus.READY


# ============================================================
# ACTION STATE
# ============================================================

def determine_position_action_state(
    decision: PositionDecision,
) -> PositionActionState:

    if decision == PositionDecision.ALLOW:
        return PositionActionState.ALLOW

    if decision == PositionDecision.ALLOW_WITH_RESTRICTION:
        return PositionActionState.ALLOW_WITH_RESTRICTION

    if decision == PositionDecision.REVIEW_REQUIRED:
        return PositionActionState.REVIEW

    if decision == PositionDecision.BLOCK:
        return PositionActionState.BLOCK

    return PositionActionState.NO_ACTION


# ============================================================
# DECISION LOGIC
# ============================================================

def determine_position_decision(
    assessment: PositionAssessment,
) -> PositionDecision:

    # --------------------------------------------------------
    # Hard structural failures
    # --------------------------------------------------------

    if assessment.data_state == PositionDataState.INVALID:
        return PositionDecision.BLOCK

    if assessment.consistency == PositionConsistency.INCONSISTENT:
        return PositionDecision.BLOCK

    if assessment.position_locked:
        return PositionDecision.BLOCK

    if assessment.flags:
        hard_flags = {
            "INSTRUMENT_MISSING",
            "ACTION_MISSING",
            "POSITION_STATE_MISSING",
            "POSITION_LOCKED",
            "POSITION_STATE_INCONSISTENT",
            "MAX_POSITION_BREACH",
            "MIN_POSITION_BREACH",
        }

        if any(
            flag in hard_flags
            for flag in assessment.flags
        ):
            return PositionDecision.BLOCK

    # --------------------------------------------------------
    # Readiness
    # --------------------------------------------------------

    if assessment.readiness == PositionReadiness.BLOCKED:
        return PositionDecision.BLOCK

    if assessment.readiness == PositionReadiness.NOT_READY:
        return PositionDecision.REVIEW_REQUIRED

    # --------------------------------------------------------
    # Requirements
    # --------------------------------------------------------

    if not assessment.requirements_met:
        return PositionDecision.REVIEW_REQUIRED

    # --------------------------------------------------------
    # Partial / uncertain position state
    # --------------------------------------------------------

    if assessment.readiness == PositionReadiness.CONDITIONALLY_READY:
        return PositionDecision.ALLOW_WITH_RESTRICTION

    if assessment.consistency == PositionConsistency.UNKNOWN:
        return PositionDecision.ALLOW_WITH_RESTRICTION

    # --------------------------------------------------------
    # Explicit restrictions
    # --------------------------------------------------------

    if assessment.restrictions:
        return PositionDecision.ALLOW_WITH_RESTRICTION

    # --------------------------------------------------------
    # Strong position state
    # --------------------------------------------------------

    return PositionDecision.ALLOW


# ============================================================
# ACTION BUILDER
# ============================================================

def build_position_action(
    request: PositionRequest,
    assessment: PositionAssessment,
    decision: PositionDecision,
) -> PositionAction:

    return PositionAction(
        action=request.action,

        action_state=determine_position_action_state(
            decision
        ),

        decision=decision,

        status=determine_position_status(
            assessment,
            decision,
        ),

        restrictions=assessment.restrictions,
        flags=assessment.flags,

        position_change=(
            assessment.position_change
        ),

        projected_position=(
            assessment.projected_position
        ),
    )


# ============================================================
# RESULT BUILDER
# ============================================================

def build_position_result(
    assessment: PositionAssessment,
    action: PositionAction,
    decision: PositionDecision,
) -> PositionResult:

    return PositionResult(
        result_status=determine_position_result_status(
            assessment,
            decision,
        ),

        status=determine_position_status(
            assessment,
            decision,
        ),

        decision=decision,

        action=action,
        assessment=assessment,
    )


# ============================================================
# CONTRACT STATE
# ============================================================

def determine_position_contract_state(
    result: PositionResult,
) -> PositionContractStatus:

    if result.result_status == PositionResultStatus.INVALID:
        return PositionContractStatus.INVALID

    if result.result_status == PositionResultStatus.BLOCKED:
        return PositionContractStatus.BLOCKED

    if result.result_status == PositionResultStatus.REVIEW_REQUIRED:
        return PositionContractStatus.REVIEW

    if result.result_status == PositionResultStatus.RESTRICTED:
        return PositionContractStatus.RESTRICTED

    if result.result_status == PositionResultStatus.SUCCESS:
        return PositionContractStatus.ACTIVE

    return PositionContractStatus.COMPLETE


# ============================================================
# CONTRACT BUILDER
# ============================================================

def build_position_contract(
    request: PositionRequest,
    assessment: PositionAssessment,
    result: PositionResult,
) -> PositionContract:

    return PositionContract(
        contract_status=determine_position_contract_state(
            result
        ),

        request=request,
        assessment=assessment,
        result=result,
    )


# ============================================================
# POSITION GATE ENGINE
# ============================================================

class PositionGateEngine:
    """
    CAS Position Gate.

    Authority:
        Position-state compatibility/control only.

    It does not:
        - generate alpha
        - generate market direction
        - modify D13
        - override D13
        - replace Risk Authority
        - authorize execution
        - place orders
        - change positions
    """

    _instance: Optional["PositionGateEngine"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    @property
    def engine_name(self) -> str:
        return POSITION_GATE_ENGINE

    @property
    def version(self) -> str:
        return POSITION_GATE_VERSION

    def evaluate(
        self,
        request: PositionRequest | Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> PositionContract:

        normalized_request = (
            request
            if isinstance(request, PositionRequest)
            else build_position_request(
                request,
                **kwargs,
            )
        )

        validation = validate_position_request(
            normalized_request
        )

        if not validation.valid:
            assessment = build_position_assessment(
                normalized_request
            )

            decision = PositionDecision.BLOCK

            action = build_position_action(
                normalized_request,
                assessment,
                decision,
            )

            result = build_position_result(
                assessment,
                action,
                decision,
            )

            return build_position_contract(
                normalized_request,
                assessment,
                result,
            )

        assessment = build_position_assessment(
            normalized_request
        )

        decision = determine_position_decision(
            assessment
        )

        action = build_position_action(
            normalized_request,
            assessment,
            decision,
        )

        result = build_position_result(
            assessment,
            action,
            decision,
        )

        return build_position_contract(
            normalized_request,
            assessment,
            result,
        )

    def check(
        self,
        request: PositionRequest | Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> PositionResult:

        contract = self.evaluate(
            request,
            **kwargs,
        )

        return contract.result

    def review(
        self,
        request: PositionRequest | Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> PositionContract:

        return self.evaluate(
            request,
            **kwargs,
        )


# ============================================================
# SINGLETON ACCESS
# ============================================================

def get_position_gate_engine() -> PositionGateEngine:
    return PositionGateEngine()


# ============================================================
# PUBLIC EVALUATION HELPERS
# ============================================================

def evaluate_position(
    request: PositionRequest | Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> PositionContract:

    return get_position_gate_engine().evaluate(
        request,
        **kwargs,
    )


def check_position(
    request: PositionRequest | Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> PositionResult:

    return get_position_gate_engine().check(
        request,
        **kwargs,
    )


def review_position(
    request: PositionRequest | Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> PositionContract:

    return get_position_gate_engine().review(
        request,
        **kwargs,
    )
# ============================================================
# POSITION GATE — PART 4
# Validation • Readiness • Safety • Authority • Audit • Health
# ============================================================


# ============================================================
# ACTION / RESULT / CONTRACT VALIDATION
# ============================================================

def validate_position_action(
    action: PositionAction,
) -> bool:
    """Strict structural validation for PositionAction."""

    if not isinstance(action, PositionAction):
        return False

    if not action.action:
        return False

    if not isinstance(
        action.action_state,
        PositionActionState,
    ):
        return False

    if not isinstance(
        action.decision,
        PositionDecision,
    ):
        return False

    if not isinstance(
        action.status,
        PositionStatus,
    ):
        return False

    if action.restrictions is None:
        return False

    if action.flags is None:
        return False

    return True


def validate_position_result(
    result: PositionResult,
) -> bool:
    """Strict structural validation for PositionResult."""

    if not isinstance(result, PositionResult):
        return False

    if not isinstance(
        result.result_status,
        PositionResultStatus,
    ):
        return False

    if not isinstance(
        result.status,
        PositionStatus,
    ):
        return False

    if not isinstance(
        result.decision,
        PositionDecision,
    ):
        return False

    if result.action is None:
        return False

    if result.assessment is None:
        return False

    return validate_position_action(
        result.action
    )


def validate_position_contract(
    contract: PositionContract,
) -> bool:
    """Strict structural validation for PositionContract."""

    if not isinstance(contract, PositionContract):
        return False

    if not isinstance(
        contract.contract_status,
        PositionContractStatus,
    ):
        return False

    if contract.request is None:
        return False

    if contract.assessment is None:
        return False

    if contract.result is None:
        return False

    return validate_position_result(
        contract.result
    )


# ============================================================
# READINESS / SAFETY
# ============================================================

def position_ready(
    contract_or_result,
) -> bool:
    """
    True when Position Gate has a structurally valid and
    usable result/contract.
    """

    if isinstance(contract_or_result, PositionContract):

        if not validate_position_contract(
            contract_or_result
        ):
            return False

        return contract_or_result.contract_status in (
            PositionContractStatus.VALID,
            PositionContractStatus.ACTIVE,
            PositionContractStatus.RESTRICTED,
            PositionContractStatus.COMPLETE,
        )

    if isinstance(contract_or_result, PositionResult):

        if not validate_position_result(
            contract_or_result
        ):
            return False

        return contract_or_result.result_status not in (
            PositionResultStatus.INVALID,
            PositionResultStatus.ERROR,
        )

    return False


def position_can_advance(
    result: PositionResult,
) -> bool:
    """
    Position Gate may advance only when the position pathway
    is allowed, either normally or with explicit restrictions.
    """

    if not validate_position_result(result):
        return False

    return result.decision in (
        PositionDecision.ALLOW,
        PositionDecision.ALLOW_WITH_RESTRICTION,
    )


def position_requires_review(
    result: PositionResult,
) -> bool:

    if not validate_position_result(result):
        return True

    return (
        result.decision
        == PositionDecision.REVIEW_REQUIRED
    )


def position_is_blocked(
    result: PositionResult,
) -> bool:

    if not validate_position_result(result):
        return True

    return (
        result.decision
        == PositionDecision.BLOCK
    )


def position_is_restricted(
    result: PositionResult,
) -> bool:

    if not validate_position_result(result):
        return False

    return (
        result.decision
        == PositionDecision.ALLOW_WITH_RESTRICTION
    )


def position_is_safe_for_next_gate(
    result: PositionResult,
) -> bool:
    """
    Safe for next CAS layer means that Position Gate has not
    identified a blocking position-state condition.
    """

    if not validate_position_result(result):
        return False

    return result.decision in (
        PositionDecision.ALLOW,
        PositionDecision.ALLOW_WITH_RESTRICTION,
    )


# ============================================================
# ACCESSORS
# ============================================================

def get_position_status(
    result: PositionResult,
):
    if not validate_position_result(result):
        return None

    return result.status


def get_position_decision(
    result: PositionResult,
):
    if not validate_position_result(result):
        return None

    return result.decision


def get_position_action_state(
    result: PositionResult,
):
    if not validate_position_result(result):
        return None

    return result.action.action_state


# ============================================================
# AUTHORITY BOUNDARIES
# ============================================================

def position_generates_market_decision() -> bool:
    return False


def position_generates_alpha() -> bool:
    return False


def position_modifies_d13() -> bool:
    return False


def position_overrides_d13() -> bool:
    return False


def position_replaces_risk_authority() -> bool:
    return False


def position_overrides_risk_authority() -> bool:
    return False


def position_overrides_cas() -> bool:
    return False


def position_authorizes_execution() -> bool:
    return False


def position_places_orders() -> bool:
    return False


def position_changes_position() -> bool:
    return False


def position_has_execution_authority() -> bool:
    return False


def position_has_market_decision_authority() -> bool:
    return False


def position_is_alpha_engine() -> bool:
    return False


def position_authority_integrity_ok() -> bool:
    """
    Position Gate is a position-state control layer only.
    """

    boundaries = (
        position_generates_market_decision(),
        position_generates_alpha(),
        position_modifies_d13(),
        position_overrides_d13(),
        position_replaces_risk_authority(),
        position_overrides_risk_authority(),
        position_overrides_cas(),
        position_authorizes_execution(),
        position_places_orders(),
        position_changes_position(),
        position_has_execution_authority(),
        position_has_market_decision_authority(),
        position_is_alpha_engine(),
    )

    return not any(boundaries)


def position_has_authority_conflict() -> bool:
    return not position_authority_integrity_ok()


# ============================================================
# AUDIT
# ============================================================

@dataclass(frozen=True)
class PositionAuditRecord:
    request_id: str

    engine: str
    version: str

    decision: str
    status: str
    action_state: str

    position_score: float
    position_confidence: float

    current_position: float
    proposed_position: float
    projected_position: float
    position_change: float

    flags: tuple[str, ...]
    restrictions: tuple[str, ...]

    authority_integrity: bool
    timestamp: str


def build_position_audit(
    result: PositionResult,
    request_id: str = "",
) -> PositionAuditRecord:
    """
    Immutable audit representation of a Position Gate result.
    """

    assessment = result.assessment

    return PositionAuditRecord(
        request_id=request_id,

        engine=POSITION_GATE_ENGINE,
        version=POSITION_GATE_VERSION,

        decision=str(result.decision),
        status=str(result.status),
        action_state=str(
            result.action.action_state
        ),

        position_score=float(
            assessment.position_score
        ),

        position_confidence=float(
            assessment.position_confidence
        ),

        current_position=float(
            assessment.current_position
        ),

        proposed_position=float(
            assessment.proposed_position
        ),

        projected_position=float(
            assessment.projected_position
        ),

        position_change=float(
            assessment.position_change
        ),

        flags=tuple(
            assessment.flags or ()
        ),

        restrictions=tuple(
            assessment.restrictions or ()
        ),

        authority_integrity=(
            position_authority_integrity_ok()
        ),

        timestamp=_pg_timestamp(),
    )


# ============================================================
# ENGINE HEALTH
# ============================================================

@dataclass(frozen=True)
class PositionEngineHealth:
    engine: str
    version: str

    operational: bool
    authority_integrity: bool

    validation_available: bool
    assessment_available: bool
    decision_available: bool
    audit_available: bool

    status: str


def get_position_engine_health() -> PositionEngineHealth:
    """
    Structural runtime health check.

    No market decision, D13 modification, execution, or
    position mutation occurs here.
    """

    validation_ok = all(
        callable(fn)
        for fn in (
            validate_position_request,
            validate_position_action,
            validate_position_result,
            validate_position_contract,
        )
    )

    assessment_ok = all(
        callable(fn)
        for fn in (
            evaluate_position_data_state,
            evaluate_position_consistency,
            calculate_position_completeness,
            evaluate_position_readiness,
            evaluate_position_requirements,
            build_position_assessment,
        )
    )

    decision_ok = all(
        callable(fn)
        for fn in (
            determine_position_result_status,
            determine_position_status,
            determine_position_action_state,
            determine_position_decision,
            build_position_action,
            build_position_result,
            build_position_contract,
        )
    )

    audit_ok = callable(
        build_position_audit
    )

    authority_ok = (
        position_authority_integrity_ok()
    )

    operational = all(
        (
            validation_ok,
            assessment_ok,
            decision_ok,
            audit_ok,
            authority_ok,
        )
    )

    return PositionEngineHealth(
        engine=POSITION_GATE_ENGINE,
        version=POSITION_GATE_VERSION,

        operational=operational,
        authority_integrity=authority_ok,

        validation_available=validation_ok,
        assessment_available=assessment_ok,
        decision_available=decision_ok,
        audit_available=audit_ok,

        status=(
            "OPERATIONAL"
            if operational
            else "DEGRADED"
        ),
    )


def get_position_engine_info() -> dict:
    """
    Static identity and authority contract.
    """

    return {
        "engine": POSITION_GATE_ENGINE,
        "version": POSITION_GATE_VERSION,

        "role": "CAS_POSITION_CONTROL",
        "authority": "POSITION_STATE_CONTROL_ONLY",

        "generates_market_decision": False,
        "generates_alpha": False,

        "modifies_d13": False,
        "overrides_d13": False,

        "replaces_risk_authority": False,
        "overrides_risk_authority": False,

        "overrides_cas": False,

        "authorizes_execution": False,
        "places_orders": False,
        "changes_position": False,

        "has_execution_authority": False,
        "has_market_decision_authority": False,

        "is_alpha_engine": False,

        "authority_integrity": (
            position_authority_integrity_ok()
        ),
    }


def position_integrity_ok(
    contract: Optional[PositionContract] = None,
) -> bool:
    """
    Complete Position Gate integrity check.
    """

    if not position_authority_integrity_ok():
        return False

    health = get_position_engine_health()

    if not health.operational:
        return False

    if contract is not None:
        if not validate_position_contract(
            contract
        ):
            return False

    return True
# ============================================================
# POSITION GATE — PART 5/5
# Lifecycle, Serialization, Validation, Snapshot, Public API
# ============================================================

class PositionLifecycleState(str, Enum):
    CREATED = "CREATED"
    VALIDATING = "VALIDATING"
    ASSESSED = "ASSESSED"
    DECIDED = "DECIDED"
    ACTIVE = "ACTIVE"
    RESTRICTED = "RESTRICTED"
    REVIEW = "REVIEW"
    BLOCKED = "BLOCKED"
    FROZEN = "FROZEN"
    RETAINED = "RETAINED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"


def determine_position_lifecycle(
    contract: PositionContract,
) -> PositionLifecycleState:
    if not validate_position_contract(contract):
        return PositionLifecycleState.REJECTED

    if contract.result is None:
        return PositionLifecycleState.CREATED

    decision = contract.result.decision

    if decision == PositionDecision.BLOCK:
        return PositionLifecycleState.BLOCKED

    if decision == PositionDecision.REVIEW_REQUIRED:
        return PositionLifecycleState.REVIEW

    if decision == PositionDecision.ALLOW_WITH_RESTRICTION:
        return PositionLifecycleState.RESTRICTED

    if decision == PositionDecision.ALLOW:
        if contract.result.action_state == PositionActionState.AUTHORIZED:
            return PositionLifecycleState.ACTIVE
        return PositionLifecycleState.DECIDED

    return PositionLifecycleState.COMPLETED


def freeze_position(contract: PositionContract) -> PositionLifecycleState:
    return PositionLifecycleState.FROZEN


def retain_position(contract: PositionContract) -> PositionLifecycleState:
    return PositionLifecycleState.RETAINED


def reject_position(contract: PositionContract) -> PositionLifecycleState:
    return PositionLifecycleState.REJECTED


# ------------------------------------------------------------
# SERIALIZATION
# ------------------------------------------------------------

def position_request_to_dict(
    request: PositionRequest,
) -> dict:
    return {
        "market": request.market,
        "instrument": request.instrument,
        "contract": request.contract,
        "user_id": request.user_id,
        "account_id": request.account_id,
        "plan_id": request.plan_id,
        "action": request.action,
        "direction": request.direction,
        "mode": request.mode.value
        if isinstance(request.mode, Enum)
        else request.mode,
        "strategy": request.strategy,
        "timeframe": request.timeframe,
        "priority": request.priority.value
        if isinstance(request.priority, Enum)
        else request.priority,
        "current_position": request.current_position,
        "current_position_side": request.current_position_side,
        "current_position_value": request.current_position_value,
        "proposed_position": request.proposed_position,
        "proposed_position_change": request.proposed_position_change,
        "proposed_position_value": request.proposed_position_value,
        "max_position": request.max_position,
        "min_position": request.min_position,
        "quantity": request.quantity,
        "price": request.price,
        "reduce_only": request.reduce_only,
        "close_only": request.close_only,
        "allow_new_position": request.allow_new_position,
        "allow_add_to_position": request.allow_add_to_position,
        "position_open": request.position_open,
        "position_closing": request.position_closing,
        "position_locked": request.position_locked,
        "metadata": dict(request.metadata or {}),
        "request_id": request.request_id,
        "timestamp": request.timestamp,
    }


def position_assessment_to_dict(
    assessment: PositionAssessment,
) -> dict:
    return {
        "data_state": assessment.data_state.value
        if isinstance(assessment.data_state, Enum)
        else assessment.data_state,
        "consistency": assessment.consistency.value
        if isinstance(assessment.consistency, Enum)
        else assessment.consistency,
        "readiness": assessment.readiness.value
        if isinstance(assessment.readiness, Enum)
        else assessment.readiness,
        "completeness": assessment.completeness,
        "score": assessment.position_score,
        "position_score": assessment.position_score,
        "confidence": assessment.position_confidence,
        "position_confidence": assessment.position_confidence,
        "requirements_met": assessment.requirements_met,
        "flags": list(assessment.flags or []),
        "restrictions": list(assessment.restrictions or []),
    }


def position_result_to_dict(
    result: PositionResult,
) -> dict:
    return {
        "status": result.status.value
        if isinstance(result.status, Enum)
        else result.status,
        "decision": result.decision.value
        if isinstance(result.decision, Enum)
        else result.decision,
        "action_state": result.action_state.value
        if isinstance(result.action_state, Enum)
        else result.action_state,
        "message": result.message,
        "flags": list(result.flags or []),
        "restrictions": list(result.restrictions or []),
        "position_score": result.position_score,
        "position_confidence": result.position_confidence,
        "can_advance": result.can_advance,
        "requires_review": result.requires_review,
        "blocked": result.blocked,
        "restricted": result.restricted,
        "safe_for_next_gate": result.safe_for_next_gate,
        "timestamp": result.timestamp,
    }


def position_contract_to_dict(
    contract: PositionContract,
) -> dict:
    return {
        "engine": POSITION_GATE_ENGINE,
        "version": POSITION_GATE_VERSION,
        "contract_status": contract.contract_status.value
        if isinstance(contract.contract_status, Enum)
        else contract.contract_status,
        "request": position_request_to_dict(contract.request),
        "assessment": (
            position_assessment_to_dict(contract.assessment)
            if contract.assessment is not None
            else None
        ),
        "result": (
            position_result_to_dict(contract.result)
            if contract.result is not None
            else None
        ),
        "audit": (
            contract.audit.__dict__
            if getattr(contract, "audit", None) is not None
            else None
        ),
        "lifecycle": determine_position_lifecycle(contract).value,
    }


# ------------------------------------------------------------
# SUMMARY
# ------------------------------------------------------------

def summarize_position(
    contract: PositionContract,
) -> dict:
    assessment = contract.assessment
    result = contract.result

    return {
        "valid": validate_position_contract(contract),
        "engine": POSITION_GATE_ENGINE,
        "version": POSITION_GATE_VERSION,
        "contract_status": (
            contract.contract_status.value
            if isinstance(contract.contract_status, Enum)
            else contract.contract_status
        ),
        "lifecycle": determine_position_lifecycle(contract).value,

        "status": (
            result.status.value
            if result and isinstance(result.status, Enum)
            else getattr(result, "status", None)
        ),
        "decision": (
            result.decision.value
            if result and isinstance(result.decision, Enum)
            else getattr(result, "decision", None)
        ),
        "action_state": (
            result.action_state.value
            if result and isinstance(result.action_state, Enum)
            else getattr(result, "action_state", None)
        ),

        "position_score": (
            assessment.position_score
            if assessment is not None
            else None
        ),
        "position_confidence": (
            assessment.position_confidence
            if assessment is not None
            else None
        ),

        "current_position": contract.request.current_position,
        "proposed_position": contract.request.proposed_position,
        "proposed_position_change": (
            contract.request.proposed_position_change
        ),
        "current_position_value": (
            contract.request.current_position_value
        ),
        "proposed_position_value": (
            contract.request.proposed_position_value
        ),

        "flags": (
            list(assessment.flags or [])
            if assessment is not None
            else []
        ),
        "restrictions": (
            list(assessment.restrictions or [])
            if assessment is not None
            else []
        ),

        "can_advance": (
            position_can_advance(contract)
            if result is not None
            else False
        ),
        "requires_review": (
            position_requires_review(contract)
            if result is not None
            else False
        ),
        "blocked": (
            position_is_blocked(contract)
            if result is not None
            else False
        ),
        "restricted": (
            position_is_restricted(contract)
            if result is not None
            else False
        ),
        "safe_for_next_gate": (
            position_is_safe_for_next_gate(contract)
            if result is not None
            else False
        ),

        "authority_integrity": position_authority_integrity_ok(),
    }


# ------------------------------------------------------------
# AUTHORITY STATEMENT
# ------------------------------------------------------------

def get_position_authority_statement() -> dict:
    return {
        "authority": "POSITION_STATE_CONTROL",
        "role": (
            "Evaluate whether the proposed action is compatible "
            "with the current and permitted position state."
        ),
        "generates_market_decision": False,
        "generates_alpha": False,
        "modifies_d13": False,
        "overrides_d13": False,
        "replaces_risk_authority": False,
        "overrides_risk_authority": False,
        "overrides_cas": False,
        "authorizes_execution": False,
        "places_orders": False,
        "changes_position": False,
        "has_execution_authority": False,
        "has_market_decision_authority": False,
        "is_alpha_engine": False,
    }


# ------------------------------------------------------------
# OPERATIONAL HEALTH
# ------------------------------------------------------------

def position_engine_operational() -> bool:
    health = get_position_engine_health()
    return bool(
        getattr(health, "operational", False)
        and position_authority_integrity_ok()
    )


# ------------------------------------------------------------
# COMPLETE CONTRACT VALIDATION
# ------------------------------------------------------------

def validate_position(
    contract: PositionContract,
) -> bool:
    if not validate_position_contract(contract):
        return False

    if not position_authority_integrity_ok():
        return False

    if not position_engine_operational():
        return False

    if contract.assessment is not None:
        if not validate_position_result(contract.result):
            return False

    if contract.result is not None:
        if not validate_position_result(contract.result):
            return False

    return True


# ------------------------------------------------------------
# SNAPSHOT
# ------------------------------------------------------------

def position_snapshot(
    contract: Optional[PositionContract] = None,
) -> dict:
    health = get_position_engine_health()

    snapshot = {
        "engine": POSITION_GATE_ENGINE,
        "version": POSITION_GATE_VERSION,
        "operational": position_engine_operational(),
        "health": (
            health.__dict__
            if hasattr(health, "__dict__")
            else health
        ),
        "authority": get_position_authority_statement(),
        "authority_integrity": position_authority_integrity_ok(),
    }

    if contract is not None:
        snapshot["valid"] = validate_position(contract)
        snapshot["lifecycle"] = determine_position_lifecycle(
            contract
        ).value
        snapshot["summary"] = summarize_position(contract)

    return snapshot


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    # Constants
    "POSITION_GATE_ENGINE",
    "POSITION_GATE_VERSION",

    # Enums
    "PositionStatus",
    "PositionDecision",
    "PositionMode",
    "PositionPriority",
    "PositionContractStatus",
    "PositionDataState",
    "PositionConsistency",
    "PositionReadiness",
    "PositionActionState",
    "PositionContractState",
    "PositionResultStatus",
    "PositionLifecycleState",

    # Contracts / Models
    "PositionRequest",
    "PositionReference",
    "PositionContractValidation",
    "PositionRequirements",
    "PositionAssessment",
    "PositionAction",
    "PositionResult",
    "PositionContract",
    "PositionAuditRecord",
    "PositionEngineHealth",

    # Builders / Validation
    "build_position_request",
    "validate_position_numeric_inputs",
    "validate_position_request",
    "build_position_assessment",
    "build_position_action",
    "build_position_result",
    "build_position_contract",
    "validate_position_action",
    "validate_position_result",
    "validate_position_contract",
    "validate_position",

    # Evaluation
    "evaluate_position_data_state",
    "evaluate_position_consistency",
    "calculate_position_completeness",
    "evaluate_position_readiness",
    "evaluate_position_requirements",
    "extract_position_flags",
    "extract_position_restrictions",
    "calculate_position_score",
    "calculate_position_confidence",
    "determine_position_result_status",
    "determine_position_status",
    "determine_position_action_state",
    "determine_position_decision",

    # Engine
    "PositionGateEngine",
    "get_position_gate_engine",
    "evaluate_position",
    "check_position",
    "review_position",

    # Readiness / Safety
    "position_ready",
    "position_can_advance",
    "position_requires_review",
    "position_is_blocked",
    "position_is_restricted",
    "position_is_safe_for_next_gate",

    # Accessors
    "get_position_status",
    "get_position_decision",
    "get_position_action_state",

    # Authority
    "position_generates_market_decision",
    "position_generates_alpha",
    "position_modifies_d13",
    "position_overrides_d13",
    "position_replaces_risk_authority",
    "position_overrides_risk_authority",
    "position_overrides_cas",
    "position_authorizes_execution",
    "position_places_orders",
    "position_changes_position",
    "position_has_execution_authority",
    "position_has_market_decision_authority",
    "position_is_alpha_engine",
    "position_authority_integrity_ok",
    "position_has_authority_conflict",

    # Audit / Health
    "build_position_audit",
    "get_position_engine_health",
    "get_position_engine_info",
    "position_integrity_ok",

    # Lifecycle
    "determine_position_lifecycle",
    "freeze_position",
    "retain_position",
    "reject_position",

    # Serialization / Summary
    "position_request_to_dict",
    "position_assessment_to_dict",
    "position_result_to_dict",
    "position_contract_to_dict",
    "summarize_position",
    "get_position_authority_statement",

    # Operational
    "position_engine_operational",
    "position_snapshot",
]