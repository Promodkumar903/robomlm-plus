"""
ROBOMLM PLUS
Market Data Point Schema

Purpose:
    Immutable structural representation of one atomic market data point.

Design:
    - Represents a single timestamped market value/observation.
    - Preserves market and instrument identity.
    - Separates observed values from structural metadata.
    - Does not generate signals.
    - Does not make trading decisions.
    - Does not execute orders.
    - No V7+ dependency.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Any, Mapping, Optional


MARKET_DATA_POINT_SCHEMA_VERSION = "1.0.0"
MARKET_DATA_POINT_SCHEMA = "MARKET_DATA_POINT"


def _non_empty(value: Any) -> bool:
    return value is not None and str(value).strip() != ""


def _non_negative(value: Optional[float | int]) -> bool:
    return value is None or value >= 0


@dataclass(frozen=True)
class MarketDataPoint:
    """
    Immutable atomic market data point.

    This schema describes one market observation at one point in time.
    It is intentionally neutral: a data point may represent price,
    volume, liquidity, volatility, derivative, order-book, or another
    market-measurable field.
    """

    # ------------------------------------------------------------------
    # Data point identity
    # ------------------------------------------------------------------
    data_point_id: Optional[str] = None
    data_point_type: Optional[str] = None
    data_point_name: Optional[str] = None
    data_point_code: Optional[str] = None
    data_point_state: Optional[str] = None

    # ------------------------------------------------------------------
    # Market identity
    # ------------------------------------------------------------------
    market: Optional[str] = None
    instrument: Optional[str] = None
    symbol: Optional[str] = None
    exchange: Optional[str] = None
    venue: Optional[str] = None
    contract: Optional[str] = None
    expiry: Optional[date] = None

    # ------------------------------------------------------------------
    # Temporal identity
    # ------------------------------------------------------------------
    timestamp: Optional[datetime] = None
    timezone: Optional[str] = None

    trading_date: Optional[date] = None
    session_id: Optional[str] = None
    calendar_id: Optional[str] = None
    schedule_id: Optional[str] = None

    timeframe_id: Optional[str] = None
    interval_id: Optional[str] = None
    window_id: Optional[str] = None

    sequence: Optional[int] = None

    # ------------------------------------------------------------------
    # Measurement identity
    # ------------------------------------------------------------------
    field_name: Optional[str] = None
    field_code: Optional[str] = None
    measurement_type: Optional[str] = None
    measurement_unit: Optional[str] = None

    # ------------------------------------------------------------------
    # Measurement value
    # ------------------------------------------------------------------
    value: Optional[float | int | str | bool] = None

    numeric_value: Optional[float] = None
    integer_value: Optional[int] = None
    text_value: Optional[str] = None
    boolean_value: Optional[bool] = None

    # ------------------------------------------------------------------
    # Optional market price context
    # ------------------------------------------------------------------
    price: Optional[float] = None
    bid: Optional[float] = None
    ask: Optional[float] = None

    # ------------------------------------------------------------------
    # Optional quantity / activity context
    # ------------------------------------------------------------------
    volume: Optional[float] = None
    quantity: Optional[float] = None
    turnover: Optional[float] = None
    open_interest: Optional[float] = None

    # ------------------------------------------------------------------
    # Data classification
    # ------------------------------------------------------------------
    observation_type: Optional[str] = None
    observation_status: Optional[str] = None

    observed: Optional[bool] = None
    derived: Optional[bool] = None
    estimated: Optional[bool] = None
    simulated: Optional[bool] = None

    # ------------------------------------------------------------------
    # Source / provenance
    # ------------------------------------------------------------------
    source: Optional[str] = None
    source_type: Optional[str] = None
    source_reference: Optional[str] = None
    provider: Optional[str] = None
    broker: Optional[str] = None

    provenance: Optional[str] = None

    # ------------------------------------------------------------------
    # Data quality
    # ------------------------------------------------------------------
    quality_status: Optional[str] = None
    quality_score: Optional[float] = None
    validation_status: Optional[str] = None

    latency_ms: Optional[float] = None
    age_ms: Optional[float] = None

    # ------------------------------------------------------------------
    # Environment
    # ------------------------------------------------------------------
    environment: Optional[str] = None
    mode: Optional[str] = None

    # ------------------------------------------------------------------
    # Field lineage
    # ------------------------------------------------------------------
    observed_fields: tuple[str, ...] = field(
        default_factory=tuple
    )

    derived_fields: tuple[str, ...] = field(
        default_factory=tuple
    )

    # ------------------------------------------------------------------
    # Additional structural metadata
    # ------------------------------------------------------------------
    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    # ------------------------------------------------------------------
    # Identity checks
    # ------------------------------------------------------------------
    def has_data_point_identity(self) -> bool:
        return _non_empty(self.data_point_id)

    def has_market_identity(self) -> bool:
        return any(
            _non_empty(value)
            for value in (
                self.market,
                self.instrument,
                self.symbol,
                self.exchange,
                self.venue,
                self.contract,
            )
        )

    def has_temporal_identity(self) -> bool:
        return any(
            value is not None
            for value in (
                self.timestamp,
                self.trading_date,
                self.sequence,
            )
        )

    def has_measurement_identity(self) -> bool:
        return any(
            _non_empty(value)
            for value in (
                self.field_name,
                self.field_code,
                self.measurement_type,
                self.measurement_unit,
            )
        )

    def has_value(self) -> bool:
        return any(
            value is not None
            for value in (
                self.value,
                self.numeric_value,
                self.integer_value,
                self.text_value,
                self.boolean_value,
                self.price,
                self.volume,
                self.quantity,
                self.turnover,
                self.open_interest,
            )
        )

    # ------------------------------------------------------------------
    # Numeric validation
    # ------------------------------------------------------------------
    def numeric_values_valid(self) -> bool:
        values = (
            self.numeric_value,
            self.price,
            self.bid,
            self.ask,
            self.volume,
            self.quantity,
            self.turnover,
            self.open_interest,
            self.latency_ms,
            self.age_ms,
        )

        return all(
            value is None or isinstance(value, (int, float))
            for value in values
        )

    def non_negative_values_valid(self) -> bool:
        values = (
            self.volume,
            self.quantity,
            self.turnover,
            self.open_interest,
            self.latency_ms,
            self.age_ms,
        )

        return all(
            _non_negative(value)
            for value in values
        )

    # ------------------------------------------------------------------
    # Price relationship validation
    # ------------------------------------------------------------------
    def quote_relationship_valid(self) -> bool:
        if self.bid is None or self.ask is None:
            return True

        return self.bid <= self.ask

    # ------------------------------------------------------------------
    # Quality validation
    # ------------------------------------------------------------------
    def quality_score_valid(self) -> bool:
        if self.quality_score is None:
            return True

        return 0 <= self.quality_score <= 100

    # ------------------------------------------------------------------
    # Classification validation
    # ------------------------------------------------------------------
    def classification_flags_valid(self) -> bool:
        flags = (
            self.observed,
            self.derived,
            self.estimated,
            self.simulated,
        )

        return all(
            value is None or isinstance(value, bool)
            for value in flags
        )

    # ------------------------------------------------------------------
    # Provenance
    # ------------------------------------------------------------------
    def has_provenance(self) -> bool:
        return any(
            _non_empty(value)
            for value in (
                self.source,
                self.source_type,
                self.source_reference,
                self.provider,
                self.broker,
                self.provenance,
            )
        )

    # ------------------------------------------------------------------
    # Structural issue collection
    # ------------------------------------------------------------------
    def issue_flags(self) -> list[str]:
        issues: list[str] = []

        if not self.has_data_point_identity():
            issues.append("missing_data_point_id")

        if not self.has_market_identity():
            issues.append("missing_market_identity")

        if not self.has_temporal_identity():
            issues.append("missing_temporal_identity")

        if not self.has_measurement_identity():
            issues.append("missing_measurement_identity")

        if not self.has_value():
            issues.append("missing_value")

        if not self.numeric_values_valid():
            issues.append("invalid_numeric_value")

        if not self.non_negative_values_valid():
            issues.append("negative_quantity_or_latency")

        if not self.quote_relationship_valid():
            issues.append("invalid_bid_ask_relationship")

        if not self.quality_score_valid():
            issues.append("invalid_quality_score")

        if not self.classification_flags_valid():
            issues.append("invalid_classification_flag")

        return issues

    # ------------------------------------------------------------------
    # Structural validity
    # ------------------------------------------------------------------
    def is_structurally_valid(self) -> bool:
        return len(self.issue_flags()) == 0

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    # ------------------------------------------------------------------
    # Schema metadata
    # ------------------------------------------------------------------
    @classmethod
    def schema_info(cls) -> dict[str, Any]:
        return {
            "schema": MARKET_DATA_POINT_SCHEMA,
            "version": MARKET_DATA_POINT_SCHEMA_VERSION,
            "immutable": True,
            "structural_only": True,
            "atomic_observation": True,
            "market_identity_preserved": True,
            "provenance_preserved": True,
            "signal_generation": False,
            "decision_logic": False,
            "execution_logic": False,
            "v7_dependency": False,
        }


def market_data_point_health() -> dict[str, Any]:
    """
    Return static health information for the MarketDataPoint schema.
    """

    return {
        "schema": MARKET_DATA_POINT_SCHEMA,
        "version": MARKET_DATA_POINT_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "structural_only": True,
        "atomic_observation": True,
        "market_identity_preserved": True,
        "provenance_preserved": True,
        "signal_generation": False,
        "decision_logic": False,
        "execution_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_DATA_POINT_SCHEMA_VERSION",
    "MARKET_DATA_POINT_SCHEMA",
    "MarketDataPoint",
    "market_data_point_health",
]