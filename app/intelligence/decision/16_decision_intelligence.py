# ============================================================
# ROBOMLM_PLUS
# D16 - DECISION INTELLIGENCE
# PART 1 - CORE INTELLIGENCE FOUNDATION
# ============================================================
#
# ROLE:
#   D16 is the FINAL INTELLIGENCE SYNTHESIS layer.
#
# FLOW:
#   D1-D15 validated outputs
#          ↓
#   D16 evidence-preserving synthesis
#          ↓
#   Intelligence State
#
# AUTHORITY:
#   D13 = Decision Authority
#   D14 = Validation Authority
#   D15 = Learning Authority
#   D16 = Intelligence Synthesis Authority
#
# HARD BOUNDARIES:
#   - D16 does NOT create a new BUY/SELL decision.
#   - D16 does NOT execute trades.
#   - D16 does NOT modify D13 decisions.
#   - D16 does NOT modify D14 validation.
#   - D16 does NOT modify D15 learning parameters.
#   - D16 does NOT invent probability/confidence scores.
#   - D16 does NOT use future information.
#   - D16 preserves upstream provenance.
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Mapping, Optional, Tuple
from copy import deepcopy


# ============================================================
# CONSTANTS
# ============================================================

D16_ENGINE_NAME = "D16_DecisionIntelligence"
D16_ENGINE_VERSION = "V6-CAS-1.0"

D16_AUTHORITY = "INTELLIGENCE_SYNTHESIS"

D16_DECISION_AUTHORITY = False
D16_EXECUTION_AUTHORITY = False
D16_PROBABILITY_AUTHORITY = False


# ============================================================
# ENUMS
# ============================================================

class D16Status(str, Enum):
    READY = "READY"
    LIMITED = "LIMITED"
    BLOCKED = "BLOCKED"
    UNDETERMINED = "UNDETERMINED"


class IntelligenceDisposition(str, Enum):
    SYNTHESIZED = "SYNTHESIZED"
    LIMITED = "LIMITED"
    BLOCKED = "BLOCKED"
    UNDETERMINED = "UNDETERMINED"


class IntelligenceType(str, Enum):
    MARKET_CONTEXT = "MARKET_CONTEXT"
    DECISION_CONTEXT = "DECISION_CONTEXT"
    VALIDATION_CONTEXT = "VALIDATION_CONTEXT"
    LEARNING_CONTEXT = "LEARNING_CONTEXT"
    CROSS_LAYER = "CROSS_LAYER"
    PATTERN_CONTEXT = "PATTERN_CONTEXT"
    TEMPORAL_CONTEXT = "TEMPORAL_CONTEXT"


class ProvenanceStatus(str, Enum):
    VERIFIED = "VERIFIED"
    PARTIAL = "PARTIAL"
    INVALID = "INVALID"
    MISSING = "MISSING"


# ============================================================
# HELPERS
# ============================================================

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None

    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value

    if isinstance(value, str):
        text = value.strip()

        if not text:
            return None

        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))

            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)

            return parsed

        except (TypeError, ValueError):
            return None

    return None


def clean_text(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip()


def normalize_id(value: Any) -> str:
    return clean_text(value)


def deep_copy(value: Any) -> Any:
    return deepcopy(value)


# ============================================================
# PROVENANCE
# ============================================================

@dataclass(frozen=True)
class D16Provenance:
    source_layer: str
    source_engine: str
    source_version: str
    source_id: str
    observed_at: Optional[datetime]
    received_at: Optional[datetime]
    provenance_status: ProvenanceStatus = ProvenanceStatus.VERIFIED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_layer": self.source_layer,
            "source_engine": self.source_engine,
            "source_version": self.source_version,
            "source_id": self.source_id,
            "observed_at": (
                self.observed_at.isoformat()
                if self.observed_at else None
            ),
            "received_at": (
                self.received_at.isoformat()
                if self.received_at else None
            ),
            "provenance_status": self.provenance_status.value,
        }


def validate_d16_provenance(
    provenance: Optional[D16Provenance],
) -> ProvenanceStatus:

    if provenance is None:
        return ProvenanceStatus.MISSING

    if not clean_text(provenance.source_layer):
        return ProvenanceStatus.INVALID

    if not clean_text(provenance.source_engine):
        return ProvenanceStatus.INVALID

    if not clean_text(provenance.source_version):
        return ProvenanceStatus.INVALID

    if not clean_text(provenance.source_id):
        return ProvenanceStatus.INVALID

    if provenance.observed_at is None:
        return ProvenanceStatus.PARTIAL

    if provenance.received_at is None:
        return ProvenanceStatus.PARTIAL

    if provenance.observed_at > provenance.received_at:
        return ProvenanceStatus.INVALID

    return provenance.provenance_status


# ============================================================
# UPSTREAM INPUT
# ============================================================

@dataclass
class D16UpstreamInput:
    layer: str
    engine: str
    version: str
    source_id: str
    status: str
    payload: Mapping[str, Any]
    provenance: Optional[D16Provenance] = None
    observed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "layer": self.layer,
            "engine": self.engine,
            "version": self.version,
            "source_id": self.source_id,
            "status": self.status,
            "payload": deep_copy(dict(self.payload)),
            "provenance": (
                self.provenance.to_dict()
                if self.provenance else None
            ),
            "observed_at": (
                self.observed_at.isoformat()
                if self.observed_at else None
            ),
        }


# ============================================================
# INTELLIGENCE OBSERVATION
# ============================================================

@dataclass
class IntelligenceObservation:
    observation_id: str
    intelligence_type: IntelligenceType
    disposition: IntelligenceDisposition
    statement: str
    supporting_layers: Tuple[str, ...] = field(default_factory=tuple)
    source_ids: Tuple[str, ...] = field(default_factory=tuple)
    provenance_status: ProvenanceStatus = ProvenanceStatus.VERIFIED
    observed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "intelligence_type": self.intelligence_type.value,
            "disposition": self.disposition.value,
            "statement": self.statement,
            "supporting_layers": list(self.supporting_layers),
            "source_ids": list(self.source_ids),
            "provenance_status": self.provenance_status.value,
            "observed_at": (
                self.observed_at.isoformat()
                if self.observed_at else None
            ),
            "metadata": deep_copy(self.metadata),
        }


# ============================================================
# D16 INTELLIGENCE RESULT
# ============================================================

@dataclass
class D16IntelligenceResult:
    status: D16Status
    disposition: IntelligenceDisposition

    market_identity: Optional[str] = None
    intelligence_type: Optional[IntelligenceType] = None

    observations: List[IntelligenceObservation] = field(
        default_factory=list
    )

    supporting_layers: Tuple[str, ...] = field(default_factory=tuple)
    source_ids: Tuple[str, ...] = field(default_factory=tuple)

    provenance_status: ProvenanceStatus = ProvenanceStatus.VERIFIED

    observed_at: Optional[datetime] = None
    generated_at: Optional[datetime] = None

    decision_authority: bool = False
    execution_authority: bool = False
    probability_authority: bool = False

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "disposition": self.disposition.value,
            "market_identity": self.market_identity,
            "intelligence_type": (
                self.intelligence_type.value
                if self.intelligence_type else None
            ),
            "observations": [
                item.to_dict()
                for item in self.observations
            ],
            "supporting_layers": list(self.supporting_layers),
            "source_ids": list(self.source_ids),
            "provenance_status": self.provenance_status.value,
            "observed_at": (
                self.observed_at.isoformat()
                if self.observed_at else None
            ),
            "generated_at": (
                self.generated_at.isoformat()
                if self.generated_at else None
            ),
            "decision_authority": self.decision_authority,
            "execution_authority": self.execution_authority,
            "probability_authority": self.probability_authority,
            "metadata": deep_copy(self.metadata),
        }


# ============================================================
# OBSERVATION ID
# ============================================================

def build_d16_observation_id(
    intelligence_type: IntelligenceType,
    source_ids: Tuple[str, ...],
    observed_at: Optional[datetime],
) -> str:

    source_part = "|".join(
        sorted(
            normalize_id(item)
            for item in source_ids
            if normalize_id(item)
        )
    )

    time_part = (
        observed_at.isoformat()
        if observed_at
        else "NO_TIME"
    )

    return (
        f"D16:{intelligence_type.value}:"
        f"{source_part}:{time_part}"
    )


# ============================================================
# CORE D16 ENGINE
# ============================================================

class D16DecisionIntelligenceEngine:
    """
    Final intelligence synthesis layer.

    This engine describes what the validated upstream layers
    collectively establish.

    It does not create a new trading decision.
    """

    def __init__(self) -> None:
        self._history: List[D16IntelligenceResult] = []

    def synthesize(
        self,
        upstream_inputs: List[D16UpstreamInput],
        market_identity: Optional[str] = None,
    ) -> D16IntelligenceResult:

        generated_at = utc_now()

        if not upstream_inputs:
            result = D16IntelligenceResult(
                status=D16Status.UNDETERMINED,
                disposition=IntelligenceDisposition.UNDETERMINED,
                market_identity=market_identity,
                generated_at=generated_at,
                decision_authority=False,
                execution_authority=False,
                probability_authority=False,
                provenance_status=ProvenanceStatus.MISSING,
            )

            self._history.append(result)
            return result

        valid_inputs: List[D16UpstreamInput] = []
        source_ids: List[str] = []
        layers: List[str] = []
        provenance_states: List[ProvenanceStatus] = []

        for item in upstream_inputs:

            if not clean_text(item.layer):
                continue

            if not clean_text(item.engine):
                continue

            if not clean_text(item.version):
                continue

            if not clean_text(item.source_id):
                continue

            valid_inputs.append(item)

            source_ids.append(item.source_id)
            layers.append(item.layer)

            provenance_states.append(
                validate_d16_provenance(item.provenance)
            )

        if not valid_inputs:
            result = D16IntelligenceResult(
                status=D16Status.BLOCKED,
                disposition=IntelligenceDisposition.BLOCKED,
                market_identity=market_identity,
                generated_at=generated_at,
                decision_authority=False,
                execution_authority=False,
                probability_authority=False,
                provenance_status=ProvenanceStatus.INVALID,
            )

            self._history.append(result)
            return result

        unique_layers = tuple(dict.fromkeys(layers))
        unique_sources = tuple(dict.fromkeys(source_ids))

        if all(
            state == ProvenanceStatus.VERIFIED
            for state in provenance_states
        ):
            provenance_status = ProvenanceStatus.VERIFIED

        elif any(
            state == ProvenanceStatus.INVALID
            for state in provenance_states
        ):
            provenance_status = ProvenanceStatus.INVALID

        else:
            provenance_status = ProvenanceStatus.PARTIAL

        if provenance_status == ProvenanceStatus.INVALID:
            status = D16Status.BLOCKED
            disposition = IntelligenceDisposition.BLOCKED

        elif provenance_status == ProvenanceStatus.PARTIAL:
            status = D16Status.LIMITED
            disposition = IntelligenceDisposition.LIMITED

        else:
            status = D16Status.READY
            disposition = IntelligenceDisposition.SYNTHESIZED

        observations: List[IntelligenceObservation] = []

        for item in valid_inputs:

            statement = self._extract_supported_statement(item)

            if not statement:
                continue

            intelligence_type = self._classify_intelligence_type(
                item.layer
            )

            observation_id = build_d16_observation_id(
                intelligence_type,
                (item.source_id,),
                item.observed_at,
            )

            observations.append(
                IntelligenceObservation(
                    observation_id=observation_id,
                    intelligence_type=intelligence_type,
                    disposition=disposition,
                    statement=statement,
                    supporting_layers=(item.layer,),
                    source_ids=(item.source_id,),
                    provenance_status=(
                        validate_d16_provenance(item.provenance)
                    ),
                    observed_at=item.observed_at,
                )
            )

        result = D16IntelligenceResult(
            status=status,
            disposition=disposition,
            market_identity=market_identity,
            intelligence_type=IntelligenceType.CROSS_LAYER,
            observations=observations,
            supporting_layers=unique_layers,
            source_ids=unique_sources,
            provenance_status=provenance_status,
            generated_at=generated_at,
            decision_authority=False,
            execution_authority=False,
            probability_authority=False,
        )

        self._history.append(result)

        return result

    @staticmethod
    def _classify_intelligence_type(
        layer: str,
    ) -> IntelligenceType:

        normalized = clean_text(layer).upper()

        if normalized == "D10":
            return IntelligenceType.MARKET_CONTEXT

        if normalized == "D13":
            return IntelligenceType.DECISION_CONTEXT

        if normalized == "D14":
            return IntelligenceType.VALIDATION_CONTEXT

        if normalized == "D15":
            return IntelligenceType.LEARNING_CONTEXT

        if "TEMPORAL" in normalized:
            return IntelligenceType.TEMPORAL_CONTEXT

        if "PATTERN" in normalized:
            return IntelligenceType.PATTERN_CONTEXT

        return IntelligenceType.CROSS_LAYER

    @staticmethod
    def _extract_supported_statement(
        item: D16UpstreamInput,
    ) -> str:

        payload = dict(item.payload)

        candidates = (
            payload.get("intelligence_statement"),
            payload.get("validated_statement"),
            payload.get("learning_statement"),
            payload.get("validation_statement"),
            payload.get("market_context"),
            payload.get("summary"),
            payload.get("statement"),
        )

        for candidate in candidates:

            text = clean_text(candidate)

            if text:
                return text

        return ""

    def history(self) -> List[D16IntelligenceResult]:
        return list(self._history)

    def latest(self) -> Optional[D16IntelligenceResult]:
        if not self._history:
            return None

        return self._history[-1]

    def clear(self) -> None:
        self._history.clear()


