# ============================================================
# ROBOMLM_PLUS
# SCANNER MODEL
# Complete Foundation + Qualification + Ranking
# ============================================================

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import math


# ============================================================
# ENUMS
# ============================================================

class ScannerDirection(Enum):
    BUY = "BUY"
    SELL = "SELL"
    CALL = "CALL"
    PUT = "PUT"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"


class ScannerGrade(Enum):
    A_PLUS = "A+"
    A = "A"
    B_PLUS = "B+"
    B = "B"
    NO_TRADE = "NO_TRADE"


class ScannerStatus(Enum):
    QUALIFIED = "QUALIFIED"
    REJECTED = "REJECTED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


# ============================================================
# RAW SCANNER INPUT
# ============================================================

@dataclass
class ScannerInput:
    instrument: str
    timestamp: datetime

    market: Optional[str] = None
    exchange: Optional[str] = None
    asset_class: Optional[str] = None
    timeframe: Optional[str] = None

    price: float = 0.0

    # --------------------------------------------------------
    # Engine outputs
    # --------------------------------------------------------

    structure_score: float = 0.0
    accumulation_score: float = 0.0
    distribution_score: float = 0.0
    boundary_score: float = 0.0
    breakout_score: float = 0.0
    confirmation_score: float = 0.0

    regime_score: float = 0.0
    relationship_score: float = 0.0
    opportunity_score: float = 0.0

    thesis_score: float = 0.0
    growth_score: float = 0.0
    pullback_score: float = 0.0
    holdability_score: float = 0.0
    protection_score: float = 0.0
    future_rank_score: float = 0.0

    # --------------------------------------------------------
    # Direction
    # --------------------------------------------------------

    direction: ScannerDirection = (
        ScannerDirection.UNKNOWN
    )

    # --------------------------------------------------------
    # Market data health
    # --------------------------------------------------------

    data_quality: float = 0.0
    liquidity_score: float = 0.0
    execution_score: float = 0.0

    # --------------------------------------------------------
    # Expected opportunity
    # --------------------------------------------------------

    expected_move_pct: float = 0.0
    expected_horizon_minutes: float = 0.0

    # --------------------------------------------------------
    # Risk
    # --------------------------------------------------------

    risk_score: float = 0.0

    # --------------------------------------------------------
    # Evidence
    # --------------------------------------------------------

    evidence: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )


# ============================================================
# SCANNER OPPORTUNITY
# ============================================================

@dataclass
class ScannerOpportunity:

    instrument: str
    timestamp: datetime

    rank: int = 0

    direction: ScannerDirection = (
        ScannerDirection.UNKNOWN
    )

    grade: ScannerGrade = (
        ScannerGrade.NO_TRADE
    )

    status: ScannerStatus = (
        ScannerStatus.REJECTED
    )

    quality_score: float = 0.0
    evidence_strength: float = 0.0
    timing_score: float = 0.0
    liquidity_score: float = 0.0
    volatility_score: float = 0.0
    risk_score: float = 0.0
    expected_magnitude: float = 0.0
    execution_suitability: float = 0.0
    intelligence_stability: float = 0.0

    expected_move_pct: float = 0.0
    expected_horizon_minutes: float = 0.0

    market: Optional[str] = None
    exchange: Optional[str] = None
    asset_class: Optional[str] = None
    timeframe: Optional[str] = None

    evidence_reference: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "instrument": self.instrument,
            "timestamp": (
                self.timestamp.isoformat()
                if isinstance(
                    self.timestamp,
                    datetime,
                )
                else self.timestamp
            ),
            "rank": self.rank,
            "direction": self.direction.value,
            "grade": self.grade.value,
            "status": self.status.value,
            "quality_score": round(
                self.quality_score,
                2,
            ),
            "evidence_strength": round(
                self.evidence_strength,
                2,
            ),
            "timing_score": round(
                self.timing_score,
                2,
            ),
            "liquidity_score": round(
                self.liquidity_score,
                2,
            ),
            "volatility_score": round(
                self.volatility_score,
                2,
            ),
            "risk_score": round(
                self.risk_score,
                2,
            ),
            "expected_magnitude": round(
                self.expected_magnitude,
                2,
            ),
            "execution_suitability": round(
                self.execution_suitability,
                2,
            ),
            "intelligence_stability": round(
                self.intelligence_stability,
                2,
            ),
            "expected_move_pct": round(
                self.expected_move_pct,
                4,
            ),
            "expected_horizon_minutes": (
                self.expected_horizon_minutes
            ),
            "market": self.market,
            "exchange": self.exchange,
            "asset_class": self.asset_class,
            "timeframe": self.timeframe,
            "evidence_reference": list(
                self.evidence_reference
            ),
            "warnings": list(
                self.warnings
            ),
        }


# ============================================================
# SCAN RESULT
# ============================================================

@dataclass
class ScannerResult:

    scan_id: str
    timestamp: datetime

    universe: List[str]

    qualified_count: int

    opportunities: List[
        ScannerOpportunity
    ]

    ranking_method: str = (
        "MULTI_DIMENSION_INTELLIGENCE_RANKING"
    )

    rejected_count: int = 0

    warnings: List[str] = field(
        default_factory=list
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "scan_id": self.scan_id,
            "timestamp": (
                self.timestamp.isoformat()
                if isinstance(
                    self.timestamp,
                    datetime,
                )
                else self.timestamp
            ),
            "universe": list(
                self.universe
            ),
            "qualified_count": (
                self.qualified_count
            ),
            "rejected_count": (
                self.rejected_count
            ),
            "opportunities": [
                item.to_dict()
                for item in self.opportunities
            ],
            "ranking_method": (
                self.ranking_method
            ),
            "warnings": list(
                self.warnings
            ),
        }


# ============================================================
# SCANNER MODEL
# ============================================================

