# ============================================================
# ROBOMLM_PLUS
# FUTURE RANK ENGINE — PART 1
# Future Projection Ranking Foundation
# ============================================================

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ------------------------------------------------------------
# Direction
# ------------------------------------------------------------

class FutureRankDirection(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    CALL = "CALL"
    PUT = "PUT"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"


# ------------------------------------------------------------
# Rank Grade
# ------------------------------------------------------------

class FutureRankGrade(str, Enum):
    A_PLUS = "A+"
    A = "A"
    B_PLUS = "B+"
    B = "B"
    NO_TRADE = "NO_TRADE"


# ------------------------------------------------------------
# Rank Status
# ------------------------------------------------------------

class FutureRankStatus(str, Enum):
    QUALIFIED = "QUALIFIED"
    REJECTED = "REJECTED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


# ------------------------------------------------------------
# Ranking Candidate
# ------------------------------------------------------------

@dataclass
class FutureRankCandidate:
    """
    Normalized candidate entering Future Rank Engine.

    This object carries intelligence produced upstream.
    It does not invent missing market intelligence.
    """

    candidate_id: str = ""

    instrument: str = ""
    exchange: str = ""
    market: str = ""
    asset_class: str = ""
    timeframe: str = ""

    timestamp: Any = None

    direction: FutureRankDirection = (
        FutureRankDirection.UNKNOWN
    )

    scenario_type: str = ""

    # Core future intelligence
    projection_strength: float = 0.0
    scenario_score: float = 0.0
    evidence_strength: float = 0.0

    expected_move_pct: float = 0.0
    expected_move_value: float = 0.0

    current_price: float = 0.0
    target_price: float = 0.0
    invalidation_price: float = 0.0

    horizon_minutes: int = 0

    # Upstream intelligence dimensions
    structure_score: float = 0.0
    participation_score: float = 0.0
    breakout_score: float = 0.0
    confirmation_score: float = 0.0
    regime_score: float = 0.0
    relationship_score: float = 0.0
    liquidity_score: float = 0.0
    timing_score: float = 0.0

    # Thesis / monitoring
    thesis_intact: bool = False
    continuation_strength: float = 0.0
    anti_evidence_strength: float = 0.0
    exhaustion_strength: float = 0.0

    # Data / execution context
    data_quality: float = 0.0
    execution_suitability: float = 0.0
    risk_score: float = 0.0

    status: FutureRankStatus = (
        FutureRankStatus.INSUFFICIENT_DATA
    )

    grade: FutureRankGrade = (
        FutureRankGrade.NO_TRADE
    )

    evidence_ids: List[str] = field(
        default_factory=list
    )

    source_engines: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def normalize(self) -> "FutureRankCandidate":

        score_fields = [
            "projection_strength",
            "scenario_score",
            "evidence_strength",
            "structure_score",
            "participation_score",
            "breakout_score",
            "confirmation_score",
            "regime_score",
            "relationship_score",
            "liquidity_score",
            "timing_score",
            "continuation_strength",
            "anti_evidence_strength",
            "exhaustion_strength",
            "data_quality",
            "execution_suitability",
            "risk_score",
        ]

        for name in score_fields:
            value = getattr(self, name, 0.0)

            try:
                value = float(value or 0.0)
            except (TypeError, ValueError):
                value = 0.0

            setattr(
                self,
                name,
                max(0.0, min(100.0, value)),
            )

        self.expected_move_pct = float(
            self.expected_move_pct or 0.0
        )

        self.expected_move_value = float(
            self.expected_move_value or 0.0
        )

        self.current_price = float(
            self.current_price or 0.0
        )

        self.target_price = float(
            self.target_price or 0.0
        )

        self.invalidation_price = float(
            self.invalidation_price or 0.0
        )

        self.horizon_minutes = int(
            self.horizon_minutes or 0
        )

        self.evidence_ids = list(
            self.evidence_ids or []
        )

        self.source_engines = list(
            self.source_engines or []
        )

        self.warnings = list(
            self.warnings or []
        )

        self.metadata = dict(
            self.metadata or {}
        )

        return self

    def is_directional(self) -> bool:
        return self.direction in {
            FutureRankDirection.BUY,
            FutureRankDirection.SELL,
            FutureRankDirection.CALL,
            FutureRankDirection.PUT,
        }

    def has_target(self) -> bool:
        return (
            self.target_price > 0
            or self.expected_move_pct > 0
        )

    def has_horizon(self) -> bool:
        return self.horizon_minutes > 0

    def has_valid_price(self) -> bool:
        return self.current_price > 0

    def to_dict(self) -> Dict[str, Any]:

        self.normalize()

        return {
            "candidate_id": self.candidate_id,
            "instrument": self.instrument,
            "exchange": self.exchange,
            "market": self.market,
            "asset_class": self.asset_class,
            "timeframe": self.timeframe,
            "timestamp": self.timestamp,
            "direction": (
                self.direction.value
                if isinstance(
                    self.direction,
                    FutureRankDirection,
                )
                else str(self.direction)
            ),
            "scenario_type": self.scenario_type,
            "projection_strength": (
                self.projection_strength
            ),
            "scenario_score": self.scenario_score,
            "evidence_strength": (
                self.evidence_strength
            ),
            "expected_move_pct": (
                self.expected_move_pct
            ),
            "expected_move_value": (
                self.expected_move_value
            ),
            "current_price": self.current_price,
            "target_price": self.target_price,
            "invalidation_price": (
                self.invalidation_price
            ),
            "horizon_minutes": (
                self.horizon_minutes
            ),
            "structure_score": (
                self.structure_score
            ),
            "participation_score": (
                self.participation_score
            ),
            "breakout_score": (
                self.breakout_score
            ),
            "confirmation_score": (
                self.confirmation_score
            ),
            "regime_score": self.regime_score,
            "relationship_score": (
                self.relationship_score
            ),
            "liquidity_score": (
                self.liquidity_score
            ),
            "timing_score": self.timing_score,
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
            "data_quality": self.data_quality,
            "execution_suitability": (
                self.execution_suitability
            ),
            "risk_score": self.risk_score,
            "status": (
                self.status.value
                if isinstance(
                    self.status,
                    FutureRankStatus,
                )
                else str(self.status)
            ),
            "grade": (
                self.grade.value
                if isinstance(
                    self.grade,
                    FutureRankGrade,
                )
                else str(self.grade)
            ),
            "evidence_ids": list(
                self.evidence_ids
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
# Ranking Components
# ------------------------------------------------------------

@dataclass
class FutureRankComponents:
    """
    Measurement components used by Future Rank Engine.

    Values are normalized to 0–100.
    """

    projection: float = 0.0
    scenario: float = 0.0
    evidence: float = 0.0

    structure: float = 0.0
    participation: float = 0.0
    breakout: float = 0.0
    confirmation: float = 0.0

    regime: float = 0.0
    relationship: float = 0.0

    liquidity: float = 0.0
    timing: float = 0.0

    continuation: float = 0.0

    data_quality: float = 0.0
    execution: float = 0.0

    risk_quality: float = 0.0
    expected_magnitude: float = 0.0

    def normalize(self) -> "FutureRankComponents":

        fields = [
            "projection",
            "scenario",
            "evidence",
            "structure",
            "participation",
            "breakout",
            "confirmation",
            "regime",
            "relationship",
            "liquidity",
            "timing",
            "continuation",
            "data_quality",
            "execution",
            "risk_quality",
            "expected_magnitude",
        ]

        for name in fields:

            try:
                value = float(
                    getattr(self, name)
                    or 0.0
                )
            except (TypeError, ValueError):
                value = 0.0

            setattr(
                self,
                name,
                max(0.0, min(100.0, value)),
            )

        return self

    def to_dict(self) -> Dict[str, float]:

        self.normalize()

        return {
            "projection": self.projection,
            "scenario": self.scenario,
            "evidence": self.evidence,
            "structure": self.structure,
            "participation": self.participation,
            "breakout": self.breakout,
            "confirmation": self.confirmation,
            "regime": self.regime,
            "relationship": self.relationship,
            "liquidity": self.liquidity,
            "timing": self.timing,
            "continuation": self.continuation,
            "data_quality": self.data_quality,
            "execution": self.execution,
            "risk_quality": self.risk_quality,
            "expected_magnitude": (
                self.expected_magnitude
            ),
        }


# ------------------------------------------------------------
# Future Rank Score
# ------------------------------------------------------------

@dataclass
class FutureRankScore:
    """
    Final normalized ranking score.

    This is a ranking measurement, not a probability
    and not the final D13 decision.
    """

    candidate_id: str = ""

    score: float = 0.0

    grade: FutureRankGrade = (
        FutureRankGrade.NO_TRADE
    )

    status: FutureRankStatus = (
        FutureRankStatus.INSUFFICIENT_DATA
    )

    components: FutureRankComponents = field(
        default_factory=FutureRankComponents
    )

    evidence_strength: float = 0.0

    expected_move_pct: float = 0.0
    horizon_minutes: int = 0

    rank: int = 0

    qualified: bool = False

    reasons: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def normalize(self) -> "FutureRankScore":

        self.score = max(
            0.0,
            min(100.0, float(self.score)),
        )

        self.evidence_strength = max(
            0.0,
            min(
                100.0,
                float(
                    self.evidence_strength
                ),
            ),
        )

        self.expected_move_pct = float(
            self.expected_move_pct or 0.0
        )

        self.horizon_minutes = int(
            self.horizon_minutes or 0
        )

        if self.components is None:
            self.components = FutureRankComponents()

        self.components.normalize()

        self.reasons = list(
            self.reasons or []
        )

        self.warnings = list(
            self.warnings or []
        )

        self.metadata = dict(
            self.metadata or {}
        )

        return self

    def to_dict(self) -> Dict[str, Any]:

        self.normalize()

        return {
            "candidate_id": self.candidate_id,
            "score": self.score,
            "grade": (
                self.grade.value
                if isinstance(
                    self.grade,
                    FutureRankGrade,
                )
                else str(self.grade)
            ),
            "status": (
                self.status.value
                if isinstance(
                    self.status,
                    FutureRankStatus,
                )
                else str(self.status)
            ),
            "components": (
                self.components.to_dict()
            ),
            "evidence_strength": (
                self.evidence_strength
            ),
            "expected_move_pct": (
                self.expected_move_pct
            ),
            "horizon_minutes": (
                self.horizon_minutes
            ),
            "rank": self.rank,
            "qualified": self.qualified,
            "reasons": list(self.reasons),
            "warnings": list(self.warnings),
            "metadata": dict(self.metadata),
        }


# ------------------------------------------------------------
# Future Rank Result
# ------------------------------------------------------------

@dataclass
class FutureRankResult:
    """
    Output container for Future Rank Engine.
    """

    rank_id: str = ""

    timestamp: Any = None

    candidates: List[FutureRankCandidate] = field(
        default_factory=list
    )

    scores: List[FutureRankScore] = field(
        default_factory=list
    )

    top_candidate_id: Optional[str] = None

    qualified_count: int = 0
    rejected_count: int = 0

    ranking_method: str = (
        "future_rank_score_desc"
    )

    valid: bool = False

    warnings: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def normalize(self) -> "FutureRankResult":

        self.candidates = [
            item.normalize()
            for item in (
                self.candidates or []
            )
            if isinstance(
                item,
                FutureRankCandidate,
            )
        ]

        self.scores = [
            item.normalize()
            for item in (
                self.scores or []
            )
            if isinstance(
                item,
                FutureRankScore,
            )
        ]

        self.qualified_count = sum(
            1
            for item in self.scores
            if item.qualified
        )

        self.rejected_count = max(
            0,
            len(self.candidates)
            - self.qualified_count,
        )

        qualified_scores = [
            item
            for item in self.scores
            if item.qualified
        ]

        qualified_scores.sort(
            key=lambda item: item.score,
            reverse=True,
        )

        for index, item in enumerate(
            qualified_scores,
            start=1,
        ):
            item.rank = index

        if qualified_scores:
            self.top_candidate_id = (
                qualified_scores[0].candidate_id
            )
            self.valid = True
        else:
            self.top_candidate_id = None
            self.valid = False

        self.warnings = list(
            self.warnings or []
        )

        self.metadata = dict(
            self.metadata or {}
        )

        return self

    def top(
        self,
        limit: int = 5,
    ) -> List[FutureRankScore]:

        self.normalize()

        return [
            item
            for item in self.scores
            if item.qualified
        ][:max(1, int(limit))]

    def best(self) -> Optional[FutureRankScore]:

        top = self.top(1)

        return top[0] if top else None

    def to_dict(self) -> Dict[str, Any]:

        self.normalize()

        return {
            "rank_id": self.rank_id,
            "timestamp": self.timestamp,
            "candidates": [
                item.to_dict()
                for item in self.candidates
            ],
            "scores": [
                item.to_dict()
                for item in self.scores
            ],
            "top_candidate_id": (
                self.top_candidate_id
            ),
            "qualified_count": (
                self.qualified_count
            ),
            "rejected_count": (
                self.rejected_count
            ),
            "ranking_method": (
                self.ranking_method
            ),
            "valid": self.valid,
            "warnings": list(
                self.warnings
            ),
            "metadata": dict(
                self.metadata
            ),
        }


# ------------------------------------------------------------
# Future Rank Input Builder
# ------------------------------------------------------------

def build_future_rank_candidate(
    candidate_id: str,
    instrument: str,
    direction: FutureRankDirection,
    projection_strength: float = 0.0,
    scenario_score: float = 0.0,
    evidence_strength: float = 0.0,
    expected_move_pct: float = 0.0,
    target_price: float = 0.0,
    current_price: float = 0.0,
    horizon_minutes: int = 0,
    **kwargs: Any,
) -> FutureRankCandidate:

    candidate = FutureRankCandidate(
        candidate_id=candidate_id,
        instrument=instrument,
        direction=direction,
        projection_strength=projection_strength,
        scenario_score=scenario_score,
        evidence_strength=evidence_strength,
        expected_move_pct=expected_move_pct,
        target_price=target_price,
        current_price=current_price,
        horizon_minutes=horizon_minutes,
        **kwargs,
    )

    return candidate.normalize()


# ------------------------------------------------------------
# Public API — PART 1
# ------------------------------------------------------------

__all__ = [
    "FutureRankDirection",
    "FutureRankGrade",
    "FutureRankStatus",
    "FutureRankCandidate",
    "FutureRankComponents",
    "FutureRankScore",
    "FutureRankResult",
    "build_future_rank_candidate",
]
# ============================================================
# ROBOMLM_PLUS
# FUTURE RANK ENGINE
# PART 2 — RANKING CONFIGURATION + SCORING ENGINE
# ============================================================

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple
from datetime import datetime


# ============================================================
# RANKING CONFIGURATION
# ============================================================

@dataclass
class FutureRankConfig:
    """
    Configurable ranking parameters.

    These are engineering baseline weights.
    They are NOT permanent market truths.
    Live/historical validation can calibrate them later.
    """

    # ----------------------------
    # Component weights
    # ----------------------------

    projection_weight: float = 0.15
    scenario_weight: float = 0.15
    evidence_weight: float = 0.15

    structure_weight: float = 0.08
    participation_weight: float = 0.07
    breakout_weight: float = 0.08
    confirmation_weight: float = 0.10

    regime_weight: float = 0.05
    relationship_weight: float = 0.05
    liquidity_weight: float = 0.05
    timing_weight: float = 0.05

    continuation_weight: float = 0.07

    # ----------------------------
    # Qualification baselines
    # ----------------------------

    minimum_data_quality: float = 50.0
    minimum_evidence_strength: float = 40.0

    # Structural validity checks.
    require_direction: bool = True
    require_target_or_expected_move: bool = True
    require_horizon: bool = True
    require_valid_price: bool = True

    # ----------------------------
    # Expected magnitude
    # ----------------------------

    magnitude_reference_pct: float = 10.0

    # ----------------------------
    # Grade boundaries
    # ----------------------------
    #
    # Preserve established EQE grade model:
    #
    # <35       NO TRADE
    # 35-<45    B
    # 45-<65    B+
    # 65-<74    A
    # 74-100    A+
    #

    no_trade_max: float = 35.0
    b_max: float = 45.0
    b_plus_max: float = 65.0
    a_max: float = 74.0

    version: str = "future-rank-config-v1"

    def normalized(self) -> "FutureRankConfig":
        """Return a safe normalized configuration."""

        fields = [
            "projection_weight",
            "scenario_weight",
            "evidence_weight",
            "structure_weight",
            "participation_weight",
            "breakout_weight",
            "confirmation_weight",
            "regime_weight",
            "relationship_weight",
            "liquidity_weight",
            "timing_weight",
            "continuation_weight",
        ]

        values = {
            name: max(0.0, float(getattr(self, name)))
            for name in fields
        }

        total = sum(values.values())

        if total <= 0:
            total = 1.0

        for name in fields:
            values[name] = values[name] / total

        return FutureRankConfig(
            projection_weight=values["projection_weight"],
            scenario_weight=values["scenario_weight"],
            evidence_weight=values["evidence_weight"],
            structure_weight=values["structure_weight"],
            participation_weight=values["participation_weight"],
            breakout_weight=values["breakout_weight"],
            confirmation_weight=values["confirmation_weight"],
            regime_weight=values["regime_weight"],
            relationship_weight=values["relationship_weight"],
            liquidity_weight=values["liquidity_weight"],
            timing_weight=values["timing_weight"],
            continuation_weight=values["continuation_weight"],
            minimum_data_quality=self.minimum_data_quality,
            minimum_evidence_strength=self.minimum_evidence_strength,
            require_direction=self.require_direction,
            require_target_or_expected_move=self.require_target_or_expected_move,
            require_horizon=self.require_horizon,
            require_valid_price=self.require_valid_price,
            magnitude_reference_pct=self.magnitude_reference_pct,
            no_trade_max=self.no_trade_max,
            b_max=self.b_max,
            b_plus_max=self.b_plus_max,
            a_max=self.a_max,
            version=self.version,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "projection_weight": self.projection_weight,
            "scenario_weight": self.scenario_weight,
            "evidence_weight": self.evidence_weight,
            "structure_weight": self.structure_weight,
            "participation_weight": self.participation_weight,
            "breakout_weight": self.breakout_weight,
            "confirmation_weight": self.confirmation_weight,
            "regime_weight": self.regime_weight,
            "relationship_weight": self.relationship_weight,
            "liquidity_weight": self.liquidity_weight,
            "timing_weight": self.timing_weight,
            "continuation_weight": self.continuation_weight,
            "minimum_data_quality": self.minimum_data_quality,
            "minimum_evidence_strength": self.minimum_evidence_strength,
            "require_direction": self.require_direction,
            "require_target_or_expected_move": (
                self.require_target_or_expected_move
            ),
            "require_horizon": self.require_horizon,
            "require_valid_price": self.require_valid_price,
            "magnitude_reference_pct": self.magnitude_reference_pct,
            "grade_boundaries": {
                "no_trade_max": self.no_trade_max,
                "b_max": self.b_max,
                "b_plus_max": self.b_plus_max,
                "a_max": self.a_max,
            },
            "version": self.version,
        }


# ============================================================
# ENGINE
# ============================================================

class FutureRankEngine:
    """
    Ranks current future/opportunity projections.

    Responsibilities:
        - normalize upstream measurements
        - calculate ranking score
        - map score to current-market grade
        - perform structural qualification
        - rank candidates

    It does NOT:
        - make final D13 decisions
        - invent probability
        - fabricate missing intelligence
        - execute trades
        - replace upstream engines
    """

    ENGINE_NAME = "FutureRankEngine"
    ENGINE_VERSION = "1.0.0"

    def __init__(
        self,
        config: Optional[FutureRankConfig] = None,
    ) -> None:

        self.config = (
            config.normalized()
            if config is not None
            else FutureRankConfig().normalized()
        )

    # ========================================================
    # SAFE HELPERS
    # ========================================================

    @staticmethod
    def _safe(value: Any, default: float = 0.0) -> float:
        try:
            result = float(value)

            if result != result:
                return default

            return result

        except (TypeError, ValueError):
            return default

    @staticmethod
    def _clamp(
        value: Any,
        low: float = 0.0,
        high: float = 100.0,
    ) -> float:

        value = FutureRankEngine._safe(value, low)

        return max(low, min(high, value))

    # ========================================================
    # EXPECTED MAGNITUDE
    # ========================================================

    def calculate_expected_magnitude(
        self,
        candidate: "FutureRankCandidate",
    ) -> float:
        """
        Convert expected move into a normalized magnitude score.

        This does NOT assume that every asset must move 10%.
        It only creates a ranking component.

        The reference is configurable and later validated
        against actual market outcomes.
        """

        move = abs(
            self._safe(candidate.expected_move_pct)
        )

        reference = max(
            self._safe(
                self.config.magnitude_reference_pct,
                10.0,
            ),
            0.0001,
        )

        score = (move / reference) * 100.0

        return self._clamp(score)

    # ========================================================
    # RISK QUALITY
    # ========================================================

    def calculate_risk_quality(
        self,
        candidate: "FutureRankCandidate",
    ) -> float:
        """
        Convert risk_score into positive ranking quality.

        Lower risk_score => higher risk quality.

        Missing risk information is treated conservatively
        without inventing a probability.
        """

        risk = self._clamp(
            candidate.risk_score
        )

        return self._clamp(
            100.0 - risk
        )

    # ========================================================
    # COMPONENT EXTRACTION
    # ========================================================

    def build_components(
        self,
        candidate: "FutureRankCandidate",
    ) -> "FutureRankComponents":

        components = FutureRankComponents(
            projection=self._clamp(
                candidate.projection_strength
            ),

            scenario=self._clamp(
                candidate.scenario_score
            ),

            evidence=self._clamp(
                candidate.evidence_strength
            ),

            structure=self._clamp(
                candidate.structure_score
            ),

            participation=self._clamp(
                candidate.participation_score
            ),

            breakout=self._clamp(
                candidate.breakout_score
            ),

            confirmation=self._clamp(
                candidate.confirmation_score
            ),

            regime=self._clamp(
                candidate.regime_score
            ),

            relationship=self._clamp(
                candidate.relationship_score
            ),

            liquidity=self._clamp(
                candidate.liquidity_score
            ),

            timing=self._clamp(
                candidate.timing_score
            ),

            continuation=self._clamp(
                candidate.continuation_strength
            ),

            data_quality=self._clamp(
                candidate.data_quality
            ),

            execution=self._clamp(
                candidate.execution_suitability
            ),

            risk_quality=self.calculate_risk_quality(
                candidate
            ),

            expected_magnitude=self.calculate_expected_magnitude(
                candidate
            ),
        )

        return components

    # ========================================================
    # SCORE CALCULATION
    # ========================================================

    def calculate_score(
        self,
        candidate: "FutureRankCandidate",
    ) -> Tuple[float, "FutureRankComponents"]:

        c = self.build_components(candidate)
        cfg = self.config

        score = (
            c.projection * cfg.projection_weight
            + c.scenario * cfg.scenario_weight
            + c.evidence * cfg.evidence_weight

            + c.structure * cfg.structure_weight
            + c.participation * cfg.participation_weight
            + c.breakout * cfg.breakout_weight
            + c.confirmation * cfg.confirmation_weight

            + c.regime * cfg.regime_weight
            + c.relationship * cfg.relationship_weight
            + c.liquidity * cfg.liquidity_weight
            + c.timing * cfg.timing_weight

            + c.continuation * cfg.continuation_weight
        )

        return self._clamp(score), c

    # ========================================================
    # GRADE
    # ========================================================

    def grade_from_score(
        self,
        score: float,
    ) -> "FutureRankGrade":

        score = self._clamp(score)

        if score < self.config.no_trade_max:
            return FutureRankGrade.NO_TRADE

        if score < self.config.b_max:
            return FutureRankGrade.B

        if score < self.config.b_plus_max:
            return FutureRankGrade.B_PLUS

        if score < self.config.a_max:
            return FutureRankGrade.A

        return FutureRankGrade.A_PLUS

    # ========================================================
    # QUALIFICATION
    # ========================================================

    def qualification_check(
        self,
        candidate: "FutureRankCandidate",
        score: float,
    ) -> Tuple[bool, List[str]]:

        reasons: List[str] = []

        # ----------------------------
        # Data quality
        # ----------------------------

        if (
            self._clamp(candidate.data_quality)
            < self.config.minimum_data_quality
        ):
            reasons.append(
                "data_quality_below_baseline"
            )

        # ----------------------------
        # Evidence
        # ----------------------------

        if (
            self._clamp(candidate.evidence_strength)
            < self.config.minimum_evidence_strength
        ):
            reasons.append(
                "evidence_strength_below_baseline"
            )

        # ----------------------------
        # Direction
        # ----------------------------

        if self.config.require_direction:
            if not candidate.is_directional():
                reasons.append(
                    "direction_not_actionable"
                )

        # ----------------------------
        # Price
        # ----------------------------

        if self.config.require_valid_price:
            if not candidate.has_valid_price():
                reasons.append(
                    "invalid_current_price"
                )

        # ----------------------------
        # Target / Expected Move
        # ----------------------------

        if self.config.require_target_or_expected_move:
            if not candidate.has_target():
                if abs(
                    self._safe(
                        candidate.expected_move_pct
                    )
                ) <= 0:
                    reasons.append(
                        "missing_target_and_expected_move"
                    )

        # ----------------------------
        # Horizon
        # ----------------------------

        if self.config.require_horizon:
            if not candidate.has_horizon():
                reasons.append(
                    "missing_expected_horizon"
                )

        # ----------------------------
        # Grade floor
        # ----------------------------

        if score < self.config.no_trade_max:
            reasons.append(
                "ranking_score_below_trade_grade_floor"
            )

        return (
            len(reasons) == 0,
            reasons,
        )

    # ========================================================
    # CANDIDATE EVALUATION
    # ========================================================

    def evaluate_candidate(
        self,
        candidate: "FutureRankCandidate",
    ) -> "FutureRankScore":

        score, components = self.calculate_score(
            candidate
        )

        qualified, reasons = self.qualification_check(
            candidate,
            score,
        )

        grade = self.grade_from_score(score)

        warnings: List[str] = []

        if candidate.warnings:
            warnings.extend(
                [str(item) for item in candidate.warnings]
            )

        # Existing upstream invalidation/anti-evidence
        # should remain visible to downstream consumers.
        if candidate.anti_evidence_detected:
            warnings.append(
                "anti_evidence_detected"
            )

        if candidate.exhaustion_detected:
            warnings.append(
                "exhaustion_detected"
            )

        if not candidate.thesis_intact:
            warnings.append(
                "thesis_not_intact"
            )

        # If thesis is already invalidated, ranking remains
        # measurable but candidate should not be presented
        # as an active qualified opportunity.
        if not candidate.thesis_intact:
            qualified = False
            reasons.append(
                "thesis_not_intact"
            )

        if candidate.exhaustion_detected:
            qualified = False
            reasons.append(
                "projection_exhaustion_detected"
            )

        status = (
            FutureRankStatus.QUALIFIED
            if qualified
            else FutureRankStatus.REJECTED
        )

        if (
            not candidate.has_valid_price()
            or candidate.data_quality <= 0
        ):
            status = FutureRankStatus.INSUFFICIENT_DATA
            qualified = False

        return FutureRankScore(
            candidate_id=candidate.candidate_id,
            score=score,
            grade=grade,
            status=status,
            components=components,
            evidence_strength=self._clamp(
                candidate.evidence_strength
            ),
            expected_move_pct=self._safe(
                candidate.expected_move_pct
            ),
            horizon_minutes=max(
                0,
                int(
                    self._safe(
                        candidate.horizon_minutes
                    )
                ),
            ),
            rank=0,
            qualified=qualified,
            reasons=reasons,
            warnings=warnings,
            metadata={
                "engine": self.ENGINE_NAME,
                "engine_version": self.ENGINE_VERSION,
                "config_version": self.config.version,
            },
        )

    # ========================================================
    # RANK CANDIDATES
    # ========================================================

    def rank_candidates(
        self,
        candidates: Iterable["FutureRankCandidate"],
    ) -> "FutureRankResult":

        timestamp = datetime.utcnow().isoformat()

        candidate_list = [
            item
            for item in candidates
            if item is not None
        ]

        scores: List[FutureRankScore] = []

        for candidate in candidate_list:
            scores.append(
                self.evaluate_candidate(candidate)
            )

        # ----------------------------------------------------
        # Qualified opportunities first.
        # Lower-grade candidates remain in the result.
        # ----------------------------------------------------

        scores.sort(
            key=lambda item: (
                1 if item.qualified else 0,
                item.score,
                item.evidence_strength,
                abs(item.expected_move_pct),
            ),
            reverse=True,
        )

        rank_counter = 1

        for item in scores:

            if item.qualified:
                item.rank = rank_counter
                rank_counter += 1

        qualified_count = sum(
            1
            for item in scores
            if item.qualified
        )

        rejected_count = len(scores) - qualified_count

        top_candidate_id: Optional[str] = None

        qualified_scores = [
            item
            for item in scores
            if item.qualified
        ]

        if qualified_scores:
            top_candidate_id = (
                qualified_scores[0].candidate_id
            )

        result = FutureRankResult(
            rank_id=(
                f"FR-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
            ),
            timestamp=timestamp,
            candidates=candidate_list,
            scores=scores,
            top_candidate_id=top_candidate_id,
            qualified_count=qualified_count,
            rejected_count=rejected_count,
            ranking_method=(
                "weighted_future_intelligence_ranking"
            ),
            valid=True,
            warnings=[],
            metadata={
                "engine": self.ENGINE_NAME,
                "engine_version": self.ENGINE_VERSION,
                "config": self.config.to_dict(),
            },
        )

        return result

    # ========================================================
    # TOP OPPORTUNITIES
    # ========================================================

    def top(
        self,
        result: "FutureRankResult",
        n: int = 5,
    ) -> List["FutureRankScore"]:

        n = max(1, int(n))

        return [
            item
            for item in result.scores
            if item.qualified
        ][:n]


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================

def rank_future_candidates(
    candidates: Iterable["FutureRankCandidate"],
    config: Optional[FutureRankConfig] = None,
) -> "FutureRankResult":

    engine = FutureRankEngine(
        config=config
    )

    return engine.rank_candidates(
        candidates
    )


# ============================================================
# EXPORTS
# ============================================================

__all__ += [
    "FutureRankConfig",
    "FutureRankEngine",
    "rank_future_candidates",
]
# ============================================================
# ROBOMLM_PLUS
# FUTURE RANK ENGINE
# PART 3 — RANK STABILITY + OPPORTUNITY GROUPING + FEED
# ============================================================

from collections import defaultdict
from typing import Sequence


# ============================================================
# RANK SNAPSHOT
# ============================================================

@dataclass
class FutureRankSnapshot:
    """
    Immutable-style snapshot of a ranking cycle.

    Used for comparing successive ranking cycles and
    measuring whether the current ranking is stable.
    """

    snapshot_id: str
    timestamp: str

    ranked_ids: List[str] = field(default_factory=list)
    qualified_ids: List[str] = field(default_factory=list)

    top_candidate_id: Optional[str] = None
    top_score: float = 0.0
    top_grade: str = "NO_TRADE"

    rank_positions: Dict[str, int] = field(
        default_factory=dict
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp,
            "ranked_ids": list(self.ranked_ids),
            "qualified_ids": list(self.qualified_ids),
            "top_candidate_id": self.top_candidate_id,
            "top_score": self.top_score,
            "top_grade": self.top_grade,
            "rank_positions": dict(self.rank_positions),
            "metadata": dict(self.metadata),
        }


# ============================================================
# RANK STABILITY
# ============================================================

@dataclass
class FutureRankStability:
    """
    Measures ranking continuity between two ranking cycles.

    This is a stability measurement, NOT a probability.
    """

    current_snapshot_id: str
    previous_snapshot_id: Optional[str]

    overlap_ratio: float = 0.0
    top_candidate_stable: bool = False
    direction_stable: bool = False

    average_rank_change: float = 0.0
    maximum_rank_change: int = 0

    stable: bool = False

    changed_candidates: List[str] = field(
        default_factory=list
    )

    reasons: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def normalize(self) -> "FutureRankStability":

        self.overlap_ratio = max(
            0.0,
            min(100.0, float(self.overlap_ratio))
        )

        self.average_rank_change = max(
            0.0,
            float(self.average_rank_change)
        )

        self.maximum_rank_change = max(
            0,
            int(self.maximum_rank_change)
        )

        return self

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_snapshot_id":
                self.current_snapshot_id,
            "previous_snapshot_id":
                self.previous_snapshot_id,
            "overlap_ratio":
                self.overlap_ratio,
            "top_candidate_stable":
                self.top_candidate_stable,
            "direction_stable":
                self.direction_stable,
            "average_rank_change":
                self.average_rank_change,
            "maximum_rank_change":
                self.maximum_rank_change,
            "stable":
                self.stable,
            "changed_candidates":
                list(self.changed_candidates),
            "reasons":
                list(self.reasons),
            "metadata":
                dict(self.metadata),
        }


# ============================================================
# OPPORTUNITY GROUP
# ============================================================

@dataclass
class FutureOpportunityGroup:
    """
    Groups ranked opportunities by instrument/exchange/market.

    Useful when the same underlying has multiple projections
    or multiple market representations.
    """

    group_id: str
    instrument: str

    exchange: str = ""
    market: str = ""
    asset_class: str = ""

    candidate_ids: List[str] = field(
        default_factory=list
    )

    best_candidate_id: Optional[str] = None

    best_score: float = 0.0
    best_grade: str = "NO_TRADE"

    dominant_direction: str = "UNKNOWN"

    average_score: float = 0.0

    qualified_count: int = 0
    candidate_count: int = 0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "group_id": self.group_id,
            "instrument": self.instrument,
            "exchange": self.exchange,
            "market": self.market,
            "asset_class": self.asset_class,
            "candidate_ids":
                list(self.candidate_ids),
            "best_candidate_id":
                self.best_candidate_id,
            "best_score":
                self.best_score,
            "best_grade":
                self.best_grade,
            "dominant_direction":
                self.dominant_direction,
            "average_score":
                self.average_score,
            "qualified_count":
                self.qualified_count,
            "candidate_count":
                self.candidate_count,
            "metadata":
                dict(self.metadata),
        }


# ============================================================
# FUTURE RANK FEED
# ============================================================

@dataclass
class FutureRankFeed:
    """
    Downstream normalized feed.

    This is an intelligence/ranking feed only.

    D13 remains final decision authority.
    """

    feed_id: str
    timestamp: str

    best_candidate_id: Optional[str] = None

    top_candidates: List[Dict[str, Any]] = field(
        default_factory=list
    )

    qualified_candidates: List[Dict[str, Any]] = field(
        default_factory=list
    )

    groups: List[Dict[str, Any]] = field(
        default_factory=list
    )

    rank_stability: Optional[FutureRankStability] = None

    total_candidates: int = 0
    qualified_count: int = 0

    actionable: bool = False

    warnings: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "feed_id": self.feed_id,
            "timestamp": self.timestamp,
            "best_candidate_id":
                self.best_candidate_id,
            "top_candidates":
                list(self.top_candidates),
            "qualified_candidates":
                list(self.qualified_candidates),
            "groups":
                list(self.groups),
            "rank_stability": (
                self.rank_stability.to_dict()
                if self.rank_stability
                else None
            ),
            "total_candidates":
                self.total_candidates,
            "qualified_count":
                self.qualified_count,
            "actionable":
                self.actionable,
            "warnings":
                list(self.warnings),
            "metadata":
                dict(self.metadata),
        }


