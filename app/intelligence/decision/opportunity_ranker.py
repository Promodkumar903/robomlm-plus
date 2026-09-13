"""
ROBOMLM_PLUS
Opportunity Ranker
------------------

ROLE
----
Rank EXISTING D13 decisions/opportunities by current priority.

D13 remains the ONLY decision authority.

This module MUST NOT:
    - create BUY / SELL / HOLD
    - change a D13 action
    - vote against another decision engine
    - average independent decision scores
    - manufacture a directional signal
    - use future outcome information

It answers:

    "Among the currently available D13 opportunities,
     which one deserves higher priority/attention?"

Example:

    NIFTY  -> D13 BUY
    GOLD   -> D13 BUY
    EURUSD -> D13 SELL
    BTC    -> D13 BUY

The Ranker can establish:

    Rank 1 -> NIFTY
    Rank 2 -> GOLD
    Rank 3 -> EURUSD
    Rank 4 -> BTC

The Ranker does NOT decide that GOLD should be BUY.
That BUY must already come from GOLD's D13 decision.

IMPORTANT
---------
This implementation deliberately does not invent a proprietary V6
0-100 formula. Ranking is based on explicit comparable dimensions
supplied by the upstream decision/context layer.

The ranking dimensions are:

    decision eligibility
    current lifecycle state
    thesis condition
    supporting evidence
    contradiction
    caution
    timing alignment
    opportunity readiness
    priority

The final ordering is deterministic and traceable.

Future outcome data is prohibited.
Market identity is isolated.
D13 decision snapshots remain immutable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


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


class RankBand(str, Enum):
    PRIORITY_1 = "PRIORITY_1"
    PRIORITY_2 = "PRIORITY_2"
    PRIORITY_3 = "PRIORITY_3"
    PRIORITY_4 = "PRIORITY_4"
    PRIORITY_5_PLUS = "PRIORITY_5_PLUS"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"


class RankStatus(str, Enum):
    RANKED = "RANKED"
    LIMITED = "LIMITED"
    BLOCKED = "BLOCKED"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"


class RankReason(str, Enum):
    D13_DECISION = "D13_DECISION"
    ACTIVE_OPPORTUNITY = "ACTIVE_OPPORTUNITY"
    STRENGTHENING_THESIS = "STRENGTHENING_THESIS"
    STABLE_THESIS = "STABLE_THESIS"
    WEAKENING_THESIS = "WEAKENING_THESIS"

    SUPPORTING_EVIDENCE = "SUPPORTING_EVIDENCE"
    CONTRADICTING_EVIDENCE = "CONTRADICTING_EVIDENCE"
    CAUTION_EVIDENCE = "CAUTION_EVIDENCE"

    FOLLOWABLE = "FOLLOWABLE"
    CAUTION_REQUIRED = "CAUTION_REQUIRED"

    EXITED = "EXITED"
    CLOSED = "CLOSED"
    BLOCKED = "BLOCKED"
    NO_DIRECTIONAL_DECISION = "NO_DIRECTIONAL_DECISION"

    FUTURE_DATA = "FUTURE_DATA"
    IDENTITY_ERROR = "IDENTITY_ERROR"
    TIMESTAMP_ERROR = "TIMESTAMP_ERROR"

    RANKING_COMPLETE = "RANKING_COMPLETE"


# ============================================================================
# D13 DECISION SNAPSHOT
# ============================================================================

@dataclass(frozen=True)
class D13DecisionSnapshot:
    """
    Immutable D13 decision.

    D13 is the source of directional authority.
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
# CURRENT DECISION STATE
# ============================================================================

@dataclass(frozen=True)
class RankStateSnapshot:
    """
    Current lifecycle state produced by decision_state.py.
    """

    decision_id: str
    market_id: str

    state: DecisionState
    management_action: ManagementAction

    as_of: datetime

    invalidation_triggered: bool = False

    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:

        if self.as_of.tzinfo is None:
            raise ValueError(
                "RankStateSnapshot.as_of must be timezone-aware"
            )


# ============================================================================
# CURRENT EVIDENCE CONTEXT
# ============================================================================

