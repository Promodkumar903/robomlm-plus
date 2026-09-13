# ============================================================
# ROBOMLM TERMINAL
# market_context.py — PART 1
# MARKET CONTEXT FOUNDATION / CONTRACTS
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Optional, Tuple


TERMINAL_MARKET_CONTEXT_ENGINE = "ROBOMLM_TERMINAL_MARKET_CONTEXT"
TERMINAL_MARKET_CONTEXT_VERSION = "1.0"


# ============================================================
# ENUMS
# ============================================================

class TerminalMarketContextStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    READY = "READY"
    PARTIAL = "PARTIAL"
    STALE = "STALE"
    INVALID = "INVALID"
    ERROR = "ERROR"


class TerminalMarketContextMode(str, Enum):
    PAPER = "PAPER"
    DEMO = "DEMO"
    LIVE = "LIVE"
    UNKNOWN = "UNKNOWN"


class TerminalMarketContextPriority(str, Enum):
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TerminalMarketContextContractStatus(str, Enum):
    CREATED = "CREATED"
    VALID = "VALID"
    INVALID = "INVALID"
    READY = "READY"


# ============================================================
# NORMALIZATION HELPERS
# ============================================================

def _tmc_text(value: Any, default: str = "") -> str:
    if value is None:
        return default

    try:
        text = str(value).strip()
    except Exception:
        return default

    return text if text else default


def _tmc_enum(
    enum_type: type[Enum],
    value: Any,
    default: Enum,
) -> Enum:
    if isinstance(value, enum_type):
        return value

    if value is None:
        return default

    raw = getattr(value, "value", value)

    try:
        return enum_type(str(raw).strip().upper())
    except (ValueError, TypeError):
        return default


def _tmc_number(
    value: Any,
    default: Optional[float] = None,
) -> Optional[float]:
    if value is None:
        return default

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _tmc_timestamp(value: Any = None) -> datetime:
    if isinstance(value, datetime):
        return value

    return datetime.now(timezone.utc)


# ============================================================
# MARKET CONTEXT REQUEST
# ============================================================

@dataclass(frozen=True)
class TerminalMarketContextRequest:
    market: str = ""
    instrument: str = ""
    symbol: str = ""
    contract: Optional[str] = None

    timeframe: Optional[str] = None
    session: Optional[str] = None
    market_phase: Optional[str] = None

    mode: TerminalMarketContextMode = TerminalMarketContextMode.UNKNOWN
    priority: TerminalMarketContextPriority = (
        TerminalMarketContextPriority.NORMAL
    )

    requested_fields: Tuple[str, ...] = ()

    metadata: Mapping[str, Any] = field(default_factory=dict)

    request_id: Optional[str] = None
    timestamp: datetime = field(
        default_factory=_tmc_timestamp
    )


# ============================================================
# MARKET CONTEXT REFERENCE
# ============================================================

@dataclass(frozen=True)
class TerminalMarketContextReference:
    market: str
    instrument: str
    symbol: str

    contract: Optional[str] = None
    timeframe: Optional[str] = None
    session: Optional[str] = None
    market_phase: Optional[str] = None

    status: TerminalMarketContextStatus = (
        TerminalMarketContextStatus.UNKNOWN
    )

    mode: TerminalMarketContextMode = (
        TerminalMarketContextMode.UNKNOWN
    )

    source: str = ""
    version: str = TERMINAL_MARKET_CONTEXT_VERSION

    updated_at: datetime = field(
        default_factory=_tmc_timestamp
    )


# ============================================================
# CONTRACT VALIDATION
# ============================================================

