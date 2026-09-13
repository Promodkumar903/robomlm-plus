from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from statistics import mean
from typing import Any, Mapping


class StrategyName(str, Enum):
    TREND_FOLLOWING = "TREND_FOLLOWING"
    MEAN_REVERSION = "MEAN_REVERSION"
    BREAKOUT = "BREAKOUT"
    MOMENTUM = "MOMENTUM"
    RANGE = "RANGE"
    SCALPING = "SCALPING"
    SWING = "SWING"
    CUSTOM = "CUSTOM"


class StrategyFitState(str, Enum):
    INSUFFICIENT = "INSUFFICIENT"
    POOR_FIT = "POOR_FIT"
    PARTIAL_FIT = "PARTIAL_FIT"
    GOOD_FIT = "GOOD_FIT"
    STRONG_FIT = "STRONG_FIT"
    CONFLICTED = "CONFLICTED"


@dataclass(frozen=True)
class StrategyAssessment:
    strategy: str
    fit_score: float
    state: str
    trend_fit: float
    regime_fit: float
    timing_fit: float
    volatility_fit: float
    liquidity_fit: float
    risk_fit: float
    confirmation_fit: float
    directional_bias: str
    confidence: float
    decision_ready: bool
    contradictions: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()
    risk_flags: tuple[str, ...] = ()
    evidence: Mapping[str, Any] = field(default_factory=dict)
    timestamp: str = ""