# ============================================================
# SNAPSHOT BUILDER
# ============================================================

def build_future_rank_snapshot(
    result: "FutureRankResult",
) -> FutureRankSnapshot:

    ranked = [
        item
        for item in result.scores
        if item.qualified
    ]

    ranked.sort(
        key=lambda item: (
            item.rank if item.rank > 0 else 999999
        )
    )

    ranked_ids = [
        item.candidate_id
        for item in ranked
    ]

    qualified_ids = list(ranked_ids)

    rank_positions = {
        item.candidate_id: item.rank
        for item in ranked
        if item.rank > 0
    }

    top = ranked[0] if ranked else None

    return FutureRankSnapshot(
        snapshot_id=(
            f"FRS-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
        ),
        timestamp=datetime.utcnow().isoformat(),
        ranked_ids=ranked_ids,
        qualified_ids=qualified_ids,
        top_candidate_id=(
            top.candidate_id
            if top
            else None
        ),
        top_score=(
            float(top.score)
            if top
            else 0.0
        ),
        top_grade=(
            top.grade.value
            if hasattr(top.grade, "value")
            else str(top.grade)
        ) if top else "NO_TRADE",
        rank_positions=rank_positions,
        metadata={
            "source":
                "FutureRankEngine"
        },
    )


# ============================================================
# STABILITY CALCULATION
# ============================================================