@dataclass(frozen=True)
class TerminalMarketContextContractValidation:
    valid: bool
    errors: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()

    checked_at: datetime = field(
        default_factory=_tmc_timestamp
    )


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_terminal_market_context_request(
    request: TerminalMarketContextRequest,
) -> TerminalMarketContextRequest:

    if not isinstance(
        request,
        TerminalMarketContextRequest,
    ):
        raise TypeError(
            "request must be TerminalMarketContextRequest."
        )

    fields = []

    for value in request.requested_fields:
        text = _tmc_text(value).lower()

        if text and text not in fields:
            fields.append(text)

    metadata = dict(request.metadata or {})

    return TerminalMarketContextRequest(
        market=_tmc_text(request.market).upper(),
        instrument=_tmc_text(request.instrument).upper(),
        symbol=_tmc_text(request.symbol).upper(),
        contract=(
            _tmc_text(request.contract).upper()
            if request.contract is not None
            else None
        ),
        timeframe=_tmc_text(
            request.timeframe
        ) or None,
        session=_tmc_text(
            request.session
        ) or None,
        market_phase=_tmc_text(
            request.market_phase
        ) or None,
        mode=_tmc_enum(
            TerminalMarketContextMode,
            request.mode,
            TerminalMarketContextMode.UNKNOWN,
        ),
        priority=_tmc_enum(
            TerminalMarketContextPriority,
            request.priority,
            TerminalMarketContextPriority.NORMAL,
        ),
        requested_fields=tuple(fields),
        metadata=metadata,
        request_id=(
            _tmc_text(request.request_id)
            if request.request_id is not None
            else None
        ),
        timestamp=request.timestamp,
    )


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_terminal_market_context_request(
    request: TerminalMarketContextRequest,
) -> TerminalMarketContextContractValidation:

    errors = []
    warnings = []

    if not isinstance(
        request,
        TerminalMarketContextRequest,
    ):
        return TerminalMarketContextContractValidation(
            valid=False,
            errors=(
                "request must be "
                "TerminalMarketContextRequest.",
            ),
        )

    if not _tmc_text(request.market):
        errors.append("market is required.")

    if not _tmc_text(request.instrument):
        errors.append("instrument is required.")

    if not _tmc_text(request.symbol):
        errors.append("symbol is required.")

    if request.mode == TerminalMarketContextMode.UNKNOWN:
        warnings.append("Market context mode is UNKNOWN.")

    if not request.timeframe:
        warnings.append("No timeframe supplied.")

    if not request.requested_fields:
        warnings.append(
            "No requested_fields supplied; "
            "consumer may require the complete context."
        )

    return TerminalMarketContextContractValidation(
        valid=not errors,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


# ============================================================
# REFERENCE VALIDATION
# ============================================================

def validate_terminal_market_context_reference(
    reference: TerminalMarketContextReference,
) -> bool:

    if not isinstance(
        reference,
        TerminalMarketContextReference,
    ):
        return False

    if not _tmc_text(reference.market):
        return False

    if not _tmc_text(reference.instrument):
        return False

    if not _tmc_text(reference.symbol):
        return False

    if not _tmc_text(reference.version):
        return False

    if not isinstance(
        reference.status,
        TerminalMarketContextStatus,
    ):
        return False

    if not isinstance(
        reference.mode,
        TerminalMarketContextMode,
    ):
        return False

    return True


# ============================================================
# REQUEST BUILDER
# ============================================================

def build_terminal_market_context_request(
    *,
    market: str,
    instrument: str,
    symbol: str,
    contract: Optional[str] = None,
    timeframe: Optional[str] = None,
    session: Optional[str] = None,
    market_phase: Optional[str] = None,
    mode: Any = TerminalMarketContextMode.UNKNOWN,
    priority: Any = TerminalMarketContextPriority.NORMAL,
    requested_fields: Any = (),
    metadata: Optional[Mapping[str, Any]] = None,
    request_id: Optional[str] = None,
) -> TerminalMarketContextRequest:

    if requested_fields is None:
        requested_fields = ()

    if isinstance(requested_fields, str):
        requested_fields = (requested_fields,)

    try:
        fields = tuple(requested_fields)
    except TypeError:
        fields = ()

    request = TerminalMarketContextRequest(
        market=_tmc_text(market).upper(),
        instrument=_tmc_text(instrument).upper(),
        symbol=_tmc_text(symbol).upper(),
        contract=(
            _tmc_text(contract).upper()
            if contract is not None
            else None
        ),
        timeframe=_tmc_text(timeframe) or None,
        session=_tmc_text(session) or None,
        market_phase=_tmc_text(market_phase) or None,
        mode=_tmc_enum(
            TerminalMarketContextMode,
            mode,
            TerminalMarketContextMode.UNKNOWN,
        ),
        priority=_tmc_enum(
            TerminalMarketContextPriority,
            priority,
            TerminalMarketContextPriority.NORMAL,
        ),
        requested_fields=fields,
        metadata=dict(metadata or {}),
        request_id=(
            _tmc_text(request_id)
            if request_id is not None
            else None
        ),
    )

    return normalize_terminal_market_context_request(
        request
    )


# ============================================================
# REFERENCE BUILDER
# ============================================================

def build_terminal_market_context_reference(
    *,
    market: str,
    instrument: str,
    symbol: str,
    contract: Optional[str] = None,
    timeframe: Optional[str] = None,
    session: Optional[str] = None,
    market_phase: Optional[str] = None,
    status: Any = TerminalMarketContextStatus.UNKNOWN,
    mode: Any = TerminalMarketContextMode.UNKNOWN,
    source: str = "",
    updated_at: Any = None,
) -> TerminalMarketContextReference:

    return TerminalMarketContextReference(
        market=_tmc_text(market).upper(),
        instrument=_tmc_text(instrument).upper(),
        symbol=_tmc_text(symbol).upper(),
        contract=(
            _tmc_text(contract).upper()
            if contract is not None
            else None
        ),
        timeframe=_tmc_text(timeframe) or None,
        session=_tmc_text(session) or None,
        market_phase=_tmc_text(market_phase) or None,
        status=_tmc_enum(
            TerminalMarketContextStatus,
            status,
            TerminalMarketContextStatus.UNKNOWN,
        ),
        mode=_tmc_enum(
            TerminalMarketContextMode,
            mode,
            TerminalMarketContextMode.UNKNOWN,
        ),
        source=_tmc_text(source),
        version=TERMINAL_MARKET_CONTEXT_VERSION,
        updated_at=_tmc_timestamp(updated_at),
    )


# ============================================================
# AUTHORITY BOUNDARY
# ============================================================

def terminal_market_context_authority_boundary(
) -> Mapping[str, bool]:

    return {
        "terminal_context_presentation_authority": True,

        # Consumer only — intelligence is upstream.
        "market_intelligence_authority": False,
        "evidence_authority": False,
        "decision_authority": False,
        "d13_decision_authority": False,
        "risk_authority": False,
        "cas_authority": False,

        "execution_authority": False,
        "order_authority": False,
        "position_authority": False,

        # Terminal must not mutate source-of-truth state.
        "market_state_mutation_authority": False,
        "evidence_mutation_authority": False,
        "decision_mutation_authority": False,
    }


def validate_terminal_market_context_authority_boundary(
) -> bool:

    boundary = terminal_market_context_authority_boundary()

    forbidden = (
        "market_intelligence_authority",
        "evidence_authority",
        "decision_authority",
        "d13_decision_authority",
        "risk_authority",
        "cas_authority",
        "execution_authority",
        "order_authority",
        "position_authority",
        "market_state_mutation_authority",
        "evidence_mutation_authority",
        "decision_mutation_authority",
    )

    return all(
        boundary.get(key) is False
        for key in forbidden
    )
# ============================================================
# ROBOMLM TERMINAL
# market_context.py — PART 2
# STATE / CONSISTENCY / READINESS / ASSESSMENT
# ============================================================


# ============================================================
# ENUMS
# ============================================================

class TerminalMarketContextDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    INVALID = "INVALID"


class TerminalMarketContextConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONDITIONAL = "CONDITIONAL"
    INCONSISTENT = "INCONSISTENT"
    UNKNOWN = "UNKNOWN"


class TerminalMarketContextReadiness(str, Enum):
    READY = "READY"
    CONDITIONALLY_READY = "CONDITIONALLY_READY"
    NOT_READY = "NOT_READY"
    BLOCKED = "BLOCKED"


# ============================================================
# REQUIREMENTS
# ============================================================

@dataclass(frozen=True)
class TerminalMarketContextRequirements:
    require_market: bool = True
    require_instrument: bool = True
    require_symbol: bool = True

    require_timeframe: bool = False
    require_session: bool = False
    require_market_phase: bool = False
    require_contract: bool = False

    require_source: bool = False

    allow_unknown_mode: bool = True
    allow_missing_optional_context: bool = True

    minimum_quality: float = 50.0
    ready_quality: float = 80.0


def build_terminal_market_context_requirements(
    **overrides: Any,
) -> TerminalMarketContextRequirements:

    defaults = TerminalMarketContextRequirements()

    values = {
        field_name: getattr(defaults, field_name)
        for field_name in defaults.__dataclass_fields__
    }

    for key, value in overrides.items():
        if key in values:
            values[key] = value

    values["minimum_quality"] = max(
        0.0,
        min(100.0, float(values["minimum_quality"])),
    )

    values["ready_quality"] = max(
        values["minimum_quality"],
        min(100.0, float(values["ready_quality"])),
    )

    return TerminalMarketContextRequirements(**values)


# ============================================================
# ASSESSMENT CONTRACT
# ============================================================

@dataclass(frozen=True)
class TerminalMarketContextAssessment:
    data_state: TerminalMarketContextDataState
    consistency: TerminalMarketContextConsistency
    readiness: TerminalMarketContextReadiness

    completeness: float = 0.0
    context_quality: float = 0.0
    confidence: float = 0.0

    flags: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    unmet_requirements: Tuple[str, ...] = ()

    market: str = ""
    instrument: str = ""
    symbol: str = ""
    contract: Optional[str] = None

    timeframe: Optional[str] = None
    session: Optional[str] = None
    market_phase: Optional[str] = None

    status: TerminalMarketContextStatus = (
        TerminalMarketContextStatus.UNKNOWN
    )

    mode: TerminalMarketContextMode = (
        TerminalMarketContextMode.UNKNOWN
    )

    source: str = ""

    notes: Tuple[str, ...] = ()


# ============================================================
# DATA STATE
# ============================================================

def evaluate_terminal_market_context_data_state(
    request: TerminalMarketContextRequest,
) -> TerminalMarketContextDataState:

    if not isinstance(
        request,
        TerminalMarketContextRequest,
    ):
        return TerminalMarketContextDataState.INVALID

    validation = validate_terminal_market_context_request(
        request
    )

    if not validation.valid:
        return TerminalMarketContextDataState.INVALID

    required_values = (
        request.market,
        request.instrument,
        request.symbol,
    )

    present = sum(
        bool(_tmc_text(value))
        for value in required_values
    )

    if present == 0:
        return TerminalMarketContextDataState.MISSING

    if present < len(required_values):
        return TerminalMarketContextDataState.PARTIAL

    return TerminalMarketContextDataState.COMPLETE


# ============================================================
# CONSISTENCY
# ============================================================

def evaluate_terminal_market_context_consistency(
    request: TerminalMarketContextRequest,
) -> TerminalMarketContextConsistency:

    if not isinstance(
        request,
        TerminalMarketContextRequest,
    ):
        return TerminalMarketContextConsistency.INCONSISTENT

    if not _tmc_text(request.market):
        return TerminalMarketContextConsistency.UNKNOWN

    if not _tmc_text(request.instrument):
        return TerminalMarketContextConsistency.UNKNOWN

    if not _tmc_text(request.symbol):
        return TerminalMarketContextConsistency.UNKNOWN

    if request.market_phase and not request.session:
        return TerminalMarketContextConsistency.CONDITIONAL

    if request.contract and not request.instrument:
        return TerminalMarketContextConsistency.INCONSISTENT

    return TerminalMarketContextConsistency.CONSISTENT


# ============================================================
# REQUIREMENT EVALUATION
# ============================================================

def evaluate_terminal_market_context_requirements(
    request: TerminalMarketContextRequest,
    requirements: Optional[
        TerminalMarketContextRequirements
    ] = None,
) -> Tuple[str, ...]:

    requirements = (
        requirements
        or TerminalMarketContextRequirements()
    )

    unmet = []

    checks = (
        (
            requirements.require_market,
            request.market,
            "market",
        ),
        (
            requirements.require_instrument,
            request.instrument,
            "instrument",
        ),
        (
            requirements.require_symbol,
            request.symbol,
            "symbol",
        ),
        (
            requirements.require_timeframe,
            request.timeframe,
            "timeframe",
        ),
        (
            requirements.require_session,
            request.session,
            "session",
        ),
        (
            requirements.require_market_phase,
            request.market_phase,
            "market_phase",
        ),
        (
            requirements.require_contract,
            request.contract,
            "contract",
        ),
    )

    for required, value, name in checks:
        if required and not _tmc_text(value):
            unmet.append(
                f"{name} is required."
            )

    return tuple(unmet)


# ============================================================
# FLAGS
# ============================================================

def evaluate_terminal_market_context_flags(
    request: TerminalMarketContextRequest,
    *,
    source: str = "",
    status: TerminalMarketContextStatus = (
        TerminalMarketContextStatus.UNKNOWN
    ),
) -> Tuple[str, ...]:

    flags = []

    if not _tmc_text(request.market):
        flags.append("MARKET_MISSING")

    if not _tmc_text(request.instrument):
        flags.append("INSTRUMENT_MISSING")

    if not _tmc_text(request.symbol):
        flags.append("SYMBOL_MISSING")

    if not request.timeframe:
        flags.append("TIMEFRAME_MISSING")

    if not request.session:
        flags.append("SESSION_MISSING")

    if not request.market_phase:
        flags.append("MARKET_PHASE_MISSING")

    if request.mode == TerminalMarketContextMode.UNKNOWN:
        flags.append("MODE_UNKNOWN")

    if status == TerminalMarketContextStatus.STALE:
        flags.append("CONTEXT_STALE")

    if status == TerminalMarketContextStatus.INVALID:
        flags.append("CONTEXT_INVALID")

    if status == TerminalMarketContextStatus.ERROR:
        flags.append("CONTEXT_ERROR")

    if not _tmc_text(source):
        flags.append("SOURCE_UNKNOWN")

    return tuple(dict.fromkeys(flags))


# ============================================================
# COMPLETENESS
# ============================================================

def evaluate_terminal_market_context_completeness(
    request: TerminalMarketContextRequest,
) -> float:

    if not isinstance(
        request,
        TerminalMarketContextRequest,
    ):
        return 0.0

    fields = (
        request.market,
        request.instrument,
        request.symbol,
        request.contract,
        request.timeframe,
        request.session,
        request.market_phase,
    )

    present = sum(
        bool(_tmc_text(value))
        for value in fields
    )

    return round(
        (present / len(fields)) * 100.0,
        2,
    )


# ============================================================
# QUALITY
# ============================================================

def evaluate_terminal_market_context_quality(
    *,
    data_state: TerminalMarketContextDataState,
    consistency: TerminalMarketContextConsistency,
    completeness: float,
    status: TerminalMarketContextStatus,
    source_available: bool,
) -> float:

    if data_state == TerminalMarketContextDataState.INVALID:
        return 0.0

    if data_state == TerminalMarketContextDataState.MISSING:
        return 0.0

    score = float(completeness)

    if consistency == (
        TerminalMarketContextConsistency.CONSISTENT
    ):
        score += 10.0
    elif consistency == (
        TerminalMarketContextConsistency.CONDITIONAL
    ):
        score -= 5.0
    elif consistency == (
        TerminalMarketContextConsistency.INCONSISTENT
    ):
        score -= 30.0

    if status == TerminalMarketContextStatus.READY:
        score += 5.0
    elif status == TerminalMarketContextStatus.PARTIAL:
        score -= 5.0
    elif status == TerminalMarketContextStatus.STALE:
        score -= 20.0
    elif status in {
        TerminalMarketContextStatus.INVALID,
        TerminalMarketContextStatus.ERROR,
    }:
        score -= 40.0

    if source_available:
        score += 5.0
    else:
        score -= 5.0

    return round(
        max(0.0, min(100.0, score)),
        2,
    )


# ============================================================
# CONFIDENCE
# ============================================================

def evaluate_terminal_market_context_confidence(
    *,
    quality: float,
    data_state: TerminalMarketContextDataState,
    consistency: TerminalMarketContextConsistency,
) -> float:

    confidence = float(quality)

    if data_state == TerminalMarketContextDataState.COMPLETE:
        confidence += 5.0
    elif data_state == TerminalMarketContextDataState.PARTIAL:
        confidence -= 10.0

    if consistency == (
        TerminalMarketContextConsistency.CONSISTENT
    ):
        confidence += 5.0
    elif consistency == (
        TerminalMarketContextConsistency.CONDITIONAL
    ):
        confidence -= 10.0
    elif consistency == (
        TerminalMarketContextConsistency.INCONSISTENT
    ):
        confidence -= 30.0

    return round(
        max(0.0, min(100.0, confidence)),
        2,
    )


# ============================================================
# READINESS
# ============================================================

def evaluate_terminal_market_context_readiness(
    *,
    data_state: TerminalMarketContextDataState,
    consistency: TerminalMarketContextConsistency,
    quality: float,
    unmet_requirements: Tuple[str, ...],
    status: TerminalMarketContextStatus,
    requirements: TerminalMarketContextRequirements,
) -> TerminalMarketContextReadiness:

    if data_state == (
        TerminalMarketContextDataState.INVALID
    ):
        return TerminalMarketContextReadiness.BLOCKED

    if status in {
        TerminalMarketContextStatus.INVALID,
        TerminalMarketContextStatus.ERROR,
    }:
        return TerminalMarketContextReadiness.BLOCKED

    if consistency == (
        TerminalMarketContextConsistency.INCONSISTENT
    ):
        return TerminalMarketContextReadiness.BLOCKED

    if unmet_requirements:
        return TerminalMarketContextReadiness.NOT_READY

    if data_state == (
        TerminalMarketContextDataState.MISSING
    ):
        return TerminalMarketContextReadiness.NOT_READY

    if quality < requirements.minimum_quality:
        return TerminalMarketContextReadiness.NOT_READY

    if (
        quality < requirements.ready_quality
        or data_state == TerminalMarketContextDataState.PARTIAL
        or consistency == (
            TerminalMarketContextConsistency.CONDITIONAL
        )
    ):
        return TerminalMarketContextReadiness.CONDITIONALLY_READY

    return TerminalMarketContextReadiness.READY


# ============================================================
# ASSESSMENT BUILDER
# ============================================================

def build_terminal_market_context_assessment(
    request: TerminalMarketContextRequest,
    *,
    requirements: Optional[
        TerminalMarketContextRequirements
    ] = None,
    reference: Optional[
        TerminalMarketContextReference
    ] = None,
) -> TerminalMarketContextAssessment:

    normalized = normalize_terminal_market_context_request(
        request
    )

    requirements = (
        requirements
        or TerminalMarketContextRequirements()
    )

    reference_status = (
        reference.status
        if reference is not None
        else TerminalMarketContextStatus.UNKNOWN
    )

    reference_source = (
        reference.source
        if reference is not None
        else ""
    )

    status = reference_status

    if status == TerminalMarketContextStatus.UNKNOWN:
        status = TerminalMarketContextStatus.READY

    source = (
        _tmc_text(reference_source)
        or _tmc_text(
            normalized.metadata.get("source")
        )
    )

    data_state = (
        evaluate_terminal_market_context_data_state(
            normalized
        )
    )

    consistency = (
        evaluate_terminal_market_context_consistency(
            normalized
        )
    )

    unmet = (
        evaluate_terminal_market_context_requirements(
            normalized,
            requirements,
        )
    )

    completeness = (
        evaluate_terminal_market_context_completeness(
            normalized
        )
    )

    flags = evaluate_terminal_market_context_flags(
        normalized,
        source=source,
        status=status,
    )

    warnings = []

    if not normalized.timeframe:
        warnings.append("Timeframe is not supplied.")

    if not normalized.session:
        warnings.append("Session is not supplied.")

    if not normalized.market_phase:
        warnings.append(
            "Market phase is not supplied."
        )

    if not source:
        warnings.append(
            "Context source is not identified."
        )

    quality = evaluate_terminal_market_context_quality(
        data_state=data_state,
        consistency=consistency,
        completeness=completeness,
        status=status,
        source_available=bool(source),
    )

    confidence = evaluate_terminal_market_context_confidence(
        quality=quality,
        data_state=data_state,
        consistency=consistency,
    )

    readiness = evaluate_terminal_market_context_readiness(
        data_state=data_state,
        consistency=consistency,
        quality=quality,
        unmet_requirements=unmet,
        status=status,
        requirements=requirements,
    )

    notes = []

    if readiness == (
        TerminalMarketContextReadiness.READY
    ):
        notes.append(
            "Terminal market context is ready for presentation."
        )

    if readiness == (
        TerminalMarketContextReadiness.CONDITIONALLY_READY
    ):
        notes.append(
            "Context is usable with declared conditions."
        )

    if readiness == (
        TerminalMarketContextReadiness.NOT_READY
    ):
        notes.append(
            "Context is insufficient for complete presentation."
        )

    if readiness == (
        TerminalMarketContextReadiness.BLOCKED
    ):
        notes.append(
            "Context is blocked and must not be treated as valid."
        )

    return TerminalMarketContextAssessment(
        data_state=data_state,
        consistency=consistency,
        readiness=readiness,
        completeness=completeness,
        context_quality=quality,
        confidence=confidence,
        flags=tuple(flags),
        warnings=tuple(warnings),
        unmet_requirements=tuple(unmet),
        market=normalized.market,
        instrument=normalized.instrument,
        symbol=normalized.symbol,
        contract=normalized.contract,
        timeframe=normalized.timeframe,
        session=normalized.session,
        market_phase=normalized.market_phase,
        status=status,
        mode=normalized.mode,
        source=source,
        notes=tuple(notes),
    )
# ============================================================
# ROBOMLM TERMINAL
# market_context.py — PART 3
# RESOLUTION / PRESENTATION CONTRACT / UPSTREAM MAPPING
# ============================================================


# ============================================================
# RESOLUTION ENUMS
# ============================================================

class TerminalMarketContextDecision(str, Enum):
    ALLOW = "ALLOW"
    ALLOW_WITH_RESTRICTION = "ALLOW_WITH_RESTRICTION"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCK = "BLOCK"


class TerminalMarketContextResolutionStatus(str, Enum):
    RESOLVED = "RESOLVED"
    CONDITIONAL = "CONDITIONAL"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"


# ============================================================
# RESOLUTION RULES
# ============================================================

@dataclass(frozen=True)
class TerminalMarketContextResolutionRules:
    allow_partial: bool = True
    allow_conditional: bool = True
    allow_stale_for_display: bool = True

    block_invalid: bool = True
    block_error: bool = True
    block_inconsistent: bool = True

    minimum_display_quality: float = 50.0
    minimum_ready_quality: float = 80.0


def build_terminal_market_context_resolution_rules(
    **overrides: Any,
) -> TerminalMarketContextResolutionRules:

    defaults = TerminalMarketContextResolutionRules()

    values = {
        name: getattr(defaults, name)
        for name in defaults.__dataclass_fields__
    }

    for key, value in overrides.items():
        if key in values:
            values[key] = value

    values["minimum_display_quality"] = max(
        0.0,
        min(100.0, float(values["minimum_display_quality"])),
    )

    values["minimum_ready_quality"] = max(
        values["minimum_display_quality"],
        min(100.0, float(values["minimum_ready_quality"])),
    )

    return TerminalMarketContextResolutionRules(**values)


# ============================================================
# PRESENTATION CONTRACT
# ============================================================

@dataclass(frozen=True)
class TerminalMarketContextPresentation:
    market: str
    instrument: str
    symbol: str

    contract: Optional[str]
    timeframe: Optional[str]
    session: Optional[str]
    market_phase: Optional[str]

    status: TerminalMarketContextStatus
    mode: TerminalMarketContextMode

    source: str

    completeness: float
    context_quality: float
    confidence: float

    flags: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    notes: Tuple[str, ...] = ()

    updated_at: datetime = field(
        default_factory=_tmc_timestamp
    )


# ============================================================
# RESOLUTION RESULT
# ============================================================

@dataclass(frozen=True)
class TerminalMarketContextResult:
    decision: TerminalMarketContextDecision
    status: TerminalMarketContextResolutionStatus

    allowed: bool = False
    restricted: bool = False
    review_required: bool = False
    blocked: bool = False

    assessment: Optional[
        TerminalMarketContextAssessment
    ] = None

    presentation: Optional[
        TerminalMarketContextPresentation
    ] = None

    flags: Tuple[str, ...] = ()
    restrictions: Tuple[str, ...] = ()
    errors: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()

    reason: str = ""

    timestamp: datetime = field(
        default_factory=_tmc_timestamp
    )


# ============================================================
# UPSTREAM INTELLIGENCE MAPPING
# ============================================================

@dataclass(frozen=True)
class TerminalMarketContextSourceMap:
    """
    Defines where Terminal obtains context.

    Terminal consumes upstream intelligence/context.
    It does not calculate or mutate the source intelligence.
    """

    market_context_engine: str = (
        "app.intelligence.market_context"
    )

    market_data_source: str = (
        "market_data"
    )

    evidence_source: str = (
        "app.intelligence.evidence"
    )

    decision_source: str = (
        "app.intelligence.decision"
    )

    risk_source: str = (
        "app.intelligence.cas"
    )

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )


