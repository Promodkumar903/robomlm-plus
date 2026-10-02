from __future__ import annotations

import json
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Any, Mapping

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


# ============================================================================
# ENUMS
# ============================================================================


class MarketDataQualityStatusModel(str, Enum):
    VALID = "VALID"
    DEGRADED = "DEGRADED"
    STALE = "STALE"
    INVALID = "INVALID"


class MarketSessionStateModel(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    PRE_OPEN = "pre_open"
    POST_CLOSE = "post_close"
    HALTED = "halted"
    UNKNOWN = "unknown"


class InstrumentTypeModel(str, Enum):
    EQUITY = "EQUITY"
    INDEX = "INDEX"
    FUTURES = "FUTURES"
    FUTURE = "FUTURE"
    OPTIONS = "OPTIONS"
    OPTION = "OPTION"
    SPOT = "SPOT"
    FOREX = "FOREX"
    CRYPTO = "CRYPTO"
    COMMODITY = "COMMODITY"
    ETF = "ETF"
    FUND = "FUND"
    BOND = "BOND"
    UNKNOWN = "UNKNOWN"


# ============================================================================
# COMMON CONFIG
# ============================================================================


PYDANTIC_SCHEMA_VERSION = "1.0.0"


class MarketSnapshotBaseModel(BaseModel):
    model_config = ConfigDict(
        use_enum_values=False,
        validate_assignment=True,
        extra="forbid",
        populate_by_name=True,
    )


# ============================================================================
# COMMON HELPERS
# ============================================================================


def require_timezone_aware(value: datetime) -> datetime:
    """
    Require a timezone-aware datetime.

    Naive datetimes are rejected because market timestamps must have an
    unambiguous UTC/offset interpretation.
    """
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(
            "timestamp must be timezone-aware"
        )

    return value


def normalize_decimal(
    value: Decimal | int | float | str | None,
) -> Decimal | None:
    """
    Convert numeric input into Decimal without silently accepting invalid
    values.
    """
    if value is None:
        return None

    if isinstance(value, Decimal):
        return value

    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(
            f"invalid decimal value: {value!r}"
        ) from exc


def require_non_negative(
    value: Decimal | int | float | str | None,
) -> Decimal | None:
    value = normalize_decimal(value)

    if value is not None and value < 0:
        raise ValueError(
            "value must be non-negative"
        )

    return value


def require_non_negative_int(
    value: int | None,
) -> int | None:
    if value is not None and value < 0:
        raise ValueError(
            "value must be non-negative"
        )

    return value


# ============================================================================
# MARKET IDENTITY
# ============================================================================


class MarketIdentityModel(MarketSnapshotBaseModel):
    market: str
    segment: str
    country: str = "GLOBAL"

    @field_validator(
        "market",
        "segment",
        "country",
    )
    @classmethod
    def validate_identity_text(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "identity value must not be empty"
            )

        return value


# ============================================================================
# INSTRUMENT IDENTITY
# ============================================================================


class InstrumentIdentityModel(MarketSnapshotBaseModel):
    symbol: str
    instrument_type: InstrumentTypeModel = (
        InstrumentTypeModel.UNKNOWN
    )
    instrument_id: str | None = None
    asset_class: str | None = None

    @field_validator("symbol")
    @classmethod
    def validate_symbol(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "symbol must not be empty"
            )

        return value

    @field_validator(
        "instrument_id",
        "asset_class",
    )
    @classmethod
    def validate_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value or None


# ============================================================================
# VENUE IDENTITY
# ============================================================================


class VenueIdentityModel(MarketSnapshotBaseModel):
    venue: str
    venue_id: str | None = None

    @field_validator("venue")
    @classmethod
    def validate_venue(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "venue must not be empty"
            )

        return value

    @field_validator("venue_id")
    @classmethod
    def validate_venue_id(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value or None


# ============================================================================
# CONTRACT IDENTITY
# ============================================================================


class ContractIdentityModel(MarketSnapshotBaseModel):
    contract_id: str
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

    @field_validator("contract_id")
    @classmethod
    def validate_contract_id(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "contract_id must not be empty"
            )

        return value

    @field_validator(
        "contract_type",
        "product_code",
        "option_type",
        "currency",
    )
    @classmethod
    def validate_optional_contract_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value or None

    @field_validator(
        "strike",
        "tick_size",
        "contract_size",
    )
    @classmethod
    def validate_contract_decimal(
        cls,
        value: Decimal | None,
    ) -> Decimal | None:
        return require_non_negative(value)

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
                "first_trade_date must be <= last_trade_date"
            )

        return self
# ============================================================================
# MARKET OBSERVATION
# ============================================================================


class MarketObservationModel(MarketSnapshotBaseModel):
    """
    Provider-neutral market observation.

    Provider-supplied values remain observed.
    Calculated values must not be silently inserted here as observed data.
    """

    observed_at: datetime | None = None

    window_start: datetime | None = None
    session_end_date: date | None = None

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

    observation_kind: str = "observed"

    fields_present: tuple[str, ...] = Field(
        default_factory=tuple
    )

    @field_validator(
        "observed_at",
        "window_start",
    )
    @classmethod
    def validate_observation_timestamp(
        cls,
        value: datetime | None,
    ) -> datetime | None:
        if value is None:
            return None

        return require_timezone_aware(value)

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
    )
    @classmethod
    def validate_observation_decimal(
        cls,
        value: Decimal | None,
    ) -> Decimal | None:
        return require_non_negative(value)

    @field_validator("transactions")
    @classmethod
    def validate_transactions(
        cls,
        value: int | None,
    ) -> int | None:
        return require_non_negative_int(value)

    @field_validator("observation_kind")
    @classmethod
    def validate_observation_kind(
        cls,
        value: str,
    ) -> str:
        value = value.strip().lower()

        allowed = {
            "observed",
            "derived",
            "estimated",
            "simulated",
        }

        if value not in allowed:
            raise ValueError(
                "observation_kind must be one of: "
                "observed, derived, estimated, simulated"
            )

        return value

    @field_validator("fields_present")
    @classmethod
    def validate_fields_present(
        cls,
        value: tuple[str, ...],
    ) -> tuple[str, ...]:
        normalized: list[str] = []

        for field_name in value:
            field_name = field_name.strip()

            if not field_name:
                raise ValueError(
                    "fields_present cannot contain empty values"
                )

            normalized.append(field_name)

        return tuple(dict.fromkeys(normalized))

    @model_validator(mode="after")
    def validate_ohlc_relationships(
        self,
    ) -> "MarketObservationModel":
        values = (
            self.open,
            self.high,
            self.low,
            self.close,
        )

        if all(value is not None for value in values):
            assert self.open is not None
            assert self.high is not None
            assert self.low is not None
            assert self.close is not None

            if self.high < self.low:
                raise ValueError(
                    "high must be >= low"
                )

            if self.high < self.open:
                raise ValueError(
                    "high must be >= open"
                )

            if self.high < self.close:
                raise ValueError(
                    "high must be >= close"
                )

            if self.low > self.open:
                raise ValueError(
                    "low must be <= open"
                )

            if self.low > self.close:
                raise ValueError(
                    "low must be <= close"
                )

        return self

    @model_validator(mode="after")
    def validate_bid_ask(
        self,
    ) -> "MarketObservationModel":
        if (
            self.bid is not None
            and self.ask is not None
            and self.bid > self.ask
        ):
            raise ValueError(
                "bid must be <= ask"
            )

        return self

    @model_validator(mode="after")
    def validate_observation_window(
        self,
    ) -> "MarketObservationModel":
        if (
            self.window_start is not None
            and self.observed_at is not None
            and self.window_start > self.observed_at
        ):
            raise ValueError(
                "window_start must be <= observed_at"
            )

        return self


