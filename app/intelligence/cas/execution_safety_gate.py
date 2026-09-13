# ============================================================
# ROBOMLM CAS — EXECUTION SAFETY GATE
# PART 1/5
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Mapping, Optional


# ============================================================
# ENGINE IDENTITY
# ============================================================

EXECUTION_SAFETY_GATE_ENGINE = "ROBOMLM_CAS_EXECUTION_SAFETY_GATE"
EXECUTION_SAFETY_GATE_VERSION = "1.0"


# ============================================================
# ENUMS
# ============================================================

class ExecutionSafetyStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    SAFE = "SAFE"
    CONDITIONAL = "CONDITIONAL"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    UNSAFE = "UNSAFE"
    BLOCKED = "BLOCKED"


class ExecutionSafetyDecision(str, Enum):
    ALLOW = "ALLOW"
    ALLOW_WITH_RESTRICTION = "ALLOW_WITH_RESTRICTION"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCK = "BLOCK"


class ExecutionSafetyMode(str, Enum):
    PAPER = "PAPER"
    DEMO = "DEMO"
    LIVE = "LIVE"
    UNKNOWN = "UNKNOWN"


class ExecutionSafetyPriority(str, Enum):
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ExecutionSafetyContractStatus(str, Enum):
    CREATED = "CREATED"
    VALID = "VALID"
    INVALID = "INVALID"
    READY = "READY"
    RESTRICTED = "RESTRICTED"
    REVIEW = "REVIEW"
    BLOCKED = "BLOCKED"


# ============================================================
# REQUEST CONTRACT
# ============================================================

@dataclass(frozen=True)
class ExecutionSafetyRequest:
    market: Optional[str] = None
    instrument: Optional[str] = None
    contract: Optional[str] = None

    user_id: Optional[str] = None
    account_id: Optional[str] = None
    plan_id: Optional[str] = None

    action: Optional[str] = None
    direction: Optional[str] = None

    mode: ExecutionSafetyMode = ExecutionSafetyMode.UNKNOWN
    strategy: Optional[str] = None
    timeframe: Optional[str] = None
    priority: ExecutionSafetyPriority = ExecutionSafetyPriority.NORMAL

    # Execution environment
    broker: Optional[str] = None
    venue: Optional[str] = None
    execution_channel: Optional[str] = None

    # Order intent
    order_type: Optional[str] = None
    quantity: Optional[float] = None
    price: Optional[float] = None
    stop_price: Optional[float] = None
    limit_price: Optional[float] = None

    # Execution controls
    reduce_only: bool = False
    close_only: bool = False
    post_only: bool = False

    # Safety conditions
    market_open: Optional[bool] = None
    trading_halted: Optional[bool] = None
    kill_switch_active: Optional[bool] = None
    execution_enabled: Optional[bool] = None

    # Market execution quality
    liquidity_ok: Optional[bool] = None
    slippage_ok: Optional[bool] = None
    spread_ok: Optional[bool] = None
    latency_ok: Optional[bool] = None
    price_valid: Optional[bool] = None

    # Operational readiness
    broker_connected: Optional[bool] = None
    venue_available: Optional[bool] = None
    order_channel_ready: Optional[bool] = None

    # Optional metadata
    metadata: Mapping[str, Any] = field(default_factory=dict)

    request_id: Optional[str] = None
    timestamp: Optional[str] = None


@dataclass(frozen=True)
class ExecutionSafetyReference:
    reference_id: Optional[str] = None
    source: Optional[str] = None
    source_version: Optional[str] = None
    value: Any = None
    timestamp: Optional[str] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionSafetyContractValidation:
    valid: bool
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    checked_at: str = ""


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _esg_read_value(
    source: Any,
    name: str,
    default: Any = None,
) -> Any:
    if source is None:
        return default

    if isinstance(source, Mapping):
        return source.get(name, default)

    return getattr(source, name, default)


def _esg_text(value: Any) -> Optional[str]:
    if value is None:
        return None

    text = str(value).strip()
    return text if text else None


def _esg_enum(
    value: Any,
    enum_cls: type[Enum],
    default: Enum,
) -> Enum:
    if value is None:
        return default

    if isinstance(value, enum_cls):
        return value

    try:
        return enum_cls(str(value).upper())
    except (ValueError, TypeError):
        return default


def _esg_number(value: Any) -> Optional[float]:
    if value is None:
        return None

    if isinstance(value, bool):
        return None

    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    if number != number:
        return None

    return number


def _esg_bool(value: Any) -> Optional[bool]:
    if value is None:
        return None

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        text = value.strip().lower()

        if text in {"true", "1", "yes", "y", "on"}:
            return True

        if text in {"false", "0", "no", "n", "off"}:
            return False

    return bool(value)


def _esg_timestamp(value: Any = None) -> str:
    if value:
        return str(value)

    return datetime.now(timezone.utc).isoformat()


# ============================================================
# REQUEST BUILDER
# ============================================================

def build_execution_safety_request(
    source: Any = None,
    **overrides: Any,
) -> ExecutionSafetyRequest:
    def value(name: str, default: Any = None) -> Any:
        if name in overrides:
            return overrides[name]

        return _esg_read_value(source, name, default)

    return ExecutionSafetyRequest(
        market=_esg_text(value("market")),
        instrument=_esg_text(value("instrument")),
        contract=_esg_text(value("contract")),

        user_id=_esg_text(value("user_id")),
        account_id=_esg_text(value("account_id")),
        plan_id=_esg_text(value("plan_id")),

        action=_esg_text(value("action")),
        direction=_esg_text(value("direction")),

        mode=_esg_enum(
            value("mode"),
            ExecutionSafetyMode,
            ExecutionSafetyMode.UNKNOWN,
        ),

        strategy=_esg_text(value("strategy")),
        timeframe=_esg_text(value("timeframe")),

        priority=_esg_enum(
            value("priority"),
            ExecutionSafetyPriority,
            ExecutionSafetyPriority.NORMAL,
        ),

        broker=_esg_text(value("broker")),
        venue=_esg_text(value("venue")),
        execution_channel=_esg_text(
            value("execution_channel")
        ),

        order_type=_esg_text(value("order_type")),

        quantity=_esg_number(value("quantity")),
        price=_esg_number(value("price")),
        stop_price=_esg_number(value("stop_price")),
        limit_price=_esg_number(value("limit_price")),

        reduce_only=bool(
            _esg_bool(value("reduce_only")) or False
        ),
        close_only=bool(
            _esg_bool(value("close_only")) or False
        ),
        post_only=bool(
            _esg_bool(value("post_only")) or False
        ),

        market_open=_esg_bool(value("market_open")),
        trading_halted=_esg_bool(
            value("trading_halted")
        ),
        kill_switch_active=_esg_bool(
            value("kill_switch_active")
        ),
        execution_enabled=_esg_bool(
            value("execution_enabled")
        ),

        liquidity_ok=_esg_bool(value("liquidity_ok")),
        slippage_ok=_esg_bool(value("slippage_ok")),
        spread_ok=_esg_bool(value("spread_ok")),
        latency_ok=_esg_bool(value("latency_ok")),
        price_valid=_esg_bool(value("price_valid")),

        broker_connected=_esg_bool(
            value("broker_connected")
        ),
        venue_available=_esg_bool(
            value("venue_available")
        ),
        order_channel_ready=_esg_bool(
            value("order_channel_ready")
        ),

        metadata=dict(value("metadata", {}) or {}),

        request_id=_esg_text(value("request_id")),
        timestamp=_esg_timestamp(value("timestamp")),
    )


# ============================================================
# NUMERIC VALIDATION
# ============================================================

