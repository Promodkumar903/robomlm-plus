# ============================================================
# ROBOMLM_PLUS
# OPPORTUNITY MODELS
# PART 1
# Foundation Data Models
# ============================================================

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ------------------------------------------------------------
# Opportunity Direction
# ------------------------------------------------------------

class OpportunityDirection(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    CALL = "CALL"
    PUT = "PUT"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"


# ------------------------------------------------------------
# Opportunity Grade
# ------------------------------------------------------------

class OpportunityGrade(str, Enum):
    A_PLUS = "A+"
    A = "A"
    B_PLUS = "B+"
    B = "B"
    NO_TRADE = "NO_TRADE"


# ------------------------------------------------------------
# Opportunity Status
# ------------------------------------------------------------

class OpportunityStatus(str, Enum):
    DETECTED = "DETECTED"
    QUALIFIED = "QUALIFIED"
    ACTIVE = "ACTIVE"
    INVALIDATED = "INVALIDATED"
    EXHAUSTED = "EXHAUSTED"
    CLOSED = "CLOSED"
    REJECTED = "REJECTED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


# ------------------------------------------------------------
# Opportunity Type
# ------------------------------------------------------------

class OpportunityType(str, Enum):
    BREAKOUT = "BREAKOUT"
    BREAKDOWN = "BREAKDOWN"
    CONTINUATION = "CONTINUATION"
    PULLBACK = "PULLBACK"
    REVERSAL = "REVERSAL"
    ACCUMULATION_EXPANSION = "ACCUMULATION_EXPANSION"
    DISTRIBUTION_DOWNSIDE = "DISTRIBUTION_DOWNSIDE"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


# ------------------------------------------------------------
# Opportunity Evidence
# ------------------------------------------------------------

@dataclass
class OpportunityEvidence:
    """
    Evidence supplied by upstream intelligence engines.

    This model stores evidence.
    It does not invent or calculate market intelligence.
    """

    evidence_id: str

    source_engine: str = ""

    name: str = ""

    score: float = 0.0
    confidence: float = 0.0

    direction: OpportunityDirection = (
        OpportunityDirection.UNKNOWN
    )

    available: bool = True

    timestamp: Optional[str] = None

    values: Dict[str, Any] = field(
        default_factory=dict
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def normalize(self) -> None:

        try:
            self.score = float(self.score)
        except (TypeError, ValueError):
            self.score = 0.0

        try:
            self.confidence = float(
                self.confidence
            )
        except (TypeError, ValueError):
            self.confidence = 0.0

        self.score = max(
            0.0,
            min(100.0, self.score),
        )

        self.confidence = max(
            0.0,
            min(100.0, self.confidence),
        )

    def to_dict(self) -> Dict[str, Any]:

        self.normalize()

        return {
            "evidence_id": self.evidence_id,
            "source_engine": self.source_engine,
            "name": self.name,
            "score": self.score,
            "confidence": self.confidence,
            "direction": self.direction.value,
            "available": self.available,
            "timestamp": self.timestamp,
            "values": dict(self.values),
            "metadata": dict(self.metadata),
        }


# ------------------------------------------------------------
# Opportunity Boundary
# ------------------------------------------------------------

@dataclass
class OpportunityBoundary:
    """
    Structural boundary received from Boundary/Breakout
    intelligence.

    It represents levels; it does not decide whether a trade
    should be taken.
    """

    upper: Optional[float] = None
    lower: Optional[float] = None

    breakout_level: Optional[float] = None
    breakdown_level: Optional[float] = None

    current_price: Optional[float] = None

    boundary_width: Optional[float] = None
    boundary_width_pct: Optional[float] = None

    source_engine: str = ""

    valid: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def calculate_width(self) -> Optional[float]:

        if (
            self.upper is None
            or self.lower is None
        ):
            return None

        try:
            width = (
                float(self.upper)
                - float(self.lower)
            )
        except (TypeError, ValueError):
            return None

        self.boundary_width = abs(width)

        return self.boundary_width

    def calculate_width_pct(self) -> Optional[float]:

        if (
            self.boundary_width is None
            or self.current_price is None
        ):
            return None

        try:
            price = float(
                self.current_price
            )

            if price <= 0:
                return None

            self.boundary_width_pct = (
                self.boundary_width
                / price
            ) * 100.0

        except (TypeError, ValueError):
            return None

        return self.boundary_width_pct

    def normalize(self) -> None:

        self.calculate_width()
        self.calculate_width_pct()

    def to_dict(self) -> Dict[str, Any]:

        self.normalize()

        return {
            "upper": self.upper,
            "lower": self.lower,
            "breakout_level": (
                self.breakout_level
            ),
            "breakdown_level": (
                self.breakdown_level
            ),
            "current_price": (
                self.current_price
            ),
            "boundary_width": (
                self.boundary_width
            ),
            "boundary_width_pct": (
                self.boundary_width_pct
            ),
            "source_engine": self.source_engine,
            "valid": self.valid,
            "metadata": dict(self.metadata),
        }


# ------------------------------------------------------------
# Opportunity Entry Zone
# ------------------------------------------------------------

@dataclass
class OpportunityEntryZone:
    """
    Entry information produced by upstream opportunity/
    structure intelligence.

    The model stores the calculated zone; it does not invent
    an entry level when upstream intelligence has not supplied
    one.
    """

    entry_price: Optional[float] = None

    lower: Optional[float] = None
    upper: Optional[float] = None

    direction: OpportunityDirection = (
        OpportunityDirection.UNKNOWN
    )

    valid: bool = False

    source_engine: str = ""

    reason: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def contains(
        self,
        price: Optional[float],
    ) -> bool:

        if price is None:
            return False

        try:
            price = float(price)
        except (TypeError, ValueError):
            return False

        if (
            self.lower is not None
            and price < float(self.lower)
        ):
            return False

        if (
            self.upper is not None
            and price > float(self.upper)
        ):
            return False

        return True

    def to_dict(self) -> Dict[str, Any]:

        return {
            "entry_price": self.entry_price,
            "lower": self.lower,
            "upper": self.upper,
            "direction": self.direction.value,
            "valid": self.valid,
            "source_engine": self.source_engine,
            "reason": self.reason,
            "metadata": dict(self.metadata),
        }


# ------------------------------------------------------------
# Opportunity Expected Move
# ------------------------------------------------------------

@dataclass
class OpportunityExpectedMove:
    """
    Expected move representation.

    The actual expected-move calculation belongs to the
    upstream validated intelligence/model layer.
    """

    expected_move_pct: float = 0.0

    expected_move_value: Optional[float] = None

    expected_target: Optional[float] = None

    horizon_minutes: float = 0.0

    direction: OpportunityDirection = (
        OpportunityDirection.UNKNOWN
    )

    source_engine: str = ""

    valid: bool = False

    methodology: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def normalize(self) -> None:

        try:
            self.expected_move_pct = float(
                self.expected_move_pct
            )
        except (TypeError, ValueError):
            self.expected_move_pct = 0.0

        try:
            self.horizon_minutes = float(
                self.horizon_minutes
            )
        except (TypeError, ValueError):
            self.horizon_minutes = 0.0

        self.expected_move_pct = max(
            0.0,
            self.expected_move_pct,
        )

        self.horizon_minutes = max(
            0.0,
            self.horizon_minutes,
        )

    def to_dict(self) -> Dict[str, Any]:

        self.normalize()

        return {
            "expected_move_pct": (
                self.expected_move_pct
            ),
            "expected_move_value": (
                self.expected_move_value
            ),
            "expected_target": (
                self.expected_target
            ),
            "horizon_minutes": (
                self.horizon_minutes
            ),
            "direction": self.direction.value,
            "source_engine": self.source_engine,
            "valid": self.valid,
            "methodology": self.methodology,
            "metadata": dict(self.metadata),
        }


# ------------------------------------------------------------
# Opportunity Invalidation
# ------------------------------------------------------------

@dataclass
class OpportunityInvalidation:
    """
    Thesis/invalidation information.

    It describes what invalidates an opportunity.
    Final action remains outside this model.
    """

    invalidation_price: Optional[float] = None

    reason: str = ""

    active: bool = False

    source_engine: str = ""

    anti_evidence_ids: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "invalidation_price": (
                self.invalidation_price
            ),
            "reason": self.reason,
            "active": self.active,
            "source_engine": self.source_engine,
            "anti_evidence_ids": list(
                self.anti_evidence_ids
            ),
            "metadata": dict(self.metadata),
        }


# ------------------------------------------------------------
# Base Opportunity Model
# ------------------------------------------------------------

@dataclass
class OpportunityModel:
    """
    Core ROBOMLM opportunity representation.

    Flow represented here:

    Evidence
        ->
    Opportunity
        ->
    Entry
        ->
    Expected Move
        ->
    Invalidation

    D13 remains the final decision authority.
    """

    opportunity_id: str

    instrument: str

    exchange: str = ""

    market: str = ""

    asset_class: str = ""

    timeframe: str = ""

    timestamp: Optional[str] = None

    direction: OpportunityDirection = (
        OpportunityDirection.UNKNOWN
    )

    opportunity_type: OpportunityType = (
        OpportunityType.UNKNOWN
    )

    status: OpportunityStatus = (
        OpportunityStatus.DETECTED
    )

    grade: OpportunityGrade = (
        OpportunityGrade.NO_TRADE
    )

    quality_score: float = 0.0

    evidence_strength: float = 0.0

    opportunity_score: float = 0.0

    risk_score: float = 0.0

    current_price: Optional[float] = None

    boundary: Optional[
        OpportunityBoundary
    ] = None

    entry: Optional[
        OpportunityEntryZone
    ] = None

    expected_move: Optional[
        OpportunityExpectedMove
    ] = None

    invalidation: Optional[
        OpportunityInvalidation
    ] = None

    evidence: List[
        OpportunityEvidence
    ] = field(default_factory=list)

    warnings: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def normalize(self) -> None:

        score_fields = [
            "quality_score",
            "evidence_strength",
            "opportunity_score",
            "risk_score",
        ]

        for field_name in score_fields:

            try:
                value = float(
                    getattr(
                        self,
                        field_name,
                    )
                )
            except (TypeError, ValueError):
                value = 0.0

            setattr(
                self,
                field_name,
                max(
                    0.0,
                    min(100.0, value),
                ),
            )

        for item in self.evidence:
            item.normalize()

        if self.boundary is not None:
            self.boundary.normalize()

        if self.expected_move is not None:
            self.expected_move.normalize()

    def add_evidence(
        self,
        evidence: OpportunityEvidence,
    ) -> None:

        if not isinstance(
            evidence,
            OpportunityEvidence,
        ):
            raise TypeError(
                "evidence must be "
                "OpportunityEvidence"
            )

        self.evidence.append(
            evidence
        )

    def add_warning(
        self,
        message: str,
    ) -> None:

        if (
            message
            and message not in self.warnings
        ):
            self.warnings.append(
                str(message)
            )

    def has_valid_entry(self) -> bool:

        return bool(
            self.entry is not None
            and self.entry.valid
            and self.entry.entry_price
            is not None
        )

    def has_expected_move(self) -> bool:

        return bool(
            self.expected_move is not None
            and self.expected_move.valid
            and self.expected_move.expected_move_pct
            > 0.0
        )

    def has_invalidation(self) -> bool:

        return bool(
            self.invalidation is not None
            and (
                self.invalidation.invalidation_price
                is not None
                or self.invalidation.reason
            )
        )

    def to_dict(self) -> Dict[str, Any]:

        self.normalize()

        return {
            "opportunity_id": (
                self.opportunity_id
            ),
            "instrument": self.instrument,
            "exchange": self.exchange,
            "market": self.market,
            "asset_class": self.asset_class,
            "timeframe": self.timeframe,
            "timestamp": self.timestamp,
            "direction": self.direction.value,
            "opportunity_type": (
                self.opportunity_type.value
            ),
            "status": self.status.value,
            "grade": self.grade.value,
            "quality_score": (
                self.quality_score
            ),
            "evidence_strength": (
                self.evidence_strength
            ),
            "opportunity_score": (
                self.opportunity_score
            ),
            "risk_score": self.risk_score,
            "current_price": (
                self.current_price
            ),
            "boundary": (
                self.boundary.to_dict()
                if self.boundary is not None
                else None
            ),
            "entry": (
                self.entry.to_dict()
                if self.entry is not None
                else None
            ),
            "expected_move": (
                self.expected_move.to_dict()
                if self.expected_move is not None
                else None
            ),
            "invalidation": (
                self.invalidation.to_dict()
                if self.invalidation is not None
                else None
            ),
            "evidence": [
                item.to_dict()
                for item in self.evidence
            ],
            "warnings": list(
                self.warnings
            ),
            "metadata": dict(
                self.metadata
            ),
        }


# ------------------------------------------------------------
# Public API
# ------------------------------------------------------------

__all__ = [
    "OpportunityDirection",
    "OpportunityGrade",
    "OpportunityStatus",
    "OpportunityType",
    "OpportunityEvidence",
    "OpportunityBoundary",
    "OpportunityEntryZone",
    "OpportunityExpectedMove",
    "OpportunityInvalidation",
    "OpportunityModel",
]
# ============================================================
# ROBOMLM_PLUS
# OPPORTUNITY MODELS
# PART 2
# Thesis + Target + Lifecycle + Evidence Aggregation
# ============================================================

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

# Part 1 models are expected to exist in the same file.
# No replacement of Part 1 is required.


# ------------------------------------------------------------
# Opportunity Target
# ------------------------------------------------------------

@dataclass
class OpportunityTarget:
    """
    Target representation supplied by opportunity/growth
    intelligence.

    This stores calculated target information.
    It does not create a new target formula.
    """

    target_price: Optional[float] = None

    target_move_pct: float = 0.0

    target_type: str = "EXPECTED_MOVE"

    horizon_minutes: float = 0.0

    direction: "OpportunityDirection" = field(
        default_factory=lambda: OpportunityDirection.UNKNOWN
    )

    valid: bool = False

    source_engine: str = ""

    confidence: float = 0.0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def normalize(self) -> None:

        try:
            self.target_move_pct = float(
                self.target_move_pct
            )
        except (TypeError, ValueError):
            self.target_move_pct = 0.0

        try:
            self.horizon_minutes = float(
                self.horizon_minutes
            )
        except (TypeError, ValueError):
            self.horizon_minutes = 0.0

        try:
            self.confidence = float(
                self.confidence
            )
        except (TypeError, ValueError):
            self.confidence = 0.0

        self.target_move_pct = max(
            0.0,
            self.target_move_pct,
        )

        self.horizon_minutes = max(
            0.0,
            self.horizon_minutes,
        )

        self.confidence = max(
            0.0,
            min(100.0, self.confidence),
        )

    def to_dict(self) -> Dict[str, Any]:

        self.normalize()

        return {
            "target_price": self.target_price,
            "target_move_pct": (
                self.target_move_pct
            ),
            "target_type": self.target_type,
            "horizon_minutes": (
                self.horizon_minutes
            ),
            "direction": self.direction.value,
            "valid": self.valid,
            "source_engine": self.source_engine,
            "confidence": self.confidence,
            "metadata": dict(self.metadata),
        }


# ------------------------------------------------------------
# Opportunity Risk Context
# ------------------------------------------------------------

@dataclass
class OpportunityRiskContext:
    """
    Risk information associated with an opportunity.

    Risk context is descriptive here.
    Final risk authorization remains downstream.
    """

    risk_score: float = 0.0

    invalidation_distance_pct: Optional[float] = None

    reward_distance_pct: Optional[float] = None

    expected_rr: Optional[float] = None

    volatility_context: float = 0.0

    liquidity_context: float = 0.0

    execution_context: float = 0.0

    risk_reasons: List[str] = field(
        default_factory=list
    )

    source_engine: str = ""

    valid: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def normalize(self) -> None:

        try:
            self.risk_score = float(
                self.risk_score
            )
        except (TypeError, ValueError):
            self.risk_score = 0.0

        try:
            self.volatility_context = float(
                self.volatility_context
            )
        except (TypeError, ValueError):
            self.volatility_context = 0.0

        try:
            self.liquidity_context = float(
                self.liquidity_context
            )
        except (TypeError, ValueError):
            self.liquidity_context = 0.0

        try:
            self.execution_context = float(
                self.execution_context
            )
        except (TypeError, ValueError):
            self.execution_context = 0.0

        self.risk_score = max(
            0.0,
            min(100.0, self.risk_score),
        )

        self.volatility_context = max(
            0.0,
            min(100.0, self.volatility_context),
        )

        self.liquidity_context = max(
            0.0,
            min(100.0, self.liquidity_context),
        )

        self.execution_context = max(
            0.0,
            min(100.0, self.execution_context),
        )

        if self.expected_rr is not None:
            try:
                self.expected_rr = float(
                    self.expected_rr
                )
            except (TypeError, ValueError):
                self.expected_rr = None

    def to_dict(self) -> Dict[str, Any]:

        self.normalize()

        return {
            "risk_score": self.risk_score,
            "invalidation_distance_pct": (
                self.invalidation_distance_pct
            ),
            "reward_distance_pct": (
                self.reward_distance_pct
            ),
            "expected_rr": self.expected_rr,
            "volatility_context": (
                self.volatility_context
            ),
            "liquidity_context": (
                self.liquidity_context
            ),
            "execution_context": (
                self.execution_context
            ),
            "risk_reasons": list(
                self.risk_reasons
            ),
            "source_engine": self.source_engine,
            "valid": self.valid,
            "metadata": dict(self.metadata),
        }


# ------------------------------------------------------------
# Opportunity Thesis
# ------------------------------------------------------------

@dataclass
class OpportunityThesis:
    """
    Trade thesis representation.

    The thesis explains WHY an opportunity exists and what
    conditions must remain valid.

    It does not execute or authorize a trade.
    """

    thesis_id: str

    direction: "OpportunityDirection" = field(
        default_factory=lambda: OpportunityDirection.UNKNOWN
    )

    opportunity_type: "OpportunityType" = field(
        default_factory=lambda: OpportunityType.UNKNOWN
    )

    statement: str = ""

    supporting_evidence_ids: List[str] = field(
        default_factory=list
    )

    conflicting_evidence_ids: List[str] = field(
        default_factory=list
    )

    invalidation_conditions: List[str] = field(
        default_factory=list
    )

    continuation_conditions: List[str] = field(
        default_factory=list
    )

    valid: bool = False

    strength: float = 0.0

    confidence: float = 0.0

    source_engine: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def normalize(self) -> None:

        try:
            self.strength = float(
                self.strength
            )
        except (TypeError, ValueError):
            self.strength = 0.0

        try:
            self.confidence = float(
                self.confidence
            )
        except (TypeError, ValueError):
            self.confidence = 0.0

        self.strength = max(
            0.0,
            min(100.0, self.strength),
        )

        self.confidence = max(
            0.0,
            min(100.0, self.confidence),
        )

    def has_supporting_evidence(self) -> bool:
        return bool(
            self.supporting_evidence_ids
        )

    def has_conflict(self) -> bool:
        return bool(
            self.conflicting_evidence_ids
        )

    def to_dict(self) -> Dict[str, Any]:

        self.normalize()

        return {
            "thesis_id": self.thesis_id,
            "direction": self.direction.value,
            "opportunity_type": (
                self.opportunity_type.value
            ),
            "statement": self.statement,
            "supporting_evidence_ids": list(
                self.supporting_evidence_ids
            ),
            "conflicting_evidence_ids": list(
                self.conflicting_evidence_ids
            ),
            "invalidation_conditions": list(
                self.invalidation_conditions
            ),
            "continuation_conditions": list(
                self.continuation_conditions
            ),
            "valid": self.valid,
            "strength": self.strength,
            "confidence": self.confidence,
            "source_engine": self.source_engine,
            "metadata": dict(self.metadata),
        }


# ------------------------------------------------------------
# Opportunity Lifecycle State
# ------------------------------------------------------------

@dataclass
class OpportunityLifecycleState:
    """
    Tracks the current lifecycle state of an opportunity.

    Lifecycle:

        DETECTED
           ↓
        QUALIFIED
           ↓
         ACTIVE
        ↙     ↘
    INVALIDATED  EXHAUSTED
         ↓          ↓
       CLOSED     CLOSED
    """

    status: "OpportunityStatus" = field(
        default_factory=lambda: OpportunityStatus.DETECTED
    )

    first_detected_at: Optional[str] = None

    qualified_at: Optional[str] = None

    activated_at: Optional[str] = None

    invalidated_at: Optional[str] = None

    exhausted_at: Optional[str] = None

    closed_at: Optional[str] = None

    last_updated_at: Optional[str] = None

    transition_reason: str = ""

    transition_count: int = 0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def transition(
        self,
        status: "OpportunityStatus",
        reason: str = "",
        timestamp: Optional[str] = None,
    ) -> None:

        self.status = status
        self.transition_reason = reason
        self.last_updated_at = timestamp

        self.transition_count += 1

        if status == OpportunityStatus.DETECTED:
            if self.first_detected_at is None:
                self.first_detected_at = timestamp

        elif status == OpportunityStatus.QUALIFIED:
            self.qualified_at = timestamp

        elif status == OpportunityStatus.ACTIVE:
            self.activated_at = timestamp

        elif status == OpportunityStatus.INVALIDATED:
            self.invalidated_at = timestamp

        elif status == OpportunityStatus.EXHAUSTED:
            self.exhausted_at = timestamp

        elif status == OpportunityStatus.CLOSED:
            self.closed_at = timestamp

    def is_active(self) -> bool:
        return self.status == OpportunityStatus.ACTIVE

    def is_closed(self) -> bool:
        return self.status == OpportunityStatus.CLOSED

    def is_invalidated(self) -> bool:
        return (
            self.status
            == OpportunityStatus.INVALIDATED
        )

    def is_exhausted(self) -> bool:
        return (
            self.status
            == OpportunityStatus.EXHAUSTED
        )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "status": self.status.value,
            "first_detected_at": (
                self.first_detected_at
            ),
            "qualified_at": self.qualified_at,
            "activated_at": self.activated_at,
            "invalidated_at": (
                self.invalidated_at
            ),
            "exhausted_at": self.exhausted_at,
            "closed_at": self.closed_at,
            "last_updated_at": (
                self.last_updated_at
            ),
            "transition_reason": (
                self.transition_reason
            ),
            "transition_count": (
                self.transition_count
            ),
            "metadata": dict(self.metadata),
        }