# ============================================================================
# MARKET DATA QUALITY
# ============================================================================


class MarketDataQualityModel(MarketSnapshotBaseModel):
    """
    Transport-level quality information for a market observation.

    This model is intentionally separate from:
        schemas.market.data_quality.DataQuality

    It represents the quality attached specifically to MarketSnapshot.
    """

    source: str

    source_timestamp: datetime
    received_timestamp: datetime

    sequence: int | None = None

    latency_ms: Decimal | None = None

    is_complete: bool = True
    is_stale: bool = False

    status: MarketDataQualityStatusModel = (
        MarketDataQualityStatusModel.VALID
    )

    usable: bool = True

    freshness_seconds: Decimal | None = None

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

    @field_validator("source")
    @classmethod
    def validate_source(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "source must not be empty"
            )

        return value

    @field_validator(
        "source_timestamp",
        "received_timestamp",
    )
    @classmethod
    def validate_quality_timestamp(
        cls,
        value: datetime,
    ) -> datetime:
        return require_timezone_aware(value)

    @field_validator("sequence")
    @classmethod
    def validate_sequence(
        cls,
        value: int | None,
    ) -> int | None:
        return require_non_negative_int(value)

    @field_validator("latency_ms")
    @classmethod
    def validate_latency(
        cls,
        value: Decimal | None,
    ) -> Decimal | None:
        return require_non_negative(value)

    @field_validator("freshness_seconds")
    @classmethod
    def validate_freshness(
        cls,
        value: Decimal | None,
    ) -> Decimal | None:
        return require_non_negative(value)

    @field_validator(
        "missing_fields",
        "invalid_fields",
        "quality_flags",
        "reasons",
        "provider_quality_flags",
    )
    @classmethod
    def validate_quality_lists(
        cls,
        value: tuple[str, ...],
    ) -> tuple[str, ...]:
        normalized: list[str] = []

        for item in value:
            item = item.strip()

            if not item:
                raise ValueError(
                    "quality list cannot contain empty values"
                )

            normalized.append(item)

        return tuple(dict.fromkeys(normalized))

    @model_validator(mode="after")
    def validate_quality_consistency(
        self,
    ) -> "MarketDataQualityModel":
        if (
            self.source_timestamp
            > self.received_timestamp
        ):
            raise ValueError(
                "source_timestamp must be <= received_timestamp"
            )

        if self.is_stale:
            if self.status == MarketDataQualityStatusModel.VALID:
                raise ValueError(
                    "stale data cannot have VALID quality status"
                )

        if (
            self.status
            == MarketDataQualityStatusModel.INVALID
            and self.usable
        ):
            raise ValueError(
                "INVALID quality data cannot be usable"
            )

        if (
            self.status
            == MarketDataQualityStatusModel.STALE
            and not self.is_stale
        ):
            raise ValueError(
                "STALE quality status requires is_stale=True"
            )

        if (
            self.status
            == MarketDataQualityStatusModel.VALID
            and self.is_stale
        ):
            raise ValueError(
                "VALID quality status requires is_stale=False"
            )

        return self


