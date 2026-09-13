from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from math import isfinite
from threading import RLock
from typing import Any, Mapping


@dataclass(frozen=True)
class CommitmentAssessment:
    symbol: str
    timeframe: str

    commitment_score: float

    capital_commitment: float
    time_commitment: float
    participation_commitment: float
    context_commitment: float

    data_quality: float
    regime_stability: float

    state: str
    confidence: float

    price_movement_only: bool
    suppression: bool

    reasons: tuple[str, ...] = ()
    risk_flags: tuple[str, ...] = ()
    evidence: dict[str, Any] = field(default_factory=dict)

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        scores = (
            self.commitment_score,
            self.capital_commitment,
            self.time_commitment,
            self.participation_commitment,
            self.context_commitment,
            self.data_quality,
            self.regime_stability,
            self.confidence,
        )

        for value in scores:
            if not isfinite(float(value)):
                raise ValueError("Commitment scores must be finite.")

        for value in scores:
            if not 0.0 <= float(value) <= 100.0:
                raise ValueError("Commitment scores must be between 0 and 100.")

        if not self.symbol:
            raise ValueError("symbol is required.")

        if not self.timeframe:
            raise ValueError("timeframe is required.")

        if not self.state:
            raise ValueError("state is required.")


class CommitmentEngine:
    """
    ROBOMLM Commitment Engine.

    Commitment is NOT inferred from price movement alone.

    Tested core model:

        C = (K × T × P × X) × Q × S

    where:

        K = Capital Commitment
        T = Time Commitment / persistence
        P = Participation Commitment
        X = Context Commitment
        Q = Data Quality
        S = Regime Stability

    All components are normalized to [0, 1] before multiplication.

    The multiplicative structure is intentional:
    weak/absent evidence in one critical dimension suppresses
    the final commitment instead of allowing strong values in
    unrelated dimensions to compensate for it.
    """

    VERSION = "ROBOMLM-COMMITMENT-1.0"

    MIN_FACTOR = 0.05
    COMMITTED_THRESHOLD = 70.0
    STRONG_THRESHOLD = 85.0
    PARTIAL_THRESHOLD = 50.0
    INSUFFICIENT_THRESHOLD = 30.0

    def __init__(self, max_history: int = 1000) -> None:
        if max_history < 1:
            raise ValueError("max_history must be >= 1.")

        self._history: list[CommitmentAssessment] = []
        self._max_history = max_history
        self._lock = RLock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def assess(
        self,
        data: Mapping[str, Any],
        *,
        symbol: str | None = None,
        timeframe: str | None = None,
    ) -> CommitmentAssessment:
        """
        Evaluate commitment from multi-dimensional evidence.

        Accepted aliases are deliberately broad so the engine can consume
        normalized evidence produced by different upstream ROBOMLM layers.
        """

        symbol_value = symbol or self._text(
            data,
            "symbol",
            "instrument",
            "ticker",
            default="UNKNOWN",
        )

        timeframe_value = timeframe or self._text(
            data,
            "timeframe",
            "interval",
            default="UNKNOWN",
        )

        capital = self._capital_commitment(data)
        persistence = self._time_commitment(data)
        participation = self._participation_commitment(data)
        context = self._context_commitment(data)

        quality = self._score(
            data,
            (
                "data_quality",
                "quality",
                "evidence_quality",
                "source_quality",
            ),
            default=100.0,
        )

        stability = self._score(
            data,
            (
                "regime_stability",
                "stability",
                "regime_confidence",
            ),
            default=100.0,
        )

        price_only = self._is_price_movement_only(
            data,
            capital,
            persistence,
            participation,
            context,
        )

        reasons: list[str] = []
        risk_flags: list[str] = []

        critical = {
            "capital": capital,
            "time": persistence,
            "participation": participation,
            "context": context,
        }

        weak_factors = [
            name
            for name, value in critical.items()
            if value <= self.MIN_FACTOR * 100.0
        ]

        if weak_factors:
            risk_flags.append(
                "critical_factor_near_zero:" + ",".join(weak_factors)
            )

        if price_only:
            risk_flags.append("price_movement_without_commitment_confirmation")
            reasons.append(
                "Price movement exists without sufficient capital, "
                "persistence, participation and context confirmation."
            )

        if capital >= 70.0:
            reasons.append("Capital flow confirms commitment.")
        elif capital < 40.0:
            reasons.append("Capital flow does not sufficiently confirm commitment.")

        if persistence >= 70.0:
            reasons.append("Time persistence confirms commitment.")
        elif persistence < 40.0:
            reasons.append("Time persistence is insufficient.")

        if participation >= 70.0:
            reasons.append("Participation confirms commitment.")
        elif participation < 40.0:
            reasons.append("Participation is insufficient.")

        if context >= 70.0:
            reasons.append("Context alignment confirms commitment.")
        elif context < 40.0:
            reasons.append("Context alignment is weak.")

        if quality < 50.0:
            risk_flags.append("low_data_quality")

        if stability < 50.0:
            risk_flags.append("low_regime_stability")

        # --------------------------------------------------------------
        # Tested multiplicative commitment model
        # --------------------------------------------------------------
        raw_commitment = (
            (capital / 100.0)
            * (persistence / 100.0)
            * (participation / 100.0)
            * (context / 100.0)
            * (quality / 100.0)
            * (stability / 100.0)
        )

        commitment_score = raw_commitment * 100.0

        # Price movement alone can never create commitment.
        if price_only:
            commitment_score = min(
                commitment_score,
                min(
                    capital,
                    persistence,
                    participation,
                    context,
                ),
            )

        suppression = (
            price_only
            or any(
                value <= self.MIN_FACTOR * 100.0
                for value in (
                    capital,
                    persistence,
                    participation,
                    context,
                    quality,
                    stability,
                )
            )
        )

        if suppression:
            commitment_score *= 0.50
            reasons.append("Commitment score suppressed by insufficient evidence.")

        state = self._classify(commitment_score, suppression)

        # Confidence is evidence quality + dimensional agreement,
        # not a replacement for commitment_score.
        dimensional_mean = (
            capital
            + persistence
            + participation
            + context
        ) / 4.0

        dimensional_min = min(
            capital,
            persistence,
            participation,
            context,
        )

        confidence = (
            dimensional_mean * 0.50
            + dimensional_min * 0.20
            + quality * 0.15
            + stability * 0.15
        )

        if suppression:
            confidence *= 0.70

        confidence = self._clamp(confidence)

        evidence = {
            "engine": self.VERSION,
            "formula": "C=(K*T*P*X)*Q*S",
            "capital": capital,
            "time": persistence,
            "participation": participation,
            "context": context,
            "data_quality": quality,
            "regime_stability": stability,
            "raw_commitment": commitment_score,
            "price_movement_only": price_only,
            "suppression": suppression,
            "critical_factors": {
                "capital": capital,
                "time": persistence,
                "participation": participation,
                "context": context,
            },
        }

        assessment = CommitmentAssessment(
            symbol=symbol_value,
            timeframe=timeframe_value,
            commitment_score=self._clamp(commitment_score),
            capital_commitment=capital,
            time_commitment=persistence,
            participation_commitment=participation,
            context_commitment=context,
            data_quality=quality,
            regime_stability=stability,
            state=state,
            confidence=confidence,
            price_movement_only=price_only,
            suppression=suppression,
            reasons=tuple(dict.fromkeys(reasons)),
            risk_flags=tuple(dict.fromkeys(risk_flags)),
            evidence=evidence,
        )

        with self._lock:
            self._history.append(assessment)
            if len(self._history) > self._max_history:
                self._history = self._history[-self._max_history :]

        return assessment

    def history(self) -> tuple[CommitmentAssessment, ...]:
        with self._lock:
            return tuple(self._history)

    def clear_history(self) -> None:
        with self._lock:
            self._history.clear()

    def average_score(self) -> float:
        with self._lock:
            if not self._history:
                return 0.0
            return sum(
                item.commitment_score for item in self._history
            ) / len(self._history)

    def health_check(self) -> dict[str, Any]:
        with self._lock:
            history_count = len(self._history)

        return {
            "engine": self.VERSION,
            "status": "healthy",
            "formula": "C=(K*T*P*X)*Q*S",
            "history_count": history_count,
            "thresholds": {
                "strong": self.STRONG_THRESHOLD,
                "committed": self.COMMITTED_THRESHOLD,
                "partial": self.PARTIAL_THRESHOLD,
                "insufficient": self.INSUFFICIENT_THRESHOLD,
            },
            "critical_dimensions": [
                "capital_commitment",
                "time_commitment",
                "participation_commitment",
                "context_commitment",
            ],
        }

    # ------------------------------------------------------------------
    # Commitment dimensions
    # ------------------------------------------------------------------

    def _capital_commitment(self, data: Mapping[str, Any]) -> float:
        direct = self._score(
            data,
            (
                "capital_commitment",
                "capital_flow_score",
                "capital_flow",
                "money_flow",
            ),
            default=None,
        )

        if direct is not None:
            return direct

        inflow = self._number(
            data,
            "inflow",
            "capital_inflow",
            "net_inflow",
            "buying_flow",
            default=0.0,
        )

        outflow = self._number(
            data,
            "outflow",
            "capital_outflow",
            "net_outflow",
            "selling_flow",
            default=0.0,
        )

        total = abs(inflow) + abs(outflow)

        if total <= 0.0:
            return 0.0

        directional_flow = abs(inflow - outflow) / total

        return self._clamp(directional_flow * 100.0)

    def _time_commitment(self, data: Mapping[str, Any]) -> float:
        direct = self._score(
            data,
            (
                "time_commitment",
                "persistence_score",
                "persistence",
                "time_persistence",
            ),
            default=None,
        )

        if direct is not None:
            return direct

        observed = self._number(
            data,
            "persistence_bars",
            "confirmed_bars",
            "holding_bars",
            "duration_bars",
            default=0.0,
        )

        required = self._number(
            data,
            "required_persistence_bars",
            "minimum_persistence_bars",
            default=5.0,
        )

        if required <= 0.0:
            return 0.0

        return self._clamp((observed / required) * 100.0)

    def _participation_commitment(self, data: Mapping[str, Any]) -> float:
        direct = self._score(
            data,
            (
                "participation_commitment",
                "participation_score",
                "participation",
                "breadth_score",
            ),
            default=None,
        )

        if direct is not None:
            return direct

        participants = self._number(
            data,
            "active_participants",
            "participating_entities",
            "confirmed_participants",
            default=0.0,
        )

        total = self._number(
            data,
            "total_participants",
            "eligible_participants",
            default=0.0,
        )

        if total > 0.0:
            return self._clamp((participants / total) * 100.0)

        breadth = self._score(
            data,
            ("breadth", "market_breadth", "participation_breadth"),
            default=0.0,
        )

        volume_confirmation = self._score(
            data,
            (
                "volume_confirmation",
                "participation_volume_confirmation",
            ),
            default=breadth,
        )

        return self._clamp(
            breadth * 0.50
            + volume_confirmation * 0.50
        )

    def _context_commitment(self, data: Mapping[str, Any]) -> float:
        direct = self._score(
            data,
            (
                "context_commitment",
                "context_alignment",
                "alignment_score",
                "context_score",
            ),
            default=None,
        )

        if direct is not None:
            return direct

        trend = self._score(
            data,
            ("trend_alignment", "trend_score"),
            default=0.0,
        )

        regime = self._score(
            data,
            ("regime_alignment", "regime_score"),
            default=0.0,
        )

        liquidity = self._score(
            data,
            ("liquidity_alignment", "liquidity_score"),
            default=0.0,
        )

        return self._clamp(
            trend * 0.40
            + regime * 0.35
            + liquidity * 0.25
        )

    # ------------------------------------------------------------------
    # Validation / interpretation
    # ------------------------------------------------------------------

    def _is_price_movement_only(
        self,
        data: Mapping[str, Any],
        capital: float,
        persistence: float,
        participation: float,
        context: float,
    ) -> bool:
        price_change_present = any(
            key in data
            for key in (
                "price_change",
                "price_change_pct",
                "return",
                "move_pct",
                "momentum",
            )
        )

        if not price_change_present:
            return False

        confirmation = (
            capital >= 40.0
            or persistence >= 40.0
            or participation >= 40.0
            or context >= 40.0
        )

        return not confirmation

    def _classify(self, score: float, suppression: bool) -> str:
        if suppression and score < self.PARTIAL_THRESHOLD:
            return "INSUFFICIENT"

        if score >= self.STRONG_THRESHOLD:
            return "STRONG_COMMITMENT"

        if score >= self.COMMITTED_THRESHOLD:
            return "COMMITTED"

        if score >= self.PARTIAL_THRESHOLD:
            return "PARTIAL_COMMITMENT"

        if score >= self.INSUFFICIENT_THRESHOLD:
            return "WEAK_COMMITMENT"

        return "INSUFFICIENT"

    # ------------------------------------------------------------------
    # Input helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _score(
        data: Mapping[str, Any],
        keys: tuple[str, ...],
        default: float | None,
    ) -> float | None:
        for key in keys:
            if key not in data:
                continue

            value = data[key]

            if isinstance(value, Mapping):
                for nested_key in ("score", "value", "normalized", "percentage"):
                    if nested_key in value:
                        value = value[nested_key]
                        break

            try:
                number = float(value)
            except (TypeError, ValueError):
                continue

            if not isfinite(number):
                continue

            # Accept normalized 0..1 inputs.
            if 0.0 <= number <= 1.0:
                number *= 100.0

            return CommitmentEngine._clamp(number)

        return default

    @staticmethod
    def _number(
        data: Mapping[str, Any],
        *keys: str,
        default: float = 0.0,
    ) -> float:
        for key in keys:
            if key not in data:
                continue

            try:
                value = float(data[key])
            except (TypeError, ValueError):
                continue

            if isfinite(value):
                return value

        return default

    @staticmethod
    def _text(
        data: Mapping[str, Any],
        *keys: str,
        default: str,
    ) -> str:
        for key in keys:
            value = data.get(key)
            if value is not None and str(value).strip():
                return str(value).strip()

        return default

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(100.0, float(value)))


__all__ = [
    "CommitmentAssessment",
    "CommitmentEngine",
]