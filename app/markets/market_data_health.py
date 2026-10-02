from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from schemas.market.market_snapshot import MarketSnapshot


class MarketDataHealthStatus(str, Enum):
    VALID = "VALID"
    DEGRADED = "DEGRADED"
    STALE = "STALE"
    INVALID = "INVALID"


@dataclass(frozen=True)
class MarketDataHealthResult:
    """
    Operational health result for a canonical MarketSnapshot.

    This is NOT a trading decision and NOT an intelligence score.
    It only answers:

        Can this market snapshot safely proceed
        to downstream market-intelligence processing?
    """

    status: MarketDataHealthStatus
    usable: bool

    freshness_seconds: float
    max_age_seconds: float

    timestamp_valid: bool
    completeness_valid: bool
    source_valid: bool

    provider_quality_flags: tuple[str, ...]
    health_flags: tuple[str, ...]
    reasons: tuple[str, ...]

    checked_at: datetime
    observed_at: datetime
    source_timestamp: datetime
    received_timestamp: datetime

    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "usable": self.usable,
            "freshness_seconds": self.freshness_seconds,
            "max_age_seconds": self.max_age_seconds,
            "timestamp_valid": self.timestamp_valid,
            "completeness_valid": self.completeness_valid,
            "source_valid": self.source_valid,
            "provider_quality_flags": list(
                self.provider_quality_flags
            ),
            "health_flags": list(self.health_flags),
            "reasons": list(self.reasons),
            "checked_at": self.checked_at.isoformat(),
            "observed_at": self.observed_at.isoformat(),
            "source_timestamp": (
                self.source_timestamp.isoformat()
            ),
            "received_timestamp": (
                self.received_timestamp.isoformat()
            ),
            "metadata": dict(self.metadata),
        }


