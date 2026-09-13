# ============================================================ 
# ROBOMLM_PLUS 
# THESIS ENGINE — PART 1 
# Context / Measurement Foundation Layer 
# ============================================================ 
# Purpose: 
#     Convert market evidence into a structured opportunity 
#     thesis that downstream engines can evaluate. 
# 
# Architecture: 
# 
#     Evidence 
#          ↓ 
#     Opportunity 
#          ↓ 
#     THESIS 
#          ↓ 
#     Pullback 
#          ↓ 
#     Holdability 
#          ↓ 
#     Growth Protection 
#          ↓ 
#     Future Rank 
# 
# IMPORTANT: 
#     Thesis Engine does NOT issue trades. 
#     D13 remains final authority. 
# ============================================================ 
 
from __future__ import annotations 
 
from dataclasses import dataclass, field 
from datetime import datetime, timezone 
from enum import Enum 
from typing import Any, Dict, List, Optional
from enum import Enum
from .thesis_contract import ThesisSnapshot
from .thesis_base import (
    ThesisContext,
    ThesisDirection,
    ThesisState,
    ThesisType,
    ThesisTrigger,
    ThesisMeasurement,
) 
 
 
# ============================================================ 
# ENUMS 
# ============================================================ 
 
class ThesisDirection(str, Enum): 
 
    LONG = "LONG" 
    SHORT = "SHORT" 
 
    BULLISH = "BULLISH" 
    BEARISH = "BEARISH" 
 
    CALL = "CALL" 
    PUT = "PUT" 
 
    UNKNOWN = "UNKNOWN" 
 
 
class ThesisState(str, Enum): 
 
    DEVELOPING = "DEVELOPING" 
 
    EMERGING = "EMERGING" 
 
    BUILDING = "BUILDING" 
 
    CONFIRMED = "CONFIRMED" 
 
    HIGH_CONVICTION = "HIGH_CONVICTION" 
 
    EXHAUSTING = "EXHAUSTING" 
 
    FAILING = "FAILING" 
 
    INVALIDATED = "INVALIDATED" 
 
    UNKNOWN = "UNKNOWN" 
 
 
class ThesisType(str, Enum): 
 
    BREAKOUT = "BREAKOUT" 
 
    BREAKDOWN = "BREAKDOWN" 
 
    CONTINUATION = "CONTINUATION" 
 
    REVERSAL = "REVERSAL" 
 
    EXPANSION = "EXPANSION" 
 
    MOMENTUM = "MOMENTUM" 
 
    STRUCTURE = "STRUCTURE" 
 
    UNKNOWN = "UNKNOWN" 
 
 
class ThesisTrigger(str, Enum): 
 
    STRUCTURE = "STRUCTURE" 
 
    PARTICIPATION = "PARTICIPATION" 
 
    ACCUMULATION = "ACCUMULATION" 
 
    DISTRIBUTION = "DISTRIBUTION" 
 
    BREAKOUT = "BREAKOUT" 
 
    BREAKDOWN = "BREAKDOWN" 
 
    REGIME = "REGIME" 
 
    RELATIONSHIP = "RELATIONSHIP" 
 
    MULTI_FACTOR = "MULTI_FACTOR" 
 
    UNKNOWN = "UNKNOWN" 
 
 
# ============================================================ 
# CONTEXT 
# ============================================================ 
 
@dataclass 
class ThesisContext: 
    """ 
    Upstream normalized intelligence. 
 
    Opportunity Engine 
    Breakout Engine 
    Regime Engine 
    Relationship Engine 
    Structure Engine 
    feed this object. 
    """ 
 
    instrument: str = "" 
 
    timestamp: Optional[datetime] = None 
 
    direction: ThesisDirection = ( 
        ThesisDirection.UNKNOWN 
    ) 
 
    thesis_type: ThesisType = ( 
        ThesisType.UNKNOWN 
    ) 
 
    current_price: float = 0.0 
 
    # -------------------------------------------------------- 
    # Core Evidence 
    # -------------------------------------------------------- 
 
    evidence_score: float = 0.0 
 
    structure_score: float = 0.0 
 
    participation_score: float = 0.0 
 
    liquidity_score: float = 0.0 
 
    regime_score: float = 0.0 
 
    relationship_score: float = 0.0 
 
    opportunity_score: float = 0.0 
 
    # -------------------------------------------------------- 
    # Discovery Layer 
    # -------------------------------------------------------- 
 
    breakout_score: float = 0.0 
 
    accumulation_score: float = 0.0 
 
    distribution_score: float = 0.0 
 
    boundary_strength: float = 0.0 
 
    confirmation_score: float = 0.0 
 
    # -------------------------------------------------------- 
    # Risk Layer 
    # -------------------------------------------------------- 
 
    anti_evidence_score: float = 0.0 
 
    contradiction_score: float = 0.0 
 
    uncertainty_score: float = 0.0 
 
    # -------------------------------------------------------- 
    # Metadata 
    # -------------------------------------------------------- 
 
    source_engines: List[str] = field( 
        default_factory=list 
    ) 
 
    metadata: Dict[str, Any] = field( 
        default_factory=dict 
    ) 
 
    def normalize(self): 
 
        score_fields = [ 
 
            "evidence_score", 
 
            "structure_score", 
 
            "participation_score", 
 
            "liquidity_score", 
 
            "regime_score", 
 
            "relationship_score", 
 
            "opportunity_score", 
 
            "breakout_score", 
 
            "accumulation_score", 
 
            "distribution_score", 
 
            "boundary_strength", 
 
            "confirmation_score", 
 
            "anti_evidence_score", 
 
            "contradiction_score", 
 
            "uncertainty_score", 
        ] 
 
        for field_name in score_fields: 
 
            value = getattr( 
                self, 
                field_name, 
                0.0, 
            ) 
 
            try: 
                value = float(value) 
            except Exception: 
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
 
 
# ============================================================ 
# MEASUREMENT 
# ============================================================ 
 
@dataclass 
class ThesisMeasurement: 
 
    thesis_strength: float = 0.0 
 
    evidence_strength: float = 0.0 
 
    structure_support: float = 0.0 
 
    participation_support: float = 0.0 
 
    continuation_support: float = 0.0 
 
    conviction_score: float = 0.0 
 
    contradiction_pressure: float = 0.0 
 
    uncertainty_pressure: float = 0.0 
 
    failure_risk: float = 0.0 
 
    state: ThesisState = ( 
        ThesisState.UNKNOWN 
    ) 
 
    trigger: ThesisTrigger = ( 
        ThesisTrigger.UNKNOWN 
    ) 
 
    reasons: List[str] = field( 
        default_factory=list 
    ) 
 
    warnings: List[str] = field( 
        default_factory=list 
    ) 
 
    metadata: Dict[str, Any] = field( 
        default_factory=dict 
    ) 
 
    def to_dict(self): 
 
        return { 
 
            "thesis_strength": 
                self.thesis_strength, 
 
            "evidence_strength": 
                self.evidence_strength, 
 
            "structure_support": 
                self.structure_support, 
 
            "participation_support": 
                self.participation_support, 
 
            "continuation_support": 
                self.continuation_support, 
 
            "conviction_score": 
                self.conviction_score, 
 
            "contradiction_pressure": 
                self.contradiction_pressure, 
 
            "uncertainty_pressure": 
                self.uncertainty_pressure, 
 
            "failure_risk": 
                self.failure_risk, 
 
            "state": 
                self.state.value, 
 
            "trigger": 
                self.trigger.value, 
 
            "reasons": 
                list(self.reasons), 
 
            "warnings": 
                list(self.warnings), 
 
            "metadata": 
                dict(self.metadata), 
        } 
 
 
# ============================================================ 
# EVENT 
# ============================================================ 
 
@dataclass 
class ThesisEvent: 
 
    event_id: str = "" 
 
    timestamp: Optional[ 
        datetime 
    ] = None 
 
    instrument: str = "" 
 
    direction: ThesisDirection = ( 
        ThesisDirection.UNKNOWN 
    ) 
 
    state: ThesisState = ( 
        ThesisState.UNKNOWN 
    ) 
 
    trigger: ThesisTrigger = ( 
        ThesisTrigger.UNKNOWN 
    ) 
 
    thesis_strength: float = 0.0 
 
    material: bool = False 
 
    reason: str = "" 
 
    metadata: Dict[str, Any] = field( 
        default_factory=dict 
    ) 
 
    def to_dict(self): 
 
        return { 
 
            "event_id": 
                self.event_id, 
 
            "timestamp": 
                ( 
                    self.timestamp.isoformat() 
                    if self.timestamp 
                    else None 
                ), 
 
            "instrument": 
                self.instrument, 
 
            "direction": 
                self.direction.value, 
 
            "state": 
                self.state.value, 
 
            "trigger": 
                self.trigger.value, 
 
            "thesis_strength": 
                self.thesis_strength, 
 
            "material": 
                self.material, 
 
            "reason": 
                self.reason, 
 
            "metadata": 
                dict(self.metadata), 
        } 
 
 
# ============================================================ 
# ENGINE 
# ============================================================ 
 
class ThesisEngine: 
 
    ENGINE_NAME = ( 
        "ThesisEngine" 
    ) 
 
    ENGINE_VERSION = ( 
        "1.0.0" 
    ) 
 
    HIGH_CONVICTION = 85.0 
    CONFIRMED = 75.0 
    BUILDING = 60.0 
    EMERGING = 45.0 
 
    # -------------------------------------------------------- 
    # SUPPORT 
    # -------------------------------------------------------- 
 
    def calculate_support( 
        self, 
        context: ThesisContext, 
    ) -> float: 
 
        return ( 
 
            context.structure_score * 0.22 + 
 
            context.participation_score * 0.18 + 
 
            context.liquidity_score * 0.10 + 
 
            context.regime_score * 0.12 + 
 
            context.relationship_score * 0.08 + 
 
            context.confirmation_score * 0.15 + 
 
            context.opportunity_score * 0.15 
        ) 
 
    # -------------------------------------------------------- 
    # CONTRADICTION 
    # -------------------------------------------------------- 
 
    def calculate_pressure( 
        self, 
        context: ThesisContext, 
    ) -> float: 
 
        return ( 
 
            context.anti_evidence_score * 0.50 + 
 
            context.contradiction_score * 0.30 + 
 
            context.uncertainty_score * 0.20 
        ) 
 
    # -------------------------------------------------------- 
    # THESIS STRENGTH 
    # -------------------------------------------------------- 
 
    def calculate_thesis_strength( 
        self, 
        context: ThesisContext, 
    ) -> float: 
 
        support = ( 
            self.calculate_support( 
                context 
            ) 
        ) 
 
        pressure = ( 
            self.calculate_pressure( 
                context 
            ) 
        ) 
 
        score = ( 
            support 
            - 
            ( 
                pressure * 0.35 
            ) 
        ) 
 
        return max( 
            0.0, 
            min( 
                100.0, 
                score, 
            ), 
        ) 
 
    # -------------------------------------------------------- 
    # STATE 
    # -------------------------------------------------------- 
 
    def classify_state( 
        self, 
        score: float, 
    ) -> ThesisState: 
 
        if score >= self.HIGH_CONVICTION: 
            return ThesisState.HIGH_CONVICTION 
 
        if score >= self.CONFIRMED: 
            return ThesisState.CONFIRMED 
 
        if score >= self.BUILDING: 
            return ThesisState.BUILDING 
 
        if score >= self.EMERGING: 
            return ThesisState.EMERGING 
 
        return ThesisState.DEVELOPING  next code part 2 pls

Bilkul sir. Aapke Part 1 ke exact continuation mein Thesis Engine — Part 2 de raha hoon. Isme state classification ke baad trigger determination, conviction, failure risk, reasons/warnings, measurement construction aur final evaluate() flow complete hoga. D13 final authority rahega; Thesis Engine trade issue nahi karega.

# ============================================================
# ROBOMLM_PLUS
# THESIS ENGINE — PART 2
# Evaluation / Classification / Output Layer
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


# ============================================================
# TRIGGER CLASSIFICATION
# ============================================================