def calculate_rank_stability(
    current: FutureRankSnapshot,
    previous: Optional[FutureRankSnapshot],
    current_result: Optional["FutureRankResult"] = None,
) -> FutureRankStability:

    if previous is None:

        return FutureRankStability(
            current_snapshot_id=current.snapshot_id,
            previous_snapshot_id=None,
            overlap_ratio=0.0,
            top_candidate_stable=False,
            direction_stable=False,
            average_rank_change=0.0,
            maximum_rank_change=0,
            stable=False,
            reasons=[
                "no_previous_ranking_snapshot"
            ],
        ).normalize()

    current_set = set(
        current.ranked_ids
    )

    previous_set = set(
        previous.ranked_ids
    )

    union = current_set | previous_set

    intersection = (
        current_set & previous_set
    )

    overlap_ratio = (
        len(intersection) /
        len(union) * 100.0
        if union
        else 0.0
    )

    common_ids = (
        current_set & previous_set
    )

    rank_changes: List[int] = []

    changed_candidates: List[str] = []

    for candidate_id in common_ids:

        old_rank = previous.rank_positions.get(
            candidate_id
        )

        new_rank = current.rank_positions.get(
            candidate_id
        )

        if old_rank is None or new_rank is None:
            continue

        change = abs(
            int(new_rank) -
            int(old_rank)
        )

        rank_changes.append(change)

        if change > 0:
            changed_candidates.append(
                candidate_id
            )

    average_rank_change = (
        sum(rank_changes) /
        len(rank_changes)
        if rank_changes
        else 0.0
    )

    maximum_rank_change = (
        max(rank_changes)
        if rank_changes
        else 0
    )

    top_stable = (
        current.top_candidate_id is not None
        and
        current.top_candidate_id
        == previous.top_candidate_id
    )

    direction_stable = False

    if (
        current_result is not None
        and current.top_candidate_id
        and previous.top_candidate_id
    ):

        current_candidate = next(
            (
                c for c in current_result.candidates
                if c.candidate_id
                == current.top_candidate_id
            ),
            None,
        )

        previous_candidate = next(
            (
                c for c in current_result.candidates
                if c.candidate_id
                == previous.top_candidate_id
            ),
            None,
        )

        if (
            current_candidate is not None
            and previous_candidate is not None
        ):
            direction_stable = (
                str(
                    current_candidate.direction
                )
                ==
                str(
                    previous_candidate.direction
                )
            )

    reasons: List[str] = []

    if overlap_ratio < 50.0:
        reasons.append(
            "low_candidate_overlap"
        )

    if not top_stable:
        reasons.append(
            "top_candidate_changed"
        )

    if maximum_rank_change >= 3:
        reasons.append(
            "material_rank_movement"
        )

    stable = (
        overlap_ratio >= 50.0
        and top_stable
        and average_rank_change <= 2.0
    )

    return FutureRankStability(
        current_snapshot_id=current.snapshot_id,
        previous_snapshot_id=previous.snapshot_id,
        overlap_ratio=overlap_ratio,
        top_candidate_stable=top_stable,
        direction_stable=direction_stable,
        average_rank_change=average_rank_change,
        maximum_rank_change=maximum_rank_change,
        stable=stable,
        changed_candidates=changed_candidates,
        reasons=reasons,
    ).normalize()