def validate_execution_safety_numeric_inputs(
    request: ExecutionSafetyRequest,
) -> tuple[str, ...]:
    errors: list[str] = []

    numeric_fields = {
        "quantity": request.quantity,
        "price": request.price,
        "stop_price": request.stop_price,
        "limit_price": request.limit_price,
    }

    for name, value in numeric_fields.items():
        if value is not None:
            if not isinstance(value, (int, float)):
                errors.append(f"{name.upper()}_NOT_NUMERIC")
                continue

            if isinstance(value, bool):
                errors.append(f"{name.upper()}_INVALID")

            if float(value) != float(value):
                errors.append(f"{name.upper()}_NAN")

    if request.quantity is not None and request.quantity <= 0:
        errors.append("QUANTITY_NON_POSITIVE")

    if request.price is not None and request.price <= 0:
        errors.append("PRICE_NON_POSITIVE")

    if request.stop_price is not None and request.stop_price <= 0:
        errors.append("STOP_PRICE_NON_POSITIVE")

    if request.limit_price is not None and request.limit_price <= 0:
        errors.append("LIMIT_PRICE_NON_POSITIVE")

    return tuple(errors)


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_execution_safety_request(
    request: ExecutionSafetyRequest,
) -> ExecutionSafetyContractValidation:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(request, ExecutionSafetyRequest):
        return ExecutionSafetyContractValidation(
            valid=False,
            errors=("INVALID_REQUEST_TYPE",),
            checked_at=_esg_timestamp(),
        )

    if not request.market:
        errors.append("MARKET_MISSING")

    if not request.instrument:
        errors.append("INSTRUMENT_MISSING")

    if not request.action:
        errors.append("ACTION_MISSING")

    if not request.direction:
        warnings.append("DIRECTION_MISSING")

    if request.mode == ExecutionSafetyMode.UNKNOWN:
        warnings.append("MODE_UNKNOWN")

    if not request.order_type:
        errors.append("ORDER_TYPE_MISSING")

    numeric_errors = validate_execution_safety_numeric_inputs(
        request
    )
    errors.extend(numeric_errors)

    if request.kill_switch_active is True:
        errors.append("KILL_SWITCH_ACTIVE")

    if request.trading_halted is True:
        errors.append("TRADING_HALTED")

    if request.execution_enabled is False:
        errors.append("EXECUTION_DISABLED")

    return ExecutionSafetyContractValidation(
        valid=not errors,
        errors=tuple(dict.fromkeys(errors)),
        warnings=tuple(dict.fromkeys(warnings)),
        checked_at=_esg_timestamp(),
    )


# ============================================================
# PART 1 COMPLETE
# ============================================================
# ============================================================
# ROBOMLM CAS — EXECUTION SAFETY GATE
# PART 2/5
# Data State, Consistency, Readiness, Requirements, Assessment
# ============================================================


# ============================================================
# ENUMS — DATA / READINESS
# ============================================================

class ExecutionSafetyDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    INVALID = "INVALID"


class ExecutionSafetyConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONDITIONAL = "CONDITIONAL"
    INCONSISTENT = "INCONSISTENT"
    UNKNOWN = "UNKNOWN"


class ExecutionSafetyReadiness(str, Enum):
    READY = "READY"
    CONDITIONALLY_READY = "CONDITIONALLY_READY"
    NOT_READY = "NOT_READY"
    BLOCKED = "BLOCKED"


# ============================================================
# REQUIREMENTS
# ============================================================

@dataclass(frozen=True)
class ExecutionSafetyRequirements:
    market_required: bool = True
    instrument_required: bool = True
    action_required: bool = True
    order_type_required: bool = True

    broker_required: bool = True
    venue_required: bool = True
    execution_channel_required: bool = True

    quantity_required: bool = True
    price_required: bool = True

    market_open_required: bool = True
    execution_enabled_required: bool = True

    broker_connected_required: bool = True
    venue_available_required: bool = True
    order_channel_ready_required: bool = True

    liquidity_required: bool = True
    slippage_required: bool = True
    spread_required: bool = True
    latency_required: bool = True
    price_valid_required: bool = True


# ============================================================
# ASSESSMENT CONTRACT
# ============================================================

@dataclass(frozen=True)
class ExecutionSafetyAssessment:
    data_state: ExecutionSafetyDataState
    consistency: ExecutionSafetyConsistency
    readiness: ExecutionSafetyReadiness

    completeness: float
    execution_safety_score: float
    execution_safety_confidence: float

    requirements_met: bool

    flags: tuple[str, ...] = ()
    restrictions: tuple[str, ...] = ()

    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


# ============================================================
# DATA STATE
# ============================================================

def evaluate_execution_safety_data_state(
    request: ExecutionSafetyRequest,
) -> ExecutionSafetyDataState:
    validation = validate_execution_safety_request(request)

    if not validation.valid:
        return ExecutionSafetyDataState.INVALID

    required_values = [
        request.market,
        request.instrument,
        request.action,
        request.order_type,
        request.broker,
        request.venue,
        request.execution_channel,
        request.quantity,
        request.price,
        request.market_open,
        request.execution_enabled,
        request.broker_connected,
        request.venue_available,
        request.order_channel_ready,
        request.liquidity_ok,
        request.slippage_ok,
        request.spread_ok,
        request.latency_ok,
        request.price_valid,
    ]

    present = sum(
        value is not None
        for value in required_values
    )

    total = len(required_values)

    if present == 0:
        return ExecutionSafetyDataState.MISSING

    if present < total:
        return ExecutionSafetyDataState.PARTIAL

    return ExecutionSafetyDataState.COMPLETE


# ============================================================
# CONSISTENCY
# ============================================================

def evaluate_execution_safety_consistency(
    request: ExecutionSafetyRequest,
) -> ExecutionSafetyConsistency:
    if request.kill_switch_active is True:
        return ExecutionSafetyConsistency.INCONSISTENT

    if request.trading_halted is True:
        return ExecutionSafetyConsistency.INCONSISTENT

    if request.execution_enabled is False:
        return ExecutionSafetyConsistency.INCONSISTENT

    if (
        request.broker_connected is False
        or request.venue_available is False
        or request.order_channel_ready is False
    ):
        return ExecutionSafetyConsistency.INCONSISTENT

    if request.price_valid is False:
        return ExecutionSafetyConsistency.INCONSISTENT

    if (
        request.market_open is False
        and not request.reduce_only
        and not request.close_only
    ):
        return ExecutionSafetyConsistency.INCONSISTENT

    conditional_checks = [
        request.liquidity_ok,
        request.slippage_ok,
        request.spread_ok,
        request.latency_ok,
    ]

    if any(value is False for value in conditional_checks):
        return ExecutionSafetyConsistency.CONDITIONAL

    if any(value is None for value in conditional_checks):
        return ExecutionSafetyConsistency.UNKNOWN

    return ExecutionSafetyConsistency.CONSISTENT


# ============================================================
# COMPLETENESS
# ============================================================

def calculate_execution_safety_completeness(
    request: ExecutionSafetyRequest,
) -> float:
    fields = [
        request.market,
        request.instrument,
        request.action,
        request.order_type,
        request.broker,
        request.venue,
        request.execution_channel,
        request.quantity,
        request.price,
        request.market_open,
        request.execution_enabled,
        request.broker_connected,
        request.venue_available,
        request.order_channel_ready,
        request.liquidity_ok,
        request.slippage_ok,
        request.spread_ok,
        request.latency_ok,
        request.price_valid,
    ]

    if not fields:
        return 0.0

    present = sum(value is not None for value in fields)

    return round(
        (present / len(fields)) * 100.0,
        4,
    )


# ============================================================
# REQUIREMENT EVALUATION
# ============================================================

def evaluate_execution_safety_requirements(
    request: ExecutionSafetyRequest,
    requirements: Optional[
        ExecutionSafetyRequirements
    ] = None,
) -> tuple[bool, tuple[str, ...]]:
    requirements = (
        requirements
        or ExecutionSafetyRequirements()
    )

    missing: list[str] = []

    checks = [
        (
            "MARKET",
            requirements.market_required,
            request.market,
        ),
        (
            "INSTRUMENT",
            requirements.instrument_required,
            request.instrument,
        ),
        (
            "ACTION",
            requirements.action_required,
            request.action,
        ),
        (
            "ORDER_TYPE",
            requirements.order_type_required,
            request.order_type,
        ),
        (
            "BROKER",
            requirements.broker_required,
            request.broker,
        ),
        (
            "VENUE",
            requirements.venue_required,
            request.venue,
        ),
        (
            "EXECUTION_CHANNEL",
            requirements.execution_channel_required,
            request.execution_channel,
        ),
        (
            "QUANTITY",
            requirements.quantity_required,
            request.quantity,
        ),
        (
            "PRICE",
            requirements.price_required,
            request.price,
        ),
        (
            "MARKET_OPEN",
            requirements.market_open_required,
            request.market_open,
        ),
        (
            "EXECUTION_ENABLED",
            requirements.execution_enabled_required,
            request.execution_enabled,
        ),
        (
            "BROKER_CONNECTED",
            requirements.broker_connected_required,
            request.broker_connected,
        ),
        (
            "VENUE_AVAILABLE",
            requirements.venue_available_required,
            request.venue_available,
        ),
        (
            "ORDER_CHANNEL_READY",
            requirements.order_channel_ready_required,
            request.order_channel_ready,
        ),
        (
            "LIQUIDITY",
            requirements.liquidity_required,
            request.liquidity_ok,
        ),
        (
            "SLIPPAGE",
            requirements.slippage_required,
            request.slippage_ok,
        ),
        (
            "SPREAD",
            requirements.spread_required,
            request.spread_ok,
        ),
        (
            "LATENCY",
            requirements.latency_required,
            request.latency_ok,
        ),
        (
            "PRICE_VALID",
            requirements.price_valid_required,
            request.price_valid,
        ),
    ]

    for name, required, value in checks:
        if required and value is None:
            missing.append(f"{name}_MISSING")

    return (
        not missing,
        tuple(dict.fromkeys(missing)),
    )


