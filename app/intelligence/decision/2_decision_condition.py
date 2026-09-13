# ============================================================
# ROBOMLM V6
# D2 — DECISION CONDITION ENGINE
# ============================================================
#
# Purpose:
#   Evaluate whether the current evidence/context state satisfies
#   the conditions required to move toward a directional decision.
#
# D2 does NOT:
#   - execute trades
#   - calculate position size
#   - override risk
#   - convert one metric directly into BUY/SELL
#
# It preserves:
#   Evidence -> Context -> Conditions -> Decision qualification
#
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict, Optional


ENGINE_NAME = "D2 Decision Condition Engine"
ENGINE_VERSION = "V6"

MIN_EVIDENCE_STRENGTH = 0.60
MIN_CONTEXT_STRENGTH = 0.60
MAX_ALLOWED_UNCERTAINTY = 0.40

# Metric qualification thresholds.
# These remain configuration, not permanent architectural locks.
DEFAULT_EQE_THRESHOLD = 80.0
DEFAULT_TPS_THRESHOLD = 60.0
DEFAULT_MTS_THRESHOLD = 60.0
DEFAULT_LQS_THRESHOLD = 60.0
DEFAULT_PFS_THRESHOLD = 60.0

# RDS is a risk-density measure: lower is better.
DEFAULT_MAX_RDS = 60.0


class ConditionStatus(str, Enum):
    QUALIFIED = "QUALIFIED"
    PARTIAL = "PARTIAL"
    NOT_QUALIFIED = "NOT_QUALIFIED"
    BLOCKED = "BLOCKED"


