"""
ROBOMLM PLUS
V6 Market Currency Schema

Purpose:
    Structural representation of currency identity and conversion context.

Design rules:
    - Immutable schema.
    - Currency agnostic.
    - Supports INR, USD, USDT and other currencies/assets.
    - Currency identity is distinct from account balance.
    - Conversion is represented structurally; no trading decision is made.
    - No execution authorization.
    - No V7+ dependency.
    - Observed and derived values remain explicitly separated.
    - Provenance is preserved.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional


MARKET_CURRENCY_SCHEMA_VERSION = "1.0.0"
MARKET_CURRENCY_SCHEMA = "V6_MARKET_CURRENCY"


@dataclass(frozen=True)
class MarketCurrency:
    """
    Immutable structural representation of a currency or settlement asset.

    Examples:
        currency_code="INR"
        currency_code="USD"
        currency_code="USDT"

    A conversion record can additionally describe a rate between
    source_currency and target_currency.
    """

    # ------------------------------------------------------------------
    # Currency identity
    # ------------------------------------------------------------------

    currency_id: Optional[str] = None
    currency_code: Optional[str] = None
    currency_name: Optional[str] = None
    currency_type: Optional[str] = None

    # ------------------------------------------------------------------
    # Currency classification
    # ------------------------------------------------------------------

    asset_class: Optional[str] = None
    settlement_type: Optional[str] = None
    issuer: Optional[str] = None
    network: Optional[str] = None

    # ------------------------------------------------------------------
    # Conversion identity
    # ------------------------------------------------------------------

    source_currency: Optional[str] = None
    target_currency: Optional[str] = None
    conversion_pair: Optional[str] = None

    # ------------------------------------------------------------------
    # Conversion rate
    # ------------------------------------------------------------------

    conversion_rate: Optional[float] = None
    inverse_rate: Optional[float] = None
    rate_timestamp: Optional[str] = None
    rate_source: Optional[str] = None

    # ------------------------------------------------------------------
    # Precision / denomination
    # ------------------------------------------------------------------

    decimal_places: Optional[int] = None
    minimum_unit: Optional[float] = None

    # ------------------------------------------------------------------
    # Market / environment identity
    # ------------------------------------------------------------------

    broker: Optional[str] = None
    provider: Optional[str] = None
    venue: Optional[str] = None
    environment: Optional[str] = None
    mode: Optional[str] = None

    # ------------------------------------------------------------------
    # Lifecycle / status
    # ------------------------------------------------------------------

    currency_state: Optional[str] = None
    is_active: Optional[bool] = None

    # ------------------------------------------------------------------
    # Session / request references
    # ------------------------------------------------------------------

    timestamp: Optional[str] = None
    sequence: Optional[int] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Source / provenance
    # ------------------------------------------------------------------

    source: Optional[str] = None
    source_type: Optional[str] = None
    source_reference: Optional[str] = None
    provenance: Mapping[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Explicit observed / derived separation
    # ------------------------------------------------------------------

    observed_fields: tuple[str, ...] = field(default_factory=tuple)
    derived_fields: tuple[str, ...] = field(default_factory=tuple)

    # ------------------------------------------------------------------
    # Additional metadata
    # ------------------------------------------------------------------

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate structural invariants."""

        if self.sequence is not None:
            if isinstance(self.sequence, bool):
                raise TypeError(
                    "sequence must be an integer or None."
                )

            if not isinstance(self.sequence, int):
                raise TypeError(
                    "sequence must be an integer or None."
                )

            if self.sequence < 0:
                raise ValueError("sequence must be non-negative.")

        if self.decimal_places is not None:
            if isinstance(self.decimal_places, bool):
                raise TypeError(
                    "decimal_places must be an integer or None."
                )

            if not isinstance(self.decimal_places, int):
                raise TypeError(
                    "decimal_places must be an integer or None."
                )

            if self.decimal_places < 0:
                raise ValueError(
                    "decimal_places must be non-negative."
                )

        numeric_fields = (
            "conversion_rate",
            "inverse_rate",
            "minimum_unit",
        )

        for field_name in numeric_fields:
            value = getattr(self, field_name)

            if value is not None:
                if isinstance(value, bool):
                    raise TypeError(
                        f"{field_name} must be numeric when provided."
                    )

                try:
                    numeric_value = float(value)
                except (TypeError, ValueError) as exc:
                    raise ValueError(
                        f"{field_name} must be numeric when provided."
                    ) from exc

                if field_name in {"conversion_rate", "inverse_rate"}:
                    if numeric_value <= 0:
                        raise ValueError(
                            f"{field_name} must be greater than zero."
                        )

                if field_name == "minimum_unit":
                    if numeric_value < 0:
                        raise ValueError(
                            "minimum_unit cannot be negative."
                        )

        for field_name in (
            "currency_code",
            "source_currency",
            "target_currency",
        ):
            value = getattr(self, field_name)

            if value is not None and not str(value).strip():
                raise ValueError(
                    f"{field_name} cannot be empty."
                )

        if self.provenance is None:
            raise TypeError(
                "provenance must be a mapping."
            )

        if not isinstance(self.provenance, Mapping):
            raise TypeError(
                "provenance must be a mapping."
            )

        if self.metadata is None:
            raise TypeError(
                "metadata must be a mapping."
            )

        if not isinstance(self.metadata, Mapping):
            raise TypeError(
                "metadata must be a mapping."
            )

        if isinstance(self.observed_fields, str):
            raise TypeError(
                "observed_fields must be a sequence of names."
            )

        if isinstance(self.derived_fields, str):
            raise TypeError(
                "derived_fields must be a sequence of names."
            )

        object.__setattr__(
            self,
            "provenance",
            MappingProxyType(dict(self.provenance)),
        )

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )

        object.__setattr__(
            self,
            "observed_fields",
            tuple(self.observed_fields),
        )

        object.__setattr__(
            self,
            "derived_fields",
            tuple(self.derived_fields),
        )

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    def has_identity(self) -> bool:
        return bool(self.currency_id or self.currency_code)

    def has_currency_identity(self) -> bool:
        return bool(self.currency_code)

    def has_currency_code(self) -> bool:
        return bool(self.currency_code)

    def has_timestamp(self) -> bool:
        return bool(self.timestamp)

    # ------------------------------------------------------------------
    # Currency classification
    # ------------------------------------------------------------------

    def is_fiat(self) -> bool:
        return str(self.currency_type or "").upper() == "FIAT"

    def is_stablecoin(self) -> bool:
        return str(self.currency_type or "").upper() in {
            "STABLECOIN",
            "STABLE_COIN",
        }

    def is_crypto(self) -> bool:
        return str(self.currency_type or "").upper() in {
            "CRYPTO",
            "CRYPTOCURRENCY",
        }

    def is_digital_asset(self) -> bool:
        return self.is_crypto() or self.is_stablecoin()

    # ------------------------------------------------------------------
    # Known currency convenience checks
    # ------------------------------------------------------------------

    def is_inr(self) -> bool:
        return str(self.currency_code or "").upper() == "INR"

    def is_usd(self) -> bool:
        return str(self.currency_code or "").upper() == "USD"

    def is_usdt(self) -> bool:
        return str(self.currency_code or "").upper() == "USDT"

    # ------------------------------------------------------------------
    # Conversion identity
    # ------------------------------------------------------------------

    def has_conversion_pair(self) -> bool:
        return bool(
            self.conversion_pair
            or (
                self.source_currency
                and self.target_currency
            )
        )

    def get_conversion_pair(self) -> Optional[str]:
        if self.conversion_pair:
            return self.conversion_pair

        if self.source_currency and self.target_currency:
            return (
                f"{self.source_currency}/"
                f"{self.target_currency}"
            )

        return None

    def has_conversion_rate(self) -> bool:
        return self.conversion_rate is not None

    def has_inverse_rate(self) -> bool:
        return self.inverse_rate is not None

    # ------------------------------------------------------------------
    # Conversion calculations
    # ------------------------------------------------------------------

    def calculate_inverse_rate(self) -> Optional[float]:
        """
        Calculate inverse conversion rate.

        Example:
            USD/INR = 83
            inverse = INR/USD = 1 / 83
        """

        if self.inverse_rate is not None:
            return float(self.inverse_rate)

        if self.conversion_rate is None:
            return None

        rate = float(self.conversion_rate)

        if rate <= 0:
            return None

        return 1.0 / rate

    def convert_amount(self, amount: float) -> Optional[float]:
        """
        Convert an amount using the supplied conversion rate.

        Returns None when no conversion rate is available.
        """

        if self.conversion_rate is None:
            return None

        return float(amount) * float(self.conversion_rate)

    def convert_amount_inverse(self, amount: float) -> Optional[float]:
        """
        Convert using the inverse conversion rate.
        """

        inverse = self.calculate_inverse_rate()

        if inverse is None:
            return None

        return float(amount) * inverse

    # ------------------------------------------------------------------
    # Precision
    # ------------------------------------------------------------------

    def has_precision(self) -> bool:
        return (
            self.decimal_places is not None
            or self.minimum_unit is not None
        )

    def has_minimum_unit(self) -> bool:
        return self.minimum_unit is not None

    # ------------------------------------------------------------------
    # Environment
    # ------------------------------------------------------------------

    def has_environment_identity(self) -> bool:
        return bool(
            self.broker
            or self.provider
            or self.venue
            or self.environment
            or self.mode
        )

    # ------------------------------------------------------------------
    # Source / provenance
    # ------------------------------------------------------------------

    def has_source_reference(self) -> bool:
        return bool(
            self.source
            or self.source_type
            or self.source_reference
            or self.rate_source
        )

    def has_provenance(self) -> bool:
        return bool(self.provenance)

    def observed_field_names(self) -> tuple[str, ...]:
        return tuple(self.observed_fields)

    def derived_field_names(self) -> tuple[str, ...]:
        return tuple(self.derived_fields)

    # ------------------------------------------------------------------
    # Structural diagnostics
    # ------------------------------------------------------------------

    def issue_flags(self) -> list[str]:
        issues: list[str] = []

        if not self.currency_code:
            issues.append("MISSING_CURRENCY_CODE")

        if (
            self.source_currency
            and self.target_currency
            and self.source_currency.upper()
            == self.target_currency.upper()
        ):
            issues.append("IDENTICAL_CONVERSION_CURRENCIES")

        if (
            self.conversion_pair
            and (
                not self.source_currency
                or not self.target_currency
            )
        ):
            issues.append("PAIR_COMPONENTS_NOT_EXPLICIT")

        if (
            self.conversion_rate is not None
            and self.conversion_rate <= 0
        ):
            issues.append("INVALID_CONVERSION_RATE")

        if (
            self.inverse_rate is not None
            and self.inverse_rate <= 0
        ):
            issues.append("INVALID_INVERSE_RATE")

        if (
            self.minimum_unit is not None
            and self.minimum_unit <= 0
        ):
            issues.append("NON_POSITIVE_MINIMUM_UNIT")

        return issues

    def is_structurally_valid(self) -> bool:
        return len(self.issue_flags()) == 0

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "currency_id": self.currency_id,
            "currency_code": self.currency_code,
            "currency_name": self.currency_name,
            "currency_type": self.currency_type,
            "asset_class": self.asset_class,
            "settlement_type": self.settlement_type,
            "issuer": self.issuer,
            "network": self.network,
            "source_currency": self.source_currency,
            "target_currency": self.target_currency,
            "conversion_pair": self.conversion_pair,
            "conversion_rate": self.conversion_rate,
            "inverse_rate": self.inverse_rate,
            "rate_timestamp": self.rate_timestamp,
            "rate_source": self.rate_source,
            "decimal_places": self.decimal_places,
            "minimum_unit": self.minimum_unit,
            "broker": self.broker,
            "provider": self.provider,
            "venue": self.venue,
            "environment": self.environment,
            "mode": self.mode,
            "currency_state": self.currency_state,
            "is_active": self.is_active,
            "timestamp": self.timestamp,
            "sequence": self.sequence,
            "session_id": self.session_id,
            "request_id": self.request_id,
            "source": self.source,
            "source_type": self.source_type,
            "source_reference": self.source_reference,
            "provenance": dict(self.provenance),
            "observed_fields": list(self.observed_fields),
            "derived_fields": list(self.derived_fields),
            "metadata": dict(self.metadata),
        }

    def schema_info(self) -> dict[str, Any]:
        return {
            "schema": MARKET_CURRENCY_SCHEMA,
            "version": MARKET_CURRENCY_SCHEMA_VERSION,
            "immutable": True,
            "currency_agnostic": True,
            "supports_inr": True,
            "supports_usd": True,
            "supports_usdt": True,
            "conversion_context_supported": True,
            "decision_logic": False,
            "execution_authorization": False,
            "v7_dependency": False,
        }


# ----------------------------------------------------------------------
# Health
# ----------------------------------------------------------------------

def market_currency_health() -> dict[str, Any]:
    return {
        "schema": MARKET_CURRENCY_SCHEMA,
        "version": MARKET_CURRENCY_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "currency_agnostic": True,
        "supports_inr": True,
        "supports_usd": True,
        "supports_usdt": True,
        "multi_currency": True,
        "conversion_supported": True,
        "precision_supported": True,
        "provenance_supported": True,
        "observed_derived_separation": True,
        "decision_logic": False,
        "execution_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_CURRENCY_SCHEMA_VERSION",
    "MARKET_CURRENCY_SCHEMA",
    "MarketCurrency",
    "market_currency_health",
]
