from dataclasses import dataclass, field
from typing import Dict, Any


# ==========================================================
# BREAKOUT ENGINE PART-1
# Foundation Intelligence Layer
# ==========================================================


@dataclass
class BreakoutIntelligence:

    breakout_readiness: float

    compression_score: float
    pressure_score: float
    energy_score: float

    bullish_probability: float
    bearish_probability: float

    direction_bias: str
    confidence: float

    upper_boundary: float
    lower_boundary: float

    evidence: Dict[str, Any] = field(default_factory=dict)


class BreakoutEngine:

    def evaluate(
        self,
        structure_data,
        accumulation_data,
        distribution_data,
        boundary_data
    ) -> BreakoutIntelligence:

        compression_score = self._calculate_compression(
            structure_data
        )

        pressure_score = self._calculate_pressure(
            accumulation_data,
            distribution_data
        )

        energy_score = self._calculate_energy(
            compression_score,
            pressure_score
        )

        breakout_readiness = (
            compression_score * 0.40 +
            pressure_score * 0.40 +
            energy_score * 0.20
        )

        bullish_probability = max(
            0.0,
            min(
                100.0,
                pressure_score
            )
        )

        bearish_probability = max(
            0.0,
            100.0 - bullish_probability
        )

        direction_bias = (
            "BULLISH"
            if bullish_probability >= bearish_probability
            else "BEARISH"
        )

        confidence = max(
            bullish_probability,
            bearish_probability
        )

        evidence = {
            "compression_score": compression_score,
            "pressure_score": pressure_score,
            "energy_score": energy_score
        }

        return BreakoutIntelligence(
            breakout_readiness=round(
                breakout_readiness, 2
            ),

            compression_score=round(
                compression_score, 2
            ),

            pressure_score=round(
                pressure_score, 2
            ),

            energy_score=round(
                energy_score, 2
            ),

            bullish_probability=round(
                bullish_probability, 2
            ),

            bearish_probability=round(
                bearish_probability, 2
            ),

            direction_bias=direction_bias,

            confidence=round(
                confidence, 2
            ),

            upper_boundary=boundary_data.upper_boundary,

            lower_boundary=boundary_data.lower_boundary,

            evidence=evidence
        )

    # ======================================================
    # Compression Intelligence
    # ======================================================

    def _calculate_compression(
        self,
        structure_data
    ) -> float:

        consolidation_score = getattr(
            structure_data,
            "consolidation_score",
            50.0
        )

        return max(
            0.0,
            min(
                100.0,
                consolidation_score
            )
        )

    # ======================================================
    # Pressure Intelligence
    # ======================================================

    def _calculate_pressure(
        self,
        accumulation_data,
        distribution_data
    ) -> float:

        accumulation_score = getattr(
            accumulation_data,
            "score",
            50.0
        )

        distribution_score = getattr(
            distribution_data,
            "score",
            50.0
        )

        pressure = (
            accumulation_score -
            distribution_score
        )

        normalized_pressure = (
            50.0 + pressure
        )

        return max(
            0.0,
            min(
                100.0,
                normalized_pressure
            )
        )

    # ======================================================
    # Energy Intelligence
    # ======================================================

    def _calculate_energy(
        self,
        compression_score,
        pressure_score
    ) -> float:

        return (
            compression_score * 0.50 +
            pressure_score * 0.50
        )
# ==========================================================
# BREAKOUT ENGINE PART-2
# Boundary Attack Intelligence Layer
# ==========================================================

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Sequence


# ==========================================================
# PART-2 OUTPUT CONTRACT
# ==========================================================

@dataclass
class BoundaryAttackIntelligence:

    upper_attack_score: float
    lower_attack_score: float

    attack_frequency: float
    attack_persistence: float

    rejection_strength: float
    boundary_weakening_index: float

    attack_dominance: float

    attack_direction: str
    confidence: float

    evidence: Dict[str, Any] = field(default_factory=dict)


# ==========================================================
# BREAKOUT ENGINE
# ==========================================================

