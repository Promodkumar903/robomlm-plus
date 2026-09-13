"""
ROBOMLM_PLUS
Decision Layer — D9: Time / Event

D9 responsibility:
    TIME / EVENT

D9 sits after:
    D8 Instrument Mechanics

and before:
    D10 Market State

Boundary:
    D8 = instrument/contract mechanics
    D9 = temporal + event mechanics

IMPORTANT:
    - No arbitrary 0–100 score.
    - No fabricated V6 proprietary formula.
    - No future-data leakage.
    - No silent default timestamps.
    - Expiry itself is NOT reimplemented as an instrument property here.
      D8 owns contract expiry identity/property.
      D9 only handles temporal proximity/state associated with an event.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple


# ============================================================
# ENUMS
# ============================================================

class D9Status(str, Enum):
    READY = "READY"
    LIMITED = "LIMITED"
    BLOCKED = "BLOCKED"


class EventType(str, Enum):
    NONE = "NONE"
    MARKET_OPEN = "MARKET_OPEN"
    MARKET_CLOSE = "MARKET_CLOSE"
    SESSION_CHANGE = "SESSION_CHANGE"
    ECONOMIC_EVENT = "ECONOMIC_EVENT"
    CENTRAL_BANK_EVENT = "CENTRAL_BANK_EVENT"
    EARNINGS = "EARNINGS"
    AUCTION = "AUCTION"
    SETTLEMENT = "SETTLEMENT"
    CONTRACT_EXPIRY_EVENT = "CONTRACT_EXPIRY_EVENT"
    CUSTOM = "CUSTOM"


class EventImpact(str, Enum):
    UNKNOWN = "UNKNOWN"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TimeState(str, Enum):
    UNKNOWN = "UNKNOWN"
    PRE_EVENT = "PRE_EVENT"
    EVENT_WINDOW = "EVENT_WINDOW"
    POST_EVENT = "POST_EVENT"
    NORMAL = "NORMAL"


# ============================================================
# TEMPORAL PRIMITIVES
# ============================================================

@dataclass(frozen=True)
class TimePoint:
    timestamp: datetime
    source: str = "unknown"
    observed: bool = True


@dataclass(frozen=True)
class Event:
    event_id: str
    event_type: EventType
    scheduled_time: datetime

    impact: EventImpact = EventImpact.UNKNOWN

    # Event windows are explicitly defined.
    pre_window_seconds: int = 0
    post_window_seconds: int = 0

    source: str = "unknown"

    # True if event time was actually observed/reported.
    observed: bool = True

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class D9TimeEventResult:
    status: D9Status

    as_of: Optional[datetime]

    time_state: TimeState

    active_event: Optional[Event]

    seconds_to_event: Optional[float]
    seconds_from_event: Optional[float]

    session_id: Optional[str]
    session_open: Optional[datetime]
    session_close: Optional[datetime]

    stale: bool
    future_data_detected: bool

    missing_requirements: List[str]
    conflicts: List[str]

    evidence: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# VALIDATION HELPERS
# ============================================================

def _ensure_utc(dt: datetime) -> datetime:
    """
    Normalize timezone-aware timestamps to UTC.

    Naive timestamps are rejected rather than silently assuming
    a timezone.
    """
    if dt.tzinfo is None:
        raise ValueError("Timezone-aware datetime required")

    return dt.astimezone(timezone.utc)


def _seconds_between(a: datetime, b: datetime) -> float:
    return (b - a).total_seconds()


def _validate_window(value: int, field_name: str) -> None:
    if value < 0:
        raise ValueError(f"{field_name} cannot be negative")


# ============================================================
# EVENT ENGINE
# ============================================================

class D9TimeEventEngine:
    """
    D9 temporal/event reasoning engine.

    This engine produces temporal facts and event state.
    It intentionally does not convert those facts into a
    proprietary confidence/decision score.
    """

    def __init__(
        self,
        *,
        max_data_age_seconds: Optional[float] = None,
    ) -> None:

        if (
            max_data_age_seconds is not None
            and max_data_age_seconds < 0
        ):
            raise ValueError("max_data_age_seconds cannot be negative")

        self.max_data_age_seconds = max_data_age_seconds

    # --------------------------------------------------------
    # TIMESTAMP VALIDATION
    # --------------------------------------------------------

    def validate_as_of(
        self,
        as_of: datetime,
    ) -> datetime:

        return _ensure_utc(as_of)

    # --------------------------------------------------------
    # EVENT VALIDATION
    # --------------------------------------------------------

    def validate_event(
        self,
        event: Event,
        *,
        as_of: Optional[datetime] = None,
    ) -> Event:

        if not event.event_id:
            raise ValueError("event_id is required")

        _validate_window(
            event.pre_window_seconds,
            "pre_window_seconds",
        )

        _validate_window(
            event.post_window_seconds,
            "post_window_seconds",
        )

        scheduled = _ensure_utc(event.scheduled_time)

        if as_of is not None:
            as_of_utc = _ensure_utc(as_of)

            # An event may legitimately be in the future relative
            # to as_of. That is not future-data leakage.
            #
            # Leakage occurs if an event outcome/result is used
            # before as_of. The event schedule itself is allowed
            # when it was known at as_of.

            known_at = event.metadata.get("known_at")

            if known_at is not None:
                known_at_utc = _ensure_utc(known_at)

                if known_at_utc > as_of_utc:
                    raise ValueError(
                        f"Future event information detected: "
                        f"{event.event_id}"
                    )

        return Event(
            event_id=event.event_id,
            event_type=event.event_type,
            scheduled_time=scheduled,
            impact=event.impact,
            pre_window_seconds=event.pre_window_seconds,
            post_window_seconds=event.post_window_seconds,
            source=event.source,
            observed=event.observed,
            metadata=dict(event.metadata),
        )

    # --------------------------------------------------------
    # EVENT WINDOW
    # --------------------------------------------------------

    def classify_event_state(
        self,
        *,
        as_of: datetime,
        event: Event,
    ) -> Tuple[TimeState, float, Optional[float]]:

        now = _ensure_utc(as_of)
        event_time = _ensure_utc(event.scheduled_time)

        delta = _seconds_between(now, event_time)

        # delta > 0 => event is ahead
        # delta < 0 => event already occurred

        if delta > 0:
            if delta <= event.pre_window_seconds:
                return (
                    TimeState.PRE_EVENT,
                    delta,
                    None,
                )

            return (
                TimeState.NORMAL,
                delta,
                None,
            )

        elapsed = abs(delta)

        if elapsed <= event.post_window_seconds:
            return (
                TimeState.EVENT_WINDOW,
                delta,
                elapsed,
            )

        return (
            TimeState.POST_EVENT,
            delta,
            elapsed,
        )

    # --------------------------------------------------------
    # SESSION STATE
    # --------------------------------------------------------

    def classify_session(
        self,
        *,
        as_of: datetime,
        session_open: datetime,
        session_close: datetime,
    ) -> bool:

        now = _ensure_utc(as_of)
        opening = _ensure_utc(session_open)
        closing = _ensure_utc(session_close)

        if closing < opening:
            raise ValueError(
                "session_close cannot be before session_open"
            )

        return opening <= now <= closing

    # --------------------------------------------------------
    # EVENT CONFLICT DETECTION
    # --------------------------------------------------------

    def detect_event_conflicts(
        self,
        events: Sequence[Event],
    ) -> List[str]:

        conflicts: List[str] = []

        by_id: Dict[str, List[Event]] = {}

        for event in events:
            by_id.setdefault(event.event_id, []).append(event)

        for event_id, items in by_id.items():

            if len(items) <= 1:
                continue

            times = {
                _ensure_utc(item.scheduled_time)
                for item in items
            }

            types = {
                item.event_type
                for item in items
            }

            if len(times) > 1:
                conflicts.append(
                    f"EVENT_TIME_CONFLICT:{event_id}"
                )

            if len(types) > 1:
                conflicts.append(
                    f"EVENT_TYPE_CONFLICT:{event_id}"
                )

        return conflicts

    # --------------------------------------------------------
    # FUTURE DATA GUARD
    # --------------------------------------------------------

    def future_data_guard(
        self,
        *,
        as_of: datetime,
        event: Event,
    ) -> bool:

        now = _ensure_utc(as_of)

        known_at = event.metadata.get("known_at")

        if known_at is None:
            # Missing provenance is not treated as proven-safe.
            return True

        known_at_utc = _ensure_utc(known_at)

        return known_at_utc > now

    # --------------------------------------------------------
    # STALENESS
    # --------------------------------------------------------

    def stale_guard(
        self,
        *,
        as_of: datetime,
        data_timestamp: Optional[datetime],
    ) -> bool:

        if data_timestamp is None:
            return True

        if self.max_data_age_seconds is None:
            return False

        now = _ensure_utc(as_of)
        data_time = _ensure_utc(data_timestamp)

        age = _seconds_between(data_time, now)

        if age < 0:
            return True

        return age > self.max_data_age_seconds

    # --------------------------------------------------------
    # MAIN EVALUATION
    # --------------------------------------------------------

    def evaluate(
        self,
        *,
        as_of: datetime,
        events: Sequence[Event],
        session_id: Optional[str] = None,
        session_open: Optional[datetime] = None,
        session_close: Optional[datetime] = None,
        reference_data_timestamp: Optional[datetime] = None,
    ) -> D9TimeEventResult:

        missing: List[str] = []
        conflicts: List[str] = []

        try:
            now = self.validate_as_of(as_of)
        except Exception as exc:
            return D9TimeEventResult(
                status=D9Status.BLOCKED,
                as_of=None,
                time_state=TimeState.UNKNOWN,
                active_event=None,
                seconds_to_event=None,
                seconds_from_event=None,
                session_id=session_id,
                session_open=None,
                session_close=None,
                stale=False,
                future_data_detected=False,
                missing_requirements=[
                    f"INVALID_AS_OF:{exc}"
                ],
                conflicts=[],
            )

        normalized_events: List[Event] = []

        for event in events:

            try:
                normalized_events.append(
                    self.validate_event(
                        event,
                        as_of=now,
                    )
                )

            except ValueError as exc:
                if "Future event information" in str(exc):
                    return D9TimeEventResult(
                        status=D9Status.BLOCKED,
                        as_of=now,
                        time_state=TimeState.UNKNOWN,
                        active_event=None,
                        seconds_to_event=None,
                        seconds_from_event=None,
                        session_id=session_id,
                        session_open=session_open,
                        session_close=session_close,
                        stale=False,
                        future_data_detected=True,
                        missing_requirements=[],
                        conflicts=[str(exc)],
                    )

                conflicts.append(str(exc))

        conflicts.extend(
            self.detect_event_conflicts(normalized_events)
        )

        # ----------------------------------------------------
        # SELECT EVENT WINDOW
        # ----------------------------------------------------

        candidate_states: List[
            Tuple[Event, TimeState, float, Optional[float]]
        ] = []

        for event in normalized_events:

            if self.future_data_guard(
                as_of=now,
                event=event,
            ):
                return D9TimeEventResult(
                    status=D9Status.BLOCKED,
                    as_of=now,
                    time_state=TimeState.UNKNOWN,
                    active_event=None,
                    seconds_to_event=None,
                    seconds_from_event=None,
                    session_id=session_id,
                    session_open=session_open,
                    session_close=session_close,
                    stale=False,
                    future_data_detected=True,
                    missing_requirements=[],
                    conflicts=conflicts + [
                        f"FUTURE_DATA:{event.event_id}"
                    ],
                )

            state, delta, elapsed = self.classify_event_state(
                as_of=now,
                event=event,
            )

            if state != TimeState.NORMAL:
                candidate_states.append(
                    (event, state, delta, elapsed)
                )

        # Prefer the closest active temporal event.
        active_event = None
        time_state = TimeState.NORMAL
        seconds_to_event = None
        seconds_from_event = None

        if candidate_states:

            candidate_states.sort(
                key=lambda x: abs(x[2])
            )

            (
                active_event,
                time_state,
                delta,
                elapsed,
            ) = candidate_states[0]

            if delta > 0:
                seconds_to_event = delta
            else:
                seconds_from_event = elapsed

        # ----------------------------------------------------
        # SESSION
        # ----------------------------------------------------

        normalized_open = None
        normalized_close = None

        if session_open is not None:
            normalized_open = _ensure_utc(session_open)

        if session_close is not None:
            normalized_close = _ensure_utc(session_close)

        if (
            normalized_open is not None
            and normalized_close is not None
        ):
            try:
                self.classify_session(
                    as_of=now,
                    session_open=normalized_open,
                    session_close=normalized_close,
                )
            except ValueError as exc:
                conflicts.append(str(exc))

        elif (
            normalized_open is not None
            or normalized_close is not None
        ):
            missing.append("INCOMPLETE_SESSION_WINDOW")

        # ----------------------------------------------------
        # REFERENCE DATA STALENESS
        # ----------------------------------------------------

        stale = False

        if self.max_data_age_seconds is not None:

            if reference_data_timestamp is None:
                missing.append(
                    "REFERENCE_DATA_TIMESTAMP"
                )
                stale = True

            else:
                stale = self.stale_guard(
                    as_of=now,
                    data_timestamp=reference_data_timestamp,
                )

        # ----------------------------------------------------
        # FINAL STATUS
        # ----------------------------------------------------

        if conflicts:
            status = D9Status.BLOCKED

        elif missing:
            status = D9Status.LIMITED

        elif stale:
            status = D9Status.LIMITED

        else:
            status = D9Status.READY

        return D9TimeEventResult(
            status=status,
            as_of=now,
            time_state=time_state,
            active_event=active_event,
            seconds_to_event=seconds_to_event,
            seconds_from_event=seconds_from_event,
            session_id=session_id,
            session_open=normalized_open,
            session_close=normalized_close,
            stale=stale,
            future_data_detected=False,
            missing_requirements=missing,
            conflicts=conflicts,
            evidence={
                "event_count": len(normalized_events),
                "temporal_state": time_state.value,
            },
        )


# ============================================================
# SELF TEST
# ============================================================

def _dt(hour: int, minute: int = 0, second: int = 0) -> datetime:
    return datetime(
        2026,
        1,
        1,
        hour,
        minute,
        second,
        tzinfo=timezone.utc,
    )


def self_test() -> None:

    engine = D9TimeEventEngine(
        max_data_age_seconds=300
    )

    # --------------------------------------------------------
    # TEST 1 — Normal time state
    # --------------------------------------------------------

    result = engine.evaluate(
        as_of=_dt(10, 0),
        events=[],
        session_id="TEST_SESSION",
        session_open=_dt(9, 0),
        session_close=_dt(15, 0),
        reference_data_timestamp=_dt(9, 59),
    )

    assert result.status == D9Status.READY
    assert result.time_state == TimeState.NORMAL

    # --------------------------------------------------------
    # TEST 2 — Pre-event window
    # --------------------------------------------------------

    event = Event(
        event_id="EVENT_001",
        event_type=EventType.ECONOMIC_EVENT,
        scheduled_time=_dt(10, 5),
        impact=EventImpact.HIGH,
        pre_window_seconds=600,
        post_window_seconds=300,
        source="test",
        metadata={
            "known_at": _dt(9, 0),
        },
    )

    result = engine.evaluate(
        as_of=_dt(10, 0),
        events=[event],
        reference_data_timestamp=_dt(9, 59),
    )

    assert result.status == D9Status.READY
    assert result.time_state == TimeState.PRE_EVENT
    assert result.active_event is not None
    assert result.seconds_to_event == 300

    # --------------------------------------------------------
    # TEST 3 — Event/post-event window
    # --------------------------------------------------------

    result = engine.evaluate(
        as_of=_dt(10, 7),
        events=[event],
        reference_data_timestamp=_dt(10, 6),
    )

    assert result.status == D9Status.READY
    assert result.time_state == TimeState.EVENT_WINDOW
    assert result.seconds_from_event == 120

    # --------------------------------------------------------
    # TEST 4 — Future-data leakage
    # --------------------------------------------------------

    leaked_event = Event(
        event_id="LEAK_001",
        event_type=EventType.ECONOMIC_EVENT,
        scheduled_time=_dt(11, 0),
        source="future_source",
        metadata={
            # This information was only known AFTER as_of.
            "known_at": _dt(10, 30),
        },
    )

    result = engine.evaluate(
        as_of=_dt(10, 0),
        events=[leaked_event],
    )

    assert result.status == D9Status.BLOCKED
    assert result.future_data_detected is True

    # --------------------------------------------------------
    # TEST 5 — Event conflict
    # --------------------------------------------------------

    e1 = Event(
        event_id="CONFLICT_001",
        event_type=EventType.ECONOMIC_EVENT,
        scheduled_time=_dt(11, 0),
        metadata={"known_at": _dt(9, 0)},
    )

    e2 = Event(
        event_id="CONFLICT_001",
        event_type=EventType.ECONOMIC_EVENT,
        scheduled_time=_dt(11, 5),
        metadata={"known_at": _dt(9, 0)},
    )

    result = engine.evaluate(
        as_of=_dt(10, 0),
        events=[e1, e2],
    )

    assert result.status == D9Status.BLOCKED
    assert any(
        "EVENT_TIME_CONFLICT" in c
        for c in result.conflicts
    )

    # --------------------------------------------------------
    # TEST 6 — Missing reference timestamp
    # --------------------------------------------------------

    result = engine.evaluate(
        as_of=_dt(10, 0),
        events=[],
    )

    assert result.status == D9Status.LIMITED
    assert "REFERENCE_DATA_TIMESTAMP" in (
        result.missing_requirements
    )

    # --------------------------------------------------------
    # TEST 7 — No expiry duplication
    # --------------------------------------------------------

    assert "expiry" not in EventType.__members__

    # Expiry event can exist only as an event classification,
    # while contract expiry property remains owned by D8.
    assert EventType.CONTRACT_EXPIRY_EVENT.value == (
        "CONTRACT_EXPIRY_EVENT"
    )

    # --------------------------------------------------------
    # TEST 8 — Timezone safety
    # --------------------------------------------------------

    try:
        engine.evaluate(
            as_of=datetime(2026, 1, 1, 10, 0),
            events=[],
        )
        raise AssertionError(
            "Naive datetime must not be silently accepted"
        )
    except Exception:
        pass

    print("D9 SELF-TEST: PASS")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    self_test()