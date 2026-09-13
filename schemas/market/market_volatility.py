"""
ROBOMLM PLUS
V6 Market Volatility Schema

Purpose:
    Structural representation of observed and derived market volatility
    information.

Rules:
    - Volatility representation only.
    - No trading decision.
    - No execution logic.
    - No order generation.
    - No prediction.
    - No V7+ dependency.
    - Observed and derived information remain distinguishable.
    - Range, dispersion, and volatility are kept structurally separate.
    - Does not mutate source data.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from math import isfinite
from typing import Any, Mapping, Optional


MARKET_VOLATILITY_SCHEMA_VERSION = "1.0.0"
MARKET_VOLATILITY_SCHEMA = "V6_MARKET_VOLATILITY"


@dataclass(frozen=True)
class MarketVolatility:
    """
    Immutable structural representation of market volatility.

    The schema stores volatility measurements and their classification.
    It does not determine trade direction or execution.
    """

    # ------------------------------------------------------------------
    # Volatility Identity
    # ------------------------------------------------------------------

    volatility_id: Optional[str] = None
    timestamp: Optional[str] = None
    sequence: Optional[int] = None

    # ------------------------------------------------------------------
    # Market Identity
    # ------------------------------------------------------------------

    market: Optional[str] = None
    instrument: Optional[str] = None
    symbol: Optional[str] = None
    exchange: Optional[str] = None
    venue: Optional[str] = None
    contract: Optional[str] = None
    expiry: Optional[str] = None

    # ------------------------------------------------------------------
    # Source References
    # ------------------------------------------------------------------

    observation_id: Optional[str] = None
    context_id: Optional[str] = None
    regime_id: Optional[str] = None
    structure_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Observed Volatility Inputs
    # ------------------------------------------------------------------

    price: Optional[float] = None
    previous_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    close_price: Optional[float] = None

    # ------------------------------------------------------------------
    # Range Measurements
    # ------------------------------------------------------------------

    price_range: Optional[float] = None
    true_range: Optional[float] = None
    range_percent: Optional[float] = None

    # ------------------------------------------------------------------
    # Volatility Measurements
    # ------------------------------------------------------------------

    realized_volatility: Optional[float] = None
    implied_volatility: Optional[float] = None
    historical_volatility: Optional[float] = None
    intraday_volatility: Optional[float] = None

    # ------------------------------------------------------------------
    # Dispersion / Change Measurements
    # ------------------------------------------------------------------

    price_change: Optional[float] = None
    price_change_percent: Optional[float] = None
    dispersion: Optional[float] = None

    # ------------------------------------------------------------------
    # Volatility Classification
    # ------------------------------------------------------------------

    volatility_state: Optional[str] = None
    volatility_level: Optional[str] = None
    volatility_phase: Optional[str] = None
    expansion_state: Optional[str] = None
    compression_state: Optional[str] = None

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    volatility_score: Optional[float] = None
    confidence: Optional[float] = None

    # ------------------------------------------------------------------
    # Provenance
    # ------------------------------------------------------------------

    source: Optional[str] = None
    source_type: Optional[str] = None

    # ------------------------------------------------------------------
    # Observed / Derived Separation
    # ------------------------------------------------------------------

    observed_fields: tuple[str, ...] = field(default_factory=tuple)
    derived_fields: tuple[str, ...] = field(default_factory=tuple)

    # ------------------------------------------------------------------
    # Additional Metadata
    # ------------------------------------------------------------------

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate structural volatility information."""

        if self.sequence is not None:
            if isinstance(self.sequence, bool):
                raise TypeError(
                    "MarketVolatility.sequence must be an integer or None."
                )

            if not isinstance(self.sequence, int):
                raise TypeError(
                    "MarketVolatility.sequence must be an integer or None."
                )

            if self.sequence < 0:
                raise ValueError(
                    "MarketVolatility.sequence cannot be negative."
                )

        numeric_fields = {
            "price": self.price,
            "previous_price": self.previous_price,
            "high_price": self.high_price,
            "low_price": self.low_price,
            "close_price": self.close_price,
            "price_range": self.price_range,
            "true_range": self.true_range,
            "range_percent": self.range_percent,
            "realized_volatility": self.realized_volatility,
            "implied_volatility": self.implied_volatility,
            "historical_volatility": self.historical_volatility,
            "intraday_volatility": self.intraday_volatility,
            "price_change": self.price_change,
            "price_change_percent": self.price_change_percent,
            "dispersion": self.dispersion,
            "volatility_score": self.volatility_score,
            "confidence": self.confidence,
        }

        for field_name, value in numeric_fields.items():
            if value is None:
                continue

            if isinstance(value, bool):
                raise TypeError(
                    f"MarketVolatility.{field_name} "
                    "must be numeric or None."
                )

            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"MarketVolatility.{field_name} "
                    "must be numeric or None."
                )

            if not isfinite(float(value)):
                raise ValueError(
                    f"MarketVolatility.{field_name} "
                    "must be finite when provided."
                )

        for field_name in (
            "price_range",
            "true_range",
            "dispersion",
        ):
            value = getattr(self, field_name)

            if value is not None and value < 0:
                raise ValueError(
                    f"MarketVolatility.{field_name} cannot be negative."
                )

        for field_name in (
            "range_percent",
            "implied_volatility",
            "historical_volatility",
            "realized_volatility",
            "intraday_volatility",
            "volatility_score",
            "confidence",
        ):
            value = getattr(self, field_name)

            if value is not None and value < 0:
                raise ValueError(
                    f"MarketVolatility.{field_name} cannot be negative."
                )

        if self.metadata is None:
            raise TypeError(
                "MarketVolatility.metadata must be a mapping."
            )

        if not isinstance(self.metadata, Mapping):
            raise TypeError(
                "MarketVolatility.metadata must be a mapping."
            )

        if isinstance(self.observed_fields, str):
            raise TypeError(
                "MarketVolatility.observed_fields "
                "must be a sequence of names."
            )

        if isinstance(self.derived_fields, str):
            raise TypeError(
                "MarketVolatility.derived_fields "
                "must be a sequence of names."
            )

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    def has_identity(self) -> bool:
        """Return True when sufficient market identity exists."""

        return bool(
            self.market
            or self.instrument
            or self.symbol
        )

    def has_volatility_identity(self) -> bool:
        """Return True when volatility ID or timestamp exists."""

        return bool(
            self.volatility_id
            or self.timestamp
        )

    # ------------------------------------------------------------------
    # Price / Range
    # ------------------------------------------------------------------

    def has_price(self) -> bool:
        """Return True when current price is available."""

        return self.price is not None

    def has_price_range(self) -> bool:
        """Return True when a price range is available."""

        return self.price_range is not None

    def has_ohlc_range(self) -> bool:
        """Return True when high and low prices are available."""

        return (
            self.high_price is not None
            and self.low_price is not None
        )

    def calculate_price_range(self) -> Optional[float]:
        """
        Calculate high-low price range.

        This is a structural calculation only.
        """

        if not self.has_ohlc_range():
            return None

        return self.high_price - self.low_price

    # ------------------------------------------------------------------
    # Price Change
    # ------------------------------------------------------------------

    def calculate_price_change(self) -> Optional[float]:
        """
        Calculate current price change from previous price.

        This is a structural calculation only.
        """

        if self.price is None or self.previous_price is None:
            return None

        return self.price - self.previous_price

    def calculate_price_change_percent(self) -> Optional[float]:
        """
        Calculate percentage price change.

        Returns None when previous price is unavailable or zero.
        """

        if self.price is None or self.previous_price is None:
            return None

        if self.previous_price == 0:
            return None

        return (
            (self.price - self.previous_price)
            / self.previous_price
        ) * 100.0

    # ------------------------------------------------------------------
    # Volatility Availability
    # ------------------------------------------------------------------

    def has_realized_volatility(self) -> bool:
        """Return True when realized volatility exists."""

        return self.realized_volatility is not None

    def has_implied_volatility(self) -> bool:
        """Return True when implied volatility exists."""

        return self.implied_volatility is not None

    def has_historical_volatility(self) -> bool:
        """Return True when historical volatility exists."""

        return self.historical_volatility is not None

    def has_intraday_volatility(self) -> bool:
        """Return True when intraday volatility exists."""

        return self.intraday_volatility is not None

    def has_volatility_measure(self) -> bool:
        """Return True when at least one volatility measure exists."""

        return any(
            value is not None
            for value in (
                self.realized_volatility,
                self.implied_volatility,
                self.historical_volatility,
                self.intraday_volatility,
            )
        )

    # ------------------------------------------------------------------
    # Structural States
    # ------------------------------------------------------------------

    def has_volatility_state(self) -> bool:
        """Return True when volatility state exists."""

        return bool(self.volatility_state)

    def has_expansion_state(self) -> bool:
        """Return True when expansion state exists."""

        return bool(self.expansion_state)

    def has_compression_state(self) -> bool:
        """Return True when compression state exists."""

        return bool(self.compression_state)

    # ------------------------------------------------------------------
    # Source References
    # ------------------------------------------------------------------

    def has_source_reference(self) -> bool:
        """Return True when an upstream reference exists."""

        return bool(
            self.observation_id
            or self.context_id
            or self.regime_id
            or self.structure_id
        )

    # ------------------------------------------------------------------
    # Provenance
    # ------------------------------------------------------------------

    def observed_field_names(self) -> tuple[str, ...]:
        """Return explicitly observed field names."""

        return tuple(self.observed_fields)

    def derived_field_names(self) -> tuple[str, ...]:
        """Return explicitly derived field names."""

        return tuple(self.derived_fields)

    # ------------------------------------------------------------------
    # Structural Validation
    # ------------------------------------------------------------------

    def issue_flags(self) -> tuple[str, ...]:
        """
        Return structural volatility issues.

        Validation only. No trading decision is produced.
        """

        issues: list[str] = []

        if not self.has_identity():
            issues.append("MISSING_MARKET_IDENTITY")

        if not self.timestamp:
            issues.append("MISSING_TIMESTAMP")

        if not self.source:
            issues.append("MISSING_SOURCE")

        if not self.has_volatility_measure():
            if not self.has_price_range() and not self.has_ohlc_range():
                issues.append("MISSING_VOLATILITY_MEASURE")

        if (
            self.high_price is not None
            and self.low_price is not None
            and self.high_price < self.low_price
        ):
            issues.append("INVALID_HIGH_LOW_RELATION")

        if not self.has_source_reference():
            issues.append("MISSING_SOURCE_REFERENCE")

        if (
            self.derived_fields
            and not self.has_source_reference()
        ):
            issues.append(
                "DERIVED_VOLATILITY_WITHOUT_SOURCE_REFERENCE"
            )

        return tuple(issues)

    def is_structurally_valid(self) -> bool:
        """Return True when no structural issues are present."""

        return not self.issue_flags()

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize volatility into a JSON-safe mapping."""

        data = asdict(self)

        data["observed_fields"] = list(self.observed_fields)
        data["derived_fields"] = list(self.derived_fields)
        data["metadata"] = dict(self.metadata)

        return data

    @staticmethod
    def schema_info() -> dict[str, str]:
        """Return schema identity and version."""

        return {
            "schema": MARKET_VOLATILITY_SCHEMA,
            "version": MARKET_VOLATILITY_SCHEMA_VERSION,
        }


def market_volatility_health() -> dict[str, Any]:
    """Return structural health information for the V6 volatility schema."""

    return {
        "schema": MARKET_VOLATILITY_SCHEMA,
        "version": MARKET_VOLATILITY_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "market_identity_supported": True,
        "price_reference_supported": True,
        "range_measurement_supported": True,
        "realized_volatility_supported": True,
        "implied_volatility_supported": True,
        "historical_volatility_supported": True,
        "intraday_volatility_supported": True,
        "price_change_supported": True,
        "dispersion_supported": True,
        "volatility_state_supported": True,
        "expansion_state_supported": True,
        "compression_state_supported": True,
        "provenance_supported": True,
        "source_reference_supported": True,
        "observed_derived_separation": True,
        "range_volatility_separation": True,
        "decision_logic": False,
        "execution_logic": False,
        "order_generation": False,
        "prediction_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_VOLATILITY_SCHEMA_VERSION",
    "MARKET_VOLATILITY_SCHEMA",
    "MarketVolatility",
    "market_volatility_health",
]