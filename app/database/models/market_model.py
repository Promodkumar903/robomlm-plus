"""
ROBOMLM PLUS
Market Database Model

Purpose:
    Define the persistent structure for market/instrument observations.

Design:
    - Stores precise market identity.
    - Separates observed market data from derived intelligence.
    - Supports OHLC, volume, liquidity and market-state metadata.
    - No decision generation.
    - No order execution.
    - Persistence is handled by repository/database layers.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Optional
from uuid import uuid4


@dataclass
class MarketRecord:
    """Structured market observation record."""

    market_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    market: str = ""
    instrument: str = ""
    venue: Optional[str] = None

    instrument_type: Optional[str] = None
    contract_id: Optional[str] = None
    expiry: Optional[str] = None

    timeframe: Optional[str] = None

    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    close_price: Optional[float] = None

    bid_price: Optional[float] = None
    ask_price: Optional[float] = None

    bid_size: Optional[float] = None
    ask_size: Optional[float] = None

    volume: Optional[float] = None
    turnover: Optional[float] = None

    volatility: Optional[float] = None
    spread: Optional[float] = None

    market_state: Optional[str] = None
    data_quality: Optional[str] = None

    source: Optional[str] = None
    observed_at: Optional[datetime] = None

    metadata: dict[str, Any] = field(default_factory=dict)

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        """Normalize and validate market fields."""

        self.market_id = str(self.market_id).strip()

        if not self.market_id:
            raise ValueError("market_id cannot be empty.")

        self.market = str(self.market).strip()
        self.instrument = str(self.instrument).strip()

        if not self.market:
            raise ValueError("market cannot be empty.")

        if not self.instrument:
            raise ValueError("instrument cannot be empty.")

        string_fields = (
            "venue",
            "instrument_type",
            "contract_id",
            "expiry",
            "timeframe",
            "market_state",
            "data_quality",
            "source",
        )

        for field_name in string_fields:
            value = getattr(self, field_name)

            if value is not None:
                setattr(
                    self,
                    field_name,
                    str(value).strip() or None,
                )

        if not isinstance(self.metadata, dict):
            self.metadata = dict(self.metadata)

        self.open_price = self._number(
            self.open_price,
            "open_price",
        )
        self.high_price = self._number(
            self.high_price,
            "high_price",
        )
        self.low_price = self._number(
            self.low_price,
            "low_price",
        )
        self.close_price = self._number(
            self.close_price,
            "close_price",
        )
        self.bid_price = self._number(
            self.bid_price,
            "bid_price",
        )
        self.ask_price = self._number(
            self.ask_price,
            "ask_price",
        )
        self.bid_size = self._number(
            self.bid_size,
            "bid_size",
        )
        self.ask_size = self._number(
            self.ask_size,
            "ask_size",
        )
        self.volume = self._number(
            self.volume,
            "volume",
        )
        self.turnover = self._number(
            self.turnover,
            "turnover",
        )
        self.volatility = self._number(
            self.volatility,
            "volatility",
        )
        self.spread = self._number(
            self.spread,
            "spread",
        )

        self._validate_non_negative(
            self.bid_size,
            "bid_size",
        )
        self._validate_non_negative(
            self.ask_size,
            "ask_size",
        )
        self._validate_non_negative(
            self.volume,
            "volume",
        )
        self._validate_non_negative(
            self.turnover,
            "turnover",
        )
        self._validate_non_negative(
            self.volatility,
            "volatility",
        )
        self._validate_non_negative(
            self.spread,
            "spread",
        )

        self._validate_ohlc()

        self.timestamp = self._normalize_datetime(
            self.timestamp
        )

        if self.observed_at is not None:
            self.observed_at = self._normalize_datetime(
                self.observed_at
            )

        self.created_at = self._normalize_datetime(
            self.created_at
        )

        self.updated_at = self._normalize_datetime(
            self.updated_at
        )

    @staticmethod
    def _number(
        value: Optional[float],
        field_name: str,
    ) -> Optional[float]:
        """Convert an optional numeric value to float."""

        if value is None:
            return None

        if isinstance(value, bool):
            raise TypeError(
                f"{field_name} must be numeric, not boolean."
            )

        try:
            return float(value)
        except (TypeError, ValueError) as exc:
            raise TypeError(
                f"{field_name} must be numeric."
            ) from exc

    @staticmethod
    def _validate_non_negative(
        value: Optional[float],
        field_name: str,
    ) -> None:
        """Reject negative values where they are not meaningful."""

        if value is not None and value < 0:
            raise ValueError(
                f"{field_name} cannot be negative."
            )

    def _validate_ohlc(self) -> None:
        """Validate available OHLC relationships."""

        prices = (
            self.open_price,
            self.high_price,
            self.low_price,
            self.close_price,
        )

        if all(price is not None for price in prices):
            assert self.high_price is not None
            assert self.low_price is not None
            assert self.open_price is not None
            assert self.close_price is not None

            if self.high_price < self.low_price:
                raise ValueError(
                    "high_price cannot be lower than low_price."
                )

            if not (
                self.low_price
                <= self.open_price
                <= self.high_price
            ):
                raise ValueError(
                    "open_price must be within high/low range."
                )

            if not (
                self.low_price
                <= self.close_price
                <= self.high_price
            ):
                raise ValueError(
                    "close_price must be within high/low range."
                )

        if (
            self.bid_price is not None
            and self.ask_price is not None
            and self.bid_price > self.ask_price
        ):
            raise ValueError(
                "bid_price cannot be greater than ask_price."
            )

    @staticmethod
    def _normalize_datetime(
        value: datetime,
    ) -> datetime:
        """Ensure datetime values are timezone-aware UTC."""

        if not isinstance(value, datetime):
            raise TypeError(
                "Datetime value must be a datetime instance."
            )

        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)

    def touch(self) -> None:
        """Update the modification timestamp."""

        self.updated_at = datetime.now(timezone.utc)

    def mid_price(self) -> Optional[float]:
        """Return bid/ask midpoint when both sides are available."""

        if (
            self.bid_price is None
            or self.ask_price is None
        ):
            return None

        return (
            self.bid_price + self.ask_price
        ) / 2.0

    def spread_value(self) -> Optional[float]:
        """Return absolute bid/ask spread."""

        if (
            self.bid_price is None
            or self.ask_price is None
        ):
            return None

        return self.ask_price - self.bid_price

    def spread_percentage(self) -> Optional[float]:
        """Return spread as a percentage of midpoint."""

        midpoint = self.mid_price()

        if midpoint is None or midpoint == 0:
            return None

        spread = self.spread_value()

        if spread is None:
            return None

        return (spread / midpoint) * 100.0

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable dictionary representation."""

        data = asdict(self)

        data["timestamp"] = self.timestamp.isoformat()
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()

        if self.observed_at is not None:
            data["observed_at"] = self.observed_at.isoformat()

        return data

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "MarketRecord":
        """Create a market record from a mapping."""

        if not isinstance(data, Mapping):
            raise TypeError(
                "data must be a mapping."
            )

        values = dict(data)

        for field_name in (
            "timestamp",
            "observed_at",
            "created_at",
            "updated_at",
        ):
            value = values.get(field_name)

            if isinstance(value, str):
                values[field_name] = (
                    datetime.fromisoformat(value)
                )

        return cls(**values)

    def with_metadata(
        self,
        key: str,
        value: Any,
    ) -> "MarketRecord":
        """Return a copy containing additional metadata."""

        key = str(key).strip()

        if not key:
            raise ValueError(
                "Metadata key cannot be empty."
            )

        copied_metadata = dict(self.metadata)
        copied_metadata[key] = value

        return MarketRecord(
            market_id=self.market_id,
            timestamp=self.timestamp,
            market=self.market,
            instrument=self.instrument,
            venue=self.venue,
            instrument_type=self.instrument_type,
            contract_id=self.contract_id,
            expiry=self.expiry,
            timeframe=self.timeframe,
            open_price=self.open_price,
            high_price=self.high_price,
            low_price=self.low_price,
            close_price=self.close_price,
            bid_price=self.bid_price,
            ask_price=self.ask_price,
            bid_size=self.bid_size,
            ask_size=self.ask_size,
            volume=self.volume,
            turnover=self.turnover,
            volatility=self.volatility,
            spread=self.spread,
            market_state=self.market_state,
            data_quality=self.data_quality,
            source=self.source,
            observed_at=self.observed_at,
            metadata=copied_metadata,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


def create_market_record(
    *,
    market: str,
    instrument: str,
    venue: Optional[str] = None,
    instrument_type: Optional[str] = None,
    contract_id: Optional[str] = None,
    expiry: Optional[str] = None,
    timeframe: Optional[str] = None,
    open_price: Optional[float] = None,
    high_price: Optional[float] = None,
    low_price: Optional[float] = None,
    close_price: Optional[float] = None,
    bid_price: Optional[float] = None,
    ask_price: Optional[float] = None,
    bid_size: Optional[float] = None,
    ask_size: Optional[float] = None,
    volume: Optional[float] = None,
    turnover: Optional[float] = None,
    volatility: Optional[float] = None,
    spread: Optional[float] = None,
    market_state: Optional[str] = None,
    data_quality: Optional[str] = None,
    source: Optional[str] = None,
    observed_at: Optional[datetime] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> MarketRecord:
    """Convenience factory for creating market records."""

    return MarketRecord(
        market=market,
        instrument=instrument,
        venue=venue,
        instrument_type=instrument_type,
        contract_id=contract_id,
        expiry=expiry,
        timeframe=timeframe,
        open_price=open_price,
        high_price=high_price,
        low_price=low_price,
        close_price=close_price,
        bid_price=bid_price,
        ask_price=ask_price,
        bid_size=bid_size,
        ask_size=ask_size,
        volume=volume,
        turnover=turnover,
        volatility=volatility,
        spread=spread,
        market_state=market_state,
        data_quality=data_quality,
        source=source,
        observed_at=observed_at,
        metadata=dict(metadata or {}),
    )


__all__ = [
    "MarketRecord",
    "create_market_record",
]