# ============================================================
# D16 CONTRACT
# ============================================================

@dataclass(frozen=True)
class D16IntelligenceContract:
    engine_name: str
    engine_version: str
    authority: str

    status: D16Status
    disposition: IntelligenceDisposition

    intelligence: Mapping[str, Any]

    decision_authority: bool
    execution_authority: bool
    probability_authority: bool

    generated_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "engine_name": self.engine_name,
            "engine_version": self.engine_version,
            "authority": self.authority,
            "status": self.status.value,
            "disposition": self.disposition.value,
            "intelligence": deep_copy(dict(self.intelligence)),
            "decision_authority": self.decision_authority,
            "execution_authority": self.execution_authority,
            "probability_authority": self.probability_authority,
            "generated_at": self.generated_at.isoformat(),
        }


# ============================================================
# CONTRACT BUILDER
# ============================================================

def build_d16_contract(
    result: D16IntelligenceResult,
) -> D16IntelligenceContract:

    return D16IntelligenceContract(
        engine_name=D16_ENGINE_NAME,
        engine_version=D16_ENGINE_VERSION,
        authority=D16_AUTHORITY,
        status=result.status,
        disposition=result.disposition,
        intelligence=result.to_dict(),
        decision_authority=False,
        execution_authority=False,
        probability_authority=False,
        generated_at=result.generated_at or utc_now(),
    )


# ============================================================
# CONTRACT VALIDATOR
# ============================================================

def validate_d16_contract(
    contract: D16IntelligenceContract,
) -> bool:

    if contract.engine_name != D16_ENGINE_NAME:
        return False

    if contract.engine_version != D16_ENGINE_VERSION:
        return False

    if contract.authority != D16_AUTHORITY:
        return False

    if contract.decision_authority:
        return False

    if contract.execution_authority:
        return False

    if contract.probability_authority:
        return False

    if not isinstance(contract.intelligence, Mapping):
        return False

    return True


# ============================================================
# PART-1 SELF TEST
# ============================================================

def d16_part1_self_check() -> Dict[str, bool]:

    observed = utc_now()

    provenance = D16Provenance(
        source_layer="D15",
        source_engine="D15_DecisionLearning",
        source_version="V6-CAS-1.0",
        source_id="D15-TEST-001",
        observed_at=observed,
        received_at=observed,
        provenance_status=ProvenanceStatus.VERIFIED,
    )

    upstream = D16UpstreamInput(
        layer="D15",
        engine="D15_DecisionLearning",
        version="V6-CAS-1.0",
        source_id="D15-TEST-001",
        status="READY",
        payload={
            "learning_statement": (
                "Validated learning observation supplied by D15."
            )
        },
        provenance=provenance,
        observed_at=observed,
    )

    engine = D16DecisionIntelligenceEngine()

    result = engine.synthesize(
        [upstream],
        market_identity="TEST-MARKET",
    )

    contract = build_d16_contract(result)

    checks = {
        "engine_created": engine is not None,
        "result_created": result is not None,
        "status_ready": result.status == D16Status.READY,
        "observation_created": len(result.observations) == 1,
        "provenance_verified": (
            result.provenance_status == ProvenanceStatus.VERIFIED
        ),
        "decision_authority_false": (
            result.decision_authority is False
        ),
        "execution_authority_false": (
            result.execution_authority is False
        ),
        "probability_authority_false": (
            result.probability_authority is False
        ),
        "contract_created": contract is not None,
        "contract_valid": validate_d16_contract(contract),
    }

    return checks


def create_d16_engine() -> D16DecisionIntelligenceEngine:
    return D16DecisionIntelligenceEngine()


# ============================================================
# DIRECT TEST
# ============================================================
# ============================================================
# D16 - PART 2
# UPSTREAM RECONCILIATION & CROSS-LAYER INTELLIGENCE
# ============================================================

D16_PART2_NAME = "D16_UpstreamReconciliation"
D16_PART2_VERSION = "V6-CAS-1.0"


# ============================================================
# ENUMS
# ============================================================

class D16ReconciliationStatus(str, Enum):
    READY = "READY"
    LIMITED = "LIMITED"
    BLOCKED = "BLOCKED"
    UNDETERMINED = "UNDETERMINED"


class D16EvidenceDisposition(str, Enum):
    SUPPORTING = "SUPPORTING"
    CONTRADICTORY = "CONTRADICTORY"
    NEUTRAL = "NEUTRAL"
    INSUFFICIENT = "INSUFFICIENT"


class D16ConflictType(str, Enum):
    NONE = "NONE"
    IDENTITY_CONFLICT = "IDENTITY_CONFLICT"
    TEMPORAL_CONFLICT = "TEMPORAL_CONFLICT"
    STATUS_CONFLICT = "STATUS_CONFLICT"
    DIRECTION_CONFLICT = "DIRECTION_CONFLICT"
    SCENARIO_CONFLICT = "SCENARIO_CONFLICT"
    VALIDATION_CONFLICT = "VALIDATION_CONFLICT"
    PROVENANCE_CONFLICT = "PROVENANCE_CONFLICT"


# ============================================================
# RECONCILIATION EVIDENCE
# ============================================================

@dataclass
class D16ReconciliationEvidence:
    layer: str
    engine: str
    version: str
    source_id: str

    status: str

    market_identity: Optional[str] = None
    direction: Optional[str] = None
    scenario: Optional[str] = None

    observed_at: Optional[datetime] = None

    disposition: D16EvidenceDisposition = (
        D16EvidenceDisposition.SUPPORTING
    )

    provenance: Optional[D16Provenance] = None

    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "layer": self.layer,
            "engine": self.engine,
            "version": self.version,
            "source_id": self.source_id,
            "status": self.status,
            "market_identity": self.market_identity,
            "direction": self.direction,
            "scenario": self.scenario,
            "observed_at": (
                self.observed_at.isoformat()
                if self.observed_at else None
            ),
            "disposition": self.disposition.value,
            "provenance": (
                self.provenance.to_dict()
                if self.provenance else None
            ),
            "payload": deep_copy(self.payload),
        }


# ============================================================
# RECONCILIATION RESULT
# ============================================================

@dataclass
class D16UpstreamReconciliation:
    status: D16ReconciliationStatus

    evidence: List[D16ReconciliationEvidence] = field(
        default_factory=list
    )

    supporting_layers: Tuple[str, ...] = field(default_factory=tuple)
    contradictory_layers: Tuple[str, ...] = field(default_factory=tuple)

    conflicts: Tuple[D16ConflictType, ...] = field(
        default_factory=tuple
    )

    market_identity: Optional[str] = None

    direction_values: Tuple[str, ...] = field(default_factory=tuple)
    scenario_values: Tuple[str, ...] = field(default_factory=tuple)

    earliest_observation: Optional[datetime] = None
    latest_observation: Optional[datetime] = None

    provenance_status: ProvenanceStatus = (
        ProvenanceStatus.VERIFIED
    )

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "evidence": [
                item.to_dict()
                for item in self.evidence
            ],
            "supporting_layers": list(self.supporting_layers),
            "contradictory_layers": list(
                self.contradictory_layers
            ),
            "conflicts": [
                item.value
                for item in self.conflicts
            ],
            "market_identity": self.market_identity,
            "direction_values": list(self.direction_values),
            "scenario_values": list(self.scenario_values),
            "earliest_observation": (
                self.earliest_observation.isoformat()
                if self.earliest_observation else None
            ),
            "latest_observation": (
                self.latest_observation.isoformat()
                if self.latest_observation else None
            ),
            "provenance_status": self.provenance_status.value,
            "metadata": deep_copy(self.metadata),
        }


# ============================================================
# EXTRACTION HELPERS
# ============================================================

def d16_extract_market_identity(
    payload: Mapping[str, Any],
) -> Optional[str]:

    candidates = (
        payload.get("market_identity"),
        payload.get("instrument_identity"),
        payload.get("symbol"),
        payload.get("market"),
    )

    for candidate in candidates:
        value = clean_text(candidate)
        if value:
            return value

    return None


def d16_extract_direction(
    payload: Mapping[str, Any],
) -> Optional[str]:

    candidates = (
        payload.get("direction"),
        payload.get("expected_direction"),
        payload.get("validated_direction"),
        payload.get("decision_direction"),
    )

    for candidate in candidates:
        value = clean_text(candidate).upper()

        if value:
            return value

    return None


def d16_extract_scenario(
    payload: Mapping[str, Any],
) -> Optional[str]:

    candidates = (
        payload.get("scenario"),
        payload.get("scenario_type"),
        payload.get("validated_scenario"),
    )

    for candidate in candidates:
        value = clean_text(candidate)

        if value:
            return value

    return None


def d16_extract_status(
    item: D16UpstreamInput,
) -> str:

    status = clean_text(item.status).upper()

    if status:
        return status

    payload = dict(item.payload)

    for key in (
        "status",
        "validation_status",
        "decision_status",
        "learning_status",
    ):
        value = clean_text(payload.get(key)).upper()

        if value:
            return value

    return ""


# ============================================================
# TEMPORAL VALIDATION
# ============================================================

def d16_validate_temporal_order(
    evidence: List[D16ReconciliationEvidence],
) -> bool:

    timestamps = [
        item.observed_at
        for item in evidence
        if item.observed_at is not None
    ]

    if len(timestamps) <= 1:
        return True

    return timestamps == sorted(timestamps)


def d16_temporal_bounds(
    evidence: List[D16ReconciliationEvidence],
) -> Tuple[Optional[datetime], Optional[datetime]]:

    timestamps = [
        item.observed_at
        for item in evidence
        if item.observed_at is not None
    ]

    if not timestamps:
        return None, None

    return min(timestamps), max(timestamps)


# ============================================================
# CONFLICT DETECTION
# ============================================================

def d16_detect_identity_conflict(
    evidence: List[D16ReconciliationEvidence],
) -> bool:

    identities = {
        clean_text(item.market_identity)
        for item in evidence
        if clean_text(item.market_identity)
    }

    return len(identities) > 1


def d16_detect_direction_conflict(
    evidence: List[D16ReconciliationEvidence],
) -> bool:

    directions = {
        clean_text(item.direction).upper()
        for item in evidence
        if clean_text(item.direction)
    }

    meaningful = {
        item
        for item in directions
        if item not in {"UNKNOWN", "NEUTRAL", "NONE"}
    }

    return len(meaningful) > 1


