# ============================================================
# ROBOMLM_PLUS
# HOLDABILITY ENGINE — PART 1
# ============================================================
# Purpose:
#   Measure how strongly an active trade thesis can continue
#   to be held based on market support, structure, participation,
#   liquidity, relationship, regime, continuation and adverse
#   evidence.
#
# IMPORTANT:
#   - This is an upstream intelligence engine.
#   - It does NOT make final BUY/SELL/EXIT decisions.
#   - D13 remains the final decision authority.
#   - Current thresholds are engineering baselines only.
#   - They must be validated against real market outcomes.
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


# ============================================================
# ENUMS
# ============================================================

class HoldabilityDirection(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    CALL = "CALL"
    PUT = "PUT"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"


class HoldabilityState(str, Enum):
    STRONG = "STRONG"
    HEALTHY = "HEALTHY"
    WATCH = "WATCH"
    WEAKENING = "WEAKENING"
    DAMAGED = "DAMAGED"
    INVALIDATED = "INVALIDATED"
    EXHAUSTED = "EXHAUSTED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    UNKNOWN = "UNKNOWN"


class HoldabilityTrigger(str, Enum):
    NONE = "NONE"
    CONTINUATION_SUPPORT = "CONTINUATION_SUPPORT"
    STRUCTURE_SUPPORT = "STRUCTURE_SUPPORT"
    PARTICIPATION_SUPPORT = "PARTICIPATION_SUPPORT"
    LIQUIDITY_SUPPORT = "LIQUIDITY_SUPPORT"
    RELATIONSHIP_SUPPORT = "RELATIONSHIP_SUPPORT"
    REGIME_SUPPORT = "REGIME_SUPPORT"
    THESIS_WEAKENING = "THESIS_WEAKENING"
    ANTI_EVIDENCE = "ANTI_EVIDENCE"
    OPPOSITE_PRESSURE = "OPPOSITE_PRESSURE"
    PARTICIPATION_DECAY = "PARTICIPATION_DECAY"
    LIQUIDITY_DETERIORATION = "LIQUIDITY_DETERIORATION"
    STRUCTURE_BREAK = "STRUCTURE_BREAK"
    EXHAUSTION = "EXHAUSTION"
    INVALIDATION = "INVALIDATION"
    UNKNOWN = "UNKNOWN"


# ============================================================
# CONTEXT
# ============================================================

@dataclass
class HoldabilityContext:
    """
    Normalized upstream context used by the Holdability Engine.

    Scores are expected on a 0–100 scale unless otherwise noted.
    """

    instrument: str = ""

    timestamp: Optional[datetime] = None

    direction: HoldabilityDirection = HoldabilityDirection.UNKNOWN

    current_price: float = 0.0
    entry_price: float = 0.0
    target_price: float = 0.0
    invalidation_price: float = 0.0

    # Core thesis support
    thesis_score: float = 0.0
    evidence_score: float = 0.0
    structure_score: float = 0.0
    participation_score: float = 0.0
    liquidity_score: float = 0.0
    relationship_score: float = 0.0
    regime_score: float = 0.0

    # Continuation / momentum
    continuation_score: float = 0.0
    momentum_score: float = 0.0

    # Opposing / damaging information
    anti_evidence_score: float = 0.0
    opposing_pressure_score: float = 0.0
    exhaustion_score: float = 0.0

    # Optional volatility information
    volatility_score: float = 0.0

    # Explicit thesis state
    thesis_intact: bool = True
    anti_evidence_detected: bool = False
    exhaustion_detected: bool = False
    structure_broken: bool = False

    metadata: Dict[str, Any] = field(default_factory=dict)

    def normalize(self) -> "HoldabilityContext":
        """
        Clamp normalized score fields into 0–100.
        """

        score_fields = [
            "thesis_score",
            "evidence_score",
            "structure_score",
            "participation_score",
            "liquidity_score",
            "relationship_score",
            "regime_score",
            "continuation_score",
            "momentum_score",
            "anti_evidence_score",
            "opposing_pressure_score",
            "exhaustion_score",
            "volatility_score",
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

        return self

    def to_dict(self) -> Dict[str, Any]:
        return {
            "instrument": self.instrument,
            "timestamp": (
                self.timestamp.isoformat()
                if isinstance(self.timestamp, datetime)
                else self.timestamp
            ),
            "direction": self.direction.value
            if isinstance(self.direction, HoldabilityDirection)
            else str(self.direction),
            "current_price": self.current_price,
            "entry_price": self.entry_price,
            "target_price": self.target_price,
            "invalidation_price": self.invalidation_price,
            "thesis_score": self.thesis_score,
            "evidence_score": self.evidence_score,
            "structure_score": self.structure_score,
            "participation_score": self.participation_score,
            "liquidity_score": self.liquidity_score,
            "relationship_score": self.relationship_score,
            "regime_score": self.regime_score,
            "continuation_score": self.continuation_score,
            "momentum_score": self.momentum_score,
            "anti_evidence_score": self.anti_evidence_score,
            "opposing_pressure_score": self.opposing_pressure_score,
            "exhaustion_score": self.exhaustion_score,
            "volatility_score": self.volatility_score,
            "thesis_intact": self.thesis_intact,
            "anti_evidence_detected": self.anti_evidence_detected,
            "exhaustion_detected": self.exhaustion_detected,
            "structure_broken": self.structure_broken,
            "metadata": dict(self.metadata),
        }


# ============================================================
# MEASUREMENT
# ============================================================

@dataclass
class HoldabilityMeasurement:
    """
    Raw calculated measurements produced by the engine.
    """

    current_price: float = 0.0
    entry_price: float = 0.0
    target_price: float = 0.0
    invalidation_price: float = 0.0

    realized_move_pct: float = 0.0
    favorable_move_pct: float = 0.0
    adverse_move_pct: float = 0.0

    target_progress_pct: float = 0.0
    invalidation_progress_pct: float = 0.0

    market_support_score: float = 0.0
    continuation_score: float = 0.0

    thesis_pressure: float = 0.0
    anti_evidence_pressure: float = 0.0
    opposing_pressure: float = 0.0
    exhaustion_pressure: float = 0.0

    holdability_score: float = 0.0

    state: HoldabilityState = HoldabilityState.UNKNOWN
    trigger: HoldabilityTrigger = HoldabilityTrigger.NONE

    reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def normalize(self) -> "HoldabilityMeasurement":

        score_fields = [
            "target_progress_pct",
            "invalidation_progress_pct",
            "market_support_score",
            "continuation_score",
            "thesis_pressure",
            "anti_evidence_pressure",
            "opposing_pressure",
            "exhaustion_pressure",
            "holdability_score",
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

        return self

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_price": self.current_price,
            "entry_price": self.entry_price,
            "target_price": self.target_price,
            "invalidation_price": self.invalidation_price,
            "realized_move_pct": self.realized_move_pct,
            "favorable_move_pct": self.favorable_move_pct,
            "adverse_move_pct": self.adverse_move_pct,
            "target_progress_pct": self.target_progress_pct,
            "invalidation_progress_pct": self.invalidation_progress_pct,
            "market_support_score": self.market_support_score,
            "continuation_score": self.continuation_score,
            "thesis_pressure": self.thesis_pressure,
            "anti_evidence_pressure": self.anti_evidence_pressure,
            "opposing_pressure": self.opposing_pressure,
            "exhaustion_pressure": self.exhaustion_pressure,
            "holdability_score": self.holdability_score,
            "state": self.state.value
            if isinstance(self.state, HoldabilityState)
            else str(self.state),
            "trigger": self.trigger.value
            if isinstance(self.trigger, HoldabilityTrigger)
            else str(self.trigger),
            "reasons": list(self.reasons),
            "warnings": list(self.warnings),
            "metadata": dict(self.metadata),
        }


# ============================================================
# EVENT
# ============================================================

@dataclass
class HoldabilityEvent:
    """
    Event generated when the holdability condition materially changes.
    """

    event_id: str = ""

    timestamp: Optional[datetime] = None

    instrument: str = ""

    direction: HoldabilityDirection = HoldabilityDirection.UNKNOWN

    state: HoldabilityState = HoldabilityState.UNKNOWN

    trigger: HoldabilityTrigger = HoldabilityTrigger.NONE

    current_price: float = 0.0
    holdability_score: float = 0.0

    thesis_intact: bool = True
    anti_evidence_detected: bool = False
    exhaustion_detected: bool = False

    material: bool = False

    reason: str = ""

    evidence_ids: List[str] = field(default_factory=list)
    source_engines: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "timestamp": (
                self.timestamp.isoformat()
                if isinstance(self.timestamp, datetime)
                else self.timestamp
            ),
            "instrument": self.instrument,
            "direction": self.direction.value
            if isinstance(self.direction, HoldabilityDirection)
            else str(self.direction),
            "state": self.state.value
            if isinstance(self.state, HoldabilityState)
            else str(self.state),
            "trigger": self.trigger.value
            if isinstance(self.trigger, HoldabilityTrigger)
            else str(self.trigger),
            "current_price": self.current_price,
            "holdability_score": self.holdability_score,
            "thesis_intact": self.thesis_intact,
            "anti_evidence_detected": self.anti_evidence_detected,
            "exhaustion_detected": self.exhaustion_detected,
            "material": self.material,
            "reason": self.reason,
            "evidence_ids": list(self.evidence_ids),
            "source_engines": list(self.source_engines),
            "metadata": dict(self.metadata),
        }


# ============================================================
# ENGINE
# ============================================================

class HoldabilityEngine:
    """
    Holdability measurement engine.

    Role:
        Determine whether an already identified trade thesis is
        currently supported strongly enough to remain holdable.

    Authority:
        UPSTREAM INTELLIGENCE ONLY.

        This engine does not:
            - issue final BUY
            - issue final SELL
            - execute orders
            - force an exit
            - replace D13

    Current values are engineering baselines and require validation.
    """

    ENGINE_NAME = "HoldabilityEngine"
    ENGINE_VERSION = "1.0.0"

    # Initial engineering baselines only.
    STRONG_THRESHOLD = 74.0
    HEALTHY_THRESHOLD = 60.0
    WATCH_THRESHOLD = 45.0
    WEAKENING_THRESHOLD = 35.0

    MATERIAL_ANTI_EVIDENCE = 50.0
    MATERIAL_OPPOSING_PRESSURE = 50.0
    MATERIAL_EXHAUSTION = 60.0

    def __init__(
        self,
        strong_threshold: float = STRONG_THRESHOLD,
        healthy_threshold: float = HEALTHY_THRESHOLD,
        watch_threshold: float = WATCH_THRESHOLD,
        weakening_threshold: float = WEAKENING_THRESHOLD,
    ):
        self.strong_threshold = float(strong_threshold)
        self.healthy_threshold = float(healthy_threshold)
        self.watch_threshold = float(watch_threshold)
        self.weakening_threshold = float(weakening_threshold)

    # --------------------------------------------------------
    # BASIC HELPERS
    # --------------------------------------------------------

    @staticmethod
    def _safe(value: Any, default: float = 0.0) -> float:
        try:
            value = float(value)
            if value != value:
                return default
            return value
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _clamp(
        value: float,
        minimum: float = 0.0,
        maximum: float = 100.0,
    ) -> float:
        return max(minimum, min(maximum, value))

    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(timezone.utc)

    # --------------------------------------------------------
    # DIRECTIONAL MOVE
    # --------------------------------------------------------

    def calculate_directional_move(
        self,
        context: HoldabilityContext,
    ) -> float:
        """
        Calculate realized directional move from entry.

        BUY/CALL:
            positive when current price > entry.

        SELL/PUT:
            positive when current price < entry.

        Returns percentage magnitude.
        """

        entry = self._safe(context.entry_price)
        current = self._safe(context.current_price)

        if entry <= 0.0 or current <= 0.0:
            return 0.0

        direction = context.direction

        if direction in (
            HoldabilityDirection.BUY,
            HoldabilityDirection.CALL,
        ):
            return ((current - entry) / entry) * 100.0

        if direction in (
            HoldabilityDirection.SELL,
            HoldabilityDirection.PUT,
        ):
            return ((entry - current) / entry) * 100.0

        return 0.0

    # --------------------------------------------------------
    # FAVORABLE / ADVERSE MOVE
    # --------------------------------------------------------

    def calculate_move_components(
        self,
        context: HoldabilityContext,
    ) -> Dict[str, float]:

        move = self.calculate_directional_move(context)

        favorable = max(0.0, move)
        adverse = max(0.0, -move)

        return {
            "realized_move_pct": move,
            "favorable_move_pct": favorable,
            "adverse_move_pct": adverse,
        }

    # --------------------------------------------------------
    # TARGET PROGRESS
    # --------------------------------------------------------

    def calculate_target_progress(
        self,
        context: HoldabilityContext,
    ) -> float:
        """
        Calculate progress from entry toward target.

        This is directional and therefore works for BUY/SELL/CALL/PUT.
        """

        entry = self._safe(context.entry_price)
        current = self._safe(context.current_price)
        target = self._safe(context.target_price)

        if entry <= 0.0 or current <= 0.0 or target <= 0.0:
            return 0.0

        direction = context.direction

        if direction in (
            HoldabilityDirection.BUY,
            HoldabilityDirection.CALL,
        ):
            total_distance = target - entry
            current_distance = current - entry

        elif direction in (
            HoldabilityDirection.SELL,
            HoldabilityDirection.PUT,
        ):
            total_distance = entry - target
            current_distance = entry - current

        else:
            return 0.0

        if total_distance <= 0.0:
            return 0.0

        progress = (current_distance / total_distance) * 100.0

        return self._clamp(progress)

    # --------------------------------------------------------
    # INVALIDATION PROGRESS
    # --------------------------------------------------------

    def calculate_invalidation_progress(
        self,
        context: HoldabilityContext,
    ) -> float:
        """
        Measure how close the current price is to thesis invalidation.

        0   = no progress toward invalidation
        100 = invalidation level reached/crossed
        """

        entry = self._safe(context.entry_price)
        current = self._safe(context.current_price)
        invalidation = self._safe(context.invalidation_price)

        if entry <= 0.0 or current <= 0.0 or invalidation <= 0.0:
            return 0.0

        direction = context.direction

        if direction in (
            HoldabilityDirection.BUY,
            HoldabilityDirection.CALL,
        ):
            total_distance = entry - invalidation
            adverse_distance = entry - current

        elif direction in (
            HoldabilityDirection.SELL,
            HoldabilityDirection.PUT,
        ):
            total_distance = invalidation - entry
            adverse_distance = current - entry

        else:
            return 0.0

        if total_distance <= 0.0:
            return 0.0

        progress = (adverse_distance / total_distance) * 100.0

        return self._clamp(progress)

    # --------------------------------------------------------
    # MARKET SUPPORT
    # --------------------------------------------------------

    def calculate_market_support(
        self,
        context: HoldabilityContext,
    ) -> float:
        """
        Aggregate current support for the existing thesis.

        This is intentionally measurement-oriented.

        It does not determine final trade direction.
        """

        components = [
            self._safe(context.structure_score),
            self._safe(context.participation_score),
            self._safe(context.liquidity_score),
            self._safe(context.relationship_score),
            self._safe(context.regime_score),
            self._safe(context.evidence_score),
        ]

        weights = [
            0.22,
            0.18,
            0.14,
            0.12,
            0.14,
            0.20,
        ]

        support = sum(
            component * weight
            for component, weight in zip(components, weights)
        )

        return self._clamp(support)

    # --------------------------------------------------------
    # CONTINUATION
    # --------------------------------------------------------

    def calculate_continuation_score(
        self,
        context: HoldabilityContext,
    ) -> float:
        """
        Measure continuation support.

        Thesis score and continuation evidence are combined with
        current momentum without allowing momentum alone to dominate.
        """

        thesis = self._safe(context.thesis_score)
        continuation = self._safe(context.continuation_score)
        momentum = self._safe(context.momentum_score)

        score = (
            thesis * 0.45
            + continuation * 0.40
            + momentum * 0.15
        )

        return self._clamp(score)

    # --------------------------------------------------------
    # PRESSURES
    # --------------------------------------------------------

    def calculate_pressures(
        self,
        context: HoldabilityContext,
        invalidation_progress: float,
    ) -> Dict[str, float]:

        anti_evidence = self._safe(
            context.anti_evidence_score
        )

        opposing = self._safe(
            context.opposing_pressure_score
        )

        exhaustion = self._safe(
            context.exhaustion_score
        )

        thesis_pressure = self._clamp(
            (
                anti_evidence * 0.35
                + opposing * 0.30
                + invalidation_progress * 0.35
            )
        )

        return {
            "thesis_pressure": thesis_pressure,
            "anti_evidence_pressure": anti_evidence,
            "opposing_pressure": opposing,
            "exhaustion_pressure": exhaustion,
        }

    # --------------------------------------------------------
    # HOLDABILITY SCORE
    # --------------------------------------------------------

    def calculate_holdability_score(
        self,
        market_support: float,
        continuation_score: float,
        thesis_pressure: float,
        exhaustion_pressure: float,
        invalidation_progress: float,
    ) -> float:
        """
        Calculate normalized holdability quality.

        Positive support increases holdability.
        Material thesis deterioration reduces holdability.

        This score is NOT a probability of profit.
        """

        support_component = (
            market_support * 0.40
            + continuation_score * 0.35
            + (100.0 - thesis_pressure) * 0.15
            + (100.0 - exhaustion_pressure) * 0.10
        )

        invalidation_penalty = invalidation_progress * 0.30

        score = support_component - invalidation_penalty

        return self._clamp(score)

    # --------------------------------------------------------
    # STATE
    # --------------------------------------------------------

    def classify_state(
        self,
        context: HoldabilityContext,
        score: float,
        invalidation_progress: float,
        pressures: Dict[str, float],
    ) -> HoldabilityState:

        if not context.instrument:
            return HoldabilityState.INSUFFICIENT_DATA

        if context.direction == HoldabilityDirection.UNKNOWN:
            return HoldabilityState.INSUFFICIENT_DATA

        if context.structure_broken:
            return HoldabilityState.INVALIDATED

        if not context.thesis_intact:
            return HoldabilityState.INVALIDATED

        if invalidation_progress >= 100.0:
            return HoldabilityState.INVALIDATED

        if context.exhaustion_detected:
            return HoldabilityState.EXHAUSTED

        if pressures["anti_evidence_pressure"] >= 80.0:
            return HoldabilityState.DAMAGED

        if pressures["opposing_pressure"] >= 80.0:
            return HoldabilityState.DAMAGED

        if score >= self.strong_threshold:
            return HoldabilityState.STRONG

        if score >= self.healthy_threshold:
            return HoldabilityState.HEALTHY

        if score >= self.watch_threshold:
            return HoldabilityState.WATCH

        if score >= self.weakening_threshold:
            return HoldabilityState.WEAKENING

        return HoldabilityState.DAMAGED

    # --------------------------------------------------------
    # TRIGGER
    # --------------------------------------------------------

    def detect_trigger(
        self,
        context: HoldabilityContext,
        state: HoldabilityState,
        pressures: Dict[str, float],
        continuation_score: float,
    ) -> HoldabilityTrigger:

        if context.structure_broken:
            return HoldabilityTrigger.STRUCTURE_BREAK

        if not context.thesis_intact:
            return HoldabilityTrigger.INVALIDATION

        if context.anti_evidence_detected:
            return HoldabilityTrigger.ANTI_EVIDENCE

        if context.exhaustion_detected:
            return HoldabilityTrigger.EXHAUSTION

        if pressures["opposing_pressure"] >= self.MATERIAL_OPPOSING_PRESSURE:
            return HoldabilityTrigger.OPPOSITE_PRESSURE

        if pressures["anti_evidence_pressure"] >= self.MATERIAL_ANTI_EVIDENCE:
            return HoldabilityTrigger.THESIS_WEAKENING

        if (
            pressures["exhaustion_pressure"]
            >= self.MATERIAL_EXHAUSTION
        ):
            return HoldabilityTrigger.EXHAUSTION

        if continuation_score >= 70.0:
            return HoldabilityTrigger.CONTINUATION_SUPPORT

        if state in (
            HoldabilityState.WEAKENING,
            HoldabilityState.DAMAGED,
        ):
            return HoldabilityTrigger.THESIS_WEAKENING

        return HoldabilityTrigger.NONE

    # --------------------------------------------------------
    # MEASURE
    # --------------------------------------------------------

    def measure(
        self,
        context: HoldabilityContext,
    ) -> HoldabilityMeasurement:
        """
        Main Part-1 measurement pipeline.
        """

        context.normalize()

        moves = self.calculate_move_components(context)

        target_progress = self.calculate_target_progress(context)

        invalidation_progress = (
            self.calculate_invalidation_progress(context)
        )

        market_support = self.calculate_market_support(context)

        continuation_score = (
            self.calculate_continuation_score(context)
        )

        pressures = self.calculate_pressures(
            context,
            invalidation_progress,
        )

        holdability_score = self.calculate_holdability_score(
            market_support=market_support,
            continuation_score=continuation_score,
            thesis_pressure=pressures["thesis_pressure"],
            exhaustion_pressure=pressures["exhaustion_pressure"],
            invalidation_progress=invalidation_progress,
        )

        state = self.classify_state(
            context=context,
            score=holdability_score,
            invalidation_progress=invalidation_progress,
            pressures=pressures,
        )

        trigger = self.detect_trigger(
            context=context,
            state=state,
            pressures=pressures,
            continuation_score=continuation_score,
        )

        reasons: List[str] = []
        warnings: List[str] = []

        if market_support >= 70.0:
            reasons.append(
                "Current market evidence supports the existing thesis."
            )

        if continuation_score >= 70.0:
            reasons.append(
                "Continuation support remains meaningful."
            )

        if invalidation_progress >= 75.0:
            warnings.append(
                "Price is materially close to the thesis invalidation level."
            )

        if pressures["anti_evidence_pressure"] >= 50.0:
            warnings.append(
                "Material anti-evidence is present."
            )

        if pressures["opposing_pressure"] >= 50.0:
            warnings.append(
                "Opposite pressure is increasing."
            )

        if pressures["exhaustion_pressure"] >= 60.0:
            warnings.append(
                "Exhaustion pressure is elevated."
            )

        if state == HoldabilityState.INVALIDATED:
            warnings.append(
                "Existing thesis is no longer structurally intact."
            )

        return HoldabilityMeasurement(
            current_price=self._safe(context.current_price),
            entry_price=self._safe(context.entry_price),
            target_price=self._safe(context.target_price),
            invalidation_price=self._safe(
                context.invalidation_price
            ),
            realized_move_pct=moves["realized_move_pct"],
            favorable_move_pct=moves["favorable_move_pct"],
            adverse_move_pct=moves["adverse_move_pct"],
            target_progress_pct=target_progress,
            invalidation_progress_pct=invalidation_progress,
            market_support_score=market_support,
            continuation_score=continuation_score,
            thesis_pressure=pressures["thesis_pressure"],
            anti_evidence_pressure=pressures[
                "anti_evidence_pressure"
            ],
            opposing_pressure=pressures[
                "opposing_pressure"
            ],
            exhaustion_pressure=pressures[
                "exhaustion_pressure"
            ],
            holdability_score=holdability_score,
            state=state,
            trigger=trigger,
            reasons=reasons,
            warnings=warnings,
            metadata={
                "engine": self.ENGINE_NAME,
                "engine_version": self.ENGINE_VERSION,
            },
        ).normalize()

    # --------------------------------------------------------
    # EVENT
    # --------------------------------------------------------

    def build_event(
        self,
        context: HoldabilityContext,
        measurement: HoldabilityMeasurement,
    ) -> HoldabilityEvent:

        timestamp = (
            context.timestamp
            if isinstance(context.timestamp, datetime)
            else self._utc_now()
        )

        material = measurement.state in (
            HoldabilityState.DAMAGED,
            HoldabilityState.INVALIDATED,
            HoldabilityState.EXHAUSTED,
        )

        reason = (
            measurement.warnings[0]
            if measurement.warnings
            else (
                measurement.reasons[0]
                if measurement.reasons
                else "Holdability state measured."
            )
        )

        return HoldabilityEvent(
            event_id=f"HOLD-{int(timestamp.timestamp() * 1000)}",
            timestamp=timestamp,
            instrument=context.instrument,
            direction=context.direction,
            state=measurement.state,
            trigger=measurement.trigger,
            current_price=measurement.current_price,
            holdability_score=measurement.holdability_score,
            thesis_intact=context.thesis_intact,
            anti_evidence_detected=context.anti_evidence_detected,
            exhaustion_detected=context.exhaustion_detected,
            material=material,
            reason=reason,
            evidence_ids=list(
                context.metadata.get("evidence_ids", [])
            ),
            source_engines=list(
                context.metadata.get("source_engines", [])
            ),
            metadata={
                "engine": self.ENGINE_NAME,
                "engine_version": self.ENGINE_VERSION,
            },
        )


# ============================================================
# CONVENIENCE API
# ============================================================

def measure_holdability(
    context: HoldabilityContext,
    engine: Optional[HoldabilityEngine] = None,
) -> HoldabilityMeasurement:
    """
    Convenience wrapper for holdability measurement.
    """

    active_engine = engine or HoldabilityEngine()

    return active_engine.measure(context)


def build_holdability_event(
    context: HoldabilityContext,
    measurement: Optional[HoldabilityMeasurement] = None,
    engine: Optional[HoldabilityEngine] = None,
) -> HoldabilityEvent:
    """
    Convenience wrapper for event generation.
    """

    active_engine = engine or HoldabilityEngine()

    active_measurement = (
        measurement
        if measurement is not None
        else active_engine.measure(context)
    )

    return active_engine.build_event(
        context,
        active_measurement,
    )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "HoldabilityDirection",
    "HoldabilityState",
    "HoldabilityTrigger",
    "HoldabilityContext",
    "HoldabilityMeasurement",
    "HoldabilityEvent",
    "HoldabilityEngine",
    "measure_holdability",
    "build_holdability_event",
]
# ============================================================
# HOLDABILITY ENGINE — PART 2
# Thesis / Score / Assessment Layer
# ============================================================

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ============================================================
# THESIS HEALTH
# ============================================================