def build_terminal_market_context_source_map(
    **overrides: Any,
) -> TerminalMarketContextSourceMap:

    defaults = TerminalMarketContextSourceMap()

    values = {
        name: getattr(defaults, name)
        for name in defaults.__dataclass_fields__
    }

    for key, value in overrides.items():
        if key in values:
            values[key] = value

    return TerminalMarketContextSourceMap(**values)


# ============================================================
# RESOLUTION FLAGS
# ============================================================

def collect_terminal_market_context_resolution_flags(
    assessment: TerminalMarketContextAssessment,
) -> Tuple[str, ...]:

    flags = list(assessment.flags)

    if assessment.readiness == (
        TerminalMarketContextReadiness.BLOCKED
    ):
        flags.append("CONTEXT_BLOCKED")

    if assessment.readiness == (
        TerminalMarketContextReadiness.NOT_READY
    ):
        flags.append("CONTEXT_NOT_READY")

    if assessment.readiness == (
        TerminalMarketContextReadiness.CONDITIONALLY_READY
    ):
        flags.append("CONTEXT_CONDITIONAL")

    if assessment.status == (
        TerminalMarketContextStatus.STALE
    ):
        flags.append("CONTEXT_STALE")

    return tuple(dict.fromkeys(flags))


# ============================================================
# RESTRICTIONS
# ============================================================