class BreakoutEngine:

    def __init__(self, tolerance: float = 0.0025):
        """
        tolerance:
            Relative price distance used to determine whether
            price is sufficiently close to a boundary.

        Example:
            tolerance = 0.0025
            means approximately 0.25%.
        """

        self.tolerance = max(0.0, float(tolerance))

    # ======================================================
    # PART-2 MAIN EVALUATOR
    # ======================================================

    def evaluate_boundary_attack(
        self,
        prices: Sequence[float],
        upper_boundary: float,
        lower_boundary: float,
        *,
        highs: Optional[Sequence[float]] = None,
        lows: Optional[Sequence[float]] = None,
        accumulation_score: float = 50.0,
        distribution_score: float = 50.0,
    ) -> BoundaryAttackIntelligence:

        prices = self._clean_series(prices)

        if not prices:
            return self._empty_result(
                upper_boundary,
                lower_boundary
            )

        highs = (
            self._clean_series(highs)
            if highs is not None
            else prices
        )

        lows = (
            self._clean_series(lows)
            if lows is not None
            else prices
        )

        upper_boundary = self._safe_float(
            upper_boundary
        )

        lower_boundary = self._safe_float(
            lower_boundary
        )

        if upper_boundary <= lower_boundary:
            return self._empty_result(
                upper_boundary,
                lower_boundary
            )

        upper_attacks = self._detect_upper_attacks(
            highs,
            upper_boundary
        )

        lower_attacks = self._detect_lower_attacks(
            lows,
            lower_boundary
        )

        upper_attack_score = self._attack_score(
            upper_attacks,
            len(highs)
        )

        lower_attack_score = self._attack_score(
            lower_attacks,
            len(lows)
        )

        attack_frequency = self._frequency_score(
            upper_attacks,
            lower_attacks,
            len(prices)
        )

        attack_persistence = self._persistence_score(
            upper_attacks,
            lower_attacks
        )

        rejection_strength = self._rejection_strength(
            prices,
            highs,
            lows,
            upper_boundary,
            lower_boundary,
            upper_attacks,
            lower_attacks
        )

        boundary_weakening_index = (
            self._boundary_weakening(
                upper_attacks,
                lower_attacks,
                upper_boundary,
                lower_boundary
            )
        )

        attack_dominance = (
            upper_attack_score -
            lower_attack_score
        )

        attack_direction = self._direction(
            attack_dominance
        )

        confidence = abs(attack_dominance)

        # ----------------------------------------------
        # Evidence Contract
        # ----------------------------------------------

        evidence = {
            "upper_attack_count": len(upper_attacks),
            "lower_attack_count": len(lower_attacks),

            "upper_attack_indices": upper_attacks,
            "lower_attack_indices": lower_attacks,

            "upper_boundary": upper_boundary,
            "lower_boundary": lower_boundary,

            "accumulation_score": accumulation_score,
            "distribution_score": distribution_score,

            "boundary_attack_layer": "PART-2"
        }

        return BoundaryAttackIntelligence(
            upper_attack_score=round(
                upper_attack_score, 2
            ),

            lower_attack_score=round(
                lower_attack_score, 2
            ),

            attack_frequency=round(
                attack_frequency, 2
            ),

            attack_persistence=round(
                attack_persistence, 2
            ),

            rejection_strength=round(
                rejection_strength, 2
            ),

            boundary_weakening_index=round(
                boundary_weakening_index, 2
            ),

            attack_dominance=round(
                attack_dominance, 2
            ),

            attack_direction=attack_direction,

            confidence=round(
                confidence, 2
            ),

            evidence=evidence
        )

    # ======================================================
    # UPPER BOUNDARY ATTACK DETECTION
    # ======================================================

    def _detect_upper_attacks(
        self,
        highs: Sequence[float],
        boundary: float
    ) -> list:

        attacks = []

        for index, high in enumerate(highs):

            if boundary <= 0:
                continue

            distance = abs(
                boundary - high
            ) / boundary

            if distance <= self.tolerance:
                attacks.append(index)

        return attacks

    # ======================================================
    # LOWER BOUNDARY ATTACK DETECTION
    # ======================================================

    def _detect_lower_attacks(
        self,
        lows: Sequence[float],
        boundary: float
    ) -> list:

        attacks = []

        for index, low in enumerate(lows):

            if boundary <= 0:
                continue

            distance = abs(
                low - boundary
            ) / boundary

            if distance <= self.tolerance:
                attacks.append(index)

        return attacks

    # ======================================================
    # ATTACK SCORE
    # ======================================================

    def _attack_score(
        self,
        attacks: Sequence[int],
        total_periods: int
    ) -> float:

        if total_periods <= 0:
            return 0.0

        frequency = (
            len(attacks) /
            total_periods
        )

        return self._clamp(
            frequency * 100.0,
            0.0,
            100.0
        )

    # ======================================================
    # ATTACK FREQUENCY
    # ======================================================

    def _frequency_score(
        self,
        upper_attacks: Sequence[int],
        lower_attacks: Sequence[int],
        total_periods: int
    ) -> float:

        if total_periods <= 0:
            return 0.0

        total_attacks = (
            len(upper_attacks) +
            len(lower_attacks)
        )

        frequency = (
            total_attacks /
            total_periods
        )

        return self._clamp(
            frequency * 100.0,
            0.0,
            100.0
        )

    # ======================================================
    # ATTACK PERSISTENCE
    # ======================================================

    def _persistence_score(
        self,
        upper_attacks: Sequence[int],
        lower_attacks: Sequence[int]
    ) -> float:

        all_attacks = sorted(
            list(upper_attacks) +
            list(lower_attacks)
        )

        if len(all_attacks) < 2:
            return 0.0

        consecutive_links = 0

        for previous, current in zip(
            all_attacks,
            all_attacks[1:]
        ):

            if current - previous <= 2:
                consecutive_links += 1

        persistence = (
            consecutive_links /
            max(1, len(all_attacks) - 1)
        )

        return self._clamp(
            persistence * 100.0,
            0.0,
            100.0
        )

    # ======================================================
    # REJECTION STRENGTH
    # ======================================================

    def _rejection_strength(
        self,
        prices,
        highs,
        lows,
        upper_boundary,
        lower_boundary,
        upper_attacks,
        lower_attacks
    ) -> float:

        rejection_values = []

        for index in upper_attacks:

            if index >= len(prices):
                continue

            rejection = max(
                0.0,
                (
                    upper_boundary -
                    prices[index]
                ) / upper_boundary
            )

            rejection_values.append(
                rejection
            )

        for index in lower_attacks:

            if index >= len(prices):
                continue

            rejection = max(
                0.0,
                (
                    prices[index] -
                    lower_boundary
                ) / lower_boundary
            )

            rejection_values.append(
                rejection
            )

        if not rejection_values:
            return 0.0

        average_rejection = (
            sum(rejection_values) /
            len(rejection_values)
        )

        return self._clamp(
            average_rejection * 10000.0,
            0.0,
            100.0
        )

    # ======================================================
    # BOUNDARY WEAKENING INDEX
    # ======================================================

    def _boundary_weakening(
        self,
        upper_attacks,
        lower_attacks,
        upper_boundary,
        lower_boundary
    ) -> float:

        all_attacks = sorted(
            list(upper_attacks) +
            list(lower_attacks)
        )

        if len(all_attacks) < 2:
            return 0.0

        # Repeated attacks indicate increasing interaction
        # with the boundary. This is only a structural
        # weakening proxy; Part-3 will introduce
        # participation/liquidity confirmation.

        attack_density = (
            len(all_attacks) /
            max(1, all_attacks[-1] - all_attacks[0] + 1)
        )

        return self._clamp(
            attack_density * 100.0,
            0.0,
            100.0
        )

    # ======================================================
    # ATTACK DIRECTION
    # ======================================================

    def _direction(
        self,
        dominance: float
    ) -> str:

        if dominance > 5.0:
            return "UPPER_ATTACK"

        if dominance < -5.0:
            return "LOWER_ATTACK"

        return "BALANCED"

    # ======================================================
    # EMPTY RESULT
    # ======================================================

    def _empty_result(
        self,
        upper_boundary,
        lower_boundary
    ) -> BoundaryAttackIntelligence:

        return BoundaryAttackIntelligence(
            upper_attack_score=0.0,
            lower_attack_score=0.0,

            attack_frequency=0.0,
            attack_persistence=0.0,

            rejection_strength=0.0,
            boundary_weakening_index=0.0,

            attack_dominance=0.0,

            attack_direction="INSUFFICIENT_DATA",
            confidence=0.0,

            evidence={
                "upper_boundary": upper_boundary,
                "lower_boundary": lower_boundary,
                "boundary_attack_layer": "PART-2"
            }
        )

    # ======================================================
    # UTILITIES
    # ======================================================

    @staticmethod
    def _clean_series(
        values
    ) -> list:

        if values is None:
            return []

        cleaned = []

        for value in values:

            try:
                number = float(value)

                if number == number:
                    cleaned.append(number)

            except (TypeError, ValueError):
                continue

        return cleaned

    @staticmethod
    def _safe_float(
        value
    ) -> float:

        try:
            number = float(value)

            if number == number:
                return number

        except (TypeError, ValueError):
            pass

        return 0.0

    @staticmethod
    def _clamp(
        value: float,
        minimum: float,
        maximum: float
    ) -> float:

        return max(
            minimum,
            min(maximum, value)
        )
# ==========================================================
# BREAKOUT ENGINE PART-3
# Participation & Pressure Intelligence Layer
# ==========================================================

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Sequence


