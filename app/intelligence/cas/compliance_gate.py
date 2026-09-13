# app/intelligence/cas/compliance_gate.py

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Optional


# ============================================================
# COMPLIANCE GATE — CORE CONSTANTS
# ============================================================

COMPLIANCE_GATE_ENGINE = "ROBOMLM_CAS_COMPLIANCE_GATE"
COMPLIANCE_GATE_VERSION = "1.0"


# ============================================================
# ENUMS
# ============================================================

class ComplianceStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    COMPLIANT = "COMPLIANT"
    CONDITIONAL = "CONDITIONAL"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    NON_COMPLIANT = "NON_COMPLIANT"
    BLOCKED = "BLOCKED"


class ComplianceDecision(str, Enum):
    ALLOW = "ALLOW"
    ALLOW_WITH_RESTRICTION = "ALLOW_WITH_RESTRICTION"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCK = "BLOCK"


class ComplianceMode(str, Enum):
    PAPER = "PAPER"
    DEMO = "DEMO"
    LIVE = "LIVE"
    UNKNOWN = "UNKNOWN"


class CompliancePriority(str, Enum):
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ComplianceContractStatus(str, Enum):
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
class ComplianceRequest:
    """
    CAS Compliance Gate input contract.

    This gate evaluates supplied account, permission, policy,
    jurisdiction and trading-restriction information.

    It does NOT:
        - generate market alpha
        - generate market direction
        - modify D13
        - replace Risk Authority
        - execute orders
        - mutate positions
        - invent jurisdiction-specific legal rules
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
    # ACTION
    # --------------------------------------------------------
    action: Optional[str] = None
    direction: Optional[str] = None

    # --------------------------------------------------------
    # EXECUTION CONTEXT
    # --------------------------------------------------------
    mode: ComplianceMode = ComplianceMode.UNKNOWN
    strategy: Optional[str] = None
    timeframe: Optional[str] = None
    priority: CompliancePriority = CompliancePriority.NORMAL

    # --------------------------------------------------------
    # VENUE / JURISDICTION
    # --------------------------------------------------------
    broker: Optional[str] = None
    venue: Optional[str] = None
    jurisdiction: Optional[str] = None

    # --------------------------------------------------------
    # USER / ACCOUNT ELIGIBILITY
    # --------------------------------------------------------
    user_eligible: Optional[bool] = None
    account_eligible: Optional[bool] = None

    # --------------------------------------------------------
    # PERMISSION / AUTHORIZATION
    # --------------------------------------------------------
    permission: Optional[bool] = None
    authorized: Optional[bool] = None

    # --------------------------------------------------------
    # RESTRICTED / PROHIBITED STATES
    # --------------------------------------------------------
    restricted_action: Optional[bool] = None
    prohibited_action: Optional[bool] = None

    restricted_instrument: Optional[bool] = None
    prohibited_instrument: Optional[bool] = None

    # --------------------------------------------------------
    # TRADING RESTRICTIONS
    # --------------------------------------------------------
    trading_restricted: Optional[bool] = None
    market_restricted: Optional[bool] = None

    session_restricted: Optional[bool] = None
    time_restricted: Optional[bool] = None

    # --------------------------------------------------------
    # COMPLIANCE FLAGS
    # --------------------------------------------------------
    compliance_required: Optional[bool] = None
    compliance_review_required: Optional[bool] = None
    compliance_hold: Optional[bool] = None
    compliance_breach: Optional[bool] = None

    # --------------------------------------------------------
    # OPTIONAL POLICY / EXTERNAL CONTROL FLAGS
    # --------------------------------------------------------
    policy_allowed: Optional[bool] = None
    policy_restricted: Optional[bool] = None
    policy_blocked: Optional[bool] = None

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
class ComplianceReference:
    """
    Reference information used to explain why a compliance
    decision was produced.

    Values are descriptive/control references only.
    """

    source: Optional[str] = None
    policy_id: Optional[str] = None
    rule_id: Optional[str] = None
    jurisdiction: Optional[str] = None
    description: Optional[str] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


# ============================================================
# VALIDATION CONTRACT
# ============================================================

@dataclass(frozen=True)
class ComplianceContractValidation:
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

def _cg_read_value(
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


def _cg_text(value: Any) -> Optional[str]:
    """
    Normalize textual values.
    """
    if value is None:
        return None

    text = str(value).strip()

    return text if text else None


def _cg_enum(
    value: Any,
    enum_type: type[Enum],
    default: Enum,
) -> Enum:
    """
    Normalize enum values without raising on unknown external data.
    """
    if value is None:
        return default

    if isinstance(value, enum_type):
        return value

    text = str(value).strip().upper()

    for member in enum_type:
        if text in {member.name.upper(), str(member.value).upper()}:
            return member

    return default


def _cg_number(value: Any) -> Optional[float]:
    """
    Safely normalize numeric compliance fields when supplied.
    """
    if value is None:
        return None

    if isinstance(value, bool):
        return None

    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    return number


def _cg_bool(value: Any) -> Optional[bool]:
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


def _cg_timestamp(value: Any = None) -> datetime:
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

def build_compliance_request(
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
    broker: Optional[str] = None,
    venue: Optional[str] = None,
    jurisdiction: Optional[str] = None,
    user_eligible: Optional[bool] = None,
    account_eligible: Optional[bool] = None,
    permission: Optional[bool] = None,
    authorized: Optional[bool] = None,
    restricted_action: Optional[bool] = None,
    prohibited_action: Optional[bool] = None,
    restricted_instrument: Optional[bool] = None,
    prohibited_instrument: Optional[bool] = None,
    trading_restricted: Optional[bool] = None,
    market_restricted: Optional[bool] = None,
    session_restricted: Optional[bool] = None,
    time_restricted: Optional[bool] = None,
    compliance_required: Optional[bool] = None,
    compliance_review_required: Optional[bool] = None,
    compliance_hold: Optional[bool] = None,
    compliance_breach: Optional[bool] = None,
    policy_allowed: Optional[bool] = None,
    policy_restricted: Optional[bool] = None,
    policy_blocked: Optional[bool] = None,
    metadata: Optional[Mapping[str, Any]] = None,
    request_id: Optional[str] = None,
    timestamp: Any = None,
) -> ComplianceRequest:
    """
    Build a normalized ComplianceRequest.

    Explicit keyword values take precedence over source values.
    """

    def pick(value: Any, name: str) -> Any:
        return value if value is not None else _cg_read_value(source, name)

    return ComplianceRequest(
        market=_cg_text(pick(market, "market")),
        instrument=_cg_text(pick(instrument, "instrument")),
        contract=_cg_text(pick(contract, "contract")),

        user_id=_cg_text(pick(user_id, "user_id")),
        account_id=_cg_text(pick(account_id, "account_id")),
        plan_id=_cg_text(pick(plan_id, "plan_id")),

        action=_cg_text(pick(action, "action")),
        direction=_cg_text(pick(direction, "direction")),

        mode=_cg_enum(
            pick(mode, "mode"),
            ComplianceMode,
            ComplianceMode.UNKNOWN,
        ),

        strategy=_cg_text(pick(strategy, "strategy")),
        timeframe=_cg_text(pick(timeframe, "timeframe")),

        priority=_cg_enum(
            pick(priority, "priority"),
            CompliancePriority,
            CompliancePriority.NORMAL,
        ),

        broker=_cg_text(pick(broker, "broker")),
        venue=_cg_text(pick(venue, "venue")),
        jurisdiction=_cg_text(
            pick(jurisdiction, "jurisdiction")
        ),

        user_eligible=_cg_bool(
            pick(user_eligible, "user_eligible")
        ),
        account_eligible=_cg_bool(
            pick(account_eligible, "account_eligible")
        ),

        permission=_cg_bool(
            pick(permission, "permission")
        ),
        authorized=_cg_bool(
            pick(authorized, "authorized")
        ),

        restricted_action=_cg_bool(
            pick(restricted_action, "restricted_action")
        ),
        prohibited_action=_cg_bool(
            pick(prohibited_action, "prohibited_action")
        ),

        restricted_instrument=_cg_bool(
            pick(
                restricted_instrument,
                "restricted_instrument",
            )
        ),
        prohibited_instrument=_cg_bool(
            pick(
                prohibited_instrument,
                "prohibited_instrument",
            )
        ),

        trading_restricted=_cg_bool(
            pick(trading_restricted, "trading_restricted")
        ),
        market_restricted=_cg_bool(
            pick(market_restricted, "market_restricted")
        ),

        session_restricted=_cg_bool(
            pick(session_restricted, "session_restricted")
        ),
        time_restricted=_cg_bool(
            pick(time_restricted, "time_restricted")
        ),

        compliance_required=_cg_bool(
            pick(compliance_required, "compliance_required")
        ),
        compliance_review_required=_cg_bool(
            pick(
                compliance_review_required,
                "compliance_review_required",
            )
        ),
        compliance_hold=_cg_bool(
            pick(compliance_hold, "compliance_hold")
        ),
        compliance_breach=_cg_bool(
            pick(compliance_breach, "compliance_breach")
        ),

        policy_allowed=_cg_bool(
            pick(policy_allowed, "policy_allowed")
        ),
        policy_restricted=_cg_bool(
            pick(policy_restricted, "policy_restricted")
        ),
        policy_blocked=_cg_bool(
            pick(policy_blocked, "policy_blocked")
        ),

        metadata=(
            dict(metadata)
            if metadata is not None
            else dict(
                _cg_read_value(
                    source,
                    "metadata",
                    {},
                ) or {}
            )
        ),

        request_id=_cg_text(
            pick(request_id, "request_id")
        ),

        timestamp=_cg_timestamp(
            pick(timestamp, "timestamp")
        ),
    )


# ============================================================
# NUMERIC VALIDATION
# ============================================================

def validate_compliance_numeric_inputs(
    request: ComplianceRequest,
) -> tuple[str, ...]:
    """
    Compliance Gate currently has no mandatory quantitative
    threshold model.

    This hook exists so future supplied policy thresholds can
    be validated without changing the public contract.
    """

    errors: list[str] = []

    if not isinstance(request, ComplianceRequest):
        errors.append("REQUEST_TYPE_INVALID")

    return tuple(errors)


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_compliance_request(
    request: ComplianceRequest,
) -> ComplianceContractValidation:
    """
    Validate the structural integrity of ComplianceRequest.

    Missing policy information is handled as REVIEW/UNKNOWN
    downstream rather than inventing a compliance rule.
    """

    errors: list[str] = []
    warnings: list[str] = []
    missing: list[str] = []

    if not isinstance(request, ComplianceRequest):
        return ComplianceContractValidation(
            valid=False,
            errors=("REQUEST_TYPE_INVALID",),
        )

    numeric_errors = validate_compliance_numeric_inputs(request)
    errors.extend(numeric_errors)

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
    # ACCOUNT CONTEXT
    # --------------------------------------------------------
    if not request.user_id:
        warnings.append("USER_ID_MISSING")

    if not request.account_id:
        warnings.append("ACCOUNT_ID_MISSING")

    # --------------------------------------------------------
    # PERMISSION CONTEXT
    # --------------------------------------------------------
    if request.permission is None:
        warnings.append("PERMISSION_UNKNOWN")

    if request.authorized is None:
        warnings.append("AUTHORIZATION_UNKNOWN")

    # --------------------------------------------------------
    # ELIGIBILITY CONTEXT
    # --------------------------------------------------------
    if request.user_eligible is None:
        warnings.append("USER_ELIGIBILITY_UNKNOWN")

    if request.account_eligible is None:
        warnings.append("ACCOUNT_ELIGIBILITY_UNKNOWN")

    # --------------------------------------------------------
    # JURISDICTION / POLICY CONTEXT
    # --------------------------------------------------------
    if not request.jurisdiction:
        warnings.append("JURISDICTION_NOT_SUPPLIED")

    if (
        request.compliance_required is True
        and request.compliance_review_required is None
    ):
        warnings.append("COMPLIANCE_REVIEW_STATE_UNKNOWN")

    # --------------------------------------------------------
    # HARD STRUCTURAL ERROR
    # --------------------------------------------------------
    if missing:
        errors.extend(
            f"REQUIRED_FIELD_MISSING:{field}"
            for field in missing
        )

    return ComplianceContractValidation(
        valid=not errors,
        errors=tuple(errors),
        warnings=tuple(warnings),
        missing_fields=tuple(missing),
    )
# app/intelligence/cas/compliance_gate.py
# PART 2/5
# Continue directly after Part 1


# ============================================================
# COMPLIANCE DATA STATE
# ============================================================

class ComplianceDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    INVALID = "INVALID"


class ComplianceConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONDITIONAL = "CONDITIONAL"
    INCONSISTENT = "INCONSISTENT"
    UNKNOWN = "UNKNOWN"


class ComplianceReadiness(str, Enum):
    READY = "READY"
    CONDITIONALLY_READY = "CONDITIONALLY_READY"
    NOT_READY = "NOT_READY"
    BLOCKED = "BLOCKED"


# ============================================================
# REQUIREMENTS
# ============================================================

@dataclass(frozen=True)
class ComplianceRequirements:
    """
    Requirements required for CAS compliance evaluation.

    These are ROBOMLM control requirements, not invented
    jurisdiction-specific legal rules.
    """

    require_market: bool = True
    require_instrument: bool = True
    require_action: bool = True

    require_user_eligibility: bool = False
    require_account_eligibility: bool = False

    require_permission: bool = False
    require_authorization: bool = False

    require_jurisdiction: bool = False

    require_policy_state: bool = False

    require_compliance_state: bool = False


# ============================================================
# ASSESSMENT CONTRACT
# ============================================================

@dataclass(frozen=True)
class ComplianceAssessment:
    data_state: ComplianceDataState
    consistency: ComplianceConsistency
    readiness: ComplianceReadiness

    completeness: float
    compliance_score: float
    compliance_confidence: float

    flags: tuple[str, ...] = ()
    restrictions: tuple[str, ...] = ()
    unmet_requirements: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    references: tuple[ComplianceReference, ...] = ()

    evaluated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# ============================================================
# DATA STATE EVALUATION
# ============================================================

def evaluate_compliance_data_state(
    request: ComplianceRequest,
) -> ComplianceDataState:

    validation = validate_compliance_request(request)

    if not validation.valid:
        return ComplianceDataState.INVALID

    supplied_core = [
        request.market,
        request.instrument,
        request.action,
    ]

    if not any(supplied_core):
        return ComplianceDataState.MISSING

    optional_controls = [
        request.user_eligible,
        request.account_eligible,
        request.permission,
        request.authorized,
        request.policy_allowed,
        request.policy_restricted,
        request.policy_blocked,
        request.compliance_required,
        request.compliance_review_required,
    ]

    supplied_optional = sum(
        value is not None
        for value in optional_controls
    )

    if supplied_optional == 0:
        return ComplianceDataState.PARTIAL

    if supplied_optional < len(optional_controls):
        return ComplianceDataState.PARTIAL

    return ComplianceDataState.COMPLETE


# ============================================================
# CONSISTENCY EVALUATION
# ============================================================

def evaluate_compliance_consistency(
    request: ComplianceRequest,
) -> ComplianceConsistency:

    validation = validate_compliance_request(request)

    if not validation.valid:
        return ComplianceConsistency.INCONSISTENT

    # --------------------------------------------------------
    # EXPLICIT BLOCK / BREACH STATES
    # --------------------------------------------------------
    if request.compliance_breach is True:
        return ComplianceConsistency.INCONSISTENT

    if request.compliance_hold is True:
        return ComplianceConsistency.INCONSISTENT

    if request.prohibited_action is True:
        return ComplianceConsistency.INCONSISTENT

    if request.prohibited_instrument is True:
        return ComplianceConsistency.INCONSISTENT

    if request.policy_blocked is True:
        return ComplianceConsistency.INCONSISTENT

    # --------------------------------------------------------
    # EXPLICIT CONTRADICTIONS
    # --------------------------------------------------------
    if (
        request.policy_allowed is True
        and request.policy_blocked is True
    ):
        return ComplianceConsistency.INCONSISTENT

    if (
        request.authorized is False
        and request.permission is True
    ):
        return ComplianceConsistency.CONDITIONAL

    if (
        request.authorized is True
        and request.permission is False
    ):
        return ComplianceConsistency.CONDITIONAL

    # --------------------------------------------------------
    # ELIGIBILITY CONTRADICTIONS
    # --------------------------------------------------------
    if request.user_eligible is False:
        return ComplianceConsistency.INCONSISTENT

    if request.account_eligible is False:
        return ComplianceConsistency.INCONSISTENT

    # --------------------------------------------------------
    # RESTRICTED STATES
    # --------------------------------------------------------
    restricted_values = (
        request.restricted_action,
        request.restricted_instrument,
        request.trading_restricted,
        request.market_restricted,
        request.session_restricted,
        request.time_restricted,
        request.policy_restricted,
    )

    if any(value is True for value in restricted_values):
        return ComplianceConsistency.CONDITIONAL

    # --------------------------------------------------------
    # UNKNOWN CONTROL STATE
    # --------------------------------------------------------
    controls = (
        request.permission,
        request.authorized,
        request.user_eligible,
        request.account_eligible,
    )

    if any(value is None for value in controls):
        return ComplianceConsistency.UNKNOWN

    return ComplianceConsistency.CONSISTENT


# ============================================================
# COMPLETENESS
# ============================================================

def calculate_compliance_completeness(
    request: ComplianceRequest,
    requirements: Optional[ComplianceRequirements] = None,
) -> float:

    requirements = (
        requirements or ComplianceRequirements()
    )

    checks: list[bool] = []

    if requirements.require_market:
        checks.append(bool(request.market))

    if requirements.require_instrument:
        checks.append(bool(request.instrument))

    if requirements.require_action:
        checks.append(bool(request.action))

    if requirements.require_user_eligibility:
        checks.append(
            request.user_eligible is not None
        )

    if requirements.require_account_eligibility:
        checks.append(
            request.account_eligible is not None
        )

    if requirements.require_permission:
        checks.append(
            request.permission is not None
        )

    if requirements.require_authorization:
        checks.append(
            request.authorized is not None
        )

    if requirements.require_jurisdiction:
        checks.append(
            bool(request.jurisdiction)
        )

    if requirements.require_policy_state:
        checks.append(
            any(
                value is not None
                for value in (
                    request.policy_allowed,
                    request.policy_restricted,
                    request.policy_blocked,
                )
            )
        )

    if requirements.require_compliance_state:
        checks.append(
            any(
                value is not None
                for value in (
                    request.compliance_required,
                    request.compliance_review_required,
                    request.compliance_hold,
                    request.compliance_breach,
                )
            )
        )

    if not checks:
        return 100.0

    return round(
        (sum(checks) / len(checks)) * 100.0,
        4,
    )


# ============================================================
# REQUIREMENT EVALUATION
# ============================================================

def evaluate_compliance_requirements(
    request: ComplianceRequest,
    requirements: Optional[ComplianceRequirements] = None,
) -> tuple[tuple[str, ...], tuple[str, ...]]:

    requirements = (
        requirements or ComplianceRequirements()
    )

    unmet: list[str] = []
    warnings: list[str] = []

    if requirements.require_market and not request.market:
        unmet.append("MARKET_REQUIRED")

    if (
        requirements.require_instrument
        and not request.instrument
    ):
        unmet.append("INSTRUMENT_REQUIRED")

    if requirements.require_action and not request.action:
        unmet.append("ACTION_REQUIRED")

    if (
        requirements.require_user_eligibility
        and request.user_eligible is None
    ):
        unmet.append("USER_ELIGIBILITY_REQUIRED")

    if (
        requirements.require_account_eligibility
        and request.account_eligible is None
    ):
        unmet.append("ACCOUNT_ELIGIBILITY_REQUIRED")

    if (
        requirements.require_permission
        and request.permission is None
    ):
        unmet.append("PERMISSION_REQUIRED")

    if (
        requirements.require_authorization
        and request.authorized is None
    ):
        unmet.append("AUTHORIZATION_REQUIRED")

    if (
        requirements.require_jurisdiction
        and not request.jurisdiction
    ):
        unmet.append("JURISDICTION_REQUIRED")

    if requirements.require_policy_state:
        if not any(
            value is not None
            for value in (
                request.policy_allowed,
                request.policy_restricted,
                request.policy_blocked,
            )
        ):
            unmet.append("POLICY_STATE_REQUIRED")

    if requirements.require_compliance_state:
        if not any(
            value is not None
            for value in (
                request.compliance_required,
                request.compliance_review_required,
                request.compliance_hold,
                request.compliance_breach,
            )
        ):
            unmet.append("COMPLIANCE_STATE_REQUIRED")

    # --------------------------------------------------------
    # INFORMATIONAL WARNINGS
    # --------------------------------------------------------
    if request.jurisdiction is None:
        warnings.append("JURISDICTION_UNKNOWN")

    if request.permission is None:
        warnings.append("PERMISSION_UNKNOWN")

    if request.authorized is None:
        warnings.append("AUTHORIZATION_UNKNOWN")

    return tuple(unmet), tuple(warnings)


# ============================================================
# READINESS
# ============================================================

def evaluate_compliance_readiness(
    data_state: ComplianceDataState,
    consistency: ComplianceConsistency,
    unmet_requirements: tuple[str, ...],
) -> ComplianceReadiness:

    if data_state == ComplianceDataState.INVALID:
        return ComplianceReadiness.BLOCKED

    if consistency == ComplianceConsistency.INCONSISTENT:
        return ComplianceReadiness.BLOCKED

    if unmet_requirements:
        return ComplianceReadiness.NOT_READY

    if data_state == ComplianceDataState.MISSING:
        return ComplianceReadiness.NOT_READY

    if consistency == ComplianceConsistency.CONDITIONAL:
        return ComplianceReadiness.CONDITIONALLY_READY

    if consistency == ComplianceConsistency.UNKNOWN:
        return ComplianceReadiness.CONDITIONALLY_READY

    if data_state == ComplianceDataState.PARTIAL:
        return ComplianceReadiness.CONDITIONALLY_READY

    return ComplianceReadiness.READY


# ============================================================
# FLAG EXTRACTION
# ============================================================

def extract_compliance_flags(
    request: ComplianceRequest,
) -> tuple[str, ...]:

    flags: list[str] = []

    if request.compliance_breach is True:
        flags.append("COMPLIANCE_BREACH")

    if request.compliance_hold is True:
        flags.append("COMPLIANCE_HOLD")

    if request.prohibited_action is True:
        flags.append("PROHIBITED_ACTION")

    if request.prohibited_instrument is True:
        flags.append("PROHIBITED_INSTRUMENT")

    if request.user_eligible is False:
        flags.append("USER_INELIGIBLE")

    if request.account_eligible is False:
        flags.append("ACCOUNT_INELIGIBLE")

    if request.permission is False:
        flags.append("PERMISSION_DENIED")

    if request.authorized is False:
        flags.append("AUTHORIZATION_DENIED")

    if request.policy_blocked is True:
        flags.append("POLICY_BLOCKED")

    return tuple(flags)


# ============================================================
# RESTRICTION EXTRACTION
# ============================================================

def extract_compliance_restrictions(
    request: ComplianceRequest,
) -> tuple[str, ...]:

    restrictions: list[str] = []

    if request.restricted_action is True:
        restrictions.append("RESTRICTED_ACTION")

    if request.restricted_instrument is True:
        restrictions.append("RESTRICTED_INSTRUMENT")

    if request.trading_restricted is True:
        restrictions.append("TRADING_RESTRICTED")

    if request.market_restricted is True:
        restrictions.append("MARKET_RESTRICTED")

    if request.session_restricted is True:
        restrictions.append("SESSION_RESTRICTED")

    if request.time_restricted is True:
        restrictions.append("TIME_RESTRICTED")

    if request.policy_restricted is True:
        restrictions.append("POLICY_RESTRICTED")

    if request.compliance_review_required is True:
        restrictions.append("COMPLIANCE_REVIEW")

    if request.compliance_required is True:
        restrictions.append("COMPLIANCE_REQUIRED")

    if request.permission is None:
        restrictions.append("PERMISSION_UNCONFIRMED")

    if request.authorized is None:
        restrictions.append("AUTHORIZATION_UNCONFIRMED")

    return tuple(dict.fromkeys(restrictions))


# ============================================================
# COMPLIANCE SCORE
# ============================================================

def calculate_compliance_score(
    data_state: ComplianceDataState,
    consistency: ComplianceConsistency,
    readiness: ComplianceReadiness,
    completeness: float,
    flags: tuple[str, ...],
    restrictions: tuple[str, ...],
) -> float:
    """
    Compliance-condition quality score.

    IMPORTANT:
        This is NOT:
            - winning probability
            - alpha
            - market confidence
            - D13 confidence
            - expectancy
            - trade quality
    """

    score = max(
        0.0,
        min(100.0, float(completeness)),
    )

    if data_state == ComplianceDataState.INVALID:
        return 0.0

    if data_state == ComplianceDataState.MISSING:
        return 0.0

    if consistency == ComplianceConsistency.INCONSISTENT:
        return 0.0

    if readiness == ComplianceReadiness.BLOCKED:
        return 0.0

    # --------------------------------------------------------
    # CONSISTENCY ADJUSTMENT
    # --------------------------------------------------------
    if consistency == ComplianceConsistency.CONDITIONAL:
        score -= 15.0

    elif consistency == ComplianceConsistency.UNKNOWN:
        score -= 20.0

    # --------------------------------------------------------
    # RESTRICTION ADJUSTMENT
    # --------------------------------------------------------
    score -= min(
        30.0,
        len(restrictions) * 5.0,
    )

    # --------------------------------------------------------
    # HARD FLAGS
    # --------------------------------------------------------
    if flags:
        score -= min(
            100.0,
            len(flags) * 25.0,
        )

    return round(
        max(0.0, min(100.0, score)),
        4,
    )


# ============================================================
# COMPLIANCE CONFIDENCE
# ============================================================

def calculate_compliance_confidence(
    data_state: ComplianceDataState,
    consistency: ComplianceConsistency,
    completeness: float,
    flags: tuple[str, ...],
) -> float:

    confidence = float(completeness)

    if data_state == ComplianceDataState.INVALID:
        return 0.0

    if data_state == ComplianceDataState.MISSING:
        return 0.0

    if data_state == ComplianceDataState.PARTIAL:
        confidence -= 15.0

    if consistency == ComplianceConsistency.CONSISTENT:
        confidence += 5.0

    elif consistency == ComplianceConsistency.CONDITIONAL:
        confidence -= 10.0

    elif consistency == ComplianceConsistency.UNKNOWN:
        confidence -= 20.0

    if flags:
        confidence -= min(
            60.0,
            len(flags) * 15.0,
        )

    return round(
        max(0.0, min(100.0, confidence)),
        4,
    )


# ============================================================
# ASSESSMENT BUILDER
# ============================================================

def build_compliance_assessment(
    request: ComplianceRequest,
    requirements: Optional[ComplianceRequirements] = None,
    references: Optional[tuple[ComplianceReference, ...]] = None,
) -> ComplianceAssessment:

    requirements = (
        requirements or ComplianceRequirements()
    )

    data_state = evaluate_compliance_data_state(
        request
    )

    consistency = evaluate_compliance_consistency(
        request
    )

    unmet, warnings = evaluate_compliance_requirements(
        request,
        requirements,
    )

    readiness = evaluate_compliance_readiness(
        data_state,
        consistency,
        unmet,
    )

    completeness = calculate_compliance_completeness(
        request,
        requirements,
    )

    flags = extract_compliance_flags(request)

    restrictions = extract_compliance_restrictions(
        request
    )

    score = calculate_compliance_score(
        data_state=data_state,
        consistency=consistency,
        readiness=readiness,
        completeness=completeness,
        flags=flags,
        restrictions=restrictions,
    )

    confidence = calculate_compliance_confidence(
        data_state=data_state,
        consistency=consistency,
        completeness=completeness,
        flags=flags,
    )

    return ComplianceAssessment(
        data_state=data_state,
        consistency=consistency,
        readiness=readiness,
        completeness=completeness,
        compliance_score=score,
        compliance_confidence=confidence,
        flags=flags,
        restrictions=restrictions,
        unmet_requirements=unmet,
        warnings=warnings,
        references=references or (),
    )
# app/intelligence/cas/compliance_gate.py
# PART 3/5
# Continue directly after Part 2


# ============================================================
# ACTION / CONTRACT / RESULT STATES
# ============================================================

class ComplianceActionState(str, Enum):
    PENDING = "PENDING"
    AUTHORIZED = "AUTHORIZED"
    RESTRICTED = "RESTRICTED"
    REVIEW = "REVIEW"
    BLOCKED = "BLOCKED"


class ComplianceContractState(str, Enum):
    CREATED = "CREATED"
    VALIDATED = "VALIDATED"
    ASSESSED = "ASSESSED"
    DECIDED = "DECIDED"
    AUTHORIZED = "AUTHORIZED"
    RESTRICTED = "RESTRICTED"
    REVIEW = "REVIEW"
    BLOCKED = "BLOCKED"
    REJECTED = "REJECTED"


class ComplianceResultStatus(str, Enum):
    ALLOWED = "ALLOWED"
    ALLOWED_WITH_RESTRICTION = "ALLOWED_WITH_RESTRICTION"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"


# ============================================================
# ACTION CONTRACT
# ============================================================

@dataclass(frozen=True)
class ComplianceAction:
    action: Optional[str]
    decision: ComplianceDecision
    state: ComplianceActionState
    restrictions: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# ============================================================
# RESULT CONTRACT
# ============================================================

@dataclass(frozen=True)
class ComplianceResult:
    status: ComplianceResultStatus
    decision: ComplianceDecision
    compliance_status: ComplianceStatus

    compliance_score: float
    compliance_confidence: float

    flags: tuple[str, ...] = ()
    restrictions: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    request_id: Optional[str] = None

    evaluated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# ============================================================
# COMPLETE COMPLIANCE CONTRACT
# ============================================================

@dataclass(frozen=True)
class ComplianceContract:
    request: ComplianceRequest
    assessment: ComplianceAssessment
    action: ComplianceAction
    result: ComplianceResult

    state: ComplianceContractState
    contract_status: ComplianceContractStatus

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# ============================================================
# RESULT STATUS
# ============================================================

def determine_compliance_result_status(
    decision: ComplianceDecision,
) -> ComplianceResultStatus:

    mapping = {
        ComplianceDecision.ALLOW:
            ComplianceResultStatus.ALLOWED,

        ComplianceDecision.ALLOW_WITH_RESTRICTION:
            ComplianceResultStatus.ALLOWED_WITH_RESTRICTION,

        ComplianceDecision.REVIEW_REQUIRED:
            ComplianceResultStatus.REVIEW_REQUIRED,

        ComplianceDecision.BLOCK:
            ComplianceResultStatus.BLOCKED,
    }

    return mapping.get(
        decision,
        ComplianceResultStatus.REVIEW_REQUIRED,
    )


# ============================================================
# COMPLIANCE STATUS
# ============================================================

def determine_compliance_status(
    assessment: ComplianceAssessment,
) -> ComplianceStatus:

    if assessment.data_state == ComplianceDataState.INVALID:
        return ComplianceStatus.BLOCKED

    if assessment.consistency == ComplianceConsistency.INCONSISTENT:
        return ComplianceStatus.NON_COMPLIANT

    if assessment.readiness == ComplianceReadiness.BLOCKED:
        return ComplianceStatus.BLOCKED

    if assessment.flags:
        return ComplianceStatus.NON_COMPLIANT

    if assessment.readiness == ComplianceReadiness.NOT_READY:
        return ComplianceStatus.REVIEW_REQUIRED

    if (
        assessment.readiness
        == ComplianceReadiness.CONDITIONALLY_READY
    ):
        return ComplianceStatus.CONDITIONAL

    if assessment.restrictions:
        return ComplianceStatus.CONDITIONAL

    if assessment.compliance_score >= 80.0:
        return ComplianceStatus.COMPLIANT

    if assessment.compliance_score >= 50.0:
        return ComplianceStatus.CONDITIONAL

    return ComplianceStatus.REVIEW_REQUIRED


# ============================================================
# DECISION
# ============================================================

def determine_compliance_decision(
    assessment: ComplianceAssessment,
) -> ComplianceDecision:

    # --------------------------------------------------------
    # HARD BLOCK CONDITIONS
    # --------------------------------------------------------
    if assessment.data_state == ComplianceDataState.INVALID:
        return ComplianceDecision.BLOCK

    if (
        assessment.consistency
        == ComplianceConsistency.INCONSISTENT
    ):
        return ComplianceDecision.BLOCK

    if assessment.readiness == ComplianceReadiness.BLOCKED:
        return ComplianceDecision.BLOCK

    hard_flags = {
        "COMPLIANCE_BREACH",
        "COMPLIANCE_HOLD",
        "PROHIBITED_ACTION",
        "PROHIBITED_INSTRUMENT",
        "USER_INELIGIBLE",
        "ACCOUNT_INELIGIBLE",
        "PERMISSION_DENIED",
        "AUTHORIZATION_DENIED",
        "POLICY_BLOCKED",
    }

    if any(
        flag in hard_flags
        for flag in assessment.flags
    ):
        return ComplianceDecision.BLOCK

    # --------------------------------------------------------
    # REVIEW CONDITIONS
    # --------------------------------------------------------
    if assessment.readiness == ComplianceReadiness.NOT_READY:
        return ComplianceDecision.REVIEW_REQUIRED

    if assessment.unmet_requirements:
        return ComplianceDecision.REVIEW_REQUIRED

    if assessment.compliance_score < 50.0:
        return ComplianceDecision.REVIEW_REQUIRED

    # --------------------------------------------------------
    # CONDITIONAL / RESTRICTED
    # --------------------------------------------------------
    if (
        assessment.readiness
        == ComplianceReadiness.CONDITIONALLY_READY
    ):
        return ComplianceDecision.ALLOW_WITH_RESTRICTION

    if assessment.restrictions:
        return ComplianceDecision.ALLOW_WITH_RESTRICTION

    if assessment.compliance_score < 80.0:
        return ComplianceDecision.ALLOW_WITH_RESTRICTION

    # --------------------------------------------------------
    # CLEAN ALLOW
    # --------------------------------------------------------
    return ComplianceDecision.ALLOW


# ============================================================
# ACTION STATE
# ============================================================

def determine_compliance_action_state(
    decision: ComplianceDecision,
) -> ComplianceActionState:

    mapping = {
        ComplianceDecision.ALLOW:
            ComplianceActionState.AUTHORIZED,

        ComplianceDecision.ALLOW_WITH_RESTRICTION:
            ComplianceActionState.RESTRICTED,

        ComplianceDecision.REVIEW_REQUIRED:
            ComplianceActionState.REVIEW,

        ComplianceDecision.BLOCK:
            ComplianceActionState.BLOCKED,
    }

    return mapping.get(
        decision,
        ComplianceActionState.REVIEW,
    )


# ============================================================
# ACTION BUILDER
# ============================================================

def build_compliance_action(
    request: ComplianceRequest,
    assessment: ComplianceAssessment,
    decision: ComplianceDecision,
) -> ComplianceAction:

    state = determine_compliance_action_state(
        decision
    )

    reasons: list[str] = []

    if assessment.flags:
        reasons.extend(assessment.flags)

    if assessment.restrictions:
        reasons.extend(assessment.restrictions)

    if assessment.unmet_requirements:
        reasons.extend(assessment.unmet_requirements)

    if not reasons:
        if decision == ComplianceDecision.ALLOW:
            reasons.append("COMPLIANCE_CONDITIONS_ACCEPTABLE")

        elif (
            decision
            == ComplianceDecision.ALLOW_WITH_RESTRICTION
        ):
            reasons.append("COMPLIANCE_RESTRICTIONS_PRESENT")

        elif decision == ComplianceDecision.REVIEW_REQUIRED:
            reasons.append("COMPLIANCE_REVIEW_REQUIRED")

        else:
            reasons.append("COMPLIANCE_BLOCK_CONDITION")

    return ComplianceAction(
        action=request.action,
        decision=decision,
        state=state,
        restrictions=assessment.restrictions,
        reasons=tuple(dict.fromkeys(reasons)),
    )


# ============================================================
# RESULT BUILDER
# ============================================================

def build_compliance_result(
    request: ComplianceRequest,
    assessment: ComplianceAssessment,
    decision: ComplianceDecision,
) -> ComplianceResult:

    status = determine_compliance_result_status(
        decision
    )

    compliance_status = determine_compliance_status(
        assessment
    )

    reasons: list[str] = []

    if assessment.flags:
        reasons.extend(assessment.flags)

    if assessment.restrictions:
        reasons.extend(assessment.restrictions)

    if assessment.unmet_requirements:
        reasons.extend(assessment.unmet_requirements)

    if not reasons:
        reasons.append(
            compliance_status.value
        )

    return ComplianceResult(
        status=status,
        decision=decision,
        compliance_status=compliance_status,
        compliance_score=assessment.compliance_score,
        compliance_confidence=assessment.compliance_confidence,
        flags=assessment.flags,
        restrictions=assessment.restrictions,
        reasons=tuple(dict.fromkeys(reasons)),
        warnings=assessment.warnings,
        request_id=request.request_id,
    )


# ============================================================
# CONTRACT STATE
# ============================================================

def determine_compliance_contract_state(
    result: ComplianceResult,
) -> ComplianceContractState:

    if result.status == ComplianceResultStatus.BLOCKED:
        return ComplianceContractState.BLOCKED

    if (
        result.status
        == ComplianceResultStatus.REVIEW_REQUIRED
    ):
        return ComplianceContractState.REVIEW

    if (
        result.status
        == ComplianceResultStatus.ALLOWED_WITH_RESTRICTION
    ):
        return ComplianceContractState.RESTRICTED

    if result.status == ComplianceResultStatus.ALLOWED:
        return ComplianceContractState.AUTHORIZED

    return ComplianceContractState.REJECTED


# ============================================================
# CONTRACT STATUS
# ============================================================

def determine_compliance_contract_status(
    result: ComplianceResult,
) -> ComplianceContractStatus:

    if result.status == ComplianceResultStatus.BLOCKED:
        return ComplianceContractStatus.BLOCKED

    if (
        result.status
        == ComplianceResultStatus.REVIEW_REQUIRED
    ):
        return ComplianceContractStatus.REVIEW

    if (
        result.status
        == ComplianceResultStatus.ALLOWED_WITH_RESTRICTION
    ):
        return ComplianceContractStatus.RESTRICTED

    if result.status == ComplianceResultStatus.ALLOWED:
        return ComplianceContractStatus.READY

    return ComplianceContractStatus.INVALID


# ============================================================
# CONTRACT BUILDER
# ============================================================

def build_compliance_contract(
    request: ComplianceRequest,
    assessment: ComplianceAssessment,
    action: ComplianceAction,
    result: ComplianceResult,
) -> ComplianceContract:

    return ComplianceContract(
        request=request,
        assessment=assessment,
        action=action,
        result=result,
        state=determine_compliance_contract_state(
            result
        ),
        contract_status=determine_compliance_contract_status(
            result
        ),
    )


# ============================================================
# ENGINE
# ============================================================

class ComplianceGateEngine:
    """
    CAS Compliance Gate engine.

    Authority boundary:
        Compliance Gate evaluates compliance/control
        conditions only.

    It does NOT:
        - generate market decisions
        - generate alpha
        - modify D13
        - override D13
        - replace Risk Authority
        - override Risk Authority
        - override CAS
        - place orders
        - mutate positions
    """

    _instance: Optional["ComplianceGateEngine"] = None

    def __new__(
        cls,
    ) -> "ComplianceGateEngine":

        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    @property
    def engine_name(self) -> str:
        return COMPLIANCE_GATE_ENGINE

    @property
    def version(self) -> str:
        return COMPLIANCE_GATE_VERSION

    def evaluate(
        self,
        request: ComplianceRequest,
        requirements: Optional[ComplianceRequirements] = None,
        references: Optional[
            tuple[ComplianceReference, ...]
        ] = None,
    ) -> ComplianceContract:

        validation = validate_compliance_request(
            request
        )

        if not validation.valid:
            assessment = ComplianceAssessment(
                data_state=ComplianceDataState.INVALID,
                consistency=ComplianceConsistency.INCONSISTENT,
                readiness=ComplianceReadiness.BLOCKED,
                completeness=0.0,
                compliance_score=0.0,
                compliance_confidence=0.0,
                flags=("REQUEST_INVALID",),
                restrictions=(),
                unmet_requirements=validation.missing_fields,
                warnings=validation.warnings,
                references=references or (),
            )
        else:
            assessment = build_compliance_assessment(
                request=request,
                requirements=requirements,
                references=references,
            )

        decision = determine_compliance_decision(
            assessment
        )

        action = build_compliance_action(
            request=request,
            assessment=assessment,
            decision=decision,
        )

        result = build_compliance_result(
            request=request,
            assessment=assessment,
            decision=decision,
        )

        return build_compliance_contract(
            request=request,
            assessment=assessment,
            action=action,
            result=result,
        )

    def check(
        self,
        request: ComplianceRequest,
        requirements: Optional[ComplianceRequirements] = None,
    ) -> ComplianceContract:

        return self.evaluate(
            request=request,
            requirements=requirements,
        )

    def review(
        self,
        request: ComplianceRequest,
        requirements: Optional[ComplianceRequirements] = None,
    ) -> ComplianceContract:

        contract = self.evaluate(
            request=request,
            requirements=requirements,
        )

        result = ComplianceResult(
            status=ComplianceResultStatus.REVIEW_REQUIRED,
            decision=ComplianceDecision.REVIEW_REQUIRED,
            compliance_status=ComplianceStatus.REVIEW_REQUIRED,
            compliance_score=contract.assessment.compliance_score,
            compliance_confidence=contract.assessment.compliance_confidence,
            flags=contract.assessment.flags,
            restrictions=contract.assessment.restrictions,
            reasons=(
                *contract.result.reasons,
                "EXPLICIT_COMPLIANCE_REVIEW",
            ),
            warnings=contract.assessment.warnings,
            request_id=request.request_id,
        )

        action = build_compliance_action(
            request=request,
            assessment=contract.assessment,
            decision=ComplianceDecision.REVIEW_REQUIRED,
        )

        return build_compliance_contract(
            request=request,
            assessment=contract.assessment,
            action=action,
            result=result,
        )


# ============================================================
# ENGINE ACCESS
# ============================================================

_COMPLIANCE_GATE_ENGINE_INSTANCE = ComplianceGateEngine()


def get_compliance_gate_engine() -> ComplianceGateEngine:
    return _COMPLIANCE_GATE_ENGINE_INSTANCE


# ============================================================
# PUBLIC API
# ============================================================

def evaluate_compliance(
    request: ComplianceRequest,
    requirements: Optional[ComplianceRequirements] = None,
    references: Optional[
        tuple[ComplianceReference, ...]
    ] = None,
) -> ComplianceContract:

    return get_compliance_gate_engine().evaluate(
        request=request,
        requirements=requirements,
        references=references,
    )


def check_compliance(
    request: ComplianceRequest,
    requirements: Optional[ComplianceRequirements] = None,
) -> ComplianceContract:

    return get_compliance_gate_engine().check(
        request=request,
        requirements=requirements,
    )


def review_compliance(
    request: ComplianceRequest,
    requirements: Optional[ComplianceRequirements] = None,
) -> ComplianceContract:

    return get_compliance_gate_engine().review(
        request=request,
        requirements=requirements,
    )
# app/intelligence/cas/compliance_gate.py
# PART 4/5
# Continue directly after Part 3


# ============================================================
# ACTION VALIDATION
# ============================================================

def validate_compliance_action(
    action: ComplianceAction,
) -> bool:

    if not isinstance(action, ComplianceAction):
        return False

    if not isinstance(
        action.decision,
        ComplianceDecision,
    ):
        return False

    if not isinstance(
        action.state,
        ComplianceActionState,
    ):
        return False

    if not isinstance(action.restrictions, tuple):
        return False

    if not isinstance(action.reasons, tuple):
        return False

    return True


# ============================================================
# RESULT VALIDATION
# ============================================================

def validate_compliance_result(
    result: ComplianceResult,
) -> bool:

    if not isinstance(result, ComplianceResult):
        return False

    if not isinstance(
        result.status,
        ComplianceResultStatus,
    ):
        return False

    if not isinstance(
        result.decision,
        ComplianceDecision,
    ):
        return False

    if not isinstance(
        result.compliance_status,
        ComplianceStatus,
    ):
        return False

    if not (
        0.0
        <= float(result.compliance_score)
        <= 100.0
    ):
        return False

    if not (
        0.0
        <= float(result.compliance_confidence)
        <= 100.0
    ):
        return False

    return True


# ============================================================
# CONTRACT VALIDATION
# ============================================================

def validate_compliance_contract(
    contract: ComplianceContract,
) -> bool:

    if not isinstance(
        contract,
        ComplianceContract,
    ):
        return False

    request_validation = (
        validate_compliance_request(
            contract.request
        )
    )

    if not request_validation.valid:
        return False

    if not isinstance(
        contract.assessment,
        ComplianceAssessment,
    ):
        return False

    if not validate_compliance_action(
        contract.action
    ):
        return False

    if not validate_compliance_result(
        contract.result
    ):
        return False

    if not isinstance(
        contract.state,
        ComplianceContractState,
    ):
        return False

    if not isinstance(
        contract.contract_status,
        ComplianceContractStatus,
    ):
        return False

    return True


# ============================================================
# READINESS HELPERS
# ============================================================

def compliance_ready(
    assessment: ComplianceAssessment,
) -> bool:

    return (
        assessment.readiness
        == ComplianceReadiness.READY
    )


def compliance_can_advance(
    contract: ComplianceContract,
) -> bool:

    if not validate_compliance_contract(contract):
        return False

    return contract.result.decision in {
        ComplianceDecision.ALLOW,
        ComplianceDecision.ALLOW_WITH_RESTRICTION,
    }


def compliance_requires_review(
    contract: ComplianceContract,
) -> bool:

    if not isinstance(
        contract,
        ComplianceContract,
    ):
        return False

    return (
        contract.result.decision
        == ComplianceDecision.REVIEW_REQUIRED
    )


def compliance_is_blocked(
    contract: ComplianceContract,
) -> bool:

    if not isinstance(
        contract,
        ComplianceContract,
    ):
        return True

    return (
        contract.result.decision
        == ComplianceDecision.BLOCK
    )


def compliance_is_restricted(
    contract: ComplianceContract,
) -> bool:

    if not isinstance(
        contract,
        ComplianceContract,
    ):
        return False

    return (
        contract.result.decision
        == ComplianceDecision.ALLOW_WITH_RESTRICTION
    )


def compliance_is_safe_for_next_gate(
    contract: ComplianceContract,
) -> bool:

    if not validate_compliance_contract(contract):
        return False

    return contract.result.decision in {
        ComplianceDecision.ALLOW,
        ComplianceDecision.ALLOW_WITH_RESTRICTION,
    }


# ============================================================
# ACCESSORS
# ============================================================

def get_compliance_status(
    contract: ComplianceContract,
) -> ComplianceStatus:

    return contract.result.compliance_status


def get_compliance_decision(
    contract: ComplianceContract,
) -> ComplianceDecision:

    return contract.result.decision


def get_compliance_action_state(
    contract: ComplianceContract,
) -> ComplianceActionState:

    return contract.action.state


# ============================================================
# AUTHORITY BOUNDARY
# ============================================================

def compliance_generates_market_decision() -> bool:
    return False


def compliance_generates_alpha() -> bool:
    return False


def compliance_modifies_d13() -> bool:
    return False


def compliance_overrides_d13() -> bool:
    return False


def compliance_replaces_risk_authority() -> bool:
    return False


def compliance_overrides_risk_authority() -> bool:
    return False


def compliance_overrides_cas() -> bool:
    return False


def compliance_authorizes_execution() -> bool:
    return False


def compliance_places_orders() -> bool:
    return False


def compliance_changes_position() -> bool:
    return False


def compliance_has_execution_authority() -> bool:
    return False


def compliance_has_market_decision_authority() -> bool:
    return False


def compliance_is_alpha_engine() -> bool:
    return False


def compliance_authority_integrity_ok() -> bool:
    """
    Compliance Gate must remain a CAS control gate.

    It cannot become:
        - D13
        - Risk Authority
        - Alpha Engine
        - Execution Engine
        - Position Controller
        - CAS replacement
    """

    checks = (
        not compliance_generates_market_decision(),
        not compliance_generates_alpha(),
        not compliance_modifies_d13(),
        not compliance_overrides_d13(),
        not compliance_replaces_risk_authority(),
        not compliance_overrides_risk_authority(),
        not compliance_overrides_cas(),
        not compliance_authorizes_execution(),
        not compliance_places_orders(),
        not compliance_changes_position(),
        not compliance_has_execution_authority(),
        not compliance_has_market_decision_authority(),
        not compliance_is_alpha_engine(),
    )

    return all(checks)


def compliance_has_authority_conflict() -> bool:
    return not compliance_authority_integrity_ok()


# ============================================================
# AUDIT RECORD
# ============================================================

@dataclass(frozen=True)
class ComplianceAuditRecord:
    engine: str
    version: str

    request_id: Optional[str]

    compliance_status: ComplianceStatus
    decision: ComplianceDecision
    result_status: ComplianceResultStatus

    compliance_score: float
    compliance_confidence: float

    flags: tuple[str, ...]
    restrictions: tuple[str, ...]

    authority_integrity: bool

    audited_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


def build_compliance_audit(
    contract: ComplianceContract,
) -> ComplianceAuditRecord:

    return ComplianceAuditRecord(
        engine=COMPLIANCE_GATE_ENGINE,
        version=COMPLIANCE_GATE_VERSION,
        request_id=contract.request.request_id,
        compliance_status=(
            contract.result.compliance_status
        ),
        decision=contract.result.decision,
        result_status=contract.result.status,
        compliance_score=(
            contract.result.compliance_score
        ),
        compliance_confidence=(
            contract.result.compliance_confidence
        ),
        flags=contract.result.flags,
        restrictions=contract.result.restrictions,
        authority_integrity=(
            compliance_authority_integrity_ok()
        ),
    )


# ============================================================
# ENGINE HEALTH
# ============================================================

@dataclass(frozen=True)
class ComplianceEngineHealth:
    engine: str
    version: str

    operational: bool
    contract_validation_ok: bool
    authority_integrity_ok: bool

    checked_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


def get_compliance_engine_health() -> ComplianceEngineHealth:

    authority_ok = (
        compliance_authority_integrity_ok()
    )

    # A minimal synthetic request validates the structural
    # contract path without inventing external legal data.
    test_request = build_compliance_request(
        market="HEALTH_CHECK",
        instrument="HEALTH_CHECK",
        action="CHECK",
    )

    test_contract = (
        get_compliance_gate_engine().evaluate(
            test_request
        )
    )

    contract_ok = validate_compliance_contract(
        test_contract
    )

    operational = (
        authority_ok
        and contract_ok
    )

    return ComplianceEngineHealth(
        engine=COMPLIANCE_GATE_ENGINE,
        version=COMPLIANCE_GATE_VERSION,
        operational=operational,
        contract_validation_ok=contract_ok,
        authority_integrity_ok=authority_ok,
    )


# ============================================================
# ENGINE INFORMATION
# ============================================================

def get_compliance_engine_info() -> dict[str, Any]:

    return {
        "engine": COMPLIANCE_GATE_ENGINE,
        "version": COMPLIANCE_GATE_VERSION,
        "role": "CAS_COMPLIANCE_GATE",
        "authority": "COMPLIANCE_CONTROL_ONLY",
        "market_decision_authority": False,
        "alpha_authority": False,
        "d13_authority": False,
        "risk_authority": False,
        "execution_authority": False,
        "position_mutation_authority": False,
        "cas_override_authority": False,
    }


# ============================================================
# INTEGRITY
# ============================================================

def compliance_integrity_ok(
    contract: Optional[ComplianceContract] = None,
) -> bool:

    if not compliance_authority_integrity_ok():
        return False

    if contract is not None:
        if not validate_compliance_contract(contract):
            return False

        if (
            contract.result.decision
            == ComplianceDecision.BLOCK
            and contract.action.state
            != ComplianceActionState.BLOCKED
        ):
            return False

        if (
            contract.result.decision
            == ComplianceDecision.REVIEW_REQUIRED
            and contract.action.state
            != ComplianceActionState.REVIEW
        ):
            return False

        if (
            contract.result.decision
            == ComplianceDecision.ALLOW_WITH_RESTRICTION
            and contract.action.state
            != ComplianceActionState.RESTRICTED
        ):
            return False

        if (
            contract.result.decision
            == ComplianceDecision.ALLOW
            and contract.action.state
            != ComplianceActionState.AUTHORIZED
        ):
            return False

    return True
# app/intelligence/cas/compliance_gate.py
# PART 5/5
# Continue directly after Part 4


# ============================================================
# LIFECYCLE
# ============================================================

class ComplianceLifecycleState(str, Enum):
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
    RETAINED = "RETAINED"
    REJECTED = "REJECTED"


def determine_compliance_lifecycle(
    contract: ComplianceContract,
) -> ComplianceLifecycleState:

    if not validate_compliance_contract(contract):
        return ComplianceLifecycleState.REJECTED

    if contract.result.decision == ComplianceDecision.BLOCK:
        return ComplianceLifecycleState.REJECTED

    if (
        contract.result.decision
        == ComplianceDecision.REVIEW_REQUIRED
    ):
        return ComplianceLifecycleState.FROZEN

    return ComplianceLifecycleState.ACTIVE


def freeze_compliance(
    contract: ComplianceContract,
) -> ComplianceLifecycleState:

    if not validate_compliance_contract(contract):
        return ComplianceLifecycleState.REJECTED

    return ComplianceLifecycleState.FROZEN


def retain_compliance(
    contract: ComplianceContract,
) -> ComplianceLifecycleState:

    if not validate_compliance_contract(contract):
        return ComplianceLifecycleState.REJECTED

    return ComplianceLifecycleState.RETAINED


def reject_compliance(
    contract: ComplianceContract,
) -> ComplianceLifecycleState:

    return ComplianceLifecycleState.REJECTED


# ============================================================
# SERIALIZATION HELPERS
# ============================================================

def compliance_request_to_dict(
    request: ComplianceRequest,
) -> dict[str, Any]:

    return {
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

        "broker": request.broker,
        "venue": request.venue,
        "jurisdiction": request.jurisdiction,

        "user_eligible": request.user_eligible,
        "account_eligible": request.account_eligible,

        "permission": request.permission,
        "authorized": request.authorized,

        "restricted_action": request.restricted_action,
        "prohibited_action": request.prohibited_action,

        "restricted_instrument": (
            request.restricted_instrument
        ),
        "prohibited_instrument": (
            request.prohibited_instrument
        ),

        "trading_restricted": (
            request.trading_restricted
        ),
        "market_restricted": (
            request.market_restricted
        ),

        "session_restricted": (
            request.session_restricted
        ),
        "time_restricted": (
            request.time_restricted
        ),

        "compliance_required": (
            request.compliance_required
        ),
        "compliance_review_required": (
            request.compliance_review_required
        ),
        "compliance_hold": (
            request.compliance_hold
        ),
        "compliance_breach": (
            request.compliance_breach
        ),

        "policy_allowed": request.policy_allowed,
        "policy_restricted": request.policy_restricted,
        "policy_blocked": request.policy_blocked,

        "metadata": dict(request.metadata),
        "request_id": request.request_id,

        "timestamp": (
            request.timestamp.isoformat()
            if request.timestamp
            else None
        ),
    }


def compliance_assessment_to_dict(
    assessment: ComplianceAssessment,
) -> dict[str, Any]:

    return {
        "data_state": assessment.data_state.value,
        "consistency": assessment.consistency.value,
        "readiness": assessment.readiness.value,

        "completeness": assessment.completeness,
        "compliance_score": (
            assessment.compliance_score
        ),
        "compliance_confidence": (
            assessment.compliance_confidence
        ),

        "flags": list(assessment.flags),
        "restrictions": list(assessment.restrictions),
        "unmet_requirements": list(
            assessment.unmet_requirements
        ),
        "warnings": list(assessment.warnings),

        "references": [
            {
                "source": reference.source,
                "policy_id": reference.policy_id,
                "rule_id": reference.rule_id,
                "jurisdiction": reference.jurisdiction,
                "description": reference.description,
                "metadata": dict(reference.metadata),
            }
            for reference in assessment.references
        ],

        "evaluated_at": (
            assessment.evaluated_at.isoformat()
        ),
    }


def compliance_action_to_dict(
    action: ComplianceAction,
) -> dict[str, Any]:

    return {
        "action": action.action,
        "decision": action.decision.value,
        "state": action.state.value,
        "restrictions": list(action.restrictions),
        "reasons": list(action.reasons),
        "created_at": action.created_at.isoformat(),
    }


def compliance_result_to_dict(
    result: ComplianceResult,
) -> dict[str, Any]:

    return {
        "status": result.status.value,
        "decision": result.decision.value,
        "compliance_status": (
            result.compliance_status.value
        ),

        "compliance_score": (
            result.compliance_score
        ),
        "compliance_confidence": (
            result.compliance_confidence
        ),

        "flags": list(result.flags),
        "restrictions": list(result.restrictions),
        "reasons": list(result.reasons),
        "warnings": list(result.warnings),

        "request_id": result.request_id,
        "evaluated_at": result.evaluated_at.isoformat(),
    }


def compliance_contract_to_dict(
    contract: ComplianceContract,
) -> dict[str, Any]:

    return {
        "request": compliance_request_to_dict(
            contract.request
        ),
        "assessment": compliance_assessment_to_dict(
            contract.assessment
        ),
        "action": compliance_action_to_dict(
            contract.action
        ),
        "result": compliance_result_to_dict(
            contract.result
        ),

        "state": contract.state.value,
        "contract_status": (
            contract.contract_status.value
        ),

        "created_at": contract.created_at.isoformat(),
    }


# ============================================================
# SUMMARY
# ============================================================

def summarize_compliance(
    contract: ComplianceContract,
) -> dict[str, Any]:

    if not validate_compliance_contract(contract):
        return {
            "valid": False,
            "status": "INVALID_CONTRACT",
            "decision": ComplianceDecision.BLOCK.value,
            "safe_for_next_gate": False,
        }

    return {
        "valid": True,

        "engine": COMPLIANCE_GATE_ENGINE,
        "version": COMPLIANCE_GATE_VERSION,

        "request_id": contract.request.request_id,

        "market": contract.request.market,
        "instrument": contract.request.instrument,
        "action": contract.request.action,

        "compliance_status": (
            contract.result.compliance_status.value
        ),
        "decision": contract.result.decision.value,
        "result_status": (
            contract.result.status.value
        ),

        "compliance_score": (
            contract.result.compliance_score
        ),
        "compliance_confidence": (
            contract.result.compliance_confidence
        ),

        "flags": list(contract.result.flags),
        "restrictions": list(
            contract.result.restrictions
        ),

        "safe_for_next_gate": (
            compliance_is_safe_for_next_gate(
                contract
            )
        ),

        "requires_review": (
            compliance_requires_review(
                contract
            )
        ),

        "blocked": (
            compliance_is_blocked(
                contract
            )
        ),

        "restricted": (
            compliance_is_restricted(
                contract
            )
        ),

        "authority_integrity": (
            compliance_authority_integrity_ok()
        ),
    }


# ============================================================
# AUTHORITY STATEMENT
# ============================================================

def get_compliance_authority_statement() -> str:

    return (
        "Compliance Gate is a CAS compliance/control gate. "
        "It evaluates supplied eligibility, permission, "
        "authorization, policy, restriction and compliance "
        "state. It does not generate alpha or market "
        "decisions, does not modify or override D13, does "
        "not replace or override Risk Authority, does not "
        "override CAS, and does not place orders or mutate "
        "positions. Final authorization remains with CAS."
    )


# ============================================================
# OPERATIONAL CHECK
# ============================================================

def compliance_engine_operational() -> bool:

    health = get_compliance_engine_health()

    return bool(
        health.operational
        and health.contract_validation_ok
        and health.authority_integrity_ok
    )


# ============================================================
# FINAL VALIDATION
# ============================================================

def validate_compliance(
    contract: ComplianceContract,
) -> bool:

    if not validate_compliance_contract(contract):
        return False

    if not compliance_integrity_ok(contract):
        return False

    expected_status = (
        determine_compliance_result_status(
            contract.result.decision
        )
    )

    if contract.result.status != expected_status:
        return False

    expected_action_state = (
        determine_compliance_action_state(
            contract.result.decision
        )
    )

    if contract.action.state != expected_action_state:
        return False

    expected_contract_state = (
        determine_compliance_contract_state(
            contract.result
        )
    )

    if contract.state != expected_contract_state:
        return False

    expected_contract_status = (
        determine_compliance_contract_status(
            contract.result
        )
    )

    if (
        contract.contract_status
        != expected_contract_status
    ):
        return False

    return True


# ============================================================
# SNAPSHOT
# ============================================================

def compliance_snapshot(
    contract: ComplianceContract,
) -> dict[str, Any]:

    valid = validate_compliance(contract)

    lifecycle = (
        determine_compliance_lifecycle(contract)
        if valid
        else ComplianceLifecycleState.REJECTED
    )

    return {
        "engine": COMPLIANCE_GATE_ENGINE,
        "version": COMPLIANCE_GATE_VERSION,

        "valid": valid,

        "request_id": (
            contract.request.request_id
            if isinstance(
                contract,
                ComplianceContract,
            )
            else None
        ),

        "lifecycle": lifecycle.value,

        "decision": (
            contract.result.decision.value
            if isinstance(
                contract,
                ComplianceContract,
            )
            else ComplianceDecision.BLOCK.value
        ),

        "status": (
            contract.result.status.value
            if isinstance(
                contract,
                ComplianceContract,
            )
            else ComplianceResultStatus.BLOCKED.value
        ),

        "compliance_status": (
            contract.result.compliance_status.value
            if isinstance(
                contract,
                ComplianceContract,
            )
            else ComplianceStatus.BLOCKED.value
        ),

        "compliance_score": (
            contract.result.compliance_score
            if isinstance(
                contract,
                ComplianceContract,
            )
            else 0.0
        ),

        "compliance_confidence": (
            contract.result.compliance_confidence
            if isinstance(
                contract,
                ComplianceContract,
            )
            else 0.0
        ),

        "flags": (
            list(contract.result.flags)
            if isinstance(
                contract,
                ComplianceContract,
            )
            else []
        ),

        "restrictions": (
            list(contract.result.restrictions)
            if isinstance(
                contract,
                ComplianceContract,
            )
            else []
        ),

        "safe_for_next_gate": (
            compliance_is_safe_for_next_gate(
                contract
            )
            if isinstance(
                contract,
                ComplianceContract,
            )
            else False
        ),

        "authority_integrity": (
            compliance_authority_integrity_ok()
        ),

        "operational": (
            compliance_engine_operational()
        ),
    }


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [
    # Constants
    "COMPLIANCE_GATE_ENGINE",
    "COMPLIANCE_GATE_VERSION",

    # Enums
    "ComplianceStatus",
    "ComplianceDecision",
    "ComplianceMode",
    "CompliancePriority",
    "ComplianceContractStatus",

    "ComplianceDataState",
    "ComplianceConsistency",
    "ComplianceReadiness",

    "ComplianceActionState",
    "ComplianceContractState",
    "ComplianceResultStatus",

    "ComplianceLifecycleState",

    # Request / reference / validation
    "ComplianceRequest",
    "ComplianceReference",
    "ComplianceContractValidation",

    # Requirements / assessment
    "ComplianceRequirements",
    "ComplianceAssessment",

    # Action / result / contract
    "ComplianceAction",
    "ComplianceResult",
    "ComplianceContract",

    # Request builders / validation
    "build_compliance_request",
    "validate_compliance_numeric_inputs",
    "validate_compliance_request",

    # Assessment
    "evaluate_compliance_data_state",
    "evaluate_compliance_consistency",
    "calculate_compliance_completeness",
    "evaluate_compliance_requirements",
    "evaluate_compliance_readiness",

    "extract_compliance_flags",
    "extract_compliance_restrictions",

    "calculate_compliance_score",
    "calculate_compliance_confidence",
    "build_compliance_assessment",

    # Decision / result / contract
    "determine_compliance_result_status",
    "determine_compliance_status",
    "determine_compliance_decision",
    "determine_compliance_action_state",

    "build_compliance_action",
    "build_compliance_result",

    "determine_compliance_contract_state",
    "determine_compliance_contract_status",
    "build_compliance_contract",

    # Engine
    "ComplianceGateEngine",
    "get_compliance_gate_engine",

    "evaluate_compliance",
    "check_compliance",
    "review_compliance",

    # Validation / readiness
    "validate_compliance_action",
    "validate_compliance_result",
    "validate_compliance_contract",

    "compliance_ready",
    "compliance_can_advance",
    "compliance_requires_review",
    "compliance_is_blocked",
    "compliance_is_restricted",
    "compliance_is_safe_for_next_gate",

    # Accessors
    "get_compliance_status",
    "get_compliance_decision",
    "get_compliance_action_state",

    # Authority
    "compliance_generates_market_decision",
    "compliance_generates_alpha",
    "compliance_modifies_d13",
    "compliance_overrides_d13",
    "compliance_replaces_risk_authority",
    "compliance_overrides_risk_authority",
    "compliance_overrides_cas",
    "compliance_authorizes_execution",
    "compliance_places_orders",
    "compliance_changes_position",
    "compliance_has_execution_authority",
    "compliance_has_market_decision_authority",
    "compliance_is_alpha_engine",
    "compliance_authority_integrity_ok",
    "compliance_has_authority_conflict",

    # Audit / health
    "ComplianceAuditRecord",
    "build_compliance_audit",
    "ComplianceEngineHealth",
    "get_compliance_engine_health",
    "get_compliance_engine_info",
    "compliance_integrity_ok",

    # Lifecycle
    "determine_compliance_lifecycle",
    "freeze_compliance",
    "retain_compliance",
    "reject_compliance",

    # Serialization
    "compliance_request_to_dict",
    "compliance_assessment_to_dict",
    "compliance_action_to_dict",
    "compliance_result_to_dict",
    "compliance_contract_to_dict",

    # Summary / final utilities
    "summarize_compliance",
    "get_compliance_authority_statement",
    "compliance_engine_operational",
    "validate_compliance",
    "compliance_snapshot",
]