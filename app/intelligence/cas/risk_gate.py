# ============================================================
# ROBOMLM CAS — RISK GATE
# Part 1/5
#
# Role:
#   Evaluate whether a proposed decision/pathway satisfies
#   the applicable risk context before CAS can advance it.
#
# Authority:
#   CAS internal risk gate.
#
# MUST NOT:
#   - generate a market decision
#   - modify D13
#   - override D13
#   - replace the Risk Authority
#   - override CAS
#   - execute an order
#   - change a position
#
# IMPORTANT:
#   Risk score is NOT winning probability / alpha probability.
#   It represents risk-condition quality only.
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Optional
from uuid import uuid4


RISK_GATE_ENGINE = "ROBOMLM_CAS_RISK_GATE"
RISK_GATE_VERSION = "1.0"


# ============================================================
# ENUMS
# ============================================================

class RiskStatus(str, Enum):
    NEW = "NEW"
    VALIDATING = "VALIDATING"
    ACCEPTABLE = "ACCEPTABLE"
    CONDITIONAL = "CONDITIONAL"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    UNACCEPTABLE = "UNACCEPTABLE"
    INVALID = "INVALID"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"


class RiskDecision(str, Enum):
    ALLOW = "ALLOW"
    ALLOW_WITH_RESTRICTION = "ALLOW_WITH_RESTRICTION"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


class RiskMode(str, Enum):
    ANALYSIS = "ANALYSIS"
    SIMULATION = "SIMULATION"
    AUTHORIZED_EXECUTION = "AUTHORIZED_EXECUTION"
    UNKNOWN = "UNKNOWN"


class RiskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class RiskContractStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


# ============================================================
# REQUEST CONTRACT
# ============================================================

@dataclass(frozen=True)
class RiskRequest:
    """
    Input contract for CAS risk evaluation.

    RiskRequest describes the proposed pathway and its risk
    context. It does not itself authorize execution.
    """

    market: str
    instrument: str
    contract: Optional[str] = None

    user_id: Optional[str] = None
    account_id: Optional[str] = None
    plan_id: Optional[str] = None

    action: Optional[str] = None
    direction: Optional[str] = None

    mode: RiskMode = RiskMode.UNKNOWN

    strategy: Optional[str] = None
    timeframe: Optional[str] = None

    priority: RiskPriority = RiskPriority.MEDIUM

    # Explicit risk inputs may be supplied by upstream Risk
    # Authority / Decision / portfolio systems.
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

    quantity: Optional[float] = None
    exposure: Optional[float] = None
    max_exposure: Optional[float] = None

    risk_amount: Optional[float] = None
    max_risk_amount: Optional[float] = None

    leverage: Optional[float] = None
    max_leverage: Optional[float] = None

    margin_available: Optional[float] = None
    margin_required: Optional[float] = None

    volatility: Optional[float] = None
    liquidity_score: Optional[float] = None
    slippage_estimate: Optional[float] = None
    max_slippage: Optional[float] = None

    metadata: Mapping[str, Any] = field(default_factory=dict)

    request_id: str = field(
        default_factory=lambda: str(uuid4())
    )


# ============================================================
# RESULT REFERENCE
# ============================================================

@dataclass(frozen=True)
class RiskReference:
    request_id: str

    user_id: Optional[str]
    account_id: Optional[str]
    plan_id: Optional[str]

    market: str
    instrument: str
    contract: Optional[str]

    action: Optional[str]
    direction: Optional[str]

    mode: RiskMode
    strategy: Optional[str]
    timeframe: Optional[str]

    timestamp: datetime

    status: RiskStatus
    decision: RiskDecision

    risk_score: float
    risk_confidence: float

    restrictions: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()


# ============================================================
# CONTRACT VALIDATION
# ============================================================

@dataclass(frozen=True)
class RiskContractValidation:
    valid: bool

    market_available: bool
    instrument_available: bool

    user_available: bool
    account_available: bool
    plan_available: bool

    action_available: bool
    direction_available: bool

    mode_valid: bool
    metadata_valid: bool

    numeric_inputs_valid: bool

    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:
        return self.valid


# ============================================================
# HELPERS
# ============================================================

def _rg_read_value(
    source: Any,
    key: str,
    default: Any = None,
) -> Any:

    if source is None:
        return default

    if isinstance(source, Mapping):
        return source.get(key, default)

    return getattr(source, key, default)


def _rg_text(value: Any) -> Optional[str]:

    if value is None:
        return None

    text = str(value).strip()

    return text if text else None


def _rg_enum(
    value: Any,
    enum_type: type[Enum],
    default: Enum,
) -> Enum:

    if isinstance(value, enum_type):
        return value

    if value is None:
        return default

    text = str(value).strip().upper()

    for member in enum_type:
        if member.value == text:
            return member

    return default


def _rg_number(
    value: Any,
) -> Optional[float]:

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


def _rg_bool(value: Any) -> bool:

    if isinstance(value, bool):
        return value

    if value is None:
        return False

    if isinstance(value, str):
        return value.strip().lower() in {
            "true",
            "1",
            "yes",
            "y",
            "valid",
            "available",
            "allowed",
            "safe",
        }

    return bool(value)


def _rg_timestamp(value: Any) -> datetime:

    if isinstance(value, datetime):

        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)

    return datetime.now(timezone.utc)


# ============================================================
# REQUEST BUILDER
# ============================================================

def build_risk_request(
    source: Any = None,
    **kwargs: Any,
) -> RiskRequest:

    def value(key: str, default: Any = None) -> Any:
        return kwargs.get(
            key,
            _rg_read_value(source, key, default),
        )

    market = _rg_text(value("market")) or ""
    instrument = _rg_text(value("instrument")) or ""

    mode = _rg_enum(
        value("mode"),
        RiskMode,
        RiskMode.UNKNOWN,
    )

    priority = _rg_enum(
        value("priority"),
        RiskPriority,
        RiskPriority.MEDIUM,
    )

    metadata = value("metadata", {})

    if not isinstance(metadata, Mapping):
        metadata = {}

    numeric_fields = (
        "entry_price",
        "stop_loss",
        "take_profit",
        "quantity",
        "exposure",
        "max_exposure",
        "risk_amount",
        "max_risk_amount",
        "leverage",
        "max_leverage",
        "margin_available",
        "margin_required",
        "volatility",
        "liquidity_score",
        "slippage_estimate",
        "max_slippage",
    )

    numeric_values = {
        field_name: _rg_number(
            value(field_name)
        )
        for field_name in numeric_fields
    }

    return RiskRequest(
        market=market,
        instrument=instrument,

        contract=_rg_text(value("contract")),

        user_id=_rg_text(value("user_id")),
        account_id=_rg_text(value("account_id")),
        plan_id=_rg_text(value("plan_id")),

        action=_rg_text(value("action")),
        direction=_rg_text(value("direction")),

        mode=mode,

        strategy=_rg_text(value("strategy")),
        timeframe=_rg_text(value("timeframe")),

        priority=priority,

        entry_price=numeric_values["entry_price"],
        stop_loss=numeric_values["stop_loss"],
        take_profit=numeric_values["take_profit"],

        quantity=numeric_values["quantity"],
        exposure=numeric_values["exposure"],
        max_exposure=numeric_values["max_exposure"],

        risk_amount=numeric_values["risk_amount"],
        max_risk_amount=numeric_values["max_risk_amount"],

        leverage=numeric_values["leverage"],
        max_leverage=numeric_values["max_leverage"],

        margin_available=numeric_values["margin_available"],
        margin_required=numeric_values["margin_required"],

        volatility=numeric_values["volatility"],
        liquidity_score=numeric_values["liquidity_score"],
        slippage_estimate=numeric_values["slippage_estimate"],
        max_slippage=numeric_values["max_slippage"],

        metadata=dict(metadata),

        request_id=(
            _rg_text(value("request_id"))
            or str(uuid4())
        ),
    )


# ============================================================
# NUMERIC INPUT VALIDATION
# ============================================================

