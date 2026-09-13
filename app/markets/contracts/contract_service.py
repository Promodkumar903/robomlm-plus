"""
ROBOMLM PLUS
Contract Service

Application-level service for contract identity creation, registration,
lookup, filtering, and lifecycle validation.

This service does not perform broker/exchange calls or order execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Iterable, Mapping, Optional

from .contract_identity import (
    ContractIdentity,
    ContractIdentityValidationError,
    create_contract_identity,
)
from .contract_registry import (
    ContractNotFoundError,
    ContractRegistry,
    contract_registry,
)


class ContractServiceError(Exception):
    """Base exception for contract-service failures."""


class ContractServiceValidationError(ContractServiceError):
    """Raised when contract-service input is invalid."""


@dataclass(frozen=True)
class ContractQuery:
    """Normalized contract lookup criteria."""

    market: Optional[str] = None
    instrument: Optional[str] = None
    venue: Optional[str] = None
    contract_type: Optional[str] = None
    expiry: Optional[date] = None
    option_type: Optional[str] = None

    def normalized(self) -> "ContractQuery":
        """Return a normalized copy of the query."""
        return ContractQuery(
            market=_normalize_optional(self.market),
            instrument=_normalize_optional(self.instrument),
            venue=_normalize_optional(self.venue),
            contract_type=_normalize_optional(
                self.contract_type
            ),
            expiry=self.expiry,
            option_type=_normalize_optional(
                self.option_type
            ),
        )


class ContractService:
    """
    Application service around ContractIdentity and ContractRegistry.
    """

    def __init__(
        self,
        registry: Optional[ContractRegistry] = None,
    ) -> None:
        self.registry = registry or contract_registry

    def create(
        self,
        *,
        market: str,
        instrument: str,
        venue: str,
        contract: str,
        contract_type: Optional[str] = None,
        expiry: Optional[date] = None,
        strike: Optional[float] = None,
        option_type: Optional[str] = None,
        currency: Optional[str] = None,
        multiplier: Optional[float] = None,
        metadata: Optional[Mapping[str, Any]] = None,
        replace: bool = False,
    ) -> ContractIdentity:
        """Create and register a contract identity."""
        try:
            identity = create_contract_identity(
                market=market,
                instrument=instrument,
                venue=venue,
                contract=contract,
                contract_type=contract_type,
                expiry=expiry,
                strike=strike,
                option_type=option_type,
                currency=currency,
                multiplier=multiplier,
                metadata=metadata,
            )
        except ContractIdentityValidationError as exc:
            raise ContractServiceValidationError(
                str(exc)
            ) from exc

        return self.registry.register(
            identity,
            replace=replace,
        )

    def register(
        self,
        contract: ContractIdentity,
        *,
        replace: bool = False,
    ) -> ContractIdentity:
        """Register an existing contract identity."""
        if not isinstance(contract, ContractIdentity):
            raise ContractServiceValidationError(
                "contract must be a ContractIdentity"
            )

        return self.registry.register(
            contract,
            replace=replace,
        )

    def register_many(
        self,
        contracts: Iterable[ContractIdentity],
        *,
        replace: bool = False,
    ) -> list[ContractIdentity]:
        """Register multiple contract identities."""
        return self.registry.register_many(
            contracts,
            replace=replace,
        )

    def get(
        self,
        identity_key: str,
    ) -> Optional[ContractIdentity]:
        """Get a contract by canonical identity key."""
        return self.registry.get(identity_key)

    def require(
        self,
        identity_key: str,
    ) -> ContractIdentity:
        """Require a contract by canonical identity key."""
        try:
            return self.registry.require(identity_key)
        except ContractNotFoundError as exc:
            raise ContractServiceError(
                str(exc)
            ) from exc

    def exists(
        self,
        identity_key: str,
    ) -> bool:
        """Return whether a contract exists."""
        return self.registry.exists(identity_key)

    def find(
        self,
        query: Optional[ContractQuery] = None,
        **filters: Any,
    ) -> list[ContractIdentity]:
        """
        Find contracts using a ContractQuery or explicit filters.

        Explicit filters are merged with the query, with explicit
        keyword filters taking precedence.
        """
        if query is not None and not isinstance(
            query,
            ContractQuery,
        ):
            raise ContractServiceValidationError(
                "query must be a ContractQuery"
            )

        normalized_query = (
            query.normalized()
            if query is not None
            else ContractQuery()
        )

        merged = {
            "market": normalized_query.market,
            "instrument": normalized_query.instrument,
            "venue": normalized_query.venue,
            "contract_type": normalized_query.contract_type,
            "expiry": normalized_query.expiry,
            "option_type": normalized_query.option_type,
        }

        for key, value in filters.items():
            if key not in merged:
                raise ContractServiceValidationError(
                    f"Unknown contract filter: {key}"
                )

            merged[key] = value

        return self.registry.find(**merged)

    def find_by_market(
        self,
        market: str,
    ) -> list[ContractIdentity]:
        """Find contracts by market."""
        return self.registry.list_by_market(market)

    def find_by_instrument(
        self,
        instrument: str,
    ) -> list[ContractIdentity]:
        """Find contracts by instrument."""
        return self.registry.list_by_instrument(
            instrument
        )

    def find_by_venue(
        self,
        venue: str,
    ) -> list[ContractIdentity]:
        """Find contracts by venue."""
        return self.registry.list_by_venue(venue)

    def derivatives(self) -> list[ContractIdentity]:
        """Return all derivative contracts."""
        return self.registry.list_derivatives()

    def options(self) -> list[ContractIdentity]:
        """Return all option contracts."""
        return self.registry.list_options()

    def expired(self) -> list[ContractIdentity]:
        """Return all expired contracts."""
        return self.registry.list_expired()

    def remove(
        self,
        identity_key: str,
    ) -> bool:
        """Remove a contract by identity key."""
        return self.registry.remove(identity_key)

    def validate_identity(
        self,
        contract: ContractIdentity,
    ) -> dict[str, Any]:
        """
        Validate a contract identity and return validation facts.

        This method does not alter the registry.
        """
        if not isinstance(contract, ContractIdentity):
            raise ContractServiceValidationError(
                "contract must be a ContractIdentity"
            )

        return {
            "valid": True,
            "identity_key": contract.identity_key,
            "is_derivative": contract.is_derivative,
            "is_option": contract.is_option,
            "is_expired": contract.is_expired,
            "registered": self.registry.contains(contract),
        }

    def compare(
        self,
        left: ContractIdentity,
        right: ContractIdentity,
    ) -> bool:
        """Return whether two identities represent the same contract."""
        if not isinstance(left, ContractIdentity):
            raise ContractServiceValidationError(
                "left must be a ContractIdentity"
            )

        if not isinstance(right, ContractIdentity):
            raise ContractServiceValidationError(
                "right must be a ContractIdentity"
            )

        return left.same_contract(right)

    def summary(self) -> dict[str, Any]:
        """Return service and registry summary."""
        stats = self.registry.stats()

        return {
            "service": self.__class__.__name__,
            "registry": self.registry.__class__.__name__,
            **stats.to_dict(),
        }


def _normalize_optional(
    value: Optional[str],
) -> Optional[str]:
    """Normalize an optional text filter."""
    if value is None:
        return None

    text = str(value).strip()

    return text or None


contract_service = ContractService()


def create_contract(
    **kwargs: Any,
) -> ContractIdentity:
    """Create a contract using the global contract service."""
    return contract_service.create(**kwargs)


def register_contract(
    contract: ContractIdentity,
    *,
    replace: bool = False,
) -> ContractIdentity:
    """Register a contract using the global contract service."""
    return contract_service.register(
        contract,
        replace=replace,
    )


def get_contract(
    identity_key: str,
) -> Optional[ContractIdentity]:
    """Get a contract using the global contract service."""
    return contract_service.get(identity_key)


def require_contract(
    identity_key: str,
) -> ContractIdentity:
    """Require a contract using the global contract service."""
    return contract_service.require(identity_key)


def find_contracts(
    query: Optional[ContractQuery] = None,
    **filters: Any,
) -> list[ContractIdentity]:
    """Find contracts using the global contract service."""
    return contract_service.find(
        query,
        **filters,
    )


__all__ = [
    "ContractServiceError",
    "ContractServiceValidationError",
    "ContractQuery",
    "ContractService",
    "contract_service",
    "create_contract",
    "register_contract",
    "get_contract",
    "require_contract",
    "find_contracts",
]