# ==========================================================
# PART-3 OUTPUT CONTRACT
# ==========================================================

@dataclass
class ParticipationPressureIntelligence:

    volume_pressure_score: float
    liquidity_pressure_score: float
    participation_score: float

    accumulation_pressure: float
    distribution_pressure: float

    bullish_pressure: float
    bearish_pressure: float

    breakout_fuel_score: float

    volume_expansion_score: float
    pressure_alignment_score: float

    dominant_pressure: str
    confidence: float

    evidence: Dict[str, Any] = field(default_factory=dict)


# ==========================================================
# BREAKOUT ENGINE
# ==========================================================

class BreakoutEngine:

    def __init__(
        self,
        volume_expansion_threshold: float = 1.20,
        minimum_liquidity: float = 0.0
    ):
        self.volume_expansion_threshold = max(
            1.0,
            float(volume_expansion_threshold)
        )

        self.minimum_liquidity = max(
            0.0,
            float(minimum_liquidity)
        )

    # ======================================================
    # PART-3 MAIN EVALUATOR
    # ======================================================

    def evaluate_participation_pressure(
        self,
        volumes: Sequence[float],
        *,
        average_volume: Optional[float] = None,
        liquidity_score: Optional[float] = None,
        participation_score: Optional[float] = None,
        accumulation_score: float = 50.0,
        distribution_score: float = 50.0,
        price_direction_score: float = 50.0,
        oi_pressure_score: Optional[float] = None,
        flow_pressure_score: Optional[float] = None,
    ) -> ParticipationPressureIntelligence:

        clean_volumes = self._clean_series(volumes)

        # --------------------------------------------------
        # 1. Volume Intelligence
        # --------------------------------------------------

        volume_expansion_score = (
            self._calculate_volume_expansion(
                clean_volumes,
                average_volume
            )
        )

        volume_pressure_score = (
            self._calculate_volume_pressure(
                volume_expansion_score
            )
        )

        # --------------------------------------------------
        # 2. Liquidity Intelligence
        # --------------------------------------------------

        liquidity_pressure_score = (
            self._normalize_optional_score(
                liquidity_score,
                default=50.0
            )
        )

        # --------------------------------------------------
        # 3. Participation Intelligence
        # --------------------------------------------------

        participation_score = (
            self._normalize_optional_score(
                participation_score,
                default=50.0
            )
        )

        # --------------------------------------------------
        # 4. Accumulation / Distribution Pressure
        # --------------------------------------------------

        accumulation_pressure = (
            self._normalize_optional_score(
                accumulation_score,
                default=50.0
            )
        )

        distribution_pressure = (
            self._normalize_optional_score(
                distribution_score,
                default=50.0
            )
        )

        # --------------------------------------------------
        # 5. Directional Pressure
        # --------------------------------------------------

        price_direction_score = (
            self._normalize_optional_score(
                price_direction_score,
                default=50.0
            )
        )

        directional_bias = (
            price_direction_score - 50.0
        )

        accumulation_bias = (
            accumulation_pressure -
            distribution_pressure
        )

        oi_bias = 0.0

        if oi_pressure_score is not None:
            oi_bias = (
                self._normalize_optional_score(
                    oi_pressure_score,
                    default=50.0
                ) - 50.0
            )

        flow_bias = 0.0

        if flow_pressure_score is not None:
            flow_bias = (
                self._normalize_optional_score(
                    flow_pressure_score,
                    default=50.0
                ) - 50.0
            )

        # --------------------------------------------------
        # 6. Bullish / Bearish Pressure
        # --------------------------------------------------

        raw_direction_pressure = (
            directional_bias * 0.35 +
            accumulation_bias * 0.35 +
            oi_bias * 0.15 +
            flow_bias * 0.15
        )

        bullish_pressure = self._clamp(
            50.0 + raw_direction_pressure,
            0.0,
            100.0
        )

        bearish_pressure = self._clamp(
            100.0 - bullish_pressure,
            0.0,
            100.0
        )

        # --------------------------------------------------
        # 7. Pressure Alignment
        # --------------------------------------------------

        pressure_alignment_score = (
            self._calculate_alignment(
                bullish_pressure,
                bearish_pressure,
                accumulation_pressure,
                distribution_pressure
            )
        )

        # --------------------------------------------------
        # 8. Breakout Fuel
        # --------------------------------------------------

        breakout_fuel_score = (
            volume_pressure_score * 0.25 +
            liquidity_pressure_score * 0.20 +
            participation_score * 0.20 +
            pressure_alignment_score * 0.20 +
            volume_expansion_score * 0.15
        )

        # --------------------------------------------------
        # 9. Dominant Pressure
        # --------------------------------------------------

        if bullish_pressure > bearish_pressure + 5.0:
            dominant_pressure = "BULLISH"

        elif bearish_pressure > bullish_pressure + 5.0:
            dominant_pressure = "BEARISH"

        else:
            dominant_pressure = "BALANCED"

        confidence = abs(
            bullish_pressure -
            bearish_pressure
        )

        # --------------------------------------------------
        # 10. Evidence Contract
        # --------------------------------------------------

        evidence = {
            "volume_observations": len(clean_volumes),

            "average_volume": average_volume,

            "volume_expansion_threshold":
                self.volume_expansion_threshold,

            "liquidity_input": liquidity_score,

            "participation_input":
                participation_score,

            "accumulation_input":
                accumulation_score,

            "distribution_input":
                distribution_score,

            "oi_pressure_input":
                oi_pressure_score,

            "flow_pressure_input":
                flow_pressure_score,

            "price_direction_input":
                price_direction_score,

            "part": "BREAKOUT_ENGINE_PART_3",

            "purpose":
                "Participation and breakout-fuel intelligence"
        }

        return ParticipationPressureIntelligence(
            volume_pressure_score=round(
                volume_pressure_score,
                2
            ),

            liquidity_pressure_score=round(
                liquidity_pressure_score,
                2
            ),

            participation_score=round(
                participation_score,
                2
            ),

            accumulation_pressure=round(
                accumulation_pressure,
                2
            ),

            distribution_pressure=round(
                distribution_pressure,
                2
            ),

            bullish_pressure=round(
                bullish_pressure,
                2
            ),

            bearish_pressure=round(
                bearish_pressure,
                2
            ),

            breakout_fuel_score=round(
                breakout_fuel_score,
                2
            ),

            volume_expansion_score=round(
                volume_expansion_score,
                2
            ),

            pressure_alignment_score=round(
                pressure_alignment_score,
                2
            ),

            dominant_pressure=dominant_pressure,

            confidence=round(
                confidence,
                2
            ),

            evidence=evidence
        )

    # ======================================================
    # VOLUME EXPANSION
    # ======================================================

    def _calculate_volume_expansion(
        self,
        volumes: Sequence[float],
        average_volume: Optional[float]
    ) -> float:

        if not volumes:
            return 0.0

        latest_volume = volumes[-1]

        if average_volume is None:

            if len(volumes) < 2:
                return 50.0

            baseline = (
                sum(volumes[:-1]) /
                max(1, len(volumes) - 1)
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

        # 1.0x = neutral.
        # Threshold = meaningful expansion.
        if ratio <= 1.0:
            return self._clamp(
                ratio * 50.0,
                0.0,
                50.0
            )

        expansion = (
            ratio /
            self.volume_expansion_threshold
        )

        return self._clamp(
            expansion * 50.0,
            0.0,
            100.0
        )

    # ======================================================
    # VOLUME PRESSURE
    # ======================================================

    def _calculate_volume_pressure(
        self,
        expansion_score: float
    ) -> float:

        return self._clamp(
            expansion_score,
            0.0,
            100.0
        )

    # ======================================================
    # PRESSURE ALIGNMENT
    # ======================================================

    def _calculate_alignment(
        self,
        bullish_pressure: float,
        bearish_pressure: float,
        accumulation_pressure: float,
        distribution_pressure: float
    ) -> float:

        directional_strength = abs(
            bullish_pressure -
            bearish_pressure
        )

        accumulation_strength = abs(
            accumulation_pressure -
            distribution_pressure
        )

        alignment = (
            directional_strength * 0.50 +
            accumulation_strength * 0.50
        )

        return self._clamp(
            alignment,
            0.0,
            100.0
        )

    # ======================================================
    # NORMALIZATION
    # ======================================================

    @staticmethod
    def _normalize_optional_score(
        value: Optional[float],
        default: float = 50.0
    ) -> float:

        if value is None:
            return default

        try:
            value = float(value)
        except (TypeError, ValueError):
            return default

        if value != value:
            return default

        return max(
            0.0,
            min(
                100.0,
                value
            )
        )

    # ======================================================
    # SERIES CLEANING
    # ======================================================

    @staticmethod
    def _clean_series(
        values
    ) -> list:

        if values is None:
            return []

        result = []

        for value in values:

            try:
                number = float(value)

                if number == number:
                    result.append(number)

            except (TypeError, ValueError):
                continue

        return result

    # ======================================================
    # CLAMP
    # ======================================================

    @staticmethod
    def _clamp(
        value: float,
        minimum: float,
        maximum: float
    ) -> float:

        return max(
            minimum,
            min(
                maximum,
                value
            )
        )
# ==========================================================
# BREAKOUT ENGINE PART-4
# Breakout Probability Intelligence Layer
#
# Consumes:
#   Part-1 Foundation
#   Part-2 Boundary Attack
#   Part-3 Participation / Pressure
#
# Purpose:
#   Estimate directional breakout likelihood from
#   structured evidence.
#
# IMPORTANT:
#   This is NOT a trading signal.
#   Probability calibration must eventually come from
#   historical / forward validation.
# ==========================================================

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


# ==========================================================
# OUTPUT CONTRACT
# ==========================================================

@dataclass
class BreakoutProbabilityIntelligence:

    bullish_probability: float
    bearish_probability: float
    neutral_probability: float

    breakout_probability: float

    probability_confidence: float

    directional_edge: float

    expected_move_score: float

    breakout_direction: str

    readiness_score: float
    evidence_quality: float

    calibration_status: str

    evidence: Dict[str, Any] = field(
        default_factory=dict
    )


# ==========================================================
# BREAKOUT ENGINE
# ==========================================================

class BreakoutEngine:

    def __init__(
        self,
        probability_floor: float = 0.0,
        probability_ceiling: float = 100.0,
    ):
        self.probability_floor = max(
            0.0,
            float(probability_floor)
        )

        self.probability_ceiling = min(
            100.0,
            float(probability_ceiling)
        )

    # ======================================================
    # PART-4 MAIN EVALUATOR
    # ======================================================

    def evaluate_probability(
        self,
        *,
        part1,
        part2,
        part3,
        calibration_model: Optional[Any] = None,
    ) -> BreakoutProbabilityIntelligence:

        # --------------------------------------------------
        # PART-1 FOUNDATION
        # --------------------------------------------------

        readiness = self._get_score(
            part1,
            "breakout_readiness",
            0.0
        )

        compression = self._get_score(
            part1,
            "compression_score",
            0.0
        )

        energy = self._get_score(
            part1,
            "energy_score",
            0.0
        )

        # --------------------------------------------------
        # PART-2 BOUNDARY ATTACK
        # --------------------------------------------------

        upper_attack = self._get_score(
            part2,
            "upper_attack_score",
            0.0
        )

        lower_attack = self._get_score(
            part2,
            "lower_attack_score",
            0.0
        )

        weakening = self._get_score(
            part2,
            "boundary_weakening_index",
            0.0
        )

        persistence = self._get_score(
            part2,
            "attack_persistence",
            0.0
        )

        rejection = self._get_score(
            part2,
            "rejection_strength",
            0.0
        )

        # --------------------------------------------------
        # PART-3 PARTICIPATION
        # --------------------------------------------------

        bullish_pressure = self._get_score(
            part3,
            "bullish_pressure",
            50.0
        )

        bearish_pressure = self._get_score(
            part3,
            "bearish_pressure",
            50.0
        )

        fuel = self._get_score(
            part3,
            "breakout_fuel_score",
            0.0
        )

        volume_expansion = self._get_score(
            part3,
            "volume_expansion_score",
            0.0
        )

        alignment = self._get_score(
            part3,
            "pressure_alignment_score",
            0.0
        )

        # --------------------------------------------------
        # DIRECTIONAL EVIDENCE
        # --------------------------------------------------

        bullish_boundary_edge = (
            upper_attack -
            lower_attack
        )

        pressure_edge = (
            bullish_pressure -
            bearish_pressure
        )

        # Rejection is treated as a friction factor,
        # not direct breakout confirmation.

        effective_bullish_edge = (
            bullish_boundary_edge * 0.35 +
            pressure_edge * 0.40 +
            (
                weakening - 50.0
            ) * 0.15 +
            (
                persistence - 50.0
            ) * 0.10
        )

        # --------------------------------------------------
        # RAW DIRECTION SCORE
        # --------------------------------------------------

        bullish_raw = (
            50.0 +
            effective_bullish_edge
        )

        bearish_raw = (
            50.0 -
            effective_bullish_edge
        )

        bullish_raw = self._clamp(
            bullish_raw,
            self.probability_floor,
            self.probability_ceiling
        )

        bearish_raw = self._clamp(
            bearish_raw,
            self.probability_floor,
            self.probability_ceiling
        )

        # --------------------------------------------------
        # BREAKOUT READINESS
        # --------------------------------------------------

        readiness_score = (
            readiness * 0.40 +
            compression * 0.15 +
            energy * 0.15 +
            fuel * 0.20 +
            weakening * 0.10
        )

        readiness_score = self._clamp(
            readiness_score,
            0.0,
            100.0
        )

        # --------------------------------------------------
        # RAW BREAKOUT PROBABILITY
        #
        # Readiness determines whether a breakout condition
        # exists at all.
        # Directional edge determines which side dominates.
        # --------------------------------------------------

        directional_strength = abs(
            effective_bullish_edge
        )

        raw_breakout_probability = (
            readiness_score * 0.60 +
            directional_strength * 0.40
        )

        raw_breakout_probability = self._clamp(
            raw_breakout_probability,
            0.0,
            100.0
        )

        # --------------------------------------------------
        # OPTIONAL CALIBRATION MODEL
        # --------------------------------------------------

        calibration_status = "UNCALIBRATED"

        if calibration_model is not None:

            calibrated = self._apply_calibration(
                calibration_model,
                raw_breakout_probability,
                readiness_score,
                effective_bullish_edge,
                fuel,
                alignment
            )

            if calibrated is not None:

                raw_breakout_probability = (
                    self._clamp(
                        calibrated,
                        0.0,
                        100.0
                    )
                )

                calibration_status = (
                    "HISTORICAL_MODEL"
                )

        # --------------------------------------------------
        # DIRECTIONAL PROBABILITIES
        # --------------------------------------------------

        if effective_bullish_edge > 0:

            bullish_share = (
                50.0 +
                min(
                    50.0,
                    directional_strength
                )
            )

            bearish_share = (
                100.0 -
                bullish_share
            )

        elif effective_bullish_edge < 0:

            bearish_share = (
                50.0 +
                min(
                    50.0,
                    directional_strength
                )
            )

            bullish_share = (
                100.0 -
                bearish_share
            )

        else:

            bullish_share = 50.0
            bearish_share = 50.0

        # --------------------------------------------------
        # APPLY BREAKOUT READINESS
        # --------------------------------------------------

        bullish_probability = (
            raw_breakout_probability *
            bullish_share /
            100.0
        )

        bearish_probability = (
            raw_breakout_probability *
            bearish_share /
            100.0
        )

        neutral_probability = max(
            0.0,
            100.0 -
            bullish_probability -
            bearish_probability
        )

        # --------------------------------------------------
        # BREAKOUT DIRECTION
        # --------------------------------------------------

        if raw_breakout_probability < 50.0:

            breakout_direction = "NO_CLEAR_BREAKOUT"

        elif bullish_probability > bearish_probability:

            breakout_direction = "BULLISH"

        elif bearish_probability > bullish_probability:

            breakout_direction = "BEARISH"

        else:

            breakout_direction = "BALANCED"

        # --------------------------------------------------
        # DIRECTIONAL EDGE
        # --------------------------------------------------

        directional_edge = abs(
            bullish_probability -
            bearish_probability
        )

        # --------------------------------------------------
        # EXPECTED MOVE SCORE
        #
        # This is NOT a price target.
        # It represents structural expansion potential.
        # --------------------------------------------------

        expected_move_score = (
            compression * 0.25 +
            energy * 0.20 +
            fuel * 0.25 +
            weakening * 0.15 +
            persistence * 0.15
        )

        expected_move_score = self._clamp(
            expected_move_score,
            0.0,
            100.0
        )

        # --------------------------------------------------
        # EVIDENCE QUALITY
        # --------------------------------------------------

        evidence_quality = (
            compression * 0.15 +
            weakening * 0.15 +
            persistence * 0.15 +
            fuel * 0.20 +
            volume_expansion * 0.10 +
            alignment * 0.15 +
            energy * 0.10
        )

        evidence_quality = self._clamp(
            evidence_quality,
            0.0,
            100.0
        )

        # --------------------------------------------------
        # PROBABILITY CONFIDENCE
        # --------------------------------------------------

        probability_confidence = (
            evidence_quality * 0.60 +
            directional_edge * 0.40
        )

        probability_confidence = self._clamp(
            probability_confidence,
            0.0,
            100.0
        )

        # --------------------------------------------------
        # EVIDENCE TRACE
        # --------------------------------------------------

        evidence = {

            "part_1": {
                "readiness": readiness,
                "compression": compression,
                "energy": energy,
            },

            "part_2": {
                "upper_attack": upper_attack,
                "lower_attack": lower_attack,
                "weakening": weakening,
                "persistence": persistence,
                "rejection": rejection,
            },

            "part_3": {
                "bullish_pressure":
                    bullish_pressure,

                "bearish_pressure":
                    bearish_pressure,

                "fuel": fuel,

                "volume_expansion":
                    volume_expansion,

                "alignment":
                    alignment,
            },

            "derived": {

                "effective_bullish_edge":
                    effective_bullish_edge,

                "directional_strength":
                    directional_strength,

                "readiness_score":
                    readiness_score,

                "raw_breakout_probability":
                    raw_breakout_probability,
            },

            "calibration_status":
                calibration_status,

            "part":
                "BREAKOUT_ENGINE_PART_4",

            "purpose":
                "Directional breakout probability intelligence",
        }

        return BreakoutProbabilityIntelligence(

            bullish_probability=round(
                bullish_probability,
                2
            ),

            bearish_probability=round(
                bearish_probability,
                2
            ),

            neutral_probability=round(
                neutral_probability,
                2
            ),

            breakout_probability=round(
                raw_breakout_probability,
                2
            ),

            probability_confidence=round(
                probability_confidence,
                2
            ),

            directional_edge=round(
                directional_edge,
                2
            ),

            expected_move_score=round(
                expected_move_score,
                2
            ),

            breakout_direction=
                breakout_direction,

            readiness_score=round(
                readiness_score,
                2
            ),

            evidence_quality=round(
                evidence_quality,
                2
            ),

            calibration_status=
                calibration_status,

            evidence=evidence,
        )

    # ======================================================
    # CALIBRATION HOOK
    # ======================================================

    @staticmethod
    def _apply_calibration(
        model,
        raw_probability,
        readiness,
        directional_edge,
        fuel,
        alignment
    ):

        features = {
            "raw_probability":
                raw_probability,

            "readiness":
                readiness,

            "directional_edge":
                directional_edge,

            "fuel":
                fuel,

            "alignment":
                alignment,
        }

        try:

            if hasattr(
                model,
                "predict_proba"
            ):

                result = model.predict_proba(
                    [features]
                )

                return float(
                    result[0][1] * 100.0
                )

            if callable(model):

                return float(
                    model(features)
                )

        except Exception:
            return None

        return None

    # ======================================================
    # SCORE EXTRACTION
    # ======================================================

    @staticmethod
    def _get_score(
        source,
        attribute,
        default
    ):

        if source is None:
            return default

        try:

            if isinstance(
                source,
                dict
            ):
                value = source.get(
                    attribute,
                    default
                )

            else:
                value = getattr(
                    source,
                    attribute,
                    default
                )

            value = float(value)

            if value != value:
                return default

            return max(
                0.0,
                min(
                    100.0,
                    value
                )
            )

        except (
            TypeError,
            ValueError
        ):
            return default

    # ======================================================
    # CLAMP
    # ======================================================

    @staticmethod
    def _clamp(
        value,
        minimum,
        maximum
    ):

        return max(
            minimum,
            min(
                maximum,
                value
            )
        )
```python
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class BreakoutOpportunityIntelligence:
    # False-breakout / failure intelligence
    false_breakout_risk: float
    trap_probability: float
    failure_probability: float

    # Post-breakout survivability
    retest_survivability: float
    continuation_strength: float

    # Opportunity quality
    risk_adjusted_breakout_score: float
    profit_conversion_score: float
    opportunity_grade: str
    opportunity_rank_score: float

    # Directional context
    breakout_direction: str
    opportunity_direction: str

    # Confidence / evidence
    confidence: float
    evidence_quality: float

    # Important architectural status
    calibration_status: str

    evidence: Dict[str, Any] = field(default_factory=dict)


class BreakoutEngine:
    """
    Breakout Engine - Part 5

    False Breakout & Opportunity Intelligence

    Role:
        Evaluate whether a detected breakout opportunity has:
        - excessive false-breakout risk
        - trap/failure characteristics
        - weak or strong retest survivability
        - continuation potential
        - useful risk-adjusted opportunity quality

    IMPORTANT:
        This engine does NOT make final BUY/SELL decisions.
        D13 remains the final decision authority.

        Scores below are structural/evidence proxies until
        validated research formulas and historical calibration
        are connected through the Formula Registry.
    """

    def __init__(
        self,
        probability_floor: float = 0.0,
        probability_ceiling: float = 100.0,
    ):
        self.probability_floor = probability_floor
        self.probability_ceiling = probability_ceiling

    # ============================================================
    # PART 5 MAIN EVALUATION
    # ============================================================

    def evaluate_opportunity(
        self,
        part1,
        part2,
        part3,
        part4,
        retest_score: Optional[float] = None,
        continuation_score: Optional[float] = None,
        risk_score: Optional[float] = None,
        calibration_model=None,
    ) -> BreakoutOpportunityIntelligence:

        # --------------------------------------------------------
        # Extract Part-1
        # --------------------------------------------------------

        readiness = self._safe_score(
            getattr(part1, "breakout_readiness", 50.0)
        )

        compression = self._safe_score(
            getattr(part1, "compression_score", 50.0)
        )

        energy = self._safe_score(
            getattr(part1, "energy_score", 50.0)
        )

        # --------------------------------------------------------
        # Extract Part-2
        # --------------------------------------------------------

        upper_attack = self._safe_score(
            getattr(part2, "upper_attack_score", 50.0)
        )

        lower_attack = self._safe_score(
            getattr(part2, "lower_attack_score", 50.0)
        )

        weakening = self._safe_score(
            getattr(part2, "boundary_weakening_index", 50.0)
        )

        persistence = self._safe_score(
            getattr(part2, "attack_persistence", 50.0)
        )

        rejection = self._safe_score(
            getattr(part2, "rejection_strength", 50.0)
        )

        attack_direction = getattr(
            part2,
            "attack_direction",
            "BALANCED",
        )

        # --------------------------------------------------------
        # Extract Part-3
        # --------------------------------------------------------

        bullish_pressure = self._safe_score(
            getattr(part3, "bullish_pressure", 50.0)
        )

        bearish_pressure = self._safe_score(
            getattr(part3, "bearish_pressure", 50.0)
        )

        fuel = self._safe_score(
            getattr(part3, "breakout_fuel_score", 50.0)
        )

        volume_expansion = self._safe_score(
            getattr(part3, "volume_expansion_score", 50.0)
        )

        pressure_alignment = self._safe_score(
            getattr(part3, "pressure_alignment_score", 50.0)
        )

        # --------------------------------------------------------
        # Extract Part-4
        # --------------------------------------------------------

        bullish_probability = self._safe_score(
            getattr(part4, "bullish_probability", 33.33)
        )

        bearish_probability = self._safe_score(
            getattr(part4, "bearish_probability", 33.33)
        )

        neutral_probability = self._safe_score(
            getattr(part4, "neutral_probability", 33.33)
        )

        breakout_probability = self._safe_score(
            getattr(part4, "breakout_probability", 50.0)
        )

        directional_edge = self._safe_score(
            getattr(part4, "directional_edge", 50.0)
        )

        expected_move = self._safe_score(
            getattr(part4, "expected_move_score", 50.0)
        )

        breakout_direction = getattr(
            part4,
            "breakout_direction",
            "NO_CLEAR_BREAKOUT",
        )

        evidence_quality_part4 = self._safe_score(
            getattr(part4, "evidence_quality", 50.0)
        )

        # ========================================================
        # 1. FALSE BREAKOUT RISK
        # ========================================================

        false_breakout_risk = self._calculate_false_breakout_risk(
            breakout_probability=breakout_probability,
            fuel=fuel,
            volume_expansion=volume_expansion,
            pressure_alignment=pressure_alignment,
            rejection=rejection,
            persistence=persistence,
            weakening=weakening,
            readiness=readiness,
            neutral_probability=neutral_probability,
        )

        # ========================================================
        # 2. TRAP PROBABILITY
        # ========================================================

        trap_probability = self._calculate_trap_probability(
            false_breakout_risk=false_breakout_risk,
            rejection=rejection,
            pressure_alignment=pressure_alignment,
            volume_expansion=volume_expansion,
            persistence=persistence,
            fuel=fuel,
            directional_edge=directional_edge,
        )

        # ========================================================
        # 3. FAILURE PROBABILITY
        # ========================================================

        failure_probability = self._calculate_failure_probability(
            false_breakout_risk=false_breakout_risk,
            trap_probability=trap_probability,
            readiness=readiness,
            fuel=fuel,
            pressure_alignment=pressure_alignment,
            weakening=weakening,
        )

        # ========================================================
        # 4. RETEST SURVIVABILITY
        # ========================================================

        if retest_score is not None:
            retest_survivability = self._safe_score(retest_score)
        else:
            retest_survivability = self._estimate_retest_survivability(
                weakening=weakening,
                persistence=persistence,
                rejection=rejection,
                fuel=fuel,
                pressure_alignment=pressure_alignment,
            )

        # ========================================================
        # 5. CONTINUATION STRENGTH
        # ========================================================

        if continuation_score is not None:
            continuation_strength = self._safe_score(
                continuation_score
            )
        else:
            continuation_strength = self._estimate_continuation_strength(
                readiness=readiness,
                energy=energy,
                fuel=fuel,
                pressure_alignment=pressure_alignment,
                directional_edge=directional_edge,
                expected_move=expected_move,
                retest_survivability=retest_survivability,
            )

        # ========================================================
        # 6. RISK ADJUSTED BREAKOUT SCORE
        # ========================================================

        risk_component = (
            self._safe_score(risk_score)
            if risk_score is not None
            else (100.0 - false_breakout_risk)
        )

        risk_adjusted_breakout_score = self._calculate_risk_adjusted_score(
            breakout_probability=breakout_probability,
            continuation_strength=continuation_strength,
            retest_survivability=retest_survivability,
            risk_component=risk_component,
            trap_probability=trap_probability,
            failure_probability=failure_probability,
        )

        # ========================================================
        # 7. PROFIT CONVERSION SCORE
        # ========================================================

        profit_conversion_score = self._calculate_profit_conversion_score(
            breakout_probability=breakout_probability,
            expected_move=expected_move,
            continuation_strength=continuation_strength,
            retest_survivability=retest_survivability,
            fuel=fuel,
            risk_adjusted_score=risk_adjusted_breakout_score,
            false_breakout_risk=false_breakout_risk,
        )

        # ========================================================
        # 8. EVIDENCE QUALITY
        # ========================================================

        evidence_quality = self._calculate_evidence_quality(
            compression=compression,
            readiness=readiness,
            weakening=weakening,
            persistence=persistence,
            fuel=fuel,
            volume_expansion=volume_expansion,
            pressure_alignment=pressure_alignment,
            retest_survivability=retest_survivability,
            continuation_strength=continuation_strength,
        )

        # ========================================================
        # 9. OPPORTUNITY RANK SCORE
        # ========================================================

        opportunity_rank_score = (
            risk_adjusted_breakout_score * 0.45
            + profit_conversion_score * 0.30
            + evidence_quality * 0.25
        )

        opportunity_rank_score = self._clip(
            opportunity_rank_score
        )

        # ========================================================
        # 10. OPPORTUNITY GRADE
        # ========================================================

        opportunity_grade = self._grade_opportunity(
            opportunity_rank_score,
            false_breakout_risk,
            trap_probability,
            evidence_quality,
        )

        # ========================================================
        # 11. OPPORTUNITY DIRECTION
        # ========================================================

        opportunity_direction = self._resolve_direction(
            breakout_direction=breakout_direction,
            attack_direction=attack_direction,
            bullish_probability=bullish_probability,
            bearish_probability=bearish_probability,
            bullish_pressure=bullish_pressure,
            bearish_pressure=bearish_pressure,
        )

        # ========================================================
        # 12. CONFIDENCE
        # ========================================================

        confidence = self._calculate_confidence(
            evidence_quality=evidence_quality,
            directional_edge=directional_edge,
            breakout_probability=breakout_probability,
            false_breakout_risk=false_breakout_risk,
        )

        # ========================================================
        # 13. CALIBRATION STATUS
        # ========================================================

        calibration_status = "UNCALIBRATED"

        if calibration_model is not None:
            calibration_status = self._apply_calibration_hook(
                calibration_model
            )

        # ========================================================
        # 14. EVIDENCE TRACE
        # ========================================================

        evidence = {
            "engine_part": "PART_5",
            "purpose": (
                "False Breakout & Opportunity Intelligence"
            ),

            "inputs": {
                "readiness": readiness,
                "compression": compression,
                "energy": energy,

                "upper_attack": upper_attack,
                "lower_attack": lower_attack,
                "weakening": weakening,
                "persistence": persistence,
                "rejection": rejection,

                "bullish_pressure": bullish_pressure,
                "bearish_pressure": bearish_pressure,
                "breakout_fuel": fuel,
                "volume_expansion": volume_expansion,
                "pressure_alignment": pressure_alignment,

                "bullish_probability": bullish_probability,
                "bearish_probability": bearish_probability,
                "neutral_probability": neutral_probability,
                "breakout_probability": breakout_probability,
                "directional_edge": directional_edge,
                "expected_move_score": expected_move,
            },

            "outputs": {
                "false_breakout_risk": false_breakout_risk,
                "trap_probability": trap_probability,
                "failure_probability": failure_probability,
                "retest_survivability": retest_survivability,
                "continuation_strength": continuation_strength,
                "risk_adjusted_breakout_score": (
                    risk_adjusted_breakout_score
                ),
                "profit_conversion_score": (
                    profit_conversion_score
                ),
                "opportunity_rank_score": (
                    opportunity_rank_score
                ),
                "opportunity_grade": opportunity_grade,
                "opportunity_direction": opportunity_direction,
            },

            "governance": {
                "final_decision_authority": "D13",
                "scanner_role": "OPPORTUNITY_DISCOVERY",
                "formula_status": "PROXY_UNTIL_VALIDATED",
                "probability_status": calibration_status,
            },
        }

        return BreakoutOpportunityIntelligence(
            false_breakout_risk=false_breakout_risk,
            trap_probability=trap_probability,
            failure_probability=failure_probability,
            retest_survivability=retest_survivability,
            continuation_strength=continuation_strength,
            risk_adjusted_breakout_score=(
                risk_adjusted_breakout_score
            ),
            profit_conversion_score=profit_conversion_score,
            opportunity_grade=opportunity_grade,
            opportunity_rank_score=opportunity_rank_score,
            breakout_direction=breakout_direction,
            opportunity_direction=opportunity_direction,
            confidence=confidence,
            evidence_quality=evidence_quality,
            calibration_status=calibration_status,
            evidence=evidence,
        )

    # ============================================================
    # FALSE BREAKOUT RISK
    # ============================================================

    def _calculate_false_breakout_risk(
        self,
        breakout_probability,
        fuel,
        volume_expansion,
        pressure_alignment,
        rejection,
        persistence,
        weakening,
        readiness,
        neutral_probability,
    ):

        confirmation_quality = (
            fuel * 0.25
            + volume_expansion * 0.15
            + pressure_alignment * 0.20
            + persistence * 0.15
            + weakening * 0.15
            + readiness * 0.10
        )

        rejection_penalty = rejection * 0.25

        risk = (
            100.0
            - confirmation_quality
            + rejection_penalty
            + neutral_probability * 0.20
        )

        # Strong breakout probability reduces risk,
        # but does NOT eliminate it.
        risk -= breakout_probability * 0.15

        return self._clip(risk)

    # ============================================================
    # TRAP PROBABILITY
    # ============================================================

    def _calculate_trap_probability(
        self,
        false_breakout_risk,
        rejection,
        pressure_alignment,
        volume_expansion,
        persistence,
        fuel,
        directional_edge,
    ):

        weak_participation = 100.0 - (
            fuel * 0.50
            + volume_expansion * 0.20
            + pressure_alignment * 0.30
        )

        weak_persistence = 100.0 - persistence

        weak_direction = 100.0 - directional_edge

        trap = (
            false_breakout_risk * 0.35
            + rejection * 0.20
            + weak_participation * 0.20
            + weak_persistence * 0.10
            + weak_direction * 0.15
        )

        return self._clip(trap)

    # ============================================================
    # FAILURE PROBABILITY
    # ============================================================

    def _calculate_failure_probability(
        self,
        false_breakout_risk,
        trap_probability,
        readiness,
        fuel,
        pressure_alignment,
        weakening,
    ):

        structural_support = (
            readiness * 0.25
            + fuel * 0.25
            + pressure_alignment * 0.20
            + weakening * 0.30
        )

        failure = (
            false_breakout_risk * 0.40
            + trap_probability * 0.35
            + (100.0 - structural_support) * 0.25
        )

        return self._clip(failure)

    # ============================================================
    # RETEST SURVIVABILITY
    # ============================================================

    def _estimate_retest_survivability(
        self,
        weakening,
        persistence,
        rejection,
        fuel,
        pressure_alignment,
    ):

        rejection_penalty = 100.0 - rejection

        score = (
            weakening * 0.25
            + persistence * 0.20
            + fuel * 0.20
            + pressure_alignment * 0.20
            + rejection_penalty * 0.15
        )

        return self._clip(score)

    # ============================================================
    # CONTINUATION STRENGTH
    # ============================================================

    def _estimate_continuation_strength(
        self,
        readiness,
        energy,
        fuel,
        pressure_alignment,
        directional_edge,
        expected_move,
        retest_survivability,
    ):

        score = (
            readiness * 0.10
            + energy * 0.10
            + fuel * 0.20
            + pressure_alignment * 0.20
            + directional_edge * 0.15
            + expected_move * 0.10
            + retest_survivability * 0.15
        )

        return self._clip(score)

    # ============================================================
    # RISK ADJUSTED SCORE
    # ============================================================

    def _calculate_risk_adjusted_score(
        self,
        breakout_probability,
        continuation_strength,
        retest_survivability,
        risk_component,
        trap_probability,
        failure_probability,
    ):

        gross_opportunity = (
            breakout_probability * 0.30
            + continuation_strength * 0.25
            + retest_survivability * 0.20
            + risk_component * 0.25
        )

        risk_penalty = (
            trap_probability * 0.50
            + failure_probability * 0.50
        )

        score = gross_opportunity - risk_penalty * 0.35

        return self._clip(score)

    # ============================================================
    # PROFIT CONVERSION SCORE
    # ============================================================

    def _calculate_profit_conversion_score(
        self,
        breakout_probability,
        expected_move,
        continuation_strength,
        retest_survivability,
        fuel,
        risk_adjusted_score,
        false_breakout_risk,
    ):

        score = (
            breakout_probability * 0.20
            + expected_move * 0.15
            + continuation_strength * 0.20
            + retest_survivability * 0.15
            + fuel * 0.10
            + risk_adjusted_score * 0.20
        )

        score -= false_breakout_risk * 0.20

        return self._clip(score)

    # ============================================================
    # EVIDENCE QUALITY
    # ============================================================

    def _calculate_evidence_quality(
        self,
        compression,
        readiness,
        weakening,
        persistence,
        fuel,
        volume_expansion,
        pressure_alignment,
        retest_survivability,
        continuation_strength,
    ):

        score = (
            compression * 0.10
            + readiness * 0.10
            + weakening * 0.10
            + persistence * 0.10
            + fuel * 0.15
            + volume_expansion * 0.10
            + pressure_alignment * 0.15
            + retest_survivability * 0.10
            + continuation_strength * 0.10
        )

        return self._clip(score)

    # ============================================================
    # OPPORTUNITY GRADE
    # ============================================================

    def _grade_opportunity(
        self,
        rank_score,
        false_breakout_risk,
        trap_probability,
        evidence_quality,
    ):

        # Hard safety filters
        if evidence_quality < 35.0:
            return "INSUFFICIENT_EVIDENCE"

        if false_breakout_risk >= 80.0:
            return "TRAP_RISK"

        if trap_probability >= 80.0:
            return "TRAP_RISK"

        # Opportunity grading
        if rank_score >= 85.0:
            return "A+"

        if rank_score >= 75.0:
            return "A"

        if rank_score >= 65.0:
            return "B"

        if rank_score >= 55.0:
            return "C"

        return "D"

    # ============================================================
    # DIRECTION RESOLUTION
    # ============================================================

    def _resolve_direction(
        self,
        breakout_direction,
        attack_direction,
        bullish_probability,
        bearish_probability,
        bullish_pressure,
        bearish_pressure,
    ):

        if breakout_direction in (
            "BULLISH",
            "BEARISH",
        ):
            return breakout_direction

        if attack_direction == "UPPER_ATTACK":
            return "BULLISH"

        if attack_direction == "LOWER_ATTACK":
            return "BEARISH"

        if bullish_probability > bearish_probability:
            return "BULLISH"

        if bearish_probability > bullish_probability:
            return "BEARISH"

        if bullish_pressure > bearish_pressure:
            return "BULLISH"

        if bearish_pressure > bullish_pressure:
            return "BEARISH"

        return "NEUTRAL"

    # ============================================================
    # CONFIDENCE
    # ============================================================

    def _calculate_confidence(
        self,
        evidence_quality,
        directional_edge,
        breakout_probability,
        false_breakout_risk,
    ):

        confidence = (
            evidence_quality * 0.40
            + directional_edge * 0.25
            + breakout_probability * 0.20
            + (100.0 - false_breakout_risk) * 0.15
        )

        return self._clip(confidence)

    # ============================================================
    # CALIBRATION HOOK
    # ============================================================

    def _apply_calibration_hook(self, calibration_model):

        try:
            if hasattr(calibration_model, "predict_proba"):
                return "HISTORICAL_MODEL"

            if callable(calibration_model):
                return "HISTORICAL_MODEL"

        except Exception:
            pass

        return "UNCALIBRATED"

    # ============================================================
    # SAFE NORMALIZATION
    # ============================================================

    def _safe_score(self, value):

        try:
            value = float(value)

            if value != value:  # NaN
                return 50.0

            return self._clip(value)

        except (TypeError, ValueError):
            return 50.0

    def _clip(self, value):

        return max(
            self.probability_floor,
            min(
                self.probability_ceiling,
                float(value),
            ),
        )
```