class ScannerModel:

    """
    ROBOMLM scanner orchestration model.

    The scanner:
        - receives calculated intelligence
        - validates data availability
        - qualifies opportunities
        - calculates normalized quality
        - ranks opportunities
        - returns Top-N

    The scanner DOES NOT:
        - invent market intelligence
        - invent formulas
        - make final D13 decisions
        - replace upstream engines
        - fabricate missing values
    """

    def __init__(
        self,
        top_n: int = 10,
    ):

        self.top_n = max(
            1,
            int(top_n),
        )

        # ----------------------------------------------------
        # Initial qualification baselines.
        # These remain configurable and require live validation.
        # ----------------------------------------------------

        self.minimum_data_quality = 50.0
        self.minimum_liquidity = 30.0
        self.minimum_evidence = 40.0
        self.minimum_quality = 35.0

        self.minimum_expected_move = 0.0

        self.engine = "ScannerModel"
        self.engine_version = "1.0.0"


    # ========================================================
    # SAFE NUMBER
    # ========================================================

    @staticmethod
    def _safe(
        value: Any,
    ) -> float:

        try:

            number = float(value)

            if not math.isfinite(number):
                return 0.0

            return number

        except (
            TypeError,
            ValueError,
        ):

            return 0.0


    # ========================================================
    # CLAMP
    # ========================================================

    @staticmethod
    def _clamp(
        value: float,
        low: float = 0.0,
        high: float = 100.0,
    ) -> float:

        return max(
            low,
            min(
                high,
                value,
            ),
        )


    # ========================================================
    # EVIDENCE STRENGTH
    # ========================================================

    def calculate_evidence_strength(
        self,
        data: ScannerInput,
    ) -> float:

        components = [
            data.structure_score,
            data.accumulation_score,
            data.distribution_score,
            data.boundary_score,
            data.breakout_score,
            data.confirmation_score,
            data.regime_score,
            data.relationship_score,
            data.opportunity_score,
        ]

        valid = [
            self._clamp(
                self._safe(value)
            )
            for value in components
            if self._safe(value) > 0
        ]

        if not valid:
            return 0.0

        # Strong evidence requires breadth,
        # not one artificially high component.
        average = (
            sum(valid)
            / len(valid)
        )

        breadth_factor = min(
            1.0,
            len(valid) / 5.0,
        )

        return self._clamp(
            average
            * (
                0.70
                + 0.30 * breadth_factor
            )
        )


    # ========================================================
    # QUALITY SCORE
    # ========================================================

    def calculate_quality(
        self,
        data: ScannerInput,
        evidence_strength: float,
    ) -> float:

        # ----------------------------------------------------
        # Core discovery dimensions
        # ----------------------------------------------------

        structure = self._clamp(
            data.structure_score
        )

        accumulation = self._clamp(
            data.accumulation_score
        )

        distribution = self._clamp(
            data.distribution_score
        )

        boundary = self._clamp(
            data.boundary_score
        )

        breakout = self._clamp(
            data.breakout_score
        )

        confirmation = self._clamp(
            data.confirmation_score
        )

        opportunity = self._clamp(
            data.opportunity_score
        )

        regime = self._clamp(
            data.regime_score
        )

        relationship = self._clamp(
            data.relationship_score
        )

        # ----------------------------------------------------
        # Core opportunity quality
        # ----------------------------------------------------

        core = (
            structure * 0.12
            + max(
                accumulation,
                distribution,
            ) * 0.08
            + boundary * 0.10
            + breakout * 0.12
            + confirmation * 0.12
            + opportunity * 0.18
            + evidence_strength * 0.12
            + regime * 0.08
            + relationship * 0.08
        )

        return self._clamp(
            core
        )


    # ========================================================
    # EXPECTED MAGNITUDE
    # ========================================================

    def calculate_expected_magnitude(
        self,
        data: ScannerInput,
    ) -> float:

        expected_move = abs(
            self._safe(
                data.expected_move_pct
            )
        )

        # Normalize magnitude without assuming
        # a universal asset-class price move.
        #
        # 10% baseline can be supplied upstream,
        # but scanner does not force 10% on every market.

        if expected_move <= 0:
            return 0.0

        if expected_move >= 10.0:
            score = 100.0

        else:
            score = (
                expected_move
                / 10.0
            ) * 100.0

        return self._clamp(
            score
        )


    # ========================================================
    # VOLATILITY SCORE
    # ========================================================

    def calculate_volatility_score(
        self,
        data: ScannerInput,
    ) -> float:

        # Upstream engines provide suitability.
        # Scanner does not infer direction from volatility.

        values = [
            data.breakout_score,
            data.confirmation_score,
            data.regime_score,
        ]

        valid = [
            self._safe(value)
            for value in values
            if self._safe(value) > 0
        ]

        if not valid:
            return 0.0

        return self._clamp(
            sum(valid)
            / len(valid)
        )


    # ========================================================
    # TIMING SCORE
    # ========================================================

    def calculate_timing_score(
        self,
        data: ScannerInput,
    ) -> float:

        values = [
            data.boundary_score,
            data.breakout_score,
            data.confirmation_score,
            data.pullback_score,
        ]

        valid = [
            self._safe(value)
            for value in values
            if self._safe(value) > 0
        ]

        if not valid:
            return 0.0

        return self._clamp(
            sum(valid)
            / len(valid)
        )


    # ========================================================
    # INTELLIGENCE STABILITY
    # ========================================================

    def calculate_stability(
        self,
        data: ScannerInput,
    ) -> float:

        values = [
            data.regime_score,
            data.relationship_score,
            data.confirmation_score,
            data.holdability_score,
            data.thesis_score,
        ]

        valid = [
            self._safe(value)
            for value in values
            if self._safe(value) > 0
        ]

        if not valid:
            return 0.0

        average = (
            sum(valid)
            / len(valid)
        )

        minimum = min(valid)

        # Stability rewards agreement between
        # multiple intelligence dimensions.
        stability = (
            average * 0.65
            + minimum * 0.35
        )

        return self._clamp(
            stability
        )


    # ========================================================
    # EXECUTION SUITABILITY
    # ========================================================

    def calculate_execution_suitability(
        self,
        data: ScannerInput,
    ) -> float:

        return self._clamp(
            (
                self._safe(
                    data.liquidity_score
                ) * 0.50
                +
                self._safe(
                    data.execution_score
                ) * 0.50
            )
        )


    # ========================================================
    # QUALIFICATION
    # ========================================================

    def qualify(
        self,
        data: ScannerInput,
        quality: float,
        evidence_strength: float,
    ) -> bool:

        if not data.instrument:
            return False

        if self._safe(
            data.price
        ) <= 0:
            return False

        if (
            self._safe(
                data.data_quality
            )
            < self.minimum_data_quality
        ):
            return False

        if (
            self._safe(
                data.liquidity_score
            )
            < self.minimum_liquidity
        ):
            return False

        if (
            evidence_strength
            < self.minimum_evidence
        ):
            return False

        if (
            quality
            < self.minimum_quality
        ):
            return False

        if (
            abs(
                self._safe(
                    data.expected_move_pct
                )
            )
            < self.minimum_expected_move
        ):
            return False

        return True


    # ========================================================
    # GRADE
    # ========================================================

    def grade(
        self,
        quality: float,
    ) -> ScannerGrade:

        # Scanner grade is current opportunity quality.
        # It is NOT historical win probability.

        if quality >= 74.0:
            return ScannerGrade.A_PLUS

        if quality >= 65.0:
            return ScannerGrade.A

        if quality >= 45.0:
            return ScannerGrade.B_PLUS

        if quality >= 35.0:
            return ScannerGrade.B

        return ScannerGrade.NO_TRADE


    # ========================================================
    # BUILD OPPORTUNITY
    # ========================================================

    def build_opportunity(
        self,
        data: ScannerInput,
    ) -> ScannerOpportunity:

        evidence_strength = (
            self.calculate_evidence_strength(
                data
            )
        )

        quality = (
            self.calculate_quality(
                data,
                evidence_strength,
            )
        )

        expected_magnitude = (
            self.calculate_expected_magnitude(
                data
            )
        )

        volatility_score = (
            self.calculate_volatility_score(
                data
            )
        )

        timing_score = (
            self.calculate_timing_score(
                data
            )
        )

        stability = (
            self.calculate_stability(
                data
            )
        )

        execution = (
            self.calculate_execution_suitability(
                data
            )
        )

        qualified = self.qualify(
            data,
            quality,
            evidence_strength,
        )

        grade = self.grade(
            quality
        )

        warnings = list(
            data.warnings
        )

        if not qualified:
            warnings.append(
                "Opportunity did not satisfy "
                "scanner qualification requirements."
            )

        return ScannerOpportunity(

            instrument=data.instrument,

            timestamp=data.timestamp,

            direction=data.direction,

            grade=grade,

            status=(
                ScannerStatus.QUALIFIED
                if qualified
                else ScannerStatus.REJECTED
            ),

            quality_score=quality,

            evidence_strength=(
                evidence_strength
            ),

            timing_score=timing_score,

            liquidity_score=(
                self._clamp(
                    data.liquidity_score
                )
            ),

            volatility_score=(
                volatility_score
            ),

            risk_score=(
                self._clamp(
                    data.risk_score
                )
            ),

            expected_magnitude=(
                expected_magnitude
            ),

            execution_suitability=(
                execution
            ),

            intelligence_stability=(
                stability
            ),

            expected_move_pct=(
                data.expected_move_pct
            ),

            expected_horizon_minutes=(
                data.expected_horizon_minutes
            ),

            market=data.market,

            exchange=data.exchange,

            asset_class=data.asset_class,

            timeframe=data.timeframe,

            evidence_reference=(
                list(data.evidence)
            ),

            warnings=warnings,
        )


    # ========================================================
    # RANKING SCORE
    # ========================================================

    def ranking_score(
        self,
        opportunity: ScannerOpportunity,
    ) -> float:

        return self._clamp(
            (
                opportunity.quality_score
                * 0.25

                + opportunity.evidence_strength
                * 0.15

                + opportunity.timing_score
                * 0.10

                + opportunity.liquidity_score
                * 0.10

                + opportunity.volatility_score
                * 0.05

                + opportunity.risk_score
                * 0.10

                + opportunity.expected_magnitude
                * 0.10

                + opportunity.execution_suitability
                * 0.05

                + opportunity.intelligence_stability
                * 0.10
            )
        )


    # ========================================================
    # RANK
    # ========================================================

    def rank(
        self,
        opportunities: List[
            ScannerOpportunity
        ],
    ) -> List[
        ScannerOpportunity
    ]:

        qualified = [
            item
            for item in opportunities
            if item.status
            == ScannerStatus.QUALIFIED
        ]

        qualified.sort(
            key=self.ranking_score,
            reverse=True,
        )

        for index, item in enumerate(
            qualified,
            start=1,
        ):

            item.rank = index

        return qualified


    # ========================================================
    # SCAN UNIVERSE
    # ========================================================

    def scan(
        self,
        inputs: List[ScannerInput],
        scan_id: Optional[str] = None,
    ) -> ScannerResult:

        timestamp = datetime.utcnow()

        if scan_id is None:

            scan_id = (
                f"SCAN-"
                f"{timestamp.strftime('%Y%m%d%H%M%S')}"
            )

        universe = [
            item.instrument
            for item in inputs
            if item.instrument
        ]

        opportunities = []

        rejected_count = 0

        for data in inputs:

            opportunity = (
                self.build_opportunity(
                    data
                )
            )

            if (
                opportunity.status
                == ScannerStatus.QUALIFIED
            ):

                opportunities.append(
                    opportunity
                )

            else:

                rejected_count += 1

        ranked = self.rank(
            opportunities
        )

        top_opportunities = ranked[
            :self.top_n
        ]

        warnings = []

        if not inputs:

            warnings.append(
                "Scanner received an empty universe."
            )

        if not top_opportunities:

            warnings.append(
                "No opportunity satisfied "
                "current scanner qualification."
            )

        return ScannerResult(

            scan_id=scan_id,

            timestamp=timestamp,

            universe=universe,

            qualified_count=len(
                ranked
            ),

            opportunities=(
                top_opportunities
            ),

            ranking_method=(
                "MULTI_DIMENSION_INTELLIGENCE_RANKING"
            ),

            rejected_count=rejected_count,

            warnings=warnings,
        )


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================

