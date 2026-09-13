"""
ROBOMLM PLUS
V6 Market Relationship Schema

Purpose:
    Structural representation of relationships between markets,
    instruments, contracts, or other market entities.

Rules:
    - Relationship representation only.
    - No trading decisions.
    - No execution logic.
    - No intelligence generation.
    - No V7+ dependency.
    - Does not mutate source objects.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Optional


MARKET_RELATIONSHIP_SCHEMA_VERSION = "1.0.0"
MARKET_RELATIONSHIP_SCHEMA = "V6_MARKET_RELATIONSHIP"


@dataclass(frozen=True)
class MarketRelationship:
    """
    Immutable structural representation of a relationship between
    two market entities.

    The relationship type and strength are supplied by an upstream
    source; this schema does not calculate or infer them.
    """

    # ------------------------------------------------------------------
    # Relationship Identity
    # ------------------------------------------------------------------

    relationship_id: Optional[str] = None
    relationship_type: Optional[str] = None

    # ------------------------------------------------------------------
    # Source Entity
    # ------------------------------------------------------------------

    source_market: Optional[str] = None
    source_instrument: Optional[str] = None
    source_symbol: Optional[str] = None
    source_exchange: Optional[str] = None
    source_venue: Optional[str] = None

    # ------------------------------------------------------------------
    # Target Entity
    # ------------------------------------------------------------------

    target_market: Optional[str] = None
    target_instrument: Optional[str] = None
    target_symbol: Optional[str] = None
    target_exchange: Optional[str] = None
    target_venue: Optional[str] = None

    # ------------------------------------------------------------------
    # Relationship State
    # ------------------------------------------------------------------

    relationship_strength: Optional[float] = None
    relationship_direction: Optional[str] = None
    relationship_source: Optional[str] = None

    # ------------------------------------------------------------------
    # Timing / Provenance
    # ------------------------------------------------------------------

    timestamp: Optional[str] = None
    source: Optional[str] = None
    source_type: Optional[str] = None

    # ------------------------------------------------------------------
    # Additional Metadata
    # ------------------------------------------------------------------

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate structural relationship information."""

        if self.relationship_strength is not None:
            if isinstance(self.relationship_strength, bool):
                raise TypeError(
                    "MarketRelationship.relationship_strength "
                    "must be numeric or None."
                )

            if not isinstance(
                self.relationship_strength,
                (int, float),
            ):
                raise TypeError(
                    "MarketRelationship.relationship_strength "
                    "must be numeric or None."
                )

            if not -100 <= self.relationship_strength <= 100:
                raise ValueError(
                    "MarketRelationship.relationship_strength "
                    "must be between -100 and 100."
                )

        if self.metadata is None:
            raise TypeError(
                "MarketRelationship.metadata must be a mapping."
            )

        if not isinstance(self.metadata, Mapping):
            raise TypeError(
                "MarketRelationship.metadata must be a mapping."
            )

    # ------------------------------------------------------------------
    # Entity Checks
    # ------------------------------------------------------------------

    def has_source_entity(self) -> bool:
        """Return True when source-entity identity is available."""

        return bool(
            self.source_market
            or self.source_instrument
            or self.source_symbol
        )

    def has_target_entity(self) -> bool:
        """Return True when target-entity identity is available."""

        return bool(
            self.target_market
            or self.target_instrument
            or self.target_symbol
        )

    def has_both_entities(self) -> bool:
        """Return True when both relationship entities are identified."""

        return (
            self.has_source_entity()
            and self.has_target_entity()
        )

    def has_relationship_type(self) -> bool:
        """Return True when a relationship type is available."""

        return bool(
            self.relationship_type
            and self.relationship_type.strip()
        )

    def has_strength(self) -> bool:
        """Return True when relationship strength is available."""

        return self.relationship_strength is not None

    # ------------------------------------------------------------------
    # Direction Checks
    # ------------------------------------------------------------------

    def is_positive(self) -> bool:
        """
        Return True when the recorded relationship strength is positive.
        """

        return (
            self.relationship_strength is not None
            and self.relationship_strength > 0
        )

    def is_negative(self) -> bool:
        """
        Return True when the recorded relationship strength is negative.
        """

        return (
            self.relationship_strength is not None
            and self.relationship_strength < 0
        )

    def is_neutral(self) -> bool:
        """
        Return True when the recorded relationship strength is zero.
        """

        return (
            self.relationship_strength is not None
            and self.relationship_strength == 0
        )

    # ------------------------------------------------------------------
    # Structural Checks
    # ------------------------------------------------------------------

    def issue_flags(self) -> tuple[str, ...]:
        """
        Return structural relationship issues.

        No trading or intelligence decision is made here.
        """

        issues: list[str] = []

        if not self.has_source_entity():
            issues.append("MISSING_SOURCE_ENTITY")

        if not self.has_target_entity():
            issues.append("MISSING_TARGET_ENTITY")

        if not self.has_relationship_type():
            issues.append("MISSING_RELATIONSHIP_TYPE")

        if not self.timestamp:
            issues.append("MISSING_TIMESTAMP")

        return tuple(issues)

    # ------------------------------------------------------------------
    # Identity Key
    # ------------------------------------------------------------------

    def relationship_key(self) -> str:
        """
        Build a deterministic relationship identity key.
        """

        source = (
            self.source_symbol
            or self.source_instrument
            or self.source_market
            or ""
        )

        target = (
            self.target_symbol
            or self.target_instrument
            or self.target_market
            or ""
        )

        relationship = self.relationship_type or ""

        return (
            f"{source.strip()}|"
            f"{relationship.strip()}|"
            f"{target.strip()}"
        )

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize relationship into a JSON-safe mapping."""

        data = asdict(self)
        data["metadata"] = dict(self.metadata)

        return data

    @staticmethod
    def schema_info() -> dict[str, str]:
        """Return schema identity and version."""

        return {
            "schema": MARKET_RELATIONSHIP_SCHEMA,
            "version": MARKET_RELATIONSHIP_SCHEMA_VERSION,
        }


def market_relationship_health() -> dict[str, Any]:
    """Return structural health information for the V6 relationship schema."""

    return {
        "schema": MARKET_RELATIONSHIP_SCHEMA,
        "version": MARKET_RELATIONSHIP_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "source_entity_supported": True,
        "target_entity_supported": True,
        "relationship_type_supported": True,
        "relationship_strength_supported": True,
        "decision_logic": False,
        "execution_logic": False,
        "intelligence_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_RELATIONSHIP_SCHEMA_VERSION",
    "MARKET_RELATIONSHIP_SCHEMA",
    "MarketRelationship",
    "market_relationship_health",
]