def d16_detect_scenario_conflict(
    evidence: List[D16ReconciliationEvidence],
) -> bool:

    scenarios = {
        clean_text(item.scenario).upper()
        for item in evidence
        if clean_text(item.scenario)
    }

    return len(scenarios) > 1


def d16_detect_status_conflict(
    evidence: List[D16ReconciliationEvidence],
) -> bool:

    statuses = {
        clean_text(item.status).upper()
        for item in evidence
        if clean_text(item.status)
    }

    blocking = {
        "BLOCKED",
        "INVALID",
        "INVALIDATED",
    }

    ready = {
        "READY",
        "VALIDATED",
        "CORRECT",
        "SYNTHESIZED",
    }

    has_blocking = bool(statuses.intersection(blocking))
    has_ready = bool(statuses.intersection(ready))

    return has_blocking and has_ready


# ============================================================
# PROVENANCE AGGREGATION
# ============================================================

def d16_aggregate_provenance(
    evidence: List[D16ReconciliationEvidence],
) -> ProvenanceStatus:

    if not evidence:
        return ProvenanceStatus.MISSING

    states = [
        validate_d16_provenance(item.provenance)
        for item in evidence
    ]

    if any(
        state == ProvenanceStatus.INVALID
        for state in states
    ):
        return ProvenanceStatus.INVALID

    if all(
        state == ProvenanceStatus.VERIFIED
        for state in states
    ):
        return ProvenanceStatus.VERIFIED

    return ProvenanceStatus.PARTIAL


# ============================================================
# D16 RECONCILER
# ============================================================

class D16UpstreamReconciler:

    def reconcile(
        self,
        upstream_inputs: List[D16UpstreamInput],
        market_identity: Optional[str] = None,
    ) -> D16UpstreamReconciliation:

        if not upstream_inputs:
            return D16UpstreamReconciliation(
                status=D16ReconciliationStatus.UNDETERMINED,
                provenance_status=ProvenanceStatus.MISSING,
            )

        evidence: List[D16ReconciliationEvidence] = []

        for item in upstream_inputs:

            if not clean_text(item.layer):
                continue

            if not clean_text(item.engine):
                continue

            if not clean_text(item.version):
                continue

            if not clean_text(item.source_id):
                continue

            payload = dict(item.payload)

            identity = d16_extract_market_identity(payload)

            direction = d16_extract_direction(payload)

            scenario = d16_extract_scenario(payload)

            status = d16_extract_status(item)

            provenance_status = validate_d16_provenance(
                item.provenance
            )

            if provenance_status == ProvenanceStatus.INVALID:
                disposition = (
                    D16EvidenceDisposition.CONTRADICTORY
                )
            elif status in {
                "BLOCKED",
                "INVALID",
                "INVALIDATED",
            }:
                disposition = (
                    D16EvidenceDisposition.CONTRADICTORY
                )
            else:
                disposition = (
                    D16EvidenceDisposition.SUPPORTING
                )

            evidence.append(
                D16ReconciliationEvidence(
                    layer=item.layer,
                    engine=item.engine,
                    version=item.version,
                    source_id=item.source_id,
                    status=status,
                    market_identity=identity,
                    direction=direction,
                    scenario=scenario,
                    observed_at=item.observed_at,
                    disposition=disposition,
                    provenance=item.provenance,
                    payload=deep_copy(payload),
                )
            )

        if not evidence:
            return D16UpstreamReconciliation(
                status=D16ReconciliationStatus.BLOCKED,
                provenance_status=ProvenanceStatus.INVALID,
            )

        conflicts: List[D16ConflictType] = []

        if d16_detect_identity_conflict(evidence):
            conflicts.append(
                D16ConflictType.IDENTITY_CONFLICT
            )

        if d16_detect_direction_conflict(evidence):
            conflicts.append(
                D16ConflictType.DIRECTION_CONFLICT
            )

        if d16_detect_scenario_conflict(evidence):
            conflicts.append(
                D16ConflictType.SCENARIO_CONFLICT
            )

        if d16_detect_status_conflict(evidence):
            conflicts.append(
                D16ConflictType.STATUS_CONFLICT
            )

        if not d16_validate_temporal_order(evidence):
            conflicts.append(
                D16ConflictType.TEMPORAL_CONFLICT
            )

        provenance_status = d16_aggregate_provenance(
            evidence
        )

        if provenance_status == ProvenanceStatus.INVALID:
            conflicts.append(
                D16ConflictType.PROVENANCE_CONFLICT
            )

        supporting_layers = tuple(
            dict.fromkeys(
                item.layer
                for item in evidence
                if item.disposition
                == D16EvidenceDisposition.SUPPORTING
            )
        )

        contradictory_layers = tuple(
            dict.fromkeys(
                item.layer
                for item in evidence
                if item.disposition
                == D16EvidenceDisposition.CONTRADICTORY
            )
        )

        identities = [
            clean_text(item.market_identity)
            for item in evidence
            if clean_text(item.market_identity)
        ]

        directions = tuple(
            dict.fromkeys(
                clean_text(item.direction).upper()
                for item in evidence
                if clean_text(item.direction)
            )
        )

        scenarios = tuple(
            dict.fromkeys(
                clean_text(item.scenario)
                for item in evidence
                if clean_text(item.scenario)
            )
        )

        resolved_identity = market_identity

        if not resolved_identity and identities:
            unique_identities = tuple(
                dict.fromkeys(identities)
            )

            if len(unique_identities) == 1:
                resolved_identity = unique_identities[0]

        earliest, latest = d16_temporal_bounds(evidence)

        if D16ConflictType.IDENTITY_CONFLICT in conflicts:
            status = D16ReconciliationStatus.BLOCKED

        elif D16ConflictType.PROVENANCE_CONFLICT in conflicts:
            status = D16ReconciliationStatus.BLOCKED

        elif D16ConflictType.TEMPORAL_CONFLICT in conflicts:
            status = D16ReconciliationStatus.BLOCKED

        elif conflicts:
            status = D16ReconciliationStatus.LIMITED

        elif provenance_status == ProvenanceStatus.PARTIAL:
            status = D16ReconciliationStatus.LIMITED

        else:
            status = D16ReconciliationStatus.READY

        return D16UpstreamReconciliation(
            status=status,
            evidence=evidence,
            supporting_layers=supporting_layers,
            contradictory_layers=contradictory_layers,
            conflicts=tuple(conflicts),
            market_identity=resolved_identity,
            direction_values=directions,
            scenario_values=scenarios,
            earliest_observation=earliest,
            latest_observation=latest,
            provenance_status=provenance_status,
        )


# ============================================================
# CROSS-LAYER INTELLIGENCE EXTRACTION
# ============================================================

def d16_build_cross_layer_observation(
    reconciliation: D16UpstreamReconciliation,
) -> Optional[IntelligenceObservation]:

    if reconciliation.status == (
        D16ReconciliationStatus.BLOCKED
    ):
        return None

    layers = reconciliation.supporting_layers

    source_ids = tuple(
        dict.fromkeys(
            item.source_id
            for item in reconciliation.evidence
        )
    )

    if not layers or not source_ids:
        return None

    statements: List[str] = []

    if len(layers) >= 2:
        statements.append(
            "Multiple validated upstream layers are available "
            "for cross-layer intelligence synthesis."
        )

    if reconciliation.direction_values:
        statements.append(
            "Observed directional context is explicitly "
            "represented by upstream evidence."
        )

    if reconciliation.scenario_values:
        statements.append(
            "Scenario context is explicitly represented by "
            "upstream evidence."
        )

    if reconciliation.conflicts:
        statements.append(
            "Cross-layer evidence contains explicit conflicts "
            "that remain preserved for interpretation."
        )

    if not statements:
        return None

    statement = " ".join(statements)

    observed_at = reconciliation.latest_observation

    observation_id = build_d16_observation_id(
        IntelligenceType.CROSS_LAYER,
        source_ids,
        observed_at,
    )

    disposition = (
        IntelligenceDisposition.SYNTHESIZED
        if reconciliation.status
        == D16ReconciliationStatus.READY
        else IntelligenceDisposition.LIMITED
    )

    return IntelligenceObservation(
        observation_id=observation_id,
        intelligence_type=IntelligenceType.CROSS_LAYER,
        disposition=disposition,
        statement=statement,
        supporting_layers=layers,
        source_ids=source_ids,
        provenance_status=reconciliation.provenance_status,
        observed_at=observed_at,
        metadata={
            "conflicts": [
                item.value
                for item in reconciliation.conflicts
            ],
            "direction_values": list(
                reconciliation.direction_values
            ),
            "scenario_values": list(
                reconciliation.scenario_values
            ),
        },
    )


# ============================================================
# FULL PART-2 SYNTHESIS
# ============================================================

def d16_reconcile_and_synthesize(
    upstream_inputs: List[D16UpstreamInput],
    market_identity: Optional[str] = None,
) -> Tuple[
    D16UpstreamReconciliation,
    Optional[IntelligenceObservation],
]:

    reconciler = D16UpstreamReconciler()

    reconciliation = reconciler.reconcile(
        upstream_inputs=upstream_inputs,
        market_identity=market_identity,
    )

    observation = d16_build_cross_layer_observation(
        reconciliation
    )

    return reconciliation, observation


# ============================================================
# PART-2 CONTRACT
# ============================================================

@dataclass(frozen=True)
class D16ReconciliationContract:

    engine_name: str
    engine_version: str

    reconciliation_status: D16ReconciliationStatus

    reconciliation: Mapping[str, Any]

    decision_authority: bool
    execution_authority: bool
    probability_authority: bool

    generated_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "engine_name": self.engine_name,
            "engine_version": self.engine_version,
            "reconciliation_status": (
                self.reconciliation_status.value
            ),
            "reconciliation": deep_copy(
                dict(self.reconciliation)
            ),
            "decision_authority": self.decision_authority,
            "execution_authority": self.execution_authority,
            "probability_authority": self.probability_authority,
            "generated_at": self.generated_at.isoformat(),
        }


def build_d16_reconciliation_contract(
    reconciliation: D16UpstreamReconciliation,
) -> D16ReconciliationContract:

    return D16ReconciliationContract(
        engine_name=D16_PART2_NAME,
        engine_version=D16_PART2_VERSION,
        reconciliation_status=reconciliation.status,
        reconciliation=reconciliation.to_dict(),
        decision_authority=False,
        execution_authority=False,
        probability_authority=False,
        generated_at=utc_now(),
    )


def validate_d16_reconciliation_contract(
    contract: D16ReconciliationContract,
) -> bool:

    if contract.engine_name != D16_PART2_NAME:
        return False

    if contract.engine_version != D16_PART2_VERSION:
        return False

    if contract.decision_authority:
        return False

    if contract.execution_authority:
        return False

    if contract.probability_authority:
        return False

    if not isinstance(
        contract.reconciliation,
        Mapping,
    ):
        return False

    return True


# ============================================================
# PART-2 SELF TEST
# ============================================================

