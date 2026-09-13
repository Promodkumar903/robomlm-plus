# ============================================================
# ROBOMLM CAS — EXPOSURE GATE
# Part 1/5
#
# Role:
#   Evaluate whether the proposed pathway remains within the
#   applicable exposure context before CAS can advance it.
#
# Authority:
#   CAS internal exposure gate.
#
# MUST NOT:
#   - generate a market decision
#   - modify D13
#   - override D13
#   - replace Risk Authority
#   - override CAS
#   - execute an order
#   - change a position
#
# IMPORTANT:
#   Exposure quality is NOT winning probability / alpha.
#   Exposure Gate evaluates exposure conditions only.
#
# Pathway-aware:
#   NEW_ENTRY
#   ADD
#   REDUCE
#   EXIT
#   PROFIT_BOOK
#   HOLD
#   NEXT_SESSION_PLAN
#   WATCH
#   PREPARE
#   NO_ACTION
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Optional
from uuid import uuid4


EXPOSURE_GATE_ENGINE = "ROBOMLM_CAS_EXPOSURE_GATE"
EXPOSURE_GATE_VERSION = "1.0"


class ExposureStatus(str, Enum):
    NEW = "NEW"
    VALIDATING = "VALIDATING"
    ACCEPTABLE = "ACCEPTABLE"
    CONDITIONAL = "CONDITIONAL"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    EXCESSIVE = "EXCESSIVE"
    INVALID = "INVALID"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"


class ExposureDecision(str, Enum):
    ALLOW = "ALLOW"
    ALLOW_WITH_RESTRICTION = "ALLOW_WITH_RESTRICTION"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


class ExposureMode(str, Enum):
    ANALYSIS = "ANALYSIS"
    SIMULATION = "SIMULATION"
    AUTHORIZED_EXECUTION = "AUTHORIZED_EXECUTION"
    UNKNOWN = "UNKNOWN"


class ExposurePriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class ExposureContractStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


@dataclass(frozen=True)
class ExposureRequest:
    """
    Input contract for CAS exposure evaluation.

    ExposureRequest describes the proposed pathway and its
    current/projected exposure context.

    It does not authorize execution.
    """

    market: str
    instrument: str
    contract: Optional[str] = None

    user_id: Optional[str] = None
    account_id: Optional[str] = None
    plan_id: Optional[str] = None

    action: Optional[str] = None
    direction: Optional[str] = None

    mode: ExposureMode = ExposureMode.UNKNOWN

    strategy: Optional[str] = None
    timeframe: Optional[str] = None

    priority: ExposurePriority = ExposurePriority.MEDIUM

    current_exposure: Optional[float] = None
    proposed_exposure: Optional[float] = None
    projected_exposure: Optional[float] = None

    max_exposure: Optional[float] = None
    available_exposure: Optional[float] = None

    current_position_value: Optional[float] = None
    proposed_position_value: Optional[float] = None

    quantity: Optional[float] = None
    price: Optional[float] = None

    leverage: Optional[float] = None
    max_leverage: Optional[float] = None

    concentration: Optional[float] = None
    max_concentration: Optional[float] = None

    portfolio_exposure: Optional[float] = None
    portfolio_max_exposure: Optional[float] = None

    correlated_exposure: Optional[float] = None
    correlated_max_exposure: Optional[float] = None

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    request_id: str = field(
        default_factory=lambda: str(uuid4())
    )


@dataclass(frozen=True)
class ExposureReference:
    request_id: str

    user_id: Optional[str]
    account_id: Optional[str]
    plan_id: Optional[str]

    market: str
    instrument: str
    contract: Optional[str]

    action: Optional[str]
    direction: Optional[str]

    mode: ExposureMode
    strategy: Optional[str]
    timeframe: Optional[str]

    timestamp: datetime

    status: ExposureStatus
    decision: ExposureDecision

    exposure_score: float
    exposure_confidence: float

    restrictions: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class ExposureContractValidation:
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