def run_scan(
    inputs: List[ScannerInput],
    top_n: int = 10,
    scan_id: Optional[str] = None,
) -> ScannerResult:

    scanner = ScannerModel(
        top_n=top_n
    )

    return scanner.scan(
        inputs=inputs,
        scan_id=scan_id,
    )


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "ScannerDirection",
    "ScannerGrade",
    "ScannerStatus",
    "ScannerInput",
    "ScannerOpportunity",
    "ScannerResult",
    "ScannerModel",
    "run_scan",
]
# ============================================================
# ROBOMLM_PLUS
# SCANNER MODELS
# PART 2
# Opportunity Evidence + Quality Model
# ============================================================

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ------------------------------------------------------------
# Evidence Component
# ------------------------------------------------------------

@dataclass
class ScannerEvidenceComponent:
    """
    Normalized evidence contribution received by the scanner.

    Scanner does not create market intelligence.
    It only stores/normalizes upstream intelligence.
    """

    name: str
    score: float = 0.0
    weight: float = 0.0
    available: bool = True
    source_engine: str = ""
    direction: str = "NEUTRAL"
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def normalized_score(self) -> float:
        try:
            value = float(self.score)
        except (TypeError, ValueError):
            return 0.0

        return max(0.0, min(100.0, value))

    def normalized_weight(self) -> float:
        try:
            value = float(self.weight)
        except (TypeError, ValueError):
            return 0.0

        return max(0.0, value)

    def normalized_confidence(self) -> float:
        try:
            value = float(self.confidence)
        except (TypeError, ValueError):
            return 0.0

        return max(0.0, min(100.0, value))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "score": self.normalized_score(),
            "weight": self.normalized_weight(),
            "available": self.available,
            "source_engine": self.source_engine,
            "direction": self.direction,
            "confidence": self.normalized_confidence(),
            "metadata": dict(self.metadata),
        }


# ------------------------------------------------------------
# Opportunity Quality Breakdown
# ------------------------------------------------------------

@dataclass
class ScannerQualityBreakdown:
    """
    Explains how scanner opportunity quality was formed.

    This is a measurement container.
    It is NOT final D13 decision authority.
    """

    structure: float = 0.0
    accumulation: float = 0.0
    distribution: float = 0.0
    boundary: float = 0.0
    breakout: float = 0.0
    confirmation: float = 0.0

    regime: float = 0.0
    relationship: float = 0.0

    thesis: float = 0.0
    growth: float = 0.0
    pullback: float = 0.0
    holdability: float = 0.0
    protection: float = 0.0

    evidence_strength: float = 0.0
    data_quality: float = 0.0
    liquidity: float = 0.0
    execution_suitability: float = 0.0
    risk_quality: float = 0.0

    expected_move_pct: float = 0.0
    expected_horizon_minutes: float = 0.0

    direction_alignment: float = 0.0
    conflict_penalty: float = 0.0

    def clamp(self) -> None:
        numeric_fields = [
            "structure",
            "accumulation",
            "distribution",
            "boundary",
            "breakout",
            "confirmation",
            "regime",
            "relationship",
            "thesis",
            "growth",
            "pullback",
            "holdability",
            "protection",
            "evidence_strength",
            "data_quality",
            "liquidity",
            "execution_suitability",
            "risk_quality",
            "expected_move_pct",
            "expected_horizon_minutes",
            "direction_alignment",
            "conflict_penalty",
        ]

        for field_name in numeric_fields:
            value = getattr(self, field_name, 0.0)

            try:
                value = float(value)
            except (TypeError, ValueError):
                value = 0.0

            if field_name == "expected_move_pct":
                value = max(0.0, value)
            elif field_name == "expected_horizon_minutes":
                value = max(0.0, value)
            elif field_name == "conflict_penalty":
                value = max(0.0, min(100.0, value))
            else:
                value = max(0.0, min(100.0, value))

            setattr(self, field_name, value)

    def to_dict(self) -> Dict[str, Any]:
        self.clamp()

        return {
            "structure": self.structure,
            "accumulation": self.accumulation,
            "distribution": self.distribution,
            "boundary": self.boundary,
            "breakout": self.breakout,
            "confirmation": self.confirmation,
            "regime": self.regime,
            "relationship": self.relationship,
            "thesis": self.thesis,
            "growth": self.growth,
            "pullback": self.pullback,
            "holdability": self.holdability,
            "protection": self.protection,
            "evidence_strength": self.evidence_strength,
            "data_quality": self.data_quality,
            "liquidity": self.liquidity,
            "execution_suitability": self.execution_suitability,
            "risk_quality": self.risk_quality,
            "expected_move_pct": self.expected_move_pct,
            "expected_horizon_minutes": self.expected_horizon_minutes,
            "direction_alignment": self.direction_alignment,
            "conflict_penalty": self.conflict_penalty,
        }


# ------------------------------------------------------------
# Scanner Opportunity Model
# ------------------------------------------------------------