def validate_risk_numeric_inputs(
    request: Optional[RiskRequest],
) -> tuple[bool, tuple[str, ...], tuple[str, ...]]:

    if not isinstance(request, RiskRequest):
        return (
            False,
            ("Invalid RiskRequest",),
            (),
        )

    errors: list[str] = []
    warnings: list[str] = []

    numeric_fields = {
        "entry_price": request.entry_price,
        "stop_loss": request.stop_loss,
        "take_profit": request.take_profit,
        "quantity": request.quantity,
        "exposure": request.exposure,
        "max_exposure": request.max_exposure,
        "risk_amount": request.risk_amount,
        "max_risk_amount": request.max_risk_amount,
        "leverage": request.leverage,
        "max_leverage": request.max_leverage,
        "margin_available": request.margin_available,
        "margin_required": request.margin_required,
        "volatility": request.volatility,
        "liquidity_score": request.liquidity_score,
        "slippage_estimate": request.slippage_estimate,
        "max_slippage": request.max_slippage,
    }

    for name, value in numeric_fields.items():

        if value is None:
            continue

        if not isinstance(value, (int, float)):
            errors.append(
                f"{name} must be numeric"
            )
            continue

        if value != value:
            errors.append(
                f"{name} cannot be NaN"
            )
            continue

        if value in (float("inf"), float("-inf")):
            errors.append(
                f"{name} must be finite"
            )

    non_negative_fields = (
        "quantity",
        "exposure",
        "max_exposure",
        "risk_amount",
        "max_risk_amount",
        "leverage",
        "max_leverage",
        "margin_available",
        "margin_required",
        "volatility",
        "slippage_estimate",
        "max_slippage",
    )

    for name in non_negative_fields:

        value = getattr(request, name)

        if value is not None and value < 0:
            errors.append(
                f"{name} cannot be negative"
            )

    if request.liquidity_score is not None:
        if not 0.0 <= request.liquidity_score <= 100.0:
            errors.append(
                "liquidity_score must be between 0 and 100"
            )

    if (
        request.max_exposure is not None
        and request.exposure is not None
        and request.exposure > request.max_exposure
    ):
        warnings.append(
            "Exposure exceeds supplied maximum"
        )

    if (
        request.max_risk_amount is not None
        and request.risk_amount is not None
        and request.risk_amount > request.max_risk_amount
    ):
        warnings.append(
            "Risk amount exceeds supplied maximum"
        )

    if (
        request.max_leverage is not None
        and request.leverage is not None
        and request.leverage > request.max_leverage
    ):
        warnings.append(
            "Leverage exceeds supplied maximum"
        )

    if (
        request.margin_available is not None
        and request.margin_required is not None
        and request.margin_required > request.margin_available
    ):
        warnings.append(
            "Required margin exceeds available margin"
        )

    if (
        request.max_slippage is not None
        and request.slippage_estimate is not None
        and request.slippage_estimate > request.max_slippage
    ):
        warnings.append(
            "Estimated slippage exceeds maximum"
        )

    return (
        len(errors) == 0,
        tuple(errors),
        tuple(warnings),
    )


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_risk_request(
    request: Optional[RiskRequest],
) -> RiskContractValidation:

    if not isinstance(request, RiskRequest):
        return RiskContractValidation(
            valid=False,

            market_available=False,
            instrument_available=False,

            user_available=False,
            account_available=False,
            plan_available=False,

            action_available=False,
            direction_available=False,

            mode_valid=False,
            metadata_valid=False,
            numeric_inputs_valid=False,

            errors=("Invalid RiskRequest",),
        )

    errors: list[str] = []
    warnings: list[str] = []

    market_available = bool(
        _rg_text(request.market)
    )

    instrument_available = bool(
        _rg_text(request.instrument)
    )

    user_available = bool(
        _rg_text(request.user_id)
    )

    account_available = bool(
        _rg_text(request.account_id)
    )

    plan_available = bool(
        _rg_text(request.plan_id)
    )

    action_available = bool(
        _rg_text(request.action)
    )

    direction_available = bool(
        _rg_text(request.direction)
    )

    mode_valid = (
        request.mode != RiskMode.UNKNOWN
    )

    metadata_valid = isinstance(
        request.metadata,
        Mapping,
    )

    numeric_valid, numeric_errors, numeric_warnings = (
        validate_risk_numeric_inputs(request)
    )

    if not market_available:
        errors.append("Market is required")

    if not instrument_available:
        errors.append("Instrument is required")

    if not user_available:
        errors.append("User identity is required")

    if not account_available:
        errors.append("Account identity is required")

    if not action_available:
        errors.append("Risk pathway/action is required")

    if not mode_valid:
        errors.append("Valid risk mode is required")

    if not direction_available:
        warnings.append(
            "Direction is missing; pathway may not require direction"
        )

    if not plan_available:
        warnings.append("Plan identity is missing")

    if not metadata_valid:
        errors.append(
            "Metadata must be a mapping"
        )

    errors.extend(numeric_errors)
    warnings.extend(numeric_warnings)

    return RiskContractValidation(
        valid=len(errors) == 0,

        market_available=market_available,
        instrument_available=instrument_available,

        user_available=user_available,
        account_available=account_available,
        plan_available=plan_available,

        action_available=action_available,
        direction_available=direction_available,

        mode_valid=mode_valid,
        metadata_valid=metadata_valid,

        numeric_inputs_valid=numeric_valid,

        errors=tuple(dict.fromkeys(errors)),
        warnings=tuple(dict.fromkeys(warnings)),
    )
# ============================================================
# ROBOMLM CAS — RISK GATE
# Part 2/5
#
# Requirements • Data State • Consistency • Readiness
# Assessment • Risk Condition Evaluation
# ============================================================


# ============================================================
# ENUMS — EVALUATION STATE
# ============================================================

class RiskDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    UNKNOWN = "UNKNOWN"


class RiskConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONFLICTING = "CONFLICTING"
    INSUFFICIENT = "INSUFFICIENT"
    UNKNOWN = "UNKNOWN"


class RiskReadiness(str, Enum):
    READY = "READY"
    CONDITIONAL = "CONDITIONAL"
    NOT_READY = "NOT_READY"
    UNKNOWN = "UNKNOWN"


# ============================================================
# REQUIREMENTS CONTRACT
# ============================================================

@dataclass(frozen=True)
class RiskRequirements:
    request_valid: bool

    market_available: bool
    instrument_available: bool

    user_available: bool
    account_available: bool
    plan_available: bool

    action_available: bool
    direction_available: bool

    mode_defined: bool
    strategy_available: bool
    timeframe_available: bool

    price_context_available: bool
    risk_limit_available: bool
    exposure_context_available: bool
    margin_context_available: bool
    leverage_context_available: bool
    liquidity_context_available: bool

    data_state: RiskDataState
    consistency: RiskConsistency
    readiness: RiskReadiness

    completeness_score: float

    warnings: tuple[str, ...] = ()


# ============================================================
# ASSESSMENT CONTRACT
# ============================================================

@dataclass(frozen=True)
class RiskAssessment:
    readiness: RiskReadiness
    data_state: RiskDataState
    consistency: RiskConsistency

    risk_score: float
    confidence_score: float
    completeness_score: float

    risk_flags: tuple[str, ...] = ()
    restrictions: tuple[str, ...] = ()

    strengths: tuple[str, ...] = ()
    weaknesses: tuple[str, ...] = ()

    rationale: str = ""


# ============================================================
# DATA STATE
# ============================================================

def evaluate_risk_data_state(
    request: Optional[RiskRequest],
) -> RiskDataState:

    if not isinstance(request, RiskRequest):
        return RiskDataState.MISSING

    components = (
        bool(_rg_text(request.market)),
        bool(_rg_text(request.instrument)),
        bool(_rg_text(request.user_id)),
        bool(_rg_text(request.account_id)),
        bool(_rg_text(request.action)),
        request.mode != RiskMode.UNKNOWN,

        request.entry_price is not None,
        request.quantity is not None,
        request.exposure is not None,
        request.risk_amount is not None,
    )

    available = sum(
        1 for value in components if value
    )

    if available == len(components):
        return RiskDataState.COMPLETE

    if available == 0:
        return RiskDataState.MISSING

    if available >= len(components) // 2:
        return RiskDataState.PARTIAL

    return RiskDataState.UNKNOWN


# ============================================================
# CONSISTENCY
# ============================================================

def evaluate_risk_consistency(
    request: Optional[RiskRequest],
) -> RiskConsistency:

    if not isinstance(request, RiskRequest):
        return RiskConsistency.INSUFFICIENT

    metadata = request.metadata

    if not isinstance(metadata, Mapping):
        return RiskConsistency.CONFLICTING

    conflict_keys = (
        "conflict",
        "conflicting",
        "risk_conflict",
        "account_risk_conflict",
        "exposure_conflict",
        "margin_conflict",
        "leverage_conflict",
        "liquidity_conflict",
    )

    for key in conflict_keys:
        if _rg_bool(metadata.get(key)):
            return RiskConsistency.CONFLICTING

    # Structural price/risk contradictions.
    if (
        request.entry_price is not None
        and request.stop_loss is not None
        and request.take_profit is not None
    ):
        entry = request.entry_price
        stop = request.stop_loss
        target = request.take_profit

        direction = (
            _rg_text(request.direction) or ""
        ).upper()

        if direction in {"BUY", "LONG"}:
            if stop >= entry:
                return RiskConsistency.CONFLICTING

            if target <= entry:
                return RiskConsistency.CONFLICTING

        elif direction in {"SELL", "SHORT"}:
            if stop <= entry:
                return RiskConsistency.CONFLICTING

            if target >= entry:
                return RiskConsistency.CONFLICTING

    return RiskConsistency.CONSISTENT