class ThesisEngine:
    """
    Converts normalized upstream market evidence into a
    structured thesis measurement.

    IMPORTANT
    ----------
    ThesisEngine does NOT issue trades.

    It measures:
        Evidence
        Structure
        Participation
        Continuation
        Conviction
        Contradiction
        Uncertainty
        Failure Risk
        Thesis State
        Thesis Trigger

    D13 remains the final decision authority.
    """

    ENGINE_NAME = "ThesisEngine"
    ENGINE_VERSION = "1.0.0"

    HIGH_CONVICTION = 85.0
    CONFIRMED = 75.0
    BUILDING = 60.0
    EMERGING = 45.0

    # --------------------------------------------------------
    # SUPPORT
    # --------------------------------------------------------

    def calculate_support(
        self,
        context: ThesisContext,
    ) -> float:

        return (
            context.structure_score * 0.22
            + context.participation_score * 0.18
            + context.liquidity_score * 0.10
            + context.regime_score * 0.12
            + context.relationship_score * 0.08
            + context.confirmation_score * 0.15
            + context.opportunity_score * 0.15
        )

    # --------------------------------------------------------
    # CONTRADICTION
    # --------------------------------------------------------

    def calculate_pressure(
        self,
        context: ThesisContext,
    ) -> float:

        return (
            context.anti_evidence_score * 0.50
            + context.contradiction_score * 0.30
            + context.uncertainty_score * 0.20
        )

    # --------------------------------------------------------
    # THESIS STRENGTH
    # --------------------------------------------------------

    def calculate_thesis_strength(
        self,
        context: ThesisContext,
    ) -> float:

        support = self.calculate_support(context)
        pressure = self.calculate_pressure(context)

        score = support - (pressure * 0.35)

        return max(
            0.0,
            min(100.0, score),
        )

    # --------------------------------------------------------
    # STATE
    # --------------------------------------------------------

    def classify_state(
        self,
        score: float,
    ) -> ThesisState:

        if score >= self.HIGH_CONVICTION:
            return ThesisState.HIGH_CONVICTION

        if score >= self.CONFIRMED:
            return ThesisState.CONFIRMED

        if score >= self.BUILDING:
            return ThesisState.BUILDING

        if score >= self.EMERGING:
            return ThesisState.EMERGING

        return ThesisState.DEVELOPING

    # --------------------------------------------------------
    # EVIDENCE STRENGTH
    # --------------------------------------------------------

    def calculate_evidence_strength(
        self,
        context: ThesisContext,
    ) -> float:

        return max(
            0.0,
            min(
                100.0,
                (
                    context.evidence_score * 0.40
                    + context.structure_score * 0.20
                    + context.participation_score * 0.15
                    + context.confirmation_score * 0.15
                    + context.opportunity_score * 0.10
                ),
            ),
        )

    # --------------------------------------------------------
    # STRUCTURE SUPPORT
    # --------------------------------------------------------

    def calculate_structure_support(
        self,
        context: ThesisContext,
    ) -> float:

        return max(
            0.0,
            min(
                100.0,
                (
                    context.structure_score * 0.60
                    + context.boundary_strength * 0.25
                    + context.confirmation_score * 0.15
                ),
            ),
        )

    # --------------------------------------------------------
    # PARTICIPATION SUPPORT
    # --------------------------------------------------------

    def calculate_participation_support(
        self,
        context: ThesisContext,
    ) -> float:

        return max(
            0.0,
            min(
                100.0,
                (
                    context.participation_score * 0.65
                    + context.accumulation_score * 0.15
                    + context.distribution_score * 0.20
                ),
            ),
        )

    # --------------------------------------------------------
    # CONTINUATION SUPPORT
    # --------------------------------------------------------

    def calculate_continuation_support(
        self,
        context: ThesisContext,
    ) -> float:

        return max(
            0.0,
            min(
                100.0,
                (
                    context.regime_score * 0.25
                    + context.relationship_score * 0.15
                    + context.confirmation_score * 0.25
                    + context.breakout_score * 0.20
                    + context.opportunity_score * 0.15
                ),
            ),
        )

    # --------------------------------------------------------
    # CONVICTION
    # --------------------------------------------------------

    def calculate_conviction(
        self,
        thesis_strength: float,
        evidence_strength: float,
        structure_support: float,
        participation_support: float,
        continuation_support: float,
        contradiction_pressure: float,
        uncertainty_pressure: float,
    ) -> float:

        positive = (
            thesis_strength * 0.30
            + evidence_strength * 0.15
            + structure_support * 0.15
            + participation_support * 0.15
            + continuation_support * 0.25
        )

        negative = (
            contradiction_pressure * 0.60
            + uncertainty_pressure * 0.40
        )

        score = positive - (negative * 0.35)

        return max(
            0.0,
            min(100.0, score),
        )

    # --------------------------------------------------------
    # FAILURE RISK
    # --------------------------------------------------------

    def calculate_failure_risk(
        self,
        context: ThesisContext,
    ) -> float:

        positive_failure_pressure = (
            context.anti_evidence_score * 0.35
            + context.contradiction_score * 0.25
            + context.uncertainty_score * 0.20
        )

        weak_confirmation = (
            max(
                0.0,
                100.0 - context.confirmation_score,
            )
            * 0.10
        )

        weak_structure = (
            max(
                0.0,
                100.0 - context.structure_score,
            )
            * 0.10
        )

        score = (
            positive_failure_pressure
            + weak_confirmation
            + weak_structure
        )

        return max(
            0.0,
            min(100.0, score),
        )

    # --------------------------------------------------------
    # TRIGGER
    # --------------------------------------------------------

    def classify_trigger(
        self,
        context: ThesisContext,
    ) -> ThesisTrigger:

        scores = {
            ThesisTrigger.STRUCTURE:
                context.structure_score,

            ThesisTrigger.PARTICIPATION:
                context.participation_score,

            ThesisTrigger.ACCUMULATION:
                context.accumulation_score,

            ThesisTrigger.DISTRIBUTION:
                context.distribution_score,

            ThesisTrigger.BREAKOUT:
                context.breakout_score,

            ThesisTrigger.BREAKDOWN:
                context.breakout_score,

            ThesisTrigger.REGIME:
                context.regime_score,

            ThesisTrigger.RELATIONSHIP:
                context.relationship_score,
        }

        # ----------------------------------------------------
        # Direction-aware breakout interpretation
        # ----------------------------------------------------

        if context.breakout_score >= 70.0:

            if context.direction in (
                ThesisDirection.SHORT,
                ThesisDirection.BEARISH,
                ThesisDirection.PUT,
            ):
                scores[ThesisTrigger.BREAKDOWN] = (
                    context.breakout_score
                )

                scores[ThesisTrigger.BREAKOUT] = 0.0

            else:
                scores[ThesisTrigger.BREAKOUT] = (
                    context.breakout_score
                )

                scores[ThesisTrigger.BREAKDOWN] = 0.0

        # ----------------------------------------------------
        # Multi-factor trigger
        # ----------------------------------------------------

        strong_factors = sum(
            1
            for value in [
                context.structure_score,
                context.participation_score,
                context.confirmation_score,
                context.opportunity_score,
                context.regime_score,
                context.relationship_score,
            ]
            if value >= 70.0
        )

        if strong_factors >= 3:
            return ThesisTrigger.MULTI_FACTOR

        strongest_trigger = max(
            scores,
            key=scores.get,
        )

        if scores[strongest_trigger] <= 0.0:
            return ThesisTrigger.UNKNOWN

        return strongest_trigger

    # --------------------------------------------------------
    # REASONS
    # --------------------------------------------------------

    def build_reasons(
        self,
        context: ThesisContext,
        measurement: ThesisMeasurement,
    ) -> List[str]:

        reasons: List[str] = []

        if context.structure_score >= 70.0:
            reasons.append(
                "Structure provides meaningful thesis support."
            )

        if context.participation_score >= 70.0:
            reasons.append(
                "Participation supports the developing thesis."
            )

        if context.confirmation_score >= 70.0:
            reasons.append(
                "Confirmation evidence strengthens the thesis."
            )

        if context.breakout_score >= 70.0:
            if context.direction in (
                ThesisDirection.SHORT,
                ThesisDirection.BEARISH,
                ThesisDirection.PUT,
            ):
                reasons.append(
                    "Breakdown evidence is materially present."
                )
            else:
                reasons.append(
                    "Breakout evidence is materially present."
                )

        if context.accumulation_score >= 70.0:
            reasons.append(
                "Accumulation evidence supports directional development."
            )

        if context.distribution_score >= 70.0:
            reasons.append(
                "Distribution evidence is materially present."
            )

        if context.regime_score >= 70.0:
            reasons.append(
                "Market regime is supportive of the thesis."
            )

        if context.relationship_score >= 70.0:
            reasons.append(
                "Cross-market relationship evidence is supportive."
            )

        if context.opportunity_score >= 70.0:
            reasons.append(
                "Opportunity context is sufficiently strong."
            )

        if not reasons:
            reasons.append(
                "Insufficient dominant evidence for a strong thesis."
            )

        return reasons

    # --------------------------------------------------------
    # WARNINGS
    # --------------------------------------------------------

    def build_warnings(
        self,
        context: ThesisContext,
        measurement: ThesisMeasurement,
    ) -> List[str]:

        warnings: List[str] = []

        if context.anti_evidence_score >= 60.0:
            warnings.append(
                "Anti-evidence pressure is materially elevated."
            )

        if context.contradiction_score >= 60.0:
            warnings.append(
                "Contradictory evidence is materially elevated."
            )

        if context.uncertainty_score >= 60.0:
            warnings.append(
                "Uncertainty remains materially elevated."
            )

        if context.confirmation_score < 50.0:
            warnings.append(
                "Confirmation remains weak."
            )

        if context.structure_score < 50.0:
            warnings.append(
                "Structural support remains weak."
            )

        if measurement.failure_risk >= 65.0:
            warnings.append(
                "Thesis failure risk is elevated."
            )

        if not context.instrument:
            warnings.append(
                "Instrument identity is missing."
            )

        if context.current_price <= 0.0:
            warnings.append(
                "Current price is unavailable or invalid."
            )

        return warnings

    # --------------------------------------------------------
    # INVALIDATION CHECK
    # --------------------------------------------------------

    def is_invalidated(
        self,
        context: ThesisContext,
        thesis_strength: float,
        failure_risk: float,
    ) -> bool:

        if failure_risk >= 85.0:
            return True

        if (
            context.anti_evidence_score >= 90.0
            and context.confirmation_score <= 20.0
        ):
            return True

        if (
            context.contradiction_score >= 90.0
            and thesis_strength < self.EMERGING
        ):
            return True

        return False

    # --------------------------------------------------------
    # EXHAUSTION CHECK
    # --------------------------------------------------------

    def is_exhausting(
        self,
        context: ThesisContext,
        thesis_strength: float,
    ) -> bool:

        return (
            thesis_strength >= self.CONFIRMED
            and context.uncertainty_score >= 65.0
            and context.confirmation_score < 50.0
        )

    # --------------------------------------------------------
    # FAILURE CHECK
    # --------------------------------------------------------

    def is_failing(
        self,
        context: ThesisContext,
        thesis_strength: float,
        failure_risk: float,
    ) -> bool:

        return (
            failure_risk >= 70.0
            or (
                thesis_strength < self.BUILDING
                and context.contradiction_score >= 70.0
            )
        )

    # --------------------------------------------------------
    # MEASUREMENT
    # --------------------------------------------------------

    def measure(
        self,
        context: ThesisContext,
    ) -> ThesisMeasurement:

        context.normalize()

        thesis_strength = (
            self.calculate_thesis_strength(
                context
            )
        )

        evidence_strength = (
            self.calculate_evidence_strength(
                context
            )
        )

        structure_support = (
            self.calculate_structure_support(
                context
            )
        )

        participation_support = (
            self.calculate_participation_support(
                context
            )
        )

        continuation_support = (
            self.calculate_continuation_support(
                context
            )
        )

        contradiction_pressure = (
            self.calculate_pressure(
                context
            )
        )

        uncertainty_pressure = (
            context.uncertainty_score
        )

        failure_risk = (
            self.calculate_failure_risk(
                context
            )
        )

        conviction_score = (
            self.calculate_conviction(
                thesis_strength=thesis_strength,
                evidence_strength=evidence_strength,
                structure_support=structure_support,
                participation_support=participation_support,
                continuation_support=continuation_support,
                contradiction_pressure=contradiction_pressure,
                uncertainty_pressure=uncertainty_pressure,
            )
        )

        state = self.classify_state(
            thesis_strength
        )

        trigger = self.classify_trigger(
            context
        )

        measurement = ThesisMeasurement(
            thesis_strength=thesis_strength,
            evidence_strength=evidence_strength,
            structure_support=structure_support,
            participation_support=participation_support,
            continuation_support=continuation_support,
            conviction_score=conviction_score,
            contradiction_pressure=contradiction_pressure,
            uncertainty_pressure=uncertainty_pressure,
            failure_risk=failure_risk,
            state=state,
            trigger=trigger,
        )

        # ----------------------------------------------------
        # State refinement
        # ----------------------------------------------------

        if self.is_invalidated(
            context,
            thesis_strength,
            failure_risk,
        ):
            measurement.state = (
                ThesisState.INVALIDATED
            )

        elif self.is_failing(
            context,
            thesis_strength,
            failure_risk,
        ):
            measurement.state = (
                ThesisState.FAILING
            )

        elif self.is_exhausting(
            context,
            thesis_strength,
        ):
            measurement.state = (
                ThesisState.EXHAUSTING
            )

        measurement.reasons = (
            self.build_reasons(
                context,
                measurement,
            )
        )

        measurement.warnings = (
            self.build_warnings(
                context,
                measurement,
            )
        )

        measurement.metadata = {
            "engine": self.ENGINE_NAME,
            "engine_version": self.ENGINE_VERSION,
            "instrument": context.instrument,
            "timestamp": (
                context.timestamp.isoformat()
                if context.timestamp
                else None
            ),
            "direction": context.direction.value,
            "thesis_type": context.thesis_type.value,
        }

        return measurement

    # --------------------------------------------------------
    # EVENT
    # --------------------------------------------------------

    def build_event(
        self,
        context: ThesisContext,
        measurement: ThesisMeasurement,
        previous_state: Optional[ThesisState] = None,
        previous_strength: Optional[float] = None,
    ) -> ThesisEvent:

        material = False
        reason = ""

        if (
            previous_state is not None
            and previous_state != measurement.state
        ):
            material = True

            reason = (
                "Thesis state transitioned from "
                f"{previous_state.value} to "
                f"{measurement.state.value}."
            )

        elif previous_strength is not None:

            strength_delta = (
                measurement.thesis_strength
                - previous_strength
            )

            if abs(strength_delta) >= 10.0:
                material = True

                direction_word = (
                    "strengthened"
                    if strength_delta > 0
                    else "weakened"
                )

                reason = (
                    f"Thesis materially {direction_word} "
                    f"by {abs(strength_delta):.2f} points."
                )

        if not reason:
            reason = (
                "Thesis measurement evaluated without "
                "a material transition."
            )

        event_id = (
            f"{context.instrument}:"
            f"{int(datetime.now(timezone.utc).timestamp() * 1000)}"
        )

        return ThesisEvent(
            event_id=event_id,
            timestamp=(
                context.timestamp
                or datetime.now(timezone.utc)
            ),
            instrument=context.instrument,
            direction=context.direction,
            state=measurement.state,
            trigger=measurement.trigger,
            thesis_strength=measurement.thesis_strength,
            material=material,
            reason=reason,
            metadata={
                "engine": self.ENGINE_NAME,
                "engine_version": self.ENGINE_VERSION,
            },
        )

    # --------------------------------------------------------
    # FINAL EVALUATION
    # --------------------------------------------------------

    def evaluate(
        self,
        context: ThesisContext,
        previous_state: Optional[ThesisState] = None,
        previous_strength: Optional[float] = None,
    ) -> Dict[str, Any]:

        """
        Complete thesis evaluation.

        Returns measurement + event.

        This method DOES NOT:
            - place orders
            - select broker
            - calculate position size
            - override D13
            - issue trade signals
        """

        context.normalize()

        measurement = self.measure(
            context
        )

        event = self.build_event(
            context=context,
            measurement=measurement,
            previous_state=previous_state,
            previous_strength=previous_strength,
        )

        return {
            "engine": self.ENGINE_NAME,
            "engine_version": self.ENGINE_VERSION,

            "instrument": context.instrument,

            "timestamp": (
                context.timestamp.isoformat()
                if context.timestamp
                else datetime.now(
                    timezone.utc
                ).isoformat()
            ),

            "direction": (
                context.direction.value
            ),

            "thesis_type": (
                context.thesis_type.value
            ),

            "measurement": (
                measurement.to_dict()
            ),

            "event": (
                event.to_dict()
            ),

            # Explicit authority boundary
            "decision_authority": "D13",
            "trade_issued": False,
        }

