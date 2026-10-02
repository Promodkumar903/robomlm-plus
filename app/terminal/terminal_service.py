# ============================================================
# ROBOMLM_PLUS
# app/terminal/terminal_service.py
# PART 1 — FOUNDATION / CONTRACTS / AUTHORITY
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


# ============================================================
# ENGINE IDENTITY
# ============================================================

TERMINAL_SERVICE_ENGINE = "ROBOMLM_TERMINAL_SERVICE"
TERMINAL_SERVICE_VERSION = "1.0"


# ============================================================
# ENUMS
# ============================================================

class TerminalServiceStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    READY = "READY"
    PARTIAL = "PARTIAL"
    STALE = "STALE"
    INVALID = "INVALID"
    ERROR = "ERROR"


class TerminalServiceMode(str, Enum):
    PAPER = "PAPER"
    DEMO = "DEMO"
    LIVE = "LIVE"
    UNKNOWN = "UNKNOWN"


class TerminalServicePriority(str, Enum):
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TerminalServiceSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TerminalServiceContractStatus(str, Enum):
    CREATED = "CREATED"
    VALID = "VALID"
    INVALID = "INVALID"
    READY = "READY"


class TerminalServiceDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    INVALID = "INVALID"


class TerminalServiceConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONDITIONAL = "CONDITIONAL"
    INCONSISTENT = "INCONSISTENT"
    UNKNOWN = "UNKNOWN"


class TerminalServiceReadiness(str, Enum):
    READY = "READY"
    CONDITIONALLY_READY = "CONDITIONALLY_READY"
    NOT_READY = "NOT_READY"
    BLOCKED = "BLOCKED"


class TerminalServiceDecision(str, Enum):
    ALLOW = "ALLOW"
    ALLOW_WITH_RESTRICTION = "ALLOW_WITH_RESTRICTION"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


class TerminalServiceResolutionStatus(str, Enum):
    RESOLVED = "RESOLVED"
    CONDITIONAL = "CONDITIONAL"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"


# ============================================================
# HELPERS
# ============================================================

def _ts_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def _ts_enum(
    value: Any,
    enum_type: Any,
    default: Any,
) -> Any:
    if isinstance(value, enum_type):
        return value

    text = _ts_text(value).upper()

    if not text:
        return default

    try:
        return enum_type(text)
    except (ValueError, TypeError):
        return default


def _ts_number(
    value: Any,
    default: float = 0.0,
) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _ts_timestamp(value: Any = None) -> datetime:
    if isinstance(value, datetime):
        return value

    if value:
        try:
            return datetime.fromisoformat(str(value))
        except (TypeError, ValueError):
            pass

    return datetime.utcnow()


# ============================================================
# AUTHORITY CONTRACT
# ============================================================

TERMINAL_SERVICE_AUTHORITY: Dict[str, bool] = {
    # Own authority
    "presentation_orchestration_authority": True,
    "terminal_aggregation_authority": True,
    "terminal_resolution_authority": True,

    # Forbidden intelligence authority
    "market_data_authority": False,
    "evidence_generation_authority": False,
    "intelligence_generation_authority": False,
    "market_context_generation_authority": False,

    # Decision authority
    "decision_generation_authority": False,
    "d13_authority": False,
    "d13_mutation": False,

    # Risk authority
    "risk_generation_authority": False,
    "risk_override": False,

    # CAS authority
    "cas_generation_authority": False,
    "cas_override": False,

    # Execution authority
    "execution_authority": False,
    "order_authority": False,
    "position_authority": False,

    # Upstream mutation
    "upstream_mutation_authority": False,
}


# ============================================================
# TERMINAL SERVICE REQUEST
# ============================================================

@dataclass
class TerminalServiceRequest:
    request_id: str = ""
    market: str = ""
    instrument: str = ""
    symbol: str = ""
    contract: str = ""
    timeframe: str = ""

    mode: TerminalServiceMode = TerminalServiceMode.UNKNOWN
    priority: TerminalServicePriority = TerminalServicePriority.NORMAL

    include_market_context: bool = True
    include_evidence_strip: bool = True
    include_intelligence_panel: bool = True
    include_decision_outlook: bool = True
    include_risk_panel: bool = True
    include_cas_status: bool = True

    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# TERMINAL COMPONENT REFERENCE
# ============================================================

@dataclass
class TerminalComponentReference:
    market_context_source: str = "app.terminal.market_context"
    evidence_strip_source: str = "app.terminal.evidence_strip"
    intelligence_panel_source: str = "app.terminal.intelligence_panel"
    decision_outlook_source: str = "app.terminal.decision_outlook"
    risk_panel_source: str = "app.terminal.risk_panel"
    cas_status_source: str = "app.terminal.cas_status"

    market_data_source: str = "market_data"
    evidence_source: str = "app.intelligence.evidence"
    intelligence_source: str = "app.intelligence"
    market_context_upstream: str = "app.intelligence.market_context"
    decision_source: str = "app.intelligence.decision"
    d13_source: str = "app.intelligence.decision.d13"
    risk_source: str = "app.intelligence.risk"
    cas_source: str = "app.cas"
    memory_source: str = "app.intelligence.memory"

    as_of: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# SERVICE CONTRACT VALIDATION
# ============================================================

@dataclass
class TerminalServiceContractValidation:
    status: TerminalServiceContractStatus = (
        TerminalServiceContractStatus.CREATED
    )
    valid: bool = False

    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    checked_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_terminal_service_request(
    request: TerminalServiceRequest,
) -> TerminalServiceRequest:
    if not isinstance(request, TerminalServiceRequest):
        raise TypeError(
            "request must be TerminalServiceRequest"
        )

    request.request_id = _ts_text(request.request_id)
    request.market = _ts_text(request.market).upper()
    request.instrument = _ts_text(request.instrument).upper()
    request.symbol = _ts_text(request.symbol).upper()
    request.contract = _ts_text(request.contract).upper()
    request.timeframe = _ts_text(request.timeframe).upper()

    request.mode = _ts_enum(
        request.mode,
        TerminalServiceMode,
        TerminalServiceMode.UNKNOWN,
    )

    request.priority = _ts_enum(
        request.priority,
        TerminalServicePriority,
        TerminalServicePriority.NORMAL,
    )

    request.created_at = _ts_timestamp(request.created_at)

    if not isinstance(request.metadata, dict):
        request.metadata = {}

    return request


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_terminal_service_request(
    request: TerminalServiceRequest,
) -> TerminalServiceContractValidation:
    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(request, TerminalServiceRequest):
        return TerminalServiceContractValidation(
            status=TerminalServiceContractStatus.INVALID,
            valid=False,
            errors=["request must be TerminalServiceRequest"],
        )

    if not request.market:
        errors.append("market is required")

    if not request.instrument:
        errors.append("instrument is required")

    if not request.symbol:
        errors.append("symbol is required")

    if not request.request_id:
        warnings.append(
            "request_id is empty; traceability is degraded"
        )

    if request.mode == TerminalServiceMode.UNKNOWN:
        warnings.append("mode is UNKNOWN")

    valid = len(errors) == 0

    return TerminalServiceContractValidation(
        status=(
            TerminalServiceContractStatus.VALID
            if valid
            else TerminalServiceContractStatus.INVALID
        ),
        valid=valid,
        errors=errors,
        warnings=warnings,
        checked_at=datetime.utcnow(),
    )


# ============================================================
# REQUEST BUILDER
# ============================================================

def build_terminal_service_request(
    *,
    request_id: str = "",
    market: str = "",
    instrument: str = "",
    symbol: str = "",
    contract: str = "",
    timeframe: str = "",
    mode: Any = TerminalServiceMode.UNKNOWN,
    priority: Any = TerminalServicePriority.NORMAL,
    include_market_context: bool = True,
    include_evidence_strip: bool = True,
    include_intelligence_panel: bool = True,
    include_decision_outlook: bool = True,
    include_risk_panel: bool = True,
    include_cas_status: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
) -> TerminalServiceRequest:

    request = TerminalServiceRequest(
        request_id=_ts_text(request_id),
        market=_ts_text(market),
        instrument=_ts_text(instrument),
        symbol=_ts_text(symbol),
        contract=_ts_text(contract),
        timeframe=_ts_text(timeframe),
        mode=_ts_enum(
            mode,
            TerminalServiceMode,
            TerminalServiceMode.UNKNOWN,
        ),
        priority=_ts_enum(
            priority,
            TerminalServicePriority,
            TerminalServicePriority.NORMAL,
        ),
        include_market_context=bool(include_market_context),
        include_evidence_strip=bool(include_evidence_strip),
        include_intelligence_panel=bool(
            include_intelligence_panel
        ),
        include_decision_outlook=bool(
            include_decision_outlook
        ),
        include_risk_panel=bool(include_risk_panel),
        include_cas_status=bool(include_cas_status),
        metadata=dict(metadata or {}),
    )

    return normalize_terminal_service_request(request)


# ============================================================
# COMPONENT REFERENCE BUILDER
# ============================================================

