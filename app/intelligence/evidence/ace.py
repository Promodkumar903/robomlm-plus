"""
ROBOMLM_PLUS
Evidence Cortex — L003 Market Structure

ACE — Auction Context Engine

Purpose
-------
Derive the current observable auction state from market-structure evidence.

ACE does NOT:
    - create BUY/SELL decisions
    - create confidence scores
    - create arbitrary 0-100 scores
    - replace the Decision Cortex
    - infer missing market information
    - manufacture liquidity/depth

ACE DOES:
    - reconcile directional flow with resting depth
    - identify pressure alignment / opposition
    - quantify price response to executed flow when available
    - identify auction-side structure
    - preserve the mathematical lineage of every derived result

Primary inputs
--------------
NED:
    Net Executed Demand

DAR:
    Depth Absorption Ratio

TV:
    Trade / Price Velocity

MBC:
    Market Balance Commitment

DCS:
    Depth Concentration Structure

MSDL:
    Market Structure Depth & Liquidity

Core mathematical relations
----------------------------

1. Flow pressure

    P_flow =
        (BuyVolume - SellVolume) /
        (BuyVolume + SellVolume)

2. Depth pressure

    P_depth =
        (BidDepth - AskDepth) /
        (BidDepth + AskDepth)

3. Flow-depth alignment

    A_fd = P_flow * P_depth

Interpretation:
    > 0 : flow and resting depth point in same direction
    < 0 : flow and resting depth oppose each other
    = 0 : no measurable directional alignment

4. Flow-response efficiency

    E_fr = ΔP / NED

Only defined when NED != 0 and ΔP is measured over the
same observation interval.

5. Auction pressure differential

    A_diff = P_flow - P_depth

This is a structural difference, not a score.

6. Concentration-adjusted structural pressure

When DCS is available:

    C_struct =
        A_fd * DCS

This preserves DCS's dimensionless concentration information
without converting it to an arbitrary normalized score.

7. Auction classification

Classification is rule-derived from mathematical signs:

    ALIGNED_BID
        P_flow > 0 and P_depth > 0

    ALIGNED_ASK
        P_flow < 0 and P_depth < 0

    FLOW_LEADS_BID
        P_flow > 0 and P_depth <= 0

    FLOW_LEADS_ASK
        P_flow < 0 and P_depth >= 0

    DEPTH_SUPPORTS_BID
        P_depth > 0 and P_flow <= 0

    DEPTH_SUPPORTS_ASK
        P_depth < 0 and P_flow >= 0

    BALANCED
        both pressures == 0

No arbitrary threshold is used.

The engine reports observable auction structure only.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Mapping, Optional, Sequence

from .evidence_engine_base import (
    CalculationStep,
    Evidence,
    EvidenceEngineBase,
    EvidenceStatus,
)


class ACEInputError(ValueError):
    """Raised when ACE input violates its mathematical contract."""


class AuctionState(str, Enum):
    """Deterministic auction-state classification."""

    ALIGNED_BID = "ALIGNED_BID"
    ALIGNED_ASK = "ALIGNED_ASK"

    FLOW_LEADS_BID = "FLOW_LEADS_BID"
    FLOW_LEADS_ASK = "FLOW_LEADS_ASK"

    DEPTH_SUPPORTS_BID = "DEPTH_SUPPORTS_BID"
    DEPTH_SUPPORTS_ASK = "DEPTH_SUPPORTS_ASK"

    BALANCED = "BALANCED"

    UNDETERMINED = "UNDETERMINED"


@dataclass(frozen=True)
class ACEInputs:
    """
    Normalized inputs required by ACE.

    All quantities are expected to refer to the same:
        instrument
        observation interval
        market/venue
        unit system

    Missing fields remain None.
    """

    buy_volume: Optional[float] = None
    sell_volume: Optional[float] = None

    bid_depth: Optional[float] = None
    ask_depth: Optional[float] = None

    price_change: Optional[float] = None

    ned: Optional[float] = None
    dar: Optional[float] = None
    tv: Optional[float] = None
    mbc: Optional[float] = None

    dcs: Optional[float] = None

    observed_at: Optional[datetime] = None


@dataclass(frozen=True)
class ACEResult:
    """Complete deterministic Auction Context result."""

    status: EvidenceStatus

    # Primary structural pressures
    flow_pressure: Optional[float]
    depth_pressure: Optional[float]

    # Relationship between executed flow and resting depth
    flow_depth_alignment: Optional[float]
    auction_pressure_differential: Optional[float]

    # Price response to executed flow
    flow_response_efficiency: Optional[float]

    # DCS interaction
    concentration_adjusted_pressure: Optional[float]

    # Existing engine evidence
    ned: Optional[float]
    dar: Optional[float]
    tv: Optional[float]
    mbc: Optional[float]
    dcs: Optional[float]

    # Directional structural state
    auction_state: AuctionState

    # Explicit component availability
    flow_available: bool
    depth_available: bool
    response_available: bool
    concentration_available: bool

    calculation: tuple[CalculationStep, ...]

    observed_at: Optional[datetime]

    reason: Optional[str]

    @property
    def is_valid(self) -> bool:
        return self.status == EvidenceStatus.VALID

    @property
    def is_partial(self) -> bool:
        return self.status == EvidenceStatus.PARTIAL


class ACEEngine(EvidenceEngineBase):
    """
    Auction Context Engine.

    Layer:
        L003 — Market Structure

    ACE consumes already-derived market evidence.

    It intentionally does not depend on a specific implementation of
    NED/DAR/TV/MBC/DCS so that orchestration can pass either:

        - primitive values
        - result objects
        - mappings
        - an ACEInputs object

    No trading decision is produced here.
    """

    ENGINE_NAME = "ACE"
    LAYER = "L003"
    METRIC = "auction_context"

    # ---------------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------------

    def process(
        self,
        data: Any = None,
        *,
        inputs: Optional[ACEInputs] = None,
        observed_at: Optional[datetime] = None,
    ) -> ACEResult:
        """
        Validate and calculate auction context.
        """

        if data is not None and inputs is not None:
            raise ACEInputError(
                "Use either data or inputs, not both."
            )

        if inputs is not None:
            normalized = self._validate_inputs(inputs)

        elif data is not None:
            normalized = self._normalize_input(
                data,
                observed_at=observed_at,
            )

        else:
            raise ACEInputError(
                "ACE requires market-structure evidence."
            )

        return self.calculate(normalized)

    def calculate(self, data: ACEInputs) -> ACEResult:
        """
        Perform deterministic ACE mathematics.
        """

        if not isinstance(data, ACEInputs):
            raise ACEInputError(
                "calculate() requires ACEInputs."
            )

        calculation: list[CalculationStep] = []

        # -----------------------------------------------------------
        # 1. FLOW PRESSURE
        # -----------------------------------------------------------

        flow_pressure: Optional[float] = None

        if (
            data.buy_volume is not None
            and data.sell_volume is not None
        ):
            flow_total = (
                data.buy_volume
                + data.sell_volume
            )

            if flow_total > 0:
                flow_pressure = (
                    data.buy_volume
                    - data.sell_volume
                ) / flow_total

                calculation.append(
                    CalculationStep(
                        name="flow_pressure",
                        formula=(
                            "(buy_volume - sell_volume) / "
                            "(buy_volume + sell_volume)"
                        ),
                        inputs={
                            "buy_volume": data.buy_volume,
                            "sell_volume": data.sell_volume,
                        },
                        output=flow_pressure,
                    )
                )

        # -----------------------------------------------------------
        # 2. DEPTH PRESSURE
        # -----------------------------------------------------------

        depth_pressure: Optional[float] = None

        if (
            data.bid_depth is not None
            and data.ask_depth is not None
        ):
            depth_total = (
                data.bid_depth
                + data.ask_depth
            )

            if depth_total > 0:
                depth_pressure = (
                    data.bid_depth
                    - data.ask_depth
                ) / depth_total

                calculation.append(
                    CalculationStep(
                        name="depth_pressure",
                        formula=(
                            "(bid_depth - ask_depth) / "
                            "(bid_depth + ask_depth)"
                        ),
                        inputs={
                            "bid_depth": data.bid_depth,
                            "ask_depth": data.ask_depth,
                        },
                        output=depth_pressure,
                    )
                )

        # -----------------------------------------------------------
        # 3. FLOW / DEPTH ALIGNMENT
        # -----------------------------------------------------------

        flow_depth_alignment: Optional[float] = None

        if (
            flow_pressure is not None
            and depth_pressure is not None
        ):
            flow_depth_alignment = (
                flow_pressure
                * depth_pressure
            )

            calculation.append(
                CalculationStep(
                    name="flow_depth_alignment",
                    formula="P_flow * P_depth",
                    inputs={
                        "P_flow": flow_pressure,
                        "P_depth": depth_pressure,
                    },
                    output=flow_depth_alignment,
                )
            )

        # -----------------------------------------------------------
        # 4. AUCTION PRESSURE DIFFERENTIAL
        # -----------------------------------------------------------

        auction_pressure_differential: Optional[float] = None

        if (
            flow_pressure is not None
            and depth_pressure is not None
        ):
            auction_pressure_differential = (
                flow_pressure
                - depth_pressure
            )

            calculation.append(
                CalculationStep(
                    name="auction_pressure_differential",
                    formula="P_flow - P_depth",
                    inputs={
                        "P_flow": flow_pressure,
                        "P_depth": depth_pressure,
                    },
                    output=auction_pressure_differential,
                )
            )

        # -----------------------------------------------------------
        # 5. FLOW RESPONSE EFFICIENCY
        # -----------------------------------------------------------

        flow_response_efficiency: Optional[float] = None

        if (
            data.price_change is not None
            and data.ned is not None
            and data.ned != 0
        ):
            flow_response_efficiency = (
                data.price_change
                / data.ned
            )

            calculation.append(
                CalculationStep(
                    name="flow_response_efficiency",
                    formula="price_change / NED",
                    inputs={
                        "price_change": data.price_change,
                        "NED": data.ned,
                    },
                    output=flow_response_efficiency,
                )
            )

        # -----------------------------------------------------------
        # 6. CONCENTRATION-ADJUSTED PRESSURE
        # -----------------------------------------------------------

        concentration_adjusted_pressure: Optional[float] = None

        if (
            flow_depth_alignment is not None
            and data.dcs is not None
        ):
            concentration_adjusted_pressure = (
                flow_depth_alignment
                * data.dcs
            )

            calculation.append(
                CalculationStep(
                    name="concentration_adjusted_pressure",
                    formula="flow_depth_alignment * DCS",
                    inputs={
                        "flow_depth_alignment": (
                            flow_depth_alignment
                        ),
                        "DCS": data.dcs,
                    },
                    output=concentration_adjusted_pressure,
                )
            )

        # -----------------------------------------------------------
        # 7. AUCTION STATE
        # -----------------------------------------------------------

        auction_state = self._classify_auction(
            flow_pressure=flow_pressure,
            depth_pressure=depth_pressure,
        )

        # -----------------------------------------------------------
        # 8. STATUS
        # -----------------------------------------------------------

        flow_available = flow_pressure is not None
        depth_available = depth_pressure is not None
        response_available = (
            flow_response_efficiency is not None
        )
        concentration_available = (
            data.dcs is not None
        )

        if not flow_available and not depth_available:
            status = EvidenceStatus.INSUFFICIENT

            reason = (
                "Neither executable flow nor resting depth "
                "was sufficient to derive auction context."
            )

        elif not flow_available or not depth_available:
            status = EvidenceStatus.PARTIAL

            reason = (
                "Auction context is partially observable because "
                "either executable flow or resting depth is missing."
            )

        else:
            status = EvidenceStatus.VALID
            reason = None

        return ACEResult(
            status=status,
            flow_pressure=flow_pressure,
            depth_pressure=depth_pressure,
            flow_depth_alignment=flow_depth_alignment,
            auction_pressure_differential=(
                auction_pressure_differential
            ),
            flow_response_efficiency=(
                flow_response_efficiency
            ),
            concentration_adjusted_pressure=(
                concentration_adjusted_pressure
            ),
            ned=data.ned,
            dar=data.dar,
            tv=data.tv,
            mbc=data.mbc,
            dcs=data.dcs,
            auction_state=auction_state,
            flow_available=flow_available,
            depth_available=depth_available,
            response_available=response_available,
            concentration_available=(
                concentration_available
            ),
            calculation=tuple(calculation),
            observed_at=data.observed_at,
            reason=reason,
        )

    # ---------------------------------------------------------------
    # EVIDENCE
    # ---------------------------------------------------------------

    def build_evidence(
        self,
        result: ACEResult,
        *,
        source: str = "ACE",
        source_type: str = "derived",
    ) -> list[Evidence]:
        """
        Convert ACE calculations into auditable Evidence objects.
        """

        evidence: list[Evidence] = []

        self._append_metric_evidence(
            evidence=evidence,
            result=result,
            metric="ace.flow_pressure",
            value=result.flow_pressure,
            unit="dimensionless",
            source=source,
            source_type=source_type,
            inputs={
                "NED": result.ned,
                "buy_volume_available": (
                    result.flow_available
                ),
            },
        )

        self._append_metric_evidence(
            evidence=evidence,
            result=result,
            metric="ace.depth_pressure",
            value=result.depth_pressure,
            unit="dimensionless",
            source=source,
            source_type=source_type,
            inputs={
                "DAR": result.dar,
                "depth_available": (
                    result.depth_available
                ),
            },
        )

        self._append_metric_evidence(
            evidence=evidence,
            result=result,
            metric="ace.flow_depth_alignment",
            value=result.flow_depth_alignment,
            unit="dimensionless",
            source=source,
            source_type=source_type,
            inputs={
                "flow_pressure": result.flow_pressure,
                "depth_pressure": result.depth_pressure,
            },
        )

        self._append_metric_evidence(
            evidence=evidence,
            result=result,
            metric="ace.auction_pressure_differential",
            value=result.auction_pressure_differential,
            unit="dimensionless",
            source=source,
            source_type=source_type,
            inputs={
                "flow_pressure": result.flow_pressure,
                "depth_pressure": result.depth_pressure,
            },
        )

        self._append_metric_evidence(
            evidence=evidence,
            result=result,
            metric="ace.flow_response_efficiency",
            value=result.flow_response_efficiency,
            unit="price_per_volume",
            source=source,
            source_type=source_type,
            inputs={
                "price_change_available": (
                    result.response_available
                ),
                "NED": result.ned,
            },
        )

        self._append_metric_evidence(
            evidence=evidence,
            result=result,
            metric="ace.concentration_adjusted_pressure",
            value=result.concentration_adjusted_pressure,
            unit="dimensionless",
            source=source,
            source_type=source_type,
            inputs={
                "flow_depth_alignment": (
                    result.flow_depth_alignment
                ),
                "DCS": result.dcs,
            },
        )

        evidence.append(
            self.make_evidence(
                metric="ace.auction_state",
                value=result.auction_state.value,
                unit="categorical",
                status=result.status,
                source=source,
                source_type=source_type,
                inputs={
                    "flow_pressure": result.flow_pressure,
                    "depth_pressure": result.depth_pressure,
                },
                calculation=list(result.calculation),
                reason=result.reason,
            )
        )

        return evidence

    def _append_metric_evidence(
        self,
        *,
        evidence: list[Evidence],
        result: ACEResult,
        metric: str,
        value: Optional[float],
        unit: str,
        source: str,
        source_type: str,
        inputs: Mapping[str, Any],
    ) -> None:
        """
        Add numerical evidence only when the underlying calculation
        actually exists.
        """

        if value is None:
            return

        evidence.append(
            self.make_evidence(
                metric=metric,
                value=value,
                unit=unit,
                status=result.status,
                source=source,
                source_type=source_type,
                inputs=dict(inputs),
                calculation=list(result.calculation),
                reason=result.reason,
            )
        )

    # ---------------------------------------------------------------
    # AUCTION CLASSIFICATION
    # ---------------------------------------------------------------

    @staticmethod
    def _classify_auction(
        *,
        flow_pressure: Optional[float],
        depth_pressure: Optional[float],
    ) -> AuctionState:
        """
        Classify auction structure strictly from observable signs.

        No tolerance band is invented.

        Exact zero means mathematically balanced.
        """

        if (
            flow_pressure is None
            or depth_pressure is None
        ):
            return AuctionState.UNDETERMINED

        if flow_pressure > 0 and depth_pressure > 0:
            return AuctionState.ALIGNED_BID

        if flow_pressure < 0 and depth_pressure < 0:
            return AuctionState.ALIGNED_ASK

        if flow_pressure > 0 and depth_pressure <= 0:
            return AuctionState.FLOW_LEADS_BID

        if flow_pressure < 0 and depth_pressure >= 0:
            return AuctionState.FLOW_LEADS_ASK

        if depth_pressure > 0 and flow_pressure <= 0:
            return AuctionState.DEPTH_SUPPORTS_BID

        if depth_pressure < 0 and flow_pressure >= 0:
            return AuctionState.DEPTH_SUPPORTS_ASK

        return AuctionState.BALANCED

    # ---------------------------------------------------------------
    # INPUT NORMALIZATION
    # ---------------------------------------------------------------

    def _normalize_input(
        self,
        data: Any,
        *,
        observed_at: Optional[datetime],
    ) -> ACEInputs:
        """
        Normalize mappings and compatible result objects.
        """

        if isinstance(data, ACEInputs):
            return self._validate_inputs(data)

        if isinstance(data, Mapping):
            return self._validate_inputs(
                ACEInputs(
                    buy_volume=self._optional_float(
                        data.get("buy_volume")
                    ),
                    sell_volume=self._optional_float(
                        data.get("sell_volume")
                    ),
                    bid_depth=self._optional_float(
                        data.get("bid_depth")
                    ),
                    ask_depth=self._optional_float(
                        data.get("ask_depth")
                    ),
                    price_change=self._optional_float(
                        data.get("price_change")
                    ),
                    ned=self._optional_float(
                        data.get("ned", data.get("NED"))
                    ),
                    dar=self._optional_float(
                        data.get("dar", data.get("DAR"))
                    ),
                    tv=self._optional_float(
                        data.get("tv", data.get("TV"))
                    ),
                    mbc=self._optional_float(
                        data.get("mbc", data.get("MBC"))
                    ),
                    dcs=self._optional_float(
                        data.get("dcs", data.get("DCS"))
                    ),
                    observed_at=data.get(
                        "observed_at",
                        data.get(
                            "timestamp",
                            observed_at,
                        ),
                    ),
                )
            )

        return self._from_result_object(
            data,
            observed_at=observed_at,
        )

    def _from_result_object(
        self,
        data: Any,
        *,
        observed_at: Optional[datetime],
    ) -> ACEInputs:
        """
        Extract compatible fields from NED/DAR/TV/MBC/DCS
        result objects without importing those engines.

        This avoids circular dependencies.
        """

        def read(
            *names: str,
        ) -> Any:
            for name in names:
                if hasattr(data, name):
                    return getattr(data, name)

            return None

        buy_volume = read(
            "buy_volume",
            "aggressive_buy_volume",
        )

        sell_volume = read(
            "sell_volume",
            "aggressive_sell_volume",
        )

        bid_depth = read("bid_depth")
        ask_depth = read("ask_depth")

        price_change = read(
            "price_change",
            "delta_price",
        )

        ned = read("ned", "NED")
        dar = read("dar", "DAR")
        tv = read(
            "tv",
            "velocity",
            "price_velocity",
        )
        mbc = read("mbc", "MBC")
        dcs = read("dcs", "DCS")

        timestamp = read(
            "observed_at",
            "timestamp",
        )

        return self._validate_inputs(
            ACEInputs(
                buy_volume=self._optional_float(
                    buy_volume
                ),
                sell_volume=self._optional_float(
                    sell_volume
                ),
                bid_depth=self._optional_float(
                    bid_depth
                ),
                ask_depth=self._optional_float(
                    ask_depth
                ),
                price_change=self._optional_float(
                    price_change
                ),
                ned=self._optional_float(ned),
                dar=self._optional_float(dar),
                tv=self._optional_float(tv),
                mbc=self._optional_float(mbc),
                dcs=self._optional_float(dcs),
                observed_at=timestamp or observed_at,
            )
        )

    # ---------------------------------------------------------------
    # INPUT VALIDATION
    # ---------------------------------------------------------------

    def _validate_inputs(
        self,
        inputs: ACEInputs,
    ) -> ACEInputs:
        """
        Validate every numerical input.

        Negative depth/volume is invalid.

        Negative price change, NED, DAR, TV and MBC are valid because
        those variables are directional quantities.
        """

        numeric_fields = (
            "buy_volume",
            "sell_volume",
            "bid_depth",
            "ask_depth",
            "price_change",
            "ned",
            "dar",
            "tv",
            "mbc",
            "dcs",
        )

        for field_name in numeric_fields:
            value = getattr(inputs, field_name)

            if value is None:
                continue

            if not isinstance(value, (int, float)):
                raise ACEInputError(
                    f"{field_name} must be numeric."
                )

            if not math.isfinite(float(value)):
                raise ACEInputError(
                    f"{field_name} must be finite."
                )

        for field_name in (
            "buy_volume",
            "sell_volume",
            "bid_depth",
            "ask_depth",
        ):
            value = getattr(inputs, field_name)

            if value is not None and value < 0:
                raise ACEInputError(
                    f"{field_name} cannot be negative."
                )

        if inputs.dcs is not None and inputs.dcs < 0:
            raise ACEInputError(
                "DCS cannot be negative."
            )

        return inputs

    @staticmethod
    def _optional_float(
        value: Any,
    ) -> Optional[float]:
        if value is None:
            return None

        try:
            result = float(value)
        except (TypeError, ValueError) as exc:
            raise ACEInputError(
                "ACE numerical input is not convertible to float."
            ) from exc

        if not math.isfinite(result):
            raise ACEInputError(
                "ACE numerical input must be finite."
            )

        return result


# ----------------------------------------------------------------------
# COMPATIBILITY ALIASES
# ----------------------------------------------------------------------

AuctionContextEngine = ACEEngine
AuctionContextEvidenceEngine = ACEEngine
AuctionStructureEngine = ACEEngine


__all__ = [
    "ACEInputError",
    "AuctionState",
    "ACEInputs",
    "ACEResult",
    "ACEEngine",
    "AuctionContextEngine",
    "AuctionContextEvidenceEngine",
    "AuctionStructureEngine",
]