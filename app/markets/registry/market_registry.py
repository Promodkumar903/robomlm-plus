"""
ROBOMLM PLUS
Market Registry

Central registry for canonical market identities and market metadata.

This registry is intentionally independent from live market connectivity,
broker/exchange operations, and order execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import RLock
from typing import Any, Iterable, Mapping, Optional


class MarketRegistryError(Exception):
    """Base exception for market registry failures."""


class MarketNotFoundError(MarketRegistryError):
    """Raised when a market cannot be found."""


class DuplicateMarketError(MarketRegistryError):
    """Raised when a market already exists."""


class MarketValidationError(MarketRegistryError):
    """Raised when market registry input is invalid."""


@dataclass
class MarketDefinition:
    """
    Canonical definition of a supported market.

    A market definition describes the market domain itself. It is not
    a live market snapshot and contains no execution state.
    """

    market: str
    name: Optional[str] = None
    market_type: Optional[str] = None
    region: Optional[str] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    venue_ids: list[str] = field(default_factory=list)
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.market = _normalize_required(
            self.market,
            "market",
        )

        self.name = _normalize_optional(self.name)
        self.market_type = _normalize_optional(
            self.market_type
        )
        self.region = _normalize_optional(self.region)
        self.currency = _normalize_optional(
            self.currency
        )
        self.timezone = _normalize_optional(
            self.timezone
        )

        if self.venue_ids is None:
            self.venue_ids = []

        self.venue_ids = _normalize_list(
            self.venue_ids
        )

        if not isinstance(self.enabled, bool):
            raise MarketValidationError(
                "enabled must be boolean"
            )

        if not isinstance(self.metadata, dict):
            self.metadata = dict(
                self.metadata or {}
            )

    @property
    def identity_key(self) -> str:
        """Return the canonical market identity."""
        return self.market

    def add_venue(
        self,
        venue: str,
    ) -> bool:
        """Add a venue to the market definition."""
        normalized = _normalize_required(
            venue,
            "venue",
        )

        if normalized in self.venue_ids:
            return False

        self.venue_ids.append(normalized)
        return True

    def remove_venue(
        self,
        venue: str,
    ) -> bool:
        """Remove a venue from the market definition."""
        normalized = _normalize_required(
            venue,
            "venue",
        )

        if normalized not in self.venue_ids:
            return False

        self.venue_ids.remove(normalized)
        return True

    def has_venue(
        self,
        venue: str,
    ) -> bool:
        """Return whether the market contains a venue."""
        normalized = _normalize_required(
            venue,
            "venue",
        )

        return normalized in self.venue_ids

    def set_enabled(
        self,
        enabled: bool,
    ) -> None:
        """Set market availability state."""
        if not isinstance(enabled, bool):
            raise MarketValidationError(
                "enabled must be boolean"
            )

        self.enabled = enabled

    def update_metadata(
        self,
        **metadata: Any,
    ) -> None:
        """Merge metadata into the definition."""
        self.metadata.update(metadata)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the market definition."""
        return {
            "market": self.market,
            "name": self.name,
            "market_type": self.market_type,
            "region": self.region,
            "currency": self.currency,
            "timezone": self.timezone,
            "venue_ids": list(self.venue_ids),
            "enabled": self.enabled,
            "metadata": dict(self.metadata),
            "identity_key": self.identity_key,
        }

    @classmethod
    def from_mapping(
        cls,
        data: Mapping[str, Any],
    ) -> "MarketDefinition":
        """Create a market definition from a mapping."""
        if not isinstance(data, Mapping):
            raise MarketValidationError(
                "data must be a mapping"
            )

        values = dict(data)
        values.pop("identity_key", None)

        return cls(**values)

    def copy(self) -> "MarketDefinition":
        """Return an independent copy."""
        return MarketDefinition(
            market=self.market,
            name=self.name,
            market_type=self.market_type,
            region=self.region,
            currency=self.currency,
            timezone=self.timezone,
            venue_ids=list(self.venue_ids),
            enabled=self.enabled,
            metadata=dict(self.metadata),
        )


@dataclass(frozen=True)
class MarketRegistryStats:
    """Registry statistics."""

    total: int
    enabled: int
    disabled: int

    def to_dict(self) -> dict[str, int]:
        """Return statistics as a dictionary."""
        return {
            "total": self.total,
            "enabled": self.enabled,
            "disabled": self.disabled,
        }