# ============================================================
# COMPLETENESS
# ============================================================

def calculate_risk_completeness(
    request: Optional[RiskRequest],
) -> float:

    if not isinstance(request, RiskRequest):
        return 0.0

    checks = (
        bool(_rg_text(request.market)),
        bool(_rg_text(request.instrument)),
        bool(_rg_text(request.user_id)),
        bool(_rg_text(request.account_id)),
        bool(_rg_text(request.plan_id)),
        bool(_rg_text(request.action)),
        bool(_rg_text(request.direction)),
        request.mode != RiskMode.UNKNOWN,
        bool(_rg_text(request.strategy)),
        bool(_rg_text(request.timeframe)),

        request.entry_price is not None,
        request.stop_loss is not None,
        request.take_profit is not None,

        request.quantity is not None,
        request.exposure is not None,
        request.max_exposure is not None,

        request.risk_amount is not None,
        request.max_risk_amount is not None,

        request.leverage is not None,
        request.max_leverage is not None,

        request.margin_available is not None,
        request.margin_required is not None,

        request.liquidity_score is not None,
        request.slippage_estimate is not None,
        request.max_slippage is not None,
    )

    return round(
        (
            sum(
                1 for value in checks
                if value
            )
            / len(checks)
        ) * 100.0,
        2,
    )


# ============================================================
# READINESS
# ============================================================

def evaluate_risk_readiness(
    request: Optional[RiskRequest],
    consistency: Optional[RiskConsistency] = None,
) -> RiskReadiness:

    if not isinstance(request, RiskRequest):
        return RiskReadiness.NOT_READY

    validation = validate_risk_request(request)

    if not validation.valid:
        return RiskReadiness.NOT_READY

    if consistency is None:
        consistency = evaluate_risk_consistency(
            request
        )

    if consistency == RiskConsistency.CONFLICTING:
        return RiskReadiness.NOT_READY

    if consistency == RiskConsistency.INSUFFICIENT:
        return RiskReadiness.CONDITIONAL

    completeness = calculate_risk_completeness(
        request
    )

    if completeness >= 85.0:
        return RiskReadiness.READY

    if completeness >= 50.0:
        return RiskReadiness.CONDITIONAL

    return RiskReadiness.NOT_READY


# ============================================================
# REQUIREMENTS EVALUATION
# ============================================================

def evaluate_risk_requirements(
    request: Optional[RiskRequest],
) -> RiskRequirements:

    validation = validate_risk_request(request)

    if not isinstance(request, RiskRequest):
        return RiskRequirements(
            request_valid=False,

            market_available=False,
            instrument_available=False,

            user_available=False,
            account_available=False,
            plan_available=False,

            action_available=False,
            direction_available=False,

            mode_defined=False,
            strategy_available=False,
            timeframe_available=False,

            price_context_available=False,
            risk_limit_available=False,
            exposure_context_available=False,
            margin_context_available=False,
            leverage_context_available=False,
            liquidity_context_available=False,

            data_state=RiskDataState.MISSING,
            consistency=RiskConsistency.INSUFFICIENT,
            readiness=RiskReadiness.NOT_READY,

            completeness_score=0.0,

            warnings=("Invalid risk request",),
        )

    data_state = evaluate_risk_data_state(
        request
    )

    consistency = evaluate_risk_consistency(
        request
    )

    completeness = calculate_risk_completeness(
        request
    )

    readiness = evaluate_risk_readiness(
        request,
        consistency,
    )

    warnings = list(
        validation.warnings
    )

    if not _rg_text(request.strategy):
        warnings.append(
            "Strategy information is missing"
        )

    if not _rg_text(request.timeframe):
        warnings.append(
            "Timeframe information is missing"
        )

    price_context_available = (
        request.entry_price is not None
    )

    risk_limit_available = (
        request.risk_amount is not None
        or request.max_risk_amount is not None
    )

    exposure_context_available = (
        request.exposure is not None
        or request.max_exposure is not None
    )

    margin_context_available = (
        request.margin_available is not None
        or request.margin_required is not None
    )

    leverage_context_available = (
        request.leverage is not None
        or request.max_leverage is not None
    )

    liquidity_context_available = (
        request.liquidity_score is not None
        or request.slippage_estimate is not None
        or request.max_slippage is not None
    )

    if not price_context_available:
        warnings.append(
            "Entry price context is unavailable"
        )

    if not risk_limit_available:
        warnings.append(
            "Explicit risk limit is unavailable"
        )

    if not exposure_context_available:
        warnings.append(
            "Exposure context is unavailable"
        )

    if not margin_context_available:
        warnings.append(
            "Margin context is unavailable"
        )

    if not leverage_context_available:
        warnings.append(
            "Leverage context is unavailable"
        )

    if not liquidity_context_available:
        warnings.append(
            "Liquidity/slippage context is unavailable"
        )

    return RiskRequirements(
        request_valid=validation.valid,

        market_available=validation.market_available,
        instrument_available=validation.instrument_available,

        user_available=validation.user_available,
        account_available=validation.account_available,
        plan_available=validation.plan_available,

        action_available=validation.action_available,
        direction_available=validation.direction_available,

        mode_defined=(
            request.mode != RiskMode.UNKNOWN
        ),

        strategy_available=bool(
            _rg_text(request.strategy)
        ),

        timeframe_available=bool(
            _rg_text(request.timeframe)
        ),

        price_context_available=price_context_available,
        risk_limit_available=risk_limit_available,
        exposure_context_available=exposure_context_available,
        margin_context_available=margin_context_available,
        leverage_context_available=leverage_context_available,
        liquidity_context_available=liquidity_context_available,

        data_state=data_state,
        consistency=consistency,
        readiness=readiness,

        completeness_score=completeness,

        warnings=tuple(
            dict.fromkeys(warnings)
        ),
    )


# ============================================================
# RISK CONDITION FLAGS
# ============================================================

def extract_risk_flags(
    request: Optional[RiskRequest],
) -> tuple[str, ...]:

    if not isinstance(request, RiskRequest):
        return ("INVALID_REQUEST",)

    flags: list[str] = []

    metadata = request.metadata

    explicit_flags = metadata.get(
        "risk_flags",
        (),
    )

    if isinstance(explicit_flags, str):
        explicit_flags = (
            explicit_flags,
        )

    if isinstance(
        explicit_flags,
        (list, tuple, set),
    ):
        for flag in explicit_flags:
            text = _rg_text(flag)

            if text:
                flags.append(text.upper())

    if (
        request.max_exposure is not None
        and request.exposure is not None
        and request.exposure > request.max_exposure
    ):
        flags.append("EXPOSURE_LIMIT_BREACH")

    if (
        request.max_risk_amount is not None
        and request.risk_amount is not None
        and request.risk_amount > request.max_risk_amount
    ):
        flags.append("RISK_LIMIT_BREACH")

    if (
        request.max_leverage is not None
        and request.leverage is not None
        and request.leverage > request.max_leverage
    ):
        flags.append("LEVERAGE_LIMIT_BREACH")

    if (
        request.margin_available is not None
        and request.margin_required is not None
        and request.margin_required > request.margin_available
    ):
        flags.append("MARGIN_INSUFFICIENT")

    if (
        request.max_slippage is not None
        and request.slippage_estimate is not None
        and request.slippage_estimate > request.max_slippage
    ):
        flags.append("SLIPPAGE_LIMIT_BREACH")

    if (
        request.liquidity_score is not None
        and request.liquidity_score < 30.0
    ):
        flags.append("LOW_LIQUIDITY")

    if _rg_bool(
        metadata.get("stale_data")
    ):
        flags.append("STALE_DATA")

    if _rg_bool(
        metadata.get("missing_data")
    ):
        flags.append("MISSING_DATA")

    if _rg_bool(
        metadata.get("liquidation_risk")
    ):
        flags.append("LIQUIDATION_RISK")

    if _rg_bool(
        metadata.get("high_volatility")
    ):
        flags.append("HIGH_VOLATILITY")

    return tuple(
        dict.fromkeys(flags)
    )


# ============================================================
# RISK RESTRICTIONS
# ============================================================

