# app/intelligence/cas/restriction_engine.py
# PART 1/5

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Optional


# ============================================================
# RESTRICTION ENGINE — CORE CONSTANTS
# ============================================================

RESTRICTION_ENGINE = "ROBOMLM_CAS_RESTRICTION_ENGINE"
RESTRICTION_ENGINE_VERSION = "1.0"


# ============================================================
# ENUMS
# ============================================================

class RestrictionStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    CLEAR = "CLEAR"
    RESTRICTED = "RESTRICTED"
    CONDITIONAL = "CONDITIONAL"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"


class RestrictionDecision(str, Enum):
    ALLOW = "ALLOW"
    ALLOW_WITH_RESTRICTION = "ALLOW_WITH_RESTRICTION"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCK = "BLOCK"


class RestrictionMode(str, Enum):
    PAPER = "PAPER"
    DEMO = "DEMO"
    LIVE = "LIVE"
    UNKNOWN = "UNKNOWN"


class RestrictionPriority(str, Enum):
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RestrictionContractStatus(str, Enum):
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
class RestrictionRequest:
    """
    CAS Restriction Engine input contract.

    The engine evaluates supplied restrictions and determines
    whether an action is clear, conditionally restricted,
    requires review, or must be blocked.

    It does NOT:
        - generate market alpha
        - generate market direction
        - modify D13
        - replace Risk Authority
        - override CAS
        - place orders
        - mutate positions
    """

    # --------------------------------------------------------
    # MARKET / INSTRUMENT
    # --------------------------------------------------------
    market: Optional[str] = None
    instrument: Optional[str] = None
    contract: Optional[str] = None

    # --------------------------------------------------------
    # USER / ACCOUNT / PLAN
    # --------------------------------------------------------
    user_id: Optional[str] = None
    account_id: Optional[str] = None
    plan_id: Optional[str] = None

    # --------------------------------------------------------
    # ACTION / DIRECTION
    # --------------------------------------------------------
    action: Optional[str] = None
    direction: Optional[str] = None

    # --------------------------------------------------------
    # EXECUTION CONTEXT
    # --------------------------------------------------------
    mode: RestrictionMode = RestrictionMode.UNKNOWN
    strategy: Optional[str] = None
    timeframe: Optional[str] = None
    priority: RestrictionPriority = (
        RestrictionPriority.NORMAL
    )

    # --------------------------------------------------------
    # RESTRICTION SOURCES
    # --------------------------------------------------------
    user_restricted: Optional[bool] = None
    account_restricted: Optional[bool] = None
    plan_restricted: Optional[bool] = None

    instrument_restricted: Optional[bool] = None
    market_restricted: Optional[bool] = None

    action_restricted: Optional[bool] = None
    direction_restricted: Optional[bool] = None

    strategy_restricted: Optional[bool] = None
    timeframe_restricted: Optional[bool] = None

    # --------------------------------------------------------
    # TEMPORAL / SESSION RESTRICTIONS
    # --------------------------------------------------------
    session_restricted: Optional[bool] = None
    time_restricted: Optional[bool] = None
    expiry_restricted: Optional[bool] = None
    closing_window_restricted: Optional[bool] = None

    # --------------------------------------------------------
    # POSITION / PATHWAY RESTRICTIONS
    # --------------------------------------------------------
    new_entry_restricted: Optional[bool] = None
    add_position_restricted: Optional[bool] = None
    reduce_restricted: Optional[bool] = None
    exit_restricted: Optional[bool] = None
    profit_booking_restricted: Optional[bool] = None

    # --------------------------------------------------------
    # OPERATIONAL RESTRICTIONS
    # --------------------------------------------------------
    manual_only: Optional[bool] = None
    reduce_only: Optional[bool] = None
    close_only: Optional[bool] = None
    no_new_position: Optional[bool] = None

    # --------------------------------------------------------
    # EXTERNAL CONTROL STATES
    # --------------------------------------------------------
    policy_restricted: Optional[bool] = None
    compliance_restricted: Optional[bool] = None
    risk_restricted: Optional[bool] = None
    exposure_restricted: Optional[bool] = None
    position_restricted: Optional[bool] = None
    execution_restricted: Optional[bool] = None

    # --------------------------------------------------------
    # EXPLICIT REVIEW / BLOCK
    # --------------------------------------------------------
    review_required: Optional[bool] = None
    hard_block: Optional[bool] = None

    # --------------------------------------------------------
    # METADATA
    # --------------------------------------------------------
    metadata: Mapping[str, Any] = field(default_factory=dict)

    request_id: Optional[str] = None
    timestamp: Optional[datetime] = None


# ============================================================
# REFERENCE CONTRACT
# ============================================================

@dataclass(frozen=True)
class RestrictionReference:
    """
    Reference explaining the source of a restriction.

    The engine consumes supplied restriction information;
    it does not invent external rules.
    """

    source: Optional[str] = None
    restriction_id: Optional[str] = None
    rule_id: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


# ============================================================
# VALIDATION CONTRACT
# ============================================================

@dataclass(frozen=True)
class RestrictionContractValidation:
    valid: bool
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    missing_fields: tuple[str, ...] = ()
    checked_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _rg_read_value(
    source: Any,
    name: str,
    default: Any = None,
) -> Any:
    """
    Safely read a value from mapping-like or object-like input.
    """
    if source is None:
        return default

    if isinstance(source, Mapping):
        return source.get(name, default)

    return getattr(source, name, default)


def _rg_text(value: Any) -> Optional[str]:
    """
    Normalize textual values.
    """
    if value is None:
        return None

    text = str(value).strip()

    return text if text else None


def _rg_enum(
    value: Any,
    enum_type: type[Enum],
    default: Enum,
) -> Enum:
    """
    Normalize enum values without raising on unknown external
    input.
    """
    if value is None:
        return default

    if isinstance(value, enum_type):
        return value

    text = str(value).strip().upper()

    for member in enum_type:
        if text in {
            member.name.upper(),
            str(member.value).upper(),
        }:
            return member

    return default


def _rg_number(value: Any) -> Optional[float]:
    """
    Safely normalize numeric values when supplied.
    """
    if value is None:
        return None

    if isinstance(value, bool):
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _rg_bool(value: Any) -> Optional[bool]:
    """
    Safely normalize boolean-like external values.
    """
    if value is None:
        return None

    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        if value == 1:
            return True
        if value == 0:
            return False

    if isinstance(value, str):
        normalized = value.strip().lower()

        if normalized in {
            "true",
            "yes",
            "y",
            "1",
            "allow",
            "allowed",
            "enabled",
            "active",
        }:
            return True

        if normalized in {
            "false",
            "no",
            "n",
            "0",
            "deny",
            "denied",
            "disabled",
            "inactive",
        }:
            return False

    return None


def _rg_timestamp(value: Any = None) -> datetime:
    """
    Normalize timestamp to timezone-aware UTC.
    """
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)

    return datetime.now(timezone.utc)


# ============================================================
# REQUEST BUILDER
# ============================================================