@dataclass
class ScannerOpportunityModel:
    """
    Complete normalized opportunity representation.

    Upstream engines provide intelligence.
    Scanner model organizes it for ranking.

    Final decision remains outside this model.
    """

    instrument: str
    exchange: str = ""
    market: str = ""
    asset_class: str = ""
    timeframe: str = ""

    timestamp: Optional[str] = None

    direction: str = "UNKNOWN"

    current_price: float = 0.0
    entry_price: Optional[float] = None
    entry_low: Optional[float] = None
    entry_high: Optional[float] = None

    expected_move_pct: float = 0.0
    expected_move_price: Optional[float] = None
    expected_horizon_minutes: float = 0.0

    invalidation_price: Optional[float] = None
    target_price: Optional[float] = None

    quality_score: float = 0.0
    evidence_strength: float = 0.0
    opportunity_score: float = 0.0

    risk_score: float = 0.0
    liquidity_score: float = 0.0
    timing_score: float = 0.0
    volatility_score: float = 0.0
    execution_score: float = 0.0
    stability_score: float = 0.0

    grade: str = "NO_TRADE"

    qualified: bool = False

    evidence: List[ScannerEvidenceComponent] = field(
        default_factory=list
    )

    quality_breakdown: ScannerQualityBreakdown = field(
        default_factory=ScannerQualityBreakdown
    )

    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def normalize(self) -> None:
        self.quality_score = self._clamp(self.quality_score)
        self.evidence_strength = self._clamp(self.evidence_strength)
        self.opportunity_score = self._clamp(self.opportunity_score)

        self.risk_score = self._clamp(self.risk_score)
        self.liquidity_score = self._clamp(self.liquidity_score)
        self.timing_score = self._clamp(self.timing_score)
        self.volatility_score = self._clamp(self.volatility_score)
        self.execution_score = self._clamp(self.execution_score)
        self.stability_score = self._clamp(self.stability_score)

        try:
            self.expected_move_pct = max(
                0.0,
                float(self.expected_move_pct)
            )
        except (TypeError, ValueError):
            self.expected_move_pct = 0.0

        try:
            self.expected_horizon_minutes = max(
                0.0,
                float(self.expected_horizon_minutes)
            )
        except (TypeError, ValueError):
            self.expected_horizon_minutes = 0.0

        self.quality_breakdown.clamp()

    @staticmethod
    def _clamp(value: Any) -> float:
        try:
            value = float(value)
        except (TypeError, ValueError):
            return 0.0

        return max(0.0, min(100.0, value))

    def add_warning(self, message: str) -> None:
        if message and message not in self.warnings:
            self.warnings.append(str(message))

    def add_evidence(
        self,
        name: str,
        score: float,
        weight: float = 0.0,
        source_engine: str = "",
        direction: str = "NEUTRAL",
        confidence: float = 0.0,
        available: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:

        component = ScannerEvidenceComponent(
            name=name,
            score=score,
            weight=weight,
            available=available,
            source_engine=source_engine,
            direction=direction,
            confidence=confidence,
            metadata=metadata or {},
        )

        self.evidence.append(component)

    def evidence_count(self) -> int:
        return len(
            [
                item
                for item in self.evidence
                if item.available
            ]
        )

    def to_dict(self) -> Dict[str, Any]:
        self.normalize()

        return {
            "instrument": self.instrument,
            "exchange": self.exchange,
            "market": self.market,
            "asset_class": self.asset_class,
            "timeframe": self.timeframe,
            "timestamp": self.timestamp,
            "direction": self.direction,
            "current_price": self.current_price,
            "entry_price": self.entry_price,
            "entry_low": self.entry_low,
            "entry_high": self.entry_high,
            "expected_move_pct": self.expected_move_pct,
            "expected_move_price": self.expected_move_price,
            "expected_horizon_minutes": self.expected_horizon_minutes,
            "invalidation_price": self.invalidation_price,
            "target_price": self.target_price,
            "quality_score": self.quality_score,
            "evidence_strength": self.evidence_strength,
            "opportunity_score": self.opportunity_score,
            "risk_score": self.risk_score,
            "liquidity_score": self.liquidity_score,
            "timing_score": self.timing_score,
            "volatility_score": self.volatility_score,
            "execution_score": self.execution_score,
            "stability_score": self.stability_score,
            "grade": self.grade,
            "qualified": self.qualified,
            "evidence": [
                item.to_dict()
                for item in self.evidence
            ],
            "quality_breakdown": self.quality_breakdown.to_dict(),
            "warnings": list(self.warnings),
            "metadata": dict(self.metadata),
        }


# ------------------------------------------------------------
# Model Collection
# ------------------------------------------------------------

@dataclass
class ScannerOpportunityCollection:
    """
    Container for multiple scanner opportunities.
    """

    timestamp: Optional[str] = None
    opportunities: List[ScannerOpportunityModel] = field(
        default_factory=list
    )

    def add(
        self,
        opportunity: ScannerOpportunityModel
    ) -> None:
        if not isinstance(
            opportunity,
            ScannerOpportunityModel
        ):
            raise TypeError(
                "opportunity must be ScannerOpportunityModel"
            )

        self.opportunities.append(opportunity)

    def qualified(self) -> List[ScannerOpportunityModel]:
        return [
            item
            for item in self.opportunities
            if item.qualified
        ]

    def rejected(self) -> List[ScannerOpportunityModel]:
        return [
            item
            for item in self.opportunities
            if not item.qualified
        ]

    def sort_by_quality(self) -> List[ScannerOpportunityModel]:
        return sorted(
            self.opportunities,
            key=lambda item: (
                item.opportunity_score,
                item.quality_score,
                item.evidence_strength,
            ),
            reverse=True,
        )

    def top(
        self,
        limit: int = 5
    ) -> List[ScannerOpportunityModel]:
        try:
            limit = max(1, int(limit))
        except (TypeError, ValueError):
            limit = 5

        return self.sort_by_quality()[:limit]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "count": len(self.opportunities),
            "qualified_count": len(self.qualified()),
            "rejected_count": len(self.rejected()),
            "opportunities": [
                item.to_dict()
                for item in self.sort_by_quality()
            ],
        }


__all__ = [
    "ScannerEvidenceComponent",
    "ScannerQualityBreakdown",
    "ScannerOpportunityModel",
    "ScannerOpportunityCollection",
]
# ============================================================
# ROBOMLM_PLUS
# SCANNER MODELS
# PART 3
# Ranking + Grade + Qualification Support
# ============================================================

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# ------------------------------------------------------------
# Scanner Ranking Configuration
# ------------------------------------------------------------

@dataclass
class ScannerRankingConfig:
    """
    Ranking configuration.

    These are scanner aggregation parameters only.
    They do not create upstream market intelligence.
    """

    quality_weight: float = 0.25
    evidence_weight: float = 0.20
    timing_weight: float = 0.10
    liquidity_weight: float = 0.10
    volatility_weight: float = 0.05
    risk_weight: float = 0.10
    execution_weight: float = 0.05
    stability_weight: float = 0.05
    magnitude_weight: float = 0.10

    minimum_data_quality: float = 50.0
    minimum_evidence_strength: float = 40.0
    minimum_liquidity: float = 30.0

    # Preserve agreed EQE grade structure.
    no_trade_max: float = 35.0
    b_max: float = 45.0
    b_plus_max: float = 65.0
    a_max: float = 74.0

    def normalized_weights(self) -> Dict[str, float]:
        weights = {
            "quality": max(0.0, float(self.quality_weight)),
            "evidence": max(0.0, float(self.evidence_weight)),
            "timing": max(0.0, float(self.timing_weight)),
            "liquidity": max(0.0, float(self.liquidity_weight)),
            "volatility": max(0.0, float(self.volatility_weight)),
            "risk": max(0.0, float(self.risk_weight)),
            "execution": max(0.0, float(self.execution_weight)),
            "stability": max(0.0, float(self.stability_weight)),
            "magnitude": max(0.0, float(self.magnitude_weight)),
        }

        total = sum(weights.values())

        if total <= 0.0:
            return {
                key: 0.0
                for key in weights
            }

        return {
            key: value / total
            for key, value in weights.items()
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "weights": self.normalized_weights(),
            "minimum_data_quality": self.minimum_data_quality,
            "minimum_evidence_strength": self.minimum_evidence_strength,
            "minimum_liquidity": self.minimum_liquidity,
            "grade_boundaries": {
                "no_trade_max": self.no_trade_max,
                "b_max": self.b_max,
                "b_plus_max": self.b_plus_max,
                "a_max": self.a_max,
            },
        }


