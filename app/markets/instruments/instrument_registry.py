"""
ROBOMLM PLUS
Instrument Registry

Central in-memory registry for canonical instrument identities.

This registry provides deterministic registration and lookup only.
It does not perform network, broker, exchange, market-data, or execution
operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from threading import RLock
from typing import Iterable, Optional

from .instrument_identity import InstrumentIdentity


class InstrumentRegistryError(Exception):
    """Base exception for instrument registry failures."""


class InstrumentNotFoundError(InstrumentRegistryError):
    """Raised when an instrument cannot be found."""


class DuplicateInstrumentError(InstrumentRegistryError):
    """Raised when an instrument already exists."""


@dataclass(frozen=True)
class InstrumentRegistryStats:
    """Registry statistics."""

    total: int
    derivatives: int
    options: int
    expired: int

    def to_dict(self) -> dict[str, int]:
        """Return statistics as a dictionary."""
        return {
            "total": self.total,
            "derivatives": self.derivatives,
            "options": self.options,
            "expired": self.expired,
        }


class InstrumentRegistry:
    """
    Thread-safe registry for InstrumentIdentity objects.
    """

    def __init__(self) -> None:
        self._items: dict[str, InstrumentIdentity] = {}
        self._lock = RLock()

    def register(
        self,
        instrument: InstrumentIdentity,
        *,
        replace: bool = False,
    ) -> InstrumentIdentity:
        """Register one instrument."""
        self._validate(instrument)

        key = instrument.identity_key

        with self._lock:
            if key in self._items and not replace:
                raise DuplicateInstrumentError(
                    f"Instrument already registered: {key}"
                )

            stored = instrument.copy()
            self._items[key] = stored

            return stored.copy()

    def register_many(
        self,
        instruments: Iterable[InstrumentIdentity],
        *,
        replace: bool = False,
    ) -> list[InstrumentIdentity]:
        """Register multiple instruments."""
        items = list(instruments)

        for instrument in items:
            self._validate(instrument)

        results: list[InstrumentIdentity] = []

        with self._lock:
            for instrument in items:
                key = instrument.identity_key

                if key in self._items and not replace:
                    raise DuplicateInstrumentError(
                        f"Instrument already registered: {key}"
                    )

                stored = instrument.copy()
                self._items[key] = stored
                results.append(stored.copy())

        return results

    def get(
        self,
        identity_key: str,
    ) -> Optional[InstrumentIdentity]:
        """Return an instrument or None."""
        with self._lock:
            instrument = self._items.get(identity_key)

            if instrument is None:
                return None

            return instrument.copy()

    def require(
        self,
        identity_key: str,
    ) -> InstrumentIdentity:
        """Return an instrument or raise."""
        instrument = self.get(identity_key)

        if instrument is None:
            raise InstrumentNotFoundError(
                f"Instrument not found: {identity_key}"
            )

        return instrument

    def get_by_symbol(
        self,
        symbol: str,
    ) -> list[InstrumentIdentity]:
        """Return instruments matching symbol."""
        normalized = str(symbol).strip().upper()

        with self._lock:
            return [
                item.copy()
                for item in self._items.values()
                if item.symbol == normalized
            ]

    def get_by_exchange_symbol(
        self,
        exchange_symbol: str,
    ) -> list[InstrumentIdentity]:
        """Return instruments matching exchange symbol."""
        normalized = (
            str(exchange_symbol)
            .strip()
            .upper()
        )

        with self._lock:
            return [
                item.copy()
                for item in self._items.values()
                if item.exchange_symbol == normalized
            ]

    def get_by_isin(
        self,
        isin: str,
    ) -> Optional[InstrumentIdentity]:
        """Return an instrument by ISIN."""
        normalized = str(isin).strip().upper()

        with self._lock:
            for item in self._items.values():
                if item.isin == normalized:
                    return item.copy()

        return None

    def find(
        self,
        *,
        market: Optional[str] = None,
        instrument: Optional[str] = None,
        venue: Optional[str] = None,
        instrument_type: Optional[str] = None,
        underlying: Optional[str] = None,
        expiry: Optional[date] = None,
        option_type: Optional[str] = None,
        currency: Optional[str] = None,
    ) -> list[InstrumentIdentity]:
        """Find instruments using identity attributes."""
        market = _normalize_optional(market)
        instrument = _normalize_optional(instrument)
        venue = _normalize_optional(venue)
        instrument_type = _normalize_optional(
            instrument_type
        )
        underlying = _normalize_optional(underlying)
        option_type = _normalize_optional(option_type)
        currency = _normalize_optional(currency)

        with self._lock:
            results: list[InstrumentIdentity] = []

            for item in self._items.values():
                if (
                    market is not None
                    and item.market != market
                ):
                    continue

                if (
                    instrument is not None
                    and item.instrument != instrument
                ):
                    continue

                if (
                    venue is not None
                    and item.venue != venue
                ):
                    continue

                if (
                    instrument_type is not None
                    and item.instrument_type
                    != instrument_type
                ):
                    continue

                if (
                    underlying is not None
                    and item.underlying != underlying
                ):
                    continue

                if (
                    expiry is not None
                    and item.expiry != expiry
                ):
                    continue

                if (
                    option_type is not None
                    and item.option_type != option_type
                ):
                    continue

                if (
                    currency is not None
                    and item.currency != currency
                ):
                    continue

                results.append(item.copy())

            return results

    def list_by_market(
        self,
        market: str,
    ) -> list[InstrumentIdentity]:
        """List instruments for a market."""
        return self.find(market=market)

    def list_by_instrument(
        self,
        instrument: str,
    ) -> list[InstrumentIdentity]:
        """List instruments by instrument name."""
        return self.find(instrument=instrument)

    def list_by_venue(
        self,
        venue: str,
    ) -> list[InstrumentIdentity]:
        """List instruments for a venue."""
        return self.find(venue=venue)

    def list_derivatives(self) -> list[InstrumentIdentity]:
        """Return derivative instruments."""
        with self._lock:
            return [
                item.copy()
                for item in self._items.values()
                if item.is_derivative
            ]

    def list_options(self) -> list[InstrumentIdentity]:
        """Return option instruments."""
        with self._lock:
            return [
                item.copy()
                for item in self._items.values()
                if item.is_option
            ]

    def list_expired(self) -> list[InstrumentIdentity]:
        """Return expired instruments."""
        with self._lock:
            return [
                item.copy()
                for item in self._items.values()
                if item.is_expired
            ]

    def exists(
        self,
        identity_key: str,
    ) -> bool:
        """Return whether an identity key exists."""
        with self._lock:
            return identity_key in self._items

    def contains(
        self,
        instrument: InstrumentIdentity,
    ) -> bool:
        """Return whether an instrument is registered."""
        self._validate(instrument)

        return self.exists(instrument.identity_key)

    def remove(
        self,
        identity_key: str,
    ) -> bool:
        """Remove an instrument."""
        with self._lock:
            if identity_key not in self._items:
                return False

            del self._items[identity_key]
            return True

    def clear(self) -> int:
        """Remove all instruments and return removed count."""
        with self._lock:
            count = len(self._items)
            self._items.clear()
            return count

    def count(self) -> int:
        """Return total number of registered instruments."""
        with self._lock:
            return len(self._items)

    def keys(self) -> list[str]:
        """Return all identity keys."""
        with self._lock:
            return list(self._items.keys())

    def list_all(self) -> list[InstrumentIdentity]:
        """Return all registered instruments."""
        with self._lock:
            return [
                item.copy()
                for item in self._items.values()
            ]

    def stats(self) -> InstrumentRegistryStats:
        """Return registry statistics."""
        with self._lock:
            values = list(self._items.values())

            return InstrumentRegistryStats(
                total=len(values),
                derivatives=sum(
                    1 for item in values
                    if item.is_derivative
                ),
                options=sum(
                    1 for item in values
                    if item.is_option
                ),
                expired=sum(
                    1 for item in values
                    if item.is_expired
                ),
            )

    def snapshot(self) -> dict[str, dict]:
        """Return a serialized registry snapshot."""
        with self._lock:
            return {
                key: item.to_dict()
                for key, item in self._items.items()
            }

    def summary(self) -> dict[str, object]:
        """Return a registry summary."""
        stats = self.stats()

        return {
            "registry": self.__class__.__name__,
            **stats.to_dict(),
        }

    def _validate(
        self,
        instrument: InstrumentIdentity,
    ) -> None:
        """Validate registry input."""
        if not isinstance(
            instrument,
            InstrumentIdentity,
        ):
            raise InstrumentRegistryError(
                "instrument must be an InstrumentIdentity"
            )


instrument_registry = InstrumentRegistry()


def register_instrument(
    instrument: InstrumentIdentity,
    *,
    replace: bool = False,
) -> InstrumentIdentity:
    """Register an instrument in the global registry."""
    return instrument_registry.register(
        instrument,
        replace=replace,
    )


def get_instrument(
    identity_key: str,
) -> Optional[InstrumentIdentity]:
    """Get an instrument from the global registry."""
    return instrument_registry.get(identity_key)


def require_instrument(
    identity_key: str,
) -> InstrumentIdentity:
    """Require an instrument from the global registry."""
    return instrument_registry.require(identity_key)


def find_instruments(
    **filters: object,
) -> list[InstrumentIdentity]:
    """Find instruments in the global registry."""
    return instrument_registry.find(**filters)


def _normalize_optional(
    value: Optional[str],
) -> Optional[str]:
    """Normalize an optional text filter."""
    if value is None:
        return None

    text = str(value).strip()

    return text.upper() if text else None


__all__ = [
    "InstrumentRegistryError",
    "InstrumentNotFoundError",
    "DuplicateInstrumentError",
    "InstrumentRegistryStats",
    "InstrumentRegistry",
    "instrument_registry",
    "register_instrument",
    "get_instrument",
    "require_instrument",
    "find_instruments",
]