def build_restriction_request(
    source: Any = None,
    *,
    market: Optional[str] = None,
    instrument: Optional[str] = None,
    contract: Optional[str] = None,
    user_id: Optional[str] = None,
    account_id: Optional[str] = None,
    plan_id: Optional[str] = None,
    action: Optional[str] = None,
    direction: Optional[str] = None,
    mode: Any = None,
    strategy: Optional[str] = None,
    timeframe: Optional[str] = None,
    priority: Any = None,

    user_restricted: Optional[bool] = None,
    account_restricted: Optional[bool] = None,
    plan_restricted: Optional[bool] = None,

    instrument_restricted: Optional[bool] = None,
    market_restricted: Optional[bool] = None,

    action_restricted: Optional[bool] = None,
    direction_restricted: Optional[bool] = None,

    strategy_restricted: Optional[bool] = None,
    timeframe_restricted: Optional[bool] = None,

    session_restricted: Optional[bool] = None,
    time_restricted: Optional[bool] = None,
    expiry_restricted: Optional[bool] = None,
    closing_window_restricted: Optional[bool] = None,

    new_entry_restricted: Optional[bool] = None,
    add_position_restricted: Optional[bool] = None,
    reduce_restricted: Optional[bool] = None,
    exit_restricted: Optional[bool] = None,
    profit_booking_restricted: Optional[bool] = None,

    manual_only: Optional[bool] = None,
    reduce_only: Optional[bool] = None,
    close_only: Optional[bool] = None,
    no_new_position: Optional[bool] = None,

    policy_restricted: Optional[bool] = None,
    compliance_restricted: Optional[bool] = None,
    risk_restricted: Optional[bool] = None,
    exposure_restricted: Optional[bool] = None,
    position_restricted: Optional[bool] = None,
    execution_restricted: Optional[bool] = None,

    review_required: Optional[bool] = None,
    hard_block: Optional[bool] = None,

    metadata: Optional[Mapping[str, Any]] = None,
    request_id: Optional[str] = None,
    timestamp: Any = None,
) -> RestrictionRequest:

    def pick(value: Any, name: str) -> Any:
        return (
            value
            if value is not None
            else _rg_read_value(source, name)
        )

    return RestrictionRequest(
        market=_rg_text(pick(market, "market")),
        instrument=_rg_text(
            pick(instrument, "instrument")
        ),
        contract=_rg_text(
            pick(contract, "contract")
        ),

        user_id=_rg_text(
            pick(user_id, "user_id")
        ),
        account_id=_rg_text(
            pick(account_id, "account_id")
        ),
        plan_id=_rg_text(
            pick(plan_id, "plan_id")
        ),

        action=_rg_text(
            pick(action, "action")
        ),
        direction=_rg_text(
            pick(direction, "direction")
        ),

        mode=_rg_enum(
            pick(mode, "mode"),
            RestrictionMode,
            RestrictionMode.UNKNOWN,
        ),

        strategy=_rg_text(
            pick(strategy, "strategy")
        ),
        timeframe=_rg_text(
            pick(timeframe, "timeframe")
        ),

        priority=_rg_enum(
            pick(priority, "priority"),
            RestrictionPriority,
            RestrictionPriority.NORMAL,
        ),

        user_restricted=_rg_bool(
            pick(user_restricted, "user_restricted")
        ),
        account_restricted=_rg_bool(
            pick(
                account_restricted,
                "account_restricted",
            )
        ),
        plan_restricted=_rg_bool(
            pick(plan_restricted, "plan_restricted")
        ),

        instrument_restricted=_rg_bool(
            pick(
                instrument_restricted,
                "instrument_restricted",
            )
        ),
        market_restricted=_rg_bool(
            pick(
                market_restricted,
                "market_restricted",
            )
        ),

        action_restricted=_rg_bool(
            pick(
                action_restricted,
                "action_restricted",
            )
        ),
        direction_restricted=_rg_bool(
            pick(
                direction_restricted,
                "direction_restricted",
            )
        ),

        strategy_restricted=_rg_bool(
            pick(
                strategy_restricted,
                "strategy_restricted",
            )
        ),
        timeframe_restricted=_rg_bool(
            pick(
                timeframe_restricted,
                "timeframe_restricted",
            )
        ),

        session_restricted=_rg_bool(
            pick(
                session_restricted,
                "session_restricted",
            )
        ),
        time_restricted=_rg_bool(
            pick(
                time_restricted,
                "time_restricted",
            )
        ),
        expiry_restricted=_rg_bool(
            pick(
                expiry_restricted,
                "expiry_restricted",
            )
        ),
        closing_window_restricted=_rg_bool(
            pick(
                closing_window_restricted,
                "closing_window_restricted",
            )
        ),

        new_entry_restricted=_rg_bool(
            pick(
                new_entry_restricted,
                "new_entry_restricted",
            )
        ),
        add_position_restricted=_rg_bool(
            pick(
                add_position_restricted,
                "add_position_restricted",
            )
        ),
        reduce_restricted=_rg_bool(
            pick(
                reduce_restricted,
                "reduce_restricted",
            )
        ),
        exit_restricted=_rg_bool(
            pick(
                exit_restricted,
                "exit_restricted",
            )
        ),
        profit_booking_restricted=_rg_bool(
            pick(
                profit_booking_restricted,
                "profit_booking_restricted",
            )
        ),

        manual_only=_rg_bool(
            pick(manual_only, "manual_only")
        ),
        reduce_only=_rg_bool(
            pick(reduce_only, "reduce_only")
        ),
        close_only=_rg_bool(
            pick(close_only, "close_only")
        ),
        no_new_position=_rg_bool(
            pick(no_new_position, "no_new_position")
        ),

        policy_restricted=_rg_bool(
            pick(
                policy_restricted,
                "policy_restricted",
            )
        ),
        compliance_restricted=_rg_bool(
            pick(
                compliance_restricted,
                "compliance_restricted",
            )
        ),
        risk_restricted=_rg_bool(
            pick(
                risk_restricted,
                "risk_restricted",
            )
        ),
        exposure_restricted=_rg_bool(
            pick(
                exposure_restricted,
                "exposure_restricted",
            )
        ),
        position_restricted=_rg_bool(
            pick(
                position_restricted,
                "position_restricted",
            )
        ),
        execution_restricted=_rg_bool(
            pick(
                execution_restricted,
                "execution_restricted",
            )
        ),

        review_required=_rg_bool(
            pick(review_required, "review_required")
        ),
        hard_block=_rg_bool(
            pick(hard_block, "hard_block")
        ),

        metadata=(
            dict(metadata)
            if metadata is not None
            else dict(
                _rg_read_value(
                    source,
                    "metadata",
                    {},
                ) or {}
            )
        ),

        request_id=_rg_text(
            pick(request_id, "request_id")
        ),

        timestamp=_rg_timestamp(
            pick(timestamp, "timestamp")
        ),
    )


# ============================================================
# NUMERIC VALIDATION
# ============================================================

def validate_restriction_numeric_inputs(
    request: RestrictionRequest,
) -> tuple[str, ...]:
    """
    Restriction Engine currently has no mandatory quantitative
    restriction thresholds.

    This validation hook is retained for future externally
    supplied threshold metadata without changing the contract.
    """

    errors: list[str] = []

    if not isinstance(
        request,
        RestrictionRequest,
    ):
        errors.append("REQUEST_TYPE_INVALID")

    return tuple(errors)


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_restriction_request(
    request: RestrictionRequest,
) -> RestrictionContractValidation:

    errors: list[str] = []
    warnings: list[str] = []
    missing: list[str] = []

    if not isinstance(
        request,
        RestrictionRequest,
    ):
        return RestrictionContractValidation(
            valid=False,
            errors=("REQUEST_TYPE_INVALID",),
        )

    errors.extend(
        validate_restriction_numeric_inputs(
            request
        )
    )

    # --------------------------------------------------------
    # CORE CONTEXT
    # --------------------------------------------------------
    if not request.market:
        missing.append("market")

    if not request.instrument:
        missing.append("instrument")

    if not request.action:
        missing.append("action")

    # --------------------------------------------------------
    # CONTEXT WARNINGS
    # --------------------------------------------------------
    if not request.user_id:
        warnings.append("USER_ID_MISSING")

    if not request.account_id:
        warnings.append("ACCOUNT_ID_MISSING")

    if not request.plan_id:
        warnings.append("PLAN_ID_MISSING")

    if not request.direction:
        warnings.append("DIRECTION_MISSING")

    # --------------------------------------------------------
    # RESTRICTION SOURCE WARNINGS
    # --------------------------------------------------------
    restriction_fields = (
        request.user_restricted,
        request.account_restricted,
        request.plan_restricted,
        request.instrument_restricted,
        request.market_restricted,
        request.action_restricted,
        request.direction_restricted,
        request.strategy_restricted,
        request.timeframe_restricted,
        request.session_restricted,
        request.time_restricted,
        request.expiry_restricted,
        request.closing_window_restricted,
        request.new_entry_restricted,
        request.add_position_restricted,
        request.reduce_restricted,
        request.exit_restricted,
        request.profit_booking_restricted,
        request.manual_only,
        request.reduce_only,
        request.close_only,
        request.no_new_position,
        request.policy_restricted,
        request.compliance_restricted,
        request.risk_restricted,
        request.exposure_restricted,
        request.position_restricted,
        request.execution_restricted,
    )

    if not any(
        value is not None
        for value in restriction_fields
    ):
        warnings.append(
            "NO_RESTRICTION_STATE_SUPPLIED"
        )

    # --------------------------------------------------------
    # EXPLICIT CONTROL WARNINGS
    # --------------------------------------------------------
    if request.review_required is None:
        warnings.append(
            "REVIEW_STATE_UNKNOWN"
        )

    if request.hard_block is None:
        warnings.append(
            "HARD_BLOCK_STATE_UNKNOWN"
        )

    # --------------------------------------------------------
    # STRUCTURAL ERRORS
    # --------------------------------------------------------
    if missing:
        errors.extend(
            f"REQUIRED_FIELD_MISSING:{field}"
            for field in missing
        )

    return RestrictionContractValidation(
        valid=not errors,
        errors=tuple(errors),
        warnings=tuple(warnings),
        missing_fields=tuple(missing),
    )
# ============================================================
# ROBOMLM — CAS Restriction Engine
# Part 2: State / Requirements / Assessment
# ============================================================

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


# ============================================================
# DATA / CONSISTENCY / READINESS
# ============================================================

class RestrictionDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    INVALID = "INVALID"


class RestrictionConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONDITIONAL = "CONDITIONAL"
    INCONSISTENT = "INCONSISTENT"
    UNKNOWN = "UNKNOWN"


class RestrictionReadiness(str, Enum):
    READY = "READY"
    CONDITIONALLY_READY = "CONDITIONALLY_READY"
    NOT_READY = "NOT_READY"
    BLOCKED = "BLOCKED"


# ============================================================
# PATHWAY SEMANTICS
# ============================================================

_RESTRICTION_REDUCTION_ACTIONS = {
    "REDUCE",
    "EXIT",
    "PROFIT_BOOK",
    "PARTIAL_EXIT",
    "CLOSE",
    "CLOSE_POSITION",
}

_RESTRICTION_EXPANSION_ACTIONS = {
    "NEW_ENTRY",
    "ENTRY",
    "ADD",
    "ADD_TO_POSITION",
    "SCALE_IN",
}

