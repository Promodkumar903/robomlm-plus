"""
ROBOMLM_PLUS
Opportunity Intelligence Layer
Risk Filter

Purpose
-------
Risk eligibility/filtering layer for Opportunity Discovery.

Responsibilities
----------------
- Normalize observable risk inputs.
- Validate temporal integrity.
- Validate market/instrument identity.
- Detect missing/invalid risk measurements.
- Apply externally configurable risk policies.
- Produce explainable risk eligibility decisions.
- Preserve provenance.

Non-responsibilities
--------------------
- No BUY/SELL generation.
- No proprietary opportunity score.
- No prediction.
- No replacement for D13 Decision Authority.
- No replacement for D6/D7/D8 intelligence.
- No fabricated risk values.

Engineering principles
----------------------
- Point-in-time only.
- No future-data leakage.
- No silent identity mismatch.
- Missing data is not fabricated.
- Unknown is different from safe.
- Policy thresholds remain externally configurable.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict, is_dataclass
from enum import Enum
from math import isfinite
from typing import Any, Dict, Iterable, List, Mapping, Optional
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# ENUMS
# ---------------------------------------------------------------------------

class RiskStatus(str, Enum):
    PASS = "PASS"
    REVIEW = "REVIEW"
    REJECT = "REJECT"
    UNKNOWN = "UNKNOWN"


class RiskCondition(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    EXTREME = "EXTREME"
    UNKNOWN = "UNKNOWN"


# ---------------------------------------------------------------------------
# DATA CONTRACTS
# ---------------------------------------------------------------------------

@dataclass
class RiskSnapshot:
    """
    Normalized point-in-time risk observation.

    All numeric risk fields are optional because the upstream market
    adapters/evidence engines may not provide every measurement.
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


@dataclass
class RiskFilterDecision:
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
    decisions: List[RiskFilterDecision] = field(default_factory=list)

    passed: List[RiskFilterDecision] = field(default_factory=list)
    review: List[RiskFilterDecision] = field(default_factory=list)
    rejected: List[RiskFilterDecision] = field(default_factory=list)
    unknown: List[RiskFilterDecision] = field(default_factory=list)

    total: int = 0

    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.decisions:
            self.decisions = (
                list(self.passed)
                + list(self.review)
                + list(self.rejected)
                + list(self.unknown)
            )

        self.total = len(self.decisions)

        if not self.passed:
            self.passed = [
                d for d in self.decisions
                if d.status == RiskStatus.PASS
            ]

        if not self.review:
            self.review = [
                d for d in self.decisions
                if d.status == RiskStatus.REVIEW
            ]

        if not self.rejected:
            self.rejected = [
                d for d in self.decisions
                if d.status == RiskStatus.REJECT
            ]

        if not self.unknown:
            self.unknown = [
                d for d in self.decisions
                if d.status == RiskStatus.UNKNOWN
            ]


# ---------------------------------------------------------------------------
# POLICY
# ---------------------------------------------------------------------------

