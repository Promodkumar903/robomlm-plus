```python
"""
ROBOMLM_PLUS
Confirmation Engine - Part 1
Foundation / Evidence Preparation Layer

ROLE
----
Prepare and normalize the evidence required for later confirmation
intelligence.

This layer does NOT:
    - generate BUY/SELL
    - declare a confirmed breakout
    - calculate validated market probabilities
    - replace D13 decision authority

Flow:
    Breakout Intelligence
            +
    Boundary Intelligence
            +
    Participation / Pressure
            +
    Price / Volume Evidence
            ↓
    Confirmation Foundation
            ↓
    Later Confirmation Parts
            ↓
    D13
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


# ============================================================
# DATA CONTRACT
# ============================================================

@dataclass
class ConfirmationFoundation:
    """
    Normalized evidence contract for Confirmation Engine Part-1.
    """

    breakout_readiness: float

    breakout_probability: float

    directional_strength: float

    boundary_quality: float

    participation_quality: float

    pressure_alignment: float

    volume_quality: float

    structure_quality: float

    evidence_quality: float

    confirmation_readiness: float

    direction_bias: str

    status: str

    evidence: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# CONFIRMATION ENGINE
# ============================================================

class ConfirmationEngine:
    """
    Confirmation Engine - Part 1

    Foundation Layer.

    Purpose:
        Build a normalized evidence foundation from upstream
        intelligence engines.

    Important:
        Scores in this module are structural evidence proxies.
        They are NOT validated research probabilities.

        Final decision authority remains D13.
    """

    def __init__(
        self,
        minimum_evidence_quality: float = 40.0,
        readiness_threshold: float = 60.0,
    ):
        self.minimum_evidence_quality = (
            minimum_evidence_quality
        )

        self.readiness_threshold = readiness_threshold

    # ========================================================
    # MAIN EVALUATION
    # ========================================================

    def evaluate(
        self,
        breakout_data,
        boundary_data=None,
        participation_data=None,
        structure_data=None,
    ) -> ConfirmationFoundation:

        # ----------------------------------------------------
        # BREAKOUT EVIDENCE
        # ----------------------------------------------------

        breakout_readiness = self._safe_score(
            getattr(
                breakout_data,
                "readiness_score",
                getattr(
                    breakout_data,
                    "breakout_readiness",
                    50.0,
                ),
            )
        )

        breakout_probability = self._safe_score(
            getattr(
                breakout_data,
                "breakout_probability",
                50.0,
            )
        )

        directional_strength = self._safe_score(
            getattr(
                breakout_data,
                "directional_edge",
                50.0,
            )
        )

        direction_bias = self._resolve_direction(
            breakout_data
        )

        # ----------------------------------------------------
        # BOUNDARY EVIDENCE
        # ----------------------------------------------------

        boundary_quality = self._extract_boundary_quality(
            boundary_data
        )

        # ----------------------------------------------------
        # PARTICIPATION EVIDENCE
        # ----------------------------------------------------

        participation_quality = (
            self._extract_participation_quality(
                participation_data
            )
        )

        # ----------------------------------------------------
        # PRESSURE ALIGNMENT
        # ----------------------------------------------------

        pressure_alignment = (
            self._extract_pressure_alignment(
                participation_data
            )
        )

        # ----------------------------------------------------
        # VOLUME QUALITY
        # ----------------------------------------------------

        volume_quality = self._extract_volume_quality(
            participation_data
        )

        # ----------------------------------------------------
        # STRUCTURE QUALITY
        # ----------------------------------------------------

        structure_quality = self._extract_structure_quality(
            structure_data
        )

        # ====================================================
        # EVIDENCE QUALITY
        # ====================================================

        evidence_quality = (
            breakout_readiness * 0.20
            + directional_strength * 0.15
            + boundary_quality * 0.15
            + participation_quality * 0.15
            + pressure_alignment * 0.15
            + volume_quality * 0.10
            + structure_quality * 0.10
        )

        evidence_quality = self._clip(
            evidence_quality
        )

        # ====================================================
        # CONFIRMATION READINESS
        # ====================================================

        confirmation_readiness = (
            breakout_readiness * 0.30
            + breakout_probability * 0.15
            + directional_strength * 0.15
            + boundary_quality * 0.15
            + participation_quality * 0.10
            + pressure_alignment * 0.10
            + volume_quality * 0.05
        )

        confirmation_readiness = self._clip(
            confirmation_readiness
        )

        # ====================================================
        # FOUNDATION STATUS
        # ====================================================

        status = self._resolve_status(
            evidence_quality=evidence_quality,
            confirmation_readiness=confirmation_readiness,
        )

        # ====================================================
        # EVIDENCE TRACE
        # ====================================================

        evidence = {
            "engine": "ConfirmationEngine",
            "part": "PART_1",
            "layer": "FOUNDATION",

            "inputs": {
                "breakout_readiness": breakout_readiness,
                "breakout_probability": breakout_probability,
                "directional_strength": directional_strength,
                "boundary_quality": boundary_quality,
                "participation_quality": participation_quality,
                "pressure_alignment": pressure_alignment,
                "volume_quality": volume_quality,
                "structure_quality": structure_quality,
            },

            "outputs": {
                "evidence_quality": evidence_quality,
                "confirmation_readiness": (
                    confirmation_readiness
                ),
                "direction_bias": direction_bias,
                "status": status,
            },

            "governance": {
                "final_decision_authority": "D13",
                "formula_status": "PROXY_UNTIL_VALIDATED",
                "probability_status": "NOT_CALIBRATED",
                "role": "CONFIRMATION_FOUNDATION",
            },
        }

        return ConfirmationFoundation(
            breakout_readiness=breakout_readiness,
            breakout_probability=breakout_probability,
            directional_strength=directional_strength,
            boundary_quality=boundary_quality,
            participation_quality=participation_quality,
            pressure_alignment=pressure_alignment,
            volume_quality=volume_quality,
            structure_quality=structure_quality,
            evidence_quality=evidence_quality,
            confirmation_readiness=confirmation_readiness,
            direction_bias=direction_bias,
            status=status,
            evidence=evidence,
        )

    # ========================================================
    # BOUNDARY QUALITY
    # ========================================================

    def _extract_boundary_quality(
        self,
        boundary_data,
    ) -> float:

        if boundary_data is None:
            return 50.0

        upper_quality = self._safe_score(
            getattr(
                boundary_data,
                "upper_quality",
                50.0,
            )
        )

        lower_quality = self._safe_score(
            getattr(
                boundary_data,
                "lower_quality",
                50.0,
            )
        )

        weakening = self._safe_score(
            getattr(
                boundary_data,
                "boundary_weakening_index",
                50.0,
            )
        )

        return self._clip(
            upper_quality * 0.30
            + lower_quality * 0.30
            + weakening * 0.40
        )

    # ========================================================
    # PARTICIPATION QUALITY
    # ========================================================

    def _extract_participation_quality(
        self,
        participation_data,
    ) -> float:

        if participation_data is None:
            return 50.0

        participation = self._safe_score(
            getattr(
                participation_data,
                "participation_score",
                50.0,
            )
        )

        liquidity = self._safe_score(
            getattr(
                participation_data,
                "liquidity_pressure_score",
                50.0,
            )
        )

        fuel = self._safe_score(
            getattr(
                participation_data,
                "breakout_fuel_score",
                50.0,
            )
        )

        return self._clip(
            participation * 0.35
            + liquidity * 0.25
            + fuel * 0.40
        )

    # ========================================================
    # PRESSURE ALIGNMENT
    # ========================================================

    def _extract_pressure_alignment(
        self,
        participation_data,
    ) -> float:

        if participation_data is None:
            return 50.0

        return self._safe_score(
            getattr(
                participation_data,
                "pressure_alignment_score",
                50.0,
            )
        )

    # ========================================================
    # VOLUME QUALITY
    # ========================================================

    def _extract_volume_quality(
        self,
        participation_data,
    ) -> float:

        if participation_data is None:
            return 50.0

        volume_pressure = self._safe_score(
            getattr(
                participation_data,
                "volume_pressure_score",
                50.0,
            )
        )

        volume_expansion = self._safe_score(
            getattr(
                participation_data,
                "volume_expansion_score",
                50.0,
            )
        )

        return self._clip(
            volume_pressure * 0.60
            + volume_expansion * 0.40
        )

    # ========================================================
    # STRUCTURE QUALITY
    # ========================================================

    def _extract_structure_quality(
        self,
        structure_data,
    ) -> float:

        if structure_data is None:
            return 50.0

        consolidation = self._safe_score(
            getattr(
                structure_data,
                "consolidation_score",
                50.0,
            )
        )

        structure_quality = self._safe_score(
            getattr(
                structure_data,
                "structure_quality",
                consolidation,
            )
        )

        return self._clip(
            structure_quality
        )

    # ========================================================
    # DIRECTION
    # ========================================================

    def _resolve_direction(
        self,
        breakout_data,
    ) -> str:

        direction = getattr(
            breakout_data,
            "breakout_direction",
            None,
        )

        if direction in (
            "BULLISH",
            "BEARISH",
            "BALANCED",
        ):
            return direction

        direction = getattr(
            breakout_data,
            "direction_bias",
            None,
        )

        if direction in (
            "BULLISH",
            "BEARISH",
            "BALANCED",
        ):
            return direction

        bullish = self._safe_score(
            getattr(
                breakout_data,
                "bullish_probability",
                50.0,
            )
        )

        bearish = self._safe_score(
            getattr(
                breakout_data,
                "bearish_probability",
                50.0,
            )
        )

        if bullish > bearish:
            return "BULLISH"

        if bearish > bullish:
            return "BEARISH"

        return "NEUTRAL"

    # ========================================================
    # STATUS
    # ========================================================

    def _resolve_status(
        self,
        evidence_quality: float,
        confirmation_readiness: float,
    ) -> str:

        if evidence_quality < self.minimum_evidence_quality:
            return "INSUFFICIENT_EVIDENCE"

        if confirmation_readiness >= self.readiness_threshold:
            return "READY_FOR_CONFIRMATION"

        return "BUILDING"

    # ========================================================
    # SAFE SCORE
    # ========================================================

    def _safe_score(
        self,
        value,
    ) -> float:

        try:
            value = float(value)

            if value != value:
                return 50.0

            return self._clip(value)

        except (
            TypeError,
            ValueError,
        ):
            return 50.0

    # ========================================================
    # CLIP
    # ========================================================

    def _clip(
        self,
        value,
    ) -> float:

        return max(
            0.0,
            min(
                100.0,
                float(value),
            ),
        )
```
```python
"""
ROBOMLM_PLUS
Confirmation Engine - Part 2
Breakout Event Validation / Price Acceptance Layer

ROLE
----
Validate the quality of a potential breakout event using:
    - boundary penetration
    - close acceptance
    - breakout distance
    - candle/body strength
    - volume participation
    - directional alignment
    - persistence

IMPORTANT
---------
This is NOT final BUY/SELL logic.

This layer produces confirmation evidence.
D13 remains the final decision authority.

All scoring formulas are provisional proxies until
historical market validation and the Formula Registry
provide validated research formulas.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Sequence


# ============================================================
# DATA CONTRACT
# ============================================================

@dataclass
class BreakoutEventValidation:
    upper_breakout_strength: float
    lower_breakout_strength: float

    boundary_penetration_score: float
    close_acceptance_score: float
    breakout_distance_score: float

    candle_strength_score: float
    volume_confirmation_score: float
    directional_alignment_score: float

    persistence_score: float

    event_confirmation_score: float

    confirmed_direction: str
    confirmation_status: str

    evidence_quality: float
    confidence: float

    calibration_status: str

    evidence: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# CONFIRMATION ENGINE
# ============================================================

class ConfirmationEngine:
    """
    Confirmation Engine - Part 2

    Breakout Event Validation.

    This layer asks:

        "Did price actually accept the breakout area?"

    It does NOT ask:

        "Should we BUY or SELL?"

    That decision remains downstream with D13.
    """

    def __init__(
        self,
        boundary_tolerance: float = 0.0025,
        minimum_confirmation_score: float = 60.0,
        minimum_acceptance_score: float = 55.0,
    ):
        self.boundary_tolerance = boundary_tolerance

        self.minimum_confirmation_score = (
            minimum_confirmation_score
        )

        self.minimum_acceptance_score = (
            minimum_acceptance_score
        )

    # ========================================================
    # MAIN EVALUATION
    # ========================================================

    def evaluate_breakout_event(
        self,
        prices: Sequence[float],
        upper_boundary: Optional[float] = None,
        lower_boundary: Optional[float] = None,
        highs: Optional[Sequence[float]] = None,
        lows: Optional[Sequence[float]] = None,
        opens: Optional[Sequence[float]] = None,
        closes: Optional[Sequence[float]] = None,
        volumes: Optional[Sequence[float]] = None,
        average_volume: Optional[float] = None,
        expected_direction: Optional[str] = None,
        part1_data=None,
        calibration_model=None,
    ) -> BreakoutEventValidation:

        # ----------------------------------------------------
        # DATA PREPARATION
        # ----------------------------------------------------

        close_series = list(
            closes if closes is not None else prices
        )

        if not close_series:
            return self._insufficient_data_result()

        current_close = float(close_series[-1])

        previous_close = (
            float(close_series[-2])
            if len(close_series) >= 2
            else current_close
        )

        current_high = (
            float(highs[-1])
            if highs is not None and len(highs) > 0
            else current_close
        )

        current_low = (
            float(lows[-1])
            if lows is not None and len(lows) > 0
            else current_close
        )

        current_open = (
            float(opens[-1])
            if opens is not None and len(opens) > 0
            else previous_close
        )

        # ----------------------------------------------------
        # BOUNDARY VALIDATION
        # ----------------------------------------------------

        upper_strength = 0.0
        lower_strength = 0.0

        if upper_boundary is not None:
            upper_strength = self._calculate_boundary_break_strength(
                current_price=current_close,
                boundary=float(upper_boundary),
                direction="UP"
            )

        if lower_boundary is not None:
            lower_strength = self._calculate_boundary_break_strength(
                current_price=current_close,
                boundary=float(lower_boundary),
                direction="DOWN"
            )

        # ----------------------------------------------------
        # PENETRATION
        # ----------------------------------------------------

        boundary_penetration_score = (
            self._calculate_penetration_score(
                current_close=current_close,
                upper_boundary=upper_boundary,
                lower_boundary=lower_boundary,
            )
        )

        # ----------------------------------------------------
        # CLOSE ACCEPTANCE
        # ----------------------------------------------------

        close_acceptance_score = (
            self._calculate_close_acceptance(
                close_series=close_series,
                upper_boundary=upper_boundary,
                lower_boundary=lower_boundary,
            )
        )

        # ----------------------------------------------------
        # BREAKOUT DISTANCE
        # ----------------------------------------------------

        breakout_distance_score = (
            self._calculate_breakout_distance(
                current_close=current_close,
                upper_boundary=upper_boundary,
                lower_boundary=lower_boundary,
            )
        )

        # ----------------------------------------------------
        # CANDLE STRENGTH
        # ----------------------------------------------------

        candle_strength_score = (
            self._calculate_candle_strength(
                current_open=current_open,
                current_high=current_high,
                current_low=current_low,
                current_close=current_close,
            )
        )

        # ----------------------------------------------------
        # VOLUME CONFIRMATION
        # ----------------------------------------------------

        volume_confirmation_score = (
            self._calculate_volume_confirmation(
                volumes=volumes,
                average_volume=average_volume,
            )
        )

        # ----------------------------------------------------
        # DIRECTIONAL ALIGNMENT
        # ----------------------------------------------------

        directional_alignment_score = (
            self._calculate_directional_alignment(
                close_series=close_series,
                expected_direction=expected_direction,
                upper_strength=upper_strength,
                lower_strength=lower_strength,
            )
        )

        # ----------------------------------------------------
        # PERSISTENCE
        # ----------------------------------------------------

        persistence_score = (
            self._calculate_persistence(
                close_series=close_series,
                upper_boundary=upper_boundary,
                lower_boundary=lower_boundary,
            )
        )

        # ====================================================
        # EVENT CONFIRMATION SCORE
        # ====================================================

        event_confirmation_score = (
            boundary_penetration_score * 0.15
            + close_acceptance_score * 0.25
            + breakout_distance_score * 0.10
            + candle_strength_score * 0.10
            + volume_confirmation_score * 0.15
            + directional_alignment_score * 0.10
            + persistence_score * 0.15
        )

        event_confirmation_score = self._clip(
            event_confirmation_score
        )

        # ====================================================
        # DIRECTION
        # ====================================================

        confirmed_direction = self._resolve_direction(
            upper_strength=upper_strength,
            lower_strength=lower_strength,
            expected_direction=expected_direction,
        )

        # ====================================================
        # STATUS
        # ====================================================

        confirmation_status = self._resolve_confirmation_status(
            event_confirmation_score=event_confirmation_score,
            close_acceptance_score=close_acceptance_score,
            directional_alignment_score=(
                directional_alignment_score
            ),
        )

        # ====================================================
        # EVIDENCE QUALITY
        # ====================================================

        evidence_quality = self._calculate_evidence_quality(
            boundary_penetration_score,
            close_acceptance_score,
            breakout_distance_score,
            candle_strength_score,
            volume_confirmation_score,
            directional_alignment_score,
            persistence_score,
        )

        # ====================================================
        # CONFIDENCE
        # ====================================================

        confidence = self._calculate_confidence(
            event_confirmation_score=(
                event_confirmation_score
            ),
            evidence_quality=evidence_quality,
            close_acceptance_score=(
                close_acceptance_score
            ),
            persistence_score=persistence_score,
        )

        # ====================================================
        # CALIBRATION
        # ====================================================

        calibration_status = "UNCALIBRATED"

        if calibration_model is not None:
            calibration_status = (
                self._calibration_status(
                    calibration_model
                )
            )

        # ====================================================
        # EVIDENCE TRACE
        # ====================================================

        evidence = {
            "engine": "ConfirmationEngine",
            "part": "PART_2",
            "layer": "BREAKOUT_EVENT_VALIDATION",

            "market_state": {
                "current_close": current_close,
                "previous_close": previous_close,
                "current_open": current_open,
                "current_high": current_high,
                "current_low": current_low,
            },

            "boundaries": {
                "upper_boundary": upper_boundary,
                "lower_boundary": lower_boundary,
            },

            "measurements": {
                "upper_breakout_strength": upper_strength,
                "lower_breakout_strength": lower_strength,
                "boundary_penetration_score": (
                    boundary_penetration_score
                ),
                "close_acceptance_score": (
                    close_acceptance_score
                ),
                "breakout_distance_score": (
                    breakout_distance_score
                ),
                "candle_strength_score": (
                    candle_strength_score
                ),
                "volume_confirmation_score": (
                    volume_confirmation_score
                ),
                "directional_alignment_score": (
                    directional_alignment_score
                ),
                "persistence_score": persistence_score,
            },

            "result": {
                "event_confirmation_score": (
                    event_confirmation_score
                ),
                "confirmed_direction": (
                    confirmed_direction
                ),
                "confirmation_status": (
                    confirmation_status
                ),
                "evidence_quality": evidence_quality,
                "confidence": confidence,
            },

            "governance": {
                "final_decision_authority": "D13",
                "formula_status": "PROXY_UNTIL_VALIDATED",
                "calibration_status": calibration_status,
                "role": "EVENT_CONFIRMATION",
            },
        }

        return BreakoutEventValidation(
            upper_breakout_strength=upper_strength,
            lower_breakout_strength=lower_strength,
            boundary_penetration_score=(
                boundary_penetration_score
            ),
            close_acceptance_score=(
                close_acceptance_score
            ),
            breakout_distance_score=(
                breakout_distance_score
            ),
            candle_strength_score=(
                candle_strength_score
            ),
            volume_confirmation_score=(
                volume_confirmation_score
            ),
            directional_alignment_score=(
                directional_alignment_score
            ),
            persistence_score=persistence_score,
            event_confirmation_score=(
                event_confirmation_score
            ),
            confirmed_direction=confirmed_direction,
            confirmation_status=confirmation_status,
            evidence_quality=evidence_quality,
            confidence=confidence,
            calibration_status=calibration_status,
            evidence=evidence,
        )

    # ========================================================
    # BOUNDARY BREAK STRENGTH
    # ========================================================

    def _calculate_boundary_break_strength(
        self,
        current_price: float,
        boundary: float,
        direction: str,
    ) -> float:

        if boundary == 0:
            return 0.0

        if direction == "UP":
            distance = (
                current_price - boundary
            ) / abs(boundary)

        else:
            distance = (
                boundary - current_price
            ) / abs(boundary)

        # Inside boundary = no penetration.
        if distance <= 0:
            return 0.0

        normalized = (
            distance /
            max(self.boundary_tolerance, 1e-9)
        ) * 50.0

        return self._clip(normalized)

    # ========================================================
    # PENETRATION
    # ========================================================

    def _calculate_penetration_score(
        self,
        current_close: float,
        upper_boundary: Optional[float],
        lower_boundary: Optional[float],
    ) -> float:

        scores = []

        if upper_boundary is not None:
            scores.append(
                self._calculate_boundary_break_strength(
                    current_close,
                    float(upper_boundary),
                    "UP",
                )
            )

        if lower_boundary is not None:
            scores.append(
                self._calculate_boundary_break_strength(
                    current_close,
                    float(lower_boundary),
                    "DOWN",
                )
            )

        if not scores:
            return 0.0

        return self._clip(max(scores))

    # ========================================================
    # CLOSE ACCEPTANCE
    # ========================================================

    def _calculate_close_acceptance(
        self,
        close_series,
        upper_boundary,
        lower_boundary,
    ) -> float:

        if not close_series:
            return 0.0

        if (
            upper_boundary is None
            and lower_boundary is None
        ):
            return 0.0

        recent = close_series[
            max(0, len(close_series) - 5):
        ]

        upper_acceptance = 0.0
        lower_acceptance = 0.0

        if upper_boundary is not None:

            upper = float(upper_boundary)

            above = [
                close > upper
                for close in recent
            ]

            if above:
                upper_acceptance = (
                    sum(above) /
                    len(above)
                ) * 100.0

        if lower_boundary is not None:

            lower = float(lower_boundary)

            below = [
                close < lower
                for close in recent
            ]

            if below:
                lower_acceptance = (
                    sum(below) /
                    len(below)
                ) * 100.0

        return self._clip(
            max(
                upper_acceptance,
                lower_acceptance,
            )
        )

    # ========================================================
    # BREAKOUT DISTANCE
    # ========================================================

    def _calculate_breakout_distance(
        self,
        current_close,
        upper_boundary,
        lower_boundary,
    ) -> float:

        distances = []

        if upper_boundary is not None:
            upper = float(upper_boundary)

            if current_close > upper:
                distances.append(
                    abs(
                        current_close - upper
                    ) / max(abs(upper), 1e-9)
                )

        if lower_boundary is not None:
            lower = float(lower_boundary)

            if current_close < lower:
                distances.append(
                    abs(
                        lower - current_close
                    ) / max(abs(lower), 1e-9)
                )

        if not distances:
            return 0.0

        distance = max(distances)

        # Proxy normalization.
        return self._clip(
            distance /
            max(self.boundary_tolerance, 1e-9)
            * 50.0
        )

    # ========================================================
    # CANDLE STRENGTH
    # ========================================================

    def _calculate_candle_strength(
        self,
        current_open,
        current_high,
        current_low,
        current_close,
    ) -> float:

        candle_range = (
            current_high - current_low
        )

        if candle_range <= 0:
            return 0.0

        body = abs(
            current_close - current_open
        )

        body_ratio = (
            body / candle_range
        )

        return self._clip(
            body_ratio * 100.0
        )

    # ========================================================
    # VOLUME CONFIRMATION
    # ========================================================

    def _calculate_volume_confirmation(
        self,
        volumes,
        average_volume,
    ) -> float:

        if not volumes:
            return 50.0

        latest_volume = float(volumes[-1])

        if average_volume is None:

            if len(volumes) < 3:
                return 50.0

            baseline = sum(
                float(v)
                for v in volumes[:-1]
            ) / max(
                len(volumes) - 1,
                1,
            )

        else:
            baseline = float(
                average_volume
            )

        if baseline <= 0:
            return 0.0

        ratio = (
            latest_volume /
            baseline
        )

        # Proxy:
        # 1.0x = neutral
        # >= 2.0x = strong participation
        score = ratio * 50.0

        return self._clip(score)

    # ========================================================
    # DIRECTIONAL ALIGNMENT
    # ========================================================

    def _calculate_directional_alignment(
        self,
        close_series,
        expected_direction,
        upper_strength,
        lower_strength,
    ) -> float:

        if len(close_series) < 2:
            return 50.0

        price_change = (
            float(close_series[-1])
            - float(close_series[-2])
        )

        if expected_direction == "BULLISH":

            if price_change > 0:
                return self._clip(
                    50.0 + upper_strength * 0.50
                )

            if price_change < 0:
                return 25.0

            return 50.0

        if expected_direction == "BEARISH":

            if price_change < 0:
                return self._clip(
                    50.0 + lower_strength * 0.50
                )

            if price_change > 0:
                return 25.0

            return 50.0

        if upper_strength > lower_strength:
            return self._clip(
                50.0 + upper_strength * 0.50
            )

        if lower_strength > upper_strength:
            return self._clip(
                50.0 + lower_strength * 0.50
            )

        return 50.0

    # ========================================================
    # PERSISTENCE
    # ========================================================

    def _calculate_persistence(
        self,
        close_series,
        upper_boundary,
        lower_boundary,
    ) -> float:

        if not close_series:
            return 0.0

        recent = close_series[
            max(0, len(close_series) - 5):
        ]

        upper_ratio = 0.0
        lower_ratio = 0.0

        if upper_boundary is not None:

            upper = float(upper_boundary)

            upper_ratio = (
                sum(
                    close > upper
                    for close in recent
                )
                / len(recent)
            )

        if lower_boundary is not None:

            lower = float(lower_boundary)

            lower_ratio = (
                sum(
                    close < lower
                    for close in recent
                )
                / len(recent)
            )

        return self._clip(
            max(
                upper_ratio,
                lower_ratio,
            ) * 100.0
        )

    # ========================================================
    # DIRECTION RESOLUTION
    # ========================================================

    def _resolve_direction(
        self,
        upper_strength,
        lower_strength,
        expected_direction,
    ) -> str:

        if (
            expected_direction
            in ("BULLISH", "BEARISH")
        ):
            return expected_direction

        if upper_strength > lower_strength:
            return "BULLISH"

        if lower_strength > upper_strength:
            return "BEARISH"

        return "NEUTRAL"

    # ========================================================
    # CONFIRMATION STATUS
    # ========================================================

    def _resolve_confirmation_status(
        self,
        event_confirmation_score,
        close_acceptance_score,
        directional_alignment_score,
    ) -> str:

        if (
            event_confirmation_score
            >= self.minimum_confirmation_score
            and close_acceptance_score
            >= self.minimum_acceptance_score
            and directional_alignment_score
            >= 50.0
        ):
            return "EVENT_CONFIRMED"

        if event_confirmation_score >= 45.0:
            return "PARTIAL_CONFIRMATION"

        return "NOT_CONFIRMED"

    # ========================================================
    # EVIDENCE QUALITY
    # ========================================================

    def _calculate_evidence_quality(
        self,
        penetration,
        acceptance,
        distance,
        candle,
        volume,
        alignment,
        persistence,
    ) -> float:

        score = (
            penetration * 0.15
            + acceptance * 0.25
            + distance * 0.10
            + candle * 0.10
            + volume * 0.15
            + alignment * 0.10
            + persistence * 0.15
        )

        return self._clip(score)

    # ========================================================
    # CONFIDENCE
    # ========================================================

    def _calculate_confidence(
        self,
        event_confirmation_score,
        evidence_quality,
        close_acceptance_score,
        persistence_score,
    ) -> float:

        return self._clip(
            event_confirmation_score * 0.35
            + evidence_quality * 0.35
            + close_acceptance_score * 0.15
            + persistence_score * 0.15
        )

    # ========================================================
    # CALIBRATION
    # ========================================================

    def _calibration_status(
        self,
        calibration_model,
    ) -> str:

        try:

            if hasattr(
                calibration_model,
                "predict_proba",
            ):
                return "HISTORICAL_MODEL"

            if callable(calibration_model):
                return "HISTORICAL_MODEL"

        except Exception:
            pass

        return "UNCALIBRATED"

    # ========================================================
    # INSUFFICIENT DATA
    # ========================================================

    def _insufficient_data_result(
        self,
    ) -> BreakoutEventValidation:

        return BreakoutEventValidation(
            upper_breakout_strength=0.0,
            lower_breakout_strength=0.0,
            boundary_penetration_score=0.0,
            close_acceptance_score=0.0,
            breakout_distance_score=0.0,
            candle_strength_score=0.0,
            volume_confirmation_score=0.0,
            directional_alignment_score=0.0,
            persistence_score=0.0,
            event_confirmation_score=0.0,
            confirmed_direction="NEUTRAL",
            confirmation_status="INSUFFICIENT_DATA",
            evidence_quality=0.0,
            confidence=0.0,
            calibration_status="UNCALIBRATED",
            evidence={
                "engine": "ConfirmationEngine",
                "part": "PART_2",
                "status": "INSUFFICIENT_DATA",
                "governance": {
                    "final_decision_authority": "D13",
                    "formula_status": (
                        "PROXY_UNTIL_VALIDATED"
                    ),
                },
            },
        )

    # ========================================================
    # CLIP
    # ========================================================

    def _clip(
        self,
        value,
    ) -> float:

        try:
            value = float(value)
        except (
            TypeError,
            ValueError,
        ):
            return 0.0

        return max(
            0.0,
            min(
                100.0,
                value,
            ),
        )
```
```python
"""
ROBOMLM_PLUS
Confirmation Engine - Part 3

ACCEPTANCE & RETEST INTELLIGENCE

Purpose
-------
Determine whether price movement beyond the active boundary
is being accepted by the market or rejected back into the
previous structure.

IMPORTANT
---------
Boundary discovery itself belongs to Boundary Engine.

This module does NOT invent the market boundary.

It consumes:
    - active upper boundary
    - active lower boundary
    - OHLCV
    - Part-1 foundation
    - Part-2 breakout event validation

and evaluates:
    - excursion vs breakout
    - close acceptance
    - penetration persistence
    - retest behavior
    - return-inside risk
    - acceptance quality

Final decision authority:
    D13
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Sequence


# ============================================================
# DATA CONTRACT
# ============================================================

@dataclass
class AcceptanceRetestIntelligence:

    # Boundary state
    active_boundary: Optional[float]
    boundary_side: str

    # Breakout state
    wick_excursion_score: float
    close_outside_score: float
    meaningful_penetration_score: float

    # Acceptance
    acceptance_score: float
    acceptance_persistence: float

    # Retest
    retest_detected: bool
    retest_quality: float
    retest_hold_score: float

    # Failure
    return_inside_risk: float
    rejection_risk: float

    # Final layer score
    acceptance_confirmation_score: float

    confirmation_state: str
    confirmed_direction: str

    evidence_quality: float
    confidence: float

    calibration_status: str

    evidence: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# ENGINE
# ============================================================

class ConfirmationEngine:
    """
    Confirmation Engine - Part 3

    Acceptance + Retest Intelligence.

    Boundary ownership:
        Boundary Engine

    Confirmation ownership:
        Confirmation Engine

    Final decision:
        D13
    """

    def __init__(
        self,
        boundary_tolerance: float = 0.0025,
        minimum_acceptance_score: float = 60.0,
        minimum_retest_score: float = 55.0,
        lookback: int = 5,
    ):

        self.boundary_tolerance = boundary_tolerance
        self.minimum_acceptance_score = (
            minimum_acceptance_score
        )
        self.minimum_retest_score = (
            minimum_retest_score
        )
        self.lookback = max(2, int(lookback))

    # ========================================================
    # MAIN EVALUATION
    # ========================================================

    def evaluate_acceptance_retest(
        self,
        closes: Sequence[float],
        highs: Optional[Sequence[float]] = None,
        lows: Optional[Sequence[float]] = None,
        opens: Optional[Sequence[float]] = None,
        volumes: Optional[Sequence[float]] = None,

        upper_boundary: Optional[float] = None,
        lower_boundary: Optional[float] = None,

        expected_direction: Optional[str] = None,

        part1_data=None,
        part2_data=None,

        calibration_model=None,
    ) -> AcceptanceRetestIntelligence:

        closes = list(closes)

        if not closes:
            return self._insufficient_data()

        highs = list(
            highs if highs is not None else closes
        )

        lows = list(
            lows if lows is not None else closes
        )

        opens = list(
            opens if opens is not None else closes
        )

        # ----------------------------------------------------
        # CURRENT PRICE
        # ----------------------------------------------------

        current_close = float(closes[-1])
        current_high = float(highs[-1])
        current_low = float(lows[-1])
        current_open = float(opens[-1])

        # ====================================================
        # 1. SELECT ACTIVE BOUNDARY
        # ====================================================

        active_boundary, boundary_side = (
            self._select_active_boundary(
                current_close=current_close,
                upper_boundary=upper_boundary,
                lower_boundary=lower_boundary,
                expected_direction=expected_direction,
            )
        )

        # ====================================================
        # 2. WICK EXCURSION
        # ====================================================

        wick_excursion_score = (
            self._calculate_wick_excursion(
                current_high=current_high,
                current_low=current_low,
                upper_boundary=upper_boundary,
                lower_boundary=lower_boundary,
            )
        )

        # ====================================================
        # 3. CLOSE OUTSIDE
        # ====================================================

        close_outside_score = (
            self._calculate_close_outside(
                closes=closes,
                upper_boundary=upper_boundary,
                lower_boundary=lower_boundary,
                expected_direction=expected_direction,
            )
        )

        # ====================================================
        # 4. MEANINGFUL PENETRATION
        # ====================================================

        meaningful_penetration_score = (
            self._calculate_meaningful_penetration(
                current_close=current_close,
                active_boundary=active_boundary,
                boundary_side=boundary_side,
            )
        )

        # ====================================================
        # 5. ACCEPTANCE PERSISTENCE
        # ====================================================

        acceptance_persistence = (
            self._calculate_acceptance_persistence(
                closes=closes,
                active_boundary=active_boundary,
                boundary_side=boundary_side,
            )
        )

        # ====================================================
        # 6. ACCEPTANCE SCORE
        # ====================================================

        acceptance_score = (
            close_outside_score * 0.35
            + meaningful_penetration_score * 0.20
            + acceptance_persistence * 0.30
            + wick_excursion_score * 0.15
        )

        acceptance_score = self._clip(
            acceptance_score
        )

        # ====================================================
        # 7. RETEST DETECTION
        # ====================================================

        retest_detected, retest_quality = (
            self._detect_retest(
                closes=closes,
                highs=highs,
                lows=lows,
                active_boundary=active_boundary,
                boundary_side=boundary_side,
            )
        )

        # ====================================================
        # 8. RETEST HOLD
        # ====================================================

        retest_hold_score = (
            self._calculate_retest_hold(
                closes=closes,
                active_boundary=active_boundary,
                boundary_side=boundary_side,
            )
        )

        # ====================================================
        # 9. RETURN INSIDE RISK
        # ====================================================

        return_inside_risk = (
            self._calculate_return_inside_risk(
                closes=closes,
                active_boundary=active_boundary,
                boundary_side=boundary_side,
            )
        )

        # ====================================================
        # 10. REJECTION RISK
        # ====================================================

        rejection_risk = (
            self._calculate_rejection_risk(
                wick_excursion_score=wick_excursion_score,
                close_outside_score=close_outside_score,
                acceptance_persistence=(
                    acceptance_persistence
                ),
                return_inside_risk=return_inside_risk,
            )
        )

        # ====================================================
        # 11. FINAL ACCEPTANCE CONFIRMATION
        # ====================================================

        acceptance_confirmation_score = (
            acceptance_score * 0.35
            + acceptance_persistence * 0.20
            + retest_quality * 0.15
            + retest_hold_score * 0.15
            + (100.0 - return_inside_risk) * 0.10
            + (100.0 - rejection_risk) * 0.05
        )

        acceptance_confirmation_score = self._clip(
            acceptance_confirmation_score
        )

        # ====================================================
        # 12. DIRECTION
        # ====================================================

        confirmed_direction = self._resolve_direction(
            boundary_side=boundary_side,
            expected_direction=expected_direction,
        )

        # ====================================================
        # 13. STATE
        # ====================================================

        confirmation_state = (
            self._resolve_confirmation_state(
                acceptance_score=acceptance_score,
                retest_quality=retest_quality,
                retest_hold_score=retest_hold_score,
                return_inside_risk=return_inside_risk,
                rejection_risk=rejection_risk,
                final_score=(
                    acceptance_confirmation_score
                ),
            )
        )

        # ====================================================
        # 14. EVIDENCE QUALITY
        # ====================================================

        evidence_quality = (
            close_outside_score * 0.20
            + meaningful_penetration_score * 0.15
            + acceptance_persistence * 0.20
            + retest_quality * 0.15
            + retest_hold_score * 0.15
            + (100.0 - return_inside_risk) * 0.10
            + (100.0 - rejection_risk) * 0.05
        )

        evidence_quality = self._clip(
            evidence_quality
        )

        # ====================================================
        # 15. CONFIDENCE
        # ====================================================

        confidence = (
            acceptance_confirmation_score * 0.45
            + evidence_quality * 0.35
            + acceptance_persistence * 0.20
        )

        confidence = self._clip(
            confidence
        )

        # ====================================================
        # 16. CALIBRATION
        # ====================================================

        calibration_status = "UNCALIBRATED"

        if calibration_model is not None:

            calibration_status = (
                self._calibration_status(
                    calibration_model
                )
            )

        # ====================================================
        # 17. EVIDENCE TRACE
        # ====================================================

        evidence = {

            "engine": "ConfirmationEngine",

            "part": "PART_3",

            "layer": (
                "ACCEPTANCE_AND_RETEST"
            ),

            "boundary_ownership": (
                "BoundaryEngine"
            ),

            "active_boundary": {
                "value": active_boundary,
                "side": boundary_side,
            },

            "market_state": {
                "current_open": current_open,
                "current_high": current_high,
                "current_low": current_low,
                "current_close": current_close,
            },

            "measurements": {

                "wick_excursion_score":
                    wick_excursion_score,

                "close_outside_score":
                    close_outside_score,

                "meaningful_penetration_score":
                    meaningful_penetration_score,

                "acceptance_score":
                    acceptance_score,

                "acceptance_persistence":
                    acceptance_persistence,

                "retest_detected":
                    retest_detected,

                "retest_quality":
                    retest_quality,

                "retest_hold_score":
                    retest_hold_score,

                "return_inside_risk":
                    return_inside_risk,

                "rejection_risk":
                    rejection_risk,

                "acceptance_confirmation_score":
                    acceptance_confirmation_score,
            },

            "result": {

                "confirmation_state":
                    confirmation_state,

                "confirmed_direction":
                    confirmed_direction,

                "evidence_quality":
                    evidence_quality,

                "confidence":
                    confidence,
            },

            "governance": {

                "final_decision_authority":
                    "D13",

                "boundary_authority":
                    "BoundaryEngine",

                "formula_status":
                    "PROXY_UNTIL_VALIDATED",

                "calibration_status":
                    calibration_status,
            },
        }

        return AcceptanceRetestIntelligence(

            active_boundary=active_boundary,

            boundary_side=boundary_side,

            wick_excursion_score=(
                wick_excursion_score
            ),

            close_outside_score=(
                close_outside_score
            ),

            meaningful_penetration_score=(
                meaningful_penetration_score
            ),

            acceptance_score=(
                acceptance_score
            ),

            acceptance_persistence=(
                acceptance_persistence
            ),

            retest_detected=(
                retest_detected
            ),

            retest_quality=(
                retest_quality
            ),

            retest_hold_score=(
                retest_hold_score
            ),

            return_inside_risk=(
                return_inside_risk
            ),

            rejection_risk=(
                rejection_risk
            ),

            acceptance_confirmation_score=(
                acceptance_confirmation_score
            ),

            confirmation_state=(
                confirmation_state
            ),

            confirmed_direction=(
                confirmed_direction
            ),

            evidence_quality=(
                evidence_quality
            ),

            confidence=confidence,

            calibration_status=(
                calibration_status
            ),

            evidence=evidence,
        )

    # ========================================================
    # ACTIVE BOUNDARY SELECTION
    # ========================================================

    def _select_active_boundary(
        self,
        current_close: float,
        upper_boundary: Optional[float],
        lower_boundary: Optional[float],
        expected_direction: Optional[str],
    ):

        """
        IMPORTANT:

        This function does NOT calculate a new boundary.

        It only selects which already-calculated Boundary Engine
        level is relevant to the current breakout event.
        """

        if expected_direction == "BULLISH":

            if upper_boundary is not None:
                return (
                    float(upper_boundary),
                    "UPPER",
                )

        if expected_direction == "BEARISH":

            if lower_boundary is not None:
                return (
                    float(lower_boundary),
                    "LOWER",
                )

        # If direction is not supplied, infer which boundary
        # is actually being challenged.

        candidates = []

        if upper_boundary is not None:
            distance = abs(
                current_close -
                float(upper_boundary)
            )

            candidates.append(
                (
                    distance,
                    float(upper_boundary),
                    "UPPER",
                )
            )

        if lower_boundary is not None:
            distance = abs(
                current_close -
                float(lower_boundary)
            )

            candidates.append(
                (
                    distance,
                    float(lower_boundary),
                    "LOWER",
                )
            )

        if not candidates:
            return None, "UNKNOWN"

        candidates.sort(
            key=lambda x: x[0]
        )

        return (
            candidates[0][1],
            candidates[0][2],
        )

    # ========================================================
    # WICK EXCURSION
    # ========================================================

    def _calculate_wick_excursion(
        self,
        current_high,
        current_low,
        upper_boundary,
        lower_boundary,
    ):

        scores = []

        if upper_boundary is not None:

            upper = float(
                upper_boundary
            )

            if current_high > upper:

                penetration = (
                    current_high - upper
                ) / max(
                    abs(upper),
                    1e-9,
                )

                score = (
                    penetration /
                    max(
                        self.boundary_tolerance,
                        1e-9,
                    )
                ) * 50.0

                scores.append(
                    self._clip(score)
                )

        if lower_boundary is not None:

            lower = float(
                lower_boundary
            )

            if current_low < lower:

                penetration = (
                    lower - current_low
                ) / max(
                    abs(lower),
                    1e-9,
                )

                score = (
                    penetration /
                    max(
                        self.boundary_tolerance,
                        1e-9,
                    )
                ) * 50.0

                scores.append(
                    self._clip(score)
                )

        if not scores:
            return 0.0

        return max(scores)

    # ========================================================
    # CLOSE OUTSIDE
    # ========================================================

    def _calculate_close_outside(
        self,
        closes,
        upper_boundary,
        lower_boundary,
        expected_direction,
    ):

        recent = closes[
            -self.lookback:
        ]

        if not recent:
            return 0.0

        if expected_direction == "BULLISH":

            if upper_boundary is None:
                return 0.0

            upper = float(
                upper_boundary
            )

            ratio = (
                sum(
                    float(close) > upper
                    for close in recent
                )
                / len(recent)
            )

            return self._clip(
                ratio * 100.0
            )

        if expected_direction == "BEARISH":

            if lower_boundary is None:
                return 0.0

            lower = float(
                lower_boundary
            )

            ratio = (
                sum(
                    float(close) < lower
                    for close in recent
                )
                / len(recent)
            )

            return self._clip(
                ratio * 100.0
            )

        # No direction supplied.
        scores = []

        if upper_boundary is not None:

            upper = float(
                upper_boundary
            )

            scores.append(
                (
                    sum(
                        float(close) > upper
                        for close in recent
                    )
                    / len(recent)
                ) * 100.0
            )

        if lower_boundary is not None:

            lower = float(
                lower_boundary
            )

            scores.append(
                (
                    sum(
                        float(close) < lower
                        for close in recent
                    )
                    / len(recent)
                ) * 100.0
            )

        if not scores:
            return 0.0

        return self._clip(
            max(scores)
        )

    # ========================================================
    # MEANINGFUL PENETRATION
    # ========================================================

    def _calculate_meaningful_penetration(
        self,
        current_close,
        active_boundary,
        boundary_side,
    ):

        if active_boundary is None:
            return 0.0

        boundary = float(
            active_boundary
        )

        if boundary == 0:
            return 0.0

        if boundary_side == "UPPER":

            penetration = (
                current_close - boundary
            ) / abs(boundary)

        elif boundary_side == "LOWER":

            penetration = (
                boundary - current_close
            ) / abs(boundary)

        else:
            return 0.0

        if penetration <= 0:
            return 0.0

        score = (
            penetration /
            max(
                self.boundary_tolerance,
                1e-9,
            )
        ) * 50.0

        return self._clip(
            score
        )

    # ========================================================
    # ACCEPTANCE PERSISTENCE
    # ========================================================

    def _calculate_acceptance_persistence(
        self,
        closes,
        active_boundary,
        boundary_side,
    ):

        if (
            active_boundary is None
            or not closes
        ):
            return 0.0

        boundary = float(
            active_boundary
        )

        recent = closes[
            -self.lookback:
        ]

        if boundary_side == "UPPER":

            accepted = [
                float(close) > boundary
                for close in recent
            ]

        elif boundary_side == "LOWER":

            accepted = [
                float(close) < boundary
                for close in recent
            ]

        else:
            return 0.0

        return self._clip(
            (
                sum(accepted)
                / len(accepted)
            ) * 100.0
        )

    # ========================================================
    # RETEST DETECTION
    # ========================================================

    def _detect_retest(
        self,
        closes,
        highs,
        lows,
        active_boundary,
        boundary_side,
    ):

        if (
            active_boundary is None
            or len(closes) < 3
        ):
            return False, 0.0

        boundary = float(
            active_boundary
        )

        recent_closes = closes[
            -self.lookback:
        ]

        touched = 0
        recovered = 0

        for close, high, low in zip(
            recent_closes,
            highs[-self.lookback:],
            lows[-self.lookback:],
        ):

            close = float(close)
            high = float(high)
            low = float(low)

            distance = abs(
                close - boundary
            ) / max(
                abs(boundary),
                1e-9,
            )

            near_boundary = (
                distance
                <= self.boundary_tolerance
            )

            if boundary_side == "UPPER":

                crossed_or_touched = (
                    low <= boundary
                    or near_boundary
                )

                if crossed_or_touched:
                    touched += 1

                    if close > boundary:
                        recovered += 1

            elif boundary_side == "LOWER":

                crossed_or_touched = (
                    high >= boundary
                    or near_boundary
                )

                if crossed_or_touched:
                    touched += 1

                    if close < boundary:
                        recovered += 1

        if touched == 0:
            return False, 0.0

        quality = (
            recovered / touched
        ) * 100.0

        return True, self._clip(
            quality
        )

    # ========================================================
    # RETEST HOLD
    # ========================================================

    def _calculate_retest_hold(
        self,
        closes,
        active_boundary,
        boundary_side,
    ):

        if (
            active_boundary is None
            or len(closes) < 2
        ):
            return 0.0

        boundary = float(
            active_boundary
        )

        recent = closes[
            -self.lookback:
        ]

        if boundary_side == "UPPER":

            holds = [
                float(close) > boundary
                for close in recent
            ]

        elif boundary_side == "LOWER":

            holds = [
                float(close) < boundary
                for close in recent
            ]

        else:
            return 0.0

        return self._clip(
            (
                sum(holds)
                / len(holds)
            ) * 100.0
        )

    # ========================================================
    # RETURN INSIDE RISK
    # ========================================================

    def _calculate_return_inside_risk(
        self,
        closes,
        active_boundary,
        boundary_side,
    ):

        if (
            active_boundary is None
            or not closes
        ):
            return 50.0

        boundary = float(
            active_boundary
        )

        recent = closes[
            -self.lookback:
        ]

        if boundary_side == "UPPER":

            inside = [
                float(close) <= boundary
                for close in recent
            ]

        elif boundary_side == "LOWER":

            inside = [
                float(close) >= boundary
                for close in recent
            ]

        else:
            return 50.0

        return self._clip(
            (
                sum(inside)
                / len(inside)
            ) * 100.0
        )

    # ========================================================
    # REJECTION RISK
    # ========================================================

    def _calculate_rejection_risk(
        self,
        wick_excursion_score,
        close_outside_score,
        acceptance_persistence,
        return_inside_risk,
    ):

        weak_close = (
            100.0 -
            close_outside_score
        )

        weak_persistence = (
            100.0 -
            acceptance_persistence
        )

        risk = (
            weak_close * 0.30
            + weak_persistence * 0.30
            + return_inside_risk * 0.25
            + (
                100.0 -
                wick_excursion_score
            ) * 0.15
        )

        return self._clip(
            risk
        )

    # ========================================================
    # CONFIRMATION STATE
    # ========================================================

    def _resolve_confirmation_state(
        self,
        acceptance_score,
        retest_quality,
        retest_hold_score,
        return_inside_risk,
        rejection_risk,
        final_score,
    ):

        if (
            final_score
            >= self.minimum_acceptance_score
            and acceptance_score
            >= self.minimum_acceptance_score
            and return_inside_risk < 35.0
            and rejection_risk < 40.0
        ):

            if (
                retest_quality
                >= self.minimum_retest_score
                and retest_hold_score
                >= self.minimum_retest_score
            ):
                return "ACCEPTED_WITH_RETEST"

            return "ACCEPTED"

        if final_score >= 45.0:
            return "PARTIAL_ACCEPTANCE"

        if rejection_risk >= 70.0:
            return "REJECTED"

        return "UNCONFIRMED"

    # ========================================================
    # DIRECTION
    # ========================================================

    def _resolve_direction(
        self,
        boundary_side,
        expected_direction,
    ):

        if expected_direction in (
            "BULLISH",
            "BEARISH",
        ):
            return expected_direction

        if boundary_side == "UPPER":
            return "BULLISH"

        if boundary_side == "LOWER":
            return "BEARISH"

        return "NEUTRAL"

    # ========================================================
    # CALIBRATION
    # ========================================================

    def _calibration_status(
        self,
        calibration_model,
    ):

        try:

            if hasattr(
                calibration_model,
                "predict_proba",
            ):
                return "HISTORICAL_MODEL"

            if callable(
                calibration_model
            ):
                return "HISTORICAL_MODEL"

        except Exception:
            pass

        return "UNCALIBRATED"

    # ========================================================
    # INSUFFICIENT DATA
    # ========================================================

    def _insufficient_data(self):

        return AcceptanceRetestIntelligence(

            active_boundary=None,

            boundary_side="UNKNOWN",

            wick_excursion_score=0.0,

            close_outside_score=0.0,

            meaningful_penetration_score=0.0,

            acceptance_score=0.0,

            acceptance_persistence=0.0,

            retest_detected=False,

            retest_quality=0.0,

            retest_hold_score=0.0,

            return_inside_risk=100.0,

            rejection_risk=100.0,

            acceptance_confirmation_score=0.0,

            confirmation_state=(
                "INSUFFICIENT_DATA"
            ),

            confirmed_direction="NEUTRAL",

            evidence_quality=0.0,

            confidence=0.0,

            calibration_status=(
                "UNCALIBRATED"
            ),

            evidence={
                "engine":
                    "ConfirmationEngine",

                "part":
                    "PART_3",

                "status":
                    "INSUFFICIENT_DATA",

                "governance": {
                    "final_decision_authority":
                        "D13",

                    "boundary_authority":
                        "BoundaryEngine",
                },
            },
        )

    # ========================================================
    # CLIP
    # ========================================================

    def _clip(
        self,
        value,
    ):

        try:
            value = float(value)

        except (
            TypeError,
            ValueError,
        ):
            return 0.0

        return max(
            0.0,
            min(
                100.0,
                value,
            ),
        )
```
# confirmation_engine.py
# ============================================================
# CONFIRMATION ENGINE — PART 4
# MULTI-FACTOR CONTINUATION CONFIRMATION
# ============================================================

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List


