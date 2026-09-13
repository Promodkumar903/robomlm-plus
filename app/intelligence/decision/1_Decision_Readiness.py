# ============================================================
# ROBOMLM V6
# D1 — DECISION STATE ENGINE
# ============================================================
#
# Decision Cortex / D1
#
# Purpose:
#   Convert evidence/context readiness into a deterministic
#   Decision State without prematurely forcing BUY/SELL.
#
# Mathematical foundation recovered from ROBOMLM research:
#
#   DR(T) = W(T) * (1-U(T))
#           * (1-exp(-alpha*tau(T)))
#           * exp(-beta*T)
#
#   DR_norm = DR / DR_max
#
# Interpretation:
#   >= 0.80  -> DECISION_READY
#   >= 0.50  -> MORE_EVIDENCE
#   <  0.50  -> RESEARCH_REQUIRED
#
# Important:
#   This engine does NOT perform execution.
#   This engine does NOT hide risk inside the decision.
#   This engine does NOT invent direction.
#
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from math import exp, isfinite
from typing import Any, Dict, Optional


ENGINE_NAME = "D1 Decision State Engine"
ENGINE_VERSION = "V6"

# Research thresholds
DECISION_READY_THRESHOLD = 0.80
MORE_EVIDENCE_THRESHOLD = 0.50


# ============================================================
# DECISION STATES
# ============================================================

class DecisionState(str, Enum):
    RESEARCH_REQUIRED = "RESEARCH_REQUIRED"
    MORE_EVIDENCE = "MORE_EVIDENCE"
    DECISION_READY = "DECISION_READY"


# ============================================================
# INPUT MODEL
# ============================================================

@dataclass(frozen=True)
class D1Input:
    """
    D1 mathematical inputs.

    W:
        Evidence Weight / confidence in available evidence.
        Normalized 0..1.

    U:
        Remaining uncertainty.
        Normalized 0..1.

    tau:
        Opportunity Lifetime / remaining decision time.
        Seconds.

    alpha:
        Opportunity decay sensitivity.

    beta:
        Time-pressure decay coefficient.

    T:
        Elapsed / time-pressure variable used by the dynamic
        decision-readiness equation.
        Seconds.

    Optional metadata is retained for auditability.
    """

    evidence_weight: float
    uncertainty: float
    opportunity_lifetime: float
    alpha: float
    beta: float
    time_pressure: float

    # Optional upstream context
    evidence_valid: bool = True
    context_available: bool = True
    risk_available: bool = True

    market: Optional[str] = None
    instrument: Optional[str] = None
    venue: Optional[str] = None
    contract: Optional[str] = None


# ============================================================
# OUTPUT MODEL
# ============================================================

@dataclass(frozen=True)
class D1Result:
    engine: str
    version: str

    decision_state: str

    dr_raw: float
    dr_normalized: float

    evidence_weight: float
    uncertainty: float
    certainty: float

    opportunity_lifetime: float
    opportunity_factor: float

    time_pressure: float
    time_decay_factor: float

    blockers: tuple
    diagnostics: Dict[str, Any]

    market: Optional[str]
    instrument: Optional[str]
    venue: Optional[str]
    contract: Optional[str]


# ============================================================
# VALIDATION
# ============================================================

def _finite(name: str, value: float) -> float:
    value = float(value)

    if not isfinite(value):
        raise ValueError(f"{name} must be finite")

    return value


def _bounded(
    name: str,
    value: float,
    low: float,
    high: float,
) -> float:

    value = _finite(name, value)

    if value < low or value > high:
        raise ValueError(
            f"{name} must be between {low} and {high}"
        )

    return value