def d16_part2_self_check() -> Dict[str, bool]:

    observed = utc_now()

    p1 = D16Provenance(
        source_layer="D13",
        source_engine="D13_Decision",
        source_version="V6-CAS-1.0",
        source_id="D13-TEST-001",
        observed_at=observed,
        received_at=observed,
        provenance_status=ProvenanceStatus.VERIFIED,
    )

    p2 = D16Provenance(
        source_layer="D14",
        source_engine="D14_DecisionValidation",
        source_version="V6-CAS-1.0",
        source_id="D14-TEST-001",
        observed_at=observed,
        received_at=observed,
        provenance_status=ProvenanceStatus.VERIFIED,
    )

    inputs = [
        D16UpstreamInput(
            layer="D13",
            engine="D13_Decision",
            version="V6-CAS-1.0",
            source_id="D13-TEST-001",
            status="READY",
            payload={
                "market_identity": "TEST-MARKET",
                "direction": "UP",
            },
            provenance=p1,
            observed_at=observed,
        ),
        D16UpstreamInput(
            layer="D14",
            engine="D14_DecisionValidation",
            version="V6-CAS-1.0",
            source_id="D14-TEST-001",
            status="VALIDATED",
            payload={
                "market_identity": "TEST-MARKET",
                "direction": "UP",
            },
            provenance=p2,
            observed_at=observed,
        ),
    ]

    reconciliation, observation = (
        d16_reconcile_and_synthesize(
            inputs,
            market_identity="TEST-MARKET",
        )
    )

    contract = build_d16_reconciliation_contract(
        reconciliation
    )

    checks = {
        "reconciliation_created": (
            reconciliation is not None
        ),
        "reconciliation_ready": (
            reconciliation.status
            == D16ReconciliationStatus.READY
        ),
        "supporting_layers_detected": (
            len(reconciliation.supporting_layers) == 2
        ),
        "identity_consistent": (
            D16ConflictType.IDENTITY_CONFLICT
            not in reconciliation.conflicts
        ),
        "direction_consistent": (
            D16ConflictType.DIRECTION_CONFLICT
            not in reconciliation.conflicts
        ),
        "temporal_valid": (
            D16ConflictType.TEMPORAL_CONFLICT
            not in reconciliation.conflicts
        ),
        "provenance_verified": (
            reconciliation.provenance_status
            == ProvenanceStatus.VERIFIED
        ),
        "cross_layer_observation_created": (
            observation is not None
        ),
        "decision_authority_false": (
            contract.decision_authority is False
        ),
        "execution_authority_false": (
            contract.execution_authority is False
        ),
        "probability_authority_false": (
            contract.probability_authority is False
        ),
        "contract_valid": (
            validate_d16_reconciliation_contract(
                contract
            )
        ),
    }

    return checks
# ============================================================
# D16 - PART 3
# CROSS-LAYER RELATIONSHIP & INTELLIGENCE SYNTHESIS
# ============================================================

D16_PART3_NAME = "D16_CrossLayerSynthesis"
D16_PART3_VERSION = "V6-CAS-1.0"


# ============================================================
# ENUMS
# ============================================================

class D16RelationshipType(str, Enum):
    STATE_TRANSITION = "STATE_TRANSITION"
    STATE_SCENARIO = "STATE_SCENARIO"
    TRANSITION_SCENARIO = "TRANSITION_SCENARIO"
    DECISION_VALIDATION = "DECISION_VALIDATION"
    VALIDATION_LEARNING = "VALIDATION_LEARNING"
    DECISION_LEARNING = "DECISION_LEARNING"
    STATE_VALIDATION = "STATE_VALIDATION"
    CROSS_LAYER = "CROSS_LAYER"


class D16RelationshipDisposition(str, Enum):
    ALIGNED = "ALIGNED"
    PARTIALLY_ALIGNED = "PARTIALLY_ALIGNED"
    CONFLICTED = "CONFLICTED"
    INSUFFICIENT = "INSUFFICIENT"


class D16SynthesisStatus(str, Enum):
    READY = "READY"
    LIMITED = "LIMITED"
    BLOCKED = "BLOCKED"
    UNDETERMINED = "UNDETERMINED"


# ============================================================
# LAYER RECORD
# ============================================================

@dataclass
class D16LayerRecord:
    layer: str
    source_id: str
    status: str

    direction: Optional[str] = None
    market_state: Optional[str] = None
    transition: Optional[str] = None
    scenario: Optional[str] = None

    validation_result: Optional[str] = None
    learning_disposition: Optional[str] = None

    market_identity: Optional[str] = None
    observed_at: Optional[datetime] = None

    provenance_status: ProvenanceStatus = (
        ProvenanceStatus.VERIFIED
    )

    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "layer": self.layer,
            "source_id": self.source_id,
            "status": self.status,
            "direction": self.direction,
            "market_state": self.market_state,
            "transition": self.transition,
            "scenario": self.scenario,
            "validation_result": self.validation_result,
            "learning_disposition": self.learning_disposition,
            "market_identity": self.market_identity,
            "observed_at": (
                self.observed_at.isoformat()
                if self.observed_at else None
            ),
            "provenance_status": (
                self.provenance_status.value
            ),
            "payload": deep_copy(self.payload),
        }


# ============================================================
# RELATIONSHIP RECORD
# ============================================================

@dataclass
class D16RelationshipRecord:
    relationship_type: D16RelationshipType

    source_layer: str
    target_layer: str

    disposition: D16RelationshipDisposition

    source_id: str
    target_id: str

    statement: str

    source_value: Optional[str] = None
    target_value: Optional[str] = None

    observed_at: Optional[datetime] = None

    provenance_status: ProvenanceStatus = (
        ProvenanceStatus.VERIFIED
    )

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "relationship_type": (
                self.relationship_type.value
            ),
            "source_layer": self.source_layer,
            "target_layer": self.target_layer,
            "disposition": self.disposition.value,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "statement": self.statement,
            "source_value": self.source_value,
            "target_value": self.target_value,
            "observed_at": (
                self.observed_at.isoformat()
                if self.observed_at else None
            ),
            "provenance_status": (
                self.provenance_status.value
            ),
            "metadata": deep_copy(self.metadata),
        }


# ============================================================
# SYNTHESIS RESULT
# ============================================================

@dataclass
class D16CrossLayerSynthesis:
    status: D16SynthesisStatus

    layers: List[D16LayerRecord] = field(
        default_factory=list
    )

    relationships: List[D16RelationshipRecord] = field(
        default_factory=list
    )

    aligned_relationships: int = 0
    partial_relationships: int = 0
    conflicted_relationships: int = 0

    market_identity: Optional[str] = None

    earliest_observation: Optional[datetime] = None
    latest_observation: Optional[datetime] = None

    provenance_status: ProvenanceStatus = (
        ProvenanceStatus.VERIFIED
    )

    intelligence_statements: Tuple[str, ...] = (
        field(default_factory=tuple)
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "layers": [
                item.to_dict()
                for item in self.layers
            ],
            "relationships": [
                item.to_dict()
                for item in self.relationships
            ],
            "aligned_relationships": (
                self.aligned_relationships
            ),
            "partial_relationships": (
                self.partial_relationships
            ),
            "conflicted_relationships": (
                self.conflicted_relationships
            ),
            "market_identity": self.market_identity,
            "earliest_observation": (
                self.earliest_observation.isoformat()
                if self.earliest_observation
                else None
            ),
            "latest_observation": (
                self.latest_observation.isoformat()
                if self.latest_observation
                else None
            ),
            "provenance_status": (
                self.provenance_status.value
            ),
            "intelligence_statements": list(
                self.intelligence_statements
            ),
            "metadata": deep_copy(self.metadata),
        }


# ============================================================
# LAYER RECORD BUILDER
# ============================================================

def d16_build_layer_record(
    item: D16UpstreamInput,
) -> D16LayerRecord:

    payload = dict(item.payload)

    return D16LayerRecord(
        layer=clean_text(item.layer),
        source_id=clean_text(item.source_id),
        status=d16_extract_status(item),

        direction=d16_extract_direction(
            payload
        ),

        market_state=clean_text(
            payload.get("market_state")
        ) or None,

        transition=clean_text(
            payload.get("transition")
        ) or None,

        scenario=d16_extract_scenario(
            payload
        ),

        validation_result=clean_text(
            payload.get("validation_result")
        ) or None,

        learning_disposition=clean_text(
            payload.get("learning_disposition")
        ) or None,

        market_identity=d16_extract_market_identity(
            payload
        ),

        observed_at=item.observed_at,

        provenance_status=validate_d16_provenance(
            item.provenance
        ),

        payload=deep_copy(payload),
    )


# ============================================================
# ============================================================
# D16 PART-3 — SEMANTIC VALUE NORMALIZATION
# ============================================================

def d16_normalize_value(value: Any) -> Optional[str]:
    """
    Normalize only values that have a stable semantic meaning.

    IMPORTANT:
    Values from different relationship dimensions must NOT
    be compared as if they belong to the same domain.
    """

    if value is None:
        return None

    text = clean_text(value)

    if not text:
        return None

    normalized = text.upper()

    aliases = {
        "BULLISH": "UP",
        "BEARISH": "DOWN",
        "LONG": "UP",
        "SHORT": "DOWN",
        "CALL": "UP",
        "PUT": "DOWN",
    }

    return aliases.get(
        normalized,
        normalized,
    )


# ============================================================
# MARKET DIRECTION / STRUCTURAL FAMILY
# ============================================================

def _d16_market_family(
    value: Any,
) -> Optional[str]:
    """
    Extract a broad semantic market family.

    This is NOT a score and does not create a decision.
    It is used only to determine whether two upstream
    observations are semantically compatible.
    """

    normalized = d16_normalize_value(value)

    if normalized is None:
        return None

    bullish_tokens = (
        "BULLISH",
        "UP",
        "LONG",
        "ACCUMULATION",
        "EXPANSION",
        "BULL",
    )

    bearish_tokens = (
        "BEARISH",
        "DOWN",
        "SHORT",
        "DISTRIBUTION",
        "BEAR",
    )

    range_tokens = (
        "RANGE",
        "ROTATION",
        "CONTRACTION",
    )

    chaos_tokens = (
        "CHAOS",
    )

    for token in bullish_tokens:
        if token in normalized:
            return "BULLISH"

    for token in bearish_tokens:
        if token in normalized:
            return "BEARISH"

    for token in range_tokens:
        if token in normalized:
            return "RANGE"

    for token in chaos_tokens:
        if token in normalized:
            return "CHAOS"

    return None


# ============================================================
# TRANSITION FAMILY
# ============================================================

def _d16_transition_family(
    value: Any,
) -> Optional[str]:
    """
    Map D11 transition semantics into a broad structural family.
    """

    normalized = d16_normalize_value(value)

    if normalized is None:
        return None

    bullish = (
        "BULLISH_DEVELOPMENT",
        "BULLISH_REVERSAL",
        "ACCUMULATION_TO_EXPANSION",
    )

    bearish = (
        "BEARISH_DEVELOPMENT",
        "BEARISH_REVERSAL",
        "DISTRIBUTION_TO_EXPANSION",
    )

    range_related = (
        "RANGE_EXPANSION",
        "RANGE_CONTRACTION",
        "ROTATION",
    )

    chaos_related = (
        "CHAOS_TRANSITION",
    )

    if normalized in bullish:
        return "BULLISH"

    if normalized in bearish:
        return "BEARISH"

    if normalized in range_related:
        return "RANGE"

    if normalized in chaos_related:
        return "CHAOS"

    return None


# ============================================================
# SCENARIO FAMILY
# ============================================================

def _d16_scenario_family(
    value: Any,
) -> Optional[str]:
    """
    Extract only explicit directional/structural meaning from
    a scenario label.

    Generic labels such as BASELINE are intentionally left
    without a directional family.
    """

    normalized = d16_normalize_value(value)

    if normalized is None:
        return None

    if "BULLISH" in normalized:
        return "BULLISH"

    if "BEARISH" in normalized:
        return "BEARISH"

    if "UPSIDE" in normalized:
        return "BULLISH"

    if "DOWNSIDE" in normalized:
        return "BEARISH"

    if "ACCUMULATION" in normalized:
        return "BULLISH"

    if "DISTRIBUTION" in normalized:
        return "BEARISH"

    if "RANGE" in normalized:
        return "RANGE"

    if "ROTATION" in normalized:
        return "RANGE"

    if "CHAOS" in normalized:
        return "CHAOS"

    return None


# ============================================================
# VALIDATION SEMANTICS
# ============================================================