Part 2 ka role: Part 1 ke raw normalized inputs ko ab structured thesis measurement + state + trigger + conviction + failure risk + material event mein convert karta hai. evaluate() downstream ko clean contract deta hai, lekin BUY/SELL/entry/exit/order authority deliberately nahi deta.

part 3 code pls
Something went wrong. Please try again.

Bilkul sir. Part 3 mein Part 1 + Part 2 ke upar public output contract, serialization, validation, snapshot/state transition support, and safe downstream handoff add karte hain. Isme bhi D13 authority untouched rahegi.

# ============================================================
# ROBOMLM_PLUS
# THESIS ENGINE — PART 3
# Contract / Validation / Serialization / Handoff Layer
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ============================================================
# THESIS SNAPSHOT
# ============================================================

@dataclass
class ThesisSnapshot:
    """
    Immutable-style representation of the current thesis state.

    This object is intended for:
        - memory
        - comparison
        - downstream intelligence
        - audit
        - learning

    It does NOT represent a trade instruction.
    """

    instrument: str = ""

    timestamp: Optional[datetime] = None

    direction: ThesisDirection = (
        ThesisDirection.UNKNOWN
    )

    thesis_type: ThesisType = (
        ThesisType.UNKNOWN
    )

    state: ThesisState = (
        ThesisState.UNKNOWN
    )

    trigger: ThesisTrigger = (
        ThesisTrigger.UNKNOWN
    )

    thesis_strength: float = 0.0

    conviction_score: float = 0.0

    evidence_strength: float = 0.0

    structure_support: float = 0.0

    participation_support: float = 0.0

    continuation_support: float = 0.0

    contradiction_pressure: float = 0.0

    uncertainty_pressure: float = 0.0

    failure_risk: float = 0.0

    current_price: float = 0.0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "instrument": self.instrument,

            "timestamp": (
                self.timestamp.isoformat()
                if self.timestamp
                else None
            ),

            "direction": self.direction.value,

            "thesis_type": self.thesis_type.value,

            "state": self.state.value,

            "trigger": self.trigger.value,

            "thesis_strength": self.thesis_strength,

            "conviction_score": self.conviction_score,

            "evidence_strength": self.evidence_strength,

            "structure_support": self.structure_support,

            "participation_support":
                self.participation_support,

            "continuation_support":
                self.continuation_support,

            "contradiction_pressure":
                self.contradiction_pressure,

            "uncertainty_pressure":
                self.uncertainty_pressure,

            "failure_risk": self.failure_risk,

            "current_price": self.current_price,

            "metadata": dict(self.metadata),
        }


# ============================================================
# THESIS TRANSITION
# ============================================================

@dataclass
class ThesisTransition:

    instrument: str = ""

    previous_state: ThesisState = (
        ThesisState.UNKNOWN
    )

    current_state: ThesisState = (
        ThesisState.UNKNOWN
    )

    previous_strength: float = 0.0

    current_strength: float = 0.0

    strength_delta: float = 0.0

    material: bool = False

    direction_changed: bool = False

    previous_direction: ThesisDirection = (
        ThesisDirection.UNKNOWN
    )

    current_direction: ThesisDirection = (
        ThesisDirection.UNKNOWN
    )

    transition_type: str = "NONE"

    reason: str = ""

    timestamp: Optional[datetime] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "instrument": self.instrument,

            "previous_state":
                self.previous_state.value,

            "current_state":
                self.current_state.value,

            "previous_strength":
                self.previous_strength,

            "current_strength":
                self.current_strength,

            "strength_delta":
                self.strength_delta,

            "material":
                self.material,

            "direction_changed":
                self.direction_changed,

            "previous_direction":
                self.previous_direction.value,

            "current_direction":
                self.current_direction.value,

            "transition_type":
                self.transition_type,

            "reason":
                self.reason,

            "timestamp": (
                self.timestamp.isoformat()
                if self.timestamp
                else None
            ),

            "metadata":
                dict(self.metadata),
        }


# ============================================================
# THESIS VALIDATION
# ============================================================

@dataclass
class ThesisValidation:

    valid: bool = False

    instrument_valid: bool = False

    price_valid: bool = False

    direction_valid: bool = False

    measurement_valid: bool = False

    contradiction_valid: bool = False

    errors: List[str] = field(
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
            "valid": self.valid,

            "instrument_valid":
                self.instrument_valid,

            "price_valid":
                self.price_valid,

            "direction_valid":
                self.direction_valid,

            "measurement_valid":
                self.measurement_valid,

            "contradiction_valid":
                self.contradiction_valid,

            "errors": list(self.errors),

            "warnings": list(self.warnings),

            "metadata": dict(self.metadata),
        }


# ============================================================
# ENGINE EXTENSION
# ============================================================

class ThesisEngineContractMixin:
    """
    Contract-oriented functionality for ThesisEngine.

    This mixin deliberately contains no trading authority.
    """

    # --------------------------------------------------------
    # VALIDATE CONTEXT
    # --------------------------------------------------------

    def validate_context(
        self,
        context: ThesisContext,
    ) -> ThesisValidation:

        validation = ThesisValidation()

        # ----------------------------------------------------
        # Instrument
        # ----------------------------------------------------

        if (
            isinstance(context.instrument, str)
            and context.instrument.strip()
        ):
            validation.instrument_valid = True
        else:
            validation.errors.append(
                "Instrument identity is missing."
            )

        # ----------------------------------------------------
        # Price
        # ----------------------------------------------------

        try:
            price = float(
                context.current_price
            )

            if price > 0.0:
                validation.price_valid = True
            else:
                validation.errors.append(
                    "Current price must be greater than zero."
                )

        except Exception:
            validation.errors.append(
                "Current price is not numeric."
            )

        # ----------------------------------------------------
        # Direction
        # ----------------------------------------------------

        if (
            isinstance(
                context.direction,
                ThesisDirection,
            )
            and context.direction
            != ThesisDirection.UNKNOWN
        ):
            validation.direction_valid = True
        else:
            validation.warnings.append(
                "Directional thesis is currently unknown."
            )

        # ----------------------------------------------------
        # Score fields
        # ----------------------------------------------------

        score_fields = [
            "evidence_score",
            "structure_score",
            "participation_score",
            "liquidity_score",
            "regime_score",
            "relationship_score",
            "opportunity_score",
            "breakout_score",
            "accumulation_score",
            "distribution_score",
            "boundary_strength",
            "confirmation_score",
            "anti_evidence_score",
            "contradiction_score",
            "uncertainty_score",
        ]

        invalid_scores = []

        for field_name in score_fields:

            try:
                value = float(
                    getattr(
                        context,
                        field_name,
                    )
                )

                if not 0.0 <= value <= 100.0:
                    invalid_scores.append(
                        field_name
                    )

            except Exception:
                invalid_scores.append(
                    field_name
                )

        if not invalid_scores:

            validation.measurement_valid = True

        else:

            validation.errors.append(
                "Invalid score fields: "
                + ", ".join(invalid_scores)
            )

        # ----------------------------------------------------
        # Contradiction sanity
        # ----------------------------------------------------

        if (
            context.anti_evidence_score >= 0.0
            and context.contradiction_score >= 0.0
            and context.uncertainty_score >= 0.0
        ):
            validation.contradiction_valid = True

        # ----------------------------------------------------
        # Final
        # ----------------------------------------------------

        validation.valid = (
            validation.instrument_valid
            and validation.price_valid
            and validation.measurement_valid
            and validation.contradiction_valid
        )

        validation.metadata = {
            "engine": self.ENGINE_NAME,
            "engine_version":
                self.ENGINE_VERSION,
        }

        return validation

    # --------------------------------------------------------
    # SNAPSHOT
    # --------------------------------------------------------

    def create_snapshot(
        self,
        context: ThesisContext,
        measurement: ThesisMeasurement,
    ) -> ThesisSnapshot:

        return ThesisSnapshot(

            instrument=context.instrument,

            timestamp=(
                context.timestamp
                or datetime.now(timezone.utc)
            ),

            direction=context.direction,

            thesis_type=context.thesis_type,

            state=measurement.state,

            trigger=measurement.trigger,

            thesis_strength=(
                measurement.thesis_strength
            ),

            conviction_score=(
                measurement.conviction_score
            ),

            evidence_strength=(
                measurement.evidence_strength
            ),

            structure_support=(
                measurement.structure_support
            ),

            participation_support=(
                measurement.participation_support
            ),

            continuation_support=(
                measurement.continuation_support
            ),

            contradiction_pressure=(
                measurement.contradiction_pressure
            ),

            uncertainty_pressure=(
                measurement.uncertainty_pressure
            ),

            failure_risk=(
                measurement.failure_risk
            ),

            current_price=(
                context.current_price
            ),

            metadata={
                "engine": self.ENGINE_NAME,
                "engine_version":
                    self.ENGINE_VERSION,
            },
        )

    # --------------------------------------------------------
    # TRANSITION
    # --------------------------------------------------------

    def calculate_transition(
        self,
        context: ThesisContext,
        measurement: ThesisMeasurement,
        previous_state: Optional[ThesisState] = None,
        previous_strength: Optional[float] = None,
        previous_direction: Optional[
            ThesisDirection
        ] = None,
    ) -> ThesisTransition:

        current_state = measurement.state

        old_state = (
            previous_state
            or ThesisState.UNKNOWN
        )

        old_strength = (
            float(previous_strength)
            if previous_strength is not None
            else 0.0
        )

        current_strength = (
            measurement.thesis_strength
        )

        delta = (
            current_strength
            - old_strength
        )

        old_direction = (
            previous_direction
            or ThesisDirection.UNKNOWN
        )

        current_direction = (
            context.direction
        )

        direction_changed = (
            old_direction
            != ThesisDirection.UNKNOWN
            and current_direction
            != ThesisDirection.UNKNOWN
            and old_direction
            != current_direction
        )

        transition_type = "NONE"
        reason = "No material thesis transition."

        # ----------------------------------------------------
        # State transition
        # ----------------------------------------------------

        if old_state != current_state:

            transition_type = (
                f"{old_state.value}_TO_"
                f"{current_state.value}"
            )

            reason = (
                f"Thesis state changed from "
                f"{old_state.value} to "
                f"{current_state.value}."
            )

        elif direction_changed:

            transition_type = (
                "DIRECTION_CHANGE"
            )

            reason = (
                f"Thesis direction changed from "
                f"{old_direction.value} to "
                f"{current_direction.value}."
            )

        elif abs(delta) >= 10.0:

            transition_type = (
                "MATERIAL_STRENGTH_CHANGE"
            )

            if delta > 0:
                reason = (
                    "Thesis strength materially increased."
                )
            else:
                reason = (
                    "Thesis strength materially decreased."
                )

        material = (
            old_state != current_state
            or direction_changed
            or abs(delta) >= 10.0
        )

        return ThesisTransition(

            instrument=context.instrument,

            previous_state=old_state,

            current_state=current_state,

            previous_strength=old_strength,

            current_strength=current_strength,

            strength_delta=delta,

            material=material,

            direction_changed=direction_changed,

            previous_direction=old_direction,

            current_direction=current_direction,

            transition_type=transition_type,

            reason=reason,

            timestamp=(
                context.timestamp
                or datetime.now(timezone.utc)
            ),

            metadata={
                "engine": self.ENGINE_NAME,
                "engine_version":
                    self.ENGINE_VERSION,
            },
        )


# ============================================================
# FINAL CONTRACT ENGINE
# ============================================================

class ThesisContractEngine(
    ThesisEngineContractMixin,
    ThesisEngine,
):
    """
    Final contract-aware Thesis Engine.

    Flow:

        Context
           ↓
        Validation
           ↓
        Measurement
           ↓
        Snapshot
           ↓
        Transition
           ↓
        Structured Output
           ↓
        Downstream Intelligence
           ↓
        D13

    No trade authority exists here.
    """

    CONTRACT_VERSION = "1.0.0"

    # --------------------------------------------------------
    # RUN
    # --------------------------------------------------------

    def run(
        self,
        context: ThesisContext,
        previous_state: Optional[ThesisState] = None,
        previous_strength: Optional[float] = None,
        previous_direction: Optional[
            ThesisDirection
        ] = None,
    ) -> Dict[str, Any]:

        # ----------------------------------------------------
        # Normalize first
        # ----------------------------------------------------

        context.normalize()

        # ----------------------------------------------------
        # Validate
        # ----------------------------------------------------

        validation = self.validate_context(
            context
        )

        if not validation.valid:

            return {
                "engine":
                    self.ENGINE_NAME,

                "engine_version":
                    self.ENGINE_VERSION,

                "contract_version":
                    self.CONTRACT_VERSION,

                "status":
                    "INVALID",

                "instrument":
                    context.instrument,

                "validation":
                    validation.to_dict(),

                "measurement":
                    None,

                "snapshot":
                    None,

                "transition":
                    None,

                "decision_authority":
                    "D13",

                "trade_issued":
                    False,
            }

        # ----------------------------------------------------
        # Measure
        # ----------------------------------------------------

        measurement = self.measure(
            context
        )

        # ----------------------------------------------------
        # Snapshot
        # ----------------------------------------------------

        snapshot = self.create_snapshot(
            context,
            measurement,
        )

        # ----------------------------------------------------
        # Transition
        # ----------------------------------------------------

        transition = (
            self.calculate_transition(
                context=context,
                measurement=measurement,
                previous_state=previous_state,
                previous_strength=previous_strength,
                previous_direction=previous_direction,
            )
        )

        # ----------------------------------------------------
        # Final structured contract
        # ----------------------------------------------------

        return {

            "engine":
                self.ENGINE_NAME,

            "engine_version":
                self.ENGINE_VERSION,

            "contract_version":
                self.CONTRACT_VERSION,

            "status":
                "VALID",

            "instrument":
                context.instrument,

            "timestamp":
                (
                    context.timestamp.isoformat()
                    if context.timestamp
                    else datetime.now(
                        timezone.utc
                    ).isoformat()
                ),

            "validation":
                validation.to_dict(),

            "measurement":
                measurement.to_dict(),

            "snapshot":
                snapshot.to_dict(),

            "transition":
                transition.to_dict(),

            "upstream": {
                "source_engines":
                    list(context.source_engines),
            },

            "downstream_contract": {

                "thesis_state":
                    measurement.state.value,

                "thesis_trigger":
                    measurement.trigger.value,

                "thesis_strength":
                    measurement.thesis_strength,

                "conviction_score":
                    measurement.conviction_score,

                "failure_risk":
                    measurement.failure_risk,

                "contradiction_pressure":
                    measurement.contradiction_pressure,

                "uncertainty_pressure":
                    measurement.uncertainty_pressure,

                "requires_d13_evaluation":
                    True,
            },

            # ------------------------------------------------
            # HARD AUTHORITY BOUNDARY
            # ------------------------------------------------

            "decision_authority":
                "D13",

            "trade_issued":
                False,

            "order_instruction":
                None,

            "position_instruction":
                None,
        }


