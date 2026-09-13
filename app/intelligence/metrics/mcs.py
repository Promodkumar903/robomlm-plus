"""
ROBOMLM_PLUS
MCS â€” Market Context Score

V6 implementation.

CANONICAL D6 SOURCE
-------------------

The D6 research defines the Market Context Intelligence (MCI)
framework as the canonical eight-dimensional market-context
aggregation.

MCS is the implementation-facing score representation of that
canonical Market Context Intelligence calculation.

Formula
-------

RiskContext = 100 - RDS

MCS =
    Trend          * 0.20
    + Volume       * 0.15
    + Liquidity    * 0.15
    + RiskContext  * 0.15
    + Timing       * 0.10
    + Derivatives  * 0.10
    + Participation* 0.10
    + Relationships* 0.05

All component values are canonical 0..100.

No missing component is guessed.

No BUY/SELL is generated.

No execution authority is generated.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import isfinite
from typing import Any, Mapping, Optional


# ============================================================================
# CONSTANTS
# ============================================================================

ENGINE_NAME = "MCS"
ENGINE_VERSION = "V6"

MIN_SCORE = 0.0
MAX_SCORE = 100.0

TREND_WEIGHT = 0.20
VOLUME_WEIGHT = 0.15
LIQUIDITY_WEIGHT = 0.15
RISK_WEIGHT = 0.15
TIMING_WEIGHT = 0.10
DERIVATIVES_WEIGHT = 0.10
PARTICIPATION_WEIGHT = 0.10
RELATIONSHIPS_WEIGHT = 0.05

WEIGHTS = {
    "trend": TREND_WEIGHT,
    "volume": VOLUME_WEIGHT,
    "liquidity": LIQUIDITY_WEIGHT,
    "risk": RISK_WEIGHT,
    "timing": TIMING_WEIGHT,
    "derivatives": DERIVATIVES_WEIGHT,
    "participation": PARTICIPATION_WEIGHT,
    "relationships": RELATIONSHIPS_WEIGHT,
}


# ============================================================================
# STATUS
# ============================================================================

class MCSStatus(str, Enum):
    VALID = "VALID"
    INSUFFICIENT = "INSUFFICIENT"
    INVALID = "INVALID"


# ============================================================================
# CONTEXT
# ============================================================================

class MCSContext(str, Enum):
    STRONG_CONTEXT = "STRONG_CONTEXT"
    CONSTRUCTIVE = "CONSTRUCTIVE"
    NEUTRAL = "NEUTRAL"
    WEAK = "WEAK"
    DANGER_ZONE = "DANGER_ZONE"


# ============================================================================
# COMPONENT
# ============================================================================

@dataclass(frozen=True)
class MCSComponent:

    name: str

    raw_value: float

    context_value: float

    weight: float

    weighted_contribution: float

    transformation: str = "IDENTITY"

    source: Optional[str] = None

    def as_dict(self) -> dict[str, Any]:

        return {
            "name":
                self.name,

            "raw_value":
                self.raw_value,

            "context_value":
                self.context_value,

            "weight":
                self.weight,

            "weighted_contribution":
                self.weighted_contribution,

            "transformation":
                self.transformation,

            "source":
                self.source,
        }


# ============================================================================
# INPUT
# ============================================================================

@dataclass(frozen=True)
class MCSInput:

    trend: Optional[float] = None

    volume: Optional[float] = None

    liquidity: Optional[float] = None

    # RDS:
    # 0 = lower risk
    # 100 = higher risk
    risk_density: Optional[float] = None

    timing: Optional[float] = None

    derivatives: Optional[float] = None

    participation: Optional[float] = None

    relationships: Optional[float] = None

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )


# ============================================================================
# D13 FACING STATE
# ============================================================================

@dataclass(frozen=True)
class MCSState:

    mcs: Optional[float]

    context: Optional[MCSContext]

    trend: Optional[float]

    volume: Optional[float]

    liquidity: Optional[float]

    risk_density: Optional[float]

    risk_context: Optional[float]

    timing: Optional[float]

    derivatives: Optional[float]

    participation: Optional[float]

    relationships: Optional[float]

    decision_authority: str = "NONE"

    source_engine: str = ENGINE_NAME

    source_version: str = ENGINE_VERSION

    provenance: Mapping[str, Any] = field(
        default_factory=dict
    )

    def as_dict(self) -> dict[str, Any]:

        return {
            "mcs":
                self.mcs,

            "context":
                self.context.value
                if self.context
                else None,

            "trend":
                self.trend,

            "volume":
                self.volume,

            "liquidity":
                self.liquidity,

            "risk_density":
                self.risk_density,

            "risk_context":
                self.risk_context,

            "timing":
                self.timing,

            "derivatives":
                self.derivatives,

            "participation":
                self.participation,

            "relationships":
                self.relationships,

            "decision_authority":
                self.decision_authority,

            "source_engine":
                self.source_engine,

            "source_version":
                self.source_version,

            "provenance":
                dict(self.provenance),
        }


# ============================================================================
# RESULT
# ============================================================================

@dataclass(frozen=True)
class MCSResult:

    status: MCSStatus

    mcs: Optional[float]

    context: Optional[MCSContext]

    components: tuple[MCSComponent, ...]

    supplied_components: int

    required_components: int

    weighted_sum: Optional[float]

    weight_sum: float

    calculation: str

    errors: tuple[str, ...] = ()

    warnings: tuple[str, ...] = ()

    engine: str = ENGINE_NAME

    version: str = ENGINE_VERSION

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    mcs_state: Optional[MCSState] = None

    @property
    def is_valid(self) -> bool:
        return self.status == MCSStatus.VALID

    @property
    def score(self) -> Optional[float]:
        return self.mcs

    def as_dict(self) -> dict[str, Any]:

        return {
            "status":
                self.status.value,

            "mcs":
                self.mcs,

            "score":
                self.score,

            "context":
                self.context.value
                if self.context
                else None,

            "components": [
                component.as_dict()
                for component in self.components
            ],

            "supplied_components":
                self.supplied_components,

            "required_components":
                self.required_components,

            "weighted_sum":
                self.weighted_sum,

            "weight_sum":
                self.weight_sum,

            "calculation":
                self.calculation,

            "errors":
                list(self.errors),

            "warnings":
                list(self.warnings),

            "engine":
                self.engine,

            "version":
                self.version,

            "metadata":
                dict(self.metadata),

            "mcs_state":
                None
                if self.mcs_state is None
                else self.mcs_state.as_dict(),
        }


# ============================================================================
# ENGINE
# ============================================================================

class MCSEngine:

    REQUIRED_COMPONENTS = (
        "trend",
        "volume",
        "liquidity",
        "risk_density",
        "timing",
        "derivatives",
        "participation",
        "relationships",
    )

    CALCULATION = (
        "RiskContext = 100 - RDS; "
        "MCS = "
        "Trend*0.20 "
        "+ Volume*0.15 "
        "+ Liquidity*0.15 "
        "+ RiskContext*0.15 "
        "+ Timing*0.10 "
        "+ Derivatives*0.10 "
        "+ Participation*0.10 "
        "+ Relationships*0.05"
    )

    def __init__(self) -> None:

        self.weights = dict(
            WEIGHTS
        )

        self._validate_weights()

    # ------------------------------------------------------------------------
    # MAIN
    # ------------------------------------------------------------------------

    def calculate(
        self,
        inputs: MCSInput,
    ) -> MCSResult:

        if not isinstance(
            inputs,
            MCSInput,
        ):
            return self._invalid(
                "inputs must be MCSInput"
            )

        raw_values = {
            "trend":
                inputs.trend,

            "volume":
                inputs.volume,

            "liquidity":
                inputs.liquidity,

            "risk_density":
                inputs.risk_density,

            "timing":
                inputs.timing,

            "derivatives":
                inputs.derivatives,

            "participation":
                inputs.participation,

            "relationships":
                inputs.relationships,
        }

        errors: list[str] = []

        # ------------------------------------------------------------------
        # VALIDATE
        # ------------------------------------------------------------------

        for name, value in raw_values.items():

            if value is None:
                continue

            error = self._validate_score(
                value,
                name,
            )

            if error:
                errors.append(error)

        if errors:
            return self._invalid(
                *errors
            )

        supplied_count = sum(
            value is not None
            for value in raw_values.values()
        )

        # ------------------------------------------------------------------
        # MISSING INPUT
        # ------------------------------------------------------------------

        if supplied_count < len(
            self.REQUIRED_COMPONENTS
        ):

            missing = [
                name
                for name, value
                in raw_values.items()
                if value is None
            ]

            return MCSResult(
                status=MCSStatus.INSUFFICIENT,

                mcs=None,

                context=None,

                components=(),

                supplied_components=
                    supplied_count,

                required_components=
                    len(self.REQUIRED_COMPONENTS),

                weighted_sum=None,

                weight_sum=
                    sum(
                        self.weights.values()
                    ),

                calculation=
                    self.CALCULATION,

                warnings=(
                    "MCS requires all eight "
                    "V6 context dimensions. "
                    "Missing: "
                    + ", ".join(missing),
                ),

                metadata={
                    **dict(inputs.metadata),

                    "missing_components":
                        missing,
                },

                mcs_state=self._build_state(
                    inputs,
                    None,
                    None,
                ),
            )

        # ------------------------------------------------------------------
        # RISK TRANSFORMATION
        # ------------------------------------------------------------------

        risk_density = float(
            inputs.risk_density
        )

        risk_context = (
            100.0
            - risk_density
        )

        # ------------------------------------------------------------------
        # BUILD COMPONENTS
        # ------------------------------------------------------------------

        components: list[MCSComponent] = []

        identity_components = (
            ("trend", inputs.trend),
            ("volume", inputs.volume),
            ("liquidity", inputs.liquidity),
            ("timing", inputs.timing),
            ("derivatives", inputs.derivatives),
            ("participation", inputs.participation),
            ("relationships", inputs.relationships),
        )

        for name, value in identity_components:

            weight = self.weights[name]

            contribution = (
                float(value)
                * weight
            )

            components.append(
                MCSComponent(
                    name=name,

                    raw_value=float(
                        value
                    ),

                    context_value=float(
                        value
                    ),

                    weight=weight,

                    weighted_contribution=
                        contribution,

                    transformation=
                        "IDENTITY",
                )
            )

        risk_weight = self.weights[
            "risk"
        ]

        components.append(
            MCSComponent(
                name="risk",

                raw_value=risk_density,

                context_value=risk_context,

                weight=risk_weight,

                weighted_contribution=(
                    risk_context
                    * risk_weight
                ),

                transformation=
                    "100-RDS",

                source="RDS",
            )
        )

        # ------------------------------------------------------------------
        # WEIGHTED AGGREGATION
        # ------------------------------------------------------------------

        weighted_sum = sum(
            component.weighted_contribution
            for component in components
        )

        if not isfinite(
            weighted_sum
        ):
            return self._invalid(
                "MCS weighted sum must be finite."
            )

        if not (
            MIN_SCORE
            <= weighted_sum
            <= MAX_SCORE
        ):
            return self._invalid(
                "MCS left canonical 0..100 domain."
            )

        context = self._context_from_score(
            weighted_sum
        )

        # ------------------------------------------------------------------
        # FINAL STATE
        # ------------------------------------------------------------------

        state = self._build_state(
            inputs,
            weighted_sum,
            context,
        )

        return MCSResult(
            status=MCSStatus.VALID,

            mcs=weighted_sum,

            context=context,

            components=tuple(
                components
            ),

            supplied_components=
                supplied_count,

            required_components=
                len(self.REQUIRED_COMPONENTS),

            weighted_sum=
                weighted_sum,

            weight_sum=
                sum(
                    self.weights.values()
                ),

            calculation=
                self.CALCULATION,

            metadata={
                **dict(inputs.metadata),

                "risk_transformation":
                    "100-RDS",

                "weight_sum":
                    sum(
                        self.weights.values()
                    ),

                "decision_authority":
                    "NONE",
            },

            mcs_state=state,
        )

    # ------------------------------------------------------------------------
    # CONTEXT
    # ------------------------------------------------------------------------

    @staticmethod
    def _context_from_score(
        score: float,
    ) -> MCSContext:

        if score >= 80.0:
            return MCSContext.STRONG_CONTEXT

        if score >= 60.0:
            return MCSContext.CONSTRUCTIVE

        if score >= 40.0:
            return MCSContext.NEUTRAL

        if score >= 20.0:
            return MCSContext.WEAK

        return MCSContext.DANGER_ZONE

    # ------------------------------------------------------------------------
    # STATE
    # ------------------------------------------------------------------------

    @staticmethod
    def _build_state(
        inputs: MCSInput,
        mcs: Optional[float],
        context: Optional[MCSContext],
    ) -> MCSState:

        risk_context = None

        if inputs.risk_density is not None:

            risk_context = (
                100.0
                - float(
                    inputs.risk_density
                )
            )

        return MCSState(
            mcs=mcs,

            context=context,

            trend=inputs.trend,

            volume=inputs.volume,

            liquidity=inputs.liquidity,

            risk_density=
                inputs.risk_density,

            risk_context=
                risk_context,

            timing=inputs.timing,

            derivatives=inputs.derivatives,

            participation=inputs.participation,

            relationships=inputs.relationships,

            decision_authority="NONE",

            provenance={
                "formula":
                    "D6_MCI_CANONICAL",

                "risk_transformation":
                    "100-RDS",

                "weights":
                    dict(WEIGHTS),

                "decision_authority":
                    "NONE",
            },
        )

    # ------------------------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------------------------

    @staticmethod
    def _validate_score(
        value: Any,
        name: str,
    ) -> Optional[str]:

        if isinstance(
            value,
            bool,
        ):
            return (
                f"{name}: boolean is invalid"
            )

        if not isinstance(
            value,
            (int, float),
        ):
            return (
                f"{name}: expected numeric value"
            )

        value = float(value)

        if not isfinite(
            value
        ):
            return (
                f"{name}: value must be finite"
            )

        if not (
            MIN_SCORE
            <= value
            <= MAX_SCORE
        ):
            return (
                f"{name}: value outside 0..100"
            )

        return None

    def _validate_weights(
        self,
    ) -> None:

        weight_sum = sum(
            self.weights.values()
        )

        if abs(
            weight_sum - 1.0
        ) > 1e-12:

            raise ValueError(
                "MCS V6 weights must sum to 1.0"
            )

    # ------------------------------------------------------------------------
    # INVALID
    # ------------------------------------------------------------------------

    @staticmethod
    def _invalid(
        *errors: str,
    ) -> MCSResult:

        return MCSResult(
            status=MCSStatus.INVALID,

            mcs=None,

            context=None,

            components=(),

            supplied_components=0,

            required_components=8,

            weighted_sum=None,

            weight_sum=0.0,

            calculation=(
                "RiskContext = 100 - RDS; "
                "MCS = weighted V6 MCI aggregation"
            ),

            errors=tuple(
                errors
            ),

            warnings=(),

            metadata={},

            mcs_state=None,
        )


# ============================================================================
# FUNCTIONAL API
# ============================================================================

def calculate_mcs(
    inputs: MCSInput,
) -> MCSResult:

    return MCSEngine().calculate(
        inputs
    )


# ============================================================================
# SELF TESTS
# ============================================================================

def _run_self_tests() -> None:

    # ------------------------------------------------------------------------
    # TEST 1 â€” Weights
    # ------------------------------------------------------------------------

    assert abs(
        sum(
            WEIGHTS.values()
        ) - 1.0
    ) < 1e-12

    # ------------------------------------------------------------------------
    # TEST 2 â€” Missing input
    # ------------------------------------------------------------------------

    result = calculate_mcs(
        MCSInput()
    )

    assert (
        result.status
        == MCSStatus.INSUFFICIENT
    )

    assert result.mcs is None

    # ------------------------------------------------------------------------
    # TEST 3 â€” All 100, zero RDS
    #
    # RiskContext = 100 - 0 = 100
    # All eight dimensions = 100
    # MCS = 100
    # ------------------------------------------------------------------------

    result = calculate_mcs(
        MCSInput(
            trend=100,
            volume=100,
            liquidity=100,
            risk_density=0,
            timing=100,
            derivatives=100,
            participation=100,
            relationships=100,
        )
    )

    assert (
        result.status
        == MCSStatus.VALID
    )

    assert abs(
        result.mcs - 100.0
    ) < 1e-12

    assert (
        result.context
        == MCSContext.STRONG_CONTEXT
    )

    # ------------------------------------------------------------------------
    # TEST 4 â€” All 0, maximum RDS
    #
    # RiskContext = 100 - 100 = 0
    # MCS = 0
    # ------------------------------------------------------------------------

    result = calculate_mcs(
        MCSInput(
            trend=0,
            volume=0,
            liquidity=0,
            risk_density=100,
            timing=0,
            derivatives=0,
            participation=0,
            relationships=0,
        )
    )

    assert result.mcs == 0.0

    assert (
        result.context
        == MCSContext.DANGER_ZONE
    )

    # ------------------------------------------------------------------------
    # TEST 5 â€” Exact balanced case
    #
    # Seven identity components = 50
    # RDS = 50
    # RiskContext = 50
    # Therefore MCS = 50
    # ------------------------------------------------------------------------

    result = calculate_mcs(
        MCSInput(
            trend=50,
            volume=50,
            liquidity=50,
            risk_density=50,
            timing=50,
            derivatives=50,
            participation=50,
            relationships=50,
        )
    )

    assert abs(
        result.mcs - 50.0
    ) < 1e-12

    assert (
        result.context
        == MCSContext.NEUTRAL
    )

    # ------------------------------------------------------------------------
    # TEST 6 â€” Risk transformation
    # ------------------------------------------------------------------------

    result = calculate_mcs(
        MCSInput(
            trend=100,
            volume=100,
            liquidity=100,
            risk_density=100,
            timing=100,
            derivatives=100,
            participation=100,
            relationships=100,
        )
    )

    # Only risk contribution falls from 100 to 0.
    expected = (
        100.0
        - (
            100.0
            * RISK_WEIGHT
        )
    )

    assert abs(
        result.mcs - expected
    ) < 1e-12

    risk_component = next(
        component
        for component
        in result.components
        if component.name == "risk"
    )

    assert (
        risk_component.context_value
        == 0.0
    )

    assert (
        risk_component.transformation
        == "100-RDS"
    )

    # ------------------------------------------------------------------------
    # TEST 7 â€” Invalid score
    # ------------------------------------------------------------------------

    result = calculate_mcs(
        MCSInput(
            trend=101,
            volume=50,
            liquidity=50,
            risk_density=50,
            timing=50,
            derivatives=50,
            participation=50,
            relationships=50,
        )
    )

    assert (
        result.status
        == MCSStatus.INVALID
    )

    # ------------------------------------------------------------------------
    # TEST 8 â€” Boolean rejected
    # ------------------------------------------------------------------------

    result = calculate_mcs(
        MCSInput(
            trend=True,
        )
    )

    assert (
        result.status
        == MCSStatus.INVALID
    )

    # ------------------------------------------------------------------------
    # TEST 9 â€” D13 authority
    # ------------------------------------------------------------------------

    result = calculate_mcs(
        MCSInput(
            trend=80,
            volume=80,
            liquidity=80,
            risk_density=20,
            timing=80,
            derivatives=80,
            participation=80,
            relationships=80,
        )
    )

    assert result.mcs_state is not None

    assert (
        result.mcs_state.decision_authority
        == "NONE"
    )

    # ------------------------------------------------------------------------
    # TEST 10 â€” Exact weight traceability
    # ------------------------------------------------------------------------

    assert (
        result.mcs_state.provenance[
            "formula"
        ]
        == "D6_MCI_CANONICAL"
    )

    assert (
        result.mcs_state.provenance[
            "weights"
        ]
        == WEIGHTS
    )

    print(
        "MCS V6 D6-MCI canonical self-tests: PASS"
    )


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "ENGINE_NAME",
    "ENGINE_VERSION",

    "MCSStatus",
    "MCSContext",

    "MCSComponent",
    "MCSInput",
    "MCSState",
    "MCSResult",

    "MCSEngine",

    "calculate_mcs",
]


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    _run_self_tests()
