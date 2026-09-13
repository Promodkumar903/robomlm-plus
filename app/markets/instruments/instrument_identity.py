"""
ROBOMLM PLUS
Instrument Identity

Canonical identity model for market instruments.

This module defines what uniquely identifies an instrument.
It does not perform market-data, broker, exchange, or execution calls.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from math import isfinite
from typing import Any, Mapping, Optional


class InstrumentIdentityError(Exception):
    """Base exception for instrument identity failures."""


class InstrumentIdentityValidationError(
    InstrumentIdentityError
):
    """Raised when instrument identity validation fails."""


INSTRUMENT_TYPES = frozenset(
    {
        "EQUITY",
        "INDEX",
        "ETF",
        "FUTURE",
        "OPTION",
        "BOND",
        "COMMODITY",
        "FX",
        "CRYPTO",
        "CFD",
        "FUND",
        "OTHER",
    }
)

OPTION_TYPES = frozenset(
    {
        "CE",
        "PE",
        "CALL",
        "PUT",
    }
)


def _normalize_required(
    value: Any,
    field_name: str,
) -> str:
    """Normalize and validate a required text field."""
    if value is None:
        raise InstrumentIdentityValidationError(
            f"{field_name} is required"
        )

    text = str(value).strip()

    if not text:
        raise InstrumentIdentityValidationError(
            f"{field_name} cannot be empty"
        )

    return text.upper()


def _normalize_optional(
    value: Any,
) -> Optional[str]:
    """Normalize an optional text field."""
    if value is None:
        return None

    text = str(value).strip()

    return text.upper() if text else None


def _validate_number(
    value: Optional[float],
    field_name: str,
    *,
    minimum: Optional[float] = None,
) -> Optional[float]:
    """Validate an optional numeric field."""
    if value is None:
        return None

    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise InstrumentIdentityValidationError(
            f"{field_name} must be numeric"
        ) from exc

    if not isfinite(number):
        raise InstrumentIdentityValidationError(
            f"{field_name} must be finite"
        )

    if minimum is not None and number < minimum:
        raise InstrumentIdentityValidationError(
            f"{field_name} must be >= {minimum}"
        )

    return number


def _normalize_expiry(
    value: Optional[date],
) -> Optional[date]:
    """Normalize an expiry value."""
    if value is None:
        return None

    if isinstance(value, date):
        return value

    if isinstance(value, str):
        text = value.strip()

        try:
            return date.fromisoformat(text)
        except ValueError as exc:
            raise InstrumentIdentityValidationError(
                "expiry must use YYYY-MM-DD format"
            ) from exc

    raise InstrumentIdentityValidationError(
        "expiry must be a date or YYYY-MM-DD string"
    )


@dataclass
class InstrumentIdentity:
    """
    Canonical identity of a tradable or observable instrument.

    Identity is deliberately separate from live market data.
    """

    market: str
    instrument: str
    venue: str

    symbol: Optional[str] = None
    instrument_type: Optional[str] = None
    exchange_symbol: Optional[str] = None
    isin: Optional[str] = None
    underlying: Optional[str] = None

    expiry: Optional[date] = None
    strike: Optional[float] = None
    option_type: Optional[str] = None

    currency: Optional[str] = None
    multiplier: Optional[float] = None

    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.market = _normalize_required(
            self.market,
            "market",
        )

        self.instrument = _normalize_required(
            self.instrument,
            "instrument",
        )

        self.venue = _normalize_required(
            self.venue,
            "venue",
        )

        self.symbol = _normalize_optional(self.symbol)
        self.instrument_type = _normalize_optional(
            self.instrument_type
        )
        self.exchange_symbol = _normalize_optional(
            self.exchange_symbol
        )
        self.isin = _normalize_optional(self.isin)
        self.underlying = _normalize_optional(
            self.underlying
        )

        self.expiry = _normalize_expiry(self.expiry)

        self.strike = _validate_number(
            self.strike,
            "strike",
            minimum=0.0,
        )

        self.option_type = _normalize_optional(
            self.option_type
        )

        self.currency = _normalize_optional(
            self.currency
        )

        self.multiplier = _validate_number(
            self.multiplier,
            "multiplier",
            minimum=0.0,
        )

        if not isinstance(self.metadata, dict):
            self.metadata = dict(self.metadata or {})

        self._validate_relationships()

    def _validate_relationships(self) -> None:
        """Validate relationships between identity fields."""
        if self.instrument_type is not None:
            if self.instrument_type not in INSTRUMENT_TYPES:
                raise InstrumentIdentityValidationError(
                    "Unsupported instrument_type: "
                    f"{self.instrument_type}"
                )

        if self.option_type is not None:
            if self.option_type not in OPTION_TYPES:
                raise InstrumentIdentityValidationError(
                    "Unsupported option_type: "
                    f"{self.option_type}"
                )

        if self.option_type is not None:
            if self.strike is None:
                raise InstrumentIdentityValidationError(
                    "Option instrument requires strike"
                )

            if self.expiry is None:
                raise InstrumentIdentityValidationError(
                    "Option instrument requires expiry"
                )

        if self.instrument_type == "OPTION":
            if self.strike is None:
                raise InstrumentIdentityValidationError(
                    "OPTION instrument requires strike"
                )

            if self.expiry is None:
                raise InstrumentIdentityValidationError(
                    "OPTION instrument requires expiry"
                )

    @property
    def identity_key(self) -> str:
        """
        Return the canonical identity key.

        The key intentionally excludes mutable metadata.
        """
        parts = [
            self.market,
            self.instrument,
            self.venue,
            self.symbol or "",
            self.instrument_type or "",
            self.exchange_symbol or "",
            self.isin or "",
            self.underlying or "",
            self.expiry.isoformat()
            if self.expiry is not None
            else "",
            _number_key(self.strike),
            self.option_type or "",
            self.currency or "",
            _number_key(self.multiplier),
        ]

        return "|".join(parts)

    @property
    def is_derivative(self) -> bool:
        """Return whether the instrument is derivative-like."""
        return self.instrument_type in {
            "FUTURE",
            "OPTION",
            "CFD",
        } or self.expiry is not None

    @property
    def is_option(self) -> bool:
        """Return whether the instrument is an option."""
        return (
            self.instrument_type == "OPTION"
            or self.option_type is not None
        )

    @property
    def is_expired(self) -> bool:
        """Return whether the instrument expiry has passed."""
        if self.expiry is None:
            return False

        return self.expiry < date.today()

    def same_instrument(
        self,
        other: "InstrumentIdentity",
    ) -> bool:
        """Compare two instrument identities."""
        if not isinstance(other, InstrumentIdentity):
            return False

        return self.identity_key == other.identity_key

    def with_metadata(
        self,
        **metadata: Any,
    ) -> "InstrumentIdentity":
        """Return a copy with merged metadata."""
        merged = dict(self.metadata)
        merged.update(metadata)

        return InstrumentIdentity(
            market=self.market,
            instrument=self.instrument,
            venue=self.venue,
            symbol=self.symbol,
            instrument_type=self.instrument_type,
            exchange_symbol=self.exchange_symbol,
            isin=self.isin,
            underlying=self.underlying,
            expiry=self.expiry,
            strike=self.strike,
            option_type=self.option_type,
            currency=self.currency,
            multiplier=self.multiplier,
            metadata=merged,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the identity to a dictionary."""
        return {
            "market": self.market,
            "instrument": self.instrument,
            "venue": self.venue,
            "symbol": self.symbol,
            "instrument_type": self.instrument_type,
            "exchange_symbol": self.exchange_symbol,
            "isin": self.isin,
            "underlying": self.underlying,
            "expiry": (
                self.expiry.isoformat()
                if self.expiry is not None
                else None
            ),
            "strike": self.strike,
            "option_type": self.option_type,
            "currency": self.currency,
            "multiplier": self.multiplier,
            "identity_key": self.identity_key,
            "is_derivative": self.is_derivative,
            "is_option": self.is_option,
            "is_expired": self.is_expired,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_mapping(
        cls,
        data: Mapping[str, Any],
    ) -> "InstrumentIdentity":
        """Create an identity from a mapping."""
        if not isinstance(data, Mapping):
            raise InstrumentIdentityValidationError(
                "data must be a mapping"
            )

        values = dict(data)

        values.pop("identity_key", None)
        values.pop("is_derivative", None)
        values.pop("is_option", None)
        values.pop("is_expired", None)

        return cls(**values)

    def copy(self) -> "InstrumentIdentity":
        """Return an independent copy."""
        return InstrumentIdentity(
            market=self.market,
            instrument=self.instrument,
            venue=self.venue,
            symbol=self.symbol,
            instrument_type=self.instrument_type,
            exchange_symbol=self.exchange_symbol,
            isin=self.isin,
            underlying=self.underlying,
            expiry=self.expiry,
            strike=self.strike,
            option_type=self.option_type,
            currency=self.currency,
            multiplier=self.multiplier,
            metadata=dict(self.metadata),
        )


def _number_key(
    value: Optional[float],
) -> str:
    """Create a deterministic numeric identity component."""
    if value is None:
        return ""

    return format(float(value), ".15g")


def create_instrument_identity(
    *,
    market: str,
    instrument: str,
    venue: str,
    symbol: Optional[str] = None,
    instrument_type: Optional[str] = None,
    exchange_symbol: Optional[str] = None,
    isin: Optional[str] = None,
    underlying: Optional[str] = None,
    expiry: Optional[date] = None,
    strike: Optional[float] = None,
    option_type: Optional[str] = None,
    currency: Optional[str] = None,
    multiplier: Optional[float] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> InstrumentIdentity:
    """Factory for InstrumentIdentity."""
    return InstrumentIdentity(
        market=market,
        instrument=instrument,
        venue=venue,
        symbol=symbol,
        instrument_type=instrument_type,
        exchange_symbol=exchange_symbol,
        isin=isin,
        underlying=underlying,
        expiry=expiry,
        strike=strike,
        option_type=option_type,
        currency=currency,
        multiplier=multiplier,
        metadata=dict(metadata or {}),
    )


def instrument_identity_key(
    instrument: InstrumentIdentity,
) -> str:
    """Return the canonical identity key."""
    if not isinstance(
        instrument,
        InstrumentIdentity,
    ):
        raise InstrumentIdentityValidationError(
            "instrument must be an InstrumentIdentity"
        )

    return instrument.identity_key


__all__ = [
    "INSTRUMENT_TYPES",
    "OPTION_TYPES",
    "InstrumentIdentityError",
    "InstrumentIdentityValidationError",
    "InstrumentIdentity",
    "create_instrument_identity",
    "instrument_identity_key",
]