def _d16_validation_disposition(
    value: Any,
) -> Optional[str]:

    normalized = d16_normalize_value(value)

    if normalized is None:
        return None

    if normalized == "CORRECT":
        return "CONFIRMED"

    if normalized == "INCORRECT":
        return "REJECTED"

    if normalized == "PARTIAL":
        return "PARTIAL"

    if normalized == "UNDETERMINED":
        return "UNDETERMINED"

    return None


# ============================================================
# LEARNING SEMANTICS
# ============================================================

def _d16_learning_disposition(
    value: Any,
) -> Optional[str]:

    normalized = d16_normalize_value(value)

    if normalized is None:
        return None

    if normalized in {
        "RETAIN",
        "KEEP",
        "PRESERVE",
    }:
        return "RETAIN"

    if normalized in {
        "REJECT",
        "DISCARD",
        "INVALIDATE",
        "EXCLUDE",
    }:
        return "REJECT"

    if normalized in {
        "REVIEW",
        "REFINE",
        "REASSESS",
        "RECALIBRATE",
    }:
        return "REVIEW"

    return None


# ============================================================
# FAMILY COMPATIBILITY
# ============================================================

def _d16_compare_families(
    source_family: Optional[str],
    target_family: Optional[str],
) -> D16RelationshipDisposition:

    if (
        source_family is None
        or target_family is None
    ):
        return D16RelationshipDisposition.INSUFFICIENT

    if source_family == target_family:
        return D16RelationshipDisposition.ALIGNED

    opposite_pairs = {
        ("BULLISH", "BEARISH"),
        ("BEARISH", "BULLISH"),
    }

    if (
        source_family,
        target_family,
    ) in opposite_pairs:
        return D16RelationshipDisposition.CONFLICTED

    return D16RelationshipDisposition.PARTIALLY_ALIGNED


# ============================================================
# RELATIONSHIP-SPECIFIC SEMANTIC COMPARISON
# ============================================================

def _d16_semantic_relationship(
    relationship_type: D16RelationshipType,
    source_value: Any,
    target_value: Any,
) -> Tuple[
    D16RelationshipDisposition,
    str,
]:

    if (
        source_value is None
        or target_value is None
    ):
        return (
            D16RelationshipDisposition.INSUFFICIENT,
            "One or both relationship values are unavailable.",
        )

    # --------------------------------------------------------
    # D10 STATE -> D11 TRANSITION
    # --------------------------------------------------------

    if (
        relationship_type
        == D16RelationshipType.STATE_TRANSITION
    ):

        disposition = _d16_compare_families(
            _d16_market_family(source_value),
            _d16_transition_family(target_value),
        )

        return (
            disposition,
            "Market-state family compared with transition family.",
        )

    # --------------------------------------------------------
    # D10 STATE -> D12 SCENARIO
    # --------------------------------------------------------

    if (
        relationship_type
        == D16RelationshipType.STATE_SCENARIO
    ):

        disposition = _d16_compare_families(
            _d16_market_family(source_value),
            _d16_scenario_family(target_value),
        )

        return (
            disposition,
            "Market-state family compared with explicit scenario family.",
        )

    # --------------------------------------------------------
    # D11 TRANSITION -> D12 SCENARIO
    # --------------------------------------------------------

    if (
        relationship_type
        == D16RelationshipType.TRANSITION_SCENARIO
    ):

        disposition = _d16_compare_families(
            _d16_transition_family(source_value),
            _d16_scenario_family(target_value),
        )

        return (
            disposition,
            "Transition family compared with explicit scenario family.",
        )

    # --------------------------------------------------------
    # D13 DECISION -> D14 VALIDATION
    # --------------------------------------------------------

    if (
        relationship_type
        == D16RelationshipType.DECISION_VALIDATION
    ):

        validation = _d16_validation_disposition(
            target_value
        )

        if validation == "CONFIRMED":
            return (
                D16RelationshipDisposition.ALIGNED,
                "Validation result confirms the upstream decision.",
            )

        if validation == "REJECTED":
            return (
                D16RelationshipDisposition.CONFLICTED,
                "Validation result rejects the upstream decision.",
            )

        if validation == "PARTIAL":
            return (
                D16RelationshipDisposition.PARTIALLY_ALIGNED,
                "Validation is only partial; full decision confirmation is unavailable.",
            )

        if validation == "UNDETERMINED":
            return (
                D16RelationshipDisposition.INSUFFICIENT,
                "Validation is undetermined.",
            )

        return (
            D16RelationshipDisposition.INSUFFICIENT,
            "Validation result has no recognized semantic meaning.",
        )

    # --------------------------------------------------------
    # D14 VALIDATION -> D15 LEARNING
    # --------------------------------------------------------

    if (
        relationship_type
        == D16RelationshipType.VALIDATION_LEARNING
    ):

        validation = _d16_validation_disposition(
            source_value
        )

        learning = _d16_learning_disposition(
            target_value
        )

        if (
            validation == "CONFIRMED"
            and learning == "RETAIN"
        ):
            return (
                D16RelationshipDisposition.ALIGNED,
                "Correct validation is consistent with retaining the learned observation.",
            )

        if (
            validation == "INCORRECT"
            and learning == "REJECT"
        ):
            return (
                D16RelationshipDisposition.ALIGNED,
                "Incorrect validation is consistent with rejecting the learned observation.",
            )

        if (
            validation == "PARTIAL"
            and learning == "REVIEW"
        ):
            return (
                D16RelationshipDisposition.ALIGNED,
                "Partial validation is consistent with review/refinement learning.",
            )

        if (
            validation == "CONFIRMED"
            and learning == "REJECT"
        ):
            return (
                D16RelationshipDisposition.CONFLICTED,
                "Correct validation conflicts with rejecting the learned observation.",
            )

        if (
            validation == "INCORRECT"
            and learning == "RETAIN"
        ):
            return (
                D16RelationshipDisposition.CONFLICTED,
                "Incorrect validation conflicts with retaining the learned observation.",
            )

        if (
            validation is not None
            and learning is not None
        ):
            return (
                D16RelationshipDisposition.PARTIALLY_ALIGNED,
                "Validation and learning dispositions are present but not fully compatible.",
            )

        return (
            D16RelationshipDisposition.INSUFFICIENT,
            "Validation or learning semantics are unavailable.",
        )

    # --------------------------------------------------------
    # D13 DECISION -> D15 LEARNING
    # --------------------------------------------------------

    if (
        relationship_type
        == D16RelationshipType.DECISION_LEARNING
    ):

        # Learning disposition does not itself encode direction.
        # Therefore direction cannot be treated as equal to RETAIN,
        # REJECT, REVIEW, etc.
        return (
            D16RelationshipDisposition.INSUFFICIENT,
            "Learning disposition does not independently encode decision direction.",
        )

    # --------------------------------------------------------
    # D10 STATE -> D14 VALIDATION
    # --------------------------------------------------------

    if (
        relationship_type
        == D16RelationshipType.STATE_VALIDATION
    ):

        # A validation result alone does not prove that the specific
        # D10 market state was validated. Explicit state linkage is
        # required before declaring alignment.
        return (
            D16RelationshipDisposition.INSUFFICIENT,
            "Validation result alone does not establish validation of the specific market state.",
        )

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    if (
        d16_normalize_value(source_value)
        == d16_normalize_value(target_value)
    ):
        return (
            D16RelationshipDisposition.ALIGNED,
            "Values have equivalent normalized semantics.",
        )

    return (
        D16RelationshipDisposition.INSUFFICIENT,
        "No relationship-specific semantic rule is available.",
    )


# ============================================================
# RELATIONSHIP BUILDER
# ============================================================

def d16_build_relationship(
    relationship_type: D16RelationshipType,
    source: D16LayerRecord,
    target: D16LayerRecord,
    source_value: Any,
    target_value: Any,
) -> D16RelationshipRecord:

    disposition, reason = _d16_semantic_relationship(
        relationship_type=relationship_type,
        source_value=source_value,
        target_value=target_value,
    )

    source_normalized = d16_normalize_value(
        source_value
    )

    target_normalized = d16_normalize_value(
        target_value
    )

    provenance_status = (
        ProvenanceStatus.VERIFIED
        if (
            source.provenance_status
            == ProvenanceStatus.VERIFIED
            and
            target.provenance_status
            == ProvenanceStatus.VERIFIED
        )
        else ProvenanceStatus.UNVERIFIED
    )

    return D16RelationshipRecord(
        relationship_type=relationship_type,

        source_layer=source.layer,
        target_layer=target.layer,

        disposition=disposition,

        source_id=source.source_id,
        target_id=target.source_id,

        statement=(
            f"{source.layer} -> "
            f"{target.layer}: "
            f"{reason}"
        ),

        source_value=source_value,
        target_value=target_value,

        observed_at=min(
            source.observed_at,
            target.observed_at,
        ),

        provenance_status=provenance_status,

        metadata={
            "comparison_mode": "SEMANTIC",
            "relationship_type": (
                relationship_type.value
            ),
            "source_normalized": (
                source_normalized
            ),
            "target_normalized": (
                target_normalized
            ),
            "semantic_reason": reason,
        },
    )
# ============================================================
# RELATIONSHIP PAIRS
# ============================================================

D16_LAYER_RELATIONSHIPS = (
    (
        "D10",
        "D11",
        D16RelationshipType.STATE_TRANSITION,
        "market_state",
        "transition",
    ),
    (
        "D10",
        "D12",
        D16RelationshipType.STATE_SCENARIO,
        "market_state",
        "scenario",
    ),
    (
        "D11",
        "D12",
        D16RelationshipType.TRANSITION_SCENARIO,
        "transition",
        "scenario",
    ),
    (
        "D13",
        "D14",
        D16RelationshipType.DECISION_VALIDATION,
        "direction",
        "validation_result",
    ),
    (
        "D14",
        "D15",
        D16RelationshipType.VALIDATION_LEARNING,
        "validation_result",
        "learning_disposition",
    ),
    (
        "D13",
        "D15",
        D16RelationshipType.DECISION_LEARNING,
        "direction",
        "learning_disposition",
    ),
    (
        "D10",
        "D14",
        D16RelationshipType.STATE_VALIDATION,
        "market_state",
        "validation_result",
    ),
)


# ============================================================
# RELATIONSHIP SYNTHESIZER
# ============================================================

