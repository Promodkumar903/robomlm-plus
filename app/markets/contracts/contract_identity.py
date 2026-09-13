"""
ROBOMLM PLUS
Contract Identity

Canonical identity model for market contracts.

A contract is kept distinct from the underlying instrument. This
module is identity-focused and performs no market-data, broker,
exchange, or execution operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Mapping, Optional


class ContractIdentityError(Exception):
    """Base exception for contract-identity failures."""


class ContractIdentityValidationError(ContractIdentityError):
    """Raised when contract identity data is invalid."""


@dataclass(frozen=True)
class ContractIdentity:
    """
    Canonical identity of a tradable market contract.

    The identity fields deliberately separate:
    - market
    - instrument
    - venue
    - contract
    - expiry
    - strike
    - option type
    - contract type
    """

    market: str
    instrument: str
    venue: str
    contract: str

    contract_type: Optional[str] = None
    expiry: Optional[date] = None
    strike: Optional[float] = None
    option_type: Optional[str] = None
    currency: Optional[str] = None
    multiplier: Optional[float] = None

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        market = _required_text(self.market, "market")
        instrument = _required_text(
            self.instrument,
            "instrument",
        )
        venue = _required_text(self.venue, "venue")
        contract = _required_text(
            self.contract,
            "contract",
        )

        object.__setattr__(self, "market", market)
        object.__setattr__(self, "instrument", instrument)
        object.__setattr__(self, "venue", venue)
        object.__setattr__(self, "contract", contract)

        if self.contract_type is not None:
            object.__setattr__(
                self,
                "contract_type",
                _optional_text(self.contract_type),
            )

        if self.currency is not None:
            object.__setattr__(
                self,
                "currency",
                _optional_text(self.currency),
            )

        if self.expiry is not None:
            object.__setattr__(
                self,
                "expiry",
                _normalize_date(self.expiry),
            )

        if self.strike is not None:
            strike = _finite_number(
                self.strike,
                "strike",
            )

            if strike < 0:
                raise ContractIdentityValidationError(
                    "strike cannot be negative"
                )

            object.__setattr__(
                self,
                "strike",
                strike,
            )

        if self.option_type is not None:
            option_type = _optional_text(
                self.option_type
            )

            if option_type is not None:
                option_type = option_type.upper()

            object.__setattr__(
                self,
                "option_type",
                option_type,
            )

        if self.multiplier is not None:
            multiplier = _finite_number(
                self.multiplier,
                "multiplier",
            )

            if multiplier <= 0:
                raise ContractIdentityValidationError(
                    "multiplier must be greater than zero"
                )

            object.__setattr__(
                self,
                "multiplier",
                multiplier,
            )

        object.__setattr__(
            self,
            "metadata",
            dict(self.metadata or {}),
        )

        self._validate_contract_structure()

    def _validate_contract_structure(self) -> None:
        """Validate relationships between contract identity fields."""
        option_type = self.option_type

        if option_type is not None:
            allowed = {
                "CE",
                "PE",
                "CALL",
                "PUT",
            }

            if option_type not in allowed:
                raise ContractIdentityValidationError(
                    f"Unsupported option_type: {self.option_type}"
                )

            if self.strike is None:
                raise ContractIdentityValidationError(
                    "strike is required for option contracts"
                )

            if self.expiry is None:
                raise ContractIdentityValidationError(
                    "expiry is required for option contracts"
                )

    @property
    def identity_key(self) -> str:
        """
        Return the deterministic canonical identity key.

        Expiry, strike and option type are included when present.
        """
        parts = [
            self.market,
            self.instrument,
            self.venue,
            self.contract,
        ]

        if self.expiry is not None:
            parts.append(self.expiry.isoformat())

        if self.strike is not None:
            parts.append(_format_number(self.strike))

        if self.option_type is not None:
            parts.append(self.option_type)

        return "|".join(
            _normalize_key_part(part)
            for part in parts
        )

    @property
    def is_derivative(self) -> bool:
        """Return whether the contract has derivative identity."""
        return any(
            value is not None
            for value in (
                self.expiry,
                self.strike,
                self.option_type,
            )
        )

    @property
    def is_option(self) -> bool:
        """Return whether the contract is an option."""
        return self.option_type is not None

    @property
    def is_expired(self) -> bool:
        """Return whether the contract expiry date has passed."""
        if self.expiry is None:
            return False

        return self.expiry < date.today()

    def same_contract(
        self,
        other: "ContractIdentity",
    ) -> bool:
        """Compare two complete contract identities."""
        if not isinstance(other, ContractIdentity):
            return False

        return self.identity_key == other.identity_key

    def with_metadata(
        self,
        **metadata: Any,
    ) -> "ContractIdentity":
        """Return a copy with merged metadata."""
        merged = dict(self.metadata)
        merged.update(metadata)

        return ContractIdentity(
            market=self.market,
            instrument=self.instrument,
            venue=self.venue,
            contract=self.contract,
            contract_type=self.contract_type,
            expiry=self.expiry,
            strike=self.strike,
            option_type=self.option_type,
            currency=self.currency,
            multiplier=self.multiplier,
            metadata=merged,
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable representation."""
        return {
            "market": self.market,
            "instrument": self.instrument,
            "venue": self.venue,
            "contract": self.contract,
            "contract_type": self.contract_type,
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
        value: Mapping[str, Any],
    ) -> "ContractIdentity":
        """Create contract identity from a mapping."""
        if not isinstance(value, Mapping):
            raise ContractIdentityValidationError(
                "value must be a mapping"
            )

        return cls(
            market=value.get("market", ""),
            instrument=value.get("instrument", ""),
            venue=value.get("venue", ""),
            contract=value.get("contract", ""),
            contract_type=value.get("contract_type"),
            expiry=_parse_optional_date(
                value.get("expiry")
            ),
            strike=value.get("strike"),
            option_type=value.get("option_type"),
            currency=value.get("currency"),
            multiplier=value.get("multiplier"),
            metadata=dict(
                value.get("metadata") or {}
            ),
        )


