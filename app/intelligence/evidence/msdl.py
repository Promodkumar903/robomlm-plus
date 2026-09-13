"""
ROBOMLM_PLUS
Evidence Cortex — MSDL
-----------------------

MSDL = Market Structure Depth & Liquidity

Purpose
-------
Convert an observed order book into mathematically traceable
depth/liquidity evidence.

Engineering contract
--------------------
RAW ORDER BOOK
    ↓
VALIDATION
    ↓
DEPTH CALCULATION
    ↓
PRICE-LEVEL WEIGHTING
    ↓
SPREAD CALCULATION
    ↓
NORMALIZATION
    ↓
LIQUIDITY EVIDENCE
    ↓
TRACE / LINEAGE

Important
---------
This engine does NOT:
- invent missing depth
- create fake liquidity
- assign arbitrary confidence
- manufacture a 0-100 score
- assume a market-specific calibration
- treat missing resilience data as zero
- convert absent observations into neutral evidence

The underlying research defines liquidity as a multidimensional
quantity consisting of:
    L_depth
    L_spread
    L_resilience

with a combined form:

    L(T) = α L_depth(T)
         + β L_spread(T)
         + γ L_resilience(T)

The present MSDL implementation calculates the OBSERVABLE
depth and spread components. Resilience is only calculated when
time-series liquidity observations are explicitly supplied.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite
from typing import Any, Mapping, Optional, Sequence

from .evidence_engine_base import (
    CalculationStep,
    Evidence,
    EvidenceEngineBase,
    EvidenceStatus,
)


@dataclass(frozen=True)
class DepthLevel:
    """
    One observed order-book price level.

    side:
        BID or ASK

    price:
        Absolute price of the level.

    volume:
        Available quantity at that level.

    level:
        Distance/order-book rank from the best price.
        level=0 means the best available level.

    observed_at:
        Observation timestamp.
    """

    side: str
    price: float
    volume: float
    level: int
    observed_at: Any


@dataclass(frozen=True)
class MSDLResult:
    """Immutable mathematical result returned by MSDL."""

    status: EvidenceStatus

    bid_depth: Optional[float]
    ask_depth: Optional[float]
    total_depth: Optional[float]

    weighted_bid_depth: Optional[float]
    weighted_ask_depth: Optional[float]
    weighted_depth: Optional[float]

    bid_depth_share: Optional[float]
    ask_depth_share: Optional[float]
    depth_imbalance: Optional[float]

    best_bid: Optional[float]
    best_ask: Optional[float]
    spread: Optional[float]
    relative_spread: Optional[float]
    spread_liquidity: Optional[float]

    depth_normalized: Optional[float]
    liquidity_observable: Optional[float]

    level_count: int
    bid_level_count: int
    ask_level_count: int

    decay_parameter: float
    reason: Optional[str] = None


class MSDLInvalidInput(ValueError):
    """Raised when MSDL receives structurally invalid observations."""


class MSDLEngine(EvidenceEngineBase):
    """
    Market Structure Depth & Liquidity engine.

    Mathematical definitions
    ------------------------

    Weighted depth:

        L_depth_raw
            = Σ (BidVolume_i + AskVolume_i) * exp(-γ i)

    Bid weighted depth:

        B_w = Σ BidVolume_i * exp(-γ i)

    Ask weighted depth:

        A_w = Σ AskVolume_i * exp(-γ i)

    Depth imbalance:

        D_imbalance
            = (B_w - A_w) / (B_w + A_w)

    Spread:

        S = Ask_best - Bid_best

    Relative spread:

        S_rel = S / Mid

    where:

        Mid = (Ask_best + Bid_best) / 2

    Spread liquidity:

        L_spread = 1 / (1 + S_rel)

    Observable liquidity:

        L_obs
            = normalized_depth * L_spread

    This observable product is intentionally NOT presented as the
    final three-component liquidity equation because resilience
    requires time-series observations and must not be fabricated.
    """

    ENGINE_NAME = "MSDL"
    LAYER = "L003"

    def __init__(
        self,
        *,
        decay_parameter: float = 0.25,
        depth_reference: Optional[float] = None,
    ) -> None:
        super().__init__()

        if not isfinite(decay_parameter):
            raise ValueError("decay_parameter must be finite")

        if decay_parameter < 0.0:
            raise ValueError("decay_parameter must be >= 0")

        if depth_reference is not None:
            if not isfinite(depth_reference):
                raise ValueError("depth_reference must be finite")
            if depth_reference <= 0.0:
                raise ValueError("depth_reference must be > 0")

        self.decay_parameter = float(decay_parameter)
        self.depth_reference = (
            float(depth_reference)
            if depth_reference is not None
            else None
        )

    # ------------------------------------------------------------------
    # Public calculation
    # ------------------------------------------------------------------

    def calculate(self, data: Mapping[str, Any]) -> MSDLResult:
        levels = self._extract_levels(data)

        if not levels:
            return MSDLResult(
                status=EvidenceStatus.INSUFFICIENT,
                bid_depth=None,
                ask_depth=None,
                total_depth=None,
                weighted_bid_depth=None,
                weighted_ask_depth=None,
                weighted_depth=None,
                bid_depth_share=None,
                ask_depth_share=None,
                depth_imbalance=None,
                best_bid=None,
                best_ask=None,
                spread=None,
                relative_spread=None,
                spread_liquidity=None,
                depth_normalized=None,
                liquidity_observable=None,
                level_count=0,
                bid_level_count=0,
                ask_level_count=0,
                decay_parameter=self.decay_parameter,
                reason="No order-book depth observations supplied",
            )

        self._validate_levels(levels)

        bids = [x for x in levels if x.side == "BID"]
        asks = [x for x in levels if x.side == "ASK"]

        bid_depth = sum(x.volume for x in bids)
        ask_depth = sum(x.volume for x in asks)
        total_depth = bid_depth + ask_depth

        weighted_bid_depth = self._weighted_depth(bids)
        weighted_ask_depth = self._weighted_depth(asks)
        weighted_depth = weighted_bid_depth + weighted_ask_depth

        depth_denominator = weighted_depth

        if depth_denominator > 0.0:
            bid_depth_share = (
                weighted_bid_depth / depth_denominator
            )
            ask_depth_share = (
                weighted_ask_depth / depth_denominator
            )
            depth_imbalance = (
                weighted_bid_depth - weighted_ask_depth
            ) / depth_denominator
        else:
            bid_depth_share = None
            ask_depth_share = None
            depth_imbalance = None

        best_bid = self._best_bid(bids)
        best_ask = self._best_ask(asks)

        spread = None
        relative_spread = None
        spread_liquidity = None

        if best_bid is not None and best_ask is not None:
            if best_ask < best_bid:
                raise MSDLInvalidInput(
                    "Crossed order book: best ask < best bid"
                )

            spread = best_ask - best_bid
            midpoint = (best_bid + best_ask) / 2.0

            if midpoint > 0.0:
                relative_spread = spread / midpoint
                spread_liquidity = 1.0 / (1.0 + relative_spread)

        depth_normalized = self._normalize_depth(weighted_depth)

        liquidity_observable = None

        if (
            depth_normalized is not None
            and spread_liquidity is not None
        ):
            liquidity_observable = (
                depth_normalized * spread_liquidity
            )

        status = EvidenceStatus.VALID

        if not bids or not asks:
            status = EvidenceStatus.PARTIAL

        if best_bid is None or best_ask is None:
            status = EvidenceStatus.PARTIAL

        return MSDLResult(
            status=status,
            bid_depth=bid_depth,
            ask_depth=ask_depth,
            total_depth=total_depth,
            weighted_bid_depth=weighted_bid_depth,
            weighted_ask_depth=weighted_ask_depth,
            weighted_depth=weighted_depth,
            bid_depth_share=bid_depth_share,
            ask_depth_share=ask_depth_share,
            depth_imbalance=depth_imbalance,
            best_bid=best_bid,
            best_ask=best_ask,
            spread=spread,
            relative_spread=relative_spread,
            spread_liquidity=spread_liquidity,
            depth_normalized=depth_normalized,
            liquidity_observable=liquidity_observable,
            level_count=len(levels),
            bid_level_count=len(bids),
            ask_level_count=len(asks),
            decay_parameter=self.decay_parameter,
            reason=(
                "Complete bid/ask book"
                if status == EvidenceStatus.VALID
                else "Partial order-book observation"
            ),
        )

    # ------------------------------------------------------------------
    # Evidence-producing interface
    # ------------------------------------------------------------------

    def process(self, data: Mapping[str, Any]) -> list[Evidence]:
        result = self.calculate(data)

        observed_at = self._observation_timestamp(data)

        if result.status == EvidenceStatus.INSUFFICIENT:
            return [
                self.insufficient(
                    metric="MSDL",
                    observed_at=observed_at,
                    reason=result.reason or "Insufficient order-book data",
                    inputs=self._safe_inputs(data),
                )
            ]

        evidence: list[Evidence] = []

        common_inputs = {
            "decay_parameter": result.decay_parameter,
            "level_count": result.level_count,
            "bid_level_count": result.bid_level_count,
            "ask_level_count": result.ask_level_count,
        }

        evidence.append(
            self.make_evidence(
                metric="weighted_depth",
                value=result.weighted_depth,
                unit="volume",
                status=result.status,
                observed_at=observed_at,
                inputs=common_inputs,
                calculation=(
                    CalculationStep(
                        name="weighted_depth",
                        formula=(
                            "Σ(volume_i * exp(-γ * level_i))"
                        ),
                        inputs={
                            "decay_parameter": result.decay_parameter,
                            "levels": result.level_count,
                        },
                        output=result.weighted_depth,
                    ),
                ),
            )
        )

        evidence.append(
            self.make_evidence(
                metric="depth_imbalance",
                value=result.depth_imbalance,
                unit="ratio",
                status=(
                    result.status
                    if result.depth_imbalance is not None
                    else EvidenceStatus.PARTIAL
                ),
                observed_at=observed_at,
                inputs={
                    "weighted_bid_depth": result.weighted_bid_depth,
                    "weighted_ask_depth": result.weighted_ask_depth,
                },
                calculation=(
                    CalculationStep(
                        name="depth_imbalance",
                        formula=(
                            "(weighted_bid_depth - "
                            "weighted_ask_depth) / "
                            "(weighted_bid_depth + weighted_ask_depth)"
                        ),
                        inputs={
                            "weighted_bid_depth":
                                result.weighted_bid_depth,
                            "weighted_ask_depth":
                                result.weighted_ask_depth,
                        },
                        output=result.depth_imbalance,
                    ),
                ),
            )
        )

        evidence.append(
            self.make_evidence(
                metric="spread",
                value=result.spread,
                unit="price",
                status=(
                    result.status
                    if result.spread is not None
                    else EvidenceStatus.PARTIAL
                ),
                observed_at=observed_at,
                inputs={
                    "best_bid": result.best_bid,
                    "best_ask": result.best_ask,
                },
                calculation=(
                    CalculationStep(
                        name="spread",
                        formula="best_ask - best_bid",
                        inputs={
                            "best_bid": result.best_bid,
                            "best_ask": result.best_ask,
                        },
                        output=result.spread,
                    ),
                ),
            )
        )

        evidence.append(
            self.make_evidence(
                metric="relative_spread",
                value=result.relative_spread,
                unit="ratio",
                status=(
                    EvidenceStatus.VALID
                    if result.relative_spread is not None
                    else EvidenceStatus.PARTIAL
                ),
                observed_at=observed_at,
                inputs={
                    "spread": result.spread,
                    "midpoint": (
                        (
                            result.best_bid + result.best_ask
                        ) / 2.0
                        if (
                            result.best_bid is not None
                            and result.best_ask is not None
                        )
                        else None
                    ),
                },
                calculation=(
                    CalculationStep(
                        name="relative_spread",
                        formula="spread / midpoint",
                        inputs={
                            "spread": result.spread,
                        },
                        output=result.relative_spread,
                    ),
                ),
            )
        )

        evidence.append(
            self.make_evidence(
                metric="spread_liquidity",
                value=result.spread_liquidity,
                unit="ratio",
                status=(
                    EvidenceStatus.VALID
                    if result.spread_liquidity is not None
                    else EvidenceStatus.PARTIAL
                ),
                observed_at=observed_at,
                inputs={
                    "relative_spread": result.relative_spread,
                },
                calculation=(
                    CalculationStep(
                        name="spread_liquidity",
                        formula="1 / (1 + relative_spread)",
                        inputs={
                            "relative_spread":
                                result.relative_spread,
                        },
                        output=result.spread_liquidity,
                    ),
                ),
            )
        )

        evidence.append(
            self.make_evidence(
                metric="depth_normalized",
                value=result.depth_normalized,
                unit="ratio",
                status=(
                    EvidenceStatus.VALID
                    if result.depth_normalized is not None
                    else EvidenceStatus.PARTIAL
                ),
                observed_at=observed_at,
                inputs={
                    "weighted_depth": result.weighted_depth,
                    "depth_reference": self.depth_reference,
                },
                calculation=(
                    CalculationStep(
                        name="depth_normalization",
                        formula=(
                            "weighted_depth / "
                            "(weighted_depth + depth_reference)"
                        ),
                        inputs={
                            "weighted_depth":
                                result.weighted_depth,
                            "depth_reference":
                                self.depth_reference,
                        },
                        output=result.depth_normalized,
                    ),
                ),
            )
        )

        evidence.append(
            self.make_evidence(
                metric="MSDL",
                value=result.liquidity_observable,
                unit="ratio",
                status=(
                    EvidenceStatus.VALID
                    if result.liquidity_observable is not None
                    else EvidenceStatus.PARTIAL
                ),
                observed_at=observed_at,
                inputs={
                    "depth_normalized":
                        result.depth_normalized,
                    "spread_liquidity":
                        result.spread_liquidity,
                },
                calculation=(
                    CalculationStep(
                        name="observable_liquidity",
                        formula=(
                            "depth_normalized * "
                            "spread_liquidity"
                        ),
                        inputs={
                            "depth_normalized":
                                result.depth_normalized,
                            "spread_liquidity":
                                result.spread_liquidity,
                        },
                        output=result.liquidity_observable,
                    ),
                ),
                reason=(
                    "Observable depth/spread liquidity only; "
                    "resilience intentionally excluded unless "
                    "time-series liquidity observations exist"
                ),
            )
        )

        return evidence

    # ------------------------------------------------------------------
    # Depth mathematics
    # ------------------------------------------------------------------

    def _weighted_depth(
        self,
        levels: Sequence[DepthLevel],
    ) -> float:
        total = 0.0

        for item in levels:
            weight = exp(
                -self.decay_parameter * float(item.level)
            )
            total += item.volume * weight

        return total

    def _normalize_depth(
        self,
        weighted_depth: float,
    ) -> Optional[float]:
        if weighted_depth < 0.0:
            raise MSDLInvalidInput(
                "Weighted depth cannot be negative"
            )

        if self.depth_reference is not None:
            return (
                weighted_depth
                / (weighted_depth + self.depth_reference)
            )

        # Without an external reference, the absolute depth
        # cannot be transformed into a dimensionless normalized
        # quantity without introducing an arbitrary scale.
        return None

    # ------------------------------------------------------------------
    # Book geometry
    # ------------------------------------------------------------------

    @staticmethod
    def _best_bid(
        bids: Sequence[DepthLevel],
    ) -> Optional[float]:
        if not bids:
            return None

        return max(item.price for item in bids)

    @staticmethod
    def _best_ask(
        asks: Sequence[DepthLevel],
    ) -> Optional[float]:
        if not asks:
            return None

        return min(item.price for item in asks)

    # ------------------------------------------------------------------
    # Input handling
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_levels(
        data: Mapping[str, Any],
    ) -> list[DepthLevel]:
        raw_levels = data.get("levels")

        if raw_levels is None:
            raw_levels = []

            for item in data.get("bids", []) or []:
                if isinstance(item, Mapping):
                    raw_levels.append(
                        {
                            "side": "BID",
                            **item,
                        }
                    )
                else:
                    raw_levels.append(
                        {
                            "side": "BID",
                            "price": item[0],
                            "volume": item[1],
                            "level": len(raw_levels),
                            "observed_at": data.get(
                                "timestamp"
                            ),
                        }
                    )

            for item in data.get("asks", []) or []:
                if isinstance(item, Mapping):
                    raw_levels.append(
                        {
                            "side": "ASK",
                            **item,
                        }
                    )
                else:
                    raw_levels.append(
                        {
                            "side": "ASK",
                            "price": item[0],
                            "volume": item[1],
                            "level": len(raw_levels),
                            "observed_at": data.get(
                                "timestamp"
                            ),
                        }
                    )

        levels: list[DepthLevel] = []

        for index, item in enumerate(raw_levels):
            if not isinstance(item, Mapping):
                raise MSDLInvalidInput(
                    f"Level {index} must be a mapping"
                )

            levels.append(
                DepthLevel(
                    side=str(item["side"]).upper(),
                    price=float(item["price"]),
                    volume=float(item["volume"]),
                    level=int(
                        item.get("level", index)
                    ),
                    observed_at=item.get(
                        "observed_at",
                        data.get("timestamp"),
                    ),
                )
            )

        return levels

    @staticmethod
    def _validate_levels(
        levels: Sequence[DepthLevel],
    ) -> None:
        for index, item in enumerate(levels):
            if item.side not in {"BID", "ASK"}:
                raise MSDLInvalidInput(
                    f"Invalid side at level {index}: "
                    f"{item.side!r}"
                )

            if not isfinite(item.price):
                raise MSDLInvalidInput(
                    f"Non-finite price at level {index}"
                )

            if item.price <= 0.0:
                raise MSDLInvalidInput(
                    f"Price must be > 0 at level {index}"
                )

            if not isfinite(item.volume):
                raise MSDLInvalidInput(
                    f"Non-finite volume at level {index}"
                )

            if item.volume < 0.0:
                raise MSDLInvalidInput(
                    f"Volume cannot be negative at level {index}"
                )

            if item.level < 0:
                raise MSDLInvalidInput(
                    f"Level index cannot be negative at level {index}"
                )

    @staticmethod
    def _observation_timestamp(
        data: Mapping[str, Any],
    ) -> Any:
        timestamp = data.get("timestamp")

        if timestamp is not None:
            return timestamp

        for item in data.get("levels", []) or []:
            if isinstance(item, Mapping):
                ts = item.get("observed_at")
                if ts is not None:
                    return ts

        return None

    @staticmethod
    def _safe_inputs(
        data: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        return {
            "has_levels": bool(data.get("levels")),
            "bid_count": len(data.get("bids", []) or []),
            "ask_count": len(data.get("asks", []) or []),
        }


# ----------------------------------------------------------------------
# Compatibility aliases
# ----------------------------------------------------------------------

MarketStructureDepthLiquidityEngine = MSDLEngine
MarketDepthLiquidityEngine = MSDLEngine


__all__ = [
    "DepthLevel",
    "MSDLResult",
    "MSDLInvalidInput",
    "MSDLEngine",
    "MarketStructureDepthLiquidityEngine",
    "MarketDepthLiquidityEngine",
]