# ============================================================
# SAFE FACTORY
# ============================================================

def create_thesis_engine() -> ThesisContractEngine:
    """
    Standard factory for ROBOMLM_PLUS integration.
    """

    return ThesisContractEngine()


# ============================================================
# MODULE EXPORTS
# ============================================================

__all__ = [

    "ThesisSnapshot",

    "ThesisTransition",

    "ThesisValidation",

    "ThesisEngineContractMixin",

    "ThesisContractEngine",

    "create_thesis_engine",
]
# ============================================================
# ROBOMLM_PLUS
# THESIS ENGINE — PART 2
# Evaluation / Classification / Output Layer
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


# ============================================================
# TRIGGER CLASSIFICATION
# ============================================================

class ThesisEngine:
    """
    Converts normalized upstream market evidence into a
    structured thesis measurement.

    IMPORTANT
    ----------
    ThesisEngine does NOT issue trades.

    It measures:
        Evidence
        Structure
        Participation
        Continuation
        Conviction
        Contradiction
        Uncertainty
        Failure Risk
        Thesis State
        Thesis Trigger

    D13 remains the final decision authority.
    """

    ENGINE_NAME = "ThesisEngine"
    ENGINE_VERSION = "1.0.0"

    HIGH_CONVICTION = 85.0
    CONFIRMED = 75.0
    BUILDING = 60.0
    EMERGING = 45.0

    # --------------------------------------------------------
    # SUPPORT
    # --------------------------------------------------------

    def calculate_support(
        self,
        context: ThesisContext,
    ) -> float:

        return (
            context.structure_score * 0.22
            + context.participation_score * 0.18
            + context.liquidity_score * 0.10
            + context.regime_score * 0.12
            + context.relationship_score * 0.08
            + context.confirmation_score * 0.15
            + context.opportunity_score * 0.15
        )

    # --------------------------------------------------------
    # CONTRADICTION
    # --------------------------------------------------------

    def calculate_pressure(
        self,
        context: ThesisContext,
    ) -> float:

        return (
            context.anti_evidence_score * 0.50
            + context.contradiction_score * 0.30
            + context.uncertainty_score * 0.20
        )

    # --------------------------------------------------------
    # THESIS STRENGTH
    # --------------------------------------------------------

    def calculate_thesis_strength(
        self,
        context: ThesisContext,
    ) -> float:

        support = self.calculate_support(context)
        pressure = self.calculate_pressure(context)

        score = support - (pressure * 0.35)

        return max(
            0.0,
            min(100.0, score),
        )

    # --------------------------------------------------------
    # STATE
    # --------------------------------------------------------

    def classify_state(
        self,
        score: float,
    ) -> ThesisState:

        if score >= self.HIGH_CONVICTION:
            return ThesisState.HIGH_CONVICTION

        if score >= self.CONFIRMED:
            return ThesisState.CONFIRMED

        if score >= self.BUILDING:
            return ThesisState.BUILDING

        if score >= self.EMERGING:
            return ThesisState.EMERGING

        return ThesisState.DEVELOPING

    # --------------------------------------------------------
    # EVIDENCE STRENGTH
    # --------------------------------------------------------

    def calculate_evidence_strength(
        self,
        context: ThesisContext,
    ) -> float:

        return max(
            0.0,
            min(
                100.0,
                (
                    context.evidence_score * 0.40
                    + context.structure_score * 0.20
                    + context.participation_score * 0.15
                    + context.confirmation_score * 0.15
                    + context.opportunity_score * 0.10
                ),
            ),
        )

    # --------------------------------------------------------
    # STRUCTURE SUPPORT
    # --------------------------------------------------------

    def calculate_structure_support(
        self,
        context: ThesisContext,
    ) -> float:

        return max(
            0.0,
            min(
                100.0,
                (
                    context.structure_score * 0.60
                    + context.boundary_strength * 0.25
                    + context.confirmation_score * 0.15
                ),
            ),
        )

    # --------------------------------------------------------
    # PARTICIPATION SUPPORT
    # --------------------------------------------------------

    def calculate_participation_support(
        self,
        context: ThesisContext,
    ) -> float:

        return max(
            0.0,
            min(
                100.0,
                (
                    context.participation_score * 0.65
                    + context.accumulation_score * 0.15
                    + context.distribution_score * 0.20
                ),
            ),
        )

    # --------------------------------------------------------
    # CONTINUATION SUPPORT
    # --------------------------------------------------------

    def calculate_continuation_support(
        self,
        context: ThesisContext,
    ) -> float:

        return max(
            0.0,
            min(
                100.0,
                (
                    context.regime_score * 0.25
                    + context.relationship_score * 0.15
                    + context.confirmation_score * 0.25
                    + context.breakout_score * 0.20
                    + context.opportunity_score * 0.15
                ),
            ),
        )

    # --------------------------------------------------------
    # CONVICTION
    # --------------------------------------------------------

    def calculate_conviction(
        self,
        thesis_strength: float,
        evidence_strength: float,
        structure_support: float,
        participation_support: float,
        continuation_support: float,
        contradiction_pressure: float,
        uncertainty_pressure: float,
    ) -> float:

        positive = (
            thesis_strength * 0.30
            + evidence_strength * 0.15
            + structure_support * 0.15
            + participation_support * 0.15
            + continuation_support * 0.25
        )

        negative = (
            contradiction_pressure * 0.60
            + uncertainty_pressure * 0.40
        )

        score = positive - (negative * 0.35)

        return max(
            0.0,
            min(100.0, score),
        )

    # --------------------------------------------------------
    # FAILURE RISK
    # --------------------------------------------------------

    def calculate_failure_risk(
        self,
        context: ThesisContext,
    ) -> float:

        positive_failure_pressure = (
            context.anti_evidence_score * 0.35
            + context.contradiction_score * 0.25
            + context.uncertainty_score * 0.20
        )

        weak_confirmation = (
            max(
                0.0,
                100.0 - context.confirmation_score,
            )
            * 0.10
        )

        weak_structure = (
            max(
                0.0,
                100.0 - context.structure_score,
            )
            * 0.10
        )

        score = (
            positive_failure_pressure
            + weak_confirmation
            + weak_structure
        )

        return max(
            0.0,
            min(100.0, score),
        )

    # --------------------------------------------------------
    # TRIGGER
    # --------------------------------------------------------

    def classify_trigger(
        self,
        context: ThesisContext,
    ) -> ThesisTrigger:

        scores = {
            ThesisTrigger.STRUCTURE:
                context.structure_score,

            ThesisTrigger.PARTICIPATION:
                context.participation_score,

            ThesisTrigger.ACCUMULATION:
                context.accumulation_score,

            ThesisTrigger.DISTRIBUTION:
                context.distribution_score,

            ThesisTrigger.BREAKOUT:
                context.breakout_score,

            ThesisTrigger.BREAKDOWN:
                context.breakout_score,

            ThesisTrigger.REGIME:
                context.regime_score,

            ThesisTrigger.RELATIONSHIP:
                context.relationship_score,
        }

        # ----------------------------------------------------
        # Direction-aware breakout interpretation
        # ----------------------------------------------------

        if context.breakout_score >= 70.0:

            if context.direction in (
                ThesisDirection.SHORT,
                ThesisDirection.BEARISH,
                ThesisDirection.PUT,
            ):
                scores[ThesisTrigger.BREAKDOWN] = (
                    context.breakout_score
                )

                scores[ThesisTrigger.BREAKOUT] = 0.0

            else:
                scores[ThesisTrigger.BREAKOUT] = (
                    context.breakout_score
                )

                scores[ThesisTrigger.BREAKDOWN] = 0.0

        # ----------------------------------------------------
        # Multi-factor trigger
        # ----------------------------------------------------

        strong_factors = sum(
            1
            for value in [
                context.structure_score,
                context.participation_score,
                context.confirmation_score,
                context.opportunity_score,
                context.regime_score,
                context.relationship_score,
            ]
            if value >= 70.0
        )

        if strong_factors >= 3:
            return ThesisTrigger.MULTI_FACTOR

        strongest_trigger = max(
            scores,
            key=scores.get,
        )

        if scores[strongest_trigger] <= 0.0:
            return ThesisTrigger.UNKNOWN

        return strongest_trigger

    # --------------------------------------------------------
    # REASONS
    # --------------------------------------------------------

    def build_reasons(
        self,
        context: ThesisContext,
        measurement: ThesisMeasurement,
    ) -> List[str]:

        reasons: List[str] = []

        if context.structure_score >= 70.0:
            reasons.append(
                "Structure provides meaningful thesis support."
            )

        if context.participation_score >= 70.0:
            reasons.append(
                "Participation supports the developing thesis."
            )

        if context.confirmation_score >= 70.0:
            reasons.append(
                "Confirmation evidence strengthens the thesis."
            )

        if context.breakout_score >= 70.0:
            if context.direction in (
                ThesisDirection.SHORT,
                ThesisDirection.BEARISH,
                ThesisDirection.PUT,
            ):
                reasons.append(
                    "Breakdown evidence is materially present."
                )
            else:
                reasons.append(
                    "Breakout evidence is materially present."
                )

        if context.accumulation_score >= 70.0:
            reasons.append(
                "Accumulation evidence supports directional development."
            )

        if context.distribution_score >= 70.0:
            reasons.append(
                "Distribution evidence is materially present."
            )

        if context.regime_score >= 70.0:
            reasons.append(
                "Market regime is supportive of the thesis."
            )

        if context.relationship_score >= 70.0:
            reasons.append(
                "Cross-market relationship evidence is supportive."
            )

        if context.opportunity_score >= 70.0:
            reasons.append(
                "Opportunity context is sufficiently strong."
            )

        if not reasons:
            reasons.append(
                "Insufficient dominant evidence for a strong thesis."
            )

        return reasons

    # --------------------------------------------------------
    # WARNINGS
    # --------------------------------------------------------

    def build_warnings(
        self,
        context: ThesisContext,
        measurement: ThesisMeasurement,
    ) -> List[str]:

        warnings: List[str] = []

        if context.anti_evidence_score >= 60.0:
            warnings.append(
                "Anti-evidence pressure is materially elevated."
            )

        if context.contradiction_score >= 60.0:
            warnings.append(
                "Contradictory evidence is materially elevated."
            )

        if context.uncertainty_score >= 60.0:
            warnings.append(
                "Uncertainty remains materially elevated."
            )

        if context.confirmation_score < 50.0:
            warnings.append(
                "Confirmation remains weak."
            )

        if context.structure_score < 50.0:
            warnings.append(
                "Structural support remains weak."
            )

        if measurement.failure_risk >= 65.0:
            warnings.append(
                "Thesis failure risk is elevated."
            )

        if not context.instrument:
            warnings.append(
                "Instrument identity is missing."
            )

        if context.current_price <= 0.0:
            warnings.append(
                "Current price is unavailable or invalid."
            )

        return warnings

    # --------------------------------------------------------
    # INVALIDATION CHECK
    # --------------------------------------------------------

    def is_invalidated(
        self,
        context: ThesisContext,
        thesis_strength: float,
        failure_risk: float,
    ) -> bool:

        if failure_risk >= 85.0:
            return True

        if (
            context.anti_evidence_score >= 90.0
            and context.confirmation_score <= 20.0
        ):
            return True

        if (
            context.contradiction_score >= 90.0
            and thesis_strength < self.EMERGING
        ):
            return True

        return False

    # --------------------------------------------------------
    # EXHAUSTION CHECK
    # --------------------------------------------------------

    def is_exhausting(
        self,
        context: ThesisContext,
        thesis_strength: float,
    ) -> bool:

        return (
            thesis_strength >= self.CONFIRMED
            and context.uncertainty_score >= 65.0
            and context.confirmation_score < 50.0
        )

    # --------------------------------------------------------
    # FAILURE CHECK
    # --------------------------------------------------------

    def is_failing(
        self,
        context: ThesisContext,
        thesis_strength: float,
        failure_risk: float,
    ) -> bool:

        return (
            failure_risk >= 70.0
            or (
                thesis_strength < self.BUILDING
                and context.contradiction_score >= 70.0
            )
        )

    # --------------------------------------------------------
    # MEASUREMENT
    # --------------------------------------------------------

    def measure(
        self,
        context: ThesisContext,
    ) -> ThesisMeasurement:

        context.normalize()

        thesis_strength = (
            self.calculate_thesis_strength(
                context
            )
        )

        evidence_strength = (
            self.calculate_evidence_strength(
                context
            )
        )

        structure_support = (
            self.calculate_structure_support(
                context
            )
        )

        participation_support = (
            self.calculate_participation_support(
                context
            )
        )

        continuation_support = (
            self.calculate_continuation_support(
                context
            )
        )

        contradiction_pressure = (
            self.calculate_pressure(
                context
            )
        )

        uncertainty_pressure = (
            context.uncertainty_score
        )

        failure_risk = (
            self.calculate_failure_risk(
                context
            )
        )

        conviction_score = (
            self.calculate_conviction(
                thesis_strength=thesis_strength,
                evidence_strength=evidence_strength,
                structure_support=structure_support,
                participation_support=participation_support,
                continuation_support=continuation_support,
                contradiction_pressure=contradiction_pressure,
                uncertainty_pressure=uncertainty_pressure,
            )
        )

        state = self.classify_state(
            thesis_strength
        )

        trigger = self.classify_trigger(
            context
        )

        measurement = ThesisMeasurement(
            thesis_strength=thesis_strength,
            evidence_strength=evidence_strength,
            structure_support=structure_support,
            participation_support=participation_support,
            continuation_support=continuation_support,
            conviction_score=conviction_score,
            contradiction_pressure=contradiction_pressure,
            uncertainty_pressure=uncertainty_pressure,
            failure_risk=failure_risk,
            state=state,
            trigger=trigger,
        )

        # ----------------------------------------------------
        # State refinement
        # ----------------------------------------------------

        if self.is_invalidated(
            context,
            thesis_strength,
            failure_risk,
        ):
            measurement.state = (
                ThesisState.INVALIDATED
            )

        elif self.is_failing(
            context,
            thesis_strength,
            failure_risk,
        ):
            measurement.state = (
                ThesisState.FAILING
            )

        elif self.is_exhausting(
            context,
            thesis_strength,
        ):
            measurement.state = (
                ThesisState.EXHAUSTING
            )

        measurement.reasons = (
            self.build_reasons(
                context,
                measurement,
            )
        )

        measurement.warnings = (
            self.build_warnings(
                context,
                measurement,
            )
        )

        measurement.metadata = {
            "engine": self.ENGINE_NAME,
            "engine_version": self.ENGINE_VERSION,
            "instrument": context.instrument,
            "timestamp": (
                context.timestamp.isoformat()
                if context.timestamp
                else None
            ),
            "direction": context.direction.value,
            "thesis_type": context.thesis_type.value,
        }

        return measurement

    # --------------------------------------------------------
    # EVENT
    # --------------------------------------------------------

    def build_event(
        self,
        context: ThesisContext,
        measurement: ThesisMeasurement,
        previous_state: Optional[ThesisState] = None,
        previous_strength: Optional[float] = None,
    ) -> ThesisEvent:

        material = False
        reason = ""

        if (
            previous_state is not None
            and previous_state != measurement.state
        ):
            material = True

            reason = (
                "Thesis state transitioned from "
                f"{previous_state.value} to "
                f"{measurement.state.value}."
            )

        elif previous_strength is not None:

            strength_delta = (
                measurement.thesis_strength
                - previous_strength
            )

            if abs(strength_delta) >= 10.0:
                material = True

                direction_word = (
                    "strengthened"
                    if strength_delta > 0
                    else "weakened"
                )

                reason = (
                    f"Thesis materially {direction_word} "
                    f"by {abs(strength_delta):.2f} points."
                )

        if not reason:
            reason = (
                "Thesis measurement evaluated without "
                "a material transition."
            )

        event_id = (
            f"{context.instrument}:"
            f"{int(datetime.now(timezone.utc).timestamp() * 1000)}"
        )

        return ThesisEvent(
            event_id=event_id,
            timestamp=(
                context.timestamp
                or datetime.now(timezone.utc)
            ),
            instrument=context.instrument,
            direction=context.direction,
            state=measurement.state,
            trigger=measurement.trigger,
            thesis_strength=measurement.thesis_strength,
            material=material,
            reason=reason,
            metadata={
                "engine": self.ENGINE_NAME,
                "engine_version": self.ENGINE_VERSION,
            },
        )

    # --------------------------------------------------------
    # FINAL EVALUATION
    # --------------------------------------------------------

    def evaluate(
        self,
        context: ThesisContext,
        previous_state: Optional[ThesisState] = None,
        previous_strength: Optional[float] = None,
    ) -> Dict[str, Any]:

        """
        Complete thesis evaluation.

        Returns measurement + event.

        This method DOES NOT:
            - place orders
            - select broker
            - calculate position size
            - override D13
            - issue trade signals
        """

        context.normalize()

        measurement = self.measure(
            context
        )

        event = self.build_event(
            context=context,
            measurement=measurement,
            previous_state=previous_state,
            previous_strength=previous_strength,
        )

        return {
            "engine": self.ENGINE_NAME,
            "engine_version": self.ENGINE_VERSION,

            "instrument": context.instrument,

            "timestamp": (
                context.timestamp.isoformat()
                if context.timestamp
                else datetime.now(
                    timezone.utc
                ).isoformat()
            ),

            "direction": (
                context.direction.value
            ),

            "thesis_type": (
                context.thesis_type.value
            ),

            "measurement": (
                measurement.to_dict()
            ),

            "event": (
                event.to_dict()
            ),

            # Explicit authority boundary
            "decision_authority": "D13",
            "trade_issued": False,
        }
