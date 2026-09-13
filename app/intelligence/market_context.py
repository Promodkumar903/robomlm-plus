from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from math import isfinite
from statistics import mean
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class MarketContextAssessment:
    timestamp: str
    symbol: str

    trend_score: float
    volume_score: float
    liquidity_score: float
    risk_score: float
    timing_score: float
    derivatives_score: float
    participation_score: float
    relationship_score: float

    mci_score: float
    context_state: str
    confidence_score: float
    stability_score: float

    dominant_direction: str
    contradiction: bool
    contradiction_reasons: tuple[str, ...]

    evidence: Mapping[str, Any] = field(default_factory=dict)
    observed: Mapping[str, Any] = field(default_factory=dict)
    derived: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class MarketContextIntelligence:
    """
    ROBOMLM Market Context Intelligence (MCI).

    Blueprint top-level weighting:

        Trend          20%
        Volume         15%
        Liquidity      15%
        Risk           15%  (risk quality; raw risk is inverted)
        Timing         10%
        Derivatives    10%
        Participation  10%
        Relationships   5%

    All component scores are normalized to [0, 100].

    Important architectural rule:
    observed market facts are kept separate from derived intelligence.
    No execution, authorization, broker, position, or kill-switch action
    is performed by this engine.
    """

    VERSION = "ROBOMLM-MCI-2.0"

    WEIGHTS = {
        "trend": 0.20,
        "volume": 0.15,
        "liquidity": 0.15,
        "risk": 0.15,
        "timing": 0.10,
        "derivatives": 0.10,
        "participation": 0.10,
        "relationships": 0.05,
    }

    STATES = (
        "STRONG_BULLISH",
        "BULLISH",
        "NEUTRAL",
        "BEARISH",
        "STRONG_BEARISH",
        "FRAGILE",
        "CONFLICTED",
        "INSUFFICIENT",
    )

    def __init__(self, history_limit: int = 500) -> None:
        if history_limit < 1:
            raise ValueError("history_limit must be >= 1")

        self.history_limit = int(history_limit)
        self._history: list[MarketContextAssessment] = []

    # ------------------------------------------------------------------
    # Normalization
    # ------------------------------------------------------------------

    @staticmethod
    def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
        if not isfinite(value):
            return low
        return max(low, min(high, float(value)))

    @classmethod
    def _score(cls, value: Any, default: float = 0.0) -> float:
        if value is None:
            return cls._clamp(default)

        if isinstance(value, bool):
            return 100.0 if value else 0.0

        try:
            number = float(value)
        except (TypeError, ValueError):
            return cls._clamp(default)

        if not isfinite(number):
            return cls._clamp(default)

        return cls._clamp(number)

    @classmethod
    def _percentage(cls, value: Any, default: float = 0.0) -> float:
        """
        Convert a fractional percentage input to 0-100.

        Examples:
            0.75 -> 75
            75   -> 75
        """
        if value is None:
            return cls._score(default)

        try:
            number = float(value)
        except (TypeError, ValueError):
            return cls._score(default)

        if not isfinite(number):
            return cls._score(default)

        if -1.0 <= number <= 1.0:
            number *= 100.0

        return cls._clamp(number)

    @classmethod
    def _signed_score(cls, value: Any) -> float:
        """
        Convert directional input [-100,100] into strength [0,100].
        """
        try:
            number = float(value)
        except (TypeError, ValueError):
            return 0.0

        if not isfinite(number):
            return 0.0

        number = max(-100.0, min(100.0, number))
        return abs(number)

    # ------------------------------------------------------------------
    # Input extraction
    # ------------------------------------------------------------------

    @staticmethod
    def _get(
        data: Mapping[str, Any],
        *keys: str,
        default: Any = None,
    ) -> Any:
        for key in keys:
            if key in data and data[key] is not None:
                return data[key]
        return default

    def _extract_trend(self, data: Mapping[str, Any]) -> tuple[float, float]:
        explicit = self._get(
            data,
            "trend_score",
            "trend_strength",
            "trend_quality",
        )

        direction = str(
            self._get(data, "trend_direction", "direction", default="")
        ).upper()

        if explicit is not None:
            strength = self._score(explicit)
        else:
            adx = self._score(self._get(data, "adx"), 0.0)
            slope = self._signed_score(
                self._get(data, "trend_slope", "price_slope", default=0.0)
            )

            strength = (
                adx * 0.60 +
                slope * 0.40
            )

        directional = 0.0
        if direction in {"BUY", "BULLISH", "LONG", "UP"}:
            directional = strength
        elif direction in {"SELL", "BEARISH", "SHORT", "DOWN"}:
            directional = -strength

        return self._clamp(strength), directional

    def _extract_volume(self, data: Mapping[str, Any]) -> float:
        explicit = self._get(
            data,
            "volume_score",
            "volume_strength",
            "volume_quality",
        )

        if explicit is not None:
            return self._score(explicit)

        ratio = self._get(
            data,
            "volume_ratio",
            "relative_volume",
            default=None,
        )

        if ratio is None:
            return 0.0

        try:
            ratio = float(ratio)
        except (TypeError, ValueError):
            return 0.0

        if not isfinite(ratio) or ratio < 0:
            return 0.0

        # 1.0x = normal participation.
        # 2.0x or greater = maximum volume strength.
        return self._clamp((ratio / 2.0) * 100.0)

    def _extract_liquidity(self, data: Mapping[str, Any]) -> float:
        explicit = self._get(
            data,
            "liquidity_score",
            "liquidity_quality",
        )

        if explicit is not None:
            return self._score(explicit)

        spread = self._get(
            data,
            "spread_pct",
            "bid_ask_spread_pct",
            default=None,
        )

        depth = self._get(
            data,
            "depth_score",
            "order_book_depth_score",
            default=None,
        )

        if spread is None and depth is None:
            return 0.0

        spread_quality = 100.0
        if spread is not None:
            try:
                spread_value = max(0.0, float(spread))
                # 0% spread -> 100 quality
                # >= 1% spread -> 0 quality
                spread_quality = self._clamp(
                    100.0 - spread_value * 100.0
                )
            except (TypeError, ValueError):
                spread_quality = 0.0

        depth_quality = self._score(depth, 0.0)

        if depth is None:
            return spread_quality

        if spread is None:
            return depth_quality

        return self._clamp(
            spread_quality * 0.50 +
            depth_quality * 0.50
        )

    def _extract_risk(self, data: Mapping[str, Any]) -> float:
        """
        Risk is represented internally as RISK QUALITY.

        If the caller provides raw risk (0 = low risk, 100 = high risk),
        it is inverted:

            risk_quality = 100 - raw_risk
        """
        quality = self._get(
            data,
            "risk_score",
            "risk_quality",
            default=None,
        )

        if quality is not None:
            return self._score(quality)

        raw_risk = self._get(
            data,
            "raw_risk",
            "risk",
            "risk_level",
            default=None,
        )

        if raw_risk is None:
            return 0.0

        return self._clamp(100.0 - self._score(raw_risk))

    def _extract_timing(self, data: Mapping[str, Any]) -> float:
        explicit = self._get(
            data,
            "timing_score",
            "timing_quality",
            "session_score",
        )

        if explicit is not None:
            return self._score(explicit)

        session = str(
            self._get(data, "session", "market_session", default="")
        ).upper()

        phase = str(
            self._get(data, "phase", "market_phase", default="")
        ).upper()

        session_scores = {
            "OPEN": 85.0,
            "OPENING": 85.0,
            "MORNING": 80.0,
            "MIDDAY": 45.0,
            "AFTERNOON": 70.0,
            "CLOSE": 85.0,
            "CLOSING": 85.0,
        }

        phase_scores = {
            "OPENING": 85.0,
            "DISCOVERY": 75.0,
            "EXPANSION": 90.0,
            "TREND": 85.0,
            "TRENDING": 85.0,
            "CONSOLIDATION": 55.0,
            "RANGE": 55.0,
            "TRANSITION": 40.0,
            "CLOSING": 80.0,
        }

        values: list[float] = []

        if session in session_scores:
            values.append(session_scores[session])

        if phase in phase_scores:
            values.append(phase_scores[phase])

        return self._clamp(mean(values)) if values else 0.0

    def _extract_derivatives(
        self,
        data: Mapping[str, Any],
    ) -> tuple[float, float]:
        explicit = self._get(
            data,
            "derivatives_score",
            "derivative_score",
            "options_score",
        )

        direction = str(
            self._get(
                data,
                "derivatives_direction",
                "options_direction",
                default="",
            )
        ).upper()

        if explicit is not None:
            score = self._score(explicit)
        else:
            oi = self._score(
                self._get(
                    data,
                    "oi_score",
                    "open_interest_score",
                ),
                0.0,
            )

            flow = self._signed_score(
                self._get(
                    data,
                    "derivative_flow",
                    "options_flow",
                    default=0.0,
                )
            )

            score = (
                oi * 0.50 +
                flow * 0.50
            )

        directional = 0.0

        if direction in {"BUY", "BULLISH", "LONG", "CALL"}:
            directional = score
        elif direction in {"SELL", "BEARISH", "SHORT", "PUT"}:
            directional = -score

        return self._clamp(score), directional

    def _extract_participation(
        self,
        data: Mapping[str, Any],
    ) -> tuple[float, float]:
        explicit = self._get(
            data,
            "participation_score",
            "participation_quality",
        )

        direction = str(
            self._get(
                data,
                "participation_direction",
                default="",
            )
        ).upper()

        if explicit is not None:
            score = self._score(explicit)
        else:
            breadth = self._score(
                self._get(
                    data,
                    "breadth_score",
                    "market_breadth_score",
                ),
                0.0,
            )

            active = self._score(
                self._get(
                    data,
                    "active_participation_score",
                    "participation_breadth",
                ),
                0.0,
            )

            if breadth == 0.0 and active == 0.0:
                return 0.0, 0.0

            available = [
                value
                for value in (breadth, active)
                if value > 0.0
            ]

            score = mean(available)

        directional = 0.0

        if direction in {"BUY", "BULLISH", "LONG", "UP"}:
            directional = score
        elif direction in {"SELL", "BEARISH", "SHORT", "DOWN"}:
            directional = -score

        return self._clamp(score), directional

    def _extract_relationships(
        self,
        data: Mapping[str, Any],
    ) -> tuple[float, float]:
        explicit = self._get(
            data,
            "relationship_score",
            "relationships_score",
            "relationship_quality",
        )

        direction = str(
            self._get(
                data,
                "relationship_direction",
                "relationships_direction",
                default="",
            )
        ).upper()

        if explicit is not None:
            score = self._score(explicit)
        else:
            confirmation = self._score(
                self._get(
                    data,
                    "relationship_confirmation",
                    "cross_market_confirmation",
                ),
                0.0,
            )

            correlation = self._score(
                self._get(
                    data,
                    "correlation_score",
                    "cross_asset_score",
                ),
                0.0,
            )

            divergence = self._score(
                self._get(
                    data,
                    "divergence_score",
                ),
                0.0,
            )

            if confirmation == 0.0 and correlation == 0.0:
                return 0.0, 0.0

            score = (
                confirmation * 0.50 +
                correlation * 0.30 +
                (100.0 - divergence) * 0.20
            )

        directional = 0.0

        if direction in {"BUY", "BULLISH", "LONG", "UP"}:
            directional = score
        elif direction in {"SELL", "BEARISH", "SHORT", "DOWN"}:
            directional = -score

        return self._clamp(score), directional

    # ------------------------------------------------------------------
    # Core MCI calculation
    # ------------------------------------------------------------------

    def calculate_mci(
        self,
        *,
        trend: float,
        volume: float,
        liquidity: float,
        risk: float,
        timing: float,
        derivatives: float,
        participation: float,
        relationships: float,
    ) -> float:
        """
        Blueprint MCI formula:

            MCI =
                Trend          * 0.20
              + Volume         * 0.15
              + Liquidity      * 0.15
              + Risk           * 0.15
              + Timing         * 0.10
              + Derivatives    * 0.10
              + Participation  * 0.10
              + Relationships  * 0.05
        """
        return self._clamp(
            self._score(trend) * self.WEIGHTS["trend"] +
            self._score(volume) * self.WEIGHTS["volume"] +
            self._score(liquidity) * self.WEIGHTS["liquidity"] +
            self._score(risk) * self.WEIGHTS["risk"] +
            self._score(timing) * self.WEIGHTS["timing"] +
            self._score(derivatives) * self.WEIGHTS["derivatives"] +
            self._score(participation) * self.WEIGHTS["participation"] +
            self._score(relationships) * self.WEIGHTS["relationships"]
        )

    # ------------------------------------------------------------------
    # Direction / contradiction
    # ------------------------------------------------------------------

    @staticmethod
    def _direction_from_signed(value: float) -> str:
        if value >= 20.0:
            return "BUY"
        if value <= -20.0:
            return "SELL"
        return "NEUTRAL"

    def _detect_directional_conflict(
        self,
        directional_values: Mapping[str, float],
    ) -> tuple[bool, tuple[str, ...], str]:
        active = {
            name: value
            for name, value in directional_values.items()
            if abs(value) >= 20.0
        }

        if not active:
            return False, (), "NEUTRAL"

        bullish = sum(
            value for value in active.values()
            if value > 0
        )

        bearish = sum(
            abs(value) for value in active.values()
            if value < 0
        )

        reasons: list[str] = []

        if bullish > 0 and bearish > 0:
            smaller = min(bullish, bearish)
            larger = max(bullish, bearish)

            # A materially opposing directional body is a contradiction.
            if smaller >= larger * 0.40:
                for name, value in active.items():
                    if value > 0:
                        reasons.append(f"{name}:bullish")
                    else:
                        reasons.append(f"{name}:bearish")

                return True, tuple(reasons), "CONFLICTED"

        if bullish > bearish:
            return False, tuple(reasons), "BUY"

        if bearish > bullish:
            return False, tuple(reasons), "SELL"

        return False, tuple(reasons), "NEUTRAL"

    # ------------------------------------------------------------------
    # Context classification
    # ------------------------------------------------------------------

    def _classify(
        self,
        score: float,
        confidence: float,
        contradiction: bool,
        dominant_direction: str,
    ) -> str:
        if contradiction and confidence >= 50.0:
            return "CONFLICTED"

        if confidence < 35.0:
            return "INSUFFICIENT"

        if score < 35.0:
            return "FRAGILE"

        if dominant_direction == "BUY":
            if score >= 80.0 and confidence >= 75.0:
                return "STRONG_BULLISH"
            if score >= 60.0:
                return "BULLISH"

        if dominant_direction == "SELL":
            if score <= 20.0 and confidence >= 75.0:
                return "STRONG_BEARISH"
            if score <= 40.0:
                return "BEARISH"

        return "NEUTRAL"

    # ------------------------------------------------------------------
    # Confidence / stability
    # ------------------------------------------------------------------

    def _calculate_confidence(
        self,
        scores: Mapping[str, float],
        data: Mapping[str, Any],
        contradiction: bool,
    ) -> float:
        provided = sum(
            1
            for key in (
                "trend_score",
                "volume_score",
                "liquidity_score",
                "risk_score",
                "timing_score",
                "derivatives_score",
                "participation_score",
                "relationship_score",
            )
            if key in data
        )

        coverage = self._clamp(
            (provided / 8.0) * 100.0
        )

        quality = self._score(
            self._get(
                data,
                "data_quality_score",
                "quality_score",
                default=0.0,
            )
        )

        source_reliability = self._score(
            self._get(
                data,
                "source_reliability",
                "source_reliability_score",
                default=0.0,
            )
        )

        if quality == 0.0:
            quality = coverage

        if source_reliability == 0.0:
            source_reliability = quality

        dispersion = max(scores.values()) - min(scores.values())
        consistency = self._clamp(
            100.0 - dispersion
        )

        confidence = (
            coverage * 0.25 +
            quality * 0.25 +
            source_reliability * 0.20 +
            consistency * 0.30
        )

        if contradiction:
            confidence *= 0.70

        return self._clamp(confidence)

    def _calculate_stability(
        self,
        current_score: float,
        previous: Optional[MarketContextAssessment],
    ) -> float:
        if previous is None:
            return 50.0

        change = abs(
            current_score - previous.mci_score
        )

        # Smaller MCI movement means greater contextual stability.
        return self._clamp(
            100.0 - change * 2.0
        )

    # ------------------------------------------------------------------
    # Public assessment
    # ------------------------------------------------------------------

    def assess(
        self,
        market_data: Mapping[str, Any],
        *,
        symbol: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> MarketContextAssessment:
        if not isinstance(market_data, Mapping):
            raise TypeError("market_data must be a mapping")

        resolved_symbol = str(
            symbol
            or self._get(
                market_data,
                "symbol",
                "instrument",
                "ticker",
                default="UNKNOWN",
            )
        )

        resolved_timestamp = (
            timestamp
            or self._get(
                market_data,
                "timestamp",
                "observed_at",
            )
            or datetime.now(timezone.utc).isoformat()
        )

        trend, trend_direction = self._extract_trend(market_data)
        volume = self._extract_volume(market_data)
        liquidity = self._extract_liquidity(market_data)
        risk = self._extract_risk(market_data)
        timing = self._extract_timing(market_data)
        derivatives, derivative_direction = self._extract_derivatives(
            market_data
        )
        participation, participation_direction = (
            self._extract_participation(market_data)
        )
        relationships, relationship_direction = (
            self._extract_relationships(market_data)
        )

        scores = {
            "trend": trend,
            "volume": volume,
            "liquidity": liquidity,
            "risk": risk,
            "timing": timing,
            "derivatives": derivatives,
            "participation": participation,
            "relationships": relationships,
        }

        directional_values = {
            "trend": trend_direction,
            "derivatives": derivative_direction,
            "participation": participation_direction,
            "relationships": relationship_direction,
        }

        contradiction, contradiction_reasons, dominant_direction = (
            self._detect_directional_conflict(
                directional_values
            )
        )

        mci_score = self.calculate_mci(**scores)

        confidence = self._calculate_confidence(
            scores,
            market_data,
            contradiction,
        )

        previous = self._history[-1] if self._history else None

        stability = self._calculate_stability(
            mci_score,
            previous,
        )

        context_state = self._classify(
            mci_score,
            confidence,
            contradiction,
            dominant_direction,
        )

        observed = dict(market_data)

        derived = {
            "mci_formula": dict(self.WEIGHTS),
            "mci_score": round(mci_score, 4),
            "confidence_score": round(confidence, 4),
            "stability_score": round(stability, 4),
            "dominant_direction": dominant_direction,
            "component_scores": {
                key: round(value, 4)
                for key, value in scores.items()
            },
            "contradiction": contradiction,
            "contradiction_reasons": contradiction_reasons,
        }

        evidence = {
            "engine": self.VERSION,
            "symbol": resolved_symbol,
            "timestamp": resolved_timestamp,
            "observed_fields": tuple(sorted(observed.keys())),
            "derived_fields": tuple(sorted(derived.keys())),
        }

        assessment = MarketContextAssessment(
            timestamp=str(resolved_timestamp),
            symbol=resolved_symbol,
            trend_score=round(trend, 4),
            volume_score=round(volume, 4),
            liquidity_score=round(liquidity, 4),
            risk_score=round(risk, 4),
            timing_score=round(timing, 4),
            derivatives_score=round(derivatives, 4),
            participation_score=round(participation, 4),
            relationship_score=round(relationships, 4),
            mci_score=round(mci_score, 4),
            context_state=context_state,
            confidence_score=round(confidence, 4),
            stability_score=round(stability, 4),
            dominant_direction=dominant_direction,
            contradiction=contradiction,
            contradiction_reasons=contradiction_reasons,
            evidence=evidence,
            observed=observed,
            derived=derived,
        )

        self._history.append(assessment)

        if len(self._history) > self.history_limit:
            del self._history[
                :len(self._history) - self.history_limit
            ]

        return assessment

    # ------------------------------------------------------------------
    # History / memory hooks
    # ------------------------------------------------------------------

    def latest(self) -> Optional[MarketContextAssessment]:
        return self._history[-1] if self._history else None

    def history(
        self,
        limit: Optional[int] = None,
    ) -> tuple[MarketContextAssessment, ...]:
        if limit is None:
            return tuple(self._history)

        if limit < 1:
            return ()

        return tuple(self._history[-limit:])

    def average_mci(
        self,
        limit: Optional[int] = None,
    ) -> float:
        records = self.history(limit)

        if not records:
            return 0.0

        return round(
            mean(record.mci_score for record in records),
            4,
        )

    def detect_transition(
        self,
        current: Optional[MarketContextAssessment] = None,
    ) -> dict[str, Any]:
        records = self.history()

        if current is None:
            current = self.latest()

        if current is None or len(records) < 2:
            return {
                "transition": False,
                "from_state": None,
                "to_state": (
                    current.context_state
                    if current is not None
                    else None
                ),
                "score_change": 0.0,
            }

        previous = records[-2]

        return {
            "transition": (
                previous.context_state != current.context_state
            ),
            "from_state": previous.context_state,
            "to_state": current.context_state,
            "score_change": round(
                current.mci_score - previous.mci_score,
                4,
            ),
            "direction_change": (
                previous.dominant_direction
                != current.dominant_direction
            ),
        }

    def clear_history(self) -> None:
        self._history.clear()

    def health_check(self) -> dict[str, Any]:
        weight_sum = sum(self.WEIGHTS.values())

        return {
            "engine": self.VERSION,
            "healthy": abs(weight_sum - 1.0) < 1e-9,
            "history_size": len(self._history),
            "history_limit": self.history_limit,
            "weight_sum": round(weight_sum, 10),
            "latest_available": self.latest() is not None,
        }


# Backward-compatible aliases for integration layers.
MarketContextEngine = MarketContextIntelligence
MarketContextIntelligenceEngine = MarketContextIntelligence


__all__ = [
    "MarketContextAssessment",
    "MarketContextIntelligence",
    "MarketContextEngine",
    "MarketContextIntelligenceEngine",
]