# ============================================================
# future_model.py
# PART 1 — Future State / Projection Foundation Models
# ============================================================

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


# ============================================================
# Future Direction
# ============================================================

class FutureDirection(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    CALL = "CALL"
    PUT = "PUT"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"


# ============================================================
# Future Horizon
# ============================================================

class FutureHorizon(str, Enum):
    VERY_SHORT = "VERY_SHORT"
    SHORT = "SHORT"
    MEDIUM = "MEDIUM"
    LONG = "LONG"
    UNKNOWN = "UNKNOWN"


# ============================================================
# Projection Status
# ============================================================

class FutureProjectionStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    DEVELOPING = "DEVELOPING"
    INVALIDATED = "INVALIDATED"
    EXHAUSTED = "EXHAUSTED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    UNKNOWN = "UNKNOWN"


# ============================================================
# Future Projection
# ============================================================

@dataclass
class FutureProjection:
    """
    Forward-looking projection supplied by upstream intelligence.

    This model stores projection information.
    It does not fabricate probability or direction.
    """

    projection_id: str = ""

    instrument: str = ""
    exchange: str = ""
    market: str = ""
    asset_class: str = ""
    timeframe: str = ""

    timestamp: Optional[datetime] = None

    direction: FutureDirection = FutureDirection.UNKNOWN

    horizon: FutureHorizon = FutureHorizon.UNKNOWN
    horizon_minutes: Optional[float] = None

    current_price: Optional[float] = None

    expected_move_pct: Optional[float] = None
    expected_move_value: Optional[float] = None
    expected_target: Optional[float] = None

    lower_target: Optional[float] = None
    upper_target: Optional[float] = None

    projection_strength: float = 0.0

    status: FutureProjectionStatus = (
        FutureProjectionStatus.INSUFFICIENT_DATA
    )

    methodology: str = ""

    source_engines: List[str] = field(
        default_factory=list
    )

    supporting_evidence_ids: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def normalize(self) -> "FutureProjection":
        numeric_fields = [
            "current_price",
            "expected_move_pct",
            "expected_move_value",
            "expected_target",
            "lower_target",
            "upper_target",
            "projection_strength",
            "horizon_minutes",
        ]

        for field_name in numeric_fields:
            value = getattr(self, field_name, None)

            if value is None:
                continue

            try:
                value = float(value)
            except (TypeError, ValueError):
                value = None

            setattr(
                self,
                field_name,
                value,
            )

        if self.projection_strength is not None:
            self.projection_strength = max(
                0.0,
                min(
                    100.0,
                    self.projection_strength,
                ),
            )

        if self.horizon_minutes is not None:
            self.horizon_minutes = max(
                0.0,
                self.horizon_minutes,
            )

        self.direction = self._normalize_enum(
            self.direction,
            FutureDirection,
            FutureDirection.UNKNOWN,
        )

        self.horizon = self._normalize_enum(
            self.horizon,
            FutureHorizon,
            FutureHorizon.UNKNOWN,
        )

        self.status = self._normalize_enum(
            self.status,
            FutureProjectionStatus,
            FutureProjectionStatus.UNKNOWN,
        )

        self.source_engines = list(
            dict.fromkeys(
                str(x)
                for x in self.source_engines
                if x is not None
            )
        )

        self.supporting_evidence_ids = list(
            dict.fromkeys(
                str(x)
                for x in self.supporting_evidence_ids
                if x is not None
            )
        )

        return self

    @staticmethod
    def _normalize_enum(
        value: Any,
        enum_cls: Any,
        default: Any,
    ) -> Any:
        if isinstance(value, enum_cls):
            return value

        try:
            return enum_cls(
                str(value).upper()
            )
        except (ValueError, TypeError):
            return default

    def has_target(self) -> bool:
        return (
            self.expected_target is not None
            and self.expected_target > 0
        )

    def has_expected_move(self) -> bool:
        return (
            self.expected_move_pct is not None
            and self.expected_move_pct > 0
        )

    def is_directional(self) -> bool:
        return self.direction in {
            FutureDirection.BUY,
            FutureDirection.SELL,
            FutureDirection.CALL,
            FutureDirection.PUT,
        }

    def is_valid(self) -> bool:
        self.normalize()

        return (
            bool(self.projection_id)
            and bool(self.instrument)
            and self.is_directional()
            and self.has_expected_move()
            and self.has_target()
            and self.horizon_minutes is not None
            and self.horizon_minutes > 0
            and self.status
            in {
                FutureProjectionStatus.AVAILABLE,
                FutureProjectionStatus.DEVELOPING,
            }
        )

    def to_dict(self) -> Dict[str, Any]:
        self.normalize()

        return {
            "projection_id": self.projection_id,
            "instrument": self.instrument,
            "exchange": self.exchange,
            "market": self.market,
            "asset_class": self.asset_class,
            "timeframe": self.timeframe,
            "timestamp": (
                self.timestamp.isoformat()
                if isinstance(
                    self.timestamp,
                    datetime,
                )
                else self.timestamp
            ),
            "direction": self.direction.value,
            "horizon": self.horizon.value,
            "horizon_minutes": self.horizon_minutes,
            "current_price": self.current_price,
            "expected_move_pct": self.expected_move_pct,
            "expected_move_value": self.expected_move_value,
            "expected_target": self.expected_target,
            "lower_target": self.lower_target,
            "upper_target": self.upper_target,
            "projection_strength": (
                self.projection_strength
            ),
            "status": self.status.value,
            "methodology": self.methodology,
            "source_engines": list(
                self.source_engines
            ),
            "supporting_evidence_ids": list(
                self.supporting_evidence_ids
            ),
            "warnings": list(self.warnings),
            "metadata": dict(self.metadata),
        }


# ============================================================
# Future Evidence
# ============================================================

@dataclass
class FutureEvidence:
    """
    Evidence supporting or conflicting with a future projection.
    """

    evidence_id: str = ""

    source_engine: str = ""

    name: str = ""

    direction: FutureDirection = (
        FutureDirection.UNKNOWN
    )

    score: float = 0.0
    strength: float = 0.0

    available: bool = False

    supports_projection: bool = False
    conflicts_projection: bool = False

    timestamp: Optional[datetime] = None

    values: Dict[str, Any] = field(
        default_factory=dict
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def normalize(self) -> "FutureEvidence":
        for field_name in [
            "score",
            "strength",
        ]:
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
                    min(
                        100.0,
                        value,
                    ),
                ),
            )

        if not isinstance(
            self.direction,
            FutureDirection,
        ):
            try:
                self.direction = FutureDirection(
                    str(
                        self.direction
                    ).upper()
                )
            except (
                ValueError,
                TypeError,
            ):
                self.direction = (
                    FutureDirection.UNKNOWN
                )

        return self

    def to_dict(self) -> Dict[str, Any]:
        self.normalize()

        return {
            "evidence_id": self.evidence_id,
            "source_engine": self.source_engine,
            "name": self.name,
            "direction": self.direction.value,
            "score": self.score,
            "strength": self.strength,
            "available": self.available,
            "supports_projection": (
                self.supports_projection
            ),
            "conflicts_projection": (
                self.conflicts_projection
            ),
            "timestamp": (
                self.timestamp.isoformat()
                if isinstance(
                    self.timestamp,
                    datetime,
                )
                else self.timestamp
            ),
            "values": dict(self.values),
            "metadata": dict(self.metadata),
        }


# ============================================================
# Future Context
# ============================================================

@dataclass
class FutureContext:
    """
    Context required to interpret a forward projection.

    Values are supplied by upstream engines.
    """

    market_state: str = ""
    regime_state: str = ""

    structure_state: str = ""
    participation_state: str = ""
    liquidity_state: str = ""
    relationship_state: str = ""

    volatility_state: str = ""
    timing_state: str = ""

    trend_state: str = ""

    context_score: float = 0.0

    context_valid: bool = False

    source_engines: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def normalize(self) -> "FutureContext":
        try:
            self.context_score = float(
                self.context_score
            )
        except (
            TypeError,
            ValueError,
        ):
            self.context_score = 0.0

        self.context_score = max(
            0.0,
            min(
                100.0,
                self.context_score,
            ),
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
            "market_state": self.market_state,
            "regime_state": self.regime_state,
            "structure_state": self.structure_state,
            "participation_state": (
                self.participation_state
            ),
            "liquidity_state": (
                self.liquidity_state
            ),
            "relationship_state": (
                self.relationship_state
            ),
            "volatility_state": (
                self.volatility_state
            ),
            "timing_state": self.timing_state,
            "trend_state": self.trend_state,
            "context_score": self.context_score,
            "context_valid": self.context_valid,
            "source_engines": list(
                self.source_engines
            ),
            "metadata": dict(self.metadata),
        }


# ============================================================
# Future Projection Snapshot
# ============================================================

@dataclass
class FutureProjectionSnapshot:
    """
    Point-in-time snapshot used for tracking projection evolution.
    """

    snapshot_id: str = ""

    projection_id: str = ""

    timestamp: Optional[datetime] = None

    current_price: Optional[float] = None

    direction: FutureDirection = (
        FutureDirection.UNKNOWN
    )

    expected_move_pct: Optional[float] = None

    expected_target: Optional[float] = None

    horizon_minutes: Optional[float] = None

    projection_strength: float = 0.0

    context_score: float = 0.0

    status: FutureProjectionStatus = (
        FutureProjectionStatus.UNKNOWN
    )

    thesis_intact: Optional[bool] = None

    anti_evidence_detected: bool = False

    exhaustion_detected: bool = False

    recalculation_required: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "projection_id": self.projection_id,
            "timestamp": (
                self.timestamp.isoformat()
                if isinstance(
                    self.timestamp,
                    datetime,
                )
                else self.timestamp
            ),
            "current_price": self.current_price,
            "direction": (
                self.direction.value
                if isinstance(
                    self.direction,
                    FutureDirection,
                )
                else str(
                    self.direction
                )
            ),
            "expected_move_pct": (
                self.expected_move_pct
            ),
            "expected_target": (
                self.expected_target
            ),
            "horizon_minutes": (
                self.horizon_minutes
            ),
            "projection_strength": (
                self.projection_strength
            ),
            "context_score": self.context_score,
            "status": (
                self.status.value
                if isinstance(
                    self.status,
                    FutureProjectionStatus,
                )
                else str(
                    self.status
                )
            ),
            "thesis_intact": self.thesis_intact,
            "anti_evidence_detected": (
                self.anti_evidence_detected
            ),
            "exhaustion_detected": (
                self.exhaustion_detected
            ),
            "recalculation_required": (
                self.recalculation_required
            ),
            "metadata": dict(self.metadata),
        }