# ============================================================
# OUTPUT CONTRACT
# ============================================================

@dataclass
class ContinuationConfirmation:
    direction: str

    price_confirmation_score: float
    volume_confirmation_score: float
    momentum_confirmation_score: float
    structure_confirmation_score: float
    retest_confirmation_score: float

    directional_alignment: float
    continuation_score: float
    confirmation_score: float

    continuation_probability: float
    failure_probability: float

    confirmation_state: str
    confidence: float
    evidence_quality: float

    calibration_status: str

    evidence: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# ENGINE
# ============================================================

class ConfirmationEngine:
    """
    Part-4:
    Multi-Factor Continuation Confirmation.

    ROLE
    ----
    Validate whether an already accepted boundary breakout
    is showing enough aligned evidence for continuation.

    DOES NOT
    ----------
    - calculate boundary
    - invent breakout levels
    - make final BUY/SELL decision
    - replace D13
    - invent formulas

    Boundary authority:
        Boundary Engine

    Final decision authority:
        D13
    """

    def __init__(
        self,
        minimum_confirmation_score: float = 65.0,
        minimum_continuation_score: float = 60.0,
        minimum_evidence_quality: float = 50.0,
        volume_expansion_threshold: float = 1.20,
        momentum_threshold: float = 55.0,
    ):
        self.minimum_confirmation_score = minimum_confirmation_score
        self.minimum_continuation_score = minimum_continuation_score
        self.minimum_evidence_quality = minimum_evidence_quality
        self.volume_expansion_threshold = volume_expansion_threshold
        self.momentum_threshold = momentum_threshold

    # ========================================================
    # PUBLIC API
    # ========================================================

    def evaluate_continuation(
        self,
        closes: List[float],
        volumes: Optional[List[float]] = None,
        opens: Optional[List[float]] = None,
        highs: Optional[List[float]] = None,
        lows: Optional[List[float]] = None,

        direction: str = "UNKNOWN",

        acceptance_data: Optional[Any] = None,
        retest_data: Optional[Any] = None,

        structure_score: float = 50.0,
        momentum_score: Optional[float] = None,
        participation_score: Optional[float] = None,

        calibration_model: Optional[Any] = None,
    ) -> ContinuationConfirmation:

        if not closes or len(closes) < 3:
            return self._insufficient_data()

        direction = str(direction).upper()

        # ----------------------------------------------------
        # 1. PRICE CONFIRMATION
        # ----------------------------------------------------

        price_confirmation = self._calculate_price_confirmation(
            closes=closes,
            direction=direction
        )

        # ----------------------------------------------------
        # 2. VOLUME CONFIRMATION
        # ----------------------------------------------------

        volume_confirmation = self._calculate_volume_confirmation(
            volumes=volumes,
            direction=direction
        )

        # ----------------------------------------------------
        # 3. MOMENTUM CONFIRMATION
        # ----------------------------------------------------

        if momentum_score is None:
            momentum_confirmation = self._calculate_momentum(
                closes=closes,
                direction=direction
            )
        else:
            momentum_confirmation = self._clip(momentum_score)

        # ----------------------------------------------------
        # 4. STRUCTURE CONFIRMATION
        # ----------------------------------------------------

        structure_confirmation = self._clip(structure_score)

        # ----------------------------------------------------
        # 5. RETEST CONFIRMATION
        # ----------------------------------------------------

        retest_confirmation = self._extract_retest_score(
            retest_data=retest_data,
            acceptance_data=acceptance_data
        )

        # ----------------------------------------------------
        # 6. PARTICIPATION ADJUSTMENT
        # ----------------------------------------------------

        if participation_score is not None:
            participation_confirmation = self._clip(
                participation_score
            )
        else:
            participation_confirmation = 50.0

        # ----------------------------------------------------
        # 7. DIRECTIONAL ALIGNMENT
        # ----------------------------------------------------

        directional_alignment = self._calculate_directional_alignment(
            direction=direction,
            price_confirmation=price_confirmation,
            volume_confirmation=volume_confirmation,
            momentum_confirmation=momentum_confirmation,
            structure_confirmation=structure_confirmation,
            retest_confirmation=retest_confirmation,
        )

        # ----------------------------------------------------
        # 8. CONTINUATION SCORE
        # ----------------------------------------------------

        continuation_score = (
            price_confirmation * 0.25
            + volume_confirmation * 0.15
            + momentum_confirmation * 0.20
            + structure_confirmation * 0.15
            + retest_confirmation * 0.15
            + participation_confirmation * 0.10
        )

        continuation_score = self._clip(continuation_score)

        # ----------------------------------------------------
        # 9. FINAL CONFIRMATION SCORE
        # ----------------------------------------------------

        confirmation_score = (
            continuation_score * 0.70
            + directional_alignment * 0.30
        )

        confirmation_score = self._clip(confirmation_score)

        # ----------------------------------------------------
        # 10. FAILURE PROBABILITY
        # ----------------------------------------------------

        failure_probability = self._calculate_failure_probability(
            continuation_score=continuation_score,
            directional_alignment=directional_alignment,
            retest_confirmation=retest_confirmation,
        )

        # ----------------------------------------------------
        # 11. CONTINUATION PROBABILITY
        # ----------------------------------------------------

        continuation_probability = self._calculate_probability(
            confirmation_score=confirmation_score,
            failure_probability=failure_probability,
            calibration_model=calibration_model,
        )

        # ----------------------------------------------------
        # 12. EVIDENCE QUALITY
        # ----------------------------------------------------

        evidence_quality = self._calculate_evidence_quality(
            price_confirmation,
            volume_confirmation,
            momentum_confirmation,
            structure_confirmation,
            retest_confirmation,
            participation_confirmation,
        )

        # ----------------------------------------------------
        # 13. STATE
        # ----------------------------------------------------

        confirmation_state = self._resolve_state(
            confirmation_score=confirmation_score,
            continuation_score=continuation_score,
            evidence_quality=evidence_quality,
            failure_probability=failure_probability,
        )

        # ----------------------------------------------------
        # 14. CONFIDENCE
        # ----------------------------------------------------

        confidence = self._calculate_confidence(
            confirmation_score=confirmation_score,
            evidence_quality=evidence_quality,
            directional_alignment=directional_alignment,
        )

        evidence = {
            "price_confirmation_score": price_confirmation,
            "volume_confirmation_score": volume_confirmation,
            "momentum_confirmation_score": momentum_confirmation,
            "structure_confirmation_score": structure_confirmation,
            "retest_confirmation_score": retest_confirmation,
            "participation_confirmation_score": participation_confirmation,
            "directional_alignment": directional_alignment,
            "continuation_score": continuation_score,
            "confirmation_score": confirmation_score,
            "continuation_probability": continuation_probability,
            "failure_probability": failure_probability,
            "formula_status": "PROVISIONAL",
            "decision_authority": "D13",
            "boundary_authority": "BoundaryEngine",
        }

        return ContinuationConfirmation(
            direction=direction,
            price_confirmation_score=price_confirmation,
            volume_confirmation_score=volume_confirmation,
            momentum_confirmation_score=momentum_confirmation,
            structure_confirmation_score=structure_confirmation,
            retest_confirmation_score=retest_confirmation,
            directional_alignment=directional_alignment,
            continuation_score=continuation_score,
            confirmation_score=confirmation_score,
            continuation_probability=continuation_probability,
            failure_probability=failure_probability,
            confirmation_state=confirmation_state,
            confidence=confidence,
            evidence_quality=evidence_quality,
            calibration_status=self._calibration_status(
                calibration_model
            ),
            evidence=evidence,
        )

    # ========================================================
    # PRICE CONFIRMATION
    # ========================================================

    def _calculate_price_confirmation(
        self,
        closes: List[float],
        direction: str,
    ) -> float:

        if len(closes) < 3:
            return 0.0

        recent = closes[-3:]

        if direction == "BULLISH":
            higher = 0

            if recent[1] > recent[0]:
                higher += 1

            if recent[2] > recent[1]:
                higher += 1

            return higher / 2.0 * 100.0

        if direction == "BEARISH":
            lower = 0

            if recent[1] < recent[0]:
                lower += 1

            if recent[2] < recent[1]:
                lower += 1

            return lower / 2.0 * 100.0

        return 50.0

    # ========================================================
    # VOLUME CONFIRMATION
    # ========================================================

    def _calculate_volume_confirmation(
        self,
        volumes: Optional[List[float]],
        direction: str,
    ) -> float:

        if not volumes or len(volumes) < 3:
            return 50.0

        latest = float(volumes[-1])

        baseline_values = volumes[:-1]

        if not baseline_values:
            return 50.0

        baseline = sum(baseline_values) / len(baseline_values)

        if baseline <= 0:
            return 50.0

        expansion_ratio = latest / baseline

        if expansion_ratio >= self.volume_expansion_threshold:
            score = min(
                100.0,
                50.0 + (expansion_ratio - 1.0) * 100.0
            )
        else:
            score = max(
                0.0,
                50.0 - (1.0 - expansion_ratio) * 100.0
            )

        return self._clip(score)

    # ========================================================
    # MOMENTUM
    # ========================================================

    def _calculate_momentum(
        self,
        closes: List[float],
        direction: str,
    ) -> float:

        if len(closes) < 3:
            return 50.0

        previous = closes[-2]
        latest = closes[-1]

        if previous == 0:
            return 50.0

        change_pct = (
            (latest - previous)
            / abs(previous)
        ) * 100.0

        if direction == "BULLISH":
            return self._clip(
                50.0 + change_pct * 100.0
            )

        if direction == "BEARISH":
            return self._clip(
                50.0 - change_pct * 100.0
            )

        return 50.0

    # ========================================================
    # RETEST EXTRACTION
    # ========================================================

    def _extract_retest_score(
        self,
        retest_data: Optional[Any],
        acceptance_data: Optional[Any],
    ) -> float:

        if retest_data is not None:

            value = getattr(
                retest_data,
                "retest_hold_score",
                None
            )

            if value is not None:
                return self._clip(value)

            value = getattr(
                retest_data,
                "retest_quality",
                None
            )

            if value is not None:
                return self._clip(value)

        if acceptance_data is not None:

            value = getattr(
                acceptance_data,
                "retest_hold_score",
                None
            )

            if value is not None:
                return self._clip(value)

            value = getattr(
                acceptance_data,
                "retest_quality",
                None
            )

            if value is not None:
                return self._clip(value)

        # No retest evidence is NOT automatically failure.
        return 50.0

    # ========================================================
    # DIRECTIONAL ALIGNMENT
    # ========================================================

    def _calculate_directional_alignment(
        self,
        direction: str,
        price_confirmation: float,
        volume_confirmation: float,
        momentum_confirmation: float,
        structure_confirmation: float,
        retest_confirmation: float,
    ) -> float:

        values = [
            price_confirmation,
            volume_confirmation,
            momentum_confirmation,
            structure_confirmation,
            retest_confirmation,
        ]

        if direction in ("BULLISH", "BEARISH"):
            return self._clip(
                sum(values) / len(values)
            )

        return 50.0

    # ========================================================
    # FAILURE PROBABILITY
    # ========================================================

    def _calculate_failure_probability(
        self,
        continuation_score: float,
        directional_alignment: float,
        retest_confirmation: float,
    ) -> float:

        failure = (
            (100.0 - continuation_score) * 0.50
            + (100.0 - directional_alignment) * 0.30
            + (100.0 - retest_confirmation) * 0.20
        )

        return self._clip(failure)

    # ========================================================
    # PROBABILITY
    # ========================================================

    def _calculate_probability(
        self,
        confirmation_score: float,
        failure_probability: float,
        calibration_model: Optional[Any],
    ) -> float:

        raw_probability = (
            confirmation_score * 0.70
            + (100.0 - failure_probability) * 0.30
        )

        # Optional future calibration hook.
        if calibration_model is not None:

            try:

                if hasattr(
                    calibration_model,
                    "predict_proba"
                ):
                    calibrated = calibration_model.predict_proba(
                        [[confirmation_score]]
                    )

                    if hasattr(calibrated, "__len__"):
                        value = float(calibrated[0][-1])
                        return self._clip(value * 100.0)

                elif callable(calibration_model):

                    value = float(
                        calibration_model(
                            confirmation_score
                        )
                    )

                    return self._clip(value)

            except Exception:
                pass

        return self._clip(raw_probability)

    # ========================================================
    # EVIDENCE QUALITY
    # ========================================================

    def _calculate_evidence_quality(
        self,
        price: float,
        volume: float,
        momentum: float,
        structure: float,
        retest: float,
        participation: float,
    ) -> float:

        values = [
            price,
            volume,
            momentum,
            structure,
            retest,
            participation,
        ]

        return self._clip(
            sum(values) / len(values)
        )

    # ========================================================
    # STATE RESOLUTION
    # ========================================================

    def _resolve_state(
        self,
        confirmation_score: float,
        continuation_score: float,
        evidence_quality: float,
        failure_probability: float,
    ) -> str:

        if evidence_quality < self.minimum_evidence_quality:
            return "INSUFFICIENT_EVIDENCE"

        if failure_probability >= 70.0:
            return "HIGH_FAILURE_RISK"

        if (
            confirmation_score >= self.minimum_confirmation_score
            and continuation_score >= self.minimum_continuation_score
        ):
            return "CONTINUATION_CONFIRMED"

        if continuation_score >= 50.0:
            return "CONTINUATION_BUILDING"

        return "CONTINUATION_UNCONFIRMED"

    # ========================================================
    # CONFIDENCE
    # ========================================================

    def _calculate_confidence(
        self,
        confirmation_score: float,
        evidence_quality: float,
        directional_alignment: float,
    ) -> float:

        confidence = (
            confirmation_score * 0.45
            + evidence_quality * 0.35
            + directional_alignment * 0.20
        )

        return self._clip(confidence)

    # ========================================================
    # CALIBRATION STATUS
    # ========================================================

    def _calibration_status(
        self,
        calibration_model: Optional[Any],
    ) -> str:

        if calibration_model is None:
            return "UNCALIBRATED"

        if (
            hasattr(calibration_model, "predict_proba")
            or callable(calibration_model)
        ):
            return "HISTORICAL_MODEL"

        return "UNCALIBRATED"

    # ========================================================
    # INSUFFICIENT DATA
    # ========================================================

    def _insufficient_data(self) -> ContinuationConfirmation:

        return ContinuationConfirmation(
            direction="UNKNOWN",
            price_confirmation_score=0.0,
            volume_confirmation_score=0.0,
            momentum_confirmation_score=0.0,
            structure_confirmation_score=0.0,
            retest_confirmation_score=0.0,
            directional_alignment=0.0,
            continuation_score=0.0,
            confirmation_score=0.0,
            continuation_probability=0.0,
            failure_probability=100.0,
            confirmation_state="INSUFFICIENT_DATA",
            confidence=0.0,
            evidence_quality=0.0,
            calibration_status="UNCALIBRATED",
            evidence={
                "formula_status": "PROVISIONAL",
                "decision_authority": "D13",
            },
        )

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
        except (TypeError, ValueError):
            return lower

        return max(
            lower,
            min(upper, value)
        )
