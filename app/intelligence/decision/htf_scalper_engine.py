"""
ROBOMLM_PLUS
HTF / SCALPER ENGINE

Purpose
-------
Specialized short-duration, one-shot trade-management mode.

Architecture
------------
V5 Matrices
    ↓
D1–D12
    ↓
D13  ← ONLY directional decision authority
    ↓
HTF / SCALPER ENGINE
    ↓
ONE SHOT CALL / PUT
    ↓
FOLLOW / CAUTION / EXIT / REASSESS
    ↓
CLOSE
    ↓
Fresh opportunity

Important
---------
This engine DOES NOT create BUY/SELL decisions.

D13 remains the only decision authority.

HTF/SCALPER is an operating/management mode for short-duration
option trades, primarily CALL/PUT.

No universal 0–100 score is used.
No fixed ₹5–₹10 premium rule is used.
No automatic exit merely because the primary time window ends.

Real-market validation must be performed through replay/BlackBox/live
data. The self-test below is only a structural smoke test.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional, Tuple


# ============================================================================
# ENUMS
# ============================================================================

class HTFMode(str, Enum):
    OFF = "OFF"
    ON = "ON"


class OptionSide(str, Enum):
    CE = "CE"
    PE = "PE"


class TradeLifecycle(str, Enum):
    IDLE = "IDLE"
    ELIGIBLE = "ELIGIBLE"
    READY = "READY"
    ACTIVE = "ACTIVE"
    CAUTION = "CAUTION"
    REASSESS = "REASSESS"
    EXIT = "EXIT"
    CLOSED = "CLOSED"
    BLOCKED = "BLOCKED"


class ManagementAction(str, Enum):
    NONE = "NONE"
    FOLLOW = "FOLLOW"
    CAUTION = "CAUTION"
    REASSESS = "REASSESS"
    EXIT = "EXIT"
    BLOCKED = "BLOCKED"


class ExitReason(str, Enum):
    NONE = "NONE"
    PROFIT_CAPTURE = "PROFIT_CAPTURE"
    THESIS_INVALIDATED = "THESIS_INVALIDATED"
    LIQUIDITY_FAILURE = "LIQUIDITY_FAILURE"
    DATA_FAILURE = "DATA_FAILURE"
    TIME_REASSESSMENT = "TIME_REASSESSMENT"
    MANUAL_CLOSE = "MANUAL_CLOSE"
    SESSION_END = "SESSION_END"
    EXTERNAL_RISK_GATE = "EXTERNAL_RISK_GATE"


class DataStatus(str, Enum):
    COMPLETE = "COMPLETE"
    LIMITED = "LIMITED"
    BLOCKED = "BLOCKED"


# ============================================================================
# IDENTITY
# ============================================================================

@dataclass(frozen=True)
class OptionIdentity:
    """
    Canonical option identity.

    Contract identity is deliberately explicit.
    """

    market_id: str
    underlying: str
    instrument: str
    option_side: OptionSide
    strike: float
    expiry: str
    venue: str
    contract_id: str

    def validate(self) -> Tuple[bool, str]:
        if not self.market_id:
            return False, "missing_market_id"

        if not self.underlying:
            return False, "missing_underlying"

        if not self.instrument:
            return False, "missing_instrument"

        if self.option_side not in (OptionSide.CE, OptionSide.PE):
            return False, "invalid_option_side"

        if self.strike <= 0:
            return False, "invalid_strike"

        if not self.expiry:
            return False, "missing_expiry"

        if not self.venue:
            return False, "missing_venue"

        if not self.contract_id:
            return False, "missing_contract_id"

        return True, "identity_valid"


# ============================================================================
# D13 SNAPSHOT
# ============================================================================

@dataclass(frozen=True)
class D13Snapshot:
    """
    Minimal immutable D13 contract consumed by HTF/SCALPER.

    D13 decides direction.

    HTF engine never changes it.
    """

    decision_id: str
    market_id: str
    action: str
    decision_timestamp: datetime
    state: str = "READY"

    # Optional thesis/context fields supplied by the D13 implementation.
    thesis_valid: Optional[bool] = None
    invalidated: bool = False

    future_outcome_observed: bool = False
    validated_by_D14: bool = False
    learned_by_D15: bool = False

    def direction(self) -> Optional[str]:
        action = str(self.action).upper()

        if action == "BUY":
            return "BUY"

        if action == "SELL":
            return "SELL"

        return None


# ============================================================================
# LIVE MARKET SNAPSHOT
# ============================================================================

@dataclass(frozen=True)
class HTFMarketSnapshot:
    """
    Current market/instrument observation.

    Observed values should come from live/replay data.
    No silent defaults are applied.
    """

    timestamp: datetime

    # Underlying
    underlying_price: Optional[float] = None
    underlying_previous_price: Optional[float] = None

    # Option
    option_bid: Optional[float] = None
    option_ask: Optional[float] = None
    option_last: Optional[float] = None

    # Participation / derivatives
    option_volume: Optional[float] = None
    option_oi: Optional[float] = None
    option_iv: Optional[float] = None

    # Optional Greeks
    delta: Optional[float] = None
    gamma: Optional[float] = None
    theta: Optional[float] = None
    vega: Optional[float] = None

    # Depth
    bid_depth: Optional[float] = None
    ask_depth: Optional[float] = None

    # Freshness / provenance
    source_timestamp: Optional[datetime] = None
    future_data: bool = False


# ============================================================================
# POLICY
# ============================================================================

@dataclass(frozen=True)
class HTFPolicy:
    """
    Operating policy.

    These are NOT proprietary V6 universal constants.

    They are explicit configuration controls so calibration can later
    be performed from real market data.
    """

    enabled: bool = False

    # Supported short operating windows.
    allowed_windows_minutes: Tuple[int, ...] = (1, 2, 3, 4, 5)

    # The primary window is selected per shot.
    primary_window_minutes: int = 3

    # Reassessment cadence.
    reassessment_seconds: int = 30

    # Optional user/operator premium universe filter.
    # This does NOT define the trade.
    premium_filter_enabled: bool = False
    premium_min: Optional[float] = None
    premium_max: Optional[float] = None

    # Data freshness policy.
    max_market_age_seconds: Optional[float] = None

    # One-shot enforcement.
    allow_position_stacking: bool = False
    allow_averaging: bool = False
    require_flat_before_new_shot: bool = True

    def validate(self) -> Tuple[bool, str]:
        if self.primary_window_minutes not in self.allowed_windows_minutes:
            return False, "invalid_primary_window"

        if self.reassessment_seconds < 0:
            return False, "invalid_reassessment_seconds"

        if self.premium_filter_enabled:
            if self.premium_min is None or self.premium_max is None:
                return False, "premium_filter_incomplete"

            if self.premium_min < 0 or self.premium_max < 0:
                return False, "invalid_premium_filter"

            if self.premium_min > self.premium_max:
                return False, "premium_filter_range_invalid"

        return True, "policy_valid"


# ============================================================================
# ACTIVE SHOT
# ============================================================================

@dataclass
class HTFShot:
    shot_id: str

    d13_decision_id: str
    market_id: str

    option_identity: OptionIdentity
    d13_direction: str

    entry_timestamp: datetime
    entry_premium: float

    primary_window_minutes: int

    lifecycle: TradeLifecycle = TradeLifecycle.ACTIVE
    management_action: ManagementAction = ManagementAction.FOLLOW

    last_observation_timestamp: Optional[datetime] = None

    peak_premium: Optional[float] = None
    trough_premium: Optional[float] = None

    exit_timestamp: Optional[datetime] = None
    exit_premium: Optional[float] = None

    exit_reason: ExitReason = ExitReason.NONE

    # Prevents accidental multiple entries.
    entry_locked: bool = True
    close_completed: bool = False

    provenance: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# RESULT
# ============================================================================

@dataclass(frozen=True)
class HTFResult:
    mode: HTFMode
    lifecycle: TradeLifecycle
    management_action: ManagementAction

    eligible: bool
    allowed_to_enter: bool

    d13_direction: Optional[str]

    shot_id: Optional[str]
    option_side: Optional[OptionSide]

    option_premium: Optional[float]
    spread: Optional[float]
    spread_bps: Optional[float]

    underlying_return: Optional[float]
    option_return: Optional[float]

    elapsed_seconds: Optional[float]
    remaining_seconds: Optional[float]

    reassessment_due: bool
    exit_required: bool

    exit_reason: ExitReason

    reasons: Tuple[str, ...]

    provenance: Dict[str, Any]


# ============================================================================
# ENGINE
# ============================================================================

class HTFScalperEngine:
    """
    One-shot HTF/Scalper management engine.

    Directional authority:
        D13 only.

    This engine:
        - validates HTF mode
        - validates D13
        - validates option identity
        - validates current data
        - creates one shot
        - monitors the shot
        - computes live instrument response
        - produces management context
        - closes the shot
        - prevents duplicate/stacked entries

    It never creates a new BUY/SELL decision.
    """

    def __init__(self, policy: Optional[HTFPolicy] = None):
        self.policy = policy or HTFPolicy()
        self.active_shot: Optional[HTFShot] = None

    # ----------------------------------------------------------------------
    # MODE
    # ----------------------------------------------------------------------

    def set_mode(self, enabled: bool) -> HTFMode:
        return HTFMode.ON if enabled else HTFMode.OFF

    # ----------------------------------------------------------------------
    # D13 VALIDATION
    # ----------------------------------------------------------------------

    @staticmethod
    def _validate_d13(
        d13: D13Snapshot,
        current_market_id: str,
    ) -> Tuple[bool, str]:

        if d13.future_outcome_observed:
            return False, "future_outcome_observed"

        if d13.market_id != current_market_id:
            return False, "market_identity_mismatch"

        direction = d13.direction()

        if direction not in ("BUY", "SELL"):
            return False, "d13_has_no_directional_decision"

        if d13.invalidated:
            return False, "d13_invalidated"

        return True, "d13_valid"

    # ----------------------------------------------------------------------
    # OPTION VALIDATION
    # ----------------------------------------------------------------------

    @staticmethod
    def _validate_option_identity(
        identity: OptionIdentity,
    ) -> Tuple[bool, str]:

        return identity.validate()

    # ----------------------------------------------------------------------
    # PREMIUM
    # ----------------------------------------------------------------------

    @staticmethod
    def _option_premium(snapshot: HTFMarketSnapshot) -> Optional[float]:

        if snapshot.option_bid is not None and snapshot.option_ask is not None:
            if snapshot.option_bid > 0 and snapshot.option_ask > 0:
                return (snapshot.option_bid + snapshot.option_ask) / 2.0

        if snapshot.option_last is not None and snapshot.option_last > 0:
            return snapshot.option_last

        return None

    # ----------------------------------------------------------------------
    # SPREAD
    # ----------------------------------------------------------------------

    @staticmethod
    def _spread(
        snapshot: HTFMarketSnapshot,
    ) -> Tuple[Optional[float], Optional[float]]:

        bid = snapshot.option_bid
        ask = snapshot.option_ask

        if bid is None or ask is None:
            return None, None

        if bid <= 0 or ask <= 0 or ask < bid:
            return None, None

        spread = ask - bid
        midpoint = (ask + bid) / 2.0

        if midpoint <= 0:
            return spread, None

        spread_bps = (spread / midpoint) * 10_000.0

        return spread, spread_bps

    # ----------------------------------------------------------------------
    # RETURNS
    # ----------------------------------------------------------------------

    @staticmethod
    def _return(
        current: Optional[float],
        previous: Optional[float],
    ) -> Optional[float]:

        if current is None or previous is None:
            return None

        if previous <= 0:
            return None

        return (current / previous) - 1.0

    # ----------------------------------------------------------------------
    # FRESHNESS
    # ----------------------------------------------------------------------

    def _freshness_status(
        self,
        snapshot: HTFMarketSnapshot,
    ) -> Tuple[bool, str]:

        if snapshot.future_data:
            return False, "future_data_detected"

        if self.policy.max_market_age_seconds is None:
            return True, "freshness_policy_not_restrictive"

        if snapshot.source_timestamp is None:
            return False, "source_timestamp_missing"

        age = (
            snapshot.timestamp - snapshot.source_timestamp
        ).total_seconds()

        if age < 0:
            return False, "source_timestamp_in_future"

        if age > self.policy.max_market_age_seconds:
            return False, "market_data_stale"

        return True, "market_data_fresh"

    # ----------------------------------------------------------------------
    # PREMIUM FILTER
    # ----------------------------------------------------------------------

    def _premium_filter(
        self,
        premium: Optional[float],
    ) -> Tuple[bool, str]:

        if not self.policy.premium_filter_enabled:
            return True, "premium_filter_disabled"

        if premium is None:
            return False, "premium_required_for_filter"

        if premium < self.policy.premium_min:
            return False, "premium_below_configured_range"

        if premium > self.policy.premium_max:
            return False, "premium_above_configured_range"

        return True, "premium_inside_configured_range"

    # ----------------------------------------------------------------------
    # ENTRY ELIGIBILITY
    # ----------------------------------------------------------------------

    def evaluate_entry(
        self,
        *,
        mode: HTFMode,
        d13: D13Snapshot,
        option_identity: OptionIdentity,
        snapshot: HTFMarketSnapshot,
    ) -> HTFResult:

        reasons = []

        if mode != HTFMode.ON:
            return self._blocked_result(
                "htf_mode_off"
            )

        policy_ok, policy_reason = self.policy.validate()

        if not policy_ok:
            return self._blocked_result(policy_reason)

        if self.active_shot is not None:
            return self._blocked_result(
                "active_shot_already_exists"
            )

        d13_ok, d13_reason = self._validate_d13(
            d13,
            option_identity.market_id,
        )

        if not d13_ok:
            return self._blocked_result(d13_reason)

        identity_ok, identity_reason = self._validate_option_identity(
            option_identity
        )

        if not identity_ok:
            return self._blocked_result(identity_reason)

        fresh_ok, fresh_reason = self._freshness_status(
            snapshot
        )

        if not fresh_ok:
            return self._blocked_result(fresh_reason)

        premium = self._option_premium(snapshot)

        if premium is None:
            return self._blocked_result(
                "option_premium_unavailable"
            )

        premium_ok, premium_reason = self._premium_filter(
            premium
        )

        if not premium_ok:
            return self._blocked_result(premium_reason)

        spread, spread_bps = self._spread(snapshot)

        reasons.extend(
            [
                "htf_mode_enabled",
                "d13_direction_present",
                "option_identity_valid",
                fresh_reason,
                premium_reason,
            ]
        )

        return HTFResult(
            mode=HTFMode.ON,
            lifecycle=TradeLifecycle.READY,
            management_action=ManagementAction.NONE,
            eligible=True,
            allowed_to_enter=True,
            d13_direction=d13.direction(),
            shot_id=None,
            option_side=option_identity.option_side,
            option_premium=premium,
            spread=spread,
            spread_bps=spread_bps,
            underlying_return=self._return(
                snapshot.underlying_price,
                snapshot.underlying_previous_price,
            ),
            option_return=None,
            elapsed_seconds=0.0,
            remaining_seconds=(
                self.policy.primary_window_minutes * 60.0
            ),
            reassessment_due=False,
            exit_required=False,
            exit_reason=ExitReason.NONE,
            reasons=tuple(reasons),
            provenance=self._provenance(
                d13=d13,
                new_decision_created=False,
            ),
        )

    # ----------------------------------------------------------------------
    # OPEN SHOT
    # ----------------------------------------------------------------------

    def open_shot(
        self,
        *,
        shot_id: str,
        mode: HTFMode,
        d13: D13Snapshot,
        option_identity: OptionIdentity,
        snapshot: HTFMarketSnapshot,
    ) -> HTFResult:

        evaluation = self.evaluate_entry(
            mode=mode,
            d13=d13,
            option_identity=option_identity,
            snapshot=snapshot,
        )

        if not evaluation.allowed_to_enter:
            return evaluation

        premium = evaluation.option_premium

        if premium is None:
            return self._blocked_result(
                "entry_premium_missing"
            )

        self.active_shot = HTFShot(
            shot_id=shot_id,
            d13_decision_id=d13.decision_id,
            market_id=option_identity.market_id,
            option_identity=option_identity,
            d13_direction=d13.direction(),
            entry_timestamp=snapshot.timestamp,
            entry_premium=premium,
            primary_window_minutes=self.policy.primary_window_minutes,
            lifecycle=TradeLifecycle.ACTIVE,
            management_action=ManagementAction.FOLLOW,
            last_observation_timestamp=snapshot.timestamp,
            peak_premium=premium,
            trough_premium=premium,
            provenance=self._provenance(
                d13=d13,
                new_decision_created=False,
            ),
        )

        return self._active_result(
            snapshot=snapshot,
            action=ManagementAction.FOLLOW,
            lifecycle=TradeLifecycle.ACTIVE,
            reasons=("one_shot_opened",),
        )

    # ----------------------------------------------------------------------
    # MONITOR
    # ----------------------------------------------------------------------

    def monitor(
        self,
        *,
        d13: D13Snapshot,
        snapshot: HTFMarketSnapshot,
        explicit_invalidation: bool = False,
        liquidity_failure: bool = False,
        external_risk_block: bool = False,
    ) -> HTFResult:

        shot = self.active_shot

        if shot is None:
            return self._blocked_result(
                "no_active_htf_shot"
            )

        reasons = []

        # --------------------------------------------------------------
        # Identity guard
        # --------------------------------------------------------------

        if d13.market_id != shot.market_id:
            return self._management_result(
                lifecycle=TradeLifecycle.EXIT,
                action=ManagementAction.EXIT,
                reason=ExitReason.EXTERNAL_RISK_GATE,
                text="d13_market_identity_changed",
                snapshot=snapshot,
            )

        # --------------------------------------------------------------
        # Future-data guard
        # --------------------------------------------------------------

        if snapshot.future_data or d13.future_outcome_observed:
            return self._management_result(
                lifecycle=TradeLifecycle.BLOCKED,
                action=ManagementAction.BLOCKED,
                reason=ExitReason.DATA_FAILURE,
                text="future_data_detected",
                snapshot=snapshot,
            )

        # --------------------------------------------------------------
        # Freshness
        # --------------------------------------------------------------

        fresh_ok, fresh_reason = self._freshness_status(snapshot)

        if not fresh_ok:
            return self._management_result(
                lifecycle=TradeLifecycle.CAUTION,
                action=ManagementAction.CAUTION,
                reason=ExitReason.DATA_FAILURE,
                text=fresh_reason,
                snapshot=snapshot,
            )

        # --------------------------------------------------------------
        # Current premium
        # --------------------------------------------------------------

        premium = self._option_premium(snapshot)

        if premium is None:
            return self._management_result(
                lifecycle=TradeLifecycle.CAUTION,
                action=ManagementAction.CAUTION,
                reason=ExitReason.DATA_FAILURE,
                text="current_option_premium_unavailable",
                snapshot=snapshot,
            )

        # --------------------------------------------------------------
        # Update extrema
        # --------------------------------------------------------------

        shot.last_observation_timestamp = snapshot.timestamp

        if shot.peak_premium is None or premium > shot.peak_premium:
            shot.peak_premium = premium

        if shot.trough_premium is None or premium < shot.trough_premium:
            shot.trough_premium = premium

        # --------------------------------------------------------------
        # Explicit invalidation
        # --------------------------------------------------------------

        if explicit_invalidation or d13.invalidated:
            return self._management_result(
                lifecycle=TradeLifecycle.EXIT,
                action=ManagementAction.EXIT,
                reason=ExitReason.THESIS_INVALIDATED,
                text="d13_thesis_invalidated",
                snapshot=snapshot,
            )

        # --------------------------------------------------------------
        # Liquidity failure
        # --------------------------------------------------------------

        if liquidity_failure:
            return self._management_result(
                lifecycle=TradeLifecycle.EXIT,
                action=ManagementAction.EXIT,
                reason=ExitReason.LIQUIDITY_FAILURE,
                text="liquidity_failure",
                snapshot=snapshot,
            )

        # --------------------------------------------------------------
        # External safety/risk gate
        # --------------------------------------------------------------

        if external_risk_block:
            return self._management_result(
                lifecycle=TradeLifecycle.EXIT,
                action=ManagementAction.EXIT,
                reason=ExitReason.EXTERNAL_RISK_GATE,
                text="external_risk_gate",
                snapshot=snapshot,
            )

        # --------------------------------------------------------------
        # Timing
        # --------------------------------------------------------------

        elapsed = (
            snapshot.timestamp - shot.entry_timestamp
        ).total_seconds()

        if elapsed < 0:
            return self._management_result(
                lifecycle=TradeLifecycle.BLOCKED,
                action=ManagementAction.BLOCKED,
                reason=ExitReason.DATA_FAILURE,
                text="observation_before_entry",
                snapshot=snapshot,
            )

        window_seconds = (
            shot.primary_window_minutes * 60.0
        )

        remaining = max(
            0.0,
            window_seconds - elapsed,
        )

        reassessment_due = (
            self.policy.reassessment_seconds > 0
            and elapsed > 0
            and (
                int(elapsed)
                % self.policy.reassessment_seconds
            ) == 0
        )

        # --------------------------------------------------------------
        # Option response
        # --------------------------------------------------------------

        option_return = self._return(
            premium,
            shot.entry_premium,
        )

        # --------------------------------------------------------------
        # Underlying response
        # --------------------------------------------------------------

        underlying_return = self._return(
            snapshot.underlying_price,
            snapshot.underlying_previous_price,
        )

        # --------------------------------------------------------------
        # Spread
        # --------------------------------------------------------------

        spread, spread_bps = self._spread(snapshot)

        # --------------------------------------------------------------
        # Management logic
        #
        # This is NOT a new directional decision.
        # --------------------------------------------------------------

        if option_return is not None and option_return > 0:
            reasons.append(
                "option_response_positive"
            )

        if option_return is not None and option_return < 0:
            reasons.append(
                "option_response_negative"
            )

        if underlying_return is not None:
            reasons.append(
                "underlying_response_observed"
            )

        if spread is not None:
            reasons.append(
                "option_spread_observed"
            )

        # Reassessment is context, not automatic exit.
        if reassessment_due:
            reasons.append("reassessment_due")

        # Window end is NOT automatic exit.
        if remaining <= 0:
            reasons.append(
                "primary_window_completed_reassessment_required"
            )

            return HTFResult(
                mode=HTFMode.ON,
                lifecycle=TradeLifecycle.REASSESS,
                management_action=ManagementAction.REASSESS,
                eligible=True,
                allowed_to_enter=False,
                d13_direction=shot.d13_direction,
                shot_id=shot.shot_id,
                option_side=shot.option_identity.option_side,
                option_premium=premium,
                spread=spread,
                spread_bps=spread_bps,
                underlying_return=underlying_return,
                option_return=option_return,
                elapsed_seconds=elapsed,
                remaining_seconds=0.0,
                reassessment_due=True,
                exit_required=False,
                exit_reason=ExitReason.NONE,
                reasons=tuple(reasons),
                provenance=self._provenance_from_shot(
                    shot
                ),
            )

        # --------------------------------------------------------------
        # Normal active state
        # --------------------------------------------------------------

        shot.lifecycle = TradeLifecycle.ACTIVE
        shot.management_action = ManagementAction.FOLLOW

        return HTFResult(
            mode=HTFMode.ON,
            lifecycle=TradeLifecycle.ACTIVE,
            management_action=ManagementAction.FOLLOW,
            eligible=True,
            allowed_to_enter=False,
            d13_direction=shot.d13_direction,
            shot_id=shot.shot_id,
            option_side=shot.option_identity.option_side,
            option_premium=premium,
            spread=spread,
            spread_bps=spread_bps,
            underlying_return=underlying_return,
            option_return=option_return,
            elapsed_seconds=elapsed,
            remaining_seconds=remaining,
            reassessment_due=reassessment_due,
            exit_required=False,
            exit_reason=ExitReason.NONE,
            reasons=tuple(reasons),
            provenance=self._provenance_from_shot(
                shot
            ),
        )

    # ----------------------------------------------------------------------
    # CLOSE
    # ----------------------------------------------------------------------

    def close_shot(
        self,
        *,
        snapshot: HTFMarketSnapshot,
        reason: ExitReason,
    ) -> HTFResult:

        shot = self.active_shot

        if shot is None:
            return self._blocked_result(
                "no_active_htf_shot"
            )

        premium = self._option_premium(snapshot)

        if premium is None:
            return self._management_result(
                lifecycle=TradeLifecycle.CAUTION,
                action=ManagementAction.CAUTION,
                reason=ExitReason.DATA_FAILURE,
                text="close_price_unavailable",
                snapshot=snapshot,
            )

        shot.exit_timestamp = snapshot.timestamp
        shot.exit_premium = premium
        shot.exit_reason = reason
        shot.lifecycle = TradeLifecycle.CLOSED
        shot.management_action = ManagementAction.EXIT
        shot.close_completed = True

        elapsed = (
            snapshot.timestamp - shot.entry_timestamp
        ).total_seconds()

        option_return = self._return(
            premium,
            shot.entry_premium,
        )

        spread, spread_bps = self._spread(snapshot)

        completed_shot = shot

        # Important:
        # active shot is cleared ONLY after closure.
        self.active_shot = None

        return HTFResult(
            mode=HTFMode.ON,
            lifecycle=TradeLifecycle.CLOSED,
            management_action=ManagementAction.EXIT,
            eligible=False,
            allowed_to_enter=False,
            d13_direction=completed_shot.d13_direction,
            shot_id=completed_shot.shot_id,
            option_side=completed_shot.option_identity.option_side,
            option_premium=premium,
            spread=spread,
            spread_bps=spread_bps,
            underlying_return=self._return(
                snapshot.underlying_price,
                snapshot.underlying_previous_price,
            ),
            option_return=option_return,
            elapsed_seconds=max(0.0, elapsed),
            remaining_seconds=0.0,
            reassessment_due=False,
            exit_required=True,
            exit_reason=reason,
            reasons=("one_shot_closed",),
            provenance=self._provenance_from_shot(
                completed_shot
            ),
        )

    # ----------------------------------------------------------------------
    # BLOCKED RESULT
    # ----------------------------------------------------------------------

    @staticmethod
    def _blocked_result(
        reason: str,
    ) -> HTFResult:

        return HTFResult(
            mode=HTFMode.OFF,
            lifecycle=TradeLifecycle.BLOCKED,
            management_action=ManagementAction.BLOCKED,
            eligible=False,
            allowed_to_enter=False,
            d13_direction=None,
            shot_id=None,
            option_side=None,
            option_premium=None,
            spread=None,
            spread_bps=None,
            underlying_return=None,
            option_return=None,
            elapsed_seconds=None,
            remaining_seconds=None,
            reassessment_due=False,
            exit_required=False,
            exit_reason=ExitReason.NONE,
            reasons=(reason,),
            provenance={
                "decision_authority": "D13",
                "new_decision_created": False,
                "d13_decision_modified": False,
                "future_outcome_observed": False,
                "validated_by_D14": False,
                "learned_by_D15": False,
            },
        )

    # ----------------------------------------------------------------------
    # MANAGEMENT RESULT
    # ----------------------------------------------------------------------

    def _management_result(
        self,
        *,
        lifecycle: TradeLifecycle,
        action: ManagementAction,
        reason: ExitReason,
        text: str,
        snapshot: HTFMarketSnapshot,
    ) -> HTFResult:

        shot = self.active_shot

        if shot is None:
            return self._blocked_result(
                "no_active_htf_shot"
            )

        premium = self._option_premium(snapshot)
        spread, spread_bps = self._spread(snapshot)

        elapsed = max(
            0.0,
            (
                snapshot.timestamp -
                shot.entry_timestamp
            ).total_seconds(),
        )

        window_seconds = (
            shot.primary_window_minutes * 60.0
        )

        remaining = max(
            0.0,
            window_seconds - elapsed,
        )

        if lifecycle == TradeLifecycle.EXIT:
            shot.lifecycle = TradeLifecycle.EXIT
            shot.management_action = ManagementAction.EXIT

        return HTFResult(
            mode=HTFMode.ON,
            lifecycle=lifecycle,
            management_action=action,
            eligible=True,
            allowed_to_enter=False,
            d13_direction=shot.d13_direction,
            shot_id=shot.shot_id,
            option_side=shot.option_identity.option_side,
            option_premium=premium,
            spread=spread,
            spread_bps=spread_bps,
            underlying_return=self._return(
                snapshot.underlying_price,
                snapshot.underlying_previous_price,
            ),
            option_return=self._return(
                premium,
                shot.entry_premium,
            ),
            elapsed_seconds=elapsed,
            remaining_seconds=remaining,
            reassessment_due=False,
            exit_required=(
                action == ManagementAction.EXIT
            ),
            exit_reason=reason,
            reasons=(text,),
            provenance=self._provenance_from_shot(
                shot
            ),
        )

    # ----------------------------------------------------------------------
    # ACTIVE RESULT
    # ----------------------------------------------------------------------

    def _active_result(
        self,
        *,
        snapshot: HTFMarketSnapshot,
        action: ManagementAction,
        lifecycle: TradeLifecycle,
        reasons: Tuple[str, ...],
    ) -> HTFResult:

        shot = self.active_shot

        if shot is None:
            return self._blocked_result(
                "no_active_htf_shot"
            )

        premium = self._option_premium(snapshot)
        spread, spread_bps = self._spread(snapshot)

        elapsed = max(
            0.0,
            (
                snapshot.timestamp -
                shot.entry_timestamp
            ).total_seconds(),
        )

        remaining = max(
            0.0,
            (
                shot.primary_window_minutes * 60.0
                - elapsed
            ),
        )

        return HTFResult(
            mode=HTFMode.ON,
            lifecycle=lifecycle,
            management_action=action,
            eligible=True,
            allowed_to_enter=False,
            d13_direction=shot.d13_direction,
            shot_id=shot.shot_id,
            option_side=shot.option_identity.option_side,
            option_premium=premium,
            spread=spread,
            spread_bps=spread_bps,
            underlying_return=self._return(
                snapshot.underlying_price,
                snapshot.underlying_previous_price,
            ),
            option_return=self._return(
                premium,
                shot.entry_premium,
            ),
            elapsed_seconds=elapsed,
            remaining_seconds=remaining,
            reassessment_due=False,
            exit_required=False,
            exit_reason=ExitReason.NONE,
            reasons=reasons,
            provenance=self._provenance_from_shot(
                shot
            ),
        )

    # ----------------------------------------------------------------------
    # PROVENANCE
    # ----------------------------------------------------------------------

    @staticmethod
    def _provenance(
        *,
        d13: D13Snapshot,
        new_decision_created: bool,
    ) -> Dict[str, Any]:

        return {
            "decision_authority": "D13",
            "d13_decision_id": d13.decision_id,
            "new_decision_created": new_decision_created,
            "d13_decision_modified": False,
            "future_outcome_observed": d13.future_outcome_observed,
            "validated_by_D14": d13.validated_by_D14,
            "learned_by_D15": d13.learned_by_D15,
            "management_layer": "HTF_SCALPER",
            "one_shot": True,
        }

    @staticmethod
    def _provenance_from_shot(
        shot: HTFShot,
    ) -> Dict[str, Any]:

        return dict(shot.provenance)


# ============================================================================
# SELF TEST
# ============================================================================

def _self_test() -> None:
    """
    Structural smoke tests only.

    These do NOT establish trading profitability or real-market validity.
    """

    base_time = datetime(
        2026,
        9,
        5,
        10,
        0,
        0,
        tzinfo=timezone.utc,
    )

    policy = HTFPolicy(
        enabled=True,
        primary_window_minutes=3,
        reassessment_seconds=30,
        premium_filter_enabled=False,
        allow_position_stacking=False,
        allow_averaging=False,
        require_flat_before_new_shot=True,
    )

    engine = HTFScalperEngine(policy)

    d13 = D13Snapshot(
        decision_id="D13-TEST-001",
        market_id="NIFTY",
        action="BUY",
        decision_timestamp=base_time,
    )

    option = OptionIdentity(
        market_id="NIFTY",
        underlying="NIFTY",
        instrument="OPTION",
        option_side=OptionSide.CE,
        strike=25000.0,
        expiry="2026-09-10",
        venue="NSE",
        contract_id="NIFTY-25000-CE-2026-09-10",
    )

    snap0 = HTFMarketSnapshot(
        timestamp=base_time,
        underlying_price=25000.0,
        underlying_previous_price=24995.0,
        option_bid=100.0,
        option_ask=102.0,
        option_last=101.0,
        option_volume=100000.0,
        option_oi=500000.0,
        option_iv=18.0,
        source_timestamp=base_time,
    )

    # --------------------------------------------------------------
    # 1. HTF OFF must block
    # --------------------------------------------------------------

    result = engine.evaluate_entry(
        mode=HTFMode.OFF,
        d13=d13,
        option_identity=option,
        snapshot=snap0,
    )

    assert result.allowed_to_enter is False
    assert result.lifecycle == TradeLifecycle.BLOCKED

    # --------------------------------------------------------------
    # 2. HTF ON must allow valid D13 shot
    # --------------------------------------------------------------

    result = engine.evaluate_entry(
        mode=HTFMode.ON,
        d13=d13,
        option_identity=option,
        snapshot=snap0,
    )

    assert result.allowed_to_enter is True
    assert result.d13_direction == "BUY"
    assert result.option_side == OptionSide.CE

    # --------------------------------------------------------------
    # 3. Open one shot
    # --------------------------------------------------------------

    result = engine.open_shot(
        shot_id="HTF-SHOT-001",
        mode=HTFMode.ON,
        d13=d13,
        option_identity=option,
        snapshot=snap0,
    )

    assert result.lifecycle == TradeLifecycle.ACTIVE
    assert engine.active_shot is not None

    # --------------------------------------------------------------
    # 4. Second entry must be blocked
    # --------------------------------------------------------------

    result = engine.evaluate_entry(
        mode=HTFMode.ON,
        d13=d13,
        option_identity=option,
        snapshot=snap0,
    )

    assert result.allowed_to_enter is False
    assert "active_shot_already_exists" in result.reasons

    # --------------------------------------------------------------
    # 5. Positive option response
    # --------------------------------------------------------------

    snap1 = HTFMarketSnapshot(
        timestamp=base_time.replace(second=30),
        underlying_price=25010.0,
        underlying_previous_price=25000.0,
        option_bid=103.0,
        option_ask=105.0,
        option_last=104.0,
        option_volume=110000.0,
        option_oi=505000.0,
        option_iv=18.5,
        source_timestamp=base_time.replace(second=30),
    )

    result = engine.monitor(
        d13=d13,
        snapshot=snap1,
    )

    assert result.lifecycle == TradeLifecycle.ACTIVE
    assert result.management_action == ManagementAction.FOLLOW
    assert result.option_return is not None
    assert result.option_return > 0

    # --------------------------------------------------------------
    # 6. Explicit invalidation must create EXIT context
    # --------------------------------------------------------------

    snap2 = HTFMarketSnapshot(
    timestamp=base_time.replace(minute=1),
    underlying_price=24980.0,
    underlying_previous_price=25010.0,
    option_bid=92.0,
    option_ask=94.0,
    option_last=93.0,
    option_volume=125000.0,
    option_oi=510000.0,
    option_iv=19.0,
    source_timestamp=base_time.replace(minute=1),
)

    result = engine.monitor(
        d13=d13,
        snapshot=snap2,
        explicit_invalidation=True,
    )

    assert result.exit_required is True
    assert result.management_action == ManagementAction.EXIT
    assert result.exit_reason == ExitReason.THESIS_INVALIDATED

    # --------------------------------------------------------------
    # 7. Close
    # --------------------------------------------------------------

    result = engine.close_shot(
        snapshot=snap2,
        reason=ExitReason.THESIS_INVALIDATED,
    )

    assert result.lifecycle == TradeLifecycle.CLOSED
    assert result.exit_required is True
    assert engine.active_shot is None

    # --------------------------------------------------------------
    # 8. New shot after close is allowed
    # --------------------------------------------------------------

    result = engine.evaluate_entry(
        mode=HTFMode.ON,
        d13=d13,
        option_identity=option,
        snapshot=snap0,
    )

    assert result.allowed_to_enter is True

    # --------------------------------------------------------------
    # 9. Future data must block
    # --------------------------------------------------------------

    future_snap = HTFMarketSnapshot(
        timestamp=base_time,
        underlying_price=25000.0,
        option_bid=100.0,
        option_ask=102.0,
        option_last=101.0,
        source_timestamp=base_time,
        future_data=True,
    )

    result = engine.evaluate_entry(
        mode=HTFMode.ON,
        d13=d13,
        option_identity=option,
        snapshot=future_snap,
    )

    assert result.allowed_to_enter is False
    assert "future_data_detected" in result.reasons

    # --------------------------------------------------------------
    # 10. HOLD cannot create HTF directional shot
    # --------------------------------------------------------------

    hold_d13 = D13Snapshot(
        decision_id="D13-TEST-HOLD",
        market_id="NIFTY",
        action="HOLD",
        decision_timestamp=base_time,
    )

    result = engine.evaluate_entry(
        mode=HTFMode.ON,
        d13=hold_d13,
        option_identity=option,
        snapshot=snap0,
    )

    assert result.allowed_to_enter is False
    assert "d13_has_no_directional_decision" in result.reasons

    print("HTF / SCALPER SELF-TEST: PASS")


if __name__ == "__main__":
    _self_test()