def extract_risk_restrictions(
    request: Optional[RiskRequest],
) -> tuple[str, ...]:

    if not isinstance(request, RiskRequest):
        return ("INVALID_REQUEST",)

    restrictions: list[str] = []

    metadata = request.metadata

    if _rg_bool(
        metadata.get("reduce_only")
    ):
        restrictions.append("REDUCE_ONLY")

    if _rg_bool(
        metadata.get("manual_only")
    ):
        restrictions.append("MANUAL_ONLY")

    if _rg_bool(
        metadata.get("no_new_position")
    ):
        restrictions.append("NO_NEW_POSITION")

    if _rg_bool(
        metadata.get("position_size_limited")
    ):
        restrictions.append("POSITION_SIZE_LIMITED")

    if _rg_bool(
        metadata.get("exposure_limited")
    ):
        restrictions.append("EXPOSURE_LIMITED")

    if _rg_bool(
        metadata.get("leverage_limited")
    ):
        restrictions.append("LEVERAGE_LIMITED")

    if _rg_bool(
        metadata.get("liquidity_restricted")
    ):
        restrictions.append("LIQUIDITY_RESTRICTED")

    if _rg_bool(
        metadata.get("closing_window_restricted")
    ):
        restrictions.append(
            "CLOSING_WINDOW_RESTRICTED"
        )

    return tuple(
        dict.fromkeys(restrictions)
    )


# ============================================================
# RISK SCORE
# ============================================================

def calculate_risk_score(
    request: Optional[RiskRequest],
    requirements: Optional[RiskRequirements] = None,
) -> float:

    if not isinstance(request, RiskRequest):
        return 0.0

    if requirements is None:
        requirements = evaluate_risk_requirements(
            request
        )

    score = 0.0

    # Structural context
    if requirements.market_available:
        score += 10.0

    if requirements.instrument_available:
        score += 10.0

    if requirements.user_available:
        score += 10.0

    if requirements.account_available:
        score += 10.0

    if requirements.action_available:
        score += 10.0

    if requirements.mode_defined:
        score += 5.0

    # Risk-control context
    if requirements.price_context_available:
        score += 10.0

    if requirements.risk_limit_available:
        score += 10.0

    if requirements.exposure_context_available:
        score += 10.0

    if requirements.margin_context_available:
        score += 5.0

    if requirements.leverage_context_available:
        score += 5.0

    if requirements.liquidity_context_available:
        score += 5.0

    flags = extract_risk_flags(request)

    hard_breach_flags = {
        "EXPOSURE_LIMIT_BREACH",
        "RISK_LIMIT_BREACH",
        "LEVERAGE_LIMIT_BREACH",
        "MARGIN_INSUFFICIENT",
        "SLIPPAGE_LIMIT_BREACH",
        "LIQUIDATION_RISK",
    }

    if any(
        flag in hard_breach_flags
        for flag in flags
    ):
        return 0.0

    if "STALE_DATA" in flags:
        score *= 0.60

    if "MISSING_DATA" in flags:
        score *= 0.65

    if "LOW_LIQUIDITY" in flags:
        score *= 0.75

    if "HIGH_VOLATILITY" in flags:
        score *= 0.85

    if requirements.consistency == RiskConsistency.CONFLICTING:
        return 0.0

    if requirements.consistency == RiskConsistency.INSUFFICIENT:
        score *= 0.70

    return round(
        max(
            0.0,
            min(100.0, score),
        ),
        2,
    )


# ============================================================
# RISK CONFIDENCE
# ============================================================

def calculate_risk_confidence(
    requirements: RiskRequirements,
    risk_score: float,
) -> float:

    if requirements.consistency == RiskConsistency.CONFLICTING:
        return 0.0

    confidence = (
        requirements.completeness_score * 0.60
        + risk_score * 0.40
    )

    if requirements.consistency == RiskConsistency.CONSISTENT:
        confidence += 5.0

    elif requirements.consistency == RiskConsistency.INSUFFICIENT:
        confidence -= 15.0

    return round(
        max(
            0.0,
            min(100.0, confidence),
        ),
        2,
    )


# ============================================================
# ASSESSMENT BUILDER
# ============================================================

def build_risk_assessment(
    request: Optional[RiskRequest],
    requirements: Optional[RiskRequirements] = None,
) -> RiskAssessment:

    if not isinstance(request, RiskRequest):
        return RiskAssessment(
            readiness=RiskReadiness.NOT_READY,
            data_state=RiskDataState.MISSING,
            consistency=RiskConsistency.INSUFFICIENT,

            risk_score=0.0,
            confidence_score=0.0,
            completeness_score=0.0,

            risk_flags=("INVALID_REQUEST",),
            weaknesses=(
                "Invalid risk request",
            ),

            rationale=(
                "Risk cannot be evaluated from "
                "an invalid request."
            ),
        )

    if requirements is None:
        requirements = evaluate_risk_requirements(
            request
        )

    risk_score = calculate_risk_score(
        request,
        requirements,
    )

    confidence_score = calculate_risk_confidence(
        requirements,
        risk_score,
    )

    flags = extract_risk_flags(request)
    restrictions = extract_risk_restrictions(
        request
    )

    strengths: list[str] = []
    weaknesses: list[str] = []

    if requirements.account_available:
        strengths.append(
            "Account risk context available"
        )

    if requirements.price_context_available:
        strengths.append(
            "Price context available"
        )

    if requirements.risk_limit_available:
        strengths.append(
            "Risk limit context available"
        )

    if requirements.exposure_context_available:
        strengths.append(
            "Exposure context available"
        )

    if requirements.liquidity_context_available:
        strengths.append(
            "Liquidity/slippage context available"
        )

    if flags:
        weaknesses.append(
            "Risk condition flags detected"
        )

    if restrictions:
        weaknesses.append(
            "One or more risk restrictions detected"
        )

    if requirements.consistency == RiskConsistency.CONFLICTING:
        weaknesses.append(
            "Risk context contains conflict"
        )

    if not requirements.margin_context_available:
        weaknesses.append(
            "Margin context unavailable"
        )

    if not requirements.leverage_context_available:
        weaknesses.append(
            "Leverage context unavailable"
        )

    if requirements.readiness == RiskReadiness.READY:
        rationale = (
            "Risk context is sufficiently complete "
            "and structurally consistent for CAS "
            "risk-gate evaluation."
        )

    elif requirements.readiness == RiskReadiness.CONDITIONAL:
        rationale = (
            "Risk context is partially complete and "
            "requires conditional handling or additional "
            "risk validation."
        )

    elif requirements.consistency == RiskConsistency.CONFLICTING:
        rationale = (
            "Risk evaluation is blocked because the "
            "supplied risk context contains a conflict."
        )

    else:
        rationale = (
            "Risk cannot currently be established with "
            "sufficient structural confidence."
        )

    return RiskAssessment(
        readiness=requirements.readiness,
        data_state=requirements.data_state,
        consistency=requirements.consistency,

        risk_score=risk_score,
        confidence_score=confidence_score,
        completeness_score=requirements.completeness_score,

        risk_flags=flags,
        restrictions=restrictions,

        strengths=tuple(strengths),
        weaknesses=tuple(weaknesses),

        rationale=rationale,
    )
# ============================================================
# ROBOMLM CAS — RISK GATE
# Part 3/5
#
# Result Contract • Action State • Engine
# ============================================================


class RiskActionState(str, Enum):
    NONE = "NONE"
    EVALUATE = "EVALUATE"
    ALLOW = "ALLOW"
    RESTRICT = "RESTRICT"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"
    INVALIDATE = "INVALIDATE"


