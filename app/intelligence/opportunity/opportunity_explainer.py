"""
ROBOMLM_PLUS
Opportunity Discovery Intelligence
-----------------------------------

Opportunity Explainer

Purpose
-------
Explain an already-produced Opportunity Decision without creating
a new market decision.

Architectural boundary
----------------------
Universe
    -> Liquidity
    -> Risk
    -> Timing
    -> Intraday
    -> Ranking
    -> Opportunity Engine
    -> Opportunity Explainer

This module is PRESENTATION / INTERPRETATION support only.

It MUST NOT:
    - invent market data
    - create a new BUY/SELL decision
    - replace OpportunityEngine
    - replace RankingEngine
    - recalculate D6 formulas
    - manufacture confidence
    - manufacture evidence
    - override safety/risk/liquidity/timing gates
    - act as an execution engine
    - silently convert UNKNOWN into PASS
    - silently convert missing evidence into positive evidence

V6 separation
-------------
Market State
    != Evidence State
    != Decision State
    != Trade Thesis

The explainer preserves that separation.

The explainer is intentionally deterministic:
same decision + same source data -> same explanation.

No external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
import json
import math
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


# ============================================================================
# ENUMS
# ============================================================================


class ExplanationStatus(str, Enum):
    """Overall status of the explanation payload."""

    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    UNKNOWN = "UNKNOWN"


class ExplanationTone(str, Enum):
    """Neutral semantic tone derived from the existing decision."""

    POSITIVE = "POSITIVE"
    CAUTION = "CAUTION"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"


class EvidenceState(str, Enum):
    """Evidence availability state.

    This is deliberately separate from market state and decision state.
    """

    STRONG = "STRONG"
    ADEQUATE = "ADEQUATE"
    LIMITED = "LIMITED"
    MISSING = "MISSING"
    UNKNOWN = "UNKNOWN"


# ============================================================================
# DATA OBJECTS
# ============================================================================


@dataclass(frozen=True)
class ExplanationItem:
    """One deterministic explanation statement."""

    category: str
    title: str
    detail: str
    value: Any = None
    source: Optional[str] = None
    importance: str = "NORMAL"


@dataclass(frozen=True)
class GateExplanation:
    """Explanation of one upstream gate."""

    name: str
    status: str
    interpretation: str
    blocking: bool = False
    source: Optional[str] = None


@dataclass(frozen=True)
class OpportunityExplanation:
    """Complete human-readable explanation of an opportunity decision."""

    instrument_id: Optional[str]
    symbol: Optional[str]

    status: ExplanationStatus
    tone: ExplanationTone

    headline: str
    summary: str

    decision_status: Optional[str]
    condition: Optional[str]
    direction: Optional[str]
    opportunity_type: Optional[str]

    score: Optional[float]
    normalized_score: Optional[float]
    confidence: Optional[float]

    evidence_count: int
    evidence_completeness: Optional[float]
    evidence_state: EvidenceState

    basis: Optional[str]

    reasons: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    evidence: Tuple[ExplanationItem, ...] = ()
    gates: Tuple[GateExplanation, ...] = ()

    expected_behavior: Optional[str] = None
    invalidation: Optional[str] = None
    risk_state: Optional[str] = None

    provenance: Mapping[str, Any] = field(default_factory=dict)

    generated_at: Optional[str] = None


@dataclass(frozen=True)
class OpportunityExplanationResult:
    """Batch explanation result."""

    status: ExplanationStatus
    explanations: Tuple[OpportunityExplanation, ...]

    complete_count: int
    partial_count: int
    unknown_count: int

    market_id: Optional[str]
    timestamp: Optional[str]

    provenance: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExplainerPolicy:
    """Controls interpretation without changing the underlying decision."""

    require_decision_status: bool = True
    require_symbol_or_instrument: bool = False
    include_missing_evidence_warnings: bool = True
    include_gate_details: bool = True
    include_provenance: bool = True
    reject_future_data: bool = True
    require_market_match: bool = True

    # Only semantic thresholds for explaining completeness.
    # These do NOT alter OpportunityEngine decisions.
    strong_completeness: float = 0.75
    adequate_completeness: float = 0.50


# ============================================================================
# ENGINE
# ============================================================================


class OpportunityExplainer:
    """
    Deterministic explanation layer for OpportunityEngine outputs.

    The engine accepts mappings or dataclass-like objects.

    It reads the decision; it does not mutate or replace it.
    """

    ENGINE_NAME = "OpportunityExplainer"
    ENGINE_VERSION = "2.0"

    _PRIMARY_SCORE_FIELDS = (
        "eqe",
        "pfs",
        "mci",
    )

    _SECONDARY_SCORE_FIELDS = (
        "mts",
        "lqs",
        "rds",
        "mcs",
    )

    _EVIDENCE_FIELDS = (
        "trend_strength",
        "volume_ratio",
        "liquidity_score",
        "risk_score",
        "timing_score",
        "derivatives_score",
        "participation_score",
        "relationship_score",
    )

    _GATE_FIELDS = (
        "liquidity_status",
        "risk_status",
        "timing_status",
        "intraday_status",
    )

    def __init__(
        self,
        policy: Optional[ExplainerPolicy] = None,
        market_id: Optional[str] = None,
    ) -> None:
        self.policy = policy or ExplainerPolicy()
        self.market_id = self._clean_text(market_id)

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def explain(
        self,
        decision: Any,
        *,
        now: Optional[datetime] = None,
        market_id: Optional[str] = None,
    ) -> OpportunityExplanation:
        """Explain one existing Opportunity decision."""

        data = self._to_mapping(decision)

        current_market = self._clean_text(
            market_id
            or self.market_id
            or self._text(data, "market_id")
        )

        timestamp = self._timestamp_text(data.get("timestamp"))

        status = self._text(data, "status")
        condition = self._text(data, "condition")
        direction = self._text(data, "direction")
        opportunity_type = self._text(data, "opportunity_type")

        instrument_id = self._text(data, "instrument_id")
        symbol = self._text(data, "symbol")

        score = self._number_from_mapping(data, "opportunity_score", "score")
        if score is None:
            score = self._number_from_mapping(data, "ranking_score")

        normalized_score = self._number_from_mapping(
            data,
            "normalized_score",
        )

        confidence = self._number_from_mapping(
            data,
            "confidence",
        )

        evidence_count = self._integer(
            data.get("evidence_count"),
            default=0,
        )

        completeness = self._number_from_mapping(
            data,
            "evidence_completeness",
        )

        basis = self._text(data, "basis")

        reasons = self._string_tuple(data.get("reasons"))
        warnings = self._string_tuple(data.get("warnings"))

        evidence_items = self._build_evidence_items(
            data,
            completeness=completeness,
        )

        gates = self._build_gate_explanations(data)

        evidence_state = self._evidence_state(
            evidence_count=evidence_count,
            completeness=completeness,
        )

        explanation_status = self._explanation_status(
            data=data,
            status=status,
            evidence_state=evidence_state,
            timestamp=timestamp,
            current_market=current_market,
            instrument_id=instrument_id,
            symbol=symbol,
        )

        tone = self._tone(
            decision_status=status,
            condition=condition,
            evidence_state=evidence_state,
        )

        headline = self._headline(
            status=status,
            condition=condition,
            direction=direction,
            opportunity_type=opportunity_type,
            symbol=symbol or instrument_id,
        )

        summary = self._summary(
            status=status,
            condition=condition,
            direction=direction,
            opportunity_type=opportunity_type,
            score=score,
            confidence=confidence,
            evidence_state=evidence_state,
            gates=gates,
        )

        expected_behavior = self._text(
            data,
            "expected_behavior",
        )

        invalidation = self._text(
            data,
            "invalidation",
            "invalidation_condition",
        )

        risk_state = self._text(
            data,
            "risk_state",
        )

        local_warnings = list(warnings)

        if (
            self.policy.include_missing_evidence_warnings
            and evidence_state in {
                EvidenceState.LIMITED,
                EvidenceState.MISSING,
            }
        ):
            local_warnings.append(
                "Supporting evidence is incomplete; explanation "
                "does not upgrade the underlying decision."
            )

        blocking_gates = [
            gate.name
            for gate in gates
            if gate.blocking
        ]

        if blocking_gates:
            local_warnings.append(
                "Blocking gate(s): " + ", ".join(blocking_gates)
            )

        provenance = (
            self._build_provenance(
                data=data,
                market_id=current_market,
                timestamp=timestamp,
                now=now,
            )
            if self.policy.include_provenance
            else {}
        )

        generated_at = self._utc_now_text(now)

        return OpportunityExplanation(
            instrument_id=instrument_id,
            symbol=symbol,
            status=explanation_status,
            tone=tone,
            headline=headline,
            summary=summary,
            decision_status=status,
            condition=condition,
            direction=direction,
            opportunity_type=opportunity_type,
            score=score,
            normalized_score=normalized_score,
            confidence=confidence,
            evidence_count=evidence_count,
            evidence_completeness=completeness,
            evidence_state=evidence_state,
            basis=basis,
            reasons=reasons,
            warnings=tuple(self._dedupe_strings(local_warnings)),
            evidence=tuple(evidence_items),
            gates=tuple(gates),
            expected_behavior=expected_behavior,
            invalidation=invalidation,
            risk_state=risk_state,
            provenance=provenance,
            generated_at=generated_at,
        )

    def explain_many(
        self,
        decisions: Iterable[Any],
        *,
        now: Optional[datetime] = None,
        market_id: Optional[str] = None,
    ) -> OpportunityExplanationResult:
        """Explain multiple existing decisions deterministically."""

        items = tuple(decisions)

        explanations = tuple(
            self.explain(
                item,
                now=now,
                market_id=market_id,
            )
            for item in items
        )

        complete_count = sum(
            1
            for item in explanations
            if item.status == ExplanationStatus.COMPLETE
        )

        partial_count = sum(
            1
            for item in explanations
            if item.status == ExplanationStatus.PARTIAL
        )

        unknown_count = sum(
            1
            for item in explanations
            if item.status == ExplanationStatus.UNKNOWN
        )

        overall_status = self._batch_status(
            complete_count=complete_count,
            partial_count=partial_count,
            unknown_count=unknown_count,
            total=len(explanations),
        )

        resolved_market = (
            self._clean_text(market_id)
            or self.market_id
            or (
                self._text(
                    self._to_mapping(items[0]),
                    "market_id",
                )
                if items
                else None
            )
        )

        timestamp = (
            explanations[0].provenance.get("decision_timestamp")
            if explanations
            else None
        )

        return OpportunityExplanationResult(
            status=overall_status,
            explanations=explanations,
            complete_count=complete_count,
            partial_count=partial_count,
            unknown_count=unknown_count,
            market_id=resolved_market,
            timestamp=timestamp,
            provenance={
                "engine": self.ENGINE_NAME,
                "engine_version": self.ENGINE_VERSION,
                "explanation_only": True,
                "decision_mutation": False,
                "count": len(explanations),
            },
        )

    def summarize(
        self,
        decision: Any,
        *,
        now: Optional[datetime] = None,
        market_id: Optional[str] = None,
    ) -> str:
        """Return only the deterministic human-readable summary."""

        return self.explain(
            decision,
            now=now,
            market_id=market_id,
        ).summary

    def to_dict(
        self,
        explanation: OpportunityExplanation,
    ) -> Dict[str, Any]:
        """Serialize an explanation to a JSON-safe dictionary."""

        return self._json_safe(asdict(explanation))

    def to_json(
        self,
        explanation: OpportunityExplanation,
        *,
        indent: Optional[int] = 2,
    ) -> str:
        """Serialize an explanation to JSON."""

        return json.dumps(
            self.to_dict(explanation),
            indent=indent,
            sort_keys=True,
            ensure_ascii=False,
        )

    def result_to_dict(
        self,
        result: OpportunityExplanationResult,
    ) -> Dict[str, Any]:
        """Serialize a batch explanation result."""

        return self._json_safe(asdict(result))

    def result_to_json(
        self,
        result: OpportunityExplanationResult,
        *,
        indent: Optional[int] = 2,
    ) -> str:
        """Serialize a batch explanation result."""

        return json.dumps(
            self.result_to_dict(result),
            indent=indent,
            sort_keys=True,
            ensure_ascii=False,
        )

    def get_engine_info(self) -> Dict[str, Any]:
        """Return stable engine metadata."""

        return {
            "engine_name": self.ENGINE_NAME,
            "engine_version": self.ENGINE_VERSION,
            "role": "decision_explanation",
            "creates_new_decision": False,
            "creates_new_score": False,
            "creates_execution_instruction": False,
            "recalculates_d6": False,
            "mutates_input": False,
            "deterministic": True,
        }
    # =========================================================================
    # EVIDENCE INTERPRETATION
    # =========================================================================

    def _build_evidence_items(
        self,
        data: Mapping[str, Any],
        *,
        completeness: Optional[float],
    ) -> List[ExplanationItem]:
        """
        Convert already-existing evidence fields into explanation items.

        IMPORTANT:
            This method only describes supplied evidence.
            It never derives a new signal from raw market data.
        """

        items: List[ExplanationItem] = []

        field_definitions = (
            (
                "trend_strength",
                "Trend",
                "Trend evidence supplied by the upstream opportunity pipeline.",
            ),
            (
                "volume_ratio",
                "Volume",
                "Volume participation evidence supplied by the upstream pipeline.",
            ),
            (
                "liquidity_score",
                "Liquidity",
                "Liquidity evidence supplied by the upstream pipeline.",
            ),
            (
                "risk_score",
                "Risk",
                "Risk evidence supplied by the upstream pipeline.",
            ),
            (
                "timing_score",
                "Timing",
                "Timing evidence supplied by the upstream pipeline.",
            ),
            (
                "derivatives_score",
                "Derivatives",
                "Derivative evidence supplied by the upstream pipeline.",
            ),
            (
                "participation_score",
                "Participation",
                "Participation evidence supplied by the upstream pipeline.",
            ),
            (
                "relationship_score",
                "Relationships",
                "Cross-market / relationship evidence supplied by the upstream pipeline.",
            ),
        )

        for field_name, title, description in field_definitions:
            if field_name not in data:
                continue

            raw_value = data.get(field_name)

            if raw_value is None:
                continue

            if isinstance(raw_value, str) and not raw_value.strip():
                continue

            items.append(
                ExplanationItem(
                    category="EVIDENCE",
                    title=title,
                    detail=description,
                    value=self._json_safe(raw_value),
                    source=self._text(
                        data,
                        f"{field_name}_source",
                        "evidence_source",
                    ),
                    importance=self._evidence_importance(
                        field_name,
                        raw_value,
                    ),
                )
            )

        # Existing named evidence records, if supplied by upstream engine.
        existing_evidence = data.get("evidence")

        if isinstance(existing_evidence, Sequence) and not isinstance(
            existing_evidence,
            (str, bytes, bytearray),
        ):
            for index, evidence in enumerate(existing_evidence):
                evidence_map = self._to_mapping(evidence)

                if not evidence_map:
                    continue

                title = (
                    self._text(
                        evidence_map,
                        "title",
                        "name",
                        "type",
                    )
                    or f"Evidence {index + 1}"
                )

                detail = (
                    self._text(
                        evidence_map,
                        "detail",
                        "description",
                        "reason",
                    )
                    or "Evidence supplied by upstream intelligence."
                )

                source = self._text(
                    evidence_map,
                    "source",
                    "source_id",
                    "provenance",
                )

                value = evidence_map.get(
                    "value",
                    evidence_map.get("score"),
                )

                items.append(
                    ExplanationItem(
                        category="EVIDENCE",
                        title=title,
                        detail=detail,
                        value=self._json_safe(value),
                        source=source,
                        importance=self._text(
                            evidence_map,
                            "importance",
                        ) or "NORMAL",
                    )
                )

        return items

    def _evidence_importance(
        self,
        field_name: str,
        value: Any,
    ) -> str:
        """Classify supplied evidence for display only."""

        if value is None:
            return "UNKNOWN"

        if field_name in {
            "trend_strength",
            "liquidity_score",
            "risk_score",
        }:
            return "HIGH"

        if field_name in {
            "timing_score",
            "derivatives_score",
            "participation_score",
        }:
            return "MEDIUM"

        return "NORMAL"

    def _evidence_state(
        self,
        *,
        evidence_count: int,
        completeness: Optional[float],
    ) -> EvidenceState:
        """
        Determine evidence availability state.

        This does NOT determine whether the opportunity is good or bad.
        """

        if completeness is not None:
            value = self._bounded_ratio(completeness)

            if value >= self.policy.strong_completeness:
                return EvidenceState.STRONG

            if value >= self.policy.adequate_completeness:
                return EvidenceState.ADEQUATE

            if value > 0:
                return EvidenceState.LIMITED

            return EvidenceState.MISSING

        if evidence_count >= 5:
            return EvidenceState.ADEQUATE

        if evidence_count > 0:
            return EvidenceState.LIMITED

        return EvidenceState.UNKNOWN

    # =========================================================================
    # GATE INTERPRETATION
    # =========================================================================

    def _build_gate_explanations(
        self,
        data: Mapping[str, Any],
    ) -> List[GateExplanation]:
        """
        Explain upstream gate states.

        No gate is recalculated here.
        """

        gates: List[GateExplanation] = []

        definitions = (
            ("liquidity_status", "Liquidity"),
            ("risk_status", "Risk"),
            ("timing_status", "Timing"),
            ("intraday_status", "Intraday"),
        )

        for field_name, display_name in definitions:
            if field_name not in data:
                continue

            raw_status = data.get(field_name)

            if raw_status is None:
                continue

            status = self._normalize_gate_status(raw_status)

            blocking = self._is_blocking_gate(
                status=status,
                data=data,
                field_name=field_name,
            )

            interpretation = self._gate_interpretation(
                display_name,
                status,
                blocking,
            )

            gates.append(
                GateExplanation(
                    name=display_name,
                    status=status,
                    interpretation=interpretation,
                    blocking=blocking,
                    source=self._text(
                        data,
                        f"{field_name}_source",
                        "gate_source",
                    ),
                )
            )

        # Support a prebuilt gate collection from upstream.
        supplied_gates = data.get("gates")

        if isinstance(supplied_gates, Sequence) and not isinstance(
            supplied_gates,
            (str, bytes, bytearray),
        ):
            for gate in supplied_gates:
                gate_map = self._to_mapping(gate)

                if not gate_map:
                    continue

                name = self._text(
                    gate_map,
                    "name",
                    "gate",
                    "type",
                )

                if not name:
                    continue

                status = self._normalize_gate_status(
                    gate_map.get("status")
                )

                blocking = bool(
                    gate_map.get(
                        "blocking",
                        self._is_blocking_gate(
                            status=status,
                            data=gate_map,
                            field_name="status",
                        ),
                    )
                )

                interpretation = (
                    self._text(
                        gate_map,
                        "interpretation",
                        "reason",
                        "detail",
                    )
                    or self._gate_interpretation(
                        name,
                        status,
                        blocking,
                    )
                )

                gates.append(
                    GateExplanation(
                        name=name,
                        status=status,
                        interpretation=interpretation,
                        blocking=blocking,
                        source=self._text(
                            gate_map,
                            "source",
                            "source_id",
                        ),
                    )
                )

        return self._dedupe_gates(gates)

    def _normalize_gate_status(
        self,
        value: Any,
    ) -> str:
        """Normalize gate text without changing its semantic meaning."""

        if value is None:
            return "UNKNOWN"

        if isinstance(value, bool):
            return "PASS" if value else "BLOCK"

        if isinstance(value, Enum):
            value = value.value

        text = str(value).strip().upper()

        if not text:
            return "UNKNOWN"

        aliases = {
            "OK": "PASS",
            "PASSED": "PASS",
            "TRUE": "PASS",
            "YES": "PASS",
            "VALID": "PASS",
            "CLEAR": "PASS",
            "BLOCKED": "BLOCK",
            "FAIL": "BLOCK",
            "FAILED": "BLOCK",
            "FALSE": "BLOCK",
            "NO": "BLOCK",
            "REJECT": "BLOCK",
            "REJECTED": "BLOCK",
            "CAUTION": "CAUTION",
            "WARNING": "CAUTION",
            "WARN": "CAUTION",
        }

        return aliases.get(text, text)

    def _is_blocking_gate(
        self,
        *,
        status: str,
        data: Mapping[str, Any],
        field_name: str,
    ) -> bool:
        """
        Determine whether an upstream gate is explicitly blocking.

        Explicit blocking information takes precedence.
        """

        explicit_field = f"{field_name}_blocking"

        if explicit_field in data:
            return bool(data.get(explicit_field))

        if "blocking" in data:
            # Only use a generic blocking flag when it is clearly attached
            # to this decision payload.
            return bool(data.get("blocking")) and status == "BLOCK"

        return status in {
            "BLOCK",
            "REJECT",
            "REJECTED",
            "FAIL",
            "FAILED",
        }

    def _gate_interpretation(
        self,
        name: str,
        status: str,
        blocking: bool,
    ) -> str:
        """Create neutral gate language."""

        if blocking:
            return (
                f"{name} gate is blocking according to the upstream "
                f"decision state."
            )

        if status == "PASS":
            return f"{name} gate is reported as passing."

        if status == "CAUTION":
            return (
                f"{name} gate carries a caution state in the "
                f"upstream decision."
            )

        if status == "UNKNOWN":
            return f"{name} gate state is unknown."

        return (
            f"{name} gate is reported as {status}; "
            f"the explainer does not reinterpret that state."
        )

    # =========================================================================
    # DECISION STATUS / TONE
    # =========================================================================

    def _explanation_status(
        self,
        *,
        data: Mapping[str, Any],
        status: Optional[str],
        evidence_state: EvidenceState,
        timestamp: Optional[str],
        current_market: Optional[str],
        instrument_id: Optional[str],
        symbol: Optional[str],
    ) -> ExplanationStatus:
        """
        Determine whether the explanation payload itself is complete.

        This does not judge the quality of the market decision.
        """

        missing_required: List[str] = []

        if self.policy.require_decision_status and not status:
            missing_required.append("decision_status")

        if (
            self.policy.require_symbol_or_instrument
            and not (instrument_id or symbol)
        ):
            missing_required.append("instrument")

        if self.policy.require_market_match:
            decision_market = self._text(data, "market_id")

            if (
                current_market
                and decision_market
                and decision_market != current_market
            ):
                return ExplanationStatus.UNKNOWN

        if self.policy.reject_future_data:
            if self._contains_future_data(data):
                return ExplanationStatus.UNKNOWN

        if missing_required:
            return ExplanationStatus.UNKNOWN

        if evidence_state in {
            EvidenceState.LIMITED,
            EvidenceState.MISSING,
            EvidenceState.UNKNOWN,
        }:
            return ExplanationStatus.PARTIAL

        if not timestamp:
            return ExplanationStatus.PARTIAL

        return ExplanationStatus.COMPLETE

    def _tone(
        self,
        *,
        decision_status: Optional[str],
        condition: Optional[str],
        evidence_state: EvidenceState,
    ) -> ExplanationTone:
        """
        Derive presentation tone from the existing decision state only.

        This is NOT a new trading signal.
        """

        status = (decision_status or "").strip().upper()
        cond = (condition or "").strip().upper()

        negative_states = {
            "REJECT",
            "REJECTED",
            "BLOCK",
            "BLOCKED",
            "INVALID",
            "NO_OPPORTUNITY",
            "NO_TRADE",
        }

        positive_states = {
            "PASS",
            "QUALIFIED",
            "VALID",
            "APPROVED",
            "ACTIVE",
            "OPPORTUNITY",
            "TRADABLE",
        }

        caution_states = {
            "CAUTION",
            "WATCH",
            "WAIT",
            "CONDITIONAL",
            "PARTIAL",
            "DEGRADED",
        }

        if status in negative_states or cond in negative_states:
            return ExplanationTone.NEGATIVE

        if status in positive_states or cond in positive_states:
            if evidence_state in {
                EvidenceState.LIMITED,
                EvidenceState.MISSING,
                EvidenceState.UNKNOWN,
            }:
                return ExplanationTone.CAUTION

            return ExplanationTone.POSITIVE

        if status in caution_states or cond in caution_states:
            return ExplanationTone.CAUTION

        if not status and not cond:
            return ExplanationTone.UNKNOWN

        return ExplanationTone.NEUTRAL

    # =========================================================================
    # HUMAN-READABLE NARRATIVE
    # =========================================================================

    def _headline(
        self,
        *,
        status: Optional[str],
        condition: Optional[str],
        direction: Optional[str],
        opportunity_type: Optional[str],
        symbol: Optional[str],
    ) -> str:
        """Build a deterministic headline from supplied fields."""

        subject = symbol or opportunity_type or "Opportunity"

        primary = (
            status
            or condition
            or opportunity_type
            or "UNKNOWN"
        )

        direction_text = (
            f" {direction}"
            if direction
            else ""
        )

        return (
            f"{subject}: {primary}{direction_text}"
        ).strip()

    def _summary(
        self,
        *,
        status: Optional[str],
        condition: Optional[str],
        direction: Optional[str],
        opportunity_type: Optional[str],
        score: Optional[float],
        confidence: Optional[float],
        evidence_state: EvidenceState,
        gates: Sequence[GateExplanation],
    ) -> str:
        """
        Produce concise deterministic explanation.

        Values are displayed exactly as supplied; no score is invented.
        """

        parts: List[str] = []

        decision_label = (
            status
            or condition
            or opportunity_type
            or "UNKNOWN"
        )

        parts.append(
            f"Upstream opportunity state: {decision_label}."
        )

        if direction:
            parts.append(
                f"Direction supplied by the decision: {direction}."
            )

        if score is not None:
            parts.append(
                f"Opportunity score supplied by upstream engine: "
                f"{self._format_number(score)}."
            )

        if confidence is not None:
            parts.append(
                f"Confidence supplied by upstream engine: "
                f"{self._format_number(confidence)}."
            )

        parts.append(
            f"Evidence state: {evidence_state.value}."
        )

        blocking = [
            gate.name
            for gate in gates
            if gate.blocking
        ]

        if blocking:
            parts.append(
                "Blocking gate(s): " + ", ".join(blocking) + "."
            )
        elif gates:
            parts.append(
                "No explicitly blocking gate is reported."
            )

        return " ".join(parts)

    # =========================================================================
    # PROVENANCE / DATA INTEGRITY
    # =========================================================================

    def _build_provenance(
        self,
        *,
        data: Mapping[str, Any],
        market_id: Optional[str],
        timestamp: Optional[str],
        now: Optional[datetime],
    ) -> Dict[str, Any]:
        """Preserve provenance without inventing source identifiers."""

        provenance: Dict[str, Any] = {
            "engine": self.ENGINE_NAME,
            "engine_version": self.ENGINE_VERSION,
            "role": "decision_explanation",
            "decision_timestamp": timestamp,
            "market_id": market_id,
            "explanation_only": True,
            "decision_mutation": False,
            "new_signal_created": False,
            "new_score_created": False,
        }

        for field_name in (
            "decision_id",
            "opportunity_id",
            "event_id",
            "trace_id",
            "request_id",
            "source_id",
            "source",
            "engine",
            "engine_version",
        ):
            if field_name in data and data.get(field_name) is not None:
                provenance[field_name] = self._json_safe(
                    data.get(field_name)
                )

        if now is not None:
            provenance["explanation_reference_time"] = (
                self._utc_now_text(now)
            )

        return provenance

    def _contains_future_data(
        self,
        data: Mapping[str, Any],
    ) -> bool:
        """
        Detect explicit future-data markers.

        This does not attempt to infer future data from prices.
        """

        for key in (
            "future_data",
            "lookahead",
            "look_ahead",
            "contains_future_data",
        ):
            if key in data and bool(data.get(key)):
                return True

        validation = data.get("validation")

        if isinstance(validation, Mapping):
            for key in (
                "future_data",
                "lookahead",
                "look_ahead",
                "contains_future_data",
            ):
                if bool(validation.get(key)):
                    return True

        return False

    # =========================================================================
    # BATCH HELPERS
    # =========================================================================

    def _batch_status(
        self,
        *,
        complete_count: int,
        partial_count: int,
        unknown_count: int,
        total: int,
    ) -> ExplanationStatus:
        """Determine aggregate explanation completeness."""

        if total == 0:
            return ExplanationStatus.UNKNOWN

        if unknown_count == total:
            return ExplanationStatus.UNKNOWN

        if complete_count == total:
            return ExplanationStatus.COMPLETE

        return ExplanationStatus.PARTIAL

    # =========================================================================
    # GENERIC DATA HELPERS
    # =========================================================================

    @staticmethod
    def _to_mapping(
        value: Any,
    ) -> Dict[str, Any]:
        """Convert supported objects into a shallow mapping."""

        if value is None:
            return {}

        if isinstance(value, Mapping):
            return dict(value)

        if hasattr(value, "to_dict"):
            try:
                result = value.to_dict()
                if isinstance(result, Mapping):
                    return dict(result)
            except Exception:
                pass

        if hasattr(value, "__dataclass_fields__"):
            try:
                return asdict(value)
            except Exception:
                pass

        if hasattr(value, "__dict__"):
            try:
                return dict(vars(value))
            except Exception:
                pass

        return {}

    @staticmethod
    def _clean_text(
        value: Any,
    ) -> Optional[str]:
        """Return stripped text or None."""

        if value is None:
            return None

        text = str(value).strip()

        return text or None

    def _text(
        self,
        data: Mapping[str, Any],
        *keys: str,
    ) -> Optional[str]:
        """Return the first non-empty textual field."""

        for key in keys:
            if key not in data:
                continue

            value = self._clean_text(data.get(key))

            if value is not None:
                return value

        return None

    @staticmethod
    def _number(
        value: Any,
    ) -> Optional[float]:
        """Safely parse finite numeric values."""

        if value is None:
            return None

        if isinstance(value, bool):
            return None

        try:
            number = float(value)
        except (TypeError, ValueError):
            return None

        if not math.isfinite(number):
            return None

        return number

    def _number_from_mapping(
        self,
        data: Mapping[str, Any],
        *keys: str,
    ) -> Optional[float]:
        """Return first finite numeric field."""

        for key in keys:
            if key not in data:
                continue

            value = self._number(data.get(key))

            if value is not None:
                return value

        return None

    @staticmethod
    def _integer(
        value: Any,
        *,
        default: int = 0,
    ) -> int:
        """Safely convert a value to a non-negative integer."""

        if value is None:
            return default

        if isinstance(value, bool):
            return default

        try:
            number = int(value)
        except (TypeError, ValueError):
            return default

        return max(0, number)

    @staticmethod
    def _bounded_ratio(
        value: Any,
    ) -> float:
        """
        Normalize a ratio for explanation purposes.

        0..1 is treated as ratio.
        0..100 is treated as percentage.

        This is only used for evidence completeness classification.
        """

        number = OpportunityExplainer._number(value)

        if number is None:
            return 0.0

        if number > 1.0 and number <= 100.0:
            number = number / 100.0

        return max(0.0, min(1.0, number))

    @staticmethod
    def _format_number(
        value: float,
    ) -> str:
        """Stable human-readable number formatting."""

        if float(value).is_integer():
            return str(int(value))

        return f"{value:.4f}".rstrip("0").rstrip(".")

    @staticmethod
    def _timestamp_text(
        value: Any,
    ) -> Optional[str]:
        """Preserve timestamp as supplied when possible."""

        if value is None:
            return None

        if isinstance(value, datetime):
            return value.isoformat()

        text = str(value).strip()

        return text or None

    @staticmethod
    def _utc_now_text(
        value: Optional[datetime] = None,
    ) -> str:
        """Return a deterministic UTC timestamp for generated metadata."""

        current = value or datetime.now(timezone.utc)

        if current.tzinfo is None:
            current = current.replace(tzinfo=timezone.utc)

        return current.astimezone(timezone.utc).isoformat()

    @staticmethod
    def _string_tuple(
        value: Any,
    ) -> Tuple[str, ...]:
        """Convert supported string collections to a clean tuple."""

        if value is None:
            return ()

        if isinstance(value, str):
            text = value.strip()
            return (text,) if text else ()

        if isinstance(value, Sequence):
            result: List[str] = []

            for item in value:
                text = str(item).strip()

                if text:
                    result.append(text)

            return tuple(result)

        return ()

    @staticmethod
    def _dedupe_strings(
        values: Sequence[str],
    ) -> List[str]:
        """Stable de-duplication preserving order."""

        seen = set()
        result: List[str] = []

        for value in values:
            text = str(value).strip()

            if not text:
                continue

            key = text.casefold()

            if key in seen:
                continue

            seen.add(key)
            result.append(text)

        return result

    @staticmethod
    def _dedupe_gates(
        gates: Sequence[GateExplanation],
    ) -> List[GateExplanation]:
        """Stable de-duplication of gate explanations."""

        result: List[GateExplanation] = []
        seen = set()

        for gate in gates:
            key = (
                gate.name.casefold(),
                gate.status,
                gate.blocking,
            )

            if key in seen:
                continue

            seen.add(key)
            result.append(gate)

        return result

    @staticmethod
    def _json_safe(
        value: Any,
    ) -> Any:
        """Convert common Python values into JSON-safe structures."""

        if value is None:
            return None

        if isinstance(value, (str, int, float, bool)):
            if isinstance(value, float) and not math.isfinite(value):
                return None

            return value

        if isinstance(value, datetime):
            return value.isoformat()

        if isinstance(value, Mapping):
            return {
                str(key): OpportunityExplainer._json_safe(item)
                for key, item in value.items()
            }

        if isinstance(value, Sequence) and not isinstance(
            value,
            (str, bytes, bytearray),
        ):
            return [
                OpportunityExplainer._json_safe(item)
                for item in value
            ]

        return str(value)


# ============================================================================
# FACTORY
# ============================================================================


def create_opportunity_explainer(
    *,
    market_id: Optional[str] = None,
    policy: Optional[ExplainerPolicy] = None,
) -> OpportunityExplainer:
    """
    Factory for application integration.

    Keeps construction centralized so future policy changes do not require
    changes across callers.
    """

    return OpportunityExplainer(
        policy=policy,
        market_id=market_id,
    )


# ============================================================================
# MODULE SELF-CHECK
# ============================================================================


def self_check() -> Dict[str, Any]:
    """
    Lightweight structural self-check.

    This verifies the explainer's own contract only.
    It does NOT claim market intelligence correctness.
    """

    explainer = OpportunityExplainer()

    sample_decision = {
        "instrument_id": "TEST",
        "symbol": "TEST",
        "market_id": "TEST_MARKET",
        "status": "QUALIFIED",
        "direction": "BUY",
        "opportunity_type": "MOMENTUM",
        "opportunity_score": 82.5,
        "confidence": 0.81,
        "evidence_count": 6,
        "evidence_completeness": 0.80,
        "liquidity_status": "PASS",
        "risk_status": "PASS",
        "timing_status": "PASS",
        "intraday_status": "PASS",
        "reasons": [
            "Upstream evidence supports the opportunity."
        ],
        "expected_behavior": "Continuation if qualifying conditions persist.",
        "invalidation": "Invalid if upstream invalidation condition is triggered.",
        "risk_state": "CONTROLLED",
        "timestamp": "2026-09-05T10:00:00+05:30",
        "decision_id": "SELF_CHECK",
    }

    explanation = explainer.explain(
        sample_decision,
        now=datetime(
            2026,
            9,
            5,
            10,
            1,
            tzinfo=timezone.utc,
        ),
        market_id="TEST_MARKET",
    )

    payload = explainer.to_dict(explanation)

    checks = {
        "engine_exists": isinstance(
            explainer,
            OpportunityExplainer,
        ),
        "headline_present": bool(
            payload.get("headline")
        ),
        "summary_present": bool(
            payload.get("summary")
        ),
        "evidence_present": bool(
            payload.get("evidence")
        ),
        "gates_present": bool(
            payload.get("gates")
        ),
        "provenance_present": bool(
            payload.get("provenance")
        ),
        "decision_mutation_disabled": (
            payload["provenance"].get(
                "decision_mutation"
            ) is False
        ),
        "new_signal_disabled": (
            payload["provenance"].get(
                "new_signal_created"
            ) is False
        ),
        "new_score_disabled": (
            payload["provenance"].get(
                "new_score_created"
            ) is False
        ),
    }

    return {
        "status": (
            "PASS"
            if all(checks.values())
            else "FAIL"
        ),
        "checks": checks,
        "engine": explainer.get_engine_info(),
    }


__all__ = [
    "ExplanationStatus",
    "ExplanationTone",
    "EvidenceState",
    "ExplanationItem",
    "GateExplanation",
    "OpportunityExplanation",
    "OpportunityExplanationResult",
    "ExplainerPolicy",
    "OpportunityExplainer",
    "create_opportunity_explainer",
    "self_check",
]
# ============================================================================
# PART 3
# PRODUCTION VALIDATION / INTEGRATION / RENDERING
# ============================================================================


# ============================================================================
# VALIDATION RESULT OBJECTS
# ============================================================================


@dataclass(frozen=True)
class ExplainerValidationIssue:
    """One structural validation issue."""

    code: str
    message: str
    severity: str = "ERROR"
    field: Optional[str] = None


@dataclass(frozen=True)
class ExplainerValidationResult:
    """Validation result for an existing explanation."""

    valid: bool
    status: ExplanationStatus
    issues: Tuple[ExplainerValidationIssue, ...] = ()
    checked_fields: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "status": self.status.value,
            "issues": [
                {
                    "code": issue.code,
                    "message": issue.message,
                    "severity": issue.severity,
                    "field": issue.field,
                }
                for issue in self.issues
            ],
            "checked_fields": list(self.checked_fields),
        }


# ============================================================================
# EXPLAINER VALIDATOR
# ============================================================================


class OpportunityExplainerValidator:
    """
    Structural validator for OpportunityExplanation.

    IMPORTANT:
        This validator checks explanation integrity.
        It does not validate whether the market decision itself was correct.
    """

    REQUIRED_FIELDS = (
        "status",
        "tone",
        "headline",
        "summary",
        "evidence_state",
        "provenance",
    )

    def validate(
        self,
        explanation: Any,
    ) -> ExplainerValidationResult:
        """Validate an explanation object."""

        issues: List[ExplainerValidationIssue] = []

        if not isinstance(
            explanation,
            OpportunityExplanation,
        ):
            return ExplainerValidationResult(
                valid=False,
                status=ExplanationStatus.UNKNOWN,
                issues=(
                    ExplainerValidationIssue(
                        code="INVALID_TYPE",
                        message=(
                            "Expected OpportunityExplanation instance."
                        ),
                    ),
                ),
            )

        for field_name in self.REQUIRED_FIELDS:
            if not hasattr(explanation, field_name):
                issues.append(
                    ExplainerValidationIssue(
                        code="MISSING_FIELD",
                        message=(
                            f"Required explanation field is missing: "
                            f"{field_name}."
                        ),
                        field=field_name,
                    )
                )

        self._validate_enum(
            issues,
            "status",
            explanation.status,
            ExplanationStatus,
        )

        self._validate_enum(
            issues,
            "tone",
            explanation.tone,
            ExplanationTone,
        )

        self._validate_enum(
            issues,
            "evidence_state",
            explanation.evidence_state,
            EvidenceState,
        )

        if not self._non_empty_text(explanation.headline):
            issues.append(
                ExplainerValidationIssue(
                    code="EMPTY_HEADLINE",
                    message="Explanation headline is empty.",
                    field="headline",
                )
            )

        if not self._non_empty_text(explanation.summary):
            issues.append(
                ExplainerValidationIssue(
                    code="EMPTY_SUMMARY",
                    message="Explanation summary is empty.",
                    field="summary",
                )
            )

        if explanation.evidence_count < 0:
            issues.append(
                ExplainerValidationIssue(
                    code="NEGATIVE_EVIDENCE_COUNT",
                    message="Evidence count cannot be negative.",
                    field="evidence_count",
                )
            )

        if explanation.evidence_completeness is not None:
            completeness = OpportunityExplainer._number(
                explanation.evidence_completeness
            )

            if completeness is None:
                issues.append(
                    ExplainerValidationIssue(
                        code="INVALID_COMPLETENESS",
                        message=(
                            "Evidence completeness must be numeric "
                            "when supplied."
                        ),
                        field="evidence_completeness",
                    )
                )

        if explanation.confidence is not None:
            confidence = OpportunityExplainer._number(
                explanation.confidence
            )

            if confidence is None:
                issues.append(
                    ExplainerValidationIssue(
                        code="INVALID_CONFIDENCE",
                        message=(
                            "Confidence must be numeric when supplied."
                        ),
                        field="confidence",
                    )
                )

        if not isinstance(explanation.provenance, Mapping):
            issues.append(
                ExplainerValidationIssue(
                    code="INVALID_PROVENANCE",
                    message="Provenance must be a mapping.",
                    field="provenance",
                )
            )

        provenance = explanation.provenance

        if provenance.get("decision_mutation") is not False:
            issues.append(
                ExplainerValidationIssue(
                    code="MUTATION_FLAG_INVALID",
                    message=(
                        "Explainer provenance must explicitly declare "
                        "decision_mutation=False."
                    ),
                    field="provenance",
                )
            )

        if provenance.get("new_signal_created") is not False:
            issues.append(
                ExplainerValidationIssue(
                    code="SIGNAL_CREATION_FLAG_INVALID",
                    message=(
                        "Explainer provenance must explicitly declare "
                        "new_signal_created=False."
                    ),
                    field="provenance",
                )
            )

        if provenance.get("new_score_created") is not False:
            issues.append(
                ExplainerValidationIssue(
                    code="SCORE_CREATION_FLAG_INVALID",
                    message=(
                        "Explainer provenance must explicitly declare "
                        "new_score_created=False."
                    ),
                    field="provenance",
                )
            )

        for index, gate in enumerate(explanation.gates):
            self._validate_gate(
                issues,
                gate,
                index,
            )

        for index, evidence in enumerate(explanation.evidence):
            self._validate_evidence(
                issues,
                evidence,
                index,
            )

        status = (
            ExplanationStatus.COMPLETE
            if not issues
            else ExplanationStatus.PARTIAL
        )

        return ExplainerValidationResult(
            valid=not issues,
            status=status,
            issues=tuple(issues),
            checked_fields=tuple(self.REQUIRED_FIELDS),
        )

    @staticmethod
    def _validate_enum(
        issues: List[ExplainerValidationIssue],
        field_name: str,
        value: Any,
        enum_type: Any,
    ) -> None:
        if not isinstance(value, enum_type):
            issues.append(
                ExplainerValidationIssue(
                    code="INVALID_ENUM",
                    message=(
                        f"{field_name} contains an invalid enum value."
                    ),
                    field=field_name,
                )
            )

    @staticmethod
    def _validate_gate(
        issues: List[ExplainerValidationIssue],
        gate: Any,
        index: int,
    ) -> None:
        if not isinstance(gate, GateExplanation):
            issues.append(
                ExplainerValidationIssue(
                    code="INVALID_GATE",
                    message=(
                        f"Gate at index {index} is not "
                        f"GateExplanation."
                    ),
                    field=f"gates[{index}]",
                )
            )
            return

        if not gate.name.strip():
            issues.append(
                ExplainerValidationIssue(
                    code="EMPTY_GATE_NAME",
                    message="Gate name is empty.",
                    field=f"gates[{index}].name",
                )
            )

        if not gate.status.strip():
            issues.append(
                ExplainerValidationIssue(
                    code="EMPTY_GATE_STATUS",
                    message="Gate status is empty.",
                    field=f"gates[{index}].status",
                )
            )

    @staticmethod
    def _validate_evidence(
        issues: List[ExplainerValidationIssue],
        evidence: Any,
        index: int,
    ) -> None:
        if not isinstance(evidence, ExplanationItem):
            issues.append(
                ExplainerValidationIssue(
                    code="INVALID_EVIDENCE",
                    message=(
                        f"Evidence at index {index} is not "
                        f"ExplanationItem."
                    ),
                    field=f"evidence[{index}]",
                )
            )
            return

        if not evidence.title.strip():
            issues.append(
                ExplainerValidationIssue(
                    code="EMPTY_EVIDENCE_TITLE",
                    message="Evidence title is empty.",
                    field=f"evidence[{index}].title",
                )
            )

    @staticmethod
    def _non_empty_text(value: Any) -> bool:
        return (
            isinstance(value, str)
            and bool(value.strip())
        )


# ============================================================================
# PRESENTATION RENDERER
# ============================================================================


class OpportunityExplanationRenderer:
    """
    Converts an already-created explanation into UI-safe text structures.

    No market interpretation is performed here.
    """

    def render_compact(
        self,
        explanation: OpportunityExplanation,
    ) -> Dict[str, Any]:
        """
        Compact Terminal / Opportunity Card representation.
        """

        return {
            "headline": explanation.headline,
            "summary": explanation.summary,
            "status": explanation.status.value,
            "tone": explanation.tone.value,
            "direction": explanation.direction,
            "score": explanation.score,
            "confidence": explanation.confidence,
            "evidence_state": explanation.evidence_state.value,
            "risk_state": explanation.risk_state,
            "warnings": list(explanation.warnings),
        }

    def render_detailed(
        self,
        explanation: OpportunityExplanation,
    ) -> Dict[str, Any]:
        """
        Detailed Research / Opportunity Inspector representation.
        """

        return {
            "identity": {
                "instrument_id": explanation.instrument_id,
                "symbol": explanation.symbol,
                "opportunity_type": explanation.opportunity_type,
            },
            "decision": {
                "status": explanation.decision_status,
                "condition": explanation.condition,
                "direction": explanation.direction,
                "score": explanation.score,
                "normalized_score": explanation.normalized_score,
                "confidence": explanation.confidence,
            },
            "evidence": {
                "state": explanation.evidence_state.value,
                "count": explanation.evidence_count,
                "completeness": explanation.evidence_completeness,
                "items": [
                    {
                        "category": item.category,
                        "title": item.title,
                        "detail": item.detail,
                        "value": item.value,
                        "source": item.source,
                        "importance": item.importance,
                    }
                    for item in explanation.evidence
                ],
            },
            "gates": [
                {
                    "name": gate.name,
                    "status": gate.status,
                    "interpretation": gate.interpretation,
                    "blocking": gate.blocking,
                    "source": gate.source,
                }
                for gate in explanation.gates
            ],
            "thesis": {
                "basis": explanation.basis,
                "expected_behavior": explanation.expected_behavior,
                "invalidation": explanation.invalidation,
                "risk_state": explanation.risk_state,
                "reasons": list(explanation.reasons),
                "warnings": list(explanation.warnings),
            },
            "provenance": dict(explanation.provenance),
            "generated_at": explanation.generated_at,
        }

    def render_text(
        self,
        explanation: OpportunityExplanation,
    ) -> str:
        """
        Human-readable multiline explanation.

        Suitable for logs, Chat, Research Lab and audit records.
        """

        lines: List[str] = [
            explanation.headline,
            "",
            explanation.summary,
        ]

        if explanation.basis:
            lines.extend(
                [
                    "",
                    f"Basis: {explanation.basis}",
                ]
            )

        if explanation.expected_behavior:
            lines.extend(
                [
                    "",
                    (
                        "Expected behavior: "
                        f"{explanation.expected_behavior}"
                    ),
                ]
            )

        if explanation.invalidation:
            lines.extend(
                [
                    "",
                    f"Invalidation: {explanation.invalidation}",
                ]
            )

        if explanation.risk_state:
            lines.extend(
                [
                    "",
                    f"Risk state: {explanation.risk_state}",
                ]
            )

        if explanation.reasons:
            lines.extend(
                [
                    "",
                    "Reasons:",
                ]
            )

            lines.extend(
                f"- {reason}"
                for reason in explanation.reasons
            )

        if explanation.gates:
            lines.extend(
                [
                    "",
                    "Gates:",
                ]
            )

            for gate in explanation.gates:
                marker = "BLOCKING" if gate.blocking else gate.status

                lines.append(
                    f"- {gate.name}: {marker} — "
                    f"{gate.interpretation}"
                )

        if explanation.warnings:
            lines.extend(
                [
                    "",
                    "Warnings:",
                ]
            )

            lines.extend(
                f"- {warning}"
                for warning in explanation.warnings
            )

        return "\n".join(lines)


# ============================================================================
# SAFE INTEGRATION ADAPTER
# ============================================================================


class OpportunityExplainerAdapter:
    """
    Application-facing adapter.

    Intended integration:

        opportunity_engine_output
                |
                v
        OpportunityExplainerAdapter
                |
                +--> explanation
                +--> validation
                +--> compact UI
                +--> detailed UI
                +--> audit text

    The adapter never mutates the source decision.
    """

    def __init__(
        self,
        explainer: Optional[OpportunityExplainer] = None,
        validator: Optional[OpportunityExplainerValidator] = None,
        renderer: Optional[OpportunityExplanationRenderer] = None,
    ) -> None:
        self.explainer = (
            explainer
            or OpportunityExplainer()
        )

        self.validator = (
            validator
            or OpportunityExplainerValidator()
        )

        self.renderer = (
            renderer
            or OpportunityExplanationRenderer()
        )

    def process(
        self,
        decision: Any,
        *,
        now: Optional[datetime] = None,
        market_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Full safe explanation pipeline.

        Returns:
            {
                "explanation": ...,
                "validation": ...,
                "compact": ...,
                "detailed": ...,
                "text": ...
            }
        """

        # Preserve source object identity by never modifying it.
        explanation = self.explainer.explain(
            decision,
            now=now,
            market_id=market_id,
        )

        validation = self.validator.validate(
            explanation
        )

        return {
            "explanation": self.explainer.to_dict(
                explanation
            ),
            "validation": validation.to_dict(),
            "compact": self.renderer.render_compact(
                explanation
            ),
            "detailed": self.renderer.render_detailed(
                explanation
            ),
            "text": self.renderer.render_text(
                explanation
            ),
        }

    def process_many(
        self,
        decisions: Iterable[Any],
        *,
        now: Optional[datetime] = None,
        market_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Batch-safe explanation pipeline."""

        result = self.explainer.explain_many(
            decisions,
            now=now,
            market_id=market_id,
        )

        validations = tuple(
            self.validator.validate(item)
            for item in result.explanations
        )

        return {
            "result": self.explainer.result_to_dict(
                result
            ),
            "validations": [
                validation.to_dict()
                for validation in validations
            ],
            "compact": [
                self.renderer.render_compact(item)
                for item in result.explanations
            ],
        }


# ============================================================================
# INTEGRATION HELPERS
# ============================================================================


def explain_opportunity(
    decision: Any,
    *,
    market_id: Optional[str] = None,
    now: Optional[datetime] = None,
) -> OpportunityExplanation:
    """
    Convenience function.

    This is the preferred lightweight integration point for callers that
    only need the explanation object.
    """

    explainer = OpportunityExplainer(
        market_id=market_id,
    )

    return explainer.explain(
        decision,
        now=now,
        market_id=market_id,
    )


def explain_opportunity_dict(
    decision: Any,
    *,
    market_id: Optional[str] = None,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Convenience function returning JSON-safe output.
    """

    explainer = OpportunityExplainer(
        market_id=market_id,
    )

    explanation = explainer.explain(
        decision,
        now=now,
        market_id=market_id,
    )

    return explainer.to_dict(
        explanation
    )


def validate_opportunity_explanation(
    explanation: OpportunityExplanation,
) -> ExplainerValidationResult:
    """Convenience validator."""

    return OpportunityExplainerValidator().validate(
        explanation
    )


def render_opportunity_explanation(
    explanation: OpportunityExplanation,
) -> Dict[str, Any]:
    """Convenience renderer."""

    return OpportunityExplanationRenderer().render_detailed(
        explanation
    )


# ============================================================================
# EXTENDED SELF-CHECK
# ============================================================================


def production_self_check() -> Dict[str, Any]:
    """
    Full structural self-check for production integration.

    IMPORTANT:
        PASS here means the explainer's own contract is internally valid.
        It does NOT mean the upstream market decision is profitable,
        accurate, or validated against historical/live market outcomes.
    """

    fixed_now = datetime(
        2026,
        9,
        5,
        10,
        1,
        tzinfo=timezone.utc,
    )

    source_decision = {
        "instrument_id": "NIFTY-TEST",
        "symbol": "NIFTY",
        "market_id": "NSE",
        "status": "QUALIFIED",
        "condition": "VALID",
        "direction": "BUY",
        "opportunity_type": "TREND",
        "opportunity_score": 84.25,
        "normalized_score": 0.8425,
        "confidence": 0.86,
        "evidence_count": 8,
        "evidence_completeness": 0.875,
        "trend_strength": 0.88,
        "volume_ratio": 1.42,
        "liquidity_score": 0.91,
        "risk_score": 0.78,
        "timing_score": 0.82,
        "derivatives_score": 0.80,
        "participation_score": 0.84,
        "relationship_score": 0.76,
        "liquidity_status": "PASS",
        "risk_status": "PASS",
        "timing_status": "PASS",
        "intraday_status": "PASS",
        "basis": "Upstream opportunity decision basis.",
        "expected_behavior": (
            "Expected continuation while qualifying conditions persist."
        ),
        "invalidation": (
            "Use the upstream invalidation condition."
        ),
        "risk_state": "CONTROLLED",
        "reasons": (
            "Trend evidence is present.",
            "Participation evidence is present.",
        ),
        "warnings": (),
        "decision_id": "SELF-CHECK-001",
        "event_id": "SELF-CHECK-EVENT-001",
        "source_id": "SELF-CHECK-SOURCE",
        "timestamp": "2026-09-05T10:00:00+05:30",
    }

    # ------------------------------------------------------------------
    # Source immutability check
    # ------------------------------------------------------------------

    original_source = dict(source_decision)

    adapter = OpportunityExplainerAdapter()

    result = adapter.process(
        source_decision,
        now=fixed_now,
        market_id="NSE",
    )

    source_unchanged = (
        source_decision == original_source
    )

    explainer = OpportunityExplainer(
        market_id="NSE",
    )

    authoritative_explanation = explainer.explain(
        source_decision,
        now=fixed_now,
        market_id="NSE",
    )

    validation = validate_opportunity_explanation(
        authoritative_explanation
    )

    rendered = render_opportunity_explanation(
        authoritative_explanation
    )

    compact = OpportunityExplanationRenderer().render_compact(
        authoritative_explanation
    )

    json_output = explainer.to_json(
        authoritative_explanation
    )

    checks = {
        "adapter_completed": bool(result),
        "source_unchanged": source_unchanged,
        "validation_passed": validation.valid,
        "headline_present": bool(
            authoritative_explanation.headline
        ),
        "summary_present": bool(
            authoritative_explanation.summary
        ),
        "evidence_rendered": bool(
            authoritative_explanation.evidence
        ),
        "gates_rendered": bool(
            authoritative_explanation.gates
        ),
        "compact_rendered": bool(compact),
        "detailed_rendered": bool(rendered),
        "json_serialization": bool(json_output),
        "decision_mutation_false": (
            authoritative_explanation.provenance.get(
                "decision_mutation"
            ) is False
        ),
        "new_signal_false": (
            authoritative_explanation.provenance.get(
                "new_signal_created"
            ) is False
        ),
        "new_score_false": (
            authoritative_explanation.provenance.get(
                "new_score_created"
            ) is False
        ),
    }

    return {
        "status": (
            "PASS"
            if all(checks.values())
            else "FAIL"
        ),
        "checks": checks,
        "validation": validation.to_dict(),
        "engine": explainer.get_engine_info(),
    }


# ============================================================================
# FINAL EXPORT CONTRACT
# ============================================================================


__all__ = [
    # Enums
    "ExplanationStatus",
    "ExplanationTone",
    "EvidenceState",

    # Core data contracts
    "ExplanationItem",
    "GateExplanation",
    "OpportunityExplanation",
    "OpportunityExplanationResult",
    "ExplainerPolicy",

    # Validation
    "ExplainerValidationIssue",
    "ExplainerValidationResult",
    "OpportunityExplainerValidator",

    # Core engine
    "OpportunityExplainer",
    "create_opportunity_explainer",

    # Presentation
    "OpportunityExplanationRenderer",

    # Application adapter
    "OpportunityExplainerAdapter",

    # Convenience helpers
    "explain_opportunity",
    "explain_opportunity_dict",
    "validate_opportunity_explanation",
    "render_opportunity_explanation",

    # Diagnostics
    "self_check",
    "production_self_check",
]


# ============================================================================
# OPTIONAL DIRECT EXECUTION
# ============================================================================


if __name__ == "__main__":
    check = production_self_check()

    print(
        json.dumps(
            check,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
    )


