"""
ROBOMLM_PLUS
Evidence Cortex — MBC
----------------------

MBC = Market Balance / Commitment Evidence

Purpose
-------
Measure the balance between observed aggressive execution and the
available passive order-book depth.

MBC is a derived market-balance observation. It does NOT convert
market conditions into an arbitrary 0-100 score.

Core quantities
---------------

1. Aggressive execution:

    A = BuyAggressive + SellAggressive

2. Passive depth:

    D = BidDepth + AskDepth

3. Aggressive-flow balance:

    B_flow =
        (BuyAggressive - SellAggressive)
        / (BuyAggressive + SellAggressive)

4. Passive-depth balance:

    B_depth =
        (BidDepth - AskDepth)
        / (BidDepth + AskDepth)

5. Flow/depth balance differential:

    MBC = B_flow - B_depth

Interpretation is descriptive only:

    MBC > 0  -> aggressive flow is more buy-dominant
                relative to displayed depth balance

    MBC < 0  -> aggressive flow is more sell-dominant
                relative to displayed depth balance

    MBC = 0  -> the two normalized balances are equal

No:
- hardcoded confidence
- arbitrary weights
- fake liquidity
- guessed depth
- probability generation
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
class MBCMetrics:
    aggressive_buy_volume: float
    aggressive_sell_volume: float

    bid_depth: float
    ask_depth: float

    total_aggressive_volume: float
    total_displayed_depth: float

    flow_balance: float | None
    depth_balance: float | None

    mbc: float | None

    buy_flow_share: float | None
    sell_flow_share: float | None

    bid_depth_share: float | None
    ask_depth_share: float | None

    observation_count: int
    status: EvidenceStatus

    observed_at: datetime

    volume_unit: str


class MBCEngine(EvidenceEngineBase):
    """
    Market Balance / Commitment Evidence engine.

    Expected input:

        {
            "aggressive_buy_volume": 120,
            "aggressive_sell_volume": 80,

            "bid_depth": 500,
            "ask_depth": 400,

            "timestamp": "...",
            "volume_unit": "shares"
        }

    Nested evidence sections are also accepted:

        {
            "ned": {...},
            "dar": {...},
            "timestamp": "..."
        }

    If NED/DAR sections are present, the raw components are extracted
    from them. The engine does not rely on an already-calculated MBC
    value.
    """

    ENGINE_NAME = "MBC"
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

    def calculate(
        self,
        data: Mapping[str, Any],
    ) -> tuple[Evidence, ...]:
        metrics = self.compute(data)

        common_inputs = {
            "aggressive_buy_volume":
                metrics.aggressive_buy_volume,
            "aggressive_sell_volume":
                metrics.aggressive_sell_volume,
            "bid_depth":
                metrics.bid_depth,
            "ask_depth":
                metrics.ask_depth,
            "total_aggressive_volume":
                metrics.total_aggressive_volume,
            "total_displayed_depth":
                metrics.total_displayed_depth,
            "flow_balance":
                metrics.flow_balance,
            "depth_balance":
                metrics.depth_balance,
            "observation_count":
                metrics.observation_count,
        }

        return (
            self.make_evidence(
                metric="flow_balance",
                value=metrics.flow_balance,
                unit="ratio",
                status=(
                    metrics.status
                    if metrics.flow_balance is not None
                    else EvidenceStatus.INSUFFICIENT
                ),
                observed_at=metrics.observed_at,
                source=data.get("source"),
                source_type=data.get("source_type"),
                inputs=common_inputs,
                calculation=(
                    CalculationStep(
                        name="aggressive_flow_balance",
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
                        output=metrics.flow_balance,
                    ),
                ),
                reason=(
                    "Normalized aggressive execution balance."
                    if metrics.flow_balance is not None
                    else "No aggressive volume was available."
                ),
            ),

            self.make_evidence(
                metric="depth_balance",
                value=metrics.depth_balance,
                unit="ratio",
                status=(
                    metrics.status
                    if metrics.depth_balance is not None
                    else EvidenceStatus.INSUFFICIENT
                ),
                observed_at=metrics.observed_at,
                source=data.get("source"),
                source_type=data.get("source_type"),
                inputs=common_inputs,
                calculation=(
                    CalculationStep(
                        name="passive_depth_balance",
                        formula=(
                            "(bid_depth - ask_depth) "
                            "/ "
                            "(bid_depth + ask_depth)"
                        ),
                        inputs={
                            "bid_depth": metrics.bid_depth,
                            "ask_depth": metrics.ask_depth,
                        },
                        output=metrics.depth_balance,
                    ),
                ),
                reason=(
                    "Normalized displayed bid/ask depth balance."
                    if metrics.depth_balance is not None
                    else "Total displayed depth is zero."
                ),
            ),

            self.make_evidence(
                metric="mbc",
                value=metrics.mbc,
                unit="ratio",
                status=(
                    metrics.status
                    if metrics.mbc is not None
                    else EvidenceStatus.INSUFFICIENT
                ),
                observed_at=metrics.observed_at,
                source=data.get("source"),
                source_type=data.get("source_type"),
                inputs=common_inputs,
                calculation=(
                    CalculationStep(
                        name="market_balance_commitment",
                        formula=(
                            "flow_balance - depth_balance"
                        ),
                        inputs={
                            "flow_balance":
                                metrics.flow_balance,
                            "depth_balance":
                                metrics.depth_balance,
                        },
                        output=metrics.mbc,
                    ),
                ),
                reason=(
                    "Difference between normalized aggressive-flow "
                    "balance and displayed-depth balance."
                    if metrics.mbc is not None
                    else "Both flow and depth balances are required."
                ),
            ),

            self.make_evidence(
                metric="buy_flow_share",
                value=metrics.buy_flow_share,
                unit="ratio",
                status=(
                    EvidenceStatus.VALID
                    if metrics.buy_flow_share is not None
                    else EvidenceStatus.INSUFFICIENT
                ),
                observed_at=metrics.observed_at,
                source=data.get("source"),
                source_type=data.get("source_type"),
                inputs=common_inputs,
                calculation=(
                    CalculationStep(
                        name="buy_flow_share",
                        formula=(
                            "aggressive_buy_volume "
                            "/ total_aggressive_volume"
                        ),
                        inputs={
                            "aggressive_buy_volume":
                                metrics.aggressive_buy_volume,
                            "total_aggressive_volume":
                                metrics.total_aggressive_volume,
                        },
                        output=metrics.buy_flow_share,
                    ),
                ),
                reason=(
                    "Share of classified aggressive flow executed "
                    "on the buy side."
                    if metrics.buy_flow_share is not None
                    else "Total aggressive volume is zero."
                ),
            ),

            self.make_evidence(
                metric="sell_flow_share",
                value=metrics.sell_flow_share,
                unit="ratio",
                status=(
                    EvidenceStatus.VALID
                    if metrics.sell_flow_share is not None
                    else EvidenceStatus.INSUFFICIENT
                ),
                observed_at=metrics.observed_at,
                source=data.get("source"),
                source_type=data.get("source_type"),
                inputs=common_inputs,
                calculation=(
                    CalculationStep(
                        name="sell_flow_share",
                        formula=(
                            "aggressive_sell_volume "
                            "/ total_aggressive_volume"
                        ),
                        inputs={
                            "aggressive_sell_volume":
                                metrics.aggressive_sell_volume,
                            "total_aggressive_volume":
                                metrics.total_aggressive_volume,
                        },
                        output=metrics.sell_flow_share,
                    ),
                ),
                reason=(
                    "Share of classified aggressive flow executed "
                    "on the sell side."
                    if metrics.sell_flow_share is not None
                    else "Total aggressive volume is zero."
                ),
            ),

            self.make_evidence(
                metric="bid_depth_share",
                value=metrics.bid_depth_share,
                unit="ratio",
                status=(
                    EvidenceStatus.VALID
                    if metrics.bid_depth_share is not None
                    else EvidenceStatus.INSUFFICIENT
                ),
                observed_at=metrics.observed_at,
                source=data.get("source"),
                source_type=data.get("source_type"),
                inputs=common_inputs,
                calculation=(
                    CalculationStep(
                        name="bid_depth_share",
                        formula=(
                            "bid_depth / total_displayed_depth"
                        ),
                        inputs={
                            "bid_depth": metrics.bid_depth,
                            "total_displayed_depth":
                                metrics.total_displayed_depth,
                        },
                        output=metrics.bid_depth_share,
                    ),
                ),
                reason=(
                    "Displayed bid depth share."
                    if metrics.bid_depth_share is not None
                    else "Total displayed depth is zero."
                ),
            ),

            self.make_evidence(
                metric="ask_depth_share",
                value=metrics.ask_depth_share,
                unit="ratio",
                status=(
                    EvidenceStatus.VALID
                    if metrics.ask_depth_share is not None
                    else EvidenceStatus.INSUFFICIENT
                ),
                observed_at=metrics.observed_at,
                source=data.get("source"),
                source_type=data.get("source_type"),
                inputs=common_inputs,
                calculation=(
                    CalculationStep(
                        name="ask_depth_share",
                        formula=(
                            "ask_depth / total_displayed_depth"
                        ),
                        inputs={
                            "ask_depth": metrics.ask_depth,
                            "total_displayed_depth":
                                metrics.total_displayed_depth,
                        },
                        output=metrics.ask_depth_share,
                    ),
                ),
                reason=(
                    "Displayed ask depth share."
                    if metrics.ask_depth_share is not None
                    else "Total displayed depth is zero."
                ),
            ),
        )

    # ------------------------------------------------------------------
    # CORE CALCULATION
    # ------------------------------------------------------------------

    def compute(
        self,
        data: Mapping[str, Any],
    ) -> MBCMetrics:
        ned = self._section(data, "ned")
        dar = self._section(data, "dar")

        buy_volume = self._required_non_negative(
            ned,
            self._BUY_KEYS,
            "aggressive_buy_volume",
        )

        sell_volume = self._required_non_negative(
            ned,
            self._SELL_KEYS,
            "aggressive_sell_volume",
        )

        bid_depth = self._required_non_negative(
            dar,
            self._BID_DEPTH_KEYS,
            "bid_depth",
        )

        ask_depth = self._required_non_negative(
            dar,
            self._ASK_DEPTH_KEYS,
            "ask_depth",
        )

        total_aggressive_volume = (
            buy_volume + sell_volume
        )

        total_displayed_depth = (
            bid_depth + ask_depth
        )

        flow_balance = (
            (buy_volume - sell_volume)
            / total_aggressive_volume
            if total_aggressive_volume > 0
            else None
        )

        depth_balance = (
            (bid_depth - ask_depth)
            / total_displayed_depth
            if total_displayed_depth > 0
            else None
        )

        mbc = (
            flow_balance - depth_balance
            if flow_balance is not None
            and depth_balance is not None
            else None
        )

        buy_flow_share = (
            buy_volume / total_aggressive_volume
            if total_aggressive_volume > 0
            else None
        )

        sell_flow_share = (
            sell_volume / total_aggressive_volume
            if total_aggressive_volume > 0
            else None
        )

        bid_depth_share = (
            bid_depth / total_displayed_depth
            if total_displayed_depth > 0
            else None
        )

        ask_depth_share = (
            ask_depth / total_displayed_depth
            if total_displayed_depth > 0
            else None
        )

        observed_at = self._extract_timestamp(
            data,
            ned,
            dar,
        )

        volume_unit = self._unit(
            data,
            ned,
            "volume_unit",
            "native_volume",
        )

        status = (
            EvidenceStatus.VALID
            if mbc is not None
            else EvidenceStatus.PARTIAL
        )

        return MBCMetrics(
            aggressive_buy_volume=buy_volume,
            aggressive_sell_volume=sell_volume,
            bid_depth=bid_depth,
            ask_depth=ask_depth,
            total_aggressive_volume=total_aggressive_volume,
            total_displayed_depth=total_displayed_depth,
            flow_balance=flow_balance,
            depth_balance=depth_balance,
            mbc=mbc,
            buy_flow_share=buy_flow_share,
            sell_flow_share=sell_flow_share,
            bid_depth_share=bid_depth_share,
            ask_depth_share=ask_depth_share,
            observation_count=self._observation_count(
                data,
                ned,
                dar,
            ),
            status=status,
            observed_at=observed_at,
            volume_unit=volume_unit,
        )

    # ------------------------------------------------------------------
    # INPUT SECTIONS
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
                f"MBC '{name}' section must be a mapping"
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
                f"MBC requires {name}"
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
    # METADATA
    # ------------------------------------------------------------------

    @classmethod
    def _extract_timestamp(
        cls,
        root: Mapping[str, Any],
        *sections: Mapping[str, Any],
    ) -> datetime:
        for section in (root, *sections):
            value = cls._first(
                section,
                cls._TIMESTAMP_KEYS,
            )

            if value is not None:
                return cls._coerce_timestamp(value)

        raise ValueError(
            "MBC requires an observation timestamp"
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
                    f"Invalid MBC timestamp: {value!r}"
                ) from exc

        else:
            raise TypeError(
                "MBC timestamp must be datetime or ISO-8601 string"
            )

        if (
            timestamp.tzinfo is None
            or timestamp.utcoffset() is None
        ):
            raise ValueError(
                "MBC timestamp must be timezone-aware"
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
        for section in (root, *sections):
            value = section.get("observation_count")

            if value is not None:
                if not isinstance(value, int) or value <= 0:
                    raise ValueError(
                        "observation_count must be a positive integer"
                    )

                return value

        return 1


# ----------------------------------------------------------------------
# COMPATIBILITY ALIASES
# ----------------------------------------------------------------------

MarketBalanceEngine = MBCEngine
MarketBalanceCommitmentEngine = MBCEngine


__all__ = [
    "MBCMetrics",
    "MBCEngine",
    "MarketBalanceEngine",
    "MarketBalanceCommitmentEngine",
]