# ============================================================
# GROUP BUILDER
# ============================================================

def build_future_opportunity_groups(
    candidates: Sequence["FutureRankCandidate"],
    scores: Sequence["FutureRankScore"],
) -> List[FutureOpportunityGroup]:

    candidate_map = {
        candidate.candidate_id: candidate
        for candidate in candidates
    }

    score_map = {
        score.candidate_id: score
        for score in scores
    }

    groups: Dict[
        Tuple[str, str, str],
        List[str]
    ] = defaultdict(list)

    for candidate in candidates:

        key = (
            str(candidate.instrument),
            str(candidate.exchange),
            str(candidate.market),
        )

        groups[key].append(
            candidate.candidate_id
        )

    output: List[
        FutureOpportunityGroup
    ] = []

    for key, candidate_ids in groups.items():

        instrument, exchange, market = key

        valid_scores = [
            score_map[candidate_id]
            for candidate_id in candidate_ids
            if candidate_id in score_map
        ]

        if not valid_scores:
            continue

        valid_scores.sort(
            key=lambda item: item.score,
            reverse=True
        )

        best = valid_scores[0]

        directional_candidates = []

        for candidate_id in candidate_ids:

            candidate = candidate_map.get(
                candidate_id
            )

            if candidate is None:
                continue

            if candidate.is_directional():
                directional_candidates.append(
                    candidate
                )

        direction_count: Dict[str, int] = defaultdict(int)

        for candidate in directional_candidates:

            direction = (
                candidate.direction.value
                if hasattr(
                    candidate.direction,
                    "value"
                )
                else str(candidate.direction)
            )

            direction_count[direction] += 1

        dominant_direction = "UNKNOWN"

        if direction_count:
            dominant_direction = max(
                direction_count,
                key=direction_count.get
            )

        qualified_scores = [
            score
            for score in valid_scores
            if score.qualified
        ]

        output.append(
            FutureOpportunityGroup(
                group_id=(
                    f"FOG-{instrument}-"
                    f"{exchange}-{market}"
                ),
                instrument=instrument,
                exchange=exchange,
                market=market,
                asset_class=(
                    candidate_map[
                        candidate_ids[0]
                    ].asset_class
                    if candidate_ids
                    else ""
                ),
                candidate_ids=list(
                    candidate_ids
                ),
                best_candidate_id=(
                    best.candidate_id
                ),
                best_score=float(
                    best.score
                ),
                best_grade=(
                    best.grade.value
                    if hasattr(
                        best.grade,
                        "value"
                    )
                    else str(best.grade)
                ),
                dominant_direction=(
                    dominant_direction
                ),
                average_score=(
                    sum(
                        score.score
                        for score in valid_scores
                    )
                    / len(valid_scores)
                ),
                qualified_count=len(
                    qualified_scores
                ),
                candidate_count=len(
                    valid_scores
                ),
                metadata={
                    "grouping":
                        "instrument_exchange_market"
                },
            )
        )

    output.sort(
        key=lambda item: item.best_score,
        reverse=True
    )

    return output