```python
# ============================================================
# ROBOMLM_PLUS
# THESIS ENGINE — PART 3
# Contract / Validation / Serialization / Handoff Layer
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ============================================================
# THESIS SNAPSHOT
# ============================================================

@dataclass
class ThesisSnapshot:
    """
    Immutable-style representation of the current thesis state.

    This object is intended for:
        - memory
        - comparison
        - downstream intelligence
        - audit
        - learning

    It does NOT represent a trade instruction.
    """

    instrument: str = ""

    timestamp: Optional[datetime] = None

    direction: ThesisDirection = (
        ThesisDirection.UNKNOWN
    )

    thesis_type: ThesisType = (
        ThesisType.UNKNOWN
    )

    state: ThesisState = (
        ThesisState.UNKNOWN
    )

    trigger: ThesisTrigger = (
        ThesisTrigger.UNKNOWN
    )

    thesis_strength: float = 0.0

    conviction_score: float = 0.0

    evidence_strength: float = 0.0

    structure_support: float = 0.0

    participation_support: float = 0.0

    continuation_support: float = 0.0

    contradiction_pressure: float = 0.0

    uncertainty_pressure: float = 0.0

    failure_risk: float = 0.0

    current_price: float = 0.0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "instrument": self.instrument,

            "timestamp": (
                self.timestamp.isoformat()
                if self.timestamp
                else None
            ),

            "direction": self.direction.value,

            "thesis_type": self.thesis_type.value,

            "state": self.state.value,

            "trigger": self.trigger.value,

            "thesis_strength": self.thesis_strength,

            "conviction_score": self.conviction_score,

            "evidence_strength": self.evidence_strength,

            "structure_support": self.structure_support,

            "participation_support":
                self.participation_support,

            "continuation_support":
                self.continuation_support,

            "contradiction_pressure":
                self.contradiction_pressure,

            "uncertainty_pressure":
                self.uncertainty_pressure,

            "failure_risk": self.failure_risk,

            "current_price": self.current_price,

            "metadata": dict(self.metadata),
        }


# ============================================================
# THESIS TRANSITION
# ============================================================

@dataclass
class ThesisTransition:

    instrument: str = ""

    previous_state: ThesisState = (
        ThesisState.UNKNOWN
    )

    current_state: ThesisState = (
        ThesisState.UNKNOWN
    )

    previous_strength: float = 0.0

    current_strength: float = 0.0

    strength_delta: float = 0.0

    material: bool = False

    direction_changed: bool = False

    previous_direction: ThesisDirection = (
        ThesisDirection.UNKNOWN
    )

    current_direction: ThesisDirection = (
        ThesisDirection.UNKNOWN
    )

    transition_type: str = "NONE"

    reason: str = ""

    timestamp: Optional[datetime] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "instrument": self.instrument,

            "previous_state":
                self.previous_state.value,

            "current_state":
                self.current_state.value,

            "previous_strength":
                self.previous_strength,

            "current_strength":
                self.current_strength,

            "strength_delta":
                self.strength_delta,

            "material":
                self.material,

            "direction_changed":
                self.direction_changed,

            "previous_direction":
                self.previous_direction.value,

            "current_direction":
                self.current_direction.value,

            "transition_type":
                self.transition_type,

            "reason":
                self.reason,

            "timestamp": (
                self.timestamp.isoformat()
                if self.timestamp
                else None
            ),

            "metadata":
                dict(self.metadata),
        }


# ============================================================
# THESIS VALIDATION
# ============================================================

@dataclass
class ThesisValidation:

    valid: bool = False

    instrument_valid: bool = False

    price_valid: bool = False

    direction_valid: bool = False

    measurement_valid: bool = False

    contradiction_valid: bool = False

    errors: List[str] = field(
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
            "valid": self.valid,

            "instrument_valid":
                self.instrument_valid,

            "price_valid":
                self.price_valid,

            "direction_valid":
                self.direction_valid,

            "measurement_valid":
                self.measurement_valid,

            "contradiction_valid":
                self.contradiction_valid,

            "errors": list(self.errors),

            "warnings": list(self.warnings),

            "metadata": dict(self.metadata),
        }


# ============================================================
# ENGINE EXTENSION
# ============================================================

class ThesisEngineContractMixin:
    """
    Contract-oriented functionality for ThesisEngine.

    This mixin deliberately contains no trading authority.
    """

    # --------------------------------------------------------
    # VALIDATE CONTEXT
    # --------------------------------------------------------

    def validate_context(
        self,
        context: ThesisContext,
    ) -> ThesisValidation:

        validation = ThesisValidation()

        # ----------------------------------------------------
        # Instrument
        # ----------------------------------------------------

        if (
            isinstance(context.instrument, str)
            and context.instrument.strip()
        ):
            validation.instrument_valid = True
        else:
            validation.errors.append(
                "Instrument identity is missing."
            )

        # ----------------------------------------------------
        # Price
        # ----------------------------------------------------

        try:
            price = float(
                context.current_price
            )

            if price > 0.0:
                validation.price_valid = True
            else:
                validation.errors.append(
                    "Current price must be greater than zero."
                )

        except Exception:
            validation.errors.append(
                "Current price is not numeric."
            )

        # ----------------------------------------------------
        # Direction
        # ----------------------------------------------------

        if (
            isinstance(
                context.direction,
                ThesisDirection,
            )
            and context.direction
            != ThesisDirection.UNKNOWN
        ):
            validation.direction_valid = True
        else:
            validation.warnings.append(
                "Directional thesis is currently unknown."
            )

        # ----------------------------------------------------
        # Score fields
        # ----------------------------------------------------

        score_fields = [
            "evidence_score",
            "structure_score",
            "participation_score",
            "liquidity_score",
            "regime_score",
            "relationship_score",
            "opportunity_score",
            "breakout_score",
            "accumulation_score",
            "distribution_score",
            "boundary_strength",
            "confirmation_score",
            "anti_evidence_score",
            "contradiction_score",
            "uncertainty_score",
        ]

        invalid_scores = []

        for field_name in score_fields:

            try:
                value = float(
                    getattr(
                        context,
                        field_name,
                    )
                )

                if not 0.0 <= value <= 100.0:
                    invalid_scores.append(
                        field_name
                    )

            except Exception:
                invalid_scores.append(
                    field_name
                )

        if not invalid_scores:

            validation.measurement_valid = True

        else:

            validation.errors.append(
                "Invalid score fields: "
                + ", ".join(invalid_scores)
            )

        # ----------------------------------------------------
        # Contradiction sanity
        # ----------------------------------------------------

        if (
            context.anti_evidence_score >= 0.0
            and context.contradiction_score >= 0.0
            and context.uncertainty_score >= 0.0
        ):
            validation.contradiction_valid = True

        # ----------------------------------------------------
        # Final
        # ----------------------------------------------------

        validation.valid = (
            validation.instrument_valid
            and validation.price_valid
            and validation.measurement_valid
            and validation.contradiction_valid
        )

        validation.metadata = {
            "engine": self.ENGINE_NAME,
            "engine_version":
                self.ENGINE_VERSION,
        }

        return validation

    # --------------------------------------------------------
    # SNAPSHOT
    # --------------------------------------------------------

    def create_snapshot(
        self,
        context: ThesisContext,
        measurement: ThesisMeasurement,
    ) -> ThesisSnapshot:

        return ThesisSnapshot(

            instrument=context.instrument,

            timestamp=(
                context.timestamp
                or datetime.now(timezone.utc)
            ),

            direction=context.direction,

            thesis_type=context.thesis_type,

            state=measurement.state,

            trigger=measurement.trigger,

            thesis_strength=(
                measurement.thesis_strength
            ),

            conviction_score=(
                measurement.conviction_score
            ),

            evidence_strength=(
                measurement.evidence_strength
            ),

            structure_support=(
                measurement.structure_support
            ),

            participation_support=(
                measurement.participation_support
            ),

            continuation_support=(
                measurement.continuation_support
            ),

            contradiction_pressure=(
                measurement.contradiction_pressure
            ),

            uncertainty_pressure=(
                measurement.uncertainty_pressure
            ),

            failure_risk=(
                measurement.failure_risk
            ),

            current_price=(
                context.current_price
            ),

            metadata={
                "engine": self.ENGINE_NAME,
                "engine_version":
                    self.ENGINE_VERSION,
            },
        )

    # --------------------------------------------------------
    # TRANSITION
    # --------------------------------------------------------

    def calculate_transition(
        self,
        context: ThesisContext,
        measurement: ThesisMeasurement,
        previous_state: Optional[ThesisState] = None,
        previous_strength: Optional[float] = None,
        previous_direction: Optional[
            ThesisDirection
        ] = None,
    ) -> ThesisTransition:

        current_state = measurement.state

        old_state = (
            previous_state
            or ThesisState.UNKNOWN
        )

        old_strength = (
            float(previous_strength)
            if previous_strength is not None
            else 0.0
        )

        current_strength = (
            measurement.thesis_strength
        )

        delta = (
            current_strength
            - old_strength
        )

        old_direction = (
            previous_direction
            or ThesisDirection.UNKNOWN
        )

        current_direction = (
            context.direction
        )

        direction_changed = (
            old_direction
            != ThesisDirection.UNKNOWN
            and current_direction
            != ThesisDirection.UNKNOWN
            and old_direction
            != current_direction
        )

        transition_type = "NONE"
        reason = "No material thesis transition."

        # ----------------------------------------------------
        # State transition
        # ----------------------------------------------------

        if old_state != current_state:

            transition_type = (
                f"{old_state.value}_TO_"
                f"{current_state.value}"
            )

            reason = (
                f"Thesis state changed from "
                f"{old_state.value} to "
                f"{current_state.value}."
            )

        elif direction_changed:

            transition_type = (
                "DIRECTION_CHANGE"
            )

            reason = (
                f"Thesis direction changed from "
                f"{old_direction.value} to "
                f"{current_direction.value}."
            )

        elif abs(delta) >= 10.0:

            transition_type = (
                "MATERIAL_STRENGTH_CHANGE"
            )

            if delta > 0:
                reason = (
                    "Thesis strength materially increased."
                )
            else:
                reason = (
                    "Thesis strength materially decreased."
                )

        material = (
            old_state != current_state
            or direction_changed
            or abs(delta) >= 10.0
        )

        return ThesisTransition(

            instrument=context.instrument,

            previous_state=old_state,

            current_state=current_state,

            previous_strength=old_strength,

            current_strength=current_strength,

            strength_delta=delta,

            material=material,

            direction_changed=direction_changed,

            previous_direction=old_direction,

            current_direction=current_direction,

            transition_type=transition_type,

            reason=reason,

            timestamp=(
                context.timestamp
                or datetime.now(timezone.utc)
            ),

            metadata={
                "engine": self.ENGINE_NAME,
                "engine_version":
                    self.ENGINE_VERSION,
            },
        )


# ============================================================
# FINAL CONTRACT ENGINE
# ============================================================

class ThesisContractEngine(
    ThesisEngineContractMixin,
    ThesisEngine,
):
    """
    Final contract-aware Thesis Engine.

    Flow:

        Context
           ↓
        Validation
           ↓
        Measurement
           ↓
        Snapshot
           ↓
        Transition
           ↓
        Structured Output
           ↓
        Downstream Intelligence
           ↓
        D13

    No trade authority exists here.
    """

    CONTRACT_VERSION = "1.0.0"

    # --------------------------------------------------------
    # RUN
    # --------------------------------------------------------

    def run(
        self,
        context: ThesisContext,
        previous_state: Optional[ThesisState] = None,
        previous_strength: Optional[float] = None,
        previous_direction: Optional[
            ThesisDirection
        ] = None,
    ) -> Dict[str, Any]:

        # ----------------------------------------------------
        # Normalize first
        # ----------------------------------------------------

        context.normalize()

        # ----------------------------------------------------
        # Validate
        # ----------------------------------------------------

        validation = self.validate_context(
            context
        )

        if not validation.valid:

            return {
                "engine":
                    self.ENGINE_NAME,

                "engine_version":
                    self.ENGINE_VERSION,

                "contract_version":
                    self.CONTRACT_VERSION,

                "status":
                    "INVALID",

                "instrument":
                    context.instrument,

                "validation":
                    validation.to_dict(),

                "measurement":
                    None,

                "snapshot":
                    None,

                "transition":
                    None,

                "decision_authority":
                    "D13",

                "trade_issued":
                    False,
            }

        # ----------------------------------------------------
        # Measure
        # ----------------------------------------------------

        measurement = self.measure(
            context
        )

        # ----------------------------------------------------
        # Snapshot
        # ----------------------------------------------------

        snapshot = self.create_snapshot(
            context,
            measurement,
        )

        # ----------------------------------------------------
        # Transition
        # ----------------------------------------------------

        transition = (
            self.calculate_transition(
                context=context,
                measurement=measurement,
                previous_state=previous_state,
                previous_strength=previous_strength,
                previous_direction=previous_direction,
            )
        )

        # ----------------------------------------------------
        # Final structured contract
        # ----------------------------------------------------

        return {

            "engine":
                self.ENGINE_NAME,

            "engine_version":
                self.ENGINE_VERSION,

            "contract_version":
                self.CONTRACT_VERSION,

            "status":
                "VALID",

            "instrument":
                context.instrument,

            "timestamp":
                (
                    context.timestamp.isoformat()
                    if context.timestamp
                    else datetime.now(
                        timezone.utc
                    ).isoformat()
                ),

            "validation":
                validation.to_dict(),

            "measurement":
                measurement.to_dict(),

            "snapshot":
                snapshot.to_dict(),

            "transition":
                transition.to_dict(),

            "upstream": {
                "source_engines":
                    list(context.source_engines),
            },

            "downstream_contract": {

                "thesis_state":
                    measurement.state.value,

                "thesis_trigger":
                    measurement.trigger.value,

                "thesis_strength":
                    measurement.thesis_strength,

                "conviction_score":
                    measurement.conviction_score,

                "failure_risk":
                    measurement.failure_risk,

                "contradiction_pressure":
                    measurement.contradiction_pressure,

                "uncertainty_pressure":
                    measurement.uncertainty_pressure,

                "requires_d13_evaluation":
                    True,
            },

            # ------------------------------------------------
            # HARD AUTHORITY BOUNDARY
            # ------------------------------------------------

            "decision_authority":
                "D13",

            "trade_issued":
                False,

            "order_instruction":
                None,

            "position_instruction":
                None,
        }


# ============================================================
# SAFE FACTORY
# ============================================================

def create_thesis_engine() -> ThesisContractEngine:
    """
    Standard factory for ROBOMLM_PLUS integration.
    """

    return ThesisContractEngine()


# ============================================================
# MODULE EXPORTS
# ============================================================

__all__ = [

    "ThesisSnapshot",

    "ThesisTransition",

    "ThesisValidation",

    "ThesisEngineContractMixin",

    "ThesisContractEngine",

    "create_thesis_engine",
]
```
```python
from typing import (
    Any,
    Dict,
    List,
    Optional,
)

from datetime import (
    datetime,
    timezone,
)

from .thesis_base import (
    ThesisContext,
    ThesisDirection,
    ThesisState,
    ThesisType,
    ThesisTrigger,
    ThesisMeasurement,
    ThesisEvent,
    ThesisEngine,
)
```
```python
# ============================================================
# ROBOMLM_PLUS
# THESIS ENGINE — PART 4
# Downstream Intelligence Handoff / Readiness Layer
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ============================================================
# THESIS READINESS
# ============================================================

@dataclass
class ThesisReadiness:
    """
    Measures whether the current thesis has sufficient
    structural quality for downstream intelligence engines.

    This is NOT an entry signal.
    """

    thesis_ready: bool = False

    pullback_analysis_ready: bool = False

    holdability_analysis_ready: bool = False

    growth_protection_ready: bool = False

    future_rank_ready: bool = False

    evidence_sufficient: bool = False

    structure_sufficient: bool = False

    confirmation_sufficient: bool = False

    contradiction_acceptable: bool = False

    uncertainty_acceptable: bool = False

    reasons: List[str] = field(
        default_factory=list
    )

    blockers: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "thesis_ready":
                self.thesis_ready,

            "pullback_analysis_ready":
                self.pullback_analysis_ready,

            "holdability_analysis_ready":
                self.holdability_analysis_ready,

            "growth_protection_ready":
                self.growth_protection_ready,

            "future_rank_ready":
                self.future_rank_ready,

            "evidence_sufficient":
                self.evidence_sufficient,

            "structure_sufficient":
                self.structure_sufficient,

            "confirmation_sufficient":
                self.confirmation_sufficient,

            "contradiction_acceptable":
                self.contradiction_acceptable,

            "uncertainty_acceptable":
                self.uncertainty_acceptable,

            "reasons":
                list(self.reasons),

            "blockers":
                list(self.blockers),

            "metadata":
                dict(self.metadata),
        }


# ============================================================
# DOWNSTREAM INPUT CONTRACT
# ============================================================

@dataclass
class ThesisDownstreamInput:
    """
    Clean downstream contract.

    Consumers may include:

        Pullback Engine
        Holdability Engine
        Growth Protection Engine
        Future Rank Engine
        D13 Decision Engine

    None of these fields constitute an order instruction.
    """

    instrument: str = ""

    timestamp: Optional[datetime] = None

    direction: ThesisDirection = (
        ThesisDirection.UNKNOWN
    )

    thesis_type: ThesisType = (
        ThesisType.UNKNOWN
    )

    thesis_state: ThesisState = (
        ThesisState.UNKNOWN
    )

    thesis_trigger: ThesisTrigger = (
        ThesisTrigger.UNKNOWN
    )

    thesis_strength: float = 0.0

    conviction_score: float = 0.0

    evidence_strength: float = 0.0

    structure_support: float = 0.0

    participation_support: float = 0.0

    continuation_support: float = 0.0

    contradiction_pressure: float = 0.0

    uncertainty_pressure: float = 0.0

    failure_risk: float = 0.0

    current_price: float = 0.0

    breakout_score: float = 0.0

    accumulation_score: float = 0.0

    distribution_score: float = 0.0

    boundary_strength: float = 0.0

    confirmation_score: float = 0.0

    readiness: Optional[
        ThesisReadiness
    ] = None

    source_engines: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "instrument":
                self.instrument,

            "timestamp": (
                self.timestamp.isoformat()
                if self.timestamp
                else None
            ),

            "direction":
                self.direction.value,

            "thesis_type":
                self.thesis_type.value,

            "thesis_state":
                self.thesis_state.value,

            "thesis_trigger":
                self.thesis_trigger.value,

            "thesis_strength":
                self.thesis_strength,

            "conviction_score":
                self.conviction_score,

            "evidence_strength":
                self.evidence_strength,

            "structure_support":
                self.structure_support,

            "participation_support":
                self.participation_support,

            "continuation_support":
                self.continuation_support,

            "contradiction_pressure":
                self.contradiction_pressure,

            "uncertainty_pressure":
                self.uncertainty_pressure,

            "failure_risk":
                self.failure_risk,

            "current_price":
                self.current_price,

            "breakout_score":
                self.breakout_score,

            "accumulation_score":
                self.accumulation_score,

            "distribution_score":
                self.distribution_score,

            "boundary_strength":
                self.boundary_strength,

            "confirmation_score":
                self.confirmation_score,

            "readiness": (
                self.readiness.to_dict()
                if self.readiness
                else None
            ),

            "source_engines":
                list(self.source_engines),

            "metadata":
                dict(self.metadata),
        }


# ============================================================
# READINESS THRESHOLDS
# ============================================================

class ThesisReadinessEngine:
    """
    Determines whether thesis intelligence is sufficiently
    developed for downstream evaluation.

    These thresholds do NOT authorize trading.
    """

    MIN_EVIDENCE = 50.0

    MIN_STRUCTURE = 50.0

    MIN_CONFIRMATION = 45.0

    MAX_CONTRADICTION = 70.0

    MAX_UNCERTAINTY = 75.0

    MIN_THESIS_STRENGTH = 45.0

    # --------------------------------------------------------
    # EVALUATE
    # --------------------------------------------------------

    def evaluate(
        self,
        context: ThesisContext,
        measurement: ThesisMeasurement,
    ) -> ThesisReadiness:

        readiness = ThesisReadiness()

        # ----------------------------------------------------
        # Evidence
        # ----------------------------------------------------

        if (
            measurement.evidence_strength
            >= self.MIN_EVIDENCE
        ):
            readiness.evidence_sufficient = True
            readiness.reasons.append(
                "Evidence strength is sufficient."
            )
        else:
            readiness.blockers.append(
                "Evidence strength is below readiness threshold."
            )

        # ----------------------------------------------------
        # Structure
        # ----------------------------------------------------

        if (
            measurement.structure_support
            >= self.MIN_STRUCTURE
        ):
            readiness.structure_sufficient = True
            readiness.reasons.append(
                "Structural support is sufficient."
            )
        else:
            readiness.blockers.append(
                "Structural support is insufficient."
            )

        # ----------------------------------------------------
        # Confirmation
        # ----------------------------------------------------

        if (
            context.confirmation_score
            >= self.MIN_CONFIRMATION
        ):
            readiness.confirmation_sufficient = True
            readiness.reasons.append(
                "Confirmation evidence is sufficient."
            )
        else:
            readiness.blockers.append(
                "Confirmation evidence remains weak."
            )

        # ----------------------------------------------------
        # Contradiction
        # ----------------------------------------------------

        if (
            measurement.contradiction_pressure
            <= self.MAX_CONTRADICTION
        ):
            readiness.contradiction_acceptable = True
        else:
            readiness.blockers.append(
                "Contradiction pressure is too high."
            )

        # ----------------------------------------------------
        # Uncertainty
        # ----------------------------------------------------

        if (
            measurement.uncertainty_pressure
            <= self.MAX_UNCERTAINTY
        ):
            readiness.uncertainty_acceptable = True
        else:
            readiness.blockers.append(
                "Uncertainty pressure is too high."
            )

        # ----------------------------------------------------
        # Core thesis readiness
        # ----------------------------------------------------

        readiness.thesis_ready = (
            measurement.thesis_strength
            >= self.MIN_THESIS_STRENGTH
            and readiness.evidence_sufficient
            and readiness.structure_sufficient
            and readiness.confirmation_sufficient
            and readiness.contradiction_acceptable
            and readiness.uncertainty_acceptable
            and measurement.state
            not in (
                ThesisState.FAILING,
                ThesisState.INVALIDATED,
            )
        )

        # ----------------------------------------------------
        # Pullback readiness
        # ----------------------------------------------------

        readiness.pullback_analysis_ready = (
            readiness.thesis_ready
            and measurement.structure_support
            >= 55.0
        )

        # ----------------------------------------------------
        # Holdability readiness
        # ----------------------------------------------------

        readiness.holdability_analysis_ready = (
            readiness.thesis_ready
            and measurement.continuation_support
            >= 55.0
        )

        # ----------------------------------------------------
        # Growth protection readiness
        # ----------------------------------------------------

        readiness.growth_protection_ready = (
            readiness.thesis_ready
            and measurement.failure_risk
            <= 60.0
        )

        # ----------------------------------------------------
        # Future rank readiness
        # ----------------------------------------------------

        readiness.future_rank_ready = (
            readiness.thesis_ready
            and measurement.conviction_score
            >= 50.0
        )

        readiness.metadata = {
            "engine":
                "ThesisReadinessEngine",

            "engine_version":
                "1.0.0",
        }

        return readiness


# ============================================================
# DOWNSTREAM HANDOFF ENGINE
# ============================================================

class ThesisHandoffEngine:
    """
    Converts thesis measurement into a clean downstream
    intelligence contract.

    No trade execution authority.
    """

    ENGINE_NAME = "ThesisHandoffEngine"

    ENGINE_VERSION = "1.0.0"

    CONTRACT_VERSION = "1.0.0"

    # --------------------------------------------------------
    # BUILD INPUT
    # --------------------------------------------------------

    def build(
        self,
        context: ThesisContext,
        measurement: ThesisMeasurement,
        readiness: ThesisReadiness,
    ) -> ThesisDownstreamInput:

        return ThesisDownstreamInput(

            instrument=context.instrument,

            timestamp=(
                context.timestamp
                or datetime.now(timezone.utc)
            ),

            direction=context.direction,

            thesis_type=context.thesis_type,

            thesis_state=measurement.state,

            thesis_trigger=measurement.trigger,

            thesis_strength=(
                measurement.thesis_strength
            ),

            conviction_score=(
                measurement.conviction_score
            ),

            evidence_strength=(
                measurement.evidence_strength
            ),

            structure_support=(
                measurement.structure_support
            ),

            participation_support=(
                measurement.participation_support
            ),

            continuation_support=(
                measurement.continuation_support
            ),

            contradiction_pressure=(
                measurement.contradiction_pressure
            ),

            uncertainty_pressure=(
                measurement.uncertainty_pressure
            ),

            failure_risk=(
                measurement.failure_risk
            ),

            current_price=(
                context.current_price
            ),

            breakout_score=(
                context.breakout_score
            ),

            accumulation_score=(
                context.accumulation_score
            ),

            distribution_score=(
                context.distribution_score
            ),

            boundary_strength=(
                context.boundary_strength
            ),

            confirmation_score=(
                context.confirmation_score
            ),

            readiness=readiness,

            source_engines=(
                list(context.source_engines)
            ),

            metadata={
                "engine":
                    self.ENGINE_NAME,

                "engine_version":
                    self.ENGINE_VERSION,

                "contract_version":
                    self.CONTRACT_VERSION,

                "decision_authority":
                    "D13",
            },
        )


# ============================================================
# PART 4 RESULT
# ============================================================

@dataclass
class ThesisPart4Result:

    status: str = "INVALID"

    instrument: str = ""

    readiness: Optional[
        ThesisReadiness
    ] = None

    downstream_input: Optional[
        ThesisDownstreamInput
    ] = None

    timestamp: Optional[datetime] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {

            "status":
                self.status,

            "instrument":
                self.instrument,

            "readiness": (
                self.readiness.to_dict()
                if self.readiness
                else None
            ),

            "downstream_input": (
                self.downstream_input.to_dict()
                if self.downstream_input
                else None
            ),

            "timestamp": (
                self.timestamp.isoformat()
                if self.timestamp
                else None
            ),

            "metadata":
                dict(self.metadata),
        }


# ============================================================
# PART 4 ORCHESTRATOR
# ============================================================

class ThesisPart4Engine:
    """
    Part 4 orchestration layer.

    Flow:

        ThesisContext
              ↓
        ThesisMeasurement
              ↓
        Readiness Evaluation
              ↓
        Downstream Contract
              ↓
        Pullback / Holdability /
        Growth Protection / Future Rank
              ↓
        D13

    IMPORTANT:
        This engine does not create a trade.
    """

    ENGINE_NAME = "ThesisPart4Engine"

    ENGINE_VERSION = "1.0.0"

    CONTRACT_VERSION = "1.0.0"

    def __init__(
        self,
        readiness_engine:
            Optional[
                ThesisReadinessEngine
            ] = None,

        handoff_engine:
            Optional[
                ThesisHandoffEngine
            ] = None,
    ):

        self.readiness_engine = (
            readiness_engine
            or ThesisReadinessEngine()
        )

        self.handoff_engine = (
            handoff_engine
            or ThesisHandoffEngine()
        )

    # --------------------------------------------------------
    # RUN
    # --------------------------------------------------------

    def run(
        self,
        context: ThesisContext,
        measurement: ThesisMeasurement,
    ) -> ThesisPart4Result:

        context.normalize()

        readiness = (
            self.readiness_engine.evaluate(
                context=context,
                measurement=measurement,
            )
        )

        downstream_input = (
            self.handoff_engine.build(
                context=context,
                measurement=measurement,
                readiness=readiness,
            )
        )

        return ThesisPart4Result(

            status="READY"
            if readiness.thesis_ready
            else "NOT_READY",

            instrument=context.instrument,

            readiness=readiness,

            downstream_input=downstream_input,

            timestamp=(
                context.timestamp
                or datetime.now(timezone.utc)
            ),

            metadata={
                "engine":
                    self.ENGINE_NAME,

                "engine_version":
                    self.ENGINE_VERSION,

                "contract_version":
                    self.CONTRACT_VERSION,

                "decision_authority":
                    "D13",

                "trade_issued":
                    False,

                "order_instruction":
                    None,

                "position_instruction":
                    None,
            },
        )


# ============================================================
# SAFE FACTORY
# ============================================================

def create_thesis_part4_engine() -> ThesisPart4Engine:

    return ThesisPart4Engine()


# ============================================================
# MODULE EXPORTS
# ============================================================

__all__ = [

    "ThesisReadiness",

    "ThesisDownstreamInput",

    "ThesisReadinessEngine",

    "ThesisHandoffEngine",

    "ThesisPart4Result",

    "ThesisPart4Engine",

    "create_thesis_part4_engine",
]
```
# ============================================================
# ROBOMLM_PLUS
# THESIS ENGINE — PART 5
# Thesis Lifecycle / History / Transition / Delta Audit Layer
# ============================================================
#
# PURPOSE:
#     Track how a thesis evolves over time.
#
# FLOW:
#
#     Current Thesis
#          ↓
#     Previous Thesis
#          ↓
#     Delta Analysis
#          ↓
#     State Transition
#          ↓
#     Strength Evolution
#          ↓
#     Contradiction Evolution
#          ↓
#     Thesis Lifecycle
#          ↓
#     Audit Record
#          ↓
#     Downstream Intelligence
#
# IMPORTANT:
#     This layer does NOT issue trades.
#
#     D13 remains the final decision authority.
#
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ============================================================
# LIFECYCLE STATUS
# ============================================================

