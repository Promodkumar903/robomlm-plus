# ============================================================
# ROBOMLM_PLUS
# GROWTH PROTECTION ENGINE
# PART 1 — CORE MODELS + PROTECTION MEASUREMENT
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime


# ============================================================
# ENUMS
# ============================================================

class ProtectionDirection(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    CALL = "CALL"
    PUT = "PUT"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"


class ProtectionState(str, Enum):
    NORMAL = "NORMAL"
    WATCH = "WATCH"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    INVALIDATED = "INVALIDATED"
    EXHAUSTED = "EXHAUSTED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    UNKNOWN = "UNKNOWN"


class ProtectionTrigger(str, Enum):
    NONE = "NONE"
    PRICE_ADVERSE_MOVE = "PRICE_ADVERSE_MOVE"
    THESIS_WEAKENING = "THESIS_WEAKENING"
    ANTI_EVIDENCE = "ANTI_EVIDENCE"
    STRUCTURE_BREAK = "STRUCTURE_BREAK"
    PARTICIPATION_DECAY = "PARTICIPATION_DECAY"
    LIQUIDITY_DETERIORATION = "LIQUIDITY_DETERIORATION"
    OPPOSITE_PRESSURE = "OPPOSITE_PRESSURE"
    TARGET_APPROACH = "TARGET_APPROACH"
    EXHAUSTION = "EXHAUSTION"
    MANUAL_INVALIDATION = "MANUAL_INVALIDATION"
    UNKNOWN = "UNKNOWN"


# ============================================================
# PROTECTION CONTEXT
# ============================================================

@dataclass
class GrowthProtectionContext:
    """
    Upstream market/trade context used by the protection engine.

    Scores are measurements supplied by upstream intelligence.
    The protection engine does not invent market evidence.
    """

    direction: ProtectionDirection = (
        ProtectionDirection.UNKNOWN
    )

    current_price: float = 0.0
    entry_price: float = 0.0
    target_price: float = 0.0
    invalidation_price: float = 0.0

    expected_move_pct: float = 0.0
    realized_move_pct: float = 0.0

    thesis_strength: float = 0.0
    evidence_strength: float = 0.0

    structure_score: float = 0.0
    participation_score: float = 0.0
    liquidity_score: float = 0.0
    relationship_score: float = 0.0
    regime_score: float = 0.0

    anti_evidence_strength: float = 0.0
    opposing_pressure: float = 0.0

    momentum_score: float = 0.0
    continuation_score: float = 0.0
    exhaustion_score: float = 0.0

    volatility_score: float = 0.0

    thesis_intact: bool = True
    anti_evidence_detected: bool = False
    exhaustion_detected: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def normalize(self) -> "GrowthProtectionContext":

        self.current_price = max(
            0.0,
            float(self.current_price or 0.0)
        )

        self.entry_price = max(
            0.0,
            float(self.entry_price or 0.0)
        )

        self.target_price = max(
            0.0,
            float(self.target_price or 0.0)
        )

        self.invalidation_price = max(
            0.0,
            float(self.invalidation_price or 0.0)
        )

        score_fields = [
            "thesis_strength",
            "evidence_strength",
            "structure_score",
            "participation_score",
            "liquidity_score",
            "relationship_score",
            "regime_score",
            "anti_evidence_strength",
            "opposing_pressure",
            "momentum_score",
            "continuation_score",
            "exhaustion_score",
            "volatility_score",
        ]

        for name in score_fields:
            value = float(
                getattr(self, name, 0.0) or 0.0
            )

            setattr(
                self,
                name,
                max(0.0, min(100.0, value))
            )

        return self

    def to_dict(self) -> Dict[str, Any]:
        return {
            "direction": (
                self.direction.value
                if hasattr(
                    self.direction,
                    "value"
                )
                else str(self.direction)
            ),
            "current_price":
                self.current_price,
            "entry_price":
                self.entry_price,
            "target_price":
                self.target_price,
            "invalidation_price":
                self.invalidation_price,
            "expected_move_pct":
                self.expected_move_pct,
            "realized_move_pct":
                self.realized_move_pct,
            "thesis_strength":
                self.thesis_strength,
            "evidence_strength":
                self.evidence_strength,
            "structure_score":
                self.structure_score,
            "participation_score":
                self.participation_score,
            "liquidity_score":
                self.liquidity_score,
            "relationship_score":
                self.relationship_score,
            "regime_score":
                self.regime_score,
            "anti_evidence_strength":
                self.anti_evidence_strength,
            "opposing_pressure":
                self.opposing_pressure,
            "momentum_score":
                self.momentum_score,
            "continuation_score":
                self.continuation_score,
            "exhaustion_score":
                self.exhaustion_score,
            "volatility_score":
                self.volatility_score,
            "thesis_intact":
                self.thesis_intact,
            "anti_evidence_detected":
                self.anti_evidence_detected,
            "exhaustion_detected":
                self.exhaustion_detected,
            "metadata":
                dict(self.metadata),
        }


# ============================================================
# GROWTH PROTECTION MEASUREMENT
# ============================================================

@dataclass
class GrowthProtectionMeasurement:
    """
    Calculated protection measurements.

    These are not final trading decisions.
    """

    direction: ProtectionDirection = (
        ProtectionDirection.UNKNOWN
    )

    entry_distance_pct: float = 0.0
    target_distance_pct: float = 0.0
    invalidation_distance_pct: float = 0.0

    realized_growth_pct: float = 0.0
    remaining_expected_growth_pct: float = 0.0

    adverse_move_pct: float = 0.0
    favorable_move_pct: float = 0.0

    target_progress_pct: float = 0.0
    invalidation_progress_pct: float = 0.0

    protection_pressure: float = 0.0
    thesis_risk: float = 0.0
    anti_evidence_pressure: float = 0.0
    exhaustion_pressure: float = 0.0

    continuation_strength: float = 0.0
    market_support: float = 0.0

    state: ProtectionState = (
        ProtectionState.UNKNOWN
    )

    trigger: ProtectionTrigger = (
        ProtectionTrigger.NONE
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

    def normalize(self) -> "GrowthProtectionMeasurement":

        numeric_fields = [
            "entry_distance_pct",
            "target_distance_pct",
            "invalidation_distance_pct",
            "realized_growth_pct",
            "remaining_expected_growth_pct",
            "adverse_move_pct",
            "favorable_move_pct",
            "target_progress_pct",
            "invalidation_progress_pct",
            "protection_pressure",
            "thesis_risk",
            "anti_evidence_pressure",
            "exhaustion_pressure",
            "continuation_strength",
            "market_support",
        ]

        for name in numeric_fields:
            value = float(
                getattr(self, name, 0.0) or 0.0
            )

            setattr(
                self,
                name,
                value
            )

        return self

    def to_dict(self) -> Dict[str, Any]:
        return {
            "direction": (
                self.direction.value
                if hasattr(
                    self.direction,
                    "value"
                )
                else str(self.direction)
            ),
            "entry_distance_pct":
                self.entry_distance_pct,
            "target_distance_pct":
                self.target_distance_pct,
            "invalidation_distance_pct":
                self.invalidation_distance_pct,
            "realized_growth_pct":
                self.realized_growth_pct,
            "remaining_expected_growth_pct":
                self.remaining_expected_growth_pct,
            "adverse_move_pct":
                self.adverse_move_pct,
            "favorable_move_pct":
                self.favorable_move_pct,
            "target_progress_pct":
                self.target_progress_pct,
            "invalidation_progress_pct":
                self.invalidation_progress_pct,
            "protection_pressure":
                self.protection_pressure,
            "thesis_risk":
                self.thesis_risk,
            "anti_evidence_pressure":
                self.anti_evidence_pressure,
            "exhaustion_pressure":
                self.exhaustion_pressure,
            "continuation_strength":
                self.continuation_strength,
            "market_support":
                self.market_support,
            "state": (
                self.state.value
                if hasattr(
                    self.state,
                    "value"
                )
                else str(self.state)
            ),
            "trigger": (
                self.trigger.value
                if hasattr(
                    self.trigger,
                    "value"
                )
                else str(self.trigger)
            ),
            "reasons":
                list(self.reasons),
            "warnings":
                list(self.warnings),
            "metadata":
                dict(self.metadata),
        }


# ============================================================
# PROTECTION EVENT
# ============================================================

@dataclass
class GrowthProtectionEvent:
    """
    Represents a material protection-related event.

    Event != automatic exit.
    Downstream decision authority evaluates the event.
    """

    event_id: str
    timestamp: str

    trigger: ProtectionTrigger
    state: ProtectionState

    direction: ProtectionDirection

    current_price: float
    entry_price: float
    target_price: float
    invalidation_price: float

    pressure_score: float
    thesis_strength: float
    anti_evidence_strength: float
    exhaustion_strength: float

    material: bool = False

    reason: str = ""

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
            "event_id":
                self.event_id,
            "timestamp":
                self.timestamp,
            "trigger": (
                self.trigger.value
                if hasattr(
                    self.trigger,
                    "value"
                )
                else str(self.trigger)
            ),
            "state": (
                self.state.value
                if hasattr(
                    self.state,
                    "value"
                )
                else str(self.state)
            ),
            "direction": (
                self.direction.value
                if hasattr(
                    self.direction,
                    "value"
                )
                else str(self.direction)
            ),
            "current_price":
                self.current_price,
            "entry_price":
                self.entry_price,
            "target_price":
                self.target_price,
            "invalidation_price":
                self.invalidation_price,
            "pressure_score":
                self.pressure_score,
            "thesis_strength":
                self.thesis_strength,
            "anti_evidence_strength":
                self.anti_evidence_strength,
            "exhaustion_strength":
                self.exhaustion_strength,
            "material":
                self.material,
            "reason":
                self.reason,
            "evidence_ids":
                list(self.evidence_ids),
            "source_engines":
                list(self.source_engines),
            "metadata":
                dict(self.metadata),
        }


# ============================================================
# CORE ENGINE
# ============================================================

class GrowthProtectionEngine:
    """
    Growth Protection Engine — Part 1.

    Purpose:
        Monitor whether an existing growth/trade thesis is
        being supported, weakening, approaching exhaustion,
        or being materially invalidated.

    It does NOT:
        - guarantee profit
        - fabricate probability
        - create arbitrary fixed SL/TP
        - make final D13 decisions
        - override upstream evidence
    """

    ENGINE_NAME = "GrowthProtectionEngine"
    ENGINE_VERSION = "1.0.0"

    def __init__(
        self,
        watch_threshold: float = 35.0,
        warning_threshold: float = 55.0,
        critical_threshold: float = 75.0,
        invalidation_threshold: float = 90.0,
    ) -> None:

        self.watch_threshold = float(
            watch_threshold
        )

        self.warning_threshold = float(
            warning_threshold
        )

        self.critical_threshold = float(
            critical_threshold
        )

        self.invalidation_threshold = float(
            invalidation_threshold
        )

    # ========================================================
    # SAFE HELPERS
    # ========================================================

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
    def _clamp(
        value: Any,
        low: float = 0.0,
        high: float = 100.0,
    ) -> float:

        value = GrowthProtectionEngine._safe(
            value,
            low
        )

        return max(
            low,
            min(high, value)
        )

    # ========================================================
    # PRICE MOVE
    # ========================================================

    def calculate_price_move(
        self,
        context: GrowthProtectionContext,
    ) -> Dict[str, float]:

        context.normalize()

        entry = context.entry_price
        current = context.current_price

        if entry <= 0 or current <= 0:
            return {
                "realized_move_pct": 0.0,
                "favorable_move_pct": 0.0,
                "adverse_move_pct": 0.0,
            }

        raw_move = (
            (current - entry)
            / entry
            * 100.0
        )

        direction = context.direction

        if direction in (
            ProtectionDirection.BUY,
            ProtectionDirection.CALL,
        ):
            favorable = max(
                0.0,
                raw_move
            )

            adverse = max(
                0.0,
                -raw_move
            )

        elif direction in (
            ProtectionDirection.SELL,
            ProtectionDirection.PUT,
        ):
            favorable = max(
                0.0,
                -raw_move
            )

            adverse = max(
                0.0,
                raw_move
            )

        else:
            favorable = 0.0
            adverse = abs(raw_move)

        return {
            "realized_move_pct":
                raw_move,
            "favorable_move_pct":
                favorable,
            "adverse_move_pct":
                adverse,
        }

    # ========================================================
    # TARGET PROGRESS
    # ========================================================

    def calculate_target_progress(
        self,
        context: GrowthProtectionContext,
    ) -> float:

        entry = context.entry_price
        current = context.current_price
        target = context.target_price

        if (
            entry <= 0
            or current <= 0
            or target <= 0
        ):
            return 0.0

        direction = context.direction

        total_distance = abs(
            target - entry
        )

        if total_distance <= 0:
            return 0.0

        if direction in (
            ProtectionDirection.BUY,
            ProtectionDirection.CALL,
        ):

            progress = (
                (current - entry)
                / total_distance
                * 100.0
            )

        elif direction in (
            ProtectionDirection.SELL,
            ProtectionDirection.PUT,
        ):

            progress = (
                (entry - current)
                / total_distance
                * 100.0
            )

        else:
            progress = 0.0

        return max(
            0.0,
            min(100.0, progress)
        )

    # ========================================================
    # INVALIDATION PROGRESS
    # ========================================================

    def calculate_invalidation_progress(
        self,
        context: GrowthProtectionContext,
    ) -> float:

        entry = context.entry_price
        current = context.current_price
        invalidation = (
            context.invalidation_price
        )

        if (
            entry <= 0
            or current <= 0
            or invalidation <= 0
        ):
            return 0.0

        direction = context.direction

        total_distance = abs(
            invalidation - entry
        )

        if total_distance <= 0:
            return 0.0

        if direction in (
            ProtectionDirection.BUY,
            ProtectionDirection.CALL,
        ):

            adverse_distance = max(
                0.0,
                entry - current
            )

        elif direction in (
            ProtectionDirection.SELL,
            ProtectionDirection.PUT,
        ):

            adverse_distance = max(
                0.0,
                current - entry
            )

        else:
            adverse_distance = 0.0

        progress = (
            adverse_distance
            / total_distance
            * 100.0
        )

        return max(
            0.0,
            min(100.0, progress)
        )

    # ========================================================
    # REMAINING EXPECTED GROWTH
    # ========================================================

    def calculate_remaining_growth(
        self,
        context: GrowthProtectionContext,
        favorable_move_pct: float,
    ) -> float:

        expected = abs(
            self._safe(
                context.expected_move_pct
            )
        )

        realized = max(
            0.0,
            self._safe(
                favorable_move_pct
            )
        )

        return max(
            0.0,
            expected - realized
        )

    # ========================================================
    # MARKET SUPPORT
    # ========================================================

    def calculate_market_support(
        self,
        context: GrowthProtectionContext,
    ) -> float:

        support = (
            context.thesis_strength * 0.25
            + context.evidence_strength * 0.20
            + context.structure_score * 0.15
            + context.participation_score * 0.15
            + context.liquidity_score * 0.10
            + context.relationship_score * 0.05
            + context.regime_score * 0.10
        )

        return self._clamp(
            support
        )

    # ========================================================
    # PROTECTION PRESSURE
    # ========================================================

    def calculate_protection_pressure(
        self,
        context: GrowthProtectionContext,
        adverse_move_pct: float,
        invalidation_progress_pct: float,
    ) -> float:
        """
        Calculates pressure against the active thesis.

        Adverse price movement is only one component.
        Anti-evidence, opposing pressure, thesis weakness,
        and exhaustion are also considered.
        """

        adverse_component = self._clamp(
            adverse_move_pct * 20.0
        )

        invalidation_component = (
            self._clamp(
                invalidation_progress_pct
            )
            * 0.30
        )

        anti_evidence_component = (
            self._clamp(
                context.anti_evidence_strength
            )
            * 0.25
        )

        opposing_component = (
            self._clamp(
                context.opposing_pressure
            )
            * 0.15
        )

        thesis_component = (
            (100.0 - self._clamp(
                context.thesis_strength
            ))
            * 0.15
        )

        exhaustion_component = (
            self._clamp(
                context.exhaustion_score
            )
            * 0.15
        )

        pressure = (
            adverse_component * 0.20
            + invalidation_component
            + anti_evidence_component
            + opposing_component
            + thesis_component
            + exhaustion_component
        )

        return self._clamp(
            pressure
        )

    # ========================================================
    # STATE CLASSIFICATION
    # ========================================================

    def classify_state(
        self,
        context: GrowthProtectionContext,
        pressure: float,
        target_progress_pct: float,
        invalidation_progress_pct: float,
    ) -> ProtectionState:

        if (
            context.current_price <= 0
            or context.entry_price <= 0
        ):
            return ProtectionState.INSUFFICIENT_DATA

        if (
            context.thesis_intact is False
            and
            context.anti_evidence_strength
            >= self.invalidation_threshold
        ):
            return ProtectionState.INVALIDATED

        if (
            invalidation_progress_pct
            >= 100.0
        ):
            return ProtectionState.INVALIDATED

        if (
            context.exhaustion_detected
            and
            context.exhaustion_score
            >= self.critical_threshold
        ):
            return ProtectionState.EXHAUSTED

        if (
            pressure
            >= self.invalidation_threshold
        ):
            return ProtectionState.INVALIDATED

        if (
            pressure
            >= self.critical_threshold
        ):
            return ProtectionState.CRITICAL

        if (
            pressure
            >= self.warning_threshold
        ):
            return ProtectionState.WARNING

        if (
            pressure
            >= self.watch_threshold
        ):
            return ProtectionState.WATCH

        return ProtectionState.NORMAL

    # ========================================================
    # TRIGGER DETECTION
    # ========================================================

    def detect_trigger(
        self,
        context: GrowthProtectionContext,
        state: ProtectionState,
        target_progress_pct: float,
        invalidation_progress_pct: float,
    ) -> ProtectionTrigger:

        if state == ProtectionState.INVALIDATED:

            if invalidation_progress_pct >= 100.0:
                return ProtectionTrigger.STRUCTURE_BREAK

            if (
                context.anti_evidence_detected
                and
                context.anti_evidence_strength
                >= self.invalidation_threshold
            ):
                return ProtectionTrigger.ANTI_EVIDENCE

            if not context.thesis_intact:
                return ProtectionTrigger.THESIS_WEAKENING

            return ProtectionTrigger.OPPOSITE_PRESSURE

        if state == ProtectionState.EXHAUSTED:

            return ProtectionTrigger.EXHAUSTION

        if (
            context.exhaustion_detected
            and
            context.exhaustion_score
            >= self.critical_threshold
        ):
            return ProtectionTrigger.EXHAUSTION

        if (
            context.anti_evidence_detected
            and
            context.anti_evidence_strength
            >= self.warning_threshold
        ):
            return ProtectionTrigger.ANTI_EVIDENCE

        if (
            context.participation_score
            < self.watch_threshold
        ):
            return ProtectionTrigger.PARTICIPATION_DECAY

        if (
            context.liquidity_score
            < self.watch_threshold
        ):
            return ProtectionTrigger.LIQUIDITY_DETERIORATION

        if (
            target_progress_pct >= 85.0
        ):
            return ProtectionTrigger.TARGET_APPROACH

        if (
            invalidation_progress_pct
            >= 75.0
        ):
            return ProtectionTrigger.PRICE_ADVERSE_MOVE

        if (
            context.opposing_pressure
            >= self.warning_threshold
        ):
            return ProtectionTrigger.OPPOSITE_PRESSURE

        return ProtectionTrigger.NONE

    # ========================================================
    # MEASURE
    # ========================================================

    def measure(
        self,
        context: GrowthProtectionContext,
    ) -> GrowthProtectionMeasurement:

        context.normalize()

        move = self.calculate_price_move(
            context
        )

        realized_move = move[
            "realized_move_pct"
        ]

        favorable_move = move[
            "favorable_move_pct"
        ]

        adverse_move = move[
            "adverse_move_pct"
        ]

        target_progress = (
            self.calculate_target_progress(
                context
            )
        )

        invalidation_progress = (
            self.calculate_invalidation_progress(
                context
            )
        )

        remaining_growth = (
            self.calculate_remaining_growth(
                context,
                favorable_move,
            )
        )

        market_support = (
            self.calculate_market_support(
                context
            )
        )

        protection_pressure = (
            self.calculate_protection_pressure(
                context,
                adverse_move,
                invalidation_progress,
            )
        )

        thesis_risk = self._clamp(
            100.0
            - context.thesis_strength
        )

        state = self.classify_state(
            context=context,
            pressure=protection_pressure,
            target_progress_pct=target_progress,
            invalidation_progress_pct=(
                invalidation_progress
            ),
        )

        trigger = self.detect_trigger(
            context=context,
            state=state,
            target_progress_pct=target_progress,
            invalidation_progress_pct=(
                invalidation_progress
            ),
        )

        reasons: List[str] = []
        warnings: List[str] = []

        if adverse_move > 0:
            reasons.append(
                "adverse_price_movement_present"
            )

        if (
            context.anti_evidence_detected
        ):
            reasons.append(
                "anti_evidence_detected"
            )

        if (
            context.exhaustion_detected
        ):
            reasons.append(
                "exhaustion_detected"
            )

        if (
            context.thesis_strength
            < self.watch_threshold
        ):
            reasons.append(
                "thesis_strength_weakened"
            )

        if (
            context.continuation_score
            >= self.critical_threshold
        ):
            reasons.append(
                "continuation_support_present"
            )

        if target_progress >= 85.0:
            warnings.append(
                "target_approaching"
            )

        if invalidation_progress >= 75.0:
            warnings.append(
                "invalidation_zone_approaching"
            )

        if (
            context.opposing_pressure
            >= self.warning_threshold
        ):
            warnings.append(
                "opposing_pressure_elevated"
            )

        return GrowthProtectionMeasurement(
            direction=context.direction,
            entry_distance_pct=(
                abs(
                    context.current_price
                    - context.entry_price
                )
                / context.entry_price
                * 100.0
                if context.entry_price > 0
                and context.current_price > 0
                else 0.0
            ),
            target_distance_pct=(
                abs(
                    context.target_price
                    - context.current_price
                )
                / context.current_price
                * 100.0
                if (
                    context.target_price > 0
                    and context.current_price > 0
                )
                else 0.0
            ),
            invalidation_distance_pct=(
                abs(
                    context.invalidation_price
                    - context.current_price
                )
                / context.current_price
                * 100.0
                if (
                    context.invalidation_price > 0
                    and context.current_price > 0
                )
                else 0.0
            ),
            realized_growth_pct=(
                realized_move
            ),
            remaining_expected_growth_pct=(
                remaining_growth
            ),
            adverse_move_pct=(
                adverse_move
            ),
            favorable_move_pct=(
                favorable_move
            ),
            target_progress_pct=(
                target_progress
            ),
            invalidation_progress_pct=(
                invalidation_progress
            ),
            protection_pressure=(
                protection_pressure
            ),
            thesis_risk=(
                thesis_risk
            ),
            anti_evidence_pressure=(
                context.anti_evidence_strength
            ),
            exhaustion_pressure=(
                context.exhaustion_score
            ),
            continuation_strength=(
                context.continuation_score
            ),
            market_support=(
                market_support
            ),
            state=state,
            trigger=trigger,
            reasons=reasons,
            warnings=warnings,
            metadata={
                "engine":
                    self.ENGINE_NAME,
                "engine_version":
                    self.ENGINE_VERSION,
            },
        ).normalize()

    # ========================================================
    # EVENT CREATION
    # ========================================================

    def create_event(
        self,
        context: GrowthProtectionContext,
        measurement: GrowthProtectionMeasurement,
    ) -> GrowthProtectionEvent:

        material = measurement.state in (
            ProtectionState.CRITICAL,
            ProtectionState.INVALIDATED,
            ProtectionState.EXHAUSTED,
        )

        reason = (
            measurement.reasons[0]
            if measurement.reasons
            else "protection_state_update"
        )

        return GrowthProtectionEvent(
            event_id=(
                f"GPE-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
            ),
            timestamp=datetime.utcnow().isoformat(),

            trigger=measurement.trigger,
            state=measurement.state,
            direction=context.direction,

            current_price=(
                context.current_price
            ),
            entry_price=(
                context.entry_price
            ),
            target_price=(
                context.target_price
            ),
            invalidation_price=(
                context.invalidation_price
            ),

            pressure_score=(
                measurement.protection_pressure
            ),
            thesis_strength=(
                context.thesis_strength
            ),
            anti_evidence_strength=(
                context.anti_evidence_strength
            ),
            exhaustion_strength=(
                context.exhaustion_score
            ),

            material=material,
            reason=reason,

            evidence_ids=list(
                context.metadata.get(
                    "evidence_ids",
                    []
                )
            ),

            source_engines=list(
                context.metadata.get(
                    "source_engines",
                    []
                )
            ),

            metadata={
                "target_progress_pct":
                    measurement.target_progress_pct,
                "invalidation_progress_pct":
                    measurement.invalidation_progress_pct,
                "remaining_expected_growth_pct":
                    measurement.remaining_expected_growth_pct,
            },
        )


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================

def measure_growth_protection(
    context: GrowthProtectionContext,
) -> GrowthProtectionMeasurement:

    engine = GrowthProtectionEngine()

    return engine.measure(
        context
    )


def build_growth_protection_event(
    context: GrowthProtectionContext,
    measurement: Optional[
        GrowthProtectionMeasurement
    ] = None,
) -> GrowthProtectionEvent:

    engine = GrowthProtectionEngine()

    if measurement is None:
        measurement = engine.measure(
            context
        )

    return engine.create_event(
        context=context,
        measurement=measurement,
    )


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [
    "ProtectionDirection",
    "ProtectionState",
    "ProtectionTrigger",
    "GrowthProtectionContext",
    "GrowthProtectionMeasurement",
    "GrowthProtectionEvent",
    "GrowthProtectionEngine",
    "measure_growth_protection",
    "build_growth_protection_event",
]
# ============================================================
# GROWTH PROTECTION ENGINE — PART 2
# Assessment / Thesis Health / Protection Quality
# ============================================================

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


# ============================================================
# ENUMS
# ============================================================

class ProtectionAction(str, Enum):
    MONITOR = "MONITOR"
    HOLD = "HOLD"
    WATCH = "WATCH"
    WARNING = "WARNING"
    RECALCULATE = "RECALCULATE"
    EXIT_REVIEW = "EXIT_REVIEW"
    INVALIDATED = "INVALIDATED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    UNKNOWN = "UNKNOWN"


class ThesisHealth(str, Enum):
    STRONG = "STRONG"
    HEALTHY = "HEALTHY"
    WEAKENING = "WEAKENING"
    DAMAGED = "DAMAGED"
    INVALIDATED = "INVALIDATED"
    EXHAUSTED = "EXHAUSTED"
    UNKNOWN = "UNKNOWN"


# ============================================================
# CONFIGURATION
# ============================================================

@dataclass
class ProtectionAssessmentConfig:
    """
    Configurable protection-assessment parameters.

    These are engineering baselines only.
    They are NOT permanent market truths.
    """

    # Pressure thresholds
    watch_pressure: float = 35.0
    warning_pressure: float = 55.0
    critical_pressure: float = 75.0
    invalidation_pressure: float = 90.0

    # Thesis health
    strong_support: float = 75.0
    healthy_support: float = 60.0
    weakening_support: float = 45.0
    damaged_support: float = 30.0

    # Material event thresholds
    anti_evidence_material: float = 50.0
    exhaustion_material: float = 60.0
    continuation_strong: float = 60.0

    # Target / invalidation proximity
    target_review_progress: float = 85.0
    invalidation_review_progress: float = 75.0

    def normalize(self) -> "ProtectionAssessmentConfig":
        self.watch_pressure = self._clamp(self.watch_pressure)
        self.warning_pressure = self._clamp(self.warning_pressure)
        self.critical_pressure = self._clamp(self.critical_pressure)
        self.invalidation_pressure = self._clamp(
            self.invalidation_pressure
        )

        self.strong_support = self._clamp(self.strong_support)
        self.healthy_support = self._clamp(self.healthy_support)
        self.weakening_support = self._clamp(self.weakening_support)
        self.damaged_support = self._clamp(self.damaged_support)

        self.anti_evidence_material = self._clamp(
            self.anti_evidence_material
        )
        self.exhaustion_material = self._clamp(
            self.exhaustion_material
        )
        self.continuation_strong = self._clamp(
            self.continuation_strong
        )

        self.target_review_progress = self._clamp(
            self.target_review_progress
        )
        self.invalidation_review_progress = self._clamp(
            self.invalidation_review_progress
        )

        return self

    @staticmethod
    def _clamp(value: Any) -> float:
        try:
            value = float(value)
        except (TypeError, ValueError):
            return 0.0

        return max(0.0, min(100.0, value))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "watch_pressure": self.watch_pressure,
            "warning_pressure": self.warning_pressure,
            "critical_pressure": self.critical_pressure,
            "invalidation_pressure": self.invalidation_pressure,
            "strong_support": self.strong_support,
            "healthy_support": self.healthy_support,
            "weakening_support": self.weakening_support,
            "damaged_support": self.damaged_support,
            "anti_evidence_material": self.anti_evidence_material,
            "exhaustion_material": self.exhaustion_material,
            "continuation_strong": self.continuation_strong,
            "target_review_progress": self.target_review_progress,
            "invalidation_review_progress": (
                self.invalidation_review_progress
            ),
        }