def validate_input(data: D1Input) -> None:

    _bounded(
        "evidence_weight",
        data.evidence_weight,
        0.0,
        1.0,
    )

    _bounded(
        "uncertainty",
        data.uncertainty,
        0.0,
        1.0,
    )

    _finite(
        "opportunity_lifetime",
        data.opportunity_lifetime,
    )

    _finite(
        "alpha",
        data.alpha,
    )

    _finite(
        "beta",
        data.beta,
    )

    _finite(
        "time_pressure",
        data.time_pressure,
    )

    if data.opportunity_lifetime < 0:
        raise ValueError(
            "opportunity_lifetime must be >= 0"
        )

    if data.alpha < 0:
        raise ValueError(
            "alpha must be >= 0"
        )

    if data.beta < 0:
        raise ValueError(
            "beta must be >= 0"
        )

    if data.time_pressure < 0:
        raise ValueError(
            "time_pressure must be >= 0"
        )


# ============================================================
# MATHEMATICAL COMPONENTS
# ============================================================

def evidence_factor(evidence_weight: float) -> float:
    """
    W(T)

    Evidence confidence factor.
    """

    return _bounded(
        "evidence_weight",
        evidence_weight,
        0.0,
        1.0,
    )


def certainty_factor(uncertainty: float) -> float:
    """
    1 - U(T)

    Uncertainty directly reduces decision readiness.
    """

    uncertainty = _bounded(
        "uncertainty",
        uncertainty,
        0.0,
        1.0,
    )

    return 1.0 - uncertainty


def opportunity_factor(
    opportunity_lifetime: float,
    alpha: float,
) -> float:
    """
    1 - exp(-alpha * tau)

    Opportunity lifetime contribution.
    """

    tau = _finite(
        "opportunity_lifetime",
        opportunity_lifetime,
    )

    alpha = _finite(
        "alpha",
        alpha,
    )

    if tau < 0:
        raise ValueError(
            "opportunity_lifetime must be >= 0"
        )

    if alpha < 0:
        raise ValueError(
            "alpha must be >= 0"
        )

    return 1.0 - exp(
        -alpha * tau
    )


def time_decay_factor(
    beta: float,
    time_pressure: float,
) -> float:
    """
    exp(-beta * T)

    Dynamic time-pressure decay.
    """

    beta = _finite(
        "beta",
        beta,
    )

    time_pressure = _finite(
        "time_pressure",
        time_pressure,
    )

    if beta < 0:
        raise ValueError(
            "beta must be >= 0"
        )

    if time_pressure < 0:
        raise ValueError(
            "time_pressure must be >= 0"
        )

    return exp(
        -beta * time_pressure
    )


# ============================================================
# RAW DECISION READINESS
# ============================================================

def calculate_dr(data: D1Input) -> Dict[str, float]:
    """
    Calculate the recovered Decision Readiness equation.

        DR =
            W
            * (1-U)
            * (1-exp(-alpha*tau))
            * exp(-beta*T)
    """

    validate_input(data)

    W = evidence_factor(
        data.evidence_weight
    )

    certainty = certainty_factor(
        data.uncertainty
    )

    opportunity = opportunity_factor(
        data.opportunity_lifetime,
        data.alpha,
    )

    time_decay = time_decay_factor(
        data.beta,
        data.time_pressure,
    )

    dr = (
        W
        * certainty
        * opportunity
        * time_decay
    )

    # Mathematical safety clamp.
    dr = max(
        0.0,
        min(1.0, dr),
    )

    return {
        "dr_raw": dr,
        "evidence_factor": W,
        "certainty_factor": certainty,
        "opportunity_factor": opportunity,
        "time_decay_factor": time_decay,
    }


# ============================================================
# STATE CLASSIFICATION
# ============================================================

def classify_state(
    dr_normalized: float,
) -> DecisionState:

    dr_normalized = _bounded(
        "dr_normalized",
        dr_normalized,
        0.0,
        1.0,
    )

    if dr_normalized >= DECISION_READY_THRESHOLD:
        return DecisionState.DECISION_READY

    if dr_normalized >= MORE_EVIDENCE_THRESHOLD:
        return DecisionState.MORE_EVIDENCE

    return DecisionState.RESEARCH_REQUIRED