def build_terminal_component_reference(
    *,
    as_of: Optional[datetime] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> TerminalComponentReference:

    return TerminalComponentReference(
        as_of=as_of or datetime.utcnow(),
        metadata=dict(metadata or {}),
    )


# ============================================================
# AUTHORITY VALIDATION
# ============================================================

def validate_terminal_service_authority(
    authority: Optional[Dict[str, Any]] = None,
) -> List[str]:
    errors: List[str] = []

    current = dict(
        TERMINAL_SERVICE_AUTHORITY
        if authority is None
        else authority
    )

    forbidden = [
        "market_data_authority",
        "evidence_generation_authority",
        "intelligence_generation_authority",
        "market_context_generation_authority",
        "decision_generation_authority",
        "d13_authority",
        "d13_mutation",
        "risk_generation_authority",
        "risk_override",
        "cas_generation_authority",
        "cas_override",
        "execution_authority",
        "order_authority",
        "position_authority",
        "upstream_mutation_authority",
    ]

    for key in forbidden:
        if current.get(key) is True:
            errors.append(
                f"forbidden terminal authority enabled: {key}"
            )

    return errors
# ============================================================
# PART 2 — COMPONENT SNAPSHOTS / AGGREGATION ASSESSMENT
# ============================================================

# ============================================================
# COMPONENT SNAPSHOT
# ============================================================

@dataclass
class TerminalComponentSnapshot:
    component_id: str = ""
    component_name: str = ""

    status: TerminalServiceStatus = (
        TerminalServiceStatus.UNKNOWN
    )
    severity: TerminalServiceSeverity = (
        TerminalServiceSeverity.INFO
    )

    data_state: TerminalServiceDataState = (
        TerminalServiceDataState.MISSING
    )
    consistency: TerminalServiceConsistency = (
        TerminalServiceConsistency.UNKNOWN
    )
    readiness: TerminalServiceReadiness = (
        TerminalServiceReadiness.NOT_READY
    )

    decision: TerminalServiceDecision = (
        TerminalServiceDecision.UNKNOWN
    )

    source: str = ""
    message: str = ""

    quality_score: float = 0.0
    freshness_score: float = 0.0
    completeness_score: float = 0.0
    confidence_score: float = 0.0

    restrictions: List[str] = field(default_factory=list)
    flags: List[str] = field(default_factory=list)

    timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# TERMINAL SERVICE REQUIREMENTS
# ============================================================

@dataclass
class TerminalServiceRequirements:
    require_market_context: bool = True
    require_evidence_strip: bool = True
    require_intelligence_panel: bool = True
    require_decision_outlook: bool = True
    require_risk_panel: bool = True
    require_cas_status: bool = True

    minimum_completeness: float = 0.70
    minimum_freshness: float = 0.70
    minimum_confidence: float = 0.70
    minimum_quality: float = 0.70

    require_decision_authority: bool = True
    require_risk_authority: bool = True
    require_cas_authority: bool = True

    metadata: Dict[str, Any] = field(default_factory=dict)


def build_terminal_service_requirements(
    *,
    require_market_context: bool = True,
    require_evidence_strip: bool = True,
    require_intelligence_panel: bool = True,
    require_decision_outlook: bool = True,
    require_risk_panel: bool = True,
    require_cas_status: bool = True,
    minimum_completeness: float = 0.70,
    minimum_freshness: float = 0.70,
    minimum_confidence: float = 0.70,
    minimum_quality: float = 0.70,
    require_decision_authority: bool = True,
    require_risk_authority: bool = True,
    require_cas_authority: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
) -> TerminalServiceRequirements:

    return TerminalServiceRequirements(
        require_market_context=bool(
            require_market_context
        ),
        require_evidence_strip=bool(
            require_evidence_strip
        ),
        require_intelligence_panel=bool(
            require_intelligence_panel
        ),
        require_decision_outlook=bool(
            require_decision_outlook
        ),
        require_risk_panel=bool(require_risk_panel),
        require_cas_status=bool(require_cas_status),
        minimum_completeness=max(
            0.0, min(1.0, float(minimum_completeness))
        ),
        minimum_freshness=max(
            0.0, min(1.0, float(minimum_freshness))
        ),
        minimum_confidence=max(
            0.0, min(1.0, float(minimum_confidence))
        ),
        minimum_quality=max(
            0.0, min(1.0, float(minimum_quality))
        ),
        require_decision_authority=bool(
            require_decision_authority
        ),
        require_risk_authority=bool(
            require_risk_authority
        ),
        require_cas_authority=bool(
            require_cas_authority
        ),
        metadata=dict(metadata or {}),
    )


# ============================================================
# TERMINAL SERVICE ASSESSMENT
# ============================================================

@dataclass
class TerminalServiceAssessment:
    data_state: TerminalServiceDataState = (
        TerminalServiceDataState.MISSING
    )
    consistency: TerminalServiceConsistency = (
        TerminalServiceConsistency.UNKNOWN
    )
    readiness: TerminalServiceReadiness = (
        TerminalServiceReadiness.NOT_READY
    )

    completeness_score: float = 0.0
    freshness_score: float = 0.0
    confidence_score: float = 0.0
    quality_score: float = 0.0

    component_count: int = 0
    ready_components: int = 0
    partial_components: int = 0
    invalid_components: int = 0

    requirements_met: bool = False

    flags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# COMPONENT ORDER
# ============================================================

_TERMINAL_COMPONENT_ORDER = (
    "market_context",
    "evidence_strip",
    "intelligence_panel",
    "decision_outlook",
    "risk_panel",
    "cas_status",
)


def _terminal_component_required(
    requirements: TerminalServiceRequirements,
    component_id: str,
) -> bool:

    mapping = {
        "market_context":
            requirements.require_market_context,
        "evidence_strip":
            requirements.require_evidence_strip,
        "intelligence_panel":
            requirements.require_intelligence_panel,
        "decision_outlook":
            requirements.require_decision_outlook,
        "risk_panel":
            requirements.require_risk_panel,
        "cas_status":
            requirements.require_cas_status,
    }

    return bool(mapping.get(component_id, False))


# ============================================================
# FRESHNESS
# ============================================================

def _terminal_freshness_score(
    timestamp: Optional[datetime],
    now: Optional[datetime] = None,
) -> float:

    if timestamp is None:
        return 0.0

    current = now or datetime.utcnow()

    try:
        age = max(
            0.0,
            (current - timestamp).total_seconds(),
        )
    except (TypeError, ValueError):
        return 0.0

    if age <= 5:
        return 1.0
    if age <= 30:
        return 0.95
    if age <= 60:
        return 0.90
    if age <= 120:
        return 0.80
    if age <= 300:
        return 0.65
    if age <= 600:
        return 0.45
    if age <= 1800:
        return 0.25

    return 0.0


# ============================================================
# COMPONENT VALIDITY
# ============================================================

def _validate_terminal_component(
    component: TerminalComponentSnapshot,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        component,
        TerminalComponentSnapshot,
    ):
        return ["invalid component snapshot"]

    if not component.component_id:
        errors.append("component_id is required")

    if not component.component_name:
        errors.append("component_name is required")

    if not isinstance(
        component.status,
        TerminalServiceStatus,
    ):
        errors.append("invalid component status")

    if not isinstance(
        component.data_state,
        TerminalServiceDataState,
    ):
        errors.append("invalid component data_state")

    if not isinstance(
        component.consistency,
        TerminalServiceConsistency,
    ):
        errors.append("invalid component consistency")

    if not isinstance(
        component.readiness,
        TerminalServiceReadiness,
    ):
        errors.append("invalid component readiness")

    for name, value in (
        ("quality_score", component.quality_score),
        ("freshness_score", component.freshness_score),
        ("completeness_score", component.completeness_score),
        ("confidence_score", component.confidence_score),
    ):
        if not isinstance(value, (int, float)):
            errors.append(f"{name} must be numeric")
        elif value < 0.0 or value > 1.0:
            errors.append(
                f"{name} must be between 0 and 1"
            )

    return errors


# ============================================================
# COMPONENT AGGREGATION
# ============================================================

def aggregate_terminal_components(
    components: List[TerminalComponentSnapshot],
) -> Dict[str, Any]:

    if not isinstance(components, list):
        return {
            "status": TerminalServiceStatus.INVALID,
            "data_state": TerminalServiceDataState.INVALID,
            "consistency": TerminalServiceConsistency.INCONSISTENT,
            "decision": TerminalServiceDecision.BLOCK,
        }

    if not components:
        return {
            "status": TerminalServiceStatus.PARTIAL,
            "data_state": TerminalServiceDataState.MISSING,
            "consistency": TerminalServiceConsistency.UNKNOWN,
            "decision": TerminalServiceDecision.REVIEW_REQUIRED,
        }

    valid_components = [
        item
        for item in components
        if isinstance(item, TerminalComponentSnapshot)
    ]

    if len(valid_components) != len(components):
        return {
            "status": TerminalServiceStatus.INVALID,
            "data_state": TerminalServiceDataState.INVALID,
            "consistency": TerminalServiceConsistency.INCONSISTENT,
            "decision": TerminalServiceDecision.BLOCK,
        }

    status_rank = {
        TerminalServiceStatus.ERROR: 6,
        TerminalServiceStatus.INVALID: 5,
        TerminalServiceStatus.STALE: 4,
        TerminalServiceStatus.PARTIAL: 3,
        TerminalServiceStatus.READY: 2,
        TerminalServiceStatus.UNKNOWN: 1,
    }

    consistency_rank = {
        TerminalServiceConsistency.INCONSISTENT: 4,
        TerminalServiceConsistency.CONDITIONAL: 3,
        TerminalServiceConsistency.UNKNOWN: 2,
        TerminalServiceConsistency.CONSISTENT: 1,
    }

    decision_rank = {
        TerminalServiceDecision.BLOCK: 4,
        TerminalServiceDecision.REVIEW_REQUIRED: 3,
        TerminalServiceDecision.ALLOW_WITH_RESTRICTION: 2,
        TerminalServiceDecision.ALLOW: 1,
        TerminalServiceDecision.UNKNOWN: 0,
    }

    worst_status = max(
        valid_components,
        key=lambda x: status_rank.get(
            x.status,
            0,
        ),
    ).status

    worst_consistency = max(
        valid_components,
        key=lambda x: consistency_rank.get(
            x.consistency,
            0,
        ),
    ).consistency

    worst_decision = max(
        valid_components,
        key=lambda x: decision_rank.get(
            x.decision,
            0,
        ),
    ).decision

    return {
        "status": worst_status,
        "data_state": (
            TerminalServiceDataState.COMPLETE
            if all(
                x.data_state
                == TerminalServiceDataState.COMPLETE
                for x in valid_components
            )
            else TerminalServiceDataState.PARTIAL
        ),
        "consistency": worst_consistency,
        "decision": worst_decision,
    }


# ============================================================
# REQUIREMENT EVALUATION
# ============================================================

def evaluate_terminal_requirements(
    components: List[TerminalComponentSnapshot],
    requirements: TerminalServiceRequirements,
) -> tuple[bool, List[str]]:

    flags: List[str] = []

    by_id = {
        item.component_id.lower(): item
        for item in components
        if isinstance(item, TerminalComponentSnapshot)
    }

    for component_id in _TERMINAL_COMPONENT_ORDER:

        if not _terminal_component_required(
            requirements,
            component_id,
        ):
            continue

        item = by_id.get(component_id)

        if item is None:
            flags.append(
                f"required component missing: {component_id}"
            )
            continue

        if item.data_state in (
            TerminalServiceDataState.MISSING,
            TerminalServiceDataState.INVALID,
        ):
            flags.append(
                f"required component unavailable: {component_id}"
            )

        if item.readiness in (
            TerminalServiceReadiness.NOT_READY,
            TerminalServiceReadiness.BLOCKED,
        ):
            flags.append(
                f"required component not ready: {component_id}"
            )

    if requirements.require_decision_authority:
        decision = by_id.get("decision_outlook")
        if decision is None:
            flags.append(
                "decision outlook authority reference missing"
            )

    if requirements.require_risk_authority:
        risk = by_id.get("risk_panel")
        if risk is None:
            flags.append(
                "risk panel authority reference missing"
            )

    if requirements.require_cas_authority:
        cas = by_id.get("cas_status")
        if cas is None:
            flags.append(
                "CAS status authority reference missing"
            )

    return len(flags) == 0, flags


# ============================================================
# ASSESSMENT
# ============================================================

def assess_terminal_service(
    components: List[TerminalComponentSnapshot],
    requirements: Optional[
        TerminalServiceRequirements
    ] = None,
    *,
    now: Optional[datetime] = None,
) -> TerminalServiceAssessment:

    requirements = (
        requirements
        or TerminalServiceRequirements()
    )

    if not isinstance(components, list):
        return TerminalServiceAssessment(
            data_state=TerminalServiceDataState.INVALID,
            consistency=TerminalServiceConsistency.INCONSISTENT,
            readiness=TerminalServiceReadiness.BLOCKED,
            flags=["components must be a list"],
        )

    if not components:
        return TerminalServiceAssessment(
            data_state=TerminalServiceDataState.MISSING,
            consistency=TerminalServiceConsistency.UNKNOWN,
            readiness=TerminalServiceReadiness.NOT_READY,
            flags=["no terminal components available"],
        )

    invalid_count = 0
    ready_count = 0
    partial_count = 0

    completeness_values: List[float] = []
    freshness_values: List[float] = []
    confidence_values: List[float] = []
    quality_values: List[float] = []

    flags: List[str] = []

    for component in components:

        errors = _validate_terminal_component(component)

        if errors:
            invalid_count += 1
            flags.extend(errors)
            continue

        if component.readiness == (
            TerminalServiceReadiness.READY
        ):
            ready_count += 1

        if component.data_state == (
            TerminalServiceDataState.PARTIAL
        ):
            partial_count += 1

        completeness_values.append(
            float(component.completeness_score)
        )

        confidence_values.append(
            float(component.confidence_score)
        )

        quality_values.append(
            float(component.quality_score)
        )

        freshness_values.append(
            _terminal_freshness_score(
                component.timestamp,
                now=now,
            )
        )

        if component.flags:
            flags.extend(component.flags)

        if component.restrictions:
            flags.extend(
                f"restriction:{item}"
                for item in component.restrictions
            )

    if invalid_count:
        return TerminalServiceAssessment(
            data_state=TerminalServiceDataState.INVALID,
            consistency=TerminalServiceConsistency.INCONSISTENT,
            readiness=TerminalServiceReadiness.BLOCKED,
            component_count=len(components),
            ready_components=ready_count,
            partial_components=partial_count,
            invalid_components=invalid_count,
            flags=flags,
        )

    aggregate = aggregate_terminal_components(
        components
    )

    requirements_met, requirement_flags = (
        evaluate_terminal_requirements(
            components,
            requirements,
        )
    )

    flags.extend(requirement_flags)

    completeness = (
        sum(completeness_values)
        / len(completeness_values)
        if completeness_values
        else 0.0
    )

    freshness = (
        sum(freshness_values)
        / len(freshness_values)
        if freshness_values
        else 0.0
    )

    confidence = (
        sum(confidence_values)
        / len(confidence_values)
        if confidence_values
        else 0.0
    )

    component_quality = (
        sum(quality_values)
        / len(quality_values)
        if quality_values
        else 0.0
    )

    # Terminal service quality is contract/readiness quality,
    # not market alpha or win probability.
    quality = (
        0.30 * completeness
        + 0.25 * freshness
        + 0.25 * confidence
        + 0.20 * component_quality
    )

    consistency = aggregate["consistency"]

    if consistency == (
        TerminalServiceConsistency.INCONSISTENT
    ):
        readiness = TerminalServiceReadiness.BLOCKED
    elif quality < 0.50:
        readiness = TerminalServiceReadiness.NOT_READY
    elif not requirements_met:
        readiness = (
            TerminalServiceReadiness.CONDITIONALLY_READY
            if quality >= requirements.minimum_quality
            else TerminalServiceReadiness.NOT_READY
        )
    elif (
        completeness < requirements.minimum_completeness
        or freshness < requirements.minimum_freshness
        or confidence < requirements.minimum_confidence
        or quality < requirements.minimum_quality
        or consistency
        == TerminalServiceConsistency.CONDITIONAL
        or partial_count > 0
    ):
        readiness = (
            TerminalServiceReadiness.CONDITIONALLY_READY
        )
    else:
        readiness = TerminalServiceReadiness.READY

    data_state = aggregate["data_state"]

    if data_state == TerminalServiceDataState.COMPLETE:
        final_data_state = data_state
    elif data_state == TerminalServiceDataState.PARTIAL:
        final_data_state = data_state
    else:
        final_data_state = TerminalServiceDataState.MISSING

    return TerminalServiceAssessment(
        data_state=final_data_state,
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
        component_count=len(components),
        ready_components=ready_count,
        partial_components=partial_count,
        invalid_components=invalid_count,
        requirements_met=requirements_met,
        flags=flags,
        metadata={
            "assessment_only": True,
            "intelligence_generation": False,
            "decision_generation": False,
            "d13_mutation": False,
            "risk_generation": False,
            "risk_override": False,
            "cas_generation": False,
            "cas_override": False,
            "execution": False,
            "upstream_authority_preserved": True,
        },
    )
# ============================================================
# PART 3 — RESOLUTION / PRESENTATION / RESULT / SOURCE MAP
# ============================================================

# ============================================================
# RESOLUTION RULES
# ============================================================

@dataclass
class TerminalServiceResolutionRules:
    allow_when_ready: bool = True
    allow_when_conditionally_ready: bool = True
    review_when_not_ready: bool = True

    block_when_invalid: bool = True
    block_when_inconsistent: bool = True
    block_when_authority_violation: bool = True

    require_market_context: bool = True
    require_decision_outlook: bool = True
    require_risk_panel: bool = True
    require_cas_status: bool = True

    metadata: Dict[str, Any] = field(default_factory=dict)


def build_terminal_service_resolution_rules(
    *,
    allow_when_ready: bool = True,
    allow_when_conditionally_ready: bool = True,
    review_when_not_ready: bool = True,
    block_when_invalid: bool = True,
    block_when_inconsistent: bool = True,
    block_when_authority_violation: bool = True,
    require_market_context: bool = True,
    require_decision_outlook: bool = True,
    require_risk_panel: bool = True,
    require_cas_status: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
) -> TerminalServiceResolutionRules:

    return TerminalServiceResolutionRules(
        allow_when_ready=bool(allow_when_ready),
        allow_when_conditionally_ready=bool(
            allow_when_conditionally_ready
        ),
        review_when_not_ready=bool(
            review_when_not_ready
        ),
        block_when_invalid=bool(block_when_invalid),
        block_when_inconsistent=bool(
            block_when_inconsistent
        ),
        block_when_authority_violation=bool(
            block_when_authority_violation
        ),
        require_market_context=bool(
            require_market_context
        ),
        require_decision_outlook=bool(
            require_decision_outlook
        ),
        require_risk_panel=bool(require_risk_panel),
        require_cas_status=bool(require_cas_status),
        metadata=dict(metadata or {}),
    )


# ============================================================
# TERMINAL PRESENTATION
# ============================================================

@dataclass
class TerminalServicePresentation:
    title: str = "ROBOMLM Terminal"

    status: TerminalServiceStatus = (
        TerminalServiceStatus.UNKNOWN
    )

    overall_decision: TerminalServiceDecision = (
        TerminalServiceDecision.UNKNOWN
    )

    readiness: TerminalServiceReadiness = (
        TerminalServiceReadiness.NOT_READY
    )

    market_context: Optional[
        TerminalComponentSnapshot
    ] = None

    evidence_strip: Optional[
        TerminalComponentSnapshot
    ] = None

    intelligence_panel: Optional[
        TerminalComponentSnapshot
    ] = None

    decision_outlook: Optional[
        TerminalComponentSnapshot
    ] = None

    risk_panel: Optional[
        TerminalComponentSnapshot
    ] = None

    cas_status: Optional[
        TerminalComponentSnapshot
    ] = None

    restrictions: List[str] = field(default_factory=list)
    flags: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# SERVICE RESULT
# ============================================================

@dataclass
class TerminalServiceResult:
    request: TerminalServiceRequest
    reference: TerminalComponentReference
    assessment: TerminalServiceAssessment
    presentation: TerminalServicePresentation

    decision: TerminalServiceDecision = (
        TerminalServiceDecision.UNKNOWN
    )

    resolution: TerminalServiceResolutionStatus = (
        TerminalServiceResolutionStatus.BLOCKED
    )

    restrictions: List[str] = field(default_factory=list)
    flags: List[str] = field(default_factory=list)

    authority_valid: bool = True

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# SOURCE MAP
# ============================================================

@dataclass
class TerminalServiceSourceMap:
    terminal_service: str = TERMINAL_SERVICE_ENGINE

    market_context: str = (
        "app.terminal.market_context"
    )
    evidence_strip: str = (
        "app.terminal.evidence_strip"
    )
    intelligence_panel: str = (
        "app.terminal.intelligence_panel"
    )
    decision_outlook: str = (
        "app.terminal.decision_outlook"
    )
    risk_panel: str = (
        "app.terminal.risk_panel"
    )
    cas_status: str = (
        "app.terminal.cas_status"
    )

    market_data: str = "market_data"
    evidence: str = "app.intelligence.evidence"
    intelligence: str = "app.intelligence"
    market_context_upstream: str = (
        "app.intelligence.market_context"
    )
    decision: str = "app.intelligence.decision"
    d13: str = (
        "app.intelligence.decision.d13"
    )
    risk: str = "app.intelligence.risk"
    cas: str = "app.cas"
    memory: str = "app.intelligence.memory"

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# COMPONENT MAP
# ============================================================

def _terminal_component_map(
    components: List[TerminalComponentSnapshot],
) -> Dict[str, TerminalComponentSnapshot]:

    return {
        item.component_id.lower(): item
        for item in components
        if isinstance(
            item,
            TerminalComponentSnapshot,
        )
    }


# ============================================================
# RESTRICTION COLLECTION
# ============================================================

def _collect_terminal_restrictions(
    components: List[TerminalComponentSnapshot],
    assessment: TerminalServiceAssessment,
) -> List[str]:

    restrictions: List[str] = []

    for item in components:
        if not isinstance(
            item,
            TerminalComponentSnapshot,
        ):
            continue

        for restriction in item.restrictions:
            text = _ts_text(restriction)
            if text and text not in restrictions:
                restrictions.append(text)

        if item.decision == (
            TerminalServiceDecision.ALLOW_WITH_RESTRICTION
        ):
            marker = (
                f"{item.component_id}:"
                "allow_with_restriction"
            )
            if marker not in restrictions:
                restrictions.append(marker)

        if item.readiness == (
            TerminalServiceReadiness.CONDITIONALLY_READY
        ):
            marker = (
                f"{item.component_id}:"
                "conditional_readiness"
            )
            if marker not in restrictions:
                restrictions.append(marker)

    if assessment.readiness == (
        TerminalServiceReadiness.CONDITIONALLY_READY
    ):
        marker = "terminal:conditional_readiness"
        if marker not in restrictions:
            restrictions.append(marker)

    return restrictions


# ============================================================
# FLAG COLLECTION
# ============================================================

def _collect_terminal_flags(
    components: List[TerminalComponentSnapshot],
    assessment: TerminalServiceAssessment,
) -> List[str]:

    flags: List[str] = list(assessment.flags)

    for item in components:
        if not isinstance(
            item,
            TerminalComponentSnapshot,
        ):
            continue

        for flag in item.flags:
            text = _ts_text(flag)
            if text and text not in flags:
                flags.append(text)

    return flags


# ============================================================
# PRESENTATION BUILDER
# ============================================================

def build_terminal_service_presentation(
    request: TerminalServiceRequest,
    components: List[TerminalComponentSnapshot],
    assessment: TerminalServiceAssessment,
    decision: TerminalServiceDecision,
    resolution: TerminalServiceResolutionStatus,
    restrictions: Optional[List[str]] = None,
    flags: Optional[List[str]] = None,
) -> TerminalServicePresentation:

    component_map = _terminal_component_map(
        components
    )

    if assessment.data_state == (
        TerminalServiceDataState.INVALID
    ):
        status = TerminalServiceStatus.INVALID

    elif assessment.readiness == (
        TerminalServiceReadiness.BLOCKED
    ):
        status = TerminalServiceStatus.ERROR

    elif assessment.readiness == (
        TerminalServiceReadiness.NOT_READY
    ):
        status = TerminalServiceStatus.STALE

    elif assessment.readiness == (
        TerminalServiceReadiness.CONDITIONALLY_READY
    ):
        status = TerminalServiceStatus.PARTIAL

    elif assessment.data_state == (
        TerminalServiceDataState.PARTIAL
    ):
        status = TerminalServiceStatus.PARTIAL

    else:
        status = TerminalServiceStatus.READY

    return TerminalServicePresentation(
        title=(
            f"ROBOMLM Terminal — "
            f"{request.market} "
            f"{request.symbol}"
        ).strip(),

        status=status,
        overall_decision=decision,
        readiness=assessment.readiness,

        market_context=component_map.get(
            "market_context"
        ),
        evidence_strip=component_map.get(
            "evidence_strip"
        ),
        intelligence_panel=component_map.get(
            "intelligence_panel"
        ),
        decision_outlook=component_map.get(
            "decision_outlook"
        ),
        risk_panel=component_map.get(
            "risk_panel"
        ),
        cas_status=component_map.get(
            "cas_status"
        ),

        restrictions=list(
            restrictions or []
        ),
        flags=list(flags or []),

        metadata={
            "presentation_only": True,
            "market_data_generation": False,
            "evidence_generation": False,
            "intelligence_generation": False,
            "decision_generation": False,
            "d13_mutation": False,
            "risk_generation": False,
            "risk_override": False,
            "cas_generation": False,
            "cas_override": False,
            "execution": False,
            "upstream_mutation": False,
        },
    )


# ============================================================
# RESOLUTION
# ============================================================

def resolve_terminal_service(
    request: TerminalServiceRequest,
    components: List[TerminalComponentSnapshot],
    *,
    requirements: Optional[
        TerminalServiceRequirements
    ] = None,
    rules: Optional[
        TerminalServiceResolutionRules
    ] = None,
    reference: Optional[
        TerminalComponentReference
    ] = None,
    now: Optional[datetime] = None,
) -> TerminalServiceResult:

    requirements = (
        requirements
        or TerminalServiceRequirements()
    )

    rules = (
        rules
        or TerminalServiceResolutionRules()
    )

    reference = (
        reference
        or build_terminal_component_reference()
    )

    authority_errors = validate_terminal_service_authority()

    authority_valid = len(authority_errors) == 0

    assessment = assess_terminal_service(
        components,
        requirements,
        now=now,
    )

    flags = _collect_terminal_flags(
        components,
        assessment,
    )

    flags.extend(authority_errors)

    restrictions = _collect_terminal_restrictions(
        components,
        assessment,
    )

    # --------------------------------------------------------
    # Resolution hierarchy
    # --------------------------------------------------------

    if (
        not authority_valid
        and rules.block_when_authority_violation
    ):
        decision = TerminalServiceDecision.BLOCK
        resolution = TerminalServiceResolutionStatus.BLOCKED
        flags.append("terminal_authority_violation")

    elif (
        assessment.data_state
        == TerminalServiceDataState.INVALID
        and rules.block_when_invalid
    ):
        decision = TerminalServiceDecision.BLOCK
        resolution = TerminalServiceResolutionStatus.BLOCKED
        flags.append("terminal_data_invalid")

    elif (
        assessment.consistency
        == TerminalServiceConsistency.INCONSISTENT
        and rules.block_when_inconsistent
    ):
        decision = TerminalServiceDecision.BLOCK
        resolution = TerminalServiceResolutionStatus.BLOCKED
        flags.append("terminal_components_inconsistent")

    elif assessment.readiness == (
        TerminalServiceReadiness.BLOCKED
    ):
        decision = TerminalServiceDecision.BLOCK
        resolution = TerminalServiceResolutionStatus.BLOCKED

    elif assessment.readiness == (
        TerminalServiceReadiness.NOT_READY
    ):
        if rules.review_when_not_ready:
            decision = TerminalServiceDecision.REVIEW_REQUIRED
            resolution = (
                TerminalServiceResolutionStatus.REVIEW_REQUIRED
            )
        else:
            decision = TerminalServiceDecision.BLOCK
            resolution = TerminalServiceResolutionStatus.BLOCKED

    elif assessment.readiness == (
        TerminalServiceReadiness.CONDITIONALLY_READY
    ):
        if rules.allow_when_conditionally_ready:
            decision = (
                TerminalServiceDecision.ALLOW_WITH_RESTRICTION
            )
            resolution = (
                TerminalServiceResolutionStatus.CONDITIONAL
            )
        else:
            decision = TerminalServiceDecision.REVIEW_REQUIRED
            resolution = (
                TerminalServiceResolutionStatus.REVIEW_REQUIRED
            )

    else:
        if rules.allow_when_ready:
            decision = TerminalServiceDecision.ALLOW
            resolution = (
                TerminalServiceResolutionStatus.RESOLVED
            )
        else:
            decision = TerminalServiceDecision.REVIEW_REQUIRED
            resolution = (
                TerminalServiceResolutionStatus.REVIEW_REQUIRED
            )

    presentation = build_terminal_service_presentation(
        request=request,
        components=components,
        assessment=assessment,
        decision=decision,
        resolution=resolution,
        restrictions=restrictions,
        flags=flags,
    )

    result = TerminalServiceResult(
        request=request,
        reference=reference,
        assessment=assessment,
        presentation=presentation,
        decision=decision,
        resolution=resolution,
        restrictions=restrictions,
        flags=flags,
        authority_valid=authority_valid,
        metadata={
            "terminal_service": TERMINAL_SERVICE_ENGINE,
            "version": TERMINAL_SERVICE_VERSION,

            # Explicit authority boundary
            "market_data_generation": False,
            "evidence_generation": False,
            "intelligence_generation": False,
            "decision_generation": False,
            "d13_mutation": False,
            "risk_generation": False,
            "risk_override": False,
            "cas_generation": False,
            "cas_override": False,
            "execution": False,
            "order_authority": False,
            "position_authority": False,
            "upstream_mutation": False,

            "upstream_authority_preserved": True,
        },
    )

    return result


# ============================================================
# RESULT VALIDATION
# ============================================================

def validate_terminal_service_result(
    result: TerminalServiceResult,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        result,
        TerminalServiceResult,
    ):
        return ["result must be TerminalServiceResult"]

    if not isinstance(
        result.request,
        TerminalServiceRequest,
    ):
        errors.append(
            "invalid terminal service request"
        )

    if not isinstance(
        result.reference,
        TerminalComponentReference,
    ):
        errors.append(
            "invalid terminal component reference"
        )

    if not isinstance(
        result.assessment,
        TerminalServiceAssessment,
    ):
        errors.append(
            "invalid terminal service assessment"
        )

    if not isinstance(
        result.presentation,
        TerminalServicePresentation,
    ):
        errors.append(
            "invalid terminal service presentation"
        )

    if not isinstance(
        result.decision,
        TerminalServiceDecision,
    ):
        errors.append("invalid terminal decision")

    if not isinstance(
        result.resolution,
        TerminalServiceResolutionStatus,
    ):
        errors.append(
            "invalid terminal resolution"
        )

    errors.extend(
        validate_terminal_service_authority()
    )

    forbidden = (
        "d13_mutation",
        "risk_override",
        "cas_override",
        "execution",
        "order_authority",
        "position_authority",
        "upstream_mutation",
        "intelligence_generation",
        "decision_generation",
    )

    for key in forbidden:
        if result.metadata.get(key) is True:
            errors.append(
                f"forbidden terminal authority: {key}"
            )

    return errors


# ============================================================
# SOURCE MAP BUILDER
# ============================================================

def build_terminal_service_source_map(
    *,
    metadata: Optional[Dict[str, Any]] = None,
) -> TerminalServiceSourceMap:

    return TerminalServiceSourceMap(
        metadata=dict(metadata or {})
    )
# ============================================================
# PART 4 — REGISTRY / SERVICE / OPERATIONAL HELPERS
# ============================================================

# ============================================================
# REGISTRY CONTRACTS
# ============================================================

@dataclass
class TerminalServiceRegistryEntry:
    key: str
    reference: TerminalComponentReference

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )
    updated_at: datetime = field(
        default_factory=datetime.utcnow
    )

    active: bool = True
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class TerminalServiceRegistrySnapshot:
    engine: str = TERMINAL_SERVICE_ENGINE
    version: str = TERMINAL_SERVICE_VERSION

    entries: List[TerminalServiceRegistryEntry] = field(
        default_factory=list
    )

    count: int = 0
    captured_at: datetime = field(
        default_factory=datetime.utcnow
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class TerminalServiceExecutionResult:
    request_id: str = ""

    reference: Optional[
        TerminalComponentReference
    ] = None

    assessment: Optional[
        TerminalServiceAssessment
    ] = None

    result: Optional[
        TerminalServiceResult
    ] = None

    success: bool = False

    errors: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# REGISTRY KEY
# ============================================================

def _terminal_service_registry_key(
    reference: TerminalComponentReference,
    *,
    market: str = "",
    instrument: str = "",
    symbol: str = "",
    contract: str = "",
    timeframe: str = "",
) -> str:

    parts = (
        market,
        instrument,
        symbol,
        contract,
        timeframe,
    )

    normalized = [
        _ts_text(value).upper() or "-"
        for value in parts
    ]

    return ":".join(normalized)


# ============================================================
# REGISTRY
# ============================================================

class TerminalServiceRegistry:

    def __init__(self) -> None:
        self._entries: Dict[
            str,
            TerminalServiceRegistryEntry,
        ] = {}

    def exists(self, key: str) -> bool:
        return _ts_text(key).upper() in self._entries

    def get(
        self,
        key: str,
    ) -> Optional[TerminalComponentReference]:

        entry = self._entries.get(
            _ts_text(key).upper()
        )

        return (
            entry.reference
            if entry is not None
            else None
        )

    def get_entry(
        self,
        key: str,
    ) -> Optional[TerminalServiceRegistryEntry]:

        return self._entries.get(
            _ts_text(key).upper()
        )

    def add(
        self,
        key: str,
        reference: TerminalComponentReference,
        *,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TerminalServiceRegistryEntry:

        normalized_key = _ts_text(key).upper()

        if not normalized_key:
            raise ValueError(
                "registry key is required"
            )

        if normalized_key in self._entries:
            raise ValueError(
                f"terminal service registry entry "
                f"already exists: {normalized_key}"
            )

        if not isinstance(
            reference,
            TerminalComponentReference,
        ):
            raise TypeError(
                "reference must be "
                "TerminalComponentReference"
            )

        now = datetime.utcnow()

        entry = TerminalServiceRegistryEntry(
            key=normalized_key,
            reference=reference,
            created_at=now,
            updated_at=now,
            metadata=dict(metadata or {}),
        )

        self._entries[normalized_key] = entry
        return entry

    def replace(
        self,
        key: str,
        reference: TerminalComponentReference,
        *,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TerminalServiceRegistryEntry:

        normalized_key = _ts_text(key).upper()

        if not normalized_key:
            raise ValueError(
                "registry key is required"
            )

        existing = self._entries.get(
            normalized_key
        )

        now = datetime.utcnow()

        entry = TerminalServiceRegistryEntry(
            key=normalized_key,
            reference=reference,
            created_at=(
                existing.created_at
                if existing
                else now
            ),
            updated_at=now,
            active=True,
            metadata=dict(
                metadata
                if metadata is not None
                else (
                    existing.metadata
                    if existing
                    else {}
                )
            ),
        )

        self._entries[normalized_key] = entry
        return entry

    def remove(self, key: str) -> bool:
        normalized_key = _ts_text(key).upper()

        if normalized_key not in self._entries:
            return False

        del self._entries[normalized_key]
        return True

    def list_references(
        self,
    ) -> List[TerminalComponentReference]:

        return [
            entry.reference
            for entry in self._entries.values()
            if entry.active
        ]

    def snapshot(
        self,
    ) -> TerminalServiceRegistrySnapshot:

        entries = list(
            self._entries.values()
        )

        return TerminalServiceRegistrySnapshot(
            entries=entries,
            count=len(entries),
            captured_at=datetime.utcnow(),
        )

    def count(self) -> int:
        return len(self._entries)


# ============================================================
# REGISTRY VALIDATION
# ============================================================

def validate_terminal_service_registry(
    registry: TerminalServiceRegistry,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        registry,
        TerminalServiceRegistry,
    ):
        return ["registry must be TerminalServiceRegistry"]

    for key, entry in registry._entries.items():

        if not key:
            errors.append(
                "registry contains empty key"
            )

        if not isinstance(
            entry,
            TerminalServiceRegistryEntry,
        ):
            errors.append(
                f"invalid registry entry: {key}"
            )
            continue

        if entry.key != key:
            errors.append(
                f"registry key mismatch: {key}"
            )

        if not isinstance(
            entry.reference,
            TerminalComponentReference,
        ):
            errors.append(
                f"invalid reference: {key}"
            )

    return errors


def terminal_service_registry_health(
    registry: TerminalServiceRegistry,
) -> Dict[str, Any]:

    errors = validate_terminal_service_registry(
        registry
    )

    return {
        "engine": TERMINAL_SERVICE_ENGINE,
        "version": TERMINAL_SERVICE_VERSION,
        "healthy": len(errors) == 0,
        "count": registry.count()
        if isinstance(
            registry,
            TerminalServiceRegistry,
        )
        else 0,
        "errors": errors,
    }


# ============================================================
# TERMINAL SERVICE
# ============================================================

class TerminalService:

    def __init__(
        self,
        registry: Optional[
            TerminalServiceRegistry
        ] = None,
    ) -> None:

        self.registry = (
            registry
            or TerminalServiceRegistry()
        )

    # --------------------------------------------------------
    # RESOLVE
    # --------------------------------------------------------

    def resolve(
        self,
        request: TerminalServiceRequest,
        components: List[TerminalComponentSnapshot],
        *,
        requirements: Optional[
            TerminalServiceRequirements
        ] = None,
        rules: Optional[
            TerminalServiceResolutionRules
        ] = None,
        reference: Optional[
            TerminalComponentReference
        ] = None,
        now: Optional[datetime] = None,
    ) -> TerminalServiceResult:

        request = normalize_terminal_service_request(
            request
        )

        validation = validate_terminal_service_request(
            request
        )

        if not validation.valid:
            fallback_reference = (
                reference
                or build_terminal_component_reference()
            )

            empty_assessment = assess_terminal_service(
                [],
                requirements,
                now=now,
            )

            presentation = (
                build_terminal_service_presentation(
                    request=request,
                    components=[],
                    assessment=empty_assessment,
                    decision=(
                        TerminalServiceDecision.BLOCK
                    ),
                    resolution=(
                        TerminalServiceResolutionStatus
                        .BLOCKED
                    ),
                    restrictions=[],
                    flags=validation.errors,
                )
            )

            return TerminalServiceResult(
                request=request,
                reference=fallback_reference,
                assessment=empty_assessment,
                presentation=presentation,
                decision=(
                    TerminalServiceDecision.BLOCK
                ),
                resolution=(
                    TerminalServiceResolutionStatus
                    .BLOCKED
                ),
                restrictions=[],
                flags=list(validation.errors),
                authority_valid=True,
                metadata={
                    "contract_invalid": True,
                    "upstream_authority_preserved": True,
                    "execution": False,
                    "d13_mutation": False,
                    "risk_override": False,
                    "cas_override": False,
                },
            )

        return resolve_terminal_service(
            request=request,
            components=components,
            requirements=requirements,
            rules=rules,
            reference=reference,
            now=now,
        )

    # --------------------------------------------------------
    # ASSESS
    # --------------------------------------------------------

    def assess(
        self,
        components: List[TerminalComponentSnapshot],
        requirements: Optional[
            TerminalServiceRequirements
        ] = None,
        *,
        now: Optional[datetime] = None,
    ) -> TerminalServiceAssessment:

        return assess_terminal_service(
            components,
            requirements,
            now=now,
        )

    # --------------------------------------------------------
    # REGISTER
    # --------------------------------------------------------

    def register(
        self,
        request: TerminalServiceRequest,
        reference: Optional[
            TerminalComponentReference
        ] = None,
    ) -> TerminalServiceRegistryEntry:

        request = normalize_terminal_service_request(
            request
        )

        reference = (
            reference
            or build_terminal_component_reference()
        )

        key = _terminal_service_registry_key(
            reference,
            market=request.market,
            instrument=request.instrument,
            symbol=request.symbol,
            contract=request.contract,
            timeframe=request.timeframe,
        )

        return self.registry.replace(
            key,
            reference,
        )

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    def get(
        self,
        *,
        market: str = "",
        instrument: str = "",
        symbol: str = "",
        contract: str = "",
        timeframe: str = "",
    ) -> Optional[TerminalComponentReference]:

        reference = build_terminal_component_reference()

        key = _terminal_service_registry_key(
            reference,
            market=market,
            instrument=instrument,
            symbol=symbol,
            contract=contract,
            timeframe=timeframe,
        )

        return self.registry.get(key)

    # --------------------------------------------------------
    # LIST
    # --------------------------------------------------------

    def list_references(
        self,
    ) -> List[TerminalComponentReference]:

        return self.registry.list_references()

    # --------------------------------------------------------
    # SNAPSHOT
    # --------------------------------------------------------

    def snapshot(
        self,
    ) -> TerminalServiceRegistrySnapshot:

        return self.registry.snapshot()

    # --------------------------------------------------------
    # HEALTH
    # --------------------------------------------------------

    def health(self) -> Dict[str, Any]:
        return terminal_service_registry_health(
            self.registry
        )

    # --------------------------------------------------------
    # INTEGRITY
    # --------------------------------------------------------

    def integrity(self) -> List[str]:
        return validate_terminal_service_registry(
            self.registry
        )

    # --------------------------------------------------------
    # INFO
    # --------------------------------------------------------

    def info(self) -> Dict[str, Any]:
        return {
            "engine": TERMINAL_SERVICE_ENGINE,
            "version": TERMINAL_SERVICE_VERSION,
            "registry_count": self.registry.count(),
            "authority": dict(
                TERMINAL_SERVICE_AUTHORITY
            ),
            "upstream_authority_preserved": True,
        }


# ============================================================
# SINGLETON
# ============================================================

_TERMINAL_SERVICE = TerminalService()


# ============================================================
# PUBLIC SERVICE HELPERS
# ============================================================

def get_terminal_service() -> TerminalService:
    return _TERMINAL_SERVICE


def resolve_terminal(
    request: TerminalServiceRequest,
    components: List[TerminalComponentSnapshot],
    *,
    requirements: Optional[
        TerminalServiceRequirements
    ] = None,
    rules: Optional[
        TerminalServiceResolutionRules
    ] = None,
    reference: Optional[
        TerminalComponentReference
    ] = None,
    now: Optional[datetime] = None,
) -> TerminalServiceResult:

    return _TERMINAL_SERVICE.resolve(
        request=request,
        components=components,
        requirements=requirements,
        rules=rules,
        reference=reference,
        now=now,
    )


def get_terminal_reference(
    *,
    market: str = "",
    instrument: str = "",
    symbol: str = "",
    contract: str = "",
    timeframe: str = "",
) -> Optional[TerminalComponentReference]:

    return _TERMINAL_SERVICE.get(
        market=market,
        instrument=instrument,
        symbol=symbol,
        contract=contract,
        timeframe=timeframe,
    )


def terminal_service_snapshot(
) -> TerminalServiceRegistrySnapshot:

    return _TERMINAL_SERVICE.snapshot()


def terminal_service_count() -> int:
    return _TERMINAL_SERVICE.registry.count()


def terminal_service_health() -> Dict[str, Any]:
    return _TERMINAL_SERVICE.health()


def terminal_service_integrity() -> List[str]:
    return _TERMINAL_SERVICE.integrity()


def terminal_service_operational_check() -> Dict[str, Any]:

    authority_errors = (
        validate_terminal_service_authority()
    )

    registry_errors = (
        terminal_service_integrity()
    )

    return {
        "engine": TERMINAL_SERVICE_ENGINE,
        "version": TERMINAL_SERVICE_VERSION,
        "operational": (
            len(authority_errors) == 0
            and len(registry_errors) == 0
        ),
        "authority_valid": (
            len(authority_errors) == 0
        ),
        "registry_valid": (
            len(registry_errors) == 0
        ),
        "authority_errors": authority_errors,
        "registry_errors": registry_errors,
        "execution_authority": False,
        "d13_mutation": False,
        "risk_override": False,
        "cas_override": False,
    }


def terminal_service_info() -> Dict[str, Any]:
    return _TERMINAL_SERVICE.info()
# ============================================================
# PART 5 — SERIALIZATION / INTEGRITY / SUMMARY / EXPORTS
# ============================================================

def _ts_serialize_datetime(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _ts_serialize_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value

    if isinstance(value, datetime):
        return value.isoformat()

    if hasattr(value, "__dataclass_fields__"):
        return {
            key: _ts_serialize_value(val)
            for key, val in value.__dict__.items()
        }

    if isinstance(value, dict):
        return {
            str(key): _ts_serialize_value(val)
            for key, val in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            _ts_serialize_value(item)
            for item in value
        ]

    return value


# ============================================================
# SERIALIZERS
# ============================================================

def serialize_terminal_service_request(
    request: TerminalServiceRequest,
) -> Dict[str, Any]:
    return _ts_serialize_value(request)


def serialize_terminal_component_snapshot(
    snapshot: TerminalComponentSnapshot,
) -> Dict[str, Any]:
    return _ts_serialize_value(snapshot)


def serialize_terminal_component_reference(
    reference: TerminalComponentReference,
) -> Dict[str, Any]:
    return _ts_serialize_value(reference)


def serialize_terminal_service_requirements(
    requirements: TerminalServiceRequirements,
) -> Dict[str, Any]:
    return _ts_serialize_value(requirements)


def serialize_terminal_service_assessment(
    assessment: TerminalServiceAssessment,
) -> Dict[str, Any]:
    return _ts_serialize_value(assessment)


def serialize_terminal_service_resolution_rules(
    rules: TerminalServiceResolutionRules,
) -> Dict[str, Any]:
    return _ts_serialize_value(rules)


def serialize_terminal_service_presentation(
    presentation: TerminalServicePresentation,
) -> Dict[str, Any]:
    return _ts_serialize_value(presentation)


def serialize_terminal_service_result(
    result: TerminalServiceResult,
) -> Dict[str, Any]:
    return _ts_serialize_value(result)


def serialize_terminal_service_source_map(
    source_map: TerminalServiceSourceMap,
) -> Dict[str, Any]:
    return _ts_serialize_value(source_map)


def serialize_terminal_service_registry_snapshot(
    snapshot: TerminalServiceRegistrySnapshot,
) -> Dict[str, Any]:
    return _ts_serialize_value(snapshot)


def serialize_terminal_service_execution_result(
    result: TerminalServiceExecutionResult,
) -> Dict[str, Any]:
    return _ts_serialize_value(result)


# ============================================================
# INTEGRITY — REQUEST
# ============================================================

def validate_terminal_service_request_integrity(
    request: TerminalServiceRequest,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        request,
        TerminalServiceRequest,
    ):
        return [
            "request must be TerminalServiceRequest"
        ]

    validation = validate_terminal_service_request(
        request
    )

    errors.extend(validation.errors)

    if request.mode not in TerminalServiceMode:
        errors.append("invalid request mode")

    if request.priority not in TerminalServicePriority:
        errors.append("invalid request priority")

    return errors


# ============================================================
# INTEGRITY — COMPONENT
# ============================================================

def validate_terminal_component_snapshot_integrity(
    snapshot: TerminalComponentSnapshot,
) -> List[str]:

    return _validate_terminal_component(snapshot)


# ============================================================
# INTEGRITY — REFERENCE
# ============================================================

def validate_terminal_component_reference_integrity(
    reference: TerminalComponentReference,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        reference,
        TerminalComponentReference,
    ):
        return [
            "reference must be "
            "TerminalComponentReference"
        ]

    required_sources = {
        "market_context_source":
            "app.terminal.market_context",
        "evidence_strip_source":
            "app.terminal.evidence_strip",
        "intelligence_panel_source":
            "app.terminal.intelligence_panel",
        "decision_outlook_source":
            "app.terminal.decision_outlook",
        "risk_panel_source":
            "app.terminal.risk_panel",
        "cas_status_source":
            "app.terminal.cas_status",
        "decision_source":
            "app.intelligence.decision",
        "d13_source":
            "app.intelligence.decision.d13",
        "risk_source":
            "app.intelligence.risk",
        "cas_source":
            "app.cas",
    }

    for field_name, expected in required_sources.items():
        if getattr(reference, field_name, None) != expected:
            errors.append(
                f"{field_name} must remain {expected}"
            )

    return errors


# ============================================================
# INTEGRITY — REQUIREMENTS
# ============================================================

def validate_terminal_service_requirements_integrity(
    requirements: TerminalServiceRequirements,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        requirements,
        TerminalServiceRequirements,
    ):
        return [
            "requirements must be "
            "TerminalServiceRequirements"
        ]

    for name in (
        "minimum_completeness",
        "minimum_freshness",
        "minimum_confidence",
        "minimum_quality",
    ):
        value = getattr(requirements, name)

        if not isinstance(value, (int, float)):
            errors.append(
                f"{name} must be numeric"
            )
        elif not 0.0 <= value <= 1.0:
            errors.append(
                f"{name} must be between 0 and 1"
            )

    return errors


# ============================================================
# INTEGRITY — ASSESSMENT
# ============================================================

def validate_terminal_service_assessment_integrity(
    assessment: TerminalServiceAssessment,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        assessment,
        TerminalServiceAssessment,
    ):
        return [
            "assessment must be "
            "TerminalServiceAssessment"
        ]

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
        elif value < 0.0 or value > 1.0:
            errors.append(
                f"{name} must be between 0 and 1"
            )

    for name in (
        "component_count",
        "ready_components",
        "partial_components",
        "invalid_components",
    ):
        value = getattr(assessment, name)

        if not isinstance(value, int):
            errors.append(
                f"{name} must be integer"
            )
        elif value < 0:
            errors.append(
                f"{name} cannot be negative"
            )

    if (
        assessment.ready_components
        + assessment.partial_components
        + assessment.invalid_components
        > assessment.component_count
    ):
        errors.append(
            "component counters exceed component_count"
        )

    forbidden = (
        "intelligence_generation",
        "decision_generation",
        "d13_mutation",
        "risk_generation",
        "risk_override",
        "cas_generation",
        "cas_override",
        "execution",
        "upstream_mutation",
    )

    for key in forbidden:
        if assessment.metadata.get(key) is True:
            errors.append(
                f"assessment cannot enable {key}"
            )

    return errors


# ============================================================
# INTEGRITY — RESOLUTION RULES
# ============================================================

def validate_terminal_service_resolution_rules_integrity(
    rules: TerminalServiceResolutionRules,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        rules,
        TerminalServiceResolutionRules,
    ):
        return [
            "rules must be "
            "TerminalServiceResolutionRules"
        ]

    return errors


# ============================================================
# INTEGRITY — PRESENTATION
# ============================================================

def validate_terminal_service_presentation_integrity(
    presentation: TerminalServicePresentation,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        presentation,
        TerminalServicePresentation,
    ):
        return [
            "presentation must be "
            "TerminalServicePresentation"
        ]

    if not presentation.title:
        errors.append("presentation title is required")

    components = (
        presentation.market_context,
        presentation.evidence_strip,
        presentation.intelligence_panel,
        presentation.decision_outlook,
        presentation.risk_panel,
        presentation.cas_status,
    )

    for component in components:
        if component is not None:
            errors.extend(
                validate_terminal_component_snapshot_integrity(
                    component
                )
            )

    forbidden = (
        "market_data_generation",
        "evidence_generation",
        "intelligence_generation",
        "decision_generation",
        "d13_mutation",
        "risk_generation",
        "risk_override",
        "cas_generation",
        "cas_override",
        "execution",
        "upstream_mutation",
    )

    for key in forbidden:
        if presentation.metadata.get(key) is True:
            errors.append(
                f"presentation cannot enable {key}"
            )

    return errors


# ============================================================
# INTEGRITY — RESULT
# ============================================================

def validate_terminal_service_result_integrity(
    result: TerminalServiceResult,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        result,
        TerminalServiceResult,
    ):
        return [
            "result must be TerminalServiceResult"
        ]

    errors.extend(
        validate_terminal_service_request_integrity(
            result.request
        )
    )

    errors.extend(
        validate_terminal_component_reference_integrity(
            result.reference
        )
    )

    errors.extend(
        validate_terminal_service_assessment_integrity(
            result.assessment
        )
    )

    errors.extend(
        validate_terminal_service_presentation_integrity(
            result.presentation
        )
    )

    if result.decision not in TerminalServiceDecision:
        errors.append("invalid result decision")

    if (
        result.resolution
        not in TerminalServiceResolutionStatus
    ):
        errors.append("invalid result resolution")

    if result.authority_valid is not True:
        errors.append(
            "authority_valid must be true"
        )

    forbidden = (
        "market_data_generation",
        "evidence_generation",
        "intelligence_generation",
        "decision_generation",
        "d13_mutation",
        "risk_generation",
        "risk_override",
        "cas_generation",
        "cas_override",
        "execution",
        "order_authority",
        "position_authority",
        "upstream_mutation",
    )

    for key in forbidden:
        if result.metadata.get(key) is True:
            errors.append(
                f"result cannot enable {key}"
            )

    return errors


# ============================================================
# INTEGRITY — REGISTRY SNAPSHOT
# ============================================================

def validate_terminal_service_registry_snapshot_integrity(
    snapshot: TerminalServiceRegistrySnapshot,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        snapshot,
        TerminalServiceRegistrySnapshot,
    ):
        return [
            "snapshot must be "
            "TerminalServiceRegistrySnapshot"
        ]

    if snapshot.engine != TERMINAL_SERVICE_ENGINE:
        errors.append("snapshot engine mismatch")

    if snapshot.version != TERMINAL_SERVICE_VERSION:
        errors.append("snapshot version mismatch")

    if snapshot.count != len(snapshot.entries):
        errors.append("snapshot count mismatch")

    for entry in snapshot.entries:

        if not isinstance(
            entry,
            TerminalServiceRegistryEntry,
        ):
            errors.append(
                "snapshot contains invalid registry entry"
            )
            continue

        if not entry.key:
            errors.append(
                "registry entry key is required"
            )

        errors.extend(
            validate_terminal_component_reference_integrity(
                entry.reference
            )
        )

    return errors


# ============================================================
# INTEGRITY — EXECUTION RESULT
# ============================================================

def validate_terminal_service_execution_result_integrity(
    result: TerminalServiceExecutionResult,
) -> List[str]:

    errors: List[str] = []

    if not isinstance(
        result,
        TerminalServiceExecutionResult,
    ):
        return [
            "result must be "
            "TerminalServiceExecutionResult"
        ]

    if result.success and result.result is None:
        errors.append(
            "successful result requires terminal result"
        )

    if result.result is not None:
        errors.extend(
            validate_terminal_service_result_integrity(
                result.result
            )
        )

    if result.assessment is not None:
        errors.extend(
            validate_terminal_service_assessment_integrity(
                result.assessment
            )
        )

    if result.reference is not None:
        errors.extend(
            validate_terminal_component_reference_integrity(
                result.reference
            )
        )

    return errors


# ============================================================
# TERMINAL SUMMARY
# ============================================================

def build_terminal_service_summary(
    result: TerminalServiceResult,
) -> Dict[str, Any]:

    if not isinstance(
        result,
        TerminalServiceResult,
    ):
        return {
            "engine": TERMINAL_SERVICE_ENGINE,
            "version": TERMINAL_SERVICE_VERSION,
            "status": TerminalServiceStatus.INVALID.value,
            "decision": TerminalServiceDecision.BLOCK.value,
            "resolution":
                TerminalServiceResolutionStatus.BLOCKED.value,
            "authority_valid": False,
            "flags": ["invalid_result"],
        }

    assessment = result.assessment
    presentation = result.presentation

    return {
        "engine": TERMINAL_SERVICE_ENGINE,
        "version": TERMINAL_SERVICE_VERSION,

        "market": result.request.market,
        "instrument": result.request.instrument,
        "symbol": result.request.symbol,
        "contract": result.request.contract,
        "timeframe": result.request.timeframe,
        "mode": result.request.mode.value,

        "status": presentation.status.value,
        "decision": result.decision.value,
        "resolution": result.resolution.value,

        "readiness": assessment.readiness.value,
        "data_state": assessment.data_state.value,
        "consistency": assessment.consistency.value,

        "component_count":
            assessment.component_count,
        "ready_components":
            assessment.ready_components,
        "partial_components":
            assessment.partial_components,
        "invalid_components":
            assessment.invalid_components,

        "completeness_score": round(
            assessment.completeness_score,
            6,
        ),
        "freshness_score": round(
            assessment.freshness_score,
            6,
        ),
        "confidence_score": round(
            assessment.confidence_score,
            6,
        ),
        "quality_score": round(
            assessment.quality_score,
            6,
        ),

        "requirements_met":
            assessment.requirements_met,

        "authority_valid":
            result.authority_valid,

        "restrictions":
            list(result.restrictions),

        "flags":
            list(result.flags),

        "sources": {
            "decision":
                result.reference.decision_source,
            "d13":
                result.reference.d13_source,
            "risk":
                result.reference.risk_source,
            "cas":
                result.reference.cas_source,
        },

        "metadata":
            _ts_serialize_value(result.metadata),
    }


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [
    # Identity
    "TERMINAL_SERVICE_ENGINE",
    "TERMINAL_SERVICE_VERSION",
    "TERMINAL_SERVICE_AUTHORITY",

    # Enums
    "TerminalServiceStatus",
    "TerminalServiceMode",
    "TerminalServicePriority",
    "TerminalServiceSeverity",
    "TerminalServiceContractStatus",
    "TerminalServiceDataState",
    "TerminalServiceConsistency",
    "TerminalServiceReadiness",
    "TerminalServiceDecision",
    "TerminalServiceResolutionStatus",

    # Contracts
    "TerminalServiceRequest",
    "TerminalComponentSnapshot",
    "TerminalComponentReference",
    "TerminalServiceContractValidation",
    "TerminalServiceRequirements",
    "TerminalServiceAssessment",
    "TerminalServiceResolutionRules",
    "TerminalServicePresentation",
    "TerminalServiceResult",
    "TerminalServiceSourceMap",

    # Registry / Service
    "TerminalServiceRegistryEntry",
    "TerminalServiceRegistrySnapshot",
    "TerminalServiceExecutionResult",
    "TerminalServiceRegistry",
    "TerminalService",

    # Builders / validators
    "normalize_terminal_service_request",
    "validate_terminal_service_request",
    "build_terminal_service_request",
    "build_terminal_component_reference",
    "build_terminal_service_requirements",
    "build_terminal_service_resolution_rules",
    "build_terminal_service_presentation",
    "build_terminal_service_source_map",
    "validate_terminal_service_authority",
    "validate_terminal_service_result",
    "validate_terminal_service_registry",
    "terminal_service_registry_health",

    # Core orchestration
    "aggregate_terminal_components",
    "evaluate_terminal_requirements",
    "assess_terminal_service",
    "resolve_terminal_service",

    # Service helpers
    "get_terminal_service",
    "resolve_terminal",
    "get_terminal_reference",
    "terminal_service_snapshot",
    "terminal_service_count",
    "terminal_service_health",
    "terminal_service_integrity",
    "terminal_service_operational_check",
    "terminal_service_info",

    # Serialization
    "serialize_terminal_service_request",
    "serialize_terminal_component_snapshot",
    "serialize_terminal_component_reference",
    "serialize_terminal_service_requirements",
    "serialize_terminal_service_assessment",
    "serialize_terminal_service_resolution_rules",
    "serialize_terminal_service_presentation",
    "serialize_terminal_service_result",
    "serialize_terminal_service_source_map",
    "serialize_terminal_service_registry_snapshot",
    "serialize_terminal_service_execution_result",

    # Integrity
    "validate_terminal_service_request_integrity",
    "validate_terminal_component_snapshot_integrity",
    "validate_terminal_component_reference_integrity",
    "validate_terminal_service_requirements_integrity",
    "validate_terminal_service_assessment_integrity",
    "validate_terminal_service_resolution_rules_integrity",
    "validate_terminal_service_presentation_integrity",
    "validate_terminal_service_result_integrity",
    "validate_terminal_service_registry_snapshot_integrity",
    "validate_terminal_service_execution_result_integrity",

    # Summary
    "build_terminal_service_summary",
]
# ============================================================================
# ROBOMLM TERMINAL — FRONTEND INTEGRATION CONTRACT
# PART 1
# ----------------------------------------------------------------------------
# Purpose:
#   Expose the EXISTING Terminal service through one stable application-level
#   entry point for the frontend/API integration.
#
# Rules:
#   - Does NOT create a new intelligence engine.
#   - Does NOT calculate a new decision.
#   - Does NOT create BUY/SELL authority.
#   - Does NOT bypass D13.
#   - Does NOT bypass Risk.
#   - Does NOT bypass CAS.
#   - Does NOT place orders.
#   - Does NOT fabricate missing values.
#   - Existing Terminal components remain their owners.
# ============================================================================


from typing import Any, Mapping


_TERMINAL_FRONTEND_CONTRACT_VERSION = "ROBOMLM-TERMINAL-FRONTEND-1.0"


def _terminal_frontend_dict(value: Any) -> dict[str, Any]:
    """
    Convert an existing Terminal result into a plain dictionary without
    inventing missing fields.

    Supported existing result types:
        - dict / Mapping
        - dataclass-like object
        - object exposing model_dump()
        - object exposing dict()
    """
    if value is None:
        return {}

    if isinstance(value, Mapping):
        return dict(value)

    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        try:
            result = model_dump()
            if isinstance(result, Mapping):
                return dict(result)
        except Exception:
            pass

    as_dict = getattr(value, "dict", None)
    if callable(as_dict):
        try:
            result = as_dict()
            if isinstance(result, Mapping):
                return dict(result)
        except Exception:
            pass

    if hasattr(value, "__dict__"):
        try:
            return dict(vars(value))
        except Exception:
            pass

    return {}


def _terminal_frontend_section(
    result: Mapping[str, Any],
    *names: str,
) -> Any:
    """
    Resolve an existing Terminal section from the canonical result.

    The canonical Terminal application result keeps:
        evidence -> top-level
        intelligence -> pipeline
        decision -> pipeline
        risk -> pipeline
        cas -> pipeline

    This is a transport/presentation lookup only.
    It does not calculate, transform, or manufacture domain results.
    """
    for name in names:
        if name in result:
            return result[name]

    pipeline = result.get("pipeline")
    if isinstance(pipeline, Mapping):
        for name in names:
            if name in pipeline:
                return pipeline[name]

    return None

def terminal_frontend_payload(
    result: Any,
    *,
    symbol: str | None = None,
    timeframe: str | None = None,
    market: str | None = None,
    instrument: str | None = None,
) -> dict[str, Any]:
    """
    Build the frontend transport envelope from an EXISTING Terminal result.

    Important:
        This function is a presentation/transport adapter only.

        It never creates:
            - decision
            - direction
            - confidence
            - EQE
            - risk
            - CAS approval
            - execution

        Missing sections remain None instead of being fabricated.
    """
    raw = _terminal_frontend_dict(result)

    context = {
        "symbol": symbol or raw.get("symbol"),
        "timeframe": timeframe or raw.get("timeframe"),
        "market": market or raw.get("market"),
        "instrument": instrument or raw.get("instrument"),
    }

    payload = dict(raw)

    payload["terminal_contract"] = {
        "version": _TERMINAL_FRONTEND_CONTRACT_VERSION,
        "source": "app.terminal.terminal_service",
        "generated_by": "existing_terminal_service",
    }

    payload["context"] = context

    # ------------------------------------------------------------------------
    # Preserve existing Terminal owners.
    # Nothing is generated here.
    # ------------------------------------------------------------------------

    payload["sections"] = {
        "market_context": _terminal_frontend_section(
         raw, "market_context", "marketContext", "market",
         ),

        "evidence_strip": _terminal_frontend_section(
            raw,
            "evidence_strip",
            "evidenceStrip",
            "evidence",
        ),
        "intelligence": _terminal_frontend_section(
            raw,
            "intelligence",
            "intelligence_panel",
            "intelligencePanel",
        ),
        "decision_outlook": _terminal_frontend_section(
            raw,
            "decision_outlook",
            "decisionOutlook",
            "decision",
        ),
        "risk": _terminal_frontend_section(
            raw,
            "risk",
            "risk_panel",
            "riskPanel",
        ),
        "cas_status": _terminal_frontend_section(
            raw,
            "cas_status",
            "casStatus",
            "cas",
        ),
    }

    # ------------------------------------------------------------------------
    # Explicit authority metadata.
    #
    # These are architectural declarations, NOT calculated approvals.
    # ------------------------------------------------------------------------

    payload["authority"] = {
        "decision_authority": "D13",
        "risk_authority": "Risk",
        "execution_authority": "CAS",
        "frontend_is_authority": False,
        "frontend_can_execute": False,
    }

    return payload


def terminal_frontend_context(
    *,
    symbol: str = "BTC/USDT",
    timeframe: str = "1m",
    market: str | None = None,
    instrument: str | None = None,
) -> dict[str, Any]:
    """
    Return the normalized context used by Terminal frontend integration.

    This does not fetch market data and does not perform analysis.
    """
    return {
        "symbol": str(symbol or "BTC/USDT").strip(),
        "timeframe": str(timeframe or "1m").strip(),
        "market": (
            str(market).strip()
            if market is not None and str(market).strip()
            else None
        ),
        "instrument": (
            str(instrument).strip()
            if instrument is not None and str(instrument).strip()
            else None
        ),
    }


# Public compatibility names.
#
# API/frontend integration can use these names without depending on private
# implementation details of the Terminal service.
terminal_to_frontend = terminal_frontend_payload
get_terminal_frontend_context = terminal_frontend_context
# ============================================================
# ROBOMLM TERMINAL FRONTEND CONTRACT — PART 2
# Exact Terminal UI mapping
# ============================================================

_TERMINAL_FRONTEND_UI_VERSION = "ROBOMLM-TERMINAL-UI-1.0"


def terminal_frontend_ui_map() -> dict[str, Any]:
    """
    Canonical mapping between Terminal backend sections and the
    EXISTING terminal.html DOM.

    This is presentation metadata only.
    It does not calculate signals, decisions, risk, CAS or execution.
    """

    return {
        "version": _TERMINAL_FRONTEND_UI_VERSION,

        "portfolio": {
            "capital": "#pf-capital",
            "balance": "#pf-balance",
            "today_pnl": "#pf-pnl",
            "open_positions": "#pf-open",
            "win_rate": "#pf-winrate",
            "mode": "#pf-mode",
            "positions_list": "#pf-pos-list",
        },

        "market": {
            "market_select": "#market-select",
            "symbol_select": "#symbol-select",
            "price": "#sb-price",
            "change": "#sb-change",
            "timeframe_group": "#tf-group",
            "timeframe_buttons": "[data-tf]",
            "state_badge": "#state-badge",
        },

        "chart": {
            "container": "#chart",
        },

        "metrics": {
            "container": "#metrics-strip",
        },

        "evidence": {
            "container": "#evidence-strip",
        },

        "decision": {
            "box": "#decision-box",
            "signal_box": "#d13-signal-box",
            "signal": "#d13-signal-text",
            "confidence": "#d13-conf",
            "grade": "#d13-grade",
            "rr": "#d13-rr",
            "count": "#decision-count",
            "reason": "#decision-reason",
            "progress_bar": "#decision-progress-bar",
            "advisory": "#d13-advisory",
        },

        "manual_inputs": {
            "tp": "#in-tp",
            "sl": "#in-sl",
        },

        "trade_controls": {
            "call": "#btn-call",
            "put": "#btn-put",
            "confirm": "#btn-confirm",
        },

        "cas": {
            "container": "#p-cas",
        },

        "log": {
            "container": "#p-log",
        },

        "discovery_context": {
            "symbol": "[data-discovery-symbol]",
            "market": "[data-discovery-market]",
            "instrument": "[data-discovery-instrument]",
            "timeframe": "[data-discovery-timeframe]",
        },
    }


def _terminal_frontend_ui_section(
    value: Any,
    *,
    section: str,
    selectors: dict[str, Any],
) -> dict[str, Any]:
    """
    Attach the exact existing UI selectors to one backend section.

    No transformation of the underlying domain result is performed
    beyond the safe frontend dictionary conversion already provided
    by terminal_frontend_payload().
    """

    return {
        "section": section,
        "selectors": selectors,
        "data": _terminal_frontend_dict(value),
    }


def build_terminal_frontend_ui_payload(
    result: Any,
    *,
    symbol: str = "",
    timeframe: str = "",
    market: str = "",
    instrument: str = "",
) -> dict[str, Any]:
    """
    Convert the canonical TerminalService result into the frontend
    contract expected by the existing terminal.html.

    Backend ownership remains unchanged:

        Market Context
            ↓
        Evidence
            ↓
        Intelligence
            ↓
        D13 Decision
            ↓
        Risk
            ↓
        CAS

    The frontend only renders the returned state.
    """

    base = terminal_frontend_payload(
        result,
        symbol=symbol,
        timeframe=timeframe,
        market=market,
        instrument=instrument,
    )

    ui = terminal_frontend_ui_map()
    sections = base.get("sections", {})

    payload = {
        "contract_version": _TERMINAL_FRONTEND_UI_VERSION,

        "symbol": base.get("symbol", symbol),
        "timeframe": base.get("timeframe", timeframe),

        "context": base.get("context", {
            "symbol": symbol,
            "timeframe": timeframe,
            "market": market,
            "instrument": instrument,
        }),

        "ui": ui,

        "sections": {
            "portfolio": _terminal_frontend_ui_section(
                base.get("portfolio"),
                section="portfolio",
                selectors=ui["portfolio"],
            ),

            "market": _terminal_frontend_ui_section(
                sections.get("market_context"),
                section="market",
                selectors=ui["market"],
            ),

            "chart": _terminal_frontend_ui_section(
                base.get("chart"),
                section="chart",
                selectors=ui["chart"],
            ),

            "metrics": _terminal_frontend_ui_section(
                base.get("metrics"),
                section="metrics",
                selectors=ui["metrics"],
            ),

            "evidence": _terminal_frontend_ui_section(
                sections.get("evidence_strip"),
                section="evidence",
                selectors=ui["evidence"],
            ),

            "intelligence": _terminal_frontend_ui_section(
                sections.get("intelligence"),
                section="intelligence",
                selectors={
                    "container": "#decision-box",
                },
            ),

            "decision": _terminal_frontend_ui_section(
                sections.get("decision_outlook"),
                section="decision",
                selectors=ui["decision"],
            ),

            "risk": _terminal_frontend_ui_section(
                sections.get("risk"),
                section="risk",
                selectors={
                    "container": "#decision-box",
                },
            ),

            "cas": _terminal_frontend_ui_section(
                sections.get("cas_status"),
                section="cas",
                selectors=ui["cas"],
            ),

            "log": _terminal_frontend_ui_section(
                base.get("log"),
                section="log",
                selectors=ui["log"],
            ),
        },

        "controls": {
            "manual_inputs": ui["manual_inputs"],
            "trade_controls": ui["trade_controls"],
        },

        "authority": {
            "frontend_is_authority": False,
            "frontend_can_decide": False,
            "frontend_can_authorize": False,
            "frontend_can_execute": False,
            "decision_authority": "D13",
            "risk_authority": "RISK",
            "execution_authority": "CAS",
        },
    }

    return payload


def terminal_frontend_ui_contract(
    result: Any,
    *,
    symbol: str = "",
    timeframe: str = "",
    market: str = "",
    instrument: str = "",
) -> dict[str, Any]:
    """
    Public compatibility entry point for API/application layers.

    Existing TerminalService remains the owner of the domain result.
    """

    return build_terminal_frontend_ui_payload(
        result,
        symbol=symbol,
        timeframe=timeframe,
        market=market,
        instrument=instrument,
    )


# Compatibility aliases for existing callers.
build_terminal_ui_payload = build_terminal_frontend_ui_payload
get_terminal_frontend_ui_map = terminal_frontend_ui_map