def collect_terminal_market_context_restrictions(
    assessment: TerminalMarketContextAssessment,
) -> Tuple[str, ...]:

    restrictions = []

    if assessment.status == (
        TerminalMarketContextStatus.STALE
    ):
        restrictions.append(
            "DISPLAY_STALE_WARNING"
        )

    if assessment.data_state == (
        TerminalMarketContextDataState.PARTIAL
    ):
        restrictions.append(
            "PARTIAL_CONTEXT_ONLY"
        )

    if assessment.consistency == (
        TerminalMarketContextConsistency.CONDITIONAL
    ):
        restrictions.append(
            "CONDITIONAL_CONTEXT"
        )

    if assessment.confidence < 50.0:
        restrictions.append(
            "LOW_CONTEXT_CONFIDENCE"
        )

    return tuple(dict.fromkeys(restrictions))


# ============================================================
# PRESENTATION BUILDER
# ============================================================

def build_terminal_market_context_presentation(
    assessment: TerminalMarketContextAssessment,
) -> TerminalMarketContextPresentation:

    if not isinstance(
        assessment,
        TerminalMarketContextAssessment,
    ):
        raise TypeError(
            "assessment must be "
            "TerminalMarketContextAssessment."
        )

    return TerminalMarketContextPresentation(
        market=assessment.market,
        instrument=assessment.instrument,
        symbol=assessment.symbol,
        contract=assessment.contract,
        timeframe=assessment.timeframe,
        session=assessment.session,
        market_phase=assessment.market_phase,
        status=assessment.status,
        mode=assessment.mode,
        source=assessment.source,
        completeness=assessment.completeness,
        context_quality=assessment.context_quality,
        confidence=assessment.confidence,
        flags=assessment.flags,
        warnings=assessment.warnings,
        notes=assessment.notes,
    )