class HoldabilityThesisHealth(str, Enum):
    STRONG = "STRONG"
    HEALTHY = "HEALTHY"
    STABLE = "STABLE"
    WATCH = "WATCH"
    WEAKENING = "WEAKENING"
    DAMAGED = "DAMAGED"
    EXHAUSTED = "EXHAUSTED"
    INVALIDATED = "INVALIDATED"
    UNKNOWN = "UNKNOWN"


# ============================================================
# THESIS
# ============================================================

@dataclass
class HoldabilityThesis:
    """
    Current health of the active thesis.
    """

    health: HoldabilityThesisHealth = (
        HoldabilityThesisHealth.UNKNOWN
    )

    intact: bool = True

    continuation_supported: bool = False
    structure_supported: bool = False
    participation_supported: bool = False
    liquidity_supported: bool = False
    relationship_supported: bool = False
    regime_supported: bool = False

    anti_evidence_present: bool = False
    exhaustion_present: bool = False
    invalidation_risk: bool = False

    confidence: float = 0.0

    reasons: List[str] = field(
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
            "health": self.health.value,
            "intact": self.intact,

            "continuation_supported":
                self.continuation_supported,

            "structure_supported":
                self.structure_supported,

            "participation_supported":
                self.participation_supported,

            "liquidity_supported":
                self.liquidity_supported,

            "relationship_supported":
                self.relationship_supported,

            "regime_supported":
                self.regime_supported,

            "anti_evidence_present":
                self.anti_evidence_present,

            "exhaustion_present":
                self.exhaustion_present,

            "invalidation_risk":
                self.invalidation_risk,

            "confidence": self.confidence,

            "reasons": list(self.reasons),
            "warnings": list(self.warnings),

            "metadata": dict(self.metadata),
        }


