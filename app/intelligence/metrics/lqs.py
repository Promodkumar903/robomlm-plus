"""
ROBOMLM_PLUS
LQS â€” Liquidity Quality Score / Liquidity Engine
V6 / EQ-0003

OFFICIAL V6 LIQUIDITY EQUATION
------------------------------

    L(T) =
        Î± * L_depth(T)
        + Î² * L_spread(T)
        + Î³ * L_resilience(T)

Components:

    L_depth =
        Î£ [ (BidVolume_i + AskVolume_i) * Weight_i ]

    Weight_i =
        exp(-Î³_depth * i)

    L_spread =
        1 / (1 + Spread_normalized)

    L_resilience(T) =
        L0 * exp(-Î»_liq * T)
        + OrderFlow_Injection(T)

IMPORTANT ENGINEERING RULE
--------------------------
V6 research explicitly identifies Î±, Î², Î³,
Î³_depth and Î»_liq as calibration parameters.

Therefore this implementation:

    - requires calibration parameters explicitly
    - never invents them
    - never silently defaults them
    - never uses fake liquidity proxies
    - never converts arbitrary values into 0..100
    - preserves raw mathematical liquidity
    - validates dimensional/reference normalization
    - rejects invalid market states

LQS is a derived liquidity quantity.

It does NOT:
    - create BUY/SELL
    - create confidence
    - authorize execution
    - infer missing order-book depth
    - treat traded volume as order-book depth
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import exp, isfinite
from typing import Any, Iterable, Mapping, Optional, Sequence


ENGINE_NAME = "LQS"
ENGINE_VERSION = "V6"
EQUATION_ID = "EQ-0003"


# ---------------------------------------------------------------------------
# STATUS
# ---------------------------------------------------------------------------

class LQSStatus(str, Enum):
    VALID = "VALID"
    PARTIAL = "PARTIAL"
    INSUFFICIENT = "INSUFFICIENT"
    INVALID = "INVALID"


# ---------------------------------------------------------------------------
# SIDE
# ---------------------------------------------------------------------------

class BookSide(str, Enum):
    BID = "BID"
    ASK = "ASK"


# ---------------------------------------------------------------------------
# DEPTH OBSERVATION
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DepthObservation:
    """
    One order-book depth level.

    level:
        1 = nearest level
        2 = second level
        ...

    volume:
        Quantity available at the level.

    price:
        Optional actual price.

    side:
        BID or ASK.
    """

    side: BookSide
    level: int
    volume: float
    price: Optional[float] = None

    def __post_init__(self) -> None:

        if not isinstance(self.level, int):
            raise TypeError(
                "level must be an integer"
            )

        if self.level < 1:
            raise ValueError(
                "level must be >= 1"
            )

        if isinstance(self.volume, bool):
            raise TypeError(
                "volume cannot be boolean"
            )

        if not isinstance(
            self.volume,
            (int, float),
        ):
            raise TypeError(
                "volume must be numeric"
            )

        if not isfinite(float(self.volume)):
            raise ValueError(
                "volume must be finite"
            )

        if float(self.volume) < 0:
            raise ValueError(
                "volume cannot be negative"
            )

        if self.price is not None:

            if isinstance(self.price, bool):
                raise TypeError(
                    "price cannot be boolean"
                )

            if not isinstance(
                self.price,
                (int, float),
            ):
                raise TypeError(
                    "price must be numeric"
                )

            if not isfinite(float(self.price)):
                raise ValueError(
                    "price must be finite"
                )

            if float(self.price) <= 0:
                raise ValueError(
                    "price must be > 0"
                )


# ---------------------------------------------------------------------------
# RESILIENCE INPUT
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ResilienceInput:
    """
    V6 resilience state.

    L_resilience(T) =
        L0 * exp(-Î»_liq*T)
        + OrderFlow_Injection(T)

    injection must already represent liquidity replenishment
    in the same normalized liquidity unit as L0.
    """

    initial_liquidity: float
    elapsed_seconds: float
    lambda_liq: float
    order_flow_injection: float = 0.0

    def __post_init__(self) -> None:

        values = {
            "initial_liquidity": self.initial_liquidity,
            "elapsed_seconds": self.elapsed_seconds,
            "lambda_liq": self.lambda_liq,
            "order_flow_injection": self.order_flow_injection,
        }

        for name, value in values.items():

            if isinstance(value, bool):
                raise TypeError(
                    f"{name} cannot be boolean"
                )

            if not isinstance(
                value,
                (int, float),
            ):
                raise TypeError(
                    f"{name} must be numeric"
                )

            if not isfinite(float(value)):
                raise ValueError(
                    f"{name} must be finite"
                )

        if self.initial_liquidity < 0:
            raise ValueError(
                "initial_liquidity must be >= 0"
            )

        if self.elapsed_seconds < 0:
            raise ValueError(
                "elapsed_seconds must be >= 0"
            )

        if self.lambda_liq < 0:
            raise ValueError(
                "lambda_liq must be >= 0"
            )

        if self.order_flow_injection < 0:
            raise ValueError(
                "order_flow_injection must be >= 0"
            )


# ---------------------------------------------------------------------------
# CALIBRATION
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LQSCalibration:
    """
    Explicit V6 calibration.

    alpha:
        Depth component weight.

    beta:
        Spread component weight.

    gamma:
        Resilience component weight.

    depth_decay:
        Î³_depth in:

            Weight_i = exp(-Î³_depth * i)

    lambda_liq:
        Liquidity decay parameter.

    depth_reference:
        Converts weighted raw order-book depth into normalized
        depth liquidity.

    spread_reference:
        Converts absolute spread into dimensionless normalized
        spread before applying:

            1 / (1 + spread_normalized)

    IMPORTANT:
        No production default calibration is supplied.
    """

    alpha: float
    beta: float
    gamma: float

    depth_decay: float
    lambda_liq: float

    depth_reference: float
    spread_reference: float

    def __post_init__(self) -> None:

        weights = {
            "alpha": self.alpha,
            "beta": self.beta,
            "gamma": self.gamma,
            "depth_decay": self.depth_decay,
            "lambda_liq": self.lambda_liq,
            "depth_reference": self.depth_reference,
            "spread_reference": self.spread_reference,
        }

        for name, value in weights.items():

            if isinstance(value, bool):
                raise TypeError(
                    f"{name} cannot be boolean"
                )

            if not isinstance(
                value,
                (int, float),
            ):
                raise TypeError(
                    f"{name} must be numeric"
                )

            if not isfinite(float(value)):
                raise ValueError(
                    f"{name} must be finite"
                )

        if self.alpha < 0:
            raise ValueError(
                "alpha must be >= 0"
            )

        if self.beta < 0:
            raise ValueError(
                "beta must be >= 0"
            )

        if self.gamma < 0:
            raise ValueError(
                "gamma must be >= 0"
            )

        weight_sum = (
            self.alpha
            + self.beta
            + self.gamma
        )

        if abs(weight_sum - 1.0) > 1e-12:
            raise ValueError(
                "alpha + beta + gamma must equal 1"
            )

        if self.depth_decay < 0:
            raise ValueError(
                "depth_decay must be >= 0"
            )

        if self.lambda_liq < 0:
            raise ValueError(
                "lambda_liq must be >= 0"
            )

        if self.depth_reference <= 0:
            raise ValueError(
                "depth_reference must be > 0"
            )

        if self.spread_reference <= 0:
            raise ValueError(
                "spread_reference must be > 0"
            )


# ---------------------------------------------------------------------------
# INPUT
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LQSInputs:
    """
    Complete market state required by EQ-0003.

    depths:
        Actual observed order-book levels.

    spread:
        Absolute best-ask minus best-bid spread.

    resilience:
        Optional resilience state. If absent, LQS can only be PARTIAL
        because the official combined equation contains resilience.

    calibration:
        Explicit market calibration.
    """

    depths: Sequence[DepthObservation]

    spread: float

    calibration: LQSCalibration

    resilience: Optional[ResilienceInput] = None

    observed_at: Optional[Any] = None


# ---------------------------------------------------------------------------
# RESULT
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LQSResult:
    """
    Complete V6 EQ-0003 result.

    raw_depth:
        Weighted order-book depth before normalization.

    depth_liquidity:
        Normalized depth component.

    spread_liquidity:
        Normalized spread component.

    resilience_liquidity:
        Resilience component.

    liquidity:
        Combined EQ-0003 result.
    """

    status: LQSStatus

    liquidity: Optional[float]

    raw_depth: Optional[float]
    depth_liquidity: Optional[float]

    spread: Optional[float]
    normalized_spread: Optional[float]
    spread_liquidity: Optional[float]

    resilience_liquidity: Optional[float]

    alpha: Optional[float]
    beta: Optional[float]
    gamma: Optional[float]

    depth_decay: Optional[float]
    lambda_liq: Optional[float]

    bid_depth: float
    ask_depth: float
    total_depth: float

    depth_level_count: int

    equation: str
    equation_id: str

    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    engine: str = ENGINE_NAME
    version: str = ENGINE_VERSION

    metadata: Mapping[str, Any] = None

    def __post_init__(self) -> None:

        if self.metadata is None:
            object.__setattr__(
                self,
                "metadata",
                {},
            )

    @property
    def is_valid(self) -> bool:
        return self.status == LQSStatus.VALID

    @property
    def score(self) -> Optional[float]:
        """
        No arbitrary 0..100 score.

        V6 EQ-0003's mathematical liquidity domain is 0..1 only
        after calibrated normalization. A customer-facing LQS
        0..100 transformation is deliberately not invented here.
        """

        return None

    def as_dict(self) -> dict[str, Any]:

        return {
            "status": self.status.value,
            "liquidity": self.liquidity,
            "score": self.score,
            "raw_depth": self.raw_depth,
            "depth_liquidity": self.depth_liquidity,
            "spread": self.spread,
            "normalized_spread": self.normalized_spread,
            "spread_liquidity": self.spread_liquidity,
            "resilience_liquidity": self.resilience_liquidity,
            "alpha": self.alpha,
            "beta": self.beta,
            "gamma": self.gamma,
            "depth_decay": self.depth_decay,
            "lambda_liq": self.lambda_liq,
            "bid_depth": self.bid_depth,
            "ask_depth": self.ask_depth,
            "total_depth": self.total_depth,
            "depth_level_count": self.depth_level_count,
            "equation": self.equation,
            "equation_id": self.equation_id,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "engine": self.engine,
            "version": self.version,
            "metadata": dict(self.metadata),
        }


# ---------------------------------------------------------------------------
# ENGINE
# ---------------------------------------------------------------------------

class LQSEngine:
    """
    ROBOMLM V6 EQ-0003 Liquidity Engine.

    Official equation:

        L(T) =
            Î± L_depth(T)
            + Î² L_spread(T)
            + Î³ L_resilience(T)

    No hidden calibration.
    """

    EQUATION = (
        "L(T) = Î±Â·L_depth(T) "
        "+ Î²Â·L_spread(T) "
        "+ Î³Â·L_resilience(T)"
    )

    DEPTH_EQUATION = (
        "L_depth = Î£[(BidVolume_i + AskVolume_i) "
        "Â· exp(-Î³_depthÂ·i)]"
    )

    SPREAD_EQUATION = (
        "L_spread = 1 / "
        "(1 + Spread_normalized)"
    )

    RESILIENCE_EQUATION = (
        "L_resilience(T) = "
        "L0Â·exp(-Î»_liqÂ·T) "
        "+ OrderFlow_Injection(T)"
    )

    # ------------------------------------------------------------------
    # MAIN
    # ------------------------------------------------------------------

    def calculate(
        self,
        inputs: LQSInputs,
    ) -> LQSResult:

        errors: list[str] = []
        warnings: list[str] = []

        if not isinstance(
            inputs,
            LQSInputs,
        ):
            return self._invalid(
                errors=[
                    "inputs must be an LQSInputs instance"
                ],
            )

        calibration = inputs.calibration

        # --------------------------------------------------------------
        # Validate spread
        # --------------------------------------------------------------

        if isinstance(inputs.spread, bool):

            errors.append(
                "spread cannot be boolean"
            )

        elif not isinstance(
            inputs.spread,
            (int, float),
        ):

            errors.append(
                "spread must be numeric"
            )

        elif not isfinite(
            float(inputs.spread)
        ):

            errors.append(
                "spread must be finite"
            )

        elif float(inputs.spread) < 0:

            errors.append(
                "spread must be >= 0"
            )

        if errors:
            return self._invalid(
                errors=errors
            )

        spread = float(
            inputs.spread
        )

        # --------------------------------------------------------------
        # Validate depth
        # --------------------------------------------------------------

        if inputs.depths is None:

            return self._insufficient(
                reason="Order-book depth is missing."
            )

        depths = tuple(
            inputs.depths
        )

        if not depths:

            return self._insufficient(
                reason="No order-book depth levels supplied."
            )

        # --------------------------------------------------------------
        # Aggregate weighted depth
        # --------------------------------------------------------------

        raw_depth = 0.0
        bid_depth = 0.0
        ask_depth = 0.0

        level_count = 0

        for depth in depths:

            if not isinstance(
                depth,
                DepthObservation,
            ):

                return self._invalid(
                    errors=[
                        "Every depth item must be "
                        "DepthObservation."
                    ]
                )

            level = depth.level
            volume = float(
                depth.volume
            )

            weight = exp(
                -calibration.depth_decay
                * level
            )

            weighted_volume = (
                volume * weight
            )

            raw_depth += weighted_volume

            if depth.side == BookSide.BID:

                bid_depth += volume

            elif depth.side == BookSide.ASK:

                ask_depth += volume

            else:

                return self._invalid(
                    errors=[
                        f"Unsupported book side: "
                        f"{depth.side}"
                    ]
                )

            level_count += 1

        # --------------------------------------------------------------
        # Normalize depth.
        #
        # The V6 equation requires L_depth to participate in the
        # dimensionless combined liquidity equation.
        #
        # Therefore an explicit market calibration reference is used.
        #
        # No arbitrary reference is supplied by this engine.
        # --------------------------------------------------------------

        depth_liquidity = (
            raw_depth
            / (
                raw_depth
                + calibration.depth_reference
            )
        )

        # --------------------------------------------------------------
        # Spread normalization
        #
        # Absolute spread has price units.
        # Explicit spread_reference makes the denominator dimensionless.
        # --------------------------------------------------------------

        normalized_spread = (
            spread
            / calibration.spread_reference
        )

        spread_liquidity = (
            1.0
            / (
                1.0
                + normalized_spread
            )
        )

        # --------------------------------------------------------------
        # Resilience
        # --------------------------------------------------------------

        resilience_liquidity: Optional[float]

        if inputs.resilience is None:

            resilience_liquidity = None

            warnings.append(
                "Resilience input is missing; "
                "combined EQ-0003 liquidity cannot be "
                "fully calculated."
            )

            return LQSResult(
                status=LQSStatus.PARTIAL,
                liquidity=None,
                raw_depth=raw_depth,
                depth_liquidity=depth_liquidity,
                spread=spread,
                normalized_spread=normalized_spread,
                spread_liquidity=spread_liquidity,
                resilience_liquidity=None,
                alpha=calibration.alpha,
                beta=calibration.beta,
                gamma=calibration.gamma,
                depth_decay=calibration.depth_decay,
                lambda_liq=calibration.lambda_liq,
                bid_depth=bid_depth,
                ask_depth=ask_depth,
                total_depth=(
                    bid_depth
                    + ask_depth
                ),
                depth_level_count=level_count,
                equation=self.EQUATION,
                equation_id=EQUATION_ID,
                errors=(),
                warnings=tuple(warnings),
                metadata={
                    "depth_equation":
                        self.DEPTH_EQUATION,
                    "spread_equation":
                        self.SPREAD_EQUATION,
                    "resilience_equation":
                        self.RESILIENCE_EQUATION,
                    "normalization":
                        "explicit calibration",
                    "score_scale":
                        "0..1 mathematical liquidity",
                    "customer_lqs_0_100":
                        None,
                },
            )

        resilience = inputs.resilience

        # Explicitly use the supplied lambda.
        decay = exp(
            -resilience.lambda_liq
            * resilience.elapsed_seconds
        )

        resilience_liquidity = (
            resilience.initial_liquidity
            * decay
            + resilience.order_flow_injection
        )

        if not isfinite(
            resilience_liquidity
        ):

            return self._invalid(
                errors=[
                    "Calculated resilience "
                    "became non-finite."
                ]
            )

        if resilience_liquidity < 0:

            return self._invalid(
                errors=[
                    "Calculated resilience "
                    "became negative."
                ]
            )

        # --------------------------------------------------------------
        # Combined equation
        # --------------------------------------------------------------

        liquidity = (
            calibration.alpha
            * depth_liquidity
            + calibration.beta
            * spread_liquidity
            + calibration.gamma
            * resilience_liquidity
        )

        if not isfinite(liquidity):

            return self._invalid(
                errors=[
                    "Combined liquidity became non-finite."
                ]
            )

        # --------------------------------------------------------------
        # Domain check
        #
        # V6 states normalized L domain 0..1.
        #
        # If resilience is >1 because injection/input is not normalized,
        # do NOT silently clip it.
        # --------------------------------------------------------------

        if (
            resilience_liquidity < 0
            or resilience_liquidity > 1
        ):

            return self._invalid(
                errors=[
                    "Resilience component is outside "
                    "the normalized [0,1] liquidity domain. "
                    "Normalize/calibrate resilience input "
                    "before combining EQ-0003."
                ],
                metadata={
                    "resilience_liquidity":
                        resilience_liquidity,
                },
            )

        if (
            liquidity < 0
            or liquidity > 1
        ):

            return self._invalid(
                errors=[
                    "Combined liquidity is outside "
                    "the V6 normalized [0,1] domain."
                ],
                metadata={
                    "calculated_liquidity":
                        liquidity,
                },
            )

        return LQSResult(
            status=LQSStatus.VALID,
            liquidity=liquidity,
            raw_depth=raw_depth,
            depth_liquidity=depth_liquidity,
            spread=spread,
            normalized_spread=normalized_spread,
            spread_liquidity=spread_liquidity,
            resilience_liquidity=resilience_liquidity,
            alpha=calibration.alpha,
            beta=calibration.beta,
            gamma=calibration.gamma,
            depth_decay=calibration.depth_decay,
            lambda_liq=calibration.lambda_liq,
            bid_depth=bid_depth,
            ask_depth=ask_depth,
            total_depth=(
                bid_depth
                + ask_depth
            ),
            depth_level_count=level_count,
            equation=self.EQUATION,
            equation_id=EQUATION_ID,
            errors=(),
            warnings=tuple(warnings),
            metadata={
                "depth_equation":
                    self.DEPTH_EQUATION,
                "spread_equation":
                    self.SPREAD_EQUATION,
                "resilience_equation":
                    self.RESILIENCE_EQUATION,
                "normalization":
                    "explicit calibration",
                "score_scale":
                    "0..1 mathematical liquidity",
                "customer_lqs_0_100":
                    None,
                "calibration_is_explicit":
                    True,
            },
        )

    # ------------------------------------------------------------------
    # MAPPING API
    # ------------------------------------------------------------------

    def calculate_from_mapping(
        self,
        data: Mapping[str, Any],
    ) -> LQSResult:

        if not isinstance(
            data,
            Mapping,
        ):

            return self._invalid(
                errors=[
                    "Input must be a mapping."
                ]
            )

        calibration = data.get(
            "calibration"
        )

        if not isinstance(
            calibration,
            LQSCalibration,
        ):

            return self._invalid(
                errors=[
                    "Explicit LQSCalibration is required."
                ]
            )

        raw_depths = data.get(
            "depths",
            ()
        )

        depths: list[
            DepthObservation
        ] = []

        try:

            for item in raw_depths:

                if isinstance(
                    item,
                    DepthObservation,
                ):

                    depths.append(item)
                    continue

                if not isinstance(
                    item,
                    Mapping,
                ):

                    return self._invalid(
                        errors=[
                            "Depth item must be a mapping "
                            "or DepthObservation."
                        ]
                    )

                side_value = item.get(
                    "side"
                )

                try:

                    side = BookSide(
                        str(side_value).upper()
                    )

                except ValueError:

                    return self._invalid(
                        errors=[
                            f"Invalid depth side: "
                            f"{side_value}"
                        ]
                    )

                depths.append(
                    DepthObservation(
                        side=side,
                        level=int(
                            item["level"]
                        ),
                        volume=float(
                            item["volume"]
                        ),
                        price=(
                            float(item["price"])
                            if item.get("price")
                            is not None
                            else None
                        ),
                    )
                )

        except (
            KeyError,
            TypeError,
            ValueError,
        ) as exc:

            return self._invalid(
                errors=[
                    f"Invalid depth input: {exc}"
                ]
            )

        resilience = data.get(
            "resilience"
        )

        if resilience is not None:

            if not isinstance(
                resilience,
                ResilienceInput,
            ):

                if not isinstance(
                    resilience,
                    Mapping,
                ):

                    return self._invalid(
                        errors=[
                            "resilience must be "
                            "ResilienceInput or mapping."
                        ]
                    )

                try:

                    resilience = ResilienceInput(
                        initial_liquidity=float(
                            resilience[
                                "initial_liquidity"
                            ]
                        ),
                        elapsed_seconds=float(
                            resilience[
                                "elapsed_seconds"
                            ]
                        ),
                        lambda_liq=float(
                            resilience[
                                "lambda_liq"
                            ]
                        ),
                        order_flow_injection=float(
                            resilience.get(
                                "order_flow_injection",
                                0.0,
                            )
                        ),
                    )

                except (
                    KeyError,
                    TypeError,
                    ValueError,
                ) as exc:

                    return self._invalid(
                        errors=[
                            f"Invalid resilience input: "
                            f"{exc}"
                        ]
                    )

        if "spread" not in data:

            return self._invalid(
                errors=[
                    "spread is required."
                ]
            )

        try:

            spread = float(
                data["spread"]
            )

        except (
            TypeError,
            ValueError,
        ):

            return self._invalid(
                errors=[
                    "spread must be numeric."
                ]
            )

        return self.calculate(
            LQSInputs(
                depths=tuple(depths),
                spread=spread,
                calibration=calibration,
                resilience=resilience,
                observed_at=data.get(
                    "observed_at"
                ),
            )
        )

    # ------------------------------------------------------------------
    # RESULT HELPERS
    # ------------------------------------------------------------------

    def _invalid(
        self,
        errors: Iterable[str],
        metadata: Optional[
            Mapping[str, Any]
        ] = None,
    ) -> LQSResult:

        return LQSResult(
            status=LQSStatus.INVALID,
            liquidity=None,
            raw_depth=None,
            depth_liquidity=None,
            spread=None,
            normalized_spread=None,
            spread_liquidity=None,
            resilience_liquidity=None,
            alpha=None,
            beta=None,
            gamma=None,
            depth_decay=None,
            lambda_liq=None,
            bid_depth=0.0,
            ask_depth=0.0,
            total_depth=0.0,
            depth_level_count=0,
            equation=self.EQUATION,
            equation_id=EQUATION_ID,
            errors=tuple(errors),
            warnings=(),
            metadata=(
                dict(metadata)
                if metadata is not None
                else {}
            ),
        )

    def _insufficient(
        self,
        reason: str,
    ) -> LQSResult:

        return LQSResult(
            status=LQSStatus.INSUFFICIENT,
            liquidity=None,
            raw_depth=None,
            depth_liquidity=None,
            spread=None,
            normalized_spread=None,
            spread_liquidity=None,
            resilience_liquidity=None,
            alpha=None,
            beta=None,
            gamma=None,
            depth_decay=None,
            lambda_liq=None,
            bid_depth=0.0,
            ask_depth=0.0,
            total_depth=0.0,
            depth_level_count=0,
            equation=self.EQUATION,
            equation_id=EQUATION_ID,
            errors=(),
            warnings=(reason,),
        )


# ---------------------------------------------------------------------------
# FUNCTIONAL API
# ---------------------------------------------------------------------------

def calculate_lqs(
    inputs: LQSInputs,
) -> LQSResult:
    """
    Calculate V6 EQ-0003 liquidity.
    """

    return LQSEngine().calculate(
        inputs
    )


# ---------------------------------------------------------------------------
# SELF TESTS
# ---------------------------------------------------------------------------

def _run_self_tests() -> None:

    # --------------------------------------------------------------
    # Explicit calibration.
    #
    # These values are TEST calibration only.
    # They are NOT production defaults.
    # --------------------------------------------------------------

    calibration = LQSCalibration(
        alpha=0.4,
        beta=0.3,
        gamma=0.3,
        depth_decay=0.1,
        lambda_liq=0.01,
        depth_reference=1000.0,
        spread_reference=1.0,
    )

    # --------------------------------------------------------------
    # TEST 1
    # Full valid calculation.
    # --------------------------------------------------------------

    result = calculate_lqs(
        LQSInputs(
            depths=[
                DepthObservation(
                    side=BookSide.BID,
                    level=1,
                    volume=500.0,
                    price=99.9,
                ),
                DepthObservation(
                    side=BookSide.BID,
                    level=2,
                    volume=300.0,
                    price=99.8,
                ),
                DepthObservation(
                    side=BookSide.ASK,
                    level=1,
                    volume=450.0,
                    price=100.1,
                ),
                DepthObservation(
                    side=BookSide.ASK,
                    level=2,
                    volume=250.0,
                    price=100.2,
                ),
            ],
            spread=0.2,
            calibration=calibration,
            resilience=ResilienceInput(
                initial_liquidity=0.5,
                elapsed_seconds=10.0,
                lambda_liq=0.01,
                order_flow_injection=0.1,
            ),
        )
    )

    assert result.status == LQSStatus.VALID
    assert result.liquidity is not None
    assert 0.0 <= result.liquidity <= 1.0

    # --------------------------------------------------------------
    # TEST 2
    # Depth weighting.
    #
    # Level 1 receives greater/equal weight than level 2 when
    # depth_decay > 0.
    # --------------------------------------------------------------

    w1 = exp(
        -calibration.depth_decay * 1
    )

    w2 = exp(
        -calibration.depth_decay * 2
    )

    assert w1 > w2

    # --------------------------------------------------------------
    # TEST 3
    # Spread = 0 -> L_spread = 1.
    # --------------------------------------------------------------

    result = calculate_lqs(
        LQSInputs(
            depths=[
                DepthObservation(
                    side=BookSide.BID,
                    level=1,
                    volume=500.0,
                ),
                DepthObservation(
                    side=BookSide.ASK,
                    level=1,
                    volume=500.0,
                ),
            ],
            spread=0.0,
            calibration=calibration,
            resilience=ResilienceInput(
                initial_liquidity=0.5,
                elapsed_seconds=0.0,
                lambda_liq=0.01,
                order_flow_injection=0.0,
            ),
        )
    )

    assert result.status == LQSStatus.VALID
    assert result.spread_liquidity == 1.0

    # --------------------------------------------------------------
    # TEST 4
    # Larger spread -> lower spread liquidity.
    # --------------------------------------------------------------

    narrow = calculate_lqs(
        LQSInputs(
            depths=[
                DepthObservation(
                    side=BookSide.BID,
                    level=1,
                    volume=500.0,
                ),
                DepthObservation(
                    side=BookSide.ASK,
                    level=1,
                    volume=500.0,
                ),
            ],
            spread=0.1,
            calibration=calibration,
            resilience=ResilienceInput(
                initial_liquidity=0.5,
                elapsed_seconds=1.0,
                lambda_liq=0.01,
            ),
        )
    )

    wide = calculate_lqs(
        LQSInputs(
            depths=[
                DepthObservation(
                    side=BookSide.BID,
                    level=1,
                    volume=500.0,
                ),
                DepthObservation(
                    side=BookSide.ASK,
                    level=1,
                    volume=500.0,
                ),
            ],
            spread=1.0,
            calibration=calibration,
            resilience=ResilienceInput(
                initial_liquidity=0.5,
                elapsed_seconds=1.0,
                lambda_liq=0.01,
            ),
        )
    )

    assert (
        narrow.spread_liquidity
        > wide.spread_liquidity
    )

    # --------------------------------------------------------------
    # TEST 5
    # Resilience decay without injection.
    # --------------------------------------------------------------

    early = calculate_lqs(
        LQSInputs(
            depths=[
                DepthObservation(
                    side=BookSide.BID,
                    level=1,
                    volume=500.0,
                ),
                DepthObservation(
                    side=BookSide.ASK,
                    level=1,
                    volume=500.0,
                ),
            ],
            spread=0.1,
            calibration=calibration,
            resilience=ResilienceInput(
                initial_liquidity=0.8,
                elapsed_seconds=0.0,
                lambda_liq=0.01,
            ),
        )
    )

    late = calculate_lqs(
        LQSInputs(
            depths=[
                DepthObservation(
                    side=BookSide.BID,
                    level=1,
                    volume=500.0,
                ),
                DepthObservation(
                    side=BookSide.ASK,
                    level=1,
                    volume=500.0,
                ),
            ],
            spread=0.1,
            calibration=calibration,
            resilience=ResilienceInput(
                initial_liquidity=0.8,
                elapsed_seconds=100.0,
                lambda_liq=0.01,
            ),
        )
    )

    assert (
        early.resilience_liquidity
        > late.resilience_liquidity
    )

    # --------------------------------------------------------------
    # TEST 6
    # Injection increases resilience.
    # --------------------------------------------------------------

    no_injection = calculate_lqs(
        LQSInputs(
            depths=[
                DepthObservation(
                    side=BookSide.BID,
                    level=1,
                    volume=500.0,
                ),
                DepthObservation(
                    side=BookSide.ASK,
                    level=1,
                    volume=500.0,
                ),
            ],
            spread=0.1,
            calibration=calibration,
            resilience=ResilienceInput(
                initial_liquidity=0.4,
                elapsed_seconds=10.0,
                lambda_liq=0.01,
                order_flow_injection=0.0,
            ),
        )
    )

    with_injection = calculate_lqs(
        LQSInputs(
            depths=[
                DepthObservation(
                    side=BookSide.BID,
                    level=1,
                    volume=500.0,
                ),
                DepthObservation(
                    side=BookSide.ASK,
                    level=1,
                    volume=500.0,
                ),
            ],
            spread=0.1,
            calibration=calibration,
            resilience=ResilienceInput(
                initial_liquidity=0.4,
                elapsed_seconds=10.0,
                lambda_liq=0.01,
                order_flow_injection=0.1,
            ),
        )
    )

    assert (
        with_injection.resilience_liquidity
        > no_injection.resilience_liquidity
    )

    # --------------------------------------------------------------
    # TEST 7
    # Missing resilience cannot produce a false complete score.
    # --------------------------------------------------------------

    result = calculate_lqs(
        LQSInputs(
            depths=[
                DepthObservation(
                    side=BookSide.BID,
                    level=1,
                    volume=500.0,
                ),
                DepthObservation(
                    side=BookSide.ASK,
                    level=1,
                    volume=500.0,
                ),
            ],
            spread=0.1,
            calibration=calibration,
            resilience=None,
        )
    )

    assert result.status == LQSStatus.PARTIAL
    assert result.liquidity is None
    assert result.resilience_liquidity is None

    # --------------------------------------------------------------
    # TEST 8
    # Negative spread rejected.
    # --------------------------------------------------------------

    try:

        LQSInputs(
            depths=[
                DepthObservation(
                    side=BookSide.BID,
                    level=1,
                    volume=500.0,
                ),
            ],
            spread=-1.0,
            calibration=calibration,
            resilience=ResilienceInput(
                initial_liquidity=0.5,
                elapsed_seconds=0.0,
                lambda_liq=0.01,
            ),
        )

        result = calculate_lqs(
            LQSInputs(
                depths=[
                    DepthObservation(
                        side=BookSide.BID,
                        level=1,
                        volume=500.0,
                    ),
                ],
                spread=-1.0,
                calibration=calibration,
                resilience=ResilienceInput(
                    initial_liquidity=0.5,
                    elapsed_seconds=0.0,
                    lambda_liq=0.01,
                ),
            )
        )

        assert result.status == LQSStatus.INVALID

    except AssertionError:
        raise

    # --------------------------------------------------------------
    # TEST 9
    # Calibration weights must sum to 1.
    # --------------------------------------------------------------

    failed = False

    try:

        LQSCalibration(
            alpha=0.5,
            beta=0.3,
            gamma=0.3,
            depth_decay=0.1,
            lambda_liq=0.01,
            depth_reference=1000.0,
            spread_reference=1.0,
        )

    except ValueError:
        failed = True

    assert failed

    # --------------------------------------------------------------
    # TEST 10
    # Negative depth rejected.
    # --------------------------------------------------------------

    failed = False

    try:

        DepthObservation(
            side=BookSide.BID,
            level=1,
            volume=-100.0,
        )

    except ValueError:
        failed = True

    assert failed

    # --------------------------------------------------------------
    # TEST 11
    # Invalid decay parameter rejected.
    # --------------------------------------------------------------

    failed = False

    try:

        LQSCalibration(
            alpha=0.4,
            beta=0.3,
            gamma=0.3,
            depth_decay=-0.1,
            lambda_liq=0.01,
            depth_reference=1000.0,
            spread_reference=1.0,
        )

    except ValueError:
        failed = True

    assert failed

    # --------------------------------------------------------------
    # TEST 12
    # No arbitrary 0..100 score.
    # --------------------------------------------------------------

    assert result.score is None

    # --------------------------------------------------------------
    # TEST 13
    # Official equation identity.
    # --------------------------------------------------------------

    assert result.equation_id == "EQ-0003"

    assert (
        "L_depth"
        in result.equation
    )

    assert (
        "L_spread"
        in result.equation
    )

    assert (
        "L_resilience"
        in result.equation
    )

    # --------------------------------------------------------------
    # TEST 14
    # Domain remains normalized.
    # --------------------------------------------------------------

    full = calculate_lqs(
        LQSInputs(
            depths=[
                DepthObservation(
                    side=BookSide.BID,
                    level=1,
                    volume=100.0,
                ),
                DepthObservation(
                    side=BookSide.ASK,
                    level=1,
                    volume=100.0,
                ),
            ],
            spread=0.1,
            calibration=calibration,
            resilience=ResilienceInput(
                initial_liquidity=0.2,
                elapsed_seconds=10.0,
                lambda_liq=0.01,
                order_flow_injection=0.05,
            ),
        )
    )

    assert full.status == LQSStatus.VALID
    assert (
        0.0
        <= full.liquidity
        <= 1.0
    )

    print("LQS V6 EQ-0003 self-tests: PASS")


# ---------------------------------------------------------------------------
# EXPORTS
# ---------------------------------------------------------------------------

__all__ = [
    "ENGINE_NAME",
    "ENGINE_VERSION",
    "EQUATION_ID",
    "LQSStatus",
    "BookSide",
    "DepthObservation",
    "ResilienceInput",
    "LQSCalibration",
    "LQSInputs",
    "LQSResult",
    "LQSEngine",
    "calculate_lqs",
]


if __name__ == "__main__":
    _run_self_tests()
