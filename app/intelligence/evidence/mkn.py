"""
ROBOMLM_PLUS
Evidence Cortex — MKN
----------------------

MKN = Market Knowledge / Market-Node Evidence

Purpose
-------
Convert observed market-node information into mathematically explicit
structure without manufacturing a score.

A market node represents an observed price level together with the
activity accumulated around that level.

Core quantities
---------------

For each price node i:

    node_volume_i = Σ volume of observations at node i

    node_count_i  = number of observations at node i

The engine identifies:

    POC  = price node with maximum observed volume

    V_total = Σ node_volume_i

    V_share_i = node_volume_i / V_total

For a requested value-area fraction α:

    sort nodes by volume descending

    accumulate volume until:

        cumulative_volume >= α * V_total

The selected nodes form the observed value-area set.

No:
- arbitrary market score
- hardcoded confidence
- synthetic volume
- guessed nodes
- probability generation
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
class MarketNode:
    price: float
    volume: float
    observation_count: int
    volume_share: float


@dataclass(frozen=True)
class MKNMetrics:
    nodes: tuple[MarketNode, ...]

    total_volume: float
    node_count: int
    observation_count: int

    poc_price: float | None
    poc_volume: float | None
    poc_volume_share: float | None

    value_area_low: float | None
    value_area_high: float | None
    value_area_volume: float | None
    value_area_share: float | None

    value_area_fraction: float

    min_price: float | None
    max_price: float | None
    volume_weighted_price: float | None

    observed_at: datetime
    status: EvidenceStatus

    price_unit: str
    volume_unit: str


class MKNEngine(EvidenceEngineBase):
    """
    Market Node Evidence engine.

    Input:

        {
            "observations": [
                {
                    "timestamp": ...,
                    "price": 100.0,
                    "volume": 50
                },
                {
                    "timestamp": ...,
                    "price": 101.0,
                    "volume": 80
                }
            ],

            "value_area_fraction": 0.70
        }

    Price nodes may be supplied directly:

        {
            "nodes": [
                {
                    "price": 100,
                    "volume": 500
                },
                {
                    "price": 101,
                    "volume": 700
                }
            ]
        }

    If raw observations are supplied, equal prices are aggregated.

    If a price_increment is supplied, prices are mapped to the nearest
    increment before aggregation.

    The increment is never invented by this engine.
    """

    ENGINE_NAME = "MKN"
    LAYER = "L003"

    _OBSERVATION_KEYS = (
        "observations",
        "ticks",
        "trades",
        "snapshots",
    )

    _NODE_KEYS = (
        "nodes",
        "market_nodes",
        "price_nodes",
    )

    _PRICE_KEYS = (
        "price",
        "trade_price",
        "last_price",
    )

    _VOLUME_KEYS = (
        "volume",
        "trade_volume",
        "qty",
        "quantity",
    )

    _TIMESTAMP_KEYS = (
        "timestamp",
        "observed_at",
        "trade_timestamp",
        "time",
    )

    def __init__(
        self,
        *,
        value_area_fraction: float = 0.70,
        price_increment: float | None = None,
    ) -> None:
        super().__init__()

        if not isfinite(value_area_fraction):
            raise ValueError(
                "value_area_fraction must be finite"
            )

        if not 0.0 < value_area_fraction <= 1.0:
            raise ValueError(
                "value_area_fraction must be > 0 and <= 1"
            )

        if price_increment is not None:
            if not isfinite(float(price_increment)):
                raise ValueError(
                    "price_increment must be finite"
                )

            if float(price_increment) <= 0:
                raise ValueError(
                    "price_increment must be > 0"
                )

        self.value_area_fraction = float(
            value_area_fraction
        )

        self.price_increment = (
            float(price_increment)
            if price_increment is not None
            else None
        )

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def calculate(
        self,
        data: Mapping[str, Any],
    ) -> tuple[Evidence, ...]:
        metrics = self.compute(data)

        common_inputs = {
            "node_count": metrics.node_count,
            "observation_count": metrics.observation_count,
            "total_volume": metrics.total_volume,
            "value_area_fraction":
                metrics.value_area_fraction,
            "price_increment":
                self.price_increment,
            "price_unit":
                metrics.price_unit,
            "volume_unit":
                metrics.volume_unit,
        }

        return (
            self.make_evidence(
                metric="poc_price",
                value=metrics.poc_price,
                unit=metrics.price_unit,
                status=(
                    metrics.status
                    if metrics.poc_price is not None
                    else EvidenceStatus.INSUFFICIENT
                ),
                observed_at=metrics.observed_at,
                source=data.get("source"),
                source_type=data.get("source_type"),
                inputs=common_inputs,
                calculation=(
                    CalculationStep(
                        name="point_of_control",
                        formula=(
                            "argmax_i(node_volume_i)"
                        ),
                        inputs={
                            "node_count": metrics.node_count,
                        },
                        output=metrics.poc_price,
                    ),
                ),
                reason=(
                    "Price node containing the greatest observed "
                    "volume."
                    if metrics.poc_price is not None
                    else "No positive-volume market node exists."
                ),
            ),

            self.make_evidence(
                metric="poc_volume",
                value=metrics.poc_volume,
                unit=metrics.volume_unit,
                status=(
                    metrics.status
                    if metrics.poc_volume is not None
                    else EvidenceStatus.INSUFFICIENT
                ),
                observed_at=metrics.observed_at,
                source=data.get("source"),
                source_type=data.get("source_type"),
                inputs=common_inputs,
                calculation=(
                    CalculationStep(
                        name="poc_volume",
                        formula=(
                            "max(node_volume_i)"
                        ),
                        inputs={
                            "node_count": metrics.node_count,
                        },
                        output=metrics.poc_volume,
                    ),
                ),
                reason=(
                    "Maximum observed volume at a price node."
                    if metrics.poc_volume is not None
                    else "No positive-volume market node exists."
                ),
            ),

            self.make_evidence(
                metric="poc_volume_share",
                value=metrics.poc_volume_share,
                unit="ratio",
                status=(
                    EvidenceStatus.VALID
                    if metrics.poc_volume_share is not None
                    else EvidenceStatus.INSUFFICIENT
                ),
                observed_at=metrics.observed_at,
                source=data.get("source"),
                source_type=data.get("source_type"),
                inputs=common_inputs,
                calculation=(
                    CalculationStep(
                        name="poc_volume_share",
                        formula=(
                            "poc_volume / total_volume"
                        ),
                        inputs={
                            "poc_volume": metrics.poc_volume,
                            "total_volume": metrics.total_volume,
                        },
                        output=metrics.poc_volume_share,
                    ),
                ),
                reason=(
                    "Fraction of observed volume concentrated "
                    "at the POC."
                    if metrics.poc_volume_share is not None
                    else "Total volume is zero."
                ),
            ),

            self.make_evidence(
                metric="value_area_low",
                value=metrics.value_area_low,
                unit=metrics.price_unit,
                status=(
                    metrics.status
                    if metrics.value_area_low is not None
                    else EvidenceStatus.INSUFFICIENT
                ),
                observed_at=metrics.observed_at,
                source=data.get("source"),
                source_type=data.get("source_type"),
                inputs=common_inputs,
                calculation=(
                    CalculationStep(
                        name="value_area_selection",
                        formula=(
                            "lowest_price(selected_nodes)"
                        ),
                        inputs={
                            "target_volume":
                                metrics.total_volume
                                * metrics.value_area_fraction,
                            "selected_node_count":
                                self._value_area_node_count(metrics),
                        },
                        output=metrics.value_area_low,
                    ),
                ),
                reason=(
                    "Lower boundary of the observed value-area set."
                    if metrics.value_area_low is not None
                    else "Value area is undefined without positive volume."
                ),
            ),

            self.make_evidence(
                metric="value_area_high",
                value=metrics.value_area_high,
                unit=metrics.price_unit,
                status=(
                    metrics.status
                    if metrics.value_area_high is not None
                    else EvidenceStatus.INSUFFICIENT
                ),
                observed_at=metrics.observed_at,
                source=data.get("source"),
                source_type=data.get("source_type"),
                inputs=common_inputs,
                calculation=(
                    CalculationStep(
                        name="value_area_selection",
                        formula=(
                            "highest_price(selected_nodes)"
                        ),
                        inputs={
                            "target_volume":
                                metrics.total_volume
                                * metrics.value_area_fraction,
                            "selected_node_count":
                                self._value_area_node_count(metrics),
                        },
                        output=metrics.value_area_high,
                    ),
                ),
                reason=(
                    "Upper boundary of the observed value-area set."
                    if metrics.value_area_high is not None
                    else "Value area is undefined without positive volume."
                ),
            ),

            self.make_evidence(
                metric="value_area_share",
                value=metrics.value_area_share,
                unit="ratio",
                status=(
                    EvidenceStatus.VALID
                    if metrics.value_area_share is not None
                    else EvidenceStatus.INSUFFICIENT
                ),
                observed_at=metrics.observed_at,
                source=data.get("source"),
                source_type=data.get("source_type"),
                inputs=common_inputs,
                calculation=(
                    CalculationStep(
                        name="value_area_share",
                        formula=(
                            "value_area_volume / total_volume"
                        ),
                        inputs={
                            "value_area_volume":
                                metrics.value_area_volume,
                            "total_volume":
                                metrics.total_volume,
                        },
                        output=metrics.value_area_share,
                    ),
                ),
                reason=(
                    "Observed volume contained in the selected "
                    "value-area nodes."
                    if metrics.value_area_share is not None
                    else "Total volume is zero."
                ),
            ),

            self.make_evidence(
                metric="volume_weighted_price",
                value=metrics.volume_weighted_price,
                unit=metrics.price_unit,
                status=(
                    EvidenceStatus.VALID
                    if metrics.volume_weighted_price is not None
                    else EvidenceStatus.INSUFFICIENT
                ),
                observed_at=metrics.observed_at,
                source=data.get("source"),
                source_type=data.get("source_type"),
                inputs=common_inputs,
                calculation=(
                    CalculationStep(
                        name="volume_weighted_price",
                        formula=(
                            "Σ(price_i * volume_i) / Σ(volume_i)"
                        ),
                        inputs={
                            "total_volume":
                                metrics.total_volume,
                        },
                        output=metrics.volume_weighted_price,
                    ),
                ),
                reason=(
                    "Volume-weighted observed market price."
                    if metrics.volume_weighted_price is not None
                    else "Total volume is zero."
                ),
            ),
        )

    # ------------------------------------------------------------------
    # CORE CALCULATION
    # ------------------------------------------------------------------

    def compute(
        self,
        data: Mapping[str, Any],
    ) -> MKNMetrics:
        nodes, observation_count, observed_at = (
            self._build_nodes(data)
        )

        if not nodes:
            raise ValueError(
                "MKN requires at least one market node"
            )

        total_volume = sum(
            node["volume"]
            for node in nodes
        )

        if total_volume <= 0:
            raise ValueError(
                "MKN requires positive total observed volume"
            )

        # Build normalized nodes.
        normalized_nodes = tuple(
            MarketNode(
                price=node["price"],
                volume=node["volume"],
                observation_count=node["observation_count"],
                volume_share=node["volume"] / total_volume,
            )
            for node in nodes
        )

        # POC:
        # deterministic tie-break = lower price.
        poc = max(
            normalized_nodes,
            key=lambda node: (
                node.volume,
                -node.price,
            ),
        )

        value_area_nodes = self._select_value_area(
            normalized_nodes,
            total_volume,
        )

        value_area_volume = sum(
            node.volume
            for node in value_area_nodes
        )

        value_area_share = (
            value_area_volume / total_volume
        )

        min_price = min(
            node.price
            for node in normalized_nodes
        )

        max_price = max(
            node.price
            for node in normalized_nodes
        )

        weighted_price_numerator = sum(
            node.price * node.volume
            for node in normalized_nodes
        )

        volume_weighted_price = (
            weighted_price_numerator / total_volume
        )

        value_area_low = min(
            node.price
            for node in value_area_nodes
        )

        value_area_high = max(
            node.price
            for node in value_area_nodes
        )

        return MKNMetrics(
            nodes=normalized_nodes,
            total_volume=total_volume,
            node_count=len(normalized_nodes),
            observation_count=observation_count,
            poc_price=poc.price,
            poc_volume=poc.volume,
            poc_volume_share=poc.volume_share,
            value_area_low=value_area_low,
            value_area_high=value_area_high,
            value_area_volume=value_area_volume,
            value_area_share=value_area_share,
            value_area_fraction=self.value_area_fraction,
            min_price=min_price,
            max_price=max_price,
            volume_weighted_price=volume_weighted_price,
            observed_at=observed_at,
            status=EvidenceStatus.VALID,
            price_unit=self._unit(
                data,
                "price_unit",
                "native_price",
            ),
            volume_unit=self._unit(
                data,
                "volume_unit",
                "native_volume",
            ),
        )

    # ------------------------------------------------------------------
    # NODE CONSTRUCTION
    # ------------------------------------------------------------------

    def _build_nodes(
        self,
        data: Mapping[str, Any],
    ) -> tuple[
        list[dict[str, Any]],
        int,
        datetime,
    ]:
        supplied_nodes = self._extract_sequence(
            data,
            self._NODE_KEYS,
        )

        if supplied_nodes is not None:
            return self._aggregate_supplied_nodes(
                supplied_nodes,
                data,
            )

        observations = self._extract_sequence(
            data,
            self._OBSERVATION_KEYS,
        )

        if observations is None:
            if self._has_price_volume(data):
                observations = [data]
            else:
                raise ValueError(
                    "MKN requires market nodes or price-volume observations"
                )

        buckets: dict[float, dict[str, Any]] = {}

        timestamps: list[datetime] = []

        for observation in observations:
            if not isinstance(observation, Mapping):
                raise TypeError(
                    "Every MKN observation must be a mapping"
                )

            timestamp_value = self._first(
                observation,
                self._TIMESTAMP_KEYS,
            )

            if timestamp_value is None:
                timestamp_value = self._first(
                    data,
                    self._TIMESTAMP_KEYS,
                )

            if timestamp_value is None:
                raise ValueError(
                    "MKN observations require timestamps"
                )

            timestamp = self._coerce_timestamp(
                timestamp_value
            )

            timestamps.append(timestamp)

            price = self._required_non_negative(
                observation,
                self._PRICE_KEYS,
                "price",
            )

            volume = self._required_non_negative(
                observation,
                self._VOLUME_KEYS,
                "volume",
            )

            price = self._normalize_price(price)

            if price not in buckets:
                buckets[price] = {
                    "price": price,
                    "volume": 0.0,
                    "observation_count": 0,
                }

            buckets[price]["volume"] += volume
            buckets[price]["observation_count"] += 1

        nodes = sorted(
            buckets.values(),
            key=lambda node: node["price"],
        )

        return (
            nodes,
            len(observations),
            max(timestamps),
        )

    def _aggregate_supplied_nodes(
        self,
        supplied_nodes: Sequence[Mapping[str, Any]],
        data: Mapping[str, Any],
    ) -> tuple[
        list[dict[str, Any]],
        int,
        datetime,
    ]:
        buckets: dict[float, dict[str, Any]] = {}

        timestamp_value = self._first(
            data,
            self._TIMESTAMP_KEYS,
        )

        if timestamp_value is None:
            raise ValueError(
                "MKN supplied nodes require an observation timestamp"
            )

        observed_at = self._coerce_timestamp(
            timestamp_value
        )

        for node in supplied_nodes:
            if not isinstance(node, Mapping):
                raise TypeError(
                    "Every MKN node must be a mapping"
                )

            price = self._required_non_negative(
                node,
                self._PRICE_KEYS,
                "node price",
            )

            volume = self._required_non_negative(
                node,
                self._VOLUME_KEYS,
                "node volume",
            )

            price = self._normalize_price(price)

            if price not in buckets:
                buckets[price] = {
                    "price": price,
                    "volume": 0.0,
                    "observation_count": 0,
                }

            buckets[price]["volume"] += volume
            buckets[price]["observation_count"] += int(
                node.get("observation_count", 1)
            )

        nodes = sorted(
            buckets.values(),
            key=lambda node: node["price"],
        )

        return (
            nodes,
            sum(
                node["observation_count"]
                for node in nodes
            ),
            observed_at,
        )

    # ------------------------------------------------------------------
    # VALUE AREA
    # ------------------------------------------------------------------

    def _select_value_area(
        self,
        nodes: Sequence[MarketNode],
        total_volume: float,
    ) -> tuple[MarketNode, ...]:
        target_volume = (
            total_volume * self.value_area_fraction
        )

        # Highest-volume nodes are accumulated first.
        # Deterministic tie-break: lower price first.
        ranked = sorted(
            nodes,
            key=lambda node: (
                -node.volume,
                node.price,
            ),
        )

        selected: list[MarketNode] = []
        cumulative = 0.0

        for node in ranked:
            selected.append(node)
            cumulative += node.volume

            if cumulative >= target_volume:
                break

        return tuple(
            sorted(
                selected,
                key=lambda node: node.price,
            )
        )

    @staticmethod
    def _value_area_node_count(
        metrics: MKNMetrics,
    ) -> int:
        if metrics.total_volume <= 0:
            return 0

        target = (
            metrics.total_volume
            * metrics.value_area_fraction
        )

        cumulative = 0.0
        count = 0

        ranked = sorted(
            metrics.nodes,
            key=lambda node: (
                -node.volume,
                node.price,
            ),
        )

        for node in ranked:
            cumulative += node.volume
            count += 1

            if cumulative >= target:
                break

        return count

    # ------------------------------------------------------------------
    # INPUT HELPERS
    # ------------------------------------------------------------------

    @classmethod
    def _extract_sequence(
        cls,
        data: Mapping[str, Any],
        keys: Sequence[str],
    ) -> Sequence[Mapping[str, Any]] | None:
        for key in keys:
            if key not in data:
                continue

            value = data[key]

            if not isinstance(value, Sequence) or isinstance(
                value,
                (str, bytes, bytearray),
            ):
                raise TypeError(
                    f"'{key}' must be a sequence"
                )

            return value

        return None

    @classmethod
    def _has_price_volume(
        cls,
        data: Mapping[str, Any],
    ) -> bool:
        has_price = any(
            key in data and data[key] is not None
            for key in cls._PRICE_KEYS
        )

        has_volume = any(
            key in data and data[key] is not None
            for key in cls._VOLUME_KEYS
        )

        return has_price and has_volume

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
                f"MKN requires {name}"
            )

        return cls.non_negative(
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
    # PRICE / TIME
    # ------------------------------------------------------------------

    def _normalize_price(
        self,
        price: float,
    ) -> float:
        if self.price_increment is None:
            return price

        # Nearest node using deterministic half-up behavior.
        scaled = price / self.price_increment
        lower = int(scaled)

        remainder = scaled - lower

        if remainder >= 0.5:
            index = lower + 1
        else:
            index = lower

        normalized = (
            index * self.price_increment
        )

        if not isfinite(normalized):
            raise ValueError(
                "MKN price normalization produced non-finite value"
            )

        return normalized

    @classmethod
    def _coerce_timestamp(
        cls,
        value: Any,
    ) -> datetime:
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
                    f"Invalid MKN timestamp: {value!r}"
                ) from exc

        else:
            raise TypeError(
                "MKN timestamp must be datetime or ISO-8601 string"
            )

        if (
            timestamp.tzinfo is None
            or timestamp.utcoffset() is None
        ):
            raise ValueError(
                "MKN timestamp must be timezone-aware"
            )

        return timestamp

    # ------------------------------------------------------------------
    # UNITS
    # ------------------------------------------------------------------

    @staticmethod
    def _unit(
        data: Mapping[str, Any],
        key: str,
        default: str,
    ) -> str:
        value = data.get(key)

        if value is None:
            return default

        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"{key} must be a non-empty string"
            )

        return value.strip()


# ----------------------------------------------------------------------
# COMPATIBILITY ALIASES
# ----------------------------------------------------------------------

MarketNodeEngine = MKNEngine
MarketKnowledgeEngine = MKNEngine


__all__ = [
    "MarketNode",
    "MKNMetrics",
    "MKNEngine",
    "MarketNodeEngine",
    "MarketKnowledgeEngine",
]