# ============================================================
# SCORE
# ============================================================

@dataclass
class HoldabilityScore:
    """
    Normalized holdability score container.
    """

    market_support: float = 0.0
    continuation_score: float = 0.0

    holdability_score: float = 0.0

    thesis_pressure: float = 0.0
    anti_evidence_pressure: float = 0.0
    opposing_pressure: float = 0.0
    exhaustion_pressure: float = 0.0

    target_progress: float = 0.0
    invalidation_progress: float = 0.0

    confidence_score: float = 0.0

    def normalize(self):

        score_fields = [
            "market_support",
            "continuation_score",
            "holdability_score",
            "thesis_pressure",
            "anti_evidence_pressure",
            "opposing_pressure",
            "exhaustion_pressure",
            "target_progress",
            "invalidation_progress",
            "confidence_score",
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

            value = max(
                0.0,
                min(
                    100.0,
                    value,
                ),
            )

            setattr(
                self,
                field_name,
                value,
            )

        return self

    def to_dict(self):

        return {
            "market_support":
                self.market_support,

            "continuation_score":
                self.continuation_score,

            "holdability_score":
                self.holdability_score,

            "thesis_pressure":
                self.thesis_pressure,

            "anti_evidence_pressure":
                self.anti_evidence_pressure,

            "opposing_pressure":
                self.opposing_pressure,

            "exhaustion_pressure":
                self.exhaustion_pressure,

            "target_progress":
                self.target_progress,

            "invalidation_progress":
                self.invalidation_progress,

            "confidence_score":
                self.confidence_score,
        }


# ============================================================
# ASSESSMENT
# ============================================================

@dataclass
class HoldabilityAssessment:
    """
    Final assessment object generated by
    Holdability Engine.
    """

    instrument: str = ""

    timestamp: str = ""

    direction: HoldabilityDirection = (
        HoldabilityDirection.UNKNOWN
    )

    state: HoldabilityState = (
        HoldabilityState.UNKNOWN
    )

    trigger: HoldabilityTrigger = (
        HoldabilityTrigger.NONE
    )

    thesis: HoldabilityThesis = field(
        default_factory=HoldabilityThesis
    )

    score: HoldabilityScore = field(
        default_factory=HoldabilityScore
    )

    material_change: bool = False

    recalculation_required: bool = False

    thesis_review_required: bool = False

    reasons: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self):

        if not self.timestamp:

            self.timestamp = (
                datetime.now(
                    timezone.utc
                ).isoformat()
            )

    def to_dict(self):

        return {

            "instrument":
                self.instrument,

            "timestamp":
                self.timestamp,

            "direction":
                self.direction.value,

            "state":
                self.state.value,

            "trigger":
                self.trigger.value,

            "material_change":
                self.material_change,

            "recalculation_required":
                self.recalculation_required,

            "thesis_review_required":
                self.thesis_review_required,

            "thesis":
                self.thesis.to_dict(),

            "score":
                self.score.to_dict(),

            "reasons":
                list(self.reasons),

            "warnings":
                list(self.warnings),

            "metadata":
                dict(self.metadata),
        }