# ============================================================
# Factory
# ============================================================

def build_future_projection(
    *,
    projection_id: str,
    instrument: str,
    direction: FutureDirection,
    current_price: Optional[float] = None,
    expected_move_pct: Optional[float] = None,
    expected_target: Optional[float] = None,
    horizon_minutes: Optional[float] = None,
    status: FutureProjectionStatus = (
        FutureProjectionStatus.DEVELOPING
    ),
    **kwargs: Any,
) -> FutureProjection:

    projection = FutureProjection(
        projection_id=projection_id,
        instrument=instrument,
        direction=direction,
        current_price=current_price,
        expected_move_pct=expected_move_pct,
        expected_target=expected_target,
        horizon_minutes=horizon_minutes,
        status=status,
        timestamp=datetime.utcnow(),
        **kwargs,
    )

    return projection.normalize()


# ============================================================
# Public API
# ============================================================

__all__ = [
    "FutureDirection",
    "FutureHorizon",
    "FutureProjectionStatus",
    "FutureProjection",
    "FutureEvidence",
    "FutureContext",
    "FutureProjectionSnapshot",
    "build_future_projection",
]
# ============================================================
# future_model.py
# PART 2 — Scenario / Target Path / Uncertainty / Evolution
# ============================================================

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


# ============================================================
# Future Scenario Type
# ============================================================

class FutureScenarioType(str, Enum):
    """
    Forward market scenario classification.

    This is a model state, not a guaranteed prediction.
    """

    EXPANSION = "EXPANSION"
    CONTINUATION = "CONTINUATION"
    BREAKOUT = "BREAKOUT"
    BREAKDOWN = "BREAKDOWN"
    PULLBACK = "PULLBACK"
    REVERSAL = "REVERSAL"
    RANGE = "RANGE"
    EXHAUSTION = "EXHAUSTION"
    INVALIDATION = "INVALIDATION"
    UNKNOWN = "UNKNOWN"


# ============================================================
# Future Scenario
# ============================================================

@dataclass
class FutureScenario:
    """
    One possible future market path.

    Scenario strength represents model support for the scenario.
    It is not a probability unless explicitly validated upstream.
    """

    scenario_id: str = ""

    scenario_type: FutureScenarioType = (
        FutureScenarioType.UNKNOWN
    )

    direction: FutureDirection = (
        FutureDirection.UNKNOWN
    )

    horizon: FutureHorizon = (
        FutureHorizon.UNKNOWN
    )

    horizon_minutes: Optional[float] = None

    scenario_strength: float = 0.0

    current_price: Optional[float] = None

    expected_move_pct: Optional[float] = None
    expected_move_value: Optional[float] = None

    target_price: Optional[float] = None

    trigger_price: Optional[float] = None

    invalidation_price: Optional[float] = None

    supporting_evidence_ids: List[str] = field(
        default_factory=list
    )

    conflicting_evidence_ids: List[str] = field(
        default_factory=list
    )

    conditions: List[str] = field(
        default_factory=list
    )

    risks: List[str] = field(
        default_factory=list
    )

    active: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def normalize(self) -> "FutureScenario":
        numeric_fields = [
            "horizon_minutes",
            "scenario_strength",
            "current_price",
            "expected_move_pct",
            "expected_move_value",
            "target_price",
            "trigger_price",
            "invalidation_price",
        ]

        for field_name in numeric_fields:
            value = getattr(
                self,
                field_name,
                None,
            )

            if value is None:
                continue

            try:
                value = float(value)
            except (
                TypeError,
                ValueError,
            ):
                value = None

            setattr(
                self,
                field_name,
                value,
            )

        if self.scenario_strength is not None:
            self.scenario_strength = max(
                0.0,
                min(
                    100.0,
                    self.scenario_strength,
                ),
            )

        self.scenario_type = self._enum_value(
            self.scenario_type,
            FutureScenarioType,
            FutureScenarioType.UNKNOWN,
        )

        self.direction = self._enum_value(
            self.direction,
            FutureDirection,
            FutureDirection.UNKNOWN,
        )

        self.horizon = self._enum_value(
            self.horizon,
            FutureHorizon,
            FutureHorizon.UNKNOWN,
        )

        self.supporting_evidence_ids = list(
            dict.fromkeys(
                str(x)
                for x in self.supporting_evidence_ids
                if x is not None
            )
        )

        self.conflicting_evidence_ids = list(
            dict.fromkeys(
                str(x)
                for x in self.conflicting_evidence_ids
                if x is not None
            )
        )

        return self

    @staticmethod
    def _enum_value(
        value: Any,
        enum_cls: Any,
        default: Any,
    ) -> Any:
        if isinstance(
            value,
            enum_cls,
        ):
            return value

        try:
            return enum_cls(
                str(value).upper()
            )
        except (
            TypeError,
            ValueError,
        ):
            return default

    def is_directional(self) -> bool:
        return self.direction in {
            FutureDirection.BUY,
            FutureDirection.SELL,
            FutureDirection.CALL,
            FutureDirection.PUT,
        }

    def has_target(self) -> bool:
        return (
            self.target_price is not None
            and self.target_price > 0
        )

    def to_dict(self) -> Dict[str, Any]:
        self.normalize()

        return {
            "scenario_id": self.scenario_id,
            "scenario_type": (
                self.scenario_type.value
            ),
            "direction": (
                self.direction.value
            ),
            "horizon": (
                self.horizon.value
            ),
            "horizon_minutes": (
                self.horizon_minutes
            ),
            "scenario_strength": (
                self.scenario_strength
            ),
            "current_price": (
                self.current_price
            ),
            "expected_move_pct": (
                self.expected_move_pct
            ),
            "expected_move_value": (
                self.expected_move_value
            ),
            "target_price": (
                self.target_price
            ),
            "trigger_price": (
                self.trigger_price
            ),
            "invalidation_price": (
                self.invalidation_price
            ),
            "supporting_evidence_ids": list(
                self.supporting_evidence_ids
            ),
            "conflicting_evidence_ids": list(
                self.conflicting_evidence_ids
            ),
            "conditions": list(
                self.conditions
            ),
            "risks": list(
                self.risks
            ),
            "active": self.active,
            "metadata": dict(
                self.metadata
            ),
        }


# ============================================================
# Future Target Path
# ============================================================

@dataclass
class FutureTargetPath:
    """
    Expected path between current price and future target.

    Allows multiple intermediate levels rather than only one
    terminal target.
    """

    path_id: str = ""

    direction: FutureDirection = (
        FutureDirection.UNKNOWN
    )

    current_price: Optional[float] = None

    target_price: Optional[float] = None

    intermediate_levels: List[float] = field(
        default_factory=list
    )

    expected_move_pct: Optional[float] = None

    horizon_minutes: Optional[float] = None

    path_strength: float = 0.0

    path_valid: bool = False

    source_engine: str = "future_model"

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def normalize(self) -> "FutureTargetPath":
        numeric_fields = [
            "current_price",
            "target_price",
            "expected_move_pct",
            "horizon_minutes",
            "path_strength",
        ]

        for field_name in numeric_fields:
            value = getattr(
                self,
                field_name,
                None,
            )

            if value is None:
                continue

            try:
                value = float(value)
            except (
                TypeError,
                ValueError,
            ):
                value = None

            setattr(
                self,
                field_name,
                value,
            )

        self.intermediate_levels = [
            float(x)
            for x in self.intermediate_levels
            if self._is_numeric(x)
        ]

        try:
            self.direction = FutureDirection(
                str(
                    self.direction
                ).upper()
            )
        except (
            TypeError,
            ValueError,
        ):
            self.direction = (
                FutureDirection.UNKNOWN
            )

        self.path_strength = max(
            0.0,
            min(
                100.0,
                self.path_strength or 0.0,
            ),
        )

        return self

    @staticmethod
    def _is_numeric(
        value: Any,
    ) -> bool:
        try:
            float(value)
            return True
        except (
            TypeError,
            ValueError,
        ):
            return False

    def add_level(
        self,
        level: float,
    ) -> None:
        if self._is_numeric(level):
            self.intermediate_levels.append(
                float(level)
            )

            self.intermediate_levels = sorted(
                set(
                    self.intermediate_levels
                )
            )

    def to_dict(self) -> Dict[str, Any]:
        self.normalize()

        return {
            "path_id": self.path_id,
            "direction": (
                self.direction.value
            ),
            "current_price": (
                self.current_price
            ),
            "target_price": (
                self.target_price
            ),
            "intermediate_levels": list(
                self.intermediate_levels
            ),
            "expected_move_pct": (
                self.expected_move_pct
            ),
            "horizon_minutes": (
                self.horizon_minutes
            ),
            "path_strength": (
                self.path_strength
            ),
            "path_valid": self.path_valid,
            "source_engine": (
                self.source_engine
            ),
            "metadata": dict(
                self.metadata
            ),
        }


# ============================================================
# Future Uncertainty Context
# ============================================================

@dataclass
class FutureUncertainty:
    """
    Describes uncertainty around a future projection.

    This is intentionally not converted into a fabricated
    probability or win-rate.
    """

    uncertainty_score: float = 100.0

    data_uncertainty: float = 0.0
    regime_uncertainty: float = 0.0
    directional_uncertainty: float = 0.0
    volatility_uncertainty: float = 0.0
    liquidity_uncertainty: float = 0.0
    relationship_uncertainty: float = 0.0

    direction_stability: float = 0.0

    uncertainty_reasons: List[str] = field(
        default_factory=list
    )

    material: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def normalize(self) -> "FutureUncertainty":
        fields = [
            "uncertainty_score",
            "data_uncertainty",
            "regime_uncertainty",
            "directional_uncertainty",
            "volatility_uncertainty",
            "liquidity_uncertainty",
            "relationship_uncertainty",
            "direction_stability",
        ]

        for field_name in fields:
            try:
                value = float(
                    getattr(
                        self,
                        field_name,
                    )
                )
            except (
                TypeError,
                ValueError,
            ):
                value = 0.0

            setattr(
                self,
                field_name,
                max(
                    0.0,
                    min(
                        100.0,
                        value,
                    ),
                ),
            )

        return self

    def to_dict(self) -> Dict[str, Any]:
        self.normalize()

        return {
            "uncertainty_score": (
                self.uncertainty_score
            ),
            "data_uncertainty": (
                self.data_uncertainty
            ),
            "regime_uncertainty": (
                self.regime_uncertainty
            ),
            "directional_uncertainty": (
                self.directional_uncertainty
            ),
            "volatility_uncertainty": (
                self.volatility_uncertainty
            ),
            "liquidity_uncertainty": (
                self.liquidity_uncertainty
            ),
            "relationship_uncertainty": (
                self.relationship_uncertainty
            ),
            "direction_stability": (
                self.direction_stability
            ),
            "uncertainty_reasons": list(
                self.uncertainty_reasons
            ),
            "material": self.material,
            "metadata": dict(
                self.metadata
            ),
        }