# ============================================================
# RESOLUTION
# ============================================================

def resolve_terminal_market_context(
    request: TerminalMarketContextRequest,
    *,
    requirements: Optional[
        TerminalMarketContextRequirements
    ] = None,
    rules: Optional[
        TerminalMarketContextResolutionRules
    ] = None,
    reference: Optional[
        TerminalMarketContextReference
    ] = None,
) -> TerminalMarketContextResult:

    rules = (
        rules
        or TerminalMarketContextResolutionRules()
    )

    validation = validate_terminal_market_context_request(
        request
    )

    if not validation.valid:
        return TerminalMarketContextResult(
            decision=TerminalMarketContextDecision.BLOCK,
            status=TerminalMarketContextResolutionStatus.BLOCKED,
            blocked=True,
            errors=validation.errors,
            warnings=validation.warnings,
            reason="Invalid market context request.",
        )

    assessment = build_terminal_market_context_assessment(
        request,
        requirements=requirements,
        reference=reference,
    )

    flags = collect_terminal_market_context_resolution_flags(
        assessment
    )

    restrictions = (
        collect_terminal_market_context_restrictions(
            assessment
        )
    )

    errors = []
    warnings = list(assessment.warnings)

    if assessment.data_state == (
        TerminalMarketContextDataState.INVALID
    ):
        errors.append("Market context data is invalid.")

    if assessment.consistency == (
        TerminalMarketContextConsistency.INCONSISTENT
    ):
        errors.append(
            "Market context is internally inconsistent."
        )

    if assessment.status == (
        TerminalMarketContextStatus.ERROR
    ):
        errors.append(
            "Market context source returned an error state."
        )

    if (
        assessment.status == TerminalMarketContextStatus.STALE
        and not rules.allow_stale_for_display
    ):
        errors.append(
            "Stale market context is not allowed."
        )

    # --------------------------------------------------------
    # HARD BLOCK
    # --------------------------------------------------------

    if (
        rules.block_invalid
        and assessment.status
        == TerminalMarketContextStatus.INVALID
    ):
        return TerminalMarketContextResult(
            decision=TerminalMarketContextDecision.BLOCK,
            status=TerminalMarketContextResolutionStatus.BLOCKED,
            blocked=True,
            assessment=assessment,
            flags=flags,
            restrictions=restrictions,
            errors=tuple(errors),
            warnings=tuple(warnings),
            reason="Market context is invalid.",
        )

    if (
        rules.block_error
        and assessment.status
        == TerminalMarketContextStatus.ERROR
    ):
        return TerminalMarketContextResult(
            decision=TerminalMarketContextDecision.BLOCK,
            status=TerminalMarketContextResolutionStatus.BLOCKED,
            blocked=True,
            assessment=assessment,
            flags=flags,
            restrictions=restrictions,
            errors=tuple(errors),
            warnings=tuple(warnings),
            reason="Market context is in error state.",
        )

    if (
        rules.block_inconsistent
        and assessment.consistency
        == TerminalMarketContextConsistency.INCONSISTENT
    ):
        return TerminalMarketContextResult(
            decision=TerminalMarketContextDecision.BLOCK,
            status=TerminalMarketContextResolutionStatus.BLOCKED,
            blocked=True,
            assessment=assessment,
            flags=flags,
            restrictions=restrictions,
            errors=tuple(errors),
            warnings=tuple(warnings),
            reason="Market context is inconsistent.",
        )

    # --------------------------------------------------------
    # REQUIREMENT FAILURE
    # --------------------------------------------------------

    if assessment.unmet_requirements:
        return TerminalMarketContextResult(
            decision=TerminalMarketContextDecision.REVIEW_REQUIRED,
            status=TerminalMarketContextResolutionStatus.REVIEW_REQUIRED,
            review_required=True,
            assessment=assessment,
            flags=flags,
            restrictions=restrictions,
            errors=tuple(errors),
            warnings=tuple(warnings),
            reason="Required market context fields are missing.",
        )

    # --------------------------------------------------------
    # QUALITY BELOW DISPLAY THRESHOLD
    # --------------------------------------------------------

    if (
        assessment.context_quality
        < rules.minimum_display_quality
    ):
        return TerminalMarketContextResult(
            decision=TerminalMarketContextDecision.REVIEW_REQUIRED,
            status=TerminalMarketContextResolutionStatus.REVIEW_REQUIRED,
            review_required=True,
            assessment=assessment,
            flags=flags,
            restrictions=restrictions,
            errors=tuple(errors),
            warnings=tuple(warnings),
            reason="Market context quality is below display threshold.",
        )

    # --------------------------------------------------------
    # CONDITIONAL
    # --------------------------------------------------------

    conditional = (
        assessment.readiness
        == TerminalMarketContextReadiness.CONDITIONALLY_READY
        or bool(restrictions)
        or assessment.status
        == TerminalMarketContextStatus.STALE
    )

    if conditional:
        if not rules.allow_conditional:
            return TerminalMarketContextResult(
                decision=TerminalMarketContextDecision.REVIEW_REQUIRED,
                status=TerminalMarketContextResolutionStatus.REVIEW_REQUIRED,
                review_required=True,
                assessment=assessment,
                flags=flags,
                restrictions=restrictions,
                errors=tuple(errors),
                warnings=tuple(warnings),
                reason="Conditional market context requires review.",
            )

        presentation = (
            build_terminal_market_context_presentation(
                assessment
            )
        )

        return TerminalMarketContextResult(
            decision=TerminalMarketContextDecision.ALLOW_WITH_RESTRICTION,
            status=TerminalMarketContextResolutionStatus.CONDITIONAL,
            allowed=True,
            restricted=True,
            assessment=assessment,
            presentation=presentation,
            flags=flags,
            restrictions=restrictions,
            errors=tuple(errors),
            warnings=tuple(warnings),
            reason="Market context is available with declared restrictions.",
        )

    # --------------------------------------------------------
    # FULL RESOLUTION
    # --------------------------------------------------------

    presentation = (
        build_terminal_market_context_presentation(
            assessment
        )
    )

    return TerminalMarketContextResult(
        decision=TerminalMarketContextDecision.ALLOW,
        status=TerminalMarketContextResolutionStatus.RESOLVED,
        allowed=True,
        assessment=assessment,
        presentation=presentation,
        flags=flags,
        restrictions=restrictions,
        errors=tuple(errors),
        warnings=tuple(warnings),
        reason="Market context resolved for terminal presentation.",
    )


# ============================================================
# RESULT VALIDATION
# ============================================================

def validate_terminal_market_context_result(
    result: TerminalMarketContextResult,
) -> bool:

    if not isinstance(
        result,
        TerminalMarketContextResult,
    ):
        return False

    if result.allowed and result.blocked:
        return False

    if result.restricted and not result.allowed:
        return False

    if result.review_required and result.allowed:
        return False

    if result.decision == (
        TerminalMarketContextDecision.BLOCK
    ) and not result.blocked:
        return False

    if result.decision == (
        TerminalMarketContextDecision.ALLOW
    ) and not result.allowed:
        return False

    if result.decision == (
        TerminalMarketContextDecision.ALLOW_WITH_RESTRICTION
    ):
        if not result.allowed or not result.restricted:
            return False

    if result.decision == (
        TerminalMarketContextDecision.REVIEW_REQUIRED
    ) and not result.review_required:
        return False

    if result.allowed and result.presentation is None:
        return False

    return True