# ------------------------------------------------------------
# Evidence Aggregation
# ------------------------------------------------------------

@dataclass
class OpportunityEvidenceSummary:
    """
    Aggregated evidence view.

    This summarizes already supplied evidence.
    It does not create new market evidence.
    """

    total_evidence: int = 0

    available_evidence: int = 0

    supporting_evidence: int = 0

    conflicting_evidence: int = 0

    neutral_evidence: int = 0

    average_score: float = 0.0

    average_confidence: float = 0.0

    directional_alignment: float = 0.0

    evidence_strength: float = 0.0

    dominant_direction: (
        "OpportunityDirection"
    ) = field(
        default_factory=lambda: OpportunityDirection.UNKNOWN
    )

    source_engines: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def normalize(self) -> None:

        numeric_fields = (
            "average_score",
            "average_confidence",
            "directional_alignment",
            "evidence_strength",
        )

        for field_name in numeric_fields:

            try:
                value = float(
                    getattr(
                        self,
                        field_name,
                    )
                )
            except (TypeError, ValueError):
                value = 0.0

            setattr(
                self,
                field_name,
                max(
                    0.0,
                    min(100.0, value),
                ),
            )

    def to_dict(self) -> Dict[str, Any]:

        self.normalize()

        return {
            "total_evidence": (
                self.total_evidence
            ),
            "available_evidence": (
                self.available_evidence
            ),
            "supporting_evidence": (
                self.supporting_evidence
            ),
            "conflicting_evidence": (
                self.conflicting_evidence
            ),
            "neutral_evidence": (
                self.neutral_evidence
            ),
            "average_score": (
                self.average_score
            ),
            "average_confidence": (
                self.average_confidence
            ),
            "directional_alignment": (
                self.directional_alignment
            ),
            "evidence_strength": (
                self.evidence_strength
            ),
            "dominant_direction": (
                self.dominant_direction.value
            ),
            "source_engines": list(
                self.source_engines
            ),
            "metadata": dict(self.metadata),
        }