# ============================================================
# ASSESSMENT BUILDER
# ============================================================

class HoldabilityAssessmentBuilder:
    """
    Converts measurement into assessment.
    """

    STRONG_HEALTH = 75.0
    HEALTHY_HEALTH = 60.0
    WATCH_HEALTH = 45.0
    WEAK_HEALTH = 35.0

    def build_thesis(
        self,
        context: HoldabilityContext,
        measurement: HoldabilityMeasurement,
    ) -> HoldabilityThesis:

        score = measurement.holdability_score

        if (
            not context.thesis_intact
            or context.structure_broken
        ):
            health = (
                HoldabilityThesisHealth.INVALIDATED
            )

        elif context.exhaustion_detected:
            health = (
                HoldabilityThesisHealth.EXHAUSTED
            )

        elif score >= self.STRONG_HEALTH:
            health = (
                HoldabilityThesisHealth.STRONG
            )

        elif score >= self.HEALTHY_HEALTH:
            health = (
                HoldabilityThesisHealth.HEALTHY
            )

        elif score >= self.WATCH_HEALTH:
            health = (
                HoldabilityThesisHealth.WATCH
            )

        elif score >= self.WEAK_HEALTH:
            health = (
                HoldabilityThesisHealth.WEAKENING
            )

        else:
            health = (
                HoldabilityThesisHealth.DAMAGED
            )

        thesis = HoldabilityThesis(

            health=health,

            intact=(
                health
                not in (
                    HoldabilityThesisHealth.INVALIDATED,
                    HoldabilityThesisHealth.EXHAUSTED,
                )
            ),

            continuation_supported=(
                measurement.continuation_score
                >= 60
            ),

            structure_supported=(
                context.structure_score
                >= 60
            ),

            participation_supported=(
                context.participation_score
                >= 60
            ),

            liquidity_supported=(
                context.liquidity_score
                >= 60
            ),

            relationship_supported=(
                context.relationship_score
                >= 60
            ),

            regime_supported=(
                context.regime_score
                >= 60
            ),

            anti_evidence_present=(
                context.anti_evidence_detected
            ),

            exhaustion_present=(
                context.exhaustion_detected
            ),

            invalidation_risk=(
                measurement
                .invalidation_progress_pct
                >= 70
            ),

            confidence=(
                measurement.holdability_score
            ),

            reasons=list(
                measurement.reasons
            ),

            warnings=list(
                measurement.warnings
            ),
        )

        return thesis

    def build_score(
        self,
        measurement: HoldabilityMeasurement,
    ) -> HoldabilityScore:

        score = HoldabilityScore(

            market_support=
                measurement.market_support_score,

            continuation_score=
                measurement.continuation_score,

            holdability_score=
                measurement.holdability_score,

            thesis_pressure=
                measurement.thesis_pressure,

            anti_evidence_pressure=
                measurement.anti_evidence_pressure,

            opposing_pressure=
                measurement.opposing_pressure,

            exhaustion_pressure=
                measurement.exhaustion_pressure,

            target_progress=
                measurement.target_progress_pct,

            invalidation_progress=
                measurement
                .invalidation_progress_pct,

            confidence_score=
                measurement.holdability_score,
        )

        return score.normalize()

    def build_assessment(
        self,
        context: HoldabilityContext,
        measurement: HoldabilityMeasurement,
    ) -> HoldabilityAssessment:

        thesis = self.build_thesis(
            context,
            measurement,
        )

        score = self.build_score(
            measurement,
        )

        material_change = (
            measurement.state
            in (
                HoldabilityState.DAMAGED,
                HoldabilityState.INVALIDATED,
                HoldabilityState.EXHAUSTED,
            )
        )

        assessment = HoldabilityAssessment(

            instrument=
                context.instrument,

            direction=
                context.direction,

            state=
                measurement.state,

            trigger=
                measurement.trigger,

            thesis=thesis,

            score=score,

            material_change=
                material_change,

            recalculation_required=
                material_change,

            thesis_review_required=
                (
                    thesis.health
                    in (
                        HoldabilityThesisHealth.WEAKENING,
                        HoldabilityThesisHealth.DAMAGED,
                        HoldabilityThesisHealth.EXHAUSTED,
                        HoldabilityThesisHealth.INVALIDATED,
                    )
                ),

            reasons=list(
                measurement.reasons
            ),

            warnings=list(
                measurement.warnings
            ),

            metadata={
                "builder":
                "HoldabilityAssessmentBuilder"
            },
        )

        return assessment