# ============================================================
# Future Transition
# ============================================================

@dataclass
class FutureTransition:
    """
    Records a meaningful change from one future projection
    state to another.
    """

    transition_id: str = ""

    timestamp: Optional[datetime] = None

    previous_direction: FutureDirection = (
        FutureDirection.UNKNOWN
    )

    new_direction: FutureDirection = (
        FutureDirection.UNKNOWN
    )

    previous_scenario: FutureScenarioType = (
        FutureScenarioType.UNKNOWN
    )

    new_scenario: FutureScenarioType = (
        FutureScenarioType.UNKNOWN
    )

    previous_target: Optional[float] = None
    new_target: Optional[float] = None

    previous_expected_move_pct: Optional[float] = None
    new_expected_move_pct: Optional[float] = None

    trigger: str = ""

    material: bool = False

    evidence_ids: List[str] = field(
        default_factory=list
    )

    reason: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transition_id": (
                self.transition_id
            ),
            "timestamp": (
                self.timestamp.isoformat()
                if isinstance(
                    self.timestamp,
                    datetime,
                )
                else self.timestamp
            ),
            "previous_direction": (
                self.previous_direction.value
                if isinstance(
                    self.previous_direction,
                    FutureDirection,
                )
                else str(
                    self.previous_direction
                )
            ),
            "new_direction": (
                self.new_direction.value
                if isinstance(
                    self.new_direction,
                    FutureDirection,
                )
                else str(
                    self.new_direction
                )
            ),
            "previous_scenario": (
                self.previous_scenario.value
                if isinstance(
                    self.previous_scenario,
                    FutureScenarioType,
                )
                else str(
                    self.previous_scenario
                )
            ),
            "new_scenario": (
                self.new_scenario.value
                if isinstance(
                    self.new_scenario,
                    FutureScenarioType,
                )
                else str(
                    self.new_scenario
                )
            ),
            "previous_target": (
                self.previous_target
            ),
            "new_target": (
                self.new_target
            ),
            "previous_expected_move_pct": (
                self.previous_expected_move_pct
            ),
            "new_expected_move_pct": (
                self.new_expected_move_pct
            ),
            "trigger": self.trigger,
            "material": self.material,
            "evidence_ids": list(
                self.evidence_ids
            ),
            "reason": self.reason,
            "metadata": dict(
                self.metadata
            ),
        }


# ============================================================
# Future Evolution
# ============================================================

@dataclass
class FutureEvolution:
    """
    Tracks how a projection changes over time.
    """

    projection_id: str = ""

    snapshots: List[
        FutureProjectionSnapshot
    ] = field(default_factory=list)

    transitions: List[
        FutureTransition
    ] = field(default_factory=list)

    current_direction: FutureDirection = (
        FutureDirection.UNKNOWN
    )

    current_target: Optional[float] = None

    current_expected_move_pct: Optional[float] = None

    direction_changed: bool = False
    target_changed: bool = False
    scenario_changed: bool = False

    recalculation_required: bool = False

    last_update_at: Optional[datetime] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def add_snapshot(
        self,
        snapshot: FutureProjectionSnapshot,
    ) -> None:
        self.snapshots.append(snapshot)

        if len(self.snapshots) > 500:
            self.snapshots = self.snapshots[-500:]

        self.current_direction = (
            snapshot.direction
        )

        self.current_target = (
            snapshot.expected_target
        )

        self.current_expected_move_pct = (
            snapshot.expected_move_pct
        )

        self.recalculation_required = bool(
            snapshot.recalculation_required
        )

        self.last_update_at = (
            snapshot.timestamp
            or datetime.utcnow()
        )

    def add_transition(
        self,
        transition: FutureTransition,
    ) -> None:
        self.transitions.append(
            transition
        )

        if len(self.transitions) > 200:
            self.transitions = (
                self.transitions[-200:]
            )

        self.direction_changed = (
            transition.previous_direction
            != transition.new_direction
        )

        self.scenario_changed = (
            transition.previous_scenario
            != transition.new_scenario
        )

        self.target_changed = (
            transition.previous_target
            != transition.new_target
        )

        self.last_update_at = (
            transition.timestamp
            or datetime.utcnow()
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "projection_id": (
                self.projection_id
            ),
            "snapshots": [
                item.to_dict()
                for item in self.snapshots
            ],
            "transitions": [
                item.to_dict()
                for item in self.transitions
            ],
            "current_direction": (
                self.current_direction.value
                if isinstance(
                    self.current_direction,
                    FutureDirection,
                )
                else str(
                    self.current_direction
                )
            ),
            "current_target": (
                self.current_target
            ),
            "current_expected_move_pct": (
                self.current_expected_move_pct
            ),
            "direction_changed": (
                self.direction_changed
            ),
            "target_changed": (
                self.target_changed
            ),
            "scenario_changed": (
                self.scenario_changed
            ),
            "recalculation_required": (
                self.recalculation_required
            ),
            "last_update_at": (
                self.last_update_at.isoformat()
                if isinstance(
                    self.last_update_at,
                    datetime,
                )
                else self.last_update_at
            ),
            "metadata": dict(
                self.metadata
            ),
        }


# ============================================================
# Public API — Part 2
# ============================================================

__all__ += [
    "FutureScenarioType",
    "FutureScenario",
    "FutureTargetPath",
    "FutureUncertainty",
    "FutureTransition",
    "FutureEvolution",
]
# ============================================================
# ROBOMLM_PLUS
# FUTURE MODEL — PART 3
# Future Scenario Evaluation, Ranking & Projection State
# ============================================================

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ------------------------------------------------------------
# Future Scenario Evaluation
# ------------------------------------------------------------

@dataclass
class FutureScenarioEvaluation:
    """
    Evaluation of a future scenario using currently available
    market intelligence.

    This class evaluates scenario quality.
    It does NOT make the final D13 decision.
    """

    scenario_id: str = ""

    timestamp: Any = None

    direction: FutureDirection = FutureDirection.UNKNOWN

    scenario_type: FutureScenarioType = FutureScenarioType.UNKNOWN

    horizon: FutureHorizon = FutureHorizon.UNKNOWN

    scenario_score: float = 0.0
    evidence_score: float = 0.0
    structure_score: float = 0.0
    participation_score: float = 0.0
    breakout_score: float = 0.0
    confirmation_score: float = 0.0
    regime_score: float = 0.0
    relationship_score: float = 0.0
    liquidity_score: float = 0.0
    timing_score: float = 0.0

    expected_move_pct: float = 0.0
    expected_move_value: float = 0.0

    current_price: float = 0.0
    target_price: float = 0.0
    invalidation_price: float = 0.0

    active: bool = False
    valid: bool = False

    supporting_evidence_ids: List[str] = field(default_factory=list)
    conflicting_evidence_ids: List[str] = field(default_factory=list)

    reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    source_engines: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def normalize(self) -> "FutureScenarioEvaluation":
        self.scenario_score = max(0.0, min(100.0, float(self.scenario_score)))
        self.evidence_score = max(0.0, min(100.0, float(self.evidence_score)))
        self.structure_score = max(0.0, min(100.0, float(self.structure_score)))
        self.participation_score = max(
            0.0, min(100.0, float(self.participation_score))
        )
        self.breakout_score = max(0.0, min(100.0, float(self.breakout_score)))
        self.confirmation_score = max(
            0.0, min(100.0, float(self.confirmation_score))
        )
        self.regime_score = max(0.0, min(100.0, float(self.regime_score)))
        self.relationship_score = max(
            0.0, min(100.0, float(self.relationship_score))
        )
        self.liquidity_score = max(0.0, min(100.0, float(self.liquidity_score)))
        self.timing_score = max(0.0, min(100.0, float(self.timing_score)))

        self.expected_move_pct = float(self.expected_move_pct or 0.0)
        self.expected_move_value = float(self.expected_move_value or 0.0)

        self.current_price = float(self.current_price or 0.0)
        self.target_price = float(self.target_price or 0.0)
        self.invalidation_price = float(self.invalidation_price or 0.0)

        self.supporting_evidence_ids = list(
            self.supporting_evidence_ids or []
        )
        self.conflicting_evidence_ids = list(
            self.conflicting_evidence_ids or []
        )
        self.reasons = list(self.reasons or [])
        self.warnings = list(self.warnings or [])
        self.source_engines = list(self.source_engines or [])
        self.metadata = dict(self.metadata or {})

        return self

    def has_conflict(self) -> bool:
        return len(self.conflicting_evidence_ids) > 0

    def is_directional(self) -> bool:
        return self.direction in {
            FutureDirection.BUY,
            FutureDirection.SELL,
            FutureDirection.CALL,
            FutureDirection.PUT,
        }

    def to_dict(self) -> Dict[str, Any]:
        self.normalize()

        return {
            "scenario_id": self.scenario_id,
            "timestamp": self.timestamp,
            "direction": self.direction.value
            if isinstance(self.direction, FutureDirection)
            else str(self.direction),
            "scenario_type": self.scenario_type.value
            if isinstance(self.scenario_type, FutureScenarioType)
            else str(self.scenario_type),
            "horizon": self.horizon.value
            if isinstance(self.horizon, FutureHorizon)
            else str(self.horizon),
            "scenario_score": self.scenario_score,
            "evidence_score": self.evidence_score,
            "structure_score": self.structure_score,
            "participation_score": self.participation_score,
            "breakout_score": self.breakout_score,
            "confirmation_score": self.confirmation_score,
            "regime_score": self.regime_score,
            "relationship_score": self.relationship_score,
            "liquidity_score": self.liquidity_score,
            "timing_score": self.timing_score,
            "expected_move_pct": self.expected_move_pct,
            "expected_move_value": self.expected_move_value,
            "current_price": self.current_price,
            "target_price": self.target_price,
            "invalidation_price": self.invalidation_price,
            "active": self.active,
            "valid": self.valid,
            "supporting_evidence_ids": list(
                self.supporting_evidence_ids
            ),
            "conflicting_evidence_ids": list(
                self.conflicting_evidence_ids
            ),
            "reasons": list(self.reasons),
            "warnings": list(self.warnings),
            "source_engines": list(self.source_engines),
            "metadata": dict(self.metadata),
        }