# ============================================================
# PROTECTION SCORE
# ============================================================

@dataclass
class GrowthProtectionScore:
    """
    Detailed protection-quality decomposition.

    This is measurement/intelligence support.
    It is NOT a final trading decision.
    """

    market_support: float = 0.0
    thesis_health_score: float = 0.0
    continuation_score: float = 0.0

    adverse_pressure: float = 0.0
    anti_evidence_pressure: float = 0.0
    exhaustion_pressure: float = 0.0
    invalidation_pressure: float = 0.0

    target_progress: float = 0.0
    remaining_growth: float = 0.0

    protection_quality: float = 0.0
    risk_pressure: float = 0.0

    reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def normalize(self) -> "GrowthProtectionScore":

        numeric_fields = [
            "market_support",
            "thesis_health_score",
            "continuation_score",
            "adverse_pressure",
            "anti_evidence_pressure",
            "exhaustion_pressure",
            "invalidation_pressure",
            "target_progress",
            "remaining_growth",
            "protection_quality",
            "risk_pressure",
        ]

        for name in numeric_fields:
            value = getattr(self, name)

            try:
                value = float(value)
            except (TypeError, ValueError):
                value = 0.0

            setattr(
                self,
                name,
                max(0.0, min(100.0, value))
            )

        return self

    def to_dict(self) -> Dict[str, Any]:
        self.normalize()

        return {
            "market_support": self.market_support,
            "thesis_health_score": self.thesis_health_score,
            "continuation_score": self.continuation_score,
            "adverse_pressure": self.adverse_pressure,
            "anti_evidence_pressure": self.anti_evidence_pressure,
            "exhaustion_pressure": self.exhaustion_pressure,
            "invalidation_pressure": self.invalidation_pressure,
            "target_progress": self.target_progress,
            "remaining_growth": self.remaining_growth,
            "protection_quality": self.protection_quality,
            "risk_pressure": self.risk_pressure,
            "reasons": list(self.reasons),
            "warnings": list(self.warnings),
        }