class RiskContractState(str, Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


class RiskResultStatus(str, Enum):
    ALLOWED = "ALLOWED"
    RESTRICTED = "RESTRICTED"
    REVIEW = "REVIEW"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


@dataclass(frozen=True)
class RiskAction:
    """
    Action produced by the Risk Gate.

    This is a risk-gate action, not a market/trading decision.
    """

    action_state: RiskActionState
    decision: RiskDecision

    pathway: Optional[str]
    direction: Optional[str]

    restrictions: tuple[str, ...] = ()
    risk_flags: tuple[str, ...] = ()

    reasons: tuple[str, ...] = ()

    executable: bool = False
    requires_review: bool = False
    blocked: bool = False


@dataclass(frozen=True)
class RiskResult:
    """
    Final normalized Risk Gate result.

    RiskResult authorizes only risk progression through the
    risk layer. It does not place orders and does not replace
    D13, Risk Authority, or CAS authority.
    """

    request_id: str

    status: RiskResultStatus
    decision: RiskDecision

    risk_status: RiskStatus
    action_state: RiskActionState

    risk_score: float
    risk_confidence: float
    completeness_score: float

    restrictions: tuple[str, ...] = ()
    risk_flags: tuple[str, ...] = ()

    reasons: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    pathway: Optional[str] = None
    direction: Optional[str] = None

    can_advance: bool = False
    requires_review: bool = False
    blocked: bool = False

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass(frozen=True)
class RiskContract:
    """
    Complete Risk Gate contract.

    request → requirements → assessment → action → result
    """

    request: RiskRequest

    requirements: RiskRequirements
    assessment: RiskAssessment

    action: RiskAction
    result: RiskResult

    contract_state: RiskContractState

    contract_valid: bool

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


def determine_risk_result_status(
    decision: RiskDecision,
) -> RiskResultStatus:

    if decision == RiskDecision.ALLOW:
        return RiskResultStatus.ALLOWED

    if decision == RiskDecision.ALLOW_WITH_RESTRICTION:
        return RiskResultStatus.RESTRICTED

    if decision == RiskDecision.REVIEW_REQUIRED:
        return RiskResultStatus.REVIEW

    if decision == RiskDecision.BLOCK:
        return RiskResultStatus.BLOCKED

    return RiskResultStatus.INVALID


def determine_risk_status(
    assessment: RiskAssessment,
    decision: RiskDecision,
) -> RiskStatus:

    if decision == RiskDecision.BLOCK:
        return RiskStatus.BLOCKED

    if decision == RiskDecision.REVIEW_REQUIRED:
        return RiskStatus.REVIEW_REQUIRED

    if decision == RiskDecision.ALLOW_WITH_RESTRICTION:
        return RiskStatus.CONDITIONAL

    if decision == RiskDecision.ALLOW:

        if assessment.readiness == RiskReadiness.READY:
            return RiskStatus.ACCEPTABLE

        if assessment.readiness == RiskReadiness.CONDITIONAL:
            return RiskStatus.CONDITIONAL

        return RiskStatus.UNKNOWN

    if assessment.consistency == RiskConsistency.CONFLICTING:
        return RiskStatus.INVALID

    return RiskStatus.UNKNOWN


def determine_risk_action_state(
    decision: RiskDecision,
) -> RiskActionState:

    if decision == RiskDecision.ALLOW:
        return RiskActionState.ALLOW

    if decision == RiskDecision.ALLOW_WITH_RESTRICTION:
        return RiskActionState.RESTRICT

    if decision == RiskDecision.REVIEW_REQUIRED:
        return RiskActionState.REVIEW

    if decision == RiskDecision.BLOCK:
        return RiskActionState.BLOCK

    return RiskActionState.INVALIDATE


def determine_risk_decision(
    request: Optional[RiskRequest],
    assessment: Optional[RiskAssessment] = None,
) -> RiskDecision:

    if not isinstance(request, RiskRequest):
        return RiskDecision.UNKNOWN

    if assessment is None:
        assessment = build_risk_assessment(request)

    if assessment.consistency == RiskConsistency.CONFLICTING:
        return RiskDecision.BLOCK

    if assessment.risk_score <= 0.0:
        return RiskDecision.BLOCK

    hard_flags = {
        "EXPOSURE_LIMIT_BREACH",
        "RISK_LIMIT_BREACH",
        "LEVERAGE_LIMIT_BREACH",
        "MARGIN_INSUFFICIENT",
        "SLIPPAGE_LIMIT_BREACH",
        "LIQUIDATION_RISK",
    }

    if any(
        flag in hard_flags
        for flag in assessment.risk_flags
    ):
        return RiskDecision.BLOCK

    if assessment.readiness == RiskReadiness.NOT_READY:
        return RiskDecision.REVIEW_REQUIRED

    if assessment.risk_score < 50.0:
        return RiskDecision.REVIEW_REQUIRED

    if assessment.risk_confidence if False else False:
        pass

    if assessment.restrictions:
        return RiskDecision.ALLOW_WITH_RESTRICTION

    if assessment.risk_flags:
        return RiskDecision.ALLOW_WITH_RESTRICTION

    if assessment.readiness == RiskReadiness.CONDITIONAL:
        return RiskDecision.ALLOW_WITH_RESTRICTION

    return RiskDecision.ALLOW


def build_risk_action(
    request: Optional[RiskRequest],
    assessment: Optional[RiskAssessment] = None,
    decision: Optional[RiskDecision] = None,
) -> RiskAction:

    if not isinstance(request, RiskRequest):
        return RiskAction(
            action_state=RiskActionState.INVALIDATE,
            decision=RiskDecision.UNKNOWN,
            pathway=None,
            direction=None,
            reasons=("Invalid risk request",),
            blocked=True,
        )

    if assessment is None:
        assessment = build_risk_assessment(request)

    if decision is None:
        decision = determine_risk_decision(
            request,
            assessment,
        )

    action_state = determine_risk_action_state(
        decision
    )

    executable = (
        decision == RiskDecision.ALLOW
    )

    requires_review = (
        decision == RiskDecision.REVIEW_REQUIRED
    )

    blocked = (
        decision == RiskDecision.BLOCK
    )

    reasons: list[str] = []

    if assessment.rationale:
        reasons.append(
            assessment.rationale
        )

    reasons.extend(
        assessment.weaknesses
    )

    return RiskAction(
        action_state=action_state,
        decision=decision,

        pathway=request.action,
        direction=request.direction,

        restrictions=assessment.restrictions,
        risk_flags=assessment.risk_flags,

        reasons=tuple(
            dict.fromkeys(reasons)
        ),

        executable=executable,
        requires_review=requires_review,
        blocked=blocked,
    )


def build_risk_result(
    request: Optional[RiskRequest],
    assessment: Optional[RiskAssessment] = None,
    action: Optional[RiskAction] = None,
) -> RiskResult:

    if not isinstance(request, RiskRequest):
        return RiskResult(
            request_id="",
            status=RiskResultStatus.INVALID,
            decision=RiskDecision.UNKNOWN,
            risk_status=RiskStatus.INVALID,
            action_state=RiskActionState.INVALIDATE,

            risk_score=0.0,
            risk_confidence=0.0,
            completeness_score=0.0,

            reasons=("Invalid risk request",),

            can_advance=False,
            requires_review=False,
            blocked=True,
        )

    if assessment is None:
        assessment = build_risk_assessment(
            request
        )

    if action is None:
        action = build_risk_action(
            request,
            assessment,
        )

    decision = action.decision

    status = determine_risk_result_status(
        decision
    )

    risk_status = determine_risk_status(
        assessment,
        decision,
    )

    can_advance = (
        decision in {
            RiskDecision.ALLOW,
            RiskDecision.ALLOW_WITH_RESTRICTION,
        }
        and risk_status
        in {
            RiskStatus.ACCEPTABLE,
            RiskStatus.CONDITIONAL,
        }
        and not action.blocked
    )

    warnings = list(
        assessment.weaknesses
    )

    return RiskResult(
        request_id=request.request_id,

        status=status,
        decision=decision,

        risk_status=risk_status,
        action_state=action.action_state,

        risk_score=assessment.risk_score,
        risk_confidence=assessment.confidence_score,
        completeness_score=assessment.completeness_score,

        restrictions=assessment.restrictions,
        risk_flags=assessment.risk_flags,

        reasons=action.reasons,
        warnings=tuple(
            dict.fromkeys(warnings)
        ),

        pathway=request.action,
        direction=request.direction,

        can_advance=can_advance,
        requires_review=action.requires_review,
        blocked=action.blocked,
    )


def determine_risk_contract_state(
    request: Optional[RiskRequest],
    requirements: RiskRequirements,
    result: RiskResult,
) -> RiskContractState:

    if not isinstance(request, RiskRequest):
        return RiskContractState.INVALID

    validation = validate_risk_request(
        request
    )

    if not validation.valid:
        return RiskContractState.INVALID

    if result.status == RiskResultStatus.BLOCKED:
        return RiskContractState.BLOCKED

    if result.status == RiskResultStatus.INVALID:
        return RiskContractState.INVALID

    if (
        requirements.readiness
        == RiskReadiness.NOT_READY
    ):
        return RiskContractState.INCOMPLETE

    return RiskContractState.COMPLETE


def build_risk_contract(
    request: Optional[RiskRequest],
) -> RiskContract:

    if not isinstance(request, RiskRequest):

        invalid_request = build_risk_request()

        requirements = evaluate_risk_requirements(
            invalid_request
        )

        assessment = build_risk_assessment(
            invalid_request,
            requirements,
        )

        action = build_risk_action(
            invalid_request,
            assessment,
        )

        result = build_risk_result(
            invalid_request,
            assessment,
            action,
        )

        return RiskContract(
            request=invalid_request,

            requirements=requirements,
            assessment=assessment,

            action=action,
            result=result,

            contract_state=RiskContractState.INVALID,
            contract_valid=False,
        )

    requirements = evaluate_risk_requirements(
        request
    )

    assessment = build_risk_assessment(
        request,
        requirements,
    )

    action = build_risk_action(
        request,
        assessment,
    )

    result = build_risk_result(
        request,
        assessment,
        action,
    )

    contract_state = determine_risk_contract_state(
        request,
        requirements,
        result,
    )

    contract_valid = (
        contract_state
        in {
            RiskContractState.COMPLETE,
            RiskContractState.INCOMPLETE,
            RiskContractState.BLOCKED,
        }
    )

    return RiskContract(
        request=request,

        requirements=requirements,
        assessment=assessment,

        action=action,
        result=result,

        contract_state=contract_state,
        contract_valid=contract_valid,
    )


class RiskGateEngine:
    """
    Singleton-style CAS Risk Gate engine.

    Authority boundary:
        Risk Gate evaluates risk conditions.
        It does not create market alpha or modify D13.
    """

    _instance: Optional["RiskGateEngine"] = None

    def __new__(
        cls,
    ) -> "RiskGateEngine":

        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    @property
    def engine_name(self) -> str:
        return RISK_GATE_ENGINE

    @property
    def version(self) -> str:
        return RISK_GATE_VERSION

    def evaluate(
        self,
        request: Any = None,
        **kwargs: Any,
    ) -> RiskContract:

        risk_request = build_risk_request(
            request,
            **kwargs,
        )

        return build_risk_contract(
            risk_request
        )

    def check(
        self,
        request: Any = None,
        **kwargs: Any,
    ) -> RiskResult:

        contract = self.evaluate(
            request,
            **kwargs,
        )

        return contract.result

    def review(
        self,
        request: Any = None,
        **kwargs: Any,
    ) -> RiskContract:

        contract = self.evaluate(
            request,
            **kwargs,
        )

        return contract


_RISK_GATE_ENGINE: Optional[RiskGateEngine] = None


def get_risk_gate_engine() -> RiskGateEngine:

    global _RISK_GATE_ENGINE

    if _RISK_GATE_ENGINE is None:
        _RISK_GATE_ENGINE = RiskGateEngine()

    return _RISK_GATE_ENGINE


def evaluate_risk(
    request: Any = None,
    **kwargs: Any,
) -> RiskContract:

    return get_risk_gate_engine().evaluate(
        request,
        **kwargs,
    )


def check_risk(
    request: Any = None,
    **kwargs: Any,
) -> RiskResult:

    return get_risk_gate_engine().check(
        request,
        **kwargs,
    )


def review_risk(
    request: Any = None,
    **kwargs: Any,
) -> RiskContract:

    return get_risk_gate_engine().review(
        request,
        **kwargs,
    )
# ============================================================
# ROBOMLM CAS — RISK GATE
# Part 4/5
#
# Validation • Safety • Authority Boundaries
# Audit • Engine Health • Integrity
# ============================================================


def validate_risk_action(
    action: Optional[RiskAction],
) -> bool:

    if not isinstance(action, RiskAction):
        return False

    valid_states = {
        RiskActionState.NONE,
        RiskActionState.EVALUATE,
        RiskActionState.ALLOW,
        RiskActionState.RESTRICT,
        RiskActionState.REVIEW,
        RiskActionState.BLOCK,
        RiskActionState.INVALIDATE,
    }

    if action.action_state not in valid_states:
        return False

    if not isinstance(
        action.decision,
        RiskDecision,
    ):
        return False

    if action.decision == RiskDecision.ALLOW:
        if action.blocked:
            return False

        if action.requires_review:
            return False

    if action.decision == RiskDecision.REVIEW_REQUIRED:
        if not action.requires_review:
            return False

    if action.decision == RiskDecision.BLOCK:
        if not action.blocked:
            return False

    return True


def validate_risk_result(
    result: Optional[RiskResult],
) -> bool:

    if not isinstance(result, RiskResult):
        return False

    if not result.request_id:
        return False

    if not isinstance(
        result.status,
        RiskResultStatus,
    ):
        return False

    if not isinstance(
        result.decision,
        RiskDecision,
    ):
        return False

    if not isinstance(
        result.risk_status,
        RiskStatus,
    ):
        return False

    if not isinstance(
        result.action_state,
        RiskActionState,
    ):
        return False

    numeric_values = (
        result.risk_score,
        result.risk_confidence,
        result.completeness_score,
    )

    for value in numeric_values:

        if not isinstance(value, (int, float)):
            return False

        if value != value:
            return False

        if value < 0.0 or value > 100.0:
            return False

    if result.blocked:
        if result.can_advance:
            return False

    if result.requires_review:
        if result.can_advance:
            return False

    if result.status == RiskResultStatus.BLOCKED:
        if not result.blocked:
            return False

    if result.status == RiskResultStatus.REVIEW:
        if not result.requires_review:
            return False

    return True


def validate_risk_contract(
    contract: Optional[RiskContract],
) -> bool:

    if not isinstance(contract, RiskContract):
        return False

    if not isinstance(
        contract.request,
        RiskRequest,
    ):
        return False

    if not isinstance(
        contract.requirements,
        RiskRequirements,
    ):
        return False

    if not isinstance(
        contract.assessment,
        RiskAssessment,
    ):
        return False

    if not validate_risk_action(
        contract.action
    ):
        return False

    if not validate_risk_result(
        contract.result
    ):
        return False

    if contract.result.request_id != (
        contract.request.request_id
    ):
        return False

    if not contract.contract_valid:
        return True

    return contract.contract_state in {
        RiskContractState.COMPLETE,
        RiskContractState.INCOMPLETE,
        RiskContractState.BLOCKED,
    }


def risk_ready(
    result: Optional[RiskResult],
) -> bool:

    if not validate_risk_result(result):
        return False

    return (
        result.risk_status
        == RiskStatus.ACCEPTABLE
        and result.decision
        == RiskDecision.ALLOW
        and result.can_advance
        and not result.blocked
        and not result.requires_review
    )


def risk_can_advance(
    result: Optional[RiskResult],
) -> bool:

    if not validate_risk_result(result):
        return False

    return bool(
        result.can_advance
        and not result.blocked
    )


def risk_requires_review(
    result: Optional[RiskResult],
) -> bool:

    if not validate_risk_result(result):
        return True

    return result.requires_review


def risk_is_blocked(
    result: Optional[RiskResult],
) -> bool:

    if not validate_risk_result(result):
        return True

    return result.blocked


def risk_is_restricted(
    result: Optional[RiskResult],
) -> bool:

    if not validate_risk_result(result):
        return False

    return (
        result.status
        == RiskResultStatus.RESTRICTED
    )


def risk_is_safe_for_next_gate(
    result: Optional[RiskResult],
) -> bool:

    if not validate_risk_result(result):
        return False

    return (
        result.status
        in {
            RiskResultStatus.ALLOWED,
            RiskResultStatus.RESTRICTED,
        }
        and result.can_advance
        and not result.blocked
    )


def risk_status_of(
    result: Optional[RiskResult],
) -> RiskStatus:

    if not isinstance(result, RiskResult):
        return RiskStatus.INVALID

    return result.risk_status


def risk_decision_of(
    result: Optional[RiskResult],
) -> RiskDecision:

    if not isinstance(result, RiskResult):
        return RiskDecision.UNKNOWN

    return result.decision


def risk_action_state_of(
    result: Optional[RiskResult],
) -> RiskActionState:

    if not isinstance(result, RiskResult):
        return RiskActionState.INVALIDATE

    return result.action_state


# ============================================================
# AUTHORITY BOUNDARIES
# ============================================================

def risk_generates_market_decision() -> bool:
    return False


def risk_generates_alpha() -> bool:
    return False


def risk_modifies_d13() -> bool:
    return False


def risk_overrides_d13() -> bool:
    return False


def risk_replaces_risk_authority() -> bool:
    return False


def risk_overrides_risk_authority() -> bool:
    return False


def risk_overrides_cas() -> bool:
    return False


def risk_authorizes_execution() -> bool:
    return False


def risk_places_orders() -> bool:
    return False


def risk_changes_position() -> bool:
    return False


def risk_has_execution_authority() -> bool:
    return False


def risk_has_market_decision_authority() -> bool:
    return False


def risk_is_alpha_engine() -> bool:
    return False


def risk_authority_integrity_ok() -> bool:

    return not any(
        (
            risk_generates_market_decision(),
            risk_generates_alpha(),
            risk_modifies_d13(),
            risk_overrides_d13(),
            risk_replaces_risk_authority(),
            risk_overrides_risk_authority(),
            risk_overrides_cas(),
            risk_authorizes_execution(),
            risk_places_orders(),
            risk_changes_position(),
            risk_has_execution_authority(),
            risk_has_market_decision_authority(),
            risk_is_alpha_engine(),
        )
    )


def risk_has_authority_conflict() -> bool:
    return not risk_authority_integrity_ok()


# ============================================================
# AUDIT
# ============================================================

@dataclass(frozen=True)
class RiskAuditRecord:
    audit_id: str

    request_id: str

    engine: str
    version: str

    timestamp: datetime

    status: RiskResultStatus
    decision: RiskDecision
    risk_status: RiskStatus
    action_state: RiskActionState

    risk_score: float
    risk_confidence: float
    completeness_score: float

    pathway: Optional[str]
    direction: Optional[str]

    restrictions: tuple[str, ...] = ()
    risk_flags: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()

    can_advance: bool = False
    requires_review: bool = False
    blocked: bool = False

    authority_integrity: bool = True


def build_risk_audit(
    contract: Optional[RiskContract],
) -> RiskAuditRecord:

    if not isinstance(contract, RiskContract):

        return RiskAuditRecord(
            audit_id=str(uuid4()),
            request_id="",

            engine=RISK_GATE_ENGINE,
            version=RISK_GATE_VERSION,

            timestamp=datetime.now(timezone.utc),

            status=RiskResultStatus.INVALID,
            decision=RiskDecision.UNKNOWN,
            risk_status=RiskStatus.INVALID,
            action_state=RiskActionState.INVALIDATE,

            risk_score=0.0,
            risk_confidence=0.0,
            completeness_score=0.0,

            pathway=None,
            direction=None,

            reasons=("Invalid risk contract",),

            blocked=True,
            authority_integrity=(
                risk_authority_integrity_ok()
            ),
        )

    result = contract.result

    return RiskAuditRecord(
        audit_id=str(uuid4()),
        request_id=contract.request.request_id,

        engine=RISK_GATE_ENGINE,
        version=RISK_GATE_VERSION,

        timestamp=datetime.now(timezone.utc),

        status=result.status,
        decision=result.decision,
        risk_status=result.risk_status,
        action_state=result.action_state,

        risk_score=result.risk_score,
        risk_confidence=result.risk_confidence,
        completeness_score=result.completeness_score,

        pathway=result.pathway,
        direction=result.direction,

        restrictions=result.restrictions,
        risk_flags=result.risk_flags,
        reasons=result.reasons,

        can_advance=result.can_advance,
        requires_review=result.requires_review,
        blocked=result.blocked,

        authority_integrity=(
            risk_authority_integrity_ok()
        ),
    )


# ============================================================
# ENGINE HEALTH
# ============================================================

class RiskEngineHealth(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


def get_risk_engine_health(
    contract: Optional[RiskContract] = None,
) -> RiskEngineHealth:

    if not risk_authority_integrity_ok():
        return RiskEngineHealth.BLOCKED

    if contract is None:
        return RiskEngineHealth.HEALTHY

    if not validate_risk_contract(contract):
        return RiskEngineHealth.INVALID

    result = contract.result

    if result.status == RiskResultStatus.BLOCKED:
        return RiskEngineHealth.BLOCKED

    if result.status in {
        RiskResultStatus.REVIEW,
        RiskResultStatus.RESTRICTED,
    }:
        return RiskEngineHealth.DEGRADED

    return RiskEngineHealth.HEALTHY


def get_risk_engine_info() -> dict[str, Any]:

    return {
        "engine": RISK_GATE_ENGINE,
        "version": RISK_GATE_VERSION,
        "authority": "CAS_INTERNAL_RISK_GATE",

        "market_decision_authority": False,
        "alpha_authority": False,

        "d13_modification": False,
        "d13_override": False,

        "risk_authority_replacement": False,
        "cas_override": False,

        "execution_authority": False,
        "order_placement": False,
        "position_change": False,

        "authority_integrity": (
            risk_authority_integrity_ok()
        ),
    }


def risk_integrity_ok(
    contract: Optional[RiskContract] = None,
) -> bool:

    if not risk_authority_integrity_ok():
        return False

    if contract is None:
        return True

    return validate_risk_contract(
        contract
    )
# ============================================================
# ROBOMLM CAS — RISK GATE
# Part 5/5
#
# Lifecycle • Serialization • Summary
# Operational State • Snapshot • Public API
# ============================================================


class RiskLifecycleState(str, Enum):
    NEW = "NEW"
    EVALUATED = "EVALUATED"
    ALLOWED = "ALLOWED"
    RESTRICTED = "RESTRICTED"
    REVIEW = "REVIEW"
    BLOCKED = "BLOCKED"
    REJECTED = "REJECTED"
    FROZEN = "FROZEN"
    RETAINED = "RETAINED"
    INVALID = "INVALID"


def determine_risk_lifecycle(
    contract: Optional[RiskContract],
) -> RiskLifecycleState:

    if not isinstance(contract, RiskContract):
        return RiskLifecycleState.INVALID

    if not validate_risk_contract(contract):
        return RiskLifecycleState.INVALID

    result = contract.result

    if result.status == RiskResultStatus.BLOCKED:
        return RiskLifecycleState.BLOCKED

    if result.status == RiskResultStatus.REVIEW:
        return RiskLifecycleState.REVIEW

    if result.status == RiskResultStatus.RESTRICTED:
        return RiskLifecycleState.RESTRICTED

    if result.status == RiskResultStatus.ALLOWED:
        return RiskLifecycleState.ALLOWED

    return RiskLifecycleState.REJECTED


def freeze_risk(
    contract: Optional[RiskContract],
) -> RiskLifecycleState:

    if not isinstance(contract, RiskContract):
        return RiskLifecycleState.INVALID

    if not validate_risk_contract(contract):
        return RiskLifecycleState.INVALID

    return RiskLifecycleState.FROZEN


def retain_risk(
    contract: Optional[RiskContract],
) -> RiskLifecycleState:

    if not isinstance(contract, RiskContract):
        return RiskLifecycleState.INVALID

    if not validate_risk_contract(contract):
        return RiskLifecycleState.INVALID

    return RiskLifecycleState.RETAINED


def reject_risk(
    contract: Optional[RiskContract],
) -> RiskLifecycleState:

    if not isinstance(contract, RiskContract):
        return RiskLifecycleState.INVALID

    return RiskLifecycleState.REJECTED


# ============================================================
# SERIALIZATION
# ============================================================

def risk_request_to_dict(
    request: Optional[RiskRequest],
) -> dict[str, Any]:

    if not isinstance(request, RiskRequest):
        return {}

    return {
        "request_id": request.request_id,

        "market": request.market,
        "instrument": request.instrument,
        "contract": request.contract,

        "user_id": request.user_id,
        "account_id": request.account_id,
        "plan_id": request.plan_id,

        "action": request.action,
        "direction": request.direction,

        "mode": request.mode.value,
        "strategy": request.strategy,
        "timeframe": request.timeframe,

        "priority": request.priority.value,

        "entry_price": request.entry_price,
        "stop_loss": request.stop_loss,
        "take_profit": request.take_profit,

        "quantity": request.quantity,
        "exposure": request.exposure,
        "max_exposure": request.max_exposure,

        "risk_amount": request.risk_amount,
        "max_risk_amount": request.max_risk_amount,

        "leverage": request.leverage,
        "max_leverage": request.max_leverage,

        "margin_available": request.margin_available,
        "margin_required": request.margin_required,

        "volatility": request.volatility,
        "liquidity_score": request.liquidity_score,
        "slippage_estimate": request.slippage_estimate,
        "max_slippage": request.max_slippage,

        "metadata": dict(request.metadata),
    }


def risk_assessment_to_dict(
    assessment: Optional[RiskAssessment],
) -> dict[str, Any]:

    if not isinstance(assessment, RiskAssessment):
        return {}

    return {
        "readiness": assessment.readiness.value,
        "data_state": assessment.data_state.value,
        "consistency": assessment.consistency.value,

        "risk_score": assessment.risk_score,
        "confidence_score": assessment.confidence_score,
        "completeness_score": assessment.completeness_score,

        "risk_flags": list(
            assessment.risk_flags
        ),

        "restrictions": list(
            assessment.restrictions
        ),

        "strengths": list(
            assessment.strengths
        ),

        "weaknesses": list(
            assessment.weaknesses
        ),

        "rationale": assessment.rationale,
    }


def risk_result_to_dict(
    result: Optional[RiskResult],
) -> dict[str, Any]:

    if not isinstance(result, RiskResult):
        return {}

    return {
        "request_id": result.request_id,

        "status": result.status.value,
        "decision": result.decision.value,

        "risk_status": result.risk_status.value,
        "action_state": result.action_state.value,

        "risk_score": result.risk_score,
        "risk_confidence": result.risk_confidence,
        "completeness_score": result.completeness_score,

        "restrictions": list(
            result.restrictions
        ),

        "risk_flags": list(
            result.risk_flags
        ),

        "reasons": list(
            result.reasons
        ),

        "warnings": list(
            result.warnings
        ),

        "pathway": result.pathway,
        "direction": result.direction,

        "can_advance": result.can_advance,
        "requires_review": result.requires_review,
        "blocked": result.blocked,

        "timestamp": result.timestamp.isoformat(),
    }


def risk_contract_to_dict(
    contract: Optional[RiskContract],
) -> dict[str, Any]:

    if not isinstance(contract, RiskContract):
        return {}

    return {
        "contract_state": (
            contract.contract_state.value
        ),

        "contract_valid": contract.contract_valid,

        "timestamp": contract.timestamp.isoformat(),

        "request": risk_request_to_dict(
            contract.request
        ),

        "requirements": {
            "request_valid": (
                contract.requirements.request_valid
            ),

            "market_available": (
                contract.requirements.market_available
            ),

            "instrument_available": (
                contract.requirements.instrument_available
            ),

            "user_available": (
                contract.requirements.user_available
            ),

            "account_available": (
                contract.requirements.account_available
            ),

            "plan_available": (
                contract.requirements.plan_available
            ),

            "action_available": (
                contract.requirements.action_available
            ),

            "direction_available": (
                contract.requirements.direction_available
            ),

            "mode_defined": (
                contract.requirements.mode_defined
            ),

            "strategy_available": (
                contract.requirements.strategy_available
            ),

            "timeframe_available": (
                contract.requirements.timeframe_available
            ),

            "price_context_available": (
                contract.requirements.price_context_available
            ),

            "risk_limit_available": (
                contract.requirements.risk_limit_available
            ),

            "exposure_context_available": (
                contract.requirements.exposure_context_available
            ),

            "margin_context_available": (
                contract.requirements.margin_context_available
            ),

            "leverage_context_available": (
                contract.requirements.leverage_context_available
            ),

            "liquidity_context_available": (
                contract.requirements.liquidity_context_available
            ),

            "data_state": (
                contract.requirements.data_state.value
            ),

            "consistency": (
                contract.requirements.consistency.value
            ),

            "readiness": (
                contract.requirements.readiness.value
            ),

            "completeness_score": (
                contract.requirements.completeness_score
            ),

            "warnings": list(
                contract.requirements.warnings
            ),
        },

        "assessment": risk_assessment_to_dict(
            contract.assessment
        ),

        "action": {
            "action_state": (
                contract.action.action_state.value
            ),

            "decision": (
                contract.action.decision.value
            ),

            "pathway": contract.action.pathway,
            "direction": contract.action.direction,

            "restrictions": list(
                contract.action.restrictions
            ),

            "risk_flags": list(
                contract.action.risk_flags
            ),

            "reasons": list(
                contract.action.reasons
            ),

            "executable": contract.action.executable,
            "requires_review": (
                contract.action.requires_review
            ),
            "blocked": contract.action.blocked,
        },

        "result": risk_result_to_dict(
            contract.result
        ),
    }


# ============================================================
# SUMMARY
# ============================================================

def summarize_risk(
    contract: Optional[RiskContract],
) -> dict[str, Any]:

    if not isinstance(contract, RiskContract):
        return {
            "valid": False,
            "status": RiskResultStatus.INVALID.value,
            "decision": RiskDecision.UNKNOWN.value,
            "message": "Invalid risk contract",
        }

    result = contract.result

    return {
        "valid": contract.contract_valid,

        "request_id": contract.request.request_id,

        "market": contract.request.market,
        "instrument": contract.request.instrument,

        "pathway": result.pathway,
        "direction": result.direction,

        "status": result.status.value,
        "decision": result.decision.value,

        "risk_status": result.risk_status.value,
        "action_state": result.action_state.value,

        "risk_score": result.risk_score,
        "risk_confidence": result.risk_confidence,

        "completeness_score": (
            result.completeness_score
        ),

        "can_advance": result.can_advance,
        "requires_review": result.requires_review,
        "blocked": result.blocked,

        "restrictions": list(
            result.restrictions
        ),

        "risk_flags": list(
            result.risk_flags
        ),

        "lifecycle": (
            determine_risk_lifecycle(
                contract
            ).value
        ),

        "engine": RISK_GATE_ENGINE,
        "version": RISK_GATE_VERSION,
    }


def get_risk_authority_statement() -> str:

    return (
        "Risk Gate evaluates and controls risk conditions "
        "inside CAS. It does not generate market decisions, "
        "modify or override D13, replace Risk Authority, "
        "override CAS, place orders, or change positions."
    )


# ============================================================
# OPERATIONAL CHECK
# ============================================================

def risk_engine_operational() -> bool:

    if not risk_authority_integrity_ok():
        return False

    engine = get_risk_gate_engine()

    return (
        engine.engine_name
        == RISK_GATE_ENGINE
        and engine.version
        == RISK_GATE_VERSION
    )


def validate_risk(
    contract: Optional[RiskContract],
) -> bool:

    if not risk_engine_operational():
        return False

    return validate_risk_contract(
        contract
    )


def risk_snapshot(
    contract: Optional[RiskContract] = None,
) -> dict[str, Any]:

    health = get_risk_engine_health(
        contract
    )

    snapshot: dict[str, Any] = {
        "engine": RISK_GATE_ENGINE,
        "version": RISK_GATE_VERSION,

        "operational": (
            risk_engine_operational()
        ),

        "health": health.value,

        "authority_integrity": (
            risk_authority_integrity_ok()
        ),

        "authority_conflict": (
            risk_has_authority_conflict()
        ),

        "authority_statement": (
            get_risk_authority_statement()
        ),
    }

    if contract is not None:
        snapshot["risk"] = summarize_risk(
            contract
        )

    return snapshot


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    # Constants
    "RISK_GATE_ENGINE",
    "RISK_GATE_VERSION",

    # Enums
    "RiskStatus",
    "RiskDecision",
    "RiskMode",
    "RiskPriority",
    "RiskContractStatus",

    "RiskDataState",
    "RiskConsistency",
    "RiskReadiness",

    "RiskActionState",
    "RiskContractState",
    "RiskResultStatus",

    "RiskLifecycleState",
    "RiskEngineHealth",

    # Contracts
    "RiskRequest",
    "RiskReference",
    "RiskContractValidation",

    "RiskRequirements",
    "RiskAssessment",

    "RiskAction",
    "RiskResult",
    "RiskContract",

    "RiskAuditRecord",

    # Builders
    "build_risk_request",
    "build_risk_assessment",
    "build_risk_action",
    "build_risk_result",
    "build_risk_contract",
    "build_risk_audit",

    # Validation
    "validate_risk_numeric_inputs",
    "validate_risk_request",
    "validate_risk_action",
    "validate_risk_result",
    "validate_risk_contract",
    "validate_risk",

    # Evaluation
    "evaluate_risk_data_state",
    "evaluate_risk_consistency",
    "evaluate_risk_readiness",
    "evaluate_risk_requirements",

    # Scoring / condition
    "calculate_risk_completeness",
    "calculate_risk_score",
    "calculate_risk_confidence",
    "determine_risk_decision",
    "determine_risk_result_status",
    "determine_risk_status",
    "determine_risk_action_state",
    "determine_risk_contract_state",

    # Extraction
    "extract_risk_flags",
    "extract_risk_restrictions",

    # Engine
    "RiskGateEngine",
    "get_risk_gate_engine",
    "evaluate_risk",
    "check_risk",
    "review_risk",

    # Safety / readiness
    "risk_ready",
    "risk_can_advance",
    "risk_requires_review",
    "risk_is_blocked",
    "risk_is_restricted",
    "risk_is_safe_for_next_gate",
    "risk_status_of",
    "risk_decision_of",
    "risk_action_state_of",

    # Authority
    "risk_generates_market_decision",
    "risk_generates_alpha",
    "risk_modifies_d13",
    "risk_overrides_d13",
    "risk_replaces_risk_authority",
    "risk_overrides_risk_authority",
    "risk_overrides_cas",
    "risk_authorizes_execution",
    "risk_places_orders",
    "risk_changes_position",
    "risk_has_execution_authority",
    "risk_has_market_decision_authority",
    "risk_is_alpha_engine",
    "risk_authority_integrity_ok",
    "risk_has_authority_conflict",

    # Health / lifecycle
    "get_risk_engine_health",
    "get_risk_engine_info",
    "risk_integrity_ok",
    "determine_risk_lifecycle",
    "freeze_risk",
    "retain_risk",
    "reject_risk",
    "risk_engine_operational",

    # Serialization / reporting
    "risk_request_to_dict",
    "risk_assessment_to_dict",
    "risk_result_to_dict",
    "risk_contract_to_dict",
    "summarize_risk",
    "get_risk_authority_statement",
    "risk_snapshot",
]