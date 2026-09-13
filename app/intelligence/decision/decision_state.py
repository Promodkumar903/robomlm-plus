"""
ROBOMLM_PLUS
Decision State Engine
---------------------

Role
----
This module DOES NOT make a BUY / SELL / HOLD decision.

D13 remains the sole decision authority.

This module answers:

    "D13 ke decision ki current lifecycle state kya hai?"

It tracks the journey of an already-issued D13 decision:

    SETUP
      ↓
    READY
      ↓
    ACTIVE
      ↓
    STRENGTHENING / WEAKENING
      ↓
    INVALIDATED
      ↓
    EXIT
      ↓
    CLOSED

Possible blocking/terminal states are also represented explicitly.

Design rules
------------
1. Never create a new BUY / SELL / HOLD decision.
2. Never overwrite the original D13 decision.
3. Never use future information.
4. Never silently treat missing data as neutral.
5. Preserve market identity.
6. Preserve D13 provenance.
7. State transitions must be traceable.
8. EXIT means the existing D13 thesis should no longer be followed.
9. CLOSED means the decision/trade lifecycle has ended.
10. This is lifecycle intelligence, not a second decision engine.

Exact proprietary V6 numerical state formula is not assumed here.
State derivation is structural and evidence-driven until the original
V6 specification is recovered.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence


# ---------------------------------------------------------------------------
# ENUMS
# ---------------------------------------------------------------------------

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


class StateStatus(str, Enum):
    READY = "READY"
    LIMITED = "LIMITED"
    BLOCKED = "BLOCKED"
    UNDETERMINED = "UNDETERMINED"


class EvidencePolarity(str, Enum):
    SUPPORT = "SUPPORT"
    CONTRADICTION = "CONTRADICTION"
    CAUTION = "CAUTION"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"


class StateReason(str, Enum):
    D13_DECISION_RECEIVED = "D13_DECISION_RECEIVED"
    DECISION_READY = "DECISION_READY"
    DECISION_ACTIVE = "DECISION_ACTIVE"

    THESIS_SUPPORTED = "THESIS_SUPPORTED"
    THESIS_STRENGTHENING = "THESIS_STRENGTHENING"
    THESIS_WEAKENING = "THESIS_WEAKENING"

    INVALIDATION_TRIGGERED = "INVALIDATION_TRIGGERED"
    EXIT_REQUIRED = "EXIT_REQUIRED"

    DECISION_CLOSED = "DECISION_CLOSED"
    DECISION_EXPIRED = "DECISION_EXPIRED"

    BLOCKED_INPUT = "BLOCKED_INPUT"
    MISSING_INPUT = "MISSING_INPUT"
    FUTURE_DATA = "FUTURE_DATA"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    TIMESTAMP_ERROR = "TIMESTAMP_ERROR"

    NO_LIVE_EVIDENCE = "NO_LIVE_EVIDENCE"
    STATE_UNDETERMINED = "STATE_UNDETERMINED"


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _parse_timestamp(value: Any) -> Optional[datetime]:
    """
    Parse an ISO timestamp and normalize it to UTC.

    Naive timestamps are rejected because temporal state is critical.
    """
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        text = value.strip()

        if not text:
            return None

        try:
            dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return None
    else:
        return None

    if dt.tzinfo is None:
        return None

    return dt.astimezone(timezone.utc)


def _as_bool(value: Any) -> bool:
    return bool(value) if value is not None else False


# ---------------------------------------------------------------------------
# D13 SNAPSHOT
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class D13DecisionSnapshot:
    """
    Immutable snapshot of the D13 decision.

    This is intentionally a snapshot.

    State engine may read it, but must never mutate it.
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

        if not isinstance(self.decision_timestamp, datetime):
            raise TypeError("decision_timestamp must be datetime")

        if self.decision_timestamp.tzinfo is None:
            raise ValueError("decision_timestamp must be timezone-aware")