# ------------------------------------------------------------
# Opportunity Context
# ------------------------------------------------------------

@dataclass
class OpportunityContext:
    """
    Complete contextual container around one opportunity.
    """

    market_state: Dict[str, Any] = field(
        default_factory=dict
    )

    regime_state: Dict[str, Any] = field(
        default_factory=dict
    )

    relationship_state: Dict[str, Any] = field(
        default_factory=dict
    )

    structure_state: Dict[str, Any] = field(
        default_factory=dict
    )

    participation_state: Dict[str, Any] = field(
        default_factory=dict
    )

    derivative_state: Dict[str, Any] = field(
        default_factory=dict
    )

    liquidity_state: Dict[str, Any] = field(
        default_factory=dict
    )

    timing_state: Dict[str, Any] = field(
        default_factory=dict
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "market_state": dict(
                self.market_state
            ),
            "regime_state": dict(
                self.regime_state
            ),
            "relationship_state": dict(
                self.relationship_state
            ),
            "structure_state": dict(
                self.structure_state
            ),
            "participation_state": dict(
                self.participation_state
            ),
            "derivative_state": dict(
                self.derivative_state
            ),
            "liquidity_state": dict(
                self.liquidity_state
            ),
            "timing_state": dict(
                self.timing_state
            ),
            "metadata": dict(
                self.metadata
            ),
        }


# ------------------------------------------------------------
# Opportunity Evaluation Snapshot
# ------------------------------------------------------------

@dataclass
class OpportunityEvaluationSnapshot:
    """
    Point-in-time evaluation of an opportunity.

    Used for monitoring and later BlackBox/outcome
    reconstruction.
    """

    opportunity_id: str

    timestamp: Optional[str] = None

    status: "OpportunityStatus" = field(
        default_factory=lambda: OpportunityStatus.DETECTED
    )

    direction: "OpportunityDirection" = field(
        default_factory=lambda: OpportunityDirection.UNKNOWN
    )

    quality_score: float = 0.0

    evidence_strength: float = 0.0

    opportunity_score: float = 0.0

    expected_move_pct: float = 0.0

    current_price: Optional[float] = None

    target_price: Optional[float] = None

    invalidation_price: Optional[float] = None

    thesis_valid: bool = False

    anti_evidence_detected: bool = False

    exhaustion_detected: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def normalize(self) -> None:

        for field_name in (
            "quality_score",
            "evidence_strength",
            "opportunity_score",
        ):

            try:
                value = float(
                    getattr(
                        self,
                        field_name,
                    )
                )
            except (TypeError, ValueError):
                value = 0.0

            setattr(
                self,
                field_name,
                max(
                    0.0,
                    min(100.0, value),
                ),
            )

        try:
            self.expected_move_pct = float(
                self.expected_move_pct
            )
        except (TypeError, ValueError):
            self.expected_move_pct = 0.0

        self.expected_move_pct = max(
            0.0,
            self.expected_move_pct,
        )

    def to_dict(self) -> Dict[str, Any]:

        self.normalize()

        return {
            "opportunity_id": (
                self.opportunity_id
            ),
            "timestamp": self.timestamp,
            "status": self.status.value,
            "direction": self.direction.value,
            "quality_score": (
                self.quality_score
            ),
            "evidence_strength": (
                self.evidence_strength
            ),
            "opportunity_score": (
                self.opportunity_score
            ),
            "expected_move_pct": (
                self.expected_move_pct
            ),
            "current_price": (
                self.current_price
            ),
            "target_price": (
                self.target_price
            ),
            "invalidation_price": (
                self.invalidation_price
            ),
            "thesis_valid": (
                self.thesis_valid
            ),
            "anti_evidence_detected": (
                self.anti_evidence_detected
            ),
            "exhaustion_detected": (
                self.exhaustion_detected
            ),
            "metadata": dict(
                self.metadata
            ),
        }


# ------------------------------------------------------------
# Public API
# ------------------------------------------------------------

__all__ = [
    "OpportunityTarget",
    "OpportunityRiskContext",
    "OpportunityThesis",
    "OpportunityLifecycleState",
    "OpportunityEvidenceSummary",
    "OpportunityContext",
    "OpportunityEvaluationSnapshot",
]
# ============================================================
# opportunity_models.py
# PART 3 — Opportunity Scoring / Qualification / Ranking Models
# ============================================================

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Tuple


# ============================================================
# Opportunity Score Breakdown
# ============================================================

@dataclass
class OpportunityScoreBreakdown:
    """
    Transparent score decomposition.

    This model stores the calculated components supplied by
    upstream intelligence engines.

    It does NOT create market intelligence by itself.
    """

    structure_score: float = 0.0
    participation_score: float = 0.0
    breakout_score: float = 0.0
    confirmation_score: float = 0.0
    regime_score: float = 0.0
    relationship_score: float = 0.0
    timing_score: float = 0.0
    liquidity_score: float = 0.0
    thesis_score: float = 0.0
    growth_score: float = 0.0
    holdability_score: float = 0.0
    protection_score: float = 0.0
    future_score: float = 0.0

    composite_score: float = 0.0

    source_engines: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def normalize(self) -> "OpportunityScoreBreakdown":
        score_fields = [
            "structure_score",
            "participation_score",
            "breakout_score",
            "confirmation_score",
            "regime_score",
            "relationship_score",
            "timing_score",
            "liquidity_score",
            "thesis_score",
            "growth_score",
            "holdability_score",
            "protection_score",
            "future_score",
            "composite_score",
        ]

        for field_name in score_fields:
            value = getattr(self, field_name, 0.0)

            try:
                value = float(value)
            except (TypeError, ValueError):
                value = 0.0

            setattr(
                self,
                field_name,
                max(0.0, min(100.0, value)),
            )

        self.source_engines = list(
            dict.fromkeys(
                str(x)
                for x in self.source_engines
                if x is not None
            )
        )

        return self

    def to_dict(self) -> Dict[str, Any]:
        self.normalize()

        return {
            "structure_score": self.structure_score,
            "participation_score": self.participation_score,
            "breakout_score": self.breakout_score,
            "confirmation_score": self.confirmation_score,
            "regime_score": self.regime_score,
            "relationship_score": self.relationship_score,
            "timing_score": self.timing_score,
            "liquidity_score": self.liquidity_score,
            "thesis_score": self.thesis_score,
            "growth_score": self.growth_score,
            "holdability_score": self.holdability_score,
            "protection_score": self.protection_score,
            "future_score": self.future_score,
            "composite_score": self.composite_score,
            "source_engines": list(self.source_engines),
            "metadata": dict(self.metadata),
        }