class Direction(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class D2Input:
    """
    Inputs supplied by upstream Evidence / Context / Metric engines.

    Scores are normalized to 0..100 unless explicitly documented
    otherwise.
    """

    evidence_strength: float
    context_strength: float
    uncertainty: float

    eqe: float
    tps: float
    mts: float
    lqs: float
    pfs: float
    rds: float

    # Directional evidence.
    bullish_evidence: float = 0.0
    bearish_evidence: float = 0.0

    # Dependency state.
    evidence_valid: bool = True
    context_valid: bool = True
    market_identity_valid: bool = True
    instrument_identity_valid: bool = True
    data_fresh: bool = True

    market: Optional[str] = None
    instrument: Optional[str] = None
    venue: Optional[str] = None
    contract: Optional[str] = None


@dataclass(frozen=True)
class ConditionResult:
    engine: str
    version: str

    status: str
    direction: str

    qualified_conditions: tuple
    failed_conditions: tuple
    blockers: tuple

    qualification_ratio: float

    evidence_strength: float
    context_strength: float
    uncertainty: float

    metric_state: Dict[str, bool]
    directional_state: Dict[str, float]

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

    if not value == value:
        raise ValueError(f"{name} must not be NaN")

    if value in (float("inf"), float("-inf")):
        raise ValueError(f"{name} must be finite")

    return value


def _score(name: str, value: float) -> float:
    value = _finite(name, value)

    if not 0.0 <= value <= 100.0:
        raise ValueError(
            f"{name} must be between 0 and 100"
        )

    return value


def _ratio(name: str, value: float) -> float:
    value = _finite(name, value)

    if not 0.0 <= value <= 1.0:
        raise ValueError(
            f"{name} must be between 0 and 1"
        )

    return value


def validate_input(data: D2Input) -> None:

    _ratio(
        "evidence_strength",
        data.evidence_strength,
    )

    _ratio(
        "context_strength",
        data.context_strength,
    )

    _ratio(
        "uncertainty",
        data.uncertainty,
    )

    for name in (
        "eqe",
        "tps",
        "mts",
        "lqs",
        "pfs",
        "rds",
        "bullish_evidence",
        "bearish_evidence",
    ):
        _score(
            name,
            getattr(data, name),
        )


# ============================================================
# DIRECTION RESOLUTION
# ============================================================

def resolve_direction(
    bullish_evidence: float,
    bearish_evidence: float,
) -> Direction:
    """
    Direction is resolved only when one side has greater evidence.

    Equal evidence remains unresolved.
    No arbitrary bullish/bearish default is introduced.
    """

    bullish = _score(
        "bullish_evidence",
        bullish_evidence,
    )

    bearish = _score(
        "bearish_evidence",
        bearish_evidence,
    )

    if bullish == bearish:
        return Direction.UNRESOLVED

    if bullish > bearish:
        return Direction.BULLISH

    return Direction.BEARISH


# ============================================================
# CONDITION EVALUATION
# ============================================================

def evaluate_conditions(
    data: D2Input,
    eqe_threshold: float = DEFAULT_EQE_THRESHOLD,
    tps_threshold: float = DEFAULT_TPS_THRESHOLD,
    mts_threshold: float = DEFAULT_MTS_THRESHOLD,
    lqs_threshold: float = DEFAULT_LQS_THRESHOLD,
    pfs_threshold: float = DEFAULT_PFS_THRESHOLD,
    max_rds: float = DEFAULT_MAX_RDS,
) -> ConditionResult:

    validate_input(data)

    thresholds = {
        "eqe": _score(
            "eqe_threshold",
            eqe_threshold,
        ),
        "tps": _score(
            "tps_threshold",
            tps_threshold,
        ),
        "mts": _score(
            "mts_threshold",
            mts_threshold,
        ),
        "lqs": _score(
            "lqs_threshold",
            lqs_threshold,
        ),
        "pfs": _score(
            "pfs_threshold",
            pfs_threshold,
        ),
        "max_rds": _score(
            "max_rds",
            max_rds,
        ),
    }

    # --------------------------------------------------------
    # Hard dependency blockers
    # --------------------------------------------------------

    blockers = []

    if not data.evidence_valid:
        blockers.append("EVIDENCE_INVALID")

    if not data.context_valid:
        blockers.append("CONTEXT_INVALID")

    if not data.market_identity_valid:
        blockers.append("MARKET_IDENTITY_INVALID")

    if not data.instrument_identity_valid:
        blockers.append("INSTRUMENT_IDENTITY_INVALID")

    if not data.data_fresh:
        blockers.append("DATA_STALE")

    if data.uncertainty > MAX_ALLOWED_UNCERTAINTY:
        blockers.append("UNCERTAINTY_TOO_HIGH")

    # --------------------------------------------------------
    # Base conditions
    # --------------------------------------------------------

    conditions = {
        "evidence_strength":
            data.evidence_strength
            >= MIN_EVIDENCE_STRENGTH,

        "context_strength":
            data.context_strength
            >= MIN_CONTEXT_STRENGTH,

        "eqe":
            data.eqe
            >= thresholds["eqe"],

        "tps":
            data.tps
            >= thresholds["tps"],

        "mts":
            data.mts
            >= thresholds["mts"],

        "lqs":
            data.lqs
            >= thresholds["lqs"],

        "pfs":
            data.pfs
            >= thresholds["pfs"],

        # RDS is inverse-risk logic:
        # lower RDS = better condition.
        "rds":
            data.rds
            <= thresholds["max_rds"],
    }

    qualified = [
        name
        for name, passed in conditions.items()
        if passed
    ]

    failed = [
        name
        for name, passed in conditions.items()
        if not passed
    ]

    qualification_ratio = (
        len(qualified)
        / len(conditions)
        if conditions
        else 0.0
    )

    direction = resolve_direction(
        data.bullish_evidence,
        data.bearish_evidence,
    )

    # --------------------------------------------------------
    # State classification
    # --------------------------------------------------------

    if blockers:
        status = ConditionStatus.BLOCKED

    elif qualification_ratio >= 1.0:
        status = ConditionStatus.QUALIFIED

    elif qualification_ratio >= 0.50:
        status = ConditionStatus.PARTIAL

    else:
        status = ConditionStatus.NOT_QUALIFIED

    # A directional decision cannot be considered fully
    # qualified when directional evidence itself is unresolved.
    if (
        status == ConditionStatus.QUALIFIED
        and direction == Direction.UNRESOLVED
    ):
        status = ConditionStatus.PARTIAL

    diagnostics = {
        "formula": (
            "qualification_ratio = "
            "qualified_conditions / total_conditions"
        ),

        "condition_count":
            len(conditions),

        "qualified_count":
            len(qualified),

        "failed_count":
            len(failed),

        "thresholds":
            thresholds,

        "base_thresholds": {
            "minimum_evidence_strength":
                MIN_EVIDENCE_STRENGTH,

            "minimum_context_strength":
                MIN_CONTEXT_STRENGTH,

            "maximum_allowed_uncertainty":
                MAX_ALLOWED_UNCERTAINTY,
        },

        "rds_rule":
            "RDS <= max_rds",

        "direction_rule":
            "greater directional evidence wins; equal = UNRESOLVED",

        "execution_allowed":
            False,

        "risk_override":
            False,

        "downstream_required": [
            "D3_DECISION_CONFIDENCE",
            "RISK_ENGINE",
            "EXECUTION_APPROVAL",
        ],
    }

    return ConditionResult(
        engine=ENGINE_NAME,
        version=ENGINE_VERSION,

        status=status.value,
        direction=direction.value,

        qualified_conditions=tuple(
            qualified
        ),

        failed_conditions=tuple(
            failed
        ),

        blockers=tuple(
            blockers
        ),

        qualification_ratio=round(
            qualification_ratio,
            6,
        ),

        evidence_strength=
            data.evidence_strength,

        context_strength=
            data.context_strength,

        uncertainty=
            data.uncertainty,

        metric_state=conditions,

        directional_state={
            "bullish": data.bullish_evidence,
            "bearish": data.bearish_evidence,
        },

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
    result: ConditionResult,
) -> Dict[str, Any]:

    return asdict(result)


# ============================================================
# SELF TESTS
# ============================================================

def run_self_tests() -> None:

    # --------------------------------------------------------
    # Test 1 — fully qualified
    # --------------------------------------------------------

    data = D2Input(
        evidence_strength=0.90,
        context_strength=0.90,
        uncertainty=0.10,

        eqe=90,
        tps=80,
        mts=80,
        lqs=80,
        pfs=80,
        rds=20,

        bullish_evidence=85,
        bearish_evidence=30,
    )

    result = evaluate_conditions(data)

    assert result.status == "QUALIFIED"
    assert result.direction == "BULLISH"
    assert result.qualification_ratio == 1.0

    # --------------------------------------------------------
    # Test 2 — partial
    # --------------------------------------------------------

    data = D2Input(
        evidence_strength=0.70,
        context_strength=0.70,
        uncertainty=0.20,

        eqe=85,
        tps=40,
        mts=70,
        lqs=80,
        pfs=30,
        rds=30,

        bullish_evidence=70,
        bearish_evidence=20,
    )

    result = evaluate_conditions(data)

    assert result.status == "PARTIAL"
    assert result.direction == "BULLISH"

    # --------------------------------------------------------
    # Test 3 — unresolved direction
    # --------------------------------------------------------

    data = D2Input(
        evidence_strength=0.90,
        context_strength=0.90,
        uncertainty=0.10,

        eqe=90,
        tps=80,
        mts=80,
        lqs=80,
        pfs=80,
        rds=20,

        bullish_evidence=70,
        bearish_evidence=70,
    )

    result = evaluate_conditions(data)

    assert result.direction == "UNRESOLVED"
    assert result.status == "PARTIAL"

    # --------------------------------------------------------
    # Test 4 — stale data blocker
    # --------------------------------------------------------

    data = D2Input(
        evidence_strength=1.0,
        context_strength=1.0,
        uncertainty=0.0,

        eqe=100,
        tps=100,
        mts=100,
        lqs=100,
        pfs=100,
        rds=0,

        bullish_evidence=90,
        bearish_evidence=10,

        data_fresh=False,
    )

    result = evaluate_conditions(data)

    assert result.status == "BLOCKED"
    assert "DATA_STALE" in result.blockers

    # --------------------------------------------------------
    # Test 5 — high uncertainty blocker
    # --------------------------------------------------------

    data = D2Input(
        evidence_strength=1.0,
        context_strength=1.0,
        uncertainty=0.80,

        eqe=100,
        tps=100,
        mts=100,
        lqs=100,
        pfs=100,
        rds=0,

        bullish_evidence=90,
        bearish_evidence=10,
    )

    result = evaluate_conditions(data)

    assert result.status == "BLOCKED"
    assert "UNCERTAINTY_TOO_HIGH" in result.blockers

    # --------------------------------------------------------
    # Test 6 — invalid identity
    # --------------------------------------------------------

    data = D2Input(
        evidence_strength=1.0,
        context_strength=1.0,
        uncertainty=0.0,

        eqe=100,
        tps=100,
        mts=100,
        lqs=100,
        pfs=100,
        rds=0,

        bullish_evidence=90,
        bearish_evidence=10,

        instrument_identity_valid=False,
    )

    result = evaluate_conditions(data)

    assert result.status == "BLOCKED"
    assert (
        "INSTRUMENT_IDENTITY_INVALID"
        in result.blockers
    )

    print(
        "ROBOMLM D2 self-tests: PASS"
    )


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    run_self_tests()

    sample = D2Input(
        evidence_strength=0.88,
        context_strength=0.84,
        uncertainty=0.15,

        eqe=86,
        tps=76,
        mts=72,
        lqs=81,
        pfs=74,
        rds=24,

        bullish_evidence=82,
        bearish_evidence=35,

        market="NIFTY",
        instrument="NIFTY",
        venue="UNKNOWN",
        contract="UNKNOWN",
    )

    result = evaluate_conditions(sample)

    print()
    print("=" * 60)
    print("ROBOMLM V6 — D2 DECISION CONDITION ENGINE")
    print("=" * 60)
    print(
        "Status            :",
        result.status,
    )
    print(
        "Direction         :",
        result.direction,
    )
    print(
        "Qualification     :",
        result.qualification_ratio,
    )
    print(
        "Qualified         :",
        list(result.qualified_conditions),
    )
    print(
        "Failed            :",
        list(result.failed_conditions),
    )
    print(
        "Blockers          :",
        list(result.blockers),
    )