# ============================================================
# READINESS
# ============================================================

def evaluate_execution_safety_readiness(
    request: ExecutionSafetyRequest,
    requirements: Optional[
        ExecutionSafetyRequirements
    ] = None,
) -> ExecutionSafetyReadiness:
    validation = validate_execution_safety_request(request)

    if not validation.valid:
        return ExecutionSafetyReadiness.BLOCKED

    if request.kill_switch_active is True:
        return ExecutionSafetyReadiness.BLOCKED

    if request.trading_halted is True:
        return ExecutionSafetyReadiness.BLOCKED

    if request.execution_enabled is False:
        return ExecutionSafetyReadiness.BLOCKED

    requirements_met, _ = (
        evaluate_execution_safety_requirements(
            request,
            requirements,
        )
    )

    if not requirements_met:
        return ExecutionSafetyReadiness.NOT_READY

    consistency = evaluate_execution_safety_consistency(
        request
    )

    if consistency == ExecutionSafetyConsistency.INCONSISTENT:
        return ExecutionSafetyReadiness.BLOCKED

    if consistency in {
        ExecutionSafetyConsistency.CONDITIONAL,
        ExecutionSafetyConsistency.UNKNOWN,
    }:
        return ExecutionSafetyReadiness.CONDITIONALLY_READY

    return ExecutionSafetyReadiness.READY


# ============================================================
# FLAGS
# ============================================================

def extract_execution_safety_flags(
    request: ExecutionSafetyRequest,
) -> tuple[str, ...]:
    flags: list[str] = []

    if request.kill_switch_active is True:
        flags.append("KILL_SWITCH_ACTIVE")

    if request.trading_halted is True:
        flags.append("TRADING_HALTED")

    if request.execution_enabled is False:
        flags.append("EXECUTION_DISABLED")

    if request.market_open is False:
        flags.append("MARKET_CLOSED")

    if request.broker_connected is False:
        flags.append("BROKER_DISCONNECTED")

    if request.venue_available is False:
        flags.append("VENUE_UNAVAILABLE")

    if request.order_channel_ready is False:
        flags.append("ORDER_CHANNEL_NOT_READY")

    if request.liquidity_ok is False:
        flags.append("LIQUIDITY_UNSAFE")

    if request.slippage_ok is False:
        flags.append("SLIPPAGE_UNSAFE")

    if request.spread_ok is False:
        flags.append("SPREAD_UNSAFE")

    if request.latency_ok is False:
        flags.append("LATENCY_UNSAFE")

    if request.price_valid is False:
        flags.append("PRICE_INVALID")

    return tuple(dict.fromkeys(flags))


# ============================================================
# RESTRICTIONS
# ============================================================

def extract_execution_safety_restrictions(
    request: ExecutionSafetyRequest,
) -> tuple[str, ...]:
    restrictions: list[str] = []

    if request.liquidity_ok is False:
        restrictions.append("LIQUIDITY_RESTRICTED")

    if request.slippage_ok is False:
        restrictions.append("SLIPPAGE_RESTRICTED")

    if request.spread_ok is False:
        restrictions.append("SPREAD_RESTRICTED")

    if request.latency_ok is False:
        restrictions.append("LATENCY_RESTRICTED")

    if request.market_open is False:
        if request.reduce_only or request.close_only:
            restrictions.append(
                "REDUCTION_PATHWAY_ONLY"
            )
        else:
            restrictions.append(
                "MARKET_CLOSED_RESTRICTED"
            )

    if request.reduce_only:
        restrictions.append("REDUCE_ONLY")

    if request.close_only:
        restrictions.append("CLOSE_ONLY")

    if request.post_only:
        restrictions.append("POST_ONLY")

    return tuple(dict.fromkeys(restrictions))


# ============================================================
# SAFETY SCORE
# ============================================================

def calculate_execution_safety_score(
    request: ExecutionSafetyRequest,
) -> float:
    """
    Execution-safety condition score.

    This is NOT:
      - market probability
      - alpha score
      - winning probability
      - D13 confidence
      - trade expectancy
    """

    hard_fail = [
        request.kill_switch_active is True,
        request.trading_halted is True,
        request.execution_enabled is False,
        request.broker_connected is False,
        request.venue_available is False,
        request.order_channel_ready is False,
        request.price_valid is False,
    ]

    if any(hard_fail):
        return 0.0

    checks = [
        request.market_open,
        request.liquidity_ok,
        request.slippage_ok,
        request.spread_ok,
        request.latency_ok,
        request.price_valid,
        request.broker_connected,
        request.venue_available,
        request.order_channel_ready,
        request.execution_enabled,
    ]

    known = [
        value for value in checks
        if value is not None
    ]

    if not known:
        return 0.0

    positive = sum(value is True for value in known)

    return round(
        (positive / len(known)) * 100.0,
        4,
    )


# ============================================================
# CONFIDENCE
# ============================================================

def calculate_execution_safety_confidence(
    request: ExecutionSafetyRequest,
    completeness: float,
    consistency: ExecutionSafetyConsistency,
) -> float:
    confidence = completeness

    if consistency == ExecutionSafetyConsistency.CONSISTENT:
        confidence *= 1.0

    elif consistency == ExecutionSafetyConsistency.CONDITIONAL:
        confidence *= 0.75

    elif consistency == ExecutionSafetyConsistency.UNKNOWN:
        confidence *= 0.50

    else:
        confidence *= 0.0

    return round(
        max(0.0, min(100.0, confidence)),
        4,
    )


# ============================================================
# BUILD ASSESSMENT
# ============================================================

def build_execution_safety_assessment(
    request: ExecutionSafetyRequest,
    requirements: Optional[
        ExecutionSafetyRequirements
    ] = None,
) -> ExecutionSafetyAssessment:
    validation = validate_execution_safety_request(
        request
    )

    data_state = evaluate_execution_safety_data_state(
        request
    )

    consistency = evaluate_execution_safety_consistency(
        request
    )

    readiness = evaluate_execution_safety_readiness(
        request,
        requirements,
    )

    completeness = calculate_execution_safety_completeness(
        request
    )

    requirements_met, requirement_errors = (
        evaluate_execution_safety_requirements(
            request,
            requirements,
        )
    )

    flags = extract_execution_safety_flags(request)

    restrictions = (
        extract_execution_safety_restrictions(request)
    )

    score = calculate_execution_safety_score(request)

    confidence = calculate_execution_safety_confidence(
        request,
        completeness,
        consistency,
    )

    return ExecutionSafetyAssessment(
        data_state=data_state,
        consistency=consistency,
        readiness=readiness,
        completeness=completeness,
        execution_safety_score=score,
        execution_safety_confidence=confidence,
        requirements_met=requirements_met,
        flags=flags,
        restrictions=restrictions,
        errors=tuple(
            dict.fromkeys(
                validation.errors + requirement_errors
            )
        ),
        warnings=validation.warnings,
    )


# ============================================================
# PART 2 COMPLETE
# ============================================================
# ============================================================
# ROBOMLM CAS — EXECUTION SAFETY GATE
# PART 3/5
# Decision, Action, Result, Contract, Engine
# ============================================================