# ============================================================
# Opportunity Qualification
# ============================================================

@dataclass
class OpportunityQualification:
    """
    Qualification state for an opportunity.

    Qualification is separate from final D13 decision authority.
    """

    qualified: bool = False

    minimum_quality_required: float = 35.0
    minimum_evidence_required: float = 40.0
    minimum_liquidity_required: float = 30.0

    quality_score: float = 0.0
    evidence_strength: float = 0.0
    liquidity_score: float = 0.0

    direction_valid: bool = False
    entry_valid: bool = False
    expected_move_valid: bool = False
    invalidation_valid: bool = False
    thesis_valid: bool = False

    rejection_reasons: List[str] = field(default_factory=list)
    qualification_reasons: List[str] = field(default_factory=list)

    source_engine: str = "opportunity_models"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def evaluate(self) -> bool:
        self.rejection_reasons = []
        self.qualification_reasons = []

        if self.quality_score < self.minimum_quality_required:
            self.rejection_reasons.append(
                "quality_below_minimum"
            )

        if self.evidence_strength < self.minimum_evidence_required:
            self.rejection_reasons.append(
                "evidence_below_minimum"
            )

        if self.liquidity_score < self.minimum_liquidity_required:
            self.rejection_reasons.append(
                "liquidity_below_minimum"
            )

        if not self.direction_valid:
            self.rejection_reasons.append(
                "direction_invalid"
            )

        if not self.entry_valid:
            self.rejection_reasons.append(
                "entry_invalid"
            )

        if not self.expected_move_valid:
            self.rejection_reasons.append(
                "expected_move_invalid"
            )

        if not self.invalidation_valid:
            self.rejection_reasons.append(
                "invalidation_invalid"
            )

        if not self.thesis_valid:
            self.rejection_reasons.append(
                "thesis_invalid"
            )

        self.qualified = len(self.rejection_reasons) == 0

        if self.qualified:
            self.qualification_reasons.extend(
                [
                    "quality_acceptable",
                    "evidence_acceptable",
                    "liquidity_acceptable",
                    "direction_valid",
                    "entry_valid",
                    "expected_move_valid",
                    "invalidation_valid",
                    "thesis_valid",
                ]
            )

        return self.qualified

    def to_dict(self) -> Dict[str, Any]:
        return {
            "qualified": self.qualified,
            "minimum_quality_required": self.minimum_quality_required,
            "minimum_evidence_required": self.minimum_evidence_required,
            "minimum_liquidity_required": self.minimum_liquidity_required,
            "quality_score": self.quality_score,
            "evidence_strength": self.evidence_strength,
            "liquidity_score": self.liquidity_score,
            "direction_valid": self.direction_valid,
            "entry_valid": self.entry_valid,
            "expected_move_valid": self.expected_move_valid,
            "invalidation_valid": self.invalidation_valid,
            "thesis_valid": self.thesis_valid,
            "rejection_reasons": list(self.rejection_reasons),
            "qualification_reasons": list(
                self.qualification_reasons
            ),
            "source_engine": self.source_engine,
            "metadata": dict(self.metadata),
        }


# ============================================================
# Opportunity Ranking Context
# ============================================================

@dataclass
class OpportunityRankingContext:
    """
    Ranking metadata.

    Ranking orders already calculated opportunities.
    It does not replace D13 decision authority.
    """

    rank: int = 0
    ranking_score: float = 0.0

    quality_component: float = 0.0
    evidence_component: float = 0.0
    magnitude_component: float = 0.0
    timing_component: float = 0.0
    liquidity_component: float = 0.0
    risk_component: float = 0.0
    stability_component: float = 0.0

    ranking_method: str = "composite_opportunity_quality"

    rank_reason: str = ""

    metadata: Dict[str, Any] = field(default_factory=dict)

    def normalize(self) -> "OpportunityRankingContext":
        numeric_fields = [
            "ranking_score",
            "quality_component",
            "evidence_component",
            "magnitude_component",
            "timing_component",
            "liquidity_component",
            "risk_component",
            "stability_component",
        ]

        for field_name in numeric_fields:
            value = getattr(self, field_name, 0.0)

            try:
                value = float(value)
            except (TypeError, ValueError):
                value = 0.0

            setattr(
                self,
                field_name,
                max(0.0, min(100.0, value)),
            )

        try:
            self.rank = max(0, int(self.rank))
        except (TypeError, ValueError):
            self.rank = 0

        return self

    def to_dict(self) -> Dict[str, Any]:
        self.normalize()

        return {
            "rank": self.rank,
            "ranking_score": self.ranking_score,
            "quality_component": self.quality_component,
            "evidence_component": self.evidence_component,
            "magnitude_component": self.magnitude_component,
            "timing_component": self.timing_component,
            "liquidity_component": self.liquidity_component,
            "risk_component": self.risk_component,
            "stability_component": self.stability_component,
            "ranking_method": self.ranking_method,
            "rank_reason": self.rank_reason,
            "metadata": dict(self.metadata),
        }


# ============================================================
# Opportunity Monitoring State
# ============================================================

@dataclass
class OpportunityMonitoringState:
    """
    Post-detection / post-entry monitoring state.

    Used to preserve the original thesis and compare new evidence
    against it over time.
    """

    monitoring_active: bool = False

    original_direction: str = ""
    original_entry_price: Optional[float] = None
    original_expected_move_pct: Optional[float] = None
    original_target_price: Optional[float] = None
    original_invalidation_price: Optional[float] = None

    current_price: Optional[float] = None
    current_expected_move_pct: Optional[float] = None

    thesis_strength: float = 0.0
    anti_evidence_strength: float = 0.0
    continuation_strength: float = 0.0
    exhaustion_strength: float = 0.0

    thesis_intact: bool = True
    anti_evidence_detected: bool = False
    exhaustion_detected: bool = False

    recalculation_required: bool = False
    exit_review_required: bool = False

    monitoring_events: List[Dict[str, Any]] = field(
        default_factory=list
    )

    last_update_at: Optional[datetime] = None

    source_engine: str = "opportunity_models"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def record_event(
        self,
        event_type: str,
        reason: str = "",
        values: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ) -> None:
        event = {
            "event_type": str(event_type),
            "reason": str(reason),
            "values": dict(values or {}),
            "timestamp": (
                timestamp.isoformat()
                if isinstance(timestamp, datetime)
                else timestamp
            ),
        }

        self.monitoring_events.append(event)

        if len(self.monitoring_events) > 200:
            self.monitoring_events = self.monitoring_events[-200:]

        self.last_update_at = timestamp or datetime.utcnow()

    def update_state(
        self,
        *,
        thesis_strength: Optional[float] = None,
        anti_evidence_strength: Optional[float] = None,
        continuation_strength: Optional[float] = None,
        exhaustion_strength: Optional[float] = None,
        thesis_intact: Optional[bool] = None,
        anti_evidence_detected: Optional[bool] = None,
        exhaustion_detected: Optional[bool] = None,
        recalculation_required: Optional[bool] = None,
        exit_review_required: Optional[bool] = None,
        current_price: Optional[float] = None,
        current_expected_move_pct: Optional[float] = None,
        timestamp: Optional[datetime] = None,
    ) -> None:

        score_updates = {
            "thesis_strength": thesis_strength,
            "anti_evidence_strength": anti_evidence_strength,
            "continuation_strength": continuation_strength,
            "exhaustion_strength": exhaustion_strength,
        }

        for field_name, value in score_updates.items():
            if value is not None:
                try:
                    value = float(value)
                except (TypeError, ValueError):
                    value = 0.0

                setattr(
                    self,
                    field_name,
                    max(0.0, min(100.0, value)),
                )

        bool_updates = {
            "thesis_intact": thesis_intact,
            "anti_evidence_detected": anti_evidence_detected,
            "exhaustion_detected": exhaustion_detected,
            "recalculation_required": recalculation_required,
            "exit_review_required": exit_review_required,
        }

        for field_name, value in bool_updates.items():
            if value is not None:
                setattr(self, field_name, bool(value))

        if current_price is not None:
            try:
                self.current_price = float(current_price)
            except (TypeError, ValueError):
                pass

        if current_expected_move_pct is not None:
            try:
                self.current_expected_move_pct = float(
                    current_expected_move_pct
                )
            except (TypeError, ValueError):
                pass

        self.last_update_at = timestamp or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "monitoring_active": self.monitoring_active,
            "original_direction": self.original_direction,
            "original_entry_price": self.original_entry_price,
            "original_expected_move_pct": self.original_expected_move_pct,
            "original_target_price": self.original_target_price,
            "original_invalidation_price": self.original_invalidation_price,
            "current_price": self.current_price,
            "current_expected_move_pct": self.current_expected_move_pct,
            "thesis_strength": self.thesis_strength,
            "anti_evidence_strength": self.anti_evidence_strength,
            "continuation_strength": self.continuation_strength,
            "exhaustion_strength": self.exhaustion_strength,
            "thesis_intact": self.thesis_intact,
            "anti_evidence_detected": self.anti_evidence_detected,
            "exhaustion_detected": self.exhaustion_detected,
            "recalculation_required": self.recalculation_required,
            "exit_review_required": self.exit_review_required,
            "monitoring_events": list(self.monitoring_events),
            "last_update_at": (
                self.last_update_at.isoformat()
                if isinstance(self.last_update_at, datetime)
                else self.last_update_at
            ),
            "source_engine": self.source_engine,
            "metadata": dict(self.metadata),
        }


# ============================================================
# Opportunity Outcome
# ============================================================