# ------------------------------------------------------------
# Future Scenario Ranking
# ------------------------------------------------------------

@dataclass
class FutureScenarioRanking:
    """
    Ranked future scenarios.

    Ranking is an intelligence ordering mechanism.
    It is not the final D13 decision.
    """

    ranking_id: str = ""

    timestamp: Any = None

    scenarios: List[FutureScenarioEvaluation] = field(
        default_factory=list
    )

    best_scenario_id: Optional[str] = None

    ranking_method: str = "scenario_score_desc"

    valid: bool = False

    warnings: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def normalize(self) -> "FutureScenarioRanking":
        normalized = []

        for scenario in self.scenarios:
            if isinstance(scenario, FutureScenarioEvaluation):
                normalized.append(scenario.normalize())

        self.scenarios = normalized

        self.scenarios.sort(
            key=lambda item: item.scenario_score,
            reverse=True,
        )

        if self.scenarios:
            self.best_scenario_id = self.scenarios[0].scenario_id
            self.valid = True
        else:
            self.best_scenario_id = None
            self.valid = False

        self.warnings = list(self.warnings or [])
        self.metadata = dict(self.metadata or {})

        return self

    def top(
        self,
        limit: int = 5,
    ) -> List[FutureScenarioEvaluation]:
        self.normalize()

        limit = max(1, int(limit))

        return self.scenarios[:limit]

    def best(self) -> Optional[FutureScenarioEvaluation]:
        self.normalize()

        if not self.scenarios:
            return None

        return self.scenarios[0]

    def to_dict(self) -> Dict[str, Any]:
        self.normalize()

        return {
            "ranking_id": self.ranking_id,
            "timestamp": self.timestamp,
            "scenarios": [
                scenario.to_dict()
                for scenario in self.scenarios
            ],
            "best_scenario_id": self.best_scenario_id,
            "ranking_method": self.ranking_method,
            "valid": self.valid,
            "warnings": list(self.warnings),
            "metadata": dict(self.metadata),
        }


# ------------------------------------------------------------
# Future Projection State
# ------------------------------------------------------------

@dataclass
class FutureProjectionState:
    """
    Current state of future projection intelligence.

    Keeps the currently active projection together with its
    scenario ranking and evolution history.
    """

    projection_id: str = ""

    timestamp: Any = None

    current_projection: Optional[FutureProjection] = None

    scenario_ranking: Optional[FutureScenarioRanking] = None

    evolution: Optional[FutureEvolution] = None

    current_direction: FutureDirection = FutureDirection.UNKNOWN

    current_target: float = 0.0

    current_expected_move_pct: float = 0.0

    current_horizon_minutes: int = 0

    projection_valid: bool = False

    thesis_intact: bool = False

    anti_evidence_detected: bool = False

    exhaustion_detected: bool = False

    recalculation_required: bool = False

    state_changed: bool = False

    warnings: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def refresh(self) -> "FutureProjectionState":
        if self.current_projection is not None:
            self.current_projection.normalize()

            self.current_direction = (
                self.current_projection.direction
            )

            self.current_target = (
                self.current_projection.expected_target
            )

            self.current_expected_move_pct = (
                self.current_projection.expected_move_pct
            )

            self.current_horizon_minutes = (
                self.current_projection.horizon_minutes
            )

            self.projection_valid = (
                self.current_projection.is_valid()
            )

        if self.scenario_ranking is not None:
            self.scenario_ranking.normalize()

        self.warnings = list(self.warnings or [])
        self.metadata = dict(self.metadata or {})

        return self

    def is_actionable_projection(self) -> bool:
        self.refresh()

        return (
            self.projection_valid
            and self.thesis_intact
            and self.current_direction
            in {
                FutureDirection.BUY,
                FutureDirection.SELL,
                FutureDirection.CALL,
                FutureDirection.PUT,
            }
            and self.current_target > 0
            and self.current_horizon_minutes > 0
        )

    def to_dict(self) -> Dict[str, Any]:
        self.refresh()

        return {
            "projection_id": self.projection_id,
            "timestamp": self.timestamp,
            "current_projection": (
                self.current_projection.to_dict()
                if self.current_projection is not None
                else None
            ),
            "scenario_ranking": (
                self.scenario_ranking.to_dict()
                if self.scenario_ranking is not None
                else None
            ),
            "evolution": (
                self.evolution.to_dict()
                if self.evolution is not None
                else None
            ),
            "current_direction": (
                self.current_direction.value
                if isinstance(
                    self.current_direction,
                    FutureDirection,
                )
                else str(self.current_direction)
            ),
            "current_target": self.current_target,
            "current_expected_move_pct": (
                self.current_expected_move_pct
            ),
            "current_horizon_minutes": (
                self.current_horizon_minutes
            ),
            "projection_valid": self.projection_valid,
            "thesis_intact": self.thesis_intact,
            "anti_evidence_detected": (
                self.anti_evidence_detected
            ),
            "exhaustion_detected": self.exhaustion_detected,
            "recalculation_required": (
                self.recalculation_required
            ),
            "state_changed": self.state_changed,
            "warnings": list(self.warnings),
            "metadata": dict(self.metadata),
        }


# ------------------------------------------------------------
# Future Model Engine
# ------------------------------------------------------------

class FutureModelEngine:
    """
    Future intelligence aggregation layer.

    Responsibilities:
        1. Evaluate future scenarios.
        2. Rank scenarios.
        3. Maintain projection state.
        4. Detect material projection changes.
        5. Prepare normalized intelligence for downstream engines.

    It does NOT:
        - invent market data
        - fabricate probability
        - make the final D13 decision
        - force a BUY/SELL outcome without evidence
    """

    ENGINE_NAME = "FutureModelEngine"
    ENGINE_VERSION = "1.0.0"

    def __init__(
        self,
        minimum_scenario_score: float = 35.0,
        minimum_evidence_score: float = 40.0,
    ) -> None:

        self.minimum_scenario_score = float(
            minimum_scenario_score
        )

        self.minimum_evidence_score = float(
            minimum_evidence_score
        )

    @staticmethod
    def _clamp(
        value: float,
        low: float = 0.0,
        high: float = 100.0,
    ) -> float:

        return max(
            low,
            min(high, float(value)),
        )

    def calculate_scenario_score(
        self,
        structure_score: float = 0.0,
        participation_score: float = 0.0,
        breakout_score: float = 0.0,
        confirmation_score: float = 0.0,
        regime_score: float = 0.0,
        relationship_score: float = 0.0,
        liquidity_score: float = 0.0,
        timing_score: float = 0.0,
        evidence_score: float = 0.0,
    ) -> float:

        """
        Initial aggregation baseline.

        These weights are engineering baselines only.
        Final calibration must come from real market validation.
        """

        score = (
            structure_score * 0.18
            + participation_score * 0.12
            + breakout_score * 0.12
            + confirmation_score * 0.14
            + regime_score * 0.10
            + relationship_score * 0.08
            + liquidity_score * 0.08
            + timing_score * 0.08
            + evidence_score * 0.10
        )

        return self._clamp(score)

    def evaluate_scenario(
        self,
        scenario: FutureScenario,
        evidence_score: float = 0.0,
        structure_score: float = 0.0,
        participation_score: float = 0.0,
        breakout_score: float = 0.0,
        confirmation_score: float = 0.0,
        regime_score: float = 0.0,
        relationship_score: float = 0.0,
        liquidity_score: float = 0.0,
        timing_score: float = 0.0,
    ) -> FutureScenarioEvaluation:

        scenario.normalize()

        score = self.calculate_scenario_score(
            structure_score=structure_score,
            participation_score=participation_score,
            breakout_score=breakout_score,
            confirmation_score=confirmation_score,
            regime_score=regime_score,
            relationship_score=relationship_score,
            liquidity_score=liquidity_score,
            timing_score=timing_score,
            evidence_score=evidence_score,
        )

        valid = (
            scenario.active
            and scenario.is_directional()
            and score >= self.minimum_scenario_score
            and evidence_score >= self.minimum_evidence_score
        )

        warnings = []

        if evidence_score < self.minimum_evidence_score:
            warnings.append(
                "Insufficient evidence strength"
            )

        if not scenario.is_directional():
            warnings.append(
                "Scenario has no actionable direction"
            )

        if not scenario.has_target():
            warnings.append(
                "Scenario has no valid target"
            )

        return FutureScenarioEvaluation(
            scenario_id=scenario.scenario_id,
            timestamp=None,
            direction=scenario.direction,
            scenario_type=scenario.scenario_type,
            horizon=scenario.horizon,
            scenario_score=score,
            evidence_score=self._clamp(evidence_score),
            structure_score=self._clamp(structure_score),
            participation_score=self._clamp(
                participation_score
            ),
            breakout_score=self._clamp(
                breakout_score
            ),
            confirmation_score=self._clamp(
                confirmation_score
            ),
            regime_score=self._clamp(regime_score),
            relationship_score=self._clamp(
                relationship_score
            ),
            liquidity_score=self._clamp(
                liquidity_score
            ),
            timing_score=self._clamp(timing_score),
            expected_move_pct=scenario.expected_move_pct,
            expected_move_value=scenario.expected_move_value,
            current_price=scenario.current_price,
            target_price=scenario.target_price,
            invalidation_price=scenario.invalidation_price,
            active=scenario.active,
            valid=valid,
            supporting_evidence_ids=list(
                scenario.supporting_evidence_ids
            ),
            conflicting_evidence_ids=list(
                scenario.conflicting_evidence_ids
            ),
            reasons=list(scenario.conditions),
            warnings=warnings + list(scenario.risks),
            source_engines=[
                self.ENGINE_NAME,
            ],
            metadata={
                "engine": self.ENGINE_NAME,
                "engine_version": self.ENGINE_VERSION,
            },
        )

    def rank_scenarios(
        self,
        evaluations: List[FutureScenarioEvaluation],
        ranking_id: str = "",
        timestamp: Any = None,
    ) -> FutureScenarioRanking:

        valid_evaluations = [
            item.normalize()
            for item in (evaluations or [])
            if isinstance(item, FutureScenarioEvaluation)
        ]

        ranking = FutureScenarioRanking(
            ranking_id=ranking_id,
            timestamp=timestamp,
            scenarios=valid_evaluations,
            ranking_method="scenario_score_desc",
        )

        return ranking.normalize()

    def build_state(
        self,
        projection: Optional[FutureProjection] = None,
        ranking: Optional[FutureScenarioRanking] = None,
        evolution: Optional[FutureEvolution] = None,
        thesis_intact: bool = False,
        anti_evidence_detected: bool = False,
        exhaustion_detected: bool = False,
        recalculation_required: bool = False,
        timestamp: Any = None,
    ) -> FutureProjectionState:

        state = FutureProjectionState(
            projection_id=(
                projection.projection_id
                if projection is not None
                else ""
            ),
            timestamp=timestamp,
            current_projection=projection,
            scenario_ranking=ranking,
            evolution=evolution,
            thesis_intact=bool(thesis_intact),
            anti_evidence_detected=bool(
                anti_evidence_detected
            ),
            exhaustion_detected=bool(
                exhaustion_detected
            ),
            recalculation_required=bool(
                recalculation_required
            ),
        )

        return state.refresh()