# ============================================================
# ACTION / CONTRACT / RESULT ENUMS
# ============================================================

class ExecutionSafetyActionState(str, Enum):
    PENDING = "PENDING"
    AUTHORIZED = "AUTHORIZED"
    RESTRICTED = "RESTRICTED"
    REVIEW = "REVIEW"
    BLOCKED = "BLOCKED"


class ExecutionSafetyContractState(str, Enum):
    CREATED = "CREATED"
    VALIDATED = "VALIDATED"
    ASSESSED = "ASSESSED"
    DECIDED = "DECIDED"
    AUTHORIZED = "AUTHORIZED"
    RESTRICTED = "RESTRICTED"
    REVIEW = "REVIEW"
    BLOCKED = "BLOCKED"
    REJECTED = "REJECTED"


class ExecutionSafetyResultStatus(str, Enum):
    ALLOWED = "ALLOWED"
    ALLOWED_WITH_RESTRICTION = "ALLOWED_WITH_RESTRICTION"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"


# ============================================================
# ACTION
# ============================================================

@dataclass(frozen=True)
class ExecutionSafetyAction:
    action: str
    state: ExecutionSafetyActionState
    allowed: bool
    restricted: bool
    requires_review: bool
    blocked: bool

    restrictions: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()

    timestamp: str = ""


# ============================================================
# RESULT
# ============================================================

@dataclass(frozen=True)
class ExecutionSafetyResult:
    status: ExecutionSafetyResultStatus
    decision: ExecutionSafetyDecision
    action_state: ExecutionSafetyActionState

    message: str

    flags: tuple[str, ...] = ()
    restrictions: tuple[str, ...] = ()

    execution_safety_score: float = 0.0
    execution_safety_confidence: float = 0.0

    can_advance: bool = False
    requires_review: bool = False
    blocked: bool = False
    restricted: bool = False
    safe_for_next_gate: bool = False

    timestamp: str = ""


# ============================================================
# CONTRACT
# ============================================================

@dataclass(frozen=True)
class ExecutionSafetyContract:
    request: ExecutionSafetyRequest
    assessment: Optional[ExecutionSafetyAssessment] = None
    action: Optional[ExecutionSafetyAction] = None
    result: Optional[ExecutionSafetyResult] = None

    contract_status: ExecutionSafetyContractStatus = (
        ExecutionSafetyContractStatus.CREATED
    )

    audit: Any = None


# ============================================================
# RESULT STATUS
# ============================================================

def determine_execution_safety_result_status(
    decision: ExecutionSafetyDecision,
) -> ExecutionSafetyResultStatus:

    mapping = {
        ExecutionSafetyDecision.ALLOW:
            ExecutionSafetyResultStatus.ALLOWED,

        ExecutionSafetyDecision.ALLOW_WITH_RESTRICTION:
            ExecutionSafetyResultStatus.ALLOWED_WITH_RESTRICTION,

        ExecutionSafetyDecision.REVIEW_REQUIRED:
            ExecutionSafetyResultStatus.REVIEW_REQUIRED,

        ExecutionSafetyDecision.BLOCK:
            ExecutionSafetyResultStatus.BLOCKED,
    }

    return mapping.get(
        decision,
        ExecutionSafetyResultStatus.REVIEW_REQUIRED,
    )


# ============================================================
# SAFETY STATUS
# ============================================================

def determine_execution_safety_status(
    assessment: ExecutionSafetyAssessment,
) -> ExecutionSafetyStatus:

    if assessment.readiness == (
        ExecutionSafetyReadiness.BLOCKED
    ):
        return ExecutionSafetyStatus.BLOCKED

    if assessment.consistency == (
        ExecutionSafetyConsistency.INCONSISTENT
    ):
        return ExecutionSafetyStatus.UNSAFE

    if assessment.readiness == (
        ExecutionSafetyReadiness.NOT_READY
    ):
        return ExecutionSafetyStatus.REVIEW_REQUIRED

    if assessment.readiness == (
        ExecutionSafetyReadiness.CONDITIONALLY_READY
    ):
        return ExecutionSafetyStatus.CONDITIONAL

    if (
        assessment.execution_safety_score >= 80
        and assessment.execution_safety_confidence >= 70
    ):
        return ExecutionSafetyStatus.SAFE

    if assessment.execution_safety_score >= 50:
        return ExecutionSafetyStatus.CONDITIONAL

    return ExecutionSafetyStatus.REVIEW_REQUIRED


# ============================================================
# DECISION
# ============================================================

def determine_execution_safety_decision(
    assessment: ExecutionSafetyAssessment,
) -> ExecutionSafetyDecision:

    if assessment.data_state == (
        ExecutionSafetyDataState.INVALID
    ):
        return ExecutionSafetyDecision.BLOCK

    if assessment.consistency == (
        ExecutionSafetyConsistency.INCONSISTENT
    ):
        return ExecutionSafetyDecision.BLOCK

    if assessment.readiness == (
        ExecutionSafetyReadiness.BLOCKED
    ):
        return ExecutionSafetyDecision.BLOCK

    if assessment.readiness == (
        ExecutionSafetyReadiness.NOT_READY
    ):
        return ExecutionSafetyDecision.REVIEW_REQUIRED

    if not assessment.requirements_met:
        return ExecutionSafetyDecision.REVIEW_REQUIRED

    if assessment.readiness == (
        ExecutionSafetyReadiness.CONDITIONALLY_READY
    ):
        return ExecutionSafetyDecision.ALLOW_WITH_RESTRICTION

    if assessment.restrictions:
        return ExecutionSafetyDecision.ALLOW_WITH_RESTRICTION

    if assessment.execution_safety_score < 50:
        return ExecutionSafetyDecision.REVIEW_REQUIRED

    return ExecutionSafetyDecision.ALLOW


# ============================================================
# ACTION STATE
# ============================================================

def determine_execution_safety_action_state(
    decision: ExecutionSafetyDecision,
) -> ExecutionSafetyActionState:

    mapping = {
        ExecutionSafetyDecision.ALLOW:
            ExecutionSafetyActionState.AUTHORIZED,

        ExecutionSafetyDecision.ALLOW_WITH_RESTRICTION:
            ExecutionSafetyActionState.RESTRICTED,

        ExecutionSafetyDecision.REVIEW_REQUIRED:
            ExecutionSafetyActionState.REVIEW,

        ExecutionSafetyDecision.BLOCK:
            ExecutionSafetyActionState.BLOCKED,
    }

    return mapping.get(
        decision,
        ExecutionSafetyActionState.REVIEW,
    )


# ============================================================
# ACTION BUILDER
# ============================================================

def build_execution_safety_action(
    request: ExecutionSafetyRequest,
    assessment: ExecutionSafetyAssessment,
    decision: ExecutionSafetyDecision,
) -> ExecutionSafetyAction:

    state = determine_execution_safety_action_state(
        decision
    )

    return ExecutionSafetyAction(
        action=request.action or "UNKNOWN",
        state=state,
        allowed=decision in {
            ExecutionSafetyDecision.ALLOW,
            ExecutionSafetyDecision.ALLOW_WITH_RESTRICTION,
        },
        restricted=(
            decision ==
            ExecutionSafetyDecision.ALLOW_WITH_RESTRICTION
        ),
        requires_review=(
            decision ==
            ExecutionSafetyDecision.REVIEW_REQUIRED
        ),
        blocked=(
            decision == ExecutionSafetyDecision.BLOCK
        ),
        restrictions=assessment.restrictions,
        reasons=(
            assessment.flags
            + assessment.errors
            + assessment.warnings
        ),
        timestamp=_esg_timestamp(),
    )


# ============================================================
# RESULT BUILDER
# ============================================================

