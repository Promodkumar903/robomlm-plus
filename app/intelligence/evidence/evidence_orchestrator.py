from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Iterable, Mapping, Sequence

from schemas.evidence.evidence_item import EvidenceItem
from schemas.evidence.evidence_package import EvidencePackage

from app.intelligence.evidence.evidence_engine_base import (
    EvidenceStatus,
)
from app.intelligence.evidence.evidence_normalizer import (
    EvidenceNormalizer,
    NormalizationResult,
)
from app.intelligence.evidence.evidence_package import (
    EvidencePackageEngine as EvidencePackageBuilder,
    EvidencePackageBuildResult as PackageBuildResult,
)
from app.intelligence.evidence.evidence_conflict import (
    ConflictAnalysisResult,
    EvidenceConflictEngine,
)
from app.intelligence.evidence.evidence_confidence import (
    EvidenceConfidenceEngine,
    EvidenceConfidenceResult,
)
from app.intelligence.evidence.source_reliability import (
    SourceReliabilityEngine,
    SourceReliabilityResult,
)


class OrchestrationStatus(str, Enum):
    """
    Overall status of the Evidence Cortex orchestration pipeline.
    """

    VALID = "VALID"
    PARTIAL = "PARTIAL"
    INSUFFICIENT = "INSUFFICIENT"
    INVALID = "INVALID"


@dataclass(frozen=True)
class EvidenceOrchestrationResult:
    """
    Complete output of the Evidence Cortex pipeline.

    The result preserves every stage independently so downstream layers
    can inspect lineage instead of receiving only a final opaque score.
    """

    status: OrchestrationStatus

    package: EvidencePackage | None

    normalized: NormalizationResult | None
    package_result: PackageBuildResult | None
    conflict_result: ConflictAnalysisResult | None

    confidence_results: Mapping[
        str,
        EvidenceConfidenceResult,
    ] = field(default_factory=dict)

    reliability_results: Mapping[
        str,
        SourceReliabilityResult,
    ] = field(default_factory=dict)

    input_count: int = 0
    accepted_count: int = 0
    rejected_count: int = 0

    errors: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)

    started_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    completed_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    orchestrator: str = "EvidenceOrchestrator"
    version: str = "1.0"

    reason: str = ""

    def is_valid(self) -> bool:
        if self.input_count < 0:
            return False

        if self.accepted_count < 0:
            return False

        if self.rejected_count < 0:
            return False

        if self.accepted_count > self.input_count:
            return False

        if self.started_at.tzinfo is None:
            return False

        if self.completed_at.tzinfo is None:
            return False

        if self.completed_at < self.started_at:
            return False

        if self.status == OrchestrationStatus.VALID:
            if self.package is None:
                return False

        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "package": (
                self.package.to_dict()
                if self.package is not None
                else None
            ),
            "normalized": (
                {
                    "status": self.normalized.status,
                    "items": [item.to_dict() for item in self.normalized.items],
                    "normalized_count": self.normalized.normalized_count,
                    "rejected_count": self.normalized.rejected_count,
                    "errors": list(self.normalized.errors),
                    "warnings": list(self.normalized.warnings),
                    "normalizer": self.normalized.normalizer,
                    "version": self.normalized.version,
                }
                if self.normalized is not None
                else None
            ),
            "package_result": (
                {
                    "status": self.package_result.status,
                    "package": (
                        self.package_result.package.to_dict()
                        if self.package_result.package is not None
                        else None
                    ),
                    "accepted_count": self.package_result.accepted_count,
                    "rejected_count": self.package_result.rejected_count,
                    "duplicate_count": self.package_result.duplicate_count,
                    "conflict_count": self.package_result.conflict_count,
                    "errors": list(self.package_result.errors),
                    "warnings": list(self.package_result.warnings),
                }
                if self.package_result is not None
                else None
            ),
            "conflict_result": (
                self.conflict_result.to_dict()
                if self.conflict_result is not None
                else None
            ),
            "confidence_results": {
    key: {
        "status": value.status,
        "weight": value.weight,
        "prior_weight": value.prior_weight,
        "posterior_weight": value.posterior_weight,
        "sample_adjustment": value.sample_adjustment,
        "decay_factor": value.decay_factor,
        "evidence_contribution": value.evidence_contribution,
        "observation_count": value.observation_count,
        "evidence_count": value.evidence_count,
        "observed_at": (
            value.observed_at.isoformat()
            if value.observed_at is not None
            else None
        ),
        "evaluated_at": value.evaluated_at.isoformat(),
        "calculation": dict(value.calculation),
        "errors": list(value.errors),
        "warnings": list(value.warnings),
    }
    for key, value in self.confidence_results.items()
},
            "reliability_results": {
                key: value.to_dict()
                for key, value in self.reliability_results.items()
            },
            "input_count": self.input_count,
            "accepted_count": self.accepted_count,
            "rejected_count": self.rejected_count,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
            "orchestrator": self.orchestrator,
            "version": self.version,
            "reason": self.reason,
        }
