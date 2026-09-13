from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from math import isfinite
from statistics import mean
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class RegimeAssessment:
    timestamp: str
    symbol: str

    regime: str
    regime_strength: float
    confidence_score: float
    stability_score: float
    transition_probability: float

    trend_score: float
    volatility_score: float
    liquidity_score: float
    participation_score: float
    momentum_score: float

    accumulation_score: float
    distribution_score: float
    risk_on_score: float
    risk_off_score: float

    contradiction: bool
    contradiction_reasons: tuple[str, ...]

    observed: Mapping[str, Any] = field(default_factory=dict)
    derived: Mapping[str, Any] = field(default_factory=dict)
    evidence: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RegimeIntelligence:
    """
    ROBOMLM Market Regime Intelligence Engine.

    The engine converts observable market-state variables into a
    structured regime assessment.

    Primary dimensions:
        trend
        volatility
        liquidity
        participation
        momentum

    Secondary structural states:
        accumulation
        distribution
        risk-on
        risk-off

    The engine does not execute trades and does not modify positions,
    authorization state, broker state, or kill-switch state.
    """

    VERSION = "ROBOMLM-REGIME-2.0"

    WEIGHTS = {
        "trend": 0.25,
        "volatility": 0.20,
        "liquidity": 0.15,
        "participation": 0.15,
        "momentum": 0.10,
        "stability": 0.15,
    }

    REGIMES = (
        "TRENDING",
        "RANGING",
        "EXPANSION",
        "COMPRESSION",
        "ACCUMULATION",
        "DISTRIBUTION",
        "RISK_ON",
        "RISK_OFF",
        "TRANSITION",
        "MIXED",
        "INSUFFICIENT",
    )

    def __init__(self, history_limit: int = 500) -> None:
        if history_limit < 1:
            raise ValueError("history_limit must be >= 1")

        self.history_limit = int(history_limit)
        self._history: list[RegimeAssessment] = []

    # ------------------------------------------------------------------
    # Numeric primitives
    # ------------------------------------------------------------------

    @staticmethod
    def _clamp(
        value: float,
        low: float = 0.0,
        high: float = 100.0,
    ) -> float:
        if not isfinite(value):
            return low
        return max(low, min(high, float(value)))

    @classmethod
    def _score(
        cls,
        value: Any,
        default: float = 0.0,
    ) -> float:
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
    def _signed(
        cls,
        value: Any,
    ) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return 0.0

        if not isfinite(number):
            return 0.0

        return max(-100.0, min(100.0, number))

    @classmethod
    def _direction_strength(
        cls,
        value: Any,
    ) -> tuple[float, float]:
        signed = cls._signed(value)
        return abs(signed), signed

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

    # ------------------------------------------------------------------
    # Trend
    # ------------------------------------------------------------------

    def _trend(
        self,
        data: Mapping[str, Any],
    ) -> tuple[float, float]:
        explicit = self._get(
            data,
            "trend_score",
            "trend_strength",
            default=None,
        )

        direction = str(
            self._get(
                data,
                "trend_direction",
                "direction",
                default="",
            )
        ).upper()

        if explicit is not None:
            strength = self._score(explicit)
        else:
            adx = self._score(
                self._get(data, "adx", default=0.0)
            )

            slope = abs(
                self._signed(
                    self._get(
                        data,
                        "trend_slope",
                        "price_slope",
                        default=0.0,
                    )
                )
            )

            structure = self._score(
                self._get(
                    data,
                    "structure_score",
                    "market_structure_score",
                    default=0.0,
                )
            )

            components = [
                value
                for value in (adx, slope, structure)
                if value > 0.0
            ]

            strength = (
                mean(components)
                if components
                else 0.0
            )

        signed = strength

        if direction in {
            "SELL",
            "BEARISH",
            "SHORT",
            "DOWN",
        }:
            signed = -strength

        return self._clamp(strength), self._clamp(
            signed,
            -100.0,
            100.0,
        )

    # ------------------------------------------------------------------
    # Volatility
    # ------------------------------------------------------------------

    def _volatility(
        self,
        data: Mapping[str, Any],
    ) -> float:
        explicit = self._get(
            data,
            "volatility_score",
            "volatility_strength",
            default=None,
        )

        if explicit is not None:
            return self._score(explicit)

        percentile = self._get(
            data,
            "volatility_percentile",
            "vol_percentile",
            default=None,
        )

        atr_pct = self._get(
            data,
            "atr_pct",
            "atr_percent",
            default=None,
        )

        values: list[float] = []

        if percentile is not None:
            values.append(self._score(percentile))

        if atr_pct is not None:
            try:
                atr = float(atr_pct)
                if isfinite(atr):
                    # Approximate normalized volatility strength.
                    values.append(
                        self._clamp(atr * 20.0)
                    )
            except (TypeError, ValueError):
                pass

        return (
            self._clamp(mean(values))
            if values
            else 0.0
        )

    # ------------------------------------------------------------------
    # Liquidity
    # ------------------------------------------------------------------

    def _liquidity(
        self,
        data: Mapping[str, Any],
    ) -> float:
        explicit = self._get(
            data,
            "liquidity_score",
            "liquidity_quality",
            default=None,
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
                spread_quality = self._clamp(
                    100.0 - spread_value * 100.0
                )
            except (TypeError, ValueError):
                spread_quality = 0.0

        if depth is None:
            return spread_quality

        depth_quality = self._score(depth)

        return self._clamp(
            spread_quality * 0.50
            + depth_quality * 0.50
        )

    # ------------------------------------------------------------------
    # Participation
    # ------------------------------------------------------------------

    def _participation(
        self,
        data: Mapping[str, Any],
    ) -> tuple[float, float]:
        explicit = self._get(
            data,
            "participation_score",
            "participation_quality",
            default=None,
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
                    default=0.0,
                )
            )

            volume = self._score(
                self._get(
                    data,
                    "participation_volume_score",
                    "relative_volume_score",
                    default=0.0,
                )
            )

            values = [
                value
                for value in (breadth, volume)
                if value > 0.0
            ]

            score = mean(values) if values else 0.0

        signed = score

        if direction in {
            "SELL",
            "BEARISH",
            "SHORT",
            "DOWN",
        }:
            signed = -score

        return self._clamp(score), self._clamp(
            signed,
            -100.0,
            100.0,
        )

    # ------------------------------------------------------------------
    # Momentum
    # ------------------------------------------------------------------

    def _momentum(
        self,
        data: Mapping[str, Any],
    ) -> tuple[float, float]:
        explicit = self._get(
            data,
            "momentum_score",
            "momentum_strength",
            default=None,
        )

        if explicit is not None:
            strength, signed = self._direction_strength(
                explicit
            )
            return strength, signed

        raw = self._get(
            data,
            "momentum",
            "momentum_value",
            "roc",
            default=0.0,
        )

        signed = self._signed(raw)

        return abs(signed), signed

    # ------------------------------------------------------------------
    # Accumulation / distribution
    # ------------------------------------------------------------------

    def _flow_structure(
        self,
        data: Mapping[str, Any],
    ) -> tuple[float, float]:
        accumulation = self._score(
            self._get(
                data,
                "accumulation_score",
                "accumulation",
                default=0.0,
            )
        )

        distribution = self._score(
            self._get(
                data,
                "distribution_score",
                "distribution",
                default=0.0,
            )
        )

        # Optional money-flow inputs.
        flow = self._signed(
            self._get(
                data,
                "capital_flow",
                "money_flow",
                "institutional_flow",
                default=0.0,
            )
        )

        if accumulation == 0.0 and distribution == 0.0:
            if flow > 0.0:
                accumulation = abs(flow)
            elif flow < 0.0:
                distribution = abs(flow)

        return accumulation, distribution

    # ------------------------------------------------------------------
    # Risk-on / risk-off
    # ------------------------------------------------------------------

    def _risk_state(
        self,
        data: Mapping[str, Any],
    ) -> tuple[float, float]:
        risk_on = self._score(
            self._get(
                data,
                "risk_on_score",
                "risk_on",
                default=0.0,
            )
        )

        risk_off = self._score(
            self._get(
                data,
                "risk_off_score",
                "risk_off",
                default=0.0,
            )
        )

        if risk_on == 0.0 and risk_off == 0.0:
            raw = self._signed(
                self._get(
                    data,
                    "risk_sentiment",
                    "risk_regime",
                    default=0.0,
                )
            )

            if raw > 0:
                risk_on = abs(raw)
            elif raw < 0:
                risk_off = abs(raw)

        return risk_on, risk_off

    # ------------------------------------------------------------------
    # Stability
    # ------------------------------------------------------------------

    def _stability(
        self,
        current_score: float,
        previous: Optional[RegimeAssessment],
    ) -> float:
        if previous is None:
            return 50.0

        score_change = abs(
            current_score
            - previous.regime_strength
        )

        state_penalty = (
            35.0
            if previous.regime != ""
            else 0.0
        )

        base = self._clamp(
            100.0
            - score_change * 2.0
        )

        if previous.regime != "":
            return self._clamp(
                base
                - (
                    state_penalty
                    if score_change > 25.0
                    else 0.0
                )
            )

        return base

    # ------------------------------------------------------------------
    # Composite regime strength
    # ------------------------------------------------------------------

    def _regime_strength(
        self,
        trend: float,
        volatility: float,
        liquidity: float,
        participation: float,
        momentum: float,
        stability: float,
    ) -> float:
        """
        Regime strength formula:

            RS =
                Trend          * 0.25
              + Volatility     * 0.20
              + Liquidity      * 0.15
              + Participation  * 0.15
              + Momentum       * 0.10
              + Stability      * 0.15
        """
        return self._clamp(
            trend * self.WEIGHTS["trend"]
            + volatility * self.WEIGHTS["volatility"]
            + liquidity * self.WEIGHTS["liquidity"]
            + participation * self.WEIGHTS["participation"]
            + momentum * self.WEIGHTS["momentum"]
            + stability * self.WEIGHTS["stability"]
        )

    # ------------------------------------------------------------------
    # Transition probability
    # ------------------------------------------------------------------

    def _transition_probability(
        self,
        *,
        current_score: float,
        previous: Optional[RegimeAssessment],
        contradiction: bool,
        volatility: float,
    ) -> float:
        if previous is None:
            return 0.0

        score_change = abs(
            current_score
            - previous.regime_strength
        )

        probability = self._clamp(
            score_change * 2.5
        )

        if volatility >= 80.0:
            probability += 10.0

        if contradiction:
            probability += 20.0

        if previous.regime != "":
            probability += (
                20.0
                if score_change >= 25.0
                else 0.0
            )

        return self._clamp(probability)

    # ------------------------------------------------------------------
    # Contradiction detection
    # ------------------------------------------------------------------

    def _contradictions(
        self,
        *,
        trend_direction: float,
        accumulation: float,
        distribution: float,
        risk_on: float,
        risk_off: float,
        volatility: float,
        participation: float,
    ) -> tuple[bool, tuple[str, ...]]:
        reasons: list[str] = []

        if (
            trend_direction > 30.0
            and distribution >= 60.0
        ):
            reasons.append(
                "bullish_trend_vs_distribution"
            )

        if (
            trend_direction < -30.0
            and accumulation >= 60.0
        ):
            reasons.append(
                "bearish_trend_vs_accumulation"
            )

        if (
            risk_on >= 65.0
            and risk_off >= 65.0
        ):
            reasons.append(
                "risk_on_vs_risk_off"
            )

        if (
            volatility >= 80.0
            and participation < 30.0
        ):
            reasons.append(
                "high_volatility_without_participation"
            )

        if (
            abs(trend_direction) >= 70.0
            and participation < 25.0
        ):
            reasons.append(
                "strong_trend_without_participation"
            )

        return bool(reasons), tuple(reasons)

    # ------------------------------------------------------------------
    # Regime classification
    # ------------------------------------------------------------------

    def _classify(
        self,
        *,
        trend: float,
        trend_direction: float,
        volatility: float,
        liquidity: float,
        participation: float,
        momentum: float,
        accumulation: float,
        distribution: float,
        risk_on: float,
        risk_off: float,
        stability: float,
        confidence: float,
        contradiction: bool,
    ) -> str:
        if confidence < 30.0:
            return "INSUFFICIENT"

        if contradiction and confidence >= 50.0:
            return "MIXED"

        # Structural flow regimes take priority when strongly evidenced.
        if accumulation >= 75.0 and distribution < 55.0:
            return "ACCUMULATION"

        if distribution >= 75.0 and accumulation < 55.0:
            return "DISTRIBUTION"

        # Risk regimes require a clear separation.
        if (
            risk_on >= 75.0
            and risk_on >= risk_off + 20.0
            and participation >= 40.0
        ):
            return "RISK_ON"

        if (
            risk_off >= 75.0
            and risk_off >= risk_on + 20.0
        ):
            return "RISK_OFF"

        # Volatility expansion/compression is a market-state regime.
        if (
            volatility >= 80.0
            and participation >= 45.0
            and liquidity >= 35.0
        ):
            return "EXPANSION"

        if (
            volatility <= 25.0
            and trend <= 45.0
        ):
            return "COMPRESSION"

        # Strong trend requires directional strength and participation.
        if (
            trend >= 65.0
            and abs(trend_direction) >= 45.0
            and participation >= 40.0
            and momentum >= 40.0
        ):
            return "TRENDING"

        # A range is characterized by weak trend and contained volatility.
        if (
            trend <= 40.0
            and volatility <= 65.0
            and liquidity >= 35.0
        ):
            return "RANGING"

        # Fast-changing states.
        if stability <= 35.0:
            return "TRANSITION"

        return "MIXED"

    # ------------------------------------------------------------------
    # Confidence
    # ------------------------------------------------------------------

    def _confidence(
        self,
        *,
        trend: float,
        volatility: float,
        liquidity: float,
        participation: float,
        momentum: float,
        stability: float,
        data: Mapping[str, Any],
        contradiction: bool,
    ) -> float:
        component_values = (
            trend,
            volatility,
            liquidity,
            participation,
            momentum,
            stability,
        )

        nonzero = sum(
            1
            for value in component_values
            if value > 0.0
        )

        coverage = self._clamp(
            nonzero / 6.0 * 100.0
        )

        data_quality = self._score(
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
                "source_reliability_score",
                "source_reliability",
                default=0.0,
            )
        )

        if data_quality == 0.0:
            data_quality = coverage

        if source_reliability == 0.0:
            source_reliability = data_quality

        dispersion = max(component_values) - min(
            component_values
        )

        consistency = self._clamp(
            100.0 - dispersion
        )

        confidence = (
            coverage * 0.25
            + data_quality * 0.25
            + source_reliability * 0.20
            + consistency * 0.15
            + stability * 0.15
        )

        if contradiction:
            confidence *= 0.70

        return self._clamp(confidence)

    # ------------------------------------------------------------------
    # Public assessment
    # ------------------------------------------------------------------

    def assess(
        self,
        market_data: Mapping[str, Any],
        *,
        symbol: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> RegimeAssessment:
        if not isinstance(market_data, Mapping):
            raise TypeError(
                "market_data must be a mapping"
            )

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
                default=None,
            )
            or datetime.now(
                timezone.utc
            ).isoformat()
        )

        trend, trend_direction = self._trend(
            market_data
        )

        volatility = self._volatility(
            market_data
        )

        liquidity = self._liquidity(
            market_data
        )

        participation, participation_direction = (
            self._participation(
                market_data
            )
        )

        momentum, momentum_direction = (
            self._momentum(
                market_data
            )
        )

        accumulation, distribution = (
            self._flow_structure(
                market_data
            )
        )

        risk_on, risk_off = self._risk_state(
            market_data
        )

        preliminary_strength = self._regime_strength(
            trend,
            volatility,
            liquidity,
            participation,
            momentum,
            50.0,
        )

        previous = (
            self._history[-1]
            if self._history
            else None
        )

        stability = self._stability(
            preliminary_strength,
            previous,
        )

        regime_strength = self._regime_strength(
            trend,
            volatility,
            liquidity,
            participation,
            momentum,
            stability,
        )

        contradiction, contradiction_reasons = (
            self._contradictions(
                trend_direction=trend_direction,
                accumulation=accumulation,
                distribution=distribution,
                risk_on=risk_on,
                risk_off=risk_off,
                volatility=volatility,
                participation=participation,
            )
        )

        confidence = self._confidence(
            trend=trend,
            volatility=volatility,
            liquidity=liquidity,
            participation=participation,
            momentum=momentum,
            stability=stability,
            data=market_data,
            contradiction=contradiction,
        )

        transition_probability = (
            self._transition_probability(
                current_score=regime_strength,
                previous=previous,
                contradiction=contradiction,
                volatility=volatility,
            )
        )

        regime = self._classify(
            trend=trend,
            trend_direction=trend_direction,
            volatility=volatility,
            liquidity=liquidity,
            participation=participation,
            momentum=momentum,
            accumulation=accumulation,
            distribution=distribution,
            risk_on=risk_on,
            risk_off=risk_off,
            stability=stability,
            confidence=confidence,
            contradiction=contradiction,
        )

        observed = dict(market_data)

        derived = {
            "regime_strength_formula": dict(
                self.WEIGHTS
            ),
            "regime_strength": round(
                regime_strength,
                4,
            ),
            "trend_direction": round(
                trend_direction,
                4,
            ),
            "participation_direction": round(
                participation_direction,
                4,
            ),
            "momentum_direction": round(
                momentum_direction,
                4,
            ),
            "transition_probability": round(
                transition_probability,
                4,
            ),
            "component_scores": {
                "trend": round(trend, 4),
                "volatility": round(
                    volatility,
                    4,
                ),
                "liquidity": round(
                    liquidity,
                    4,
                ),
                "participation": round(
                    participation,
                    4,
                ),
                "momentum": round(
                    momentum,
                    4,
                ),
                "stability": round(
                    stability,
                    4,
                ),
            },
            "flow_scores": {
                "accumulation": round(
                    accumulation,
                    4,
                ),
                "distribution": round(
                    distribution,
                    4,
                ),
            },
            "risk_scores": {
                "risk_on": round(
                    risk_on,
                    4,
                ),
                "risk_off": round(
                    risk_off,
                    4,
                ),
            },
        }

        evidence = {
            "engine": self.VERSION,
            "symbol": resolved_symbol,
            "timestamp": str(
                resolved_timestamp
            ),
            "observed_fields": tuple(
                sorted(observed.keys())
            ),
            "derived_fields": tuple(
                sorted(derived.keys())
            ),
            "previous_regime": (
                previous.regime
                if previous is not None
                else None
            ),
        }

        assessment = RegimeAssessment(
            timestamp=str(
                resolved_timestamp
            ),
            symbol=resolved_symbol,
            regime=regime,
            regime_strength=round(
                regime_strength,
                4,
            ),
            confidence_score=round(
                confidence,
                4,
            ),
            stability_score=round(
                stability,
                4,
            ),
            transition_probability=round(
                transition_probability,
                4,
            ),
            trend_score=round(
                trend,
                4,
            ),
            volatility_score=round(
                volatility,
                4,
            ),
            liquidity_score=round(
                liquidity,
                4,
            ),
            participation_score=round(
                participation,
                4,
            ),
            momentum_score=round(
                momentum,
                4,
            ),
            accumulation_score=round(
                accumulation,
                4,
            ),
            distribution_score=round(
                distribution,
                4,
            ),
            risk_on_score=round(
                risk_on,
                4,
            ),
            risk_off_score=round(
                risk_off,
                4,
            ),
            contradiction=contradiction,
            contradiction_reasons=(
                contradiction_reasons
            ),
            observed=observed,
            derived=derived,
            evidence=evidence,
        )

        self._history.append(
            assessment
        )

        if len(self._history) > self.history_limit:
            del self._history[
                :len(self._history)
                - self.history_limit
            ]

        return assessment

    # ------------------------------------------------------------------
    # Memory / transition interface
    # ------------------------------------------------------------------

    def latest(
        self,
    ) -> Optional[RegimeAssessment]:
        return (
            self._history[-1]
            if self._history
            else None
        )

    def history(
        self,
        limit: Optional[int] = None,
    ) -> tuple[RegimeAssessment, ...]:
        if limit is None:
            return tuple(self._history)

        if limit < 1:
            return ()

        return tuple(
            self._history[-limit:]
        )

    def detect_transition(
        self,
    ) -> dict[str, Any]:
        if len(self._history) < 2:
            latest = self.latest()

            return {
                "transition": False,
                "from_regime": None,
                "to_regime": (
                    latest.regime
                    if latest
                    else None
                ),
                "probability": 0.0,
            }

        previous = self._history[-2]
        current = self._history[-1]

        return {
            "transition": (
                previous.regime
                != current.regime
            ),
            "from_regime": previous.regime,
            "to_regime": current.regime,
            "probability": current.transition_probability,
            "strength_change": round(
                current.regime_strength
                - previous.regime_strength,
                4,
            ),
            "stability_change": round(
                current.stability_score
                - previous.stability_score,
                4,
            ),
        }

    def regime_frequency(
        self,
        limit: Optional[int] = None,
    ) -> dict[str, int]:
        records = self.history(limit)
        frequency: dict[str, int] = {}

        for record in records:
            frequency[record.regime] = (
                frequency.get(
                    record.regime,
                    0,
                )
                + 1
            )

        return frequency

    def average_strength(
        self,
        limit: Optional[int] = None,
    ) -> float:
        records = self.history(limit)

        if not records:
            return 0.0

        return round(
            mean(
                record.regime_strength
                for record in records
            ),
            4,
        )

    def clear_history(self) -> None:
        self._history.clear()

    def health_check(self) -> dict[str, Any]:
        weight_sum = sum(
            self.WEIGHTS.values()
        )

        return {
            "engine": self.VERSION,
            "healthy": (
                abs(weight_sum - 1.0)
                < 1e-9
            ),
            "weight_sum": round(
                weight_sum,
                10,
            ),
            "history_size": len(
                self._history
            ),
            "history_limit": self.history_limit,
            "latest_available": (
                self.latest()
                is not None
            ),
        }


# Integration aliases.
RegimeEngine = RegimeIntelligence
MarketRegimeIntelligence = RegimeIntelligence


__all__ = [
    "RegimeAssessment",
    "RegimeIntelligence",
    "RegimeEngine",
    "MarketRegimeIntelligence",
]