_RESTRICTION_HOLD_ACTIONS = {
    "HOLD",
    "RETAIN",
    "MAINTAIN",
    "WAIT",
    "WATCH",
}

_RESTRICTION_PLANNING_ACTIONS = {
    "NEXT_SESSION_PLAN",
    "PLAN",
    "PREPARE",
    "PREPARE_ENTRY",
}


def _restriction_action(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().upper()


def _restriction_is_reduction(action: Any) -> bool:
    return _restriction_action(action) in _RESTRICTION_REDUCTION_ACTIONS


def _restriction_is_expansion(action: Any) -> bool:
    return _restriction_action(action) in _RESTRICTION_EXPANSION_ACTIONS


def _restriction_is_hold(action: Any) -> bool:
    return _restriction_action(action) in _RESTRICTION_HOLD_ACTIONS


def _restriction_is_planning(action: Any) -> bool:
    return _restriction_action(action) in _RESTRICTION_PLANNING_ACTIONS


# ============================================================
# REQUIREMENTS
# ============================================================

@dataclass(frozen=True)
class RestrictionRequirements:
    require_market: bool = True
    require_instrument: bool = True
    require_action: bool = True

    require_user_state: bool = False
    require_account_state: bool = False
    require_plan_state: bool = False

    require_restriction_state: bool = True

    require_metadata: bool = False

    allow_unknown_restrictions: bool = False
    allow_conditional_restrictions: bool = True

    allow_reduction_pathways: bool = True
    allow_planning_pathways: bool = True

    require_timestamp: bool = False


# ============================================================
# ASSESSMENT
# ============================================================

@dataclass(frozen=True)
class RestrictionAssessment:
    status: RestrictionStatus
    data_state: RestrictionDataState
    consistency: RestrictionConsistency
    readiness: RestrictionReadiness

    completeness: float
    restriction_score: float
    restriction_confidence: float

    flags: Tuple[str, ...] = field(default_factory=tuple)
    restrictions: Tuple[str, ...] = field(default_factory=tuple)

    unmet_requirements: Tuple[str, ...] = field(default_factory=tuple)
    notes: Tuple[str, ...] = field(default_factory=tuple)

    action: Optional[str] = None
    direction: Optional[str] = None
    pathway: Optional[str] = None


# ============================================================
# DATA STATE
# ============================================================

def evaluate_restriction_data_state(
    request: RestrictionRequest,
) -> RestrictionDataState:

    if request is None:
        return RestrictionDataState.MISSING

    required = [
        request.market,
        request.instrument,
        request.action,
    ]

    if any(value is None for value in required):
        return RestrictionDataState.MISSING

    if any(
        isinstance(value, str) and not value.strip()
        for value in required
    ):
        return RestrictionDataState.INVALID

    restriction_fields = [
        request.user_restricted,
        request.account_restricted,
        request.plan_restricted,
        request.instrument_restricted,
        request.market_restricted,
        request.action_restricted,
        request.direction_restricted,
        request.strategy_restricted,
        request.timeframe_restricted,
        request.session_restricted,
        request.time_restricted,
        request.expiry_restricted,
        request.closing_window_restricted,
        request.new_entry_restricted,
        request.add_position_restricted,
        request.reduce_restricted,
        request.exit_restricted,
        request.profit_booking_restricted,
        request.manual_only,
        request.reduce_only,
        request.close_only,
        request.no_new_position,
        request.policy_restricted,
        request.compliance_restricted,
        request.risk_restricted,
        request.exposure_restricted,
        request.position_restricted,
        request.execution_restricted,
        request.review_required,
        request.hard_block,
    ]

    if not restriction_fields:
        return RestrictionDataState.PARTIAL

    return RestrictionDataState.COMPLETE


# ============================================================
# CONSISTENCY
# ============================================================

def evaluate_restriction_consistency(
    request: RestrictionRequest,
) -> RestrictionConsistency:

    if request is None:
        return RestrictionConsistency.UNKNOWN

    action = _restriction_action(request.action)

    if not action:
        return RestrictionConsistency.INCONSISTENT

    # --------------------------------------------------------
    # Explicit hard block always has deterministic meaning.
    # --------------------------------------------------------
    if request.hard_block:
        return RestrictionConsistency.CONSISTENT

    # --------------------------------------------------------
    # Expansion pathway semantics.
    # --------------------------------------------------------
    if _restriction_is_expansion(action):

        if request.reduce_restricted or request.exit_restricted:
            # These restrictions do not describe an entry pathway.
            # They must not create a false contradiction.
            pass

        if request.no_new_position:
            return RestrictionConsistency.CONSISTENT

        if request.new_entry_restricted:
            return RestrictionConsistency.CONSISTENT

        if request.add_position_restricted:
            return RestrictionConsistency.CONSISTENT

    # --------------------------------------------------------
    # Reduction pathway semantics.
    # --------------------------------------------------------
    if _restriction_is_reduction(action):

        # A restriction against new entry/addition does not
        # invalidate an exit/profit-booking pathway.
        if request.no_new_position:
            return RestrictionConsistency.CONSISTENT

        if request.new_entry_restricted:
            return RestrictionConsistency.CONSISTENT

        if request.add_position_restricted:
            return RestrictionConsistency.CONSISTENT

        if request.reduce_restricted or request.exit_restricted:
            return RestrictionConsistency.CONSISTENT

        if request.profit_booking_restricted:
            return RestrictionConsistency.CONSISTENT

    # --------------------------------------------------------
    # Planning pathways.
    # --------------------------------------------------------
    if _restriction_is_planning(action):

        if request.no_new_position or request.new_entry_restricted:
            return RestrictionConsistency.CONDITIONAL

        return RestrictionConsistency.CONSISTENT

    # --------------------------------------------------------
    # Hold/watch pathways.
    # --------------------------------------------------------
    if _restriction_is_hold(action):
        return RestrictionConsistency.CONSISTENT

    return RestrictionConsistency.UNKNOWN


# ============================================================
# COMPLETENESS
# ============================================================

def calculate_restriction_completeness(
    request: RestrictionRequest,
    requirements: Optional[RestrictionRequirements] = None,
) -> float:

    requirements = requirements or RestrictionRequirements()

    checks: List[bool] = []

    if requirements.require_market:
        checks.append(bool(_restriction_action(request.market)))

    if requirements.require_instrument:
        checks.append(bool(_restriction_action(request.instrument)))

    if requirements.require_action:
        checks.append(bool(_restriction_action(request.action)))

    if requirements.require_user_state:
        checks.append(request.user_restricted is not None)

    if requirements.require_account_state:
        checks.append(request.account_restricted is not None)

    if requirements.require_plan_state:
        checks.append(request.plan_restricted is not None)

    if requirements.require_restriction_state:
        checks.append(True)

    if requirements.require_metadata:
        checks.append(bool(request.metadata))

    if requirements.require_timestamp:
        checks.append(request.timestamp is not None)

    if not checks:
        return 0.0

    return round(
        sum(1 for item in checks if item) / len(checks) * 100.0,
        2,
    )


# ============================================================
# FLAG EXTRACTION
# ============================================================

def extract_restriction_flags(
    request: RestrictionRequest,
) -> List[str]:

    flags: List[str] = []

    if request.hard_block:
        flags.append("HARD_BLOCK")

    if request.user_restricted:
        flags.append("USER_RESTRICTED")

    if request.account_restricted:
        flags.append("ACCOUNT_RESTRICTED")

    if request.plan_restricted:
        flags.append("PLAN_RESTRICTED")

    if request.instrument_restricted:
        flags.append("INSTRUMENT_RESTRICTED")

    if request.market_restricted:
        flags.append("MARKET_RESTRICTED")

    if request.action_restricted:
        flags.append("ACTION_RESTRICTED")

    if request.direction_restricted:
        flags.append("DIRECTION_RESTRICTED")

    if request.strategy_restricted:
        flags.append("STRATEGY_RESTRICTED")

    if request.timeframe_restricted:
        flags.append("TIMEFRAME_RESTRICTED")

    if request.session_restricted:
        flags.append("SESSION_RESTRICTED")

    if request.time_restricted:
        flags.append("TIME_RESTRICTED")

    if request.expiry_restricted:
        flags.append("EXPIRY_RESTRICTED")

    if request.closing_window_restricted:
        flags.append("CLOSING_WINDOW_RESTRICTED")

    if request.review_required:
        flags.append("REVIEW_REQUIRED")

    return flags


# ============================================================
# RESTRICTION EXTRACTION
# ============================================================

def extract_restriction_restrictions(
    request: RestrictionRequest,
) -> List[str]:

    restrictions: List[str] = []

    action = _restriction_action(request.action)

    if request.new_entry_restricted and _restriction_is_expansion(action):
        restrictions.append("NEW_ENTRY_RESTRICTED")

    if request.add_position_restricted and _restriction_is_expansion(action):
        restrictions.append("ADD_POSITION_RESTRICTED")

    if request.reduce_restricted and _restriction_is_reduction(action):
        restrictions.append("REDUCE_RESTRICTED")

    if request.exit_restricted and _restriction_is_reduction(action):
        restrictions.append("EXIT_RESTRICTED")

    if request.profit_booking_restricted and _restriction_is_reduction(action):
        restrictions.append("PROFIT_BOOKING_RESTRICTED")

    if request.manual_only:
        restrictions.append("MANUAL_ONLY")

    if request.reduce_only:
        restrictions.append("REDUCE_ONLY")

    if request.close_only:
        restrictions.append("CLOSE_ONLY")

    if request.no_new_position and _restriction_is_expansion(action):
        restrictions.append("NO_NEW_POSITION")

    if request.policy_restricted:
        restrictions.append("POLICY_RESTRICTED")

    if request.compliance_restricted:
        restrictions.append("COMPLIANCE_RESTRICTED")

    if request.risk_restricted:
        restrictions.append("RISK_RESTRICTED")

    if request.exposure_restricted:
        restrictions.append("EXPOSURE_RESTRICTED")

    if request.position_restricted:
        restrictions.append("POSITION_RESTRICTED")

    if request.execution_restricted:
        restrictions.append("EXECUTION_RESTRICTED")

    return restrictions


# ============================================================
# REQUIREMENT EVALUATION
# ============================================================

def evaluate_restriction_requirements(
    request: RestrictionRequest,
    requirements: Optional[RestrictionRequirements] = None,
) -> Tuple[bool, List[str]]:

    requirements = requirements or RestrictionRequirements()

    unmet: List[str] = []

    if requirements.require_market and not _restriction_action(request.market):
        unmet.append("MARKET_REQUIRED")

    if (
        requirements.require_instrument
        and not _restriction_action(request.instrument)
    ):
        unmet.append("INSTRUMENT_REQUIRED")

    if requirements.require_action and not _restriction_action(request.action):
        unmet.append("ACTION_REQUIRED")

    if requirements.require_user_state:
        if request.user_restricted is None:
            unmet.append("USER_STATE_REQUIRED")

    if requirements.require_account_state:
        if request.account_restricted is None:
            unmet.append("ACCOUNT_STATE_REQUIRED")

    if requirements.require_plan_state:
        if request.plan_restricted is None:
            unmet.append("PLAN_STATE_REQUIRED")

    if requirements.require_metadata and not request.metadata:
        unmet.append("METADATA_REQUIRED")

    if requirements.require_timestamp and request.timestamp is None:
        unmet.append("TIMESTAMP_REQUIRED")

    if (
        not requirements.allow_unknown_restrictions
        and request.hard_block is None
    ):
        unmet.append("RESTRICTION_STATE_UNKNOWN")

    return len(unmet) == 0, unmet


# ============================================================
# READINESS
# ============================================================

def evaluate_restriction_readiness(
    request: RestrictionRequest,
    data_state: RestrictionDataState,
    consistency: RestrictionConsistency,
    requirements_met: bool,
    restrictions: Optional[List[str]] = None,
) -> RestrictionReadiness:

    restrictions = restrictions or []

    if data_state == RestrictionDataState.INVALID:
        return RestrictionReadiness.BLOCKED

    if consistency == RestrictionConsistency.INCONSISTENT:
        return RestrictionReadiness.BLOCKED

    if request.hard_block:
        return RestrictionReadiness.BLOCKED

    if not requirements_met:
        return RestrictionReadiness.NOT_READY

    if data_state == RestrictionDataState.MISSING:
        return RestrictionReadiness.NOT_READY

    if data_state == RestrictionDataState.PARTIAL:
        return RestrictionReadiness.CONDITIONALLY_READY

    if consistency == RestrictionConsistency.UNKNOWN:
        return RestrictionReadiness.CONDITIONALLY_READY

    if consistency == RestrictionConsistency.CONDITIONAL:
        return RestrictionReadiness.CONDITIONALLY_READY

    if restrictions:
        return RestrictionReadiness.CONDITIONALLY_READY

    return RestrictionReadiness.READY


# ============================================================
# RESTRICTION SCORE
# ============================================================

def calculate_restriction_score(
    data_state: RestrictionDataState,
    consistency: RestrictionConsistency,
    readiness: RestrictionReadiness,
    completeness: float,
    flags: Optional[List[str]] = None,
    restrictions: Optional[List[str]] = None,
) -> float:

    flags = flags or []
    restrictions = restrictions or []

    score = max(0.0, min(100.0, completeness))

    if data_state == RestrictionDataState.COMPLETE:
        score += 5.0
    elif data_state == RestrictionDataState.PARTIAL:
        score -= 10.0
    elif data_state == RestrictionDataState.MISSING:
        score -= 30.0
    elif data_state == RestrictionDataState.INVALID:
        score -= 60.0

    if consistency == RestrictionConsistency.CONSISTENT:
        score += 5.0
    elif consistency == RestrictionConsistency.CONDITIONAL:
        score -= 5.0
    elif consistency == RestrictionConsistency.UNKNOWN:
        score -= 15.0
    elif consistency == RestrictionConsistency.INCONSISTENT:
        score -= 50.0

    if readiness == RestrictionReadiness.READY:
        score += 5.0
    elif readiness == RestrictionReadiness.CONDITIONALLY_READY:
        score -= 5.0
    elif readiness == RestrictionReadiness.NOT_READY:
        score -= 20.0
    elif readiness == RestrictionReadiness.BLOCKED:
        score -= 60.0

    score -= min(30.0, len(flags) * 3.0)
    score -= min(25.0, len(restrictions) * 2.0)

    return round(max(0.0, min(100.0, score)), 2)


# ============================================================
# CONFIDENCE
# ============================================================

def calculate_restriction_confidence(
    data_state: RestrictionDataState,
    consistency: RestrictionConsistency,
    completeness: float,
) -> float:

    confidence = completeness

    if data_state == RestrictionDataState.COMPLETE:
        confidence += 5.0
    elif data_state == RestrictionDataState.PARTIAL:
        confidence -= 10.0
    elif data_state == RestrictionDataState.MISSING:
        confidence -= 35.0
    elif data_state == RestrictionDataState.INVALID:
        confidence -= 60.0

    if consistency == RestrictionConsistency.CONSISTENT:
        confidence += 5.0
    elif consistency == RestrictionConsistency.CONDITIONAL:
        confidence -= 5.0
    elif consistency == RestrictionConsistency.UNKNOWN:
        confidence -= 15.0
    elif consistency == RestrictionConsistency.INCONSISTENT:
        confidence -= 50.0

    return round(max(0.0, min(100.0, confidence)), 2)


# ============================================================
# ASSESSMENT BUILDER
# ============================================================

def build_restriction_assessment(
    request: RestrictionRequest,
    requirements: Optional[RestrictionRequirements] = None,
) -> RestrictionAssessment:

    requirements = requirements or RestrictionRequirements()

    data_state = evaluate_restriction_data_state(request)
    consistency = evaluate_restriction_consistency(request)

    requirements_met, unmet = evaluate_restriction_requirements(
        request,
        requirements,
    )

    flags = extract_restriction_flags(request)
    restrictions = extract_restriction_restrictions(request)

    readiness = evaluate_restriction_readiness(
        request=request,
        data_state=data_state,
        consistency=consistency,
        requirements_met=requirements_met,
        restrictions=restrictions,
    )

    completeness = calculate_restriction_completeness(
        request,
        requirements,
    )

    score = calculate_restriction_score(
        data_state=data_state,
        consistency=consistency,
        readiness=readiness,
        completeness=completeness,
        flags=flags,
        restrictions=restrictions,
    )

    confidence = calculate_restriction_confidence(
        data_state=data_state,
        consistency=consistency,
        completeness=completeness,
    )

    action = _restriction_action(request.action)

    if _restriction_is_reduction(action):
        pathway = "REDUCTION"
    elif _restriction_is_expansion(action):
        pathway = "EXPANSION"
    elif _restriction_is_hold(action):
        pathway = "HOLD"
    elif _restriction_is_planning(action):
        pathway = "PLANNING"
    else:
        pathway = "OTHER"

    if readiness == RestrictionReadiness.BLOCKED:
        status = RestrictionStatus.BLOCKED
    elif readiness == RestrictionReadiness.NOT_READY:
        status = RestrictionStatus.REVIEW_REQUIRED
    elif readiness == RestrictionReadiness.CONDITIONALLY_READY:
        status = RestrictionStatus.CONDITIONAL
    elif restrictions:
        status = RestrictionStatus.RESTRICTED
    else:
        status = RestrictionStatus.CLEAR

    notes: List[str] = [
        "Restriction assessment evaluates supplied control states.",
        "Restriction score is restriction-condition quality, not market probability.",
        "Restriction engine does not generate alpha or market direction.",
        "Closing-window restrictions do not automatically invalidate reduction pathways.",
    ]

    if _restriction_is_reduction(action):
        notes.append(
            "Reduction pathway semantics preserve EXIT/PROFIT_BOOK/PARTIAL_EXIT."
        )

    if _restriction_is_expansion(action):
        notes.append(
            "Expansion pathway semantics distinguish NEW_ENTRY/ADD/SCALE_IN."
        )

    return RestrictionAssessment(
        status=status,
        data_state=data_state,
        consistency=consistency,
        readiness=readiness,
        completeness=completeness,
        restriction_score=score,
        restriction_confidence=confidence,
        flags=tuple(flags),
        restrictions=tuple(restrictions),
        unmet_requirements=tuple(unmet),
        notes=tuple(notes),
        action=action,
        direction=_restriction_action(request.direction),
        pathway=pathway,
    )
# ============================================================
# ROBOMLM — CAS Restriction Engine
# Part 3: Decision / Action / Result / Contract / Engine
# ============================================================

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple


# ============================================================
# ACTION / CONTRACT / RESULT STATES
# ============================================================

class RestrictionActionState(str, Enum):
    PENDING = "PENDING"
    AUTHORIZED = "AUTHORIZED"
    RESTRICTED = "RESTRICTED"
    REVIEW = "REVIEW"
    BLOCKED = "BLOCKED"


class RestrictionContractState(str, Enum):
    CREATED = "CREATED"
    VALIDATED = "VALIDATED"
    ASSESSED = "ASSESSED"
    DECIDED = "DECIDED"
    AUTHORIZED = "AUTHORIZED"
    RESTRICTED = "RESTRICTED"
    REVIEW = "REVIEW"
    BLOCKED = "BLOCKED"
    REJECTED = "REJECTED"


class RestrictionResultStatus(str, Enum):
    ALLOWED = "ALLOWED"
    ALLOWED_WITH_RESTRICTION = "ALLOWED_WITH_RESTRICTION"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"


# ============================================================
# IMMUTABLE OUTPUT CONTRACTS
# ============================================================

@dataclass(frozen=True)
class RestrictionAction:
    action: str
    state: RestrictionActionState
    allowed: bool
    restricted: bool
    review_required: bool
    blocked: bool

    restrictions: Tuple[str, ...] = field(default_factory=tuple)
    flags: Tuple[str, ...] = field(default_factory=tuple)

    pathway: Optional[str] = None
    reason: str = ""


@dataclass(frozen=True)
class RestrictionResult:
    status: RestrictionResultStatus
    decision: RestrictionDecision
    restriction_status: RestrictionStatus

    allowed: bool
    restricted: bool
    review_required: bool
    blocked: bool

    action: RestrictionAction
    restrictions: Tuple[str, ...] = field(default_factory=tuple)
    flags: Tuple[str, ...] = field(default_factory=tuple)

    score: float = 0.0
    confidence: float = 0.0

    reason: str = ""
    request_id: Optional[str] = None


@dataclass(frozen=True)
class RestrictionContract:
    request: RestrictionRequest
    assessment: RestrictionAssessment
    action: RestrictionAction
    result: RestrictionResult

    state: RestrictionContractState
    status: RestrictionContractStatus

    contract_id: Optional[str] = None
    engine: str = RESTRICTION_ENGINE
    version: str = RESTRICTION_ENGINE_VERSION


# ============================================================
# RESULT STATUS
# ============================================================

def determine_restriction_result_status(
    assessment: RestrictionAssessment,
) -> RestrictionResultStatus:

    if assessment.status == RestrictionStatus.BLOCKED:
        return RestrictionResultStatus.BLOCKED

    if assessment.readiness == RestrictionReadiness.BLOCKED:
        return RestrictionResultStatus.BLOCKED

    if assessment.data_state == RestrictionDataState.INVALID:
        return RestrictionResultStatus.BLOCKED

    if assessment.consistency == RestrictionConsistency.INCONSISTENT:
        return RestrictionResultStatus.BLOCKED

    if assessment.readiness == RestrictionReadiness.NOT_READY:
        return RestrictionResultStatus.REVIEW_REQUIRED

    if assessment.status == RestrictionStatus.REVIEW_REQUIRED:
        return RestrictionResultStatus.REVIEW_REQUIRED

    if assessment.restrictions:
        return RestrictionResultStatus.ALLOWED_WITH_RESTRICTION

    if assessment.readiness == RestrictionReadiness.CONDITIONALLY_READY:
        return RestrictionResultStatus.ALLOWED_WITH_RESTRICTION

    if assessment.status == RestrictionStatus.RESTRICTED:
        return RestrictionResultStatus.ALLOWED_WITH_RESTRICTION

    return RestrictionResultStatus.ALLOWED


# ============================================================
# RESTRICTION STATUS
# ============================================================

def determine_restriction_status(
    assessment: RestrictionAssessment,
) -> RestrictionStatus:

    if assessment.readiness == RestrictionReadiness.BLOCKED:
        return RestrictionStatus.BLOCKED

    if assessment.data_state == RestrictionDataState.INVALID:
        return RestrictionStatus.BLOCKED

    if assessment.consistency == RestrictionConsistency.INCONSISTENT:
        return RestrictionStatus.BLOCKED

    if assessment.readiness == RestrictionReadiness.NOT_READY:
        return RestrictionStatus.REVIEW_REQUIRED

    if assessment.restrictions:
        return RestrictionStatus.RESTRICTED

    if assessment.readiness == RestrictionReadiness.CONDITIONALLY_READY:
        return RestrictionStatus.CONDITIONAL

    return RestrictionStatus.CLEAR


# ============================================================
# DECISION
# ============================================================

def determine_restriction_decision(
    assessment: RestrictionAssessment,
) -> RestrictionDecision:

    result_status = determine_restriction_result_status(assessment)

    if result_status == RestrictionResultStatus.BLOCKED:
        return RestrictionDecision.BLOCK

    if result_status == RestrictionResultStatus.REVIEW_REQUIRED:
        return RestrictionDecision.REVIEW_REQUIRED

    if result_status == RestrictionResultStatus.ALLOWED_WITH_RESTRICTION:
        return RestrictionDecision.ALLOW_WITH_RESTRICTION

    return RestrictionDecision.ALLOW


# ============================================================
# ACTION STATE
# ============================================================

def determine_restriction_action_state(
    decision: RestrictionDecision,
) -> RestrictionActionState:

    if decision == RestrictionDecision.BLOCK:
        return RestrictionActionState.BLOCKED

    if decision == RestrictionDecision.REVIEW_REQUIRED:
        return RestrictionActionState.REVIEW

    if decision == RestrictionDecision.ALLOW_WITH_RESTRICTION:
        return RestrictionActionState.RESTRICTED

    return RestrictionActionState.AUTHORIZED


# ============================================================
# ACTION BUILDER
# ============================================================

def build_restriction_action(
    request: RestrictionRequest,
    assessment: RestrictionAssessment,
    decision: RestrictionDecision,
) -> RestrictionAction:

    state = determine_restriction_action_state(decision)

    allowed = decision in {
        RestrictionDecision.ALLOW,
        RestrictionDecision.ALLOW_WITH_RESTRICTION,
    }

    restricted = decision == RestrictionDecision.ALLOW_WITH_RESTRICTION
    review_required = decision == RestrictionDecision.REVIEW_REQUIRED
    blocked = decision == RestrictionDecision.BLOCK

    if blocked:
        reason = "Restriction pathway is blocked."
    elif review_required:
        reason = "Restriction pathway requires review."
    elif restricted:
        reason = "Pathway is allowed subject to restrictions."
    else:
        reason = "Restriction pathway is clear."

    return RestrictionAction(
        action=str(request.action or "").strip().upper(),
        state=state,
        allowed=allowed,
        restricted=restricted,
        review_required=review_required,
        blocked=blocked,
        restrictions=assessment.restrictions,
        flags=assessment.flags,
        pathway=assessment.pathway,
        reason=reason,
    )


# ============================================================
# RESULT BUILDER
# ============================================================

def build_restriction_result(
    request: RestrictionRequest,
    assessment: RestrictionAssessment,
    action: RestrictionAction,
    decision: RestrictionDecision,
) -> RestrictionResult:

    status = determine_restriction_result_status(assessment)
    restriction_status = determine_restriction_status(assessment)

    return RestrictionResult(
        status=status,
        decision=decision,
        restriction_status=restriction_status,
        allowed=action.allowed,
        restricted=action.restricted,
        review_required=action.review_required,
        blocked=action.blocked,
        action=action,
        restrictions=assessment.restrictions,
        flags=assessment.flags,
        score=assessment.restriction_score,
        confidence=assessment.restriction_confidence,
        reason=action.reason,
        request_id=request.request_id,
    )


# ============================================================
# CONTRACT STATE
# ============================================================

def determine_restriction_contract_state(
    result: RestrictionResult,
) -> RestrictionContractState:

    if result.blocked:
        return RestrictionContractState.BLOCKED

    if result.review_required:
        return RestrictionContractState.REVIEW

    if result.restricted:
        return RestrictionContractState.RESTRICTED

    if result.allowed:
        return RestrictionContractState.AUTHORIZED

    return RestrictionContractState.REJECTED


# ============================================================
# CONTRACT STATUS
# ============================================================

def determine_restriction_contract_status(
    result: RestrictionResult,
) -> RestrictionContractStatus:

    if result.blocked:
        return RestrictionContractStatus.BLOCKED

    if result.review_required:
        return RestrictionContractStatus.REVIEW

    if result.restricted:
        return RestrictionContractStatus.RESTRICTED

    if result.allowed:
        return RestrictionContractStatus.READY

    return RestrictionContractStatus.INVALID


# ============================================================
# CONTRACT BUILDER
# ============================================================

def build_restriction_contract(
    request: RestrictionRequest,
    assessment: RestrictionAssessment,
    action: RestrictionAction,
    result: RestrictionResult,
) -> RestrictionContract:

    state = determine_restriction_contract_state(result)
    status = determine_restriction_contract_status(result)

    return RestrictionContract(
        request=request,
        assessment=assessment,
        action=action,
        result=result,
        state=state,
        status=status,
        contract_id=request.request_id,
    )


# ============================================================
# ENGINE
# ============================================================

class RestrictionEngine:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def engine_name(self) -> str:
        return RESTRICTION_ENGINE

    @property
    def engine_version(self) -> str:
        return RESTRICTION_ENGINE_VERSION

    def evaluate(
        self,
        request: RestrictionRequest,
        requirements: Optional[RestrictionRequirements] = None,
    ) -> RestrictionContract:

        if request is None:
            raise ValueError("RestrictionRequest is required.")

        validation = validate_restriction_request(request)

        if not validation.valid:
            assessment = RestrictionAssessment(
                status=RestrictionStatus.BLOCKED,
                data_state=RestrictionDataState.INVALID,
                consistency=RestrictionConsistency.INCONSISTENT,
                readiness=RestrictionReadiness.BLOCKED,
                completeness=0.0,
                restriction_score=0.0,
                restriction_confidence=0.0,
                flags=("INVALID_REQUEST",),
                restrictions=(),
                unmet_requirements=tuple(validation.errors),
                notes=("Restriction request validation failed.",),
                action=_restriction_action(request.action),
                direction=_restriction_action(request.direction),
                pathway="UNKNOWN",
            )
        else:
            assessment = build_restriction_assessment(
                request=request,
                requirements=requirements,
            )

        decision = determine_restriction_decision(assessment)

        action = build_restriction_action(
            request=request,
            assessment=assessment,
            decision=decision,
        )

        result = build_restriction_result(
            request=request,
            assessment=assessment,
            action=action,
            decision=decision,
        )

        return build_restriction_contract(
            request=request,
            assessment=assessment,
            action=action,
            result=result,
        )

    def check(
        self,
        request: RestrictionRequest,
        requirements: Optional[RestrictionRequirements] = None,
    ) -> RestrictionResult:

        return self.evaluate(
            request=request,
            requirements=requirements,
        ).result

    def review(
        self,
        request: RestrictionRequest,
        requirements: Optional[RestrictionRequirements] = None,
    ) -> RestrictionResult:

        contract = self.evaluate(
            request=request,
            requirements=requirements,
        )

        if contract.result.blocked:
            return contract.result

        return RestrictionResult(
            status=RestrictionResultStatus.REVIEW_REQUIRED,
            decision=RestrictionDecision.REVIEW_REQUIRED,
            restriction_status=RestrictionStatus.REVIEW_REQUIRED,
            allowed=False,
            restricted=False,
            review_required=True,
            blocked=False,
            action=RestrictionAction(
                action=contract.action.action,
                state=RestrictionActionState.REVIEW,
                allowed=False,
                restricted=False,
                review_required=True,
                blocked=False,
                restrictions=contract.action.restrictions,
                flags=contract.action.flags,
                pathway=contract.action.pathway,
                reason="Explicit restriction review requested.",
            ),
            restrictions=contract.result.restrictions,
            flags=contract.result.flags,
            score=contract.result.score,
            confidence=contract.result.confidence,
            reason="Explicit restriction review requested.",
            request_id=request.request_id,
        )


# ============================================================
# SINGLETON ACCESS
# ============================================================

_RESTRICTION_ENGINE_INSTANCE = RestrictionEngine()


def get_restriction_engine() -> RestrictionEngine:
    return _RESTRICTION_ENGINE_INSTANCE


# ============================================================
# PUBLIC API
# ============================================================

def evaluate_restriction(
    request: RestrictionRequest,
    requirements: Optional[RestrictionRequirements] = None,
) -> RestrictionContract:

    return get_restriction_engine().evaluate(
        request=request,
        requirements=requirements,
    )


def check_restriction(
    request: RestrictionRequest,
    requirements: Optional[RestrictionRequirements] = None,
) -> RestrictionResult:

    return get_restriction_engine().check(
        request=request,
        requirements=requirements,
    )


def review_restriction(
    request: RestrictionRequest,
    requirements: Optional[RestrictionRequirements] = None,
) -> RestrictionResult:

    return get_restriction_engine().review(
        request=request,
        requirements=requirements,
    )
# ============================================================
# ROBOMLM — CAS Restriction Engine
# Part 4: Validation / Safety / Authority / Audit / Health
# ============================================================


# ============================================================
# ACTION VALIDATION
# ============================================================

def validate_restriction_action(
    action: RestrictionAction,
) -> Tuple[bool, Tuple[str, ...]]:

    errors = []

    if action is None:
        return False, ("ACTION_REQUIRED",)

    if not action.action:
        errors.append("ACTION_REQUIRED")

    if not isinstance(action.state, RestrictionActionState):
        errors.append("INVALID_ACTION_STATE")

    if action.blocked and action.allowed:
        errors.append("BLOCKED_ACTION_CANNOT_BE_ALLOWED")

    if action.review_required and action.allowed:
        errors.append("REVIEW_ACTION_CANNOT_BE_AUTHORIZED")

    if action.restricted and not action.allowed:
        errors.append("RESTRICTED_ACTION_MUST_REMAIN_ALLOWED")

    return len(errors) == 0, tuple(errors)


# ============================================================
# RESULT VALIDATION
# ============================================================

def validate_restriction_result(
    result: RestrictionResult,
) -> Tuple[bool, Tuple[str, ...]]:

    errors = []

    if result is None:
        return False, ("RESULT_REQUIRED",)

    if not isinstance(result.status, RestrictionResultStatus):
        errors.append("INVALID_RESULT_STATUS")

    if not isinstance(result.decision, RestrictionDecision):
        errors.append("INVALID_DECISION")

    if result.blocked and result.allowed:
        errors.append("BLOCKED_RESULT_CANNOT_BE_ALLOWED")

    if result.review_required and result.allowed:
        errors.append("REVIEW_RESULT_CANNOT_BE_AUTHORIZED")

    if (
        result.status == RestrictionResultStatus.BLOCKED
        and not result.blocked
    ):
        errors.append("BLOCKED_STATUS_STATE_MISMATCH")

    if (
        result.status == RestrictionResultStatus.REVIEW_REQUIRED
        and not result.review_required
    ):
        errors.append("REVIEW_STATUS_STATE_MISMATCH")

    if (
        result.status
        == RestrictionResultStatus.ALLOWED_WITH_RESTRICTION
        and not result.restricted
    ):
        errors.append("RESTRICTED_STATUS_STATE_MISMATCH")

    action_ok, action_errors = validate_restriction_action(
        result.action
    )

    if not action_ok:
        errors.extend(action_errors)

    return len(errors) == 0, tuple(errors)


# ============================================================
# CONTRACT VALIDATION
# ============================================================

def validate_restriction_contract(
    contract: RestrictionContract,
) -> Tuple[bool, Tuple[str, ...]]:

    errors = []

    if contract is None:
        return False, ("CONTRACT_REQUIRED",)

    request_validation = validate_restriction_request(
        contract.request
    )

    if not request_validation.valid:
        errors.extend(request_validation.errors)

    result_ok, result_errors = validate_restriction_result(
        contract.result
    )

    if not result_ok:
        errors.extend(result_errors)

    if contract.assessment is None:
        errors.append("ASSESSMENT_REQUIRED")

    if contract.action is None:
        errors.append("ACTION_REQUIRED")

    if not isinstance(contract.state, RestrictionContractState):
        errors.append("INVALID_CONTRACT_STATE")

    if not isinstance(contract.status, RestrictionContractStatus):
        errors.append("INVALID_CONTRACT_STATUS")

    expected_state = determine_restriction_contract_state(
        contract.result
    )

    if contract.state != expected_state:
        errors.append("CONTRACT_STATE_MISMATCH")

    expected_status = determine_restriction_contract_status(
        contract.result
    )

    if contract.status != expected_status:
        errors.append("CONTRACT_STATUS_MISMATCH")

    return len(errors) == 0, tuple(errors)


# ============================================================
# READINESS / SAFETY
# ============================================================

def restriction_ready(
    contract: RestrictionContract,
) -> bool:

    if contract is None:
        return False

    return (
        contract.result.allowed
        and not contract.result.blocked
        and not contract.result.review_required
    )


def restriction_can_advance(
    contract: RestrictionContract,
) -> bool:

    if contract is None:
        return False

    if contract.result.blocked:
        return False

    if contract.result.review_required:
        return False

    return contract.result.allowed


def restriction_requires_review(
    contract: RestrictionContract,
) -> bool:

    if contract is None:
        return True

    return contract.result.review_required


def restriction_is_blocked(
    contract: RestrictionContract,
) -> bool:

    if contract is None:
        return True

    return contract.result.blocked


def restriction_is_restricted(
    contract: RestrictionContract,
) -> bool:

    if contract is None:
        return False

    return contract.result.restricted


def restriction_is_safe_for_next_gate(
    contract: RestrictionContract,
) -> bool:

    if contract is None:
        return False

    if contract.result.blocked:
        return False

    if contract.result.review_required:
        return False

    # ALLOW and ALLOW_WITH_RESTRICTION may advance,
    # but downstream gates must consume the restrictions.
    return contract.result.allowed


# ============================================================
# ACCESSORS
# ============================================================

def get_restriction_status(
    contract: RestrictionContract,
) -> RestrictionStatus:

    if contract is None:
        return RestrictionStatus.UNKNOWN

    return contract.result.restriction_status


def get_restriction_decision(
    contract: RestrictionContract,
) -> RestrictionDecision:

    if contract is None:
        return RestrictionDecision.BLOCK

    return contract.result.decision


def get_restriction_action_state(
    contract: RestrictionContract,
) -> RestrictionActionState:

    if contract is None:
        return RestrictionActionState.BLOCKED

    return contract.action.state


# ============================================================
# AUTHORITY BOUNDARIES
# ============================================================

def restriction_generates_market_decision() -> bool:
    return False


def restriction_generates_alpha() -> bool:
    return False


def restriction_modifies_d13() -> bool:
    return False


def restriction_overrides_d13() -> bool:
    return False


def restriction_replaces_risk_authority() -> bool:
    return False


def restriction_overrides_risk_authority() -> bool:
    return False


def restriction_overrides_cas() -> bool:
    return False


def restriction_authorizes_execution() -> bool:
    return False


def restriction_places_orders() -> bool:
    return False


def restriction_changes_position() -> bool:
    return False


def restriction_has_execution_authority() -> bool:
    return False


def restriction_has_market_decision_authority() -> bool:
    return False


def restriction_is_alpha_engine() -> bool:
    return False


def restriction_authority_integrity_ok() -> bool:
    return not any(
        (
            restriction_generates_market_decision(),
            restriction_generates_alpha(),
            restriction_modifies_d13(),
            restriction_overrides_d13(),
            restriction_replaces_risk_authority(),
            restriction_overrides_risk_authority(),
            restriction_overrides_cas(),
            restriction_authorizes_execution(),
            restriction_places_orders(),
            restriction_changes_position(),
            restriction_has_execution_authority(),
            restriction_has_market_decision_authority(),
            restriction_is_alpha_engine(),
        )
    )


def restriction_has_authority_conflict() -> bool:
    return not restriction_authority_integrity_ok()


# ============================================================
# AUDIT
# ============================================================

@dataclass(frozen=True)
class RestrictionAuditRecord:
    engine: str
    version: str

    request_id: Optional[str]

    action: Optional[str]
    pathway: Optional[str]

    status: RestrictionStatus
    decision: RestrictionDecision
    result_status: RestrictionResultStatus

    allowed: bool
    restricted: bool
    review_required: bool
    blocked: bool

    score: float
    confidence: float

    flags: Tuple[str, ...] = field(default_factory=tuple)
    restrictions: Tuple[str, ...] = field(default_factory=tuple)

    reason: str = ""


def build_restriction_audit(
    contract: RestrictionContract,
) -> RestrictionAuditRecord:

    if contract is None:
        raise ValueError("RestrictionContract is required.")

    result = contract.result
    assessment = contract.assessment

    return RestrictionAuditRecord(
        engine=RESTRICTION_ENGINE,
        version=RESTRICTION_ENGINE_VERSION,
        request_id=contract.request.request_id,
        action=contract.request.action,
        pathway=assessment.pathway,
        status=result.restriction_status,
        decision=result.decision,
        result_status=result.status,
        allowed=result.allowed,
        restricted=result.restricted,
        review_required=result.review_required,
        blocked=result.blocked,
        score=result.score,
        confidence=result.confidence,
        flags=result.flags,
        restrictions=result.restrictions,
        reason=result.reason,
    )


# ============================================================
# ENGINE HEALTH
# ============================================================

@dataclass(frozen=True)
class RestrictionEngineHealth:
    engine: str
    version: str

    operational: bool
    authority_integrity: bool

    validation_available: bool
    evaluation_available: bool
    audit_available: bool

    status: str
    message: str


def get_restriction_engine_health() -> RestrictionEngineHealth:

    authority_ok = restriction_authority_integrity_ok()

    operational = (
        authority_ok
        and callable(validate_restriction_request)
        and callable(build_restriction_assessment)
        and callable(evaluate_restriction)
        and callable(build_restriction_audit)
    )

    if operational:
        status = "HEALTHY"
        message = "Restriction Engine operational."
    else:
        status = "DEGRADED"
        message = "Restriction Engine authority or capability check failed."

    return RestrictionEngineHealth(
        engine=RESTRICTION_ENGINE,
        version=RESTRICTION_ENGINE_VERSION,
        operational=operational,
        authority_integrity=authority_ok,
        validation_available=callable(validate_restriction_request),
        evaluation_available=callable(evaluate_restriction),
        audit_available=callable(build_restriction_audit),
        status=status,
        message=message,
    )


# ============================================================
# ENGINE INFORMATION
# ============================================================

def get_restriction_engine_info() -> Dict[str, Any]:

    return {
        "engine": RESTRICTION_ENGINE,
        "version": RESTRICTION_ENGINE_VERSION,
        "role": "CAS restriction/control evaluation",
        "authority": "restriction_control_only",
        "generates_market_decision": False,
        "generates_alpha": False,
        "modifies_d13": False,
        "overrides_d13": False,
        "replaces_risk_authority": False,
        "overrides_cas": False,
        "authorizes_execution": False,
        "places_orders": False,
        "changes_position": False,
        "supports_reduction_pathways": True,
        "supports_profit_booking_pathways": True,
        "supports_closing_window_context": True,
        "supports_planning_pathways": True,
        "operational": get_restriction_engine_health().operational,
    }


def restriction_integrity_ok() -> bool:

    health = get_restriction_engine_health()

    return (
        health.operational
        and health.authority_integrity
    )
# ============================================================
# ROBOMLM — CAS Restriction Engine
# Part 5: Lifecycle / Serialization / Summary / Validation
# ============================================================


# ============================================================
# LIFECYCLE
# ============================================================

class RestrictionLifecycleState(str, Enum):
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
    RETAINED = "RETAINED"
    REJECTED = "REJECTED"


def determine_restriction_lifecycle(
    contract: RestrictionContract,
) -> RestrictionLifecycleState:

    if contract is None:
        return RestrictionLifecycleState.REJECTED

    if contract.result.blocked:
        return RestrictionLifecycleState.REJECTED

    if contract.result.review_required:
        return RestrictionLifecycleState.ACTIVE

    if contract.result.allowed:
        return RestrictionLifecycleState.ACTIVE

    return RestrictionLifecycleState.REJECTED


def freeze_restriction(
    contract: RestrictionContract,
) -> RestrictionLifecycleState:

    if contract is None:
        return RestrictionLifecycleState.REJECTED

    if contract.result.blocked:
        return RestrictionLifecycleState.REJECTED

    return RestrictionLifecycleState.FROZEN


def retain_restriction(
    contract: RestrictionContract,
) -> RestrictionLifecycleState:

    if contract is None:
        return RestrictionLifecycleState.REJECTED

    if contract.result.blocked:
        return RestrictionLifecycleState.REJECTED

    return RestrictionLifecycleState.RETAINED


def reject_restriction(
    contract: Optional[RestrictionContract] = None,
) -> RestrictionLifecycleState:

    return RestrictionLifecycleState.REJECTED


# ============================================================
# SERIALIZATION HELPERS
# ============================================================

def restriction_request_to_dict(
    request: RestrictionRequest,
) -> Dict[str, Any]:

    if request is None:
        return {}

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

        "user_restricted": request.user_restricted,
        "account_restricted": request.account_restricted,
        "plan_restricted": request.plan_restricted,

        "instrument_restricted": request.instrument_restricted,
        "market_restricted": request.market_restricted,
        "action_restricted": request.action_restricted,
        "direction_restricted": request.direction_restricted,

        "strategy_restricted": request.strategy_restricted,
        "timeframe_restricted": request.timeframe_restricted,
        "session_restricted": request.session_restricted,
        "time_restricted": request.time_restricted,
        "expiry_restricted": request.expiry_restricted,
        "closing_window_restricted": request.closing_window_restricted,

        "new_entry_restricted": request.new_entry_restricted,
        "add_position_restricted": request.add_position_restricted,
        "reduce_restricted": request.reduce_restricted,
        "exit_restricted": request.exit_restricted,
        "profit_booking_restricted": request.profit_booking_restricted,

        "manual_only": request.manual_only,
        "reduce_only": request.reduce_only,
        "close_only": request.close_only,
        "no_new_position": request.no_new_position,

        "policy_restricted": request.policy_restricted,
        "compliance_restricted": request.compliance_restricted,
        "risk_restricted": request.risk_restricted,
        "exposure_restricted": request.exposure_restricted,
        "position_restricted": request.position_restricted,
        "execution_restricted": request.execution_restricted,

        "review_required": request.review_required,
        "hard_block": request.hard_block,

        "metadata": dict(request.metadata or {}),
        "request_id": request.request_id,

        "timestamp": (
            request.timestamp.isoformat()
            if request.timestamp is not None
            else None
        ),
    }