def build_execution_safety_result(
    assessment: ExecutionSafetyAssessment,
    decision: ExecutionSafetyDecision,
) -> ExecutionSafetyResult:

    status = determine_execution_safety_result_status(
        decision
    )

    action_state = (
        determine_execution_safety_action_state(
            decision
        )
    )

    blocked = (
        decision == ExecutionSafetyDecision.BLOCK
    )

    restricted = (
        decision ==
        ExecutionSafetyDecision.ALLOW_WITH_RESTRICTION
    )

    requires_review = (
        decision ==
        ExecutionSafetyDecision.REVIEW_REQUIRED
    )

    can_advance = decision in {
        ExecutionSafetyDecision.ALLOW,
        ExecutionSafetyDecision.ALLOW_WITH_RESTRICTION,
    }

    safe_for_next_gate = (
        decision in {
            ExecutionSafetyDecision.ALLOW,
            ExecutionSafetyDecision.ALLOW_WITH_RESTRICTION,
        }
        and not blocked
    )

    if decision == ExecutionSafetyDecision.ALLOW:
        message = (
            "Execution safety conditions are acceptable "
            "for the next CAS stage."
        )

    elif decision == (
        ExecutionSafetyDecision.ALLOW_WITH_RESTRICTION
    ):
        message = (
            "Execution safety is acceptable only "
            "under the identified restrictions."
        )

    elif decision == (
        ExecutionSafetyDecision.REVIEW_REQUIRED
    ):
        message = (
            "Execution safety requires review before "
            "advancing."
        )

    else:
        message = (
            "Execution safety conditions block advancement."
        )

    return ExecutionSafetyResult(
        status=status,
        decision=decision,
        action_state=action_state,
        message=message,
        flags=assessment.flags,
        restrictions=assessment.restrictions,
        execution_safety_score=(
            assessment.execution_safety_score
        ),
        execution_safety_confidence=(
            assessment.execution_safety_confidence
        ),
        can_advance=can_advance,
        requires_review=requires_review,
        blocked=blocked,
        restricted=restricted,
        safe_for_next_gate=safe_for_next_gate,
        timestamp=_esg_timestamp(),
    )


# ============================================================
# CONTRACT STATE
# ============================================================

def determine_execution_safety_contract_state(
    contract: ExecutionSafetyContract,
) -> ExecutionSafetyContractStatus:

    if contract.result is None:
        if contract.assessment is None:
            return ExecutionSafetyContractStatus.CREATED

        return ExecutionSafetyContractStatus.ASSESSED

    decision = contract.result.decision

    if decision == ExecutionSafetyDecision.BLOCK:
        return ExecutionSafetyContractStatus.BLOCKED

    if decision == (
        ExecutionSafetyDecision.REVIEW_REQUIRED
    ):
        return ExecutionSafetyContractStatus.REVIEW

    if decision == (
        ExecutionSafetyDecision.ALLOW_WITH_RESTRICTION
    ):
        return ExecutionSafetyContractStatus.RESTRICTED

    if decision == ExecutionSafetyDecision.ALLOW:
        if (
            contract.action is not None
            and contract.action.state ==
            ExecutionSafetyActionState.AUTHORIZED
        ):
            return ExecutionSafetyContractStatus.AUTHORIZED

        return ExecutionSafetyContractStatus.DECIDED

    return ExecutionSafetyContractStatus.REJECTED


# ============================================================
# CONTRACT BUILDER
# ============================================================

def build_execution_safety_contract(
    request: ExecutionSafetyRequest,
    assessment: Optional[
        ExecutionSafetyAssessment
    ] = None,
    action: Optional[
        ExecutionSafetyAction
    ] = None,
    result: Optional[
        ExecutionSafetyResult
    ] = None,
) -> ExecutionSafetyContract:

    if assessment is None:
        assessment = build_execution_safety_assessment(
            request
        )

    if result is None:
        decision = determine_execution_safety_decision(
            assessment
        )

        action = build_execution_safety_action(
            request,
            assessment,
            decision,
        )

        result = build_execution_safety_result(
            assessment,
            decision,
        )

    contract = ExecutionSafetyContract(
        request=request,
        assessment=assessment,
        action=action,
        result=result,
        contract_status=(
            ExecutionSafetyContractStatus.CREATED
        ),
    )

    return ExecutionSafetyContract(
        request=contract.request,
        assessment=contract.assessment,
        action=contract.action,
        result=contract.result,
        contract_status=(
            determine_execution_safety_contract_state(
                contract
            )
        ),
        audit=contract.audit,
    )


# ============================================================
# ENGINE
# ============================================================

class ExecutionSafetyGateEngine:

    _instance: Optional[
        "ExecutionSafetyGateEngine"
    ] = None

    def __new__(
        cls,
    ) -> "ExecutionSafetyGateEngine":

        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    @property
    def engine_name(self) -> str:
        return EXECUTION_SAFETY_GATE_ENGINE

    @property
    def version(self) -> str:
        return EXECUTION_SAFETY_GATE_VERSION

    def evaluate(
        self,
        request: ExecutionSafetyRequest,
    ) -> ExecutionSafetyContract:

        assessment = (
            build_execution_safety_assessment(
                request
            )
        )

        decision = (
            determine_execution_safety_decision(
                assessment
            )
        )

        action = build_execution_safety_action(
            request,
            assessment,
            decision,
        )

        result = build_execution_safety_result(
            assessment,
            decision,
        )

        return build_execution_safety_contract(
            request=request,
            assessment=assessment,
            action=action,
            result=result,
        )

    def check(
        self,
        source: Any = None,
        **overrides: Any,
    ) -> ExecutionSafetyContract:

        request = build_execution_safety_request(
            source,
            **overrides,
        )

        return self.evaluate(request)

    def review(
        self,
        source: Any = None,
        **overrides: Any,
    ) -> ExecutionSafetyContract:

        request = build_execution_safety_request(
            source,
            **overrides,
        )

        assessment = (
            build_execution_safety_assessment(
                request
            )
        )

        action = ExecutionSafetyAction(
            action=request.action or "UNKNOWN",
            state=ExecutionSafetyActionState.REVIEW,
            allowed=False,
            restricted=False,
            requires_review=True,
            blocked=False,
            restrictions=assessment.restrictions,
            reasons=(
                assessment.flags
                + assessment.errors
                + assessment.warnings
            ),
            timestamp=_esg_timestamp(),
        )

        result = ExecutionSafetyResult(
            status=ExecutionSafetyResultStatus.REVIEW_REQUIRED,
            decision=ExecutionSafetyDecision.REVIEW_REQUIRED,
            action_state=ExecutionSafetyActionState.REVIEW,
            message=(
                "Explicit execution safety review required."
            ),
            flags=assessment.flags,
            restrictions=assessment.restrictions,
            execution_safety_score=(
                assessment.execution_safety_score
            ),
            execution_safety_confidence=(
                assessment.execution_safety_confidence
            ),
            can_advance=False,
            requires_review=True,
            blocked=False,
            restricted=False,
            safe_for_next_gate=False,
            timestamp=_esg_timestamp(),
        )

        return build_execution_safety_contract(
            request=request,
            assessment=assessment,
            action=action,
            result=result,
        )


# ============================================================
# PUBLIC ENGINE ACCESS
# ============================================================

def get_execution_safety_gate_engine(
) -> ExecutionSafetyGateEngine:
    return ExecutionSafetyGateEngine()


def evaluate_execution_safety(
    request: ExecutionSafetyRequest,
) -> ExecutionSafetyContract:

    return get_execution_safety_gate_engine().evaluate(
        request
    )


def check_execution_safety(
    source: Any = None,
    **overrides: Any,
) -> ExecutionSafetyContract:

    return get_execution_safety_gate_engine().check(
        source,
        **overrides,
    )


def review_execution_safety(
    source: Any = None,
    **overrides: Any,
) -> ExecutionSafetyContract:

    return get_execution_safety_gate_engine().review(
        source,
        **overrides,
    )


# ============================================================
# PART 3 COMPLETE
# ============================================================
# ============================================================
# ROBOMLM CAS — EXECUTION SAFETY GATE
# PART 4/5
# Validation, Safety Helpers, Authority, Audit, Health
# ============================================================


# ============================================================
# ACTION VALIDATION
# ============================================================

def validate_execution_safety_action(
    action: ExecutionSafetyAction,
) -> bool:

    if not isinstance(
        action,
        ExecutionSafetyAction,
    ):
        return False

    if not action.action:
        return False

    if action.state == ExecutionSafetyActionState.AUTHORIZED:
        if not action.allowed:
            return False

        if action.blocked or action.requires_review:
            return False

    if action.state == ExecutionSafetyActionState.RESTRICTED:
        if not action.allowed:
            return False

        if not action.restricted:
            return False

    if action.state == ExecutionSafetyActionState.REVIEW:
        if not action.requires_review:
            return False

    if action.state == ExecutionSafetyActionState.BLOCKED:
        if not action.blocked:
            return False

    return True