# ============================================================================
# MARKET TIMING
# ============================================================================


class MarketTimingModel(MarketSnapshotBaseModel):
    """
    Explicit timing boundary for source, receipt and observation timestamps.
    """

    source_timestamp: datetime
    received_timestamp: datetime

    observed_at: datetime

    checked_at: datetime | None = None

    latency_ms: Decimal | None = None

    freshness_seconds: Decimal | None = None

    @field_validator(
        "source_timestamp",
        "received_timestamp",
        "observed_at",
        "checked_at",
    )
    @classmethod
    def validate_timing_timestamp(
        cls,
        value: datetime | None,
    ) -> datetime | None:
        if value is None:
            return None

        return require_timezone_aware(value)

    @field_validator("latency_ms")
    @classmethod
    def validate_timing_latency(
        cls,
        value: Decimal | None,
    ) -> Decimal | None:
        return require_non_negative(value)

    @field_validator("freshness_seconds")
    @classmethod
    def validate_timing_freshness(
        cls,
        value: Decimal | None,
    ) -> Decimal | None:
        return require_non_negative(value)

    @model_validator(mode="after")
    def validate_timing_order(
        self,
    ) -> "MarketTimingModel":
        if (
            self.source_timestamp
            > self.received_timestamp
        ):
            raise ValueError(
                "source_timestamp must be <= received_timestamp"
            )

        if (
            self.received_timestamp
            > self.observed_at
        ):
            raise ValueError(
                "received_timestamp must be <= observed_at"
            )

        if (
            self.checked_at is not None
            and self.observed_at > self.checked_at
        ):
            raise ValueError(
                "observed_at must be <= checked_at"
            )

        return self
# ============================================================================
# MARKET PROVENANCE
# ============================================================================


class MarketProvenanceModel(MarketSnapshotBaseModel):
    """
    Provenance describing where the normalized observation came from.
    """

    provider: str

    endpoint: str | None = None

    provider_symbol: str | None = None

    raw_reference: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    @field_validator("provider")
    @classmethod
    def validate_provider(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "provider must not be empty"
            )

        return value

    @field_validator(
        "endpoint",
        "provider_symbol",
        "raw_reference",
    )
    @classmethod
    def validate_optional_provenance_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value or None


# ============================================================================
# MARKET STATE
# ============================================================================


