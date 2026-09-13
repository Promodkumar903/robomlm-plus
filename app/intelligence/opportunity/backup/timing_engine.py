"""
ROBOMLM_PLUS
Opportunity Intelligence Layer
Timing Engine

Purpose
-------
Determine whether the current market observation is temporally suitable
for Opportunity Discovery.

Responsibilities
----------------
- Normalize timing/session observations.
- Validate point-in-time integrity.
- Identify market session state.
- Evaluate configurable trading windows.
- Detect opening/closing proximity.
- Detect expiry/session-event proximity when supplied.
- Produce explainable timing eligibility.
- Preserve provenance.

Non-responsibilities
--------------------
- No BUY/SELL generation.
- No future prediction.
- No proprietary opportunity score.
- No replacement for D13 Decision Authority.
- No fabrication of market-session data.
- No hard-coded assumption that every market follows NSE timings.

Architecture
------------
Universe -> Liquidity -> Risk -> Timing -> Intraday -> Ranking
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict, is_dataclass
from enum import Enum
from datetime import datetime, time, timezone
from math import isfinite
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple


# ---------------------------------------------------------------------------
# ENUMS
# ---------------------------------------------------------------------------

class TimingStatus(str, Enum):
    PASS = "PASS"
    REVIEW = "REVIEW"
    REJECT = "REJECT"
    UNKNOWN = "UNKNOWN"


class SessionState(str, Enum):
    PRE_OPEN = "PRE_OPEN"
    OPEN = "OPEN"
    MID_SESSION = "MID_SESSION"
    CLOSING = "CLOSING"
    POST_CLOSE = "POST_CLOSE"
    CLOSED = "CLOSED"
    UNKNOWN = "UNKNOWN"


class TimingCondition(str, Enum):
    OPTIMAL = "OPTIMAL"
    ACTIVE = "ACTIVE"
    LATE = "LATE"
    EARLY = "EARLY"
    EVENT_NEAR = "EVENT_NEAR"
    OUTSIDE_WINDOW = "OUTSIDE_WINDOW"
    UNKNOWN = "UNKNOWN"


# ---------------------------------------------------------------------------
# SESSION WINDOW
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TimingWindow:
    """
    Configurable market/session window.

    start/end are local market-clock times.

    Overnight windows are supported:
        start > end

    Example:
        22:00 -> 05:00
    """

    name: str
    start: time
    end: time

    enabled: bool = True
    priority: int = 0

    metadata: Dict[str, Any] = field(default_factory=dict)

    def contains(self, current: time) -> bool:
        if not self.enabled:
            return False

        if self.start <= self.end:
            return self.start <= current <= self.end

        # Overnight window.
        return current >= self.start or current <= self.end


# ---------------------------------------------------------------------------
# DATA CONTRACTS
# ---------------------------------------------------------------------------

@dataclass
class TimingSnapshot:
    """
    Normalized point-in-time timing observation.
    """

    instrument_id: str
    symbol: str

    timestamp: Optional[datetime] = None

    market_id: Optional[str] = None
    venue_id: Optional[str] = None

    timezone: Optional[str] = None

    session_state: SessionState = SessionState.UNKNOWN

    current_time: Optional[time] = None

    minutes_from_open: Optional[float] = None
    minutes_to_close: Optional[float] = None

    minutes_to_event: Optional[float] = None

    expiry_near: Optional[bool] = None
    event_near: Optional[bool] = None

    is_trading_day: Optional[bool] = None
    market_open: Optional[bool] = None

    window_name: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TimingDecision:
    instrument_id: str
    symbol: str

    status: TimingStatus
    session_state: SessionState
    condition: TimingCondition

    reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    window_name: Optional[str] = None

    minutes_from_open: Optional[float] = None
    minutes_to_close: Optional[float] = None
    minutes_to_event: Optional[float] = None

    expiry_near: Optional[bool] = None
    event_near: Optional[bool] = None

    market_id: Optional[str] = None
    timestamp: Optional[datetime] = None

    provenance: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TimingResult:
    decisions: List[TimingDecision] = field(default_factory=list)

    passed: List[TimingDecision] = field(default_factory=list)
    review: List[TimingDecision] = field(default_factory=list)
    rejected: List[TimingDecision] = field(default_factory=list)
    unknown: List[TimingDecision] = field(default_factory=list)

    total: int = 0

    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.decisions:
            self.decisions = (
                list(self.passed)
                + list(self.review)
                + list(self.rejected)
                + list(self.unknown)
            )

        self.total = len(self.decisions)

        if not self.passed:
            self.passed = [
                d for d in self.decisions
                if d.status == TimingStatus.PASS
            ]

        if not self.review:
            self.review = [
                d for d in self.decisions
                if d.status == TimingStatus.REVIEW
            ]

        if not self.rejected:
            self.rejected = [
                d for d in self.decisions
                if d.status == TimingStatus.REJECT
            ]

        if not self.unknown:
            self.unknown = [
                d for d in self.decisions
                if d.status == TimingStatus.UNKNOWN
            ]


# ---------------------------------------------------------------------------
# POLICY
# ---------------------------------------------------------------------------

@dataclass
class TimingPolicy:
    """
    External timing policy.

    No market-specific timing assumptions are forced by default.
    Deployment/market configuration should provide actual windows.
    """

    windows: List[TimingWindow] = field(default_factory=list)

    review_outside_window: bool = True
    reject_outside_window: bool = False

    review_event_near: bool = True
    reject_event_near: bool = False

    review_expiry_near: bool = True
    reject_expiry_near: bool = False

    review_before_close_minutes: Optional[float] = None
    reject_before_close_minutes: Optional[float] = None

    review_after_open_minutes: Optional[float] = None
    reject_after_open_minutes: Optional[float] = None

    require_market_match: bool = True
    reject_future_data: bool = True

    require_trading_day: bool = False
    require_market_open: bool = False

    policy_version: str = "EXTERNAL_POLICY_REQUIRED"

    metadata: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# ENGINE
# ---------------------------------------------------------------------------

class TimingEngine:
    """
    Timing eligibility engine for Opportunity Discovery.
    """

    def __init__(
        self,
        policy: Optional[TimingPolicy] = None,
        expected_market_id: Optional[str] = None,
    ) -> None:
        self.policy = policy or TimingPolicy()
        self.expected_market_id = expected_market_id

    # -----------------------------------------------------------------------
    # PUBLIC EVALUATION API
    # -----------------------------------------------------------------------

    def evaluate(
        self,
        snapshot: Any,
        *,
        expected_market_id: Optional[str] = None,
        now: Optional[datetime] = None,
    ) -> TimingDecision:

        timing = self.normalize(snapshot)

        reasons: List[str] = []
        warnings: List[str] = []

        market_id = expected_market_id or self.expected_market_id

        # -------------------------------------------------------------------
        # Basic identity
        # -------------------------------------------------------------------

        if not timing.instrument_id:
            return self._decision(
                timing,
                TimingStatus.REJECT,
                TimingCondition.UNKNOWN,
                ["Missing instrument_id"],
                warnings,
            )

        if not timing.symbol:
            return self._decision(
                timing,
                TimingStatus.REJECT,
                TimingCondition.UNKNOWN,
                ["Missing symbol"],
                warnings,
            )

        # -------------------------------------------------------------------
        # Market identity
        # -------------------------------------------------------------------

        if (
            self.policy.require_market_match
            and market_id is not None
            and timing.market_id is not None
            and str(timing.market_id) != str(market_id)
        ):
            return self._decision(
                timing,
                TimingStatus.REJECT,
                TimingCondition.UNKNOWN,
                [
                    "Market identity mismatch",
                    f"expected_market_id={market_id}",
                    f"observed_market_id={timing.market_id}",
                ],
                warnings,
            )

        if (
            self.policy.require_market_match
            and market_id is not None
            and timing.market_id is None
        ):
            return self._decision(
                timing,
                TimingStatus.REJECT,
                TimingCondition.UNKNOWN,
                ["Market identity unavailable"],
                warnings,
            )

        # -------------------------------------------------------------------
        # Future-data protection
        # -------------------------------------------------------------------

        if timing.timestamp is not None:
            current_time = now or datetime.now(timezone.utc)

            observed = self._ensure_aware(timing.timestamp)
            current_time = self._ensure_aware(current_time)

            if self.policy.reject_future_data and observed > current_time:
                return self._decision(
                    timing,
                    TimingStatus.REJECT,
                    TimingCondition.UNKNOWN,
                    ["Future-dated timing observation rejected"],
                    warnings,
                )

        # -------------------------------------------------------------------
        # Trading-day validation
        # -------------------------------------------------------------------

        if (
            self.policy.require_trading_day
            and timing.is_trading_day is None
        ):
            return self._decision(
                timing,
                TimingStatus.UNKNOWN,
                TimingCondition.UNKNOWN,
                ["Trading-day state unavailable"],
                warnings,
            )

        if (
            self.policy.require_trading_day
            and timing.is_trading_day is False
        ):
            return self._decision(
                timing,
                TimingStatus.REJECT,
                TimingCondition.OUTSIDE_WINDOW,
                ["Observation is outside a trading day"],
                warnings,
            )

        # -------------------------------------------------------------------
        # Market-open validation
        # -------------------------------------------------------------------

        if (
            self.policy.require_market_open
            and timing.market_open is None
        ):
            return self._decision(
                timing,
                TimingStatus.UNKNOWN,
                TimingCondition.UNKNOWN,
                ["Market-open state unavailable"],
                warnings,
            )

        if (
            self.policy.require_market_open
            and timing.market_open is False
        ):
            return self._decision(
                timing,
                TimingStatus.REJECT,
                TimingCondition.OUTSIDE_WINDOW,
                ["Market is not open"],
                warnings,
            )

        # -------------------------------------------------------------------
        # Validate numeric timing fields
        # -------------------------------------------------------------------

        numeric_fields = {
            "minutes_from_open": timing.minutes_from_open,
            "minutes_to_close": timing.minutes_to_close,
            "minutes_to_event": timing.minutes_to_event,
        }

        invalid = [
            name
            for name, value in numeric_fields.items()
            if value is not None and not self._valid_number(value)
        ]

        if invalid:
            return self._decision(
                timing,
                TimingStatus.REJECT,
                TimingCondition.UNKNOWN,
                [
                    "Invalid numeric timing fields",
                    ", ".join(invalid),
                ],
                warnings,
            )

        # -------------------------------------------------------------------
        # Resolve configured timing window
        # -------------------------------------------------------------------

        matched_window = self._match_window(
            timing.current_time
        )

        if matched_window is not None:
            timing.window_name = matched_window.name

        # -------------------------------------------------------------------
        # Determine base timing condition
        # -------------------------------------------------------------------

        condition = self._condition(
            timing,
            matched_window,
        )

        # -------------------------------------------------------------------
        # Decision flags
        # -------------------------------------------------------------------

        review_required = False
        hard_reject = False

        # -------------------------------------------------------------------
        # Outside configured window
        # -------------------------------------------------------------------

        if self.policy.windows and matched_window is None:

            if self.policy.reject_outside_window:
                hard_reject = True
                reasons.append(
                    "Current time is outside configured timing windows"
                )

            elif self.policy.review_outside_window:
                review_required = True
                warnings.append(
                    "Current time is outside configured timing windows"
                )

        # -------------------------------------------------------------------
        # Event proximity
        # -------------------------------------------------------------------

        if timing.event_near is True:

            if self.policy.reject_event_near:
                hard_reject = True
                reasons.append(
                    "Market event is flagged as near"
                )

            elif self.policy.review_event_near:
                review_required = True
                warnings.append(
                    "Market event is flagged as near"
                )

        # -------------------------------------------------------------------
        # Expiry proximity
        # -------------------------------------------------------------------

        if timing.expiry_near is True:

            if self.policy.reject_expiry_near:
                hard_reject = True
                reasons.append(
                    "Expiry proximity is flagged as near"
                )

            elif self.policy.review_expiry_near:
                review_required = True
                warnings.append(
                    "Expiry proximity is flagged as near"
                )

        # -------------------------------------------------------------------
        # PART 1 ENDS HERE
        # -------------------------------------------------------------------
        # -------------------------------------------------------------------
        # Opening proximity
        # -------------------------------------------------------------------

        if (
            timing.minutes_from_open is not None
            and self.policy.reject_after_open_minutes is not None
            and timing.minutes_from_open >= 0
            and timing.minutes_from_open
            <= self.policy.reject_after_open_minutes
        ):
            hard_reject = True
            reasons.append(
                "Observation is within configured opening rejection period"
            )

        elif (
            timing.minutes_from_open is not None
            and self.policy.review_after_open_minutes is not None
            and timing.minutes_from_open >= 0
            and timing.minutes_from_open
            <= self.policy.review_after_open_minutes
        ):
            review_required = True
            warnings.append(
                "Observation is within configured opening review period"
            )

        # -------------------------------------------------------------------
        # Closing proximity
        # -------------------------------------------------------------------

        if (
            timing.minutes_to_close is not None
            and timing.minutes_to_close >= 0
            and self.policy.reject_before_close_minutes is not None
            and timing.minutes_to_close
            <= self.policy.reject_before_close_minutes
        ):
            hard_reject = True
            reasons.append(
                "Observation is within configured closing rejection period"
            )

        elif (
            timing.minutes_to_close is not None
            and timing.minutes_to_close >= 0
            and self.policy.review_before_close_minutes is not None
            and timing.minutes_to_close
            <= self.policy.review_before_close_minutes
        ):
            review_required = True
            warnings.append(
                "Observation is within configured closing review period"
            )

        # -------------------------------------------------------------------
        # Negative temporal distances are invalid states.
        # -------------------------------------------------------------------

        negative_fields = []

        if (
            timing.minutes_from_open is not None
            and timing.minutes_from_open < 0
        ):
            negative_fields.append("minutes_from_open")

        if (
            timing.minutes_to_close is not None
            and timing.minutes_to_close < 0
        ):
            negative_fields.append("minutes_to_close")

        if (
            timing.minutes_to_event is not None
            and timing.minutes_to_event < 0
        ):
            negative_fields.append("minutes_to_event")

        if negative_fields:
            return self._decision(
                timing,
                TimingStatus.REJECT,
                TimingCondition.UNKNOWN,
                [
                    "Invalid negative timing distance",
                    ", ".join(negative_fields),
                ],
                warnings,
            )

        # -------------------------------------------------------------------
        # Resolve final status.
        # -------------------------------------------------------------------

        if hard_reject:
            final_status = TimingStatus.REJECT

            if not reasons:
                reasons.append(
                    "Timing policy rejected observation"
                )

        elif review_required:
            final_status = TimingStatus.REVIEW

            if not reasons and not warnings:
                warnings.append(
                    "Timing requires review under configured policy"
                )

        else:
            # No rejection/review condition remains.
            #
            # If there is enough observable timing information,
            # the observation can pass.
            if self._has_observable_timing(
                timing,
                matched_window,
            ):
                final_status = TimingStatus.PASS
                reasons.append(
                    "Timing conditions satisfy configured policy"
                )
            else:
                final_status = TimingStatus.UNKNOWN
                warnings.append(
                    "Insufficient observable timing information"
                )

        return self._decision(
            timing,
            final_status,
            condition,
            reasons,
            warnings,
        )

    # -----------------------------------------------------------------------
    # COLLECTION API
    # -----------------------------------------------------------------------

    def filter(
        self,
        snapshots: Iterable[Any],
        *,
        expected_market_id: Optional[str] = None,
        now: Optional[datetime] = None,
    ) -> TimingResult:
        """
        Evaluate a collection of timing observations.

        No observation is silently discarded from the result.
        Every normalized decision remains auditable.
        """

        decisions: List[TimingDecision] = []

        for snapshot in snapshots:
            try:
                decision = self.evaluate(
                    snapshot,
                    expected_market_id=expected_market_id,
                    now=now,
                )
            except Exception as exc:
                try:
                    timing = self.normalize(snapshot)

                    decision = self._decision(
                        timing,
                        TimingStatus.UNKNOWN,
                        TimingCondition.UNKNOWN,
                        [
                            "Timing evaluation exception"
                        ],
                        [
                            f"{type(exc).__name__}: {exc}"
                        ],
                    )
                except Exception as normalize_exc:
                    decision = TimingDecision(
                        instrument_id="",
                        symbol="",
                        status=TimingStatus.UNKNOWN,
                        session_state=SessionState.UNKNOWN,
                        condition=TimingCondition.UNKNOWN,
                        reasons=[
                            "Unable to normalize timing observation"
                        ],
                        warnings=[
                            f"{type(normalize_exc).__name__}: "
                            f"{normalize_exc}"
                        ],
                        provenance={
                            "engine": "TimingEngine",
                            "engine_version": "1.0",
                            "evaluation_error": True,
                        },
                    )

            decisions.append(decision)

        return TimingResult(
            decisions=decisions,
            metadata={
                "engine": "TimingEngine",
                "engine_version": "1.0",
                "policy_version": self.policy.policy_version,
                "expected_market_id": (
                    expected_market_id
                    or self.expected_market_id
                ),
            },
        )

    def apply(
        self,
        snapshots: Iterable[Any],
        *,
        expected_market_id: Optional[str] = None,
        now: Optional[datetime] = None,
        include_review: bool = False,
    ) -> List[TimingDecision]:
        """
        Apply timing eligibility to a collection.

        Default:
            PASS only.

        include_review=True:
            PASS + REVIEW.

        REJECT and UNKNOWN are never returned as eligible.
        """

        result = self.filter(
            snapshots,
            expected_market_id=expected_market_id,
            now=now,
        )

        if include_review:
            return (
                list(result.passed)
                + list(result.review)
            )

        return list(result.passed)

    # -----------------------------------------------------------------------
    # WINDOW MATCHING
    # -----------------------------------------------------------------------

    def _match_window(
        self,
        current_time: Optional[time],
    ) -> Optional[TimingWindow]:
        """
        Find the highest-priority enabled timing window containing
        current_time.

        If multiple windows overlap, highest priority wins.

        Equal priorities preserve configuration order.
        """

        if current_time is None:
            return None

        candidates: List[
            Tuple[int, int, TimingWindow]
        ] = []

        for index, window in enumerate(
            self.policy.windows
        ):
            if not isinstance(window, TimingWindow):
                continue

            if not window.enabled:
                continue

            if window.contains(current_time):
                candidates.append(
                    (
                        int(window.priority),
                        -index,
                        window,
                    )
                )

        if not candidates:
            return None

        candidates.sort(
            key=lambda item: (
                item[0],
                item[1],
            ),
            reverse=True,
        )

        return candidates[0][2]

    # -----------------------------------------------------------------------
    # CONDITION
    # -----------------------------------------------------------------------

    def _condition(
        self,
        timing: TimingSnapshot,
        matched_window: Optional[TimingWindow],
    ) -> TimingCondition:
        """
        Determine the descriptive timing condition.

        This is classification, not prediction and not scoring.
        """

        # Explicit event proximity takes precedence.
        if timing.event_near is True:
            return TimingCondition.EVENT_NEAR

        if timing.expiry_near is True:
            return TimingCondition.EVENT_NEAR

        # Opening proximity.
        if (
            timing.minutes_from_open is not None
            and timing.minutes_from_open >= 0
        ):
            if (
                self.policy.review_after_open_minutes is not None
                and timing.minutes_from_open
                <= self.policy.review_after_open_minutes
            ):
                return TimingCondition.EARLY

            if (
                self.policy.reject_after_open_minutes is not None
                and timing.minutes_from_open
                <= self.policy.reject_after_open_minutes
            ):
                return TimingCondition.EARLY

        # Closing proximity.
        if (
            timing.minutes_to_close is not None
            and timing.minutes_to_close >= 0
        ):
            if (
                self.policy.review_before_close_minutes is not None
                and timing.minutes_to_close
                <= self.policy.review_before_close_minutes
            ):
                return TimingCondition.LATE

            if (
                self.policy.reject_before_close_minutes is not None
                and timing.minutes_to_close
                <= self.policy.reject_before_close_minutes
            ):
                return TimingCondition.LATE

        # Configured window state.
        if matched_window is not None:
            if timing.session_state in {
                SessionState.OPEN,
                SessionState.MID_SESSION,
            }:
                return TimingCondition.OPTIMAL

            if timing.session_state == SessionState.CLOSING:
                return TimingCondition.LATE

            if timing.session_state == SessionState.PRE_OPEN:
                return TimingCondition.EARLY

            return TimingCondition.ACTIVE

        # A configured policy exists but observation is outside it.
        if self.policy.windows:
            return TimingCondition.OUTSIDE_WINDOW

        # No configured window: classify from observable session state.
        if timing.session_state in {
            SessionState.OPEN,
            SessionState.MID_SESSION,
        }:
            return TimingCondition.ACTIVE

        if timing.session_state == SessionState.CLOSING:
            return TimingCondition.LATE

        if timing.session_state == SessionState.PRE_OPEN:
            return TimingCondition.EARLY

        return TimingCondition.UNKNOWN

    # -----------------------------------------------------------------------
    # OBSERVABILITY
    # -----------------------------------------------------------------------

    @staticmethod
    def _has_observable_timing(
        timing: TimingSnapshot,
        matched_window: Optional[TimingWindow],
    ) -> bool:
        """
        Determine whether enough timing information exists to make
        an eligibility determination.

        This does not infer missing market-session information.
        """

        if matched_window is not None:
            return True

        if timing.session_state != SessionState.UNKNOWN:
            return True

        if timing.current_time is not None:
            return True

        if timing.minutes_from_open is not None:
            return True

        if timing.minutes_to_close is not None:
            return True

        if timing.minutes_to_event is not None:
            return True

        if timing.event_near is not None:
            return True

        if timing.expiry_near is not None:
            return True

        if timing.market_open is not None:
            return True

        return False

    # -----------------------------------------------------------------------
    # DECISION BUILDER
    # -----------------------------------------------------------------------

    def _decision(
        self,
        timing: TimingSnapshot,
        status: TimingStatus,
        condition: TimingCondition,
        reasons: List[str],
        warnings: List[str],
    ) -> TimingDecision:

        return TimingDecision(
            instrument_id=timing.instrument_id,
            symbol=timing.symbol,
            status=status,
            session_state=timing.session_state,
            condition=condition,
            reasons=list(reasons),
            warnings=list(warnings),
            window_name=timing.window_name,
            minutes_from_open=timing.minutes_from_open,
            minutes_to_close=timing.minutes_to_close,
            minutes_to_event=timing.minutes_to_event,
            expiry_near=timing.expiry_near,
            event_near=timing.event_near,
            market_id=timing.market_id,
            timestamp=timing.timestamp,
            provenance={
                "engine": "TimingEngine",
                "engine_version": "1.0",
                "policy_version": self.policy.policy_version,
                "expected_market_id": self.expected_market_id,
                "source": (
                    timing.metadata.get("source")
                    if isinstance(timing.metadata, Mapping)
                    else None
                ),
                "point_in_time": True,
                "future_data_rejected": (
                    self.policy.reject_future_data
                ),
            },
        )

    # -----------------------------------------------------------------------
    # PART 2 ENDS HERE
    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------
    # NORMALIZATION
    # -----------------------------------------------------------------------

    def normalize(
        self,
        value: Any,
    ) -> TimingSnapshot:
        """
        Convert Mapping, dataclass, object, or TimingSnapshot into
        the normalized TimingSnapshot contract.
        """

        if isinstance(value, TimingSnapshot):
            return value

        data = self._to_mapping(value)

        instrument_id = self._first(
            data,
            "instrument_id",
            "instrumentId",
            "id",
            default="",
        )

        symbol = self._first(
            data,
            "symbol",
            "ticker",
            "exchange_symbol",
            "exchangeSymbol",
            default="",
        )

        timestamp = self._first(
            data,
            "timestamp",
            "time",
            "observed_at",
            "observedAt",
            default=None,
        )

        timestamp = self._parse_timestamp(timestamp)

        market_id = self._first(
            data,
            "market_id",
            "marketId",
            default=None,
        )

        venue_id = self._first(
            data,
            "venue_id",
            "venueId",
            default=None,
        )

        timezone_name = self._first(
            data,
            "timezone",
            "time_zone",
            "tz",
            default=None,
        )

        session_state = self._parse_session_state(
            self._first(
                data,
                "session_state",
                "sessionState",
                "session",
                default=None,
            )
        )

        current_time = self._parse_time(
            self._first(
                data,
                "current_time",
                "currentTime",
                "local_time",
                "localTime",
                default=None,
            )
        )

        # If current_time is not explicitly supplied, derive it from
        # the observed timestamp. This does not create future information.
        if current_time is None and timestamp is not None:
            current_time = timestamp.timetz().replace(
                tzinfo=None
            )

        minutes_from_open = self._number(
            self._first(
                data,
                "minutes_from_open",
                "minutesFromOpen",
                "mins_from_open",
                default=None,
            )
        )

        minutes_to_close = self._number(
            self._first(
                data,
                "minutes_to_close",
                "minutesToClose",
                "mins_to_close",
                default=None,
            )
        )

        minutes_to_event = self._number(
            self._first(
                data,
                "minutes_to_event",
                "minutesToEvent",
                "mins_to_event",
                default=None,
            )
        )

        expiry_near = self._boolean(
            self._first(
                data,
                "expiry_near",
                "expiryNear",
                default=None,
            )
        )

        event_near = self._boolean(
            self._first(
                data,
                "event_near",
                "eventNear",
                default=None,
            )
        )

        is_trading_day = self._boolean(
            self._first(
                data,
                "is_trading_day",
                "isTradingDay",
                "trading_day",
                default=None,
            )
        )

        market_open = self._boolean(
            self._first(
                data,
                "market_open",
                "marketOpen",
                "is_open",
                "isOpen",
                default=None,
            )
        )

        window_name = self._first(
            data,
            "window_name",
            "windowName",
            default=None,
        )

        metadata = self._first(
            data,
            "metadata",
            "meta",
            default={},
        )

        if not isinstance(metadata, Mapping):
            metadata = {
                "raw_metadata": metadata
            }

        return TimingSnapshot(
            instrument_id=str(
                instrument_id or ""
            ),
            symbol=str(
                symbol or ""
            ),
            timestamp=timestamp,
            market_id=self._string_or_none(
                market_id
            ),
            venue_id=self._string_or_none(
                venue_id
            ),
            timezone=self._string_or_none(
                timezone_name
            ),
            session_state=session_state,
            current_time=current_time,
            minutes_from_open=minutes_from_open,
            minutes_to_close=minutes_to_close,
            minutes_to_event=minutes_to_event,
            expiry_near=expiry_near,
            event_near=event_near,
            is_trading_day=is_trading_day,
            market_open=market_open,
            window_name=self._string_or_none(
                window_name
            ),
            metadata=dict(metadata),
        )

    # -----------------------------------------------------------------------
    # NORMALIZATION HELPERS
    # -----------------------------------------------------------------------

    @staticmethod
    def _to_mapping(
        value: Any,
    ) -> Dict[str, Any]:
        """
        Convert supported input types to a dictionary.
        """

        if isinstance(value, Mapping):
            return dict(value)

        if is_dataclass(value) and not isinstance(
            value,
            type,
        ):
            return asdict(value)

        if hasattr(value, "__dict__"):
            return dict(vars(value))

        raise TypeError(
            f"Unsupported timing snapshot type: "
            f"{type(value).__name__}"
        )

    @staticmethod
    def _first(
        data: Mapping[str, Any],
        *keys: str,
        default: Any = None,
    ) -> Any:
        """
        Return the first present key.

        Zero and False are valid values and are preserved.
        """

        for key in keys:
            if key in data:
                return data[key]

        return default

    @staticmethod
    def _number(
        value: Any,
    ) -> Optional[float]:
        """
        Convert numeric input safely.
        """

        if value is None:
            return None

        if isinstance(value, bool):
            return None

        try:
            number = float(value)
        except (
            TypeError,
            ValueError,
        ):
            return None

        if not isfinite(number):
            return None

        return number

    @staticmethod
    def _valid_number(
        value: Any,
    ) -> bool:

        if isinstance(value, bool):
            return False

        try:
            number = float(value)
        except (
            TypeError,
            ValueError,
        ):
            return False

        return isfinite(number)

    @staticmethod
    def _boolean(
        value: Any,
    ) -> Optional[bool]:
        """
        Parse boolean-like values without guessing arbitrary values.
        """

        if value is None:
            return None

        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            text = value.strip().lower()

            if text in {
                "true",
                "1",
                "yes",
                "y",
                "open",
            }:
                return True

            if text in {
                "false",
                "0",
                "no",
                "n",
                "closed",
            }:
                return False

        if isinstance(value, (int, float)):
            if value == 1:
                return True

            if value == 0:
                return False

        return None

    @staticmethod
    def _string_or_none(
        value: Any,
    ) -> Optional[str]:

        if value is None:
            return None

        text = str(value).strip()

        return text if text else None

    # -----------------------------------------------------------------------
    # TIME PARSING
    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_timestamp(
        value: Any,
    ) -> Optional[datetime]:
        """
        Parse datetime, ISO-8601 string, or Unix timestamp.
        """

        if value is None:
            return None

        if isinstance(value, datetime):
            return value

        if (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
        ):
            try:
                return datetime.fromtimestamp(
                    float(value),
                    tz=timezone.utc,
                )
            except (
                OverflowError,
                OSError,
                ValueError,
            ):
                return None

        if isinstance(value, str):
            text = value.strip()

            if not text:
                return None

            if text.endswith("Z"):
                text = text[:-1] + "+00:00"

            try:
                return datetime.fromisoformat(text)
            except ValueError:
                return None

        return None

    @staticmethod
    def _parse_time(
        value: Any,
    ) -> Optional[time]:
        """
        Parse common time representations.
        """

        if value is None:
            return None

        if isinstance(value, time):
            return value

        if isinstance(value, datetime):
            return value.timetz().replace(
                tzinfo=None
            )

        if isinstance(value, str):
            text = value.strip()

            if not text:
                return None

            try:
                return time.fromisoformat(text)
            except ValueError:
                pass

            parsed_datetime = TimingEngine._parse_timestamp(
                text
            )

            if parsed_datetime is not None:
                return parsed_datetime.timetz().replace(
                    tzinfo=None
                )

        return None

    @staticmethod
    def _parse_session_state(
        value: Any,
    ) -> SessionState:

        if isinstance(value, SessionState):
            return value

        if value is None:
            return SessionState.UNKNOWN

        text = str(value).strip().upper()

        aliases = {
            "PREOPEN": SessionState.PRE_OPEN,
            "PRE-OPEN": SessionState.PRE_OPEN,
            "OPENING": SessionState.PRE_OPEN,

            "OPEN": SessionState.OPEN,
            "LIVE": SessionState.OPEN,

            "MID": SessionState.MID_SESSION,
            "MIDSESSION": SessionState.MID_SESSION,
            "MID-SESSION": SessionState.MID_SESSION,

            "CLOSE": SessionState.CLOSING,
            "CLOSING": SessionState.CLOSING,

            "POSTCLOSE": SessionState.POST_CLOSE,
            "POST-CLOSE": SessionState.POST_CLOSE,

            "CLOSED": SessionState.CLOSED,
            "OFF": SessionState.CLOSED,
        }

        if text in aliases:
            return aliases[text]

        try:
            return SessionState(text)
        except ValueError:
            return SessionState.UNKNOWN

    @staticmethod
    def _ensure_aware(
        value: datetime,
    ) -> datetime:
        """
        Normalize datetime to UTC for comparison.
        """

        if value.tzinfo is None:
            return value.replace(
                tzinfo=timezone.utc
            )

        return value.astimezone(
            timezone.utc
        )

    # -----------------------------------------------------------------------
    # SERIALIZATION
    # -----------------------------------------------------------------------

    @staticmethod
    def snapshot_to_dict(
        snapshot: TimingSnapshot,
    ) -> Dict[str, Any]:

        data = asdict(snapshot)

        data["session_state"] = (
            snapshot.session_state.value
        )

        if isinstance(
            snapshot.timestamp,
            datetime,
        ):
            data["timestamp"] = (
                snapshot.timestamp.isoformat()
            )

        if isinstance(
            snapshot.current_time,
            time,
        ):
            data["current_time"] = (
                snapshot.current_time.isoformat()
            )

        return data

    @staticmethod
    def decision_to_dict(
        decision: TimingDecision,
    ) -> Dict[str, Any]:

        data = asdict(decision)

        data["status"] = decision.status.value

        data["session_state"] = (
            decision.session_state.value
        )

        data["condition"] = (
            decision.condition.value
        )

        if isinstance(
            decision.timestamp,
            datetime,
        ):
            data["timestamp"] = (
                decision.timestamp.isoformat()
            )

        return data

    @classmethod
    def result_to_dict(
        cls,
        result: TimingResult,
    ) -> Dict[str, Any]:

        return {
            "total": result.total,

            "passed": [
                cls.decision_to_dict(d)
                for d in result.passed
            ],

            "review": [
                cls.decision_to_dict(d)
                for d in result.review
            ],

            "rejected": [
                cls.decision_to_dict(d)
                for d in result.rejected
            ],

            "unknown": [
                cls.decision_to_dict(d)
                for d in result.unknown
            ],

            "metadata": dict(
                result.metadata
            ),
        }


# ---------------------------------------------------------------------------
# CONVENIENCE API
# ---------------------------------------------------------------------------

def evaluate_timing(
    snapshot: Any,
    policy: Optional[TimingPolicy] = None,
    *,
    expected_market_id: Optional[str] = None,
    now: Optional[datetime] = None,
) -> TimingDecision:
    """
    Convenience API for evaluating one timing observation.
    """

    engine = TimingEngine(
        policy=policy,
        expected_market_id=expected_market_id,
    )

    return engine.evaluate(
        snapshot,
        expected_market_id=expected_market_id,
        now=now,
    )


def filter_timing(
    snapshots: Iterable[Any],
    policy: Optional[TimingPolicy] = None,
    *,
    expected_market_id: Optional[str] = None,
    now: Optional[datetime] = None,
    include_review: bool = False,
) -> List[TimingDecision]:
    """
    Convenience API for Opportunity Discovery.

    Returns PASS decisions by default.

    include_review=True returns:
        PASS + REVIEW
    """

    engine = TimingEngine(
        policy=policy,
        expected_market_id=expected_market_id,
    )

    return engine.apply(
        snapshots,
        expected_market_id=expected_market_id,
        now=now,
        include_review=include_review,
    )


# ---------------------------------------------------------------------------
# SELF TEST
# ---------------------------------------------------------------------------

def _self_test() -> None:
    """
    Deterministic contract tests.

    These tests validate implementation behavior.
    They do not claim market-performance accuracy.
    """

    test_time = datetime(
        2026,
        9,
        5,
        10,
        0,
        0,
        tzinfo=timezone.utc,
    )

    # -------------------------------------------------------------------
    # Test 1: Configured active window
    # -------------------------------------------------------------------

    policy = TimingPolicy(
        windows=[
            TimingWindow(
                name="PRIMARY",
                start=time(9, 15),
                end=time(11, 30),
                priority=10,
            )
        ],
        policy_version="TEST-1",
    )

    engine = TimingEngine(
        policy=policy,
        expected_market_id="NSE",
    )

    snapshot = TimingSnapshot(
        instrument_id="NIFTY",
        symbol="NIFTY",
        market_id="NSE",
        timestamp=test_time,
        current_time=time(10, 0),
        session_state=SessionState.OPEN,
        market_open=True,
        is_trading_day=True,
        minutes_from_open=45,
        minutes_to_close=330,
    )

    decision = engine.evaluate(
        snapshot,
        now=test_time,
    )

    assert decision.status == TimingStatus.PASS
    assert decision.window_name == "PRIMARY"

    # -------------------------------------------------------------------
    # Test 2: Outside window with REVIEW policy
    # -------------------------------------------------------------------

    policy = TimingPolicy(
        windows=[
            TimingWindow(
                name="PRIMARY",
                start=time(9, 15),
                end=time(11, 30),
            )
        ],
        review_outside_window=True,
        reject_outside_window=False,
        policy_version="TEST-2",
    )

    engine = TimingEngine(
        policy=policy,
        expected_market_id="NSE",
    )

    outside = TimingSnapshot(
        instrument_id="TEST1",
        symbol="TEST1",
        market_id="NSE",
        timestamp=test_time,
        current_time=time(13, 0),
        session_state=SessionState.MID_SESSION,
    )

    decision = engine.evaluate(
        outside,
        now=test_time,
    )

    assert decision.status == TimingStatus.REVIEW
    assert decision.condition == TimingCondition.OUTSIDE_WINDOW

    # -------------------------------------------------------------------
    # Test 3: Outside window hard rejection
    # -------------------------------------------------------------------

    policy = TimingPolicy(
        windows=[
            TimingWindow(
                name="PRIMARY",
                start=time(9, 15),
                end=time(11, 30),
            )
        ],
        review_outside_window=False,
        reject_outside_window=True,
        policy_version="TEST-3",
    )

    engine = TimingEngine(
        policy=policy,
        expected_market_id="NSE",
    )

    decision = engine.evaluate(
        outside,
        now=test_time,
    )

    assert decision.status == TimingStatus.REJECT

    # -------------------------------------------------------------------
    # Test 4: Event-near review
    # -------------------------------------------------------------------

    policy = TimingPolicy(
        review_event_near=True,
        reject_event_near=False,
        policy_version="TEST-4",
    )

    engine = TimingEngine(
        policy=policy,
        expected_market_id="NSE",
    )

    event_snapshot = TimingSnapshot(
        instrument_id="TEST2",
        symbol="TEST2",
        market_id="NSE",
        timestamp=test_time,
        current_time=time(10, 0),
        session_state=SessionState.OPEN,
        event_near=True,
    )

    decision = engine.evaluate(
        event_snapshot,
        now=test_time,
    )

    assert decision.status == TimingStatus.REVIEW
    assert decision.condition == TimingCondition.EVENT_NEAR

    # -------------------------------------------------------------------
    # Test 5: Expiry hard rejection
    # -------------------------------------------------------------------

    policy = TimingPolicy(
        review_expiry_near=False,
        reject_expiry_near=True,
        policy_version="TEST-5",
    )

    engine = TimingEngine(
        policy=policy,
        expected_market_id="NSE",
    )

    expiry_snapshot = TimingSnapshot(
        instrument_id="TEST3",
        symbol="TEST3",
        market_id="NSE",
        timestamp=test_time,
        current_time=time(10, 0),
        session_state=SessionState.OPEN,
        expiry_near=True,
    )

    decision = engine.evaluate(
        expiry_snapshot,
        now=test_time,
    )

    assert decision.status == TimingStatus.REJECT

    # -------------------------------------------------------------------
    # Test 6: Near close review
    # -------------------------------------------------------------------

    policy = TimingPolicy(
        review_before_close_minutes=30,
        reject_before_close_minutes=None,
        policy_version="TEST-6",
    )

    engine = TimingEngine(
        policy=policy,
        expected_market_id="NSE",
    )

    near_close = TimingSnapshot(
        instrument_id="TEST4",
        symbol="TEST4",
        market_id="NSE",
        timestamp=test_time,
        current_time=time(15, 20),
        session_state=SessionState.CLOSING,
        minutes_to_close=20,
    )

    decision = engine.evaluate(
        near_close,
        now=test_time,
    )

    assert decision.status == TimingStatus.REVIEW
    assert decision.condition == TimingCondition.LATE

    # -------------------------------------------------------------------
    # Test 7: Market identity mismatch
    # -------------------------------------------------------------------

    mismatch = TimingSnapshot(
        instrument_id="TEST5",
        symbol="TEST5",
        market_id="BSE",
        timestamp=test_time,
        current_time=time(10, 0),
        session_state=SessionState.OPEN,
    )

    decision = engine.evaluate(
        mismatch,
        now=test_time,
    )

    assert decision.status == TimingStatus.REJECT
    assert "Market identity mismatch" in decision.reasons

    # -------------------------------------------------------------------
    # Test 8: Future data rejection
    # -------------------------------------------------------------------

    future = TimingSnapshot(
        instrument_id="TEST6",
        symbol="TEST6",
        market_id="NSE",
        timestamp=datetime(
            2026,
            9,
            5,
            11,
            0,
            0,
            tzinfo=timezone.utc,
        ),
        current_time=time(11, 0),
        session_state=SessionState.OPEN,
    )

    decision = engine.evaluate(
        future,
        now=test_time,
    )

    assert decision.status == TimingStatus.REJECT

    # -------------------------------------------------------------------
    # Test 9: Unknown timing
    # -------------------------------------------------------------------

    unknown = TimingSnapshot(
        instrument_id="TEST7",
        symbol="TEST7",
        market_id="NSE",
        timestamp=test_time,
    )

    decision = engine.evaluate(
        unknown,
        now=test_time,
    )

    assert decision.status == TimingStatus.UNKNOWN

    # -------------------------------------------------------------------
    # Test 10: Overnight window
    # -------------------------------------------------------------------

    overnight = TimingWindow(
        name="OVERNIGHT",
        start=time(22, 0),
        end=time(5, 0),
    )

    assert overnight.contains(time(23, 0))
    assert overnight.contains(time(2, 0))
    assert not overnight.contains(time(12, 0))

    # -------------------------------------------------------------------
    # Test 11: Collection
    # -------------------------------------------------------------------

    policy = TimingPolicy(
        windows=[
            TimingWindow(
                name="PRIMARY",
                start=time(9, 15),
                end=time(11, 30),
            )
        ],
        review_outside_window=True,
        policy_version="TEST-11",
    )

    engine = TimingEngine(
        policy=policy,
        expected_market_id="NSE",
    )

    collection = [
        TimingSnapshot(
            instrument_id="A",
            symbol="A",
            market_id="NSE",
            timestamp=test_time,
            current_time=time(10, 0),
            session_state=SessionState.OPEN,
        ),
        TimingSnapshot(
            instrument_id="B",
            symbol="B",
            market_id="NSE",
            timestamp=test_time,
            current_time=time(13, 0),
            session_state=SessionState.MID_SESSION,
        ),
    ]

    result = engine.filter(
        collection,
        now=test_time,
    )

    assert result.total == 2
    assert len(result.passed) == 1
    assert len(result.review) == 1

    # -------------------------------------------------------------------
    # Test 12: Serialization
    # -------------------------------------------------------------------

    serialized = engine.result_to_dict(result)

    assert serialized["total"] == 2

    assert isinstance(
        serialized["passed"],
        list,
    )

    assert isinstance(
        serialized["review"],
        list,
    )

    print("timing_engine.py self-test: PASS")


if __name__ == "__main__":
    _self_test()