class ThesisLifecycleStatus(str, Enum):

    NEW = "NEW"

    DEVELOPING = "DEVELOPING"

    STRENGTHENING = "STRENGTHENING"

    STABLE = "STABLE"

    WEAKENING = "WEAKENING"

    FAILING = "FAILING"

    INVALIDATED = "INVALIDATED"

    UNKNOWN = "UNKNOWN"


# ============================================================
# THESIS DELTA
# ============================================================

@dataclass
class ThesisDelta:

    previous_strength: float = 0.0

    current_strength: float = 0.0

    strength_delta: float = 0.0

    previous_evidence: float = 0.0

    current_evidence: float = 0.0

    evidence_delta: float = 0.0

    previous_structure: float = 0.0

    current_structure: float = 0.0

    structure_delta: float = 0.0

    previous_participation: float = 0.0

    current_participation: float = 0.0

    participation_delta: float = 0.0

    previous_contradiction: float = 0.0

    current_contradiction: float = 0.0

    contradiction_delta: float = 0.0

    previous_uncertainty: float = 0.0

    current_uncertainty: float = 0.0

    uncertainty_delta: float = 0.0

    previous_failure_risk: float = 0.0

    current_failure_risk: float = 0.0

    failure_risk_delta: float = 0.0

    state_changed: bool = False

    previous_state: ThesisState = ThesisState.UNKNOWN

    current_state: ThesisState = ThesisState.UNKNOWN

    direction_changed: bool = False

    previous_direction: ThesisDirection = (
        ThesisDirection.UNKNOWN
    )

    current_direction: ThesisDirection = (
        ThesisDirection.UNKNOWN
    )

    material_change: bool = False

    reasons: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self):

        return {

            "previous_strength":
                self.previous_strength,

            "current_strength":
                self.current_strength,

            "strength_delta":
                self.strength_delta,

            "previous_evidence":
                self.previous_evidence,

            "current_evidence":
                self.current_evidence,

            "evidence_delta":
                self.evidence_delta,

            "previous_structure":
                self.previous_structure,

            "current_structure":
                self.current_structure,

            "structure_delta":
                self.structure_delta,

            "previous_participation":
                self.previous_participation,

            "current_participation":
                self.current_participation,

            "participation_delta":
                self.participation_delta,

            "previous_contradiction":
                self.previous_contradiction,

            "current_contradiction":
                self.current_contradiction,

            "contradiction_delta":
                self.contradiction_delta,

            "previous_uncertainty":
                self.previous_uncertainty,

            "current_uncertainty":
                self.current_uncertainty,

            "uncertainty_delta":
                self.uncertainty_delta,

            "previous_failure_risk":
                self.previous_failure_risk,

            "current_failure_risk":
                self.current_failure_risk,

            "failure_risk_delta":
                self.failure_risk_delta,

            "state_changed":
                self.state_changed,

            "previous_state":
                self.previous_state.value,

            "current_state":
                self.current_state.value,

            "direction_changed":
                self.direction_changed,

            "previous_direction":
                self.previous_direction.value,

            "current_direction":
                self.current_direction.value,

            "material_change":
                self.material_change,

            "reasons":
                list(self.reasons),

            "metadata":
                dict(self.metadata),
        }