class D16CrossLayerRelationshipEngine:

    def synthesize(
        self,
        layer_records: List[D16LayerRecord],
    ) -> D16CrossLayerSynthesis:

        if not layer_records:

            return D16CrossLayerSynthesis(
                status=D16SynthesisStatus.UNDETERMINED,
                provenance_status=(
                    ProvenanceStatus.MISSING
                ),
            )

        relationships: List[
            D16RelationshipRecord
        ] = []

        by_layer: Dict[str, List[D16LayerRecord]] = {}

        for record in layer_records:

            by_layer.setdefault(
                record.layer.upper(),
                [],
            ).append(record)

        for (
            source_layer,
            target_layer,
            relationship_type,
            source_field,
            target_field,
        ) in D16_LAYER_RELATIONSHIPS:

            sources = by_layer.get(
                source_layer,
                [],
            )

            targets = by_layer.get(
                target_layer,
                [],
            )

            for source in sources:

                for target in targets:

                    if (
                        source.market_identity
                        and target.market_identity
                        and source.market_identity
                        != target.market_identity
                    ):
                        continue

                    source_value = getattr(
                        source,
                        source_field,
                        None,
                    )

                    target_value = getattr(
                        target,
                        target_field,
                        None,
                    )

                    relationship = (
                        d16_build_relationship(
                            source=source,
                            target=target,
                            relationship_type=(
                                relationship_type
                            ),
                            source_value=source_value,
                            target_value=target_value,
                        )
                    )

                    relationships.append(
                        relationship
                    )

        aligned = sum(
            item.disposition
            == D16RelationshipDisposition.ALIGNED
            for item in relationships
        )

        partial = sum(
            item.disposition
            == D16RelationshipDisposition.PARTIALLY_ALIGNED
            for item in relationships
        )

        conflicted = sum(
            item.disposition
            == D16RelationshipDisposition.CONFLICTED
            for item in relationships
        )

        provenance_states = [
            item.provenance_status
            for item in layer_records
        ]

        if ProvenanceStatus.INVALID in provenance_states:

            provenance_status = (
                ProvenanceStatus.INVALID
            )

        elif all(
            item == ProvenanceStatus.VERIFIED
            for item in provenance_states
        ):

            provenance_status = (
                ProvenanceStatus.VERIFIED
            )

        else:

            provenance_status = (
                ProvenanceStatus.PARTIAL
            )

        timestamps = [
            item.observed_at
            for item in layer_records
            if item.observed_at is not None
        ]

        earliest = (
            min(timestamps)
            if timestamps
            else None
        )

        latest = (
            max(timestamps)
            if timestamps
            else None
        )

        identities = {
            clean_text(item.market_identity)
            for item in layer_records
            if clean_text(item.market_identity)
        }

        market_identity = (
            next(iter(identities))
            if len(identities) == 1
            else None
        )

        if provenance_status == ProvenanceStatus.INVALID:

            status = D16SynthesisStatus.BLOCKED

        elif conflicted > 0:

            status = D16SynthesisStatus.LIMITED

        elif not relationships:

            status = D16SynthesisStatus.LIMITED

        elif provenance_status == ProvenanceStatus.PARTIAL:

            status = D16SynthesisStatus.LIMITED

        else:

            status = D16SynthesisStatus.READY

        statements = (
            d16_generate_synthesis_statements(
                relationships
            )
        )

        return D16CrossLayerSynthesis(
            status=status,
            layers=list(layer_records),
            relationships=relationships,
            aligned_relationships=aligned,
            partial_relationships=partial,
            conflicted_relationships=conflicted,
            market_identity=market_identity,
            earliest_observation=earliest,
            latest_observation=latest,
            provenance_status=provenance_status,
            intelligence_statements=statements,
        )


# ============================================================
# SYNTHESIS STATEMENTS
# ============================================================

def d16_generate_synthesis_statements(
    relationships: List[D16RelationshipRecord],
) -> Tuple[str, ...]:

    statements: List[str] = []

    aligned_types = [
        item.relationship_type.value
        for item in relationships
        if item.disposition
        == D16RelationshipDisposition.ALIGNED
    ]

    conflict_types = [
        item.relationship_type.value
        for item in relationships
        if item.disposition
        == D16RelationshipDisposition.CONFLICTED
    ]

    if aligned_types:

        statements.append(
            "Explicit upstream relationships show "
            "alignment across validated layers."
        )

    if conflict_types:

        statements.append(
            "Explicit upstream relationships contain "
            "conflicts that remain unresolved."
        )

    if not aligned_types and not conflict_types:

        statements.append(
            "Available upstream layers do not provide "
            "sufficient relationship evidence for a "
            "strong cross-layer synthesis."
        )

    return tuple(
        dict.fromkeys(statements)
    )


# ============================================================
# PART-3 CONTRACT
# ============================================================

@dataclass(frozen=True)
class D16CrossLayerContract:

    engine_name: str
    engine_version: str

    synthesis_status: D16SynthesisStatus

    synthesis: Mapping[str, Any]

    decision_authority: bool
    execution_authority: bool
    probability_authority: bool

    generated_at: datetime

    def to_dict(self) -> Dict[str, Any]:

        return {
            "engine_name": self.engine_name,
            "engine_version": self.engine_version,
            "synthesis_status": (
                self.synthesis_status.value
            ),
            "synthesis": deep_copy(
                dict(self.synthesis)
            ),
            "decision_authority": (
                self.decision_authority
            ),
            "execution_authority": (
                self.execution_authority
            ),
            "probability_authority": (
                self.probability_authority
            ),
            "generated_at": (
                self.generated_at.isoformat()
            ),
        }


def build_d16_cross_layer_contract(
    synthesis: D16CrossLayerSynthesis,
) -> D16CrossLayerContract:

    return D16CrossLayerContract(
        engine_name=D16_PART3_NAME,
        engine_version=D16_PART3_VERSION,
        synthesis_status=synthesis.status,
        synthesis=synthesis.to_dict(),
        decision_authority=False,
        execution_authority=False,
        probability_authority=False,
        generated_at=utc_now(),
    )


def validate_d16_cross_layer_contract(
    contract: D16CrossLayerContract,
) -> bool:

    if contract.engine_name != D16_PART3_NAME:
        return False

    if contract.engine_version != D16_PART3_VERSION:
        return False

    if contract.decision_authority:
        return False

    if contract.execution_authority:
        return False

    if contract.probability_authority:
        return False

    if not isinstance(
        contract.synthesis,
        Mapping,
    ):
        return False

    return True


# ============================================================
# PART-3 SELF TEST
# ============================================================

def d16_part3_self_check() -> Dict[str, bool]:

    observed = utc_now()

    def make_provenance(
        layer: str,
        engine: str,
        source_id: str,
    ) -> D16Provenance:

        return D16Provenance(
            source_layer=layer,
            source_engine=engine,
            source_version="V6-CAS-1.0",
            source_id=source_id,
            observed_at=observed,
            received_at=observed,
            provenance_status=(
                ProvenanceStatus.VERIFIED
            ),
        )

    inputs = [
        D16UpstreamInput(
            layer="D10",
            engine="D10_MarketState",
            version="V6-CAS-1.0",
            source_id="D10-TEST-001",
            status="READY",
            payload={
                "market_identity": "TEST-MARKET",
                "market_state": "BULLISH_EXPANSION",
            },
            provenance=make_provenance(
                "D10",
                "D10_MarketState",
                "D10-TEST-001",
            ),
            observed_at=observed,
        ),
        D16UpstreamInput(
            layer="D13",
            engine="D13_Decision",
            version="V6-CAS-1.0",
            source_id="D13-TEST-001",
            status="READY",
            payload={
                "market_identity": "TEST-MARKET",
                "direction": "UP",
            },
            provenance=make_provenance(
                "D13",
                "D13_Decision",
                "D13-TEST-001",
            ),
            observed_at=observed,
        ),
        D16UpstreamInput(
            layer="D14",
            engine="D14_DecisionValidation",
            version="V6-CAS-1.0",
            source_id="D14-TEST-001",
            status="VALIDATED",
            payload={
                "market_identity": "TEST-MARKET",
                "validation_result": "CORRECT",
            },
            provenance=make_provenance(
                "D14",
                "D14_DecisionValidation",
                "D14-TEST-001",
            ),
            observed_at=observed,
        ),
        D16UpstreamInput(
            layer="D15",
            engine="D15_DecisionLearning",
            version="V6-CAS-1.0",
            source_id="D15-TEST-001",
            status="READY",
            payload={
                "market_identity": "TEST-MARKET",
                "learning_disposition": "RETAIN",
            },
            provenance=make_provenance(
                "D15",
                "D15_DecisionLearning",
                "D15-TEST-001",
            ),
            observed_at=observed,
        ),
    ]

    records = [
        d16_build_layer_record(item)
        for item in inputs
    ]

    engine = D16CrossLayerRelationshipEngine()

    synthesis = engine.synthesize(records)

    contract = build_d16_cross_layer_contract(
        synthesis
    )

    checks = {
        "records_created": (
            len(records) == 4
        ),

        "synthesis_created": (
            synthesis is not None
        ),

        "relationships_created": (
            len(synthesis.relationships) > 0
        ),

        "aligned_relationships_detected": (
            synthesis.aligned_relationships >= 1
        ),

        "provenance_verified": (
            synthesis.provenance_status
            == ProvenanceStatus.VERIFIED
        ),

        "decision_authority_false": (
            contract.decision_authority is False
        ),

        "execution_authority_false": (
            contract.execution_authority is False
        ),

        "probability_authority_false": (
            contract.probability_authority is False
        ),

        "contract_valid": (
            validate_d16_cross_layer_contract(
                contract
            )
        ),
    }

    return checks
# ============================================================
# D16 - PART 4
# FINAL INTELLIGENCE AUTHORITY
# ============================================================
#
# D16 FINAL ROLE:
#   D16 is the final intelligence synthesis layer.
#
#   D13 = Decision Authority
#   D14 = Validation Authority
#   D15 = Learning Authority
#   D16 = Intelligence Synthesis Authority
#
# D16 MUST NOT:
#   - create a new trading decision
#   - modify D13 decision
#   - modify D14 validation
#   - modify D15 learning
#   - execute trades
#   - fabricate probability
#   - fabricate confidence
#   - use future information
#
# FINAL FLOW:
#
#   D1-D15
#      ↓
#   Upstream Reconciliation
#      ↓
#   Cross-Layer Synthesis
#      ↓
#   Final Intelligence Contract
#      ↓
#   D16 Final Intelligence
# ============================================================

D16_PART4_NAME = "D16_FinalIntelligenceAuthority"
D16_PART4_VERSION = "V6-CAS-1.0"


# ============================================================
# FINAL STATUS
# ============================================================

class D16FinalStatus(str, Enum):
    READY = "READY"
    LIMITED = "LIMITED"
    BLOCKED = "BLOCKED"
    UNDETERMINED = "UNDETERMINED"


class D16FinalDisposition(str, Enum):
    FINALIZED = "FINALIZED"
    LIMITED = "LIMITED"
    BLOCKED = "BLOCKED"
    UNDETERMINED = "UNDETERMINED"


# ============================================================
# FINAL INTELLIGENCE SNAPSHOT
# ============================================================

@dataclass(frozen=True)
class D16FinalIntelligenceSnapshot:

    snapshot_id: str

    engine_name: str
    engine_version: str

    status: D16FinalStatus
    disposition: D16FinalDisposition

    market_identity: Optional[str]

    supporting_layers: Tuple[str, ...]
    source_ids: Tuple[str, ...]

    intelligence_statements: Tuple[str, ...]

    aligned_relationships: int
    partial_relationships: int
    conflicted_relationships: int

    provenance_status: ProvenanceStatus

    earliest_observation: Optional[datetime]
    latest_observation: Optional[datetime]

    generated_at: datetime

    decision_authority: bool
    execution_authority: bool
    probability_authority: bool

    metadata: Mapping[str, Any]

    def to_dict(self) -> Dict[str, Any]:

        return {
            "snapshot_id": self.snapshot_id,
            "engine_name": self.engine_name,
            "engine_version": self.engine_version,
            "status": self.status.value,
            "disposition": self.disposition.value,
            "market_identity": self.market_identity,
            "supporting_layers": list(
                self.supporting_layers
            ),
            "source_ids": list(
                self.source_ids
            ),
            "intelligence_statements": list(
                self.intelligence_statements
            ),
            "aligned_relationships": (
                self.aligned_relationships
            ),
            "partial_relationships": (
                self.partial_relationships
            ),
            "conflicted_relationships": (
                self.conflicted_relationships
            ),
            "provenance_status": (
                self.provenance_status.value
            ),
            "earliest_observation": (
                self.earliest_observation.isoformat()
                if self.earliest_observation
                else None
            ),
            "latest_observation": (
                self.latest_observation.isoformat()
                if self.latest_observation
                else None
            ),
            "generated_at": (
                self.generated_at.isoformat()
            ),
            "decision_authority": (
                self.decision_authority
            ),
            "execution_authority": (
                self.execution_authority
            ),
            "probability_authority": (
                self.probability_authority
            ),
            "metadata": deep_copy(
                dict(self.metadata)
            ),
        }


# ============================================================
# SNAPSHOT ID
# ============================================================

def build_d16_final_snapshot_id(
    market_identity: Optional[str],
    source_ids: Tuple[str, ...],
    generated_at: datetime,
) -> str:

    market_part = (
        clean_text(market_identity)
        if market_identity
        else "UNKNOWN_MARKET"
    )

    source_part = "|".join(
        sorted(
            clean_text(item)
            for item in source_ids
            if clean_text(item)
        )
    )

    time_part = generated_at.isoformat()

    return (
        f"D16-FINAL:{market_part}:"
        f"{source_part}:{time_part}"
    )