# ============================================================
# FEED BUILDER
# ============================================================

def build_future_rank_feed(
    result: "FutureRankResult",
    top_n: int = 5,
    previous_snapshot: Optional[
        FutureRankSnapshot
    ] = None,
) -> FutureRankFeed:

    top_n = max(
        1,
        int(top_n)
    )

    current_snapshot = (
        build_future_rank_snapshot(
            result
        )
    )

    stability = calculate_rank_stability(
        current=current_snapshot,
        previous=previous_snapshot,
        current_result=result,
    )

    groups = build_future_opportunity_groups(
        result.candidates,
        result.scores,
    )

    qualified_scores = [
        item
        for item in result.scores
        if item.qualified
    ]

    qualified_scores.sort(
        key=lambda item: item.rank
    )

    top_scores = qualified_scores[
        :top_n
    ]

    top_candidates = []

    candidate_map = {
        candidate.candidate_id: candidate
        for candidate in result.candidates
    }

    for score in top_scores:

        candidate = candidate_map.get(
            score.candidate_id
        )

        if candidate is None:
            continue

        top_candidates.append({
            "candidate": candidate.to_dict(),
            "score": score.to_dict(),
        })

    all_qualified = []

    for score in qualified_scores:

        candidate = candidate_map.get(
            score.candidate_id
        )

        if candidate is None:
            continue

        all_qualified.append({
            "candidate_id":
                candidate.candidate_id,
            "instrument":
                candidate.instrument,
            "exchange":
                candidate.exchange,
            "direction": (
                candidate.direction.value
                if hasattr(
                    candidate.direction,
                    "value"
                )
                else str(candidate.direction)
            ),
            "grade": (
                score.grade.value
                if hasattr(
                    score.grade,
                    "value"
                )
                else str(score.grade)
            ),
            "rank":
                score.rank,
            "score":
                score.score,
            "expected_move_pct":
                candidate.expected_move_pct,
            "expected_horizon_minutes":
                candidate.horizon_minutes,
            "target_price":
                candidate.target_price,
            "thesis_intact":
                candidate.thesis_intact,
        })

    warnings = list(
        result.warnings
        if result.warnings
        else []
    )

    if not qualified_scores:
        warnings.append(
            "no_current_qualified_future_opportunity"
        )

    actionable = (
        len(qualified_scores) > 0
    )

    return FutureRankFeed(
        feed_id=(
            f"FRF-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
        ),
        timestamp=datetime.utcnow().isoformat(),
        best_candidate_id=(
            result.top_candidate_id
        ),
        top_candidates=top_candidates,
        qualified_candidates=all_qualified,
        groups=[
            group.to_dict()
            for group in groups
        ],
        rank_stability=stability,
        total_candidates=len(
            result.candidates
        ),
        qualified_count=len(
            qualified_scores
        ),
        actionable=actionable,
        warnings=warnings,
        metadata={
            "engine":
                "FutureRankEngine",
            "engine_version":
                FutureRankEngine.ENGINE_VERSION,
            "top_n":
                top_n,
            "d13_role":
                "downstream_final_decision_authority",
        },
    )


# ============================================================
# TOP-N HELPER
# ============================================================

def get_top_future_opportunities(
    result: "FutureRankResult",
    n: int = 5,
) -> List["FutureRankScore"]:

    n = max(
        1,
        int(n)
    )

    return [
        score
        for score in result.scores
        if score.qualified
    ][:n]


# ============================================================
# D13 FEED HELPER
# ============================================================

def export_future_rank_d13_feed(
    result: "FutureRankResult",
    top_n: int = 5,
    previous_snapshot: Optional[
        FutureRankSnapshot
    ] = None,
) -> Dict[str, Any]:

    feed = build_future_rank_feed(
        result=result,
        top_n=top_n,
        previous_snapshot=previous_snapshot,
    )

    payload = feed.to_dict()

    payload["consumer"] = "D13"
    payload["decision_authority"] = (
        "D13"
    )

    # Future Rank provides ranked intelligence.
    # It does NOT emit a final BUY/SELL decision.
    payload["final_decision"] = None

    return payload


# ============================================================
# EXPORTS
# ============================================================

__all__ += [
    "FutureRankSnapshot",
    "FutureRankStability",
    "FutureOpportunityGroup",
    "FutureRankFeed",
    "build_future_rank_snapshot",
    "calculate_rank_stability",
    "build_future_opportunity_groups",
    "build_future_rank_feed",
    "get_top_future_opportunities",
    "export_future_rank_d13_feed",
]
# ============================================================
# ROBOMLM_PLUS
# FUTURE RANK ENGINE
# PART 4 — RANK MONITORING + DIRECTION CONSISTENCY
#          + DETERIORATION / IMPROVEMENT + HISTORY
# ============================================================

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence
from datetime import datetime


# ============================================================
# CANDIDATE RANK MONITOR
# ============================================================

@dataclass
class FutureRankMonitor:
    """
    Tracks how one future candidate behaves across ranking cycles.

    This is monitoring intelligence only.
    It does not create a final trading decision.
    """

    candidate_id: str

    first_seen_at: Optional[str] = None
    last_seen_at: Optional[str] = None

    current_rank: int = 0
    previous_rank: int = 0

    current_score: float = 0.0
    previous_score: float = 0.0

    current_grade: str = "NO_TRADE"
    previous_grade: str = "NO_TRADE"

    current_direction: str = "UNKNOWN"
    previous_direction: str = "UNKNOWN"

    rank_change: int = 0
    score_change: float = 0.0

    improving: bool = False
    deteriorating: bool = False

    direction_changed: bool = False
    grade_changed: bool = False

    currently_qualified: bool = False
    previously_qualified: bool = False

    consecutive_present_cycles: int = 0
    consecutive_qualified_cycles: int = 0

    events: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def update(
        self,
        score: "FutureRankScore",
        candidate: "FutureRankCandidate",
    ) -> "FutureRankMonitor":

        now = datetime.utcnow().isoformat()

        if self.first_seen_at is None:
            self.first_seen_at = now

        self.last_seen_at = now

        # --------------------------------------------
        # Previous state
        # --------------------------------------------

        self.previous_rank = self.current_rank
        self.previous_score = self.current_score

        self.previous_grade = self.current_grade
        self.previous_direction = (
            self.current_direction
        )

        self.previously_qualified = (
            self.currently_qualified
        )

        # --------------------------------------------
        # Current state
        # --------------------------------------------

        self.current_rank = int(
            score.rank
        )

        self.current_score = float(
            score.score
        )

        self.current_grade = (
            score.grade.value
            if hasattr(score.grade, "value")
            else str(score.grade)
        )

        self.current_direction = (
            candidate.direction.value
            if hasattr(candidate.direction, "value")
            else str(candidate.direction)
        )

        self.currently_qualified = bool(
            score.qualified
        )

        # --------------------------------------------
        # Changes
        # --------------------------------------------

        if (
            self.previous_rank > 0
            and self.current_rank > 0
        ):
            self.rank_change = (
                self.previous_rank
                - self.current_rank
            )
        else:
            self.rank_change = 0

        self.score_change = (
            self.current_score
            - self.previous_score
        )

        self.direction_changed = (
            self.previous_direction != "UNKNOWN"
            and self.current_direction != "UNKNOWN"
            and
            self.previous_direction
            != self.current_direction
        )

        self.grade_changed = (
            self.previous_grade != "NO_TRADE"
            and
            self.current_grade
            != self.previous_grade
        )

        self.improving = (
            self.score_change > 0
            or self.rank_change > 0
        )

        self.deteriorating = (
            self.score_change < 0
            or (
                self.previous_rank > 0
                and self.current_rank > self.previous_rank
            )
        )

        # --------------------------------------------
        # Cycle counters
        # --------------------------------------------

        self.consecutive_present_cycles += 1

        if self.currently_qualified:
            self.consecutive_qualified_cycles += 1
        else:
            self.consecutive_qualified_cycles = 0

        # --------------------------------------------
        # Events
        # --------------------------------------------

        self.events = []

        if self.improving:
            self.events.append(
                "ranking_improved"
            )

        if self.deteriorating:
            self.events.append(
                "ranking_deteriorated"
            )

        if self.direction_changed:
            self.events.append(
                "direction_changed"
            )

        if self.grade_changed:
            self.events.append(
                "grade_changed"
            )

        if (
            not self.previously_qualified
            and self.currently_qualified
        ):
            self.events.append(
                "became_qualified"
            )

        if (
            self.previously_qualified
            and not self.currently_qualified
        ):
            self.events.append(
                "lost_qualification"
            )

        return self

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id":
                self.candidate_id,
            "first_seen_at":
                self.first_seen_at,
            "last_seen_at":
                self.last_seen_at,
            "current_rank":
                self.current_rank,
            "previous_rank":
                self.previous_rank,
            "current_score":
                self.current_score,
            "previous_score":
                self.previous_score,
            "current_grade":
                self.current_grade,
            "previous_grade":
                self.previous_grade,
            "current_direction":
                self.current_direction,
            "previous_direction":
                self.previous_direction,
            "rank_change":
                self.rank_change,
            "score_change":
                self.score_change,
            "improving":
                self.improving,
            "deteriorating":
                self.deteriorating,
            "direction_changed":
                self.direction_changed,
            "grade_changed":
                self.grade_changed,
            "currently_qualified":
                self.currently_qualified,
            "previously_qualified":
                self.previously_qualified,
            "consecutive_present_cycles":
                self.consecutive_present_cycles,
            "consecutive_qualified_cycles":
                self.consecutive_qualified_cycles,
            "events":
                list(self.events),
            "metadata":
                dict(self.metadata),
        }


