"""
ROBOMLM PLUS
Market Data Feed Schema

Purpose:
    Immutable structural representation of a market data feed.

Design:
    - Describes a source/feed delivering market data.
    - Separates feed identity, market identity, transport state,
      timing, quality, and provenance.
    - Does not generate signals.
    - Does not make trading decisions.
    - Does not execute orders.
    - No V7+ dependency.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Any, Mapping, Optional


MARKET_DATA_FEED_SCHEMA_VERSION = "1.0.0"
MARKET_DATA_FEED_SCHEMA = "MARKET_DATA_FEED"


def _non_empty(value: Any) -> bool:
    return value is not None and str(value).strip() != ""


def _non_negative(value: Optional[float | int]) -> bool:
    return value is None or value >= 0


@dataclass(frozen=True)
class MarketDataFeed:
    """
    Immutable structural market-data feed record.

    A feed identifies the source and delivery context of market data.
    It describes the feed; it does not interpret the delivered data.
    """

    # ------------------------------------------------------------------
    # Feed identity
    # ------------------------------------------------------------------
    feed_id: Optional[str] = None
    feed_name: Optional[str] = None
    feed_type: Optional[str] = None
    feed_code: Optional[str] = None
    feed_state: Optional[str] = None

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
    # Data definition
    # ------------------------------------------------------------------
    data_type: Optional[str] = None
    observation_type: Optional[str] = None
    measurement_type: Optional[str] = None

    schema_name: Optional[str] = None
    schema_version: Optional[str] = None

    timeframe_id: Optional[str] = None
    interval_id: Optional[str] = None
    series_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Source identity
    # ------------------------------------------------------------------
    source: Optional[str] = None
    source_type: Optional[str] = None
    source_id: Optional[str] = None
    source_reference: Optional[str] = None

    provider: Optional[str] = None
    broker: Optional[str] = None

    # ------------------------------------------------------------------
    # Transport / protocol
    # ------------------------------------------------------------------
    transport: Optional[str] = None
    protocol: Optional[str] = None
    endpoint: Optional[str] = None
    channel: Optional[str] = None
    topic: Optional[str] = None

    connection_id: Optional[str] = None
    subscription_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Feed mode
    # ------------------------------------------------------------------
    environment: Optional[str] = None
    mode: Optional[str] = None
    delivery_mode: Optional[str] = None

    is_live: Optional[bool] = None
    is_realtime: Optional[bool] = None
    is_delayed: Optional[bool] = None
    is_simulated: Optional[bool] = None

    # ------------------------------------------------------------------
    # Feed lifecycle
    # ------------------------------------------------------------------
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None

    last_message_at: Optional[datetime] = None
    last_data_at: Optional[datetime] = None

    # ------------------------------------------------------------------
    # Feed state
    # ------------------------------------------------------------------
    connection_status: Optional[str] = None
    subscription_status: Optional[str] = None
    health_status: Optional[str] = None
    availability_status: Optional[str] = None

    error_code: Optional[str] = None
    error_message: Optional[str] = None

    # ------------------------------------------------------------------
    # Throughput / counters
    # ------------------------------------------------------------------
    message_count: Optional[int] = None
    data_point_count: Optional[int] = None
    error_count: Optional[int] = None
    dropped_count: Optional[int] = None
    duplicate_count: Optional[int] = None

    bytes_received: Optional[int] = None

    # ------------------------------------------------------------------
    # Timing / latency
    # ------------------------------------------------------------------
    latency_ms: Optional[float] = None
    average_latency_ms: Optional[float] = None
    maximum_latency_ms: Optional[float] = None

    heartbeat_interval_ms: Optional[float] = None
    last_heartbeat_at: Optional[datetime] = None

    # ------------------------------------------------------------------
    # Quality
    # ------------------------------------------------------------------
    quality_status: Optional[str] = None
    quality_score: Optional[float] = None
    completeness_status: Optional[str] = None
    continuity_status: Optional[str] = None
    validation_status: Optional[str] = None

    # ------------------------------------------------------------------
    # Feed coverage
    # ------------------------------------------------------------------
    coverage_start: Optional[datetime] = None
    coverage_end: Optional[datetime] = None

    trading_date: Optional[date] = None
    timezone: Optional[str] = None

    # ------------------------------------------------------------------
    # Request / session context
    # ------------------------------------------------------------------
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    ingestion_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Provenance
    # ------------------------------------------------------------------
    provenance: Optional[str] = None

    observed_fields: tuple[str, ...] = field(
        default_factory=tuple
    )

    derived_fields: tuple[str, ...] = field(
        default_factory=tuple
    )

    # ------------------------------------------------------------------
    # Additional metadata
    # ------------------------------------------------------------------
    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    # ------------------------------------------------------------------
    # Identity checks
    # ------------------------------------------------------------------
    def has_feed_identity(self) -> bool:
        return _non_empty(self.feed_id)

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

    def has_source_identity(self) -> bool:
        return any(
            _non_empty(value)
            for value in (
                self.source,
                self.source_type,
                self.source_id,
                self.source_reference,
                self.provider,
                self.broker,
            )
        )

    def has_data_definition(self) -> bool:
        return any(
            _non_empty(value)
            for value in (
                self.data_type,
                self.observation_type,
                self.measurement_type,
                self.schema_name,
                self.timeframe_id,
                self.interval_id,
                self.series_id,
            )
        )

    # ------------------------------------------------------------------
    # Transport checks
    # ------------------------------------------------------------------
    def has_transport_definition(self) -> bool:
        return any(
            _non_empty(value)
            for value in (
                self.transport,
                self.protocol,
                self.endpoint,
                self.channel,
                self.topic,
            )
        )

    # ------------------------------------------------------------------
    # Lifecycle validation
    # ------------------------------------------------------------------
    def lifecycle_timestamps_valid(self) -> bool:
        pairs = (
            (
                self.created_at,
                self.updated_at,
            ),
            (
                self.started_at,
                self.stopped_at,
            ),
            (
                self.coverage_start,
                self.coverage_end,
            ),
        )

        for start, end in pairs:
            if start is not None and end is not None:
                if start > end:
                    return False

        return True

    # ------------------------------------------------------------------
    # Counter validation
    # ------------------------------------------------------------------
    def counters_valid(self) -> bool:
        values = (
            self.message_count,
            self.data_point_count,
            self.error_count,
            self.dropped_count,
            self.duplicate_count,
            self.bytes_received,
        )

        return all(
            _non_negative(value)
            for value in values
        )

    # ------------------------------------------------------------------
    # Latency validation
    # ------------------------------------------------------------------
    def latency_values_valid(self) -> bool:
        values = (
            self.latency_ms,
            self.average_latency_ms,
            self.maximum_latency_ms,
            self.heartbeat_interval_ms,
        )

        return all(
            _non_negative(value)
            for value in values
        )

    # ------------------------------------------------------------------
    # Quality validation
    # ------------------------------------------------------------------
    def quality_score_valid(self) -> bool:
        if self.quality_score is None:
            return True

        return 0 <= self.quality_score <= 100

    # ------------------------------------------------------------------
    # Boolean state validation
    # ------------------------------------------------------------------
    def state_flags_valid(self) -> bool:
        flags = (
            self.is_live,
            self.is_realtime,
            self.is_delayed,
            self.is_simulated,
        )

        return all(
            value is None or isinstance(value, bool)
            for value in flags
        )

    # ------------------------------------------------------------------
    # Structural issue collection
    # ------------------------------------------------------------------
    def issue_flags(self) -> list[str]:
        issues: list[str] = []

        if not self.has_feed_identity():
            issues.append("missing_feed_id")

        if not self.has_market_identity():
            issues.append("missing_market_identity")

        if not self.has_source_identity():
            issues.append("missing_source_identity")

        if not self.has_data_definition():
            issues.append("missing_data_definition")

        if not self.has_transport_definition():
            issues.append("missing_transport_definition")

        if not self.lifecycle_timestamps_valid():
            issues.append("invalid_lifecycle_timestamp")

        if not self.counters_valid():
            issues.append("invalid_counter")

        if not self.latency_values_valid():
            issues.append("invalid_latency_value")

        if not self.quality_score_valid():
            issues.append("invalid_quality_score")

        if not self.state_flags_valid():
            issues.append("invalid_state_flag")

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
            "schema": MARKET_DATA_FEED_SCHEMA,
            "version": MARKET_DATA_FEED_SCHEMA_VERSION,
            "immutable": True,
            "structural_only": True,
            "feed_identity": True,
            "source_provenance": True,
            "transport_context": True,
            "quality_context": True,
            "signal_generation": False,
            "decision_logic": False,
            "execution_logic": False,
            "v7_dependency": False,
        }


def market_data_feed_health() -> dict[str, Any]:
    """
    Return static health information for the MarketDataFeed schema.
    """

    return {
        "schema": MARKET_DATA_FEED_SCHEMA,
        "version": MARKET_DATA_FEED_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "structural_only": True,
        "feed_identity": True,
        "source_provenance": True,
        "transport_context": True,
        "quality_context": True,
        "signal_generation": False,
        "decision_logic": False,
        "execution_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_DATA_FEED_SCHEMA_VERSION",
    "MARKET_DATA_FEED_SCHEMA",
    "MarketDataFeed",
    "market_data_feed_health",
]