@dataclass
class OpportunityOutcome:
    """
    Realized outcome record.

    This is intentionally separated from the opportunity judgment.

    Current intelligence -> outcome validation.

    Historical outcome must NOT be used to manufacture the current
    opportunity grade.
    """

    outcome_available: bool = False

    direction_correct: Optional[bool] = None
    entry_useful: Optional[bool] = None
    expected_move_reached: Optional[bool] = None
    target_reached: Optional[bool] = None
    invalidation_triggered: Optional[bool] = None

    realized_move_pct: Optional[float] = None
    maximum_favorable_excursion_pct: Optional[float] = None
    maximum_adverse_excursion_pct: Optional[float] = None

    realized_horizon_minutes: Optional[float] = None

    realized_entry_price: Optional[float] = None
    realized_exit_price: Optional[float] = None

    pnl_value: Optional[float] = None
    pnl_pct: Optional[float] = None

    exit_reason: str = ""

    validation_notes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "outcome_available": self.outcome_available,
            "direction_correct": self.direction_correct,
            "entry_useful": self.entry_useful,
            "expected_move_reached": self.expected_move_reached,
            "target_reached": self.target_reached,
            "invalidation_triggered": self.invalidation_triggered,
            "realized_move_pct": self.realized_move_pct,
            "maximum_favorable_excursion_pct": (
                self.maximum_favorable_excursion_pct
            ),
            "maximum_adverse_excursion_pct": (
                self.maximum_adverse_excursion_pct
            ),
            "realized_horizon_minutes": (
                self.realized_horizon_minutes
            ),
            "realized_entry_price": self.realized_entry_price,
            "realized_exit_price": self.realized_exit_price,
            "pnl_value": self.pnl_value,
            "pnl_pct": self.pnl_pct,
            "exit_reason": self.exit_reason,
            "validation_notes": list(self.validation_notes),
            "metadata": dict(self.metadata),
        }


# ============================================================
# Opportunity Lifecycle Container
# ============================================================

@dataclass
class OpportunityLifecycle:
    """
    Complete lifecycle state container.

    Detection -> Qualification -> Activation -> Monitoring ->
    Exhaustion / Invalidation -> Closure -> Outcome.
    """

    opportunity_id: str

    model: Optional["OpportunityModel"] = None

    qualification: OpportunityQualification = field(
        default_factory=OpportunityQualification
    )

    score_breakdown: OpportunityScoreBreakdown = field(
        default_factory=OpportunityScoreBreakdown
    )

    ranking: OpportunityRankingContext = field(
        default_factory=OpportunityRankingContext
    )

    monitoring: OpportunityMonitoringState = field(
        default_factory=OpportunityMonitoringState
    )

    outcome: OpportunityOutcome = field(
        default_factory=OpportunityOutcome
    )

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    metadata: Dict[str, Any] = field(default_factory=dict)

    def touch(
        self,
        timestamp: Optional[datetime] = None,
    ) -> None:
        self.updated_at = timestamp or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "opportunity_id": self.opportunity_id,
            "model": (
                self.model.to_dict()
                if self.model is not None
                else None
            ),
            "qualification": self.qualification.to_dict(),
            "score_breakdown": self.score_breakdown.to_dict(),
            "ranking": self.ranking.to_dict(),
            "monitoring": self.monitoring.to_dict(),
            "outcome": self.outcome.to_dict(),
            "created_at": (
                self.created_at.isoformat()
                if isinstance(self.created_at, datetime)
                else self.created_at
            ),
            "updated_at": (
                self.updated_at.isoformat()
                if isinstance(self.updated_at, datetime)
                else self.updated_at
            ),
            "metadata": dict(self.metadata),
        }


# ============================================================
# Opportunity Collection
# ============================================================

@dataclass
class OpportunityModelCollection:
    """
    Collection of opportunity models used by scanner/model layer.
    """

    opportunities: List["OpportunityModel"] = field(
        default_factory=list
    )

    timestamp: Optional[datetime] = None

    total_count: int = 0
    qualified_count: int = 0
    rejected_count: int = 0

    metadata: Dict[str, Any] = field(default_factory=dict)

    def refresh_counts(self) -> None:
        self.total_count = len(self.opportunities)

        qualified = 0

        for opportunity in self.opportunities:
            status = getattr(opportunity, "status", None)

            if status is not None:
                status_value = getattr(
                    status,
                    "value",
                    str(status),
                )

                if str(status_value).upper() in {
                    "QUALIFIED",
                    "ACTIVE",
                    "ENTRY",
                }:
                    qualified += 1

        self.qualified_count = qualified
        self.rejected_count = max(
            0,
            self.total_count - self.qualified_count,
        )

    def add(
        self,
        opportunity: "OpportunityModel",
    ) -> None:
        self.opportunities.append(opportunity)
        self.refresh_counts()

    def top(
        self,
        n: int = 5,
    ) -> List["OpportunityModel"]:
        try:
            n = max(1, int(n))
        except (TypeError, ValueError):
            n = 5

        ranked = sorted(
            self.opportunities,
            key=lambda x: float(
                getattr(x, "opportunity_score", 0.0) or 0.0
            ),
            reverse=True,
        )

        return ranked[:n]

    def by_direction(
        self,
        direction: str,
    ) -> List["OpportunityModel"]:
        target = str(direction).upper()

        result = []

        for opportunity in self.opportunities:
            current = getattr(
                getattr(opportunity, "direction", None),
                "value",
                getattr(opportunity, "direction", ""),
            )

            if str(current).upper() == target:
                result.append(opportunity)

        return result

    def to_dict(self) -> Dict[str, Any]:
        self.refresh_counts()

        return {
            "opportunities": [
                item.to_dict()
                for item in self.opportunities
            ],
            "timestamp": (
                self.timestamp.isoformat()
                if isinstance(self.timestamp, datetime)
                else self.timestamp
            ),
            "total_count": self.total_count,
            "qualified_count": self.qualified_count,
            "rejected_count": self.rejected_count,
            "metadata": dict(self.metadata),
        }


# ============================================================
# Factory Helpers
# ============================================================

def build_opportunity_score_breakdown(
    *,
    structure_score: float = 0.0,
    participation_score: float = 0.0,
    breakout_score: float = 0.0,
    confirmation_score: float = 0.0,
    regime_score: float = 0.0,
    relationship_score: float = 0.0,
    timing_score: float = 0.0,
    liquidity_score: float = 0.0,
    thesis_score: float = 0.0,
    growth_score: float = 0.0,
    holdability_score: float = 0.0,
    protection_score: float = 0.0,
    future_score: float = 0.0,
    composite_score: float = 0.0,
    source_engines: Optional[Sequence[str]] = None,
) -> OpportunityScoreBreakdown:

    result = OpportunityScoreBreakdown(
        structure_score=structure_score,
        participation_score=participation_score,
        breakout_score=breakout_score,
        confirmation_score=confirmation_score,
        regime_score=regime_score,
        relationship_score=relationship_score,
        timing_score=timing_score,
        liquidity_score=liquidity_score,
        thesis_score=thesis_score,
        growth_score=growth_score,
        holdability_score=holdability_score,
        protection_score=protection_score,
        future_score=future_score,
        composite_score=composite_score,
        source_engines=list(source_engines or []),
    )

    return result.normalize()


def build_opportunity_collection(
    opportunities: Optional[
        Sequence["OpportunityModel"]
    ] = None,
) -> OpportunityModelCollection:

    collection = OpportunityModelCollection(
        opportunities=list(opportunities or []),
        timestamp=datetime.utcnow(),
    )

    collection.refresh_counts()

    return collection


# ============================================================
# Public API
# ============================================================

__all__ = [
    # Score
    "OpportunityScoreBreakdown",

    # Qualification
    "OpportunityQualification",

    # Ranking
    "OpportunityRankingContext",

    # Monitoring
    "OpportunityMonitoringState",

    # Outcome
    "OpportunityOutcome",

    # Lifecycle
    "OpportunityLifecycle",

    # Collection
    "OpportunityModelCollection",

    # Factories
    "build_opportunity_score_breakdown",
    "build_opportunity_collection",
]
# ============================================================
# opportunity_models.py
# PART 4 — Opportunity Decision Context / Thesis / Action Models
# ============================================================

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


# ============================================================
# Action Direction
# ============================================================

@dataclass
class OpportunityAction:
    """
    Actionable representation of an opportunity.

    This describes what the opportunity model has calculated.
    It does NOT become final D13 authority.
    """

    action: str = "NO_ACTION"

    direction: str = ""
    instrument: str = ""

    entry_price: Optional[float] = None
    entry_lower: Optional[float] = None
    entry_upper: Optional[float] = None

    target_price: Optional[float] = None
    expected_move_pct: Optional[float] = None

    invalidation_price: Optional[float] = None

    expected_horizon_minutes: Optional[float] = None

    action_valid: bool = False

    action_reason: str = ""

    source_engine: str = "opportunity_models"

    metadata: Dict[str, Any] = field(default_factory=dict)

    def normalize(self) -> "OpportunityAction":
        numeric_fields = [
            "entry_price",
            "entry_lower",
            "entry_upper",
            "target_price",
            "expected_move_pct",
            "invalidation_price",
            "expected_horizon_minutes",
        ]

        for name in numeric_fields:
            value = getattr(self, name, None)

            if value is None:
                continue

            try:
                setattr(self, name, float(value))
            except (TypeError, ValueError):
                setattr(self, name, None)

        self.action = str(self.action or "NO_ACTION").upper()
        self.direction = str(self.direction or "").upper()
        self.instrument = str(self.instrument or "")

        self.action_valid = bool(self.action_valid)

        return self

    def to_dict(self) -> Dict[str, Any]:
        self.normalize()

        return {
            "action": self.action,
            "direction": self.direction,
            "instrument": self.instrument,
            "entry_price": self.entry_price,
            "entry_lower": self.entry_lower,
            "entry_upper": self.entry_upper,
            "target_price": self.target_price,
            "expected_move_pct": self.expected_move_pct,
            "invalidation_price": self.invalidation_price,
            "expected_horizon_minutes": (
                self.expected_horizon_minutes
            ),
            "action_valid": self.action_valid,
            "action_reason": self.action_reason,
            "source_engine": self.source_engine,
            "metadata": dict(self.metadata),
        }


# ============================================================
# Opportunity Conviction Context
# ============================================================