# ============================================================
# PUBLIC HELPERS
# ============================================================

def build_holdability_assessment(
    context: HoldabilityContext,
    measurement: HoldabilityMeasurement,
) -> HoldabilityAssessment:

    builder = (
        HoldabilityAssessmentBuilder()
    )

    return builder.build_assessment(
        context=context,
        measurement=measurement,
    )


__all__ += [

    "HoldabilityThesisHealth",

    "HoldabilityThesis",

    "HoldabilityScore",

    "HoldabilityAssessment",

    "HoldabilityAssessmentBuilder",

    "build_holdability_assessment",
]
# ============================================================
# HOLDABILITY ENGINE — PART 3
# Lifecycle / Monitoring / Transition Intelligence
# ============================================================

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any


# ============================================================
# TRANSITION
# ============================================================

@dataclass
class HoldabilityTransition:
    """
    Tracks state evolution.
    """

    previous_state: HoldabilityState = (
        HoldabilityState.UNKNOWN
    )

    current_state: HoldabilityState = (
        HoldabilityState.UNKNOWN
    )

    transition_detected: bool = False

    severity: float = 0.0

    reason: str = ""

    timestamp: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self):

        if not self.timestamp:

            self.timestamp = (
                datetime.now(
                    timezone.utc
                ).isoformat()
            )

    def to_dict(self):

        return {
            "previous_state":
                self.previous_state.value,

            "current_state":
                self.current_state.value,

            "transition_detected":
                self.transition_detected,

            "severity":
                self.severity,

            "reason":
                self.reason,

            "timestamp":
                self.timestamp,

            "metadata":
                dict(self.metadata),
        }