# ============================================================
# RESULT VALIDATION
# ============================================================

def validate_execution_safety_result(
    result: ExecutionSafetyResult,
) -> bool:

    if not isinstance(
        result,
        ExecutionSafetyResult,
    ):
        return False

    if result.decision == ExecutionSafetyDecision.ALLOW:
        if result.blocked:
            return False

        if result.requires_review:
            return False

        if not result.can_advance:
            return False

    elif result.decision == (
        ExecutionSafetyDecision.ALLOW_WITH_RESTRICTION
    ):
        if result.blocked:
            return False

        if not result.restricted:
            return False

        if not result.can_advance:
            return False

    elif result.decision == (
        ExecutionSafetyDecision.REVIEW_REQUIRED
    ):
        if not result.requires_review:
            return False

        if result.can_advance:
            return False

    elif result.decision == (
        ExecutionSafetyDecision.BLOCK
    ):
        if not result.blocked:
            return False

        if result.can_advance:
            return False

    else:
        return False

    expected_status = (
        determine_execution_safety_result_status(
            result.decision
        )
    )

    if result.status != expected_status:
        return False

    expected_state = (
        determine_execution_safety_action_state(
            result.decision
        )
    )

    if result.action_state != expected_state:
        return False

    return True


# ============================================================
# CONTRACT VALIDATION
# ============================================================

def validate_execution_safety_contract(
    contract: ExecutionSafetyContract,
) -> bool:

    if not isinstance(
        contract,
        ExecutionSafetyContract,
    ):
        return False

    request_validation = (
        validate_execution_safety_request(
            contract.request
        )
    )

    if not request_validation.valid:
        return False

    if contract.assessment is None:
        return False

    if contract.action is None:
        return False

    if contract.result is None:
        return False

    if not validate_execution_safety_action(
        contract.action
    ):
        return False

    if not validate_execution_safety_result(
        contract.result
    ):
        return False

    expected_state = (
        determine_execution_safety_contract_state(
            contract
        )
    )

    if contract.contract_status != expected_state:
        return False

    return True


# ============================================================
# READINESS / SAFETY HELPERS
# ============================================================

def execution_safety_ready(
    contract: ExecutionSafetyContract,
) -> bool:

    if contract.assessment is None:
        return False

    return (
        contract.assessment.readiness
        == ExecutionSafetyReadiness.READY
    )


def execution_safety_can_advance(
    contract: ExecutionSafetyContract,
) -> bool:

    if contract.result is None:
        return False

    return bool(
        contract.result.can_advance
    )


def execution_safety_requires_review(
    contract: ExecutionSafetyContract,
) -> bool:

    if contract.result is None:
        return True

    return bool(
        contract.result.requires_review
    )


def execution_safety_is_blocked(
    contract: ExecutionSafetyContract,
) -> bool:

    if contract.result is None:
        return False

    return bool(
        contract.result.blocked
    )


def execution_safety_is_restricted(
    contract: ExecutionSafetyContract,
) -> bool:

    if contract.result is None:
        return False

    return bool(
        contract.result.restricted
    )


def execution_safety_is_safe_for_next_gate(
    contract: ExecutionSafetyContract,
) -> bool:

    if contract.result is None:
        return False

    return bool(
        contract.result.safe_for_next_gate
    )


# ============================================================
# ACCESSORS
# ============================================================

def get_execution_safety_status(
    contract: ExecutionSafetyContract,
) -> Optional[ExecutionSafetyStatus]:

    if contract.assessment is None:
        return None

    return determine_execution_safety_status(
        contract.assessment
    )


def get_execution_safety_decision(
    contract: ExecutionSafetyContract,
) -> Optional[ExecutionSafetyDecision]:

    if contract.result is None:
        return None

    return contract.result.decision


def get_execution_safety_action_state(
    contract: ExecutionSafetyContract,
) -> Optional[ExecutionSafetyActionState]:

    if contract.result is None:
        return None

    return contract.result.action_state


# ============================================================
# AUTHORITY BOUNDARIES
# ============================================================

def execution_safety_generates_market_decision() -> bool:
    return False


def execution_safety_generates_alpha() -> bool:
    return False


def execution_safety_modifies_d13() -> bool:
    return False


def execution_safety_overrides_d13() -> bool:
    return False


def execution_safety_replaces_risk_authority() -> bool:
    return False


def execution_safety_overrides_risk_authority() -> bool:
    return False


def execution_safety_overrides_cas() -> bool:
    return False


def execution_safety_authorizes_execution() -> bool:
    """
    This gate evaluates execution safety.

    It does NOT itself grant final execution authority.
    Final authorization remains with CAS.
    """
    return False


def execution_safety_places_orders() -> bool:
    return False


def execution_safety_changes_position() -> bool:
    return False


def execution_safety_has_execution_authority() -> bool:
    return False


def execution_safety_has_market_decision_authority() -> bool:
    return False


def execution_safety_is_alpha_engine() -> bool:
    return False


# ============================================================
# AUTHORITY INTEGRITY
# ============================================================

def execution_safety_authority_integrity_ok() -> bool:

    boundaries = (
        execution_safety_generates_market_decision(),
        execution_safety_generates_alpha(),
        execution_safety_modifies_d13(),
        execution_safety_overrides_d13(),
        execution_safety_replaces_risk_authority(),
        execution_safety_overrides_risk_authority(),
        execution_safety_overrides_cas(),
        execution_safety_authorizes_execution(),
        execution_safety_places_orders(),
        execution_safety_changes_position(),
        execution_safety_has_execution_authority(),
        execution_safety_has_market_decision_authority(),
        execution_safety_is_alpha_engine(),
    )

    return not any(boundaries)


def execution_safety_has_authority_conflict() -> bool:
    return not execution_safety_authority_integrity_ok()


# ============================================================
# AUDIT
# ============================================================

@dataclass(frozen=True)
class ExecutionSafetyAuditRecord:
    engine: str
    version: str

    request_id: Optional[str]

    status: Optional[str]
    decision: Optional[str]
    action_state: Optional[str]

    execution_safety_score: float
    execution_safety_confidence: float

    flags: tuple[str, ...] = ()
    restrictions: tuple[str, ...] = ()

    authority_integrity: bool = True

    timestamp: str = ""


def build_execution_safety_audit(
    contract: ExecutionSafetyContract,
) -> ExecutionSafetyAuditRecord:

    result = contract.result

    return ExecutionSafetyAuditRecord(
        engine=EXECUTION_SAFETY_GATE_ENGINE,
        version=EXECUTION_SAFETY_GATE_VERSION,
        request_id=contract.request.request_id,

        status=(
            result.status.value
            if result is not None
            and isinstance(result.status, Enum)
            else getattr(result, "status", None)
        ),

        decision=(
            result.decision.value
            if result is not None
            and isinstance(result.decision, Enum)
            else getattr(result, "decision", None)
        ),

        action_state=(
            result.action_state.value
            if result is not None
            and isinstance(result.action_state, Enum)
            else getattr(result, "action_state", None)
        ),

        execution_safety_score=(
            result.execution_safety_score
            if result is not None
            else 0.0
        ),

        execution_safety_confidence=(
            result.execution_safety_confidence
            if result is not None
            else 0.0
        ),

        flags=(
            result.flags
            if result is not None
            else ()
        ),

        restrictions=(
            result.restrictions
            if result is not None
            else ()
        ),

        authority_integrity=(
            execution_safety_authority_integrity_ok()
        ),

        timestamp=_esg_timestamp(),
    )


# ============================================================
# ENGINE HEALTH
# ============================================================

@dataclass(frozen=True)
class ExecutionSafetyEngineHealth:
    engine: str
    version: str

    healthy: bool
    operational: bool

    authority_integrity: bool

    request_contract_available: bool
    assessment_available: bool
    result_contract_available: bool

    checked_at: str = ""


def get_execution_safety_engine_health(
) -> ExecutionSafetyEngineHealth:

    authority_ok = (
        execution_safety_authority_integrity_ok()
    )

    healthy = bool(authority_ok)

    return ExecutionSafetyEngineHealth(
        engine=EXECUTION_SAFETY_GATE_ENGINE,
        version=EXECUTION_SAFETY_GATE_VERSION,
        healthy=healthy,
        operational=healthy,
        authority_integrity=authority_ok,
        request_contract_available=True,
        assessment_available=True,
        result_contract_available=True,
        checked_at=_esg_timestamp(),
    )