@dataclass(frozen=True)
class RankEvidence:
    """
    Current evidence context for one D13 opportunity.

    This is NOT a new decision signal.
    """

    name: str

    polarity: str

    source: str

    timestamp: datetime

    stale: bool = False
    future: bool = False

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:

        if self.timestamp.tzinfo is None:
            raise ValueError(
                "RankEvidence.timestamp must be timezone-aware"
            )


# ============================================================================
# TIMING CONTEXT
# ============================================================================

@dataclass(frozen=True)
class RankTimingContext:
    """
    Timing information supplied by timing_engine.py.

    Timing affects opportunity priority but does not create direction.
    """

    primary_window: Optional[str]

    window_active: bool

    reassessment_due: bool = False

    elapsed_seconds: Optional[float] = None

    remaining_seconds: Optional[float] = None

    timing_status: str = "UNKNOWN"

    provenance: Mapping[str, Any] = field(default_factory=dict)


# ============================================================================
# OPPORTUNITY
# ============================================================================

@dataclass(frozen=True)
class OpportunityCandidate:
    """
    One complete candidate for ranking.

    Every candidate must already have a D13 decision.
    """

    decision: D13DecisionSnapshot

    state: RankStateSnapshot

    evidence: Sequence[RankEvidence] = field(default_factory=tuple)

    timing: Optional[RankTimingContext] = None


# ============================================================================
# RANKED RESULT
# ============================================================================

@dataclass(frozen=True)
class RankedOpportunity:
    """
    Final ranking output for one D13 opportunity.
    """

    decision_id: str
    market_id: str

    action: DecisionAction
    state: DecisionState
    management_action: ManagementAction

    rank: Optional[int]

    rank_band: RankBand
    status: RankStatus

    priority_key: Tuple[int, ...]

    reasons: Sequence[RankReason] = field(default_factory=tuple)

    supporting_evidence: Sequence[str] = field(
        default_factory=tuple
    )

    contradicting_evidence: Sequence[str] = field(
        default_factory=tuple
    )

    caution_evidence: Sequence[str] = field(
        default_factory=tuple
    )

    timing_active: Optional[bool] = None

    provenance: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:

        return {
            "decision_id": self.decision_id,
            "market_id": self.market_id,

            "action": self.action.value,
            "state": self.state.value,
            "management_action": self.management_action.value,

            "rank": self.rank,
            "rank_band": self.rank_band.value,
            "status": self.status.value,

            "priority_key": list(self.priority_key),

            "reasons": [
                reason.value
                for reason in self.reasons
            ],

            "supporting_evidence": list(
                self.supporting_evidence
            ),

            "contradicting_evidence": list(
                self.contradicting_evidence
            ),

            "caution_evidence": list(
                self.caution_evidence
            ),

            "timing_active": self.timing_active,

            "provenance": dict(self.provenance),
        }


# ============================================================================
# RANKING RESULT
# ============================================================================

@dataclass(frozen=True)
class OpportunityRanking:
    """
    Complete ordered ranking across all eligible D13 opportunities.
    """

    as_of: datetime

    ranked: Sequence[RankedOpportunity]

    eligible_count: int
    excluded_count: int

    provenance: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:

        return {
            "as_of": self.as_of.isoformat(),

            "eligible_count": self.eligible_count,
            "excluded_count": self.excluded_count,

            "ranked": [
                item.to_dict()
                for item in self.ranked
            ],

            "provenance": dict(self.provenance),
        }


# ============================================================================
# ENGINE
# ============================================================================