# ------------------------------------------------------------
# Ranking Result
# ------------------------------------------------------------

@dataclass
class ScannerRankingResult:
    """
    Ranking result for one opportunity.
    """

    instrument: str

    ranking_score: float = 0.0
    rank: int = 0

    qualified: bool = False
    grade: str = "NO_TRADE"

    components: Dict[str, float] = field(
        default_factory=dict
    )

    rejection_reasons: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "instrument": self.instrument,
            "ranking_score": self.ranking_score,
            "rank": self.rank,
            "qualified": self.qualified,
            "grade": self.grade,
            "components": dict(self.components),
            "rejection_reasons": list(self.rejection_reasons),
            "metadata": dict(self.metadata),
        }


# ------------------------------------------------------------
# Scanner Model Engine
# ------------------------------------------------------------

class ScannerModelEngine:
    """
    Converts normalized ScannerOpportunityModel objects into
    ranked scanner results.

    IMPORTANT:
    - Does not calculate raw market intelligence.
    - Does not replace D13.
    - Does not invent missing evidence.
    - Does not force an opportunity when none qualifies.
    """

    VERSION = "1.0.0"

    def __init__(
        self,
        config: Optional[ScannerRankingConfig] = None,
    ) -> None:

        self.config = (
            config
            if config is not None
            else ScannerRankingConfig()
        )

    # --------------------------------------------------------
    # Utility
    # --------------------------------------------------------

    @staticmethod
    def _safe(value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _clamp(
        value: Any,
        minimum: float = 0.0,
        maximum: float = 100.0,
    ) -> float:

        value = ScannerModelEngine._safe(value)

        return max(
            minimum,
            min(maximum, value)
        )

    # --------------------------------------------------------
    # Expected Magnitude Score
    # --------------------------------------------------------

    def magnitude_score(
        self,
        opportunity: Any,
    ) -> float:

        expected_move = self._safe(
            getattr(
                opportunity,
                "expected_move_pct",
                0.0,
            )
        )

        if expected_move <= 0.0:
            return 0.0

        # Scanner normalization only.
        # No directional prediction is created here.
        score = min(
            100.0,
            expected_move * 10.0,
        )

        return self._clamp(score)

    # --------------------------------------------------------
    # Risk Quality
    # --------------------------------------------------------

    def risk_quality(
        self,
        opportunity: Any,
    ) -> float:

        risk = self._clamp(
            getattr(
                opportunity,
                "risk_score",
                0.0,
            )
        )

        # Higher risk score is treated as stronger
        # risk-quality input when upstream engine defines it
        # on a 0-100 quality scale.
        return risk

    # --------------------------------------------------------
    # Ranking Score
    # --------------------------------------------------------

    def calculate_ranking_score(
        self,
        opportunity: Any,
    ) -> Tuple[float, Dict[str, float]]:

        weights = self.config.normalized_weights()

        quality = self._clamp(
            getattr(
                opportunity,
                "quality_score",
                0.0,
            )
        )

        evidence = self._clamp(
            getattr(
                opportunity,
                "evidence_strength",
                0.0,
            )
        )

        timing = self._clamp(
            getattr(
                opportunity,
                "timing_score",
                0.0,
            )
        )

        liquidity = self._clamp(
            getattr(
                opportunity,
                "liquidity_score",
                0.0,
            )
        )

        volatility = self._clamp(
            getattr(
                opportunity,
                "volatility_score",
                0.0,
            )
        )

        risk = self.risk_quality(
            opportunity
        )

        execution = self._clamp(
            getattr(
                opportunity,
                "execution_score",
                0.0,
            )
        )

        stability = self._clamp(
            getattr(
                opportunity,
                "stability_score",
                0.0,
            )
        )

        magnitude = self.magnitude_score(
            opportunity
        )

        components = {
            "quality": quality,
            "evidence": evidence,
            "timing": timing,
            "liquidity": liquidity,
            "volatility": volatility,
            "risk": risk,
            "execution": execution,
            "stability": stability,
            "magnitude": magnitude,
        }

        score = sum(
            components[key] * weights[key]
            for key in components
        )

        return (
            self._clamp(score),
            components,
        )

    # --------------------------------------------------------
    # EQE Grade Mapping
    # --------------------------------------------------------

    def grade_from_score(
        self,
        score: float,
    ) -> str:

        score = self._clamp(score)

        if score < self.config.no_trade_max:
            return "NO_TRADE"

        if score < self.config.b_max:
            return "B"

        if score < self.config.b_plus_max:
            return "B+"

        if score < self.config.a_max:
            return "A"

        return "A+"

    # --------------------------------------------------------
    # Qualification
    # --------------------------------------------------------

    def qualification_check(
        self,
        opportunity: Any,
    ) -> Tuple[bool, List[str]]:

        reasons: List[str] = []

        data_quality = self._clamp(
            getattr(
                opportunity,
                "quality_score",
                0.0,
            )
        )

        evidence = self._clamp(
            getattr(
                opportunity,
                "evidence_strength",
                0.0,
            )
        )

        liquidity = self._clamp(
            getattr(
                opportunity,
                "liquidity_score",
                0.0,
            )
        )

        direction = str(
            getattr(
                opportunity,
                "direction",
                "UNKNOWN",
            )
        ).upper()

        if data_quality < self.config.minimum_data_quality:
            reasons.append(
                "data_quality_below_minimum"
            )

        if evidence < self.config.minimum_evidence_strength:
            reasons.append(
                "evidence_strength_below_minimum"
            )

        if liquidity < self.config.minimum_liquidity:
            reasons.append(
                "liquidity_below_minimum"
            )

        if direction in {
            "",
            "UNKNOWN",
            "NEUTRAL",
        }:
            reasons.append(
                "direction_not_actionable"
            )

        return (
            len(reasons) == 0,
            reasons,
        )

    # --------------------------------------------------------
    # Build Ranking Result
    # --------------------------------------------------------

    def evaluate(
        self,
        opportunity: Any,
    ) -> ScannerRankingResult:

        instrument = str(
            getattr(
                opportunity,
                "instrument",
                "",
            )
        )

        score, components = (
            self.calculate_ranking_score(
                opportunity
            )
        )

        qualified, reasons = (
            self.qualification_check(
                opportunity
            )
        )

        grade = self.grade_from_score(
            score
        )

        if not qualified:
            grade = "NO_TRADE"

        return ScannerRankingResult(
            instrument=instrument,
            ranking_score=score,
            rank=0,
            qualified=qualified,
            grade=grade,
            components=components,
            rejection_reasons=reasons,
            metadata={
                "engine": "ScannerModelEngine",
                "version": self.VERSION,
            },
        )

    # --------------------------------------------------------
    # Rank Collection
    # --------------------------------------------------------

    def rank(
        self,
        opportunities: List[Any],
    ) -> List[ScannerRankingResult]:

        results: List[ScannerRankingResult] = []

        for opportunity in opportunities:

            result = self.evaluate(
                opportunity
            )

            results.append(result)

        results.sort(
            key=lambda item: (
                item.qualified,
                item.ranking_score,
                item.components.get(
                    "evidence",
                    0.0,
                ),
                item.components.get(
                    "quality",
                    0.0,
                ),
            ),
            reverse=True,
        )

        for index, result in enumerate(
            results,
            start=1,
        ):
            result.rank = index

        return results

    # --------------------------------------------------------
    # Top Opportunities
    # --------------------------------------------------------

    def top(
        self,
        opportunities: List[Any],
        limit: int = 5,
    ) -> List[ScannerRankingResult]:

        try:
            limit = max(
                1,
                int(limit),
            )
        except (TypeError, ValueError):
            limit = 5

        ranked = self.rank(
            opportunities
        )

        return [
            result
            for result in ranked
            if result.qualified
        ][:limit]


# ------------------------------------------------------------
# Convenience Function
# ------------------------------------------------------------

def rank_scanner_opportunities(
    opportunities: List[Any],
    config: Optional[
        ScannerRankingConfig
    ] = None,
) -> List[ScannerRankingResult]:

    engine = ScannerModelEngine(
        config=config
    )

    return engine.rank(
        opportunities
    )


# ------------------------------------------------------------
# Public API
# ------------------------------------------------------------

__all__ = [
    "ScannerRankingConfig",
    "ScannerRankingResult",
    "ScannerModelEngine",
    "rank_scanner_opportunities",
]
# ============================================================
# ROBOMLM_PLUS
# SCANNER MODELS
# PART 4
# Scan Result + Top-N + Serialization
# ============================================================

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ------------------------------------------------------------
# Scanner Candidate Snapshot
# ------------------------------------------------------------

@dataclass
class ScannerCandidateSnapshot:
    """
    Immutable-style snapshot of one scanner candidate.

    This model stores the state used by the scanner at a
    particular scan cycle.
    """

    instrument: str
    exchange: str = ""
    market: str = ""
    asset_class: str = ""

    timestamp: Optional[str] = None

    direction: str = "UNKNOWN"
    grade: str = "NO_TRADE"

    ranking_score: float = 0.0
    quality_score: float = 0.0
    evidence_strength: float = 0.0

    timing_score: float = 0.0
    liquidity_score: float = 0.0
    volatility_score: float = 0.0
    risk_score: float = 0.0
    execution_score: float = 0.0
    stability_score: float = 0.0

    expected_move_pct: float = 0.0
    expected_horizon_minutes: float = 0.0

    rank: int = 0
    qualified: bool = False

    evidence_reference: Optional[str] = None

    warnings: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    @staticmethod
    def _number(value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _score(value: Any) -> float:
        try:
            value = float(value)
        except (TypeError, ValueError):
            return 0.0

        return max(
            0.0,
            min(100.0, value),
        )

    def normalize(self) -> None:

        score_fields = [
            "ranking_score",
            "quality_score",
            "evidence_strength",
            "timing_score",
            "liquidity_score",
            "volatility_score",
            "risk_score",
            "execution_score",
            "stability_score",
        ]

        for field_name in score_fields:
            setattr(
                self,
                field_name,
                self._score(
                    getattr(
                        self,
                        field_name,
                        0.0,
                    )
                ),
            )

        self.expected_move_pct = max(
            0.0,
            self._number(
                self.expected_move_pct
            ),
        )

        self.expected_horizon_minutes = max(
            0.0,
            self._number(
                self.expected_horizon_minutes
            ),
        )

        try:
            self.rank = max(
                0,
                int(self.rank),
            )
        except (TypeError, ValueError):
            self.rank = 0

    def to_dict(self) -> Dict[str, Any]:

        self.normalize()

        return {
            "instrument": self.instrument,
            "exchange": self.exchange,
            "market": self.market,
            "asset_class": self.asset_class,
            "timestamp": self.timestamp,
            "direction": self.direction,
            "grade": self.grade,
            "ranking_score": self.ranking_score,
            "quality_score": self.quality_score,
            "evidence_strength": self.evidence_strength,
            "timing_score": self.timing_score,
            "liquidity_score": self.liquidity_score,
            "volatility_score": self.volatility_score,
            "risk_score": self.risk_score,
            "execution_score": self.execution_score,
            "stability_score": self.stability_score,
            "expected_move_pct": self.expected_move_pct,
            "expected_horizon_minutes": (
                self.expected_horizon_minutes
            ),
            "rank": self.rank,
            "qualified": self.qualified,
            "evidence_reference": (
                self.evidence_reference
            ),
            "warnings": list(self.warnings),
            "metadata": dict(self.metadata),
        }


# ------------------------------------------------------------
# Scanner Result Model
# ------------------------------------------------------------

@dataclass
class ScannerResultModel:
    """
    Complete output of one scanner cycle.

    Important:
    This is a scanner output model, not a D13 decision.
    """

    scan_id: str

    timestamp: Optional[str] = None

    universe_size: int = 0
    scanned_count: int = 0
    qualified_count: int = 0
    rejected_count: int = 0

    opportunities: List[
        ScannerCandidateSnapshot
    ] = field(default_factory=list)

    ranking_method: str = (
        "multi_dimensional_opportunity_ranking"
    )

    top_n: int = 5

    market_coverage: List[str] = field(
        default_factory=list
    )

    exchanges: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def normalize(self) -> None:

        try:
            self.universe_size = max(
                0,
                int(self.universe_size),
            )
        except (TypeError, ValueError):
            self.universe_size = 0

        try:
            self.scanned_count = max(
                0,
                int(self.scanned_count),
            )
        except (TypeError, ValueError):
            self.scanned_count = 0

        try:
            self.qualified_count = max(
                0,
                int(self.qualified_count),
            )
        except (TypeError, ValueError):
            self.qualified_count = 0

        try:
            self.rejected_count = max(
                0,
                int(self.rejected_count),
            )
        except (TypeError, ValueError):
            self.rejected_count = 0

        try:
            self.top_n = max(
                1,
                int(self.top_n),
            )
        except (TypeError, ValueError):
            self.top_n = 5

        for item in self.opportunities:
            item.normalize()

    # --------------------------------------------------------
    # Qualified Opportunities
    # --------------------------------------------------------

    def qualified_opportunities(
        self,
    ) -> List[ScannerCandidateSnapshot]:

        return [
            item
            for item in self.opportunities
            if item.qualified
        ]

    # --------------------------------------------------------
    # Top Opportunities
    # --------------------------------------------------------

    def top_opportunities(
        self,
        limit: Optional[int] = None,
    ) -> List[ScannerCandidateSnapshot]:

        if limit is None:
            limit = self.top_n

        try:
            limit = max(
                1,
                int(limit),
            )
        except (TypeError, ValueError):
            limit = self.top_n

        qualified = self.qualified_opportunities()

        ordered = sorted(
            qualified,
            key=lambda item: (
                item.ranking_score,
                item.quality_score,
                item.evidence_strength,
            ),
            reverse=True,
        )

        return ordered[:limit]

    # --------------------------------------------------------
    # Grade Distribution
    # --------------------------------------------------------

    def grade_distribution(
        self,
    ) -> Dict[str, int]:

        distribution = {
            "A+": 0,
            "A": 0,
            "B+": 0,
            "B": 0,
            "NO_TRADE": 0,
        }

        for item in self.opportunities:

            grade = str(
                item.grade
            ).upper()

            if grade not in distribution:
                grade = "NO_TRADE"

            distribution[grade] += 1

        return distribution

    # --------------------------------------------------------
    # Direction Distribution
    # --------------------------------------------------------

    def direction_distribution(
        self,
    ) -> Dict[str, int]:

        distribution: Dict[str, int] = {}

        for item in self.opportunities:

            direction = str(
                item.direction
            ).upper()

            if not direction:
                direction = "UNKNOWN"

            distribution[direction] = (
                distribution.get(
                    direction,
                    0,
                ) + 1
            )

        return distribution

    # --------------------------------------------------------
    # Best Opportunity
    # --------------------------------------------------------

    def best_opportunity(
        self,
    ) -> Optional[ScannerCandidateSnapshot]:

        top = self.top_opportunities(
            limit=1
        )

        if not top:
            return None

        return top[0]

    # --------------------------------------------------------
    # Has Actionable Opportunity
    # --------------------------------------------------------

    def has_actionable_opportunity(
        self,
    ) -> bool:

        return any(
            item.qualified
            for item in self.opportunities
        )

    # --------------------------------------------------------
    # Add Warning
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Serialization
    # --------------------------------------------------------

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        self.normalize()

        top = self.top_opportunities()

        return {
            "scan_id": self.scan_id,
            "timestamp": self.timestamp,
            "universe_size": self.universe_size,
            "scanned_count": self.scanned_count,
            "qualified_count": self.qualified_count,
            "rejected_count": self.rejected_count,
            "ranking_method": self.ranking_method,
            "top_n": self.top_n,
            "market_coverage": list(
                self.market_coverage
            ),
            "exchanges": list(
                self.exchanges
            ),
            "grade_distribution": (
                self.grade_distribution()
            ),
            "direction_distribution": (
                self.direction_distribution()
            ),
            "has_actionable_opportunity": (
                self.has_actionable_opportunity()
            ),
            "best_opportunity": (
                top[0].to_dict()
                if top
                else None
            ),
            "top_opportunities": [
                item.to_dict()
                for item in top
            ],
            "all_opportunities": [
                item.to_dict()
                for item in self.opportunities
            ],
            "warnings": list(
                self.warnings
            ),
            "metadata": dict(
                self.metadata
            ),
        }


# ------------------------------------------------------------
# Scanner Result Builder
# ------------------------------------------------------------

def build_scanner_result(
    scan_id: str,
    opportunities: List[
        ScannerCandidateSnapshot
    ],
    timestamp: Optional[str] = None,
    universe_size: Optional[int] = None,
    top_n: int = 5,
    ranking_method: str = (
        "multi_dimensional_opportunity_ranking"
    ),
) -> ScannerResultModel:

    qualified = [
        item
        for item in opportunities
        if item.qualified
    ]

    rejected = [
        item
        for item in opportunities
        if not item.qualified
    ]

    ordered = sorted(
        opportunities,
        key=lambda item: (
            item.qualified,
            item.ranking_score,
            item.quality_score,
            item.evidence_strength,
        ),
        reverse=True,
    )

    for index, item in enumerate(
        ordered,
        start=1,
    ):
        item.rank = index

    if universe_size is None:
        universe_size = len(opportunities)

    exchanges = sorted(
        {
            str(item.exchange)
            for item in opportunities
            if item.exchange
        }
    )

    markets = sorted(
        {
            str(item.market)
            for item in opportunities
            if item.market
        }
    )

    result = ScannerResultModel(
        scan_id=scan_id,
        timestamp=timestamp,
        universe_size=universe_size,
        scanned_count=len(opportunities),
        qualified_count=len(qualified),
        rejected_count=len(rejected),
        opportunities=ordered,
        ranking_method=ranking_method,
        top_n=top_n,
        market_coverage=markets,
        exchanges=exchanges,
    )

    return result


# ------------------------------------------------------------
# Public API
# ------------------------------------------------------------

__all__ = [
    "ScannerCandidateSnapshot",
    "ScannerResultModel",
    "build_scanner_result",
]
# ============================================================
# ROBOMLM_PLUS
# SCANNER MODELS
# PART 5
# Validation + Consistency + Audit Support
# ============================================================

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ------------------------------------------------------------
# Validation Issue
# ------------------------------------------------------------

@dataclass
class ScannerValidationIssue:
    """
    Validation issue generated by the scanner model layer.

    Validation does not alter intelligence.
    It identifies incomplete or inconsistent model state.
    """

    code: str
    message: str
    severity: str = "WARNING"
    field: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "field": self.field,
        }


# ------------------------------------------------------------
# Scanner Model Validator
# ------------------------------------------------------------

class ScannerModelValidator:
    """
    Structural validation for scanner model objects.

    This validator does NOT:
    - generate market intelligence
    - calculate direction
    - modify upstream formulas
    - make D13 decisions
    - force qualification
    """

    VERSION = "1.0.0"

    REQUIRED_ATTRIBUTES = (
        "instrument",
        "direction",
        "quality_score",
        "evidence_strength",
        "liquidity_score",
    )

    SCORE_ATTRIBUTES = (
        "quality_score",
        "evidence_strength",
        "opportunity_score",
        "risk_score",
        "liquidity_score",
        "timing_score",
        "volatility_score",
        "execution_score",
        "stability_score",
    )

    def __init__(
        self,
        strict: bool = False,
    ) -> None:

        self.strict = bool(strict)

    # --------------------------------------------------------
    # Safe Numeric Conversion
    # --------------------------------------------------------

    @staticmethod
    def _number(
        value: Any,
    ) -> Optional[float]:

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    # --------------------------------------------------------
    # Single Opportunity Validation
    # --------------------------------------------------------

    def validate_opportunity(
        self,
        opportunity: Any,
    ) -> List[ScannerValidationIssue]:

        issues: List[
            ScannerValidationIssue
        ] = []

        if opportunity is None:
            return [
                ScannerValidationIssue(
                    code="NULL_OPPORTUNITY",
                    message=(
                        "Opportunity object is None."
                    ),
                    severity="ERROR",
                )
            ]

        # Required fields
        for field_name in self.REQUIRED_ATTRIBUTES:

            if not hasattr(
                opportunity,
                field_name,
            ):
                issues.append(
                    ScannerValidationIssue(
                        code="MISSING_FIELD",
                        message=(
                            f"Required field "
                            f"'{field_name}' is missing."
                        ),
                        severity="ERROR",
                        field=field_name,
                    )
                )

        # Instrument
        instrument = getattr(
            opportunity,
            "instrument",
            None,
        )

        if not instrument:
            issues.append(
                ScannerValidationIssue(
                    code="EMPTY_INSTRUMENT",
                    message=(
                        "Instrument identifier is empty."
                    ),
                    severity="ERROR",
                    field="instrument",
                )
            )

        # Direction
        direction = str(
            getattr(
                opportunity,
                "direction",
                "UNKNOWN",
            )
        ).upper()

        valid_directions = {
            "BUY",
            "SELL",
            "CALL",
            "PUT",
            "NEUTRAL",
            "UNKNOWN",
        }

        if direction not in valid_directions:
            issues.append(
                ScannerValidationIssue(
                    code="INVALID_DIRECTION",
                    message=(
                        f"Unknown direction '{direction}'."
                    ),
                    severity="WARNING",
                    field="direction",
                )
            )

        # Score ranges
        for field_name in self.SCORE_ATTRIBUTES:

            if not hasattr(
                opportunity,
                field_name,
            ):
                continue

            value = self._number(
                getattr(
                    opportunity,
                    field_name,
                    None,
                )
            )

            if value is None:
                issues.append(
                    ScannerValidationIssue(
                        code="NON_NUMERIC_SCORE",
                        message=(
                            f"Field '{field_name}' "
                            "is not numeric."
                        ),
                        severity="ERROR",
                        field=field_name,
                    )
                )
                continue

            if value < 0.0 or value > 100.0:
                issues.append(
                    ScannerValidationIssue(
                        code="SCORE_OUT_OF_RANGE",
                        message=(
                            f"Field '{field_name}' "
                            "must be between 0 and 100."
                        ),
                        severity="ERROR",
                        field=field_name,
                    )
                )

        # Expected move
        if hasattr(
            opportunity,
            "expected_move_pct",
        ):

            expected_move = self._number(
                getattr(
                    opportunity,
                    "expected_move_pct",
                    None,
                )
            )

            if (
                expected_move is None
                or expected_move < 0.0
            ):
                issues.append(
                    ScannerValidationIssue(
                        code="INVALID_EXPECTED_MOVE",
                        message=(
                            "Expected move must be "
                            "a non-negative number."
                        ),
                        severity="WARNING",
                        field="expected_move_pct",
                    )
                )

        # Expected horizon
        if hasattr(
            opportunity,
            "expected_horizon_minutes",
        ):

            horizon = self._number(
                getattr(
                    opportunity,
                    "expected_horizon_minutes",
                    None,
                )
            )

            if (
                horizon is None
                or horizon < 0.0
            ):
                issues.append(
                    ScannerValidationIssue(
                        code="INVALID_HORIZON",
                        message=(
                            "Expected horizon must be "
                            "a non-negative number."
                        ),
                        severity="WARNING",
                        field=(
                            "expected_horizon_minutes"
                        ),
                    )
                )

        # Qualified opportunity must have actionable direction
        qualified = bool(
            getattr(
                opportunity,
                "qualified",
                False,
            )
        )

        if qualified and direction in {
            "UNKNOWN",
            "NEUTRAL",
        }:
            issues.append(
                ScannerValidationIssue(
                    code="QUALIFIED_WITHOUT_DIRECTION",
                    message=(
                        "Qualified opportunity has "
                        "no actionable direction."
                    ),
                    severity="ERROR",
                    field="direction",
                )
            )

        return issues

    # --------------------------------------------------------
    # Collection Validation
    # --------------------------------------------------------

    def validate_collection(
        self,
        opportunities: List[Any],
    ) -> List[ScannerValidationIssue]:

        issues: List[
            ScannerValidationIssue
        ] = []

        if opportunities is None:
            return [
                ScannerValidationIssue(
                    code="NULL_COLLECTION",
                    message=(
                        "Opportunity collection is None."
                    ),
                    severity="ERROR",
                )
            ]

        if not isinstance(
            opportunities,
            list,
        ):
            return [
                ScannerValidationIssue(
                    code="INVALID_COLLECTION",
                    message=(
                        "Opportunity collection "
                        "must be a list."
                    ),
                    severity="ERROR",
                )
            ]

        seen_instruments = set()

        for index, opportunity in enumerate(
            opportunities
        ):

            item_issues = (
                self.validate_opportunity(
                    opportunity
                )
            )

            for issue in item_issues:
                issue.metadata = (
                    getattr(
                        issue,
                        "metadata",
                        {},
                    )
                    if hasattr(
                        issue,
                        "metadata",
                    )
                    else {}
                )

                issue.metadata["index"] = index

                issues.append(issue)

            instrument = getattr(
                opportunity,
                "instrument",
                None,
            )

            if instrument:

                if instrument in seen_instruments:
                    issues.append(
                        ScannerValidationIssue(
                            code="DUPLICATE_INSTRUMENT",
                            message=(
                                f"Duplicate instrument "
                                f"'{instrument}' "
                                "found in scan."
                            ),
                            severity="WARNING",
                            field="instrument",
                        )
                    )

                seen_instruments.add(
                    instrument
                )

        return issues

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    def summarize(
        self,
        issues: List[
            ScannerValidationIssue
        ],
    ) -> Dict[str, Any]:

        errors = [
            issue
            for issue in issues
            if issue.severity.upper()
            == "ERROR"
        ]

        warnings = [
            issue
            for issue in issues
            if issue.severity.upper()
            == "WARNING"
        ]

        return {
            "validator_version": self.VERSION,
            "valid": len(errors) == 0,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "issue_count": len(issues),
            "errors": [
                issue.to_dict()
                for issue in errors
            ],
            "warnings": [
                issue.to_dict()
                for issue in warnings
            ],
        }


# ------------------------------------------------------------
# Scanner Audit Record
# ------------------------------------------------------------

@dataclass
class ScannerAuditRecord:
    """
    Audit information for one scanner cycle.
    """

    scan_id: str
    timestamp: Optional[str] = None

    model_version: str = "1.0.0"
    validator_version: str = "1.0.0"

    universe_size: int = 0
    scanned_count: int = 0
    qualified_count: int = 0
    rejected_count: int = 0

    top_ranked_instrument: Optional[str] = None
    top_ranked_score: float = 0.0
    top_ranked_grade: str = "NO_TRADE"

    validation_passed: bool = True
    validation_errors: int = 0
    validation_warnings: int = 0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "scan_id": self.scan_id,
            "timestamp": self.timestamp,
            "model_version": self.model_version,
            "validator_version": (
                self.validator_version
            ),
            "universe_size": self.universe_size,
            "scanned_count": self.scanned_count,
            "qualified_count": self.qualified_count,
            "rejected_count": self.rejected_count,
            "top_ranked_instrument": (
                self.top_ranked_instrument
            ),
            "top_ranked_score": (
                self.top_ranked_score
            ),
            "top_ranked_grade": (
                self.top_ranked_grade
            ),
            "validation_passed": (
                self.validation_passed
            ),
            "validation_errors": (
                self.validation_errors
            ),
            "validation_warnings": (
                self.validation_warnings
            ),
            "metadata": dict(self.metadata),
        }