# ============================================================
# THESIS HEALTH ASSESSMENT
# ============================================================

@dataclass
class GrowthProtectionThesis:
    """
    Current health of the original trade thesis.
    """

    health: ThesisHealth = ThesisHealth.UNKNOWN
    support_score: float = 0.0

    structure_intact: bool = True
    participation_intact: bool = True
    liquidity_intact: bool = True
    relationship_intact: bool = True
    regime_compatible: bool = True

    anti_evidence_detected: bool = False
    exhaustion_detected: bool = False

    continuation_active: bool = False
    continuation_strength: float = 0.0

    reasons: List[str] = field(default_factory=list)
    evidence_ids: List[str] = field(default_factory=list)

    def normalize(self) -> "GrowthProtectionThesis":

        try:
            self.support_score = float(self.support_score)
        except (TypeError, ValueError):
            self.support_score = 0.0

        self.support_score = max(
            0.0,
            min(100.0, self.support_score)
        )

        try:
            self.continuation_strength = float(
                self.continuation_strength
            )
        except (TypeError, ValueError):
            self.continuation_strength = 0.0

        self.continuation_strength = max(
            0.0,
            min(100.0, self.continuation_strength)
        )

        if isinstance(self.health, str):
            try:
                self.health = ThesisHealth(self.health)
            except ValueError:
                self.health = ThesisHealth.UNKNOWN

        return self

    def to_dict(self) -> Dict[str, Any]:
        self.normalize()

        return {
            "health": self.health.value,
            "support_score": self.support_score,
            "structure_intact": self.structure_intact,
            "participation_intact": self.participation_intact,
            "liquidity_intact": self.liquidity_intact,
            "relationship_intact": self.relationship_intact,
            "regime_compatible": self.regime_compatible,
            "anti_evidence_detected": self.anti_evidence_detected,
            "exhaustion_detected": self.exhaustion_detected,
            "continuation_active": self.continuation_active,
            "continuation_strength": self.continuation_strength,
            "reasons": list(self.reasons),
            "evidence_ids": list(self.evidence_ids),
        }


# ============================================================
# PROTECTION ASSESSMENT
# ============================================================

@dataclass
class GrowthProtectionAssessment:
    """
    Complete current-state protection assessment.

    Important:
    - HOLD does not mean guaranteed profit.
    - EXIT_REVIEW does not execute an exit.
    - RECALCULATE requests reassessment.
    - D13 remains final decision authority.
    """

    assessment_id: str = ""
    timestamp: str = ""

    action: ProtectionAction = ProtectionAction.INSUFFICIENT_DATA
    state: ProtectionState = ProtectionState.UNKNOWN

    direction: ProtectionDirection = ProtectionDirection.UNKNOWN
    instrument: str = ""

    score: GrowthProtectionScore = field(
        default_factory=GrowthProtectionScore
    )

    thesis: GrowthProtectionThesis = field(
        default_factory=GrowthProtectionThesis
    )

    trigger: ProtectionTrigger = ProtectionTrigger.NONE

    recalculation_required: bool = False
    exit_review_required: bool = False
    thesis_review_required: bool = False

    material_change: bool = False

    reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def normalize(self) -> "GrowthProtectionAssessment":

        if not self.timestamp:
            self.timestamp = datetime.now(
                timezone.utc
            ).isoformat()

        if isinstance(self.action, str):
            try:
                self.action = ProtectionAction(self.action)
            except ValueError:
                self.action = ProtectionAction.UNKNOWN

        if isinstance(self.state, str):
            try:
                self.state = ProtectionState(self.state)
            except ValueError:
                self.state = ProtectionState.UNKNOWN

        if isinstance(self.direction, str):
            try:
                self.direction = ProtectionDirection(
                    self.direction
                )
            except ValueError:
                self.direction = ProtectionDirection.UNKNOWN

        if isinstance(self.trigger, str):
            try:
                self.trigger = ProtectionTrigger(
                    self.trigger
                )
            except ValueError:
                self.trigger = ProtectionTrigger.UNKNOWN

        self.score.normalize()
        self.thesis.normalize()

        return self

    def to_dict(self) -> Dict[str, Any]:
        self.normalize()

        return {
            "assessment_id": self.assessment_id,
            "timestamp": self.timestamp,
            "action": self.action.value,
            "state": self.state.value,
            "direction": self.direction.value,
            "instrument": self.instrument,
            "score": self.score.to_dict(),
            "thesis": self.thesis.to_dict(),
            "trigger": self.trigger.value,
            "recalculation_required": (
                self.recalculation_required
            ),
            "exit_review_required": (
                self.exit_review_required
            ),
            "thesis_review_required": (
                self.thesis_review_required
            ),
            "material_change": self.material_change,
            "reasons": list(self.reasons),
            "warnings": list(self.warnings),
            "metadata": dict(self.metadata),
        }


# ============================================================
# ENGINE PART 2
# ============================================================