# ============================================================
# LIFECYCLE
# ============================================================

@dataclass
class HoldabilityLifecycle:
    """
    Historical holdability evolution.
    """

    instrument: str = ""

    first_seen: Optional[str] = None

    last_updated: Optional[str] = None

    current_state: HoldabilityState = (
        HoldabilityState.UNKNOWN
    )

    strongest_score: float = 0.0

    weakest_score: float = 100.0

    average_score: float = 0.0

    observation_count: int = 0

    deterioration_events: int = 0

    recovery_events: int = 0

    state_history: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def update(
        self,
        assessment: HoldabilityAssessment,
    ):

        now = datetime.now(
            timezone.utc
        ).isoformat()

        score = (
            assessment
            .score
            .holdability_score
        )

        if not self.first_seen:
            self.first_seen = now

        self.last_updated = now

        self.current_state = (
            assessment.state
        )

        self.state_history.append(
            assessment.state.value
        )

        self.strongest_score = max(
            self.strongest_score,
            score,
        )

        self.weakest_score = min(
            self.weakest_score,
            score,
        )

        self.observation_count += 1

        if self.observation_count == 1:

            self.average_score = score

        else:

            self.average_score = (
                (
                    self.average_score
                    *
                    (
                        self.observation_count
                        - 1
                    )
                )
                + score
            ) / self.observation_count

    def to_dict(self):

        return {
            "instrument":
                self.instrument,

            "first_seen":
                self.first_seen,

            "last_updated":
                self.last_updated,

            "current_state":
                self.current_state.value,

            "strongest_score":
                self.strongest_score,

            "weakest_score":
                self.weakest_score,

            "average_score":
                self.average_score,

            "observation_count":
                self.observation_count,

            "deterioration_events":
                self.deterioration_events,

            "recovery_events":
                self.recovery_events,

            "state_history":
                list(self.state_history),

            "metadata":
                dict(self.metadata),
        }


# ============================================================
# MONITOR
# ============================================================

class HoldabilityMonitor:
    """
    Monitors holdability evolution.

    No trade authority.
    Monitoring only.
    """

    def __init__(self):

        self.lifecycle_store: Dict[
            str,
            HoldabilityLifecycle
        ] = {}

    # --------------------------------------------------------
    # RANK
    # --------------------------------------------------------

    def _rank(
        self,
        state: HoldabilityState,
    ) -> int:

        mapping = {

            HoldabilityState.STRONG: 7,

            HoldabilityState.HEALTHY: 6,

            HoldabilityState.WATCH: 5,

            HoldabilityState.WEAKENING: 4,

            HoldabilityState.DAMAGED: 3,

            HoldabilityState.EXHAUSTED: 2,

            HoldabilityState.INVALIDATED: 1,

            HoldabilityState.UNKNOWN: 0,
        }

        return mapping.get(
            state,
            0,
        )

    # --------------------------------------------------------
    # TRANSITION
    # --------------------------------------------------------

    def detect_transition(
        self,
        previous_state: HoldabilityState,
        current_state: HoldabilityState,
    ) -> HoldabilityTransition:

        if previous_state == current_state:

            return HoldabilityTransition(
                previous_state=
                    previous_state,

                current_state=
                    current_state,

                transition_detected=False,
            )

        severity = abs(
            self._rank(previous_state)
            -
            self._rank(current_state)
        )

        return HoldabilityTransition(

            previous_state=
                previous_state,

            current_state=
                current_state,

            transition_detected=True,

            severity=float(
                severity
            ),

            reason=
                f"{previous_state.value}"
                f" -> "
                f"{current_state.value}",
        )

    # --------------------------------------------------------
    # DETERIORATION
    # --------------------------------------------------------

    def is_deteriorating(
        self,
        previous_state,
        current_state,
    ) -> bool:

        return (
            self._rank(current_state)
            <
            self._rank(previous_state)
        )

    # --------------------------------------------------------
    # RECOVERY
    # --------------------------------------------------------

    def is_recovering(
        self,
        previous_state,
        current_state,
    ) -> bool:

        return (
            self._rank(current_state)
            >
            self._rank(previous_state)
        )

    # --------------------------------------------------------
    # LIFECYCLE
    # --------------------------------------------------------

    def update_lifecycle(
        self,
        assessment: HoldabilityAssessment,
    ) -> HoldabilityLifecycle:

        instrument = (
            assessment.instrument
            or
            "UNKNOWN"
        )

        lifecycle = (
            self.lifecycle_store.get(
                instrument
            )
        )

        if lifecycle is None:

            lifecycle = (
                HoldabilityLifecycle(
                    instrument=
                        instrument
                )
            )

            self.lifecycle_store[
                instrument
            ] = lifecycle

        previous_state = (
            lifecycle.current_state
        )

        lifecycle.update(
            assessment
        )

        if self.is_deteriorating(
            previous_state,
            assessment.state,
        ):

            lifecycle.deterioration_events += 1

        elif self.is_recovering(
            previous_state,
            assessment.state,
        ):

            lifecycle.recovery_events += 1

        return lifecycle

    # --------------------------------------------------------
    # MATERIAL CHANGE
    # --------------------------------------------------------

    def detect_material_change(
        self,
        assessment: HoldabilityAssessment,
    ) -> bool:

        if assessment.state in (

            HoldabilityState.INVALIDATED,

            HoldabilityState.EXHAUSTED,

            HoldabilityState.DAMAGED,
        ):
            return True

        if (
            assessment
            .score
            .invalidation_progress
            >= 80
        ):
            return True

        if (
            assessment
            .score
            .anti_evidence_pressure
            >= 70
        ):
            return True

        if (
            assessment
            .score
            .opposing_pressure
            >= 70
        ):
            return True

        return False

    # --------------------------------------------------------
    # TREND
    # --------------------------------------------------------

    def estimate_trend(
        self,
        lifecycle: HoldabilityLifecycle,
    ) -> str:

        if lifecycle.observation_count < 3:
            return "INSUFFICIENT_DATA"

        if (
            lifecycle.recovery_events
            >
            lifecycle.deterioration_events
        ):
            return "IMPROVING"

        if (
            lifecycle.deterioration_events
            >
            lifecycle.recovery_events
        ):
            return "DETERIORATING"

        return "STABLE"


# ============================================================
# HELPERS
# ============================================================

def create_holdability_monitor():

    return HoldabilityMonitor()


__all__ += [

    "HoldabilityTransition",

    "HoldabilityLifecycle",

    "HoldabilityMonitor",

    "create_holdability_monitor",
]
# ============================================================
# HOLDABILITY ENGINE — PART 4
# Intelligence / Diagnostics / Survivability Layer
# ============================================================

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


# ============================================================
# INTELLIGENCE
# ============================================================

@dataclass
class HoldabilityIntelligence:
    """
    Higher-order intelligence interpretation.

    Measurement
        ↓
    Assessment
        ↓
    Intelligence
    """

    thesis_integrity_score: float = 0.0

    persistence_score: float = 0.0

    survivability_score: float = 0.0

    deterioration_risk: float = 0.0

    continuation_probability: float = 0.0

    holdability_quality: str = "UNKNOWN"

    dominant_factor: str = ""

    risk_factor: str = ""

    strengths: List[str] = field(
        default_factory=list
    )

    weaknesses: List[str] = field(
        default_factory=list
    )

    diagnostics: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self):

        return {
            "thesis_integrity_score":
                self.thesis_integrity_score,

            "persistence_score":
                self.persistence_score,

            "survivability_score":
                self.survivability_score,

            "deterioration_risk":
                self.deterioration_risk,

            "continuation_probability":
                self.continuation_probability,

            "holdability_quality":
                self.holdability_quality,

            "dominant_factor":
                self.dominant_factor,

            "risk_factor":
                self.risk_factor,

            "strengths":
                list(self.strengths),

            "weaknesses":
                list(self.weaknesses),

            "diagnostics":
                dict(self.diagnostics),
        }


