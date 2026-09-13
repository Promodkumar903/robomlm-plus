"""
ROBOMLM_PLUS
Opportunity Intelligence Layer
ranking_engine.py

ROLE
----
Ranking Engine sits after candidate eligibility/evidence preparation.

Pipeline:
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

CORE RULE
---------
Ranking Engine ranks candidates.
It does NOT create a new market-intelligence formula.

It consumes authoritative upstream intelligence when available,
preserves evidence/provenance, validates point-in-time integrity,
and produces deterministic ordering.

It must never:
    - invent BUY/SELL signals
    - predict future price
    - replace D6 formulas
    - replace D13 decision authority
    - replace EQE/PFS/MCI formulas
    - silently convert missing evidence into positive evidence
    - use future information
    - fabricate confidence
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict, is_dataclass
from datetime import datetime, timezone
from enum import Enum
import json
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
    """
    Describes where the ranking value came from.

    UPSTREAM:
        Existing authoritative intelligence score.

    EVIDENCE:
        Explicitly permitted ranking evidence.

    NONE:
        No valid ranking basis.
    """

    UPSTREAM = "UPSTREAM"
    EVIDENCE = "EVIDENCE"
    NONE = "NONE"


# ============================================================================
# SNAPSHOT CONTRACT
# ============================================================================

@dataclass
class RankingSnapshot:
    """
    Point-in-time candidate snapshot.

    This is deliberately broad so that RankingEngine can consume
    normalized outputs from preceding intelligence layers without
    forcing those layers into a new formula.

    IMPORTANT:
    Missing values remain None.
    None is NOT converted into zero.
    """

    instrument_id: Optional[str] = None
    symbol: Optional[str] = None

    timestamp: Optional[datetime] = None

    market_id: Optional[str] = None
    venue_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Authoritative / upstream intelligence
    # ------------------------------------------------------------------

    eqe: Optional[float] = None
    pfs: Optional[float] = None
    mci: Optional[float] = None

    mts: Optional[float] = None
    lqs: Optional[float] = None
    rds: Optional[float] = None
    mcs: Optional[float] = None

    # ------------------------------------------------------------------
    # Supporting evidence
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
    # Upstream eligibility/status
    # ------------------------------------------------------------------

    eligible: Optional[bool] = None

    liquidity_status: Optional[str] = None
    risk_status: Optional[str] = None
    timing_status: Optional[str] = None
    intraday_status: Optional[str] = None

    # ------------------------------------------------------------------
    # Opportunity metadata
    # ------------------------------------------------------------------

    opportunity_type: Optional[str] = None
    direction: Optional[str] = None

    confidence: Optional[float] = None
    evidence_completeness: Optional[float] = None

    source: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# DECISION CONTRACT
# ============================================================================

@dataclass
class RankingDecision:
    """
    Ranking decision for one candidate.
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


# ============================================================================
# COLLECTION RESULT
# ============================================================================

@dataclass
class RankingResult:
    """
    Collection-level ranking result.
    """

    status: RankingStatus = RankingStatus.UNKNOWN

    decisions: List[RankingDecision] = field(
        default_factory=list
    )

    ranked: List[RankingDecision] = field(
        default_factory=list
    )

    review: List[RankingDecision] = field(
        default_factory=list
    )

    rejected: List[RankingDecision] = field(
        default_factory=list
    )

    unknown: List[RankingDecision] = field(
        default_factory=list
    )

    count_input: int = 0
    count_ranked: int = 0
    count_review: int = 0
    count_rejected: int = 0
    count_unknown: int = 0

    market_id: Optional[str] = None
    timestamp: Optional[datetime] = None

    provenance: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================================
# POLICY
# ============================================================================

@dataclass
class RankingPolicy:
    """
    Ranking policy.

    No invented intelligence threshold is hard-coded here.

    Thresholds may be supplied by the higher-level architecture
    once the authoritative ROBOMLM contract defines them.
    """

    # Minimum score gate.
    minimum_rank_score: Optional[float] = None

    # Optional review threshold.
    review_rank_score: Optional[float] = None

    # Minimum number of observable ranking inputs.
    minimum_evidence_count: int = 1

    # Optional completeness gates.
    minimum_evidence_completeness: Optional[float] = None
    review_evidence_completeness: Optional[float] = None

    # Data-integrity rules.
    require_timestamp: bool = True
    reject_future_data: bool = True

    # Market isolation.
    require_market_match: bool = True

    # Upstream eligibility.
    reject_ineligible: bool = True

    # Numeric validation.
    reject_invalid_numeric: bool = True

    # Authoritative upstream scores are preferred.
    prefer_upstream_scores: bool = True

    # Evidence fallback is allowed only when explicitly enabled.
    allow_evidence_ranking: bool = False

    # Deterministic tie-breaking.
    tie_break_symbol: bool = True


# ============================================================================
# ENGINE
# ============================================================================