def _eg_read_value(
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


def _eg_text(
    value: Any,
) -> Optional[str]:

    if value is None:
        return None

    text = str(value).strip()

    return text if text else None


def _eg_enum(
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


def _eg_number(
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

    if number in (
        float("inf"),
        float("-inf"),
    ):
        return None

    return number


def _eg_bool(
    value: Any,
) -> bool:

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


def _eg_timestamp(
    value: Any,
) -> datetime:

    if isinstance(value, datetime):

        if value.tzinfo is None:
            return value.replace(
                tzinfo=timezone.utc
            )

        return value.astimezone(
            timezone.utc
        )

    return datetime.now(
        timezone.utc
    )


def build_exposure_request(
    source: Any = None,
    **kwargs: Any,
) -> ExposureRequest:

    def value(
        key: str,
        default: Any = None,
    ) -> Any:

        return kwargs.get(
            key,
            _eg_read_value(
                source,
                key,
                default,
            ),
        )

    market = _eg_text(
        value("market")
    ) or ""

    instrument = _eg_text(
        value("instrument")
    ) or ""

    mode = _eg_enum(
        value("mode"),
        ExposureMode,
        ExposureMode.UNKNOWN,
    )

    priority = _eg_enum(
        value("priority"),
        ExposurePriority,
        ExposurePriority.MEDIUM,
    )

    metadata = value(
        "metadata",
        {},
    )

    if not isinstance(
        metadata,
        Mapping,
    ):
        metadata = {}

    numeric_fields = (
        "current_exposure",
        "proposed_exposure",
        "projected_exposure",
        "max_exposure",
        "available_exposure",

        "current_position_value",
        "proposed_position_value",

        "quantity",
        "price",

        "leverage",
        "max_leverage",

        "concentration",
        "max_concentration",

        "portfolio_exposure",
        "portfolio_max_exposure",

        "correlated_exposure",
        "correlated_max_exposure",
    )

    numeric_values = {
        field_name: _eg_number(
            value(field_name)
        )
        for field_name in numeric_fields
    }

    return ExposureRequest(
        market=market,
        instrument=instrument,

        contract=_eg_text(
            value("contract")
        ),

        user_id=_eg_text(
            value("user_id")
        ),

        account_id=_eg_text(
            value("account_id")
        ),

        plan_id=_eg_text(
            value("plan_id")
        ),

        action=_eg_text(
            value("action")
        ),

        direction=_eg_text(
            value("direction")
        ),

        mode=mode,

        strategy=_eg_text(
            value("strategy")
        ),

        timeframe=_eg_text(
            value("timeframe")
        ),

        priority=priority,

        current_exposure=(
            numeric_values[
                "current_exposure"
            ]
        ),

        proposed_exposure=(
            numeric_values[
                "proposed_exposure"
            ]
        ),

        projected_exposure=(
            numeric_values[
                "projected_exposure"
            ]
        ),

        max_exposure=(
            numeric_values[
                "max_exposure"
            ]
        ),

        available_exposure=(
            numeric_values[
                "available_exposure"
            ]
        ),

        current_position_value=(
            numeric_values[
                "current_position_value"
            ]
        ),

        proposed_position_value=(
            numeric_values[
                "proposed_position_value"
            ]
        ),

        quantity=(
            numeric_values[
                "quantity"
            ]
        ),

        price=(
            numeric_values[
                "price"
            ]
        ),

        leverage=(
            numeric_values[
                "leverage"
            ]
        ),

        max_leverage=(
            numeric_values[
                "max_leverage"
            ]
        ),

        concentration=(
            numeric_values[
                "concentration"
            ]
        ),

        max_concentration=(
            numeric_values[
                "max_concentration"
            ]
        ),

        portfolio_exposure=(
            numeric_values[
                "portfolio_exposure"
            ]
        ),

        portfolio_max_exposure=(
            numeric_values[
                "portfolio_max_exposure"
            ]
        ),

        correlated_exposure=(
            numeric_values[
                "correlated_exposure"
            ]
        ),

        correlated_max_exposure=(
            numeric_values[
                "correlated_max_exposure"
            ]
        ),

        metadata=dict(metadata),

        request_id=(
            _eg_text(
                value("request_id")
            )
            or str(uuid4())
        ),
    )


def validate_exposure_numeric_inputs(
    request: Optional[ExposureRequest],
) -> tuple[
    bool,
    tuple[str, ...],
    tuple[str, ...],
]:

    if not isinstance(
        request,
        ExposureRequest,
    ):
        return (
            False,
            ("Invalid ExposureRequest",),
            (),
        )

    errors: list[str] = []
    warnings: list[str] = []

    numeric_fields = {
        "current_exposure":
            request.current_exposure,

        "proposed_exposure":
            request.proposed_exposure,

        "projected_exposure":
            request.projected_exposure,

        "max_exposure":
            request.max_exposure,

        "available_exposure":
            request.available_exposure,

        "current_position_value":
            request.current_position_value,

        "proposed_position_value":
            request.proposed_position_value,

        "quantity":
            request.quantity,

        "price":
            request.price,

        "leverage":
            request.leverage,

        "max_leverage":
            request.max_leverage,

        "concentration":
            request.concentration,

        "max_concentration":
            request.max_concentration,

        "portfolio_exposure":
            request.portfolio_exposure,

        "portfolio_max_exposure":
            request.portfolio_max_exposure,

        "correlated_exposure":
            request.correlated_exposure,

        "correlated_max_exposure":
            request.correlated_max_exposure,
    }

    for name, value in numeric_fields.items():

        if value is None:
            continue

        if not isinstance(
            value,
            (int, float),
        ):
            errors.append(
                f"{name} must be numeric"
            )
            continue

        if value != value:
            errors.append(
                f"{name} cannot be NaN"
            )
            continue

        if value in (
            float("inf"),
            float("-inf"),
        ):
            errors.append(
                f"{name} must be finite"
            )

    non_negative_fields = (
        "current_exposure",
        "proposed_exposure",
        "projected_exposure",
        "max_exposure",
        "available_exposure",

        "current_position_value",
        "proposed_position_value",

        "quantity",
        "price",

        "leverage",
        "max_leverage",

        "concentration",
        "max_concentration",

        "portfolio_exposure",
        "portfolio_max_exposure",

        "correlated_exposure",
        "correlated_max_exposure",
    )

    for name in non_negative_fields:

        value = getattr(
            request,
            name,
        )

        if (
            value is not None
            and value < 0
        ):
            errors.append(
                f"{name} cannot be negative"
            )

    if (
        request.max_exposure is not None
        and request.projected_exposure is not None
        and request.projected_exposure
        > request.max_exposure
    ):
        warnings.append(
            "Projected exposure exceeds supplied maximum"
        )

    if (
        request.available_exposure is not None
        and request.proposed_exposure is not None
        and request.proposed_exposure
        > request.available_exposure
    ):
        warnings.append(
            "Proposed exposure exceeds available exposure"
        )

    if (
        request.max_leverage is not None
        and request.leverage is not None
        and request.leverage
        > request.max_leverage
    ):
        warnings.append(
            "Leverage exceeds supplied maximum"
        )

    if (
        request.max_concentration is not None
        and request.concentration is not None
        and request.concentration
        > request.max_concentration
    ):
        warnings.append(
            "Concentration exceeds supplied maximum"
        )

    if (
        request.portfolio_max_exposure is not None
        and request.portfolio_exposure is not None
        and request.portfolio_exposure
        > request.portfolio_max_exposure
    ):
        warnings.append(
            "Portfolio exposure exceeds maximum"
        )

    if (
        request.correlated_max_exposure is not None
        and request.correlated_exposure is not None
        and request.correlated_exposure
        > request.correlated_max_exposure
    ):
        warnings.append(
            "Correlated exposure exceeds maximum"
        )

    return (
        len(errors) == 0,
        tuple(errors),
        tuple(warnings),
    )


def validate_exposure_request(
    request: Optional[ExposureRequest],
) -> ExposureContractValidation:

    if not isinstance(
        request,
        ExposureRequest,
    ):
        return ExposureContractValidation(
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

            errors=(
                "Invalid ExposureRequest",
            ),
        )

    errors: list[str] = []
    warnings: list[str] = []

    market_available = bool(
        _eg_text(request.market)
    )

    instrument_available = bool(
        _eg_text(request.instrument)
    )

    user_available = bool(
        _eg_text(request.user_id)
    )

    account_available = bool(
        _eg_text(request.account_id)
    )

    plan_available = bool(
        _eg_text(request.plan_id)
    )

    action_available = bool(
        _eg_text(request.action)
    )

    direction_available = bool(
        _eg_text(request.direction)
    )

    mode_valid = (
        request.mode
        != ExposureMode.UNKNOWN
    )

    metadata_valid = isinstance(
        request.metadata,
        Mapping,
    )

    (
        numeric_valid,
        numeric_errors,
        numeric_warnings,
    ) = validate_exposure_numeric_inputs(
        request
    )

    if not market_available:
        errors.append(
            "Market is required"
        )

    if not instrument_available:
        errors.append(
            "Instrument is required"
        )

    if not user_available:
        errors.append(
            "User identity is required"
        )

    if not account_available:
        errors.append(
            "Account identity is required"
        )

    if not action_available:
        errors.append(
            "Exposure pathway/action is required"
        )

    if not mode_valid:
        errors.append(
            "Valid exposure mode is required"
        )

    if not direction_available:
        warnings.append(
            "Direction is missing; pathway may not require direction"
        )

    if not plan_available:
        warnings.append(
            "Plan identity is missing"
        )

    if not metadata_valid:
        errors.append(
            "Metadata must be a mapping"
        )

    errors.extend(
        numeric_errors
    )

    warnings.extend(
        numeric_warnings
    )

    return ExposureContractValidation(
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

        errors=tuple(
            dict.fromkeys(errors)
        ),

        warnings=tuple(
            dict.fromkeys(warnings)
        ),
    )
# ============================================================
# ROBOMLM CAS — EXPOSURE GATE
# Part 2/5
#
# Requirements • Data State • Consistency • Readiness
# Flags • Restrictions • Exposure Assessment
# ============================================================


class ExposureDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    UNKNOWN = "UNKNOWN"


class ExposureConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONFLICTING = "CONFLICTING"
    INSUFFICIENT = "INSUFFICIENT"
    UNKNOWN = "UNKNOWN"


class ExposureReadiness(str, Enum):
    READY = "READY"
    CONDITIONAL = "CONDITIONAL"
    NOT_READY = "NOT_READY"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ExposureRequirements:
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

    current_exposure_available: bool
    proposed_exposure_available: bool
    projected_exposure_available: bool

    exposure_limit_available: bool
    available_exposure_available: bool

    position_value_available: bool
    leverage_context_available: bool
    concentration_context_available: bool

    portfolio_exposure_available: bool
    correlated_exposure_available: bool

    data_state: ExposureDataState
    consistency: ExposureConsistency
    readiness: ExposureReadiness

    completeness_score: float

    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class ExposureAssessment:
    readiness: ExposureReadiness
    data_state: ExposureDataState
    consistency: ExposureConsistency

    exposure_score: float
    confidence_score: float
    completeness_score: float

    exposure_flags: tuple[str, ...] = ()
    restrictions: tuple[str, ...] = ()

    strengths: tuple[str, ...] = ()
    weaknesses: tuple[str, ...] = ()

    rationale: str = ""


def evaluate_exposure_data_state(
    request: Optional[ExposureRequest],
) -> ExposureDataState:

    if not isinstance(
        request,
        ExposureRequest,
    ):
        return ExposureDataState.MISSING

    components = (
        bool(_eg_text(request.market)),
        bool(_eg_text(request.instrument)),
        bool(_eg_text(request.user_id)),
        bool(_eg_text(request.account_id)),
        bool(_eg_text(request.action)),
        request.mode != ExposureMode.UNKNOWN,

        request.current_exposure is not None,
        request.proposed_exposure is not None,
        request.projected_exposure is not None,
        request.max_exposure is not None,
    )

    available = sum(
        1
        for value in components
        if value
    )

    if available == len(components):
        return ExposureDataState.COMPLETE

    if available == 0:
        return ExposureDataState.MISSING

    if available >= len(components) // 2:
        return ExposureDataState.PARTIAL

    return ExposureDataState.UNKNOWN


def evaluate_exposure_consistency(
    request: Optional[ExposureRequest],
) -> ExposureConsistency:

    if not isinstance(
        request,
        ExposureRequest,
    ):
        return ExposureConsistency.INSUFFICIENT

    metadata = request.metadata

    if not isinstance(
        metadata,
        Mapping,
    ):
        return ExposureConsistency.CONFLICTING

    conflict_keys = (
        "conflict",
        "conflicting",
        "exposure_conflict",
        "account_exposure_conflict",
        "portfolio_exposure_conflict",
        "correlated_exposure_conflict",
        "concentration_conflict",
        "leverage_conflict",
    )

    for key in conflict_keys:

        if _eg_bool(
            metadata.get(key)
        ):
            return ExposureConsistency.CONFLICTING

    if (
        request.current_exposure is not None
        and request.projected_exposure is not None
    ):
        if request.projected_exposure < 0:
            return ExposureConsistency.CONFLICTING

    if (
        request.max_exposure is not None
        and request.max_exposure < 0
    ):
        return ExposureConsistency.CONFLICTING

    if (
        request.available_exposure is not None
        and request.available_exposure < 0
    ):
        return ExposureConsistency.CONFLICTING

    if (
        request.max_leverage is not None
        and request.leverage is not None
        and request.leverage < 0
    ):
        return ExposureConsistency.CONFLICTING

    if (
        request.max_concentration is not None
        and request.concentration is not None
        and request.concentration < 0
    ):
        return ExposureConsistency.CONFLICTING

    # A projected exposure lower than current exposure is valid
    # for REDUCE / EXIT / PROFIT_BOOK pathways and must not be
    # treated as an inconsistency.
    #
    # Therefore pathway semantics matter here.

    action = (
        _eg_text(request.action)
        or ""
    ).upper()

    reduction_pathways = {
        "REDUCE",
        "EXIT",
        "PROFIT_BOOK",
        "PARTIAL_EXIT",
        "CLOSE",
    }

    expansion_pathways = {
        "NEW_ENTRY",
        "ENTRY",
        "ADD",
        "SCALE_IN",
    }

    if (
        action in expansion_pathways
        and request.proposed_exposure is not None
        and request.current_exposure is not None
        and request.proposed_exposure
        < 0
    ):
        return ExposureConsistency.CONFLICTING

    if (
        action in reduction_pathways
        and request.proposed_exposure is not None
        and request.proposed_exposure < 0
    ):
        return ExposureConsistency.CONFLICTING

    return ExposureConsistency.CONSISTENT


def calculate_exposure_completeness(
    request: Optional[ExposureRequest],
) -> float:

    if not isinstance(
        request,
        ExposureRequest,
    ):
        return 0.0

    checks = (
        bool(_eg_text(request.market)),
        bool(_eg_text(request.instrument)),
        bool(_eg_text(request.user_id)),
        bool(_eg_text(request.account_id)),
        bool(_eg_text(request.plan_id)),
        bool(_eg_text(request.action)),
        bool(_eg_text(request.direction)),

        request.mode != ExposureMode.UNKNOWN,

        bool(_eg_text(request.strategy)),
        bool(_eg_text(request.timeframe)),

        request.current_exposure is not None,
        request.proposed_exposure is not None,
        request.projected_exposure is not None,

        request.max_exposure is not None,
        request.available_exposure is not None,

        request.current_position_value is not None,
        request.proposed_position_value is not None,

        request.quantity is not None,
        request.price is not None,

        request.leverage is not None,
        request.max_leverage is not None,

        request.concentration is not None,
        request.max_concentration is not None,

        request.portfolio_exposure is not None,
        request.portfolio_max_exposure is not None,

        request.correlated_exposure is not None,
        request.correlated_max_exposure is not None,
    )

    return round(
        (
            sum(
                1
                for value in checks
                if value
            )
            / len(checks)
        ) * 100.0,
        2,
    )


def evaluate_exposure_readiness(
    request: Optional[ExposureRequest],
    consistency: Optional[ExposureConsistency] = None,
) -> ExposureReadiness:

    if not isinstance(
        request,
        ExposureRequest,
    ):
        return ExposureReadiness.NOT_READY

    validation = validate_exposure_request(
        request
    )

    if not validation.valid:
        return ExposureReadiness.NOT_READY

    if consistency is None:
        consistency = evaluate_exposure_consistency(
            request
        )

    if consistency == ExposureConsistency.CONFLICTING:
        return ExposureReadiness.NOT_READY

    if consistency == ExposureConsistency.INSUFFICIENT:
        return ExposureReadiness.CONDITIONAL

    completeness = calculate_exposure_completeness(
        request
    )

    if completeness >= 85.0:
        return ExposureReadiness.READY

    if completeness >= 50.0:
        return ExposureReadiness.CONDITIONAL

    return ExposureReadiness.NOT_READY


def evaluate_exposure_requirements(
    request: Optional[ExposureRequest],
) -> ExposureRequirements:

    validation = validate_exposure_request(
        request
    )

    if not isinstance(
        request,
        ExposureRequest,
    ):
        return ExposureRequirements(
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

            current_exposure_available=False,
            proposed_exposure_available=False,
            projected_exposure_available=False,

            exposure_limit_available=False,
            available_exposure_available=False,

            position_value_available=False,
            leverage_context_available=False,
            concentration_context_available=False,

            portfolio_exposure_available=False,
            correlated_exposure_available=False,

            data_state=ExposureDataState.MISSING,
            consistency=ExposureConsistency.INSUFFICIENT,
            readiness=ExposureReadiness.NOT_READY,

            completeness_score=0.0,

            warnings=("Invalid exposure request",),
        )

    data_state = evaluate_exposure_data_state(
        request
    )

    consistency = evaluate_exposure_consistency(
        request
    )

    completeness = calculate_exposure_completeness(
        request
    )

    readiness = evaluate_exposure_readiness(
        request,
        consistency,
    )

    warnings = list(
        validation.warnings
    )

    if not _eg_text(request.strategy):
        warnings.append(
            "Strategy information is missing"
        )

    if not _eg_text(request.timeframe):
        warnings.append(
            "Timeframe information is missing"
        )

    current_exposure_available = (
        request.current_exposure is not None
    )

    proposed_exposure_available = (
        request.proposed_exposure is not None
    )

    projected_exposure_available = (
        request.projected_exposure is not None
    )

    exposure_limit_available = (
        request.max_exposure is not None
    )

    available_exposure_available = (
        request.available_exposure is not None
    )

    position_value_available = (
        request.current_position_value is not None
        or request.proposed_position_value is not None
    )

    leverage_context_available = (
        request.leverage is not None
        or request.max_leverage is not None
    )

    concentration_context_available = (
        request.concentration is not None
        or request.max_concentration is not None
    )

    portfolio_exposure_available = (
        request.portfolio_exposure is not None
        or request.portfolio_max_exposure is not None
    )

    correlated_exposure_available = (
        request.correlated_exposure is not None
        or request.correlated_max_exposure is not None
    )

    if not current_exposure_available:
        warnings.append(
            "Current exposure context is unavailable"
        )

    if not proposed_exposure_available:
        warnings.append(
            "Proposed exposure context is unavailable"
        )

    if not projected_exposure_available:
        warnings.append(
            "Projected exposure context is unavailable"
        )

    if not exposure_limit_available:
        warnings.append(
            "Explicit exposure limit is unavailable"
        )

    if not available_exposure_available:
        warnings.append(
            "Available exposure capacity is unavailable"
        )

    if not position_value_available:
        warnings.append(
            "Position value context is unavailable"
        )

    if not leverage_context_available:
        warnings.append(
            "Leverage context is unavailable"
        )

    if not concentration_context_available:
        warnings.append(
            "Concentration context is unavailable"
        )

    if not portfolio_exposure_available:
        warnings.append(
            "Portfolio exposure context is unavailable"
        )

    if not correlated_exposure_available:
        warnings.append(
            "Correlated exposure context is unavailable"
        )

    return ExposureRequirements(
        request_valid=validation.valid,

        market_available=validation.market_available,
        instrument_available=validation.instrument_available,

        user_available=validation.user_available,
        account_available=validation.account_available,
        plan_available=validation.plan_available,

        action_available=validation.action_available,
        direction_available=validation.direction_available,

        mode_defined=(
            request.mode
            != ExposureMode.UNKNOWN
        ),

        strategy_available=bool(
            _eg_text(request.strategy)
        ),

        timeframe_available=bool(
            _eg_text(request.timeframe)
        ),

        current_exposure_available=(
            current_exposure_available
        ),

        proposed_exposure_available=(
            proposed_exposure_available
        ),

        projected_exposure_available=(
            projected_exposure_available
        ),

        exposure_limit_available=(
            exposure_limit_available
        ),

        available_exposure_available=(
            available_exposure_available
        ),

        position_value_available=(
            position_value_available
        ),

        leverage_context_available=(
            leverage_context_available
        ),

        concentration_context_available=(
            concentration_context_available
        ),

        portfolio_exposure_available=(
            portfolio_exposure_available
        ),

        correlated_exposure_available=(
            correlated_exposure_available
        ),

        data_state=data_state,
        consistency=consistency,
        readiness=readiness,

        completeness_score=completeness,

        warnings=tuple(
            dict.fromkeys(warnings)
        ),
    )


def extract_exposure_flags(
    request: Optional[ExposureRequest],
) -> tuple[str, ...]:

    if not isinstance(
        request,
        ExposureRequest,
    ):
        return ("INVALID_REQUEST",)

    flags: list[str] = []

    metadata = request.metadata

    explicit_flags = metadata.get(
        "exposure_flags",
        (),
    )

    if isinstance(
        explicit_flags,
        str,
    ):
        explicit_flags = (
            explicit_flags,
        )

    if isinstance(
        explicit_flags,
        (list, tuple, set),
    ):
        for flag in explicit_flags:

            text = _eg_text(flag)

            if text:
                flags.append(
                    text.upper()
                )

    if (
        request.max_exposure is not None
        and request.projected_exposure is not None
        and request.projected_exposure
        > request.max_exposure
    ):
        flags.append(
            "EXPOSURE_LIMIT_BREACH"
        )

    if (
        request.available_exposure is not None
        and request.proposed_exposure is not None
        and request.proposed_exposure
        > request.available_exposure
    ):
        flags.append(
            "EXPOSURE_CAPACITY_BREACH"
        )

    if (
        request.max_leverage is not None
        and request.leverage is not None
        and request.leverage
        > request.max_leverage
    ):
        flags.append(
            "LEVERAGE_LIMIT_BREACH"
        )

    if (
        request.max_concentration is not None
        and request.concentration is not None
        and request.concentration
        > request.max_concentration
    ):
        flags.append(
            "CONCENTRATION_LIMIT_BREACH"
        )

    if (
        request.portfolio_max_exposure is not None
        and request.portfolio_exposure is not None
        and request.portfolio_exposure
        > request.portfolio_max_exposure
    ):
        flags.append(
            "PORTFOLIO_EXPOSURE_BREACH"
        )

    if (
        request.correlated_max_exposure is not None
        and request.correlated_exposure is not None
        and request.correlated_exposure
        > request.correlated_max_exposure
    ):
        flags.append(
            "CORRELATED_EXPOSURE_BREACH"
        )

    if _eg_bool(
        metadata.get("stale_data")
    ):
        flags.append(
            "STALE_DATA"
        )

    if _eg_bool(
        metadata.get("missing_data")
    ):
        flags.append(
            "MISSING_DATA"
        )

    if _eg_bool(
        metadata.get("concentration_risk")
    ):
        flags.append(
            "CONCENTRATION_RISK"
        )

    if _eg_bool(
        metadata.get("correlation_risk")
    ):
        flags.append(
            "CORRELATION_RISK"
        )

    if _eg_bool(
        metadata.get("portfolio_risk")
    ):
        flags.append(
            "PORTFOLIO_RISK"
        )

    return tuple(
        dict.fromkeys(flags)
    )


def extract_exposure_restrictions(
    request: Optional[ExposureRequest],
) -> tuple[str, ...]:

    if not isinstance(
        request,
        ExposureRequest,
    ):
        return ("INVALID_REQUEST",)

    restrictions: list[str] = []

    metadata = request.metadata

    if _eg_bool(
        metadata.get("reduce_only")
    ):
        restrictions.append(
            "REDUCE_ONLY"
        )

    if _eg_bool(
        metadata.get("no_new_exposure")
    ):
        restrictions.append(
            "NO_NEW_EXPOSURE"
        )

    if _eg_bool(
        metadata.get("exposure_limited")
    ):
        restrictions.append(
            "EXPOSURE_LIMITED"
        )

    if _eg_bool(
        metadata.get("position_size_limited")
    ):
        restrictions.append(
            "POSITION_SIZE_LIMITED"
        )

    if _eg_bool(
        metadata.get("leverage_limited")
    ):
        restrictions.append(
            "LEVERAGE_LIMITED"
        )

    if _eg_bool(
        metadata.get("concentration_limited")
    ):
        restrictions.append(
            "CONCENTRATION_LIMITED"
        )

    if _eg_bool(
        metadata.get("portfolio_limited")
    ):
        restrictions.append(
            "PORTFOLIO_LIMITED"
        )

    if _eg_bool(
        metadata.get("correlation_limited")
    ):
        restrictions.append(
            "CORRELATION_LIMITED"
        )

    if _eg_bool(
        metadata.get("closing_window_restricted")
    ):
        restrictions.append(
            "CLOSING_WINDOW_RESTRICTED"
        )

    return tuple(
        dict.fromkeys(restrictions)
    )


def calculate_exposure_score(
    request: Optional[ExposureRequest],
    requirements: Optional[ExposureRequirements] = None,
) -> float:

    if not isinstance(
        request,
        ExposureRequest,
    ):
        return 0.0

    if requirements is None:
        requirements = evaluate_exposure_requirements(
            request
        )

    score = 0.0

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

    if requirements.current_exposure_available:
        score += 10.0

    if requirements.proposed_exposure_available:
        score += 10.0

    if requirements.projected_exposure_available:
        score += 10.0

    if requirements.exposure_limit_available:
        score += 5.0

    if requirements.available_exposure_available:
        score += 5.0

    if requirements.position_value_available:
        score += 5.0

    flags = extract_exposure_flags(
        request
    )

    hard_breach_flags = {
        "EXPOSURE_LIMIT_BREACH",
        "EXPOSURE_CAPACITY_BREACH",
        "LEVERAGE_LIMIT_BREACH",
        "CONCENTRATION_LIMIT_BREACH",
        "PORTFOLIO_EXPOSURE_BREACH",
        "CORRELATED_EXPOSURE_BREACH",
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

    if "CONCENTRATION_RISK" in flags:
        score *= 0.80

    if "CORRELATION_RISK" in flags:
        score *= 0.85

    if "PORTFOLIO_RISK" in flags:
        score *= 0.85

    if (
        requirements.consistency
        == ExposureConsistency.CONFLICTING
    ):
        return 0.0

    if (
        requirements.consistency
        == ExposureConsistency.INSUFFICIENT
    ):
        score *= 0.70

    return round(
        max(
            0.0,
            min(
                100.0,
                score,
            ),
        ),
        2,
    )


def calculate_exposure_confidence(
    requirements: ExposureRequirements,
    exposure_score: float,
) -> float:

    if (
        requirements.consistency
        == ExposureConsistency.CONFLICTING
    ):
        return 0.0

    confidence = (
        requirements.completeness_score * 0.60
        + exposure_score * 0.40
    )

    if (
        requirements.consistency
        == ExposureConsistency.CONSISTENT
    ):
        confidence += 5.0

    elif (
        requirements.consistency
        == ExposureConsistency.INSUFFICIENT
    ):
        confidence -= 15.0

    return round(
        max(
            0.0,
            min(
                100.0,
                confidence,
            ),
        ),
        2,
    )


def build_exposure_assessment(
    request: Optional[ExposureRequest],
    requirements: Optional[ExposureRequirements] = None,
) -> ExposureAssessment:

    if not isinstance(
        request,
        ExposureRequest,
    ):
        return ExposureAssessment(
            readiness=ExposureReadiness.NOT_READY,
            data_state=ExposureDataState.MISSING,
            consistency=ExposureConsistency.INSUFFICIENT,

            exposure_score=0.0,
            confidence_score=0.0,
            completeness_score=0.0,

            exposure_flags=(
                "INVALID_REQUEST",
            ),

            weaknesses=(
                "Invalid exposure request",
            ),

            rationale=(
                "Exposure cannot be evaluated "
                "from an invalid request."
            ),
        )

    if requirements is None:
        requirements = evaluate_exposure_requirements(
            request
        )

    exposure_score = calculate_exposure_score(
        request,
        requirements,
    )

    confidence_score = calculate_exposure_confidence(
        requirements,
        exposure_score,
    )

    flags = extract_exposure_flags(
        request
    )

    restrictions = extract_exposure_restrictions(
        request
    )

    strengths: list[str] = []
    weaknesses: list[str] = []

    if requirements.current_exposure_available:
        strengths.append(
            "Current exposure context available"
        )

    if requirements.proposed_exposure_available:
        strengths.append(
            "Proposed exposure context available"
        )

    if requirements.projected_exposure_available:
        strengths.append(
            "Projected exposure context available"
        )

    if requirements.exposure_limit_available:
        strengths.append(
            "Exposure limit context available"
        )

    if requirements.portfolio_exposure_available:
        strengths.append(
            "Portfolio exposure context available"
        )

    if requirements.correlated_exposure_available:
        strengths.append(
            "Correlated exposure context available"
        )

    if flags:
        weaknesses.append(
            "Exposure condition flags detected"
        )

    if restrictions:
        weaknesses.append(
            "One or more exposure restrictions detected"
        )

    if (
        requirements.consistency
        == ExposureConsistency.CONFLICTING
    ):
        weaknesses.append(
            "Exposure context contains conflict"
        )

    if not requirements.exposure_limit_available:
        weaknesses.append(
            "Explicit exposure limit unavailable"
        )

    if not requirements.portfolio_exposure_available:
        weaknesses.append(
            "Portfolio exposure context unavailable"
        )

    if requirements.readiness == ExposureReadiness.READY:
        rationale = (
            "Exposure context is sufficiently complete "
            "and structurally consistent for CAS "
            "exposure-gate evaluation."
        )

    elif requirements.readiness == ExposureReadiness.CONDITIONAL:
        rationale = (
            "Exposure context is partially complete "
            "and requires conditional handling or "
            "additional exposure validation."
        )

    elif (
        requirements.consistency
        == ExposureConsistency.CONFLICTING
    ):
        rationale = (
            "Exposure evaluation is blocked because "
            "the supplied exposure context contains "
            "a conflict."
        )

    else:
        rationale = (
            "Exposure cannot currently be established "
            "with sufficient structural confidence."
        )

    return ExposureAssessment(
        readiness=requirements.readiness,
        data_state=requirements.data_state,
        consistency=requirements.consistency,

        exposure_score=exposure_score,
        confidence_score=confidence_score,
        completeness_score=(
            requirements.completeness_score
        ),

        exposure_flags=flags,
        restrictions=restrictions,

        strengths=tuple(strengths),
        weaknesses=tuple(weaknesses),

        rationale=rationale,
    )
# ============================================================
# ROBOMLM CAS — EXPOSURE GATE
# Part 3/5
#
# Result Contract • Action State • Engine
# ============================================================


class ExposureActionState(str, Enum):
    NONE = "NONE"
    EVALUATE = "EVALUATE"
    ALLOW = "ALLOW"
    RESTRICT = "RESTRICT"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"
    INVALIDATE = "INVALIDATE"


class ExposureContractState(str, Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


class ExposureResultStatus(str, Enum):
    ALLOWED = "ALLOWED"
    RESTRICTED = "RESTRICTED"
    REVIEW = "REVIEW"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


@dataclass(frozen=True)
class ExposureAction:
    """
    Action produced by the Exposure Gate.

    This is an exposure-control action, not a market
    decision or trading signal.
    """

    action_state: ExposureActionState
    decision: ExposureDecision

    pathway: Optional[str]
    direction: Optional[str]

    restrictions: tuple[str, ...] = ()
    exposure_flags: tuple[str, ...] = ()

    reasons: tuple[str, ...] = ()

    executable: bool = False
    requires_review: bool = False
    blocked: bool = False


@dataclass(frozen=True)
class ExposureResult:
    """
    Final normalized Exposure Gate result.

    ExposureResult controls exposure progression inside CAS.
    It does not place orders and does not replace D13,
    Risk Authority, or CAS authority.
    """

    request_id: str

    status: ExposureResultStatus
    decision: ExposureDecision

    exposure_status: ExposureStatus
    action_state: ExposureActionState

    exposure_score: float
    exposure_confidence: float
    completeness_score: float

    restrictions: tuple[str, ...] = ()
    exposure_flags: tuple[str, ...] = ()

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
class ExposureContract:
    """
    Complete Exposure Gate contract.

    request → requirements → assessment → action → result
    """

    request: ExposureRequest

    requirements: ExposureRequirements
    assessment: ExposureAssessment

    action: ExposureAction
    result: ExposureResult

    contract_state: ExposureContractState

    contract_valid: bool

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


def determine_exposure_result_status(
    decision: ExposureDecision,
) -> ExposureResultStatus:

    if decision == ExposureDecision.ALLOW:
        return ExposureResultStatus.ALLOWED

    if decision == ExposureDecision.ALLOW_WITH_RESTRICTION:
        return ExposureResultStatus.RESTRICTED

    if decision == ExposureDecision.REVIEW_REQUIRED:
        return ExposureResultStatus.REVIEW

    if decision == ExposureDecision.BLOCK:
        return ExposureResultStatus.BLOCKED

    return ExposureResultStatus.INVALID


def determine_exposure_status(
    assessment: ExposureAssessment,
    decision: ExposureDecision,
) -> ExposureStatus:

    if decision == ExposureDecision.BLOCK:
        return ExposureStatus.BLOCKED

    if decision == ExposureDecision.REVIEW_REQUIRED:
        return ExposureStatus.REVIEW_REQUIRED

    if decision == ExposureDecision.ALLOW_WITH_RESTRICTION:
        return ExposureStatus.CONDITIONAL

    if decision == ExposureDecision.ALLOW:

        if assessment.readiness == ExposureReadiness.READY:
            return ExposureStatus.ACCEPTABLE

        if assessment.readiness == ExposureReadiness.CONDITIONAL:
            return ExposureStatus.CONDITIONAL

        return ExposureStatus.UNKNOWN

    if (
        assessment.consistency
        == ExposureConsistency.CONFLICTING
    ):
        return ExposureStatus.INVALID

    return ExposureStatus.UNKNOWN


def determine_exposure_action_state(
    decision: ExposureDecision,
) -> ExposureActionState:

    if decision == ExposureDecision.ALLOW:
        return ExposureActionState.ALLOW

    if decision == ExposureDecision.ALLOW_WITH_RESTRICTION:
        return ExposureActionState.RESTRICT

    if decision == ExposureDecision.REVIEW_REQUIRED:
        return ExposureActionState.REVIEW

    if decision == ExposureDecision.BLOCK:
        return ExposureActionState.BLOCK

    return ExposureActionState.INVALIDATE


def determine_exposure_decision(
    request: Optional[ExposureRequest],
    assessment: Optional[ExposureAssessment] = None,
) -> ExposureDecision:

    if not isinstance(
        request,
        ExposureRequest,
    ):
        return ExposureDecision.UNKNOWN

    if assessment is None:
        assessment = build_exposure_assessment(
            request
        )

    if (
        assessment.consistency
        == ExposureConsistency.CONFLICTING
    ):
        return ExposureDecision.BLOCK

    if assessment.exposure_score <= 0.0:
        return ExposureDecision.BLOCK

    hard_flags = {
        "EXPOSURE_LIMIT_BREACH",
        "EXPOSURE_CAPACITY_BREACH",
        "LEVERAGE_LIMIT_BREACH",
        "CONCENTRATION_LIMIT_BREACH",
        "PORTFOLIO_EXPOSURE_BREACH",
        "CORRELATED_EXPOSURE_BREACH",
    }

    if any(
        flag in hard_flags
        for flag in assessment.exposure_flags
    ):
        return ExposureDecision.BLOCK

    if (
        assessment.readiness
        == ExposureReadiness.NOT_READY
    ):
        return ExposureDecision.REVIEW_REQUIRED

    if assessment.exposure_score < 50.0:
        return ExposureDecision.REVIEW_REQUIRED

    if assessment.restrictions:
        return ExposureDecision.ALLOW_WITH_RESTRICTION

    if assessment.exposure_flags:
        return ExposureDecision.ALLOW_WITH_RESTRICTION

    if (
        assessment.readiness
        == ExposureReadiness.CONDITIONAL
    ):
        return ExposureDecision.ALLOW_WITH_RESTRICTION

    return ExposureDecision.ALLOW


def build_exposure_action(
    request: Optional[ExposureRequest],
    assessment: Optional[ExposureAssessment] = None,
    decision: Optional[ExposureDecision] = None,
) -> ExposureAction:

    if not isinstance(
        request,
        ExposureRequest,
    ):
        return ExposureAction(
            action_state=ExposureActionState.INVALIDATE,
            decision=ExposureDecision.UNKNOWN,

            pathway=None,
            direction=None,

            reasons=(
                "Invalid exposure request",
            ),

            blocked=True,
        )

    if assessment is None:
        assessment = build_exposure_assessment(
            request
        )

    if decision is None:
        decision = determine_exposure_decision(
            request,
            assessment,
        )

    action_state = (
        determine_exposure_action_state(
            decision
        )
    )

    executable = (
        decision == ExposureDecision.ALLOW
    )

    requires_review = (
        decision
        == ExposureDecision.REVIEW_REQUIRED
    )

    blocked = (
        decision
        == ExposureDecision.BLOCK
    )

    reasons: list[str] = []

    if assessment.rationale:
        reasons.append(
            assessment.rationale
        )

    reasons.extend(
        assessment.weaknesses
    )

    return ExposureAction(
        action_state=action_state,
        decision=decision,

        pathway=request.action,
        direction=request.direction,

        restrictions=assessment.restrictions,
        exposure_flags=assessment.exposure_flags,

        reasons=tuple(
            dict.fromkeys(reasons)
        ),

        executable=executable,
        requires_review=requires_review,
        blocked=blocked,
    )


def build_exposure_result(
    request: Optional[ExposureRequest],
    assessment: Optional[ExposureAssessment] = None,
    action: Optional[ExposureAction] = None,
) -> ExposureResult:

    if not isinstance(
        request,
        ExposureRequest,
    ):
        return ExposureResult(
            request_id="",

            status=ExposureResultStatus.INVALID,
            decision=ExposureDecision.UNKNOWN,

            exposure_status=ExposureStatus.INVALID,
            action_state=ExposureActionState.INVALIDATE,

            exposure_score=0.0,
            exposure_confidence=0.0,
            completeness_score=0.0,

            reasons=(
                "Invalid exposure request",
            ),

            can_advance=False,
            requires_review=False,
            blocked=True,
        )

    if assessment is None:
        assessment = build_exposure_assessment(
            request
        )

    if action is None:
        action = build_exposure_action(
            request,
            assessment,
        )

    decision = action.decision

    status = determine_exposure_result_status(
        decision
    )

    exposure_status = determine_exposure_status(
        assessment,
        decision,
    )

    can_advance = (
        decision
        in {
            ExposureDecision.ALLOW,
            ExposureDecision.ALLOW_WITH_RESTRICTION,
        }
        and exposure_status
        in {
            ExposureStatus.ACCEPTABLE,
            ExposureStatus.CONDITIONAL,
        }
        and not action.blocked
    )

    warnings = list(
        assessment.weaknesses
    )

    return ExposureResult(
        request_id=request.request_id,

        status=status,
        decision=decision,

        exposure_status=exposure_status,
        action_state=action.action_state,

        exposure_score=assessment.exposure_score,
        exposure_confidence=assessment.confidence_score,
        completeness_score=(
            assessment.completeness_score
        ),

        restrictions=assessment.restrictions,
        exposure_flags=assessment.exposure_flags,

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


def determine_exposure_contract_state(
    request: Optional[ExposureRequest],
    requirements: ExposureRequirements,
    result: ExposureResult,
) -> ExposureContractState:

    if not isinstance(
        request,
        ExposureRequest,
    ):
        return ExposureContractState.INVALID

    validation = validate_exposure_request(
        request
    )

    if not validation.valid:
        return ExposureContractState.INVALID

    if (
        result.status
        == ExposureResultStatus.BLOCKED
    ):
        return ExposureContractState.BLOCKED

    if (
        result.status
        == ExposureResultStatus.INVALID
    ):
        return ExposureContractState.INVALID

    if (
        requirements.readiness
        == ExposureReadiness.NOT_READY
    ):
        return ExposureContractState.INCOMPLETE

    return ExposureContractState.COMPLETE


def build_exposure_contract(
    request: Optional[ExposureRequest],
) -> ExposureContract:

    if not isinstance(
        request,
        ExposureRequest,
    ):

        invalid_request = (
            build_exposure_request()
        )

        requirements = (
            evaluate_exposure_requirements(
                invalid_request
            )
        )

        assessment = (
            build_exposure_assessment(
                invalid_request,
                requirements,
            )
        )

        action = build_exposure_action(
            invalid_request,
            assessment,
        )

        result = build_exposure_result(
            invalid_request,
            assessment,
            action,
        )

        return ExposureContract(
            request=invalid_request,

            requirements=requirements,
            assessment=assessment,

            action=action,
            result=result,

            contract_state=(
                ExposureContractState.INVALID
            ),

            contract_valid=False,
        )

    requirements = (
        evaluate_exposure_requirements(
            request
        )
    )

    assessment = build_exposure_assessment(
        request,
        requirements,
    )

    action = build_exposure_action(
        request,
        assessment,
    )

    result = build_exposure_result(
        request,
        assessment,
        action,
    )

    contract_state = (
        determine_exposure_contract_state(
            request,
            requirements,
            result,
        )
    )

    contract_valid = (
        contract_state
        in {
            ExposureContractState.COMPLETE,
            ExposureContractState.INCOMPLETE,
            ExposureContractState.BLOCKED,
        }
    )

    return ExposureContract(
        request=request,

        requirements=requirements,
        assessment=assessment,

        action=action,
        result=result,

        contract_state=contract_state,
        contract_valid=contract_valid,
    )


class ExposureGateEngine:
    """
    Singleton-style CAS Exposure Gate engine.

    Authority boundary:
        Exposure Gate evaluates exposure conditions.
        It does not create market alpha or modify D13.
    """

    _instance: Optional["ExposureGateEngine"] = None

    def __new__(
        cls,
    ) -> "ExposureGateEngine":

        if cls._instance is None:
            cls._instance = super().__new__(
                cls
            )

        return cls._instance

    @property
    def engine_name(self) -> str:
        return EXPOSURE_GATE_ENGINE

    @property
    def version(self) -> str:
        return EXPOSURE_GATE_VERSION

    def evaluate(
        self,
        request: Any = None,
        **kwargs: Any,
    ) -> ExposureContract:

        exposure_request = (
            build_exposure_request(
                request,
                **kwargs,
            )
        )

        return build_exposure_contract(
            exposure_request
        )

    def check(
        self,
        request: Any = None,
        **kwargs: Any,
    ) -> ExposureResult:

        contract = self.evaluate(
            request,
            **kwargs,
        )

        return contract.result

    def review(
        self,
        request: Any = None,
        **kwargs: Any,
    ) -> ExposureContract:

        return self.evaluate(
            request,
            **kwargs,
        )


_EXPOSURE_GATE_ENGINE: Optional[
    ExposureGateEngine
] = None


def get_exposure_gate_engine() -> ExposureGateEngine:

    global _EXPOSURE_GATE_ENGINE

    if _EXPOSURE_GATE_ENGINE is None:
        _EXPOSURE_GATE_ENGINE = (
            ExposureGateEngine()
        )

    return _EXPOSURE_GATE_ENGINE


def evaluate_exposure(
    request: Any = None,
    **kwargs: Any,
) -> ExposureContract:

    return get_exposure_gate_engine().evaluate(
        request,
        **kwargs,
    )


def check_exposure(
    request: Any = None,
    **kwargs: Any,
) -> ExposureResult:

    return get_exposure_gate_engine().check(
        request,
        **kwargs,
    )


def review_exposure(
    request: Any = None,
    **kwargs: Any,
) -> ExposureContract:

    return get_exposure_gate_engine().review(
        request,
        **kwargs,
    )
# ============================================================
# EXPOSURE GATE — PART 4
# Validation • Readiness • Safety • Authority • Audit • Health
# ============================================================

def validate_exposure_action(action: ExposureAction) -> bool:
    """Strict structural validation for ExposureAction."""
    if not isinstance(action, ExposureAction):
        return False

    if not action.action:
        return False

    if not action.decision:
        return False

    if not action.status:
        return False

    if action.restrictions is None:
        return False

    if action.flags is None:
        return False

    return True


def validate_exposure_result(result: ExposureResult) -> bool:
    """Strict structural validation for ExposureResult."""
    if not isinstance(result, ExposureResult):
        return False

    if not result.result_status:
        return False

    if not result.decision:
        return False

    if not result.status:
        return False

    if result.action is None:
        return False

    if result.assessment is None:
        return False

    return validate_exposure_action(result.action)


def validate_exposure_contract(contract: ExposureContract) -> bool:
    """Strict structural validation for ExposureContract."""
    if not isinstance(contract, ExposureContract):
        return False

    if not contract.contract_status:
        return False

    if contract.request is None:
        return False

    if contract.assessment is None:
        return False

    if contract.result is None:
        return False

    if not validate_exposure_result(contract.result):
        return False

    return True


# ------------------------------------------------------------
# READINESS / SAFETY
# ------------------------------------------------------------

def exposure_ready(contract_or_result) -> bool:
    """True only when exposure control is operational and usable."""
    if isinstance(contract_or_result, ExposureContract):
        if not validate_exposure_contract(contract_or_result):
            return False
        return contract_or_result.contract_status in (
            ExposureContractStatus.VALID,
            ExposureContractStatus.ACTIVE,
            ExposureContractStatus.COMPLETE,
        )

    if isinstance(contract_or_result, ExposureResult):
        if not validate_exposure_result(contract_or_result):
            return False
        return contract_or_result.result_status not in (
            ExposureResultStatus.INVALID,
            ExposureResultStatus.ERROR,
        )

    return False


def exposure_can_advance(result: ExposureResult) -> bool:
    """Determine whether downstream CAS processing may continue."""
    if not validate_exposure_result(result):
        return False

    return result.decision in (
        ExposureDecision.ALLOW,
        ExposureDecision.ALLOW_WITH_RESTRICTION,
    )


def exposure_requires_review(result: ExposureResult) -> bool:
    """True when exposure requires human/downstream review."""
    if not validate_exposure_result(result):
        return True

    return result.decision == ExposureDecision.REVIEW_REQUIRED


def exposure_is_blocked(result: ExposureResult) -> bool:
    """True when exposure gate blocks the pathway."""
    if not validate_exposure_result(result):
        return True

    return result.decision == ExposureDecision.BLOCK


def exposure_is_restricted(result: ExposureResult) -> bool:
    """True when exposure is allowed only with restrictions."""
    if not validate_exposure_result(result):
        return False

    return result.decision == ExposureDecision.ALLOW_WITH_RESTRICTION


def exposure_is_safe_for_next_gate(result: ExposureResult) -> bool:
    """
    Exposure-safe means the exposure condition may proceed to
    the next CAS layer without violating exposure authority.
    """
    if not validate_exposure_result(result):
        return False

    return result.decision in (
        ExposureDecision.ALLOW,
        ExposureDecision.ALLOW_WITH_RESTRICTION,
    )


def get_exposure_status(result: ExposureResult):
    if not validate_exposure_result(result):
        return None
    return result.status


def get_exposure_decision(result: ExposureResult):
    if not validate_exposure_result(result):
        return None
    return result.decision


def get_exposure_action_state(result: ExposureResult):
    if not validate_exposure_result(result):
        return None
    return result.action.action_state


# ------------------------------------------------------------
# AUTHORITY BOUNDARIES
# ------------------------------------------------------------

def exposure_generates_market_decision() -> bool:
    return False


def exposure_generates_alpha() -> bool:
    return False


def exposure_modifies_d13() -> bool:
    return False


def exposure_overrides_d13() -> bool:
    return False


def exposure_replaces_risk_authority() -> bool:
    return False


def exposure_overrides_risk_authority() -> bool:
    return False


def exposure_overrides_cas() -> bool:
    return False


def exposure_authorizes_execution() -> bool:
    return False


def exposure_places_orders() -> bool:
    return False


def exposure_changes_position() -> bool:
    return False


def exposure_has_execution_authority() -> bool:
    return False


def exposure_has_market_decision_authority() -> bool:
    return False


def exposure_is_alpha_engine() -> bool:
    return False


def exposure_authority_integrity_ok() -> bool:
    """
    Exposure Gate must remain an exposure-control authority only.
    """
    boundaries = (
        exposure_generates_market_decision(),
        exposure_generates_alpha(),
        exposure_modifies_d13(),
        exposure_overrides_d13(),
        exposure_replaces_risk_authority(),
        exposure_overrides_risk_authority(),
        exposure_overrides_cas(),
        exposure_authorizes_execution(),
        exposure_places_orders(),
        exposure_changes_position(),
        exposure_has_execution_authority(),
        exposure_has_market_decision_authority(),
        exposure_is_alpha_engine(),
    )

    return not any(boundaries)


def exposure_has_authority_conflict() -> bool:
    return not exposure_authority_integrity_ok()


# ------------------------------------------------------------
# AUDIT
# ------------------------------------------------------------

@dataclass(frozen=True)
class ExposureAuditRecord:
    request_id: str
    engine: str
    version: str
    decision: str
    status: str
    action_state: str
    exposure_score: float
    exposure_confidence: float
    flags: tuple
    restrictions: tuple
    authority_integrity: bool
    timestamp: str


def build_exposure_audit(
    result: ExposureResult,
    request_id: str = "",
) -> ExposureAuditRecord:
    """Create immutable audit record for Exposure Gate evaluation."""

    assessment = result.assessment

    return ExposureAuditRecord(
        request_id=request_id,
        engine=EXPOSURE_GATE_ENGINE,
        version=EXPOSURE_GATE_VERSION,
        decision=str(result.decision),
        status=str(result.status),
        action_state=str(result.action.action_state),
        exposure_score=float(assessment.exposure_score),
        exposure_confidence=float(assessment.exposure_confidence),
        flags=tuple(assessment.flags or ()),
        restrictions=tuple(assessment.restrictions or ()),
        authority_integrity=exposure_authority_integrity_ok(),
        timestamp=datetime.utcnow().isoformat(),
    )


# ------------------------------------------------------------
# ENGINE HEALTH
# ------------------------------------------------------------

@dataclass(frozen=True)
class ExposureEngineHealth:
    engine: str
    version: str
    operational: bool
    authority_integrity: bool
    validation_available: bool
    assessment_available: bool
    decision_available: bool
    audit_available: bool
    status: str


def get_exposure_engine_health() -> ExposureEngineHealth:
    """
    Runtime health descriptor.

    This function checks structural availability without executing
    a market decision or altering any state.
    """

    validation_ok = all(
        callable(fn)
        for fn in (
            validate_exposure_request,
            validate_exposure_action,
            validate_exposure_result,
            validate_exposure_contract,
        )
    )

    assessment_ok = all(
        callable(fn)
        for fn in (
            evaluate_exposure_data_state,
            evaluate_exposure_consistency,
            evaluate_exposure_readiness,
            evaluate_exposure_requirements,
            build_exposure_assessment,
        )
    )

    decision_ok = all(
        callable(fn)
        for fn in (
            determine_exposure_status,
            determine_exposure_decision,
            determine_exposure_action_state,
            build_exposure_result,
            build_exposure_contract,
        )
    )

    audit_ok = callable(build_exposure_audit)

    authority_ok = exposure_authority_integrity_ok()

    operational = all(
        (
            validation_ok,
            assessment_ok,
            decision_ok,
            audit_ok,
            authority_ok,
        )
    )

    return ExposureEngineHealth(
        engine=EXPOSURE_GATE_ENGINE,
        version=EXPOSURE_GATE_VERSION,
        operational=operational,
        authority_integrity=authority_ok,
        validation_available=validation_ok,
        assessment_available=assessment_ok,
        decision_available=decision_ok,
        audit_available=audit_ok,
        status="OPERATIONAL" if operational else "DEGRADED",
    )


def get_exposure_engine_info() -> dict:
    """Static engine identity and authority information."""

    return {
        "engine": EXPOSURE_GATE_ENGINE,
        "version": EXPOSURE_GATE_VERSION,
        "role": "CAS_EXPOSURE_CONTROL",
        "authority": "EXPOSURE_CONTROL_ONLY",
        "generates_market_decision": False,
        "generates_alpha": False,
        "modifies_d13": False,
        "overrides_d13": False,
        "replaces_risk_authority": False,
        "overrides_cas": False,
        "authorizes_execution": False,
        "places_orders": False,
        "changes_position": False,
        "authority_integrity": exposure_authority_integrity_ok(),
    }


def exposure_integrity_ok(
    contract: ExposureContract | None = None,
) -> bool:
    """
    Complete Exposure Gate integrity check.

    Contract validation is included when a contract is supplied.
    """

    if not exposure_authority_integrity_ok():
        return False

    health = get_exposure_engine_health()

    if not health.operational:
        return False

    if contract is not None and not validate_exposure_contract(contract):
        return False

    return True
# ============================================================
# EXPOSURE GATE — PART 5
# Lifecycle • Serialization • Summary • Snapshot • Public API
# ============================================================


# ------------------------------------------------------------
# LIFECYCLE
# ------------------------------------------------------------

class ExposureLifecycleState(str, Enum):
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


def determine_exposure_lifecycle(
    contract: ExposureContract,
) -> ExposureLifecycleState:

    if not validate_exposure_contract(contract):
        return ExposureLifecycleState.REJECTED

    result = contract.result

    if result.decision == ExposureDecision.BLOCK:
        return ExposureLifecycleState.BLOCKED

    if result.decision == ExposureDecision.REVIEW_REQUIRED:
        return ExposureLifecycleState.REVIEW

    if result.decision == ExposureDecision.ALLOW_WITH_RESTRICTION:
        return ExposureLifecycleState.RESTRICTED

    if result.decision == ExposureDecision.ALLOW:
        return ExposureLifecycleState.ACTIVE

    return ExposureLifecycleState.COMPLETED


def freeze_exposure(
    contract: ExposureContract,
) -> ExposureLifecycleState:
    if not validate_exposure_contract(contract):
        return ExposureLifecycleState.REJECTED

    return ExposureLifecycleState.FROZEN


def retain_exposure(
    contract: ExposureContract,
) -> ExposureLifecycleState:
    if not validate_exposure_contract(contract):
        return ExposureLifecycleState.REJECTED

    return ExposureLifecycleState.RETAINED


def reject_exposure(
    contract: ExposureContract,
) -> ExposureLifecycleState:
    if not validate_exposure_contract(contract):
        return ExposureLifecycleState.REJECTED

    return ExposureLifecycleState.REJECTED


# ------------------------------------------------------------
# SERIALIZATION HELPERS
# ------------------------------------------------------------

def exposure_request_to_dict(
    request: ExposureRequest,
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
        "mode": str(request.mode),
        "strategy": request.strategy,
        "timeframe": request.timeframe,
        "priority": str(request.priority),

        "current_exposure": request.current_exposure,
        "proposed_exposure": request.proposed_exposure,
        "projected_exposure": request.projected_exposure,
        "max_exposure": request.max_exposure,
        "available_exposure": request.available_exposure,

        "current_position_value": request.current_position_value,
        "proposed_position_value": request.proposed_position_value,

        "quantity": request.quantity,
        "price": request.price,

        "leverage": request.leverage,
        "max_leverage": request.max_leverage,

        "concentration": request.concentration,
        "max_concentration": request.max_concentration,

        "portfolio_exposure": request.portfolio_exposure,
        "portfolio_max_exposure": request.portfolio_max_exposure,

        "correlated_exposure": request.correlated_exposure,
        "correlated_max_exposure": request.correlated_max_exposure,

        "metadata": dict(request.metadata or {}),
        "request_id": request.request_id,
    }


def exposure_assessment_to_dict(
    assessment: ExposureAssessment,
) -> dict:

    return {
        "data_state": str(assessment.data_state),
        "consistency": str(assessment.consistency),
        "readiness": str(assessment.readiness),
        "completeness": float(assessment.completeness),

        "requirements_met": bool(assessment.requirements_met),

        "flags": list(assessment.flags or ()),
        "restrictions": list(assessment.restrictions or ()),

        "exposure_score": float(assessment.exposure_score),
        "exposure_confidence": float(assessment.exposure_confidence),
    }


def exposure_result_to_dict(
    result: ExposureResult,
) -> dict:

    return {
        "result_status": str(result.result_status),
        "status": str(result.status),
        "decision": str(result.decision),

        "action": {
            "action": result.action.action,
            "action_state": str(result.action.action_state),
            "decision": str(result.action.decision),
            "status": str(result.action.status),
            "restrictions": list(result.action.restrictions or ()),
            "flags": list(result.action.flags or ()),
        },

        "assessment": exposure_assessment_to_dict(
            result.assessment
        ),
    }


def exposure_contract_to_dict(
    contract: ExposureContract,
) -> dict:

    return {
        "contract_status": str(contract.contract_status),
        "request": exposure_request_to_dict(contract.request),
        "assessment": exposure_assessment_to_dict(
            contract.assessment
        ),
        "result": exposure_result_to_dict(contract.result),
        "lifecycle": str(
            determine_exposure_lifecycle(contract)
        ),
    }


# ------------------------------------------------------------
# SUMMARY
# ------------------------------------------------------------

def summarize_exposure(
    result: ExposureResult,
) -> dict:

    if not validate_exposure_result(result):
        return {
            "valid": False,
            "engine": EXPOSURE_GATE_ENGINE,
            "version": EXPOSURE_GATE_VERSION,
            "status": "INVALID",
        }

    assessment = result.assessment

    return {
        "valid": True,
        "engine": EXPOSURE_GATE_ENGINE,
        "version": EXPOSURE_GATE_VERSION,

        "status": str(result.status),
        "decision": str(result.decision),
        "action_state": str(result.action.action_state),

        "exposure_score": float(
            assessment.exposure_score
        ),
        "exposure_confidence": float(
            assessment.exposure_confidence
        ),

        "flags": list(assessment.flags or ()),
        "restrictions": list(
            assessment.restrictions or ()
        ),

        "can_advance": exposure_can_advance(result),
        "requires_review": exposure_requires_review(result),
        "blocked": exposure_is_blocked(result),
        "restricted": exposure_is_restricted(result),
        "safe_for_next_gate": exposure_is_safe_for_next_gate(
            result
        ),

        "authority_integrity": (
            exposure_authority_integrity_ok()
        ),
    }


# ------------------------------------------------------------
# AUTHORITY STATEMENT
# ------------------------------------------------------------

def get_exposure_authority_statement() -> str:
    return (
        "Exposure Gate is a CAS internal exposure-control "
        "authority. It evaluates exposure capacity, "
        "concentration, leverage, portfolio exposure and "
        "correlated exposure. It does not generate alpha, "
        "make market decisions, modify or override D13, "
        "replace Risk Authority, authorize execution, "
        "place orders, or change positions."
    )


# ------------------------------------------------------------
# OPERATIONAL CHECK
# ------------------------------------------------------------

def exposure_engine_operational() -> bool:
    health = get_exposure_engine_health()

    return bool(
        health.operational
        and health.authority_integrity
        and health.validation_available
        and health.assessment_available
        and health.decision_available
        and health.audit_available
    )


# ------------------------------------------------------------
# COMPLETE VALIDATION
# ------------------------------------------------------------

def validate_exposure(
    contract: ExposureContract,
) -> bool:

    if not validate_exposure_contract(contract):
        return False

    if not exposure_authority_integrity_ok():
        return False

    if contract.assessment is None:
        return False

    if contract.result is None:
        return False

    return True


# ------------------------------------------------------------
# SNAPSHOT
# ------------------------------------------------------------

def exposure_snapshot(
    contract: ExposureContract | None = None,
) -> dict:

    health = get_exposure_engine_health()

    snapshot = {
        "engine": EXPOSURE_GATE_ENGINE,
        "version": EXPOSURE_GATE_VERSION,
        "operational": exposure_engine_operational(),

        "health": {
            "operational": health.operational,
            "authority_integrity": (
                health.authority_integrity
            ),
            "validation_available": (
                health.validation_available
            ),
            "assessment_available": (
                health.assessment_available
            ),
            "decision_available": (
                health.decision_available
            ),
            "audit_available": (
                health.audit_available
            ),
            "status": health.status,
        },

        "authority": get_exposure_authority_statement(),

        "authority_boundaries": {
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
        },
    }

    if contract is not None:
        snapshot["contract_valid"] = validate_exposure_contract(
            contract
        )
        snapshot["lifecycle"] = str(
            determine_exposure_lifecycle(contract)
        )

        if validate_exposure_contract(contract):
            snapshot["summary"] = summarize_exposure(
                contract.result
            )

    return snapshot


# ------------------------------------------------------------
# PUBLIC EXPORTS
# ------------------------------------------------------------

__all__ = [
    # Constants
    "EXPOSURE_GATE_ENGINE",
    "EXPOSURE_GATE_VERSION",

    # Enums
    "ExposureStatus",
    "ExposureDecision",
    "ExposureMode",
    "ExposurePriority",
    "ExposureContractStatus",
    "ExposureDataState",
    "ExposureConsistency",
    "ExposureReadiness",
    "ExposureActionState",
    "ExposureContractState",
    "ExposureResultStatus",
    "ExposureLifecycleState",

    # Contracts
    "ExposureRequest",
    "ExposureReference",
    "ExposureContractValidation",
    "ExposureRequirements",
    "ExposureAssessment",
    "ExposureAction",
    "ExposureResult",
    "ExposureContract",

    # Builders / evaluation
    "build_exposure_request",
    "build_exposure_assessment",
    "build_exposure_action",
    "build_exposure_result",
    "build_exposure_contract",

    "evaluate_exposure_data_state",
    "evaluate_exposure_consistency",
    "calculate_exposure_completeness",
    "evaluate_exposure_readiness",
    "evaluate_exposure_requirements",

    "calculate_exposure_score",
    "calculate_exposure_confidence",

    "extract_exposure_flags",
    "extract_exposure_restrictions",

    "determine_exposure_status",
    "determine_exposure_action_state",
    "determine_exposure_decision",
    "determine_exposure_result_status",
    "determine_exposure_lifecycle",

    # Engine
    "ExposureGateEngine",
    "get_exposure_gate_engine",
    "evaluate_exposure",
    "check_exposure",
    "review_exposure",

    # Validation
    "validate_exposure_numeric_inputs",
    "validate_exposure_request",
    "validate_exposure_action",
    "validate_exposure_result",
    "validate_exposure_contract",
    "validate_exposure",

    # Readiness / safety
    "exposure_ready",
    "exposure_can_advance",
    "exposure_requires_review",
    "exposure_is_blocked",
    "exposure_is_restricted",
    "exposure_is_safe_for_next_gate",

    # Accessors
    "get_exposure_status",
    "get_exposure_decision",
    "get_exposure_action_state",

    # Authority
    "exposure_generates_market_decision",
    "exposure_generates_alpha",
    "exposure_modifies_d13",
    "exposure_overrides_d13",
    "exposure_replaces_risk_authority",
    "exposure_overrides_risk_authority",
    "exposure_overrides_cas",
    "exposure_authorizes_execution",
    "exposure_places_orders",
    "exposure_changes_position",
    "exposure_has_execution_authority",
    "exposure_has_market_decision_authority",
    "exposure_is_alpha_engine",
    "exposure_authority_integrity_ok",
    "exposure_has_authority_conflict",

    # Audit / health
    "ExposureAuditRecord",
    "build_exposure_audit",
    "ExposureEngineHealth",
    "get_exposure_engine_health",
    "get_exposure_engine_info",
    "exposure_integrity_ok",

    # Lifecycle
    "freeze_exposure",
    "retain_exposure",
    "reject_exposure",

    # Serialization
    "exposure_request_to_dict",
    "exposure_assessment_to_dict",
    "exposure_result_to_dict",
    "exposure_contract_to_dict",

    # Summary / snapshot
    "summarize_exposure",
    "get_exposure_authority_statement",
    "exposure_engine_operational",
    "exposure_snapshot",
]