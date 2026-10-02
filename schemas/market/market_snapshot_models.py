from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from schemas.market.market_snapshot import (
    MarketDataQualityStatus,
    MarketSessionState,
    ObservationKind,
)


class CanonicalModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        use_enum_values=False,
        json_encoders={
            Decimal: lambda value: str(value),
        },
    )


def _validate_aware_datetime(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(
            "timestamp must be timezone-aware"
        )
    return value


def _validate_decimal(
    value: Decimal | None,
) -> Decimal | None:
    if value is None:
        return None

    if not isinstance(value, Decimal):
        try:
            value = Decimal(str(value))
        except (InvalidOperation, ValueError) as exc:
            raise ValueError(
                "value must be a valid Decimal"
            ) from exc

    if not value.is_finite():
        raise ValueError(
            "Decimal value must be finite"
        )

    return value


class MarketIdentityModel(CanonicalModel):
    market: str = Field(min_length=1)
    segment: str = Field(min_length=1)
    country: str | None = None

    @field_validator("market", "segment")
    @classmethod
    def normalize_identity(cls, value: str) -> str:
        value = value.strip().upper()

        if not value:
            raise ValueError(
                "identity value must not be empty"
            )

        return value


class InstrumentIdentityModel(CanonicalModel):
    symbol: str = Field(min_length=1)
    instrument_type: str = Field(min_length=1)
    instrument_id: str = Field(min_length=1)
    asset_class: str | None = None

    @field_validator(
        "symbol",
        "instrument_type",
        "instrument_id",
    )
    @classmethod
    def normalize_identity(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "identity value must not be empty"
            )

        return value.upper()


class VenueIdentityModel(CanonicalModel):
    venue: str = Field(min_length=1)
    venue_id: str | None = None

    @field_validator("venue")
    @classmethod
    def normalize_venue(cls, value: str) -> str:
        value = value.strip().upper()

        if not value:
            raise ValueError(
                "venue must not be empty"
            )

        return value


class ContractIdentityModel(CanonicalModel):
    contract_id: str | None = None
    contract_type: str | None = None
    product_code: str | None = None

    expiry: date | None = None
    strike: Decimal | None = None
    option_type: str | None = None

    first_trade_date: date | None = None
    last_trade_date: date | None = None
    settlement_date: date | None = None

    tick_size: Decimal | None = None
    contract_size: Decimal | None = None
    currency: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    @field_validator(
        "strike",
        "tick_size",
        "contract_size",
        mode="before",
    )
    @classmethod
    def validate_decimal_fields(
        cls,
        value: Any,
    ) -> Decimal | None:
        return _validate_decimal(value)

    @field_validator(
        "contract_id",
        "contract_type",
        "product_code",
        "currency",
        "option_type",
        mode="before",
    )
    @classmethod
    def normalize_optional_strings(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value.upper() if value else None

    @model_validator(mode="after")
    def validate_contract_dates(
        self,
    ) -> "ContractIdentityModel":
        if (
            self.first_trade_date is not None
            and self.last_trade_date is not None
            and self.first_trade_date
            > self.last_trade_date
        ):
            raise ValueError(
                "first_trade_date must not be "
                "after last_trade_date"
            )

        if (
            self.expiry is not None
            and self.last_trade_date is not None
            and self.expiry < self.last_trade_date
        ):
            raise ValueError(
                "expiry must not be before "
                "last_trade_date"
            )

        return self


class MarketObservationModel(CanonicalModel):
    observed_at: datetime

    price: Decimal | None = None

    open: Decimal | None = None
    high: Decimal | None = None
    low: Decimal | None = None
    close: Decimal | None = None

    volume: Decimal | None = None
    turnover: Decimal | None = None
    transactions: int | None = None

    bid: Decimal | None = None
    ask: Decimal | None = None

    open_interest: Decimal | None = None

    window_start: datetime | None = None
    session_end_date: date | None = None

    observation_kind: ObservationKind = (
        ObservationKind.OBSERVED
    )

    fields_present: tuple[str, ...] = Field(
        default_factory=tuple
    )

    @field_validator(
        "observed_at",
        "window_start",
    )
    @classmethod
    def validate_timestamps(
        cls,
        value: datetime | None,
    ) -> datetime | None:
        if value is None:
            return None

        return _validate_aware_datetime(value)

    @field_validator(
        "price",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "turnover",
        "bid",
        "ask",
        "open_interest",
        mode="before",
    )
    @classmethod
    def validate_decimal_values(
        cls,
        value: Any,
    ) -> Decimal | None:
        return _validate_decimal(value)

    @field_validator("transactions")
    @classmethod
    def validate_transactions(
        cls,
        value: int | None,
    ) -> int | None:
        if value is not None and value < 0:
            raise ValueError(
                "transactions must not be negative"
            )

        return value

    @model_validator(mode="after")
    def validate_market_values(
        self,
    ) -> "MarketObservationModel":

        if (
            self.open is not None
            and self.high is not None
            and self.open > self.high
        ):
            raise ValueError(
                "open must not exceed high"
            )

        if (
            self.low is not None
            and self.high is not None
            and self.low > self.high
        ):
            raise ValueError(
                "low must not exceed high"
            )

        if (
            self.close is not None
            and self.high is not None
            and self.close > self.high
        ):
            raise ValueError(
                "close must not exceed high"
            )

        if (
            self.close is not None
            and self.low is not None
            and self.close < self.low
        ):
            raise ValueError(
                "close must not be below low"
            )

        if (
            self.bid is not None
            and self.ask is not None
            and self.bid > self.ask
        ):
            raise ValueError(
                "bid must not exceed ask"
            )

        if (
            self.volume is not None
            and self.volume < 0
        ):
            raise ValueError(
                "volume must not be negative"
            )

        if (
            self.turnover is not None
            and self.turnover < 0
        ):
            raise ValueError(
                "turnover must not be negative"
            )

        if (
            self.open_interest is not None
            and self.open_interest < 0
        ):
            raise ValueError(
                "open_interest must not be negative"
            )

        if (
            self.window_start is not None
            and self.window_start > self.observed_at
        ):
            raise ValueError(
                "window_start must not be after observed_at"
            )

        return self


class MarketTimingModel(CanonicalModel):
    source_timestamp: datetime
    received_timestamp: datetime
    observed_at: datetime

    window_start: datetime | None = None
    session_end_date: date | None = None

    @field_validator(
        "source_timestamp",
        "received_timestamp",
        "observed_at",
        "window_start",
    )
    @classmethod
    def validate_timestamps(
        cls,
        value: datetime | None,
    ) -> datetime | None:
        if value is None:
            return None

        return _validate_aware_datetime(value)

    @model_validator(mode="after")
    def validate_order(
        self,
    ) -> "MarketTimingModel":

        if (
            self.source_timestamp
            > self.received_timestamp
        ):
            raise ValueError(
                "source_timestamp must not be after "
                "received_timestamp"
            )

        if (
            self.received_timestamp
            > self.observed_at
        ):
            raise ValueError(
                "received_timestamp must not be after "
                "observed_at"
            )

        return self

    @property
    def latency_ms(self) -> float:
        return max(
            0.0,
            (
                self.received_timestamp
                - self.source_timestamp
            ).total_seconds()
            * 1000.0,
        )


class MarketDataQualityModel(CanonicalModel):
    source: str

    source_timestamp: datetime
    received_timestamp: datetime

    sequence: int | None = None
    latency_ms: float | None = None

    is_complete: bool = True
    is_stale: bool = False

    status: MarketDataQualityStatus = (
        MarketDataQualityStatus.VALID
    )

    usable: bool = True

    freshness_seconds: float | None = None

    missing_fields: tuple[str, ...] = Field(
        default_factory=tuple
    )

    invalid_fields: tuple[str, ...] = Field(
        default_factory=tuple
    )

    quality_flags: tuple[str, ...] = Field(
        default_factory=tuple
    )

    reasons: tuple[str, ...] = Field(
        default_factory=tuple
    )

    provider_quality_flags: tuple[str, ...] = Field(
        default_factory=tuple
    )

    @field_validator(
        "source_timestamp",
        "received_timestamp",
    )
    @classmethod
    def validate_timestamps(
        cls,
        value: datetime,
    ) -> datetime:
        return _validate_aware_datetime(value)

    @field_validator(
        "latency_ms",
        "freshness_seconds",
    )
    @classmethod
    def validate_non_negative(
        cls,
        value: float | None,
    ) -> float | None:
        if value is not None and value < 0:
            raise ValueError(
                "timing values must not be negative"
            )

        return value

    @model_validator(mode="after")
    def validate_quality(
        self,
    ) -> "MarketDataQualityModel":

        if (
            self.source_timestamp
            > self.received_timestamp
        ):
            raise ValueError(
                "source_timestamp must not be after "
                "received_timestamp"
            )

        if self.status == MarketDataQualityStatus.STALE:
            if not self.is_stale:
                raise ValueError(
                    "STALE status requires is_stale=True"
                )

        if self.status == MarketDataQualityStatus.INVALID:
            if self.usable:
                raise ValueError(
                    "INVALID data cannot be usable"
                )

        return self


class MarketProvenanceModel(CanonicalModel):
    provider: str

    endpoint: str | None = None
    provider_symbol: str | None = None
    raw_reference: str | None = None
    adapter_version: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    @field_validator("provider")
    @classmethod
    def normalize_provider(
        cls,
        value: str,
    ) -> str:
        value = value.strip().upper()

        if not value:
            raise ValueError(
                "provider must not be empty"
            )

        return value


class MarketStateModel(CanonicalModel):
    session: MarketSessionState = (
        MarketSessionState.UNKNOWN
    )

    halted: bool = False
    tradable: bool = True

    state_reason: str | None = None


class MarketSnapshotModel(CanonicalModel):
    """
    Pydantic API/serialization representation of the
    canonical ROBOMLM MarketSnapshot.

    This model contains observed provider data and
    provenance/quality metadata only.

    Intelligence and decision outputs do not belong here.
    """

    schema_version: str = "2.0.0"

    snapshot_id: str | None = None

    market: MarketIdentityModel
    instrument: InstrumentIdentityModel
    venue: VenueIdentityModel

    contract: ContractIdentityModel | None = None

    observation: MarketObservationModel

    timing: MarketTimingModel | None = None

    data_quality: MarketDataQualityModel

    provenance: MarketProvenanceModel | None = None

    state: MarketStateModel = Field(
        default_factory=MarketStateModel
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    @field_validator("schema_version")
    @classmethod
    def validate_schema_version(
        cls,
        value: str,
    ) -> str:
        if not value.strip():
            raise ValueError(
                "schema_version must not be empty"
            )

        return value.strip()

    @field_validator("snapshot_id")
    @classmethod
    def validate_snapshot_id(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError(
                "snapshot_id must not be empty"
            )

        return value

    @model_validator(mode="after")
    def validate_snapshot(
        self,
    ) -> "MarketSnapshotModel":

        observation_time = (
            self.observation.observed_at
        )

        quality_source_time = (
            self.data_quality.source_timestamp
        )

        quality_received_time = (
            self.data_quality.received_timestamp
        )

        if quality_source_time > quality_received_time:
            raise ValueError(
                "source_timestamp must not be after "
                "received_timestamp"
            )

        if quality_received_time > observation_time:
            raise ValueError(
                "received_timestamp must not be after "
                "observation.observed_at"
            )

        if self.timing is not None:
            if (
                self.timing.observed_at
                != observation_time
            ):
                raise ValueError(
                    "timing.observed_at must equal "
                    "observation.observed_at"
                )

        if self.contract is not None:
            if (
                self.instrument.instrument_type
                not in {
                    "FUTURES",
                    "FUTURE",
                    "OPTIONS",
                    "OPTION",
                }
            ):
                raise ValueError(
                    "contract metadata requires a "
                    "derivative instrument type"
                )

        return self

    def to_json_dict(self) -> dict[str, Any]:
        """
        JSON-safe serialization.

        Decimal values remain strings to prevent
        floating-point corruption.
        """

        return self.model_dump(
            mode="json"
        )

    def to_json(
        self,
        *,
        indent: int | None = None,
    ) -> str:
        return self.model_dump_json(
            indent=indent
        )