@dataclass
class OpportunityConviction:
    """
    Current opportunity-quality judgment.

    Conviction is not a fabricated probability.
    """

    grade: str = "NO_TRADE"

    score: float = 0.0

    evidence_alignment: float = 0.0
    structure_alignment: float = 0.0
    participation_alignment: float = 0.0
    directional_alignment: float = 0.0

    thesis_strength: float = 0.0
    stability_score: float = 0.0

    conviction_valid: bool = False

    supporting_factors: List[str] = field(
        default_factory=list
    )

    conflicting_factors: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    source_engines: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(default_factory=dict)

    def normalize(self) -> "OpportunityConviction":
        score_fields = [
            "score",
            "evidence_alignment",
            "structure_alignment",
            "participation_alignment",
            "directional_alignment",
            "thesis_strength",
            "stability_score",
        ]

        for name in score_fields:
            try:
                value = float(getattr(self, name))
            except (TypeError, ValueError):
                value = 0.0

            setattr(
                self,
                name,
                max(0.0, min(100.0, value)),
            )

        self.grade = str(
            self.grade or "NO_TRADE"
        ).upper()

        self.source_engines = list(
            dict.fromkeys(
                str(x)
                for x in self.source_engines
                if x is not None
            )
        )

        return self

    def to_dict(self) -> Dict[str, Any]:
        self.normalize()

        return {
            "grade": self.grade,
            "score": self.score,
            "evidence_alignment": self.evidence_alignment,
            "structure_alignment": self.structure_alignment,
            "participation_alignment": (
                self.participation_alignment
            ),
            "directional_alignment": (
                self.directional_alignment
            ),
            "thesis_strength": self.thesis_strength,
            "stability_score": self.stability_score,
            "conviction_valid": self.conviction_valid,
            "supporting_factors": list(
                self.supporting_factors
            ),
            "conflicting_factors": list(
                self.conflicting_factors
            ),
            "warnings": list(self.warnings),
            "source_engines": list(
                self.source_engines
            ),
            "metadata": dict(self.metadata),
        }


# ============================================================
# Anti-Evidence State
# ============================================================

@dataclass
class OpportunityAntiEvidence:
    """
    Represents meaningful evidence against the active thesis.

    It does not automatically force an exit. It records the
    evidence so the monitoring/decision layer can reassess it.
    """

    detected: bool = False

    strength: float = 0.0

    direction: str = ""

    evidence_ids: List[str] = field(
        default_factory=list
    )

    source_engines: List[str] = field(
        default_factory=list
    )

    reasons: List[str] = field(
        default_factory=list
    )

    price_conflict: bool = False
    structure_conflict: bool = False
    participation_conflict: bool = False
    derivative_conflict: bool = False
    relationship_conflict: bool = False

    requires_recalculation: bool = False
    requires_exit_review: bool = False

    detected_at: Optional[datetime] = None

    metadata: Dict[str, Any] = field(default_factory=dict)

    def normalize(self) -> "OpportunityAntiEvidence":
        try:
            self.strength = float(self.strength)
        except (TypeError, ValueError):
            self.strength = 0.0

        self.strength = max(
            0.0,
            min(100.0, self.strength),
        )

        self.direction = str(
            self.direction or ""
        ).upper()

        self.evidence_ids = list(
            dict.fromkeys(
                str(x)
                for x in self.evidence_ids
                if x is not None
            )
        )

        self.source_engines = list(
            dict.fromkeys(
                str(x)
                for x in self.source_engines
                if x is not None
            )
        )

        return self

    def to_dict(self) -> Dict[str, Any]:
        self.normalize()

        return {
            "detected": self.detected,
            "strength": self.strength,
            "direction": self.direction,
            "evidence_ids": list(
                self.evidence_ids
            ),
            "source_engines": list(
                self.source_engines
            ),
            "reasons": list(self.reasons),
            "price_conflict": self.price_conflict,
            "structure_conflict": self.structure_conflict,
            "participation_conflict": (
                self.participation_conflict
            ),
            "derivative_conflict": (
                self.derivative_conflict
            ),
            "relationship_conflict": (
                self.relationship_conflict
            ),
            "requires_recalculation": (
                self.requires_recalculation
            ),
            "requires_exit_review": (
                self.requires_exit_review
            ),
            "detected_at": (
                self.detected_at.isoformat()
                if isinstance(
                    self.detected_at,
                    datetime
                )
                else self.detected_at
            ),
            "metadata": dict(self.metadata),
        }


# ============================================================
# Opportunity Continuation State
# ============================================================

@dataclass
class OpportunityContinuation:
    """
    Tracks evidence that the original thesis continues to hold.
    """

    active: bool = False

    strength: float = 0.0

    direction: str = ""

    continuation_factors: List[str] = field(
        default_factory=list
    )

    supporting_evidence_ids: List[str] = field(
        default_factory=list
    )

    last_confirmed_at: Optional[datetime] = None

    metadata: Dict[str, Any] = field(default_factory=dict)

    def normalize(self) -> "OpportunityContinuation":
        try:
            self.strength = float(self.strength)
        except (TypeError, ValueError):
            self.strength = 0.0

        self.strength = max(
            0.0,
            min(100.0, self.strength),
        )

        self.direction = str(
            self.direction or ""
        ).upper()

        return self

    def to_dict(self) -> Dict[str, Any]:
        self.normalize()

        return {
            "active": self.active,
            "strength": self.strength,
            "direction": self.direction,
            "continuation_factors": list(
                self.continuation_factors
            ),
            "supporting_evidence_ids": list(
                self.supporting_evidence_ids
            ),
            "last_confirmed_at": (
                self.last_confirmed_at.isoformat()
                if isinstance(
                    self.last_confirmed_at,
                    datetime
                )
                else self.last_confirmed_at
            ),
            "metadata": dict(self.metadata),
        }


# ============================================================
# Opportunity Exhaustion State
# ============================================================

@dataclass
class OpportunityExhaustion:
    """
    Detectable state describing possible move exhaustion.

    Exhaustion is not automatically equal to exit.
    It triggers exit/reassessment intelligence.
    """

    detected: bool = False

    strength: float = 0.0

    exhaustion_type: str = ""

    price_extension: bool = False
    momentum_decay: bool = False
    participation_decay: bool = False
    liquidity_deterioration: bool = False
    opposing_pressure: bool = False

    reasons: List[str] = field(
        default_factory=list
    )

    exit_review_required: bool = False

    detected_at: Optional[datetime] = None

    source_engines: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(default_factory=dict)

    def normalize(self) -> "OpportunityExhaustion":
        try:
            self.strength = float(self.strength)
        except (TypeError, ValueError):
            self.strength = 0.0

        self.strength = max(
            0.0,
            min(100.0, self.strength),
        )

        self.exhaustion_type = str(
            self.exhaustion_type or ""
        ).upper()

        return self

    def to_dict(self) -> Dict[str, Any]:
        self.normalize()

        return {
            "detected": self.detected,
            "strength": self.strength,
            "exhaustion_type": self.exhaustion_type,
            "price_extension": self.price_extension,
            "momentum_decay": self.momentum_decay,
            "participation_decay": (
                self.participation_decay
            ),
            "liquidity_deterioration": (
                self.liquidity_deterioration
            ),
            "opposing_pressure": (
                self.opposing_pressure
            ),
            "reasons": list(self.reasons),
            "exit_review_required": (
                self.exit_review_required
            ),
            "detected_at": (
                self.detected_at.isoformat()
                if isinstance(
                    self.detected_at,
                    datetime
                )
                else self.detected_at
            ),
            "source_engines": list(
                self.source_engines
            ),
            "metadata": dict(self.metadata),
        }


# ============================================================
# Opportunity Recalculation State
# ============================================================

@dataclass
class OpportunityRecalculation:
    """
    State used when the original opportunity needs to be
    recalculated because market evidence has materially changed.
    """

    required: bool = False

    reason: str = ""

    trigger_type: str = ""

    previous_direction: str = ""
    previous_expected_move_pct: Optional[float] = None
    previous_target_price: Optional[float] = None
    previous_invalidation_price: Optional[float] = None

    recalculation_count: int = 0

    requested_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    result_status: str = "PENDING"

    metadata: Dict[str, Any] = field(default_factory=dict)

    def request(
        self,
        reason: str,
        trigger_type: str = "MARKET_CHANGE",
        timestamp: Optional[datetime] = None,
    ) -> None:
        self.required = True
        self.reason = str(reason)
        self.trigger_type = str(
            trigger_type
        ).upper()

        self.recalculation_count += 1

        self.requested_at = (
            timestamp or datetime.utcnow()
        )

        self.result_status = "PENDING"

    def complete(
        self,
        status: str = "COMPLETED",
        timestamp: Optional[datetime] = None,
    ) -> None:
        self.required = False
        self.result_status = str(
            status
        ).upper()

        self.completed_at = (
            timestamp or datetime.utcnow()
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "required": self.required,
            "reason": self.reason,
            "trigger_type": self.trigger_type,
            "previous_direction": (
                self.previous_direction
            ),
            "previous_expected_move_pct": (
                self.previous_expected_move_pct
            ),
            "previous_target_price": (
                self.previous_target_price
            ),
            "previous_invalidation_price": (
                self.previous_invalidation_price
            ),
            "recalculation_count": (
                self.recalculation_count
            ),
            "requested_at": (
                self.requested_at.isoformat()
                if isinstance(
                    self.requested_at,
                    datetime
                )
                else self.requested_at
            ),
            "completed_at": (
                self.completed_at.isoformat()
                if isinstance(
                    self.completed_at,
                    datetime
                )
                else self.completed_at
            ),
            "result_status": self.result_status,
            "metadata": dict(self.metadata),
        }


# ============================================================
# Complete Opportunity Intelligence State
# ============================================================

