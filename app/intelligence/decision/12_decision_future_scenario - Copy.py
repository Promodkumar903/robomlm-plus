
ROBOMLM_PLUS
Decision Layer — D12: Future / Scenario

D12 responsibility:
    FUTURE / SCENARIO

Boundary:
    D10 = Current Market State
    D11 = Transition
    D12 = Future / Scenario
    D13 = Decision
    D14 = Validation

D12 creates explicit forward scenarios from information available
at the decision timestamp.

IMPORTANT:
    - No future observed data.
    - No outcome leakage.
    - Scenario != prediction fact.
    - Scenario != decision.
    - No fabricated universal probability.
    - No arbitrary 0-100 score.
    - No silent scenario selection.
    - Every scenario carries provenance.
    - Future outcome validation belongs to D14.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple


# ============================================================
# ENUMS
# ============================================================

class D12Status(str, Enum):
    READY = "READY"
    LIMITED = "LIMITED"
    BLOCKED = "BLOCKED"


class ScenarioType(str, Enum):
    CONTINUATION = "CONTINUATION"
    REVERSAL = "REVERSAL"
    RANGE = "RANGE"
    BREAKOUT = "BREAKOUT"
    BREAKDOWN = "BREAKDOWN"
    EVENT_RESPONSE = "EVENT_RESPONSE"
    VOLATILITY_EXPANSION = "VOLATILITY_EXPANSION"
    VOLATILITY_CONTRACTION = "VOLATILITY_CONTRACTION"
    UNKNOWN = "UNKNOWN"


class ScenarioHorizon(str, Enum):
    SHORT = "SHORT"
    MEDIUM = "MEDIUM"
    LONG = "LONG"


class ScenarioRole(str, Enum):
    PRIMARY = "PRIMARY"
    ALTERNATIVE = "ALTERNATIVE"
    INVALIDATION = "INVALIDATION"


# ============================================================
# CURRENT EVIDENCE
# ============================================================

@dataclass(frozen=True)
class ScenarioEvidence:
    """
    Information available at T0.

    D12 is only allowed to use information whose timestamp
    is <= as_of.
    """

    name: str
    value: Any
    timestamp: Any
    source: str

    observed: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# SCENARIO
# ============================================================

@dataclass
class Scenario:
    scenario_id: str

    scenario_type: ScenarioType

    horizon: ScenarioHorizon

    role: ScenarioRole

    # Human-readable structural condition.
    condition: str

    # What would support the scenario.
    supporting_evidence: List[str]

    # What would invalidate the scenario.
    invalidation_conditions: List[str]

    # Optional calibrated probability supplied externally.
    # D12 does NOT invent one.
    probability: Optional[float] = None

    probability_source: Optional[str] = None

    provenance: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# RESULT
# ============================================================

@dataclass
class D12ScenarioResult:
    status: D12Status

    as_of: Optional[Any]

    market_id: Optional[str]

    scenarios: List[Scenario]

    current_state: Optional[str]

    transition_type: Optional[str]

    missing_requirements: List[str]

    conflicts: List[str]

    future_data_detected: bool

    evidence: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# ENGINE
# ============================================================