def restriction_assessment_to_dict(
    assessment: RestrictionAssessment,
) -> Dict[str, Any]:

    if assessment is None:
        return {}

    return {
        "status": assessment.status.value,
        "data_state": assessment.data_state.value,
        "consistency": assessment.consistency.value,
        "readiness": assessment.readiness.value,

        "completeness": assessment.completeness,
        "restriction_score": assessment.restriction_score,
        "restriction_confidence": assessment.restriction_confidence,

        "flags": list(assessment.flags),
        "restrictions": list(assessment.restrictions),

        "unmet_requirements": list(
            assessment.unmet_requirements
        ),
        "notes": list(assessment.notes),

        "action": assessment.action,
        "direction": assessment.direction,
        "pathway": assessment.pathway,
    }


def restriction_action_to_dict(
    action: RestrictionAction,
) -> Dict[str, Any]:

    if action is None:
        return {}

    return {
        "action": action.action,
        "state": action.state.value,

        "allowed": action.allowed,
        "restricted": action.restricted,
        "review_required": action.review_required,
        "blocked": action.blocked,

        "restrictions": list(action.restrictions),
        "flags": list(action.flags),

        "pathway": action.pathway,
        "reason": action.reason,
    }


def restriction_result_to_dict(
    result: RestrictionResult,
) -> Dict[str, Any]:

    if result is None:
        return {}

    return {
        "status": result.status.value,
        "decision": result.decision.value,
        "restriction_status": result.restriction_status.value,

        "allowed": result.allowed,
        "restricted": result.restricted,
        "review_required": result.review_required,
        "blocked": result.blocked,

        "action": restriction_action_to_dict(
            result.action
        ),

        "restrictions": list(result.restrictions),
        "flags": list(result.flags),

        "score": result.score,
        "confidence": result.confidence,

        "reason": result.reason,
        "request_id": result.request_id,
    }