class MarketRegistry:
    """
    Thread-safe registry for MarketDefinition objects.
    """

    def __init__(self) -> None:
        self._items: dict[str, MarketDefinition] = {}
        self._lock = RLock()

    def register(
        self,
        market: MarketDefinition,
        *,
        replace: bool = False,
    ) -> MarketDefinition:
        """Register one market definition."""
        self._validate(market)

        key = market.identity_key

        with self._lock:
            if key in self._items and not replace:
                raise DuplicateMarketError(
                    f"Market already registered: {key}"
                )

            stored = market.copy()
            self._items[key] = stored

            return stored.copy()

    def register_many(
        self,
        markets: Iterable[MarketDefinition],
        *,
        replace: bool = False,
    ) -> list[MarketDefinition]:
        """Register multiple market definitions."""
        items = list(markets)

        for market in items:
            self._validate(market)

        results: list[MarketDefinition] = []

        with self._lock:
            for market in items:
                key = market.identity_key

                if key in self._items and not replace:
                    raise DuplicateMarketError(
                        f"Market already registered: {key}"
                    )

                stored = market.copy()
                self._items[key] = stored
                results.append(stored.copy())

        return results

    def create(
        self,
        *,
        market: str,
        name: Optional[str] = None,
        market_type: Optional[str] = None,
        region: Optional[str] = None,
        currency: Optional[str] = None,
        timezone: Optional[str] = None,
        venue_ids: Optional[Iterable[str]] = None,
        enabled: bool = True,
        metadata: Optional[Mapping[str, Any]] = None,
        replace: bool = False,
    ) -> MarketDefinition:
        """Create and register a market definition."""
        definition = MarketDefinition(
            market=market,
            name=name,
            market_type=market_type,
            region=region,
            currency=currency,
            timezone=timezone,
            venue_ids=list(venue_ids or []),
            enabled=enabled,
            metadata=dict(metadata or {}),
        )

        return self.register(
            definition,
            replace=replace,
        )

    def get(
        self,
        market: str,
    ) -> Optional[MarketDefinition]:
        """Return a market definition or None."""
        key = _normalize_required(
            market,
            "market",
        )

        with self._lock:
            item = self._items.get(key)

            if item is None:
                return None

            return item.copy()

    def require(
        self,
        market: str,
    ) -> MarketDefinition:
        """Return a market definition or raise."""
        item = self.get(market)

        if item is None:
            raise MarketNotFoundError(
                f"Market not found: {market}"
            )

        return item

    def exists(
        self,
        market: str,
    ) -> bool:
        """Return whether a market exists."""
        key = _normalize_required(
            market,
            "market",
        )

        with self._lock:
            return key in self._items

    def contains(
        self,
        market: MarketDefinition,
    ) -> bool:
        """Return whether a market definition is registered."""
        self._validate(market)

        return self.exists(market.identity_key)

    def find(
        self,
        *,
        market_type: Optional[str] = None,
        region: Optional[str] = None,
        currency: Optional[str] = None,
        timezone: Optional[str] = None,
        enabled: Optional[bool] = None,
        venue: Optional[str] = None,
    ) -> list[MarketDefinition]:
        """Find markets using definition attributes."""
        market_type = _normalize_optional(
            market_type
        )
        region = _normalize_optional(region)
        currency = _normalize_optional(currency)
        timezone = _normalize_optional(timezone)

        if enabled is not None and not isinstance(
            enabled,
            bool,
        ):
            raise MarketValidationError(
                "enabled filter must be boolean"
            )

        normalized_venue = (
            _normalize_optional(venue)
            if venue is not None
            else None
        )

        with self._lock:
            results: list[MarketDefinition] = []

            for item in self._items.values():
                if (
                    market_type is not None
                    and item.market_type != market_type
                ):
                    continue

                if (
                    region is not None
                    and item.region != region
                ):
                    continue

                if (
                    currency is not None
                    and item.currency != currency
                ):
                    continue

                if (
                    timezone is not None
                    and item.timezone != timezone
                ):
                    continue

                if (
                    enabled is not None
                    and item.enabled != enabled
                ):
                    continue

                if (
                    normalized_venue is not None
                    and normalized_venue
                    not in item.venue_ids
                ):
                    continue

                results.append(item.copy())

            return results

    def enabled_markets(self) -> list[MarketDefinition]:
        """Return enabled markets."""
        return self.find(enabled=True)

    def disabled_markets(self) -> list[MarketDefinition]:
        """Return disabled markets."""
        return self.find(enabled=False)

    def list_by_region(
        self,
        region: str,
    ) -> list[MarketDefinition]:
        """Return markets in a region."""
        return self.find(region=region)

    def list_by_type(
        self,
        market_type: str,
    ) -> list[MarketDefinition]:
        """Return markets of a given type."""
        return self.find(market_type=market_type)

    def list_by_currency(
        self,
        currency: str,
    ) -> list[MarketDefinition]:
        """Return markets using a currency."""
        return self.find(currency=currency)

    def list_by_venue(
        self,
        venue: str,
    ) -> list[MarketDefinition]:
        """Return markets containing a venue."""
        return self.find(venue=venue)

    def set_enabled(
        self,
        market: str,
        enabled: bool,
    ) -> MarketDefinition:
        """Update enabled state of a registered market."""
        if not isinstance(enabled, bool):
            raise MarketValidationError(
                "enabled must be boolean"
            )

        key = _normalize_required(
            market,
            "market",
        )

        with self._lock:
            item = self._items.get(key)

            if item is None:
                raise MarketNotFoundError(
                    f"Market not found: {market}"
                )

            updated = item.copy()
            updated.set_enabled(enabled)
            self._items[key] = updated

            return updated.copy()

    def add_venue(
        self,
        market: str,
        venue: str,
    ) -> MarketDefinition:
        """Add a venue to a registered market."""
        key = _normalize_required(
            market,
            "market",
        )

        with self._lock:
            item = self._items.get(key)

            if item is None:
                raise MarketNotFoundError(
                    f"Market not found: {market}"
                )

            updated = item.copy()
            updated.add_venue(venue)
            self._items[key] = updated

            return updated.copy()

    def remove_venue(
        self,
        market: str,
        venue: str,
    ) -> MarketDefinition:
        """Remove a venue from a registered market."""
        key = _normalize_required(
            market,
            "market",
        )

        with self._lock:
            item = self._items.get(key)

            if item is None:
                raise MarketNotFoundError(
                    f"Market not found: {market}"
                )

            updated = item.copy()
            updated.remove_venue(venue)
            self._items[key] = updated

            return updated.copy()

    def update_metadata(
        self,
        market: str,
        **metadata: Any,
    ) -> MarketDefinition:
        """Merge metadata into a registered market."""
        key = _normalize_required(
            market,
            "market",
        )

        with self._lock:
            item = self._items.get(key)

            if item is None:
                raise MarketNotFoundError(
                    f"Market not found: {market}"
                )

            updated = item.copy()
            updated.update_metadata(**metadata)
            self._items[key] = updated

            return updated.copy()

    def remove(
        self,
        market: str,
    ) -> bool:
        """Remove a market definition."""
        key = _normalize_required(
            market,
            "market",
        )

        with self._lock:
            if key not in self._items:
                return False

            del self._items[key]
            return True

    def clear(self) -> int:
        """Remove all markets and return removed count."""
        with self._lock:
            count = len(self._items)
            self._items.clear()
            return count

    def count(self) -> int:
        """Return total market count."""
        with self._lock:
            return len(self._items)

    def keys(self) -> list[str]:
        """Return all market identity keys."""
        with self._lock:
            return list(self._items.keys())

    def list_all(self) -> list[MarketDefinition]:
        """Return all registered markets."""
        with self._lock:
            return [
                item.copy()
                for item in self._items.values()
            ]

    def stats(self) -> MarketRegistryStats:
        """Return registry statistics."""
        with self._lock:
            values = list(self._items.values())

            enabled = sum(
                1
                for item in values
                if item.enabled
            )

            return MarketRegistryStats(
                total=len(values),
                enabled=enabled,
                disabled=len(values) - enabled,
            )

    def snapshot(self) -> dict[str, dict[str, Any]]:
        """Return a serialized registry snapshot."""
        with self._lock:
            return {
                key: item.to_dict()
                for key, item in self._items.items()
            }

    def summary(self) -> dict[str, Any]:
        """Return registry summary."""
        stats = self.stats()

        return {
            "registry": self.__class__.__name__,
            **stats.to_dict(),
        }

    @staticmethod
    def _validate(
        market: MarketDefinition,
    ) -> None:
        """Validate registry input."""
        if not isinstance(
            market,
            MarketDefinition,
        ):
            raise MarketValidationError(
                "market must be a MarketDefinition"
            )


