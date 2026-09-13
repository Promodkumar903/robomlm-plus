"""
ROBOMLM_PLUS
Decision Explainer
-----------------

ROLE
----
Explain an existing D13 decision and its CURRENT JOURNEY.

D13 remains the ONLY decision authority.

This module MUST NOT:
    - create BUY / SELL / HOLD
    - override D13
    - vote against D13
    - create an independent decision score
    - use future outcome information
    - modify the original D13 record

It answers:

    WHY did D13 make this decision?
    WHAT is supporting it now?
    WHAT is weakening it now?
    IS the thesis still intact?
    SHOULD the existing decision be followed, watched, or exited?
    WHAT has changed during the decision journey?

Management context:
    FOLLOW
    CAUTION
    EXIT

EXIT is a lifecycle/management interpretation of an existing D13
decision, NOT a new BUY/SELL decision.

Exact proprietary V6 explanatory formula is not assumed here.
The module is evidence/provenance driven.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence


# ============================================================================
# ENUMS
# ============================================================================

class DecisionAction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    WAIT = "WAIT"
    NO_ACTION = "NO_ACTION"
    BLOCKED = "BLOCKED"


class DecisionState(str, Enum):
    SETUP = "SETUP"
    READY = "READY"
    ACTIVE = "ACTIVE"
    STRENGTHENING = "STRENGTHENING"
    WEAKENING = "WEAKENING"
    INVALIDATED = "INVALIDATED"
    EXIT = "EXIT"
    CLOSED = "CLOSED"
    BLOCKED = "BLOCKED"
    EXPIRED = "EXPIRED"


class ManagementAction(str, Enum):
    FOLLOW = "FOLLOW"
    CAUTION = "CAUTION"
    EXIT = "EXIT"
    WAIT = "WAIT"
    NO_ACTION = "NO_ACTION"
    BLOCKED = "BLOCKED"


class EvidencePolarity(str, Enum):
    SUPPORT = "SUPPORT"
    CONTRADICTION = "CONTRADICTION"
    CAUTION = "CAUTION"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"


class ExplanationStatus(str, Enum):
    READY = "READY"
    LIMITED = "LIMITED"
    BLOCKED = "BLOCKED"
    UNDETERMINED = "UNDETERMINED"


class ExplanationReason(str, Enum):
    D13_DECISION = "D13_DECISION"
    CURRENT_STATE = "CURRENT_STATE"

    SUPPORTING_EVIDENCE = "SUPPORTING_EVIDENCE"
    CONTRADICTING_EVIDENCE = "CONTRADICTING_EVIDENCE"
    CAUTION_EVIDENCE = "CAUTION_EVIDENCE"

    THESIS_INTACT = "THESIS_INTACT"
    THESIS_STRENGTHENING = "THESIS_STRENGTHENING"
    THESIS_WEAKENING = "THESIS_WEAKENING"

    INVALIDATION_TRIGGERED = "INVALIDATION_TRIGGERED"
    EXIT_REQUIRED = "EXIT_REQUIRED"

    MISSING_LIVE_EVIDENCE = "MISSING_LIVE_EVIDENCE"
    STALE_EVIDENCE = "STALE_EVIDENCE"

    FUTURE_DATA = "FUTURE_DATA"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    TIMESTAMP_ERROR = "TIMESTAMP_ERROR"

    EXPLANATION_GENERATED = "EXPLANATION_GENERATED"


# ============================================================================
# HELPERS
# ============================================================================

def _utc(value: datetime) -> Optional[datetime]:
    if not isinstance(value, datetime):
        return None

    if value.tzinfo is None:
        return None

    return value.astimezone(timezone.utc)


# ============================================================================
# D13 SNAPSHOT
# ============================================================================

@dataclass(frozen=True)
class D13DecisionSnapshot:
    """
    Immutable snapshot of the actual D13 decision.
    """

    decision_id: str
    market_id: str
    action: DecisionAction
    decision_timestamp: datetime

    scenario: Optional[str] = None
    horizon: Optional[str] = None

    thesis: Optional[str] = None
    invalidation_condition: Optional[str] = None

    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:

        if not self.decision_id:
            raise ValueError("decision_id is required")

        if not self.market_id:
            raise ValueError("market_id is required")

        if self.decision_timestamp.tzinfo is None:
            raise ValueError(
                "decision_timestamp must be timezone-aware"
            )


# ============================================================================
# CURRENT STATE SNAPSHOT
# ============================================================================

@dataclass(frozen=True)
class StateSnapshot:
    """
    Output of decision_state.py.

    Explainer consumes this state.
    It does not calculate a new decision.
    """

    decision_id: str
    market_id: str

    action: DecisionAction
    state: DecisionState

    as_of: datetime

    invalidation_triggered: bool = False

    state_changed: bool = False

    reasons: Sequence[str] = field(default_factory=tuple)

    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:

        if self.as_of.tzinfo is None:
            raise ValueError(
                "StateSnapshot.as_of must be timezone-aware"
            )


# ============================================================================
# LIVE EVIDENCE
# ============================================================================

@dataclass(frozen=True)
class ExplanationEvidence:
    """
    Current evidence used to explain the existing D13 decision.
    """

    timestamp: datetime
    market_id: str

    source: str
    name: str

    polarity: EvidencePolarity

    value: Any = None

    observed: bool = True
    stale: bool = False
    future: bool = False

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:

        if self.timestamp.tzinfo is None:
            raise ValueError(
                "ExplanationEvidence.timestamp must be timezone-aware"
            )

        if not self.market_id:
            raise ValueError(
                "ExplanationEvidence.market_id is required"
            )

        if not self.name:
            raise ValueError(
                "ExplanationEvidence.name is required"
            )


# ============================================================================
# EXPLANATION RESULT
# ============================================================================

@dataclass(frozen=True)
class DecisionExplanation:
    """
    Human-readable + machine-readable explanation of D13's current journey.
    """

    decision_id: str
    market_id: str

    action: DecisionAction
    state: DecisionState
    management_action: ManagementAction

    status: ExplanationStatus

    as_of: datetime

    headline: str
    decision_summary: str
    journey_summary: str
    current_scenario: str

    why_summary: str
    support_summary: str
    contradiction_summary: str
    caution_summary: str

    thesis_status: str
    next_context: str

    reasons: Sequence[ExplanationReason] = field(default_factory=tuple)

    supporting_evidence: Sequence[str] = field(default_factory=tuple)
    contradicting_evidence: Sequence[str] = field(default_factory=tuple)
    caution_evidence: Sequence[str] = field(default_factory=tuple)

    provenance: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:

        return {
            "decision_id": self.decision_id,
            "market_id": self.market_id,

            "action": self.action.value,
            "state": self.state.value,
            "management_action": self.management_action.value,

            "status": self.status.value,
            "as_of": self.as_of.isoformat(),

            "headline": self.headline,
            "decision_summary": self.decision_summary,
            "journey_summary": self.journey_summary,
            "current_scenario": self.current_scenario,

            "why_summary": self.why_summary,
            "support_summary": self.support_summary,
            "contradiction_summary": self.contradiction_summary,
            "caution_summary": self.caution_summary,

            "thesis_status": self.thesis_status,
            "next_context": self.next_context,

            "reasons": [r.value for r in self.reasons],

            "supporting_evidence": list(self.supporting_evidence),
            "contradicting_evidence": list(
                self.contradicting_evidence
            ),
            "caution_evidence": list(self.caution_evidence),

            "provenance": dict(self.provenance),
        }


# ============================================================================
# EXPLAINER ENGINE
# ============================================================================

class DecisionExplainerEngine:
    """
    Explains an existing D13 decision.

    D13 remains authoritative.
    """

    VERSION = "DECISION-EXPLAINER-1.0"

    def explain(
        self,
        decision: D13DecisionSnapshot,
        *,
        current_state: StateSnapshot,
        evidence: Optional[Iterable[ExplanationEvidence]] = None,
        as_of: Optional[datetime] = None,
    ) -> DecisionExplanation:

        now = as_of or datetime.now(timezone.utc)

        if now.tzinfo is None:

            return self._blocked(
                decision,
                current_state,
                now,
                ExplanationReason.TIMESTAMP_ERROR,
            )

        now = now.astimezone(timezone.utc)

        # ------------------------------------------------------------------
        # D13 identity guard
        # ------------------------------------------------------------------

        if current_state.decision_id != decision.decision_id:
            return self._blocked(
                decision,
                current_state,
                now,
                ExplanationReason.IDENTITY_MISMATCH,
            )

        if current_state.market_id != decision.market_id:
            return self._blocked(
                decision,
                current_state,
                now,
                ExplanationReason.IDENTITY_MISMATCH,
            )

        # ------------------------------------------------------------------
        # Future outcome guard
        # ------------------------------------------------------------------

        decision_provenance = dict(decision.provenance)

        if decision_provenance.get("future_outcome_observed") is True:

            return self._blocked(
                decision,
                current_state,
                now,
                ExplanationReason.FUTURE_DATA,
            )

        # ------------------------------------------------------------------
        # Validate current state provenance
        # ------------------------------------------------------------------

        state_provenance = dict(current_state.provenance)

        if state_provenance.get("future_outcome_observed") is True:

            return self._blocked(
                decision,
                current_state,
                now,
                ExplanationReason.FUTURE_DATA,
            )

        # ------------------------------------------------------------------
        # Validate current evidence
        # ------------------------------------------------------------------

        clean: List[ExplanationEvidence] = []

        for item in evidence or []:

            if item.market_id != decision.market_id:

                return self._blocked(
                    decision,
                    current_state,
                    now,
                    ExplanationReason.IDENTITY_MISMATCH,
                )

            if item.future or item.timestamp > now:

                return self._blocked(
                    decision,
                    current_state,
                    now,
                    ExplanationReason.FUTURE_DATA,
                )

            clean.append(item)

        clean.sort(key=lambda x: x.timestamp)

        # ------------------------------------------------------------------
        # Classify evidence
        # ------------------------------------------------------------------

        supporting = [
            e.name
            for e in clean
            if e.polarity == EvidencePolarity.SUPPORT
        ]

        contradicting = [
            e.name
            for e in clean
            if e.polarity == EvidencePolarity.CONTRADICTION
        ]

        caution = [
            e.name
            for e in clean
            if e.polarity == EvidencePolarity.CAUTION
        ]

        # ------------------------------------------------------------------
        # Current scenario
        # ------------------------------------------------------------------

        current_scenario = (
            decision.scenario
            if decision.scenario
            else "CURRENT SCENARIO NOT EXPLICITLY PROVIDED BY D13"
        )

        # ------------------------------------------------------------------
        # Determine management interpretation.
        #
        # This does NOT change D13 action.
        # ------------------------------------------------------------------

        management_action = self._management_action(
            decision=decision,
            current_state=current_state,
            supporting=supporting,
            contradicting=contradicting,
            caution=caution,
        )

        # ------------------------------------------------------------------
        # Thesis status
        # ------------------------------------------------------------------

        thesis_status = self._thesis_status(
            current_state=current_state,
            supporting=supporting,
            contradicting=contradicting,
            caution=caution,
        )

        # ------------------------------------------------------------------
        # Journey explanation
        # ------------------------------------------------------------------

        journey_summary = self._journey_summary(
            decision,
            current_state,
            management_action,
        )

        why_summary = self._why_summary(
            decision,
            supporting,
            contradicting,
            caution,
        )

        support_summary = self._evidence_summary(
            "Supporting evidence",
            supporting,
        )

        contradiction_summary = self._evidence_summary(
            "Contradicting evidence",
            contradicting,
        )

        caution_summary = self._evidence_summary(
            "Caution evidence",
            caution,
        )

        next_context = self._next_context(
            decision=decision,
            state=current_state.state,
            management_action=management_action,
        )

        headline = (
            f"{decision.action.value} — "
            f"{current_state.state.value} — "
            f"{management_action.value}"
        )

        status = ExplanationStatus.READY

        if not clean:
            status = ExplanationStatus.LIMITED

        if clean and all(e.stale for e in clean):
            status = ExplanationStatus.LIMITED

        reasons: List[ExplanationReason] = [
            ExplanationReason.D13_DECISION,
            ExplanationReason.CURRENT_STATE,
        ]

        if supporting:
            reasons.append(
                ExplanationReason.SUPPORTING_EVIDENCE
            )

        if contradicting:
            reasons.append(
                ExplanationReason.CONTRADICTING_EVIDENCE
            )

        if caution:
            reasons.append(
                ExplanationReason.CAUTION_EVIDENCE
            )

        if current_state.state == DecisionState.STRENGTHENING:
            reasons.append(
                ExplanationReason.THESIS_STRENGTHENING
            )
        elif current_state.state == DecisionState.WEAKENING:
            reasons.append(
                ExplanationReason.THESIS_WEAKENING
            )
        elif current_state.state == DecisionState.ACTIVE:
            reasons.append(
                ExplanationReason.THESIS_INTACT
            )

        if current_state.invalidation_triggered:
            reasons.extend(
                [
                    ExplanationReason.INVALIDATION_TRIGGERED,
                    ExplanationReason.EXIT_REQUIRED,
                ]
            )

        if not clean:
            reasons.append(
                ExplanationReason.MISSING_LIVE_EVIDENCE
            )

        reasons.append(
            ExplanationReason.EXPLANATION_GENERATED
        )

        return DecisionExplanation(
            decision_id=decision.decision_id,
            market_id=decision.market_id,

            action=decision.action,
            state=current_state.state,
            management_action=management_action,

            status=status,

            as_of=now,

            headline=headline,

            decision_summary=(
                f"D13 final decision: {decision.action.value}."
            ),

            journey_summary=journey_summary,

            current_scenario=current_scenario,

            why_summary=why_summary,

            support_summary=support_summary,

            contradiction_summary=contradiction_summary,

            caution_summary=caution_summary,

            thesis_status=thesis_status,

            next_context=next_context,

            reasons=tuple(reasons),

            supporting_evidence=tuple(supporting),

            contradicting_evidence=tuple(
                contradicting
            ),

            caution_evidence=tuple(caution),

            provenance={
                **decision_provenance,

                "engine": "DecisionExplainerEngine",
                "engine_version": self.VERSION,

                "decision_authority": "D13",

                "new_decision_created": False,
                "d13_decision_modified": False,

                "future_outcome_observed": False,

                "explanation_is_current": True,

                "management_action_is_not_new_decision": True,
            },
        )

    # ========================================================================
    # MANAGEMENT
    # ========================================================================

    @staticmethod
    def _management_action(
        *,
        decision: D13DecisionSnapshot,
        current_state: StateSnapshot,
        supporting: Sequence[str],
        contradicting: Sequence[str],
        caution: Sequence[str],
    ) -> ManagementAction:

        if decision.action == DecisionAction.BLOCKED:
            return ManagementAction.BLOCKED

        if decision.action in (
            DecisionAction.WAIT,
            DecisionAction.NO_ACTION,
        ):
            return ManagementAction.WAIT

        if current_state.state in (
            DecisionState.EXIT,
            DecisionState.INVALIDATED,
            DecisionState.CLOSED,
            DecisionState.EXPIRED,
        ):
            return ManagementAction.EXIT

        if current_state.invalidation_triggered:
            return ManagementAction.EXIT

        if current_state.state == DecisionState.WEAKENING:
            return ManagementAction.CAUTION

        if contradicting and not supporting:
            return ManagementAction.CAUTION

        if caution and not supporting:
            return ManagementAction.CAUTION

        if supporting:
            return ManagementAction.FOLLOW

        return ManagementAction.CAUTION

    # ========================================================================
    # THESIS
    # ========================================================================

    @staticmethod
    def _thesis_status(
        *,
        current_state: StateSnapshot,
        supporting: Sequence[str],
        contradicting: Sequence[str],
        caution: Sequence[str],
    ) -> str:

        if current_state.state in (
            DecisionState.EXIT,
            DecisionState.INVALIDATED,
        ):
            return "INVALIDATED"

        if current_state.state == DecisionState.WEAKENING:
            return "WEAKENING"

        if current_state.state == DecisionState.STRENGTHENING:
            return "STRENGTHENING"

        if supporting and not contradicting:
            return "INTACT"

        if supporting and caution:
            return "INTACT_WITH_CAUTION"

        if caution:
            return "CAUTION"

        if contradicting:
            return "WEAKENING"

        return "UNDETERMINED"

    # ========================================================================
    # WHY
    # ========================================================================

    @staticmethod
    def _why_summary(
        decision: D13DecisionSnapshot,
        supporting: Sequence[str],
        contradicting: Sequence[str],
        caution: Sequence[str],
    ) -> str:

        parts: List[str] = []

        if decision.thesis:
            parts.append(
                f"D13 thesis: {decision.thesis}"
            )

        if supporting:
            parts.append(
                "Current support: "
                + ", ".join(supporting)
            )

        if contradicting:
            parts.append(
                "Current contradiction: "
                + ", ".join(contradicting)
            )

        if caution:
            parts.append(
                "Current caution: "
                + ", ".join(caution)
            )

        if not parts:
            return (
                "D13 decision exists, but insufficient current "
                "evidence is available for a detailed explanation."
            )

        return " | ".join(parts)

    # ========================================================================
    # EVIDENCE SUMMARY
    # ========================================================================

    @staticmethod
    def _evidence_summary(
        label: str,
        values: Sequence[str],
    ) -> str:

        if not values:
            return f"{label}: NONE IDENTIFIED"

        return f"{label}: " + ", ".join(values)

    # ========================================================================
    # JOURNEY
    # ========================================================================

    @staticmethod
    def _journey_summary(
        decision: D13DecisionSnapshot,
        state: StateSnapshot,
        management: ManagementAction,
    ) -> str:

        return (
            f"D13 issued {decision.action.value}; "
            f"current lifecycle state is {state.state.value}; "
            f"current management interpretation is "
            f"{management.value}."
        )

    # ========================================================================
    # NEXT CONTEXT
    # ========================================================================

    @staticmethod
    def _next_context(
        *,
        decision: D13DecisionSnapshot,
        state: DecisionState,
        management_action: ManagementAction,
    ) -> str:

        if management_action == ManagementAction.EXIT:
            return (
                "Existing D13 decision has reached an exit condition. "
                "Do not continue following this decision."
            )

        if management_action == ManagementAction.CAUTION:
            return (
                "Continue monitoring the existing D13 thesis. "
                "Contradiction or weakening evidence requires "
                "reassessment against the explicit D13 invalidation "
                "condition."
            )

        if management_action == ManagementAction.FOLLOW:
            return (
                "Continue following the existing D13 decision while "
                "its thesis remains intact. Reassess when new "
                "validated current evidence arrives."
            )

        if management_action == ManagementAction.WAIT:
            return (
                "D13 has not authorized an active directional trade. "
                "Wait for the decision lifecycle to change."
            )

        if management_action == ManagementAction.BLOCKED:
            return (
                "Required decision context is blocked. "
                "Do not treat this explanation as execution authority."
            )

        return (
            f"Current lifecycle state: {state.value}. "
            "Further validated evidence is required."
        )

    # ========================================================================
    # BLOCKED
    # ========================================================================

    def _blocked(
        self,
        decision: D13DecisionSnapshot,
        state: StateSnapshot,
        now: datetime,
        reason: ExplanationReason,
    ) -> DecisionExplanation:

        return DecisionExplanation(
            decision_id=decision.decision_id,
            market_id=decision.market_id,

            action=decision.action,
            state=DecisionState.BLOCKED,
            management_action=ManagementAction.BLOCKED,

            status=ExplanationStatus.BLOCKED,

            as_of=now,

            headline=(
                f"{decision.action.value} — BLOCKED"
            ),

            decision_summary=(
                f"D13 final decision: {decision.action.value}."
            ),

            journey_summary=(
                "Current decision journey cannot be safely explained "
                "because required provenance/identity/time conditions "
                "failed."
            ),

            current_scenario=(
                decision.scenario or "UNKNOWN"
            ),

            why_summary=(
                "Explanation blocked."
            ),

            support_summary="Supporting evidence unavailable.",

            contradiction_summary=(
                "Contradicting evidence unavailable."
            ),

            caution_summary="Caution evidence unavailable.",

            thesis_status="BLOCKED",

            next_context=(
                "Resolve the blocking condition before using "
                "the explanation operationally."
            ),

            reasons=(reason,),

            provenance={
                **dict(decision.provenance),
                "engine": "DecisionExplainerEngine",
                "engine_version": self.VERSION,
                "decision_authority": "D13",
                "new_decision_created": False,
                "d13_decision_modified": False,
                "future_outcome_observed": False,
            },
        )


# ============================================================================
# SELF TESTS
# ============================================================================

def _base_decision() -> D13DecisionSnapshot:

    now = datetime.now(timezone.utc)

    return D13DecisionSnapshot(
        decision_id="D13-NIFTY-EXPLAIN-001",
        market_id="NSE:NIFTY:INDEX",
        action=DecisionAction.BUY,
        decision_timestamp=now,
        scenario="BULLISH_CONTINUATION",
        horizon="5M",
        thesis=(
            "Structure and flow support bullish continuation."
        ),
        invalidation_condition=(
            "Explicit D13 invalidation condition."
        ),
        provenance={
            "future_outcome_observed": False,
            "validated_by_D14": False,
        },
    )


def _base_state(
    decision: D13DecisionSnapshot,
    state: DecisionState = DecisionState.ACTIVE,
    invalidation: bool = False,
) -> StateSnapshot:

    return StateSnapshot(
        decision_id=decision.decision_id,
        market_id=decision.market_id,
        action=decision.action,
        state=state,
        as_of=decision.decision_timestamp,
        invalidation_triggered=invalidation,
        provenance={
            "future_outcome_observed": False,
            "decision_authority": "D13",
        },
    )


def _test_buy_active_follow() -> None:

    decision = _base_decision()
    state = _base_state(decision)

    evidence = [
        ExplanationEvidence(
            timestamp=decision.decision_timestamp,
            market_id=decision.market_id,
            source="MATRIX",
            name="STRUCTURE",
            polarity=EvidencePolarity.SUPPORT,
        ),
        ExplanationEvidence(
            timestamp=decision.decision_timestamp,
            market_id=decision.market_id,
            source="MATRIX",
            name="FLOW",
            polarity=EvidencePolarity.SUPPORT,
        ),
    ]

    result = DecisionExplainerEngine().explain(
        decision,
        current_state=state,
        evidence=evidence,
        as_of=decision.decision_timestamp,
    )

    assert result.action == DecisionAction.BUY
    assert result.state == DecisionState.ACTIVE
    assert result.management_action == ManagementAction.FOLLOW
    assert result.status == ExplanationStatus.READY
    assert "STRUCTURE" in result.supporting_evidence
    assert result.provenance["decision_authority"] == "D13"


def _test_weakening_caution() -> None:

    decision = _base_decision()

    state = _base_state(
        decision,
        state=DecisionState.WEAKENING,
    )

    evidence = [
        ExplanationEvidence(
            timestamp=decision.decision_timestamp,
            market_id=decision.market_id,
            source="FLOW",
            name="FLOW_CONFLICT",
            polarity=EvidencePolarity.CONTRADICTION,
        )
    ]

    result = DecisionExplainerEngine().explain(
        decision,
        current_state=state,
        evidence=evidence,
        as_of=decision.decision_timestamp,
    )

    assert result.action == DecisionAction.BUY
    assert result.state == DecisionState.WEAKENING
    assert result.management_action == ManagementAction.CAUTION
    assert result.thesis_status == "WEAKENING"


def _test_invalidation_exit() -> None:

    decision = _base_decision()

    state = _base_state(
        decision,
        state=DecisionState.EXIT,
        invalidation=True,
    )

    result = DecisionExplainerEngine().explain(
        decision,
        current_state=state,
        evidence=[],
        as_of=decision.decision_timestamp,
    )

    assert result.action == DecisionAction.BUY
    assert result.state == DecisionState.EXIT
    assert result.management_action == ManagementAction.EXIT
    assert result.provenance["new_decision_created"] is False


def _test_d13_sell_is_preserved() -> None:

    now = datetime.now(timezone.utc)

    decision = D13DecisionSnapshot(
        decision_id="D13-GOLD-SELL-001",
        market_id="COMEX:GOLD:FUTURE",
        action=DecisionAction.SELL,
        decision_timestamp=now,
        scenario="BEARISH_CONTINUATION",
        horizon="15M",
        thesis="Bearish continuation thesis.",
        provenance={
            "future_outcome_observed": False,
        },
    )

    state = _base_state(
        decision,
        state=DecisionState.ACTIVE,
    )

    evidence = [
        ExplanationEvidence(
            timestamp=now,
            market_id=decision.market_id,
            source="MATRIX",
            name="STRUCTURE",
            polarity=EvidencePolarity.SUPPORT,
        )
    ]

    result = DecisionExplainerEngine().explain(
        decision,
        current_state=state,
        evidence=evidence,
        as_of=now,
    )

    assert result.action == DecisionAction.SELL
    assert result.management_action == ManagementAction.FOLLOW


def _test_missing_evidence_is_limited() -> None:

    decision = _base_decision()

    state = _base_state(decision)

    result = DecisionExplainerEngine().explain(
        decision,
        current_state=state,
        evidence=[],
        as_of=decision.decision_timestamp,
    )

    assert result.status == ExplanationStatus.LIMITED
    assert result.management_action == ManagementAction.CAUTION
    assert ExplanationReason.MISSING_LIVE_EVIDENCE in result.reasons


def _test_identity_attack() -> None:

    decision = _base_decision()

    wrong_state = StateSnapshot(
        decision_id=decision.decision_id,
        market_id="COMEX:GOLD:FUTURE",
        action=decision.action,
        state=DecisionState.ACTIVE,
        as_of=decision.decision_timestamp,
        provenance={
            "future_outcome_observed": False,
        },
    )

    result = DecisionExplainerEngine().explain(
        decision,
        current_state=wrong_state,
        as_of=decision.decision_timestamp,
    )

    assert result.status == ExplanationStatus.BLOCKED
    assert result.management_action == ManagementAction.BLOCKED
    assert (
        ExplanationReason.IDENTITY_MISMATCH
        in result.reasons
    )


def _test_future_attack() -> None:

    decision = _base_decision()
    state = _base_state(decision)

    evidence = [
        ExplanationEvidence(
            timestamp=decision.decision_timestamp,
            market_id=decision.market_id,
            source="D14",
            name="FUTURE_OUTCOME",
            polarity=EvidencePolarity.SUPPORT,
            future=True,
        )
    ]

    result = DecisionExplainerEngine().explain(
        decision,
        current_state=state,
        evidence=evidence,
        as_of=decision.decision_timestamp,
    )

    assert result.status == ExplanationStatus.BLOCKED
    assert result.management_action == ManagementAction.BLOCKED
    assert ExplanationReason.FUTURE_DATA in result.reasons


def _test_d13_immutability() -> None:

    decision = _base_decision()

    original_action = decision.action
    original_scenario = decision.scenario
    original_thesis = decision.thesis

    state = _base_state(
        decision,
        state=DecisionState.STRENGTHENING,
    )

    evidence = [
        ExplanationEvidence(
            timestamp=decision.decision_timestamp,
            market_id=decision.market_id,
            source="FLOW",
            name="FLOW",
            polarity=EvidencePolarity.SUPPORT,
        )
    ]

    DecisionExplainerEngine().explain(
        decision,
        current_state=state,
        evidence=evidence,
        as_of=decision.decision_timestamp,
    )

    assert decision.action == original_action
    assert decision.scenario == original_scenario
    assert decision.thesis == original_thesis


def _test_hold_wait() -> None:

    now = datetime.now(timezone.utc)

    decision = D13DecisionSnapshot(
        decision_id="D13-NIFTY-HOLD-001",
        market_id="NSE:NIFTY:INDEX",
        action=DecisionAction.HOLD,
        decision_timestamp=now,
        scenario="RANGE",
        horizon="5M",
        provenance={
            "future_outcome_observed": False,
        },
    )

    state = _base_state(
        decision,
        state=DecisionState.READY,
    )

    result = DecisionExplainerEngine().explain(
        decision,
        current_state=state,
        evidence=[],
        as_of=now,
    )

    assert result.action == DecisionAction.HOLD
    assert result.management_action == ManagementAction.CAUTION


def run_self_test() -> None:

    _test_buy_active_follow()
    _test_weakening_caution()
    _test_invalidation_exit()
    _test_d13_sell_is_preserved()
    _test_missing_evidence_is_limited()
    _test_identity_attack()
    _test_future_attack()
    _test_d13_immutability()
    _test_hold_wait()

    print("DECISION EXPLAINER SELF-TEST: PASS")


if __name__ == "__main__":
    run_self_test()