# ============================================================
# BLOCKER ANALYSIS
# ============================================================

def collect_blockers(
    data: D1Input,
    dr_normalized: float,
) -> list[str]:

    blockers: list[str] = []

    if not data.evidence_valid:
        blockers.append(
            "EVIDENCE_INVALID"
        )

    if not data.context_available:
        blockers.append(
            "CONTEXT_UNAVAILABLE"
        )

    if not data.risk_available:
        blockers.append(
            "RISK_UNAVAILABLE"
        )

    if data.uncertainty >= 1.0:
        blockers.append(
            "MAXIMUM_UNCERTAINTY"
        )

    if data.opportunity_lifetime <= 0:
        blockers.append(
            "OPPORTUNITY_EXPIRED"
        )

    if dr_normalized < MORE_EVIDENCE_THRESHOLD:
        blockers.append(
            "DECISION_READINESS_LOW"
        )

    return blockers


# ============================================================
# MAIN ENGINE
# ============================================================

def evaluate_d1(
    data: D1Input,
) -> D1Result:

    values = calculate_dr(data)

    dr_raw = values["dr_raw"]

    # DR_max = 1 under normalized bounded formulation.
    dr_normalized = dr_raw

    state = classify_state(
        dr_normalized
    )

    blockers = collect_blockers(
        data,
        dr_normalized,
    )

    # A missing foundational dependency prevents the engine
    # from declaring a clean ready state.
    if (
        not data.evidence_valid
        or not data.context_available
        or not data.risk_available
    ):
        state = DecisionState.RESEARCH_REQUIRED

    diagnostics = {
        "formula": (
            "DR = W*(1-U)"
            "*(1-exp(-alpha*tau))"
            "*exp(-beta*T)"
        ),
        "normalization": (
            "DR_normalized = DR / DR_max"
        ),
        "dr_max": 1.0,

        "decision_ready_threshold":
            DECISION_READY_THRESHOLD,

        "more_evidence_threshold":
            MORE_EVIDENCE_THRESHOLD,

        "formula_components": {
            "W": data.evidence_weight,
            "U": data.uncertainty,
            "tau": data.opportunity_lifetime,
            "alpha": data.alpha,
            "beta": data.beta,
            "T": data.time_pressure,
        },

        "principle":
            "Decision readiness is not the directional decision.",

        "execution_allowed":
            False,

        "direction_generated":
            False,

        "risk_hidden_inside_decision":
            False,
    }

    return D1Result(
        engine=ENGINE_NAME,
        version=ENGINE_VERSION,

        decision_state=state.value,

        dr_raw=round(dr_raw, 8),
        dr_normalized=round(
            dr_normalized,
            8,
        ),

        evidence_weight=
            data.evidence_weight,

        uncertainty=
            data.uncertainty,

        certainty=
            values["certainty_factor"],

        opportunity_lifetime=
            data.opportunity_lifetime,

        opportunity_factor=
            values["opportunity_factor"],

        time_pressure=
            data.time_pressure,

        time_decay_factor=
            values["time_decay_factor"],

        blockers=tuple(blockers),

        diagnostics=diagnostics,

        market=data.market,
        instrument=data.instrument,
        venue=data.venue,
        contract=data.contract,
    )


# ============================================================
# SERIALIZATION
# ============================================================

def result_to_dict(
    result: D1Result,
) -> Dict[str, Any]:

    return asdict(result)


# ============================================================
# SELF TESTS
# ============================================================

