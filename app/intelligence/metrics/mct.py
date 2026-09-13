"""
ROBOMLM_PLUS
Market Context Metric (MCT)

V6-derived Market Context Intelligence calculation.

SOURCE OF TRUTH
---------------
V6 Market Context Intelligence (MCI) framework:

    Trend           = 20%
    Volume          = 15%
    Liquidity       = 15%
    Risk            = 15%
    Timing          = 10%
    Derivatives     = 10%
    Participation   = 10%
    Relationships   = 5%

    Total           = 100%

All component inputs are expected on the canonical 0..100 scale.

IMPORTANT
---------
This module does NOT invent missing values.
A missing component is not replaced by 50, 0, or any other
default value.

For the risk component, RDS is used directly as the source
metric, but because lower RDS means lower risk, its positive
context contribution is:

    RiskContribution = 100 - RDS

The final MCT/MCI score is the weighted arithmetic aggregation
of the eight V6 context dimensions.

This module:
    - validates inputs
    - preserves component provenance
    - calculates weighted contributions
    - exposes the exact calculation
    - provides deterministic interpretation
    - does not generate BUY/SELL
    - does not generate confidence
    - does not generate execution authority
    - does not fabricate unavailable evidence
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import isfinite
from typing import Any, Mapping, Optional


# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------

ENGINE_NAME = "MCT"
ENGINE_VERSION = "V6"

MIN_SCORE = 0.0
MAX_SCORE = 100.0

# V6 MCI weights.
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
    "risk_density": RISK_WEIGHT,
    "timing": TIMING_WEIGHT,
    "derivatives": DERIVATIVES_WEIGHT,
    "participation": PARTICIPATION_WEIGHT,
    "relationships": RELATIONSHIPS_WEIGHT,
}


# ---------------------------------------------------------------------------
# ENUMS
# ---------------------------------------------------------------------------

class MCTStatus(str, Enum):
    VALID = "VALID"
    INSUFFICIENT = "INSUFFICIENT"
    INVALID = "INVALID"


class MCTContext(str, Enum):
    STRONG_CONTEXT = "STRONG_CONTEXT"
    CONSTRUCTIVE = "CONSTRUCTIVE"
    NEUTRAL = "NEUTRAL"
    WEAK = "WEAK"
    DANGER_ZONE = "DANGER_ZONE"


# ---------------------------------------------------------------------------
# COMPONENT
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MCTComponent:
    """
    One V6 context component.

    raw_value:
        Original metric value supplied by upstream engine.

    context_value:
        Value actually used in MCT aggregation.

        For all components except risk:
            context_value = raw_value

        For risk:
            context_value = 100 - RDS
    """

    name: str
    raw_value: float
    context_value: float
    weight: float
    contribution: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "raw_value": self.raw_value,
            "context_value": self.context_value,
            "weight": self.weight,
            "contribution": self.contribution,
        }


# ---------------------------------------------------------------------------
# INPUT
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MCTInputs:
    """
    V6 MCT inputs.

    Every value must be an explicit 0..100 metric.

    risk_density is RDS:
        0   = lower risk
        100 = higher risk

    MCT converts RDS into positive context contribution:

        risk_context = 100 - RDS
    """

    trend: Optional[float] = None
    volume: Optional[float] = None
    liquidity: Optional[float] = None
    risk_density: Optional[float] = None
    timing: Optional[float] = None
    derivatives: Optional[float] = None
    participation: Optional[float] = None
    relationships: Optional[float] = None

    metadata: Mapping[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# RESULT
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MCTResult:
    """
    Complete deterministic MCT calculation result.
    """

    status: MCTStatus
    mct: Optional[float]

    context: Optional[MCTContext]

    components: tuple[MCTComponent, ...]

    supplied_components: int
    required_components: int

    weighted_sum: Optional[float]
    weight_sum: float

    calculation: str

    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    engine: str = ENGINE_NAME
    version: str = ENGINE_VERSION

    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        return self.status == MCTStatus.VALID

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "mct": self.mct,
            "context": self.context.value if self.context else None,
            "components": [
                component.as_dict()
                for component in self.components
            ],
            "supplied_components": self.supplied_components,
            "required_components": self.required_components,
            "weighted_sum": self.weighted_sum,
            "weight_sum": self.weight_sum,
            "calculation": self.calculation,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "engine": self.engine,
            "version": self.version,
            "metadata": dict(self.metadata),
        }


# ---------------------------------------------------------------------------
# ENGINE
# ---------------------------------------------------------------------------

class MCTEngine:
    """
    V6 Market Context calculation engine.

    Formula
    -------

    R_context = 100 - RDS

    MCT =
        Trend * 0.20
        + Volume * 0.15
        + Liquidity * 0.15
        + RiskContext * 0.15
        + Timing * 0.10
        + Derivatives * 0.10
        + Participation * 0.10
        + Relationships * 0.05

    Since all weights sum to 1.00, the result remains on 0..100.
    """

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

    def __init__(self) -> None:
        self.weights = dict(WEIGHTS)

        self._validate_weights()

    # ------------------------------------------------------------------
    # PUBLIC
    # ------------------------------------------------------------------

    def calculate(self, inputs: MCTInputs) -> MCTResult:
        """
        Calculate MCT from V6 context inputs.

        Missing input:
            -> INSUFFICIENT

        Invalid numeric input:
            -> INVALID

        No missing/invalid input:
            -> VALID
        """

        errors: list[str] = []
        warnings: list[str] = []

        values = {
            name: getattr(inputs, name)
            for name in self.REQUIRED_COMPONENTS
        }

        # --------------------------------------------------------------
        # Validate supplied values
        # --------------------------------------------------------------

        for name, value in values.items():
            if value is None:
                continue

            if isinstance(value, bool):
                errors.append(
                    f"{name}: boolean is not a valid numeric metric"
                )
                continue

            if not isinstance(value, (int, float)):
                errors.append(
                    f"{name}: expected numeric value, got "
                    f"{type(value).__name__}"
                )
                continue

            numeric_value = float(value)

            if not isfinite(numeric_value):
                errors.append(
                    f"{name}: value must be finite"
                )
                continue

            if numeric_value < MIN_SCORE or numeric_value > MAX_SCORE:
                errors.append(
                    f"{name}: value {numeric_value} outside "
                    f"canonical range 0..100"
                )

        # --------------------------------------------------------------
        # Invalid input stops calculation.
        # --------------------------------------------------------------

        if errors:
            return MCTResult(
                status=MCTStatus.INVALID,
                mct=None,
                context=None,
                components=(),
                supplied_components=self._count_supplied(values),
                required_components=len(self.REQUIRED_COMPONENTS),
                weighted_sum=None,
                weight_sum=0.0,
                calculation=self._calculation_formula(),
                errors=tuple(errors),
                warnings=tuple(warnings),
                metadata=dict(inputs.metadata),
            )

        # --------------------------------------------------------------
        # Missing input is NOT guessed.
        # --------------------------------------------------------------

        missing = [
            name
            for name, value in values.items()
            if value is None
        ]

        if missing:
            warnings.append(
                "Calculation stopped because required V6 context "
                "components are missing: "
                + ", ".join(missing)
            )

            return MCTResult(
                status=MCTStatus.INSUFFICIENT,
                mct=None,
                context=None,
                components=(),
                supplied_components=self._count_supplied(values),
                required_components=len(self.REQUIRED_COMPONENTS),
                weighted_sum=None,
                weight_sum=0.0,
                calculation=self._calculation_formula(),
                errors=(),
                warnings=tuple(warnings),
                metadata={
                    **dict(inputs.metadata),
                    "missing_components": tuple(missing),
                },
            )

        # --------------------------------------------------------------
        # Calculate components
        # --------------------------------------------------------------

        components: list[MCTComponent] = []

        for name in self.REQUIRED_COMPONENTS:
            raw_value = float(values[name])
            weight = self.weights[name]

            if name == "risk_density":
                context_value = MAX_SCORE - raw_value
            else:
                context_value = raw_value

            contribution = context_value * weight

            components.append(
                MCTComponent(
                    name=name,
                    raw_value=raw_value,
                    context_value=context_value,
                    weight=weight,
                    contribution=contribution,
                )
            )

        # --------------------------------------------------------------
        # Aggregate
        # --------------------------------------------------------------

        weight_sum = sum(
            component.weight
            for component in components
        )

        weighted_sum = sum(
            component.contribution
            for component in components
        )

        # Full V6 framework must equal exactly 1.
        if weight_sum != 1.0:
            return MCTResult(
                status=MCTStatus.INVALID,
                mct=None,
                context=None,
                components=tuple(components),
                supplied_components=len(self.REQUIRED_COMPONENTS),
                required_components=len(self.REQUIRED_COMPONENTS),
                weighted_sum=weighted_sum,
                weight_sum=weight_sum,
                calculation=self._calculation_formula(),
                errors=(
                    "Internal V6 weight invariant failed: "
                    f"weight_sum={weight_sum!r}, expected 1.0"
                ),
                warnings=tuple(warnings),
                metadata=dict(inputs.metadata),
            )

        # Floating point safety only.
        # This is NOT an intelligence adjustment.
        mct = self._bound_score(weighted_sum)

        context = self._interpret(mct)

        return MCTResult(
            status=MCTStatus.VALID,
            mct=mct,
            context=context,
            components=tuple(components),
            supplied_components=len(self.REQUIRED_COMPONENTS),
            required_components=len(self.REQUIRED_COMPONENTS),
            weighted_sum=weighted_sum,
            weight_sum=weight_sum,
            calculation=self._calculation_formula(),
            errors=(),
            warnings=tuple(warnings),
            metadata={
                **dict(inputs.metadata),
                "risk_transformation": "100 - RDS",
                "weight_total": 1.0,
            },
        )

    # ------------------------------------------------------------------
    # CONVENIENCE
    # ------------------------------------------------------------------

    def calculate_from_mapping(
        self,
        data: Mapping[str, Any],
    ) -> MCTResult:
        """
        Calculate from a mapping.

        Accepted aliases:
            risk_density / rds / risk
            derivatives / derivative
            relationships / relationship
        """

        normalized = dict(data)

        inputs = MCTInputs(
            trend=self._first_present(
                normalized,
                "trend",
            ),
            volume=self._first_present(
                normalized,
                "volume",
            ),
            liquidity=self._first_present(
                normalized,
                "liquidity",
            ),
            risk_density=self._first_present(
                normalized,
                "risk_density",
                "rds",
                "risk",
            ),
            timing=self._first_present(
                normalized,
                "timing",
            ),
            derivatives=self._first_present(
                normalized,
                "derivatives",
                "derivative",
            ),
            participation=self._first_present(
                normalized,
                "participation",
            ),
            relationships=self._first_present(
                normalized,
                "relationships",
                "relationship",
            ),
            metadata={
                key: value
                for key, value in normalized.items()
                if key not in {
                    "trend",
                    "volume",
                    "liquidity",
                    "risk_density",
                    "rds",
                    "risk",
                    "timing",
                    "derivatives",
                    "derivative",
                    "participation",
                    "relationships",
                    "relationship",
                }
            },
        )

        return self.calculate(inputs)

    # ------------------------------------------------------------------
    # INTERNAL
    # ------------------------------------------------------------------
    def _validate_weights(self) -> None:
        expected = dict(WEIGHTS)

        if self.weights != expected:
            raise RuntimeError(
                "MCT V6 weight configuration was modified. "
                "Expected canonical V6 weights."
            )

        total = sum(self.weights.values())

        if total != 1.0:
            raise RuntimeError(
                f"MCT V6 weights must sum to 1.0, got {total!r}"
            )
    @staticmethod
    def _count_supplied(values: Mapping[str, Any]) -> int:
        return sum(
            value is not None
            for value in values.values()
        )

    @staticmethod
    def _first_present(
        data: Mapping[str, Any],
        *names: str,
    ) -> Any:
        for name in names:
            if name in data:
                return data[name]
        return None

    @staticmethod
    def _bound_score(value: float) -> float:
        """
        Mathematical boundary protection.

        This does not change a legitimate value inside 0..100.
        """

        if value < MIN_SCORE:
            return MIN_SCORE

        if value > MAX_SCORE:
            return MAX_SCORE

        return float(value)

    @staticmethod
    def _interpret(value: float) -> MCTContext:
        """
        V6 blueprint interpretation bands.

            80..100 = Strong Context
            60..79  = Constructive
            40..59  = Neutral
            20..39  = Weak
            0..19   = Danger Zone

        Decimal scores are classified by their numerical position.
        """

        if value >= 80.0:
            return MCTContext.STRONG_CONTEXT

        if value >= 60.0:
            return MCTContext.CONSTRUCTIVE

        if value >= 40.0:
            return MCTContext.NEUTRAL

        if value >= 20.0:
            return MCTContext.WEAK

        return MCTContext.DANGER_ZONE

    @staticmethod
    def _calculation_formula() -> str:
        return (
            "MCT = "
            "(Trend × 0.20) + "
            "(Volume × 0.15) + "
            "(Liquidity × 0.15) + "
            "((100 - RDS) × 0.15) + "
            "(Timing × 0.10) + "
            "(Derivatives × 0.10) + "
            "(Participation × 0.10) + "
            "(Relationships × 0.05)"
        )


# ---------------------------------------------------------------------------
# CONVENIENCE FUNCTION
# ---------------------------------------------------------------------------

def calculate_mct(
    *,
    trend: Optional[float] = None,
    volume: Optional[float] = None,
    liquidity: Optional[float] = None,
    risk_density: Optional[float] = None,
    timing: Optional[float] = None,
    derivatives: Optional[float] = None,
    participation: Optional[float] = None,
    relationships: Optional[float] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> MCTResult:
    """
    Functional API for MCT.
    """

    engine = MCTEngine()

    inputs = MCTInputs(
        trend=trend,
        volume=volume,
        liquidity=liquidity,
        risk_density=risk_density,
        timing=timing,
        derivatives=derivatives,
        participation=participation,
        relationships=relationships,
        metadata=metadata or {},
    )

    return engine.calculate(inputs)


# ---------------------------------------------------------------------------
# SELF TESTS
# ---------------------------------------------------------------------------

def _run_self_tests() -> None:
    engine = MCTEngine()

    # --------------------------------------------------------------
    # TEST 1: All 100
    #
    # RDS = 0 means maximum positive risk contribution:
    # 100 - 0 = 100
    #
    # Therefore MCT = 100.
    # --------------------------------------------------------------

    result = engine.calculate(
        MCTInputs(
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

    assert result.status == MCTStatus.VALID
    assert result.mct == 100.0
    assert result.context == MCTContext.STRONG_CONTEXT

    # --------------------------------------------------------------
    # TEST 2: All zero
    #
    # RDS = 100 => risk context = 0
    #
    # Therefore MCT = 0.
    # --------------------------------------------------------------

    result = engine.calculate(
        MCTInputs(
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

    assert result.status == MCTStatus.VALID
    assert result.mct == 0.0
    assert result.context == MCTContext.DANGER_ZONE

    # --------------------------------------------------------------
    # TEST 3: Exact weighted calculation
    # --------------------------------------------------------------

    result = engine.calculate(
        MCTInputs(
            trend=80,
            volume=70,
            liquidity=90,
            risk_density=20,
            timing=60,
            derivatives=50,
            participation=80,
            relationships=40,
        )
    )

    expected = (
        80 * 0.20
        + 70 * 0.15
        + 90 * 0.15
        + (100 - 20) * 0.15
        + 60 * 0.10
        + 50 * 0.10
        + 80 * 0.10
        + 40 * 0.05
    )

    assert result.status == MCTStatus.VALID
    assert result.mct is not None
    assert abs(result.mct - expected) < 1e-12
    assert abs(result.weight_sum - 1.0) < 1e-12

    # --------------------------------------------------------------
    # TEST 4: Missing component must not be guessed
    # --------------------------------------------------------------

    result = engine.calculate(
        MCTInputs(
            trend=80,
            volume=70,
            liquidity=90,
            risk_density=20,
            timing=None,
            derivatives=50,
            participation=80,
            relationships=40,
        )
    )

    assert result.status == MCTStatus.INSUFFICIENT
    assert result.mct is None

    # --------------------------------------------------------------
    # TEST 5: Invalid range
    # --------------------------------------------------------------

    result = engine.calculate(
        MCTInputs(
            trend=101,
            volume=70,
            liquidity=90,
            risk_density=20,
            timing=60,
            derivatives=50,
            participation=80,
            relationships=40,
        )
    )

    assert result.status == MCTStatus.INVALID
    assert result.mct is None

    # --------------------------------------------------------------
    # TEST 6: NaN rejected
    # --------------------------------------------------------------

    result = engine.calculate(
        MCTInputs(
            trend=float("nan"),
            volume=70,
            liquidity=90,
            risk_density=20,
            timing=60,
            derivatives=50,
            participation=80,
            relationships=40,
        )
    )

    assert result.status == MCTStatus.INVALID
    assert result.mct is None

    # --------------------------------------------------------------
    # TEST 7: RDS inversion
    #
    # Same everything else.
    # Lower RDS must produce higher MCT.
    # --------------------------------------------------------------

    low_risk = engine.calculate(
        MCTInputs(
            trend=70,
            volume=70,
            liquidity=70,
            risk_density=10,
            timing=70,
            derivatives=70,
            participation=70,
            relationships=70,
        )
    )

    high_risk = engine.calculate(
        MCTInputs(
            trend=70,
            volume=70,
            liquidity=70,
            risk_density=90,
            timing=70,
            derivatives=70,
            participation=70,
            relationships=70,
        )
    )

    assert low_risk.is_valid
    assert high_risk.is_valid
    assert low_risk.mct is not None
    assert high_risk.mct is not None
    assert low_risk.mct > high_risk.mct

    # --------------------------------------------------------------
    # TEST 8: Mapping API
    # --------------------------------------------------------------

    result = engine.calculate_from_mapping(
        {
            "trend": 80,
            "volume": 70,
            "liquidity": 90,
            "rds": 20,
            "timing": 60,
            "derivative": 50,
            "participation": 80,
            "relationship": 40,
        }
    )

    assert result.status == MCTStatus.VALID
    assert result.mct is not None

    # --------------------------------------------------------------
    # TEST 9: Boolean rejected
    # --------------------------------------------------------------

    result = engine.calculate(
        MCTInputs(
            trend=True,
            volume=70,
            liquidity=90,
            risk_density=20,
            timing=60,
            derivatives=50,
            participation=80,
            relationships=40,
        )
    )

    assert result.status == MCTStatus.INVALID

    # --------------------------------------------------------------
    # TEST 10: Weight conservation
    # --------------------------------------------------------------

    assert abs(
        sum(WEIGHTS.values()) - 1.0
    ) < 1e-12


# ---------------------------------------------------------------------------
# MODULE EXPORTS
# ---------------------------------------------------------------------------

__all__ = [
    "ENGINE_NAME",
    "ENGINE_VERSION",
    "MCTStatus",
    "MCTContext",
    "MCTComponent",
    "MCTInputs",
    "MCTResult",
    "MCTEngine",
    "calculate_mct",
]


if __name__ == "__main__":
    _run_self_tests()
    print("MCT V6 self-tests: PASS")