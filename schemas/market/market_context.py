"""
ROBOMLM PLUS
V6 Market Context Schema

Purpose:
    Structural container for contextual market information built from
    observed market data.

Rules:
    - Context representation only.
    - No trading decisions.
    - No execution logic.
    - No intelligence generation.
    - No prediction.
    - No V7+ dependency.
    - Observed data and derived context remain distinguishable.
    - Does not mutate source data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional


MARKET_CONTEXT_SCHEMA_VERSION = "1.0.0"
MARKET_CONTEXT_SCHEMA = "V6_MARKET_CONTEXT"


@dataclass(frozen=True)
class MarketContext:
    """
    Immutable structural representation of market context.

    The object may contain observed references and explicitly labelled
    derived/contextual fields, but it does not itself make decisions.
    """

    # ------------------------------------------------------------------
    # Context Identity
    # ------------------------------------------------------------------

    context_id: Optional[str] = None
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
    # Source Observation Reference
    # ------------------------------------------------------------------

    observation_id: Optional[str] = None
    source: Optional[str] = None
    source_type: Optional[str] = None

    # ------------------------------------------------------------------
    # Explicit Context Fields
    #
    # These are descriptive/contextual values only.
    # They are NOT trading decisions or predictions.
    # ------------------------------------------------------------------

    timeframe: Optional[str] = None
    session: Optional[str] = None
    phase: Optional[str] = None
    trend_context: Optional[str] = None
    participation_context: Optional[str] = None
    liquidity_context: Optional[str] = None
    volatility_context: Optional[str] = None

    # ------------------------------------------------------------------
    # Context Metrics
    # ------------------------------------------------------------------

    context_score: Optional[float] = None
    data_quality_score: Optional[float] = None

    # ------------------------------------------------------------------
    # Provenance / Classification
    # ------------------------------------------------------------------

    observed_fields: tuple[str, ...] = field(default_factory=tuple)
    derived_fields: tuple[str, ...] = field(default_factory=tuple)

    # ------------------------------------------------------------------
    # Additional Context Metadata
    # ------------------------------------------------------------------

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate and normalize structural context information."""

        if self.sequence is not None:
            if isinstance(self.sequence, bool):
                raise TypeError(
                    "MarketContext.sequence must be an integer or None."
                )

            if not isinstance(self.sequence, int):
                raise TypeError(
                    "MarketContext.sequence must be an integer or None."
                )

            if self.sequence < 0:
                raise ValueError(
                    "MarketContext.sequence cannot be negative."
                )

        for field_name in (
            "context_score",
            "data_quality_score",
        ):
            value = getattr(self, field_name)

            if value is None:
                continue

            if isinstance(value, bool):
                raise TypeError(
                    f"MarketContext.{field_name} must be numeric or None."
                )

            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"MarketContext.{field_name} must be numeric or None."
                )

        if self.context_score is not None:
            if not 0 <= self.context_score <= 100:
                raise ValueError(
                    "MarketContext.context_score must be between 0 and 100."
                )

        if self.data_quality_score is not None:
            if not 0 <= self.data_quality_score <= 100:
                raise ValueError(
                    "MarketContext.data_quality_score "
                    "must be between 0 and 100."
                )

        if self.metadata is None:
            raise TypeError(
                "MarketContext.metadata must be a mapping."
            )

        if not isinstance(self.metadata, Mapping):
            raise TypeError(
                "MarketContext.metadata must be a mapping."
            )

        if isinstance(self.observed_fields, str):
            raise TypeError(
                "MarketContext.observed_fields must be a sequence of names."
            )

        if isinstance(self.derived_fields, str):
            raise TypeError(
                "MarketContext.derived_fields must be a sequence of names."
            )

        # Normalize potentially mutable input containers into immutable
        # internal representations. This preserves the frozen contract.
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

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
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

    def has_context_identity(self) -> bool:
        """Return True when context ID or timestamp exists."""

        return bool(
            self.context_id
            or self.timestamp
        )

    # ------------------------------------------------------------------
    # Provenance
    # ------------------------------------------------------------------

    def has_observation_reference(self) -> bool:
        """Return True when this context references an observation."""

        return bool(self.observation_id)

    def observed_field_names(self) -> tuple[str, ...]:
        """Return explicitly observed field names."""

        return tuple(self.observed_fields)

    def derived_field_names(self) -> tuple[str, ...]:
        """Return explicitly derived/contextual field names."""

        return tuple(self.derived_fields)

    # ------------------------------------------------------------------
    # Context Availability
    # ------------------------------------------------------------------

    def has_time_context(self) -> bool:
        """Return True when timeframe or session information exists."""

        return bool(
            self.timeframe
            or self.session
        )

    def has_phase_context(self) -> bool:
        """Return True when a market phase is available."""

        return bool(self.phase)

    def has_participation_context(self) -> bool:
        """Return True when participation context exists."""

        return bool(self.participation_context)

    def has_liquidity_context(self) -> bool:
        """Return True when liquidity context exists."""

        return bool(self.liquidity_context)

    def has_volatility_context(self) -> bool:
        """Return True when volatility context exists."""

        return bool(self.volatility_context)

    # ------------------------------------------------------------------
    # Structural Validation
    # ------------------------------------------------------------------

    def issue_flags(self) -> tuple[str, ...]:
        """
        Return structural context issues.

        This performs validation only. It does not generate a decision.
        """

        issues: list[str] = []

        if not self.has_identity():
            issues.append("MISSING_MARKET_IDENTITY")

        if not self.timestamp:
            issues.append("MISSING_TIMESTAMP")

        if not self.source:
            issues.append("MISSING_SOURCE")

        if not self.observation_id:
            issues.append("MISSING_OBSERVATION_REFERENCE")

        if (
            self.context_score is None
            and self.data_quality_score is None
            and not self.observed_fields
            and not self.derived_fields
        ):
            issues.append("EMPTY_CONTEXT")

        if (
            self.derived_fields
            and not self.observation_id
        ):
            issues.append(
                "DERIVED_CONTEXT_WITHOUT_OBSERVATION_REFERENCE"
            )

        return tuple(issues)

    def is_structurally_valid(self) -> bool:
        """Return True when no structural issues are present."""

        return not self.issue_flags()

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize context into a JSON-safe mapping."""

        return {
            "context_id": self.context_id,
            "timestamp": self.timestamp,
            "sequence": self.sequence,
            "market": self.market,
            "instrument": self.instrument,
            "symbol": self.symbol,
            "exchange": self.exchange,
            "venue": self.venue,
            "contract": self.contract,
            "expiry": self.expiry,
            "observation_id": self.observation_id,
            "source": self.source,
            "source_type": self.source_type,
            "timeframe": self.timeframe,
            "session": self.session,
            "phase": self.phase,
            "trend_context": self.trend_context,
            "participation_context": self.participation_context,
            "liquidity_context": self.liquidity_context,
            "volatility_context": self.volatility_context,
            "context_score": self.context_score,
            "data_quality_score": self.data_quality_score,
            "observed_fields": list(self.observed_fields),
            "derived_fields": list(self.derived_fields),
            "metadata": dict(self.metadata),
        }

    @staticmethod
    def schema_info() -> dict[str, str]:
        """Return schema identity and version."""

        return {
            "schema": MARKET_CONTEXT_SCHEMA,
            "version": MARKET_CONTEXT_SCHEMA_VERSION,
        }


def market_context_health() -> dict[str, Any]:
    """Return structural health information for the V6 context schema."""

    return {
        "schema": MARKET_CONTEXT_SCHEMA,
        "version": MARKET_CONTEXT_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "market_identity_supported": True,
        "observation_reference_supported": True,
        "time_context_supported": True,
        "phase_context_supported": True,
        "participation_context_supported": True,
        "liquidity_context_supported": True,
        "volatility_context_supported": True,
        "provenance_supported": True,
        "observed_derived_separation": True,
        "decision_logic": False,
        "execution_logic": False,
        "prediction_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_CONTEXT_SCHEMA_VERSION",
    "MARKET_CONTEXT_SCHEMA",
    "MarketContext",
    "market_context_health",
]


