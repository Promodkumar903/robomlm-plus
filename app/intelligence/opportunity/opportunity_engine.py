"""
ROBOMLM_PLUS - Opportunity Discovery Intelligence
==================================================

Opportunity Engine
------------------

Role
----
The Opportunity Engine is the orchestration layer for Opportunity Discovery.

Pipeline:

    Universe
        ↓
    Liquidity
        ↓
    Risk
        ↓
    Timing
        ↓
    Intraday
        ↓
    Ranking
        ↓
    Opportunity Engine
        ↓
    Opportunity Discovery Output

This engine does NOT:

- invent market data
- replace upstream intelligence engines
- recalculate D6 formulas
- fabricate missing intelligence
- create arbitrary BUY/SELL logic
- act as an execution engine
- override authoritative upstream decisions
- create entry/SL/TP
- silently convert missing evidence into positive evidence

The engine may:

- normalize upstream opportunity candidates
- evaluate opportunity gates
- preserve upstream scores
- optionally calculate a transparent composite from secondary
  intelligence fields when explicitly enabled
- classify opportunity condition
- expose evidence completeness
- produce deterministic ordering
- preserve point-in-time integrity
- preserve market identity
- expose provenance
- filter and rank candidates

Important
---------
Upstream authoritative intelligence remains authoritative.

Primary upstream scores:
    EQE
    PFS
    MCI

Secondary intelligence:
    MTS
    LQS
    RDS
    MCS

Supporting evidence:
    Trend
    Volume
    Liquidity
    Risk
    Timing
    Derivatives
    Participation
    Relationships

No proprietary replacement formula is introduced here.

"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
import math
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
)


# ============================================================================
# ENUMS
# ============================================================================


class OpportunityStatus(str, Enum):
    PASS = "PASS"
    REVIEW = "REVIEW"
    REJECT = "REJECT"
    UNKNOWN = "UNKNOWN"


class OpportunityCondition(str, Enum):
    ACTIONABLE = "ACTIONABLE"
    PROMISING = "PROMISING"
    DEVELOPING = "DEVELOPING"
    FRAGILE = "FRAGILE"
    BLOCKED = "BLOCKED"
    INCOMPLETE = "INCOMPLETE"
    UNKNOWN = "UNKNOWN"


class OpportunityDirection(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"


class OpportunityType(str, Enum):
    BREAKOUT = "BREAKOUT"
    TREND = "TREND"
    REVERSAL = "REVERSAL"
    MOMENTUM = "MOMENTUM"
    MEAN_REVERSION = "MEAN_REVERSION"
    RANGE = "RANGE"
    EXPANSION = "EXPANSION"
    CONTINUATION = "CONTINUATION"
    WATCHLIST = "WATCHLIST"
    UNKNOWN = "UNKNOWN"


class OpportunityBasis(str, Enum):
    UPSTREAM = "UPSTREAM"
    COMPOSITE = "COMPOSITE"
    NONE = "NONE"


class GateStatus(str, Enum):
    PASS = "PASS"
    REVIEW = "REVIEW"
    REJECT = "REJECT"
    UNKNOWN = "UNKNOWN"


# ============================================================================
# DATA CONTRACTS
# ============================================================================


@dataclass(frozen=True)
class OpportunitySnapshot:
    """
    Normalized point-in-time candidate snapshot.

    This is an input contract.

    It contains observable/upstream intelligence only.
    """

    instrument_id: str
    symbol: str

    timestamp: Optional[datetime] = None

    market_id: Optional[str] = None
    venue_id: Optional[str] = None

    # Primary upstream intelligence
    eqe: Optional[float] = None
    pfs: Optional[float] = None
    mci: Optional[float] = None

    # Secondary intelligence
    mts: Optional[float] = None
    lqs: Optional[float] = None
    rds: Optional[float] = None
    mcs: Optional[float] = None

    # Supporting evidence
    trend_strength: Optional[float] = None
    volume_ratio: Optional[float] = None
    liquidity_score: Optional[float] = None
    risk_score: Optional[float] = None
    timing_score: Optional[float] = None
    derivatives_score: Optional[float] = None
    participation_score: Optional[float] = None
    relationship_score: Optional[float] = None

    # Gate information
    eligible: Optional[bool] = None
    liquidity_status: Optional[str] = None
    risk_status: Optional[str] = None
    timing_status: Optional[str] = None
    intraday_status: Optional[str] = None

    # Opportunity metadata
    opportunity_type: OpportunityType = OpportunityType.UNKNOWN
    direction: OpportunityDirection = OpportunityDirection.UNKNOWN

    confidence: Optional[float] = None

    # Informational only. The engine recalculates completeness.
    evidence_completeness: Optional[float] = None

    source: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class OpportunityGate:
    """
    Individual opportunity gate result.
    """

    name: str
    status: GateStatus
    value: Optional[str] = None
    reason: Optional[str] = None


@dataclass(frozen=True)
class OpportunityDecision:
    """
    Final normalized opportunity decision.

    This is NOT an execution instruction.
    """

    instrument_id: str
    symbol: str

    status: OpportunityStatus
    condition: OpportunityCondition

    opportunity_score: Optional[float] = None
    normalized_score: Optional[float] = None

    basis: OpportunityBasis = OpportunityBasis.NONE

    evidence_count: int = 0
    evidence_completeness: float = 0.0

    gates: Tuple[OpportunityGate, ...] = ()

    reasons: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()

    opportunity_type: OpportunityType = OpportunityType.UNKNOWN
    direction: OpportunityDirection = OpportunityDirection.UNKNOWN

    market_id: Optional[str] = None
    timestamp: Optional[datetime] = None

    provenance: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class OpportunityResult:
    """
    Collection-level Opportunity Discovery result.
    """

    status: OpportunityStatus

    decisions: Tuple[OpportunityDecision, ...] = ()

    ranked: Tuple[OpportunityDecision, ...] = ()
    review: Tuple[OpportunityDecision, ...] = ()
    rejected: Tuple[OpportunityDecision, ...] = ()
    unknown: Tuple[OpportunityDecision, ...] = ()

    total_count: int = 0
    pass_count: int = 0
    review_count: int = 0
    reject_count: int = 0
    unknown_count: int = 0

    market_id: Optional[str] = None
    timestamp: Optional[datetime] = None

    provenance: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class OpportunityPolicy:
    """
    Explicit Opportunity Engine policy.

    None means that the corresponding threshold is not imposed locally.

    The engine does not invent defaults for authoritative upstream scores.
    """

    minimum_opportunity_score: Optional[float] = None
    review_opportunity_score: Optional[float] = None

    minimum_evidence_count: int = 1

    minimum_evidence_completeness: Optional[float] = None
    review_evidence_completeness: Optional[float] = None

    require_timestamp: bool = True
    reject_future_data: bool = True
    require_market_match: bool = True

    reject_ineligible: bool = True

    reject_liquidity: bool = True
    reject_risk: bool = True

    reject_timing: bool = False
    reject_intraday: bool = False

    prefer_upstream_scores: bool = True

    # Disabled by default because this must never replace authoritative
    # upstream opportunity intelligence.
    allow_composite_score: bool = False

    allow_unknown_opportunities: bool = True

    tie_break_symbol: bool = True


# ============================================================================
# ENGINE
# ============================================================================


class OpportunityEngine:
    """
    Opportunity Discovery orchestration engine.
    """

    ENGINE_NAME = "OpportunityEngine"
    ENGINE_VERSION = "2.0"

    PRIMARY_SCORE_FIELDS = (
        "eqe",
        "pfs",
        "mci",
    )

    SECONDARY_SCORE_FIELDS = (
        "mts",
        "lqs",
        "rds",
        "mcs",
    )

    EVIDENCE_FIELDS = (
        "trend_strength",
        "volume_ratio",
        "liquidity_score",
        "risk_score",
        "timing_score",
        "derivatives_score",
        "participation_score",
        "relationship_score",
    )

    GATE_FIELDS = (
        "liquidity_status",
        "risk_status",
        "timing_status",
        "intraday_status",
    )

    def __init__(
        self,
        policy: Optional[OpportunityPolicy] = None,
        market_id: Optional[str] = None,
    ) -> None:
        self.policy = policy or OpportunityPolicy()
        self.market_id = market_id

    # ========================================================================
    # NORMALIZATION
    # ========================================================================

    def normalize(
        self,
        candidate: Any,
    ) -> OpportunitySnapshot:
        """
        Normalize mapping/object/snapshot into OpportunitySnapshot.
        """

        if isinstance(candidate, OpportunitySnapshot):
            return candidate

        if isinstance(candidate, Mapping):
            data = dict(candidate)
        else:
            data = {}

            for field_name in OpportunitySnapshot.__dataclass_fields__:
                if hasattr(candidate, field_name):
                    data[field_name] = getattr(candidate, field_name)

            if not data:
                raise TypeError(
                    "Candidate must be OpportunitySnapshot, mapping, "
                    "or object exposing OpportunitySnapshot fields."
                )

        instrument_id = self._string(
            data.get("instrument_id")
            or data.get("id")
            or data.get("instrument")
        )

        symbol = self._string(
            data.get("symbol")
            or data.get("ticker")
            or data.get("name")
        )

        if not instrument_id:
            instrument_id = symbol or "UNKNOWN"

        if not symbol:
            symbol = instrument_id

        timestamp = self._parse_timestamp(
            data.get("timestamp")
            or data.get("time")
            or data.get("as_of")
        )

        opportunity_type = self._enum_value(
            OpportunityType,
            data.get("opportunity_type")
            or data.get("type"),
            OpportunityType.UNKNOWN,
        )

        direction = self._enum_value(
            OpportunityDirection,
            data.get("direction"),
            OpportunityDirection.UNKNOWN,
        )

        metadata = data.get("metadata")

        if not isinstance(metadata, Mapping):
            metadata = {}

        known_fields = set(
            OpportunitySnapshot.__dataclass_fields__.keys()
        )

        extra_metadata = {
            str(key): value
            for key, value in data.items()
            if key not in known_fields
        }

        merged_metadata = dict(metadata)
        merged_metadata.update(extra_metadata)

        return OpportunitySnapshot(
            instrument_id=instrument_id,
            symbol=symbol,
            timestamp=timestamp,
            market_id=self._string(data.get("market_id")),
            venue_id=self._string(data.get("venue_id")),
            eqe=self._number(data.get("eqe")),
            pfs=self._number(data.get("pfs")),
            mci=self._number(data.get("mci")),
            mts=self._number(data.get("mts")),
            lqs=self._number(data.get("lqs")),
            rds=self._number(data.get("rds")),
            mcs=self._number(data.get("mcs")),
            trend_strength=self._number(
                data.get("trend_strength")
            ),
            volume_ratio=self._number(
                data.get("volume_ratio")
            ),
            liquidity_score=self._number(
                data.get("liquidity_score")
            ),
            risk_score=self._number(
                data.get("risk_score")
            ),
            timing_score=self._number(
                data.get("timing_score")
            ),
            derivatives_score=self._number(
                data.get("derivatives_score")
            ),
            participation_score=self._number(
                data.get("participation_score")
            ),
            relationship_score=self._number(
                data.get("relationship_score")
            ),
            eligible=self._boolean_or_none(
                data.get("eligible")
            ),
            liquidity_status=self._string(
                data.get("liquidity_status")
            ),
            risk_status=self._string(
                data.get("risk_status")
            ),
            timing_status=self._string(
                data.get("timing_status")
            ),
            intraday_status=self._string(
                data.get("intraday_status")
            ),
            opportunity_type=opportunity_type,
            direction=direction,
            confidence=self._number(
                data.get("confidence")
            ),
            evidence_completeness=self._number(
                data.get("evidence_completeness")
            ),
            source=self._string(
                data.get("source")
            ),
            metadata=merged_metadata,
        )

    # ========================================================================
    # EVALUATION
    # ========================================================================

    def evaluate(
        self,
        candidate: Any,
    ) -> OpportunityDecision:
        """
        Evaluate a single opportunity candidate.
        """

        snapshot = self.normalize(candidate)

        invalid_fields = self._invalid_numeric_fields(
            snapshot
        )

        if invalid_fields:
            return self._decision(
                snapshot=snapshot,
                status=OpportunityStatus.REJECT,
                condition=OpportunityCondition.BLOCKED,
                score=None,
                basis=OpportunityBasis.NONE,
                gates=(),
                evidence_count=0,
                completeness=0.0,
                reasons=(
                    "Invalid numeric input detected.",
                ),
                warnings=(
                    "Invalid fields: "
                    + ", ".join(invalid_fields),
                ),
            )

        timestamp_issue = self._timestamp_issue(
            snapshot.timestamp
        )

        if timestamp_issue is not None:
            return self._decision(
                snapshot=snapshot,
                status=OpportunityStatus.REJECT,
                condition=OpportunityCondition.BLOCKED,
                score=None,
                basis=OpportunityBasis.NONE,
                gates=(),
                evidence_count=0,
                completeness=0.0,
                reasons=(timestamp_issue,),
                warnings=(),
            )

        if (
            self.policy.require_market_match
            and self.market_id is not None
            and snapshot.market_id is not None
            and snapshot.market_id != self.market_id
        ):
            return self._decision(
                snapshot=snapshot,
                status=OpportunityStatus.REJECT,
                condition=OpportunityCondition.BLOCKED,
                score=None,
                basis=OpportunityBasis.NONE,
                gates=(),
                evidence_count=0,
                completeness=0.0,
                reasons=(
                    "Market identity mismatch.",
                ),
                warnings=(
                    f"Expected market_id={self.market_id!r}, "
                    f"received {snapshot.market_id!r}.",
                ),
            )

        if (
            self.policy.reject_ineligible
            and snapshot.eligible is False
        ):
            return self._decision(
                snapshot=snapshot,
                status=OpportunityStatus.REJECT,
                condition=OpportunityCondition.BLOCKED,
                score=None,
                basis=OpportunityBasis.NONE,
                gates=(),
                evidence_count=0,
                completeness=0.0,
                reasons=(
                    "Candidate is explicitly marked ineligible.",
                ),
                warnings=(),
            )

        score, basis = self._resolve_opportunity_score(
            snapshot
        )

        gates = self._evaluate_gates(snapshot)

        hard_rejections = [
            gate
            for gate in gates
            if gate.status == GateStatus.REJECT
        ]

        if hard_rejections:
            return self._decision(
                snapshot=snapshot,
                status=OpportunityStatus.REJECT,
                condition=OpportunityCondition.BLOCKED,
                score=score,
                basis=basis,
                gates=gates,
                evidence_count=self._evidence_count(
                    snapshot
                ),
                completeness=self._calculate_completeness(
                    snapshot
                ),
                reasons=tuple(
                    gate.reason or f"{gate.name} rejected."
                    for gate in hard_rejections
                ),
                warnings=self._gate_warnings(gates),
            )

        evidence_count = self._evidence_count(
            snapshot
        )

        completeness = self._calculate_completeness(
            snapshot
        )

        condition = self._condition(
            score=score,
            evidence_completeness=completeness,
            gate_statuses=gates,
        )

        status = OpportunityStatus.PASS

        gate_reviews = [
            gate
            for gate in gates
            if gate.status == GateStatus.REVIEW
        ]

        gate_unknowns = [
            gate
            for gate in gates
            if gate.status == GateStatus.UNKNOWN
        ]

        # IMPORTANT:
        # Missing optional gate information is not itself a negative
        # intelligence decision. It becomes a warning only.
        #
        # Explicit REVIEW remains REVIEW.
        if gate_reviews:
            status = OpportunityStatus.REVIEW

        if (
            score is None
            and not self.policy.allow_unknown_opportunities
        ):
            status = OpportunityStatus.UNKNOWN

        if (
            self.policy.minimum_opportunity_score is not None
            and score is not None
            and score < self.policy.minimum_opportunity_score
        ):
            status = OpportunityStatus.REVIEW

        if (
            self.policy.review_opportunity_score is not None
            and score is not None
            and score < self.policy.review_opportunity_score
        ):
            status = OpportunityStatus.REVIEW

        if (
            completeness < 0.50
            and score is None
        ):
            status = OpportunityStatus.UNKNOWN

        reasons = self._build_reasons(
            snapshot=snapshot,
            score=score,
            basis=basis,
            condition=condition,
            completeness=completeness,
        )

        warnings = list(
            self._gate_warnings(gates)
        )

        if gate_unknowns:
            warnings.append(
                "One or more optional gate states are unavailable."
            )

        if (
            completeness < 1.0
            and score is not None
        ):
            warnings.append(
                "Supporting evidence is incomplete; "
                "upstream opportunity intelligence is preserved."
            )

        if evidence_count < self.policy.minimum_evidence_count:
            status = OpportunityStatus.UNKNOWN
            warnings.append(
                "Evidence count is below the configured minimum."
            )

        if (
            self.policy.minimum_evidence_completeness is not None
            and completeness
            < self.policy.minimum_evidence_completeness
        ):
            status = OpportunityStatus.UNKNOWN
            warnings.append(
                "Evidence completeness is below the configured minimum."
            )

        if (
            self.policy.review_evidence_completeness is not None
            and completeness
            < self.policy.review_evidence_completeness
        ):
            if status == OpportunityStatus.PASS:
                status = OpportunityStatus.REVIEW

        return self._decision(
            snapshot=snapshot,
            status=status,
            condition=condition,
            score=score,
            basis=basis,
            gates=gates,
            evidence_count=evidence_count,
            completeness=completeness,
            reasons=tuple(reasons),
            warnings=tuple(
                self._deduplicate_strings(warnings)
            ),
        )

    # ========================================================================
    # SCORE RESOLUTION
    # ========================================================================

    def _resolve_opportunity_score(
        self,
        snapshot: OpportunitySnapshot,
    ) -> Tuple[Optional[float], OpportunityBasis]:
        """
        Resolve the best available opportunity score.

        Priority:
            EQE → PFS → MCI

        Optional composite:
            MTS + LQS + RDS + MCS

        Composite mode is explicitly disabled by default.
        """

        if self.policy.prefer_upstream_scores:
            for field_name in self.PRIMARY_SCORE_FIELDS:
                value = getattr(snapshot, field_name)

                if self._valid_number(value):
                    return (
                        self._normalize_score(value),
                        OpportunityBasis.UPSTREAM,
                    )

        if self.policy.allow_composite_score:
            values = [
                getattr(snapshot, field_name)
                for field_name in self.SECONDARY_SCORE_FIELDS
            ]

            values = [
                self._normalize_score(value)
                for value in values
                if self._valid_number(value)
            ]

            if values:
                return (
                    sum(values) / len(values),
                    OpportunityBasis.COMPOSITE,
                )

        return (
            None,
            OpportunityBasis.NONE,
        )

    # ========================================================================
    # GATES
    # ========================================================================

    def _evaluate_gates(
        self,
        snapshot: OpportunitySnapshot,
    ) -> Tuple[OpportunityGate, ...]:

        return (
            self._build_gate(
                "liquidity",
                snapshot.liquidity_status,
                reject=self.policy.reject_liquidity,
            ),
            self._build_gate(
                "risk",
                snapshot.risk_status,
                reject=self.policy.reject_risk,
            ),
            self._build_gate(
                "timing",
                snapshot.timing_status,
                reject=self.policy.reject_timing,
            ),
            self._build_gate(
                "intraday",
                snapshot.intraday_status,
                reject=self.policy.reject_intraday,
            ),
        )

    def _build_gate(
        self,
        name: str,
        value: Optional[str],
        reject: bool,
    ) -> OpportunityGate:

        if value is None:
            return OpportunityGate(
                name=name,
                status=GateStatus.UNKNOWN,
                value=None,
                reason=None,
            )

        normalized = value.strip().lower()

        if normalized in {
            "pass",
            "passed",
            "healthy",
            "adequate",
            "low",
            "open",
            "active",
            "optimal",
            "safe",
        }:
            return OpportunityGate(
                name=name,
                status=GateStatus.PASS,
                value=value,
                reason=f"{name.capitalize()} gate passed.",
            )

        if normalized in {
            "review",
            "warning",
            "warn",
            "moderate",
            "thin",
            "late",
            "high",
            "event_near",
        }:
            return OpportunityGate(
                name=name,
                status=GateStatus.REVIEW,
                value=value,
                reason=f"{name.capitalize()} gate requires review.",
            )

        if normalized in {
            "reject",
            "rejected",
            "blocked",
            "extreme",
            "poor",
            "fail",
            "failed",
            "closed",
            "outside_window",
        }:
            return OpportunityGate(
                name=name,
                status=(
                    GateStatus.REJECT
                    if reject
                    else GateStatus.REVIEW
                ),
                value=value,
                reason=(
                    f"{name.capitalize()} gate rejected."
                    if reject
                    else (
                        f"{name.capitalize()} gate requires review "
                        f"under current policy."
                    )
                ),
            )

        return OpportunityGate(
            name=name,
            status=GateStatus.UNKNOWN,
            value=value,
            reason=(
                f"{name.capitalize()} gate state is unknown."
            ),
        )

    # ========================================================================
    # CONDITION
    # ========================================================================

    def _condition(
        self,
        score: Optional[float],
        evidence_completeness: float,
        gate_statuses: Sequence[OpportunityGate],
    ) -> OpportunityCondition:

        if score is None:
            return OpportunityCondition.UNKNOWN

        if any(
            gate.status == GateStatus.REJECT
            for gate in gate_statuses
        ):
            return OpportunityCondition.BLOCKED

        if evidence_completeness < 0.50:
            return OpportunityCondition.INCOMPLETE

        if score >= 80.0:
            return OpportunityCondition.ACTIONABLE

        if score >= 65.0:
            return OpportunityCondition.PROMISING

        if score >= 45.0:
            return OpportunityCondition.DEVELOPING

        return OpportunityCondition.FRAGILE

    # ========================================================================
    # EVIDENCE
    # ========================================================================

    def _evidence_count(
        self,
        snapshot: OpportunitySnapshot,
    ) -> int:

        count = 0

        for field_name in self.PRIMARY_SCORE_FIELDS:
            if self._valid_number(
                getattr(snapshot, field_name)
            ):
                count += 1

        for field_name in self.SECONDARY_SCORE_FIELDS:
            if self._valid_number(
                getattr(snapshot, field_name)
            ):
                count += 1

        for field_name in self.EVIDENCE_FIELDS:
            if self._valid_number(
                getattr(snapshot, field_name)
            ):
                count += 1

        if self._valid_number(snapshot.confidence):
            count += 1

        return count

    def _calculate_completeness(
        self,
        snapshot: OpportunitySnapshot,
    ) -> float:

        available = 0

        for field_name in self.EVIDENCE_FIELDS:
            if self._valid_number(
                getattr(snapshot, field_name)
            ):
                available += 1

        total = len(self.EVIDENCE_FIELDS)

        if total == 0:
            return 0.0

        return available / total

    # ========================================================================
    # REASONS / WARNINGS
    # ========================================================================

    def _build_reasons(
        self,
        snapshot: OpportunitySnapshot,
        score: Optional[float],
        basis: OpportunityBasis,
        condition: OpportunityCondition,
        completeness: float,
    ) -> List[str]:

        reasons: List[str] = []

        if score is not None:
            reasons.append(
                f"Opportunity score={score:.4f}."
            )

        if basis == OpportunityBasis.UPSTREAM:
            reasons.append(
                "Score originates from upstream intelligence."
            )

        elif basis == OpportunityBasis.COMPOSITE:
            reasons.append(
                "Score is a configured secondary-field composite."
            )

        if condition == OpportunityCondition.ACTIONABLE:
            reasons.append(
                "Opportunity score is in the actionable range."
            )

        elif condition == OpportunityCondition.PROMISING:
            reasons.append(
                "Opportunity score is in the promising range."
            )

        elif condition == OpportunityCondition.DEVELOPING:
            reasons.append(
                "Opportunity is developing and requires context."
            )

        elif condition == OpportunityCondition.FRAGILE:
            reasons.append(
                "Opportunity strength is fragile."
            )

        elif condition == OpportunityCondition.INCOMPLETE:
            reasons.append(
                "Supporting evidence is incomplete."
            )

        if snapshot.opportunity_type != OpportunityType.UNKNOWN:
            reasons.append(
                "Opportunity type="
                f"{snapshot.opportunity_type.value}."
            )

        if snapshot.direction != OpportunityDirection.UNKNOWN:
            reasons.append(
                "Direction="
                f"{snapshot.direction.value}."
            )

        reasons.append(
            f"Supporting evidence completeness="
            f"{completeness:.2%}."
        )

        return reasons

    def _gate_warnings(
        self,
        gates: Sequence[OpportunityGate],
    ) -> Tuple[str, ...]:

        warnings: List[str] = []

        for gate in gates:
            if gate.status == GateStatus.UNKNOWN:
                warnings.append(
                    f"{gate.name.capitalize()} gate state unavailable."
                )

        return tuple(
            self._deduplicate_strings(warnings)
        )

    # ========================================================================
    # DECISION CONSTRUCTION
    # ========================================================================

    def _decision(
        self,
        snapshot: OpportunitySnapshot,
        status: OpportunityStatus,
        condition: OpportunityCondition,
        score: Optional[float],
        basis: OpportunityBasis,
        gates: Sequence[OpportunityGate],
        evidence_count: int,
        completeness: float,
        reasons: Sequence[str],
        warnings: Sequence[str],
    ) -> OpportunityDecision:

        return OpportunityDecision(
            instrument_id=snapshot.instrument_id,
            symbol=snapshot.symbol,
            status=status,
            condition=condition,
            opportunity_score=score,
            normalized_score=(
                self._normalize_score(score)
                if score is not None
                else None
            ),
            basis=basis,
            evidence_count=evidence_count,
            evidence_completeness=completeness,
            gates=tuple(gates),
            reasons=tuple(
                self._deduplicate_strings(reasons)
            ),
            warnings=tuple(
                self._deduplicate_strings(warnings)
            ),
            opportunity_type=snapshot.opportunity_type,
            direction=snapshot.direction,
            market_id=snapshot.market_id,
            timestamp=snapshot.timestamp,
            provenance=self._build_provenance(
                snapshot=snapshot,
                basis=basis,
            ),
        )

    def _build_provenance(
        self,
        snapshot: OpportunitySnapshot,
        basis: OpportunityBasis,
    ) -> Dict[str, Any]:

        return {
            "engine": self.ENGINE_NAME,
            "engine_version": self.ENGINE_VERSION,
            "basis": basis.value,
            "source": snapshot.source,
            "market_id": snapshot.market_id,
            "venue_id": snapshot.venue_id,
            "timestamp": (
                snapshot.timestamp.isoformat()
                if snapshot.timestamp is not None
                else None
            ),
            "primary_score_fields": list(
                self.PRIMARY_SCORE_FIELDS
            ),
            "secondary_score_fields": list(
                self.SECONDARY_SCORE_FIELDS
            ),
            "evidence_fields": list(
                self.EVIDENCE_FIELDS
            ),
        }

    # ========================================================================
    # COLLECTION EVALUATION
    # ========================================================================

    def evaluate_many(
        self,
        candidates: Iterable[Any],
    ) -> OpportunityResult:

        decisions = tuple(
            self.evaluate(candidate)
            for candidate in candidates
        )

        return self._build_result(decisions)

    def _build_result(
        self,
        decisions: Sequence[OpportunityDecision],
    ) -> OpportunityResult:

        ranked = self.rank(decisions)

        review = tuple(
            decision
            for decision in decisions
            if decision.status == OpportunityStatus.REVIEW
        )

        rejected = tuple(
            decision
            for decision in decisions
            if decision.status == OpportunityStatus.REJECT
        )

        unknown = tuple(
            decision
            for decision in decisions
            if decision.status == OpportunityStatus.UNKNOWN
        )

        pass_items = tuple(
            decision
            for decision in decisions
            if decision.status == OpportunityStatus.PASS
        )

        if rejected and not pass_items and not review:
            collection_status = OpportunityStatus.REJECT
        elif review:
            collection_status = OpportunityStatus.REVIEW
        elif pass_items:
            collection_status = OpportunityStatus.PASS
        elif unknown:
            collection_status = OpportunityStatus.UNKNOWN
        else:
            collection_status = OpportunityStatus.UNKNOWN

        timestamp = self._collection_timestamp(
            decisions
        )

        return OpportunityResult(
            status=collection_status,
            decisions=tuple(decisions),
            ranked=ranked,
            review=review,
            rejected=rejected,
            unknown=unknown,
            total_count=len(decisions),
            pass_count=len(pass_items),
            review_count=len(review),
            reject_count=len(rejected),
            unknown_count=len(unknown),
            market_id=self.market_id,
            timestamp=timestamp,
            provenance={
                "engine": self.ENGINE_NAME,
                "engine_version": self.ENGINE_VERSION,
                "market_id": self.market_id,
                "count": len(decisions),
            },
        )
        return OpportunityResult(
            status=collection_status,
            decisions=tuple(decisions),
            ranked=ranked,
            review=review,
            rejected=rejected,
            unknown=unknown,
            total_count=len(decisions),
            pass_count=len(pass_items),
            review_count=len(review),
            reject_count=len(rejected),
            unknown_count=len(unknown),
            market_id=self.market_id,
            timestamp=timestamp,
            provenance={
                "engine": self.ENGINE_NAME,
                "engine_version": self.ENGINE_VERSION,
                "market_id": self.market_id,
                "count": len(decisions),
            },
        )

    # ========================================================================
    # RANKING
    # ========================================================================

    def rank(
        self,
        decisions: Sequence[OpportunityDecision],
    ) -> Tuple[OpportunityDecision, ...]:
        """
        Deterministic ranking.

        Ordering:

            opportunity_score DESC
            normalized_score DESC
            evidence_completeness DESC
            evidence_count DESC
            instrument_id ASC
            symbol ASC

        Only PASS opportunities are included in ranked output.
        """

        ranked = [
            decision
            for decision in decisions
            if decision.status == OpportunityStatus.PASS
            and decision.opportunity_score is not None
        ]

        ranked.sort(
            key=lambda decision: (
                -(
                    decision.opportunity_score
                    if decision.opportunity_score is not None
                    else float("-inf")
                ),
                -(
                    decision.normalized_score
                    if decision.normalized_score is not None
                    else float("-inf")
                ),
                -decision.evidence_completeness,
                -decision.evidence_count,
                decision.instrument_id,
                decision.symbol,
            )
        )

        result: List[OpportunityDecision] = []

        for rank_number, decision in enumerate(
            ranked,
            start=1,
        ):
            provenance = dict(decision.provenance)
            provenance["rank"] = rank_number

            result.append(
                OpportunityDecision(
                    instrument_id=decision.instrument_id,
                    symbol=decision.symbol,
                    status=decision.status,
                    condition=decision.condition,
                    opportunity_score=decision.opportunity_score,
                    normalized_score=decision.normalized_score,
                    basis=decision.basis,
                    evidence_count=decision.evidence_count,
                    evidence_completeness=decision.evidence_completeness,
                    gates=decision.gates,
                    reasons=decision.reasons,
                    warnings=decision.warnings,
                    opportunity_type=decision.opportunity_type,
                    direction=decision.direction,
                    market_id=decision.market_id,
                    timestamp=decision.timestamp,
                    provenance=provenance,
                )
            )

        return tuple(result)

    def top(
        self,
        decisions: Sequence[OpportunityDecision],
        limit: int = 10,
    ) -> Tuple[OpportunityDecision, ...]:

        if limit <= 0:
            return ()

        return self.rank(decisions)[:limit]

    def filter(
        self,
        decisions: Sequence[OpportunityDecision],
        status: Optional[OpportunityStatus] = None,
        condition: Optional[OpportunityCondition] = None,
        opportunity_type: Optional[OpportunityType] = None,
        direction: Optional[OpportunityDirection] = None,
    ) -> Tuple[OpportunityDecision, ...]:

        result = []

        for decision in decisions:

            if (
                status is not None
                and decision.status != status
            ):
                continue

            if (
                condition is not None
                and decision.condition != condition
            ):
                continue

            if (
                opportunity_type is not None
                and decision.opportunity_type != opportunity_type
            ):
                continue

            if (
                direction is not None
                and decision.direction != direction
            ):
                continue

            result.append(decision)

        return tuple(result)

    # ========================================================================
    # VALIDATION
    # ========================================================================

    def validate_snapshot(
        self,
        snapshot: OpportunitySnapshot,
    ) -> Tuple[str, ...]:
        """
        Validate normalized snapshot integrity.

        Returns a tuple of validation errors.
        Empty tuple means no validation errors.
        """

        errors: List[str] = []

        if not snapshot.instrument_id:
            errors.append(
                "instrument_id is required."
            )

        if not snapshot.symbol:
            errors.append(
                "symbol is required."
            )

        if (
            self.policy.require_timestamp
            and snapshot.timestamp is None
        ):
            errors.append(
                "timestamp is required by policy."
            )

        if (
            snapshot.timestamp is not None
            and not isinstance(snapshot.timestamp, datetime)
        ):
            errors.append(
                "timestamp must be datetime."
            )

        if (
            self.market_id is not None
            and snapshot.market_id is not None
            and snapshot.market_id != self.market_id
        ):
            errors.append(
                "market_id does not match engine market_id."
            )

        invalid_numeric = self._invalid_numeric_fields(
            snapshot
        )

        if invalid_numeric:
            errors.append(
                "Invalid numeric fields: "
                + ", ".join(invalid_numeric)
            )

        return tuple(errors)

    # ========================================================================
    # SERIALIZATION
    # ========================================================================

    def serialize_decision(
        self,
        decision: OpportunityDecision,
    ) -> Dict[str, Any]:

        payload = asdict(decision)

        payload["status"] = decision.status.value
        payload["condition"] = decision.condition.value
        payload["basis"] = decision.basis.value
        payload["opportunity_type"] = (
            decision.opportunity_type.value
        )
        payload["direction"] = (
            decision.direction.value
        )

        payload["gates"] = [
            {
                "name": gate.name,
                "status": gate.status.value,
                "value": gate.value,
                "reason": gate.reason,
            }
            for gate in decision.gates
        ]

        if decision.timestamp is not None:
            payload["timestamp"] = (
                decision.timestamp.isoformat()
            )

        return self._json_safe(payload)

    def serialize_result(
        self,
        result: OpportunityResult,
    ) -> Dict[str, Any]:

        payload = asdict(result)

        payload["status"] = result.status.value

        payload["decisions"] = [
            self.serialize_decision(decision)
            for decision in result.decisions
        ]

        payload["ranked"] = [
            self.serialize_decision(decision)
            for decision in result.ranked
        ]

        payload["review"] = [
            self.serialize_decision(decision)
            for decision in result.review
        ]

        payload["rejected"] = [
            self.serialize_decision(decision)
            for decision in result.rejected
        ]

        payload["unknown"] = [
            self.serialize_decision(decision)
            for decision in result.unknown
        ]

        if result.timestamp is not None:
            payload["timestamp"] = (
                result.timestamp.isoformat()
            )

        return self._json_safe(payload)

    # ========================================================================
    # ENGINE INFO
    # ========================================================================

    def get_engine_info(self) -> Dict[str, Any]:

        return {
            "engine": self.ENGINE_NAME,
            "engine_version": self.ENGINE_VERSION,
            "role": "Opportunity Discovery orchestration",
            "primary_scores": list(
                self.PRIMARY_SCORE_FIELDS
            ),
            "secondary_scores": list(
                self.SECONDARY_SCORE_FIELDS
            ),
            "evidence_fields": list(
                self.EVIDENCE_FIELDS
            ),
            "gate_fields": list(
                self.GATE_FIELDS
            ),
            "composite_enabled": (
                self.policy.allow_composite_score
            ),
            "market_id": self.market_id,
        }

    # ========================================================================
    # HELPERS
    # ========================================================================

    @staticmethod
    def _valid_number(
        value: Any,
    ) -> bool:

        if isinstance(value, bool):
            return False

        if not isinstance(value, (int, float)):
            return False

        return math.isfinite(float(value))

    @staticmethod
    def _number(
        value: Any,
    ) -> Optional[float]:

        if value is None:
            return None

        if isinstance(value, bool):
            return None

        try:
            number = float(value)
        except (TypeError, ValueError):
            return None

        if not math.isfinite(number):
            return None

        return number

    @staticmethod
    def _normalize_score(
        value: Optional[float],
    ) -> Optional[float]:

        if value is None:
            return None

        if not OpportunityEngine._valid_number(value):
            return None

        score = float(value)

        # Scores are expected to be in the standard 0-100 range.
        # Values outside that range are not silently clipped.
        if score < 0.0 or score > 100.0:
            return None

        return score

    @staticmethod
    def _boolean_or_none(
        value: Any,
    ) -> Optional[bool]:

        if value is None:
            return None

        if isinstance(value, bool):
            return value

        if isinstance(value, str):

            normalized = value.strip().lower()

            if normalized in {
                "true",
                "1",
                "yes",
                "y",
                "pass",
                "eligible",
            }:
                return True

            if normalized in {
                "false",
                "0",
                "no",
                "n",
                "fail",
                "blocked",
                "reject",
                "ineligible",
            }:
                return False

        if isinstance(value, (int, float)):

            if value == 1:
                return True

            if value == 0:
                return False

        return None

    @staticmethod
    def _ensure_aware(
        value: datetime,
    ) -> datetime:

        if value.tzinfo is None:
            return value.replace(
                tzinfo=timezone.utc
            )

        return value.astimezone(
            timezone.utc
        )

    @classmethod
    def _parse_timestamp(
        cls,
        value: Any,
    ) -> Optional[datetime]:

        if value is None:
            return None

        if isinstance(value, datetime):
            return cls._ensure_aware(value)

        if isinstance(value, (int, float)):
            if not math.isfinite(float(value)):
                return None

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

            if text.endswith("Z"):
                text = text[:-1] + "+00:00"

            try:
                parsed = datetime.fromisoformat(text)
            except ValueError:
                return None

            return cls._ensure_aware(parsed)

        return None

    @staticmethod
    def _string(
        value: Any,
    ) -> Optional[str]:

        if value is None:
            return None

        if isinstance(value, str):
            text = value.strip()

            return text if text else None

        return str(value)

    @staticmethod
    def _enum_value(
        enum_cls: Any,
        value: Any,
        default: Any,
    ) -> Any:

        if isinstance(value, enum_cls):
            return value

        if value is None:
            return default

        if isinstance(value, str):

            normalized = value.strip().upper()

            for member in enum_cls:

                if normalized in {
                    member.name.upper(),
                    str(member.value).upper(),
                }:
                    return member

        return default

    @staticmethod
    def _deduplicate_strings(
        values: Iterable[str],
    ) -> List[str]:

        result: List[str] = []
        seen = set()

        for value in values:

            if not value:
                continue

            if value in seen:
                continue

            seen.add(value)
            result.append(value)

        return result

    @classmethod
    def _invalid_numeric_fields(
        cls,
        snapshot: OpportunitySnapshot,
    ) -> Tuple[str, ...]:

        invalid = []

        numeric_fields = (
            *cls.PRIMARY_SCORE_FIELDS,
            *cls.SECONDARY_SCORE_FIELDS,
            *cls.EVIDENCE_FIELDS,
            "confidence",
            "evidence_completeness",
        )

        for field_name in numeric_fields:

            value = getattr(
                snapshot,
                field_name,
            )

            if value is None:
                continue

            if not cls._valid_number(value):
                invalid.append(field_name)

        return tuple(invalid)

    def _timestamp_issue(
        self,
        timestamp: Optional[datetime],
    ) -> Optional[str]:

        if (
            self.policy.require_timestamp
            and timestamp is None
        ):
            return "Timestamp is required by policy."

        if timestamp is None:
            return None

        aware_timestamp = self._ensure_aware(
            timestamp
        )

        if (
            self.policy.reject_future_data
            and aware_timestamp > datetime.now(
                timezone.utc
            )
        ):
            return "Future-dated market data is not accepted."

        return None

    @staticmethod
    def _collection_timestamp(
        decisions: Sequence[OpportunityDecision],
    ) -> Optional[datetime]:

        timestamps = [
            decision.timestamp
            for decision in decisions
            if decision.timestamp is not None
        ]

        if not timestamps:
            return None

        return max(timestamps)

    @classmethod
    def _json_safe(
        cls,
        value: Any,
    ) -> Any:

        if isinstance(value, Enum):
            return value.value

        if isinstance(value, datetime):
            return value.isoformat()

        if isinstance(value, Mapping):
            return {
                str(key): cls._json_safe(item)
                for key, item in value.items()
            }

        if isinstance(value, (list, tuple)):
            return [
                cls._json_safe(item)
                for item in value
            ]

        if isinstance(value, float):

            if not math.isfinite(value):
                return None

            return value

        return value
# ============================================================================
# MODULE-LEVEL API
# ============================================================================


def evaluate_opportunity(
    candidate: Any,
    policy: Optional[OpportunityPolicy] = None,
    market_id: Optional[str] = None,
) -> OpportunityDecision:
    """
    Evaluate one opportunity candidate.
    """

    engine = OpportunityEngine(
        policy=policy,
        market_id=market_id,
    )

    return engine.evaluate(candidate)


def evaluate_opportunities(
    candidates: Iterable[Any],
    policy: Optional[OpportunityPolicy] = None,
    market_id: Optional[str] = None,
) -> OpportunityResult:
    """
    Evaluate a collection of opportunity candidates.
    """

    engine = OpportunityEngine(
        policy=policy,
        market_id=market_id,
    )

    return engine.evaluate_many(candidates)


def discover_opportunities(
    candidates: Iterable[Any],
    policy: Optional[OpportunityPolicy] = None,
    market_id: Optional[str] = None,
) -> OpportunityResult:
    """
    Public Opportunity Discovery entry point.
    """

    return evaluate_opportunities(
        candidates=candidates,
        policy=policy,
        market_id=market_id,
    )


def top_opportunities(
    decisions: Sequence[OpportunityDecision],
    limit: int = 10,
    policy: Optional[OpportunityPolicy] = None,
    market_id: Optional[str] = None,
) -> Tuple[OpportunityDecision, ...]:
    """
    Return deterministic top opportunities.
    """

    engine = OpportunityEngine(
        policy=policy,
        market_id=market_id,
    )

    return engine.top(
        decisions,
        limit=limit,
    )


def filter_opportunities(
    decisions: Sequence[OpportunityDecision],
    status: Optional[OpportunityStatus] = None,
    condition: Optional[OpportunityCondition] = None,
    opportunity_type: Optional[OpportunityType] = None,
    direction: Optional[OpportunityDirection] = None,
    policy: Optional[OpportunityPolicy] = None,
    market_id: Optional[str] = None,
) -> Tuple[OpportunityDecision, ...]:
    """
    Filter evaluated opportunities.
    """

    engine = OpportunityEngine(
        policy=policy,
        market_id=market_id,
    )

    return engine.filter(
        decisions=decisions,
        status=status,
        condition=condition,
        opportunity_type=opportunity_type,
        direction=direction,
    )


def serialize_opportunity_decision(
    decision: OpportunityDecision,
) -> Dict[str, Any]:
    """
    Serialize one OpportunityDecision.
    """

    engine = OpportunityEngine()

    return engine.serialize_decision(
        decision
    )


def serialize_opportunity_result(
    result: OpportunityResult,
) -> Dict[str, Any]:
    """
    Serialize one OpportunityResult.
    """

    engine = OpportunityEngine()

    return engine.serialize_result(
        result
    )


# ============================================================================
# SELF TEST
# ============================================================================


def _self_test() -> None:
    """
    Internal deterministic contract tests.

    These tests verify:

    - normalization
    - point-in-time protection
    - market identity
    - upstream score preference
    - secondary score behavior
    - composite behavior
    - gate handling
    - evidence completeness
    - deterministic ranking
    - filtering
    - serialization
    - no execution fields
    """

    now = datetime.now(timezone.utc)

    engine = OpportunityEngine(
        market_id="NSE",
    )

    # ------------------------------------------------------------------------
    # 1. Basic normalization
    # ------------------------------------------------------------------------

    candidate = {
        "instrument_id": "NIFTY001",
        "symbol": "NIFTY",
        "timestamp": now.isoformat(),
        "market_id": "NSE",
        "eqe": 88,
        "opportunity_type": "BREAKOUT",
        "direction": "LONG",
        "confidence": 91,
        "trend_strength": 82,
        "volume_ratio": 1.8,
        "liquidity_score": 88,
        "risk_score": 28,
        "timing_score": 80,
        "derivatives_score": 86,
        "participation_score": 84,
        "relationship_score": 79,
    }

    normalized = engine.normalize(
        candidate
    )

    assert isinstance(
        normalized,
        OpportunitySnapshot,
    )

    assert normalized.instrument_id == "NIFTY001"
    assert normalized.symbol == "NIFTY"
    assert normalized.eqe == 88.0
    assert normalized.market_id == "NSE"
    assert normalized.direction == OpportunityDirection.LONG
    assert normalized.opportunity_type == OpportunityType.BREAKOUT

    # ------------------------------------------------------------------------
    # 2. Strong upstream opportunity
    # ------------------------------------------------------------------------

    strong = engine.evaluate(
        candidate
    )

    assert strong.status == OpportunityStatus.PASS
    assert strong.condition == OpportunityCondition.ACTIONABLE
    assert strong.opportunity_score == 88.0
    assert strong.basis == OpportunityBasis.UPSTREAM
    assert strong.evidence_completeness == 1.0
    assert strong.evidence_count >= 9

    # ------------------------------------------------------------------------
    # 3. PFS is used when EQE is unavailable
    # ------------------------------------------------------------------------

    pfs_candidate = {
        "instrument_id": "BANK001",
        "symbol": "BANKNIFTY",
        "timestamp": now,
        "market_id": "NSE",
        "pfs": 72,
        "trend_strength": 70,
        "volume_ratio": 1.4,
        "liquidity_score": 75,
        "risk_score": 35,
    }

    pfs_result = engine.evaluate(
        pfs_candidate
    )

    assert pfs_result.status == OpportunityStatus.PASS
    assert pfs_result.opportunity_score == 72.0
    assert pfs_result.basis == OpportunityBasis.UPSTREAM

    # ------------------------------------------------------------------------
    # 4. MCI is used when EQE and PFS are unavailable
    # ------------------------------------------------------------------------

    mci_candidate = {
        "instrument_id": "MCI001",
        "symbol": "MCI-ASSET",
        "timestamp": now,
        "market_id": "NSE",
        "mci": 66,
        "trend_strength": 71,
        "volume_ratio": 1.2,
    }

    mci_result = engine.evaluate(
        mci_candidate
    )

    assert mci_result.status == OpportunityStatus.PASS
    assert mci_result.opportunity_score == 66.0
    assert mci_result.basis == OpportunityBasis.UPSTREAM
    assert (
        mci_result.condition
        == OpportunityCondition.INCOMPLETE
    )

    # ------------------------------------------------------------------------
    # 5. Secondary-only candidate does not become a score by default
    # ------------------------------------------------------------------------

    secondary_only = {
        "instrument_id": "SEC001",
        "symbol": "SECONDARY",
        "timestamp": now,
        "market_id": "NSE",
        "mts": 90,
        "lqs": 88,
        "rds": 85,
        "mcs": 87,
    }

    secondary_result = engine.evaluate(
        secondary_only
    )

    assert (
        secondary_result.opportunity_score
        is None
    )
    assert (
        secondary_result.basis
        == OpportunityBasis.NONE
    )

    # ------------------------------------------------------------------------
    # 6. Composite remains opt-in
    # ------------------------------------------------------------------------

    composite_engine = OpportunityEngine(
        policy=OpportunityPolicy(
            allow_composite_score=True,
        ),
        market_id="NSE",
    )

    composite = composite_engine.evaluate(
        secondary_only
    )

    assert composite.status == OpportunityStatus.PASS
    assert composite.opportunity_score == 87.5
    assert (
        composite.basis
        == OpportunityBasis.COMPOSITE
    )

    # ------------------------------------------------------------------------
    # 7. Explicit liquidity rejection
    # ------------------------------------------------------------------------

    liquidity_reject = {
        "instrument_id": "LIQ001",
        "symbol": "THIN",
        "timestamp": now,
        "market_id": "NSE",
        "eqe": 90,
        "liquidity_status": "REJECT",
    }

    liquidity_result = engine.evaluate(
        liquidity_reject
    )

    assert (
        liquidity_result.status
        == OpportunityStatus.REJECT
    )

    assert (
        liquidity_result.condition
        == OpportunityCondition.BLOCKED
    )

    # ------------------------------------------------------------------------
    # 8. Explicit risk rejection
    # ------------------------------------------------------------------------

    risk_reject = {
        "instrument_id": "RISK001",
        "symbol": "RISKY",
        "timestamp": now,
        "market_id": "NSE",
        "eqe": 91,
        "risk_status": "EXTREME",
    }

    risk_result = engine.evaluate(
        risk_reject
    )

    assert (
        risk_result.status
        == OpportunityStatus.REJECT
    )

    # ------------------------------------------------------------------------
    # 9. Explicit review gate
    # ------------------------------------------------------------------------

    review_candidate = {
        "instrument_id": "REV001",
        "symbol": "REVIEW",
        "timestamp": now,
        "market_id": "NSE",
        "eqe": 85,
        "timing_status": "REVIEW",
    }

    review_result = engine.evaluate(
        review_candidate
    )

    assert (
        review_result.status
        == OpportunityStatus.REVIEW
    )

    # ------------------------------------------------------------------------
    # 10. Missing optional gates are warnings, not automatic rejection/review
    # ------------------------------------------------------------------------

    sparse = {
        "instrument_id": "SPARSE001",
        "symbol": "SPARSE",
        "timestamp": now,
        "market_id": "NSE",
        "eqe": 84,
    }

    sparse_result = engine.evaluate(
        sparse
    )

    assert (
        sparse_result.status
        == OpportunityStatus.PASS
    )

    assert (
        sparse_result.opportunity_score
        == 84.0
    )

    assert sparse_result.warnings

    # ------------------------------------------------------------------------
    # 11. Ineligible candidate
    # ------------------------------------------------------------------------

    ineligible = {
        "instrument_id": "INEL001",
        "symbol": "INELIGIBLE",
        "timestamp": now,
        "market_id": "NSE",
        "eqe": 90,
        "eligible": False,
    }

    ineligible_result = engine.evaluate(
        ineligible
    )

    assert (
        ineligible_result.status
        == OpportunityStatus.REJECT
    )

    assert (
        ineligible_result.condition
        == OpportunityCondition.BLOCKED
    )

    # ------------------------------------------------------------------------
    # 12. Market identity protection
    # ------------------------------------------------------------------------

    wrong_market = {
        "instrument_id": "WRONG001",
        "symbol": "WRONGMARKET",
        "timestamp": now,
        "market_id": "BSE",
        "eqe": 90,
    }

    wrong_market_result = engine.evaluate(
        wrong_market
    )

    assert (
        wrong_market_result.status
        == OpportunityStatus.REJECT
    )

    # ------------------------------------------------------------------------
    # 13. Future timestamp protection
    # ------------------------------------------------------------------------

    future_candidate = {
        "instrument_id": "FUTURE001",
        "symbol": "FUTURE",
        "timestamp": (
            now.timestamp() + 3600
        ),
        "market_id": "NSE",
        "eqe": 90,
    }

    future_result = engine.evaluate(
        future_candidate
    )

    assert (
        future_result.status
        == OpportunityStatus.REJECT
    )

    # ------------------------------------------------------------------------
    # 14. Unknown opportunity
    # ------------------------------------------------------------------------

    unknown = {
        "instrument_id": "UNKNOWN001",
        "symbol": "UNKNOWN",
        "timestamp": now,
        "market_id": "NSE",
    }

    unknown_result = engine.evaluate(
        unknown
    )

    assert (
        unknown_result.status
        == OpportunityStatus.UNKNOWN
    )

    assert (
        unknown_result.condition
        == OpportunityCondition.UNKNOWN
    )

    # ------------------------------------------------------------------------
    # 15. Evidence completeness
    # ------------------------------------------------------------------------

    partial = {
        "instrument_id": "PARTIAL001",
        "symbol": "PARTIAL",
        "timestamp": now,
        "market_id": "NSE",
        "eqe": 70,
        "trend_strength": 72,
        "volume_ratio": 1.3,
        "liquidity_score": 70,
        "risk_score": 40,
    }

    partial_result = engine.evaluate(
        partial
    )

    assert (
        partial_result.status
        == OpportunityStatus.PASS
    )

    assert (
        partial_result.evidence_completeness
        == 0.5
    )

    # ------------------------------------------------------------------------
    # 16. Opportunity condition boundaries
    # ------------------------------------------------------------------------

    for score, expected in (
        (80, OpportunityCondition.ACTIONABLE),
        (79.99, OpportunityCondition.PROMISING),
        (65, OpportunityCondition.PROMISING),
        (64.99, OpportunityCondition.DEVELOPING),
        (45, OpportunityCondition.DEVELOPING),
        (44.99, OpportunityCondition.FRAGILE),
    ):

        boundary = {
            "instrument_id": f"BOUNDARY-{score}",
            "symbol": f"B{score}",
            "timestamp": now,
            "market_id": "NSE",
            "eqe": score,
            "trend_strength": 70,
            "volume_ratio": 1.2,
            "liquidity_score": 70,
            "risk_score": 30,
        }

        boundary_result = engine.evaluate(
            boundary
        )

        assert (
            boundary_result.condition
            == expected
        )

    # ------------------------------------------------------------------------
    # 17. Deterministic collection ranking
    # ------------------------------------------------------------------------

    collection_candidates = [
        {
            "instrument_id": "A",
            "symbol": "AAA",
            "timestamp": now,
            "market_id": "NSE",
            "eqe": 72,
        },
        {
            "instrument_id": "B",
            "symbol": "BBB",
            "timestamp": now,
            "market_id": "NSE",
            "eqe": 91,
        },
        {
            "instrument_id": "C",
            "symbol": "CCC",
            "timestamp": now,
            "market_id": "NSE",
            "eqe": 66,
        },
        {
            "instrument_id": "D",
            "symbol": "DDD",
            "timestamp": now,
            "market_id": "NSE",
            "eqe": 84,
        },
    ]

    collection = engine.evaluate_many(
        collection_candidates
    )

    assert collection.total_count == 4
    assert collection.pass_count == 4
    assert collection.reject_count == 0

    assert [
        item.instrument_id
        for item in collection.ranked
    ] == [
        "B",
        "D",
        "A",
        "C",
    ]

    # ------------------------------------------------------------------------
    # 18. Top N
    # ------------------------------------------------------------------------

    top_two = engine.top(
        collection.decisions,
        limit=2,
    )

    assert len(top_two) == 2

    assert top_two[0].instrument_id == "B"
    assert top_two[1].instrument_id == "D"

    # ------------------------------------------------------------------------
    # 19. Filtering
    # ------------------------------------------------------------------------

    filtered = engine.filter(
        collection.decisions,
        status=OpportunityStatus.PASS,
    )

    assert len(filtered) == 4

    # ------------------------------------------------------------------------
    # 20. Mapping input with extra fields
    # ------------------------------------------------------------------------

    mapping_candidate = {
        "id": "MAP001",
        "ticker": "MAP",
        "time": now.isoformat(),
        "market_id": "NSE",
        "eqe": "88.5",
        "direction": "SHORT",
        "opportunity_type": "REVERSAL",
        "custom_field": "preserve-me",
    }

    mapping_result = engine.evaluate(
        mapping_candidate
    )

    assert (
        mapping_result.status
        == OpportunityStatus.PASS
    )

    assert (
        mapping_result.opportunity_score
        == 88.5
    )

    assert (
        mapping_result.direction
        == OpportunityDirection.SHORT
    )

    assert (
        mapping_result.opportunity_type
        == OpportunityType.REVERSAL
    )

    assert (
        mapping_result.provenance["engine"]
        == "OpportunityEngine"
    )

    # ------------------------------------------------------------------------
    # 21. Serialization
    # ------------------------------------------------------------------------

    serialized_decision = (
        engine.serialize_decision(
            strong
        )
    )

    assert isinstance(
        serialized_decision,
        dict,
    )

    assert (
        serialized_decision["status"]
        == "PASS"
    )

    assert (
        serialized_decision["condition"]
        == "ACTIONABLE"
    )

    serialized_result = (
        engine.serialize_result(
            collection
        )
    )

    assert isinstance(
        serialized_result,
        dict,
    )

    assert (
        serialized_result["total_count"]
        == 4
    )

    # ------------------------------------------------------------------------
    # 22. Engine info
    # ------------------------------------------------------------------------

    info = engine.get_engine_info()

    assert (
        info["engine"]
        == "OpportunityEngine"
    )

    assert (
        info["engine_version"]
        == "2.0"
    )

    assert (
        "eqe"
        in info["primary_scores"]
    )

    # ------------------------------------------------------------------------
    # 23. No execution contract
    # ------------------------------------------------------------------------

    assert not hasattr(
        strong,
        "entry_price",
    )

    assert not hasattr(
        strong,
        "stop_loss",
    )

    assert not hasattr(
        strong,
        "take_profit",
    )

    # ------------------------------------------------------------------------
    # 24. Module-level API
    # ------------------------------------------------------------------------

    module_decision = evaluate_opportunity(
        candidate,
        market_id="NSE",
    )

    assert (
        module_decision.status
        == OpportunityStatus.PASS
    )

    module_result = evaluate_opportunities(
        collection_candidates,
        market_id="NSE",
    )

    assert module_result.total_count == 4

    discovered = discover_opportunities(
        collection_candidates,
        market_id="NSE",
    )

    assert discovered.total_count == 4

    module_top = top_opportunities(
        module_result.decisions,
        limit=1,
        market_id="NSE",
    )

    assert len(module_top) == 1
    assert module_top[0].instrument_id == "B"

    module_filtered = filter_opportunities(
        module_result.decisions,
        status=OpportunityStatus.PASS,
        market_id="NSE",
    )

    assert len(module_filtered) == 4

    # ------------------------------------------------------------------------
    # 25. Module-level serialization APIs
    # ------------------------------------------------------------------------

    serialized_one = (
        serialize_opportunity_decision(
            strong
        )
    )

    assert (
        serialized_one["instrument_id"]
        == "NIFTY001"
    )

    serialized_many = (
        serialize_opportunity_result(
            collection
        )
    )

    assert (
        serialized_many["total_count"]
        == 4
    )

    # ------------------------------------------------------------------------
    # PASS
    # ------------------------------------------------------------------------

    print(
        "opportunity_engine.py self-test: PASS"
    )


# ============================================================================
# PUBLIC EXPORTS
# ============================================================================


__all__ = [
    "OpportunityStatus",
    "OpportunityCondition",
    "OpportunityDirection",
    "OpportunityType",
    "OpportunityBasis",
    "GateStatus",
    "OpportunitySnapshot",
    "OpportunityGate",
    "OpportunityDecision",
    "OpportunityResult",
    "OpportunityPolicy",
    "OpportunityEngine",
    "evaluate_opportunity",
    "evaluate_opportunities",
    "discover_opportunities",
    "top_opportunities",
    "filter_opportunities",
    "serialize_opportunity_decision",
    "serialize_opportunity_result",
]


# ============================================================================
# DIRECT EXECUTION
# ============================================================================


if __name__ == "__main__":
    _self_test()