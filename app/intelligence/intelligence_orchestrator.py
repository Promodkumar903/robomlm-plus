from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Callable, Mapping


@dataclass(frozen=True)
class IntelligenceRequest:
    symbol: str
    timeframe: str
    data: Mapping[str, Any] = field(default_factory=dict)
    evidence: Mapping[str, Any] = field(default_factory=dict)
    context: Mapping[str, Any] = field(default_factory=dict)
    specialized: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class IntelligenceResult:
    symbol: str
    timeframe: str

    intelligence_score: float
    evidence_score: float
    context_score: float
    specialized_score: float
    confidence_score: float
    commitment_score: float

    directional_bias: str
    state: str
    decision_ready: bool

    contradiction: bool
    contradiction_flags: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()

    evidence: dict[str, Any] = field(default_factory=dict)

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class IntelligenceOrchestrator:
    """
    ROBOMLM Intelligence Cortex.

    Processing chain:

        MARKET DATA
             ↓
        EVIDENCE
             ↓
        MARKET CONTEXT
             ↓
        SPECIALIZED INTELLIGENCE
             ↓
        CONFIDENCE
             ↓
        COMMITMENT
             ↓
        DIRECTIONAL SYNTHESIS
             ↓
        INTELLIGENCE VERDICT
             ↓
        DECISION-READY GATE

    Core intelligence composition:

        I =
            E*0.25
          + M*0.25
          + S*0.30
          + C*0.10
          + K*0.10

    E = Evidence
    M = Market Context
    S = Specialized Intelligence
    C = Confidence
    K = Commitment

    The orchestrator does not execute trades and does not bypass
    Risk, Authorization, Kill Switch or Execution layers.
    """

    VERSION = "ROBOMLM-INTELLIGENCE-2.0"

    WEIGHTS = {
        "evidence": 0.25,
        "context": 0.25,
        "specialized": 0.30,
        "confidence": 0.10,
        "commitment": 0.10,
    }

    ACTIONABLE_THRESHOLD = 70.0
    STRONG_THRESHOLD = 85.0

    MIN_EVIDENCE = 40.0
    MIN_CONTEXT = 40.0
    MIN_CONFIDENCE = 50.0
    MIN_COMMITMENT = 50.0

    def __init__(self, max_history: int = 1000) -> None:
        if max_history < 1:
            raise ValueError("max_history must be >= 1.")

        self._history: list[IntelligenceResult] = []
        self._processors: dict[str, Callable[..., Any]] = {}
        self._max_history = max_history
        self._lock = RLock()

    # ================================================================
    # MAIN PIPELINE
    # ================================================================

    def analyze(
        self,
        request: IntelligenceRequest | Mapping[str, Any],
    ) -> IntelligenceResult:

        normalized = self._normalize_request(request)

        evidence_score = self._extract_score(
            normalized.evidence,
            normalized.data,
            (
                "evidence_score",
                "evidence_quality",
                "evidence_strength",
            ),
        )

        context_score = self._extract_score(
            normalized.context,
            normalized.data,
            (
                "context_score",
                "market_context_score",
                "mci_score",
            ),
        )

        specialized_score = self._extract_score(
            normalized.specialized,
            normalized.data,
            (
                "specialized_score",
                "intelligence_score",
                "specialized_quality",
            ),
        )

        confidence_score = self._extract_score(
            normalized.specialized,
            normalized.data,
            (
                "confidence_score",
                "confidence",
            ),
        )

        commitment_score = self._extract_score(
            normalized.specialized,
            normalized.data,
            (
                "commitment_score",
                "commitment",
            ),
        )

        evidence_score = self._clamp(evidence_score)
        context_score = self._clamp(context_score)
        specialized_score = self._clamp(specialized_score)
        confidence_score = self._clamp(confidence_score)
        commitment_score = self._clamp(commitment_score)

        reasons: list[str] = []
        contradiction_flags: list[str] = []

        # ------------------------------------------------------------
        # Core intelligence score
        # ------------------------------------------------------------

        intelligence_score = (
            evidence_score * self.WEIGHTS["evidence"]
            + context_score * self.WEIGHTS["context"]
            + specialized_score * self.WEIGHTS["specialized"]
            + confidence_score * self.WEIGHTS["confidence"]
            + commitment_score * self.WEIGHTS["commitment"]
        )

        # ------------------------------------------------------------
        # Directional synthesis
        # ------------------------------------------------------------

        directional_bias = self._directional_bias(
            normalized
        )

        # ------------------------------------------------------------
        # Contradiction detection
        # ------------------------------------------------------------

        contradiction_flags.extend(
            self._detect_contradictions(
                normalized,
                evidence_score,
                context_score,
                specialized_score,
                confidence_score,
                commitment_score,
                directional_bias,
            )
        )

        contradiction = bool(contradiction_flags)

        if contradiction:
            intelligence_score *= 0.70
            reasons.append(
                "Intelligence score reduced because material "
                "cross-layer contradiction was detected."
            )

        # ------------------------------------------------------------
        # Weak layer gates
        # ------------------------------------------------------------

        if evidence_score < self.MIN_EVIDENCE:
            reasons.append(
                "Evidence layer below minimum intelligence threshold."
            )

        if context_score < self.MIN_CONTEXT:
            reasons.append(
                "Market context below minimum intelligence threshold."
            )

        if confidence_score < self.MIN_CONFIDENCE:
            reasons.append(
                "Confidence below minimum intelligence threshold."
            )

        if commitment_score < self.MIN_COMMITMENT:
            reasons.append(
                "Commitment below minimum intelligence threshold."
            )

        intelligence_score = self._clamp(intelligence_score)

        # ------------------------------------------------------------
        # Decision-ready gate
        # ------------------------------------------------------------

        decision_ready = (
            intelligence_score >= self.ACTIONABLE_THRESHOLD
            and evidence_score >= self.MIN_EVIDENCE
            and context_score >= self.MIN_CONTEXT
            and confidence_score >= self.MIN_CONFIDENCE
            and commitment_score >= self.MIN_COMMITMENT
            and not contradiction
            and directional_bias in {"BUY", "SELL"}
        )

        # ------------------------------------------------------------
        # State
        # ------------------------------------------------------------

        if contradiction:
            state = "CONFLICTED"
        elif intelligence_score >= self.STRONG_THRESHOLD:
            state = "STRONG"
        elif decision_ready:
            state = "ACTIONABLE"
        elif intelligence_score >= self.ACTIONABLE_THRESHOLD:
            state = "QUALIFIED"
        elif intelligence_score >= 50.0:
            state = "PARTIAL"
        elif intelligence_score >= 30.0:
            state = "WEAK"
        else:
            state = "INSUFFICIENT"

        # A strong numeric score alone cannot override a failed gate.
        if (
            intelligence_score >= self.STRONG_THRESHOLD
            and not decision_ready
        ):
            reasons.append(
                "High composite score does not override failed "
                "decision-readiness gates."
            )

        evidence_snapshot = {
            "engine": self.VERSION,
            "formula": (
                "I=E*0.25+M*0.25+S*0.30+"
                "C*0.10+K*0.10"
            ),
            "weights": dict(self.WEIGHTS),
            "layers": {
                "evidence": evidence_score,
                "context": context_score,
                "specialized": specialized_score,
                "confidence": confidence_score,
                "commitment": commitment_score,
            },
            "directional_bias": directional_bias,
            "contradiction": contradiction,
            "contradiction_flags": tuple(contradiction_flags),
            "decision_ready": decision_ready,
            "thresholds": {
                "actionable": self.ACTIONABLE_THRESHOLD,
                "strong": self.STRONG_THRESHOLD,
                "minimum_evidence": self.MIN_EVIDENCE,
                "minimum_context": self.MIN_CONTEXT,
                "minimum_confidence": self.MIN_CONFIDENCE,
                "minimum_commitment": self.MIN_COMMITMENT,
            },
        }

        result = IntelligenceResult(
            symbol=normalized.symbol,
            timeframe=normalized.timeframe,
            intelligence_score=intelligence_score,
            evidence_score=evidence_score,
            context_score=context_score,
            specialized_score=specialized_score,
            confidence_score=confidence_score,
            commitment_score=commitment_score,
            directional_bias=directional_bias,
            state=state,
            decision_ready=decision_ready,
            contradiction=contradiction,
            contradiction_flags=tuple(
                dict.fromkeys(contradiction_flags)
            ),
            reasons=tuple(dict.fromkeys(reasons)),
            evidence=evidence_snapshot,
        )

        with self._lock:
            self._history.append(result)

            if len(self._history) > self._max_history:
                self._history = self._history[-self._max_history:]

        return result

    # Compatibility aliases
    def assess(
        self,
        request: IntelligenceRequest | Mapping[str, Any],
    ) -> IntelligenceResult:
        return self.analyze(request)

    def evaluate(
        self,
        request: IntelligenceRequest | Mapping[str, Any],
    ) -> IntelligenceResult:
        return self.analyze(request)

    # ================================================================
    # DIRECTIONAL INTELLIGENCE
    # ================================================================

    def _directional_bias(
        self,
        request: IntelligenceRequest,
    ) -> str:

        sources = (
            request.specialized,
            request.context,
            request.evidence,
            request.data,
        )

        scores = {
            "BUY": 0.0,
            "SELL": 0.0,
        }

        for source in sources:
            if not isinstance(source, Mapping):
                continue

            for key in (
                "direction",
                "bias",
                "directional_bias",
                "signal",
            ):
                value = source.get(key)

                if value is None:
                    continue

                direction = self._normalize_direction(value)

                if direction == "BUY":
                    scores["BUY"] += 1.0
                elif direction == "SELL":
                    scores["SELL"] += 1.0

        if scores["BUY"] == 0.0 and scores["SELL"] == 0.0:
            return "HOLD"

        if scores["BUY"] == scores["SELL"]:
            return "HOLD"

        return (
            "BUY"
            if scores["BUY"] > scores["SELL"]
            else "SELL"
        )

    # ================================================================
    # CONTRADICTION ENGINE
    # ================================================================

    def _detect_contradictions(
        self,
        request: IntelligenceRequest,
        evidence_score: float,
        context_score: float,
        specialized_score: float,
        confidence_score: float,
        commitment_score: float,
        directional_bias: str,
    ) -> list[str]:

        conflicts: list[str] = []

        layers = {
            "evidence": request.evidence,
            "context": request.context,
            "specialized": request.specialized,
            "data": request.data,
        }

        directions: dict[str, str] = {}

        for name, source in layers.items():
            if not isinstance(source, Mapping):
                continue

            for key in (
                "direction",
                "bias",
                "directional_bias",
                "signal",
            ):
                if key in source:
                    direction = self._normalize_direction(
                        source[key]
                    )

                    if direction in {"BUY", "SELL"}:
                        directions[name] = direction
                    break

        unique_directions = set(directions.values())

        if len(unique_directions) > 1:
            conflicts.append("cross_layer_directional_conflict")

        # Strong context against specialized intelligence.
        if (
            context_score >= 75.0
            and specialized_score <= 35.0
        ):
            conflicts.append(
                "context_specialized_divergence"
            )

        if (
            specialized_score >= 75.0
            and context_score <= 35.0
        ):
            conflicts.append(
                "specialized_context_divergence"
            )

        # Confidence cannot be ignored by a high commitment reading.
        if (
            commitment_score >= 80.0
            and confidence_score <= 35.0
        ):
            conflicts.append(
                "commitment_confidence_divergence"
            )

        # Strong commitment with insufficient evidence is not a
        # valid intelligence confirmation.
        if (
            commitment_score >= 80.0
            and evidence_score < self.MIN_EVIDENCE
        ):
            conflicts.append(
                "commitment_without_sufficient_evidence"
            )

        # A directional source contradicting final synthesis.
        if directional_bias in {"BUY", "SELL"}:
            for name, direction in directions.items():
                if direction != directional_bias:
                    conflicts.append(
                        f"{name}_direction_conflicts_with_synthesis"
                    )

        return list(dict.fromkeys(conflicts))

    # ================================================================
    # REQUEST NORMALIZATION
    # ================================================================

    def _normalize_request(
        self,
        request: IntelligenceRequest | Mapping[str, Any],
    ) -> IntelligenceRequest:

        if isinstance(request, IntelligenceRequest):
            return request

        if not isinstance(request, Mapping):
            raise TypeError(
                "request must be IntelligenceRequest or Mapping."
            )

        return IntelligenceRequest(
            symbol=str(
                request.get(
                    "symbol",
                    request.get("instrument", "UNKNOWN"),
                )
            ),
            timeframe=str(
                request.get(
                    "timeframe",
                    request.get("interval", "UNKNOWN"),
                )
            ),
            data=self._mapping(
                request.get("data", request)
            ),
            evidence=self._mapping(
                request.get("evidence", {})
            ),
            context=self._mapping(
                request.get("context", {})
            ),
            specialized=self._mapping(
                request.get(
                    "specialized",
                    request.get("intelligence", {}),
                )
            ),
        )

    # ================================================================
    # PROCESSOR REGISTRY
    # ================================================================

    def register_processor(
        self,
        name: str,
        processor: Callable[..., Any],
    ) -> None:

        if not name:
            raise ValueError("processor name is required.")

        if not callable(processor):
            raise TypeError("processor must be callable.")

        with self._lock:
            self._processors[str(name)] = processor

    def unregister_processor(self, name: str) -> bool:
        with self._lock:
            return (
                self._processors.pop(str(name), None)
                is not None
            )

    def processor_names(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(self._processors.keys())

    # ================================================================
    # HISTORY
    # ================================================================

    def history(self) -> tuple[IntelligenceResult, ...]:
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
                result.intelligence_score
                for result in self._history
            ) / len(self._history)

    # ================================================================
    # HEALTH
    # ================================================================

    def health_check(self) -> dict[str, Any]:
        with self._lock:
            history_count = len(self._history)
            processor_count = len(self._processors)

        return {
            "engine": self.VERSION,
            "status": "healthy",
            "history_count": history_count,
            "processor_count": processor_count,
            "formula": (
                "I=E*0.25+M*0.25+S*0.30+"
                "C*0.10+K*0.10"
            ),
            "weights": dict(self.WEIGHTS),
            "thresholds": {
                "actionable": self.ACTIONABLE_THRESHOLD,
                "strong": self.STRONG_THRESHOLD,
                "minimum_evidence": self.MIN_EVIDENCE,
                "minimum_context": self.MIN_CONTEXT,
                "minimum_confidence": self.MIN_CONFIDENCE,
                "minimum_commitment": self.MIN_COMMITMENT,
            },
            "pipeline": [
                "evidence",
                "market_context",
                "specialized_intelligence",
                "confidence",
                "commitment",
                "directional_synthesis",
                "contradiction_detection",
                "decision_readiness",
            ],
        }

    # ================================================================
    # HELPERS
    # ================================================================

    @staticmethod
    def _mapping(value: Any) -> Mapping[str, Any]:
        if isinstance(value, Mapping):
            return value
        return {}

    @staticmethod
    def _extract_score(
        primary: Mapping[str, Any],
        secondary: Mapping[str, Any],
        keys: tuple[str, ...],
    ) -> float:

        for source in (primary, secondary):
            for key in keys:
                if key not in source:
                    continue

                value = source[key]

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

                if 0.0 <= number <= 1.0:
                    number *= 100.0

                return IntelligenceOrchestrator._clamp(
                    number
                )

        return 0.0

    @staticmethod
    def _normalize_direction(value: Any) -> str:

        direction = str(value).strip().upper()

        aliases = {
            "LONG": "BUY",
            "SHORT": "SELL",
            "BULLISH": "BUY",
            "BEARISH": "SELL",
            "NEUTRAL": "HOLD",
            "NONE": "HOLD",
        }

        return aliases.get(direction, direction)

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(100.0, float(value)))


__all__ = [
    "IntelligenceRequest",
    "IntelligenceResult",
    "IntelligenceOrchestrator",
]