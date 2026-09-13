"""
ROBOMLM_PLUS
MTS â€” Market Trend Score / Trend State Engine
V6 Mathematical Implementation

FOUNDATION
----------
ROBOMLM V6 Equation-0001:

    dP = Î¼(P,T) dt + Ïƒ(P,T) dW

where:

    Î¼ = drift / expected price movement per unit time
    Ïƒ = volatility / diffusion coefficient

MTS uses the established V6 mathematical primitives:

    1. Price movement
    2. Time
    3. Drift (Î¼)
    4. Volatility (Ïƒ)

The principal trend-strength quantity is:

    Z_trend = Î¼ / Ïƒ

when Ïƒ > 0 and both quantities use compatible time units.

Interpretation:

    Z_trend > 0  -> bullish pressure
    Z_trend < 0  -> bearish pressure
    Z_trend = 0  -> neutral

IMPORTANT
---------
The stored V6 research identifies MTS as a core intelligence indicator,
but does not expose a verified final 0..100 MTS normalization equation.

Therefore this implementation deliberately does NOT invent one.

It exposes:
    - raw price drift
    - realized volatility
    - drift/volatility ratio
    - price return
    - direction
    - mathematical validity

A future V6 calibration/normalization specification can consume
these quantities without changing the underlying mathematics.

NO:
    - arbitrary weights
    - arbitrary thresholds
    - fake confidence
    - default values
    - guessed volatility
    - BUY/SELL
    - execution authority
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from math import isfinite, sqrt, log
from typing import Any, Iterable, Mapping, Optional, Sequence


ENGINE_NAME = "MTS"
ENGINE_VERSION = "V6"
EQUATION_ID = "EQ-0001"

MIN_PRICE = 0.0


# ---------------------------------------------------------------------------
# ENUMS
# ---------------------------------------------------------------------------

class MTSStatus(str, Enum):
    VALID = "VALID"
    INSUFFICIENT = "INSUFFICIENT"
    INVALID = "INVALID"


class TrendDirection(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


class VolatilityState(str, Enum):
    POSITIVE = "POSITIVE"
    ZERO = "ZERO"
    UNDEFINED = "UNDEFINED"


# ---------------------------------------------------------------------------
# INPUT
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MTSObservation:
    """
    Timestamped positive price observation.

    Price is the primitive used by EQ-0001.

    Volume is accepted only as preserved metadata. It is deliberately
    not inserted into MTS because no verified V6 MTS volume weighting
    was recovered.
    """

    price: float
    timestamp: datetime
    volume: Optional[float] = None
    metadata: Mapping[str, Any] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            object.__setattr__(
                self,
                "metadata",
                {},
            )


# ---------------------------------------------------------------------------
# RESULT
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MTSResult:
    """
    Complete MTS mathematical result.

    drift:
        Î¼_hat = Î”P / Î”t

    realized_volatility:
        Standard deviation of interval log returns divided by
        sqrt(interval duration).

    trend_ratio:
        Î¼_log / Ïƒ_log

    This is a dimensionless trend-to-volatility measure.
    """

    status: MTSStatus

    direction: Optional[TrendDirection]

    volatility_state: VolatilityState

    price_start: Optional[float]
    price_end: Optional[float]

    elapsed_seconds: Optional[float]
    observation_count: int

    price_change: Optional[float]
    price_return: Optional[float]
    price_return_pct: Optional[float]

    drift: Optional[float]
    drift_unit: Optional[str]

    mean_log_return: Optional[float]
    realized_volatility: Optional[float]
    volatility_unit: Optional[str]

    trend_ratio: Optional[float]

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
        return self.status == MTSStatus.VALID

    @property
    def score(self) -> Optional[float]:
        """
        Compatibility property.

        No fabricated 0..100 score is returned.

        The exact V6 customer-facing MTS normalization was not
        recovered, therefore this remains None.
        """

        return None

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "direction": (
                self.direction.value
                if self.direction is not None
                else None
            ),
            "volatility_state": self.volatility_state.value,
            "price_start": self.price_start,
            "price_end": self.price_end,
            "elapsed_seconds": self.elapsed_seconds,
            "observation_count": self.observation_count,
            "price_change": self.price_change,
            "price_return": self.price_return,
            "price_return_pct": self.price_return_pct,
            "drift": self.drift,
            "drift_unit": self.drift_unit,
            "mean_log_return": self.mean_log_return,
            "realized_volatility": self.realized_volatility,
            "volatility_unit": self.volatility_unit,
            "trend_ratio": self.trend_ratio,
            "score": self.score,
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

class MTSEngine:
    """
    V6 Market Trend Engine.

    Mathematical foundation:

        dP = Î¼(P,T)dt + Ïƒ(P,T)dW

    Finite interval drift:

        Î¼_hat = Î”P / Î”t

    Log return:

        r_t = ln(P_t / P_(t-1))

    Mean log-return rate:

        Î¼_log = mean(r_t) / mean(Î”t)

    Realized volatility:

        Ïƒ_log =
            std(r_t) / sqrt(mean(Î”t))

    Trend-to-volatility ratio:

        Z_trend = Î¼_log / Ïƒ_log

    No arbitrary normalization is applied.
    """

    EQUATION = (
        "dP = Î¼(P,T)dt + Ïƒ(P,T)dW"
    )

    DRIFT_EQUATION = (
        "Î¼_hat = (P_end - P_start) / Î”t"
    )

    LOG_RETURN_EQUATION = (
        "r_t = ln(P_t / P_(t-1))"
    )

    VOLATILITY_EQUATION = (
        "Ïƒ_log = std(r_t) / sqrt(Î”t)"
    )

    TREND_RATIO_EQUATION = (
        "Z_trend = Î¼_log / Ïƒ_log"
    )

    # ------------------------------------------------------------------
    # PUBLIC CALCULATION
    # ------------------------------------------------------------------

    def calculate(
        self,
        observations: Sequence[MTSObservation],
    ) -> MTSResult:

        errors: list[str] = []
        warnings: list[str] = []

        if observations is None:
            return self._insufficient(
                count=0,
                reason="No market observations supplied.",
            )

        observations = tuple(observations)

        if len(observations) < 2:
            return self._insufficient(
                count=len(observations),
                reason=(
                    "At least two timestamped price observations "
                    "are required."
                ),
            )

        # --------------------------------------------------------------
        # VALIDATE OBSERVATIONS
        # --------------------------------------------------------------

        for index, obs in enumerate(observations):

            if not isinstance(obs.timestamp, datetime):
                errors.append(
                    f"observation[{index}]: timestamp must be datetime"
                )

            if isinstance(obs.price, bool):
                errors.append(
                    f"observation[{index}]: boolean price is invalid"
                )
                continue

            if not isinstance(obs.price, (int, float)):
                errors.append(
                    f"observation[{index}]: price must be numeric"
                )
                continue

            price = float(obs.price)

            if not isfinite(price):
                errors.append(
                    f"observation[{index}]: price must be finite"
                )
            elif price <= MIN_PRICE:
                errors.append(
                    f"observation[{index}]: price must be > 0"
                )

            if obs.volume is not None:

                if isinstance(obs.volume, bool):
                    errors.append(
                        f"observation[{index}]: volume cannot be boolean"
                    )

                elif not isinstance(
                    obs.volume,
                    (int, float),
                ):
                    errors.append(
                        f"observation[{index}]: volume must be numeric"
                    )

                elif not isfinite(float(obs.volume)):
                    errors.append(
                        f"observation[{index}]: volume must be finite"
                    )

                elif float(obs.volume) < 0:
                    errors.append(
                        f"observation[{index}]: volume cannot be negative"
                    )

        if errors:
            return self._invalid(
                count=len(observations),
                errors=errors,
            )

        # --------------------------------------------------------------
        # CHRONOLOGY
        # --------------------------------------------------------------

        interval_seconds: list[float] = []

        for index in range(1, len(observations)):

            dt = (
                observations[index].timestamp
                - observations[index - 1].timestamp
            ).total_seconds()

            if dt <= 0:
                errors.append(
                    "Observation timestamps must be strictly "
                    "increasing."
                )
            else:
                interval_seconds.append(dt)

        if errors:
            return self._invalid(
                count=len(observations),
                errors=errors,
            )

        # --------------------------------------------------------------
        # PRICES
        # --------------------------------------------------------------

        prices = [
            float(obs.price)
            for obs in observations
        ]

        price_start = prices[0]
        price_end = prices[-1]

        elapsed_seconds = (
            observations[-1].timestamp
            - observations[0].timestamp
        ).total_seconds()

        if elapsed_seconds <= 0:
            return self._invalid(
                count=len(observations),
                errors=[
                    "Total elapsed time must be > 0."
                ],
            )

        # --------------------------------------------------------------
        # NET PRICE MOVEMENT
        # --------------------------------------------------------------

        price_change = (
            price_end
            - price_start
        )

        price_return = (
            price_end / price_start
        ) - 1.0

        price_return_pct = (
            price_return * 100.0
        )

        # --------------------------------------------------------------
        # EQ-0001 FINITE-INTERVAL DRIFT
        #
        # Î¼_hat = Î”P / Î”t
        # --------------------------------------------------------------

        drift = (
            price_change
            / elapsed_seconds
        )

        if drift > 0:
            direction = TrendDirection.BULLISH

        elif drift < 0:
            direction = TrendDirection.BEARISH

        else:
            direction = TrendDirection.NEUTRAL

        # --------------------------------------------------------------
        # INTERVAL LOG RETURNS
        # --------------------------------------------------------------

        log_returns: list[float] = []

        for index in range(1, len(prices)):

            current = prices[index]
            previous = prices[index - 1]

            value = log(
                current / previous
            )

            if not isfinite(value):
                return self._invalid(
                    count=len(observations),
                    errors=[
                        "Non-finite log return encountered."
                    ],
                )

            log_returns.append(value)

        # --------------------------------------------------------------
        # MEAN LOG RETURN
        # --------------------------------------------------------------

        mean_log_return = (
            sum(log_returns)
            / len(log_returns)
        )

        # --------------------------------------------------------------
        # TIME-ADJUSTED LOG DRIFT
        #
        # For unequal intervals we use total log return / total time.
        # This preserves dimensional correctness.
        # --------------------------------------------------------------

        total_log_return = sum(
            log_returns
        )

        mean_log_drift = (
            total_log_return
            / elapsed_seconds
        )

        # --------------------------------------------------------------
        # REALIZED VOLATILITY
        #
        # Use time-normalized returns.
        #
        # If only two observations exist, volatility cannot be estimated
        # as a sample standard deviation from a return series with
        # degrees of freedom = 1.
        #
        # Therefore:
        #     Ïƒ = 0
        #
        # is NOT assumed.
        #
        # Instead, trend-ratio remains unavailable.
        # --------------------------------------------------------------

        if len(log_returns) < 2:

            realized_volatility = None
            volatility_state = VolatilityState.UNDEFINED

            warnings.append(
                "Only one return interval is available; "
                "realized volatility cannot be estimated."
            )

            trend_ratio = None

        else:

            mean_interval = (
                elapsed_seconds
                / len(log_returns)
            )

            variance_sum = sum(
                (
                    value - mean_log_return
                ) ** 2
                for value in log_returns
            )

            sample_variance = (
                variance_sum
                / (len(log_returns) - 1)
            )

            if sample_variance < 0:
                return self._invalid(
                    count=len(observations),
                    errors=[
                        "Calculated volatility variance "
                        "became negative."
                    ],
                )

            realized_volatility = (
                sqrt(sample_variance)
                / sqrt(mean_interval)
            )

            if not isfinite(
                realized_volatility
            ):
                return self._invalid(
                    count=len(observations),
                    errors=[
                        "Realized volatility is non-finite."
                    ],
                )

            if realized_volatility > 0:

                volatility_state = (
                    VolatilityState.POSITIVE
                )

                trend_ratio = (
                    mean_log_drift
                    / realized_volatility
                )

            else:

                volatility_state = (
                    VolatilityState.ZERO
                )

                # Zero volatility does not imply an infinite score.
                # The ratio is mathematically undefined.
                trend_ratio = None

                warnings.append(
                    "Realized volatility is zero; "
                    "trend/volatility ratio is undefined."
                )

        # --------------------------------------------------------------
        # FINAL VALID RESULT
        # --------------------------------------------------------------

        return MTSResult(
            status=MTSStatus.VALID,
            direction=direction,
            volatility_state=volatility_state,
            price_start=price_start,
            price_end=price_end,
            elapsed_seconds=elapsed_seconds,
            observation_count=len(observations),
            price_change=price_change,
            price_return=price_return,
            price_return_pct=price_return_pct,
            drift=drift,
            drift_unit="price_units_per_second",
            mean_log_return=mean_log_return,
            realized_volatility=realized_volatility,
            volatility_unit="log_return_per_sqrt_second",
            trend_ratio=trend_ratio,
            equation=self.EQUATION,
            equation_id=EQUATION_ID,
            errors=(),
            warnings=tuple(warnings),
            metadata={
                "drift_equation": self.DRIFT_EQUATION,
                "log_return_equation": self.LOG_RETURN_EQUATION,
                "volatility_equation": self.VOLATILITY_EQUATION,
                "trend_ratio_equation": self.TREND_RATIO_EQUATION,
                "score_normalization": "NOT_APPLIED",
                "customer_score": None,
                "v6_normalization_recovery": "PENDING",
            },
        )

    # ------------------------------------------------------------------
    # MAPPING API
    # ------------------------------------------------------------------

    def calculate_from_mapping(
        self,
        observations: Iterable[Mapping[str, Any]],
    ) -> MTSResult:

        converted: list[MTSObservation] = []
        errors: list[str] = []

        for index, item in enumerate(observations):

            if not isinstance(item, Mapping):
                errors.append(
                    f"observation[{index}]: expected mapping"
                )
                continue

            price = self._first_present(
                item,
                "price",
                "close",
                "last_price",
                "ltp",
            )

            timestamp = self._first_present(
                item,
                "timestamp",
                "time",
                "observed_at",
                "datetime",
            )

            volume = self._first_present(
                item,
                "volume",
            )

            metadata = item.get(
                "metadata",
                {},
            )

            if price is None:
                errors.append(
                    f"observation[{index}]: price missing"
                )
                continue

            if timestamp is None:
                errors.append(
                    f"observation[{index}]: timestamp missing"
                )
                continue

            if not isinstance(
                timestamp,
                datetime,
            ):
                errors.append(
                    f"observation[{index}]: "
                    "timestamp must be datetime"
                )
                continue

            converted.append(
                MTSObservation(
                    price=price,
                    timestamp=timestamp,
                    volume=volume,
                    metadata=(
                        metadata
                        if isinstance(
                            metadata,
                            Mapping,
                        )
                        else {}
                    ),
                )
            )

        if errors:
            return self._invalid(
                count=len(converted),
                errors=errors,
            )

        return self.calculate(converted)

    # ------------------------------------------------------------------
    # INTERNAL RESULT BUILDERS
    # ------------------------------------------------------------------

    def _invalid(
        self,
        count: int,
        errors: Iterable[str],
    ) -> MTSResult:

        return MTSResult(
            status=MTSStatus.INVALID,
            direction=None,
            volatility_state=VolatilityState.UNDEFINED,
            price_start=None,
            price_end=None,
            elapsed_seconds=None,
            observation_count=count,
            price_change=None,
            price_return=None,
            price_return_pct=None,
            drift=None,
            drift_unit=None,
            mean_log_return=None,
            realized_volatility=None,
            volatility_unit=None,
            trend_ratio=None,
            equation=self.EQUATION,
            equation_id=EQUATION_ID,
            errors=tuple(errors),
            warnings=(),
        )

    def _insufficient(
        self,
        count: int,
        reason: str,
    ) -> MTSResult:

        return MTSResult(
            status=MTSStatus.INSUFFICIENT,
            direction=None,
            volatility_state=VolatilityState.UNDEFINED,
            price_start=None,
            price_end=None,
            elapsed_seconds=None,
            observation_count=count,
            price_change=None,
            price_return=None,
            price_return_pct=None,
            drift=None,
            drift_unit=None,
            mean_log_return=None,
            realized_volatility=None,
            volatility_unit=None,
            trend_ratio=None,
            equation=self.EQUATION,
            equation_id=EQUATION_ID,
            errors=(),
            warnings=(reason,),
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


# ---------------------------------------------------------------------------
# FUNCTIONAL API
# ---------------------------------------------------------------------------

def calculate_mts(
    observations: Sequence[MTSObservation],
) -> MTSResult:
    """
    Functional MTS API.
    """

    return MTSEngine().calculate(
        observations
    )


# ---------------------------------------------------------------------------
# SELF TESTS
# ---------------------------------------------------------------------------

def _run_self_tests() -> None:

    from datetime import timedelta

    start = datetime(
        2026,
        1,
        1,
        9,
        0,
        0,
    )

    # --------------------------------------------------------------
    # TEST 1
    # Rising market -> bullish drift.
    # --------------------------------------------------------------

    result = calculate_mts(
        [
            MTSObservation(
                price=100.0,
                timestamp=start,
            ),
            MTSObservation(
                price=102.0,
                timestamp=start + timedelta(seconds=10),
            ),
            MTSObservation(
                price=104.0,
                timestamp=start + timedelta(seconds=20),
            ),
        ]
    )

    assert result.status == MTSStatus.VALID
    assert result.direction == TrendDirection.BULLISH
    assert result.drift > 0
    assert result.price_change == 4.0

    # --------------------------------------------------------------
    # TEST 2
    # Falling market -> bearish drift.
    # --------------------------------------------------------------

    result = calculate_mts(
        [
            MTSObservation(
                price=104.0,
                timestamp=start,
            ),
            MTSObservation(
                price=102.0,
                timestamp=start + timedelta(seconds=10),
            ),
            MTSObservation(
                price=100.0,
                timestamp=start + timedelta(seconds=20),
            ),
        ]
    )

    assert result.status == MTSStatus.VALID
    assert result.direction == TrendDirection.BEARISH
    assert result.drift < 0

    # --------------------------------------------------------------
    # TEST 3
    # Flat market -> neutral.
    # --------------------------------------------------------------

    result = calculate_mts(
        [
            MTSObservation(
                price=100.0,
                timestamp=start,
            ),
            MTSObservation(
                price=100.0,
                timestamp=start + timedelta(seconds=10),
            ),
            MTSObservation(
                price=100.0,
                timestamp=start + timedelta(seconds=20),
            ),
        ]
    )

    assert result.status == MTSStatus.VALID
    assert result.direction == TrendDirection.NEUTRAL
    assert result.drift == 0.0

    # --------------------------------------------------------------
    # TEST 4
    # Two observations:
    # drift can be calculated, volatility cannot.
    # --------------------------------------------------------------

    result = calculate_mts(
        [
            MTSObservation(
                price=100.0,
                timestamp=start,
            ),
            MTSObservation(
                price=110.0,
                timestamp=start + timedelta(seconds=10),
            ),
        ]
    )

    assert result.status == MTSStatus.VALID
    assert result.drift == 1.0
    assert result.realized_volatility is None
    assert result.trend_ratio is None

    # --------------------------------------------------------------
    # TEST 5
    # Multiple returns with changing prices -> volatility exists.
    # --------------------------------------------------------------

    result = calculate_mts(
        [
            MTSObservation(
                price=100.0,
                timestamp=start,
            ),
            MTSObservation(
                price=102.0,
                timestamp=start + timedelta(seconds=10),
            ),
            MTSObservation(
                price=101.0,
                timestamp=start + timedelta(seconds=20),
            ),
            MTSObservation(
                price=104.0,
                timestamp=start + timedelta(seconds=30),
            ),
        ]
    )

    assert result.status == MTSStatus.VALID
    assert result.realized_volatility is not None
    assert result.realized_volatility > 0
    assert result.trend_ratio is not None

    # --------------------------------------------------------------
    # TEST 6
    # Positive trend ratio means positive drift relative to volatility.
    # --------------------------------------------------------------

    assert result.trend_ratio is not None

    if result.drift > 0:
        assert result.trend_ratio > 0

    # --------------------------------------------------------------
    # TEST 7
    # Missing data must stop.
    # --------------------------------------------------------------

    result = calculate_mts([])

    assert result.status == MTSStatus.INSUFFICIENT
    assert result.drift is None

    # --------------------------------------------------------------
    # TEST 8
    # Negative price rejected.
    # --------------------------------------------------------------

    result = calculate_mts(
        [
            MTSObservation(
                price=-100.0,
                timestamp=start,
            ),
            MTSObservation(
                price=101.0,
                timestamp=start + timedelta(seconds=10),
            ),
        ]
    )

    assert result.status == MTSStatus.INVALID

    # --------------------------------------------------------------
    # TEST 9
    # Zero elapsed time rejected.
    # --------------------------------------------------------------

    result = calculate_mts(
        [
            MTSObservation(
                price=100.0,
                timestamp=start,
            ),
            MTSObservation(
                price=101.0,
                timestamp=start,
            ),
        ]
    )

    assert result.status == MTSStatus.INVALID

    # --------------------------------------------------------------
    # TEST 10
    # Out-of-order timestamps rejected.
    # --------------------------------------------------------------

    result = calculate_mts(
        [
            MTSObservation(
                price=101.0,
                timestamp=start + timedelta(seconds=10),
            ),
            MTSObservation(
                price=100.0,
                timestamp=start,
            ),
        ]
    )

    assert result.status == MTSStatus.INVALID

    # --------------------------------------------------------------
    # TEST 11
    # Score must NOT be fabricated.
    # --------------------------------------------------------------

    assert result.score is None

    # --------------------------------------------------------------
    # TEST 12
    # Exact return calculation.
    # --------------------------------------------------------------

    result = calculate_mts(
        [
            MTSObservation(
                price=100.0,
                timestamp=start,
            ),
            MTSObservation(
                price=110.0,
                timestamp=start + timedelta(seconds=10),
            ),
            MTSObservation(
                price=121.0,
                timestamp=start + timedelta(seconds=20),
            ),
        ]
    )

    expected_return = 0.21

    assert abs(
        result.price_return - expected_return
    ) < 1e-12

    # --------------------------------------------------------------
    # TEST 13
    # Equation identity preserved.
    # --------------------------------------------------------------

    assert result.equation_id == "EQ-0001"
    assert "Î¼" in result.equation
    assert "Ïƒ" in result.equation

    # --------------------------------------------------------------
    # TEST 14
    # No hidden normalization.
    # --------------------------------------------------------------

    assert (
        result.metadata["score_normalization"]
        == "NOT_APPLIED"
    )

    assert (
        result.metadata["customer_score"]
        is None
    )

    print("MTS V6 self-tests: PASS")


# ---------------------------------------------------------------------------
# EXPORTS
# ---------------------------------------------------------------------------

__all__ = [
    "ENGINE_NAME",
    "ENGINE_VERSION",
    "EQUATION_ID",
    "MTSStatus",
    "TrendDirection",
    "VolatilityState",
    "MTSObservation",
    "MTSResult",
    "MTSEngine",
    "calculate_mts",
]


if __name__ == "__main__":
    _run_self_tests()
