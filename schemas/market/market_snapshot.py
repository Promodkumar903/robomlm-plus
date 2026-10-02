from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, Mapping


MARKET_SNAPSHOT_SCHEMA_VERSION = "2.0.0"


class ObservationKind(str, Enum):
    OBSERVED = "observed"
    DERIVED = "derived"


class MarketSessionState(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    PRE_OPEN = "pre_open"
    POST_CLOSE = "post_close"
    HALTED = "halted"
    UNKNOWN = "unknown"


class MarketDataQualityStatus(str, Enum):
    VALID = "VALID"
    DEGRADED = "DEGRADED"
    STALE = "STALE"
    INVALID = "INVALID"


@dataclass(frozen=True, slots=True)
class MarketIdentity:
    market: str
    segment: str
    country: str | None = None


@dataclass(frozen=True, slots=True)
class InstrumentIdentity:
    symbol: str
    instrument_type: str
    instrument_id: str
    asset_class: str | None = None


@dataclass(frozen=True, slots=True)
class VenueIdentity:
    venue: str
    venue_id: str | None = None


@dataclass(frozen=True, slots=True)
class ContractIdentity:
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

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True, slots=True)
class MarketObservation:
    """
    Provider-observed market values only.

    No ROBOMLM-derived calculations belong here.
    """

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

    bid_size: Decimal | None = None
    ask_size: Decimal | None = None

    trade_size: Decimal | None = None
    trade_conditions: tuple[str, ...] | None = None
    trade_exchange: str | None = None

    open_interest: Decimal | None = None

    window_start: datetime | None = None
    session_end_date: date | None = None

    observation_kind: ObservationKind = (
        ObservationKind.OBSERVED
    )

    fields_present: tuple[str, ...] = field(
        default_factory=tuple
    )


@dataclass(frozen=True, slots=True)
class MarketDataQuality:
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

    missing_fields: tuple[str, ...] = field(
        default_factory=tuple
    )

    invalid_fields: tuple[str, ...] = field(
        default_factory=tuple
    )

    quality_flags: tuple[str, ...] = field(
        default_factory=tuple
    )

    reasons: tuple[str, ...] = field(
        default_factory=tuple
    )

    provider_quality_flags: tuple[str, ...] = field(
        default_factory=tuple
    )


@dataclass(frozen=True, slots=True)
class MarketTiming:
    source_timestamp: datetime
    received_timestamp: datetime
    observed_at: datetime

    window_start: datetime | None = None
    session_end_date: date | None = None

    @property
    def latency_ms(self) -> float:
        delta = (
            self.received_timestamp
            - self.source_timestamp
        )
        return max(
            0.0,
            delta.total_seconds() * 1000.0,
        )


@dataclass(frozen=True, slots=True)
class MarketProvenance:
    provider: str
    endpoint: str | None = None

    provider_symbol: str | None = None
    raw_reference: str | None = None

    adapter_version: str | None = None

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True, slots=True)
class MarketState:
    session: MarketSessionState = (
        MarketSessionState.UNKNOWN
    )

    halted: bool = False
    tradable: bool = True

    state_reason: str | None = None


@dataclass(frozen=True, slots=True)
class MarketSnapshot:
    """
    Universal provider-neutral market snapshot.

    Supported examples:

        AAPL
        EURUSD
        ESH7
        CLX6
        GCF7
        BTCUSDT

    Raw provider observations are normalized into this
    structure. Intelligence and decision calculations
    happen outside this object.
    """

    schema_version: str = (
        MARKET_SNAPSHOT_SCHEMA_VERSION
    )

    snapshot_id: str | None = None

    market: MarketIdentity = field(
        default_factory=lambda: MarketIdentity(
            market="UNKNOWN",
            segment="UNKNOWN",
        )
    )

    instrument: InstrumentIdentity = field(
        default_factory=lambda: InstrumentIdentity(
            symbol="UNKNOWN",
            instrument_type="UNKNOWN",
            instrument_id="UNKNOWN",
        )
    )

    venue: VenueIdentity = field(
        default_factory=lambda: VenueIdentity(
            venue="UNKNOWN"
        )
    )

    contract: ContractIdentity | None = None

    observation: MarketObservation = field(
        default_factory=lambda: MarketObservation(
            observed_at=datetime.now(timezone.utc)
        )
    )

    timing: MarketTiming | None = None

    data_quality: MarketDataQuality = field(
        default_factory=lambda: MarketDataQuality(
            source="unknown",
            source_timestamp=datetime.now(timezone.utc),
            received_timestamp=datetime.now(timezone.utc),
        )
    )

    provenance: MarketProvenance | None = None

    state: MarketState = field(
        default_factory=MarketState
    )

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    @property
    def identity_key(self) -> tuple[str, ...]:
        return (
            self.market.market,
            self.market.segment,
            self.instrument.symbol,
            self.instrument.instrument_type,
            self.instrument.instrument_id,
            (
                self.contract.contract_id
                if self.contract
                else ""
            ),
            self.venue.venue,
            self.venue.venue_id or "",
        )