# ============================================================
# D16 PART-4 — FINAL INTELLIGENCE AUTHORITY
# ============================================================

D16_PART4_NAME = "D16_FinalIntelligenceAuthority"
D16_PART4_VERSION = "V6-CAS-1.0"


# ============================================================
# FINAL AUTHORITY BOUNDARY
# ============================================================

@dataclass(frozen=True)
class D16AuthorityBoundary:

    intelligence_authority: bool = True

    decision_authority: bool = False
    validation_authority: bool = False
    learning_authority: bool = False
    execution_authority: bool = False
    probability_authority: bool = False

    def is_valid(self) -> bool:

        return (
            self.intelligence_authority is True
            and self.decision_authority is False
            and self.validation_authority is False
            and self.learning_authority is False
            and self.execution_authority is False
            and self.probability_authority is False
        )

    def to_dict(self) -> Dict[str, bool]:

        return {
            "intelligence_authority": (
                self.intelligence_authority
            ),
            "decision_authority": (
                self.decision_authority
            ),
            "validation_authority": (
                self.validation_authority
            ),
            "learning_authority": (
                self.learning_authority
            ),
            "execution_authority": (
                self.execution_authority
            ),
            "probability_authority": (
                self.probability_authority
            ),
        }


# ============================================================
# FORBIDDEN OUTPUT SCANNER
# ============================================================

D16_FORBIDDEN_AUTHORITY_FIELDS = frozenset({
    "execute",
    "execution",
    "order",
    "order_size",
    "position_size",
    "stop_loss_authority",
    "take_profit_authority",
    "probability",
    "win_probability",
    "prediction_probability",
    "confidence",
})


def _d16_normalize_field_name(
    value: Any,
) -> str:

    return (
        str(value)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )


def d16_scan_forbidden_authority(
    payload: Any,
    *,
    scan_metadata: bool = False,
) -> bool:
    """
    Detect forbidden operational authority in the
    generated intelligence payload.

    D16 authority declarations are boundary metadata,
    not operational commands.

    Therefore fields such as:

        decision_authority
        execution_authority
        probability_authority
        intelligence_authority

    are not themselves forbidden outputs.
    """

    if payload is None:
        return False

    if isinstance(
        payload,
        (str, int, float, bool),
    ):
        return False

    authority_metadata_fields = {
        "intelligence_authority",
        "decision_authority",
        "validation_authority",
        "learning_authority",
        "execution_authority",
        "probability_authority",
    }

    if isinstance(payload, Mapping):

        for raw_key, value in payload.items():

            key = _d16_normalize_field_name(
                raw_key
            )

            # ------------------------------------------------
            # AUTHORITY METADATA
            # ------------------------------------------------

            if (
                not scan_metadata
                and key in authority_metadata_fields
            ):
                continue

            # ------------------------------------------------
            # EXACT FORBIDDEN FIELDS
            # ------------------------------------------------

            if key in D16_FORBIDDEN_AUTHORITY_FIELDS:
                return True

            # ------------------------------------------------
            # EXPLICIT OPERATIONAL VARIANTS
            # ------------------------------------------------

            if key in {
                "execute_order",
                "place_order",
                "submit_order",
                "send_order",
                "entry_order",
                "exit_order",
                "trade_order",
                "buy_order",
                "sell_order",
                "stop_loss",
                "take_profit",
                "order_quantity",
                "quantity_to_execute",
            }:
                return True

            # ------------------------------------------------
            # RECURSIVE SCAN
            # ------------------------------------------------

            if d16_scan_forbidden_authority(
                value,
                scan_metadata=scan_metadata,
            ):
                return True

        return False

    if isinstance(
        payload,
        (list, tuple, set, frozenset),
    ):

        for item in payload:

            if d16_scan_forbidden_authority(
                item,
                scan_metadata=scan_metadata,
            ):
                return True

        return False

    if is_dataclass(payload):

        try:

            return d16_scan_forbidden_authority(
                asdict(payload),
                scan_metadata=scan_metadata,
            )

        except Exception:

            return False

    return False


# ============================================================
# DECISION PROTECTION
# ============================================================

def d16_extract_decision_without_modifying(
    payload: Mapping[str, Any],
) -> Optional[str]:
    """
    Read-only extraction.

    D16 may preserve upstream decision information
    for provenance/context, but does not create,
    modify, or authorize a decision.
    """

    if not isinstance(
        payload,
        Mapping,
    ):
        return None

    for key in (
        "decision",
        "decision_action",
        "action",
        "original_decision",
    ):

        value = clean_text(
            payload.get(key)
        )

        if value:
            return value

    return None


# ============================================================
# FINAL STATUS RESOLUTION
# ============================================================

def d16_resolve_final_status(
    reconciliation: D16UpstreamReconciliation,
    synthesis: D16CrossLayerSynthesis,
) -> D16FinalStatus:

    if (
        reconciliation.status
        == D16ReconciliationStatus.BLOCKED
    ):
        return D16FinalStatus.BLOCKED

    if (
        synthesis.status
        == D16SynthesisStatus.BLOCKED
    ):
        return D16FinalStatus.BLOCKED

    if (
        reconciliation.provenance_status
        == ProvenanceStatus.INVALID
    ):
        return D16FinalStatus.BLOCKED

    if (
        synthesis.provenance_status
        == ProvenanceStatus.INVALID
    ):
        return D16FinalStatus.BLOCKED

    if (
        reconciliation.status
        == D16ReconciliationStatus.LIMITED
        or
        synthesis.status
        == D16SynthesisStatus.LIMITED
    ):
        return D16FinalStatus.LIMITED

    if (
        reconciliation.status
        == D16ReconciliationStatus.UNDETERMINED
        or
        synthesis.status
        == D16SynthesisStatus.UNDETERMINED
    ):
        return D16FinalStatus.UNDETERMINED

    return D16FinalStatus.READY


def d16_resolve_final_disposition(
    status: D16FinalStatus,
) -> D16FinalDisposition:

    if status == D16FinalStatus.READY:
        return D16FinalDisposition.FINALIZED

    if status == D16FinalStatus.LIMITED:
        return D16FinalDisposition.LIMITED

    if status == D16FinalStatus.BLOCKED:
        return D16FinalDisposition.BLOCKED

    return D16FinalDisposition.UNDETERMINED


# ============================================================
# FINAL SNAPSHOT BUILDER
# ============================================================

def d16_build_final_snapshot(
    reconciliation: D16UpstreamReconciliation,
    synthesis: D16CrossLayerSynthesis,
) -> D16FinalIntelligenceSnapshot:

    generated_at = utc_now()

    status = d16_resolve_final_status(
        reconciliation,
        synthesis,
    )

    disposition = d16_resolve_final_disposition(
        status
    )

    source_ids = tuple(
        dict.fromkeys(
            item.source_id
            for item in reconciliation.evidence
            if clean_text(item.source_id)
        )
    )

    supporting_layers = tuple(
        dict.fromkeys(
            item.layer
            for item in reconciliation.evidence
            if clean_text(item.layer)
        )
    )

    snapshot_id = build_d16_final_snapshot_id(
        reconciliation.market_identity,
        source_ids,
        generated_at,
    )

    boundary = D16AuthorityBoundary()

    statements = tuple(
        dict.fromkeys(
            synthesis.intelligence_statements
        )
    )

    metadata = {
        "part": 4,
        "final_layer": True,

        "source_reconciliation_status": (
            reconciliation.status.value
        ),

        "cross_layer_synthesis_status": (
            synthesis.status.value
        ),

        "conflicts": [
            item.value
            for item in reconciliation.conflicts
        ],

        "authority_boundary": (
            boundary.to_dict()
        ),
    }

    return D16FinalIntelligenceSnapshot(
        snapshot_id=snapshot_id,
        engine_name=D16_ENGINE_NAME,
        engine_version=D16_ENGINE_VERSION,

        status=status,
        disposition=disposition,

        market_identity=(
            reconciliation.market_identity
            or synthesis.market_identity
        ),

        supporting_layers=supporting_layers,
        source_ids=source_ids,

        intelligence_statements=statements,

        aligned_relationships=(
            synthesis.aligned_relationships
        ),

        partial_relationships=(
            synthesis.partial_relationships
        ),

        conflicted_relationships=(
            synthesis.conflicted_relationships
        ),

        provenance_status=(
            synthesis.provenance_status
        ),

        earliest_observation=(
            synthesis.earliest_observation
        ),

        latest_observation=(
            synthesis.latest_observation
        ),

        generated_at=generated_at,

        decision_authority=False,
        execution_authority=False,
        probability_authority=False,

        metadata=metadata,
    )


# ============================================================
# FINAL CONTRACT
# ============================================================

@dataclass(frozen=True)
class D16FinalContract:

    engine_name: str
    engine_version: str

    authority: str

    final_status: D16FinalStatus
    final_disposition: D16FinalDisposition

    snapshot: Mapping[str, Any]

    authority_boundary: Mapping[str, bool]

    decision_authority: bool
    execution_authority: bool
    probability_authority: bool

    generated_at: datetime

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {
            "engine_name": self.engine_name,

            "engine_version": self.engine_version,

            "authority": self.authority,

            "final_status": (
                self.final_status.value
            ),

            "final_disposition": (
                self.final_disposition.value
            ),

            "snapshot": deep_copy(
                dict(self.snapshot)
            ),

            "authority_boundary": deep_copy(
                dict(self.authority_boundary)
            ),

            "decision_authority": (
                self.decision_authority
            ),

            "execution_authority": (
                self.execution_authority
            ),

            "probability_authority": (
                self.probability_authority
            ),

            "generated_at": (
                self.generated_at.isoformat()
            ),
        }


# ============================================================
# FINAL CONTRACT BUILDER
# ============================================================

def build_d16_final_contract(
    snapshot: D16FinalIntelligenceSnapshot,
) -> D16FinalContract:

    boundary = D16AuthorityBoundary()

    return D16FinalContract(
        engine_name=D16_PART4_NAME,
        engine_version=D16_PART4_VERSION,
        authority=D16_AUTHORITY,

        final_status=snapshot.status,
        final_disposition=snapshot.disposition,

        snapshot=snapshot.to_dict(),

        authority_boundary=(
            boundary.to_dict()
        ),

        decision_authority=False,
        execution_authority=False,
        probability_authority=False,

        generated_at=(
            snapshot.generated_at
        ),
    )


# ============================================================
# INTELLIGENCE PAYLOAD VALIDATION
# ============================================================

def d16_validate_intelligence_payload(
    intelligence_statements: Any,
) -> bool:
    """
    Validate only generated intelligence statements.

    Contract metadata and authority declarations are
    not treated as generated operational authority.
    """

    return not d16_scan_forbidden_authority(
        intelligence_statements,
        scan_metadata=False,
    )


# ============================================================
# FINAL CONTRACT VALIDATOR
# ============================================================