class GrowthProtectionAssessmentEngine:
    """
    Part 2 assessment layer.

    Responsibility:
        Part 1 Measurement
              ↓
        Thesis Health
              ↓
        Protection Score
              ↓
        Assessment
              ↓
        Recalculation / Exit Review flags
              ↓
        D13

    This class does NOT execute trades.
    """

    def __init__(
        self,
        config: Optional[
            ProtectionAssessmentConfig
        ] = None,
    ):
        self.config = (
            config
            if config is not None
            else ProtectionAssessmentConfig()
        )

        self.config.normalize()

    # --------------------------------------------------------
    # Helpers
    # --------------------------------------------------------

    @staticmethod
    def _safe(value: Any) -> float:
        try:
            value = float(value)
        except (TypeError, ValueError):
            return 0.0

        if value != value:
            return 0.0

        return value

    @staticmethod
    def _clamp(value: Any) -> float:
        return max(
            0.0,
            min(100.0, GrowthProtectionAssessmentEngine._safe(value))
        )

    @staticmethod
    def _directional(direction: ProtectionDirection) -> bool:
        return direction in (
            ProtectionDirection.BUY,
            ProtectionDirection.SELL,
            ProtectionDirection.CALL,
            ProtectionDirection.PUT,
        )

    # --------------------------------------------------------
    # Thesis Health
    # --------------------------------------------------------

    def calculate_thesis_health(
        self,
        context: GrowthProtectionContext,
        measurement: GrowthProtectionMeasurement,
    ) -> GrowthProtectionThesis:

        support = self._clamp(
            measurement.market_support
        )

        reasons: List[str] = []

        if context.thesis_intact:
            reasons.append(
                "Original thesis currently remains intact."
            )
        else:
            reasons.append(
                "Original thesis is no longer fully intact."
            )

        if context.anti_evidence_detected:
            reasons.append(
                "Meaningful anti-evidence is present."
            )

        if context.exhaustion_detected:
            reasons.append(
                "Exhaustion evidence is present."
            )

        if context.structure_score < 40:
            reasons.append(
                "Structure support is weak."
            )

        if context.participation_score < 40:
            reasons.append(
                "Participation support is weak."
            )

        if context.liquidity_score < 40:
            reasons.append(
                "Liquidity support is weak."
            )

        if context.regime_score < 40:
            reasons.append(
                "Current regime compatibility is weak."
            )

        if (
            not context.thesis_intact
            or measurement.invalidation_progress >= 90
        ):
            health = ThesisHealth.INVALIDATED

        elif (
            context.exhaustion_detected
            and measurement.exhaustion_pressure
            >= self.config.exhaustion_material
        ):
            health = ThesisHealth.EXHAUSTED

        elif support >= self.config.strong_support:
            health = ThesisHealth.STRONG

        elif support >= self.config.healthy_support:
            health = ThesisHealth.HEALTHY

        elif support >= self.config.weakening_support:
            health = ThesisHealth.WEAKENING

        elif support >= self.config.damaged_support:
            health = ThesisHealth.DAMAGED

        else:
            health = ThesisHealth.INVALIDATED

        return GrowthProtectionThesis(
            health=health,
            support_score=support,

            structure_intact=(
                context.structure_score >= 40
            ),
            participation_intact=(
                context.participation_score >= 40
            ),
            liquidity_intact=(
                context.liquidity_score >= 40
            ),
            relationship_intact=(
                context.relationship_score >= 40
            ),
            regime_compatible=(
                context.regime_score >= 40
            ),

            anti_evidence_detected=(
                context.anti_evidence_detected
            ),
            exhaustion_detected=(
                context.exhaustion_detected
            ),

            continuation_active=(
                context.continuation_score
                >= self.config.continuation_strong
            ),
            continuation_strength=self._clamp(
                context.continuation_score
            ),

            reasons=reasons,
        )

    # --------------------------------------------------------
    # Protection Score
    # --------------------------------------------------------

    def calculate_protection_score(
        self,
        context: GrowthProtectionContext,
        measurement: GrowthProtectionMeasurement,
        thesis: GrowthProtectionThesis,
    ) -> GrowthProtectionScore:

        market_support = self._clamp(
            measurement.market_support
        )

        adverse_pressure = self._clamp(
            measurement.adverse_move_pct * 10.0
        )

        anti_evidence_pressure = self._clamp(
            context.anti_evidence_strength
        )

        exhaustion_pressure = self._clamp(
            context.exhaustion_score
        )

        invalidation_pressure = self._clamp(
            measurement.invalidation_progress
        )

        continuation = self._clamp(
            context.continuation_score
        )

        target_progress = self._clamp(
            measurement.target_progress
        )

        remaining_growth = self._clamp(
            measurement.remaining_growth
        )

        # Risk pressure is intentionally a separate measurement.
        risk_pressure = self._clamp(
            (
                adverse_pressure * 0.20
                + anti_evidence_pressure * 0.25
                + exhaustion_pressure * 0.20
                + invalidation_pressure * 0.25
                + (100.0 - market_support) * 0.10
            )
        )

        # Protection quality rewards thesis support and continuation,
        # while penalizing material deterioration.
        protection_quality = self._clamp(
            (
                market_support * 0.30
                + thesis.support_score * 0.25
                + continuation * 0.15
                + remaining_growth * 0.10
                + (100.0 - risk_pressure) * 0.20
            )
        )

        reasons: List[str] = []
        warnings: List[str] = []

        if thesis.health in (
            ThesisHealth.STRONG,
            ThesisHealth.HEALTHY,
        ):
            reasons.append(
                "Trade thesis remains sufficiently supported."
            )

        if continuation >= self.config.continuation_strong:
            reasons.append(
                "Continuation evidence remains active."
            )

        if target_progress >= self.config.target_review_progress:
            warnings.append(
                "Target-progress is approaching review zone."
            )

        if (
            invalidation_pressure
            >= self.config.invalidation_review_progress
        ):
            warnings.append(
                "Invalidation proximity requires thesis review."
            )

        if (
            anti_evidence_pressure
            >= self.config.anti_evidence_material
        ):
            warnings.append(
                "Meaningful anti-evidence detected."
            )

        if (
            exhaustion_pressure
            >= self.config.exhaustion_material
        ):
            warnings.append(
                "Meaningful exhaustion pressure detected."
            )

        return GrowthProtectionScore(
            market_support=market_support,
            thesis_health_score=thesis.support_score,
            continuation_score=continuation,

            adverse_pressure=adverse_pressure,
            anti_evidence_pressure=anti_evidence_pressure,
            exhaustion_pressure=exhaustion_pressure,
            invalidation_pressure=invalidation_pressure,

            target_progress=target_progress,
            remaining_growth=remaining_growth,

            protection_quality=protection_quality,
            risk_pressure=risk_pressure,

            reasons=reasons,
            warnings=warnings,
        )

    # --------------------------------------------------------
    # Action Classification
    # --------------------------------------------------------

    def classify_action(
        self,
        context: GrowthProtectionContext,
        measurement: GrowthProtectionMeasurement,
        thesis: GrowthProtectionThesis,
        score: GrowthProtectionScore,
    ) -> ProtectionAction:

        if not self._directional(context.direction):
            return ProtectionAction.INSUFFICIENT_DATA

        if (
            measurement.state
            == ProtectionState.INSUFFICIENT_DATA
        ):
            return ProtectionAction.INSUFFICIENT_DATA

        if (
            thesis.health
            == ThesisHealth.INVALIDATED
        ):
            return ProtectionAction.INVALIDATED

        if (
            thesis.health
            == ThesisHealth.EXHAUSTED
        ):
            return ProtectionAction.EXIT_REVIEW

        if (
            score.invalidation_pressure
            >= self.config.invalidation_pressure
        ):
            return ProtectionAction.EXIT_REVIEW

        if (
            score.exhaustion_pressure
            >= self.config.exhaustion_material
        ):
            return ProtectionAction.EXIT_REVIEW

        if (
            score.anti_evidence_pressure
            >= self.config.anti_evidence_material
        ):
            return ProtectionAction.RECALCULATE

        if (
            score.invalidation_pressure
            >= self.config.invalidation_review_progress
        ):
            return ProtectionAction.RECALCULATE

        if (
            score.target_progress
            >= self.config.target_review_progress
        ):
            return ProtectionAction.WATCH

        if (
            score.risk_pressure
            >= self.config.critical_pressure
        ):
            return ProtectionAction.WARNING

        if (
            score.risk_pressure
            >= self.config.warning_pressure
        ):
            return ProtectionAction.WATCH

        if (
            thesis.health
            in (
                ThesisHealth.STRONG,
                ThesisHealth.HEALTHY,
            )
            and score.protection_quality >= 60
        ):
            return ProtectionAction.HOLD

        return ProtectionAction.MONITOR

    # --------------------------------------------------------
    # Assessment
    # --------------------------------------------------------

    def assess(
        self,
        context: GrowthProtectionContext,
        measurement: GrowthProtectionMeasurement,
        *,
        assessment_id: str = "",
    ) -> GrowthProtectionAssessment:

        context.normalize()
        measurement.normalize()

        thesis = self.calculate_thesis_health(
            context,
            measurement,
        )

        score = self.calculate_protection_score(
            context,
            measurement,
            thesis,
        )

        action = self.classify_action(
            context,
            measurement,
            thesis,
            score,
        )

        thesis_review_required = (
            thesis.health
            in (
                ThesisHealth.WEAKENING,
                ThesisHealth.DAMAGED,
                ThesisHealth.INVALIDATED,
                ThesisHealth.EXHAUSTED,
            )
        )

        recalculation_required = (
            action
            == ProtectionAction.RECALCULATE
            or context.anti_evidence_detected
            or (
                measurement.invalidation_progress
                >= self.config.invalidation_review_progress
            )
        )

        exit_review_required = (
            action
            in (
                ProtectionAction.EXIT_REVIEW,
                ProtectionAction.INVALIDATED,
            )
            or thesis.health
            in (
                ThesisHealth.INVALIDATED,
                ThesisHealth.EXHAUSTED,
            )
        )

        material_change = (
            recalculation_required
            or exit_review_required
            or context.anti_evidence_detected
            or context.exhaustion_detected
            or (
                measurement.target_progress
                >= self.config.target_review_progress
            )
        )

        reasons = list(measurement.reasons)
        reasons.extend(score.reasons)
        reasons.extend(thesis.reasons)

        warnings = list(measurement.warnings)
        warnings.extend(score.warnings)

        return GrowthProtectionAssessment(
            assessment_id=assessment_id,
            timestamp=datetime.now(
                timezone.utc
            ).isoformat(),

            action=action,
            state=measurement.state,
            direction=context.direction,
            instrument=str(
                context.metadata.get(
                    "instrument",
                    ""
                )
            ),

            score=score,
            thesis=thesis,

            trigger=measurement.trigger,

            recalculation_required=(
                recalculation_required
            ),
            exit_review_required=(
                exit_review_required
            ),
            thesis_review_required=(
                thesis_review_required
            ),

            material_change=material_change,

            reasons=reasons,
            warnings=warnings,

            metadata={
                "engine": "GrowthProtectionAssessmentEngine",
                "part": 2,
            },
        )


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================

def assess_growth_protection(
    context: GrowthProtectionContext,
    measurement: GrowthProtectionMeasurement,
    *,
    config: Optional[
        ProtectionAssessmentConfig
    ] = None,
    assessment_id: str = "",
) -> GrowthProtectionAssessment:

    engine = GrowthProtectionAssessmentEngine(
        config=config
    )

    return engine.assess(
        context,
        measurement,
        assessment_id=assessment_id,
    )


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "ProtectionAction",
    "ThesisHealth",
    "ProtectionAssessmentConfig",
    "GrowthProtectionScore",
    "GrowthProtectionThesis",
    "GrowthProtectionAssessment",
    "GrowthProtectionAssessmentEngine",
    "assess_growth_protection",
]
# ============================================================
# GROWTH PROTECTION ENGINE — PART 3
# Lifecycle Monitoring / State Transition / History
# ============================================================

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ============================================================
# PROTECTION STATE TRANSITION
# ============================================================

@dataclass
class ProtectionStateTransition:
    """
    Records a meaningful change in protection state.
    """

    transition_id: str = ""
    timestamp: str = ""

    previous_state: ProtectionState = ProtectionState.UNKNOWN
    current_state: ProtectionState = ProtectionState.UNKNOWN

    previous_action: ProtectionAction = ProtectionAction.UNKNOWN
    current_action: ProtectionAction = ProtectionAction.UNKNOWN

    previous_thesis_health: ThesisHealth = ThesisHealth.UNKNOWN
    current_thesis_health: ThesisHealth = ThesisHealth.UNKNOWN

    pressure_change: float = 0.0
    protection_quality_change: float = 0.0

    material: bool = False
    reasons: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def normalize(self) -> "ProtectionStateTransition":

        if not self.timestamp:
            self.timestamp = datetime.now(
                timezone.utc
            ).isoformat()

        if isinstance(self.previous_state, str):
            try:
                self.previous_state = ProtectionState(
                    self.previous_state
                )
            except ValueError:
                self.previous_state = ProtectionState.UNKNOWN

        if isinstance(self.current_state, str):
            try:
                self.current_state = ProtectionState(
                    self.current_state
                )
            except ValueError:
                self.current_state = ProtectionState.UNKNOWN

        if isinstance(self.previous_action, str):
            try:
                self.previous_action = ProtectionAction(
                    self.previous_action
                )
            except ValueError:
                self.previous_action = ProtectionAction.UNKNOWN

        if isinstance(self.current_action, str):
            try:
                self.current_action = ProtectionAction(
                    self.current_action
                )
            except ValueError:
                self.current_action = ProtectionAction.UNKNOWN

        if isinstance(self.previous_thesis_health, str):
            try:
                self.previous_thesis_health = ThesisHealth(
                    self.previous_thesis_health
                )
            except ValueError:
                self.previous_thesis_health = ThesisHealth.UNKNOWN

        if isinstance(self.current_thesis_health, str):
            try:
                self.current_thesis_health = ThesisHealth(
                    self.current_thesis_health
                )
            except ValueError:
                self.current_thesis_health = ThesisHealth.UNKNOWN

        return self

    def to_dict(self) -> Dict[str, Any]:
        self.normalize()

        return {
            "transition_id": self.transition_id,
            "timestamp": self.timestamp,
            "previous_state": self.previous_state.value,
            "current_state": self.current_state.value,
            "previous_action": self.previous_action.value,
            "current_action": self.current_action.value,
            "previous_thesis_health": (
                self.previous_thesis_health.value
            ),
            "current_thesis_health": (
                self.current_thesis_health.value
            ),
            "pressure_change": self.pressure_change,
            "protection_quality_change": (
                self.protection_quality_change
            ),
            "material": self.material,
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }


# ============================================================
# PROTECTION HISTORY ENTRY
# ============================================================

@dataclass
class ProtectionHistoryEntry:
    """
    Immutable-style snapshot of protection intelligence.
    """

    timestamp: str = ""

    state: ProtectionState = ProtectionState.UNKNOWN
    action: ProtectionAction = ProtectionAction.UNKNOWN
    thesis_health: ThesisHealth = ThesisHealth.UNKNOWN

    protection_pressure: float = 0.0
    protection_quality: float = 0.0
    market_support: float = 0.0
    risk_pressure: float = 0.0

    target_progress: float = 0.0
    invalidation_progress: float = 0.0
    remaining_growth: float = 0.0

    anti_evidence_pressure: float = 0.0
    exhaustion_pressure: float = 0.0
    continuation_score: float = 0.0

    trigger: ProtectionTrigger = ProtectionTrigger.NONE

    recalculation_required: bool = False
    exit_review_required: bool = False

    material_change: bool = False

    reasons: List[str] = field(default_factory=list)

    def normalize(self) -> "ProtectionHistoryEntry":

        if not self.timestamp:
            self.timestamp = datetime.now(
                timezone.utc
            ).isoformat()

        if isinstance(self.state, str):
            try:
                self.state = ProtectionState(
                    self.state
                )
            except ValueError:
                self.state = ProtectionState.UNKNOWN

        if isinstance(self.action, str):
            try:
                self.action = ProtectionAction(
                    self.action
                )
            except ValueError:
                self.action = ProtectionAction.UNKNOWN

        if isinstance(self.thesis_health, str):
            try:
                self.thesis_health = ThesisHealth(
                    self.thesis_health
                )
            except ValueError:
                self.thesis_health = ThesisHealth.UNKNOWN

        if isinstance(self.trigger, str):
            try:
                self.trigger = ProtectionTrigger(
                    self.trigger
                )
            except ValueError:
                self.trigger = ProtectionTrigger.UNKNOWN

        numeric_fields = [
            "protection_pressure",
            "protection_quality",
            "market_support",
            "risk_pressure",
            "target_progress",
            "invalidation_progress",
            "remaining_growth",
            "anti_evidence_pressure",
            "exhaustion_pressure",
            "continuation_score",
        ]

        for field_name in numeric_fields:
            try:
                value = float(
                    getattr(self, field_name)
                )
            except (TypeError, ValueError):
                value = 0.0

            setattr(
                self,
                field_name,
                max(0.0, min(100.0, value))
            )

        return self

    def to_dict(self) -> Dict[str, Any]:
        self.normalize()

        return {
            "timestamp": self.timestamp,
            "state": self.state.value,
            "action": self.action.value,
            "thesis_health": self.thesis_health.value,
            "protection_pressure": self.protection_pressure,
            "protection_quality": self.protection_quality,
            "market_support": self.market_support,
            "risk_pressure": self.risk_pressure,
            "target_progress": self.target_progress,
            "invalidation_progress": (
                self.invalidation_progress
            ),
            "remaining_growth": self.remaining_growth,
            "anti_evidence_pressure": (
                self.anti_evidence_pressure
            ),
            "exhaustion_pressure": (
                self.exhaustion_pressure
            ),
            "continuation_score": (
                self.continuation_score
            ),
            "trigger": self.trigger.value,
            "recalculation_required": (
                self.recalculation_required
            ),
            "exit_review_required": (
                self.exit_review_required
            ),
            "material_change": self.material_change,
            "reasons": list(self.reasons),
        }


