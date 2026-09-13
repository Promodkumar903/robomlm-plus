# ============================================================
# ROBOMLM
# OPPORTUNITY ENGINE — PART 1
# FOUNDATION / OPPORTUNITY EVIDENCE CONTRACT
# ============================================================

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


# ============================================================
# OUTPUT CONTRACT
# ============================================================

@dataclass
class OpportunityIntelligence:
    """
    Normalized output contract for Opportunity Engine.

    Opportunity Engine identifies and ranks the quality of a
    market opportunity.

    It does NOT make the final trading decision.
    """

    symbol: str

    opportunity_score: float

    structure_score: float
    accumulation_score: float
    distribution_score: float

    breakout_score: float
    confirmation_score: float

    directional_bias: str

    opportunity_grade: str

    confidence: float
    evidence_quality: float

    status: str

    calibration_status: str

    evidence: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# ENGINE
# ============================================================

class OpportunityEngine:
    """
    Opportunity Engine — Part 1.

    ROLE
    ----
    Convert upstream intelligence into a normalized
    opportunity-quality assessment.

    INPUT FLOW
    ----------
    Structure Engine
        ↓
    Accumulation Engine
        ↓
    Distribution Engine
        ↓
    Breakout Engine
        ↓
    Confirmation Engine
        ↓
    Opportunity Engine
        ↓
    D13

    AUTHORITY
    ---------
    Opportunity Engine:
        Opportunity discovery / ranking intelligence

    D13:
        Final decision authority

    IMPORTANT
    ---------
    This engine does NOT invent market formulas.
    Upstream engine outputs remain the source of evidence.
    """

    def __init__(
        self,
        minimum_evidence_quality: float = 50.0,
        minimum_opportunity_score: float = 60.0,
        high_opportunity_threshold: float = 80.0,
    ):
        self.minimum_evidence_quality = (
            minimum_evidence_quality
        )

        self.minimum_opportunity_score = (
            minimum_opportunity_score
        )

        self.high_opportunity_threshold = (
            high_opportunity_threshold
        )

    # ========================================================
    # PUBLIC API
    # ========================================================

    def evaluate(
        self,
        symbol: str,

        structure_data: Optional[Any] = None,
        accumulation_data: Optional[Any] = None,
        distribution_data: Optional[Any] = None,
        breakout_data: Optional[Any] = None,
        confirmation_data: Optional[Any] = None,
    ) -> OpportunityIntelligence:

        """
        Evaluate opportunity quality using upstream
        intelligence.

        No final BUY/SELL decision is generated here.
        """

        # ----------------------------------------------------
        # 1. EXTRACT STRUCTURE
        # ----------------------------------------------------

        structure_score = self._extract_score(
            structure_data,
            "structure_score",
            50.0
        )

        # ----------------------------------------------------
        # 2. EXTRACT ACCUMULATION
        # ----------------------------------------------------

        accumulation_score = self._extract_score(
            accumulation_data,
            "score",
            50.0
        )

        # ----------------------------------------------------
        # 3. EXTRACT DISTRIBUTION
        # ----------------------------------------------------

        distribution_score = self._extract_score(
            distribution_data,
            "score",
            50.0
        )

        # ----------------------------------------------------
        # 4. EXTRACT BREAKOUT INTELLIGENCE
        # ----------------------------------------------------

        breakout_score = self._extract_breakout_score(
            breakout_data
        )

        # ----------------------------------------------------
        # 5. EXTRACT CONFIRMATION
        # ----------------------------------------------------

        confirmation_score = (
            self._extract_confirmation_score(
                confirmation_data
            )
        )

        # ----------------------------------------------------
        # 6. DIRECTIONAL BIAS
        # ----------------------------------------------------

        directional_bias = (
            self._resolve_direction(
                breakout_data,
                confirmation_data
            )
        )

        # ----------------------------------------------------
        # 7. EVIDENCE QUALITY
        # ----------------------------------------------------

        evidence_quality = (
            self._calculate_evidence_quality(
                structure_score=structure_score,
                accumulation_score=accumulation_score,
                distribution_score=distribution_score,
                breakout_score=breakout_score,
                confirmation_score=confirmation_score,
            )
        )

        # ----------------------------------------------------
        # 8. OPPORTUNITY SCORE
        # ----------------------------------------------------

        opportunity_score = (
            self._calculate_opportunity_score(
                structure_score=structure_score,
                accumulation_score=accumulation_score,
                distribution_score=distribution_score,
                breakout_score=breakout_score,
                confirmation_score=confirmation_score,
            )
        )

        # ----------------------------------------------------
        # 9. GRADE
        # ----------------------------------------------------

        opportunity_grade = (
            self._calculate_grade(
                opportunity_score
            )
        )

        # ----------------------------------------------------
        # 10. STATUS
        # ----------------------------------------------------

        status = self._resolve_status(
            opportunity_score=opportunity_score,
            evidence_quality=evidence_quality,
        )

        # ----------------------------------------------------
        # 11. CONFIDENCE
        # ----------------------------------------------------

        confidence = self._calculate_confidence(
            opportunity_score=opportunity_score,
            evidence_quality=evidence_quality,
        )

        # ----------------------------------------------------
        # 12. EVIDENCE
        # ----------------------------------------------------

        evidence = {
            "structure_score": structure_score,
            "accumulation_score": accumulation_score,
            "distribution_score": distribution_score,
            "breakout_score": breakout_score,
            "confirmation_score": confirmation_score,

            "directional_bias": directional_bias,

            "opportunity_score": opportunity_score,
            "opportunity_grade": opportunity_grade,

            "formula_status": "PROVISIONAL",
            "calibration_status": "UNCALIBRATED",

            "role": "OPPORTUNITY_DISCOVERY",
            "decision_authority": "D13",
        }

        return OpportunityIntelligence(
            symbol=symbol,

            opportunity_score=opportunity_score,

            structure_score=structure_score,
            accumulation_score=accumulation_score,
            distribution_score=distribution_score,

            breakout_score=breakout_score,
            confirmation_score=confirmation_score,

            directional_bias=directional_bias,

            opportunity_grade=opportunity_grade,

            confidence=confidence,
            evidence_quality=evidence_quality,

            status=status,

            calibration_status="UNCALIBRATED",

            evidence=evidence,
        )

    # ========================================================
    # SCORE EXTRACTION
    # ========================================================

    def _extract_score(
        self,
        data: Optional[Any],
        attribute: str,
        default: float = 50.0,
    ) -> float:

        if data is None:
            return default

        value = getattr(
            data,
            attribute,
            default
        )

        return self._clip(value)

    # ========================================================
    # BREAKOUT SCORE
    # ========================================================

    def _extract_breakout_score(
        self,
        breakout_data: Optional[Any],
    ) -> float:

        if breakout_data is None:
            return 50.0

        # Preferred field
        value = getattr(
            breakout_data,
            "risk_adjusted_breakout_score",
            None
        )

        if value is not None:
            return self._clip(value)

        # Secondary field
        value = getattr(
            breakout_data,
            "breakout_probability",
            None
        )

        if value is not None:
            return self._clip(value)

        # Foundation readiness
        value = getattr(
            breakout_data,
            "breakout_readiness",
            None
        )

        if value is not None:
            return self._clip(value)

        return 50.0

    # ========================================================
    # CONFIRMATION SCORE
    # ========================================================

    def _extract_confirmation_score(
        self,
        confirmation_data: Optional[Any],
    ) -> float:

        if confirmation_data is None:
            return 50.0

        # Part-5 preferred output
        value = getattr(
            confirmation_data,
            "risk_adjusted_confirmation_score",
            None
        )

        if value is not None:
            return self._clip(value)

        # Part-4 output
        value = getattr(
            confirmation_data,
            "confirmation_score",
            None
        )

        if value is not None:
            return self._clip(value)

        # Part-3 output
        value = getattr(
            confirmation_data,
            "acceptance_confirmation_score",
            None
        )

        if value is not None:
            return self._clip(value)

        return 50.0

    # ========================================================
    # DIRECTION
    # ========================================================

    def _resolve_direction(
        self,
        breakout_data: Optional[Any],
        confirmation_data: Optional[Any],
    ) -> str:

        # Confirmation has priority because it represents
        # later-stage evidence.

        if confirmation_data is not None:

            value = getattr(
                confirmation_data,
                "direction",
                None
            )

            if value in (
                "BULLISH",
                "BEARISH",
            ):
                return value

            value = getattr(
                confirmation_data,
                "confirmed_direction",
                None
            )

            if value in (
                "BULLISH",
                "BEARISH",
            ):
                return value

        if breakout_data is not None:

            value = getattr(
                breakout_data,
                "breakout_direction",
                None
            )

            if value in (
                "BULLISH",
                "BEARISH",
            ):
                return value

            value = getattr(
                breakout_data,
                "direction_bias",
                None
            )

            if value in (
                "BULLISH",
                "BEARISH",
            ):
                return value

        return "UNKNOWN"

    # ========================================================
    # EVIDENCE QUALITY
    # ========================================================

    def _calculate_evidence_quality(
        self,
        structure_score: float,
        accumulation_score: float,
        distribution_score: float,
        breakout_score: float,
        confirmation_score: float,
    ) -> float:

        # Distribution is treated as inverse opportunity
        # evidence in this foundation layer.

        distribution_quality = (
            100.0 - distribution_score
        )

        quality = (
            structure_score * 0.25
            + accumulation_score * 0.20
            + distribution_quality * 0.15
            + breakout_score * 0.20
            + confirmation_score * 0.20
        )

        return self._clip(quality)

    # ========================================================
    # OPPORTUNITY SCORE
    # ========================================================

    def _calculate_opportunity_score(
        self,
        structure_score: float,
        accumulation_score: float,
        distribution_score: float,
        breakout_score: float,
        confirmation_score: float,
    ) -> float:

        distribution_quality = (
            100.0 - distribution_score
        )

        score = (
            structure_score * 0.25
            + accumulation_score * 0.20
            + distribution_quality * 0.15
            + breakout_score * 0.20
            + confirmation_score * 0.20
        )

        return self._clip(score)

    # ========================================================
    # GRADE
    # ========================================================

    def _calculate_grade(
        self,
        opportunity_score: float,
    ) -> str:

        if opportunity_score >= 90.0:
            return "A+"

        if opportunity_score >= 80.0:
            return "A"

        if opportunity_score >= 70.0:
            return "B"

        if opportunity_score >= 60.0:
            return "C"

        return "D"

    # ========================================================
    # STATUS
    # ========================================================

    def _resolve_status(
        self,
        opportunity_score: float,
        evidence_quality: float,
    ) -> str:

        if evidence_quality < self.minimum_evidence_quality:
            return "INSUFFICIENT_EVIDENCE"

        if opportunity_score >= self.high_opportunity_threshold:
            return "HIGH_QUALITY_OPPORTUNITY"

        if opportunity_score >= self.minimum_opportunity_score:
            return "OPPORTUNITY_BUILDING"

        return "LOW_QUALITY_OPPORTUNITY"

    # ========================================================
    # CONFIDENCE
    # ========================================================

    def _calculate_confidence(
        self,
        opportunity_score: float,
        evidence_quality: float,
    ) -> float:

        confidence = (
            opportunity_score * 0.55
            + evidence_quality * 0.45
        )

        return self._clip(confidence)

    # ========================================================
    # CLIP
    # ========================================================

    @staticmethod
    def _clip(
        value: float,
        lower: float = 0.0,
        upper: float = 100.0,
    ) -> float:

        try:
            value = float(value)
        except (
            TypeError,
            ValueError,
        ):
            return lower

        return max(
            lower,
            min(upper, value)
        )
    # ========================================================
    # OPPORTUNITY QUALITY DECOMPOSITION
    # PART-2
    # ========================================================

    def evaluate_quality_components(
        self,
        structure_data: Optional[Any] = None,
        accumulation_data: Optional[Any] = None,
        distribution_data: Optional[Any] = None,
        breakout_data: Optional[Any] = None,
        confirmation_data: Optional[Any] = None,
    ) -> Dict[str, Any]:

        """
        Decompose opportunity quality into independent
        evidence components.

        This method does not create a final BUY/SELL decision.
        """

        # ----------------------------------------------------
        # 1. STRUCTURE QUALITY
        # ----------------------------------------------------

        structure_quality = self._extract_structure_quality(
            structure_data
        )

        # ----------------------------------------------------
        # 2. ACCUMULATION QUALITY
        # ----------------------------------------------------

        accumulation_quality = self._extract_accumulation_quality(
            accumulation_data
        )

        # ----------------------------------------------------
        # 3. DISTRIBUTION RISK
        # ----------------------------------------------------

        distribution_risk = self._extract_distribution_risk(
            distribution_data
        )

        # ----------------------------------------------------
        # 4. BREAKOUT QUALITY
        # ----------------------------------------------------

        breakout_quality = self._extract_breakout_quality(
            breakout_data
        )

        # ----------------------------------------------------
        # 5. CONFIRMATION QUALITY
        # ----------------------------------------------------

        confirmation_quality = (
            self._extract_confirmation_quality(
                confirmation_data
            )
        )

        # ----------------------------------------------------
        # 6. RISK-ADJUSTED QUALITY
        # ----------------------------------------------------

        risk_adjusted_quality = (
            self._calculate_risk_adjusted_quality(
                breakout_quality=breakout_quality,
                confirmation_quality=confirmation_quality,
                distribution_risk=distribution_risk,
            )
        )

        # ----------------------------------------------------
        # 7. STRUCTURAL ALIGNMENT
        # ----------------------------------------------------

        structural_alignment = (
            self._calculate_structural_alignment(
                structure_quality=structure_quality,
                accumulation_quality=accumulation_quality,
                distribution_risk=distribution_risk,
            )
        )

        # ----------------------------------------------------
        # 8. CONFIRMATION ALIGNMENT
        # ----------------------------------------------------

        confirmation_alignment = (
            self._calculate_confirmation_alignment(
                breakout_quality=breakout_quality,
                confirmation_quality=confirmation_quality,
            )
        )

        # ----------------------------------------------------
        # 9. OVERALL QUALITY
        # ----------------------------------------------------

        overall_quality = (
            structure_quality * 0.20
            + accumulation_quality * 0.15
            + (100.0 - distribution_risk) * 0.15
            + breakout_quality * 0.25
            + confirmation_quality * 0.25
        )

        overall_quality = self._clip(
            overall_quality
        )

        return {
            "structure_quality": structure_quality,
            "accumulation_quality": accumulation_quality,
            "distribution_risk": distribution_risk,
            "breakout_quality": breakout_quality,
            "confirmation_quality": confirmation_quality,

            "risk_adjusted_quality":
                risk_adjusted_quality,

            "structural_alignment":
                structural_alignment,

            "confirmation_alignment":
                confirmation_alignment,

            "overall_quality":
                overall_quality,

            "formula_status":
                "PROVISIONAL",

            "decision_authority":
                "D13",
        }


    # ========================================================
    # STRUCTURE QUALITY
    # ========================================================

    def _extract_structure_quality(
        self,
        structure_data: Optional[Any],
    ) -> float:

        if structure_data is None:
            return 50.0

        # Preferred explicit structure score.
        value = getattr(
            structure_data,
            "structure_score",
            None
        )

        if value is not None:
            return self._clip(value)

        # Consolidation can act as a structural input,
        # but is not equivalent to final structure quality.
        value = getattr(
            structure_data,
            "consolidation_score",
            None
        )

        if value is not None:
            return self._clip(value)

        value = getattr(
            structure_data,
            "quality",
            None
        )

        if value is not None:
            return self._clip(value)

        return 50.0


    # ========================================================
    # ACCUMULATION QUALITY
    # ========================================================

    def _extract_accumulation_quality(
        self,
        accumulation_data: Optional[Any],
    ) -> float:

        if accumulation_data is None:
            return 50.0

        value = getattr(
            accumulation_data,
            "score",
            None
        )

        if value is not None:
            return self._clip(value)

        value = getattr(
            accumulation_data,
            "accumulation_score",
            None
        )

        if value is not None:
            return self._clip(value)

        value = getattr(
            accumulation_data,
            "quality",
            None
        )

        if value is not None:
            return self._clip(value)

        return 50.0


    # ========================================================
    # DISTRIBUTION RISK
    # ========================================================

    def _extract_distribution_risk(
        self,
        distribution_data: Optional[Any],
    ) -> float:

        if distribution_data is None:
            return 50.0

        value = getattr(
            distribution_data,
            "score",
            None
        )

        if value is not None:
            return self._clip(value)

        value = getattr(
            distribution_data,
            "distribution_score",
            None
        )

        if value is not None:
            return self._clip(value)

        value = getattr(
            distribution_data,
            "risk_score",
            None
        )

        if value is not None:
            return self._clip(value)

        return 50.0


    # ========================================================
    # BREAKOUT QUALITY
    # ========================================================

    def _extract_breakout_quality(
        self,
        breakout_data: Optional[Any],
    ) -> float:

        if breakout_data is None:
            return 50.0

        # Highest priority:
        # risk-adjusted breakout intelligence.
        value = getattr(
            breakout_data,
            "risk_adjusted_breakout_score",
            None
        )

        if value is not None:
            return self._clip(value)

        # Opportunity-level breakout score.
        value = getattr(
            breakout_data,
            "profit_conversion_score",
            None
        )

        if value is not None:
            return self._clip(value)

        # Raw breakout probability.
        value = getattr(
            breakout_data,
            "breakout_probability",
            None
        )

        if value is not None:
            return self._clip(value)

        # Readiness is weaker evidence than probability.
        value = getattr(
            breakout_data,
            "breakout_readiness",
            None
        )

        if value is not None:
            return self._clip(value)

        return 50.0


    # ========================================================
    # CONFIRMATION QUALITY
    # ========================================================

    def _extract_confirmation_quality(
        self,
        confirmation_data: Optional[Any],
    ) -> float:

        if confirmation_data is None:
            return 50.0

        # Part-5
        value = getattr(
            confirmation_data,
            "risk_adjusted_confirmation_score",
            None
        )

        if value is not None:
            return self._clip(value)

        # Part-4
        value = getattr(
            confirmation_data,
            "confirmation_score",
            None
        )

        if value is not None:
            return self._clip(value)

        # Part-3
        value = getattr(
            confirmation_data,
            "acceptance_confirmation_score",
            None
        )

        if value is not None:
            return self._clip(value)

        # Foundation
        value = getattr(
            confirmation_data,
            "confirmation_readiness",
            None
        )

        if value is not None:
            return self._clip(value)

        return 50.0


    # ========================================================
    # RISK-ADJUSTED QUALITY
    # ========================================================

    def _calculate_risk_adjusted_quality(
        self,
        breakout_quality: float,
        confirmation_quality: float,
        distribution_risk: float,
    ) -> float:

        base_quality = (
            breakout_quality * 0.50
            + confirmation_quality * 0.50
        )

        # Distribution acts as a quality penalty.
        risk_factor = (
            1.0 - distribution_risk / 100.0
        )

        adjusted_quality = (
            base_quality * risk_factor
        )

        return self._clip(
            adjusted_quality
        )


    # ========================================================
    # STRUCTURAL ALIGNMENT
    # ========================================================

    def _calculate_structural_alignment(
        self,
        structure_quality: float,
        accumulation_quality: float,
        distribution_risk: float,
    ) -> float:

        distribution_quality = (
            100.0 - distribution_risk
        )

        alignment = (
            structure_quality * 0.40
            + accumulation_quality * 0.35
            + distribution_quality * 0.25
        )

        return self._clip(
            alignment
        )


    # ========================================================
    # CONFIRMATION ALIGNMENT
    # ========================================================

    def _calculate_confirmation_alignment(
        self,
        breakout_quality: float,
        confirmation_quality: float,
    ) -> float:

        # Difference between breakout expectation and
        # confirmation evidence is itself useful information.

        disagreement = abs(
            breakout_quality
            - confirmation_quality
        )

        alignment = (
            100.0 - disagreement
        )

        return self._clip(
            alignment
        )
    # ========================================================
    # OPPORTUNITY ENGINE — PART 3
    # DIRECTION + CONFLICT + EVIDENCE ALIGNMENT
    # ========================================================

    def evaluate_direction_intelligence(
        self,
        breakout_data: Optional[Any] = None,
        confirmation_data: Optional[Any] = None,
        accumulation_data: Optional[Any] = None,
        distribution_data: Optional[Any] = None,
    ) -> Dict[str, Any]:

        """
        Evaluate directional evidence alignment.

        This is opportunity intelligence only.
        It does NOT create a final BUY/SELL decision.
        """

        # ----------------------------------------------------
        # 1. BREAKOUT DIRECTION
        # ----------------------------------------------------

        breakout_direction = (
            self._extract_direction(
                breakout_data
            )
        )

        # ----------------------------------------------------
        # 2. CONFIRMATION DIRECTION
        # ----------------------------------------------------

        confirmation_direction = (
            self._extract_direction(
                confirmation_data
            )
        )

        # ----------------------------------------------------
        # 3. ACCUMULATION / DISTRIBUTION BIAS
        # ----------------------------------------------------

        accumulation_score = (
            self._extract_score(
                accumulation_data,
                "score",
                50.0
            )
        )

        distribution_score = (
            self._extract_score(
                distribution_data,
                "score",
                50.0
            )
        )

        pressure_bias = (
            self._calculate_pressure_bias(
                accumulation_score,
                distribution_score
            )
        )

        # ----------------------------------------------------
        # 4. DIRECTION AGREEMENT
        # ----------------------------------------------------

        direction_agreement = (
            self._calculate_direction_agreement(
                breakout_direction,
                confirmation_direction,
                pressure_bias
            )
        )

        # ----------------------------------------------------
        # 5. CONFLICT DETECTION
        # ----------------------------------------------------

        conflict_score = (
            self._calculate_direction_conflict(
                breakout_direction,
                confirmation_direction,
                pressure_bias
            )
        )

        # ----------------------------------------------------
        # 6. FINAL OPPORTUNITY BIAS
        # ----------------------------------------------------

        opportunity_bias = (
            self._resolve_opportunity_bias(
                breakout_direction,
                confirmation_direction,
                pressure_bias,
                direction_agreement,
                conflict_score
            )
        )

        # ----------------------------------------------------
        # 7. DIRECTION CONFIDENCE
        # ----------------------------------------------------

        direction_confidence = (
            self._calculate_direction_confidence(
                direction_agreement,
                conflict_score,
                opportunity_bias
            )
        )

        return {
            "breakout_direction": breakout_direction,
            "confirmation_direction": confirmation_direction,

            "accumulation_score": accumulation_score,
            "distribution_score": distribution_score,

            "pressure_bias": pressure_bias,

            "direction_agreement": direction_agreement,
            "direction_conflict": conflict_score,

            "opportunity_bias": opportunity_bias,
            "direction_confidence": direction_confidence,

            "formula_status": "PROVISIONAL",
            "decision_authority": "D13",
        }


    # ========================================================
    # DIRECTION EXTRACTION
    # ========================================================

    def _extract_direction(
        self,
        data: Optional[Any],
    ) -> str:

        if data is None:
            return "UNKNOWN"

        possible_fields = [
            "opportunity_direction",
            "confirmed_direction",
            "breakout_direction",
            "direction_bias",
            "direction",
        ]

        for field_name in possible_fields:

            value = getattr(
                data,
                field_name,
                None
            )

            if value is None:
                continue

            value = str(value).upper()

            if value in (
                "BULLISH",
                "BEARISH",
            ):
                return value

        return "UNKNOWN"


    # ========================================================
    # PRESSURE BIAS
    # ========================================================

    def _calculate_pressure_bias(
        self,
        accumulation_score: float,
        distribution_score: float,
    ) -> str:

        difference = (
            accumulation_score
            - distribution_score
        )

        if difference > 10.0:
            return "BULLISH"

        if difference < -10.0:
            return "BEARISH"

        return "BALANCED"


    # ========================================================
    # DIRECTION AGREEMENT
    # ========================================================

    def _calculate_direction_agreement(
        self,
        breakout_direction: str,
        confirmation_direction: str,
        pressure_bias: str,
    ) -> float:

        directions = [
            breakout_direction,
            confirmation_direction,
            pressure_bias,
        ]

        valid = [
            d for d in directions
            if d in (
                "BULLISH",
                "BEARISH",
            )
        ]

        if not valid:
            return 0.0

        bullish_count = valid.count(
            "BULLISH"
        )

        bearish_count = valid.count(
            "BEARISH"
        )

        total = len(valid)

        majority = max(
            bullish_count,
            bearish_count
        )

        agreement = (
            majority / total
        ) * 100.0

        return self._clip(
            agreement
        )


    # ========================================================
    # DIRECTION CONFLICT
    # ========================================================

    def _calculate_direction_conflict(
        self,
        breakout_direction: str,
        confirmation_direction: str,
        pressure_bias: str,
    ) -> float:

        directions = [
            breakout_direction,
            confirmation_direction,
            pressure_bias,
        ]

        valid = [
            d for d in directions
            if d in (
                "BULLISH",
                "BEARISH",
            )
        ]

        if len(valid) < 2:
            return 0.0

        bullish_count = valid.count(
            "BULLISH"
        )

        bearish_count = valid.count(
            "BEARISH"
        )

        # Both sides represented.
        if (
            bullish_count > 0
            and bearish_count > 0
        ):

            minority = min(
                bullish_count,
                bearish_count
            )

            conflict = (
                minority / len(valid)
            ) * 100.0

            return self._clip(
                conflict * 2.0
            )

        return 0.0


    # ========================================================
    # OPPORTUNITY BIAS
    # ========================================================

    def _resolve_opportunity_bias(
        self,
        breakout_direction: str,
        confirmation_direction: str,
        pressure_bias: str,
        direction_agreement: float,
        conflict_score: float,
    ) -> str:

        # Strong conflict means no forced direction.
        if conflict_score >= 50.0:
            return "CONFLICTED"

        candidates = [
            breakout_direction,
            confirmation_direction,
            pressure_bias,
        ]

        bullish = candidates.count(
            "BULLISH"
        )

        bearish = candidates.count(
            "BEARISH"
        )

        if (
            bullish == 0
            and bearish == 0
        ):
            return "UNKNOWN"

        if bullish > bearish:
            if direction_agreement >= 66.0:
                return "BULLISH"

            return "BULLISH_WEAK"

        if bearish > bullish:
            if direction_agreement >= 66.0:
                return "BEARISH"

            return "BEARISH_WEAK"

        return "BALANCED"


    # ========================================================
    # DIRECTION CONFIDENCE
    # ========================================================

    def _calculate_direction_confidence(
        self,
        direction_agreement: float,
        conflict_score: float,
        opportunity_bias: str,
    ) -> float:

        confidence = (
            direction_agreement * 0.70
            + (100.0 - conflict_score) * 0.30
        )

        if opportunity_bias in (
            "UNKNOWN",
            "CONFLICTED",
            "BALANCED",
        ):
            confidence *= 0.70

        return self._clip(
            confidence
        )
    # ========================================================
    # OPPORTUNITY ENGINE — PART 4
    # STRENGTH + QUALITY GATES
    # ========================================================

    def evaluate_strength(
        self,
        quality_components: Optional[Dict[str, Any]] = None,
        direction_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        """
        Evaluate opportunity strength and evidence gates.

        This layer prevents a single strong component from
        automatically turning an opportunity into a high-quality
        opportunity.

        Final decision remains with D13.
        """

        if quality_components is None:
            quality_components = {}

        if direction_data is None:
            direction_data = {}

        # ----------------------------------------------------
        # 1. COMPONENT EXTRACTION
        # ----------------------------------------------------

        structure_quality = self._clip(
            quality_components.get(
                "structure_quality",
                50.0
            )
        )

        accumulation_quality = self._clip(
            quality_components.get(
                "accumulation_quality",
                50.0
            )
        )

        distribution_risk = self._clip(
            quality_components.get(
                "distribution_risk",
                50.0
            )
        )

        breakout_quality = self._clip(
            quality_components.get(
                "breakout_quality",
                50.0
            )
        )

        confirmation_quality = self._clip(
            quality_components.get(
                "confirmation_quality",
                50.0
            )
        )

        risk_adjusted_quality = self._clip(
            quality_components.get(
                "risk_adjusted_quality",
                50.0
            )
        )

        structural_alignment = self._clip(
            quality_components.get(
                "structural_alignment",
                50.0
            )
        )

        confirmation_alignment = self._clip(
            quality_components.get(
                "confirmation_alignment",
                50.0
            )
        )

        direction_agreement = self._clip(
            direction_data.get(
                "direction_agreement",
                50.0
            )
        )

        direction_conflict = self._clip(
            direction_data.get(
                "direction_conflict",
                0.0
            )
        )

        opportunity_bias = direction_data.get(
            "opportunity_bias",
            "UNKNOWN"
        )

        # ----------------------------------------------------
        # 2. CORE STRENGTH
        # ----------------------------------------------------

        core_strength = (
            structure_quality * 0.20
            + accumulation_quality * 0.15
            + (100.0 - distribution_risk) * 0.15
            + breakout_quality * 0.20
            + confirmation_quality * 0.20
            + risk_adjusted_quality * 0.10
        )

        core_strength = self._clip(
            core_strength
        )

        # ----------------------------------------------------
        # 3. ALIGNMENT STRENGTH
        # ----------------------------------------------------

        alignment_strength = (
            structural_alignment * 0.40
            + confirmation_alignment * 0.30
            + direction_agreement * 0.30
        )

        alignment_strength = self._clip(
            alignment_strength
        )

        # ----------------------------------------------------
        # 4. CONFLICT PENALTY
        # ----------------------------------------------------

        conflict_penalty = (
            direction_conflict * 0.50
        )

        # ----------------------------------------------------
        # 5. FINAL STRENGTH
        # ----------------------------------------------------

        opportunity_strength = (
            core_strength * 0.65
            + alignment_strength * 0.35
            - conflict_penalty
        )

        opportunity_strength = self._clip(
            opportunity_strength
        )

        # ----------------------------------------------------
        # 6. WEAK COMPONENT DETECTION
        # ----------------------------------------------------

        weak_components = (
            self._detect_weak_components(
                structure_quality=structure_quality,
                accumulation_quality=accumulation_quality,
                breakout_quality=breakout_quality,
                confirmation_quality=confirmation_quality,
                structural_alignment=structural_alignment,
                confirmation_alignment=confirmation_alignment,
            )
        )

        # ----------------------------------------------------
        # 7. EVIDENCE GATE
        # ----------------------------------------------------

        evidence_gate = (
            self._evaluate_evidence_gate(
                structure_quality=structure_quality,
                breakout_quality=breakout_quality,
                confirmation_quality=confirmation_quality,
                direction_agreement=direction_agreement,
                direction_conflict=direction_conflict,
            )
        )

        # ----------------------------------------------------
        # 8. QUALITY GATE
        # ----------------------------------------------------

        quality_gate = (
            self._evaluate_quality_gate(
                opportunity_strength=opportunity_strength,
                evidence_gate=evidence_gate,
                weak_components=weak_components,
                opportunity_bias=opportunity_bias,
            )
        )

        # ----------------------------------------------------
        # 9. STRENGTH STATE
        # ----------------------------------------------------

        strength_state = (
            self._resolve_strength_state(
                opportunity_strength=opportunity_strength,
                evidence_gate=evidence_gate,
                quality_gate=quality_gate,
                direction_conflict=direction_conflict,
            )
        )

        # ----------------------------------------------------
        # 10. STRENGTH CONFIDENCE
        # ----------------------------------------------------

        strength_confidence = (
            self._calculate_strength_confidence(
                opportunity_strength=opportunity_strength,
                alignment_strength=alignment_strength,
                evidence_gate=evidence_gate,
            )
        )

        return {
            "core_strength": core_strength,
            "alignment_strength": alignment_strength,

            "opportunity_strength":
                opportunity_strength,

            "weak_components":
                weak_components,

            "evidence_gate":
                evidence_gate,

            "quality_gate":
                quality_gate,

            "strength_state":
                strength_state,

            "strength_confidence":
                strength_confidence,

            "direction_conflict":
                direction_conflict,

            "opportunity_bias":
                opportunity_bias,

            "formula_status":
                "PROVISIONAL",

            "decision_authority":
                "D13",
        }


    # ========================================================
    # WEAK COMPONENT DETECTION
    # ========================================================

    def _detect_weak_components(
        self,
        structure_quality: float,
        accumulation_quality: float,
        breakout_quality: float,
        confirmation_quality: float,
        structural_alignment: float,
        confirmation_alignment: float,
    ) -> list:

        components = {
            "structure": structure_quality,
            "accumulation": accumulation_quality,
            "breakout": breakout_quality,
            "confirmation": confirmation_quality,
            "structural_alignment":
                structural_alignment,
            "confirmation_alignment":
                confirmation_alignment,
        }

        weak = []

        for name, value in components.items():

            if value < 40.0:
                weak.append(name)

        return weak


    # ========================================================
    # EVIDENCE GATE
    # ========================================================

    def _evaluate_evidence_gate(
        self,
        structure_quality: float,
        breakout_quality: float,
        confirmation_quality: float,
        direction_agreement: float,
        direction_conflict: float,
    ) -> str:

        # Critical evidence missing or too weak.
        if (
            structure_quality < 30.0
            or breakout_quality < 30.0
        ):
            return "FAIL"

        # Strong directional conflict.
        if direction_conflict >= 70.0:
            return "FAIL"

        # Confirmation is too weak to support
        # a mature opportunity.
        if confirmation_quality < 35.0:
            return "WEAK"

        # Direction is unresolved.
        if direction_agreement < 40.0:
            return "WEAK"

        if (
            structure_quality >= 60.0
            and breakout_quality >= 60.0
            and confirmation_quality >= 60.0
            and direction_agreement >= 60.0
        ):
            return "PASS"

        return "PARTIAL"


    # ========================================================
    # QUALITY GATE
    # ========================================================

    def _evaluate_quality_gate(
        self,
        opportunity_strength: float,
        evidence_gate: str,
        weak_components: list,
        opportunity_bias: str,
    ) -> str:

        if evidence_gate == "FAIL":
            return "FAIL"

        if opportunity_bias in (
            "UNKNOWN",
            "CONFLICTED",
        ):
            return "FAIL"

        if len(weak_components) >= 3:
            return "FAIL"

        if (
            opportunity_strength >= 80.0
            and evidence_gate == "PASS"
            and len(weak_components) == 0
        ):
            return "PASS"

        if opportunity_strength >= 60.0:
            return "PARTIAL"

        return "FAIL"


    # ========================================================
    # STRENGTH STATE
    # ========================================================

    def _resolve_strength_state(
        self,
        opportunity_strength: float,
        evidence_gate: str,
        quality_gate: str,
        direction_conflict: float,
    ) -> str:

        if evidence_gate == "FAIL":
            return "INSUFFICIENT_OPPORTUNITY_EVIDENCE"

        if direction_conflict >= 70.0:
            return "DIRECTION_CONFLICT"

        if quality_gate == "FAIL":
            return "LOW_QUALITY"

        if (
            opportunity_strength >= 80.0
            and quality_gate == "PASS"
        ):
            return "HIGH_STRENGTH"

        if (
            opportunity_strength >= 60.0
            and quality_gate in (
                "PASS",
                "PARTIAL",
            )
        ):
            return "MODERATE_STRENGTH"

        return "WEAK_STRENGTH"


    # ========================================================
    # STRENGTH CONFIDENCE
    # ========================================================

    def _calculate_strength_confidence(
        self,
        opportunity_strength: float,
        alignment_strength: float,
        evidence_gate: str,
    ) -> float:

        confidence = (
            opportunity_strength * 0.55
            + alignment_strength * 0.45
        )

        if evidence_gate == "FAIL":
            confidence *= 0.50

        elif evidence_gate == "WEAK":
            confidence *= 0.75

        elif evidence_gate == "PARTIAL":
            confidence *= 0.90

        return self._clip(
            confidence
        )
    # ========================================================
    # OPPORTUNITY ENGINE — PART 5
    # RANKING + GRADE + PROFIT CONVERSION
    # ========================================================

    def evaluate_ranking(
        self,
        strength_data: Optional[Dict[str, Any]] = None,
        quality_data: Optional[Dict[str, Any]] = None,
        direction_data: Optional[Dict[str, Any]] = None,
        symbol: str = "UNKNOWN",
    ) -> Dict[str, Any]:

        """
        Rank opportunity quality.

        Ranking is for opportunity discovery only.
        It does NOT authorize trade execution.
        """

        strength_data = (
            strength_data or {}
        )

        quality_data = (
            quality_data or {}
        )

        direction_data = (
            direction_data or {}
        )

        # ----------------------------------------------------
        # 1. CORE INPUTS
        # ----------------------------------------------------

        opportunity_strength = self._clip(
            strength_data.get(
                "opportunity_strength",
                50.0
            )
        )

        strength_confidence = self._clip(
            strength_data.get(
                "strength_confidence",
                50.0
            )
        )

        quality_score = self._clip(
            quality_data.get(
                "overall_quality",
                50.0
            )
        )

        risk_adjusted_quality = self._clip(
            quality_data.get(
                "risk_adjusted_quality",
                50.0
            )
        )

        direction_agreement = self._clip(
            direction_data.get(
                "direction_agreement",
                50.0
            )
        )

        direction_conflict = self._clip(
            direction_data.get(
                "direction_conflict",
                0.0
            )
        )

        direction_confidence = self._clip(
            direction_data.get(
                "direction_confidence",
                50.0
            )
        )

        opportunity_bias = direction_data.get(
            "opportunity_bias",
            "UNKNOWN"
        )

        evidence_gate = strength_data.get(
            "evidence_gate",
            "FAIL"
        )

        quality_gate = strength_data.get(
            "quality_gate",
            "FAIL"
        )

        strength_state = strength_data.get(
            "strength_state",
            "WEAK_STRENGTH"
        )

        # ----------------------------------------------------
        # 2. RANKING SCORE
        # ----------------------------------------------------

        ranking_score = (
            opportunity_strength * 0.30
            + quality_score * 0.25
            + risk_adjusted_quality * 0.20
            + direction_agreement * 0.10
            + strength_confidence * 0.10
            + direction_confidence * 0.05
        )

        # Conflict penalty.
        ranking_score -= (
            direction_conflict * 0.20
        )

        ranking_score = self._clip(
            ranking_score
        )

        # ----------------------------------------------------
        # 3. PROFIT CONVERSION READINESS
        # ----------------------------------------------------

        profit_conversion = (
            opportunity_strength * 0.30
            + risk_adjusted_quality * 0.30
            + quality_score * 0.20
            + direction_agreement * 0.10
            + strength_confidence * 0.10
        )

        profit_conversion = self._clip(
            profit_conversion
        )

        # ----------------------------------------------------
        # 4. OPPORTUNITY GRADE
        # ----------------------------------------------------

        opportunity_grade = (
            self._resolve_opportunity_grade(
                ranking_score,
                evidence_gate,
                quality_gate,
                direction_conflict,
            )
        )

        # ----------------------------------------------------
        # 5. RANKING STATE
        # ----------------------------------------------------

        ranking_state = (
            self._resolve_ranking_state(
                ranking_score,
                profit_conversion,
                opportunity_grade,
                opportunity_bias,
            )
        )

        # ----------------------------------------------------
        # 6. RANKING CONFIDENCE
        # ----------------------------------------------------

        ranking_confidence = (
            self._calculate_ranking_confidence(
                ranking_score,
                profit_conversion,
                strength_confidence,
                direction_conflict,
            )
        )

        # ----------------------------------------------------
        # 7. OPPORTUNITY PRIORITY
        # ----------------------------------------------------

        priority = (
            self._resolve_priority(
                ranking_score,
                opportunity_grade,
                ranking_state,
            )
        )

        return {
            "symbol": symbol,

            "ranking_score":
                ranking_score,

            "profit_conversion_score":
                profit_conversion,

            "opportunity_grade":
                opportunity_grade,

            "ranking_state":
                ranking_state,

            "ranking_confidence":
                ranking_confidence,

            "priority":
                priority,

            "opportunity_bias":
                opportunity_bias,

            "direction_conflict":
                direction_conflict,

            "formula_status":
                "PROVISIONAL",

            "calibration_status":
                "UNCALIBRATED",

            "role":
                "OPPORTUNITY_DISCOVERY",

            "decision_authority":
                "D13",
        }


    # ========================================================
    # OPPORTUNITY GRADE
    # ========================================================

    def _resolve_opportunity_grade(
        self,
        ranking_score: float,
        evidence_gate: str,
        quality_gate: str,
        direction_conflict: float,
    ) -> str:

        # Hard protection against false high grades.
        if evidence_gate == "FAIL":
            return "D"

        if quality_gate == "FAIL":
            return "D"

        if direction_conflict >= 70.0:
            return "D"

        if (
            ranking_score >= 90.0
            and evidence_gate == "PASS"
            and quality_gate == "PASS"
        ):
            return "A+"

        if (
            ranking_score >= 80.0
            and evidence_gate == "PASS"
        ):
            return "A"

        if ranking_score >= 70.0:
            return "B"

        if ranking_score >= 60.0:
            return "C"

        return "D"


    # ========================================================
    # RANKING STATE
    # ========================================================

    def _resolve_ranking_state(
        self,
        ranking_score: float,
        profit_conversion: float,
        opportunity_grade: str,
        opportunity_bias: str,
    ) -> str:

        if opportunity_bias in (
            "UNKNOWN",
            "CONFLICTED",
        ):
            return "UNRESOLVED_DIRECTION"

        if opportunity_grade == "D":
            return "LOW_PRIORITY"

        if (
            ranking_score >= 85.0
            and profit_conversion >= 80.0
        ):
            return "HIGH_CONVICTION_CANDIDATE"

        if (
            ranking_score >= 75.0
            and profit_conversion >= 70.0
        ):
            return "STRONG_CANDIDATE"

        if ranking_score >= 60.0:
            return "WATCHLIST_CANDIDATE"

        return "LOW_PRIORITY"


    # ========================================================
    # RANKING CONFIDENCE
    # ========================================================

    def _calculate_ranking_confidence(
        self,
        ranking_score: float,
        profit_conversion: float,
        strength_confidence: float,
        direction_conflict: float,
    ) -> float:

        confidence = (
            ranking_score * 0.40
            + profit_conversion * 0.30
            + strength_confidence * 0.30
        )

        confidence -= (
            direction_conflict * 0.15
        )

        return self._clip(
            confidence
        )


    # ========================================================
    # PRIORITY
    # ========================================================

    def _resolve_priority(
        self,
        ranking_score: float,
        opportunity_grade: str,
        ranking_state: str,
    ) -> str:

        if (
            opportunity_grade == "A+"
            and ranking_state
            == "HIGH_CONVICTION_CANDIDATE"
        ):
            return "P1"

        if (
            opportunity_grade == "A"
            and ranking_state
            in (
                "HIGH_CONVICTION_CANDIDATE",
                "STRONG_CANDIDATE",
            )
        ):
            return "P2"

        if (
            opportunity_grade == "B"
            and ranking_score >= 70.0
        ):
            return "P3"

        if ranking_score >= 60.0:
            return "P4"

        return "P5"