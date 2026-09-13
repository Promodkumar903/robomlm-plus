"""
ROBOMLM_PLUS
Evidence Cortex — L003 Market Structure

DCS — Depth Concentration Structure

Purpose
-------
Measure how concentrated executable resting depth is across observed
order-book levels.

Core mathematics
----------------
For one side of the book:

    s_i = v_i / V

    HHI = Σ(s_i²)

    N_eff = 1 / HHI

    H = -Σ(s_i * ln(s_i))

    H_norm = H / ln(N)

Where:
    v_i   = positive depth volume at level i
    V     = total observed side depth
    s_i   = level's share of side depth
    N     = number of positive-volume levels

Cross-side structural measures:

    concentration_imbalance = HHI_bid - HHI_ask

    effective_level_imbalance =
        (N_eff_bid - N_eff_ask) /
        (N_eff_bid + N_eff_ask)

When both sides exist:

    DCS = (HHI_bid + HHI_ask) / 2

DCS is deliberately NOT converted into an arbitrary 0–100 score.

Interpretation
--------------
Higher HHI:
    depth is concentrated into fewer levels.

Lower HHI:
    depth is distributed across more levels.

Higher N_eff:
    depth is structurally distributed across more effective levels.

Normalized entropy:
    0 -> maximally concentrated for the observed support
    1 -> uniform distribution across observed positive-volume levels

The engine reports structure. It does not make a trade decision.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable, Mapping, Optional, Sequence

from .evidence_engine_base import (
    CalculationStep,
    Evidence,
    EvidenceEngineBase,
    EvidenceStatus,
)


class DCSInputError(ValueError):
    """Raised when DCS input violates the engine contract."""


@dataclass(frozen=True)
class DCSLevel:
    """
    Normalized order-book depth level.

    side:
        BID or ASK.

    price:
        Observed price of the level.

    volume:
        Resting depth at that level.

    level:
        Book level number. If supplied, it must be non-negative.

    observed_at:
        Observation timestamp.
    """

    side: str
    price: float
    volume: float
    level: int
    observed_at: Optional[datetime] = None


@dataclass(frozen=True)
class DCSResult:
    """Complete deterministic DCS calculation result."""

    status: EvidenceStatus

    # Core DCS
    dcs: Optional[float]

    # Side totals
    bid_depth: float
    ask_depth: float

    # Number of positive-volume levels
    bid_level_count: int
    ask_level_count: int

    # HHI concentration
    bid_hhi: Optional[float]
    ask_hhi: Optional[float]

    # Effective number of levels
    bid_effective_levels: Optional[float]
    ask_effective_levels: Optional[float]

    # Shannon entropy
    bid_entropy: Optional[float]
    ask_entropy: Optional[float]

    # Entropy normalized to observed support
    bid_entropy_normalized: Optional[float]
    ask_entropy_normalized: Optional[float]

    # Cross-side structural relationships
    concentration_imbalance: Optional[float]
    effective_level_imbalance: Optional[float]

    # Top-level structural shares
    bid_level_shares: tuple[float, ...]
    ask_level_shares: tuple[float, ...]

    # Calculation trace
    calculation: tuple[CalculationStep, ...]

    # Audit metadata
    observed_at: Optional[datetime]
    reason: Optional[str]

    @property
    def is_valid(self) -> bool:
        return self.status == EvidenceStatus.VALID

    @property
    def is_partial(self) -> bool:
        return self.status == EvidenceStatus.PARTIAL


class DCSEngine(EvidenceEngineBase):
    """
    Depth Concentration Structure Engine.

    Layer:
        L003 — Market Structure

    The engine accepts either:

        levels=[...]
    or:
        bids=[...], asks=[...]

    Each level can be:

        DCSLevel

    or mapping:

        {
            "side": "BID",
            "price": 100.0,
            "volume": 10.0,
            "level": 1,
            "observed_at": datetime(...)
        }

    or tuple:

        (price, volume)

    For tuple input, the level number is assigned from sequence order.
    """

    ENGINE_NAME = "DCS"
    LAYER = "L003"
    METRIC = "depth_concentration_structure"

    def __init__(
        self,
        *,
        zero_volume_policy: str = "ignore",
    ) -> None:
        super().__init__()

        if zero_volume_policy not in {"ignore"}:
            raise DCSInputError(
                "zero_volume_policy must be 'ignore'."
            )

        self.zero_volume_policy = zero_volume_policy

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def process(
        self,
        data: Any = None,
        *,
        levels: Optional[Iterable[Any]] = None,
        bids: Optional[Iterable[Any]] = None,
        asks: Optional[Iterable[Any]] = None,
        observed_at: Optional[datetime] = None,
    ) -> DCSResult:
        """
        Validate, normalize and calculate DCS.

        Supported forms:

            engine.process(levels=[...])

        or:

            engine.process(bids=[...], asks=[...])

        or:

            engine.process(data)

        where data may itself contain levels/bids/asks.
        """

        if data is not None:
            if levels is not None or bids is not None or asks is not None:
                raise DCSInputError(
                    "Use either data or explicit levels/bids/asks, not both."
                )

            levels, bids, asks, observed_at = self._extract_input(
                data,
                observed_at,
            )

        normalized = self._normalize_book(
            levels=levels,
            bids=bids,
            asks=asks,
            observed_at=observed_at,
        )

        return self.calculate(normalized)

    def calculate(self, data: Any) -> DCSResult:
        """
        Calculate DCS from normalized DCSLevel records.

        No decision or trading authorization is generated.
        """

        if not isinstance(data, Sequence):
            raise DCSInputError(
                "calculate() requires a sequence of DCSLevel records."
            )

        levels = list(data)

        if not levels:
            return self._insufficient_result(
                "No order-book depth levels were supplied."
            )

        bid_levels = [
            level
            for level in levels
            if level.side == "BID" and level.volume > 0
        ]

        ask_levels = [
            level
            for level in levels
            if level.side == "ASK" and level.volume > 0
        ]

        bid_stats = self._calculate_side(bid_levels)
        ask_stats = self._calculate_side(ask_levels)

        calculation: list[CalculationStep] = []

        if bid_stats["hhi"] is not None:
            calculation.extend(
                self._side_calculation_steps(
                    "BID",
                    bid_stats,
                )
            )

        if ask_stats["hhi"] is not None:
            calculation.extend(
                self._side_calculation_steps(
                    "ASK",
                    ask_stats,
                )
            )

        dcs: Optional[float]

        if (
            bid_stats["hhi"] is not None
            and ask_stats["hhi"] is not None
        ):
            dcs = (
                bid_stats["hhi"]
                + ask_stats["hhi"]
            ) / 2.0

            calculation.append(
                CalculationStep(
                    name="dcs",
                    formula="(HHI_bid + HHI_ask) / 2",
                    inputs={
                        "HHI_bid": bid_stats["hhi"],
                        "HHI_ask": ask_stats["hhi"],
                    },
                    output=dcs,
                )
            )
        else:
            dcs = None

        concentration_imbalance: Optional[float]

        if (
            bid_stats["hhi"] is not None
            and ask_stats["hhi"] is not None
        ):
            concentration_imbalance = (
                bid_stats["hhi"]
                - ask_stats["hhi"]
            )

            calculation.append(
                CalculationStep(
                    name="concentration_imbalance",
                    formula="HHI_bid - HHI_ask",
                    inputs={
                        "HHI_bid": bid_stats["hhi"],
                        "HHI_ask": ask_stats["hhi"],
                    },
                    output=concentration_imbalance,
                )
            )
        else:
            concentration_imbalance = None

        effective_level_imbalance: Optional[float]

        if (
            bid_stats["effective_levels"] is not None
            and ask_stats["effective_levels"] is not None
        ):
            denominator = (
                bid_stats["effective_levels"]
                + ask_stats["effective_levels"]
            )

            if denominator > 0:
                effective_level_imbalance = (
                    bid_stats["effective_levels"]
                    - ask_stats["effective_levels"]
                ) / denominator
            else:
                effective_level_imbalance = None

            calculation.append(
                CalculationStep(
                    name="effective_level_imbalance",
                    formula=(
                        "(N_eff_bid - N_eff_ask) / "
                        "(N_eff_bid + N_eff_ask)"
                    ),
                    inputs={
                        "N_eff_bid": bid_stats["effective_levels"],
                        "N_eff_ask": ask_stats["effective_levels"],
                    },
                    output=effective_level_imbalance,
                )
            )
        else:
            effective_level_imbalance = None

        if bid_stats["hhi"] is None and ask_stats["hhi"] is None:
            status = EvidenceStatus.INSUFFICIENT
            reason = (
                "No positive-volume BID or ASK depth was available."
            )
        elif (
            bid_stats["hhi"] is None
            or ask_stats["hhi"] is None
        ):
            status = EvidenceStatus.PARTIAL
            reason = (
                "Only one side of the order book contained "
                "positive-volume depth."
            )
        else:
            status = EvidenceStatus.VALID
            reason = None

        return DCSResult(
            status=status,
            dcs=dcs,
            bid_depth=bid_stats["total_depth"],
            ask_depth=ask_stats["total_depth"],
            bid_level_count=bid_stats["level_count"],
            ask_level_count=ask_stats["level_count"],
            bid_hhi=bid_stats["hhi"],
            ask_hhi=ask_stats["hhi"],
            bid_effective_levels=bid_stats["effective_levels"],
            ask_effective_levels=ask_stats["effective_levels"],
            bid_entropy=bid_stats["entropy"],
            ask_entropy=ask_stats["entropy"],
            bid_entropy_normalized=bid_stats[
                "entropy_normalized"
            ],
            ask_entropy_normalized=ask_stats[
                "entropy_normalized"
            ],
            concentration_imbalance=concentration_imbalance,
            effective_level_imbalance=effective_level_imbalance,
            bid_level_shares=tuple(bid_stats["shares"]),
            ask_level_shares=tuple(ask_stats["shares"]),
            calculation=tuple(calculation),
            observed_at=observed_at
            or self._latest_timestamp(levels),
            reason=reason,
        )

    # ------------------------------------------------------------------
    # EVIDENCE
    # ------------------------------------------------------------------

    def build_evidence(
        self,
        result: DCSResult,
        *,
        source: str = "DCS",
        source_type: str = "derived",
    ) -> list[Evidence]:
        """
        Convert deterministic DCS outputs into traceable Evidence objects.

        Missing metrics are not fabricated.
        """

        evidence: list[Evidence] = []

        if result.bid_hhi is not None:
            evidence.append(
                self.make_evidence(
                    metric="dcs.bid_hhi",
                    value=result.bid_hhi,
                    unit="dimensionless",
                    status=result.status,
                    source=source,
                    source_type=source_type,
                    inputs={
                        "bid_depth": result.bid_depth,
                        "bid_level_count": result.bid_level_count,
                    },
                    calculation=list(result.calculation),
                    reason=result.reason,
                )
            )

        if result.ask_hhi is not None:
            evidence.append(
                self.make_evidence(
                    metric="dcs.ask_hhi",
                    value=result.ask_hhi,
                    unit="dimensionless",
                    status=result.status,
                    source=source,
                    source_type=source_type,
                    inputs={
                        "ask_depth": result.ask_depth,
                        "ask_level_count": result.ask_level_count,
                    },
                    calculation=list(result.calculation),
                    reason=result.reason,
                )
            )

        if result.bid_effective_levels is not None:
            evidence.append(
                self.make_evidence(
                    metric="dcs.bid_effective_levels",
                    value=result.bid_effective_levels,
                    unit="levels",
                    status=result.status,
                    source=source,
                    source_type=source_type,
                    inputs={
                        "bid_hhi": result.bid_hhi,
                    },
                    calculation=list(result.calculation),
                    reason=result.reason,
                )
            )

        if result.ask_effective_levels is not None:
            evidence.append(
                self.make_evidence(
                    metric="dcs.ask_effective_levels",
                    value=result.ask_effective_levels,
                    unit="levels",
                    status=result.status,
                    source=source,
                    source_type=source_type,
                    inputs={
                        "ask_hhi": result.ask_hhi,
                    },
                    calculation=list(result.calculation),
                    reason=result.reason,
                )
            )

        if result.bid_entropy is not None:
            evidence.append(
                self.make_evidence(
                    metric="dcs.bid_entropy",
                    value=result.bid_entropy,
                    unit="nats",
                    status=result.status,
                    source=source,
                    source_type=source_type,
                    inputs={
                        "bid_level_count": result.bid_level_count,
                    },
                    calculation=list(result.calculation),
                    reason=result.reason,
                )
            )

        if result.ask_entropy is not None:
            evidence.append(
                self.make_evidence(
                    metric="dcs.ask_entropy",
                    value=result.ask_entropy,
                    unit="nats",
                    status=result.status,
                    source=source,
                    source_type=source_type,
                    inputs={
                        "ask_level_count": result.ask_level_count,
                    },
                    calculation=list(result.calculation),
                    reason=result.reason,
                )
            )

        if result.bid_entropy_normalized is not None:
            evidence.append(
                self.make_evidence(
                    metric="dcs.bid_entropy_normalized",
                    value=result.bid_entropy_normalized,
                    unit="dimensionless",
                    status=result.status,
                    source=source,
                    source_type=source_type,
                    inputs={
                        "bid_entropy": result.bid_entropy,
                        "bid_level_count": result.bid_level_count,
                    },
                    calculation=list(result.calculation),
                    reason=result.reason,
                )
            )

        if result.ask_entropy_normalized is not None:
            evidence.append(
                self.make_evidence(
                    metric="dcs.ask_entropy_normalized",
                    value=result.ask_entropy_normalized,
                    unit="dimensionless",
                    status=result.status,
                    source=source,
                    source_type=source_type,
                    inputs={
                        "ask_entropy": result.ask_entropy,
                        "ask_level_count": result.ask_level_count,
                    },
                    calculation=list(result.calculation),
                    reason=result.reason,
                )
            )

        if result.dcs is not None:
            evidence.append(
                self.make_evidence(
                    metric="dcs",
                    value=result.dcs,
                    unit="dimensionless",
                    status=result.status,
                    source=source,
                    source_type=source_type,
                    inputs={
                        "bid_hhi": result.bid_hhi,
                        "ask_hhi": result.ask_hhi,
                    },
                    calculation=list(result.calculation),
                    reason=result.reason,
                )
            )

        if result.concentration_imbalance is not None:
            evidence.append(
                self.make_evidence(
                    metric="dcs.concentration_imbalance",
                    value=result.concentration_imbalance,
                    unit="dimensionless",
                    status=result.status,
                    source=source,
                    source_type=source_type,
                    inputs={
                        "bid_hhi": result.bid_hhi,
                        "ask_hhi": result.ask_hhi,
                    },
                    calculation=list(result.calculation),
                    reason=result.reason,
                )
            )

        if result.effective_level_imbalance is not None:
            evidence.append(
                self.make_evidence(
                    metric="dcs.effective_level_imbalance",
                    value=result.effective_level_imbalance,
                    unit="dimensionless",
                    status=result.status,
                    source=source,
                    source_type=source_type,
                    inputs={
                        "bid_effective_levels": (
                            result.bid_effective_levels
                        ),
                        "ask_effective_levels": (
                            result.ask_effective_levels
                        ),
                    },
                    calculation=list(result.calculation),
                    reason=result.reason,
                )
            )

        return evidence

    # ------------------------------------------------------------------
    # SIDE MATHEMATICS
    # ------------------------------------------------------------------

    def _calculate_side(
        self,
        levels: Sequence[DCSLevel],
    ) -> dict[str, Any]:
        """
        Calculate concentration statistics for one side.

        Duplicate level numbers are allowed because the input can represent
        independently observed rows. Volumes are aggregated by level.

        HHI is calculated over the resulting level-volume distribution.
        """

        aggregated: dict[int, float] = {}

        for level in levels:
            aggregated[level.level] = (
                aggregated.get(level.level, 0.0)
                + level.volume
            )

        positive_volumes = [
            volume
            for volume in aggregated.values()
            if volume > 0
        ]

        if not positive_volumes:
            return {
                "total_depth": 0.0,
                "level_count": 0,
                "shares": [],
                "hhi": None,
                "effective_levels": None,
                "entropy": None,
                "entropy_normalized": None,
            }

        total_depth = math.fsum(positive_volumes)

        shares = [
            volume / total_depth
            for volume in positive_volumes
        ]

        hhi = math.fsum(
            share * share
            for share in shares
        )

        effective_levels = (
            1.0 / hhi
            if hhi > 0
            else None
        )

        entropy = math.fsum(
            -share * math.log(share)
            for share in shares
            if share > 0
        )

        level_count = len(shares)

        if level_count <= 1:
            entropy_normalized = 0.0
        else:
            maximum_entropy = math.log(level_count)
            entropy_normalized = (
                entropy / maximum_entropy
                if maximum_entropy > 0
                else 0.0
            )

        return {
            "total_depth": total_depth,
            "level_count": level_count,
            "shares": shares,
            "hhi": hhi,
            "effective_levels": effective_levels,
            "entropy": entropy,
            "entropy_normalized": entropy_normalized,
        }

    @staticmethod
    def _side_calculation_steps(
        side: str,
        stats: Mapping[str, Any],
    ) -> list[CalculationStep]:
        return [
            CalculationStep(
                name=f"{side.lower()}_level_shares",
                formula="s_i = v_i / Σ(v_i)",
                inputs={
                    "total_depth": stats["total_depth"],
                    "level_count": stats["level_count"],
                },
                output=stats["shares"],
            ),
            CalculationStep(
                name=f"{side.lower()}_hhi",
                formula="HHI = Σ(s_i²)",
                inputs={
                    "shares": stats["shares"],
                },
                output=stats["hhi"],
            ),
            CalculationStep(
                name=f"{side.lower()}_effective_levels",
                formula="N_eff = 1 / HHI",
                inputs={
                    "HHI": stats["hhi"],
                },
                output=stats["effective_levels"],
            ),
            CalculationStep(
                name=f"{side.lower()}_entropy",
                formula="H = -Σ(s_i * ln(s_i))",
                inputs={
                    "shares": stats["shares"],
                },
                output=stats["entropy"],
            ),
            CalculationStep(
                name=f"{side.lower()}_normalized_entropy",
                formula="H_norm = H / ln(N)",
                inputs={
                    "entropy": stats["entropy"],
                    "N": stats["level_count"],
                },
                output=stats["entropy_normalized"],
            ),
        ]

    # ------------------------------------------------------------------
    # INPUT NORMALIZATION
    # ------------------------------------------------------------------

    def _normalize_book(
        self,
        *,
        levels: Optional[Iterable[Any]],
        bids: Optional[Iterable[Any]],
        asks: Optional[Iterable[Any]],
        observed_at: Optional[datetime],
    ) -> list[DCSLevel]:
        if levels is not None and (bids is not None or asks is not None):
            raise DCSInputError(
                "Do not combine levels with bids/asks."
            )

        normalized: list[DCSLevel] = []

        if levels is not None:
            for index, raw in enumerate(levels, start=1):
                normalized.append(
                    self._normalize_level(
                        raw,
                        default_side=None,
                        default_level=index,
                        observed_at=observed_at,
                    )
                )

        else:
            if bids is not None:
                for index, raw in enumerate(bids, start=1):
                    normalized.append(
                        self._normalize_level(
                            raw,
                            default_side="BID",
                            default_level=index,
                            observed_at=observed_at,
                        )
                    )

            if asks is not None:
                for index, raw in enumerate(asks, start=1):
                    normalized.append(
                        self._normalize_level(
                            raw,
                            default_side="ASK",
                            default_level=index,
                            observed_at=observed_at,
                        )
                    )

        if not normalized:
            raise DCSInputError(
                "At least one order-book depth level is required."
            )

        return normalized

    def _normalize_level(
        self,
        raw: Any,
        *,
        default_side: Optional[str],
        default_level: int,
        observed_at: Optional[datetime],
    ) -> DCSLevel:
        if isinstance(raw, DCSLevel):
            level = raw
            side = self._normalize_side(level.side)

            if level.level < 0:
                raise DCSInputError(
                    "Book level cannot be negative."
                )

            self._validate_price(level.price)
            self._validate_volume(level.volume)

            return DCSLevel(
                side=side,
                price=float(level.price),
                volume=float(level.volume),
                level=int(level.level),
                observed_at=(
                    level.observed_at
                    or observed_at
                ),
            )

        if isinstance(raw, Mapping):
            side_raw = raw.get("side", default_side)

            if side_raw is None:
                raise DCSInputError(
                    "Each level requires side when levels are supplied."
                )

            side = self._normalize_side(side_raw)

            price = raw.get("price")

            if price is None:
                raise DCSInputError(
                    "Each depth level requires price."
                )

            volume = raw.get(
                "volume",
                raw.get("qty", raw.get("quantity")),
            )

            if volume is None:
                raise DCSInputError(
                    "Each depth level requires volume."
                )

            level_number = raw.get(
                "level",
                raw.get(
                    "level_number",
                    raw.get("position", default_level),
                ),
            )

            timestamp = raw.get(
                "observed_at",
                raw.get("timestamp", observed_at),
            )

            try:
                level_number = int(level_number)
            except (TypeError, ValueError) as exc:
                raise DCSInputError(
                    "Book level number must be an integer."
                ) from exc

            if level_number < 0:
                raise DCSInputError(
                    "Book level cannot be negative."
                )

            price_value = self._as_float(price, "price")
            volume_value = self._as_float(volume, "volume")

            self._validate_price(price_value)
            self._validate_volume(volume_value)

            return DCSLevel(
                side=side,
                price=price_value,
                volume=volume_value,
                level=level_number,
                observed_at=timestamp,
            )

        if isinstance(raw, (tuple, list)):
            if len(raw) < 2:
                raise DCSInputError(
                    "Tuple/list depth level requires (price, volume)."
                )

            if default_side is None:
                raise DCSInputError(
                    "Tuple/list levels require bids/asks input "
                    "because side is not encoded."
                )

            price_value = self._as_float(raw[0], "price")
            volume_value = self._as_float(raw[1], "volume")

            self._validate_price(price_value)
            self._validate_volume(volume_value)

            return DCSLevel(
                side=default_side,
                price=price_value,
                volume=volume_value,
                level=default_level,
                observed_at=observed_at,
            )

        raise DCSInputError(
            f"Unsupported depth level type: {type(raw).__name__}"
        )

    # ------------------------------------------------------------------
    # DATA EXTRACTION
    # ------------------------------------------------------------------

    def _extract_input(
        self,
        data: Any,
        observed_at: Optional[datetime],
    ) -> tuple[
        Optional[Iterable[Any]],
        Optional[Iterable[Any]],
        Optional[Iterable[Any]],
        Optional[datetime],
    ]:
        if isinstance(data, Mapping):
            extracted_observed_at = data.get(
                "observed_at",
                data.get("timestamp", observed_at),
            )

            if "levels" in data:
                return (
                    data["levels"],
                    None,
                    None,
                    extracted_observed_at,
                )

            if "bids" in data or "asks" in data:
                return (
                    None,
                    data.get("bids"),
                    data.get("asks"),
                    extracted_observed_at,
                )

        if isinstance(data, Sequence) and not isinstance(
            data,
            (str, bytes, bytearray),
        ):
            return (
                data,
                None,
                None,
                observed_at,
            )

        raise DCSInputError(
            "Unsupported DCS input. Expected mapping or sequence."
        )

    # ------------------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_side(value: Any) -> str:
        if not isinstance(value, str):
            raise DCSInputError("Depth side must be a string.")

        normalized = value.strip().upper()

        aliases = {
            "BUY": "BID",
            "BID": "BID",
            "B": "BID",
            "SELL": "ASK",
            "ASK": "ASK",
            "A": "ASK",
        }

        if normalized not in aliases:
            raise DCSInputError(
                f"Unsupported depth side: {value!r}"
            )

        return aliases[normalized]

    @staticmethod
    def _as_float(value: Any, field: str) -> float:
        try:
            result = float(value)
        except (TypeError, ValueError) as exc:
            raise DCSInputError(
                f"{field} must be numeric."
            ) from exc

        if not math.isfinite(result):
            raise DCSInputError(
                f"{field} must be finite."
            )

        return result

    @staticmethod
    def _validate_price(price: float) -> None:
        if not math.isfinite(price) or price <= 0:
            raise DCSInputError(
                "Depth price must be finite and strictly positive."
            )

    @staticmethod
    def _validate_volume(volume: float) -> None:
        if not math.isfinite(volume) or volume < 0:
            raise DCSInputError(
                "Depth volume must be finite and non-negative."
            )

    @staticmethod
    def _latest_timestamp(
        levels: Sequence[DCSLevel],
    ) -> Optional[datetime]:
        timestamps = [
            level.observed_at
            for level in levels
            if level.observed_at is not None
        ]

        return max(timestamps) if timestamps else None

    # ------------------------------------------------------------------
    # INSUFFICIENT RESULT
    # ------------------------------------------------------------------

    def _insufficient_result(
        self,
        reason: str,
    ) -> DCSResult:
        return DCSResult(
            status=EvidenceStatus.INSUFFICIENT,
            dcs=None,
            bid_depth=0.0,
            ask_depth=0.0,
            bid_level_count=0,
            ask_level_count=0,
            bid_hhi=None,
            ask_hhi=None,
            bid_effective_levels=None,
            ask_effective_levels=None,
            bid_entropy=None,
            ask_entropy=None,
            bid_entropy_normalized=None,
            ask_entropy_normalized=None,
            concentration_imbalance=None,
            effective_level_imbalance=None,
            bid_level_shares=(),
            ask_level_shares=(),
            calculation=(),
            observed_at=None,
            reason=reason,
        )


# ----------------------------------------------------------------------
# COMPATIBILITY ALIASES
# ----------------------------------------------------------------------

DCSConcentrationEngine = DCSEngine
DepthConcentrationEngine = DCSEngine
DepthConcentrationStructureEngine = DCSEngine
DepthConcentrationStructure = DCSEngine


__all__ = [
    "DCSInputError",
    "DCSLevel",
    "DCSResult",
    "DCSEngine",
    "DCSConcentrationEngine",
    "DepthConcentrationEngine",
    "DepthConcentrationStructureEngine",
    "DepthConcentrationStructure",
]