class OpportunityRankerEngine:
    """
    Ranks existing D13 opportunities.

    It does not make a new decision.
    """

    VERSION = "OPPORTUNITY-RANKER-1.0"

    # ------------------------------------------------------------------------
    # Rank priority hierarchy
    #
    # IMPORTANT:
    # These are ordering dimensions, NOT a proprietary 0-100 score.
    # ------------------------------------------------------------------------

    _STATE_PRIORITY = {
        DecisionState.STRENGTHENING: 6,
        DecisionState.ACTIVE: 5,
        DecisionState.READY: 4,
        DecisionState.SETUP: 3,
        DecisionState.WEAKENING: 2,
        DecisionState.EXPIRED: 1,
        DecisionState.EXIT: 0,
        DecisionState.INVALIDATED: 0,
        DecisionState.CLOSED: 0,
        DecisionState.BLOCKED: 0,
    }

    _MANAGEMENT_PRIORITY = {
        ManagementAction.FOLLOW: 3,
        ManagementAction.CAUTION: 2,
        ManagementAction.WAIT: 1,
        ManagementAction.NO_ACTION: 1,
        ManagementAction.EXIT: 0,
        ManagementAction.BLOCKED: 0,
    }

    def rank(
        self,
        candidates: Iterable[OpportunityCandidate],
        *,
        as_of: Optional[datetime] = None,
    ) -> OpportunityRanking:

        now = as_of or datetime.now(timezone.utc)

        if now.tzinfo is None:
            raise ValueError(
                "as_of must be timezone-aware"
            )

        now = now.astimezone(timezone.utc)

        prepared: List[
            Tuple[OpportunityCandidate, Tuple[int, ...]]
        ] = []

        excluded: List[RankedOpportunity] = []

        seen_decisions = set()

        for candidate in candidates:

            decision = candidate.decision
            state = candidate.state

            # --------------------------------------------------------------
            # Duplicate protection
            # --------------------------------------------------------------

            if decision.decision_id in seen_decisions:
                excluded.append(
                    self._excluded(
                        candidate,
                        now,
                        RankReason.IDENTITY_ERROR,
                    )
                )
                continue

            seen_decisions.add(
                decision.decision_id
            )

            # --------------------------------------------------------------
            # Identity protection
            # --------------------------------------------------------------

            if state.decision_id != decision.decision_id:
                excluded.append(
                    self._excluded(
                        candidate,
                        now,
                        RankReason.IDENTITY_ERROR,
                    )
                )
                continue

            if state.market_id != decision.market_id:
                excluded.append(
                    self._excluded(
                        candidate,
                        now,
                        RankReason.IDENTITY_ERROR,
                    )
                )
                continue

            # --------------------------------------------------------------
            # D13 future provenance guard
            # --------------------------------------------------------------

            if decision.provenance.get(
                "future_outcome_observed"
            ) is True:

                excluded.append(
                    self._excluded(
                        candidate,
                        now,
                        RankReason.FUTURE_DATA,
                    )
                )
                continue

            # --------------------------------------------------------------
            # Timestamp guard
            # --------------------------------------------------------------

            if decision.decision_timestamp > now:
                excluded.append(
                    self._excluded(
                        candidate,
                        now,
                        RankReason.TIMESTAMP_ERROR,
                    )
                )
                continue

            if state.as_of > now:
                excluded.append(
                    self._excluded(
                        candidate,
                        now,
                        RankReason.TIMESTAMP_ERROR,
                    )
                )
                continue

            # --------------------------------------------------------------
            # Directional eligibility
            # --------------------------------------------------------------

            if decision.action not in (
                DecisionAction.BUY,
                DecisionAction.SELL,
            ):
                excluded.append(
                    self._excluded(
                        candidate,
                        now,
                        RankReason.NO_DIRECTIONAL_DECISION,
                    )
                )
                continue

            # --------------------------------------------------------------
            # State eligibility
            # --------------------------------------------------------------

            if state.state in (
                DecisionState.BLOCKED,
                DecisionState.CLOSED,
                DecisionState.INVALIDATED,
                DecisionState.EXIT,
                DecisionState.EXPIRED,
            ):
                excluded.append(
                    self._excluded(
                        candidate,
                        now,
                        self._terminal_reason(state.state),
                    )
                )
                continue

            # --------------------------------------------------------------
            # Evidence future guard
            # --------------------------------------------------------------

            evidence_invalid = False

            for evidence in candidate.evidence:

                if evidence.future:
                    evidence_invalid = True
                    break

                if evidence.timestamp > now:
                    evidence_invalid = True
                    break

            if evidence_invalid:
                excluded.append(
                    self._excluded(
                        candidate,
                        now,
                        RankReason.FUTURE_DATA,
                    )
                )
                continue

            # --------------------------------------------------------------
            # Build deterministic priority key.
            # --------------------------------------------------------------

            priority_key = self._priority_key(
                candidate
            )

            prepared.append(
                (
                    candidate,
                    priority_key,
                )
            )

        # ------------------------------------------------------------------
        # Deterministic ordering.
        #
        # Higher tuple values are preferred.
        # decision_id is final deterministic tie breaker.
        # ------------------------------------------------------------------

        prepared.sort(
            key=lambda item: (
                item[1],
                item[0].decision.decision_id,
            ),
            reverse=True,
        )

        ranked_results: List[RankedOpportunity] = []

        for index, (candidate, priority_key) in enumerate(
            prepared,
            start=1,
        ):

            ranked_results.append(
                self._ranked(
                    candidate=candidate,
                    rank=index,
                    priority_key=priority_key,
                    now=now,
                )
            )

        # ------------------------------------------------------------------
        # Include exclusions after ranked opportunities.
        #
        # They retain rank=None.
        # ------------------------------------------------------------------

        all_results = ranked_results + excluded

        return OpportunityRanking(
            as_of=now,

            ranked=tuple(all_results),

            eligible_count=len(ranked_results),

            excluded_count=len(excluded),

            provenance={
                "engine": "OpportunityRankerEngine",
                "engine_version": self.VERSION,

                "decision_authority": "D13",

                "new_decision_created": False,
                "d13_decision_modified": False,

                "future_outcome_observed": False,

                "ranking_is_relative": True,

                "proprietary_0_100_score_used": False,
            },
        )

    # ========================================================================
    # PRIORITY KEY
    # ========================================================================

    def _priority_key(
        self,
        candidate: OpportunityCandidate,
    ) -> Tuple[int, ...]:

        decision = candidate.decision
        state = candidate.state

        support = 0
        contradiction = 0
        caution = 0

        for evidence in candidate.evidence:

            if evidence.stale:
                continue

            polarity = evidence.polarity.upper()

            if polarity == "SUPPORT":
                support += 1

            elif polarity == "CONTRADICTION":
                contradiction += 1

            elif polarity == "CAUTION":
                caution += 1

        # --------------------------------------------------------------
        # Evidence balance is represented structurally.
        #
        # It is NOT converted to a fake percentage.
        # --------------------------------------------------------------

        evidence_balance = support - contradiction

        timing_priority = 0

        if candidate.timing is not None:

            if candidate.timing.window_active:
                timing_priority += 2

            if candidate.timing.reassessment_due:
                timing_priority -= 1

        state_priority = self._STATE_PRIORITY.get(
            state.state,
            0,
        )

        management_priority = self._MANAGEMENT_PRIORITY.get(
            state.management_action,
            0,
        )

        # More support is useful.
        # More contradiction reduces priority.
        # Caution is retained separately in the key.
        #
        # No normalization / arbitrary score is used.

        return (
            state_priority,
            management_priority,
            evidence_balance,
            support,
            -contradiction,
            timing_priority,
            -caution,
        )

    # ========================================================================
    # RANKED OBJECT
    # ========================================================================

    def _ranked(
        self,
        *,
        candidate: OpportunityCandidate,
        rank: int,
        priority_key: Tuple[int, ...],
        now: datetime,
    ) -> RankedOpportunity:

        decision = candidate.decision
        state = candidate.state

        supporting = tuple(
            e.name
            for e in candidate.evidence
            if e.polarity.upper() == "SUPPORT"
            and not e.stale
        )

        contradicting = tuple(
            e.name
            for e in candidate.evidence
            if e.polarity.upper() == "CONTRADICTION"
            and not e.stale
        )

        caution = tuple(
            e.name
            for e in candidate.evidence
            if e.polarity.upper() == "CAUTION"
            and not e.stale
        )

        reasons: List[RankReason] = [
            RankReason.D13_DECISION,
        ]

        if state.state == DecisionState.STRENGTHENING:
            reasons.append(
                RankReason.STRENGTHENING_THESIS
            )

        elif state.state == DecisionState.ACTIVE:
            reasons.append(
                RankReason.ACTIVE_OPPORTUNITY
            )

        elif state.state == DecisionState.READY:
            reasons.append(
                RankReason.STABLE_THESIS
            )

        elif state.state == DecisionState.WEAKENING:
            reasons.append(
                RankReason.WEAKENING_THESIS
            )

        if supporting:
            reasons.append(
                RankReason.SUPPORTING_EVIDENCE
            )

        if contradicting:
            reasons.append(
                RankReason.CONTRADICTING_EVIDENCE
            )

        if caution:
            reasons.append(
                RankReason.CAUTION_EVIDENCE
            )

        if state.management_action == ManagementAction.FOLLOW:
            reasons.append(
                RankReason.FOLLOWABLE
            )

        elif state.management_action == ManagementAction.CAUTION:
            reasons.append(
                RankReason.CAUTION_REQUIRED
            )

        reasons.append(
            RankReason.RANKING_COMPLETE
        )

        return RankedOpportunity(
            decision_id=decision.decision_id,
            market_id=decision.market_id,

            action=decision.action,
            state=state.state,
            management_action=state.management_action,

            rank=rank,

            rank_band=self._rank_band(rank),

            status=RankStatus.RANKED,

            priority_key=priority_key,

            reasons=tuple(reasons),

            supporting_evidence=supporting,

            contradicting_evidence=contradicting,

            caution_evidence=caution,

            timing_active=(
                candidate.timing.window_active
                if candidate.timing is not None
                else None
            ),

            provenance={
                **dict(decision.provenance),

                "engine": "OpportunityRankerEngine",
                "engine_version": self.VERSION,

                "decision_authority": "D13",

                "new_decision_created": False,
                "d13_decision_modified": False,

                "future_outcome_observed": False,

                "ranking_is_relative": True,

                "rank_generated_at": now.isoformat(),
            },
        )

    # ========================================================================
    # EXCLUDED
    # ========================================================================

    def _excluded(
        self,
        candidate: OpportunityCandidate,
        now: datetime,
        reason: RankReason,
    ) -> RankedOpportunity:

        decision = candidate.decision
        state = candidate.state

        return RankedOpportunity(
            decision_id=decision.decision_id,
            market_id=decision.market_id,

            action=decision.action,
            state=state.state,
            management_action=state.management_action,

            rank=None,

            rank_band=RankBand.NOT_ELIGIBLE,

            status=(
                RankStatus.BLOCKED
                if reason in (
                    RankReason.FUTURE_DATA,
                    RankReason.IDENTITY_ERROR,
                    RankReason.TIMESTAMP_ERROR,
                )
                else RankStatus.NOT_ELIGIBLE
            ),

            priority_key=tuple(),

            reasons=(reason,),

            supporting_evidence=tuple(),
            contradicting_evidence=tuple(),
            caution_evidence=tuple(),

            timing_active=(
                candidate.timing.window_active
                if candidate.timing is not None
                else None
            ),

            provenance={
                **dict(decision.provenance),

                "engine": "OpportunityRankerEngine",
                "engine_version": self.VERSION,

                "decision_authority": "D13",

                "new_decision_created": False,
                "d13_decision_modified": False,

                "future_outcome_observed": False,

                "eligible_for_rank": False,
            },
        )

    # ========================================================================
    # HELPERS
    # ========================================================================

    @staticmethod
    def _rank_band(rank: int) -> RankBand:

        if rank == 1:
            return RankBand.PRIORITY_1

        if rank == 2:
            return RankBand.PRIORITY_2

        if rank == 3:
            return RankBand.PRIORITY_3

        if rank == 4:
            return RankBand.PRIORITY_4

        return RankBand.PRIORITY_5_PLUS

    @staticmethod
    def _terminal_reason(
        state: DecisionState,
    ) -> RankReason:

        if state == DecisionState.EXIT:
            return RankReason.EXITED

        if state == DecisionState.CLOSED:
            return RankReason.CLOSED

        if state == DecisionState.INVALIDATED:
            return RankReason.EXITED

        if state == DecisionState.EXPIRED:
            return RankReason.EXITED

        return RankReason.BLOCKED


