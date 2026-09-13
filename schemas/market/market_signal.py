"""
ROBOMLM PLUS
V6 Market Signal Schema

Purpose:
    Structural representation of a market-derived signal.

Rules:
    - Signal representation only.
    - No trading decision.
    - No execution logic.
    - No order generation.
    - No prediction guarantee.
    - No V7+ dependency.
    - Signal provenance must remain identifiable.
    - Observed and derived information remain distinguishable.
    - Does not mutate source data.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Optional


MARKET_SIGNAL_SCHEMA_VERSION = "1.0.0"
MARKET_SIGNAL_SCHEMA = "V6_MARKET_SIGNAL"


@dataclass(frozen=True)
class MarketSignal:
    """
    Immutable structural representation of one market signal.

    A signal describes an identified market condition or event.
    It is not itself a trade instruction.
    """

    # ------------------------------------------------------------------
    # Signal Identity
    # ------------------------------------------------------------------

    signal_id: Optional[str] = None
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
    # Signal Classification
    # ------------------------------------------------------------------

    signal_type: Optional[str] = None
    signal_family: Optional[str] = None
    signal_state: Optional[str] = None
    direction: Optional[str] = None

    # ------------------------------------------------------------------
    # Signal Description
    # ------------------------------------------------------------------

    condition: Optional[str] = None
    trigger: Optional[str] = None
    reason: Optional[str] = None

    # ------------------------------------------------------------------
    # Signal Metrics
    # ------------------------------------------------------------------

    strength: Optional[float] = None
    confidence: Optional[float] = None
    relevance: Optional[float] = None

    # ------------------------------------------------------------------
    # Signal Lifecycle
    # ------------------------------------------------------------------

    status: Optional[str] = None
    validity: Optional[str] = None

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
        """Validate structural signal information."""

        if self.sequence is not None:
            if isinstance(self.sequence, bool):
                raise TypeError(
                    "MarketSignal.sequence must be an integer or None."
                )

            if not isinstance(self.sequence, int):
                raise TypeError(
                    "MarketSignal.sequence must be an integer or None."
                )

            if self.sequence < 0:
                raise ValueError(
                    "MarketSignal.sequence cannot be negative."
                )

        numeric_fields = {
            "strength": self.strength,
            "confidence": self.confidence,
            "relevance": self.relevance,
        }

        for field_name, value in numeric_fields.items():
            if value is None:
                continue

            if isinstance(value, bool):
                raise TypeError(
                    f"MarketSignal.{field_name} must be numeric or None."
                )

            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"MarketSignal.{field_name} must be numeric or None."
                )

            if not 0 <= value <= 100:
                raise ValueError(
                    f"MarketSignal.{field_name} must be between 0 and 100."
                )

        if self.metadata is None:
            raise TypeError(
                "MarketSignal.metadata must be a mapping."
            )

        if not isinstance(self.metadata, Mapping):
            raise TypeError(
                "MarketSignal.metadata must be a mapping."
            )

        if isinstance(self.observed_fields, str):
            raise TypeError(
                "MarketSignal.observed_fields must be a sequence of names."
            )

        if isinstance(self.derived_fields, str):
            raise TypeError(
                "MarketSignal.derived_fields must be a sequence of names."
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

    def has_signal_identity(self) -> bool:
        """Return True when signal ID or timestamp exists."""

        return bool(
            self.signal_id
            or self.timestamp
        )

    # ------------------------------------------------------------------
    # Signal Classification
    # ------------------------------------------------------------------

    def has_signal_type(self) -> bool:
        """Return True when signal type exists."""

        return bool(self.signal_type)

    def has_signal_family(self) -> bool:
        """Return True when signal family exists."""

        return bool(self.signal_family)

    def has_signal_state(self) -> bool:
        """Return True when signal state exists."""

        return bool(self.signal_state)

    def has_direction(self) -> bool:
        """Return True when a structural direction is available."""

        return bool(self.direction)

    # ------------------------------------------------------------------
    # Signal Description
    # ------------------------------------------------------------------

    def has_condition(self) -> bool:
        """Return True when the signal condition is described."""

        return bool(self.condition)

    def has_trigger(self) -> bool:
        """Return True when a trigger description exists."""

        return bool(self.trigger)

    def has_reason(self) -> bool:
        """Return True when a signal reason exists."""

        return bool(self.reason)

    # ------------------------------------------------------------------
    # Source References
    # ------------------------------------------------------------------

    def has_source_reference(self) -> bool:
        """Return True when at least one source object is referenced."""

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
        Return structural signal issues.

        Validation only. No trading decision is produced.
        """

        issues: list[str] = []

        if not self.has_identity():
            issues.append("MISSING_MARKET_IDENTITY")

        if not self.timestamp:
            issues.append("MISSING_TIMESTAMP")

        if not self.source:
            issues.append("MISSING_SOURCE")

        if not self.has_signal_type():
            issues.append("MISSING_SIGNAL_TYPE")

        if not self.has_signal_state():
            issues.append("MISSING_SIGNAL_STATE")

        if not (
            self.has_condition()
            or self.has_trigger()
            or self.has_reason()
        ):
            issues.append("MISSING_SIGNAL_DESCRIPTION")

        if not self.has_source_reference():
            issues.append("MISSING_SOURCE_REFERENCE")

        if (
            self.derived_fields
            and not self.has_source_reference()
        ):
            issues.append(
                "DERIVED_SIGNAL_WITHOUT_SOURCE_REFERENCE"
            )

        return tuple(issues)

    def is_structurally_valid(self) -> bool:
        """Return True when no structural issues are present."""

        return not self.issue_flags()

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize signal into a JSON-safe mapping."""

        data = asdict(self)

        data["observed_fields"] = list(self.observed_fields)
        data["derived_fields"] = list(self.derived_fields)
        data["metadata"] = dict(self.metadata)

        return data

    @staticmethod
    def schema_info() -> dict[str, str]:
        """Return schema identity and version."""

        return {
            "schema": MARKET_SIGNAL_SCHEMA,
            "version": MARKET_SIGNAL_SCHEMA_VERSION,
        }


def market_signal_health() -> dict[str, Any]:
    """Return structural health information for the V6 signal schema."""

    return {
        "schema": MARKET_SIGNAL_SCHEMA,
        "version": MARKET_SIGNAL_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "market_identity_supported": True,
        "signal_classification_supported": True,
        "signal_family_supported": True,
        "signal_state_supported": True,
        "direction_supported": True,
        "condition_supported": True,
        "trigger_supported": True,
        "reason_supported": True,
        "strength_supported": True,
        "confidence_supported": True,
        "relevance_supported": True,
        "lifecycle_supported": True,
        "provenance_supported": True,
        "source_references_supported": True,
        "observed_derived_separation": True,
        "decision_logic": False,
        "execution_logic": False,
        "order_generation": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_SIGNAL_SCHEMA_VERSION",
    "MARKET_SIGNAL_SCHEMA",
    "MarketSignal",
    "market_signal_health",
]