# ---------------------------------------------------------------------------
# LIVE EVIDENCE
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class StateEvidence:
    """
    Current evidence used ONLY to evaluate the lifecycle of D13.

    It does not create a new decision.
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

    invalidation_triggered: bool = False

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None:
            raise ValueError("StateEvidence.timestamp must be timezone-aware")

        if not self.market_id:
            raise ValueError("StateEvidence.market_id is required")

        if not self.name:
            raise ValueError("StateEvidence.name is required")


# ---------------------------------------------------------------------------
# STATE RESULT
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DecisionStateResult:
    decision_id: str
    market_id: str

    action: DecisionAction
    state: DecisionState
    status: StateStatus

    as_of: datetime

    reasons: Sequence[StateReason] = field(default_factory=tuple)

    supporting_evidence: Sequence[str] = field(default_factory=tuple)
    contradicting_evidence: Sequence[str] = field(default_factory=tuple)
    caution_evidence: Sequence[str] = field(default_factory=tuple)

    invalidation_triggered: bool = False

    previous_state: Optional[DecisionState] = None

    state_changed: bool = False

    provenance: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "market_id": self.market_id,
            "action": self.action.value,
            "state": self.state.value,
            "status": self.status.value,
            "as_of": self.as_of.isoformat(),

            "reasons": [r.value for r in self.reasons],

            "supporting_evidence": list(self.supporting_evidence),
            "contradicting_evidence": list(self.contradicting_evidence),
            "caution_evidence": list(self.caution_evidence),

            "invalidation_triggered": self.invalidation_triggered,

            "previous_state": (
                self.previous_state.value
                if self.previous_state is not None
                else None
            ),

            "state_changed": self.state_changed,

            "provenance": dict(self.provenance),
        }


# ---------------------------------------------------------------------------
# STATE ENGINE
# ---------------------------------------------------------------------------

class DecisionStateEngine:
    """
    Lifecycle state engine for D13 decisions.

    IMPORTANT:
        This engine does not decide BUY / SELL / HOLD.

    It receives D13's decision and determines the current lifecycle state.
    """

    VERSION = "DECISION-STATE-1.0"

    def evaluate(
        self,
        decision: D13DecisionSnapshot,
        *,
        evidence: Optional[Iterable[StateEvidence]] = None,
        as_of: Optional[datetime] = None,
        previous_state: Optional[DecisionState] = None,
        manually_closed: bool = False,
    ) -> DecisionStateResult:

        now = as_of or datetime.now(timezone.utc)

        if now.tzinfo is None:
            return self._blocked_result(
                decision,
                now,
                StateReason.TIMESTAMP_ERROR,
                previous_state,
            )

        now = now.astimezone(timezone.utc)

        decision_time = _parse_timestamp(decision.decision_timestamp)

        if decision_time is None:
            return self._blocked_result(
                decision,
                now,
                StateReason.TIMESTAMP_ERROR,
                previous_state,
            )

        # ------------------------------------------------------------------
        # D13 provenance guard
        # ------------------------------------------------------------------

        provenance = dict(decision.provenance)

        if provenance.get("future_outcome_observed") is True:
            return self._blocked_result(
                decision,
                now,
                StateReason.FUTURE_DATA,
                previous_state,
            )

        # ------------------------------------------------------------------
        # Decision itself must already exist.
        # ------------------------------------------------------------------

        if decision.action == DecisionAction.BLOCKED:
            return self._result(
                decision=decision,
                now=now,
                state=DecisionState.BLOCKED,
                status=StateStatus.BLOCKED,
                reasons=(StateReason.BLOCKED_INPUT,),
                previous_state=previous_state,
                provenance=provenance,
            )

        if decision.action in (
            DecisionAction.WAIT,
            DecisionAction.NO_ACTION,
        ):
            return self._result(
                decision=decision,
                now=now,
                state=DecisionState.READY,
                status=StateStatus.READY,
                reasons=(StateReason.DECISION_READY,),
                previous_state=previous_state,
                provenance=provenance,
            )

        # ------------------------------------------------------------------
        # CLOSED is terminal.
        # ------------------------------------------------------------------

        if manually_closed:
            return self._result(
                decision=decision,
                now=now,
                state=DecisionState.CLOSED,
                status=StateStatus.READY,
                reasons=(StateReason.DECISION_CLOSED,),
                previous_state=previous_state,
                provenance=provenance,
            )

        # ------------------------------------------------------------------
        # Normalize evidence.
        # ------------------------------------------------------------------

        clean_evidence: List[StateEvidence] = []

        for item in evidence or []:

            if item.market_id != decision.market_id:
                return self._blocked_result(
                    decision,
                    now,
                    StateReason.IDENTITY_MISMATCH,
                    previous_state,
                )

            if item.timestamp > now:
                return self._blocked_result(
                    decision,
                    now,
                    StateReason.FUTURE_DATA,
                    previous_state,
                )

            if item.future:
                return self._blocked_result(
                    decision,
                    now,
                    StateReason.FUTURE_DATA,
                    previous_state,
                )

            clean_evidence.append(item)

        clean_evidence.sort(key=lambda x: x.timestamp)

        # ------------------------------------------------------------------
        # No live evidence.
        # ------------------------------------------------------------------

        if not clean_evidence:

            # Existing ACTIVE state should not silently become EXIT merely
            # because evidence is absent.
            # Missing evidence means lifecycle cannot be confidently updated.
            state = (
                previous_state
                if previous_state is not None
                else DecisionState.READY
            )

            return self._result(
                decision=decision,
                now=now,
                state=state,
                status=StateStatus.LIMITED,
                reasons=(StateReason.NO_LIVE_EVIDENCE,),
                previous_state=previous_state,
                provenance=provenance,
            )

        # ------------------------------------------------------------------
        # Evidence classification.
        # ------------------------------------------------------------------

        supporting = [
            e.name
            for e in clean_evidence
            if e.polarity == EvidencePolarity.SUPPORT
        ]

        contradicting = [
            e.name
            for e in clean_evidence
            if e.polarity == EvidencePolarity.CONTRADICTION
        ]

        caution = [
            e.name
            for e in clean_evidence
            if e.polarity == EvidencePolarity.CAUTION
        ]

        invalidation = any(
            e.invalidation_triggered
            for e in clean_evidence
        )

        # ------------------------------------------------------------------
        # STALE DATA
        # ------------------------------------------------------------------

        usable_evidence = [
            e for e in clean_evidence
            if not e.stale
        ]

        if not usable_evidence:
            return self._result(
                decision=decision,
                now=now,
                state=(
                    previous_state
                    if previous_state is not None
                    else DecisionState.READY
                ),
                status=StateStatus.LIMITED,
                reasons=(StateReason.MISSING_INPUT,),
                supporting_evidence=supporting,
                contradicting_evidence=contradicting,
                caution_evidence=caution,
                previous_state=previous_state,
                provenance=provenance,
            )

        # ------------------------------------------------------------------
        # INVALIDATION HAS PRIORITY.
        # ------------------------------------------------------------------

        if invalidation:
            return self._result(
                decision=decision,
                now=now,
                state=DecisionState.EXIT,
                status=StateStatus.READY,
                reasons=(
                    StateReason.INVALIDATION_TRIGGERED,
                    StateReason.EXIT_REQUIRED,
                ),
                supporting_evidence=supporting,
                contradicting_evidence=contradicting,
                caution_evidence=caution,
                invalidation_triggered=True,
                previous_state=previous_state,
                provenance=provenance,
            )

        # ------------------------------------------------------------------
        # Strong contradiction => WEAKENING / INVALIDATED.
        #
        # We do NOT automatically call it invalidated unless the actual
        # invalidation condition is explicitly supplied.
        # ------------------------------------------------------------------

        if contradicting:
            state = DecisionState.WEAKENING

            if previous_state == DecisionState.WEAKENING:
                state = DecisionState.WEAKENING

            return self._result(
                decision=decision,
                now=now,
                state=state,
                status=StateStatus.READY,
                reasons=(StateReason.THESIS_WEAKENING,),
                supporting_evidence=supporting,
                contradicting_evidence=contradicting,
                caution_evidence=caution,
                previous_state=previous_state,
                provenance=provenance,
            )

        # ------------------------------------------------------------------
        # SUPPORT
        # ------------------------------------------------------------------

        if supporting and not caution:
            if previous_state in (
                DecisionState.ACTIVE,
                DecisionState.STRENGTHENING,
            ):
                state = DecisionState.STRENGTHENING
                reason = StateReason.THESIS_STRENGTHENING
            else:
                state = DecisionState.ACTIVE
                reason = StateReason.DECISION_ACTIVE

            return self._result(
                decision=decision,
                now=now,
                state=state,
                status=StateStatus.READY,
                reasons=(reason,),
                supporting_evidence=supporting,
                contradicting_evidence=contradicting,
                caution_evidence=caution,
                previous_state=previous_state,
                provenance=provenance,
            )

        # ------------------------------------------------------------------
        # SUPPORT + CAUTION
        # ------------------------------------------------------------------

        if supporting and caution:
            return self._result(
                decision=decision,
                now=now,
                state=DecisionState.ACTIVE,
                status=StateStatus.LIMITED,
                reasons=(StateReason.THESIS_SUPPORTED,),
                supporting_evidence=supporting,
                contradicting_evidence=contradicting,
                caution_evidence=caution,
                previous_state=previous_state,
                provenance=provenance,
            )

        # ------------------------------------------------------------------
        # ONLY CAUTION / NEUTRAL / UNKNOWN
        # ------------------------------------------------------------------

        return self._result(
            decision=decision,
            now=now,
            state=(
                previous_state
                if previous_state is not None
                else DecisionState.READY
            ),
            status=StateStatus.UNDETERMINED,
            reasons=(StateReason.STATE_UNDETERMINED,),
            supporting_evidence=supporting,
            contradicting_evidence=contradicting,
            caution_evidence=caution,
            previous_state=previous_state,
            provenance=provenance,
        )

    # ----------------------------------------------------------------------
    # RESULT HELPERS
    # ----------------------------------------------------------------------

    def _result(
        self,
        *,
        decision: D13DecisionSnapshot,
        now: datetime,
        state: DecisionState,
        status: StateStatus,
        reasons: Sequence[StateReason],
        previous_state: Optional[DecisionState],
        provenance: Mapping[str, Any],
        supporting_evidence: Sequence[str] = (),
        contradicting_evidence: Sequence[str] = (),
        caution_evidence: Sequence[str] = (),
        invalidation_triggered: bool = False,
    ) -> DecisionStateResult:

        return DecisionStateResult(
            decision_id=decision.decision_id,
            market_id=decision.market_id,
            action=decision.action,
            state=state,
            status=status,
            as_of=now,
            reasons=tuple(reasons),
            supporting_evidence=tuple(supporting_evidence),
            contradicting_evidence=tuple(contradicting_evidence),
            caution_evidence=tuple(caution_evidence),
            invalidation_triggered=invalidation_triggered,
            previous_state=previous_state,
            state_changed=(
                previous_state is not None
                and previous_state != state
            ),
            provenance={
                **dict(provenance),
                "engine": "DecisionStateEngine",
                "engine_version": self.VERSION,
                "decision_authority": "D13",
                "new_decision_created": False,
                "d13_decision_modified": False,
                "future_outcome_observed": False,
            },
        )

    def _blocked_result(
        self,
        decision: D13DecisionSnapshot,
        now: datetime,
        reason: StateReason,
        previous_state: Optional[DecisionState],
    ) -> DecisionStateResult:

        return self._result(
            decision=decision,
            now=now,
            state=DecisionState.BLOCKED,
            status=StateStatus.BLOCKED,
            reasons=(reason,),
            previous_state=previous_state,
            provenance=decision.provenance,
        )


# ---------------------------------------------------------------------------
# SELF TEST
# ---------------------------------------------------------------------------

def _test_d13_buy_active() -> None:

    now = datetime.now(timezone.utc)

    decision = D13DecisionSnapshot(
        decision_id="D13-NIFTY-001",
        market_id="NSE:NIFTY:INDEX",
        action=DecisionAction.BUY,
        decision_timestamp=now,
        scenario="BULLISH_CONTINUATION",
        horizon="5M",
        thesis="Structure and flow support continuation.",
        invalidation_condition="Explicit D13 invalidation condition.",
        provenance={
            "future_outcome_observed": False,
            "validated_by_D14": False,
        },
    )

    evidence = [
        StateEvidence(
            timestamp=now,
            market_id="NSE:NIFTY:INDEX",
            source="MATRIX",
            name="STRUCTURE",
            polarity=EvidencePolarity.SUPPORT,
        ),
        StateEvidence(
            timestamp=now,
            market_id="NSE:NIFTY:INDEX",
            source="MATRIX",
            name="FLOW",
            polarity=EvidencePolarity.SUPPORT,
        ),
    ]

    result = DecisionStateEngine().evaluate(
        decision,
        evidence=evidence,
        as_of=now,
    )

    assert result.action == DecisionAction.BUY
    assert result.state == DecisionState.ACTIVE
    assert result.status == StateStatus.READY
    assert result.provenance["decision_authority"] == "D13"
    assert result.provenance["new_decision_created"] is False


def _test_strengthening() -> None:

    now = datetime.now(timezone.utc)

    decision = D13DecisionSnapshot(
        decision_id="D13-GOLD-001",
        market_id="COMEX:GOLD:FUTURE",
        action=DecisionAction.BUY,
        decision_timestamp=now,
        scenario="BULLISH_CONTINUATION",
        horizon="15M",
        provenance={
            "future_outcome_observed": False,
        },
    )

    evidence = [
        StateEvidence(
            timestamp=now,
            market_id="COMEX:GOLD:FUTURE",
            source="MATRIX",
            name="FLOW",
            polarity=EvidencePolarity.SUPPORT,
        )
    ]

    result = DecisionStateEngine().evaluate(
        decision,
        evidence=evidence,
        as_of=now,
        previous_state=DecisionState.ACTIVE,
    )

    assert result.state == DecisionState.STRENGTHENING
    assert result.state_changed is True


def _test_weakening() -> None:

    now = datetime.now(timezone.utc)

    decision = D13DecisionSnapshot(
        decision_id="D13-FX-001",
        market_id="FX:EUR/USD:SPOT",
        action=DecisionAction.SELL,
        decision_timestamp=now,
        scenario="BEARISH_CONTINUATION",
        horizon="5M",
        provenance={
            "future_outcome_observed": False,
        },
    )

    evidence = [
        StateEvidence(
            timestamp=now,
            market_id="FX:EUR/USD:SPOT",
            source="MATRIX",
            name="FLOW_CONFLICT",
            polarity=EvidencePolarity.CONTRADICTION,
        )
    ]

    result = DecisionStateEngine().evaluate(
        decision,
        evidence=evidence,
        as_of=now,
        previous_state=DecisionState.ACTIVE,
    )

    assert result.state == DecisionState.WEAKENING


def _test_invalidation_exit() -> None:

    now = datetime.now(timezone.utc)

    decision = D13DecisionSnapshot(
        decision_id="D13-BTC-001",
        market_id="BINANCE:BTC/USDT:SPOT",
        action=DecisionAction.BUY,
        decision_timestamp=now,
        scenario="BULLISH_CONTINUATION",
        horizon="5M",
        invalidation_condition="Explicit invalidation condition.",
        provenance={
            "future_outcome_observed": False,
        },
    )

    evidence = [
        StateEvidence(
            timestamp=now,
            market_id="BINANCE:BTC/USDT:SPOT",
            source="DECISION_MONITOR",
            name="D13_INVALIDATION",
            polarity=EvidencePolarity.CONTRADICTION,
            invalidation_triggered=True,
        )
    ]

    result = DecisionStateEngine().evaluate(
        decision,
        evidence=evidence,
        as_of=now,
        previous_state=DecisionState.WEAKENING,
    )

    assert result.state == DecisionState.EXIT
    assert result.invalidation_triggered is True
    assert StateReason.EXIT_REQUIRED in result.reasons


def _test_identity_guard() -> None:

    now = datetime.now(timezone.utc)

    decision = D13DecisionSnapshot(
        decision_id="D13-NIFTY-002",
        market_id="NSE:NIFTY:INDEX",
        action=DecisionAction.BUY,
        decision_timestamp=now,
        provenance={
            "future_outcome_observed": False,
        },
    )

    evidence = [
        StateEvidence(
            timestamp=now,
            market_id="COMEX:GOLD:FUTURE",
            source="MATRIX",
            name="STRUCTURE",
            polarity=EvidencePolarity.SUPPORT,
        )
    ]

    result = DecisionStateEngine().evaluate(
        decision,
        evidence=evidence,
        as_of=now,
    )

    assert result.state == DecisionState.BLOCKED
    assert StateReason.IDENTITY_MISMATCH in result.reasons


def _test_future_guard() -> None:

    now = datetime.now(timezone.utc)

    decision = D13DecisionSnapshot(
        decision_id="D13-SPX-001",
        market_id="CME:SPX:INDEX",
        action=DecisionAction.BUY,
        decision_timestamp=now,
        provenance={
            "future_outcome_observed": False,
        },
    )

    future_evidence = [
        StateEvidence(
            timestamp=now,
            market_id="CME:SPX:INDEX",
            source="D14",
            name="FUTURE_OUTCOME",
            polarity=EvidencePolarity.SUPPORT,
            future=True,
        )
    ]

    result = DecisionStateEngine().evaluate(
        decision,
        evidence=future_evidence,
        as_of=now,
    )

    assert result.state == DecisionState.BLOCKED
    assert StateReason.FUTURE_DATA in result.reasons


def _test_d13_blocked_passthrough() -> None:

    now = datetime.now(timezone.utc)

    decision = D13DecisionSnapshot(
        decision_id="D13-BLOCKED-001",
        market_id="NSE:NIFTY:INDEX",
        action=DecisionAction.BLOCKED,
        decision_timestamp=now,
        provenance={
            "future_outcome_observed": False,
        },
    )

    result = DecisionStateEngine().evaluate(
        decision,
        as_of=now,
    )

    assert result.action == DecisionAction.BLOCKED
    assert result.state == DecisionState.BLOCKED


def _test_no_evidence_does_not_force_exit() -> None:

    now = datetime.now(timezone.utc)

    decision = D13DecisionSnapshot(
        decision_id="D13-NIFTY-003",
        market_id="NSE:NIFTY:INDEX",
        action=DecisionAction.BUY,
        decision_timestamp=now,
        provenance={
            "future_outcome_observed": False,
        },
    )

    result = DecisionStateEngine().evaluate(
        decision,
        evidence=[],
        as_of=now,
        previous_state=DecisionState.ACTIVE,
    )

    assert result.state == DecisionState.ACTIVE
    assert result.status == StateStatus.LIMITED
    assert StateReason.NO_LIVE_EVIDENCE in result.reasons


def _test_manual_close() -> None:

    now = datetime.now(timezone.utc)

    decision = D13DecisionSnapshot(
        decision_id="D13-GOLD-002",
        market_id="COMEX:GOLD:FUTURE",
        action=DecisionAction.BUY,
        decision_timestamp=now,
        provenance={
            "future_outcome_observed": False,
        },
    )

    result = DecisionStateEngine().evaluate(
        decision,
        as_of=now,
        previous_state=DecisionState.EXIT,
        manually_closed=True,
    )

    assert result.state == DecisionState.CLOSED


def run_self_test() -> None:

    _test_d13_buy_active()
    _test_strengthening()
    _test_weakening()
    _test_invalidation_exit()
    _test_identity_guard()
    _test_future_guard()
    _test_d13_blocked_passthrough()
    _test_no_evidence_does_not_force_exit()
    _test_manual_close()

    print("DECISION STATE SELF-TEST: PASS")


if __name__ == "__main__":
    run_self_test()