# ============================================================================
# SELF TEST DATA
# ============================================================================

def _decision(
    *,
    decision_id: str,
    market_id: str,
    action: DecisionAction,
    now: datetime,
    scenario: str,
) -> D13DecisionSnapshot:

    return D13DecisionSnapshot(
        decision_id=decision_id,
        market_id=market_id,
        action=action,
        decision_timestamp=now,
        scenario=scenario,
        horizon="5M",
        thesis=f"D13 thesis for {market_id}.",
        provenance={
            "future_outcome_observed": False,
            "validated_by_D14": False,
        },
    )


def _state(
    decision: D13DecisionSnapshot,
    state: DecisionState,
    management: ManagementAction,
    now: datetime,
) -> RankStateSnapshot:

    return RankStateSnapshot(
        decision_id=decision.decision_id,
        market_id=decision.market_id,

        state=state,
        management_action=management,

        as_of=now,

        provenance={
            "future_outcome_observed": False,
            "decision_authority": "D13",
        },
    )


def _evidence(
    decision: D13DecisionSnapshot,
    *,
    name: str,
    polarity: str,
    now: datetime,
) -> RankEvidence:

    return RankEvidence(
        name=name,
        polarity=polarity,
        source="MATRIX",
        timestamp=now,
    )


# ============================================================================
# SELF TESTS
# ============================================================================