# ============================================================
# LIFECYCLE EVENT
# ============================================================

@dataclass
class ThesisLifecycleEvent:

    event_id: str = ""

    timestamp: Optional[datetime] = None

    instrument: str = ""

    lifecycle_status: ThesisLifecycleStatus = (
        ThesisLifecycleStatus.UNKNOWN
    )

    previous_state: ThesisState = (
        ThesisState.UNKNOWN
    )

    current_state: ThesisState = (
        ThesisState.UNKNOWN
    )

    previous_strength: float = 0.0

    current_strength: float = 0.0

    strength_delta: float = 0.0

    material: bool = False

    reason: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self):

        return {

            "event_id":
                self.event_id,

            "timestamp":
                (
                    self.timestamp.isoformat()
                    if self.timestamp
                    else None
                ),

            "instrument":
                self.instrument,

            "lifecycle_status":
                self.lifecycle_status.value,

            "previous_state":
                self.previous_state.value,

            "current_state":
                self.current_state.value,

            "previous_strength":
                self.previous_strength,

            "current_strength":
                self.current_strength,

            "strength_delta":
                self.strength_delta,

            "material":
                self.material,

            "reason":
                self.reason,

            "metadata":
                dict(self.metadata),
        }


# ============================================================
# THESIS HISTORY
# ============================================================

@dataclass
class ThesisHistory:

    instrument: str = ""

    first_seen: Optional[datetime] = None

    last_updated: Optional[datetime] = None

    observation_count: int = 0

    current_state: ThesisState = (
        ThesisState.UNKNOWN
    )

    current_strength: float = 0.0

    current_direction: ThesisDirection = (
        ThesisDirection.UNKNOWN
    )

    lifecycle_status: ThesisLifecycleStatus = (
        ThesisLifecycleStatus.UNKNOWN
    )

    strongest_strength: float = 0.0

    weakest_strength: float = 0.0

    strengthening_count: int = 0

    weakening_count: int = 0

    invalidation_count: int = 0

    material_change_count: int = 0

    events: List[ThesisLifecycleEvent] = field(
        default_factory=list
    )

    snapshots: List[ThesisSnapshot] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self):

        return {

            "instrument":
                self.instrument,

            "first_seen":
                (
                    self.first_seen.isoformat()
                    if self.first_seen
                    else None
                ),

            "last_updated":
                (
                    self.last_updated.isoformat()
                    if self.last_updated
                    else None
                ),

            "observation_count":
                self.observation_count,

            "current_state":
                self.current_state.value,

            "current_strength":
                self.current_strength,

            "current_direction":
                self.current_direction.value,

            "lifecycle_status":
                self.lifecycle_status.value,

            "strongest_strength":
                self.strongest_strength,

            "weakest_strength":
                self.weakest_strength,

            "strengthening_count":
                self.strengthening_count,

            "weakening_count":
                self.weakening_count,

            "invalidation_count":
                self.invalidation_count,

            "material_change_count":
                self.material_change_count,

            "events":
                [
                    event.to_dict()
                    for event in self.events
                ],

            "snapshots":
                [
                    snapshot.to_dict()
                    for snapshot in self.snapshots
                ],

            "metadata":
                dict(self.metadata),
        }


# ============================================================
# LIFECYCLE ENGINE
# ============================================================

