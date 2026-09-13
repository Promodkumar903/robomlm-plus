"""
ROBOMLM PLUS
V6 Market Regime Schema

Purpose:
    Structural representation of the current market regime.

Rules:
    - Regime representation only.
    - No trading decision.
    - No execution logic.
    - No prediction.
    - No order generation.
    - No V7+ dependency.
    - Regime state remains explicitly classified.
    - Does not mutate source data.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Optional


MARKET_REGIME_SCHEMA_VERSION = "1.0.0"
MARKET_REGIME_SCHEMA = "V6_MARKET_REGIME"


@dataclass(frozen=True)
class MarketRegime:
    """
    Immutable structural representation of a market regime.

    A regime describes the currently classified market environment.
    It does not determine what action should be taken.
    """

    # ------------------------------------------------------------------
    # Regime Identity
    # ------------------------------------------------------------------

    regime_id: Optional[str] = None
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
    # Context Reference
    # ------------------------------------------------------------------

    context_id: Optional[str] = None
    observation_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Regime Classification
    # ------------------------------------------------------------------

    regime: Optional[str] = None
    regime_family: Optional[str] = None
    regime_state: Optional[str] = None
    regime_status: Optional[str] = None

    # ------------------------------------------------------------------
    # Structural Regime Attributes
    # ------------------------------------------------------------------

    trend_state: Optional[str] = None
    volatility_state: Optional[str] = None
    liquidity_state: Optional[str] = None
    participation_state: Optional[str] = None
    momentum_state: Optional[str] = None
    market_structure_state: Optional[str] = None

    # ------------------------------------------------------------------
    # Classification Metadata
    # ------------------------------------------------------------------

    confidence: Optional[float] = None
    stability: Optional[float] = None

    # ------------------------------------------------------------------
    # Provenance
    # ------------------------------------------------------------------

    source: Optional[str] = None
    source_type: Optional[str] = None

    # ------------------------------------------------------------------
    # Explicit Field Classification
    # ------------------------------------------------------------------

    observed_fields: tuple[str, ...] = field(default_factory=tuple)
    derived_fields: tuple[str, ...] = field(default_factory=tuple)

    # ------------------------------------------------------------------
    # Additional Metadata
    # ------------------------------------------------------------------

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate structural regime information."""

        if self.sequence is not None:
            if isinstance(self.sequence, bool):
                raise TypeError(
                    "MarketRegime.sequence must be an integer or None."
                )

            if not isinstance(self.sequence, int):
                raise TypeError(
                    "MarketRegime.sequence must be an integer or None."
                )

            if self.sequence < 0:
                raise ValueError(
                    "MarketRegime.sequence cannot be negative."
                )

        for field_name in (
            "confidence",
            "stability",
        ):
            value = getattr(self, field_name)

            if value is None:
                continue

            if isinstance(value, bool):
                raise TypeError(
                    f"MarketRegime.{field_name} must be numeric or None."
                )

            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"MarketRegime.{field_name} must be numeric or None."
                )

            if not 0 <= value <= 100:
                raise ValueError(
                    f"MarketRegime.{field_name} must be between 0 and 100."
                )

        if self.metadata is None:
            raise TypeError(
                "MarketRegime.metadata must be a mapping."
            )

        if not isinstance(self.metadata, Mapping):
            raise TypeError(
                "MarketRegime.metadata must be a mapping."
            )

        if isinstance(self.observed_fields, str):
            raise TypeError(
                "MarketRegime.observed_fields must be a sequence of names."
            )

        if isinstance(self.derived_fields, str):
            raise TypeError(
                "MarketRegime.derived_fields must be a sequence of names."
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

    def has_regime_identity(self) -> bool:
        """Return True when regime ID or timestamp exists."""

        return bool(
            self.regime_id
            or self.timestamp
        )

    # ------------------------------------------------------------------
    # Classification Availability
    # ------------------------------------------------------------------

    def has_regime(self) -> bool:
        """Return True when a regime classification exists."""

        return bool(self.regime)

    def has_regime_family(self) -> bool:
        """Return True when a regime family exists."""

        return bool(self.regime_family)

    def has_regime_state(self) -> bool:
        """Return True when a regime state exists."""

        return bool(self.regime_state)

    def has_structural_context(self) -> bool:
        """Return True when at least one structural regime attribute exists."""

        return any(
            value is not None
            for value in (
                self.trend_state,
                self.volatility_state,
                self.liquidity_state,
                self.participation_state,
                self.momentum_state,
                self.market_structure_state,
            )
        )

    # ------------------------------------------------------------------
    # References
    # ------------------------------------------------------------------

    def has_context_reference(self) -> bool:
        """Return True when context or observation reference exists."""

        return bool(
            self.context_id
            or self.observation_id
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
        Return structural regime issues.

        Validation only. No trading decision is produced.
        """

        issues: list[str] = []

        if not self.has_identity():
            issues.append("MISSING_MARKET_IDENTITY")

        if not self.timestamp:
            issues.append("MISSING_TIMESTAMP")

        if not self.source:
            issues.append("MISSING_SOURCE")

        if not self.has_regime():
            issues.append("MISSING_REGIME")

        if (
            not self.has_regime_family()
            and not self.has_regime_state()
            and not self.has_structural_context()
        ):
            issues.append("EMPTY_REGIME_CONTEXT")

        if not self.has_context_reference():
            issues.append("MISSING_CONTEXT_REFERENCE")

        if self.derived_fields and not self.has_context_reference():
            issues.append(
                "DERIVED_REGIME_WITHOUT_CONTEXT_REFERENCE"
            )

        return tuple(issues)

    def is_structurally_valid(self) -> bool:
        """Return True when no structural issues are present."""

        return not self.issue_flags()

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize regime into a JSON-safe mapping."""

        data = asdict(self)

        data["observed_fields"] = list(self.observed_fields)
        data["derived_fields"] = list(self.derived_fields)
        data["metadata"] = dict(self.metadata)

        return data

    @staticmethod
    def schema_info() -> dict[str, str]:
        """Return schema identity and version."""

        return {
            "schema": MARKET_REGIME_SCHEMA,
            "version": MARKET_REGIME_SCHEMA_VERSION,
        }


def market_regime_health() -> dict[str, Any]:
    """Return structural health information for the V6 regime schema."""

    return {
        "schema": MARKET_REGIME_SCHEMA,
        "version": MARKET_REGIME_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "market_identity_supported": True,
        "regime_classification_supported": True,
        "regime_family_supported": True,
        "regime_state_supported": True,
        "trend_state_supported": True,
        "volatility_state_supported": True,
        "liquidity_state_supported": True,
        "participation_state_supported": True,
        "momentum_state_supported": True,
        "market_structure_state_supported": True,
        "confidence_supported": True,
        "stability_supported": True,
        "provenance_supported": True,
        "observed_derived_separation": True,
        "decision_logic": False,
        "execution_logic": False,
        "prediction_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_REGIME_SCHEMA_VERSION",
    "MARKET_REGIME_SCHEMA",
    "MarketRegime",
    "market_regime_health",
]