def _test_multi_market_ranking() -> None:

    now = datetime.now(timezone.utc)

    nifty = _decision(
        decision_id="D13-NIFTY-001",
        market_id="NSE:NIFTY:INDEX",
        action=DecisionAction.BUY,
        now=now,
        scenario="BULLISH_CONTINUATION",
    )

    gold = _decision(
        decision_id="D13-GOLD-001",
        market_id="COMEX:GOLD:FUTURE",
        action=DecisionAction.BUY,
        now=now,
        scenario="BULLISH_CONTINUATION",
    )

    fx = _decision(
        decision_id="D13-EURUSD-001",
        market_id="FX:EUR/USD:SPOT",
        action=DecisionAction.SELL,
        now=now,
        scenario="BEARISH_CONTINUATION",
    )

    btc = _decision(
        decision_id="D13-BTC-001",
        market_id="BINANCE:BTC/USDT:SPOT",
        action=DecisionAction.BUY,
        now=now,
        scenario="BULLISH_CONTINUATION",
    )

    candidates = [
        OpportunityCandidate(
            decision=nifty,
            state=_state(
                nifty,
                DecisionState.STRENGTHENING,
                ManagementAction.FOLLOW,
                now,
            ),
            evidence=(
                _evidence(
                    nifty,
                    name="STRUCTURE",
                    polarity="SUPPORT",
                    now=now,
                ),
                _evidence(
                    nifty,
                    name="FLOW",
                    polarity="SUPPORT",
                    now=now,
                ),
            ),
        ),

        OpportunityCandidate(
            decision=gold,
            state=_state(
                gold,
                DecisionState.ACTIVE,
                ManagementAction.FOLLOW,
                now,
            ),
            evidence=(
                _evidence(
                    gold,
                    name="STRUCTURE",
                    polarity="SUPPORT",
                    now=now,
                ),
            ),
        ),

        OpportunityCandidate(
            decision=fx,
            state=_state(
                fx,
                DecisionState.ACTIVE,
                ManagementAction.CAUTION,
                now,
            ),
            evidence=(
                _evidence(
                    fx,
                    name="FLOW_CONFLICT",
                    polarity="CONTRADICTION",
                    now=now,
                ),
            ),
        ),

        OpportunityCandidate(
            decision=btc,
            state=_state(
                btc,
                DecisionState.READY,
                ManagementAction.FOLLOW,
                now,
            ),
            evidence=(
                _evidence(
                    btc,
                    name="STRUCTURE",
                    polarity="SUPPORT",
                    now=now,
                ),
            ),
        ),
    ]

    result = OpportunityRankerEngine().rank(
        candidates,
        as_of=now,
    )

    assert result.eligible_count == 4

    ranked = [
        item
        for item in result.ranked
        if item.rank is not None
    ]

    assert ranked[0].market_id == "NSE:NIFTY:INDEX"
    assert ranked[0].rank == 1

    assert ranked[1].market_id == "COMEX:GOLD:FUTURE"
    assert ranked[1].rank == 2

    assert ranked[0].action == DecisionAction.BUY
    assert ranked[1].action == DecisionAction.BUY
    assert ranked[2].action == DecisionAction.SELL