class D12FutureScenarioEngine:
    """
    D12 scenario construction engine.

    It converts current state + transition + current evidence
    into explicit possible future paths.

    It does NOT claim that any scenario will occur.
    """

    def __init__(
        self,
        *,
        allow_external_probabilities: bool = True,
    ) -> None:

        self.allow_external_probabilities = (
            allow_external_probabilities
        )

    # --------------------------------------------------------
    # FUTURE DATA GUARD
    # --------------------------------------------------------

    @staticmethod
    def future_data_guard(
        *,
        as_of: Any,
        evidence: ScenarioEvidence,
    ) -> bool:

        try:
            delta = (
                as_of
                - evidence.timestamp
            )

            if hasattr(delta, "total_seconds"):
                seconds = float(
                    delta.total_seconds()
                )
            else:
                seconds = float(delta)

            return seconds < 0

        except Exception:
            # If temporal provenance cannot be established,
            # do not silently accept the evidence.
            return True

    # --------------------------------------------------------
    # EVIDENCE VALIDATION
    # --------------------------------------------------------

    def validate_evidence(
        self,
        *,
        as_of: Any,
        evidence: Sequence[ScenarioEvidence],
    ) -> Tuple[
        List[ScenarioEvidence],
        List[str],
        bool,
    ]:

        valid: List[ScenarioEvidence] = []
        conflicts: List[str] = []
        future_detected = False

        for item in evidence:

            if not item.name:
                conflicts.append(
                    "EMPTY_EVIDENCE_NAME"
                )
                continue

            if item.timestamp is None:
                conflicts.append(
                    f"MISSING_TIMESTAMP:{item.name}"
                )
                continue

            if self.future_data_guard(
                as_of=as_of,
                evidence=item,
            ):
                future_detected = True
                conflicts.append(
                    f"FUTURE_DATA:{item.name}"
                )
                continue

            valid.append(item)

        return (
            valid,
            conflicts,
            future_detected,
        )

    # --------------------------------------------------------
    # EVIDENCE MAP
    # --------------------------------------------------------

    @staticmethod
    def evidence_map(
        evidence: Sequence[ScenarioEvidence],
    ) -> Dict[str, ScenarioEvidence]:

        result: Dict[str, ScenarioEvidence] = {}

        for item in evidence:

            if item.name in result:
                existing = result[item.name]

                # Never silently overwrite conflicting
                # observations.
                if existing.value != item.value:
                    continue

            result[item.name] = item

        return result

    # --------------------------------------------------------
    # STATE DIRECTION
    # --------------------------------------------------------

    @staticmethod
    def state_direction(
        state: Optional[str],
    ) -> str:

        if state in (
            "TRENDING_UP",
            "BREAKOUT",
        ):
            return "UP"

        if state in (
            "TRENDING_DOWN",
            "BREAKDOWN",
        ):
            return "DOWN"

        return "NEUTRAL"

    # --------------------------------------------------------
    # BASE SCENARIO
    # --------------------------------------------------------

    def build_base_scenarios(
        self,
        *,
        current_state: str,
        transition_type: str,
        evidence: Dict[str, ScenarioEvidence],
    ) -> List[Scenario]:

        scenarios: List[Scenario] = []

        direction = self.state_direction(
            current_state
        )

        # ----------------------------------------------------
        # TREND CONTINUATION
        # ----------------------------------------------------

        if current_state == "TRENDING_UP":

            scenarios.append(
                Scenario(
                    scenario_id="SCN_CONT_UP",
                    scenario_type=(
                        ScenarioType.CONTINUATION
                    ),
                    horizon=ScenarioHorizon.SHORT,
                    role=ScenarioRole.PRIMARY,
                    condition=(
                        "Current upward state persists "
                        "without validated reversal evidence."
                    ),
                    supporting_evidence=[
                        "CURRENT_STATE:TRENDING_UP"
                    ],
                    invalidation_conditions=[
                        "Validated transition away from "
                        "upward state."
                    ],
                    provenance={
                        "constructed_from": [
                            "D10_STATE",
                            "D11_TRANSITION",
                        ]
                    },
                )
            )

            scenarios.append(
                Scenario(
                    scenario_id="SCN_REVERSAL_DOWN",
                    scenario_type=(
                        ScenarioType.REVERSAL
                    ),
                    horizon=ScenarioHorizon.SHORT,
                    role=ScenarioRole.ALTERNATIVE,
                    condition=(
                        "Current upward state transitions "
                        "toward a downward state."
                    ),
                    supporting_evidence=[],
                    invalidation_conditions=[
                        "Upward state remains intact."
                    ],
                    provenance={
                        "constructed_from": [
                            "D10_STATE",
                            "D11_TRANSITION",
                        ]
                    },
                )
            )

        # ----------------------------------------------------
        # TREND CONTINUATION DOWN
        # ----------------------------------------------------

        elif current_state == "TRENDING_DOWN":

            scenarios.append(
                Scenario(
                    scenario_id="SCN_CONT_DOWN",
                    scenario_type=(
                        ScenarioType.CONTINUATION
                    ),
                    horizon=ScenarioHorizon.SHORT,
                    role=ScenarioRole.PRIMARY,
                    condition=(
                        "Current downward state persists "
                        "without validated reversal evidence."
                    ),
                    supporting_evidence=[
                        "CURRENT_STATE:TRENDING_DOWN"
                    ],
                    invalidation_conditions=[
                        "Validated transition away from "
                        "downward state."
                    ],
                    provenance={
                        "constructed_from": [
                            "D10_STATE",
                            "D11_TRANSITION",
                        ]
                    },
                )
            )

            scenarios.append(
                Scenario(
                    scenario_id="SCN_REVERSAL_UP",
                    scenario_type=(
                        ScenarioType.REVERSAL
                    ),
                    horizon=ScenarioHorizon.SHORT,
                    role=ScenarioRole.ALTERNATIVE,
                    condition=(
                        "Current downward state transitions "
                        "toward an upward state."
                    ),
                    supporting_evidence=[],
                    invalidation_conditions=[
                        "Downward state remains intact."
                    ],
                    provenance={
                        "constructed_from": [
                            "D10_STATE",
                            "D11_TRANSITION",
                        ]
                    },
                )
            )

        # ----------------------------------------------------
        # RANGE
        # ----------------------------------------------------

        elif current_state in (
            "RANGE",
            "BALANCED",
        ):

            scenarios.append(
                Scenario(
                    scenario_id="SCN_RANGE",
                    scenario_type=ScenarioType.RANGE,
                    horizon=ScenarioHorizon.SHORT,
                    role=ScenarioRole.PRIMARY,
                    condition=(
                        "Current balanced/range state persists."
                    ),
                    supporting_evidence=[
                        f"CURRENT_STATE:{current_state}"
                    ],
                    invalidation_conditions=[
                        "Validated directional transition "
                        "or structural expansion."
                    ],
                    provenance={
                        "constructed_from": [
                            "D10_STATE"
                        ]
                    },
                )
            )

            scenarios.append(
                Scenario(
                    scenario_id="SCN_BREAKOUT",
                    scenario_type=ScenarioType.BREAKOUT,
                    horizon=ScenarioHorizon.SHORT,
                    role=ScenarioRole.ALTERNATIVE,
                    condition=(
                        "Range resolves into an upward "
                        "directional state."
                    ),
                    supporting_evidence=[],
                    invalidation_conditions=[
                        "Range remains intact."
                    ],
                    provenance={
                        "constructed_from": [
                            "D10_STATE"
                        ]
                    },
                )
            )

            scenarios.append(
                Scenario(
                    scenario_id="SCN_BREAKDOWN",
                    scenario_type=ScenarioType.BREAKDOWN,
                    horizon=ScenarioHorizon.SHORT,
                    role=ScenarioRole.ALTERNATIVE,
                    condition=(
                        "Range resolves into a downward "
                        "directional state."
                    ),
                    supporting_evidence=[],
                    invalidation_conditions=[
                        "Range remains intact."
                    ],
                    provenance={
                        "constructed_from": [
                            "D10_STATE"
                        ]
                    },
                )
            )

        # ----------------------------------------------------
        # VOLATILITY STATES
        # ----------------------------------------------------

        elif current_state == "HIGH_VOLATILITY":

            scenarios.append(
                Scenario(
                    scenario_id="SCN_VOL_CONT",
                    scenario_type=(
                        ScenarioType.VOLATILITY_EXPANSION
                    ),
                    horizon=ScenarioHorizon.SHORT,
                    role=ScenarioRole.PRIMARY,
                    condition=(
                        "Elevated volatility persists."
                    ),
                    supporting_evidence=[
                        "CURRENT_STATE:HIGH_VOLATILITY"
                    ],
                    invalidation_conditions=[
                        "Validated volatility contraction."
                    ],
                    provenance={
                        "constructed_from": [
                            "D10_STATE"
                        ]
                    },
                )
            )

            scenarios.append(
                Scenario(
                    scenario_id="SCN_VOL_CONTRACT",
                    scenario_type=(
                        ScenarioType.VOLATILITY_CONTRACTION
                    ),
                    horizon=ScenarioHorizon.MEDIUM,
                    role=ScenarioRole.ALTERNATIVE,
                    condition=(
                        "Volatility contracts from "
                        "the current elevated state."
                    ),
                    supporting_evidence=[],
                    invalidation_conditions=[
                        "Elevated volatility persists."
                    ],
                    provenance={
                        "constructed_from": [
                            "D10_STATE"
                        ]
                    },
                )
            )

        elif current_state == "LOW_VOLATILITY":

            scenarios.append(
                Scenario(
                    scenario_id="SCN_LOW_VOL_CONT",
                    scenario_type=(
                        ScenarioType.VOLATILITY_CONTRACTION
                    ),
                    horizon=ScenarioHorizon.SHORT,
                    role=ScenarioRole.PRIMARY,
                    condition=(
                        "Low-volatility state persists."
                    ),
                    supporting_evidence=[
                        "CURRENT_STATE:LOW_VOLATILITY"
                    ],
                    invalidation_conditions=[
                        "Validated volatility expansion."
                    ],
                    provenance={
                        "constructed_from": [
                            "D10_STATE"
                        ]
                    },
                )
            )

            scenarios.append(
                Scenario(
                    scenario_id="SCN_VOL_EXPAND",
                    scenario_type=(
                        ScenarioType.VOLATILITY_EXPANSION
                    ),
                    horizon=ScenarioHorizon.MEDIUM,
                    role=ScenarioRole.ALTERNATIVE,
                    condition=(
                        "Volatility expands from the "
                        "current low-volatility state."
                    ),
                    supporting_evidence=[],
                    invalidation_conditions=[
                        "Low-volatility state persists."
                    ],
                    provenance={
                        "constructed_from": [
                            "D10_STATE"
                        ]
                    },
                )
            )

        # ----------------------------------------------------
        # EVENT DRIVEN
        # ----------------------------------------------------

        elif current_state == "EVENT_DRIVEN":

            scenarios.append(
                Scenario(
                    scenario_id="SCN_EVENT_RESPONSE",
                    scenario_type=(
                        ScenarioType.EVENT_RESPONSE
                    ),
                    horizon=ScenarioHorizon.SHORT,
                    role=ScenarioRole.PRIMARY,
                    condition=(
                        "Current event-driven regime "
                        "continues around the event window."
                    ),
                    supporting_evidence=[
                        "CURRENT_STATE:EVENT_DRIVEN"
                    ],
                    invalidation_conditions=[
                        "Event window terminates and "
                        "market returns to a different state."
                    ],
                    provenance={
                        "constructed_from": [
                            "D9_TIME_EVENT",
                            "D10_STATE",
                        ]
                    },
                )
            )

        elif current_state == "ILLIQUID":

            scenarios.append(
                Scenario(
                    scenario_id="SCN_ILLIQUID_CONT",
                    scenario_type=(
                        ScenarioType.RANGE
                    ),
                    horizon=ScenarioHorizon.SHORT,
                    role=ScenarioRole.PRIMARY,
                    condition=(
                        "Illiquid conditions persist."
                    ),
                    supporting_evidence=[
                        "CURRENT_STATE:ILLIQUID"
                    ],
                    invalidation_conditions=[
                        "Liquidity state normalizes."
                    ],
                    provenance={
                        "constructed_from": [
                            "D7_LIQUIDITY",
                            "D10_STATE",
                        ]
                    },
                )
            )

        return scenarios

    # --------------------------------------------------------
    # PROBABILITY VALIDATION
    # --------------------------------------------------------

    @staticmethod
    def validate_probability(
        probability: Optional[float],
    ) -> Optional[float]:

        if probability is None:
            return None

        if not isinstance(
            probability,
            (int, float),
        ):
            raise ValueError(
                "Scenario probability must be numeric"
            )

        probability = float(probability)

        if probability < 0.0 or probability > 1.0:
            raise ValueError(
                "Scenario probability must be between 0 and 1"
            )

        return probability

    # --------------------------------------------------------
    # EXTERNAL CALIBRATED PROBABILITY
    # --------------------------------------------------------

    def attach_external_probability(
        self,
        *,
        scenario: Scenario,
        probability: float,
        source: str,
    ) -> Scenario:

        if not self.allow_external_probabilities:
            raise ValueError(
                "External probabilities disabled"
            )

        probability = self.validate_probability(
            probability
        )

        if not source:
            raise ValueError(
                "Probability source is required"
            )

        scenario.probability = probability
        scenario.probability_source = source

        return scenario

    # --------------------------------------------------------
    # MAIN EVALUATION
    # --------------------------------------------------------

    def evaluate(
        self,
        *,
        as_of: Any,
        current_state: Optional[str],
        transition_type: Optional[str],
        evidence: Sequence[ScenarioEvidence],
        market_id: Optional[str] = None,
    ) -> D12ScenarioResult:

        missing: List[str] = []

        if current_state is None:
            missing.append("CURRENT_STATE")

        if transition_type is None:
            missing.append("TRANSITION_TYPE")

        if missing:

            return D12ScenarioResult(
                status=D12Status.LIMITED,
                as_of=as_of,
                market_id=market_id,
                scenarios=[],
                current_state=current_state,
                transition_type=transition_type,
                missing_requirements=missing,
                conflicts=[],
                future_data_detected=False,
            )

        (
            valid_evidence,
            conflicts,
            future_detected,
        ) = self.validate_evidence(
            as_of=as_of,
            evidence=evidence,
        )

        if future_detected:

            return D12ScenarioResult(
                status=D12Status.BLOCKED,
                as_of=as_of,
                market_id=market_id,
                scenarios=[],
                current_state=current_state,
                transition_type=transition_type,
                missing_requirements=[],
                conflicts=conflicts,
                future_data_detected=True,
            )

        if conflicts:

            return D12ScenarioResult(
                status=D12Status.BLOCKED,
                as_of=as_of,
                market_id=market_id,
                scenarios=[],
                current_state=current_state,
                transition_type=transition_type,
                missing_requirements=[],
                conflicts=conflicts,
                future_data_detected=False,
            )

        evidence_map = self.evidence_map(
            valid_evidence
        )

        scenarios = self.build_base_scenarios(
            current_state=current_state,
            transition_type=transition_type,
            evidence=evidence_map,
        )

        if not scenarios:

            return D12ScenarioResult(
                status=D12Status.LIMITED,
                as_of=as_of,
                market_id=market_id,
                scenarios=[],
                current_state=current_state,
                transition_type=transition_type,
                missing_requirements=[
                    "SCENARIO_CONSTRUCTION_INSUFFICIENT"
                ],
                conflicts=[],
                future_data_detected=False,
            )

        # ----------------------------------------------------
        # D12 DOES NOT SELECT A DECISION
        # ----------------------------------------------------

        for scenario in scenarios:

            scenario.provenance.update(
                {
                    "as_of": as_of,
                    "market_id": market_id,
                    "future_outcome_observed": False,
                    "validated_by_D14": False,
                }
            )

        return D12ScenarioResult(
            status=D12Status.READY,
            as_of=as_of,
            market_id=market_id,
            scenarios=scenarios,
            current_state=current_state,
            transition_type=transition_type,
            missing_requirements=[],
            conflicts=[],
            future_data_detected=False,
            evidence={
                "scenario_count": len(scenarios),
                "future_outcome_used": False,
                "prediction_claimed_as_fact": False,
                "decision_performed": False,
                "validation_performed": False,
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

    t1 = t0 - timedelta(minutes=5)

    engine = D12FutureScenarioEngine()

    # --------------------------------------------------------
    # TEST 1 — Trending up scenarios
    # --------------------------------------------------------

    result = engine.evaluate(
        as_of=t0,
        current_state="TRENDING_UP",
        transition_type="STABLE",
        evidence=[
            ScenarioEvidence(
                name="price",
                value=25000.0,
                timestamp=t1,
                source="TEST",
            )
        ],
        market_id="NIFTY_SPOT",
    )

    assert result.status == D12Status.READY
    assert len(result.scenarios) >= 2
    assert result.future_data_detected is False

    # --------------------------------------------------------
    # TEST 2 — Trending down
    # --------------------------------------------------------

    result = engine.evaluate(
        as_of=t0,
        current_state="TRENDING_DOWN",
        transition_type="TRANSITION",
        evidence=[
            ScenarioEvidence(
                name="price",
                value=25000.0,
                timestamp=t1,
                source="TEST",
            )
        ],
        market_id="NIFTY_SPOT",
    )

    assert result.status == D12Status.READY

    assert any(
        s.scenario_type
        == ScenarioType.CONTINUATION
        for s in result.scenarios
    )

    assert any(
        s.scenario_type
        == ScenarioType.REVERSAL
        for s in result.scenarios
    )

    # --------------------------------------------------------
    # TEST 3 — Range gives multiple paths
    # --------------------------------------------------------

    result = engine.evaluate(
        as_of=t0,
        current_state="RANGE",
        transition_type="STABLE",
        evidence=[
            ScenarioEvidence(
                name="price",
                value=25000.0,
                timestamp=t1,
                source="TEST",
            )
        ],
        market_id="NIFTY_SPOT",
    )

    assert result.status == D12Status.READY
    assert len(result.scenarios) == 3

    scenario_types = {
        s.scenario_type
        for s in result.scenarios
    }

    assert ScenarioType.RANGE in scenario_types
    assert ScenarioType.BREAKOUT in scenario_types
    assert ScenarioType.BREAKDOWN in scenario_types

    # --------------------------------------------------------
    # TEST 4 — Future data attack
    # --------------------------------------------------------

    future = t0 + timedelta(minutes=1)

    result = engine.evaluate(
        as_of=t0,
        current_state="TRENDING_UP",
        transition_type="STABLE",
        evidence=[
            ScenarioEvidence(
                name="future_price",
                value=26000.0,
                timestamp=future,
                source="FUTURE",
            )
        ],
        market_id="NIFTY_SPOT",
    )

    assert result.status == D12Status.BLOCKED
    assert result.future_data_detected is True
    assert len(result.scenarios) == 0

    # --------------------------------------------------------
    # TEST 5 — Missing current state
    # --------------------------------------------------------

    result = engine.evaluate(
        as_of=t0,
        current_state=None,
        transition_type="STABLE",
        evidence=[],
    )

    assert result.status == D12Status.LIMITED
    assert "CURRENT_STATE" in (
        result.missing_requirements
    )

    # --------------------------------------------------------
    # TEST 6 — Missing transition
    # --------------------------------------------------------

    result = engine.evaluate(
        as_of=t0,
        current_state="RANGE",
        transition_type=None,
        evidence=[],
    )

    assert result.status == D12Status.LIMITED
    assert "TRANSITION_TYPE" in (
        result.missing_requirements
    )

    # --------------------------------------------------------
    # TEST 7 — Probability is optional and external
    # --------------------------------------------------------

    result = engine.evaluate(
        as_of=t0,
        current_state="TRENDING_UP",
        transition_type="STABLE",
        evidence=[
            ScenarioEvidence(
                name="price",
                value=25000.0,
                timestamp=t1,
                source="TEST",
            )
        ],
    )

    scenario = result.scenarios[0]

    assert scenario.probability is None

    engine.attach_external_probability(
        scenario=scenario,
        probability=0.70,
        source="CALIBRATED_PROFILE_V1",
    )

    assert scenario.probability == 0.70
    assert (
        scenario.probability_source
        == "CALIBRATED_PROFILE_V1"
    )

    # --------------------------------------------------------
    # TEST 8 — Invalid probability
    # --------------------------------------------------------

    try:
        engine.attach_external_probability(
            scenario=scenario,
            probability=1.50,
            source="TEST",
        )
        raise AssertionError(
            "Invalid probability accepted"
        )
    except ValueError:
        pass

    # --------------------------------------------------------
    # TEST 9 — Scenario is not fact
    # --------------------------------------------------------

    assert scenario.provenance[
        "future_outcome_observed"
    ] is False

    assert scenario.provenance[
        "validated_by_D14"
    ] is False

    # --------------------------------------------------------
    # TEST 10 — D12 boundary
    # --------------------------------------------------------

    assert result.evidence[
        "decision_performed"
    ] is False

    assert result.evidence[
        "validation_performed"
    ] is False

    assert result.evidence[
        "prediction_claimed_as_fact"
    ] is False

    print("D12 SELF-TEST: PASS")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    self_test()
# ============================================================
# D12 — FUTURE / SCENARIO
# PART 2/4
# CAS EVIDENCE + D10/D11 INTEGRATION
# ============================================================


# ============================================================
# D10 / D11 INPUT CONTRACTS
# ============================================================

@dataclass(frozen=True)
class D12StateInput:
    """
    Normalized current-state information received from D10.

    D12 consumes the state; it does not redefine D10 state.
    """

    market_id: Optional[str]

    current_state: str

    timestamp: Any

    evidence_quality: str = "INSUFFICIENT"

    source_ids: Tuple[str, ...] = ()
    evidence_ids: Tuple[str, ...] = ()

    provenance: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class D12TransitionInput:
    """
    Normalized transition information received from D11.

    D12 does not reinterpret D11 authority.
    """

    transition_type: str

    transition_status: str

    timestamp: Any

    transition_detected: bool = False

    structural_change: bool = False
    directional_change: bool = False
    flow_change: bool = False
    liquidity_change: bool = False
    volatility_change: bool = False

    evidence_ids: Tuple[str, ...] = ()
    source_ids: Tuple[str, ...] = ()

    provenance: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# SCENARIO EVIDENCE RECONCILIATION
# ============================================================

@dataclass
class ScenarioEvidenceReconciliation:
    status: D12Status

    total_evidence: int = 0
    valid_evidence: int = 0

    observed_count: int = 0
    derived_count: int = 0

    duplicate_names: List[str] = field(
        default_factory=list
    )

    contradictory_names: List[str] = field(
        default_factory=list
    )

    missing_timestamps: List[str] = field(
        default_factory=list
    )

    future_evidence: List[str] = field(
        default_factory=list
    )

    invalid_provenance: List[str] = field(
        default_factory=list
    )

    reasons: List[str] = field(
        default_factory=list
    )

    evidence_ids: List[str] = field(
        default_factory=list
    )

    source_ids: List[str] = field(
        default_factory=list
    )


# ============================================================
# PROVENANCE VALIDATION
# ============================================================

def validate_d12_provenance(
    provenance: Optional[Dict[str, Any]],
) -> bool:
    """
    D12 requires traceable provenance.

    Empty provenance is not automatically considered invalid
    because upstream adapters may provide traceability through
    evidence/source IDs.
    """

    if provenance is None:
        return False

    if not isinstance(provenance, dict):
        return False

    return True


def d12_unique(
    values: Sequence[Any],
) -> List[Any]:

    result = []

    for value in values:

        if value not in result:
            result.append(value)

    return result


# ============================================================
# TEMPORAL VALIDATION
# ============================================================

def validate_d12_temporal_order(
    *,
    as_of: Any,
    timestamp: Any,
) -> bool:

    if as_of is None or timestamp is None:
        return False

    try:
        delta = as_of - timestamp

        if hasattr(delta, "total_seconds"):
            return float(
                delta.total_seconds()
            ) >= 0.0

        return float(delta) >= 0.0

    except Exception:
        return False


# ============================================================
# EVIDENCE RECONCILER
# ============================================================

class D12EvidenceReconciler:

    def reconcile(
        self,
        *,
        as_of: Any,
        evidence: Sequence[ScenarioEvidence],
    ) -> ScenarioEvidenceReconciliation:

        total = len(evidence)

        if total == 0:

            return ScenarioEvidenceReconciliation(
                status=D12Status.LIMITED,
                total_evidence=0,
                valid_evidence=0,
                reasons=[
                    "No scenario evidence supplied."
                ],
            )

        valid_count = 0
        observed_count = 0
        derived_count = 0

        duplicate_names = []
        contradictory_names = []
        missing_timestamps = []
        future_evidence = []
        invalid_provenance = []

        evidence_ids = []
        source_ids = []

        values_by_name: Dict[
            str,
            List[Any]
        ] = {}

        for item in evidence:

            name = str(
                item.name
            ).strip()

            if not name:
                contradictory_names.append(
                    "EMPTY_NAME"
                )
                continue

            if item.timestamp is None:
                missing_timestamps.append(
                    name
                )
                continue

            if not validate_d12_temporal_order(
                as_of=as_of,
                timestamp=item.timestamp,
            ):
                future_evidence.append(
                    name
                )
                continue

            if not validate_d12_provenance(
                item.metadata
            ):
                invalid_provenance.append(
                    name
                )

            valid_count += 1

            if item.observed:
                observed_count += 1
            else:
                derived_count += 1

            values_by_name.setdefault(
                name,
                []
            ).append(item.value)

            evidence_id = item.metadata.get(
                "evidence_id"
            )

            source_id = item.source

            if evidence_id:
                evidence_ids.append(
                    evidence_id
                )

            if source_id:
                source_ids.append(
                    source_id
                )

        for name, values in values_by_name.items():

            if len(values) > 1:
                duplicate_names.append(name)

                first = values[0]

                if any(
                    value != first
                    for value in values[1:]
                ):
                    contradictory_names.append(
                        name
                    )

        reasons = []

        if missing_timestamps:
            reasons.append(
                "Evidence with missing timestamps excluded."
            )

        if future_evidence:
            reasons.append(
                "Future-dated evidence detected."
            )

        if contradictory_names:
            reasons.append(
                "Contradictory evidence detected."
            )

        if invalid_provenance:
            reasons.append(
                "Some evidence has weak provenance metadata."
            )

        if future_evidence:
            status = D12Status.BLOCKED

        elif contradictory_names:
            status = D12Status.LIMITED

        elif valid_count == 0:
            status = D12Status.LIMITED

        elif invalid_provenance:
            status = D12Status.LIMITED

        else:
            status = D12Status.READY

        return ScenarioEvidenceReconciliation(
            status=status,
            total_evidence=total,
            valid_evidence=valid_count,
            observed_count=observed_count,
            derived_count=derived_count,
            duplicate_names=d12_unique(
                duplicate_names
            ),
            contradictory_names=d12_unique(
                contradictory_names
            ),
            missing_timestamps=d12_unique(
                missing_timestamps
            ),
            future_evidence=d12_unique(
                future_evidence
            ),
            invalid_provenance=d12_unique(
                invalid_provenance
            ),
            reasons=reasons,
            evidence_ids=d12_unique(
                evidence_ids
            ),
            source_ids=d12_unique(
                source_ids
            ),
        )


# ============================================================
# D10 / D11 CONSISTENCY
# ============================================================

@dataclass
class D12UpstreamReconciliation:
    status: D12Status

    state_valid: bool = False
    transition_valid: bool = False

    state_transition_consistent: bool = True

    conflicts: List[str] = field(
        default_factory=list
    )

    reasons: List[str] = field(
        default_factory=list
    )

    evidence_ids: List[str] = field(
        default_factory=list
    )

    source_ids: List[str] = field(
        default_factory=list
    )


def reconcile_d12_upstream(
    *,
    state_input: Optional[D12StateInput],
    transition_input: Optional[D12TransitionInput],
) -> D12UpstreamReconciliation:

    conflicts = []
    reasons = []

    if state_input is None:
        conflicts.append(
            "D10_STATE_INPUT_MISSING"
        )

    if transition_input is None:
        conflicts.append(
            "D11_TRANSITION_INPUT_MISSING"
        )

    if conflicts:

        return D12UpstreamReconciliation(
            status=D12Status.LIMITED,
            state_valid=state_input is not None,
            transition_valid=(
                transition_input is not None
            ),
            state_transition_consistent=False,
            conflicts=conflicts,
        )

    state = str(
        state_input.current_state
    ).upper()

    transition = str(
        transition_input.transition_type
    ).upper()

    state_valid = bool(state)

    transition_valid = bool(
        transition
    )

    # --------------------------------------------------------
    # Explicit D11 transition consistency checks.
    # These are consistency checks, not scenario selection.
    # --------------------------------------------------------

    consistency = True

    if (
        transition
        == "ACCUMULATION_TO_EXPANSION"
        and state not in {
            "BULLISH_EXPANSION",
            "TRENDING_UP",
            "BREAKOUT",
        }
    ):
        consistency = False
        conflicts.append(
            "ACCUMULATION_TO_EXPANSION_WITHOUT_BULLISH_STATE"
        )

    if (
        transition
        == "DISTRIBUTION_TO_EXPANSION"
        and state not in {
            "BEARISH_EXPANSION",
            "TRENDING_DOWN",
            "BREAKDOWN",
        }
    ):
        consistency = False
        conflicts.append(
            "DISTRIBUTION_TO_EXPANSION_WITHOUT_BEARISH_STATE"
        )

    if (
        transition == "BULLISH_REVERSAL"
        and state == "TRENDING_DOWN"
    ):
        # This is not automatically invalid.
        # D12 records the tension rather than rewriting D11.
        reasons.append(
            "Bullish reversal remains compatible with current "
            "downward state as a transition process."
        )

    if (
        transition == "BEARISH_REVERSAL"
        and state == "TRENDING_UP"
    ):
        reasons.append(
            "Bearish reversal remains compatible with current "
            "upward state as a transition process."
        )

    if consistency:
        reasons.append(
            "D10 state and D11 transition are structurally compatible."
        )

    status = (
        D12Status.READY
        if consistency
        else D12Status.LIMITED
    )

    return D12UpstreamReconciliation(
        status=status,
        state_valid=state_valid,
        transition_valid=transition_valid,
        state_transition_consistent=consistency,
        conflicts=conflicts,
        reasons=reasons,
        evidence_ids=d12_unique(
            list(state_input.evidence_ids)
            + list(transition_input.evidence_ids)
        ),
        source_ids=d12_unique(
            list(state_input.source_ids)
            + list(transition_input.source_ids)
        ),
    )


# ============================================================
# SCENARIO DEDUPLICATION / ROLE VALIDATION
# ============================================================

def validate_scenario_roles(
    scenarios: Sequence[Scenario],
) -> Tuple[
    bool,
    List[str],
]:

    errors = []

    if not scenarios:
        return False, [
            "NO_SCENARIOS"
        ]

    ids = [
        scenario.scenario_id
        for scenario in scenarios
    ]

    if len(ids) != len(set(ids)):
        errors.append(
            "DUPLICATE_SCENARIO_ID"
        )

    primary_count = sum(
        scenario.role
        == ScenarioRole.PRIMARY
        for scenario in scenarios
    )

    # Multiple PRIMARY scenarios are not automatically wrong.
    # D12 must preserve competing valid paths.
    if primary_count == 0:
        errors.append(
            "NO_PRIMARY_OR_BASE_SCENARIO"
        )

    for scenario in scenarios:

        if not scenario.condition:
            errors.append(
                f"EMPTY_CONDITION:{scenario.scenario_id}"
            )

        if not scenario.invalidation_conditions:
            errors.append(
                f"MISSING_INVALIDATION:{scenario.scenario_id}"
            )

        if not scenario.provenance:
            errors.append(
                f"MISSING_PROVENANCE:{scenario.scenario_id}"
            )

    return (
        not errors,
        errors,
    )


# ============================================================
# SCENARIO NORMALIZATION
# ============================================================

def normalize_d12_scenario(
    scenario: Scenario,
) -> Scenario:

    if not scenario.supporting_evidence:
        scenario.supporting_evidence = []

    if not scenario.invalidation_conditions:
        scenario.invalidation_conditions = [
            "Scenario invalidation condition not supplied."
        ]

    scenario.supporting_evidence = d12_unique(
        scenario.supporting_evidence
    )

    scenario.invalidation_conditions = d12_unique(
        scenario.invalidation_conditions
    )

    scenario.provenance = dict(
        scenario.provenance or {}
    )

    scenario.provenance.setdefault(
        "future_outcome_observed",
        False,
    )

    scenario.provenance.setdefault(
        "validated_by_D14",
        False,
    )

    return scenario


# ============================================================
# SCENARIO CONFLICT DETECTION
# ============================================================

def detect_d12_scenario_conflicts(
    scenarios: Sequence[Scenario],
) -> List[str]:

    conflicts = []

    directional = []

    for scenario in scenarios:

        if scenario.scenario_type in {
            ScenarioType.BREAKOUT,
            ScenarioType.CONTINUATION,
        }:
            directional.append(
                "DIRECTIONAL"
            )

        elif scenario.scenario_type in {
            ScenarioType.BREAKDOWN,
            ScenarioType.REVERSAL,
        }:
            directional.append(
                "OPPOSING"
            )

    if (
        "DIRECTIONAL" in directional
        and "OPPOSING" in directional
    ):
        conflicts.append(
            "COMPETING_DIRECTIONAL_SCENARIOS"
        )

    # Competition is not an error.
    # It is an explicit property of scenario space.
    return conflicts


# ============================================================
# ATTACH CAS INTELLIGENCE
# ============================================================

def attach_d12_cas_reconciliation(
    result: D12ScenarioResult,
    reconciliation: ScenarioEvidenceReconciliation,
    upstream: Optional[D12UpstreamReconciliation] = None,
) -> D12ScenarioResult:

    upstream = upstream or D12UpstreamReconciliation(
        status=D12Status.LIMITED
    )

    result.evidence = dict(
        result.evidence or {}
    )

    result.evidence[
        "cas_evidence_reconciliation"
    ] = {
        "status": reconciliation.status.value,
        "total_evidence": reconciliation.total_evidence,
        "valid_evidence": reconciliation.valid_evidence,
        "observed_count": reconciliation.observed_count,
        "derived_count": reconciliation.derived_count,
        "duplicate_names": reconciliation.duplicate_names,
        "contradictory_names": (
            reconciliation.contradictory_names
        ),
        "future_evidence": (
            reconciliation.future_evidence
        ),
        "invalid_provenance": (
            reconciliation.invalid_provenance
        ),
        "reasons": reconciliation.reasons,
    }

    result.evidence[
        "upstream_reconciliation"
    ] = {
        "status": upstream.status.value,
        "state_valid": upstream.state_valid,
        "transition_valid": upstream.transition_valid,
        "state_transition_consistent": (
            upstream.state_transition_consistent
        ),
        "conflicts": upstream.conflicts,
        "reasons": upstream.reasons,
    }

    result.conflicts = d12_unique(
        list(result.conflicts)
        + list(reconciliation.contradictory_names)
        + list(upstream.conflicts)
    )

    if (
        reconciliation.status
        == D12Status.BLOCKED
    ):
        result.status = D12Status.BLOCKED

    elif (
        reconciliation.status
        == D12Status.LIMITED
        or upstream.status
        == D12Status.LIMITED
    ):
        if result.status == D12Status.READY:
            result.status = D12Status.LIMITED

    return result


# ============================================================
# INTEGRATED D10/D11 → D12 INPUT BUILDER
# ============================================================

def build_d12_from_upstream(
    *,
    as_of: Any,
    state_input: D12StateInput,
    transition_input: D12TransitionInput,
    evidence: Sequence[ScenarioEvidence],
    market_id: Optional[str] = None,
) -> D12ScenarioResult:

    reconciler = D12EvidenceReconciler()

    evidence_result = reconciler.reconcile(
        as_of=as_of,
        evidence=evidence,
    )

    upstream_result = reconcile_d12_upstream(
        state_input=state_input,
        transition_input=transition_input,
    )

    engine = D12FutureScenarioEngine()

    if (
        evidence_result.status
        == D12Status.BLOCKED
    ):

        result = D12ScenarioResult(
            status=D12Status.BLOCKED,
            as_of=as_of,
            market_id=market_id
            or state_input.market_id,
            scenarios=[],
            current_state=state_input.current_state,
            transition_type=transition_input.transition_type,
            missing_requirements=[],
            conflicts=evidence_result.reasons,
            future_data_detected=True,
        )

        return attach_d12_cas_reconciliation(
            result,
            evidence_result,
            upstream_result,
        )

    valid_evidence = []

    for item in evidence:

        if validate_d12_temporal_order(
            as_of=as_of,
            timestamp=item.timestamp,
        ):
            valid_evidence.append(item)

    result = engine.evaluate(
        as_of=as_of,
        current_state=state_input.current_state,
        transition_type=transition_input.transition_type,
        evidence=valid_evidence,
        market_id=market_id
        or state_input.market_id,
    )

    result = attach_d12_cas_reconciliation(
        result,
        evidence_result,
        upstream_result,
    )

    # --------------------------------------------------------
    # Attach D10 / D11 provenance to every scenario.
    # --------------------------------------------------------

    for scenario in result.scenarios:

        scenario = normalize_d12_scenario(
            scenario
        )

        scenario.provenance.update(
            {
                "D10_state": (
                    state_input.current_state
                ),
                "D10_timestamp": (
                    state_input.timestamp
                ),
                "D11_transition": (
                    transition_input.transition_type
                ),
                "D11_timestamp": (
                    transition_input.timestamp
                ),
                "D11_transition_status": (
                    transition_input.transition_status
                ),
                "future_outcome_observed": False,
                "validated_by_D14": False,
            }
        )

    result.evidence[
        "D10_consumed"
    ] = True

    result.evidence[
        "D11_consumed"
    ] = True

    result.evidence[
        "D13_authority"
    ] = True

    result.evidence[
        "D14_future_validation_owner"
    ] = True

    result.evidence[
        "decision_performed"
    ] = False

    return result


# ============================================================
# PART 2 SELF-CHECK
# ============================================================

def d12_part2_self_check() -> Dict[str, Any]:

    from datetime import datetime, timedelta, timezone

    t0 = datetime(
        2026,
        1,
        1,
        10,
        0,
        tzinfo=timezone.utc,
    )

    t1 = t0 - timedelta(
        minutes=5
    )

    evidence = [
        ScenarioEvidence(
            name="price",
            value=25000.0,
            timestamp=t1,
            source="TEST_SOURCE",
            observed=True,
            metadata={
                "evidence_id": "E1"
            },
        )
    ]

    state_input = D12StateInput(
        market_id="TEST_MARKET",
        current_state="TRENDING_UP",
        timestamp=t0,
        evidence_quality="STRONG",
        source_ids=("S1",),
        evidence_ids=("E1",),
        provenance={
            "source": "D10"
        },
    )

    transition_input = D12TransitionInput(
        transition_type="BULLISH_DEVELOPMENT",
        transition_status="READY",
        timestamp=t0,
        transition_detected=True,
        structural_change=True,
        directional_change=True,
        evidence_ids=("E2",),
        source_ids=("S2",),
        provenance={
            "source": "D11"
        },
    )

    result = build_d12_from_upstream(
        as_of=t0,
        state_input=state_input,
        transition_input=transition_input,
        evidence=evidence,
        market_id="TEST_MARKET",
    )

    checks = {}

    checks[
        "result_ready_or_limited"
    ] = result.status in {
        D12Status.READY,
        D12Status.LIMITED,
    }

    checks[
        "scenarios_created"
    ] = len(result.scenarios) > 0

    checks[
        "D10_consumed"
    ] = (
        result.evidence.get(
            "D10_consumed"
        ) is True
    )

    checks[
        "D11_consumed"
    ] = (
        result.evidence.get(
            "D11_consumed"
        ) is True
    )

    checks[
        "decision_not_performed"
    ] = (
        result.evidence.get(
            "decision_performed"
        ) is False
    )

    checks[
        "D14_validation_owner"
    ] = (
        result.evidence.get(
            "D14_future_validation_owner"
        ) is True
    )

    checks[
        "future_data_not_used"
    ] = (
        result.future_data_detected
        is False
    )

    valid_roles, role_errors = (
        validate_scenario_roles(
            result.scenarios
        )
    )

    checks[
        "scenario_roles"
    ] = valid_roles

    checks[
        "scenario_provenance"
    ] = all(
        scenario.provenance.get(
            "future_outcome_observed"
        ) is False
        for scenario in result.scenarios
    )

    # --------------------------------------------------------
    # Future evidence must be blocked.
    # --------------------------------------------------------

    future_evidence = [
        ScenarioEvidence(
            name="future_price",
            value=26000.0,
            timestamp=t0 + timedelta(
                minutes=1
            ),
            source="FUTURE_SOURCE",
            observed=True,
        )
    ]

    future_result = build_d12_from_upstream(
        as_of=t0,
        state_input=state_input,
        transition_input=transition_input,
        evidence=future_evidence,
        market_id="TEST_MARKET",
    )

    checks[
        "future_data_blocked"
    ] = (
        future_result.status
        == D12Status.BLOCKED
    )

    return {
        "engine": "D12FutureScenario",
        "part": "2/4",
        "checks": checks,
        "role_errors": role_errors,
        "passed": all(checks.values()),
        "decision_authority": "D13",
        "future_validation_authority": "D14",
    }


# ============================================================
# EXPORT EXTENSION
# ============================================================

try:
    __all__.extend([
        "D12StateInput",
        "D12TransitionInput",
        "ScenarioEvidenceReconciliation",
        "validate_d12_provenance",
        "validate_d12_temporal_order",
        "D12EvidenceReconciler",
        "D12UpstreamReconciliation",
        "reconcile_d12_upstream",
        "validate_scenario_roles",
        "normalize_d12_scenario",
        "detect_d12_scenario_conflicts",
        "attach_d12_cas_reconciliation",
        "build_d12_from_upstream",
        "d12_part2_self_check",
    ])
except NameError:
    pass


# ============================================================
# END D12 PART 2/4
# ============================================================
# =============================================================================
# D12 FUTURE / SCENARIO ENGINE
# PART 3/4 — TRANSITION-AWARE SCENARIO GRAPH & BRANCH INTELLIGENCE
# =============================================================================
#
# PURPOSE
# -------
# Part 3 converts reconciled D10 + D11 context into a structured scenario
# dependency graph.
#
# HARD BOUNDARIES
# ---------------
# 1. Scenario != prediction fact
# 2. Scenario != decision
# 3. Scenario != execution authority
# 4. No fabricated probability
# 5. No arbitrary 0-100 score
# 6. No future-data leakage
# 7. D13 remains Decision Authority
# 8. D14 remains Future Outcome Validation Authority
# 9. A scenario may only exist when its conditions are explicitly represented
# 10. PRIMARY/ALTERNATIVE role is structural, not a trading recommendation
#
# =============================================================================

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple


# =============================================================================
# 3.1 — NORMALIZATION MAPS
# =============================================================================

D12_STATE_ALIASES: Dict[str, str] = {
    "BULLISH": "BULLISH_EXPANSION",
    "BULLISH_EXPANSION": "BULLISH_EXPANSION",
    "TRENDING_UP": "BULLISH_EXPANSION",
    "UPTREND": "BULLISH_EXPANSION",

    "BEARISH": "BEARISH_EXPANSION",
    "BEARISH_EXPANSION": "BEARISH_EXPANSION",
    "TRENDING_DOWN": "BEARISH_EXPANSION",
    "DOWNTREND": "BEARISH_EXPANSION",

    "ACCUMULATION": "ACCUMULATION",
    "DISTRIBUTION": "DISTRIBUTION",
    "RANGE": "RANGE",
    "BALANCED": "RANGE",
    "ROTATION": "ROTATION",
    "TRANSITION": "TRANSITION",
    "CHAOS": "CHAOS",
    "UNKNOWN": "UNKNOWN",
}


D12_TRANSITION_ALIASES: Dict[str, str] = {
    "NONE": "NONE",
    "NO_CHANGE": "NONE",

    "BULLISH_DEVELOPMENT": "BULLISH_DEVELOPMENT",
    "BEARISH_DEVELOPMENT": "BEARISH_DEVELOPMENT",

    "BULLISH_REVERSAL": "BULLISH_REVERSAL",
    "BEARISH_REVERSAL": "BEARISH_REVERSAL",

    "RANGE_EXPANSION": "RANGE_EXPANSION",
    "RANGE_CONTRACTION": "RANGE_CONTRACTION",

    "ACCUMULATION_TO_EXPANSION": "ACCUMULATION_TO_EXPANSION",
    "DISTRIBUTION_TO_EXPANSION": "DISTRIBUTION_TO_EXPANSION",

    "STRUCTURAL_BREAK": "STRUCTURAL_BREAK",
    "FAILED_BREAKOUT": "FAILED_BREAKOUT",

    "LIQUIDITY_TRANSITION": "LIQUIDITY_TRANSITION",
    "VOLATILITY_TRANSITION": "VOLATILITY_TRANSITION",
    "ROTATION": "ROTATION",
    "CHAOS_TRANSITION": "CHAOS_TRANSITION",
    "UNKNOWN": "UNKNOWN",
}


def normalize_d12_state(value: Any) -> str:
    text = str(value or "").strip().upper()
    return D12_STATE_ALIASES.get(text, text or "UNKNOWN")


def normalize_d12_transition(value: Any) -> str:
    text = str(value or "").strip().upper()
    return D12_TRANSITION_ALIASES.get(text, text or "UNKNOWN")


# =============================================================================
# 3.2 — SCENARIO BRANCH STRUCTURE
# =============================================================================

@dataclass
class D12ScenarioBranch:
    branch_id: str
    scenario_id: str
    scenario_type: str
    horizon: str
    role: str

    parent_branch_id: Optional[str] = None
    trigger_conditions: List[str] = field(default_factory=list)
    supporting_evidence_ids: List[str] = field(default_factory=list)
    invalidation_conditions: List[str] = field(default_factory=list)
    invalidation_evidence_ids: List[str] = field(default_factory=list)

    direction: str = "NEUTRAL"

    probability: Optional[float] = None
    probability_source: Optional[str] = None

    provenance: Dict[str, Any] = field(default_factory=dict)


@dataclass
class D12ScenarioGraph:
    market_id: str
    as_of: Any

    current_state: str
    transition_type: str

    root_branch_id: Optional[str]

    branches: List[D12ScenarioBranch] = field(default_factory=list)

    status: str = "READY"

    conflicts: List[str] = field(default_factory=list)
    missing_requirements: List[str] = field(default_factory=list)

    future_data_detected: bool = False

    provenance: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# 3.3 — CONDITION EXTRACTION
# =============================================================================

def d12_condition_list(value: Any) -> List[str]:
    if value is None:
        return []

    if isinstance(value, str):
        value = [value]

    if not isinstance(value, (list, tuple, set)):
        return []

    output: List[str] = []

    for item in value:
        text = str(item).strip()

        if text and text not in output:
            output.append(text)

    return output


def d12_evidence_ids(evidence: Any) -> List[str]:
    output: List[str] = []

    if evidence is None:
        return output

    if isinstance(evidence, dict):
        evidence = list(evidence.values())

    if not isinstance(evidence, (list, tuple, set)):
        return output

    for item in evidence:
        if isinstance(item, ScenarioEvidence):
            value = item.metadata.get("evidence_id")
            if value:
                output.append(str(value))

            continue

        if isinstance(item, dict):
            value = (
                item.get("evidence_id")
                or item.get("id")
                or item.get("name")
            )

            if value:
                output.append(str(value))

    return d12_unique(output)


# =============================================================================
# 3.4 — TRANSITION → SCENARIO FAMILY
# =============================================================================

def d12_transition_family(
    current_state: Any,
    transition_type: Any,
) -> str:
    state = normalize_d12_state(current_state)
    transition = normalize_d12_transition(transition_type)

    if transition in {
        "BULLISH_DEVELOPMENT",
        "ACCUMULATION_TO_EXPANSION",
        "BULLISH_REVERSAL",
    }:
        return "BULLISH_DEVELOPMENT"

    if transition in {
        "BEARISH_DEVELOPMENT",
        "DISTRIBUTION_TO_EXPANSION",
        "BEARISH_REVERSAL",
    }:
        return "BEARISH_DEVELOPMENT"

    if transition == "RANGE_EXPANSION":
        return "RANGE_EXPANSION"

    if transition == "RANGE_CONTRACTION":
        return "RANGE_CONTRACTION"

    if transition == "FAILED_BREAKOUT":
        return "FAILED_BREAKOUT"

    if transition == "STRUCTURAL_BREAK":
        return "STRUCTURAL_BREAK"

    if transition == "LIQUIDITY_TRANSITION":
        return "LIQUIDITY_TRANSITION"

    if transition == "VOLATILITY_TRANSITION":
        return "VOLATILITY_TRANSITION"

    if transition == "ROTATION":
        return "ROTATION"

    if transition == "CHAOS_TRANSITION":
        return "CHAOS_TRANSITION"

    if state == "BULLISH_EXPANSION":
        return "BULLISH_CONTINUATION"

    if state == "BEARISH_EXPANSION":
        return "BEARISH_CONTINUATION"

    if state in {"RANGE", "ROTATION"}:
        return "RANGE_STRUCTURE"

    if state == "ACCUMULATION":
        return "ACCUMULATION_STRUCTURE"

    if state == "DISTRIBUTION":
        return "DISTRIBUTION_STRUCTURE"

    return "UNRESOLVED"


# =============================================================================
# 3.5 — SCENARIO TYPE / DIRECTION HELPERS
# =============================================================================

def d12_scenario_direction(scenario_type: Any) -> str:
    value = str(scenario_type or "").strip().upper()

    if value in {
        "BREAKOUT",
        "CONTINUATION",
        "EVENT_RESPONSE",
        "VOLATILITY_EXPANSION",
    }:
        return "UP_OR_EXPANSION"

    if value in {
        "BREAKDOWN",
    }:
        return "DOWN_OR_EXPANSION"

    if value in {
        "REVERSAL",
    }:
        return "REVERSAL"

    if value in {
        "RANGE",
        "VOLATILITY_CONTRACTION",
    }:
        return "NEUTRAL_OR_CONTRACTION"

    return "NEUTRAL"


def d12_scenario_type_for_family(
    family: str,
    state: str,
) -> str:
    family = str(family or "").upper()
    state = normalize_d12_state(state)

    mapping = {
        "BULLISH_DEVELOPMENT": "CONTINUATION",
        "BEARISH_DEVELOPMENT": "CONTINUATION",
        "BULLISH_CONTINUATION": "CONTINUATION",
        "BEARISH_CONTINUATION": "CONTINUATION",
        "RANGE_EXPANSION": "BREAKOUT",
        "RANGE_CONTRACTION": "RANGE",
        "FAILED_BREAKOUT": "REVERSAL",
        "STRUCTURAL_BREAK": "BREAKOUT",
        "LIQUIDITY_TRANSITION": "EVENT_RESPONSE",
        "VOLATILITY_TRANSITION": "VOLATILITY_EXPANSION",
        "ROTATION": "RANGE",
        "CHAOS_TRANSITION": "EVENT_RESPONSE",
        "RANGE_STRUCTURE": "RANGE",
        "ACCUMULATION_STRUCTURE": "BREAKOUT",
        "DISTRIBUTION_STRUCTURE": "BREAKDOWN",
    }

    return mapping.get(family, "UNKNOWN")


# =============================================================================
# 3.6 — BRANCH CONSTRUCTION
# =============================================================================

def build_d12_transition_scenarios(
    market_id: str,
    as_of: Any,
    current_state: Any,
    transition_type: Any,
    evidence: Optional[Sequence[Any]] = None,
    horizon: str = "SHORT",
) -> List[D12ScenarioBranch]:

    state = normalize_d12_state(current_state)
    transition = normalize_d12_transition(transition_type)
    family = d12_transition_family(state, transition)

    evidence_ids = d12_evidence_ids(evidence)

    branches: List[D12ScenarioBranch] = []

    def add_branch(
        branch_id: str,
        scenario_id: str,
        scenario_type: str,
        role: str,
        conditions: Sequence[str],
        invalidations: Sequence[str],
        direction: str = "NEUTRAL",
        parent: Optional[str] = None,
    ) -> None:

        branches.append(
            D12ScenarioBranch(
                branch_id=branch_id,
                scenario_id=scenario_id,
                scenario_type=scenario_type,
                horizon=horizon,
                role=role,
                parent_branch_id=parent,
                trigger_conditions=d12_condition_list(conditions),
                supporting_evidence_ids=list(evidence_ids),
                invalidation_conditions=d12_condition_list(invalidations),
                direction=direction,
                provenance={
                    "market_id": market_id,
                    "as_of": as_of,
                    "current_state": state,
                    "transition_type": transition,
                    "transition_family": family,
                    "future_outcome_observed": False,
                    "validated_by_D14": False,
                    "decision_performed": False,
                },
            )
        )

    # -------------------------------------------------------------------------
    # BULLISH DEVELOPMENT
    # -------------------------------------------------------------------------
    if family in {
        "BULLISH_DEVELOPMENT",
        "BULLISH_CONTINUATION",
    }:
        root = "D12-BULL-PRIMARY"

        add_branch(
            root,
            "SCN-BULL-CONTINUATION",
            "CONTINUATION",
            "PRIMARY",
            [
                "bullish structure remains supported",
                "transition evidence remains directionally consistent",
            ],
            [
                "material structural failure",
                "validated opposing transition",
            ],
            "UP",
        )

        add_branch(
            "D12-BULL-ALT",
            "SCN-BULL-REVERSAL",
            "REVERSAL",
            "ALTERNATIVE",
            [
                "opposing structure develops",
                "bullish transition loses supporting evidence",
            ],
            [
                "bullish structure reasserts with supporting evidence",
            ],
            "REVERSAL",
            root,
        )

        add_branch(
            "D12-BULL-INVALID",
            "SCN-BULL-INVALIDATION",
            "REVERSAL",
            "INVALIDATION",
            [
                "bullish scenario invalidation condition becomes observed",
            ],
            [],
            "DOWN",
            root,
        )

    # -------------------------------------------------------------------------
    # BEARISH DEVELOPMENT
    # -------------------------------------------------------------------------
    elif family in {
        "BEARISH_DEVELOPMENT",
        "BEARISH_CONTINUATION",
    }:
        root = "D12-BEAR-PRIMARY"

        add_branch(
            root,
            "SCN-BEAR-CONTINUATION",
            "CONTINUATION",
            "PRIMARY",
            [
                "bearish structure remains supported",
                "transition evidence remains directionally consistent",
            ],
            [
                "material structural failure",
                "validated opposing transition",
            ],
            "DOWN",
        )

        add_branch(
            "D12-BEAR-ALT",
            "SCN-BEAR-REVERSAL",
            "REVERSAL",
            "ALTERNATIVE",
            [
                "opposing structure develops",
                "bearish transition loses supporting evidence",
            ],
            [
                "bearish structure reasserts with supporting evidence",
            ],
            "REVERSAL",
            root,
        )

        add_branch(
            "D12-BEAR-INVALID",
            "SCN-BEAR-INVALIDATION",
            "REVERSAL",
            "INVALIDATION",
            [
                "bearish scenario invalidation condition becomes observed",
            ],
            [],
            "UP",
            root,
        )

    # -------------------------------------------------------------------------
    # RANGE / BALANCED STRUCTURE
    # -------------------------------------------------------------------------
    elif family in {
        "RANGE_STRUCTURE",
        "RANGE_CONTRACTION",
    }:
        root = "D12-RANGE-PRIMARY"

        add_branch(
            root,
            "SCN-RANGE-CONTINUATION",
            "RANGE",
            "PRIMARY",
            [
                "range structure remains intact",
                "no validated structural expansion dominates",
            ],
            [
                "validated structural expansion",
            ],
            "NEUTRAL",
        )

        add_branch(
            "D12-RANGE-UP",
            "SCN-RANGE-BREAKOUT",
            "BREAKOUT",
            "ALTERNATIVE",
            [
                "upper structural boundary is breached",
                "supporting evidence confirms structural expansion",
            ],
            [
                "breakout failure",
            ],
            "UP",
            root,
        )

        add_branch(
            "D12-RANGE-DOWN",
            "SCN-RANGE-BREAKDOWN",
            "BREAKDOWN",
            "ALTERNATIVE",
            [
                "lower structural boundary is breached",
                "supporting evidence confirms structural expansion",
            ],
            [
                "breakdown failure",
            ],
            "DOWN",
            root,
        )

    # -------------------------------------------------------------------------
    # ACCUMULATION
    # -------------------------------------------------------------------------
    elif family == "ACCUMULATION_STRUCTURE":
        root = "D12-ACCUMULATION-PRIMARY"

        add_branch(
            root,
            "SCN-ACCUMULATION",
            "RANGE",
            "PRIMARY",
            [
                "accumulation structure persists",
                "expansion evidence is not yet validated",
            ],
            [
                "validated expansion",
                "validated structural failure",
            ],
            "NEUTRAL",
        )

        add_branch(
            "D12-ACCUMULATION-EXPANSION",
            "SCN-ACCUMULATION-BREAKOUT",
            "BREAKOUT",
            "ALTERNATIVE",
            [
                "accumulation resolves into structural expansion",
            ],
            [
                "expansion fails",
            ],
            "UP",
            root,
        )

    # -------------------------------------------------------------------------
    # DISTRIBUTION
    # -------------------------------------------------------------------------
    elif family == "DISTRIBUTION_STRUCTURE":
        root = "D12-DISTRIBUTION-PRIMARY"

        add_branch(
            root,
            "SCN-DISTRIBUTION",
            "RANGE",
            "PRIMARY",
            [
                "distribution structure persists",
                "downside expansion is not yet validated",
            ],
            [
                "validated downside expansion",
                "validated structural failure",
            ],
            "NEUTRAL",
        )

        add_branch(
            "D12-DISTRIBUTION-BREAKDOWN",
            "SCN-DISTRIBUTION-BREAKDOWN",
            "BREAKDOWN",
            "ALTERNATIVE",
            [
                "distribution resolves into downside structural expansion",
            ],
            [
                "downside expansion fails",
            ],
            "DOWN",
            root,
        )

    # -------------------------------------------------------------------------
    # FAILED BREAKOUT / REVERSAL
    # -------------------------------------------------------------------------
    elif family == "FAILED_BREAKOUT":
        root = "D12-FAILED-BREAKOUT"

        add_branch(
            root,
            "SCN-FAILED-BREAKOUT-REVERSAL",
            "REVERSAL",
            "PRIMARY",
            [
                "breakout failure is explicitly observed",
                "opposing structure is developing",
            ],
            [
                "failed-breakout condition is invalidated",
            ],
            "REVERSAL",
        )

        add_branch(
            "D12-FAILED-BREAKOUT-RETEST",
            "SCN-FAILED-BREAKOUT-RETEST",
            "RANGE",
            "ALTERNATIVE",
            [
                "market re-enters prior structural region",
            ],
            [
                "new validated structural expansion",
            ],
            "NEUTRAL",
            root,
        )

    # -------------------------------------------------------------------------
    # STRUCTURAL BREAK
    # -------------------------------------------------------------------------
    elif family == "STRUCTURAL_BREAK":
        root = "D12-STRUCTURAL-BREAK"

        add_branch(
            root,
            "SCN-STRUCTURAL-CONTINUATION",
            "BREAKOUT",
            "PRIMARY",
            [
                "structural break remains supported by evidence",
            ],
            [
                "break invalidation",
                "validated opposite structural transition",
            ],
            "UP_OR_DOWN",
        )

        add_branch(
            "D12-STRUCTURAL-FAILURE",
            "SCN-STRUCTURAL-FAILURE",
            "REVERSAL",
            "ALTERNATIVE",
            [
                "structural break loses supporting evidence",
            ],
            [
                "structural continuation re-established",
            ],
            "REVERSAL",
            root,
        )

    # -------------------------------------------------------------------------
    # VOLATILITY TRANSITION
    # -------------------------------------------------------------------------
    elif family == "VOLATILITY_TRANSITION":
        root = "D12-VOL-PRIMARY"

        add_branch(
            root,
            "SCN-VOL-EXPANSION",
            "VOLATILITY_EXPANSION",
            "PRIMARY",
            [
                "volatility transition remains supported",
            ],
            [
                "volatility contraction becomes structurally supported",
            ],
            "EXPANSION",
        )

        add_branch(
            "D12-VOL-CONTRACTION",
            "SCN-VOL-CONTRACTION",
            "VOLATILITY_CONTRACTION",
            "ALTERNATIVE",
            [
                "volatility contracts after transition",
            ],
            [
                "new volatility expansion evidence",
            ],
            "CONTRACTION",
            root,
        )

    # -------------------------------------------------------------------------
    # LIQUIDITY TRANSITION
    # -------------------------------------------------------------------------
    elif family == "LIQUIDITY_TRANSITION":
        root = "D12-LIQUIDITY-PRIMARY"

        add_branch(
            root,
            "SCN-LIQUIDITY-REPRICING",
            "EVENT_RESPONSE",
            "PRIMARY",
            [
                "liquidity regime transition remains observed",
            ],
            [
                "liquidity regime normalizes",
            ],
            "REPRICING",
        )

        add_branch(
            "D12-LIQUIDITY-NORMALIZATION",
            "SCN-LIQUIDITY-NORMALIZATION",
            "RANGE",
            "ALTERNATIVE",
            [
                "liquidity conditions normalize",
            ],
            [
                "new liquidity deterioration",
            ],
            "NEUTRAL",
            root,
        )

    # -------------------------------------------------------------------------
    # ROTATION
    # -------------------------------------------------------------------------
    elif family == "ROTATION":
        root = "D12-ROTATION"

        add_branch(
            root,
            "SCN-ROTATION-CONTINUATION",
            "RANGE",
            "PRIMARY",
            [
                "rotation structure persists",
            ],
            [
                "validated directional structural expansion",
            ],
            "NEUTRAL",
        )

        add_branch(
            "D12-ROTATION-BREAK",
            "SCN-ROTATION-BREAK",
            "BREAKOUT",
            "ALTERNATIVE",
            [
                "rotation resolves into directional structure",
            ],
            [
                "directional expansion fails",
            ],
            "UP_OR_DOWN",
            root,
        )

    # -------------------------------------------------------------------------
    # CHAOS
    # -------------------------------------------------------------------------
    elif family == "CHAOS_TRANSITION":
        root = "D12-CHAOS"

        add_branch(
            root,
            "SCN-CHAOS-PERSISTENCE",
            "EVENT_RESPONSE",
            "PRIMARY",
            [
                "chaotic market structure remains unresolved",
            ],
            [
                "structure becomes sufficiently coherent",
            ],
            "UNRESOLVED",
        )

        add_branch(
            "D12-CHAOS-RESOLUTION",
            "SCN-CHAOS-RESOLUTION",
            "RANGE",
            "ALTERNATIVE",
            [
                "market structure becomes coherent",
            ],
            [
                "chaos persists or increases",
            ],
            "NEUTRAL",
            root,
        )

    # -------------------------------------------------------------------------
    # UNKNOWN / INSUFFICIENT CONTEXT
    # -------------------------------------------------------------------------
    else:
        add_branch(
            "D12-UNKNOWN",
            "SCN-UNKNOWN",
            "UNKNOWN",
            "PRIMARY",
            [
                "current state or transition remains insufficiently resolved",
            ],
            [
                "sufficient validated context becomes available",
            ],
            "NEUTRAL",
        )

    return branches


# =============================================================================
# 3.7 — SCENARIO GRAPH BUILDER
# =============================================================================

def build_d12_scenario_graph(
    market_id: str,
    as_of: Any,
    current_state: Any,
    transition_type: Any,
    evidence: Optional[Sequence[Any]] = None,
    horizon: str = "SHORT",
    provenance: Optional[Dict[str, Any]] = None,
) -> D12ScenarioGraph:

    state = normalize_d12_state(current_state)
    transition = normalize_d12_transition(transition_type)

    branches = build_d12_transition_scenarios(
        market_id=market_id,
        as_of=as_of,
        current_state=state,
        transition_type=transition,
        evidence=evidence,
        horizon=horizon,
    )

    root_branch = next(
        (
            branch.branch_id
            for branch in branches
            if branch.role == "PRIMARY"
        ),
        None,
    )

    graph = D12ScenarioGraph(
        market_id=str(market_id or ""),
        as_of=as_of,
        current_state=state,
        transition_type=transition,
        root_branch_id=root_branch,
        branches=branches,
        provenance={
            **(provenance or {}),
            "market_id": market_id,
            "as_of": as_of,
            "D10_consumed": True,
            "D11_consumed": True,
            "future_outcome_observed": False,
            "validated_by_D14": False,
            "decision_performed": False,
            "decision_authority": "D13",
            "future_validation_authority": "D14",
        },
    )

    graph.status, graph.conflicts = validate_d12_scenario_graph(graph)

    return graph


# =============================================================================
# 3.8 — GRAPH VALIDATION
# =============================================================================

def validate_d12_scenario_graph(
    graph: D12ScenarioGraph,
) -> Tuple[str, List[str]]:

    conflicts: List[str] = []

    if not graph.market_id:
        conflicts.append("missing_market_id")

    if not graph.branches:
        conflicts.append("no_scenario_branches")

    primary_count = sum(
        1 for branch in graph.branches
        if branch.role == "PRIMARY"
    )

    if primary_count == 0:
        conflicts.append("missing_primary_branch")

    if primary_count > 1:
        conflicts.append("multiple_primary_branches")

    branch_ids = [
        branch.branch_id
        for branch in graph.branches
    ]

    if len(branch_ids) != len(set(branch_ids)):
        conflicts.append("duplicate_branch_id")

    scenario_ids = [
        branch.scenario_id
        for branch in graph.branches
    ]

    if len(scenario_ids) != len(set(scenario_ids)):
        conflicts.append("duplicate_scenario_id")

    branch_map = {
        branch.branch_id: branch
        for branch in graph.branches
    }

    for branch in graph.branches:

        if branch.parent_branch_id:
            if branch.parent_branch_id not in branch_map:
                conflicts.append(
                    f"missing_parent:{branch.branch_id}"
                )

        if branch.role not in {
            "PRIMARY",
            "ALTERNATIVE",
            "INVALIDATION",
        }:
            conflicts.append(
                f"invalid_role:{branch.branch_id}"
            )

        if not branch.trigger_conditions:
            conflicts.append(
                f"missing_trigger_conditions:{branch.branch_id}"
            )

        if branch.provenance.get("future_outcome_observed"):
            conflicts.append(
                f"future_outcome_leakage:{branch.branch_id}"
            )

        if branch.probability is not None:
            if not (0.0 <= float(branch.probability) <= 1.0):
                conflicts.append(
                    f"invalid_probability:{branch.branch_id}"
                )

            if not branch.probability_source:
                conflicts.append(
                    f"probability_without_source:{branch.branch_id}"
                )

    if conflicts:
        return "LIMITED", d12_unique(conflicts)

    return "READY", []


# =============================================================================
# 3.9 — SCENARIO INVALIDATION MAPPING
# =============================================================================

def map_d12_invalidation_evidence(
    graph: D12ScenarioGraph,
    evidence: Optional[Sequence[Any]] = None,
) -> D12ScenarioGraph:

    if evidence is None:
        return graph

    evidence_names: Dict[str, Any] = {}

    for item in evidence:

        if isinstance(item, ScenarioEvidence):
            evidence_names[item.name.upper()] = item.value

        elif isinstance(item, dict):
            name = item.get("name") or item.get("id")

            if name:
                evidence_names[str(name).upper()] = item.get("value")

    for branch in graph.branches:

        matched: List[str] = []

        for condition in branch.invalidation_conditions:

            condition_upper = condition.upper()

            for evidence_name in evidence_names:

                if evidence_name in condition_upper:
                    matched.append(evidence_name)

        branch.invalidation_evidence_ids = d12_unique(matched)

    return graph


# =============================================================================
# 3.10 — HORIZON CONSISTENCY
# =============================================================================

D12_VALID_HORIZONS = {
    "SHORT",
    "MEDIUM",
    "LONG",
}


def validate_d12_horizon(horizon: Any) -> str:
    value = str(horizon or "").strip().upper()

    if value not in D12_VALID_HORIZONS:
        return "SHORT"

    return value


def normalize_d12_graph_horizon(
    graph: D12ScenarioGraph,
    horizon: Any,
) -> D12ScenarioGraph:

    normalized = validate_d12_horizon(horizon)

    for branch in graph.branches:
        branch.horizon = normalized

    return graph


# =============================================================================
# 3.11 — PROBABILITY SAFETY
# =============================================================================

def validate_d12_graph_probabilities(
    graph: D12ScenarioGraph,
) -> Tuple[bool, List[str]]:

    errors: List[str] = []

    for branch in graph.branches:

        if branch.probability is None:
            continue

        if not graph.provenance.get(
            "allow_external_probabilities",
            False,
        ):
            errors.append(
                f"internal_probability_forbidden:{branch.branch_id}"
            )
            continue

        try:
            probability = float(branch.probability)
        except (TypeError, ValueError):
            errors.append(
                f"invalid_probability:{branch.branch_id}"
            )
            continue

        if not 0.0 <= probability <= 1.0:
            errors.append(
                f"probability_out_of_range:{branch.branch_id}"
            )

        if not branch.probability_source:
            errors.append(
                f"missing_probability_source:{branch.branch_id}"
            )

    return not errors, errors


# =============================================================================
# 3.12 — GRAPH → EXISTING D12 SCENARIO OBJECTS
# =============================================================================

def d12_graph_to_scenarios(
    graph: D12ScenarioGraph,
) -> List[Scenario]:

    scenarios: List[Scenario] = []

    for branch in graph.branches:

        scenarios.append(
            Scenario(
                scenario_id=branch.scenario_id,
                scenario_type=branch.scenario_type,
                horizon=branch.horizon,
                role=branch.role,
                condition="; ".join(
                    branch.trigger_conditions
                ),
                supporting_evidence=[],
                invalidation_conditions=list(
                    branch.invalidation_conditions
                ),
                probability=branch.probability,
                probability_source=branch.probability_source,
                provenance={
                    **branch.provenance,
                    "branch_id": branch.branch_id,
                    "parent_branch_id": branch.parent_branch_id,
                    "direction": branch.direction,
                    "graph_status": graph.status,
                    "future_outcome_observed": False,
                    "validated_by_D14": False,
                    "decision_performed": False,
                },
            )
        )

    return scenarios


# =============================================================================
# 3.13 — FULL PART-3 ATTACHMENT
# =============================================================================

def attach_d12_scenario_graph(
    result: D12ScenarioResult,
    graph: D12ScenarioGraph,
) -> D12ScenarioResult:

    result.scenarios = d12_graph_to_scenarios(graph)

    result.conflicts = d12_unique(
        list(result.conflicts)
        + list(graph.conflicts)
    )

    if graph.future_data_detected:
        result.future_data_detected = True
        result.status = D12Status.BLOCKED

    elif graph.status == "LIMITED":
        if result.status != D12Status.BLOCKED:
            result.status = D12Status.LIMITED

    result.evidence = {
        **dict(result.evidence or {}),
        "scenario_graph": graph,
        "scenario_graph_status": graph.status,
        "scenario_branch_count": len(graph.branches),
        "scenario_primary_branch": graph.root_branch_id,
        "scenario_graph_validated": graph.status != "BLOCKED",
        "decision_performed": False,
        "decision_authority": "D13",
        "future_validation_authority": "D14",
        "future_outcome_observed": False,
    }

    return result


# =============================================================================
# 3.14 — COMPLETE D12 PART-3 BUILDER
# =============================================================================

def build_d12_part3(
    market_id: str,
    as_of: Any,
    current_state: Any,
    transition_type: Any,
    evidence: Optional[Sequence[Any]] = None,
    horizon: str = "SHORT",
    provenance: Optional[Dict[str, Any]] = None,
) -> D12ScenarioGraph:

    graph = build_d12_scenario_graph(
        market_id=market_id,
        as_of=as_of,
        current_state=current_state,
        transition_type=transition_type,
        evidence=evidence,
        horizon=horizon,
        provenance=provenance,
    )

    graph = normalize_d12_graph_horizon(
        graph,
        horizon,
    )

    graph = map_d12_invalidation_evidence(
        graph,
        evidence,
    )

    probability_ok, probability_errors = (
        validate_d12_graph_probabilities(graph)
    )

    if not probability_ok:
        graph.status = "LIMITED"
        graph.conflicts = d12_unique(
            graph.conflicts + probability_errors
        )

    return graph


# =============================================================================
# 3.15 — PART 3 SELF CHECK
# =============================================================================

def d12_part3_self_check() -> Dict[str, Any]:

    checks: Dict[str, bool] = {}

    graph = build_d12_part3(
        market_id="TEST",
        as_of="2026-01-01T10:00:00",
        current_state="BULLISH_EXPANSION",
        transition_type="BULLISH_DEVELOPMENT",
        evidence=[
            ScenarioEvidence(
                name="structure",
                value="bullish",
                timestamp="2026-01-01T09:59:00",
                source="TEST_SOURCE",
                observed=True,
                metadata={"evidence_id": "E1"},
            )
        ],
        horizon="SHORT",
    )

    checks["graph_created"] = bool(graph.branches)

    checks["primary_exists"] = any(
        branch.role == "PRIMARY"
        for branch in graph.branches
    )

    checks["alternative_exists"] = any(
        branch.role == "ALTERNATIVE"
        for branch in graph.branches
    )

    checks["invalidation_exists"] = any(
        branch.role == "INVALIDATION"
        for branch in graph.branches
    )

    checks["future_leakage_false"] = all(
        branch.provenance.get(
            "future_outcome_observed"
        ) is False
        for branch in graph.branches
    )

    checks["decision_not_performed"] = all(
        branch.provenance.get(
            "decision_performed"
        ) is False
        for branch in graph.branches
    )

    checks["d13_authority"] = (
        graph.provenance.get(
            "decision_authority"
        ) == "D13"
    )

    checks["d14_validation_owner"] = (
        graph.provenance.get(
            "future_validation_authority"
        ) == "D14"
    )

    checks["no_internal_probability"] = all(
        branch.probability is None
        for branch in graph.branches
    )

    range_graph = build_d12_part3(
        market_id="TEST",
        as_of="2026-01-01T10:00:00",
        current_state="RANGE",
        transition_type="NONE",
    )

    checks["range_has_branches"] = (
        len(range_graph.branches) >= 3
    )

    failed_graph = build_d12_part3(
        market_id="TEST",
        as_of="2026-01-01T10:00:00",
        current_state="BULLISH_EXPANSION",
        transition_type="FAILED_BREAKOUT",
    )

    checks["failed_breakout_explicit"] = any(
        branch.scenario_type == "REVERSAL"
        for branch in failed_graph.branches
    )

    checks["all_pass"] = all(checks.values())

    return checks


# =============================================================================
# 3.16 — PART 3 EXPORT / FACTORY
# =============================================================================

def create_d12_scenario_graph_engine(
    allow_external_probabilities: bool = False,
):
    """
    Lightweight factory.

    The returned callable builds a scenario graph while preserving
    D12 authority boundaries.
    """

    def _build(
        market_id: str,
        as_of: Any,
        current_state: Any,
        transition_type: Any,
        evidence: Optional[Sequence[Any]] = None,
        horizon: str = "SHORT",
        provenance: Optional[Dict[str, Any]] = None,
    ) -> D12ScenarioGraph:

        graph = build_d12_part3(
            market_id=market_id,
            as_of=as_of,
            current_state=current_state,
            transition_type=transition_type,
            evidence=evidence,
            horizon=horizon,
            provenance={
                **(provenance or {}),
                "allow_external_probabilities":
                    bool(allow_external_probabilities),
            },
        )

        return graph

    return _build


D12_PART3_EXPORTS = (
    "D12ScenarioBranch",
    "D12ScenarioGraph",
    "normalize_d12_state",
    "normalize_d12_transition",
    "d12_transition_family",
    "build_d12_transition_scenarios",
    "build_d12_scenario_graph",
    "validate_d12_scenario_graph",
    "map_d12_invalidation_evidence",
    "validate_d12_horizon",
    "normalize_d12_graph_horizon",
    "validate_d12_graph_probabilities",
    "d12_graph_to_scenarios",
    "attach_d12_scenario_graph",
    "build_d12_part3",
    "d12_part3_self_check",
    "create_d12_scenario_graph_engine",
)


# =============================================================================
# END — D12 PART 3/4
# =============================================================================
# =============================================================================
# D12 FUTURE / SCENARIO ENGINE
# PART 4/4 — FINAL CONTRACT, PIPELINE, D13 HANDOFF & COMPLETE SELF-CHECK
# =============================================================================
#
# FINAL AUTHORITY BOUNDARY
# ------------------------
# D12 = Future / Scenario Intelligence
# D13 = Decision Authority
# D14 = Future Outcome Validation Authority
#
# D12 MUST NOT:
#   - issue BUY / SELL
#   - create execution instructions
#   - determine position size
#   - authorize entry / exit
#   - claim future outcome as observed fact
#   - generate fabricated probability
#   - generate arbitrary 0-100 confidence/intelligence score
#   - replace D13
#   - replace D14
#
# D12 MAY:
#   - construct conditional scenarios
#   - maintain alternative branches
#   - expose invalidation conditions
#   - preserve provenance
#   - identify unresolved future paths
#   - attach externally supplied probability only when explicitly sourced
#
# =============================================================================

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple


# =============================================================================
# 4.1 — FINAL CONTRACT
# =============================================================================

@dataclass
class D12FinalContract:
    engine_name: str
    engine_version: str

    status: str
    as_of: Any

    market_id: str

    current_state: str
    transition_type: str

    scenarios: List[Scenario] = field(default_factory=list)

    primary_scenario_id: Optional[str] = None
    alternative_scenario_ids: List[str] = field(
        default_factory=list
    )
    invalidation_scenario_ids: List[str] = field(
        default_factory=list
    )

    missing_requirements: List[str] = field(
        default_factory=list
    )
    conflicts: List[str] = field(
        default_factory=list
    )

    future_data_detected: bool = False

    decision_performed: bool = False
    execution_authority: bool = False

    d13_authority: str = "D13"
    d14_future_validation_authority: str = "D14"

    provenance: Dict[str, Any] = field(
        default_factory=dict
    )


# =============================================================================
# 4.2 — CONTRACT SERIALIZATION
# =============================================================================

def d12_scenario_to_dict(
    scenario: Scenario,
) -> Dict[str, Any]:

    return {
        "scenario_id": scenario.scenario_id,
        "scenario_type": scenario.scenario_type,
        "horizon": scenario.horizon,
        "role": scenario.role,
        "condition": scenario.condition,
        "supporting_evidence": list(
            scenario.supporting_evidence
        ),
        "invalidation_conditions": list(
            scenario.invalidation_conditions
        ),
        "probability": scenario.probability,
        "probability_source": scenario.probability_source,
        "provenance": dict(
            scenario.provenance or {}
        ),
    }


def d12_contract_to_dict(
    contract: D12FinalContract,
) -> Dict[str, Any]:

    return {
        "engine_name": contract.engine_name,
        "engine_version": contract.engine_version,
        "status": contract.status,
        "as_of": contract.as_of,
        "market_id": contract.market_id,
        "current_state": contract.current_state,
        "transition_type": contract.transition_type,
        "scenarios": [
            d12_scenario_to_dict(item)
            for item in contract.scenarios
        ],
        "primary_scenario_id": contract.primary_scenario_id,
        "alternative_scenario_ids": list(
            contract.alternative_scenario_ids
        ),
        "invalidation_scenario_ids": list(
            contract.invalidation_scenario_ids
        ),
        "missing_requirements": list(
            contract.missing_requirements
        ),
        "conflicts": list(
            contract.conflicts
        ),
        "future_data_detected": contract.future_data_detected,
        "decision_performed": contract.decision_performed,
        "execution_authority": contract.execution_authority,
        "d13_authority": contract.d13_authority,
        "d14_future_validation_authority": (
            contract.d14_future_validation_authority
        ),
        "provenance": dict(
            contract.provenance or {}
        ),
    }


# =============================================================================
# 4.3 — CONTRACT VALIDATION
# =============================================================================

D12_FORBIDDEN_OUTPUTS = {
    "BUY",
    "SELL",
    "ENTRY",
    "EXIT",
    "EXECUTE",
    "EXECUTION",
    "POSITION_SIZE",
    "PROFIT_TARGET",
    "STOP_LOSS_AUTHORITY",
    "TRADE_AUTHORITY",
    "UNIVERSAL_PROBABILITY",
}


def validate_d12_final_contract(
    contract: D12FinalContract,
) -> Tuple[bool, List[str]]:

    errors: List[str] = []

    if contract.engine_name != "D12_FutureScenario":
        errors.append("invalid_engine_name")

    if not contract.engine_version:
        errors.append("missing_engine_version")

    if not contract.market_id:
        errors.append("missing_market_id")

    if contract.execution_authority:
        errors.append(
            "d12_execution_authority_must_be_false"
        )

    if contract.decision_performed:
        errors.append(
            "d12_must_not_perform_decision"
        )

    if contract.d13_authority != "D13":
        errors.append(
            "d13_authority_boundary_broken"
        )

    if contract.d14_future_validation_authority != "D14":
        errors.append(
            "d14_validation_boundary_broken"
        )

    if contract.future_data_detected:
        if contract.status != D12Status.BLOCKED.value:
            errors.append(
                "future_data_requires_blocked_status"
            )

    scenario_ids = [
        scenario.scenario_id
        for scenario in contract.scenarios
    ]

    if len(scenario_ids) != len(set(scenario_ids)):
        errors.append(
            "duplicate_scenario_ids"
        )

    for scenario in contract.scenarios:

        if scenario.role not in {
            ScenarioRole.PRIMARY.value,
            ScenarioRole.ALTERNATIVE.value,
            ScenarioRole.INVALIDATION.value,
        }:
            errors.append(
                f"invalid_scenario_role:{scenario.scenario_id}"
            )

        if scenario.probability is not None:

            try:
                probability = float(
                    scenario.probability
                )
            except (TypeError, ValueError):
                errors.append(
                    f"invalid_probability:{scenario.scenario_id}"
                )
                continue

            if not 0.0 <= probability <= 1.0:
                errors.append(
                    f"probability_out_of_range:{scenario.scenario_id}"
                )

            if not scenario.probability_source:
                errors.append(
                    f"probability_source_missing:{scenario.scenario_id}"
                )

        if scenario.provenance.get(
            "future_outcome_observed",
            False,
        ):
            errors.append(
                f"future_outcome_leakage:{scenario.scenario_id}"
            )

        if scenario.provenance.get(
            "decision_performed",
            False,
        ):
            errors.append(
                f"decision_leakage:{scenario.scenario_id}"
            )

    return not errors, d12_unique(errors)


# =============================================================================
# 4.4 — FINAL STATUS RESOLUTION
# =============================================================================

def resolve_d12_final_status(
    base_status: Any,
    graph: Optional[D12ScenarioGraph] = None,
    future_data_detected: bool = False,
    conflicts: Optional[Sequence[str]] = None,
) -> D12Status:

    if future_data_detected:
        return D12Status.BLOCKED

    conflict_list = list(conflicts or [])

    if graph is not None:
        conflict_list.extend(
            graph.conflicts
        )

        if graph.future_data_detected:
            return D12Status.BLOCKED

        if graph.status == "LIMITED":
            return D12Status.LIMITED

    if conflict_list:
        return D12Status.LIMITED

    if isinstance(base_status, D12Status):
        return base_status

    try:
        return D12Status(
            str(base_status)
        )
    except ValueError:
        return D12Status.LIMITED


# =============================================================================
# 4.5 — CONTRACT BUILDER
# =============================================================================

def build_d12_final_contract(
    market_id: str,
    as_of: Any,
    current_state: Any,
    transition_type: Any,
    scenarios: Sequence[Scenario],
    status: Any,
    missing_requirements: Optional[
        Sequence[str]
    ] = None,
    conflicts: Optional[
        Sequence[str]
    ] = None,
    future_data_detected: bool = False,
    provenance: Optional[
        Dict[str, Any]
    ] = None,
) -> D12FinalContract:

    scenario_list = list(scenarios or [])

    primary = next(
        (
            item.scenario_id
            for item in scenario_list
            if item.role == ScenarioRole.PRIMARY.value
        ),
        None,
    )

    alternatives = [
        item.scenario_id
        for item in scenario_list
        if item.role == ScenarioRole.ALTERNATIVE.value
    ]

    invalidations = [
        item.scenario_id
        for item in scenario_list
        if item.role == ScenarioRole.INVALIDATION.value
    ]

    final_status = resolve_d12_final_status(
        base_status=status,
        future_data_detected=future_data_detected,
        conflicts=conflicts,
    )

    contract = D12FinalContract(
        engine_name="D12_FutureScenario",
        engine_version="V6-CAS-1.0",
        status=final_status.value,
        as_of=as_of,
        market_id=str(market_id or ""),
        current_state=normalize_d12_state(
            current_state
        ),
        transition_type=normalize_d12_transition(
            transition_type
        ),
        scenarios=scenario_list,
        primary_scenario_id=primary,
        alternative_scenario_ids=alternatives,
        invalidation_scenario_ids=invalidations,
        missing_requirements=d12_unique(
            list(missing_requirements or [])
        ),
        conflicts=d12_unique(
            list(conflicts or [])
        ),
        future_data_detected=bool(
            future_data_detected
        ),
        decision_performed=False,
        execution_authority=False,
        d13_authority="D13",
        d14_future_validation_authority="D14",
        provenance={
            **(provenance or {}),
            "future_outcome_observed": False,
            "validated_by_D14": False,
            "decision_performed": False,
            "execution_authority": False,
            "decision_authority": "D13",
            "future_validation_authority": "D14",
        },
    )

    return contract


# =============================================================================
# 4.6 — D12 → D13 HANDOFF
# =============================================================================

@dataclass
class D12D13Handoff:
    market_id: str
    as_of: Any

    current_state: str
    transition_type: str

    scenarios: List[Dict[str, Any]] = field(
        default_factory=list
    )

    primary_scenario_id: Optional[str] = None

    alternative_scenario_ids: List[str] = field(
        default_factory=list
    )

    invalidation_scenario_ids: List[str] = field(
        default_factory=list
    )

    d12_status: str = D12Status.LIMITED.value

    future_data_detected: bool = False

    decision_authority: str = "D13"

    decision_performed: bool = False

    provenance: Dict[str, Any] = field(
        default_factory=dict
    )


def d12_to_d13_handoff(
    contract: D12FinalContract,
) -> D12D13Handoff:

    valid, errors = validate_d12_final_contract(
        contract
    )

    handoff_provenance = {
        **dict(contract.provenance or {}),
        "source_engine": "D12_FutureScenario",
        "source_version": contract.engine_version,
        "d12_contract_valid": valid,
        "d12_contract_errors": errors,
        "decision_performed": False,
        "decision_authority": "D13",
        "future_validation_authority": "D14",
    }

    return D12D13Handoff(
        market_id=contract.market_id,
        as_of=contract.as_of,
        current_state=contract.current_state,
        transition_type=contract.transition_type,
        scenarios=[
            d12_scenario_to_dict(item)
            for item in contract.scenarios
        ],
        primary_scenario_id=(
            contract.primary_scenario_id
        ),
        alternative_scenario_ids=list(
            contract.alternative_scenario_ids
        ),
        invalidation_scenario_ids=list(
            contract.invalidation_scenario_ids
        ),
        d12_status=contract.status,
        future_data_detected=(
            contract.future_data_detected
        ),
        decision_authority="D13",
        decision_performed=False,
        provenance=handoff_provenance,
    )


def d12_d13_handoff_to_dict(
    handoff: D12D13Handoff,
) -> Dict[str, Any]:

    return {
        "market_id": handoff.market_id,
        "as_of": handoff.as_of,
        "current_state": handoff.current_state,
        "transition_type": handoff.transition_type,
        "scenarios": list(handoff.scenarios),
        "primary_scenario_id": (
            handoff.primary_scenario_id
        ),
        "alternative_scenario_ids": list(
            handoff.alternative_scenario_ids
        ),
        "invalidation_scenario_ids": list(
            handoff.invalidation_scenario_ids
        ),
        "d12_status": handoff.d12_status,
        "future_data_detected": (
            handoff.future_data_detected
        ),
        "decision_authority": (
            handoff.decision_authority
        ),
        "decision_performed": (
            handoff.decision_performed
        ),
        "provenance": dict(
            handoff.provenance or {}
        ),
    }


# =============================================================================
# 4.7 — COMPLETE D12 PIPELINE
# =============================================================================

class D12FinalPipeline:
    """
    Complete D12 pipeline.

    Flow:

        D10 State
             ↓
        D11 Transition
             ↓
        D12 Evidence Reconciliation
             ↓
        Scenario Construction
             ↓
        Scenario Graph
             ↓
        Scenario Validation
             ↓
        Final D12 Contract
             ↓
        D13 Handoff

    D12 does not decide or execute.
    """

    def __init__(
        self,
        allow_external_probabilities: bool = False,
    ) -> None:

        self.allow_external_probabilities = bool(
            allow_external_probabilities
        )

        self.history: List[D12FinalContract] = []

    def evaluate(
        self,
        market_id: str,
        as_of: Any,
        current_state: Any,
        transition_type: Any,
        evidence: Optional[
            Sequence[Any]
        ] = None,
        horizon: str = "SHORT",
        missing_requirements: Optional[
            Sequence[str]
        ] = None,
        provenance: Optional[
            Dict[str, Any]
        ] = None,
    ) -> D12FinalContract:

        state = normalize_d12_state(
            current_state
        )

        transition = normalize_d12_transition(
            transition_type
        )

        # ---------------------------------------------------------------------
        # STEP 1 — Evidence reconciliation
        # ---------------------------------------------------------------------

        reconciliation = (
            D12EvidenceReconciler.reconcile(
                evidence=evidence,
                as_of=as_of,
            )
        )

        # ---------------------------------------------------------------------
        # STEP 2 — Build scenario graph
        # ---------------------------------------------------------------------

        graph = build_d12_part3(
            market_id=market_id,
            as_of=as_of,
            current_state=state,
            transition_type=transition,
            evidence=evidence,
            horizon=validate_d12_horizon(
                horizon
            ),
            provenance={
                **(provenance or {}),
                "allow_external_probabilities": (
                    self.allow_external_probabilities
                ),
            },
        )

        # ---------------------------------------------------------------------
        # STEP 3 — Apply evidence reconciliation state
        # ---------------------------------------------------------------------

        final_conflicts = d12_unique(
            list(
                reconciliation.conflicts
                if hasattr(
                    reconciliation,
                    "conflicts",
                )
                else []
            )
            + list(graph.conflicts)
        )

        future_data_detected = bool(
            getattr(
                reconciliation,
                "future_evidence",
                False,
            )
            or graph.future_data_detected
        )

        base_status = (
            D12Status.BLOCKED
            if future_data_detected
            else (
                D12Status.LIMITED
                if final_conflicts
                else D12Status.READY
            )
        )

        # ---------------------------------------------------------------------
        # STEP 4 — Convert graph into scenario objects
        # ---------------------------------------------------------------------

        scenarios = d12_graph_to_scenarios(
            graph
        )

        # ---------------------------------------------------------------------
        # STEP 5 — Build final contract
        # ---------------------------------------------------------------------

        contract = build_d12_final_contract(
            market_id=market_id,
            as_of=as_of,
            current_state=state,
            transition_type=transition,
            scenarios=scenarios,
            status=base_status,
            missing_requirements=(
                list(missing_requirements or [])
                + list(
                    getattr(
                        reconciliation,
                        "missing_timestamps",
                        [],
                    )
                )
            ),
            conflicts=final_conflicts,
            future_data_detected=future_data_detected,
            provenance={
                **(provenance or {}),
                "D10_consumed": True,
                "D11_consumed": True,
                "D12_evidence_reconciled": True,
                "D12_scenario_graph_built": True,
                "future_outcome_observed": False,
                "validated_by_D14": False,
                "decision_performed": False,
                "execution_authority": False,
                "decision_authority": "D13",
                "future_validation_authority": "D14",
            },
        )

        # ---------------------------------------------------------------------
        # STEP 6 — Final contract validation
        # ---------------------------------------------------------------------

        valid, errors = (
            validate_d12_final_contract(
                contract
            )
        )

        if not valid:
            contract.conflicts = d12_unique(
                contract.conflicts + errors
            )

            if (
                contract.status
                != D12Status.BLOCKED.value
            ):
                contract.status = (
                    D12Status.LIMITED.value
                )

        self.history.append(contract)

        return contract

    def evaluate_dict(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:

        contract = self.evaluate(
            *args,
            **kwargs,
        )

        return d12_contract_to_dict(
            contract
        )

    def handoff_to_d13(
        self,
        contract: D12FinalContract,
    ) -> D12D13Handoff:

        return d12_to_d13_handoff(
            contract
        )

    def latest(
        self,
    ) -> Optional[D12FinalContract]:

        if not self.history:
            return None

        return self.history[-1]


# =============================================================================
# 4.8 — SIMPLE PUBLIC API
# =============================================================================

def evaluate_d12_future_scenario(
    market_id: str,
    as_of: Any,
    current_state: Any,
    transition_type: Any,
    evidence: Optional[
        Sequence[Any]
    ] = None,
    horizon: str = "SHORT",
    allow_external_probabilities: bool = False,
    missing_requirements: Optional[
        Sequence[str]
    ] = None,
    provenance: Optional[
        Dict[str, Any]
    ] = None,
) -> D12FinalContract:

    pipeline = D12FinalPipeline(
        allow_external_probabilities=(
            allow_external_probabilities
        )
    )

    return pipeline.evaluate(
        market_id=market_id,
        as_of=as_of,
        current_state=current_state,
        transition_type=transition_type,
        evidence=evidence,
        horizon=horizon,
        missing_requirements=missing_requirements,
        provenance=provenance,
    )


def evaluate_d12_future_scenario_dict(
    *args: Any,
    **kwargs: Any,
) -> Dict[str, Any]:

    contract = evaluate_d12_future_scenario(
        *args,
        **kwargs,
    )

    return d12_contract_to_dict(
        contract
    )


# =============================================================================
# 4.9 — COMPLETE D12 SELF-CHECK
# =============================================================================

def d12_complete_self_check() -> Dict[str, Any]:

    checks: Dict[str, bool] = {}

    # -------------------------------------------------------------------------
    # Part 1 check
    # -------------------------------------------------------------------------

    try:
        base_engine = D12FutureScenarioEngine()

        base_result = base_engine.evaluate(
            market_id="SELF_TEST",
            as_of="2026-01-01T10:00:00",
            current_state="TRENDING_UP",
            transition_type="BULLISH_DEVELOPMENT",
            evidence=[
                ScenarioEvidence(
                    name="structure",
                    value="bullish",
                    timestamp="2026-01-01T09:59:00",
                    source="TEST",
                    observed=True,
                )
            ],
        )

        checks["part1_engine"] = (
            base_result.status
            in {
                D12Status.READY,
                D12Status.LIMITED,
            }
        )

    except Exception:
        checks["part1_engine"] = False

    # -------------------------------------------------------------------------
    # Part 2 check
    # -------------------------------------------------------------------------

    try:
        reconciliation = (
            D12EvidenceReconciler.reconcile(
                evidence=[
                    ScenarioEvidence(
                        name="structure",
                        value="bullish",
                        timestamp="2026-01-01T09:59:00",
                        source="TEST",
                        observed=True,
                        metadata={
                            "evidence_id": "E1"
                        },
                    )
                ],
                as_of="2026-01-01T10:00:00",
            )
        )

        checks["part2_reconciliation"] = (
            reconciliation.status
            in {
                "READY",
                "LIMITED",
                "BLOCKED",
            }
        )

    except Exception:
        checks["part2_reconciliation"] = False

    # -------------------------------------------------------------------------
    # Part 3 check
    # -------------------------------------------------------------------------

    try:
        graph = build_d12_part3(
            market_id="SELF_TEST",
            as_of="2026-01-01T10:00:00",
            current_state="BULLISH_EXPANSION",
            transition_type="BULLISH_DEVELOPMENT",
        )

        checks["part3_graph"] = (
            len(graph.branches) >= 2
        )

        checks["part3_invalidation"] = any(
            item.role == "INVALIDATION"
            for item in graph.branches
        )

    except Exception:
        checks["part3_graph"] = False
        checks["part3_invalidation"] = False

    # -------------------------------------------------------------------------
    # Part 4 final pipeline
    # -------------------------------------------------------------------------

    try:
        pipeline = D12FinalPipeline()

        contract = pipeline.evaluate(
            market_id="SELF_TEST",
            as_of="2026-01-01T10:00:00",
            current_state="BULLISH_EXPANSION",
            transition_type="BULLISH_DEVELOPMENT",
            evidence=[
                ScenarioEvidence(
                    name="structure",
                    value="bullish",
                    timestamp="2026-01-01T09:59:00",
                    source="TEST",
                    observed=True,
                    metadata={
                        "evidence_id": "E1"
                    },
                )
            ],
        )

        valid, errors = (
            validate_d12_final_contract(
                contract
            )
        )

        checks["part4_contract_valid"] = (
            valid and not errors
        )

        checks["d13_authority"] = (
            contract.d13_authority == "D13"
        )

        checks["d14_authority"] = (
            contract.d14_future_validation_authority
            == "D14"
        )

        checks["decision_false"] = (
            contract.decision_performed is False
        )

        checks["execution_false"] = (
            contract.execution_authority is False
        )

        checks["scenarios_present"] = (
            len(contract.scenarios) >= 2
        )

    except Exception:
        checks["part4_contract_valid"] = False
        checks["d13_authority"] = False
        checks["d14_authority"] = False
        checks["decision_false"] = False
        checks["execution_false"] = False
        checks["scenarios_present"] = False

    # -------------------------------------------------------------------------
    # Future-data leakage test
    # -------------------------------------------------------------------------

    try:
        future_contract = evaluate_d12_future_scenario(
            market_id="SELF_TEST",
            as_of="2026-01-01T10:00:00",
            current_state="BULLISH_EXPANSION",
            transition_type="BULLISH_DEVELOPMENT",
            evidence=[
                ScenarioEvidence(
                    name="future_observation",
                    value="future",
                    timestamp="2026-01-01T10:01:00",
                    source="TEST",
                    observed=True,
                )
            ],
        )

        checks["future_data_blocked"] = (
            future_contract.status
            == D12Status.BLOCKED.value
        )

    except Exception:
        checks["future_data_blocked"] = False

    # -------------------------------------------------------------------------
    # No internal probability test
    # -------------------------------------------------------------------------

    try:
        checks["no_fabricated_probability"] = all(
            item.probability is None
            for item in contract.scenarios
        )

    except Exception:
        checks["no_fabricated_probability"] = False

    # -------------------------------------------------------------------------
    # D13 handoff test
    # -------------------------------------------------------------------------

    try:
        handoff = d12_to_d13_handoff(
            contract
        )

        checks["handoff_created"] = (
            handoff.decision_authority
            == "D13"
        )

        checks["handoff_no_decision"] = (
            handoff.decision_performed
            is False
        )

    except Exception:
        checks["handoff_created"] = False
        checks["handoff_no_decision"] = False

    checks["all_pass"] = all(
        checks.values()
    )

    return checks


# =============================================================================
# 4.10 — FACTORY
# =============================================================================

def create_full_d12_future_scenario_engine(
    allow_external_probabilities: bool = False,
) -> D12FinalPipeline:

    return D12FinalPipeline(
        allow_external_probabilities=(
            allow_external_probabilities
        )
    )


def create_d12_pipeline(
    allow_external_probabilities: bool = False,
) -> D12FinalPipeline:

    return create_full_d12_future_scenario_engine(
        allow_external_probabilities=(
            allow_external_probabilities
        )
    )


# =============================================================================
# 4.11 — FINAL PUBLIC EXPORTS
# =============================================================================

D12_FINAL_EXPORTS = (
    "D12FinalContract",
    "D12D13Handoff",
    "D12FinalPipeline",
    "d12_scenario_to_dict",
    "d12_contract_to_dict",
    "validate_d12_final_contract",
    "resolve_d12_final_status",
    "build_d12_final_contract",
    "d12_to_d13_handoff",
    "d12_d13_handoff_to_dict",
    "evaluate_d12_future_scenario",
    "evaluate_d12_future_scenario_dict",
    "d12_complete_self_check",
    "create_full_d12_future_scenario_engine",
    "create_d12_pipeline",
)


# =============================================================================
# END — D12 PART 4/4
# =============================================================================
#
# D12 COMPLETE ARCHITECTURE
#
# D10 → CURRENT MARKET STATE
# D11 → TRANSITION
# D12 → FUTURE / SCENARIO BRANCHES
# D13 → DECISION AUTHORITY
# D14 → FUTURE OUTCOME VALIDATION
# D15 → LEARNING
# D16 → FINAL INTELLIGENCE SYNTHESIS
#
# D12 NEVER BECOMES D13.
# =============================================================================