# confirmation_engine.py
# ============================================================
# CONFIRMATION ENGINE — PART 5
# FAILURE / REJECTION / REVERSAL INTELLIGENCE
# ============================================================

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List


# ============================================================
# OUTPUT CONTRACT
# ============================================================

@dataclass
class FailureReversalIntelligence:
    direction: str

    boundary_failure_score: float
    rejection_score: float
    return_inside_score: float
    momentum_failure_score: float
    volume_failure_score: float
    structure_failure_score: float

    continuation_decay_score: float
    reversal_pressure_score: float
    trap_risk_score: float
    failure_probability: float
    reversal_probability: float

    failure_state: str
    reversal_state: str

    confidence: float
    evidence_quality: float
    calibration_status: str

    evidence: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# ENGINE
# ============================================================

class ConfirmationEngine:
    """
    Part-5:
    Failure / Rejection / Reversal Intelligence.

    ROLE
    ----
    Detect whether an apparent breakout/continuation is failing.

    Detects:
        - boundary rejection
        - return inside boundary
        - momentum deterioration
        - volume deterioration
        - structure deterioration
        - continuation decay
        - reversal pressure
        - trap risk

    DOES NOT
    ----------
        - calculate the boundary
        - change the Boundary Engine level
        - issue final BUY/SELL
        - override D13

    Boundary authority:
        BoundaryEngine

    Final decision authority:
        D13
    """

    def __init__(
        self,
        boundary_tolerance: float = 0.0025,
        failure_threshold: float = 60.0,
        high_failure_threshold: float = 75.0,
        reversal_threshold: float = 65.0,
        minimum_evidence_quality: float = 45.0,
    ):
        self.boundary_tolerance = boundary_tolerance
        self.failure_threshold = failure_threshold
        self.high_failure_threshold = high_failure_threshold
        self.reversal_threshold = reversal_threshold
        self.minimum_evidence_quality = minimum_evidence_quality

    # ========================================================
    # PUBLIC API
    # ========================================================

    def evaluate_failure_reversal(
        self,
        closes: List[float],
        highs: Optional[List[float]] = None,
        lows: Optional[List[float]] = None,
        volumes: Optional[List[float]] = None,

        direction: str = "UNKNOWN",

        upper_boundary: Optional[float] = None,
        lower_boundary: Optional[float] = None,

        continuation_data: Optional[Any] = None,
        acceptance_data: Optional[Any] = None,

        structure_score: float = 50.0,
        momentum_score: Optional[float] = None,

        calibration_model: Optional[Any] = None,
    ) -> FailureReversalIntelligence:

        if not closes or len(closes) < 3:
            return self._insufficient_data()

        direction = str(direction).upper()

        # ----------------------------------------------------
        # 1. BOUNDARY FAILURE
        # ----------------------------------------------------

        boundary_failure = self._calculate_boundary_failure(
            closes=closes,
            direction=direction,
            upper_boundary=upper_boundary,
            lower_boundary=lower_boundary,
        )

        # ----------------------------------------------------
        # 2. REJECTION
        # ----------------------------------------------------

        rejection_score = self._calculate_rejection(
            closes=closes,
            highs=highs,
            lows=lows,
            direction=direction,
            upper_boundary=upper_boundary,
            lower_boundary=lower_boundary,
        )

        # ----------------------------------------------------
        # 3. RETURN INSIDE
        # ----------------------------------------------------

        return_inside_score = self._calculate_return_inside(
            closes=closes,
            direction=direction,
            upper_boundary=upper_boundary,
            lower_boundary=lower_boundary,
        )

        # ----------------------------------------------------
        # 4. MOMENTUM FAILURE
        # ----------------------------------------------------

        if momentum_score is None:
            momentum_failure = self._calculate_momentum_failure(
                closes=closes,
                direction=direction,
            )
        else:
            momentum_failure = self._clip(
                100.0 - float(momentum_score)
            )

        # ----------------------------------------------------
        # 5. VOLUME FAILURE
        # ----------------------------------------------------

        volume_failure = self._calculate_volume_failure(
            volumes=volumes
        )

        # ----------------------------------------------------
        # 6. STRUCTURE FAILURE
        # ----------------------------------------------------

        structure_failure = self._clip(
            100.0 - float(structure_score)
        )

        # ----------------------------------------------------
        # 7. CONTINUATION DECAY
        # ----------------------------------------------------

        continuation_decay = self._calculate_continuation_decay(
            continuation_data=continuation_data,
            momentum_failure=momentum_failure,
            volume_failure=volume_failure,
        )

        # ----------------------------------------------------
        # 8. REVERSAL PRESSURE
        # ----------------------------------------------------

        reversal_pressure = self._calculate_reversal_pressure(
            direction=direction,
            boundary_failure=boundary_failure,
            rejection_score=rejection_score,
            return_inside_score=return_inside_score,
            momentum_failure=momentum_failure,
            structure_failure=structure_failure,
        )

        # ----------------------------------------------------
        # 9. TRAP RISK
        # ----------------------------------------------------

        trap_risk = self._calculate_trap_risk(
            boundary_failure=boundary_failure,
            rejection_score=rejection_score,
            return_inside_score=return_inside_score,
            volume_failure=volume_failure,
            continuation_decay=continuation_decay,
        )

        # ----------------------------------------------------
        # 10. FAILURE PROBABILITY
        # ----------------------------------------------------

        failure_probability = self._calculate_failure_probability(
            boundary_failure=boundary_failure,
            rejection_score=rejection_score,
            return_inside_score=return_inside_score,
            continuation_decay=continuation_decay,
            trap_risk=trap_risk,
        )

        # ----------------------------------------------------
        # 11. REVERSAL PROBABILITY
        # ----------------------------------------------------

        reversal_probability = self._calculate_reversal_probability(
            reversal_pressure=reversal_pressure,
            failure_probability=failure_probability,
            momentum_failure=momentum_failure,
            structure_failure=structure_failure,
        )

        # ----------------------------------------------------
        # 12. EVIDENCE QUALITY
        # ----------------------------------------------------

        evidence_quality = self._calculate_evidence_quality(
            boundary_failure=boundary_failure,
            rejection_score=rejection_score,
            return_inside_score=return_inside_score,
            momentum_failure=momentum_failure,
            volume_failure=volume_failure,
            structure_failure=structure_failure,
        )

        # ----------------------------------------------------
        # 13. FAILURE STATE
        # ----------------------------------------------------

        failure_state = self._resolve_failure_state(
            failure_probability=failure_probability,
            trap_risk=trap_risk,
            evidence_quality=evidence_quality,
        )

        # ----------------------------------------------------
        # 14. REVERSAL STATE
        # ----------------------------------------------------

        reversal_state = self._resolve_reversal_state(
            reversal_probability=reversal_probability,
            evidence_quality=evidence_quality,
        )

        # ----------------------------------------------------
        # 15. CONFIDENCE
        # ----------------------------------------------------

        confidence = self._calculate_confidence(
            failure_probability=failure_probability,
            reversal_probability=reversal_probability,
            evidence_quality=evidence_quality,
        )

        evidence = {
            "boundary_failure_score": boundary_failure,
            "rejection_score": rejection_score,
            "return_inside_score": return_inside_score,
            "momentum_failure_score": momentum_failure,
            "volume_failure_score": volume_failure,
            "structure_failure_score": structure_failure,
            "continuation_decay_score": continuation_decay,
            "reversal_pressure_score": reversal_pressure,
            "trap_risk_score": trap_risk,
            "failure_probability": failure_probability,
            "reversal_probability": reversal_probability,

            "formula_status": "PROVISIONAL",
            "boundary_authority": "BoundaryEngine",
            "decision_authority": "D13",
        }

        return FailureReversalIntelligence(
            direction=direction,

            boundary_failure_score=boundary_failure,
            rejection_score=rejection_score,
            return_inside_score=return_inside_score,
            momentum_failure_score=momentum_failure,
            volume_failure_score=volume_failure,
            structure_failure_score=structure_failure,

            continuation_decay_score=continuation_decay,
            reversal_pressure_score=reversal_pressure,
            trap_risk_score=trap_risk,

            failure_probability=failure_probability,
            reversal_probability=reversal_probability,

            failure_state=failure_state,
            reversal_state=reversal_state,

            confidence=confidence,
            evidence_quality=evidence_quality,

            calibration_status=self._calibration_status(
                calibration_model
            ),

            evidence=evidence,
        )

    # ========================================================
    # BOUNDARY FAILURE
    # ========================================================

    def _calculate_boundary_failure(
        self,
        closes: List[float],
        direction: str,
        upper_boundary: Optional[float],
        lower_boundary: Optional[float],
    ) -> float:

        if direction == "BULLISH":

            if upper_boundary is None:
                return 50.0

            outside_count = sum(
                1
                for price in closes[-3:]
                if price > upper_boundary
            )

            inside_count = 3 - outside_count

            return self._clip(
                50.0 + (inside_count - outside_count) * 25.0
            )

        if direction == "BEARISH":

            if lower_boundary is None:
                return 50.0

            outside_count = sum(
                1
                for price in closes[-3:]
                if price < lower_boundary
            )

            inside_count = 3 - outside_count

            return self._clip(
                50.0 + (inside_count - outside_count) * 25.0
            )

        return 50.0

    # ========================================================
    # REJECTION
    # ========================================================

    def _calculate_rejection(
        self,
        closes: List[float],
        highs: Optional[List[float]],
        lows: Optional[List[float]],
        direction: str,
        upper_boundary: Optional[float],
        lower_boundary: Optional[float],
    ) -> float:

        if not highs or not lows:
            return 50.0

        if len(highs) != len(closes) or len(lows) != len(closes):
            return 50.0

        if direction == "BULLISH":

            if upper_boundary is None:
                return 50.0

            wick_rejections = 0

            for high, close in zip(
                highs[-5:],
                closes[-5:]
            ):
                if (
                    high > upper_boundary
                    and close < upper_boundary
                ):
                    wick_rejections += 1

            return self._clip(
                wick_rejections / 5.0 * 100.0
            )

        if direction == "BEARISH":

            if lower_boundary is None:
                return 50.0

            wick_rejections = 0

            for low, close in zip(
                lows[-5:],
                closes[-5:]
            ):
                if (
                    low < lower_boundary
                    and close > lower_boundary
                ):
                    wick_rejections += 1

            return self._clip(
                wick_rejections / 5.0 * 100.0
            )

        return 50.0

    # ========================================================
    # RETURN INSIDE
    # ========================================================

    def _calculate_return_inside(
        self,
        closes: List[float],
        direction: str,
        upper_boundary: Optional[float],
        lower_boundary: Optional[float],
    ) -> float:

        if len(closes) < 2:
            return 50.0

        latest = closes[-1]

        if direction == "BULLISH":

            if upper_boundary is None:
                return 50.0

            if latest < upper_boundary:
                return 100.0

            return 0.0

        if direction == "BEARISH":

            if lower_boundary is None:
                return 50.0

            if latest > lower_boundary:
                return 100.0

            return 0.0

        return 50.0

    # ========================================================
    # MOMENTUM FAILURE
    # ========================================================

    def _calculate_momentum_failure(
        self,
        closes: List[float],
        direction: str,
    ) -> float:

        if len(closes) < 4:
            return 50.0

        changes = []

        for i in range(
            max(1, len(closes) - 4),
            len(closes)
        ):
            previous = closes[i - 1]

            if previous == 0:
                continue

            change = (
                (closes[i] - previous)
                / abs(previous)
            ) * 100.0

            changes.append(change)

        if not changes:
            return 50.0

        if direction == "BULLISH":

            negative = sum(
                1 for value in changes
                if value <= 0
            )

            return self._clip(
                negative / len(changes) * 100.0
            )

        if direction == "BEARISH":

            positive = sum(
                1 for value in changes
                if value >= 0
            )

            return self._clip(
                positive / len(changes) * 100.0
            )

        return 50.0

    # ========================================================
    # VOLUME FAILURE
    # ========================================================

    def _calculate_volume_failure(
        self,
        volumes: Optional[List[float]],
    ) -> float:

        if not volumes or len(volumes) < 3:
            return 50.0

        latest = float(volumes[-1])

        previous = volumes[:-1]

        if not previous:
            return 50.0

        baseline = sum(previous) / len(previous)

        if baseline <= 0:
            return 50.0

        ratio = latest / baseline

        if ratio >= 1.0:
            return self._clip(
                50.0 - (ratio - 1.0) * 100.0
            )

        return self._clip(
            50.0 + (1.0 - ratio) * 100.0
        )

    # ========================================================
    # CONTINUATION DECAY
    # ========================================================

    def _calculate_continuation_decay(
        self,
        continuation_data: Optional[Any],
        momentum_failure: float,
        volume_failure: float,
    ) -> float:

        if continuation_data is not None:

            score = getattr(
                continuation_data,
                "continuation_score",
                None
            )

            if score is not None:

                score = self._clip(score)

                model_decay = 100.0 - score

                return self._clip(
                    model_decay * 0.70
                    + momentum_failure * 0.15
                    + volume_failure * 0.15
                )

        return self._clip(
            momentum_failure * 0.50
            + volume_failure * 0.50
        )

    # ========================================================
    # REVERSAL PRESSURE
    # ========================================================

    def _calculate_reversal_pressure(
        self,
        direction: str,
        boundary_failure: float,
        rejection_score: float,
        return_inside_score: float,
        momentum_failure: float,
        structure_failure: float,
    ) -> float:

        # Failure evidence is directional-agnostic.
        # D13 decides what action follows.

        pressure = (
            boundary_failure * 0.20
            + rejection_score * 0.20
            + return_inside_score * 0.20
            + momentum_failure * 0.20
            + structure_failure * 0.20
        )

        return self._clip(pressure)

    # ========================================================
    # TRAP RISK
    # ========================================================

    def _calculate_trap_risk(
        self,
        boundary_failure: float,
        rejection_score: float,
        return_inside_score: float,
        volume_failure: float,
        continuation_decay: float,
    ) -> float:

        trap_risk = (
            boundary_failure * 0.25
            + rejection_score * 0.25
            + return_inside_score * 0.20
            + volume_failure * 0.15
            + continuation_decay * 0.15
        )

        return self._clip(trap_risk)

    # ========================================================
    # FAILURE PROBABILITY
    # ========================================================

    def _calculate_failure_probability(
        self,
        boundary_failure: float,
        rejection_score: float,
        return_inside_score: float,
        continuation_decay: float,
        trap_risk: float,
    ) -> float:

        probability = (
            boundary_failure * 0.25
            + rejection_score * 0.20
            + return_inside_score * 0.20
            + continuation_decay * 0.15
            + trap_risk * 0.20
        )

        return self._clip(probability)

    # ========================================================
    # REVERSAL PROBABILITY
    # ========================================================

    def _calculate_reversal_probability(
        self,
        reversal_pressure: float,
        failure_probability: float,
        momentum_failure: float,
        structure_failure: float,
    ) -> float:

        probability = (
            reversal_pressure * 0.40
            + failure_probability * 0.30
            + momentum_failure * 0.15
            + structure_failure * 0.15
        )

        return self._clip(probability)

    # ========================================================
    # EVIDENCE QUALITY
    # ========================================================

    def _calculate_evidence_quality(
        self,
        boundary_failure: float,
        rejection_score: float,
        return_inside_score: float,
        momentum_failure: float,
        volume_failure: float,
        structure_failure: float,
    ) -> float:

        values = [
            boundary_failure,
            rejection_score,
            return_inside_score,
            momentum_failure,
            volume_failure,
            structure_failure,
        ]

        # Magnitude of failure evidence
    # ========================================================
    # RETURN INSIDE RISK
    # ========================================================

    def _calculate_return_inside_risk(
        self,
        closes: List[float],
        direction: str,
        upper_boundary: Optional[float],
        lower_boundary: Optional[float],
    ) -> float:

        if len(closes) < 2:
            return 50.0

        latest = float(closes[-1])
        previous = float(closes[-2])

        # ----------------------------------------------------
        # BULLISH
        # ----------------------------------------------------

        if direction == "BULLISH":

            if upper_boundary is None:
                return 50.0

            if latest < upper_boundary:
                return 85.0

            if (
                previous >= upper_boundary
                and latest >= upper_boundary
            ):
                return 15.0

            return 50.0

        # ----------------------------------------------------
        # BEARISH
        # ----------------------------------------------------

        if direction == "BEARISH":

            if lower_boundary is None:
                return 50.0

            if latest > lower_boundary:
                return 85.0

            if (
                previous <= lower_boundary
                and latest <= lower_boundary
            ):
                return 15.0

            return 50.0

        return 50.0


    # ========================================================
    # REJECTION RISK
    # ========================================================

    def _calculate_rejection_risk(
        self,
        closes: List[float],
        highs: Optional[List[float]],
        lows: Optional[List[float]],
        direction: str,
        upper_boundary: Optional[float],
        lower_boundary: Optional[float],
    ) -> float:

        if not highs or not lows:
            return 50.0

        if len(highs) < 2 or len(lows) < 2:
            return 50.0

        latest_close = float(closes[-1])
        latest_high = float(highs[-1])
        latest_low = float(lows[-1])

        # ----------------------------------------------------
        # BULLISH REJECTION
        # ----------------------------------------------------

        if direction == "BULLISH":

            if upper_boundary is None:
                return 50.0

            # Price moved above boundary
            # but closed back below it.
            if (
                latest_high > upper_boundary
                and latest_close < upper_boundary
            ):
                return 90.0

            if latest_high > upper_boundary:
                return 45.0

            return 25.0

        # ----------------------------------------------------
        # BEARISH REJECTION
        # ----------------------------------------------------

        if direction == "BEARISH":

            if lower_boundary is None:
                return 50.0

            # Price moved below boundary
            # but closed back above it.
            if (
                latest_low < lower_boundary
                and latest_close > lower_boundary
            ):
                return 90.0

            if latest_low < lower_boundary:
                return 45.0

            return 25.0

        return 50.0


    # ========================================================
    # EXHAUSTION RISK
    # ========================================================

    def _calculate_exhaustion_risk(
        self,
        closes: List[float],
        direction: str,
    ) -> float:

        if len(closes) < 4:
            return 50.0

        p1 = float(closes[-4])
        p2 = float(closes[-3])
        p3 = float(closes[-2])
        p4 = float(closes[-1])

        if p1 == 0:
            return 50.0

        total_move = (
            (p4 - p1)
            / abs(p1)
        ) * 100.0

        # Small movement does not provide
        # strong exhaustion evidence.
        if abs(total_move) < self.exhaustion_move_threshold:
            return 25.0

        move_1 = abs(p2 - p1)
        move_2 = abs(p3 - p2)
        move_3 = abs(p4 - p3)

        # ----------------------------------------------------
        # Decelerating movement
        # ----------------------------------------------------

        if move_3 < move_2 < move_1:
            return 75.0

        if move_3 < move_2:
            return 60.0

        return 40.0


    # ========================================================
    # CONTINUATION RISK
    # ========================================================

    def _calculate_continuation_risk(
        self,
        price_stability: float,
        volume_stability: float,
        momentum_stability: float,
        structure_stability: float,
    ) -> float:

        stability = (
            price_stability * 0.35
            + volume_stability * 0.15
            + momentum_stability * 0.25
            + structure_stability * 0.25
        )

        return self._clip(
            100.0 - stability
        )


    # ========================================================
    # FAILURE RISK
    # ========================================================

    def _calculate_failure_risk(
        self,
        return_inside_risk: float,
        rejection_risk: float,
        exhaustion_risk: float,
        continuation_risk: float,
    ) -> float:

        failure = (
            return_inside_risk * 0.35
            + rejection_risk * 0.30
            + exhaustion_risk * 0.15
            + continuation_risk * 0.20
        )

        return self._clip(failure)


    # ========================================================
    # EVIDENCE QUALITY
    # ========================================================

    def _calculate_evidence_quality(
        self,
        price: float,
        volume: float,
        momentum: float,
        structure: float,
        return_inside_risk: float,
        rejection_risk: float,
    ) -> float:

        risk_quality = (
            (100.0 - return_inside_risk) * 0.50
            + (100.0 - rejection_risk) * 0.50
        )

        quality = (
            price * 0.20
            + volume * 0.15
            + momentum * 0.15
            + structure * 0.20
            + risk_quality * 0.30
        )

        return self._clip(quality)


    # ========================================================
    # CONFIRMATION STATE
    # ========================================================

    def _resolve_state(
        self,
        failure_risk: float,
        rejection_risk: float,
        confirmation_stability: float,
        risk_adjusted_confirmation: float,
        evidence_quality: float,
    ) -> str:

        if evidence_quality < self.minimum_evidence_quality:
            return "INSUFFICIENT_EVIDENCE"

        if rejection_risk >= self.high_rejection_threshold:
            return "REJECTION_RISK"

        if failure_risk >= self.high_failure_threshold:
            return "BREAKOUT_FAILURE_RISK"

        if (
            confirmation_stability >= self.minimum_stability
            and risk_adjusted_confirmation >= 60.0
        ):
            return "STABLE_CONTINUATION"

        if confirmation_stability >= 45.0:
            return "CONTINUATION_WEAKENING"

        return "UNSTABLE_CONFIRMATION"


    # ========================================================
    # CONFIDENCE
    # ========================================================

    def _calculate_confidence(
        self,
        confirmation_stability: float,
        evidence_quality: float,
        failure_risk: float,
    ) -> float:

        confidence = (
            confirmation_stability * 0.45
            + evidence_quality * 0.35
            + (100.0 - failure_risk) * 0.20
        )

        return self._clip(confidence)


    # ========================================================
    # CALIBRATION
    # ========================================================

    def _apply_calibration(
        self,
        raw_probability: float,
        calibration_model: Optional[Any],
    ) -> float:

        if calibration_model is None:
            return self._clip(raw_probability)

        try:

            if hasattr(
                calibration_model,
                "predict_proba"
            ):

                calibrated = (
                    calibration_model.predict_proba(
                        [[raw_probability]]
                    )
                )

                value = float(
                    calibrated[0][-1]
                )

                return self._clip(
                    value * 100.0
                )

            if callable(calibration_model):

                value = float(
                    calibration_model(
                        raw_probability
                    )
                )

                return self._clip(value)

        except Exception:
            pass

        return self._clip(raw_probability)


    # ========================================================
    # CALIBRATION STATUS
    # ========================================================

    def _calibration_status(
        self,
        calibration_model: Optional[Any],
    ) -> str:

        if calibration_model is None:
            return "UNCALIBRATED"

        if (
            hasattr(
                calibration_model,
                "predict_proba"
            )
            or callable(calibration_model)
        ):
            return "HISTORICAL_MODEL"

        return "UNCALIBRATED"


    # ========================================================
    # INSUFFICIENT DATA
    # ========================================================

    def _insufficient_data(
        self,
    ) -> ConfirmationRiskIntelligence:

        return ConfirmationRiskIntelligence(
            direction="UNKNOWN",

            failure_risk=100.0,
            rejection_risk=100.0,
            return_inside_risk=100.0,
            exhaustion_risk=100.0,
            continuation_risk=100.0,

            price_stability_score=0.0,
            volume_stability_score=0.0,
            momentum_stability_score=0.0,
            structure_stability_score=0.0,

            confirmation_stability=0.0,
            risk_adjusted_confirmation_score=0.0,

            failure_probability=100.0,
            continuation_probability=0.0,

            confirmation_state="INSUFFICIENT_DATA",
            confidence=0.0,
            evidence_quality=0.0,

            calibration_status="UNCALIBRATED",

            evidence={
                "formula_status": "PROVISIONAL",
                "boundary_authority": "BoundaryEngine",
                "decision_authority": "D13",
            },
        )


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
        except (TypeError, ValueError):
            return lower

        return max(
            lower,
            min(upper, value)
        )