# ------------------------------------------------------------
# Factory Helpers
# ------------------------------------------------------------

def evaluate_future_scenario(
    scenario: FutureScenario,
    **scores: float,
) -> FutureScenarioEvaluation:

    engine = FutureModelEngine()

    return engine.evaluate_scenario(
        scenario=scenario,
        **scores,
    )


def rank_future_scenarios(
    evaluations: List[FutureScenarioEvaluation],
    ranking_id: str = "",
    timestamp: Any = None,
) -> FutureScenarioRanking:

    engine = FutureModelEngine()

    return engine.rank_scenarios(
        evaluations=evaluations,
        ranking_id=ranking_id,
        timestamp=timestamp,
    )


def build_future_projection_state(
    projection: Optional[FutureProjection] = None,
    ranking: Optional[FutureScenarioRanking] = None,
    evolution: Optional[FutureEvolution] = None,
    thesis_intact: bool = False,
    anti_evidence_detected: bool = False,
    exhaustion_detected: bool = False,
    recalculation_required: bool = False,
    timestamp: Any = None,
) -> FutureProjectionState:

    engine = FutureModelEngine()

    return engine.build_state(
        projection=projection,
        ranking=ranking,
        evolution=evolution,
        thesis_intact=thesis_intact,
        anti_evidence_detected=anti_evidence_detected,
        exhaustion_detected=exhaustion_detected,
        recalculation_required=recalculation_required,
        timestamp=timestamp,
    )


# ------------------------------------------------------------
# Public API — PART 3
# ------------------------------------------------------------

__all__ += [
    "FutureScenarioEvaluation",
    "FutureScenarioRanking",
    "FutureProjectionState",
    "FutureModelEngine",
    "evaluate_future_scenario",
    "rank_future_scenarios",
    "build_future_projection_state",
]
# ============================================================
# ROBOMLM_PLUS
# FUTURE MODEL — PART 4
# Future Monitoring, Anti-Evidence, Exhaustion & Recalculation
# ============================================================

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ------------------------------------------------------------
# Future Anti-Evidence
# ------------------------------------------------------------

@dataclass
class FutureAntiEvidence:
    """
    Material evidence that conflicts with the active future thesis.

    This does not automatically execute an exit.
    It informs downstream decision/risk layers.
    """

    detected: bool = False
    strength: float = 0.0

    direction: FutureDirection = FutureDirection.UNKNOWN

    evidence_ids: List[str] = field(default_factory=list)
    source_engines: List[str] = field(default_factory=list)

    price_conflict: bool = False
    structure_conflict: bool = False
    participation_conflict: bool = False
    derivative_conflict: bool = False
    relationship_conflict: bool = False
    regime_conflict: bool = False

    reasons: List[str] = field(default_factory=list)

    thesis_review_required: bool = False
    recalculation_required: bool = False
    exit_review_required: bool = False

    timestamp: Any = None

    metadata: Dict[str, Any] = field(default_factory=dict)

    def normalize(self) -> "FutureAntiEvidence":
        self.strength = max(
            0.0,
            min(100.0, float(self.strength)),
        )

        self.evidence_ids = list(
            self.evidence_ids or []
        )
        self.source_engines = list(
            self.source_engines or []
        )
        self.reasons = list(
            self.reasons or []
        )
        self.metadata = dict(
            self.metadata or {}
        )

        return self

    def is_material(self) -> bool:
        self.normalize()

        return (
            self.detected
            and self.strength >= 50.0
        )

    def to_dict(self) -> Dict[str, Any]:
        self.normalize()

        return {
            "detected": self.detected,
            "strength": self.strength,
            "direction": (
                self.direction.value
                if isinstance(
                    self.direction,
                    FutureDirection,
                )
                else str(self.direction)
            ),
            "evidence_ids": list(self.evidence_ids),
            "source_engines": list(self.source_engines),
            "price_conflict": self.price_conflict,
            "structure_conflict": self.structure_conflict,
            "participation_conflict": self.participation_conflict,
            "derivative_conflict": self.derivative_conflict,
            "relationship_conflict": self.relationship_conflict,
            "regime_conflict": self.regime_conflict,
            "reasons": list(self.reasons),
            "thesis_review_required": (
                self.thesis_review_required
            ),
            "recalculation_required": (
                self.recalculation_required
            ),
            "exit_review_required": (
                self.exit_review_required
            ),
            "timestamp": self.timestamp,
            "metadata": dict(self.metadata),
        }


# ------------------------------------------------------------
# Future Continuation
# ------------------------------------------------------------

@dataclass
class FutureContinuation:
    """
    Evidence that the original future thesis remains valid.

    Continuation is not a guarantee of outcome.
    """

    active: bool = False
    strength: float = 0.0

    direction: FutureDirection = FutureDirection.UNKNOWN

    factors: List[str] = field(default_factory=list)
    supporting_evidence_ids: List[str] = field(
        default_factory=list
    )
    source_engines: List[str] = field(
        default_factory=list
    )

    last_confirmed_at: Any = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def normalize(self) -> "FutureContinuation":
        self.strength = max(
            0.0,
            min(100.0, float(self.strength)),
        )

        self.factors = list(
            self.factors or []
        )

        self.supporting_evidence_ids = list(
            self.supporting_evidence_ids or []
        )

        self.source_engines = list(
            self.source_engines or []
        )

        self.metadata = dict(
            self.metadata or {}
        )

        return self

    def is_strong(self) -> bool:
        self.normalize()

        return (
            self.active
            and self.strength >= 60.0
        )

    def to_dict(self) -> Dict[str, Any]:
        self.normalize()

        return {
            "active": self.active,
            "strength": self.strength,
            "direction": (
                self.direction.value
                if isinstance(
                    self.direction,
                    FutureDirection,
                )
                else str(self.direction)
            ),
            "factors": list(self.factors),
            "supporting_evidence_ids": list(
                self.supporting_evidence_ids
            ),
            "source_engines": list(
                self.source_engines
            ),
            "last_confirmed_at": (
                self.last_confirmed_at
            ),
            "metadata": dict(self.metadata),
        }


# ------------------------------------------------------------
# Future Exhaustion
# ------------------------------------------------------------

@dataclass
class FutureExhaustion:
    """
    Detects weakening / exhaustion of the projected move.

    Exhaustion is separate from thesis invalidation.
    """

    detected: bool = False
    strength: float = 0.0

    exhaustion_type: str = ""

    price_extension: float = 0.0
    momentum_decay: float = 0.0
    participation_decay: float = 0.0
    liquidity_deterioration: float = 0.0
    opposing_pressure: float = 0.0

    reasons: List[str] = field(
        default_factory=list
    )

    exit_review_required: bool = False
    recalculation_required: bool = False

    source_engines: List[str] = field(
        default_factory=list
    )

    timestamp: Any = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def normalize(self) -> "FutureExhaustion":
        self.strength = max(
            0.0,
            min(100.0, float(self.strength)),
        )

        self.price_extension = max(
            0.0,
            min(100.0, float(self.price_extension)),
        )

        self.momentum_decay = max(
            0.0,
            min(100.0, float(self.momentum_decay)),
        )

        self.participation_decay = max(
            0.0,
            min(100.0, float(self.participation_decay)),
        )

        self.liquidity_deterioration = max(
            0.0,
            min(100.0, float(
                self.liquidity_deterioration
            )),
        )

        self.opposing_pressure = max(
            0.0,
            min(100.0, float(
                self.opposing_pressure
            )),
        )

        self.reasons = list(
            self.reasons or []
        )

        self.source_engines = list(
            self.source_engines or []
        )

        self.metadata = dict(
            self.metadata or {}
        )

        return self

    def is_material(self) -> bool:
        self.normalize()

        return (
            self.detected
            and self.strength >= 60.0
        )

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
            "recalculation_required": (
                self.recalculation_required
            ),
            "source_engines": list(
                self.source_engines
            ),
            "timestamp": self.timestamp,
            "metadata": dict(self.metadata),
        }


# ------------------------------------------------------------
# Future Recalculation
# ------------------------------------------------------------

@dataclass
class FutureRecalculation:
    """
    Tracks recalculation of a future projection after
    material market-state change.
    """

    required: bool = False

    trigger_type: str = ""

    reason: str = ""

    previous_direction: FutureDirection = (
        FutureDirection.UNKNOWN
    )

    previous_target: float = 0.0
    previous_expected_move_pct: float = 0.0
    previous_horizon_minutes: int = 0

    new_direction: FutureDirection = (
        FutureDirection.UNKNOWN
    )

    new_target: float = 0.0
    new_expected_move_pct: float = 0.0
    new_horizon_minutes: int = 0

    recalculation_count: int = 0

    requested_at: Any = None
    completed_at: Any = None

    result_status: str = "PENDING"

    evidence_ids: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def request(
        self,
        trigger_type: str,
        reason: str,
        timestamp: Any = None,
    ) -> None:

        self.required = True
        self.trigger_type = str(
            trigger_type or ""
        )
        self.reason = str(
            reason or ""
        )
        self.requested_at = timestamp
        self.result_status = "PENDING"

    def complete(
        self,
        direction: FutureDirection,
        target: float,
        expected_move_pct: float,
        horizon_minutes: int,
        timestamp: Any = None,
        result_status: str = "COMPLETED",
    ) -> None:

        self.new_direction = direction
        self.new_target = float(
            target or 0.0
        )
        self.new_expected_move_pct = float(
            expected_move_pct or 0.0
        )
        self.new_horizon_minutes = int(
            horizon_minutes or 0
        )

        self.completed_at = timestamp
        self.result_status = str(
            result_status
        )

        self.recalculation_count += 1
        self.required = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "required": self.required,
            "trigger_type": self.trigger_type,
            "reason": self.reason,
            "previous_direction": (
                self.previous_direction.value
                if isinstance(
                    self.previous_direction,
                    FutureDirection,
                )
                else str(self.previous_direction)
            ),
            "previous_target": self.previous_target,
            "previous_expected_move_pct": (
                self.previous_expected_move_pct
            ),
            "previous_horizon_minutes": (
                self.previous_horizon_minutes
            ),
            "new_direction": (
                self.new_direction.value
                if isinstance(
                    self.new_direction,
                    FutureDirection,
                )
                else str(self.new_direction)
            ),
            "new_target": self.new_target,
            "new_expected_move_pct": (
                self.new_expected_move_pct
            ),
            "new_horizon_minutes": (
                self.new_horizon_minutes
            ),
            "recalculation_count": (
                self.recalculation_count
            ),
            "requested_at": self.requested_at,
            "completed_at": self.completed_at,
            "result_status": self.result_status,
            "evidence_ids": list(
                self.evidence_ids
            ),
            "warnings": list(
                self.warnings
            ),
            "metadata": dict(
                self.metadata
            ),
        }


