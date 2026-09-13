"""
ROBOMLM_PLUS
Decision Timing Engine
----------------------

ROLE
----
Temporal management layer for an EXISTING D13 decision.

D13 remains the ONLY current directional decision authority.

Timing Engine answers:

    - Which operating window is governing the decision?
    - How long has the decision been active?
    - How much of the current operating window remains?
    - When should the decision be reassessed?
    - What higher timeframe is context?
    - What lower timeframe is confirmation?
    - Is the operating window currently active?
    - Has reassessment become due?
    - Has an existing invalidation/exit state already occurred?

Timing Engine MUST NOT:

    - create BUY
    - create SELL
    - change D13 action
    - create a new trading thesis
    - automatically EXIT only because a window ended
    - use future outcome information
    - fabricate probability
    - create arbitrary 0-100 timing scores

PRIMARY WINDOW PRINCIPLE
------------------------
The selected primary timeframe is the operating window.

Examples:

    Primary 5M:
        Context      = 1H / 15M
        Operating    = 5M
        Confirmation = 1M / tick

    Primary 1H:
        Context      = 4H
        Operating    = 1H
        Confirmation = 15M / 5M

The exact context/confirmation mapping can be supplied by the caller.

WINDOW END
----------
Window end does NOT automatically mean EXIT.

At window end the engine returns:

    reassessment_due = True

The caller must evaluate the current D13 thesis/state again.

EXIT is reflected only when an existing decision/state/invalidation
already says EXIT.

FUTURE DATA
-----------
All timing observations must be <= as_of.

This engine is temporal management, not a future-data generator.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Mapping, Optional, Sequence, Tuple


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


class TimingPhase(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    ACTIVE = "ACTIVE"
    REASSESSMENT_DUE = "REASSESSMENT_DUE"
    WINDOW_ENDED = "WINDOW_ENDED"
    EXIT_CONTEXT = "EXIT_CONTEXT"
    BLOCKED = "BLOCKED"


class TimingStatus(str, Enum):
    READY = "READY"
    ACTIVE = "ACTIVE"
    DUE = "DUE"
    ENDED = "ENDED"
    LIMITED = "LIMITED"
    BLOCKED = "BLOCKED"


class TimingReason(str, Enum):
    D13_DECISION = "D13_DECISION"

    PRIMARY_WINDOW_ACTIVE = "PRIMARY_WINDOW_ACTIVE"
    PRIMARY_WINDOW_ENDED = "PRIMARY_WINDOW_ENDED"

    REASSESSMENT_DUE = "REASSESSMENT_DUE"
    REASSESSMENT_NOT_DUE = "REASSESSMENT_NOT_DUE"

    FOLLOW_WINDOW = "FOLLOW_WINDOW"
    CONTEXT_WINDOW = "CONTEXT_WINDOW"
    CONFIRMATION_WINDOW = "CONFIRMATION_WINDOW"

    EXISTING_EXIT_STATE = "EXISTING_EXIT_STATE"
    EXISTING_INVALIDATION = "EXISTING_INVALIDATION"

    FUTURE_DATA = "FUTURE_DATA"
    INVALID_TIMESTAMP = "INVALID_TIMESTAMP"
    INVALID_WINDOW = "INVALID_WINDOW"
    IDENTITY_ERROR = "IDENTITY_ERROR"

    NO_AUTOMATIC_EXIT = "NO_AUTOMATIC_EXIT"

    TIMING_COMPLETE = "TIMING_COMPLETE"


# ============================================================================
# D13 SNAPSHOT
# ============================================================================

@dataclass(frozen=True)
class D13DecisionSnapshot:
    """
    Immutable current D13 decision.
    """

    decision_id: str
    market_id: str
    action: DecisionAction
    decision_timestamp: datetime

    primary_timeframe: str

    scenario: Optional[str] = None
    horizon: Optional[str] = None

    provenance: Mapping[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:

        if not self.decision_id:
            raise ValueError("decision_id is required")

        if not self.market_id:
            raise ValueError("market_id is required")

        if not self.primary_timeframe:
            raise ValueError(
                "primary_timeframe is required"
            )

        if self.decision_timestamp.tzinfo is None:
            raise ValueError(
                "decision_timestamp must be timezone-aware"
            )


# ============================================================================
# CURRENT STATE
# ============================================================================

@dataclass(frozen=True)
class DecisionStateSnapshot:
    """
    Current state supplied by decision_state.py.
    """

    decision_id: str
    market_id: str

    state: str

    invalidation_triggered: bool = False

    exit_required: bool = False

    as_of: Optional[datetime] = None

    provenance: Mapping[str, Any] = field(
        default_factory=dict
    )


# ============================================================================
# TIMING CONTRACT
# ============================================================================

@dataclass(frozen=True)
class TimingWindowContract:
    """
    Operating-window definition.

    duration_seconds is the actual primary operating-window duration.

    context_timeframes and confirmation_timeframes are supporting
    timeframes and do not replace the primary window.
    """

    primary_timeframe: str

    duration_seconds: float

    context_timeframes: Tuple[str, ...] = tuple()

    confirmation_timeframes: Tuple[str, ...] = tuple()

    reassessment_seconds: Optional[float] = None

    def __post_init__(self) -> None:

        if not self.primary_timeframe:
            raise ValueError(
                "primary_timeframe is required"
            )

        if self.duration_seconds <= 0:
            raise ValueError(
                "duration_seconds must be > 0"
            )

        if (
            self.reassessment_seconds is not None
            and self.reassessment_seconds <= 0
        ):
            raise ValueError(
                "reassessment_seconds must be > 0"
            )


# ============================================================================
# TIMING RESULT
# ============================================================================

@dataclass(frozen=True)
class DecisionTimingResult:
    """
    Complete timing state for one D13 decision.
    """

    decision_id: str
    market_id: str

    action: DecisionAction

    primary_timeframe: str

    cycle_start: datetime
    cycle_end: datetime

    as_of: datetime

    elapsed_seconds: float
    remaining_seconds: float

    elapsed_fraction: float
    remaining_fraction: float

    window_active: bool

    reassessment_due: bool

    next_reassessment_at: Optional[datetime]

    phase: TimingPhase
    status: TimingStatus

    context_timeframes: Sequence[str]
    confirmation_timeframes: Sequence[str]

    exit_required: bool

    reasons: Sequence[TimingReason]

    provenance: Mapping[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict:

        return {
            "decision_id": self.decision_id,
            "market_id": self.market_id,

            "action": self.action.value,

            "primary_timeframe": self.primary_timeframe,

            "cycle_start": self.cycle_start.isoformat(),
            "cycle_end": self.cycle_end.isoformat(),
            "as_of": self.as_of.isoformat(),

            "elapsed_seconds": self.elapsed_seconds,
            "remaining_seconds": self.remaining_seconds,

            "elapsed_fraction": self.elapsed_fraction,
            "remaining_fraction": self.remaining_fraction,

            "window_active": self.window_active,
            "reassessment_due": self.reassessment_due,

            "next_reassessment_at": (
                self.next_reassessment_at.isoformat()
                if self.next_reassessment_at is not None
                else None
            ),

            "phase": self.phase.value,
            "status": self.status.value,

            "context_timeframes": list(
                self.context_timeframes
            ),

            "confirmation_timeframes": list(
                self.confirmation_timeframes
            ),

            "exit_required": self.exit_required,

            "reasons": [
                reason.value
                for reason in self.reasons
            ],

            "provenance": dict(self.provenance),
        }


# ============================================================================
# ENGINE
# ============================================================================

class DecisionTimingEngine:
    """
    Temporal management engine for D13 decisions.
    """

    VERSION = "DECISION-TIMING-1.0"

    # ------------------------------------------------------------------------
    # Common timeframe durations.
    #
    # These are duration representations only.
    # They are NOT trading signals or exit rules.
    # ------------------------------------------------------------------------

    TIMEFRAME_SECONDS = {
        "1m": 60.0,
        "3m": 180.0,
        "5m": 300.0,
        "15m": 900.0,
        "30m": 1800.0,

        "1h": 3600.0,
        "2h": 7200.0,
        "4h": 14400.0,

        "1d": 86400.0,
    }

    # ------------------------------------------------------------------------
    # Explicit default timeframe relationships.
    #
    # These are structural timeframe relationships, not directional logic.
    # Caller can override them through TimingWindowContract.
    # ------------------------------------------------------------------------

    DEFAULT_CONTEXT = {
        "1m": ("5m", "15m"),
        "3m": ("15m", "1h"),
        "5m": ("15m", "1h"),
        "15m": ("1h", "4h"),
        "30m": ("1h", "4h"),
        "1h": ("4h", "1d"),
        "2h": ("4h", "1d"),
        "4h": ("1d",),
        "1d": tuple(),
    }

    DEFAULT_CONFIRMATION = {
        "1m": tuple(),
        "3m": ("1m",),
        "5m": ("1m", "3m"),
        "15m": ("5m",),
        "30m": ("5m", "15m"),
        "1h": ("5m", "15m"),
        "2h": ("15m", "30m"),
        "4h": ("15m", "1h"),
        "1d": ("1h", "4h"),
    }

    # ========================================================================
    # PUBLIC
    # ========================================================================

    def evaluate(
        self,
        decision: D13DecisionSnapshot,
        *,
        as_of: datetime,
        window: Optional[TimingWindowContract] = None,
        state: Optional[DecisionStateSnapshot] = None,
    ) -> DecisionTimingResult:

        if as_of.tzinfo is None:
            raise ValueError(
                "as_of must be timezone-aware"
            )

        now = as_of.astimezone(timezone.utc)

        # ------------------------------------------------------------------
        # D13 future-data guard
        # ------------------------------------------------------------------

        if decision.decision_timestamp > now:

            return self._blocked_result(
                decision=decision,
                as_of=now,
                reason=TimingReason.FUTURE_DATA,
            )

        # ------------------------------------------------------------------
        # Existing D13 future-outcome guard
        # ------------------------------------------------------------------

        if decision.provenance.get(
            "future_outcome_observed"
        ) is True:

            return self._blocked_result(
                decision=decision,
                as_of=now,
                reason=TimingReason.FUTURE_DATA,
            )

        # ------------------------------------------------------------------
        # Window resolution
        # ------------------------------------------------------------------

        try:
            resolved = self._resolve_window(
                decision,
                window,
            )
        except ValueError:

            return self._blocked_result(
                decision=decision,
                as_of=now,
                reason=TimingReason.INVALID_WINDOW,
            )

        cycle_start = decision.decision_timestamp.astimezone(
            timezone.utc
        )

        cycle_end = (
            cycle_start
            + timedelta(
                seconds=resolved.duration_seconds
            )
        )

        # ------------------------------------------------------------------
        # State identity guard
        # ------------------------------------------------------------------

        if state is not None:

            if state.decision_id != decision.decision_id:
                return self._blocked_result(
                    decision=decision,
                    as_of=now,
                    reason=TimingReason.IDENTITY_ERROR,
                )

            if state.market_id != decision.market_id:
                return self._blocked_result(
                    decision=decision,
                    as_of=now,
                    reason=TimingReason.IDENTITY_ERROR,
                )

            if state.as_of is not None:

                state_as_of = state.as_of

                if state_as_of.tzinfo is None:
                    return self._blocked_result(
                        decision=decision,
                        as_of=now,
                        reason=TimingReason.INVALID_TIMESTAMP,
                    )

                if state_as_of > now:
                    return self._blocked_result(
                        decision=decision,
                        as_of=now,
                        reason=TimingReason.FUTURE_DATA,
                    )

        # ------------------------------------------------------------------
        # Existing exit / invalidation has precedence.
        # ------------------------------------------------------------------

        exit_required = False
        existing_exit = False
        existing_invalidation = False

        if state is not None:

            existing_exit = (
                state.exit_required
                or state.state.upper()
                in {
                    "EXIT",
                    "INVALIDATED",
                    "CLOSED",
                }
            )

            existing_invalidation = (
                state.invalidation_triggered
            )

            if existing_exit or existing_invalidation:
                exit_required = True

        # ------------------------------------------------------------------
        # Elapsed / remaining.
        # ------------------------------------------------------------------

        raw_elapsed = (
            now - cycle_start
        ).total_seconds()

        elapsed_seconds = max(
            0.0,
            min(
                raw_elapsed,
                resolved.duration_seconds,
            ),
        )

        remaining_seconds = max(
            0.0,
            resolved.duration_seconds
            - elapsed_seconds,
        )

        elapsed_fraction = (
            elapsed_seconds
            / resolved.duration_seconds
        )

        remaining_fraction = (
            remaining_seconds
            / resolved.duration_seconds
        )

        # ------------------------------------------------------------------
        # Window state.
        # ------------------------------------------------------------------

        if now < cycle_start:

            phase = TimingPhase.NOT_STARTED
            status = TimingStatus.READY

            window_active = False

        elif now < cycle_end:

            window_active = True

            if exit_required:

                phase = TimingPhase.EXIT_CONTEXT
                status = TimingStatus.ACTIVE

            else:

                # Reassessment may be explicitly configured.
                due = self._is_reassessment_due(
                    cycle_start=cycle_start,
                    now=now,
                    contract=resolved,
                )

                if due:

                    phase = TimingPhase.REASSESSMENT_DUE
                    status = TimingStatus.DUE

                else:

                    phase = TimingPhase.ACTIVE
                    status = TimingStatus.ACTIVE

        else:

            window_active = False

            if exit_required:

                phase = TimingPhase.EXIT_CONTEXT
                status = TimingStatus.ENDED

            else:

                phase = TimingPhase.WINDOW_ENDED
                status = TimingStatus.ENDED

        # ------------------------------------------------------------------
        # Reassessment.
        #
        # Window end itself causes reassessment, NOT automatic EXIT.
        # ------------------------------------------------------------------

        reassessment_due = False

        if exit_required:

            reassessment_due = True

        elif now >= cycle_end:

            reassessment_due = True

        elif self._is_reassessment_due(
            cycle_start=cycle_start,
            now=now,
            contract=resolved,
        ):

            reassessment_due = True

        # ------------------------------------------------------------------
        # Next reassessment.
        # ------------------------------------------------------------------

        next_reassessment_at = self._next_reassessment(
            cycle_start=cycle_start,
            cycle_end=cycle_end,
            now=now,
            contract=resolved,
        )

        # ------------------------------------------------------------------
        # Reasons.
        # ------------------------------------------------------------------

        reasons = [
            TimingReason.D13_DECISION,
        ]

        if window_active:
            reasons.append(
                TimingReason.PRIMARY_WINDOW_ACTIVE
            )

        if now >= cycle_end:
            reasons.append(
                TimingReason.PRIMARY_WINDOW_ENDED
            )

        if reassessment_due:
            reasons.append(
                TimingReason.REASSESSMENT_DUE
            )
        else:
            reasons.append(
                TimingReason.REASSESSMENT_NOT_DUE
            )

        if resolved.context_timeframes:
            reasons.append(
                TimingReason.CONTEXT_WINDOW
            )

        if resolved.confirmation_timeframes:
            reasons.append(
                TimingReason.CONFIRMATION_WINDOW
            )

        if exit_required:

            if existing_exit:
                reasons.append(
                    TimingReason.EXISTING_EXIT_STATE
                )

            if existing_invalidation:
                reasons.append(
                    TimingReason.EXISTING_INVALIDATION
                )

        else:
            reasons.append(
                TimingReason.FOLLOW_WINDOW
            )

            reasons.append(
                TimingReason.NO_AUTOMATIC_EXIT
            )

        reasons.append(
            TimingReason.TIMING_COMPLETE
        )

        # ------------------------------------------------------------------
        # Provenance.
        # ------------------------------------------------------------------

        provenance = {
            **dict(decision.provenance),

            "engine": "DecisionTimingEngine",
            "engine_version": self.VERSION,

            "decision_authority": "D13",

            "new_decision_created": False,
            "d13_decision_modified": False,

            "future_outcome_observed": False,

            "primary_window_is_operating_window": True,

            "window_end_is_not_automatic_exit": True,

            "timing_is_management_context": True,

            "cycle_start": cycle_start.isoformat(),
            "cycle_end": cycle_end.isoformat(),
        }

        return DecisionTimingResult(
            decision_id=decision.decision_id,
            market_id=decision.market_id,

            action=decision.action,

            primary_timeframe=resolved.primary_timeframe,

            cycle_start=cycle_start,
            cycle_end=cycle_end,

            as_of=now,

            elapsed_seconds=elapsed_seconds,
            remaining_seconds=remaining_seconds,

            elapsed_fraction=elapsed_fraction,
            remaining_fraction=remaining_fraction,

            window_active=window_active,

            reassessment_due=reassessment_due,

            next_reassessment_at=next_reassessment_at,

            phase=phase,
            status=status,

            context_timeframes=resolved.context_timeframes,

            confirmation_timeframes=(
                resolved.confirmation_timeframes
            ),

            exit_required=exit_required,

            reasons=tuple(reasons),

            provenance=provenance,
        )

    # ========================================================================
    # WINDOW RESOLUTION
    # ========================================================================

    def _resolve_window(
        self,
        decision: D13DecisionSnapshot,
        window: Optional[TimingWindowContract],
    ) -> TimingWindowContract:

        if window is not None:

            if (
                window.primary_timeframe
                != decision.primary_timeframe
            ):
                raise ValueError(
                    "window primary timeframe does not match D13"
                )

            return window

        timeframe = decision.primary_timeframe

        duration = self.TIMEFRAME_SECONDS.get(
            timeframe
        )

        if duration is None:
            raise ValueError(
                f"Unknown timeframe: {timeframe}"
            )

        context = self.DEFAULT_CONTEXT.get(
            timeframe,
            tuple(),
        )

        confirmation = self.DEFAULT_CONFIRMATION.get(
            timeframe,
            tuple(),
        )

        return TimingWindowContract(
            primary_timeframe=timeframe,

            duration_seconds=duration,

            context_timeframes=context,

            confirmation_timeframes=confirmation,

            reassessment_seconds=duration,
        )

    # ========================================================================
    # REASSESSMENT
    # ========================================================================

    @staticmethod
    def _is_reassessment_due(
        *,
        cycle_start: datetime,
        now: datetime,
        contract: TimingWindowContract,
    ) -> bool:

        interval = contract.reassessment_seconds

        if interval is None:
            return False

        elapsed = (
            now - cycle_start
        ).total_seconds()

        if elapsed <= 0:
            return False

        return elapsed >= interval

    # ========================================================================
    # NEXT REASSESSMENT
    # ========================================================================

    @staticmethod
    def _next_reassessment(
        *,
        cycle_start: datetime,
        cycle_end: datetime,
        now: datetime,
        contract: TimingWindowContract,
    ) -> Optional[datetime]:

        interval = contract.reassessment_seconds

        if interval is None:
            return cycle_end

        if now >= cycle_end:
            return None

        elapsed = (
            now - cycle_start
        ).total_seconds()

        if elapsed < 0:
            return cycle_start + timedelta(
                seconds=interval
            )

        completed_cycles = int(
            elapsed // interval
        )

        candidate = (
            cycle_start
            + timedelta(
                seconds=(
                    completed_cycles + 1
                ) * interval
            )
        )

        if candidate >= cycle_end:
            return cycle_end

        return candidate

    # ========================================================================
    # BLOCKED RESULT
    # ========================================================================

    def _blocked_result(
        self,
        *,
        decision: D13DecisionSnapshot,
        as_of: datetime,
        reason: TimingReason,
    ) -> DecisionTimingResult:

        start = decision.decision_timestamp.astimezone(
            timezone.utc
        )

        # Safe placeholder values for invalid timing state.
        end = start

        return DecisionTimingResult(
            decision_id=decision.decision_id,
            market_id=decision.market_id,

            action=decision.action,

            primary_timeframe=decision.primary_timeframe,

            cycle_start=start,
            cycle_end=end,

            as_of=as_of,

            elapsed_seconds=0.0,
            remaining_seconds=0.0,

            elapsed_fraction=0.0,
            remaining_fraction=0.0,

            window_active=False,

            reassessment_due=False,

            next_reassessment_at=None,

            phase=TimingPhase.BLOCKED,

            status=TimingStatus.BLOCKED,

            context_timeframes=tuple(),
            confirmation_timeframes=tuple(),

            exit_required=False,

            reasons=(
                reason,
            ),

            provenance={
                **dict(decision.provenance),

                "engine": "DecisionTimingEngine",
                "engine_version": self.VERSION,

                "decision_authority": "D13",

                "new_decision_created": False,
                "d13_decision_modified": False,

                "future_outcome_observed": False,
            },
        )


# ============================================================================
# SELF TEST HELPERS
# ============================================================================

def _make_decision(
    *,
    decision_id: str,
    market_id: str,
    action: DecisionAction,
    timestamp: datetime,
    timeframe: str,
) -> D13DecisionSnapshot:

    return D13DecisionSnapshot(
        decision_id=decision_id,
        market_id=market_id,

        action=action,

        decision_timestamp=timestamp,

        primary_timeframe=timeframe,

        scenario="CONTINUATION",
        horizon=timeframe,

        provenance={
            "future_outcome_observed": False,
            "validated_by_D14": False,
        },
    )


# ============================================================================
# SELF TEST 1
# ============================================================================

def _test_active_window() -> None:

    base = datetime(
        2026,
        9,
        5,
        0,
        0,
        0,
        tzinfo=timezone.utc,
    )

    decision = _make_decision(
        decision_id="D13-NIFTY-TIME-001",
        market_id="NSE:NIFTY:INDEX",
        action=DecisionAction.BUY,
        timestamp=base,
        timeframe="5m",
    )

    result = DecisionTimingEngine().evaluate(
        decision,
        as_of=base + timedelta(
            seconds=120
        ),
    )

    assert result.status == TimingStatus.ACTIVE
    assert result.phase == TimingPhase.ACTIVE

    assert result.window_active is True

    assert result.elapsed_seconds == 120.0
    assert result.remaining_seconds == 180.0

    assert result.action == DecisionAction.BUY

    assert result.primary_timeframe == "5m"

    assert result.exit_required is False


# ============================================================================
# SELF TEST 2
# ============================================================================

def _test_window_end_does_not_exit() -> None:

    base = datetime(
        2026,
        9,
        5,
        0,
        0,
        0,
        tzinfo=timezone.utc,
    )

    decision = _make_decision(
        decision_id="D13-GOLD-TIME-001",
        market_id="COMEX:GOLD:FUTURE",
        action=DecisionAction.SELL,
        timestamp=base,
        timeframe="5m",
    )

    result = DecisionTimingEngine().evaluate(
        decision,
        as_of=base + timedelta(
            seconds=300
        ),
    )

    assert result.phase == TimingPhase.WINDOW_ENDED

    assert result.status == TimingStatus.ENDED

    assert result.window_active is False

    assert result.reassessment_due is True

    # Critical architectural rule:
    # window end != automatic exit.
    assert result.exit_required is False

    assert (
        TimingReason.NO_AUTOMATIC_EXIT
        in result.reasons
    )


# ============================================================================
# SELF TEST 3
# ============================================================================

def _test_elapsed_remaining() -> None:

    base = datetime(
        2026,
        9,
        5,
        0,
        0,
        0,
        tzinfo=timezone.utc,
    )

    decision = _make_decision(
        decision_id="D13-BTC-TIME-001",
        market_id="BINANCE:BTC/USDT:SPOT",
        action=DecisionAction.BUY,
        timestamp=base,
        timeframe="15m",
    )

    result = DecisionTimingEngine().evaluate(
        decision,
        as_of=base + timedelta(
            seconds=450
        ),
    )

    assert result.elapsed_seconds == 450.0
    assert result.remaining_seconds == 450.0

    assert result.elapsed_fraction == 0.5
    assert result.remaining_fraction == 0.5


# ============================================================================
# SELF TEST 4
# ============================================================================

def _test_context_and_confirmation() -> None:

    base = datetime(
        2026,
        9,
        5,
        0,
        0,
        0,
        tzinfo=timezone.utc,
    )

    decision = _make_decision(
        decision_id="D13-NIFTY-MTF-001",
        market_id="NSE:NIFTY:INDEX",
        action=DecisionAction.BUY,
        timestamp=base,
        timeframe="5m",
    )

    result = DecisionTimingEngine().evaluate(
        decision,
        as_of=base + timedelta(
            seconds=60
        ),
    )

    assert result.primary_timeframe == "5m"

    assert "15m" in result.context_timeframes
    assert "1h" in result.context_timeframes

    assert "1m" in result.confirmation_timeframes
    assert "3m" in result.confirmation_timeframes


# ============================================================================
# SELF TEST 5
# ============================================================================

def _test_existing_exit_state() -> None:

    base = datetime(
        2026,
        9,
        5,
        0,
        0,
        0,
        tzinfo=timezone.utc,
    )

    decision = _make_decision(
        decision_id="D13-FX-EXIT-001",
        market_id="FX:EUR/USD:SPOT",
        action=DecisionAction.SELL,
        timestamp=base,
        timeframe="5m",
    )

    state = DecisionStateSnapshot(
        decision_id=decision.decision_id,
        market_id=decision.market_id,

        state="EXIT",

        invalidation_triggered=False,
        exit_required=True,

        as_of=base + timedelta(
            seconds=120
        ),
    )

    result = DecisionTimingEngine().evaluate(
        decision,
        as_of=base + timedelta(
            seconds=180
        ),
        state=state,
    )

    assert result.exit_required is True

    assert result.phase == TimingPhase.EXIT_CONTEXT

    assert (
        TimingReason.EXISTING_EXIT_STATE
        in result.reasons
    )


# ============================================================================
# SELF TEST 6
# ============================================================================

def _test_invalidation_state() -> None:

    base = datetime(
        2026,
        9,
        5,
        0,
        0,
        0,
        tzinfo=timezone.utc,
    )

    decision = _make_decision(
        decision_id="D13-BTC-INVALID-001",
        market_id="BINANCE:BTC/USDT:SPOT",
        action=DecisionAction.BUY,
        timestamp=base,
        timeframe="5m",
    )

    state = DecisionStateSnapshot(
        decision_id=decision.decision_id,
        market_id=decision.market_id,

        state="INVALIDATED",

        invalidation_triggered=True,
        exit_required=False,

        as_of=base + timedelta(
            seconds=60
        ),
    )

    result = DecisionTimingEngine().evaluate(
        decision,
        as_of=base + timedelta(
            seconds=120
        ),
        state=state,
    )

    assert result.exit_required is True

    assert (
        TimingReason.EXISTING_INVALIDATION
        in result.reasons
    )


# ============================================================================
# SELF TEST 7
# ============================================================================

def _test_future_data_block() -> None:

    base = datetime(
        2026,
        9,
        5,
        0,
        0,
        0,
        tzinfo=timezone.utc,
    )

    decision = _make_decision(
        decision_id="D13-FUTURE-001",
        market_id="NSE:NIFTY:INDEX",
        action=DecisionAction.BUY,
        timestamp=base + timedelta(
            seconds=60
        ),
        timeframe="5m",
    )

    result = DecisionTimingEngine().evaluate(
        decision,
        as_of=base,
    )

    assert result.status == TimingStatus.BLOCKED
    assert result.phase == TimingPhase.BLOCKED

    assert (
        TimingReason.FUTURE_DATA
        in result.reasons
    )


# ============================================================================
# SELF TEST 8
# ============================================================================

def _test_identity_isolation() -> None:

    base = datetime(
        2026,
        9,
        5,
        0,
        0,
        0,
        tzinfo=timezone.utc,
    )

    decision = _make_decision(
        decision_id="D13-NIFTY-ID-001",
        market_id="NSE:NIFTY:INDEX",
        action=DecisionAction.BUY,
        timestamp=base,
        timeframe="5m",
    )

    wrong_state = DecisionStateSnapshot(
        decision_id=decision.decision_id,
        market_id="COMEX:GOLD:FUTURE",

        state="ACTIVE",

        as_of=base + timedelta(
            seconds=60
        ),
    )

    result = DecisionTimingEngine().evaluate(
        decision,
        as_of=base + timedelta(
            seconds=120
        ),
        state=wrong_state,
    )

    assert result.status == TimingStatus.BLOCKED

    assert (
        TimingReason.IDENTITY_ERROR
        in result.reasons
    )


# ============================================================================
# SELF TEST 9
# ============================================================================

def _test_custom_primary_window() -> None:

    base = datetime(
        2026,
        9,
        5,
        0,
        0,
        0,
        tzinfo=timezone.utc,
    )

    decision = _make_decision(
        decision_id="D13-CUSTOM-001",
        market_id="CUSTOM:ASSET:FUTURE",
        action=DecisionAction.BUY,
        timestamp=base,
        timeframe="5m",
    )

    contract = TimingWindowContract(
        primary_timeframe="5m",

        duration_seconds=600.0,

        context_timeframes=(
            "15m",
            "1h",
        ),

        confirmation_timeframes=(
            "1m",
        ),

        reassessment_seconds=300.0,
    )

    result = DecisionTimingEngine().evaluate(
        decision,
        as_of=base + timedelta(
            seconds=350
        ),
        window=contract,
    )

    assert result.elapsed_seconds == 350.0

    assert result.remaining_seconds == 250.0

    assert result.reassessment_due is True

    assert result.primary_timeframe == "5m"

    assert result.context_timeframes == (
        "15m",
        "1h",
    )

    assert result.confirmation_timeframes == (
        "1m",
    )


# ============================================================================
# SELF TEST 10
# ============================================================================

def _test_d13_immutability() -> None:

    base = datetime(
        2026,
        9,
        5,
        0,
        0,
        0,
        tzinfo=timezone.utc,
    )

    decision = _make_decision(
        decision_id="D13-IMMUTABLE-001",
        market_id="NSE:NIFTY:INDEX",
        action=DecisionAction.BUY,
        timestamp=base,
        timeframe="5m",
    )

    original_action = decision.action
    original_market = decision.market_id
    original_timeframe = decision.primary_timeframe

    DecisionTimingEngine().evaluate(
        decision,
        as_of=base + timedelta(
            seconds=100
        ),
    )

    assert decision.action == original_action
    assert decision.market_id == original_market
    assert (
        decision.primary_timeframe
        == original_timeframe
    )


# ============================================================================
# SELF TEST 11
# ============================================================================

def _test_no_direction_creation() -> None:

    base = datetime(
        2026,
        9,
        5,
        0,
        0,
        0,
        tzinfo=timezone.utc,
    )

    decision = _make_decision(
        decision_id="D13-NO-DIRECTION-001",
        market_id="COMEX:GOLD:FUTURE",
        action=DecisionAction.SELL,
        timestamp=base,
        timeframe="1h",
    )

    result = DecisionTimingEngine().evaluate(
        decision,
        as_of=base + timedelta(
            seconds=600
        ),
    )

    assert result.action == DecisionAction.SELL

    assert result.action != DecisionAction.BUY

    assert result.action != DecisionAction.HOLD

    assert (
        result.provenance[
            "new_decision_created"
        ]
        is False
    )

    assert (
        result.provenance[
            "d13_decision_modified"
        ]
        is False
    )


# ============================================================================
# SELF TEST 12
# ============================================================================

def _test_future_outcome_provenance_block() -> None:

    base = datetime(
        2026,
        9,
        5,
        0,
        0,
        0,
        tzinfo=timezone.utc,
    )

    decision = D13DecisionSnapshot(
        decision_id="D13-TAINTED-001",
        market_id="NSE:NIFTY:INDEX",
        action=DecisionAction.BUY,
        decision_timestamp=base,
        primary_timeframe="5m",

        provenance={
            "future_outcome_observed": True,
        },
    )

    result = DecisionTimingEngine().evaluate(
        decision,
        as_of=base + timedelta(
            seconds=60
        ),
    )

    assert result.status == TimingStatus.BLOCKED

    assert (
        TimingReason.FUTURE_DATA
        in result.reasons
    )


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_self_test() -> None:

    _test_active_window()
    _test_window_end_does_not_exit()
    _test_elapsed_remaining()
    _test_context_and_confirmation()
    _test_existing_exit_state()
    _test_invalidation_state()
    _test_future_data_block()
    _test_identity_isolation()
    _test_custom_primary_window()
    _test_d13_immutability()
    _test_no_direction_creation()
    _test_future_outcome_provenance_block()

    print("DECISION TIMING SELF-TEST: PASS")


if __name__ == "__main__":
    run_self_test()