class MarketDataHealthService:
    """
    Deterministic market-data health evaluator.

    Responsibilities:
        - freshness
        - timestamp validation
        - completeness
        - source validation
        - provider quality flags
        - stale detection
        - downstream usability gate

    Does NOT:
        - calculate trading indicators
        - predict price
        - generate BUY/SELL decisions
        - modify MarketSnapshot
        - fabricate missing values
    """

    def __init__(
        self,
        *,
        default_max_age_seconds: float = 60.0,
        required_fields: tuple[str, ...] = ("price",),
    ) -> None:
        if default_max_age_seconds <= 0:
            raise ValueError(
                "default_max_age_seconds must be > 0"
            )

        self.default_max_age_seconds = float(
            default_max_age_seconds
        )

        self.required_fields = tuple(
            field.strip()
            for field in required_fields
            if field and field.strip()
        )

    @staticmethod
    def _ensure_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError(
                "Naive datetime is not allowed"
            )

        return value.astimezone(timezone.utc)

    def evaluate(
        self,
        snapshot: MarketSnapshot,
        *,
        now: datetime | None = None,
        max_age_seconds: float | None = None,
    ) -> MarketDataHealthResult:

        if not isinstance(snapshot, MarketSnapshot):
            raise TypeError(
                "snapshot must be a MarketSnapshot"
            )

        checked_at = self._ensure_utc(
            now
            if now is not None
            else datetime.now(timezone.utc)
        )

        observed_at = self._ensure_utc(
            snapshot.observation.observed_at
        )

        source_timestamp = self._ensure_utc(
            snapshot.data_quality.source_timestamp
        )

        received_timestamp = self._ensure_utc(
            snapshot.data_quality.received_timestamp
        )

        age_limit = (
            self.default_max_age_seconds
            if max_age_seconds is None
            else float(max_age_seconds)
        )

        if age_limit <= 0:
            raise ValueError(
                "max_age_seconds must be > 0"
            )

        health_flags: set[str] = set()
        reasons: list[str] = []

        provider_quality_flags = tuple(
            str(flag)
            for flag in snapshot.data_quality.quality_flags
            if str(flag).strip()
        )

        # ---------------------------------------------------------
        # 1. TIMESTAMP VALIDITY
        # ---------------------------------------------------------

        timestamp_valid = True

        if source_timestamp > received_timestamp:
            timestamp_valid = False
            health_flags.add("INVALID_TIMESTAMP_ORDER")
            reasons.append(
                "SOURCE_TIMESTAMP_AFTER_RECEIVED_TIMESTAMP"
            )

        if received_timestamp > observed_at:
            timestamp_valid = False
            health_flags.add("INVALID_TIMESTAMP_ORDER")
            reasons.append(
                "RECEIVED_TIMESTAMP_AFTER_OBSERVED_AT"
            )

        if observed_at > checked_at:
            timestamp_valid = False
            health_flags.add("FUTURE_OBSERVATION")
            reasons.append(
                "OBSERVED_AT_IS_IN_THE_FUTURE"
            )

        # ---------------------------------------------------------
        # 2. FRESHNESS
        # ---------------------------------------------------------

        freshness_seconds = max(
            (checked_at - observed_at).total_seconds(),
            0.0,
        )

        stale = (
            freshness_seconds > age_limit
            or snapshot.data_quality.is_stale
        )

        if stale:
            health_flags.add("STALE")
            reasons.append("MARKET_DATA_STALE")

        # ---------------------------------------------------------
        # 3. COMPLETENESS
        # ---------------------------------------------------------

        present_fields = set(
            snapshot.observation.fields_present
        )

        missing_required_fields = tuple(
            field
            for field in self.required_fields
            if field not in present_fields
        )

        completeness_valid = (
            snapshot.data_quality.is_complete
            and not missing_required_fields
        )

        if not snapshot.data_quality.is_complete:
            health_flags.add("PARTIAL")
            reasons.append(
                "PROVIDER_DECLARED_DATA_INCOMPLETE"
            )

        if missing_required_fields:
            health_flags.add("MISSING_REQUIRED_FIELD")
            reasons.append(
                "MISSING_REQUIRED_FIELDS:"
                + ",".join(missing_required_fields)
            )

        # ---------------------------------------------------------
        # 4. SOURCE VALIDITY
        # ---------------------------------------------------------

        source_valid = bool(
            snapshot.data_quality.source.strip()
        )

        if not source_valid:
            health_flags.add("SOURCE_MISSING")
            reasons.append(
                "MARKET_DATA_SOURCE_MISSING"
            )

        # ---------------------------------------------------------
        # 5. PROVIDER QUALITY FLAGS
        # ---------------------------------------------------------

        for flag in provider_quality_flags:
            health_flags.add(
                f"PROVIDER_{flag.upper()}"
            )

        # ---------------------------------------------------------
        # 6. FINAL HEALTH STATUS
        # ---------------------------------------------------------

        if not timestamp_valid or not source_valid:
            status = MarketDataHealthStatus.INVALID

        elif stale:
            status = MarketDataHealthStatus.STALE

        elif not completeness_valid:
            status = MarketDataHealthStatus.DEGRADED

        elif provider_quality_flags:
            status = MarketDataHealthStatus.DEGRADED

        else:
            status = MarketDataHealthStatus.VALID

        # ---------------------------------------------------------
        # 7. DOWNSTREAM USABILITY
        # ---------------------------------------------------------

        usable = (
            status == MarketDataHealthStatus.VALID
        )

        # ---------------------------------------------------------
        # 8. METADATA
        # ---------------------------------------------------------

        metadata = {
            "market": snapshot.market.market,
            "segment": snapshot.market.segment,
            "country": snapshot.market.country,
            "instrument": snapshot.instrument.symbol,
            "instrument_type": (
                snapshot.instrument.instrument_type
            ),
            "instrument_id": (
                snapshot.instrument.instrument_id
            ),
            "venue": snapshot.venue.venue,
            "venue_id": snapshot.venue.venue_id,
            "contract_id": (
                snapshot.contract.contract_id
                if snapshot.contract is not None
                else None
            ),
            "source": snapshot.data_quality.source,
            "source_type": (
                snapshot.metadata.get("source_type")
            ),
            "required_fields": list(
                self.required_fields
            ),
            "present_fields": sorted(
                present_fields
            ),
            "missing_required_fields": list(
                missing_required_fields
            ),
            "provider_latency_ms": (
                snapshot.data_quality.latency_ms
            ),
            "provider_is_complete": (
                snapshot.data_quality.is_complete
            ),
            "provider_is_stale": (
                snapshot.data_quality.is_stale
            ),
        }

        return MarketDataHealthResult(
            status=status,
            usable=usable,
            freshness_seconds=freshness_seconds,
            max_age_seconds=age_limit,
            timestamp_valid=timestamp_valid,
            completeness_valid=completeness_valid,
            source_valid=source_valid,
            provider_quality_flags=provider_quality_flags,
            health_flags=tuple(
                sorted(health_flags)
            ),
            reasons=tuple(reasons),
            checked_at=checked_at,
            observed_at=observed_at,
            source_timestamp=source_timestamp,
            received_timestamp=received_timestamp,
            metadata=metadata,
        )

    def is_usable(
        self,
        snapshot: MarketSnapshot,
        *,
        now: datetime | None = None,
        max_age_seconds: float | None = None,
    ) -> bool:

        return self.evaluate(
            snapshot,
            now=now,
            max_age_seconds=max_age_seconds,
        ).usable

    def assert_usable(
        self,
        snapshot: MarketSnapshot,
        *,
        now: datetime | None = None,
        max_age_seconds: float | None = None,
    ) -> MarketDataHealthResult:

        result = self.evaluate(
            snapshot,
            now=now,
            max_age_seconds=max_age_seconds,
        )

        if not result.usable:
            raise ValueError(
                "MARKET_DATA_NOT_USABLE: "
                + "; ".join(result.reasons)
            )

        return result