# ------------------------------------------------------------
# Future Monitoring Snapshot
# ------------------------------------------------------------

@dataclass
class FutureMonitoringSnapshot:
    """
    Point-in-time monitoring record for an active projection.
    """

    snapshot_id: str = ""
    projection_id: str = ""

    timestamp: Any = None

    current_price: float = 0.0

    direction: FutureDirection = (
        FutureDirection.UNKNOWN
    )

    expected_target: float = 0.0
    expected_move_pct: float = 0.0
    horizon_minutes: int = 0

    thesis_intact: bool = False

    continuation_strength: float = 0.0
    anti_evidence_strength: float = 0.0
    exhaustion_strength: float = 0.0

    anti_evidence_detected: bool = False
    exhaustion_detected: bool = False

    recalculation_required: bool = False
    exit_review_required: bool = False

    projection_valid: bool = False

    reasons: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def normalize(self) -> "FutureMonitoringSnapshot":
        self.current_price = float(
            self.current_price or 0.0
        )

        self.expected_target = float(
            self.expected_target or 0.0
        )

        self.expected_move_pct = float(
            self.expected_move_pct or 0.0
        )

        self.horizon_minutes = int(
            self.horizon_minutes or 0
        )

        self.continuation_strength = max(
            0.0,
            min(
                100.0,
                float(
                    self.continuation_strength
                ),
            ),
        )

        self.anti_evidence_strength = max(
            0.0,
            min(
                100.0,
                float(
                    self.anti_evidence_strength
                ),
            ),
        )

        self.exhaustion_strength = max(
            0.0,
            min(
                100.0,
                float(
                    self.exhaustion_strength
                ),
            ),
        )

        self.reasons = list(
            self.reasons or []
        )

        self.metadata = dict(
            self.metadata or {}
        )

        return self

    def to_dict(self) -> Dict[str, Any]:
        self.normalize()

        return {
            "snapshot_id": self.snapshot_id,
            "projection_id": self.projection_id,
            "timestamp": self.timestamp,
            "current_price": self.current_price,
            "direction": (
                self.direction.value
                if isinstance(
                    self.direction,
                    FutureDirection,
                )
                else str(self.direction)
            ),
            "expected_target": self.expected_target,
            "expected_move_pct": (
                self.expected_move_pct
            ),
            "horizon_minutes": (
                self.horizon_minutes
            ),
            "thesis_intact": self.thesis_intact,
            "continuation_strength": (
                self.continuation_strength
            ),
            "anti_evidence_strength": (
                self.anti_evidence_strength
            ),
            "exhaustion_strength": (
                self.exhaustion_strength
            ),
            "anti_evidence_detected": (
                self.anti_evidence_detected
            ),
            "exhaustion_detected": (
                self.exhaustion_detected
            ),
            "recalculation_required": (
                self.recalculation_required
            ),
            "exit_review_required": (
                self.exit_review_required
            ),
            "projection_valid": (
                self.projection_valid
            ),
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }


# ------------------------------------------------------------
# Future Monitoring State
# ------------------------------------------------------------

@dataclass
class FutureMonitoringState:
    """
    Complete live monitoring state of a future projection.

    This is the bridge between future projection and
    downstream opportunity / decision intelligence.
    """

    projection_id: str = ""

    timestamp: Any = None

    projection_state: Optional[
        FutureProjectionState
    ] = None

    continuation: FutureContinuation = field(
        default_factory=FutureContinuation
    )

    anti_evidence: FutureAntiEvidence = field(
        default_factory=FutureAntiEvidence
    )

    exhaustion: FutureExhaustion = field(
        default_factory=FutureExhaustion
    )

    recalculation: FutureRecalculation = field(
        default_factory=FutureRecalculation
    )

    snapshots: List[
        FutureMonitoringSnapshot
    ] = field(default_factory=list)

    thesis_intact: bool = False

    monitoring_active: bool = False

    action_review_required: bool = False

    warnings: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def add_snapshot(
        self,
        snapshot: FutureMonitoringSnapshot,
    ) -> None:

        if not isinstance(
            snapshot,
            FutureMonitoringSnapshot,
        ):
            return

        self.snapshots.append(
            snapshot.normalize()
        )

        # Keep monitoring history bounded.
        if len(self.snapshots) > 500:
            self.snapshots = self.snapshots[-500:]

        self.timestamp = snapshot.timestamp

    def refresh(self) -> "FutureMonitoringState":

        self.continuation.normalize()
        self.anti_evidence.normalize()
        self.exhaustion.normalize()

        if (
            self.anti_evidence.is_material()
        ):
            self.thesis_intact = False
            self.action_review_required = True

        elif (
            self.exhaustion.is_material()
        ):
            self.action_review_required = True

        elif self.continuation.is_strong():
            self.thesis_intact = True

        self.monitoring_active = (
            self.thesis_intact
            and not self.recalculation.required
        )

        self.warnings = list(
            self.warnings or []
        )

        self.metadata = dict(
            self.metadata or {}
        )

        return self

    def needs_recalculation(self) -> bool:
        self.refresh()

        return (
            self.recalculation.required
            or self.anti_evidence.recalculation_required
            or self.exhaustion.recalculation_required
        )

    def needs_exit_review(self) -> bool:
        self.refresh()

        return (
            self.anti_evidence.exit_review_required
            or self.exhaustion.exit_review_required
        )

    def to_dict(self) -> Dict[str, Any]:
        self.refresh()

        return {
            "projection_id": self.projection_id,
            "timestamp": self.timestamp,
            "projection_state": (
                self.projection_state.to_dict()
                if self.projection_state is not None
                else None
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
            "snapshots": [
                item.to_dict()
                for item in self.snapshots
            ],
            "thesis_intact": (
                self.thesis_intact
            ),
            "monitoring_active": (
                self.monitoring_active
            ),
            "action_review_required": (
                self.action_review_required
            ),
            "warnings": list(
                self.warnings
            ),
            "metadata": dict(
                self.metadata
            ),
        }


# ------------------------------------------------------------
# Future Monitoring Engine
# ------------------------------------------------------------

class FutureMonitoringEngine:
    """
    Monitoring layer for future intelligence.

    Flow:

        Active Projection
              ↓
        Continuation Check
              ↓
        Anti-Evidence Check
              ↓
        Exhaustion Check
              ↓
        Recalculation / Review
              ↓
        Downstream Decision Intelligence

    No fabricated probability.
    No forced trade.
    No direct D13 override.
    """

    ENGINE_NAME = "FutureMonitoringEngine"
    ENGINE_VERSION = "1.0.0"

    def build_snapshot(
        self,
        projection: FutureProjection,
        thesis_intact: bool,
        continuation_strength: float = 0.0,
        anti_evidence_strength: float = 0.0,
        exhaustion_strength: float = 0.0,
        anti_evidence_detected: bool = False,
        exhaustion_detected: bool = False,
        recalculation_required: bool = False,
        exit_review_required: bool = False,
        timestamp: Any = None,
        snapshot_id: str = "",
    ) -> FutureMonitoringSnapshot:

        projection.normalize()

        snapshot = FutureMonitoringSnapshot(
            snapshot_id=snapshot_id,
            projection_id=projection.projection_id,
            timestamp=timestamp,
            current_price=projection.current_price,
            direction=projection.direction,
            expected_target=projection.expected_target,
            expected_move_pct=projection.expected_move_pct,
            horizon_minutes=projection.horizon_minutes,
            thesis_intact=bool(thesis_intact),
            continuation_strength=(
                continuation_strength
            ),
            anti_evidence_strength=(
                anti_evidence_strength
            ),
            exhaustion_strength=(
                exhaustion_strength
            ),
            anti_evidence_detected=(
                anti_evidence_detected
            ),
            exhaustion_detected=(
                exhaustion_detected
            ),
            recalculation_required=(
                recalculation_required
            ),
            exit_review_required=(
                exit_review_required
            ),
            projection_valid=projection.is_valid(),
        )

        return snapshot.normalize()

    def update_state(
        self,
        state: FutureMonitoringState,
        snapshot: FutureMonitoringSnapshot,
    ) -> FutureMonitoringState:

        state.add_snapshot(snapshot)

        if snapshot.anti_evidence_detected:
            state.anti_evidence.detected = True
            state.anti_evidence.strength = max(
                state.anti_evidence.strength,
                snapshot.anti_evidence_strength,
            )

        if snapshot.exhaustion_detected:
            state.exhaustion.detected = True
            state.exhaustion.strength = max(
                state.exhaustion.strength,
                snapshot.exhaustion_strength,
            )

        if snapshot.recalculation_required:
            state.recalculation.required = True

        if snapshot.exit_review_required:
            state.action_review_required = True

        state.thesis_intact = snapshot.thesis_intact

        return state.refresh()


# ------------------------------------------------------------
# Public API — PART 4
# ------------------------------------------------------------

__all__ += [
    "FutureAntiEvidence",
    "FutureContinuation",
    "FutureExhaustion",
    "FutureRecalculation",
    "FutureMonitoringSnapshot",
    "FutureMonitoringState",
    "FutureMonitoringEngine",
]
# ============================================================
# ROBOMLM_PLUS
# FUTURE MODEL — PART 5
# Validation, Audit, Serialization & Public API
# ============================================================

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ------------------------------------------------------------
# Validation Issue
# ------------------------------------------------------------

@dataclass
class FutureValidationIssue:
    code: str = ""
    message: str = ""
    severity: str = "ERROR"
    field: str = ""
    projection_id: str = ""
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "field": self.field,
            "projection_id": self.projection_id,
            "metadata": dict(self.metadata),
        }