def run_self_tests() -> None:

    # --------------------------------------------------------
    # Test 1:
    # No evidence
    # --------------------------------------------------------

    data = D1Input(
        evidence_weight=0.0,
        uncertainty=0.0,
        opportunity_lifetime=100.0,
        alpha=0.1,
        beta=0.0,
        time_pressure=0.0,
    )

    result = evaluate_d1(data)

    assert result.dr_normalized == 0.0
    assert (
        result.decision_state
        == "RESEARCH_REQUIRED"
    )

    # --------------------------------------------------------
    # Test 2:
    # Maximum uncertainty
    # --------------------------------------------------------

    data = D1Input(
        evidence_weight=1.0,
        uncertainty=1.0,
        opportunity_lifetime=100.0,
        alpha=0.1,
        beta=0.0,
        time_pressure=0.0,
    )

    result = evaluate_d1(data)

    assert result.dr_normalized == 0.0
    assert (
        result.decision_state
        == "RESEARCH_REQUIRED"
    )

    # --------------------------------------------------------
    # Test 3:
    # No remaining opportunity lifetime
    # --------------------------------------------------------

    data = D1Input(
        evidence_weight=1.0,
        uncertainty=0.0,
        opportunity_lifetime=0.0,
        alpha=0.1,
        beta=0.0,
        time_pressure=0.0,
    )

    result = evaluate_d1(data)

    assert result.dr_normalized == 0.0
    assert (
        result.decision_state
        == "RESEARCH_REQUIRED"
    )

    # --------------------------------------------------------
    # Test 4:
    # More-evidence region
    # --------------------------------------------------------

    data = D1Input(
        evidence_weight=0.8,
        uncertainty=0.2,
        opportunity_lifetime=10.0,
        alpha=0.1,
        beta=0.01,
        time_pressure=1.0,
    )

    result = evaluate_d1(data)

    assert (
        0.0
        <= result.dr_normalized
        <= 1.0
    )

    # --------------------------------------------------------
    # Test 5:
    # High readiness
    # --------------------------------------------------------

    data = D1Input(
        evidence_weight=1.0,
        uncertainty=0.0,
        opportunity_lifetime=1000.0,
        alpha=1.0,
        beta=0.0,
        time_pressure=0.0,
    )

    result = evaluate_d1(data)

    assert result.dr_normalized > 0.80
    assert (
        result.decision_state
        == "DECISION_READY"
    )

    # --------------------------------------------------------
    # Test 6:
    # Dependency blocker
    # --------------------------------------------------------

    data = D1Input(
        evidence_weight=1.0,
        uncertainty=0.0,
        opportunity_lifetime=1000.0,
        alpha=1.0,
        beta=0.0,
        time_pressure=0.0,
        evidence_valid=False,
    )

    result = evaluate_d1(data)

    assert (
        result.decision_state
        == "RESEARCH_REQUIRED"
    )

    assert (
        "EVIDENCE_INVALID"
        in result.blockers
    )

    print(
        "ROBOMLM D1 self-tests: PASS"
    )


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    run_self_tests()

    sample = D1Input(
        evidence_weight=0.92,
        uncertainty=0.12,
        opportunity_lifetime=30.0,
        alpha=0.10,
        beta=0.01,
        time_pressure=2.0,

        evidence_valid=True,
        context_available=True,
        risk_available=True,

        market="NIFTY",
        instrument="NIFTY",
        venue="UNKNOWN",
        contract="UNKNOWN",
    )

    result = evaluate_d1(sample)

    print()
    print("=" * 60)
    print("ROBOMLM V6 — D1 DECISION STATE ENGINE")
    print("=" * 60)
    print(
        "Decision State :",
        result.decision_state,
    )
    print(
        "DR Raw         :",
        result.dr_raw,
    )
    print(
        "DR Normalized  :",
        result.dr_normalized,
    )
    print(
        "Evidence       :",
        result.evidence_weight,
    )
    print(
        "Uncertainty    :",
        result.uncertainty,
    )
    print(
        "Opportunity    :",
        result.opportunity_factor,
    )
    print(
        "Time Decay     :",
        result.time_decay_factor,
    )
    print(
        "Blockers       :",
        list(result.blockers),
    )