class RankingEngine:
    """
    Deterministic opportunity ranking engine.

    The engine's job is ordering, not decision authority.
    """

    ENGINE_NAME = "RankingEngine"
    ENGINE_VERSION = "2.0"

    # ------------------------------------------------------------------
    # Authoritative ranking sources.
    #
    # Order matters only as a fallback preference.
    # The engine does not recompute these scores.
    # ------------------------------------------------------------------

    UPSTREAM_SCORE_FIELDS: Sequence[str] = (
        "eqe",
        "pfs",
        "mci",
    )

    # ------------------------------------------------------------------
    # Supporting evidence fields.
    # ------------------------------------------------------------------

    EVIDENCE_FIELDS: Sequence[str] = (
        "trend_strength",
        "volume_ratio",
        "liquidity_score",
        "risk_score",
        "timing_score",
        "derivatives_score",
        "participation_score",
        "relationship_score",
    )

    # ==================================================================
    # INITIALIZATION
    # ==================================================================

    def __init__(
        self,
        policy: Optional[RankingPolicy] = None,
    ) -> None:

        self.policy = policy or RankingPolicy()

    # ==================================================================
    # EVALUATE ONE CANDIDATE
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
                reasons=[
                    "Missing instrument identity"
                ],
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
                    reasons=[
                        "Missing point-in-time timestamp"
                    ],
                )

            warnings.append(
                "Timestamp is missing"
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
                )

        # --------------------------------------------------------------
        # Numeric integrity
        # --------------------------------------------------------------

        invalid_fields = self._invalid_numeric_fields(item)

        if (
            invalid_fields
            and self.policy.reject_invalid_numeric
        ):
            return self._decision(
                item,
                RankingStatus.REJECT,
                RankingCondition.UNKNOWN,
                reasons=[
                    "Invalid numeric evidence: "
                    + ", ".join(invalid_fields)
                ],
            )

        # --------------------------------------------------------------
        # Upstream eligibility
        # --------------------------------------------------------------

        if (
            self.policy.reject_ineligible
            and item.eligible is False
        ):
            return self._decision(
                item,
                RankingStatus.REJECT,
                RankingCondition.WEAK,
                reasons=[
                    "Candidate marked ineligible upstream"
                ],
            )

        # --------------------------------------------------------------
        # Evidence count
        # --------------------------------------------------------------

        evidence_count = self._evidence_count(
            item
        )

        if (
            evidence_count
            < self.policy.minimum_evidence_count
        ):
            return self._decision(
                item,
                RankingStatus.UNKNOWN,
                RankingCondition.INCOMPLETE,
                reasons=[
                    "Insufficient observable ranking evidence"
                ],
                evidence_count=evidence_count,
            )

        # --------------------------------------------------------------
        # Completeness
        # --------------------------------------------------------------

        completeness = (
            self._calculate_completeness(item)
        )

        if (
            self.policy.minimum_evidence_completeness
            is not None
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
                evidence_count=evidence_count,
                evidence_completeness=completeness,
            )

        if (
            self.policy.review_evidence_completeness
            is not None
            and completeness is not None
            and completeness
            < self.policy.review_evidence_completeness
        ):
            warnings.append(
                "Evidence completeness requires review"
            )

        # --------------------------------------------------------------
        # Resolve ranking basis
        # --------------------------------------------------------------

        ranking_score, basis = (
            self._resolve_ranking_score(item)
        )

        if ranking_score is None:

            return self._decision(
                item,
                RankingStatus.UNKNOWN,
                RankingCondition.INCOMPLETE,
                reasons=[
                    "No valid ranking basis available"
                ],
                warnings=warnings,
                evidence_count=evidence_count,
                evidence_completeness=completeness,
                basis=basis,
            )

        # --------------------------------------------------------------
        # Normalize only for presentation/classification.
        # --------------------------------------------------------------

        normalized_score = (
            self._normalize_score(
                ranking_score
            )
        )

        if normalized_score is None:

            return self._decision(
                item,
                RankingStatus.REJECT,
                RankingCondition.UNKNOWN,
                reasons=[
                    "Ranking score is outside supported 0-100 range"
                ],
                warnings=warnings,
                evidence_count=evidence_count,
                evidence_completeness=completeness,
                ranking_score=ranking_score,
                basis=basis,
            )

        # --------------------------------------------------------------
        # Condition
        # --------------------------------------------------------------

        condition = self._condition(
            normalized_score,
            completeness,
        )

        # --------------------------------------------------------------
        # Status
        # --------------------------------------------------------------

        status = RankingStatus.PASS

        if (
            self.policy.minimum_rank_score
            is not None
            and normalized_score
            < self.policy.minimum_rank_score
        ):
            status = RankingStatus.REJECT

            reasons.append(
                "Ranking score below minimum policy"
            )

        elif (
            self.policy.review_rank_score
            is not None
            and normalized_score
            < self.policy.review_rank_score
        ):
            status = RankingStatus.REVIEW

            warnings.append(
                "Ranking score requires review"
            )

        if (
            warnings
            and status == RankingStatus.PASS
        ):
            status = RankingStatus.REVIEW

        if not reasons:
            reasons.append(
                "Candidate ranked from valid point-in-time evidence"
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
            normalized_score=normalized_score,
            basis=basis,
        )

    # ==================================================================
    # COLLECTION RANKING
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

            decisions.append(
                decision
            )

        # --------------------------------------------------------------
        # Candidates that can actually be ranked.
        # --------------------------------------------------------------

        ranked_candidates = [
            decision
            for decision in decisions
            if (
                decision.status
                in (
                    RankingStatus.PASS,
                    RankingStatus.REVIEW,
                )
                and decision.ranking_score
                is not None
                and decision.normalized_score
                is not None
            )
        ]

        # --------------------------------------------------------------
        # Deterministic ordering.
        #
        # 1. Higher normalized score
        # 2. Higher evidence completeness
        # 3. Higher evidence count
        # 4. Stable symbol / instrument ID
        # --------------------------------------------------------------

        ranked_candidates.sort(
            key=self._ranking_sort_key
        )

        # --------------------------------------------------------------
        # Assign rank.
        # --------------------------------------------------------------

        for rank_number, decision in enumerate(
            ranked_candidates,
            start=1,
        ):
            decision.rank = rank_number

        # --------------------------------------------------------------
        # Buckets.
        # --------------------------------------------------------------

        ranked = [
            decision
            for decision in ranked_candidates
            if decision.status
            == RankingStatus.PASS
        ]

        review = [
            decision
            for decision in ranked_candidates
            if decision.status
            == RankingStatus.REVIEW
        ]

        rejected = [
            decision
            for decision in decisions
            if decision.status
            == RankingStatus.REJECT
        ]

        unknown = [
            decision
            for decision in decisions
            if decision.status
            == RankingStatus.UNKNOWN
        ]

        # --------------------------------------------------------------
        # Collection status.
        # --------------------------------------------------------------

        if ranked:
            collection_status = RankingStatus.PASS

        elif review:
            collection_status = RankingStatus.REVIEW

        elif unknown:
            collection_status = RankingStatus.UNKNOWN

        elif rejected:
            collection_status = RankingStatus.REJECT

        else:
            collection_status = RankingStatus.UNKNOWN

        return RankingResult(
            status=collection_status,
            decisions=decisions,
            ranked=ranked,
            review=review,
            rejected=rejected,
            unknown=unknown,
            count_input=len(items),
            count_ranked=len(ranked),
            count_review=len(review),
            count_rejected=len(rejected),
            count_unknown=len(unknown),
            market_id=market_id,
            timestamp=current_now,
            provenance={
                "engine": self.ENGINE_NAME,
                "engine_version": self.ENGINE_VERSION,
                "point_in_time": True,
                "deterministic": True,
                "ranking_only": True,
            },
        )

    # ==================================================================
    # FILTER / APPLY ALIASES
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
    # RANKING BASIS RESOLUTION
    # ==================================================================

    def _resolve_ranking_score(
        self,
        item: RankingSnapshot,
    ) -> Tuple[
        Optional[float],
        RankingBasis,
    ]:
        """
        Resolve an already-existing ranking basis.

        Priority:
            EQE → PFS → MCI

        These are consumed, not recomputed.

        If no upstream score exists, evidence ranking is disabled
        by default. This prevents this engine from silently becoming
        a new proprietary intelligence formula.
        """

        if self.policy.prefer_upstream_scores:

            for field_name in self.UPSTREAM_SCORE_FIELDS:

                value = getattr(
                    item,
                    field_name,
                    None,
                )

                if self._valid_number(value):

                    return (
                        float(value),
                        RankingBasis.UPSTREAM,
                    )

        if not self.policy.allow_evidence_ranking:
            return (
                None,
                RankingBasis.NONE,
            )

        # --------------------------------------------------------------
        # Explicit evidence-ranking mode.
        #
        # This mode does NOT invent weights.
        # It requires an already comparable 0-100 evidence field.
        #
        # Priority:
        # MTS → LQS → RDS → MCS
        #
        # These are consumed only when supplied.
        # --------------------------------------------------------------

        for field_name in (
            "mts",
            "lqs",
            "rds",
            "mcs",
        ):

            value = getattr(
                item,
                field_name,
                None,
            )

            if self._valid_number(value):

                return (
                    float(value),
                    RankingBasis.EVIDENCE,
                )

        return (
            None,
            RankingBasis.NONE,
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

        # Incomplete evidence must not be labelled strong merely
        # because one upstream score is high.
        if (
            completeness is not None
            and completeness < 0.50
        ):
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

        values = []

        for field_name in (
            *self.UPSTREAM_SCORE_FIELDS,
            "mts",
            "lqs",
            "rds",
            "mcs",
            *self.EVIDENCE_FIELDS,
            "confidence",
        ):

            values.append(
                getattr(
                    item,
                    field_name,
                    None,
                )
            )

        return sum(
            1
            for value in values
            if self._valid_number(value)
        )

    # ==================================================================
    # COMPLETENESS
    # ==================================================================

    def _calculate_completeness(
        self,
        item: RankingSnapshot,
    ) -> Optional[float]:
        """
        Supporting-evidence completeness.

        Important:
        upstream score availability is NOT treated as evidence
        completeness. A high EQE does not magically mean all
        underlying dimensions are present.
        """

        fields = [
            getattr(
                item,
                field_name,
                None,
            )
            for field_name in self.EVIDENCE_FIELDS
        ]

        if not fields:
            return None

        valid = sum(
            1
            for value in fields
            if self._valid_number(value)
        )

        return valid / len(fields)

    # ==================================================================
    # SORT KEY
    # ==================================================================

    def _ranking_sort_key(
        self,
        decision: RankingDecision,
    ) -> Tuple[
        float,
        float,
        int,
        str,
    ]:

        score = (
            decision.normalized_score
            if decision.normalized_score
            is not None
            else float("-inf")
        )

        completeness = (
            decision.evidence_completeness
            if decision.evidence_completeness
            is not None
            else 0.0
        )

        evidence_count = (
            decision.evidence_count
        )

        identifier = (
            decision.symbol
            or decision.instrument_id
            or ""
        )

        return (
            -score,
            -completeness,
            -evidence_count,
            identifier,
        )

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
            reasons=list(
                reasons or []
            ),
            warnings=list(
                warnings or []
            ),
            opportunity_type=item.opportunity_type,
            direction=item.direction,
            market_id=item.market_id,
            timestamp=item.timestamp,
            provenance={
                "engine": self.ENGINE_NAME,
                "engine_version": self.ENGINE_VERSION,
                "source": item.source,
                "point_in_time": True,
                "ranking_only": True,
            },
        )

    # ==================================================================
    # END OF PART 1
    # ==================================================================