# ------------------------------------------------------------
# Build Audit Record
# ------------------------------------------------------------

def build_scanner_audit_record(
    scan_id: str,
    opportunities: List[Any],
    timestamp: Optional[str] = None,
    universe_size: Optional[int] = None,
) -> ScannerAuditRecord:

    validator = ScannerModelValidator()

    issues = validator.validate_collection(
        opportunities
    )

    summary = validator.summarize(
        issues
    )

    qualified = [
        item
        for item in opportunities
        if bool(
            getattr(
                item,
                "qualified",
                False,
            )
        )
    ]

    ordered = sorted(
        qualified,
        key=lambda item: (
            float(
                getattr(
                    item,
                    "ranking_score",
                    0.0,
                )
                or 0.0
            ),
            float(
                getattr(
                    item,
                    "quality_score",
                    0.0,
                )
                or 0.0
            ),
        ),
        reverse=True,
    )

    top = (
        ordered[0]
        if ordered
        else None
    )

    if universe_size is None:
        universe_size = len(opportunities)

    return ScannerAuditRecord(
        scan_id=scan_id,
        timestamp=timestamp,
        universe_size=max(
            0,
            int(universe_size),
        ),
        scanned_count=len(
            opportunities
        ),
        qualified_count=len(
            qualified
        ),
        rejected_count=(
            len(opportunities)
            - len(qualified)
        ),
        top_ranked_instrument=(
            getattr(
                top,
                "instrument",
                None,
            )
            if top is not None
            else None
        ),
        top_ranked_score=(
            float(
                getattr(
                    top,
                    "ranking_score",
                    0.0,
                )
                or 0.0
            )
            if top is not None
            else 0.0
        ),
        top_ranked_grade=(
            str(
                getattr(
                    top,
                    "grade",
                    "NO_TRADE",
                )
            )
            if top is not None
            else "NO_TRADE"
        ),
        validation_passed=summary[
            "valid"
        ],
        validation_errors=summary[
            "error_count"
        ],
        validation_warnings=summary[
            "warning_count"
        ],
        metadata={
            "validation_summary": summary,
        },
    )


# ------------------------------------------------------------
# Complete Model Validation Helper
# ------------------------------------------------------------

def validate_scanner_models(
    opportunities: List[Any],
) -> Dict[str, Any]:

    validator = ScannerModelValidator()

    issues = validator.validate_collection(
        opportunities
    )

    return validator.summarize(
        issues
    )


# ------------------------------------------------------------
# Public API
# ------------------------------------------------------------

__all__ = [
    "ScannerValidationIssue",
    "ScannerModelValidator",
    "ScannerAuditRecord",
    "build_scanner_audit_record",
    "validate_scanner_models",
]