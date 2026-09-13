"""
ROBOMLM PLUS
V6 Market Identity Schema

Purpose:
    Precise structural identity of a market/instrument/contract/venue.

Rules:
    - Identity only.
    - No market-data calculation.
    - No trading decisions.
    - No execution logic.
    - No intelligence generation.
    - No V7+ dependency.
    - Preserves precise market/instrument/contract identity.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Optional


MARKET_IDENTITY_SCHEMA_VERSION = "1.0.0"
MARKET_IDENTITY_SCHEMA = "V6_MARKET_IDENTITY"


@dataclass(frozen=True)
class MarketIdentity:
    """
    Immutable identity descriptor for a market observation.

    The fields intentionally distinguish market, instrument, contract,
    exchange/venue, and expiry so that different tradable identities
    are not silently merged.
    """

    # ------------------------------------------------------------------
    # Market / Instrument Identity
    # ------------------------------------------------------------------

    market: Optional[str] = None
    instrument: Optional[str] = None
    symbol: Optional[str] = None

    # ------------------------------------------------------------------
    # Venue Identity
    # ------------------------------------------------------------------

    exchange: Optional[str] = None
    venue: Optional[str] = None

    # ------------------------------------------------------------------
    # Contract Identity
    # ------------------------------------------------------------------

    contract: Optional[str] = None
    contract_type: Optional[str] = None
    expiry: Optional[str] = None
    strike: Optional[float] = None
    option_type: Optional[str] = None

    # ------------------------------------------------------------------
    # Currency / Unit Identity
    # ------------------------------------------------------------------

    currency: Optional[str] = None
    quote_currency: Optional[str] = None
    unit: Optional[str] = None

    # ------------------------------------------------------------------
    # Additional Identity Metadata
    # ------------------------------------------------------------------

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate structural identity information."""

        if self.strike is not None:
            if isinstance(self.strike, bool):
                raise TypeError(
                    "MarketIdentity.strike must be numeric or None."
                )

            if not isinstance(self.strike, (int, float)):
                raise TypeError(
                    "MarketIdentity.strike must be numeric or None."
                )

        if self.metadata is None:
            raise TypeError(
                "MarketIdentity.metadata must be a mapping."
            )

        if not isinstance(self.metadata, Mapping):
            raise TypeError(
                "MarketIdentity.metadata must be a mapping."
            )

    # ------------------------------------------------------------------
    # Identity Checks
    # ------------------------------------------------------------------

    def has_market_identity(self) -> bool:
        """
        Return True when a market or instrument identifier exists.
        """

        return bool(
            self.market
            or self.instrument
            or self.symbol
        )

    def has_venue_identity(self) -> bool:
        """
        Return True when exchange or venue information exists.
        """

        return bool(
            self.exchange
            or self.venue
        )

    def has_contract_identity(self) -> bool:
        """
        Return True when contract-level identity exists.
        """

        return bool(
            self.contract
            or self.contract_type
            or self.expiry
            or self.strike is not None
            or self.option_type
        )

    def is_option_contract(self) -> bool:
        """
        Return whether the identity structurally represents an option.
        """

        if self.option_type:
            return True

        if self.contract_type:
            return self.contract_type.upper() in {
                "OPTION",
                "OPTIONS",
            }

        return False

    def is_complete(self) -> bool:
        """
        Return whether the minimum primary identity is available.

        This is an identity completeness check only.
        """

        return bool(
            self.market
            and (
                self.instrument
                or self.symbol
            )
            and (
                self.exchange
                or self.venue
            )
        )

    # ------------------------------------------------------------------
    # Identity Key
    # ------------------------------------------------------------------

    def identity_key(self) -> str:
        """
        Build a deterministic textual identity key.

        Empty components are omitted so that the key remains compact
        while preserving the identity dimensions that are available.
        """

        parts = [
            self.market,
            self.instrument,
            self.symbol,
            self.exchange,
            self.venue,
            self.contract,
            self.contract_type,
            self.expiry,
            str(self.strike) if self.strike is not None else None,
            self.option_type,
            self.currency,
            self.quote_currency,
            self.unit,
        ]

        return "|".join(
            str(value).strip()
            for value in parts
            if value is not None and str(value).strip()
        )

    # ------------------------------------------------------------------
    # Structural Issues
    # ------------------------------------------------------------------

    def issue_flags(self) -> tuple[str, ...]:
        """
        Return structural identity issues.

        No trading or intelligence decision is made here.
        """

        issues: list[str] = []

        if not self.market:
            issues.append("MISSING_MARKET")

        if not self.instrument and not self.symbol:
            issues.append("MISSING_INSTRUMENT_ID")

        if not self.exchange and not self.venue:
            issues.append("MISSING_VENUE")

        if self.is_option_contract():
            if not self.expiry:
                issues.append("MISSING_OPTION_EXPIRY")

            if self.strike is None:
                issues.append("MISSING_OPTION_STRIKE")

            if not self.option_type:
                issues.append("MISSING_OPTION_TYPE")

        return tuple(issues)

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize identity into a JSON-safe mapping.
        """

        data = asdict(self)
        data["metadata"] = dict(self.metadata)

        return data

    @staticmethod
    def schema_info() -> dict[str, str]:
        """Return schema identity and version."""

        return {
            "schema": MARKET_IDENTITY_SCHEMA,
            "version": MARKET_IDENTITY_SCHEMA_VERSION,
        }


def market_identity_health() -> dict[str, Any]:
    """
    Return structural health information for the V6 identity schema.
    """

    return {
        "schema": MARKET_IDENTITY_SCHEMA,
        "version": MARKET_IDENTITY_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "precise_identity_supported": True,
        "market_supported": True,
        "instrument_supported": True,
        "contract_supported": True,
        "venue_supported": True,
        "expiry_supported": True,
        "decision_logic": False,
        "execution_logic": False,
        "intelligence_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_IDENTITY_SCHEMA_VERSION",
    "MARKET_IDENTITY_SCHEMA",
    "MarketIdentity",
    "market_identity_health",
]