# ============================================================
# RANK HISTORY ENTRY
# ============================================================

@dataclass
class FutureRankHistoryEntry:
    """
    One historical ranking observation.
    """

    timestamp: str
    candidate_id: str

    rank: int
    score: float
    grade: str
    qualified: bool

    direction: str
    expected_move_pct: float
    horizon_minutes: int

    evidence_strength: float

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp":
                self.timestamp,
            "candidate_id":
                self.candidate_id,
            "rank":
                self.rank,
            "score":
                self.score,
            "grade":
                self.grade,
            "qualified":
                self.qualified,
            "direction":
                self.direction,
            "expected_move_pct":
                self.expected_move_pct,
            "horizon_minutes":
                self.horizon_minutes,
            "evidence_strength":
                self.evidence_strength,
            "metadata":
                dict(self.metadata),
        }


# ============================================================
# RANK HISTORY
# ============================================================

@dataclass
class FutureRankHistory:
    """
    Rolling ranking history.

    The history is intended for:
        - stability measurement
        - later validation
        - BlackBox analysis
        - ranking calibration
    """

    max_entries_per_candidate: int = 100

    entries: Dict[
        str,
        List[FutureRankHistoryEntry]
    ] = field(
        default_factory=dict
    )

    def add(
        self,
        score: "FutureRankScore",
        candidate: "FutureRankCandidate",
        timestamp: Optional[str] = None,
    ) -> None:

        timestamp = (
            timestamp
            or datetime.utcnow().isoformat()
        )

        grade = (
            score.grade.value
            if hasattr(score.grade, "value")
            else str(score.grade)
        )

        direction = (
            candidate.direction.value
            if hasattr(
                candidate.direction,
                "value"
            )
            else str(candidate.direction)
        )

        entry = FutureRankHistoryEntry(
            timestamp=timestamp,
            candidate_id=candidate.candidate_id,
            rank=int(score.rank),
            score=float(score.score),
            grade=grade,
            qualified=bool(score.qualified),
            direction=direction,
            expected_move_pct=float(
                candidate.expected_move_pct
                or 0.0
            ),
            horizon_minutes=int(
                candidate.horizon_minutes
                or 0
            ),
            evidence_strength=float(
                candidate.evidence_strength
                or 0.0
            ),
        )

        history = self.entries.setdefault(
            candidate.candidate_id,
            []
        )

        history.append(entry)

        if (
            len(history)
            > self.max_entries_per_candidate
        ):
            self.entries[
                candidate.candidate_id
            ] = history[
                -self.max_entries_per_candidate:
            ]

    def get(
        self,
        candidate_id: str,
    ) -> List[FutureRankHistoryEntry]:

        return list(
            self.entries.get(
                candidate_id,
                []
            )
        )

    def latest(
        self,
        candidate_id: str,
    ) -> Optional[FutureRankHistoryEntry]:

        history = self.entries.get(
            candidate_id,
            []
        )

        if not history:
            return None

        return history[-1]

    def clear(
        self,
        candidate_id: Optional[str] = None,
    ) -> None:

        if candidate_id is None:
            self.entries.clear()
        else:
            self.entries.pop(
                candidate_id,
                None
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_entries_per_candidate":
                self.max_entries_per_candidate,
            "candidate_count":
                len(self.entries),
            "entries": {
                candidate_id: [
                    entry.to_dict()
                    for entry in history
                ]
                for candidate_id, history
                in self.entries.items()
            },
        }


# ============================================================
# RANK MONITORING ENGINE
# ============================================================

class FutureRankMonitoringEngine:
    """
    Maintains candidate ranking state across cycles.

    Important:
        Monitoring deterioration does not automatically
        create a SELL/BUY/EXIT decision.

        It only exposes changing intelligence to downstream
        consumers such as D13.
    """

    ENGINE_NAME = "FutureRankMonitoringEngine"
    ENGINE_VERSION = "1.0.0"

    def __init__(
        self,
        max_history_per_candidate: int = 100,
    ) -> None:

        self.monitors: Dict[
            str,
            FutureRankMonitor
        ] = {}

        self.history = FutureRankHistory(
            max_entries_per_candidate=max(
                1,
                int(
                    max_history_per_candidate
                )
            )
        )

    # ========================================================
    # UPDATE ONE CANDIDATE
    # ========================================================

    def update_candidate(
        self,
        score: "FutureRankScore",
        candidate: "FutureRankCandidate",
    ) -> FutureRankMonitor:

        monitor = self.monitors.get(
            candidate.candidate_id
        )

        if monitor is None:
            monitor = FutureRankMonitor(
                candidate_id=
                    candidate.candidate_id
            )

            self.monitors[
                candidate.candidate_id
            ] = monitor

        monitor.update(
            score=score,
            candidate=candidate,
        )

        self.history.add(
            score=score,
            candidate=candidate,
        )

        return monitor

    # ========================================================
    # UPDATE RESULT
    # ========================================================

    def update_result(
        self,
        result: "FutureRankResult",
    ) -> Dict[str, FutureRankMonitor]:

        candidate_map = {
            candidate.candidate_id:
                candidate
            for candidate
            in result.candidates
        }

        updated: Dict[
            str,
            FutureRankMonitor
        ] = {}

        for score in result.scores:

            candidate = candidate_map.get(
                score.candidate_id
            )

            if candidate is None:
                continue

            monitor = self.update_candidate(
                score=score,
                candidate=candidate,
            )

            updated[
                candidate.candidate_id
            ] = monitor

        return updated

    # ========================================================
    # GET MONITOR
    # ========================================================

    def get_monitor(
        self,
        candidate_id: str,
    ) -> Optional[FutureRankMonitor]:

        return self.monitors.get(
            candidate_id
        )

    # ========================================================
    # IMPROVING CANDIDATES
    # ========================================================

    def improving_candidates(
        self,
    ) -> List[FutureRankMonitor]:

        output = [
            monitor
            for monitor in self.monitors.values()
            if monitor.improving
        ]

        output.sort(
            key=lambda item: (
                item.score_change,
                item.rank_change,
            ),
            reverse=True,
        )

        return output

    # ========================================================
    # DETERIORATING CANDIDATES
    # ========================================================

    def deteriorating_candidates(
        self,
    ) -> List[FutureRankMonitor]:

        output = [
            monitor
            for monitor in self.monitors.values()
            if monitor.deteriorating
        ]

        output.sort(
            key=lambda item: (
                item.score_change,
                item.rank_change,
            )
        )

        return output

    # ========================================================
    # DIRECTION CHANGES
    # ========================================================

    def direction_changes(
        self,
    ) -> List[FutureRankMonitor]:

        return [
            monitor
            for monitor in self.monitors.values()
            if monitor.direction_changed
        ]

    # ========================================================
    # CURRENTLY QUALIFIED
    # ========================================================

    def qualified_candidates(
        self,
    ) -> List[FutureRankMonitor]:

        output = [
            monitor
            for monitor in self.monitors.values()
            if monitor.currently_qualified
        ]

        output.sort(
            key=lambda item: (
                item.current_rank
                if item.current_rank > 0
                else 999999
            )
        )

        return output

    # ========================================================
    # MONITORING SUMMARY
    # ========================================================

    def summary(self) -> Dict[str, Any]:

        monitors = list(
            self.monitors.values()
        )

        return {
            "engine":
                self.ENGINE_NAME,
            "engine_version":
                self.ENGINE_VERSION,
            "candidate_count":
                len(monitors),
            "qualified_count":
                sum(
                    1
                    for item in monitors
                    if item.currently_qualified
                ),
            "improving_count":
                sum(
                    1
                    for item in monitors
                    if item.improving
                ),
            "deteriorating_count":
                sum(
                    1
                    for item in monitors
                    if item.deteriorating
                ),
            "direction_change_count":
                sum(
                    1
                    for item in monitors
                    if item.direction_changed
                ),
        }

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:

        return {
            "engine":
                self.ENGINE_NAME,
            "engine_version":
                self.ENGINE_VERSION,
            "monitors": {
                candidate_id:
                    monitor.to_dict()
                for candidate_id, monitor
                in self.monitors.items()
            },
            "history":
                self.history.to_dict(),
            "summary":
                self.summary(),
        }


# ============================================================
# RANK CHANGE ANALYSIS
# ============================================================

def analyze_future_rank_change(
    previous: Optional["FutureRankScore"],
    current: "FutureRankScore",
) -> Dict[str, Any]:
    """
    Compare two observations of the same candidate.

    Returns measurement only.
    No probability or final decision is generated.
    """

    if previous is None:

        return {
            "candidate_id":
                current.candidate_id,
            "baseline_available":
                False,
            "rank_change":
                0,
            "score_change":
                0.0,
            "grade_changed":
                False,
            "qualified_changed":
                False,
            "status":
                "initial_observation",
        }

    previous_grade = (
        previous.grade.value
        if hasattr(
            previous.grade,
            "value"
        )
        else str(previous.grade)
    )

    current_grade = (
        current.grade.value
        if hasattr(
            current.grade,
            "value"
        )
        else str(current.grade)
    )

    rank_change = (
        previous.rank - current.rank
        if (
            previous.rank > 0
            and current.rank > 0
        )
        else 0
    )

    score_change = (
        float(current.score)
        - float(previous.score)
    )

    grade_changed = (
        previous_grade
        != current_grade
    )

    qualified_changed = (
        bool(previous.qualified)
        != bool(current.qualified)
    )

    if (
        score_change > 0
        or rank_change > 0
    ):
        status = "improving"

    elif (
        score_change < 0
        or rank_change < 0
    ):
        status = "deteriorating"

    else:
        status = "stable"

    return {
        "candidate_id":
            current.candidate_id,
        "baseline_available":
            True,
        "previous_rank":
            previous.rank,
        "current_rank":
            current.rank,
        "rank_change":
            rank_change,
        "previous_score":
            previous.score,
        "current_score":
            current.score,
        "score_change":
            score_change,
        "previous_grade":
            previous_grade,
        "current_grade":
            current_grade,
        "grade_changed":
            grade_changed,
        "previous_qualified":
            previous.qualified,
        "current_qualified":
            current.qualified,
        "qualified_changed":
            qualified_changed,
        "status":
            status,
    }


# ============================================================
# EXPORTS
# ============================================================

__all__ += [
    "FutureRankMonitor",
    "FutureRankHistoryEntry",
    "FutureRankHistory",
    "FutureRankMonitoringEngine",
    "analyze_future_rank_change",
]
# ============================================================
# ROBOMLM_PLUS
# FUTURE RANK ENGINE
# PART 5 — VALIDATION + AUDIT + BLACKBOX + SERIALIZATION
# ============================================================

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence
from datetime import datetime


