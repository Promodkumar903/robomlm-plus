from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Callable, Mapping


@dataclass(frozen=True)
class DecisionRequest:
    symbol: str
    timeframe: str
    direction: str
    evidence_score: float
    confidence_score: float
    commitment_score: float
    context_score: float = 0.0
    risk_score: float = 0.0
    timing_score: float = 0.0
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DecisionOutcome:
    symbol: str
    timeframe: str
    decision: str
    direction: str
    decision_score: float

    evidence_score: float
    confidence_score: float
    commitment_score: float
    context_score: float
    risk_score: float
    timing_score: float

    approved: bool
    confidence: float
    gate_reasons: tuple[str, ...] = ()
    conflict_flags: tuple[str, ...] = ()
    evidence: dict[str, Any] = field(default_factory=dict)

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class DecisionOrchestrator:
    """
    ROBOMLM Decision Cortex orchestration layer.

    Decision is downstream of intelligence.

    Core decision composition:

        D = E*0.35 + C*0.35 + K*0.30

    E = Evidence quality
    C = Confidence
    K = Commitment

    Context, risk and timing are preserved as decision-gate dimensions.
    They do not silently replace the core Decision Cortex score.

    Direction is accepted only after signal consistency is checked.
    A high score with contradictory direction is not converted into
    an executable BUY/SELL decision.

    This class does NOT:
        - place orders
        - bypass risk
        - bypass authorization
        - bypass kill switch
        - manage broker state
    """

    VERSION = "ROBOMLM-DECISION-2.0"

    WEIGHTS = {
        "evidence": 0.35,
        "confidence": 0.35,
        "commitment": 0.30,
    }

    APPROVAL_THRESHOLD = 70.0
    STRONG_THRESHOLD = 85.0

    MIN_EVIDENCE = 40.0
    MIN_CONFIDENCE = 50.0
    MIN_COMMITMENT = 50.0

    VALID_DIRECTIONS = {
        "BUY",
        "SELL",
        "LONG",
        "SHORT",
        "HOLD",
        "NEUTRAL",
    }

    def __init__(self, max_history: int = 1000) -> None:
        if max_history < 1:
            raise ValueError("max_history must be >= 1.")

        self._history: list[DecisionOutcome] = []
        self._handlers: dict[str, Callable[..., Any]] = {}
        self._max_history = max_history
        self._lock = RLock()

    # ================================================================
    # MAIN DECISION FLOW
    # ================================================================

    def decide(
        self,
        request: DecisionRequest | Mapping[str, Any],
    ) -> DecisionOutcome:

        normalized = self._normalize_request(request)

        direction = self._normalize_direction(normalized.direction)

        evidence = self._clamp(normalized.evidence_score)
        confidence = self._clamp(normalized.confidence_score)
        commitment = self._clamp(normalized.commitment_score)
        context = self._clamp(normalized.context_score)
        risk = self._clamp(normalized.risk_score)
        timing = self._clamp(normalized.timing_score)

        reasons: list[str] = []
        conflicts: list[str] = []

        # ------------------------------------------------------------
        # Core Decision Cortex score
        # ------------------------------------------------------------

        decision_score = (
            evidence * self.WEIGHTS["evidence"]
            + confidence * self.WEIGHTS["confidence"]
            + commitment * self.WEIGHTS["commitment"]
        )

        # ------------------------------------------------------------
        # Minimum intelligence gates
        # ------------------------------------------------------------

        if evidence < self.MIN_EVIDENCE:
            reasons.append("Evidence below minimum decision threshold.")

        if confidence < self.MIN_CONFIDENCE:
            reasons.append("Confidence below minimum decision threshold.")

        if commitment < self.MIN_COMMITMENT:
            reasons.append("Commitment below minimum decision threshold.")

        # ------------------------------------------------------------
        # Context gate
        # ------------------------------------------------------------

        if context > 0.0 and context < 40.0:
            reasons.append("Market context is weak.")
            conflicts.append("context_weak")

        # ------------------------------------------------------------
        # Timing gate
        # ------------------------------------------------------------

        if timing > 0.0 and timing < 30.0:
            reasons.append("Timing quality is weak.")
            conflicts.append("timing_weak")

        # ------------------------------------------------------------
        # Risk gate
        #
        # risk_score is interpreted as remaining risk quality:
        # 100 = favorable / controlled
        # 0   = unacceptable
        # ------------------------------------------------------------

        if risk > 0.0 and risk < 30.0:
            reasons.append("Risk condition is unacceptable.")
            conflicts.append("risk_weak")

        # ------------------------------------------------------------
        # Direction consistency
        # ------------------------------------------------------------

        directional_conflict = self._directional_conflict(
            normalized.metadata
        )

        if directional_conflict:
            conflicts.append("directional_conflict")
            reasons.append(
                "Upstream intelligence contains contradictory direction."
            )

        # ------------------------------------------------------------
        # Decision gate
        # ------------------------------------------------------------

        approved = (
            decision_score >= self.APPROVAL_THRESHOLD
            and evidence >= self.MIN_EVIDENCE
            and confidence >= self.MIN_CONFIDENCE
            and commitment >= self.MIN_COMMITMENT
            and not directional_conflict
            and "risk_weak" not in conflicts
        )

        # If direction is HOLD/NEUTRAL, approval does not create
        # an entry decision.
        if direction in {"HOLD", "NEUTRAL"}:
            approved = False
            reasons.append("Directional state is HOLD/NEUTRAL.")

        # ------------------------------------------------------------
        # Final verdict
        # ------------------------------------------------------------

        if directional_conflict:
            decision = "CONFLICTED"
        elif not approved:
            if decision_score >= self.APPROVAL_THRESHOLD:
                decision = "REJECTED"
            else:
                decision = "HOLD"
        elif decision_score >= self.STRONG_THRESHOLD:
            decision = direction
        else:
            decision = direction

        # ------------------------------------------------------------
        # Decision confidence
        #
        # This is a decision-level confidence measure, not the
        # upstream Confidence Engine score.
        # ------------------------------------------------------------

        gate_quality = (
            evidence * 0.25
            + confidence * 0.30
            + commitment * 0.25
            + (context if context > 0.0 else decision_score) * 0.10
            + (timing if timing > 0.0 else decision_score) * 0.10
        )

        if conflicts:
            gate_quality *= 0.70

        if not approved:
            gate_quality *= 0.80

        decision_confidence = self._clamp(gate_quality)

        evidence_record = {
            "engine": self.VERSION,
            "formula": "D=E*0.35+C*0.35+K*0.30",
            "weights": dict(self.WEIGHTS),
            "direction": direction,
            "decision_score": decision_score,
            "approved": approved,
            "minimum_gates": {
                "evidence": self.MIN_EVIDENCE,
                "confidence": self.MIN_CONFIDENCE,
                "commitment": self.MIN_COMMITMENT,
            },
            "context_score": context,
            "risk_score": risk,
            "timing_score": timing,
            "directional_conflict": directional_conflict,
            "conflicts": tuple(conflicts),
        }

        outcome = DecisionOutcome(
            symbol=normalized.symbol,
            timeframe=normalized.timeframe,
            decision=decision,
            direction=direction,
            decision_score=self._clamp(decision_score),
            evidence_score=evidence,
            confidence_score=confidence,
            commitment_score=commitment,
            context_score=context,
            risk_score=risk,
            timing_score=timing,
            approved=approved,
            confidence=decision_confidence,
            gate_reasons=tuple(dict.fromkeys(reasons)),
            conflict_flags=tuple(dict.fromkeys(conflicts)),
            evidence=evidence_record,
        )

        with self._lock:
            self._history.append(outcome)

            if len(self._history) > self._max_history:
                self._history = self._history[-self._max_history:]

        return outcome

    # ================================================================
    # COMPATIBILITY ALIAS
    # ================================================================

    def evaluate(
        self,
        request: DecisionRequest | Mapping[str, Any],
    ) -> DecisionOutcome:
        return self.decide(request)

    # ================================================================
    # REQUEST NORMALIZATION
    # ================================================================

    def _normalize_request(
        self,
        request: DecisionRequest | Mapping[str, Any],
    ) -> DecisionRequest:

        if isinstance(request, DecisionRequest):
            return request

        if not isinstance(request, Mapping):
            raise TypeError(
                "request must be DecisionRequest or Mapping."
            )

        return DecisionRequest(
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
            direction=str(
                request.get(
                    "direction",
                    request.get("bias", "HOLD"),
                )
            ),
            evidence_score=self._extract_score(
                request,
                (
                    "evidence_score",
                    "evidence",
                    "evidence_quality",
                ),
            ),
            confidence_score=self._extract_score(
                request,
                (
                    "confidence_score",
                    "confidence",
                ),
            ),
            commitment_score=self._extract_score(
                request,
                (
                    "commitment_score",
                    "commitment",
                ),
            ),
            context_score=self._extract_score(
                request,
                (
                    "context_score",
                    "context_alignment",
                ),
            ),
            risk_score=self._extract_score(
                request,
                (
                    "risk_score",
                    "risk_quality",
                ),
            ),
            timing_score=self._extract_score(
                request,
                (
                    "timing_score",
                    "timing_quality",
                ),
            ),
            metadata=request.get("metadata", {}),
        )

    # ================================================================
    # DIRECTION
    # ================================================================

    def _normalize_direction(self, value: str) -> str:
        direction = str(value).strip().upper()

        aliases = {
            "LONG": "BUY",
            "SHORT": "SELL",
            "BULLISH": "BUY",
            "BEARISH": "SELL",
            "NEUTRAL": "HOLD",
            "NONE": "HOLD",
        }

        direction = aliases.get(direction, direction)

        if direction not in {"BUY", "SELL", "HOLD"}:
            raise ValueError(
                f"Unsupported direction: {value!r}"
            )

        return direction

    def _directional_conflict(
        self,
        metadata: Mapping[str, Any],
    ) -> bool:

        if not isinstance(metadata, Mapping):
            return False

        conflict = metadata.get("directional_conflict")

        if isinstance(conflict, bool):
            return conflict

        conflicts = metadata.get("conflicts")

        if isinstance(conflicts, (list, tuple, set)):
            normalized = {
                str(item).strip().lower()
                for item in conflicts
            }

            return bool(
                normalized.intersection(
                    {
                        "directional_conflict",
                        "signal_conflict",
                        "contradiction",
                        "contradictory_signal",
                    }
                )
            )

        return False

    # ================================================================
    # HANDLER REGISTRY
    # ================================================================

    def register_handler(
        self,
        name: str,
        handler: Callable[..., Any],
    ) -> None:

        if not name or not callable(handler):
            raise ValueError(
                "name and callable handler are required."
            )

        with self._lock:
            self._handlers[str(name)] = handler

    def unregister_handler(self, name: str) -> bool:
        with self._lock:
            return self._handlers.pop(str(name), None) is not None

    def handler_names(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(self._handlers.keys())

    # ================================================================
    # HISTORY
    # ================================================================

    def history(self) -> tuple[DecisionOutcome, ...]:
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
                item.decision_score
                for item in self._history
            ) / len(self._history)

    # ================================================================
    # HEALTH
    # ================================================================

    def health_check(self) -> dict[str, Any]:
        with self._lock:
            history_count = len(self._history)
            handler_count = len(self._handlers)

        return {
            "engine": self.VERSION,
            "status": "healthy",
            "history_count": history_count,
            "handler_count": handler_count,
            "formula": "D=E*0.35+C*0.35+K*0.30",
            "weights": dict(self.WEIGHTS),
            "thresholds": {
                "approval": self.APPROVAL_THRESHOLD,
                "strong": self.STRONG_THRESHOLD,
                "minimum_evidence": self.MIN_EVIDENCE,
                "minimum_confidence": self.MIN_CONFIDENCE,
                "minimum_commitment": self.MIN_COMMITMENT,
            },
        }

    # ================================================================
    # HELPERS
    # ================================================================

    @staticmethod
    def _extract_score(
        data: Mapping[str, Any],
        keys: tuple[str, ...],
    ) -> float:

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

            if 0.0 <= number <= 1.0:
                number *= 100.0

            return DecisionOrchestrator._clamp(number)

        return 0.0

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(100.0, float(value)))


__all__ = [
    "DecisionRequest",
    "DecisionOutcome",
    "DecisionOrchestrator",
]