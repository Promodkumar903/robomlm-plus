"""
ROBOMLM_PLUS
Opportunity Layer
Risk Filter

Role
----
RiskFilter is an eligibility / risk-screening component.

Pipeline position:

    Evidence / Opportunity Context
                |
                v
           RiskFilter
                |
                v
        Eligibility Result
                |
                v
              CAS

Important boundary rules
------------------------
RiskFilter MUST:
- evaluate externally supplied risk measurements;
- reject unsafe conditions according to an externally supplied policy;
- distinguish PASS / REVIEW / REJECT / UNKNOWN;
- preserve provenance;
- preserve missing-data semantics;
- reject explicitly supplied invalid numeric values.

RiskFilter MUST NOT:
- create BUY / SELL decisions;
- create trade direction;
- create an opportunity score;
- predict price;
- replace D13;
- modify D13;
- create position size;
- create execution authority;
- invent missing risk measurements;
- silently convert invalid supplied measurements into missing values.

Missing vs invalid
------------------
Missing measurement:
    field was not supplied / is None
    -> may result in UNKNOWN depending on policy.

Invalid measurement:
    field was supplied but is not a valid finite numeric value
    -> REJECT.

This distinction is intentional and contractual.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from math import isfinite
from typing import Any, Dict, Iterable, List, Optional


# ============================================================================
# ENUMS
# ============================================================================


class RiskStatus(str, Enum):
    """Final eligibility status produced by RiskFilter."""

    PASS = "PASS"
    REVIEW = "REVIEW"
    REJECT = "REJECT"
    UNKNOWN = "UNKNOWN"


class RiskCondition(str, Enum):
    """Risk severity classification."""

    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    EXTREME = "EXTREME"
    UNKNOWN = "UNKNOWN"


# ============================================================================
# SNAPSHOT CONTRACT
# ============================================================================


@dataclass
class RiskSnapshot:
    """
    Normalized risk observation.

    All measurements are observations supplied to RiskFilter.
    RiskFilter does not manufacture them.
    """

    instrument_id: str
    symbol: str

    timestamp: Optional[datetime] = None

    market_id: Optional[str] = None
    venue_id: Optional[str] = None

    price: Optional[float] = None

    volatility: Optional[float] = None
    volatility_pct: Optional[float] = None

    atr: Optional[float] = None
    atr_pct: Optional[float] = None

    spread_bps: Optional[float] = None
    drawdown_pct: Optional[float] = None

    leverage: Optional[float] = None
    margin_usage_pct: Optional[float] = None

    liquidity_score: Optional[float] = None
    risk_score: Optional[float] = None

    stop_distance_pct: Optional[float] = None
    position_risk_pct: Optional[float] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# DECISION CONTRACT
# ============================================================================


@dataclass
class RiskFilterDecision:
    """Single instrument risk-filter decision."""

    instrument_id: str
    symbol: str

    status: RiskStatus
    condition: RiskCondition

    reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    volatility: Optional[float] = None
    volatility_pct: Optional[float] = None
    atr_pct: Optional[float] = None
    spread_bps: Optional[float] = None
    drawdown_pct: Optional[float] = None
    leverage: Optional[float] = None
    margin_usage_pct: Optional[float] = None
    liquidity_score: Optional[float] = None
    risk_score: Optional[float] = None

    market_id: Optional[str] = None
    timestamp: Optional[datetime] = None

    provenance: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RiskFilterResult:
    """Batch result from RiskFilter.filter()."""

    decisions: List[RiskFilterDecision] = field(default_factory=list)

    passed: List[RiskFilterDecision] = field(default_factory=list)
    review: List[RiskFilterDecision] = field(default_factory=list)
    rejected: List[RiskFilterDecision] = field(default_factory=list)
    unknown: List[RiskFilterDecision] = field(default_factory=list)

    total: int = 0

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# POLICY CONTRACT
# ============================================================================


@dataclass
class RiskPolicy:
    """
    External risk policy.

    None means no threshold is imposed by that particular field.

    RiskPolicy intentionally does not contain trading direction,
    target, entry, stop-generation, position sizing, or execution authority.
    """

    minimum_liquidity_score: Optional[float] = None
    review_liquidity_score: Optional[float] = None

    maximum_volatility_pct: Optional[float] = None
    review_volatility_pct: Optional[float] = None

    maximum_atr_pct: Optional[float] = None
    review_atr_pct: Optional[float] = None

    maximum_spread_bps: Optional[float] = None
    review_spread_bps: Optional[float] = None

    maximum_drawdown_pct: Optional[float] = None
    review_drawdown_pct: Optional[float] = None

    maximum_leverage: Optional[float] = None
    review_leverage: Optional[float] = None

    maximum_margin_usage_pct: Optional[float] = None
    review_margin_usage_pct: Optional[float] = None

    maximum_position_risk_pct: Optional[float] = None
    review_position_risk_pct: Optional[float] = None

    minimum_risk_score: Optional[float] = None
    review_risk_score: Optional[float] = None

    reject_missing_liquidity: bool = False
    reject_missing_volatility: bool = False
    reject_missing_spread: bool = False
    reject_missing_risk_score: bool = False

    require_market_match: bool = True
    reject_future_data: bool = True

    policy_version: str = "EXTERNAL_POLICY_REQUIRED"

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# ENGINE
# ============================================================================


class RiskFilter:
    """
    Risk eligibility engine.

    The engine is intentionally deterministic and policy-driven.
    """

    _NUMERIC_FIELDS = (
        "price",
        "volatility",
        "volatility_pct",
        "atr",
        "atr_pct",
        "spread_bps",
        "drawdown_pct",
        "leverage",
        "margin_usage_pct",
        "liquidity_score",
        "risk_score",
        "stop_distance_pct",
        "position_risk_pct",
    )

    _ALIASES = {
        "instrument": "instrument_id",
        "instrumentId": "instrument_id",
        "symbol_id": "instrument_id",

        "ticker": "symbol",

        "market": "market_id",
        "marketId": "market_id",

        "venue": "venue_id",
        "venueId": "venue_id",

        "time": "timestamp",
        "time_stamp": "timestamp",
        "ts": "timestamp",

        "vol": "volatility",
        "volatilityPercent": "volatility_pct",
        "volatility_percentage": "volatility_pct",

        "atrPercent": "atr_pct",
        "atr_percentage": "atr_pct",

        "spread": "spread_bps",
        "spreadBps": "spread_bps",

        "drawdown": "drawdown_pct",
        "drawdownPercent": "drawdown_pct",

        "marginUsage": "margin_usage_pct",
        "marginUsagePercent": "margin_usage_pct",

        "liquidity": "liquidity_score",
        "liquidityScore": "liquidity_score",

        "risk": "risk_score",
        "riskScore": "risk_score",

        "stopDistance": "stop_distance_pct",
        "positionRisk": "position_risk_pct",
    }

    def __init__(
        self,
        policy: Optional[RiskPolicy] = None,
        expected_market_id: Optional[str] = None,
    ) -> None:
        self.policy = policy or RiskPolicy()
        self.expected_market_id = expected_market_id

    # ========================================================================
    # PUBLIC API
    # ========================================================================

    def evaluate(
        self,
        snapshot: Any,
        *,
        expected_market_id: Optional[str] = None,
        now: Optional[datetime] = None,
    ) -> RiskFilterDecision:
        """
        Evaluate one risk snapshot.

        Contract precedence:

        1. Structural identity
        2. Market identity
        3. Timestamp validity
        4. Explicit invalid numeric data
        5. Missing-data policy
        6. Hard threshold rejection
        7. Review threshold
        8. Unknown if no usable risk measurement exists
        9. Pass
        """

        risk = self.normalize(snapshot)

        warnings: List[str] = []

        # --------------------------------------------------------------------
        # Structural identity
        # --------------------------------------------------------------------

        if not risk.instrument_id:
            return self._decision(
                risk,
                RiskStatus.REJECT,
                RiskCondition.MODERATE,
                ["Missing instrument_id"],
                warnings,
            )

        if not risk.symbol:
            return self._decision(
                risk,
                RiskStatus.REJECT,
                RiskCondition.MODERATE,
                ["Missing symbol"],
                warnings,
            )

        # --------------------------------------------------------------------
        # Market identity
        # --------------------------------------------------------------------

        expected_market = (
            expected_market_id
            if expected_market_id is not None
            else self.expected_market_id
        )

        if self.policy.require_market_match and expected_market:
            if not risk.market_id:
                return self._decision(
                    risk,
                    RiskStatus.REJECT,
                    RiskCondition.MODERATE,
                    ["Missing market_id"],
                    warnings,
                )

            if risk.market_id != expected_market:
                return self._decision(
                    risk,
                    RiskStatus.REJECT,
                    RiskCondition.HIGH,
                    [
                        "Market mismatch",
                        f"expected={expected_market}",
                        f"received={risk.market_id}",
                    ],
                    warnings,
                )

        # --------------------------------------------------------------------
        # Timestamp validation
        # --------------------------------------------------------------------

        current_time = now or datetime.now(timezone.utc)

        if risk.timestamp is not None and self.policy.reject_future_data:
            timestamp = risk.timestamp

            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)

            comparison_now = current_time
            if comparison_now.tzinfo is None:
                comparison_now = comparison_now.replace(tzinfo=timezone.utc)

            if timestamp > comparison_now:
                return self._decision(
                    risk,
                    RiskStatus.REJECT,
                    RiskCondition.HIGH,
                    ["Future-dated risk data"],
                    warnings,
                )

        # --------------------------------------------------------------------
        # INVALID NUMERIC DATA
        #
        # Critical contract:
        #
        # supplied invalid numeric field != missing field
        #
        # NaN / +/-inf / non-numeric supplied value is explicitly rejected.
        # --------------------------------------------------------------------

        invalid_numeric_fields = risk.metadata.get(
            "_invalid_numeric_fields",
            [],
        )

        if invalid_numeric_fields:
            return self._decision(
                risk,
                RiskStatus.REJECT,
                RiskCondition.MODERATE,
                [
                    "Invalid numeric risk fields",
                    ", ".join(invalid_numeric_fields),
                ],
                warnings,
            )

        # --------------------------------------------------------------------
        # Missing-data policy
        # --------------------------------------------------------------------

        if risk.liquidity_score is None:
            if self.policy.reject_missing_liquidity:
                return self._decision(
                    risk,
                    RiskStatus.REJECT,
                    RiskCondition.UNKNOWN,
                    ["Missing liquidity_score"],
                    warnings,
                )

            warnings.append("Missing liquidity_score")

        if risk.volatility_pct is None and risk.volatility is None:
            if self.policy.reject_missing_volatility:
                return self._decision(
                    risk,
                    RiskStatus.REJECT,
                    RiskCondition.UNKNOWN,
                    ["Missing volatility measurement"],
                    warnings,
                )

            warnings.append("Missing volatility measurement")

        if risk.spread_bps is None:
            if self.policy.reject_missing_spread:
                return self._decision(
                    risk,
                    RiskStatus.REJECT,
                    RiskCondition.UNKNOWN,
                    ["Missing spread_bps"],
                    warnings,
                )

            warnings.append("Missing spread_bps")

        if risk.risk_score is None:
            if self.policy.reject_missing_risk_score:
                return self._decision(
                    risk,
                    RiskStatus.REJECT,
                    RiskCondition.UNKNOWN,
                    ["Missing risk_score"],
                    warnings,
                )

            warnings.append("Missing risk_score")

        # --------------------------------------------------------------------
        # Threshold evaluation
        # --------------------------------------------------------------------

        hard_reasons: List[str] = []
        review_reasons: List[str] = []

        # Liquidity
        if risk.liquidity_score is not None:
            if (
                self.policy.minimum_liquidity_score is not None
                and risk.liquidity_score
                < self.policy.minimum_liquidity_score
            ):
                hard_reasons.append(
                    "Liquidity below minimum policy threshold"
                )

            if (
                self.policy.review_liquidity_score is not None
                and risk.liquidity_score
                < self.policy.review_liquidity_score
            ):
                review_reasons.append(
                    "Liquidity below review policy threshold"
                )

        # Volatility
        if risk.volatility_pct is not None:
            if (
                self.policy.maximum_volatility_pct is not None
                and risk.volatility_pct
                > self.policy.maximum_volatility_pct
            ):
                hard_reasons.append(
                    "Volatility above maximum policy threshold"
                )

            if (
                self.policy.review_volatility_pct is not None
                and risk.volatility_pct
                > self.policy.review_volatility_pct
            ):
                review_reasons.append(
                    "Volatility above review policy threshold"
                )

        # ATR
        if risk.atr_pct is not None:
            if (
                self.policy.maximum_atr_pct is not None
                and risk.atr_pct > self.policy.maximum_atr_pct
            ):
                hard_reasons.append(
                    "ATR above maximum policy threshold"
                )

            if (
                self.policy.review_atr_pct is not None
                and risk.atr_pct > self.policy.review_atr_pct
            ):
                review_reasons.append(
                    "ATR above review policy threshold"
                )

        # Spread
        if risk.spread_bps is not None:
            if (
                self.policy.maximum_spread_bps is not None
                and risk.spread_bps > self.policy.maximum_spread_bps
            ):
                hard_reasons.append(
                    "Spread above maximum policy threshold"
                )

            if (
                self.policy.review_spread_bps is not None
                and risk.spread_bps > self.policy.review_spread_bps
            ):
                review_reasons.append(
                    "Spread above review policy threshold"
                )

        # Drawdown
        if risk.drawdown_pct is not None:
            if (
                self.policy.maximum_drawdown_pct is not None
                and risk.drawdown_pct > self.policy.maximum_drawdown_pct
            ):
                hard_reasons.append(
                    "Drawdown above maximum policy threshold"
                )

            if (
                self.policy.review_drawdown_pct is not None
                and risk.drawdown_pct > self.policy.review_drawdown_pct
            ):
                review_reasons.append(
                    "Drawdown above review policy threshold"
                )

        # Leverage
        if risk.leverage is not None:
            if (
                self.policy.maximum_leverage is not None
                and risk.leverage > self.policy.maximum_leverage
            ):
                hard_reasons.append(
                    "Leverage above maximum policy threshold"
                )

            if (
                self.policy.review_leverage is not None
                and risk.leverage > self.policy.review_leverage
            ):
                review_reasons.append(
                    "Leverage above review policy threshold"
                )

        # Margin usage
        if risk.margin_usage_pct is not None:
            if (
                self.policy.maximum_margin_usage_pct is not None
                and risk.margin_usage_pct
                > self.policy.maximum_margin_usage_pct
            ):
                hard_reasons.append(
                    "Margin usage above maximum policy threshold"
                )

            if (
                self.policy.review_margin_usage_pct is not None
                and risk.margin_usage_pct
                > self.policy.review_margin_usage_pct
            ):
                review_reasons.append(
                    "Margin usage above review policy threshold"
                )

        # Position risk
        if risk.position_risk_pct is not None:
            if (
                self.policy.maximum_position_risk_pct is not None
                and risk.position_risk_pct
                > self.policy.maximum_position_risk_pct
            ):
                hard_reasons.append(
                    "Position risk above maximum policy threshold"
                )

            if (
                self.policy.review_position_risk_pct is not None
                and risk.position_risk_pct
                > self.policy.review_position_risk_pct
            ):
                review_reasons.append(
                    "Position risk above review policy threshold"
                )

        # Risk score
        if risk.risk_score is not None:
            if (
                self.policy.minimum_risk_score is not None
                and risk.risk_score < self.policy.minimum_risk_score
            ):
                hard_reasons.append(
                    "Risk score below minimum policy threshold"
                )

            if (
                self.policy.review_risk_score is not None
                and risk.risk_score < self.policy.review_risk_score
            ):
                review_reasons.append(
                    "Risk score below review policy threshold"
                )

        # --------------------------------------------------------------------
        # Condition
        # --------------------------------------------------------------------

        condition = self._condition(risk)

        # --------------------------------------------------------------------
        # Decision precedence
        # --------------------------------------------------------------------

        if hard_reasons:
            return self._decision(
                risk,
                RiskStatus.REJECT,
                condition,
                hard_reasons,
                warnings + review_reasons,
            )

        if review_reasons:
            return self._decision(
                risk,
                RiskStatus.REVIEW,
                condition,
                review_reasons,
                warnings,
            )

        # --------------------------------------------------------------------
        # No observable measurement
        #
        # Missing data is not automatically a rejection unless policy says so.
        # But with no usable risk observation at all, the result is UNKNOWN.
        # --------------------------------------------------------------------

        if not self._has_observable_risk(risk):
            return self._decision(
                risk,
                RiskStatus.UNKNOWN,
                RiskCondition.UNKNOWN,
                ["No usable risk measurement available"],
                warnings,
            )

        return self._decision(
            risk,
            RiskStatus.PASS,
            condition,
            [],
            warnings,
        )

    # ========================================================================

    def filter(
        self,
        snapshots: Iterable[Any],
        *,
        expected_market_id: Optional[str] = None,
        now: Optional[datetime] = None,
    ) -> RiskFilterResult:
        """
        Evaluate a collection of snapshots.

        Exceptions are contained per item and represented as UNKNOWN.
        """

        decisions: List[RiskFilterDecision] = []

        for snapshot in snapshots:
            try:
                decision = self.evaluate(
                    snapshot,
                    expected_market_id=expected_market_id,
                    now=now,
                )
            except Exception as exc:
                try:
                    risk = self.normalize(snapshot)
                except Exception:
                    risk = RiskSnapshot(
                        instrument_id="UNKNOWN",
                        symbol="UNKNOWN",
                    )

                decision = self._decision(
                    risk,
                    RiskStatus.UNKNOWN,
                    RiskCondition.UNKNOWN,
                    ["Risk evaluation failed"],
                    [str(exc)],
                )

            decisions.append(decision)

        return self._build_result(decisions)

    # ========================================================================

    def apply(
        self,
        snapshots: Iterable[Any],
        *,
        expected_market_id: Optional[str] = None,
        now: Optional[datetime] = None,
        include_review: bool = False,
    ) -> List[RiskFilterDecision]:
        """
        Convenience API.

        Default:
            return PASS decisions only.

        include_review=True:
            return PASS + REVIEW decisions.

        REJECT and UNKNOWN are never returned by this convenience method.
        """

        result = self.filter(
            snapshots,
            expected_market_id=expected_market_id,
            now=now,
        )

        if include_review:
            return result.passed + result.review

        return result.passed

    # ========================================================================

    def normalize(self, value: Any) -> RiskSnapshot:
        """
        Normalize an external mapping/object into RiskSnapshot.

        Critical behavior:
        - None means missing.
        - invalid supplied numeric values are recorded in
          `_invalid_numeric_fields`.
        - invalid values are normalized to None only after recording them.
        - RiskFilter.evaluate() subsequently converts those records into REJECT.
        """

        if isinstance(value, RiskSnapshot):
            return value

        if value is None:
            return RiskSnapshot(
                instrument_id="",
                symbol="",
                metadata={
                    "_invalid_numeric_fields": [],
                },
            )

        # --------------------------------------------------------------------
        # Convert arbitrary object to mapping-like source
        # --------------------------------------------------------------------

        if isinstance(value, dict):
            source: Dict[str, Any] = dict(value)
        else:
            source: Dict[str, Any] = {}

            for field_name in (
                "instrument_id",
                "symbol",
                "timestamp",
                "market_id",
                "venue_id",
                *self._NUMERIC_FIELDS,
                "metadata",
            ):
                if hasattr(value, field_name):
                    source[field_name] = getattr(value, field_name)

            if hasattr(value, "__dict__"):
                try:
                    source.update(vars(value))
                except TypeError:
                    pass

        # --------------------------------------------------------------------
        # Apply aliases
        # --------------------------------------------------------------------

        normalized_source: Dict[str, Any] = dict(source)

        for alias, canonical in self._ALIASES.items():
            if canonical not in normalized_source and alias in source:
                normalized_source[canonical] = source[alias]

        # --------------------------------------------------------------------
        # Metadata
        # --------------------------------------------------------------------

        raw_metadata = normalized_source.get("metadata")

        if isinstance(raw_metadata, dict):
            metadata: Dict[str, Any] = dict(raw_metadata)
        else:
            metadata = {}

        # --------------------------------------------------------------------
        # Detect invalid numeric fields BEFORE conversion.
        # --------------------------------------------------------------------

        invalid_numeric_fields: List[str] = []

        numeric_values: Dict[str, Optional[float]] = {}

        for field_name in self._NUMERIC_FIELDS:
            raw_value = normalized_source.get(field_name)

            if raw_value is None:
                numeric_values[field_name] = None
                continue

            if not self._valid_number(raw_value):
                invalid_numeric_fields.append(field_name)
                numeric_values[field_name] = None
                continue

            numeric_values[field_name] = self._number(raw_value)

        metadata["_invalid_numeric_fields"] = invalid_numeric_fields

        # --------------------------------------------------------------------
        # Timestamp
        # --------------------------------------------------------------------

        raw_timestamp = normalized_source.get("timestamp")

        timestamp = self._parse_timestamp(raw_timestamp)

        if raw_timestamp is not None and timestamp is None:
            metadata["_invalid_timestamp"] = True

        # --------------------------------------------------------------------
        # Identity
        # --------------------------------------------------------------------

        instrument_id = normalized_source.get("instrument_id")
        symbol = normalized_source.get("symbol")
        market_id = normalized_source.get("market_id")
        venue_id = normalized_source.get("venue_id")

        # --------------------------------------------------------------------
        # Return normalized contract
        # --------------------------------------------------------------------

        return RiskSnapshot(
            instrument_id=(
                ""
                if instrument_id is None
                else str(instrument_id)
            ),
            symbol=(
                ""
                if symbol is None
                else str(symbol)
            ),
            timestamp=timestamp,
            market_id=(
                None
                if market_id is None
                else str(market_id)
            ),
            venue_id=(
                None
                if venue_id is None
                else str(venue_id)
            ),
            price=numeric_values["price"],
            volatility=numeric_values["volatility"],
            volatility_pct=numeric_values["volatility_pct"],
            atr=numeric_values["atr"],
            atr_pct=numeric_values["atr_pct"],
            spread_bps=numeric_values["spread_bps"],
            drawdown_pct=numeric_values["drawdown_pct"],
            leverage=numeric_values["leverage"],
            margin_usage_pct=numeric_values["margin_usage_pct"],
            liquidity_score=numeric_values["liquidity_score"],
            risk_score=numeric_values["risk_score"],
            stop_distance_pct=numeric_values["stop_distance_pct"],
            position_risk_pct=numeric_values["position_risk_pct"],
            metadata=metadata,
        )

    # ========================================================================
    # INTERNAL DECISION HELPERS
    # ========================================================================

    def _decision(
        self,
        risk: RiskSnapshot,
        status: RiskStatus,
        condition: RiskCondition,
        reasons: List[str],
        warnings: List[str],
    ) -> RiskFilterDecision:
        """Build a contract-compliant RiskFilterDecision."""

        provenance = {
            "engine": "RiskFilter",
            "engine_role": "opportunity_risk_eligibility",
            "policy_version": self.policy.policy_version,
            "market_id_expected": self.expected_market_id,
            "source": risk.metadata.get("source"),
            "source_timestamp": risk.timestamp,
        }

        if "_invalid_numeric_fields" in risk.metadata:
            provenance["invalid_numeric_fields"] = list(
                risk.metadata.get(
                    "_invalid_numeric_fields",
                    [],
                )
            )

        if risk.metadata.get("_invalid_timestamp"):
            provenance["invalid_timestamp"] = True

        return RiskFilterDecision(
            instrument_id=risk.instrument_id,
            symbol=risk.symbol,
            status=status,
            condition=condition,
            reasons=list(reasons),
            warnings=list(warnings),
            volatility=risk.volatility,
            volatility_pct=risk.volatility_pct,
            atr_pct=risk.atr_pct,
            spread_bps=risk.spread_bps,
            drawdown_pct=risk.drawdown_pct,
            leverage=risk.leverage,
            margin_usage_pct=risk.margin_usage_pct,
            liquidity_score=risk.liquidity_score,
            risk_score=risk.risk_score,
            market_id=risk.market_id,
            timestamp=risk.timestamp,
            provenance=provenance,
        )

    # ========================================================================

    def _build_result(
        self,
        decisions: List[RiskFilterDecision],
    ) -> RiskFilterResult:
        """Partition decisions by status."""

        passed = [
            decision
            for decision in decisions
            if decision.status == RiskStatus.PASS
        ]

        review = [
            decision
            for decision in decisions
            if decision.status == RiskStatus.REVIEW
        ]

        rejected = [
            decision
            for decision in decisions
            if decision.status == RiskStatus.REJECT
        ]

        unknown = [
            decision
            for decision in decisions
            if decision.status == RiskStatus.UNKNOWN
        ]

        return RiskFilterResult(
            decisions=decisions,
            passed=passed,
            review=review,
            rejected=rejected,
            unknown=unknown,
            total=len(decisions),
            metadata={
                "engine": "RiskFilter",
                "engine_role": "opportunity_risk_eligibility",
                "policy_version": self.policy.policy_version,
            },
        )

    # ========================================================================
    # RISK CONDITION
    # ========================================================================

    def _condition(
        self,
        risk: RiskSnapshot,
    ) -> RiskCondition:
        """
        Determine risk condition from observable supplied measurements.

        Explicit risk_score takes precedence when present.
        """

        if risk.risk_score is not None:
            if risk.risk_score >= 80:
                return RiskCondition.LOW

            if risk.risk_score >= 60:
                return RiskCondition.MODERATE

            if risk.risk_score >= 40:
                return RiskCondition.HIGH

            return RiskCondition.EXTREME

        levels: List[RiskCondition] = []

        # Volatility / ATR
        volatility_values = [
            value
            for value in (
                risk.volatility_pct,
                risk.atr_pct,
            )
            if value is not None
        ]

        for value in volatility_values:
            if value >= 10:
                levels.append(RiskCondition.EXTREME)
            elif value >= 5:
                levels.append(RiskCondition.HIGH)
            elif value >= 2:
                levels.append(RiskCondition.MODERATE)
            else:
                levels.append(RiskCondition.LOW)

        # Margin usage
        if risk.margin_usage_pct is not None:
            if risk.margin_usage_pct >= 90:
                levels.append(RiskCondition.EXTREME)
            elif risk.margin_usage_pct >= 70:
                levels.append(RiskCondition.HIGH)
            elif risk.margin_usage_pct >= 50:
                levels.append(RiskCondition.MODERATE)
            else:
                levels.append(RiskCondition.LOW)

        # Leverage
        if risk.leverage is not None:
            if risk.leverage >= 20:
                levels.append(RiskCondition.EXTREME)
            elif risk.leverage >= 10:
                levels.append(RiskCondition.HIGH)
            elif risk.leverage >= 5:
                levels.append(RiskCondition.MODERATE)
            else:
                levels.append(RiskCondition.LOW)

        # Spread
        if risk.spread_bps is not None:
            if risk.spread_bps >= 100:
                levels.append(RiskCondition.EXTREME)
            elif risk.spread_bps >= 50:
                levels.append(RiskCondition.HIGH)
            elif risk.spread_bps >= 20:
                levels.append(RiskCondition.MODERATE)
            else:
                levels.append(RiskCondition.LOW)

        # Drawdown
        if risk.drawdown_pct is not None:
            drawdown = abs(risk.drawdown_pct)

            if drawdown >= 20:
                levels.append(RiskCondition.EXTREME)
            elif drawdown >= 10:
                levels.append(RiskCondition.HIGH)
            elif drawdown >= 5:
                levels.append(RiskCondition.MODERATE)
            else:
                levels.append(RiskCondition.LOW)

        if not levels:
            return RiskCondition.UNKNOWN

        severity = {
            RiskCondition.LOW: 0,
            RiskCondition.MODERATE: 1,
            RiskCondition.HIGH: 2,
            RiskCondition.EXTREME: 3,
            RiskCondition.UNKNOWN: -1,
        }

        return max(
            levels,
            key=lambda item: severity[item],
        )

    # ========================================================================

    def _has_observable_risk(
        self,
        risk: RiskSnapshot,
    ) -> bool:
        """Return True when at least one usable risk measurement exists."""

        values = (
            risk.price,
            risk.volatility,
            risk.volatility_pct,
            risk.atr,
            risk.atr_pct,
            risk.spread_bps,
            risk.drawdown_pct,
            risk.leverage,
            risk.margin_usage_pct,
            risk.liquidity_score,
            risk.risk_score,
            risk.stop_distance_pct,
            risk.position_risk_pct,
        )

        return any(
            self._valid_number(value)
            for value in values
        )

    # ========================================================================
    # NUMERIC HELPERS
    # ========================================================================

    @staticmethod
    def _valid_number(value: Any) -> bool:
        """
        Return True only for finite numeric values.

        bool is intentionally rejected.
        """

        if value is None:
            return False

        if isinstance(value, bool):
            return False

        try:
            number = float(value)
        except (TypeError, ValueError):
            return False

        return isfinite(number)

    # ========================================================================

    @staticmethod
    def _number(
        value: Any,
    ) -> Optional[float]:
        """
        Convert a valid numeric value to float.

        Invalid values are returned as None only after normalize()
        has recorded the field in `_invalid_numeric_fields`.
        """

        if value is None:
            return None

        if isinstance(value, bool):
            return None

        try:
            number = float(value)
        except (TypeError, ValueError):
            return None

        if not isfinite(number):
            return None

        return number

    # ========================================================================
    # TIMESTAMP HELPER
    # ========================================================================

    @staticmethod
    def _parse_timestamp(
        value: Any,
    ) -> Optional[datetime]:
        """Normalize supported timestamp representations."""

        if value is None:
            return None

        if isinstance(value, datetime):
            return value

        if isinstance(value, (int, float)) and not isinstance(value, bool):
            try:
                number = float(value)

                if not isfinite(number):
                    return None

                return datetime.fromtimestamp(
                    number,
                    tz=timezone.utc,
                )

            except (
                OverflowError,
                OSError,
                ValueError,
            ):
                return None

        if isinstance(value, str):
            text = value.strip()

            if not text:
                return None

            try:
                return datetime.fromisoformat(
                    text.replace("Z", "+00:00")
                )
            except ValueError:
                return None

        return None


# ============================================================================
# SELF TEST
# ============================================================================


def _self_test() -> None:
    """
    Built-in RiskFilter contract smoke test.

    Critical distinction:

        missing measurement -> UNKNOWN
        invalid supplied numeric -> REJECT
    """

    test_time = datetime.now(timezone.utc)

    # ------------------------------------------------------------------------
    # PASS
    # ------------------------------------------------------------------------

    engine = RiskFilter(
        policy=RiskPolicy(),
        expected_market_id="NSE",
    )

    safe = {
        "instrument_id": "TEST1",
        "symbol": "TEST1",
        "market_id": "NSE",
        "timestamp": test_time,
        "risk_score": 85,
    }

    decision = engine.evaluate(
        safe,
        now=test_time,
    )

    assert decision.status == RiskStatus.PASS
    assert decision.condition == RiskCondition.LOW

    # ------------------------------------------------------------------------
    # REVIEW
    # ------------------------------------------------------------------------

    review_engine = RiskFilter(
        policy=RiskPolicy(
            review_volatility_pct=5,
        ),
        expected_market_id="NSE",
    )

    review_data = {
        "instrument_id": "TEST2",
        "symbol": "TEST2",
        "market_id": "NSE",
        "timestamp": test_time,
        "volatility_pct": 7,
    }

    decision = review_engine.evaluate(
        review_data,
        now=test_time,
    )

    assert decision.status == RiskStatus.REVIEW

    # ------------------------------------------------------------------------
    # REJECT
    # ------------------------------------------------------------------------

    reject_engine = RiskFilter(
        policy=RiskPolicy(
            maximum_volatility_pct=10,
        ),
        expected_market_id="NSE",
    )

    reject_data = {
        "instrument_id": "TEST3",
        "symbol": "TEST3",
        "market_id": "NSE",
        "timestamp": test_time,
        "volatility_pct": 15,
    }

    decision = reject_engine.evaluate(
        reject_data,
        now=test_time,
    )

    assert decision.status == RiskStatus.REJECT

    # ------------------------------------------------------------------------
    # UNKNOWN = genuinely missing risk measurements
    # ------------------------------------------------------------------------

    unknown_data = {
        "instrument_id": "TEST4",
        "symbol": "TEST4",
        "market_id": "NSE",
        "timestamp": test_time,
    }

    decision = engine.evaluate(
        unknown_data,
        now=test_time,
    )

    assert decision.status == RiskStatus.UNKNOWN
    assert (
        "No usable risk measurement available"
        in decision.reasons
    )
    assert decision.condition == RiskCondition.UNKNOWN

    # ------------------------------------------------------------------------
    # MARKET MISMATCH
    # ------------------------------------------------------------------------

    mismatch_data = {
        "instrument_id": "TEST5",
        "symbol": "TEST5",
        "market_id": "BSE",
        "timestamp": test_time,
        "risk_score": 80,
    }

    decision = engine.evaluate(
        mismatch_data,
        now=test_time,
    )

    assert decision.status == RiskStatus.REJECT
    assert "Market mismatch" in decision.reasons

    # ------------------------------------------------------------------------
    # FUTURE TIMESTAMP
    # ------------------------------------------------------------------------

    future_data = {
        "instrument_id": "TEST6",
        "symbol": "TEST6",
        "market_id": "NSE",
        "timestamp": datetime(
            2099,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        "risk_score": 80,
    }

    decision = engine.evaluate(
        future_data,
        now=test_time,
    )

    assert decision.status == RiskStatus.REJECT
    assert "Future-dated risk data" in decision.reasons

    # ------------------------------------------------------------------------
    # INVALID NUMERIC -> REJECT
    # ------------------------------------------------------------------------

    invalid_numeric = {
        "instrument_id": "TEST7",
        "symbol": "TEST7",
        "market_id": "NSE",
        "timestamp": test_time,
        "volatility_pct": float("nan"),
    }

    decision = engine.evaluate(
        invalid_numeric,
        now=test_time,
    )

    assert decision.status == RiskStatus.REJECT
    assert "Invalid numeric risk fields" in decision.reasons
    assert "volatility_pct" in decision.reasons

    # ------------------------------------------------------------------------
    # INVALID STRING NUMERIC -> REJECT
    # ------------------------------------------------------------------------

    invalid_string_numeric = {
        "instrument_id": "TEST8",
        "symbol": "TEST8",
        "market_id": "NSE",
        "timestamp": test_time,
        "risk_score": "not-a-number",
    }

    decision = engine.evaluate(
        invalid_string_numeric,
        now=test_time,
    )

    assert decision.status == RiskStatus.REJECT
    assert "Invalid numeric risk fields" in decision.reasons
    assert "risk_score" in decision.reasons

    # ------------------------------------------------------------------------
    # ALIAS NORMALIZATION
    # ------------------------------------------------------------------------

    alias_data = {
        "instrument": "TEST9",
        "ticker": "TEST9",
        "market": "NSE",
        "riskScore": 90,
        "volatilityPercent": 1.5,
    }

    normalized = engine.normalize(alias_data)

    assert normalized.instrument_id == "TEST9"
    assert normalized.symbol == "TEST9"
    assert normalized.market_id == "NSE"
    assert normalized.risk_score == 90.0
    assert normalized.volatility_pct == 1.5

    # ------------------------------------------------------------------------
    # BATCH RESULT
    # ------------------------------------------------------------------------

    batch = engine.filter(
        [
            safe,
            review_data,
            reject_data,
            unknown_data,
        ],
        now=test_time,
    )

    assert batch.total == 4
    assert len(batch.decisions) == 4

    assert all(
        isinstance(item, RiskFilterDecision)
        for item in batch.decisions
    )

    # ------------------------------------------------------------------------
    # RESULT PARTITION INTEGRITY
    # ------------------------------------------------------------------------

    assert (
        len(batch.passed)
        + len(batch.review)
        + len(batch.rejected)
        + len(batch.unknown)
        == batch.total
    )

    # ------------------------------------------------------------------------
    # APPLY - PASS ONLY
    # ------------------------------------------------------------------------

    applied = engine.apply(
        [
            safe,
            unknown_data,
            reject_data,
        ],
        now=test_time,
    )

    assert all(
        item.status == RiskStatus.PASS
        for item in applied
    )

    # ------------------------------------------------------------------------
    # APPLY - PASS + REVIEW
    # ------------------------------------------------------------------------

    applied_with_review = review_engine.apply(
        [
            safe,
            review_data,
        ],
        now=test_time,
        include_review=True,
    )

    assert all(
        item.status in (
            RiskStatus.PASS,
            RiskStatus.REVIEW,
        )
        for item in applied_with_review
    )


# ============================================================================
# MODULE ENTRY
# ============================================================================


if __name__ == "__main__":
    _self_test()
    print("risk_filter.py self-test: PASS")
