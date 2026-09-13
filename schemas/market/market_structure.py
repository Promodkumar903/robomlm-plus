"""
ROBOMLM PLUS
V6 Market Structure Schema

Purpose:
    Structural representation of observed and derived market structure.

Rules:
    - Structure representation only.
    - No trading decision.
    - No execution logic.
    - No prediction.
    - No order generation.
    - No V7+ dependency.
    - Observed and derived information remain distinguishable.
    - Does not mutate source data.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Optional


MARKET_STRUCTURE_SCHEMA_VERSION = "1.0.0"
MARKET_STRUCTURE_SCHEMA = "V6_MARKET_STRUCTURE"


@dataclass(frozen=True)
class MarketStructure:
    """
    Immutable structural representation of market structure.

    This schema describes structural conditions such as swing points,
    structural direction and reference levels. It does not determine
    whether a trade should be taken.
    """

    # ------------------------------------------------------------------
    # Structure Identity
    # ------------------------------------------------------------------

    structure_id: Optional[str] = None
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

    # ------------------------------------------------------------------
    # Structural Classification
    # ------------------------------------------------------------------

    structure_state: Optional[str] = None
    structure_direction: Optional[str] = None
    structure_phase: Optional[str] = None

    # ------------------------------------------------------------------
    # Swing / Extremum References
    # ------------------------------------------------------------------

    last_swing_high: Optional[float] = None
    last_swing_low: Optional[float] = None
    previous_swing_high: Optional[float] = None
    previous_swing_low: Optional[float] = None

    # ------------------------------------------------------------------
    # Structural Reference Levels
    # ------------------------------------------------------------------

    support_level: Optional[float] = None
    resistance_level: Optional[float] = None
    structural_high: Optional[float] = None
    structural_low: Optional[float] = None

    # ------------------------------------------------------------------
    # Structural Events / States
    # ------------------------------------------------------------------

    break_state: Optional[str] = None
    displacement_state: Optional[str] = None
    compression_state: Optional[str] = None

    # ------------------------------------------------------------------
    # Classification Metrics
    # ------------------------------------------------------------------

    confidence: Optional[float] = None
    strength: Optional[float] = None

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
        """Validate structural market structure information."""

        if self.sequence is not None:
            if isinstance(self.sequence, bool):
                raise TypeError(
                    "MarketStructure.sequence must be an integer or None."
                )

            if not isinstance(self.sequence, int):
                raise TypeError(
                    "MarketStructure.sequence must be an integer or None."
                )

            if self.sequence < 0:
                raise ValueError(
                    "MarketStructure.sequence cannot be negative."
                )

        numeric_fields = {
            "last_swing_high": self.last_swing_high,
            "last_swing_low": self.last_swing_low,
            "previous_swing_high": self.previous_swing_high,
            "previous_swing_low": self.previous_swing_low,
            "support_level": self.support_level,
            "resistance_level": self.resistance_level,
            "structural_high": self.structural_high,
            "structural_low": self.structural_low,
            "confidence": self.confidence,
            "strength": self.strength,
        }

        for field_name, value in numeric_fields.items():
            if value is None:
                continue

            if isinstance(value, bool):
                raise TypeError(
                    f"MarketStructure.{field_name} must be numeric or None."
                )

            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"MarketStructure.{field_name} must be numeric or None."
                )

        for field_name in ("confidence", "strength"):
            value = getattr(self, field_name)

            if value is not None and not 0 <= value <= 100:
                raise ValueError(
                    f"MarketStructure.{field_name} must be between 0 and 100."
                )

        if self.metadata is None:
            raise TypeError(
                "MarketStructure.metadata must be a mapping."
            )

        if not isinstance(self.metadata, Mapping):
            raise TypeError(
                "MarketStructure.metadata must be a mapping."
            )

        if isinstance(self.observed_fields, str):
            raise TypeError(
                "MarketStructure.observed_fields must be a sequence of names."
            )

        if isinstance(self.derived_fields, str):
            raise TypeError(
                "MarketStructure.derived_fields must be a sequence of names."
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

    def has_structure_identity(self) -> bool:
        """Return True when structure ID or timestamp exists."""

        return bool(
            self.structure_id
            or self.timestamp
        )

    # ------------------------------------------------------------------
    # Reference Availability
    # ------------------------------------------------------------------

    def has_observation_reference(self) -> bool:
        """Return True when an observation reference exists."""

        return bool(self.observation_id)

    def has_context_reference(self) -> bool:
        """Return True when a context reference exists."""

        return bool(self.context_id)

    def has_regime_reference(self) -> bool:
        """Return True when a regime reference exists."""

        return bool(self.regime_id)

    # ------------------------------------------------------------------
    # Swing Structure
    # ------------------------------------------------------------------

    def has_swing_high(self) -> bool:
        """Return True when a latest swing high exists."""

        return self.last_swing_high is not None

    def has_swing_low(self) -> bool:
        """Return True when a latest swing low exists."""

        return self.last_swing_low is not None

    def has_swing_structure(self) -> bool:
        """Return True when at least one swing reference exists."""

        return (
            self.last_swing_high is not None
            or self.last_swing_low is not None
            or self.previous_swing_high is not None
            or self.previous_swing_low is not None
        )

    # ------------------------------------------------------------------
    # Structural Levels
    # ------------------------------------------------------------------

    def has_support(self) -> bool:
        """Return True when a support reference exists."""

        return self.support_level is not None

    def has_resistance(self) -> bool:
        """Return True when a resistance reference exists."""

        return self.resistance_level is not None

    def has_structural_range(self) -> bool:
        """Return True when both structural high and low exist."""

        return (
            self.structural_high is not None
            and self.structural_low is not None
        )

    # ------------------------------------------------------------------
    # Structural Validation
    # ------------------------------------------------------------------

    def issue_flags(self) -> tuple[str, ...]:
        """
        Return structural validation issues.

        This method validates the schema only.
        """

        issues: list[str] = []

        if not self.has_identity():
            issues.append("MISSING_MARKET_IDENTITY")

        if not self.timestamp:
            issues.append("MISSING_TIMESTAMP")

        if not self.source:
            issues.append("MISSING_SOURCE")

        if not self.structure_state:
            issues.append("MISSING_STRUCTURE_STATE")

        if not self.has_swing_structure():
            issues.append("MISSING_SWING_STRUCTURE")

        if (
            self.structural_high is not None
            and self.structural_low is not None
            and self.structural_high < self.structural_low
        ):
            issues.append("INVALID_STRUCTURAL_RANGE")

        if (
            self.support_level is not None
            and self.resistance_level is not None
            and self.support_level > self.resistance_level
        ):
            issues.append("INVALID_SUPPORT_RESISTANCE_RELATION")

        if (
            self.derived_fields
            and not (
                self.observation_id
                or self.context_id
                or self.regime_id
            )
        ):
            issues.append(
                "DERIVED_STRUCTURE_WITHOUT_SOURCE_REFERENCE"
            )

        return tuple(issues)

    def is_structurally_valid(self) -> bool:
        """Return True when no structural issues are present."""

        return not self.issue_flags()

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize structure into a JSON-safe mapping."""

        data = asdict(self)

        data["observed_fields"] = list(self.observed_fields)
        data["derived_fields"] = list(self.derived_fields)
        data["metadata"] = dict(self.metadata)

        return data

    @staticmethod
    def schema_info() -> dict[str, str]:
        """Return schema identity and version."""

        return {
            "schema": MARKET_STRUCTURE_SCHEMA,
            "version": MARKET_STRUCTURE_SCHEMA_VERSION,
        }


def market_structure_health() -> dict[str, Any]:
    """Return structural health information for the V6 structure schema."""

    return {
        "schema": MARKET_STRUCTURE_SCHEMA,
        "version": MARKET_STRUCTURE_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "market_identity_supported": True,
        "observation_reference_supported": True,
        "context_reference_supported": True,
        "regime_reference_supported": True,
        "swing_structure_supported": True,
        "support_resistance_supported": True,
        "structural_range_supported": True,
        "break_state_supported": True,
        "displacement_state_supported": True,
        "compression_state_supported": True,
        "provenance_supported": True,
        "observed_derived_separation": True,
        "decision_logic": False,
        "execution_logic": False,
        "prediction_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_STRUCTURE_SCHEMA_VERSION",
    "MARKET_STRUCTURE_SCHEMA",
    "MarketStructure",
    "market_structure_health",
]