class MarketStateModel(MarketSnapshotBaseModel):
    """
    Tradability/session state of the instrument at observation time.
    """

    session: MarketSessionStateModel = (
        MarketSessionStateModel.UNKNOWN
    )

    halted: bool = False

    tradable: bool = True

    state_reason: str | None = None

    @field_validator("state_reason")
    @classmethod
    def validate_state_reason(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value or None

    @model_validator(mode="after")
    def validate_halted_state(
        self,
    ) -> "MarketStateModel":
        if self.halted and self.tradable:
            raise ValueError(
                "halted market cannot be tradable"
            )

        return self


# ============================================================================
# MARKET SNAPSHOT
# ============================================================================


class MarketSnapshotModel(MarketSnapshotBaseModel):
    """
    Canonical Pydantic representation of MarketSnapshot.

    This is the provider-neutral transport/serialization model.

    It does not replace:
        schemas.market.market_snapshot.MarketSnapshot

    The domain dataclass remains authoritative for existing domain logic.
    """

    schema_version: str = PYDANTIC_SCHEMA_VERSION

    snapshot_id: str | None = None

    market: MarketIdentityModel

    instrument: InstrumentIdentityModel

    venue: VenueIdentityModel

    contract: ContractIdentityModel | None = None

    observed_at: datetime

    observation: MarketObservationModel

    timing: MarketTimingModel

    data_quality: MarketDataQualityModel

    provenance: MarketProvenanceModel

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
        value = value.strip()

        if not value:
            raise ValueError(
                "schema_version must not be empty"
            )

        return value

    @field_validator("snapshot_id")
    @classmethod
    def validate_snapshot_id(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value or None

    @field_validator("observed_at")
    @classmethod
    def validate_observed_at(
        cls,
        value: datetime,
    ) -> datetime:
        return require_timezone_aware(value)

    # ------------------------------------------------------------------------
    # Cross-field validation
    # ------------------------------------------------------------------------

    @model_validator(mode="after")
    def validate_snapshot_timing(
        self,
    ) -> "MarketSnapshotModel":
        """
        The top-level observed_at must agree with the timing boundary.
        """

        if self.observed_at != self.timing.observed_at:
            raise ValueError(
                "observed_at must match timing.observed_at"
            )

        return self

    @model_validator(mode="after")
    def validate_observation_timing(
        self,
    ) -> "MarketSnapshotModel":
        """
        If the observation contains its own timestamp, it must agree with
        the canonical snapshot observation time.
        """

        if (
            self.observation.observed_at is not None
            and self.observation.observed_at
            != self.observed_at
        ):
            raise ValueError(
                "observation.observed_at must match "
                "MarketSnapshot.observed_at"
            )

        return self

    @model_validator(mode="after")
    def validate_quality_timing(
        self,
    ) -> "MarketSnapshotModel":
        """
        Quality timestamps and canonical timing must remain consistent.
        """

        if (
            self.data_quality.source_timestamp
            != self.timing.source_timestamp
        ):
            raise ValueError(
                "data_quality.source_timestamp must match "
                "timing.source_timestamp"
            )

        if (
            self.data_quality.received_timestamp
            != self.timing.received_timestamp
        ):
            raise ValueError(
                "data_quality.received_timestamp must match "
                "timing.received_timestamp"
            )

        return self

    @model_validator(mode="after")
    def validate_derivative_contract(
        self,
    ) -> "MarketSnapshotModel":
        """
        Derivative instruments require contract identity.

        Spot/equity/index/forex/crypto instruments may legitimately have
        contract=None.
        """

        instrument_type = (
            self.instrument.instrument_type
        )

        derivative_types = {
            InstrumentTypeModel.FUTURES,
            InstrumentTypeModel.FUTURE,
            InstrumentTypeModel.OPTIONS,
            InstrumentTypeModel.OPTION,
        }

        if (
            instrument_type in derivative_types
            and self.contract is None
        ):
            raise ValueError(
                "derivative instrument requires contract metadata"
            )

        return self

    @model_validator(mode="after")
    def validate_option_contract(
        self,
    ) -> "MarketSnapshotModel":
        """
        Options should carry option-specific contract metadata.
        """

        instrument_type = (
            self.instrument.instrument_type
        )

        option_types = {
            InstrumentTypeModel.OPTIONS,
            InstrumentTypeModel.OPTION,
        }

        if instrument_type in option_types:
            if self.contract is None:
                raise ValueError(
                    "option instrument requires contract metadata"
                )

            if self.contract.option_type is None:
                raise ValueError(
                    "option instrument requires option_type"
                )

            if self.contract.strike is None:
                raise ValueError(
                    "option instrument requires strike"
                )

        return self

    @model_validator(mode="after")
    def validate_quality_state(
        self,
    ) -> "MarketSnapshotModel":
        """
        Invalid market data must not be exposed as usable.
        """

        if (
            self.data_quality.status
            == MarketDataQualityStatusModel.INVALID
            and self.data_quality.usable
        ):
            raise ValueError(
                "INVALID market data cannot be usable"
            )

        return self

    @model_validator(mode="after")
    def validate_stale_state(
        self,
    ) -> "MarketSnapshotModel":
        """
        STALE quality must agree with the stale flag.
        """

        if (
            self.data_quality.status
            == MarketDataQualityStatusModel.STALE
            and not self.data_quality.is_stale
        ):
            raise ValueError(
                "STALE quality status requires is_stale=True"
            )

        return self

    @model_validator(mode="after")
    def validate_identity_consistency(
        self,
    ) -> "MarketSnapshotModel":
        """
        Ensure the instrument identity is internally usable.
        """

        if (
            self.instrument.instrument_id is None
            and not self.instrument.symbol
        ):
            raise ValueError(
                "instrument requires symbol or instrument_id"
            )

        return self

    # ------------------------------------------------------------------------
    # Serialization helpers
    # ------------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """
        JSON-compatible dictionary.

        Enums become their string values and Decimal/datetime values are
        converted into JSON-compatible representations.
        """

        return self.model_dump(mode="json")

    def to_json(self) -> str:
        """
        JSON string representation of the canonical snapshot.
        """

        return self.model_dump_json()

    def to_pretty_json(self) -> str:
        """
        Human-readable JSON representation.
        """

        return json.dumps(
            self.to_dict(),
            indent=2,
            ensure_ascii=False,
        )

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, Any],
    ) -> "MarketSnapshotModel":
        """
        Construct a canonical model from a dictionary.
        """

        return cls.model_validate(
            dict(payload)
        )
# ============================================================================
# DOMAIN CONVERSION
# ============================================================================


def _domain_instrument_type_to_model(
    value: Any,
) -> InstrumentTypeModel:
    """
    Convert an existing domain instrument type into the Pydantic enum.

    The domain currently stores instrument_type as a string, while some
    future/alternate domain versions may expose an Enum.
    """

    if isinstance(value, InstrumentTypeModel):
        return value

    if isinstance(value, Enum):
        value = value.value

    if value is None:
        return InstrumentTypeModel.UNKNOWN

    normalized = str(value).strip().upper()

    try:
        return InstrumentTypeModel(normalized)
    except ValueError:
        return InstrumentTypeModel.UNKNOWN


def _domain_session_to_model(
    value: Any,
) -> MarketSessionStateModel:
    """
    Convert domain MarketSessionState into the Pydantic enum.
    """

    if isinstance(value, MarketSessionStateModel):
        return value

    if isinstance(value, Enum):
        value = value.value

    if value is None:
        return MarketSessionStateModel.UNKNOWN

    normalized = str(value).strip().lower()

    try:
        return MarketSessionStateModel(normalized)
    except ValueError:
        return MarketSessionStateModel.UNKNOWN


def _quality_status_from_domain(
    data_quality: Any,
) -> MarketDataQualityStatusModel:
    """
    Derive a quality status from the existing domain quality object.

    The current domain MarketDataQuality does not necessarily expose a
    dedicated status field, so status must NOT be hardcoded to VALID.
    """

    status = getattr(
        data_quality,
        "status",
        None,
    )

    if isinstance(status, MarketDataQualityStatusModel):
        return status

    if isinstance(status, Enum):
        status = status.value

    if status is not None:
        try:
            return MarketDataQualityStatusModel(
                str(status).strip().upper()
            )
        except ValueError:
            pass

    is_stale = bool(
        getattr(
            data_quality,
            "is_stale",
            False,
        )
    )

    is_complete = bool(
        getattr(
            data_quality,
            "is_complete",
            True,
        )
    )

    quality_flags = tuple(
        getattr(
            data_quality,
            "quality_flags",
            (),
        )
        or ()
    )

    if is_stale:
        return MarketDataQualityStatusModel.STALE

    if not is_complete or quality_flags:
        return MarketDataQualityStatusModel.DEGRADED

    return MarketDataQualityStatusModel.VALID


def _field_exists(
    model_type: type[Any],
    field_name: str,
) -> bool:
    """
    Compatibility helper for dataclass/model versions.

    This allows the Pydantic transport model to work with the current
    MarketSnapshot dataclass even when newer transport-only fields exist.
    """

    dataclass_fields = getattr(
        model_type,
        "__dataclass_fields__",
        None,
    )

    if dataclass_fields is not None:
        return field_name in dataclass_fields

    model_fields = getattr(
        model_type,
        "model_fields",
        None,
    )

    if model_fields is not None:
        return field_name in model_fields

    return False


# ============================================================================
# FROM DOMAIN
# ============================================================================


@classmethod
def _market_snapshot_from_domain(
    cls,
    snapshot: Any,
) -> "MarketSnapshotModel":
    """
    Convert the existing domain MarketSnapshot dataclass into the Pydantic
    canonical transport model.

    This function intentionally reads the domain object instead of
    reconstructing values from provider responses.
    """

    domain_market = snapshot.market
    domain_instrument = snapshot.instrument
    domain_venue = snapshot.venue
    domain_observation = snapshot.observation
    domain_quality = snapshot.data_quality
    domain_state = snapshot.state
    domain_contract = getattr(
        snapshot,
        "contract",
        None,
    )

    observed_at = require_timezone_aware(
        domain_observation.observed_at
    )

    # ------------------------------------------------------------------------
    # Observation
    # ------------------------------------------------------------------------

    observation_observed_at = observed_at

    observation = MarketObservationModel(
        observed_at=observation_observed_at,
        window_start=getattr(
            domain_observation,
            "window_start",
            None,
        ),
        session_end_date=getattr(
            domain_observation,
            "session_end_date",
            None,
        ),
        price=getattr(
            domain_observation,
            "price",
            None,
        ),
        open=getattr(
            domain_observation,
            "open",
            None,
        ),
        high=getattr(
            domain_observation,
            "high",
            None,
        ),
        low=getattr(
            domain_observation,
            "low",
            None,
        ),
        close=getattr(
            domain_observation,
            "close",
            None,
        ),
        volume=getattr(
            domain_observation,
            "volume",
            None,
        ),
        turnover=getattr(
            domain_observation,
            "turnover",
            None,
        ),
        transactions=getattr(
            domain_observation,
            "transactions",
            None,
        ),
        bid=getattr(
            domain_observation,
            "bid",
            None,
        ),
        ask=getattr(
            domain_observation,
            "ask",
            None,
        ),
        open_interest=getattr(
            domain_observation,
            "open_interest",
            None,
        ),
        observation_kind=getattr(
            getattr(
                domain_observation,
                "observation_kind",
                "observed",
            ),
            "value",
            getattr(
                domain_observation,
                "observation_kind",
                "observed",
            ),
        ),
        fields_present=tuple(
            getattr(
                domain_observation,
                "fields_present",
                (),
            )
            or ()
        ),
    )

    # ------------------------------------------------------------------------
    # Timing
    # ------------------------------------------------------------------------

    source_timestamp = require_timezone_aware(
        domain_quality.source_timestamp
    )

    received_timestamp = require_timezone_aware(
        domain_quality.received_timestamp
    )

    checked_at = received_timestamp

    timing = MarketTimingModel(
        source_timestamp=source_timestamp,
        received_timestamp=received_timestamp,
        observed_at=observed_at,
        checked_at=checked_at,
        latency_ms=getattr(
            domain_quality,
            "latency_ms",
            None,
        ),
    )

    # ------------------------------------------------------------------------
    # Quality
    # ------------------------------------------------------------------------

    quality_status = _quality_status_from_domain(
        domain_quality
    )

    is_stale = bool(
        getattr(
            domain_quality,
            "is_stale",
            False,
        )
    )

    is_complete = bool(
        getattr(
            domain_quality,
            "is_complete",
            True,
        )
    )

    quality_flags = tuple(
        getattr(
            domain_quality,
            "quality_flags",
            (),
        )
        or ()
    )

    usable = (
        quality_status
        not in {
            MarketDataQualityStatusModel.INVALID,
            MarketDataQualityStatusModel.STALE,
        }
    )

    data_quality = MarketDataQualityModel(
        source=domain_quality.source,
        source_timestamp=source_timestamp,
        received_timestamp=received_timestamp,
        sequence=getattr(
            domain_quality,
            "sequence",
            None,
        ),
        latency_ms=getattr(
            domain_quality,
            "latency_ms",
            None,
        ),
        is_complete=is_complete,
        is_stale=is_stale,
        status=quality_status,
        usable=usable,
        freshness_seconds=None,
        missing_fields=(),
        invalid_fields=(),
        quality_flags=quality_flags,
        reasons=(),
        provider_quality_flags=(),
    )

    # ------------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------------

    state = MarketStateModel(
        session=_domain_session_to_model(
            domain_state.session
        ),
        halted=bool(
            getattr(
                domain_state,
                "halted",
                False,
            )
        ),
        tradable=bool(
            getattr(
                domain_state,
                "tradable",
                True,
            )
        ),
        state_reason=getattr(
            domain_state,
            "state_reason",
            None,
        ),
    )

    # ------------------------------------------------------------------------
    # Contract
    # ------------------------------------------------------------------------

    contract = None

    if domain_contract is not None:
        contract = ContractIdentityModel(
            contract_id=domain_contract.contract_id,
            contract_type=getattr(
                domain_contract,
                "contract_type",
                None,
            ),
            product_code=getattr(
                domain_contract,
                "product_code",
                None,
            ),
            expiry=getattr(
                domain_contract,
                "expiry",
                None,
            ),
            strike=getattr(
                domain_contract,
                "strike",
                None,
            ),
            option_type=getattr(
                domain_contract,
                "option_type",
                None,
            ),
            first_trade_date=getattr(
                domain_contract,
                "first_trade_date",
                None,
            ),
            last_trade_date=getattr(
                domain_contract,
                "last_trade_date",
                None,
            ),
            settlement_date=getattr(
                domain_contract,
                "settlement_date",
                None,
            ),
            tick_size=getattr(
                domain_contract,
                "tick_size",
                None,
            ),
            contract_size=getattr(
                domain_contract,
                "contract_size",
                None,
            ),
            currency=getattr(
                domain_contract,
                "currency",
                None,
            ),
            metadata=dict(
                getattr(
                    domain_contract,
                    "metadata",
                    {},
                )
                or {}
            ),
        )

    # ------------------------------------------------------------------------
    # Provenance
    # ------------------------------------------------------------------------

    provenance = MarketProvenanceModel(
        provider=domain_quality.source,
        endpoint=None,
        provider_symbol=domain_instrument.symbol,
        raw_reference=None,
        metadata={
            "market": domain_market.market,
            "segment": domain_market.segment,
            "country": domain_market.country,
            "venue": domain_venue.venue,
            "venue_id": domain_venue.venue_id,
        },
    )

    return cls(
        schema_version=PYDANTIC_SCHEMA_VERSION,
        snapshot_id=getattr(
            snapshot,
            "snapshot_id",
            None,
        ),
        market=MarketIdentityModel(
            market=domain_market.market,
            segment=domain_market.segment,
            country=domain_market.country,
        ),
        instrument=InstrumentIdentityModel(
            symbol=domain_instrument.symbol,
            instrument_type=_domain_instrument_type_to_model(
                domain_instrument.instrument_type
            ),
            instrument_id=getattr(
                domain_instrument,
                "instrument_id",
                None,
            ),
            asset_class=getattr(
                domain_instrument,
                "asset_class",
                None,
            ),
        ),
        venue=VenueIdentityModel(
            venue=domain_venue.venue,
            venue_id=getattr(
                domain_venue,
                "venue_id",
                None,
            ),
        ),
        contract=contract,
        observed_at=observed_at,
        observation=observation,
        timing=timing,
        data_quality=data_quality,
        provenance=provenance,
        state=state,
        metadata=dict(
            getattr(
                snapshot,
                "metadata",
                {},
            )
            or {}
        ),
    )


# Attach the classmethod to the model.
MarketSnapshotModel.from_domain = _market_snapshot_from_domain


# ============================================================================
# TO DOMAIN
# ============================================================================


def _model_observation_to_domain(
    model: MarketObservationModel,
    domain_type: type[Any],
) -> Any:
    """
    Convert the Pydantic observation into the currently available domain
    MarketObservation constructor.

    Only fields actually present in the domain dataclass are supplied.
    """

    values: dict[str, Any] = {}

    candidate_fields = (
        "price",
        "bid",
        "ask",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "turnover",
        "open_interest",
        "observation_kind",
        "fields_present",
        "observed_at",
        "transactions",
        "window_start",
        "session_end_date",
    )

    for field_name in candidate_fields:
        if not _field_exists(
            domain_type,
            field_name,
        ):
            continue

        value = getattr(
            model,
            field_name,
            None,
        )

        if field_name == "observation_kind":
            value = str(value)

        values[field_name] = value

    return domain_type(**values)


def _model_quality_to_domain(
    model: MarketDataQualityModel,
    domain_type: type[Any],
) -> Any:
    """
    Convert Pydantic quality into the existing MarketDataQuality domain
    structure.

    Pydantic-only fields such as status/usable/reasons are not injected into
    a domain dataclass that does not define them.
    """

    values: dict[str, Any] = {}

    candidate_fields = (
        "source",
        "source_timestamp",
        "received_timestamp",
        "sequence",
        "latency_ms",
        "is_complete",
        "is_stale",
        "quality_flags",
    )

    for field_name in candidate_fields:
        if not _field_exists(
            domain_type,
            field_name,
        ):
            continue

        values[field_name] = getattr(
            model,
            field_name,
        )

    return domain_type(**values)


def _model_state_to_domain(
    model: MarketStateModel,
    domain_type: type[Any],
) -> Any:
    """
    Convert Pydantic state into the existing MarketState domain structure.
    """

    values: dict[str, Any] = {}

    if _field_exists(
        domain_type,
        "session",
    ):
        from schemas.market.market_snapshot import (
            MarketSessionState,
        )

        values["session"] = MarketSessionState(
            model.session.value
        )

    if _field_exists(
        domain_type,
        "halted",
    ):
        values["halted"] = model.halted

    if _field_exists(
        domain_type,
        "tradable",
    ):
        values["tradable"] = model.tradable

    if _field_exists(
        domain_type,
        "state_reason",
    ):
        values["state_reason"] = model.state_reason

    return domain_type(**values)


def _model_contract_to_domain(
    model: ContractIdentityModel,
    domain_type: type[Any],
) -> Any:
    """
    Convert contract metadata while only passing fields supported by the
    installed domain dataclass.
    """

    values: dict[str, Any] = {}

    candidate_fields = (
        "contract_id",
        "contract_type",
        "product_code",
        "expiry",
        "strike",
        "option_type",
        "first_trade_date",
        "last_trade_date",
        "settlement_date",
        "tick_size",
        "contract_size",
        "currency",
        "metadata",
    )

    for field_name in candidate_fields:
        if not _field_exists(
            domain_type,
            field_name,
        ):
            continue

        values[field_name] = getattr(
            model,
            field_name,
        )

    return domain_type(**values)


def _market_snapshot_to_domain(
    self: MarketSnapshotModel,
) -> Any:
    """
    Convert the Pydantic canonical transport model back into the existing
    domain MarketSnapshot dataclass.

    Compatibility is intentional:
    transport-only fields are ignored when the installed domain dataclass
    does not yet contain them.
    """

    from schemas.market.market_snapshot import (
        ContractIdentity,
        InstrumentIdentity,
        MarketDataQuality,
        MarketIdentity,
        MarketObservation,
        MarketSessionState,
        MarketSnapshot,
        MarketState,
        VenueIdentity,
    )

    market = MarketIdentity(
        market=self.market.market,
        segment=self.market.segment,
        country=self.market.country,
    )

    instrument_kwargs = {
        "symbol": self.instrument.symbol,
        "instrument_type": self.instrument.instrument_type.value,
    }

    if _field_exists(
        InstrumentIdentity,
        "instrument_id",
    ):
        instrument_kwargs["instrument_id"] = (
            self.instrument.instrument_id
        )

    if _field_exists(
        InstrumentIdentity,
        "asset_class",
    ):
        instrument_kwargs["asset_class"] = (
            self.instrument.asset_class
        )

    instrument = InstrumentIdentity(
        **instrument_kwargs
    )

    venue_kwargs = {
        "venue": self.venue.venue,
    }

    if _field_exists(
        VenueIdentity,
        "venue_id",
    ):
        venue_kwargs["venue_id"] = self.venue.venue_id

    venue = VenueIdentity(
        **venue_kwargs
    )

    observation = _model_observation_to_domain(
        self.observation,
        MarketObservation,
    )

    quality = _model_quality_to_domain(
        self.data_quality,
        MarketDataQuality,
    )

    state = _model_state_to_domain(
        self.state,
        MarketState,
    )

    contract = None

    if self.contract is not None:
        contract = _model_contract_to_domain(
            self.contract,
            ContractIdentity,
        )

    snapshot_kwargs = {
        "market": market,
        "instrument": instrument,
        "venue": venue,
        "observed_at": self.observed_at,
        "observation": observation,
        "data_quality": quality,
        "state": state,
    }

    if _field_exists(
        MarketSnapshot,
        "contract",
    ):
        snapshot_kwargs["contract"] = contract

    if _field_exists(
        MarketSnapshot,
        "snapshot_id",
    ):
        snapshot_kwargs["snapshot_id"] = (
            self.snapshot_id
        )

    if _field_exists(
        MarketSnapshot,
        "metadata",
    ):
        snapshot_kwargs["metadata"] = dict(
            self.metadata
        )

    return MarketSnapshot(
        **snapshot_kwargs
    )


MarketSnapshotModel.to_domain = _market_snapshot_to_domain


# ============================================================================
# FINAL SERIALIZATION API
# ============================================================================


def _market_snapshot_model_json(
    self: MarketSnapshotModel,
    *,
    indent: int | None = None,
) -> str:
    """
    Final JSON serialization helper.

    Enum values become strings.
    Decimal values become JSON numbers/strings according to Pydantic's
    JSON serializer.
    Datetimes become ISO-8601 strings.
    """

    if indent is None:
        return self.model_dump_json()

    return json.dumps(
        self.model_dump(mode="json"),
        indent=indent,
        ensure_ascii=False,
    )


def _market_snapshot_model_json_dict(
    self: MarketSnapshotModel,
) -> dict[str, Any]:
    """
    Final JSON-compatible dictionary.
    """

    return self.model_dump(
        mode="json"
    )


# Keep explicit helpers available even if the class body changes later.
MarketSnapshotModel.to_json = _market_snapshot_model_json
MarketSnapshotModel.to_dict = _market_snapshot_model_json_dict


# ============================================================================
# FINAL VALIDATION HELPERS
# ============================================================================


def validate_market_snapshot_payload(
    payload: Mapping[str, Any],
) -> MarketSnapshotModel:
    """
    Validate an incoming canonical MarketSnapshot payload.
    """

    return MarketSnapshotModel.model_validate(
        dict(payload)
    )


def market_snapshot_from_json(
    payload: str,
) -> MarketSnapshotModel:
    """
    Parse and validate JSON into MarketSnapshotModel.
    """

    return MarketSnapshotModel.model_validate_json(
        payload
    )


def market_snapshot_to_json(
    snapshot: MarketSnapshotModel,
    *,
    indent: int | None = None,
) -> str:
    """
    Serialize MarketSnapshotModel into JSON.
    """

    return snapshot.to_json(
        indent=indent
    )


def market_snapshot_to_dict(
    snapshot: MarketSnapshotModel,
) -> dict[str, Any]:
    """
    Serialize MarketSnapshotModel into a JSON-compatible dictionary.
    """

    return snapshot.to_dict()