@dataclass
class OpportunityIntelligenceState:
    """
    Consolidated current intelligence state for one opportunity.

    Flow:

        Opportunity
            ↓
        Conviction
            ↓
        Action
            ↓
        Continuation / Anti-Evidence
            ↓
        Recalculation
            ↓
        Exhaustion / Exit Review
    """

    opportunity_id: str

    conviction: OpportunityConviction = field(
        default_factory=OpportunityConviction
    )

    action: OpportunityAction = field(
        default_factory=OpportunityAction
    )

    continuation: OpportunityContinuation = field(
        default_factory=OpportunityContinuation
    )

    anti_evidence: OpportunityAntiEvidence = field(
        default_factory=OpportunityAntiEvidence
    )

    exhaustion: OpportunityExhaustion = field(
        default_factory=OpportunityExhaustion
    )

    recalculation: OpportunityRecalculation = field(
        default_factory=OpportunityRecalculation
    )

    current_price: Optional[float] = None

    last_update_at: Optional[datetime] = None

    intelligence_valid: bool = False

    warnings: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def update_timestamp(
        self,
        timestamp: Optional[datetime] = None,
    ) -> None:
        self.last_update_at = (
            timestamp or datetime.utcnow()
        )

    def mark_recalculation(
        self,
        reason: str,
        trigger_type: str = "MARKET_CHANGE",
        timestamp: Optional[datetime] = None,
    ) -> None:
        self.recalculation.request(
            reason=reason,
            trigger_type=trigger_type,
            timestamp=timestamp,
        )

        self.update_timestamp(timestamp)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "opportunity_id": self.opportunity_id,
            "conviction": (
                self.conviction.to_dict()
            ),
            "action": (
                self.action.to_dict()
            ),
            "continuation": (
                self.continuation.to_dict()
            ),
            "anti_evidence": (
                self.anti_evidence.to_dict()
            ),
            "exhaustion": (
                self.exhaustion.to_dict()
            ),
            "recalculation": (
                self.recalculation.to_dict()
            ),
            "current_price": self.current_price,
            "last_update_at": (
                self.last_update_at.isoformat()
                if isinstance(
                    self.last_update_at,
                    datetime
                )
                else self.last_update_at
            ),
            "intelligence_valid": (
                self.intelligence_valid
            ),
            "warnings": list(self.warnings),
            "metadata": dict(self.metadata),
        }


# ============================================================
# Public API
# ============================================================

__all__ = [
    "OpportunityAction",
    "OpportunityConviction",
    "OpportunityAntiEvidence",
    "OpportunityContinuation",
    "OpportunityExhaustion",
    "OpportunityRecalculation",
    "OpportunityIntelligenceState",
]
# ============================================================
# opportunity_models.py
# PART 5 — Validation / Audit / Serialization / Public Helpers
# ============================================================

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence


# ============================================================
# Validation Issue
# ============================================================

@dataclass
class OpportunityValidationIssue:
    """
    Validation issue generated by the opportunity model validator.

    Validation only checks structural/data integrity.
    It does not invent or alter intelligence.
    """

    code: str
    message: str

    severity: str = "ERROR"

    field_name: str = ""
    opportunity_id: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "field_name": self.field_name,
            "opportunity_id": self.opportunity_id,
            "metadata": dict(self.metadata),
        }


# ============================================================
# Validation Result
# ============================================================

@dataclass
class OpportunityValidationResult:
    """
    Complete validation result.
    """

    valid: bool = True

    issues: List[OpportunityValidationIssue] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    checked_count: int = 0

    valid_count: int = 0

    invalid_count: int = 0

    timestamp: Optional[datetime] = None

    validator_version: str = "1.0"

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def add_issue(
        self,
        issue: OpportunityValidationIssue,
    ) -> None:
        self.issues.append(issue)

        if issue.severity.upper() == "ERROR":
            self.valid = False

    def finalize(self) -> "OpportunityValidationResult":
        self.invalid_count = sum(
            1
            for issue in self.issues
            if issue.severity.upper() == "ERROR"
        )

        self.valid = self.invalid_count == 0

        self.valid_count = max(
            0,
            self.checked_count - self.invalid_count,
        )

        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

        return self

    def to_dict(self) -> Dict[str, Any]:
        self.finalize()

        return {
            "valid": self.valid,
            "issues": [
                issue.to_dict()
                for issue in self.issues
            ],
            "warnings": list(self.warnings),
            "checked_count": self.checked_count,
            "valid_count": self.valid_count,
            "invalid_count": self.invalid_count,
            "timestamp": (
                self.timestamp.isoformat()
                if isinstance(
                    self.timestamp,
                    datetime,
                )
                else self.timestamp
            ),
            "validator_version": self.validator_version,
            "metadata": dict(self.metadata),
        }


# ============================================================
# Opportunity Model Validator
# ============================================================

class OpportunityModelValidator:
    """
    Structural validator for OpportunityModel.

    Important:
        This validator does NOT calculate market intelligence.
        It only verifies that upstream intelligence has supplied
        coherent fields.
    """

    VERSION = "1.0"

    REQUIRED_ATTRIBUTES = (
        "opportunity_id",
        "instrument",
        "direction",
        "status",
        "grade",
        "current_price",
        "evidence",
        "warnings",
    )

    SCORE_FIELDS = (
        "quality_score",
        "evidence_strength",
        "opportunity_score",
        "risk_score",
    )

    def __init__(
        self,
        minimum_price: float = 0.0,
    ) -> None:
        self.minimum_price = float(
            minimum_price
        )

    # --------------------------------------------------------
    # Generic Helpers
    # --------------------------------------------------------

    @staticmethod
    def _enum_value(value: Any) -> str:
        if value is None:
            return ""

        return str(
            getattr(
                value,
                "value",
                value,
            )
        ).upper()

    @staticmethod
    def _numeric(
        value: Any,
    ) -> Optional[float]:
        if value is None:
            return None

        try:
            return float(value)
        except (
            TypeError,
            ValueError,
        ):
            return None

    # --------------------------------------------------------
    # Single Opportunity Validation
    # --------------------------------------------------------

    def validate(
        self,
        opportunity: "OpportunityModel",
    ) -> OpportunityValidationResult:

        result = OpportunityValidationResult(
            checked_count=1,
            validator_version=self.VERSION,
        )

        opportunity_id = str(
            getattr(
                opportunity,
                "opportunity_id",
                "",
            )
            or ""
        )

        # Required attributes
        for attribute in self.REQUIRED_ATTRIBUTES:
            if not hasattr(
                opportunity,
                attribute,
            ):
                result.add_issue(
                    OpportunityValidationIssue(
                        code="MISSING_ATTRIBUTE",
                        message=(
                            f"Required attribute missing: "
                            f"{attribute}"
                        ),
                        field_name=attribute,
                        opportunity_id=opportunity_id,
                    )
                )

        # Opportunity ID
        if not opportunity_id:
            result.add_issue(
                OpportunityValidationIssue(
                    code="INVALID_OPPORTUNITY_ID",
                    message="Opportunity ID is empty.",
                    field_name="opportunity_id",
                    opportunity_id=opportunity_id,
                )
            )

        # Instrument
        instrument = str(
            getattr(
                opportunity,
                "instrument",
                "",
            )
            or ""
        )

        if not instrument:
            result.add_issue(
                OpportunityValidationIssue(
                    code="INVALID_INSTRUMENT",
                    message="Instrument is empty.",
                    field_name="instrument",
                    opportunity_id=opportunity_id,
                )
            )

        # Direction
        direction = self._enum_value(
            getattr(
                opportunity,
                "direction",
                None,
            )
        )

        allowed_directions = {
            "BUY",
            "SELL",
            "CALL",
            "PUT",
            "NEUTRAL",
            "UNKNOWN",
            "",
        }

        if direction not in allowed_directions:
            result.add_issue(
                OpportunityValidationIssue(
                    code="INVALID_DIRECTION",
                    message=(
                        f"Unsupported direction: "
                        f"{direction}"
                    ),
                    field_name="direction",
                    opportunity_id=opportunity_id,
                )
            )

        # Current price
        current_price = self._numeric(
            getattr(
                opportunity,
                "current_price",
                None,
            )
        )

        if (
            current_price is not None
            and current_price < self.minimum_price
        ):
            result.add_issue(
                OpportunityValidationIssue(
                    code="INVALID_CURRENT_PRICE",
                    message=(
                        "Current price is below "
                        "the allowed minimum."
                    ),
                    field_name="current_price",
                    opportunity_id=opportunity_id,
                )
            )

        # Scores
        for field_name in self.SCORE_FIELDS:
            value = self._numeric(
                getattr(
                    opportunity,
                    field_name,
                    None,
                )
            )

            if value is None:
                result.add_issue(
                    OpportunityValidationIssue(
                        code="INVALID_SCORE",
                        message=(
                            f"{field_name} is not numeric."
                        ),
                        field_name=field_name,
                        opportunity_id=opportunity_id,
                    )
                )
                continue

            if value < 0.0 or value > 100.0:
                result.add_issue(
                    OpportunityValidationIssue(
                        code="SCORE_OUT_OF_RANGE",
                        message=(
                            f"{field_name} must be "
                            "between 0 and 100."
                        ),
                        field_name=field_name,
                        opportunity_id=opportunity_id,
                    )
                )

        # Expected move
        expected_move = getattr(
            opportunity,
            "expected_move",
            None,
        )

        if expected_move is not None:
            expected_move_pct = self._numeric(
                getattr(
                    expected_move,
                    "expected_move_pct",
                    None,
                )
            )

            if expected_move_pct is not None:
                if expected_move_pct < 0:
                    result.add_issue(
                        OpportunityValidationIssue(
                            code="NEGATIVE_EXPECTED_MOVE",
                            message=(
                                "Expected move percentage "
                                "cannot be negative."
                            ),
                            field_name=(
                                "expected_move"
                            ),
                            opportunity_id=(
                                opportunity_id
                            ),
                        )
                    )

            horizon = self._numeric(
                getattr(
                    expected_move,
                    "horizon_minutes",
                    None,
                )
            )

            if (
                horizon is not None
                and horizon <= 0
            ):
                result.add_issue(
                    OpportunityValidationIssue(
                        code="INVALID_HORIZON",
                        message=(
                            "Expected move horizon "
                            "must be positive."
                        ),
                        field_name=(
                            "expected_move"
                        ),
                        opportunity_id=(
                            opportunity_id
                        ),
                    )
                )

        # Entry validation
        entry = getattr(
            opportunity,
            "entry",
            None,
        )

        if entry is not None:
            entry_valid = bool(
                getattr(
                    entry,
                    "valid",
                    False,
                )
            )

            if entry_valid:
                entry_price = self._numeric(
                    getattr(
                        entry,
                        "entry_price",
                        None,
                    )
                )

                if (
                    entry_price is None
                    or entry_price <= 0
                ):
                    result.add_issue(
                        OpportunityValidationIssue(
                            code="INVALID_ENTRY_PRICE",
                            message=(
                                "Valid entry must contain "
                                "a positive entry price."
                            ),
                            field_name="entry",
                            opportunity_id=(
                                opportunity_id
                            ),
                        )
                    )

        # Invalidation validation
        invalidation = getattr(
            opportunity,
            "invalidation",
            None,
        )

        if invalidation is not None:
            active = bool(
                getattr(
                    invalidation,
                    "active",
                    False,
                )
            )

            invalidation_price = self._numeric(
                getattr(
                    invalidation,
                    "invalidation_price",
                    None,
                )
            )

            if active and (
                invalidation_price is None
                or invalidation_price <= 0
            ):
                result.add_issue(
                    OpportunityValidationIssue(
                        code="INVALID_INVALIDATION",
                        message=(
                            "Active invalidation requires "
                            "a valid invalidation price."
                        ),
                        field_name=(
                            "invalidation"
                        ),
                        opportunity_id=(
                            opportunity_id
                        ),
                    )
                )

        # Evidence collection
        evidence = getattr(
            opportunity,
            "evidence",
            None,
        )

        if evidence is None:
            result.add_issue(
                OpportunityValidationIssue(
                    code="MISSING_EVIDENCE",
                    message=(
                        "Opportunity has no evidence "
                        "collection."
                    ),
                    field_name="evidence",
                    opportunity_id=opportunity_id,
                )
            )
        elif not isinstance(
            evidence,
            (list, tuple),
        ):
            result.add_issue(
                OpportunityValidationIssue(
                    code="INVALID_EVIDENCE_CONTAINER",
                    message=(
                        "Evidence must be a list or tuple."
                    ),
                    field_name="evidence",
                    opportunity_id=opportunity_id,
                )
            )

        return result.finalize()

    # --------------------------------------------------------
    # Collection Validation
    # --------------------------------------------------------

    def validate_collection(
        self,
        opportunities: Sequence[
            "OpportunityModel"
        ],
    ) -> OpportunityValidationResult:

        result = OpportunityValidationResult(
            checked_count=len(
                opportunities
            ),
            validator_version=self.VERSION,
        )

        for opportunity in opportunities:
            single_result = self.validate(
                opportunity
            )

            result.issues.extend(
                single_result.issues
            )

            result.warnings.extend(
                single_result.warnings
            )

        return result.finalize()

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    def summary(
        self,
        result: OpportunityValidationResult,
    ) -> Dict[str, Any]:

        return {
            "valid": result.valid,
            "checked_count": result.checked_count,
            "valid_count": result.valid_count,
            "invalid_count": result.invalid_count,
            "error_count": sum(
                1
                for issue in result.issues
                if issue.severity.upper()
                == "ERROR"
            ),
            "warning_count": sum(
                1
                for issue in result.issues
                if issue.severity.upper()
                == "WARNING"
            ),
            "validator_version": (
                result.validator_version
            ),
        }


