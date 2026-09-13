"""
ROBOMLM_PLUS
Evidence Cortex — DAR
----------------------

DAR = Depth Absorption Ratio

Purpose
-------
Measure how much observed aggressive market-order flow is being
absorbed by available passive order-book depth.

Core principle
--------------
Aggressive flow alone is not enough.

For each side:

    Buy Absorption  = Aggressive Buy Volume / Available Ask Depth
    Sell Absorption = Aggressive Sell Volume / Available Bid Depth

Directional DAR:

    DAR = Buy Absorption - Sell Absorption

The engine never invents order-book depth.
Missing depth remains missing.

No:
- arbitrary score
- hardcoded confidence
- fake liquidity
- synthetic limit volume
- guessed order-book values
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from typing import Any, Mapping, Sequence

from .evidence_engine_base import (
    CalculationStep,
    Evidence,
    EvidenceEngineBase,
    EvidenceStatus,
)


@dataclass(frozen=True)
class DARMetrics:
    aggressive_buy_volume: float
    aggressive_sell_volume: float

    ask_depth: float
    bid_depth: float

    buy_absorption: float | None
    sell_absorption: float | None

    dar: float | None

    buy_depth_coverage: float | None
    sell_depth_coverage: float | None

    total_depth: float
    total_aggressive_volume: float

    observation_count: int
    status: EvidenceStatus

    observed_at: datetime
    volume_unit: str


class DAREngine(EvidenceEngineBase):
    """
    Depth Absorption Ratio engine.

    Expected input:

    {
        "timestamp": datetime,
        "instrument_id": "...",

        "aggressive_buy_volume": 100,
        "aggressive_sell_volume": 80,

        "bid_depth": 500,
        "ask_depth": 400,

        "volume_unit": "shares"
    }

    Alternatively, aggregated observations may be supplied:

    {
        "observations": [
            {
                "timestamp": ...,
                "aggressive_buy_volume": ...,
                "aggressive_sell_volume": ...,
                "bid_depth": ...,
                "ask_depth": ...
            }
        ]
    }

    Depth must represent actual observed passive depth from the
    supplied market-data source. This engine does not manufacture it.
    """

    ENGINE_NAME = "DAR"
    LAYER = "L003"

    _BUY_KEYS = (
        "aggressive_buy_volume",
        "buy_volume",
        "aggressive_buy_qty",
    )

    _SELL_KEYS = (
        "aggressive_sell_volume",
        "sell_volume",
        "aggressive_sell_qty",
    )

    _BID_DEPTH_KEYS = (
        "bid_depth",
        "bid_size",
        "bid_volume",
    )

    _ASK_DEPTH_KEYS = (
        "ask_depth",
        "ask_size",
        "ask_volume",
    )

    _TIMESTAMP_KEYS = (
        "timestamp",
        "observed_at",
        "trade_timestamp",
        "time",
    )

    def __init__(self, *, depth_levels: int | None = None) -> None:
        super().__init__()

        if depth_levels is not None:
            if not isinstance(depth_levels, int):
                raise TypeError("depth_levels must be an integer or None")
            if depth_levels <= 0:
                raise ValueError("depth_levels must be > 0")

        self.depth_levels = depth_levels

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def calculate(self, data: Mapping[str, Any]) -> tuple[Evidence, ...]:
        metrics = self.compute(data)

        common_inputs = {
            "observation_count": metrics.observation_count,
            "aggressive_buy_volume": metrics.aggressive_buy_volume,
            "aggressive_sell_volume": metrics.aggressive_sell_volume,
            "bid_depth": metrics.bid_depth,
            "ask_depth": metrics.ask_depth,
            "volume_unit": metrics.volume_unit,
        }

        evidences: list[Evidence] = []

        evidences.append(
            self.make_evidence(
                metric="aggressive_buy_volume",
                value=metrics.aggressive_buy_volume,
                unit=metrics.volume_unit,
                status=metrics.status,
                observed_at=metrics.observed_at,
                source=data.get("source"),
                source_type=data.get("source_type"),
                inputs=common_inputs,
                calculation=(
                    CalculationStep(
                        name="aggregate_buy_flow",
                        formula="Σ aggressive_buy_volume_i",
                        inputs={
                            "observation_count": metrics.observation_count,
                        },
                        output=metrics.aggressive_buy_volume,
                    ),
                ),
                reason=self._status_reason(
                    metrics.status,
                    "Aggregated aggressive buy-side market volume.",
                ),
            )
        )

        evidences.append(
            self.make_evidence(
                metric="aggressive_sell_volume",
                value=metrics.aggressive_sell_volume,
                unit=metrics.volume_unit,
                status=metrics.status,
                observed_at=metrics.observed_at,
                source=data.get("source"),
                source_type=data.get("source_type"),
                inputs=common_inputs,
                calculation=(
                    CalculationStep(
                        name="aggregate_sell_flow",
                        formula="Σ aggressive_sell_volume_i",
                        inputs={
                            "observation_count": metrics.observation_count,
                        },
                        output=metrics.aggressive_sell_volume,
                    ),
                ),
                reason=self._status_reason(
                    metrics.status,
                    "Aggregated aggressive sell-side market volume.",
                ),
            )
        )

        evidences.append(
            self.make_evidence(
                metric="bid_depth",
                value=metrics.bid_depth,
                unit=metrics.volume_unit,
                status=metrics.status,
                observed_at=metrics.observed_at,
                source=data.get("source"),
                source_type=data.get("source_type"),
                inputs=common_inputs,
                calculation=(
                    CalculationStep(
                        name="aggregate_bid_depth",
                        formula="Σ observed_bid_depth_i",
                        inputs={
                            "observation_count": metrics.observation_count,
                        },
                        output=metrics.bid_depth,
                    ),
                ),
                reason=self._status_reason(
                    metrics.status,
                    "Aggregated observed passive bid depth.",
                ),
            )
        )

        evidences.append(
            self.make_evidence(
                metric="ask_depth",
                value=metrics.ask_depth,
                unit=metrics.volume_unit,
                status=metrics.status,
                observed_at=metrics.observed_at,
                source=data.get("source"),
                source_type=data.get("source_type"),
                inputs=common_inputs,
                calculation=(
                    CalculationStep(
                        name="aggregate_ask_depth",
                        formula="Σ observed_ask_depth_i",
                        inputs={
                            "observation_count": metrics.observation_count,
                        },
                        output=metrics.ask_depth,
                    ),
                ),
                reason=self._status_reason(
                    metrics.status,
                    "Aggregated observed passive ask depth.",
                ),
            )
        )

        evidences.append(
            self._derived_evidence(
                data=data,
                metric="buy_absorption",
                value=metrics.buy_absorption,
                unit="ratio",
                status=metrics.status
                if metrics.buy_absorption is not None
                else EvidenceStatus.INSUFFICIENT,
                observed_at=metrics.observed_at,
                inputs=common_inputs,
                formula=(
                    "aggressive_buy_volume / ask_depth"
                ),
                output=metrics.buy_absorption,
                reason=(
                    "Aggressive buy flow relative to observed ask depth."
                    if metrics.buy_absorption is not None
                    else "Ask depth is zero; buy absorption is undefined."
                ),
            )
        )

        evidences.append(
            self._derived_evidence(
                data=data,
                metric="sell_absorption",
                value=metrics.sell_absorption,
                unit="ratio",
                status=metrics.status
                if metrics.sell_absorption is not None
                else EvidenceStatus.INSUFFICIENT,
                observed_at=metrics.observed_at,
                inputs=common_inputs,
                formula=(
                    "aggressive_sell_volume / bid_depth"
                ),
                output=metrics.sell_absorption,
                reason=(
                    "Aggressive sell flow relative to observed bid depth."
                    if metrics.sell_absorption is not None
                    else "Bid depth is zero; sell absorption is undefined."
                ),
            )
        )

        evidences.append(
            self._derived_evidence(
                data=data,
                metric="dar",
                value=metrics.dar,
                unit="ratio",
                status=metrics.status
                if metrics.dar is not None
                else EvidenceStatus.INSUFFICIENT,
                observed_at=metrics.observed_at,
                inputs={
                    **common_inputs,
                    "buy_absorption": metrics.buy_absorption,
                    "sell_absorption": metrics.sell_absorption,
                },
                formula=(
                    "(aggressive_buy_volume / ask_depth) "
                    "- "
                    "(aggressive_sell_volume / bid_depth)"
                ),
                output=metrics.dar,
                reason=(
                    "Directional depth-absorption differential."
                    if metrics.dar is not None
                    else "DAR cannot be calculated because one or both "
                    "side-specific depth denominators are zero."
                ),
            )
        )

        evidences.append(
            self._derived_evidence(
                data=data,
                metric="buy_depth_coverage",
                value=metrics.buy_depth_coverage,
                unit="ratio",
                status=metrics.status
                if metrics.buy_depth_coverage is not None
                else EvidenceStatus.INSUFFICIENT,
                observed_at=metrics.observed_at,
                inputs=common_inputs,
                formula=(
                    "ask_depth / aggressive_buy_volume"
                ),
                output=metrics.buy_depth_coverage,
                reason=(
                    "Observed ask depth per unit of aggressive buy flow."
                    if metrics.buy_depth_coverage is not None
                    else "Aggressive buy volume is zero."
                ),
            )
        )

        evidences.append(
            self._derived_evidence(
                data=data,
                metric="sell_depth_coverage",
                value=metrics.sell_depth_coverage,
                unit="ratio",
                status=metrics.status
                if metrics.sell_depth_coverage is not None
                else EvidenceStatus.INSUFFICIENT,
                observed_at=metrics.observed_at,
                inputs=common_inputs,
                formula=(
                    "bid_depth / aggressive_sell_volume"
                ),
                output=metrics.sell_depth_coverage,
                reason=(
                    "Observed bid depth per unit of aggressive sell flow."
                    if metrics.sell_depth_coverage is not None
                    else "Aggressive sell volume is zero."
                ),
            )
        )

        return tuple(evidences)

    def compute(self, data: Mapping[str, Any]) -> DARMetrics:
        observations = self._extract_observations(data)

        if not observations:
            raise ValueError("DAR requires at least one observation")

        parsed = [
            self._parse_observation(
                observation,
                inherited=data,
            )
            for observation in observations
        ]

        timestamps = [item["timestamp"] for item in parsed]
        observed_at = max(timestamps)

        volume_units = {
            item["volume_unit"]
            for item in parsed
            if item["volume_unit"] is not None
        }

        if len(volume_units) > 1:
            raise ValueError(
                "DAR cannot aggregate observations with different volume units"
            )

        volume_unit = (
            next(iter(volume_units))
            if volume_units
            else str(data.get("volume_unit", "native_volume"))
        )

        buy_volume = sum(
            item["aggressive_buy_volume"] for item in parsed
        )

        sell_volume = sum(
            item["aggressive_sell_volume"] for item in parsed
        )

        bid_depth = sum(
            item["bid_depth"] for item in parsed
        )

        ask_depth = sum(
            item["ask_depth"] for item in parsed
        )

        buy_absorption = (
            buy_volume / ask_depth
            if ask_depth > 0
            else None
        )

        sell_absorption = (
            sell_volume / bid_depth
            if bid_depth > 0
            else None
        )

        # DAR is only mathematically defined when BOTH side-specific
        # denominators exist.
        dar = (
            buy_absorption - sell_absorption
            if buy_absorption is not None
            and sell_absorption is not None
            else None
        )

        buy_depth_coverage = (
            ask_depth / buy_volume
            if buy_volume > 0
            else None
        )

        sell_depth_coverage = (
            bid_depth / sell_volume
            if sell_volume > 0
            else None
        )

        total_depth = bid_depth + ask_depth
        total_aggressive_volume = buy_volume + sell_volume

        return DARMetrics(
            aggressive_buy_volume=buy_volume,
            aggressive_sell_volume=sell_volume,
            ask_depth=ask_depth,
            bid_depth=bid_depth,
            buy_absorption=buy_absorption,
            sell_absorption=sell_absorption,
            dar=dar,
            buy_depth_coverage=buy_depth_coverage,
            sell_depth_coverage=sell_depth_coverage,
            total_depth=total_depth,
            total_aggressive_volume=total_aggressive_volume,
            observation_count=len(parsed),
            status=(
                EvidenceStatus.VALID
                if buy_absorption is not None
                and sell_absorption is not None
                else EvidenceStatus.PARTIAL
            ),
            observed_at=observed_at,
            volume_unit=volume_unit,
        )

    # ------------------------------------------------------------------
    # INPUT EXTRACTION
    # ------------------------------------------------------------------

    def _extract_observations(
        self,
        data: Mapping[str, Any],
    ) -> list[Mapping[str, Any]]:
        for key in ("observations", "snapshots", "ticks", "trades"):
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

            result: list[Mapping[str, Any]] = []

            for item in value:
                if not isinstance(item, Mapping):
                    raise TypeError(
                        f"Every {key} item must be a mapping"
                    )
                result.append(item)

            return result

        if self._has_any(
            data,
            self._BUY_KEYS
            + self._SELL_KEYS
            + self._BID_DEPTH_KEYS
            + self._ASK_DEPTH_KEYS,
        ):
            return [data]

        raise ValueError(
            "DAR input must contain an observation sequence or "
            "a single observation"
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
            raise ValueError("DAR observation requires timestamp")

        timestamp = self._coerce_timestamp(timestamp_value)

        buy = self._first(
            observation,
            self._BUY_KEYS,
        )

        if buy is None:
            buy = self._first(inherited, self._BUY_KEYS)

        sell = self._first(
            observation,
            self._SELL_KEYS,
        )

        if sell is None:
            sell = self._first(inherited, self._SELL_KEYS)

        bid_depth = self._first(
            observation,
            self._BID_DEPTH_KEYS,
        )

        if bid_depth is None:
            bid_depth = self._first(
                inherited,
                self._BID_DEPTH_KEYS,
            )

        ask_depth = self._first(
            observation,
            self._ASK_DEPTH_KEYS,
        )

        if ask_depth is None:
            ask_depth = self._first(
                inherited,
                self._ASK_DEPTH_KEYS,
            )

        buy = self.non_negative(
            0.0 if buy is None else buy,
            name="aggressive_buy_volume",
        )

        sell = self.non_negative(
            0.0 if sell is None else sell,
            name="aggressive_sell_volume",
        )

        bid_depth = self.non_negative(
            0.0 if bid_depth is None else bid_depth,
            name="bid_depth",
        )

        ask_depth = self.non_negative(
            0.0 if ask_depth is None else ask_depth,
            name="ask_depth",
        )

        volume_unit = observation.get(
            "volume_unit",
            inherited.get("volume_unit"),
        )

        if volume_unit is not None:
            if not isinstance(volume_unit, str) or not volume_unit.strip():
                raise ValueError("volume_unit must be a non-empty string")

            volume_unit = volume_unit.strip()

        return {
            "timestamp": timestamp,
            "aggressive_buy_volume": buy,
            "aggressive_sell_volume": sell,
            "bid_depth": bid_depth,
            "ask_depth": ask_depth,
            "volume_unit": volume_unit,
        }

    # ------------------------------------------------------------------
    # EVIDENCE HELPERS
    # ------------------------------------------------------------------

    def _derived_evidence(
        self,
        *,
        data: Mapping[str, Any],
        metric: str,
        value: Any,
        unit: str,
        status: EvidenceStatus,
        observed_at: datetime,
        inputs: Mapping[str, Any],
        formula: str,
        output: Any,
        reason: str,
    ) -> Evidence:
        return self.make_evidence(
            metric=metric,
            value=value,
            unit=unit,
            status=status,
            observed_at=observed_at,
            source=data.get("source"),
            source_type=data.get("source_type"),
            inputs=inputs,
            calculation=(
                CalculationStep(
                    name=metric,
                    formula=formula,
                    inputs=inputs,
                    output=output,
                ),
            ),
            reason=reason,
        )

    @staticmethod
    def _status_reason(
        status: EvidenceStatus,
        valid_reason: str,
    ) -> str:
        if status == EvidenceStatus.VALID:
            return valid_reason

        return (
            valid_reason
            + " One or more mathematical prerequisites were "
            "not fully available."
        )

    # ------------------------------------------------------------------
    # GENERAL HELPERS
    # ------------------------------------------------------------------

    @staticmethod
    def _has_any(
        data: Mapping[str, Any],
        keys: Sequence[str],
    ) -> bool:
        return any(key in data for key in keys)

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
                    f"Invalid DAR timestamp: {value!r}"
                ) from exc
        else:
            raise TypeError(
                "DAR timestamp must be datetime or ISO-8601 string"
            )

        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError(
                "DAR timestamp must be timezone-aware"
            )

        return timestamp


# ----------------------------------------------------------------------
# COMPATIBILITY ALIASES
# ----------------------------------------------------------------------

DARGate = DAREngine
DepthAbsorptionRatioEngine = DAREngine


__all__ = [
    "DARMetrics",
    "DAREngine",
    "DARGate",
    "DepthAbsorptionRatioEngine",
]