# ============================================================
# PROTECTION MONITOR
# ============================================================

@dataclass
class GrowthProtectionMonitor:
    """
    Tracks the evolution of one active opportunity/trade thesis.
    """

    monitor_id: str = ""
    instrument: str = ""

    first_seen_at: str = ""
    last_seen_at: str = ""

    observation_count: int = 0

    current_state: ProtectionState = ProtectionState.UNKNOWN
    previous_state: ProtectionState = ProtectionState.UNKNOWN

    current_action: ProtectionAction = ProtectionAction.UNKNOWN
    previous_action: ProtectionAction = ProtectionAction.UNKNOWN

    current_thesis_health: ThesisHealth = ThesisHealth.UNKNOWN
    previous_thesis_health: ThesisHealth = ThesisHealth.UNKNOWN

    current_pressure: float = 0.0
    previous_pressure: float = 0.0

    current_quality: float = 0.0
    previous_quality: float = 0.0

    pressure_change: float = 0.0
    quality_change: float = 0.0

    deteriorating: bool = False
    improving: bool = False

    thesis_weakened: bool = False
    thesis_invalidated: bool = False

    anti_evidence_active: bool = False
    exhaustion_active: bool = False
    continuation_active: bool = False

    recalculation_required: bool = False
    exit_review_required: bool = False

    transitions: List[ProtectionStateTransition] = field(
        default_factory=list
    )

    history: List[ProtectionHistoryEntry] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def normalize(self) -> "GrowthProtectionMonitor":

        self.observation_count = max(
            0,
            int(self.observation_count)
        )

        return self

    def add_history(
        self,
        entry: ProtectionHistoryEntry,
        max_history: int = 500,
    ) -> None:

        entry.normalize()

        self.history.append(entry)

        if len(self.history) > max_history:
            self.history = self.history[
                -max_history:
            ]

    def add_transition(
        self,
        transition: ProtectionStateTransition,
        max_transitions: int = 200,
    ) -> None:

        transition.normalize()

        self.transitions.append(
            transition
        )

        if len(self.transitions) > max_transitions:
            self.transitions = self.transitions[
                -max_transitions:
            ]

    def to_dict(self) -> Dict[str, Any]:

        return {
            "monitor_id": self.monitor_id,
            "instrument": self.instrument,
            "first_seen_at": self.first_seen_at,
            "last_seen_at": self.last_seen_at,
            "observation_count": self.observation_count,

            "current_state": self.current_state.value,
            "previous_state": self.previous_state.value,

            "current_action": self.current_action.value,
            "previous_action": self.previous_action.value,

            "current_thesis_health": (
                self.current_thesis_health.value
            ),
            "previous_thesis_health": (
                self.previous_thesis_health.value
            ),

            "current_pressure": self.current_pressure,
            "previous_pressure": self.previous_pressure,

            "current_quality": self.current_quality,
            "previous_quality": self.previous_quality,

            "pressure_change": self.pressure_change,
            "quality_change": self.quality_change,

            "deteriorating": self.deteriorating,
            "improving": self.improving,

            "thesis_weakened": self.thesis_weakened,
            "thesis_invalidated": self.thesis_invalidated,

            "anti_evidence_active": (
                self.anti_evidence_active
            ),
            "exhaustion_active": (
                self.exhaustion_active
            ),
            "continuation_active": (
                self.continuation_active
            ),

            "recalculation_required": (
                self.recalculation_required
            ),
            "exit_review_required": (
                self.exit_review_required
            ),

            "transitions": [
                item.to_dict()
                for item in self.transitions
            ],

            "history": [
                item.to_dict()
                for item in self.history
            ],

            "metadata": dict(self.metadata),
        }


# ============================================================
# MONITORING ENGINE
# ============================================================

class GrowthProtectionMonitoringEngine:
    """
    Part 3 lifecycle monitoring engine.

    Responsibilities:
        - compare consecutive assessments
        - detect meaningful deterioration/improvement
        - maintain protection history
        - track thesis lifecycle
        - expose recalculation / exit-review conditions

    It does NOT execute an order.
    """

    def __init__(
        self,
        max_history: int = 500,
        max_transitions: int = 200,
    ):
        self.max_history = max_history
        self.max_transitions = max_transitions

        self.monitors: Dict[
            str,
            GrowthProtectionMonitor
        ] = {}

    # --------------------------------------------------------
    # Helpers
    # --------------------------------------------------------

    @staticmethod
    def _safe(value: Any) -> float:
        try:
            value = float(value)
        except (TypeError, ValueError):
            return 0.0

        if value != value:
            return 0.0

        return value

    # --------------------------------------------------------
    # History Conversion
    # --------------------------------------------------------

    def assessment_to_history(
        self,
        assessment: GrowthProtectionAssessment,
    ) -> ProtectionHistoryEntry:

        return ProtectionHistoryEntry(
            timestamp=assessment.timestamp,

            state=assessment.state,
            action=assessment.action,
            thesis_health=assessment.thesis.health,

            protection_pressure=(
                assessment.score.risk_pressure
            ),
            protection_quality=(
                assessment.score.protection_quality
            ),
            market_support=(
                assessment.score.market_support
            ),
            risk_pressure=(
                assessment.score.risk_pressure
            ),

            target_progress=(
                assessment.score.target_progress
            ),
            invalidation_progress=(
                assessment.score.invalidation_pressure
            ),
            remaining_growth=(
                assessment.score.remaining_growth
            ),

            anti_evidence_pressure=(
                assessment.score.anti_evidence_pressure
            ),
            exhaustion_pressure=(
                assessment.score.exhaustion_pressure
            ),
            continuation_score=(
                assessment.score.continuation_score
            ),

            trigger=assessment.trigger,

            recalculation_required=(
                assessment.recalculation_required
            ),
            exit_review_required=(
                assessment.exit_review_required
            ),

            material_change=(
                assessment.material_change
            ),

            reasons=list(assessment.reasons),
        )

    # --------------------------------------------------------
    # Transition Detection
    # --------------------------------------------------------

    def detect_transition(
        self,
        previous: Optional[
            ProtectionHistoryEntry
        ],
        current: ProtectionHistoryEntry,
        *,
        transition_id: str = "",
    ) -> Optional[ProtectionStateTransition]:

        if previous is None:
            return None

        pressure_change = (
            current.protection_pressure
            - previous.protection_pressure
        )

        quality_change = (
            current.protection_quality
            - previous.protection_quality
        )

        state_changed = (
            previous.state != current.state
        )

        action_changed = (
            previous.action != current.action
        )

        thesis_changed = (
            previous.thesis_health
            != current.thesis_health
        )

        material = (
            state_changed
            or action_changed
            or thesis_changed
            or abs(pressure_change) >= 15.0
            or abs(quality_change) >= 15.0
            or current.material_change
        )

        if not material:
            return None

        reasons: List[str] = []

        if state_changed:
            reasons.append(
                "Protection state changed."
            )

        if action_changed:
            reasons.append(
                "Protection action changed."
            )

        if thesis_changed:
            reasons.append(
                "Trade thesis health changed."
            )

        if pressure_change >= 15:
            reasons.append(
                "Protection pressure materially increased."
            )

        elif pressure_change <= -15:
            reasons.append(
                "Protection pressure materially decreased."
            )

        if quality_change >= 15:
            reasons.append(
                "Protection quality materially improved."
            )

        elif quality_change <= -15:
            reasons.append(
                "Protection quality materially deteriorated."
            )

        return ProtectionStateTransition(
            transition_id=transition_id,
            timestamp=current.timestamp,

            previous_state=previous.state,
            current_state=current.state,

            previous_action=previous.action,
            current_action=current.action,

            previous_thesis_health=(
                previous.thesis_health
            ),
            current_thesis_health=(
                current.thesis_health
            ),

            pressure_change=pressure_change,
            protection_quality_change=quality_change,

            material=True,
            reasons=reasons,
        )

    # --------------------------------------------------------
    # Update Monitor
    # --------------------------------------------------------

    def update(
        self,
        assessment: GrowthProtectionAssessment,
        *,
        monitor_id: Optional[str] = None,
    ) -> GrowthProtectionMonitor:

        assessment.normalize()

        if monitor_id is None:
            monitor_id = (
                assessment.assessment_id
                or assessment.instrument
                or "growth_protection_default"
            )

        monitor = self.monitors.get(
            monitor_id
        )

        if monitor is None:

            monitor = GrowthProtectionMonitor(
                monitor_id=monitor_id,
                instrument=assessment.instrument,
                first_seen_at=assessment.timestamp,
            )

            self.monitors[
                monitor_id
            ] = monitor

        current = self.assessment_to_history(
            assessment
        )

        previous = (
            monitor.history[-1]
            if monitor.history
            else None
        )

        transition = self.detect_transition(
            previous,
            current,
            transition_id=(
                f"{monitor_id}_"
                f"{monitor.observation_count + 1}"
            ),
        )

        # Previous values
        if previous is not None:
            monitor.previous_state = (
                previous.state
            )
            monitor.previous_action = (
                previous.action
            )
            monitor.previous_thesis_health = (
                previous.thesis_health
            )

            monitor.previous_pressure = (
                previous.protection_pressure
            )
            monitor.previous_quality = (
                previous.protection_quality
            )

        # Current values
        monitor.current_state = (
            current.state
        )
        monitor.current_action = (
            current.action
        )
        monitor.current_thesis_health = (
            current.thesis_health
        )

        monitor.current_pressure = (
            current.protection_pressure
        )
        monitor.current_quality = (
            current.protection_quality
        )

        monitor.pressure_change = (
            current.protection_pressure
            - monitor.previous_pressure
        )

        monitor.quality_change = (
            current.protection_quality
            - monitor.previous_quality
        )

        monitor.deteriorating = (
            monitor.pressure_change >= 10.0
            or monitor.quality_change <= -10.0
            or (
                previous is not None
                and current.thesis_health
                in (
                    ThesisHealth.WEAKENING,
                    ThesisHealth.DAMAGED,
                    ThesisHealth.INVALIDATED,
                    ThesisHealth.EXHAUSTED,
                )
                and previous.thesis_health
                in (
                    ThesisHealth.STRONG,
                    ThesisHealth.HEALTHY,
                )
            )
        )

        monitor.improving = (
            monitor.pressure_change <= -10.0
            or monitor.quality_change >= 10.0
        )

        monitor.thesis_weakened = (
            current.thesis_health
            in (
                ThesisHealth.WEAKENING,
                ThesisHealth.DAMAGED,
            )
        )

        monitor.thesis_invalidated = (
            current.thesis_health
            in (
                ThesisHealth.INVALIDATED,
                ThesisHealth.EXHAUSTED,
            )
        )

        monitor.anti_evidence_active = (
            current.anti_evidence_pressure
            >= 50.0
        )

        monitor.exhaustion_active = (
            current.exhaustion_pressure
            >= 60.0
        )

        monitor.continuation_active = (
            current.continuation_score
            >= 60.0
        )

        monitor.recalculation_required = (
            current.recalculation_required
        )

        monitor.exit_review_required = (
            current.exit_review_required
        )

        monitor.last_seen_at = (
            current.timestamp
        )

        monitor.observation_count += 1

        monitor.add_history(
            current,
            max_history=self.max_history,
        )

        if transition is not None:
            monitor.add_transition(
                transition,
                max_transitions=self.max_transitions,
            )

        return monitor

    # --------------------------------------------------------
    # Query Methods
    # --------------------------------------------------------

    def get_monitor(
        self,
        monitor_id: str,
    ) -> Optional[GrowthProtectionMonitor]:

        return self.monitors.get(
            monitor_id
        )

    def get_deteriorating(
        self,
    ) -> List[GrowthProtectionMonitor]:

        return [
            monitor
            for monitor in self.monitors.values()
            if monitor.deteriorating
        ]

    def get_improving(
        self,
    ) -> List[GrowthProtectionMonitor]:

        return [
            monitor
            for monitor in self.monitors.values()
            if monitor.improving
        ]

    def get_recalculation_required(
        self,
    ) -> List[GrowthProtectionMonitor]:

        return [
            monitor
            for monitor in self.monitors.values()
            if monitor.recalculation_required
        ]

    def get_exit_review_required(
        self,
    ) -> List[GrowthProtectionMonitor]:

        return [
            monitor
            for monitor in self.monitors.values()
            if monitor.exit_review_required
        ]

    def get_invalidated(
        self,
    ) -> List[GrowthProtectionMonitor]:

        return [
            monitor
            for monitor in self.monitors.values()
            if monitor.thesis_invalidated
        ]

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    def summary(self) -> Dict[str, Any]:

        monitors = list(
            self.monitors.values()
        )

        return {
            "monitor_count": len(monitors),

            "deteriorating_count": sum(
                1
                for item in monitors
                if item.deteriorating
            ),

            "improving_count": sum(
                1
                for item in monitors
                if item.improving
            ),

            "recalculation_required_count": sum(
                1
                for item in monitors
                if item.recalculation_required
            ),

            "exit_review_required_count": sum(
                1
                for item in monitors
                if item.exit_review_required
            ),

            "invalidated_count": sum(
                1
                for item in monitors
                if item.thesis_invalidated
            ),

            "continuation_active_count": sum(
                1
                for item in monitors
                if item.continuation_active
            ),
        }

    def to_dict(self) -> Dict[str, Any]:

        return {
            "summary": self.summary(),
            "monitors": {
                key: value.to_dict()
                for key, value
                in self.monitors.items()
            },
        }


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================