class ThesisLifecycleEngine:

    ENGINE_NAME = (
        "ThesisLifecycleEngine"
    )

    ENGINE_VERSION = (
        "1.0.0"
    )

    # --------------------------------------------------------
    # DELTA CALCULATION
    # --------------------------------------------------------

    def calculate_delta(
        self,
        previous: ThesisMeasurement,
        current: ThesisMeasurement,
        previous_context: ThesisContext,
        current_context: ThesisContext,
    ) -> ThesisDelta:

        delta = ThesisDelta()

        delta.previous_strength = float(
            previous.thesis_strength
        )

        delta.current_strength = float(
            current.thesis_strength
        )

        delta.strength_delta = (
            delta.current_strength
            - delta.previous_strength
        )

        delta.previous_evidence = float(
            previous.evidence_strength
        )

        delta.current_evidence = float(
            current.evidence_strength
        )

        delta.evidence_delta = (
            delta.current_evidence
            - delta.previous_evidence
        )

        delta.previous_structure = float(
            previous.structure_support
        )

        delta.current_structure = float(
            current.structure_support
        )

        delta.structure_delta = (
            delta.current_structure
            - delta.previous_structure
        )

        delta.previous_participation = float(
            previous.participation_support
        )

        delta.current_participation = float(
            current.participation_support
        )

        delta.participation_delta = (
            delta.current_participation
            - delta.previous_participation
        )

        delta.previous_contradiction = float(
            previous.contradiction_pressure
        )

        delta.current_contradiction = float(
            current.contradiction_pressure
        )

        delta.contradiction_delta = (
            delta.current_contradiction
            - delta.previous_contradiction
        )

        delta.previous_uncertainty = float(
            previous.uncertainty_pressure
        )

        delta.current_uncertainty = float(
            current.uncertainty_pressure
        )

        delta.uncertainty_delta = (
            delta.current_uncertainty
            - delta.previous_uncertainty
        )

        delta.previous_failure_risk = float(
            previous.failure_risk
        )

        delta.current_failure_risk = float(
            current.failure_risk
        )

        delta.failure_risk_delta = (
            delta.current_failure_risk
            - delta.previous_failure_risk
        )

        delta.previous_state = (
            previous.state
        )

        delta.current_state = (
            current.state
        )

        delta.state_changed = (
            previous.state
            != current.state
        )

        delta.previous_direction = (
            previous_context.direction
        )

        delta.current_direction = (
            current_context.direction
        )

        delta.direction_changed = (
            previous_context.direction
            != current_context.direction
        )

        reasons = []

        if delta.strength_delta > 0:
            reasons.append(
                "Thesis strength increased."
            )

        elif delta.strength_delta < 0:
            reasons.append(
                "Thesis strength decreased."
            )

        if delta.evidence_delta > 0:
            reasons.append(
                "Supporting evidence increased."
            )

        elif delta.evidence_delta < 0:
            reasons.append(
                "Supporting evidence decreased."
            )

        if delta.structure_delta > 0:
            reasons.append(
                "Structure support increased."
            )

        elif delta.structure_delta < 0:
            reasons.append(
                "Structure support decreased."
            )

        if delta.contradiction_delta > 0:
            reasons.append(
                "Contradiction pressure increased."
            )

        elif delta.contradiction_delta < 0:
            reasons.append(
                "Contradiction pressure decreased."
            )

        if delta.uncertainty_delta > 0:
            reasons.append(
                "Uncertainty increased."
            )

        elif delta.uncertainty_delta < 0:
            reasons.append(
                "Uncertainty decreased."
            )

        if delta.failure_risk_delta > 0:
            reasons.append(
                "Failure risk increased."
            )

        elif delta.failure_risk_delta < 0:
            reasons.append(
                "Failure risk decreased."
            )

        if delta.state_changed:
            reasons.append(
                "Thesis state changed."
            )

        if delta.direction_changed:
            reasons.append(
                "Thesis direction changed."
            )

        delta.reasons = reasons

        # ----------------------------------------------------
        # Material change
        #
        # Deliberately based on state/direction changes and
        # explicit measurement movement, not trade logic.
        # ----------------------------------------------------

        delta.material_change = (
            delta.state_changed
            or delta.direction_changed
            or abs(delta.strength_delta) >= 10.0
            or abs(delta.contradiction_delta) >= 10.0
            or abs(delta.failure_risk_delta) >= 10.0
        )

        return delta

    # --------------------------------------------------------
    # LIFECYCLE CLASSIFICATION
    # --------------------------------------------------------

    def classify_lifecycle(
        self,
        delta: ThesisDelta,
        current: ThesisMeasurement,
    ) -> ThesisLifecycleStatus:

        if current.state == ThesisState.INVALIDATED:

            return (
                ThesisLifecycleStatus.INVALIDATED
            )

        if current.state == ThesisState.FAILING:

            return (
                ThesisLifecycleStatus.FAILING
            )

        if delta.strength_delta > 0:

            return (
                ThesisLifecycleStatus.STRENGTHENING
            )

        if delta.strength_delta < 0:

            return (
                ThesisLifecycleStatus.WEAKENING
            )

        return ThesisLifecycleStatus.STABLE

    # --------------------------------------------------------
    # REASON GENERATION
    # --------------------------------------------------------

    def build_lifecycle_reason(
        self,
        lifecycle: ThesisLifecycleStatus,
        delta: ThesisDelta,
    ) -> str:

        if lifecycle == (
            ThesisLifecycleStatus.STRENGTHENING
        ):

            return (
                "Thesis is strengthening based "
                "on the latest measurement delta."
            )

        if lifecycle == (
            ThesisLifecycleStatus.WEAKENING
        ):

            return (
                "Thesis is weakening based "
                "on the latest measurement delta."
            )

        if lifecycle == (
            ThesisLifecycleStatus.FAILING
        ):

            return (
                "Thesis is in a failing state."
            )

        if lifecycle == (
            ThesisLifecycleStatus.INVALIDATED
        ):

            return (
                "Thesis has been invalidated."
            )

        return (
            "Thesis measurements are currently stable."
        )

    # --------------------------------------------------------
    # EVENT
    # --------------------------------------------------------

    def build_event(
        self,
        context: ThesisContext,
        measurement: ThesisMeasurement,
        delta: ThesisDelta,
        lifecycle: ThesisLifecycleStatus,
    ) -> ThesisLifecycleEvent:

        timestamp = (
            context.timestamp
            or datetime.now(timezone.utc)
        )

        event_id = (
            f"THESIS-LIFE-"
            f"{context.instrument}-"
            f"{timestamp.strftime('%Y%m%d%H%M%S%f')}"
        )

        return ThesisLifecycleEvent(

            event_id=event_id,

            timestamp=timestamp,

            instrument=context.instrument,

            lifecycle_status=lifecycle,

            previous_state=(
                delta.previous_state
            ),

            current_state=(
                delta.current_state
            ),

            previous_strength=(
                delta.previous_strength
            ),

            current_strength=(
                delta.current_strength
            ),

            strength_delta=(
                delta.strength_delta
            ),

            material=(
                delta.material_change
            ),

            reason=(
                self.build_lifecycle_reason(
                    lifecycle,
                    delta,
                )
            ),

            metadata={
                "engine":
                    self.ENGINE_NAME,

                "engine_version":
                    self.ENGINE_VERSION,

                "decision_authority":
                    "D13",

                "trade_issued":
                    False,
            },
        )

    # --------------------------------------------------------
    # HISTORY UPDATE
    # --------------------------------------------------------

    def update_history(
        self,
        history: ThesisHistory,
        snapshot: ThesisSnapshot,
        event: ThesisLifecycleEvent,
    ) -> ThesisHistory:

        now = (
            snapshot.timestamp
            or datetime.now(timezone.utc)
        )

        if history.first_seen is None:

            history.first_seen = now

        history.last_updated = now

        history.observation_count += 1

        history.current_state = (
            snapshot.state
        )

        history.current_strength = (
            snapshot.thesis_strength
        )

        history.current_direction = (
            snapshot.direction
        )

        history.lifecycle_status = (
            event.lifecycle_status
        )

        if history.observation_count == 1:

            history.strongest_strength = (
                snapshot.thesis_strength
            )

            history.weakest_strength = (
                snapshot.thesis_strength
            )

        else:

            history.strongest_strength = max(
                history.strongest_strength,
                snapshot.thesis_strength,
            )

            history.weakest_strength = min(
                history.weakest_strength,
                snapshot.thesis_strength,
            )

        if (
            event.lifecycle_status
            == ThesisLifecycleStatus.STRENGTHENING
        ):

            history.strengthening_count += 1

        elif (
            event.lifecycle_status
            == ThesisLifecycleStatus.WEAKENING
        ):

            history.weakening_count += 1

        elif (
            event.lifecycle_status
            == ThesisLifecycleStatus.INVALIDATED
        ):

            history.invalidation_count += 1

        if event.material:

            history.material_change_count += 1

        history.events.append(event)

        history.snapshots.append(snapshot)

        return history


# ============================================================
# PART 5 RESULT
# ============================================================

@dataclass
class ThesisPart5Result:

    instrument: str = ""

    timestamp: Optional[datetime] = None

    snapshot: Optional[ThesisSnapshot] = None

    measurement: Optional[ThesisMeasurement] = None

    delta: Optional[ThesisDelta] = None

    lifecycle_status: ThesisLifecycleStatus = (
        ThesisLifecycleStatus.UNKNOWN
    )

    lifecycle_event: Optional[
        ThesisLifecycleEvent
    ] = None

    history: Optional[ThesisHistory] = None

    downstream_contract: Dict[str, Any] = field(
        default_factory=dict
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self):

        return {

            "instrument":
                self.instrument,

            "timestamp":
                (
                    self.timestamp.isoformat()
                    if self.timestamp
                    else None
                ),

            "snapshot":
                (
                    self.snapshot.to_dict()
                    if self.snapshot
                    else None
                ),

            "measurement":
                (
                    self.measurement.to_dict()
                    if self.measurement
                    else None
                ),

            "delta":
                (
                    self.delta.to_dict()
                    if self.delta
                    else None
                ),

            "lifecycle_status":
                self.lifecycle_status.value,

            "lifecycle_event":
                (
                    self.lifecycle_event.to_dict()
                    if self.lifecycle_event
                    else None
                ),

            "history":
                (
                    self.history.to_dict()
                    if self.history
                    else None
                ),

            "downstream_contract":
                dict(self.downstream_contract),

            "metadata":
                dict(self.metadata),
        }


# ============================================================
# PART 5 ENGINE
# ============================================================

class ThesisPart5Engine:

    ENGINE_NAME = (
        "ThesisPart5Engine"
    )

    ENGINE_VERSION = (
        "1.0.0"
    )

    def __init__(self):

        self.lifecycle_engine = (
            ThesisLifecycleEngine()
        )

        self.history_store: Dict[
            str,
            ThesisHistory,
        ] = {}

    # --------------------------------------------------------
    # PROCESS
    # --------------------------------------------------------

    def process(
        self,
        context: ThesisContext,
        measurement: ThesisMeasurement,
        snapshot: ThesisSnapshot,
    ) -> ThesisPart5Result:

        context.normalize()

        instrument = (
            context.instrument
            or snapshot.instrument
        )

        timestamp = (
            context.timestamp
            or snapshot.timestamp
            or datetime.now(timezone.utc)
        )

        history = (
            self.history_store.get(
                instrument
            )
        )

        # ----------------------------------------------------
        # First observation
        # ----------------------------------------------------

        if history is None:

            history = ThesisHistory(
                instrument=instrument
            )

            previous_measurement = (
                ThesisMeasurement(
                    thesis_strength=0.0,
                    evidence_strength=0.0,
                    structure_support=0.0,
                    participation_support=0.0,
                    continuation_support=0.0,
                    conviction_score=0.0,
                    contradiction_pressure=0.0,
                    uncertainty_pressure=0.0,
                    failure_risk=0.0,
                    state=ThesisState.UNKNOWN,
                    trigger=ThesisTrigger.UNKNOWN,
                )
            )

            previous_context = ThesisContext(
                instrument=instrument,
                direction=(
                    ThesisDirection.UNKNOWN
                ),
            )

        else:

            if history.snapshots:

                previous_snapshot = (
                    history.snapshots[-1]
                )

                previous_context = ThesisContext(
                    instrument=(
                        previous_snapshot.instrument
                    ),

                    timestamp=(
                        previous_snapshot.timestamp
                    ),

                    direction=(
                        previous_snapshot.direction
                    ),

                    thesis_type=(
                        previous_snapshot.thesis_type
                    ),

                    current_price=(
                        previous_snapshot.current_price
                    ),
                )

            else:

                previous_context = ThesisContext(
                    instrument=instrument,
                    direction=(
                        history.current_direction
                    ),
                )

            if history.events:

                previous_event = (
                    history.events[-1]
                )

                previous_measurement = (
                    ThesisMeasurement(
                        thesis_strength=(
                            previous_event.current_strength
                        ),

                        state=(
                            previous_event.current_state
                        ),
                    )
                )

            else:

                previous_measurement = (
                    ThesisMeasurement(
                        thesis_strength=(
                            history.current_strength
                        ),

                        state=(
                            history.current_state
                        ),
                    )
                )

        # ----------------------------------------------------
        # Delta
        # ----------------------------------------------------

        delta = (
            self.lifecycle_engine.calculate_delta(
                previous=previous_measurement,

                current=measurement,

                previous_context=previous_context,

                current_context=context,
            )
        )

        # ----------------------------------------------------
        # Lifecycle
        # ----------------------------------------------------

        if history.observation_count == 0:

            lifecycle = (
                ThesisLifecycleStatus.NEW
            )

        else:

            lifecycle = (
                self.lifecycle_engine
                .classify_lifecycle(
                    delta,
                    measurement,
                )
            )

        # ----------------------------------------------------
        # Event
        # ----------------------------------------------------

        event = (
            self.lifecycle_engine.build_event(
                context=context,

                measurement=measurement,

                delta=delta,

                lifecycle=lifecycle,
            )
        )

        # ----------------------------------------------------
        # History
        # ----------------------------------------------------

        history = (
            self.lifecycle_engine.update_history(
                history=history,

                snapshot=snapshot,

                event=event,
            )
        )

        self.history_store[instrument] = (
            history
        )

        # ----------------------------------------------------
        # Downstream contract
        # ----------------------------------------------------

        downstream_contract = {

            "instrument":
                instrument,

            "thesis_state":
                measurement.state.value,

            "thesis_strength":
                measurement.thesis_strength,

            "lifecycle_status":
                lifecycle.value,

            "strength_delta":
                delta.strength_delta,

            "material_change":
                delta.material_change,

            "direction":
                context.direction.value,

            "decision_authority":
                "D13",

            "trade_issued":
                False,

            "order_created":
                False,

            "position_created":
                False,

            "execution_authority":
                False,
        }

        return ThesisPart5Result(

            instrument=instrument,

            timestamp=timestamp,

            snapshot=snapshot,

            measurement=measurement,

            delta=delta,

            lifecycle_status=lifecycle,

            lifecycle_event=event,

            history=history,

            downstream_contract=(
                downstream_contract
            ),

            metadata={

                "engine":
                    self.ENGINE_NAME,

                "engine_version":
                    self.ENGINE_VERSION,

                "decision_authority":
                    "D13",

                "trade_issued":
                    False,
            },
        )

    # --------------------------------------------------------
    # HISTORY ACCESS
    # --------------------------------------------------------

    def get_history(
        self,
        instrument: str,
    ) -> Optional[ThesisHistory]:

        return self.history_store.get(
            instrument
        )

    # --------------------------------------------------------
    # CLEAR HISTORY
    # --------------------------------------------------------

    def clear_history(
        self,
        instrument: Optional[str] = None,
    ):

        if instrument is None:

            self.history_store.clear()

        else:

            self.history_store.pop(
                instrument,
                None,
            )


# ============================================================
# FACTORY
# ============================================================

def create_thesis_part5_engine():

    return ThesisPart5Engine()


# ============================================================
# EXPORTS
# ============================================================

__all__ = [

    "ThesisLifecycleStatus",

    "ThesisDelta",

    "ThesisLifecycleEvent",

    "ThesisHistory",

    "ThesisLifecycleEngine",

    "ThesisPart5Result",

    "ThesisPart5Engine",

    "create_thesis_part5_engine",
]