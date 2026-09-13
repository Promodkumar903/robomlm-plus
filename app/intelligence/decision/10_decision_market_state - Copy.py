"""
ROBOMLM_PLUS
Decision Layer — D10: Market State

D10 responsibility:
    MARKET STATE

Position in D1-D16:
    D1  Market Identity
    D2  Data Contract
    D3  Trust
    D4  Relationships
    D5  Structure
    D6  Flow
    D7  Liquidity / Volatility
    D8  Instrument Mechanics
    D9  Time / Event
    D10 Market State
    D11 Transition
    D12 Future / Scenario
    D13 Decision
    D14 Validation
    D15 Learning
    D16 Intelligence

D10 converts validated current observations into a
descriptive market-state representation.

IMPORTANT:
    - No arbitrary 0-100 score.
    - No fabricated proprietary V6 formula.
    - State != prediction.
    - State != decision.
    - Transition belongs to D11.
    - Scenario belongs to D12.
    - Decision belongs to D13.
    - Future information is prohibited.
    - Missing information is explicitly represented.
    - Observed and derived values remain distinguishable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import isfinite
from typing import Any, Dict, List, Optional


# ============================================================
# ENUMS
# ============================================================

class D10Status(str, Enum):
    READY = "READY"
    LIMITED = "LIMITED"
    BLOCKED = "BLOCKED"


class MarketState(str, Enum):
    UNKNOWN = "UNKNOWN"

    TRENDING_UP = "TRENDING_UP"
    TRENDING_DOWN = "TRENDING_DOWN"

    RANGE = "RANGE"
    BALANCED = "BALANCED"

    BREAKOUT = "BREAKOUT"
    BREAKDOWN = "BREAKDOWN"

    HIGH_VOLATILITY = "HIGH_VOLATILITY"
    LOW_VOLATILITY = "LOW_VOLATILITY"

    ILLIQUID = "ILLIQUID"

    EVENT_DRIVEN = "EVENT_DRIVEN"


class EvidenceKind(str, Enum):
    OBSERVED = "OBSERVED"
    DERIVED = "DERIVED"


# ============================================================
# INPUT DATA
# ============================================================

@dataclass(frozen=True)
class StateObservation:
    """
    One current-state observation.

    Examples:
        price
        return
        realized_volatility
        spread_bps
        depth_imbalance
        trend_measure
        range_measure
        volume_relative
    """

    name: str
    value: float

    timestamp: Any
    source: str

    kind: EvidenceKind = EvidenceKind.OBSERVED

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class D10MarketStateResult:
    status: D10Status

    state: MarketState

    as_of: Optional[Any]

    observations_used: List[str]

    missing_requirements: List[str]

    conflicts: List[str]

    future_data_detected: bool

    stale_data_detected: bool

    evidence: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# ENGINE
# ============================================================

class D10MarketStateEngine:
    """
    D10 descriptive state engine.

    Thresholds are supplied by the caller/profile rather than
    being silently invented as universal V6 constants.

    This keeps market-specific calibration/profile logic outside
    the structural D10 implementation.
    """

    REQUIRED_FIELDS = {
        "price",
    }

    OPTIONAL_FIELDS = {
        "trend_measure",
        "return",
        "realized_volatility",
        "spread_bps",
        "depth_imbalance",
        "range_measure",
        "volume_relative",
        "event_active",
    }

    def __init__(
        self,
        *,
        thresholds: Optional[Dict[str, float]] = None,
        max_age_seconds: Optional[float] = None,
    ) -> None:

        self.thresholds = dict(thresholds or {})
        self.max_age_seconds = max_age_seconds

        if max_age_seconds is not None:
            if max_age_seconds < 0:
                raise ValueError(
                    "max_age_seconds cannot be negative"
                )

    # --------------------------------------------------------
    # NUMERIC VALIDATION
    # --------------------------------------------------------

    @staticmethod
    def _valid_number(value: Any) -> bool:
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and isfinite(float(value))
        )

    # --------------------------------------------------------
    # TIME NORMALIZATION
    # --------------------------------------------------------

    @staticmethod
    def _seconds_difference(
        current: Any,
        previous: Any,
    ) -> float:

        delta = current - previous

        if hasattr(delta, "total_seconds"):
            return float(delta.total_seconds())

        return float(delta)

    # --------------------------------------------------------
    # OBSERVATION VALIDATION
    # --------------------------------------------------------

    def validate_observation(
        self,
        observation: StateObservation,
        *,
        as_of: Any,
    ) -> Optional[str]:

        if not observation.name:
            return "EMPTY_OBSERVATION_NAME"

        if not self._valid_number(observation.value):
            return (
                f"INVALID_VALUE:{observation.name}"
            )

        # Future observation guard.
        try:
            age = self._seconds_difference(
                as_of,
                observation.timestamp,
            )

            if age < 0:
                return (
                    f"FUTURE_DATA:{observation.name}"
                )

            if (
                self.max_age_seconds is not None
                and age > self.max_age_seconds
            ):
                return (
                    f"STALE_DATA:{observation.name}"
                )

        except Exception:
            return (
                f"INVALID_TIMESTAMP:{observation.name}"
            )

        return None

    # --------------------------------------------------------
    # CONFLICT DETECTION
    # --------------------------------------------------------

    @staticmethod
    def detect_conflicts(
        observations: List[StateObservation],
    ) -> List[str]:

        grouped: Dict[str, List[StateObservation]] = {}

        for obs in observations:
            grouped.setdefault(
                obs.name,
                []
            ).append(obs)

        conflicts: List[str] = []

        for name, items in grouped.items():

            if len(items) < 2:
                continue

            values = {
                float(item.value)
                for item in items
            }

            # Conflict is only established when explicitly
            # declared by source metadata.
            explicit_conflicts = [
                bool(
                    item.metadata.get(
                        "conflict",
                        False,
                    )
                )
                for item in items
            ]

            if any(explicit_conflicts):
                conflicts.append(
                    f"OBSERVATION_CONFLICT:{name}"
                )
                continue

            # Multiple different values from different sources
            # are surfaced, not silently averaged.
            if len(values) > 1:

                sources = {
                    item.source
                    for item in items
                }

                if len(sources) > 1:
                    conflicts.append(
                        f"SOURCE_VALUE_CONFLICT:{name}"
                    )

        return conflicts

    # --------------------------------------------------------
    # PROFILE THRESHOLD
    # --------------------------------------------------------

    def threshold(
        self,
        name: str,
    ) -> Optional[float]:

        value = self.thresholds.get(name)

        if value is None:
            return None

        if not self._valid_number(value):
            raise ValueError(
                f"Invalid threshold: {name}"
            )

        return float(value)

    # --------------------------------------------------------
    # CURRENT OBSERVATION MAP
    # --------------------------------------------------------

    @staticmethod
    def _observation_map(
        observations: List[StateObservation],
    ) -> Dict[str, StateObservation]:

        result: Dict[str, StateObservation] = {}

        for obs in observations:

            # Do not silently overwrite a conflicting value.
            if obs.name in result:
                continue

            result[obs.name] = obs

        return result

    # --------------------------------------------------------
    # STATE CLASSIFICATION
    # --------------------------------------------------------

    def classify(
        self,
        observation_map: Dict[str, StateObservation],
    ) -> MarketState:

        # ----------------------------------------------------
        # EVENT-DRIVEN STATE
        # ----------------------------------------------------

        event_obs = observation_map.get(
            "event_active"
        )

        if event_obs is not None:

            if bool(event_obs.value):
                return MarketState.EVENT_DRIVEN

        # ----------------------------------------------------
        # LIQUIDITY STATE
        # ----------------------------------------------------

        spread = observation_map.get(
            "spread_bps"
        )

        illiquid_threshold = self.threshold(
            "illiquid_spread_bps"
        )

        if (
            spread is not None
            and illiquid_threshold is not None
            and spread.value >= illiquid_threshold
        ):
            return MarketState.ILLIQUID

        # ----------------------------------------------------
        # VOLATILITY STATE
        # ----------------------------------------------------

        volatility = observation_map.get(
            "realized_volatility"
        )

        high_vol_threshold = self.threshold(
            "high_volatility"
        )

        low_vol_threshold = self.threshold(
            "low_volatility"
        )

        if (
            volatility is not None
            and high_vol_threshold is not None
            and volatility.value >= high_vol_threshold
        ):
            return MarketState.HIGH_VOLATILITY

        if (
            volatility is not None
            and low_vol_threshold is not None
            and volatility.value <= low_vol_threshold
        ):
            return MarketState.LOW_VOLATILITY

        # ----------------------------------------------------
        # TREND STATE
        # ----------------------------------------------------

        trend = observation_map.get(
            "trend_measure"
        )

        trend_up_threshold = self.threshold(
            "trend_up"
        )

        trend_down_threshold = self.threshold(
            "trend_down"
        )

        if (
            trend is not None
            and trend_up_threshold is not None
            and trend.value >= trend_up_threshold
        ):
            return MarketState.TRENDING_UP

        if (
            trend is not None
            and trend_down_threshold is not None
            and trend.value <= trend_down_threshold
        ):
            return MarketState.TRENDING_DOWN

        # ----------------------------------------------------
        # RANGE / BALANCE
        # ----------------------------------------------------

        range_measure = observation_map.get(
            "range_measure"
        )

        range_threshold = self.threshold(
            "range_threshold"
        )

        if (
            range_measure is not None
            and range_threshold is not None
            and range_measure.value <= range_threshold
        ):
            return MarketState.RANGE

        # If no calibrated classification can be established,
        # remain UNKNOWN rather than inventing a state.
        return MarketState.UNKNOWN

    # --------------------------------------------------------
    # MAIN EVALUATION
    # --------------------------------------------------------

    def evaluate(
        self,
        *,
        as_of: Any,
        observations: List[StateObservation],
    ) -> D10MarketStateResult:

        missing: List[str] = []
        conflicts: List[str] = []

        valid_observations: List[
            StateObservation
        ] = []

        future_data = False
        stale_data = False

        # ----------------------------------------------------
        # VALIDATE OBSERVATIONS
        # ----------------------------------------------------

        for observation in observations:

            error = self.validate_observation(
                observation,
                as_of=as_of,
            )

            if error is None:
                valid_observations.append(
                    observation
                )
                continue

            if error.startswith("FUTURE_DATA:"):
                future_data = True

            if error.startswith("STALE_DATA:"):
                stale_data = True

            if error.startswith("STALE_DATA:"):
                missing.append(error)
            else:
                conflicts.append(error)

        # ----------------------------------------------------
        # FUTURE DATA = HARD BLOCK
        # ----------------------------------------------------

        if future_data:

            return D10MarketStateResult(
                status=D10Status.BLOCKED,
                state=MarketState.UNKNOWN,
                as_of=as_of,
                observations_used=[],
                missing_requirements=[],
                conflicts=conflicts,
                future_data_detected=True,
                stale_data_detected=stale_data,
            )

        # ----------------------------------------------------
        # CONFLICTS
        # ----------------------------------------------------

        conflicts.extend(
            self.detect_conflicts(
                valid_observations
            )
        )

        if conflicts:

            return D10MarketStateResult(
                status=D10Status.BLOCKED,
                state=MarketState.UNKNOWN,
                as_of=as_of,
                observations_used=[],
                missing_requirements=missing,
                conflicts=conflicts,
                future_data_detected=False,
                stale_data_detected=stale_data,
            )

        # ----------------------------------------------------
        # OBSERVATION MAP
        # ----------------------------------------------------

        observation_map = self._observation_map(
            valid_observations
        )

        # ----------------------------------------------------
        # REQUIRED DATA
        # ----------------------------------------------------

        for field_name in self.REQUIRED_FIELDS:

            if field_name not in observation_map:
                missing.append(
                    f"REQUIRED:{field_name}"
                )

        if missing:

            return D10MarketStateResult(
                status=D10Status.LIMITED,
                state=MarketState.UNKNOWN,
                as_of=as_of,
                observations_used=list(
                    observation_map.keys()
                ),
                missing_requirements=missing,
                conflicts=[],
                future_data_detected=False,
                stale_data_detected=stale_data,
            )

        # ----------------------------------------------------
        # CLASSIFY CURRENT STATE
        # ----------------------------------------------------

        state = self.classify(
            observation_map
        )

        used = list(
            observation_map.keys()
        )

        # ----------------------------------------------------
        # UNKNOWN STATE IS NOT A FAILURE
        # ----------------------------------------------------

        if state == MarketState.UNKNOWN:

            return D10MarketStateResult(
                status=D10Status.LIMITED,
                state=MarketState.UNKNOWN,
                as_of=as_of,
                observations_used=used,
                missing_requirements=[
                    "INSUFFICIENT_STATE_CLASSIFICATION"
                ],
                conflicts=[],
                future_data_detected=False,
                stale_data_detected=stale_data,
                evidence={
                    "state_is_descriptive": True,
                    "prediction_not_performed": True,
                },
            )

        # ----------------------------------------------------
        # READY
        # ----------------------------------------------------

        status = (
            D10Status.LIMITED
            if stale_data
            else D10Status.READY
        )

        return D10MarketStateResult(
            status=status,
            state=state,
            as_of=as_of,
            observations_used=used,
            missing_requirements=missing,
            conflicts=[],
            future_data_detected=False,
            stale_data_detected=stale_data,
            evidence={
                "state_is_descriptive": True,
                "prediction_not_performed": True,
                "transition_not_performed": True,
                "scenario_not_performed": True,
                "decision_not_performed": True,
            },
        )


# ============================================================
# SELF TEST
# ============================================================

def self_test() -> None:

    from datetime import datetime, timezone, timedelta

    now = datetime(
        2026,
        1,
        1,
        10,
        0,
        tzinfo=timezone.utc,
    )

    engine = D10MarketStateEngine(
        thresholds={
            "trend_up": 0.70,
            "trend_down": -0.70,
            "high_volatility": 0.05,
            "low_volatility": 0.01,
            "illiquid_spread_bps": 50.0,
            "range_threshold": 0.20,
        },
        max_age_seconds=300,
    )

    # --------------------------------------------------------
    # TEST 1 — Trending up
    # --------------------------------------------------------

    result = engine.evaluate(
        as_of=now,
        observations=[
            StateObservation(
                name="price",
                value=25000.0,
                timestamp=now,
                source="TEST",
            ),
            StateObservation(
                name="trend_measure",
                value=0.85,
                timestamp=now,
                source="TEST",
                kind=EvidenceKind.DERIVED,
            ),
        ],
    )

    assert result.status == D10Status.READY
    assert result.state == MarketState.TRENDING_UP

    # --------------------------------------------------------
    # TEST 2 — Trending down
    # --------------------------------------------------------

    result = engine.evaluate(
        as_of=now,
        observations=[
            StateObservation(
                name="price",
                value=25000.0,
                timestamp=now,
                source="TEST",
            ),
            StateObservation(
                name="trend_measure",
                value=-0.85,
                timestamp=now,
                source="TEST",
                kind=EvidenceKind.DERIVED,
            ),
        ],
    )

    assert result.status == D10Status.READY
    assert result.state == MarketState.TRENDING_DOWN

    # --------------------------------------------------------
    # TEST 3 — High volatility
    # --------------------------------------------------------

    result = engine.evaluate(
        as_of=now,
        observations=[
            StateObservation(
                name="price",
                value=25000.0,
                timestamp=now,
                source="TEST",
            ),
            StateObservation(
                name="realized_volatility",
                value=0.08,
                timestamp=now,
                source="TEST",
                kind=EvidenceKind.DERIVED,
            ),
        ],
    )

    assert result.status == D10Status.READY
    assert result.state == MarketState.HIGH_VOLATILITY

    # --------------------------------------------------------
    # TEST 4 — Illiquid
    # --------------------------------------------------------

    result = engine.evaluate(
        as_of=now,
        observations=[
            StateObservation(
                name="price",
                value=25000.0,
                timestamp=now,
                source="TEST",
            ),
            StateObservation(
                name="spread_bps",
                value=75.0,
                timestamp=now,
                source="TEST",
            ),
        ],
    )

    assert result.status == D10Status.READY
    assert result.state == MarketState.ILLIQUID

    # --------------------------------------------------------
    # TEST 5 — Event driven
    # --------------------------------------------------------

    result = engine.evaluate(
        as_of=now,
        observations=[
            StateObservation(
                name="price",
                value=25000.0,
                timestamp=now,
                source="TEST",
            ),
            StateObservation(
                name="event_active",
                value=1.0,
                timestamp=now,
                source="TEST",
            ),
        ],
    )

    assert result.status == D10Status.READY
    assert result.state == MarketState.EVENT_DRIVEN

    # --------------------------------------------------------
    # TEST 6 — Missing price
    # --------------------------------------------------------

    result = engine.evaluate(
        as_of=now,
        observations=[
            StateObservation(
                name="trend_measure",
                value=0.8,
                timestamp=now,
                source="TEST",
            )
        ],
    )

    assert result.status == D10Status.LIMITED
    assert result.state == MarketState.UNKNOWN
    assert "REQUIRED:price" in (
        result.missing_requirements
    )

    # --------------------------------------------------------
    # TEST 7 — Future data attack
    # --------------------------------------------------------

    future = now + timedelta(minutes=1)

    result = engine.evaluate(
        as_of=now,
        observations=[
            StateObservation(
                name="price",
                value=25000.0,
                timestamp=future,
                source="FUTURE",
            )
        ],
    )

    assert result.status == D10Status.BLOCKED
    assert result.future_data_detected is True
    assert result.state == MarketState.UNKNOWN

    # --------------------------------------------------------
    # TEST 8 — Stale data
    # --------------------------------------------------------

    stale_time = now - timedelta(minutes=10)

    result = engine.evaluate(
        as_of=now,
        observations=[
            StateObservation(
                name="price",
                value=25000.0,
                timestamp=stale_time,
                source="OLD",
            )
        ],
    )

    assert result.status == D10Status.LIMITED
    assert result.stale_data_detected is True

    # --------------------------------------------------------
    # TEST 9 — Source conflict
    # --------------------------------------------------------

    result = engine.evaluate(
        as_of=now,
        observations=[
            StateObservation(
                name="price",
                value=25000.0,
                timestamp=now,
                source="SOURCE_A",
            ),
            StateObservation(
                name="price",
                value=25010.0,
                timestamp=now,
                source="SOURCE_B",
            ),
        ],
    )

    assert result.status == D10Status.BLOCKED
    assert any(
        "SOURCE_VALUE_CONFLICT:price" in conflict
        for conflict in result.conflicts
    )

    # --------------------------------------------------------
    # TEST 10 — No D11/D12/D13 leakage
    # --------------------------------------------------------

    result = engine.evaluate(
        as_of=now,
        observations=[
            StateObservation(
                name="price",
                value=25000.0,
                timestamp=now,
                source="TEST",
            ),
            StateObservation(
                name="trend_measure",
                value=0.8,
                timestamp=now,
                source="TEST",
            ),
        ],
    )

    assert result.evidence[
        "transition_not_performed"
    ] is True

    assert result.evidence[
        "scenario_not_performed"
    ] is True

    assert result.evidence[
        "decision_not_performed"
    ] is True

    print("D10 SELF-TEST: PASS")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    self_test()