from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class TerminalRequest:
    symbol: str
    timeframe: str = "1m"
    direction: str = "HOLD"
    mode: str = "ANALYSIS"
    request_id: str | None = None
    metadata: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class TerminalResult:
    request_id: str
    symbol: str
    timeframe: str
    status: str
    decision: dict[str, Any]
    evidence: dict[str, Any]
    provenance: dict[str, Any]
    generated_at: str
    errors: tuple[str, ...] = ()


class TerminalRuntime:
    """
    ROBOMLM Terminal application boundary.

    Responsibility:
        API/UI request
            ->
        existing market/signal source
            ->
        existing Decision Cortex

    This class does NOT:
        - replace D13
        - place orders
        - bypass Risk
        - bypass CAS
        - create fake evidence
        - manufacture missing market data
        - change D6 formulas
    """

    VERSION = "ROBOMLM-TERMINAL-1.0"

    def __init__(self) -> None:
        self._decision_engine = None

    # ------------------------------------------------------------
    # PUBLIC
    # ------------------------------------------------------------

    def run(self, request: TerminalRequest) -> TerminalResult:
        request_id = (
            request.request_id
            or self._request_id(request.symbol, request.timeframe)
        )

        errors: list[str] = []

        signal = self._load_existing_signal(
            symbol=request.symbol,
            timeframe=request.timeframe,
        )

        if not signal:
            return TerminalResult(
                request_id=request_id,
                symbol=request.symbol,
                timeframe=request.timeframe,
                status="INSUFFICIENT",
                decision={
                    "decision": "HOLD",
                    "direction": "HOLD",
                    "approved": False,
                },
                evidence={},
                provenance={
                    "runtime": self.VERSION,
                    "source": "existing_signal_engine",
                },
                generated_at=self._now(),
                errors=("No usable market signal was returned.",),
            )

        decision = self._run_existing_d13(
            symbol=request.symbol,
            timeframe=request.timeframe,
            signal=signal,
            requested_direction=request.direction,
        )

        status = "VALID"

        if not decision.get("approved", False):
            status = "REVIEW"

        return TerminalResult(
            request_id=request_id,
            symbol=request.symbol,
            timeframe=request.timeframe,
            status=status,
            decision=decision,
            evidence=self._extract_evidence(signal),
            provenance={
                "runtime": self.VERSION,
                "signal_source": "existing_live_signal_engine",
                "decision_engine": decision.get(
                    "engine",
                    "ROBOMLM-DECISION-2.0",
                ),
                "no_order_execution": True,
            },
            generated_at=self._now(),
            errors=tuple(errors),
        )

    # ------------------------------------------------------------
    # EXISTING SIGNAL SOURCE
    # ------------------------------------------------------------

    @staticmethod
    def _load_existing_signal(
        symbol: str,
        timeframe: str,
    ) -> dict[str, Any]:
        """
        Reuse the existing ROBOMLM live signal generator.

        We deliberately do not duplicate V4.5/V5 signal calculations here.
        """
        try:
            from app.intelligence.live_signal_generator import get_signal

            result = get_signal(symbol)

            if isinstance(result, Mapping):
                return dict(result)

        except ImportError:
            pass
        except Exception as exc:
            return {
                "status": "ERROR",
                "error": str(exc),
            }

        # Compatibility with the current server's existing helper.
        try:
            import serve

            getter = getattr(serve, "_get_live_signal", None)

            if callable(getter):
                result = getter(symbol)

                if isinstance(result, Mapping):
                    return dict(result)

        except Exception:
            pass

        return {}

    # ------------------------------------------------------------
    # EXISTING D13
    # ------------------------------------------------------------

    def _run_existing_d13(
        self,
        symbol: str,
        timeframe: str,
        signal: Mapping[str, Any],
        requested_direction: str,
    ) -> dict[str, Any]:

        direction = self._resolve_direction(
            signal,
            requested_direction,
        )

        evidence_score = self._score(
            signal,
            (
                "evidence_score",
                "confidence",
                "final_confidence",
                "score",
            ),
        )

        confidence_score = self._score(
            signal,
            (
                "confidence",
                "consensus_pct",
                "confidence_score",
            ),
        )

        commitment_score = self._score(
            signal,
            (
                "commitment_score",
                "confidence",
                "final_confidence",
                "score",
            ),
        )

        context_score = self._score(
            signal,
            (
                "context_score",
                "context",
                "market_context",
            ),
        )

        risk_score = self._score(
            signal,
            (
                "risk_score",
                "risk_quality",
            ),
        )

        timing_score = self._score(
            signal,
            (
                "timing_score",
                "timing_quality",
            ),
        )

        try:
            from app.intelligence.decision_orchestrator import (
                DecisionOrchestrator,
                DecisionRequest,
            )

            if self._decision_engine is None:
                self._decision_engine = DecisionOrchestrator()

            request = DecisionRequest(
                symbol=symbol,
                timeframe=timeframe,
                direction=direction,
                evidence_score=evidence_score,
                confidence_score=confidence_score,
                commitment_score=commitment_score,
                context_score=context_score,
                risk_score=risk_score,
                timing_score=timing_score,
                metadata={
                    "source": "terminal_runtime",
                    "signal_status": signal.get("status"),
                    "requested_direction": requested_direction,
                    "signal_conflicts": signal.get(
                        "conflicts",
                        signal.get("conflict_flags", []),
                    ),
                },
            )

            outcome = self._decision_engine.decide(request)

            return {
                "engine": getattr(
                    self._decision_engine,
                    "VERSION",
                    "ROBOMLM-DECISION-2.0",
                ),
                "decision": getattr(outcome, "decision", "HOLD"),
                "direction": getattr(outcome, "direction", "HOLD"),
                "decision_score": float(
                    getattr(outcome, "decision_score", 0.0)
                ),
                "evidence_score": float(
                    getattr(outcome, "evidence_score", 0.0)
                ),
                "confidence_score": float(
                    getattr(outcome, "confidence_score", 0.0)
                ),
                "commitment_score": float(
                    getattr(outcome, "commitment_score", 0.0)
                ),
                "context_score": float(
                    getattr(outcome, "context_score", 0.0)
                ),
                "risk_score": float(
                    getattr(outcome, "risk_score", 0.0)
                ),
                "timing_score": float(
                    getattr(outcome, "timing_score", 0.0)
                ),
                "approved": bool(
                    getattr(outcome, "approved", False)
                ),
                "confidence": float(
                    getattr(outcome, "confidence", 0.0)
                ),
                "gate_reasons": list(
                    getattr(outcome, "gate_reasons", ())
                ),
                "conflict_flags": list(
                    getattr(outcome, "conflict_flags", ())
                ),
                "evidence": dict(
                    getattr(outcome, "evidence", {})
                ),
            }

        except Exception as exc:
            return {
                "engine": "ROBOMLM-DECISION-2.0",
                "decision": "HOLD",
                "direction": direction,
                "decision_score": 0.0,
                "approved": False,
                "confidence": 0.0,
                "gate_reasons": [
                    f"D13 unavailable: {exc}"
                ],
                "conflict_flags": [
                    "decision_engine_error"
                ],
            }

    # ------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------

    @staticmethod
    def _resolve_direction(
        signal: Mapping[str, Any],
        requested: str,
    ) -> str:

        candidate = (
            requested
            if requested and requested.upper() != "HOLD"
            else signal.get("direction")
            or signal.get("signal")
            or signal.get("decision")
            or "HOLD"
        )

        value = str(candidate).strip().upper()

        aliases = {
            "LONG": "BUY",
            "SHORT": "SELL",
            "BULLISH": "BUY",
            "BEARISH": "SELL",
            "NEUTRAL": "HOLD",
        }

        return aliases.get(value, value) if value in {
            "BUY",
            "SELL",
            "LONG",
            "SHORT",
            "BULLISH",
            "BEARISH",
            "HOLD",
            "NEUTRAL",
        } else "HOLD"

    @staticmethod
    def _score(
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

            return max(0.0, min(100.0, number))

        return 0.0

    @staticmethod
    def _extract_evidence(
        signal: Mapping[str, Any],
    ) -> dict[str, Any]:

        evidence = signal.get("evidence")

        if isinstance(evidence, Mapping):
            return dict(evidence)

        return {
            "metrics": signal.get("metrics", []),
            "engines": signal.get("engines", []),
            "mtf": signal.get("mtf", []),
            "status": signal.get("status"),
        }

    @staticmethod
    def _request_id(
        symbol: str,
        timeframe: str,
    ) -> str:

        now = datetime.now(timezone.utc)
        return (
            f"TERM-"
            f"{now.strftime('%Y%m%d%H%M%S%f')}-"
            f"{symbol.replace('/', '').upper()}-"
            f"{timeframe}"
        )

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()


def terminal_result_to_dict(
    result: TerminalResult,
) -> dict[str, Any]:

    return asdict(result)


__all__ = [
    "TerminalRequest",
    "TerminalResult",
    "TerminalRuntime",
    "terminal_result_to_dict",
]