# ============================================================
# ENGINE INFO
# ============================================================

def get_execution_safety_engine_info() -> dict:

    return {
        "engine": EXECUTION_SAFETY_GATE_ENGINE,
        "version": EXECUTION_SAFETY_GATE_VERSION,
        "role": "EXECUTION_SAFETY_CONTROL",
        "healthy": (
            get_execution_safety_engine_health().healthy
        ),
        "operational": (
            get_execution_safety_engine_health().operational
        ),
        "authority_integrity": (
            execution_safety_authority_integrity_ok()
        ),
        "generates_alpha": False,
        "generates_market_decision": False,
        "modifies_d13": False,
        "overrides_d13": False,
        "replaces_risk_authority": False,
        "overrides_cas": False,
        "authorizes_execution": False,
        "places_orders": False,
        "changes_position": False,
    }


# ============================================================
# INTEGRITY
# ============================================================

def execution_safety_integrity_ok() -> bool:

    health = get_execution_safety_engine_health()

    return bool(
        health.healthy
        and health.authority_integrity
    )


# ============================================================
# PART 4 COMPLETE
# ============================================================
# ============================================================
# ROBOMLM CAS — EXECUTION SAFETY GATE
# PART 5/5
# Lifecycle, Serialization, Summary, Snapshot, Public API
# ============================================================


# ============================================================
# LIFECYCLE
# ============================================================

class ExecutionSafetyLifecycleState(str, Enum):
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


def determine_execution_safety_lifecycle(
    contract: ExecutionSafetyContract,
) -> ExecutionSafetyLifecycleState:

    if not validate_execution_safety_contract(contract):
        return ExecutionSafetyLifecycleState.REJECTED

    if contract.result is None:
        if contract.assessment is None:
            return ExecutionSafetyLifecycleState.CREATED

        return ExecutionSafetyLifecycleState.ASSESSED

    decision = contract.result.decision

    if decision == ExecutionSafetyDecision.BLOCK:
        return ExecutionSafetyLifecycleState.BLOCKED

    if decision == ExecutionSafetyDecision.REVIEW_REQUIRED:
        return ExecutionSafetyLifecycleState.REVIEW

    if decision == (
        ExecutionSafetyDecision.ALLOW_WITH_RESTRICTION
    ):
        return ExecutionSafetyLifecycleState.RESTRICTED

    if decision == ExecutionSafetyDecision.ALLOW:
        if (
            contract.action is not None
            and contract.action.state
            == ExecutionSafetyActionState.AUTHORIZED
        ):
            return ExecutionSafetyLifecycleState.ACTIVE

        return ExecutionSafetyLifecycleState.DECIDED

    return ExecutionSafetyLifecycleState.COMPLETED


def freeze_execution_safety(
    contract: ExecutionSafetyContract,
) -> ExecutionSafetyLifecycleState:
    return ExecutionSafetyLifecycleState.FROZEN


def retain_execution_safety(
    contract: ExecutionSafetyContract,
) -> ExecutionSafetyLifecycleState:
    return ExecutionSafetyLifecycleState.RETAINED


def reject_execution_safety(
    contract: ExecutionSafetyContract,
) -> ExecutionSafetyLifecycleState:
    return ExecutionSafetyLifecycleState.REJECTED


# ============================================================
# SERIALIZATION HELPERS
# ============================================================

def execution_safety_request_to_dict(
    request: ExecutionSafetyRequest,
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

        "mode": (
            request.mode.value
            if isinstance(request.mode, Enum)
            else request.mode
        ),

        "strategy": request.strategy,
        "timeframe": request.timeframe,

        "priority": (
            request.priority.value
            if isinstance(request.priority, Enum)
            else request.priority
        ),

        "broker": request.broker,
        "venue": request.venue,
        "execution_channel": request.execution_channel,

        "order_type": request.order_type,
        "quantity": request.quantity,
        "price": request.price,
        "stop_price": request.stop_price,
        "limit_price": request.limit_price,

        "reduce_only": request.reduce_only,
        "close_only": request.close_only,
        "post_only": request.post_only,

        "market_open": request.market_open,
        "trading_halted": request.trading_halted,
        "kill_switch_active": request.kill_switch_active,
        "execution_enabled": request.execution_enabled,

        "liquidity_ok": request.liquidity_ok,
        "slippage_ok": request.slippage_ok,
        "spread_ok": request.spread_ok,
        "latency_ok": request.latency_ok,
        "price_valid": request.price_valid,

        "broker_connected": request.broker_connected,
        "venue_available": request.venue_available,
        "order_channel_ready": request.order_channel_ready,

        "metadata": dict(request.metadata or {}),

        "request_id": request.request_id,
        "timestamp": request.timestamp,
    }


def execution_safety_assessment_to_dict(
    assessment: ExecutionSafetyAssessment,
) -> dict:

    return {
        "data_state": (
            assessment.data_state.value
            if isinstance(
                assessment.data_state,
                Enum,
            )
            else assessment.data_state
        ),

        "consistency": (
            assessment.consistency.value
            if isinstance(
                assessment.consistency,
                Enum,
            )
            else assessment.consistency
        ),

        "readiness": (
            assessment.readiness.value
            if isinstance(
                assessment.readiness,
                Enum,
            )
            else assessment.readiness
        ),

        "completeness": assessment.completeness,

        "execution_safety_score": (
            assessment.execution_safety_score
        ),

        "execution_safety_confidence": (
            assessment.execution_safety_confidence
        ),

        "requirements_met": assessment.requirements_met,

        "flags": list(assessment.flags or []),
        "restrictions": list(
            assessment.restrictions or []
        ),

        "errors": list(assessment.errors or []),
        "warnings": list(assessment.warnings or []),
    }


def execution_safety_action_to_dict(
    action: ExecutionSafetyAction,
) -> dict:

    return {
        "action": action.action,

        "state": (
            action.state.value
            if isinstance(action.state, Enum)
            else action.state
        ),

        "allowed": action.allowed,
        "restricted": action.restricted,
        "requires_review": action.requires_review,
        "blocked": action.blocked,

        "restrictions": list(
            action.restrictions or []
        ),

        "reasons": list(
            action.reasons or []
        ),

        "timestamp": action.timestamp,
    }


def execution_safety_result_to_dict(
    result: ExecutionSafetyResult,
) -> dict:

    return {
        "status": (
            result.status.value
            if isinstance(result.status, Enum)
            else result.status
        ),

        "decision": (
            result.decision.value
            if isinstance(result.decision, Enum)
            else result.decision
        ),

        "action_state": (
            result.action_state.value
            if isinstance(result.action_state, Enum)
            else result.action_state
        ),

        "message": result.message,

        "flags": list(result.flags or []),
        "restrictions": list(
            result.restrictions or []
        ),

        "execution_safety_score": (
            result.execution_safety_score
        ),

        "execution_safety_confidence": (
            result.execution_safety_confidence
        ),

        "can_advance": result.can_advance,
        "requires_review": result.requires_review,
        "blocked": result.blocked,
        "restricted": result.restricted,
        "safe_for_next_gate": (
            result.safe_for_next_gate
        ),

        "timestamp": result.timestamp,
    }


def execution_safety_contract_to_dict(
    contract: ExecutionSafetyContract,
) -> dict:

    return {
        "engine": EXECUTION_SAFETY_GATE_ENGINE,
        "version": EXECUTION_SAFETY_GATE_VERSION,

        "contract_status": (
            contract.contract_status.value
            if isinstance(
                contract.contract_status,
                Enum,
            )
            else contract.contract_status
        ),

        "request": (
            execution_safety_request_to_dict(
                contract.request
            )
        ),

        "assessment": (
            execution_safety_assessment_to_dict(
                contract.assessment
            )
            if contract.assessment is not None
            else None
        ),

        "action": (
            execution_safety_action_to_dict(
                contract.action
            )
            if contract.action is not None
            else None
        ),

        "result": (
            execution_safety_result_to_dict(
                contract.result
            )
            if contract.result is not None
            else None
        ),

        "audit": (
            contract.audit.__dict__
            if getattr(contract, "audit", None) is not None
            else None
        ),

        "lifecycle": (
            determine_execution_safety_lifecycle(
                contract
            ).value
        ),
    }