def _test_ranker_does_not_create_direction() -> None:

    now = datetime.now(timezone.utc)

    decision = _decision(
        decision_id="D13-GOLD-002",
        market_id="COMEX:GOLD:FUTURE",
        action=DecisionAction.SELL,
        now=now,
        scenario="BEARISH_CONTINUATION",
    )

    state = _state(
        decision,
        DecisionState.ACTIVE,
        ManagementAction.FOLLOW,
        now,
    )

    result = OpportunityRankerEngine().rank(
        [
            OpportunityCandidate(
                decision=decision,
                state=state,
            )
        ],
        as_of=now,
    )

    item = result.ranked[0]

    assert item.action == DecisionAction.SELL
    assert item.action != DecisionAction.BUY
    assert item.action != DecisionAction.HOLD


def _test_exit_not_ranked() -> None:

    now = datetime.now(timezone.utc)

    decision = _decision(
        decision_id="D13-NIFTY-EXIT-001",
        market_id="NSE:NIFTY:INDEX",
        action=DecisionAction.BUY,
        now=now,
        scenario="BULLISH_CONTINUATION",
    )

    state = _state(
        decision,
        DecisionState.EXIT,
        ManagementAction.EXIT,
        now,
    )

    result = OpportunityRankerEngine().rank(
        [
            OpportunityCandidate(
                decision=decision,
                state=state,
            )
        ],
        as_of=now,
    )

    assert result.eligible_count == 0
    assert result.excluded_count == 1

    item = result.ranked[0]

    assert item.rank is None
    assert item.rank_band == RankBand.NOT_ELIGIBLE