# ============================================================
# AUTHORITY VALIDATION
# ============================================================

def validate_terminal_market_context_result_authority(
    result: TerminalMarketContextResult,
) -> bool:

    if not validate_terminal_market_context_result(
        result
    ):
        return False

    return validate_terminal_market_context_authority_boundary()
# ============================================================
# ROBOMLM TERMINAL
# market_context.py — PART 4
# CONTEXT REGISTRY / SNAPSHOT / SERVICE LAYER
# ============================================================


# ============================================================
# REGISTRY CONTRACTS
# ============================================================

@dataclass(frozen=True)
class TerminalMarketContextRegistryEntry:
    reference: TerminalMarketContextReference
    revision: int = 1
    updated_at: datetime = field(
        default_factory=_tmc_timestamp
    )


@dataclass(frozen=True)
class TerminalMarketContextRegistrySnapshot:
    total: int
    ready: int
    partial: int
    stale: int
    invalid: int
    error: int

    references: Tuple[
        TerminalMarketContextReference,
        ...,
    ] = ()

    timestamp: datetime = field(
        default_factory=_tmc_timestamp
    )


# ============================================================
# REGISTRY
# ============================================================

class TerminalMarketContextRegistry:
    """
    In-process registry of terminal-readable market-context
    references.

    This registry stores presentation references only.
    It does not become the source of market intelligence.
    """

    def __init__(self) -> None:
        self._entries: dict[
            str,
            TerminalMarketContextRegistryEntry,
        ] = {}

    @staticmethod
    def _key(
        reference: TerminalMarketContextReference,
    ) -> str:
        return (
            f"{reference.market}:"
            f"{reference.instrument}:"
            f"{reference.symbol}:"
            f"{reference.contract or ''}:"
            f"{reference.timeframe or ''}"
        )

    def exists(
        self,
        reference_or_key: Any,
    ) -> bool:
        if isinstance(
            reference_or_key,
            TerminalMarketContextReference,
        ):
            key = self._key(reference_or_key)
        else:
            key = _tmc_text(reference_or_key)

        return key in self._entries

    def get(
        self,
        reference_or_key: Any,
    ) -> Optional[
        TerminalMarketContextReference
    ]:
        if isinstance(
            reference_or_key,
            TerminalMarketContextReference,
        ):
            key = self._key(reference_or_key)
        else:
            key = _tmc_text(reference_or_key)

        entry = self._entries.get(key)

        return (
            entry.reference
            if entry is not None
            else None
        )

    def get_entry(
        self,
        reference_or_key: Any,
    ) -> Optional[
        TerminalMarketContextRegistryEntry
    ]:
        if isinstance(
            reference_or_key,
            TerminalMarketContextReference,
        ):
            key = self._key(reference_or_key)
        else:
            key = _tmc_text(reference_or_key)

        return self._entries.get(key)

    def add(
        self,
        reference: TerminalMarketContextReference,
    ) -> TerminalMarketContextRegistryEntry:

        if not validate_terminal_market_context_reference(
            reference
        ):
            raise ValueError(
                "Invalid terminal market context reference."
            )

        key = self._key(reference)

        if key in self._entries:
            raise ValueError(
                f"Market context already exists: {key}"
            )

        entry = TerminalMarketContextRegistryEntry(
            reference=reference,
            revision=1,
        )

        self._entries[key] = entry
        return entry

    def replace(
        self,
        reference: TerminalMarketContextReference,
    ) -> TerminalMarketContextRegistryEntry:

        if not validate_terminal_market_context_reference(
            reference
        ):
            raise ValueError(
                "Invalid terminal market context reference."
            )

        key = self._key(reference)

        previous = self._entries.get(key)

        revision = (
            previous.revision + 1
            if previous is not None
            else 1
        )

        entry = TerminalMarketContextRegistryEntry(
            reference=reference,
            revision=revision,
        )

        self._entries[key] = entry
        return entry

    def remove(
        self,
        reference_or_key: Any,
    ) -> bool:

        if isinstance(
            reference_or_key,
            TerminalMarketContextReference,
        ):
            key = self._key(reference_or_key)
        else:
            key = _tmc_text(reference_or_key)

        return (
            self._entries.pop(
                key,
                None,
            )
            is not None
        )

    def list_references(
        self,
        *,
        market: Optional[str] = None,
        instrument: Optional[str] = None,
        symbol: Optional[str] = None,
        timeframe: Optional[str] = None,
        status: Optional[
            TerminalMarketContextStatus
        ] = None,
    ) -> Tuple[
        TerminalMarketContextReference,
        ...,
    ]:

        normalized_market = (
            _tmc_text(market).upper()
        )

        normalized_instrument = (
            _tmc_text(instrument).upper()
        )

        normalized_symbol = (
            _tmc_text(symbol).upper()
        )

        normalized_timeframe = (
            _tmc_text(timeframe)
        )

        result = []

        for entry in self._entries.values():
            reference = entry.reference

            if (
                normalized_market
                and reference.market
                != normalized_market
            ):
                continue

            if (
                normalized_instrument
                and reference.instrument
                != normalized_instrument
            ):
                continue

            if (
                normalized_symbol
                and reference.symbol
                != normalized_symbol
            ):
                continue

            if (
                normalized_timeframe
                and reference.timeframe
                != normalized_timeframe
            ):
                continue

            if (
                status is not None
                and reference.status != status
            ):
                continue

            result.append(reference)

        result.sort(
            key=lambda item: (
                item.market,
                item.instrument,
                item.symbol,
                item.timeframe or "",
            )
        )

        return tuple(result)

    def snapshot(
        self,
    ) -> TerminalMarketContextRegistrySnapshot:

        references = tuple(
            entry.reference
            for entry in self._entries.values()
        )

        counts = {
            TerminalMarketContextStatus.READY: 0,
            TerminalMarketContextStatus.PARTIAL: 0,
            TerminalMarketContextStatus.STALE: 0,
            TerminalMarketContextStatus.INVALID: 0,
            TerminalMarketContextStatus.ERROR: 0,
        }

        for reference in references:
            if reference.status in counts:
                counts[reference.status] += 1

        ordered = tuple(
            sorted(
                references,
                key=lambda item: (
                    item.market,
                    item.instrument,
                    item.symbol,
                    item.timeframe or "",
                ),
            )
        )

        return TerminalMarketContextRegistrySnapshot(
            total=len(references),
            ready=counts[
                TerminalMarketContextStatus.READY
            ],
            partial=counts[
                TerminalMarketContextStatus.PARTIAL
            ],
            stale=counts[
                TerminalMarketContextStatus.STALE
            ],
            invalid=counts[
                TerminalMarketContextStatus.INVALID
            ],
            error=counts[
                TerminalMarketContextStatus.ERROR
            ],
            references=ordered,
        )

    def count(self) -> int:
        return len(self._entries)


# ============================================================
# REGISTRY VALIDATION / HEALTH
# ============================================================

def validate_terminal_market_context_registry(
    registry: TerminalMarketContextRegistry,
) -> bool:

    if not isinstance(
        registry,
        TerminalMarketContextRegistry,
    ):
        return False

    for entry in registry._entries.values():
        if not isinstance(
            entry,
            TerminalMarketContextRegistryEntry,
        ):
            return False

        if entry.revision < 1:
            return False

        if not validate_terminal_market_context_reference(
            entry.reference
        ):
            return False

    snapshot = registry.snapshot()

    return (
        snapshot.total
        == registry.count()
        and len(snapshot.references)
        == snapshot.total
    )


def terminal_market_context_registry_health(
    registry: TerminalMarketContextRegistry,
) -> Mapping[str, Any]:

    valid = validate_terminal_market_context_registry(
        registry
    )

    snapshot = registry.snapshot()

    return {
        "healthy": valid,
        "engine": TERMINAL_MARKET_CONTEXT_ENGINE,
        "version": TERMINAL_MARKET_CONTEXT_VERSION,
        "count": snapshot.total,
        "ready": snapshot.ready,
        "partial": snapshot.partial,
        "stale": snapshot.stale,
        "invalid": snapshot.invalid,
        "error": snapshot.error,
    }