# ============================================================
# VALIDATION ISSUE
# ============================================================

@dataclass
class FutureRankValidationIssue:
    """
    Validation issue generated by FutureRankEngine audit layer.
    """

    code: str
    message: str

    severity: str = "ERROR"
    field: Optional[str] = None
    candidate_id: Optional[str] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "field": self.field,
            "candidate_id": self.candidate_id,
            "metadata": dict(self.metadata),
        }


# ============================================================
# VALIDATION RESULT
# ============================================================

@dataclass
class FutureRankValidationResult:
    """
    Complete validation result.
    """

    valid: bool = True

    issues: List[
        FutureRankValidationIssue
    ] = field(default_factory=list)

    warnings: List[str] = field(
        default_factory=list
    )

    checked_candidates: int = 0
    checked_scores: int = 0

    timestamp: str = field(
        default_factory=lambda:
            datetime.utcnow().isoformat()
    )

    engine_version: str = (
        "1.0.0"
    )

    def add_issue(
        self,
        code: str,
        message: str,
        severity: str = "ERROR",
        field_name: Optional[str] = None,
        candidate_id: Optional[str] = None,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        issue = FutureRankValidationIssue(
            code=code,
            message=message,
            severity=severity,
            field=field_name,
            candidate_id=candidate_id,
            metadata=(
                dict(metadata)
                if metadata
                else {}
            ),
        )

        self.issues.append(issue)

        if severity.upper() == "ERROR":
            self.valid = False

    def add_warning(
        self,
        message: str,
    ) -> None:

        self.warnings.append(
            str(message)
        )

    def finalize(self) -> "FutureRankValidationResult":

        self.valid = not any(
            issue.severity.upper()
            == "ERROR"
            for issue in self.issues
        )

        return self

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "issues": [
                issue.to_dict()
                for issue in self.issues
            ],
            "warnings": list(
                self.warnings
            ),
            "checked_candidates":
                self.checked_candidates,
            "checked_scores":
                self.checked_scores,
            "error_count": sum(
                1
                for issue in self.issues
                if issue.severity.upper()
                == "ERROR"
            ),
            "warning_issue_count": sum(
                1
                for issue in self.issues
                if issue.severity.upper()
                == "WARNING"
            ),
            "timestamp":
                self.timestamp,
            "engine_version":
                self.engine_version,
        }


# ============================================================
# VALIDATOR
# ============================================================

class FutureRankValidator:
    """
    Structural and contract validation for FutureRankEngine.

    Validation does not modify intelligence.

    It only identifies:
        - missing fields
        - invalid ranges
        - inconsistent ranking state
        - malformed actionable candidates
    """

    ENGINE_NAME = "FutureRankValidator"
    ENGINE_VERSION = "1.0.0"

    # --------------------------------------------------------
    # SAFE HELPERS
    # --------------------------------------------------------

    @staticmethod
    def _safe(
        value: Any,
        default: float = 0.0,
    ) -> float:

        try:
            result = float(value)

            if result != result:
                return default

            return result

        except (
            TypeError,
            ValueError,
        ):
            return default

    @staticmethod
    def _enum_value(
        value: Any,
        default: str = "UNKNOWN",
    ) -> str:

        if hasattr(value, "value"):
            return str(value.value)

        if value is None:
            return default

        return str(value)

    # --------------------------------------------------------
    # SCORE RANGE
    # --------------------------------------------------------

    def _validate_score(
        self,
        result: FutureRankValidationResult,
        value: Any,
        name: str,
        candidate_id: Optional[str],
    ) -> None:

        score = self._safe(value, -1.0)

        if score < 0.0 or score > 100.0:

            result.add_issue(
                code="score_out_of_range",
                message=(
                    f"{name} must be between "
                    f"0 and 100"
                ),
                field_name=name,
                candidate_id=candidate_id,
                metadata={
                    "value": value
                },
            )

    # --------------------------------------------------------
    # CANDIDATE VALIDATION
    # --------------------------------------------------------

    def validate_candidate(
        self,
        candidate: "FutureRankCandidate",
        result: Optional[
            FutureRankValidationResult
        ] = None,
    ) -> FutureRankValidationResult:

        if result is None:
            result = FutureRankValidationResult()

        result.checked_candidates += 1

        candidate_id = (
            candidate.candidate_id
        )

        if not candidate_id:
            result.add_issue(
                code="missing_candidate_id",
                message=(
                    "Candidate ID is required"
                ),
                field_name="candidate_id",
            )

        if not candidate.instrument:
            result.add_issue(
                code="missing_instrument",
                message=(
                    "Instrument is required"
                ),
                field_name="instrument",
                candidate_id=candidate_id,
            )

        # ----------------------------------------------------
        # Direction
        # ----------------------------------------------------

        direction = self._enum_value(
            candidate.direction
        )

        allowed_directions = {
            "BUY",
            "SELL",
            "CALL",
            "PUT",
            "NEUTRAL",
            "UNKNOWN",
        }

        if direction not in allowed_directions:

            result.add_issue(
                code="invalid_direction",
                message=(
                    "Unknown future rank direction"
                ),
                field_name="direction",
                candidate_id=candidate_id,
                metadata={
                    "direction": direction
                },
            )

        # ----------------------------------------------------
        # Scores
        # ----------------------------------------------------

        score_fields = [
            "projection_strength",
            "scenario_score",
            "evidence_strength",
            "structure_score",
            "participation_score",
            "breakout_score",
            "confirmation_score",
            "regime_score",
            "relationship_score",
            "liquidity_score",
            "timing_score",
            "continuation_strength",
            "data_quality",
            "execution_suitability",
            "risk_score",
        ]

        for name in score_fields:
            self._validate_score(
                result=result,
                value=getattr(
                    candidate,
                    name,
                    0.0,
                ),
                name=name,
                candidate_id=candidate_id,
            )

        # ----------------------------------------------------
        # Price
        # ----------------------------------------------------

        current_price = self._safe(
            candidate.current_price
        )

        if current_price <= 0:

            result.add_issue(
                code="invalid_current_price",
                message=(
                    "Current price must be "
                    "greater than zero"
                ),
                field_name="current_price",
                candidate_id=candidate_id,
            )

        # ----------------------------------------------------
        # Expected Move
        # ----------------------------------------------------

        expected_move = self._safe(
            candidate.expected_move_pct
        )

        if expected_move < 0:

            result.add_issue(
                code="negative_expected_move",
                message=(
                    "Expected move should be "
                    "direction-normalized or zero"
                ),
                field_name="expected_move_pct",
                candidate_id=candidate_id,
                severity="WARNING",
            )

        # ----------------------------------------------------
        # Horizon
        # ----------------------------------------------------

        horizon = int(
            self._safe(
                candidate.horizon_minutes
            )
        )

        if horizon < 0:

            result.add_issue(
                code="negative_horizon",
                message=(
                    "Expected horizon cannot "
                    "be negative"
                ),
                field_name="horizon_minutes",
                candidate_id=candidate_id,
            )

        # ----------------------------------------------------
        # Target
        # ----------------------------------------------------

        target = self._safe(
            candidate.target_price
        )

        if target < 0:

            result.add_issue(
                code="invalid_target",
                message=(
                    "Target price cannot be negative"
                ),
                field_name="target_price",
                candidate_id=candidate_id,
            )

        # ----------------------------------------------------
        # Thesis state
        # ----------------------------------------------------

        if not candidate.thesis_intact:

            result.add_issue(
                code="thesis_not_intact",
                message=(
                    "Candidate thesis is not intact"
                ),
                severity="WARNING",
                candidate_id=candidate_id,
            )

        # ----------------------------------------------------
        # Anti-evidence
        # ----------------------------------------------------

        if candidate.anti_evidence_detected:

            result.add_issue(
                code="anti_evidence_detected",
                message=(
                    "Material anti-evidence "
                    "is present"
                ),
                severity="WARNING",
                candidate_id=candidate_id,
            )

        # ----------------------------------------------------
        # Exhaustion
        # ----------------------------------------------------

        if candidate.exhaustion_detected:

            result.add_issue(
                code="exhaustion_detected",
                message=(
                    "Projection exhaustion is detected"
                ),
                severity="WARNING",
                candidate_id=candidate_id,
            )

        return result

    # --------------------------------------------------------
    # SCORE VALIDATION
    # --------------------------------------------------------

    def validate_score(
        self,
        score: "FutureRankScore",
        result: Optional[
            FutureRankValidationResult
        ] = None,
    ) -> FutureRankValidationResult:

        if result is None:
            result = FutureRankValidationResult()

        result.checked_scores += 1

        candidate_id = (
            score.candidate_id
        )

        self._validate_score(
            result,
            score.score,
            "score",
            candidate_id,
        )

        self._validate_score(
            result,
            score.evidence_strength,
            "evidence_strength",
            candidate_id,
        )

        if score.rank < 0:

            result.add_issue(
                code="invalid_rank",
                message=(
                    "Rank cannot be negative"
                ),
                field_name="rank",
                candidate_id=candidate_id,
            )

        if score.horizon_minutes < 0:

            result.add_issue(
                code="invalid_score_horizon",
                message=(
                    "Score horizon cannot "
                    "be negative"
                ),
                field_name="horizon_minutes",
                candidate_id=candidate_id,
            )

        return result

    # --------------------------------------------------------
    # RESULT VALIDATION
    # --------------------------------------------------------

    def validate_result(
        self,
        result_object: "FutureRankResult",
    ) -> FutureRankValidationResult:

        validation = (
            FutureRankValidationResult()
        )

        candidates = list(
            result_object.candidates
            or []
        )

        scores = list(
            result_object.scores
            or []
        )

        # ----------------------------------------------------
        # Candidate validation
        # ----------------------------------------------------

        for candidate in candidates:

            if candidate is None:
                validation.add_issue(
                    code="null_candidate",
                    message=(
                        "Null candidate found"
                    ),
                )
                continue

            self.validate_candidate(
                candidate,
                validation,
            )

        # ----------------------------------------------------
        # Score validation
        # ----------------------------------------------------

        for score in scores:

            if score is None:
                validation.add_issue(
                    code="null_score",
                    message=(
                        "Null ranking score found"
                    ),
                )
                continue

            self.validate_score(
                score,
                validation,
            )

        # ----------------------------------------------------
        # Candidate/score consistency
        # ----------------------------------------------------

        candidate_ids = {
            candidate.candidate_id
            for candidate in candidates
            if candidate is not None
        }

        score_ids = {
            score.candidate_id
            for score in scores
            if score is not None
        }

        missing_scores = (
            candidate_ids - score_ids
        )

        unknown_scores = (
            score_ids - candidate_ids
        )

        for candidate_id in missing_scores:

            validation.add_issue(
                code="candidate_without_score",
                message=(
                    "Candidate has no ranking score"
                ),
                candidate_id=candidate_id,
            )

        for candidate_id in unknown_scores:

            validation.add_issue(
                code="score_without_candidate",
                message=(
                    "Ranking score has no candidate"
                ),
                candidate_id=candidate_id,
            )

        # ----------------------------------------------------
        # Qualified count
        # ----------------------------------------------------

        actual_qualified = sum(
            1
            for score in scores
            if score.qualified
        )

        if (
            int(result_object.qualified_count)
            != actual_qualified
        ):

            validation.add_issue(
                code="qualified_count_mismatch",
                message=(
                    "qualified_count does not "
                    "match score records"
                ),
                severity="WARNING",
                metadata={
                    "declared":
                        result_object.qualified_count,
                    "actual":
                        actual_qualified,
                },
            )

        # ----------------------------------------------------
        # Top candidate consistency
        # ----------------------------------------------------

        qualified_scores = [
            score
            for score in scores
            if score.qualified
        ]

        qualified_scores.sort(
            key=lambda item: item.score,
            reverse=True,
        )

        expected_top = (
            qualified_scores[0].candidate_id
            if qualified_scores
            else None
        )

        if (
            result_object.top_candidate_id
            != expected_top
        ):

            validation.add_issue(
                code="top_candidate_mismatch",
                message=(
                    "top_candidate_id does not "
                    "match highest qualified score"
                ),
                severity="WARNING",
                metadata={
                    "declared":
                        result_object.top_candidate_id,
                    "expected":
                        expected_top,
                },
            )

        return validation.finalize()

    # --------------------------------------------------------
    # COLLECTION VALIDATION
    # --------------------------------------------------------

    def validate_collection(
        self,
        candidates: Sequence[
            "FutureRankCandidate"
        ],
    ) -> FutureRankValidationResult:

        validation = (
            FutureRankValidationResult()
        )

        for candidate in candidates:

            if candidate is None:

                validation.add_issue(
                    code="null_candidate",
                    message=(
                        "Null candidate in collection"
                    ),
                )

                continue

            self.validate_candidate(
                candidate,
                validation,
            )

        return validation.finalize()