def update_growth_protection_monitor(
    engine: GrowthProtectionMonitoringEngine,
    assessment: GrowthProtectionAssessment,
    *,
    monitor_id: Optional[str] = None,
) -> GrowthProtectionMonitor:

    return engine.update(
        assessment,
        monitor_id=monitor_id,
    )


# ============================================================
# PUBLIC API
# ============================================================

__all__ += [
    "ProtectionStateTransition",
    "ProtectionHistoryEntry",
    "GrowthProtectionMonitor",
    "GrowthProtectionMonitoringEngine",
    "update_growth_protection_monitor",
]
# ============================================================
# GROWTH PROTECTION ENGINE — PART 4
# Intelligence State / D13 Feed / BlackBox Export
# ============================================================

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ============================================================
# PROTECTION INTELLIGENCE STATE
# ============================================================

@dataclass
class GrowthProtectionIntelligence:
    """
    Normalized protection intelligence state.

    This is an upstream intelligence object.
    D13 remains the final decision authority.
    """

    intelligence_id: str = ""
    timestamp: str = ""

    instrument: str = ""
    direction: ProtectionDirection = (
        ProtectionDirection.UNKNOWN
    )

    state: ProtectionState = ProtectionState.UNKNOWN
    action: ProtectionAction = ProtectionAction.UNKNOWN
    thesis_health: ThesisHealth = ThesisHealth.UNKNOWN
    trigger: ProtectionTrigger = ProtectionTrigger.NONE

    protection_quality: float = 0.0
    protection_pressure: float = 0.0
    market_support: float = 0.0
    risk_pressure: float = 0.0

    continuation_score: float = 0.0
    anti_evidence_pressure: float = 0.0
    exhaustion_pressure: float = 0.0

    target_progress: float = 0.0
    invalidation_progress: float = 0.0
    remaining_growth: float = 0.0

    thesis_intact: bool = True
    recalculation_required: bool = False
    thesis_review_required: bool = False
    exit_review_required: bool = False

    improving: bool = False
    deteriorating: bool = False
    material_change: bool = False

    reasons: List[str] = field(
        default_factory=list
    )
    warnings: List[str] = field(
        default_factory=list
    )

    source_engines: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def normalize(self) -> "GrowthProtectionIntelligence":

        if not self.timestamp:
            self.timestamp = datetime.now(
                timezone.utc
            ).isoformat()

        if isinstance(self.direction, str):
            try:
                self.direction = ProtectionDirection(
                    self.direction
                )
            except ValueError:
                self.direction = ProtectionDirection.UNKNOWN

        if isinstance(self.state, str):
            try:
                self.state = ProtectionState(
                    self.state
                )
            except ValueError:
                self.state = ProtectionState.UNKNOWN

        if isinstance(self.action, str):
            try:
                self.action = ProtectionAction(
                    self.action
                )
            except ValueError:
                self.action = ProtectionAction.UNKNOWN

        if isinstance(self.thesis_health, str):
            try:
                self.thesis_health = ThesisHealth(
                    self.thesis_health
                )
            except ValueError:
                self.thesis_health = ThesisHealth.UNKNOWN

        if isinstance(self.trigger, str):
            try:
                self.trigger = ProtectionTrigger(
                    self.trigger
                )
            except ValueError:
                self.trigger = ProtectionTrigger.UNKNOWN

        numeric_fields = [
            "protection_quality",
            "protection_pressure",
            "market_support",
            "risk_pressure",
            "continuation_score",
            "anti_evidence_pressure",
            "exhaustion_pressure",
            "target_progress",
            "invalidation_progress",
            "remaining_growth",
        ]

        for name in numeric_fields:

            try:
                value = float(
                    getattr(self, name)
                )
            except (TypeError, ValueError):
                value = 0.0

            setattr(
                self,
                name,
                max(0.0, min(100.0, value))
            )

        return self

    def to_dict(self) -> Dict[str, Any]:

        self.normalize()

        return {
            "intelligence_id": self.intelligence_id,
            "timestamp": self.timestamp,
            "instrument": self.instrument,
            "direction": self.direction.value,

            "state": self.state.value,
            "action": self.action.value,
            "thesis_health": self.thesis_health.value,
            "trigger": self.trigger.value,

            "protection_quality": (
                self.protection_quality
            ),
            "protection_pressure": (
                self.protection_pressure
            ),
            "market_support": self.market_support,
            "risk_pressure": self.risk_pressure,

            "continuation_score": (
                self.continuation_score
            ),
            "anti_evidence_pressure": (
                self.anti_evidence_pressure
            ),
            "exhaustion_pressure": (
                self.exhaustion_pressure
            ),

            "target_progress": self.target_progress,
            "invalidation_progress": (
                self.invalidation_progress
            ),
            "remaining_growth": (
                self.remaining_growth
            ),

            "thesis_intact": self.thesis_intact,

            "recalculation_required": (
                self.recalculation_required
            ),
            "thesis_review_required": (
                self.thesis_review_required
            ),
            "exit_review_required": (
                self.exit_review_required
            ),

            "improving": self.improving,
            "deteriorating": self.deteriorating,
            "material_change": self.material_change,

            "reasons": list(self.reasons),
            "warnings": list(self.warnings),
            "source_engines": list(self.source_engines),
            "metadata": dict(self.metadata),
        }


# ============================================================
# D13 PROTECTION FEED
# ============================================================

@dataclass
class GrowthProtectionD13Feed:
    """
    Normalized upstream feed for D13.

    No final BUY/SELL/EXIT decision is fabricated here.
    """

    feed_id: str = ""
    timestamp: str = ""

    instrument: str = ""
    direction: ProtectionDirection = (
        ProtectionDirection.UNKNOWN
    )

    current_state: ProtectionState = (
        ProtectionState.UNKNOWN
    )

    thesis_health: ThesisHealth = (
        ThesisHealth.UNKNOWN
    )

    protection_quality: float = 0.0
    protection_pressure: float = 0.0

    continuation_active: bool = False
    anti_evidence_active: bool = False
    exhaustion_active: bool = False

    thesis_review_required: bool = False
    recalculation_required: bool = False
    exit_review_required: bool = False

    current_action: ProtectionAction = (
        ProtectionAction.UNKNOWN
    )

    final_decision: Optional[str] = None

    reasons: List[str] = field(
        default_factory=list
    )
    warnings: List[str] = field(
        default_factory=list
    )

    source: str = "growth_protection_engine"

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "feed_id": self.feed_id,
            "timestamp": self.timestamp,
            "instrument": self.instrument,
            "direction": self.direction.value,
            "current_state": self.current_state.value,
            "thesis_health": self.thesis_health.value,

            "protection_quality": (
                self.protection_quality
            ),
            "protection_pressure": (
                self.protection_pressure
            ),

            "continuation_active": (
                self.continuation_active
            ),
            "anti_evidence_active": (
                self.anti_evidence_active
            ),
            "exhaustion_active": (
                self.exhaustion_active
            ),

            "thesis_review_required": (
                self.thesis_review_required
            ),
            "recalculation_required": (
                self.recalculation_required
            ),
            "exit_review_required": (
                self.exit_review_required
            ),

            "current_action": (
                self.current_action.value
            ),

            # Intentionally remains None until D13 decides.
            "final_decision": self.final_decision,

            "reasons": list(self.reasons),
            "warnings": list(self.warnings),

            "source": self.source,
            "metadata": dict(self.metadata),
        }


# ============================================================
# BLACKBOX PROTECTION RECORD
# ============================================================

@dataclass
class GrowthProtectionBlackBoxRecord:
    """
    Compact immutable-style record for outcome analysis,
    validation and learning.
    """

    record_id: str = ""
    timestamp: str = ""

    instrument: str = ""
    direction: ProtectionDirection = (
        ProtectionDirection.UNKNOWN
    )

    state: ProtectionState = ProtectionState.UNKNOWN
    action: ProtectionAction = ProtectionAction.UNKNOWN
    thesis_health: ThesisHealth = ThesisHealth.UNKNOWN
    trigger: ProtectionTrigger = ProtectionTrigger.NONE

    protection_quality: float = 0.0
    protection_pressure: float = 0.0
    market_support: float = 0.0
    risk_pressure: float = 0.0

    target_progress: float = 0.0
    invalidation_progress: float = 0.0
    remaining_growth: float = 0.0

    anti_evidence_pressure: float = 0.0
    exhaustion_pressure: float = 0.0
    continuation_score: float = 0.0

    recalculation_required: bool = False
    exit_review_required: bool = False
    material_change: bool = False

    reasons: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "record_id": self.record_id,
            "timestamp": self.timestamp,
            "instrument": self.instrument,
            "direction": self.direction.value,

            "state": self.state.value,
            "action": self.action.value,
            "thesis_health": self.thesis_health.value,
            "trigger": self.trigger.value,

            "protection_quality": (
                self.protection_quality
            ),
            "protection_pressure": (
                self.protection_pressure
            ),
            "market_support": self.market_support,
            "risk_pressure": self.risk_pressure,

            "target_progress": self.target_progress,
            "invalidation_progress": (
                self.invalidation_progress
            ),
            "remaining_growth": (
                self.remaining_growth
            ),

            "anti_evidence_pressure": (
                self.anti_evidence_pressure
            ),
            "exhaustion_pressure": (
                self.exhaustion_pressure
            ),
            "continuation_score": (
                self.continuation_score
            ),

            "recalculation_required": (
                self.recalculation_required
            ),
            "exit_review_required": (
                self.exit_review_required
            ),
            "material_change": self.material_change,

            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }


# ============================================================
# INTELLIGENCE BUILDER
# ============================================================

