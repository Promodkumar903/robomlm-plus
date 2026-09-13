"""
ROBOMLM PLUS
Instrument Service

Application-level service for canonical instrument creation,
registration, lookup, filtering, validation, and lifecycle operations.

This service does not perform network, broker, exchange, market-data,
or execution operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Iterable, Mapping, Optional

from .instrument_identity import (
    InstrumentIdentity,
    InstrumentIdentityValidationError,
    create_instrument_identity,
)
from .instrument_registry import (
    InstrumentNotFoundError,
    InstrumentRegistry,
    instrument_registry,
)


class InstrumentServiceError(Exception):
    """Base exception for instrument-service failures."""


class InstrumentServiceValidationError(
    InstrumentServiceError
):
    """Raised when instrument-service input is invalid."""


@dataclass(frozen=True)
class InstrumentQuery:
    """Normalized instrument lookup criteria."""

    market: Optional[str] = None
    instrument: Optional[str] = None
    venue: Optional[str] = None
    instrument_type: Optional[str] = None
    underlying: Optional[str] = None
    expiry: Optional[date] = None
    option_type: Optional[str] = None
    currency: Optional[str] = None

    def normalized(self) -> "InstrumentQuery":
        """Return a normalized copy of the query."""
        return InstrumentQuery(
            market=_normalize_optional(self.market),
            instrument=_normalize_optional(
                self.instrument
            ),
            venue=_normalize_optional(self.venue),
            instrument_type=_normalize_optional(
                self.instrument_type
            ),
            underlying=_normalize_optional(
                self.underlying
            ),
            expiry=self.expiry,
            option_type=_normalize_optional(
                self.option_type
            ),
            currency=_normalize_optional(
                self.currency
            ),
        )


class InstrumentService:
    """
    Application service around InstrumentIdentity
    and InstrumentRegistry.
    """

    def __init__(
        self,
        registry: Optional[InstrumentRegistry] = None,
    ) -> None:
        self.registry = registry or instrument_registry

    def create(
        self,
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
        replace: bool = False,
    ) -> InstrumentIdentity:
        """Create and register an instrument identity."""
        try:
            identity = create_instrument_identity(
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
                metadata=metadata,
            )
        except InstrumentIdentityValidationError as exc:
            raise InstrumentServiceValidationError(
                str(exc)
            ) from exc

        return self.registry.register(
            identity,
            replace=replace,
        )

    def register(
        self,
        instrument: InstrumentIdentity,
        *,
        replace: bool = False,
    ) -> InstrumentIdentity:
        """Register an existing instrument identity."""
        self._validate_identity(instrument)

        return self.registry.register(
            instrument,
            replace=replace,
        )

    def register_many(
        self,
        instruments: Iterable[InstrumentIdentity],
        *,
        replace: bool = False,
    ) -> list[InstrumentIdentity]:
        """Register multiple instrument identities."""
        items = list(instruments)

        for instrument in items:
            self._validate_identity(instrument)

        return self.registry.register_many(
            items,
            replace=replace,
        )

    def get(
        self,
        identity_key: str,
    ) -> Optional[InstrumentIdentity]:
        """Get an instrument by canonical identity key."""
        return self.registry.get(identity_key)

    def require(
        self,
        identity_key: str,
    ) -> InstrumentIdentity:
        """Require an instrument by canonical identity key."""
        try:
            return self.registry.require(identity_key)
        except InstrumentNotFoundError as exc:
            raise InstrumentServiceError(
                str(exc)
            ) from exc

    def exists(
        self,
        identity_key: str,
    ) -> bool:
        """Return whether an instrument exists."""
        return self.registry.exists(identity_key)

    def find(
        self,
        query: Optional[InstrumentQuery] = None,
        **filters: Any,
    ) -> list[InstrumentIdentity]:
        """
        Find instruments using an InstrumentQuery or explicit filters.

        Explicit keyword filters take precedence over values supplied
        by the query object.
        """
        if query is not None and not isinstance(
            query,
            InstrumentQuery,
        ):
            raise InstrumentServiceValidationError(
                "query must be an InstrumentQuery"
            )

        normalized_query = (
            query.normalized()
            if query is not None
            else InstrumentQuery()
        )

        merged = {
            "market": normalized_query.market,
            "instrument": normalized_query.instrument,
            "venue": normalized_query.venue,
            "instrument_type": (
                normalized_query.instrument_type
            ),
            "underlying": normalized_query.underlying,
            "expiry": normalized_query.expiry,
            "option_type": normalized_query.option_type,
            "currency": normalized_query.currency,
        }

        for key, value in filters.items():
            if key not in merged:
                raise InstrumentServiceValidationError(
                    f"Unknown instrument filter: {key}"
                )

            merged[key] = value

        return self.registry.find(**merged)

    def find_by_symbol(
        self,
        symbol: str,
    ) -> list[InstrumentIdentity]:
        """Find instruments by symbol."""
        return self.registry.get_by_symbol(symbol)

    def find_by_exchange_symbol(
        self,
        exchange_symbol: str,
    ) -> list[InstrumentIdentity]:
        """Find instruments by exchange symbol."""
        return self.registry.get_by_exchange_symbol(
            exchange_symbol
        )

    def find_by_isin(
        self,
        isin: str,
    ) -> Optional[InstrumentIdentity]:
        """Find an instrument by ISIN."""
        return self.registry.get_by_isin(isin)

    def find_by_market(
        self,
        market: str,
    ) -> list[InstrumentIdentity]:
        """Find instruments by market."""
        return self.registry.list_by_market(market)

    def find_by_instrument(
        self,
        instrument: str,
    ) -> list[InstrumentIdentity]:
        """Find instruments by instrument name."""
        return self.registry.list_by_instrument(
            instrument
        )

    def find_by_venue(
        self,
        venue: str,
    ) -> list[InstrumentIdentity]:
        """Find instruments by venue."""
        return self.registry.list_by_venue(venue)

    def derivatives(self) -> list[InstrumentIdentity]:
        """Return all derivative instruments."""
        return self.registry.list_derivatives()

    def options(self) -> list[InstrumentIdentity]:
        """Return all option instruments."""
        return self.registry.list_options()

    def expired(self) -> list[InstrumentIdentity]:
        """Return all expired instruments."""
        return self.registry.list_expired()

    def update_metadata(
        self,
        identity_key: str,
        **metadata: Any,
    ) -> InstrumentIdentity:
        """
        Replace the registered instrument with a metadata-merged copy.

        Identity fields remain unchanged.
        """
        current = self.require(identity_key)

        updated = current.with_metadata(**metadata)

        return self.registry.register(
            updated,
            replace=True,
        )

    def validate_identity(
        self,
        instrument: InstrumentIdentity,
    ) -> dict[str, Any]:
        """
        Validate an instrument identity and return validation facts.

        This method does not alter the registry.
        """
        self._validate_identity(instrument)

        return {
            "valid": True,
            "identity_key": instrument.identity_key,
            "is_derivative": instrument.is_derivative,
            "is_option": instrument.is_option,
            "is_expired": instrument.is_expired,
            "registered": self.registry.contains(
                instrument
            ),
        }

    def compare(
        self,
        left: InstrumentIdentity,
        right: InstrumentIdentity,
    ) -> bool:
        """Return whether two identities represent the same instrument."""
        self._validate_identity(left)
        self._validate_identity(right)

        return left.same_instrument(right)

    def remove(
        self,
        identity_key: str,
    ) -> bool:
        """Remove an instrument by identity key."""
        return self.registry.remove(identity_key)

    def count(self) -> int:
        """Return total registered instrument count."""
        return self.registry.count()

    def list_all(self) -> list[InstrumentIdentity]:
        """Return all registered instruments."""
        return self.registry.list_all()

    def summary(self) -> dict[str, Any]:
        """Return service and registry summary."""
        stats = self.registry.stats()

        return {
            "service": self.__class__.__name__,
            "registry": self.registry.__class__.__name__,
            **stats.to_dict(),
        }

    @staticmethod
    def _validate_identity(
        instrument: InstrumentIdentity,
    ) -> None:
        """Validate service identity input."""
        if not isinstance(
            instrument,
            InstrumentIdentity,
        ):
            raise InstrumentServiceValidationError(
                "instrument must be an InstrumentIdentity"
            )


instrument_service = InstrumentService()


def create_instrument(
    **kwargs: Any,
) -> InstrumentIdentity:
    """Create an instrument using the global service."""
    return instrument_service.create(**kwargs)


def register_instrument(
    instrument: InstrumentIdentity,
    *,
    replace: bool = False,
) -> InstrumentIdentity:
    """Register an instrument using the global service."""
    return instrument_service.register(
        instrument,
        replace=replace,
    )


def get_instrument(
    identity_key: str,
) -> Optional[InstrumentIdentity]:
    """Get an instrument using the global service."""
    return instrument_service.get(identity_key)


def require_instrument(
    identity_key: str,
) -> InstrumentIdentity:
    """Require an instrument using the global service."""
    return instrument_service.require(identity_key)


def find_instruments(
    query: Optional[InstrumentQuery] = None,
    **filters: Any,
) -> list[InstrumentIdentity]:
    """Find instruments using the global service."""
    return instrument_service.find(
        query,
        **filters,
    )


def _normalize_optional(
    value: Optional[str],
) -> Optional[str]:
    """Normalize an optional text filter."""
    if value is None:
        return None

    text = str(value).strip()

    return text.upper() if text else None


__all__ = [
    "InstrumentServiceError",
    "InstrumentServiceValidationError",
    "InstrumentQuery",
    "InstrumentService",
    "instrument_service",
    "create_instrument",
    "register_instrument",
    "get_instrument",
    "require_instrument",
    "find_instruments",
]