# ============================================================
# NARRATIVE
# ============================================================

@dataclass
class HoldabilityNarrative:

    summary: str = ""

    thesis_status: str = ""

    continuation_view: str = ""

    risk_view: str = ""

    conclusion: str = ""

    def to_dict(self):

        return {
            "summary":
                self.summary,

            "thesis_status":
                self.thesis_status,

            "continuation_view":
                self.continuation_view,

            "risk_view":
                self.risk_view,

            "conclusion":
                self.conclusion,
        }


# ============================================================
# DIAGNOSTICS
# ============================================================

class HoldabilityDiagnostics:

    @staticmethod
    def thesis_integrity(
        assessment: HoldabilityAssessment
    ) -> float:

        score = (
            assessment.score.holdability_score
        )

        penalty = 0.0

        if (
            assessment.thesis
            .anti_evidence_present
        ):
            penalty += 15

        if (
            assessment.thesis
            .exhaustion_present
        ):
            penalty += 20

        if (
            assessment.thesis
            .invalidation_risk
        ):
            penalty += 25

        return max(
            0.0,
            min(
                100.0,
                score - penalty,
            ),
        )

    @staticmethod
    def persistence_score(
        lifecycle: HoldabilityLifecycle
    ) -> float:

        if (
            lifecycle.observation_count
            == 0
        ):
            return 0.0

        stability_bonus = max(
            0,
            (
                lifecycle.recovery_events
                -
                lifecycle.deterioration_events
            )
            * 5,
        )

        score = (
            lifecycle.average_score
            + stability_bonus
        )

        return max(
            0.0,
            min(
                100.0,
                score,
            ),
        )

    @staticmethod
    def survivability_score(
        assessment: HoldabilityAssessment
    ) -> float:

        score = (
            assessment.score.holdability_score
        )

        score -= (
            assessment.score
            .invalidation_progress
            * 0.30
        )

        score -= (
            assessment.score
            .anti_evidence_pressure
            * 0.20
        )

        return max(
            0.0,
            min(
                100.0,
                score,
            ),
        )

    @staticmethod
    def deterioration_risk(
        assessment: HoldabilityAssessment
    ) -> float:

        risk = 0.0

        risk += (
            assessment.score
            .anti_evidence_pressure
            * 0.40
        )

        risk += (
            assessment.score
            .opposing_pressure
            * 0.30
        )

        risk += (
            assessment.score
            .exhaustion_pressure
            * 0.30
        )

        return max(
            0.0,
            min(
                100.0,
                risk,
            ),
        )


# ============================================================
# INTELLIGENCE BUILDER
# ============================================================

class HoldabilityIntelligenceBuilder:

    def build(
        self,
        assessment: HoldabilityAssessment,
        lifecycle: HoldabilityLifecycle,
    ) -> HoldabilityIntelligence:

        integrity = (
            HoldabilityDiagnostics
            .thesis_integrity(
                assessment
            )
        )

        persistence = (
            HoldabilityDiagnostics
            .persistence_score(
                lifecycle
            )
        )

        survivability = (
            HoldabilityDiagnostics
            .survivability_score(
                assessment
            )
        )

        deterioration = (
            HoldabilityDiagnostics
            .deterioration_risk(
                assessment
            )
        )

        continuation = max(
            0.0,
            min(
                100.0,
                (
                    integrity * 0.40
                    +
                    persistence * 0.25
                    +
                    survivability * 0.35
                ),
            ),
        )

        strengths = []
        weaknesses = []

        if integrity >= 70:
            strengths.append(
                "Thesis integrity remains strong."
            )

        if persistence >= 70:
            strengths.append(
                "Historical holdability remains stable."
            )

        if survivability >= 70:
            strengths.append(
                "Position survives adverse pressure well."
            )

        if deterioration >= 60:
            weaknesses.append(
                "Deterioration pressure elevated."
            )

        if (
            assessment.score
            .anti_evidence_pressure
            >= 60
        ):
            weaknesses.append(
                "Anti-evidence increasing."
            )

        if continuation >= 80:

            quality = "A+"

        elif continuation >= 70:

            quality = "A"

        elif continuation >= 60:

            quality = "B"

        elif continuation >= 50:

            quality = "C"

        else:

            quality = "D"

        return HoldabilityIntelligence(

            thesis_integrity_score=
                integrity,

            persistence_score=
                persistence,

            survivability_score=
                survivability,

            deterioration_risk=
                deterioration,

            continuation_probability=
                continuation,

            holdability_quality=
                quality,

            dominant_factor=
                "THESIS_INTEGRITY",

            risk_factor=
                "DETERIORATION_RISK",

            strengths=
                strengths,

            weaknesses=
                weaknesses,

            diagnostics={

                "integrity":
                    integrity,

                "persistence":
                    persistence,

                "survivability":
                    survivability,

                "deterioration":
                    deterioration,
            },
        )


# ============================================================
# NARRATIVE BUILDER
# ============================================================

class HoldabilityNarrativeBuilder:

    def build(
        self,
        intelligence:
        HoldabilityIntelligence
    ) -> HoldabilityNarrative:

        thesis_status = (
            f"Integrity "
            f"{intelligence.thesis_integrity_score:.1f}"
        )

        continuation_view = (
            f"Continuation "
            f"{intelligence.continuation_probability:.1f}"
        )

        risk_view = (
            f"Risk "
            f"{intelligence.deterioration_risk:.1f}"
        )

        conclusion = (
            f"Holdability Grade "
            f"{intelligence.holdability_quality}"
        )

        return HoldabilityNarrative(

            summary=
                "Holdability intelligence generated.",

            thesis_status=
                thesis_status,

            continuation_view=
                continuation_view,

            risk_view=
                risk_view,

            conclusion=
                conclusion,
        )


# ============================================================
# HELPERS
# ============================================================

def build_holdability_intelligence(
    assessment: HoldabilityAssessment,
    lifecycle: HoldabilityLifecycle,
):

    builder = (
        HoldabilityIntelligenceBuilder()
    )

    return builder.build(
        assessment,
        lifecycle,
    )


def build_holdability_narrative(
    intelligence:
    HoldabilityIntelligence
):

    builder = (
        HoldabilityNarrativeBuilder()
    )

    return builder.build(
        intelligence
    )


__all__ += [

    "HoldabilityIntelligence",

    "HoldabilityNarrative",

    "HoldabilityDiagnostics",

    "HoldabilityIntelligenceBuilder",

    "HoldabilityNarrativeBuilder",

    "build_holdability_intelligence",

    "build_holdability_narrative",
]
# ============================================================
# HOLDABILITY ENGINE — PART 5
# Integration / Export / Orchestration Layer
# ============================================================

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional


# ============================================================
# D13 CONTRACT
# ============================================================