class GrowthProtectionIntelligenceEngine:
    """
    Converts Part 2 + Part 3 protection information into
    normalized intelligence feeds.

    D13 remains the final decision authority.
    """

    def __init__(
        self,
        monitoring_engine:
            Optional[
                GrowthProtectionMonitoringEngine
            ] = None,
    ):

        self.monitoring_engine = (
            monitoring_engine
            if monitoring_engine is not None
            else GrowthProtectionMonitoringEngine()
        )

    # --------------------------------------------------------
    # Assessment → Intelligence
    # --------------------------------------------------------

    def build_intelligence(
        self,
        assessment: GrowthProtectionAssessment,
        *,
        monitor:
            Optional[GrowthProtectionMonitor] = None,
        intelligence_id: str = "",
    ) -> GrowthProtectionIntelligence:

        assessment.normalize()

        if monitor is None:
            monitor = self.monitoring_engine.get_monitor(
                assessment.assessment_id
            )

        improving = False
        deteriorating = False

        if monitor is not None:
            improving = monitor.improving
            deteriorating = monitor.deteriorating

        return GrowthProtectionIntelligence(
            intelligence_id=intelligence_id,
            timestamp=assessment.timestamp,

            instrument=assessment.instrument,
            direction=assessment.direction,

            state=assessment.state,
            action=assessment.action,
            thesis_health=(
                assessment.thesis.health
            ),
            trigger=assessment.trigger,

            protection_quality=(
                assessment.score.protection_quality
            ),
            protection_pressure=(
                assessment.score.risk_pressure
            ),
            market_support=(
                assessment.score.market_support
            ),
            risk_pressure=(
                assessment.score.risk_pressure
            ),

            continuation_score=(
                assessment.score.continuation_score
            ),
            anti_evidence_pressure=(
                assessment.score.anti_evidence_pressure
            ),
            exhaustion_pressure=(
                assessment.score.exhaustion_pressure
            ),

            target_progress=(
                assessment.score.target_progress
            ),
            invalidation_progress=(
                assessment.score.invalidation_pressure
            ),
            remaining_growth=(
                assessment.score.remaining_growth
            ),

            thesis_intact=(
                assessment.thesis.health
                not in (
                    ThesisHealth.INVALIDATED,
                    ThesisHealth.EXHAUSTED,
                )
            ),

            recalculation_required=(
                assessment.recalculation_required
            ),
            thesis_review_required=(
                assessment.thesis_review_required
            ),
            exit_review_required=(
                assessment.exit_review_required
            ),

            improving=improving,
            deteriorating=deteriorating,

            material_change=(
                assessment.material_change
            ),

            reasons=list(assessment.reasons),
            warnings=list(assessment.warnings),

            source_engines=[
                "GrowthProtectionEngine",
                "GrowthProtectionAssessmentEngine",
                "GrowthProtectionMonitoringEngine",
            ],
        )

    # --------------------------------------------------------
    # Intelligence → D13
    # --------------------------------------------------------

    def build_d13_feed(
        self,
        intelligence: GrowthProtectionIntelligence,
        *,
        feed_id: str = "",
    ) -> GrowthProtectionD13Feed:

        intelligence.normalize()

        return GrowthProtectionD13Feed(
            feed_id=feed_id,
            timestamp=intelligence.timestamp,

            instrument=intelligence.instrument,
            direction=intelligence.direction,

            current_state=intelligence.state,
            thesis_health=intelligence.thesis_health,

            protection_quality=(
                intelligence.protection_quality
            ),
            protection_pressure=(
                intelligence.protection_pressure
            ),

            continuation_active=(
                intelligence.continuation_score >= 60.0
            ),
            anti_evidence_active=(
                intelligence.anti_evidence_pressure >= 50.0
            ),
            exhaustion_active=(
                intelligence.exhaustion_pressure >= 60.0
            ),

            thesis_review_required=(
                intelligence.thesis_review_required
            ),
            recalculation_required=(
                intelligence.recalculation_required
            ),
            exit_review_required=(
                intelligence.exit_review_required
            ),

            current_action=(
                intelligence.action
            ),

            # Explicitly no final decision here.
            final_decision=None,

            reasons=list(intelligence.reasons),
            warnings=list(intelligence.warnings),

            metadata={
                "source_engine": (
                    "GrowthProtectionIntelligenceEngine"
                ),
                "decision_authority": "D13",
            },
        )

    # --------------------------------------------------------
    # Assessment → BlackBox
    # --------------------------------------------------------

    def build_blackbox_record(
        self,
        assessment: GrowthProtectionAssessment,
        *,
        record_id: str = "",
    ) -> GrowthProtectionBlackBoxRecord:

        assessment.normalize()

        return GrowthProtectionBlackBoxRecord(
            record_id=record_id,
            timestamp=assessment.timestamp,

            instrument=assessment.instrument,
            direction=assessment.direction,

            state=assessment.state,
            action=assessment.action,
            thesis_health=(
                assessment.thesis.health
            ),
            trigger=assessment.trigger,

            protection_quality=(
                assessment.score.protection_quality
            ),
            protection_pressure=(
                assessment.score.risk_pressure
            ),
            market_support=(
                assessment.score.market_support
            ),
            risk_pressure=(
                assessment.score.risk_pressure
            ),

            target_progress=(
                assessment.score.target_progress
            ),
            invalidation_progress=(
                assessment.score.invalidation_pressure
            ),
            remaining_growth=(
                assessment.score.remaining_growth
            ),

            anti_evidence_pressure=(
                assessment.score.anti_evidence_pressure
            ),
            exhaustion_pressure=(
                assessment.score.exhaustion_pressure
            ),
            continuation_score=(
                assessment.score.continuation_score
            ),

            recalculation_required=(
                assessment.recalculation_required
            ),
            exit_review_required=(
                assessment.exit_review_required
            ),
            material_change=(
                assessment.material_change
            ),

            reasons=list(assessment.reasons),

            metadata={
                "source": "growth_protection_engine",
                "engine_part": 4,
            },
        )


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def build_growth_protection_intelligence(
    assessment: GrowthProtectionAssessment,
    *,
    monitoring_engine:
        Optional[
            GrowthProtectionMonitoringEngine
        ] = None,
    intelligence_id: str = "",
) -> GrowthProtectionIntelligence:

    engine = GrowthProtectionIntelligenceEngine(
        monitoring_engine=monitoring_engine
    )

    return engine.build_intelligence(
        assessment,
        intelligence_id=intelligence_id,
    )


def export_growth_protection_d13_feed(
    intelligence: GrowthProtectionIntelligence,
    *,
    feed_id: str = "",
) -> Dict[str, Any]:

    engine = GrowthProtectionIntelligenceEngine()

    feed = engine.build_d13_feed(
        intelligence,
        feed_id=feed_id,
    )

    return feed.to_dict()


def build_growth_protection_blackbox_record(
    assessment: GrowthProtectionAssessment,
    *,
    record_id: str = "",
) -> Dict[str, Any]:

    engine = GrowthProtectionIntelligenceEngine()

    record = engine.build_blackbox_record(
        assessment,
        record_id=record_id,
    )

    return record.to_dict()


# ============================================================
# PUBLIC API
# ============================================================

__all__ += [
    "GrowthProtectionIntelligence",
    "GrowthProtectionD13Feed",
    "GrowthProtectionBlackBoxRecord",
    "GrowthProtectionIntelligenceEngine",
    "build_growth_protection_intelligence",
    "export_growth_protection_d13_feed",
    "build_growth_protection_blackbox_record",
]
# ============================================================
# GROWTH PROTECTION ENGINE — PART 5
# Validation / Audit / Serialization / Public API
# ============================================================

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ============================================================
# VALIDATION ISSUE
# ============================================================

@dataclass
class GrowthProtectionValidationIssue:
    """
    Single validation issue.
    """

    code: str = ""
    field: str = ""
    message: str = ""
    severity: str = "ERROR"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "field": self.field,
            "message": self.message,
            "severity": self.severity,
        }


# ============================================================
# VALIDATION RESULT
# ============================================================

@dataclass
class GrowthProtectionValidationResult:
    """
    Validation result for Growth Protection objects.
    """

    valid: bool = True

    issues: List[
        GrowthProtectionValidationIssue
    ] = field(default_factory=list)

    warnings: List[str] = field(
        default_factory=list
    )

    checked_at: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if not self.checked_at:
            self.checked_at = datetime.now(
                timezone.utc
            ).isoformat()

    def add_error(
        self,
        code: str,
        field: str,
        message: str,
    ) -> None:

        self.issues.append(
            GrowthProtectionValidationIssue(
                code=code,
                field=field,
                message=message,
                severity="ERROR",
            )
        )

        self.valid = False

    def add_warning(
        self,
        message: str,
        *,
        code: str = "WARNING",
        field: str = "",
    ) -> None:

        self.warnings.append(message)

        self.issues.append(
            GrowthProtectionValidationIssue(
                code=code,
                field=field,
                message=message,
                severity="WARNING",
            )
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "issues": [
                issue.to_dict()
                for issue in self.issues
            ],
            "warnings": list(self.warnings),
            "checked_at": self.checked_at,
            "metadata": dict(self.metadata),
        }


# ============================================================
# VALIDATOR
# ============================================================

class GrowthProtectionValidator:
    """
    Final validation layer for Growth Protection.

    Validates:
        - context
        - measurement
        - assessment
        - intelligence
        - D13 feed
        - BlackBox record

    Validation does not modify trading decisions.
    """

    @staticmethod
    def _safe_float(
        value: Any,
    ) -> Optional[float]:

        try:
            result = float(value)
        except (TypeError, ValueError):
            return None

        if result != result:
            return None

        return result

    @staticmethod
    def _check_score(
        result: GrowthProtectionValidationResult,
        field_name: str,
        value: Any,
    ) -> None:

        numeric = GrowthProtectionValidator._safe_float(
            value
        )

        if numeric is None:
            result.add_error(
                code="INVALID_SCORE",
                field=field_name,
                message=(
                    f"{field_name} must be numeric."
                ),
            )
            return

        if numeric < 0.0 or numeric > 100.0:
            result.add_error(
                code="SCORE_OUT_OF_RANGE",
                field=field_name,
                message=(
                    f"{field_name} must be between "
                    "0 and 100."
                ),
            )

    # --------------------------------------------------------
    # Context Validation
    # --------------------------------------------------------

    def validate_context(
        self,
        context: GrowthProtectionContext,
    ) -> GrowthProtectionValidationResult:

        result = GrowthProtectionValidationResult()

        if not isinstance(
            context,
            GrowthProtectionContext,
        ):
            result.add_error(
                code="INVALID_CONTEXT",
                field="context",
                message=(
                    "Expected GrowthProtectionContext."
                ),
            )
            return result

        directional = (
            context.direction
            in (
                ProtectionDirection.BUY,
                ProtectionDirection.SELL,
                ProtectionDirection.CALL,
                ProtectionDirection.PUT,
            )
        )

        if not directional:
            result.add_warning(
                "Context direction is not directional.",
                code="NON_DIRECTIONAL_CONTEXT",
                field="direction",
            )

        score_fields = [
            "thesis_score",
            "evidence_score",
            "structure_score",
            "participation_score",
            "liquidity_score",
            "relationship_score",
            "regime_score",
            "continuation_score",
            "exhaustion_score",
            "anti_evidence_strength",
            "opposing_pressure",
            "volatility_score",
        ]

        for field_name in score_fields:
            self._check_score(
                result,
                field_name,
                getattr(context, field_name),
            )

        price_fields = [
            "current_price",
            "entry_price",
            "target_price",
            "invalidation_price",
        ]

        for field_name in price_fields:
            value = getattr(context, field_name)

            if value is None:
                continue

            numeric = self._safe_float(value)

            if numeric is None:
                result.add_error(
                    code="INVALID_PRICE",
                    field=field_name,
                    message=(
                        f"{field_name} must be numeric."
                    ),
                )
            elif numeric < 0:
                result.add_error(
                    code="NEGATIVE_PRICE",
                    field=field_name,
                    message=(
                        f"{field_name} cannot be negative."
                    ),
                )

        return result

    # --------------------------------------------------------
    # Measurement Validation
    # --------------------------------------------------------

    def validate_measurement(
        self,
        measurement: GrowthProtectionMeasurement,
    ) -> GrowthProtectionValidationResult:

        result = GrowthProtectionValidationResult()

        if not isinstance(
            measurement,
            GrowthProtectionMeasurement,
        ):
            result.add_error(
                code="INVALID_MEASUREMENT",
                field="measurement",
                message=(
                    "Expected "
                    "GrowthProtectionMeasurement."
                ),
            )
            return result

        score_fields = [
            "entry_distance_pct",
            "target_distance_pct",
            "invalidation_distance_pct",
            "realized_move_pct",
            "favorable_move_pct",
            "adverse_move_pct",
            "target_progress",
            "invalidation_progress",
            "protection_pressure",
            "thesis_risk",
            "anti_evidence_pressure",
            "exhaustion_pressure",
            "continuation_score",
            "market_support",
            "remaining_growth",
        ]

        for field_name in score_fields:
            self._check_score(
                result,
                field_name,
                getattr(measurement, field_name),
            )

        if (
            measurement.target_progress
            > 100.0
        ):
            result.add_error(
                code="TARGET_PROGRESS_INVALID",
                field="target_progress",
                message=(
                    "Target progress exceeds 100."
                ),
            )

        if (
            measurement.invalidation_progress
            > 100.0
        ):
            result.add_error(
                code="INVALIDATION_PROGRESS_INVALID",
                field="invalidation_progress",
                message=(
                    "Invalidation progress exceeds 100."
                ),
            )

        return result

    # --------------------------------------------------------
    # Assessment Validation
    # --------------------------------------------------------

    def validate_assessment(
        self,
        assessment: GrowthProtectionAssessment,
    ) -> GrowthProtectionValidationResult:

        result = GrowthProtectionValidationResult()

        if not isinstance(
            assessment,
            GrowthProtectionAssessment,
        ):
            result.add_error(
                code="INVALID_ASSESSMENT",
                field="assessment",
                message=(
                    "Expected "
                    "GrowthProtectionAssessment."
                ),
            )
            return result

        if not assessment.timestamp:
            result.add_error(
                code="MISSING_TIMESTAMP",
                field="timestamp",
                message="Assessment timestamp is required.",
            )

        if not isinstance(
            assessment.score,
            GrowthProtectionScore,
        ):
            result.add_error(
                code="INVALID_SCORE_OBJECT",
                field="score",
                message=(
                    "Assessment score object is invalid."
                ),
            )

        if not isinstance(
            assessment.thesis,
            GrowthProtectionThesis,
        ):
            result.add_error(
                code="INVALID_THESIS_OBJECT",
                field="thesis",
                message=(
                    "Assessment thesis object is invalid."
                ),
            )

        score_fields = [
            "market_support",
            "thesis_health_score",
            "continuation_score",
            "adverse_pressure",
            "anti_evidence_pressure",
            "exhaustion_pressure",
            "invalidation_pressure",
            "target_progress",
            "remaining_growth",
            "protection_quality",
            "risk_pressure",
        ]

        for field_name in score_fields:
            self._check_score(
                result,
                f"score.{field_name}",
                getattr(
                    assessment.score,
                    field_name,
                ),
            )

        # Consistency checks
        if (
            assessment.exit_review_required
            and assessment.action
            not in (
                ProtectionAction.EXIT_REVIEW,
                ProtectionAction.INVALIDATED,
            )
        ):
            result.add_warning(
                (
                    "Exit review is required while "
                    "current action is not EXIT_REVIEW/"
                    "INVALIDATED."
                ),
                code="EXIT_REVIEW_ACTION_MISMATCH",
                field="action",
            )

        if (
            assessment.thesis.health
            == ThesisHealth.INVALIDATED
            and not assessment.exit_review_required
        ):
            result.add_error(
                code="INVALIDATED_WITHOUT_REVIEW",
                field="exit_review_required",
                message=(
                    "Invalidated thesis must expose "
                    "exit review."
                ),
            )

        if (
            assessment.recalculation_required
            and assessment.thesis.health
            == ThesisHealth.INVALIDATED
        ):
            result.add_warning(
                (
                    "Recalculation flag remains active "
                    "after thesis invalidation."
                ),
                code="RECALCULATION_AFTER_INVALIDATION",
                field="recalculation_required",
            )

        return result

    # --------------------------------------------------------
    # Intelligence Validation
    # --------------------------------------------------------

    def validate_intelligence(
        self,
        intelligence:
            GrowthProtectionIntelligence,
    ) -> GrowthProtectionValidationResult:

        result = GrowthProtectionValidationResult()

        if not isinstance(
            intelligence,
            GrowthProtectionIntelligence,
        ):
            result.add_error(
                code="INVALID_INTELLIGENCE",
                field="intelligence",
                message=(
                    "Expected "
                    "GrowthProtectionIntelligence."
                ),
            )
            return result

        score_fields = [
            "protection_quality",
            "protection_pressure",
            "market_support",
            "risk_pressure",
            "continuation_score",
            "anti_evidence_pressure",
            "exhaustion_pressure",
            "target_progress",
            "invalidation_progress",
            "remaining_growth",
        ]

        for field_name in score_fields:
            self._check_score(
                result,
                field_name,
                getattr(intelligence, field_name),
            )

        if (
            intelligence.thesis_health
            in (
                ThesisHealth.INVALIDATED,
                ThesisHealth.EXHAUSTED,
            )
            and intelligence.thesis_intact
        ):
            result.add_error(
                code="THESIS_STATE_CONFLICT",
                field="thesis_intact",
                message=(
                    "Thesis cannot be marked intact "
                    "while health is INVALIDATED or "
                    "EXHAUSTED."
                ),
            )

        return result

    # --------------------------------------------------------
    # D13 Feed Validation
    # --------------------------------------------------------

    def validate_d13_feed(
        self,
        feed: GrowthProtectionD13Feed,
    ) -> GrowthProtectionValidationResult:

        result = GrowthProtectionValidationResult()

        if not isinstance(
            feed,
            GrowthProtectionD13Feed,
        ):
            result.add_error(
                code="INVALID_D13_FEED",
                field="feed",
                message=(
                    "Expected "
                    "GrowthProtectionD13Feed."
                ),
            )
            return result

        self._check_score(
            result,
            "protection_quality",
            feed.protection_quality,
        )

        self._check_score(
            result,
            "protection_pressure",
            feed.protection_pressure,
        )

        # D13 feed must not contain a fabricated
        # upstream final decision.
        if feed.final_decision is not None:
            result.add_error(
                code="UNAUTHORIZED_FINAL_DECISION",
                field="final_decision",
                message=(
                    "Growth Protection feed must not "
                    "populate final_decision. "
                    "D13 owns final decision authority."
                ),
            )

        return result

    # --------------------------------------------------------
    # BlackBox Validation
    # --------------------------------------------------------

    def validate_blackbox_record(
        self,
        record:
            GrowthProtectionBlackBoxRecord,
    ) -> GrowthProtectionValidationResult:

        result = GrowthProtectionValidationResult()

        if not isinstance(
            record,
            GrowthProtectionBlackBoxRecord,
        ):
            result.add_error(
                code="INVALID_BLACKBOX_RECORD",
                field="record",
                message=(
                    "Expected "
                    "GrowthProtectionBlackBoxRecord."
                ),
            )
            return result

        if not record.record_id:
            result.add_warning(
                "BlackBox record has no explicit record ID.",
                code="MISSING_RECORD_ID",
                field="record_id",
            )

        score_fields = [
            "protection_quality",
            "protection_pressure",
            "market_support",
            "risk_pressure",
            "target_progress",
            "invalidation_progress",
            "remaining_growth",
            "anti_evidence_pressure",
            "exhaustion_pressure",
            "continuation_score",
        ]

        for field_name in score_fields:
            self._check_score(
                result,
                field_name,
                getattr(record, field_name),
            )

        return result

    # --------------------------------------------------------
    # Full Validation
    # --------------------------------------------------------

    def validate_all(
        self,
        *,
        context:
            Optional[GrowthProtectionContext] = None,
        measurement:
            Optional[GrowthProtectionMeasurement] = None,
        assessment:
            Optional[GrowthProtectionAssessment] = None,
        intelligence:
            Optional[GrowthProtectionIntelligence] = None,
        d13_feed:
            Optional[GrowthProtectionD13Feed] = None,
        blackbox_record:
            Optional[GrowthProtectionBlackBoxRecord] = None,
    ) -> GrowthProtectionValidationResult:

        final = GrowthProtectionValidationResult()

        validators = []

        if context is not None:
            validators.append(
                self.validate_context(context)
            )

        if measurement is not None:
            validators.append(
                self.validate_measurement(
                    measurement
                )
            )

        if assessment is not None:
            validators.append(
                self.validate_assessment(
                    assessment
                )
            )

        if intelligence is not None:
            validators.append(
                self.validate_intelligence(
                    intelligence
                )
            )

        if d13_feed is not None:
            validators.append(
                self.validate_d13_feed(
                    d13_feed
                )
            )

        if blackbox_record is not None:
            validators.append(
                self.validate_blackbox_record(
                    blackbox_record
                )
            )

        for validation in validators:

            final.issues.extend(
                validation.issues
            )

            final.warnings.extend(
                validation.warnings
            )

            if not validation.valid:
                final.valid = False

        final.metadata = {
            "engine": "GrowthProtectionValidator",
            "objects_checked": len(validators),
        }

        return final