# ============================================================
# SERVICE RESULT
# ============================================================

@dataclass(frozen=True)
class TerminalMarketContextServiceResult:
    success: bool
    decision: TerminalMarketContextDecision

    request_id: Optional[str] = None

    assessment: Optional[
        TerminalMarketContextAssessment
    ] = None

    result: Optional[
        TerminalMarketContextResult
    ] = None

    reference: Optional[
        TerminalMarketContextReference
    ] = None

    errors: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()

    reason: str = ""

    timestamp: datetime = field(
        default_factory=_tmc_timestamp
    )


# ============================================================
# SERVICE
# ============================================================

class TerminalMarketContextService:
    """
    Application/service facade for terminal market context.

    Responsibilities:
      - accept terminal context requests
      - resolve upstream context
      - maintain terminal-readable references
      - provide snapshots and health

    Non-responsibilities:
      - market intelligence calculation
      - evidence generation
      - D13 decision generation
      - risk calculation
      - CAS authorization
      - execution
    """

    def __init__(self) -> None:
        self.registry = TerminalMarketContextRegistry()

    def resolve(
        self,
        request: TerminalMarketContextRequest,
        *,
        requirements: Optional[
            TerminalMarketContextRequirements
        ] = None,
        rules: Optional[
            TerminalMarketContextResolutionRules
        ] = None,
        reference: Optional[
            TerminalMarketContextReference
        ] = None,
    ) -> TerminalMarketContextResult:

        return resolve_terminal_market_context(
            request,
            requirements=requirements,
            rules=rules,
            reference=reference,
        )

    def assess(
        self,
        request: TerminalMarketContextRequest,
        *,
        requirements: Optional[
            TerminalMarketContextRequirements
        ] = None,
        reference: Optional[
            TerminalMarketContextReference
        ] = None,
    ) -> TerminalMarketContextAssessment:

        return build_terminal_market_context_assessment(
            request,
            requirements=requirements,
            reference=reference,
        )

    def register(
        self,
        reference: TerminalMarketContextReference,
    ) -> TerminalMarketContextRegistryEntry:

        if self.registry.exists(reference):
            return self.registry.replace(reference)

        return self.registry.add(reference)

    def get(
        self,
        reference_or_key: Any,
    ) -> Optional[
        TerminalMarketContextReference
    ]:

        return self.registry.get(reference_or_key)

    def list_references(
        self,
        *,
        market: Optional[str] = None,
        instrument: Optional[str] = None,
        symbol: Optional[str] = None,
        timeframe: Optional[str] = None,
        status: Optional[
            TerminalMarketContextStatus
        ] = None,
    ) -> Tuple[
        TerminalMarketContextReference,
        ...,
    ]:

        return self.registry.list_references(
            market=market,
            instrument=instrument,
            symbol=symbol,
            timeframe=timeframe,
            status=status,
        )

    def snapshot(
        self,
    ) -> TerminalMarketContextRegistrySnapshot:

        return self.registry.snapshot()

    def health(self) -> Mapping[str, Any]:

        return terminal_market_context_registry_health(
            self.registry
        )

    def integrity(self) -> bool:

        return validate_terminal_market_context_registry(
            self.registry
        )

    def info(self) -> Mapping[str, Any]:

        return {
            "engine": TERMINAL_MARKET_CONTEXT_ENGINE,
            "version": TERMINAL_MARKET_CONTEXT_VERSION,
            "registry_count": self.registry.count(),
            "authority":
                terminal_market_context_authority_boundary(),
            "healthy": self.integrity(),
        }


# ============================================================
# SINGLETON
# ============================================================

_TERMINAL_MARKET_CONTEXT_SERVICE = (
    TerminalMarketContextService()
)


def get_terminal_market_context_service(
) -> TerminalMarketContextService:

    return _TERMINAL_MARKET_CONTEXT_SERVICE


# ============================================================
# CONVENIENCE API
# ============================================================

def resolve_market_context_for_terminal(
    request: TerminalMarketContextRequest,
    *,
    requirements: Optional[
        TerminalMarketContextRequirements
    ] = None,
    rules: Optional[
        TerminalMarketContextResolutionRules
    ] = None,
    reference: Optional[
        TerminalMarketContextReference
    ] = None,
) -> TerminalMarketContextResult:

    return (
        _TERMINAL_MARKET_CONTEXT_SERVICE.resolve(
            request,
            requirements=requirements,
            rules=rules,
            reference=reference,
        )
    )


def get_terminal_market_context(
    reference_or_key: Any,
) -> Optional[
    TerminalMarketContextReference
]:

    return _TERMINAL_MARKET_CONTEXT_SERVICE.get(
        reference_or_key
    )


def terminal_market_context_snapshot(
) -> TerminalMarketContextRegistrySnapshot:

    return _TERMINAL_MARKET_CONTEXT_SERVICE.snapshot()


def terminal_market_context_count() -> int:

    return (
        _TERMINAL_MARKET_CONTEXT_SERVICE.registry.count()
    )


def terminal_market_context_health(
) -> Mapping[str, Any]:

    return _TERMINAL_MARKET_CONTEXT_SERVICE.health()


def terminal_market_context_integrity() -> bool:

    return _TERMINAL_MARKET_CONTEXT_SERVICE.integrity()


def terminal_market_context_operational_check() -> bool:

    if not validate_terminal_market_context_authority_boundary():
        return False

    if not _TERMINAL_MARKET_CONTEXT_SERVICE.integrity():
        return False

    return True


def terminal_market_context_service_info(
) -> Mapping[str, Any]:

    return _TERMINAL_MARKET_CONTEXT_SERVICE.info()

# ============================================================
# ROBOMLM_PLUS
# app/terminal/market_context.py
# PART 5 / 5
# Serialization + Integrity + Summary + Public API
# ============================================================

from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict


def _tmc_iso(value: Any) -> Any:
    """Convert datetime values into stable ISO strings."""
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _tmc_serialize(value: Any) -> Any:
    """Recursive terminal-market-context serializer."""
    if isinstance(value, datetime):
        return value.isoformat()

    if hasattr(value, "value"):
        return value.value

    if hasattr(value, "__dataclass_fields__"):
        return {
            key: _tmc_serialize(val)
            for key, val in asdict(value).items()
        }

    if isinstance(value, dict):
        return {
            str(key): _tmc_serialize(val)
            for key, val in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [_tmc_serialize(item) for item in value]

    return value


# ------------------------------------------------------------
# SERIALIZATION
# ------------------------------------------------------------

def serialize_terminal_market_context_reference(
    reference: TerminalMarketContextReference,
) -> Dict[str, Any]:
    return _tmc_serialize(reference)


def serialize_terminal_market_context_assessment(
    assessment: TerminalMarketContextAssessment,
) -> Dict[str, Any]:
    return _tmc_serialize(assessment)


def serialize_terminal_market_context_presentation(
    presentation: TerminalMarketContextPresentation,
) -> Dict[str, Any]:
    return _tmc_serialize(presentation)


def serialize_terminal_market_context_result(
    result: TerminalMarketContextResult,
) -> Dict[str, Any]:
    return _tmc_serialize(result)


def serialize_terminal_market_context_service_result(
    service_result: TerminalMarketContextServiceResult,
) -> Dict[str, Any]:
    return _tmc_serialize(service_result)


def serialize_terminal_market_context_snapshot(
    snapshot: TerminalMarketContextRegistrySnapshot,
) -> Dict[str, Any]:
    return _tmc_serialize(snapshot)


# ------------------------------------------------------------
# INTEGRITY VALIDATION
# ------------------------------------------------------------

def validate_terminal_market_context_integrity(
    reference: TerminalMarketContextReference,
) -> TerminalMarketContextContractValidation:
    validation = validate_terminal_market_context_reference(reference)

    errors = list(validation.errors)
    warnings = list(validation.warnings)

    if not _tmc_text(reference.market):
        errors.append("market_missing")

    if not _tmc_text(reference.instrument):
        errors.append("instrument_missing")

    if not _tmc_text(reference.symbol):
        errors.append("symbol_missing")

    if not _tmc_text(reference.version):
        errors.append("version_missing")

    if reference.status not in TerminalMarketContextStatus:
        errors.append("invalid_status")

    if reference.mode not in TerminalMarketContextMode:
        errors.append("invalid_mode")

    return TerminalMarketContextContractValidation(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


def validate_terminal_market_context_snapshot_integrity(
    snapshot: TerminalMarketContextRegistrySnapshot,
) -> bool:
    references = snapshot.references or []

    if snapshot.total != len(references):
        return False

    counted = (
        snapshot.ready
        + snapshot.partial
        + snapshot.stale
        + snapshot.invalid
        + snapshot.error
    )

    if counted != snapshot.total:
        return False

    for reference in references:
        validation = validate_terminal_market_context_integrity(reference)
        if not validation.valid:
            return False

    return True


def validate_terminal_market_context_presentation_integrity(
    presentation: TerminalMarketContextPresentation,
) -> bool:
    if not _tmc_text(presentation.market):
        return False

    if not _tmc_text(presentation.instrument):
        return False

    if not _tmc_text(presentation.symbol):
        return False

    if not 0.0 <= float(presentation.completeness) <= 100.0:
        return False

    if not 0.0 <= float(presentation.context_quality) <= 100.0:
        return False

    if not 0.0 <= float(presentation.confidence) <= 100.0:
        return False

    if presentation.status not in TerminalMarketContextStatus:
        return False

    if presentation.mode not in TerminalMarketContextMode:
        return False

    return True


def validate_terminal_market_context_result_integrity(
    result: TerminalMarketContextResult,
) -> bool:
    if not validate_terminal_market_context_result(result):
        return False

    states = [
        bool(result.allowed),
        bool(result.restricted),
        bool(result.review_required),
        bool(result.blocked),
    ]

    # Exactly one terminal state must be active.
    if sum(states) != 1:
        return False

    if result.decision == TerminalMarketContextDecision.ALLOW:
        return result.allowed and not result.restricted

    if result.decision == TerminalMarketContextDecision.ALLOW_WITH_RESTRICTION:
        return result.restricted and result.allowed

    if result.decision == TerminalMarketContextDecision.REVIEW_REQUIRED:
        return result.review_required and not result.allowed

    if result.decision == TerminalMarketContextDecision.BLOCK:
        return result.blocked and not result.allowed

    return False


def validate_terminal_market_context_service_result_integrity(
    service_result: TerminalMarketContextServiceResult,
) -> bool:
    if not isinstance(service_result.success, bool):
        return False

    if not _tmc_text(service_result.request_id):
        return False

    if service_result.result is not None:
        if not validate_terminal_market_context_result_integrity(
            service_result.result
        ):
            return False

    if service_result.reference is not None:
        if not validate_terminal_market_context_integrity(
            service_result.reference
        ).valid:
            return False

    if service_result.success and service_result.errors:
        return False

    return True


# ------------------------------------------------------------
# SUMMARY
# ------------------------------------------------------------

def build_terminal_market_context_summary(
    result: TerminalMarketContextResult,
) -> Dict[str, Any]:
    assessment = result.assessment
    presentation = result.presentation

    return {
        "engine": TERMINAL_MARKET_CONTEXT_ENGINE,
        "version": TERMINAL_MARKET_CONTEXT_VERSION,
        "decision": result.decision.value,
        "resolution_status": result.status.value,
        "allowed": result.allowed,
        "restricted": result.restricted,
        "review_required": result.review_required,
        "blocked": result.blocked,
        "market": presentation.market,
        "instrument": presentation.instrument,
        "symbol": presentation.symbol,
        "contract": presentation.contract,
        "timeframe": presentation.timeframe,
        "session": presentation.session,
        "market_phase": presentation.market_phase,
        "mode": presentation.mode.value,
        "source": presentation.source,
        "status": presentation.status.value,
        "completeness": presentation.completeness,
        "context_quality": presentation.context_quality,
        "confidence": presentation.confidence,
        "flags": list(result.flags),
        "restrictions": list(result.restrictions),
        "warnings": list(result.warnings),
        "errors": list(result.errors),
        "reason": result.reason,
        "updated_at": _tmc_iso(presentation.updated_at),
        "assessment_ready": (
            assessment.readiness.value
            if assessment is not None
            else None
        ),
    }


# ------------------------------------------------------------
# FINAL PUBLIC API
# ------------------------------------------------------------

__all__ = [
    # Constants
    "TERMINAL_MARKET_CONTEXT_ENGINE",
    "TERMINAL_MARKET_CONTEXT_VERSION",

    # Enums
    "TerminalMarketContextStatus",
    "TerminalMarketContextMode",
    "TerminalMarketContextPriority",
    "TerminalMarketContextContractStatus",
    "TerminalMarketContextDataState",
    "TerminalMarketContextConsistency",
    "TerminalMarketContextReadiness",
    "TerminalMarketContextDecision",
    "TerminalMarketContextResolutionStatus",

    # Core contracts
    "TerminalMarketContextRequest",
    "TerminalMarketContextReference",
    "TerminalMarketContextContractValidation",
    "TerminalMarketContextRequirements",
    "TerminalMarketContextAssessment",
    "TerminalMarketContextResolutionRules",
    "TerminalMarketContextPresentation",
    "TerminalMarketContextResult",
    "TerminalMarketContextSourceMap",
    "TerminalMarketContextRegistryEntry",
    "TerminalMarketContextRegistrySnapshot",
    "TerminalMarketContextServiceResult",

    # Requirements / normalization
    "normalize_terminal_market_context_request",
    "validate_terminal_market_context_request",
    "validate_terminal_market_context_reference",
    "build_terminal_market_context_request",
    "build_terminal_market_context_reference",
    "build_terminal_market_context_requirements",
    "build_terminal_market_context_resolution_rules",

    # Assessment
    "evaluate_terminal_market_context_data_state",
    "evaluate_terminal_market_context_consistency",
    "evaluate_terminal_market_context_requirements",
    "evaluate_terminal_market_context_flags",
    "evaluate_terminal_market_context_completeness",
    "evaluate_terminal_market_context_quality",
    "evaluate_terminal_market_context_confidence",
    "evaluate_terminal_market_context_readiness",
    "build_terminal_market_context_assessment",

    # Resolution
    "collect_terminal_market_context_resolution_flags",
    "collect_terminal_market_context_restrictions",
    "build_terminal_market_context_presentation",
    "resolve_terminal_market_context",
    "validate_terminal_market_context_result",
    "validate_terminal_market_context_result_authority",
    "build_terminal_market_context_source_map",

    # Registry
    "TerminalMarketContextRegistry",
    "validate_terminal_market_context_registry",
    "terminal_market_context_registry_health",

    # Service
    "TerminalMarketContextService",
    "get_terminal_market_context_service",
    "resolve_market_context_for_terminal",
    "get_terminal_market_context",
    "terminal_market_context_snapshot",
    "terminal_market_context_count",
    "terminal_market_context_health",
    "terminal_market_context_integrity",
    "terminal_market_context_operational_check",
    "terminal_market_context_service_info",

    # Serialization
    "serialize_terminal_market_context_reference",
    "serialize_terminal_market_context_assessment",
    "serialize_terminal_market_context_presentation",
    "serialize_terminal_market_context_result",
    "serialize_terminal_market_context_service_result",
    "serialize_terminal_market_context_snapshot",

    # Integrity
    "validate_terminal_market_context_integrity",
    "validate_terminal_market_context_snapshot_integrity",
    "validate_terminal_market_context_presentation_integrity",
    "validate_terminal_market_context_result_integrity",
    "validate_terminal_market_context_service_result_integrity",

    # Summary
    "build_terminal_market_context_summary",
]