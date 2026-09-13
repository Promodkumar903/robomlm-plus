from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from typing import Any, Iterable, Mapping, Sequence

from .evidence_engine_base import (
    EvidenceEngineBase,
    EvidenceStatus,
)


@dataclass(frozen=True)
class NEDObservation:
    """
    Single executed-trade observation used by the NED engine.

    Required:
        price
        volume

    Preferred aggressor-side input:
        aggressor_side

    Quote-based classification fallback:
        bid
        ask

    aggressor_side values accepted:
        BUY / SELL
        B / S
        LONG / SHORT
        BID / ASK

    If aggressor_side is unavailable, the engine may classify using:
        price >= ask -> BUY
        price <= bid -> SELL

    A trade strictly inside the spread remains unclassified.
    """

    price: float
    volume: float
    timestamp: datetime

    aggressor_side: str | None = None
    bid: float | None = None
    ask: float | None = None

    trade_id: str | None = None
    source: str | None = None
    metadata: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class NEDResult:
    """
    Net Execution Delta result.

    NED is measured in executed volume:

        NED = aggressive_buy_volume - aggressive_sell_volume

    No normalization is applied to the primary NED value.
    """

    status: EvidenceStatus

    ned: float | None

    buy_volume: float
    sell_volume: float
    neutral_volume: float

    classified_volume: float
    total_volume: float

    buy_share: float | None
    sell_share: float | None

    execution_imbalance: float | None

    observation_count: int
    classified_observation_count: int
    unclassified_observation_count: int

    first_observed_at: datetime | None
    last_observed_at: datetime | None

    unit: str = "volume"

    reason: str | None = None

    def is_valid(self) -> bool:
        if self.status == EvidenceStatus.INVALID:
            return False

        numeric_values = (
            self.buy_volume,
            self.sell_volume,
            self.neutral_volume,
            self.classified_volume,
            self.total_volume,
        )

        if not all(isfinite(float(value)) for value in numeric_values):
            return False

        if self.buy_volume < 0.0:
            return False

        if self.sell_volume < 0.0:
            return False

        if self.neutral_volume < 0.0:
            return False

        if self.classified_volume < 0.0:
            return False

        if self.total_volume < 0.0:
            return False

        if self.ned is not None and not isfinite(float(self.ned)):
            return False

        if self.buy_share is not None:
            if not 0.0 <= self.buy_share <= 1.0:
                return False

        if self.sell_share is not None:
            if not 0.0 <= self.sell_share <= 1.0:
                return False

        if self.execution_imbalance is not None:
            if not -1.0 <= self.execution_imbalance <= 1.0:
                return False

        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "ned": self.ned,
            "buy_volume": self.buy_volume,
            "sell_volume": self.sell_volume,
            "neutral_volume": self.neutral_volume,
            "classified_volume": self.classified_volume,
            "total_volume": self.total_volume,
            "buy_share": self.buy_share,
            "sell_share": self.sell_share,
            "execution_imbalance": self.execution_imbalance,
            "observation_count": self.observation_count,
            "classified_observation_count": (
                self.classified_observation_count
            ),
            "unclassified_observation_count": (
                self.unclassified_observation_count
            ),
            "first_observed_at": (
                self.first_observed_at.isoformat()
                if self.first_observed_at is not None
                else None
            ),
            "last_observed_at": (
                self.last_observed_at.isoformat()
                if self.last_observed_at is not None
                else None
            ),
            "unit": self.unit,
            "reason": self.reason,
        }


