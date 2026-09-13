"""
ROBOMLM_PLUS
TPS â€” Trend Pressure Engine
V6 Mathematical Foundation

Foundation:
    EQ-0001 Price Motion

        dP = Î¼(P,T)dt + Ïƒ(P,T)dW

V6 defines:
    Î¼ = Drift = expected price change per unit time

TPS therefore measures the directional pressure contained in
the observed price path through estimated drift.

IMPORTANT:
    This module does NOT invent a 0..100 score.
    It calculates the mathematically observable trend-pressure
    quantities first.

    No:
        - arbitrary weights
        - arbitrary thresholds
        - fake confidence
        - default score
        - guessed missing values
        - BUY/SELL decision
        - execution authority

The 0..100 customer-facing TPS normalization must only be added
when its V6 normalization/calibration specification is recovered.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from math import isfinite, log
from typing import Any, Iterable, Mapping, Optional, Sequence


ENGINE_NAME = "TPS"
ENGINE_VERSION = "V6"

EQ_ID = "EQ-0001"


class TPSStatus(str, Enum):
    VALID = "VALID"
    INSUFFICIENT = "INSUFFICIENT"
    INVALID = "INVALID"


class TrendDirection(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


@dataclass(frozen=True)
class PriceObservation:
    """
    One timestamped price observation.

    price:
        Positive market price.

    timestamp:
        Observation time.

    volume:
        Optional observed volume. It is preserved but is NOT
        silently incorporated into TPS because V6 does not define
        a TPS volume weighting here.
    """

    price: float
    timestamp: datetime
    volume: Optional[float] = None
    metadata: Mapping[str, Any] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            object.__setattr__(self, "metadata", {})


@dataclass(frozen=True)
class TPSResult:
    """
    Complete V6 trend-pressure calculation.

    Core quantities:

        Î”P
        Î”t
        arithmetic velocity = Î”P / Î”t
        log return
        log-return rate
        drift estimate Î¼

    Î¼ is the principal V6 trend quantity.
    """

    status: TPSStatus

    direction: Optional[TrendDirection]

    price_start: Optional[float]
    price_end: Optional[float]

    elapsed_seconds: Optional[float]

    price_change: Optional[float]
    price_change_pct: Optional[float]

    log_return: Optional[float]
    log_return_rate: Optional[float]

    drift: Optional[float]
    drift_unit: Optional[str]

    observation_count: int

    equation: str
    equation_id: str

    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    engine: str = ENGINE_NAME
    version: str = ENGINE_VERSION

    metadata: Mapping[str, Any] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            object.__setattr__(self, "metadata", {})

    @property
    def is_valid(self) -> bool:
        return self.status == TPSStatus.VALID

    @property
    def is_directional(self) -> bool:
        return (
            self.direction is not None
            and self.direction != TrendDirection.NEUTRAL
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "direction": (
                self.direction.value
                if self.direction is not None
                else None
            ),
            "price_start": self.price_start,
            "price_end": self.price_end,
            "elapsed_seconds": self.elapsed_seconds,
            "price_change": self.price_change,
            "price_change_pct": self.price_change_pct,
            "log_return": self.log_return,
            "log_return_rate": self.log_return_rate,
            "drift": self.drift,
            "drift_unit": self.drift_unit,
            "observation_count": self.observation_count,
            "equation": self.equation,
            "equation_id": self.equation_id,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "engine": self.engine,
            "version": self.version,
            "metadata": dict(self.metadata),
        }


class TPSEngine:
    """
    V6 Trend Pressure Engine.

    Mathematical foundation:

        EQ-0001:
            dP = Î¼(P,T)dt + Ïƒ(P,T)dW

    Observed finite-interval drift estimate:

        Î¼Ì‚ = Î”P / Î”t

    Because price is strictly positive, the engine additionally
    calculates the dimensionless log-return rate:

        r = ln(P_t / P_0)

        Î¼_log = r / Î”t

    Both are retained.

    The engine deliberately does not convert Î¼ into an arbitrary
    0..100 score.
    """

    EQUATION = (
        "dP = Î¼(P,T)dt + Ïƒ(P,T)dW"
    )

    DRIFT_EQUATION = (
        "Î¼_hat = (P_end - P_start) / Î”t"
    )

    LOG_DRIFT_EQUATION = (
        "Î¼_log = ln(P_end / P_start) / Î”t"
    )

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def calculate(
        self,
        observations: Sequence[PriceObservation],
    ) -> TPSResult:
        """
        Calculate trend pressure from timestamped prices.

        Requirements:
            - at least two observations
            - strictly positive prices
            - finite numeric values
            - valid timestamps
            - strictly increasing time
        """

        errors: list[str] = []
        warnings: list[str] = []

        if observations is None:
            return self._insufficient(
                count=0,
                reason="No price observations supplied.",
            )

        observations = tuple(observations)

        if len(observations) < 2:
            return self._insufficient(
                count=len(observations),
                reason=(
                    "At least two timestamped price observations "
                    "are required to estimate trend pressure."
                ),
            )

        # --------------------------------------------------------------
        # Validate observations
        # --------------------------------------------------------------

        for index, observation in enumerate(observations):

            if not isinstance(observation.timestamp, datetime):
                errors.append(
                    f"observation[{index}]: timestamp must be datetime"
                )

            if isinstance(observation.price, bool):
                errors.append(
                    f"observation[{index}]: boolean price is invalid"
                )
                continue

            if not isinstance(observation.price, (int, float)):
                errors.append(
                    f"observation[{index}]: price must be numeric"
                )
                continue

            price = float(observation.price)

            if not isfinite(price):
                errors.append(
                    f"observation[{index}]: price must be finite"
                )
            elif price <= 0:
                errors.append(
                    f"observation[{index}]: price must be > 0"
                )

            if observation.volume is not None:

                if isinstance(observation.volume, bool):
                    errors.append(
                        f"observation[{index}]: volume cannot be boolean"
                    )

                elif not isinstance(
                    observation.volume,
                    (int, float),
                ):
                    errors.append(
                        f"observation[{index}]: volume must be numeric"
                    )

                elif not isfinite(float(observation.volume)):
                    errors.append(
                        f"observation[{index}]: volume must be finite"
                    )

                elif float(observation.volume) < 0:
                    errors.append(
                        f"observation[{index}]: volume cannot be negative"
                    )

        if errors:
            return TPSResult(
                status=TPSStatus.INVALID,
                direction=None,
                price_start=None,
                price_end=None,
                elapsed_seconds=None,
                price_change=None,
                price_change_pct=None,
                log_return=None,
                log_return_rate=None,
                drift=None,
                drift_unit=None,
                observation_count=len(observations),
                equation=self.EQUATION,
                equation_id=EQ_ID,
                errors=tuple(errors),
                warnings=tuple(warnings),
            )

        # --------------------------------------------------------------
        # Validate chronological ordering
        # --------------------------------------------------------------

        for index in range(1, len(observations)):

            previous_time = observations[index - 1].timestamp
            current_time = observations[index].timestamp

            elapsed = (
                current_time - previous_time
            ).total_seconds()

            if elapsed <= 0:
                errors.append(
                    "Observations must be strictly chronological; "
                    f"observation[{index - 1}] and "
                    f"observation[{index}] have non-positive "
                    "elapsed time."
                )

        if errors:
            return TPSResult(
                status=TPSStatus.INVALID,
                direction=None,
                price_start=None,
                price_end=None,
                elapsed_seconds=None,
                price_change=None,
                price_change_pct=None,
                log_return=None,
                log_return_rate=None,
                drift=None,
                drift_unit=None,
                observation_count=len(observations),
                equation=self.EQUATION,
                equation_id=EQ_ID,
                errors=tuple(errors),
                warnings=tuple(warnings),
            )

        # --------------------------------------------------------------
        # Use complete observed interval
        # --------------------------------------------------------------

        first = observations[0]
        last = observations[-1]

        price_start = float(first.price)
        price_end = float(last.price)

        elapsed_seconds = (
            last.timestamp - first.timestamp
        ).total_seconds()

        if elapsed_seconds <= 0:
            return TPSResult(
                status=TPSStatus.INVALID,
                direction=None,
                price_start=price_start,
                price_end=price_end,
                elapsed_seconds=elapsed_seconds,
                price_change=None,
                price_change_pct=None,
                log_return=None,
                log_return_rate=None,
                drift=None,
                drift_unit=None,
                observation_count=len(observations),
                equation=self.EQUATION,
                equation_id=EQ_ID,
                errors=(
                    "Total elapsed time must be strictly positive.",
                ),
                warnings=(),
            )

        # --------------------------------------------------------------
        # Price change
        # --------------------------------------------------------------

        price_change = price_end - price_start

        price_change_pct = (
            price_change / price_start
        ) * 100.0

        # --------------------------------------------------------------
        # Log return
        #
        # Price > 0 has already been validated.
        # --------------------------------------------------------------

        log_return = log(
            price_end / price_start
        )

        log_return_rate = (
            log_return / elapsed_seconds
        )

        # --------------------------------------------------------------
        # EQ-0001 finite-interval drift estimate
        #
        # Î¼_hat = Î”P / Î”t
        # --------------------------------------------------------------

        drift = (
            price_change / elapsed_seconds
        )

        if drift > 0:
            direction = TrendDirection.BULLISH
        elif drift < 0:
            direction = TrendDirection.BEARISH
        else:
            direction = TrendDirection.NEUTRAL

        # --------------------------------------------------------------
        # Detect intermediate path reversals.
        #
        # This is diagnostic information only.
        # It does not alter drift.
        # --------------------------------------------------------------

        path_directions: list[int] = []

        for index in range(1, len(observations)):
            delta = (
                float(observations[index].price)
                - float(observations[index - 1].price)
            )

            if delta > 0:
                path_directions.append(1)
            elif delta < 0:
                path_directions.append(-1)
            else:
                path_directions.append(0)

        sign_changes = 0

        previous_nonzero: Optional[int] = None

        for value in path_directions:

            if value == 0:
                continue

            if (
                previous_nonzero is not None
                and value != previous_nonzero
            ):
                sign_changes += 1

            previous_nonzero = value

        if sign_changes > 0:
            warnings.append(
                "Observed path contains directional reversals; "
                "net drift remains calculated from the complete "
                "observation interval."
            )

        return TPSResult(
            status=TPSStatus.VALID,
            direction=direction,
            price_start=price_start,
            price_end=price_end,
            elapsed_seconds=elapsed_seconds,
            price_change=price_change,
            price_change_pct=price_change_pct,
            log_return=log_return,
            log_return_rate=log_return_rate,
            drift=drift,
            drift_unit="price_units_per_second",
            observation_count=len(observations),
            equation=self.EQUATION,
            equation_id=EQ_ID,
            errors=(),
            warnings=tuple(warnings),
            metadata={
                "drift_equation": self.DRIFT_EQUATION,
                "log_drift_equation": self.LOG_DRIFT_EQUATION,
                "sign_changes": sign_changes,
                "path_direction_count": len(path_directions),
                "normalization": "NOT_APPLIED",
                "score_scale": "RAW",
            },
        )

    # ------------------------------------------------------------------
    # Convenience: raw mappings
    # ------------------------------------------------------------------

    def calculate_from_mapping(
        self,
        observations: Iterable[Mapping[str, Any]],
    ) -> TPSResult:
        """
        Accepts mappings with common semantic field names.

        Required:
            price
            timestamp

        Optional:
            volume
            metadata
        """

        converted: list[PriceObservation] = []
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

            if not isinstance(timestamp, datetime):
                errors.append(
                    f"observation[{index}]: timestamp must be datetime"
                )
                continue

            converted.append(
                PriceObservation(
                    price=price,
                    timestamp=timestamp,
                    volume=volume,
                    metadata=(
                        metadata
                        if isinstance(metadata, Mapping)
                        else {}
                    ),
                )
            )

        if errors:
            return TPSResult(
                status=TPSStatus.INVALID,
                direction=None,
                price_start=None,
                price_end=None,
                elapsed_seconds=None,
                price_change=None,
                price_change_pct=None,
                log_return=None,
                log_return_rate=None,
                drift=None,
                drift_unit=None,
                observation_count=len(converted),
                equation=self.EQUATION,
                equation_id=EQ_ID,
                errors=tuple(errors),
                warnings=(),
            )

        return self.calculate(converted)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _first_present(
        data: Mapping[str, Any],
        *names: str,
    ) -> Any:

        for name in names:
            if name in data:
                return data[name]

        return None

    def _insufficient(
        self,
        count: int,
        reason: str,
    ) -> TPSResult:

        return TPSResult(
            status=TPSStatus.INSUFFICIENT,
            direction=None,
            price_start=None,
            price_end=None,
            elapsed_seconds=None,
            price_change=None,
            price_change_pct=None,
            log_return=None,
            log_return_rate=None,
            drift=None,
            drift_unit=None,
            observation_count=count,
            equation=self.EQUATION,
            equation_id=EQ_ID,
            errors=(),
            warnings=(reason,),
        )


# ---------------------------------------------------------------------------
# FUNCTIONAL API
# ---------------------------------------------------------------------------

def calculate_tps(
    observations: Sequence[PriceObservation],
) -> TPSResult:
    """
    Calculate V6 raw trend pressure.
    """

    return TPSEngine().calculate(observations)


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
    # Increasing price => positive drift.
    # --------------------------------------------------------------

    result = calculate_tps(
        [
            PriceObservation(
                price=100.0,
                timestamp=start,
            ),
            PriceObservation(
                price=110.0,
                timestamp=start + timedelta(seconds=10),
            ),
        ]
    )

    assert result.status == TPSStatus.VALID
    assert result.direction == TrendDirection.BULLISH
    assert result.price_change == 10.0
    assert result.elapsed_seconds == 10.0
    assert result.drift == 1.0

    # --------------------------------------------------------------
    # TEST 2
    # Decreasing price => negative drift.
    # --------------------------------------------------------------

    result = calculate_tps(
        [
            PriceObservation(
                price=110.0,
                timestamp=start,
            ),
            PriceObservation(
                price=100.0,
                timestamp=start + timedelta(seconds=10),
            ),
        ]
    )

    assert result.status == TPSStatus.VALID
    assert result.direction == TrendDirection.BEARISH
    assert result.drift == -1.0

    # --------------------------------------------------------------
    # TEST 3
    # Flat price => zero drift.
    # --------------------------------------------------------------

    result = calculate_tps(
        [
            PriceObservation(
                price=100.0,
                timestamp=start,
            ),
            PriceObservation(
                price=100.0,
                timestamp=start + timedelta(seconds=10),
            ),
        ]
    )

    assert result.status == TPSStatus.VALID
    assert result.direction == TrendDirection.NEUTRAL
    assert result.drift == 0.0

    # --------------------------------------------------------------
    # TEST 4
    # More time for same price change => lower velocity/drift.
    # --------------------------------------------------------------

    fast = calculate_tps(
        [
            PriceObservation(
                price=100.0,
                timestamp=start,
            ),
            PriceObservation(
                price=110.0,
                timestamp=start + timedelta(seconds=10),
            ),
        ]
    )

    slow = calculate_tps(
        [
            PriceObservation(
                price=100.0,
                timestamp=start,
            ),
            PriceObservation(
                price=110.0,
                timestamp=start + timedelta(seconds=20),
            ),
        ]
    )

    assert fast.is_valid
    assert slow.is_valid
    assert fast.drift > slow.drift

    # --------------------------------------------------------------
    # TEST 5
    # Reversal path is preserved as warning and does not distort
    # net drift.
    # --------------------------------------------------------------

    result = calculate_tps(
        [
            PriceObservation(
                price=100.0,
                timestamp=start,
            ),
            PriceObservation(
                price=110.0,
                timestamp=start + timedelta(seconds=10),
            ),
            PriceObservation(
                price=105.0,
                timestamp=start + timedelta(seconds=20),
            ),
            PriceObservation(
                price=115.0,
                timestamp=start + timedelta(seconds=30),
            ),
        ]
    )

    assert result.status == TPSStatus.VALID
    assert result.direction == TrendDirection.BULLISH
    assert result.drift == 0.5
    assert result.metadata["sign_changes"] == 2
    assert len(result.warnings) >= 1

    # --------------------------------------------------------------
    # TEST 6
    # Missing observation.
    # --------------------------------------------------------------

    result = calculate_tps([])

    assert result.status == TPSStatus.INSUFFICIENT
    assert result.drift is None

    # --------------------------------------------------------------
    # TEST 7
    # Negative price rejected.
    # --------------------------------------------------------------

    result = calculate_tps(
        [
            PriceObservation(
                price=-100.0,
                timestamp=start,
            ),
            PriceObservation(
                price=110.0,
                timestamp=start + timedelta(seconds=10),
            ),
        ]
    )

    assert result.status == TPSStatus.INVALID
    assert result.drift is None

    # --------------------------------------------------------------
    # TEST 8
    # Zero elapsed time rejected.
    # --------------------------------------------------------------

    result = calculate_tps(
        [
            PriceObservation(
                price=100.0,
                timestamp=start,
            ),
            PriceObservation(
                price=110.0,
                timestamp=start,
            ),
        ]
    )

    assert result.status == TPSStatus.INVALID

    # --------------------------------------------------------------
    # TEST 9
    # Chronological ordering required.
    # --------------------------------------------------------------

    result = calculate_tps(
        [
            PriceObservation(
                price=110.0,
                timestamp=start + timedelta(seconds=10),
            ),
            PriceObservation(
                price=100.0,
                timestamp=start,
            ),
        ]
    )

    assert result.status == TPSStatus.INVALID

    # --------------------------------------------------------------
    # TEST 10
    # Log-return mathematical identity.
    # --------------------------------------------------------------

    result = calculate_tps(
        [
            PriceObservation(
                price=100.0,
                timestamp=start,
            ),
            PriceObservation(
                price=200.0,
                timestamp=start + timedelta(seconds=10),
            ),
        ]
    )

    expected_log_return = log(2.0)

    assert result.status == TPSStatus.VALID
    assert abs(
        result.log_return - expected_log_return
    ) < 1e-12

    assert abs(
        result.log_return_rate
        - expected_log_return / 10.0
    ) < 1e-12

    # --------------------------------------------------------------
    # TEST 11
    # No arbitrary 0..100 normalization.
    # --------------------------------------------------------------

    assert result.metadata["normalization"] == "NOT_APPLIED"
    assert result.metadata["score_scale"] == "RAW"

    print("TPS V6 self-tests: PASS")


__all__ = [
    "ENGINE_NAME",
    "ENGINE_VERSION",
    "EQ_ID",
    "TPSStatus",
    "TrendDirection",
    "PriceObservation",
    "TPSResult",
    "TPSEngine",
    "calculate_tps",
]


if __name__ == "__main__":
    _run_self_tests()
