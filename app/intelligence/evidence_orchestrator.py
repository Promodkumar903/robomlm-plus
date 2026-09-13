from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Mapping


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    evidence_type: str
    value: Any

    strength: float
    quality: float
    reliability: float

    source: str = ""
    observed_at: datetime | None = None
    derived: bool = False
    source_evidence_ids: tuple[str, ...] = ()

    direction: str = "NEUTRAL"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.evidence_id:
            raise ValueError("evidence_id is required.")

        if not self.evidence_type:
            raise ValueError("evidence_type is required.")

        for value in (
            self.strength,
            self.quality,
            self.reliability,
        ):
            if not 0.0 <= float(value) <= 100.0:
                raise ValueError(
                    "Evidence scores must be between 0 and 100."
                )

        if self.derived and not self.source_evidence_ids:
            raise ValueError(
                "Derived evidence must reference source evidence."
            )


@dataclass(frozen=True)
class EvidenceAssessment:
    symbol: str
    timeframe: str

    evidence_score: float
    strength_score: float
    quality_score: float
    reliability_score: float
    corroboration_score: float
    contradiction_score: float

    evidence_count: int
    observed_count: int
    derived_count: int

    state: str
    confidence: float

    contradictions: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    lineage_valid: bool = True

    evidence: dict[str, Any] = field(default_factory=dict)

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class EvidenceOrchestrator:
    """
    ROBOMLM Evidence Cortex orchestration layer.

    Evidence is not merely a collection of numbers.

    The orchestrator preserves:

        1. Evidence identity
        2. Observed vs derived distinction
        3. Source lineage
        4. Evidence strength
        5. Evidence quality
        6. Source reliability
        7. Corroboration
        8. Contradiction
        9. Evidence sufficiency

    Core evidence score:

        E =
            Strength       * 0.25
          + Quality        * 0.25
          + Reliability   * 0.20
          + Corroboration * 0.15
          + Consistency   * 0.15

    Contradiction is treated as a penalty, not as a positive
    evidence contribution.

    Derived evidence cannot silently become primary evidence.
    """

    VERSION = "ROBOMLM-EVIDENCE-2.0"

    WEIGHTS = {
        "strength": 0.25,
        "quality": 0.25,
        "reliability": 0.20,
        "corroboration": 0.15,
        "consistency": 0.15,
    }

    STRONG_THRESHOLD = 85.0
    SUFFICIENT_THRESHOLD = 70.0
    PARTIAL_THRESHOLD = 50.0
    WEAK_THRESHOLD = 30.0

    CONTRADICTION_PENALTY = 0.35
    MAX_CONTRADICTION_RATIO = 0.50

    def __init__(self, max_history: int = 1000) -> None:
        if max_history < 1:
            raise ValueError("max_history must be >= 1.")

        self._records: dict[str, EvidenceRecord] = {}
        self._history: list[EvidenceAssessment] = []
        self._max_history = max_history
        self._lock = RLock()

    # ================================================================
    # RECORD MANAGEMENT
    # ================================================================

    def add(self, record: EvidenceRecord) -> EvidenceRecord:
        with self._lock:
            self._records[record.evidence_id] = record

        return record

    def add_many(
        self,
        records: list[EvidenceRecord] | tuple[EvidenceRecord, ...],
    ) -> tuple[EvidenceRecord, ...]:

        for record in records:
            self.add(record)

        return tuple(records)

    def remove(self, evidence_id: str) -> bool:
        with self._lock:
            return self._records.pop(str(evidence_id), None) is not None

    def get(self, evidence_id: str) -> EvidenceRecord | None:
        with self._lock:
            return self._records.get(str(evidence_id))

    def records(self) -> tuple[EvidenceRecord, ...]:
        with self._lock:
            return tuple(self._records.values())

    def clear_records(self) -> None:
        with self._lock:
            self._records.clear()

    # ================================================================
    # ASSESSMENT
    # ================================================================

    def assess(
        self,
        records: (
            list[EvidenceRecord]
            | tuple[EvidenceRecord, ...]
            | None
        ) = None,
        *,
        symbol: str = "UNKNOWN",
        timeframe: str = "UNKNOWN",
    ) -> EvidenceAssessment:

        if records is None:
            records = self.records()

        records = tuple(records)

        if not records:
            assessment = EvidenceAssessment(
                symbol=symbol,
                timeframe=timeframe,
                evidence_score=0.0,
                strength_score=0.0,
                quality_score=0.0,
                reliability_score=0.0,
                corroboration_score=0.0,
                contradiction_score=0.0,
                evidence_count=0,
                observed_count=0,
                derived_count=0,
                state="INSUFFICIENT",
                confidence=0.0,
                warnings=("No evidence available.",),
                lineage_valid=True,
                evidence={
                    "engine": self.VERSION,
                    "status": "no_evidence",
                },
            )

            self._store_history(assessment)
            return assessment

        strength = self._average(
            record.strength for record in records
        )

        quality = self._average(
            record.quality for record in records
        )

        reliability = self._average(
            record.reliability for record in records
        )

        observed_count = sum(
            1 for record in records if not record.derived
        )

        derived_count = sum(
            1 for record in records if record.derived
        )

        lineage_valid, lineage_warnings = self._validate_lineage(
            records
        )

        corroboration = self._corroboration_score(records)

        contradiction_score, contradictions = (
            self._contradiction_analysis(records)
        )

        consistency = self._consistency_score(
            records,
            contradiction_score,
        )

        warnings = list(lineage_warnings)

        if derived_count and observed_count == 0:
            warnings.append(
                "Evidence set contains derived evidence without "
                "an observed primary evidence set."
            )

        if contradiction_score >= 50.0:
            warnings.append(
                "Material directional contradiction detected."
            )

        # ------------------------------------------------------------
        # Core evidence model
        # ------------------------------------------------------------

        evidence_score = (
            strength * self.WEIGHTS["strength"]
            + quality * self.WEIGHTS["quality"]
            + reliability * self.WEIGHTS["reliability"]
            + corroboration * self.WEIGHTS["corroboration"]
            + consistency * self.WEIGHTS["consistency"]
        )

        # Contradiction is explicitly penalized.
        contradiction_penalty = (
            contradiction_score / 100.0
        ) * self.CONTRADICTION_PENALTY

        evidence_score *= 1.0 - contradiction_penalty

        if not lineage_valid:
            evidence_score *= 0.70

        evidence_score = self._clamp(evidence_score)

        # ------------------------------------------------------------
        # Sufficiency gates
        # ------------------------------------------------------------

        if not lineage_valid:
            state = "LINEAGE_INVALID"
        elif contradiction_score >= 70.0:
            state = "CONTRADICTED"
        elif evidence_score >= self.STRONG_THRESHOLD:
            state = "STRONG"
        elif evidence_score >= self.SUFFICIENT_THRESHOLD:
            state = "SUFFICIENT"
        elif evidence_score >= self.PARTIAL_THRESHOLD:
            state = "PARTIAL"
        elif evidence_score >= self.WEAK_THRESHOLD:
            state = "WEAK"
        else:
            state = "INSUFFICIENT"

        # ------------------------------------------------------------
        # Evidence confidence
        # ------------------------------------------------------------

        confidence = (
            evidence_score * 0.50
            + quality * 0.15
            + reliability * 0.15
            + corroboration * 0.10
            + consistency * 0.10
        )

        if contradiction_score >= 50.0:
            confidence *= 0.70

        if not lineage_valid:
            confidence *= 0.70

        confidence = self._clamp(confidence)

        evidence_snapshot = {
            "engine": self.VERSION,
            "formula": (
                "E=S*0.25+Q*0.25+R*0.20+"
                "C*0.15+K*0.15"
            ),
            "weights": dict(self.WEIGHTS),
            "evidence_count": len(records),
            "observed_count": observed_count,
            "derived_count": derived_count,
            "strength": strength,
            "quality": quality,
            "reliability": reliability,
            "corroboration": corroboration,
            "consistency": consistency,
            "contradiction": contradiction_score,
            "contradiction_penalty": contradiction_penalty,
            "lineage_valid": lineage_valid,
        }

        assessment = EvidenceAssessment(
            symbol=symbol,
            timeframe=timeframe,
            evidence_score=evidence_score,
            strength_score=strength,
            quality_score=quality,
            reliability_score=reliability,
            corroboration_score=corroboration,
            contradiction_score=contradiction_score,
            evidence_count=len(records),
            observed_count=observed_count,
            derived_count=derived_count,
            state=state,
            confidence=confidence,
            contradictions=tuple(contradictions),
            warnings=tuple(dict.fromkeys(warnings)),
            lineage_valid=lineage_valid,
            evidence=evidence_snapshot,
        )

        self._store_history(assessment)

        return assessment

    # ================================================================
    # CORROBORATION
    # ================================================================

    def _corroboration_score(
        self,
        records: tuple[EvidenceRecord, ...],
    ) -> float:

        if len(records) <= 1:
            return 0.0

        groups: dict[str, list[EvidenceRecord]] = {}

        for record in records:
            key = record.evidence_type.strip().upper()
            groups.setdefault(key, []).append(record)

        # Independent evidence types provide stronger corroboration.
        type_count = len(groups)

        type_score = self._clamp(
            type_count / 5.0 * 100.0
        )

        source_count = len(
            {
                record.source
                for record in records
                if record.source
            }
        )

        source_score = self._clamp(
            source_count / 4.0 * 100.0
        )

        directional_records = [
            record
            for record in records
            if record.direction in {"BUY", "SELL"}
        ]

        if not directional_records:
            directional_agreement = 50.0
        else:
            buy = sum(
                1
                for record in directional_records
                if record.direction == "BUY"
            )

            sell = sum(
                1
                for record in directional_records
                if record.direction == "SELL"
            )

            total = buy + sell

            directional_agreement = (
                abs(buy - sell) / total * 100.0
            )

        return self._clamp(
            type_score * 0.35
            + source_score * 0.30
            + directional_agreement * 0.35
        )

    # ================================================================
    # CONTRADICTION
    # ================================================================

    def _contradiction_analysis(
        self,
        records: tuple[EvidenceRecord, ...],
    ) -> tuple[float, list[str]]:

        directional = [
            record
            for record in records
            if record.direction in {"BUY", "SELL"}
        ]

        if len(directional) < 2:
            return 0.0, []

        buy_records = [
            record
            for record in directional
            if record.direction == "BUY"
        ]

        sell_records = [
            record
            for record in directional
            if record.direction == "SELL"
        ]

        if not buy_records or not sell_records:
            return 0.0, []

        total_strength = sum(
            record.strength
            for record in directional
        )

        if total_strength <= 0.0:
            return 100.0, ["directional_conflict"]

        opposing_strength = min(
            sum(record.strength for record in buy_records),
            sum(record.strength for record in sell_records),
        )

        ratio = opposing_strength / total_strength

        score = self._clamp(
            ratio / self.MAX_CONTRADICTION_RATIO * 100.0
        )

        contradictions = [
            f"BUY={len(buy_records)}",
            f"SELL={len(sell_records)}",
        ]

        return score, contradictions

    # ================================================================
    # CONSISTENCY
    # ================================================================

    def _consistency_score(
        self,
        records: tuple[EvidenceRecord, ...],
        contradiction_score: float,
    ) -> float:

        if not records:
            return 0.0

        quality_values = [
            record.quality
            for record in records
        ]

        reliability_values = [
            record.reliability
            for record in records
        ]

        quality_dispersion = (
            max(quality_values)
            - min(quality_values)
        )

        reliability_dispersion = (
            max(reliability_values)
            - min(reliability_values)
        )

        dispersion_penalty = (
            quality_dispersion * 0.50
            + reliability_dispersion * 0.50
        )

        score = 100.0 - dispersion_penalty

        score *= 1.0 - (
            contradiction_score / 100.0 * 0.50
        )

        return self._clamp(score)

    # ================================================================
    # LINEAGE
    # ================================================================

    def _validate_lineage(
        self,
        records: tuple[EvidenceRecord, ...],
    ) -> tuple[bool, list[str]]:

        ids = {
            record.evidence_id
            for record in records
        }

        warnings: list[str] = []
        valid = True

        for record in records:
            if not record.derived:
                continue

            missing = [
                source_id
                for source_id in record.source_evidence_ids
                if source_id not in ids
            ]

            if missing:
                valid = False
                warnings.append(
                    f"{record.evidence_id}:missing_sources="
                    + ",".join(missing)
                )

        return valid, warnings

    # ================================================================
    # HISTORY
    # ================================================================

    def _store_history(
        self,
        assessment: EvidenceAssessment,
    ) -> None:

        with self._lock:
            self._history.append(assessment)

            if len(self._history) > self._max_history:
                self._history = self._history[-self._max_history:]

    def history(self) -> tuple[EvidenceAssessment, ...]:
        with self._lock:
            return tuple(self._history)

    def clear_history(self) -> None:
        with self._lock:
            self._history.clear()

    def average_score(self) -> float:
        with self._lock:
            if not self._history:
                return 0.0

            return sum(
                item.evidence_score
                for item in self._history
            ) / len(self._history)

    # ================================================================
    # HEALTH
    # ================================================================

    def health_check(self) -> dict[str, Any]:
        with self._lock:
            record_count = len(self._records)
            history_count = len(self._history)

        return {
            "engine": self.VERSION,
            "status": "healthy",
            "record_count": record_count,
            "history_count": history_count,
            "formula": (
                "E=S*0.25+Q*0.25+R*0.20+"
                "C*0.15+K*0.15"
            ),
            "weights": dict(self.WEIGHTS),
            "thresholds": {
                "strong": self.STRONG_THRESHOLD,
                "sufficient": self.SUFFICIENT_THRESHOLD,
                "partial": self.PARTIAL_THRESHOLD,
                "weak": self.WEAK_THRESHOLD,
            },
            "features": [
                "observed_vs_derived",
                "source_lineage",
                "corroboration",
                "contradiction_detection",
                "quality",
                "reliability",
                "consistency",
            ],
        }

    # ================================================================
    # HELPERS
    # ================================================================

    @staticmethod
    def _average(values: Any) -> float:
        values = tuple(float(value) for value in values)

        if not values:
            return 0.0

        return max(
            0.0,
            min(
                100.0,
                sum(values) / len(values),
            ),
        )

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(100.0, float(value)))


__all__ = [
    "EvidenceRecord",
    "EvidenceAssessment",
    "EvidenceOrchestrator",
]