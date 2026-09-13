"""
ROBOMLM PLUS
V6 Market Participation Schema

Purpose:
    Structural representation of market participation information.

Rules:
    - Participation representation only.
    - No trading decision.
    - No execution logic.
    - No order generation.
    - No prediction.
    - No V7+ dependency.
    - Activity and volume remain distinct concepts.
    - Observed and derived information remain distinguishable.
    - Does not mutate source data.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Optional


MARKET_PARTICIPATION_SCHEMA_VERSION = "1.0.0"
MARKET_PARTICIPATION_SCHEMA = "V6_MARKET_PARTICIPATION"


@dataclass(frozen=True)
class MarketParticipation:
    """
    Immutable structural representation of market participation.

    Participation describes measurable activity and involvement in a
    market. It does not determine trade direction or execution.
    """

    # ------------------------------------------------------------------
    # Participation Identity
    # ------------------------------------------------------------------

    participation_id: Optional[str] = None
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
    # Observed Participation Measures
    # ------------------------------------------------------------------

    volume: Optional[float] = None
    trade_count: Optional[int] = None
    buy_volume: Optional[float] = None
    sell_volume: Optional[float] = None
    open_interest: Optional[float] = None

    # ------------------------------------------------------------------
    # Activity Measures
    # ------------------------------------------------------------------

    activity_count: Optional[int] = None
    activity_rate: Optional[float] = None
    participation_rate: Optional[float] = None

    # ------------------------------------------------------------------
    # Derived Participation Measures
    # ------------------------------------------------------------------

    volume_delta: Optional[float] = None
    buy_sell_ratio: Optional[float] = None
    participation_balance: Optional[float] = None

    # ------------------------------------------------------------------
    # Participation Classification
    # ------------------------------------------------------------------

    participation_state: Optional[str] = None
    participation_level: Optional[str] = None
    activity_state: Optional[str] = None
    volume_state: Optional[str] = None

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    participation_score: Optional[float] = None
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
        """Validate structural participation information."""

        if self.sequence is not None:
            if isinstance(self.sequence, bool):
                raise TypeError(
                    "MarketParticipation.sequence "
                    "must be an integer or None."
                )

            if not isinstance(self.sequence, int):
                raise TypeError(
                    "MarketParticipation.sequence "
                    "must be an integer or None."
                )

            if self.sequence < 0:
                raise ValueError(
                    "MarketParticipation.sequence cannot be negative."
                )

        integer_fields = {
            "trade_count": self.trade_count,
            "activity_count": self.activity_count,
        }

        for field_name, value in integer_fields.items():
            if value is None:
                continue

            if isinstance(value, bool):
                raise TypeError(
                    f"MarketParticipation.{field_name} "
                    "must be an integer or None."
                )

            if not isinstance(value, int):
                raise TypeError(
                    f"MarketParticipation.{field_name} "
                    "must be an integer or None."
                )

            if value < 0:
                raise ValueError(
                    f"MarketParticipation.{field_name} "
                    "cannot be negative."
                )

        numeric_fields = {
            "volume": self.volume,
            "buy_volume": self.buy_volume,
            "sell_volume": self.sell_volume,
            "open_interest": self.open_interest,
            "activity_rate": self.activity_rate,
            "participation_rate": self.participation_rate,
            "volume_delta": self.volume_delta,
            "buy_sell_ratio": self.buy_sell_ratio,
            "participation_balance": self.participation_balance,
            "participation_score": self.participation_score,
            "confidence": self.confidence,
        }

        for field_name, value in numeric_fields.items():
            if value is None:
                continue

            if isinstance(value, bool):
                raise TypeError(
                    f"MarketParticipation.{field_name} "
                    "must be numeric or None."
                )

            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"MarketParticipation.{field_name} "
                    "must be numeric or None."
                )

        for field_name in (
            "volume",
            "buy_volume",
            "sell_volume",
            "open_interest",
        ):
            value = getattr(self, field_name)

            if value is not None and value < 0:
                raise ValueError(
                    f"MarketParticipation.{field_name} "
                    "cannot be negative."
                )

        for field_name in (
            "activity_rate",
            "participation_rate",
            "participation_score",
            "confidence",
        ):
            value = getattr(self, field_name)

            if value is not None and not 0 <= value <= 100:
                raise ValueError(
                    f"MarketParticipation.{field_name} "
                    "must be between 0 and 100."
                )

        if self.participation_balance is not None:
            if not -1 <= self.participation_balance <= 1:
                raise ValueError(
                    "MarketParticipation.participation_balance "
                    "must be between -1 and 1."
                )

        if self.metadata is None:
            raise TypeError(
                "MarketParticipation.metadata must be a mapping."
            )

        if not isinstance(self.metadata, Mapping):
            raise TypeError(
                "MarketParticipation.metadata must be a mapping."
            )

        if isinstance(self.observed_fields, str):
            raise TypeError(
                "MarketParticipation.observed_fields "
                "must be a sequence of names."
            )

        if isinstance(self.derived_fields, str):
            raise TypeError(
                "MarketParticipation.derived_fields "
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

    def has_participation_identity(self) -> bool:
        """Return True when participation ID or timestamp exists."""

        return bool(
            self.participation_id
            or self.timestamp
        )

    # ------------------------------------------------------------------
    # Volume
    # ------------------------------------------------------------------

    def has_volume(self) -> bool:
        """Return True when total volume is available."""

        return self.volume is not None

    def has_buy_sell_volume(self) -> bool:
        """Return True when both buy and sell volume are available."""

        return (
            self.buy_volume is not None
            and self.sell_volume is not None
        )

    def calculate_volume_delta(self) -> Optional[float]:
        """
        Calculate buy volume minus sell volume.

        This is a structural calculation only.
        """

        if not self.has_buy_sell_volume():
            return None

        return self.buy_volume - self.sell_volume

    def calculate_buy_sell_ratio(self) -> Optional[float]:
        """
        Calculate buy-volume to sell-volume ratio.

        Returns None when sell volume is unavailable or zero.
        """

        if self.buy_volume is None or self.sell_volume is None:
            return None

        if self.sell_volume == 0:
            return None

        return self.buy_volume / self.sell_volume

    # ------------------------------------------------------------------
    # Activity
    # ------------------------------------------------------------------

    def has_activity(self) -> bool:
        """Return True when activity count or rate exists."""

        return (
            self.activity_count is not None
            or self.activity_rate is not None
        )

    def has_trade_count(self) -> bool:
        """Return True when trade count is available."""

        return self.trade_count is not None

    # ------------------------------------------------------------------
    # Participation
    # ------------------------------------------------------------------

    def has_participation_rate(self) -> bool:
        """Return True when participation rate is available."""

        return self.participation_rate is not None

    def has_open_interest(self) -> bool:
        """Return True when open interest is available."""

        return self.open_interest is not None

    def has_participation_measure(self) -> bool:
        """Return True when at least one participation measure exists."""

        return any(
            value is not None
            for value in (
                self.volume,
                self.trade_count,
                self.buy_volume,
                self.sell_volume,
                self.open_interest,
                self.activity_count,
                self.activity_rate,
                self.participation_rate,
            )
        )

    # ------------------------------------------------------------------
    # Source References
    # ------------------------------------------------------------------

    def has_source_reference(self) -> bool:
        """Return True when an upstream reference exists."""

        return bool(
            self.observation_id
            or self.context_id
            or self.regime_id
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
        Return structural participation issues.

        Validation only. No trading decision is produced.
        """

        issues: list[str] = []

        if not self.has_identity():
            issues.append("MISSING_MARKET_IDENTITY")

        if not self.timestamp:
            issues.append("MISSING_TIMESTAMP")

        if not self.source:
            issues.append("MISSING_SOURCE")

        if not self.has_participation_measure():
            issues.append("MISSING_PARTICIPATION_MEASURE")

        if not self.has_source_reference():
            issues.append("MISSING_SOURCE_REFERENCE")

        if (
            self.buy_volume is not None
            and self.sell_volume is not None
            and self.volume is not None
            and self.buy_volume + self.sell_volume > self.volume
        ):
            issues.append(
                "BUY_SELL_VOLUME_EXCEEDS_TOTAL_VOLUME"
            )

        if (
            self.derived_fields
            and not self.has_source_reference()
        ):
            issues.append(
                "DERIVED_PARTICIPATION_WITHOUT_SOURCE_REFERENCE"
            )

        return tuple(issues)

    def is_structurally_valid(self) -> bool:
        """Return True when no structural issues are present."""

        return not self.issue_flags()

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize participation into a JSON-safe mapping."""

        data = asdict(self)

        data["observed_fields"] = list(self.observed_fields)
        data["derived_fields"] = list(self.derived_fields)
        data["metadata"] = dict(self.metadata)

        return data

    @staticmethod
    def schema_info() -> dict[str, str]:
        """Return schema identity and version."""

        return {
            "schema": MARKET_PARTICIPATION_SCHEMA,
            "version": MARKET_PARTICIPATION_SCHEMA_VERSION,
        }


def market_participation_health() -> dict[str, Any]:
    """Return structural health information for the V6 participation schema."""

    return {
        "schema": MARKET_PARTICIPATION_SCHEMA,
        "version": MARKET_PARTICIPATION_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "market_identity_supported": True,
        "volume_supported": True,
        "buy_sell_volume_supported": True,
        "trade_count_supported": True,
        "activity_supported": True,
        "participation_rate_supported": True,
        "open_interest_supported": True,
        "volume_delta_supported": True,
        "buy_sell_ratio_supported": True,
        "participation_balance_supported": True,
        "classification_supported": True,
        "provenance_supported": True,
        "source_reference_supported": True,
        "observed_derived_separation": True,
        "activity_volume_separation": True,
        "decision_logic": False,
        "execution_logic": False,
        "order_generation": False,
        "prediction_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_PARTICIPATION_SCHEMA_VERSION",
    "MARKET_PARTICIPATION_SCHEMA",
    "MarketParticipation",
    "market_participation_health",
]