# ============================================================
# SUMMARY
# ============================================================

def summarize_execution_safety(
    contract: ExecutionSafetyContract,
) -> dict:

    assessment = contract.assessment
    result = contract.result

    return {
        "valid": validate_execution_safety_contract(
            contract
        ),

        "engine": EXECUTION_SAFETY_GATE_ENGINE,
        "version": EXECUTION_SAFETY_GATE_VERSION,

        "contract_status": (
            contract.contract_status.value
            if isinstance(
                contract.contract_status,
                Enum,
            )
            else contract.contract_status
        ),

        "lifecycle": (
            determine_execution_safety_lifecycle(
                contract
            ).value
        ),

        "status": (
            result.status.value
            if result is not None
            and isinstance(result.status, Enum)
            else getattr(result, "status", None)
        ),

        "decision": (
            result.decision.value
            if result is not None
            and isinstance(result.decision, Enum)
            else getattr(result, "decision", None)
        ),

        "action_state": (
            result.action_state.value
            if result is not None
            and isinstance(result.action_state, Enum)
            else getattr(
                result,
                "action_state",
                None,
            )
        ),

        "execution_safety_score": (
            assessment.execution_safety_score
            if assessment is not None
            else None
        ),

        "execution_safety_confidence": (
            assessment.execution_safety_confidence
            if assessment is not None
            else None
        ),

        "completeness": (
            assessment.completeness
            if assessment is not None
            else None
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
            execution_safety_can_advance(contract)
            if result is not None
            else False
        ),

        "requires_review": (
            execution_safety_requires_review(contract)
            if result is not None
            else False
        ),

        "blocked": (
            execution_safety_is_blocked(contract)
            if result is not None
            else False
        ),

        "restricted": (
            execution_safety_is_restricted(contract)
            if result is not None
            else False
        ),

        "safe_for_next_gate": (
            execution_safety_is_safe_for_next_gate(
                contract
            )
            if result is not None
            else False
        ),

        "authority_integrity": (
            execution_safety_authority_integrity_ok()
        ),
    }


# ============================================================
# AUTHORITY STATEMENT
# ============================================================

def get_execution_safety_authority_statement() -> dict:

    return {
        "authority": "EXECUTION_SAFETY_CONTROL",

        "role": (
            "Evaluate execution environment, order "
            "safety conditions and operational readiness."
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


# ============================================================
# OPERATIONAL STATUS
# ============================================================

def execution_safety_engine_operational() -> bool:

    health = get_execution_safety_engine_health()

    return bool(
        health.healthy
        and health.operational
        and health.authority_integrity
    )


# ============================================================
# FINAL VALIDATION
# ============================================================

def validate_execution_safety(
    contract: ExecutionSafetyContract,
) -> bool:

    if not validate_execution_safety_contract(
        contract
    ):
        return False

    if not execution_safety_authority_integrity_ok():
        return False

    if not execution_safety_engine_operational():
        return False

    if contract.assessment is None:
        return False

    if contract.result is None:
        return False

    if contract.action is None:
        return False

    return True


# ============================================================
# SNAPSHOT
# ============================================================

def execution_safety_snapshot(
    contract: Optional[
        ExecutionSafetyContract
    ] = None,
) -> dict:

    health = get_execution_safety_engine_health()

    snapshot = {
        "engine": EXECUTION_SAFETY_GATE_ENGINE,
        "version": EXECUTION_SAFETY_GATE_VERSION,

        "operational": (
            execution_safety_engine_operational()
        ),

        "health": (
            health.__dict__
            if hasattr(health, "__dict__")
            else health
        ),

        "authority": (
            get_execution_safety_authority_statement()
        ),

        "authority_integrity": (
            execution_safety_authority_integrity_ok()
        ),
    }

    if contract is not None:
        snapshot["valid"] = (
            validate_execution_safety(contract)
        )

        snapshot["lifecycle"] = (
            determine_execution_safety_lifecycle(
                contract
            ).value
        )

        snapshot["summary"] = (
            summarize_execution_safety(contract)
        )

    return snapshot


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [

    # Constants
    "EXECUTION_SAFETY_GATE_ENGINE",
    "EXECUTION_SAFETY_GATE_VERSION",

    # Enums
    "ExecutionSafetyStatus",
    "ExecutionSafetyDecision",
    "ExecutionSafetyMode",
    "ExecutionSafetyPriority",
    "ExecutionSafetyContractStatus",

    "ExecutionSafetyDataState",
    "ExecutionSafetyConsistency",
    "ExecutionSafetyReadiness",

    "ExecutionSafetyActionState",
    "ExecutionSafetyContractState",
    "ExecutionSafetyResultStatus",

    "ExecutionSafetyLifecycleState",

    # Contracts / Models
    "ExecutionSafetyRequest",
    "ExecutionSafetyReference",
    "ExecutionSafetyContractValidation",
    "ExecutionSafetyRequirements",
    "ExecutionSafetyAssessment",
    "ExecutionSafetyAction",
    "ExecutionSafetyResult",
    "ExecutionSafetyContract",
    "ExecutionSafetyAuditRecord",
    "ExecutionSafetyEngineHealth",

    # Builders
    "build_execution_safety_request",
    "build_execution_safety_assessment",
    "build_execution_safety_action",
    "build_execution_safety_result",
    "build_execution_safety_contract",

    # Validation
    "validate_execution_safety_numeric_inputs",
    "validate_execution_safety_request",
    "validate_execution_safety_action",
    "validate_execution_safety_result",
    "validate_execution_safety_contract",
    "validate_execution_safety",

    # Evaluation
    "evaluate_execution_safety_data_state",
    "evaluate_execution_safety_consistency",
    "calculate_execution_safety_completeness",
    "evaluate_execution_safety_requirements",
    "evaluate_execution_safety_readiness",
    "extract_execution_safety_flags",
    "extract_execution_safety_restrictions",
    "calculate_execution_safety_score",
    "calculate_execution_safety_confidence",

    # Decision
    "determine_execution_safety_result_status",
    "determine_execution_safety_status",
    "determine_execution_safety_decision",
    "determine_execution_safety_action_state",
    "determine_execution_safety_contract_state",

    # Engine
    "ExecutionSafetyGateEngine",
    "get_execution_safety_gate_engine",
    "evaluate_execution_safety",
    "check_execution_safety",
    "review_execution_safety",

    # Readiness / Safety
    "execution_safety_ready",
    "execution_safety_can_advance",
    "execution_safety_requires_review",
    "execution_safety_is_blocked",
    "execution_safety_is_restricted",
    "execution_safety_is_safe_for_next_gate",

    # Accessors
    "get_execution_safety_status",
    "get_execution_safety_decision",
    "get_execution_safety_action_state",

    # Authority
    "execution_safety_generates_market_decision",
    "execution_safety_generates_alpha",
    "execution_safety_modifies_d13",
    "execution_safety_overrides_d13",
    "execution_safety_replaces_risk_authority",
    "execution_safety_overrides_risk_authority",
    "execution_safety_overrides_cas",
    "execution_safety_authorizes_execution",
    "execution_safety_places_orders",
    "execution_safety_changes_position",
    "execution_safety_has_execution_authority",
    "execution_safety_has_market_decision_authority",
    "execution_safety_is_alpha_engine",

    "execution_safety_authority_integrity_ok",
    "execution_safety_has_authority_conflict",

    # Audit / Health
    "build_execution_safety_audit",
    "get_execution_safety_engine_health",
    "get_execution_safety_engine_info",
    "execution_safety_integrity_ok",

    # Lifecycle
    "determine_execution_safety_lifecycle",
    "freeze_execution_safety",
    "retain_execution_safety",
    "reject_execution_safety",

    # Serialization
    "execution_safety_request_to_dict",
    "execution_safety_assessment_to_dict",
    "execution_safety_action_to_dict",
    "execution_safety_result_to_dict",
    "execution_safety_contract_to_dict",

    # Summary / Authority / Runtime
    "summarize_execution_safety",
    "get_execution_safety_authority_statement",
    "execution_safety_engine_operational",
    "execution_safety_snapshot",
]