# ============================================================
# Opportunity Audit Record
# ============================================================

@dataclass
class OpportunityAuditRecord:
    """
    Immutable-style audit snapshot of an opportunity state.

    Intended for BlackBox / validation / learning pipelines.
    """

    audit_id: str

    opportunity_id: str

    timestamp: datetime

    instrument: str = ""

    direction: str = ""

    grade: str = ""

    status: str = ""

    quality_score: float = 0.0
    evidence_strength: float = 0.0
    opportunity_score: float = 0.0
    risk_score: float = 0.0

    expected_move_pct: Optional[float] = None
    expected_horizon_minutes: Optional[float] = None

    current_price: Optional[float] = None
    target_price: Optional[float] = None
    invalidation_price: Optional[float] = None

    thesis_valid: Optional[bool] = None
    anti_evidence_detected: bool = False
    exhaustion_detected: bool = False
    recalculation_required: bool = False

    action: str = "NO_ACTION"

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "audit_id": self.audit_id,
            "opportunity_id": self.opportunity_id,
            "timestamp": (
                self.timestamp.isoformat()
                if isinstance(
                    self.timestamp,
                    datetime,
                )
                else self.timestamp
            ),
            "instrument": self.instrument,
            "direction": self.direction,
            "grade": self.grade,
            "status": self.status,
            "quality_score": self.quality_score,
            "evidence_strength": (
                self.evidence_strength
            ),
            "opportunity_score": (
                self.opportunity_score
            ),
            "risk_score": self.risk_score,
            "expected_move_pct": (
                self.expected_move_pct
            ),
            "expected_horizon_minutes": (
                self.expected_horizon_minutes
            ),
            "current_price": self.current_price,
            "target_price": self.target_price,
            "invalidation_price": (
                self.invalidation_price
            ),
            "thesis_valid": self.thesis_valid,
            "anti_evidence_detected": (
                self.anti_evidence_detected
            ),
            "exhaustion_detected": (
                self.exhaustion_detected
            ),
            "recalculation_required": (
                self.recalculation_required
            ),
            "action": self.action,
            "metadata": dict(self.metadata),
        }


# ============================================================
# Audit Factory
# ============================================================

def build_opportunity_audit_record(
    opportunity: "OpportunityModel",
    *,
    audit_id: str,
    timestamp: Optional[datetime] = None,
    intelligence_state: Optional[
        OpportunityIntelligenceState
    ] = None,
) -> OpportunityAuditRecord:
    """
    Build a BlackBox-ready opportunity audit snapshot.
    """

    expected_move = getattr(
        opportunity,
        "expected_move",
        None,
    )

    target_price = None

    if expected_move is not None:
        target_price = getattr(
            expected_move,
            "expected_target",
            None,
        )

    invalidation = getattr(
        opportunity,
        "invalidation",
        None,
    )

    invalidation_price = None

    if invalidation is not None:
        invalidation_price = getattr(
            invalidation,
            "invalidation_price",
            None,
        )

    thesis_valid = None
    anti_evidence_detected = False
    exhaustion_detected = False
    recalculation_required = False
    action = "NO_ACTION"

    if intelligence_state is not None:
        thesis_valid = (
            getattr(
                intelligence_state.conviction,
                "conviction_valid",
                None,
            )
        )

        anti_evidence_detected = bool(
            getattr(
                intelligence_state.anti_evidence,
                "detected",
                False,
            )
        )

        exhaustion_detected = bool(
            getattr(
                intelligence_state.exhaustion,
                "detected",
                False,
            )
        )

        recalculation_required = bool(
            getattr(
                intelligence_state.recalculation,
                "required",
                False,
            )
        )

        action = str(
            getattr(
                intelligence_state.action,
                "action",
                "NO_ACTION",
            )
        )

    return OpportunityAuditRecord(
        audit_id=str(audit_id),
        opportunity_id=str(
            getattr(
                opportunity,
                "opportunity_id",
                "",
            )
        ),
        timestamp=(
            timestamp or datetime.utcnow()
        ),
        instrument=str(
            getattr(
                opportunity,
                "instrument",
                "",
            )
            or ""
        ),
        direction=OpportunityModelValidator._enum_value(
            getattr(
                opportunity,
                "direction",
                None,
            )
        ),
        grade=OpportunityModelValidator._enum_value(
            getattr(
                opportunity,
                "grade",
                None,
            )
        ),
        status=OpportunityModelValidator._enum_value(
            getattr(
                opportunity,
                "status",
                None,
            )
        ),
        quality_score=float(
            getattr(
                opportunity,
                "quality_score",
                0.0,
            )
            or 0.0
        ),
        evidence_strength=float(
            getattr(
                opportunity,
                "evidence_strength",
                0.0,
            )
            or 0.0
        ),
        opportunity_score=float(
            getattr(
                opportunity,
                "opportunity_score",
                0.0,
            )
            or 0.0
        ),
        risk_score=float(
            getattr(
                opportunity,
                "risk_score",
                0.0,
            )
            or 0.0
        ),
        expected_move_pct=(
            getattr(
                expected_move,
                "expected_move_pct",
                None,
            )
            if expected_move is not None
            else None
        ),
        expected_horizon_minutes=(
            getattr(
                expected_move,
                "horizon_minutes",
                None,
            )
            if expected_move is not None
            else None
        ),
        current_price=getattr(
            opportunity,
            "current_price",
            None,
        ),
        target_price=target_price,
        invalidation_price=invalidation_price,
        thesis_valid=thesis_valid,
        anti_evidence_detected=(
            anti_evidence_detected
        ),
        exhaustion_detected=(
            exhaustion_detected
        ),
        recalculation_required=(
            recalculation_required
        ),
        action=action,
    )


# ============================================================
# Serialization Helpers
# ============================================================

def serialize_opportunity(
    opportunity: "OpportunityModel",
) -> Dict[str, Any]:
    """
    Safe serialization helper.
    """

    if hasattr(
        opportunity,
        "to_dict",
    ):
        return opportunity.to_dict()

    raise TypeError(
        "Object does not provide to_dict()."
    )


def serialize_opportunity_collection(
    opportunities: Sequence[
        "OpportunityModel"
    ],
) -> List[Dict[str, Any]]:
    """
    Serialize multiple opportunities.
    """

    return [
        serialize_opportunity(
            opportunity
        )
        for opportunity in opportunities
    ]


# ============================================================
# Validation Convenience Function
# ============================================================

def validate_opportunity(
    opportunity: "OpportunityModel",
) -> OpportunityValidationResult:
    """
    Convenience validator.
    """

    validator = OpportunityModelValidator()

    return validator.validate(
        opportunity
    )


def validate_opportunity_collection(
    opportunities: Sequence[
        "OpportunityModel"
    ],
) -> OpportunityValidationResult:
    """
    Convenience collection validator.
    """

    validator = OpportunityModelValidator()

    return validator.validate_collection(
        opportunities
    )


# ============================================================
# Public API
# ============================================================

__all__ = [
    "OpportunityValidationIssue",
    "OpportunityValidationResult",
    "OpportunityModelValidator",
    "OpportunityAuditRecord",
    "build_opportunity_audit_record",
    "serialize_opportunity",
    "serialize_opportunity_collection",
    "validate_opportunity",
    "validate_opportunity_collection",
]