# ============================================================
# AUDIT RECORD
# ============================================================

@dataclass
class GrowthProtectionAuditRecord:
    """
    Complete audit snapshot.

    Designed for BlackBox / validation / learning.
    """

    audit_id: str = ""
    timestamp: str = ""

    instrument: str = ""
    direction: ProtectionDirection = (
        ProtectionDirection.UNKNOWN
    )

    state: ProtectionState = ProtectionState.UNKNOWN
    action: ProtectionAction = ProtectionAction.UNKNOWN
    thesis_health: ThesisHealth = ThesisHealth.UNKNOWN
    trigger: ProtectionTrigger = ProtectionTrigger.NONE

    protection_quality: float = 0.0
    protection_pressure: float = 0.0
    market_support: float = 0.0
    risk_pressure: float = 0.0

    continuation_score: float = 0.0
    anti_evidence_pressure: float = 0.0
    exhaustion_pressure: float = 0.0

    target_progress: float = 0.0
    invalidation_progress: float = 0.0
    remaining_growth: float = 0.0

    thesis_intact: bool = True

    improving: bool = False
    deteriorating: bool = False

    recalculation_required: bool = False
    thesis_review_required: bool = False
    exit_review_required: bool = False
    material_change: bool = False

    validation_status: str = "UNKNOWN"

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
            "audit_id": self.audit_id,
            "timestamp": self.timestamp,
            "instrument": self.instrument,
            "direction": self.direction.value,

            "state": self.state.value,
            "action": self.action.value,
            "thesis_health": self.thesis_health.value,
            "trigger": self.trigger.value,

            "protection_quality": (
                self.protection_quality
            ),
            "protection_pressure": (
                self.protection_pressure
            ),
            "market_support": self.market_support,
            "risk_pressure": self.risk_pressure,

            "continuation_score": (
                self.continuation_score
            ),
            "anti_evidence_pressure": (
                self.anti_evidence_pressure
            ),
            "exhaustion_pressure": (
                self.exhaustion_pressure
            ),

            "target_progress": self.target_progress,
            "invalidation_progress": (
                self.invalidation_progress
            ),
            "remaining_growth": (
                self.remaining_growth
            ),

            "thesis_intact": self.thesis_intact,

            "improving": self.improving,
            "deteriorating": self.deteriorating,

            "recalculation_required": (
                self.recalculation_required
            ),
            "thesis_review_required": (
                self.thesis_review_required
            ),
            "exit_review_required": (
                self.exit_review_required
            ),
            "material_change": (
                self.material_change
            ),

            "validation_status": (
                self.validation_status
            ),

            "reasons": list(self.reasons),
            "warnings": list(self.warnings),
            "metadata": dict(self.metadata),
        }


# ============================================================
# AUDIT BUILDER
# ============================================================

def build_growth_protection_audit_record(
    assessment: GrowthProtectionAssessment,
    *,
    monitor:
        Optional[GrowthProtectionMonitor] = None,
    validation:
        Optional[GrowthProtectionValidationResult] = None,
    audit_id: str = "",
) -> GrowthProtectionAuditRecord:

    assessment.normalize()

    improving = False
    deteriorating = False

    if monitor is not None:
        improving = monitor.improving
        deteriorating = monitor.deteriorating

    validation_status = "NOT_CHECKED"

    if validation is not None:
        validation_status = (
            "VALID"
            if validation.valid
            else "INVALID"
        )

    return GrowthProtectionAuditRecord(
        audit_id=audit_id,
        timestamp=assessment.timestamp,

        instrument=assessment.instrument,
        direction=assessment.direction,

        state=assessment.state,
        action=assessment.action,
        thesis_health=(
            assessment.thesis.health
        ),
        trigger=assessment.trigger,

        protection_quality=(
            assessment.score.protection_quality
        ),
        protection_pressure=(
            assessment.score.risk_pressure
        ),
        market_support=(
            assessment.score.market_support
        ),
        risk_pressure=(
            assessment.score.risk_pressure
        ),

        continuation_score=(
            assessment.score.continuation_score
        ),
        anti_evidence_pressure=(
            assessment.score.anti_evidence_pressure
        ),
        exhaustion_pressure=(
            assessment.score.exhaustion_pressure
        ),

        target_progress=(
            assessment.score.target_progress
        ),
        invalidation_progress=(
            assessment.score.invalidation_pressure
        ),
        remaining_growth=(
            assessment.score.remaining_growth
        ),

        thesis_intact=(
            assessment.thesis.health
            not in (
                ThesisHealth.INVALIDATED,
                ThesisHealth.EXHAUSTED,
            )
        ),

        improving=improving,
        deteriorating=deteriorating,

        recalculation_required=(
            assessment.recalculation_required
        ),
        thesis_review_required=(
            assessment.thesis_review_required
        ),
        exit_review_required=(
            assessment.exit_review_required
        ),
        material_change=(
            assessment.material_change
        ),

        validation_status=validation_status,

        reasons=list(assessment.reasons),
        warnings=list(assessment.warnings),

        metadata={
            "source": "growth_protection_engine",
            "engine_part": 5,
        },
    )


# ============================================================
# SERIALIZATION HELPERS
# ============================================================

def serialize_growth_protection_assessment(
    assessment: GrowthProtectionAssessment,
) -> Dict[str, Any]:

    return assessment.to_dict()


def serialize_growth_protection_intelligence(
    intelligence:
        GrowthProtectionIntelligence,
) -> Dict[str, Any]:

    return intelligence.to_dict()


def serialize_growth_protection_d13_feed(
    feed: GrowthProtectionD13Feed,
) -> Dict[str, Any]:

    return feed.to_dict()


def serialize_growth_protection_audit(
    audit:
        GrowthProtectionAuditRecord,
) -> Dict[str, Any]:

    return audit.to_dict()


# ============================================================
# VALIDATION CONVENIENCE FUNCTIONS
# ============================================================

def validate_growth_protection(
    *,
    context:
        Optional[GrowthProtectionContext] = None,
    measurement:
        Optional[GrowthProtectionMeasurement] = None,
    assessment:
        Optional[GrowthProtectionAssessment] = None,
    intelligence:
        Optional[GrowthProtectionIntelligence] = None,
    d13_feed:
        Optional[GrowthProtectionD13Feed] = None,
    blackbox_record:
        Optional[GrowthProtectionBlackBoxRecord] = None,
) -> GrowthProtectionValidationResult:

    validator = GrowthProtectionValidator()

    return validator.validate_all(
        context=context,
        measurement=measurement,
        assessment=assessment,
        intelligence=intelligence,
        d13_feed=d13_feed,
        blackbox_record=blackbox_record,
    )


def audit_growth_protection(
    assessment: GrowthProtectionAssessment,
    *,
    monitor:
        Optional[GrowthProtectionMonitor] = None,
    validation:
        Optional[GrowthProtectionValidationResult] = None,
    audit_id: str = "",
) -> Dict[str, Any]:

    audit = build_growth_protection_audit_record(
        assessment,
        monitor=monitor,
        validation=validation,
        audit_id=audit_id,
    )

    return audit.to_dict()


# ============================================================
# FINAL PUBLIC API
# ============================================================

__all__ += [
    "GrowthProtectionValidationIssue",
    "GrowthProtectionValidationResult",
    "GrowthProtectionValidator",
    "GrowthProtectionAuditRecord",
    "build_growth_protection_audit_record",
    "serialize_growth_protection_assessment",
    "serialize_growth_protection_intelligence",
    "serialize_growth_protection_d13_feed",
    "serialize_growth_protection_audit",
    "validate_growth_protection",
    "audit_growth_protection",
]