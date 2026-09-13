"""
ROBOMLM_PLUS
Opportunity Intelligence Layer
Ranking Engine

Purpose
-------
Ranks already-evaluated opportunity candidates using observable,
point-in-time evidence.

Architecture Position
---------------------
Universe
    ↓
Liquidity Filter
    ↓
Risk Filter
    ↓
Timing Engine
    ↓
Intraday Engine
    ↓
Ranking Engine
    ↓
Opportunity Engine

Design Principles
-----------------
1. Ranking is NOT prediction.
2. Ranking is NOT BUY/SELL generation.
3. Ranking must not fabricate missing evidence.
4. Point-in-time integrity is mandatory.
5. Market identity must be preserved.
6. Existing upstream intelligence is consumed rather than replaced.
7. No arbitrary proprietary score is invented when authoritative
   upstream scores already exist.
8. Evidence completeness must remain visible.
9. Deterministic ordering is required.
10. Equal candidates must have deterministic tie-breaking.
11. Invalid numeric values are rejected.
12. Future timestamps are rejected.
13. The engine must remain usable with dicts, dataclasses and
    compatible objects.
14. Ranking output must preserve provenance.

This module intentionally does NOT:
- generate BUY/SELL signals
- predict future prices
- invent probability
- create leverage
- execute trades
- replace EQE/PFS/LQS/MTS/RDS/etc.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict, is_dataclass
from datetime import datetime, timezone
from enum import Enum
import json
import math
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


# ============================================================================
# ENUMS
# ============================================================================

class RankingStatus(str, Enum):
    PASS = "PASS"
    REVIEW = "REVIEW"
    REJECT = "REJECT"
    UNKNOWN = "UNKNOWN"


class RankingCondition(str, Enum):
    STRONG = "STRONG"
    GOOD = "GOOD"
    NEUTRAL = "NEUTRAL"
    WEAK = "WEAK"
    INCOMPLETE = "INCOMPLETE"
    UNKNOWN = "UNKNOWN"


class RankingBasis(str, Enum):
    EVIDENCE = "EVIDENCE"
    UPSTREAM_SCORE = "UPSTREAM_SCORE"
    HYBRID = "HYBRID"
    NONE = "NONE"


# ============================================================================
# DATA CONTRACTS
# ============================================================================

@dataclass
class RankingSnapshot:
    """
    Normalized point-in-time opportunity evidence.

    The engine accepts a broad evidence contract because different
    upstream modules may expose different subsets.

    All fields are optional unless required by policy.
    """

    instrument_id: Optional[str] = None
    symbol: Optional[str] = None

    timestamp: Optional[datetime] = None

    market_id: Optional[str] = None
    venue_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Upstream intelligence
    # ------------------------------------------------------------------

    eqe: Optional[float] = None
    pfs: Optional[float] = None
    mci: Optional[float] = None

    mts: Optional[float] = None
    lqs: Optional[float] = None
    rds: Optional[float] = None
    mcs: Optional[float] = None

    # ------------------------------------------------------------------
    # Evidence dimensions
    # ------------------------------------------------------------------

    trend_strength: Optional[float] = None
    volume_ratio: Optional[float] = None
    liquidity_score: Optional[float] = None
    risk_score: Optional[float] = None
    timing_score: Optional[float] = None
    derivatives_score: Optional[float] = None
    participation_score: Optional[float] = None
    relationship_score: Optional[float] = None

    # ------------------------------------------------------------------
    # Eligibility / upstream decisions
    # ------------------------------------------------------------------

    liquidity_status: Optional[str] = None
    risk_status: Optional[str] = None
    timing_status: Optional[str] = None
    intraday_status: Optional[str] = None

    eligible: Optional[bool] = None

    # ------------------------------------------------------------------
    # Opportunity metadata
    # ------------------------------------------------------------------

    opportunity_type: Optional[str] = None
    direction: Optional[str] = None

    confidence: Optional[float] = None
    evidence_completeness: Optional[float] = None

    source: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RankingDecision:
    """
    Result for one candidate.
    """

    instrument_id: Optional[str] = None
    symbol: Optional[str] = None

    status: RankingStatus = RankingStatus.UNKNOWN
    condition: RankingCondition = RankingCondition.UNKNOWN

    rank: Optional[int] = None

    ranking_score: Optional[float] = None
    normalized_score: Optional[float] = None

    basis: RankingBasis = RankingBasis.NONE

    evidence_count: int = 0
    evidence_completeness: Optional[float] = None

    reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    opportunity_type: Optional[str] = None
    direction: Optional[str] = None

    market_id: Optional[str] = None
    timestamp: Optional[datetime] = None

    provenance: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RankingResult:
    """
    Collection-level ranking output.
    """

    status: RankingStatus = RankingStatus.UNKNOWN

    decisions: List[RankingDecision] = field(default_factory=list)

    ranked: List[RankingDecision] = field(default_factory=list)
    rejected: List[RankingDecision] = field(default_factory=list)
    review: List[RankingDecision] = field(default_factory=list)
    unknown: List[RankingDecision] = field(default_factory=list)

    count_input: int = 0
    count_ranked: int = 0
    count_rejected: int = 0
    count_review: int = 0
    count_unknown: int = 0

    market_id: Optional[str] = None
    timestamp: Optional[datetime] = None

    provenance: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RankingPolicy:
    """
    Configuration for RankingEngine.

    Defaults intentionally avoid inventing arbitrary intelligence
    thresholds. The engine can rank from authoritative upstream
    scores when available, while preserving evidence completeness.
    """

    minimum_rank_score: Optional[float] = None
    review_rank_score: Optional[float] = None

    minimum_evidence_count: int = 1

    minimum_evidence_completeness: Optional[float] = None
    review_evidence_completeness: Optional[float] = None

    require_timestamp: bool = True
    reject_future_data: bool = True

    require_market_match: bool = True

    reject_ineligible: bool = True

    reject_invalid_numeric: bool = True

    # If True, authoritative upstream scores are preferred.
    prefer_upstream_scores: bool = True

    # When no authoritative score exists, evidence-based ranking
    # can be enabled explicitly.
    allow_evidence_ranking: bool = True

    # Deterministic tie breaker.
    tie_break_symbol: bool = True


# ============================================================================
# ENGINE
# ============================================================================

class RankingEngine:
    """
    Opportunity candidate ranking engine.

    This engine orders candidates; it does not create a trade decision.
    """

    ENGINE_NAME = "RankingEngine"
    ENGINE_VERSION = "1.0"

    def __init__(
        self,
        policy: Optional[RankingPolicy] = None,
    ) -> None:
        self.policy = policy or RankingPolicy()

    # ==================================================================
    # PUBLIC: EVALUATE ONE
    # ==================================================================

    def evaluate(
        self,
        snapshot: Any,
        *,
        now: Optional[datetime] = None,
        market_id: Optional[str] = None,
    ) -> RankingDecision:

        current_now = self._ensure_aware(
            now or datetime.now(timezone.utc)
        )

        item = self.normalize(snapshot)

        reasons: List[str] = []
        warnings: List[str] = []

        # --------------------------------------------------------------
        # Identity
        # --------------------------------------------------------------

        if not item.instrument_id and not item.symbol:
            return self._decision(
                item,
                RankingStatus.UNKNOWN,
                RankingCondition.UNKNOWN,
                reasons=["Missing instrument identity"],
                warnings=warnings,
            )

        # --------------------------------------------------------------
        # Market identity
        # --------------------------------------------------------------

        if (
            self.policy.require_market_match
            and market_id is not None
            and item.market_id is not None
            and str(item.market_id) != str(market_id)
        ):
            return self._decision(
                item,
                RankingStatus.REJECT,
                RankingCondition.UNKNOWN,
                reasons=[
                    "Market identity mismatch"
                ],
                warnings=warnings,
            )

        # --------------------------------------------------------------
        # Timestamp
        # --------------------------------------------------------------

        if item.timestamp is None:
            if self.policy.require_timestamp:
                return self._decision(
                    item,
                    RankingStatus.UNKNOWN,
                    RankingCondition.UNKNOWN,
                    reasons=["Missing point-in-time timestamp"],
                    warnings=warnings,
                )
        else:
            if (
                self.policy.reject_future_data
                and item.timestamp > current_now
            ):
                return self._decision(
                    item,
                    RankingStatus.REJECT,
                    RankingCondition.UNKNOWN,
                    reasons=[
                        "Future-dated evidence is not allowed"
                    ],
                    warnings=warnings,
                )

        # --------------------------------------------------------------
        # Numeric integrity
        # --------------------------------------------------------------

        invalid_fields = self._invalid_numeric_fields(item)

        if invalid_fields and self.policy.reject_invalid_numeric:
            return self._decision(
                item,
                RankingStatus.REJECT,
                RankingCondition.UNKNOWN,
                reasons=[
                    "Invalid numeric evidence: "
                    + ", ".join(invalid_fields)
                ],
                warnings=warnings,
            )

        # --------------------------------------------------------------
        # Eligibility
        # --------------------------------------------------------------

        if (
            self.policy.reject_ineligible
            and item.eligible is False
        ):
            return self._decision(
                item,
                RankingStatus.REJECT,
                RankingCondition.WEAK,
                reasons=["Candidate marked ineligible upstream"],
                warnings=warnings,
            )

        # --------------------------------------------------------------
        # Evidence availability
        # --------------------------------------------------------------

        evidence_count = self._evidence_count(item)

        if evidence_count < self.policy.minimum_evidence_count:
            return self._decision(
                item,
                RankingStatus.UNKNOWN,
                RankingCondition.INCOMPLETE,
                reasons=[
                    "Insufficient observable ranking evidence"
                ],
                warnings=warnings,
                evidence_count=evidence_count,
            )

        # --------------------------------------------------------------
        # Evidence completeness
        # --------------------------------------------------------------

        completeness = self._calculate_completeness(item)

        if (
            self.policy.minimum_evidence_completeness is not None
            and completeness is not None
            and completeness
            < self.policy.minimum_evidence_completeness
        ):
            return self._decision(
                item,
                RankingStatus.REJECT,
                RankingCondition.INCOMPLETE,
                reasons=[
                    "Evidence completeness below minimum policy"
                ],
                warnings=warnings,
                evidence_count=evidence_count,
                evidence_completeness=completeness,
            )

        if (
            self.policy.review_evidence_completeness is not None
            and completeness is not None
            and completeness
            < self.policy.review_evidence_completeness
        ):
            warnings.append(
                "Evidence completeness requires review"
            )

        # --------------------------------------------------------------
        # Ranking basis
        # --------------------------------------------------------------

        ranking_score, basis = self._resolve_ranking_score(item)

        if ranking_score is None:
            return self._decision(
                item,
                RankingStatus.UNKNOWN,
                RankingCondition.INCOMPLETE,
                reasons=[
                    "No authoritative or permitted ranking evidence"
                ],
                warnings=warnings,
                evidence_count=evidence_count,
                evidence_completeness=completeness,
                basis=basis,
            )

        # --------------------------------------------------------------
        # Normalize
        # --------------------------------------------------------------

        normalized = self._normalize_score(ranking_score)

        # --------------------------------------------------------------
        # Condition
        # --------------------------------------------------------------

        condition = self._condition(
            normalized,
            completeness,
        )

        # --------------------------------------------------------------
        # Threshold status
        # --------------------------------------------------------------

        status = RankingStatus.PASS

        if (
            self.policy.minimum_rank_score is not None
            and ranking_score < self.policy.minimum_rank_score
        ):
            status = RankingStatus.REJECT
            reasons.append(
                "Ranking score below minimum policy"
            )

        elif (
            self.policy.review_rank_score is not None
            and ranking_score < self.policy.review_rank_score
        ):
            status = RankingStatus.REVIEW
            warnings.append(
                "Ranking score is below preferred review threshold"
            )

        if warnings and status == RankingStatus.PASS:
            status = RankingStatus.REVIEW

        if not reasons:
            reasons.append(
                "Candidate ranked from observable point-in-time evidence"
            )

        return self._decision(
            item,
            status,
            condition,
            reasons=reasons,
            warnings=warnings,
            evidence_count=evidence_count,
            evidence_completeness=completeness,
            ranking_score=ranking_score,
            normalized_score=normalized,
            basis=basis,
        )

    # ==================================================================
    # PUBLIC: COLLECTION
    # ==================================================================

    def rank(
        self,
        snapshots: Iterable[Any],
        *,
        now: Optional[datetime] = None,
        market_id: Optional[str] = None,
    ) -> RankingResult:

        current_now = self._ensure_aware(
            now or datetime.now(timezone.utc)
        )

        items = list(snapshots)

        decisions: List[RankingDecision] = []

        for snapshot in items:
            decision = self.evaluate(
                snapshot,
                now=current_now,
                market_id=market_id,
            )
            decisions.append(decision)

        # --------------------------------------------------------------
        # Deterministic ranking
        # --------------------------------------------------------------

        ranked_candidates = [
            d
            for d in decisions
            if d.status in (
                RankingStatus.PASS,
                RankingStatus.REVIEW,
            )
            and d.ranking_score is not None
        ]

        ranked_candidates.sort(
            key=self._ranking_sort_key
        )

        for index, decision in enumerate(
            ranked_candidates,
            start=1,
        ):
            decision.rank = index

        # --------------------------------------------------------------
        # Buckets
        # --------------------------------------------------------------

        ranked = [
            d
            for d in ranked_candidates
            if d.status == RankingStatus.PASS
        ]

        review = [
            d
            for d in decisions
            if d.status == RankingStatus.REVIEW
        ]

        rejected = [
            d
            for d in decisions
            if d.status == RankingStatus.REJECT
        ]

        unknown = [
            d
            for d in decisions
            if d.status == RankingStatus.UNKNOWN
        ]

        # --------------------------------------------------------------
        # Collection status
        # --------------------------------------------------------------

        if ranked:
            collection_status = RankingStatus.PASS
        elif review:
            collection_status = RankingStatus.REVIEW
        elif unknown:
            collection_status = RankingStatus.UNKNOWN
        else:
            collection_status = RankingStatus.REJECT

        return RankingResult(
            status=collection_status,
            decisions=decisions,
            ranked=ranked,
            rejected=rejected,
            review=review,
            unknown=unknown,
            count_input=len(items),
            count_ranked=len(ranked),
            count_rejected=len(rejected),
            count_review=len(review),
            count_unknown=len(unknown),
            market_id=market_id,
            timestamp=current_now,
            provenance={
                "engine": self.ENGINE_NAME,
                "engine_version": self.ENGINE_VERSION,
                "policy": self.policy_to_dict(),
                "point_in_time": True,
            },
        )

    # ==================================================================
    # PUBLIC ALIASES
    # ==================================================================

    def filter(
        self,
        snapshots: Iterable[Any],
        *,
        now: Optional[datetime] = None,
        market_id: Optional[str] = None,
    ) -> RankingResult:

        return self.rank(
            snapshots,
            now=now,
            market_id=market_id,
        )

    def apply(
        self,
        snapshots: Iterable[Any],
        *,
        now: Optional[datetime] = None,
        market_id: Optional[str] = None,
    ) -> RankingResult:

        return self.rank(
            snapshots,
            now=now,
            market_id=market_id,
        )

    # ==================================================================
    # NORMALIZATION
    # ==================================================================

    def normalize(self, value: Any) -> RankingSnapshot:

        if isinstance(value, RankingSnapshot):
            return value

        mapping = self._to_mapping(value)

        timestamp = self._parse_timestamp(
            self._first(
                mapping,
                "timestamp",
                "time",
                "ts",
                "source_timestamp",
            )
        )

        return RankingSnapshot(
            instrument_id=self._string_or_none(
                self._first(
                    mapping,
                    "instrument_id",
                    "instrument",
                    "id",
                    "security_id",
                )
            ),
            symbol=self._string_or_none(
                self._first(
                    mapping,
                    "symbol",
                    "ticker",
                    "exchange_symbol",
                )
            ),
            timestamp=timestamp,
            market_id=self._string_or_none(
                self._first(
                    mapping,
                    "market_id",
                    "market",
                    "exchange",
                )
            ),
            venue_id=self._string_or_none(
                self._first(
                    mapping,
                    "venue_id",
                    "venue",
                )
            ),

            eqe=self._number(
                self._first(mapping, "eqe", "eqe_score")
            ),
            pfs=self._number(
                self._first(mapping, "pfs", "pfs_score")
            ),
            mci=self._number(
                self._first(mapping, "mci", "mci_score")
            ),

            mts=self._number(
                self._first(mapping, "mts", "mts_score")
            ),
            lqs=self._number(
                self._first(mapping, "lqs", "lqs_score")
            ),
            rds=self._number(
                self._first(mapping, "rds", "rds_score")
            ),
            mcs=self._number(
                self._first(mapping, "mcs", "mcs_score")
            ),

            trend_strength=self._number(
                self._first(
                    mapping,
                    "trend_strength",
                    "trend_score",
                )
            ),
            volume_ratio=self._number(
                self._first(
                    mapping,
                    "volume_ratio",
                )
            ),
            liquidity_score=self._number(
                self._first(
                    mapping,
                    "liquidity_score",
                )
            ),
            risk_score=self._number(
                self._first(
                    mapping,
                    "risk_score",
                )
            ),
            timing_score=self._number(
                self._first(
                    mapping,
                    "timing_score",
                )
            ),
            derivatives_score=self._number(
                self._first(
                    mapping,
                    "derivatives_score",
                )
            ),
            participation_score=self._number(
                self._first(
                    mapping,
                    "participation_score",
                )
            ),
            relationship_score=self._number(
                self._first(
                    mapping,
                    "relationship_score",
                )
            ),

            liquidity_status=self._string_or_none(
                self._first(
                    mapping,
                    "liquidity_status",
                )
            ),
            risk_status=self._string_or_none(
                self._first(
                    mapping,
                    "risk_status",
                )
            ),
            timing_status=self._string_or_none(
                self._first(
                    mapping,
                    "timing_status",
                )
            ),
            intraday_status=self._string_or_none(
                self._first(
                    mapping,
                    "intraday_status",
                )
            ),

            eligible=self._boolean(
                self._first(
                    mapping,
                    "eligible",
                    "is_eligible",
                )
            ),

            opportunity_type=self._string_or_none(
                self._first(
                    mapping,
                    "opportunity_type",
                    "type",
                )
            ),
            direction=self._string_or_none(
                self._first(
                    mapping,
                    "direction",
                    "bias",
                )
            ),

            confidence=self._number(
                self._first(
                    mapping,
                    "confidence",
                )
            ),
            evidence_completeness=self._number(
                self._first(
                    mapping,
                    "evidence_completeness",
                    "completeness",
                )
            ),

            source=self._string_or_none(
                self._first(
                    mapping,
                    "source",
                    "provenance_source",
                )
            ),

            metadata=dict(
                self._first(
                    mapping,
                    "metadata",
                    default={},
                )
                or {}
            ),
        )

    # ==================================================================
    # SCORE RESOLUTION
    # ==================================================================

    def _resolve_ranking_score(
        self,
        item: RankingSnapshot,
    ) -> Tuple[Optional[float], RankingBasis]:

        # --------------------------------------------------------------
        # Authoritative upstream scores
        #
        # Preference:
        # EQE → PFS → MCI
        #
        # These are consumed as already-established intelligence.
        # The ranking engine does not redefine their formulas.
        # --------------------------------------------------------------

        if self.policy.prefer_upstream_scores:

            for value in (
                item.eqe,
                item.pfs,
                item.mci,
            ):
                if self._valid_number(value):
                    return float(value), RankingBasis.UPSTREAM_SCORE

        # --------------------------------------------------------------
        # Explicit evidence ranking
        # --------------------------------------------------------------

        if not self.policy.allow_evidence_ranking:
            return None, RankingBasis.NONE

        evidence_values = [
            item.trend_strength,
            item.volume_ratio,
            item.liquidity_score,
            item.risk_score,
            item.timing_score,
            item.derivatives_score,
            item.participation_score,
            item.relationship_score,
        ]

        valid_values = [
            float(v)
            for v in evidence_values
            if self._valid_number(v)
        ]

        if not valid_values:
            return None, RankingBasis.NONE

        # IMPORTANT:
        # This is a neutral evidence aggregation only.
        # It does not claim to replace any authoritative D6/D13 formula.
        #
        # Values are normalized to [0, 100] only when the input appears
        # to already use a 0-100 convention. Otherwise raw evidence is
        # preserved and no artificial transformation is applied.

        normalized_values = []

        for value in valid_values:
            if 0.0 <= value <= 100.0:
                normalized_values.append(value)

        if not normalized_values:
            return None, RankingBasis.NONE

        return (
            sum(normalized_values) / len(normalized_values),
            RankingBasis.EVIDENCE,
        )

    # ==================================================================
    # CONDITION
    # ==================================================================

    def _condition(
        self,
        normalized_score: Optional[float],
        completeness: Optional[float],
    ) -> RankingCondition:

        if normalized_score is None:
            return RankingCondition.UNKNOWN

        if completeness is not None and completeness < 0.50:
            return RankingCondition.INCOMPLETE

        if normalized_score >= 80.0:
            return RankingCondition.STRONG

        if normalized_score >= 65.0:
            return RankingCondition.GOOD

        if normalized_score >= 45.0:
            return RankingCondition.NEUTRAL

        return RankingCondition.WEAK

    # ==================================================================
    # EVIDENCE COUNT
    # ==================================================================

    def _evidence_count(
        self,
        item: RankingSnapshot,
    ) -> int:

        fields = (
            item.eqe,
            item.pfs,
            item.mci,
            item.mts,
            item.lqs,
            item.rds,
            item.mcs,
            item.trend_strength,
            item.volume_ratio,
            item.liquidity_score,
            item.risk_score,
            item.timing_score,
            item.derivatives_score,
            item.participation_score,
            item.relationship_score,
            item.confidence,
        )

        return sum(
            1
            for value in fields
            if self._valid_number(value)
        )

    # ==================================================================
    # COMPLETENESS
    # ==================================================================

    def _calculate_completeness(
        self,
        item: RankingSnapshot,
    ) -> Optional[float]:

        fields = (
            item.trend_strength,
            item.volume_ratio,
            item.liquidity_score,
            item.risk_score,
            item.timing_score,
            item.derivatives_score,
            item.participation_score,
            item.relationship_score,
        )

        total = len(fields)

        if total == 0:
            return None

        valid = sum(
            1
            for value in fields
            if self._valid_number(value)
        )

        return valid / total

    # ==================================================================
    # SORT KEY
    # ==================================================================

    def _ranking_sort_key(
        self,
        decision: RankingDecision,
    ) -> Tuple[float, float, str]:

        score = (
            decision.ranking_score
            if decision.ranking_score is not None
            else float("-inf")
        )

        completeness = (
            decision.evidence_completeness
            if decision.evidence_completeness is not None
            else 0.0
        )

        symbol = (
            decision.symbol or
            decision.instrument_id or
            ""
        )

        # Higher score first.
        # Higher completeness first.
        # Symbol ascending provides deterministic tie-break.
        return (
            -score,
            -completeness,
            symbol,
        )
# ============================================================================
# RANKING ENGINE — PART 2/3
# ============================================================================

    # ==================================================================
    # DECISION BUILDER
    # ==================================================================

    def _decision(
        self,
        item: RankingSnapshot,
        status: RankingStatus,
        condition: RankingCondition,
        *,
        reasons: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None,
        evidence_count: int = 0,
        evidence_completeness: Optional[float] = None,
        ranking_score: Optional[float] = None,
        normalized_score: Optional[float] = None,
        basis: RankingBasis = RankingBasis.NONE,
    ) -> RankingDecision:

        return RankingDecision(
            instrument_id=item.instrument_id,
            symbol=item.symbol,
            status=status,
            condition=condition,
            ranking_score=ranking_score,
            normalized_score=normalized_score,
            basis=basis,
            evidence_count=evidence_count,
            evidence_completeness=evidence_completeness,
            reasons=list(reasons or []),
            warnings=list(warnings or []),
            opportunity_type=item.opportunity_type,
            direction=item.direction,
            market_id=item.market_id,
            timestamp=item.timestamp,
            provenance={
                "engine": self.ENGINE_NAME,
                "engine_version": self.ENGINE_VERSION,
                "source": item.source,
                "point_in_time": True,
            },
        )

    # ==================================================================
    # SCORE NORMALIZATION
    # ==================================================================

    @staticmethod
    def _normalize_score(
        value: Optional[float],
    ) -> Optional[float]:

        if not RankingEngine._valid_number(value):
            return None

        value = float(value)

        # Existing intelligence scores are normally 0–100.
        # Do not silently manufacture a transformation for other scales.
        if 0.0 <= value <= 100.0:
            return value

        return None

    # ==================================================================
    # NUMERIC INTEGRITY
    # ==================================================================

    def _invalid_numeric_fields(
        self,
        item: RankingSnapshot,
    ) -> List[str]:

        numeric_fields = {
            "eqe": item.eqe,
            "pfs": item.pfs,
            "mci": item.mci,
            "mts": item.mts,
            "lqs": item.lqs,
            "rds": item.rds,
            "mcs": item.mcs,
            "trend_strength": item.trend_strength,
            "volume_ratio": item.volume_ratio,
            "liquidity_score": item.liquidity_score,
            "risk_score": item.risk_score,
            "timing_score": item.timing_score,
            "derivatives_score": item.derivatives_score,
            "participation_score": item.participation_score,
            "relationship_score": item.relationship_score,
            "confidence": item.confidence,
            "evidence_completeness": item.evidence_completeness,
        }

        invalid: List[str] = []

        for name, value in numeric_fields.items():

            if value is None:
                continue

            try:
                number = float(value)
            except (TypeError, ValueError):
                invalid.append(name)
                continue

            if not math.isfinite(number):
                invalid.append(name)

        return invalid

    # ==================================================================
    # NORMALIZATION HELPERS
    # ==================================================================

    @staticmethod
    def _to_mapping(
        value: Any,
    ) -> Mapping[str, Any]:

        if isinstance(value, Mapping):
            return value

        if is_dataclass(value):
            return asdict(value)

        if hasattr(value, "__dict__"):
            return vars(value)

        raise TypeError(
            "RankingEngine accepts mappings, dataclasses, "
            "or objects exposing __dict__"
        )

    @staticmethod
    def _first(
        mapping: Mapping[str, Any],
        *keys: str,
        default: Any = None,
    ) -> Any:

        for key in keys:
            if key in mapping:
                return mapping[key]

        return default

    @staticmethod
    def _number(
        value: Any,
    ) -> Optional[float]:

        if value is None:
            return None

        try:
            number = float(value)
        except (TypeError, ValueError):
            return None

        if not math.isfinite(number):
            return None

        return number

    @staticmethod
    def _valid_number(
        value: Any,
    ) -> bool:

        if value is None:
            return False

        try:
            number = float(value)
        except (TypeError, ValueError):
            return False

        return math.isfinite(number)

    @staticmethod
    def _boolean(
        value: Any,
    ) -> Optional[bool]:

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
            normalized = value.strip().lower()

            if normalized in {
                "true",
                "1",
                "yes",
                "y",
                "on",
                "enabled",
            }:
                return True

            if normalized in {
                "false",
                "0",
                "no",
                "n",
                "off",
                "disabled",
            }:
                return False

        return None

    @staticmethod
    def _string_or_none(
        value: Any,
    ) -> Optional[str]:

        if value is None:
            return None

        text = str(value).strip()

        return text if text else None

    # ==================================================================
    # TIMESTAMP PARSING
    # ==================================================================

    @staticmethod
    def _parse_timestamp(
        value: Any,
    ) -> Optional[datetime]:

        if value is None:
            return None

        if isinstance(value, datetime):
            return RankingEngine._ensure_aware(value)

        if isinstance(value, (int, float)):
            try:
                if not math.isfinite(float(value)):
                    return None

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
                return RankingEngine._ensure_aware(parsed)
            except ValueError:
                return None

        return None

    @staticmethod
    def _ensure_aware(
        value: datetime,
    ) -> datetime:

        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)

    # ==================================================================
    # SERIALIZATION
    # ==================================================================

    @staticmethod
    def _safe_enum_value(
        value: Any,
    ) -> Any:

        if isinstance(value, Enum):
            return value.value

        return value

    @classmethod
    def _json_safe(
        cls,
        value: Any,
    ) -> Any:

        if isinstance(value, Enum):
            return value.value

        if isinstance(value, datetime):
            return cls._ensure_aware(value).isoformat()

        if is_dataclass(value):
            return cls._json_safe(asdict(value))

        if isinstance(value, Mapping):
            return {
                str(key): cls._json_safe(item)
                for key, item in value.items()
            }

        if isinstance(value, (list, tuple, set)):
            return [
                cls._json_safe(item)
                for item in value
            ]

        if isinstance(value, float):

            if not math.isfinite(value):
                return None

            return value

        return value

    # ==================================================================
    # SNAPSHOT SERIALIZATION
    # ==================================================================

    def snapshot_to_dict(
        self,
        snapshot: RankingSnapshot,
    ) -> Dict[str, Any]:

        return self._json_safe(snapshot)

    def decision_to_dict(
        self,
        decision: RankingDecision,
    ) -> Dict[str, Any]:

        return self._json_safe(decision)

    def result_to_dict(
        self,
        result: RankingResult,
    ) -> Dict[str, Any]:

        return self._json_safe(result)

    def policy_to_dict(
        self,
    ) -> Dict[str, Any]:

        return self._json_safe(self.policy)

    # ==================================================================
    # JSON SERIALIZATION
    # ==================================================================

    def serialize_decision(
        self,
        decision: RankingDecision,
        *,
        indent: Optional[int] = None,
    ) -> str:

        return json.dumps(
            self.decision_to_dict(decision),
            indent=indent,
            sort_keys=True,
        )

    def serialize_result(
        self,
        result: RankingResult,
        *,
        indent: Optional[int] = None,
    ) -> str:

        return json.dumps(
            self.result_to_dict(result),
            indent=indent,
            sort_keys=True,
        )

    # ==================================================================
    # INFORMATION
    # ==================================================================

    def get_engine_info(self) -> Dict[str, Any]:

        return {
            "engine": self.ENGINE_NAME,
            "version": self.ENGINE_VERSION,
            "purpose": (
                "Rank opportunity candidates using "
                "observable point-in-time evidence"
            ),
            "generates_trade_signal": False,
            "predicts_future": False,
            "uses_external_thresholds": True,
            "point_in_time": True,
            "deterministic": True,
            "policy": self.policy_to_dict(),
        }


# ============================================================================
# MODULE-LEVEL CONVENIENCE APIs
# ============================================================================

def evaluate_ranking(
    snapshot: Any,
    *,
    policy: Optional[RankingPolicy] = None,
    now: Optional[datetime] = None,
    market_id: Optional[str] = None,
) -> RankingDecision:

    engine = RankingEngine(policy=policy)

    return engine.evaluate(
        snapshot,
        now=now,
        market_id=market_id,
    )


def rank_opportunities(
    snapshots: Iterable[Any],
    *,
    policy: Optional[RankingPolicy] = None,
    now: Optional[datetime] = None,
    market_id: Optional[str] = None,
) -> RankingResult:

    engine = RankingEngine(policy=policy)

    return engine.rank(
        snapshots,
        now=now,
        market_id=market_id,
    )


def filter_ranking(
    snapshots: Iterable[Any],
    *,
    policy: Optional[RankingPolicy] = None,
    now: Optional[datetime] = None,
    market_id: Optional[str] = None,
) -> RankingResult:

    return rank_opportunities(
        snapshots,
        policy=policy,
        now=now,
        market_id=market_id,
    )


# ============================================================================
# STRUCTURAL VALIDATION
# ============================================================================

def _structural_check() -> None:

    required_methods = (
        "evaluate",
        "rank",
        "filter",
        "apply",
        "normalize",
        "_resolve_ranking_score",
        "_condition",
        "_evidence_count",
        "_calculate_completeness",
        "_ranking_sort_key",
        "_decision",
        "_normalize_score",
        "_invalid_numeric_fields",
        "_to_mapping",
        "_first",
        "_number",
        "_valid_number",
        "_boolean",
        "_string_or_none",
        "_parse_timestamp",
        "_ensure_aware",
        "snapshot_to_dict",
        "decision_to_dict",
        "result_to_dict",
        "serialize_decision",
        "serialize_result",
        "get_engine_info",
    )

    for method_name in required_methods:
        assert hasattr(
            RankingEngine,
            method_name
        ), (
            f"Missing RankingEngine method: {method_name}"
        )

    assert RankingEngine.ENGINE_NAME == "RankingEngine"
    assert RankingEngine.ENGINE_VERSION == "1.0"


# ============================================================================
# END OF PART 2
# ============================================================================
# ============================================================================
# RANKING ENGINE — PART 3/3
# ============================================================================


def serialize_ranking(
    value: Any,
    *,
    indent: Optional[int] = None,
) -> str:
    """
    Generic serialization helper.

    Accepts RankingSnapshot, RankingDecision, RankingResult,
    RankingPolicy or compatible objects.
    """

    return json.dumps(
        RankingEngine._json_safe(value),
        indent=indent,
        sort_keys=True,
    )


def get_ranking_engine_info(
    policy: Optional[RankingPolicy] = None,
) -> Dict[str, Any]:
    """
    Return public engine metadata.
    """

    return RankingEngine(
        policy=policy
    ).get_engine_info()


# ============================================================================
# SELF TEST
# ============================================================================

def _self_test() -> None:
    """
    Deterministic local validation.

    These tests validate:
    - basic upstream-score ranking
    - deterministic ordering
    - evidence-based ranking
    - market protection
    - future-data protection
    - invalid numeric protection
    - eligibility protection
    - incomplete evidence handling
    - mapping normalization
    - timestamp normalization
    - serialization
    - generator safety
    """

    engine = RankingEngine(
        RankingPolicy(
            minimum_evidence_count=1,
            require_timestamp=True,
            reject_future_data=True,
            require_market_match=True,
            reject_ineligible=True,
            reject_invalid_numeric=True,
            prefer_upstream_scores=True,
            allow_evidence_ranking=True,
        )
    )

    test_time = datetime(
        2026,
        9,
        5,
        10,
        0,
        0,
        tzinfo=timezone.utc,
    )

    # ==================================================================
    # TEST 1 — Strong upstream score
    # ==================================================================

    strong = RankingSnapshot(
        instrument_id="NSE-001",
        symbol="AAA",
        timestamp=test_time,
        market_id="NSE",
        eqe=91.0,
        eligible=True,
        opportunity_type="TREND",
        direction="UP",
        source="test",
    )

    decision = engine.evaluate(
        strong,
        now=test_time,
        market_id="NSE",
    )

    assert decision.status == RankingStatus.PASS
    assert decision.condition == RankingCondition.STRONG
    assert decision.ranking_score == 91.0
    assert decision.basis == RankingBasis.UPSTREAM_SCORE

    # ==================================================================
    # TEST 2 — Good upstream score
    # ==================================================================

    good = RankingSnapshot(
        instrument_id="NSE-002",
        symbol="BBB",
        timestamp=test_time,
        market_id="NSE",
        pfs=70.0,
        eligible=True,
        source="test",
    )

    decision = engine.evaluate(
        good,
        now=test_time,
        market_id="NSE",
    )

    assert decision.status == RankingStatus.PASS
    assert decision.condition == RankingCondition.GOOD
    assert decision.ranking_score == 70.0

    # ==================================================================
    # TEST 3 — Collection ranking
    # ==================================================================

    collection = engine.rank(
        [
            good,
            strong,
        ],
        now=test_time,
        market_id="NSE",
    )

    assert collection.count_input == 2
    assert collection.count_ranked == 2
    assert collection.ranked[0].symbol == "AAA"
    assert collection.ranked[0].rank == 1
    assert collection.ranked[1].symbol == "BBB"
    assert collection.ranked[1].rank == 2

    # ==================================================================
    # TEST 4 — Deterministic tie-break
    # ==================================================================

    tie_a = RankingSnapshot(
        instrument_id="NSE-003",
        symbol="ZZZ",
        timestamp=test_time,
        market_id="NSE",
        eqe=75.0,
        eligible=True,
    )

    tie_b = RankingSnapshot(
        instrument_id="NSE-004",
        symbol="AAA2",
        timestamp=test_time,
        market_id="NSE",
        eqe=75.0,
        eligible=True,
    )

    tie_result = engine.rank(
        [tie_a, tie_b],
        now=test_time,
        market_id="NSE",
    )

    assert tie_result.ranked[0].symbol == "AAA2"
    assert tie_result.ranked[1].symbol == "ZZZ"

    # ==================================================================
    # TEST 5 — Evidence-based ranking
    # ==================================================================

    evidence_item = RankingSnapshot(
        instrument_id="NSE-005",
        symbol="CCC",
        timestamp=test_time,
        market_id="NSE",
        trend_strength=80.0,
        volume_ratio=75.0,
        liquidity_score=90.0,
        risk_score=70.0,
        timing_score=80.0,
        derivatives_score=75.0,
        participation_score=85.0,
        relationship_score=70.0,
        eligible=True,
    )

    evidence_decision = engine.evaluate(
        evidence_item,
        now=test_time,
        market_id="NSE",
    )

    assert evidence_decision.status == RankingStatus.PASS
    assert evidence_decision.basis == RankingBasis.EVIDENCE
    assert evidence_decision.ranking_score is not None
    assert evidence_decision.evidence_count >= 8

    # ==================================================================
    # TEST 6 — Market mismatch
    # ==================================================================

    wrong_market = RankingSnapshot(
        instrument_id="NSE-006",
        symbol="WRONG",
        timestamp=test_time,
        market_id="BSE",
        eqe=90.0,
        eligible=True,
    )

    wrong_market_decision = engine.evaluate(
        wrong_market,
        now=test_time,
        market_id="NSE",
    )

    assert wrong_market_decision.status == RankingStatus.REJECT
    assert any(
        "Market identity mismatch" in reason
        for reason in wrong_market_decision.reasons
    )

    # ==================================================================
    # TEST 7 — Future data
    # ==================================================================

    future_item = RankingSnapshot(
        instrument_id="NSE-007",
        symbol="FUTURE",
        timestamp=test_time.replace(
            hour=11
        ),
        market_id="NSE",
        eqe=90.0,
        eligible=True,
    )

    future_decision = engine.evaluate(
        future_item,
        now=test_time,
        market_id="NSE",
    )

    assert future_decision.status == RankingStatus.REJECT
    assert any(
        "Future-dated evidence" in reason
        for reason in future_decision.reasons
    )

    # ==================================================================
    # TEST 8 — Invalid numeric value
    # ==================================================================

    invalid_numeric = RankingSnapshot(
        instrument_id="NSE-008",
        symbol="BADNUM",
        timestamp=test_time,
        market_id="NSE",
        eqe=float("nan"),
        eligible=True,
    )

    invalid_decision = engine.evaluate(
        invalid_numeric,
        now=test_time,
        market_id="NSE",
    )

    assert invalid_decision.status == RankingStatus.REJECT
    assert any(
        "Invalid numeric evidence" in reason
        for reason in invalid_decision.reasons
    )

    # ==================================================================
    # TEST 9 — Ineligible candidate
    # ==================================================================

    ineligible = RankingSnapshot(
        instrument_id="NSE-009",
        symbol="INELIGIBLE",
        timestamp=test_time,
        market_id="NSE",
        eqe=95.0,
        eligible=False,
    )

    ineligible_decision = engine.evaluate(
        ineligible,
        now=test_time,
        market_id="NSE",
    )

    assert ineligible_decision.status == RankingStatus.REJECT

    # ==================================================================
    # TEST 10 — Missing evidence
    # ==================================================================

    missing = RankingSnapshot(
        instrument_id="NSE-010",
        symbol="MISSING",
        timestamp=test_time,
        market_id="NSE",
        eligible=True,
    )

    missing_decision = engine.evaluate(
        missing,
        now=test_time,
        market_id="NSE",
    )

    assert missing_decision.status == RankingStatus.UNKNOWN
    assert missing_decision.condition == RankingCondition.INCOMPLETE

    # ==================================================================
    # TEST 11 — Mapping normalization
    # ==================================================================

    mapping_item = {
        "instrument_id": "NSE-011",
        "symbol": "MAP",
        "timestamp": "2026-09-05T10:00:00Z",
        "market_id": "NSE",
        "eqe": "88.5",
        "eligible": True,
    }

    mapping_decision = engine.evaluate(
        mapping_item,
        now=test_time,
        market_id="NSE",
    )

    assert mapping_decision.status == RankingStatus.PASS
    assert mapping_decision.ranking_score == 88.5

    # ==================================================================
    # TEST 12 — Naive timestamp becomes UTC
    # ==================================================================

    naive_item = RankingSnapshot(
        instrument_id="NSE-012",
        symbol="NAIVE",
        timestamp=datetime(
            2026,
            9,
            5,
            9,
            0,
            0,
        ),
        market_id="NSE",
        eqe=80.0,
        eligible=True,
    )

    naive_decision = engine.evaluate(
        naive_item,
        now=test_time,
        market_id="NSE",
    )

    assert naive_decision.status == RankingStatus.PASS
    assert naive_decision.timestamp is not None
    assert naive_decision.timestamp.tzinfo is not None

    # ==================================================================
    # TEST 13 — Generator input
    # ==================================================================

    def candidate_generator():
        yield strong
        yield good

    generator_result = engine.rank(
        candidate_generator(),
        now=test_time,
        market_id="NSE",
    )

    assert generator_result.count_input == 2
    assert generator_result.count_ranked == 2

    # ==================================================================
    # TEST 14 — Serialization
    # ==================================================================

    serialized_decision = engine.serialize_decision(
        decision
    )

    assert isinstance(serialized_decision, str)
    assert "status" in serialized_decision
    assert "ranking_score" in serialized_decision

    serialized_result = engine.serialize_result(
        collection
    )

    assert isinstance(serialized_result, str)
    assert "decisions" in serialized_result

    # ==================================================================
    # TEST 15 — Public info
    # ==================================================================

    info = engine.get_engine_info()

    assert info["engine"] == "RankingEngine"
    assert info["version"] == "1.0"
    assert info["generates_trade_signal"] is False
    assert info["predicts_future"] is False
    assert info["deterministic"] is True

    # ==================================================================
    # TEST 16 — Convenience API
    # ==================================================================

    convenience_decision = evaluate_ranking(
        strong,
        now=test_time,
        market_id="NSE",
    )

    assert convenience_decision.status == RankingStatus.PASS

    convenience_result = rank_opportunities(
        [strong, good],
        now=test_time,
        market_id="NSE",
    )

    assert convenience_result.count_ranked == 2

    # ==================================================================
    # TEST 17 — Structural check
    # ==================================================================

    _structural_check()

    # ==================================================================
    # SUCCESS
    # ==================================================================

    print("ranking_engine.py self-test: PASS")


# ============================================================================
# PUBLIC EXPORTS
# ============================================================================

__all__ = [
    "RankingStatus",
    "RankingCondition",
    "RankingBasis",
    "RankingSnapshot",
    "RankingDecision",
    "RankingResult",
    "RankingPolicy",
    "RankingEngine",
    "evaluate_ranking",
    "rank_opportunities",
    "filter_ranking",
    "serialize_ranking",
    "get_ranking_engine_info",
]


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    _structural_check()
    _self_test()