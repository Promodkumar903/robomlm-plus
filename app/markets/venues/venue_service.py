"""
ROBOMLM PLUS - Venue Service

Purpose:
    Provide the application-level service layer for venue identity
    and registry operations.

Design principles:
    - Uses VenueRegistry as the source of venue definitions.
    - No broker/exchange/network connections.
    - No order execution.
    - No market-data fetching.
    - Keeps venue identity separate from runtime adapter connectivity.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional

from app.markets.registry.venue_registry import (
    VenueDefinition,
    VenueRegistry,
    VenueRegistryError,
    venue_registry,
)


class VenueServiceError(Exception):
    """Base exception for venue service errors."""


class VenueServiceValidationError(VenueServiceError):
    """Raised when venue service input is invalid."""


@dataclass(frozen=True)
class VenueQuery:
    """Structured query for venue discovery."""

    venue_type: Optional[str] = None
    market: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    currency: Optional[str] = None
    enabled: Optional[bool] = None
    data_enabled: Optional[bool] = None
    trading_enabled: Optional[bool] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "venue_type": self.venue_type,
            "market": self.market,
            "region": self.region,
            "country": self.country,
            "currency": self.currency,
            "enabled": self.enabled,
            "data_enabled": self.data_enabled,
            "trading_enabled": self.trading_enabled,
        }


class VenueService:
    """
    Application service for venue registry operations.

    This service coordinates identity and registry access only.
    Runtime connectivity remains outside this layer.
    """

    def __init__(
        self,
        registry: Optional[VenueRegistry] = None,
    ) -> None:
        self.registry = registry or venue_registry

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
        """Create and register a venue."""
        try:
            return self.registry.create(
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
        except VenueRegistryError as exc:
            raise VenueServiceValidationError(
                str(exc)
            ) from exc

    def register(
        self,
        venue: VenueDefinition,
        *,
        replace: bool = False,
    ) -> VenueDefinition:
        """Register a venue definition."""
        try:
            return self.registry.register(
                venue,
                replace=replace,
            )
        except VenueRegistryError as exc:
            raise VenueServiceValidationError(
                str(exc)
            ) from exc

    def register_many(
        self,
        venues: list[VenueDefinition],
        *,
        replace: bool = False,
    ) -> list[VenueDefinition]:
        """Register multiple venue definitions."""
        try:
            return self.registry.register_many(
                venues,
                replace=replace,
            )
        except VenueRegistryError as exc:
            raise VenueServiceValidationError(
                str(exc)
            ) from exc

    def get(
        self,
        venue: str,
    ) -> Optional[VenueDefinition]:
        """Get a venue by canonical venue identity."""
        try:
            return self.registry.get(venue)
        except VenueRegistryError as exc:
            raise VenueServiceValidationError(
                str(exc)
            ) from exc

    def require(
        self,
        venue: str,
    ) -> VenueDefinition:
        """Get a venue or raise an application-level error."""
        try:
            return self.registry.require(venue)
        except VenueRegistryError as exc:
            raise VenueServiceValidationError(
                str(exc)
            ) from exc

    def exists(self, venue: str) -> bool:
        """Return whether a venue exists."""
        try:
            return self.registry.exists(venue)
        except VenueRegistryError as exc:
            raise VenueServiceValidationError(
                str(exc)
            ) from exc

    def find(
        self,
        query: Optional[VenueQuery] = None,
        **filters: Any,
    ) -> list[VenueDefinition]:
        """
        Find venues using a VenueQuery and/or explicit filters.

        Explicit filters override values supplied by VenueQuery.
        """
        if query is not None and not isinstance(query, VenueQuery):
            raise VenueServiceValidationError(
                "query must be a VenueQuery or None."
            )

        values = query.to_dict() if query else {}

        for key, value in filters.items():
            if key not in values:
                raise VenueServiceValidationError(
                    f"Unsupported venue filter: {key}"
                )
            values[key] = value

        return self.registry.find(**values)

    def find_by_type(
        self,
        venue_type: str,
    ) -> list[VenueDefinition]:
        """Find venues by venue type."""
        return self.registry.by_type(venue_type)

    def find_by_market(
        self,
        market: str,
    ) -> list[VenueDefinition]:
        """Find venues by market."""
        return self.registry.by_market(market)

    def find_by_region(
        self,
        region: str,
    ) -> list[VenueDefinition]:
        """Find venues by region."""
        return self.registry.by_region(region)

    def find_by_name(
        self,
        name: str,
    ) -> list[VenueDefinition]:
        """Find venues by exact name."""
        return self.registry.get_by_name(name)

    def enabled(self) -> list[VenueDefinition]:
        """Return enabled venues."""
        return self.registry.enabled()

    def disabled(self) -> list[VenueDefinition]:
        """Return disabled venues."""
        return self.registry.disabled()

    def data_enabled(self) -> list[VenueDefinition]:
        """Return venues enabled for data."""
        return self.registry.data_enabled()

    def trading_enabled(self) -> list[VenueDefinition]:
        """Return venues enabled for trading."""
        return self.registry.trading_enabled()

    def set_enabled(
        self,
        venue: str,
        enabled: bool,
    ) -> VenueDefinition:
        """Set venue application-enabled state."""
        try:
            return self.registry.set_enabled(
                venue,
                enabled,
            )
        except VenueRegistryError as exc:
            raise VenueServiceValidationError(
                str(exc)
            ) from exc

    def set_data_enabled(
        self,
        venue: str,
        enabled: bool,
    ) -> VenueDefinition:
        """Set venue data-enabled state."""
        try:
            return self.registry.set_data_enabled(
                venue,
                enabled,
            )
        except VenueRegistryError as exc:
            raise VenueServiceValidationError(
                str(exc)
            ) from exc

    def set_trading_enabled(
        self,
        venue: str,
        enabled: bool,
    ) -> VenueDefinition:
        """Set venue trading-enabled state."""
        try:
            return self.registry.set_trading_enabled(
                venue,
                enabled,
            )
        except VenueRegistryError as exc:
            raise VenueServiceValidationError(
                str(exc)
            ) from exc

    def update_metadata(
        self,
        venue: str,
        values: Mapping[str, Any],
    ) -> VenueDefinition:
        """Update venue metadata."""
        try:
            return self.registry.update_metadata(
                venue,
                values,
            )
        except VenueRegistryError as exc:
            raise VenueServiceValidationError(
                str(exc)
            ) from exc

    def remove(
        self,
        venue: str,
    ) -> VenueDefinition:
        """Remove a venue."""
        try:
            return self.registry.remove(venue)
        except VenueRegistryError as exc:
            raise VenueServiceValidationError(
                str(exc)
            ) from exc

    def count(self) -> int:
        """Return total number of venues."""
        return self.registry.count()

    def list_all(self) -> list[VenueDefinition]:
        """Return all registered venues."""
        return self.registry.list_all()

    def stats(self) -> dict[str, int]:
        """Return registry statistics."""
        return self.registry.stats().to_dict()

    def snapshot(self) -> list[dict[str, Any]]:
        """Return serializable venue snapshot."""
        return self.registry.snapshot()

    def summary(self) -> dict[str, Any]:
        """Return service-level venue summary."""
        return self.registry.summary()

    def validate_definition(
        self,
        venue: VenueDefinition,
    ) -> bool:
        """Validate a venue definition without registering it."""
        if not isinstance(venue, VenueDefinition):
            raise VenueServiceValidationError(
                "venue must be a VenueDefinition."
            )

        try:
            venue.validate()
        except VenueRegistryError as exc:
            raise VenueServiceValidationError(
                str(exc)
            ) from exc

        return True

    def compare(
        self,
        first: str,
        second: str,
    ) -> bool:
        """
        Compare two venue identities.

        Returns True only when both resolve to the same canonical
        venue identity.
        """
        first_venue = self.require(first)
        second_venue = self.require(second)

        return (
            first_venue.identity_key
            == second_venue.identity_key
        )


# ---------------------------------------------------------------------------
# Global service
# ---------------------------------------------------------------------------

venue_service = VenueService()


# ---------------------------------------------------------------------------
# Convenience functions
# ---------------------------------------------------------------------------

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
    """Create a venue using the global venue service."""
    return venue_service.create(
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


def register_venue(
    venue: VenueDefinition,
    *,
    replace: bool = False,
) -> VenueDefinition:
    """Register a venue using the global venue service."""
    return venue_service.register(
        venue,
        replace=replace,
    )


def get_venue(
    venue: str,
) -> Optional[VenueDefinition]:
    """Get a venue using the global venue service."""
    return venue_service.get(venue)


def require_venue(
    venue: str,
) -> VenueDefinition:
    """Require a venue using the global venue service."""
    return venue_service.require(venue)


def find_venues(
    query: Optional[VenueQuery] = None,
    **filters: Any,
) -> list[VenueDefinition]:
    """Find venues using the global venue service."""
    return venue_service.find(
        query,
        **filters,
    )


def venue_exists(
    venue: str,
) -> bool:
    """Check venue existence using the global venue service."""
    return venue_service.exists(venue)