def restriction_contract_to_dict(
    contract: RestrictionContract,
) -> Dict[str, Any]:

    if contract is None:
        return {}

    return {
        "engine": contract.engine,
        "version": contract.version,
        "contract_id": contract.contract_id,

        "state": contract.state.value,
        "status": contract.status.value,

        "request": restriction_request_to_dict(
            contract.request
        ),
        "assessment": restriction_assessment_to_dict(
            contract.assessment
        ),
        "action": restriction_action_to_dict(
            contract.action
        ),
        "result": restriction_result_to_dict(
            contract.result
        ),
    }


# ============================================================
# SUMMARY
# ============================================================

def summarize_restriction(
    contract: RestrictionContract,
) -> Dict[str, Any]:

    if contract is None:
        return {
            "valid": False,
            "status": RestrictionStatus.UNKNOWN.value,
            "decision": RestrictionDecision.BLOCK.value,
            "reason": "Restriction contract is missing.",
        }

    result = contract.result
    assessment = contract.assessment

    return {
        "valid": True,

        "engine": contract.engine,
        "version": contract.version,

        "contract_id": contract.contract_id,

        "market": contract.request.market,
        "instrument": contract.request.instrument,
        "action": contract.request.action,
        "direction": contract.request.direction,

        "pathway": assessment.pathway,

        "status": result.restriction_status.value,
        "decision": result.decision.value,
        "result_status": result.status.value,

        "allowed": result.allowed,
        "restricted": result.restricted,
        "review_required": result.review_required,
        "blocked": result.blocked,

        "restriction_score": result.score,
        "restriction_confidence": result.confidence,

        "flags": list(result.flags),
        "restrictions": list(result.restrictions),

        "reason": result.reason,
    }