# ============================================================================
# RANKING ENGINE — PART 2/3
# ============================================================================

    # ==================================================================
    # NORMALIZATION
    # ==================================================================

    def normalize(
        self,
        value: Any,
    ) -> RankingSnapshot:
        """
        Normalize mappings, dataclasses and compatible objects.

        Existing RankingSnapshot instances are returned as-is so that
        invalid numeric values are not silently hidden before the
        integrity layer sees them.
        """

        if isinstance(
            value,
            RankingSnapshot,
        ):
            return value

        mapping = self._to_mapping(
            value
        )

        timestamp = self._parse_timestamp(
            self._first(
                mapping,
                "timestamp",
                "time",
                "ts",
                "source_timestamp",
            )
        )

        metadata_value = self._first(
            mapping,
            "metadata",
            default={},
        )

        if isinstance(
            metadata_value,
            Mapping,
        ):
            metadata = dict(
                metadata_value
            )
        else:
            metadata = {
                "raw_metadata": metadata_value
            }

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

            # ----------------------------------------------------------
            # Upstream intelligence
            # ----------------------------------------------------------

            eqe=self._number(
                self._first(
                    mapping,
                    "eqe",
                    "eqe_score",
                )
            ),

            pfs=self._number(
                self._first(
                    mapping,
                    "pfs",
                    "pfs_score",
                )
            ),

            mci=self._number(
                self._first(
                    mapping,
                    "mci",
                    "mci_score",
                )
            ),

            mts=self._number(
                self._first(
                    mapping,
                    "mts",
                    "mts_score",
                )
            ),

            lqs=self._number(
                self._first(
                    mapping,
                    "lqs",
                    "lqs_score",
                )
            ),

            rds=self._number(
                self._first(
                    mapping,
                    "rds",
                    "rds_score",
                )
            ),

            mcs=self._number(
                self._first(
                    mapping,
                    "mcs",
                    "mcs_score",
                )
            ),

            # ----------------------------------------------------------
            # Supporting evidence
            # ----------------------------------------------------------

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

            # ----------------------------------------------------------
            # Eligibility / status
            # ----------------------------------------------------------

            eligible=self._boolean(
                self._first(
                    mapping,
                    "eligible",
                    "is_eligible",
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

            # ----------------------------------------------------------
            # Opportunity metadata
            # ----------------------------------------------------------

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

            metadata=metadata,
        )

    # ==================================================================
    # MAPPING HELPERS
    # ==================================================================

    @staticmethod
    def _to_mapping(
        value: Any,
    ) -> Mapping[str, Any]:

        if isinstance(
            value,
            Mapping,
        ):
            return value

        if is_dataclass(value):
            return asdict(
                value
            )

        if hasattr(
            value,
            "__dict__",
        ):
            return vars(
                value
            )

        raise TypeError(
            "RankingEngine accepts mappings, "
            "dataclasses, or objects exposing __dict__"
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

    # ==================================================================
    # NUMERIC HELPERS
    # ==================================================================

    @staticmethod
    def _number(
        value: Any,
    ) -> Optional[float]:

        if value is None:
            return None

        try:
            number = float(
                value
            )
        except (
            TypeError,
            ValueError,
        ):
            return None

        if not math.isfinite(
            number
        ):
            return None

        return number

    @staticmethod
    def _valid_number(
        value: Any,
    ) -> bool:

        if value is None:
            return False

        try:
            number = float(
                value
            )
        except (
            TypeError,
            ValueError,
        ):
            return False

        return math.isfinite(
            number
        )

    @staticmethod
    def _boolean(
        value: Any,
    ) -> Optional[bool]:

        if value is None:
            return None

        if isinstance(
            value,
            bool,
        ):
            return value

        if isinstance(
            value,
            (int, float),
        ):

            if value == 1:
                return True

            if value == 0:
                return False

        if isinstance(
            value,
            str,
        ):

            normalized = (
                value
                .strip()
                .lower()
            )

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

        text = str(
            value
        ).strip()

        return (
            text
            if text
            else None
        )

    # ==================================================================
    # TIMESTAMP HELPERS
    # ==================================================================

    @staticmethod
    def _parse_timestamp(
        value: Any,
    ) -> Optional[datetime]:

        if value is None:
            return None

        if isinstance(
            value,
            datetime,
        ):
            return RankingEngine._ensure_aware(
                value
            )

        if isinstance(
            value,
            (int, float),
        ):

            try:

                number = float(
                    value
                )

                if not math.isfinite(
                    number
                ):
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

        if isinstance(
            value,
            str,
        ):

            text = (
                value
                .strip()
            )

            if not text:
                return None

            if text.endswith(
                "Z"
            ):
                text = (
                    text[:-1]
                    + "+00:00"
                )

            try:

                parsed = datetime.fromisoformat(
                    text
                )

                return RankingEngine._ensure_aware(
                    parsed
                )

            except ValueError:
                return None

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

    # ==================================================================
    # INVALID NUMERIC FIELD DETECTION
    # ==================================================================

    def _invalid_numeric_fields(
        self,
        item: RankingSnapshot,
    ) -> List[str]:

        field_names = (
            *self.UPSTREAM_SCORE_FIELDS,
            "mts",
            "lqs",
            "rds",
            "mcs",
            *self.EVIDENCE_FIELDS,
            "confidence",
            "evidence_completeness",
        )

        invalid: List[str] = []

        for field_name in field_names:

            value = getattr(
                item,
                field_name,
                None,
            )

            if value is None:
                continue

            try:

                number = float(
                    value
                )

            except (
                TypeError,
                ValueError,
            ):

                invalid.append(
                    field_name
                )
                continue

            if not math.isfinite(
                number
            ):
                invalid.append(
                    field_name
                )

        return invalid

    # ==================================================================
    # SCORE NORMALIZATION
    # ==================================================================

    @staticmethod
    def _normalize_score(
        value: Optional[float],
    ) -> Optional[float]:

        if not RankingEngine._valid_number(
            value
        ):
            return None

        number = float(
            value
        )

        # Ranking Engine expects already comparable
        # 0–100 intelligence scores.
        #
        # It does not invent transformations for unknown scales.

        if not (
            0.0
            <= number
            <= 100.0
        ):
            return None

        return number

    # ==================================================================
    # PUBLIC SERIALIZATION
    # ==================================================================

    @staticmethod
    def _safe_enum_value(
        value: Any,
    ) -> Any:

        if isinstance(
            value,
            Enum,
        ):
            return value.value

        return value

    @classmethod
    def _json_safe(
        cls,
        value: Any,
    ) -> Any:

        if isinstance(
            value,
            Enum,
        ):
            return value.value

        if isinstance(
            value,
            datetime,
        ):
            return cls._ensure_aware(
                value
            ).isoformat()

        if is_dataclass(
            value
        ):
            return cls._json_safe(
                asdict(
                    value
                )
            )

        if isinstance(
            value,
            Mapping,
        ):
            return {
                str(key): cls._json_safe(
                    item
                )
                for key, item
                in value.items()
            }

        if isinstance(
            value,
            (list, tuple, set),
        ):
            return [
                cls._json_safe(
                    item
                )
                for item in value
            ]

        if isinstance(
            value,
            float,
        ):

            if not math.isfinite(
                value
            ):
                return None

            return value

        return value

    def snapshot_to_dict(
        self,
        snapshot: RankingSnapshot,
    ) -> Dict[str, Any]:

        return self._json_safe(
            snapshot
        )

    def decision_to_dict(
        self,
        decision: RankingDecision,
    ) -> Dict[str, Any]:

        return self._json_safe(
            decision
        )

    def result_to_dict(
        self,
        result: RankingResult,
    ) -> Dict[str, Any]:

        return self._json_safe(
            result
        )

    def policy_to_dict(
        self,
    ) -> Dict[str, Any]:

        return self._json_safe(
            self.policy
        )

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
            self.decision_to_dict(
                decision
            ),
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
            self.result_to_dict(
                result
            ),
            indent=indent,
            sort_keys=True,
        )

    # ==================================================================
    # ENGINE INFORMATION
    # ==================================================================

    def get_engine_info(
        self,
    ) -> Dict[str, Any]:

        return {
            "engine": self.ENGINE_NAME,
            "engine_version": self.ENGINE_VERSION,
            "purpose": (
                "Deterministic ranking of "
                "already-evaluated opportunity candidates"
            ),
            "ranking_only": True,
            "generates_trade_signal": False,
            "predicts_future": False,
            "recomputes_authoritative_formulas": False,
            "point_in_time": True,
            "deterministic": True,
            "upstream_scores_preferred": (
                self.policy.prefer_upstream_scores
            ),
            "evidence_fallback_enabled": (
                self.policy.allow_evidence_ranking
            ),
            "policy": self.policy_to_dict(),
        }


# ============================================================================
# END OF PART 2
# ============================================================================
# ============================================================
# PART 3 / 3
# Public API, Structural Validation, Self-Test
# ============================================================

    def evaluate_many(
        self,
        snapshots: Iterable[Any],
        *,
        market_id: Optional[str] = None,
        now: Optional[datetime] = None,
    ) -> RankingResult:
        """
        Evaluate and rank an iterable of candidates.

        This is an explicit public alias around rank() so callers
        that semantically think in terms of batch evaluation can
        use the engine without changing ranking behavior.
        """
        return self.rank(
            snapshots,
            market_id=market_id,
            now=now,
        )

    def validate_snapshot(
        self,
        snapshot: Any,
        *,
        market_id: Optional[str] = None,
        now: Optional[datetime] = None,
    ) -> RankingDecision:
        """
        Validate one candidate through the complete ranking gate.

        No separate validation logic is invented here. The candidate
        goes through the same deterministic evaluation path used by
        normal ranking.
        """
        return self.evaluate(
            snapshot,
            market_id=market_id,
            now=now,
        )

    def rank_top(
        self,
        snapshots: Iterable[Any],
        *,
        limit: int = 10,
        market_id: Optional[str] = None,
        now: Optional[datetime] = None,
    ) -> RankingResult:
        """
        Return a RankingResult containing at most `limit` ranked
        PASS candidates.

        The full deterministic evaluation is still performed first.
        This method only truncates the final ranked presentation;
        it does not alter ranking scores or eligibility.
        """
        try:
            limit = int(limit)
        except (TypeError, ValueError):
            limit = 10

        if limit < 1:
            limit = 1

        result = self.rank(
            snapshots,
            market_id=market_id,
            now=now,
        )

        result.ranked = result.ranked[:limit]

        # Re-number visible ranks after truncation.
        for index, decision in enumerate(result.ranked, start=1):
            decision.rank = index

        result.count_ranked = len(result.ranked)

        return result


# ============================================================
# MODULE-LEVEL PUBLIC API
# ============================================================

def evaluate_ranking(
    snapshot: Any,
    *,
    policy: Optional[RankingPolicy] = None,
    market_id: Optional[str] = None,
    now: Optional[datetime] = None,
) -> RankingDecision:
    """
    Evaluate one candidate using RankingEngine.
    """
    engine = RankingEngine(policy=policy)
    return engine.evaluate(
        snapshot,
        market_id=market_id,
        now=now,
    )


def rank_opportunities(
    snapshots: Iterable[Any],
    *,
    policy: Optional[RankingPolicy] = None,
    market_id: Optional[str] = None,
    now: Optional[datetime] = None,
) -> RankingResult:
    """
    Rank a collection of candidates deterministically.
    """
    engine = RankingEngine(policy=policy)
    return engine.rank(
        snapshots,
        market_id=market_id,
        now=now,
    )


def filter_ranked_opportunities(
    snapshots: Iterable[Any],
    *,
    policy: Optional[RankingPolicy] = None,
    market_id: Optional[str] = None,
    now: Optional[datetime] = None,
) -> RankingResult:
    """
    Compatibility-oriented filtering API.

    Ranking remains the governing operation; this does not create
    a second filtering/scoring algorithm.
    """
    engine = RankingEngine(policy=policy)
    return engine.filter(
        snapshots,
        market_id=market_id,
        now=now,
    )


def serialize_ranking_decision(
    decision: RankingDecision,
) -> str:
    """
    Serialize one RankingDecision to deterministic JSON.
    """
    engine = RankingEngine()
    return engine.serialize_decision(
        decision
    )


def serialize_ranking_result(
    result: RankingResult,
) -> str:
    """
    Serialize one RankingResult to deterministic JSON.
    """
    engine = RankingEngine()
    return engine.serialize_result(
        result
    )


# ============================================================
# STRUCTURAL SELF-TEST
# ============================================================

def _self_test() -> None:
    """
    Production-oriented deterministic self-test.

    Important:
    - Tests the actual public contract.
    - Does not use fabricated future values.
    - Uses complete supporting evidence when expecting STRONG.
    - Separately tests sparse-but-valid upstream ranking.
    - Tests point-in-time protection.
    - Tests market identity protection.
    - Tests deterministic ranking and tie-breaking.
    """

    now = datetime(
        2026,
        9,
        5,
        10,
        0,
        0,
        tzinfo=timezone.utc,
    )

    market = "NIFTY"

    # --------------------------------------------------------
    # Complete supporting evidence helper
    # --------------------------------------------------------

    def complete_supporting_evidence(
        *,
        trend: float = 80.0,
        volume: float = 1.50,
        liquidity: float = 82.0,
        risk: float = 25.0,
        timing: float = 78.0,
        derivatives: float = 76.0,
        participation: float = 81.0,
        relationships: float = 74.0,
    ) -> Dict[str, float]:
        return {
            "trend_strength": trend,
            "volume_ratio": volume,
            "liquidity_score": liquidity,
            "risk_score": risk,
            "timing_score": timing,
            "derivatives_score": derivatives,
            "participation_score": participation,
            "relationship_score": relationships,
        }

    # --------------------------------------------------------
    # 1. Strong candidate
    # --------------------------------------------------------

    strong = RankingSnapshot(
        instrument_id="NIFTY-001",
        symbol="NIFTY",
        timestamp=now,
        market_id=market,
        venue_id="NSE",
        eqe=91.0,
        eligible=True,
        liquidity_status="PASS",
        risk_status="PASS",
        timing_status="PASS",
        intraday_status="PASS",
        opportunity_type="TREND_CONTINUATION",
        direction="LONG",
        confidence=0.91,
        source="test",
        **complete_supporting_evidence(),
    )

    engine = RankingEngine()

    strong_decision = engine.evaluate(
        strong,
        market_id=market,
        now=now,
    )

    assert strong_decision.status == RankingStatus.PASS
    assert strong_decision.condition == RankingCondition.STRONG
    assert strong_decision.ranking_score == 91.0
    assert strong_decision.normalized_score == 91.0
    assert strong_decision.basis == RankingBasis.UPSTREAM
    assert strong_decision.evidence_count >= 9
    assert strong_decision.evidence_completeness == 1.0

    # --------------------------------------------------------
    # 2. Good candidate using PFS
    # --------------------------------------------------------

    good = RankingSnapshot(
        instrument_id="NIFTY-002",
        symbol="BANKNIFTY",
        timestamp=now,
        market_id=market,
        venue_id="NSE",
        pfs=72.0,
        eligible=True,
        liquidity_status="PASS",
        risk_status="PASS",
        timing_status="PASS",
        intraday_status="PASS",
        opportunity_type="MOMENTUM",
        direction="LONG",
        confidence=0.78,
        source="test",
        **complete_supporting_evidence(
            trend=72.0,
            volume=1.30,
            liquidity=75.0,
            risk=30.0,
            timing=70.0,
            derivatives=68.0,
            participation=73.0,
            relationships=69.0,
        ),
    )

    good_decision = engine.evaluate(
        good,
        market_id=market,
        now=now,
    )

    assert good_decision.status == RankingStatus.PASS
    assert good_decision.condition == RankingCondition.GOOD
    assert good_decision.ranking_score == 72.0
    assert good_decision.basis == RankingBasis.UPSTREAM

    # --------------------------------------------------------
    # 3. Sparse but valid upstream score
    # --------------------------------------------------------

    sparse = RankingSnapshot(
        instrument_id="NIFTY-003",
        symbol="FINNIFTY",
        timestamp=now,
        market_id=market,
        venue_id="NSE",
        mci=84.0,
        eligible=True,
        source="upstream_mci",
    )

    sparse_decision = engine.evaluate(
        sparse,
        market_id=market,
        now=now,
    )

    assert sparse_decision.status == RankingStatus.PASS
    assert sparse_decision.ranking_score == 84.0
    assert sparse_decision.basis == RankingBasis.UPSTREAM
    assert sparse_decision.condition == RankingCondition.INCOMPLETE

    # --------------------------------------------------------
    # 4. Missing score
    # --------------------------------------------------------

    missing = RankingSnapshot(
        instrument_id="NIFTY-004",
        symbol="MIDCPNIFTY",
        timestamp=now,
        market_id=market,
        venue_id="NSE",
        eligible=True,
        source="test",
    )

    missing_decision = engine.evaluate(
        missing,
        market_id=market,
        now=now,
    )

    assert missing_decision.status == RankingStatus.UNKNOWN
    assert missing_decision.ranking_score is None

    # --------------------------------------------------------
    # 5. Ineligible candidate
    # --------------------------------------------------------

    ineligible = RankingSnapshot(
        instrument_id="NIFTY-005",
        symbol="REJECTED",
        timestamp=now,
        market_id=market,
        venue_id="NSE",
        eqe=90.0,
        eligible=False,
        source="test",
    )

    ineligible_decision = engine.evaluate(
        ineligible,
        market_id=market,
        now=now,
    )

    assert ineligible_decision.status == RankingStatus.REJECT

    # --------------------------------------------------------
    # 6. Market mismatch
    # --------------------------------------------------------

    mismatch = RankingSnapshot(
        instrument_id="BTC-001",
        symbol="BTCUSDT",
        timestamp=now,
        market_id="CRYPTO",
        venue_id="BINANCE",
        eqe=90.0,
        eligible=True,
        source="test",
    )

    mismatch_decision = engine.evaluate(
        mismatch,
        market_id=market,
        now=now,
    )

    assert mismatch_decision.status == RankingStatus.REJECT

    # --------------------------------------------------------
    # 7. Future timestamp
    # --------------------------------------------------------

    future = RankingSnapshot(
        instrument_id="NIFTY-006",
        symbol="FUTURE-DATA",
        timestamp=now.replace(hour=11),
        market_id=market,
        venue_id="NSE",
        eqe=90.0,
        eligible=True,
        source="test",
    )

    future_decision = engine.evaluate(
        future,
        market_id=market,
        now=now,
    )

    assert future_decision.status == RankingStatus.REJECT

    # --------------------------------------------------------
    # 8. Invalid non-finite numeric value
    # --------------------------------------------------------

    invalid_numeric = RankingSnapshot(
        instrument_id="NIFTY-007",
        symbol="INVALID-NUMERIC",
        timestamp=now,
        market_id=market,
        venue_id="NSE",
        eqe=float("nan"),
        eligible=True,
        source="test",
    )

    invalid_decision = engine.evaluate(
        invalid_numeric,
        market_id=market,
        now=now,
    )

    assert invalid_decision.status == RankingStatus.REJECT

    # --------------------------------------------------------
    # 9. Evidence fallback explicitly enabled
    # --------------------------------------------------------

    evidence_policy = RankingPolicy(
        allow_evidence_ranking=True,
        minimum_evidence_count=1,
    )

    evidence_engine = RankingEngine(policy=evidence_policy)

    evidence_candidate = RankingSnapshot(
        instrument_id="NIFTY-008",
        symbol="EVIDENCE-ONLY",
        timestamp=now,
        market_id=market,
        venue_id="NSE",
        mts=82.0,
        eligible=True,
        source="test",
    )

    evidence_decision = evidence_engine.evaluate(
        evidence_candidate,
        market_id=market,
        now=now,
    )

    assert evidence_decision.status == RankingStatus.PASS
    assert evidence_decision.ranking_score == 82.0
    assert evidence_decision.basis == RankingBasis.EVIDENCE

    # --------------------------------------------------------
    # 10. Evidence fallback disabled by default
    # --------------------------------------------------------

    no_fallback_candidate = RankingSnapshot(
        instrument_id="NIFTY-009",
        symbol="NO-FALLBACK",
        timestamp=now,
        market_id=market,
        venue_id="NSE",
        mts=82.0,
        eligible=True,
        source="test",
    )

    no_fallback_decision = engine.evaluate(
        no_fallback_candidate,
        market_id=market,
        now=now,
    )

    assert no_fallback_decision.status == RankingStatus.UNKNOWN
    assert no_fallback_decision.ranking_score is None

    # --------------------------------------------------------
    # 11. Deterministic collection ranking
    # --------------------------------------------------------

    candidates = [
        strong,
        good,
        sparse,
    ]

    result = engine.rank(
        candidates,
        market_id=market,
        now=now,
    )

    assert result.count_input == 3
    assert result.count_ranked == 3
    assert len(result.ranked) == 3
    assert result.ranked[0].symbol == "NIFTY"
    assert result.ranked[0].rank == 1
    assert result.ranked[1].symbol == "FINNIFTY"
    assert result.ranked[1].rank == 2
    assert result.ranked[2].symbol == "BANKNIFTY"
    assert result.ranked[2].rank == 3

    # --------------------------------------------------------
    # 12. Stable tie-break
    # --------------------------------------------------------

    tie_a = RankingSnapshot(
        instrument_id="TIE-A",
        symbol="AAA",
        timestamp=now,
        market_id=market,
        venue_id="NSE",
        eqe=80.0,
        eligible=True,
        source="test",
    )

    tie_b = RankingSnapshot(
        instrument_id="TIE-B",
        symbol="BBB",
        timestamp=now,
        market_id=market,
        venue_id="NSE",
        eqe=80.0,
        eligible=True,
        source="test",
    )

    tie_result = engine.rank(
        [tie_b, tie_a],
        market_id=market,
        now=now,
    )

    assert tie_result.ranked[0].symbol == "AAA"
    assert tie_result.ranked[1].symbol == "BBB"

    # --------------------------------------------------------
    # 13. Review threshold
    # --------------------------------------------------------

    review_policy = RankingPolicy(
        review_rank_score=85.0,
        minimum_evidence_count=1,
    )

    review_engine = RankingEngine(policy=review_policy)

    review_candidate = RankingSnapshot(
        instrument_id="NIFTY-010",
        symbol="REVIEW",
        timestamp=now,
        market_id=market,
        venue_id="NSE",
        eqe=83.0,
        eligible=True,
        source="test",
    )

    review_decision = review_engine.evaluate(
        review_candidate,
        market_id=market,
        now=now,
    )

    assert review_decision.status == RankingStatus.REVIEW

    # --------------------------------------------------------
    # 14. Minimum score rejection
    # --------------------------------------------------------

    minimum_policy = RankingPolicy(
        minimum_rank_score=80.0,
        minimum_evidence_count=1,
    )

    minimum_engine = RankingEngine(policy=minimum_policy)

    weak_candidate = RankingSnapshot(
        instrument_id="NIFTY-011",
        symbol="BELOW-MINIMUM",
        timestamp=now,
        market_id=market,
        venue_id="NSE",
        eqe=65.0,
        eligible=True,
        source="test",
    )

    weak_decision = minimum_engine.evaluate(
        weak_candidate,
        market_id=market,
        now=now,
    )

    assert weak_decision.status == RankingStatus.REJECT

    # --------------------------------------------------------
    # 15. Mapping normalization
    # --------------------------------------------------------

    mapping_candidate = {
        "instrument_id": "NIFTY-012",
        "symbol": "MAPPED",
        "timestamp": now.isoformat(),
        "market_id": market,
        "venue_id": "NSE",
        "eqe": 88.5,
        "eligible": True,
        "source": "mapping_test",
    }

    mapping_decision = engine.evaluate(
        mapping_candidate,
        market_id=market,
        now=now,
    )

    assert mapping_decision.status == RankingStatus.PASS
    assert mapping_decision.ranking_score == 88.5

    # --------------------------------------------------------
    # 16. Generator input
    # --------------------------------------------------------

    generator_result = engine.rank(
        (item for item in [strong, good]),
        market_id=market,
        now=now,
    )

    assert generator_result.count_input == 2
    assert generator_result.count_ranked == 2

    # --------------------------------------------------------
    # 17. Serialization
    # --------------------------------------------------------

    decision_json = serialize_ranking_decision(strong_decision)
    result_json = serialize_ranking_result(result)

    assert isinstance(decision_json, str)
    assert isinstance(result_json, str)

    decision_payload = json.loads(decision_json)
    result_payload = json.loads(result_json)

    assert decision_payload["instrument_id"] == "NIFTY-001"
    assert result_payload["count_input"] == 3

    # --------------------------------------------------------
    # 18. Engine metadata
    # --------------------------------------------------------

    info = engine.get_engine_info()

    assert info["engine"] == "RankingEngine"
    assert info["engine_version"] == "2.0"
    assert info["ranking_only"] is True
    assert info["generates_trade_signal"] is False
    assert info["predicts_future"] is False
    assert info["point_in_time"] is True
    assert info["deterministic"] is True

    # --------------------------------------------------------
    # 19. Top ranking API
    # --------------------------------------------------------

    top_result = engine.rank_top(
        [strong, good, sparse],
        limit=2,
        market_id=market,
        now=now,
    )

    assert len(top_result.ranked) == 2
    assert top_result.ranked[0].rank == 1
    assert top_result.ranked[1].rank == 2

    # --------------------------------------------------------
    # 20. Convenience APIs
    # --------------------------------------------------------

    convenience_decision = evaluate_ranking(
        strong,
        market_id=market,
        now=now,
    )

    convenience_result = rank_opportunities(
        [strong, good],
        market_id=market,
        now=now,
    )

    filtered_result = filter_ranked_opportunities(
        [strong, good],
        market_id=market,
        now=now,
    )

    assert convenience_decision.status == RankingStatus.PASS
    assert convenience_result.count_ranked == 2
    assert filtered_result.count_ranked == 2

    # --------------------------------------------------------
    # Final success marker
    # --------------------------------------------------------

    print("ranking_engine.py self-test: PASS")


# ============================================================
# PUBLIC EXPORTS
# ============================================================

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
    "filter_ranked_opportunities",
    "serialize_ranking_decision",
    "serialize_ranking_result",
]


# ============================================================
# DIRECT EXECUTION
# ============================================================

if __name__ == "__main__":
    _self_test()