# ============================================================
# AUDIT RECORD
# ============================================================

@dataclass
class FutureRankAuditRecord:
    """
    BlackBox-ready audit snapshot.

    Captures what FutureRankEngine knew at a specific moment.
    """

    audit_id: str
    timestamp: str

    candidate_id: str
    instrument: str
    exchange: str
    market: str
    asset_class: str
    timeframe: str

    direction: str
    scenario_type: str

    rank: int
    score: float
    grade: str
    status: str
    qualified: bool

    projection_strength: float
    scenario_score: float
    evidence_strength: float

    expected_move_pct: float
    expected_move_value: float
    current_price: float
    target_price: float
    invalidation_price: float
    horizon_minutes: int

    thesis_intact: bool
    continuation_strength: float
    anti_evidence_detected: bool
    anti_evidence_strength: float
    exhaustion_detected: bool
    exhaustion_strength: float

    data_quality: float
    execution_suitability: float
    risk_score: float

    warnings: List[str] = field(
        default_factory=list
    )

    evidence_ids: List[str] = field(
        default_factory=list
    )

    source_engines: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "audit_id":
                self.audit_id,
            "timestamp":
                self.timestamp,
            "candidate_id":
                self.candidate_id,
            "instrument":
                self.instrument,
            "exchange":
                self.exchange,
            "market":
                self.market,
            "asset_class":
                self.asset_class,
            "timeframe":
                self.timeframe,
            "direction":
                self.direction,
            "scenario_type":
                self.scenario_type,
            "rank":
                self.rank,
            "score":
                self.score,
            "grade":
                self.grade,
            "status":
                self.status,
            "qualified":
                self.qualified,
            "projection_strength":
                self.projection_strength,
            "scenario_score":
                self.scenario_score,
            "evidence_strength":
                self.evidence_strength,
            "expected_move_pct":
                self.expected_move_pct,
            "expected_move_value":
                self.expected_move_value,
            "current_price":
                self.current_price,
            "target_price":
                self.target_price,
            "invalidation_price":
                self.invalidation_price,
            "horizon_minutes":
                self.horizon_minutes,
            "thesis_intact":
                self.thesis_intact,
            "continuation_strength":
                self.continuation_strength,
            "anti_evidence_detected":
                self.anti_evidence_detected,
            "anti_evidence_strength":
                self.anti_evidence_strength,
            "exhaustion_detected":
                self.exhaustion_detected,
            "exhaustion_strength":
                self.exhaustion_strength,
            "data_quality":
                self.data_quality,
            "execution_suitability":
                self.execution_suitability,
            "risk_score":
                self.risk_score,
            "warnings":
                list(self.warnings),
            "evidence_ids":
                list(self.evidence_ids),
            "source_engines":
                list(self.source_engines),
            "metadata":
                dict(self.metadata),
        }


# ============================================================
# AUDIT BUILDER
# ============================================================

def build_future_rank_audit_record(
    candidate: "FutureRankCandidate",
    score: "FutureRankScore",
) -> FutureRankAuditRecord:

    direction = (
        candidate.direction.value
        if hasattr(
            candidate.direction,
            "value",
        )
        else str(
            candidate.direction
        )
    )

    scenario_type = (
        candidate.scenario_type.value
        if hasattr(
            candidate.scenario_type,
            "value",
        )
        else str(
            candidate.scenario_type
        )
    )

    grade = (
        score.grade.value
        if hasattr(
            score.grade,
            "value",
        )
        else str(score.grade)
    )

    status = (
        score.status.value
        if hasattr(
            score.status,
            "value",
        )
        else str(score.status)
    )

    return FutureRankAuditRecord(
        audit_id=(
            f"FRA-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
        ),
        timestamp=datetime.utcnow().isoformat(),

        candidate_id=
            candidate.candidate_id,
        instrument=
            candidate.instrument,
        exchange=
            candidate.exchange,
        market=
            candidate.market,
        asset_class=
            candidate.asset_class,
        timeframe=
            candidate.timeframe,

        direction=
            direction,
        scenario_type=
            scenario_type,

        rank=
            int(score.rank),
        score=
            float(score.score),
        grade=
            grade,
        status=
            status,
        qualified=
            bool(score.qualified),

        projection_strength=
            float(candidate.projection_strength),
        scenario_score=
            float(candidate.scenario_score),
        evidence_strength=
            float(candidate.evidence_strength),

        expected_move_pct=
            float(candidate.expected_move_pct),
        expected_move_value=
            float(candidate.expected_move_value),
        current_price=
            float(candidate.current_price),
        target_price=
            float(candidate.target_price),
        invalidation_price=
            float(candidate.invalidation_price),
        horizon_minutes=
            int(candidate.horizon_minutes),

        thesis_intact=
            bool(candidate.thesis_intact),

        continuation_strength=
            float(candidate.continuation_strength),

        anti_evidence_detected=
            bool(candidate.anti_evidence_detected),

        anti_evidence_strength=
            float(candidate.anti_evidence_strength),

        exhaustion_detected=
            bool(candidate.exhaustion_detected),

        exhaustion_strength=
            float(candidate.exhaustion_strength),

        data_quality=
            float(candidate.data_quality),

        execution_suitability=
            float(candidate.execution_suitability),

        risk_score=
            float(candidate.risk_score),

        warnings=list(
            candidate.warnings
            or []
        ),

        evidence_ids=list(
            candidate.evidence_ids
            or []
        ),

        source_engines=list(
            candidate.source_engines
            or []
        ),

        metadata={
            "engine":
                FutureRankEngine.ENGINE_NAME,
            "engine_version":
                FutureRankEngine.ENGINE_VERSION,
            "audit_type":
                "future_rank_snapshot",
            "decision_authority":
                "D13",
        },
    )


# ============================================================
# SERIALIZATION HELPERS
# ============================================================

def serialize_future_rank_result(
    result: "FutureRankResult",
) -> Dict[str, Any]:

    return result.to_dict()


def serialize_future_rank_feed(
    feed: "FutureRankFeed",
) -> Dict[str, Any]:

    return feed.to_dict()


def serialize_future_rank_audit(
    audit: FutureRankAuditRecord,
) -> Dict[str, Any]:

    return audit.to_dict()


# ============================================================
# VALIDATION CONVENIENCE FUNCTIONS
# ============================================================

def validate_future_rank_candidate(
    candidate: "FutureRankCandidate",
) -> FutureRankValidationResult:

    validator = FutureRankValidator()

    return validator.validate_candidate(
        candidate
    ).finalize()


def validate_future_rank_result(
    result: "FutureRankResult",
) -> FutureRankValidationResult:

    validator = FutureRankValidator()

    return validator.validate_result(
        result
    )


def validate_future_rank_collection(
    candidates: Sequence[
        "FutureRankCandidate"
    ],
) -> FutureRankValidationResult:

    validator = FutureRankValidator()

    return validator.validate_collection(
        candidates
    )


# ============================================================
# COMPLETE ENGINE AUDIT
# ============================================================

def audit_future_rank_result(
    result: "FutureRankResult",
) -> Dict[str, Any]:

    validator = FutureRankValidator()

    validation = validator.validate_result(
        result
    )

    audits: List[
        Dict[str, Any]
    ] = []

    candidate_map = {
        candidate.candidate_id:
            candidate
        for candidate
        in result.candidates
        if candidate is not None
    }

    for score in result.scores:

        candidate = candidate_map.get(
            score.candidate_id
        )

        if candidate is None:
            continue

        audit = (
            build_future_rank_audit_record(
                candidate=candidate,
                score=score,
            )
        )

        audits.append(
            audit.to_dict()
        )

    return {
        "audit_timestamp":
            datetime.utcnow().isoformat(),

        "engine":
            FutureRankEngine.ENGINE_NAME,

        "engine_version":
            FutureRankEngine.ENGINE_VERSION,

        "validation":
            validation.to_dict(),

        "result":
            result.to_dict(),

        "audit_records":
            audits,

        "decision_authority":
            "D13",

        "final_decision":
            None,
    }


# ============================================================
# PUBLIC API
# ============================================================

__all__ += [
    "FutureRankValidationIssue",
    "FutureRankValidationResult",
    "FutureRankValidator",
    "FutureRankAuditRecord",
    "build_future_rank_audit_record",
    "serialize_future_rank_result",
    "serialize_future_rank_feed",
    "serialize_future_rank_audit",
    "validate_future_rank_candidate",
    "validate_future_rank_result",
    "validate_future_rank_collection",
    "audit_future_rank_result",
]