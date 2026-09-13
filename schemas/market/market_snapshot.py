from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, Mapping, Optional


class ObservationKind(str, Enum):
    """
    Identifies whether a value is directly observed from a source
    or derived by a downstream calculation.

    Market schema MUST preserve this distinction.
    """

    OBSERVED = "observed"
    DERIVED = "derived"


class MarketSessionState(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    PRE_OPEN = "pre_open"
    POST_CLOSE = "post_close"
    HALTED = "halted"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class MarketIdentity:
    """
    Exact market identity.

    Example:
        market="NSE"
        segment="EQUITY"
        country="IN"
    """

    market: str
    segment: str
    country: Optional[str] = None

    def __post_init__(self) -> None:
        market = self.market.strip()
        segment = self.segment.strip()

        if not market:
            raise ValueError("market must not be empty")

        if not segment:
            raise ValueError("segment must not be empty")

        object.__setattr__(self, "market", market)
        object.__setattr__(self, "segment", segment)

        if self.country is not None:
            country = self.country.strip()
            if not country:
                raise ValueError("country must be non-empty when supplied")
            object.__setattr__(self, "country", country)


@dataclass(frozen=True, slots=True)
class InstrumentIdentity:
    """
    Exact instrument identity.

    The symbol alone is NOT sufficient for universal identity.
    """

    symbol: str
    instrument_type: str
    instrument_id: Optional[str] = None

    def __post_init__(self) -> None:
        symbol = self.symbol.strip()
        instrument_type = self.instrument_type.strip()

        if not symbol:
            raise ValueError("symbol must not be empty")

        if not instrument_type:
            raise ValueError("instrument_type must not be empty")

        object.__setattr__(self, "symbol", symbol)
        object.__setattr__(self, "instrument_type", instrument_type)

        if self.instrument_id is not None:
            instrument_id = self.instrument_id.strip()
            if not instrument_id:
                raise ValueError(
                    "instrument_id must be non-empty when supplied"
                )
            object.__setattr__(self, "instrument_id", instrument_id)


@dataclass(frozen=True, slots=True)
class ContractIdentity:
    """
    Contract-level identity.

    Required especially for derivatives where instrument identity
    without expiry/contract information is insufficient.
    """

    contract_id: Optional[str] = None
    contract_type: Optional[str] = None
    expiry: Optional[datetime] = None
    strike: Optional[Decimal] = None
    option_type: Optional[str] = None

    def __post_init__(self) -> None:
        if self.contract_id is not None:
            value = self.contract_id.strip()
            if not value:
                raise ValueError(
                    "contract_id must be non-empty when supplied"
                )
            object.__setattr__(self, "contract_id", value)

        if self.contract_type is not None:
            value = self.contract_type.strip()
            if not value:
                raise ValueError(
                    "contract_type must be non-empty when supplied"
                )
            object.__setattr__(self, "contract_type", value)

        if self.expiry is not None:
            if self.expiry.tzinfo is None:
                raise ValueError("expiry must be timezone-aware")

            object.__setattr__(
                self,
                "expiry",
                self.expiry.astimezone(timezone.utc),
            )

        if self.strike is not None:
            if self.strike < 0:
                raise ValueError("strike must not be negative")

        if self.option_type is not None:
            value = self.option_type.strip().upper()
            if value not in {"CE", "PE", "CALL", "PUT"}:
                raise ValueError(
                    "option_type must be CE, PE, CALL, or PUT"
                )
            object.__setattr__(self, "option_type", value)


@dataclass(frozen=True, slots=True)
class VenueIdentity:
    """
    Execution/data venue identity.

    Venue is intentionally separate from market and instrument.
    """

    venue: str
    venue_id: Optional[str] = None

    def __post_init__(self) -> None:
        venue = self.venue.strip()

        if not venue:
            raise ValueError("venue must not be empty")

        object.__setattr__(self, "venue", venue)

        if self.venue_id is not None:
            value = self.venue_id.strip()
            if not value:
                raise ValueError(
                    "venue_id must be non-empty when supplied"
                )
            object.__setattr__(self, "venue_id", value)


@dataclass(frozen=True, slots=True)
class MarketDataQuality:
    """
    Data-quality facts.

    These are facts about the data stream, NOT an intelligence score.
    """

    source: str
    source_timestamp: datetime
    received_timestamp: datetime

    sequence: Optional[int] = None
    latency_ms: Optional[float] = None
    is_complete: bool = True
    is_stale: bool = False
    quality_flags: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        source = self.source.strip()

        if not source:
            raise ValueError("source must not be empty")

        object.__setattr__(self, "source", source)

        if self.source_timestamp.tzinfo is None:
            raise ValueError(
                "source_timestamp must be timezone-aware"
            )

        if self.received_timestamp.tzinfo is None:
            raise ValueError(
                "received_timestamp must be timezone-aware"
            )

        source_ts = self.source_timestamp.astimezone(timezone.utc)
        received_ts = self.received_timestamp.astimezone(timezone.utc)

        if received_ts < source_ts:
            raise ValueError(
                "received_timestamp cannot precede source_timestamp"
            )

        object.__setattr__(
            self,
            "source_timestamp",
            source_ts,
        )

        object.__setattr__(
            self,
            "received_timestamp",
            received_ts,
        )

        if self.sequence is not None and self.sequence < 0:
            raise ValueError("sequence must not be negative")

        if self.latency_ms is not None:
            if self.latency_ms < 0:
                raise ValueError("latency_ms must not be negative")

        flags = tuple(
            str(flag).strip()
            for flag in self.quality_flags
            if str(flag).strip()
        )

        object.__setattr__(self, "quality_flags", flags)


@dataclass(frozen=True, slots=True)
class MarketObservation:
    """
    Direct market observation.

    No intelligence score belongs here.
    No direction prediction belongs here.
    No CAS decision belongs here.
    """

    price: Optional[Decimal] = None
    bid: Optional[Decimal] = None
    ask: Optional[Decimal] = None

    open: Optional[Decimal] = None
    high: Optional[Decimal] = None
    low: Optional[Decimal] = None
    close: Optional[Decimal] = None

    volume: Optional[Decimal] = None
    turnover: Optional[Decimal] = None
    open_interest: Optional[Decimal] = None

    observation_kind: ObservationKind = ObservationKind.OBSERVED

    fields_present: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.observation_kind is not ObservationKind.OBSERVED:
            raise ValueError(
                "MarketObservation must be OBSERVED"
            )

        numeric_fields = {
            "price": self.price,
            "bid": self.bid,
            "ask": self.ask,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "turnover": self.turnover,
            "open_interest": self.open_interest,
        }

        for name, value in numeric_fields.items():
            if value is not None and value < 0:
                raise ValueError(
                    f"{name} must not be negative"
                )

        if self.bid is not None and self.ask is not None:
            if self.bid > self.ask:
                raise ValueError(
                    "bid cannot be greater than ask"
                )

        if (
            self.low is not None
            and self.high is not None
            and self.low > self.high
        ):
            raise ValueError(
                "low cannot be greater than high"
            )

        if (
            self.open is not None
            and self.high is not None
            and self.open > self.high
        ):
            raise ValueError(
                "open cannot exceed high"
            )

        if (
            self.open is not None
            and self.low is not None
            and self.open < self.low
        ):
            raise ValueError(
                "open cannot be below low"
            )

        if (
            self.close is not None
            and self.high is not None
            and self.close > self.high
        ):
            raise ValueError(
                "close cannot exceed high"
            )

        if (
            self.close is not None
            and self.low is not None
            and self.close < self.low
        ):
            raise ValueError(
                "close cannot be below low"
            )

        present = tuple(
            field_name
            for field_name, value in numeric_fields.items()
            if value is not None
        )

        supplied = tuple(
            str(value).strip()
            for value in self.fields_present
            if str(value).strip()
        )

        # Preserve explicit source declaration but ensure actual
        # present fields are represented as well.
        merged = tuple(dict.fromkeys((*supplied, *present)))

        object.__setattr__(
            self,
            "fields_present",
            merged,
        )


@dataclass(frozen=True, slots=True)
class MarketState:
    """
    Explicit market state.

    State is descriptive, not predictive.
    """

    session: MarketSessionState = MarketSessionState.UNKNOWN
    halted: bool = False
    tradable: bool = True

    state_reason: Optional[str] = None

    def __post_init__(self) -> None:
        if self.halted and self.tradable:
            raise ValueError(
                "halted market cannot be marked tradable"
            )

        if self.state_reason is not None:
            reason = self.state_reason.strip()
            if not reason:
                raise ValueError(
                    "state_reason must be non-empty when supplied"
                )
            object.__setattr__(
                self,
                "state_reason",
                reason,
            )


@dataclass(frozen=True, slots=True)
class MarketSnapshot:
    """
    Canonical immutable market snapshot.

    Canonical hierarchy:

        Market
          -> Instrument
          -> Contract
          -> Venue
          -> Observation
          -> Timestamp
          -> Data Quality
          -> State

    This schema is deliberately intelligence-neutral.
    """

    market: MarketIdentity
    instrument: InstrumentIdentity
    venue: VenueIdentity

    observed_at: datetime

    observation: MarketObservation
    data_quality: MarketDataQuality
    state: MarketState

    contract: Optional[ContractIdentity] = None

    snapshot_id: Optional[str] = None

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if self.observed_at.tzinfo is None:
            raise ValueError(
                "observed_at must be timezone-aware"
            )

        observed_at = self.observed_at.astimezone(timezone.utc)

        object.__setattr__(
            self,
            "observed_at",
            observed_at,
        )

        if self.snapshot_id is not None:
            snapshot_id = self.snapshot_id.strip()

            if not snapshot_id:
                raise ValueError(
                    "snapshot_id must be non-empty when supplied"
                )

            object.__setattr__(
                self,
                "snapshot_id",
                snapshot_id,
            )

        if self.observed_at < self.data_quality.source_timestamp:
            raise ValueError(
                "observed_at cannot precede source_timestamp"
            )

        if self.observed_at < self.data_quality.received_timestamp:
            raise ValueError(
                "observed_at cannot precede received_timestamp"
            )

        if (
            self.contract is not None
            and self.contract.contract_type is None
            and (
                self.contract.expiry is not None
                or self.contract.strike is not None
                or self.contract.option_type is not None
            )
        ):
            raise ValueError(
                "derivative contract attributes require contract_type"
            )

        # Copy metadata so external mutation cannot modify the
        # logical snapshot after construction.
        object.__setattr__(
            self,
            "metadata",
            dict(self.metadata),
        )

    @property
    def identity_key(self) -> tuple[str, ...]:
        """
        Stable logical identity of the market object.

        Snapshot timestamp is intentionally excluded because this
        represents identity, not observation event identity.
        """

        return (
            self.market.market,
            self.market.segment,
            self.instrument.symbol,
            self.instrument.instrument_type,
            self.instrument.instrument_id or "",
            self.contract.contract_id
            if self.contract is not None
            else "",
            self.venue.venue,
            self.venue.venue_id or "",
        )

    @property
    def age_seconds(self) -> float:
        """
        Age of the observation relative to data receipt.

        This is a measured temporal property, not a quality score.
        """

        delta = (
            self.data_quality.received_timestamp
            - self.data_quality.source_timestamp
        )

        return max(delta.total_seconds(), 0.0)

    def observed_value(
        self,
        field_name: str,
    ) -> Optional[Decimal]:
        """
        Retrieve an observed numerical field.

        Unknown fields raise AttributeError rather than silently
        returning zero. Missing market data must remain missing.
        """

        if not hasattr(self.observation, field_name):
            raise AttributeError(
                f"Unknown market observation field: {field_name}"
            )

        value = getattr(self.observation, field_name)

        if value is None:
            return None

        if not isinstance(value, Decimal):
            raise TypeError(
                f"Observation field {field_name!r} is not Decimal"
            )

        return value

    def to_dict(self) -> dict[str, Any]:
        """
        Explicit serialization.

        Decimal values are serialized as strings to prevent
        precision loss.
        """

        def decimal_value(
            value: Optional[Decimal],
        ) -> Optional[str]:
            return None if value is None else str(value)

        contract = self.contract

        return {
            "snapshot_id": self.snapshot_id,
            "observed_at": self.observed_at.isoformat(),

            "market": {
                "market": self.market.market,
                "segment": self.market.segment,
                "country": self.market.country,
            },

            "instrument": {
                "symbol": self.instrument.symbol,
                "instrument_type": self.instrument.instrument_type,
                "instrument_id": self.instrument.instrument_id,
            },

            "contract": (
                None
                if contract is None
                else {
                    "contract_id": contract.contract_id,
                    "contract_type": contract.contract_type,
                    "expiry": (
                        contract.expiry.isoformat()
                        if contract.expiry is not None
                        else None
                    ),
                    "strike": decimal_value(contract.strike),
                    "option_type": contract.option_type,
                }
            ),

            "venue": {
                "venue": self.venue.venue,
                "venue_id": self.venue.venue_id,
            },

            "observation": {
                "price": decimal_value(
                    self.observation.price
                ),
                "bid": decimal_value(
                    self.observation.bid
                ),
                "ask": decimal_value(
                    self.observation.ask
                ),
                "open": decimal_value(
                    self.observation.open
                ),
                "high": decimal_value(
                    self.observation.high
                ),
                "low": decimal_value(
                    self.observation.low
                ),
                "close": decimal_value(
                    self.observation.close
                ),
                "volume": decimal_value(
                    self.observation.volume
                ),
                "turnover": decimal_value(
                    self.observation.turnover
                ),
                "open_interest": decimal_value(
                    self.observation.open_interest
                ),
                "observation_kind":
                    self.observation.observation_kind.value,
                "fields_present":
                    list(self.observation.fields_present),
            },

            "data_quality": {
                "source": self.data_quality.source,
                "source_timestamp":
                    self.data_quality.source_timestamp.isoformat(),
                "received_timestamp":
                    self.data_quality.received_timestamp.isoformat(),
                "sequence": self.data_quality.sequence,
                "latency_ms": self.data_quality.latency_ms,
                "is_complete": self.data_quality.is_complete,
                "is_stale": self.data_quality.is_stale,
                "quality_flags":
                    list(self.data_quality.quality_flags),
            },

            "state": {
                "session":
                    self.state.session.value,
                "halted": self.state.halted,
                "tradable": self.state.tradable,
                "state_reason": self.state.state_reason,
            },

            "metadata": dict(self.metadata),
        }


def utc_now() -> datetime:
    """
    Return a timezone-aware UTC timestamp.
    """

    return datetime.now(timezone.utc)


__all__ = [
    "ObservationKind",
    "MarketSessionState",
    "MarketIdentity",
    "InstrumentIdentity",
    "ContractIdentity",
    "VenueIdentity",
    "MarketDataQuality",
    "MarketObservation",
    "MarketState",
    "MarketSnapshot",
    "utc_now",
]