# ------------------------------------------------------------
# Validation Result
# ------------------------------------------------------------

@dataclass
class FutureValidationResult:
    valid: bool = True

    issues: List[FutureValidationIssue] = field(
        default_factory=list
    )

    warnings: List[FutureValidationIssue] = field(
        default_factory=list
    )

    checked_at: Any = None

    engine: str = "FutureModel"
    version: str = "1.0.0"

    def add_issue(
        self,
        code: str,
        message: str,
        severity: str = "ERROR",
        field: str = "",
        projection_id: str = "",
        warning: bool = False,
    ) -> None:

        issue = FutureValidationIssue(
            code=code,
            message=message,
            severity=severity,
            field=field,
            projection_id=projection_id,
        )

        if warning:
            self.warnings.append(issue)
        else:
            self.issues.append(issue)

        if severity.upper() == "ERROR" and not warning:
            self.valid = False

    def finalize(self) -> "FutureValidationResult":
        self.valid = len(self.issues) == 0
        return self

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "issues": [
                item.to_dict()
                for item in self.issues
            ],
            "warnings": [
                item.to_dict()
                for item in self.warnings
            ],
            "checked_at": self.checked_at,
            "engine": self.engine,
            "version": self.version,
        }


# ------------------------------------------------------------
# Future Model Validator
# ------------------------------------------------------------

class FutureModelValidator:
    """
    Structural and contract validation for Future Model.

    This validator checks whether the future intelligence object
    is internally usable.

    It does NOT validate whether the market prediction was correct.
    Prediction quality is validated later through real outcomes.
    """

    ENGINE_NAME = "FutureModelValidator"
    ENGINE_VERSION = "1.0.0"

    VALID_DIRECTIONS = {
        FutureDirection.BUY,
        FutureDirection.SELL,
        FutureDirection.CALL,
        FutureDirection.PUT,
        FutureDirection.NEUTRAL,
        FutureDirection.UNKNOWN,
    }

    VALID_STATUSES = {
        FutureProjectionStatus.AVAILABLE,
        FutureProjectionStatus.DEVELOPING,
        FutureProjectionStatus.INVALIDATED,
        FutureProjectionStatus.EXHAUSTED,
        FutureProjectionStatus.INSUFFICIENT_DATA,
        FutureProjectionStatus.UNKNOWN,
    }

    def validate_projection(
        self,
        projection: Optional[FutureProjection],
        checked_at: Any = None,
    ) -> FutureValidationResult:

        result = FutureValidationResult(
            checked_at=checked_at,
            engine=self.ENGINE_NAME,
            version=self.ENGINE_VERSION,
        )

        if projection is None:
            result.add_issue(
                code="FUTURE_NULL_PROJECTION",
                message="Future projection is missing.",
            )
            return result.finalize()

        projection.normalize()

        projection_id = projection.projection_id

        if not projection_id:
            result.add_issue(
                code="FUTURE_MISSING_ID",
                message="Projection ID is missing.",
                field="projection_id",
                projection_id=projection_id,
            )

        if not projection.instrument:
            result.add_issue(
                code="FUTURE_MISSING_INSTRUMENT",
                message="Instrument is missing.",
                field="instrument",
                projection_id=projection_id,
            )

        if not projection.exchange:
            result.add_issue(
                code="FUTURE_MISSING_EXCHANGE",
                message="Exchange is missing.",
                field="exchange",
                projection_id=projection_id,
            )

        if projection.direction not in self.VALID_DIRECTIONS:
            result.add_issue(
                code="FUTURE_INVALID_DIRECTION",
                message="Invalid future projection direction.",
                field="direction",
                projection_id=projection_id,
            )

        if projection.status not in self.VALID_STATUSES:
            result.add_issue(
                code="FUTURE_INVALID_STATUS",
                message="Invalid projection status.",
                field="status",
                projection_id=projection_id,
            )

        if not (
            0.0
            <= projection.projection_strength
            <= 100.0
        ):
            result.add_issue(
                code="FUTURE_INVALID_STRENGTH",
                message="Projection strength must be between 0 and 100.",
                field="projection_strength",
                projection_id=projection_id,
            )

        if projection.current_price < 0:
            result.add_issue(
                code="FUTURE_INVALID_PRICE",
                message="Current price cannot be negative.",
                field="current_price",
                projection_id=projection_id,
            )

        if projection.expected_move_pct < 0:
            result.add_issue(
                code="FUTURE_INVALID_EXPECTED_MOVE",
                message="Expected move percentage cannot be negative.",
                field="expected_move_pct",
                projection_id=projection_id,
            )

        if projection.horizon_minutes < 0:
            result.add_issue(
                code="FUTURE_INVALID_HORIZON",
                message="Horizon cannot be negative.",
                field="horizon_minutes",
                projection_id=projection_id,
            )

        if projection.is_directional():

            if projection.expected_move_pct <= 0:
                result.add_issue(
                    code="FUTURE_DIRECTIONAL_NO_MOVE",
                    message=(
                        "Directional projection does not contain "
                        "a positive expected move."
                    ),
                    severity="WARNING",
                    field="expected_move_pct",
                    projection_id=projection_id,
                    warning=True,
                )

            if projection.expected_target <= 0:
                result.add_issue(
                    code="FUTURE_DIRECTIONAL_NO_TARGET",
                    message=(
                        "Directional projection does not contain "
                        "a valid expected target."
                    ),
                    severity="WARNING",
                    field="expected_target",
                    projection_id=projection_id,
                    warning=True,
                )

            if projection.horizon_minutes <= 0:
                result.add_issue(
                    code="FUTURE_DIRECTIONAL_NO_HORIZON",
                    message=(
                        "Directional projection does not contain "
                        "a valid horizon."
                    ),
                    severity="WARNING",
                    field="horizon_minutes",
                    projection_id=projection_id,
                    warning=True,
                )

        if (
            projection.status
            == FutureProjectionStatus.AVAILABLE
            and projection.projection_strength <= 0
        ):
            result.add_issue(
                code="FUTURE_AVAILABLE_ZERO_STRENGTH",
                message=(
                    "Projection is marked AVAILABLE but "
                    "projection strength is zero."
                ),
                severity="WARNING",
                projection_id=projection_id,
                warning=True,
            )

        return result.finalize()

    def validate_scenario(
        self,
        scenario: Optional[FutureScenario],
        checked_at: Any = None,
    ) -> FutureValidationResult:

        result = FutureValidationResult(
            checked_at=checked_at,
            engine=self.ENGINE_NAME,
            version=self.ENGINE_VERSION,
        )

        if scenario is None:
            result.add_issue(
                code="FUTURE_NULL_SCENARIO",
                message="Future scenario is missing.",
            )
            return result.finalize()

        scenario.normalize()

        if not scenario.scenario_id:
            result.add_issue(
                code="FUTURE_SCENARIO_MISSING_ID",
                message="Scenario ID is missing.",
                field="scenario_id",
            )

        if scenario.current_price < 0:
            result.add_issue(
                code="FUTURE_SCENARIO_INVALID_PRICE",
                message="Scenario current price cannot be negative.",
                field="current_price",
            )

        if scenario.expected_move_pct < 0:
            result.add_issue(
                code="FUTURE_SCENARIO_INVALID_MOVE",
                message="Scenario expected move cannot be negative.",
                field="expected_move_pct",
            )

        if scenario.scenario_strength < 0:
            result.add_issue(
                code="FUTURE_SCENARIO_INVALID_STRENGTH",
                message="Scenario strength cannot be negative.",
                field="scenario_strength",
            )

        if scenario.scenario_strength > 100:
            result.add_issue(
                code="FUTURE_SCENARIO_STRENGTH_RANGE",
                message="Scenario strength cannot exceed 100.",
                field="scenario_strength",
            )

        return result.finalize()

    def validate_evaluation(
        self,
        evaluation: Optional[
            FutureScenarioEvaluation
        ],
        checked_at: Any = None,
    ) -> FutureValidationResult:

        result = FutureValidationResult(
            checked_at=checked_at,
            engine=self.ENGINE_NAME,
            version=self.ENGINE_VERSION,
        )

        if evaluation is None:
            result.add_issue(
                code="FUTURE_NULL_EVALUATION",
                message="Future scenario evaluation is missing.",
            )
            return result.finalize()

        evaluation.normalize()

        if not evaluation.scenario_id:
            result.add_issue(
                code="FUTURE_EVALUATION_MISSING_ID",
                message="Scenario evaluation ID is missing.",
                field="scenario_id",
            )

        score_fields = [
            "scenario_score",
            "evidence_score",
            "structure_score",
            "participation_score",
            "breakout_score",
            "confirmation_score",
            "regime_score",
            "relationship_score",
            "liquidity_score",
            "timing_score",
        ]

        for field_name in score_fields:
            value = getattr(
                evaluation,
                field_name,
                0.0,
            )

            if not 0.0 <= value <= 100.0:
                result.add_issue(
                    code="FUTURE_SCORE_OUT_OF_RANGE",
                    message=(
                        f"{field_name} must be between 0 and 100."
                    ),
                    field=field_name,
                    projection_id=evaluation.scenario_id,
                )

        return result.finalize()

    def validate_ranking(
        self,
        ranking: Optional[FutureScenarioRanking],
        checked_at: Any = None,
    ) -> FutureValidationResult:

        result = FutureValidationResult(
            checked_at=checked_at,
            engine=self.ENGINE_NAME,
            version=self.ENGINE_VERSION,
        )

        if ranking is None:
            result.add_issue(
                code="FUTURE_NULL_RANKING",
                message="Future scenario ranking is missing.",
            )
            return result.finalize()

        ranking.normalize()

        previous_score = None

        for scenario in ranking.scenarios:

            if previous_score is not None:
                if scenario.scenario_score > previous_score:
                    result.add_issue(
                        code="FUTURE_RANKING_ORDER",
                        message=(
                            "Scenario ranking is not ordered "
                            "by descending scenario score."
                        ),
                        severity="WARNING",
                        warning=True,
                    )

            previous_score = scenario.scenario_score

        if ranking.scenarios:
            expected_best = (
                ranking.scenarios[0].scenario_id
            )

            if ranking.best_scenario_id != expected_best:
                result.add_issue(
                    code="FUTURE_BEST_SCENARIO_MISMATCH",
                    message=(
                        "Best scenario ID does not match "
                        "the highest ranked scenario."
                    ),
                    severity="WARNING",
                    warning=True,
                )

        return result.finalize()

    def validate_monitoring_state(
        self,
        state: Optional[FutureMonitoringState],
        checked_at: Any = None,
    ) -> FutureValidationResult:

        result = FutureValidationResult(
            checked_at=checked_at,
            engine=self.ENGINE_NAME,
            version=self.ENGINE_VERSION,
        )

        if state is None:
            result.add_issue(
                code="FUTURE_NULL_MONITORING",
                message="Future monitoring state is missing.",
            )
            return result.finalize()

        state.refresh()

        if state.continuation.strength < 0:
            result.add_issue(
                code="FUTURE_CONTINUATION_STRENGTH",
                message="Continuation strength cannot be negative.",
                field="continuation.strength",
            )

        if state.anti_evidence.strength < 0:
            result.add_issue(
                code="FUTURE_ANTI_EVIDENCE_STRENGTH",
                message="Anti-evidence strength cannot be negative.",
                field="anti_evidence.strength",
            )

        if state.exhaustion.strength < 0:
            result.add_issue(
                code="FUTURE_EXHAUSTION_STRENGTH",
                message="Exhaustion strength cannot be negative.",
                field="exhaustion.strength",
            )

        if (
            state.anti_evidence.detected
            and state.anti_evidence.strength >= 50
            and not state.action_review_required
        ):
            result.add_issue(
                code="FUTURE_ANTI_EVIDENCE_REVIEW_MISSING",
                message=(
                    "Material anti-evidence detected without "
                    "action review being requested."
                ),
                severity="WARNING",
                warning=True,
            )

        return result.finalize()

    def validate_collection(
        self,
        projections: List[FutureProjection],
        checked_at: Any = None,
    ) -> FutureValidationResult:

        result = FutureValidationResult(
            checked_at=checked_at,
            engine=self.ENGINE_NAME,
            version=self.ENGINE_VERSION,
        )

        for projection in projections or []:

            child = self.validate_projection(
                projection,
                checked_at=checked_at,
            )

            result.issues.extend(
                child.issues
            )

            result.warnings.extend(
                child.warnings
            )

        return result.finalize()