class NEDEngine(EvidenceEngineBase):
    """
    Net Execution Delta (NED).

    Core mathematical definition:

        NED = Σ aggressive_buy_volume
              - Σ aggressive_sell_volume

    Classification priority:

        1. Explicit aggressor side.
        2. Trade price >= ask -> aggressive BUY.
        3. Trade price <= bid -> aggressive SELL.
        4. Otherwise -> unclassified / neutral.

    Important:
        - Missing side information is never guessed.
        - A trade inside the spread is not forced into BUY or SELL.
        - NED is not converted into a 0-100 score.
        - No confidence value is fabricated.
        - No minimum sample threshold is invented.
    """

    name = "NED"
    engine_name = "Net Execution Delta Engine"
    layer = "L003"
    metric = "net_execution_delta"

    _BUY_SIDES = {
        "BUY",
        "B",
        "LONG",
        "BID",
        "AGGRESSIVE_BUY",
        "AGGRESSOR_BUY",
    }

    _SELL_SIDES = {
        "SELL",
        "S",
        "SHORT",
        "ASK",
        "AGGRESSIVE_SELL",
        "AGGRESSOR_SELL",
    }

    def process(
        self,
        observations: (
            Iterable[NEDObservation | Mapping[str, Any]]
            | None
        ) = None,
        *,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> NEDResult:
        """
        Calculate NED from executed trade observations.

        Optional start_time/end_time restrict the calculation window.

        Window boundaries are inclusive.
        """

        if observations is None:
            return self._insufficient(
                "No execution observations supplied."
            )

        try:
            normalized = [
                self._normalize_observation(item)
                for item in observations
            ]
        except (TypeError, ValueError) as exc:
            return self._invalid(str(exc))

        if start_time is not None:
            start_time = self._normalize_datetime(start_time)

        if end_time is not None:
            end_time = self._normalize_datetime(end_time)

        if (
            start_time is not None
            and end_time is not None
            and end_time < start_time
        ):
            return self._invalid(
                "end_time must be greater than or equal to start_time."
            )

        filtered: list[NEDObservation] = []

        for observation in normalized:
            timestamp = observation.timestamp

            if start_time is not None and timestamp < start_time:
                continue

            if end_time is not None and timestamp > end_time:
                continue

            filtered.append(observation)

        if not filtered:
            return self._insufficient(
                "No execution observations remain in the requested window."
            )

        filtered.sort(
            key=lambda item: (
                item.timestamp,
                item.trade_id or "",
            )
        )

        return self._calculate(filtered)

    def calculate(
        self,
        observations: (
            Iterable[NEDObservation | Mapping[str, Any]]
            | None
        ) = None,
        *,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> NEDResult:
        return self.process(
            observations,
            start_time=start_time,
            end_time=end_time,
        )

    def calculate_ned(
        self,
        observations: (
            Iterable[NEDObservation | Mapping[str, Any]]
            | None
        ) = None,
        *,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> NEDResult:
        return self.process(
            observations,
            start_time=start_time,
            end_time=end_time,
        )

    def _calculate(
        self,
        observations: Sequence[NEDObservation],
    ) -> NEDResult:
        buy_volume = 0.0
        sell_volume = 0.0
        neutral_volume = 0.0
        total_volume = 0.0

        classified_observation_count = 0
        unclassified_observation_count = 0

        for observation in observations:
            volume = observation.volume
            total_volume += volume

            side = self._classify_side(observation)

            if side == "BUY":
                buy_volume += volume
                classified_observation_count += 1

            elif side == "SELL":
                sell_volume += volume
                classified_observation_count += 1

            else:
                neutral_volume += volume
                unclassified_observation_count += 1

        classified_volume = buy_volume + sell_volume

        if classified_observation_count == 0:
            return NEDResult(
                status=EvidenceStatus.INSUFFICIENT,
                ned=None,
                buy_volume=buy_volume,
                sell_volume=sell_volume,
                neutral_volume=neutral_volume,
                classified_volume=classified_volume,
                total_volume=total_volume,
                buy_share=None,
                sell_share=None,
                execution_imbalance=None,
                observation_count=len(observations),
                classified_observation_count=0,
                unclassified_observation_count=(
                    unclassified_observation_count
                ),
                first_observed_at=observations[0].timestamp,
                last_observed_at=observations[-1].timestamp,
                reason=(
                    "No observations could be classified as "
                    "aggressive BUY or aggressive SELL."
                ),
            )

        ned = buy_volume - sell_volume

        buy_share = buy_volume / classified_volume
        sell_share = sell_volume / classified_volume

        execution_imbalance = ned / classified_volume

        status = (
            EvidenceStatus.VALID
            if unclassified_observation_count == 0
            else EvidenceStatus.PARTIAL
        )

        reason = None

        if status == EvidenceStatus.PARTIAL:
            reason = (
                "Some executions could not be classified because "
                "aggressor side and usable quote information were "
                "unavailable or the trade occurred inside the spread."
            )

        result = NEDResult(
            status=status,
            ned=ned,
            buy_volume=buy_volume,
            sell_volume=sell_volume,
            neutral_volume=neutral_volume,
            classified_volume=classified_volume,
            total_volume=total_volume,
            buy_share=buy_share,
            sell_share=sell_share,
            execution_imbalance=execution_imbalance,
            observation_count=len(observations),
            classified_observation_count=(
                classified_observation_count
            ),
            unclassified_observation_count=(
                unclassified_observation_count
            ),
            first_observed_at=observations[0].timestamp,
            last_observed_at=observations[-1].timestamp,
            reason=reason,
        )

        if not result.is_valid():
            return self._invalid(
                "NED calculation produced an invalid result."
            )

        return result

    @classmethod
    def _classify_side(
        cls,
        observation: NEDObservation,
    ) -> str | None:
        """
        Determine execution side without guessing.

        Explicit aggressor side has precedence over quote inference.
        """

        if observation.aggressor_side is not None:
            side = cls._normalize_side(observation.aggressor_side)

            if side is not None:
                return side

        price = observation.price
        bid = observation.bid
        ask = observation.ask

        if bid is None or ask is None:
            return None

        if price >= ask:
            return "BUY"

        if price <= bid:
            return "SELL"

        return None

    @classmethod
    def _normalize_side(cls, value: Any) -> str | None:
        if not isinstance(value, str):
            return None

        normalized = value.strip().upper().replace("-", "_").replace(
            " ", "_"
        )

        if normalized in cls._BUY_SIDES:
            return "BUY"

        if normalized in cls._SELL_SIDES:
            return "SELL"

        return None

    @classmethod
    def _normalize_observation(
        cls,
        value: NEDObservation | Mapping[str, Any],
    ) -> NEDObservation:
        if isinstance(value, NEDObservation):
            observation = value
        elif isinstance(value, Mapping):
            observation = cls._observation_from_mapping(value)
        else:
            raise TypeError(
                "Each NED observation must be NEDObservation "
                "or a mapping."
            )

        price = cls._finite_float(
            observation.price,
            "price",
        )

        volume = cls._finite_float(
            observation.volume,
            "volume",
        )

        if price <= 0.0:
            raise ValueError("price must be greater than zero.")

        if volume < 0.0:
            raise ValueError("volume must be non-negative.")

        timestamp = cls._normalize_datetime(observation.timestamp)

        bid = None
        if observation.bid is not None:
            bid = cls._finite_float(
                observation.bid,
                "bid",
            )
            if bid <= 0.0:
                raise ValueError("bid must be greater than zero.")

        ask = None
        if observation.ask is not None:
            ask = cls._finite_float(
                observation.ask,
                "ask",
            )
            if ask <= 0.0:
                raise ValueError("ask must be greater than zero.")

        if bid is not None and ask is not None and bid > ask:
            raise ValueError(
                "bid cannot be greater than ask."
            )

        return NEDObservation(
            price=price,
            volume=volume,
            timestamp=timestamp,
            aggressor_side=observation.aggressor_side,
            bid=bid,
            ask=ask,
            trade_id=observation.trade_id,
            source=observation.source,
            metadata=(
                dict(observation.metadata)
                if observation.metadata is not None
                else None
            ),
        )

    @classmethod
    def _observation_from_mapping(
        cls,
        data: Mapping[str, Any],
    ) -> NEDObservation:
        price = cls._first_present(
            data,
            "price",
            "trade_price",
            "execution_price",
        )

        volume = cls._first_present(
            data,
            "volume",
            "trade_volume",
            "quantity",
            "qty",
        )

        timestamp = cls._first_present(
            data,
            "timestamp",
            "observed_at",
            "time",
            "ts",
        )

        aggressor_side = cls._first_present(
            data,
            "aggressor_side",
            "aggressor",
            "side",
            "trade_side",
        )

        bid = cls._first_present(
            data,
            "bid",
            "best_bid",
            "bid_price",
        )

        ask = cls._first_present(
            data,
            "ask",
            "best_ask",
            "ask_price",
        )

        trade_id = cls._first_present(
            data,
            "trade_id",
            "execution_id",
            "id",
        )

        source = cls._first_present(
            data,
            "source",
            "venue",
            "provider",
        )

        return NEDObservation(
            price=price,
            volume=volume,
            timestamp=timestamp,
            aggressor_side=aggressor_side,
            bid=bid,
            ask=ask,
            trade_id=trade_id,
            source=source,
            metadata=dict(data),
        )

    @staticmethod
    def _first_present(
        data: Mapping[str, Any],
        *keys: str,
    ) -> Any:
        for key in keys:
            if key in data:
                return data[key]

        raise ValueError(
            f"Missing required observation field; "
            f"expected one of: {', '.join(keys)}"
        )

    @staticmethod
    def _finite_float(
        value: Any,
        field_name: str,
    ) -> float:
        try:
            converted = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{field_name} must be numeric."
            ) from exc

        if not isfinite(converted):
            raise ValueError(
                f"{field_name} must be finite."
            )

        return converted

    @staticmethod
    def _normalize_datetime(
        value: datetime,
    ) -> datetime:
        if not isinstance(value, datetime):
            raise TypeError(
                "timestamp must be a datetime."
            )

        if value.tzinfo is None:
            raise ValueError(
                "Naive timestamps are not accepted."
            )

        return value.astimezone(timezone.utc)

    def _insufficient(
        self,
        reason: str,
    ) -> NEDResult:
        return NEDResult(
            status=EvidenceStatus.INSUFFICIENT,
            ned=None,
            buy_volume=0.0,
            sell_volume=0.0,
            neutral_volume=0.0,
            classified_volume=0.0,
            total_volume=0.0,
            buy_share=None,
            sell_share=None,
            execution_imbalance=None,
            observation_count=0,
            classified_observation_count=0,
            unclassified_observation_count=0,
            first_observed_at=None,
            last_observed_at=None,
            reason=reason,
        )

    def _invalid(
        self,
        reason: str,
    ) -> NEDResult:
        return NEDResult(
            status=EvidenceStatus.INVALID,
            ned=None,
            buy_volume=0.0,
            sell_volume=0.0,
            neutral_volume=0.0,
            classified_volume=0.0,
            total_volume=0.0,
            buy_share=None,
            sell_share=None,
            execution_imbalance=None,
            observation_count=0,
            classified_observation_count=0,
            unclassified_observation_count=0,
            first_observed_at=None,
            last_observed_at=None,
            reason=reason,
        )


# Compatibility aliases.
NetExecutionDeltaEngine = NEDEngine
NetExecutionDeltaEvidenceEngine = NEDEngine
ExecutionDeltaEngine = NEDEngine


def calculate_ned(
    observations: (
        Iterable[NEDObservation | Mapping[str, Any]]
        | None
    ) = None,
    *,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> NEDResult:
    """
    Convenience function for NED calculation.
    """
    return NEDEngine().process(
        observations,
        start_time=start_time,
        end_time=end_time,
    )


__all__ = [
    "NEDObservation",
    "NEDResult",
    "NEDEngine",
    "NetExecutionDeltaEngine",
    "NetExecutionDeltaEvidenceEngine",
    "ExecutionDeltaEngine",
    "calculate_ned",
]