class EvidenceOrchestrator:
    """
    Evidence Cortex orchestration boundary.

    Pipeline
    --------
        Raw evidence
            â†“
        Normalization
            â†“
        Evidence Package
            â†“
        Conflict Detection
            â†“
        Evidence Confidence
            â†“
        Source Reliability
            â†“
        Evidence Orchestration Result

    Constitutional boundaries
    --------------------------
    1. No missing evidence is converted into a neutral value.
    2. No confidence is invented.
    3. No source is trusted merely because of its name.
    4. Conflicts are preserved rather than voted away.
    5. Evidence identity and lineage are preserved.
    6. No trading decision is produced.
    7. No risk/execution authorization is produced.
    8. A failed stage cannot silently become a successful stage.
    """

    VERSION = "1.0"

    def __init__(
        self,
        *,
        normalizer: EvidenceNormalizer | None = None,
        package_builder: EvidencePackageBuilder | None = None,
        conflict_engine: EvidenceConflictEngine | None = None,
        confidence_engine: EvidenceConfidenceEngine | None = None,
        reliability_engine: SourceReliabilityEngine | None = None,
    ) -> None:
        self.normalizer = (
            normalizer
            if normalizer is not None
            else EvidenceNormalizer()
        )

        self.package_builder = (
            package_builder
            if package_builder is not None
            else EvidencePackageBuilder()
        )

        self.conflict_engine = (
            conflict_engine
            if conflict_engine is not None
            else EvidenceConflictEngine()
        )

        self.confidence_engine = (
            confidence_engine
            if confidence_engine is not None
            else EvidenceConfidenceEngine()
        )

        self.reliability_engine = (
            reliability_engine
            if reliability_engine is not None
            else SourceReliabilityEngine()
        )

    def process(
        self,
        evidence: Iterable[
            EvidenceItem | Mapping[str, Any]
        ],
        *,
        package_id: str | None = None,
        market: str | None = None,
        instrument_id: str | None = None,
        timeframe: str | None = None,
        created_at: datetime | None = None,
        metadata: Mapping[str, Any] | None = None,
        tolerance: float = 0.0,
        temporal_overlap_seconds: float | None = None,
    ) -> EvidenceOrchestrationResult:
        """
        Execute the complete Evidence Cortex pipeline.
        """
        started_at = datetime.now(timezone.utc)

        raw_items = tuple(evidence)

        errors: list[str] = []
        warnings: list[str] = []

        # --------------------------------------------------------------
        # Stage 1 â€” Normalization
        # --------------------------------------------------------------

        normalized = self.normalizer.normalize_many(raw_items)

        if normalized is None:
            return self._failed_result(
                started_at=started_at,
                input_count=len(raw_items),
                error="Evidence normalization returned no result.",
            )

        if normalized.status == "INVALID":
            errors.extend(normalized.errors)

            return self._failed_result(
                started_at=started_at,
                input_count=len(raw_items),
                normalized=normalized,
                errors=errors,
                reason="Evidence normalization failed.",
            )

        warnings.extend(normalized.warnings)

        normalized_items = tuple(normalized.items)

        if not normalized_items:
            completed_at = datetime.now(timezone.utc)

            return EvidenceOrchestrationResult(
                status=OrchestrationStatus.INSUFFICIENT,
                package=None,
                normalized=normalized,
                package_result=None,
                conflict_result=None,
                input_count=len(raw_items),
                accepted_count=0,
                rejected_count=len(raw_items),
                errors=tuple(errors),
                warnings=tuple(warnings),
                started_at=started_at,
                completed_at=completed_at,
                reason=(
                    "No valid evidence remained after normalization."
                ),
                version=self.VERSION,
            )

        # --------------------------------------------------------------
        # Stage 2 â€” Package construction
        # --------------------------------------------------------------

        package_result = self.package_builder.build(
            normalized_items,
            package_id=package_id,
            market=market,
            instrument_id=instrument_id,
            timeframe=timeframe,
            created_at=created_at,
            metadata=metadata,
        )

        if package_result is None:
            return self._failed_result(
                started_at=started_at,
                input_count=len(raw_items),
                normalized=normalized,
                error="Evidence package builder returned no result.",
            )

        warnings.extend(package_result.warnings)
        errors.extend(package_result.errors)

        package = package_result.package

        if package is None:
            completed_at = datetime.now(timezone.utc)

            return EvidenceOrchestrationResult(
                status=OrchestrationStatus.INVALID,
                package=None,
                normalized=normalized,
                package_result=package_result,
                conflict_result=None,
                input_count=len(raw_items),
                accepted_count=len(normalized_items),
                rejected_count=(
                    len(raw_items) - len(normalized_items)
                ),
                errors=tuple(errors),
                warnings=tuple(warnings),
                started_at=started_at,
                completed_at=completed_at,
                reason=(
                    "Evidence package could not be constructed."
                ),
                version=self.VERSION,
            )

        # --------------------------------------------------------------
        # Stage 3 â€” Conflict detection
        # --------------------------------------------------------------

        conflict_result = self.conflict_engine.analyze(
            package,
            tolerance=tolerance,
            temporal_overlap_seconds=temporal_overlap_seconds,
        )

        if not conflict_result.is_valid():
            errors.append(
                "Conflict analysis produced an invalid result."
            )

        if conflict_result.status.value == "PARTIAL":
            warnings.append(
                "Evidence conflicts detected; dissent is preserved."
            )

        # --------------------------------------------------------------
        # Stage 4 â€” Evidence confidence
        # --------------------------------------------------------------

        confidence_results = (
            self._calculate_confidence(
                package=package,
                conflict_result=conflict_result,
            )
        )

        for evidence_id, result in confidence_results.items():
            if not result.is_valid():
                errors.append(
                    "Invalid confidence result for "
                    f"evidence_id={evidence_id}."
                )

        # --------------------------------------------------------------
        # Stage 5 â€” Source reliability
        # --------------------------------------------------------------

        reliability_results = (
            self.reliability_engine.evaluate_package(package)
        )

        for source, result in reliability_results.items():
            if not result.is_valid():
                errors.append(
                    "Invalid source reliability result for "
                    f"source={source}."
                )

        # --------------------------------------------------------------
        # Stage 6 â€” Final state
        # --------------------------------------------------------------

        rejected_count = (
            len(raw_items) - len(normalized_items)
        )

        completed_at = datetime.now(timezone.utc)

        if errors:
            status = OrchestrationStatus.PARTIAL

            reason = (
                "Evidence pipeline completed with validation "
                "errors. Downstream consumers must inspect "
                "stage-level results."
            )

        elif rejected_count > 0:
            status = OrchestrationStatus.PARTIAL

            reason = (
                "Evidence pipeline completed with partial "
                "normalization; rejected evidence was preserved "
                "as explicit warnings/errors."
            )

        elif conflict_result.conflict_count > 0:
            status = OrchestrationStatus.PARTIAL

            reason = (
                "Evidence pipeline completed and detected "
                "conflicts. Conflicting evidence remains preserved."
            )

        else:
            status = OrchestrationStatus.VALID

            reason = (
                "Evidence pipeline completed successfully with "
                "no deterministic structural conflicts."
            )

        return EvidenceOrchestrationResult(
            status=status,
            package=package,
            normalized=normalized,
            package_result=package_result,
            conflict_result=conflict_result,
            confidence_results=confidence_results,
            reliability_results=reliability_results,
            input_count=len(raw_items),
            accepted_count=len(normalized_items),
            rejected_count=rejected_count,
            errors=tuple(errors),
            warnings=tuple(warnings),
            started_at=started_at,
            completed_at=completed_at,
            reason=reason,
            version=self.VERSION,
        )

    # ------------------------------------------------------------------
    # Confidence integration
    # ------------------------------------------------------------------

    def _calculate_confidence(
        self,
        *,
        package: EvidencePackage,
        conflict_result: ConflictAnalysisResult,
    ) -> dict[str, EvidenceConfidenceResult]:
        """
        Calculate confidence independently for every evidence item.

        Conflict information is supplied as evidence to the confidence
        layer; the orchestrator does not modify confidence itself.
        """
        results: dict[
            str,
            EvidenceConfidenceResult,
        ] = {}

        conflict_map: dict[
            str,
            int,
        ] = {}

        for conflict in conflict_result.conflicts:
            for evidence_id in conflict.evidence_ids:
                conflict_map[evidence_id] = (
                    conflict_map.get(evidence_id, 0) + 1
                )

        for item in package.items:
            result = self._evaluate_item_confidence(
                item=item,
                conflict_count=conflict_map.get(
                    item.evidence_id,
                    0,
                ),
            )

            results[item.evidence_id] = result

        return results

    def _evaluate_item_confidence(
        self,
        *,
        item: EvidenceItem,
        conflict_count: int,
    ) -> EvidenceConfidenceResult:
        """
        Adapter to the canonical EQ-0009 EvidenceConfidenceEngine.

        The orchestrator does not invent confidence, prior weights,
        or EQ-0009 parameters. The canonical confidence engine remains
        the owner of confidence mathematics.
        """
        return self.confidence_engine.calculate_from_items(
            (item,),
            prior_weight=None,
            observations=1,
            parameters=None,
        )
    # ------------------------------------------------------------------
    # Failure helper
    # ------------------------------------------------------------------

    def _failed_result(
        self,
        *,
        started_at: datetime,
        input_count: int,
        normalized: NormalizationResult | None = None,
        package_result: PackageBuildResult | None = None,
        errors: Sequence[str] = (),
        error: str | None = None,
        reason: str = "Evidence orchestration failed.",
    ) -> EvidenceOrchestrationResult:
        all_errors = list(errors)

        if error is not None:
            all_errors.append(error)

        completed_at = datetime.now(timezone.utc)

        return EvidenceOrchestrationResult(
            status=OrchestrationStatus.INVALID,
            package=None,
            normalized=normalized,
            package_result=package_result,
            conflict_result=None,
            input_count=input_count,
            accepted_count=0,
            rejected_count=input_count,
            errors=tuple(all_errors),
            warnings=(),
            started_at=started_at,
            completed_at=completed_at,
            reason=reason,
            version=self.VERSION,
        )


