from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any
from pydantic import model_validator

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MarketActivityType(str, Enum):
    LARGE_VALUE = "LARGE_VALUE"
    LARGE_VOLUME = "LARGE_VOLUME"
    ABSORPTION = "ABSORPTION"
    REPLENISHMENT = "REPLENISHMENT"
    POSSIBLE_LARGE_PARTICIPANT = "POSSIBLE_LARGE_PARTICIPANT"


class ActivityDirection(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"


class ActivityEvidenceType(str, Enum):
    SIZE = "SIZE"
    VALUE = "VALUE"
    VOLUME = "VOLUME"
    TRADE_CLUSTER = "TRADE_CLUSTER"
    BID_ASK = "BID_ASK"
    ORDERBOOK = "ORDERBOOK"
    PRICE_RESPONSE = "PRICE_RESPONSE"
    ABSORPTION_PATTERN = "ABSORPTION_PATTERN"
    REPLENISHMENT_PATTERN = "REPLENISHMENT_PATTERN"
    BASELINE_DEVIATION = "BASELINE_DEVIATION"


class ActivityConfidence(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ParticipantClassification(str, Enum):
    UNKNOWN = "UNKNOWN"
    LARGE_PARTICIPANT = "LARGE_PARTICIPANT"
    POSSIBLE_LARGE_PARTICIPANT = "POSSIBLE_LARGE_PARTICIPANT"
    POSSIBLE_MARKET_MAKER = "POSSIBLE_MARKET_MAKER"
    MARKET_MAKER_CONFIRMED = "MARKET_MAKER_CONFIRMED"
class ActivityEvidence(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        use_enum_values=False,
    )

    evidence_type: ActivityEvidenceType

    description: str

    observed_value: Decimal | None = None
    baseline_value: Decimal | None = None

    ratio: Decimal | None = None

    source: str | None = None

    reference_timestamp: datetime | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    @field_validator(
        "observed_value",
        "baseline_value",
        "ratio",
        mode="before",
    )
    @classmethod
    def normalize_decimal(
        cls,
        value: Any,
    ) -> Decimal | None:
        if value is None:
            return None

        return Decimal(str(value))
class MarketActivityMarker(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        use_enum_values=False,
    )

    schema_version: str = "1.0.0"

    marker_id: str

    activity_type: MarketActivityType

    direction: ActivityDirection = (
        ActivityDirection.UNKNOWN
    )

    participant_classification: (
        ParticipantClassification
    ) = ParticipantClassification.UNKNOWN

    confidence: ActivityConfidence = (
        ActivityConfidence.LOW
    )

    market_id: str
    exchange_id: str

    instrument_id: str
    contract_id: str | None = None

    symbol: str

    timeframe: str

    detected_at: datetime

    window_start: datetime | None = None
    window_end: datetime | None = None

    reference_price: Decimal | None = None

    volume: Decimal | None = None
    value: Decimal | None = None

    baseline_volume: Decimal | None = None
    baseline_value: Decimal | None = None

    volume_ratio: Decimal | None = None
    value_ratio: Decimal | None = None

    trade_count: int | None = None

    price_impact: Decimal | None = None

    evidence: list[ActivityEvidence] = Field(
        default_factory=list
    )

    detection_rule: str

    detection_rule_version: str = "1.0.0"

    source: str

    status: str = "ACTIVE"

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    @field_validator("detected_at")
    @classmethod
    def validate_detected_at(
        cls,
        value: datetime,
    ) -> datetime:
        if (
            value.tzinfo is None
            or value.utcoffset() is None
        ):
            raise ValueError(
                "detected_at must be timezone-aware"
            )

        return value

    @field_validator(
        "window_start",
        "window_end",
    )
    @classmethod
    def validate_window_timestamp(
        cls,
        value: datetime | None,
    ) -> datetime | None:
        if value is None:
            return None

        if (
            value.tzinfo is None
            or value.utcoffset() is None
        ):
            raise ValueError(
                "activity window timestamps must be timezone-aware"
            )

        return value

    @field_validator(
        "reference_price",
        "volume",
        "value",
        "baseline_volume",
        "baseline_value",
        "volume_ratio",
        "value_ratio",
        "price_impact",
        mode="before",
    )
    @classmethod
    def normalize_numeric(
        cls,
        value: Any,
    ) -> Decimal | None:
        if value is None:
            return None

        value = Decimal(str(value))

        if value < 0:
            raise ValueError(
                "activity numeric values must not be negative"
            )

        return value

    @field_validator("trade_count")
    @classmethod
    def validate_trade_count(
        cls,
        value: int | None,
    ) -> int | None:
        if value is not None and value < 0:
            raise ValueError(
                "trade_count must not be negative"
            )

        return value

    @field_validator(
        "market_id",
        "exchange_id",
        "instrument_id",
        "symbol",
        "timeframe",
        "detection_rule",
        "source",
    )
    @classmethod
    def validate_required_text(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "required activity marker field cannot be empty"
            )

        return value
    @classmethod
    def _validate_activity_consistency(
        cls,
        values: dict[str, Any],
    ) -> dict[str, Any]:
        return values
  

    @model_validator(mode="after")
    def validate_activity_consistency(
        self,
    ) -> "MarketActivityMarker":

        if (
            self.window_start is not None
            and self.window_end is not None
            and self.window_start > self.window_end
        ):
            raise ValueError(
                "window_start must be <= window_end"
            )

        if (
            self.volume_ratio is not None
            and self.baseline_volume is not None
            and self.baseline_volume == 0
        ):
            raise ValueError(
                "volume_ratio cannot use zero baseline_volume"
            )

        if (
            self.value_ratio is not None
            and self.baseline_value is not None
            and self.baseline_value == 0
        ):
            raise ValueError(
                "value_ratio cannot use zero baseline_value"
            )

        if (
            self.activity_type
            == MarketActivityType.ABSORPTION
            and self.direction
            == ActivityDirection.UNKNOWN
        ):
            raise ValueError(
                "ABSORPTION requires a known direction"
            )

        if (
            self.activity_type
            == MarketActivityType.REPLENISHMENT
            and self.direction
            == ActivityDirection.UNKNOWN
        ):
            raise ValueError(
                "REPLENISHMENT requires a known direction"
            )

        return self