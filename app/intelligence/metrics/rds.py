"""
ROBOMLM_PLUS
RDS â€” Risk Density Score / Risk Density Intelligence

V6 implementation.

SOURCE OF TRUTH
---------------

RDS:
    Risk Density Score

Domain:
    0 <= RDS <= 100

Interpretation:
    lower RDS = lower risk environment

RDS is an independent risk intelligence layer.

Verified V6 risk dimensions:
    - market risk
    - liquidity risk
    - volatility risk
    - event risk
    - correlation risk
    - execution risk

Verified mathematical primitive:
    EQ-0008 â€” Uncertainty (U)

    U(T) =
        alpha * H(T)/Hmax
        + beta * (1-W(T))
        + gamma * exp(-lambda_unc*T)

IMPORTANT
---------

The recovered V6 research does NOT provide a verified standalone
six-dimension aggregation formula for RDS.

Therefore this engine does NOT invent:

    - arbitrary risk weights
    - arbitrary thresholds
    - fake RDS values
    - synthetic confidence
    - fabricated risk states

A numeric RDS is produced only when an explicit calibrated
six-dimension mapping is supplied by the caller.

EQ-0008 uncertainty is calculated independently.

It is NOT silently converted into RDS.

RDS is not a trading decision.
RDS does not authorize execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import exp, isfinite
from typing import Any, Mapping, Optional


# ============================================================================
# CONSTANTS
# ============================================================================

ENGINE_NAME = "RDS"
ENGINE_VERSION = "V6"

EQUATION_ID = "EQ-0008"

MIN_RISK = 0.0
MAX_RISK = 1.0

MIN_RDS = 0.0
MAX_RDS = 100.0

TOTAL_RISK_COMPONENTS = 6


# ============================================================================
# STATUS
# ============================================================================

class RDSStatus(str, Enum):
    VALID = "VALID"
    PARTIAL = "PARTIAL"
    INSUFFICIENT = "INSUFFICIENT"
    INVALID = "INVALID"


# ============================================================================
# RISK DIMENSIONS
# ============================================================================

class RiskDimension(str, Enum):
    MARKET = "market"
    LIQUIDITY = "liquidity"
    VOLATILITY = "volatility"
    EVENT = "event"
    CORRELATION = "correlation"
    EXECUTION = "execution"


# ============================================================================
# RISK STATE
# ============================================================================

class RiskState(str, Enum):
    UNKNOWN = "UNKNOWN"


# ============================================================================
# MAPPING STATE
# ============================================================================

class RDSMappingState(str, Enum):
    NOT_CALCULATED = "NOT_CALCULATED"
    INCOMPLETE = "INCOMPLETE"
    EXPLICIT_CALIBRATED = "EXPLICIT_CALIBRATED"


# ============================================================================
# INPUT
# ============================================================================

@dataclass(frozen=True)
class RDSInputs:
    """
    Risk input state.

    Each risk dimension must be independently derived upstream
    and supplied on [0,1].

        0 = minimum measured risk contribution
        1 = maximum measured risk contribution

    No missing risk dimension is silently replaced.

    EQ-0008 inputs:

        entropy_normalized = H/Hmax
        evidence_weight    = W(T)
        elapsed_time       = T

    EQ-0008:

        U(T) =
            alpha * H/Hmax
            + beta * (1-W(T))
            + gamma * exp(-lambda_unc*T)

    Coefficients require calibration.
    """

    market_risk: Optional[float] = None
    liquidity_risk: Optional[float] = None
    volatility_risk: Optional[float] = None
    event_risk: Optional[float] = None
    correlation_risk: Optional[float] = None
    execution_risk: Optional[float] = None

    # EQ-0008
    entropy_normalized: Optional[float] = None
    evidence_weight: Optional[float] = None
    elapsed_time: Optional[float] = None

    alpha: Optional[float] = None
    beta: Optional[float] = None
    gamma: Optional[float] = None
    lambda_unc: Optional[float] = None

    # Explicit external/calibrated RDS mapping.
    market_weight: Optional[float] = None
    liquidity_weight: Optional[float] = None
    volatility_weight: Optional[float] = None
    event_weight: Optional[float] = None
    correlation_weight: Optional[float] = None
    execution_weight: Optional[float] = None

    # Optional externally calibrated uncertainty contribution.
    #
    # This is NOT part of the verified EQ-0008 equation.
    uncertainty_weight: Optional[float] = None

    metadata: Optional[Mapping[str, Any]] = None


# ============================================================================
# D13 FACING STATE
# ============================================================================

@dataclass(frozen=True)
class RDSState:
    """
    Normalized RDS state intended for downstream consumption.

    This object carries intelligence state only.

    It does NOT contain:
        - BUY/SELL
        - execution authorization
        - order instructions
        - confidence fabricated by RDS
    """

    rds: Optional[float]

    risk_state: RiskState

    market_risk: Optional[float]
    liquidity_risk: Optional[float]
    volatility_risk: Optional[float]
    event_risk: Optional[float]
    correlation_risk: Optional[float]
    execution_risk: Optional[float]

    uncertainty: Optional[float]

    mapping_state: RDSMappingState

    equation_id: str = EQUATION_ID
    source_engine: str = ENGINE_NAME
    source_version: str = ENGINE_VERSION

    decision_authority: str = "NONE"

    market_memory_link: Optional[Mapping[str, Any]] = None

    provenance: Optional[Mapping[str, Any]] = None

    def __post_init__(self) -> None:

        if self.market_memory_link is None:
            object.__setattr__(
                self,
                "market_memory_link",
                {
                    "connected": False,
                    "role": "INTERFACE_ONLY",
                },
            )

        if self.provenance is None:
            object.__setattr__(
                self,
                "provenance",
                {
                    "formula_status":
                        "EQ-0008_VERIFIED",
                    "rds_mapping_status":
                        self.mapping_state.value,
                    "score_normalization":
                        "RDS_0_100_ONLY_WHEN_CALIBRATED",
                },
            )


# ============================================================================
# RESULT
# ============================================================================

@dataclass(frozen=True)
class RDSResult:

    status: RDSStatus

    rds: Optional[float]

    risk_state: RiskState

    market_risk: Optional[float]
    liquidity_risk: Optional[float]
    volatility_risk: Optional[float]
    event_risk: Optional[float]
    correlation_risk: Optional[float]
    execution_risk: Optional[float]

    uncertainty: Optional[float]

    weighted_risk_density: Optional[float]

    risk_components_available: int
    risk_components_total: int

    mapping_state: RDSMappingState

    equation: str
    equation_id: str

    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    engine: str = ENGINE_NAME
    version: str = ENGINE_VERSION

    metadata: Optional[Mapping[str, Any]] = None

    rds_state: Optional[RDSState] = None

    def __post_init__(self) -> None:

        if self.metadata is None:
            object.__setattr__(
                self,
                "metadata",
                {},
            )

    @property
    def is_valid(self) -> bool:
        return self.status == RDSStatus.VALID

    @property
    def score(self) -> Optional[float]:
        return self.rds

    def as_dict(self) -> dict[str, Any]:

        return {
            "status": self.status.value,
            "rds": self.rds,
            "score": self.score,

            "risk_state":
                self.risk_state.value,

            "market_risk":
                self.market_risk,

            "liquidity_risk":
                self.liquidity_risk,

            "volatility_risk":
                self.volatility_risk,

            "event_risk":
                self.event_risk,

            "correlation_risk":
                self.correlation_risk,

            "execution_risk":
                self.execution_risk,

            "uncertainty":
                self.uncertainty,

            "weighted_risk_density":
                self.weighted_risk_density,

            "risk_components_available":
                self.risk_components_available,

            "risk_components_total":
                self.risk_components_total,

            "mapping_state":
                self.mapping_state.value,

            "equation":
                self.equation,

            "equation_id":
                self.equation_id,

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

            "rds_state":
                None
                if self.rds_state is None
                else {
                    "rds":
                        self.rds_state.rds,

                    "risk_state":
                        self.rds_state.risk_state.value,

                    "market_risk":
                        self.rds_state.market_risk,

                    "liquidity_risk":
                        self.rds_state.liquidity_risk,

                    "volatility_risk":
                        self.rds_state.volatility_risk,

                    "event_risk":
                        self.rds_state.event_risk,

                    "correlation_risk":
                        self.rds_state.correlation_risk,

                    "execution_risk":
                        self.rds_state.execution_risk,

                    "uncertainty":
                        self.rds_state.uncertainty,

                    "mapping_state":
                        self.rds_state.mapping_state.value,

                    "equation_id":
                        self.rds_state.equation_id,

                    "source_engine":
                        self.rds_state.source_engine,

                    "source_version":
                        self.rds_state.source_version,

                    "decision_authority":
                        self.rds_state.decision_authority,

                    "market_memory_link":
                        dict(
                            self.rds_state.market_memory_link
                        ),

                    "provenance":
                        dict(
                            self.rds_state.provenance
                        ),
                },
        }


# ============================================================================
# ENGINE
# ============================================================================

class RDSEngine:

    UNCERTAINTY_EQUATION = (
        "U(T) = "
        "alpha*(H/Hmax) "
        "+ beta*(1-W(T)) "
        "+ gamma*exp(-lambda_unc*T)"
    )

    RDS_EQUATION = (
        "RDS = 100 * weighted_risk_density"
    )

    TOTAL_COMPONENTS = TOTAL_RISK_COMPONENTS

    # ------------------------------------------------------------------------
    # MAIN
    # ------------------------------------------------------------------------

    def calculate(
        self,
        inputs: RDSInputs,
    ) -> RDSResult:

        if not isinstance(
            inputs,
            RDSInputs,
        ):
            return self._invalid(
                "inputs must be RDSInputs"
            )

        errors: list[str] = []
        warnings: list[str] = []

        values = {
            RiskDimension.MARKET:
                inputs.market_risk,

            RiskDimension.LIQUIDITY:
                inputs.liquidity_risk,

            RiskDimension.VOLATILITY:
                inputs.volatility_risk,

            RiskDimension.EVENT:
                inputs.event_risk,

            RiskDimension.CORRELATION:
                inputs.correlation_risk,

            RiskDimension.EXECUTION:
                inputs.execution_risk,
        }

        # ------------------------------------------------------------------
        # VALIDATE RISK DIMENSIONS
        # ------------------------------------------------------------------

        for dimension, value in values.items():

            if value is None:
                continue

            validation_error = (
                self._validate_unit_value(
                    value,
                    f"{dimension.value}_risk",
                )
            )

            if validation_error:
                errors.append(
                    validation_error
                )

        if errors:
            return self._invalid(
                *errors
            )

        # ------------------------------------------------------------------
        # EQ-0008
        # ------------------------------------------------------------------

        uncertainty, uncertainty_errors = (
            self._calculate_uncertainty(
                inputs
            )
        )

        errors.extend(
            uncertainty_errors
        )

        if errors:
            return self._invalid(
                *errors
            )

        # ------------------------------------------------------------------
        # AVAILABLE COMPONENTS
        # ------------------------------------------------------------------

        available_count = sum(
            value is not None
            for value in values.values()
        )

        if (
            available_count == 0
            and uncertainty is None
        ):

            state = self._build_state(
                inputs=inputs,
                rds=None,
                uncertainty=None,
                mapping_state=(
                    RDSMappingState.NOT_CALCULATED
                ),
            )

            return RDSResult(
                status=RDSStatus.INSUFFICIENT,
                rds=None,
                risk_state=RiskState.UNKNOWN,

                market_risk=inputs.market_risk,
                liquidity_risk=inputs.liquidity_risk,
                volatility_risk=inputs.volatility_risk,
                event_risk=inputs.event_risk,
                correlation_risk=inputs.correlation_risk,
                execution_risk=inputs.execution_risk,

                uncertainty=None,
                weighted_risk_density=None,

                risk_components_available=0,
                risk_components_total=self.TOTAL_COMPONENTS,

                mapping_state=(
                    RDSMappingState.NOT_CALCULATED
                ),

                equation=self.RDS_EQUATION,
                equation_id=EQUATION_ID,

                warnings=(
                    "No observable/calculated "
                    "risk component supplied.",
                ),

                rds_state=state,
            )

        # ------------------------------------------------------------------
        # WEIGHTS
        # ------------------------------------------------------------------

        weights = {
            RiskDimension.MARKET:
                inputs.market_weight,

            RiskDimension.LIQUIDITY:
                inputs.liquidity_weight,

            RiskDimension.VOLATILITY:
                inputs.volatility_weight,

            RiskDimension.EVENT:
                inputs.event_weight,

            RiskDimension.CORRELATION:
                inputs.correlation_weight,

            RiskDimension.EXECUTION:
                inputs.execution_weight,
        }

        supplied_weights = [
            weight
            for weight in weights.values()
            if weight is not None
        ]

        # ------------------------------------------------------------------
        # NO CALIBRATED MAPPING
        # ------------------------------------------------------------------

        if not supplied_weights:

            warnings.append(
                "RDS 0-100 aggregation not calculated: "
                "no explicit calibrated dimension weights supplied."
            )

            if uncertainty is not None:
                warnings.append(
                    "EQ-0008 uncertainty calculated independently; "
                    "it is not silently converted into RDS."
                )

            state = self._build_state(
                inputs=inputs,
                rds=None,
                uncertainty=uncertainty,
                mapping_state=(
                    RDSMappingState.NOT_CALCULATED
                ),
            )

            return RDSResult(
                status=RDSStatus.PARTIAL,

                rds=None,

                risk_state=RiskState.UNKNOWN,

                market_risk=inputs.market_risk,
                liquidity_risk=inputs.liquidity_risk,
                volatility_risk=inputs.volatility_risk,
                event_risk=inputs.event_risk,
                correlation_risk=inputs.correlation_risk,
                execution_risk=inputs.execution_risk,

                uncertainty=uncertainty,

                weighted_risk_density=None,

                risk_components_available=available_count,
                risk_components_total=self.TOTAL_COMPONENTS,

                mapping_state=(
                    RDSMappingState.NOT_CALCULATED
                ),

                equation=self.RDS_EQUATION,
                equation_id=EQUATION_ID,

                warnings=tuple(
                    warnings
                ),

                metadata={
                    "rds_mapping":
                        "NOT_CALCULATED",

                    "reason":
                        "No verified standalone "
                        "six-dimension aggregation supplied.",

                    "uncertainty_equation":
                        self.UNCERTAINTY_EQUATION,
                },

                rds_state=state,
            )

        # ------------------------------------------------------------------
        # COMPLETE WEIGHTS REQUIRED
        # ------------------------------------------------------------------

        missing_weights = [
            dimension.value
            for dimension, weight in weights.items()
            if weight is None
        ]

        if missing_weights:

            state = self._build_state(
                inputs=inputs,
                rds=None,
                uncertainty=uncertainty,
                mapping_state=(
                    RDSMappingState.INCOMPLETE
                ),
            )

            return RDSResult(
                status=RDSStatus.PARTIAL,

                rds=None,

                risk_state=RiskState.UNKNOWN,

                market_risk=inputs.market_risk,
                liquidity_risk=inputs.liquidity_risk,
                volatility_risk=inputs.volatility_risk,
                event_risk=inputs.event_risk,
                correlation_risk=inputs.correlation_risk,
                execution_risk=inputs.execution_risk,

                uncertainty=uncertainty,

                weighted_risk_density=None,

                risk_components_available=available_count,
                risk_components_total=self.TOTAL_COMPONENTS,

                mapping_state=(
                    RDSMappingState.INCOMPLETE
                ),

                equation=self.RDS_EQUATION,
                equation_id=EQUATION_ID,

                warnings=(
                    "Incomplete calibrated RDS mapping; "
                    "missing weights: "
                    + ", ".join(
                        missing_weights
                    ),
                ),

                rds_state=state,
            )

        # ------------------------------------------------------------------
        # VALIDATE WEIGHTS
        # ------------------------------------------------------------------

        for dimension, weight in weights.items():

            validation_error = (
                self._validate_weight(
                    weight,
                    f"{dimension.value}_weight",
                )
            )

            if validation_error:
                errors.append(
                    validation_error
                )

        if errors:
            return self._invalid(
                *errors
            )

        weight_sum = sum(
            float(weight)
            for weight in weights.values()
        )

        # Do not use exact floating point equality.
        if abs(
            weight_sum - 1.0
        ) > 1e-12:

            return self._invalid(
                "Calibrated RDS weights must sum to 1.0."
            )

        # ------------------------------------------------------------------
        # ALL SIX RISK COMPONENTS REQUIRED
        # ------------------------------------------------------------------

        missing_components = [
            dimension.value
            for dimension, value in values.items()
            if value is None
        ]

        if missing_components:

            state = self._build_state(
                inputs=inputs,
                rds=None,
                uncertainty=uncertainty,
                mapping_state=(
                    RDSMappingState.INCOMPLETE
                ),
            )

            return RDSResult(
                status=RDSStatus.PARTIAL,

                rds=None,

                risk_state=RiskState.UNKNOWN,

                market_risk=inputs.market_risk,
                liquidity_risk=inputs.liquidity_risk,
                volatility_risk=inputs.volatility_risk,
                event_risk=inputs.event_risk,
                correlation_risk=inputs.correlation_risk,
                execution_risk=inputs.execution_risk,

                uncertainty=uncertainty,

                weighted_risk_density=None,

                risk_components_available=available_count,
                risk_components_total=self.TOTAL_COMPONENTS,

                mapping_state=(
                    RDSMappingState.INCOMPLETE
                ),

                equation=self.RDS_EQUATION,
                equation_id=EQUATION_ID,

                warnings=(
                    "RDS requires all six risk "
                    "dimensions for calibrated aggregation. "
                    "Missing: "
                    + ", ".join(
                        missing_components
                    ),
                ),

                rds_state=state,
            )

        # ------------------------------------------------------------------
        # CALIBRATED WEIGHTED RISK DENSITY
        # ------------------------------------------------------------------

        weighted_risk_density = sum(
            float(
                values[dimension]
            )
            * float(
                weights[dimension]
            )
            for dimension in values
        )

        # ------------------------------------------------------------------
        # OPTIONAL EXPLICIT UNCERTAINTY CONTRIBUTION
        # ------------------------------------------------------------------

        if (
            uncertainty is not None
            and inputs.uncertainty_weight is not None
        ):

            uncertainty_weight = (
                inputs.uncertainty_weight
            )

            validation_error = (
                self._validate_unit_value(
                    uncertainty_weight,
                    "uncertainty_weight",
                )
            )

            if validation_error:
                return self._invalid(
                    validation_error
                )

            weighted_risk_density = (
                weighted_risk_density
                * (
                    1.0
                    - float(
                        uncertainty_weight
                    )
                )
                + uncertainty
                * float(
                    uncertainty_weight
                )
            )

        # ------------------------------------------------------------------
        # DOMAIN CHECK
        # ------------------------------------------------------------------

        if not (
            MIN_RISK
            <= weighted_risk_density
            <= MAX_RISK
        ):

            return self._invalid(
                "Weighted risk density left [0,1] domain."
            )

        rds = (
            weighted_risk_density
            * 100.0
        )

        if not (
            MIN_RDS
            <= rds
            <= MAX_RDS
        ):

            return self._invalid(
                "RDS left [0,100] domain."
            )

        # ------------------------------------------------------------------
        # FINAL STATE
        # ------------------------------------------------------------------

        state = self._build_state(
            inputs=inputs,
            rds=rds,
            uncertainty=uncertainty,
            mapping_state=(
                RDSMappingState.EXPLICIT_CALIBRATED
            ),
        )

        return RDSResult(
            status=RDSStatus.VALID,

            rds=rds,

            risk_state=RiskState.UNKNOWN,

            market_risk=inputs.market_risk,
            liquidity_risk=inputs.liquidity_risk,
            volatility_risk=inputs.volatility_risk,
            event_risk=inputs.event_risk,
            correlation_risk=inputs.correlation_risk,
            execution_risk=inputs.execution_risk,

            uncertainty=uncertainty,

            weighted_risk_density=(
                weighted_risk_density
            ),

            risk_components_available=available_count,
            risk_components_total=self.TOTAL_COMPONENTS,

            mapping_state=(
                RDSMappingState.EXPLICIT_CALIBRATED
            ),

            equation=self.RDS_EQUATION,
            equation_id=EQUATION_ID,

            warnings=tuple(
                warnings
            ),

            metadata={
                "rds_mapping":
                    "EXPLICIT_CALIBRATED_MAPPING",

                "weights_sum":
                    weight_sum,

                "uncertainty_weight":
                    inputs.uncertainty_weight,

                "uncertainty_equation":
                    self.UNCERTAINTY_EQUATION,

                "decision_authority":
                    "NONE",
            },

            rds_state=state,
        )

    # =========================================================================
    # EQ-0008
    # =========================================================================

    @staticmethod
    def _calculate_uncertainty(
        inputs: RDSInputs,
    ) -> tuple[
        Optional[float],
        list[str],
    ]:

        supplied = any(
            value is not None
            for value in (
                inputs.entropy_normalized,
                inputs.evidence_weight,
                inputs.elapsed_time,
                inputs.alpha,
                inputs.beta,
                inputs.gamma,
                inputs.lambda_unc,
            )
        )

        if not supplied:
            return None, []

        required = {
            "entropy_normalized":
                inputs.entropy_normalized,

            "evidence_weight":
                inputs.evidence_weight,

            "elapsed_time":
                inputs.elapsed_time,

            "alpha":
                inputs.alpha,

            "beta":
                inputs.beta,

            "gamma":
                inputs.gamma,

            "lambda_unc":
                inputs.lambda_unc,
        }

        missing = [
            name
            for name, value in required.items()
            if value is None
        ]

        if missing:
            return None, [
                "EQ-0008 incomplete; missing: "
                + ", ".join(missing)
            ]

        entropy = float(
            inputs.entropy_normalized
        )

        evidence_weight = float(
            inputs.evidence_weight
        )

        elapsed_time = float(
            inputs.elapsed_time
        )

        alpha = float(
            inputs.alpha
        )

        beta = float(
            inputs.beta
        )

        gamma = float(
            inputs.gamma
        )

        lambda_unc = float(
            inputs.lambda_unc
        )

        values = (
            entropy,
            evidence_weight,
            elapsed_time,
            alpha,
            beta,
            gamma,
            lambda_unc,
        )

        if not all(
            isfinite(value)
            for value in values
        ):
            return None, [
                "EQ-0008 inputs must all be finite."
            ]

        if not (
            0.0
            <= entropy
            <= 1.0
        ):
            return None, [
                "entropy_normalized must be in [0,1]."
            ]

        if not (
            0.0
            <= evidence_weight
            <= 1.0
        ):
            return None, [
                "evidence_weight must be in [0,1]."
            ]

        if elapsed_time < 0.0:
            return None, [
                "elapsed_time must be >= 0."
            ]

        if alpha < 0.0:
            return None, [
                "alpha must be >= 0."
            ]

        if beta < 0.0:
            return None, [
                "beta must be >= 0."
            ]

        if gamma < 0.0:
            return None, [
                "gamma must be >= 0."
            ]

        if lambda_unc < 0.0:
            return None, [
                "lambda_unc must be >= 0."
            ]

        uncertainty = (
            alpha * entropy
            + beta * (
                1.0 - evidence_weight
            )
            + gamma * exp(
                -lambda_unc * elapsed_time
            )
        )

        # IMPORTANT:
        # EQ-0008 official domain is 0 <= U <= 1.
        # Do not clamp an invalid result.
        if not (
            0.0
            <= uncertainty
            <= 1.0
        ):
            return None, [
                "EQ-0008 uncertainty left [0,1] domain; "
                "coefficient calibration is invalid for this input."
            ]

        return uncertainty, []

    # =========================================================================
    # STATE BUILDER
    # =========================================================================

    @staticmethod
    def _build_state(
        *,
        inputs: RDSInputs,
        rds: Optional[float],
        uncertainty: Optional[float],
        mapping_state: RDSMappingState,
    ) -> RDSState:

        return RDSState(
            rds=rds,

            risk_state=RiskState.UNKNOWN,

            market_risk=inputs.market_risk,
            liquidity_risk=inputs.liquidity_risk,
            volatility_risk=inputs.volatility_risk,
            event_risk=inputs.event_risk,
            correlation_risk=inputs.correlation_risk,
            execution_risk=inputs.execution_risk,

            uncertainty=uncertainty,

            mapping_state=mapping_state,

            market_memory_link={
                "connected": False,
                "role": "INTERFACE_ONLY",
                "future_consumer":
                    "MARKET_MEMORY_ENGINE",
            },

            provenance={
                "source_engine":
                    ENGINE_NAME,

                "source_version":
                    ENGINE_VERSION,

                "equation_id":
                    EQUATION_ID,

                "rds_mapping":
                    mapping_state.value,

                "score_normalization":
                    "NO_UNVERIFIED_NORMALIZATION",

                "decision_authority":
                    "NONE",
            },
        )

    # =========================================================================
    # VALIDATION HELPERS
    # =========================================================================

    @staticmethod
    def _validate_unit_value(
        value: Any,
        name: str,
    ) -> Optional[str]:

        if isinstance(
            value,
            bool,
        ):
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
            0.0
            <= value
            <= 1.0
        ):
            return (
                f"{name} must be in [0,1]"
            )

        return None

    @staticmethod
    def _validate_weight(
        value: Any,
        name: str,
    ) -> Optional[str]:

        if isinstance(
            value,
            bool,
        ):
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
    ) -> RDSResult:

        return RDSResult(
            status=RDSStatus.INVALID,

            rds=None,

            risk_state=RiskState.UNKNOWN,

            market_risk=None,
            liquidity_risk=None,
            volatility_risk=None,
            event_risk=None,
            correlation_risk=None,
            execution_risk=None,

            uncertainty=None,

            weighted_risk_density=None,

            risk_components_available=0,
            risk_components_total=(
                RDSEngine.TOTAL_COMPONENTS
            ),

            mapping_state=(
                RDSMappingState.NOT_CALCULATED
            ),

            equation=(
                RDSEngine.RDS_EQUATION
            ),

            equation_id=EQUATION_ID,

            errors=tuple(errors),

            warnings=(),

            rds_state=None,
        )


# ============================================================================
# FUNCTIONAL API
# ============================================================================

def calculate_rds(
    inputs: RDSInputs,
) -> RDSResult:

    return RDSEngine().calculate(
        inputs
    )


def calculate_uncertainty_eq0008(
    *,
    entropy_normalized: float,
    evidence_weight: float,
    elapsed_time: float,
    alpha: float,
    beta: float,
    gamma: float,
    lambda_unc: float,
) -> Optional[float]:

    result = RDSEngine().calculate(
        RDSInputs(
            entropy_normalized=entropy_normalized,
            evidence_weight=evidence_weight,
            elapsed_time=elapsed_time,
            alpha=alpha,
            beta=beta,
            gamma=gamma,
            lambda_unc=lambda_unc,
        )
    )

    return result.uncertainty


# ============================================================================
# SELF TESTS
# ============================================================================

def _run_self_tests() -> None:

    equal_weights = 1.0 / 6.0

    # ------------------------------------------------------------------------
    # TEST 1 â€” No inputs
    # ------------------------------------------------------------------------

    result = calculate_rds(
        RDSInputs()
    )

    assert (
        result.status
        == RDSStatus.INSUFFICIENT
    )

    assert result.rds is None

    # ------------------------------------------------------------------------
    # TEST 2 â€” Risk dimensions without mapping
    # ------------------------------------------------------------------------

    result = calculate_rds(
        RDSInputs(
            market_risk=0.2,
            liquidity_risk=0.1,
            volatility_risk=0.3,
            event_risk=0.0,
            correlation_risk=0.2,
            execution_risk=0.1,
        )
    )

    assert (
        result.status
        == RDSStatus.PARTIAL
    )

    assert result.rds is None

    assert (
        result.mapping_state
        == RDSMappingState.NOT_CALCULATED
    )

    # ------------------------------------------------------------------------
    # TEST 3 â€” Equal calibrated weights
    # ------------------------------------------------------------------------

    result = calculate_rds(
        RDSInputs(
            market_risk=0.2,
            liquidity_risk=0.1,
            volatility_risk=0.3,
            event_risk=0.0,
            correlation_risk=0.2,
            execution_risk=0.1,

            market_weight=equal_weights,
            liquidity_weight=equal_weights,
            volatility_weight=equal_weights,
            event_weight=equal_weights,
            correlation_weight=equal_weights,
            execution_weight=equal_weights,
        )
    )

    assert (
        result.status
        == RDSStatus.VALID
    )

    assert abs(
        result.rds - 15.0
    ) < 1e-12

    assert abs(
        result.weighted_risk_density
        - 0.15
    ) < 1e-12

    assert (
        result.mapping_state
        == RDSMappingState.EXPLICIT_CALIBRATED
    )

    assert result.rds_state is not None

    assert (
        result.rds_state.decision_authority
        == "NONE"
    )

    # ------------------------------------------------------------------------
    # TEST 4 â€” Zero risk
    # ------------------------------------------------------------------------

    result = calculate_rds(
        RDSInputs(
            market_risk=0.0,
            liquidity_risk=0.0,
            volatility_risk=0.0,
            event_risk=0.0,
            correlation_risk=0.0,
            execution_risk=0.0,

            market_weight=equal_weights,
            liquidity_weight=equal_weights,
            volatility_weight=equal_weights,
            event_weight=equal_weights,
            correlation_weight=equal_weights,
            execution_weight=equal_weights,
        )
    )

    assert result.rds == 0.0

    # ------------------------------------------------------------------------
    # TEST 5 â€” Maximum risk
    # ------------------------------------------------------------------------

    result = calculate_rds(
        RDSInputs(
            market_risk=1.0,
            liquidity_risk=1.0,
            volatility_risk=1.0,
            event_risk=1.0,
            correlation_risk=1.0,
            execution_risk=1.0,

            market_weight=equal_weights,
            liquidity_weight=equal_weights,
            volatility_weight=equal_weights,
            event_weight=equal_weights,
            correlation_weight=equal_weights,
            execution_weight=equal_weights,
        )
    )

    assert result.rds == 100.0

    # ------------------------------------------------------------------------
    # TEST 6 â€” Weight sum rejection
    # ------------------------------------------------------------------------

    result = calculate_rds(
        RDSInputs(
            market_risk=0.1,
            liquidity_risk=0.1,
            volatility_risk=0.1,
            event_risk=0.1,
            correlation_risk=0.1,
            execution_risk=0.1,

            market_weight=0.2,
            liquidity_weight=0.2,
            volatility_weight=0.2,
            event_weight=0.2,
            correlation_weight=0.1,
            execution_weight=0.05,
        )
    )

    assert (
        result.status
        == RDSStatus.INVALID
    )

    # ------------------------------------------------------------------------
    # TEST 7 â€” Missing component
    # ------------------------------------------------------------------------

    result = calculate_rds(
        RDSInputs(
            market_risk=0.1,
            liquidity_risk=0.1,
            volatility_risk=0.1,
            event_risk=0.1,
            correlation_risk=0.1,
            execution_risk=None,

            market_weight=equal_weights,
            liquidity_weight=equal_weights,
            volatility_weight=equal_weights,
            event_weight=equal_weights,
            correlation_weight=equal_weights,
            execution_weight=equal_weights,
        )
    )

    assert (
        result.status
        == RDSStatus.PARTIAL
    )

    assert result.rds is None

    # ------------------------------------------------------------------------
    # TEST 8 â€” EQ-0008 exact
    #
    # U = .2*.5 + .3*(1-.8) + .1*exp(0)
    #   = .10 + .06 + .10
    #   = .26
    # ------------------------------------------------------------------------

    uncertainty = calculate_uncertainty_eq0008(
        entropy_normalized=0.5,
        evidence_weight=0.8,
        elapsed_time=0.0,
        alpha=0.2,
        beta=0.3,
        gamma=0.1,
        lambda_unc=0.5,
    )

    assert uncertainty is not None

    assert abs(
        uncertainty - 0.26
    ) < 1e-12

    # ------------------------------------------------------------------------
    # TEST 9 â€” EQ-0008 temporal decay
    # ------------------------------------------------------------------------

    uncertainty = calculate_uncertainty_eq0008(
        entropy_normalized=0.0,
        evidence_weight=1.0,
        elapsed_time=2.0,
        alpha=0.0,
        beta=0.0,
        gamma=1.0,
        lambda_unc=0.5,
    )

    assert uncertainty is not None

    assert abs(
        uncertainty - exp(-1.0)
    ) < 1e-12

    # ------------------------------------------------------------------------
    # TEST 10 â€” EQ-0008 invalid entropy
    # ------------------------------------------------------------------------

    result = calculate_rds(
        RDSInputs(
            entropy_normalized=1.5,
            evidence_weight=0.8,
            elapsed_time=0.0,
            alpha=0.2,
            beta=0.3,
            gamma=0.1,
            lambda_unc=0.5,
        )
    )

    assert (
        result.status
        == RDSStatus.INVALID
    )

    # ------------------------------------------------------------------------
    # TEST 11 â€” Negative risk
    # ------------------------------------------------------------------------

    result = calculate_rds(
        RDSInputs(
            market_risk=-0.1,
        )
    )

    assert (
        result.status
        == RDSStatus.INVALID
    )

    # ------------------------------------------------------------------------
    # TEST 12 â€” Risk > 1
    # ------------------------------------------------------------------------

    result = calculate_rds(
        RDSInputs(
            volatility_risk=1.1,
        )
    )

    assert (
        result.status
        == RDSStatus.INVALID
    )

    # ------------------------------------------------------------------------
    # TEST 13 â€” Infinite risk
    # ------------------------------------------------------------------------

    result = calculate_rds(
        RDSInputs(
            execution_risk=float("inf"),
        )
    )

    assert (
        result.status
        == RDSStatus.INVALID
    )

    # ------------------------------------------------------------------------
    # TEST 14 â€” Explicit uncertainty contribution
    #
    # U = .65
    # Risk = .20
    # Combined = .425
    # RDS = 42.5
    # ------------------------------------------------------------------------

    result = calculate_rds(
        RDSInputs(
            market_risk=0.2,
            liquidity_risk=0.2,
            volatility_risk=0.2,
            event_risk=0.2,
            correlation_risk=0.2,
            execution_risk=0.2,

            market_weight=equal_weights,
            liquidity_weight=equal_weights,
            volatility_weight=equal_weights,
            event_weight=equal_weights,
            correlation_weight=equal_weights,
            execution_weight=equal_weights,

            entropy_normalized=0.8,
            evidence_weight=0.5,
            elapsed_time=0.0,

            alpha=0.5,
            beta=0.5,
            gamma=0.0,
            lambda_unc=0.0,

            uncertainty_weight=0.5,
        )
    )

    assert (
        result.status
        == RDSStatus.VALID
    )

    assert abs(
        result.uncertainty - 0.65
    ) < 1e-12

    assert abs(
        result.rds - 42.5
    ) < 1e-12

    # ------------------------------------------------------------------------
    # TEST 15 â€” EQ-0008 result > 1 rejected
    #
    # alpha + beta + gamma can produce invalid U.
    # It must NOT be silently clamped.
    # ------------------------------------------------------------------------

    result = calculate_rds(
        RDSInputs(
            entropy_normalized=1.0,
            evidence_weight=0.0,
            elapsed_time=0.0,

            alpha=1.0,
            beta=1.0,
            gamma=1.0,
            lambda_unc=0.0,
        )
    )

    assert (
        result.status
        == RDSStatus.INVALID
    )

    # ------------------------------------------------------------------------
    # TEST 16 â€” RDS bounded
    # ------------------------------------------------------------------------

    result = calculate_rds(
        RDSInputs(
            market_risk=0.5,
            liquidity_risk=0.5,
            volatility_risk=0.5,
            event_risk=0.5,
            correlation_risk=0.5,
            execution_risk=0.5,

            market_weight=equal_weights,
            liquidity_weight=equal_weights,
            volatility_weight=equal_weights,
            event_weight=equal_weights,
            correlation_weight=equal_weights,
            execution_weight=equal_weights,
        )
    )

    assert (
        0.0
        <= result.rds
        <= 100.0
    )

    # ------------------------------------------------------------------------
    # TEST 17 â€” D13 state exists
    # ------------------------------------------------------------------------

    assert result.rds_state is not None

    assert (
        result.rds_state.equation_id
        == "EQ-0008"
    )

    # ------------------------------------------------------------------------
    # TEST 18 â€” No execution authority
    # ------------------------------------------------------------------------

    assert not hasattr(
        result,
        "execution_authorized",
    )

    assert (
        result.rds_state.decision_authority
        == "NONE"
    )

    # ------------------------------------------------------------------------
    # TEST 19 â€” Market Memory interface only
    # ------------------------------------------------------------------------

    assert (
        result.rds_state.market_memory_link[
            "connected"
        ]
        is False
    )

    # ------------------------------------------------------------------------
    # TEST 20 â€” Score remains numeric RDS only
    # ------------------------------------------------------------------------

    assert (
        result.score
        == result.rds
    )

    print(
        "RDS V6 EQ-0008 + Risk Density self-tests: PASS"
    )


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "ENGINE_NAME",
    "ENGINE_VERSION",
    "EQUATION_ID",

    "RDSStatus",
    "RiskDimension",
    "RiskState",
    "RDSMappingState",

    "RDSInputs",
    "RDSState",
    "RDSResult",

    "RDSEngine",

    "calculate_rds",
    "calculate_uncertainty_eq0008",
]


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    _run_self_tests()