# ------------------------------------------------------------
# Future Audit Record
# ------------------------------------------------------------

@dataclass
class FutureAuditRecord:
    """
    BlackBox-ready audit snapshot.

    Stores what Future Model believed at a particular point in time.
    """

    audit_id: str = ""

    timestamp: Any = None

    projection_id: str = ""

    instrument: str = ""
    exchange: str = ""
    market: str = ""
    asset_class: str = ""
    timeframe: str = ""

    direction: str = "UNKNOWN"
    horizon: str = "UNKNOWN"
    status: str = "UNKNOWN"

    projection_strength: float = 0.0

    current_price: float = 0.0
    expected_move_pct: float = 0.0
    expected_move_value: float = 0.0
    expected_target: float = 0.0

    target_lower: float = 0.0
    target_upper: float = 0.0

    scenario_count: int = 0
    best_scenario_id: Optional[str] = None
    best_scenario_score: float = 0.0

    thesis_intact: bool = False

    continuation_strength: float = 0.0
    anti_evidence_strength: float = 0.0
    exhaustion_strength: float = 0.0

    anti_evidence_detected: bool = False
    exhaustion_detected: bool = False
    recalculation_required: bool = False
    exit_review_required: bool = False

    projection_valid: bool = False

    source_engines: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "audit_id": self.audit_id,
            "timestamp": self.timestamp,
            "projection_id": self.projection_id,
            "instrument": self.instrument,
            "exchange": self.exchange,
            "market": self.market,
            "asset_class": self.asset_class,
            "timeframe": self.timeframe,
            "direction": self.direction,
            "horizon": self.horizon,
            "status": self.status,
            "projection_strength": self.projection_strength,
            "current_price": self.current_price,
            "expected_move_pct": self.expected_move_pct,
            "expected_move_value": self.expected_move_value,
            "expected_target": self.expected_target,
            "target_lower": self.target_lower,
            "target_upper": self.target_upper,
            "scenario_count": self.scenario_count,
            "best_scenario_id": self.best_scenario_id,
            "best_scenario_score": self.best_scenario_score,
            "thesis_intact": self.thesis_intact,
            "continuation_strength": (
                self.continuation_strength
            ),
            "anti_evidence_strength": (
                self.anti_evidence_strength
            ),
            "exhaustion_strength": (
                self.exhaustion_strength
            ),
            "anti_evidence_detected": (
                self.anti_evidence_detected
            ),
            "exhaustion_detected": (
                self.exhaustion_detected
            ),
            "recalculation_required": (
                self.recalculation_required
            ),
            "exit_review_required": (
                self.exit_review_required
            ),
            "projection_valid": (
                self.projection_valid
            ),
            "source_engines": list(
                self.source_engines
            ),
            "warnings": list(
                self.warnings
            ),
            "metadata": dict(
                self.metadata
            ),
        }


# ------------------------------------------------------------
# Audit Builder
# ------------------------------------------------------------

def build_future_audit_record(
    projection: Optional[FutureProjection] = None,
    ranking: Optional[FutureScenarioRanking] = None,
    monitoring: Optional[FutureMonitoringState] = None,
    audit_id: str = "",
    timestamp: Any = None,
) -> FutureAuditRecord:

    record = FutureAuditRecord(
        audit_id=audit_id,
        timestamp=timestamp,
    )

    if projection is not None:

        projection.normalize()

        record.projection_id = (
            projection.projection_id
        )

        record.instrument = projection.instrument
        record.exchange = projection.exchange
        record.market = projection.market
        record.asset_class = projection.asset_class
        record.timeframe = projection.timeframe

        record.direction = (
            projection.direction.value
            if isinstance(
                projection.direction,
                FutureDirection,
            )
            else str(projection.direction)
        )

        record.horizon = (
            projection.horizon.value
            if isinstance(
                projection.horizon,
                FutureHorizon,
            )
            else str(projection.horizon)
        )

        record.status = (
            projection.status.value
            if isinstance(
                projection.status,
                FutureProjectionStatus,
            )
            else str(projection.status)
        )

        record.projection_strength = (
            projection.projection_strength
        )

        record.current_price = (
            projection.current_price
        )

        record.expected_move_pct = (
            projection.expected_move_pct
        )

        record.expected_move_value = (
            projection.expected_move_value
        )

        record.expected_target = (
            projection.expected_target
        )

        record.target_lower = (
            projection.target_lower
        )

        record.target_upper = (
            projection.target_upper
        )

        record.projection_valid = (
            projection.is_valid()
        )

        record.source_engines = list(
            projection.source_engines
        )

        record.warnings.extend(
            projection.warnings
        )

    if ranking is not None:

        ranking.normalize()

        record.scenario_count = len(
            ranking.scenarios
        )

        record.best_scenario_id = (
            ranking.best_scenario_id
        )

        best = ranking.best()

        if best is not None:
            record.best_scenario_score = (
                best.scenario_score
            )

    if monitoring is not None:

        monitoring.refresh()

        record.thesis_intact = (
            monitoring.thesis_intact
        )

        record.continuation_strength = (
            monitoring.continuation.strength
        )

        record.anti_evidence_strength = (
            monitoring.anti_evidence.strength
        )

        record.exhaustion_strength = (
            monitoring.exhaustion.strength
        )

        record.anti_evidence_detected = (
            monitoring.anti_evidence.detected
        )

        record.exhaustion_detected = (
            monitoring.exhaustion.detected
        )

        record.recalculation_required = (
            monitoring.recalculation.required
        )

        record.exit_review_required = (
            monitoring.action_review_required
            or monitoring.exhaustion.exit_review_required
            or monitoring.anti_evidence.exit_review_required
        )

        record.warnings.extend(
            monitoring.warnings
        )

    return record


# ------------------------------------------------------------
# Serialization Helpers
# ------------------------------------------------------------

def serialize_future_projection(
    projection: FutureProjection,
) -> Dict[str, Any]:

    if projection is None:
        return {}

    return projection.to_dict()


def serialize_future_scenario(
    scenario: FutureScenario,
) -> Dict[str, Any]:

    if scenario is None:
        return {}

    return scenario.to_dict()


def serialize_future_evaluation(
    evaluation: FutureScenarioEvaluation,
) -> Dict[str, Any]:

    if evaluation is None:
        return {}

    return evaluation.to_dict()


def serialize_future_ranking(
    ranking: FutureScenarioRanking,
) -> Dict[str, Any]:

    if ranking is None:
        return {}

    return ranking.to_dict()


def serialize_future_monitoring(
    monitoring: FutureMonitoringState,
) -> Dict[str, Any]:

    if monitoring is None:
        return {}

    return monitoring.to_dict()


def serialize_future_state(
    state: FutureProjectionState,
) -> Dict[str, Any]:

    if state is None:
        return {}

    return state.to_dict()


# ------------------------------------------------------------
# Validation Convenience Functions
# ------------------------------------------------------------

def validate_future_projection(
    projection: FutureProjection,
    checked_at: Any = None,
) -> FutureValidationResult:

    validator = FutureModelValidator()

    return validator.validate_projection(
        projection,
        checked_at=checked_at,
    )


def validate_future_scenario(
    scenario: FutureScenario,
    checked_at: Any = None,
) -> FutureValidationResult:

    validator = FutureModelValidator()

    return validator.validate_scenario(
        scenario,
        checked_at=checked_at,
    )


def validate_future_ranking(
    ranking: FutureScenarioRanking,
    checked_at: Any = None,
) -> FutureValidationResult:

    validator = FutureModelValidator()

    return validator.validate_ranking(
        ranking,
        checked_at=checked_at,
    )


def validate_future_monitoring(
    monitoring: FutureMonitoringState,
    checked_at: Any = None,
) -> FutureValidationResult:

    validator = FutureModelValidator()

    return validator.validate_monitoring_state(
        monitoring,
        checked_at=checked_at,
    )


# ------------------------------------------------------------
# Public API — PART 5
# ------------------------------------------------------------

__all__ += [
    "FutureValidationIssue",
    "FutureValidationResult",
    "FutureModelValidator",
    "FutureAuditRecord",
    "build_future_audit_record",
    "serialize_future_projection",
    "serialize_future_scenario",
    "serialize_future_evaluation",
    "serialize_future_ranking",
    "serialize_future_monitoring",
    "serialize_future_state",
    "validate_future_projection",
    "validate_future_scenario",
    "validate_future_ranking",
    "validate_future_monitoring",
]