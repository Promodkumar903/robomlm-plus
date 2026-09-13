"""
ROBOMLM_PLUS
Evidence Cortex — TV
---------------------

TV = Trade / Price Velocity

Core calculation:

    TV = ΔP / Δt

where:

    ΔP = P_current - P_previous
    Δt = t_current - t_previous

For a sequence:

    TV_i = (P_i - P_(i-1)) / (t_i - t_(i-1))

The engine also exposes:

    absolute_velocity = |TV|

No:
- hardcoded velocity
- arbitrary score
- synthetic movement
- fixed confidence
- division by zero
- guessing missing timestamps
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping, Sequence

from .evidence_engine_base import (
    CalculationStep,
    Evidence,
    EvidenceEngineBase,
    EvidenceStatus,
)


@dataclass(frozen=True)
class TVMetrics:
    start_price: float
    end_price: float

    price_change: float
    elapsed_seconds: float

    velocity: float
    absolute_velocity: float

    observation_count: int
    interval_count: int

    observed_at: datetime
    status: EvidenceStatus

    price_unit: str
    time_unit: str


class TVEngine(EvidenceEngineBase):
    """
    Trade/Price Velocity engine.

    Expected input:

        {
            "observations": [
                {
                    "timestamp": datetime,
                    "price": 100.0
                },
                {
                    "timestamp": datetime,
                    "price": 101.5
                }
            ]
        }

    A single observation is insufficient because:

        Δt = 0 / unavailable

    The engine therefore does not manufacture a velocity.

    If multiple observations exist, observations are ordered
    chronologically before calculation.
    """

    ENGINE_NAME = "TV"
    LAYER = "L003"

    _OBSERVATION_KEYS = (
        "observations",
        "ticks",
        "trades",
        "snapshots",
    )

    _TIMESTAMP_KEYS = (
        "timestamp",
        "observed_at",
        "trade_timestamp",
        "time",
    )

    _PRICE_KEYS = (
        "price",
        "trade_price",
        "last_price",
        "close",
    )

    def calculate(
        self,
        data: Mapping[str, Any],
    ) -> tuple[Evidence, ...]:
        metrics = self.compute(data)

        common_inputs = {
            "observation_count": metrics.observation_count,
            "interval_count": metrics.interval_count,
            "start_price": metrics.start_price,
            "end_price": metrics.end_price,
            "elapsed_seconds": metrics.elapsed_seconds,
            "price_unit": metrics.price_unit,
        }

        return (
            self.make_evidence(
                metric="price_change",
                value=metrics.price_change,
                unit=metrics.price_unit,
                status=metrics.status,
                observed_at=metrics.observed_at,
                source=data.get("source"),
                source_type=data.get("source_type"),
                inputs=common_inputs,
                calculation=(
                    CalculationStep(
                        name="price_displacement",
                        formula="P_end - P_start",
                        inputs={
                            "start_price": metrics.start_price,
                            "end_price": metrics.end_price,
                        },
                        output=metrics.price_change,
                    ),
                ),
                reason=(
                    "Observed end-to-end price displacement."
                ),
            ),
            self.make_evidence(
                metric="elapsed_seconds",
                value=metrics.elapsed_seconds,
                unit=metrics.time_unit,
                status=metrics.status,
                observed_at=metrics.observed_at,
                source=data.get("source"),
                source_type=data.get("source_type"),
                inputs=common_inputs,
                calculation=(
                    CalculationStep(
                        name="elapsed_time",
                        formula="t_end - t_start",
                        inputs={
                            "start_timestamp": self._extract_timestamp(
                                self._extract_observations(data)[0]
                            ),
                            "end_timestamp": metrics.observed_at,
                        },
                        output=metrics.elapsed_seconds,
                    ),
                ),
                reason=(
                    "Elapsed observation time used for velocity."
                ),
            ),
            self.make_evidence(
                metric="velocity",
                value=metrics.velocity,
                unit=f"{metrics.price_unit}/second",
                status=metrics.status,
                observed_at=metrics.observed_at,
                source=data.get("source"),
                source_type=data.get("source_type"),
                inputs=common_inputs,
                calculation=(
                    CalculationStep(
                        name="price_velocity",
                        formula="(P_end - P_start) / (t_end - t_start)",
                        inputs={
                            "price_change": metrics.price_change,
                            "elapsed_seconds": metrics.elapsed_seconds,
                        },
                        output=metrics.velocity,
                    ),
                ),
                reason=(
                    "Signed price velocity derived from observed "
                    "price displacement and elapsed time."
                ),
            ),
            self.make_evidence(
                metric="absolute_velocity",
                value=metrics.absolute_velocity,
                unit=f"{metrics.price_unit}/second",
                status=metrics.status,
                observed_at=metrics.observed_at,
                source=data.get("source"),
                source_type=data.get("source_type"),
                inputs={
                    **common_inputs,
                    "velocity": metrics.velocity,
                },
                calculation=(
                    CalculationStep(
                        name="absolute_price_velocity",
                        formula="abs(velocity)",
                        inputs={
                            "velocity": metrics.velocity,
                        },
                        output=metrics.absolute_velocity,
                    ),
                ),
                reason=(
                    "Magnitude of observed price velocity independent "
                    "of direction."
                ),
            ),
        )

    def compute(
        self,
        data: Mapping[str, Any],
    ) -> TVMetrics:
        observations = self._extract_observations(data)

        if len(observations) < 2:
            raise ValueError(
                "TV requires at least two timestamped price observations"
            )

        parsed = [
            self._parse_observation(
                observation,
                inherited=data,
            )
            for observation in observations
        ]

        # Chronological ordering is mandatory for ΔP / Δt.
        parsed.sort(key=lambda item: item["timestamp"])

        self._validate_identity_consistency(parsed)

        start = parsed[0]
        end = parsed[-1]

        elapsed_seconds = (
            end["timestamp"] - start["timestamp"]
        ).total_seconds()

        if elapsed_seconds <= 0:
            raise ValueError(
                "TV requires strictly positive elapsed time"
            )

        price_change = (
            end["price"] - start["price"]
        )

        velocity = price_change / elapsed_seconds

        if not self._finite(velocity):
            raise ValueError(
                "TV calculation produced a non-finite velocity"
            )

        absolute_velocity = abs(velocity)

        price_units = {
            item["price_unit"]
            for item in parsed
            if item["price_unit"] is not None
        }

        if len(price_units) > 1:
            raise ValueError(
                "TV cannot calculate across different price units"
            )

        price_unit = (
            next(iter(price_units))
            if price_units
            else str(data.get("price_unit", "native_price"))
        )

        return TVMetrics(
            start_price=start["price"],
            end_price=end["price"],
            price_change=price_change,
            elapsed_seconds=elapsed_seconds,
            velocity=velocity,
            absolute_velocity=absolute_velocity,
            observation_count=len(parsed),
            interval_count=len(parsed) - 1,
            observed_at=end["timestamp"],
            status=EvidenceStatus.VALID,
            price_unit=price_unit,
            time_unit="seconds",
        )

    # ------------------------------------------------------------------
    # INPUT
    # ------------------------------------------------------------------

    def _extract_observations(
        self,
        data: Mapping[str, Any],
    ) -> list[Mapping[str, Any]]:
        for key in self._OBSERVATION_KEYS:
            value = data.get(key)

            if value is None:
                continue

            if not isinstance(value, Sequence) or isinstance(
                value,
                (str, bytes, bytearray),
            ):
                raise TypeError(
                    f"'{key}' must be a sequence of mappings"
                )

            observations: list[Mapping[str, Any]] = []

            for item in value:
                if not isinstance(item, Mapping):
                    raise TypeError(
                        f"Every '{key}' item must be a mapping"
                    )

                observations.append(item)

            return observations

        if self._has_price_and_timestamp(data):
            return [data]

        raise ValueError(
            "TV input must contain timestamped price observations"
        )

    def _parse_observation(
        self,
        observation: Mapping[str, Any],
        *,
        inherited: Mapping[str, Any],
    ) -> dict[str, Any]:
        timestamp_value = self._first(
            observation,
            self._TIMESTAMP_KEYS,
        )

        if timestamp_value is None:
            timestamp_value = self._first(
                inherited,
                self._TIMESTAMP_KEYS,
            )

        if timestamp_value is None:
            raise ValueError(
                "TV observation requires timestamp"
            )

        timestamp = self._coerce_timestamp(timestamp_value)

        price_value = self._first(
            observation,
            self._PRICE_KEYS,
        )

        if price_value is None:
            price_value = self._first(
                inherited,
                self._PRICE_KEYS,
            )

        if price_value is None:
            raise ValueError(
                "TV observation requires price"
            )

        price = self.non_negative(
            price_value,
            name="price",
        )

        price_unit = observation.get(
            "price_unit",
            inherited.get("price_unit"),
        )

        if price_unit is not None:
            if (
                not isinstance(price_unit, str)
                or not price_unit.strip()
            ):
                raise ValueError(
                    "price_unit must be a non-empty string"
                )

            price_unit = price_unit.strip()

        instrument_id = observation.get(
            "instrument_id",
            inherited.get("instrument_id"),
        )

        return {
            "timestamp": timestamp,
            "price": price,
            "price_unit": price_unit,
            "instrument_id": instrument_id,
        }

    # ------------------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_identity_consistency(
        observations: Sequence[Mapping[str, Any]],
    ) -> None:
        identities = {
            item["instrument_id"]
            for item in observations
            if item.get("instrument_id") is not None
        }

        if len(identities) > 1:
            raise ValueError(
                "TV cannot calculate velocity across multiple instruments"
            )

    @staticmethod
    def _has_price_and_timestamp(
        data: Mapping[str, Any],
    ) -> bool:
        has_price = any(
            key in data and data[key] is not None
            for key in TVEngine._PRICE_KEYS
        )

        has_timestamp = any(
            key in data and data[key] is not None
            for key in TVEngine._TIMESTAMP_KEYS
        )

        return has_price and has_timestamp

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    @staticmethod
    def _first(
        data: Mapping[str, Any],
        keys: Sequence[str],
    ) -> Any:
        for key in keys:
            if key in data and data[key] is not None:
                return data[key]

        return None

    @staticmethod
    def _coerce_timestamp(value: Any) -> datetime:
        if isinstance(value, datetime):
            timestamp = value

        elif isinstance(value, str):
            text = value.strip()

            if text.endswith("Z"):
                text = text[:-1] + "+00:00"

            try:
                timestamp = datetime.fromisoformat(text)
            except ValueError as exc:
                raise ValueError(
                    f"Invalid TV timestamp: {value!r}"
                ) from exc

        else:
            raise TypeError(
                "TV timestamp must be datetime or ISO-8601 string"
            )

        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError(
                "TV timestamp must be timezone-aware"
            )

        return timestamp

    @staticmethod
    def _finite(value: float) -> bool:
        return isfinite(value)


# ----------------------------------------------------------------------
# COMPATIBILITY ALIASES
# ----------------------------------------------------------------------

TradeVelocityEngine = TVEngine
PriceVelocityEngine = TVEngine


__all__ = [
    "TVMetrics",
    "TVEngine",
    "TradeVelocityEngine",
    "PriceVelocityEngine",
]