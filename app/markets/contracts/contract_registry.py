"""
ROBOMLM PLUS
Contract Registry

In-process registry for canonical ContractIdentity objects.

This module is identity and lookup infrastructure only. It performs
no network access, broker/exchange calls, or execution operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Optional

from .contract_identity import (
    ContractIdentity,
    ContractIdentityValidationError,
)


class ContractRegistryError(Exception):
    """Base exception for contract-registry failures."""


class ContractNotFoundError(ContractRegistryError):
    """Raised when a requested contract does not exist."""


class DuplicateContractError(ContractRegistryError):
    """Raised when duplicate registration is explicitly rejected."""


@dataclass(frozen=True)
class ContractRegistryStats:
    """Compact registry statistics."""

    total: int
    derivatives: int
    options: int
    expired: int

    def to_dict(self) -> dict[str, int]:
        return {
            "total": self.total,
            "derivatives": self.derivatives,
            "options": self.options,
            "expired": self.expired,
        }


class ContractRegistry:
    """
    Canonical in-process contract registry.

    Identity is determined by ContractIdentity.identity_key.
    """

    def __init__(self) -> None:
        self._contracts: dict[str, ContractIdentity] = {}

    @staticmethod
    def _validate_contract(
        contract: ContractIdentity,
    ) -> ContractIdentity:
        if not isinstance(contract, ContractIdentity):
            raise ContractIdentityValidationError(
                "contract must be a ContractIdentity"
            )

        return contract

    def register(
        self,
        contract: ContractIdentity,
        *,
        replace: bool = False,
    ) -> ContractIdentity:
        """
        Register a contract.

        By default duplicate identities are rejected. Set replace=True
        when an explicit replacement is intended.
        """
        contract = self._validate_contract(contract)
        key = contract.identity_key

        if key in self._contracts and not replace:
            raise DuplicateContractError(
                f"Contract already registered: {key}"
            )

        self._contracts[key] = contract
        return contract

    def register_many(
        self,
        contracts: Iterable[ContractIdentity],
        *,
        replace: bool = False,
    ) -> list[ContractIdentity]:
        """Register multiple contracts."""
        registered: list[ContractIdentity] = []

        for contract in contracts:
            registered.append(
                self.register(
                    contract,
                    replace=replace,
                )
            )

        return registered

    def get(
        self,
        identity_key: str,
    ) -> Optional[ContractIdentity]:
        """Return a contract by canonical identity key."""
        key = str(identity_key).strip().upper()

        if not key:
            return None

        return self._contracts.get(key)

    def require(
        self,
        identity_key: str,
    ) -> ContractIdentity:
        """Return a contract or raise ContractNotFoundError."""
        contract = self.get(identity_key)

        if contract is None:
            raise ContractNotFoundError(
                f"Contract not found: {identity_key}"
            )

        return contract

    def get_by_identity(
        self,
        contract: ContractIdentity,
    ) -> Optional[ContractIdentity]:
        """Look up a contract using a ContractIdentity object."""
        contract = self._validate_contract(contract)
        return self.get(contract.identity_key)

    def require_by_identity(
        self,
        contract: ContractIdentity,
    ) -> ContractIdentity:
        """Require a contract using a ContractIdentity object."""
        contract = self._validate_contract(contract)
        return self.require(contract.identity_key)

    def exists(
        self,
        identity_key: str,
    ) -> bool:
        """Return whether a canonical identity key exists."""
        key = str(identity_key).strip().upper()

        if not key:
            return False

        return key in self._contracts

    def contains(
        self,
        contract: ContractIdentity,
    ) -> bool:
        """Return whether a ContractIdentity is registered."""
        contract = self._validate_contract(contract)
        return contract.identity_key in self._contracts

    def remove(
        self,
        identity_key: str,
    ) -> bool:
        """Remove a contract by identity key."""
        key = str(identity_key).strip().upper()

        if key not in self._contracts:
            return False

        del self._contracts[key]
        return True

    def remove_contract(
        self,
        contract: ContractIdentity,
    ) -> bool:
        """Remove a contract using its identity."""
        contract = self._validate_contract(contract)
        return self.remove(contract.identity_key)

    def clear(self) -> None:
        """Remove all registered contracts."""
        self._contracts.clear()

    def count(self) -> int:
        """Return total registered contracts."""
        return len(self._contracts)

    def keys(self) -> list[str]:
        """Return all canonical identity keys."""
        return list(self._contracts.keys())

    def list_all(self) -> list[ContractIdentity]:
        """Return all registered contracts."""
        return list(self._contracts.values())

    def list_by_market(
        self,
        market: str,
    ) -> list[ContractIdentity]:
        """Return contracts belonging to a market."""
        target = str(market).strip().upper()

        return [
            contract
            for contract in self._contracts.values()
            if contract.market.upper() == target
        ]

    def list_by_instrument(
        self,
        instrument: str,
    ) -> list[ContractIdentity]:
        """Return contracts belonging to an instrument."""
        target = str(instrument).strip().upper()

        return [
            contract
            for contract in self._contracts.values()
            if contract.instrument.upper() == target
        ]

    def list_by_venue(
        self,
        venue: str,
    ) -> list[ContractIdentity]:
        """Return contracts belonging to a venue."""
        target = str(venue).strip().upper()

        return [
            contract
            for contract in self._contracts.values()
            if contract.venue.upper() == target
        ]

    def list_derivatives(self) -> list[ContractIdentity]:
        """Return all derivative contracts."""
        return [
            contract
            for contract in self._contracts.values()
            if contract.is_derivative
        ]

    def list_options(self) -> list[ContractIdentity]:
        """Return all option contracts."""
        return [
            contract
            for contract in self._contracts.values()
            if contract.is_option
        ]

    def list_expired(self) -> list[ContractIdentity]:
        """Return contracts whose expiry has passed."""
        return [
            contract
            for contract in self._contracts.values()
            if contract.is_expired
        ]

    def find(
        self,
        *,
        market: Optional[str] = None,
        instrument: Optional[str] = None,
        venue: Optional[str] = None,
        contract_type: Optional[str] = None,
        expiry: Any = None,
        option_type: Optional[str] = None,
    ) -> list[ContractIdentity]:
        """
        Filter registered contracts by identity attributes.

        None means no filter for that attribute.
        """
        results = list(self._contracts.values())

        if market is not None:
            target = str(market).strip().upper()
            results = [
                item
                for item in results
                if item.market.upper() == target
            ]

        if instrument is not None:
            target = str(instrument).strip().upper()
            results = [
                item
                for item in results
                if item.instrument.upper() == target
            ]

        if venue is not None:
            target = str(venue).strip().upper()
            results = [
                item
                for item in results
                if item.venue.upper() == target
            ]

        if contract_type is not None:
            target = str(contract_type).strip().upper()
            results = [
                item
                for item in results
                if (
                    item.contract_type is not None
                    and item.contract_type.upper() == target
                )
            ]

        if expiry is not None:
            results = [
                item
                for item in results
                if item.expiry == expiry
            ]

        if option_type is not None:
            target = str(option_type).strip().upper()

            aliases = {
                "CALL": {"CALL", "CE"},
                "PUT": {"PUT", "PE"},
                "CE": {"CE", "CALL"},
                "PE": {"PE", "PUT"},
            }

            accepted = aliases.get(
                target,
                {target},
            )

            results = [
                item
                for item in results
                if item.option_type in accepted
            ]

        return results

    def stats(self) -> ContractRegistryStats:
        """Return registry statistics."""
        contracts = self.list_all()

        return ContractRegistryStats(
            total=len(contracts),
            derivatives=sum(
                contract.is_derivative
                for contract in contracts
            ),
            options=sum(
                contract.is_option
                for contract in contracts
            ),
            expired=sum(
                contract.is_expired
                for contract in contracts
            ),
        )

    def snapshot(self) -> dict[str, dict[str, Any]]:
        """Return a serializable registry snapshot."""
        return {
            key: contract.to_dict()
            for key, contract in self._contracts.items()
        }

    def summary(self) -> dict[str, Any]:
        """Return a compact registry summary."""
        return {
            "registry": self.__class__.__name__,
            **self.stats().to_dict(),
        }


contract_registry = ContractRegistry()


def register_contract(
    contract: ContractIdentity,
    *,
    replace: bool = False,
) -> ContractIdentity:
    """Register a contract in the global registry."""
    return contract_registry.register(
        contract,
        replace=replace,
    )


def get_contract(
    identity_key: str,
) -> Optional[ContractIdentity]:
    """Get a contract from the global registry."""
    return contract_registry.get(identity_key)


def require_contract(
    identity_key: str,
) -> ContractIdentity:
    """Require a contract from the global registry."""
    return contract_registry.require(identity_key)


def find_contracts(
    **filters: Any,
) -> list[ContractIdentity]:
    """Find contracts using the global registry."""
    return contract_registry.find(**filters)


__all__ = [
    "ContractRegistryError",
    "ContractNotFoundError",
    "DuplicateContractError",
    "ContractRegistryStats",
    "ContractRegistry",
    "contract_registry",
    "register_contract",
    "get_contract",
    "require_contract",
    "find_contracts",
]