@dataclass
class RiskPolicy:
    """
    External policy configuration.

    None means that this filter does not invent a threshold.

    Threshold semantics:
        reject_* -> hard exclusion
        review_* -> REVIEW classification

    The policy is deliberately configurable so deployment-specific risk
    governance can be supplied without changing intelligence code.
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


# ---------------------------------------------------------------------------
# ENGINE
# ---------------------------------------------------------------------------

class RiskFilter:
    """
    Risk eligibility engine.

    This engine is intentionally a filter/classifier, not a decision engine.
    """

    def __init__(
        self,
        policy: Optional[RiskPolicy] = None,
        expected_market_id: Optional[str] = None,
    ) -> None:
        self.policy = policy or RiskPolicy()
        self.expected_market_id = expected_market_id

    # -----------------------------------------------------------------------
    # PUBLIC API
    # -----------------------------------------------------------------------

    def evaluate(
        self,
        snapshot: Any,
        *,
        expected_market_id: Optional[str] = None,
        now: Optional[datetime] = None,
    ) -> RiskFilterDecision:
        """
        Evaluate one risk snapshot.
        """

        risk = self.normalize(snapshot)

        reasons: List[str] = []
        warnings: List[str] = []

        market_id = expected_market_id or self.expected_market_id

        # ---------------------------------------------------------------
        # Basic identity validation
        # ---------------------------------------------------------------

        if not risk.instrument_id:
            return self._decision(
                risk,
                RiskStatus.REJECT,
                RiskCondition.UNKNOWN,
                ["Missing instrument_id"],
                warnings,
            )

        if not risk.symbol:
            return self._decision(
                risk,
                RiskStatus.REJECT,
                RiskCondition.UNKNOWN,
                ["Missing symbol"],
                warnings,
            )

        # ---------------------------------------------------------------
        # Market identity protection
        # ---------------------------------------------------------------

        if (
            self.policy.require_market_match
            and market_id is not None
            and risk.market_id is not None
            and str(risk.market_id) != str(market_id)
        ):
            return self._decision(
                risk,
                RiskStatus.REJECT,
                RiskCondition.UNKNOWN,
                [
                    "Market identity mismatch",
                    f"expected_market_id={market_id}",
                    f"observed_market_id={risk.market_id}",
                ],
                warnings,
            )

        if (
            self.policy.require_market_match
            and market_id is not None
            and risk.market_id is None
        ):
            return self._decision(
                risk,
                RiskStatus.REJECT,
                RiskCondition.UNKNOWN,
                ["Market identity unavailable"],
                warnings,
            )

        # ---------------------------------------------------------------
        # Timestamp / future-data protection
        # ---------------------------------------------------------------

        if risk.timestamp is not None:
            current_time = now or datetime.now(timezone.utc)

            ts = self._ensure_aware(risk.timestamp)
            current_time = self._ensure_aware(current_time)

            if self.policy.reject_future_data and ts > current_time:
                return self._decision(
                    risk,
                    RiskStatus.REJECT,
                    RiskCondition.UNKNOWN,
                    ["Future-dated risk observation rejected"],
                    warnings,
                )

        # ---------------------------------------------------------------
        # Numeric validation
        # ---------------------------------------------------------------

        numeric_fields = {
            "price": risk.price,
            "volatility": risk.volatility,
            "volatility_pct": risk.volatility_pct,
            "atr": risk.atr,
            "atr_pct": risk.atr_pct,
            "spread_bps": risk.spread_bps,
            "drawdown_pct": risk.drawdown_pct,
            "leverage": risk.leverage,
            "margin_usage_pct": risk.margin_usage_pct,
            "liquidity_score": risk.liquidity_score,
            "risk_score": risk.risk_score,
            "stop_distance_pct": risk.stop_distance_pct,
            "position_risk_pct": risk.position_risk_pct,
        }

        invalid_fields = [
            name
            for name, value in numeric_fields.items()
            if value is not None and not self._valid_number(value)
        ]

        if invalid_fields:
            return self._decision(
                risk,
                RiskStatus.REJECT,
                RiskCondition.UNKNOWN,
                [
                    "Invalid numeric risk fields",
                    ", ".join(invalid_fields),
                ],
                warnings,
            )
        # ---------------------------------------------------------------
        # Missing-data policy checks
        # ---------------------------------------------------------------

        if (
            self.policy.reject_missing_liquidity
            and risk.liquidity_score is None
        ):
            return self._decision(
                risk,
                RiskStatus.REJECT,
                RiskCondition.UNKNOWN,
                ["Liquidity risk measurement unavailable"],
                warnings,
            )

        if (
            self.policy.reject_missing_volatility
            and risk.volatility_pct is None
            and risk.atr_pct is None
            and risk.volatility is None
        ):
            return self._decision(
                risk,
                RiskStatus.REJECT,
                RiskCondition.UNKNOWN,
                ["Volatility measurement unavailable"],
                warnings,
            )

        if (
            self.policy.reject_missing_spread
            and risk.spread_bps is None
        ):
            return self._decision(
                risk,
                RiskStatus.REJECT,
                RiskCondition.UNKNOWN,
                ["Spread measurement unavailable"],
                warnings,
            )

        if (
            self.policy.reject_missing_risk_score
            and risk.risk_score is None
        ):
            return self._decision(
                risk,
                RiskStatus.REJECT,
                RiskCondition.UNKNOWN,
                ["Risk score unavailable"],
                warnings,
            )

        # ---------------------------------------------------------------
        # Threshold evaluation
        # ---------------------------------------------------------------

        hard_reject = False
        review_required = False

        # Liquidity score
        if risk.liquidity_score is not None:
            if (
                self.policy.minimum_liquidity_score is not None
                and risk.liquidity_score
                < self.policy.minimum_liquidity_score
            ):
                hard_reject = True
                reasons.append(
                    "Liquidity score below minimum policy threshold"
                )

            elif (
                self.policy.review_liquidity_score is not None
                and risk.liquidity_score
                < self.policy.review_liquidity_score
            ):
                review_required = True
                warnings.append(
                    "Liquidity score requires review"
                )

        # Volatility percentage
        if risk.volatility_pct is not None:
            if (
                self.policy.maximum_volatility_pct is not None
                and risk.volatility_pct
                > self.policy.maximum_volatility_pct
            ):
                hard_reject = True
                reasons.append(
                    "Volatility exceeds maximum policy threshold"
                )

            elif (
                self.policy.review_volatility_pct is not None
                and risk.volatility_pct
                > self.policy.review_volatility_pct
            ):
                review_required = True
                warnings.append(
                    "Volatility is elevated"
                )

        # ATR percentage
        if risk.atr_pct is not None:
            if (
                self.policy.maximum_atr_pct is not None
                and risk.atr_pct
                > self.policy.maximum_atr_pct
            ):
                hard_reject = True
                reasons.append(
                    "ATR percentage exceeds maximum policy threshold"
                )

            elif (
                self.policy.review_atr_pct is not None
                and risk.atr_pct
                > self.policy.review_atr_pct
            ):
                review_required = True
                warnings.append(
                    "ATR percentage is elevated"
                )

        # Spread
        if risk.spread_bps is not None:
            if (
                self.policy.maximum_spread_bps is not None
                and risk.spread_bps
                > self.policy.maximum_spread_bps
            ):
                hard_reject = True
                reasons.append(
                    "Spread exceeds maximum policy threshold"
                )

            elif (
                self.policy.review_spread_bps is not None
                and risk.spread_bps
                > self.policy.review_spread_bps
            ):
                review_required = True
                warnings.append(
                    "Spread requires review"
                )

        # Drawdown
        if risk.drawdown_pct is not None:
            if (
                self.policy.maximum_drawdown_pct is not None
                and risk.drawdown_pct
                > self.policy.maximum_drawdown_pct
            ):
                hard_reject = True
                reasons.append(
                    "Drawdown exceeds maximum policy threshold"
                )

            elif (
                self.policy.review_drawdown_pct is not None
                and risk.drawdown_pct
                > self.policy.review_drawdown_pct
            ):
                review_required = True
                warnings.append(
                    "Drawdown requires review"
                )

        # Leverage
        if risk.leverage is not None:
            if (
                self.policy.maximum_leverage is not None
                and risk.leverage
                > self.policy.maximum_leverage
            ):
                hard_reject = True
                reasons.append(
                    "Leverage exceeds maximum policy threshold"
                )

            elif (
                self.policy.review_leverage is not None
                and risk.leverage
                > self.policy.review_leverage
            ):
                review_required = True
                warnings.append(
                    "Leverage requires review"
                )

        # Margin usage
        if risk.margin_usage_pct is not None:
            if (
                self.policy.maximum_margin_usage_pct is not None
                and risk.margin_usage_pct
                > self.policy.maximum_margin_usage_pct
            ):
                hard_reject = True
                reasons.append(
                    "Margin usage exceeds maximum policy threshold"
                )

            elif (
                self.policy.review_margin_usage_pct is not None
                and risk.margin_usage_pct
                > self.policy.review_margin_usage_pct
            ):
                review_required = True
                warnings.append(
                    "Margin usage requires review"
                )

        # Position risk
        if risk.position_risk_pct is not None:
            if (
                self.policy.maximum_position_risk_pct is not None
                and risk.position_risk_pct
                > self.policy.maximum_position_risk_pct
            ):
                hard_reject = True
                reasons.append(
                    "Position risk exceeds maximum policy threshold"
                )

            elif (
                self.policy.review_position_risk_pct is not None
                and risk.position_risk_pct
                > self.policy.review_position_risk_pct
            ):
                review_required = True
                warnings.append(
                    "Position risk requires review"
                )

        # Risk score
        if risk.risk_score is not None:
            if (
                self.policy.minimum_risk_score is not None
                and risk.risk_score
                < self.policy.minimum_risk_score
            ):
                hard_reject = True
                reasons.append(
                    "Risk score below minimum policy threshold"
                )

            elif (
                self.policy.review_risk_score is not None
                and risk.risk_score
                < self.policy.review_risk_score
            ):
                review_required = True
                warnings.append(
                    "Risk score requires review"
                )

        # ---------------------------------------------------------------
        # Determine overall condition
        # ---------------------------------------------------------------

        condition = self._condition(risk)

        # Hard policy rejection always wins.
        if hard_reject:
            return self._decision(
                risk,
                RiskStatus.REJECT,
                condition,
                reasons,
                warnings,
            )

        # Review has priority over PASS.
        if review_required:
            return self._decision(
                risk,
                RiskStatus.REVIEW,
                condition,
                reasons,
                warnings,
            )

        # ---------------------------------------------------------------
        # No measurable risk signal
        # ---------------------------------------------------------------

        if not self._has_observable_risk(risk):
            return self._decision(
                risk,
                RiskStatus.UNKNOWN,
                RiskCondition.UNKNOWN,
                ["No usable risk measurement available"],
                warnings,
            )

        # ---------------------------------------------------------------
        # Valid and policy-compliant
        # ---------------------------------------------------------------

        reasons.append("Risk profile satisfies configured policy")

        return self._decision(
            risk,
            RiskStatus.PASS,
            condition,
            reasons,
            warnings,
        )

    # -----------------------------------------------------------------------
    # COLLECTION API
    # -----------------------------------------------------------------------

    def filter(
        self,
        snapshots: Iterable[Any],
        *,
        expected_market_id: Optional[str] = None,
        now: Optional[datetime] = None,
    ) -> RiskFilterResult:
        """
        Evaluate a collection of snapshots.
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
                normalized = self.normalize(snapshot)

                decision = self._decision(
                    normalized,
                    RiskStatus.UNKNOWN,
                    RiskCondition.UNKNOWN,
                    ["Risk evaluation failed"],
                    [f"{type(exc).__name__}: {exc}"],
                )

            decisions.append(decision)

        return self._build_result(decisions)

    def apply(
        self,
        snapshots: Iterable[Any],
        *,
        expected_market_id: Optional[str] = None,
        now: Optional[datetime] = None,
        include_review: bool = False,
    ) -> List[RiskFilterDecision]:
        """
        Return risk-eligible decisions.

        By default only PASS decisions are returned.
        REVIEW can be included explicitly.
        """

        result = self.filter(
            snapshots,
            expected_market_id=expected_market_id,
            now=now,
        )

        if include_review:
            return result.passed + result.review

        return result.passed

    # -----------------------------------------------------------------------
    # NORMALIZATION
    # -----------------------------------------------------------------------

    def normalize(self, value: Any) -> RiskSnapshot:
        """
        Convert Mapping, dataclass, object, or RiskSnapshot into the
        normalized RiskSnapshot contract.
        """

        if isinstance(value, RiskSnapshot):
            return value

        data = self._to_mapping(value)

        instrument_id = self._first(
            data,
            "instrument_id",
            "instrumentId",
            "id",
            default="",
        )

        symbol = self._first(
            data,
            "symbol",
            "ticker",
            "exchange_symbol",
            "exchangeSymbol",
            default="",
        )

        timestamp = self._first(
            data,
            "timestamp",
            "time",
            "observed_at",
            "observedAt",
            default=None,
        )

        timestamp = self._parse_timestamp(timestamp)

        metadata = self._first(
            data,
            "metadata",
            "meta",
            default={},
        )

        if not isinstance(metadata, Mapping):
            metadata = {"raw_metadata": metadata}

        return RiskSnapshot(
            instrument_id=str(instrument_id or ""),
            symbol=str(symbol or ""),
            timestamp=timestamp,

            market_id=self._string_or_none(
                self._first(data, "market_id", "marketId")
            ),
            venue_id=self._string_or_none(
                self._first(data, "venue_id", "venueId")
            ),

            price=self._number(
                self._first(data, "price", "ltp", "last_price")
            ),

            volatility=self._number(
                self._first(data, "volatility", "vol")
            ),
            volatility_pct=self._number(
                self._first(
                    data,
                    "volatility_pct",
                    "volatilityPct",
                    "vol_pct",
                )
            ),

            atr=self._number(
                self._first(data, "atr", "ATR")
            ),
            atr_pct=self._number(
                self._first(data, "atr_pct", "atrPct")
            ),

            spread_bps=self._number(
                self._first(
                    data,
                    "spread_bps",
                    "spreadBps",
                )
            ),

            drawdown_pct=self._number(
                self._first(
                    data,
                    "drawdown_pct",
                    "drawdownPct",
                )
            ),

            leverage=self._number(
                self._first(data, "leverage")
            ),

            margin_usage_pct=self._number(
                self._first(
                    data,
                    "margin_usage_pct",
                    "marginUsagePct",
                )
            ),

            liquidity_score=self._number(
                self._first(
                    data,
                    "liquidity_score",
                    "liquidityScore",
                    "lqs",
                )
            ),

            risk_score=self._number(
                self._first(
                    data,
                    "risk_score",
                    "riskScore",
                )
            ),

            stop_distance_pct=self._number(
                self._first(
                    data,
                    "stop_distance_pct",
                    "stopDistancePct",
                )
            ),

            position_risk_pct=self._number(
                self._first(
                    data,
                    "position_risk_pct",
                    "positionRiskPct",
                )
            ),

            metadata=dict(metadata),
        )

    # -----------------------------------------------------------------------
    # HELPERS
    # -----------------------------------------------------------------------

    def _decision(
        self,
        risk: RiskSnapshot,
        status: RiskStatus,
        condition: RiskCondition,
        reasons: List[str],
        warnings: List[str],
    ) -> RiskFilterDecision:

        provenance = {
            "engine": "RiskFilter",
            "engine_role": "opportunity_risk_eligibility",
            "policy_version": self.policy.policy_version,
            "market_id_expected": self.expected_market_id,
            "source": risk.metadata.get("source"),
            "source_timestamp": risk.metadata.get(
                "source_timestamp"
            ),
        }

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

    def _build_result(
        self,
        decisions: List[RiskFilterDecision],
    ) -> RiskFilterResult:

        passed = [
            d for d in decisions
            if d.status == RiskStatus.PASS
        ]

        review = [
            d for d in decisions
            if d.status == RiskStatus.REVIEW
        ]

        rejected = [
            d for d in decisions
            if d.status == RiskStatus.REJECT
        ]

        unknown = [
            d for d in decisions
            if d.status == RiskStatus.UNKNOWN
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
                "policy_version": self.policy.policy_version,
            },
        )

    def _condition(
        self,
        risk: RiskSnapshot,
    ) -> RiskCondition:

        # Prefer explicit upstream risk score when available.
        if risk.risk_score is not None:
            score = risk.risk_score

            if score >= 80:
                return RiskCondition.LOW
            if score >= 60:
                return RiskCondition.MODERATE
            if score >= 40:
                return RiskCondition.HIGH
            return RiskCondition.EXTREME

        # Otherwise derive a descriptive condition only from observable
        # risk measurements. This is not a proprietary intelligence score.

        extreme = False
        high = False
        moderate = False

        if risk.volatility_pct is not None:
            if risk.volatility_pct >= 10:
                extreme = True
            elif risk.volatility_pct >= 5:
                high = True
            elif risk.volatility_pct >= 2:
                moderate = True

        if risk.atr_pct is not None:
            if risk.atr_pct >= 10:
                extreme = True
            elif risk.atr_pct >= 5:
                high = True
            elif risk.atr_pct >= 2:
                moderate = True

        if risk.margin_usage_pct is not None:
            if risk.margin_usage_pct >= 90:
                extreme = True
            elif risk.margin_usage_pct >= 70:
                high = True
            elif risk.margin_usage_pct >= 50:
                moderate = True

        if risk.leverage is not None:
            if risk.leverage >= 20:
                extreme = True
            elif risk.leverage >= 10:
                high = True
            elif risk.leverage >= 5:
                moderate = True

        if extreme:
            return RiskCondition.EXTREME

        if high:
            return RiskCondition.HIGH

        if moderate:
            return RiskCondition.MODERATE

        if self._has_observable_risk(risk):
            return RiskCondition.LOW

        return RiskCondition.UNKNOWN
    def _has_observable_risk(
        self,
        risk: RiskSnapshot,
    ) -> bool:
        """
        Determine whether at least one usable risk measurement exists.
        """

        fields = (
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
            value is not None and self._valid_number(value)
            for value in fields
        )

    @staticmethod
    def _valid_number(value: Any) -> bool:
        """
        Validate numeric values.

        bool is deliberately rejected because bool is a subclass of int.
        """

        if isinstance(value, bool):
            return False

        try:
            number = float(value)
        except (TypeError, ValueError):
            return False

        return isfinite(number)

    @staticmethod
    def _number(value: Any) -> Optional[float]:
        """
        Convert a value to float when valid.
        Invalid values become None rather than being fabricated.
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

    @staticmethod
    def _string_or_none(value: Any) -> Optional[str]:
        if value is None:
            return None

        text = str(value).strip()

        return text if text else None

    @staticmethod
    def _first(
        data: Mapping[str, Any],
        *keys: str,
        default: Any = None,
    ) -> Any:
        """
        Return the first available key.

        Presence matters: a value of 0 is valid and must not be treated
        as missing.
        """

        for key in keys:
            if key in data:
                return data[key]

        return default

    @staticmethod
    def _to_mapping(value: Any) -> Dict[str, Any]:
        """
        Normalize Mapping, dataclass, or ordinary object.
        """

        if isinstance(value, Mapping):
            return dict(value)

        if is_dataclass(value) and not isinstance(value, type):
            return asdict(value)

        if hasattr(value, "__dict__"):
            return dict(vars(value))

        raise TypeError(
            f"Unsupported risk snapshot type: "
            f"{type(value).__name__}"
        )

    @staticmethod
    def _parse_timestamp(
        value: Any,
    ) -> Optional[datetime]:
        """
        Parse common timestamp representations.

        Unsupported timestamps are treated as unavailable instead of
        inventing a timestamp.
        """

        if value is None:
            return None

        if isinstance(value, datetime):
            return value

        if isinstance(value, (int, float)) and not isinstance(value, bool):
            try:
                return datetime.fromtimestamp(
                    float(value),
                    tz=timezone.utc,
                )
            except (OverflowError, OSError, ValueError):
                return None

        if isinstance(value, str):
            text = value.strip()

            if not text:
                return None

            # ISO-8601 UTC "Z"
            if text.endswith("Z"):
                text = text[:-1] + "+00:00"

            try:
                return datetime.fromisoformat(text)
            except ValueError:
                return None

        return None

    @staticmethod
    def _ensure_aware(
        value: datetime,
    ) -> datetime:
        """
        Convert naive datetime to UTC for safe comparison.
        """

        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)

    # -----------------------------------------------------------------------
    # SERIALIZATION
    # -----------------------------------------------------------------------

    @staticmethod
    def snapshot_to_dict(
        snapshot: RiskSnapshot,
    ) -> Dict[str, Any]:
        data = asdict(snapshot)

        if isinstance(snapshot.timestamp, datetime):
            data["timestamp"] = snapshot.timestamp.isoformat()

        return data

    @staticmethod
    def decision_to_dict(
        decision: RiskFilterDecision,
    ) -> Dict[str, Any]:
        data = asdict(decision)

        data["status"] = decision.status.value
        data["condition"] = decision.condition.value

        if isinstance(decision.timestamp, datetime):
            data["timestamp"] = decision.timestamp.isoformat()

        return data

    @classmethod
    def result_to_dict(
        cls,
        result: RiskFilterResult,
    ) -> Dict[str, Any]:
        return {
            "total": result.total,
            "passed": [
                cls.decision_to_dict(d)
                for d in result.passed
            ],
            "review": [
                cls.decision_to_dict(d)
                for d in result.review
            ],
            "rejected": [
                cls.decision_to_dict(d)
                for d in result.rejected
            ],
            "unknown": [
                cls.decision_to_dict(d)
                for d in result.unknown
            ],
            "metadata": dict(result.metadata),
        }


# ---------------------------------------------------------------------------
# CONVENIENCE API
# ---------------------------------------------------------------------------

def filter_risk(
    snapshots: Iterable[Any],
    policy: Optional[RiskPolicy] = None,
    *,
    expected_market_id: Optional[str] = None,
    now: Optional[datetime] = None,
    include_review: bool = False,
) -> List[RiskFilterDecision]:
    """
    Convenience API for Opportunity Discovery.

    Returns:
        PASS decisions by default.
        PASS + REVIEW when include_review=True.
    """

    engine = RiskFilter(
        policy=policy,
        expected_market_id=expected_market_id,
    )

    return engine.apply(
        snapshots,
        expected_market_id=expected_market_id,
        now=now,
        include_review=include_review,
    )


# ---------------------------------------------------------------------------
# SELF TEST
# ---------------------------------------------------------------------------

def _self_test() -> None:
    """
    Lightweight deterministic tests.

    These tests verify contract behavior only. They do not claim
    market-performance accuracy.
    """

    test_time = datetime(
        2026,
        9,
        5,
        10,
        0,
        0,
        tzinfo=timezone.utc,
    )

    # ---------------------------------------------------------------
    # Test 1: Observable risk + no restrictive policy => PASS
    # ---------------------------------------------------------------

    policy = RiskPolicy(
        policy_version="TEST-1",
    )

    engine = RiskFilter(
        policy=policy,
        expected_market_id="NSE",
    )

    healthy = RiskSnapshot(
        instrument_id="NIFTY",
        symbol="NIFTY",
        market_id="NSE",
        timestamp=test_time,
        volatility_pct=1.5,
        atr_pct=1.2,
        spread_bps=3.0,
        liquidity_score=85.0,
        risk_score=82.0,
    )

    decision = engine.evaluate(
        healthy,
        now=test_time,
    )

    assert decision.status == RiskStatus.PASS
    assert decision.condition == RiskCondition.LOW

    # ---------------------------------------------------------------
    # Test 2: Volatility hard rejection
    # ---------------------------------------------------------------

    policy = RiskPolicy(
        maximum_volatility_pct=5.0,
        policy_version="TEST-2",
    )

    engine = RiskFilter(
        policy=policy,
        expected_market_id="NSE",
    )

    volatile = RiskSnapshot(
        instrument_id="TEST1",
        symbol="TEST1",
        market_id="NSE",
        timestamp=test_time,
        volatility_pct=7.5,
    )

    decision = engine.evaluate(
        volatile,
        now=test_time,
    )

    assert decision.status == RiskStatus.REJECT

    # ---------------------------------------------------------------
    # Test 3: Review threshold
    # ---------------------------------------------------------------

    policy = RiskPolicy(
        maximum_volatility_pct=10.0,
        review_volatility_pct=5.0,
        policy_version="TEST-3",
    )

    engine = RiskFilter(
        policy=policy,
        expected_market_id="NSE",
    )

    elevated = RiskSnapshot(
        instrument_id="TEST2",
        symbol="TEST2",
        market_id="NSE",
        timestamp=test_time,
        volatility_pct=6.0,
    )

    decision = engine.evaluate(
        elevated,
        now=test_time,
    )

    assert decision.status == RiskStatus.REVIEW

    # ---------------------------------------------------------------
    # Test 4: Market identity mismatch
    # ---------------------------------------------------------------

    mismatch = RiskSnapshot(
        instrument_id="TEST3",
        symbol="TEST3",
        market_id="BSE",
        timestamp=test_time,
        volatility_pct=1.0,
    )

    decision = engine.evaluate(
        mismatch,
        now=test_time,
    )

    assert decision.status == RiskStatus.REJECT
    assert "Market identity mismatch" in decision.reasons

    # ---------------------------------------------------------------
    # Test 5: Future data rejection
    # ---------------------------------------------------------------

    future = RiskSnapshot(
        instrument_id="TEST4",
        symbol="TEST4",
        market_id="NSE",
        timestamp=datetime(
            2026,
            9,
            5,
            11,
            0,
            0,
            tzinfo=timezone.utc,
        ),
        volatility_pct=1.0,
    )

    decision = engine.evaluate(
        future,
        now=test_time,
    )

    assert decision.status == RiskStatus.REJECT
    assert "Future-dated risk observation rejected" in decision.reasons

    # ---------------------------------------------------------------
    # Test 6: No measurements => UNKNOWN
    # ---------------------------------------------------------------

    unknown = RiskSnapshot(
        instrument_id="TEST5",
        symbol="TEST5",
        market_id="NSE",
        timestamp=test_time,
    )

    decision = engine.evaluate(
        unknown,
        now=test_time,
    )

    assert decision.status == RiskStatus.UNKNOWN
    assert decision.condition == RiskCondition.UNKNOWN

    # ---------------------------------------------------------------
    # Test 7: Invalid numeric value
    # ---------------------------------------------------------------

    invalid = {
        "instrument_id": "TEST6",
        "symbol": "TEST6",
        "market_id": "NSE",
        "timestamp": test_time,
        "volatility_pct": float("nan"),
    }

    decision = engine.evaluate(
        invalid,
        now=test_time,
    )

    assert decision.status == RiskStatus.UNKNOWN

    # ---------------------------------------------------------------
    # Test 8: Collection filtering
    # ---------------------------------------------------------------

    policy = RiskPolicy(
        maximum_volatility_pct=5.0,
        policy_version="TEST-8",
    )

    engine = RiskFilter(
        policy=policy,
        expected_market_id="NSE",
    )

    collection = [
        RiskSnapshot(
            instrument_id="A",
            symbol="A",
            market_id="NSE",
            timestamp=test_time,
            volatility_pct=2.0,
        ),
        RiskSnapshot(
            instrument_id="B",
            symbol="B",
            market_id="NSE",
            timestamp=test_time,
            volatility_pct=8.0,
        ),
        RiskSnapshot(
            instrument_id="C",
            symbol="C",
            market_id="NSE",
            timestamp=test_time,
        ),
    ]

    result = engine.filter(
        collection,
        now=test_time,
    )

    assert result.total == 3
    assert len(result.passed) == 1
    assert len(result.rejected) == 1
    assert len(result.unknown) == 1

    # ---------------------------------------------------------------
    # Test 9: Serialization
    # ---------------------------------------------------------------

    serialized = engine.result_to_dict(result)

    assert serialized["total"] == 3
    assert isinstance(serialized["passed"], list)
    assert isinstance(serialized["rejected"], list)

    print("risk_filter.py self-test: PASS")


if __name__ == "__main__":
    _self_test()