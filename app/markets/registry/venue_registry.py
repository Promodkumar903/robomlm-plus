"""
ROBOMLM PLUS - Venue Registry

Purpose:
    Maintain canonical in-memory definitions of market venues.

Design principles:
    - Deterministic and side-effect free.
    - No broker/exchange/network connections.
    - Venue identity is explicit and stable.
    - Registry supports registration, lookup, filtering and lifecycle state.
    - Runtime connectivity belongs to adapters/services, not this registry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Iterable, Mapping, Optional


class VenueRegistryError(Exception):
    """Base exception for venue registry errors."""


class VenueNotFoundError(VenueRegistryError):
    """Raised when a requested venue does not exist."""


class DuplicateVenueError(VenueRegistryError):
    """Raised when a venue already exists."""


class VenueValidationError(VenueRegistryError):
    """Raised when venue data is invalid."""


@dataclass
class VenueDefinition:
    """
    Canonical definition of a trading/data venue.

    This object describes venue identity and configuration metadata.
    It does not establish a connection and does not execute orders.
    """

    venue: str
    name: str
    venue_type: str = "OTHER"
    market: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    currency: Optional[str] = None
    enabled: bool = True
    data_enabled: bool = True
    trading_enabled: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        self.venue = self._normalize_required(self.venue, "venue")
        self.name = self._normalize_required(self.name, "name")
        self.venue_type = self._normalize_required(
            self.venue_type,
            "venue_type",
        ).upper()

        if self.market is not None:
            self.market = self._normalize_optional(self.market)

        if self.region is not None:
            self.region = self._normalize_optional(self.region)

        if self.country is not None:
            self.country = self._normalize_optional(self.country)

        if self.timezone is not None:
            self.timezone = self._normalize_optional(self.timezone)

        if self.currency is not None:
            self.currency = self._normalize_optional(self.currency)

        self.enabled = bool(self.enabled)
        self.data_enabled = bool(self.data_enabled)
        self.trading_enabled = bool(self.trading_enabled)

        if not isinstance(self.metadata, dict):
            self.metadata = dict(self.metadata)

        self.validate()

    @staticmethod
    def _normalize_required(value: Any, field_name: str) -> str:
        if value is None:
            raise VenueValidationError(
                f"{field_name} cannot be None."
            )

        text = str(value).strip()

        if not text:
            raise VenueValidationError(
                f"{field_name} cannot be empty."
            )

        return text

    @staticmethod
    def _normalize_optional(value: Any) -> Optional[str]:
        if value is None:
            return None

        text = str(value).strip()
        return text if text else None

    def validate(self) -> None:
        """Validate venue definition."""
        if not self.venue.strip():
            raise VenueValidationError("venue cannot be empty.")

        if not self.name.strip():
            raise VenueValidationError("name cannot be empty.")

        if not self.venue_type.strip():
            raise VenueValidationError(
                "venue_type cannot be empty."
            )

        if not isinstance(self.metadata, dict):
            raise VenueValidationError(
                "metadata must be a dictionary."
            )

    @property
    def identity_key(self) -> str:
        """Return the canonical venue identity key."""
        return self.venue.strip().upper()

    def set_enabled(self, enabled: bool) -> "VenueDefinition":
        """Enable or disable the venue."""
        self.enabled = bool(enabled)
        self.updated_at = datetime.now(timezone.utc)
        return self

    def set_data_enabled(self, enabled: bool) -> "VenueDefinition":
        """Enable or disable venue data usage."""
        self.data_enabled = bool(enabled)
        self.updated_at = datetime.now(timezone.utc)
        return self

    def set_trading_enabled(self, enabled: bool) -> "VenueDefinition":
        """Enable or disable venue trading capability."""
        self.trading_enabled = bool(enabled)
        self.updated_at = datetime.now(timezone.utc)
        return self

    def update_metadata(self, values: Mapping[str, Any]) -> "VenueDefinition":
        """Merge metadata values into the venue metadata."""
        if not isinstance(values, Mapping):
            raise VenueValidationError(
                "metadata update must be a mapping."
            )

        self.metadata.update(dict(values))
        self.updated_at = datetime.now(timezone.utc)
        return self

    def has_metadata(self, key: str) -> bool:
        """Return whether a metadata key exists."""
        return key in self.metadata

    def copy(self) -> "VenueDefinition":
        """Return a detached copy of the venue definition."""
        return VenueDefinition(
            venue=self.venue,
            name=self.name,
            venue_type=self.venue_type,
            market=self.market,
            region=self.region,
            country=self.country,
            timezone=self.timezone,
            currency=self.currency,
            enabled=self.enabled,
            data_enabled=self.data_enabled,
            trading_enabled=self.trading_enabled,
            metadata=dict(self.metadata),
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the venue definition."""
        return {
            "venue": self.venue,
            "name": self.name,
            "venue_type": self.venue_type,
            "market": self.market,
            "region": self.region,
            "country": self.country,
            "timezone": self.timezone,
            "currency": self.currency,
            "enabled": self.enabled,
            "data_enabled": self.data_enabled,
            "trading_enabled": self.trading_enabled,
            "metadata": dict(self.metadata),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_mapping(
        cls,
        value: Mapping[str, Any],
    ) -> "VenueDefinition":
        """Create a venue definition from a mapping."""
        if not isinstance(value, Mapping):
            raise VenueValidationError(
                "venue definition must be a mapping."
            )

        data = dict(value)

        created_at = data.get("created_at")
        updated_at = data.get("updated_at")

        if isinstance(created_at, str):
            data["created_at"] = datetime.fromisoformat(created_at)

        if isinstance(updated_at, str):
            data["updated_at"] = datetime.fromisoformat(updated_at)

        return cls(**data)


@dataclass(frozen=True)
class VenueRegistryStats:
    """Summary statistics for the venue registry."""

    total: int
    enabled: int
    disabled: int
    data_enabled: int
    trading_enabled: int

    def to_dict(self) -> dict[str, int]:
        return {
            "total": self.total,
            "enabled": self.enabled,
            "disabled": self.disabled,
            "data_enabled": self.data_enabled,
            "trading_enabled": self.trading_enabled,
        }


class VenueRegistry:
    """
    Thread-safe in-memory venue registry.

    The registry is responsible only for venue identity and definitions.
    It never performs network operations or trading actions.
    """

    def __init__(
        self,
        venues: Optional[Iterable[VenueDefinition]] = None,
    ) -> None:
        self._lock = RLock()
        self._venues: dict[str, VenueDefinition] = {}

        if venues is not None:
            self.register_many(venues)

    def register(
        self,
        venue: VenueDefinition,
        *,
        replace: bool = False,
    ) -> VenueDefinition:
        """Register one venue."""
        if not isinstance(venue, VenueDefinition):
            raise VenueValidationError(
                "venue must be a VenueDefinition."
            )

        venue.validate()
        key = venue.identity_key

        with self._lock:
            if key in self._venues and not replace:
                raise DuplicateVenueError(
                    f"Venue already exists: {venue.venue}"
                )

            self._venues[key] = venue.copy()

            return self._venues[key].copy()

    def register_many(
        self,
        venues: Iterable[VenueDefinition],
        *,
        replace: bool = False,
    ) -> list[VenueDefinition]:
        """Register multiple venues."""
        if venues is None:
            raise VenueValidationError(
                "venues cannot be None."
            )

        registered: list[VenueDefinition] = []

        for venue in venues:
            registered.append(
                self.register(
                    venue,
                    replace=replace,
                )
            )

        return registered

    def create(
        self,
        venue: str,
        name: str,
        *,
        venue_type: str = "OTHER",
        market: Optional[str] = None,
        region: Optional[str] = None,
        country: Optional[str] = None,
        timezone: Optional[str] = None,
        currency: Optional[str] = None,
        enabled: bool = True,
        data_enabled: bool = True,
        trading_enabled: bool = False,
        metadata: Optional[Mapping[str, Any]] = None,
        replace: bool = False,
    ) -> VenueDefinition:
        """Create and register a venue definition."""
        definition = VenueDefinition(
            venue=venue,
            name=name,
            venue_type=venue_type,
            market=market,
            region=region,
            country=country,
            timezone=timezone,
            currency=currency,
            enabled=enabled,
            data_enabled=data_enabled,
            trading_enabled=trading_enabled,
            metadata=dict(metadata or {}),
        )

        return self.register(
            definition,
            replace=replace,
        )

    def get(self, venue: str) -> Optional[VenueDefinition]:
        """Return a venue or None."""
        key = self._normalize_key(venue)

        with self._lock:
            value = self._venues.get(key)

            if value is None:
                return None

            return value.copy()

    def require(self, venue: str) -> VenueDefinition:
        """Return a venue or raise VenueNotFoundError."""
        result = self.get(venue)

        if result is None:
            raise VenueNotFoundError(
                f"Venue not found: {venue}"
            )

        return result

    def exists(self, venue: str) -> bool:
        """Return whether a venue exists."""
        key = self._normalize_key(venue)

        with self._lock:
            return key in self._venues

    def contains(self, venue: str) -> bool:
        """Alias for exists."""
        return self.exists(venue)

    def get_by_name(self, name: str) -> list[VenueDefinition]:
        """Find venues by exact case-insensitive name."""
        target = self._normalize_text(name)

        with self._lock:
            return [
                venue.copy()
                for venue in self._venues.values()
                if venue.name.strip().casefold() == target.casefold()
            ]

    def list_all(self) -> list[VenueDefinition]:
        """Return all venues."""
        with self._lock:
            return [
                venue.copy()
                for venue in self._venues.values()
            ]

    def find(
        self,
        *,
        venue_type: Optional[str] = None,
        market: Optional[str] = None,
        region: Optional[str] = None,
        country: Optional[str] = None,
        currency: Optional[str] = None,
        enabled: Optional[bool] = None,
        data_enabled: Optional[bool] = None,
        trading_enabled: Optional[bool] = None,
    ) -> list[VenueDefinition]:
        """Find venues matching supplied filters."""
        with self._lock:
            values = list(self._venues.values())

        if venue_type is not None:
            target = self._normalize_text(venue_type).upper()
            values = [
                item
                for item in values
                if item.venue_type.upper() == target
            ]

        if market is not None:
            target = self._normalize_text(market).casefold()
            values = [
                item
                for item in values
                if (item.market or "").casefold() == target
            ]

        if region is not None:
            target = self._normalize_text(region).casefold()
            values = [
                item
                for item in values
                if (item.region or "").casefold() == target
            ]

        if country is not None:
            target = self._normalize_text(country).casefold()
            values = [
                item
                for item in values
                if (item.country or "").casefold() == target
            ]

        if currency is not None:
            target = self._normalize_text(currency).casefold()
            values = [
                item
                for item in values
                if (item.currency or "").casefold() == target
            ]

        if enabled is not None:
            values = [
                item
                for item in values
                if item.enabled is bool(enabled)
            ]

        if data_enabled is not None:
            values = [
                item
                for item in values
                if item.data_enabled is bool(data_enabled)
            ]

        if trading_enabled is not None:
            values = [
                item
                for item in values
                if item.trading_enabled is bool(trading_enabled)
            ]

        return [item.copy() for item in values]

    def enabled(self) -> list[VenueDefinition]:
        """Return enabled venues."""
        return self.find(enabled=True)

    def disabled(self) -> list[VenueDefinition]:
        """Return disabled venues."""
        return self.find(enabled=False)

    def data_enabled(self) -> list[VenueDefinition]:
        """Return venues enabled for data."""
        return self.find(data_enabled=True)

    def trading_enabled(self) -> list[VenueDefinition]:
        """Return venues enabled for trading."""
        return self.find(trading_enabled=True)

    def by_market(self, market: str) -> list[VenueDefinition]:
        """Return venues belonging to a market."""
        return self.find(market=market)

    def by_region(self, region: str) -> list[VenueDefinition]:
        """Return venues belonging to a region."""
        return self.find(region=region)

    def by_type(self, venue_type: str) -> list[VenueDefinition]:
        """Return venues of a specific type."""
        return self.find(venue_type=venue_type)

    def set_enabled(
        self,
        venue: str,
        enabled: bool,
    ) -> VenueDefinition:
        """Update enabled state."""
        key = self._normalize_key(venue)

        with self._lock:
            current = self._venues.get(key)

            if current is None:
                raise VenueNotFoundError(
                    f"Venue not found: {venue}"
                )

            current.set_enabled(enabled)
            return current.copy()

    def set_data_enabled(
        self,
        venue: str,
        enabled: bool,
    ) -> VenueDefinition:
        """Update data-enabled state."""
        key = self._normalize_key(venue)

        with self._lock:
            current = self._venues.get(key)

            if current is None:
                raise VenueNotFoundError(
                    f"Venue not found: {venue}"
                )

            current.set_data_enabled(enabled)
            return current.copy()

    def set_trading_enabled(
        self,
        venue: str,
        enabled: bool,
    ) -> VenueDefinition:
        """Update trading-enabled state."""
        key = self._normalize_key(venue)

        with self._lock:
            current = self._venues.get(key)

            if current is None:
                raise VenueNotFoundError(
                    f"Venue not found: {venue}"
                )

            current.set_trading_enabled(enabled)
            return current.copy()

    def update_metadata(
        self,
        venue: str,
        values: Mapping[str, Any],
    ) -> VenueDefinition:
        """Update venue metadata."""
        key = self._normalize_key(venue)

        with self._lock:
            current = self._venues.get(key)

            if current is None:
                raise VenueNotFoundError(
                    f"Venue not found: {venue}"
                )

            current.update_metadata(values)
            return current.copy()

    def remove(self, venue: str) -> VenueDefinition:
        """Remove and return a venue."""
        key = self._normalize_key(venue)

        with self._lock:
            current = self._venues.pop(key, None)

            if current is None:
                raise VenueNotFoundError(
                    f"Venue not found: {venue}"
                )

            return current.copy()

    def clear(self) -> int:
        """Remove all venues and return the number removed."""
        with self._lock:
            count = len(self._venues)
            self._venues.clear()
            return count

    def count(self) -> int:
        """Return total venue count."""
        with self._lock:
            return len(self._venues)

    def keys(self) -> list[str]:
        """Return canonical venue keys."""
        with self._lock:
            return list(self._venues.keys())

    def stats(self) -> VenueRegistryStats:
        """Return registry statistics."""
        with self._lock:
            values = list(self._venues.values())

        total = len(values)
        enabled = sum(1 for item in values if item.enabled)
        data_enabled = sum(
            1 for item in values if item.data_enabled
        )
        trading_enabled = sum(
            1 for item in values if item.trading_enabled
        )

        return VenueRegistryStats(
            total=total,
            enabled=enabled,
            disabled=total - enabled,
            data_enabled=data_enabled,
            trading_enabled=trading_enabled,
        )

    def snapshot(self) -> list[dict[str, Any]]:
        """Return a serializable registry snapshot."""
        return [
            venue.to_dict()
            for venue in self.list_all()
        ]

    def summary(self) -> dict[str, Any]:
        """Return registry summary."""
        return {
            "stats": self.stats().to_dict(),
            "venues": self.snapshot(),
        }

    @staticmethod
    def _normalize_text(value: Any) -> str:
        if value is None:
            raise VenueValidationError(
                "lookup value cannot be None."
            )

        text = str(value).strip()

        if not text:
            raise VenueValidationError(
                "lookup value cannot be empty."
            )

        return text

    @classmethod
    def _normalize_key(cls, value: Any) -> str:
        return cls._normalize_text(value).upper()


# ---------------------------------------------------------------------------
# Global registry
# ---------------------------------------------------------------------------

venue_registry = VenueRegistry()


# ---------------------------------------------------------------------------
# Convenience functions
# ---------------------------------------------------------------------------

def register_venue(
    venue: VenueDefinition,
    *,
    replace: bool = False,
) -> VenueDefinition:
    """Register a venue in the global registry."""
    return venue_registry.register(
        venue,
        replace=replace,
    )


def create_venue(
    venue: str,
    name: str,
    *,
    venue_type: str = "OTHER",
    market: Optional[str] = None,
    region: Optional[str] = None,
    country: Optional[str] = None,
    timezone: Optional[str] = None,
    currency: Optional[str] = None,
    enabled: bool = True,
    data_enabled: bool = True,
    trading_enabled: bool = False,
    metadata: Optional[Mapping[str, Any]] = None,
    replace: bool = False,
) -> VenueDefinition:
    """Create and register a venue in the global registry."""
    return venue_registry.create(
        venue=venue,
        name=name,
        venue_type=venue_type,
        market=market,
        region=region,
        country=country,
        timezone=timezone,
        currency=currency,
        enabled=enabled,
        data_enabled=data_enabled,
        trading_enabled=trading_enabled,
        metadata=metadata,
        replace=replace,
    )


def get_venue(venue: str) -> Optional[VenueDefinition]:
    """Get a venue from the global registry."""
    return venue_registry.get(venue)


def require_venue(venue: str) -> VenueDefinition:
    """Require a venue from the global registry."""
    return venue_registry.require(venue)


def find_venues(
    *,
    venue_type: Optional[str] = None,
    market: Optional[str] = None,
    region: Optional[str] = None,
    country: Optional[str] = None,
    currency: Optional[str] = None,
    enabled: Optional[bool] = None,
    data_enabled: Optional[bool] = None,
    trading_enabled: Optional[bool] = None,
) -> list[VenueDefinition]:
    """Find venues in the global registry."""
    return venue_registry.find(
        venue_type=venue_type,
        market=market,
        region=region,
        country=country,
        currency=currency,
        enabled=enabled,
        data_enabled=data_enabled,
        trading_enabled=trading_enabled,
    )


def venue_exists(venue: str) -> bool:
    """Return whether a venue exists in the global registry."""
    return venue_registry.exists(venue)