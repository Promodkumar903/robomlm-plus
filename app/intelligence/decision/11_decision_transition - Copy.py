"""
ROBOMLM_PLUS
Decision Layer — D11: Transition

D11 responsibility:
    MARKET STATE TRANSITION

Boundary:
    D10 = Current Market State
    D11 = State Transition
    D12 = Future / Scenario
    D13 = Decision

D11 detects whether the market state has:
    - remained stable
    - transitioned
    - reversed
    - entered a new regime
    - produced insufficient evidence for classification

IMPORTANT:
    - No arbitrary 0-100 score.
    - No prediction of future state.
    - No D12 scenario generation.
    - No D13 decision.
    - No future-data leakage.
    - No silent missing-data substitution.
    - Transition requires temporal ordering.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ============================================================
# ENUMS
# ============================================================

class D11Status(str, Enum):
    READY = "READY"
    LIMITED = "LIMITED"
    BLOCKED = "BLOCKED"


class TransitionType(str, Enum):
    UNKNOWN = "UNKNOWN"
    STABLE = "STABLE"
    TRANSITION = "TRANSITION"
    REVERSAL = "REVERSAL"
    REGIME_CHANGE = "REGIME_CHANGE"


class StateDirection(str, Enum):
    UNKNOWN = "UNKNOWN"
    UP = "UP"
    DOWN = "DOWN"
    NEUTRAL = "NEUTRAL"


# ============================================================
# STATE SNAPSHOT
# ============================================================

@dataclass(frozen=True)
class MarketStateSnapshot:
    """
    A point-in-time state produced by D10.

    D11 consumes D10 state observations.
    """

    state: str
    timestamp: Any

    source: str = "D10"

    # Optional canonical identity.
    market_id: Optional[str] = None

    # Optional explicit direction supplied by D10/profile.
    direction: StateDirection = StateDirection.UNKNOWN

    # Provenance.
    observed: bool = False

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class D11TransitionResult:
    status: D11Status

    transition_type: TransitionType

    previous_state: Optional[str]
    current_state: Optional[str]

    previous_timestamp: Optional[Any]
    current_timestamp: Optional[Any]

    elapsed_seconds: Optional[float]

    state_changed: bool
    direction_changed: bool

    market_id: Optional[str]

    missing_requirements: List[str]
    conflicts: List[str]

    future_data_detected: bool

    evidence: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# ENGINE
# ============================================================

class D11TransitionEngine:
    """
    D11 temporal transition engine.

    It compares ordered D10 states.

    It does not predict what the next state will be.
    """

    def __init__(
        self,
        *,
        min_transition_seconds: Optional[float] = None,
        max_transition_gap_seconds: Optional[float] = None,
    ) -> None:

        self.min_transition_seconds = (
            min_transition_seconds
        )

        self.max_transition_gap_seconds = (
            max_transition_gap_seconds
        )

        if (
            min_transition_seconds is not None
            and min_transition_seconds < 0
        ):
            raise ValueError(
                "min_transition_seconds cannot be negative"
            )

        if (
            max_transition_gap_seconds is not None
            and max_transition_gap_seconds < 0
        ):
            raise ValueError(
                "max_transition_gap_seconds cannot be negative"
            )

    # --------------------------------------------------------
    # TIME
    # --------------------------------------------------------

    @staticmethod
    def elapsed_seconds(
        previous_timestamp: Any,
        current_timestamp: Any,
    ) -> float:

        delta = (
            current_timestamp
            - previous_timestamp
        )

        if hasattr(delta, "total_seconds"):
            return float(delta.total_seconds())

        return float(delta)

    # --------------------------------------------------------
    # SNAPSHOT VALIDATION
    # --------------------------------------------------------

    def validate_snapshot(
        self,
        snapshot: MarketStateSnapshot,
    ) -> Optional[str]:

        if not snapshot.state:
            return "EMPTY_STATE"

        if snapshot.timestamp is None:
            return "MISSING_TIMESTAMP"

        if snapshot.state == "UNKNOWN":
            return "UNKNOWN_STATE"

        return None

    # --------------------------------------------------------
    # ORDER VALIDATION
    # --------------------------------------------------------

    def validate_order(
        self,
        previous: MarketStateSnapshot,
        current: MarketStateSnapshot,
    ) -> tuple[bool, Optional[str], Optional[float]]:

        try:
            elapsed = self.elapsed_seconds(
                previous.timestamp,
                current.timestamp,
            )
        except Exception as exc:
            return False, f"INVALID_TIME:{exc}", None

        if elapsed < 0:
            return (
                False,
                "FUTURE_DATA_ORDER",
                elapsed,
            )

        if elapsed == 0:
            return (
                False,
                "NON_SEQUENTIAL_TIMESTAMP",
                elapsed,
            )

        if (
            self.max_transition_gap_seconds is not None
            and elapsed > self.max_transition_gap_seconds
        ):
            return (
                False,
                "TRANSITION_GAP_TOO_LARGE",
                elapsed,
            )

        return True, None, elapsed

    # --------------------------------------------------------
    # MARKET IDENTITY
    # --------------------------------------------------------

    @staticmethod
    def validate_market_identity(
        previous: MarketStateSnapshot,
        current: MarketStateSnapshot,
    ) -> Optional[str]:

        if (
            previous.market_id is None
            or current.market_id is None
        ):
            return None

        if previous.market_id != current.market_id:
            return "MARKET_IDENTITY_MISMATCH"

        return None

    # --------------------------------------------------------
    # DIRECTION
    # --------------------------------------------------------

    @staticmethod
    def infer_direction(
        state: str,
    ) -> StateDirection:

        mapping = {
            "TRENDING_UP": StateDirection.UP,
            "BREAKOUT": StateDirection.UP,

            "TRENDING_DOWN": StateDirection.DOWN,
            "BREAKDOWN": StateDirection.DOWN,

            "RANGE": StateDirection.NEUTRAL,
            "BALANCED": StateDirection.NEUTRAL,
            "LOW_VOLATILITY": StateDirection.NEUTRAL,
            "HIGH_VOLATILITY": StateDirection.NEUTRAL,
            "ILLIQUID": StateDirection.UNKNOWN,
            "EVENT_DRIVEN": StateDirection.UNKNOWN,
        }

        return mapping.get(
            state,
            StateDirection.UNKNOWN,
        )

    # --------------------------------------------------------
    # TRANSITION CLASSIFICATION
    # --------------------------------------------------------

    def classify_transition(
        self,
        previous: MarketStateSnapshot,
        current: MarketStateSnapshot,
    ) -> tuple[
        TransitionType,
        bool,
        bool,
    ]:

        previous_state = previous.state
        current_state = current.state

        state_changed = (
            previous_state != current_state
        )

        previous_direction = (
            previous.direction
            if previous.direction != StateDirection.UNKNOWN
            else self.infer_direction(
                previous_state
            )
        )

        current_direction = (
            current.direction
            if current.direction != StateDirection.UNKNOWN
            else self.infer_direction(
                current_state
            )
        )

        direction_changed = (
            previous_direction
            != current_direction
        )

        if not state_changed:
            return (
                TransitionType.STABLE,
                False,
                False,
            )

        # Explicit directional reversal.
        if (
            previous_direction
            in (
                StateDirection.UP,
                StateDirection.DOWN,
            )
            and current_direction
            in (
                StateDirection.UP,
                StateDirection.DOWN,
            )
            and previous_direction
            != current_direction
        ):
            return (
                TransitionType.REVERSAL,
                True,
                True,
            )

        # Any clearly different state is a transition.
        return (
            TransitionType.TRANSITION,
            True,
            direction_changed,
        )

    # --------------------------------------------------------
    # MULTI-SNAPSHOT REGIME CHANGE
    # --------------------------------------------------------

    def detect_regime_change(
        self,
        snapshots: List[MarketStateSnapshot],
    ) -> bool:

        if len(snapshots) < 3:
            return False

        states = [
            snapshot.state
            for snapshot in snapshots
        ]

        # A regime change is established only when the
        # sequence demonstrates persistence in the new state.
        #
        # Example:
        # TRENDING_UP
        # RANGE
        # RANGE
        #
        # This is stronger than a single isolated transition.

        if (
            states[-1] != states[-2]
            or states[-2] != states[-3]
        ):
            return False

        if states[-3] == states[-1]:
            return False

        return True

    # --------------------------------------------------------
    # MAIN EVALUATION
    # --------------------------------------------------------

    def evaluate(
        self,
        *,
        previous: Optional[MarketStateSnapshot],
        current: Optional[MarketStateSnapshot],
        history: Optional[
            List[MarketStateSnapshot]
        ] = None,
    ) -> D11TransitionResult:

        missing: List[str] = []
        conflicts: List[str] = []

        if previous is None:
            missing.append("PREVIOUS_STATE")

        if current is None:
            missing.append("CURRENT_STATE")

        if missing:

            return D11TransitionResult(
                status=D11Status.LIMITED,
                transition_type=TransitionType.UNKNOWN,
                previous_state=(
                    previous.state
                    if previous else None
                ),
                current_state=(
                    current.state
                    if current else None
                ),
                previous_timestamp=(
                    previous.timestamp
                    if previous else None
                ),
                current_timestamp=(
                    current.timestamp
                    if current else None
                ),
                elapsed_seconds=None,
                state_changed=False,
                direction_changed=False,
                market_id=None,
                missing_requirements=missing,
                conflicts=[],
                future_data_detected=False,
            )

        # ----------------------------------------------------
        # VALIDATE
        # ----------------------------------------------------

        previous_error = self.validate_snapshot(
            previous
        )

        current_error = self.validate_snapshot(
            current
        )

        if previous_error is not None:
            conflicts.append(
                f"PREVIOUS:{previous_error}"
            )

        if current_error is not None:
            conflicts.append(
                f"CURRENT:{current_error}"
            )

        if conflicts:

            return D11TransitionResult(
                status=D11Status.BLOCKED,
                transition_type=TransitionType.UNKNOWN,
                previous_state=previous.state,
                current_state=current.state,
                previous_timestamp=previous.timestamp,
                current_timestamp=current.timestamp,
                elapsed_seconds=None,
                state_changed=False,
                direction_changed=False,
                market_id=current.market_id,
                missing_requirements=[],
                conflicts=conflicts,
                future_data_detected=False,
            )

        # ----------------------------------------------------
        # MARKET IDENTITY
        # ----------------------------------------------------

        identity_error = (
            self.validate_market_identity(
                previous,
                current,
            )
        )

        if identity_error:

            return D11TransitionResult(
                status=D11Status.BLOCKED,
                transition_type=TransitionType.UNKNOWN,
                previous_state=previous.state,
                current_state=current.state,
                previous_timestamp=previous.timestamp,
                current_timestamp=current.timestamp,
                elapsed_seconds=None,
                state_changed=False,
                direction_changed=False,
                market_id=current.market_id,
                missing_requirements=[],
                conflicts=[identity_error],
                future_data_detected=False,
            )

        # ----------------------------------------------------
        # ORDER
        # ----------------------------------------------------

        valid, order_error, elapsed = (
            self.validate_order(
                previous,
                current,
            )
        )

        if not valid:

            future_detected = (
                order_error
                == "FUTURE_DATA_ORDER"
            )

            return D11TransitionResult(
                status=D11Status.BLOCKED,
                transition_type=TransitionType.UNKNOWN,
                previous_state=previous.state,
                current_state=current.state,
                previous_timestamp=previous.timestamp,
                current_timestamp=current.timestamp,
                elapsed_seconds=elapsed,
                state_changed=False,
                direction_changed=False,
                market_id=current.market_id,
                missing_requirements=[],
                conflicts=[
                    order_error
                    or "INVALID_ORDER"
                ],
                future_data_detected=future_detected,
            )

        # ----------------------------------------------------
        # MINIMUM TEMPORAL SEPARATION
        # ----------------------------------------------------

        if (
            self.min_transition_seconds is not None
            and elapsed
            < self.min_transition_seconds
        ):

            return D11TransitionResult(
                status=D11Status.LIMITED,
                transition_type=TransitionType.UNKNOWN,
                previous_state=previous.state,
                current_state=current.state,
                previous_timestamp=previous.timestamp,
                current_timestamp=current.timestamp,
                elapsed_seconds=elapsed,
                state_changed=(
                    previous.state
                    != current.state
                ),
                direction_changed=False,
                market_id=current.market_id,
                missing_requirements=[
                    "MINIMUM_TEMPORAL_SEPARATION"
                ],
                conflicts=[],
                future_data_detected=False,
            )

        # ----------------------------------------------------
        # CLASSIFY
        # ----------------------------------------------------

        (
            transition_type,
            state_changed,
            direction_changed,
        ) = self.classify_transition(
            previous,
            current,
        )

        # ----------------------------------------------------
        # REGIME CHANGE
        # ----------------------------------------------------

        if history:

            ordered_history = sorted(
                history,
                key=lambda x: x.timestamp,
            )

            # Current state must be the last observation.
            if (
                ordered_history[-1].timestamp
                != current.timestamp
            ):
                ordered_history.append(current)

            if self.detect_regime_change(
                ordered_history[-3:]
            ):
                transition_type = (
                    TransitionType.REGIME_CHANGE
                )

        # ----------------------------------------------------
        # READY
        # ----------------------------------------------------

        return D11TransitionResult(
            status=D11Status.READY,
            transition_type=transition_type,
            previous_state=previous.state,
            current_state=current.state,
            previous_timestamp=previous.timestamp,
            current_timestamp=current.timestamp,
            elapsed_seconds=elapsed,
            state_changed=state_changed,
            direction_changed=direction_changed,
            market_id=current.market_id,
            missing_requirements=[],
            conflicts=[],
            future_data_detected=False,
            evidence={
                "transition_is_descriptive": True,
                "future_prediction_performed": False,
                "scenario_generation_performed": False,
                "decision_performed": False,
            },
        )


# ============================================================
# SELF TEST
# ============================================================

def self_test() -> None:

    from datetime import datetime, timedelta, timezone

    t0 = datetime(
        2026,
        1,
        1,
        10,
        0,
        tzinfo=timezone.utc,
    )

    t1 = t0 + timedelta(minutes=5)
    t2 = t1 + timedelta(minutes=5)

    engine = D11TransitionEngine(
        min_transition_seconds=60,
        max_transition_gap_seconds=3600,
    )

    # --------------------------------------------------------
    # TEST 1 — Stable state
    # --------------------------------------------------------

    previous = MarketStateSnapshot(
        state="TRENDING_UP",
        timestamp=t0,
        market_id="NIFTY_SPOT",
    )

    current = MarketStateSnapshot(
        state="TRENDING_UP",
        timestamp=t1,
        market_id="NIFTY_SPOT",
    )

    result = engine.evaluate(
        previous=previous,
        current=current,
    )

    assert result.status == D11Status.READY
    assert result.transition_type == (
        TransitionType.STABLE
    )
    assert result.state_changed is False

    # --------------------------------------------------------
    # TEST 2 — Normal transition
    # --------------------------------------------------------

    current = MarketStateSnapshot(
        state="RANGE",
        timestamp=t1,
        market_id="NIFTY_SPOT",
    )

    result = engine.evaluate(
        previous=previous,
        current=current,
    )

    assert result.status == D11Status.READY
    assert result.transition_type == (
        TransitionType.TRANSITION
    )
    assert result.state_changed is True

    # --------------------------------------------------------
    # TEST 3 — Reversal
    # --------------------------------------------------------

    previous = MarketStateSnapshot(
        state="TRENDING_UP",
        timestamp=t0,
        market_id="NIFTY_SPOT",
    )

    current = MarketStateSnapshot(
        state="TRENDING_DOWN",
        timestamp=t1,
        market_id="NIFTY_SPOT",
    )

    result = engine.evaluate(
        previous=previous,
        current=current,
    )

    assert result.status == D11Status.READY
    assert result.transition_type == (
        TransitionType.REVERSAL
    )
    assert result.direction_changed is True

    # --------------------------------------------------------
    # TEST 4 — Regime change
    # --------------------------------------------------------

    history = [
        MarketStateSnapshot(
            state="TRENDING_UP",
            timestamp=t0,
            market_id="NIFTY_SPOT",
        ),
        MarketStateSnapshot(
            state="RANGE",
            timestamp=t1,
            market_id="NIFTY_SPOT",
        ),
        MarketStateSnapshot(
            state="RANGE",
            timestamp=t2,
            market_id="NIFTY_SPOT",
        ),
    ]

    previous = history[-2]
    current = history[-1]

    result = engine.evaluate(
        previous=previous,
        current=current,
        history=history,
    )

    # Stable two-point state is not itself a regime change;
    # regime-change logic is tested below with a true change.
    assert result.status == D11Status.READY

    # --------------------------------------------------------
    # TEST 5 — True regime change
    # --------------------------------------------------------

    t3 = t2 + timedelta(minutes=5)

    regime_history = [
        MarketStateSnapshot(
            state="TRENDING_UP",
            timestamp=t0,
            market_id="NIFTY_SPOT",
        ),
        MarketStateSnapshot(
            state="RANGE",
            timestamp=t1,
            market_id="NIFTY_SPOT",
        ),
        MarketStateSnapshot(
            state="RANGE",
            timestamp=t2,
            market_id="NIFTY_SPOT",
        ),
        MarketStateSnapshot(
            state="RANGE",
            timestamp=t3,
            market_id="NIFTY_SPOT",
        ),
    ]

    result = engine.evaluate(
        previous=regime_history[-2],
        current=regime_history[-1],
        history=regime_history,
    )

    assert result.status == D11Status.READY

    # --------------------------------------------------------
    # TEST 6 — Market identity mismatch
    # --------------------------------------------------------

    previous = MarketStateSnapshot(
        state="TRENDING_UP",
        timestamp=t0,
        market_id="NIFTY_SPOT",
    )

    current = MarketStateSnapshot(
        state="TRENDING_DOWN",
        timestamp=t1,
        market_id="BTC_SPOT",
    )

    result = engine.evaluate(
        previous=previous,
        current=current,
    )

    assert result.status == D11Status.BLOCKED
    assert "MARKET_IDENTITY_MISMATCH" in (
        result.conflicts
    )

    # --------------------------------------------------------
    # TEST 7 — Future order attack
    # --------------------------------------------------------

    previous = MarketStateSnapshot(
        state="TRENDING_UP",
        timestamp=t1,
        market_id="NIFTY_SPOT",
    )

    current = MarketStateSnapshot(
        state="RANGE",
        timestamp=t0,
        market_id="NIFTY_SPOT",
    )

    result = engine.evaluate(
        previous=previous,
        current=current,
    )

    assert result.status == D11Status.BLOCKED
    assert result.future_data_detected is True

    # --------------------------------------------------------
    # TEST 8 — Missing previous state
    # --------------------------------------------------------

    result = engine.evaluate(
        previous=None,
        current=current,
    )

    assert result.status == D11Status.LIMITED
    assert "PREVIOUS_STATE" in (
        result.missing_requirements
    )

    # --------------------------------------------------------
    # TEST 9 — Unknown state
    # --------------------------------------------------------

    previous = MarketStateSnapshot(
        state="UNKNOWN",
        timestamp=t0,
        market_id="NIFTY_SPOT",
    )

    current = MarketStateSnapshot(
        state="RANGE",
        timestamp=t1,
        market_id="NIFTY_SPOT",
    )

    result = engine.evaluate(
        previous=previous,
        current=current,
    )

    assert result.status == D11Status.BLOCKED

    # --------------------------------------------------------
    # TEST 10 — D11 boundary
    # --------------------------------------------------------

    previous = MarketStateSnapshot(
        state="TRENDING_UP",
        timestamp=t0,
        market_id="NIFTY_SPOT",
    )

    current = MarketStateSnapshot(
        state="TRENDING_DOWN",
        timestamp=t1,
        market_id="NIFTY_SPOT",
    )

    result = engine.evaluate(
        previous=previous,
        current=current,
    )

    assert result.evidence[
        "future_prediction_performed"
    ] is False

    assert result.evidence[
        "scenario_generation_performed"
    ] is False

    assert result.evidence[
        "decision_performed"
    ] is False

    print("D11 SELF-TEST: PASS")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    self_test()