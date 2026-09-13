"""
ROBOMLM_PLUS
EQE — Entry Quality Engine

V6 implementation.

IMPORTANT
---------
The legacy V5 EQE implementation contained hard-coded scoring thresholds,
weights and an automatic Entry_Allowed gate.

Those values are NOT treated as a verified V6 mathematical formula.

Therefore V6 EQE separates:

1. Component measurements
2. Explicit calibrated aggregation
3. Entry-quality state
4. Decision authority

No missing component is silently replaced.
No BUY/SELL decision is generated.
No execution authorization is generated.

The engine is designed to receive upstream V6 evidence/measurements.

V6 engineering chain:

D6 Formula / Primitive
    ->
Formula Registry
    ->
Required Inputs
    ->
Feed / API Mapping
    ->
EQE Calculation
    ->
Normalized EQE State
    ->
D13 Consumption
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import isfinite
from typing import Any, Mapping, Optional


# ============================================================================
# CONSTANTS
# ============================================================================

ENGINE_NAME = "EQE"
ENGINE_VERSION = "V6"

MIN_SCORE = 0.0
MAX_SCORE = 100.0


# ============================================================================
# STATUS
# ============================================================================

class EQEStatus(str, Enum):
    VALID = "VALID"
    PARTIAL = "PARTIAL"
    INSUFFICIENT = "INSUFFICIENT"
    INVALID = "INVALID"


# ============================================================================
# QUALITY STATE
# ============================================================================

class EQEQuality(str, Enum):
    UNKNOWN = "UNKNOWN"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"


# ============================================================================
# MAPPING STATE
# ============================================================================

class EQEMappingState(str, Enum):
    NOT_CALCULATED = "NOT_CALCULATED"
    INCOMPLETE = "INCOMPLETE"
    EXPLICIT_CALIBRATED = "EXPLICIT_CALIBRATED"


# ============================================================================
# COMPONENT NAMES
# ============================================================================

class EQEComponent(str, Enum):
    SIGNAL_AGE = "signal_age"
    MTF = "mtf"
    MOMENTUM = "momentum"
    VOLUME_OI = "volume_oi"
    EXHAUSTION = "exhaustion"
    RR = "rr"
    SPREAD = "spread"


TOTAL_COMPONENTS = 7


# ============================================================================
# INPUT
# ============================================================================

@dataclass(frozen=True)
class EQEInput:
    """
    Canonical EQE input.

    All component scores must already be normalized to 0..100.

    IMPORTANT:
        The component scores are measurements supplied by upstream
        evidence/measurement engines.

    Raw market variables such as:
        price
        previous price
        volume
        change %
        spread
        etc.

    are NOT automatically converted here using the legacy V5 thresholds.

    This prevents legacy heuristics from being silently promoted to
    V6 mathematical truth.
    """

    signal_age_score: Optional[float] = None
    mtf_score: Optional[float] = None
    momentum_score: Optional[float] = None
    volume_oi_score: Optional[float] = None
    exhaustion_score: Optional[float] = None
    rr_score: Optional[float] = None
    spread_score: Optional[float] = None

    # Explicit calibrated aggregation.
    signal_age_weight: Optional[float] = None
    mtf_weight: Optional[float] = None
    momentum_weight: Optional[float] = None
    volume_oi_weight: Optional[float] = None
    exhaustion_weight: Optional[float] = None
    rr_weight: Optional[float] = None
    spread_weight: Optional[float] = None

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )


# ============================================================================
# D13 FACING STATE
# ============================================================================

@dataclass(frozen=True)
class EQEState:
    """
    Normalized EQE intelligence state.

    EQE does NOT contain:
        - BUY
        - SELL
        - order instruction
        - execution authorization
        - fabricated confidence
    """

    eqe: Optional[float]

    quality: EQEQuality

    signal_age_score: Optional[float]
    mtf_score: Optional[float]
    momentum_score: Optional[float]
    volume_oi_score: Optional[float]
    exhaustion_score: Optional[float]
    rr_score: Optional[float]
    spread_score: Optional[float]

    mapping_state: EQEMappingState

    decision_authority: str = "NONE"

    source_engine: str = ENGINE_NAME
    source_version: str = ENGINE_VERSION

    provenance: Mapping[str, Any] = field(
        default_factory=dict
    )

    def as_dict(self) -> dict[str, Any]:
        return {
            "eqe": self.eqe,
            "quality": self.quality.value,

            "signal_age_score": self.signal_age_score,
            "mtf_score": self.mtf_score,
            "momentum_score": self.momentum_score,
            "volume_oi_score": self.volume_oi_score,
            "exhaustion_score": self.exhaustion_score,
            "rr_score": self.rr_score,
            "spread_score": self.spread_score,

            "mapping_state":
                self.mapping_state.value,

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
class EQEResult:
    status: EQEStatus

    eqe: Optional[float]

    quality: EQEQuality

    components: Mapping[str, Optional[float]]

    weighted_sum: Optional[float]

    component_count: int

    component_total: int

    mapping_state: EQEMappingState

    calculation: str

    errors: tuple[str, ...] = ()

    warnings: tuple[str, ...] = ()

    engine: str = ENGINE_NAME

    version: str = ENGINE_VERSION

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    eqe_state: Optional[EQEState] = None

    @property
    def is_valid(self) -> bool:
        return self.status == EQEStatus.VALID

    @property
    def score(self) -> Optional[float]:
        return self.eqe

    @property
    def entry_authorized(self) -> bool:
        """
        EQE never authorizes entry.

        This property intentionally always returns False.
        D13 / execution layer owns authority.
        """
        return False

    def as_dict(self) -> dict[str, Any]:
        return {
            "status":
                self.status.value,

            "eqe":
                self.eqe,

            "score":
                self.score,

            "quality":
                self.quality.value,

            "components":
                dict(self.components),

            "weighted_sum":
                self.weighted_sum,

            "component_count":
                self.component_count,

            "component_total":
                self.component_total,

            "mapping_state":
                self.mapping_state.value,

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

            "entry_authorized":
                False,

            "eqe_state":
                None
                if self.eqe_state is None
                else self.eqe_state.as_dict(),
        }


# ============================================================================
# ENGINE
# ============================================================================

class EQEEngine:

    COMPONENTS = (
        EQEComponent.SIGNAL_AGE,
        EQEComponent.MTF,
        EQEComponent.MOMENTUM,
        EQEComponent.VOLUME_OI,
        EQEComponent.EXHAUSTION,
        EQEComponent.RR,
        EQEComponent.SPREAD,
    )

    CALCULATION = (
        "EQE = "
        "Σ(component_score_i * calibrated_weight_i)"
    )

    def calculate(
        self,
        inputs: EQEInput,
    ) -> EQEResult:

        if not isinstance(
            inputs,
            EQEInput,
        ):
            return self._invalid(
                "inputs must be EQEInput"
            )

        component_values = {
            EQEComponent.SIGNAL_AGE:
                inputs.signal_age_score,

            EQEComponent.MTF:
                inputs.mtf_score,

            EQEComponent.MOMENTUM:
                inputs.momentum_score,

            EQEComponent.VOLUME_OI:
                inputs.volume_oi_score,

            EQEComponent.EXHAUSTION:
                inputs.exhaustion_score,

            EQEComponent.RR:
                inputs.rr_score,

            EQEComponent.SPREAD:
                inputs.spread_score,
        }

        weights = {
            EQEComponent.SIGNAL_AGE:
                inputs.signal_age_weight,

            EQEComponent.MTF:
                inputs.mtf_weight,

            EQEComponent.MOMENTUM:
                inputs.momentum_weight,

            EQEComponent.VOLUME_OI:
                inputs.volume_oi_weight,

            EQEComponent.EXHAUSTION:
                inputs.exhaustion_weight,

            EQEComponent.RR:
                inputs.rr_weight,

            EQEComponent.SPREAD:
                inputs.spread_weight,
        }

        errors: list[str] = []

        # ------------------------------------------------------------------
        # VALIDATE COMPONENTS
        # ------------------------------------------------------------------

        for component, value in component_values.items():

            if value is None:
                continue

            error = self._validate_score(
                value,
                component.value,
            )

            if error:
                errors.append(error)

        if errors:
            return self._invalid(
                *errors
            )

        component_count = sum(
            value is not None
            for value in component_values.values()
        )

        # ------------------------------------------------------------------
        # NO COMPONENTS
        # ------------------------------------------------------------------

        if component_count == 0:

            state = self._build_state(
                inputs,
                None,
                EQEQuality.UNKNOWN,
                EQEMappingState.NOT_CALCULATED,
            )

            return EQEResult(
                status=EQEStatus.INSUFFICIENT,

                eqe=None,

                quality=EQEQuality.UNKNOWN,

                components={
                    component.value: value
                    for component, value
                    in component_values.items()
                },

                weighted_sum=None,

                component_count=0,

                component_total=TOTAL_COMPONENTS,

                mapping_state=(
                    EQEMappingState.NOT_CALCULATED
                ),

                calculation=self.CALCULATION,

                warnings=(
                    "No EQE component measurements supplied.",
                ),

                metadata=dict(
                    inputs.metadata
                ),

                eqe_state=state,
            )

        # ------------------------------------------------------------------
        # WEIGHTS
        # ------------------------------------------------------------------

        supplied_weights = [
            value
            for value in weights.values()
            if value is not None
        ]

        if not supplied_weights:

            state = self._build_state(
                inputs,
                None,
                EQEQuality.UNKNOWN,
                EQEMappingState.NOT_CALCULATED,
            )

            return EQEResult(
                status=EQEStatus.PARTIAL,

                eqe=None,

                quality=EQEQuality.UNKNOWN,

                components={
                    component.value: value
                    for component, value
                    in component_values.items()
                },

                weighted_sum=None,

                component_count=component_count,

                component_total=TOTAL_COMPONENTS,

                mapping_state=(
                    EQEMappingState.NOT_CALCULATED
                ),

                calculation=self.CALCULATION,

                warnings=(
                    "EQE aggregation not calculated: "
                    "no explicit calibrated weights supplied.",
                ),

                metadata={
                    **dict(inputs.metadata),
                    "aggregation":
                        "NOT_CALCULATED",
                    "legacy_v5_weights":
                        "NOT_USED_AS_V6_TRUTH",
                },

                eqe_state=state,
            )

        # ------------------------------------------------------------------
        # COMPLETE WEIGHTS
        # ------------------------------------------------------------------

        missing_weights = [
            component.value
            for component, weight
            in weights.items()
            if weight is None
        ]

        if missing_weights:

            state = self._build_state(
                inputs,
                None,
                EQEQuality.UNKNOWN,
                EQEMappingState.INCOMPLETE,
            )

            return EQEResult(
                status=EQEStatus.PARTIAL,

                eqe=None,

                quality=EQEQuality.UNKNOWN,

                components={
                    component.value: value
                    for component, value
                    in component_values.items()
                },

                weighted_sum=None,

                component_count=component_count,

                component_total=TOTAL_COMPONENTS,

                mapping_state=(
                    EQEMappingState.INCOMPLETE
                ),

                calculation=self.CALCULATION,

                warnings=(
                    "Incomplete EQE calibrated mapping; "
                    "missing weights: "
                    + ", ".join(missing_weights),
                ),

                metadata=dict(
                    inputs.metadata
                ),

                eqe_state=state,
            )

        # ------------------------------------------------------------------
        # VALIDATE WEIGHTS
        # ------------------------------------------------------------------

        for component, weight in weights.items():

            error = self._validate_weight(
                weight,
                f"{component.value}_weight",
            )

            if error:
                errors.append(error)

        if errors:
            return self._invalid(
                *errors
            )

        weight_sum = sum(
            float(weight)
            for weight in weights.values()
        )

        if abs(
            weight_sum - 1.0
        ) > 1e-12:

            return self._invalid(
                "EQE calibrated weights must sum to 1.0."
            )

        # ------------------------------------------------------------------
        # ALL COMPONENTS REQUIRED FOR CALIBRATED EQE
        # ------------------------------------------------------------------

        missing_components = [
            component.value
            for component, value
            in component_values.items()
            if value is None
        ]

        if missing_components:

            state = self._build_state(
                inputs,
                None,
                EQEQuality.UNKNOWN,
                EQEMappingState.INCOMPLETE,
            )

            return EQEResult(
                status=EQEStatus.PARTIAL,

                eqe=None,

                quality=EQEQuality.UNKNOWN,

                components={
                    component.value: value
                    for component, value
                    in component_values.items()
                },

                weighted_sum=None,

                component_count=component_count,

                component_total=TOTAL_COMPONENTS,

                mapping_state=(
                    EQEMappingState.INCOMPLETE
                ),

                calculation=self.CALCULATION,

                warnings=(
                    "Calibrated EQE requires all seven "
                    "component measurements. Missing: "
                    + ", ".join(
                        missing_components
                    ),
                ),

                metadata=dict(
                    inputs.metadata
                ),

                eqe_state=state,
            )

        # ------------------------------------------------------------------
        # AGGREGATION
        # ------------------------------------------------------------------

        weighted_sum = sum(
            float(component_values[component])
            * float(weights[component])
            for component in self.COMPONENTS
        )

        if not (
            MIN_SCORE
            <= weighted_sum
            <= MAX_SCORE
        ):

            return self._invalid(
                "EQE weighted result left 0..100 domain."
            )

        eqe = float(
            weighted_sum
        )

        quality = self._quality_from_score(
            eqe
        )

        state = self._build_state(
            inputs,
            eqe,
            quality,
            EQEMappingState.EXPLICIT_CALIBRATED,
        )

        return EQEResult(
            status=EQEStatus.VALID,

            eqe=eqe,

            quality=quality,

            components={
                component.value:
                    float(component_values[component])
                for component in self.COMPONENTS
            },

            weighted_sum=weighted_sum,

            component_count=component_count,

            component_total=TOTAL_COMPONENTS,

            mapping_state=(
                EQEMappingState.EXPLICIT_CALIBRATED
            ),

            calculation=self.CALCULATION,

            metadata={
                **dict(inputs.metadata),

                "aggregation":
                    "EXPLICIT_CALIBRATED",

                "weight_sum":
                    weight_sum,

                "decision_authority":
                    "NONE",

                "legacy_v5_thresholds":
                    "NOT_USED_AS_V6_TRUTH",
            },

            eqe_state=state,
        )

    # =========================================================================
    # QUALITY
    # =========================================================================

    @staticmethod
    def _quality_from_score(
        score: float,
    ) -> EQEQuality:

        # These are descriptive labels only.
        # They are NOT an execution gate.

        if score >= 80.0:
            return EQEQuality.HIGH

        if score >= 60.0:
            return EQEQuality.MODERATE

        return EQEQuality.LOW

    # =========================================================================
    # STATE
    # =========================================================================

    @staticmethod
    def _build_state(
        inputs: EQEInput,
        eqe: Optional[float],
        quality: EQEQuality,
        mapping_state: EQEMappingState,
    ) -> EQEState:

        return EQEState(
            eqe=eqe,

            quality=quality,

            signal_age_score=
                inputs.signal_age_score,

            mtf_score=
                inputs.mtf_score,

            momentum_score=
                inputs.momentum_score,

            volume_oi_score=
                inputs.volume_oi_score,

            exhaustion_score=
                inputs.exhaustion_score,

            rr_score=
                inputs.rr_score,

            spread_score=
                inputs.spread_score,

            mapping_state=mapping_state,

            decision_authority="NONE",

            provenance={
                "engine":
                    ENGINE_NAME,

                "version":
                    ENGINE_VERSION,

                "aggregation":
                    mapping_state.value,

                "legacy_v5_formula":
                    "NOT_PROMOTED_TO_V6",

                "decision_authority":
                    "NONE",
            },
        )

    # =========================================================================
    # VALIDATION
    # =========================================================================

    @staticmethod
    def _validate_score(
        value: Any,
        name: str,
    ) -> Optional[str]:

        if isinstance(value, bool):
            return (
                f"{name} cannot be boolean"
            )

        if not isinstance(
            value,
            (int, float),
        ):
            return (
                f"{name} must be numeric"
            )

        value = float(value)

        if not isfinite(value):
            return (
                f"{name} must be finite"
            )

        if not (
            MIN_SCORE
            <= value
            <= MAX_SCORE
        ):
            return (
                f"{name} must be in [0,100]"
            )

        return None

    @staticmethod
    def _validate_weight(
        value: Any,
        name: str,
    ) -> Optional[str]:

        if isinstance(value, bool):
            return (
                f"{name} cannot be boolean"
            )

        if not isinstance(
            value,
            (int, float),
        ):
            return (
                f"{name} must be numeric"
            )

        value = float(value)

        if not isfinite(value):
            return (
                f"{name} must be finite"
            )

        if value < 0.0:
            return (
                f"{name} must be >= 0"
            )

        return None

    # =========================================================================
    # INVALID
    # =========================================================================

    @staticmethod
    def _invalid(
        *errors: str,
    ) -> EQEResult:

        return EQEResult(
            status=EQEStatus.INVALID,

            eqe=None,

            quality=EQEQuality.UNKNOWN,

            components={},

            weighted_sum=None,

            component_count=0,

            component_total=TOTAL_COMPONENTS,

            mapping_state=(
                EQEMappingState.NOT_CALCULATED
            ),

            calculation=(
                "EQE = "
                "Σ(component_score_i * calibrated_weight_i)"
            ),

            errors=tuple(errors),

            warnings=(),

            metadata={},

            eqe_state=None,
        )


# ============================================================================
# FUNCTIONAL API
# ============================================================================

def calculate_eqe(
    inputs: EQEInput,
) -> EQEResult:

    return EQEEngine().calculate(
        inputs
    )


# ============================================================================
# SELF TESTS
# ============================================================================

def _run_self_tests() -> None:

    # ------------------------------------------------------------------------
    # Equal weights
    # ------------------------------------------------------------------------

    weight = 1.0 / 7.0

    # ------------------------------------------------------------------------
    # TEST 1 — No input
    # ------------------------------------------------------------------------

    result = calculate_eqe(
        EQEInput()
    )

    assert (
        result.status
        == EQEStatus.INSUFFICIENT
    )

    assert result.eqe is None

    # ------------------------------------------------------------------------
    # TEST 2 — Components without mapping
    # ------------------------------------------------------------------------

    result = calculate_eqe(
        EQEInput(
            signal_age_score=100,
            mtf_score=100,
            momentum_score=100,
            volume_oi_score=100,
            exhaustion_score=100,
            rr_score=100,
            spread_score=100,
        )
    )

    assert (
        result.status
        == EQEStatus.PARTIAL
    )

    assert result.eqe is None

    # ------------------------------------------------------------------------
    # TEST 3 — Equal calibrated mapping
    # ------------------------------------------------------------------------

    result = calculate_eqe(
        EQEInput(
            signal_age_score=100,
            mtf_score=100,
            momentum_score=100,
            volume_oi_score=100,
            exhaustion_score=100,
            rr_score=100,
            spread_score=100,

            signal_age_weight=weight,
            mtf_weight=weight,
            momentum_weight=weight,
            volume_oi_weight=weight,
            exhaustion_weight=weight,
            rr_weight=weight,
            spread_weight=weight,
        )
    )

    assert (
        result.status
        == EQEStatus.VALID
    )

    assert abs(
        result.eqe - 100.0
    ) < 1e-12

    assert (
        result.quality
        == EQEQuality.HIGH
    )

    # ------------------------------------------------------------------------
    # TEST 4 — All zero
    # ------------------------------------------------------------------------

    result = calculate_eqe(
        EQEInput(
            signal_age_score=0,
            mtf_score=0,
            momentum_score=0,
            volume_oi_score=0,
            exhaustion_score=0,
            rr_score=0,
            spread_score=0,

            signal_age_weight=weight,
            mtf_weight=weight,
            momentum_weight=weight,
            volume_oi_weight=weight,
            exhaustion_weight=weight,
            rr_weight=weight,
            spread_weight=weight,
        )
    )

    assert result.eqe == 0.0
    assert result.quality == EQEQuality.LOW

    # ------------------------------------------------------------------------
    # TEST 5 — Mid score
    # ------------------------------------------------------------------------

    result = calculate_eqe(
        EQEInput(
            signal_age_score=50,
            mtf_score=50,
            momentum_score=50,
            volume_oi_score=50,
            exhaustion_score=50,
            rr_score=50,
            spread_score=50,

            signal_age_weight=weight,
            mtf_weight=weight,
            momentum_weight=weight,
            volume_oi_weight=weight,
            exhaustion_weight=weight,
            rr_weight=weight,
            spread_weight=weight,
        )
    )

    assert abs(
        result.eqe - 50.0
    ) < 1e-12

    assert (
        result.quality
        == EQEQuality.LOW
    )

    # ------------------------------------------------------------------------
    # TEST 6 — Missing component
    # ------------------------------------------------------------------------

    result = calculate_eqe(
        EQEInput(
            signal_age_score=100,
            mtf_score=100,
            momentum_score=100,
            volume_oi_score=100,
            exhaustion_score=100,
            rr_score=100,

            spread_score=None,

            signal_age_weight=weight,
            mtf_weight=weight,
            momentum_weight=weight,
            volume_oi_weight=weight,
            exhaustion_weight=weight,
            rr_weight=weight,
            spread_weight=weight,
        )
    )

    assert (
        result.status
        == EQEStatus.PARTIAL
    )

    assert result.eqe is None

    # ------------------------------------------------------------------------
    # TEST 7 — Bad weight sum
    # ------------------------------------------------------------------------

    result = calculate_eqe(
        EQEInput(
            signal_age_score=50,
            mtf_score=50,
            momentum_score=50,
            volume_oi_score=50,
            exhaustion_score=50,
            rr_score=50,
            spread_score=50,

            signal_age_weight=0.20,
            mtf_weight=0.20,
            momentum_weight=0.20,
            volume_oi_weight=0.10,
            exhaustion_weight=0.10,
            rr_weight=0.05,
            spread_weight=0.05,
        )
    )

    assert (
        result.status
        == EQEStatus.INVALID
    )

    # ------------------------------------------------------------------------
    # TEST 8 — Invalid score
    # ------------------------------------------------------------------------

    result = calculate_eqe(
        EQEInput(
            signal_age_score=101,
        )
    )

    assert (
        result.status
        == EQEStatus.INVALID
    )

    # ------------------------------------------------------------------------
    # TEST 9 — Boolean rejected
    # ------------------------------------------------------------------------

    result = calculate_eqe(
        EQEInput(
            mtf_score=True,
        )
    )

    assert (
        result.status
        == EQEStatus.INVALID
    )

    # ------------------------------------------------------------------------
    # TEST 10 — D13 authority remains NONE
    # ------------------------------------------------------------------------

    result = calculate_eqe(
        EQEInput(
            signal_age_score=100,
            mtf_score=100,
            momentum_score=100,
            volume_oi_score=100,
            exhaustion_score=100,
            rr_score=100,
            spread_score=100,

            signal_age_weight=weight,
            mtf_weight=weight,
            momentum_weight=weight,
            volume_oi_weight=weight,
            exhaustion_weight=weight,
            rr_weight=weight,
            spread_weight=weight,
        )
    )

    assert result.eqe_state is not None

    assert (
        result.eqe_state.decision_authority
        == "NONE"
    )

    assert (
        result.entry_authorized
        is False
    )

    # ------------------------------------------------------------------------
    # TEST 11 — Score property
    # ------------------------------------------------------------------------

    assert (
        result.score
        == result.eqe
    )

    print(
        "EQE V6 calibrated intelligence self-tests: PASS"
    )


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "ENGINE_NAME",
    "ENGINE_VERSION",

    "EQEStatus",
    "EQEQuality",
    "EQEMappingState",
    "EQEComponent",

    "EQEInput",
    "EQEState",
    "EQEResult",

    "EQEEngine",

    "calculate_eqe",
]


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    _run_self_tests()