def _test_future_data_block() -> None:

    now = datetime.now(timezone.utc)

    decision = _decision(
        decision_id="D13-BTC-FUTURE-001",
        market_id="BINANCE:BTC/USDT:SPOT",
        action=DecisionAction.BUY,
        now=now,
        scenario="BULLISH_CONTINUATION",
    )

    future = RankEvidence(
        name="FUTURE_OUTCOME",
        polarity="SUPPORT",
        source="D14",
        timestamp=now,
        future=True,
    )

    state = _state(
        decision,
        DecisionState.ACTIVE,
        ManagementAction.FOLLOW,
        now,
    )

    result = OpportunityRankerEngine().rank(
        [
            OpportunityCandidate(
                decision=decision,
                state=state,
                evidence=(future,),
            )
        ],
        as_of=now,
    )

    assert result.eligible_count == 0
    assert result.excluded_count == 1
    assert result.ranked[0].status == RankStatus.BLOCKED
    assert RankReason.FUTURE_DATA in result.ranked[0].reasons


def _test_identity_isolation() -> None:

    now = datetime.now(timezone.utc)

    decision = _decision(
        decision_id="D13-NIFTY-ID-001",
        market_id="NSE:NIFTY:INDEX",
        action=DecisionAction.BUY,
        now=now,
        scenario="BULLISH_CONTINUATION",
    )

    wrong_state = RankStateSnapshot(
        decision_id=decision.decision_id,
        market_id="COMEX:GOLD:FUTURE",
        state=DecisionState.ACTIVE,
        management_action=ManagementAction.FOLLOW,
        as_of=now,
    )

    result = OpportunityRankerEngine().rank(
        [
            OpportunityCandidate(
                decision=decision,
                state=wrong_state,
            )
        ],
        as_of=now,
    )

    assert result.eligible_count == 0
    assert result.excluded_count == 1
    assert result.ranked[0].status == RankStatus.BLOCKED
    assert RankReason.IDENTITY_ERROR in result.ranked[0].reasons


