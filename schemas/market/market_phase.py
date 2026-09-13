"""
ROBOMLM PLUS
V6 Market Phase Schema

Purpose:
    Structural representation of the current market phase/state.

Rules:
    - Phase representation only.
    - No trading decisions.
    - No execution logic.
    - No intelligence generation.
    - No V7+ dependency.
    - Phase labels may be observed or derived, but this schema does not
      calculate or infer them.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Optional


MARKET_PHASE_SCHEMA_VERSION = "1.0.0"
MARKET_PHASE_SCHEMA = "V6_MARKET_PHASE"


@dataclass(frozen=True)
class MarketPhase:
    """
    Immutable structural representation of a market phase.

    `phase` stores the phase label supplied by an upstream source.
    `phase_source` explicitly identifies whether that label is observed
    or derived.
    """

    # ------------------------------------------------------------------
    # Phase Identity
    # ------------------------------------------------------------------

    phase: Optional[str] = None
    phase_source: Optional[str] = None

    # ------------------------------------------------------------------
    # Timing / Session Context
    # ------------------------------------------------------------------

    timestamp: Optional[str] = None
    session_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Market Identity
    # ------------------------------------------------------------------

    market: Optional[str] = None
    instrument: Optional[str] = None
    symbol: Optional[str] = None
    exchange: Optional[str] = None
    venue: Optional[str] = None

    # ------------------------------------------------------------------
    # Phase Context
    # ------------------------------------------------------------------

    previous_phase: Optional[str] = None
    transition: Optional[str] = None
    confidence: Optional[float] = None

    # ------------------------------------------------------------------
    # Provenance
    # ------------------------------------------------------------------

    source: Optional[str] = None
    source_type: Optional[str] = None

    # ------------------------------------------------------------------
    # Additional Metadata
    # ------------------------------------------------------------------

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate structural market-phase information."""

        if self.confidence is not None:
            if isinstance(self.confidence, bool):
                raise TypeError(
                    "MarketPhase.confidence must be numeric or None."
                )

            if not isinstance(self.confidence, (int, float)):
                raise TypeError(
                    "MarketPhase.confidence must be numeric or None."
                )

            if not 0 <= self.confidence <= 100:
                raise ValueError(
                    "MarketPhase.confidence must be between 0 and 100."
                )

        if self.metadata is None:
            raise TypeError(
                "MarketPhase.metadata must be a mapping."
            )

        if not isinstance(self.metadata, Mapping):
            raise TypeError(
                "MarketPhase.metadata must be a mapping."
            )

        if self.phase_source is not None:
            allowed_sources = {
                "OBSERVED",
                "DERIVED",
                "EXTERNAL",
                "UNKNOWN",
            }

            if self.phase_source.upper() not in allowed_sources:
                raise ValueError(
                    "MarketPhase.phase_source must be one of: "
                    "OBSERVED, DERIVED, EXTERNAL, UNKNOWN."
                )

    # ------------------------------------------------------------------
    # Structural Checks
    # ------------------------------------------------------------------

    def has_phase(self) -> bool:
        """Return True when a phase label is available."""

        return bool(
            self.phase
            and self.phase.strip()
        )

    def has_market_identity(self) -> bool:
        """Return True when market/instrument identity is available."""

        return bool(
            self.market
            or self.instrument
            or self.symbol
        )

    def is_observed(self) -> bool:
        """
        Return True when the phase is explicitly marked as observed.

        This does not verify the correctness of the observation.
        """

        return (
            self.phase_source is not None
            and self.phase_source.upper() == "OBSERVED"
        )

    def is_derived(self) -> bool:
        """
        Return True when the phase is explicitly marked as derived.

        This does not perform any derivation.
        """

        return (
            self.phase_source is not None
            and self.phase_source.upper() == "DERIVED"
        )

    def has_transition(self) -> bool:
        """Return True when a phase transition is recorded."""

        return bool(
            self.transition
            and self.transition.strip()
        )

    def issue_flags(self) -> tuple[str, ...]:
        """
        Return structural phase issues.

        No trading or intelligence decision is made here.
        """

        issues: list[str] = []

        if not self.has_phase():
            issues.append("MISSING_PHASE")

        if not self.has_market_identity():
            issues.append("MISSING_MARKET_IDENTITY")

        if not self.timestamp:
            issues.append("MISSING_TIMESTAMP")

        if self.phase_source is None:
            issues.append("MISSING_PHASE_SOURCE")

        return tuple(issues)

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize market phase into a JSON-safe mapping."""

        data = asdict(self)
        data["metadata"] = dict(self.metadata)

        return data

    @staticmethod
    def schema_info() -> dict[str, str]:
        """Return schema identity and version."""

        return {
            "schema": MARKET_PHASE_SCHEMA,
            "version": MARKET_PHASE_SCHEMA_VERSION,
        }


def market_phase_health() -> dict[str, Any]:
    """Return structural health information for the V6 phase schema."""

    return {
        "schema": MARKET_PHASE_SCHEMA,
        "version": MARKET_PHASE_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "observed_phase_supported": True,
        "derived_phase_supported": True,
        "transition_supported": True,
        "decision_logic": False,
        "execution_logic": False,
        "intelligence_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_PHASE_SCHEMA_VERSION",
    "MARKET_PHASE_SCHEMA",
    "MarketPhase",
    "market_phase_health",
]