# ============================================================
# AUTHORITY STATEMENT
# ============================================================

def get_restriction_authority_statement() -> str:

    return (
        "Restriction Engine is a CAS internal restriction/control "
        "engine. It evaluates supplied restriction states and "
        "pathway constraints. It does not generate market decisions "
        "or alpha, does not modify or override D13, does not replace "
        "Risk Authority, does not override CAS, does not authorize "
        "execution, does not place orders, and does not change "
        "positions."
    )


# ============================================================
# OPERATIONAL CHECK
# ============================================================

def restriction_engine_operational() -> bool:

    return restriction_integrity_ok()


# ============================================================
# FULL VALIDATION
# ============================================================

def validate_restriction(
    contract: RestrictionContract,
) -> Tuple[bool, Tuple[str, ...]]:

    if contract is None:
        return False, ("CONTRACT_REQUIRED",)

    errors = []

    contract_ok, contract_errors = validate_restriction_contract(
        contract
    )

    if not contract_ok:
        errors.extend(contract_errors)

    if not restriction_authority_integrity_ok():
        errors.append("AUTHORITY_INTEGRITY_FAILURE")

    if not restriction_engine_operational():
        errors.append("ENGINE_NOT_OPERATIONAL")

    return len(errors) == 0, tuple(errors)


