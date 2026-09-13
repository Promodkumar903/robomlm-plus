"""
ROBOMLM_PLUS
Evidence Cortex — OXE
----------------------

OXE = Order-flow eXecution / Obstacle Evidence

Purpose
-------
Combine independently calculated execution-flow evidence:

    NED -> directional aggressive execution pressure
    DAR -> aggressive flow relative to passive depth
    TV  -> price displacement velocity

OXE does NOT create an arbitrary 0-100 score.

Core derived quantities
-----------------------

1. Execution pressure

    NED_pressure =
        (buy_volume - sell_volume)
        /
        (buy_volume + sell_volume)

Range:

    [-1, +1]

2. Absorption differential

    DAR = buy_absorption - sell_absorption

3. Price response

    TV = ΔPrice / ΔTime

4. Flow-response efficiency

    F = ΔPrice / NED

Only defined when NED != 0.

5. Obstacle interpretation

The engine preserves the independently calculated quantities and
derives a directional obstacle relationship rather than inventing
a confidence percentage.

No:
- arbitrary weighted score
- hardcoded confidence
- fake liquidity
- guessed depth
- synthetic probability
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
class OXEMetrics:
    aggressive_buy_volume: float
    aggressive_sell_volume: float

    bid_depth: float
    ask_depth: float

    ned: float
    ned_pressure: float | None

    buy_absorption: float | None
    sell_absorption: float | None
    dar: float | None

    price_change: float
    elapsed_seconds: float
    velocity: float

    flow_response_efficiency: float | None

    execution_side: str
    obstacle_side: str

    observation_count: int
    status: EvidenceStatus

    observed_at: datetime
    volume_unit: str
    price_unit: str


class OXEEngine(EvidenceEngineBase):
    """
    Order-flow execution / obstacle evidence engine.

    OXE consumes already-derived NED/DAR/TV values.

    Preferred input:

    {
        "ned": {
            "aggressive_buy_volume": ...,
            "aggressive_sell_volume": ...
        },

        "dar": {
            "bid_depth": ...,
            "ask_depth": ...,
            "buy_absorption": ...,
            "sell_absorption": ...,
            "dar": ...
        },

        "tv": {
            "price_change": ...,
            "elapsed_seconds": ...,
            "velocity": ...
        },

        "timestamp": ...
    }

    A flattened representation is also accepted.

    The engine never reconstructs missing values from unrelated
    approximations.
    """

    ENGINE_NAME = "OXE"
    LAYER = "L003"

    def calculate(
        self,
        data: Mapping[str, Any],
    ) -> tuple[Evidence, ...]:
        metrics = self.compute(data)

        common_inputs = {
            "aggressive_buy_volume": metrics.aggressive_buy_volume,
            "aggressive_sell_volume": metrics.aggressive_sell_volume,
            "bid_depth": metrics.bid_depth,
            "ask_depth": metrics.ask_depth,
            "ned": metrics.ned,
            "ned_pressure": metrics.ned_pressure,
            "buy_absorption": metrics.buy_absorption,
            "sell_absorption": metrics.sell_absorption,
            "dar": metrics.dar,
            "price_change": metrics.price_change,
            "elapsed_seconds": metrics.elapsed_seconds,
            "velocity": metrics.velocity,
            "flow_response_efficiency":
                metrics.flow_response_efficiency,
        }

        evidences: list[Evidence] = []

        evidences.append(
            self.make_evidence(
                metric="ned_pressure",
                value=metrics.ned_pressure,
                unit="ratio",
                status=(
                    metrics.status
                    if metrics.ned_pressure is not None
                    else EvidenceStatus.INSUFFICIENT
                ),
                observed_at=metrics.observed_at,
                source=data.get("source"),
                source_type=data.get("source_type"),
                inputs=common_inputs,
                calculation=(
                    CalculationStep(
                        name="ned_pressure",
                        formula=(
                            "(aggressive_buy_volume "
                            "- aggressive_sell_volume) "
                            "/ "
                            "(aggressive_buy_volume "
                            "+ aggressive_sell_volume)"
                        ),
                        inputs={
                            "aggressive_buy_volume":
                                metrics.aggressive_buy_volume,
                            "aggressive_sell_volume":
                                metrics.aggressive_sell_volume,
                        },
                        output=metrics.ned_pressure,
                    ),
                ),
                reason=(
                    "Directional aggressive execution pressure."
                    if metrics.ned_pressure is not None
                    else "Total aggressive volume is zero."
                ),
            )
        )

        evidences.append(
            self.make_evidence(
                metric="dar",
                value=metrics.dar,
                unit="ratio",
                status=(
                    metrics.status
                    if metrics.dar is not None
                    else EvidenceStatus.INSUFFICIENT
                ),
                observed_at=metrics.observed_at,
                source=data.get("source"),
                source_type=data.get("source_type"),
                inputs=common_inputs,
                calculation=(
                    CalculationStep(
                        name="dar",
                        formula=(
                            "(aggressive_buy_volume / ask_depth) "
                            "- "
                            "(aggressive_sell_volume / bid_depth)"
                        ),
                        inputs={
                            "aggressive_buy_volume":
                                metrics.aggressive_buy_volume,
                            "aggressive_sell_volume":
                                metrics.aggressive_sell_volume,
                            "ask_depth": metrics.ask_depth,
                            "bid_depth": metrics.bid_depth,
                        },
                        output=metrics.dar,
                    ),
                ),
                reason=(
                    "Directional passive-depth absorption differential."
                    if metrics.dar is not None
                    else "Both side-specific depth denominators "
                         "are required."
                ),
            )
        )

        evidences.append(
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
                        formula=(
                            "price_change / elapsed_seconds"
                        ),
                        inputs={
                            "price_change": metrics.price_change,
                            "elapsed_seconds":
                                metrics.elapsed_seconds,
                        },
                        output=metrics.velocity,
                    ),
                ),
                reason="Observed signed price response over time.",
            )
        )

        evidences.append(
            self.make_evidence(
                metric="flow_response_efficiency",
                value=metrics.flow_response_efficiency,
                unit=f"{metrics.price_unit}/{metrics.volume_unit}",
                status=(
                    metrics.status
                    if metrics.flow_response_efficiency is not None
                    else EvidenceStatus.INSUFFICIENT
                ),
                observed_at=metrics.observed_at,
                source=data.get("source"),
                source_type=data.get("source_type"),
                inputs=common_inputs,
                calculation=(
                    CalculationStep(
                        name="flow_response_efficiency",
                        formula=(
                            "price_change / NED"
                        ),
                        inputs={
                            "price_change": metrics.price_change,
                            "ned": metrics.ned,
                        },
                        output=metrics.flow_response_efficiency,
                    ),
                ),
                reason=(
                    "Price displacement per unit of net aggressive "
                    "execution."
                    if metrics.flow_response_efficiency is not None
                    else "NED is zero; flow-response ratio is undefined."
                ),
            )
        )

        evidences.append(
            self.make_evidence(
                metric="execution_side",
                value=metrics.execution_side,
                unit=None,
                status=metrics.status,
                observed_at=metrics.observed_at,
                source=data.get("source"),
                source_type=data.get("source_type"),
                inputs=common_inputs,
                calculation=(
                    CalculationStep(
                        name="execution_direction",
                        formula=(
                            "sign(NED)"
                        ),
                        inputs={
                            "ned": metrics.ned,
                        },
                        output=metrics.execution_side,
                    ),
                ),
                reason=(
                    "Directional side derived directly from NED."
                ),
            )
        )

        evidences.append(
            self.make_evidence(
                metric="obstacle_side",
                value=metrics.obstacle_side,
                unit=None,
                status=metrics.status,
                observed_at=metrics.observed_at,
                source=data.get("source"),
                source_type=data.get("source_type"),
                inputs=common_inputs,
                calculation=(
                    CalculationStep(
                        name="obstacle_direction",
                        formula=(
                            "opposite_side_of_positive_DAR"
                        ),
                        inputs={
                            "dar": metrics.dar,
                            "ned": metrics.ned,
                        },
                        output=metrics.obstacle_side,
                    ),
                ),
                reason=(
                    "Potential opposing absorption side derived from "
                    "the observed directional absorption differential."
                ),
            )
        )

        return tuple(evidences)

    # ------------------------------------------------------------------
    # CORE CALCULATION
    # ------------------------------------------------------------------

    def compute(
        self,
        data: Mapping[str, Any],
    ) -> OXEMetrics:
        ned = self._section(data, "ned")
        dar = self._section(data, "dar")
        tv = self._section(data, "tv")

        buy_volume = self._required_non_negative(
            ned,
            (
                "aggressive_buy_volume",
                "buy_volume",
                "aggressive_buy_qty",
            ),
            "aggressive_buy_volume",
        )

        sell_volume = self._required_non_negative(
            ned,
            (
                "aggressive_sell_volume",
                "sell_volume",
                "aggressive_sell_qty",
            ),
            "aggressive_sell_volume",
        )

        bid_depth = self._required_non_negative(
            dar,
            (
                "bid_depth",
                "bid_size",
                "bid_volume",
            ),
            "bid_depth",
        )

        ask_depth = self._required_non_negative(
            dar,
            (
                "ask_depth",
                "ask_size",
                "ask_volume",
            ),
            "ask_depth",
        )

        price_change = self._required_numeric(
            tv,
            (
                "price_change",
                "delta_price",
            ),
            "price_change",
        )

        elapsed_seconds = self._required_positive(
            tv,
            (
                "elapsed_seconds",
                "elapsed_time",
            ),
            "elapsed_seconds",
        )

        velocity = self._required_numeric(
            tv,
            (
                "velocity",
                "price_velocity",
            ),
            "velocity",
        )

        ned_value = buy_volume - sell_volume

        total_aggressive_volume = (
            buy_volume + sell_volume
        )

        ned_pressure = (
            ned_value / total_aggressive_volume
            if total_aggressive_volume > 0
            else None
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

        dar_value = (
            buy_absorption - sell_absorption
            if buy_absorption is not None
            and sell_absorption is not None
            else None
        )

        flow_response_efficiency = (
            price_change / ned_value
            if ned_value != 0
            else None
        )

        if ned_value > 0:
            execution_side = "BUY"
        elif ned_value < 0:
            execution_side = "SELL"
        else:
            execution_side = "BALANCED"

        obstacle_side = self._obstacle_side(
            dar_value=dar_value,
            execution_side=execution_side,
        )

        timestamp = self._extract_timestamp(
            data,
            ned,
            dar,
            tv,
        )

        price_unit = self._unit(
            data,
            tv,
            "price_unit",
            "native_price",
        )

        volume_unit = self._unit(
            data,
            ned,
            "volume_unit",
            "native_volume",
        )

        status = (
            EvidenceStatus.VALID
            if dar_value is not None
            else EvidenceStatus.PARTIAL
        )

        return OXEMetrics(
            aggressive_buy_volume=buy_volume,
            aggressive_sell_volume=sell_volume,
            bid_depth=bid_depth,
            ask_depth=ask_depth,
            ned=ned_value,
            ned_pressure=ned_pressure,
            buy_absorption=buy_absorption,
            sell_absorption=sell_absorption,
            dar=dar_value,
            price_change=price_change,
            elapsed_seconds=elapsed_seconds,
            velocity=velocity,
            flow_response_efficiency=flow_response_efficiency,
            execution_side=execution_side,
            obstacle_side=obstacle_side,
            observation_count=self._observation_count(
                data,
                ned,
                dar,
                tv,
            ),
            status=status,
            observed_at=timestamp,
            volume_unit=volume_unit,
            price_unit=price_unit,
        )

    # ------------------------------------------------------------------
    # OBSTACLE INTERPRETATION
    # ------------------------------------------------------------------

    @staticmethod
    def _obstacle_side(
        *,
        dar_value: float | None,
        execution_side: str,
    ) -> str:
        if dar_value is None:
            return "UNDETERMINED"

        if dar_value > 0:
            return "ASK"

        if dar_value < 0:
            return "BID"

        # No directional absorption differential.
        if execution_side == "BUY":
            return "BID"

        if execution_side == "SELL":
            return "ASK"

        return "BALANCED"

    # ------------------------------------------------------------------
    # SECTION / FIELD ACCESS
    # ------------------------------------------------------------------

    @staticmethod
    def _section(
        data: Mapping[str, Any],
        name: str,
    ) -> Mapping[str, Any]:
        section = data.get(name)

        if section is None:
            return data

        if not isinstance(section, Mapping):
            raise TypeError(
                f"OXE '{name}' section must be a mapping"
            )

        return section

    @classmethod
    def _required_non_negative(
        cls,
        data: Mapping[str, Any],
        keys: Sequence[str],
        name: str,
    ) -> float:
        value = cls._first(data, keys)

        if value is None:
            raise ValueError(
                f"OXE requires {name}"
            )

        return cls.non_negative(
            value,
            name=name,
        )

    @classmethod
    def _required_numeric(
        cls,
        data: Mapping[str, Any],
        keys: Sequence[str],
        name: str,
    ) -> float:
        value = cls._first(data, keys)

        if value is None:
            raise ValueError(
                f"OXE requires {name}"
            )

        return cls.numeric(
            value,
            name=name,
            allow_negative=True,
        )

    @classmethod
    def _required_positive(
        cls,
        data: Mapping[str, Any],
        keys: Sequence[str],
        name: str,
    ) -> float:
        value = cls._first(data, keys)

        if value is None:
            raise ValueError(
                f"OXE requires {name}"
            )

        return cls.positive(
            value,
            name=name,
        )

    @staticmethod
    def _first(
        data: Mapping[str, Any],
        keys: Sequence[str],
    ) -> Any:
        for key in keys:
            if key in data and data[key] is not None:
                return data[key]

        return None

    # ------------------------------------------------------------------
    # TIMESTAMP / METADATA
    # ------------------------------------------------------------------

    @classmethod
    def _extract_timestamp(
        cls,
        root: Mapping[str, Any],
        *sections: Mapping[str, Any],
    ) -> datetime:
        keys = (
            "timestamp",
            "observed_at",
            "trade_timestamp",
            "time",
        )

        candidates = [root, *sections]

        for section in candidates:
            value = cls._first(section, keys)

            if value is not None:
                return cls._coerce_timestamp(value)

        raise ValueError(
            "OXE requires an observation timestamp"
        )

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
                    f"Invalid OXE timestamp: {value!r}"
                ) from exc

        else:
            raise TypeError(
                "OXE timestamp must be datetime or ISO-8601 string"
            )

        if (
            timestamp.tzinfo is None
            or timestamp.utcoffset() is None
        ):
            raise ValueError(
                "OXE timestamp must be timezone-aware"
            )

        return timestamp

    @staticmethod
    def _unit(
        root: Mapping[str, Any],
        section: Mapping[str, Any],
        key: str,
        default: str,
    ) -> str:
        value = section.get(
            key,
            root.get(key),
        )

        if value is None:
            return default

        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"{key} must be a non-empty string"
            )

        return value.strip()

    @staticmethod
    def _observation_count(
        root: Mapping[str, Any],
        *sections: Mapping[str, Any],
    ) -> int:
        value = root.get("observation_count")

        if value is not None:
            if not isinstance(value, int) or value <= 0:
                raise ValueError(
                    "observation_count must be a positive integer"
                )
            return value

        for section in sections:
            value = section.get("observation_count")

            if value is not None:
                if not isinstance(value, int) or value <= 0:
                    raise ValueError(
                        "observation_count must be a positive integer"
                    )
                return value

        return 1

    # ------------------------------------------------------------------
    # FINITE CHECK
    # ------------------------------------------------------------------

    @staticmethod
    def _finite(value: float) -> bool:
        return isfinite(value)


# ----------------------------------------------------------------------
# COMPATIBILITY ALIASES
# ----------------------------------------------------------------------

OrderFlowExecutionEngine = OXEEngine
OrderExecutionObstacleEngine = OXEEngine


__all__ = [
    "OXEMetrics",
    "OXEEngine",
    "OrderFlowExecutionEngine",
    "OrderExecutionObstacleEngine",
]