@dataclass
class HoldabilityDecisionContract:
    """
    Upstream intelligence contract.

    IMPORTANT:
    Does NOT issue final trade decisions.

    D13 remains final authority.
    """

    instrument: str = ""

    direction: str = ""

    holdability_score: float = 0.0

    holdability_state: str = ""

    holdability_quality: str = ""

    continuation_probability: float = 0.0

    deterioration_risk: float = 0.0

    thesis_integrity_score: float = 0.0

    persistence_score: float = 0.0

    survivability_score: float = 0.0

    thesis_review_required: bool = False

    material_change: bool = False

    timestamp: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self):

        if not self.timestamp:

            self.timestamp = (
                datetime.now(
                    timezone.utc
                ).isoformat()
            )

    def to_dict(self):

        return {
            "instrument":
                self.instrument,

            "direction":
                self.direction,

            "holdability_score":
                self.holdability_score,

            "holdability_state":
                self.holdability_state,

            "holdability_quality":
                self.holdability_quality,

            "continuation_probability":
                self.continuation_probability,

            "deterioration_risk":
                self.deterioration_risk,

            "thesis_integrity_score":
                self.thesis_integrity_score,

            "persistence_score":
                self.persistence_score,

            "survivability_score":
                self.survivability_score,

            "thesis_review_required":
                self.thesis_review_required,

            "material_change":
                self.material_change,

            "timestamp":
                self.timestamp,

            "metadata":
                dict(self.metadata),
        }


# ============================================================
# FUTURE RANK CONTRACT
# ============================================================

@dataclass
class HoldabilityFutureRankContract:

    instrument: str = ""

    holdability_score: float = 0.0

    persistence_score: float = 0.0

    survivability_score: float = 0.0

    future_rank_contribution: float = 0.0

    quality: str = "UNKNOWN"

    def to_dict(self):

        return {
            "instrument":
                self.instrument,

            "holdability_score":
                self.holdability_score,

            "persistence_score":
                self.persistence_score,

            "survivability_score":
                self.survivability_score,

            "future_rank_contribution":
                self.future_rank_contribution,

            "quality":
                self.quality,
        }


# ============================================================
# GROWTH PROTECTION CONTRACT
# ============================================================

@dataclass
class HoldabilityProtectionContract:

    instrument: str = ""

    protection_score: float = 0.0

    deterioration_risk: float = 0.0

    survivability_score: float = 0.0

    capital_retention_support: float = 0.0

    protection_quality: str = ""

    def to_dict(self):

        return {
            "instrument":
                self.instrument,

            "protection_score":
                self.protection_score,

            "deterioration_risk":
                self.deterioration_risk,

            "survivability_score":
                self.survivability_score,

            "capital_retention_support":
                self.capital_retention_support,

            "protection_quality":
                self.protection_quality,
        }


# ============================================================
# EXPORT PACKAGE
# ============================================================

@dataclass
class HoldabilityExportPackage:

    assessment: Dict[str, Any] = field(
        default_factory=dict
    )

    intelligence: Dict[str, Any] = field(
        default_factory=dict
    )

    narrative: Dict[str, Any] = field(
        default_factory=dict
    )

    d13_contract: Dict[str, Any] = field(
        default_factory=dict
    )

    future_rank_contract: Dict[str, Any] = field(
        default_factory=dict
    )

    protection_contract: Dict[str, Any] = field(
        default_factory=dict
    )

    lifecycle: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self):

        return {
            "assessment":
                self.assessment,

            "intelligence":
                self.intelligence,

            "narrative":
                self.narrative,

            "d13_contract":
                self.d13_contract,

            "future_rank_contract":
                self.future_rank_contract,

            "protection_contract":
                self.protection_contract,

            "lifecycle":
                self.lifecycle,
        }


# ============================================================
# ORCHESTRATOR
# ============================================================

class HoldabilityOrchestrator:

    """
    Final assembly layer.

    No decision authority.
    Intelligence packaging only.
    """

    def build_d13_contract(
        self,
        assessment: HoldabilityAssessment,
        intelligence: HoldabilityIntelligence,
    ) -> HoldabilityDecisionContract:

        return HoldabilityDecisionContract(

            instrument=
                assessment.instrument,

            direction=
                assessment.direction.value,

            holdability_score=
                assessment
                .score
                .holdability_score,

            holdability_state=
                assessment.state.value,

            holdability_quality=
                intelligence
                .holdability_quality,

            continuation_probability=
                intelligence
                .continuation_probability,

            deterioration_risk=
                intelligence
                .deterioration_risk,

            thesis_integrity_score=
                intelligence
                .thesis_integrity_score,

            persistence_score=
                intelligence
                .persistence_score,

            survivability_score=
                intelligence
                .survivability_score,

            thesis_review_required=
                assessment
                .thesis_review_required,

            material_change=
                assessment
                .material_change,
        )

    def build_future_rank_contract(
        self,
        assessment: HoldabilityAssessment,
        intelligence: HoldabilityIntelligence,
    ) -> HoldabilityFutureRankContract:

        contribution = (
            intelligence.persistence_score
            * 0.40
            +
            intelligence.survivability_score
            * 0.60
        )

        return HoldabilityFutureRankContract(

            instrument=
                assessment.instrument,

            holdability_score=
                assessment
                .score
                .holdability_score,

            persistence_score=
                intelligence
                .persistence_score,

            survivability_score=
                intelligence
                .survivability_score,

            future_rank_contribution=
                contribution,

            quality=
                intelligence
                .holdability_quality,
        )

    def build_protection_contract(
        self,
        assessment: HoldabilityAssessment,
        intelligence: HoldabilityIntelligence,
    ) -> HoldabilityProtectionContract:

        protection = max(
            0.0,
            min(
                100.0,
                intelligence
                .survivability_score
                -
                (
                    intelligence
                    .deterioration_risk
                    * 0.30
                ),
            ),
        )

        return HoldabilityProtectionContract(

            instrument=
                assessment.instrument,

            protection_score=
                protection,

            deterioration_risk=
                intelligence
                .deterioration_risk,

            survivability_score=
                intelligence
                .survivability_score,

            capital_retention_support=
                protection,

            protection_quality=
                intelligence
                .holdability_quality,
        )

    def build_export_package(
        self,
        assessment: HoldabilityAssessment,
        intelligence: HoldabilityIntelligence,
        narrative: HoldabilityNarrative,
        lifecycle: HoldabilityLifecycle,
    ) -> HoldabilityExportPackage:

        d13 = self.build_d13_contract(
            assessment,
            intelligence,
        )

        future_rank = (
            self.build_future_rank_contract(
                assessment,
                intelligence,
            )
        )

        protection = (
            self.build_protection_contract(
                assessment,
                intelligence,
            )
        )

        return HoldabilityExportPackage(

            assessment=
                assessment.to_dict(),

            intelligence=
                intelligence.to_dict(),

            narrative=
                narrative.to_dict(),

            d13_contract=
                d13.to_dict(),

            future_rank_contract=
                future_rank.to_dict(),

            protection_contract=
                protection.to_dict(),

            lifecycle=
                lifecycle.to_dict(),
        )


# ============================================================
# PUBLIC API
# ============================================================

def export_holdability_package(
    assessment: HoldabilityAssessment,
    intelligence: HoldabilityIntelligence,
    narrative: HoldabilityNarrative,
    lifecycle: HoldabilityLifecycle,
):

    orchestrator = (
        HoldabilityOrchestrator()
    )

    return (
        orchestrator
        .build_export_package(
            assessment,
            intelligence,
            narrative,
            lifecycle,
        )
    )


__all__ += [

    "HoldabilityDecisionContract",

    "HoldabilityFutureRankContract",

    "HoldabilityProtectionContract",

    "HoldabilityExportPackage",

    "HoldabilityOrchestrator",

    "export_holdability_package",
]