# ============================================================
# SNAPSHOT
# ============================================================

def restriction_snapshot(
    contract: RestrictionContract,
) -> Dict[str, Any]:

    if contract is None:
        return {
            "engine": RESTRICTION_ENGINE,
            "version": RESTRICTION_ENGINE_VERSION,
            "valid": False,
            "operational": restriction_engine_operational(),
        }

    valid, errors = validate_restriction(contract)

    return {
        "engine": RESTRICTION_ENGINE,
        "version": RESTRICTION_ENGINE_VERSION,

        "valid": valid,
        "errors": list(errors),

        "operational": restriction_engine_operational(),
        "authority_integrity": restriction_authority_integrity_ok(),

        "contract_state": contract.state.value,
        "contract_status": contract.status.value,

        "result_status": contract.result.status.value,
        "decision": contract.result.decision.value,

        "allowed": contract.result.allowed,
        "restricted": contract.result.restricted,
        "review_required": contract.result.review_required,
        "blocked": contract.result.blocked,

        "action": contract.action.action,
        "pathway": contract.action.pathway,

        "restriction_score": contract.result.score,
        "restriction_confidence": contract.result.confidence,

        "flags": list(contract.result.flags),
        "restrictions": list(contract.result.restrictions),

        "authority": {
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
        },
    }


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [
    # Constants
    "RESTRICTION_ENGINE",
    "RESTRICTION_ENGINE_VERSION",

    # Enums
    "RestrictionStatus",
    "RestrictionDecision",
    "RestrictionMode",
    "RestrictionPriority",
    "RestrictionContractStatus",

    "RestrictionDataState",
    "RestrictionConsistency",
    "RestrictionReadiness",

    "RestrictionActionState",
    "RestrictionContractState",
    "RestrictionResultStatus",

    "RestrictionLifecycleState",

    # Contracts
    "RestrictionRequest",
    "RestrictionReference",
    "RestrictionContractValidation",
    "RestrictionRequirements",
    "RestrictionAssessment",

    "RestrictionAction",
    "RestrictionResult",
    "RestrictionContract",

    "RestrictionAuditRecord",
    "RestrictionEngineHealth",

    # Builders / evaluation
    "build_restriction_request",
    "validate_restriction_request",

    "evaluate_restriction_data_state",
    "evaluate_restriction_consistency",
    "calculate_restriction_completeness",
    "evaluate_restriction_requirements",
    "evaluate_restriction_readiness",

    "extract_restriction_flags",
    "extract_restriction_restrictions",

    "calculate_restriction_score",
    "calculate_restriction_confidence",

    "build_restriction_assessment",

    "determine_restriction_result_status",
    "determine_restriction_status",
    "determine_restriction_decision",
    "determine_restriction_action_state",

    "build_restriction_action",
    "build_restriction_result",

    "determine_restriction_contract_state",
    "determine_restriction_contract_status",
    "build_restriction_contract",

    # Engine
    "RestrictionEngine",
    "get_restriction_engine",
    "evaluate_restriction",
    "check_restriction",
    "review_restriction",

    # Validation
    "validate_restriction_action",
    "validate_restriction_result",
    "validate_restriction_contract",
    "validate_restriction",

    # Readiness / safety
    "restriction_ready",
    "restriction_can_advance",
    "restriction_requires_review",
    "restriction_is_blocked",
    "restriction_is_restricted",
    "restriction_is_safe_for_next_gate",

    # Accessors
    "get_restriction_status",
    "get_restriction_decision",
    "get_restriction_action_state",

    # Authority
    "restriction_generates_market_decision",
    "restriction_generates_alpha",
    "restriction_modifies_d13",
    "restriction_overrides_d13",
    "restriction_replaces_risk_authority",
    "restriction_overrides_risk_authority",
    "restriction_overrides_cas",
    "restriction_authorizes_execution",
    "restriction_places_orders",
    "restriction_changes_position",
    "restriction_has_execution_authority",
    "restriction_has_market_decision_authority",
    "restriction_is_alpha_engine",

    "restriction_authority_integrity_ok",
    "restriction_has_authority_conflict",

    # Audit / health
    "build_restriction_audit",
    "get_restriction_engine_health",
    "get_restriction_engine_info",
    "restriction_integrity_ok",

    # Lifecycle
    "determine_restriction_lifecycle",
    "freeze_restriction",
    "retain_restriction",
    "reject_restriction",

    # Serialization / utility
    "restriction_request_to_dict",
    "restriction_assessment_to_dict",
    "restriction_action_to_dict",
    "restriction_result_to_dict",
    "restriction_contract_to_dict",
    "summarize_restriction",
    "get_restriction_authority_statement",
    "restriction_engine_operational",
    "restriction_snapshot",
]