"""
ROBOMLM_PLUS
Intraday Intelligence Engine
============================

Purpose
-------
Point-in-time intraday qualification layer for Opportunity Discovery.

This engine:
    - normalizes intraday observations
    - validates temporal and market identity integrity
    - evaluates observable intraday conditions
    - applies externally supplied policy thresholds
    - produces a normalized qualification decision

This engine does NOT:
    - generate BUY/SELL signals
    - invent proprietary prediction scores
    - predict future prices
    - replace EQE/PFS/MCI/D13
    - replace the dedicated risk/liquidity/timing engines
    - manufacture missing market data

Engineering principles
----------------------
1. Point-in-time integrity
2. Market identity integrity
3. No future-data leakage
4. No fabricated values
5. External-policy-driven thresholds
6. Deterministic outputs
7. Provenance preservation
8. Normalized output contract
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict, is_dataclass
from enum import Enum
from datetime import datetime, timezone
from math import isfinite
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple


# ============================================================================
# ENUMS
# ============================================================================

class IntradayStatus(str, Enum):
    PASS = "PASS"
    REVIEW = "REVIEW"
    REJECT = "REJECT"
    UNKNOWN = "UNKNOWN"


class IntradayCondition(str, Enum):
    ACTIVE = "ACTIVE"
    DEVELOPING = "DEVELOPING"
    EXPANDING = "EXPANDING"
    CONTRACTING = "CONTRACTING"
    WEAK = "WEAK"
    STALE = "STALE"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    UNKNOWN = "UNKNOWN"


class IntradayStructure(str, Enum):
    TRENDING = "TRENDING"
    RANGE = "RANGE"
    BREAKOUT = "BREAKOUT"
    BREAKDOWN = "BREAKDOWN"
    REVERSAL = "REVERSAL"
    CHOPPY = "CHOPPY"
    FLAT = "FLAT"
    UNKNOWN = "UNKNOWN"


class IntradayDirection(str, Enum):
    UP = "UP"
    DOWN = "DOWN"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"


# ============================================================================
# SNAPSHOT
# ============================================================================

@dataclass
class IntradaySnapshot:
    """
    Point-in-time intraday market observation.

    All values are observations or upstream-derived measurements.
    No value is invented by this engine.
    """

    instrument_id: Optional[str] = None
    symbol: Optional[str] = None

    timestamp: Optional[datetime] = None

    market_id: Optional[str] = None
    venue_id: Optional[str] = None

    price: Optional[float] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    previous_close: Optional[float] = None

    volume: Optional[float] = None
    average_volume: Optional[float] = None

    turnover: Optional[float] = None
    average_turnover: Optional[float] = None

    volatility: Optional[float] = None
    volatility_pct: Optional[float] = None

    atr: Optional[float] = None
    atr_pct: Optional[float] = None

    range_pct: Optional[float] = None
    body_pct: Optional[float] = None

    price_change_pct: Optional[float] = None
    change_from_open_pct: Optional[float] = None
    change_from_previous_close_pct: Optional[float] = None

    volume_ratio: Optional[float] = None
    turnover_ratio: Optional[float] = None

    momentum: Optional[float] = None
    trend_strength: Optional[float] = None

    structure: IntradayStructure = IntradayStructure.UNKNOWN
    direction: IntradayDirection = IntradayDirection.UNKNOWN

    session_progress_pct: Optional[float] = None

    minutes_from_open: Optional[float] = None
    minutes_to_close: Optional[float] = None

    market_open: Optional[bool] = None
    is_trading_day: Optional[bool] = None

    event_near: Optional[bool] = None
    expiry_near: Optional[bool] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# DECISION
# ============================================================================

@dataclass
class IntradayDecision:
    instrument_id: Optional[str]
    symbol: Optional[str]

    status: IntradayStatus
    condition: IntradayCondition

    structure: IntradayStructure
    direction: IntradayDirection

    reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    price: Optional[float] = None

    volume_ratio: Optional[float] = None
    turnover_ratio: Optional[float] = None

    volatility_pct: Optional[float] = None
    atr_pct: Optional[float] = None

    momentum: Optional[float] = None
    trend_strength: Optional[float] = None

    range_pct: Optional[float] = None
    body_pct: Optional[float] = None

    session_progress_pct: Optional[float] = None
    minutes_from_open: Optional[float] = None
    minutes_to_close: Optional[float] = None

    event_near: Optional[bool] = None
    expiry_near: Optional[bool] = None

    market_id: Optional[str] = None
    venue_id: Optional[str] = None
    timestamp: Optional[datetime] = None

    provenance: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# RESULT
# ============================================================================

@dataclass
class IntradayResult:
    decision: IntradayDecision

    snapshot: Optional[IntradaySnapshot] = None

    passed: bool = False
    review: bool = False
    rejected: bool = False
    unknown: bool = False

    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.passed = self.decision.status == IntradayStatus.PASS
        self.review = self.decision.status == IntradayStatus.REVIEW
        self.rejected = self.decision.status == IntradayStatus.REJECT
        self.unknown = self.decision.status == IntradayStatus.UNKNOWN


# ============================================================================
# POLICY
# ============================================================================

@dataclass
class IntradayPolicy:
    """
    External policy contract.

    Defaults intentionally remain None where a business threshold has not
    been explicitly established by the upstream ROBOMLM blueprint.

    The engine must not invent such thresholds.
    """

    policy_version: str = "EXTERNAL_POLICY_REQUIRED"

    minimum_volume_ratio: Optional[float] = None
    review_volume_ratio: Optional[float] = None

    minimum_turnover_ratio: Optional[float] = None
    review_turnover_ratio: Optional[float] = None

    minimum_trend_strength: Optional[float] = None
    review_trend_strength: Optional[float] = None

    minimum_momentum: Optional[float] = None
    review_momentum: Optional[float] = None

    maximum_range_pct: Optional[float] = None
    review_range_pct: Optional[float] = None

    minimum_session_progress_pct: Optional[float] = None

    maximum_minutes_to_close: Optional[float] = None
    review_minutes_to_close: Optional[float] = None

    stale_after_seconds: Optional[float] = None

    require_price: bool = True
    require_trading_day: bool = False
    require_market_open: bool = False

    reject_non_trading_day: bool = True
    reject_closed_market: bool = False

    reject_event_near: bool = False
    review_event_near: bool = True

    reject_expiry_near: bool = False
    review_expiry_near: bool = True

    review_unknown_structure: bool = True
    review_unknown_direction: bool = False

    require_intraday_observation: bool = True

    reject_future_data: bool = True
    require_market_match: bool = True

    minimum_data_fields: int = 1


# ============================================================================
# ENGINE
# ============================================================================

class IntradayEngine:
    """
    ROBOMLM_PLUS Intraday Intelligence Engine.
    """

    ENGINE_NAME = "IntradayEngine"
    ENGINE_VERSION = "1.0"

    def __init__(
        self,
        policy: Optional[IntradayPolicy] = None,
        *,
        expected_market_id: Optional[str] = None,
        now: Optional[datetime] = None,
    ) -> None:
        self.policy = policy or IntradayPolicy()
        self.expected_market_id = expected_market_id
        self.now = self._ensure_aware(now) if now is not None else None

    # ----------------------------------------------------------------------
    # PUBLIC EVALUATION API
    # ----------------------------------------------------------------------

    def evaluate(
        self,
        snapshot: Any,
        *,
        now: Optional[datetime] = None,
        expected_market_id: Optional[str] = None,
    ) -> IntradayDecision:
        """
        Evaluate one point-in-time intraday snapshot.
        """

        normalized = self.normalize(snapshot)

        current_now = self._ensure_aware(
            now if now is not None else self.now
        )

        if current_now is None:
            current_now = datetime.now(timezone.utc)

        reasons: List[str] = []
        warnings: List[str] = []

        # --------------------------------------------------------------
        # Identity
        # --------------------------------------------------------------

        if not normalized.instrument_id and not normalized.symbol:
            return self._decision(
                normalized,
                IntradayStatus.UNKNOWN,
                IntradayCondition.INSUFFICIENT_DATA,
                reasons=["Missing instrument identity"],
                warnings=warnings,
            )

        # --------------------------------------------------------------
        # Market identity
        # --------------------------------------------------------------

        market_to_check = (
            expected_market_id
            if expected_market_id is not None
            else self.expected_market_id
        )

        if self.policy.require_market_match and market_to_check:
            if normalized.market_id is None:
                return self._decision(
                    normalized,
                    IntradayStatus.UNKNOWN,
                    IntradayCondition.INSUFFICIENT_DATA,
                    reasons=["Missing market identity"],
                    warnings=warnings,
                )

            if normalized.market_id != market_to_check:
                return self._decision(
                    normalized,
                    IntradayStatus.REJECT,
                    IntradayCondition.UNKNOWN,
                    reasons=[
                        "Market identity mismatch",
                        f"Expected market_id={market_to_check}",
                        f"Received market_id={normalized.market_id}",
                    ],
                    warnings=warnings,
                )

        # --------------------------------------------------------------
        # Timestamp
        # --------------------------------------------------------------

        if normalized.timestamp is None:
            warnings.append("Timestamp unavailable")

        else:
            timestamp = self._ensure_aware(normalized.timestamp)

            if timestamp is None:
                return self._decision(
                    normalized,
                    IntradayStatus.UNKNOWN,
                    IntradayCondition.INSUFFICIENT_DATA,
                    reasons=["Invalid timestamp"],
                    warnings=warnings,
                )

            normalized.timestamp = timestamp

            if self.policy.reject_future_data and timestamp > current_now:
                return self._decision(
                    normalized,
                    IntradayStatus.REJECT,
                    IntradayCondition.UNKNOWN,
                    reasons=["Future-dated intraday observation rejected"],
                    warnings=warnings,
                )

        # --------------------------------------------------------------
        # Trading day
        # --------------------------------------------------------------

        if normalized.is_trading_day is False:
            if self.policy.reject_non_trading_day:
                return self._decision(
                    normalized,
                    IntradayStatus.REJECT,
                    IntradayCondition.INSUFFICIENT_DATA,
                    reasons=["Observation belongs to a non-trading day"],
                    warnings=warnings,
                )

            warnings.append("Non-trading day")

        elif normalized.is_trading_day is None:
            if self.policy.require_trading_day:
                return self._decision(
                    normalized,
                    IntradayStatus.UNKNOWN,
                    IntradayCondition.INSUFFICIENT_DATA,
                    reasons=["Trading-day state unavailable"],
                    warnings=warnings,
                )

            warnings.append("Trading-day state unavailable")

        # --------------------------------------------------------------
        # Market open state
        # --------------------------------------------------------------

        if normalized.market_open is False:
            if self.policy.reject_closed_market:
                return self._decision(
                    normalized,
                    IntradayStatus.REJECT,
                    IntradayCondition.INSUFFICIENT_DATA,
                    reasons=["Market is closed"],
                    warnings=warnings,
                )

            if self.policy.require_market_open:
                return self._decision(
                    normalized,
                    IntradayStatus.REVIEW,
                    IntradayCondition.INSUFFICIENT_DATA,
                    reasons=["Market is not open"],
                    warnings=warnings,
                )

            warnings.append("Market is currently closed")

        elif normalized.market_open is None:
            if self.policy.require_market_open:
                return self._decision(
                    normalized,
                    IntradayStatus.UNKNOWN,
                    IntradayCondition.INSUFFICIENT_DATA,
                    reasons=["Market-open state unavailable"],
                    warnings=warnings,
                )

            warnings.append("Market-open state unavailable")

        # --------------------------------------------------------------
        # Price validation
        # --------------------------------------------------------------

        if self.policy.require_price:
            if not self._valid_number(normalized.price):
                return self._decision(
                    normalized,
                    IntradayStatus.UNKNOWN,
                    IntradayCondition.INSUFFICIENT_DATA,
                    reasons=["Valid price observation unavailable"],
                    warnings=warnings,
                )

        # --------------------------------------------------------------
        # Numeric integrity
        # --------------------------------------------------------------

        numeric_fields = {
            "volume": normalized.volume,
            "average_volume": normalized.average_volume,
            "turnover": normalized.turnover,
            "average_turnover": normalized.average_turnover,
            "volatility": normalized.volatility,
            "volatility_pct": normalized.volatility_pct,
            "atr": normalized.atr,
            "atr_pct": normalized.atr_pct,
            "range_pct": normalized.range_pct,
            "body_pct": normalized.body_pct,
            "price_change_pct": normalized.price_change_pct,
            "change_from_open_pct": normalized.change_from_open_pct,
            "change_from_previous_close_pct":
                normalized.change_from_previous_close_pct,
            "volume_ratio": normalized.volume_ratio,
            "turnover_ratio": normalized.turnover_ratio,
            "momentum": normalized.momentum,
            "trend_strength": normalized.trend_strength,
            "session_progress_pct": normalized.session_progress_pct,
            "minutes_from_open": normalized.minutes_from_open,
            "minutes_to_close": normalized.minutes_to_close,
        }

        for field_name, value in numeric_fields.items():
            if value is not None and not self._valid_number(value):
                return self._decision(
                    normalized,
                    IntradayStatus.REJECT,
                    IntradayCondition.UNKNOWN,
                    reasons=[
                        f"Invalid numeric field: {field_name}"
                    ],
                    warnings=warnings,
                )

        # --------------------------------------------------------------
        # Timing distance validation
        # --------------------------------------------------------------

        if (
            normalized.minutes_from_open is not None
            and normalized.minutes_from_open < 0
        ):
            return self._decision(
                normalized,
                IntradayStatus.REJECT,
                IntradayCondition.UNKNOWN,
                reasons=["minutes_from_open cannot be negative"],
                warnings=warnings,
            )

        if (
            normalized.minutes_to_close is not None
            and normalized.minutes_to_close < 0
        ):
            warnings.append("minutes_to_close is negative")

        # --------------------------------------------------------------
        # Observability
        # --------------------------------------------------------------

        if self.policy.require_intraday_observation:
            if not self._has_observable_intraday_data(normalized):
                return self._decision(
                    normalized,
                    IntradayStatus.UNKNOWN,
                    IntradayCondition.INSUFFICIENT_DATA,
                    reasons=["Insufficient intraday observations"],
                    warnings=warnings,
                )

        # --------------------------------------------------------------
        # Volume policy
        # --------------------------------------------------------------

        if normalized.volume_ratio is not None:

            if (
                self.policy.minimum_volume_ratio is not None
                and normalized.volume_ratio
                < self.policy.minimum_volume_ratio
            ):
                return self._decision(
                    normalized,
                    IntradayStatus.REJECT,
                    IntradayCondition.WEAK,
                    reasons=[
                        "Volume ratio below minimum policy threshold"
                    ],
                    warnings=warnings,
                )

            if (
                self.policy.review_volume_ratio is not None
                and normalized.volume_ratio
                < self.policy.review_volume_ratio
            ):
                warnings.append(
                    "Volume ratio below review threshold"
                )

        # --------------------------------------------------------------
        # Turnover policy
        # --------------------------------------------------------------

        if normalized.turnover_ratio is not None:

            if (
                self.policy.minimum_turnover_ratio is not None
                and normalized.turnover_ratio
                < self.policy.minimum_turnover_ratio
            ):
                return self._decision(
                    normalized,
                    IntradayStatus.REJECT,
                    IntradayCondition.WEAK,
                    reasons=[
                        "Turnover ratio below minimum policy threshold"
                    ],
                    warnings=warnings,
                )

            if (
                self.policy.review_turnover_ratio is not None
                and normalized.turnover_ratio
                < self.policy.review_turnover_ratio
            ):
                warnings.append(
                    "Turnover ratio below review threshold"
                )

        # --------------------------------------------------------------
        # Trend-strength policy
        # --------------------------------------------------------------

        if normalized.trend_strength is not None:

            if (
                self.policy.minimum_trend_strength is not None
                and abs(normalized.trend_strength)
                < self.policy.minimum_trend_strength
            ):
                return self._decision(
                    normalized,
                    IntradayStatus.REJECT,
                    IntradayCondition.WEAK,
                    reasons=[
                        "Trend strength below minimum policy threshold"
                    ],
                    warnings=warnings,
                )

            if (
                self.policy.review_trend_strength is not None
                and abs(normalized.trend_strength)
                < self.policy.review_trend_strength
            ):
                warnings.append(
                    "Trend strength below review threshold"
                )

        # --------------------------------------------------------------
        # Momentum policy
        # --------------------------------------------------------------

        if normalized.momentum is not None:

            if (
                self.policy.minimum_momentum is not None
                and abs(normalized.momentum)
                < self.policy.minimum_momentum
            ):
                return self._decision(
                    normalized,
                    IntradayStatus.REJECT,
                    IntradayCondition.WEAK,
                    reasons=[
                        "Momentum below minimum policy threshold"
                    ],
                    warnings=warnings,
                )

            if (
                self.policy.review_momentum is not None
                and abs(normalized.momentum)
                < self.policy.review_momentum
            ):
                warnings.append(
                    "Momentum below review threshold"
                )

        # --------------------------------------------------------------
        # Range policy
        # --------------------------------------------------------------

        if normalized.range_pct is not None:

            if (
                self.policy.maximum_range_pct is not None
                and normalized.range_pct
                > self.policy.maximum_range_pct
            ):
                return self._decision(
                    normalized,
                    IntradayStatus.REJECT,
                    IntradayCondition.WEAK,
                    reasons=[
                        "Intraday range exceeds maximum policy threshold"
                    ],
                    warnings=warnings,
                )

            if (
                self.policy.review_range_pct is not None
                and normalized.range_pct
                > self.policy.review_range_pct
            ):
                warnings.append(
                    "Intraday range exceeds review threshold"
                )

        # --------------------------------------------------------------
        # Session progress
        # --------------------------------------------------------------

        if normalized.session_progress_pct is not None:

            if (
                self.policy.minimum_session_progress_pct is not None
                and normalized.session_progress_pct
                < self.policy.minimum_session_progress_pct
            ):
                warnings.append(
                    "Session progress is below configured minimum"
                )

        # --------------------------------------------------------------
        # Closing proximity
        # --------------------------------------------------------------

        if normalized.minutes_to_close is not None:

            if (
                self.policy.maximum_minutes_to_close is not None
                and normalized.minutes_to_close
                <= self.policy.maximum_minutes_to_close
            ):
                return self._decision(
                    normalized,
                    IntradayStatus.REJECT,
                    IntradayCondition.WEAK,
                    reasons=[
                        "Observation is too close to market close"
                    ],
                    warnings=warnings,
                )

            if (
                self.policy.review_minutes_to_close is not None
                and normalized.minutes_to_close
                <= self.policy.review_minutes_to_close
            ):
                warnings.append(
                    "Observation is approaching market close"
                )

        # --------------------------------------------------------------
        # Structure
        # --------------------------------------------------------------

        if (
            normalized.structure == IntradayStructure.UNKNOWN
            and self.policy.review_unknown_structure
        ):
            warnings.append("Intraday structure is unknown")

        # --------------------------------------------------------------
        # Direction
        # --------------------------------------------------------------

        if (
            normalized.direction == IntradayDirection.UNKNOWN
            and self.policy.review_unknown_direction
        ):
            warnings.append("Intraday direction is unknown")

        # --------------------------------------------------------------
        # Event proximity
        # --------------------------------------------------------------

        if normalized.event_near is True:

            if self.policy.reject_event_near:
                return self._decision(
                    normalized,
                    IntradayStatus.REJECT,
                    IntradayCondition.UNKNOWN,
                    reasons=["Event-near observation rejected by policy"],
                    warnings=warnings,
                )

            if self.policy.review_event_near:
                warnings.append("Event-near condition")

        # --------------------------------------------------------------
        # Expiry proximity
        # --------------------------------------------------------------

        if normalized.expiry_near is True:

            if self.policy.reject_expiry_near:
                return self._decision(
                    normalized,
                    IntradayStatus.REJECT,
                    IntradayCondition.UNKNOWN,
                    reasons=["Expiry-near observation rejected by policy"],
                    warnings=warnings,
                )

            if self.policy.review_expiry_near:
                warnings.append("Expiry-near condition")

        # --------------------------------------------------------------
        # Condition
        # --------------------------------------------------------------

        condition = self._condition(normalized)

        # --------------------------------------------------------------
        # Staleness
        # --------------------------------------------------------------

        if (
            normalized.timestamp is not None
            and self.policy.stale_after_seconds is not None
        ):
            age_seconds = (
                current_now - normalized.timestamp
            ).total_seconds()

            if age_seconds < 0:
                if self.policy.reject_future_data:
                    return self._decision(
                        normalized,
                        IntradayStatus.REJECT,
                        IntradayCondition.UNKNOWN,
                        reasons=["Future observation detected"],
                        warnings=warnings,
                    )

            elif age_seconds > self.policy.stale_after_seconds:
                return self._decision(
                    normalized,
                    IntradayStatus.REVIEW,
                    IntradayCondition.STALE,
                    reasons=["Intraday observation is stale"],
                    warnings=warnings,
                )

        # --------------------------------------------------------------
        # Final status
        # --------------------------------------------------------------

        if warnings:
            status = IntradayStatus.REVIEW
            reasons.append(
                "Intraday observation satisfies core validation "
                "but requires review"
            )
        else:
            status = IntradayStatus.PASS
            reasons.append(
                "Intraday observation satisfies configured policy"
            )

        return self._decision(
            normalized,
            status,
            condition,
            reasons=reasons,
            warnings=warnings,
        )

    # ----------------------------------------------------------------------
    # COLLECTION FILTER
    # ----------------------------------------------------------------------

    def filter(
        self,
        snapshots: Iterable[Any],
        *,
        now: Optional[datetime] = None,
        expected_market_id: Optional[str] = None,
    ) -> List[IntradayDecision]:

        decisions: List[IntradayDecision] = []

        for snapshot in snapshots:
            decisions.append(
                self.evaluate(
                    snapshot,
                    now=now,
                    expected_market_id=expected_market_id,
                )
            )

        return decisions

    # ----------------------------------------------------------------------
    # APPLY
    # ----------------------------------------------------------------------

    def apply(
        self,
        snapshots: Iterable[Any],
        *,
        now: Optional[datetime] = None,
        expected_market_id: Optional[str] = None,
    ) -> List[IntradayResult]:

        items = list(snapshots)

        decisions = self.filter(
            items,
            now=now,
            expected_market_id=expected_market_id,
        )

        results: List[IntradayResult] = []

        for snapshot, decision in zip(items, decisions):
            normalized = self.normalize(snapshot)

            results.append(
                IntradayResult(
                    decision=decision,
                    snapshot=normalized,
                    metadata={
                        "engine": self.ENGINE_NAME,
                        "engine_version": self.ENGINE_VERSION,
                        "policy_version": self.policy.policy_version,
                    },
                )
            )

        return results

    # ----------------------------------------------------------------------
    # NORMALIZATION
    # ----------------------------------------------------------------------

    def normalize(self, snapshot: Any) -> IntradaySnapshot:
        """
        Normalize mapping/dataclass/object input into IntradaySnapshot.
        Unknown fields are preserved in metadata.
        """

        if isinstance(snapshot, IntradaySnapshot):
            normalized = snapshot

            normalized.timestamp = self._parse_timestamp(
                normalized.timestamp
            )

            normalized.structure = self._parse_structure(
                normalized.structure
            )

            normalized.direction = self._parse_direction(
                normalized.direction
            )

            return normalized

        data = self._to_mapping(snapshot)

        metadata = dict(data.get("metadata") or {})

        known_fields = {
            field_name
            for field_name in IntradaySnapshot.__dataclass_fields__
        }

        for key, value in data.items():
            if key not in known_fields and key != "metadata":
                metadata.setdefault(key, value)

        timestamp = self._parse_timestamp(
            self._first(
                data,
                "timestamp",
                "time",
                "observed_at",
                "datetime",
                "date_time",
            )
        )

        normalized = IntradaySnapshot(
            instrument_id=self._string_or_none(
                self._first(
                    data,
                    "instrument_id",
                    "instrument",
                    "id",
                )
            ),
            symbol=self._string_or_none(
                self._first(
                    data,
                    "symbol",
                    "ticker",
                    "exchange_symbol",
                )
            ),
            timestamp=timestamp,
            market_id=self._string_or_none(
                self._first(
                    data,
                    "market_id",
                    "market",
                )
            ),
            venue_id=self._string_or_none(
                self._first(
                    data,
                    "venue_id",
                    "venue",
                    "exchange",
                )
            ),
            price=self._number(
                self._first(data, "price", "ltp", "last_price")
            ),
            open=self._number(
                self._first(data, "open", "open_price")
            ),
            high=self._number(
                self._first(data, "high", "high_price")
            ),
            low=self._number(
                self._first(data, "low", "low_price")
            ),
            previous_close=self._number(
                self._first(
                    data,
                    "previous_close",
                    "prev_close",
                    "close_previous",
                )
            ),
            volume=self._number(
                self._first(data, "volume", "current_volume")
            ),
            average_volume=self._number(
                self._first(
                    data,
                    "average_volume",
                    "avg_volume",
                    "volume_avg",
                )
            ),
            turnover=self._number(
                self._first(
                    data,
                    "turnover",
                    "current_turnover",
                )
            ),
            average_turnover=self._number(
                self._first(
                    data,
                    "average_turnover",
                    "avg_turnover",
                )
            ),
            volatility=self._number(
                self._first(data, "volatility")
            ),
            volatility_pct=self._number(
                self._first(
                    data,
                    "volatility_pct",
                    "vol_pct",
                )
            ),
            atr=self._number(
                self._first(data, "atr")
            ),
            atr_pct=self._number(
                self._first(
                    data,
                    "atr_pct",
                )
            ),
            range_pct=self._number(
                self._first(
                    data,
                    "range_pct",
                    "intraday_range_pct",
                )
            ),
            body_pct=self._number(
                self._first(
                    data,
                    "body_pct",
                    "candle_body_pct",
                )
            ),
            price_change_pct=self._number(
                self._first(
                    data,
                    "price_change_pct",
                    "change_pct",
                )
            ),
            change_from_open_pct=self._number(
                self._first(
                    data,
                    "change_from_open_pct",
                    "open_change_pct",
                )
            ),
            change_from_previous_close_pct=self._number(
                self._first(
                    data,
                    "change_from_previous_close_pct",
                    "prev_close_change_pct",
                )
            ),
            volume_ratio=self._number(
                self._first(
                    data,
                    "volume_ratio",
                    "vol_ratio",
                )
            ),
            turnover_ratio=self._number(
                self._first(
                    data,
                    "turnover_ratio",
                    "turn_ratio",
                )
            ),
            momentum=self._number(
                self._first(data, "momentum")
            ),
            trend_strength=self._number(
                self._first(
                    data,
                    "trend_strength",
                    "trend_score",
                )
            ),
            structure=self._parse_structure(
                self._first(
                    data,
                    "structure",
                    "intraday_structure",
                )
            ),
            direction=self._parse_direction(
                self._first(
                    data,
                    "direction",
                    "intraday_direction",
                )
            ),
            session_progress_pct=self._number(
                self._first(
                    data,
                    "session_progress_pct",
                    "session_progress",
                )
            ),
            minutes_from_open=self._number(
                self._first(
                    data,
                    "minutes_from_open",
                )
            ),
            minutes_to_close=self._number(
                self._first(
                    data,
                    "minutes_to_close",
                )
            ),
            market_open=self._boolean(
                self._first(
                    data,
                    "market_open",
                    "is_market_open",
                )
            ),
            is_trading_day=self._boolean(
                self._first(
                    data,
                    "is_trading_day",
                    "trading_day",
                )
            ),
            event_near=self._boolean(
                self._first(
                    data,
                    "event_near",
                    "event_proximity",
                )
            ),
            expiry_near=self._boolean(
                self._first(
                    data,
                    "expiry_near",
                    "expiry_proximity",
                )
            ),
            metadata=metadata,
        )

        return normalized

    # ----------------------------------------------------------------------
    # OBSERVABILITY
    # ----------------------------------------------------------------------

    def _has_observable_intraday_data(
        self,
        snapshot: IntradaySnapshot,
    ) -> bool:

        fields = [
            snapshot.price,
            snapshot.volume,
            snapshot.turnover,
            snapshot.volatility,
            snapshot.volatility_pct,
            snapshot.atr,
            snapshot.atr_pct,
            snapshot.range_pct,
            snapshot.body_pct,
            snapshot.price_change_pct,
            snapshot.change_from_open_pct,
            snapshot.change_from_previous_close_pct,
            snapshot.volume_ratio,
            snapshot.turnover_ratio,
            snapshot.momentum,
            snapshot.trend_strength,
            snapshot.session_progress_pct,
            snapshot.minutes_from_open,
            snapshot.minutes_to_close,
        ]

        count = sum(
            1 for value in fields
            if self._valid_number(value)
        )

        return count >= max(
            1,
            self.policy.minimum_data_fields,
        )

    # ----------------------------------------------------------------------
    # CONDITION
    # ----------------------------------------------------------------------

    def _condition(
        self,
        snapshot: IntradaySnapshot,
    ) -> IntradayCondition:

        if (
            snapshot.timestamp is None
            and not self._has_observable_intraday_data(snapshot)
        ):
            return IntradayCondition.INSUFFICIENT_DATA

        if snapshot.structure == IntradayStructure.FLAT:
            return IntradayCondition.WEAK

        if snapshot.structure == IntradayStructure.CHOPPY:
            return IntradayCondition.CONTRACTING

        if snapshot.structure in (
            IntradayStructure.BREAKOUT,
            IntradayStructure.TRENDING,
        ):
            if (
                snapshot.trend_strength is not None
                and snapshot.trend_strength > 0
            ):
                return IntradayCondition.EXPANDING

            if (
                snapshot.momentum is not None
                and abs(snapshot.momentum) > 0
            ):
                return IntradayCondition.ACTIVE

            return IntradayCondition.DEVELOPING

        if snapshot.structure in (
            IntradayStructure.BREAKDOWN,
            IntradayStructure.REVERSAL,
        ):
            if (
                snapshot.momentum is not None
                and snapshot.momentum < 0
            ):
                return IntradayCondition.CONTRACTING

            return IntradayCondition.DEVELOPING

        if snapshot.momentum is not None:
            if snapshot.momentum > 0:
                return IntradayCondition.EXPANDING

            if snapshot.momentum < 0:
                return IntradayCondition.CONTRACTING

        if snapshot.trend_strength is not None:
            if abs(snapshot.trend_strength) > 0:
                return IntradayCondition.ACTIVE

        if snapshot.volume_ratio is not None:
            if snapshot.volume_ratio > 1:
                return IntradayCondition.ACTIVE

        return IntradayCondition.DEVELOPING

    # ----------------------------------------------------------------------
    # DECISION BUILDER
    # ----------------------------------------------------------------------

    def _decision(
        self,
        snapshot: IntradaySnapshot,
        status: IntradayStatus,
        condition: IntradayCondition,
        *,
        reasons: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None,
    ) -> IntradayDecision:

        provenance = {
            "engine": self.ENGINE_NAME,
            "engine_version": self.ENGINE_VERSION,
            "policy_version": self.policy.policy_version,
            "point_in_time": snapshot.timestamp.isoformat()
            if snapshot.timestamp is not None
            else None,
            "market_id": snapshot.market_id,
            "venue_id": snapshot.venue_id,
        }

        return IntradayDecision(
            instrument_id=snapshot.instrument_id,
            symbol=snapshot.symbol,
            status=status,
            condition=condition,
            structure=snapshot.structure,
            direction=snapshot.direction,
            reasons=list(reasons or []),
            warnings=list(warnings or []),
            price=snapshot.price,
            volume_ratio=snapshot.volume_ratio,
            turnover_ratio=snapshot.turnover_ratio,
            volatility_pct=snapshot.volatility_pct,
            atr_pct=snapshot.atr_pct,
            momentum=snapshot.momentum,
            trend_strength=snapshot.trend_strength,
            range_pct=snapshot.range_pct,
            body_pct=snapshot.body_pct,
            session_progress_pct=snapshot.session_progress_pct,
            minutes_from_open=snapshot.minutes_from_open,
            minutes_to_close=snapshot.minutes_to_close,
            event_near=snapshot.event_near,
            expiry_near=snapshot.expiry_near,
            market_id=snapshot.market_id,
            venue_id=snapshot.venue_id,
            timestamp=snapshot.timestamp,
            provenance=provenance,
        )

    # ----------------------------------------------------------------------
    # GENERIC INPUT HELPERS
    # ----------------------------------------------------------------------

    def _to_mapping(self, value: Any) -> Dict[str, Any]:

        if value is None:
            return {}

        if isinstance(value, Mapping):
            return dict(value)

        if is_dataclass(value):
            return asdict(value)

        if hasattr(value, "__dict__"):
            try:
                return dict(vars(value))
            except TypeError:
                pass

        return {}

    def _first(
        self,
        data: Mapping[str, Any],
        *keys: str,
    ) -> Any:

        for key in keys:
            if key in data and data[key] is not None:
                return data[key]

        return None

    def _number(self, value: Any) -> Optional[float]:

        if value is None:
            return None

        if isinstance(value, bool):
            return None

        if isinstance(value, (int, float)):
            number = float(value)
            return number if isfinite(number) else None

        if isinstance(value, str):
            text = value.strip()

            if not text:
                return None

            try:
                number = float(text)
            except ValueError:
                return None

            return number if isfinite(number) else None

        return None

    def _valid_number(self, value: Any) -> bool:

        if value is None:
            return False

        if isinstance(value, bool):
            return False

        try:
            number = float(value)
        except (TypeError, ValueError):
            return False

        return isfinite(number)

    def _boolean(self, value: Any) -> Optional[bool]:

        if value is None:
            return None

        if isinstance(value, bool):
            return value

        if isinstance(value, (int, float)):
            if value == 1:
                return True

            if value == 0:
                return False

        if isinstance(value, str):
            text = value.strip().lower()

            if text in {
                "true",
                "1",
                "yes",
                "y",
                "open",
                "opened",
                "active",
            }:
                return True

            if text in {
                "false",
                "0",
                "no",
                "n",
                "closed",
                "inactive",
            }:
                return False

        return None

    def _string_or_none(self, value: Any) -> Optional[str]:

        if value is None:
            return None

        text = str(value).strip()

        return text if text else None

    # ----------------------------------------------------------------------
    # TEMPORAL HELPERS
    # ----------------------------------------------------------------------

    def _ensure_aware(
        self,
        value: Optional[datetime],
    ) -> Optional[datetime]:
        """
        Ensure datetime is timezone-aware.

        Naive timestamps are interpreted as UTC rather than silently using
        the machine's local timezone. This keeps point-in-time comparisons
        deterministic across environments.
        """

        if value is None:
            return None

        if not isinstance(value, datetime):
            return None

        if value.tzinfo is None or value.utcoffset() is None:
            return value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)

    def _parse_timestamp(
        self,
        value: Any,
    ) -> Optional[datetime]:
        """
        Parse datetime values safely.

        Supported:
            - datetime
            - ISO-8601 string
            - Unix epoch seconds
        """

        if value is None:
            return None

        if isinstance(value, datetime):
            return self._ensure_aware(value)

        if isinstance(value, (int, float)) and not isinstance(value, bool):
            try:
                timestamp = datetime.fromtimestamp(
                    float(value),
                    tz=timezone.utc,
                )
                return timestamp
            except (OverflowError, OSError, ValueError):
                return None

        if isinstance(value, str):
            text = value.strip()

            if not text:
                return None

            if text.endswith("Z"):
                text = text[:-1] + "+00:00"

            try:
                parsed = datetime.fromisoformat(text)
            except ValueError:
                return None

            return self._ensure_aware(parsed)

        return None

    # ----------------------------------------------------------------------
    # STRUCTURE / DIRECTION PARSERS
    # ----------------------------------------------------------------------

    def _parse_structure(
        self,
        value: Any,
    ) -> IntradayStructure:

        if isinstance(value, IntradayStructure):
            return value

        if value is None:
            return IntradayStructure.UNKNOWN

        text = str(value).strip().upper()

        aliases = {
            "TREND": IntradayStructure.TRENDING,
            "TRENDING": IntradayStructure.TRENDING,
            "RANGE": IntradayStructure.RANGE,
            "RANGING": IntradayStructure.RANGE,
            "BREAKOUT": IntradayStructure.BREAKOUT,
            "BREAKDOWN": IntradayStructure.BREAKDOWN,
            "REVERSAL": IntradayStructure.REVERSAL,
            "CHOP": IntradayStructure.CHOPPY,
            "CHOPPY": IntradayStructure.CHOPPY,
            "FLAT": IntradayStructure.FLAT,
            "UNKNOWN": IntradayStructure.UNKNOWN,
        }

        return aliases.get(
            text,
            IntradayStructure.UNKNOWN,
        )

    def _parse_direction(
        self,
        value: Any,
    ) -> IntradayDirection:

        if isinstance(value, IntradayDirection):
            return value

        if value is None:
            return IntradayDirection.UNKNOWN

        text = str(value).strip().upper()

        aliases = {
            "UP": IntradayDirection.UP,
            "BULLISH": IntradayDirection.UP,
            "LONG": IntradayDirection.UP,
            "DOWN": IntradayDirection.DOWN,
            "BEARISH": IntradayDirection.DOWN,
            "SHORT": IntradayDirection.DOWN,
            "NEUTRAL": IntradayDirection.NEUTRAL,
            "FLAT": IntradayDirection.NEUTRAL,
            "UNKNOWN": IntradayDirection.UNKNOWN,
        }

        return aliases.get(
            text,
            IntradayDirection.UNKNOWN,
        )
# ============================================================================
# SERIALIZATION
# ============================================================================

    def snapshot_to_dict(
        self,
        snapshot: Any,
    ) -> Dict[str, Any]:

        normalized = self.normalize(snapshot)

        data = asdict(normalized)

        if normalized.timestamp is not None:
            data["timestamp"] = normalized.timestamp.isoformat()

        if isinstance(normalized.structure, Enum):
            data["structure"] = normalized.structure.value

        if isinstance(normalized.direction, Enum):
            data["direction"] = normalized.direction.value

        return data

    def decision_to_dict(
        self,
        decision: IntradayDecision,
    ) -> Dict[str, Any]:

        data = asdict(decision)

        if isinstance(decision.status, Enum):
            data["status"] = decision.status.value

        if isinstance(decision.condition, Enum):
            data["condition"] = decision.condition.value

        if isinstance(decision.structure, Enum):
            data["structure"] = decision.structure.value

        if isinstance(decision.direction, Enum):
            data["direction"] = decision.direction.value

        if decision.timestamp is not None:
            data["timestamp"] = decision.timestamp.isoformat()

        return data

    def result_to_dict(
        self,
        result: IntradayResult,
    ) -> Dict[str, Any]:

        return {
            "decision": self.decision_to_dict(
                result.decision
            ),
            "snapshot": (
                self.snapshot_to_dict(result.snapshot)
                if result.snapshot is not None
                else None
            ),
            "passed": result.passed,
            "review": result.review,
            "rejected": result.rejected,
            "unknown": result.unknown,
            "metadata": dict(result.metadata),
        }

    # ----------------------------------------------------------------------
    # INSTANCE CONVENIENCE API
    # ----------------------------------------------------------------------

    def evaluate_intraday(
        self,
        snapshot: Any,
        *,
        now: Optional[datetime] = None,
        expected_market_id: Optional[str] = None,
    ) -> IntradayDecision:

        return self.evaluate(
            snapshot,
            now=now,
            expected_market_id=expected_market_id,
        )


# ============================================================================
# MODULE-LEVEL CONVENIENCE APIs
# ============================================================================

def evaluate_intraday(
    snapshot: Any,
    *,
    policy: Optional[IntradayPolicy] = None,
    now: Optional[datetime] = None,
    expected_market_id: Optional[str] = None,
) -> IntradayDecision:
    """
    Stateless convenience API for one intraday observation.
    """

    engine = IntradayEngine(
        policy=policy,
        expected_market_id=expected_market_id,
        now=now,
    )

    return engine.evaluate(
        snapshot,
        now=now,
        expected_market_id=expected_market_id,
    )


def filter_intraday(
    snapshots: Iterable[Any],
    *,
    policy: Optional[IntradayPolicy] = None,
    now: Optional[datetime] = None,
    expected_market_id: Optional[str] = None,
) -> List[IntradayDecision]:
    """
    Stateless convenience API for a collection of observations.
    """

    engine = IntradayEngine(
        policy=policy,
        expected_market_id=expected_market_id,
        now=now,
    )

    return engine.filter(
        snapshots,
        now=now,
        expected_market_id=expected_market_id,
    )


# ============================================================================
# SELF TEST
# ============================================================================

def _self_test() -> None:
    """
    Deterministic structural and behavioral self-test.

    These tests verify:
        - normalization
        - timestamp parsing
        - timezone handling
        - market identity
        - future-data protection
        - basic qualification
        - review behavior
        - collection handling
        - serialization
    """

    test_time = datetime(
        2026,
        9,
        5,
        10,
        30,
        tzinfo=timezone.utc,
    )

    policy = IntradayPolicy(
        policy_version="SELF_TEST",
        minimum_volume_ratio=0.50,
        review_volume_ratio=0.80,
        minimum_turnover_ratio=0.50,
        review_turnover_ratio=0.80,
        minimum_trend_strength=0.20,
        review_trend_strength=0.40,
        minimum_momentum=0.10,
        review_momentum=0.20,
        maximum_range_pct=10.0,
        review_range_pct=5.0,
        stale_after_seconds=300,
        require_price=True,
        reject_future_data=True,
        require_market_match=True,
        review_unknown_structure=True,
        review_unknown_direction=False,
    )

    engine = IntradayEngine(
        policy=policy,
        expected_market_id="NSE",
        now=test_time,
    )

    # ------------------------------------------------------------------
    # TEST 1: Healthy observation
    # ------------------------------------------------------------------

    healthy = IntradaySnapshot(
        instrument_id="NSE-001",
        symbol="TEST",
        timestamp=test_time,
        market_id="NSE",
        venue_id="NSE",
        price=100.0,
        volume=100000.0,
        average_volume=100000.0,
        turnover=10000000.0,
        average_turnover=10000000.0,
        volume_ratio=1.0,
        turnover_ratio=1.0,
        momentum=0.50,
        trend_strength=0.80,
        range_pct=2.0,
        body_pct=1.5,
        structure=IntradayStructure.TRENDING,
        direction=IntradayDirection.UP,
        session_progress_pct=50.0,
        minutes_from_open=75.0,
        minutes_to_close=300.0,
        market_open=True,
        is_trading_day=True,
    )

    decision = engine.evaluate(
        healthy,
        now=test_time,
    )

    assert decision.status == IntradayStatus.PASS
    assert decision.condition in {
        IntradayCondition.EXPANDING,
        IntradayCondition.ACTIVE,
        IntradayCondition.DEVELOPING,
    }

    # ------------------------------------------------------------------
    # TEST 2: Missing price
    # ------------------------------------------------------------------

    missing_price = IntradaySnapshot(
        instrument_id="NSE-002",
        symbol="NOPRICE",
        timestamp=test_time,
        market_id="NSE",
        volume_ratio=1.0,
    )

    decision = engine.evaluate(
        missing_price,
        now=test_time,
    )

    assert decision.status == IntradayStatus.UNKNOWN
    assert decision.condition == IntradayCondition.INSUFFICIENT_DATA

    # ------------------------------------------------------------------
    # TEST 3: Wrong market
    # ------------------------------------------------------------------

    wrong_market = IntradaySnapshot(
        instrument_id="BSE-001",
        symbol="WRONG",
        timestamp=test_time,
        market_id="BSE",
        price=100.0,
        volume_ratio=1.0,
    )

    decision = engine.evaluate(
        wrong_market,
        now=test_time,
    )

    assert decision.status == IntradayStatus.REJECT
    assert "Market identity mismatch" in decision.reasons

    # ------------------------------------------------------------------
    # TEST 4: Future observation
    # ------------------------------------------------------------------

    future_snapshot = IntradaySnapshot(
        instrument_id="NSE-003",
        symbol="FUTURE",
        timestamp=datetime(
            2026,
            9,
            5,
            10,
            31,
            tzinfo=timezone.utc,
        ),
        market_id="NSE",
        price=100.0,
        volume_ratio=1.0,
    )

    decision = engine.evaluate(
        future_snapshot,
        now=test_time,
    )

    assert decision.status == IntradayStatus.REJECT

    # ------------------------------------------------------------------
    # TEST 5: Closed market with permissive policy
    # ------------------------------------------------------------------

    closed_snapshot = IntradaySnapshot(
        instrument_id="NSE-004",
        symbol="CLOSED",
        timestamp=test_time,
        market_id="NSE",
        price=100.0,
        volume_ratio=1.0,
        turnover_ratio=1.0,
        momentum=0.30,
        trend_strength=0.50,
        structure=IntradayStructure.TRENDING,
        market_open=False,
        is_trading_day=True,
    )

    decision = engine.evaluate(
        closed_snapshot,
        now=test_time,
    )

    assert decision.status == IntradayStatus.REVIEW
    assert "Market is currently closed" in decision.warnings

    # ------------------------------------------------------------------
    # TEST 6: Low volume rejection
    # ------------------------------------------------------------------

    low_volume = IntradaySnapshot(
        instrument_id="NSE-005",
        symbol="LOWVOL",
        timestamp=test_time,
        market_id="NSE",
        price=100.0,
        volume_ratio=0.20,
        turnover_ratio=1.0,
        momentum=0.30,
        trend_strength=0.50,
        structure=IntradayStructure.TRENDING,
        market_open=True,
        is_trading_day=True,
    )

    decision = engine.evaluate(
        low_volume,
        now=test_time,
    )

    assert decision.status == IntradayStatus.REJECT
    assert decision.condition == IntradayCondition.WEAK

    # ------------------------------------------------------------------
    # TEST 7: Low turnover rejection
    # ------------------------------------------------------------------

    low_turnover = IntradaySnapshot(
        instrument_id="NSE-006",
        symbol="LOWTURN",
        timestamp=test_time,
        market_id="NSE",
        price=100.0,
        volume_ratio=1.0,
        turnover_ratio=0.20,
        momentum=0.30,
        trend_strength=0.50,
        structure=IntradayStructure.TRENDING,
        market_open=True,
        is_trading_day=True,
    )

    decision = engine.evaluate(
        low_turnover,
        now=test_time,
    )

    assert decision.status == IntradayStatus.REJECT

    # ------------------------------------------------------------------
    # TEST 8: Weak trend
    # ------------------------------------------------------------------

    weak_trend = IntradaySnapshot(
        instrument_id="NSE-007",
        symbol="WEAK",
        timestamp=test_time,
        market_id="NSE",
        price=100.0,
        volume_ratio=1.0,
        turnover_ratio=1.0,
        momentum=0.05,
        trend_strength=0.05,
        structure=IntradayStructure.TRENDING,
        market_open=True,
        is_trading_day=True,
    )

    decision = engine.evaluate(
        weak_trend,
        now=test_time,
    )

    assert decision.status == IntradayStatus.REJECT
    assert decision.condition == IntradayCondition.WEAK

    # ------------------------------------------------------------------
    # TEST 9: Unknown structure produces review
    # ------------------------------------------------------------------

    unknown_structure = IntradaySnapshot(
        instrument_id="NSE-008",
        symbol="UNKNOWNSTRUCT",
        timestamp=test_time,
        market_id="NSE",
        price=100.0,
        volume_ratio=1.0,
        turnover_ratio=1.0,
        momentum=0.30,
        trend_strength=0.50,
        structure=IntradayStructure.UNKNOWN,
        direction=IntradayDirection.UNKNOWN,
        market_open=True,
        is_trading_day=True,
    )

    decision = engine.evaluate(
        unknown_structure,
        now=test_time,
    )

    assert decision.status == IntradayStatus.REVIEW
    assert "Intraday structure is unknown" in decision.warnings

    # ------------------------------------------------------------------
    # TEST 10: Event-near review
    # ------------------------------------------------------------------

    event_near = IntradaySnapshot(
        instrument_id="NSE-009",
        symbol="EVENT",
        timestamp=test_time,
        market_id="NSE",
        price=100.0,
        volume_ratio=1.0,
        turnover_ratio=1.0,
        momentum=0.30,
        trend_strength=0.50,
        structure=IntradayStructure.TRENDING,
        direction=IntradayDirection.UP,
        event_near=True,
        market_open=True,
        is_trading_day=True,
    )

    decision = engine.evaluate(
        event_near,
        now=test_time,
    )

    assert decision.status == IntradayStatus.REVIEW
    assert "Event-near condition" in decision.warnings

    # ------------------------------------------------------------------
    # TEST 11: Expiry-near review
    # ------------------------------------------------------------------

    expiry_near = IntradaySnapshot(
        instrument_id="NSE-010",
        symbol="EXPIRY",
        timestamp=test_time,
        market_id="NSE",
        price=100.0,
        volume_ratio=1.0,
        turnover_ratio=1.0,
        momentum=0.30,
        trend_strength=0.50,
        structure=IntradayStructure.TRENDING,
        direction=IntradayDirection.UP,
        expiry_near=True,
        market_open=True,
        is_trading_day=True,
    )

    decision = engine.evaluate(
        expiry_near,
        now=test_time,
    )

    assert decision.status == IntradayStatus.REVIEW
    assert "Expiry-near condition" in decision.warnings

    # ------------------------------------------------------------------
    # TEST 12: Stale observation
    # ------------------------------------------------------------------

    stale_snapshot = IntradaySnapshot(
        instrument_id="NSE-011",
        symbol="STALE",
        timestamp=datetime(
            2026,
            9,
            5,
            10,
            20,
            tzinfo=timezone.utc,
        ),
        market_id="NSE",
        price=100.0,
        volume_ratio=1.0,
        turnover_ratio=1.0,
        momentum=0.30,
        trend_strength=0.50,
        structure=IntradayStructure.TRENDING,
        market_open=True,
        is_trading_day=True,
    )

    decision = engine.evaluate(
        stale_snapshot,
        now=test_time,
    )

    assert decision.status == IntradayStatus.REVIEW
    assert decision.condition == IntradayCondition.STALE

    # ------------------------------------------------------------------
    # TEST 13: ISO timestamp normalization
    # ------------------------------------------------------------------

    iso_snapshot = {
        "instrument_id": "NSE-012",
        "symbol": "ISO",
        "timestamp": "2026-09-05T10:30:00Z",
        "market_id": "NSE",
        "price": 100,
        "volume_ratio": 1.0,
        "turnover_ratio": 1.0,
        "momentum": 0.30,
        "trend_strength": 0.50,
        "structure": "TRENDING",
        "direction": "UP",
        "market_open": True,
        "is_trading_day": True,
    }

    normalized = engine.normalize(iso_snapshot)

    assert normalized.timestamp is not None
    assert normalized.timestamp.tzinfo is not None
    assert normalized.structure == IntradayStructure.TRENDING
    assert normalized.direction == IntradayDirection.UP

    # ------------------------------------------------------------------
    # TEST 14: Serialization
    # ------------------------------------------------------------------

    serialized_snapshot = engine.snapshot_to_dict(
        normalized
    )

    assert serialized_snapshot["symbol"] == "ISO"
    assert isinstance(
        serialized_snapshot["timestamp"],
        str,
    )

    serialized_decision = engine.decision_to_dict(
        engine.evaluate(
            normalized,
            now=test_time,
        )
    )

    assert "status" in serialized_decision
    assert "condition" in serialized_decision
    assert "provenance" in serialized_decision

    # ------------------------------------------------------------------
    # TEST 15: Collection / generator safety
    # ------------------------------------------------------------------

    collection = (
        item
        for item in [
            healthy,
            low_volume,
            wrong_market,
        ]
    )

    results = engine.apply(
        collection,
        now=test_time,
    )

    assert len(results) == 3
    assert results[0].passed is True
    assert results[1].rejected is True
    assert results[2].rejected is True

    # ------------------------------------------------------------------
    # TEST 16: Naive datetime becomes UTC-aware
    # ------------------------------------------------------------------

    naive = engine._parse_timestamp(
        datetime(
            2026,
            9,
            5,
            10,
            30,
        )
    )

    assert naive is not None
    assert naive.tzinfo == timezone.utc

    # ------------------------------------------------------------------
    # TEST 17: Unix timestamp
    # ------------------------------------------------------------------

    epoch_value = engine._parse_timestamp(
        0
    )

    assert epoch_value is not None
    assert epoch_value.tzinfo is not None

    # ------------------------------------------------------------------
    # TEST 18: Invalid timestamp
    # ------------------------------------------------------------------

    invalid_timestamp = engine._parse_timestamp(
        "not-a-timestamp"
    )

    assert invalid_timestamp is None

    # ------------------------------------------------------------------
    # TEST 19: Invalid numeric value
    # ------------------------------------------------------------------

    invalid_numeric = IntradaySnapshot(
        instrument_id="NSE-013",
        symbol="BADNUM",
        timestamp=test_time,
        market_id="NSE",
        price=100.0,
        volume_ratio=float("nan"),
        turnover_ratio=1.0,
        momentum=0.30,
        trend_strength=0.50,
        structure=IntradayStructure.TRENDING,
        market_open=True,
        is_trading_day=True,
    )

    decision = engine.evaluate(
        invalid_numeric,
        now=test_time,
    )

    assert decision.status == IntradayStatus.REJECT

    # ------------------------------------------------------------------
    # TEST 20: Direction alias normalization
    # ------------------------------------------------------------------

    alias_snapshot = engine.normalize(
        {
            "instrument_id": "NSE-014",
            "symbol": "ALIAS",
            "timestamp": test_time,
            "market_id": "NSE",
            "price": 100.0,
            "structure": "trend",
            "direction": "bullish",
        }
    )

    assert alias_snapshot.structure == IntradayStructure.TRENDING
    assert alias_snapshot.direction == IntradayDirection.UP

    print("intraday_engine.py self-test: PASS")


if __name__ == "__main__":
    _self_test()
# ============================================================================
# END OF INTRADAY ENGINE
# ============================================================================
#
# Part 1:
#   - Core contracts
#   - IntradayEngine.evaluate()
#   - filter()
#   - apply()
#   - normalize()
#   - validation helpers
#   - temporal helpers
#   - structure/direction parsing
#
# Part 2:
#   - serialization
#   - module-level APIs
#   - deterministic self-test
#
# This final section intentionally contains no additional scoring,
# prediction, BUY/SELL generation, or hidden market assumptions.
#
# The engine remains a qualification/measurement component and leaves
# higher-order decision authority to the appropriate ROBOMLM layers.
# ============================================================================


# ============================================================================
# COMPATIBILITY HELPERS
# ============================================================================

def _safe_enum_value(value: Any) -> Any:
    """
    Convert Enum values to their serialized representation.

    Kept module-level for integrations that import this helper while
    remaining intentionally generic.
    """

    if isinstance(value, Enum):
        return value.value

    return value


def _json_safe(value: Any) -> Any:
    """
    Recursively convert engine objects into serialization-safe structures.

    This helper does not alter the underlying intelligence or measurements.
    """

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, datetime):
        aware = value

        if aware.tzinfo is None or aware.utcoffset() is None:
            aware = aware.replace(tzinfo=timezone.utc)
        else:
            aware = aware.astimezone(timezone.utc)

        return aware.isoformat()

    if is_dataclass(value):
        return {
            key: _json_safe(item)
            for key, item in asdict(value).items()
        }

    if isinstance(value, Mapping):
        return {
            str(key): _json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [
            _json_safe(item)
            for item in value
        ]

    return value


# ============================================================================
# OPTIONAL GENERIC SERIALIZATION ENTRY POINT
# ============================================================================

def serialize_intraday(
    value: Any,
) -> Dict[str, Any]:
    """
    Generic serialization entry point.

    Supported values:
        IntradaySnapshot
        IntradayDecision
        IntradayResult
        mapping/dataclass/object

    This function is intentionally non-destructive.
    """

    if isinstance(value, IntradayResult):
        return _json_safe(value)

    if isinstance(value, IntradayDecision):
        return _json_safe(value)

    if isinstance(value, IntradaySnapshot):
        return _json_safe(value)

    if isinstance(value, Mapping):
        return _json_safe(dict(value))

    if is_dataclass(value):
        return _json_safe(value)

    if hasattr(value, "__dict__"):
        try:
            return _json_safe(vars(value))
        except TypeError:
            pass

    return {
        "value": _json_safe(value)
    }


# ============================================================================
# CONTRACT INTROSPECTION
# ============================================================================

def get_intraday_engine_info() -> Dict[str, Any]:
    """
    Return static engine metadata for diagnostics/integration.

    No runtime market data is generated here.
    """

    return {
        "engine_name": IntradayEngine.ENGINE_NAME,
        "engine_version": IntradayEngine.ENGINE_VERSION,
        "purpose": (
            "Point-in-time intraday qualification for "
            "Opportunity Discovery"
        ),
        "decision_authority": False,
        "generates_trade_signal": False,
        "generates_buy_sell": False,
        "predictive_model": False,
        "uses_external_policy": True,
        "future_data_rejected_by_default": True,
        "market_identity_validation": True,
        "provenance_preserved": True,
    }


# ============================================================================
# FINAL STRUCTURAL ASSERTIONS
# ============================================================================

def _structural_check() -> None:
    """
    Lightweight import-time contract verification.

    This is intentionally not executed automatically on import so that
    production imports remain side-effect free.
    """

    required_engine_methods = (
        "evaluate",
        "filter",
        "apply",
        "normalize",
        "_has_observable_intraday_data",
        "_condition",
        "_decision",
        "_to_mapping",
        "_first",
        "_number",
        "_valid_number",
        "_boolean",
        "_string_or_none",
        "_ensure_aware",
        "_parse_timestamp",
        "_parse_structure",
        "_parse_direction",
        "snapshot_to_dict",
        "decision_to_dict",
        "result_to_dict",
        "evaluate_intraday",
    )

    for method_name in required_engine_methods:
        assert hasattr(
            IntradayEngine,
            method_name,
        ), f"Missing IntradayEngine method: {method_name}"

    required_contracts = (
        IntradaySnapshot,
        IntradayDecision,
        IntradayResult,
        IntradayPolicy,
        IntradayStatus,
        IntradayCondition,
        IntradayStructure,
        IntradayDirection,
    )

    for contract in required_contracts:
        assert contract is not None


# ============================================================================
# EXPLICIT MODULE CONTRACT
# ============================================================================

__all__ = [
    "IntradayStatus",
    "IntradayCondition",
    "IntradayStructure",
    "IntradayDirection",
    "IntradaySnapshot",
    "IntradayDecision",
    "IntradayResult",
    "IntradayPolicy",
    "IntradayEngine",
    "evaluate_intraday",
    "filter_intraday",
    "serialize_intraday",
    "get_intraday_engine_info",
]


# ============================================================================
# FINAL SELF-TEST ENTRY
# ============================================================================

if __name__ == "__main__":
    _structural_check()
    _self_test()