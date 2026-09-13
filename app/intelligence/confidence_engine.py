from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from math import isfinite
from threading import RLock
from typing import Any, Mapping


@dataclass(frozen=True)
class ConfidenceAssessment:
    symbol: str
    timeframe: str
    confidence_score: float

    evidence_quality: float
    signal_alignment: float
    data_quality: float
    source_reliability: float
    context_alignment: float
    timing_quality: float

    state: str
    confidence_band: str
    suppression: bool

    reasons: tuple[str, ...] = ()
    risk_flags: tuple[str, ...] = ()
    evidence: dict[str, Any] = field(default_factory=dict)

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        values = (
            self.confidence_score,
            self.evidence_quality,
            self.signal_alignment,
            self.data_quality,
            self.source_reliability,
            self.context_alignment,
            self.timing_quality,
        )

        for value in values:
            if not isfinite(float(value)):
                raise ValueError("Confidence values must be finite.")
            if not 0.0 <= float(value) <= 100.0:
                raise ValueError(
                    "Confidence values must be between 0 and 100."
                )

        if not self.symbol:
            raise ValueError("symbol is required.")

        if not self.timeframe:
            raise ValueError("timeframe is required.")


class ConfidenceEngine:
    """
    ROBOMLM Confidence Engine.

    Confidence answers:

        "How strongly does the available evidence support the
         current intelligence interpretation?"

    It does NOT answer:

        "Should ROBOMLM execute?"

    Execution remains downstream of Decision, Risk, Authorization
    and Automation controls.

    Confidence model:

        C = EQ*0.25
          + SA*0.20
          + DQ*0.15
          + SR*0.15
          + CA*0.15
          + TQ*0.10

    EQ = Evidence Quality
    SA = Signal Alignment
    DQ = Data Quality
    SR = Source Reliability
    CA = Context Alignment
    TQ = Timing Quality

    Critical weakness suppression is applied when the evidence base
    is structurally weak. This prevents one strong dimension from
    masking a serious information-quality failure.
    """

    VERSION = "ROBOMLM-CONFIDENCE-1.0"

    WEIGHTS = {
        "evidence_quality": 0.25,
        "signal_alignment": 0.20,
        "data_quality": 0.15,
        "source_reliability": 0.15,
        "context_alignment": 0.15,
        "timing_quality": 0.10,
    }

    HIGH_THRESHOLD = 85.0
    RELIABLE_THRESHOLD = 70.0
    PARTIAL_THRESHOLD = 50.0
    WEAK_THRESHOLD = 30.0

    CRITICAL_MINIMUM = 20.0

    def __init__(self, max_history: int = 1000) -> None:
        if max_history < 1:
            raise ValueError("max_history must be >= 1.")

        self._history: list[ConfidenceAssessment] = []
        self._max_history = max_history
        self._lock = RLock()

    # ================================================================
    # PUBLIC API
    # ================================================================

    def assess(
        self,
        data: Mapping[str, Any],
        *,
        symbol: str | None = None,
        timeframe: str | None = None,
    ) -> ConfidenceAssessment:

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

        evidence_quality = self._dimension(
            data,
            (
                "evidence_quality",
                "evidence_score",
                "evidence_strength",
            ),
        )

        signal_alignment = self._dimension(
            data,
            (
                "signal_alignment",
                "signal_agreement",
                "directional_alignment",
                "alignment_score",
            ),
        )

        data_quality = self._dimension(
            data,
            (
                "data_quality",
                "market_data_quality",
                "data_integrity",
            ),
        )

        source_reliability = self._dimension(
            data,
            (
                "source_reliability",
                "source_quality",
                "reliability_score",
            ),
        )

        context_alignment = self._dimension(
            data,
            (
                "context_alignment",
                "context_score",
                "market_context_score",
            ),
        )

        timing_quality = self._dimension(
            data,
            (
                "timing_quality",
                "timing_score",
                "timing_alignment",
            ),
        )

        values = {
            "evidence_quality": evidence_quality,
            "signal_alignment": signal_alignment,
            "data_quality": data_quality,
            "source_reliability": source_reliability,
            "context_alignment": context_alignment,
            "timing_quality": timing_quality,
        }

        reasons: list[str] = []
        risk_flags: list[str] = []

        # ------------------------------------------------------------
        # Core weighted confidence model
        # ------------------------------------------------------------

        confidence_score = sum(
            values[name] * self.WEIGHTS[name]
            for name in self.WEIGHTS
        )

        # ------------------------------------------------------------
        # Structural weakness detection
        # ------------------------------------------------------------

        critical_weak = [
            name
            for name, value in values.items()
            if value <= self.CRITICAL_MINIMUM
        ]

        suppression = bool(critical_weak)

        if critical_weak:
            risk_flags.append(
                "critical_confidence_dimension_weak:"
                + ",".join(critical_weak)
            )

            confidence_score *= 0.50

            reasons.append(
                "Confidence suppressed because one or more critical "
                "information dimensions are materially weak."
            )

        # ------------------------------------------------------------
        # Evidence-specific interpretation
        # ------------------------------------------------------------

        if evidence_quality >= 85:
            reasons.append("Evidence quality is strong.")
        elif evidence_quality < 50:
            reasons.append("Evidence quality is insufficient.")

        if signal_alignment >= 85:
            reasons.append("Signals show strong directional alignment.")
        elif signal_alignment < 50:
            reasons.append("Signals contain meaningful disagreement.")

        if data_quality >= 85:
            reasons.append("Market data quality is strong.")
        elif data_quality < 50:
            risk_flags.append("data_quality_below_operational_threshold")

        if source_reliability >= 85:
            reasons.append("Source reliability is strong.")
        elif source_reliability < 50:
            risk_flags.append("source_reliability_below_operational_threshold")

        if context_alignment >= 85:
            reasons.append("Market context strongly supports the interpretation.")
        elif context_alignment < 50:
            reasons.append("Market context does not sufficiently support the interpretation.")

        if timing_quality >= 85:
            reasons.append("Timing quality strongly supports the interpretation.")
        elif timing_quality < 50:
            reasons.append("Timing quality is weak.")

        # ------------------------------------------------------------
        # Cross-dimension consistency
        # ------------------------------------------------------------

        maximum = max(values.values())
        minimum = min(values.values())
        dispersion = maximum - minimum

        if dispersion >= 60.0:
            risk_flags.append("high_dimension_dispersion")
            reasons.append(
                "Confidence dimensions are materially inconsistent."
            )

        # A very high score with weak evidence cannot remain HIGH.
        if evidence_quality < 60.0:
            confidence_score = min(confidence_score, 69.99)
            risk_flags.append("high_confidence_blocked_by_evidence_quality")

        if data_quality < 50.0:
            confidence_score = min(confidence_score, 59.99)
            risk_flags.append("confidence_capped_by_data_quality")

        if source_reliability < 50.0:
            confidence_score = min(confidence_score, 59.99)
            risk_flags.append("confidence_capped_by_source_reliability")

        confidence_score = self._clamp(confidence_score)

        state = self._classify(confidence_score, suppression)

        confidence_band = self._band(confidence_score)

        evidence = {
            "engine": self.VERSION,
            "formula": (
                "C=EQ*0.25+SA*0.20+DQ*0.15+"
                "SR*0.15+CA*0.15+TQ*0.10"
            ),
            "weights": dict(self.WEIGHTS),
            "dimensions": dict(values),
            "critical_weak_dimensions": tuple(critical_weak),
            "dispersion": dispersion,
            "suppression": suppression,
            "confidence_score": confidence_score,
        }

        assessment = ConfidenceAssessment(
            symbol=symbol_value,
            timeframe=timeframe_value,
            confidence_score=confidence_score,
            evidence_quality=evidence_quality,
            signal_alignment=signal_alignment,
            data_quality=data_quality,
            source_reliability=source_reliability,
            context_alignment=context_alignment,
            timing_quality=timing_quality,
            state=state,
            confidence_band=confidence_band,
            suppression=suppression,
            reasons=tuple(dict.fromkeys(reasons)),
            risk_flags=tuple(dict.fromkeys(risk_flags)),
            evidence=evidence,
        )

        with self._lock:
            self._history.append(assessment)

            if len(self._history) > self._max_history:
                self._history = self._history[-self._max_history:]

        return assessment

    # ================================================================
    # HISTORY
    # ================================================================

    def history(self) -> tuple[ConfidenceAssessment, ...]:
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
                item.confidence_score
                for item in self._history
            ) / len(self._history)

    # ================================================================
    # STATE
    # ================================================================

    def _classify(
        self,
        score: float,
        suppression: bool,
    ) -> str:

        if suppression and score < self.PARTIAL_THRESHOLD:
            return "SUPPRESSED"

        if score >= self.HIGH_THRESHOLD:
            return "HIGH"

        if score >= self.RELIABLE_THRESHOLD:
            return "RELIABLE"

        if score >= self.PARTIAL_THRESHOLD:
            return "PARTIAL"

        if score >= self.WEAK_THRESHOLD:
            return "WEAK"

        return "INSUFFICIENT"

    def _band(self, score: float) -> str:
        if score >= self.HIGH_THRESHOLD:
            return "85-100"

        if score >= self.RELIABLE_THRESHOLD:
            return "70-84.99"

        if score >= self.PARTIAL_THRESHOLD:
            return "50-69.99"

        if score >= self.WEAK_THRESHOLD:
            return "30-49.99"

        return "0-29.99"

    # ================================================================
    # INPUT NORMALIZATION
    # ================================================================

    def _dimension(
        self,
        data: Mapping[str, Any],
        keys: tuple[str, ...],
    ) -> float:

        value = self._score(data, keys)

        if value is not None:
            return value

        # Missing evidence is treated as unavailable, not as confidence.
        return 0.0

    @staticmethod
    def _score(
        data: Mapping[str, Any],
        keys: tuple[str, ...],
    ) -> float | None:

        for key in keys:
            if key not in data:
                continue

            value = data[key]

            if isinstance(value, Mapping):
                for nested in (
                    "score",
                    "value",
                    "normalized",
                    "percentage",
                ):
                    if nested in value:
                        value = value[nested]
                        break

            try:
                number = float(value)
            except (TypeError, ValueError):
                continue

            if not isfinite(number):
                continue

            # Accept normalized [0,1] upstream values.
            if 0.0 <= number <= 1.0:
                number *= 100.0

            return ConfidenceEngine._clamp(number)

        return None

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

    # ================================================================
    # HEALTH
    # ================================================================

    def health_check(self) -> dict[str, Any]:
        with self._lock:
            history_count = len(self._history)

        return {
            "engine": self.VERSION,
            "status": "healthy",
            "formula": (
                "C=EQ*0.25+SA*0.20+DQ*0.15+"
                "SR*0.15+CA*0.15+TQ*0.10"
            ),
            "history_count": history_count,
            "weights": dict(self.WEIGHTS),
            "thresholds": {
                "high": self.HIGH_THRESHOLD,
                "reliable": self.RELIABLE_THRESHOLD,
                "partial": self.PARTIAL_THRESHOLD,
                "weak": self.WEAK_THRESHOLD,
            },
            "critical_minimum": self.CRITICAL_MINIMUM,
        }


__all__ = [
    "ConfidenceAssessment",
    "ConfidenceEngine",
]