class StrategyIntelligence:
    """
    ROBOMLM Strategy Intelligence Engine.

    Purpose:
        Determine how well a selected strategy fits the current
        market context without executing trades.

    Core fit model:

        S =
            TF * 0.20
          + RF * 0.20
          + TM * 0.15
          + VF * 0.15
          + LF * 0.10
          + RK * 0.10
          + CF * 0.10

    Where:
        TF = Trend Fit
        RF = Regime Fit
        TM = Timing Fit
        VF = Volatility Fit
        LF = Liquidity Fit
        RK = Risk Fit
        CF = Confirmation Fit

    Hard protection:
        - insufficient evidence cannot become actionable
        - weak risk fit blocks readiness
        - weak liquidity fit blocks readiness
        - directional conflicts block readiness
        - strategy/regime contradiction is explicitly retained
        - no execution, authorization, broker or position mutation
    """

    VERSION = "ROBOMLM-STRATEGY-2.0"

    WEIGHTS = {
        "trend_fit": 0.20,
        "regime_fit": 0.20,
        "timing_fit": 0.15,
        "volatility_fit": 0.15,
        "liquidity_fit": 0.10,
        "risk_fit": 0.10,
        "confirmation_fit": 0.10,
    }

    STRONG_THRESHOLD = 85.0
    GOOD_THRESHOLD = 70.0
    PARTIAL_THRESHOLD = 55.0
    POOR_THRESHOLD = 35.0

    MIN_RISK_FIT = 40.0
    MIN_LIQUIDITY_FIT = 30.0
    MIN_CONFIRMATION = 35.0
    MIN_DECISION_SCORE = 70.0

    def __init__(self) -> None:
        self._history: list[StrategyAssessment] = []

    # ------------------------------------------------------------------
    # Generic extraction
    # ------------------------------------------------------------------

    @staticmethod
    def _value(
        data: Mapping[str, Any] | None,
        *keys: str,
        default: Any = None,
    ) -> Any:
        if not data:
            return default

        for key in keys:
            if key in data and data[key] is not None:
                return data[key]

        return default

    @staticmethod
    def _number(value: Any, default: float = 0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @classmethod
    def _score(cls, value: Any, default: float = 0.0) -> float:
        """
        Normalize score-like values to 0..100.

        Accepted:
            0..100 score directly
            -1..1 directional/correlation-like value -> mapped to 0..100
        """
        number = cls._number(value, default)

        if -1.0 <= number <= 1.0:
            if number < 0.0:
                number = (number + 1.0) * 50.0
            else:
                number *= 100.0

        return max(0.0, min(100.0, number))

    @staticmethod
    def _text(value: Any) -> str:
        if value is None:
            return ""
        return str(value).strip().upper()

    # ------------------------------------------------------------------
    # Strategy-specific trend fit
    # ------------------------------------------------------------------

    def _trend_fit(
        self,
        strategy: str,
        context: Mapping[str, Any],
    ) -> float:
        explicit = self._value(
            context,
            "trend_fit",
            "trend_score",
            default=None,
        )
        if explicit is not None:
            return self._score(explicit)

        trend = self._score(
            self._value(
                context,
                "trend_strength",
                "trend_score",
                "trend",
                default=50.0,
            ),
            50.0,
        )

        trend_direction = self._text(
            self._value(
                context,
                "trend_direction",
                "direction",
                "bias",
                default="",
            )
        )

        if strategy in {
            StrategyName.TREND_FOLLOWING.value,
            StrategyName.MOMENTUM.value,
            StrategyName.BREAKOUT.value,
            StrategyName.SWING.value,
        }:
            return trend

        if strategy == StrategyName.SCALPING.value:
            return min(100.0, trend * 0.70 + 30.0)

        if strategy in {
            StrategyName.MEAN_REVERSION.value,
            StrategyName.RANGE.value,
        }:
            return 100.0 - trend

        if strategy == StrategyName.CUSTOM.value:
            return trend

        if trend_direction in {"UP", "DOWN", "BULLISH", "BEARISH"}:
            return trend

        return 50.0

    # ------------------------------------------------------------------
    # Regime fit
    # ------------------------------------------------------------------

    def _regime_fit(
        self,
        strategy: str,
        context: Mapping[str, Any],
    ) -> float:
        explicit = self._value(
            context,
            "regime_fit",
            default=None,
        )
        if explicit is not None:
            return self._score(explicit)

        regime = self._text(
            self._value(
                context,
                "regime",
                "market_regime",
                "regime_state",
                default="",
            )
        )

        mapping: dict[str, set[str]] = {
            StrategyName.TREND_FOLLOWING.value: {
                "TRENDING",
                "EXPANSION",
                "RISK_ON",
                "RISK_OFF",
            },
            StrategyName.MOMENTUM.value: {
                "TRENDING",
                "EXPANSION",
            },
            StrategyName.BREAKOUT.value: {
                "EXPANSION",
                "COMPRESSION",
                "TRENDING",
            },
            StrategyName.MEAN_REVERSION.value: {
                "RANGING",
                "COMPRESSION",
            },
            StrategyName.RANGE.value: {
                "RANGING",
                "COMPRESSION",
            },
            StrategyName.SCALPING.value: {
                "TRENDING",
                "RANGING",
                "EXPANSION",
            },
            StrategyName.SWING.value: {
                "TRENDING",
                "EXPANSION",
                "ACCUMULATION",
                "DISTRIBUTION",
            },
            StrategyName.CUSTOM.value: {
                "TRENDING",
                "RANGING",
                "EXPANSION",
                "COMPRESSION",
                "ACCUMULATION",
                "DISTRIBUTION",
                "RISK_ON",
                "RISK_OFF",
            },
        }

        if not regime:
            return 50.0

        if regime in mapping.get(strategy, set()):
            return 90.0

        if regime in {"TRANSITION", "MIXED"}:
            return 45.0

        if regime == "INSUFFICIENT":
            return 20.0

        return 30.0

    # ------------------------------------------------------------------
    # Timing fit
    # ------------------------------------------------------------------

    def _timing_fit(
        self,
        strategy: str,
        context: Mapping[str, Any],
    ) -> float:
        explicit = self._value(
            context,
            "timing_fit",
            "timing_score",
            default=None,
        )
        if explicit is not None:
            return self._score(explicit)

        timing = self._score(
            self._value(
                context,
                "timing_quality",
                "timing_score",
                "timing",
                default=50.0,
            ),
            50.0,
        )

        session = self._text(
            self._value(
                context,
                "session",
                "market_session",
                default="",
            )
        )

        if strategy == StrategyName.SCALPING.value:
            if session in {"OPEN", "OVERLAP", "ACTIVE"}:
                return min(100.0, timing + 10.0)

        if strategy == StrategyName.SWING.value:
            if session in {"OPEN", "CLOSE"}:
                return min(100.0, timing + 5.0)

        return timing

    # ------------------------------------------------------------------
    # Volatility fit
    # ------------------------------------------------------------------

    def _volatility_fit(
        self,
        strategy: str,
        context: Mapping[str, Any],
    ) -> float:
        explicit = self._value(
            context,
            "volatility_fit",
            default=None,
        )
        if explicit is not None:
            return self._score(explicit)

        volatility = self._score(
            self._value(
                context,
                "volatility_score",
                "volatility",
                default=50.0,
            ),
            50.0,
        )

        if strategy in {
            StrategyName.BREAKOUT.value,
            StrategyName.MOMENTUM.value,
        }:
            return volatility

        if strategy == StrategyName.MEAN_REVERSION.value:
            distance = abs(volatility - 50.0)
            return max(0.0, 100.0 - distance)

        if strategy == StrategyName.RANGE.value:
            return max(0.0, 100.0 - volatility)

        if strategy == StrategyName.SCALPING.value:
            return max(0.0, 100.0 - abs(volatility - 60.0))

        if strategy == StrategyName.SWING.value:
            return max(0.0, 100.0 - abs(volatility - 60.0))

        return volatility

    # ------------------------------------------------------------------
    # Liquidity fit
    # ------------------------------------------------------------------

    def _liquidity_fit(
        self,
        context: Mapping[str, Any],
    ) -> float:
        explicit = self._value(
            context,
            "liquidity_fit",
            "liquidity_score",
            default=None,
        )
        if explicit is not None:
            return self._score(explicit)

        return self._score(
            self._value(
                context,
                "liquidity_quality",
                "liquidity",
                default=50.0,
            ),
            50.0,
        )

    # ------------------------------------------------------------------
    # Risk fit
    # ------------------------------------------------------------------

    def _risk_fit(
        self,
        context: Mapping[str, Any],
    ) -> float:
        explicit = self._value(
            context,
            "risk_fit",
            "risk_score",
            default=None,
        )
        if explicit is not None:
            return self._score(explicit)

        risk_quality = self._value(
            context,
            "risk_quality",
            default=None,
        )

        if risk_quality is not None:
            return self._score(risk_quality)

        raw_risk = self._value(
            context,
            "risk",
            "risk_level",
            default=50.0,
        )

        return 100.0 - self._score(raw_risk, 50.0)

    # ------------------------------------------------------------------
    # Confirmation fit
    # ------------------------------------------------------------------

    def _confirmation_fit(
        self,
        context: Mapping[str, Any],
    ) -> float:
        explicit = self._value(
            context,
            "confirmation_fit",
            "confirmation_score",
            default=None,
        )
        if explicit is not None:
            return self._score(explicit)

        values: list[float] = []

        for key in (
            "evidence_score",
            "context_score",
            "intelligence_score",
            "commitment_score",
            "relationship_score",
        ):
            value = self._value(context, key, default=None)
            if value is not None:
                values.append(self._score(value))

        if not values:
            return 50.0

        return sum(values) / len(values)

    # ------------------------------------------------------------------
    # Directional logic
    # ------------------------------------------------------------------

    @staticmethod
    def _direction(value: Any) -> str:
        text = str(value).strip().upper() if value is not None else ""

        if text in {"BUY", "LONG", "UP", "BULLISH"}:
            return "BUY"

        if text in {"SELL", "SHORT", "DOWN", "BEARISH"}:
            return "SELL"

        if text in {"HOLD", "NEUTRAL", "FLAT", ""}:
            return "NEUTRAL"

        return text

    def _directional_bias(
        self,
        context: Mapping[str, Any],
    ) -> str:
        directions: list[str] = []

        for key in (
            "trend_direction",
            "direction",
            "bias",
            "intelligence_bias",
            "relationship_bias",
            "commitment_bias",
        ):
            value = self._value(context, key, default=None)
            if value is not None:
                direction = self._direction(value)
                if direction in {"BUY", "SELL"}:
                    directions.append(direction)

        if not directions:
            return "NEUTRAL"

        buys = directions.count("BUY")
        sells = directions.count("SELL")

        if buys > sells:
            return "BUY"

        if sells > buys:
            return "SELL"

        return "CONFLICTED"

    # ------------------------------------------------------------------
    # Contradiction detection
    # ------------------------------------------------------------------

    def _contradictions(
        self,
        strategy: str,
        context: Mapping[str, Any],
        components: Mapping[str, float],
    ) -> list[str]:
        contradictions: list[str] = []

        regime = self._text(
            self._value(
                context,
                "regime",
                "market_regime",
                "regime_state",
                default="",
            )
        )

        trend = components["trend_fit"]
        regime_fit = components["regime_fit"]
        risk = components["risk_fit"]
        liquidity = components["liquidity_fit"]
        confirmation = components["confirmation_fit"]

        if strategy in {
            StrategyName.TREND_FOLLOWING.value,
            StrategyName.MOMENTUM.value,
            StrategyName.BREAKOUT.value,
        }:
            if trend < 35.0:
                contradictions.append("trend_strategy_without_sufficient_trend")

        if strategy in {
            StrategyName.MEAN_REVERSION.value,
            StrategyName.RANGE.value,
        }:
            if trend > 75.0:
                contradictions.append("mean_reversion_against_strong_trend")

        if regime in {"TRANSITION", "MIXED"} and regime_fit < 50.0:
            contradictions.append("unstable_market_regime")

        if risk < self.MIN_RISK_FIT:
            contradictions.append("risk_fit_below_minimum")

        if liquidity < self.MIN_LIQUIDITY_FIT:
            contradictions.append("liquidity_fit_below_minimum")

        if confirmation < self.MIN_CONFIRMATION:
            contradictions.append("confirmation_below_minimum")

        explicit_conflict = self._value(
            context,
            "conflicted",
            "directional_conflict",
            "contradiction",
            default=False,
        )

        if bool(explicit_conflict):
            contradictions.append("upstream_directional_conflict")

        return contradictions

    # ------------------------------------------------------------------
    # Composite score
    # ------------------------------------------------------------------

    def calculate_fit(
        self,
        *,
        trend_fit: float,
        regime_fit: float,
        timing_fit: float,
        volatility_fit: float,
        liquidity_fit: float,
        risk_fit: float,
        confirmation_fit: float,
    ) -> float:
        score = (
            trend_fit * self.WEIGHTS["trend_fit"]
            + regime_fit * self.WEIGHTS["regime_fit"]
            + timing_fit * self.WEIGHTS["timing_fit"]
            + volatility_fit * self.WEIGHTS["volatility_fit"]
            + liquidity_fit * self.WEIGHTS["liquidity_fit"]
            + risk_fit * self.WEIGHTS["risk_fit"]
            + confirmation_fit * self.WEIGHTS["confirmation_fit"]
        )

        return round(max(0.0, min(100.0, score)), 4)

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------

    def classify(
        self,
        score: float,
        contradictions: list[str],
    ) -> StrategyFitState:
        if contradictions:
            return StrategyFitState.CONFLICTED

        if score >= self.STRONG_THRESHOLD:
            return StrategyFitState.STRONG_FIT

        if score >= self.GOOD_THRESHOLD:
            return StrategyFitState.GOOD_FIT

        if score >= self.PARTIAL_THRESHOLD:
            return StrategyFitState.PARTIAL_FIT

        if score >= self.POOR_THRESHOLD:
            return StrategyFitState.POOR_FIT

        return StrategyFitState.INSUFFICIENT

    # ------------------------------------------------------------------
    # Confidence
    # ------------------------------------------------------------------

    def _confidence(
        self,
        components: Mapping[str, float],
        score: float,
        contradictions: list[str],
    ) -> float:
        values = list(components.values())

        if not values:
            return 0.0

        average = mean(values)
        minimum = min(values)
        spread = max(values) - min(values)

        confidence = (
            average * 0.50
            + minimum * 0.30
            + score * 0.20
        )

        if spread > 60.0:
            confidence -= 15.0
        elif spread > 40.0:
            confidence -= 8.0

        confidence -= len(contradictions) * 10.0

        return round(max(0.0, min(100.0, confidence)), 4)

    # ------------------------------------------------------------------
    # Assessment
    # ------------------------------------------------------------------

    def assess(
        self,
        strategy: str | StrategyName,
        context: Mapping[str, Any] | None = None,
    ) -> StrategyAssessment:
        context = dict(context or {})

        if isinstance(strategy, StrategyName):
            strategy_name = strategy.value
        else:
            strategy_name = self._text(strategy)

        valid_names = {item.value for item in StrategyName}

        if strategy_name not in valid_names:
            raise ValueError(
                f"Unsupported strategy: {strategy_name}. "
                f"Supported: {sorted(valid_names)}"
            )

        evidence_score = self._score(
            self._value(
                context,
                "evidence_score",
                "evidence_quality",
                default=50.0,
            ),
            50.0,
        )

        trend_fit = self._trend_fit(strategy_name, context)
        regime_fit = self._regime_fit(strategy_name, context)
        timing_fit = self._timing_fit(strategy_name, context)
        volatility_fit = self._volatility_fit(strategy_name, context)
        liquidity_fit = self._liquidity_fit(context)
        risk_fit = self._risk_fit(context)
        confirmation_fit = self._confirmation_fit(context)

        components = {
            "trend_fit": trend_fit,
            "regime_fit": regime_fit,
            "timing_fit": timing_fit,
            "volatility_fit": volatility_fit,
            "liquidity_fit": liquidity_fit,
            "risk_fit": risk_fit,
            "confirmation_fit": confirmation_fit,
        }

        score = self.calculate_fit(**components)

        contradictions = self._contradictions(
            strategy_name,
            context,
            components,
        )

        state = self.classify(score, contradictions)

        directional_bias = self._directional_bias(context)

        if directional_bias == "CONFLICTED":
            contradictions.append("directional_bias_conflict")
            state = StrategyFitState.CONFLICTED

        confidence = self._confidence(
            components,
            score,
            contradictions,
        )

        evidence_sufficient = evidence_score >= 40.0

        decision_ready = (
            score >= self.MIN_DECISION_SCORE
            and evidence_sufficient
            and risk_fit >= self.MIN_RISK_FIT
            and liquidity_fit >= self.MIN_LIQUIDITY_FIT
            and confirmation_fit >= self.MIN_CONFIRMATION
            and not contradictions
            and directional_bias in {"BUY", "SELL", "NEUTRAL"}
        )

        reasons: list[str] = []

        if trend_fit >= 70.0:
            reasons.append("trend_structure_supports_strategy")
        elif trend_fit < 35.0:
            reasons.append("trend_structure_weak_for_strategy")

        if regime_fit >= 70.0:
            reasons.append("market_regime_supports_strategy")
        elif regime_fit < 40.0:
            reasons.append("market_regime_misaligned")

        if timing_fit >= 70.0:
            reasons.append("timing_window_supportive")

        if volatility_fit >= 70.0:
            reasons.append("volatility_profile_supportive")

        if liquidity_fit >= 70.0:
            reasons.append("liquidity_supportive")
        elif liquidity_fit < self.MIN_LIQUIDITY_FIT:
            reasons.append("liquidity_is_a_material_constraint")

        if risk_fit >= 70.0:
            reasons.append("risk_profile_supportive")
        elif risk_fit < self.MIN_RISK_FIT:
            reasons.append("risk_profile_blocks_readiness")

        if confirmation_fit >= 70.0:
            reasons.append("cross_dimension_confirmation_supportive")
        elif confirmation_fit < self.MIN_CONFIRMATION:
            reasons.append("confirmation_is_insufficient")

        risk_flags: list[str] = []

        if evidence_score < 40.0:
            risk_flags.append("INSUFFICIENT_EVIDENCE")

        if risk_fit < self.MIN_RISK_FIT:
            risk_flags.append("LOW_RISK_FIT")

        if liquidity_fit < self.MIN_LIQUIDITY_FIT:
            risk_flags.append("LOW_LIQUIDITY_FIT")

        if contradictions:
            risk_flags.append("STRATEGY_CONTRADICTION")

        if directional_bias == "CONFLICTED":
            risk_flags.append("DIRECTIONAL_CONFLICT")

        timestamp = datetime.now(timezone.utc).isoformat()

        assessment = StrategyAssessment(
            strategy=strategy_name,
            fit_score=score,
            state=state.value,
            trend_fit=round(trend_fit, 4),
            regime_fit=round(regime_fit, 4),
            timing_fit=round(timing_fit, 4),
            volatility_fit=round(volatility_fit, 4),
            liquidity_fit=round(liquidity_fit, 4),
            risk_fit=round(risk_fit, 4),
            confirmation_fit=round(confirmation_fit, 4),
            directional_bias=directional_bias,
            confidence=confidence,
            decision_ready=decision_ready,
            contradictions=tuple(dict.fromkeys(contradictions)),
            reasons=tuple(dict.fromkeys(reasons)),
            risk_flags=tuple(dict.fromkeys(risk_flags)),
            evidence={
                "strategy": strategy_name,
                "evidence_score": round(evidence_score, 4),
                "components": dict(components),
                "weights": dict(self.WEIGHTS),
                "formula": (
                    "S = TF*0.20 + RF*0.20 + TM*0.15 + "
                    "VF*0.15 + LF*0.10 + RK*0.10 + CF*0.10"
                ),
            },
            timestamp=timestamp,
        )

        self._history.append(assessment)

        return assessment

    # ------------------------------------------------------------------
    # History / memory
    # ------------------------------------------------------------------

    @property
    def history(self) -> tuple[StrategyAssessment, ...]:
        return tuple(self._history)

    @property
    def latest(self) -> StrategyAssessment | None:
        return self._history[-1] if self._history else None

    def average_score(self) -> float:
        if not self._history:
            return 0.0

        return round(
            mean(item.fit_score for item in self._history),
            4,
        )

    def strategy_history(
        self,
        strategy: str | StrategyName,
    ) -> tuple[StrategyAssessment, ...]:
        name = (
            strategy.value
            if isinstance(strategy, StrategyName)
            else self._text(strategy)
        )

        return tuple(
            item
            for item in self._history
            if item.strategy == name
        )

    def clear(self) -> None:
        self._history.clear()

    # ------------------------------------------------------------------
    # Health / validation
    # ------------------------------------------------------------------

    def health_check(self) -> dict[str, Any]:
        formula_weight_sum = sum(self.WEIGHTS.values())

        return {
            "engine": "StrategyIntelligence",
            "version": self.VERSION,
            "healthy": abs(formula_weight_sum - 1.0) < 1e-9,
            "history_size": len(self._history),
            "weight_sum": formula_weight_sum,
            "thresholds": {
                "strong": self.STRONG_THRESHOLD,
                "good": self.GOOD_THRESHOLD,
                "partial": self.PARTIAL_THRESHOLD,
                "poor": self.POOR_THRESHOLD,
            },
            "gates": {
                "minimum_risk_fit": self.MIN_RISK_FIT,
                "minimum_liquidity_fit": self.MIN_LIQUIDITY_FIT,
                "minimum_confirmation": self.MIN_CONFIRMATION,
                "minimum_decision_score": self.MIN_DECISION_SCORE,
            },
        }


# Compatibility aliases used by higher-level ROBOMLM modules.
StrategyEngine = StrategyIntelligence
MarketStrategyIntelligence = StrategyIntelligence


__all__ = [
    "StrategyName",
    "StrategyFitState",
    "StrategyAssessment",
    "StrategyIntelligence",
    "StrategyEngine",
    "MarketStrategyIntelligence",
]