def _test_no_100_score() -> None:

    now = datetime.now(timezone.utc)

    decision = _decision(
        decision_id="D13-GOLD-RANK-001",
        market_id="COMEX:GOLD:FUTURE",
        action=DecisionAction.BUY,
        now=now,
        scenario="BULLISH_CONTINUATION",
    )

    state = _state(
        decision,
        DecisionState.ACTIVE,
        ManagementAction.FOLLOW,
        now,
    )

    result = OpportunityRankerEngine().rank(
        [
            OpportunityCandidate(
                decision=decision,
                state=state,
            )
        ],
        as_of=now,
    )

    item = result.ranked[0]

    assert item.rank == 1
    assert isinstance(item.priority_key, tuple)
    assert "score" not in item.to_dict()
    assert (
        result.provenance[
            "proprietary_0_100_score_used"
        ]
        is False
    )


def _test_timing_influences_priority_without_direction() -> None:

    now = datetime.now(timezone.utc)

    active = _decision(
        decision_id="D13-NIFTY-TIME-001",
        market_id="NSE:NIFTY:INDEX",
        action=DecisionAction.BUY,
        now=now,
        scenario="BULLISH_CONTINUATION",
    )

    normal = _decision(
        decision_id="D13-GOLD-TIME-001",
        market_id="COMEX:GOLD:FUTURE",
        action=DecisionAction.BUY,
        now=now,
        scenario="BULLISH_CONTINUATION",
    )

    state_a = _state(
        active,
        DecisionState.ACTIVE,
        ManagementAction.FOLLOW,
        now,
    )

    state_b = _state(
        normal,
        DecisionState.ACTIVE,
        ManagementAction.FOLLOW,
        now,
    )

    timing_a = RankTimingContext(
        primary_window="5M",
        window_active=True,
        reassessment_due=False,
        timing_status="ACTIVE",
    )

    timing_b = RankTimingContext(
        primary_window="5M",
        window_active=False,
        reassessment_due=False,
        timing_status="INACTIVE",
    )

    result = OpportunityRankerEngine().rank(
        [
            OpportunityCandidate(
                decision=active,
                state=state_a,
                timing=timing_a,
            ),
            OpportunityCandidate(
                decision=normal,
                state=state_b,
                timing=timing_b,
            ),
        ],
        as_of=now,
    )

    ranked = [
        item
        for item in result.ranked
        if item.rank is not None
    ]

    assert ranked[0].market_id == "NSE:NIFTY:INDEX"
    assert ranked[0].action == DecisionAction.BUY
    assert ranked[1].action == DecisionAction.BUY


def _test_d13_immutability() -> None:

    now = datetime.now(timezone.utc)

    decision = _decision(
        decision_id="D13-NIFTY-IMMUTABLE-001",
        market_id="NSE:NIFTY:INDEX",
        action=DecisionAction.BUY,
        now=now,
        scenario="BULLISH_CONTINUATION",
    )

    original_action = decision.action
    original_scenario = decision.scenario
    original_thesis = decision.thesis

    state = _state(
        decision,
        DecisionState.STRENGTHENING,
        ManagementAction.FOLLOW,
        now,
    )

    OpportunityRankerEngine().rank(
        [
            OpportunityCandidate(
                decision=decision,
                state=state,
            )
        ],
        as_of=now,
    )

    assert decision.action == original_action
    assert decision.scenario == original_scenario
    assert decision.thesis == original_thesis


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_self_test() -> None:

    _test_multi_market_ranking()
    _test_ranker_does_not_create_direction()
    _test_exit_not_ranked()
    _test_future_data_block()
    _test_identity_isolation()
    _test_no_100_score()
    _test_timing_influences_priority_without_direction()
    _test_d13_immutability()

    print("OPPORTUNITY RANKER SELF-TEST: PASS")


if __name__ == "__main__":
    run_self_test()