def _required_text(
    value: Any,
    field_name: str,
) -> str:
    """Validate a required textual field."""
    text = str(value).strip()

    if not text:
        raise ContractIdentityValidationError(
            f"{field_name} is required"
        )

    return text


def _optional_text(value: Any) -> Optional[str]:
    """Normalize an optional text value."""
    if value is None:
        return None

    text = str(value).strip()

    return text or None


def _finite_number(
    value: Any,
    field_name: str,
) -> float:
    """Validate and normalize a finite numeric value."""
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ContractIdentityValidationError(
            f"{field_name} must be numeric"
        ) from exc

    if number != number:
        raise ContractIdentityValidationError(
            f"{field_name} cannot be NaN"
        )

    if number in (
        float("inf"),
        float("-inf"),
    ):
        raise ContractIdentityValidationError(
            f"{field_name} must be finite"
        )

    return number


def _normalize_date(value: date) -> date:
    """Validate a date object."""
    if isinstance(value, datetime):
        return value.date()

    if not isinstance(value, date):
        raise ContractIdentityValidationError(
            "expiry must be a date"
        )

    return value


def _parse_optional_date(
    value: Any,
) -> Optional[date]:
    """Parse an optional date or ISO date string."""
    if value is None:
        return None

    if isinstance(value, date):
        return _normalize_date(value)

    if isinstance(value, str):
        text = value.strip()

        if not text:
            return None

        try:
            return date.fromisoformat(text)
        except ValueError as exc:
            raise ContractIdentityValidationError(
                "Invalid expiry date"
            ) from exc

    raise ContractIdentityValidationError(
        "expiry must be a date, ISO date string, or None"
    )


def _normalize_key_part(value: Any) -> str:
    """Normalize one identity-key component."""
    return str(value).strip().upper()


def _format_number(value: float) -> str:
    """Produce a stable compact representation of a number."""
    if value.is_integer():
        return str(int(value))

    return format(value, ".15g")


def create_contract_identity(
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
) -> ContractIdentity:
    """Convenience factory for ContractIdentity."""
    return ContractIdentity(
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
        metadata=dict(metadata or {}),
    )


def contract_identity_key(
    contract: ContractIdentity,
) -> str:
    """Return the canonical identity key for a contract."""
    if not isinstance(contract, ContractIdentity):
        raise ContractIdentityValidationError(
            "contract must be a ContractIdentity"
        )

    return contract.identity_key


__all__ = [
    "ContractIdentityError",
    "ContractIdentityValidationError",
    "ContractIdentity",
    "create_contract_identity",
    "contract_identity_key",
]