def validate_d16_final_contract(
    contract: D16FinalContract,
) -> bool:

    if not isinstance(
        contract,
        D16FinalContract,
    ):
        return False

    # --------------------------------------------------------
    # ENGINE IDENTITY
    # --------------------------------------------------------

    if contract.engine_name != D16_PART4_NAME:
        return False

    if contract.engine_version != D16_PART4_VERSION:
        return False

    if contract.authority != D16_AUTHORITY:
        return False

    # --------------------------------------------------------
    # TOP-LEVEL AUTHORITY
    # --------------------------------------------------------

    if contract.decision_authority is not False:
        return False

    if contract.execution_authority is not False:
        return False

    if contract.probability_authority is not False:
        return False

    # --------------------------------------------------------
    # AUTHORITY BOUNDARY
    # --------------------------------------------------------

    if not isinstance(
        contract.authority_boundary,
        Mapping,
    ):
        return False

    boundary = D16AuthorityBoundary(
        intelligence_authority=bool(
            contract.authority_boundary.get(
                "intelligence_authority",
                False,
            )
        ),

        decision_authority=bool(
            contract.authority_boundary.get(
                "decision_authority",
                True,
            )
        ),

        validation_authority=bool(
            contract.authority_boundary.get(
                "validation_authority",
                True,
            )
        ),

        learning_authority=bool(
            contract.authority_boundary.get(
                "learning_authority",
                True,
            )
        ),

        execution_authority=bool(
            contract.authority_boundary.get(
                "execution_authority",
                True,
            )
        ),

        probability_authority=bool(
            contract.authority_boundary.get(
                "probability_authority",
                True,
            )
        ),
    )

    if not boundary.is_valid():
        return False

    # --------------------------------------------------------
    # SNAPSHOT CONTRACT
    # --------------------------------------------------------

    if not isinstance(
        contract.snapshot,
        Mapping,
    ):
        return False

    snapshot = contract.snapshot

    # Snapshot identity.
    if not clean_text(
        snapshot.get("snapshot_id")
    ):
        return False

    # Snapshot engine identity.
    if (
        snapshot.get("engine_name")
        != D16_ENGINE_NAME
    ):
        return False

    if (
        snapshot.get("engine_version")
        != D16_ENGINE_VERSION
    ):
        return False

    # --------------------------------------------------------
    # SNAPSHOT AUTHORITY
    # --------------------------------------------------------

    if snapshot.get(
        "decision_authority",
        True,
    ) is not False:
        return False

    if snapshot.get(
        "execution_authority",
        True,
    ) is not False:
        return False

    if snapshot.get(
        "probability_authority",
        True,
    ) is not False:
        return False

    # --------------------------------------------------------
    # INTELLIGENCE PAYLOAD
    # --------------------------------------------------------

    intelligence_statements = snapshot.get(
        "intelligence_statements",
        (),
    )

    if not isinstance(
        intelligence_statements,
        (list, tuple),
    ):
        return False

    if not d16_validate_intelligence_payload(
        intelligence_statements
    ):
        return False

    # --------------------------------------------------------
    # AUTHORITY METADATA ITSELF
    # --------------------------------------------------------

    snapshot_boundary = snapshot.get(
        "metadata",
        {},
    )

    if isinstance(
        snapshot_boundary,
        Mapping,
    ):

        embedded_boundary = snapshot_boundary.get(
            "authority_boundary"
        )

        if embedded_boundary is not None:

            if not isinstance(
                embedded_boundary,
                Mapping,
            ):
                return False

            embedded = D16AuthorityBoundary(
                intelligence_authority=bool(
                    embedded_boundary.get(
                        "intelligence_authority",
                        False,
                    )
                ),

                decision_authority=bool(
                    embedded_boundary.get(
                        "decision_authority",
                        True,
                    )
                ),

                validation_authority=bool(
                    embedded_boundary.get(
                        "validation_authority",
                        True,
                    )
                ),

                learning_authority=bool(
                    embedded_boundary.get(
                        "learning_authority",
                        True,
                    )
                ),

                execution_authority=bool(
                    embedded_boundary.get(
                        "execution_authority",
                        True,
                    )
                ),

                probability_authority=bool(
                    embedded_boundary.get(
                        "probability_authority",
                        True,
                    )
                ),
            )

            if not embedded.is_valid():
                return False

    # --------------------------------------------------------
    # GENERATED TIMESTAMP
    # --------------------------------------------------------

    if not isinstance(
        contract.generated_at,
        datetime,
    ):
        return False

    return True


# ============================================================
# FINAL PIPELINE
# ============================================================

class D16FinalIntelligencePipeline:

    def __init__(self) -> None:

        self.reconciler = (
            D16UpstreamReconciler()
        )

        self.relationship_engine = (
            D16CrossLayerRelationshipEngine()
        )

        self._latest_contract: Optional[
            D16FinalContract
        ] = None

        self._history: List[
            D16FinalContract
        ] = []

    def process(
        self,
        upstream_inputs: List[D16UpstreamInput],
        market_identity: Optional[str] = None,
    ) -> D16FinalContract:

        reconciliation = (
            self.reconciler.reconcile(
                upstream_inputs=upstream_inputs,
                market_identity=market_identity,
            )
        )

        layer_records = [
            d16_build_layer_record(item)
            for item in upstream_inputs
        ]

        synthesis = (
            self.relationship_engine.synthesize(
                layer_records
            )
        )

        snapshot = d16_build_final_snapshot(
            reconciliation,
            synthesis,
        )

        contract = build_d16_final_contract(
            snapshot
        )

        self._latest_contract = contract

        self._history.append(
            contract
        )

        return contract

    def latest(
        self,
    ) -> Optional[D16FinalContract]:

        return self._latest_contract

    def history(
        self,
    ) -> List[D16FinalContract]:

        return list(self._history)

    def clear(self) -> None:

        self._latest_contract = None
        self._history.clear()


# ============================================================
# FACTORY
# ============================================================

def create_d16_final_pipeline() -> (
    D16FinalIntelligencePipeline
):

    return D16FinalIntelligencePipeline()


# ============================================================
# COMPLETE D16 PART-4 SELF-CHECK
# ============================================================

def d16_part4_self_check() -> Dict[str, bool]:

    observed = utc_now()

    def provenance(
        layer: str,
        engine: str,
        source_id: str,
    ) -> D16Provenance:

        return D16Provenance(
            source_layer=layer,
            source_engine=engine,
            source_version="V6-CAS-1.0",
            source_id=source_id,
            observed_at=observed,
            received_at=observed,
            provenance_status=(
                ProvenanceStatus.VERIFIED
            ),
        )

    inputs = [

        D16UpstreamInput(
            layer="D10",
            engine="D10_MarketState",
            version="V6-CAS-1.0",
            source_id="D10-FINAL-001",
            status="READY",

            payload={
                "market_identity": "TEST-MARKET",
                "market_state": "BULLISH_EXPANSION",
            },

            provenance=provenance(
                "D10",
                "D10_MarketState",
                "D10-FINAL-001",
            ),

            observed_at=observed,
        ),

        D16UpstreamInput(
            layer="D11",
            engine="D11_DecisionTransition",
            version="V6-CAS-1.0",
            source_id="D11-FINAL-001",
            status="READY",

            payload={
                "market_identity": "TEST-MARKET",
                "transition": (
                    "BULLISH_DEVELOPMENT"
                ),
            },

            provenance=provenance(
                "D11",
                "D11_DecisionTransition",
                "D11-FINAL-001",
            ),

            observed_at=observed,
        ),

        D16UpstreamInput(
            layer="D12",
            engine="D12_FutureScenario",
            version="V6-CAS-1.0",
            source_id="D12-FINAL-001",
            status="READY",

            payload={
                "market_identity": "TEST-MARKET",
                "scenario": "BASELINE",
            },

            provenance=provenance(
                "D12",
                "D12_FutureScenario",
                "D12-FINAL-001",
            ),

            observed_at=observed,
        ),

        D16UpstreamInput(
            layer="D13",
            engine="D13_Decision",
            version="V6-CAS-1.0",
            source_id="D13-FINAL-001",
            status="READY",

            payload={
                "market_identity": "TEST-MARKET",
                "direction": "UP",
            },

            provenance=provenance(
                "D13",
                "D13_Decision",
                "D13-FINAL-001",
            ),

            observed_at=observed,
        ),

        D16UpstreamInput(
            layer="D14",
            engine="D14_DecisionValidation",
            version="V6-CAS-1.0",
            source_id="D14-FINAL-001",
            status="VALIDATED",

            payload={
                "market_identity": "TEST-MARKET",
                "validation_result": "CORRECT",
            },

            provenance=provenance(
                "D14",
                "D14_DecisionValidation",
                "D14-FINAL-001",
            ),

            observed_at=observed,
        ),

        D16UpstreamInput(
            layer="D15",
            engine="D15_DecisionLearning",
            version="V6-CAS-1.0",
            source_id="D15-FINAL-001",
            status="READY",

            payload={
                "market_identity": "TEST-MARKET",
                "learning_disposition": "RETAIN",
            },

            provenance=provenance(
                "D15",
                "D15_DecisionLearning",
                "D15-FINAL-001",
            ),

            observed_at=observed,
        ),
    ]

    pipeline = create_d16_final_pipeline()

    contract = pipeline.process(
        inputs,
        market_identity="TEST-MARKET",
    )

    boundary = D16AuthorityBoundary()

    snapshot = contract.snapshot

    forbidden = d16_scan_forbidden_authority(
        snapshot
    )

    checks = {

        "pipeline_created": (
            pipeline is not None
        ),

        "contract_created": (
            contract is not None
        ),

        "final_status_valid": (
            contract.final_status
            in {
                D16FinalStatus.READY,
                D16FinalStatus.LIMITED,
            }
        ),

        "snapshot_created": (
            bool(
                snapshot.get(
                    "snapshot_id"
                )
            )
        ),

        "all_layers_preserved": (
            len(
                snapshot.get(
                    "supporting_layers",
                    (),
                )
            ) == 6
        ),

        "source_provenance_preserved": (
            len(
                snapshot.get(
                    "source_ids",
                    (),
                )
            ) == 6
        ),

        "intelligence_present": (
            len(
                snapshot.get(
                    "intelligence_statements",
                    (),
                )
            ) > 0
        ),

        "authority_boundary_valid": (
            boundary.is_valid()
        ),

        "decision_authority_false": (
            contract.decision_authority
            is False
        ),

        "execution_authority_false": (
            contract.execution_authority
            is False
        ),

        "probability_authority_false": (
            contract.probability_authority
            is False
        ),

        "no_forbidden_output": (
            not forbidden
        ),

        "contract_valid": (
            validate_d16_final_contract(
                contract
            )
        ),

        "history_created": (
            len(
                pipeline.history()
            ) == 1
        ),

        "latest_available": (
            pipeline.latest()
            is not None
        ),
    }

    return checks


# ============================================================
# DIRECT COMPLETE TEST
# ============================================================

if __name__ == "__main__":

    checks = d16_part4_self_check()

    failed = [
        name
        for name, passed in checks.items()
        if not passed
    ]

    if failed:

        print(
            "D16 PART-4 SELF-TEST: FAIL"
        )

        for name in failed:

            print(
                f"  {name}: FAIL"
            )

    else:

        print(
            "D16 PART-4 SELF-TEST: PASS"
        )

        for name, passed in checks.items():

            print(
                f"  {name}: "
                f"{'PASS' if passed else 'FAIL'}"
            )
# ============================================================
# DIRECT COMPLETE TEST
# ============================================================

if __name__ == "__main__":

    test_groups = [
        ("D16 PART-1 SELF-TEST", d16_part1_self_check),
        ("D16 PART-2 SELF-TEST", d16_part2_self_check),
        ("D16 PART-3 SELF-TEST", d16_part3_self_check),
        ("D16 PART-4 SELF-TEST", d16_part4_self_check),
    ]

    overall_failed = []

    for test_name, test_function in test_groups:

        try:
            checks = test_function()

            failed = [
                name
                for name, passed in checks.items()
                if not passed
            ]

            if failed:
                print(f"{test_name}: FAIL")

                for name in failed:
                    print(f"  {name}: FAIL")

                overall_failed.extend(
                    f"{test_name} -> {name}"
                    for name in failed
                )

            else:
                print(f"{test_name}: PASS")

                for name, passed in checks.items():
                    print(
                        f"  {name}: "
                        f"{'PASS' if passed else 'FAIL'}"
                    )

        except Exception as exc:

            print(f"{test_name}: ERROR")
            print(
                f"  exception: "
                f"{type(exc).__name__}: {exc}"
            )

            overall_failed.append(
                f"{test_name} -> exception"
            )

    print()

    if overall_failed:

        print("D16 COMPLETE SELF-TEST: FAIL")

        for item in overall_failed:
            print(f"  {item}")

    else:

        print("D16 COMPLETE SELF-TEST: PASS")