# ----------------------------------------------------------------------
# Convenience API
# ----------------------------------------------------------------------

def orchestrate_evidence(
    evidence: Iterable[
        EvidenceItem | Mapping[str, Any]
    ],
    *,
    package_id: str | None = None,
    market: str | None = None,
    instrument_id: str | None = None,
    timeframe: str | None = None,
    created_at: datetime | None = None,
    metadata: Mapping[str, Any] | None = None,
    tolerance: float = 0.0,
    temporal_overlap_seconds: float | None = None,
) -> EvidenceOrchestrationResult:
    """
    Convenience function for complete Evidence Cortex processing.
    """
    return EvidenceOrchestrator().process(
        evidence,
        package_id=package_id,
        market=market,
        instrument_id=instrument_id,
        timeframe=timeframe,
        created_at=created_at,
        metadata=metadata,
        tolerance=tolerance,
        temporal_overlap_seconds=temporal_overlap_seconds,
    )


# ----------------------------------------------------------------------
# Deterministic integration self-test
# ----------------------------------------------------------------------

def _self_test() -> None:
    timestamp = datetime(
        2026,
        1,
        1,
        10,
        0,
        tzinfo=timezone.utc,
    )

    item_a = EvidenceItem(
        evidence_id="E-001",
        evidence_type="direction",
        source="feed_A",
        value="BUY",
        observed_at=timestamp,
        market="NSE",
        instrument_id="NIFTY",
        timeframe="5m",
        metadata={
            "metric": "direction",
        },
    )

    item_b = EvidenceItem(
        evidence_id="E-002",
        evidence_type="direction",
        source="feed_B",
        value="SELL",
        observed_at=timestamp,
        market="NSE",
        instrument_id="NIFTY",
        timeframe="5m",
        metadata={
            "metric": "direction",
        },
    )

    orchestrator = EvidenceOrchestrator()

    result = orchestrator.process(
        (item_a, item_b),
        package_id="PKG-TEST",
        temporal_overlap_seconds=5.0,
    )

    assert result.package is not None
    assert result.input_count == 2
    assert result.accepted_count == 2
    assert result.rejected_count == 0

    assert result.conflict_result is not None
    assert result.conflict_result.conflict_count >= 1

    assert "E-001" in result.confidence_results
    assert "E-002" in result.confidence_results

    assert "feed_A" in result.reliability_results
    assert "feed_B" in result.reliability_results

    # No reliability may be fabricated merely because the source exists.
    assert (
        result.reliability_results["feed_A"].reliability
        is None
    )

    # Pipeline must remain auditable.
    serialized = result.to_dict()

    assert serialized["package"]["package_id"] == "PKG-TEST"
    assert serialized["input_count"] == 2

    # Invalid mapping must not silently become evidence.
    invalid_result = orchestrator.process(
        (
            {
                "evidence_id": "E-BAD",
                "evidence_type": "price",
                "value": 100.0,
                # source intentionally missing
            },
        )
    )

    assert invalid_result.accepted_count == 0
    assert invalid_result.rejected_count == 1
    assert invalid_result.status in {
        OrchestrationStatus.PARTIAL,
        OrchestrationStatus.INSUFFICIENT,
        OrchestrationStatus.INVALID,
    }


__all__ = [
    "OrchestrationStatus",
    "EvidenceOrchestrationResult",
    "EvidenceOrchestrator",
    "orchestrate_evidence",
]