def _normalize_required(
    value: Any,
    field_name: str,
) -> str:
    """Normalize a required text value."""
    if value is None:
        raise MarketValidationError(
            f"{field_name} is required"
        )

    text = str(value).strip()

    if not text:
        raise MarketValidationError(
            f"{field_name} cannot be empty"
        )

    return text.upper()


def _normalize_optional(
    value: Any,
) -> Optional[str]:
    """Normalize an optional text value."""
    if value is None:
        return None

    text = str(value).strip()

    return text.upper() if text else None


def _normalize_list(
    values: Iterable[Any],
) -> list[str]:
    """Normalize a collection of text identifiers."""
    result: list[str] = []

    for value in values:
        normalized = _normalize_required(
            value,
            "venue",
        )

        if normalized not in result:
            result.append(normalized)

    return result


market_registry = MarketRegistry()


def register_market(
    market: MarketDefinition,
    *,
    replace: bool = False,
) -> MarketDefinition:
    """Register a market in the global registry."""
    return market_registry.register(
        market,
        replace=replace,
    )


def create_market(
    **kwargs: Any,
) -> MarketDefinition:
    """Create a market in the global registry."""
    return market_registry.create(**kwargs)


def get_market(
    market: str,
) -> Optional[MarketDefinition]:
    """Get a market from the global registry."""
    return market_registry.get(market)


def require_market(
    market: str,
) -> MarketDefinition:
    """Require a market from the global registry."""
    return market_registry.require(market)


def find_markets(
    **filters: Any,
) -> list[MarketDefinition]:
    """Find markets in the global registry."""
    return market_registry.find(**filters)


__all__ = [
    "MarketRegistryError",
    "MarketNotFoundError",
    "DuplicateMarketError",
    "MarketValidationError",
    "MarketDefinition",
    "MarketRegistryStats",
    "MarketRegistry",
    "market_registry",
    "register_market",
    "create_market",
    "get_market",
    "require_market",
    "find_markets",
]